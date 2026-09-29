"""TW6 Irkkk bamboo huts: selected masters, complete wall masks, floor and
door tiles, parity, value separation from the town's floors and byte
identity of runtime files."""
import hashlib
import json
import unittest
from pathlib import Path
from PIL import Image, ImageStat

ROOT = Path(__file__).resolve().parents[2]
SUITE = ROOT / 'art/terrain-bamboo-hut-v1'
RUNTIME = ROOT / 'data/gfx/refined/bamboo'
MASTERS = {'floor-bamboo-wall-top.png': 'top', 'prop-bamboo-hut-wall.png': 'wall',
           'floor-bamboo-hut-floor.png': 'floor', 'prop-bamboo-hut-door.png': 'door'}
DOORS = [f'door-{s}-{o}{p}.png' for s in ('closed', 'open') for o in ('horizontal', 'vertical') for p in (0, 1)]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def lum(path, box=None):
    im = Image.open(path).convert('L')
    return ImageStat.Stat(im.crop(box) if box else im).mean[0]


class BambooHutExporterTests(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads((SUITE / 'export-manifest.json').read_text())
        self.out = SUITE / 'exports/runtime'

    def test_selected_masters_are_the_recorded_generations(self):
        selected = json.loads((SUITE / 'selected-masters.json').read_text())
        self.assertEqual(sorted(selected), sorted(MASTERS))
        for name, key in MASTERS.items():
            entry = selected[name]
            with self.subTest(name=name):
                self.assertEqual(digest(SUITE / entry['selected']), entry['sha256'])
                self.assertEqual(digest(SUITE / entry['source']), entry['sha256'])
                self.assertEqual(self.manifest['masters'][key]['sha256'], entry['sha256'])
                receipt = json.loads((ROOT / entry['receipt']).read_text())
                self.assertEqual(receipt['sha256'], entry['sha256'])
                self.assertEqual(receipt['saved_output_path'], str((SUITE / entry['source']).relative_to(ROOT)))
                im = Image.open(SUITE / entry['selected'])
                if name.startswith('floor-'):
                    self.assertEqual(im.mode, 'RGB')
                else:
                    self.assertEqual(im.mode, 'RGBA')
                    alpha = im.getchannel('A')
                    self.assertEqual(alpha.getextrema(), (0, 255))
                    w, h = im.size
                    for corner in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)):
                        self.assertEqual(alpha.getpixel(corner), 0)

    def test_complete_tiles_and_bytes(self):
        expected = sorted([f'wall-{m}-{p}.png' for m in range(16) for p in (0, 1)] +
                          ['floor0.png', 'floor1.png'] + DOORS)
        self.assertEqual(self.manifest['count'], 42)
        self.assertEqual(sorted(self.manifest['files']), expected)
        for name, sha in self.manifest['files'].items():
            for folder in (self.out, RUNTIME):
                with self.subTest(folder=folder.name, name=name):
                    path = folder / name
                    self.assertEqual(digest(path), sha)
                    im = Image.open(path)
                    self.assertEqual(im.size, (128, 128))
                    self.assertEqual(im.mode, 'RGB')
        self.assertEqual(sorted(p.name for p in RUNTIME.glob('*.png')), expected)

    def test_parity(self):
        for name in [f'wall-{m}-0.png' for m in range(16)] + ['floor0.png'] + [d for d in DOORS if d.endswith('0.png')]:
            light, dark = lum(self.out / name), lum(self.out / (name[:-5] + '1.png'))
            with self.subTest(name=name):
                self.assertGreaterEqual((light - dark) / light, .10)

    def test_blocking_walls_clearly_darker_than_every_floor(self):
        # The floors a hut wall touches in Irkkk: board jungle grass (Caldera)
        # and the new hut floor. No bright-wall (V2) problem, in every mask.
        floors = [ROOT / 'data/gfx/refined/caldera/floor0.png', self.out / 'floor0.png']
        darkest_floor = min(lum(f) for f in floors)
        brightest_wall = max(lum(self.out / f'wall-{m}-0.png') for m in range(16))
        self.assertGreaterEqual((darkest_floor - brightest_wall) / darkest_floor, .30)
        # Parity-1 walls stay below parity-1 floors too.
        darkest_floor1 = min(lum(ROOT / 'data/gfx/refined/caldera/floor1.png'), lum(self.out / 'floor1.png'))
        self.assertGreaterEqual((darkest_floor1 - max(lum(self.out / f'wall-{m}-1.png') for m in range(16))) / darkest_floor1, .30)
        # The hut floor is the lightest ground in the hut and warm, not green.
        r, g, b = ImageStat.Stat(Image.open(self.out / 'floor0.png').convert('RGB')).mean
        self.assertGreater(r, g)
        self.assertGreater(g, b)
        self.assertGreater(lum(self.out / 'floor0.png'), lum(ROOT / 'data/gfx/refined/caldera/floor0.png'))

    def test_wall_structure(self):
        # An exposed south edge shows the bamboo culm face (a distinct band);
        # a wall joined to the south does not.
        box = (8, 90, 120, 128)
        open_s, closed_s = self.out / 'wall-10-0.png', self.out / 'wall-15-0.png'
        self.assertNotEqual(Image.open(open_s).crop(box).tobytes(), Image.open(closed_s).crop(box).tobytes())
        # Warm brown hut wall, not a grey mountain and not green foliage.
        r, g, b = ImageStat.Stat(Image.open(self.out / 'wall-15-0.png').convert('RGB')).mean
        self.assertGreater(r, g)
        self.assertGreater(g, b)
        for other in ('gold-mountain/wall-15-0.png', 'cave/wall-15-0.png', 'caldera/tree-a0.png'):
            theirs = Image.open(ROOT / 'data/gfx/refined' / other).convert('RGB')
            with self.subTest(other=other):
                self.assertNotEqual(Image.open(self.out / 'wall-15-0.png').convert('RGB').tobytes(), theirs.tobytes())

    def test_doors_read_between_wall_and_floor(self):
        # Doors are floor-based: much lighter than the walls; a closed door
        # covers more of its cell with the leaf than an open one.
        brightest_wall = max(lum(self.out / f'wall-{m}-0.png') for m in range(16))
        floor = Image.open(self.out / 'floor0.png').convert('RGB')
        for name in [d for d in DOORS if d.endswith('0.png')]:
            with self.subTest(name=name):
                self.assertGreater(lum(self.out / name), brightest_wall * 1.5)

        def changed(name):
            a, b = Image.open(self.out / name).convert('RGB'), floor
            return sum(1 for p, q in zip(a.getdata(), b.getdata()) if sum(abs(x - y) for x, y in zip(p, q)) > 30)

        for orient in ('horizontal', 'vertical'):
            with self.subTest(orient=orient):
                self.assertGreater(changed(f'door-closed-{orient}0.png'), changed(f'door-open-{orient}0.png'))


if __name__ == '__main__':
    unittest.main()
