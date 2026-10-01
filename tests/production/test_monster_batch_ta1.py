"""TA-1: thirteen town residents; unchanged AF/UA style and 65 body floor.

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
ART = ROOT / 'art/monster-batch-ta1'
EVIDENCE = ROOT / 'evidence/monster-batch-ta1-20261001'
spec = importlib.util.spec_from_file_location('ta1_style', ROOT / 'tools/check_token_style.py')
style = importlib.util.module_from_spec(spec)
spec.loader.exec_module(style)

ALL_IDS = ['apprentice-mage','pyromancer','cryomancer','geomancer','tempest','human-guard','derth-guard',
           'last-hope-guard','halfling-guard','dwarven-guard','elvala-guard','slaver','enthralled-slave']
TALL = {'pyromancer','cryomancer','geomancer','tempest'}
SUBTYPES = {'halfling-guard':'halfling','dwarven-guard':'dwarf','elvala-guard':'shalore','slaver':'yaech'}
GROUPS = ('angolwen-mages','guards','ring-of-blood')
ZONE_FLOORS = {
    'apprentice-mage': ['town road', 'town fields', 'gothic'], 'human-guard': ['town road', 'town fields', 'sand'],
    'pyromancer': ['town fields', 'gothic'], 'cryomancer': ['town fields', 'snow'], 'geomancer': ['town fields', 'korpul'],
    'tempest': ['town fields', 'gloomy'], 'derth-guard': ['town fields', 'grass'], 'last-hope-guard': ['town road', 'burnt'],
    'halfling-guard': ['town road', 'grass'], 'dwarven-guard': ['gothic', 'korpul'], 'elvala-guard': ['sand', 'town road'],
    'slaver': ['cave', 'burnt'], 'enthralled-slave': ['cave', 'town road'],
}
FLOOR = 45.0
BODY_MINIMUM = 65.0  # unchanged shipped body gate


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def accepted():
    return read(ART / 'final-admission.json')['accepted_ids']


class TA1ShippedTests(unittest.TestCase):
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
        self.assertFalse((ROOT / 'art/production/waivers/monster-batch-ta1.json').exists())

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
        first = next(n for n, a in enumerate(manifest['assets']) if a['batch'] == 'monster-batch-ta1')
        previous = manifest['assets'][:first]
        self.assertEqual(len(previous), base['pre_ta1_manifest_asset_count'])
        self.assertEqual(
            hashlib.sha256(json.dumps(previous, sort_keys=True, separators=(',', ':')).encode()).hexdigest(),
            base['pre_ta1_manifest_assets_sha256'])
        entries = {a['id']: a for a in manifest['assets']}
        report = {a['id']: a for a in read(ART / 'export-report.json')['assets']}
        selected = read(ART / 'selected-masters.json')
        for i in ALL_IDS:
            self.assertEqual(entries[i]['batch'], 'monster-batch-ta1')
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
        for i in ('elven-mage', 'orc-pyromancer', 'caravan-guard', 'human-sun-paladin', 'norgan',
                  'yaech-hunter', 'yaech-diver', 'bandit'):
            self.assertIn("'" + i + "'", text)
        for label, prefixes in ZONE_FLOORS.items():
            self.assertIn(label, text)
            for prefix in prefixes:
                self.assertIn(prefix, text)


class TA1ContractsTests(unittest.TestCase):
    def test_exact_thirteen_resident_sources_and_catalog(self):
        ev = read(EVIDENCE / 'source-contracts.json')
        ws = ROOT.parents[2]
        self.assertEqual([i['id'] for i in ev['identities']], ALL_IDS)
        source = (ROOT / 'overload/mod/class/CheckerTokens.lua').read_text()
        pins = ev['auxiliary_sources'][:]
        for i in ev['identities']:
            id_ = i['id']
            self.assertFalse(i['unique'])
            self.assertIsNone(i['define_as'])
            self.assertEqual(i['type'], 'humanoid')
            self.assertEqual(i['subtype'], SUBTYPES.get(id_, 'human'))
            self.assertEqual(i['native_image_size'], [64, 128] if id_ in TALL else [64, 64])
            self.assertEqual(i['native_tall'], id_ in TALL)
            self.assertEqual('tall_body' in i, id_ in TALL)
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
            self.assertEqual('native_tall=true' in line, id_ in TALL)
            self.assertNotIn('define_as', line)
            self.assertNotIn('unique=', line)
            self.assertNotIn('native_shader', line)
            self.assertNotIn('urh_rok_form', line)
        for pin in pins:
            path = ws / pin['path']
            self.assertEqual(sha(path), pin['sha256'])
            self.assertIn(pin['anchor'], path.read_text().splitlines()[pin['line'] - 1])
        text = str(ev['summons_and_same_body_copies']) + str(ev['auxiliary_sources'])
        for term in ('make_escort', 'enthralled slave', 'nice_tile', 'no define_as'):
            self.assertIn(term, text)

    def test_slaver_escort_same_body_contract(self):
        # The escort is the same body, so exact identity is sufficient; pin the
        # native constructor so a silent name/type/image change fails the test.
        path = ROOT.parents[2] / 'game/modules/tome/data/zones/ring-of-blood/npcs.lua'
        text = path.read_text()
        self.assertIn('{type="humanoid", subtype="human", name="enthralled slave", number=2, post=function(self, m)', text)
        self.assertIn('newEntity{ base = "BASE_NPC_SLAVER",\n\tname = "enthralled slave"', text)

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
        repaired = []
        for pack in (ROOT / 'art/production/handoffs').glob('monster-batch-ta1-*/*'):
            if not (pack / 'inputs.json').is_file():
                continue
            calls = sorted(pack.glob('imagegen-calls/call-*/call.json'))
            task = read(pack / 'inputs.json')['task']
            self.assertLessEqual(len(calls), task['max_attempts'])
            for p in calls:
                d = read(p)
                self.assertEqual(d['codex_model'], 'gpt-6.1-sol')
                self.assertTrue(d['codex_ephemeral'])
                intervals.append((d['timestamp_started'], d['timestamp_finished']))
                if d['review_source'] == 'external-review':
                    repaired.append(d['asset_id'])
                if d['outcome'] == 'recorded':
                    m = ART / 'masters' / Path(d['saved_output_path']).name
                    if not m.exists():
                        m = ART / 'superseded' / m.name
                    self.assertEqual(sha(m), d['sha256'])
                    self.assertTrue(d['provenance']['ok'])
                    self.assertTrue(d['gate_passed'])
        intervals.sort()
        for a, b in zip(intervals, intervals[1:]):
            self.assertLessEqual(a[1], b[0], 'TA-1 image calls must be serial')
        self.assertEqual(sorted(set(repaired)), ['derth-guard', 'human-guard', 'pyromancer'])

    def test_generation_pins_and_render_evidence(self):
        digest = sha(EVIDENCE / 'source-contracts.json')
        count = 0
        for p in (ROOT / 'art/production/batches').glob('monster-batch-ta1-[1-5].json'):
            for a in read(p)['assets']:
                count += 1
                self.assertEqual(a['render_evidence'][0]['sha256'], digest)
                for key in ('sources', 'references'):
                    for pin in a[key]:
                        self.assertEqual(sha(ROOT.parents[2] / pin['path']), pin['sha256'])
        self.assertEqual(count, len(ALL_IDS))
        rework = read(ROOT / 'art/production/batches/monster-batch-ta1-rework-1.json')['assets']
        self.assertEqual([a['asset_id'] for a in rework], ['human-guard'])
        for a in rework:
            self.assertEqual({k: a['refinement'][k] for k in ('supersedes', 'previous_batch')},
                             {'supersedes': 'human-guard', 'previous_batch': 'monster-batch-ta1-2'})
            self.assertGreaterEqual(len(a['refinement']['design_change_reason']), 80)
            for pin in a['refinement']['evidence']:
                self.assertEqual(sha(ROOT.parents[2] / pin['path']), pin['sha256'])
            self.assertEqual(a['render_evidence'][0]['sha256'], digest)
            for key in ('sources', 'references', 'render_evidence'):
                for pin in a[key]:
                    self.assertEqual(sha(ROOT.parents[2] / pin['path']), pin['sha256'])
        for pack in (ROOT / 'art/production/handoffs').glob('monster-batch-ta1-*/*'):
            if not (pack / 'inputs.json').is_file():
                continue
            task = read(pack / 'inputs.json')['task']
            for pin in task['sources']:
                self.assertEqual(sha(ROOT.parents[2] / pin['path']), pin['sha256'])
            for pin in task['references'] + task['render_evidence']:
                self.assertEqual(sha(ROOT.parents[2] / pin['path']), pin['sha256'])

    def test_repaired_masters_and_superseded_lineage(self):
        selected = read(ART / 'selected-masters.json')
        packs = {p.name: p for p in (ROOT / 'art/production/handoffs').glob('monster-batch-ta1-*/*') if p.is_dir()}
        # pyromancer and derth-guard used the two standard attempts (v1 -> v2).
        for i in ('pyromancer', 'derth-guard'):
            self.assertEqual(selected[i], f'masters/{i}-v2.png')
            self.assertTrue((ART / 'masters' / f'{i}-v1.png').is_file())
            self.assertNotEqual(sha(ART / selected[i]), sha(ART / f'masters/{i}-v1.png'))
            self.assertTrue((packs[i] / 'repair/review.json').is_file())
            self.assertTrue((packs[i] / 'receipts/attempt-2.json').is_file())
            review = read(packs[i] / 'repair/review.json')
            self.assertEqual(set(review), {'review_scale', 'observed_failure', 'required_change', 'invariants'})
        # human-guard was separately reworked by coordinator request into v3; the
        # original v2 lineage under monster-batch-ta1-2 is retained, not deleted.
        self.assertEqual(selected['human-guard'], 'masters/human-guard-v3.png')
        for suffix in ('v1', 'v2', 'v3'):
            self.assertTrue((ART / 'masters' / f'human-guard-{suffix}.png').is_file())
        old_pack = ROOT / 'art/production/handoffs/monster-batch-ta1-2/human-guard'
        rework_pack = ROOT / 'art/production/handoffs/monster-batch-ta1-rework-1/human-guard'
        self.assertTrue((old_pack / 'receipts/attempt-2.json').is_file())
        self.assertTrue((rework_pack / 'receipts/attempt-1.json').is_file())
        self.assertEqual(sha(ART / selected['human-guard']), sha(ART / 'masters/human-guard-v3.png'))
        self.assertNotEqual(sha(ART / 'masters/human-guard-v2.png'), sha(ART / 'masters/human-guard-v3.png'))
        coord = read(ART / 'rework/coordinator-rework-human-guard.json')
        self.assertIn('human-guard', coord['rework'])
        self.assertNotIn('metric/128px', coord['rework']['human-guard'])
        for i in set(ALL_IDS) - {'pyromancer', 'derth-guard', 'human-guard'}:
            self.assertEqual(selected[i], f'masters/{i}-v1.png')


if __name__ == '__main__':
    unittest.main()
