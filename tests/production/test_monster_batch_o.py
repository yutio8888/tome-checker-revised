"""monster-batch-o: survey-2 batch 6 (white ooze, gigantic corrosive tunneler,
gigantic gravity worm, slimy/poison/brittle clear ooze, carrion worm mass, cute
little bunny, dredgling, onilug, wretchling, brecklorn). All pass the style gate
with no waiver. Superseded or rejected drafts are never selected.
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
    'white-ooze': 'white-ooze-v1', 'gigantic-corrosive-tunneler': 'gigantic-corrosive-tunneler-v1',
    'gigantic-gravity-worm': 'gigantic-gravity-worm-v1', 'slimy-ooze': 'slimy-ooze-v1', 'poison-ooze': 'poison-ooze-v1',
    'carrion-worm-mass': 'carrion-worm-mass-v1', 'brittle-clear-ooze': 'brittle-clear-ooze-v1',
    'cute-little-bunny': 'cute-little-bunny-v2', 'dredgling': 'dredgling-v1', 'onilug': 'onilug-v3',
    'wretchling': 'wretchling-v1', 'brecklorn': 'brecklorn-v1',
}
NAMES = {
    'white-ooze': 'white ooze', 'gigantic-corrosive-tunneler': 'gigantic corrosive tunneler',
    'gigantic-gravity-worm': 'gigantic gravity worm', 'slimy-ooze': 'slimy ooze', 'poison-ooze': 'poison ooze',
    'carrion-worm-mass': 'carrion worm mass', 'brittle-clear-ooze': 'brittle clear ooze',
    'cute-little-bunny': 'cute little bunny', 'dredgling': 'dredgling', 'onilug': 'onilug',
    'wretchling': 'wretchling', 'brecklorn': 'brecklorn',
}
IMAGES = {
    'white-ooze': 'vermin_oozes_white_ooze', 'gigantic-corrosive-tunneler': 'vermin_sandworm_gigantic_corrosive_tunneler',
    'gigantic-gravity-worm': 'vermin_sandworm_gigantic_gravity_worm', 'slimy-ooze': 'vermin_oozes_slimy_ooze',
    'poison-ooze': 'vermin_oozes_poison_ooze', 'carrion-worm-mass': 'vermin_worms_carrion_worm_mass',
    'brittle-clear-ooze': 'vermin_oozes_brittle_clear_ooze', 'cute-little-bunny': 'vermin_rodent_cute_little_bunny',
    'dredgling': 'horror_temporal_dredgling', 'onilug': 'demon_minor_onilug', 'wretchling': 'demon_minor_wretchling',
    'brecklorn': 'horror_corrupted_brecklorn',
}
TYPES = {
    'white-ooze': 'vermin', 'gigantic-corrosive-tunneler': 'vermin', 'gigantic-gravity-worm': 'vermin', 'slimy-ooze': 'vermin',
    'poison-ooze': 'vermin', 'carrion-worm-mass': 'vermin', 'brittle-clear-ooze': 'vermin', 'cute-little-bunny': 'vermin',
    'dredgling': 'horror', 'onilug': 'demon', 'wretchling': 'demon', 'brecklorn': 'horror',
}
DEFINE_AS = {'carrion-worm-mass': 'CARRION_WORM_MASS'}
UNIQUE = ()
TALL = ('gigantic-corrosive-tunneler', 'gigantic-gravity-worm', 'onilug')
SUPERSEDED = {'onilug': 'onilug-v2'}
# onilug v3 (2026-10-04): gaunt over-long-limbed repaint per its desc.
FLOOR = 45.0


class MonsterBatchOShippedTests(unittest.TestCase):
    def test_every_asset_passes_with_no_waiver(self):
        for asset_id, master_name in SHIPPED.items():
            token = ROOT / f'art/monster-batch-o/sprites/128/{asset_id}.png'
            master = ROOT / f'art/monster-batch-o/masters/{master_name}.png'
            result = style.check_asset(token, master, asset_id, allow_grandfather=False)
            self.assertEqual(result['blocking'], [], asset_id)
            self.assertEqual(result['warnings'], [], asset_id)
            self.assertFalse(result['waived'], asset_id)
            self.assertTrue(result['passed'], asset_id)

    def test_no_pending_request_or_waiver_exists(self):
        waivers = ROOT / 'art/production/waivers'
        self.assertFalse((waivers / 'monster-batch-o.json').exists())
        self.assertFalse((waivers / 'monster-batch-o-PENDING-REQUEST.json').exists())

    def test_selection_matches_the_shipped_set(self):
        selection = json.loads((ROOT / 'art/monster-batch-o/selected-masters.json').read_text())
        self.assertEqual(selection, {k: f'masters/{v}.png' for k, v in SHIPPED.items()})
        catalog = json.loads((ROOT / 'art/monster-batch-o/catalog.json').read_text())
        self.assertEqual([a['id'] for a in catalog], list(SHIPPED))

    def test_manifest_and_runtime_bytes_match_the_exports(self):
        manifest = json.loads((ROOT / 'data/token-manifest.json').read_text())
        init = (ROOT / 'init.lua').read_text()
        version = '.'.join(re.search(r'addon_version\s*=\s*\{(\d+),\s*(\d+),\s*(\d+)\}', init).groups())
        self.assertEqual(manifest['version'], version)
        shipped = {a['id'] for a in manifest['assets']}
        for asset_id in SHIPPED:
            self.assertIn(asset_id, shipped)
            runtime = (ROOT / f'data/gfx/tokens/{asset_id}.png').read_bytes()
            export = (ROOT / f'art/monster-batch-o/sprites/128/{asset_id}.png').read_bytes()
            self.assertEqual(runtime, export, asset_id)

    def test_superseded_drafts_are_never_selected_and_nothing_shipped_is_dark(self):
        selection = json.loads((ROOT / 'art/monster-batch-o/selected-masters.json').read_text())
        for asset_id, old in SUPERSEDED.items():
            self.assertNotIn(old, selection[asset_id], asset_id)
        lum = json.loads((ROOT / 'art/monster-batch-o/review/luminance.json').read_text())
        self.assertEqual(lum['floor_minimum_for_body'], FLOOR)
        for asset_id in SHIPPED:
            self.assertGreater(lum['assets'][asset_id], FLOOR + 5, asset_id)

    def test_review_sheets_exist(self):
        review = ROOT / 'art/monster-batch-o/review'
        for name in ('floor-readability-48.png', 'floor-readability-48-x2.png', 'luminance.json'):
            self.assertTrue((review / name).is_file(), name)
        for group in ('oozes', 'worms', 'critters-demons-horrors'):
            for mode in ('color', 'grayscale'):
                self.assertTrue((review / f'{group}-{mode}-48-64-96.png').is_file(), group)


class MonsterBatchOCatalogTests(unittest.TestCase):
    def setUp(self):
        self.source = (ROOT / 'overload/mod/class/CheckerTokens.lua').read_text()

    def line(self, asset_id):
        line = next((l for l in self.source.splitlines() if f'{{id="{asset_id}",' in l), None)
        self.assertIsNotNone(line, asset_id)
        return line

    def test_exact_entries(self):
        for asset_id, name in NAMES.items():
            line = self.line(asset_id)
            self.assertIn(f'name="{name}"', line)
            self.assertIn(f'image="npc/{IMAGES[asset_id]}.png"', line)
            self.assertIn(f'type="{TYPES[asset_id]}"', line)

    def test_flags(self):
        for asset_id in SHIPPED:
            line = self.line(asset_id)
            self.assertEqual('native_tall=true' in line, asset_id in TALL, asset_id)
            self.assertEqual('unique=true' in line, asset_id in UNIQUE, asset_id)
            self.assertEqual('define_as' in line, asset_id in DEFINE_AS, asset_id)
            if asset_id in DEFINE_AS:
                self.assertIn(f'define_as="{DEFINE_AS[asset_id]}"', line)
            self.assertNotIn('urh_rok_form', line, asset_id)
        opted = [l for l in self.source.splitlines() if 'urh_rok_form=true' in l and '{id=' in l]
        self.assertEqual(len(opted), 5)  # grand corruptor, elven cultist, Rak'shor, Kor's Fury, Weirdling Beast (batch T)

    def test_contract_evidence_pins_source_and_native_sprite(self):
        import hashlib
        workspace = ROOT.parents[2]
        evidence = json.loads((ROOT / 'evidence/monster-batch-o-20260929/source-contracts.json').read_text())
        self.assertEqual(sorted(i['id'] for i in evidence['identities']), sorted(SHIPPED))
        self.assertEqual(evidence['kept_native'], [])
        self.assertEqual(evidence['runtime_mutation_scan']['hits_in_batch'], [])
        pinned = []
        for item in evidence['identities']:
            pinned.extend(item.get('extra_sources', []))
            for key in ('source', 'base_source'):
                if key in item:
                    pinned.append(item[key])
            sprite = workspace / item['native_image_path']
            self.assertEqual(hashlib.sha256(sprite.read_bytes()).hexdigest(), item['native_image_sha256'])
            self.assertEqual(item['native_image'], f"npc/{IMAGES[item['id']]}.png")
            self.assertEqual(item['native_image_size'], [64, 128] if item['id'] in TALL else [64, 64], item['id'])
            self.assertEqual(bool(item['native_tall']), item['id'] in TALL)
            self.assertEqual(bool(item['unique']), item['id'] in UNIQUE)
            self.assertEqual(item['define_as'], DEFINE_AS.get(item['id']), item['id'])
            self.assertEqual(item['type'], TYPES[item['id']])
        for pin in pinned:
            path = workspace / pin['path']
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), pin['sha256'])
            self.assertIn(pin['anchor'], path.read_text().splitlines()[pin['line'] - 1])
        collided = ' '.join(c['name'] for c in evidence['name_collisions_checked'])
        for name in ('carrion worm mass', 'white ooze', 'wretchling', 'gigantic corrosive tunneler', 'dredgling'):
            self.assertIn(name, collided)

    def test_render_evidence_pin_matches_the_pack_files(self):
        import hashlib
        evidence = ROOT / 'evidence/monster-batch-o-20260929/source-contracts.json'
        digest = hashlib.sha256(evidence.read_bytes()).hexdigest()
        for pack in sorted((ROOT / 'art/production/batches').glob('monster-batch-o-*.json')):
            for asset in json.loads(pack.read_text())['assets']:
                self.assertEqual([e['sha256'] for e in asset['render_evidence']], [digest], pack.name)


class MonsterBatchOBudgetTests(unittest.TestCase):
    def test_budget(self):
        per_asset, total = {}, 0
        for call in (ROOT / 'art/production/handoffs').glob('monster-batch-o-*/*/imagegen-calls/call-*'):
            per_asset[call.parents[1].name] = per_asset.get(call.parents[1].name, 0) + 1
            total += 1
        self.assertLessEqual(max(per_asset.values()), 3, per_asset)
        self.assertLessEqual(total, 28, per_asset)
        self.assertEqual(set(per_asset), set(SHIPPED))


if __name__ == '__main__':
    unittest.main()
