#!/usr/bin/env python3
"""Export the S10a slime masters into 128px board tiles.

Two opaque ImageGen masters (masters/slime-floor-v1.png, a pale slime-glazed
cave floor; masters/slime-wall-v1.png, the top of a congealed dark-green ooze
wall) become the board slime family, built the same way as the accepted cave
and golden-mountain families (art/terrain-cave-v1, art/terrain-gold-mountain-v1):

* floor<p>: one fixed window of the floor master, softened, lifted to the
  board floor value (the cave floor reads 135) with pebbles kept decorative;
* wall-<mask>-<p>: the whole cell is dark ooze (one fixed master window per
  mask), toned well below every floor; an open north edge gets a thin wet
  highlight rim, open east/west edges a shaded side, and an open south edge
  the only cliff: a darker compressed band of the same ooze with a contact
  shadow. Bit order N=1 E=2 S=4 W=8 (CheckerTerrain.lua dirs); a set bit means
  the neighbour is also slime wall;
* creep-<mask>-<p>: Grushnak's mushroom creep, the slime floor material laid
  over the board stone floor (refined/korpul/floor-a-0-<p>); an exposed side
  (bit clear) fades back to stone over about ten pixels, the gloom creep rule;
* stairs-up<p> / stairs-down<p>: the board's shared Kor'Pul stair pieces
  (refined/korpul/stairs-*.png, unchanged) on the slime floor.

Parity 1 is the same tile at 0.875 brightness. Deterministic: fixed crops, no
noise. Writes exports/runtime, data/gfx/refined/slime, review/ and
export-manifest.json.
"""
from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter, ImageOps, ImageStat
import hashlib, json, math, shutil

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
RUNTIME = ROOT / 'data/gfx/refined/slime'
KORPUL = ROOT / 'data/gfx/refined/korpul'
SIZE = 128
PARITY = .875
# Floor: a centred window about three pebble clusters across, softened.
FLOOR_WINDOW = 560
FLOOR_BLUR = .6
FLOOR_CONTRAST = .62
FLOOR_BRIGHTNESS = 1.02
FLOOR_COLOR = 1.35
# Channel balance: the generated floor leans khaki; pull it toward sage green.
FLOOR_HUE = (.88, 1.0, .92)
# Wall top: one window per mask, darkened into a blocking mass.
WALL_WINDOW = 470
WALL_BLUR = .7
WALL_CONTRAST = .70
WALL_BRIGHTNESS = 1.0
WALL_COLOR = .85
RIM = (150, 168, 84, 255)       # wet yellow-green highlight catching upper-left light
FACE_H = 36
FACE_BRIGHTNESS = .42
# Creep over stone: the slime material slightly darker and greener than the
# stone floor so the patch reads as a flat film, never as a pool.
CREEP_BRIGHTNESS = .93


def master(name):
    return Image.open(HERE / 'masters' / f'{name}-v1.png').convert('RGB')


def window(im, size, sx, sy):
    return im.crop((sx, sy, sx + size, sy + size)).resize((SIZE, SIZE), Image.Resampling.LANCZOS)


def floor_tile(im):
    w, h = im.size
    t = window(im, FLOOR_WINDOW, (w - FLOOR_WINDOW) // 2, (h - FLOOR_WINDOW) // 2)
    t = ImageEnhance.Contrast(t.filter(ImageFilter.GaussianBlur(FLOOR_BLUR))).enhance(FLOOR_CONTRAST)
    t = ImageEnhance.Color(t).enhance(FLOOR_COLOR)
    t = Image.merge('RGB', [c.point(lambda v, k=k: min(255, int(round(v * k)))) for c, k in zip(t.split(), FLOOR_HUE)])
    return ImageEnhance.Brightness(t).enhance(FLOOR_BRIGHTNESS)


def wall_tile(im, mask):
    w, h = im.size
    sx = (mask * 211) % (w - WALL_WINDOW)
    sy = (mask * 137) % (h - WALL_WINDOW)
    top = window(im, WALL_WINDOW, sx, sy)
    top = ImageEnhance.Contrast(top.filter(ImageFilter.GaussianBlur(WALL_BLUR))).enhance(WALL_CONTRAST)
    top = ImageEnhance.Color(top).enhance(WALL_COLOR)
    tile = ImageEnhance.Brightness(top).enhance(WALL_BRIGHTNESS)
    if not mask & 1:
        rim = Image.new('RGB', (SIZE, 5), RIM[:3])
        tile.paste(Image.blend(tile.crop((0, 0, SIZE, 5)), rim, .45), (0, 0))
    if not mask & 8:
        rim = Image.new('RGB', (3, SIZE), RIM[:3])
        tile.paste(Image.blend(tile.crop((0, 0, 3, SIZE)), rim, .28), (0, 0))
        strip = ImageEnhance.Brightness(tile.crop((6, 0, 17, SIZE))).enhance(.80)
        tile.paste(strip.resize((8, SIZE)), (3, 0))
    if not mask & 2:
        strip = ImageEnhance.Brightness(tile.crop((109, 0, 121, SIZE))).enhance(.68)
        tile.paste(strip.resize((9, SIZE)), (119, 0))
    if not mask & 4:
        # The south cliff: the same ooze compressed vertically (it hangs down
        # the face) and darker; a thin contact shadow where it meets the floor.
        band = im.crop((sx, sy + WALL_WINDOW // 3, sx + WALL_WINDOW, sy + WALL_WINDOW // 3 + WALL_WINDOW // 2))
        face = band.resize((SIZE, FACE_H), Image.Resampling.LANCZOS)
        face = ImageEnhance.Contrast(face).enhance(.8)
        face = ImageEnhance.Brightness(face).enhance(FACE_BRIGHTNESS)
        tile.paste(face, (0, SIZE - FACE_H))
        shadow = Image.new('RGB', (SIZE, 4), (14, 20, 10))
        tile.paste(Image.blend(tile.crop((0, SIZE - FACE_H - 3, SIZE, SIZE - FACE_H + 1)), shadow, .55), (0, SIZE - FACE_H - 3))
    return tile


def creep_mask(bits):
    """Gloom creep rule (art/terrain-gloom-v1/export.py): a connected
    neighbour removes that side's exposed fringe."""
    vals = []
    for y in range(SIZE):
        for x in range(SIZE):
            edges = (y, SIZE - 1 - x, SIZE - 1 - y, x)
            distance = min((d for i, d in enumerate(edges) if bits & (1 << i) == 0), default=SIZE)
            jitter = 2.5 * math.sin(x * .19 + y * .07) + 1.5 * math.sin(y * .31 - x * .13)
            vals.append(max(0, min(255, int((distance - 10 + jitter) * 36))))
    m = Image.new('L', (SIZE, SIZE))
    m.putdata(vals)
    return m.filter(ImageFilter.GaussianBlur(1.2))


def stairs_tile(floor, kind):
    piece = Image.open(KORPUL / f'{kind}.png').convert('RGBA').resize((SIZE, SIZE), Image.Resampling.LANCZOS)
    tile = floor.convert('RGBA')
    tile.alpha_composite(piece)
    return tile.convert('RGB')


def parity(tile, p):
    return ImageEnhance.Brightness(tile).enhance(PARITY) if p else tile


def lum(tile):
    return round(ImageStat.Stat(tile.convert('L')).mean[0], 1)


def main():
    floor_m, wall_m = master('slime-floor'), master('slime-wall')
    floor = floor_tile(floor_m)
    creep = ImageEnhance.Brightness(floor).enhance(CREEP_BRIGHTNESS)
    out = HERE / 'exports/runtime'
    review = HERE / 'review'
    out.mkdir(parents=True, exist_ok=True)
    RUNTIME.mkdir(parents=True, exist_ok=True)
    files, lums = {}, {}
    for p in (0, 1):
        stone = Image.open(KORPUL / f'floor-a-0-{p}.png').convert('RGB')
        tiles = {f'floor{p}.png': parity(floor, p),
                 f'stairs-up{p}.png': parity(stairs_tile(floor, 'stairs-up'), p),
                 f'stairs-down{p}.png': parity(stairs_tile(floor, 'stairs-down'), p)}
        for mask in range(16):
            tiles[f'wall-{mask}-{p}.png'] = parity(wall_tile(wall_m, mask), p)
            # The stone base already carries its own parity.
            tiles[f'creep-{mask}-{p}.png'] = Image.composite(parity(creep, p), stone, creep_mask(mask))
        for name, tile in tiles.items():
            tile = tile.convert('RGB')
            path = out / name
            tile.save(path, optimize=True)
            shutil.copy2(path, RUNTIME / name)
            files[name] = hashlib.sha256(path.read_bytes()).hexdigest()
            lums[name] = lum(tile)
            for size in (48, 64, 96):
                target = review / str(size) / name
                target.parent.mkdir(parents=True, exist_ok=True)
                tile.resize((size, size), Image.Resampling.LANCZOS).save(target)
    masters = {n: hashlib.sha256((HERE / 'masters' / f'{n}-v1.png').read_bytes()).hexdigest() for n in ('slime-floor', 'slime-wall')}
    reused = {f'korpul/{n}': hashlib.sha256((KORPUL / n).read_bytes()).hexdigest()
              for n in ('floor-a-0-0.png', 'floor-a-0-1.png', 'stairs-up.png', 'stairs-down.png')}
    (HERE / 'export-manifest.json').write_text(json.dumps({
        'count': len(files), 'files': files, 'masters': masters, 'reused_board_tiles': reused, 'luminance': lums,
        'constants': {k: v for k, v in globals().items() if k.isupper() and isinstance(v, (int, float, tuple))}},
        indent=2) + '\n')
    contact(review)
    scenes(review)
    print(len(files), 'tiles; floor', lums['floor0.png'], 'wall-15', lums['wall-15-0.png'], 'wall-0', lums['wall-0-0.png'],
          'creep-15', lums['creep-15-0.png'])


def contact(review):
    names = ['floor0.png', 'floor1.png', 'wall-0-0.png', 'wall-15-0.png', 'wall-5-1.png', 'creep-15-0.png', 'creep-0-0.png',
             'stairs-up0.png', 'stairs-down0.png']
    for size in (48, 64, 96):
        sheet = Image.new('RGB', (len(names) * size, size), (36, 34, 39))
        for col, name in enumerate(names):
            sheet.paste(Image.open(review / str(size) / name).convert('RGB'), (col * size, 0))
        sheet.save(review / f'contact-{size}.png')
        ImageOps.grayscale(sheet).save(review / f'contact-{size}-gray.png')


# Review scenes: the three S10a situations drawn with the runtime tiles (the
# board picks come from CheckerTerrain.lua): a slime tunnel; Grushnak's slime
# pit (creep over board stone floor, mushroom thicket = gloom plain walls,
# S8 dark brick); Sludgenest L1 (caldera jungle beside slime floor and wall).
SCENES = {
    'tunnel': ["##########",
               "##....####",
               "#...>..###",
               "#.......##",
               "##..##...#",
               "###.##<..#",
               "#.......##",
               "##########"],
    'grushnak': ["BBBBBBBBBB",
                 "B,,,,BTTTT",
                 "B,,,,,;;TT",
                 "B,,,,;;;;T",
                 "BB+BB;;>;T",
                 "B,,,B;;;TT",
                 "B,,,,;;TTT",
                 "BBBBBTTTTT"],
    'sludge': ["jjjjjjjjjj",
               "jgggjjjggj",
               "jgg...ggjj",
               "gg..##..gj",
               "g..####.gg",
               "gg..##..gj",
               "jgg....ggj",
               "jjjggggjjj"],
}


def scene_tile(kind, plan, x, y):
    def same(dx, dy, group):
        ny, nx = y + dy, x + dx
        return 0 <= ny < len(plan) and 0 <= nx < len(plan[0]) and plan[ny][nx] in group
    def mask(group):
        return sum(1 << i for i, (dx, dy) in enumerate(((0, -1), (1, 0), (0, 1), (-1, 0))) if same(dx, dy, group))
    p = (x + y) % 2
    c = plan[y][x]
    refined = ROOT / 'data/gfx/refined'
    if c == '#': return RUNTIME / f'wall-{mask("#")}-{p}.png'
    if c == '.': return RUNTIME / f'floor{p}.png'
    if c == '>': return RUNTIME / f'stairs-down{p}.png'
    if c == '<': return RUNTIME / f'stairs-up{p}.png'
    if c == ';': return RUNTIME / f'creep-{mask(";>")}-{p}.png'
    if c == ',': return refined / f'korpul/floor-{"b" if (x * 17 + y * 7) % 3 == 0 else "a"}-0-{p}.png'
    if c == 'B': return refined / f'korpul-dark/wall-{mask("B+")}-{p}.png'
    if c == '+': return refined / f'korpul-dark/door-closed-horizontal-{mask("B")}-{p}.png'
    if c == 'T': return refined / f'gloom/plain/wall-{mask("T")}-{p}.png'
    if c == 'g': return refined / f'caldera/floor{p}.png'
    if c == 'j': return refined / f'caldera/tree-{"abc"[(x * 17 + y * 7) % 3]}{p}.png'


def scenes(review):
    for size in (48, 64):
        for name, plan in SCENES.items():
            im = Image.new('RGB', (len(plan[0]) * size, len(plan) * size))
            for y in range(len(plan)):
                for x in range(len(plan[0])):
                    t = Image.open(scene_tile(name, plan, x, y)).convert('RGB').resize((size, size), Image.Resampling.LANCZOS)
                    im.paste(t, (x * size, y * size))
            im.save(review / f'scene-{name}-{size}.png')
            ImageOps.grayscale(im).save(review / f'scene-{name}-{size}-gray.png')


if __name__ == '__main__':
    main()
