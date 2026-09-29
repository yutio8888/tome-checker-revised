"""TW5 Sunwall golden-mountain walls: selected master, complete masks, parity,
value separation from the town's floors and byte identity of runtime files."""
import hashlib
import json
import unittest
from pathlib import Path
from PIL import Image, ImageStat

ROOT = Path(__file__).resolve().parents[2]
SUITE = ROOT / 'art/terrain-gold-mountain-v1'
RUNTIME = ROOT / 'data/gfx/refined/gold-mountain'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def lum(path, box=None):
    im = Image.open(path).convert('L')
    return ImageStat.Stat(im.crop(box) if box else im).mean[0]


class GoldMountainExporterTests(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads((SUITE / 'export-manifest.json').read_text())

    def test_selected_masters_are_the_recorded_generations(self):
        selected = json.loads((SUITE / 'selected-masters.json').read_text())
        self.assertEqual(sorted(selected), ['floor-gold-crest.png', 'prop-gold-mountain.png'])
        for name, key in (('prop-gold-mountain.png', 'master'), ('floor-gold-crest.png', 'crest')):
            entry = selected[name]
            with self.subTest(name=name):
                self.assertEqual(digest(SUITE / entry['selected']), entry['sha256'])
                self.assertEqual(digest(SUITE / entry['source']), entry['sha256'])
                self.assertEqual(self.manifest[key]['sha256'], entry['sha256'])
                receipt = json.loads((ROOT / entry['receipt']).read_text())
                self.assertEqual(receipt['sha256'], entry['sha256'])
                self.assertEqual(receipt['saved_output_path'], str((SUITE / entry['source']).relative_to(ROOT)))
        crest = Image.open(SUITE / selected['floor-gold-crest.png']['selected'])
        self.assertEqual(crest.mode, 'RGB')
        master = SUITE / selected['prop-gold-mountain.png']['selected']
        im = Image.open(master)
        self.assertEqual(im.mode, 'RGBA')
        alpha = im.getchannel('A')
        self.assertEqual(alpha.getextrema(), (0, 255))
        w, h = im.size
        for corner in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)):
            self.assertEqual(alpha.getpixel(corner), 0)

    def test_complete_masks_and_bytes(self):
        self.assertEqual(self.manifest['count'], 32)
        self.assertEqual(sorted(self.manifest['files']),
                         sorted(f'wall-{m}-{p}.png' for m in range(16) for p in (0, 1)))
        for name, sha in self.manifest['files'].items():
            for folder in (SUITE / 'exports/runtime', RUNTIME):
                with self.subTest(folder=folder.name, name=name):
                    path = folder / name
                    self.assertEqual(digest(path), sha)
                    im = Image.open(path)
                    self.assertEqual(im.size, (128, 128))
                    self.assertEqual(im.mode, 'RGB')
        self.assertEqual(sorted(p.name for p in RUNTIME.glob('*.png')), sorted(self.manifest['files']))

    def test_parity_and_value_separation(self):
        out = SUITE / 'exports/runtime'
        for mask in range(16):
            light, dark = lum(out / f'wall-{mask}-0.png'), lum(out / f'wall-{mask}-1.png')
            with self.subTest(mask=mask):
                self.assertGreaterEqual((light - dark) / light, .10)
        # Blocking mass clearly darker than every board floor it touches in
        # Gates of Morning (no bright-wall V2 problem), in every mask.
        floors = [ROOT / 'data/gfx/refined' / n for n in ('korpul/floor-a-0-0.png', 'grass0.png', 'beach/sand0.png', 'road0.png')]
        darkest_floor = min(lum(f) for f in floors)
        brightest_wall = max(lum(out / f'wall-{m}-0.png') for m in range(16))
        self.assertGreaterEqual((darkest_floor - brightest_wall) / darkest_floor, .30)
        # An exposed south edge shows a darker cliff face than the interior top.
        box = (8, 96, 120, 128)
        self.assertLess(lum(out / 'wall-11-0.png', box), .85 * lum(out / 'wall-15-0.png', box))
        # Warm Sunwall hue, not a grey mountain: red > green > blue on average.
        r, g, b = ImageStat.Stat(Image.open(out / 'wall-15-0.png').convert('RGB')).mean
        self.assertGreater(r, g)
        self.assertGreater(g, b * 1.2)

    def test_distinct_from_other_mountain_families(self):
        ours = Image.open(SUITE / 'exports/runtime/wall-15-0.png').convert('RGB')
        for other in ('daikara/mountain-wall-150.png', 'cave/wall-15-0.png', 'crystal/wall-15-0.png'):
            theirs = Image.open(ROOT / 'data/gfx/refined' / other).convert('RGB')
            with self.subTest(other=other):
                self.assertNotEqual(ours.tobytes(), theirs.tobytes())


if __name__ == '__main__':
    unittest.main()
