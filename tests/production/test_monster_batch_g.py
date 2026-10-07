"""monster-batch-g: 11 shipped identities (all clean, no waiver) plus Massok,
whose only miss is base_drift and which ships under the reviewer-approved
trusted waiver art/production/waivers/monster-batch-g.json.

xhaiak arachnomancer, shiaak venomblade (lighter v2), dremling (black-skinned
pale-scabrous v3 repaint of 2026-10-04, reversing the pale-stone v2 that had
followed the batch-F dark-on-dark rejection), Pale Drake, The Master (lighter v2),
Fillarel Aldaren, Krogar, Spellblaze Crystal, Rhaloren Inquisitor (v2 after a
disc-overflow repair), Harno and Lithfengel (v2) pass every style-gate check.
"""
import hashlib
import importlib.util
import json
import math
import tempfile
import unittest
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('check_token_style', ROOT / 'tools/check_token_style.py')
style = importlib.util.module_from_spec(spec)
spec.loader.exec_module(style)

SHIPPED = {
    'xhaiak-arachnomancer': 'xhaiak-arachnomancer-v1',
    'shiaak-venomblade': 'shiaak-venomblade-v2',
    'dremling': 'dremling-v3',
    'pale-drake': 'pale-drake-v1',
    'fillarel-aldaren': 'fillarel-aldaren-v1',
    'krogar': 'krogar-v1',
    'spellblaze-crystal': 'spellblaze-crystal-v2',
    'the-master': 'the-master-v2',
    'rhaloren-inquisitor': 'rhaloren-inquisitor-v2',
    'harno': 'harno-v1',
    'lithfengel': 'lithfengel-v2',
}


class MonsterBatchGShippedTests(unittest.TestCase):
    def test_every_shipped_asset_passes_with_no_waiver(self):
        for asset_id, master_name in SHIPPED.items():
            token = ROOT / f'art/monster-batch-g/sprites/128/{asset_id}.png'
            master = ROOT / f'art/monster-batch-g/masters/{master_name}.png'
            result = style.check_asset(token, master, asset_id, allow_grandfather=False)
            self.assertEqual(result['blocking'], [], asset_id)
            self.assertFalse(result['waived'], asset_id)
            self.assertTrue(result['passed'], asset_id)

    def test_selection_matches_the_shipped_set(self):
        selection = json.loads((ROOT / 'art/monster-batch-g/selected-masters.json').read_text())
        self.assertEqual(selection, {k: f'masters/{v}.png' for k, v in {**SHIPPED, 'massok': 'massok-v1'}.items()})

    def test_manifest_and_runtime_bytes_match_the_exports(self):
        manifest = json.loads((ROOT / 'data/token-manifest.json').read_text())
        # The manifest tracks the addon release, not this batch.
        import re
        init = (ROOT / 'init.lua').read_text()
        version = '.'.join(re.search(r'addon_version\s*=\s*\{(\d+),\s*(\d+),\s*(\d+)\}', init).groups())
        self.assertEqual(manifest['version'], version)
        shipped = {a['id'] for a in manifest['assets']}
        for asset_id in SHIPPED:
            self.assertIn(asset_id, shipped)
            runtime = (ROOT / f'data/gfx/tokens/{asset_id}.png').read_bytes()
            export = (ROOT / f'art/monster-batch-g/sprites/128/{asset_id}.png').read_bytes()
            self.assertEqual(runtime, export, asset_id)

    def test_dremling_repaint_is_darker_than_the_superseded_pale_token(self):
        # User decision 2026-10-04: the shipped pale-stone v2 (which held an axe)
        # was reversed to a black-skinned, pale-scabrous, weaponless repaint that
        # matches dremling's own desc and the accepted standee. The shipped token
        # must be the new v3 master and measurably darker in the masked-body
        # region than the superseded v2 token kept for provenance.
        def body_luminance(path):
            image = Image.open(path).convert('RGBA')
            size = image.width
            values = []
            for y in range(size):
                for x in range(size):
                    r, g, b, a = image.getpixel((x, y))
                    if a >= 180 and math.hypot(x + .5 - size / 2, y + .5 - size / 2) <= 0.55 * size / 2:
                        values.append(0.299 * r + 0.587 * g + 0.114 * b)
            return sum(values) / len(values)
        new = ROOT / 'art/monster-batch-g/sprites/128/dremling.png'
        old = ROOT / 'art/monster-batch-g/superseded/dremling-v2-runtime-128.png'
        self.assertTrue(old.is_file(), 'the superseded pale token must be kept for provenance')
        self.assertNotEqual(new.read_bytes(), old.read_bytes())
        self.assertLess(body_luminance(new), body_luminance(old) - 20)
        selection = json.loads((ROOT / 'art/monster-batch-g/selected-masters.json').read_text())
        self.assertEqual(selection['dremling'], 'masters/dremling-v3.png')

    def test_superseded_dark_drafts_are_not_selected(self):
        selection = json.loads((ROOT / 'art/monster-batch-g/selected-masters.json').read_text())
        self.assertTrue(selection['shiaak-venomblade'].endswith('-v2.png'))
        self.assertTrue(selection['the-master'].endswith('-v2.png'))


class MonsterBatchGMassokWaiverTests(unittest.TestCase):
    def test_massok_waiver_is_bound_to_both_images(self):
        token = ROOT / 'art/monster-batch-g/sprites/128/massok.png'
        master = ROOT / 'art/monster-batch-g/masters/massok-v1.png'
        accepted = style.check_asset(token, master, 'massok', allow_grandfather=False)
        self.assertTrue(accepted['waived'])
        self.assertEqual(accepted['blocking'], ['base_drift'])
        with tempfile.TemporaryDirectory() as folder:
            changed = Path(folder) / 'changed.png'
            for src, args in ((master, 'master'), (token, 'token')):
                with Image.open(src) as image:
                    image = image.copy()
                    image.putpixel((0, 0), (1, 1, 1, 0))
                    image.save(changed)
                result = (style.check_asset(token, changed, 'massok', False) if args == 'master'
                          else style.check_asset(changed, master, 'massok', False))
                self.assertFalse(result['passed'], f'changed {args} bytes must invalidate the waiver')

    def test_massok_is_wired_and_bytes_match_the_pinned_hashes(self):
        request = json.loads((ROOT / 'art/production/waivers/monster-batch-g-PENDING-REQUEST.json').read_text())['assets'][0]
        trusted = json.loads((ROOT / 'art/production/waivers/monster-batch-g.json').read_text())
        self.assertEqual([a['id'] for a in trusted['assets']], ['massok'])
        self.assertEqual(trusted['assets'][0]['master_sha256'], request['master_sha256'])
        self.assertEqual(trusted['assets'][0]['runtime_sha256'], request['runtime_128_export_sha256'])
        self.assertEqual(trusted['assets'][0]['waived_checks'], ['base_drift'])
        runtime = (ROOT / 'data/gfx/tokens/massok.png').read_bytes()
        self.assertEqual(hashlib.sha256(runtime).hexdigest(), request['runtime_128_export_sha256'])
        self.assertEqual(runtime, (ROOT / 'art/monster-batch-g/sprites/128/massok.png').read_bytes())
        manifest = {a['id']: a for a in json.loads((ROOT / 'data/token-manifest.json').read_text())['assets']}
        self.assertEqual(manifest['massok']['runtime_sha256'], request['runtime_128_export_sha256'])
        self.assertEqual(manifest['massok']['master_sha256'], request['master_sha256'])
        self.assertIn('id="massok"', (ROOT / 'overload/mod/class/CheckerTokens.lua').read_text())
        self.assertIn("'monster-batch-g'", (ROOT / 'tools/check_token_style.py').read_text())

    def test_request_file_is_base_drift_only_and_bound_to_the_master(self):
        request = json.loads((ROOT / 'art/production/waivers/monster-batch-g-PENDING-REQUEST.json').read_text())
        self.assertTrue(request['status'].startswith(('PENDING', 'REVIEWED')))
        self.assertEqual([a['id'] for a in request['assets']], ['massok'])
        asset = request['assets'][0]
        self.assertEqual(asset['corner_alpha'], [0, 0, 0, 0])
        self.assertLessEqual(asset['disc_overflow_max_opaque_radius'], 0.867)
        self.assertGreater(abs(asset['base_drift']), 8.0)
        self.assertLessEqual(asset['attempts_used'], 3)
        master = ROOT / asset['master_path']
        self.assertEqual(hashlib.sha256(master.read_bytes()).hexdigest(), asset['master_sha256'])


class MonsterBatchGBudgetTests(unittest.TestCase):
    def test_no_asset_exceeds_three_calls_and_batch_total_is_within_budget(self):
        totals = {}
        for call in (ROOT / 'art/production/handoffs').glob('monster-batch-g-*/*/imagegen-calls/call-*'):
            totals[call.parents[1].name] = totals.get(call.parents[1].name, 0) + 1
        self.assertTrue(all(v <= 3 for v in totals.values()), totals)
        self.assertLessEqual(sum(totals.values()), 26, totals)


if __name__ == '__main__':
    unittest.main()
