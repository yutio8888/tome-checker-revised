"""Batch E review sheets: each of the 12 recommended zone-finale bosses beside its
confusable same-type/subtype siblings at 48/64/96px, color and grayscale.

Read-only composition of existing exports/masters; no creature pixels are painted.
Shipped batch-E assets (lady-zoisla, brotoq, the-mouth, the-abomination, celia) are
read from their stored art/monster-batch-e/sprites/<size>/ exports. The 7 base_drift
-only pending-waiver candidates (urkis, golbug, ungole, half-finished-bone-giant,
kryl-feijan, atamathon, ritch-hive-mother) have no stored sprite export -- they are
not in the catalog -- so tools/bin/export_token is run on their attempt-1 masters
into a temporary directory purely for this review; that does not admit them to the
catalog. horned-horror is read from the shipped runtime token (data/gfx/tokens) as
family context for the-mouth/the-abomination.
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
    'orcs': [
        ('E golbug (PENDING base_drift waiver -15.18)', ('master', HERE / 'masters/golbug-v1.png', None)),
        ('E brotoq (SHIPPED, gate pass)', ('export', HERE, 'brotoq')),
    ],
    'humans': [
        ('E urkis (PENDING base_drift waiver -12.21)', ('master', HERE / 'masters/urkis-v1.png', None)),
        ('E celia (SHIPPED, gate pass)', ('export', HERE, 'celia')),
    ],
    'horror-corrupted': [
        ('B horned-horror (shipped, existing catalog, context only)', ('runtime', 'horned-horror', None)),
        ('E the-mouth (SHIPPED, gate pass)', ('export', HERE, 'the-mouth')),
        ('E the-abomination (SHIPPED, gate pass)', ('export', HERE, 'the-abomination')),
    ],
    'naga': [
        ('E lady-zoisla (SHIPPED, gate pass, v2 after design-fix 3rd attempt)', ('export', HERE, 'lady-zoisla')),
    ],
    'spiderkin': [
        ('E ungole (PENDING base_drift waiver -9.47)', ('master', HERE / 'masters/ungole-v1.png', None)),
    ],
    'undead-giant': [
        ('E half-finished-bone-giant (PENDING base_drift waiver -12.83)', ('master', HERE / 'masters/half-finished-bone-giant-v1.png', None)),
    ],
    'demon-major': [
        ('E kryl-feijan (PENDING base_drift waiver -10.97)', ('master', HERE / 'masters/kryl-feijan-v1.png', None)),
    ],
    'construct-golem': [
        ('E atamathon (PENDING base_drift waiver -10.60)', ('master', HERE / 'masters/atamathon-v1.png', None)),
    ],
    'insect-ritch': [
        ('E ritch-hive-mother (PENDING base_drift waiver -10.34)', ('master', HERE / 'masters/ritch-hive-mother-v1.png', None)),
    ],
}


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
    width = 520 + cell
    height = PAD + len(rows) * (max(SIZES) + PAD)
    for mode in ('color', 'grayscale'):
        canvas = Image.new('RGBA', (width, height), BG)
        draw = ImageDraw.Draw(canvas)
        y = PAD
        for label, spec in rows:
            draw.text((PAD, y + max(SIZES) // 2 - 6), label, fill=(232, 232, 226, 255))
            x = 520
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


if __name__ == '__main__':
    with tempfile.TemporaryDirectory(prefix='batch-e-review-') as scratch:
        for group, rows in GROUPS.items():
            sheet(group, rows, scratch)
