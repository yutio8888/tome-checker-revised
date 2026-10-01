"""UB-1 review sheets: unchanged UA/TA-1 geometry, 48/64/96 colour and
grayscale with shipped unique/kin siblings, ten real floors and the unchanged
central masked-body luminance measurement. No creature painting.
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
WS = ROOT.parents[2]
NPC = WS / 'game/modules/tome/data/gfx/shockbolt/npc'
NAT = lambda f: ('native', NPC / f, None)
# Native body beside each UB-1 token (2x nearest) so the portrait can be compared directly.
NATIVE = {
 'high-sun-paladin-aeryn': 'humanoid_human_high_sun_paladin_aeryn.png',
 'fallen-sun-paladin-aeryn': 'humanoid_human_fallen_sun_paladin_aeryn.png',
 'caldizar': 'horror_sher_tul_caldizar.png',
 'chronolith-twin': 'horror_temporal_cronolith_twin.png',
 'chronolith-clone': 'horror_temporal_cronolith_clone.png',
 'temporal-defiler': 'horror_temporal_temporal_defiler.png',
 'corrupted-daelach': 'demon_major_corrupted_daelach.png',
 'supreme-archmage-linaniil': 'humanoid_human_linaniil_supreme_archmage.png',
 'archmage-tarelion': 'humanoid_shalore_archmage_tarelion.png',
}
NAT_W, NAT_H = 128, 256  # 2x nearest of the 64x128 native sprite

GROUPS = {
 'sun-paladins': [('shipped ' + i, R(i), None) for i in
                  ('human-sun-paladin', 'high-sun-paladin-rodmour', 'aluin-the-fallen', 'argoniel', 'elandar')]
                 + [('UB1 ' + i, X(i), NAT(NATIVE[i])) for i in ('high-sun-paladin-aeryn', 'fallen-sun-paladin-aeryn')],
 'shertul': [('shipped fortress-shadow', R('fortress-shadow'), None)]
            + [('UB1 caldizar', X('caldizar'), NAT(NATIVE['caldizar']))],
 'temporal-horrors': [('shipped ' + i, R(i), None) for i in
                      ('temporal-stalker', 'dredgling', 'dredge', 'void-horror', 'telugoroth', 'teluvorta')]
                     + [('UB1 ' + i, X(i), NAT(NATIVE[i])) for i in ('chronolith-twin', 'chronolith-clone', 'temporal-defiler')],
 'archmages': [('shipped ' + i, R(i), None) for i in
               ('elven-mage', 'rhaloren-inquisitor', 'necromancer', 'fillarel-aldaren', 'grand-corruptor', 'elven-blood-mage')]
              + [('UB1 ' + i, X(i), NAT(NATIVE[i])) for i in ('supreme-archmage-linaniil', 'archmage-tarelion')],
 'demons': [('shipped ' + i, R(i), None) for i in
            ('daelach', 'lithfengel', 'kryl-feijan', 'uruivellas', 'champion-of-urh-rok', 'forge-giant')]
           + [('UB1 corrupted-daelach', X('corrupted-daelach'), NAT(NATIVE['corrupted-daelach']))],
}

RF = ROOT / 'data/gfx/refined/'
FLOOR_TILES = {
    'shertul stone': RF / 'shertul/floor0.png',
    'void': RF / 'void/floor0.png',
    'gothic stone A': RF / 'gothic/floor-a0.png',
    'korpul stone A': RF / 'korpul/floor-a-0-0.png',
    'sand': RF / 'sand/floor0.png',
    'town road A': RF / 'town/road0.png',
    'cave rock': RF / 'cave/floor-rock-1-0.png',
    'grass': RF / 'grass0.png',
    'burnt ground': RF / 'burnt/floor0.png',
    'snow ground': RF / 'snow/snow-ground0.png',
}
IDS = ['high-sun-paladin-aeryn', 'fallen-sun-paladin-aeryn', 'caldizar', 'chronolith-twin', 'chronolith-clone',
       'temporal-defiler', 'corrupted-daelach', 'supreme-archmage-linaniil', 'archmage-tarelion']
ZONE_FLOORS = {
    'high-sun-paladin-aeryn': ['korpul stone A', 'sand'],
    'fallen-sun-paladin-aeryn': ['korpul stone A'],
    'caldizar': ['shertul stone', 'void'],
    'chronolith-twin': ['cave rock', 'void'],
    'chronolith-clone': ['cave rock', 'void'],
    'temporal-defiler': ['town road A', 'void'],
    'corrupted-daelach': ['grass', 'sand'],
    'supreme-archmage-linaniil': ['gothic stone A', 'town road A'],
    'archmage-tarelion': ['gothic stone A', 'town road A'],
}
FLOOR_ASSETS = [(i, X(i)) for i in IDS]
SUPERSEDED = []


def load(spec, size, scratch):
    kind, base, asset = spec
    if kind == 'export':
        return Image.open(base / 'sprites' / str(size) / f'{asset}.png').convert('RGBA')
    if kind == 'native':
        return Image.open(base).convert('RGBA').resize((NAT_W, NAT_H), Image.NEAREST)
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
    width = 560 + NAT_W + PAD + cell
    row_h = NAT_H + PAD
    height = PAD + len(rows) * row_h
    for mode in ('color', 'grayscale'):
        canvas = Image.new('RGBA', (width, height), BG)
        draw = ImageDraw.Draw(canvas)
        y = PAD
        for label, spec, native in rows:
            draw.text((PAD, y + row_h // 2 - 6), label, fill=(232, 232, 226, 255))
            x = 560
            if native is not None:
                draw.text((x, y + 2), 'native 2x', fill=(200, 200, 160, 255))
                image = load(native, NAT_W, scratch)
                if mode == 'grayscale':
                    image = gray(image)
                canvas.alpha_composite(image, (x, y))
            x += NAT_W + PAD
            for size in SIZES:
                image = load(spec, size, scratch)
                if mode == 'grayscale':
                    image = gray(image)
                canvas.alpha_composite(image, (x, y + (NAT_H - size) // 2))
                x += size + PAD
            y += row_h
        out = HERE / 'review' / f'{name}-{mode}-48-64-96.png'
        out.parent.mkdir(exist_ok=True)
        canvas.convert('RGB').save(out)
        print(out.relative_to(ROOT))


def floor_sheet(scratch):
    """48px composite of every batch-UB1 asset on each real floor tile, the tile
    resampled to the 48px cell the board draws (no tile is cropped). The whole
    9-row sheet is written at 1x; the 2x version is split into two halves."""
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
           'floor_minimum_for_body': 45.0, 'assets': {}, 'floors': {}}
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
    with tempfile.TemporaryDirectory(prefix='batch-ub1-review-', dir='/workspace/t-engine4/tmp/rotation/R22-scratch') as scratch:
        for group, rows in GROUPS.items():
            sheet(group, rows, scratch)
        floor_sheet(scratch)
        luminance(scratch)
