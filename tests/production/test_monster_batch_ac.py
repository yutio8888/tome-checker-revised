"""monster-batch-ac (the final batch): the seventeen identities that remain in the
survey-2 unscheduled list after batch AB (Aletta Soultorn, ruin banshee, Filio
Flightfond, orc high pyromancer, orc high cryomancer, Glacial Legion, Arch Zephyr,
Rotting Titan, Heavy Sentinel, Void Spectre, oozing horror, abyssal horror,
ungolmor, umbral horror, vampire lord, degenerated ogric mass, ogric
abomination). All pass the style gate with no waiver and every masked body
luminance is at least 65 (floor unchanged), except abyssal horror, which was
deliberately repainted pitch-black on 2026-10-04 (v2, one pair of deep red eyes)
to match its own desc; its readability is asserted by measured body darkness
against the superseded bright v1 rather than the retired luminance floor. Four
are non-unique native_tall bodies, five are unique tall bodies, eight are 64x64
single images (two of them unique); six bind a define_as.
"""
import importlib.util
import json
import math
import re
import unittest
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('check_token_style', ROOT / 'tools/check_token_style.py')
style = importlib.util.module_from_spec(spec)
spec.loader.exec_module(style)

IDS = ['aletta-soultorn', 'ruin-banshee', 'filio-flightfond', 'orc-high-pyromancer', 'orc-high-cryomancer', 'glacial-legion', 'arch-zephyr', 'rotting-titan',
       'heavy-sentinel', 'void-spectre', 'oozing-horror', 'abyssal-horror', 'ungolmor', 'umbral-horror', 'vampire-lord', 'degenerated-ogric-mass', 'ogric-abomination']
SHIPPED = {i: i + '-v1' for i in IDS}
SHIPPED['vampire-lord'] = 'vampire-lord-v2'  # v1 (pack 8) passed every numeric gate but was a small dull mustard mass at 48px (masked luminance 70.4); v1 is kept under superseded/
SHIPPED['abyssal-horror'] = 'abyssal-horror-v2'  # user decision 2026-10-04: pitch-black single-red-eye-pair repaint matching the desc; v1 (bright blue-violet, multi-eyed) is kept under superseded/
NAMES = {i: i.replace('-', ' ') for i in IDS}
NAMES.update({'aletta-soultorn': 'Aletta Soultorn', 'filio-flightfond': 'Filio Flightfond', 'glacial-legion': 'Glacial Legion', 'arch-zephyr': 'Arch Zephyr',
              'rotting-titan': 'Rotting Titan', 'heavy-sentinel': 'Heavy Sentinel', 'void-spectre': 'Void Spectre'})
IMAGES = {
    'aletta-soultorn': 'npc/undead_ghost_aletta_soultorn',
    'ruin-banshee': 'npc/undead_ghost_ruin_banshee',
    'filio-flightfond': 'npc/undead_skeleton_filio_flightfond',
    'orc-high-pyromancer': 'npc/humanoid_orc_orc_high_pyromancer',
    'orc-high-cryomancer': 'npc/humanoid_orc_orc_high_cryomancer',
    'glacial-legion': 'npc/undead_ghost_glacial_legion',
    'arch-zephyr': 'npc/undead_vampire_arch_zephyr',
    'rotting-titan': 'npc/undead_ghoul_rotting_titan',
    'heavy-sentinel': 'npc/undead_giant_heavy_sentinel',
    'void-spectre': 'npc/undead_wight_void_spectre',
    'oozing-horror': 'npc/horror_eldritch_oozing_horror',
    'abyssal-horror': 'npc/horror_aquatic_abyssal_horror',
    'ungolmor': 'npc/spiderkin_spider_ungolmor',
    'umbral-horror': 'npc/horror_eldritch_umbral_horror',
    'vampire-lord': 'npc/vampire_lord',
    'degenerated-ogric-mass': 'npc/giant_ogre_degenerated_ogric_mass',
    'ogric-abomination': 'npc/giant_ogre_ogric_abomination',
}
TYPES = {'aletta-soultorn': 'undead', 'ruin-banshee': 'undead', 'filio-flightfond': 'undead', 'orc-high-pyromancer': 'humanoid', 'orc-high-cryomancer': 'humanoid',
         'glacial-legion': 'undead', 'arch-zephyr': 'undead', 'rotting-titan': 'undead', 'heavy-sentinel': 'undead', 'void-spectre': 'undead', 'oozing-horror': 'horror',
         'abyssal-horror': 'horror', 'ungolmor': 'spiderkin', 'umbral-horror': 'horror', 'vampire-lord': 'undead', 'degenerated-ogric-mass': 'giant', 'ogric-abomination': 'giant'}
SUBTYPES = {'aletta-soultorn': 'ghost', 'ruin-banshee': 'ghost', 'filio-flightfond': 'skeleton', 'orc-high-pyromancer': 'orc', 'orc-high-cryomancer': 'orc',
            'glacial-legion': 'ghost', 'arch-zephyr': 'vampire', 'rotting-titan': 'ghoul', 'heavy-sentinel': 'giant', 'void-spectre': 'wight', 'oozing-horror': 'eldritch',
            'abyssal-horror': 'aquatic', 'ungolmor': 'spider', 'umbral-horror': 'eldritch', 'vampire-lord': 'vampire', 'degenerated-ogric-mass': 'ogre', 'ogric-abomination': 'ogre'}
DEFINE_AS = {'aletta-soultorn': 'ALETTA', 'filio-flightfond': 'FILIO', 'glacial-legion': 'GLACIAL_LEGION', 'arch-zephyr': 'ARCH_ZEPHYR',
             'rotting-titan': 'ROTTING_TITAN', 'heavy-sentinel': 'HEAVY_SENTINEL'}
UNIQUE = {'aletta-soultorn', 'filio-flightfond', 'glacial-legion', 'arch-zephyr', 'rotting-titan', 'heavy-sentinel', 'void-spectre'}
UNIQUE_TALL = {'glacial-legion', 'arch-zephyr', 'rotting-titan', 'heavy-sentinel', 'void-spectre'}
TALL = {'abyssal-horror', 'umbral-horror', 'degenerated-ogric-mass', 'ogric-abomination'}  # non-unique native_tall entries
TALL_BODY = TALL | UNIQUE_TALL  # every 64x128 body
FLOOR = 45.0
GROUPS = ('ghosts-skeletons-vampires', 'orcs-giants-wights', 'horrors-spiders')


class MonsterBatchACShippedTests(unittest.TestCase):
    def test_every_asset_passes_with_no_waiver(self):
        for asset_id, master_name in SHIPPED.items():
            token = ROOT / f'art/monster-batch-ac/sprites/128/{asset_id}.png'
            master = ROOT / f'art/monster-batch-ac/masters/{master_name}.png'
            result = style.check_asset(token, master, asset_id, allow_grandfather=False)
            self.assertEqual(result['blocking'], [], asset_id)
            self.assertEqual(result['warnings'], [], asset_id)
            self.assertFalse(result['waived'], asset_id)
            self.assertTrue(result['passed'], asset_id)

    def test_no_pending_request_or_waiver_exists(self):
        waivers = ROOT / 'art/production/waivers'
        self.assertFalse((waivers / 'monster-batch-ac.json').exists())
        self.assertFalse((waivers / 'monster-batch-ac-PENDING-REQUEST.json').exists())

    def test_selection_matches_the_shipped_set(self):
        selection = json.loads((ROOT / 'art/monster-batch-ac/selected-masters.json').read_text())
        self.assertEqual(selection, {k: f'masters/{v}.png' for k, v in SHIPPED.items()})
        catalog = json.loads((ROOT / 'art/monster-batch-ac/catalog.json').read_text())
        self.assertEqual([a['id'] for a in catalog], list(SHIPPED))
        self.assertEqual(sorted(p.name for p in (ROOT / 'art/monster-batch-ac/masters').glob('*.png')),
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
            export = (ROOT / f'art/monster-batch-ac/sprites/128/{asset_id}.png').read_bytes()
            self.assertEqual(runtime, export, asset_id)

    def test_nothing_shipped_is_dark(self):
        lum = json.loads((ROOT / 'art/monster-batch-ac/review/luminance.json').read_text())
        self.assertEqual(lum['floor_minimum_for_body'], FLOOR)
        for asset_id in SHIPPED:
            if asset_id == 'abyssal-horror':
                # Deliberate 2026-10-04 black repaint; the historical v1 luminance
                # record no longer describes the shipped token (see the test below).
                continue
            self.assertGreaterEqual(lum['assets'][asset_id], 65.0, asset_id)

    def test_abyssal_horror_repaint_is_darker_than_the_superseded_token(self):
        # User decision 2026-10-04: the shipped v1 was a bright blue-violet
        # multi-eyed tentacle blob that contradicted abyssal horror's own desc
        # ('This pitch black form is shrouded in darkness. All you can make out
        # are a pair of deep red eyes, hidden behind a mass of tentacles.').
        # The v2 repaint is pitch-black with exactly one pair of deep red eyes;
        # readability comes from internal sheen and a cool rim, not a bright body.
        def body_luminance(path):
            image = Image.open(path).convert('RGBA')
            size = image.width
            values = []
            for y in range(size):
                for x in range(size):
                    r, g, b, a = image.getpixel((x, y))
                    if a >= 180 and math.hypot(x + .5 - size / 2, y + .5 - size / 2) <= 0.55 * size / 2:
                        values.append(0.299 * r + 0.587 * g + 0.114 * b)
            return sum(values) / len(values)
        new = ROOT / 'art/monster-batch-ac/sprites/128/abyssal-horror.png'
        old = ROOT / 'art/monster-batch-ac/superseded/abyssal-horror-v1-runtime-128.png'
        self.assertTrue(old.is_file(), 'the superseded bright token must be kept for provenance')
        self.assertNotEqual(new.read_bytes(), old.read_bytes())
        self.assertLess(body_luminance(new), body_luminance(old) - 20)
        selection = json.loads((ROOT / 'art/monster-batch-ac/selected-masters.json').read_text())
        self.assertEqual(selection['abyssal-horror'], 'masters/abyssal-horror-v2.png')

    def test_review_sheets_exist(self):
        review = ROOT / 'art/monster-batch-ac/review'
        for name in ('floor-readability-48.png', 'floor-readability-48-x2.png', 'floor-readability-48-x2-b.png', 'luminance.json'):
            self.assertTrue((review / name).is_file(), name)
        for group in GROUPS:
            for mode in ('color', 'grayscale'):
                self.assertTrue((review / f'{group}-{mode}-48-64-96.png').is_file(), group)


class MonsterBatchACCatalogTests(unittest.TestCase):
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
            self.assertEqual('unique=true' in line, asset_id in UNIQUE, asset_id)
            self.assertNotIn('urh_rok_form', line, asset_id)
            if asset_id in DEFINE_AS:
                self.assertIn(f'define_as="{DEFINE_AS[asset_id]}"', line, asset_id)
            else:
                self.assertNotIn('define_as', line, asset_id)
            self.assertEqual('native_tall=true' in line, asset_id in TALL, asset_id)
        opted = [l for l in self.source.splitlines() if 'urh_rok_form=true' in l and '{id=' in l]
        self.assertEqual(len(opted), 5)  # unchanged by batch AC: none of its identities can reach Flame of Urh'Rok

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
        evidence = json.loads((ROOT / 'evidence/monster-batch-ac-20260930/source-contracts.json').read_text())
        self.assertEqual(sorted(i['id'] for i in evidence['identities']), sorted(SHIPPED))
        self.assertEqual(evidence['runtime_mutation_scan']['hits_in_batch'], [])
        self.assertEqual([k['name'] for k in evidence['kept_native']], ['Vilespawn (Corpathus artifact minion)'])
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
        self.assertIn('Vilespawn', summons)
        self.assertIn('captureRandomOrigin', summons)
        self.assertIn('Void Spectre', summons)
        self.assertIn('no per-identity `variants` entry', summons)

    def test_render_evidence_pin_matches_the_pack_files(self):
        import hashlib
        evidence = ROOT / 'evidence/monster-batch-ac-20260930/source-contracts.json'
        digest = hashlib.sha256(evidence.read_bytes()).hexdigest()
        for pack in sorted((ROOT / 'art/production/batches').glob('monster-batch-ac-*.json')):
            for asset in json.loads(pack.read_text())['assets']:
                self.assertEqual([e['sha256'] for e in asset['render_evidence']], [digest], pack.name)


class MonsterBatchACBudgetTests(unittest.TestCase):
    def test_budget(self):
        per_asset, total = {}, 0
        for call in (ROOT / 'art/production/handoffs').glob('monster-batch-ac-*/*/imagegen-calls/call-*'):
            per_asset[call.parents[1].name] = per_asset.get(call.parents[1].name, 0) + 1
            total += 1
        self.assertLessEqual(max(per_asset.values()), 3, per_asset)
        self.assertLessEqual(total, 34, per_asset)
        self.assertEqual(set(per_asset), set(SHIPPED))


if __name__ == '__main__':
    unittest.main()
