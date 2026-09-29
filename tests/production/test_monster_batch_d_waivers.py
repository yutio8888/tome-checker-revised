"""Exact-byte exceptions must stop applying after either art file changes.

Mirrors test_monster_batch_a_waivers.py for the monster-batch-d trusted
waiver (art/production/waivers/monster-batch-d.json), which is consulted the
same way as batches A/B (tools/check_token_style.py, ~line 299). Only
giant-brown-ant and giant-blue-ant are in the trusted file; giant-carpenter-ant
and giant-black-ant shipped clean after a redraw and never needed a waiver
(see art/monster-batch-d/REVIEW.md).
"""
import importlib.util
import tempfile
import unittest
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('check_token_style', ROOT / 'tools/check_token_style.py')
style = importlib.util.module_from_spec(spec)
spec.loader.exec_module(style)


class MonsterBatchDWaiverTests(unittest.TestCase):
    def _check_asset_bound(self, asset_id):
        token = ROOT / f'art/monster-batch-d/sprites/128/{asset_id}.png'
        master = ROOT / f'art/monster-batch-d/masters/{asset_id}-v1.png'
        accepted = style.check_asset(token, master, asset_id, allow_grandfather=False)
        self.assertTrue(accepted['waived'], f'{asset_id} should be waived by monster-batch-d.json')
        self.assertEqual(accepted['blocking'], ['base_drift'])
        with tempfile.TemporaryDirectory() as folder:
            changed = Path(folder) / 'changed.png'
            with Image.open(master) as image:
                image = image.copy()
                image.putpixel((0, 0), (1, 1, 1, 0))
                image.save(changed)
            self.assertFalse(style.check_asset(token, changed, asset_id, False)['passed'],
                              'changing the master bytes must invalidate the waiver')
            with Image.open(token) as image:
                image = image.copy()
                image.putpixel((0, 0), (1, 1, 1, 0))
                image.save(changed)
            self.assertFalse(style.check_asset(changed, master, asset_id, False)['passed'],
                              'changing the runtime export bytes must invalidate the waiver')

    def test_giant_brown_ant_waiver_is_bound_to_both_images(self):
        self._check_asset_bound('giant-brown-ant')

    def test_giant_blue_ant_waiver_is_bound_to_both_images(self):
        self._check_asset_bound('giant-blue-ant')

    def test_carpenter_and_black_ant_pass_without_any_waiver(self):
        # These two shipped after a calibrated redraw (monster-batch-d-4) that
        # cleared the style gate outright; they must never need
        # monster-batch-d.json (or any other trusted file) to pass.
        for asset_id, master_name in (
            ('giant-carpenter-ant', 'giant-carpenter-ant-redraw2-v1'),
            ('giant-black-ant', 'giant-black-ant-redraw2-v1'),
        ):
            token = ROOT / f'art/monster-batch-d/sprites/128/{asset_id}.png'
            master = ROOT / f'art/monster-batch-d/masters/{master_name}.png'
            result = style.check_asset(token, master, asset_id, allow_grandfather=False)
            self.assertEqual(result['blocking'], [], f'{asset_id} must pass with zero blocking findings')
            self.assertFalse(result['waived'], f'{asset_id} must not need a waiver')
            self.assertTrue(result['passed'])


if __name__ == '__main__':
    unittest.main()
