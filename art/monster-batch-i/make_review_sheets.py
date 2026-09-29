"""Monster batch I review sheets: family comparisons at 48/64/96px (color and
grayscale) that include the already shipped related tokens, real-floor 48px
composites on six real refined floors (daikara rock for Tempest Peak, korpul for Reknor, gloom/plain for Deep Bellow, crystal, cave, snow), and masked-body luminance.
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
    'oozes': [
        ('shipped red-ooze (bright red branching blob)', R('red-ooze')),
        ('shipped black-ooze', R('black-ooze')),
        ('shipped yellow-ooze (spiky flame blob)', R('yellow-ooze')),
        ('shipped blue-ooze (pale branching amoeba)', R('blue-ooze')),
        ('shipped green-jelly (olive stippled dome)', R('green-jelly')),
        ('shipped red-jelly (clover dome, dark seeds)', R('red-jelly')),
        ('shipped sanguine-experiment (red clot, cross-family)', R('sanguine-experiment')),
        ('I green-ooze (flat lime puddle, crest, 3 droplets)', X('green-ooze')),
        ('I crimson-ooze OLD v1 (superseded: dark wine blob, lum 40.1)', M('masters/crimson-ooze-v1.png')),
        ('I crimson-ooze v2 (light raspberry-rose rearing wave, drips, bud)', X('crimson-ooze')),
        ('I gelatinous-cube (rigid translucent cube)', X('gelatinous-cube')),
    ],
    'jellies': [
        ('shipped black-jelly (black tar mound)', R('black-jelly')),
        ('shipped blue-jelly (blue dome, spiral)', R('blue-jelly')),
        ('shipped white-jelly', R('white-jelly')),
        ('shipped yellow-jelly (gold bumpy dome)', R('yellow-jelly')),
        ('shipped green-jelly', R('green-jelly')),
        ('shipped black-ooze (dark flat blob)', R('black-ooze')),
        ('I malevolent-dimensional-jelly OLD v1 (superseded: dark indigo rim, lum 64.0)', M('masters/malevolent-dimensional-jelly-v1.png')),
        ('I malevolent-dimensional-jelly v2 (amethyst puddle, starry window)', X('malevolent-dimensional-jelly')),
        ('I gelatinous-cube (context)', X('gelatinous-cube')),
    ],
    'tempest-peak': [
        ('shipped lithfengel (brown horned demon/major)', R('lithfengel')),
        ('shipped boney-experiment (ivory spikes)', R('boney-experiment')),
        ('shipped bill (giant/troll)', R('bill')),
        ('shipped shivgoroth (blue ice elemental)', R('shivgoroth')),
        ('shipped sandworm-burrower (sand heap, context)', R('sandworm-burrower')),
        ('I harkor-zun-fragment (splinter heap, violet cracks)', X('harkor-zun-fragment')),
        ('I harkor-zun (stone humanoid, amber cracks)', X('harkor-zun')),
        ('I burb-snow-giant-champion (frost armour, fur, horned helm)', X('burb-snow-giant-champion')),
    ],
    'humanoids': [
        ('shipped krogar (orc, heavy armour)', R('krogar')),
        ('shipped fillarel-aldaren (elf, gold robe)', R('fillarel-aldaren')),
        ('shipped necromancer (bald human, slate robe)', R('necromancer')),
        ('shipped harno (hooded, two knives)', R('harno')),
        ('shipped celia', R('celia')),
        ('shipped urkis', R('urkis')),
        ('I norgan (squat bearded dwarf with maul)', X('norgan')),
        ('I kryl-feijan-acolyte OLD v1 (superseded: near-black robe, lum 41.3)', M('masters/kryl-feijan-acolyte-v1.png')),
        ('I kryl-feijan-acolyte v2 (silver-haired elf, mauve robe, blood orb, dagger)', X('kryl-feijan-acolyte')),
    ],
    'crawler': [
        ('shipped sandworm (slim pale S-curve)', R('sandworm')),
        ('shipped sandworm-destroyer', R('sandworm-destroyer')),
        ('shipped giant-white-ant', R('giant-white-ant')),
        ('shipped the-mouth (horror/corrupted)', R('the-mouth')),
        ('shipped green-worm-mass', R('green-worm-mass')),
        ('I slimy-crawler (plated many-legged, pincers, slime)', X('slimy-crawler')),
    ],
    'molds-crystals': [
        ('shipped green-mold', R('green-mold')),
        ('shipped brown-mold', R('brown-mold')),
        ('shipped shining-mold', R('shining-mold')),
        ('shipped grey-mold', R('grey-mold')),
        ('shipped boney-experiment (bare bone pile)', R('boney-experiment')),
        ('I zquikzshl OLD v1 (superseded: grey-green low-contrast bone heap)', M('masters/zquikzshl-v1.png')),
        ('I zquikzshl OLD v2 (superseded: green dome, read as a green mold)', M('masters/zquikzshl-v2.png')),
        ('I zquikzshl v3 (ivory rib-cage arch and skull on green-violet pad)', X('zquikzshl')),
        ('shipped spellblaze-crystal (round purple cluster)', R('spellblaze-crystal')),
        ('shipped white-crystal', R('white-crystal')),
        ('shipped crimson-crystal', R('crimson-crystal')),
        ('I spellblaze-simulacrum (person-shaped violet crystal)', X('spellblaze-simulacrum')),
    ],
}

FLOOR_TILES = {
    'daikara': ROOT / 'data/gfx/refined/daikara/rock-ground0.png',
    'korpul': ROOT / 'data/gfx/refined/korpul/floor-a-0-0.png',
    'gloom-plain': ROOT / 'data/gfx/refined/gloom/plain/creep-0-0.png',
    'crystal': ROOT / 'data/gfx/refined/crystal/floor0.png',
    'cave': ROOT / 'data/gfx/refined/cave/floor-rock-1-0.png',
    'snow': ROOT / 'data/gfx/refined/snow/snow-ground0.png',
}
IDS = ['green-ooze', 'crimson-ooze', 'gelatinous-cube', 'malevolent-dimensional-jelly', 'harkor-zun-fragment', 'harkor-zun',
       'burb-snow-giant-champion', 'norgan', 'slimy-crawler', 'spellblaze-simulacrum', 'kryl-feijan-acolyte', 'zquikzshl']
FLOOR_ASSETS = [(i, X(i)) for i in IDS] + [
    ('crimson-ooze OLD v1 (superseded)', M('masters/crimson-ooze-v1.png')),
    ('kryl-feijan-acolyte OLD v1 (superseded)', M('masters/kryl-feijan-acolyte-v1.png')),
    ('zquikzshl OLD v1 (superseded)', M('masters/zquikzshl-v1.png')),
    ('zquikzshl OLD v2 (superseded)', M('masters/zquikzshl-v2.png')),
    ('malevolent-dimensional-jelly OLD v1 (superseded)', M('masters/malevolent-dimensional-jelly-v1.png')),
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
    """48px composite of every batch-I asset onto each real dark floor tile."""
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
    with tempfile.TemporaryDirectory(prefix='batch-i-review-') as scratch:
        for group, rows in GROUPS.items():
            sheet(group, rows, scratch)
        floor_sheet(scratch)
        luminance(scratch)
