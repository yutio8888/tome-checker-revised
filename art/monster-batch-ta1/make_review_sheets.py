"""Batch TA-1 review sheets: unchanged UA geometry, 48/64/96 colour and
grayscale with shipped mage/guard/yaech siblings, ten real floors and the
unchanged central masked-body luminance measurement. No creature painting.
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
 'angolwen-mages': [('shipped '+i, R(i)) for i in ('elven-mage','elven-tempest','orc-pyromancer','orc-cryomancer','necromancer','urkis')]
                   + [('TA1 '+i, X(i)) for i in ('apprentice-mage','pyromancer','cryomancer','geomancer','tempest')],
 'guards': [('shipped '+i, R(i)) for i in ('caravan-guard','elven-guard','mean-looking-elven-guard','human-sun-paladin','elven-warrior','norgan')]
           + [('TA1 '+i, X(i)) for i in ('human-guard','derth-guard','last-hope-guard','halfling-guard','dwarven-guard','elvala-guard')],
 'ring-of-blood': [('shipped '+i, R(i)) for i in ('yaech-hunter','yaech-mindslayer','yaech-psion','yaech-diver','bandit')]
                  + [('TA1 '+i, X(i)) for i in ('slaver','enthralled-slave')],
}

RF = ROOT / 'data/gfx/refined/'
FLOOR_TILES = {
    'town road A': RF / 'town/road0.png',
    'town fields A': RF / 'town/fields0.png',
    'grass': RF / 'grass0.png',
    'sand (Gates of Morning)': RF / 'sand/floor0.png',
    'snow ground': RF / 'snow/snow-ground0.png',
    'gothic stone A': RF / 'gothic/floor-a0.png',
    'korpul stone A': RF / 'korpul/floor-a-0-0.png',
    'cave rock': RF / 'cave/floor-rock-1-0.png',
    'gloomy (Heart of the Gloom)': RF / 'gloom/gloomy/floor0.png',
    'burnt ground': RF / 'burnt/floor0.png',
}
IDS = ['apprentice-mage','pyromancer','cryomancer','geomancer','tempest','human-guard','derth-guard',
       'last-hope-guard','halfling-guard','dwarven-guard','elvala-guard','slaver','enthralled-slave']
ZONE_FLOORS = {
    'apprentice-mage': ['town road', 'town fields', 'gothic'], 'human-guard': ['town road', 'town fields', 'sand'],
    'pyromancer': ['town fields', 'gothic'], 'cryomancer': ['town fields', 'snow'], 'geomancer': ['town fields', 'korpul'],
    'tempest': ['town fields', 'gloomy'],
    'derth-guard': ['town fields', 'grass'], 'last-hope-guard': ['town road', 'burnt'],
    'halfling-guard': ['town road', 'grass'], 'dwarven-guard': ['gothic', 'korpul'],
    'elvala-guard': ['sand', 'town road'], 'slaver': ['cave', 'burnt'], 'enthralled-slave': ['cave', 'town road'],
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
    """48px composite of every batch-TA1 asset on each real floor tile, the tile
    resampled to the 48px cell the board draws (no tile is cropped). The whole
    sheet is written at 1x; the 2x version is split into two halves."""
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
    import json, math
    out = {'method': '128px export; alpha>=180 pixels with d<=0.55 of centre; L=0.299R+0.587G+0.114B',
           'floor_minimum_for_body': 45.0, 'assets': {}, 'floors': {}}
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
    out['note'] = "floor-readability-48.png draws a yellow frame around the floors of each creature's own zones (ZONE_FLOORS)"
    (HERE / 'review' / 'luminance.json').write_text(json.dumps(out, indent=2))
    print(json.dumps(out['assets'], indent=2))
    pins = {name: {'path': str(path.relative_to(ROOT)), 'sha256': __import__('hashlib').sha256(path.read_bytes()).hexdigest()} for name, path in FLOOR_TILES.items()}
    (HERE / 'review' / 'floor-source-pins.json').write_text(json.dumps(pins, indent=2) + '\n')


if __name__ == '__main__':
    with tempfile.TemporaryDirectory(prefix='batch-ta1-review-', dir='/workspace/t-engine4/tmp/rotation/R19-scratch') as scratch:
        for group, rows in GROUPS.items():
            sheet(group, rows, scratch)
        floor_sheet(scratch)
        luminance(scratch)
