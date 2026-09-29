"""Batch C review sheets: each new token beside its confusable siblings at 48/64/96px.

Read-only composition of existing exports; no creature pixels are painted. Where a
sibling has no stored 48/64/96 export (Minotaur of the Labyrinth only kept 128px),
the same tools/bin/export_token mechanical exporter is run on its approved master
into a temporary directory.
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
    'archers': [
        ('C master archer (new)', ('sprites', ART / 'monster-batch-c', 'skeleton-master-archer')),
        ('C skeleton archer (new)', ('sprites', ART / 'monster-batch-c', 'skeleton-archer')),
        ('degenerated archer (kept)', ('sprites', ART / 'monsters-v5', 'degenerated-skeleton-archer')),
        ('B skeleton archer (replaced)', ('sprites', ART / 'monster-batch-b', 'skeleton-archer')),
        ('B master draft (rejected)', ('sprites', ART / 'monster-batch-b', 'skeleton-master-archer')),
    ],
    'horror': [
        ('C Horned Horror (new)', ('sprites', ART / 'monster-batch-c', 'horned-horror')),
        ('Minotaur of the Labyrinth', ('master', ART / 'monster-batch-a/masters/minotaur-maze-v1.png', None)),
        ('B Horned Horror (replaced)', ('sprites', ART / 'monster-batch-b', 'horned-horror')),
    ],
}


def load(spec, size, scratch):
    kind, base, asset = spec
    if kind == 'sprites':
        return Image.open(base / 'sprites' / str(size) / f'{asset}.png').convert('RGBA')
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
    width = 250 + cell
    height = PAD + len(rows) * (max(SIZES) + PAD)
    for mode in ('color', 'grayscale'):
        canvas = Image.new('RGBA', (width, height), BG)
        draw = ImageDraw.Draw(canvas)
        y = PAD
        for label, spec in rows:
            draw.text((PAD, y + max(SIZES) // 2 - 6), label, fill=(232, 232, 226, 255))
            x = 250
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
    with tempfile.TemporaryDirectory(prefix='batch-c-review-') as scratch:
        for group, rows in GROUPS.items():
            sheet(group, rows, scratch)
