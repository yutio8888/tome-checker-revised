"""Monster batch P review sheets: family comparisons at 48/64/96px (colour and
grayscale) including the already shipped related tokens, and real-floor 48px
composites on the refined floors of the creatures' own zones (Daikara/Tempest
Peak rock and snow, korpul stone for the crypt and vault, ardhungol cave rock),
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
    'snow-giants': [
        ('shipped burb-snow-giant-champion (silver plate, horned helm)', R('burb-snow-giant-champion')),
        ('shipped bone-giant (batch N)', R('bone-giant')),
        ('P snow-giant (bald, maul low)', X('snow-giant')),
        ('P snow-giant-thunderer (bearded, lightning fists)', X('snow-giant-thunderer')),
        ('P snow-giant-boulder-thrower (boulder)', X('snow-giant-boulder-thrower')),
        ('P snow-giant-chieftain (horned, fur mantle)', X('snow-giant-chieftain')),
    ],
    'minotaur-trolls': [
        ('shipped minotaur-maze (dark brown, axe low)', R('minotaur-maze')),
        ('shipped horned-horror', R('horned-horror')),
        ('P minotaur (piebald cream+black, axe across chest)', X('minotaur')),
        ('shipped forest-troll', R('forest-troll')),
        ('shipped stone-troll', R('stone-troll')),
        ('shipped cave-troll', R('cave-troll')),
        ('P mountain-troll (rust-brown, fists up)', X('mountain-troll')),
        ('P mountain-troll-thunderer (teal, lightning)', X('mountain-troll-thunderer')),
    ],
    'ogres': [
        ('shipped cave-troll', R('cave-troll')),
        ('P ogre-guard (tan, blue trousers, maul)', X('ogre-guard')),
        ('P ogre-mauler (brick red, gold fist)', X('ogre-mauler')),
        ('P ogre-rune-spinner (orange, runes, fire)', X('ogre-rune-spinner')),
        ('P ogre-pounder (blue, arms wide)', X('ogre-pounder')),
        ('P healer-astelrid (violet robe, plaster club)', X('healer-astelrid')),
    ],
}

FLOOR_TILES = {
    'daikara rock (daikara, tempest-peak)': ROOT / 'data/gfx/refined/daikara/rock-ground0.png',
    'snow ground (daikara snow)': ROOT / 'data/gfx/refined/snow/snow-ground0.png',
    'korpul stone A (crypt/vault/reknor stone)': ROOT / 'data/gfx/refined/korpul/floor-a-0-0.png',
    'korpul stone B (crypt/vault/reknor stone)': ROOT / 'data/gfx/refined/korpul/floor-b-0-0.png',
    'cave rock (ardhungol)': ROOT / 'data/gfx/refined/cave/floor-rock-1-0.png',
    'cave mushroom (ardhungol)': ROOT / 'data/gfx/refined/cave/floor-mushroom-1-0.png',
}
IDS = ['snow-giant', 'snow-giant-thunderer', 'snow-giant-boulder-thrower', 'snow-giant-chieftain', 'minotaur', 'mountain-troll',
       'mountain-troll-thunderer', 'ogre-guard', 'ogre-mauler', 'ogre-rune-spinner', 'ogre-pounder', 'healer-astelrid']
SNOWY = ['daikara', 'snow']
KORPUL = ['korpul stone A', 'korpul stone B']
ZONE_FLOORS = {
    'snow-giant': SNOWY, 'snow-giant-thunderer': SNOWY, 'snow-giant-boulder-thrower': SNOWY, 'snow-giant-chieftain': SNOWY,
    'minotaur': ['cave'] + KORPUL, 'mountain-troll': KORPUL + ['cave'], 'mountain-troll-thunderer': KORPUL,
    'ogre-guard': KORPUL, 'ogre-mauler': KORPUL, 'ogre-rune-spinner': KORPUL, 'ogre-pounder': KORPUL, 'healer-astelrid': KORPUL,
}
FLOOR_ASSETS = [(i, X(i)) for i in IDS]
# Superseded drafts (rejected before shipping) are appended here when a retry happens.
H = lambda pack, asset, call=1: ('file', ROOT / f'art/production/handoffs/monster-batch-p-{pack}/{asset}/imagegen-calls/call-{call}/export-128.png', None)
SUPERSEDED = [
    ('snow-giant OLD v1 (rejected by gate: base_drift -8.16)', H(1, 'snow-giant')),
    ('snow-giant-boulder-thrower OLD v1 (rejected by gate: base_drift -9.04)', H(1, 'snow-giant-boulder-thrower')),
    ('minotaur OLD v1 (superseded: near twin of minotaur-maze at 48px)', ('file', ROOT / 'art/monster-batch-p/masters/minotaur-v1.png', None)),
    ('minotaur OLD v2 (rejected: axe crosses the disc rim, intrusion +38.5)', H(6, 'minotaur')),
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
    """48px composite of every batch-P asset on each real floor tile, the tile
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
    with tempfile.TemporaryDirectory(prefix='batch-p-review-') as scratch:
        for group, rows in GROUPS.items():
            sheet(group, rows, scratch)
        floor_sheet(scratch)
        luminance(scratch)
