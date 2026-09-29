"""Monster batch J review sheets: family comparisons at 48/64/96px (color and
grayscale) that include the already shipped related tokens, real-floor 48px
composites on the real refined floors of the bosses' own zones (crystal/forest grass for Old Forest and the Rift forest level, gloomy/dreamy creep for Heart of the Gloom, void for Unhallowed Morass, underwater for Murgol Lair, korpul stone for Kor'Pul/Halfling Ruins/Thieves' Tunnels, burnt for Mark of the Spellblaze), and masked-body luminance.
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
    'crystals-orbs': [
        ('shipped white-crystal (tall pale bouquet)', R('white-crystal')),
        ('shipped red-crystal (blade fan)', R('red-crystal')),
        ('shipped crimson-crystal (two prisms)', R('crimson-crystal')),
        ('shipped spellblaze-crystal (round purple cluster)', R('spellblaze-crystal')),
        ('shipped spellblaze-simulacrum (person-shaped crystal)', R('spellblaze-simulacrum')),
        ('shipped malevolent-dimensional-jelly (starry window)', R('malevolent-dimensional-jelly')),
        ('J shardskin (broad golden crystal mass, trapped tree trunk)', X('shardskin')),
        ('J the-dreaming-one (smooth aqua glass sphere, lilac vortex)', X('the-dreaming-one')),
    ],
    'canines-spiders': [
        ('shipped wolf', R('wolf')), ('shipped great-wolf', R('great-wolf')), ('shipped dire-wolf', R('dire-wolf')),
        ('shipped white-wolf', R('white-wolf')), ('shipped warg', R('warg')), ('shipped fox', R('fox')),
        ('J the-withering-thing (emaciated mangy wolf, worms)', X('the-withering-thing')),
        ('shipped ungole (black spider)', R('ungole')),
        ('J weaver-queen (pale frost-white furry spider)', X('weaver-queen')),
    ],
    'aquatic': [
        ('shipped lady-zoisla (orange tail, gold trident)', R('lady-zoisla')),
        ('shipped naga-tidewarden', R('naga-tidewarden')),
        ('shipped naga-tidecaller (hooded)', R('naga-tidecaller')),
        ('J murgol (small finned yaech, red eyes, gold trident)', X('murgol')),
        ('J lady-nashva (teal-tailed naga, water orb, teal trident)', X('lady-nashva')),
    ],
    'humans': [
        ('shipped thief', R('thief')), ('shipped rogue', R('rogue')), ('shipped cutpurse', R('cutpurse')),
        ('shipped bandit', R('bandit')), ('shipped harno (hooded blue-grey)', R('harno')),
        ('J subject-z OLD v2 (superseded: passes gate but figure only a third of the disc)', M('masters/subject-z-v2.png')),
        ('J subject-z v3 (stiff upright, cream tunic, green trousers, short daggers)', X('subject-z')),
        ('J assassin-lord (olive fur mantle, crimson trousers, lunge)', X('assassin-lord')),
        ('J the-possessed OLD v1 (superseded: dark forest-green cloak, lum 49.4)', M('masters/the-possessed-v1.png')),
        ('J the-possessed v2 (green skull face, flame crown, sage-green cloak)', X('the-possessed')),
    ],
    'casters-brutes': [
        ('shipped necromancer', R('necromancer')), ('shipped kryl-feijan-acolyte', R('kryl-feijan-acolyte')),
        ('shipped rhaloren-inquisitor (armoured knight)', R('rhaloren-inquisitor')),
        ('shipped fillarel-aldaren', R('fillarel-aldaren')), ('shipped urkis', R('urkis')),
        ('J grand-corruptor OLD v1 (superseded: near-black navy robe, lum 42.7)', M('masters/grand-corruptor-v1.png')),
        ('J grand-corruptor v2 (horned cobalt cowl, crimson sash, red-orb staff)', X('grand-corruptor')),
        ('shipped krogar', R('krogar')), ('shipped norgan', R('norgan')), ('shipped bill', R('bill')),
        ('shipped the-abomination (pink flesh spire)', R('the-abomination')),
        ('J ben-cruthdar-abomination (pale hunched madman, battleaxe, cyan cracks)', X('ben-cruthdar-abomination')),
    ],
}

FLOOR_TILES = {
    'old-forest grass': ROOT / 'data/gfx/refined/grass0.png',
    'crystal (Old Forest CRYSTALINE)': ROOT / 'data/gfx/refined/crystal/floor0.png',
    'gloomy creep (heart-gloom)': ROOT / 'data/gfx/refined/gloom/gloomy/creep-0-0.png',
    'dreamy creep (heart-gloom purified)': ROOT / 'data/gfx/refined/gloom/dreamy/creep-0-0.png',
    'void (morass/rift L1)': ROOT / 'data/gfx/refined/void/floor0.png',
    'underwater (murgol)': ROOT / 'data/gfx/refined/underwater/floor0.png',
    'korpul stone (kor-pul/halfling/thieves)': ROOT / 'data/gfx/refined/korpul/floor-a-0-0.png',
    'burnt (spellblaze)': ROOT / 'data/gfx/refined/burnt/floor0.png',
}
IDS = ['shardskin', 'the-withering-thing', 'the-dreaming-one', 'weaver-queen', 'murgol', 'lady-nashva', 'the-possessed',
       'subject-z', 'grand-corruptor', 'assassin-lord', 'ben-cruthdar-abomination']
FLOOR_ASSETS = [(i, X(i)) for i in IDS] + [
    ('grand-corruptor OLD v1 (superseded)', M('masters/grand-corruptor-v1.png')),
    ('the-possessed OLD v1 (superseded)', M('masters/the-possessed-v1.png')),
    ('subject-z OLD v2 (superseded)', M('masters/subject-z-v2.png')),
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
    """48px composite of every batch-J asset onto each real dark floor tile."""
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
        draw.text((x, 2), name[:9], fill=(232, 232, 226, 255))
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
    with tempfile.TemporaryDirectory(prefix='batch-j-review-') as scratch:
        for group, rows in GROUPS.items():
            sheet(group, rows, scratch)
        floor_sheet(scratch)
        luminance(scratch)
