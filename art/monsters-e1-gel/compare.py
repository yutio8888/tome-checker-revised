"""Build the E1-gel review contact sheets: same-family groups plus jelly-vs-ooze
same-colour pairs, in colour and in grayscale, at 48/64/96px.

Read-only: it reads this batch's own C exports under `exports/` and writes only
review sheets, also under `exports/`. Review sheets are never runtime assets.
"""
import json
from pathlib import Path

from PIL import Image

ART = Path(__file__).resolve().parent
ROOT = ART.parents[1]

# (group, [(label, id, source)]) - all assets in this batch are 'new'.
GROUPS = [
    ('jellies', [('green jelly', 'green-jelly', 'new'),
                 ('black jelly', 'black-jelly', 'new'),
                 ('white jelly', 'white-jelly', 'new'),
                 ('yellow jelly', 'yellow-jelly', 'new')]),
    ('oozes', [('black ooze', 'black-ooze', 'new'),
               ('yellow ooze', 'yellow-ooze', 'new'),
               ('red ooze', 'red-ooze', 'new'),
               ('blue ooze', 'blue-ooze', 'new')]),
    ('black-pair-dark-subject', [('black jelly', 'black-jelly', 'new'),
                                 ('black ooze', 'black-ooze', 'new')]),
    ('yellow-pair', [('yellow jelly', 'yellow-jelly', 'new'),
                     ('yellow ooze', 'yellow-ooze', 'new')]),
]
SIZES = (48, 64, 96)
BG = (44, 44, 50, 255)


def load(asset_id, source, size):
    return Image.open(ART / 'exports' / str(size) / (asset_id + '.png')).convert('RGBA')


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
