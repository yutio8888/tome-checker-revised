"""UA first unique/boss batch: unchanged AE review geometry, 48/64/96 colour
and grayscale with shipped horror/undead siblings, ten real floors and the
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
 'grushnak-rejected-provenance': [('NATIVE Grushnak fixed portrait', ('file', ROOT.parents[2] / 'game/modules/tome/data/gfx/shockbolt/npc/humanoid_orc_grushnak__battlemaster_of_the_pride.png', None)), ('REJECTED unreported call 1; never admitted', M('superseded/grushnak-unreported-call-1-1.png')), ('REJECTED unreported call 2; never admitted', M('superseded/grushnak-unreported-call-2-1.png'))],
 'orc-bosses': [('shipped '+i,R(i)) for i in ('orc-berserker','orc-elite-fighter','orc-master-wyrmic','fiery-orc-wyrmic','icy-orc-wyrmic','orc-high-pyromancer','orc-high-cryomancer','golbug','massok')] + [('UA '+i,X(i)) for i in ('kra-tor','ukruk','gorbat','grushnak','vor')],
 'insect-bosses': [('shipped '+i,R(i)) for i in ('giant-black-ant','giant-army-ant','giant-carpenter-ant','weaver-young','weaver-queen','weaver-matriarch','weaver-patriarch','ungole')] + [('UA '+i,X(i)) for i in ('queen-ant','ninandra')],
 'horror-demon-bosses': [('shipped '+i,R(i)) for i in ('abyssal-horror','nightmare-horror','blade-horror','umbral-horror','champion-of-urh-rok','forge-giant','uruivellas','kryl-feijan')] + [('UA '+i,X(i)) for i in ('khulmanar','grgglck','ak-gishil')],
 'rework-before-after': [('SUPERSEDED v1 '+i,M('masters/'+i+'-v1.png')) if old else ('REWORK '+i,X(i)) for i in ('rungof','ninandra','grgglck') for old in (True,False)] + [('NATIVE portrait Grushnak', ('file', ROOT.parents[2] / 'game/modules/tome/data/gfx/shockbolt/npc/humanoid_orc_grushnak__battlemaster_of_the_pride.png',None)), ('REWORK grushnak',X('grushnak'))],
 'beast-bosses': [('shipped '+i,R(i)) for i in ('warg','wolf','great-wolf','the-withering-thing','faeros','ultimate-faeros')] + [('UA '+i,X(i)) for i in ('rungof','phoenix')],
}

RF = ROOT / 'data/gfx/refined/'
FLOOR_TILES = {
    'korpul stone A (dreadfell, grushnak-pride)': RF / 'korpul/floor-a-0-0.png',
    'cave rock (ardhungol)': RF / 'cave/floor-rock-1-0.png',
    'gloomy (heart-gloom unpurified)': RF / 'gloom/gloomy/floor0.png',
    'dreamy (heart-gloom purified)': RF / 'gloom/dreamy/floor0.png',
    'gothic stone (vor-pride)': RF / 'gothic/floor-a0.png',
    'snow ground': RF / 'snow/snow-ground0.png',
    'grass': RF / 'grass0.png',
    'bamboo hut (gorbat-pride)': RF / 'bamboo/floor0.png',
    'burnt ground': RF / 'burnt/floor0.png',
    'slime (slime-tunnels context)': RF / 'slime/floor0.png',
}
IDS = ['kra-tor','khulmanar','rungof','grgglck','queen-ant','ak-gishil','ninandra','phoenix','ukruk','gorbat','grushnak','vor']
ZONE_FLOORS = {i: [] for i in IDS}
ZONE_FLOORS.update({'rungof':['grass','gloomy','dreamy'], 'gorbat':['bamboo'], 'grushnak':['korpul'], 'vor':['gothic','burnt']})
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
    """48px composite of every batch-UA asset on each real floor tile, the tile
    resampled to the 48px cell the board draws (no tile is cropped). The whole
    9-row sheet is written at 1x; the 2x version is split into two halves."""
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
    with tempfile.TemporaryDirectory(prefix='batch-ua-review-', dir='/workspace/t-engine4/tmp/rotation/R11-scratch') as scratch:
        for group, rows in GROUPS.items():
            sheet(group, rows, scratch)
        floor_sheet(scratch)
        luminance(scratch)
