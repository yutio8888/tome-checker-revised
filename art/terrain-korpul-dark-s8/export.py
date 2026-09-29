#!/usr/bin/env python3
"""S8 (V2/V7) darker diggable-wall sets, derived deterministically. No ImageGen.

korpul-dark: the reviewed Kor'Pul brick is lighter than the Kor'Pul floor it
stands beside (board language: walkable floor light, blocking mass dark).
The two wall *material* masters (wall-top-v1, wall-v1) are recoloured to a
darker slate (per-channel scale, alpha kept) and the unmodified reviewed
assembler tools/export_korpul_terrain.c renders them with the original floor,
hard-wall and door-leaf masters. So the wall tiles and the door jambs get the
new stone, while every mask, edge strip, jamb rectangle, leaf, floor and
parity step is the reviewed geometry. The run first proves the assembler
still reproduces the shipped korpul/ set byte for byte, and that the new
render differs from it only inside wall cells and door-jamb rectangles.

scorch-dark: the Fearscape (demon plane) walks on the dark cracked lava
floor, where the batch 5 ash rock is lighter than the floor. The scorch wall
tiles are recoloured per pixel to a dark basalt (same masks and faces).

Outputs data/gfx/refined/{korpul-dark,scorch-dark}/, their runtime manifests,
export-manifest.json and review sheets under review/.
"""
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw, ImageOps, ImageStat
import hashlib, json, shutil, subprocess, tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
GFX = ROOT / 'data/gfx/refined'
MASTERS = ROOT / 'art/terrain-korpul-v1/masters'
ASSEMBLER = ROOT / 'tools/export_korpul_terrain.c'
# Darker cool slate for the brick material; the blue channel is kept a little
# higher so the warm sandstone becomes a neutral grey-slate that sits with the
# grey HARDWALL slabs instead of turning muddy brown.
KORPUL_SCALE = (0.58, 0.60, 0.66)
# Fearscape basalt: dark enough to sit below the lava floor's lit value.
SCORCH_SCALE = (0.42, 0.40, 0.39)
WALL_KINDS = ('wall', 'door-closed-horizontal', 'door-closed-vertical', 'door-open-horizontal', 'door-open-vertical')
# Door-jamb rectangles of the assembler (render(), kind>=4), per orientation,
# as the maximal boxes the jambs can cover (edge strips included).
JAMBS = {'horizontal': ((0, 84, 20, 124), (108, 84, 128, 124)),
         'vertical': ((4, 0, 44, 20), (4, 108, 44, 128))}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def scale(im, f):
    im = im.convert('RGBA')
    r, g, b, a = im.split()
    return Image.merge('RGBA', (r.point(lambda v: round(v * f[0])), g.point(lambda v: round(v * f[1])),
                                b.point(lambda v: round(v * f[2])), a))


def lum(path, size=64):
    return ImageStat.Stat(Image.open(path).convert('L').resize((size, size), Image.Resampling.LANCZOS)).mean[0]


def build():
    work = Path(tempfile.mkdtemp(prefix='s8-korpul-dark-'))
    try:
        binary = work / 'export_korpul_terrain'
        subprocess.run(['cc', '-O2', str(ASSEMBLER), '-o', str(binary), '-lpng', '-lm'], check=True)
        # 1. The assembler still reproduces the shipped reviewed set exactly.
        subprocess.run([str(binary), str(MASTERS), str(work / 'ref'), str(work / 'ref-review')], check=True,
                       capture_output=True)
        shipped = sorted((GFX / 'korpul').glob('*.png'))
        rendered = [p for p in shipped if (work / 'ref' / p.name).is_file()]
        assert len(rendered) == 196, len(rendered)
        for p in rendered:
            assert sha(p) == sha(work / 'ref' / p.name), p.name
        # 2. Recoloured wall material masters, everything else untouched.
        masters = work / 'masters'
        shutil.copytree(MASTERS, masters)
        for name in ('wall-top-v1.png', 'wall-v1.png'):
            scale(Image.open(MASTERS / name), KORPUL_SCALE).save(masters / name)
        subprocess.run([str(binary), str(masters), str(work / 'dark'), str(work / 'dark-review')], check=True,
                       capture_output=True)
        # 3. Only wall cells and door-jamb rectangles change.
        for p in rendered:
            new = work / 'dark' / p.name
            kind = p.name.rsplit('-', 2)[0]
            if kind not in WALL_KINDS:
                assert sha(p) == sha(new), p.name
                continue
            if kind == 'wall':
                continue
            diff = ImageChops.difference(Image.open(p).convert('RGBA'), Image.open(new).convert('RGBA')).convert('L')
            allowed = Image.new('L', diff.size, 0)
            for box in JAMBS[kind.rsplit('-', 1)[1]]:
                ImageDraw.Draw(allowed).rectangle((box[0], box[1], box[2] - 1, box[3] - 1), fill=255)
            outside = ImageChops.multiply(diff.point(lambda v: 255 if v else 0), ImageOps.invert(allowed))
            assert outside.getbbox() is None, ('change outside the jambs', p.name)
        files = {}
        out = GFX / 'korpul-dark'
        if out.exists():
            shutil.rmtree(out)
        out.mkdir(parents=True)
        for p in sorted((work / 'dark').glob('*.png')):
            if p.name.rsplit('-', 2)[0] in WALL_KINDS:
                shutil.copyfile(p, out / p.name)
                files['korpul-dark/' + p.name] = sha(out / p.name)
        assert len(files) == 160, len(files)
    finally:
        shutil.rmtree(work, ignore_errors=True)
    # scorch-dark: per-pixel recolour of the batch 5 Fearscape rock.
    out = GFX / 'scorch-dark'
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    scorch = {}
    for mask in range(16):
        for p in (0, 1):
            name = f'wall-{mask}-{p}.png'
            scale(Image.open(GFX / 'scorch' / name), SCORCH_SCALE).convert('RGB').save(out / name, optimize=True)
            scorch['scorch-dark/' + name] = sha(out / name)
    return files, scorch


def manifest_lua(path, comment, revision, keys):
    path.write_text('-- Generated by art/terrain-korpul-dark-s8/export.py.\n-- ' + comment + '\n'
                    'return {\n ready=true,\n revision=\'' + revision + '-' +
                    hashlib.sha256(''.join(keys.values()).encode()).hexdigest()[:12] + '\',\n files={\n' +
                    ''.join(f"  ['checker-revised+refined/{k}']=true,\n" for k in keys) + ' },\n}\n')


def review(files, scorch):
    """Review sheets: the dark set beside the shipped set at 48/64/96 px, as
    dungeon rooms (floor, door, stairs, hard wall) and a town block (grass,
    road, shop wall), in colour and grayscale; and the Fearscape rock on lava."""
    dun = ['#########', '#FFFF#FF#', '#FFSF#FF#', '##D###D##', '#FFFFFFF#', '#FF#HHHF#', '#########']
    town = ['ggggggggg', 'g#####ggg', 'g#FFF#rrr', 'g##D##rgg', 'grrrrrrgg', 'gg#D#gggg', 'ggggggggg']
    lava = ['#########', '#LLLL##L#', '#LL#LLLL#', '#LLL##LL#', '#########']

    def tile(folder, lay, x, y):
        c = lay[y][x]

        def wallish(xx, yy):
            return 0 <= yy < len(lay) and 0 <= xx < len(lay[0]) and lay[yy][xx] in '#H'
        m = sum(b for (dx, dy), b in (((0, -1), 1), ((1, 0), 2), ((0, 1), 4), ((-1, 0), 8)) if wallish(x + dx, y + dy))
        p = (x + y) % 2
        if c == '#':
            return Image.open(GFX / folder / f'wall-{m}-{p}.png')
        if c == 'H':
            return Image.open(GFX / f'korpul/hardwall-{m}-{p}.png')
        if c == 'D':
            o = 'vertical' if m % 16 == 5 else 'horizontal'
            return Image.open(GFX / folder / f'door-closed-{o}-{m}-{p}.png')
        if c in 'FS':
            k = 'floor-b' if (x * 17 + y * 7) % 3 == 0 else 'floor-a'
            im = Image.open(GFX / f'korpul/{k}-0-{p}.png').convert('RGBA')
            if c == 'S':
                im.alpha_composite(Image.open(GFX / 'korpul/stairs-down.png').convert('RGBA').resize(im.size))
            return im
        if c == 'L':
            return Image.open(GFX / f'daikara/lava-floor{p}.png')
        return Image.open(GFX / f'{"grass" if c == "g" else "road"}{p}.png')

    def scene(folder, lay, t):
        im = Image.new('RGB', (len(lay[0]) * t, len(lay) * t))
        for y in range(len(lay)):
            for x in range(len(lay[0])):
                im.paste(tile(folder, lay, x, y).convert('RGB').resize((t, t), Image.Resampling.LANCZOS), (x * t, y * t))
        return im
    (HERE / 'review').mkdir(exist_ok=True)
    for t in (48, 64, 96):
        rows = []
        for folder, lays in (('korpul', (dun, town)), ('korpul-dark', (dun, town))):
            parts = [scene(folder, lay, t) for lay in lays]
            parts += [ImageOps.grayscale(p).convert('RGB') for p in parts]
            rows.append(parts)
        w = sum(p.width for p in rows[0]) + 10 * 3
        sheet = Image.new('RGB', (w, sum(r[0].height for r in rows) + 10), (255, 0, 255))
        y = 0
        for r in rows:
            x = 0
            for p in r:
                sheet.paste(p, (x, y))
                x += p.width + 10
            y += r[0].height + 10
        sheet.save(HERE / f'review/korpul-dark-{t}.png', optimize=True)
        a, b = scene('scorch', lava, t), scene('scorch-dark', lava, t)
        sheet = Image.new('RGB', (a.width * 4 + 30, a.height), (255, 0, 255))
        for i, p in enumerate((a, b, ImageOps.grayscale(a).convert('RGB'), ImageOps.grayscale(b).convert('RGB'))):
            sheet.paste(p, (i * (a.width + 10), 0))
        sheet.save(HERE / f'review/scorch-dark-{t}.png', optimize=True)


def main():
    files, scorch = build()
    manifest_lua(ROOT / 'data/terrain-korpul-dark-manifest.lua',
                 "S8 darker diggable-wall and door-jamb recolour of the reviewed Kor'Pul brick.", 'korpul-dark-s8', files)
    manifest_lua(ROOT / 'data/terrain-scorch-dark-manifest.lua',
                 'S8 Fearscape basalt recolour of the batch 5 scorch rock.', 'scorch-dark-s8', scorch)
    review(files, scorch)
    metrics = {}
    for p in (0, 1):
        metrics[f'korpul_floor_a_{p}'] = round(lum(GFX / f'korpul/floor-a-0-{p}.png'), 1)
        metrics[f'korpul_floor_b_{p}'] = round(lum(GFX / f'korpul/floor-b-0-{p}.png'), 1)
        metrics[f'korpul_hardwall_15_{p}'] = round(lum(GFX / f'korpul/hardwall-15-{p}.png'), 1)
        metrics[f'grass_{p}'] = round(lum(GFX / f'grass{p}.png'), 1)
        metrics[f'road_{p}'] = round(lum(GFX / f'road{p}.png'), 1)
        metrics[f'lava_floor_{p}'] = round(lum(GFX / f'daikara/lava-floor{p}.png'), 1)
    walls = {k: round(lum(GFX / k), 1) for k in files if k.split('/')[1].startswith('wall-')}
    metrics['korpul_dark_wall_min'] = min(walls.values())
    metrics['korpul_dark_wall_max'] = max(walls.values())
    metrics['korpul_wall_max_before'] = round(max(lum(GFX / f'korpul/wall-{m}-{p}.png') for m in range(16) for p in (0, 1)), 1)
    sw = [round(lum(GFX / k), 1) for k in scorch]
    metrics['scorch_dark_wall_min'], metrics['scorch_dark_wall_max'] = min(sw), max(sw)
    metrics['scorch_wall_max_before'] = round(max(lum(GFX / f'scorch/wall-{m}-{p}.png') for m in range(16) for p in (0, 1)), 1)
    sources = [MASTERS / n for n in ('wall-top-v1.png', 'wall-v1.png', 'hardwall-top-v1.png', 'hardwall-v1.png',
                                     'floor-a-v2.png', 'floor-b-v2.png', 'door-leaf-horizontal-v1.png',
                                     'door-leaf-vertical-v2.png')] + [ASSEMBLER]
    sources += [GFX / f'scorch/wall-{m}-{p}.png' for m in range(16) for p in (0, 1)]
    manifest = {'generator': 'art/terrain-korpul-dark-s8/export.py', 'imagegen_calls': 0,
                'korpul_scale': KORPUL_SCALE, 'scorch_scale': SCORCH_SCALE,
                'sources': {s.relative_to(ROOT).as_posix(): sha(s) for s in sources},
                'files': dict(files, **scorch), 'metrics_64px': metrics}
    (HERE / 'export-manifest.json').write_text(json.dumps(manifest, indent=1, sort_keys=True) + '\n')
    print(len(files), 'korpul-dark +', len(scorch), 'scorch-dark files;', json.dumps(metrics))


if __name__ == '__main__':
    main()
