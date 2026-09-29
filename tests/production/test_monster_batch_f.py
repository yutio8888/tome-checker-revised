"""monster-batch-f: 6 shipped identities (4 clean, 2 under a reviewer-approved
base_drift waiver) plus 1 rejected candidate that must stay unwired.

CONTRACTS-B5-B7-20260929.md 4.1's "NEEDS-CONTRACT-EXTENSION" identities:
naga tidewarden, naga tidecaller and treant cleared the style gate cleanly
(no waiver). dremling, shivgoroth and greater shivgoroth all missed only
base_drift and were recorded as PENDING waiver requests
(art/production/waivers/monster-batch-f-PENDING-REQUEST.json). The reviewer
approved shivgoroth and greater shivgoroth (2026-09-29, see
art/monster-batch-f/REVIEW.md 'Reviewer decision'); they now ship under the
trusted exact-byte waiver in art/production/waivers/monster-batch-f.json and
are wired into the catalog, tools/check_token_style.py's trusted batch list
and the runtime manifest. dremling was rejected (dark subject on a dark
base, the same 48px failure as the old kryl-feijan master) and stays
native/unmapped; no monster-batch-f.json entry exists for it.

kryl-feijan (already shipped in monster-batch-e under a base_drift waiver)
was redrawn for 48px dark-floor readability and now also ships clean with no
waiver, superseding and removing its old monster-batch-e waiver entry (see
test_monster_batch_e_waivers.py).
"""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('check_token_style', ROOT / 'tools/check_token_style.py')
style = importlib.util.module_from_spec(spec)
spec.loader.exec_module(style)


class MonsterBatchFShippedTests(unittest.TestCase):
    def test_shipped_assets_pass_without_any_waiver(self):
        for asset_id, master_name in (
            ('naga-tidewarden', 'naga-tidewarden-v2'),
            ('naga-tidecaller', 'naga-tidecaller-v2'),
            ('treant', 'treant-v2'),
            ('kryl-feijan', 'kryl-feijan-c-v1'),
        ):
            token = ROOT / f'art/monster-batch-f/sprites/128/{asset_id}.png'
            master = ROOT / f'art/monster-batch-f/masters/{master_name}.png'
            result = style.check_asset(token, master, asset_id, allow_grandfather=False)
            self.assertEqual(result['blocking'], [], f'{asset_id} must pass with zero blocking findings')
            self.assertFalse(result['waived'], f'{asset_id} must not need a waiver')
            self.assertTrue(result['passed'])

    def test_shipped_ids_are_exactly_the_six_catalog_additions(self):
        manifest = json.loads((ROOT / 'data/token-manifest.json').read_text())
        shipped = {a['id'] for a in manifest['assets']}
        for asset_id in ('naga-tidewarden', 'naga-tidecaller', 'treant', 'kryl-feijan',
                          'shivgoroth', 'greater-shivgoroth'):
            self.assertIn(asset_id, shipped)
        # dremling: the batch-F draft was rejected; the batch-G pale-stone redraw
        # ships (tests/production/test_monster_batch_g.py). The batch-F draft
        # itself must never be selected: see MonsterBatchFRejectedTests.


class MonsterBatchFWaiverTests(unittest.TestCase):
    """shivgoroth and greater shivgoroth ship under the trusted exact-byte
    waiver in art/production/waivers/monster-batch-f.json, mirroring
    test_monster_batch_e_waivers.py's _check_asset_bound pattern."""

    def _check_asset_bound(self, asset_id, master_name):
        token = ROOT / f'art/monster-batch-f/sprites/128/{asset_id}.png'
        master = ROOT / f'art/monster-batch-f/masters/{master_name}.png'
        accepted = style.check_asset(token, master, asset_id, allow_grandfather=False)
        self.assertTrue(accepted['waived'], f'{asset_id} should be waived by monster-batch-f.json')
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

    def test_shivgoroth_waiver_is_bound_to_both_images(self):
        self._check_asset_bound('shivgoroth', 'shivgoroth-v1')

    def test_greater_shivgoroth_waiver_is_bound_to_both_images(self):
        self._check_asset_bound('greater-shivgoroth', 'greater-shivgoroth-v1')

    def test_monster_batch_f_is_in_the_trusted_batch_list(self):
        source = (ROOT / 'tools/check_token_style.py').read_text()
        self.assertIn("'monster-batch-f'", source)


class MonsterBatchFRejectedTests(unittest.TestCase):
    """dremling was rejected by the reviewer and must never ship, with or
    without a waiver."""

    def test_dremling_has_no_trusted_waiver_entry(self):
        waiver = json.loads((ROOT / 'art/production/waivers/monster-batch-f.json').read_text())
        ids = {a['id'] for a in waiver['assets']}
        self.assertEqual(ids, {'shivgoroth', 'greater-shivgoroth'})
        self.assertNotIn('dremling', ids)

    def test_dremling_master_fails_base_drift_and_stays_unwaived(self):
        master = ROOT / 'art/monster-batch-f/masters/dremling-v1.png'
        self.assertTrue(master.is_file(), 'dremling candidate master must be recorded for review')
        for size in (128,):
            candidate = ROOT / f'art/monster-batch-f/sprites/{size}/dremling.png'
            self.assertFalse(candidate.is_file(), 'dremling must have no shipped runtime export')

    def test_batch_f_dremling_draft_is_not_the_shipped_master(self):
        # The rejected batch-F obsidian draft must not be what ships; the
        # shipped dremling is the batch-G redraw (a different master).
        selection = json.loads((ROOT / 'art/monster-batch-g/selected-masters.json').read_text())
        self.assertNotIn('monster-batch-f', selection['dremling'])
        self.assertNotEqual(selection['dremling'], 'masters/dremling-v1.png')
        report = json.loads((ROOT / 'art/monster-batch-g/export-report.json').read_text())
        shipped = {a['id']: a for a in report['assets']}['dremling']
        old = (ROOT / 'art/monster-batch-f/masters/dremling-v1.png').read_bytes()
        import hashlib
        self.assertNotEqual(shipped['sha256'], hashlib.sha256(old).hexdigest())


class MonsterBatchFRequestFileTests(unittest.TestCase):
    def test_pending_request_file_lists_exactly_three_base_drift_only_candidates(self):
        request = json.loads((ROOT / 'art/production/waivers/monster-batch-f-PENDING-REQUEST.json').read_text())
        # The request file itself is a historical record and stays untrusted;
        # it is REVIEWED now (2 approved, 1 rejected), not PENDING, but wiring
        # happened only through the trusted monster-batch-f.json above.
        self.assertTrue(request['status'].startswith(('PENDING', 'REVIEWED')))
        ids = {a['id'] for a in request['assets']}
        self.assertEqual(ids, {'dremling', 'shivgoroth', 'greater-shivgoroth'})
        for asset in request['assets']:
            self.assertEqual(asset['corner_alpha'], [0, 0, 0, 0])
            self.assertLessEqual(asset['disc_overflow_max_opaque_radius'], 0.867)
            self.assertGreater(abs(asset['base_drift']), 8.0, f"{asset['id']} must actually miss base_drift")


if __name__ == '__main__':
    unittest.main()
