"""Exact-byte exceptions must stop applying after either art file changes."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('check_token_style', ROOT / 'tools/check_token_style.py')
style = importlib.util.module_from_spec(spec)
spec.loader.exec_module(style)


class MonsterBatchAWaiverTests(unittest.TestCase):
    def test_waiver_is_bound_to_both_images(self):
        token = ROOT / 'art/monster-batch-a/sprites/128/rantha.png'
        master = ROOT / 'art/monster-batch-a/masters/rantha-v1.png'
        accepted = style.check_asset(token, master, 'rantha', allow_grandfather=False)
        self.assertTrue(accepted['waived'])
        self.assertEqual(accepted['blocking'], ['base_drift'])
        with tempfile.TemporaryDirectory() as folder:
            changed = Path(folder) / 'changed.png'
            with Image.open(master) as image:
                image = image.copy()
                image.putpixel((0, 0), (1, 1, 1, 0))
                image.save(changed)
            self.assertFalse(style.check_asset(token, changed, 'rantha', False)['passed'])
            with Image.open(token) as image:
                image = image.copy()
                image.putpixel((0, 0), (1, 1, 1, 0))
                image.save(changed)
            self.assertFalse(style.check_asset(changed, master, 'rantha', False)['passed'])


if __name__ == '__main__':
    unittest.main()
