"""Monster batch Q review sheets: family comparisons at 48/64/96px (colour and
grayscale) including the already shipped related dragons, and real-floor 48px
composites on the refined floors of the creatures' own zones (Daikara/Tempest
caldera, flooded-cave water, temporal-rift void, ardhungol cave rock),
plus masked-body luminance. Read-only
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
    'drakes': [
        ('shipped varsha (crimson coiled, folded wings)', R('varsha')),
        ('Q fire-drake-hatchling (upright sitting)', X('fire-drake-hatchling')),
        ('Q fire-drake (stalking, delta wings, flame)', X('fire-drake')),
        ('shipped rantha (pale silver-blue coiled)', R('rantha')),
        ('Q cold-drake-hatchling (low pounce)', X('cold-drake-hatchling')),
        ('Q cold-drake (hunched boulder, folded wings)', X('cold-drake')),
        ('Q storm-drake-hatchling (reared, flared wings)', X('storm-drake-hatchling')),
        ('Q storm-drake (diagonal dart)', X('storm-drake')),
        ('Q venom-drake-hatchling (S coil)', X('venom-drake-hatchling')),
        ('Q venom-drake (hunched, low spitting head)', X('venom-drake')),
    ],
    'sand-and-uniques': [
        ('shipped corrupted-sand-wyrm (brown S coil)', R('corrupted-sand-wyrm')),
        ('shipped sandworm-destroyer', R('sandworm-destroyer')),
        ('Q sand-drake (pale wingless lizard)', X('sand-drake')),
        ('Q briagh (golden cobra coil, violet frill)', X('briagh')),
        ('shipped rantha (Worm)', R('rantha')),
        ('Q rantha-abomination (slate, cyan cracks)', X('rantha-abomination')),
        ('Q ukllmswwik (shark-headed sea dragon, trident)', X('ukllmswwik')),
        ('Q cold-drake (for the water/ice contrast)', X('cold-drake')),
    ],
}

RF = ROOT / 'data/gfx/refined/'
FLOOR_TILES = {
    'daikara rock (daikara, tempest-peak)': RF / 'daikara/rock-ground0.png',
    'snow ground (daikara snow)': RF / 'snow/snow-ground0.png',
    'burnt ground (charred-scar)': RF / 'burnt/floor0.png',
    'sand (sandworm, briagh)': RF / 'sand/floor0.png',
    'caldera ground (noxious-caldera)': RF / 'caldera/floor0.png',
    'underwater floor (flooded cave)': RF / 'underwater/floor0.png',
    'water (flooded cave)': ROOT / 'data/gfx/water0.png',
    'void floor (temporal-rift)': RF / 'void/floor0.png',
    'cave rock (ardhungol)': RF / 'cave/floor-rock-1-0.png',
}
IDS = ['fire-drake-hatchling', 'cold-drake-hatchling', 'storm-drake-hatchling', 'sand-drake', 'venom-drake-hatchling', 'rantha-abomination',
       'briagh', 'ukllmswwik', 'fire-drake', 'storm-drake', 'cold-drake', 'venom-drake']
DAI = ['daikara', 'snow']
ZONE_FLOORS = {
    'fire-drake-hatchling': DAI + ['burnt'], 'fire-drake': ['burnt'] + DAI,
    'cold-drake-hatchling': DAI + ['cave'], 'cold-drake': DAI + ['cave'],
    'storm-drake-hatchling': ['daikara', 'cave'], 'storm-drake': ['daikara', 'cave'],
    'sand-drake': ['sand'], 'briagh': ['sand'],
    'venom-drake-hatchling': ['caldera', 'cave'], 'venom-drake': ['caldera', 'cave'],
    'rantha-abomination': ['void'], 'ukllmswwik': ['underwater', 'water'],
}
FLOOR_ASSETS = [(i, X(i)) for i in IDS]
# Superseded drafts (rejected before shipping) are appended here when a retry happens.
H = lambda pack, asset, call=1: ('file', ROOT / f'art/production/handoffs/monster-batch-q-{pack}/{asset}/imagegen-calls/call-{call}/export-128.png', None)
SUPERSEDED = [
    ('ukllmswwik OLD v1 (rejected by gate: disc_overflow 0.908, trident and fin crossed the rim)', H(2, 'ukllmswwik')),
    ('storm-drake OLD v1 (superseded: thin muted violet, low contrast at 48px)', ('file', ROOT / 'art/monster-batch-q/masters/storm-drake-v1.png', None)),
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
    """48px composite of every batch-Q asset on each real floor tile, the tile
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
    with tempfile.TemporaryDirectory(prefix='batch-q-review-') as scratch:
        for group, rows in GROUPS.items():
            sheet(group, rows, scratch)
        floor_sheet(scratch)
        luminance(scratch)
