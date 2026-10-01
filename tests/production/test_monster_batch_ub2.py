"""UB-2: ten flat 64x64 unique/boss identities plus one wiring-only reuse
(Ben Cruthdar, the Cursed). Unchanged style gate and 65 masked-body floor.

Static validation only. Live installation/combat validation is a separate task.
"""
import hashlib
import importlib.util
import json
import math
import os
import re
import unittest
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
ART = ROOT / 'art/monster-batch-ub2'
EVIDENCE = ROOT / 'evidence/monster-batch-ub2-20261001'
spec = importlib.util.spec_from_file_location('ub2_style', ROOT / 'tools/check_token_style.py')
style = importlib.util.module_from_spec(spec)
spec.loader.exec_module(style)

ALL_IDS = ['sun-paladin-guren', 'epoch', 'corrupted-oozemancer', 'zemekkys', 'blood-master',
           'limmir-the-jeweler', 'protector-myssil', 'rak-shor-cultist', 'shady-cornac-man', 'tannen']
WIRING = ['ben-cruthdar-the-cursed']
ACCEPTED = ALL_IDS + WIRING
DEFINES = {'sun-paladin-guren': 'SUN_PALADIN_GUREN', 'epoch': 'EPOCH',
           'corrupted-oozemancer': 'CORRUPTED_OOZEMANCER', 'zemekkys': 'ZEMEKKYS',
           'blood-master': 'RING_MASTER', 'limmir-the-jeweler': 'LIMMIR',
           'protector-myssil': 'PROTECTOR_MYSSIL', 'rak-shor-cultist': 'CULTIST_RAK_SHOR',
           'shady-cornac-man': 'ARENA_AGENT', 'tannen': 'TANNEN',
           'ben-cruthdar-the-cursed': 'BEN_CRUTHDAR'}
TYPES = {'sun-paladin-guren': ('humanoid', 'human'), 'epoch': ('elemental', 'temporal'),
         'corrupted-oozemancer': ('giant', 'troll'), 'zemekkys': ('humanoid', 'shalore'),
         'blood-master': ('humanoid', 'yaech'), 'limmir-the-jeweler': ('humanoid', 'elf'),
         'protector-myssil': ('humanoid', 'halfling'), 'rak-shor-cultist': ('humanoid', 'orc'),
         'shady-cornac-man': ('humanoid', 'human'), 'tannen': ('humanoid', 'human'),
         'ben-cruthdar-the-cursed': ('humanoid', 'human')}
GROUPS = ('sun-paladins', 'temporal', 'trolls', 'elf-story', 'yaech', 'orc-casters',
          'human-story', 'short-proportions', 'wiring-ben-cruthdar')
FLOOR = 45.0
BODY_MINIMUM = 65.0  # unchanged shipped body gate


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def accepted():
    return read(ART / 'final-admission.json')['accepted_ids']


class UB2ShippedTests(unittest.TestCase):
    def test_original_gates_without_waiver(self):
        selected = read(ART / 'selected-masters.json')
        self.assertEqual(set(selected), set(ACCEPTED))
        self.assertEqual([a['id'] for a in read(ART / 'catalog.json')], accepted())
        self.assertEqual(set(accepted()), set(ACCEPTED))
        for i, master in selected.items():
            result = style.check_asset(ART / f'sprites/128/{i}.png', ART / master, i, allow_grandfather=False)
            self.assertTrue(result['passed'], (i, result))
            self.assertEqual(result['blocking'], [], i)
            self.assertEqual(result['warnings'], [], i)
            self.assertFalse(result['waived'], i)
        self.assertFalse((ROOT / 'art/production/waivers/monster-batch-ub2.json').exists())

    def test_body_luminance_original_floor(self):
        lum = read(ART / 'review/luminance.json')
        self.assertEqual(lum['floor_minimum_for_body'], FLOOR)
        self.assertEqual(lum['body_minimum'], BODY_MINIMUM)
        for i in ACCEPTED:
            with Image.open(ART / f'sprites/128/{i}.png') as im:
                vals = [.299*r + .587*g + .114*b for y in range(128) for x in range(128)
                        for r, g, b, a in [im.getpixel((x, y))]
                        if a >= 180 and math.hypot(x + .5 - 64, y + .5 - 64) / 64 <= .55]
            measured = round(sum(vals) / len(vals), 2)
            self.assertEqual(lum['assets'][i], measured, i)
            self.assertGreaterEqual(measured, BODY_MINIMUM, i)

    def test_runtime_bytes_and_unchanged_baseline(self):
        manifest = read(ROOT / 'data/token-manifest.json')
        base = read(EVIDENCE / 'unchanged-baseline.json')
        first = next(n for n, a in enumerate(manifest['assets']) if a['batch'] == 'monster-batch-ub2')
        previous = manifest['assets'][:first]
        self.assertEqual(len(previous), base['pre_ub2_manifest_asset_count'])
        self.assertEqual(
            hashlib.sha256(json.dumps(previous, sort_keys=True, separators=(',', ':')).encode()).hexdigest(),
            base['pre_ub2_manifest_assets_sha256'])
        entries = {a['id']: a for a in manifest['assets']}
        report = {a['id']: a for a in read(ART / 'export-report.json')['assets']}
        selected = read(ART / 'selected-masters.json')
        self.assertEqual(len([a for a in manifest['assets'] if a['batch'] == 'monster-batch-ub2']), len(ACCEPTED))
        for i in ACCEPTED:
            self.assertEqual(entries[i]['batch'], 'monster-batch-ub2')
            self.assertEqual(entries[i]['runtime_sha256'], sha(ART / f'sprites/128/{i}.png'))
            self.assertEqual(entries[i]['master_sha256'], sha(ART / selected[i]))
            self.assertEqual((ROOT / f'data/gfx/tokens/{i}.png').read_bytes(),
                             (ART / f'sprites/128/{i}.png').read_bytes())
            self.assertFalse(report[i]['style_gate']['advisory_downgrade'])
            for size in (48, 64, 96, 128, 256):
                with Image.open(ART / f'sprites/{size}/{i}.png') as im:
                    self.assertEqual(im.size, (size, size))
                    self.assertEqual(im.mode, 'RGBA')
                    self.assertTrue(all(im.getpixel(p)[3] == 0
                                        for p in ((0, 0), (0, size - 1), (size - 1, 0), (size - 1, size - 1))))
        # The abomination entry and its runtime token are unchanged.
        self.assertEqual(entries['ben-cruthdar-abomination'], base['abomination'])
        self.assertEqual(sha(ROOT / 'data/gfx/tokens/ben-cruthdar-abomination.png'),
                         base['abomination']['runtime_sha256'])
        # The wiring-only Cursed token is byte-identical to the abomination token.
        self.assertEqual((ROOT / 'data/gfx/tokens/ben-cruthdar-the-cursed.png').read_bytes(),
                         (ROOT / 'data/gfx/tokens/ben-cruthdar-abomination.png').read_bytes())

    def test_review_with_shipped_siblings_and_frozen_floors(self):
        for g in GROUPS:
            for mode in ('color', 'grayscale'):
                self.assertTrue((ART / f'review/{g}-{mode}-48-64-96.png').is_file())
        for n in ('floor-readability-48.png', 'floor-readability-48-x2.png', 'floor-readability-48-x2-b.png'):
            self.assertTrue((ART / 'review' / n).exists())
        for p in read(ART / 'review/floor-source-pins.json').values():
            self.assertEqual(sha(ROOT / p['path']), p['sha256'])
        text = (ART / 'make_review_sheets.py').read_text()
        for i in ('human-sun-paladin', 'high-sun-paladin-rodmour', 'telugoroth', 'mountain-troll',
                  'elven-mage', 'archmage-tarelion', 'yaech-diver', 'orc-necromancer', 'necromancer',
                  'halfling-guard', 'ben-cruthdar-abomination'):
            self.assertIn("'" + i + "'", text)
        for label, prefixes in read(ART / 'review/luminance.json')['zone_floors'].items():
            self.assertIn(label, text)
            for prefix in prefixes:
                self.assertIn(prefix, text)


class UB2ContractsTests(unittest.TestCase):
    def test_exact_ten_flat_unique_sources_and_catalog(self):
        ev = read(EVIDENCE / 'source-contracts.json')
        ws = ROOT.parents[2]
        self.assertEqual(ev['art_ids'], ALL_IDS)
        self.assertEqual(ev['wiring_only'], WIRING)
        source = (ROOT / 'overload/mod/class/CheckerTokens.lua').read_text()
        pins = ev['auxiliary_sources'][:]
        for i in ev['identities']:
            id_ = i['id']
            self.assertTrue(i['unique'])
            self.assertEqual(i['define_as'], DEFINES[id_])
            self.assertEqual((i['type'], i['subtype']), TYPES[id_])
            self.assertEqual(i['native_image_size'], [64, 64])
            self.assertFalse(i['native_tall'])
            for key in ('shader', 'moddable_tile', 'anim', 'add_displays'):
                self.assertIsNone(i[key])
            pins += i['sources']
            sprite = ws / i['native_image_path']
            self.assertEqual(sha(sprite), i['native_image_sha256'])
            with Image.open(sprite) as im:
                self.assertEqual(list(im.size), i['native_image_size'])
            line = next(l for l in source.splitlines() if '{id="' + id_ + '",' in l)
            for key, value in (('name', i['native_name']), ('image', i['native_image']),
                               ('type', i['type']), ('subtype', i['subtype'])):
                self.assertIn(f'{key}="{value}"', line)
            self.assertIn('unique=true', line)
            self.assertIn(f'define_as="{DEFINES[id_]}"', line)
            self.assertNotIn('native_tall=', line)
            self.assertNotIn('native_shader=', line)
            self.assertNotIn('shared_name=', line)
            self.assertNotIn('define_as_alias=', line)
        for pin in pins:
            path = ws / pin['path']
            self.assertEqual(sha(path), pin['sha256'])
            if 'line' in pin:
                self.assertIn(pin['anchor'], path.read_text().splitlines()[pin['line'] - 1])

    def test_wiring_only_ben_cruthdar_reuses_abomination_token(self):
        ev = read(EVIDENCE / 'source-contracts.json')
        wiring = read(ART / 'wiring-only.json')
        source = (ROOT / 'overload/mod/class/CheckerTokens.lua').read_text()
        self.assertEqual(ev['wiring_only'], [wiring['id']])
        self.assertEqual(wiring['define_as'], 'BEN_CRUTHDAR')
        self.assertEqual(wiring['native_image'], 'npc/humanoid_human_ben_cruthdar__the_cursed.png')
        self.assertEqual(wiring['reuse']['id'], 'ben-cruthdar-abomination')
        self.assertEqual(wiring['reuse']['master'], 'monster-batch-j/masters/ben-cruthdar-abomination-v1.png')
        line = next(l for l in source.splitlines() if '{id="ben-cruthdar-the-cursed",' in l)
        self.assertIn('name="Ben Cruthdar, the Cursed"', line)
        self.assertIn('image="npc/humanoid_human_ben_cruthdar__the_cursed.png"', line)
        self.assertIn('type="humanoid"', line)
        self.assertIn('subtype="human"', line)
        self.assertIn('define_as="BEN_CRUTHDAR"', line)
        self.assertIn('unique=true', line)
        # The abomination entry has no shared_name/alias and is byte-for-byte as shipped.
        abom_line = next(l for l in source.splitlines() if '{id="ben-cruthdar-abomination",' in l)
        self.assertEqual(abom_line.strip(), read(EVIDENCE / 'unchanged-baseline.json')['abomination_catalog_line'].strip())
        # Reuse master is pinned by the source contract and the selected master.
        ident = next(i for i in ev['identities'] if i['id'] == 'ben-cruthdar-the-cursed')
        self.assertEqual(ident['reuse']['master_sha256'], sha(ROOT.parents[2] / 'game/addons/tome-checker-revised/art/monster-batch-j/masters/ben-cruthdar-abomination-v1.png'))
        self.assertEqual(read(ART / 'selected-masters.json')[wiring['id']], '../' + wiring['reuse']['master'])

    def test_official_chinese_names(self):
        names = read(ART / 'official-names.json')
        self.assertEqual(names['path'], '/workspace/tome4-chinese-translation/mod-tome.lua')
        self.assertEqual(len(names['names']), len(ALL_IDS))
        source = Path(os.environ.get('TOME_CHECKER_PINNED_TRANSLATION', names['path']))
        if not source.is_file():
            self.skipTest(f'official translation source unavailable: {source}')
        lines = source.read_text(encoding='utf-8').splitlines()
        pair = re.compile(r'^\s*t\(\s*"((?:[^"\\]|\\.)*)"\s*,\s*"((?:[^"\\]|\\.)*)"')
        for row in names['names']:
            self.assertTrue(row['hits'], row['id'])
            for hit in row['hits']:
                expected = hit['official_line']
                found = next((n for n, line in enumerate(lines, 1) if line == expected), None)
                self.assertIsNotNone(found, f"{row['native_name']!r}: recorded official line missing")
                parsed = pair.match(lines[found - 1])
                expected_pair = pair.match(expected)
                self.assertIsNotNone(parsed, f'official line {found} is not a pair')
                self.assertIsNotNone(expected_pair, f'recorded line is not a pair: {expected!r}')
                self.assertEqual(parsed.group(1), row['native_name'])
                self.assertEqual(parsed.group(2), expected_pair.group(2))

    def test_serial_builtin_provenance_and_budget(self):
        intervals = []
        outcomes = []
        for pack in (ROOT / 'art/production/handoffs').glob('monster-batch-ub2*'):
            for asset in sorted(p for p in pack.glob('*') if (p / 'inputs.json').is_file()):
                calls = sorted(asset.glob('imagegen-calls/call-*/call.json'))
                for p in calls:
                    d = read(p)
                    outcomes.append(d['outcome'])
                    self.assertEqual(d['codex_model'], 'gpt-6.1-sol')
                    self.assertTrue(d['codex_ephemeral'])
                    intervals.append((d['timestamp_started'], d['timestamp_finished']))
                    if d['outcome'] == 'recorded':
                        m = ART / 'masters' / Path(d['saved_output_path']).name
                        if not m.exists():
                            m = ART / 'superseded' / m.name
                        self.assertEqual(sha(m), d['sha256'])
                        self.assertTrue(d['provenance']['ok'])
                        self.assertTrue(d['gate_passed'])
        intervals.sort()
        for a, b in zip(intervals, intervals[1:]):
            self.assertLessEqual(a[1], b[0], 'UB-2 image calls must be serial')
        self.assertEqual(outcomes.count('recorded'), 13)
        self.assertEqual(outcomes.count('style-gate-rejected'), 2)
        self.assertEqual(len(outcomes), 15)

    def test_rework_lineage_and_no_floor_change(self):
        selected = read(ART / 'selected-masters.json')
        self.assertEqual(selected['zemekkys'], 'masters/zemekkys-rework-v1.png')
        self.assertEqual(selected['rak-shor-cultist'], 'masters/rak-shor-cultist-rework-v1.png')
        self.assertEqual(selected['sun-paladin-guren'], 'masters/sun-paladin-guren-rework-v1.png')
        for i in ('zemekkys', 'rak-shor-cultist'):
            self.assertTrue((ART / f'masters/{i}-v1.png').is_file())
            self.assertTrue((ART / f'masters/{i}-rework-v1.png').is_file())
            # First attempt passed the disc geometry but measured below the floor.
            first = read(ROOT / f'art/production/handoffs/monster-batch-ub2-{"2" if i == "zemekkys" else "3"}/{i}/imagegen-calls/call-1/call.json')
            self.assertEqual(first['outcome'], 'recorded')
            rej = read(ROOT / f'art/production/handoffs/monster-batch-ub2-{"2" if i == "zemekkys" else "3"}/{i}/imagegen-calls/call-2/call.json')
            self.assertEqual(rej['outcome'], 'style-gate-rejected')
        # Guren was redrawn on coordinator order (warm bronze-gold -> cold steel).
        self.assertTrue((ART / 'masters/sun-paladin-guren-rework-v1.png').is_file())
        self.assertTrue((ART / 'superseded/sun-paladin-guren-v1.png').is_file())
        guren_first = read(ROOT / 'art/production/handoffs/monster-batch-ub2-1/sun-paladin-guren/imagegen-calls/call-1/call.json')
        self.assertEqual(guren_first['outcome'], 'recorded')
        guren_rework = read(ROOT / 'art/production/handoffs/monster-batch-ub2-rework-2/sun-paladin-guren/imagegen-calls/call-1/call.json')
        self.assertEqual(guren_rework['outcome'], 'recorded')
        guren_ref = (read(ART / 'superseded/lineage.json')['assets']['sun-paladin-guren'])
        self.assertEqual(guren_ref['accepted'], 'art/monster-batch-ub2/masters/sun-paladin-guren-rework-v1.png')
        self.assertEqual(guren_ref['retained'][0]['path'], 'art/monster-batch-ub2/superseded/sun-paladin-guren-v1.png')
        self.assertEqual(guren_ref['retained'][0]['sha256'], sha(ROOT / 'art/monster-batch-ub2/superseded/sun-paladin-guren-v1.png'))
        admission = read(ART / 'final-admission.json')
        self.assertEqual(admission['body_minimum'], BODY_MINIMUM)
        self.assertEqual(admission['descriptive_floor_baseline'], FLOOR)
        self.assertEqual(admission['waivers'], [])
        # The sheets carry a native 2x column beside each UB-2 token.
        text = (ART / 'make_review_sheets.py').read_text()
        self.assertIn('native 2x', text)
        self.assertIn('NAT_W = NAT_H = 128', text)


if __name__ == '__main__':
    unittest.main()
