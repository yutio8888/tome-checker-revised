#!/usr/bin/env python3
"""Export the TW7 town masters into board road and crop-field tiles.

Two opaque masters -- pale stone slabs (town roads) and tilled furrows with
low seedlings (Zigur/Angolwen crop fields) -- become 2 checker parities each
of 128px RGB floor tiles, the same structure as the existing board road and
grass (no neighbour masks: both are plain walkable floors). Parity 1 =
x0.875. Deterministic: fixed crops, no noise.

* road<parity>: a fixed square window of the slab master (about two slabs
  across a cell), toned lighter than grass and the Kor'Pul plaza floor and far
  above every wall, contrast flattened so pieces stay readable.
* fields<parity>: a window exactly two furrow periods high, starting half a
  period above a seedling row, so vertically adjacent cells continue the row
  rhythm and every cell holds two low green rows on light tilled soil.

Writes exports/runtime, data/gfx/refined/town, review/ (48/64/96 contact
sheets, a 64px town scene and its grayscale) and export-manifest.json.
"""
from pathlib import Path
from PIL import Image, ImageEnhance, ImageOps, ImageStat
import hashlib, json, os, shutil

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
ROAD = HERE / 'masters/town-road-slab-v1.png'
FIELD = HERE / 'masters/town-crop-field-v1.png'
RUNTIME = ROOT / 'data/gfx/refined/town'
REFINED = ROOT / 'data/gfx/refined'
SIZE = 128
PARITY = .875
# Road: centred window, about two slabs across; lighter than grass (109) and
# the plaza floor (132), calmer joints.
ROAD_WINDOW = (380, 380, 880, 880)
ROAD_BRIGHTNESS = .86
ROAD_CONTRAST = .78
# Fields: furrow (seedling-row) period measured on the master: rows at
# y = 122, 330, 535, 750, 961, 1163 (green-minus-red row profile), period
# ~208.5 px. Window = 2 periods, top half a period above the first row.
FIELD_WINDOW = (300, 18, 717, 435)
FIELD_BRIGHTNESS = 1.02
FIELD_CONTRAST = .82


def tone(im, brightness, contrast):
    return ImageEnhance.Brightness(ImageEnhance.Contrast(im).enhance(contrast)).enhance(brightness)


def tile(master, box, brightness, contrast):
    cell = master.crop(box).resize((SIZE, SIZE), Image.Resampling.LANCZOS)
    return tone(cell, brightness, contrast)


def lum(im):
    return ImageStat.Stat(im.convert('L')).mean[0]


def dim(t):
    return ImageEnhance.Brightness(t).enhance(PARITY)


def main():
    road = Image.open(ROAD)
    field = Image.open(FIELD)
    for m in (road, field):
        assert m.mode == 'RGB' and m.size[0] == m.size[1], (m.mode, m.size)
    out = HERE / 'exports/runtime'
    review = HERE / 'review'
    out.mkdir(parents=True, exist_ok=True)
    RUNTIME.mkdir(parents=True, exist_ok=True)
    hashes, lums = {}, {}
    base = {'road': tile(road, ROAD_WINDOW, ROAD_BRIGHTNESS, ROAD_CONTRAST),
            'fields': tile(field, FIELD_WINDOW, FIELD_BRIGHTNESS, FIELD_CONTRAST)}
    for kind, t in base.items():
        for parity in (0, 1):
            name = f'{kind}{parity}.png'
            im = (dim(t) if parity else t).convert('RGB')
            im.save(out / name, optimize=True)
            shutil.copy2(out / name, RUNTIME / name)
            hashes[name] = hashlib.sha256((out / name).read_bytes()).hexdigest()
            lums[name] = round(lum(im), 3)
            for size in (48, 64, 96):
                target = review / str(size) / name
                target.parent.mkdir(parents=True, exist_ok=True)
                im.resize((size, size), Image.Resampling.LANCZOS).save(target)

    def ref(name):
        return Image.open(REFINED / name).convert('RGB')

    neighbours = {n: round(lum(ref(n)), 3) for n in (
        'grass0.png', 'grass1.png', 'road0.png', 'korpul/floor-a-0-0.png', 'korpul/floor-b-0-0.png',
        'korpul/hardwall-15-0.png', 'korpul/hardwall-5-0.png', 'gold-mountain/wall-15-0.png',
        'beach/sand0.png', 'tree-oak0.png', 'eruan/palm-a0.png', 'deep15-0-0.png')}
    metrics = {
        'road_vs_grass_parity0': round((lums['road0.png'] - neighbours['grass0.png']) / lums['road0.png'], 4),
        'road_vs_plaza_floor_parity0': round((lums['road0.png'] - neighbours['korpul/floor-a-0-0.png']) / lums['road0.png'], 4),
        'road_vs_hardwall_interior': round((lums['road0.png'] - neighbours['korpul/hardwall-15-0.png']) / lums['road0.png'], 4),
        'road_vs_gold_mountain': round((lums['road0.png'] - neighbours['gold-mountain/wall-15-0.png']) / lums['road0.png'], 4),
        'fields_vs_grass_parity0': round((lums['fields0.png'] - neighbours['grass0.png']) / lums['fields0.png'], 4),
        'fields_vs_tree': round((lums['fields0.png'] - neighbours['tree-oak0.png']) / lums['fields0.png'], 4),
        'min_parity_gap': round(min((lums[f'{k}0.png'] - lums[f'{k}1.png']) / lums[f'{k}0.png'] for k in base), 4),
    }
    (HERE / 'export-manifest.json').write_text(json.dumps({
        'count': len(hashes),
        'masters': {k: {'path': os.path.relpath(p, HERE), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
                    for k, p in (('road', ROAD), ('fields', FIELD))},
        'runtime_dir': os.path.relpath(RUNTIME, ROOT), 'files': hashes, 'luminance': lums,
        'neighbour_luminance': neighbours, 'metrics': metrics,
        'constants': {'ROAD_WINDOW': ROAD_WINDOW, 'ROAD_BRIGHTNESS': ROAD_BRIGHTNESS, 'ROAD_CONTRAST': ROAD_CONTRAST,
                      'FIELD_WINDOW': FIELD_WINDOW, 'FIELD_BRIGHTNESS': FIELD_BRIGHTNESS,
                      'FIELD_CONTRAST': FIELD_CONTRAST, 'PARITY': PARITY},
    }, indent=2) + '\n')
    names = sorted(hashes)
    for size in (48, 64, 96):
        sheet = Image.new('RGB', (len(names) * size, size), (30, 30, 30))
        for i, n in enumerate(names):
            sheet.paste(Image.open(review / str(size) / n), (i * size, 0))
        sheet.save(review / f'contact-{size}.png')
    # Town scene at 48 and 64 px: a stone house (Kor'Pul hardwall masks) with a
    # road in front, the plaza floor, grass, a crop plot beside the road, trees,
    # and a beach with the S6 palm on sand.
    plan = ['tt..##########..t',
            't...#########...t',
            '..______________.',
            '.._..PPPP..-----.',
            '.._..PPPP..-----.',
            't._......._-----.',
            '.._____________..',
            'ss.p..sssspsss..t']
    wall = {'#'}
    for size in (48, 64):
        scene = Image.new('RGB', (len(plan[0]) * size, len(plan) * size))
        for y, row in enumerate(plan):
            for x, c in enumerate(row):
                p = (x + y) % 2
                if c == '#':
                    m = sum(bit for dx, dy, bit in ((0, -1, 1), (1, 0, 2), (0, 1, 4), (-1, 0, 8))
                            if 0 <= y + dy < len(plan) and 0 <= x + dx < len(row) and plan[y + dy][x + dx] in wall)
                    im = ref(f'korpul/hardwall-{m}-{p}.png')
                elif c == '_':
                    im = Image.open(out / f'road{p}.png')
                elif c == '-':
                    im = Image.open(out / f'fields{p}.png')
                elif c == 'P':
                    im = ref(f'korpul/floor-a-0-{p}.png')
                elif c == 't':
                    im = ref(f'tree-oak{p}.png')
                elif c == 's':
                    im = ref(f'beach/sand{p}.png')
                elif c == 'p':
                    im = ref(f'eruan/palm-a{p}.png')
                else:
                    im = ref(f'grass{p}.png')
                scene.paste(im.convert('RGB').resize((size, size), Image.Resampling.LANCZOS), (x * size, y * size))
        scene.save(review / f'town-scene-{size}.png')
        ImageOps.grayscale(scene).save(review / f'town-scene-{size}-gray.png')
    print(len(hashes), 'tiles', json.dumps(lums), json.dumps(metrics))


if __name__ == '__main__':
    main()
