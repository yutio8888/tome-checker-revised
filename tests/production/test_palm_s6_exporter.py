"""S6 Eruan palm and sand exits: the recorded master, complete tiles, byte
identity of runtime files, parity and the palm's value separation from the
beach sand it stands on."""
import hashlib
import json
import unittest
from pathlib import Path
from PIL import Image, ImageChops, ImageOps, ImageStat

ROOT = Path(__file__).resolve().parents[2]
SUITE = ROOT / 'art/terrain-palm-s6'
RUNTIME = ROOT / 'data/gfx/refined/eruan'
RECEIPT = ROOT / 'art/production/handoffs/palm-s6-v1/palm-tree/receipts/attempt-1.json'
EXPECTED = sorted(f'{k}{p}.png' for k in ('palm-a', 'palm-b', 'exit-up', 'exit-down', 'exit-world') for p in (0, 1))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def lum(path, box=None):
    im = Image.open(path).convert('L')
    return ImageStat.Stat(im.crop(box) if box else im).mean[0]


class PalmExporterTests(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads((SUITE / 'export-manifest.json').read_text())
        self.out = SUITE / 'exports/runtime'

    def test_master_is_the_recorded_generation(self):
        receipt = json.loads(RECEIPT.read_text())
        master = ROOT / receipt['saved_output_path']
        self.assertEqual(receipt['saved_output_path'], 'art/terrain-palm-s6/masters/palm-tree-v1.png')
        self.assertEqual(digest(master), receipt['sha256'])
        self.assertEqual(self.manifest['master']['sha256'], receipt['sha256'])
        im = Image.open(master)
        self.assertEqual(im.mode, 'RGBA')
        alpha = im.getchannel('A')
        self.assertEqual(alpha.getextrema(), (0, 255))
        w, h = im.size
        for corner in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)):
            self.assertEqual(alpha.getpixel(corner), 0)

    def test_complete_tiles_and_bytes(self):
        self.assertEqual(sorted(k.split('/', 1)[1] for k in self.manifest['files']), EXPECTED)
        for key, sha in self.manifest['files'].items():
            name = key.split('/', 1)[1]
            for folder in (self.out, RUNTIME):
                with self.subTest(folder=folder.name, name=name):
                    path = folder / name
                    self.assertEqual(digest(path), sha)
                    im = Image.open(path)
                    self.assertEqual(im.size, (128, 128))
                    self.assertEqual(im.mode, 'RGB')
        self.assertEqual(sorted(p.name for p in RUNTIME.glob('*.png')), EXPECTED)
        for rel, sha in self.manifest['sources'].items():
            with self.subTest(source=rel):
                self.assertEqual(digest(ROOT / rel), sha)

    def test_parity(self):
        for key in ('palm-a', 'palm-b', 'exit-up', 'exit-down', 'exit-world'):
            light, dark = lum(self.out / f'{key}0.png'), lum(self.out / f'{key}1.png')
            with self.subTest(key=key):
                self.assertGreaterEqual((light - dark) / light, .10)

    def test_palm_blocks_visibly_against_the_beach_sand(self):
        # A palm cell (whole tile and the lit-pixel centre crop) reads at least
        # 25% darker than the open beach sand of the same parity.
        for p in (0, 1):
            sand = lum(ROOT / f'data/gfx/refined/beach/sand{p}.png')
            for key in ('palm-a', 'palm-b'):
                with self.subTest(key=key, parity=p):
                    self.assertLessEqual(lum(self.out / f'{key}{p}.png'), sand * .75)
                    self.assertLessEqual(lum(self.out / f'{key}{p}.png', (38, 38, 90, 90)), sand * .75)

    def test_mirrored_variant(self):
        a = Image.open(self.out / 'palm-a0.png').convert('L')
        b = Image.open(self.out / 'palm-b0.png').convert('L')
        self.assertNotEqual(digest(self.out / 'palm-a0.png'), digest(self.out / 'palm-b0.png'))
        # The crown silhouette is the mirror image (the shaded sand is not).
        crown = (0, 0, 128, 70)
        diff = ImageStat.Stat(ImageChops.difference(ImageOps.mirror(a).crop(crown), b.crop(crown))).mean[0]
        self.assertLess(diff, 12)

    def test_exits_carry_distinct_glyphs_on_sand(self):
        sand = Image.open(ROOT / 'data/gfx/refined/beach/sand0.png').convert('L')
        glyphs = {}
        for kind in ('up', 'down', 'world'):
            im = Image.open(self.out / f'exit-{kind}0.png').convert('L')
            glyphs[kind] = im
            bright = sum(1 for v in im.point(lambda v: 255 if v > 200 else 0).get_flattened_data() if v)
            with self.subTest(kind=kind):
                self.assertGreater(bright, 150)
                self.assertGreater(ImageStat.Stat(ImageChops.difference(im, sand)).mean[0], 3)
        self.assertNotEqual(list(glyphs['up'].get_flattened_data()), list(glyphs['down'].get_flattened_data()))
        self.assertNotEqual(list(glyphs['up'].get_flattened_data()), list(glyphs['world'].get_flattened_data()))


if __name__ == '__main__':
    unittest.main()
