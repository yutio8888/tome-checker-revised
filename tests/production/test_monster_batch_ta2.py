"""TA-2: second town-resident batch; thirteen new non-unique bodies (two
native-tall) plus one wiring-only reuse (elven archer). Unchanged style gate and
65 masked-body floor.

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
ART = ROOT / 'art/monster-batch-ta2'
EVIDENCE = ROOT / 'evidence/monster-batch-ta2-20261001'
spec = importlib.util.spec_from_file_location('ta2_style', ROOT / 'tools/check_token_style.py')
style = importlib.util.module_from_spec(spec)
spec.loader.exec_module(style)

ART_IDS = ['human-citizen', 'halfling-citizen', 'human-farmer', 'halfling-gardener', 'lumberjack',
           'halfling-slinger', 'dwarven-earthwarden', 'yeek-mindslayer', 'yeek-psionic', 'thalore-hunter',
           'thalore-wilder', 'elven-sun-mage', 'shalore-rune-master']
WIRING = ['elven-archer']
ACCEPTED = ART_IDS + WIRING
TALL = {'yeek-mindslayer', 'thalore-wilder'}
SUBTYPES = {'halfling-citizen': 'halfling', 'halfling-gardener': 'halfling', 'halfling-slinger': 'halfling',
            'dwarven-earthwarden': 'dwarf', 'yeek-mindslayer': 'yeek', 'yeek-psionic': 'yeek',
            'thalore-hunter': 'thalore', 'thalore-wilder': 'thalore', 'elven-sun-mage': 'elf',
            'shalore-rune-master': 'shalore', 'elven-archer': 'elf'}
GROUPS = ('citizens', 'yeeks', 'dwarves', 'thalore', 'elves', 'wiring-elven-archer')
FLOOR = 45.0
BODY_MINIMUM = 65.0  # unchanged shipped body gate


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def accepted():
    return read(ART / 'final-admission.json')['accepted_ids']


class TA2ShippedTests(unittest.TestCase):
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
        self.assertFalse((ROOT / 'art/production/waivers/monster-batch-ta2.json').exists())

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
        first = next(n for n, a in enumerate(manifest['assets']) if a['batch'] == 'monster-batch-ta2')
        previous = manifest['assets'][:first]
        self.assertEqual(len(previous), base['pre_ta2_manifest_asset_count'])
        self.assertEqual(
            hashlib.sha256(json.dumps({a['id']: a for a in previous}, sort_keys=True,
                                      separators=(',', ':')).encode()).hexdigest(),
            base['pre_ta2_manifest_by_id_sha256'])
        entries = {a['id']: a for a in manifest['assets']}
        report = {a['id']: a for a in read(ART / 'export-report.json')['assets']}
        selected = read(ART / 'selected-masters.json')
        self.assertEqual(len([a for a in manifest['assets'] if a['batch'] == 'monster-batch-ta2']), len(ACCEPTED))
        for i in ACCEPTED:
            self.assertEqual(entries[i]['batch'], 'monster-batch-ta2')
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
        # The companion-archer entry and its runtime token are unchanged.
        self.assertEqual(entries['companion-archer'], base['companion_archer'])
        self.assertEqual(sha(ROOT / 'data/gfx/tokens/companion-archer.png'),
                         base['companion_archer']['runtime_sha256'])
        # The wiring-only elven archer token is byte-identical to companion-archer.
        self.assertEqual((ROOT / 'data/gfx/tokens/elven-archer.png').read_bytes(),
                         (ROOT / 'data/gfx/tokens/companion-archer.png').read_bytes())

    def test_review_with_shipped_siblings_and_frozen_floors(self):
        for g in GROUPS:
            for mode in ('color', 'grayscale'):
                self.assertTrue((ART / f'review/{g}-{mode}-48-64-96.png').is_file())
        for n in ('floor-readability-48.png', 'floor-readability-48-x2.png', 'floor-readability-48-x2-b.png'):
            self.assertTrue((ART / 'review' / n).exists())
        for p in read(ART / 'review/floor-source-pins.json').values():
            self.assertEqual(sha(ROOT / p['path']), p['sha256'])
        text = (ART / 'make_review_sheets.py').read_text()
        for i in ('caravan-merchant', 'caravan-porter', 'cutpurse', 'bandit', 'yeek-wayist', 'yaech-hunter',
                  'yaech-psion', 'dwarven-guard', 'norgan', 'protector-myssil', 'berethh', 'mindworm',
                  'companion-archer', 'fillarel-aldaren', 'elven-mage', 'elven-corruptor'):
            self.assertIn("'" + i + "'", text)
        for label, prefixes in read(ART / 'review/luminance.json')['zone_floors'].items():
            self.assertIn(label, text)
            for prefix in prefixes:
                self.assertIn(prefix, text)


class TA2ContractsTests(unittest.TestCase):
    def test_exact_sources_and_catalog(self):
        ev = read(EVIDENCE / 'source-contracts.json')
        ws = ROOT.parents[2]
        self.assertEqual(ev['art_ids'], ART_IDS)
        self.assertEqual(ev['wiring_only'], WIRING)
        source = (ROOT / 'overload/mod/class/CheckerTokens.lua').read_text()
        pins = ev['auxiliary_sources'][:]
        for i in ev['identities']:
            id_ = i['id']
            self.assertFalse(i['unique'])
            self.assertIsNone(i['define_as'])
            self.assertEqual(i['type'], 'humanoid')
            if id_ == 'elven-archer':
                self.assertEqual(i['subtype'], 'elf')
                self.assertEqual(i['native_image_size'], [64, 64])
            else:
                self.assertEqual(i['subtype'], SUBTYPES.get(id_, 'human'))
                self.assertEqual(i['native_image_size'], [64, 128] if id_ in TALL else [64, 64])
                self.assertEqual(i['native_tall'], id_ in TALL)
                self.assertEqual('tall_body' in i, id_ in TALL)
            for key in ('shader', 'moddable_tile', 'anim', 'add_displays'):
                self.assertIsNone(i[key])
            pins += i['sources']
            if id_ == 'elven-archer':
                continue
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
        for term in ('defined_as', 'nice_tile', 'SLINGER', 'shalore scribe', 'anomalies.lua', 'races.lua'):
            self.assertIn(term, text)

    def test_lumberjack_defined_as_typo_is_pinned(self):
        path = ROOT.parents[2] / 'game/modules/tome/data/zones/town-lumberjack-village/npcs.lua'
        text = path.read_text()
        self.assertIn('newEntity{ defined_as = "LUMBERJACK",\n\ttype = "humanoid", subtype = "human",\n\tname = "lumberjack"', text)
        # No runtime define_as: the misspelled key never binds a define_as.
        self.assertNotIn('define_as = "LUMBERJACK"', text)
        entry = read(EVIDENCE / 'source-contracts.json')['identities']
        lj = next(i for i in entry if i['id'] == 'lumberjack')
        self.assertIsNone(lj['define_as'])

    def test_arena_slinger_stays_native_contract(self):
        path = ROOT.parents[2] / 'game/modules/tome/data/zones/arena-unlock/npcs.lua'
        text = path.read_text()
        self.assertIn('newEntity{ name = "halfling slinger",\n\tdefine_as = "SLINGER"', text)
        zone = (ROOT.parents[2] / 'game/modules/tome/data/zones/arena-unlock/zone.lua').read_text()
        self.assertIn("makeEntityByName(game.level, \"actor\", \"SLINGER\")", zone)

    def test_wiring_only_elven_archer_reuses_companion_token(self):
        ev = read(EVIDENCE / 'source-contracts.json')
        wiring = read(ART / 'wiring-only.json')
        source = (ROOT / 'overload/mod/class/CheckerTokens.lua').read_text()
        self.assertEqual(ev['wiring_only'], [wiring['id']])
        self.assertEqual(wiring['type'], 'humanoid')
        self.assertEqual(wiring['subtype'], 'elf')
        self.assertEqual(wiring['native_image'], 'npc/humanoid_elf_elven_archer.png')
        self.assertEqual(wiring['reuse']['id'], 'companion-archer')
        self.assertEqual(wiring['reuse']['master'], 'monster-batch-s/masters/companion-archer-v1.png')
        line = next(l for l in source.splitlines() if '{id="elven-archer",' in l)
        self.assertIn('name="elven archer"', line)
        self.assertIn('image="npc/humanoid_elf_elven_archer.png"', line)
        self.assertIn('type="humanoid"', line)
        self.assertIn('subtype="elf"', line)
        self.assertNotIn('define_as', line)
        self.assertNotIn('unique=', line)
        # The companion-archer entry is byte-for-byte as shipped.
        comp_line = next(l for l in source.splitlines() if '{id="companion-archer",' in l)
        self.assertEqual(comp_line.strip(), read(EVIDENCE / 'unchanged-baseline.json')['companion_archer_catalog_line'].strip())
        # Reuse master is pinned by the source contract and the selected master.
        ident = next(i for i in ev['identities'] if i['id'] == 'elven-archer')
        self.assertEqual(ident['reuse']['master_sha256'], sha(ROOT.parents[2] / 'game/addons/tome-checker-revised/art/monster-batch-s/masters/companion-archer-v1.png'))
        self.assertEqual(read(ART / 'selected-masters.json')[wiring['id']], '../' + wiring['reuse']['master'])

    def test_official_chinese_names(self):
        names = read(ART / 'official-names.json')
        self.assertEqual(names['path'], '/workspace/tome4-chinese-translation/mod-tome.lua')
        self.assertEqual(len(names['names']), len(ACCEPTED))
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
        for pack in (ROOT / 'art/production/handoffs').glob('monster-batch-ta2-*/*'):
            if not (pack / 'inputs.json').is_file():
                continue
            calls = sorted(pack.glob('imagegen-calls/call-*/call.json'))
            task = read(pack / 'inputs.json')['task']
            self.assertLessEqual(len(calls), task['max_attempts'])
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
            self.assertLessEqual(a[1], b[0], 'TA-2 image calls must be serial')
        self.assertEqual(outcomes.count('recorded'), 14)
        self.assertEqual(outcomes.count('provenance-rejected'), 3)
        self.assertEqual(outcomes.count('style-gate-rejected'), 1)
        self.assertEqual(len(outcomes), 18)

    def test_rework_and_retry_lineage_and_no_floor_change(self):
        selected = read(ART / 'selected-masters.json')
        self.assertEqual(selected['thalore-hunter'], 'masters/thalore-hunter-rework-v1.png')
        self.assertTrue((ART / 'masters/thalore-hunter-v1.png').is_file())
        self.assertTrue((ART / 'masters/thalore-hunter-rework-v1.png').is_file())
        for i in ART_IDS:
            if i != 'thalore-hunter':
                self.assertEqual(selected[i], f'masters/{i}-v1.png')
        # The two identities whose first wrapper call failed were re-issued in a
        # fresh retry pack; no threshold or floor changed.
        self.assertTrue((ROOT / 'art/production/handoffs/monster-batch-ta2-retry-1/halfling-slinger/receipts/attempt-1.json').is_file())
        self.assertTrue((ROOT / 'art/production/handoffs/monster-batch-ta2-retry-1/halfling-gardener/receipts/attempt-1.json').is_file())
        self.assertEqual(read(ROOT / 'art/production/handoffs/monster-batch-ta2-2/halfling-slinger/imagegen-calls/call-2/call.json')['outcome'], 'provenance-rejected')
        self.assertEqual(read(ROOT / 'art/production/handoffs/monster-batch-ta2-2/halfling-gardener/imagegen-calls/call-1/call.json')['outcome'], 'style-gate-rejected')
        self.assertTrue((ROOT / 'art/production/handoffs/monster-batch-ta2-rework-1/thalore-hunter/receipts/attempt-1.json').is_file())
        admission = read(ART / 'final-admission.json')
        self.assertEqual(admission['body_minimum'], BODY_MINIMUM)
        self.assertEqual(admission['descriptive_floor_baseline'], FLOOR)
        self.assertEqual(admission['waivers'], [])
        # The sheets carry a 2x-nearest native column beside each TA-2 token.
        text = (ART / 'make_review_sheets.py').read_text()
        self.assertIn('native 2x', text)
        self.assertIn('NAT_W = 128', text)

    def test_generation_pins_and_render_evidence(self):
        digest = sha(EVIDENCE / 'source-contracts.json')
        count = 0
        for p in (ROOT / 'art/production/batches').glob('monster-batch-ta2-[1-5].json'):
            for a in read(p)['assets']:
                count += 1
                self.assertEqual(a['render_evidence'][0]['sha256'], digest)
                for key in ('sources', 'references'):
                    for pin in a[key]:
                        self.assertEqual(sha(ROOT.parents[2] / pin['path']), pin['sha256'])
        self.assertEqual(count, len(ART_IDS))
        for name in ('monster-batch-ta2-retry-1', 'monster-batch-ta2-rework-1'):
            for a in read(ROOT / f'art/production/batches/{name}.json')['assets']:
                self.assertEqual(a['render_evidence'][0]['sha256'], digest)
                for key in ('sources', 'references', 'render_evidence'):
                    for pin in a[key]:
                        self.assertEqual(sha(ROOT.parents[2] / pin['path']), pin['sha256'])
        for pack in (ROOT / 'art/production/handoffs').glob('monster-batch-ta2-*/*'):
            if not (pack / 'inputs.json').is_file():
                continue
            task = read(pack / 'inputs.json')['task']
            for pin in task['sources']:
                self.assertEqual(sha(ROOT.parents[2] / pin['path']), pin['sha256'])
            for pin in task['references'] + task['render_evidence']:
                self.assertEqual(sha(ROOT.parents[2] / pin['path']), pin['sha256'])


if __name__ == '__main__':
    unittest.main()
