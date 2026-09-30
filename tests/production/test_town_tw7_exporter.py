"""TW7 town roads and crop fields: recorded masters, complete tiles, parity,
value relations against the town floors/walls and byte identity of runtime files."""
import hashlib
import json
import unittest
from pathlib import Path
from PIL import Image, ImageStat

ROOT = Path(__file__).resolve().parents[2]
SUITE = ROOT / 'art/terrain-town-tw7'
RUNTIME = ROOT / 'data/gfx/refined/town'
REFINED = ROOT / 'data/gfx/refined'
PACKS = {'road': 'town-road-slab', 'fields': 'town-crop-field'}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def lum(path):
    return ImageStat.Stat(Image.open(path).convert('L')).mean[0]


class TownTw7ExporterTests(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads((SUITE / 'export-manifest.json').read_text())
        self.out = SUITE / 'exports/runtime'

    def test_masters_are_the_recorded_generations(self):
        for key, pack in PACKS.items():
            with self.subTest(pack=pack):
                receipt = json.loads((ROOT / 'art/production/handoffs/town-tw7-v1' / pack / 'receipts/attempt-1.json').read_text())
                master = ROOT / receipt['saved_output_path']
                self.assertEqual(master.parent, SUITE / 'masters')
                self.assertEqual(digest(master), receipt['sha256'])
                self.assertEqual(self.manifest['masters'][key]['sha256'], receipt['sha256'])
                im = Image.open(master)
                self.assertEqual(im.mode, 'RGB')
                self.assertEqual(im.size[0], im.size[1])

    def test_complete_tiles_and_bytes(self):
        expected = sorted(f'{k}{p}.png' for k in PACKS for p in (0, 1))
        self.assertEqual(self.manifest['count'], 4)
        self.assertEqual(sorted(self.manifest['files']), expected)
        self.assertEqual(sorted(p.name for p in RUNTIME.iterdir()), expected)
        for name, sha in self.manifest['files'].items():
            with self.subTest(name=name):
                self.assertEqual(digest(self.out / name), sha)
                self.assertEqual(digest(RUNTIME / name), sha)
                im = Image.open(RUNTIME / name)
                self.assertEqual((im.mode, im.size), ('RGB', (128, 128)))

    def test_parity(self):
        for k in PACKS:
            a, b = lum(RUNTIME / f'{k}0.png'), lum(RUNTIME / f'{k}1.png')
            self.assertGreaterEqual((a - b) / a, .10, k)

    def test_road_is_light_ground_distinct_from_grass_plaza_and_walls(self):
        for p in (0, 1):
            road = lum(RUNTIME / f'road{p}.png')
            self.assertGreaterEqual((road - lum(REFINED / f'grass{p}.png')) / road, .20, p)
            self.assertGreaterEqual((road - lum(REFINED / f'korpul/floor-a-0-{p}.png')) / road, .10, p)
            self.assertGreaterEqual((road - lum(REFINED / f'korpul/hardwall-15-{p}.png')) / road, .25, p)
            self.assertGreaterEqual((road - lum(REFINED / f'gold-mountain/wall-15-{p}.png')) / road, .40, p)
        # Warm stone, not the green grass nor the old brown dirt road.
        r, g, b = ImageStat.Stat(Image.open(RUNTIME / 'road0.png').convert('RGB')).mean
        self.assertGreater(r, g)
        self.assertGreater(g, b)
        self.assertGreater(lum(RUNTIME / 'road0.png') - lum(REFINED / 'road0.png'), 25)

    def test_fields_read_as_ground_not_obstacle(self):
        for p in (0, 1):
            field, grass = lum(RUNTIME / f'fields{p}.png'), lum(REFINED / f'grass{p}.png')
            # As light as grass (walkable ground), lighter than trees, far above walls.
            self.assertLessEqual(abs(field - grass) / grass, .10, p)
            self.assertGreater(field, lum(REFINED / f'tree-oak{p}.png'), p)
        # Brown soil with green rows: redder than grass on average.
        fr, fg, _ = ImageStat.Stat(Image.open(RUNTIME / 'fields0.png').convert('RGB')).mean
        gr, gg, _ = ImageStat.Stat(Image.open(REFINED / 'grass0.png').convert('RGB')).mean
        self.assertGreater(fr - fg, gr - gg + 10)


if __name__ == '__main__':
    unittest.main()
