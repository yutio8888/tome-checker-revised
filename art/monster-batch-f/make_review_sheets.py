"""Monster batch F review sheets: family comparisons at 48/64/96px, color and
grayscale, plus a real-dark-floor-tile composite at 48px for every asset in
this batch (shipped and PENDING-waiver alike), per this task's explicit
readability requirement.

Read-only composition of existing exports/masters; no creature pixels are
painted. Shipped batch-F assets (naga-tidewarden, naga-tidecaller, treant,
kryl-feijan) are read from their stored art/monster-batch-f/sprites/<size>/
exports. The 3 base_drift-only PENDING candidates (dremling, shivgoroth,
greater-shivgoroth) have no stored sprite export -- they are not in the
catalog -- so tools/bin/export_token is run on their attempt-1 masters into a
temporary directory purely for this review; that does not admit them to the
catalog. horned-horror/the-mouth/the-abomination, lady-zoisla and
venus-flytrap are read from the shipped runtime tokens (data/gfx/tokens) as
family context. The old (superseded) batch-E kryl-feijan-v1 master is
included for a direct before/after comparison of the redraw.
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

GROUPS = {
    'horror-corrupted': [
        ('B horned-horror (shipped, existing catalog, context only)', ('runtime', 'horned-horror', None)),
        ('E the-mouth (shipped, existing catalog, context only)', ('runtime', 'the-mouth', None)),
        ('E the-abomination (shipped, existing catalog, context only)', ('runtime', 'the-abomination', None)),
        ('F dremling (PENDING base_drift waiver -8.94)', ('master', HERE / 'masters/dremling-v1.png', None)),
    ],
    'elemental-ice': [
        ('F shivgoroth (PENDING base_drift waiver -11.23)', ('master', HERE / 'masters/shivgoroth-v1.png', None)),
        ('F greater-shivgoroth (PENDING base_drift waiver -9.40)', ('master', HERE / 'masters/greater-shivgoroth-v1.png', None)),
    ],
    'naga': [
        ('E lady-zoisla (shipped, existing catalog, context only)', ('runtime', 'lady-zoisla', None)),
        ('F naga-tidewarden (SHIPPED, gate pass, v2 after disc-overflow repair)', ('export', HERE, 'naga-tidewarden')),
        ('F naga-tidecaller (SHIPPED, gate pass, v2 after disc-overflow repair)', ('export', HERE, 'naga-tidecaller')),
    ],
    'immovable-plants': [
        ('venus-flytrap (shipped, existing catalog, context only)', ('runtime', 'venus-flytrap', None)),
        ('F treant (SHIPPED, gate pass, v2 after disc-overflow repair)', ('export', HERE, 'treant')),
    ],
    'demon-major-before-after': [
        ('E kryl-feijan-v1 (SUPERSEDED -- shipped under base_drift waiver, read as a near-black blob at 48px in-game; masked-body mean luminance 59.3)', ('master', HERE / 'masters/kryl-feijan-v1.png', None)),
        ('F kryl-feijan-b (rejected -- cleared the style gate but measured luminance 59.0, statistically unchanged from v1)', ('master', HERE / 'masters/kryl-feijan-b-v1.png', None)),
        ('F kryl-feijan-c (SHIPPED, gate pass, pale storm-grey redraw; masked-body mean luminance 85.4, +44% over v1)', ('export', HERE, 'kryl-feijan')),
    ],
}

# Floor-composite check: every batch-F asset (shipped or PENDING) composited
# at 48px onto two real dark floor tiles used by shipped dungeons.
FLOOR_TILES = {
    'gloom-floor': ROOT / 'data/gfx/refined/gloom/gloomy/floor0.png',
    'korpul-stone-floor': ROOT / 'data/gfx/refined/korpul/floor-a-0-0.png',
}
FLOOR_ASSETS = [
    ('naga-tidewarden', ('export', HERE, 'naga-tidewarden')),
    ('naga-tidecaller', ('export', HERE, 'naga-tidecaller')),
    ('treant', ('export', HERE, 'treant')),
    ('kryl-feijan-c (new, shipped)', ('export', HERE, 'kryl-feijan')),
    ('kryl-feijan-v1 (old, superseded)', ('master', HERE / 'masters/kryl-feijan-v1.png', None)),
    ('dremling (PENDING)', ('master', HERE / 'masters/dremling-v1.png', None)),
    ('shivgoroth (PENDING)', ('master', HERE / 'masters/shivgoroth-v1.png', None)),
    ('greater-shivgoroth (PENDING)', ('master', HERE / 'masters/greater-shivgoroth-v1.png', None)),
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


if __name__ == '__main__':
    with tempfile.TemporaryDirectory(prefix='batch-f-review-') as scratch:
        for group, rows in GROUPS.items():
            sheet(group, rows, scratch)
        floor_sheet(scratch)
