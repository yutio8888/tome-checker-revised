"""monster-batch-r: the next twelve identities by score of the survey-2 follow-up
list (orc necromancer, Rak'shor, Warmaster Gnarg, orc assassin, weaver young,
fate spinner, giant green and red ants, quasit, elven warrior, corrupted war
dog, grannor'vor). All pass the style gate with no waiver. Superseded or
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
    'orc-necromancer': 'orc-necromancer-v1', 'rak-shor': 'rak-shor-v2', 'warmaster-gnarg': 'warmaster-gnarg-v2',
    'orc-assassin': 'orc-assassin-v3', 'weaver-young': 'weaver-young-v1', 'fate-spinner': 'fate-spinner-v1',
    'giant-green-ant': 'giant-green-ant-v1', 'giant-red-ant': 'giant-red-ant-v1', 'quasit': 'quasit-v1',
    'elven-warrior': 'elven-warrior-v1', 'corrupted-war-dog': 'corrupted-war-dog-v2', 'grannor-vor': 'grannor-vor-v1',
}
NAMES = {
    'orc-necromancer': 'orc necromancer', 'rak-shor': "Rak'shor, Grand Necromancer of the Pride",
    'warmaster-gnarg': 'Warmaster Gnarg', 'orc-assassin': 'orc assassin', 'weaver-young': 'weaver young',
    'fate-spinner': 'fate spinner', 'giant-green-ant': 'giant green ant', 'giant-red-ant': 'giant red ant',
    'quasit': 'quasit', 'elven-warrior': 'elven warrior', 'corrupted-war-dog': 'corrupted war dog',
    'grannor-vor': "grannor'vor",
}
IMAGES = {
    'orc-necromancer': 'humanoid_orc_orc_necromancer', 'rak-shor': 'humanoid_orc_rak_shor__grand_necromancer_of_the_pride',
    'warmaster-gnarg': 'humanoid_orc_warmaster_gnarg', 'orc-assassin': 'humanoid_orc_orc_assassin',
    'weaver-young': 'spiderkin_spider_weaver_young', 'fate-spinner': 'spiderkin_spider_fate_spinner',
    'giant-green-ant': 'green_ant', 'giant-red-ant': 'red_ant', 'quasit': 'demon_minor_quasit',
    'elven-warrior': 'humanoid_shalore_elven_warrior', 'corrupted-war-dog': 'canine_dw',
    'grannor-vor': 'horror_corrupted_grannor_vor',
}
TYPES = {
    'orc-necromancer': 'humanoid', 'rak-shor': 'humanoid', 'warmaster-gnarg': 'humanoid', 'orc-assassin': 'humanoid',
    'weaver-young': 'spiderkin', 'fate-spinner': 'spiderkin', 'giant-green-ant': 'insect', 'giant-red-ant': 'insect',
    'quasit': 'demon', 'elven-warrior': 'humanoid', 'corrupted-war-dog': 'animal', 'grannor-vor': 'horror',
}
SUBTYPES = {
    'orc-necromancer': 'orc', 'rak-shor': 'orc', 'warmaster-gnarg': 'orc', 'orc-assassin': 'orc',
    'weaver-young': 'spider', 'fate-spinner': 'spider', 'giant-green-ant': 'ant', 'giant-red-ant': 'ant',
    'quasit': 'minor', 'elven-warrior': 'shalore', 'corrupted-war-dog': 'canine', 'grannor-vor': 'corrupted',
}
DEFINE_AS = {'rak-shor': 'RAK_SHOR', 'warmaster-gnarg': 'GNARG', 'corrupted-war-dog': 'CORRUPTED_WAR_DOG'}
UNIQUE = ('rak-shor', 'warmaster-gnarg')
# Every native sprite of this batch is 64x64 (no nice_tile, no tall body).
NATIVE_TALL_SPRITE = ()
SUPERSEDED = (('orc-assassin', 'orc-assassin-v1'), ('orc-assassin', 'orc-assassin-v2'), ('corrupted-war-dog', 'corrupted-war-dog-v1'))
FLOOR = 45.0


class MonsterBatchRShippedTests(unittest.TestCase):
    def test_every_asset_passes_with_no_waiver(self):
        for asset_id, master_name in SHIPPED.items():
            token = ROOT / f'art/monster-batch-r/sprites/128/{asset_id}.png'
            master = ROOT / f'art/monster-batch-r/masters/{master_name}.png'
            result = style.check_asset(token, master, asset_id, allow_grandfather=False)
            self.assertEqual(result['blocking'], [], asset_id)
            self.assertEqual(result['warnings'], [], asset_id)
            self.assertFalse(result['waived'], asset_id)
            self.assertTrue(result['passed'], asset_id)

    def test_no_pending_request_or_waiver_exists(self):
        waivers = ROOT / 'art/production/waivers'
        self.assertFalse((waivers / 'monster-batch-r.json').exists())
        self.assertFalse((waivers / 'monster-batch-r-PENDING-REQUEST.json').exists())

    def test_selection_matches_the_shipped_set(self):
        selection = json.loads((ROOT / 'art/monster-batch-r/selected-masters.json').read_text())
        self.assertEqual(selection, {k: f'masters/{v}.png' for k, v in SHIPPED.items()})
        catalog = json.loads((ROOT / 'art/monster-batch-r/catalog.json').read_text())
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
            export = (ROOT / f'art/monster-batch-r/sprites/128/{asset_id}.png').read_bytes()
            self.assertEqual(runtime, export, asset_id)

    def test_superseded_drafts_are_never_selected_and_nothing_shipped_is_dark(self):
        selection = json.loads((ROOT / 'art/monster-batch-r/selected-masters.json').read_text())
        for asset_id, old in SUPERSEDED:
            self.assertNotIn(old, selection[asset_id], asset_id)
        lum = json.loads((ROOT / 'art/monster-batch-r/review/luminance.json').read_text())
        self.assertEqual(lum['floor_minimum_for_body'], FLOOR)
        for asset_id in SHIPPED:
            self.assertGreater(lum['assets'][asset_id], FLOOR + 5, asset_id)

    def test_review_sheets_exist(self):
        review = ROOT / 'art/monster-batch-r/review'
        for name in ('floor-readability-48.png', 'floor-readability-48-x2.png', 'luminance.json'):
            self.assertTrue((review / name).is_file(), name)
        for group in ('orcs', 'spiders-ants', 'others'):
            for mode in ('color', 'grayscale'):
                self.assertTrue((review / f'{group}-{mode}-48-64-96.png').is_file(), group)


class MonsterBatchRCatalogTests(unittest.TestCase):
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
            self.assertNotIn('native_tall', line, asset_id)
            self.assertEqual('unique=true' in line, asset_id in UNIQUE, asset_id)
            self.assertIn(f'subtype="{SUBTYPES[asset_id]}"', line, asset_id)
            self.assertEqual('define_as' in line, asset_id in DEFINE_AS, asset_id)
            if asset_id in DEFINE_AS:
                self.assertIn(f'define_as="{DEFINE_AS[asset_id]}"', line)
            self.assertEqual('urh_rok_form=true' in line, asset_id == 'rak-shor', asset_id)
        opted = [l for l in self.source.splitlines() if 'urh_rok_form=true' in l and '{id=' in l]
        self.assertEqual(len(opted), 5)  # grand corruptor, elven cultist, Rak'shor, Kor's Fury, Weirdling Beast (batch T)

    def test_contract_evidence_pins_source_and_native_sprite(self):
        import hashlib
        workspace = ROOT.parents[2]
        evidence = json.loads((ROOT / 'evidence/monster-batch-r-20260929/source-contracts.json').read_text())
        self.assertEqual(sorted(i['id'] for i in evidence['identities']), sorted(SHIPPED))
        self.assertEqual(evidence['kept_native'], [])
        self.assertEqual(len(evidence['runtime_mutation_scan']['hits_in_batch']), 2)
        self.assertEqual(len(evidence['runtime_mutation_scan']['writers_found']), 2)
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
            self.assertFalse(item['native_tall'], item['id'])
            self.assertEqual(bool(item['unique']), item['id'] in UNIQUE)
            self.assertEqual(item['define_as'], DEFINE_AS.get(item['id']), item['id'])
            self.assertEqual(item['type'], TYPES[item['id']])
        for pin in pinned:
            path = workspace / pin['path']
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), pin['sha256'])
            self.assertIn(pin['anchor'], path.read_text().splitlines()[pin['line'] - 1])
        collided = ' '.join(c['name'] for c in evidence['name_collisions_checked'])
        for name in ('weaver young', 'corrupted war dog', "Rak'shor, Grand Necromancer of the Pride", 'Warmaster Gnarg',
                     'giant green ant / giant red ant', 'orc necromancer', 'orc assassin', 'fate spinner', 'quasit',
                     'elven warrior', "grannor'vor"):
            self.assertIn(name, collided)
        scan = evidence['runtime_mutation_scan']
        self.assertEqual(len(scan['auto_classes_review']), 2)
        classes = ' '.join(r['class'] for r in scan['auto_classes_review'])
        self.assertIn('Corruptor', classes)
        self.assertIn('Berserker', classes)
        flame = ' '.join(h for h in scan['hits_in_batch'])
        self.assertIn("Flame of Urh'Rok", flame)

    def test_render_evidence_pin_matches_the_pack_files(self):
        import hashlib
        evidence = ROOT / 'evidence/monster-batch-r-20260929/source-contracts.json'
        digest = hashlib.sha256(evidence.read_bytes()).hexdigest()
        for pack in sorted((ROOT / 'art/production/batches').glob('monster-batch-r-*.json')):
            for asset in json.loads(pack.read_text())['assets']:
                self.assertEqual([e['sha256'] for e in asset['render_evidence']], [digest], pack.name)


class MonsterBatchRBudgetTests(unittest.TestCase):
    def test_budget(self):
        per_asset, total = {}, 0
        for call in (ROOT / 'art/production/handoffs').glob('monster-batch-r-*/*/imagegen-calls/call-*'):
            per_asset[call.parents[1].name] = per_asset.get(call.parents[1].name, 0) + 1
            total += 1
        self.assertLessEqual(max(per_asset.values()), 3, per_asset)
        self.assertLessEqual(total, 28, per_asset)
        self.assertEqual(set(per_asset), set(SHIPPED))


if __name__ == '__main__':
    unittest.main()
