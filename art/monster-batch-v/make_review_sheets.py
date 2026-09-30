"""Monster batch V review sheets: family comparisons at 48/64/96px (colour and
grayscale) including the already shipped related crystal, spider, horror, orc, giant, demon and
yeek tokens, and real-floor 48px composites on the refined floors of the
creatures' own zones (cave, crystal, grass, gloom, maze, void, underwater,
burnt ground, Kor'Pul, rak-shor), plus masked-body luminance. Read-only
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
    'crystals-spiders': [
        ('shipped white-crystal', R('white-crystal')), ('shipped red-crystal', R('red-crystal')),
        ('shipped crimson-crystal', R('crimson-crystal')), ('shipped spellblaze-crystal', R('spellblaze-crystal')),
        ('V black-crystal (gunmetal columns, silver highlights)', X('black-crystal')),
        ('shipped giant-spider', R('giant-spider')), ('shipped spitting-spider', R('spitting-spider')), ('shipped chitinous-spider', R('chitinous-spider')),
        ('shipped fate-spinner', R('fate-spinner')), ('shipped weaver-young', R('weaver-young')), ('shipped nimisil', R('nimisil')),
        ('shipped gaeramarth', R('gaeramarth')), ('shipped ninurlhing', R('ninurlhing')), ('shipped fate-weaver', R('fate-weaver')),
        ('V faerlhing (amethyst, cage legs, rune, teal orb)', X('faerlhing')),
        ('V losselhing (frost fur, ice crest)', X('losselhing')),
    ],
    'horrors': [
        ('shipped dredgling', R('dredgling')), ('shipped drem', R('drem')), ('shipped dremling', R('dremling')),
        ('shipped weirdling-beast', R('weirdling-beast')), ('shipped horned-horror', R('horned-horror')), ('shipped brecklorn', R('brecklorn')),
        ('V dredge (salmon brute, fists planted)', X('dredge')),
        ('V drem-master (steel-blue mail, raised fist)', X('drem-master')),
        ('V bloated-horror (cream pear, red sores)', X('bloated-horror')),
    ],
    'orcs': [
        ('shipped orc-necromancer', R('orc-necromancer')), ('shipped orc-archer', R('orc-archer')), ('shipped orc-assassin', R('orc-assassin')),
        ('shipped orc-warrior', R('orc-warrior')), ('shipped orc-soldier', R('orc-soldier')),
        ('shipped orc-master-assassin', R('orc-master-assassin')), ('shipped orc-grand-master-assassin', R('orc-grand-master-assassin')),
        ('V orc-pyromancer (orange-red robe, fire staff)', X('orc-pyromancer')),
        ('V orc-cryomancer (ice-blue robe, ice fan)', X('orc-cryomancer')),
        ('V orc-blood-mage (rose robe, blood orb)', X('orc-blood-mage')),
    ],
    'giants-demons-yeeks': [
        ('shipped bone-giant', R('bone-giant')), ('shipped half-finished-bone-giant', R('half-finished-bone-giant')), ('shipped snow-giant', R('snow-giant')),
        ('V eternal-bone-giant (ivory, skulls, raised arm)', X('eternal-bone-giant')),
        ('shipped fire-imp', R('fire-imp')), ('shipped quasit', R('quasit')), ('shipped wretchling', R('wretchling')), ('shipped onilug', R('onilug')),
        ('V dolleg (brick-red, thorns, horns)', X('dolleg')),
        ('shipped yaech-diver', R('yaech-diver')), ('shipped yeek-wayist', R('yeek-wayist')),
        ('V yaech-hunter (umber fur, trident)', X('yaech-hunter')),
    ],
}

RF = ROOT / 'data/gfx/refined/'
FLOOR_TILES = {
    'cave rock (ardhungol, valley-moon-caverns)': RF / 'cave/floor-rock-1-0.png',
    'cave mushroom (ardhungol)': RF / 'cave/floor-mushroom-1-0.png',
    'crystal (scintillating-caves)': RF / 'crystal/floor0.png',
    'grass (old-forest, lake-nur)': RF / 'grass0.png',
    'gloom plain (deep-bellow)': RF / 'gloom/plain/floor0.png',
    'void floor (temporal-rift)': RF / 'void/floor0.png',
    'underwater floor (murgol-lair, lake-nur)': RF / 'underwater/floor0.png',
    'burnt ground (demon-plane)': RF / 'burnt/floor0.png',
    'korpul stone A (vor-armoury, telmur)': RF / 'korpul/floor-a-0-0.png',
    'rak-shor floor (rak-shor-pride)': RF / 'rakshor/floor0.png',
}
IDS = ['black-crystal', 'faerlhing', 'losselhing', 'dredge', 'drem-master', 'bloated-horror', 'orc-pyromancer', 'orc-cryomancer',
       'orc-blood-mage', 'dolleg', 'eternal-bone-giant', 'yaech-hunter']
ZONE_FLOORS = {
    'black-crystal': ['crystal', 'grass'], 'faerlhing': ['cave'], 'losselhing': ['cave'], 'dredge': ['void', 'cave'],
    'drem-master': ['gloom'], 'bloated-horror': ['underwater', 'cave', 'grass'],
    'orc-pyromancer': ['korpul', 'rak-shor'], 'orc-cryomancer': ['korpul', 'rak-shor'], 'orc-blood-mage': ['rak-shor'],
    'dolleg': ['cave', 'burnt'], 'eternal-bone-giant': ['rak-shor', 'korpul'], 'yaech-hunter': ['underwater'],
}
FLOOR_ASSETS = [(i, X(i)) for i in IDS]
H = lambda pack, asset, call=1: ('file', ROOT / f'art/production/handoffs/monster-batch-v-{pack}/{asset}/imagegen-calls/call-{call}/export-128.png', None)
SUPERSEDED = [
    ('drem-master OLD v1 (passed gate; replaced: dark steel-grey mail lost the silhouette at 48px)', H(2, 'drem-master')),
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
    """48px composite of every batch-V asset on each real floor tile, the tile
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
    with tempfile.TemporaryDirectory(prefix='batch-v-review-') as scratch:
        for group, rows in GROUPS.items():
            sheet(group, rows, scratch)
        floor_sheet(scratch)
        luminance(scratch)
