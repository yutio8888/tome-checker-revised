"""Build the V9-refine review contact sheets at 48/64/96px, colour and grayscale.

Read-only: it reads existing C exports (this batch's `exports/`, the superseded
C0b export of the same identity, and the runtime `data/gfx/tokens` copies of the
already mapped anchors) and writes only review sheets under `exports/`. Review
sheets are never runtime assets, and nothing in art/monsters-v8-c0b is modified.
"""
import json
from pathlib import Path

from PIL import Image

ART = Path(__file__).resolve().parent
ROOT = ART.parents[1]
RUNTIME = ROOT / 'data/gfx/tokens'
C0B = ROOT / 'art/monsters-v8-c0b/exports'

# (group, [(label, id, source)]) where source is 'new' (this batch), 'c0b' (the
# superseded C0b export kept for the before/after pair) or 'mapped' (runtime).
GROUPS = [
    ('brown-mouse-refine', [('giant brown rat (mapped)', 'brown-rat', 'mapped'),
                            ('giant brown mouse v1 (C0b, superseded)', 'giant-brown-mouse', 'c0b'),
                            ('giant brown mouse v9 (new)', 'giant-brown-mouse', 'new'),
                            ('giant white mouse (mapped)', 'giant-white-mouse', 'mapped'),
                            ('giant grey mouse (mapped)', 'giant-grey-mouse', 'mapped')]),
    ('skeleton-warrior', [('degenerated skeleton warrior (mapped)', 'degenerated-skeleton-warrior', 'mapped'),
                          ('skeleton warrior (new)', 'skeleton-warrior', 'new'),
                          ('skeleton mage (mapped)', 'skeleton-mage', 'mapped')]),
]
SIZES = (48, 64, 96)
BG = (44, 44, 50, 255)


def load(asset_id, source, size):
    if source == 'new':
        return Image.open(ART / 'exports' / str(size) / (asset_id + '.png')).convert('RGBA')
    if source == 'c0b':
        return Image.open(C0B / str(size) / (asset_id + '.png')).convert('RGBA')
    # Mapped anchors only exist at 128px in the runtime directory; downscale for
    # review only. This is a review sheet, never a runtime asset.
    image = Image.open(RUNTIME / (asset_id + '.png')).convert('RGBA')
    return image if image.width == size else image.resize((size, size), Image.LANCZOS)


def sheet(entries, size, gray):
    pad, cell = 8, size
    width = pad + len(entries) * (cell + pad)
    image = Image.new('RGBA', (width, cell + pad * 2), BG)
    for i, (_, asset_id, source) in enumerate(entries):
        token = load(asset_id, source, size)
        if gray:
            grey = token.convert('LA').convert('RGBA')
            grey.putalpha(token.getchannel('A'))
            token = grey
        image.alpha_composite(token, (pad + i * (cell + pad), pad))
    return image


def main():
    index = {}
    for group, entries in GROUPS:
        for gray in (False, True):
            rows = [sheet(entries, size, gray) for size in SIZES]
            width = max(r.width for r in rows)
            out = Image.new('RGBA', (width, sum(r.height for r in rows)), BG)
            y = 0
            for r in rows:
                out.alpha_composite(r, (0, y))
                y += r.height
            name = f"compare-{group}-{'grayscale' if gray else 'colour'}.png"
            (ART / 'exports').mkdir(exist_ok=True)
            out.convert('RGB').save(ART / 'exports' / name)
            index[name] = dict(group=group, grayscale=gray, sizes=list(SIZES),
                               order=[e[0] for e in entries])
    (ART / 'exports' / 'compare-index.json').write_text(json.dumps(index, ensure_ascii=False, indent=2) + '\n')
    print('PASS:', len(index), 'review sheets; rows are 48/64/96px, review only, not runtime assets')


if __name__ == '__main__':
    main()
