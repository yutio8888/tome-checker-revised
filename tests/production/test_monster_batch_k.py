"""monster-batch-k: twelve identities of the second survey's batch 2 (squid,
ink squid, water imp, Walrog, weaver hatchling, orb spinner, giant/spitting/
chitinous spider, ghoul, drem, gigantic sandworm tunneler), all passing the
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
    'squid': 'squid-v1',
    'ink-squid': 'ink-squid-v2',
    'water-imp': 'water-imp-v1',
    'walrog': 'walrog-v2',
    'weaver-hatchling': 'weaver-hatchling-v1',
    'orb-spinner': 'orb-spinner-v1',
    'giant-spider': 'giant-spider-v1',
    'spitting-spider': 'spitting-spider-v1',
    'chitinous-spider': 'chitinous-spider-v1',
    'ghoul': 'ghoul-v1',
    'drem': 'drem-v1',
    'gigantic-sandworm-tunneler': 'gigantic-sandworm-tunneler-v2',
}
NAMES = {
    'squid': 'squid', 'ink-squid': 'ink squid', 'water-imp': 'water imp', 'walrog': 'Walrog',
    'weaver-hatchling': 'weaver hatchling', 'orb-spinner': 'orb spinner', 'giant-spider': 'giant spider',
    'spitting-spider': 'spitting spider', 'chitinous-spider': 'chitinous spider', 'ghoul': 'ghoul',
    'drem': 'drem', 'gigantic-sandworm-tunneler': 'gigantic sandworm tunneler',
}
IMAGES = {
    'squid': 'aquatic_critter_squid', 'ink-squid': 'aquatic_critter_ink_squid', 'water-imp': 'aquatic_demon_water_imp',
    'walrog': 'aquatic_demon_walrog', 'weaver-hatchling': 'spiderkin_spider_weaver_young',
    'orb-spinner': 'spiderkin_spider_orb_spinner', 'giant-spider': 'spiderkin_spider_giant_spider',
    'spitting-spider': 'spiderkin_spider_spitting_spider', 'chitinous-spider': 'spiderkin_spider_chitinous_spider',
    'ghoul': 'undead_ghoul_ghoul', 'drem': 'horror_corrupted_dremling',
    'gigantic-sandworm-tunneler': 'vermin_sandworm_gigantic_sandworm_tunneler',
}
SUPERSEDED = {'ink-squid': 'ink-squid-v1', 'walrog': 'walrog-v1'}
FLOOR = 45.0


class MonsterBatchKShippedTests(unittest.TestCase):
    def test_every_asset_passes_with_no_waiver(self):
        for asset_id, master_name in SHIPPED.items():
            token = ROOT / f'art/monster-batch-k/sprites/128/{asset_id}.png'
            master = ROOT / f'art/monster-batch-k/masters/{master_name}.png'
            result = style.check_asset(token, master, asset_id, allow_grandfather=False)
            self.assertEqual(result['blocking'], [], asset_id)
            self.assertEqual(result['warnings'], [], asset_id)
            self.assertFalse(result['waived'], asset_id)
            self.assertTrue(result['passed'], asset_id)

    def test_no_pending_request_or_waiver_exists(self):
        waivers = ROOT / 'art/production/waivers'
        self.assertFalse((waivers / 'monster-batch-k.json').exists())
        self.assertFalse((waivers / 'monster-batch-k-PENDING-REQUEST.json').exists())

    def test_selection_matches_the_shipped_set(self):
        selection = json.loads((ROOT / 'art/monster-batch-k/selected-masters.json').read_text())
        self.assertEqual(selection, {k: f'masters/{v}.png' for k, v in SHIPPED.items()})
        catalog = json.loads((ROOT / 'art/monster-batch-k/catalog.json').read_text())
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
            export = (ROOT / f'art/monster-batch-k/sprites/128/{asset_id}.png').read_bytes()
            self.assertEqual(runtime, export, asset_id)

    def test_superseded_drafts_are_never_selected_and_nothing_shipped_is_dark(self):
        selection = json.loads((ROOT / 'art/monster-batch-k/selected-masters.json').read_text())
        for asset_id, old in SUPERSEDED.items():
            self.assertNotIn(old, selection[asset_id], asset_id)
            self.assertTrue((ROOT / f'art/monster-batch-k/masters/{old}.png').is_file(), old)
        lum = json.loads((ROOT / 'art/monster-batch-k/review/luminance.json').read_text())
        self.assertEqual(lum['floor_minimum_for_body'], FLOOR)
        for asset_id in SHIPPED:
            self.assertGreater(lum['assets'][asset_id], FLOOR, asset_id)

    def test_review_sheets_exist(self):
        review = ROOT / 'art/monster-batch-k/review'
        for name in ('floor-readability-48.png', 'floor-readability-48-x2.png', 'luminance.json'):
            self.assertTrue((review / name).is_file(), name)
        for group in ('aquatic', 'spiders', 'undead-horror-worm'):
            for mode in ('color', 'grayscale'):
                self.assertTrue((review / f'{group}-{mode}-48-64-96.png').is_file(), group)


class MonsterBatchKCatalogTests(unittest.TestCase):
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
        self.assertIn('unique=true', self.line('walrog'))
        self.assertNotIn('define_as', self.line('walrog'))
        self.assertIn('native_tall=true', self.line('gigantic-sandworm-tunneler'))
        self.assertNotIn('unique', self.line('gigantic-sandworm-tunneler'))
        self.assertIn('define_as="GHOUL"', self.line('ghoul'))
        for asset_id in SHIPPED:
            if asset_id not in ('walrog', 'gigantic-sandworm-tunneler'):
                self.assertNotIn('native_tall', self.line(asset_id), asset_id)
            if asset_id != 'walrog':
                self.assertNotIn('unique', self.line(asset_id), asset_id)
            if asset_id != 'ghoul':
                self.assertNotIn('define_as', self.line(asset_id), asset_id)

    def test_contract_evidence_pins_source_and_native_sprite(self):
        import hashlib
        workspace = ROOT.parents[2]
        evidence = json.loads((ROOT / 'evidence/monster-batch-k-20260929/source-contracts.json').read_text())
        self.assertEqual(sorted(i['id'] for i in evidence['identities']), sorted(SHIPPED))
        self.assertEqual(evidence['kept_native'], [])
        for item in evidence['identities']:
            for extra in item.get('extra_sources', []):
                path = workspace / extra['path']
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), extra['sha256'])
                self.assertIn(extra['anchor'], path.read_text().splitlines()[extra['line'] - 1])
            for key in ('source', 'base_source'):
                if key not in item:
                    continue
                pin = item[key]
                path = workspace / pin['path']
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), pin['sha256'])
                self.assertIn(pin['anchor'], path.read_text().splitlines()[pin['line'] - 1])
            sprite = workspace / item['native_image_path']
            self.assertEqual(hashlib.sha256(sprite.read_bytes()).hexdigest(), item['native_image_sha256'])
            self.assertEqual(item['native_image'], f"npc/{IMAGES[item['id']]}.png")
            tall = item['id'] in ('walrog', 'gigantic-sandworm-tunneler')
            self.assertEqual(item['native_image_size'], [64, 128] if tall else [64, 64], item['id'])
            self.assertEqual(bool(item['native_tall']), item['id'] == 'gigantic-sandworm-tunneler')
            self.assertEqual(bool(item['unique']), item['id'] == 'walrog')
        collided = {c['name'] for c in evidence['name_collisions_checked']}
        self.assertTrue({'giant spider', 'ghoul', 'drem'} <= collided)


class MonsterBatchKBudgetTests(unittest.TestCase):
    def test_budget(self):
        per_asset, total = {}, 0
        for call in (ROOT / 'art/production/handoffs').glob('monster-batch-k-*/*/imagegen-calls/call-*'):
            per_asset[call.parents[1].name] = per_asset.get(call.parents[1].name, 0) + 1
            total += 1
        self.assertTrue(all(v <= 3 for v in per_asset.values()), per_asset)
        self.assertLessEqual(total, 26, per_asset)
        self.assertEqual(set(per_asset), set(SHIPPED))


if __name__ == '__main__':
    unittest.main()
