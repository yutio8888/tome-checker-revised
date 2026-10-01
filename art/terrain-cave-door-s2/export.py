#!/usr/bin/env python3
"""S2/T7: Keepsake cave doors as board tiles. 0 ImageGen: an existing-export
recolour/composite only.

Source tiles (all already shipped and reviewed):
  * refined/korpul/door-{closed,open}-{horizontal,vertical}-{10|5}-{p}.png --
    the Kor'Pul door with its jambs on floor-a (horizontal: walls W/E, mask 10;
    vertical: walls N/S, mask 5);
  * refined/korpul/floor-a-0-{p}.png -- the floor those doors were drawn on;
  * refined/cave/floor{p}.png and refined/cave/wall-15-{p}.png -- the cave
    family's floor and interior wall texture.

Method (deterministic, per pixel): every pixel where the Kor'Pul door tile
differs from its floor-a background is door content. Low-saturation content
(the grey stone jambs and their shading) is replaced by the cave wall texture
scaled by the source luminance, so the jambs read as cut rock; the saturated
content (the wooden leaf, iron fittings, its cast shadow) is kept unchanged.
Everything else is the cave floor tile. Output: 8 RGB 128px tiles
refined/cave/door-{closed,open}-{horizontal,vertical}{0,1}.png.
"""
from pathlib import Path
import hashlib, json
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
GFX = ROOT / 'data/gfx/refined'
HERE = Path(__file__).resolve().parent
FROZEN = ROOT / 'art/terrain-contrast-v1/frozen-inputs/korpul'
KINDS = (('closed-horizontal', 10), ('closed-vertical', 5), ('open-horizontal', 10), ('open-vertical', 5))
STONE_SATURATION = 0.18
WALL_GAIN = 1.35


def rgb(path):
    return np.asarray(Image.open(path).convert('RGB')).astype(float)


def tile(kind, mask, parity):
    # Frozen pre-2026-10-01 Kor'Pul door/floor pair (the live pair got a hue finish).
    door = rgb(FROZEN / f'door-{kind}-{mask}-{parity}.png')
    base = rgb(FROZEN / f'floor-a-0-{parity}.png')
    floor = rgb(GFX / f'cave/floor{parity}.png')
    wall = rgb(GFX / f'cave/wall-15-{parity}.png')
    content = np.abs(door - base).sum(2) > 0
    hi, lo = door.max(2), door.min(2)
    saturation = (hi - lo) / np.maximum(hi, 1)
    luminance = door.mean(2)
    stone = content & (saturation < STONE_SATURATION)
    wood = content & ~stone
    out = floor.copy()
    if stone.any():
        factor = luminance / max(luminance[stone].mean(), 1)
        out[stone] = np.clip(wall[stone] * WALL_GAIN * factor[stone][:, None], 0, 255)
    out[wood] = door[wood]
    return Image.fromarray(out.round().astype('uint8'), 'RGB'), int(stone.sum()), int(wood.sum())


def main():
    record = {'method': __doc__.strip().splitlines()[0], 'imagegen_calls': 0, 'files': []}
    for kind, mask in KINDS:
        for parity in (0, 1):
            im, stone, wood = tile(kind, mask, parity)
            dst = GFX / f'cave/door-{kind}{parity}.png'
            im.save(dst, optimize=True)
            record['files'].append({'file': str(dst.relative_to(ROOT)), 'source_door': f'korpul/door-{kind}-{mask}-{parity}.png',
                                    'stone_pixels': stone, 'wood_pixels': wood,
                                    'sha256': hashlib.sha256(dst.read_bytes()).hexdigest()})
    (HERE / 'export-manifest.json').write_text(json.dumps(record, indent=1) + '\n')
    print(len(record['files']), 'cave door tiles')


if __name__ == '__main__':
    main()
