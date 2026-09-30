"""Monster batch Z review sheets: family comparisons at 48/64/96px (colour and
grayscale) including the already shipped related ant, horror, orc, thief, skeleton,
elf, yaech, crystal, temporal and ghost tokens, and real-floor 48px composites on the refined
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
    'snakes-thieves-spider-elf': [
        ('shipped brown-snake', R('brown-snake')), ('shipped king-cobra', R('king-cobra')), ('shipped rattlesnake', R('rattlesnake')), ('shipped white-snake', R('white-snake')),
        ('Z black-mamba (steel-blue, raised S neck)', X('black-mamba')),
        ('shipped bandit', R('bandit')), ('shipped thief', R('thief')), ('shipped rogue', R('rogue')), ('shipped assassin', R('assassin')), ('shipped cutpurse', R('cutpurse')),
        ('Z bandit-lord (bearded, crossed arms, crimson)', X('bandit-lord')), ('Z rogue-sapper (khaki goggles, trap bandolier)', X('rogue-sapper')),
        ('shipped weaver-young', R('weaver-young')), ('shipped weaver-queen', R('weaver-queen')), ('shipped weaver-patriarch', R('weaver-patriarch')), ('shipped giant-spider', R('giant-spider')),
        ('Z orb-weaver (frost-blue, ringed abdomen)', X('orb-weaver')),
        ('shipped elven-warrior', R('elven-warrior')), ('shipped elven-guard', R('elven-guard')),
        ('Z elven-elite-warrior (heavy bronze plate, tower shield)', X('elven-elite-warrior')),
    ],
    'giants-dragon-temporal': [
        ('shipped bone-giant', R('bone-giant')), ('shipped heavy-bone-giant', R('heavy-bone-giant')), ('shipped eternal-bone-giant', R('eternal-bone-giant')),
        ('Z runed-bone-giant (crimson runes, floating glyphs)', X('runed-bone-giant')),
        ('shipped fire-drake', R('fire-drake')), ('shipped cold-drake', R('cold-drake')), ('shipped venom-drake', R('venom-drake')),
        ('Z fire-wyrm (scarlet coiled serpent, horn crown)', X('fire-wyrm')),
        ('shipped telugoroth', R('telugoroth')), ('shipped greater-telugoroth', R('greater-telugoroth')), ('shipped teluvorta', R('teluvorta')),
        ('Z ultimate-telugoroth (starburst time storm)', X('ultimate-telugoroth')), ('Z greater-teluvorta (horned violet cloud, dust wake)', X('greater-teluvorta')),
    ],
    'voids-aquatic': [
        ('shipped dredgling', R('dredgling')), ('shipped dredge', R('dredge')), ('shipped temporal-stalker', R('temporal-stalker')), ('shipped dread', R('dread')),
        ('shipped ink-squid', R('ink-squid')), ('shipped giant-eel', R('giant-eel')),
        ('Z void-horror (lens-shaped spacetime tear)', X('void-horror')), ('Z swarming-horror (school of eight)', X('swarming-horror')), ('Z ravenous-horror (spined acid-drooling predator)', X('ravenous-horror')),
    ],
}

RF = ROOT / 'data/gfx/refined/'
FLOOR_TILES = {
    'cave rock (unremarkable-cave, thieves-tunnels)': RF / 'cave/floor-rock-1-0.png',
    'bog (unhallowed-morass)': RF / 'bog0-0-0.png',
    'grass (lake-nur, maze)': RF / 'grass0.png',
    'caldera (noxious-caldera)': RF / 'caldera/floor0.png',
    'burnt ground (charred-scar, demon-plane)': RF / 'burnt/floor0.png',
    'gothic stone (crypt-kryl-feijan)': RF / 'gothic/floor-a0.png',
    'void floor (temporal-rift)': RF / 'void/floor0.png',
    'underwater floor (lake-nur)': RF / 'underwater/floor0.png',
    'korpul stone A (bandit-fortress-like)': RF / 'korpul/floor-a-0-0.png',
    'rak-shor floor (rak-shor-pride)': RF / 'rakshor/floor0.png',
}
IDS = ['black-mamba', 'bandit-lord', 'orb-weaver', 'elven-elite-warrior', 'ultimate-telugoroth', 'greater-teluvorta',
       'runed-bone-giant', 'void-horror', 'swarming-horror', 'ravenous-horror', 'rogue-sapper', 'fire-wyrm']
ZONE_FLOORS = {
    'black-mamba': ['caldera', 'cave', 'grass'], 'bandit-lord': ['cave', 'grass', 'korpul'], 'rogue-sapper': ['cave', 'grass', 'korpul'],
    'orb-weaver': ['bog'], 'elven-elite-warrior': ['gothic'], 'ultimate-telugoroth': ['void'], 'greater-teluvorta': ['void'],
    'runed-bone-giant': ['rak-shor'], 'void-horror': ['void'], 'swarming-horror': ['underwater'], 'ravenous-horror': ['underwater'],
    'fire-wyrm': ['burnt'],
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
    """48px composite of every batch-Z asset on each real floor tile, the tile
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
    with tempfile.TemporaryDirectory(prefix='batch-z-review-') as scratch:
        for group, rows in GROUPS.items():
            sheet(group, rows, scratch)
        floor_sheet(scratch)
        luminance(scratch)
