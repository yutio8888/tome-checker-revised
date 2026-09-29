"""monster-batch-q: survey-2 batch 8 (four drake hatchlings, four adult drakes,
sand-drake, Ukllmswwik the Wise, Rantha the Abomination, Briagh). All pass the
style gate with no waiver. Superseded or rejected drafts are never selected.
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
    'fire-drake-hatchling': 'fire-drake-hatchling-v1', 'cold-drake-hatchling': 'cold-drake-hatchling-v1',
    'storm-drake-hatchling': 'storm-drake-hatchling-v1', 'sand-drake': 'sand-drake-v1',
    'venom-drake-hatchling': 'venom-drake-hatchling-v1', 'rantha-abomination': 'rantha-abomination-v1',
    'briagh': 'briagh-v1', 'ukllmswwik': 'ukllmswwik-v2', 'fire-drake': 'fire-drake-v1',
    'storm-drake': 'storm-drake-v2', 'cold-drake': 'cold-drake-v1', 'venom-drake': 'venom-drake-v1',
}
NAMES = {
    'fire-drake-hatchling': 'fire drake hatchling', 'cold-drake-hatchling': 'cold drake hatchling',
    'storm-drake-hatchling': 'storm drake hatchling', 'sand-drake': 'sand-drake',
    'venom-drake-hatchling': 'venom drake hatchling', 'rantha-abomination': 'Rantha the Abomination',
    'briagh': 'Briagh, Great Sand Wyrm', 'ukllmswwik': 'Ukllmswwik the Wise', 'fire-drake': 'fire drake',
    'storm-drake': 'storm drake', 'cold-drake': 'cold drake', 'venom-drake': 'venom drake',
}
IMAGES = {
    'fire-drake-hatchling': 'dragon_fire_fire_drake_hatchling', 'cold-drake-hatchling': 'dragon_cold_cold_drake_hatchling',
    'storm-drake-hatchling': 'dragon_storm_storm_drake_hatchling', 'sand-drake': 'dragon_sand_sand_drake',
    'venom-drake-hatchling': 'dragon_venom_venom_drake_hatchling', 'rantha-abomination': 'dragon_temporal_rantha_the_abomination',
    'briagh': 'dragon_sand_briagh__great_sand_wyrm', 'ukllmswwik': 'dragon_water_ukllmswwik_the_wise',
    'fire-drake': 'dragon_fire_fire_drake', 'storm-drake': 'dragon_storm_storm_drake',
    'cold-drake': 'dragon_cold_cold_drake', 'venom-drake': 'dragon_venom_venom_drake',
}
TYPES = {asset_id: 'dragon' for asset_id in SHIPPED}
SUBTYPES = {
    'fire-drake-hatchling': 'fire', 'fire-drake': 'fire', 'cold-drake-hatchling': 'cold', 'cold-drake': 'cold',
    'storm-drake-hatchling': 'storm', 'storm-drake': 'storm', 'venom-drake-hatchling': 'venom', 'venom-drake': 'venom',
    'sand-drake': 'sand', 'briagh': 'sand', 'rantha-abomination': 'temporal', 'ukllmswwik': 'water',
}
DEFINE_AS = {'fire-drake-hatchling': 'FIRE_DRAKE_HATCHLING', 'cold-drake': 'NPC_COLD_DRAKE',
             'rantha-abomination': 'ABOMINATION_RANTHA', 'briagh': 'BRIAGH', 'ukllmswwik': 'UKLLMSWWIK'}
UNIQUE = ('rantha-abomination', 'briagh', 'ukllmswwik')
# Native sprite is 64x128 only for Rantha the Abomination and Briagh (explicit nice_tile PNGs); the rest are 64x64.
NATIVE_TALL_SPRITE = ('rantha-abomination', 'briagh')
SUPERSEDED = {'storm-drake': 'storm-drake-v1'}
FLOOR = 45.0


class MonsterBatchQShippedTests(unittest.TestCase):
    def test_every_asset_passes_with_no_waiver(self):
        for asset_id, master_name in SHIPPED.items():
            token = ROOT / f'art/monster-batch-q/sprites/128/{asset_id}.png'
            master = ROOT / f'art/monster-batch-q/masters/{master_name}.png'
            result = style.check_asset(token, master, asset_id, allow_grandfather=False)
            self.assertEqual(result['blocking'], [], asset_id)
            self.assertEqual(result['warnings'], [], asset_id)
            self.assertFalse(result['waived'], asset_id)
            self.assertTrue(result['passed'], asset_id)

    def test_no_pending_request_or_waiver_exists(self):
        waivers = ROOT / 'art/production/waivers'
        self.assertFalse((waivers / 'monster-batch-q.json').exists())
        self.assertFalse((waivers / 'monster-batch-q-PENDING-REQUEST.json').exists())

    def test_selection_matches_the_shipped_set(self):
        selection = json.loads((ROOT / 'art/monster-batch-q/selected-masters.json').read_text())
        self.assertEqual(selection, {k: f'masters/{v}.png' for k, v in SHIPPED.items()})
        catalog = json.loads((ROOT / 'art/monster-batch-q/catalog.json').read_text())
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
            export = (ROOT / f'art/monster-batch-q/sprites/128/{asset_id}.png').read_bytes()
            self.assertEqual(runtime, export, asset_id)

    def test_superseded_drafts_are_never_selected_and_nothing_shipped_is_dark(self):
        selection = json.loads((ROOT / 'art/monster-batch-q/selected-masters.json').read_text())
        for asset_id, old in SUPERSEDED.items():
            self.assertNotIn(old, selection[asset_id], asset_id)
        lum = json.loads((ROOT / 'art/monster-batch-q/review/luminance.json').read_text())
        self.assertEqual(lum['floor_minimum_for_body'], FLOOR)
        for asset_id in SHIPPED:
            self.assertGreater(lum['assets'][asset_id], FLOOR + 5, asset_id)

    def test_review_sheets_exist(self):
        review = ROOT / 'art/monster-batch-q/review'
        for name in ('floor-readability-48.png', 'floor-readability-48-x2.png', 'luminance.json'):
            self.assertTrue((review / name).is_file(), name)
        for group in ('drakes', 'sand-and-uniques'):
            for mode in ('color', 'grayscale'):
                self.assertTrue((review / f'{group}-{mode}-48-64-96.png').is_file(), group)


class MonsterBatchQCatalogTests(unittest.TestCase):
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
            self.assertNotIn('urh_rok_form', line, asset_id)
        opted = [l for l in self.source.splitlines() if 'urh_rok_form=true' in l and '{id=' in l]
        self.assertEqual(len(opted), 4)  # grand corruptor, elven cultist, Rak'shor, Kor's Fury (2026-09-29)

    def test_contract_evidence_pins_source_and_native_sprite(self):
        import hashlib
        workspace = ROOT.parents[2]
        evidence = json.loads((ROOT / 'evidence/monster-batch-q-20260929/source-contracts.json').read_text())
        self.assertEqual(sorted(i['id'] for i in evidence['identities']), sorted(SHIPPED))
        self.assertEqual(evidence['kept_native'], [])
        self.assertEqual(len(evidence['runtime_mutation_scan']['hits_in_batch']), 1)
        self.assertEqual(evidence['runtime_mutation_scan']['writers_found'], [])
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
        for name in ('fire drake hatchling', 'fire drake', 'cold drake / storm drake / venom drake', 'sand-drake',
                     'Rantha the Abomination', 'Briagh / Ukllmswwik'):
            self.assertIn(name, collided)
        scan = evidence['runtime_mutation_scan']
        self.assertEqual(len(scan['auto_classes_review']), 1)
        self.assertIn('Master Summoner', scan['auto_classes_review'][0]['class'])

    def test_render_evidence_pin_matches_the_pack_files(self):
        import hashlib
        evidence = ROOT / 'evidence/monster-batch-q-20260929/source-contracts.json'
        digest = hashlib.sha256(evidence.read_bytes()).hexdigest()
        for pack in sorted((ROOT / 'art/production/batches').glob('monster-batch-q-*.json')):
            for asset in json.loads(pack.read_text())['assets']:
                self.assertEqual([e['sha256'] for e in asset['render_evidence']], [digest], pack.name)


class MonsterBatchQBudgetTests(unittest.TestCase):
    def test_budget(self):
        per_asset, total = {}, 0
        for call in (ROOT / 'art/production/handoffs').glob('monster-batch-q-*/*/imagegen-calls/call-*'):
            per_asset[call.parents[1].name] = per_asset.get(call.parents[1].name, 0) + 1
            total += 1
        self.assertLessEqual(max(per_asset.values()), 3, per_asset)
        self.assertLessEqual(total, 28, per_asset)
        self.assertEqual(set(per_asset), set(SHIPPED))


if __name__ == '__main__':
    unittest.main()
