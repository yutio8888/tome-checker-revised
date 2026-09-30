"""Monster batch AB review sheets: family comparisons at 48/64/96px (colour and
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
    'aquatic-horrors': [
        ('shipped ravenous-horror', R('ravenous-horror')), ('shipped swarming-horror', R('swarming-horror')), ('shipped bloated-horror', R('bloated-horror')), ('shipped necrotic-mass', R('necrotic-mass')),
        ('AB entrenched-horror (limestone pillar, teal tentacle wreath)', X('entrenched-horror')),
        ('AB boiling-horror (aquamarine froth sphere, orange core)', X('boiling-horror')),
        ('AB swarm-hive (pearl flesh mound spawning silver fish)', X('swarm-hive')),
    ],
    'orcs-mummies-thieves': [
        ('shipped orc-fighter', R('orc-fighter')), ('shipped orc-berserker', R('orc-berserker')),
        ('AB orc-elite-fighter (crested bulwark, blue tower shield)', X('orc-elite-fighter')),
        ('AB orc-elite-berserker (vermilion charge, ram horns, fur)', X('orc-elite-berserker')),
        ('shipped orc-corruptor', R('orc-corruptor')), ('shipped orc-necromancer', R('orc-necromancer')), ('shipped orc-pyromancer', R('orc-pyromancer')),
        ('AB orc-summoner (antlered beast-shaman, spirit wisps)', X('orc-summoner')),
        ('shipped rotting-mummy', R('rotting-mummy')), ('shipped greater-mummy-lord', R('greater-mummy-lord')),
        ('AB greater-mummy (ivory linen, nemes, greatsword)', X('greater-mummy')),
        ('shipped assassin', R('assassin')), ('shipped rogue', R('rogue')), ('shipped rogue-sapper', R('rogue-sapper')),
        ('AB shadowblade (twin scimitars, periwinkle scarf)', X('shadowblade')),
    ],
    'wyrm-golem-ice-troll': [
        ('shipped venom-drake', R('venom-drake')), ('shipped fire-wyrm', R('fire-wyrm')),
        ('AB venom-wyrm (reared S-neck, acid drip)', X('venom-wyrm')),
        ('shipped golem', R('golem')), ('shipped broken-golem', R('broken-golem')),
        ('AB alchemist-golem (tan sandstone, gold runes, cyan orb)', X('alchemist-golem')),
        ('shipped shivgoroth', R('shivgoroth')), ('shipped greater-shivgoroth', R('greater-shivgoroth')),
        ('AB ultimate-shivgoroth (sapphire colossus, shard ring)', X('ultimate-shivgoroth')),
        ('shipped forest-troll', R('forest-troll')), ('shipped cave-troll', R('cave-troll')),
        ('AB forest-troll-hedge-wizard (plum tabard, flames)', X('forest-troll-hedge-wizard')),
    ],
}

RF = ROOT / 'data/gfx/refined/'
FLOOR_TILES = {
    'cave rock (unremarkable-cave, thieves-tunnels)': RF / 'cave/floor-rock-1-0.png',
    'underwater floor (lake-nur)': RF / 'underwater/floor0.png',
    'grass (maze)': RF / 'grass0.png',
    'caldera (noxious-caldera)': RF / 'caldera/floor0.png',
    'gothic stone (ancient-elven-ruins, golem-graveyard)': RF / 'gothic/floor-a0.png',
    'snow ground (norgos-lair)': RF / 'snow/snow-ground0.png',
    'korpul stone A (vor-armoury, reknor)': RF / 'korpul/floor-a-0-0.png',
    'rak-shor floor (rak-shor-pride)': RF / 'rakshor/floor0.png',
    'burnt ground': RF / 'burnt/floor0.png',
    'void floor': RF / 'void/floor0.png',
}
IDS = ['entrenched-horror', 'orc-summoner', 'greater-mummy', 'shadowblade', 'orc-elite-fighter', 'orc-elite-berserker', 'boiling-horror',
       'venom-wyrm', 'alchemist-golem', 'swarm-hive', 'forest-troll-hedge-wizard', 'ultimate-shivgoroth']
# Approximate: the zone floors listed are the refined families that dress each creature's own zones (golem-graveyard and reknor use the nearest available family).
ZONE_FLOORS = {
    'entrenched-horror': ['underwater'], 'boiling-horror': ['underwater'], 'swarm-hive': ['underwater'],
    'orc-summoner': ['cave', 'rak-shor'], 'greater-mummy': ['gothic'], 'shadowblade': ['cave', 'grass'],
    'orc-elite-fighter': ['korpul'], 'orc-elite-berserker': ['korpul'], 'venom-wyrm': ['caldera'], 'alchemist-golem': ['gothic'],
    'forest-troll-hedge-wizard': ['korpul'], 'ultimate-shivgoroth': ['snow'],
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
    """48px composite of every batch-AB asset on each real floor tile, the tile
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
    with tempfile.TemporaryDirectory(prefix='batch-ab-review-') as scratch:
        for group, rows in GROUPS.items():
            sheet(group, rows, scratch)
        floor_sheet(scratch)
        luminance(scratch)
