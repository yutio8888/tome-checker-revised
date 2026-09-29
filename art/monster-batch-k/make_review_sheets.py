"""Monster batch K review sheets: family comparisons at 48/64/96px (color and
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
    'aquatic': [
        ('shipped giant-eel (slate-blue S-curve)', R('giant-eel')),
        ('shipped electric-eel', R('electric-eel')),
        ('shipped dragon-turtle', R('dragon-turtle')),
        ('shipped ancient-dragon-turtle (tall)', R('ancient-dragon-turtle')),
        ('shipped murgol (finned yaech)', R('murgol')),
        ('shipped shivgoroth (ice elemental, tall)', R('shivgoroth')),
        ('K squid (fat rounded mantle, short curled arms)', X('squid')),
        ('K ink-squid (slim pointed mantle, fins, long tentacles)', X('ink-squid')),
        ('K water-imp (small teal horned imp, arms raised)', X('water-imp')),
        ('K walrog (horned water-lord, whirlpool tail, tall)', X('walrog')),
    ],
    'spiders': [
        ('shipped ungole (round black, red)', R('ungole')),
        ('shipped weaver-queen (furry frost-white)', R('weaver-queen')),
        ('shipped xhaiak-arachnomancer', R('xhaiak-arachnomancer')),
        ('shipped shiaak-venomblade', R('shiaak-venomblade')),
        ('K weaver-hatchling (small glassy, glowing orbs)', X('weaver-hatchling')),
        ('K orb-spinner (long ribbed abdomen)', X('orb-spinner')),
        ('K giant-spider (slate-grey, silver chevrons, long legs)', X('giant-spider')),
        ('K spitting-spider (brown hairy, green venom)', X('spitting-spider')),
        ('K chitinous-spider (ivory armoured plates)', X('chitinous-spider')),
    ],
    'undead-horror-worm': [
        ('shipped skeleton-warrior', R('skeleton-warrior')),
        ('shipped player-ghoul', R('player-ghoul')),
        ('K ghoul (hunched tan rotting brute, long claws)', X('ghoul')),
        ('shipped dremling (tall pale stone giant)', R('dremling')),
        ('K drem (small axe-and-shield dredge in rags)', X('drem')),
        ('shipped sandworm (slim orange S)', R('sandworm')),
        ('shipped sandworm-destroyer (ring, toothy mouth)', R('sandworm-destroyer')),
        ('shipped sandworm-burrower (green arches)', R('sandworm-burrower')),
        ('K gigantic-sandworm-tunneler (thick earth worm, petal maw)', X('gigantic-sandworm-tunneler')),
    ],
}

FLOOR_TILES = {
    'underwater (flooded/murgol/lake-nur/temple)': ROOT / 'data/gfx/refined/underwater/floor0.png',
    'void (unhallowed morass)': ROOT / 'data/gfx/refined/void/floor0.png',
    'cave rock (ardhungol)': ROOT / 'data/gfx/refined/cave/floor-rock-1-0.png',
    'cave mushroom (ardhungol)': ROOT / 'data/gfx/refined/cave/floor-mushroom-1-0.png',
    'daikara rock ground': ROOT / 'data/gfx/refined/daikara/rock-ground0.png',
    'sand (briagh/sandworm lair)': ROOT / 'data/gfx/refined/sand/floor0.png',
    'gloom plain creep (deep-bellow)': ROOT / 'data/gfx/refined/gloom/plain/creep-0-0.png',
    'korpul stone (halfling-ruins ghouls)': ROOT / 'data/gfx/refined/korpul/floor-a-0-0.png',
    'grass (last-hope graveyard)': ROOT / 'data/gfx/refined/grass0.png',
}
IDS = ['squid', 'ink-squid', 'water-imp', 'walrog', 'weaver-hatchling', 'orb-spinner', 'giant-spider', 'spitting-spider',
       'chitinous-spider', 'ghoul', 'drem', 'gigantic-sandworm-tunneler']
FLOOR_ASSETS = [(i, X(i)) for i in IDS]
# Superseded drafts (rejected before shipping) are appended here when a retry happens.
SUPERSEDED = [
    ('ink-squid OLD v1 (superseded: small and thin)', M('masters/ink-squid-v1.png')),
    ('walrog OLD v1 (superseded: filled the whole disc, intrusion 31)', M('masters/walrog-v1.png')),
    ('gigantic-sandworm-tunneler OLD v1 (rejected at gate: radius 0.899)', ('file', ROOT / 'art/production/handoffs/monster-batch-k-3/gigantic-sandworm-tunneler/imagegen-calls/call-1/export-128.png', None)),
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
    """48px composite of every batch-K asset on each real floor tile, the tile
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
    (HERE / 'review' / 'luminance.json').write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))


if __name__ == '__main__':
    with tempfile.TemporaryDirectory(prefix='batch-k-review-') as scratch:
        for group, rows in GROUPS.items():
            sheet(group, rows, scratch)
        floor_sheet(scratch)
        luminance(scratch)
