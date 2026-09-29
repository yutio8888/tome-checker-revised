#!/usr/bin/env python3
"""S4/T1: underwater air bubbles as board tiles. 0 ImageGen: an existing-art
composite only.

Sources (all already shipped):
  * refined/underwater/floor{p}.png -- the reviewed board underwater floor
    (art/terrain-underwater-v1, exported from its ImageGen floor master);
  * the native bubble cell terrain/underwater/subsea_floor_bubbles.png and its
    own floor terrain/underwater/subsea_floor_02.png (ToME shockbolt set).

Method (deterministic): the native bubble cell is its floor plus pure
brightening (no pixel is darker), so the per-pixel brightening is the bubble
layer. It is upscaled 2x to 128px and used as the alpha of a pale-aqua
highlight; the areas it encloses (bubble interiors) get a faint pale fill so
each bubble reads as a volume, and a 1px deep-teal rim under the rings keeps
them apart from the busy board floor at 48px. The result is composited on the
board floor of the same parity. Output: refined/underwater/bubble{0,1}.png.
"""
from pathlib import Path
import hashlib, json
import numpy as np
from PIL import Image, ImageFilter

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
GFX = ROOT / 'data/gfx/refined/underwater'
NATIVE = ROOT.parents[1] / 'modules/tome/data/gfx/shockbolt/terrain/underwater'
N = 128
RING = np.array([232, 250, 248], float)   # pale aqua highlight
RIM = np.array([10, 42, 52], float)       # deep teal shadow under rings
FILL_ALPHA = 0.20
RIM_ALPHA = 0.55


def dilate(m):
    return np.asarray(Image.fromarray((m * 255).astype('uint8'), 'L').filter(ImageFilter.MaxFilter(3))) > 0


def outside(solid):
    # Flood fill from the tile border through non-ring pixels (4-neighbour).
    reach = np.zeros_like(solid)
    reach[0, :] = reach[-1, :] = reach[:, 0] = reach[:, -1] = True
    reach &= ~solid
    while True:
        grown = reach.copy()
        grown[1:] |= reach[:-1]; grown[:-1] |= reach[1:]
        grown[:, 1:] |= reach[:, :-1]; grown[:, :-1] |= reach[:, 1:]
        grown &= ~solid
        if (grown == reach).all():
            return reach
        reach = grown


def layer():
    a = np.asarray(Image.open(NATIVE / 'subsea_floor_bubbles.png').convert('RGB')).astype(float)
    b = np.asarray(Image.open(NATIVE / 'subsea_floor_02.png').convert('RGB')).astype(float)
    d = np.clip((a - b).mean(2), 0, None)
    assert (a - b).mean(2).min() >= 0, 'native bubble cell is no longer pure brightening'
    d = Image.fromarray(np.clip(d / d.max() * 255, 0, 255).astype('uint8'), 'L').resize((N, N), Image.Resampling.LANCZOS)
    ring = np.asarray(d).astype(float) / 255
    ring = np.clip(ring * 1.6, 0, 1)
    solid = ring > 0.18
    inside = ~solid & ~outside(solid)
    rim = np.asarray(Image.fromarray((solid * 255).astype('uint8'), 'L').filter(ImageFilter.MaxFilter(3))).astype(float) / 255
    rim = np.roll(np.roll(rim, 1, 0), 1, 1) * (1 - ring)
    return ring, inside.astype(float), rim


def main():
    ring, inside, rim = layer()
    record = {'method': __doc__.strip().splitlines()[0], 'imagegen_calls': 0, 'files': []}
    for p in (0, 1):
        floor = np.asarray(Image.open(GFX / f'floor{p}.png').convert('RGB')).astype(float)
        out = floor * (1 - RIM_ALPHA * rim[..., None]) + RIM * (RIM_ALPHA * rim[..., None])
        out = out * (1 - FILL_ALPHA * inside[..., None]) + RING * (FILL_ALPHA * inside[..., None])
        out = out * (1 - ring[..., None]) + RING * ring[..., None]
        dst = GFX / f'bubble{p}.png'
        Image.fromarray(np.clip(out.round(), 0, 255).astype('uint8'), 'RGB').save(dst, optimize=True)
        record['files'].append({'file': str(dst.relative_to(ROOT)), 'base': f'refined/underwater/floor{p}.png',
                                'sha256': hashlib.sha256(dst.read_bytes()).hexdigest()})
    # Review contact: floor / bubble / floor1 / bubble1 / wall at 48, 64, 96px.
    names = ('floor0', 'bubble0', 'floor1', 'bubble1', 'wall-0-0')
    sheet = Image.new('RGB', (4 + len(names) * 100, 4 + 52 + 68 + 100), (30, 30, 30))
    y = 4
    for size in (48, 64, 96):
        for i, n in enumerate(names):
            sheet.paste(Image.open(GFX / f'{n}.png').convert('RGB').resize((size, size), Image.Resampling.LANCZOS), (4 + i * 100, y))
        y += size + 4
    (HERE / 'review').mkdir(exist_ok=True)
    sheet.save(HERE / 'review/contact-48-64-96.png', optimize=True)
    record['native_sources'] = {n: hashlib.sha256((NATIVE / n).read_bytes()).hexdigest()
                                for n in ('subsea_floor_bubbles.png', 'subsea_floor_02.png')}
    (HERE / 'export-manifest.json').write_text(json.dumps(record, indent=1) + '\n')
    print(len(record['files']), 'bubble tiles')


if __name__ == '__main__':
    main()
