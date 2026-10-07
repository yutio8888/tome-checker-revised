"""monster-batch-t: the remaining 12.0-tier story identities (caravan merchant,
guard and porter, Lost Merchant, war dog, Yeek Wayist, Nimisil, Slasul, Draebor,
Weirdling Beast, Fortress Shadow, Pumpkin; Training Dummy stays native). All pass
the style gate with no waiver. Superseded or rejected drafts are never selected.
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
    'caravan-merchant': 'caravan-merchant-v1', 'caravan-guard': 'caravan-guard-v1', 'caravan-porter': 'caravan-porter-v1',
    'lost-merchant': 'lost-merchant-v1', 'war-dog': 'war-dog-v1', 'yeek-wayist': 'yeek-wayist-v1', 'nimisil': 'nimisil-v1',
    'slasul': 'slasul-v2', 'draebor': 'draebor-v1', 'weirdling-beast': 'weirdling-beast-v1',
    'fortress-shadow': 'fortress-shadow-v2', 'pumpkin': 'pumpkin-v1',
}
NAMES = {
    'caravan-merchant': 'caravan merchant', 'caravan-guard': 'caravan guard', 'caravan-porter': 'caravan porter',
    'lost-merchant': 'Lost Merchant', 'war-dog': 'war dog', 'yeek-wayist': 'Yeek Wayist', 'nimisil': 'Nimisil', 'slasul': 'Slasul',
    'draebor': 'Draebor, the Imp', 'weirdling-beast': 'Weirdling Beast', 'fortress-shadow': 'Fortress Shadow',
    'pumpkin': 'Pumpkin, the little kitty',
}
IMAGES = {
    'caravan-merchant': 'humanoid_human_spectator02', 'caravan-guard': 'humanoid_human_spectator', 'caravan-porter': 'humanoid_human_spectator03',
    'lost-merchant': 'humanoid_human_lost_merchant', 'war-dog': 'canine_dw', 'yeek-wayist': 'humanoid_yeek_yeek_wayist',
    'nimisil': 'spiderkin_spider_nimisil', 'slasul': 'humanoid_naga_slasul', 'draebor': 'demon_minor_draebor__the_imp',
    'weirdling-beast': 'horror_eldritch_weirdling_beast', 'fortress-shadow': 'horror_sher_tul_fortress_shadow', 'pumpkin': 'sage_kitty',
}
TYPES = {
    'caravan-merchant': 'humanoid', 'caravan-guard': 'humanoid', 'caravan-porter': 'humanoid', 'lost-merchant': 'humanoid',
    'war-dog': 'animal', 'yeek-wayist': 'humanoid', 'nimisil': 'spiderkin', 'slasul': 'humanoid', 'draebor': 'demon',
    'weirdling-beast': 'horror', 'fortress-shadow': 'horror', 'pumpkin': 'animal',
}
SUBTYPES = {
    'caravan-merchant': 'human', 'caravan-guard': 'human', 'caravan-porter': 'human', 'lost-merchant': 'human', 'war-dog': 'canine',
    'yeek-wayist': 'yeek', 'nimisil': 'spider', 'slasul': 'naga', 'draebor': 'minor', 'weirdling-beast': 'eldritch',
    'fortress-shadow': "Sher'Tul", 'pumpkin': 'feline',
}
DEFINE_AS = {
    'caravan-merchant': 'CARAVAN_MERCHANT', 'caravan-guard': 'CARAVAN_GUARD', 'caravan-porter': 'CARAVAN_PORTER', 'lost-merchant': 'MERCHANT',
    'war-dog': 'WAR_DOG', 'yeek-wayist': 'YEEK_WAYIST', 'nimisil': 'NIMISIL', 'slasul': 'SLASUL', 'draebor': 'DRAEBOR',
    'weirdling-beast': 'WEIRDLING_BEAST', 'fortress-shadow': 'BUTLER', 'pumpkin': 'KITTY',
}
UNIQUE = ('yeek-wayist', 'nimisil', 'slasul', 'draebor', 'weirdling-beast', 'pumpkin')
# Slasul: UNIQUE explicit nice_tile tall body (64x128), no native_tall flag (as Walrog).
NATIVE_TALL_SPRITE = ('slasul',)
URH_ROK = ('weirdling-beast',)
SUPERSEDED = (('fortress-shadow', 'fortress-shadow-v1'), ('slasul', 'slasul-v1'))
# Slasul v2 (2026-10-04): bare-chested repaint with the chest pearl, per desc.
FLOOR = 45.0


class MonsterBatchTShippedTests(unittest.TestCase):
    def test_every_asset_passes_with_no_waiver(self):
        for asset_id, master_name in SHIPPED.items():
            token = ROOT / f'art/monster-batch-t/sprites/128/{asset_id}.png'
            master = ROOT / f'art/monster-batch-t/masters/{master_name}.png'
            result = style.check_asset(token, master, asset_id, allow_grandfather=False)
            self.assertEqual(result['blocking'], [], asset_id)
            self.assertEqual(result['warnings'], [], asset_id)
            self.assertFalse(result['waived'], asset_id)
            self.assertTrue(result['passed'], asset_id)

    def test_no_pending_request_or_waiver_exists(self):
        waivers = ROOT / 'art/production/waivers'
        self.assertFalse((waivers / 'monster-batch-t.json').exists())
        self.assertFalse((waivers / 'monster-batch-t-PENDING-REQUEST.json').exists())

    def test_selection_matches_the_shipped_set(self):
        selection = json.loads((ROOT / 'art/monster-batch-t/selected-masters.json').read_text())
        self.assertEqual(selection, {k: f'masters/{v}.png' for k, v in SHIPPED.items()})
        catalog = json.loads((ROOT / 'art/monster-batch-t/catalog.json').read_text())
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
            export = (ROOT / f'art/monster-batch-t/sprites/128/{asset_id}.png').read_bytes()
            self.assertEqual(runtime, export, asset_id)

    def test_superseded_drafts_are_never_selected_and_nothing_shipped_is_dark(self):
        selection = json.loads((ROOT / 'art/monster-batch-t/selected-masters.json').read_text())
        for asset_id, old in SUPERSEDED:
            self.assertNotIn(old, selection[asset_id], asset_id)
        lum = json.loads((ROOT / 'art/monster-batch-t/review/luminance.json').read_text())
        self.assertEqual(lum['floor_minimum_for_body'], FLOOR)
        for asset_id in SHIPPED:
            self.assertGreater(lum['assets'][asset_id], FLOOR + 5, asset_id)

    def test_review_sheets_exist(self):
        review = ROOT / 'art/monster-batch-t/review'
        for name in ('floor-readability-48.png', 'floor-readability-48-x2.png', 'luminance.json'):
            self.assertTrue((review / name).is_file(), name)
        for group in ('humans', 'canines-small', 'bosses', 'horrors'):
            for mode in ('color', 'grayscale'):
                self.assertTrue((review / f'{group}-{mode}-48-64-96.png').is_file(), group)


class MonsterBatchTCatalogTests(unittest.TestCase):
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
            self.assertEqual('native_tall=true' in line, False, asset_id)
            self.assertEqual('unique=true' in line, asset_id in UNIQUE, asset_id)
            self.assertIn(f'subtype="{SUBTYPES[asset_id]}"', line, asset_id)
            self.assertIn(f'define_as="{DEFINE_AS[asset_id]}"', line)
            self.assertEqual('urh_rok_form=true' in line, asset_id in URH_ROK, asset_id)
        opted = [l for l in self.source.splitlines() if 'urh_rok_form=true' in l and '{id=' in l]
        self.assertEqual(len(opted), 5)  # grand corruptor, elven cultist, Rak'shor, Kor's Fury, Weirdling Beast (batch T)

    def test_contract_evidence_pins_source_and_native_sprite(self):
        import hashlib
        workspace = ROOT.parents[2]
        evidence = json.loads((ROOT / 'evidence/monster-batch-t-20260930/source-contracts.json').read_text())
        self.assertEqual(sorted(i['id'] for i in evidence['identities']), sorted(SHIPPED))
        self.assertEqual(len(evidence['runtime_mutation_scan']['hits_in_batch']), 2)
        self.assertEqual([k['name'] for k in evidence['kept_native']], ['Training Dummy'])
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
        for name in NAMES.values():
            if not name.startswith('caravan'):
                self.assertIn(name, collided)
        self.assertIn('caravan merchant / caravan guard / caravan porter', collided)
        scan = evidence['runtime_mutation_scan']
        self.assertEqual(len(scan['auto_classes_review']), 2)
        classes = ' '.join(r['class'] for r in scan['auto_classes_review'])
        for cls in ('Corruptor', 'Anorithil', 'Doomed', 'Archmage'):
            self.assertIn(cls, classes)
        self.assertIn("Flame of Urh'Rok", ' '.join(scan['hits_in_batch']))

    def test_render_evidence_pin_matches_the_pack_files(self):
        import hashlib
        evidence = ROOT / 'evidence/monster-batch-t-20260930/source-contracts.json'
        digest = hashlib.sha256(evidence.read_bytes()).hexdigest()
        for pack in sorted((ROOT / 'art/production/batches').glob('monster-batch-t-*.json')):
            for asset in json.loads(pack.read_text())['assets']:
                self.assertEqual([e['sha256'] for e in asset['render_evidence']], [digest], pack.name)


class MonsterBatchTBudgetTests(unittest.TestCase):
    def test_budget(self):
        per_asset, total = {}, 0
        for call in (ROOT / 'art/production/handoffs').glob('monster-batch-t-*/*/imagegen-calls/call-*'):
            per_asset[call.parents[1].name] = per_asset.get(call.parents[1].name, 0) + 1
            total += 1
        self.assertLessEqual(max(per_asset.values()), 3, per_asset)
        self.assertLessEqual(total, 28, per_asset)
        self.assertEqual(set(per_asset), set(SHIPPED))


if __name__ == '__main__':
    unittest.main()
