"""Monster batch S review sheets: family comparisons at 48/64/96px (colour and
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
    'knights-mages': [
        ('shipped elven-warrior (silver plate, kite shield, axe)', R('elven-warrior')),
        ('shipped elven-mage (purple robe, vertical staff)', R('elven-mage')),
        ('S human-sun-paladin (gold plate, sunburst shield, mace)', X('human-sun-paladin')),
        ('S high-sun-paladin-rodmour (ivory plate, violet cloak, planted sword)', X('high-sun-paladin-rodmour')),
        ('S aluin-the-fallen (hunched tarnished knight, dragging axe)', X('aluin-the-fallen')),
        ('S argoniel (plum robe, fire sphere, leaning)', X('argoniel')),
        ('S elandar (crimson cloak fan, crossed staves)', X('elandar')),
        ('S mindworm (sage robe, floating cross-legged)', X('mindworm')),
    ],
    'keepsake-elves': [
        ('shipped elven-guard (green tunic, sword, shield)', R('elven-guard')),
        ('S berethh (olive-grey cloak, full draw)', X('berethh')),
        ('S companion-warrior (russet lunge, teal scarf)', X('companion-warrior')),
        ('S companion-archer (green-gold kneeling archer)', X('companion-archer')),
    ],
    'undead': [
        ('shipped armoured-skeleton-warrior (bone in plate)', R('armoured-skeleton-warrior')),
        ('shipped shade-of-telos (upright ice-blue ghost)', R('shade-of-telos')),
        ('shipped ghoul (bare crawling ghoul)', R('ghoul')),
        ('S greater-mummy-lord (cream bandages, bronze mask, shield)', X('greater-mummy-lord')),
        ('S kors-fury (skull spectre, spiral tail)', X('kors-fury')),
        ('S borfast (armoured dwarf ghoul, round shield)', X('borfast')),
    ],
}

RF = ROOT / 'data/gfx/refined/'
FLOOR_TILES = {
    'burnt ground (charred-scar)': RF / 'burnt/floor0.png',
    'meadow grass (keepsake, trollmire)': RF / 'grass0.png',
    'caldera floor (noxious-caldera)': RF / 'caldera/floor0.png',
    'cave rock (ancient-elven-ruins, dreadfell)': RF / 'cave/floor-rock-1-0.png',
    'korpul floor A (ruins-kor-pul)': RF / 'korpul/floor-a-0-0.png',
    'korpul floor B (ruins-kor-pul)': RF / 'korpul/floor-b-0-0.png',
    'sand (dry ruins)': RF / 'sand/floor0.png',
}
IDS = ['human-sun-paladin', 'high-sun-paladin-rodmour', 'aluin-the-fallen', 'argoniel', 'elandar', 'mindworm', 'berethh',
       'companion-warrior', 'companion-archer', 'greater-mummy-lord', 'kors-fury', 'borfast']
ZONE_FLOORS = {
    'human-sun-paladin': ['burnt'], 'high-sun-paladin-rodmour': ['burnt'], 'aluin-the-fallen': ['meadow'],
    'argoniel': ['burnt'], 'elandar': ['burnt'], 'mindworm': ['caldera'], 'berethh': ['meadow'],
    'companion-warrior': ['meadow'], 'companion-archer': ['meadow'], 'greater-mummy-lord': ['cave'],
    'kors-fury': ['korpul'], 'borfast': ['cave'],
}
FLOOR_ASSETS = [(i, X(i)) for i in IDS]
# Superseded drafts (rejected by the gate before shipping) are appended here.
H = lambda pack, asset, call=1: ('file', ROOT / f'art/production/handoffs/monster-batch-s-{pack}/{asset}/imagegen-calls/call-{call}/export-128.png', None)
SUPERSEDED = [
    ('berethh OLD v1 (rejected by gate: base_drift -8.19)', H(3, 'berethh')),
    ('berethh OLD v2 (rejected by gate: base_drift +9.63, disc over-lightened)', H(5, 'berethh')),
    ('borfast OLD v1 (rejected by gate: base_drift -10.61, dark brown-bronze figure)', H(4, 'borfast')),
    ('aluin-the-fallen OLD v1 (superseded: dark rust-brown blob at 48px, luminance 59.1)', ('file', ROOT / 'art/monster-batch-s/masters/aluin-the-fallen-v1.png', None)),
    ('aluin-the-fallen OLD v2 (superseded: brown-grey plate still a mid-dark mass at 48px, luminance 64.0)', ('file', ROOT / 'art/monster-batch-s/masters/aluin-the-fallen-v2.png', None)),
    ('companion-warrior OLD v1 (superseded: mid-dark russet, luminance 62.2)', ('file', ROOT / 'art/monster-batch-s/masters/companion-warrior-v1.png', None)),
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
    with tempfile.TemporaryDirectory(prefix='batch-s-review-') as scratch:
        for group, rows in GROUPS.items():
            sheet(group, rows, scratch)
        floor_sheet(scratch)
        luminance(scratch)
