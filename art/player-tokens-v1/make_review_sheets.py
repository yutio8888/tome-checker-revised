"""Build player-token review sheets (color + grayscale + pair comparisons).
Reads the accepted 128px runtime exports and downsizes for the grid; writes
into art/player-tokens-v1/exports/. Not part of the production pipeline --
a one-off review aid, kept in art/ per instructions, not tools/.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path('/workspace/t-engine4/game/addons/tome-checker-revised')
TOKENS = ROOT / 'data/gfx/tokens'
OUT = ROOT / 'art/player-tokens-v1/exports'
OUT.mkdir(parents=True, exist_ok=True)

FAMILIES = [
    'human_male', 'human_female', 'elf_male', 'elf_female',
    'dwarf_male', 'dwarf_female', 'halfling_male',
    'ogre_male', 'ogre_female', 'yeek', 'ghoul', 'skeleton', 'runic_golem',
]

SIZES = [48, 64, 96]
PAD = 10
LABEL_H = 16
ROW_LABEL_W = 40

try:
    FONT = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 11)
except Exception:
    FONT = ImageFont.load_default()


def load(family):
    return Image.open(TOKENS / f'player-{family}.png').convert('RGBA')


def checker_bg(w, h, cell=8):
    bg = Image.new('RGBA', (w, h), (255, 255, 255, 255))
    d = ImageDraw.Draw(bg)
    for y in range(0, h, cell):
        for x in range(0, w, cell):
            if (x // cell + y // cell) % 2 == 0:
                d.rectangle([x, y, x + cell - 1, y + cell - 1], fill=(214, 214, 214, 255))
    return bg


def grid_sheet(families, path, gray=False):
    col_w = max(SIZES) + PAD
    row_h = max(SIZES) + PAD
    width = ROW_LABEL_W + col_w * len(families)
    height = LABEL_H + row_h * len(SIZES)
    canvas = checker_bg(width, height)
    d = ImageDraw.Draw(canvas)
    for c, family in enumerate(families):
        x = ROW_LABEL_W + c * col_w
        d.text((x + 4, 2), family, fill=(20, 20, 20, 255), font=FONT)
    for r, size in enumerate(SIZES):
        y = LABEL_H + r * row_h
        d.text((4, y + row_h // 2 - 6), f'{size}px', fill=(20, 20, 20, 255), font=FONT)
        for c, family in enumerate(families):
            img = load(family).resize((size, size), Image.LANCZOS)
            if gray:
                alpha = img.getchannel('A')
                img = Image.merge('RGBA', (*Image.merge('RGB', [img.convert('L')] * 3).split(), alpha))
            x = ROW_LABEL_W + c * col_w + (col_w - size) // 2
            yy = y + (row_h - size) // 2
            canvas.alpha_composite(img, (x, yy))
    canvas.convert('RGB').save(path)
    print('wrote', path, canvas.size)


def pair_sheet(pairs, path, title_pairs):
    """pairs: list of (label, family_or_None) rows; title_pairs: list of (left_label, right_label) headers per group."""
    size_list = [64, 96]
    col_w = max(size_list) + PAD
    n_cols = 2
    row_h = max(size_list) + PAD + LABEL_H
    width = n_cols * col_w + PAD
    height = len(pairs) * row_h + LABEL_H
    canvas = checker_bg(width, height)
    d = ImageDraw.Draw(canvas)
    y = LABEL_H
    for left, right in pairs:
        for col, family in enumerate((left, right)):
            x0 = PAD // 2 + col * col_w
            if family is None:
                d.text((x0 + 4, y + 4), '(missing)', fill=(180, 30, 30, 255), font=FONT)
                continue
            d.text((x0 + 4, y + 2), family, fill=(20, 20, 20, 255), font=FONT)
            for i, size in enumerate(size_list):
                img = load(family).resize((size, size), Image.LANCZOS)
                x = x0 + i * (max(size_list) - size)
                yy = y + LABEL_H + (max(size_list) - size)
                canvas.alpha_composite(img, (x, yy))
        y += row_h
    canvas.convert('RGB').save(path)
    print('wrote', path, canvas.size)


grid_sheet(FAMILIES, OUT / 'compare-color.png', gray=False)
grid_sheet(FAMILIES, OUT / 'compare-gray.png', gray=True)

pair_sheet([('human_male', 'elf_male'), ('human_female', 'elf_female')],
           OUT / 'pair-human-vs-elf.png', None)
pair_sheet([('dwarf_male', 'halfling_male'), ('dwarf_female', None)],
           OUT / 'pair-dwarf-vs-halfling.png', None)
pair_sheet([('human_male', 'human_female'), ('elf_male', 'elf_female'),
            ('dwarf_male', 'dwarf_female'), ('ogre_male', 'ogre_female')],
           OUT / 'pair-male-vs-female.png', None)

print('done')
