"""Batch TA-2 review sheets: TA-1/UB-2 geometry, 48/64/96 colour and grayscale
with shipped kin siblings, a 2x-nearest native column beside every TA-2 token,
the wiring-only elven-archer reuse sheet, ten real floors and the unchanged
central masked-body luminance measurement. No creature painting.
"""
from pathlib import Path
import subprocess
import tempfile

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BIN = ROOT / 'tools/bin/export_token'
SIZES = (48, 64, 96)
PAD, LABEL = 14, 18
BG = (46, 50, 46, 255)
X = lambda i: ('export', HERE, i)
R = lambda i: ('runtime', i, None)
WS = ROOT.parents[2]
NPC = WS / 'game/modules/tome/data/gfx/shockbolt/npc'
NAT = lambda f: ('native', NPC / f, None)
NAT_W = 128
# 2x nearest of the native sprite; tall bodies are 64x128 -> 128x256.
NATIVE = {
    'human-citizen': 'humanoid_human_human_citizen.png',
    'halfling-citizen': 'humanoid_halfling_halfling_citizen.png',
    'human-farmer': 'humanoid_human_human_farmer.png',
    'halfling-gardener': 'humanoid_halfling_halfling_gardener.png',
    'lumberjack': 'humanoid_human_lumberjack.png',
    'halfling-slinger': 'humanoid_halfling_halfling_slinger.png',
    'dwarven-earthwarden': 'humanoid_dwarf_dwarven_earthwarden.png',
    'yeek-mindslayer': 'humanoid_yeek_yeek_mindslayer.png',
    'yeek-psionic': 'humanoid_yeek_yeek_psionic.png',
    'thalore-hunter': 'humanoid_thalore_thalore_hunter.png',
    'thalore-wilder': 'humanoid_thalore_thalore_wilder.png',
    'elven-sun-mage': 'humanoid_elf_elven_sun_mage.png',
    'shalore-rune-master': 'humanoid_shalore_shalore_rune_master.png',
    'elven-archer': 'humanoid_elf_elven_archer.png',
}
TALL = {'yeek-mindslayer', 'thalore-wilder'}
IDS = [i for i in NATIVE if i != 'elven-archer']

GROUPS = {
 'citizens': [('shipped ' + i, R(i), None) for i in
              ('caravan-merchant', 'caravan-porter', 'lost-merchant', 'cutpurse', 'thief', 'bandit')]
             + [('TA2 ' + i, X(i), NAT(NATIVE[i])) for i in
                ('human-citizen', 'halfling-citizen', 'human-farmer', 'halfling-gardener',
                 'lumberjack', 'halfling-slinger')],
 'yeeks': [('shipped ' + i, R(i), None) for i in
           ('yeek-wayist', 'yaech-hunter', 'yaech-mindslayer', 'yaech-psion', 'yaech-diver', 'slaver')]
          + [('TA2 ' + i, X(i), NAT(NATIVE[i])) for i in ('yeek-mindslayer', 'yeek-psionic')],
 'dwarves': [('shipped ' + i, R(i), None) for i in
             ('dwarven-guard', 'norgan', 'protector-myssil', 'human-sun-paladin')]
            + [('TA2 dwarven-earthwarden', X('dwarven-earthwarden'), NAT(NATIVE['dwarven-earthwarden']))],
 'thalore': [('shipped ' + i, R(i), None) for i in
             ('berethh', 'companion-warrior', 'companion-archer', 'mindworm')]
            + [('TA2 ' + i, X(i), NAT(NATIVE[i])) for i in ('thalore-hunter', 'thalore-wilder')],
 'elves': [('shipped ' + i, R(i), None) for i in
           ('companion-archer', 'fillarel-aldaren', 'elven-warrior', 'elven-elite-warrior',
            'elven-mage', 'elven-corruptor', 'elven-cultist', 'elven-blood-mage')]
          + [('TA2 ' + i, X(i), NAT(NATIVE[i])) for i in ('elven-sun-mage', 'shalore-rune-master')],
 'wiring-elven-archer': [
    ('native elven archer', NAT(NATIVE['elven-archer']), None),
    ('shipped companion-archer token', R('companion-archer'), None),
    ('TA2 wiring elven-archer token (byte-identical)', X('elven-archer'), None),
 ],
}

RF = ROOT / 'data/gfx/refined/'
FLOOR_TILES = {
    'town road A': RF / 'town/road0.png',
    'town fields A': RF / 'town/fields0.png',
    'grass': RF / 'grass0.png',
    'sand': RF / 'sand/floor0.png',
    'snow ground': RF / 'snow/snow-ground0.png',
    'gothic stone A': RF / 'gothic/floor-a0.png',
    'korpul stone A': RF / 'korpul/floor-a-0-0.png',
    'cave rock': RF / 'cave/floor-rock-1-0.png',
    'burnt ground': RF / 'burnt/floor0.png',
    'gloomy (Heart of the Gloom)': RF / 'gloom/gloomy/floor0.png',
}
ZONE_FLOORS = {
    'human-citizen': ['town road', 'town fields'],
    'halfling-citizen': ['town road', 'town fields'],
    'human-farmer': ['town fields', 'grass'],
    'halfling-gardener': ['town fields', 'grass'],
    'lumberjack': ['grass', 'gothic'],
    'halfling-slinger': ['town fields', 'grass'],
    'dwarven-earthwarden': ['gothic', 'korpul'],
    'yeek-mindslayer': ['grass', 'cave'],
    'yeek-psionic': ['grass', 'cave'],
    'thalore-hunter': ['snow ground', 'grass'],
    'thalore-wilder': ['snow ground', 'grass'],
    'elven-sun-mage': ['sand', 'grass'],
    'shalore-rune-master': ['town road', 'grass'],
    'elven-archer': ['sand', 'grass'],
}
FLOOR_ASSETS = [(i, X(i)) for i in IDS]
FLOOR_ASSETS.append(('elven-archer', X('elven-archer')))


def load(spec, size, scratch, nat_h=128):
    kind, base, asset = spec
    if kind == 'export':
        return Image.open(base / 'sprites' / str(size) / f'{asset}.png').convert('RGBA')
    if kind == 'native':
        return Image.open(base).convert('RGBA').resize((NAT_W, nat_h), Image.NEAREST)
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
    width = 560 + NAT_W + PAD + cell
    tall_sheet = name in ('yeeks', 'thalore')
    row_h = 270 if tall_sheet else 128 + PAD
    height = PAD + len(rows) * row_h
    for mode in ('color', 'grayscale'):
        canvas = Image.new('RGBA', (width, height), BG)
        draw = ImageDraw.Draw(canvas)
        y = PAD
        for label, spec, native in rows:
            draw.text((PAD, y + row_h // 2 - 6), label, fill=(232, 232, 226, 255))
            x = 560
            if native is not None:
                nat_h = 256 if spec[2] in TALL else 128
                draw.text((x, y + 2), 'native 2x', fill=(200, 200, 160, 255))
                image = load(native, NAT_W, scratch, nat_h)
                if mode == 'grayscale':
                    image = gray(image)
                canvas.alpha_composite(image, (x, y))
            x += NAT_W + PAD
            for size in SIZES:
                image = load(spec, size, scratch)
                if mode == 'grayscale':
                    image = gray(image)
                canvas.alpha_composite(image, (x, y + (row_h - PAD - size) // 2))
                x += size + PAD
            y += row_h
        out = HERE / 'review' / f'{name}-{mode}-48-64-96.png'
        out.parent.mkdir(exist_ok=True)
        canvas.convert('RGB').save(out)
        print(out.relative_to(ROOT))


def floor_sheet(scratch):
    size = 48
    tiles = {name: Image.open(path).convert('RGBA').resize((size, size), Image.LANCZOS) for name, path in FLOOR_TILES.items()}
    cell = size + 6
    left = 380

    def render(assets):
        width = left + len(FLOOR_TILES) * cell + PAD
        height = LABEL + PAD + len(assets) * (size + 6) + PAD
        canvas = Image.new('RGBA', (width, height), BG)
        draw = ImageDraw.Draw(canvas)
        x = left
        for i, name in enumerate(FLOOR_TILES):
            draw.text((x, 2 + (i % 2) * 11), name.split(' ')[0][:9], fill=(232, 232, 226, 255))
            x += cell
        y = LABEL + PAD
        for label, spec in assets:
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
        return canvas.convert('RGB')

    review = HERE / 'review'
    review.mkdir(exist_ok=True)
    render(FLOOR_ASSETS).save(review / 'floor-readability-48.png')
    print((review / 'floor-readability-48.png').relative_to(ROOT))
    half = (len(FLOOR_ASSETS) + 1) // 2
    for name, assets in (('floor-readability-48-x2.png', FLOOR_ASSETS[:half]), ('floor-readability-48-x2-b.png', FLOOR_ASSETS[half:])):
        sheet_ = render(assets)
        sheet_.resize((sheet_.width * 2, sheet_.height * 2), Image.NEAREST).save(review / name)
        print((review / name).relative_to(ROOT))


def luminance(scratch):
    import json, math, hashlib
    out = {'method': '128px export; alpha>=180 pixels with d<=0.55 of centre; L=0.299R+0.587G+0.114B',
           'floor_minimum_for_body': 45.0, 'body_minimum': 65.0, 'assets': {}, 'floors': {}}
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
    out['note'] = "floor-readability-48.png draws a yellow frame around the floors of each creature's own zones (ZONE_FLOORS)"
    (HERE / 'review' / 'luminance.json').write_text(json.dumps(out, indent=2))
    print(json.dumps(out['assets'], indent=2))
    pins = {name: {'path': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()} for name, path in FLOOR_TILES.items()}
    (HERE / 'review' / 'floor-source-pins.json').write_text(json.dumps(pins, indent=2) + '\n')


if __name__ == '__main__':
    with tempfile.TemporaryDirectory(prefix='batch-ta2-review-', dir='<workspace>/tmp/rotation/R27-scratch') as scratch:
        for group, rows in GROUPS.items():
            sheet(group, rows, scratch)
        floor_sheet(scratch)
        luminance(scratch)
