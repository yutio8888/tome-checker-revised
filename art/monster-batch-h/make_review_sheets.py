"""Monster batch H review sheets: family comparisons at 48/64/96px (color and
grayscale) that include the already shipped related tokens, real-floor 48px
composites on six real refined floors, and masked-body luminance.
Read-only composition of existing exports; no creature pixels painted.
"""
from pathlib import Path
import subprocess
import tempfile

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ART = ROOT / 'art'
BIN = ROOT / 'tools/bin/export_token'
SIZES = (48, 64, 96)
PAD, LABEL = 14, 18
BG = (46, 50, 46, 255)
X = lambda i: ('export', HERE, i)
R = lambda i: ('runtime', i, None)
M = lambda p: ('master', HERE / p, None)

GROUPS = {
    'sandworm': [
        ('E sandworm-queen (shipped, context; fat tan frilled coil)', R('sandworm-queen')),
        ('H sandworm (slim open pale S-curve)', X('sandworm')),
        ('H sandworm-destroyer (thick dark-armoured closed ring)', X('sandworm-destroyer')),
        ('H sandworm-burrower (green, two arches over a sand heap)', X('sandworm-burrower')),
    ],
    'crystal': [
        ('G spellblaze-crystal (shipped, context; round purple cluster)', R('spellblaze-crystal')),
        ('H white-crystal (tall upright pale bouquet)', X('white-crystal')),
        ('H red-crystal (long horizontal blade fan)', X('red-crystal')),
        ('H crimson-crystal (two chunky blocky prisms)', X('crimson-crystal')),
        ('H sanguine-experiment v2 (smooth glossy blob, red cross-family check)', X('sanguine-experiment')),
    ],
    'plants': [
        ('venus-flytrap (shipped, context; red mouth)', R('venus-flytrap')),
        ('H poison-ivy (low open vine web)', X('poison-ivy')),
        ('H honey-tree (round canopy on trunk, hive)', X('honey-tree')),
        ('green-worm-mass (shipped green context)', R('green-worm-mass')),
    ],
    'humanoid-human': [
        ('E urkis (shipped, context)', R('urkis')),
        ('E celia (shipped, context)', R('celia')),
        ('G harno (shipped, context)', R('harno')),
        ('H necromancer OLD v1 (superseded: dark robe, lum 49.4)', M('masters/necromancer-v1.png')),
        ('H necromancer v2 (light slate-lavender robe, raised hand)', X('necromancer')),
    ],
    'experiments-horror': [
        ('E the-abomination (shipped, context)', R('the-abomination')),
        ('E half-finished-bone-giant (shipped, context)', R('half-finished-bone-giant')),
        ('H fleshy-experiment (lumpy pink-brown, trailing strands)', X('fleshy-experiment')),
        ('H boney-experiment (ivory spiky bone pile)', X('boney-experiment')),
        ('H sanguine-experiment OLD v1 (superseded: near-black, lum 34.1)', M('masters/sanguine-experiment-v1.png')),
        ('H sanguine-experiment v2 (bright scarlet glossy clot)', X('sanguine-experiment')),
    ],
}

FLOOR_TILES = {
    'sand': ROOT / 'data/gfx/refined/sand/floor0.png',
    'crystal': ROOT / 'data/gfx/refined/crystal/floor0.png',
    'grass': ROOT / 'data/gfx/refined/grass0.png',
    'cave': ROOT / 'data/gfx/refined/cave/floor-rock-1-0.png',
    'korpul': ROOT / 'data/gfx/refined/korpul/floor-a-0-0.png',
    'gloom': ROOT / 'data/gfx/refined/gloom/gloomy/floor0.png',
}
IDS = ['sandworm', 'sandworm-destroyer', 'sandworm-burrower', 'white-crystal', 'red-crystal', 'crimson-crystal',
       'poison-ivy', 'honey-tree', 'necromancer', 'fleshy-experiment', 'boney-experiment', 'sanguine-experiment']
FLOOR_ASSETS = [(i, X(i)) for i in IDS] + [
    ('necromancer OLD v1 (superseded: dark robe)', M('masters/necromancer-v1.png')),
    ('sanguine-experiment OLD v1 (superseded: near-black clot)', M('masters/sanguine-experiment-v1.png')),
]


def load(spec, size, scratch):
    kind, base, asset = spec
    if kind == 'export':
        return Image.open(base / 'sprites' / str(size) / f'{asset}.png').convert('RGBA')
    if kind == 'runtime':
        # Already-shipped catalog token, stored only at 128px in data/gfx/tokens;
        # resample here purely for side-by-side review composition.
        img = Image.open(ROOT / 'data/gfx/tokens' / f'{base}.png').convert('RGBA')
        return img.resize((size, size), Image.LANCZOS)
    target = Path(scratch) / f'{base.stem}-{size}.png'
    if not target.exists():
        subprocess.run([str(BIN), str(base), str(target), str(size)], check=True, capture_output=True)
    return Image.open(target).convert('RGBA')


def gray(image):
    out = image.convert('L').convert('RGBA')
    out.putalpha(image.getchannel('A'))
    return out


def sheet(name, rows, scratch):
    cell = sum(SIZES) + PAD * (len(SIZES) + 1)
    width = 620 + cell
    height = PAD + len(rows) * (max(SIZES) + PAD)
    for mode in ('color', 'grayscale'):
        canvas = Image.new('RGBA', (width, height), BG)
        draw = ImageDraw.Draw(canvas)
        y = PAD
        for label, spec in rows:
            draw.text((PAD, y + max(SIZES) // 2 - 6), label, fill=(232, 232, 226, 255))
            x = 620
            for size in SIZES:
                image = load(spec, size, scratch)
                if mode == 'grayscale':
                    image = gray(image)
                canvas.alpha_composite(image, (x, y + (max(SIZES) - size) // 2))
                x += size + PAD
            y += max(SIZES) + PAD
        out = HERE / 'review' / f'{name}-{mode}-48-64-96.png'
        out.parent.mkdir(exist_ok=True)
        canvas.convert('RGB').save(out)
        print(out.relative_to(ROOT))


def floor_sheet(scratch):
    """48px composite of every batch-H asset onto each real dark floor tile."""
    size = 48
    tiles = {name: Image.open(path).convert('RGBA') for name, path in FLOOR_TILES.items()}
    cell = size + PAD
    width = 380 + len(FLOOR_TILES) * cell + PAD
    height = PAD + len(FLOOR_ASSETS) * (size + PAD)
    canvas = Image.new('RGBA', (width, height), BG)
    draw = ImageDraw.Draw(canvas)
    # Header
    x = 380
    for name in FLOOR_TILES:
        draw.text((x, 2), name, fill=(232, 232, 226, 255))
        x += cell
    y = LABEL + PAD
    for label, spec in FLOOR_ASSETS:
        draw.text((PAD, y + size // 2 - 6), label, fill=(232, 232, 226, 255))
        token = load(spec, size, scratch)
        x = 380
        for name, tile in tiles.items():
            frame = tile.copy()
            frame.alpha_composite(token, (0, 0))
            canvas.alpha_composite(frame, (x, y))
            x += cell
        y += size + PAD
    out = HERE / 'review' / 'floor-readability-48.png'
    out.parent.mkdir(exist_ok=True)
    canvas.convert('RGB').save(out)
    print(out.relative_to(ROOT))
    big = canvas.convert('RGB').resize((canvas.width * 2, canvas.height * 2), Image.NEAREST)
    big.save(HERE / 'review' / 'floor-readability-48-x2.png')


def luminance(scratch):
    """Masked-body mean luminance (128px export, alpha>=180 within d<=0.55 of
    centre; same method as the Kryl-Feijan v1-vs-c comparison) next to the
    mean luminance of the two real floor tiles."""
    import json, math
    out = {'method': '128px export; alpha>=180 pixels with d<=0.55 of centre; L=0.299R+0.587G+0.114B', 'assets': {}, 'floors': {}}
    for name, path in FLOOR_TILES.items():
        img = Image.open(path).convert('RGB')
        px = list(img.getdata())
        out['floors'][name] = round(sum(0.299*r + 0.587*g + 0.114*b for r, g, b in px) / len(px), 2)
    for label, spec in FLOOR_ASSETS:
        img = load(spec, 128, scratch)
        vals = []
        for y in range(128):
            for x in range(128):
                r, g, b, a = img.getpixel((x, y))
                if a >= 180 and math.hypot(x + .5 - 64, y + .5 - 64) / 64 <= .55:
                    vals.append(0.299*r + 0.587*g + 0.114*b)
        out['assets'][label] = round(sum(vals) / len(vals), 2)
    (HERE / 'review' / 'luminance.json').write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))


if __name__ == '__main__':
    with tempfile.TemporaryDirectory(prefix='batch-h-review-') as scratch:
        for group, rows in GROUPS.items():
            sheet(group, rows, scratch)
        floor_sheet(scratch)
        luminance(scratch)
