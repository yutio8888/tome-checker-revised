#!/usr/bin/env python3
"""Review sheets for the S17 dream family (offline, runtime tiles only).

scene-<n>.png / -gray: a Dreamscape-like plane at n px per cell (cloud
islands, a one-cell peninsula and a lone cloud cell over the dream void, the
demo player token and a monster token on the cloud); scene-64-tinted.png: the
same scene multiplied by the zone's color_shown {0.5, 1, 0.7} (the native
foreground then varies this tint over time); compare-<n>.png / -gray: cloud
interior / edges / single and the dream void beside other board floors and
voids (Point Zero space and platform, snow ground, grass, Kor'Pul floor,
hazard lava) and the native cloud puff. Mask and variant choice exactly as
CheckerTerrain.lua (N=1 E=2 S=4 W=8; cloud variant (x*17+y*7)%3, void
variant (x*17+y*7)%2, parity (x+y)%2).
"""
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw, ImageOps

ROOT = Path(__file__).resolve().parents[2]
REF = ROOT / 'data/gfx/refined'
OUT = Path(__file__).resolve().parent / 'review'
NATIVE_CLOUD = ROOT.parents[1] / 'modules/tome/data/gfx/shockbolt/terrain/clouds/cloud_normal_002.png'
PLAN = [
    '             ',
    ' ~~~~   ~~~  ',
    ' ~~~~~~ ~~~~ ',
    ' ~P~~~~~~~~  ',
    ' ~~~ ~~~~M~  ',
    '  ~~  ~~~~   ',
    '   ~   ~  ~  ',
    '             ',
]
DIRS = ((0, -1), (1, 0), (0, 1), (-1, 0))
TOKENS = {'P': ROOT / 'data/gfx/hero.png', 'M': ROOT / 'data/gfx/tokens/giant-white-mouse.png'}


def at(x, y):
    if 0 <= y < len(PLAN) and 0 <= x < len(PLAN[0]):
        return PLAN[y][x]
    return ' '


def mask(x, y):
    return sum(1 << i for i, (dx, dy) in enumerate(DIRS) if at(x + dx, y + dy) != ' ')


def tile(x, y):
    p = (x + y) % 2
    if at(x, y) == ' ':
        return REF / f"dream/void-{'ab'[(x * 17 + y * 7) % 2]}-{p}.png"
    return REF / f"dream/cloud-{'abc'[(x * 17 + y * 7) % 3]}-{mask(x, y)}-{p}.png"


def scene(n):
    w, h = len(PLAN[0]), len(PLAN)
    im = Image.new('RGBA', (w * n, h * n))
    for y in range(h):
        for x in range(w):
            with Image.open(tile(x, y)) as t:
                im.alpha_composite(t.convert('RGBA').resize((n, n), Image.Resampling.LANCZOS), (x * n, y * n))
            token = TOKENS.get(at(x, y))
            if token and token.exists():
                with Image.open(token) as tk:
                    im.alpha_composite(tk.convert('RGBA').resize((n, n), Image.Resampling.LANCZOS), (x * n, y * n))
    return im


def compare(n):
    names = [('dream/cloud-a-15-0', 'cloud interior'), ('dream/cloud-b-15-1', 'cloud parity 1'),
             ('dream/cloud-c-11-0', 'cloud rim S'), ('dream/cloud-a-5-0', 'cloud rim E/W'),
             ('dream/cloud-b-0-0', 'cloud single'), ('dream/void-a-0', 'dream void'), ('dream/void-b-1', 'void parity 1'),
             ('void/space0', 'PZ space'), ('void/floor0', 'PZ platform'), ('snow/snow-ground0', 'snow ground'),
             ('grass0', 'grass'), ('korpul/floor-a-0-0', 'stone floor'), ('hazard/lava-a-15-0', 'hazard lava')]
    im = Image.new('RGBA', ((len(names) + 1) * (n + 4), n + 14), (24, 24, 24, 255))
    d = ImageDraw.Draw(im)
    for i, (name, label) in enumerate(names):
        with Image.open(REF / f'{name}.png') as t:
            im.alpha_composite(t.convert('RGBA').resize((n, n), Image.Resampling.LANCZOS), (i * (n + 4), 0))
        d.text((i * (n + 4), n + 1), label[:max(4, n // 6)], fill=(220, 220, 220, 255))
    with Image.open(NATIVE_CLOUD) as t:
        im.alpha_composite(t.convert('RGBA').resize((n, n), Image.Resampling.LANCZOS), (len(names) * (n + 4), 0))
    d.text((len(names) * (n + 4), n + 1), 'native cloud'[:max(4, n // 6)], fill=(220, 220, 220, 255))
    return im


def main():
    OUT.mkdir(exist_ok=True)
    for n in (48, 64, 96):
        s = scene(n)
        s.save(OUT / f'scene-{n}.png')
        ImageOps.grayscale(s.convert('RGB')).save(OUT / f'scene-{n}-gray.png')
        if n == 64:
            tint = Image.new('RGB', s.size, (128, 255, 179))
            ImageChops.multiply(s.convert('RGB'), tint).save(OUT / 'scene-64-tinted.png')
        c = compare(n)
        c.save(OUT / f'compare-{n}.png')
        ImageOps.grayscale(c.convert('RGB')).save(OUT / f'compare-{n}-gray.png')


if __name__ == '__main__':
    main()
