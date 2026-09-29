"""Monster batch R review sheets: family comparisons at 48/64/96px (colour and
grayscale) including the already shipped related orcs, spiders, ants, imps,
elves, canines and horrors, and real-floor 48px composites on the refined
floors of the creatures' own zones (rak-shor, ardhungol cave, morass void,
meadow grass, sand, burnt ground, gloom pit), plus masked-body luminance. Read-only
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
    'orcs': [
        ('shipped krogar (brown armoured staff orc)', R('krogar')),
        ('shipped massok (black plate, horned helm, axe)', R('massok')),
        ('shipped orc-warrior (leather, curved blade)', R('orc-warrior')),
        ('shipped orc-soldier (grey plate, shield)', R('orc-soldier')),
        ('R orc-necromancer (hunched, staffless, soul flame)', X('orc-necromancer')),
        ('R rak-shor (upright, bone-crook staff, spiked collar)', X('rak-shor')),
        ('R warmaster-gnarg (horizontal greatsword brute)', X('warmaster-gnarg')),
        ('R orc-assassin (low crouch, two daggers)', X('orc-assassin')),
    ],
    'spiders-ants': [
        ('shipped weaver-hatchling (pale radial spider)', R('weaver-hatchling')),
        ('shipped weaver-queen (white radial spider)', R('weaver-queen')),
        ('shipped giant-spider (black)', R('giant-spider')),
        ('R weaver-young (curled ball, white spiral)', X('weaver-young')),
        ('R fate-spinner (wide star, thread ring)', X('fate-spinner')),
        ('shipped giant-yellow-ant (straight ant)', R('giant-yellow-ant')),
        ('shipped giant-blue-ant (straight ant)', R('giant-blue-ant')),
        ('shipped giant-carpenter-ant (big mandibles)', R('giant-carpenter-ant')),
        ('R giant-green-ant (C crescent, venom drop)', X('giant-green-ant')),
        ('R giant-red-ant (rearing T)', X('giant-red-ant')),
    ],
    'others': [
        ('shipped onilug (tall grey demon)', R('onilug')),
        ('shipped wretchling (small yellow imp)', R('wretchling')),
        ('R quasit (squat armoured, round shield)', X('quasit')),
        ('shipped elven-guard (green tunic, sword)', R('elven-guard')),
        ('R elven-warrior (silver plate, shield, axe)', X('elven-warrior')),
        ('shipped dire-wolf (brown, side-on)', R('dire-wolf')),
        ('shipped warg (grey, side-on)', R('warg')),
        ('R corrupted-war-dog (black, pouncing crouch)', X('corrupted-war-dog')),
        ('shipped slimy-crawler (green segmented)', R('slimy-crawler')),
        ('R grannor-vor (crescent slug, melted face)', X('grannor-vor')),
    ],
}

RF = ROOT / 'data/gfx/refined/'
FLOOR_TILES = {
    'rak-shor floor (rak-shor-pride)': RF / 'rakshor/floor0.png',
    'cave rock (ardhungol, valley-moon-caverns)': RF / 'cave/floor-rock-1-0.png',
    'cave mushroom (ardhungol)': RF / 'cave/floor-mushroom-1-0.png',
    'void floor (unhallowed-morass)': RF / 'void/floor0.png',
    'meadow grass (keepsake, old-forest)': RF / 'grass0.png',
    'sand (ritch-tunnels)': RF / 'sand/floor0.png',
    'burnt ground (charred-scar, demon-plane)': RF / 'burnt/floor0.png',
    'gloom pit floor (heart-gloom)': RF / 'gloom/pit/floor0.png',
}
IDS = ['orc-necromancer', 'rak-shor', 'warmaster-gnarg', 'orc-assassin', 'weaver-young', 'fate-spinner', 'giant-green-ant',
       'giant-red-ant', 'quasit', 'elven-warrior', 'corrupted-war-dog', 'grannor-vor']
ZONE_FLOORS = {
    'orc-necromancer': ['rak-shor', 'cave'], 'rak-shor': ['rak-shor'], 'warmaster-gnarg': ['cave', 'burnt'],
    'orc-assassin': ['rak-shor', 'cave'], 'weaver-young': ['cave', 'void'], 'fate-spinner': ['void'],
    'giant-green-ant': ['meadow', 'sand'], 'giant-red-ant': ['meadow', 'sand'], 'quasit': ['cave', 'burnt'],
    'elven-warrior': ['cave'], 'corrupted-war-dog': ['meadow'], 'grannor-vor': ['cave', 'gloom'],
}
FLOOR_ASSETS = [(i, X(i)) for i in IDS]
# Superseded drafts (rejected before shipping) are appended here when a retry happens.
H = lambda pack, asset, call=1: ('file', ROOT / f'art/production/handoffs/monster-batch-r-{pack}/{asset}/imagegen-calls/call-{call}/export-128.png', None)
SUPERSEDED = [
    ("rak-shor OLD v1 (rejected by gate: disc_overflow 0.987, the tall staff crossed the rim)", H(1, 'rak-shor')),
    ('warmaster-gnarg OLD v1 (rejected by gate: base_drift -9.24)', H(1, 'warmaster-gnarg')),
    ('orc-assassin OLD v1 (superseded: near-black navy, luminance 48.4, dark blob at 48px)', ('file', ROOT / 'art/monster-batch-r/masters/orc-assassin-v1.png', None)),
    ('orc-assassin OLD v2 (superseded: still near-black at 48px, luminance 54.8)', ('file', ROOT / 'art/monster-batch-r/masters/orc-assassin-v2.png', None)),
    ('corrupted-war-dog OLD v1 (superseded: near-black fur, dark blob at 48px, luminance 53.5)', ('file', ROOT / 'art/monster-batch-r/masters/corrupted-war-dog-v1.png', None)),
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
    """48px composite of every batch-R asset on each real floor tile, the tile
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
    with tempfile.TemporaryDirectory(prefix='batch-r-review-') as scratch:
        for group, rows in GROUPS.items():
            sheet(group, rows, scratch)
        floor_sheet(scratch)
        luminance(scratch)
