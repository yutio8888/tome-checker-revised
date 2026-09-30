#!/usr/bin/env python3
"""Export the S12 board hazard family (data/gfx/refined/hazard).

Two identities, both drawn by the stone adapter in stone rooms:

* lava-<v>-<mask>-<p> (T19, damaging lava.lua LAVA_FLOOR*): one ImageGen master
  (masters/hazard-lava-floor-v1.png: flat dark basalt crust plates with thin
  glowing seams, gpt-6.1-sol, see REVIEW.md). Each cell is a fixed 640 px window
  of the master (three variants a/b/c, chosen on the board like the Kor'Pul
  floor-a/b: (x*17+y*7)%3), so a pool never repeats one tile in a checker. Where
  the neighbour is NOT hazard lava (bit clear) the cell gets a flush glowing
  seam: a thin hot line on the shared edge and a short red-orange heat bleed into
  the crust. No raised rim or dark frame (that is the blocking molten pit of the
  burnt family, refined/burnt/lava-*), no pool: it reads as walkable hot ground.
* deep-<mask>-<p> (T20, Vor Armoury L2 DEEP_WATER): derived, 0 ImageGen. The
  board deep-water surface (art/terrain-forest-v1/masters-derived/floor-deep.png,
  the same surface as refined/deep*) with a stone kerb instead of the grass bank
  where the neighbour is not deep water: the accepted Kor'Pul floor master
  (art/terrain-korpul-v1/masters/floor-a-v2.png) sampled in world coordinates,
  10 px deep like the forest bank (BANK_DEPTH 10), with a dark wet line at the
  water side and a faint shadow on the water under it.

Bit order N=1 E=2 S=4 W=8 (CheckerTerrain.lua dirs); a set bit means the
neighbour is the same family. Both families use the Kor'Pul board conventions
of the rooms they sit in: 1 px printed grid on all four edges (x0.88) and
parity 1 = x0.90. Deterministic: fixed windows, no noise. Writes
data/gfx/refined/hazard, data/terrain-hazard-manifest.lua, review/ and
export-manifest.json.
"""
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageStat
import hashlib, json

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUT = ROOT / 'data/gfx/refined/hazard'
MANIFEST = ROOT / 'data/terrain-hazard-manifest.lua'
REVIEW = HERE / 'review'
LAVA_MASTER = HERE / 'masters/hazard-lava-floor-v1.png'
DEEP_SURFACE = ROOT / 'art/terrain-forest-v1/masters-derived/floor-deep.png'
KORPUL_FLOOR = ROOT / 'art/terrain-korpul-v1/masters/floor-a-v2.png'
SIZE = 128
GRID = .88
PARITY = .90
# Lava: three fixed 640 px windows (about four crust plates across).
WINDOW = 640
WINDOWS = {'a': (60, 70), 'b': (560, 180), 'c': (250, 560)}
LAVA_BRIGHTNESS = 1.0
SEAM = (255, 176, 64)           # the hot line on an open edge
SEAM_W = 2
BLEED = (236, 82, 22)           # heat bleeding into the crust
BLEED_W = 10
BLEED_ALPHA = .62
# Water: stone kerb.
KERB = 10
KERB_BRIGHTNESS = 1.08
WET = .52                       # the wet line at the water side of the kerb
WET_W = 2
UNDER = .80                     # shadow on the water just under the kerb
UNDER_W = 4


def printed(im):
    """Kor'Pul printed grid: 1 px on all four edges, x0.88."""
    im = im.copy()
    px = im.load()
    for i in range(SIZE):
        for x, y in ((i, 0), (i, SIZE - 1), (0, i), (SIZE - 1, i)):
            r, g, b = px[x, y][:3]
            px[x, y] = (round(r * GRID), round(g * GRID), round(b * GRID)) + ((255,) if im.mode == 'RGBA' else ())
    return im


def parity(im, p):
    im = im.convert('RGB')
    if p:
        im = im.point(lambda v: round(v * PARITY))
    return im.convert('RGBA')


def edge_ramp(mask, width, power=1.0):
    """L mask: 255 at an open edge fading to 0 at `width` px inward (max over open edges)."""
    ramp = Image.new('L', (SIZE, SIZE), 0)
    px = ramp.load()
    for y in range(SIZE):
        for x in range(SIZE):
            best = 0.0
            for bit, d in ((1, y), (2, SIZE - 1 - x), (4, SIZE - 1 - y), (8, x)):
                if not mask & bit and d < width:
                    best = max(best, (1 - d / width) ** power)
            px[x, y] = round(255 * best)
    return ramp


def lava_tile(master, v, mask):
    x0, y0 = WINDOWS[v]
    cell = master.crop((x0, y0, x0 + WINDOW, y0 + WINDOW)).resize((SIZE, SIZE), Image.Resampling.LANCZOS)
    cell = ImageEnhance.Brightness(cell).enhance(LAVA_BRIGHTNESS)
    # Heat bleed: screen-like lift toward the bleed colour near open edges.
    bleed = edge_ramp(mask, BLEED_W, 1.6).point(lambda a: round(a * BLEED_ALPHA))
    cell = Image.composite(ImageChops.screen(cell, Image.new('RGB', (SIZE, SIZE), BLEED)), cell, bleed)
    # The hot seam line itself on the shared edge.
    seam = edge_ramp(mask, SEAM_W + 1, 0.6)
    cell = Image.composite(Image.new('RGB', (SIZE, SIZE), SEAM), cell, seam)
    return printed(cell)


def deep_tile(surface, kerb_src, mask):
    cell = surface.convert('RGB').resize((SIZE, SIZE), Image.Resampling.LANCZOS)
    # Shadow on the water just under the kerb.
    under = Image.new('L', (SIZE, SIZE), 0)
    d = ImageDraw.Draw(under)
    for bit, box in ((1, (0, 0, SIZE - 1, KERB + UNDER_W - 1)), (2, (SIZE - KERB - UNDER_W, 0, SIZE - 1, SIZE - 1)),
                     (4, (0, SIZE - KERB - UNDER_W, SIZE - 1, SIZE - 1)), (8, (0, 0, KERB + UNDER_W - 1, SIZE - 1))):
        if not mask & bit:
            d.rectangle(box, fill=255)
    cell = Image.composite(cell.point(lambda v: round(v * UNDER)), cell, under)
    # Kerb: world-fixed window of the board stone floor.
    stone = ImageEnhance.Brightness(kerb_src).enhance(KERB_BRIGHTNESS)
    kerb = Image.new('L', (SIZE, SIZE), 0)
    wet = Image.new('L', (SIZE, SIZE), 0)
    dk, dw = ImageDraw.Draw(kerb), ImageDraw.Draw(wet)
    n, e, s, w = (not mask & 1), (not mask & 2), (not mask & 4), (not mask & 8)
    # Each wet line runs only along the water, never through a crossing kerb
    # (a corner where two kerbs meet stays dry stone).
    lo, hi = (KERB if w else 0), (SIZE - KERB - 1 if e else SIZE - 1)
    top, bot = (KERB if n else 0), (SIZE - KERB - 1 if s else SIZE - 1)
    if n:
        dk.rectangle((0, 0, SIZE - 1, KERB - 1), fill=255); dw.rectangle((lo, KERB - WET_W, hi, KERB - 1), fill=255)
    if e:
        dk.rectangle((SIZE - KERB, 0, SIZE - 1, SIZE - 1), fill=255); dw.rectangle((SIZE - KERB, top, SIZE - KERB + WET_W - 1, bot), fill=255)
    if s:
        dk.rectangle((0, SIZE - KERB, SIZE - 1, SIZE - 1), fill=255); dw.rectangle((lo, SIZE - KERB, hi, SIZE - KERB + WET_W - 1), fill=255)
    if w:
        dk.rectangle((0, 0, KERB - 1, SIZE - 1), fill=255); dw.rectangle((KERB - WET_W, top, KERB - 1, bot), fill=255)
    cell = Image.composite(stone, cell, kerb)
    cell = Image.composite(cell.point(lambda v: round(v * WET)), cell, wet)
    return printed(cell)


def lum(im):
    return round(ImageStat.Stat(im.convert('L')).mean[0], 1)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob('*.png'):
        old.unlink()
    with Image.open(LAVA_MASTER) as m:
        master = m.convert('RGB')
    with Image.open(DEEP_SURFACE) as s:
        surface = s.convert('RGBA')
    with Image.open(KORPUL_FLOOR) as k:
        kerb_src = k.convert('RGB').resize((SIZE, SIZE), Image.Resampling.LANCZOS)
    files = []
    for p in (0, 1):
        for mask in range(16):
            for v in WINDOWS:
                name = f'lava-{v}-{mask}-{p}.png'
                parity(lava_tile(master, v, mask), p).save(OUT / name)
                files.append(name)
            name = f'deep-{mask}-{p}.png'
            parity(deep_tile(surface, kerb_src, mask), p).save(OUT / name)
            files.append(name)
    files.sort()
    digest = hashlib.sha256(b''.join((OUT / f).read_bytes() for f in files)).hexdigest()[:12]
    lines = ['-- Generated by art/terrain-hazard-s12/export.py.',
             '-- S12 hazard family: damaging lava floor (T19) and stone-kerb deep water (T20).',
             'return {', ' ready=true,', f" revision='hazard-s12-{digest}',", ' files={']
    lines += [f"  ['checker-revised+refined/hazard/{f}']=true," for f in files]
    lines += [' },', '}']
    MANIFEST.write_text('\n'.join(lines) + '\n')
    # Review: every tile at 48/64/96 plus contact sheets.
    for n in (48, 64, 96):
        (REVIEW / str(n)).mkdir(parents=True, exist_ok=True)
        for f in files:
            with Image.open(OUT / f) as im:
                im.resize((n, n), Image.Resampling.LANCZOS).save(REVIEW / str(n) / f)
    report = {'imagegen_calls': 1, 'runtime_files': len(files), 'revision': f'hazard-s12-{digest}',
              'source_sha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in (LAVA_MASTER, DEEP_SURFACE, KORPUL_FLOOR)},
              'luminance': {f: lum(Image.open(OUT / f)) for f in ('lava-a-15-0.png', 'lava-b-15-0.png', 'lava-c-15-0.png',
                                                                   'lava-a-0-0.png', 'deep-15-0.png', 'deep-0-0.png')},
              'runtime_sha256': {f: hashlib.sha256((OUT / f).read_bytes()).hexdigest() for f in files}}
    (HERE / 'export-manifest.json').write_text(json.dumps(report, indent=1) + '\n')
    print(len(files), report['revision'], report['luminance'])


if __name__ == '__main__':
    main()
