"""Acceptance checks for the selected Heart of the Gloom runtime exports."""
import json
import unittest
from pathlib import Path

from PIL import Image, ImageStat


ROOT = Path(__file__).resolve().parents[2]
SUITE = ROOT / 'art/terrain-gloom-v1'


class GloomExporterTests(unittest.TestCase):
    def test_all_parity_pairs_keep_checker_contrast(self):
        for skin in ('gloomy', 'dreamy', 'plain'):
            directory = SUITE / 'exports/runtime' / skin
            for light_file in directory.glob('*0.png'):
                dark_file = light_file.with_name(light_file.name[:-5] + '1.png')
                with self.subTest(skin=skin, pair=light_file.name):
                    self.assertTrue(dark_file.is_file())
                    light = ImageStat.Stat(Image.open(light_file).convert('L')).mean[0]
                    dark = ImageStat.Stat(Image.open(dark_file).convert('L')).mean[0]
                    self.assertGreaterEqual((light - dark) / light, .10)

    def test_manifest_has_all_connected_wall_masks(self):
        manifest = json.loads((SUITE / 'export-manifest.json').read_text())
        self.assertEqual(manifest['count'], 216)
        for skin in ('gloomy', 'dreamy', 'plain'):
            for mask in range(16):
                for parity in (0, 1):
                    name = f'{skin}/wall-{mask}-{parity}.png'
                    self.assertIn(name, manifest['files'])
                    self.assertTrue((ROOT / 'data/gfx/refined/gloom' / name).is_file())
