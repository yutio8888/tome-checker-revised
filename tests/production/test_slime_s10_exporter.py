"""S10a slime family: recorded masters, complete tiles, parity, the board
value hierarchy (light floor, dark wall, creep between stone and wall) and byte
identity of the runtime files."""
import hashlib
import json
import unittest
from pathlib import Path
from PIL import Image, ImageStat

ROOT = Path(__file__).resolve().parents[2]
SUITE = ROOT / 'art/terrain-slime-s10'
RUNTIME = ROOT / 'data/gfx/refined/slime'
REFINED = ROOT / 'data/gfx/refined'
PACKS = ('slime-floor', 'slime-wall')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def lum(path):
    return ImageStat.Stat(Image.open(path).convert('L')).mean[0]


class SlimeS10ExporterTests(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads((SUITE / 'export-manifest.json').read_text())
        self.out = SUITE / 'exports/runtime'

    def test_masters_are_the_recorded_generations(self):
        for pack in PACKS:
            with self.subTest(pack=pack):
                receipt = json.loads((ROOT / 'art/production/handoffs/slime-s10-v1' / pack / 'receipts/attempt-1.json').read_text())
                master = ROOT / receipt['saved_output_path']
                self.assertEqual(master, SUITE / 'masters' / f'{pack}-v1.png')
                self.assertEqual(digest(master), receipt['sha256'])
                self.assertEqual(self.manifest['masters'][pack], receipt['sha256'])
                im = Image.open(master)
                self.assertEqual(im.size[0], im.size[1])
                call = json.loads((ROOT / 'art/production/handoffs/slime-s10-v1' / pack / 'imagegen-calls/call-1/call.json').read_text())
                self.assertEqual(call['codex_model'], 'gpt-6.1-sol')
                self.assertEqual(call['outcome'], 'recorded')

    def test_complete_tiles_and_bytes(self):
        expected = sorted([f'{k}{p}.png' for k in ('floor', 'stairs-up', 'stairs-down') for p in (0, 1)] +
                          [f'{k}-{m}-{p}.png' for k in ('wall', 'creep') for m in range(16) for p in (0, 1)])
        self.assertEqual(self.manifest['count'], 70)
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
        for name in ['floor', 'stairs-up', 'stairs-down'] + [f'wall-{m}-' for m in range(16)]:
            a, b = lum(RUNTIME / f'{name}0.png'), lum(RUNTIME / f'{name}1.png')
            self.assertGreaterEqual((a - b) / a, .10, name)

    def test_value_hierarchy(self):
        for p in (0, 1):
            floor = lum(RUNTIME / f'floor{p}.png')
            # Light walkable ground, like the board cave floor.
            self.assertGreaterEqual(floor, lum(REFINED / f'cave/floor{p}.png') * .9, p)
            for m in range(16):
                wall = lum(RUNTIME / f'wall-{m}-{p}.png')
                # The blocker is far below the floor (>= 55%) yet not a black hole.
                self.assertGreaterEqual((floor - wall) / floor, .55, (m, p))
                self.assertGreaterEqual(wall, 30, (m, p))
            # Open creep (all edges exposed) sits on the board stone floor;
            # full creep stays walkable-light, far above every wall.
            creep = lum(RUNTIME / f'creep-15-{p}.png')
            self.assertGreaterEqual((creep - lum(RUNTIME / f'wall-15-{p}.png')) / creep, .50, p)
            self.assertGreaterEqual((creep - lum(REFINED / f'gloom/plain/wall-15-{p}.png')) / creep, .35, p)
        # Green slime, not grey stone: the floor and wall lean green.
        for name in ('floor0.png', 'wall-15-0.png', 'creep-15-0.png'):
            r, g, b = ImageStat.Stat(Image.open(RUNTIME / name).convert('RGB')).mean
            self.assertGreater(g, r, name)
            self.assertGreater(g, b + 8, name)
        sr, sg, _ = ImageStat.Stat(Image.open(REFINED / 'korpul/floor-a-0-0.png').convert('RGB')).mean
        cr, cg, _ = ImageStat.Stat(Image.open(RUNTIME / 'creep-15-0.png').convert('RGB')).mean
        self.assertGreater(cg - cr, sg - sr + 5)


if __name__ == '__main__':
    unittest.main()
