#!/usr/bin/env python3
"""Review sheets for the S12 hazard family (offline, runtime tiles only).

scene-<n>.png / -gray: a Vor Armoury-like stone room at n px per cell (Kor'Pul
floor and hard wall, a hazard-lava pool, a deep-water channel with its stone
kerb, the demo player token standing next to the lava); compare-<n>.png: the
hazard interior and edge beside the other board lava / water tiles (blocking
molten pit, harmless Daikara lava floor, Fearscape/Charred Scar lava wall,
Caldera poison water, forest deep water). Mask and variant choice exactly as
CheckerTerrain.lua (N=1 E=2 S=4 W=8, variant (x*17+y*7)%3, parity (x+y)%2).
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageOps

ROOT = Path(__file__).resolve().parents[2]
REF = ROOT / 'data/gfx/refined'
OUT = Path(__file__).resolve().parent / 'review'
PLAN = [
    '#############',
    '#....~~~....#',
    '#....~~~.LL.#',
    '#.....~.LLL.#',
    '#..#..~.LLLL#',
    '#..#.~~..LL.#',
    '#....~~.P...#',
    '#############',
]
DIRS = ((0, -1), (1, 0), (0, 1), (-1, 0))


def at(x, y):
    if 0 <= y < len(PLAN) and 0 <= x < len(PLAN[0]):
        return PLAN[y][x]
    return '#'


def mask(x, y, kinds):
    return sum(1 << i for i, (dx, dy) in enumerate(DIRS) if at(x + dx, y + dy) in kinds)


def tile(x, y):
    c, p = at(x, y), (x + y) % 2
    if c == '#':
        return REF / f'korpul/hardwall-{mask(x, y, "#")}-{p}.png'
    if c == 'L':
        return REF / f"hazard/lava-{'abc'[(x * 17 + y * 7) % 3]}-{mask(x, y, 'L')}-{p}.png"
    if c == '~':
        return REF / f'hazard/deep-{mask(x, y, "~")}-{p}.png'
    return REF / f"korpul/{'floor-b' if (x * 17 + y * 7) % 3 == 0 else 'floor-a'}-0-{p}.png"


def scene(n):
    w, h = len(PLAN[0]), len(PLAN)
    im = Image.new('RGBA', (w * n, h * n))
    for y in range(h):
        for x in range(w):
            with Image.open(tile(x, y)) as t:
                im.alpha_composite(t.convert('RGBA').resize((n, n), Image.Resampling.LANCZOS), (x * n, y * n))
            if at(x, y) == 'P':
                with Image.open(ROOT / 'data/gfx/hero.png') as hero:
                    im.alpha_composite(hero.convert('RGBA').resize((n, n), Image.Resampling.LANCZOS), (x * n, y * n))
    return im


def compare(n):
    names = [('hazard/lava-a-15-0', 'hazard interior'), ('hazard/lava-b-5-0', 'hazard edge E/W'),
             ('hazard/lava-c-0-0', 'hazard single'), ('burnt/lava-15-0', 'molten pit (blocks)'),
             ('burnt/lava-0-0', 'molten pit edge'), ('daikara/lava-floor0', 'harmless lava floor'),
             ('scorch/wall-15-0', 'lava wall'), ('caldera/poison-15-0', 'poison water'),
             ('deep15-0-0', 'forest deep'), ('hazard/deep-5-0', 'stone deep E/W'), ('korpul/floor-a-0-0', 'stone floor'),
             ('korpul/hardwall-15-0', 'hard wall')]
    im = Image.new('RGBA', (len(names) * (n + 4), n + 14), (24, 24, 24, 255))
    d = ImageDraw.Draw(im)
    for i, (name, label) in enumerate(names):
        with Image.open(REF / f'{name}.png') as t:
            im.alpha_composite(t.convert('RGBA').resize((n, n), Image.Resampling.LANCZOS), (i * (n + 4), 0))
        d.text((i * (n + 4), n + 1), label[:max(4, n // 6)], fill=(220, 220, 220, 255))
    return im


def main():
    OUT.mkdir(exist_ok=True)
    for n in (48, 64, 96):
        s = scene(n)
        s.save(OUT / f'scene-{n}.png')
        ImageOps.grayscale(s.convert('RGB')).save(OUT / f'scene-{n}-gray.png')
        c = compare(n)
        c.save(OUT / f'compare-{n}.png')
        ImageOps.grayscale(c.convert('RGB')).save(OUT / f'compare-{n}-gray.png')


if __name__ == '__main__':
    main()
