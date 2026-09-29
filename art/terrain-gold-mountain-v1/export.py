#!/usr/bin/env python3
"""Export the selected Sunwall golden-mountain master into connected board walls.

TW5 (Gates of Morning). Two masters -- a native-alpha raised golden sandstone
block and an opaque overhead crest material -- become 16 N/E/S/W neighbour
masks x 2 checker parities of cell-filling 128px RGB wall tiles, the same
construction as the accepted cave and crystal wall families
(art/terrain-cave-v1/export.py):

* the whole cell is crumpled golden crest rock (a fixed window of the crest
  master per mask), toned down so the blocking mass reads clearly below the
  town's floor, grass, sand and road tiles (board luminance 109-134); the
  block's own stepped plateau was tried first and read as wooden boards;
* an edge facing a non-mountain neighbour gets a thin warm-gold sunlit ridge
  (N) or a shaded side (E/W), and a south edge facing open ground shows the
  master's own darker strata cliff face -- the only place a cliff appears, so
  the connected ring has a continuous top and no repeated interior stripe;
* parity 1 is the same tile at 0.875 brightness (>= 10% separation).

Bit order N=1 E=2 S=4 W=8 (CheckerTerrain.lua dirs); a set bit means the
neighbour is also Sunwall mountain. Deterministic: fixed crops, no noise.
Writes exports/runtime, data/gfx/refined/gold-mountain, review/ and
export-manifest.json.
"""
from pathlib import Path
from PIL import Image, ImageEnhance, ImageOps, ImageStat
import hashlib, json, os, shutil

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
MASTER = HERE / 'selected/prop-gold-mountain.png'     # native-alpha block: south cliff faces
CREST = HERE / 'selected/floor-gold-crest.png'        # opaque overhead crest: cell-filling top
RUNTIME = ROOT / 'data/gfx/refined/gold-mountain'
SIZE = 128
# Fraction of the block master's opaque bounding box holding its front cliff
# face (measured on the selected master; see REVIEW.md).
FACE = (.14, .52, .86, .88)
FACE_H = 36
FACE_BRIGHTNESS = .42
# Crest windows: one fixed square window of the crest master per mask, so the
# 16 masks do not repeat one texture across the ring.
WINDOW = 420
TOP_GAMMA = 1.5
TOP_COLOR = .95
HUE = (.96, 1.0, .90)
PARITY = .875
RIDGE = (214, 160, 62, 255)   # warm Sunwall gold catching upper-left light


def material(im):
    # Opaque bounding box (alpha >= 128): the soft generated halo is ignored.
    body = im.crop(im.getchannel('A').point(lambda a: 255 if a >= 128 else 0).getbbox())
    w, h = body.size
    return body.crop((int(w * FACE[0]), int(h * FACE[1]), int(w * FACE[2]), int(h * FACE[3])))


def wall_tile(crest, face, mask):
    cw, ch = crest.size
    sx = (mask * 211) % (cw - WINDOW)
    sy = (mask * 137) % (ch - WINDOW)
    cell = crest.crop((sx, sy, sx + WINDOW, sy + WINDOW)).resize((SIZE, SIZE), Image.Resampling.LANCZOS)
    # Tone: a power curve darkens the sandstone's mid-tones and crevices more
    # than its sunlit crags, so the mass sits clearly below every floor tile
    # while its gold highlights keep the Sunwall identity.
    rgb = cell.point([int(round(255 * (i / 255) ** TOP_GAMMA)) for i in range(256)] * 3)
    rgb = ImageEnhance.Color(rgb).enhance(TOP_COLOR)
    r, g, b = rgb.split()
    rgb = Image.merge('RGB', [c.point(lambda v, k=k: int(round(v * k))) for c, k in zip((r, g, b), HUE)])
    tile = rgb.convert('RGBA')
    if not mask & 1:
        # Sunlit crest along an open north edge.
        rim = Image.new('RGBA', (SIZE, 5), RIDGE)
        tile.paste(Image.blend(tile.crop((0, 0, SIZE, 5)), rim, .50), (0, 0))
    if not mask & 8:
        rim = Image.new('RGBA', (3, SIZE), RIDGE)
        tile.paste(Image.blend(tile.crop((0, 0, 3, SIZE)), rim, .30), (0, 0))
        strip = ImageEnhance.Brightness(tile.crop((6, 0, 17, SIZE))).enhance(.80)
        tile.paste(strip.resize((8, SIZE)), (3, 0))
    if not mask & 2:
        strip = ImageEnhance.Brightness(tile.crop((109, 0, 121, SIZE))).enhance(.66)
        tile.paste(strip.resize((9, SIZE)), (119, 0))
    if not mask & 4:
        cliff = ImageOps.fit(face, (SIZE, FACE_H), method=Image.Resampling.LANCZOS)
        cliff = ImageEnhance.Brightness(cliff).enhance(FACE_BRIGHTNESS)
        tile.alpha_composite(cliff.convert('RGBA'), (0, SIZE - FACE_H))
        shadow = Image.new('RGBA', (SIZE, 4), (24, 15, 9, 255))
        tile.paste(Image.blend(tile.crop((0, SIZE - FACE_H - 3, SIZE, SIZE - FACE_H + 1)), shadow, .55), (0, SIZE - FACE_H - 3))
    return tile


def lum(im):
    return ImageStat.Stat(im.convert('L')).mean[0]


def main():
    im = Image.open(MASTER)
    assert im.mode == 'RGBA', im.mode
    face = material(im)
    crest = Image.open(CREST)
    assert crest.mode == 'RGB' and crest.size[0] == crest.size[1], (crest.mode, crest.size)
    out = HERE / 'exports/runtime'
    review = HERE / 'review'
    hashes, lums = {}, {}
    for parity in (0, 1):
        for mask in range(16):
            name = f'wall-{mask}-{parity}.png'
            tile = wall_tile(crest, face, mask)
            if parity:
                tile = ImageEnhance.Brightness(tile).enhance(PARITY)
            tile = tile.convert('RGB')
            path = out / name
            path.parent.mkdir(parents=True, exist_ok=True)
            tile.save(path, optimize=True)
            RUNTIME.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, RUNTIME / name)
            hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
            lums[name] = round(lum(tile), 3)
            for size in (48, 64, 96):
                target = review / str(size) / name
                target.parent.mkdir(parents=True, exist_ok=True)
                tile.resize((size, size), Image.Resampling.LANCZOS).save(target)
    # Board floors the ring touches in Gates of Morning (existing runtime art).
    floors = {'stone-floor': 'korpul/floor-a-0-0.png', 'grass': 'grass0.png', 'sand': 'beach/sand0.png', 'road': 'road0.png'}
    floor_lum = {k: round(lum(Image.open(ROOT / 'data/gfx/refined' / v)), 3) for k, v in floors.items()}
    interior = lums['wall-15-0.png']
    metrics = {
        'interior_luminance': interior,
        'floor_luminance': floor_lum,
        'relative_gap_to_floor': {k: round((v - interior) / v, 4) for k, v in floor_lum.items()},
        'min_parity_gap': round(min((lums[n] - lums[n[:-5] + '1.png']) / lums[n] for n in lums if n.endswith('-0.png')), 4),
        'max_wall_luminance': max(lums.values()),
    }
    (HERE / 'export-manifest.json').write_text(json.dumps({
        'count': len(hashes), 'master': {'path': os.path.relpath(MASTER, HERE), 'sha256': hashlib.sha256(MASTER.read_bytes()).hexdigest()},
        'crest': {'path': os.path.relpath(CREST, HERE), 'sha256': hashlib.sha256(CREST.read_bytes()).hexdigest()},
        'runtime_dir': os.path.relpath(RUNTIME, ROOT), 'files': hashes, 'luminance': lums, 'metrics': metrics,
        'constants': {'WINDOW': WINDOW, 'FACE': FACE, 'FACE_H': FACE_H, 'TOP_GAMMA': TOP_GAMMA, 'TOP_COLOR': TOP_COLOR, 'HUE': HUE, 'FACE_BRIGHTNESS': FACE_BRIGHTNESS, 'PARITY': PARITY, 'RIDGE': RIDGE},
    }, indent=2) + '\n')
    # Contact sheets (all 16 masks x 2 parities) and a 64px connected field:
    # a ring round a stone/grass/sand clearing like the town's.
    for size in (48, 64, 96):
        sheet = Image.new('RGB', (16 * size, 2 * size))
        for parity in (0, 1):
            for mask in range(16):
                sheet.paste(Image.open(review / str(size) / f'wall-{mask}-{parity}.png'), (mask * size, parity * size))
        sheet.save(review / f'contact-{size}.png')
    plan = ['mmmmmmmmmmmm',
            'mmmmm..mmmmm',
            'mm.......mmm',
            'm..#2#.....m',
            'm..###..gg.m',
            'mm..__..ggmm',
            'm...ss.....m',
            'mmm.sssmm.mm',
            'mmmmmmmmmmmm']
    floor_tiles = {'.': 'korpul/floor-a-0-%d.png', '_': 'road%d.png', 'g': 'grass%d.png', 's': 'beach/sand%d.png',
                   '#': 'korpul/hardwall-0-%d.png', '2': 'korpul/hardwall-0-%d.png'}
    field = Image.new('RGB', (len(plan[0]) * 64, len(plan) * 64))
    for y, row in enumerate(plan):
        for x, c in enumerate(row):
            p = (x + y) % 2
            if c == 'm':
                m = sum(bit for dx, dy, bit in ((0, -1, 1), (1, 0, 2), (0, 1, 4), (-1, 0, 8))
                        if 0 <= y + dy < len(plan) and 0 <= x + dx < len(row) and plan[y + dy][x + dx] == 'm')
                tile = Image.open(out / f'wall-{m}-{p}.png')
            else:
                tile = Image.open(ROOT / 'data/gfx/refined' / (floor_tiles[c] % p))
            field.paste(tile.convert('RGB').resize((64, 64), Image.Resampling.LANCZOS), (x * 64, y * 64))
    field.save(review / 'wall-field-64.png')
    print(len(hashes), 'tiles', json.dumps(metrics))


if __name__ == '__main__':
    main()
