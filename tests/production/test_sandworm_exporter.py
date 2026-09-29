"""Selected Sandworm tiles preserve parity and exact 16-way wall coverage."""
import hashlib
import json
import unittest
from pathlib import Path
from PIL import Image, ImageStat

ROOT=Path(__file__).resolve().parents[2]
SUITE=ROOT/'art/terrain-sandworm-v1'

class SandwormExporterTests(unittest.TestCase):
    def test_every_parity_pair_exceeds_ten_percent(self):
        directory=SUITE/'exports/runtime'
        light_files=list(directory.glob('*0.png'))
        self.assertEqual(len(light_files),20)
        for light_file in light_files:
            dark_file=light_file.with_name(light_file.name[:-5]+'1.png')
            with self.subTest(pair=light_file.name):
                light=ImageStat.Stat(Image.open(light_file).convert('L')).mean[0]
                dark=ImageStat.Stat(Image.open(dark_file).convert('L')).mean[0]
                self.assertGreaterEqual((light-dark)/light,.10)

    def test_manifest_and_runtime_bytes(self):
        manifest=json.loads((SUITE/'export-manifest.json').read_text())
        self.assertEqual(manifest['count'],40)
        for mask in range(16):
            for parity in (0,1):
                self.assertIn(f'wall-{mask}-{parity}.png',manifest['files'])
        for name,digest in manifest['files'].items():
            for folder in (SUITE/'exports/runtime',ROOT/'data/gfx/refined/sand'):
                self.assertEqual(hashlib.sha256((folder/name).read_bytes()).hexdigest(),digest)

    def test_wall_faces_only_on_exposed_edges_and_reads_apart_from_floor(self):
        directory=SUITE/'exports/runtime'
        def mean(name,box=None):
            image=Image.open(directory/name).convert('L')
            return ImageStat.Stat(image.crop(box) if box else image).mean[0]
        interior='wall-15-0.png'  # N/E/S/W are all wall neighbours
        south_exposed='wall-11-0.png'  # only the south neighbour is floor
        for parity in (0,1):
            with self.subTest(parity=parity):
                self.assertLessEqual(mean(f'wall-15-{parity}.png'),
                                     .82*mean(f'floor{parity}.png'))
        warm=Image.open(directory/interior).convert('RGB')
        red,green,blue=ImageStat.Stat(warm).mean
        self.assertGreater(red,green+18)
        self.assertGreater(green,blue+18)
        self.assertGreater(ImageStat.Stat(warm.convert('L')).stddev[0],3)
        self.assertAlmostEqual(mean(interior,(0,0,128,88)),
                               mean(interior,(0,94,128,128)),delta=5)
        self.assertEqual(Image.open(directory/interior).crop((0,0,128,80)).tobytes(),
                         Image.open(directory/south_exposed).crop((0,0,128,80)).tobytes())
        self.assertLess(mean(south_exposed,(0,94,128,128)),
                        .7*mean(interior,(0,94,128,128)))
