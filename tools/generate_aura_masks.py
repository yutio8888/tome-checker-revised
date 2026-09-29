"""Generate the two shipped aura grid masks and an optional strong study."""
from pathlib import Path
import argparse
import struct
import zlib

ROOT = Path(__file__).resolve().parents[1]
SIZE = 128
COLORS = {'teal': (68, 238, 215), 'violet': (197, 133, 242),
          'crimson': (245, 104, 145)}
LEGACY_COLORS = {'teal': (79, 198, 183), 'violet': (151, 113, 190),
                 'crimson': (190, 93, 116)}


def chunk(name, data):
    return (struct.pack('>I', len(data)) + name + data +
            struct.pack('>I', zlib.crc32(name + data) & 0xffffffff))


def image(color, variant='b1'):
    rows = bytearray()
    for y in range(SIZE):
        rows.append(0)
        for x in range(SIZE):
            edge = min(x, y, SIZE - 1 - x, SIZE - 1 - y)
            # Four source pixels become a 2px border at 64px (1.5/3 at 48/96).
            # The clear outer margin keeps adjacent cells from merging visually.
            if variant == 'legacy':
                alpha = 35 if 7 <= edge < 10 else (8 if edge >= 10 else 0)
            else:
                strong = variant == 'b2'
                alpha = (255 if strong else 195) if 6 <= edge < 10 else (
                    (142 if strong else 88) if edge >= 10 else 0)
            rows.extend((*color, alpha))
    return (b'\x89PNG\r\n\x1a\n' +
            chunk(b'IHDR', struct.pack('>IIBBBBB', SIZE, SIZE, 8, 6, 0, 0, 0)) +
            chunk(b'IDAT', zlib.compress(rows, 9)) + chunk(b'IEND', b''))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--strong-out', type=Path,
                        help='write the unshipped strong study to a separate directory')
    args = parser.parse_args()
    out = ROOT / 'data/gfx'
    for name, color in COLORS.items():
        (out / f'aura-{name}-moderate.png').write_bytes(image(color))
        (out / f'aura-{name}-subtle.png').write_bytes(image(LEGACY_COLORS[name], 'legacy'))
        if args.strong_out:
            args.strong_out.mkdir(parents=True, exist_ok=True)
            (args.strong_out / f'aura-{name}-strong.png').write_bytes(image(color, 'b2'))
