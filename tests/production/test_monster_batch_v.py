"""monster-batch-v: the twelve identities that follow batch U in the survey-2
unscheduled list (black crystal, faerlhing, losselhing, dredge, dolleg, eternal
bone giant, drem master, orc pyromancer, orc cryomancer, bloated horror, yaech
hunter, orc blood mage). All pass the style gate with no waiver. Rejected drafts
were never stored as masters. Ten are non-unique define_as-less 64x64 single
images; dolleg and the eternal bone giant are non-unique native_tall bodies.
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

SHIPPED = {i: i + '-v1' for i in ['black-crystal', 'faerlhing', 'losselhing', 'dredge', 'drem-master', 'bloated-horror', 'orc-pyromancer', 'orc-cryomancer', 'orc-blood-mage', 'dolleg', 'eternal-bone-giant', 'yaech-hunter']}
NAMES = {
    'black-crystal': 'black crystal',
    'faerlhing': 'faerlhing',
    'losselhing': 'losselhing',
    'dredge': 'dredge',
    'drem-master': 'drem master',
    'bloated-horror': 'bloated horror',
    'orc-pyromancer': 'orc pyromancer',
    'orc-cryomancer': 'orc cryomancer',
    'orc-blood-mage': 'orc blood mage',
    'dolleg': 'dolleg',
    'eternal-bone-giant': 'eternal bone giant',
    'yaech-hunter': 'yaech hunter',
}
IMAGES = {
    'black-crystal': 'crystal_black',
    'faerlhing': 'spiderkin_spider_faerlhing',
    'losselhing': 'spiderkin_spider_losselhing',
    'dredge': 'horror_temporal_dredge',
    'drem-master': 'horror_corrupted_drem_master',
    'bloated-horror': 'horror_eldritch_bloated_horror',
    'orc-pyromancer': 'humanoid_orc_orc_pyromancer',
    'orc-cryomancer': 'humanoid_orc_orc_cryomancer',
    'orc-blood-mage': 'humanoid_orc_orc_blood_mage',
    'dolleg': 'demon_major_dolleg',
    'eternal-bone-giant': 'undead_giant_eternal_bone_giant',
    'yaech-hunter': 'humanoid_yaech_yaech_hunter',
}
TYPES = {
    'black-crystal': 'immovable',
    'faerlhing': 'spiderkin',
    'losselhing': 'spiderkin',
    'dredge': 'horror',
    'drem-master': 'horror',
    'bloated-horror': 'horror',
    'orc-pyromancer': 'humanoid',
    'orc-cryomancer': 'humanoid',
    'orc-blood-mage': 'humanoid',
    'dolleg': 'demon',
    'eternal-bone-giant': 'undead',
    'yaech-hunter': 'humanoid',
}
SUBTYPES = {
    'black-crystal': 'crystal',
    'faerlhing': 'spider',
    'losselhing': 'spider',
    'dredge': 'temporal',
    'drem-master': 'corrupted',
    'bloated-horror': 'eldritch',
    'orc-pyromancer': 'orc',
    'orc-cryomancer': 'orc',
    'orc-blood-mage': 'orc',
    'dolleg': 'major',
    'eternal-bone-giant': 'giant',
    'yaech-hunter': 'yaech',
}
SHIPPED['drem-master'] = 'drem-master-v2'
SUPERSEDED = (('drem-master', 'drem-master-v1'),)
TALL = {'dolleg', 'eternal-bone-giant'}
FLOOR = 45.0


class MonsterBatchVShippedTests(unittest.TestCase):
    def test_every_asset_passes_with_no_waiver(self):
        for asset_id, master_name in SHIPPED.items():
            token = ROOT / f'art/monster-batch-v/sprites/128/{asset_id}.png'
            master = ROOT / f'art/monster-batch-v/masters/{master_name}.png'
            result = style.check_asset(token, master, asset_id, allow_grandfather=False)
            self.assertEqual(result['blocking'], [], asset_id)
            self.assertEqual(result['warnings'], [], asset_id)
            self.assertFalse(result['waived'], asset_id)
            self.assertTrue(result['passed'], asset_id)

    def test_no_pending_request_or_waiver_exists(self):
        waivers = ROOT / 'art/production/waivers'
        self.assertFalse((waivers / 'monster-batch-v.json').exists())
        self.assertFalse((waivers / 'monster-batch-v-PENDING-REQUEST.json').exists())

    def test_selection_matches_the_shipped_set(self):
        selection = json.loads((ROOT / 'art/monster-batch-v/selected-masters.json').read_text())
        self.assertEqual(selection, {k: f'masters/{v}.png' for k, v in SHIPPED.items()})
        catalog = json.loads((ROOT / 'art/monster-batch-v/catalog.json').read_text())
        self.assertEqual([a['id'] for a in catalog], list(SHIPPED))
        for asset_id, old in SUPERSEDED:
            self.assertNotIn(old + '.png', selection[asset_id], asset_id)
        self.assertEqual(sorted(p.name for p in (ROOT / 'art/monster-batch-v/masters').glob('*.png')),
                         sorted([f'{v}.png' for v in SHIPPED.values()] + [f'{o}.png' for _, o in SUPERSEDED]))

    def test_manifest_and_runtime_bytes_match_the_exports(self):
        manifest = json.loads((ROOT / 'data/token-manifest.json').read_text())
        init = (ROOT / 'init.lua').read_text()
        version = '.'.join(re.search(r'addon_version\s*=\s*\{(\d+),\s*(\d+),\s*(\d+)\}', init).groups())
        self.assertEqual(manifest['version'], version)
        shipped = {a['id'] for a in manifest['assets']}
        for asset_id in SHIPPED:
            self.assertIn(asset_id, shipped)
            runtime = (ROOT / f'data/gfx/tokens/{asset_id}.png').read_bytes()
            export = (ROOT / f'art/monster-batch-v/sprites/128/{asset_id}.png').read_bytes()
            self.assertEqual(runtime, export, asset_id)

    def test_nothing_shipped_is_dark(self):
        lum = json.loads((ROOT / 'art/monster-batch-v/review/luminance.json').read_text())
        self.assertEqual(lum['floor_minimum_for_body'], FLOOR)
        for asset_id in SHIPPED:
            self.assertGreaterEqual(lum['assets'][asset_id], 65.0, asset_id)

    def test_review_sheets_exist(self):
        review = ROOT / 'art/monster-batch-v/review'
        for name in ('floor-readability-48.png', 'floor-readability-48-x2.png', 'luminance.json'):
            self.assertTrue((review / name).is_file(), name)
        for group in ('crystals-spiders', 'horrors', 'orcs', 'giants-demons-yeeks'):
            for mode in ('color', 'grayscale'):
                self.assertTrue((review / f'{group}-{mode}-48-64-96.png').is_file(), group)


class MonsterBatchVCatalogTests(unittest.TestCase):
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
            self.assertIn(f'subtype="{SUBTYPES[asset_id]}"', line)

    def test_flags(self):
        for asset_id in SHIPPED:
            line = self.line(asset_id)
            for flag in ('unique', 'define_as', 'urh_rok_form'):
                self.assertNotIn(flag, line, (asset_id, flag))
            self.assertEqual('native_tall=true' in line, asset_id in TALL, asset_id)
        opted = [l for l in self.source.splitlines() if 'urh_rok_form=true' in l and '{id=' in l]
        self.assertEqual(len(opted), 5)  # unchanged by batch V: none of its identities can reach Flame of Urh'Rok

    def test_no_variants_or_aliases_were_added(self):
        for asset_id in SHIPPED:
            self.assertNotIn(f'["{asset_id}"] = function', self.source)
            self.assertNotIn(f'{asset_id} = function', self.source)
            self.assertNotIn(f'["{asset_id}"] = {{\n\t\timage', self.source)
        self.assertIn('local wild_summon_ids = {minotaur=true, ["black-jelly"]=true, ["fire-drake"]=true, ["ritch-flamespitter"]=true}', self.source)
        self.assertEqual(self.source.count('image_aliases[entry.id]'), 1)

    def test_contract_evidence_pins_source_and_native_sprite(self):
        import hashlib
        workspace = ROOT.parents[2]
        evidence = json.loads((ROOT / 'evidence/monster-batch-v-20260930/source-contracts.json').read_text())
        self.assertEqual(sorted(i['id'] for i in evidence['identities']), sorted(SHIPPED))
        self.assertEqual(evidence['runtime_mutation_scan']['hits_in_batch'], [])
        self.assertEqual(evidence['kept_native'], [])
        self.assertEqual(len(evidence['runtime_mutation_scan']['writers_found']), 3)
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
            self.assertEqual(item['native_tall'], item['id'] in TALL, item['id'])
            self.assertEqual('tall_body' in item, item['id'] in TALL, item['id'])
            self.assertFalse(item['unique'], item['id'])
            self.assertIsNone(item['define_as'], item['id'])
            self.assertEqual(item['type'], TYPES[item['id']])
            self.assertEqual(item['subtype'], SUBTYPES[item['id']])
        for pin in pinned:
            path = workspace / pin['path']
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), pin['sha256'])
            self.assertIn(pin['anchor'], path.read_text().splitlines()[pin['line'] - 1])
        collided = ' '.join(c['name'] for c in evidence['name_collisions_checked'])
        for name in NAMES.values():
            self.assertIn(name, collided)
        scan = evidence['runtime_mutation_scan']
        self.assertEqual(len(scan['auto_classes_review']), 1)
        self.assertIn('none', scan['auto_classes_review'][0]['class'])
        summons = ' '.join(evidence['summons_and_same_body_copies']['findings'])
        self.assertIn('e_bone_giant', summons)
        self.assertIn('NO variants entry', summons)

    def test_render_evidence_pin_matches_the_pack_files(self):
        import hashlib
        evidence = ROOT / 'evidence/monster-batch-v-20260930/source-contracts.json'
        digest = hashlib.sha256(evidence.read_bytes()).hexdigest()
        for pack in sorted((ROOT / 'art/production/batches').glob('monster-batch-v-*.json')):
            for asset in json.loads(pack.read_text())['assets']:
                self.assertEqual([e['sha256'] for e in asset['render_evidence']], [digest], pack.name)


class MonsterBatchVBudgetTests(unittest.TestCase):
    def test_budget(self):
        per_asset, total = {}, 0
        for call in (ROOT / 'art/production/handoffs').glob('monster-batch-v-*/*/imagegen-calls/call-*'):
            per_asset[call.parents[1].name] = per_asset.get(call.parents[1].name, 0) + 1
            total += 1
        self.assertLessEqual(max(per_asset.values()), 3, per_asset)
        self.assertLessEqual(total, 28, per_asset)
        self.assertEqual(set(per_asset), set(SHIPPED))


if __name__ == '__main__':
    unittest.main()
