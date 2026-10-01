"""UB-1: nine native-tall unique/boss bodies; unchanged AF/UA style and 65 floor.

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
ART = ROOT / 'art/monster-batch-ub1'
EVIDENCE = ROOT / 'evidence/monster-batch-ub1-20261001'
spec = importlib.util.spec_from_file_location('ub1_style', ROOT / 'tools/check_token_style.py')
style = importlib.util.module_from_spec(spec)
spec.loader.exec_module(style)

ALL_IDS = ['high-sun-paladin-aeryn', 'fallen-sun-paladin-aeryn', 'caldizar', 'chronolith-twin', 'chronolith-clone',
           'temporal-defiler', 'corrupted-daelach', 'supreme-archmage-linaniil', 'archmage-tarelion']
DEFINES = {'high-sun-paladin-aeryn': 'HIGH_SUN_PALADIN_AERYN', 'fallen-sun-paladin-aeryn': 'FALLEN_SUN_PALADIN_AERYN',
           'caldizar': 'CALDIZAR', 'chronolith-twin': 'CHRONOLITH_TWIN', 'chronolith-clone': 'CHRONOLITH_CLONE',
           'temporal-defiler': 'TEMPORAL_DEFILER', 'corrupted-daelach': 'CORRUPTED_DAELACH',
           'supreme-archmage-linaniil': 'SUPREME_ARCHMAGE_LINANIIL', 'archmage-tarelion': 'TARELION'}
TYPES = {'high-sun-paladin-aeryn': ('humanoid', 'human'), 'fallen-sun-paladin-aeryn': ('humanoid', 'human'),
         'caldizar': ('horror', "sher'tul"), 'chronolith-twin': ('horror', 'temporal'),
         'chronolith-clone': ('horror', 'temporal'), 'temporal-defiler': ('horror', 'temporal'),
         'corrupted-daelach': ('demon', 'major'), 'supreme-archmage-linaniil': ('humanoid', 'human'),
         'archmage-tarelion': ('humanoid', 'shalore')}
GROUPS = ('sun-paladins', 'shertul', 'temporal-horrors', 'archmages', 'demons')
FLOOR = 45.0
BODY_MINIMUM = 65.0  # unchanged shipped body gate


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def accepted():
    return read(ART / 'final-admission.json')['accepted_ids']


class UB1ShippedTests(unittest.TestCase):
    def test_original_gates_without_waiver(self):
        selected = read(ART / 'selected-masters.json')
        self.assertEqual(set(selected), set(ALL_IDS))
        self.assertEqual([a['id'] for a in read(ART / 'catalog.json')], accepted())
        self.assertEqual(set(accepted()), set(ALL_IDS))
        for i, master in selected.items():
            result = style.check_asset(ART / f'sprites/128/{i}.png', ART / master, i, allow_grandfather=False)
            self.assertTrue(result['passed'], (i, result))
            self.assertEqual(result['blocking'], [], i)
            self.assertEqual(result['warnings'], [], i)
            self.assertFalse(result['waived'], i)
        self.assertFalse((ROOT / 'art/production/waivers/monster-batch-ub1.json').exists())

    def test_body_luminance_original_floor(self):
        lum = read(ART / 'review/luminance.json')
        self.assertEqual(lum['floor_minimum_for_body'], FLOOR)
        for i in ALL_IDS:
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
        first = next(n for n, a in enumerate(manifest['assets']) if a['batch'] == 'monster-batch-ub1')
        previous = manifest['assets'][:first]
        self.assertEqual(len(previous), base['pre_ub1_manifest_asset_count'])
        self.assertEqual(
            hashlib.sha256(json.dumps(previous, sort_keys=True, separators=(',', ':')).encode()).hexdigest(),
            base['pre_ub1_manifest_assets_sha256'])
        entries = {a['id']: a for a in manifest['assets']}
        report = {a['id']: a for a in read(ART / 'export-report.json')['assets']}
        selected = read(ART / 'selected-masters.json')
        self.assertEqual(len([a for a in manifest['assets'] if a['batch'] == 'monster-batch-ub1']), len(ALL_IDS))
        for i in ALL_IDS:
            self.assertEqual(entries[i]['batch'], 'monster-batch-ub1')
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

    def test_review_with_shipped_siblings_and_frozen_floors(self):
        for g in GROUPS:
            for mode in ('color', 'grayscale'):
                self.assertTrue((ART / f'review/{g}-{mode}-48-64-96.png').is_file())
        for n in ('floor-readability-48.png', 'floor-readability-48-x2.png', 'floor-readability-48-x2-b.png'):
            self.assertTrue((ART / 'review' / n).exists())
        for p in read(ART / 'review/floor-source-pins.json').values():
            self.assertEqual(sha(ROOT / p['path']), p['sha256'])
        text = (ART / 'make_review_sheets.py').read_text()
        for i in ('human-sun-paladin', 'high-sun-paladin-rodmour', 'aluin-the-fallen', 'fortress-shadow',
                  'temporal-stalker', 'elven-mage', 'necromancer', 'daelach'):
            self.assertIn("'" + i + "'", text)
        for label, prefixes in read(ART / 'review/luminance.json')['zone_floors'].items():
            self.assertIn(label, text)
            for prefix in prefixes:
                self.assertIn(prefix, text)


class UB1ContractsTests(unittest.TestCase):
    def test_exact_nine_unique_tall_sources_and_catalog(self):
        ev = read(EVIDENCE / 'source-contracts.json')
        ws = ROOT.parents[2]
        self.assertEqual([i['id'] for i in ev['identities']], ALL_IDS)
        source = (ROOT / 'overload/mod/class/CheckerTokens.lua').read_text()
        pins = ev['auxiliary_sources'][:]
        for i in ev['identities']:
            id_ = i['id']
            self.assertTrue(i['unique'])
            self.assertEqual(i['define_as'], DEFINES[id_])
            self.assertEqual((i['type'], i['subtype']), TYPES[id_])
            self.assertEqual(i['native_image_size'], [64, 128])
            self.assertTrue(i['native_tall'])
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
            if id_ == 'caldizar':
                self.assertEqual(i['define_as_alias'], 'CALDIZAR_AOADS')
                self.assertIn('define_as_alias="CALDIZAR_AOADS"', line)
                self.assertIn('shared_name=true', line)
            else:
                self.assertIsNone(i['define_as_alias'])
                self.assertNotIn('shared_name=', line)
                self.assertNotIn('define_as_alias=', line)
        for pin in pins:
            path = ws / pin['path']
            self.assertEqual(sha(path), pin['sha256'])
            if 'line' in pin:
                self.assertIn(pin['anchor'], path.read_text().splitlines()[pin['line'] - 1])
        # High Aeryn's second define site and Caldizar's second site are pinned.
        high = next(i for i in ev['identities'] if i['id'] == 'high-sun-paladin-aeryn')
        self.assertTrue(any(p['path'].endswith('town-gates-of-morning/npcs.lua') for p in high['sources']))
        cal = next(i for i in ev['identities'] if i['id'] == 'caldizar')
        self.assertTrue(any(p['path'].endswith('high-peak/npcs.lua') for p in cal['sources']))

    def test_tarelion_probe_is_pinned_render_evidence(self):
        probe = ART / 'refs/tarelion-probe.md'
        self.assertTrue(probe.is_file())
        digest = sha(ROOT / 'evidence/monster-batch-ub1-20261001/source-contracts.json')
        count = 0
        for p in (ROOT / 'art/production/batches').glob('monster-batch-ub1-[1-3].json'):
            for a in read(p)['assets']:
                count += 1
                self.assertEqual(a['render_evidence'][0]['sha256'], digest)
                if a['asset_id'] == 'archmage-tarelion':
                    self.assertTrue(any(e['path'].endswith('refs/tarelion-probe.md') for e in a['render_evidence']))
                    self.assertEqual([e['sha256'] for e in a['render_evidence'] if e['path'].endswith('tarelion-probe.md')],
                                     [sha(probe)])
                for key in ('sources', 'references'):
                    for pin in a[key]:
                        self.assertEqual(sha(ROOT.parents[2] / pin['path']), pin['sha256'])
        self.assertEqual(count, len(ALL_IDS))

    def test_shared_caldizar_token_and_no_other_shared_name(self):
        source = (ROOT / 'overload/mod/class/CheckerTokens.lua').read_text()
        cal = read(ART / 'final-admission.json')['shared_token']
        self.assertEqual(cal['id'], 'caldizar')
        self.assertEqual(cal['define_as'], ['CALDIZAR', 'CALDIZAR_AOADS'])
        shared = [l for l in source.splitlines() if 'shared_name=true' in l and '{id="' in l]
        self.assertEqual(len(shared), 3)  # shadow-claw, shadow-caster, caldizar
        self.assertTrue(any('{id="caldizar",' in l for l in shared))
        for i in ('shadow-claw', 'shadow-caster'):
            self.assertTrue(any('{id="' + i + '",' in l for l in shared))
        # The alias machinery is exercised by the isolated catalog index test.
        self.assertIn('entry.define_as_alias', source)

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
        for pack in (ROOT / 'art/production/handoffs').glob('monster-batch-ub1-*/*'):
            if not (pack / 'inputs.json').is_file():
                continue
            calls = sorted(pack.glob('imagegen-calls/call-*/call.json'))
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
            self.assertLessEqual(a[1], b[0], 'UB-1 image calls must be serial')
        self.assertEqual(outcomes.count('recorded'), 14)
        self.assertEqual(outcomes.count('provenance-rejected'), 1)
        self.assertEqual(outcomes.count('style-gate-rejected'), 1)
        self.assertEqual(len(outcomes), 16)

    def test_superseded_lineage_and_no_floor_change(self):
        selected = read(ART / 'selected-masters.json')
        self.assertEqual(selected['fallen-sun-paladin-aeryn'], 'masters/fallen-sun-paladin-aeryn-rework-v4.png')
        self.assertEqual(selected['chronolith-clone'], 'masters/chronolith-clone-rework-v1.png')
        line = read(ART / 'superseded/lineage.json')['assets']
        for id_, row in line.items():
            self.assertEqual(row['accepted'], 'art/monster-batch-ub1/' + selected[id_])
            self.assertEqual(row['accepted_sha256'], sha(ROOT / row['accepted']))
            for entry in row['retained']:
                self.assertEqual(entry['sha256'], sha(ROOT / entry['path']))
        admission = read(ART / 'final-admission.json')
        self.assertEqual(admission['body_minimum'], BODY_MINIMUM)
        self.assertEqual(admission['descriptive_floor_baseline'], FLOOR)
        self.assertEqual(admission['waivers'], [])
        # The reworked sheets carry a native 2x column beside each UB-1 token.
        text = (ART / 'make_review_sheets.py').read_text()
        self.assertIn('native 2x', text)
        self.assertIn('NAT_W, NAT_H = 128, 256', text)


if __name__ == '__main__':
    unittest.main()
