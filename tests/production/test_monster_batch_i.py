"""monster-batch-i: twelve identities (green/crimson ooze, gelatinous cube,
Malevolent Dimensional Jelly, Harkor'Zun fragment + full demon, Burb, Norgan,
slimy crawler, Spellblaze Simulacrum, Kryl-Feijan acolyte, Z'quikzshl), all
passing the style gate with no waiver. Four v1 drafts passed the gate but were
rejected by eye/luminance and are never selected.
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
    'green-ooze': 'green-ooze-v1',
    'crimson-ooze': 'crimson-ooze-v2',
    'gelatinous-cube': 'gelatinous-cube-v1',
    'malevolent-dimensional-jelly': 'malevolent-dimensional-jelly-v2',
    'harkor-zun-fragment': 'harkor-zun-fragment-v1',
    'harkor-zun': 'harkor-zun-v1',
    'burb-snow-giant-champion': 'burb-snow-giant-champion-v1',
    'norgan': 'norgan-v1',
    'slimy-crawler': 'slimy-crawler-v1',
    'spellblaze-simulacrum': 'spellblaze-simulacrum-v1',
    'kryl-feijan-acolyte': 'kryl-feijan-acolyte-v2',
    'zquikzshl': 'zquikzshl-v3',
}
NAMES = {
    "green-ooze": "green ooze",
    "crimson-ooze": "crimson ooze",
    "gelatinous-cube": "gelatinous cube",
    "malevolent-dimensional-jelly": "Malevolent Dimensional Jelly",
    "harkor-zun-fragment": "The Fragmented Essence of Harkor'Zun",
    "harkor-zun": "Harkor'Zun",
    "burb-snow-giant-champion": "Burb the snow giant champion",
    "norgan": "Norgan",
    "slimy-crawler": "slimy crawler",
    "spellblaze-simulacrum": "Spellblaze Simulacrum",
    "kryl-feijan-acolyte": "Acolyte of the Sect of Kryl-Feijan",
    "zquikzshl": "Z'quikzshl the skeletal mold",
}
UNIQUE = {'malevolent-dimensional-jelly', 'harkor-zun-fragment', 'harkor-zun', 'burb-snow-giant-champion', 'norgan', 'spellblaze-simulacrum', 'zquikzshl'}


class MonsterBatchIShippedTests(unittest.TestCase):
    def test_every_asset_passes_with_no_waiver(self):
        for asset_id, master_name in SHIPPED.items():
            token = ROOT / f'art/monster-batch-i/sprites/128/{asset_id}.png'
            master = ROOT / f'art/monster-batch-i/masters/{master_name}.png'
            result = style.check_asset(token, master, asset_id, allow_grandfather=False)
            self.assertEqual(result['blocking'], [], asset_id)
            self.assertFalse(result['waived'], asset_id)
            self.assertTrue(result['passed'], asset_id)

    def test_no_pending_request_or_waiver_exists(self):
        waivers = ROOT / 'art/production/waivers'
        self.assertFalse((waivers / 'monster-batch-i.json').exists())
        self.assertFalse((waivers / 'monster-batch-i-PENDING-REQUEST.json').exists())

    def test_selection_matches_the_shipped_set(self):
        selection = json.loads((ROOT / 'art/monster-batch-i/selected-masters.json').read_text())
        self.assertEqual(selection, {k: f'masters/{v}.png' for k, v in SHIPPED.items()})
        catalog = json.loads((ROOT / 'art/monster-batch-i/catalog.json').read_text())
        self.assertEqual([a['id'] for a in catalog], list(SHIPPED))

    def test_manifest_and_runtime_bytes_match_the_exports(self):
        manifest = json.loads((ROOT / 'data/token-manifest.json').read_text())
        # The manifest tracks the addon release, not this batch.
        init = (ROOT / 'init.lua').read_text()
        version = '.'.join(re.search(r'addon_version\s*=\s*\{(\d+),\s*(\d+),\s*(\d+)\}', init).groups())
        self.assertEqual(manifest['version'], version)
        shipped = {a['id'] for a in manifest['assets']}
        for asset_id in SHIPPED:
            self.assertIn(asset_id, shipped)
            runtime = (ROOT / f'data/gfx/tokens/{asset_id}.png').read_bytes()
            export = (ROOT / f'art/monster-batch-i/sprites/128/{asset_id}.png').read_bytes()
            self.assertEqual(runtime, export, asset_id)

    def test_dark_drafts_are_superseded_and_nothing_shipped_is_dark(self):
        selection = json.loads((ROOT / 'art/monster-batch-i/selected-masters.json').read_text())
        for asset_id in ('crimson-ooze', 'kryl-feijan-acolyte', 'malevolent-dimensional-jelly', 'zquikzshl'):
            self.assertNotIn('-v1', selection[asset_id], asset_id)
        lum = json.loads((ROOT / 'art/monster-batch-i/review/luminance.json').read_text())['assets']
        self.assertGreater(lum['kryl-feijan-acolyte'], lum['kryl-feijan-acolyte OLD v1 (superseded)'] * 1.3)
        self.assertGreater(lum['crimson-ooze'], lum['crimson-ooze OLD v1 (superseded)'] * 1.25)
        for asset_id in SHIPPED:
            self.assertGreater(lum[asset_id], 45.0, asset_id)


class MonsterBatchICatalogTests(unittest.TestCase):
    def setUp(self):
        self.source = (ROOT / 'overload/mod/class/CheckerTokens.lua').read_text()

    def test_exact_entries(self):
        for asset_id, name in NAMES.items():
            line = next((l for l in self.source.splitlines() if f'id="{asset_id}"' in l), None)
            self.assertIsNotNone(line, asset_id)
            self.assertIn(f'name="{name}"', line)
            self.assertNotIn('native_tall', line, asset_id)
            self.assertEqual('unique=true' in line, asset_id in UNIQUE, asset_id)
        for define_as in ('FULL_HARKOR_ZUN', 'BURB_SNOW_GIANT', 'NORGAN', 'SLIMY_CRAWLER', 'SPELLBLAZE_SIMULACRUM', 'ACOLYTE'):
            self.assertIn(f'define_as="{define_as}"', self.source)

    def test_contract_evidence_pins_source_and_native_sprite(self):
        evidence = json.loads((ROOT / 'evidence/monster-batch-i-20260929/source-contracts.json').read_text())
        import hashlib
        workspace = ROOT.parents[2]
        self.assertEqual(sorted(i['id'] for i in evidence['identities']), sorted(SHIPPED))
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
            self.assertTrue(sprite.is_file(), item['id'])
            self.assertEqual(hashlib.sha256(sprite.read_bytes()).hexdigest(), item['native_image_sha256'])
            self.assertEqual(item['unique'], item['id'] in UNIQUE)


class MonsterBatchIBudgetTests(unittest.TestCase):
    def test_budget_and_no_pending_waiver(self):
        per_asset, total = {}, 0
        for call in (ROOT / 'art/production/handoffs').glob('monster-batch-i-*/*/imagegen-calls/call-*'):
            per_asset[call.parents[1].name] = per_asset.get(call.parents[1].name, 0) + 1
            total += 1
        self.assertTrue(all(v <= 3 for v in per_asset.values()), per_asset)
        self.assertLessEqual(total, 26, per_asset)
        self.assertEqual(set(per_asset), set(SHIPPED))


if __name__ == '__main__':
    unittest.main()
