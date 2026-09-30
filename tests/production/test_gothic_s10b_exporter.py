"""S10b gothic family: recorded masters, complete tiles, parity, the board
value hierarchy (light flagstone floor, dark slate wall, doors between),
distinctness from the Kor'Pul brick and byte identity of the runtime files."""
import hashlib
import json
import unittest
from pathlib import Path
from PIL import Image, ImageStat

ROOT = Path(__file__).resolve().parents[2]
SUITE = ROOT / 'art/terrain-gothic-s10b'
RUNTIME = ROOT / 'data/gfx/refined/gothic'
REFINED = ROOT / 'data/gfx/refined'
HANDOFF = ROOT / 'art/production/handoffs/gothic-s10b-v1'
PACKS = ('gothic-floor', 'gothic-wall-top', 'gothic-door')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def lum(path):
    return ImageStat.Stat(Image.open(path).convert('L')).mean[0]


class GothicS10bExporterTests(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads((SUITE / 'export-manifest.json').read_text())
        self.out = SUITE / 'exports/runtime'

    def test_masters_are_the_recorded_generations(self):
        for pack in PACKS:
            with self.subTest(pack=pack):
                receipt = json.loads((HANDOFF / pack / 'receipts/attempt-1.json').read_text())
                master = ROOT / receipt['saved_output_path']
                self.assertEqual(master, SUITE / 'masters' / f'{pack}-v1.png')
                self.assertEqual(digest(master), receipt['sha256'])
                self.assertEqual(self.manifest['masters'][pack], receipt['sha256'])
                im = Image.open(master)
                self.assertEqual(im.size[0], im.size[1])
                self.assertEqual(im.mode, 'RGBA' if pack == 'gothic-door' else 'RGB')
                call = json.loads((HANDOFF / pack / 'imagegen-calls/call-1/call.json').read_text())
                self.assertEqual(call['codex_model'], 'gpt-6.1-sol')
                self.assertEqual(call['outcome'], 'recorded')
        # The wall-face pack spent both calls without a recorded master; the
        # exporter does not read any wall-face image.
        face = HANDOFF / 'gothic-wall-face'
        self.assertFalse((face / 'receipts').exists() and any((face / 'receipts').iterdir()))
        self.assertFalse((SUITE / 'masters/gothic-wall-face-v1.png').exists())
        self.assertNotIn('gothic-wall-face', self.manifest['masters'])

    def test_complete_tiles_and_bytes(self):
        expected = sorted([f'floor-{v}{p}.png' for v in 'abc' for p in (0, 1)] +
                          [f'wall-{m}-{p}.png' for m in range(16) for p in (0, 1)] +
                          [f'door-{s}-{o}{p}.png' for s in ('closed', 'open') for o in ('horizontal', 'vertical') for p in (0, 1)] +
                          [f'exit-{k}{p}.png' for k in ('up', 'down', 'world') for p in (0, 1)])
        self.assertEqual(self.manifest['count'], 52)
        self.assertEqual(sorted(self.manifest['files']), expected)
        self.assertEqual(sorted(p.name for p in RUNTIME.iterdir()), expected)
        for name, sha in self.manifest['files'].items():
            with self.subTest(name=name):
                self.assertEqual(digest(self.out / name), sha)
                self.assertEqual(digest(RUNTIME / name), sha)
                im = Image.open(RUNTIME / name)
                self.assertEqual((im.mode, im.size), ('RGB', (128, 128)))
        for name, sha in self.manifest['reused_board_tiles'].items():
            self.assertEqual(digest(REFINED / name), sha, name)

    def test_parity(self):
        names = [f'floor-{v}' for v in 'abc'] + [f'wall-{m}-' for m in range(16)] + \
            [f'door-{s}-{o}' for s in ('closed', 'open') for o in ('horizontal', 'vertical')] + \
            [f'exit-{k}' for k in ('up', 'down', 'world')]
        for name in names:
            a, b = lum(RUNTIME / f'{name}0.png'), lum(RUNTIME / f'{name}1.png')
            self.assertGreaterEqual((a - b) / a, .10, name)

    def test_value_hierarchy(self):
        for p in (0, 1):
            floors = [lum(RUNTIME / f'floor-{v}{p}.png') for v in 'abc']
            # Light walkable ground: the three flag variants share one value,
            # at least as light as the board stone floor.
            self.assertLess(max(floors) - min(floors), 1.5, p)
            self.assertGreaterEqual(min(floors), lum(REFINED / f'korpul/floor-a-0-{p}.png'), p)
            walls = [lum(RUNTIME / f'wall-{m}-{p}.png') for m in range(16)]
            for m, wall in enumerate(walls):
                # The blocker is far below the floor (>= 55%) yet not a black hole,
                # and below the burnt yard it borders (>= 20%).
                self.assertGreaterEqual((min(floors) - wall) / min(floors), .55, (m, p))
                self.assertGreaterEqual(wall, 30, (m, p))
                self.assertGreaterEqual((lum(REFINED / f'burnt/floor{p}.png') - wall) / lum(REFINED / f'burnt/floor{p}.png'), .20, (m, p))
            # Doors sit between wall and floor; a closed leaf covers more than an open one.
            for o in ('horizontal', 'vertical'):
                closed = lum(RUNTIME / f'door-closed-{o}{p}.png')
                opened = lum(RUNTIME / f'door-open-{o}{p}.png')
                self.assertGreater(closed, max(walls) * 1.5, (o, p))
                self.assertLess(closed, opened, (o, p))
                self.assertLess(opened, min(floors), (o, p))
            # An open south edge carries the darker face band.
            for m in range(16):
                face = ImageStat.Stat(Image.open(RUNTIME / f'wall-{m}-{p}.png').convert('L').crop((0, 96, 128, 128))).mean[0]
                top = ImageStat.Stat(Image.open(RUNTIME / f'wall-{m}-{p}.png').convert('L').crop((0, 24, 128, 72))).mean[0]
                if m & 4:
                    self.assertGreater(face, top * .8, (m, p))
                else:
                    self.assertLess(face, top * .8, (m, p))

    def test_distinct_from_korpul(self):
        # A cool slate wall, not the warm Kor'Pul brick (either set) recoloured:
        # far darker, and blue >= red where the brick leans warm.
        for m in (0, 5, 10, 15):
            g = Image.open(RUNTIME / f'wall-{m}-0.png').convert('RGB')
            r, _, b = ImageStat.Stat(g).mean
            self.assertGreaterEqual(b, r - 1, m)
            for ref in ('korpul', 'korpul-dark'):
                self.assertLess(lum(RUNTIME / f'wall-{m}-0.png'), lum(REFINED / f'{ref}/wall-{m}-0.png') * .65, (ref, m))
        r, _, b = ImageStat.Stat(Image.open(RUNTIME / 'floor-a0.png').convert('RGB')).mean
        kr, _, kb = ImageStat.Stat(Image.open(REFINED / 'korpul/floor-a-0-0.png').convert('RGB')).mean
        self.assertGreater(b - r, kb - kr + 5)


if __name__ == '__main__':
    unittest.main()
