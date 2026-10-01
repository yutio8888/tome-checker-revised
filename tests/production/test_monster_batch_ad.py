"""monster-batch-ad (first off-list dungeon-pool batch): thirteen non-unique identities
(duathedlen, daelach, orc grand summoner, orc master wyrmic, orc mage-hunter, ritch
larva, ritch hunter, ritch hive mother, snow cat, panther, tiger, sabertooth tiger,
ice wyrm). All pass the style gate with no waiver and every masked body luminance is
at least 65 (floor unchanged; the first panther and ritch hunter exports measured
59.32 and 61.31 and were redrawn). Four are tall native_tall bodies (duathedlen,
daelach, ice wyrm, snow cat), nine are 64x64 single images; none is unique and none
binds a define_as.
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

IDS = ['duathedlen', 'daelach', 'orc-grand-summoner', 'orc-master-wyrmic', 'orc-mage-hunter', 'ritch-larva', 'ritch-hunter', 'ritch-hive-mother-pool',
       'snow-cat', 'panther', 'tiger', 'sabertooth-tiger', 'ice-wyrm']
SHIPPED = {i: i + '-v1' for i in IDS}
# tiger and orc mage-hunter: the first call returned no image path (provenance-rejected), the re-run is v2.
# panther: v1 passed the geometry gates but measured 59.32 (< 65); v2 is the redraw (v1 kept under superseded/).
# ritch hunter: v1 measured 61.31; the redraw v2 failed base_drift (+8.77, not stored); v3 is the third and last call (v1 kept under superseded/).
SHIPPED.update({'tiger': 'tiger-v2', 'orc-mage-hunter': 'orc-mage-hunter-v2', 'panther': 'panther-v2', 'ritch-hunter': 'ritch-hunter-v3'})
NAMES = {i: i.replace('-', ' ') for i in IDS}
NAMES.update({'duathedlen': 'd\u00faathedlen', 'orc-mage-hunter': 'orc mage-hunter', 'ritch-hive-mother-pool': 'ritch hive mother'})
IMAGES = {
    'duathedlen': 'npc/demon_major_duathedlen',
    'daelach': 'npc/demon_major_daelach',
    'orc-grand-summoner': 'npc/humanoid_orc_orc_grand_summoner',
    'orc-master-wyrmic': 'npc/humanoid_orc_orc_master_wyrmic',
    'orc-mage-hunter': 'npc/humanoid_orc_orc_mage_hunter',
    'ritch-larva': 'npc/insect_ritch_ritch_larva',
    'ritch-hunter': 'npc/insect_ritch_ritch_hunter',
    'ritch-hive-mother-pool': 'npc/insect_ritch_ritch_hive_mother',
    'snow-cat': 'npc/animal_feline_snow_cat',
    'panther': 'npc/animal_feline_panther',
    'tiger': 'npc/animal_feline_tiger',
    'sabertooth-tiger': 'npc/animal_feline_sabertooth_tiger',
    'ice-wyrm': 'npc/dragon_cold_ice_wyrm',
}
TYPES = {'duathedlen': 'demon', 'daelach': 'demon', 'orc-grand-summoner': 'humanoid', 'orc-master-wyrmic': 'humanoid', 'orc-mage-hunter': 'humanoid',
         'ritch-larva': 'insect', 'ritch-hunter': 'insect', 'ritch-hive-mother-pool': 'insect', 'snow-cat': 'animal', 'panther': 'animal', 'tiger': 'animal',
         'sabertooth-tiger': 'animal', 'ice-wyrm': 'dragon'}
SUBTYPES = {'duathedlen': 'major', 'daelach': 'major', 'orc-grand-summoner': 'orc', 'orc-master-wyrmic': 'orc', 'orc-mage-hunter': 'orc',
            'ritch-larva': 'ritch', 'ritch-hunter': 'ritch', 'ritch-hive-mother-pool': 'ritch', 'snow-cat': 'feline', 'panther': 'feline', 'tiger': 'feline',
            'sabertooth-tiger': 'feline', 'ice-wyrm': 'cold'}
TALL = {'duathedlen', 'daelach', 'snow-cat', 'ice-wyrm'}  # non-unique native_tall entries (explicit nice_tile)
TALL_BODY = TALL
UNIQUE = set()
DEFINE_AS = {}
LUA_NAMES = {'duathedlen': 'd\\195\\186athedlen'}  # the non-ASCII u-acute is written as UTF-8 byte escapes in CheckerTokens.lua
FLOOR = 45.0
GROUPS = ('demons-wyrms', 'cats', 'orcs-ritches')


class MonsterBatchADShippedTests(unittest.TestCase):
    def test_every_asset_passes_with_no_waiver(self):
        for asset_id, master_name in SHIPPED.items():
            token = ROOT / f'art/monster-batch-ad/sprites/128/{asset_id}.png'
            master = ROOT / f'art/monster-batch-ad/masters/{master_name}.png'
            result = style.check_asset(token, master, asset_id, allow_grandfather=False)
            self.assertEqual(result['blocking'], [], asset_id)
            self.assertEqual(result['warnings'], [], asset_id)
            self.assertFalse(result['waived'], asset_id)
            self.assertTrue(result['passed'], asset_id)

    def test_no_pending_request_or_waiver_exists(self):
        waivers = ROOT / 'art/production/waivers'
        self.assertFalse((waivers / 'monster-batch-ad.json').exists())
        self.assertFalse((waivers / 'monster-batch-ad-PENDING-REQUEST.json').exists())

    def test_selection_matches_the_shipped_set(self):
        selection = json.loads((ROOT / 'art/monster-batch-ad/selected-masters.json').read_text())
        self.assertEqual(selection, {k: f'masters/{v}.png' for k, v in SHIPPED.items()})
        catalog = json.loads((ROOT / 'art/monster-batch-ad/catalog.json').read_text())
        self.assertEqual([a['id'] for a in catalog], list(SHIPPED))
        self.assertEqual(sorted(p.name for p in (ROOT / 'art/monster-batch-ad/masters').glob('*.png')),
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
            export = (ROOT / f'art/monster-batch-ad/sprites/128/{asset_id}.png').read_bytes()
            self.assertEqual(runtime, export, asset_id)

    def test_nothing_shipped_is_dark(self):
        lum = json.loads((ROOT / 'art/monster-batch-ad/review/luminance.json').read_text())
        self.assertEqual(lum['floor_minimum_for_body'], FLOOR)
        for asset_id in SHIPPED:
            self.assertGreaterEqual(lum['assets'][asset_id], 65.0, asset_id)

    def test_dark_first_drafts_were_superseded_not_waived(self):
        # panther v1 (59.32) and ritch hunter v1 (61.31) passed the geometry gates but sat under the unchanged 65 floor.
        for name in ('panther-v1', 'ritch-hunter-v1'):
            self.assertTrue((ROOT / f'art/monster-batch-ad/superseded/{name}.png').is_file(), name)
            self.assertFalse((ROOT / f'art/monster-batch-ad/masters/{name}.png').exists(), name)

    def test_review_sheets_exist(self):
        review = ROOT / 'art/monster-batch-ad/review'
        for name in ('floor-readability-48.png', 'floor-readability-48-x2.png', 'floor-readability-48-x2-b.png', 'luminance.json'):
            self.assertTrue((review / name).is_file(), name)
        for group in GROUPS:
            for mode in ('color', 'grayscale'):
                self.assertTrue((review / f'{group}-{mode}-48-64-96.png').is_file(), group)


class MonsterBatchADCatalogTests(unittest.TestCase):
    def setUp(self):
        self.source = (ROOT / 'overload/mod/class/CheckerTokens.lua').read_text()

    def line(self, asset_id):
        line = next((l for l in self.source.splitlines() if f'{{id="{asset_id}",' in l), None)
        self.assertIsNotNone(line, asset_id)
        return line

    def test_exact_entries(self):
        for asset_id, name in NAMES.items():
            line = self.line(asset_id)
            self.assertIn('name="%s"' % LUA_NAMES.get(asset_id, name), line)
            self.assertIn(f'image="{IMAGES[asset_id]}.png"', line)
            self.assertIn(f'type="{TYPES[asset_id]}"', line)
            self.assertIn(f'subtype="{SUBTYPES[asset_id]}"', line)

    def test_flags(self):
        for asset_id in SHIPPED:
            line = self.line(asset_id)
            self.assertEqual('unique=true' in line, asset_id in UNIQUE, asset_id)
            self.assertNotIn('urh_rok_form', line, asset_id)
            if asset_id in DEFINE_AS:
                self.assertIn(f'define_as="{DEFINE_AS[asset_id]}"', line, asset_id)
            else:
                self.assertNotIn('define_as', line, asset_id)
            self.assertEqual('native_tall=true' in line, asset_id in TALL, asset_id)
        opted = [l for l in self.source.splitlines() if 'urh_rok_form=true' in l and '{id=' in l]
        self.assertEqual(len(opted), 5)  # unchanged by batch AD: none of its identities can reach Flame of Urh'Rok

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
        evidence = json.loads((ROOT / 'evidence/monster-batch-ad-20260930/source-contracts.json').read_text())
        self.assertEqual(sorted(i['id'] for i in evidence['identities']), sorted(SHIPPED))
        self.assertEqual(evidence['runtime_mutation_scan']['hits_in_batch'], [])
        self.assertEqual([k['name'] for k in evidence['kept_native']], ['Corrupted Daelach (valley-moon unique)', 'd\u00faathedlen with nicer_tiles off'])
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
            self.assertEqual(item['native_image_size'], [64, 128] if item['id'] in TALL_BODY else [64, 64], item['id'])
            self.assertEqual(item['native_tall'], item['id'] in TALL, item['id'])
            self.assertEqual('tall_body' in item, item['id'] in TALL_BODY, item['id'])
            self.assertEqual(item['unique'], item['id'] in UNIQUE, item['id'])
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
        self.assertIn('ritch-hive-mother-pool', summons)
        self.assertIn('captureRandomOrigin', summons)
        self.assertIn('Great Hive Mother', summons)
        self.assertIn('no per-identity `variants` entry', summons)

    def test_render_evidence_pin_matches_the_pack_files(self):
        import hashlib
        evidence = ROOT / 'evidence/monster-batch-ad-20260930/source-contracts.json'
        digest = hashlib.sha256(evidence.read_bytes()).hexdigest()
        for pack in sorted((ROOT / 'art/production/batches').glob('monster-batch-ad-*.json')):
            for asset in json.loads(pack.read_text())['assets']:
                self.assertEqual([e['sha256'] for e in asset['render_evidence']], [digest], pack.name)


class MonsterBatchADBudgetTests(unittest.TestCase):
    def test_budget(self):
        per_asset, total = {}, 0
        for call in (ROOT / 'art/production/handoffs').glob('monster-batch-ad-*/*/imagegen-calls/call-*'):
            per_asset[call.parents[1].name] = per_asset.get(call.parents[1].name, 0) + 1
            total += 1
        self.assertLessEqual(max(per_asset.values()), 3, per_asset)
        self.assertLessEqual(total, 26, per_asset)
        self.assertEqual(set(per_asset), set(SHIPPED))


if __name__ == '__main__':
    unittest.main()
