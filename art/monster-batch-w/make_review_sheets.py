"""Monster batch W review sheets: family comparisons at 48/64/96px (colour and
grayscale) including the already shipped related orc, yaech, giant, bear, slug,
mummy, ghost and ant tokens, and real-floor 48px composites on the refined
floors of the creatures' own zones (cave, crystal, grass, gloom, underwater,
burnt ground, Kor'Pul, rak-shor), plus masked-body luminance. Read-only
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
    'orcs-yaech': [
        ('shipped orc-warrior', R('orc-warrior')), ('shipped orc-soldier', R('orc-soldier')), ('shipped orc-archer', R('orc-archer')),
        ('shipped orc-master-assassin', R('orc-master-assassin')), ('shipped orc-pyromancer', R('orc-pyromancer')),
        ('W fiery-orc-wyrmic (crimson scales, raised axe)', X('fiery-orc-wyrmic')),
        ('W icy-orc-wyrmic (pale ice scales, ice pauldrons)', X('icy-orc-wyrmic')),
        ('shipped yaech-diver', R('yaech-diver')), ('shipped yeek-wayist', R('yeek-wayist')), ('shipped yaech-hunter', R('yaech-hunter')),
        ('W yaech-mindslayer (seafoam teal, lightning ball)', X('yaech-mindslayer')),
    ],
    'giants-bears-slugs': [
        ('shipped bone-giant', R('bone-giant')), ('shipped half-finished-bone-giant', R('half-finished-bone-giant')),
        ('shipped eternal-bone-giant', R('eternal-bone-giant')),
        ('W heavy-bone-giant (honey amber, hugging bone bundle)', X('heavy-bone-giant')),
        ('shipped brown-bear', R('brown-bear')), ('shipped black-bear', R('black-bear')),
        ('W cave-bear (stone grey, profile)', X('cave-bear')), ('W war-bear (russet, reared, tusks)', X('war-bear')),
        ('shipped grannor-vor', R('grannor-vor')), ('shipped slimy-crawler', R('slimy-crawler')),
        ('W grannor-vin (lavender slug, human face)', X('grannor-vin')),
    ],
    'undead': [
        ('shipped ancient-elven-mummy', R('ancient-elven-mummy')), ('shipped ghoul', R('ghoul')), ('shipped ghast', R('ghast')),
        ('shipped shade-of-telos', R('shade-of-telos')), ('shipped forest-wight', R('forest-wight')), ('shipped grave-wight', R('grave-wight')),
        ('W rotting-mummy (hunched, green-grey rot)', X('rotting-mummy')),
        ('W banshee (pale cyan wailing woman)', X('banshee')),
    ],
    'ants': [
        ('shipped giant-white-ant', R('giant-white-ant')), ('shipped giant-yellow-ant', R('giant-yellow-ant')), ('shipped giant-brown-ant', R('giant-brown-ant')),
        ('shipped giant-blue-ant', R('giant-blue-ant')), ('shipped giant-carpenter-ant', R('giant-carpenter-ant')), ('shipped giant-black-ant', R('giant-black-ant')),
        ('shipped giant-green-ant', R('giant-green-ant')), ('shipped giant-red-ant', R('giant-red-ant')),
        ('W giant-fire-ant (burnt orange, flame plume)', X('giant-fire-ant')),
        ('W giant-ice-ant (crystalline cyan, spike crest)', X('giant-ice-ant')),
        ('W giant-lightning-ant (lavender, arc halo)', X('giant-lightning-ant')),
    ],
}

RF = ROOT / 'data/gfx/refined/'
FLOOR_TILES = {
    'cave rock (ancient-elven-ruins, ardhungol, old-forest)': RF / 'cave/floor-rock-1-0.png',
    'cave mushroom (ardhungol)': RF / 'cave/floor-mushroom-1-0.png',
    'crystal (scintillating-caves)': RF / 'crystal/floor0.png',
    'grass (old-forest, lake-nur)': RF / 'grass0.png',
    'gloom plain (deep-bellow)': RF / 'gloom/plain/floor0.png',
    'void floor (temporal-rift)': RF / 'void/floor0.png',
    'underwater floor (murgol-lair, lake-nur)': RF / 'underwater/floor0.png',
    'burnt ground (demon-plane)': RF / 'burnt/floor0.png',
    'korpul stone A (vor-armoury, telmur)': RF / 'korpul/floor-a-0-0.png',
    'rak-shor floor (rak-shor-pride)': RF / 'rakshor/floor0.png',
}
IDS = ['fiery-orc-wyrmic', 'icy-orc-wyrmic', 'yaech-mindslayer', 'heavy-bone-giant', 'cave-bear', 'war-bear', 'grannor-vin',
       'rotting-mummy', 'banshee', 'giant-fire-ant', 'giant-ice-ant', 'giant-lightning-ant']
ZONE_FLOORS = {
    'fiery-orc-wyrmic': ['korpul', 'rak-shor'], 'icy-orc-wyrmic': ['korpul', 'rak-shor'], 'yaech-mindslayer': ['underwater'],
    'heavy-bone-giant': ['rak-shor', 'korpul'], 'cave-bear': ['cave', 'grass', 'crystal'], 'war-bear': ['cave', 'grass', 'crystal'],
    'grannor-vin': ['gloom'], 'rotting-mummy': ['cave rock'], 'banshee': ['rak-shor', 'korpul', 'burnt'],
    'giant-fire-ant': ['cave', 'grass', 'korpul'], 'giant-ice-ant': ['cave', 'grass', 'korpul'], 'giant-lightning-ant': ['cave', 'grass', 'korpul'],
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
    """48px composite of every batch-W asset on each real floor tile, the tile
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
    with tempfile.TemporaryDirectory(prefix='batch-w-review-') as scratch:
        for group, rows in GROUPS.items():
            sheet(group, rows, scratch)
        floor_sheet(scratch)
        luminance(scratch)
