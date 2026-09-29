#!/usr/bin/env python3
"""S6 Eruan board terrain: palm and sand exits, derived deterministically.

Sources: the recorded ImageGen palm master (art/terrain-palm-s6/masters,
receipt in art/production/handoffs/palm-s6-v1/palm-tree/receipts) and the
existing reviewed board tiles it is composited on: the South Beach board sand
(data/gfx/refined/beach/sand0.png) and the forest board exit glyph
(data/gfx/refined/exit0.png, the same glyph the Caldera exits use).

Outputs (128 px RGB, parity 1 = x0.86 like the beach family) are written to
exports/runtime/ and byte-identically to data/gfx/refined/eruan/:
  palm-{a,b}{0,1}   the palm, cell-filling, over shaded beach sand
                    (b = mirrored, for rhythm in dense groves)
  exit-{up,down,world}{0,1}   the sand exits on board beach sand
The manifest pins master/source/output hashes and the measured values.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps, ImageStat
import hashlib, json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
GFX = ROOT / 'data/gfx/refined'
OUT = HERE / 'exports/runtime'
S = 128
PARITY = .86
MASTER = HERE / 'masters/palm-tree-v1.png'
SOURCES = {}


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def src(p):
    SOURCES[str(Path(p).relative_to(ROOT))] = sha(p)
    return p


def parity(im, p):
    im = im.convert('RGB')
    return ImageEnhance.Brightness(im).enhance(PARITY) if p else im


sand = Image.open(src(GFX / 'beach/sand0.png')).convert('RGB')
master = Image.open(src(MASTER)).convert('RGBA')
# Crop to the solid silhouette (alpha > 60): the faint outer haze of the
# generated fringe is dropped so the tree, not a halo, sets the scale.
solid = master.getchannel('A').point(lambda v: 255 if v > 60 else 0)
palm = master.crop(solid.getbbox())
palm.putalpha(Image.composite(palm.getchannel('A'), Image.new('L', palm.size, 0),
                              solid.crop(solid.getbbox()).filter(ImageFilter.MaxFilter(3))))

# Palm width fills the cell (frond tips just past the edges, like the board
# jungle/beach trees); the sand mound rests on the cell's bottom edge and the
# topmost frond tips are cut by the cell above, never the trunk or crown mass.
W = 136


def palm_tile(mirror):
    # Blocking ground: the beach sand darkened, with a broad contact shadow
    # under the crown, so the whole cell reads as an obstacle while the sand
    # still continues the open floor around it.
    base = ImageEnhance.Brightness(sand).enhance(.62).convert('RGBA')
    sh = Image.new('RGBA', (S, S))
    ImageDraw.Draw(sh).ellipse((4, 22, 124, 118), fill=(28, 20, 8, 150))
    base.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))
    im = ImageOps.mirror(palm) if mirror else palm
    h = round(im.height * W / im.width)
    im = im.resize((W, h), Image.Resampling.LANCZOS)
    base.alpha_composite(im, ((S - W) // 2, S - h + 3))
    return base


# Exit glyph: the forest board exit's pale arrow (and ring for the world exit),
# with a thin dark keyline so it holds on the lighter sand.
board_exit = Image.open(src(GFX / 'exit0.png')).convert('RGB')
glyph = Image.new('L', (S, S))
glyph.putdata([255 if r > 164 and g > 150 and b > 95 and r > g else 0 for r, g, b in board_exit.get_flattened_data()])
glyph = glyph.filter(ImageFilter.GaussianBlur(.4))


def exit_tile(kind):
    base = sand.copy()
    g = glyph.rotate(180) if kind == 'down' else glyph
    base.paste(Image.new('RGB', (S, S), (58, 38, 18)), (0, 0), g.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(.6)))
    base.paste(Image.new('RGB', (S, S), (246, 226, 168)), (0, 0), g)
    if kind == 'world':
        d = ImageDraw.Draw(base)
        d.ellipse((35, 35, 93, 93), outline=(58, 38, 18), width=4)
        d.ellipse((37, 37, 91, 91), outline=(246, 226, 168), width=2)
    return base


FILES = {}


def save(name, im):
    OUT.mkdir(parents=True, exist_ok=True)
    (GFX / 'eruan').mkdir(parents=True, exist_ok=True)
    a = OUT / name
    im.convert('RGB').save(a, optimize=True)
    b = GFX / 'eruan' / name
    b.write_bytes(a.read_bytes())
    FILES['eruan/' + name] = sha(b)


def lum(im, box=(0, 0, S, S)):
    return round(ImageStat.Stat(im.convert('L').crop(box)).mean[0], 1)


tiles = {}
for p in (0, 1):
    for key, mirror in (('a', False), ('b', True)):
        tiles[f'palm-{key}{p}'] = parity(palm_tile(mirror), p)
    for kind in ('up', 'down', 'world'):
        tiles[f'exit-{kind}{p}'] = parity(exit_tile(kind), p)
for name, im in tiles.items():
    save(name + '.png', im)

sand1 = parity(sand, 1)
metrics = {
    'beach_sand': {'0': lum(sand), '1': lum(sand1)},
    'palm_whole': {k: lum(v) for k, v in tiles.items() if k.startswith('palm')},
    # The 40% centre crop the live lit-pixel pairs use.
    'palm_centre40': {k: lum(v, (38, 38, 90, 90)) for k, v in tiles.items() if k.startswith('palm')},
    'exits': {k: lum(v) for k, v in tiles.items() if k.startswith('exit')},
}
metrics['parity_gap'] = {k: round(1 - lum(tiles[k + '1']) / lum(tiles[k + '0']), 4)
                         for k in ('palm-a', 'palm-b', 'exit-up', 'exit-down', 'exit-world')}
metrics['palm_vs_sand_gap'] = {p: round(1 - metrics['palm_whole'][f'palm-a{p}'] / metrics['beach_sand'][p], 4) for p in '01'}
(HERE / 'export-manifest.json').write_text(json.dumps({
    'master': {'path': str(MASTER.relative_to(ROOT)), 'sha256': sha(MASTER)},
    'sources': SOURCES, 'constants': {'S': S, 'PARITY': PARITY, 'palm_width': W},
    'files': FILES, 'metrics': metrics}, indent=1) + '\n')
print(json.dumps(metrics, indent=1))

# Review sheets (not runtime): every tile at 48/64/96 px, and a small Erúan
# shore at 48/64/96 px -- palm groves on sand, palms beside board deep water,
# the three sand exits -- using the runtime tiles and the renderer's own
# variant/parity rule ((x*17+y*7)%4<2 -> plain palm).
REVIEW = HERE / 'review'
REVIEW.mkdir(exist_ok=True)
names = sorted(tiles)
for sz in (48, 64, 96):
    sheet = Image.new('RGB', (len(names) * (sz + 4) + 4, sz + 8), (40, 40, 40))
    for i, n in enumerate(names):
        sheet.paste(tiles[n].resize((sz, sz), Image.Resampling.LANCZOS), (4 + i * (sz + 4), 4))
    sheet.save(REVIEW / f'contact-{sz}.png', optimize=True)
LAYOUT = ['..pp.p..~~~~', '.ppp...pp~~~', '..p..U....p~', 'p.....D...pp', 'pp.W..pp....', 'ppp..ppp..p.']


def field_tile(c, x, y):
    p = (x + y) % 2
    if c == 'p':
        return tiles[f"palm-{'a' if (x * 17 + y * 7) % 4 < 2 else 'b'}{p}"]
    if c == '~':
        m = sum(b for b, (dx, dy) in zip((1, 2, 4, 8), ((0, -1), (1, 0), (0, 1), (-1, 0)))
                if 0 <= y + dy < len(LAYOUT) and 0 <= x + dx < len(LAYOUT[0]) and LAYOUT[y + dy][x + dx] == '~'
                or not (0 <= y + dy < len(LAYOUT) and 0 <= x + dx < len(LAYOUT[0])))
        return Image.open(GFX / f'deep{m}-{p}-0.png').convert('RGB')
    if c in 'UDW':
        return tiles[f"exit-{ {'U': 'up', 'D': 'down', 'W': 'world'}[c]}{p}"]
    return parity(sand, p)


for sz in (48, 64, 96):
    field = Image.new('RGB', (len(LAYOUT[0]) * sz, len(LAYOUT) * sz))
    for y, row in enumerate(LAYOUT):
        for x, c in enumerate(row):
            field.paste(field_tile(c, x, y).resize((sz, sz), Image.Resampling.LANCZOS), (x * sz, y * sz))
    field.save(REVIEW / f'shore-{sz}.png', optimize=True)
