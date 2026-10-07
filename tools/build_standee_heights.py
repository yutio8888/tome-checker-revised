#!/usr/bin/env python3
"""Generate the committed native-tall standee height table.

Standee eligibility is static and decided from the creature catalogue, never
from a live actor field:

* an id is **natively tall** when its catalogue `image` resolves to a 64x128
  shockbolt sprite (the native `nice_tile tall=1` / `display_h=2` body);
* its height cap is ``clamp(native alpha-bbox height / 64 - 0.25, 1.0, 1.75)``
  cells, measured on the native sprite with the same alpha>8 threshold the
  layer exporter uses;
* a cap of exactly 1.0 means the native visible body is <= 1.25 cells tall, so
  the id keeps the flat token for now.

This tool is DETERMINISTIC and read-only over the game tree. It reads the
catalogue out of ``overload/mod/class/CheckerTokens.lua`` and the native sprites
from ``game/modules/tome/data/gfx/shockbolt/`` and writes
``data/token-standee-heights.lua``. It never runs during packaging or tests; the
committed Lua table is the product.

    python3 tools/build_standee_heights.py            # write the table
    python3 tools/build_standee_heights.py --check    # fail if it would change
    python3 tools/build_standee_heights.py --review   # print the manual-review list
"""
from __future__ import annotations

import argparse
import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parents[2]
TOKENS_LUA = ROOT / 'overload/mod/class/CheckerTokens.lua'
STYLE_LUA = ROOT / 'overload/mod/class/CheckerTokenStyle.lua'
SPRITES = WORKSPACE / 'game/modules/tome/data/gfx/shockbolt'
OUT = ROOT / 'data/token-standee-heights.lua'

TALL_W, TALL_H = 64, 128
ALPHA_THRESHOLD = 8
# R46 solid top: the body top for a sprite whose top rows are a semi-transparent
# glue, mist or particle fringe is the FIRST ROW with at least SOLID_MIN_PIXELS
# pixels above SOLID_ALPHA. The alpha>8 bbox top is then not body. This is the
# reproducible measure behind the R46 overrides (weaver-queen, archmage-tarelion,
# duathedlen, onilug, ninandra) and the sweep report; it is NOT applied to the
# generated cap, which keeps the alpha>8 bbox rule.
SOLID_ALPHA = 128
SOLID_MIN_PIXELS = 6
HEIGHT_MIN, HEIGHT_MAX = 1.0, 1.75
HEIGHT_OFFSET = 0.25
# Raised weapons, staves, floating orbs, debris, particles, flames, lightning
# and glow above the head inflate the alpha bbox, so the measured native height
# can overstate the standing body. These ids were reviewed sprite by sprite
# against the user's body-only rule (head, horns, helmet, hair, raised arms,
# wings and fins count) and are listed for a manual height check with
# M.standee_height_override. An id whose head/horns/helmet/hair/arms/wings/fins
# is the bbox top keeps the generated cap and is not listed. The tool fails
# loudly if an id here is unknown, not natively tall, or if an override key is
# missing from this set. Energy/cloud/elemental beings whose glow IS the body
# keep their derived cap and need no override (decision 3): greater-telugoroth,
# ultimate-telugoroth, daelach, fyrk, ultimate-faeros, ultimate-teluvorta,
# maelstrom, ultimate-gwelgoroth and glacial-legion.
MANUAL_HEIGHT_REVIEW = (
    'ak-gishil', 'animated-blood', 'arch-zephyr', 'archmage-tarelion', 'argoniel',
    'blade-horror', 'boiling-horror', 'brotoq', 'burb-snow-giant-champion', 'caldizar',
    'celia', 'champion-of-urh-rok', 'corrupted-daelach', 'corrupted-sand-wyrm',
    'cryomancer', 'duathedlen', 'elandar', 'emperor-wight', 'fallen-sun-paladin-aeryn',
    'fillarel-aldaren', 'forge-giant', 'fyrk', 'geomancer', 'gigantic-gravity-worm',
    'gigantic-sandworm-tunneler', 'gorbat', 'greater-teluvorta', 'half-finished-bone-giant', 'harkor-zun',
    'heavy-sentinel', 'high-sun-paladin-aeryn', 'khulmanar', 'kra-tor', 'krogar',
    'kryl-feijan', 'kyless', 'lady-nashva', 'lady-zoisla', 'maelstrom', 'massok', 'minotaur-maze',
    'naga-nereid', 'naga-tidecaller', 'naga-tidewarden', 'ninandra', 'norgos-frozen',
    'ogre-guard', 'ogre-rune-spinner', 'ogre-warmaster', 'ogric-abomination',
    'onilug', 'pale-drake', 'prox', 'ravenous-horror', 'rotting-titan', 'shiaak-venomblade',
    'slasul', 'snow-giant', 'snow-giant-boulder-thrower', 'snow-giant-chieftain',
    'snow-giant-thunderer', 'spellblaze-simulacrum', 'tempest', 'temporal-defiler',
    'thaurhereg', 'urkis', 'uruivellas', 'void-spectre', 'walrog', 'weaver-queen',
    'xhaiak-arachnomancer', 'yeek-mindslayer',
)
NARROW_TOP_SHARE = 0.5


def png_size(path: Path) -> tuple[int, int]:
    with path.open('rb') as fh:
        head = fh.read(24)
    if head[:8] != b'\x89PNG\r\n\x1a\n':
        raise ValueError(f'not a PNG: {path}')
    return struct.unpack('>II', head[16:24])


def solid_top(alpha, threshold: int = SOLID_ALPHA, min_pixels: int = SOLID_MIN_PIXELS):
    """First row with at least ``min_pixels`` pixels above ``threshold``.

    The R46 reproducible body top for a semi-transparent fringe: a glow, mist or
    particle top row usually has only a few opaque pixels, while the body mass
    below it has many. Return ``None`` when no row reaches the count.
    """
    for y in range(alpha.shape[0]):
        if int((alpha[y] > threshold).sum()) >= min_pixels:
            return y
    return None


def alpha_metrics(path: Path) -> dict:
    """Alpha bbox height and top-band width on the native sprite.

    PIL is available in the tool venv and on the host; the bitmap decode is the
    only way to measure the visible body rather than the 64x128 canvas.
    """
    from PIL import Image
    import numpy as np

    image = Image.open(path).convert('RGBA')
    alpha = np.asarray(image)[..., 3]
    ys, xs = np.where(alpha > ALPHA_THRESHOLD)
    if not len(xs):
        raise ValueError(f'empty alpha: {path}')
    top, bottom = int(ys.min()), int(ys.max())
    left, right = int(xs.min()), int(xs.max())
    bh = bottom - top + 1
    bw = right - left + 1
    band = max(1, bh // 8)
    rows = alpha[top:top + band] > ALPHA_THRESHOLD
    top_run = int(rows.sum(axis=1).max()) if len(rows) else 0
    solid = solid_top(alpha)
    solid_px = (bottom - solid + 1) if solid is not None else 0
    return {'height_px': bh, 'top': top, 'left': left, 'width_px': bw,
            'top_run_px': top_run, 'top_band_px': band,
            'solid_top': solid, 'solid_height_px': solid_px}


def parse_catalogue(text: str) -> list[tuple[str, str]]:
    """Return (id, image) for every single-line catalogue entry, in order."""
    found = []
    for match in re.finditer(r'^\s*\{id="([^"]+)",.*?image="([^"]+)"', text, re.M):
        found.append((match.group(1), match.group(2)))
    if len(found) < 400:
        raise SystemExit(f'only {len(found)} catalogue entries parsed; the table format changed')
    return found


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def lua_number(value: float) -> str:
    # Native heights are multiples of 1/64, so every cap is exact in decimal.
    text = ('%.6f' % value).rstrip('0').rstrip('.')
    return text if text else '0'


def parse_overrides(text: str) -> dict[str, float]:
    """The committed M.standee_height_override table (key -> body height).

    The tool must fail loudly rather than silently accept an override that is
    unknown, unreviewed, above the generated cap or outside the clamp range.
    """
    match = re.search(r'M\.standee_height_override=\{([^}]*)\}', text, re.S)
    if not match:
        raise SystemExit('M.standee_height_override table not found in CheckerTokenStyle.lua')
    overrides = {}
    for key, value in re.findall(r"\['([^']+)'\]\s*=\s*([0-9.]+)", match.group(1)):
        overrides[key] = float(value)
    return overrides


def check_overrides(overrides: dict[str, float], caps: dict[str, float]) -> None:
    unreviewed = sorted(set(overrides) - set(MANUAL_HEIGHT_REVIEW))
    if unreviewed:
        raise SystemExit('height overrides missing from MANUAL_HEIGHT_REVIEW: ' + ', '.join(unreviewed))
    for cid, value in sorted(overrides.items()):
        cap = caps.get(cid)
        if cap is None:
            raise SystemExit(f'height override {cid!r} is not a natively tall id')
        if not (HEIGHT_MIN <= value <= HEIGHT_MAX):
            raise SystemExit(f'height override {cid!r} outside [{HEIGHT_MIN}, {HEIGHT_MAX}]')
        if value > cap + 1e-9:
            raise SystemExit(f'height override {cid!r} exceeds the generated cap {cap}')



def compute() -> tuple[list[tuple[str, float]], list[dict]]:
    entries = parse_catalogue(TOKENS_LUA.read_text())
    catalogue_ids = {cid for cid, _ in entries}
    unknown = sorted(set(MANUAL_HEIGHT_REVIEW) - catalogue_ids)
    if unknown:
        raise SystemExit('manual height review names unknown catalogue ids: ' + ', '.join(unknown))
    heights = []
    review = []
    for cid, image in entries:
        path = SPRITES / image
        if not path.is_file():
            raise SystemExit(f'catalogue image missing on disk: {cid} -> {image}')
        if png_size(path) != (TALL_W, TALL_H):
            continue
        metrics = alpha_metrics(path)
        native_cells = metrics['height_px'] / 64.0
        cap = clamp(native_cells - HEIGHT_OFFSET, HEIGHT_MIN, HEIGHT_MAX)
        heights.append((cid, cap))
        if cid in MANUAL_HEIGHT_REVIEW:
            review.append({'id': cid, 'image': image, 'cap': cap,
                           'native_cells': round(native_cells, 4),
                           'width_px': metrics['width_px'],
                           'top_run_px': metrics['top_run_px']})
    reviewed_ids = {row['id'] for row in review}
    stale = sorted(set(MANUAL_HEIGHT_REVIEW) - reviewed_ids)
    if stale:
        raise SystemExit('manual height review ids are not natively tall (64x128): ' + ', '.join(stale))
    check_overrides(parse_overrides(STYLE_LUA.read_text()), dict(heights))
    heights.sort()
    review.sort(key=lambda row: (row['cap'], row['id']))
    return heights, review


HEADER = [
    '-- Generated by tools/build_standee_heights.py. Do not edit by hand.',
    '-- Native-tall creature ids and their standee height cap in cells. An id is',
    '-- natively tall when its catalogue image is a 64x128 shockbolt sprite; the',
    '-- cap is clamp(native alpha-bbox height / 64 - 0.25, 1.0, 1.75). A cap of',
    '-- exactly 1.0 means the native visible body is <= 1.25 cells tall, so the id',
    '-- keeps the flat token for now. An id absent here is not natively tall and',
    '-- never gets a standee. Rank and live size_category are not consulted.',
    'return {',
]


def solid_report() -> list[dict]:
    """R46 solid-top comparison for every native-tall id (read-only).

    For each id the effective height (override when present, else the generated
    cap) is compared with the solid-top body height. A difference larger than
    1/64 means the sprite has more than one row of non-body fringe above its
    body; the sweep report lists those ids so they can be reviewed. The measure
    is not applied automatically: a change needs a fringe/glow/particle top.
    """
    entries = parse_catalogue(TOKENS_LUA.read_text())
    overrides = parse_overrides(STYLE_LUA.read_text())
    caps = dict(compute()[0])
    rows = []
    for cid, image in entries:
        path = SPRITES / image
        if not path.is_file() or png_size(path) != (TALL_W, TALL_H):
            continue
        metrics = alpha_metrics(path)
        solid = metrics['solid_top']
        if solid is None:
            continue
        bottom = metrics['top'] + metrics['height_px'] - 1
        solid_cells = (bottom - solid + 1) / 64.0 - HEIGHT_OFFSET
        solid_cap = clamp(solid_cells, HEIGHT_MIN, HEIGHT_MAX)
        current = overrides.get(cid, caps[cid])
        rows.append({'id': cid, 'current': current, 'solid_cap': solid_cap,
                     'solid_cells': solid_cells, 'delta': solid_cap - current,
                     'solid_top': solid, 'top': metrics['top'], 'bottom': bottom,
                     'override': cid in overrides})
    rows.sort(key=lambda row: (-abs(row['delta']), row['id']))
    return rows


def render(heights: list[tuple[str, float]]) -> str:
    body = [f'\t[{cid!r}]={lua_number(cap)},' for cid, cap in heights]
    return '\n'.join(HEADER + body) + '\n}\n'


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--check', action='store_true',
                        help='exit 1 if the committed table differs from the computed one')
    parser.add_argument('--review', action='store_true',
                        help='print the manual height-review list and exit')
    parser.add_argument('--solid', action='store_true',
                        help='print every id whose solid top differs from its effective cap by > 1/64')
    args = parser.parse_args(argv)
    if args.solid:
        rows = solid_report()
        flagged = [row for row in rows if abs(row['delta']) > 1 / 64 + 1e-9]
        print(f'native-tall ids: {len(rows)}; solid top differs by > 1/64: {len(flagged)}')
        for row in flagged:
            print(f"  {row['id']:<30} current={lua_number(row['current']):<9} "
                  f"solid={lua_number(row['solid_cap']):<9} delta={row['delta']:+.6f} "
                  f"top={row['top']} solid_top={row['solid_top']} bottom={row['bottom']} "
                  f"override={row['override']}")
        return 0
    heights, review = compute()
    if args.review:
        print(f'native-tall ids: {len(heights)}')
        print(f'flat (cap == 1.0): {sum(1 for _, cap in heights if cap <= HEIGHT_MIN)}')
        print(f'manual height review ({len(review)}):')
        for row in review:
            print(f"  {row['id']:<28} cap={row['cap']:<7} native={row['native_cells']:<7} "
                  f"top_run={row['top_run_px']}px of {row['width_px']}px")
        return 0
    text = render(heights)
    if args.check:
        current = OUT.read_text() if OUT.is_file() else ''
        if current != text:
            print('data/token-standee-heights.lua is out of date; re-run without --check', file=sys.stderr)
            return 1
        print(f'token-standee-heights.lua up to date: {len(heights)} native-tall ids')
        return 0
    OUT.write_text(text)
    print(f'wrote {OUT.relative_to(ROOT)}: {len(heights)} native-tall ids, '
          f'{len(review)} flagged for manual height review')
    return 0


if __name__ == '__main__':
    sys.exit(main())
