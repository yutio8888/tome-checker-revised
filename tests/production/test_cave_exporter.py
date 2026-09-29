"""Unremarkable Cave export: complete masks, parity and value separation."""
import hashlib
import json
import unittest
from pathlib import Path
from PIL import Image, ImageStat

ROOT=Path(__file__).resolve().parents[2]
SUITE=ROOT/'art/terrain-cave-v1'

class CaveExporterTests(unittest.TestCase):
    def test_parity_wall_gap_and_bytes(self):
        manifest=json.loads((SUITE/'export-manifest.json').read_text())
        self.assertEqual(manifest['count'],62)
        out=SUITE/'exports/runtime'
        for name,digest in manifest['files'].items():
            for folder in (out,ROOT/'data/gfx/refined/cave'):
                self.assertEqual(hashlib.sha256((folder/name).read_bytes()).hexdigest(),digest)
        native=ROOT.parents[1]/'modules/tome/data/gfx/shockbolt/terrain/cave'
        self.assertEqual(len(manifest['native_cutouts']),12)
        for name,digest in manifest['native_cutouts'].items():
            self.assertEqual(hashlib.sha256((native/name).read_bytes()).hexdigest(),digest)
        for mask in range(16):
            for parity in (0,1):
                self.assertIn(f'wall-{mask}-{parity}.png',manifest['files'])
        for index in range(1,10):
            for parity in (0,1):self.assertIn(f'floor-rock-{index}-{parity}.png',manifest['files'])
        for index in range(1,3):
            for parity in (0,1):self.assertIn(f'floor-mushroom-{index}-{parity}.png',manifest['files'])
        for name in manifest['files']:
            if not name.endswith('0.png'):continue
            light=ImageStat.Stat(Image.open(out/name).convert('L')).mean[0]
            dark=ImageStat.Stat(Image.open(out/(name[:-5]+'1.png')).convert('L')).mean[0]
            with self.subTest(name=name):self.assertGreaterEqual((light-dark)/light,.10)
        floor=ImageStat.Stat(Image.open(out/'floor0.png').convert('L')).mean[0]
        wall=ImageStat.Stat(Image.open(out/'wall-15-0.png').convert('L')).mean[0]
        self.assertGreaterEqual((floor-wall)/floor,.30)
        exposed=Image.open(out/'wall-11-0.png').convert('L')
        interior=Image.open(out/'wall-15-0.png').convert('L')
        self.assertLess(ImageStat.Stat(exposed.crop((8,94,120,128))).mean[0],
                        .85*ImageStat.Stat(interior.crop((8,94,120,128))).mean[0])

if __name__=='__main__':unittest.main()
