"""Monster batch U review sheets: family comparisons at 48/64/96px (colour and
grayscale) including the already shipped related ritch, naga, mummy, orc, imp and
spider tokens, and real-floor 48px composites on the refined floors of the
creatures' own zones (sand, underwater, cave rock, void, Kor'Pul, rak-shor,
burnt ground), plus masked-body luminance. Read-only
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
    'ritches': [
        ('shipped ritch-hive-mother (orange radial crab)', R('ritch-hive-mother')),
        ('shipped chitinous-spider (cream radial spider)', R('chitinous-spider')),
        ('U ritch-flamespitter (scarlet, reared, fire ball)', X('ritch-flamespitter')),
        ('U ritch-impaler (copper, low, bone lance)', X('ritch-impaler')),
        ('U chitinous-ritch (golden dome, folded legs)', X('chitinous-ritch')),
    ],
    'nagas-mummies': [
        ('shipped naga-myrmidon', R('naga-myrmidon')), ('shipped naga-tidewarden', R('naga-tidewarden')), ('shipped naga-nereid', R('naga-nereid')),
        ('shipped lady-zoisla', R('lady-zoisla')), ('shipped lady-nashva', R('lady-nashva')), ('shipped naga-tidecaller', R('naga-tidecaller')),
        ('shipped slasul', R('slasul')),
        ('U naga-tide-huntress (white-silver tail, bow)', X('naga-tide-huntress')),
        ('U naga-psyren (violet tail, orb)', X('naga-psyren')),
        ('shipped greater-mummy-lord', R('greater-mummy-lord')),
        ('U ancient-elven-mummy (slender, pointed ears, arms forward)', X('ancient-elven-mummy')),
    ],
    'orcs-imps': [
        ('shipped orc-assassin (hooded, blue-grey)', R('orc-assassin')), ('shipped orc-necromancer', R('orc-necromancer')),
        ('shipped orc-warrior', R('orc-warrior')), ('shipped orc-soldier', R('orc-soldier')),
        ('U orc-master-assassin (topknot-less, crossed daggers)', X('orc-master-assassin')),
        ('U orc-grand-master-assassin (ivory mask, arms wide)', X('orc-grand-master-assassin')),
        ('shipped quasit', R('quasit')), ('shipped water-imp', R('water-imp')), ('shipped wretchling', R('wretchling')), ('shipped draebor', R('draebor')),
        ('U fire-imp (vermilion, winged, fire ball overhead)', X('fire-imp')),
    ],
    'spiders': [
        ('shipped giant-spider', R('giant-spider')), ('shipped spitting-spider', R('spitting-spider')), ('shipped chitinous-spider', R('chitinous-spider')),
        ('shipped fate-spinner', R('fate-spinner')), ('shipped weaver-young', R('weaver-young')), ('shipped nimisil', R('nimisil')),
        ('U gaeramarth (ash/bone, banded legs, skull, rearing)', X('gaeramarth')),
        ('U ninurlhing (bloated lime abdomen, acid drips)', X('ninurlhing')),
        ('U fate-weaver (fluffy lavender, gold clock, thread)', X('fate-weaver')),
    ],
}

RF = ROOT / 'data/gfx/refined/'
FLOOR_TILES = {
    'sand (ritch-tunnels)': RF / 'sand/floor0.png',
    'underwater floor (temple-of-creation)': RF / 'underwater/floor0.png',
    'cave rock (ancient-elven-ruins, ardhungol, valley-moon)': RF / 'cave/floor-rock-1-0.png',
    'cave mushroom (ardhungol)': RF / 'cave/floor-mushroom-1-0.png',
    'void floor (unhallowed-morass)': RF / 'void/floor0.png',
    'korpul stone A (reknor, vor-armoury)': RF / 'korpul/floor-a-0-0.png',
    'rak-shor floor (rak-shor-pride)': RF / 'rakshor/floor0.png',
    'burnt ground (demon-plane)': RF / 'burnt/floor0.png',
}
IDS = ['ritch-flamespitter', 'ritch-impaler', 'chitinous-ritch', 'naga-tide-huntress', 'naga-psyren', 'ancient-elven-mummy',
       'orc-master-assassin', 'orc-grand-master-assassin', 'fire-imp', 'gaeramarth', 'ninurlhing', 'fate-weaver']
ZONE_FLOORS = {
    'ritch-flamespitter': ['sand'], 'ritch-impaler': ['sand'], 'chitinous-ritch': ['sand'],
    'naga-tide-huntress': ['underwater'], 'naga-psyren': ['underwater'], 'ancient-elven-mummy': ['cave rock'],
    'orc-master-assassin': ['korpul', 'rak-shor'], 'orc-grand-master-assassin': ['korpul', 'rak-shor'],
    'fire-imp': ['cave rock', 'burnt'], 'gaeramarth': ['cave'], 'ninurlhing': ['cave'], 'fate-weaver': ['void'],
}
FLOOR_ASSETS = [(i, X(i)) for i in IDS]
H = lambda pack, asset, call=1: ('file', ROOT / f'art/production/handoffs/monster-batch-u-{pack}/{asset}/imagegen-calls/call-{call}/export-128.png', None)
SUPERSEDED = [
    ('naga-psyren OLD v1 (rejected by gate: base_drift -9.08, disc darkened, hair to the rim)', H(2, 'naga-psyren')),
    ('orc-master-assassin OLD v1 (rejected by review: topknot and daggers over the rim, export shrunk)', H(3, 'orc-master-assassin')),
    ('fire-imp OLD v1 (passed gate; replaced: masked body lum 62.11, dark red at 48px)', H(3, 'fire-imp')),
    ('gaeramarth OLD v1 (passed gate; replaced: cream radial spider like chitinous-spider at 48px)', H(4, 'gaeramarth')),
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
    """48px composite of every batch-U asset on each real floor tile, the tile
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
    with tempfile.TemporaryDirectory(prefix='batch-u-review-') as scratch:
        for group, rows in GROUPS.items():
            sheet(group, rows, scratch)
        floor_sheet(scratch)
        luminance(scratch)
