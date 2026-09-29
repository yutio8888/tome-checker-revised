"""Monster batch O review sheets: family comparisons at 48/64/96px (colour and
grayscale) including the already shipped related tokens, and real-floor 48px
composites on the refined floors of the creatures' own zones (korpul stone,
cave, rakshor, grass, flower meadow), plus masked-body luminance. Read-only
composition of existing exports; no creature pixels painted.
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
    'oozes': [
        ('shipped white-jelly (tall opaque dome)', R('white-jelly')),
        ('shipped green-ooze (flat puddle, round drops)', R('green-ooze')),
        ('shipped crimson-ooze (upright wave)', R('crimson-ooze')),
        ('shipped yellow-ooze (flame splash)', R('yellow-ooze')),
        ('O white-ooze', X('white-ooze')),
        ('O slimy-ooze', X('slimy-ooze')),
        ('O poison-ooze', X('poison-ooze')),
        ('O brittle-clear-ooze', X('brittle-clear-ooze')),
    ],
    'worms': [
        ('shipped sandworm', R('sandworm')),
        ('shipped sandworm-burrower', R('sandworm-burrower')),
        ('shipped gigantic-sandworm-tunneler (batch K)', R('gigantic-sandworm-tunneler')),
        ('O gigantic-corrosive-tunneler', X('gigantic-corrosive-tunneler')),
        ('O gigantic-gravity-worm', X('gigantic-gravity-worm')),
        ('shipped white-worm-mass', R('white-worm-mass')),
        ('shipped green-worm-mass', R('green-worm-mass')),
        ('O carrion-worm-mass', X('carrion-worm-mass')),
    ],
    'critters-demons-horrors': [
        ('shipped giant-white-mouse', R('giant-white-mouse')),
        ('O cute-little-bunny', X('cute-little-bunny')),
        ('shipped drem', R('drem')),
        ('shipped dremling', R('dremling')),
        ('O dredgling', X('dredgling')),
        ('O brecklorn', X('brecklorn')),
        ('shipped water-imp', R('water-imp')),
        ('O wretchling', X('wretchling')),
        ('O onilug', X('onilug')),
    ],
}

FLOOR_TILES = {
    'sand (sandworm-lair, briagh-lair)': ROOT / 'data/gfx/refined/sand/floor0.png',
    'cave rock (ardhungol)': ROOT / 'data/gfx/refined/cave/floor-rock-1-0.png',
    'cave mushroom (ardhungol)': ROOT / 'data/gfx/refined/cave/floor-mushroom-1-0.png',
    'grass (old-forest)': ROOT / 'data/gfx/refined/grass0.png',
    'flower meadow (old-forest)': ROOT / 'data/gfx/refined/flower0.png',
    'void (temporal-rift, mark-spellblaze)': ROOT / 'data/gfx/refined/void/floor0.png',
    'burnt (demon-plane, valley-moon-caverns)': ROOT / 'data/gfx/refined/burnt/floor0.png',
    'gloom plain creep (deep-bellow)': ROOT / 'data/gfx/refined/gloom/plain/creep-0-0.png',
    'korpul stone (ancient-elven-ruins)': ROOT / 'data/gfx/refined/korpul/floor-a-0-0.png',
}
IDS = ['white-ooze', 'gigantic-corrosive-tunneler', 'gigantic-gravity-worm', 'slimy-ooze', 'poison-ooze', 'carrion-worm-mass',
       'brittle-clear-ooze', 'cute-little-bunny', 'dredgling', 'onilug', 'wretchling', 'brecklorn']
SAND, CAVE = ['sand'], ['cave']
ZONE_FLOORS = {
    'white-ooze': SAND + CAVE, 'slimy-ooze': CAVE, 'poison-ooze': CAVE, 'brittle-clear-ooze': CAVE,
    'gigantic-corrosive-tunneler': SAND, 'gigantic-gravity-worm': SAND, 'carrion-worm-mass': ['void', 'korpul'],
    'cute-little-bunny': ['grass', 'flower'], 'dredgling': ['void'], 'onilug': ['burnt'], 'wretchling': ['burnt'],
    'brecklorn': ['gloom'],
}
FLOOR_ASSETS = [(i, X(i)) for i in IDS]
# Superseded drafts (rejected before shipping) are appended here when a retry happens.
H = lambda pack, asset: ('file', ROOT / f'art/production/handoffs/monster-batch-o-{pack}/{asset}/imagegen-calls/call-1/export-128.png', None)
SUPERSEDED = [
    ('cute-little-bunny OLD v1 (rejected by gate: ear tips radius 0.879)', H(4, 'cute-little-bunny')),
    ('onilug OLD v1 (superseded: thin faint column at 48px)', H(5, 'onilug')),
]
FLOOR_ASSETS += SUPERSEDED


def load(spec, size, scratch):
    kind, base, asset = spec
    if kind == 'export':
        return Image.open(base / 'sprites' / str(size) / f'{asset}.png').convert('RGBA')
    if kind == 'file':
        return Image.open(base).convert('RGBA').resize((size, size), Image.LANCZOS)
    if kind == 'runtime':
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
    """48px composite of every batch-N asset on each real floor tile, the tile
    resampled to the 48px cell the board draws (no tile is cropped)."""
    size = 48
    tiles = {name: Image.open(path).convert('RGBA').resize((size, size), Image.LANCZOS) for name, path in FLOOR_TILES.items()}
    cell = size + 6
    left = 380
    width = left + len(FLOOR_TILES) * cell + PAD
    height = LABEL + PAD + len(FLOOR_ASSETS) * (size + 6) + PAD
    canvas = Image.new('RGBA', (width, height), BG)
    draw = ImageDraw.Draw(canvas)
    x = left
    for i, name in enumerate(FLOOR_TILES):
        draw.text((x, 2 + (i % 2) * 11), name.split(' ')[0][:9], fill=(232, 232, 226, 255))
        x += cell
    y = LABEL + PAD
    for label, spec in FLOOR_ASSETS:
        draw.text((PAD, y + size // 2 - 6), label, fill=(232, 232, 226, 255))
        token = load(spec, size, scratch)
        x = left
        for name, tile in tiles.items():
            frame = tile.copy()
            frame.alpha_composite(token, (0, 0))
            canvas.alpha_composite(frame, (x, y))
            if label in ZONE_FLOORS and any(name.startswith(prefix) for prefix in ZONE_FLOORS[label]):
                draw.rectangle((x - 1, y - 1, x + size, y + size), outline=(255, 214, 64, 255))
            x += cell
        y += size + 6
    out = HERE / 'review' / 'floor-readability-48.png'
    out.parent.mkdir(exist_ok=True)
    canvas.convert('RGB').save(out)
    print(out.relative_to(ROOT))
    big = canvas.convert('RGB').resize((canvas.width * 2, canvas.height * 2), Image.NEAREST)
    big.save(HERE / 'review' / 'floor-readability-48-x2.png')


def luminance(scratch):
    """Masked-body mean luminance (128px export, alpha>=180 within d<=0.55 of
    centre) next to the mean luminance of each real floor tile."""
    import json, math
    out = {'method': '128px export; alpha>=180 pixels with d<=0.55 of centre; L=0.299R+0.587G+0.114B', 'floor_minimum_for_body': 45.0, 'assets': {}, 'floors': {}}
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
    out['zone_floors'] = {label: {name: out['floors'][name] for name in out['floors']
                                  if any(name.startswith(prefix) for prefix in prefixes)} for label, prefixes in ZONE_FLOORS.items()}
    out['note'] = 'floor-readability-48.png draws a yellow frame around the floors of each creature\'s own zones (ZONE_FLOORS)'
    (HERE / 'review' / 'luminance.json').write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))


if __name__ == '__main__':
    with tempfile.TemporaryDirectory(prefix='batch-o-review-') as scratch:
        for group, rows in GROUPS.items():
            sheet(group, rows, scratch)
        floor_sheet(scratch)
        luminance(scratch)
