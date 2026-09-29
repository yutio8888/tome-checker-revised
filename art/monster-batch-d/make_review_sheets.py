"""Batch D review sheets: each new token beside its confusable siblings at 48/64/96px.

Read-only composition of existing exports; no creature pixels are painted. New
batch-D assets have no stored sprite export yet, so tools/bin/export_token is run
on their approved (or pending-waiver) masters into a temporary directory. Already
shipped E1 jellies are read from their stored art/monsters-e1-gel/exports/<size>/
files.
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
    'jellies': [
        ('D red jelly (new)', ('master', HERE / 'masters/red-jelly-v1.png', None)),
        ('D blue jelly (new)', ('master', HERE / 'masters/blue-jelly-v1.png', None)),
        ('E1 green jelly (shipped)', ('export', ART / 'monsters-e1-gel', 'green-jelly')),
        ('E1 black jelly (shipped)', ('export', ART / 'monsters-e1-gel', 'black-jelly')),
        ('E1 white jelly (shipped)', ('export', ART / 'monsters-e1-gel', 'white-jelly')),
        ('E1 yellow jelly (shipped)', ('export', ART / 'monsters-e1-gel', 'yellow-jelly')),
    ],
    'ants': [
        ('D giant white ant (shipped, gate pass)', ('master', HERE / 'masters/giant-white-ant-v1.png', None)),
        ('D giant brown ant (shipped, base_drift waiver)', ('master', HERE / 'masters/giant-brown-ant-v1.png', None)),
        ('D giant carpenter ant (shipped, gate pass, redraw2)', ('master', HERE / 'masters/giant-carpenter-ant-redraw2-v1.png', None)),
        ('D giant blue ant (shipped, base_drift waiver)', ('master', HERE / 'masters/giant-blue-ant-v1.png', None)),
        ('D giant yellow ant (shipped, gate pass)', ('master', HERE / 'masters/giant-yellow-ant-v1.png', None)),
        ('D giant black ant (shipped, gate pass, redraw2)', ('master', HERE / 'masters/giant-black-ant-redraw2-v1.png', None)),
    ],
    'ants-carpenter-black-redraw': [
        ('D giant carpenter ant (REJECTED 2026-09-29 draft, batch-d-2)', ('master', HERE / 'masters/giant-carpenter-ant-v1.png', None)),
        ('D giant black ant (REJECTED 2026-09-29 draft, batch-d-2)', ('master', HERE / 'masters/giant-black-ant-v1.png', None)),
        ('D giant carpenter ant (batch-d-3 redraw attempt 1, base_drift +12.14, not saved to catalog)', ('master', HERE / 'masters/giant-carpenter-ant-redraw-v1.png', None)),
        ('D giant black ant (batch-d-3 redraw attempt 1, base_drift +12.27, not saved to catalog)', ('master', HERE / 'masters/giant-black-ant-redraw-v1.png', None)),
        ('D giant carpenter ant (SHIPPED, batch-d-4 calibrated redraw, base_drift -7.27)', ('master', HERE / 'masters/giant-carpenter-ant-redraw2-v1.png', None)),
        ('D giant black ant (SHIPPED, batch-d-4 calibrated redraw, base_drift -5.43)', ('master', HERE / 'masters/giant-black-ant-redraw2-v1.png', None)),
    ],
}


def load(spec, size, scratch):
    kind, base, asset = spec
    if kind == 'export':
        return Image.open(base / 'exports' / str(size) / f'{asset}.png').convert('RGBA')
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
    width = 440 + cell
    height = PAD + len(rows) * (max(SIZES) + PAD)
    for mode in ('color', 'grayscale'):
        canvas = Image.new('RGBA', (width, height), BG)
        draw = ImageDraw.Draw(canvas)
        y = PAD
        for label, spec in rows:
            draw.text((PAD, y + max(SIZES) // 2 - 6), label, fill=(232, 232, 226, 255))
            x = 440
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
    with tempfile.TemporaryDirectory(prefix='batch-d-review-') as scratch:
        for group, rows in GROUPS.items():
            sheet(group, rows, scratch)
