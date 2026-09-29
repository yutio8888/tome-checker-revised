"""monster-batch-m: survey-2 batch 4 (losgoroth, manaworm, telugoroth, gwelgoroth
trio, faeros trio incl. Fyrk, umber hulk, xorn, xaren) plus the elven cultist
(kept native by batch L, mapped here with urh_rok_form=true after the batch L
live check). All pass the style gate with no waiver. Superseded or rejected
drafts are never selected.
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
    'losgoroth': 'losgoroth-v1', 'manaworm': 'manaworm-v1', 'telugoroth': 'telugoroth-v1',
    'gwelgoroth': 'gwelgoroth-v1', 'greater-gwelgoroth': 'greater-gwelgoroth-v1',
    'ultimate-gwelgoroth': 'ultimate-gwelgoroth-v1', 'faeros': 'faeros-v1',
    'greater-faeros': 'greater-faeros-v2', 'fyrk': 'fyrk-v1', 'umber-hulk': 'umber-hulk-v1',
    'xorn': 'xorn-v1', 'xaren': 'xaren-v1', 'elven-cultist': 'elven-cultist-v1',
}
NAMES = {
    'losgoroth': 'losgoroth', 'manaworm': 'manaworm', 'telugoroth': 'telugoroth', 'gwelgoroth': 'gwelgoroth',
    'greater-gwelgoroth': 'greater gwelgoroth', 'ultimate-gwelgoroth': 'ultimate gwelgoroth', 'faeros': 'faeros',
    'greater-faeros': 'greater faeros', 'fyrk': 'Fyrk, Faeros High Guard', 'umber-hulk': 'umber hulk',
    'xorn': 'xorn', 'xaren': 'xaren', 'elven-cultist': 'elven cultist',
}
IMAGES = {
    'losgoroth': 'elemental_void_losgoroth', 'manaworm': 'elemental_void_manaworm',
    'telugoroth': 'elemental_temporal_telugoroth', 'gwelgoroth': 'elemental_air_gwelgoroth',
    'greater-gwelgoroth': 'elemental_air_greater_gwelgoroth', 'ultimate-gwelgoroth': 'elemental_air_ultimate_gwelgoroth',
    'faeros': 'elemental_fire_faeros', 'greater-faeros': 'elemental_fire_greater_faeros',
    'fyrk': 'elemental_fire_fyrk__faeros_high_guard', 'umber-hulk': 'elemental_xorn_umber_hulk',
    'xorn': 'elemental_xorn_xorn', 'xaren': 'elemental_xorn_xaren', 'elven-cultist': 'humanoid_shalore_elven_cultist',
}
TALL = ('greater-gwelgoroth', 'ultimate-gwelgoroth', 'fyrk')
NATIVE_TALL_FLAG = ('greater-gwelgoroth', 'ultimate-gwelgoroth')
SUPERSEDED = {'greater-faeros': 'greater-faeros-v1'}
FLOOR = 45.0


class MonsterBatchMShippedTests(unittest.TestCase):
    def test_every_asset_passes_with_no_waiver(self):
        for asset_id, master_name in SHIPPED.items():
            token = ROOT / f'art/monster-batch-m/sprites/128/{asset_id}.png'
            master = ROOT / f'art/monster-batch-m/masters/{master_name}.png'
            result = style.check_asset(token, master, asset_id, allow_grandfather=False)
            self.assertEqual(result['blocking'], [], asset_id)
            self.assertEqual(result['warnings'], [], asset_id)
            self.assertFalse(result['waived'], asset_id)
            self.assertTrue(result['passed'], asset_id)

    def test_no_pending_request_or_waiver_exists(self):
        waivers = ROOT / 'art/production/waivers'
        self.assertFalse((waivers / 'monster-batch-m.json').exists())
        self.assertFalse((waivers / 'monster-batch-m-PENDING-REQUEST.json').exists())

    def test_selection_matches_the_shipped_set(self):
        selection = json.loads((ROOT / 'art/monster-batch-m/selected-masters.json').read_text())
        self.assertEqual(selection, {k: f'masters/{v}.png' for k, v in SHIPPED.items()})
        catalog = json.loads((ROOT / 'art/monster-batch-m/catalog.json').read_text())
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
            export = (ROOT / f'art/monster-batch-m/sprites/128/{asset_id}.png').read_bytes()
            self.assertEqual(runtime, export, asset_id)

    def test_superseded_drafts_are_never_selected_and_nothing_shipped_is_dark(self):
        selection = json.loads((ROOT / 'art/monster-batch-m/selected-masters.json').read_text())
        for asset_id, old in SUPERSEDED.items():
            self.assertNotIn(old, selection[asset_id], asset_id)
        lum = json.loads((ROOT / 'art/monster-batch-m/review/luminance.json').read_text())
        self.assertEqual(lum['floor_minimum_for_body'], FLOOR)
        for asset_id in SHIPPED:
            self.assertGreater(lum['assets'][asset_id], FLOOR + 10, asset_id)

    def test_review_sheets_exist(self):
        review = ROOT / 'art/monster-batch-m/review'
        for name in ('floor-readability-48.png', 'floor-readability-48-x2.png', 'luminance.json'):
            self.assertTrue((review / name).is_file(), name)
        for group in ('void-temporal-air', 'fire', 'xorn-elves'):
            for mode in ('color', 'grayscale'):
                self.assertTrue((review / f'{group}-{mode}-48-64-96.png').is_file(), group)


class MonsterBatchMCatalogTests(unittest.TestCase):
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

    def test_flags(self):
        self.assertIn('unique=true', self.line('fyrk'))
        self.assertIn('define_as="FYRK"', self.line('fyrk'))
        self.assertNotIn('native_tall', self.line('fyrk'))
        for asset_id in SHIPPED:
            line = self.line(asset_id)
            self.assertEqual('native_tall=true' in line, asset_id in NATIVE_TALL_FLAG, asset_id)
            self.assertEqual('unique' in line, asset_id == 'fyrk', asset_id)
            self.assertEqual('define_as' in line, asset_id == 'fyrk', asset_id)
            self.assertEqual('urh_rok_form=true' in line, asset_id == 'elven-cultist', asset_id)
        self.assertIn('type="humanoid", subtype="shalore"', self.line('elven-cultist'))
        self.assertNotIn('demon', self.line('elven-cultist'))
        # Only the Grand Corruptor and the cultist opt into Flame of Urh'Rok.
        opted = [l for l in self.source.splitlines() if 'urh_rok_form=true' in l and '{id=' in l]
        self.assertEqual(len(opted), 4)  # grand corruptor, elven cultist, Rak'shor, Kor's Fury (2026-09-29)

    def test_contract_evidence_pins_source_and_native_sprite(self):
        import hashlib
        workspace = ROOT.parents[2]
        evidence = json.loads((ROOT / 'evidence/monster-batch-m-20260929/source-contracts.json').read_text())
        self.assertEqual(sorted(i['id'] for i in evidence['identities']), sorted(SHIPPED))
        self.assertEqual(evidence['kept_native'], [])
        self.assertEqual([h['identity'] for h in evidence['runtime_mutation_scan']['hits_in_batch']], ['elven cultist'])
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
            self.assertEqual(bool(item['native_tall']), item['id'] in NATIVE_TALL_FLAG)
            self.assertEqual(bool(item['unique']), item['id'] == 'fyrk')
            self.assertEqual(item['define_as'], 'FYRK' if item['id'] == 'fyrk' else None, item['id'])
            self.assertEqual(item['urh_rok_form'], item['id'] == 'elven-cultist')
        for pin in pinned:
            path = workspace / pin['path']
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), pin['sha256'])
            self.assertIn(pin['anchor'], path.read_text().splitlines()[pin['line'] - 1])
        collided = ' '.join(c['name'] for c in evidence['name_collisions_checked'])
        for name in ('losgoroth', 'telugoroth', 'faeros', 'elven cultist'):
            self.assertIn(name, collided)

    def test_cultist_live_evidence_backs_the_demon_form(self):
        census = (ROOT / 'evidence/monster-batch-l-live-20260929/README.md').read_text()
        self.assertIn('T_FLAME_OF_URH_ROK', census)
        self.assertIn('__old_type={humanoid,shalore}', census)


class MonsterBatchMBudgetTests(unittest.TestCase):
    def test_budget(self):
        per_asset, total = {}, 0
        for call in (ROOT / 'art/production/handoffs').glob('monster-batch-m-*/*/imagegen-calls/call-*'):
            per_asset[call.parents[1].name] = per_asset.get(call.parents[1].name, 0) + 1
            total += 1
        self.assertLessEqual(max(per_asset.values()), 3, per_asset)
        self.assertLessEqual(total, 28, per_asset)
        self.assertEqual(set(per_asset), set(SHIPPED))


if __name__ == '__main__':
    unittest.main()
