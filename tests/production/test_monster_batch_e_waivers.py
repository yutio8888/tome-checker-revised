"""Exact-byte exceptions must stop applying after either art file changes.

Mirrors test_monster_batch_d_waivers.py for the monster-batch-e trusted
waiver (art/production/waivers/monster-batch-e.json), which is consulted the
same way as batches A/B/D (tools/check_token_style.py, ~line 299). All seven
base_drift-only candidates from the pending request were approved by the
reviewer (see art/monster-batch-e/REVIEW.md 'Reviewer decision'); the other 5
batch-E identities shipped clean and never needed a waiver.

2026-09-29 (monster-batch-f): the kryl-feijan entry was removed from
monster-batch-e.json -- the batch-E master read as an almost pure black blob
at 48px on a real dark stone floor (evidence/monster-live-e-20260929), and
monster-batch-f shipped a pale storm-grey redraw that clears the style gate
cleanly with no waiver at all (art/monster-batch-f/masters/kryl-feijan-c-v1.png,
see overload/mod/class/CheckerTokens.lua and art/monster-batch-f/REVIEW.md).
Six of the seven original base_drift-only identities remain waived here.
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


class MonsterBatchEWaiverTests(unittest.TestCase):
    def _check_asset_bound(self, asset_id):
        token = ROOT / f'art/monster-batch-e/sprites/128/{asset_id}.png'
        master = ROOT / f'art/monster-batch-e/masters/{asset_id}-v1.png'
        accepted = style.check_asset(token, master, asset_id, allow_grandfather=False)
        self.assertTrue(accepted['waived'], f'{asset_id} should be waived by monster-batch-e.json')
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

    def test_urkis_waiver_is_bound_to_both_images(self):
        self._check_asset_bound('urkis')

    def test_golbug_waiver_is_bound_to_both_images(self):
        self._check_asset_bound('golbug')

    def test_ungole_waiver_is_bound_to_both_images(self):
        self._check_asset_bound('ungole')

    def test_half_finished_bone_giant_waiver_is_bound_to_both_images(self):
        self._check_asset_bound('half-finished-bone-giant')

    def test_kryl_feijan_waiver_was_removed_by_monster_batch_f(self):
        # The old batch-E artifact itself is untouched on disk, but its
        # waiver entry in monster-batch-e.json was deliberately removed
        # (superseded by monster-batch-f's clean, no-waiver redraw), so the
        # same old master/token pair must now come back unwaived. This is
        # the mirror image of _check_asset_bound: proving removal actually
        # revokes the exception rather than leaving a stale byte match.
        token = ROOT / 'art/monster-batch-e/sprites/128/kryl-feijan.png'
        master = ROOT / 'art/monster-batch-e/masters/kryl-feijan-v1.png'
        result = style.check_asset(token, master, 'kryl-feijan', allow_grandfather=False)
        self.assertFalse(result['waived'], 'kryl-feijan waiver must be gone from monster-batch-e.json')
        self.assertFalse(result['passed'], 'the old master still fails base_drift on its own merits')
        self.assertEqual(result['blocking'], ['base_drift'])

    def test_atamathon_waiver_is_bound_to_both_images(self):
        self._check_asset_bound('atamathon')

    def test_ritch_hive_mother_waiver_is_bound_to_both_images(self):
        self._check_asset_bound('ritch-hive-mother')

    def test_shipped_without_waiver_pass_without_any_waiver(self):
        # These five shipped in the same batch without needing base_drift
        # forgiveness; they must never need monster-batch-e.json (or any
        # other trusted file) to pass.
        for asset_id, master_name in (
            ('lady-zoisla', 'lady-zoisla-v2'),
            ('brotoq', 'brotoq-v2'),
            ('the-mouth', 'the-mouth-v1'),
            ('the-abomination', 'the-abomination-v2'),
            ('celia', 'celia-v1'),
        ):
            token = ROOT / f'art/monster-batch-e/sprites/128/{asset_id}.png'
            master = ROOT / f'art/monster-batch-e/masters/{master_name}.png'
            result = style.check_asset(token, master, asset_id, allow_grandfather=False)
            self.assertEqual(result['blocking'], [], f'{asset_id} must pass with zero blocking findings')
            self.assertFalse(result['waived'], f'{asset_id} must not need a waiver')
            self.assertTrue(result['passed'])


if __name__ == '__main__':
    unittest.main()
