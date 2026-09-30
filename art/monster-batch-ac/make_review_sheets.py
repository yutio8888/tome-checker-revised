"""Monster batch AC (final batch) review sheets: family comparisons at 48/64/96px
(colour and grayscale) including the already shipped ghost, skeleton, vampire,
wight, giant, ogre, horror, ooze and spider tokens, and real-floor 48px composites
on the refined floors of the creatures' own zones (Dreadfell/vor-armoury stone,
cave, underwater, rak-shor, gothic), plus masked-body luminance. The 17-row floor
sheet is written whole at 1x and split into two 2x halves so no sheet is too tall.
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
    'ghosts-skeletons-vampires': [
        ('shipped banshee', R('banshee')), ('shipped dread', R('dread')), ('shipped kors-fury', R('kors-fury')),
        ('AC aletta-soultorn (violet ghost-woman, diadem)', X('aletta-soultorn')),
        ('AC ruin-banshee (acid-green clawed spectre)', X('ruin-banshee')),
        ('AC glacial-legion (frosted teardrop, red orb)', X('glacial-legion')),
        ('shipped skeleton-mage', R('skeleton-mage')), ('shipped skeleton-master-archer', R('skeleton-master-archer')),
        ('AC filio-flightfond (ivory sneak, sling and dagger)', X('filio-flightfond')),
        ('shipped vampire', R('vampire')), ('shipped master-vampire', R('master-vampire')), ('shipped elder-vampire', R('elder-vampire')),
        ('AC vampire-lord (ochre-gold noble, rapier)', X('vampire-lord')),
        ('AC arch-zephyr (storm archer, lightning bow)', X('arch-zephyr')),
    ],
    'orcs-giants-wights': [
        ('shipped orc-pyromancer', R('orc-pyromancer')), ('shipped orc-cryomancer', R('orc-cryomancer')),
        ('AC orc-high-pyromancer (crest mitre, fire ring)', X('orc-high-pyromancer')),
        ('AC orc-high-cryomancer (ice crown, snowflake staff)', X('orc-high-cryomancer')),
        ('shipped bone-giant', R('bone-giant')), ('shipped heavy-bone-giant', R('heavy-bone-giant')), ('shipped ghoulking', R('ghoulking')),
        ('AC rotting-titan (mauve flesh and stone slabs)', X('rotting-titan')),
        ('AC heavy-sentinel (furnace bone giant)', X('heavy-sentinel')),
        ('shipped forest-wight', R('forest-wight')), ('shipped barrow-wight', R('barrow-wight')),
        ('AC void-spectre (rose-red hooded wraith)', X('void-spectre')),
        ('shipped ogre-pounder', R('ogre-pounder')), ('shipped ogre-mauler', R('ogre-mauler')), ('shipped necrotic-mass', R('necrotic-mass')),
        ('AC degenerated-ogric-mass (ochre flesh heap)', X('degenerated-ogric-mass')),
        ('AC ogric-abomination (grey-mauve ogre, stone arm)', X('ogric-abomination')),
    ],
    'horrors-spiders': [
        ('shipped entrenched-horror', R('entrenched-horror')), ('shipped weirdling-beast', R('weirdling-beast')), ('shipped horned-horror', R('horned-horror')),
        ('shipped green-ooze', R('green-ooze')), ('shipped bloated-horror', R('bloated-horror')),
        ('AC oozing-horror (lime slime mound, many eyes)', X('oozing-horror')),
        ('AC abyssal-horror (indigo tentacle knot, red eyes)', X('abyssal-horror')),
        ('AC umbral-horror (grey-lilac shadow stalker)', X('umbral-horror')),
        ('shipped giant-spider', R('giant-spider')), ('shipped ungole', R('ungole')), ('shipped chitinous-spider', R('chitinous-spider')),
        ('AC ungolmor (armoured dome spider, amber eyes)', X('ungolmor')),
    ],
}

RF = ROOT / 'data/gfx/refined/'
FLOOR_TILES = {
    'korpul stone A (dreadfell, vor-armoury)': RF / 'korpul/floor-a-0-0.png',
    'cave rock (ardhungol)': RF / 'cave/floor-rock-1-0.png',
    'underwater floor (lake-nur)': RF / 'underwater/floor0.png',
    'rak-shor floor (rak-shor-pride)': RF / 'rakshor/floor0.png',
    'gothic stone (conclave-vault nearest)': RF / 'gothic/floor-a0.png',
    'snow ground': RF / 'snow/snow-ground0.png',
    'grass': RF / 'grass0.png',
    'caldera': RF / 'caldera/floor0.png',
    'burnt ground': RF / 'burnt/floor0.png',
    'void floor': RF / 'void/floor0.png',
}
IDS = ['aletta-soultorn', 'ruin-banshee', 'filio-flightfond', 'orc-high-pyromancer', 'orc-high-cryomancer', 'glacial-legion', 'arch-zephyr', 'rotting-titan',
       'heavy-sentinel', 'void-spectre', 'oozing-horror', 'abyssal-horror', 'ungolmor', 'umbral-horror', 'vampire-lord', 'degenerated-ogric-mass', 'ogric-abomination']
# Approximate: dreadfell shares the korpul stone family here and conclave-vault uses the nearest gothic stone.
ZONE_FLOORS = {
    'aletta-soultorn': ['korpul'], 'filio-flightfond': ['korpul'], 'vampire-lord': ['korpul'], 'orc-high-pyromancer': ['korpul'], 'orc-high-cryomancer': ['korpul'],
    'ruin-banshee': ['rak-shor'], 'glacial-legion': ['rak-shor'], 'arch-zephyr': ['rak-shor'], 'rotting-titan': ['rak-shor'], 'heavy-sentinel': ['rak-shor'], 'void-spectre': ['rak-shor'],
    'oozing-horror': ['underwater'], 'abyssal-horror': ['underwater'], 'umbral-horror': ['underwater'], 'ungolmor': ['cave'],
    'degenerated-ogric-mass': ['gothic'], 'ogric-abomination': ['gothic'],
}
FLOOR_ASSETS = [(i, X(i)) for i in IDS]
SUPERSEDED = []


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
    """48px composite of every batch-AC asset on each real floor tile, the tile
    resampled to the 48px cell the board draws (no tile is cropped). The whole
    17-row sheet is written at 1x; the 2x version is split into two halves."""
    size = 48
    tiles = {name: Image.open(path).convert('RGBA').resize((size, size), Image.LANCZOS) for name, path in FLOOR_TILES.items()}
    cell = size + 6
    left = 380

    def render(assets):
        width = left + len(FLOOR_TILES) * cell + PAD
        height = LABEL + PAD + len(assets) * (size + 6) + PAD
        canvas = Image.new('RGBA', (width, height), BG)
        draw = ImageDraw.Draw(canvas)
        x = left
        for i, name in enumerate(FLOOR_TILES):
            draw.text((x, 2 + (i % 2) * 11), name.split(' ')[0][:9], fill=(232, 232, 226, 255))
            x += cell
        y = LABEL + PAD
        for label, spec in assets:
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
        return canvas.convert('RGB')

    review = HERE / 'review'
    review.mkdir(exist_ok=True)
    render(FLOOR_ASSETS).save(review / 'floor-readability-48.png')
    print((review / 'floor-readability-48.png').relative_to(ROOT))
    half = (len(FLOOR_ASSETS) + 1) // 2
    for name, assets in (('floor-readability-48-x2.png', FLOOR_ASSETS[:half]), ('floor-readability-48-x2-b.png', FLOOR_ASSETS[half:])):
        sheet_ = render(assets)
        sheet_.resize((sheet_.width * 2, sheet_.height * 2), Image.NEAREST).save(review / name)
        print((review / name).relative_to(ROOT))


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
    with tempfile.TemporaryDirectory(prefix='batch-ac-review-') as scratch:
        for group, rows in GROUPS.items():
            sheet(group, rows, scratch)
        floor_sheet(scratch)
        luminance(scratch)
