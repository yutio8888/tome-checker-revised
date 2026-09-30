"""monster-batch-aa: the twelve identities that follow batch Z in the survey-2
unscheduled list (ultimate faeros, orc berserker, dredge captain, polar bear,
anaconda, ultimate teluvorta, necrotic abomination, bone horror, sanguine horror,
barrow wight, ogre warmaster, dreadmaster). All pass the style gate with no
waiver and every masked body luminance is at least 65 (floor unchanged). Seven are
non-unique native_tall bodies; five are 64x64 single images; none binds a
define_as.
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

IDS = ['ultimate-faeros', 'orc-berserker', 'dredge-captain', 'polar-bear', 'anaconda', 'ultimate-teluvorta', 'necrotic-abomination', 'bone-horror', 'sanguine-horror', 'barrow-wight', 'ogre-warmaster', 'dreadmaster']
SHIPPED = {i: i + '-v1' for i in IDS}
SHIPPED['ogre-warmaster'] = 'ogre-warmaster-v2'  # v1 drew a subject_intrusion warning (+38.07) and is kept under superseded/
SHIPPED['barrow-wight'] = 'barrow-wight-v2'  # v1 (pack 6) was a busy muted grey-green mass at 48px; v2 (pack 10) is the simplified light version; v1 is kept under superseded/
SHIPPED['sanguine-horror'] = 'sanguine-horror-v3'  # v1 measured 58.6 and v2 60.8 masked luminance (floor 65); both are kept under superseded/
NAMES = {i: i.replace('-', ' ') for i in IDS}
IMAGES = {
    'ultimate-faeros': 'npc/elemental_fire_ultimate_faeros',
    'orc-berserker': 'npc/humanoid_orc_orc_berserker',
    'dredge-captain': 'npc/horror_temporal_dredge_captain',
    'polar-bear': 'npc/polar_bear',
    'anaconda': 'npc/yellow-green-snake',
    'ultimate-teluvorta': 'npc/elemental_temporal_ultimate_teluvorta',
    'necrotic-abomination': 'npc/undead_horror_necrotic_abomination',
    'bone-horror': 'npc/undead_horror_bone_horror',
    'sanguine-horror': 'npc/undead_horror_sanguine_horror',
    'barrow-wight': 'npc/barrow_wight',
    'ogre-warmaster': 'npc/giant_ogre_ogre_warmaster',
    'dreadmaster': 'npc/dreadmaster',
}
TYPES = {'ultimate-faeros': 'elemental', 'orc-berserker': 'humanoid', 'dredge-captain': 'horror', 'polar-bear': 'animal', 'anaconda': 'animal',
         'ultimate-teluvorta': 'elemental', 'necrotic-abomination': 'undead', 'bone-horror': 'undead', 'sanguine-horror': 'undead',
         'barrow-wight': 'undead', 'ogre-warmaster': 'giant', 'dreadmaster': 'undead'}
SUBTYPES = {'ultimate-faeros': 'fire', 'orc-berserker': 'orc', 'dredge-captain': 'temporal', 'polar-bear': 'bear', 'anaconda': 'snake',
            'ultimate-teluvorta': 'temporal', 'necrotic-abomination': 'horror', 'bone-horror': 'horror', 'sanguine-horror': 'horror',
            'barrow-wight': 'wight', 'ogre-warmaster': 'ogre', 'dreadmaster': 'ghost'}
DEFINE_AS = {}
TALL = {'ultimate-faeros', 'ultimate-teluvorta', 'necrotic-abomination', 'bone-horror', 'sanguine-horror', 'barrow-wight', 'ogre-warmaster'}
FLOOR = 45.0
GROUPS = ('fire-temporal-dredge-ghost', 'orc-ogre-wight-bear-snake', 'undead-horrors')


class MonsterBatchAAShippedTests(unittest.TestCase):
    def test_every_asset_passes_with_no_waiver(self):
        for asset_id, master_name in SHIPPED.items():
            token = ROOT / f'art/monster-batch-aa/sprites/128/{asset_id}.png'
            master = ROOT / f'art/monster-batch-aa/masters/{master_name}.png'
            result = style.check_asset(token, master, asset_id, allow_grandfather=False)
            self.assertEqual(result['blocking'], [], asset_id)
            self.assertEqual(result['warnings'], [], asset_id)
            self.assertFalse(result['waived'], asset_id)
            self.assertTrue(result['passed'], asset_id)

    def test_no_pending_request_or_waiver_exists(self):
        waivers = ROOT / 'art/production/waivers'
        self.assertFalse((waivers / 'monster-batch-aa.json').exists())
        self.assertFalse((waivers / 'monster-batch-aa-PENDING-REQUEST.json').exists())

    def test_selection_matches_the_shipped_set(self):
        selection = json.loads((ROOT / 'art/monster-batch-aa/selected-masters.json').read_text())
        self.assertEqual(selection, {k: f'masters/{v}.png' for k, v in SHIPPED.items()})
        catalog = json.loads((ROOT / 'art/monster-batch-aa/catalog.json').read_text())
        self.assertEqual([a['id'] for a in catalog], list(SHIPPED))
        self.assertEqual(sorted(p.name for p in (ROOT / 'art/monster-batch-aa/masters').glob('*.png')),
                         sorted(f'{v}.png' for v in SHIPPED.values()))

    def test_manifest_and_runtime_bytes_match_the_exports(self):
        manifest = json.loads((ROOT / 'data/token-manifest.json').read_text())
        init = (ROOT / 'init.lua').read_text()
        version = '.'.join(re.search(r'addon_version\s*=\s*\{(\d+),\s*(\d+),\s*(\d+)\}', init).groups())
        self.assertEqual(manifest['version'], version)
        shipped = {a['id'] for a in manifest['assets']}
        for asset_id in SHIPPED:
            self.assertIn(asset_id, shipped)
            runtime = (ROOT / f'data/gfx/tokens/{asset_id}.png').read_bytes()
            export = (ROOT / f'art/monster-batch-aa/sprites/128/{asset_id}.png').read_bytes()
            self.assertEqual(runtime, export, asset_id)

    def test_nothing_shipped_is_dark(self):
        lum = json.loads((ROOT / 'art/monster-batch-aa/review/luminance.json').read_text())
        self.assertEqual(lum['floor_minimum_for_body'], FLOOR)
        for asset_id in SHIPPED:
            self.assertGreaterEqual(lum['assets'][asset_id], 65.0, asset_id)

    def test_review_sheets_exist(self):
        review = ROOT / 'art/monster-batch-aa/review'
        for name in ('floor-readability-48.png', 'floor-readability-48-x2.png', 'luminance.json'):
            self.assertTrue((review / name).is_file(), name)
        for group in GROUPS:
            for mode in ('color', 'grayscale'):
                self.assertTrue((review / f'{group}-{mode}-48-64-96.png').is_file(), group)


class MonsterBatchAACatalogTests(unittest.TestCase):
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
            self.assertIn(f'image="{IMAGES[asset_id]}.png"', line)
            self.assertIn(f'type="{TYPES[asset_id]}"', line)
            self.assertIn(f'subtype="{SUBTYPES[asset_id]}"', line)

    def test_flags(self):
        for asset_id in SHIPPED:
            line = self.line(asset_id)
            for flag in ('unique', 'urh_rok_form'):
                self.assertNotIn(flag, line, (asset_id, flag))
            if asset_id in DEFINE_AS:
                self.assertIn(f'define_as="{DEFINE_AS[asset_id]}"', line, asset_id)
            else:
                self.assertNotIn('define_as', line, asset_id)
            self.assertEqual('native_tall=true' in line, asset_id in TALL, asset_id)
        opted = [l for l in self.source.splitlines() if 'urh_rok_form=true' in l and '{id=' in l]
        self.assertEqual(len(opted), 5)  # unchanged by batch AA: none of its identities can reach Flame of Urh'Rok

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
        evidence = json.loads((ROOT / 'evidence/monster-batch-aa-20260930/source-contracts.json').read_text())
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
            self.assertEqual(item['native_image'], f"{IMAGES[item['id']]}.png")
            self.assertEqual(item['native_image_size'], [64, 128] if item['id'] in TALL else [64, 64], item['id'])
            self.assertEqual(item['native_tall'], item['id'] in TALL, item['id'])
            self.assertEqual('tall_body' in item, item['id'] in TALL, item['id'])
            self.assertFalse(item['unique'], item['id'])
            self.assertEqual(item['define_as'], DEFINE_AS.get(item['id']), item['id'])
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
        self.assertIn('dreadmaster', summons)
        self.assertIn('Necromancer', summons)
        self.assertIn('no per-identity `variants` entry', summons)

    def test_render_evidence_pin_matches_the_pack_files(self):
        import hashlib
        evidence = ROOT / 'evidence/monster-batch-aa-20260930/source-contracts.json'
        digest = hashlib.sha256(evidence.read_bytes()).hexdigest()
        for pack in sorted((ROOT / 'art/production/batches').glob('monster-batch-aa-*.json')):
            for asset in json.loads(pack.read_text())['assets']:
                self.assertEqual([e['sha256'] for e in asset['render_evidence']], [digest], pack.name)


class MonsterBatchAABudgetTests(unittest.TestCase):
    def test_budget(self):
        per_asset, total = {}, 0
        for call in (ROOT / 'art/production/handoffs').glob('monster-batch-aa-*/*/imagegen-calls/call-*'):
            per_asset[call.parents[1].name] = per_asset.get(call.parents[1].name, 0) + 1
            total += 1
        self.assertLessEqual(max(per_asset.values()), 3, per_asset)
        self.assertLessEqual(total, 28, per_asset)
        self.assertEqual(set(per_asset), set(SHIPPED))


if __name__ == '__main__':
    unittest.main()
