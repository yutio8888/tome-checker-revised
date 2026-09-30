#!/usr/bin/env python3
"""Export the S17 board dream family (data/gfx/refined/dream).

The Solipsist Dreamscape plane (zones/dreamscape-talent) is a 20x20 Forest
map of zone-local CLOUD floor over void.lua OUTERSPACE. Two ImageGen masters
(gpt-6.1-sol, see REVIEW.md):

* cloud-<v>-<mask>-<p> (CLOUD, walkable): masters/dream-cloud-floor-v1.png,
  a flat overhead packed-cloud surface. Each cell is a fixed 640 px window
  (three variants a/b/c, chosen on the board by (x*17+y*7)%3 like the other
  board floors), toned down to a mid-high value so tokens stay the strongest
  element. Where the neighbour is NOT cloud (bit clear) the cell ends in a
  soft billowed cloud rim: a scalloped edge band shaded toward lilac (the
  cloud's side falling away; widest on the south edge, where a raised floor
  shows its side under the board's upper-left light) with a thin bright lip
  on the walkable side. The scallops have a 32 px period anchored at the cell
  corners, so rims of neighbouring cloud cells meet. No wall, rail or fence.
* void-<v>-<p> (OUTERSPACE, impassable, harmless): masters/dream-void-v1.png,
  a dark indigo haze with faint far-below wisps; two fixed 640 px windows
  (a/b by (x*17+y*7)%2), unmasked (the cloud side carries the rim).

Bit order N=1 E=2 S=4 W=8 (CheckerTerrain.lua dirs); a set bit means the
neighbour is cloud. Cloud cells carry a faint 1 px printed grid (x0.93);
parity 1 = x0.90 (cloud) / x0.86 (void). Deterministic: fixed windows, no
noise. Writes data/gfx/refined/dream, data/terrain-dream-manifest.lua,
review/<n>/ and export-manifest.json.
"""
from pathlib import Path
from PIL import Image, ImageChops, ImageEnhance, ImageFilter, ImageStat
import hashlib, json, math

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUT = ROOT / 'data/gfx/refined/dream'
MANIFEST = ROOT / 'data/terrain-dream-manifest.lua'
REVIEW = HERE / 'review'
CLOUD_MASTER = HERE / 'masters/dream-cloud-floor-v1.png'
VOID_MASTER = HERE / 'masters/dream-void-v1.png'
SIZE = 128
WINDOW = 640
CLOUD_WINDOWS = {'a': (40, 60), 'b': (560, 120), 'c': (260, 560)}
VOID_WINDOWS = {'a': (80, 80), 'b': (520, 500)}
CLOUD_BRIGHTNESS = .82
CLOUD_CONTRAST = 1.18
VOID_BRIGHTNESS = 1.0
GRID = .93
PARITY_CLOUD = .90
PARITY_VOID = .86
# Rim: base depth per open edge (N, E, S, W) plus a scallop swell.
RIM = {1: 5, 2: 7, 4: 13, 8: 7}
SCALLOP = 32
SWELL = 4
SIDE = (118, 104, 150)          # lilac side colour the rim shades toward
SIDE_MIX = .70
LIP = 2                         # bright lip on the walkable side of the rim
LIP_LIFT = .38


def rim_masks(mask):
    """(side, lip) L masks for the open edges of one cloud cell."""
    side = Image.new('L', (SIZE, SIZE), 0)
    lip = Image.new('L', (SIZE, SIZE), 0)
    sp, lp = side.load(), lip.load()
    for y in range(SIZE):
        for x in range(SIZE):
            s = l = 0.0
            for bit, d, t in ((1, y, x), (2, SIZE - 1 - x, y), (4, SIZE - 1 - y, x), (8, x, y)):
                if mask & bit:
                    continue
                depth = RIM[bit] + SWELL * abs(math.sin(math.pi * (t + .5) / SCALLOP))
                if d < depth:
                    # Darker toward the open edge (the side falling away).
                    s = max(s, .55 + .45 * (1 - d / depth))
                elif d < depth + LIP:
                    l = max(l, 1 - (d - depth) / LIP)
            sp[x, y] = round(255 * s)
            lp[x, y] = round(255 * l)
    return side.filter(ImageFilter.GaussianBlur(.6)), lip.filter(ImageFilter.GaussianBlur(.5))


def printed(im):
    im = im.copy()
    px = im.load()
    for i in range(SIZE):
        for x, y in ((i, 0), (i, SIZE - 1), (0, i), (SIZE - 1, i)):
            r, g, b = px[x, y][:3]
            px[x, y] = (round(r * GRID), round(g * GRID), round(b * GRID))
    return im


def parity(im, p, factor):
    im = im.convert('RGB')
    if p:
        im = im.point(lambda v: round(v * factor))
    return im


def window(master, box):
    x0, y0 = box
    return master.crop((x0, y0, x0 + WINDOW, y0 + WINDOW)).resize((SIZE, SIZE), Image.Resampling.LANCZOS)


def cloud_tile(master, v, mask):
    cell = window(master, CLOUD_WINDOWS[v])
    cell = ImageEnhance.Contrast(cell).enhance(CLOUD_CONTRAST)
    cell = ImageEnhance.Brightness(cell).enhance(CLOUD_BRIGHTNESS)
    side, lip = rim_masks(mask)
    shaded = Image.blend(ImageChops.multiply(cell, Image.new('RGB', (SIZE, SIZE), SIDE)),
                         Image.new('RGB', (SIZE, SIZE), SIDE), .25)
    cell = Image.composite(Image.blend(cell, shaded, SIDE_MIX), cell, side)
    lifted = Image.blend(cell, Image.new('RGB', (SIZE, SIZE), (255, 255, 255)), LIP_LIFT)
    cell = Image.composite(lifted, cell, lip)
    return printed(cell)


def void_tile(master, v):
    return ImageEnhance.Brightness(window(master, VOID_WINDOWS[v])).enhance(VOID_BRIGHTNESS)


def lum(im):
    return round(ImageStat.Stat(im.convert('L')).mean[0], 1)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob('*.png'):
        old.unlink()
    with Image.open(CLOUD_MASTER) as m:
        cloud = m.convert('RGB')
    with Image.open(VOID_MASTER) as m:
        void = m.convert('RGB')
    files = []
    for p in (0, 1):
        for v in CLOUD_WINDOWS:
            for mask in range(16):
                name = f'cloud-{v}-{mask}-{p}.png'
                parity(cloud_tile(cloud, v, mask), p, PARITY_CLOUD).save(OUT / name)
                files.append(name)
        for v in VOID_WINDOWS:
            name = f'void-{v}-{p}.png'
            parity(void_tile(void, v), p, PARITY_VOID).save(OUT / name)
            files.append(name)
    files.sort()
    digest = hashlib.sha256(b''.join((OUT / f).read_bytes() for f in files)).hexdigest()[:12]
    lines = ['-- Generated by art/terrain-dream-s17/export.py.',
             '-- S17 dream family: Dreamscape cloud floor (3 variants x 16 masks) and dream void (2 variants), 2 parities.',
             'return {', ' ready=true,', f" revision='dream-s17-{digest}',", ' files={']
    lines += [f"  ['checker-revised+refined/dream/{f}']=true," for f in files]
    lines += [' },', '}']
    MANIFEST.write_text('\n'.join(lines) + '\n')
    for n in (48, 64, 96):
        (REVIEW / str(n)).mkdir(parents=True, exist_ok=True)
        for f in files:
            with Image.open(OUT / f) as im:
                im.resize((n, n), Image.Resampling.LANCZOS).save(REVIEW / str(n) / f)
    probe = ('cloud-a-15-0.png', 'cloud-b-15-0.png', 'cloud-c-15-0.png', 'cloud-a-15-1.png', 'cloud-a-0-0.png',
             'cloud-a-11-0.png', 'void-a-0.png', 'void-b-0.png', 'void-a-1.png')
    report = {'imagegen_calls': 2, 'runtime_files': len(files), 'revision': f'dream-s17-{digest}',
              'source_sha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in (CLOUD_MASTER, VOID_MASTER)},
              'luminance': {f: lum(Image.open(OUT / f)) for f in probe},
              'runtime_sha256': {f: hashlib.sha256((OUT / f).read_bytes()).hexdigest() for f in files}}
    (HERE / 'export-manifest.json').write_text(json.dumps(report, indent=1) + '\n')
    print(len(files), report['revision'], report['luminance'])


if __name__ == '__main__':
    main()
