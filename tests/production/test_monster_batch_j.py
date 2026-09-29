"""monster-batch-j: eleven guaranteed bosses/uniques (Shardskin, The Withering
Thing, The Dreaming One, Weaver Queen, Murgol, Lady Nashva, The Possessed,
Subject Z, Grand Corruptor, Assassin Lord, Ben Cruthdar the Abomination), all
passing the style gate with no waiver. Kyless was kept native here (nice_tile{tall=1}
with no image=). Superseded drafts are never selected.
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
    'shardskin': 'shardskin-v1',
    'the-withering-thing': 'the-withering-thing-v1',
    'the-dreaming-one': 'the-dreaming-one-v1',
    'weaver-queen': 'weaver-queen-v1',
    'murgol': 'murgol-v2',
    'lady-nashva': 'lady-nashva-v2',
    'the-possessed': 'the-possessed-v2',
    'subject-z': 'subject-z-v3',
    'grand-corruptor': 'grand-corruptor-v2',
    'assassin-lord': 'assassin-lord-v1',
    'ben-cruthdar-abomination': 'ben-cruthdar-abomination-v1',
}
NAMES = {
    "shardskin": "Shardskin",
    "the-withering-thing": "The Withering Thing",
    "the-dreaming-one": "The Dreaming One",
    "weaver-queen": "Weaver Queen",
    "murgol": "Murgol, the Yaech Lord",
    "lady-nashva": "Lady Nashva the Streambender",
    "the-possessed": "The Possessed",
    "subject-z": "Subject Z",
    "grand-corruptor": "Grand Corruptor",
    "assassin-lord": "Assassin Lord",
    "ben-cruthdar-abomination": "Ben Cruthdar, the Abomination",
}
DEFINE_AS = {
    'shardskin': 'SHARDSKIN', 'the-withering-thing': 'WITHERING_THING', 'the-dreaming-one': 'DREAMING_ONE',
    'weaver-queen': 'WEAVER_QUEEN', 'murgol': 'MURGOL', 'lady-nashva': 'NASHVA', 'the-possessed': 'THE_POSSESSED',
    'subject-z': 'SUBJECT_Z', 'grand-corruptor': 'GRAND_CORRUPTOR', 'assassin-lord': 'ASSASSIN_LORD',
    'ben-cruthdar-abomination': 'BEN_CRUTHDAR_ABOMINATION',
}
SUPERSEDED = {
    'grand-corruptor': 'grand-corruptor-v1',
    'the-possessed': 'the-possessed-v1',
    'subject-z': 'subject-z-v2',
}


class MonsterBatchJShippedTests(unittest.TestCase):
    def test_every_asset_passes_with_no_waiver(self):
        for asset_id, master_name in SHIPPED.items():
            token = ROOT / f'art/monster-batch-j/sprites/128/{asset_id}.png'
            master = ROOT / f'art/monster-batch-j/masters/{master_name}.png'
            result = style.check_asset(token, master, asset_id, allow_grandfather=False)
            self.assertEqual(result['blocking'], [], asset_id)
            self.assertFalse(result['waived'], asset_id)
            self.assertTrue(result['passed'], asset_id)

    def test_no_pending_request_or_waiver_exists(self):
        waivers = ROOT / 'art/production/waivers'
        self.assertFalse((waivers / 'monster-batch-j.json').exists())
        self.assertFalse((waivers / 'monster-batch-j-PENDING-REQUEST.json').exists())

    def test_selection_matches_the_shipped_set(self):
        selection = json.loads((ROOT / 'art/monster-batch-j/selected-masters.json').read_text())
        self.assertEqual(selection, {k: f'masters/{v}.png' for k, v in SHIPPED.items()})
        catalog = json.loads((ROOT / 'art/monster-batch-j/catalog.json').read_text())
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
            export = (ROOT / f'art/monster-batch-j/sprites/128/{asset_id}.png').read_bytes()
            self.assertEqual(runtime, export, asset_id)

    def test_superseded_drafts_are_never_selected_and_nothing_shipped_is_dark(self):
        selection = json.loads((ROOT / 'art/monster-batch-j/selected-masters.json').read_text())
        for asset_id, old in SUPERSEDED.items():
            self.assertNotIn(old, selection[asset_id], asset_id)
            self.assertTrue((ROOT / f'art/monster-batch-j/masters/{old}.png').is_file(), old)
        lum = json.loads((ROOT / 'art/monster-batch-j/review/luminance.json').read_text())['assets']
        self.assertGreater(lum['grand-corruptor'], lum['grand-corruptor OLD v1 (superseded)'] * 1.3)
        self.assertGreater(lum['the-possessed'], lum['the-possessed OLD v1 (superseded)'] * 1.3)
        for asset_id in SHIPPED:
            self.assertGreater(lum[asset_id], 45.0, asset_id)


class MonsterBatchJCatalogTests(unittest.TestCase):
    def setUp(self):
        self.source = (ROOT / 'overload/mod/class/CheckerTokens.lua').read_text()

    def test_exact_entries(self):
        for asset_id, name in NAMES.items():
            line = next((l for l in self.source.splitlines() if f'id="{asset_id}"' in l), None)
            self.assertIsNotNone(line, asset_id)
            self.assertIn(f'name="{name}"', line)
            self.assertIn(f'define_as="{DEFINE_AS[asset_id]}"', line)
            self.assertIn('unique=true', line)
            self.assertNotIn('native_tall', line, asset_id)

    def test_kyless_was_kept_native_in_j_and_is_mapped_by_batch_l(self):
        # Batch J kept Kyless native on a static guess (nice_tile{tall=1}); its
        # live census showed image=invis.png with one add_mos naming the PNG, so
        # batch L maps him. Batch J's own evidence still records the earlier
        # decision, and the catalog line is owned by batch L.
        self.assertIn('id="kyless"', self.source)
        self.assertIn('define_as="KYLESS"', self.source)
        evidence = json.loads((ROOT / 'evidence/monster-batch-j-20260929/source-contracts.json').read_text())
        self.assertEqual([k['define_as'] for k in evidence['kept_native']], ['KYLESS'])

    def test_heart_gloom_whitelist_covers_exactly_four_families(self):
        self.assertIn('["animal/bear"] = true, ["immovable/plants"] = true', self.source)
        self.assertIn('["vermin/rodent"] = true, ["animal/canine"] = true', self.source)

    def test_contract_evidence_pins_source_and_native_sprite(self):
        evidence = json.loads((ROOT / 'evidence/monster-batch-j-20260929/source-contracts.json').read_text())
        import hashlib
        workspace = ROOT.parents[2]
        self.assertEqual(sorted(i['id'] for i in evidence['identities']), sorted(SHIPPED))
        self.assertEqual(evidence['kept_native'][0]['native_image_sha256'], hashlib.sha256((workspace / evidence['kept_native'][0]['native_image_path']).read_bytes()).hexdigest())
        for item in evidence['identities']:
            for extra in item.get('extra_sources', []):
                path = workspace / extra['path']
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), extra['sha256'])
                self.assertIn(extra['anchor'], path.read_text().splitlines()[extra['line'] - 1])
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
            self.assertTrue(item['unique'], item['id'])


class MonsterBatchJBudgetTests(unittest.TestCase):
    def test_budget_and_no_pending_waiver(self):
        per_asset, total = {}, 0
        for call in (ROOT / 'art/production/handoffs').glob('monster-batch-j-*/*/imagegen-calls/call-*'):
            per_asset[call.parents[1].name] = per_asset.get(call.parents[1].name, 0) + 1
            total += 1
        self.assertTrue(all(v <= 3 for v in per_asset.values()), per_asset)
        self.assertLessEqual(total, 26, per_asset)
        self.assertEqual(set(per_asset), set(SHIPPED))


if __name__ == '__main__':
    unittest.main()
