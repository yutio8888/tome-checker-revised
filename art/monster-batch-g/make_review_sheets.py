"""Monster batch G review sheets: family comparisons at 48/64/96px (color and
grayscale), real dark-floor 48px composites for every batch-G asset (shipped,
pending and rejected), and masked-body luminance for dremling old-vs-new.
Read-only composition of existing exports/masters; no creature pixels painted.
The massok master (PENDING base_drift request, not in the catalog) and the old
rejected batch-F dremling are exported into a temporary directory for review only.
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
F = ART / 'monster-batch-f'
X = lambda i: ('export', HERE, i)
R = lambda i: ('runtime', i, None)
M = lambda p: ('master', HERE / p, None)

GROUPS = {
    'spiderkin': [
        ('E ungole (shipped, context; round black spider)', R('ungole')),
        ('G xhaiak-arachnomancer (v1, gate pass -6.07)', X('xhaiak-arachnomancer')),
        ('G shiaak-venomblade OLD v1 (superseded: near-black olive, lum 43)', M('masters/shiaak-venomblade-v1.png')),
        ('G shiaak-venomblade v2 (gate pass +0.01, lighter sage)', X('shiaak-venomblade')),
    ],
    'undead': [
        ('skeleton-mage (shipped, context)', R('skeleton-mage')),
        ('skeleton-master-archer (shipped, context)', R('skeleton-master-archer')),
        ('E half-finished-bone-giant (shipped, context)', R('half-finished-bone-giant')),
        ('G pale-drake (v1, gate pass -4.86)', X('pale-drake')),
        ('G the-master OLD v1 (superseded: near-black robe, lum 35)', M('masters/the-master-v1.png')),
        ('G the-master v2 (gate pass -2.58, crimson/ivory robe)', X('the-master')),
    ],
    'orc': [
        ('E golbug (shipped, context)', R('golbug')),
        ('E brotoq (shipped, context)', R('brotoq')),
        ('G krogar (v1 of retry pack 3c, gate pass -2.87)', X('krogar')),
        ('G massok (PENDING base_drift -10.32, not shipped)', M('masters/massok-v1.png')),
    ],
    'horror-corrupted': [
        ('B horned-horror (shipped, context)', R('horned-horror')),
        ('E the-mouth (shipped, context)', R('the-mouth')),
        ('E the-abomination (shipped, context)', R('the-abomination')),
        ('F dremling OLD obsidian (REJECTED dark-on-dark)', ('master', F / 'masters/dremling-v1.png', None)),
        ('G dremling NEW pale stone (v2, gate pass +3.37)', X('dremling')),
    ],
    'humanoid-elf-human': [
        ('E celia (shipped, context)', R('celia')),
        ('E urkis (shipped, context)', R('urkis')),
        ('G fillarel-aldaren (v1, gate pass -7.17)', X('fillarel-aldaren')),
        ('G rhaloren-inquisitor (v2, gate pass -6.01)', X('rhaloren-inquisitor')),
        ('G harno (v1, gate pass -7.63)', X('harno')),
    ],
    'demon-crystal-other': [
        ('E kryl-feijan (shipped, context)', R('kryl-feijan')),
        ('G lithfengel (v2, gate pass -5.28)', X('lithfengel')),
        ('G spellblaze-crystal (v2, gate pass +0.68)', X('spellblaze-crystal')),
    ],
}

FLOOR_TILES = {
    'gloom-floor': ROOT / 'data/gfx/refined/gloom/gloomy/floor0.png',
    'korpul-stone-floor': ROOT / 'data/gfx/refined/korpul/floor-a-0-0.png',
}
FLOOR_ASSETS = [
    ('xhaiak-arachnomancer', X('xhaiak-arachnomancer')),
    ('shiaak-venomblade v2', X('shiaak-venomblade')),
    ('shiaak-venomblade OLD v1 (superseded)', M('masters/shiaak-venomblade-v1.png')),
    ('dremling NEW (v2)', X('dremling')),
    ('dremling OLD (rejected)', ('master', F / 'masters/dremling-v1.png', None)),
    ('massok (PENDING)', M('masters/massok-v1.png')),
    ('pale-drake', X('pale-drake')),
    ('fillarel-aldaren', X('fillarel-aldaren')),
    ('krogar', X('krogar')),
    ('spellblaze-crystal', X('spellblaze-crystal')),
    ('the-master v2', X('the-master')),
    ('the-master OLD v1 (superseded)', M('masters/the-master-v1.png')),
    ('rhaloren-inquisitor', X('rhaloren-inquisitor')),
    ('harno', X('harno')),
    ('lithfengel', X('lithfengel')),
]


def load(spec, size, scratch):
    kind, base, asset = spec
    if kind == 'export':
        return Image.open(base / 'sprites' / str(size) / f'{asset}.png').convert('RGBA')
    if kind == 'runtime':
        # Already-shipped catalog token, stored only at 128px in data/gfx/tokens;
        # resample here purely for side-by-side review composition.
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
    """48px composite of every batch-F asset onto each real dark floor tile."""
    size = 48
    tiles = {name: Image.open(path).convert('RGBA') for name, path in FLOOR_TILES.items()}
    cell = size + PAD
    width = 380 + len(FLOOR_TILES) * cell + PAD
    height = PAD + len(FLOOR_ASSETS) * (size + PAD)
    canvas = Image.new('RGBA', (width, height), BG)
    draw = ImageDraw.Draw(canvas)
    # Header
    x = 380
    for name in FLOOR_TILES:
        draw.text((x, 2), name, fill=(232, 232, 226, 255))
        x += cell
    y = LABEL + PAD
    for label, spec in FLOOR_ASSETS:
        draw.text((PAD, y + size // 2 - 6), label, fill=(232, 232, 226, 255))
        token = load(spec, size, scratch)
        x = 380
        for name, tile in tiles.items():
            frame = tile.copy()
            frame.alpha_composite(token, (0, 0))
            canvas.alpha_composite(frame, (x, y))
            x += cell
        y += size + PAD
    out = HERE / 'review' / 'floor-readability-48.png'
    out.parent.mkdir(exist_ok=True)
    canvas.convert('RGB').save(out)
    print(out.relative_to(ROOT))
    big = canvas.convert('RGB').resize((canvas.width * 2, canvas.height * 2), Image.NEAREST)
    big.save(HERE / 'review' / 'floor-readability-48-x2.png')


def luminance(scratch):
    """Masked-body mean luminance (128px export, alpha>=180 within d<=0.55 of
    centre; same method as the Kryl-Feijan v1-vs-c comparison) next to the
    mean luminance of the two real floor tiles."""
    import json, math
    out = {'method': '128px export; alpha>=180 pixels with d<=0.55 of centre; L=0.299R+0.587G+0.114B', 'assets': {}, 'floors': {}}
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
    with tempfile.TemporaryDirectory(prefix='batch-g-review-') as scratch:
        for group, rows in GROUPS.items():
            sheet(group, rows, scratch)
        floor_sheet(scratch)
        luminance(scratch)
