#!/usr/bin/env python3
"""Export the selected Irkkk bamboo-hut masters into board wall, floor and door tiles.

TW6 (Irkkk). Four masters -- an opaque overhead thatch-and-bamboo wall-top
material, a native-alpha bamboo palisade wall section, an opaque woven-mat
hut floor and a native-alpha palm-frond door leaf -- become:

* 16 N/E/S/W neighbour masks x 2 checker parities of cell-filling 128px RGB
  hut-wall tiles (the same construction as the golden-mountain and cave wall
  families): the whole cell is dark thatch top (a fixed window of the top
  master per mask, toned well below every floor it touches); an edge facing a
  non-wall neighbour gets a thin light rim (N/W) or a shaded side (E), and a
  south edge facing open ground shows the master's own bamboo culm face with a
  contact shadow. A hut door counts as a connected wall neighbour, so the wall
  line runs into the doorway without a false end;
* 2 parities of the calm woven-mat hut floor (walls, shops and cooking pits
  stand on it);
* horizontal/vertical x closed/open x 2 parities of floor-based door tiles:
  the closed leaf spans the doorway between two short thatch posts, the open
  leaf is swung against the west (horizontal) or north (vertical) post so the
  floor reads through, the board language of the Kor'Pul doors.

Parity 1 = x0.875. Bit order N=1 E=2 S=4 W=8 (CheckerTerrain.lua dirs).
Deterministic: fixed crops, no noise. Writes exports/runtime,
data/gfx/refined/bamboo, review/ and export-manifest.json.
"""
from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter, ImageOps, ImageStat
import hashlib, json, os, shutil

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
TOP = HERE / 'selected/floor-bamboo-wall-top.png'    # opaque overhead thatch: cell-filling wall top
WALL = HERE / 'selected/prop-bamboo-hut-wall.png'     # native-alpha palisade: south culm faces
FLOOR = HERE / 'selected/floor-bamboo-hut-floor.png'  # opaque woven mat: hut floor
DOOR = HERE / 'selected/prop-bamboo-hut-door.png'     # native-alpha palm-frond door leaf
RUNTIME = ROOT / 'data/gfx/refined/bamboo'
SIZE = 128
PARITY = .875
# Wall top: one fixed square window of the thatch master per mask, darkened
# and flattened so the blocking mass sits well below the jungle grass (82-97)
# and the hut floor.
WINDOW = 380
TOP_BRIGHTNESS = .80
TOP_CONTRAST = .78
# Fraction of the palisade master's opaque bounding box holding its bamboo
# culm face (below the thatch cap), measured on the selected master.
FACE = (.06, .30, .93, .99)
FACE_H = 44
FACE_BRIGHTNESS = .82
# Ridge poles along the wall line (centre height and pole width).
RIDGE_Y = 46
RIDGE_W = 24
RIDGE_BRIGHTNESS = .85
RIM = (176, 138, 82, 255)      # dry-thatch highlight catching upper-left light
# Floor: a centred window of the mat master, calmer and a little darker.
FLOOR_WINDOW = 520
FLOOR_BRIGHTNESS = .80
FLOOR_CONTRAST = .72
# Doors: leaf face crop of the door master's opaque box, band thickness,
# post width and the open leaf's width.
LEAF = (.0, .08, 1.0, .92)      # woven leaf between its stiles (skewed top/bottom rails trimmed)
EDGE = (.0, .08, .20, .92)      # the leaf's west stile: the open leaf seen edge-on
BAND = 46
POST = 16
OPEN_W = 20
DOOR_BRIGHTNESS = .92


def body(im):
    """Opaque bounding box (alpha >= 128): the soft generated halo is ignored."""
    return im.crop(im.getchannel('A').point(lambda a: 255 if a >= 128 else 0).getbbox())


def frac(im, box):
    w, h = im.size
    return im.crop((int(w * box[0]), int(h * box[1]), int(w * box[2]), int(h * box[3])))


def tone(im, brightness, contrast):
    return ImageEnhance.Brightness(ImageEnhance.Contrast(im).enhance(contrast)).enhance(brightness)


def top_cell(top, mask):
    cw, ch = top.size
    sx = (mask * 211) % (cw - WINDOW)
    sy = (mask * 137) % (ch - WINDOW)
    cell = top.crop((sx, sy, sx + WINDOW, sy + WINDOW)).resize((SIZE, SIZE), Image.Resampling.LANCZOS)
    return tone(cell, TOP_BRIGHTNESS, TOP_CONTRAST).convert('RGBA')


def ridge(tile, face, mask):
    """Bamboo ridge poles lashed along the wall line: from the cell's ridge
    centre a single culm (cropped from the palisade face) runs to every side
    whose neighbour is also wall/door, so the pole network follows the
    connected hut outline; an unconnected cell keeps a short stub."""
    cx, cy, half = SIZE // 2, RIDGE_Y, RIDGE_W // 2
    runs = []
    if mask & 1:
        runs.append((cx - half, 0, cx + half, cy + half))
    if mask & 4:
        runs.append((cx - half, cy - half, cx + half, SIZE))
    if mask & 8:
        runs.append((0, cy - half, cx + half, cy + half))
    if mask & 2:
        runs.append((cx - half, cy - half, SIZE, cy + half))
    if not runs:
        runs.append((cx - 20, cy - half, cx + 20, cy + half))
    shade = Image.new('L', tile.size, 0)
    for x0, y0, x1, y1 in runs:
        shade.paste(110, (x0 + 2, y0 + 3, x1 + 2, y1 + 3))
    shade = shade.filter(ImageFilter.GaussianBlur(2))
    tile = Image.composite(Image.new('RGBA', tile.size, (16, 10, 5, 255)), tile, shade)
    # Vertical runs first, horizontal on top: the E-W pole binds over the N-S one.
    for x0, y0, x1, y1 in sorted(runs, key=lambda r: (r[2] - r[0]) > (r[3] - r[1])):
        w, h = x1 - x0, y1 - y0
        piece = face if h >= w else face.rotate(90, expand=True)
        tile.alpha_composite(bright(ImageOps.fit(piece, (w, h), method=Image.Resampling.LANCZOS), RIDGE_BRIGHTNESS), (x0, y0))
    return tile


def wall_tile(top, face, mask):
    tile = ridge(top_cell(top, mask), face, mask)
    if not mask & 1:
        rim = Image.new('RGBA', (SIZE, 4), RIM)
        tile.paste(Image.blend(tile.crop((0, 0, SIZE, 4)), rim, .45), (0, 0))
    if not mask & 8:
        rim = Image.new('RGBA', (3, SIZE), RIM)
        tile.paste(Image.blend(tile.crop((0, 0, 3, SIZE)), rim, .30), (0, 0))
    if not mask & 2:
        strip = ImageEnhance.Brightness(tile.crop((110, 0, 122, SIZE))).enhance(.62)
        tile.paste(strip.resize((9, SIZE)), (119, 0))
    if not mask & 4:
        cliff = ImageOps.fit(face, (SIZE, FACE_H), method=Image.Resampling.LANCZOS)
        tile.alpha_composite(bright(cliff, FACE_BRIGHTNESS), (0, SIZE - FACE_H))
        shadow = Image.new('RGBA', (SIZE, 4), (22, 14, 8, 255))
        tile.paste(Image.blend(tile.crop((0, SIZE - FACE_H - 3, SIZE, SIZE - FACE_H + 1)), shadow, .55),
                   (0, SIZE - FACE_H - 3))
    return tile


def floor_tile(floor):
    w, h = floor.size
    x0, y0 = (w - FLOOR_WINDOW) // 2, (h - FLOOR_WINDOW) // 2
    cell = floor.crop((x0, y0, x0 + FLOOR_WINDOW, y0 + FLOOR_WINDOW)).resize((SIZE, SIZE), Image.Resampling.LANCZOS)
    return tone(cell, FLOOR_BRIGHTNESS, FLOOR_CONTRAST).convert('RGBA')


def shadow_under(tile, box, strength=.45, blur=3):
    """Soft contact shadow for a door leaf/post lying at `box` on the floor."""
    mask = Image.new('L', tile.size, 0)
    x0, y0, x1, y1 = box
    mask.paste(int(255 * strength), (x0 + 2, y0 + 3, x1 + 2, y1 + 3))
    mask = mask.filter(ImageFilter.GaussianBlur(blur))
    dark = Image.new('RGBA', tile.size, (18, 12, 6, 255))
    return Image.composite(dark, tile, mask)


def bright(im, factor):
    """Brightness of the colour channels only; alpha is kept."""
    rgb = ImageEnhance.Brightness(im.convert('RGB')).enhance(factor)
    if im.mode == 'RGBA':
        rgb.putalpha(im.getchannel('A'))
    return rgb


def door_tile(floor, top, leaf, edge, horizontal, opened):
    tile = floor_tile(floor)
    if horizontal:
        band = (0, (SIZE - BAND) // 2, SIZE, (SIZE + BAND) // 2)
        posts = [(0, band[1], POST, band[3]), (SIZE - POST, band[1], SIZE, band[3])]
        # Open: the leaf swung against the west post, seen edge-on as its
        # bamboo stile; closed: the woven leaf spans the doorway.
        box = (POST, band[1] - 34, POST + OPEN_W, band[3] + 34) if opened else (POST, band[1], SIZE - POST, band[3])
        piece = edge if opened else leaf
    else:
        band = ((SIZE - BAND) // 2, 0, (SIZE + BAND) // 2, SIZE)
        posts = [(band[0], 0, band[2], POST), (band[0], SIZE - POST, band[2], SIZE)]
        box = (band[0] - 34, POST, band[2] + 34, POST + OPEN_W) if opened else (band[0], POST, band[2], SIZE - POST)
        piece = (edge if opened else leaf).rotate(90, expand=True)
    bw, bh = box[2] - box[0], box[3] - box[1]
    face = bright(ImageOps.fit(piece, (bw, bh), method=Image.Resampling.LANCZOS), DOOR_BRIGHTNESS)
    tile = shadow_under(tile, box)
    tile.alpha_composite(face, box[:2])
    for p in posts:
        tile = shadow_under(tile, p, .5, 2)
        tile.paste(top_cell(top, 15).crop((0, 0, p[2] - p[0], p[3] - p[1])), p[:2])
    return tile


def lum(im, box=None):
    return ImageStat.Stat((im.crop(box) if box else im).convert('L')).mean[0]


def save(tile, name, out, review, hashes, lums):
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


def dim(tile):
    return ImageEnhance.Brightness(tile).enhance(PARITY)


def main():
    top = Image.open(TOP)
    assert top.mode == 'RGB' and top.size[0] == top.size[1], (top.mode, top.size)
    floor = Image.open(FLOOR)
    assert floor.mode == 'RGB' and floor.size[0] == floor.size[1], (floor.mode, floor.size)
    wall = Image.open(WALL)
    assert wall.mode == 'RGBA', wall.mode
    door = Image.open(DOOR)
    assert door.mode == 'RGBA', door.mode
    face = frac(body(wall), FACE)
    leaf = frac(body(door), LEAF)
    edge = frac(body(door), EDGE)
    out = HERE / 'exports/runtime'
    review = HERE / 'review'
    hashes, lums = {}, {}
    for parity in (0, 1):
        for mask in range(16):
            t = wall_tile(top, face, mask)
            save(dim(t) if parity else t, f'wall-{mask}-{parity}.png', out, review, hashes, lums)
        f = floor_tile(floor)
        save(dim(f) if parity else f, f'floor{parity}.png', out, review, hashes, lums)
        for state in ('closed', 'open'):
            for orient in ('horizontal', 'vertical'):
                d = door_tile(floor, top, leaf, edge, orient == 'horizontal', state == 'open')
                save(dim(d) if parity else d, f'door-{state}-{orient}{parity}.png', out, review, hashes, lums)
    # Board floors the huts touch in Irkkk: jungle grass (Caldera art) and the new hut floor.
    grass = {p: round(lum(Image.open(ROOT / 'data/gfx/refined/caldera' / f'floor{p}.png')), 3) for p in (0, 1)}
    walls0 = [lums[f'wall-{m}-0.png'] for m in range(16)]
    interior = lums['wall-15-0.png']
    darkest_floor0 = min(grass[0], lums['floor0.png'])
    metrics = {
        'interior_luminance': interior,
        'max_wall_luminance_parity0': max(walls0),
        'hut_floor_luminance': {'floor0': lums['floor0.png'], 'floor1': lums['floor1.png']},
        'jungle_grass_luminance': grass,
        'relative_gap_interior_to_floor': {'hut-floor': round((lums['floor0.png'] - interior) / lums['floor0.png'], 4),
                                           'jungle-grass': round((grass[0] - interior) / grass[0], 4)},
        'brightest_wall_vs_darkest_floor_parity0': round((darkest_floor0 - max(walls0)) / darkest_floor0, 4),
        'min_parity_gap': round(min((lums[n] - lums[n[:-5] + '1.png']) / lums[n] for n in lums if n.endswith('0.png')), 4),
        'door_luminance': {n: lums[n] for n in lums if n.startswith('door')},
    }
    (HERE / 'export-manifest.json').write_text(json.dumps({
        'count': len(hashes),
        'masters': {k: {'path': os.path.relpath(p, HERE), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
                    for k, p in (('top', TOP), ('wall', WALL), ('floor', FLOOR), ('door', DOOR))},
        'runtime_dir': os.path.relpath(RUNTIME, ROOT), 'files': hashes, 'luminance': lums, 'metrics': metrics,
        'constants': {'WINDOW': WINDOW, 'TOP_BRIGHTNESS': TOP_BRIGHTNESS, 'TOP_CONTRAST': TOP_CONTRAST, 'FACE': FACE,
                      'FACE_H': FACE_H, 'FACE_BRIGHTNESS': FACE_BRIGHTNESS,
                      'RIDGE_Y': RIDGE_Y, 'RIDGE_W': RIDGE_W, 'RIDGE_BRIGHTNESS': RIDGE_BRIGHTNESS, 'RIM': RIM, 'FLOOR_WINDOW': FLOOR_WINDOW,
                      'FLOOR_BRIGHTNESS': FLOOR_BRIGHTNESS, 'FLOOR_CONTRAST': FLOOR_CONTRAST, 'LEAF': LEAF, 'EDGE': EDGE, 'BAND': BAND,
                      'POST': POST, 'OPEN_W': OPEN_W, 'DOOR_BRIGHTNESS': DOOR_BRIGHTNESS, 'PARITY': PARITY},
    }, indent=2) + '\n')
    for size in (48, 64, 96):
        names = [f'wall-{m}-{p}.png' for p in (0, 1) for m in range(16)]
        sheet = Image.new('RGB', (16 * size, 3 * size), (30, 30, 30))
        for i, n in enumerate(names):
            sheet.paste(Image.open(review / str(size) / n), ((i % 16) * size, (i // 16) * size))
        extra = [f'floor{p}.png' for p in (0, 1)] + [f'door-{s}-{o}{p}.png' for s in ('closed', 'open')
                                                     for o in ('horizontal', 'vertical') for p in (0, 1)]
        for i, n in enumerate(extra):
            sheet.paste(Image.open(review / str(size) / n), (i * size, 2 * size))
        sheet.save(review / f'contact-{size}.png')
    # 64px connected field: Irkkk's market corner -- the west hut with its
    # vertical door and shops, the hut with a horizontal door, cooking pits,
    # jungle grass, trees and the lake.
    plan = ['~~~..t...t..',
            '~~~.......t.',
            '~~..#####...',
            '~~..#___#.t.',
            '~~..#_s_V...',
            '~~..#___#...',
            '~~..##D##.**',
            '~~~.......**',
            '~~~..t..____']
    field = Image.new('RGB', (len(plan[0]) * 64, len(plan) * 64))
    doorish = set('DV')
    for y, row in enumerate(plan):
        for x, c in enumerate(row):
            p = (x + y) % 2
            if c == '#':
                m = sum(bit for dx, dy, bit in ((0, -1, 1), (1, 0, 2), (0, 1, 4), (-1, 0, 8))
                        if 0 <= y + dy < len(plan) and 0 <= x + dx < len(row) and plan[y + dy][x + dx] in '#' + ''.join(doorish))
                tile = Image.open(out / f'wall-{m}-{p}.png')
            elif c == 'D':
                tile = Image.open(out / f'door-closed-horizontal{p}.png')
            elif c == 'V':
                tile = Image.open(out / f'door-open-vertical{p}.png')
            elif c in '_s*':
                tile = Image.open(out / f'floor{p}.png').convert('RGBA')
                if c == '*':
                    pit = Image.open(ROOT.parents[1] / 'modules/tome/data/gfx/shockbolt/terrain/bamboo/floor_deco_cooking_pit_c_01.png').convert('RGBA').resize((SIZE, SIZE))
                    tile.alpha_composite(pit)
            elif c == '~':
                tile = Image.open(ROOT / 'data/gfx/refined' / f'deep{15 if 0 < x < 2 else 5}-{p}-0.png')
            elif c == 't':
                tile = Image.open(ROOT / 'data/gfx/refined/caldera' / f'tree-{"abc"[(x * 17 + y * 7) % 3]}{p}.png')
            else:
                tile = Image.open(ROOT / 'data/gfx/refined/caldera' / f'floor{p}.png')
            field.paste(tile.convert('RGB').resize((64, 64), Image.Resampling.LANCZOS), (x * 64, y * 64))
    field.save(review / 'hut-field-64.png')
    print(len(hashes), 'tiles', json.dumps(metrics))


if __name__ == '__main__':
    main()
