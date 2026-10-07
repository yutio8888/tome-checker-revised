"""monster-batch-p: survey-2 batch 7 (four snow giants, minotaur, two mountain
trolls, four ogres, Healer Astelrid). All pass the style gate with no waiver.
Superseded or rejected drafts are never selected.
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
    'snow-giant': 'snow-giant-v2', 'snow-giant-thunderer': 'snow-giant-thunderer-v1',
    'snow-giant-boulder-thrower': 'snow-giant-boulder-thrower-v2', 'snow-giant-chieftain': 'snow-giant-chieftain-v1',
    'minotaur': 'minotaur-v3', 'mountain-troll': 'mountain-troll-v1', 'mountain-troll-thunderer': 'mountain-troll-thunderer-v1',
    'ogre-guard': 'ogre-guard-v1', 'ogre-mauler': 'ogre-mauler-v2', 'ogre-rune-spinner': 'ogre-rune-spinner-v1',
    'ogre-pounder': 'ogre-pounder-v1', 'healer-astelrid': 'healer-astelrid-v1',
}
NAMES = {
    'snow-giant': 'snow giant', 'snow-giant-thunderer': 'snow giant thunderer',
    'snow-giant-boulder-thrower': 'snow giant boulder thrower', 'snow-giant-chieftain': 'snow giant chieftain',
    'minotaur': 'minotaur', 'mountain-troll': 'mountain troll', 'mountain-troll-thunderer': 'mountain troll thunderer',
    'ogre-guard': 'ogre guard', 'ogre-mauler': 'ogre mauler', 'ogre-rune-spinner': 'ogre rune-spinner',
    'ogre-pounder': 'ogre pounder', 'healer-astelrid': 'Healer Astelrid',
}
IMAGES = {
    'snow-giant': 'giant_ice_snow_giant', 'snow-giant-thunderer': 'giant_ice_snow_giant_thunderer',
    'snow-giant-boulder-thrower': 'giant_ice_snow_giant_boulder_thrower', 'snow-giant-chieftain': 'giant_ice_snow_giant_chieftain',
    'minotaur': 'giant_minotaur_minotaur', 'mountain-troll': 'troll_m', 'mountain-troll-thunderer': 'troll_mt',
    'ogre-guard': 'giant_ogre_ogre_guard', 'ogre-mauler': 'giant_ogre_ogre_mauler',
    'ogre-rune-spinner': 'giant_ogre_ogre_rune_spinner', 'ogre-pounder': 'giant_ogre_ogre_pounder',
    'healer-astelrid': 'giant_ogre_healer_astelrid',
}
TYPES = {asset_id: 'giant' for asset_id in SHIPPED}
SUBTYPES = {'minotaur': 'minotaur', 'mountain-troll': 'troll', 'mountain-troll-thunderer': 'troll'}
DEFINE_AS = {'healer-astelrid': 'HEALER_ASTELRID'}
UNIQUE = ('healer-astelrid',)
TALL = ('snow-giant', 'snow-giant-thunderer', 'snow-giant-boulder-thrower', 'snow-giant-chieftain', 'minotaur',
        'ogre-guard', 'ogre-mauler', 'ogre-rune-spinner', 'ogre-pounder')
# Native sprite is 64x128 for every tall body (Astelrid included); the trolls are 64x64.
NATIVE_TALL_SPRITE = TALL + ('healer-astelrid',)
SUPERSEDED = {'minotaur': 'minotaur-v1', 'ogre-mauler': 'ogre-mauler-v1'}
FLOOR = 45.0


class MonsterBatchPShippedTests(unittest.TestCase):
    def test_every_asset_passes_with_no_waiver(self):
        for asset_id, master_name in SHIPPED.items():
            token = ROOT / f'art/monster-batch-p/sprites/128/{asset_id}.png'
            master = ROOT / f'art/monster-batch-p/masters/{master_name}.png'
            result = style.check_asset(token, master, asset_id, allow_grandfather=False)
            self.assertEqual(result['blocking'], [], asset_id)
            self.assertEqual(result['warnings'], [], asset_id)
            self.assertFalse(result['waived'], asset_id)
            self.assertTrue(result['passed'], asset_id)

    def test_no_pending_request_or_waiver_exists(self):
        waivers = ROOT / 'art/production/waivers'
        self.assertFalse((waivers / 'monster-batch-p.json').exists())
        self.assertFalse((waivers / 'monster-batch-p-PENDING-REQUEST.json').exists())

    def test_selection_matches_the_shipped_set(self):
        selection = json.loads((ROOT / 'art/monster-batch-p/selected-masters.json').read_text())
        self.assertEqual(selection, {k: f'masters/{v}.png' for k, v in SHIPPED.items()})
        catalog = json.loads((ROOT / 'art/monster-batch-p/catalog.json').read_text())
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
            export = (ROOT / f'art/monster-batch-p/sprites/128/{asset_id}.png').read_bytes()
            self.assertEqual(runtime, export, asset_id)

    def test_superseded_drafts_are_never_selected_and_nothing_shipped_is_dark(self):
        selection = json.loads((ROOT / 'art/monster-batch-p/selected-masters.json').read_text())
        for asset_id, old in SUPERSEDED.items():
            self.assertNotIn(old, selection[asset_id], asset_id)
        lum = json.loads((ROOT / 'art/monster-batch-p/review/luminance.json').read_text())
        self.assertEqual(lum['floor_minimum_for_body'], FLOOR)
        for asset_id in SHIPPED:
            self.assertGreater(lum['assets'][asset_id], FLOOR + 5, asset_id)

    def test_review_sheets_exist(self):
        review = ROOT / 'art/monster-batch-p/review'
        for name in ('floor-readability-48.png', 'floor-readability-48-x2.png', 'luminance.json'):
            self.assertTrue((review / name).is_file(), name)
        for group in ('snow-giants', 'minotaur-trolls', 'ogres'):
            for mode in ('color', 'grayscale'):
                self.assertTrue((review / f'{group}-{mode}-48-64-96.png').is_file(), group)


class MonsterBatchPCatalogTests(unittest.TestCase):
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
            self.assertIn(f'subtype="{SUBTYPES.get(asset_id, "ice" if asset_id.startswith("snow") else "ogre")}"', line, asset_id)
            self.assertEqual('define_as' in line, asset_id in DEFINE_AS, asset_id)
            if asset_id in DEFINE_AS:
                self.assertIn(f'define_as="{DEFINE_AS[asset_id]}"', line)
            self.assertNotIn('urh_rok_form', line, asset_id)
        opted = [l for l in self.source.splitlines() if 'urh_rok_form=true' in l and '{id=' in l]
        self.assertEqual(len(opted), 5)  # grand corruptor, elven cultist, Rak'shor, Kor's Fury, Weirdling Beast (batch T)
        # Astelrid is a unique bound to her define_as and is NOT flagged native_tall.
        self.assertNotIn('native_tall', self.line('healer-astelrid'))

    def test_contract_evidence_pins_source_and_native_sprite(self):
        import hashlib
        workspace = ROOT.parents[2]
        evidence = json.loads((ROOT / 'evidence/monster-batch-p-20260929/source-contracts.json').read_text())
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
            self.assertEqual(item['native_image_size'], [64, 128] if item['id'] in NATIVE_TALL_SPRITE else [64, 64], item['id'])
            self.assertEqual(bool(item['native_tall']), item['id'] in TALL)
            self.assertEqual(bool(item['unique']), item['id'] in UNIQUE)
            self.assertEqual(item['define_as'], DEFINE_AS.get(item['id']), item['id'])
            self.assertEqual(item['type'], TYPES[item['id']])
        for pin in pinned:
            path = workspace / pin['path']
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), pin['sha256'])
            self.assertIn(pin['anchor'], path.read_text().splitlines()[pin['line'] - 1])
        collided = ' '.join(c['name'] for c in evidence['name_collisions_checked'])
        for name in ('minotaur', 'ogre rune-spinner', 'mountain troll', 'snow giant family', 'Healer Astelrid'):
            self.assertIn(name, collided)

    def test_render_evidence_pin_matches_the_pack_files(self):
        import hashlib
        evidence = ROOT / 'evidence/monster-batch-p-20260929/source-contracts.json'
        digest = hashlib.sha256(evidence.read_bytes()).hexdigest()
        for pack in sorted((ROOT / 'art/production/batches').glob('monster-batch-p-*.json')):
            for asset in json.loads(pack.read_text())['assets']:
                self.assertEqual([e['sha256'] for e in asset['render_evidence']], [digest], pack.name)


class MonsterBatchPBudgetTests(unittest.TestCase):
    def test_budget(self):
        per_asset, total = {}, 0
        for call in (ROOT / 'art/production/handoffs').glob('monster-batch-p-*/*/imagegen-calls/call-*'):
            per_asset[call.parents[1].name] = per_asset.get(call.parents[1].name, 0) + 1
            total += 1
        self.assertLessEqual(max(per_asset.values()), 3, per_asset)
        self.assertLessEqual(total, 28, per_asset)
        self.assertEqual(set(per_asset), set(SHIPPED))


if __name__ == '__main__':
    unittest.main()
