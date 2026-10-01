#!/usr/bin/env python3
"""Kor'Pul / Kor'Pul-dark floor-vs-wall hue split; zero ImageGen, no runtime Lua.

The cross-family value gates pin both the floor and the wall *values*:
Gothic and lava must stay below the Kor'Pul / dark brick, the S8 dark brick
keeps 0.55-0.66 of the Kor'Pul brick and stays 18% under the floor and below
grass, the floor stays 30% above Conclave, under the TW7 road and the Gothic
floors.  So this finish keeps every pixel's luma (PIL "L") and moves only hue:

* floor-a / floor-b: warm sandstone (R/G/B gains FLOOR_GAINS, luma restored);
* Kor'Pul diggable brick (wall-*, door jambs): cool grey (WALL_GAINS);
* Kor'Pul-dark brick and jambs: byte-identical (already near-neutral);
* door tiles: pixels equal to the baseline floor get the floor finish, jamb
  pixels (where the baseline Kor'Pul and dark doors differ) the brick finish,
  leaf/fittings unchanged.  Dark doors therefore still differ from Kor'Pul
  doors only inside the jamb rectangles.
Hardwall and stairs are untouched.

Inputs are the byte-pinned baseline tiles in frozen-inputs/korpul{,-dark}.
Run after tools/export_korpul_terrain.c and art/terrain-korpul-dark-s8/export.py.
It then resynchronises their records and the derived families that composite
the live floor (slime creep edges, graveyard coffin/mausoleum road).
"""
from pathlib import Path
import hashlib, json, runpy, shutil
import numpy as np
from PIL import Image, ImageStat

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
GFX = ROOT / 'data/gfx/refined'
FROZEN = HERE / 'frozen-inputs'
FLOOR_GAINS = (1.08, .99, .82)
WALL_GAINS = (.93, 1.0, 1.14)
LUMA = np.array([.299, .587, .114])
DOORS = [f'door-{s}-{o}' for s in ('closed', 'open') for o in ('horizontal', 'vertical')]
spec = runpy.run_path(str(HERE / 'export.py'))
lab = spec['lab']


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def rgba(path):
    return np.asarray(Image.open(path).convert('RGBA')).astype(float)


def hue(rgb, gains):
    """Scale R/G/B, then restore each pixel's original luma."""
    y = rgb @ LUMA
    out = rgb * np.array(gains)
    out *= (y / np.maximum(out @ LUMA, 1e-6))[..., None]
    return out


def save(a, dst):
    a = np.clip(np.round(a), 0, 255).astype(np.uint8)
    Image.fromarray(a, 'RGBA').save(dst, optimize=True)


def finish(name):
    """Return {family: array} for one baseline tile name."""
    src = rgba(FROZEN / 'korpul' / name)
    if name.startswith('floor-'):
        out = src.copy(); out[..., :3] = hue(src[..., :3], FLOOR_GAINS)
        return {'korpul': out}
    if name.startswith('wall-'):
        out = src.copy(); out[..., :3] = hue(src[..., :3], WALL_GAINS)
        return {'korpul': out}
    p = name.rsplit('-', 1)[1][0]
    floor = rgba(FROZEN / 'korpul' / f'floor-a-0-{p}.png')
    dark = rgba(FROZEN / 'korpul-dark' / name)
    is_floor = (src == floor).all(-1)
    jamb = (src != dark).any(-1)
    assert not (is_floor & jamb).any(), name
    warm = hue(src[..., :3], FLOOR_GAINS)
    light, darkout = src.copy(), dark.copy()
    light[is_floor, :3] = warm[is_floor]
    darkout[is_floor, :3] = warm[is_floor]
    light[jamb, :3] = hue(src[..., :3], WALL_GAINS)[jamb]
    return {'korpul': light, 'korpul-dark': darkout}


def delta_e(a, b):
    return float(np.linalg.norm(lab(Image.open(a)) - lab(Image.open(b))))


def metrics(floor_dir, wall_dir, dark_dir):
    m = {}
    for p in (0, 1):
        f = floor_dir / f'floor-a-0-{p}.png'
        fl = lab(Image.open(f))
        for key, path in (('korpul', wall_dir / f'wall-15-{p}.png'), ('korpul-dark', dark_dir / f'wall-15-{p}.png'),
                          ('hardwall', GFX / f'korpul/hardwall-15-{p}.png'), ('maze', GFX / f'maze/old-wall-15-{p}.png')):
            wl = lab(Image.open(path))
            m[f'{key}-{p}'] = {'delta_e': round(float(np.linalg.norm(fl - wl)), 2),
                               'floor_lab': [round(float(v), 2) for v in fl], 'wall_lab': [round(float(v), 2) for v in wl]}
    return m


def sync_records(changed):
    # Original Kor'Pul assembly record and its 48/64/96 review downscales.
    mp = ROOT / 'art/terrain-korpul-v1/runtime-manifest.json'
    m = json.loads(mp.read_text())
    for entry in m['files']:
        p = ROOT / entry['file']
        if entry['file'] in changed:
            entry['sha256'] = sha(p); entry['bytes'] = p.stat().st_size
    mp.write_text(json.dumps(m, indent=2) + '\n')
    for rel in changed:
        fam, name = rel.split('/')[-2:]
        review = (ROOT / 'art/terrain-korpul-v1/review/runtime') if fam == 'korpul' else None
        if review:
            for size in (48, 64, 96):
                Image.open(ROOT / rel).resize((size, size), Image.Resampling.LANCZOS).save(review / str(size) / name)
    # S8 dark export record: the door tiles carry the new floor.
    sp = ROOT / 'art/terrain-korpul-dark-s8/export-manifest.json'
    s = json.loads(sp.read_text())
    for rel in changed:
        key = '/'.join(rel.split('/')[-2:])
        if key in s['files']:
            s['files'][key] = sha(ROOT / rel)
    sp.write_text(json.dumps(s, indent=2) + '\n')


def sheet(dest_prefix, floor_dir, wall_dir, dark_dir):
    """Before/after 10x8 boards (two rooms, a jambed door) at 48/64/96."""
    holes = {(4, 3), (5, 4)}
    def is_wall(x, y):
        return 2 <= x <= 7 and 2 <= y <= 5 and (x, y) not in holes
    for size in (48, 64, 96):
        out = Image.new('RGB', (20 * size + size, 8 * size))
        for col, wdir, fam in ((0, wall_dir, 'korpul'), (1, dark_dir, 'korpul-dark')):
            for y in range(8):
                for x in range(10):
                    p = (x + y) % 2
                    if is_wall(x, y):
                        mask = sum(b for dx, dy, b in ((0, -1, 1), (1, 0, 2), (0, 1, 4), (-1, 0, 8)) if is_wall(x + dx, y + dy))
                        path = wdir / f'wall-{mask}-{p}.png'
                    elif (x, y) == (8, 3):
                        path = (floor_dir if fam == 'korpul' else dark_dir) / f'door-closed-vertical-5-{p}.png'
                    else:
                        path = floor_dir / f'floor-{"b" if (x * 17 + y * 7) % 3 == 0 else "a"}-0-{p}.png'
                    out.paste(Image.open(path).convert('RGB').resize((size, size), Image.Resampling.LANCZOS),
                              (col * 11 * size + x * size, y * size))
        out.save(HERE / 'review' / f'{dest_prefix}-{size}.png')


def main():
    names = sorted(p.name for p in (FROZEN / 'korpul').glob('*.png'))
    assert len(names) == 4 + 32 + 128, len(names)
    changed, files = [], {}
    for name in names:
        for fam, arr in finish(name).items():
            dst = GFX / fam / name
            save(arr, dst)
            sel = HERE / 'exports' / fam / name
            sel.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(dst, sel)
            rel = str(dst.relative_to(ROOT)); changed.append(rel)
            files[rel] = {'before': sha(FROZEN / fam / name), 'after': sha(dst)}
    sync_records(changed)
    report = {
        'imagegen_calls': 0, 'floor_gains': FLOOR_GAINS, 'wall_gains': WALL_GAINS,
        'metrics_before': metrics(FROZEN / 'korpul', FROZEN / 'korpul', GFX / 'korpul-dark'),
        'metrics_after': metrics(GFX / 'korpul', GFX / 'korpul', GFX / 'korpul-dark'),
        'files': files}
    (HERE / 'korpul-manifest.json').write_text(json.dumps(report, indent=2) + '\n')
    (HERE / 'review').mkdir(exist_ok=True)
    sheet('korpul-before', FROZEN / 'korpul', FROZEN / 'korpul', FROZEN / 'korpul-dark')
    sheet('korpul-after', GFX / 'korpul', GFX / 'korpul', GFX / 'korpul-dark')
    # Families that composite the live floor next to live floor cells.
    for suite in ('terrain-slime-s10', 'terrain-graveyard-v1'):
        runpy.run_path(str(ROOT / 'art' / suite / 'export.py'), run_name='__main__')
    print(json.dumps({k: v['delta_e'] for k, v in report['metrics_after'].items()}, indent=1))


if __name__ == '__main__':
    main()
