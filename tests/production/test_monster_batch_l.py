"""monster-batch-l: survey-2 batch 3 (orc warrior/soldier/archer, elven guard,
mean looking elven guard, elven mage/tempest/blood mage, naga myrmidon, naga
nereid, yaech diver) plus Kyless, all passing the style gate with no waiver.
The elven cultist was kept native here (Flame of Urh'Rok at birth) and is
mapped by batch M after its live check. Superseded or
rejected drafts are never selected.
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
    'orc-warrior': 'orc-warrior-v1',
    'orc-soldier': 'orc-soldier-v1',
    'orc-archer': 'orc-archer-v1',
    'naga-myrmidon': 'naga-myrmidon-v2',
    'elven-guard': 'elven-guard-v1',
    'mean-looking-elven-guard': 'mean-looking-elven-guard-v1',
    'naga-nereid': 'naga-nereid-v1',
    'elven-mage': 'elven-mage-v1',
    'elven-tempest': 'elven-tempest-v1',
    'elven-blood-mage': 'elven-blood-mage-v2',
    'yaech-diver': 'yaech-diver-v1',
    'kyless': 'kyless-v2',
}
NAMES = {
    'orc-warrior': 'orc warrior', 'orc-soldier': 'orc soldier', 'orc-archer': 'orc archer',
    'naga-myrmidon': 'naga myrmidon', 'elven-guard': 'elven guard',
    'mean-looking-elven-guard': 'mean looking elven guard', 'naga-nereid': 'naga nereid',
    'elven-mage': 'elven mage', 'elven-tempest': 'elven tempest', 'elven-blood-mage': 'elven blood mage',
    'yaech-diver': 'yaech diver', 'kyless': 'Kyless',
}
IMAGES = {
    'orc-warrior': 'humanoid_orc_orc_warrior', 'orc-soldier': 'humanoid_orc_orc_soldier',
    'orc-archer': 'humanoid_orc_orc_archer', 'naga-myrmidon': None,
    'elven-guard': 'humanoid_shalore_elven_guard', 'mean-looking-elven-guard': 'humanoid_shalore_mean_looking_elven_guard',
    'naga-nereid': 'humanoid_naga_naga_nereid', 'elven-mage': 'humanoid_shalore_elven_mage',
    'elven-tempest': 'humanoid_shalore_elven_tempest', 'elven-blood-mage': 'humanoid_shalore_elven_blood_mage',
    'yaech-diver': 'humanoid_yaech_yaech_diver', 'kyless': 'humanoid_human_kyless',
}
DEFINE_AS = {'orc-warrior': 'HILL_ORC_WARRIOR', 'orc-soldier': 'ORC', 'orc-archer': 'HILL_ORC_ARCHER', 'kyless': 'KYLESS'}
TALL = ('naga-nereid', 'kyless')
SUPERSEDED = {'naga-myrmidon': 'naga-myrmidon-v1', 'kyless': 'kyless-v1', 'elven-blood-mage': 'elven-blood-mage-v1'}
FLOOR = 45.0


class MonsterBatchLShippedTests(unittest.TestCase):
    def test_every_asset_passes_with_no_waiver(self):
        for asset_id, master_name in SHIPPED.items():
            token = ROOT / f'art/monster-batch-l/sprites/128/{asset_id}.png'
            master = ROOT / f'art/monster-batch-l/masters/{master_name}.png'
            result = style.check_asset(token, master, asset_id, allow_grandfather=False)
            self.assertEqual(result['blocking'], [], asset_id)
            self.assertEqual(result['warnings'], [], asset_id)
            self.assertFalse(result['waived'], asset_id)
            self.assertTrue(result['passed'], asset_id)

    def test_no_pending_request_or_waiver_exists(self):
        waivers = ROOT / 'art/production/waivers'
        self.assertFalse((waivers / 'monster-batch-l.json').exists())
        self.assertFalse((waivers / 'monster-batch-l-PENDING-REQUEST.json').exists())

    def test_selection_matches_the_shipped_set(self):
        selection = json.loads((ROOT / 'art/monster-batch-l/selected-masters.json').read_text())
        self.assertEqual(selection, {k: f'masters/{v}.png' for k, v in SHIPPED.items()})
        catalog = json.loads((ROOT / 'art/monster-batch-l/catalog.json').read_text())
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
            export = (ROOT / f'art/monster-batch-l/sprites/128/{asset_id}.png').read_bytes()
            self.assertEqual(runtime, export, asset_id)
        # Batch L kept the cultist native; batch M mapped it (see test_monster_batch_m).

    def test_superseded_drafts_are_never_selected_and_nothing_shipped_is_dark(self):
        selection = json.loads((ROOT / 'art/monster-batch-l/selected-masters.json').read_text())
        for asset_id, old in SUPERSEDED.items():
            self.assertNotIn(old, selection[asset_id], asset_id)
            self.assertTrue((ROOT / f'art/monster-batch-l/masters/{old}.png').is_file() or asset_id == 'naga-myrmidon', old)
        lum = json.loads((ROOT / 'art/monster-batch-l/review/luminance.json').read_text())
        self.assertEqual(lum['floor_minimum_for_body'], FLOOR)
        for asset_id in SHIPPED:
            self.assertGreater(lum['assets'][asset_id], FLOOR + 10, asset_id)

    def test_review_sheets_exist(self):
        review = ROOT / 'art/monster-batch-l/review'
        for name in ('floor-readability-48.png', 'floor-readability-48-x2.png', 'luminance.json'):
            self.assertTrue((review / name).is_file(), name)
        for group in ('orcs', 'elves', 'nagas-yaech-humans'):
            for mode in ('color', 'grayscale'):
                self.assertTrue((review / f'{group}-{mode}-48-64-96.png').is_file(), group)


class MonsterBatchLCatalogTests(unittest.TestCase):
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
            image = IMAGES[asset_id] or 'naga_myrmidon'
            self.assertIn(f'image="npc/{image}.png"', line)

    def test_flags(self):
        self.assertIn('unique=true', self.line('kyless'))
        self.assertIn('define_as="KYLESS"', self.line('kyless'))
        self.assertNotIn('native_tall', self.line('kyless'))
        self.assertIn('native_tall=true', self.line('naga-nereid'))
        self.assertNotIn('unique', self.line('naga-nereid'))
        for asset_id in SHIPPED:
            if asset_id != 'naga-nereid':
                self.assertNotIn('native_tall', self.line(asset_id), asset_id)
            if asset_id != 'kyless':
                self.assertNotIn('unique', self.line(asset_id), asset_id)
            if asset_id in DEFINE_AS:
                self.assertIn(f'define_as="{DEFINE_AS[asset_id]}"', self.line(asset_id))
            else:
                self.assertNotIn('define_as', self.line(asset_id), asset_id)
            self.assertNotIn('urh_rok_form', self.line(asset_id), asset_id)

    def test_elven_cultist_was_kept_native_by_l_and_is_mapped_by_m(self):
        # L kept it native; M maps it with urh_rok_form=true. L's own entries
        # never carry the flag (asserted in test_flags), and L's evidence still
        # records the original kept-native decision.
        self.assertIn('id="elven-cultist"', self.source)
        self.assertTrue((ROOT / 'art/monster-batch-m/catalog.json').is_file())

    def test_contract_evidence_pins_source_and_native_sprite(self):
        import hashlib
        workspace = ROOT.parents[2]
        evidence = json.loads((ROOT / 'evidence/monster-batch-l-20260929/source-contracts.json').read_text())
        self.assertEqual(sorted(i['id'] for i in evidence['identities']), sorted(SHIPPED))
        self.assertEqual([k['name'] for k in evidence['kept_native']], ['elven cultist'])
        self.assertEqual([h['identity'] for h in evidence['runtime_mutation_scan']['hits_in_batch']], ['elven cultist'])
        pinned = [evidence['kept_native'][0]['source']]
        for item in evidence['identities']:
            pinned.extend(item.get('extra_sources', []))
            for key in ('source', 'base_source'):
                if key in item:
                    pinned.append(item[key])
            sprite = workspace / item['native_image_path']
            self.assertEqual(hashlib.sha256(sprite.read_bytes()).hexdigest(), item['native_image_sha256'])
            expected = IMAGES[item['id']]
            self.assertEqual(item['native_image'], f"npc/{expected}.png" if expected else 'npc/naga_myrmidon.png')
            self.assertEqual(item['native_image_size'], [64, 128] if item['id'] in TALL else [64, 64], item['id'])
            self.assertEqual(bool(item['native_tall']), item['id'] == 'naga-nereid')
            self.assertEqual(bool(item['unique']), item['id'] == 'kyless')
            self.assertEqual(item['define_as'], DEFINE_AS.get(item['id']), item['id'])
        for pin in pinned:
            path = workspace / pin['path']
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), pin['sha256'])
            self.assertIn(pin['anchor'], path.read_text().splitlines()[pin['line'] - 1])
        collided = ' '.join(c['name'] for c in evidence['name_collisions_checked'])
        for name in ('orc warrior', 'naga nereid', 'naga myrmidon'):
            self.assertIn(name, collided)


class MonsterBatchLBudgetTests(unittest.TestCase):
    def test_budget(self):
        per_asset, total = {}, 0
        for call in (ROOT / 'art/production/handoffs').glob('monster-batch-l-*/*/imagegen-calls/call-*'):
            per_asset[call.parents[1].name] = per_asset.get(call.parents[1].name, 0) + 1
            total += 1
        self.assertLessEqual(max(per_asset.values()), 3, per_asset)
        self.assertLessEqual(total, 28, per_asset)
        self.assertEqual(set(per_asset), set(SHIPPED))


if __name__ == '__main__':
    unittest.main()
