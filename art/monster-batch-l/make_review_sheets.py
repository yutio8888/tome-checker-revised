"""Monster batch L review sheets: family comparisons at 48/64/96px (color and
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
    'orcs': [
        ('shipped brotoq (near-black plate, raised blade)', R('brotoq')),
        ('shipped golbug (gold horned)', R('golbug')),
        ('shipped krogar (brown leather brute)', R('krogar')),
        ('shipped massok (dark horned helm)', R('massok')),
        ('L orc-warrior (olive, rust leather, curved scimitar)', X('orc-warrior')),
        ('L orc-soldier (grey spiked steel, broad axe)', X('orc-soldier')),
        ('L orc-archer (khaki leather, tall bow)', X('orc-archer')),
    ],
    'elves': [
        ('shipped rhaloren-inquisitor (steel plate)', R('rhaloren-inquisitor')),
        ('shipped kryl-feijan-acolyte (crimson robe, red orb)', R('kryl-feijan-acolyte')),
        ('shipped grand-corruptor (blue and red, horned)', R('grand-corruptor')),
        ('shipped fillarel-aldaren (golden robe)', R('fillarel-aldaren')),
        ('L elven-guard (bright green, gold, raised sword)', X('elven-guard')),
        ('L mean-looking-elven-guard (drab olive, hunched, low sword)', X('mean-looking-elven-guard')),
        ('L elven-mage (indigo robe, upright staff)', X('elven-mage')),
        ('L elven-tempest (sky blue, raised arm lightning)', X('elven-tempest')),
        ('L elven-blood-mage (slate robe, red stains, open hands)', X('elven-blood-mage')),
    ],
    'nagas-yaech-humans': [
        ('shipped naga-tidewarden (brown man, shield)', R('naga-tidewarden')),
        ('shipped naga-tidecaller (hooded dark)', R('naga-tidecaller')),
        ('shipped lady-nashva (teal)', R('lady-nashva')),
        ('shipped lady-zoisla (orange tail, trident)', R('lady-zoisla')),
        ('shipped murgol (spiky grey-blue yaech lord)', R('murgol')),
        ('shipped subject-z (human unique)', R('subject-z')),
        ('shipped the-possessed (human unique, tall)', R('the-possessed')),
        ('L naga-myrmidon (cobalt tail, steel armour, trident)', X('naga-myrmidon')),
        ('L naga-nereid (pale gold tail, lilac staff, tall)', X('naga-nereid')),
        ('L yaech-diver (small fluffy pale swimmer)', X('yaech-diver')),
        ('L kyless (olive tunic, violet-grey tendrils, tall)', X('kyless')),
    ],
}

FLOOR_TILES = {
    'korpul stone A (reknor/kryl-feijan/rhaloren)': ROOT / 'data/gfx/refined/korpul/floor-a-0-0.png',
    'korpul stone B (reknor/kryl-feijan/rhaloren)': ROOT / 'data/gfx/refined/korpul/floor-b-0-0.png',
    'grass (rhaloren-camp, keepsake-meadow)': ROOT / 'data/gfx/refined/grass0.png',
    'flower meadow (keepsake-meadow)': ROOT / 'data/gfx/refined/flower0.png',
    'bog (slazish-fen)': ROOT / 'data/gfx/refined/bog0-0-0.png',
    'underwater (murgol/temple-of-creation)': ROOT / 'data/gfx/refined/underwater/floor0.png',
    'cave rock (ardhungol)': ROOT / 'data/gfx/refined/cave/floor-rock-1-0.png',
    'cave mushroom (ardhungol)': ROOT / 'data/gfx/refined/cave/floor-mushroom-1-0.png',
    'burnt (mark-spellblaze)': ROOT / 'data/gfx/refined/burnt/floor0.png',
}
IDS = ['orc-warrior', 'orc-soldier', 'orc-archer', 'naga-myrmidon', 'elven-guard', 'mean-looking-elven-guard', 'naga-nereid',
       'kyless', 'elven-mage', 'elven-tempest', 'elven-blood-mage', 'yaech-diver']
# Zones each creature actually spawns in (source scopes) and the floor columns that apply.
ZONE_FLOORS = {
    'orc-warrior': ['korpul stone A', 'korpul stone B'], 'orc-soldier': ['korpul stone A', 'korpul stone B'],
    'orc-archer': ['korpul stone A', 'korpul stone B'],
    'naga-myrmidon': ['underwater', 'cave rock', 'cave mushroom'], 'naga-nereid': ['underwater', 'bog'],
    'elven-guard': ['korpul stone A', 'korpul stone B', 'grass'], 'mean-looking-elven-guard': ['korpul stone A', 'korpul stone B', 'grass'],
    'elven-mage': ['burnt', 'grass', 'korpul stone A'], 'elven-tempest': ['burnt', 'grass'],
    'elven-blood-mage': ['korpul stone A', 'korpul stone B', 'burnt'], 'yaech-diver': ['underwater'],
    'kyless': ['grass', 'flower meadow'],
}
FLOOR_ASSETS = [(i, X(i)) for i in IDS]
# Superseded drafts (rejected before shipping) are appended here when a retry happens.
SUPERSEDED = [
    ('kyless OLD v1 (superseded: dark, lum 48.1)', M('masters/kyless-v1.png')),
    ('elven-blood-mage OLD v1 (superseded: dark, lum 51.9)', M('masters/elven-blood-mage-v1.png')),
    ('naga-myrmidon OLD v1 (rejected at gate: radius 1.161)', ('file', ROOT / 'art/production/handoffs/monster-batch-l-1/naga-myrmidon/imagegen-calls/call-1/export-128.png', None)),
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
    """48px composite of every batch-L asset on each real floor tile, the tile
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
    with tempfile.TemporaryDirectory(prefix='batch-k-review-') as scratch:
        for group, rows in GROUPS.items():
            sheet(group, rows, scratch)
        floor_sheet(scratch)
        luminance(scratch)
