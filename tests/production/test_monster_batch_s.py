"""monster-batch-s: the next twelve identities under the batch R score rule
(human sun-paladin, Rodmour, Aluin, Argoniel, Elandar, Mindworm, Berethh,
Companion Warrior and Archer, Greater Mummy Lord, Kor's Fury, Borfast). All
pass the style gate with no waiver. Superseded or rejected drafts are never
selected.
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
    'human-sun-paladin': 'human-sun-paladin-v1', 'high-sun-paladin-rodmour': 'high-sun-paladin-rodmour-v1',
    'aluin-the-fallen': 'aluin-the-fallen-v3', 'argoniel': 'argoniel-v1', 'elandar': 'elandar-v1', 'mindworm': 'mindworm-v1',
    'berethh': 'berethh-v3', 'companion-warrior': 'companion-warrior-v2', 'companion-archer': 'companion-archer-v1',
    'greater-mummy-lord': 'greater-mummy-lord-v1', 'kors-fury': 'kors-fury-v1', 'borfast': 'borfast-v2',
}
NAMES = {
    'human-sun-paladin': 'human sun-paladin', 'high-sun-paladin-rodmour': 'High Sun-Paladin Rodmour',
    'aluin-the-fallen': 'Aluin the Fallen', 'argoniel': 'Argoniel', 'elandar': 'Elandar', 'mindworm': 'Mindworm',
    'berethh': 'Berethh', 'companion-warrior': 'Companion Warrior', 'companion-archer': 'Companion Archer',
    'greater-mummy-lord': 'Greater Mummy Lord', 'kors-fury': "Kor's Fury", 'borfast': 'Borfast the Broken',
}
IMAGES = {
    'human-sun-paladin': 'humanoid_human_human_sun_paladin', 'high-sun-paladin-rodmour': 'humanoid_human_high_sun_paladin_rodmour',
    'aluin-the-fallen': 'humanoid_human_aluin_the_fallen', 'argoniel': 'humanoid_human_argoniel', 'elandar': 'humanoid_shalore_elandar',
    'mindworm': 'humanoid_thalore_mindworm', 'berethh': 'humanoid_thalore_berethh', 'companion-warrior': 'humanoid_elenulach_thief',
    'companion-archer': 'humanoid_elf_elven_archer', 'greater-mummy-lord': 'undead_mummy_greater_mummy_lord',
    'kors-fury': 'undead_ghost_kor_s_fury', 'borfast': 'undead_ghoul_borfast_the_broken',
}
TYPES = {i: 'humanoid' for i in SHIPPED}
TYPES.update({'greater-mummy-lord': 'undead', 'kors-fury': 'undead', 'borfast': 'undead'})
SUBTYPES = {
    'human-sun-paladin': 'human', 'high-sun-paladin-rodmour': 'human', 'aluin-the-fallen': 'human', 'argoniel': 'human',
    'elandar': 'shalore', 'mindworm': 'thalore', 'berethh': 'thalore', 'companion-warrior': 'thalore', 'companion-archer': 'thalore',
    'greater-mummy-lord': 'mummy', 'kors-fury': 'ghost', 'borfast': 'ghoul',
}
DEFINE_AS = {
    'human-sun-paladin': 'SUN_PALADIN_DEFENDER', 'high-sun-paladin-rodmour': 'SUN_PALADIN_DEFENDER_RODMOUR', 'aluin-the-fallen': 'ALUIN',
    'argoniel': 'ARGONIEL', 'elandar': 'ELANDAR', 'mindworm': 'MINDWORM', 'berethh': 'BERETHH', 'companion-warrior': 'BERETHH_WARRIOR',
    'companion-archer': 'BERETHH_ARCHER', 'greater-mummy-lord': 'GREATER_MUMMY_LORD', 'kors-fury': 'KOR_FURY', 'borfast': 'BORFAST',
}
UNIQUE = ('high-sun-paladin-rodmour', 'aluin-the-fallen', 'mindworm', 'berethh', 'greater-mummy-lord', 'kors-fury', 'borfast')
# Argoniel and Elandar: non-unique explicit nice_tile tall bodies (64x128), native_tall=true.
NATIVE_TALL_SPRITE = ('argoniel', 'elandar')
SUPERSEDED = (('aluin-the-fallen', 'aluin-the-fallen-v1'), ('aluin-the-fallen', 'aluin-the-fallen-v2'),
              ('companion-warrior', 'companion-warrior-v1'))
FLOOR = 45.0


class MonsterBatchSShippedTests(unittest.TestCase):
    def test_every_asset_passes_with_no_waiver(self):
        for asset_id, master_name in SHIPPED.items():
            token = ROOT / f'art/monster-batch-s/sprites/128/{asset_id}.png'
            master = ROOT / f'art/monster-batch-s/masters/{master_name}.png'
            result = style.check_asset(token, master, asset_id, allow_grandfather=False)
            self.assertEqual(result['blocking'], [], asset_id)
            self.assertEqual(result['warnings'], [], asset_id)
            self.assertFalse(result['waived'], asset_id)
            self.assertTrue(result['passed'], asset_id)

    def test_no_pending_request_or_waiver_exists(self):
        waivers = ROOT / 'art/production/waivers'
        self.assertFalse((waivers / 'monster-batch-s.json').exists())
        self.assertFalse((waivers / 'monster-batch-s-PENDING-REQUEST.json').exists())

    def test_selection_matches_the_shipped_set(self):
        selection = json.loads((ROOT / 'art/monster-batch-s/selected-masters.json').read_text())
        self.assertEqual(selection, {k: f'masters/{v}.png' for k, v in SHIPPED.items()})
        catalog = json.loads((ROOT / 'art/monster-batch-s/catalog.json').read_text())
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
            export = (ROOT / f'art/monster-batch-s/sprites/128/{asset_id}.png').read_bytes()
            self.assertEqual(runtime, export, asset_id)

    def test_superseded_drafts_are_never_selected_and_nothing_shipped_is_dark(self):
        selection = json.loads((ROOT / 'art/monster-batch-s/selected-masters.json').read_text())
        for asset_id, old in SUPERSEDED:
            self.assertNotIn(old, selection[asset_id], asset_id)
        lum = json.loads((ROOT / 'art/monster-batch-s/review/luminance.json').read_text())
        self.assertEqual(lum['floor_minimum_for_body'], FLOOR)
        for asset_id in SHIPPED:
            self.assertGreater(lum['assets'][asset_id], FLOOR + 5, asset_id)

    def test_review_sheets_exist(self):
        review = ROOT / 'art/monster-batch-s/review'
        for name in ('floor-readability-48.png', 'floor-readability-48-x2.png', 'luminance.json'):
            self.assertTrue((review / name).is_file(), name)
        for group in ('knights-mages', 'keepsake-elves', 'undead'):
            for mode in ('color', 'grayscale'):
                self.assertTrue((review / f'{group}-{mode}-48-64-96.png').is_file(), group)


class MonsterBatchSCatalogTests(unittest.TestCase):
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
            self.assertEqual('native_tall=true' in line, asset_id in NATIVE_TALL_SPRITE, asset_id)
            self.assertEqual('unique=true' in line, asset_id in UNIQUE, asset_id)
            self.assertIn(f'subtype="{SUBTYPES[asset_id]}"', line, asset_id)
            self.assertIn(f'define_as="{DEFINE_AS[asset_id]}"', line)
            self.assertEqual('urh_rok_form=true' in line, asset_id == 'kors-fury', asset_id)
        opted = [l for l in self.source.splitlines() if 'urh_rok_form=true' in l and '{id=' in l]
        self.assertEqual(len(opted), 5)  # grand corruptor, elven cultist, Rak'shor, Kor's Fury, Weirdling Beast (batch T)

    def test_contract_evidence_pins_source_and_native_sprite(self):
        import hashlib
        workspace = ROOT.parents[2]
        evidence = json.loads((ROOT / 'evidence/monster-batch-s-20260929/source-contracts.json').read_text())
        self.assertEqual(sorted(i['id'] for i in evidence['identities']), sorted(SHIPPED))
        self.assertEqual(evidence['kept_native'], [])
        self.assertEqual(len(evidence['runtime_mutation_scan']['hits_in_batch']), 2)
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
            self.assertEqual(item['native_tall'], item['id'] in NATIVE_TALL_SPRITE, item['id'])
            self.assertEqual(bool(item['unique']), item['id'] in UNIQUE)
            self.assertEqual(item['define_as'], DEFINE_AS.get(item['id']), item['id'])
            self.assertEqual(item['type'], TYPES[item['id']])
        for pin in pinned:
            path = workspace / pin['path']
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), pin['sha256'])
            self.assertIn(pin['anchor'], path.read_text().splitlines()[pin['line'] - 1])
        collided = ' '.join(c['name'] for c in evidence['name_collisions_checked'])
        for name in NAMES.values():
            self.assertIn(name.split(' / ')[0], collided)
        self.assertIn('Companion Warrior / Companion Archer', collided)
        scan = evidence['runtime_mutation_scan']
        self.assertEqual(len(scan['auto_classes_review']), 4)
        classes = ' '.join(r['class'] for r in scan['auto_classes_review'])
        for cls in ('Corruptor', 'Sun Paladin', 'Bulwark', 'Solipsist'):
            self.assertIn(cls, classes)
        self.assertIn("Flame of Urh'Rok", ' '.join(scan['hits_in_batch']))

    def test_render_evidence_pin_matches_the_pack_files(self):
        import hashlib
        evidence = ROOT / 'evidence/monster-batch-s-20260929/source-contracts.json'
        digest = hashlib.sha256(evidence.read_bytes()).hexdigest()
        for pack in sorted((ROOT / 'art/production/batches').glob('monster-batch-s-*.json')):
            for asset in json.loads(pack.read_text())['assets']:
                self.assertEqual([e['sha256'] for e in asset['render_evidence']], [digest], pack.name)


class MonsterBatchSBudgetTests(unittest.TestCase):
    def test_budget(self):
        per_asset, total = {}, 0
        for call in (ROOT / 'art/production/handoffs').glob('monster-batch-s-*/*/imagegen-calls/call-*'):
            per_asset[call.parents[1].name] = per_asset.get(call.parents[1].name, 0) + 1
            total += 1
        self.assertLessEqual(max(per_asset.values()), 3, per_asset)
        self.assertLessEqual(total, 28, per_asset)
        self.assertEqual(set(per_asset), set(SHIPPED))


if __name__ == '__main__':
    unittest.main()
