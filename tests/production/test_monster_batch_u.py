"""monster-batch-u: the twelve identities that follow the finished 12.0 story
tier in the survey-2 unscheduled list (naga tide huntress, ancient elven mummy,
ritch flamespitter, chitinous ritch, gaeramarth, ninurlhing, orc master
assassin, fire imp, ritch impaler, orc grand master assassin, naga psyren, fate
weaver). All pass the style gate with no waiver. Superseded or rejected drafts
are never selected. All are non-unique define_as-less 64x64 single images.
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
    'ritch-flamespitter': 'ritch-flamespitter-v1', 'ritch-impaler': 'ritch-impaler-v1', 'chitinous-ritch': 'chitinous-ritch-v1',
    'naga-tide-huntress': 'naga-tide-huntress-v1', 'naga-psyren': 'naga-psyren-v1', 'ancient-elven-mummy': 'ancient-elven-mummy-v1',
    'orc-master-assassin': 'orc-master-assassin-v2', 'orc-grand-master-assassin': 'orc-grand-master-assassin-v1',
    'fire-imp': 'fire-imp-v2', 'gaeramarth': 'gaeramarth-v2', 'ninurlhing': 'ninurlhing-v1', 'fate-weaver': 'fate-weaver-v1',
}
NAMES = {
    'ritch-flamespitter': 'ritch flamespitter', 'ritch-impaler': 'ritch impaler', 'chitinous-ritch': 'chitinous ritch',
    'naga-tide-huntress': 'naga tide huntress', 'naga-psyren': 'naga psyren', 'ancient-elven-mummy': 'ancient elven mummy',
    'orc-master-assassin': 'orc master assassin', 'orc-grand-master-assassin': 'orc grand master assassin', 'fire-imp': 'fire imp',
    'gaeramarth': 'gaeramarth', 'ninurlhing': 'ninurlhing', 'fate-weaver': 'fate weaver',
}
IMAGES = {
    'ritch-flamespitter': 'insect_ritch_ritch_flamespitter', 'ritch-impaler': 'insect_ritch_ritch_impaler',
    'chitinous-ritch': 'insect_ritch_chitinous_ritch', 'naga-tide-huntress': 'naga_tide_huntress', 'naga-psyren': 'naga_psyren',
    'ancient-elven-mummy': 'undead_mummy_ancient_elven_mummy', 'orc-master-assassin': 'humanoid_orc_orc_master_assassin',
    'orc-grand-master-assassin': 'humanoid_orc_orc_grand_master_assassin', 'fire-imp': 'demon_minor_fire_imp',
    'gaeramarth': 'spiderkin_spider_gaeramarth', 'ninurlhing': 'spiderkin_spider_ninurlhing', 'fate-weaver': 'spiderkin_spider_fate_weaver',
}
TYPES = {
    'ritch-flamespitter': 'insect', 'ritch-impaler': 'insect', 'chitinous-ritch': 'insect', 'naga-tide-huntress': 'humanoid',
    'naga-psyren': 'humanoid', 'ancient-elven-mummy': 'undead', 'orc-master-assassin': 'humanoid', 'orc-grand-master-assassin': 'humanoid',
    'fire-imp': 'demon', 'gaeramarth': 'spiderkin', 'ninurlhing': 'spiderkin', 'fate-weaver': 'spiderkin',
}
SUBTYPES = {
    'ritch-flamespitter': 'ritch', 'ritch-impaler': 'ritch', 'chitinous-ritch': 'ritch', 'naga-tide-huntress': 'naga',
    'naga-psyren': 'naga', 'ancient-elven-mummy': 'mummy', 'orc-master-assassin': 'orc', 'orc-grand-master-assassin': 'orc',
    'fire-imp': 'minor', 'gaeramarth': 'spider', 'ninurlhing': 'spider', 'fate-weaver': 'spider',
}
SUPERSEDED = (('orc-master-assassin', 'orc-master-assassin-v1'),
              ('fire-imp', 'fire-imp-v1'), ('gaeramarth', 'gaeramarth-v1'))
FLOOR = 45.0


class MonsterBatchUShippedTests(unittest.TestCase):
    def test_every_asset_passes_with_no_waiver(self):
        for asset_id, master_name in SHIPPED.items():
            token = ROOT / f'art/monster-batch-u/sprites/128/{asset_id}.png'
            master = ROOT / f'art/monster-batch-u/masters/{master_name}.png'
            result = style.check_asset(token, master, asset_id, allow_grandfather=False)
            self.assertEqual(result['blocking'], [], asset_id)
            self.assertEqual(result['warnings'], [], asset_id)
            self.assertFalse(result['waived'], asset_id)
            self.assertTrue(result['passed'], asset_id)

    def test_no_pending_request_or_waiver_exists(self):
        waivers = ROOT / 'art/production/waivers'
        self.assertFalse((waivers / 'monster-batch-u.json').exists())
        self.assertFalse((waivers / 'monster-batch-u-PENDING-REQUEST.json').exists())

    def test_selection_matches_the_shipped_set(self):
        selection = json.loads((ROOT / 'art/monster-batch-u/selected-masters.json').read_text())
        self.assertEqual(selection, {k: f'masters/{v}.png' for k, v in SHIPPED.items()})
        catalog = json.loads((ROOT / 'art/monster-batch-u/catalog.json').read_text())
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
            export = (ROOT / f'art/monster-batch-u/sprites/128/{asset_id}.png').read_bytes()
            self.assertEqual(runtime, export, asset_id)

    def test_superseded_drafts_are_never_selected_and_nothing_shipped_is_dark(self):
        selection = json.loads((ROOT / 'art/monster-batch-u/selected-masters.json').read_text())
        for asset_id, old in SUPERSEDED:
            self.assertNotIn(old + '.png', selection[asset_id], asset_id)
        lum = json.loads((ROOT / 'art/monster-batch-u/review/luminance.json').read_text())
        self.assertEqual(lum['floor_minimum_for_body'], FLOOR)
        for asset_id in SHIPPED:
            self.assertGreaterEqual(lum['assets'][asset_id], 65.0, asset_id)

    def test_review_sheets_exist(self):
        review = ROOT / 'art/monster-batch-u/review'
        for name in ('floor-readability-48.png', 'floor-readability-48-x2.png', 'luminance.json'):
            self.assertTrue((review / name).is_file(), name)
        for group in ('ritches', 'nagas-mummies', 'orcs-imps', 'spiders'):
            for mode in ('color', 'grayscale'):
                self.assertTrue((review / f'{group}-{mode}-48-64-96.png').is_file(), group)


class MonsterBatchUCatalogTests(unittest.TestCase):
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
            for flag in ('native_tall', 'unique', 'define_as', 'urh_rok_form'):
                self.assertNotIn(flag, line, (asset_id, flag))
        opted = [l for l in self.source.splitlines() if 'urh_rok_form=true' in l and '{id=' in l]
        self.assertEqual(len(opted), 5)  # unchanged by batch U: none of its identities can reach Flame of Urh'Rok

    def test_only_the_ritch_summon_alias_was_added(self):
        for asset_id in SHIPPED:
            self.assertNotIn(f'["{asset_id}"] = function', self.source)
            self.assertNotIn(f'{asset_id} = function', self.source)
        self.assertIn('local wild_summon_ids = {minotaur=true, ["black-jelly"]=true, ["fire-drake"]=true, ["ritch-flamespitter"]=true}', self.source)

    def test_contract_evidence_pins_source_and_native_sprite(self):
        import hashlib
        workspace = ROOT.parents[2]
        evidence = json.loads((ROOT / 'evidence/monster-batch-u-20260930/source-contracts.json').read_text())
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
            self.assertEqual(item['native_image_size'], [64, 64], item['id'])
            self.assertFalse(item['native_tall'], item['id'])
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
        self.assertIn('summoner_ritch.png', summons)
        self.assertIn('NO variants entry', summons)  # superseded by summon-alias.json, which keeps source-contracts.json byte-stable
        alias = json.loads((ROOT / 'evidence/monster-batch-u-20260930/summon-alias.json').read_text())
        self.assertEqual([c['entry'] for c in alias['covered']], ['ritch-flamespitter'])
        self.assertEqual(self.source.count('image_aliases[entry.id]'), 1)
        self.assertEqual(len(re.findall(r'^\t\["[a-z-]+"\] = \{\n\t\timage = ', self.source, re.M)), 1)

    def test_render_evidence_pin_matches_the_pack_files(self):
        import hashlib
        evidence = ROOT / 'evidence/monster-batch-u-20260930/source-contracts.json'
        digest = hashlib.sha256(evidence.read_bytes()).hexdigest()
        for pack in sorted((ROOT / 'art/production/batches').glob('monster-batch-u-*.json')):
            for asset in json.loads(pack.read_text())['assets']:
                self.assertEqual([e['sha256'] for e in asset['render_evidence']], [digest], pack.name)


class MonsterBatchUBudgetTests(unittest.TestCase):
    def test_budget(self):
        per_asset, total = {}, 0
        for call in (ROOT / 'art/production/handoffs').glob('monster-batch-u-*/*/imagegen-calls/call-*'):
            per_asset[call.parents[1].name] = per_asset.get(call.parents[1].name, 0) + 1
            total += 1
        self.assertLessEqual(max(per_asset.values()), 3, per_asset)
        self.assertLessEqual(total, 28, per_asset)
        self.assertEqual(set(per_asset), set(SHIPPED))


if __name__ == '__main__':
    unittest.main()
