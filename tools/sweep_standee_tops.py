#!/usr/bin/env python3
"""R44/R46 colour and solid-top sweep: triage native-tall standee ids whose
derived-height top is an effect (lightning, glow, flame or particle) rather
than body.

Read-only over the game tree. It triages every native-tall id by looking at the
top rows of the native sprite:

* translucent top   -- the top rows have no opaque pixel (max
                       alpha < 200): smoke, glow or lightning;
* bright glow       -- >= 50% of the top rows are light and
                       low-saturation (V > 205, colour spread S < 64, which
                       catches e.g. burb's (155,194,212) lightning at S=57);
* warm flame        -- >= 50% of the top rows are saturated warm
                       (R - B > 70, R > 170);
* detached blob     -- an empty row band separates the topmost blob from the
                       body mass (gap >= 2);
* fog               -- the alpha>8 top and the solid alpha>128 top differ by
                       >= 6 px (a semi-transparent bristle/speck/mist/shroud
                       fringe above the body mass -- the R45 user rule).

It also reports the R46 **solid top** (the first row with >= 6 pixels above
alpha 128, from tools/build_standee_heights.py) for EVERY native-tall id and
lists every id whose solid-top cap differs from its effective cap (override or
derived) by more than 1/64. That is triage, not the product rule: a change
needs a fringe/glow/particle top, and energy/cloud beings whose glow is the
body keep their cap. Every flagged sprite is classified mechanically by the checks above and only
spot-checked by eye; the colour flags are triage, not a decision (see
evidence/token-standee-shape-20261004/).

    python3 tools/sweep_standee_tops.py            # table, flags marked
    python3 tools/sweep_standee_tops.py --json     # machine readable
"""
from __future__ import annotations
import argparse
import importlib.util
import json
import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parents[2]
TOKENS_LUA = ROOT / 'overload/mod/class/CheckerTokens.lua'
STYLE_LUA = ROOT / 'overload/mod/class/CheckerTokenStyle.lua'
SPRITES = WORKSPACE / 'game/modules/tome/data/gfx/shockbolt'


def _heights_module():
    spec = importlib.util.spec_from_file_location(
        'build_standee_heights', ROOT / 'tools' / 'build_standee_heights.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_HEIGHTS = _heights_module()
ALPHA = 8
TALL_W, TALL_H = 64, 128
TOP_ROWS = 8
OPAQUE_ROWS = 3
LIGHT_V, LIGHT_S = 205, 64
WARM_RB, WARM_R = 70, 170
TRANSLUCENT_MAX_ALPHA = 200
DETACH_GAP = 2
SOLID_ALPHA = 128
FOG_DELTA = 6


def catalogue() -> list[tuple[str, str]]:
    text = TOKENS_LUA.read_text()
    return [(m.group(1), m.group(2)) for m in re.finditer(
        r'^\s*\{id="([^"]+)",.*?image="([^"]+)"', text, re.M)]


def overrides() -> dict[str, float]:
    text = STYLE_LUA.read_text()
    m = re.search(r'M\.standee_height_override=\{([^}]*)\}', text, re.S)
    return {k: float(v) for k, v in re.findall(r"\['([^']+)'\]\s*=\s*([0-9.]+)", m.group(1))}


def png_size(path: Path) -> tuple[int, int]:
    return struct.unpack('>II', path.open('rb').read(24)[16:24])


def analyse(pid: str, image: str) -> dict:
    import numpy as np
    from PIL import Image
    arr = np.asarray(Image.open(SPRITES / image).convert('RGBA')).astype(int)
    a = arr[..., 3]
    rgb = arr[..., :3]
    ys, xs = np.where(a > ALPHA)
    top, bottom = int(ys.min()), int(ys.max())
    bh = bottom - top + 1
    cap = max(1.0, min(1.75, bh / 64 - 0.25))
    sel = np.zeros(a.shape, bool)
    for y in range(top, min(top + TOP_ROWS, bottom + 1)):
        sel[y] = a[y] > ALPHA
    px = rgb[sel]
    v = px.max(1)
    s = px.max(1) - px.min(1)
    n = max(1, len(px))
    light = float(((v > LIGHT_V) & (s < LIGHT_S)).mean())
    warm = float(((px[:, 0] - px[:, 2] > WARM_RB) & (px[:, 0] > WARM_R)).mean())
    # Translucent top keeps the R44 three-row window: the immediate cap rows.
    al = a[top:top + OPAQUE_ROWS][a[top:top + OPAQUE_ROWS] > ALPHA]
    max_alpha = int(al.max()) if len(al) else 0
    # Fog: a semi-transparent fringe whose top is well above the solid mass.
    ys128, _ = np.where(a > SOLID_ALPHA)
    top128 = int(ys128.min()) if len(ys128) else top
    fog = (top128 - top) >= FOG_DELTA
    # Detached blob: an empty row band between the top and the body mass.
    wide = max(int((a[y] > ALPHA).sum()) for y in range(top, bottom + 1))
    body_row = None
    empty = 0
    gap = 0
    for y in range(top, bottom + 1):
        r = a[y] > ALPHA
        if not r.any():
            empty += 1
            continue
        if empty >= 1 and body_row is None:
            gap = max(gap, empty)
        if body_row is None and int(r.sum()) >= max(3, int(0.45 * wide)):
            body_row = y
        empty = 0
    flag = bool(max_alpha < TRANSLUCENT_MAX_ALPHA or light >= 0.5 or warm >= 0.5
                or gap >= DETACH_GAP or fog)
    # R46 solid top: first row with >= 6 pixels above alpha 128.
    solid = _HEIGHTS.solid_top(a, SOLID_ALPHA, _HEIGHTS.SOLID_MIN_PIXELS)
    solid_cells = ((bottom - solid + 1) / 64 - 0.25) if solid is not None else None
    solid_cap = max(1.0, min(1.75, solid_cells)) if solid_cells is not None else None
    return {'id': pid, 'image': image, 'top': top, 'bottom': bottom, 'bh': bh,
            'cap': round(cap, 6), 'body_row': body_row, 'detach_gap': gap,
            'light': round(light, 2), 'warm': round(warm, 2), 'max_alpha': max_alpha,
            'top8': top, 'top128': top128, 'fog_delta': top128 - top, 'fog': fog,
            'solid_top': solid, 'solid_cells': round(solid_cells, 6) if solid_cells is not None else None,
            'solid_cap': round(solid_cap, 6) if solid_cap is not None else None,
            'flag': flag}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()
    ov = overrides()
    out = []
    for pid, image in catalogue():
        path = SPRITES / image
        if not path.is_file() or png_size(path) != (TALL_W, TALL_H):
            continue
        row = analyse(pid, image)
        override = ov.get(pid)
        row['override'] = override
        row['current'] = override if override is not None else row['cap']
        delta = (row['solid_cap'] - row['current']) if row['solid_cap'] is not None else 0.0
        row['solid_delta'] = round(delta, 6)
        row['solid_flag'] = bool(row['solid_cap'] is not None and abs(delta) > 1 / 64 + 1e-9)
        # R45: ids already reviewed keep their cap; the colour flag is triage
        # for the unreviewed ids only (the R46 solid report covers all ids).
        row['reviewed'] = override is not None
        out.append(row)
    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=1))
        return 0
    unreviewed = [r for r in out if not r['reviewed']]
    print(f'{len(out)} native-tall ids ({len(unreviewed)} without an override)')
    for row in sorted(out, key=lambda r: (not r['flag'], r['id'])):
        print(f"{'FLAG' if row['flag'] and not row['reviewed'] else '    '} {row['id']:<30} "
              f"cap={row['cap']:<9} top={row['top']:<3} top128={row['top128']:<3} "
              f"solid={row['solid_top']!s:<4} body={row['body_row']!s:<4} "
              f"gap={row['detach_gap']} maxA={row['max_alpha']:<3} "
              f"light={row['light']:.2f} warm={row['warm']:.2f} fog={row['fog_delta']} "
              f"solidD={row['solid_delta']:+.4f}")
    flagged = sorted(r['id'] for r in unreviewed if r['flag'])
    print(f'colour flagged (no override): {len(flagged)}: {", ".join(flagged)}')
    solid = sorted(r['id'] for r in out if r['solid_flag'])
    print(f'solid top differs from the effective cap by > 1/64: {len(solid)}: {", ".join(solid)}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
