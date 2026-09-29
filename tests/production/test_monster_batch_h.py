"""monster-batch-h: twelve ordinary (non-unique) single-image identities, all
passing the style gate with no waiver: sandworm, sandworm destroyer, sandworm
burrower, white/red/crimson crystal, poison ivy, honey tree, Necromancer and the
fleshy/boney/sanguine experiments. Necromancer and the sanguine experiment ship
their v2 masters; the v1 drafts passed the gate but were rejected by eye
(near-black at 48px) and are never selected.
"""
import importlib.util
import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('check_token_style', ROOT / 'tools/check_token_style.py')
style = importlib.util.module_from_spec(spec)
spec.loader.exec_module(style)

SHIPPED = {
    'sandworm': 'sandworm-v1',
    'sandworm-destroyer': 'sandworm-destroyer-v1',
    'sandworm-burrower': 'sandworm-burrower-v1',
    'white-crystal': 'white-crystal-v1',
    'red-crystal': 'red-crystal-v1',
    'crimson-crystal': 'crimson-crystal-v1',
    'poison-ivy': 'poison-ivy-v1',
    'honey-tree': 'honey-tree-v1',
    'necromancer': 'necromancer-v2',
    'fleshy-experiment': 'fleshy-experiment-v1',
    'boney-experiment': 'boney-experiment-v1',
    'sanguine-experiment': 'sanguine-experiment-v2',
}
NAMES = {
    'sandworm': 'sandworm', 'sandworm-destroyer': 'sandworm destroyer',
    'sandworm-burrower': 'sandworm burrower', 'white-crystal': 'white crystal',
    'red-crystal': 'red crystal', 'crimson-crystal': 'crimson crystal',
    'poison-ivy': 'poison ivy', 'honey-tree': 'honey tree', 'necromancer': 'Necromancer',
    'fleshy-experiment': 'fleshy experiment', 'boney-experiment': 'boney experiment',
    'sanguine-experiment': 'sanguine experiment',
}


class MonsterBatchHShippedTests(unittest.TestCase):
    def test_every_asset_passes_with_no_waiver(self):
        for asset_id, master_name in SHIPPED.items():
            token = ROOT / f'art/monster-batch-h/sprites/128/{asset_id}.png'
            master = ROOT / f'art/monster-batch-h/masters/{master_name}.png'
            result = style.check_asset(token, master, asset_id, allow_grandfather=False)
            self.assertEqual(result['blocking'], [], asset_id)
            self.assertFalse(result['waived'], asset_id)
            self.assertTrue(result['passed'], asset_id)

    def test_no_pending_request_or_waiver_exists(self):
        waivers = ROOT / 'art/production/waivers'
        self.assertFalse((waivers / 'monster-batch-h.json').exists())
        self.assertFalse((waivers / 'monster-batch-h-PENDING-REQUEST.json').exists())

    def test_selection_matches_the_shipped_set(self):
        selection = json.loads((ROOT / 'art/monster-batch-h/selected-masters.json').read_text())
        self.assertEqual(selection, {k: f'masters/{v}.png' for k, v in SHIPPED.items()})
        catalog = json.loads((ROOT / 'art/monster-batch-h/catalog.json').read_text())
        self.assertEqual([a['id'] for a in catalog], list(SHIPPED))

    def test_manifest_and_runtime_bytes_match_the_exports(self):
        manifest = json.loads((ROOT / 'data/token-manifest.json').read_text())
        # The manifest tracks the addon release, not this batch.
        init = (ROOT / 'init.lua').read_text()
        version = '.'.join(re.search(r'addon_version\s*=\s*\{(\d+),\s*(\d+),\s*(\d+)\}', init).groups())
        self.assertEqual(manifest['version'], version)
        shipped = {a['id'] for a in manifest['assets']}
        for asset_id in SHIPPED:
            self.assertIn(asset_id, shipped)
            runtime = (ROOT / f'data/gfx/tokens/{asset_id}.png').read_bytes()
            export = (ROOT / f'art/monster-batch-h/sprites/128/{asset_id}.png').read_bytes()
            self.assertEqual(runtime, export, asset_id)

    def test_superseded_dark_drafts_are_not_selected_and_are_much_lighter_now(self):
        selection = json.loads((ROOT / 'art/monster-batch-h/selected-masters.json').read_text())
        self.assertTrue(selection['necromancer'].endswith('-v2.png'))
        self.assertTrue(selection['sanguine-experiment'].endswith('-v2.png'))
        lum = json.loads((ROOT / 'art/monster-batch-h/review/luminance.json').read_text())['assets']
        self.assertGreater(lum['necromancer'], lum['necromancer OLD v1 (superseded: dark robe)'] * 1.25)
        self.assertGreater(lum['sanguine-experiment'], lum['sanguine-experiment OLD v1 (superseded: near-black clot)'] * 1.5)
        # Nothing that ships is below the shipped weakest dark subject (harno 45.7).
        for asset_id in SHIPPED:
            self.assertGreater(lum[asset_id], 45.0, asset_id)


class MonsterBatchHCatalogTests(unittest.TestCase):
    def setUp(self):
        self.source = (ROOT / 'overload/mod/class/CheckerTokens.lua').read_text()

    def test_exact_single_image_entries_only(self):
        for asset_id, name in NAMES.items():
            line = next((l for l in self.source.splitlines() if f'id="{asset_id}"' in l), None)
            self.assertIsNotNone(line, asset_id)
            self.assertIn(f'name="{name}"', line)
            # Non-unique, single-image: no unique / native_tall marker.
            self.assertNotIn('unique=true', line, asset_id)
            self.assertNotIn('native_tall', line, asset_id)
        self.assertIn('define_as="SANDWORM_TUNNELER"', self.source)
        self.assertIn('define_as="NECROMANCER"', self.source)

    def test_contract_evidence_pins_source_and_native_sprite(self):
        evidence = json.loads((ROOT / 'evidence/monster-batch-h-20260929/source-contracts.json').read_text())
        import hashlib
        workspace = ROOT.parents[2]
        self.assertEqual(sorted(i['id'] for i in evidence['identities']), sorted(SHIPPED))
        for item in evidence['identities']:
            for key in ('source', 'base_source'):
                if key not in item:
                    continue
                pin = item[key]
                path = workspace / pin['path']
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), pin['sha256'])
                self.assertIn(pin['anchor'], path.read_text().splitlines()[pin['line'] - 1])
            sprite = workspace / item['native_image_path']
            self.assertTrue(sprite.is_file(), item['id'])
            self.assertEqual(hashlib.sha256(sprite.read_bytes()).hexdigest(), item['native_image_sha256'])
            self.assertFalse(item['unique'])


class MonsterBatchHBudgetTests(unittest.TestCase):
    def test_no_asset_exceeds_three_calls_and_batch_total_is_within_budget(self):
        totals = {}
        for call in (ROOT / 'art/production/handoffs').glob('monster-batch-h-*/*/imagegen-calls/call-*'):
            totals[call.parents[1].name] = totals.get(call.parents[1].name, 0) + 1
        self.assertTrue(all(v <= 3 for v in totals.values()), totals)
        self.assertLessEqual(sum(totals.values()), 26, totals)
        self.assertEqual(set(totals), set(SHIPPED), 'every shipped asset has at least one recorded call')


if __name__ == '__main__':
    unittest.main()
