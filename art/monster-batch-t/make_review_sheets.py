"""Monster batch T review sheets: family comparisons at 48/64/96px (colour and
grayscale) including the already shipped related elves, mages, guards and undead,
and real-floor 48px composites on the refined floors of the creatures' own
zones (burnt ground, meadow grass, caldera, cave rock, Kor'Pul floors, sand),
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
    'humans': [
        ('shipped cutpurse', R('cutpurse')), ('shipped rogue', R('rogue')), ('shipped thief', R('thief')), ('shipped bandit', R('bandit')),
        ('shipped human-sun-paladin (gold plate, round shield)', R('human-sun-paladin')),
        ('T caravan-merchant (blue, wide hat, coin purse)', X('caravan-merchant')),
        ('T caravan-guard (mail, rectangular shield, sword)', X('caravan-guard')),
        ('T caravan-porter (crates on back)', X('caravan-porter')),
        ('T lost-merchant (cowering, rucksack, lantern)', X('lost-merchant')),
    ],
    'canines-small': [
        ('shipped dire-wolf (same native PNG)', R('dire-wolf')),
        ('shipped corrupted-war-dog (same native PNG)', R('corrupted-war-dog')),
        ('shipped wolf', R('wolf')),
        ('T war-dog (sandy mastiff, head-on, red cloth)', X('war-dog')),
        ('T pumpkin (orange sitting cat)', X('pumpkin')),
        ('T yeek-wayist (white yeek, floating sword)', X('yeek-wayist')),
    ],
    'bosses': [
        ('shipped naga-myrmidon', R('naga-myrmidon')), ('shipped naga-tidewarden', R('naga-tidewarden')), ('shipped lady-zoisla', R('lady-zoisla')),
        ('shipped quasit', R('quasit')), ('shipped water-imp', R('water-imp')),
        ('shipped giant-spider', R('giant-spider')), ('shipped fate-spinner', R('fate-spinner')),
        ('T slasul (crested naga king, green tail)', X('slasul')),
        ('T draebor (shaggy imp with fireball)', X('draebor')),
        ('T nimisil (silver spider, gem crown)', X('nimisil')),
    ],
    'horrors': [
        ('shipped the-mouth', R('the-mouth')), ('shipped horned-horror', R('horned-horror')),
        ('shipped shade-of-telos', R('shade-of-telos')), ('shipped the-dreaming-one', R('the-dreaming-one')),
        ('T weirdling-beast (headless warty tentacles)', X('weirdling-beast')),
        ('T fortress-shadow (aqua jellyfish dome)', X('fortress-shadow')),
    ],
}

RF = ROOT / 'data/gfx/refined/'
FLOOR_TILES = {
    'meadow grass (keepsake-meadow/dream)': RF / 'grass0.png',
    'cave rock (keepsake cave, temple, thieves)': RF / 'cave/floor-rock-1-0.png',
    'korpul stone A (maze, halfling-ruins stone)': RF / 'korpul/floor-a-0-0.png',
    'underwater floor (temple-of-creation)': RF / 'underwater/floor0.png',
    'shertul floor (shertul-fortress)': RF / 'shertul/floor0.png',
    'burnt ground (demon-plane)': RF / 'burnt/floor0.png',
}
IDS = ['caravan-merchant', 'caravan-guard', 'caravan-porter', 'lost-merchant', 'war-dog', 'yeek-wayist', 'nimisil', 'slasul',
       'draebor', 'weirdling-beast', 'fortress-shadow', 'pumpkin']
ZONE_FLOORS = {
    'caravan-merchant': ['meadow'], 'caravan-guard': ['meadow'], 'caravan-porter': ['meadow'], 'lost-merchant': ['korpul'],
    'war-dog': ['meadow', 'cave'], 'yeek-wayist': ['korpul'], 'nimisil': ['korpul'], 'slasul': ['underwater'],
    'draebor': ['burnt'], 'weirdling-beast': ['shertul'], 'fortress-shadow': ['shertul'], 'pumpkin': ['shertul'],
}
FLOOR_ASSETS = [(i, X(i)) for i in IDS]
H = lambda pack, asset, call=1: ('file', ROOT / f'art/production/handoffs/monster-batch-t-{pack}/{asset}/imagegen-calls/call-{call}/export-128.png', None)
SUPERSEDED = [
    ('fortress-shadow OLD v1 (rejected by gate: base_drift -10.81, disc darkened under tendrils)', H(4, 'fortress-shadow')),
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
    """48px composite of every batch-S asset on each real floor tile, the tile
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
    with tempfile.TemporaryDirectory(prefix='batch-t-review-') as scratch:
        for group, rows in GROUPS.items():
            sheet(group, rows, scratch)
        floor_sheet(scratch)
        luminance(scratch)
