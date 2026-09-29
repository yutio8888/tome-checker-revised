"""Monster batch N review sheets: family comparisons at 48/64/96px (colour and
grayscale) including the already shipped related tokens, and real-floor 48px
composites on the refined floors of the creatures' own zones (korpul stone,
cave, rakshor, grass, flower meadow), plus masked-body luminance. Read-only
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
    'skeleton-ghoul-giant': [
        ('shipped skeleton-mage (dark-cloaked hunched skeleton)', R('skeleton-mage')),
        ('shipped skeleton-warrior (steel armour, sword)', R('skeleton-warrior')),
        ('N skeleton-magus (open bare skeleton, V arms, hand flames, cobalt ribbons)', X('skeleton-magus')),
        ('shipped ghoul (tan low crawler)', R('ghoul')),
        ('N ghast (pale grey-green hunched, dangling arms)', X('ghast')),
        ('N ghoulking (umber, gold crown, arms spread)', X('ghoulking')),
        ('shipped half-finished-bone-giant (thin, purple aura)', R('half-finished-bone-giant')),
        ('N bone-giant (dense ivory mass, big fists)', X('bone-giant')),
    ],
    'vampires': [
        ('shipped the-master (crimson robe, staff)', R('the-master')),
        ('N lesser-vampire (orange tunic, no cape)', X('lesser-vampire')),
        ('N vampire (crouching, scarlet cape)', X('vampire')),
        ('N master-vampire (tall indigo cloak)', X('master-vampire')),
        ('N elder-vampire (hooded burgundy, violet magic)', X('elder-vampire')),
    ],
    'wights-shadows': [
        ('shipped skeleton-warrior (steel armour, sword)', R('skeleton-warrior')),
        ('N forest-wight (green armour, axe, round shield)', X('forest-wight')),
        ('N grave-wight (pale teal reaching ghost)', X('grave-wight')),
        ('N shadow-stalker (slate-violet smoke, claws)', X('shadow-stalker')),
        ('N shade-of-telos (blue-violet archmage, crown, staff)', X('shade-of-telos')),
    ],
}

FLOOR_TILES = {
    'korpul stone A (dreadfell/halfling-ruins/telmur)': ROOT / 'data/gfx/refined/korpul/floor-a-0-0.png',
    'korpul stone B (dreadfell/halfling-ruins/telmur)': ROOT / 'data/gfx/refined/korpul/floor-b-0-0.png',
    'cave rock (ardhungol/keepsake caves)': ROOT / 'data/gfx/refined/cave/floor-rock-1-0.png',
    'cave mushroom (ardhungol)': ROOT / 'data/gfx/refined/cave/floor-mushroom-1-0.png',
    'rakshor A (rak-shor-pride)': ROOT / 'data/gfx/refined/rakshor/floor0.png',
    'rakshor B (rak-shor-pride)': ROOT / 'data/gfx/refined/rakshor/floor1.png',
    'grass (keepsake-meadow)': ROOT / 'data/gfx/refined/grass0.png',
    'flower meadow (keepsake-meadow)': ROOT / 'data/gfx/refined/flower0.png',
}
IDS = ['skeleton-magus', 'ghast', 'ghoulking', 'bone-giant', 'lesser-vampire', 'vampire', 'master-vampire', 'elder-vampire',
       'forest-wight', 'grave-wight', 'shadow-stalker', 'shade-of-telos']
# Zones each creature actually spawns in (source scopes) and the floor columns that apply.
KORPUL = ['korpul stone A', 'korpul stone B']
ZONE_FLOORS = {
    'skeleton-magus': KORPUL, 'ghast': KORPUL, 'ghoulking': KORPUL,
    'bone-giant': ['rakshor', 'korpul stone A', 'korpul stone B'],
    'lesser-vampire': KORPUL + ['cave'], 'vampire': KORPUL + ['cave'], 'master-vampire': KORPUL + ['cave'], 'elder-vampire': KORPUL + ['cave'],
    'forest-wight': KORPUL + ['cave'], 'grave-wight': KORPUL + ['cave'],
    'shadow-stalker': ['grass', 'flower', 'cave rock'],
    'shade-of-telos': KORPUL,
}
FLOOR_ASSETS = [(i, X(i)) for i in IDS]
# Superseded drafts (rejected before shipping) are appended here when a retry happens.
H = lambda pack, asset: ('file', ROOT / f'art/production/handoffs/monster-batch-n-{pack}/{asset}/imagegen-calls/call-1/export-128.png', None)
SUPERSEDED = [
    ('vampire OLD v1 (superseded: too dark, lum 42.8)', H(2, 'vampire')),
    ('elder-vampire OLD v2 (superseded: too dark, lum 42.6)', H(5, 'elder-vampire')),
    ('elder-vampire OLD v3 (superseded: dark wine robe, reads as The Master)', H(10, 'elder-vampire')),
    ('master-vampire OLD v1 (superseded: dark navy column)', H(2, 'master-vampire')),
    ('ghoulking OLD v1 (superseded: dark on real floors, lum 50.8)', H(1, 'ghoulking')),
    ('skeleton-magus OLD v2 (superseded: tiny figure)', H(4, 'skeleton-magus')),
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
    """48px composite of every batch-N asset on each real floor tile, the tile
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
    with tempfile.TemporaryDirectory(prefix='batch-n-review-') as scratch:
        for group, rows in GROUPS.items():
            sheet(group, rows, scratch)
        floor_sheet(scratch)
        luminance(scratch)
