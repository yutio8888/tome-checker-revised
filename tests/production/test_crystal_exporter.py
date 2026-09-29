"""Crystal suite parity, wall value separation, masks, and byte inventory."""
import hashlib
import json
import unittest
from pathlib import Path
from PIL import Image, ImageStat

ROOT=Path(__file__).resolve().parents[2]
SUITE=ROOT/'art/terrain-crystal-v1'

class CrystalExporterTests(unittest.TestCase):
    def test_parity_and_wall_gap(self):
        out=SUITE/'exports/runtime'
        for source in out.glob('*0.png'):
            other=source.with_name(source.name[:-5]+'1.png')
            light=ImageStat.Stat(Image.open(source).convert('L')).mean[0]
            dark=ImageStat.Stat(Image.open(other).convert('L')).mean[0]
            with self.subTest(source=source.name):
                self.assertGreaterEqual((light-dark)/light,.10)
        floor=ImageStat.Stat(Image.open(out/'floor0.png').convert('L')).mean[0]
        wall=ImageStat.Stat(Image.open(out/'wall-15-0.png').convert('L')).mean[0]
        self.assertLessEqual(wall,.82*floor)
        self.assertGreater(ImageStat.Stat(Image.open(out/'wall-15-0.png').convert('L')).stddev[0],3)
        floor_rgb=ImageStat.Stat(Image.open(out/'floor0.png').convert('RGB')).mean
        wall_rgb=ImageStat.Stat(Image.open(out/'wall-15-0.png').convert('RGB')).mean
        self.assertGreater((wall_rgb[2]-wall_rgb[0])-(floor_rgb[2]-floor_rgb[0]),20)

    def test_complete_masks_and_source_bytes(self):
        manifest=json.loads((SUITE/'export-manifest.json').read_text())
        self.assertEqual(manifest['count'],40)
        for mask in range(16):
            for parity in (0,1):self.assertIn(f'wall-{mask}-{parity}.png',manifest['files'])
        for name,digest in manifest['files'].items():
            for folder in (SUITE/'exports/runtime',ROOT/'data/gfx/refined/crystal'):
                self.assertEqual(hashlib.sha256((folder/name).read_bytes()).hexdigest(),digest)

    def test_face_only_on_exposed_south(self):
        out=SUITE/'exports/runtime'
        interior=Image.open(out/'wall-15-0.png')
        south=Image.open(out/'wall-11-0.png')
        self.assertNotEqual(interior.crop((10,10,118,80)).tobytes(),
                            south.crop((10,10,118,80)).tobytes())
        self.assertLess(ImageStat.Stat(south.crop((10,94,118,128)).convert('L')).mean[0],
                        .85*ImageStat.Stat(interior.crop((10,94,118,128)).convert('L')).mean[0])
