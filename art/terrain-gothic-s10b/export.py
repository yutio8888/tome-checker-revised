#!/usr/bin/env python3
"""Export the S10b gothic masters into 128px board tiles (Vor Pride).

Three ImageGen masters -- an opaque pale limestone flagstone floor
(masters/gothic-floor-v1.png), an opaque dark slate coping wall top with iron
clamps (masters/gothic-wall-top-v1.png) and a native-alpha iron-bound oak
door leaf (masters/gothic-door-v1.png) -- become the board gothic family,
built the same way as the accepted cave / slime / bamboo-hut families. (The
separate wall-face section was not generated: both calls of its pack failed,
see REVIEW.md; the south face is built from the wall-top master as in the
slime family.)

* floor-<v><p> (v = a, b, c): one whole flagstone of the floor master per
  cell, cropped from joint centre to joint centre so two neighbouring cells
  form one full joint on the board grid line; each flag is levelled to the
  same value and toned calm (the three variants differ in veining only);
* wall-<mask>-<p>: the whole cell is dark slate coping (one fixed master
  window per mask), toned well below the floor; an open north edge gets a
  thin cool rim, open west a thin rim, open east a shaded side, and an open
  south edge the only face: two courses of the same slate compressed and
  darkened under a lit coping lip, with a contact shadow. Bit order N=1 E=2 S=4 W=8 (CheckerTerrain.lua dirs); a set
  bit means the neighbour is gothic wall, a gothic door or a native lever door;
* door-{closed,open}-{horizontal,vertical}<p>: gothic floor with two dark
  slate jamb posts in the wall line; closed = the oak leaf spans the doorway,
  open = the leaf swung against the west/north post, seen edge-on (the
  Kor'Pul / bamboo door language);
* exit-{up,down,world}<p>: the board's shared Kor'Pul stair pieces
  (refined/korpul/stairs-*.png, unchanged; the stone adapter draws basic.lua
  flat exits with the same pieces) on floor-a.

Parity 1 = x0.875. Deterministic: fixed crops, no noise. Writes
exports/runtime, data/gfx/refined/gothic, review/ and export-manifest.json.
"""
from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter, ImageOps, ImageStat
import hashlib, json, shutil

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
RUNTIME = ROOT / 'data/gfx/refined/gothic'
REFINED = ROOT / 'data/gfx/refined'
KORPUL = REFINED / 'korpul'
MASTERS = {n: HERE / 'masters' / f'{n}-v1.png' for n in ('gothic-floor', 'gothic-wall-top', 'gothic-door')}
SIZE = 128
PARITY = .875
# Floor: the master's flagstone joints (measured column/row minima) at
# 313/626/940 px; the three interior flags that are not the darker one.
FLAGS = {'a': (626, 313, 940, 627), 'b': (313, 627, 626, 939), 'c': (626, 627, 940, 939)}
FLOOR_TARGET = 146.0            # levelled flag mean (Kor'Pul floor 131.8, cave 135)
FLOOR_CONTRAST = .72
FLOOR_BLUR = .5
# Wall top: one window per mask, darkened into a blocking mass.
WALL_WINDOW = 470
WALL_CONTRAST = .78
WALL_BRIGHTNESS = 1.08
RIM = (132, 138, 152)           # cool slate highlight catching upper-left light
# South face: a band of the wall-top master (two block courses) compressed
# into FACE_H px, darkened, under a lit coping lip.
FACE_H = 40
FACE_BAND = 300
FACE_BRIGHTNESS = .52
LIP = (150, 156, 170)
# Doors.
LEAF = (.04, .02, .96, .98)     # oak leaf inside its opaque box
EDGE = (.0, .02, .16, .98)      # the hinge stile: the open leaf seen edge-on
BAND = 46
POST = 16
OPEN_W = 20
DOOR_BRIGHTNESS = .96


def body(im):
    """Opaque bounding box (alpha >= 128): the soft generated halo is ignored."""
    return im.crop(im.getchannel('A').point(lambda a: 255 if a >= 128 else 0).getbbox())


def frac(im, box):
    w, h = im.size
    return im.crop((int(w * box[0]), int(h * box[1]), int(w * box[2]), int(h * box[3])))


def bright(im, factor):
    """Brightness of the colour channels only; alpha is kept."""
    rgb = ImageEnhance.Brightness(im.convert('RGB')).enhance(factor)
    if im.mode == 'RGBA':
        rgb.putalpha(im.getchannel('A'))
    return rgb


def lum(im, box=None):
    return ImageStat.Stat((im.crop(box) if box else im).convert('L')).mean[0]


def floor_tile(master, v):
    t = master.crop(FLAGS[v]).resize((SIZE, SIZE), Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(FLOOR_BLUR))
    t = ImageEnhance.Contrast(t).enhance(FLOOR_CONTRAST)
    return ImageEnhance.Brightness(t).enhance(FLOOR_TARGET / lum(t))


def top_cell(top, mask):
    w, h = top.size
    sx = (mask * 211) % (w - WALL_WINDOW)
    sy = (mask * 137) % (h - WALL_WINDOW)
    cell = top.crop((sx, sy, sx + WALL_WINDOW, sy + WALL_WINDOW)).resize((SIZE, SIZE), Image.Resampling.LANCZOS)
    cell = ImageEnhance.Contrast(cell).enhance(WALL_CONTRAST)
    return ImageEnhance.Brightness(cell).enhance(WALL_BRIGHTNESS)


def face_band(top, mask):
    w, h = top.size
    sx = (mask * 211) % (w - WALL_WINDOW)
    sy = (mask * 137) % (h - WALL_WINDOW)
    band = top.crop((sx, sy + WALL_WINDOW // 3, sx + WALL_WINDOW, sy + WALL_WINDOW // 3 + FACE_BAND))
    face = band.resize((SIZE, FACE_H), Image.Resampling.LANCZOS)
    face = ImageEnhance.Brightness(ImageEnhance.Contrast(face).enhance(.85)).enhance(FACE_BRIGHTNESS).convert('RGBA')
    lip = Image.new('RGBA', (SIZE, 3), LIP + (255,))
    face.paste(Image.blend(face.crop((0, 0, SIZE, 3)), lip, .55), (0, 0))
    return face


def wall_tile(top, mask):
    tile = top_cell(top, mask).convert('RGBA')
    if not mask & 1:
        rim = Image.new('RGBA', (SIZE, 4), RIM + (255,))
        tile.paste(Image.blend(tile.crop((0, 0, SIZE, 4)), rim, .5), (0, 0))
    if not mask & 8:
        rim = Image.new('RGBA', (3, SIZE), RIM + (255,))
        tile.paste(Image.blend(tile.crop((0, 0, 3, SIZE)), rim, .32), (0, 0))
    if not mask & 2:
        strip = ImageEnhance.Brightness(tile.crop((110, 0, 122, SIZE))).enhance(.62)
        tile.paste(strip.resize((9, SIZE)), (119, 0))
    if not mask & 4:
        tile.paste(face_band(top, mask), (0, SIZE - FACE_H))
        shadow = Image.new('RGBA', (SIZE, 4), (10, 10, 14, 255))
        tile.paste(Image.blend(tile.crop((0, SIZE - FACE_H - 3, SIZE, SIZE - FACE_H + 1)), shadow, .55),
                   (0, SIZE - FACE_H - 3))
    return tile


def shadow_under(tile, box, strength=.45, blur=3):
    mask = Image.new('L', tile.size, 0)
    x0, y0, x1, y1 = box
    mask.paste(int(255 * strength), (x0 + 2, y0 + 3, x1 + 2, y1 + 3))
    mask = mask.filter(ImageFilter.GaussianBlur(blur))
    return Image.composite(Image.new('RGBA', tile.size, (16, 14, 20, 255)), tile, mask)


def door_tile(floor, top, leaf, edge, horizontal, opened):
    tile = floor.convert('RGBA')
    if horizontal:
        band = (0, (SIZE - BAND) // 2, SIZE, (SIZE + BAND) // 2)
        posts = [(0, band[1], POST, band[3]), (SIZE - POST, band[1], SIZE, band[3])]
        box = (POST, band[1] - 34, POST + OPEN_W, band[3] + 34) if opened else (POST, band[1], SIZE - POST, band[3])
        piece = edge if opened else leaf.rotate(90, expand=True)
    else:
        band = ((SIZE - BAND) // 2, 0, (SIZE + BAND) // 2, SIZE)
        posts = [(band[0], 0, band[2], POST), (band[0], SIZE - POST, band[2], SIZE)]
        box = (band[0] - 34, POST, band[2] + 34, POST + OPEN_W) if opened else (band[0], POST, band[2], SIZE - POST)
        piece = edge.rotate(90, expand=True) if opened else leaf
    bw, bh = box[2] - box[0], box[3] - box[1]
    face = bright(ImageOps.fit(piece, (bw, bh), method=Image.Resampling.LANCZOS), DOOR_BRIGHTNESS)
    tile = shadow_under(tile, box)
    tile.alpha_composite(face, box[:2])
    post_src = top_cell(top, 15)
    for p in posts:
        tile = shadow_under(tile, p, .5, 2)
        tile.paste(post_src.crop((0, 0, p[2] - p[0], p[3] - p[1])), p[:2])
    return tile


def exit_tile(floor, kind):
    piece = Image.open(KORPUL / f'stairs-{kind}.png').convert('RGBA').resize((SIZE, SIZE), Image.Resampling.LANCZOS)
    tile = floor.convert('RGBA')
    tile.alpha_composite(piece)
    return tile


def parity(tile, p):
    return ImageEnhance.Brightness(tile.convert('RGB')).enhance(PARITY) if p else tile.convert('RGB')


def main():
    floor_m = Image.open(MASTERS['gothic-floor']).convert('RGB')
    top = Image.open(MASTERS['gothic-wall-top']).convert('RGB')
    door_m = Image.open(MASTERS['gothic-door'])
    assert door_m.mode == 'RGBA', door_m.mode
    leaf = frac(body(door_m), LEAF)
    edge = frac(body(door_m), EDGE)
    floors = {v: floor_tile(floor_m, v) for v in FLAGS}
    out = HERE / 'exports/runtime'
    review = HERE / 'review'
    out.mkdir(parents=True, exist_ok=True)
    RUNTIME.mkdir(parents=True, exist_ok=True)
    files, lums = {}, {}
    for p in (0, 1):
        tiles = {f'floor-{v}{p}.png': parity(t, p) for v, t in floors.items()}
        for mask in range(16):
            tiles[f'wall-{mask}-{p}.png'] = parity(wall_tile(top, mask), p)
        for state in ('closed', 'open'):
            for orient in ('horizontal', 'vertical'):
                tiles[f'door-{state}-{orient}{p}.png'] = parity(
                    door_tile(floors['a'], top, leaf, edge, orient == 'horizontal', state == 'open'), p)
        for kind in ('up', 'down', 'world'):
            tiles[f'exit-{kind}{p}.png'] = parity(exit_tile(floors['a'], kind), p)
        for name, tile in tiles.items():
            path = out / name
            tile.save(path, optimize=True)
            shutil.copy2(path, RUNTIME / name)
            files[name] = hashlib.sha256(path.read_bytes()).hexdigest()
            lums[name] = round(lum(tile), 1)
            for size in (48, 64, 96):
                target = review / str(size) / name
                target.parent.mkdir(parents=True, exist_ok=True)
                tile.resize((size, size), Image.Resampling.LANCZOS).save(target)
    walls0 = [lums[f'wall-{m}-0.png'] for m in range(16)]
    floors0 = [lums[f'floor-{v}0.png'] for v in FLAGS]
    metrics = {
        'floor_parity0': floors0, 'wall_interior': lums['wall-15-0.png'], 'wall_parity0_range': [min(walls0), max(walls0)],
        'floor_minus_brightest_wall': round((min(floors0) - max(walls0)) / min(floors0), 4),
        'doors': {n: lums[n] for n in lums if n.startswith('door') and n.endswith('0.png')},
        'min_parity_gap': round(min((lums[n] - lums[n[:-5] + '1.png']) / lums[n] for n in lums if n.endswith('0.png')), 4),
        'reused': {'korpul_floor': round(lum(Image.open(KORPUL / 'floor-a-0-0.png')), 1),
                   'korpul_wall15': round(lum(Image.open(KORPUL / 'wall-15-0.png')), 1),
                   'korpul_dark_wall15': round(lum(Image.open(REFINED / 'korpul-dark/wall-15-0.png')), 1),
                   'burnt_floor': round(lum(Image.open(REFINED / 'burnt/floor0.png')), 1),
                   'burnt_tree': round(lum(Image.open(REFINED / 'burnt/tree0.png')), 1)},
    }
    masters = {n: hashlib.sha256(p.read_bytes()).hexdigest() for n, p in MASTERS.items()}
    reused = {f'korpul/stairs-{k}.png': hashlib.sha256((KORPUL / f'stairs-{k}.png').read_bytes()).hexdigest()
              for k in ('up', 'down', 'world')}
    (HERE / 'export-manifest.json').write_text(json.dumps({
        'count': len(files), 'files': files, 'masters': masters, 'reused_board_tiles': reused, 'luminance': lums,
        'metrics': metrics,
        'constants': {k: v for k, v in globals().items() if k.isupper() and isinstance(v, (int, float, tuple, dict))
                      and k not in ('MASTERS',)}}, indent=2, default=str) + '\n')
    contact(review)
    scenes(review)
    print(len(files), 'tiles', json.dumps(metrics))


def contact(review):
    names = ['floor-a0.png', 'floor-b0.png', 'floor-c1.png', 'wall-0-0.png', 'wall-15-0.png', 'wall-10-1.png', 'wall-5-0.png',
             'door-closed-horizontal0.png', 'door-open-horizontal1.png', 'door-closed-vertical1.png', 'door-open-vertical0.png',
             'exit-up0.png', 'exit-down1.png', 'exit-world0.png']
    for size in (48, 64, 96):
        sheet = Image.new('RGB', (len(names) * size, size), (36, 34, 39))
        for col, name in enumerate(names):
            sheet.paste(Image.open(review / str(size) / name).convert('RGB'), (col * size, 0))
        sheet.save(review / f'contact-{size}.png')
        ImageOps.grayscale(sheet).save(review / f'contact-{size}-gray.png')


# Review scenes drawn with the runtime tiles (picks as in CheckerTerrain.lua):
# a Vor hall with a horizontal and a vertical door and pillars; the outer
# gate yard (burnt ground and trees against the hall wall, the up exit on
# gothic floor and FLAT_DOWN4 as the burnt exit-down).
SCENES = {
    'hall': ["##########",
             "#....#...#",
             "#.o..|...#",
             "#....#.<.#",
             "##+###...#",
             ";;;;;#o..#",
             ";T;;;#...#",
             ";;;T;#####"],
    'yard': ["TTT;;;;;;;",
             ";;;;;;##+#",
             ">;T;;;#..#",
             ";;;;;;#..#",
             ";;T;;;#.w#",
             ";;;;;;#..#",
             "T;;;;;####",
             ";;;T;;;;;;"],
}


def scene_tile(plan, x, y):
    def at(dx, dy):
        ny, nx = y + dy, x + dx
        return plan[ny][nx] if 0 <= ny < len(plan) and 0 <= nx < len(plan[0]) else ''
    def mask():
        return sum(1 << i for i, (dx, dy) in enumerate(((0, -1), (1, 0), (0, 1), (-1, 0))) if at(dx, dy) in '#o+|')
    p = (x + y) % 2
    c = plan[y][x]
    v = 'abc'[(x * 17 + y * 7) % 3]
    if c in '#o': return RUNTIME / f'wall-{mask()}-{p}.png'
    if c == '.': return RUNTIME / f'floor-{v}{p}.png'
    if c == '+': return RUNTIME / f'door-closed-horizontal{p}.png'
    if c == '|': return RUNTIME / f'door-open-vertical{p}.png'
    if c == '<': return RUNTIME / f'exit-up{p}.png'
    if c == 'w': return RUNTIME / f'exit-world{p}.png'
    if c == ';': return REFINED / f'burnt/floor{p}.png'
    if c == 'T': return REFINED / f'burnt/tree{p}.png'
    if c == '>': return REFINED / f'burnt/exit-down{p}.png'


def scenes(review):
    for size in (48, 64):
        for name, plan in SCENES.items():
            im = Image.new('RGB', (len(plan[0]) * size, len(plan) * size))
            for y in range(len(plan)):
                for x in range(len(plan[0])):
                    t = Image.open(scene_tile(plan, x, y)).convert('RGB').resize((size, size), Image.Resampling.LANCZOS)
                    im.paste(t, (x * size, y * size))
            im.save(review / f'scene-{name}-{size}.png')
            ImageOps.grayscale(im).save(review / f'scene-{name}-{size}-gray.png')


if __name__ == '__main__':
    main()
