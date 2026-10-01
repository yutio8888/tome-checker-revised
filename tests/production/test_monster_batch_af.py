"""AF: nine admitted exact off-list pool identities; unchanged AD style/luminance floors.
Static validation only. Live installation/combat validation is a separate task.
"""
import hashlib
import os
import re
import importlib.util
import json
import math
import unittest
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
ART = ROOT / 'art/monster-batch-af'
EVIDENCE = ROOT / 'evidence/monster-batch-af-20261001/source-contracts.json'
spec = importlib.util.spec_from_file_location('af_style', ROOT / 'tools/check_token_style.py')
style = importlib.util.module_from_spec(spec)
spec.loader.exec_module(style)
IDS = ['nightmare-horror','radiant-horror','maelstrom','parasitic-horror','lich','ancient-lich','archlich','blood-lich','animated-blood']
ATTEMPTED = IDS[:]
TALL = set(IDS) - {'nightmare-horror','radiant-horror','blood-lich'}
GROUPS = ('horrors','liches-blood')
FLOOR = 45.0  # same real-floor baseline as AD
BODY_MINIMUM = 65.0  # unchanged shipped body gate


class MonsterBatchAFShippedTests(unittest.TestCase):
    def test_exact_selection_style_without_waiver(self):
        selected = json.loads((ART / 'selected-masters.json').read_text())
        self.assertEqual(set(selected), set(IDS))
        self.assertEqual([a['id'] for a in json.loads((ART / 'catalog.json').read_text())], IDS)
        self.assertEqual(sorted(p.name for p in (ART / 'masters').glob('*.png')),
                         sorted(Path(v).name for v in selected.values()))
        for i, master in selected.items():
            result = style.check_asset(ART / f'sprites/128/{i}.png', ART / master, i, allow_grandfather=False)
            self.assertEqual(result['blocking'], [], i)
            self.assertEqual(result['warnings'], [], i)
            self.assertFalse(result['waived'], i)
            self.assertTrue(result['passed'], i)
        self.assertFalse((ROOT / 'art/production/waivers/monster-batch-af.json').exists())
        held = json.loads((ART / 'review/blood-lich-waiver-request-SUPERSEDED.json').read_text())
        self.assertEqual(held['status'], 'SUPERSEDED')
        self.assertFalse(held['approved'])
        self.assertEqual(held['unchanged_body_floor'], BODY_MINIMUM)
        self.assertIn('blood-lich', selected)
        self.assertFalse((ART / 'review/blood-lich-PENDING-waiver-request.json').exists())

    def test_body_luminance_remeasured(self):
        lum = json.loads((ART / 'review/luminance.json').read_text())
        self.assertEqual(lum['floor_minimum_for_body'], FLOOR)
        for i in IDS:
            with Image.open(ART / f'sprites/128/{i}.png') as im:
                vals = []
                for y in range(128):
                    for x in range(128):
                        r,g,b,a = im.getpixel((x,y))
                        if a >= 180 and math.hypot(x+.5-64, y+.5-64)/64 <= .55:
                            vals.append(.299*r + .587*g + .114*b)
            measured = round(sum(vals)/len(vals), 2)
            self.assertEqual(lum['assets'][i], measured, i)
            self.assertGreaterEqual(measured, BODY_MINIMUM, i)

    def test_exports_runtime_and_manifest(self):
        manifest = json.loads((ROOT / 'data/token-manifest.json').read_text())
        entries = {a['id']: a for a in manifest['assets']}
        report = {a['id']: a for a in json.loads((ART / 'export-report.json').read_text())['assets']}
        selected = json.loads((ART / 'selected-masters.json').read_text())
        baseline = json.loads((EVIDENCE.parent / 'unchanged-baseline.json').read_text())
        # The frozen pre-AF prefix excludes all later batches as the ordered
        # manifest grows; keep its original count/hash assertions unchanged.
        first_af = next(n for n,a in enumerate(manifest['assets']) if a['batch'] == 'monster-batch-af')
        previous = manifest['assets'][:first_af]
        self.assertEqual(len(previous), baseline['pre_af_manifest_asset_count'])
        self.assertEqual(hashlib.sha256(json.dumps(previous, sort_keys=True, separators=(',',':')).encode()).hexdigest(),
                         baseline['pre_af_manifest_assets_sha256'])
        for i in IDS:
            self.assertEqual(entries[i]['batch'], 'monster-batch-af')
            self.assertEqual((ROOT / f'data/gfx/tokens/{i}.png').read_bytes(), (ART / f'sprites/128/{i}.png').read_bytes())
            self.assertEqual(entries[i]['master_sha256'], hashlib.sha256((ART / selected[i]).read_bytes()).hexdigest())
            self.assertEqual(entries[i]['runtime_sha256'], hashlib.sha256((ART / f'sprites/128/{i}.png').read_bytes()).hexdigest())
            self.assertFalse(report[i]['style_gate']['advisory_downgrade'])
            for size in (48,64,96,128,256):
                with Image.open(ART / f'sprites/{size}/{i}.png') as im:
                    self.assertEqual(im.size, (size,size))
                    self.assertEqual(im.mode, 'RGBA')
                    self.assertTrue(all(im.getpixel(p)[3] == 0 for p in ((0,0),(0,size-1),(size-1,0),(size-1,size-1))))

    def test_review_sheets_include_shipped_siblings(self):
        for group in GROUPS:
            for mode in ('color','grayscale'):
                self.assertTrue((ART / f'review/{group}-{mode}-48-64-96.png').is_file())
        for n in ('floor-readability-48.png','floor-readability-48-x2.png','floor-readability-48-x2-b.png'):
            self.assertTrue((ART / 'review' / n).is_file())
        script = (ART / 'make_review_sheets.py').read_text()
        for i in ('luminous-horror','oozing-horror','abyssal-horror','umbral-horror','bone-horror','sanguine-horror','dread','barrow-wight'):
            self.assertIn("'"+i+"'", script)


class MonsterBatchAFContractsTests(unittest.TestCase):
    def test_source_contracts_and_exact_catalog(self):
        ev = json.loads(EVIDENCE.read_text())
        workspace = ROOT.parents[2]
        self.assertEqual(set(i['id'] for i in ev['identities'] if i['verdict']=='READY'), set(ATTEMPTED))
        dreaming = next(i for i in ev['identities'] if i['id']=='dreaming-horror')
        self.assertEqual(dreaming['shader'], 'shadow_simulacrum')
        self.assertNotIn('{id="dreaming-horror",', (ROOT / 'overload/mod/class/CheckerTokens.lua').read_text())
        source = (ROOT / 'overload/mod/class/CheckerTokens.lua').read_text()
        pins = ev['auxiliary_sources'][:] + json.loads((EVIDENCE.parent / 'supplement-source-pins.json').read_text())
        for i in ev['identities']:
            id_ = i['id']
            pins += [i['source'],i['base_source']] + i['extra_sources']
            sprite = workspace / i['native_image_path']
            self.assertEqual(hashlib.sha256(sprite.read_bytes()).hexdigest(), i['native_image_sha256'])
            with Image.open(sprite) as im:
                self.assertEqual(list(im.size), i['native_image_size'])
            if id_ == 'dreaming-horror':
                continue
            self.assertEqual(i['native_image_size'], [64,128] if id_ in TALL else [64,64])
            self.assertEqual(i['native_tall'], id_ in TALL)
            self.assertEqual('tall_body' in i, id_ in TALL)
            self.assertIsNone(i['define_as'])
            self.assertFalse(i['unique'])
            for key in ('shader','moddable_tile','anim','add_displays'):
                self.assertIsNone(i[key])
            line = next(l for l in source.splitlines() if '{id="'+id_+'",' in l)
            for key, value in (('name',i['native_name']),('image',i['native_image']),('type',i['type']),('subtype',i['subtype'])):
                self.assertIn(f'{key}="{value}"', line)
            self.assertEqual('native_tall=true' in line, id_ in TALL)
            self.assertNotIn('define_as', line)
            self.assertNotIn('unique=', line)
            self.assertNotIn('urh_rok_form', line)
        for pin in pins:
            path = workspace / pin['path']
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), pin['sha256'])
            self.assertIn(pin['anchor'], path.read_text().splitlines()[pin['line']-1])
        self.assertIn('Bloodcaller', str(ev['name_collisions_checked']))
        # Temporal clones are handled by the existing whole-catalog helper.
        self.assertIn('local function temporalClone(actor)', source)
        self.assertIn('nameAlias(actor) or temporalClone(actor)', source)
        for term in ('Bloodcaller','HORROR_PARASITIC_LEECHES','luminous horror','captureRandomOrigin','Call Shadows','temporalClone'):
            self.assertIn(term,str(ev['summons_and_same_body_copies']))

    def test_resolved_talents_and_appearance_hits(self):
        talents = json.loads((EVIDENCE.parent / 'talent-contracts.json').read_text())
        self.assertEqual(set(talents), set(ATTEMPTED) | {'dreaming-horror'})
        for id_, rows in talents.items():
            for t, pin in rows.items():
                self.assertNotIn('unresolved', pin, (id_,t))
                path = ROOT.parents[2] / 'game/modules/tome' / pin['path']
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), pin['sha256'])
        self.assertEqual(talents['nightmare-horror']['T_STEALTH']['mode'], 'sustained')
        self.assertEqual(talents['maelstrom']['T_THUNDERSTORM']['mode'], 'sustained')
        self.assertIn('addShaderAura', str(talents['lich']['T_STONE_SKIN']['display_hits']))
        self.assertEqual(talents['animated-blood'], {})

    def test_blood_edge_constructor_and_official_names(self):
        contract = json.loads((EVIDENCE.parent / 'blood-edge-contract.json').read_text())
        self.assertEqual(contract['artifact'], 'Blood-Edge')
        self.assertEqual(contract['define_as'], 'BLOODEDGE')
        source = ROOT.parents[2] / contract['source_file']
        self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), contract['source_sha256'])
        body = contract['body']['add_mos']
        self.assertEqual(body, [{'image':'npc/undead_horror_animated_blood.png','display_h':1,'display_y':0}])
        for talent, pin in contract['talents'].items():
            source = ROOT.parents[2] / 'game/modules/tome' / pin['path']
            self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), pin['sha256'])
        ev = json.loads(EVIDENCE.read_text())
        blood = next(i for i in ev['identities'] if i['id']=='animated-blood')
        self.assertEqual(blood['subtype'], 'blood')
        self.assertFalse(blood['default_image_exists'])
        self.assertEqual(blood['default_image'], 'npc/undead_blood_animated_blood.png')
        names = json.loads((EVIDENCE.parent / 'official-names.json').read_text())
        self.assertEqual(names['path'], '/workspace/tome4-chinese-translation/mod-tome.lua')
        self.assertEqual(len(names['names']), 10)
        # Offline gates run against a separate translation checkout that keeps
        # changing, so bind every batch-AF name to its recorded official line by
        # exact text (line numbers may drift, the text may not). The whole-file SHA
        # is deliberately not asserted; TOME_CHECKER_PINNED_TRANSLATION can point at
        # a copy but is no longer required.
        source = Path(os.environ.get('TOME_CHECKER_PINNED_TRANSLATION', names['path']))
        if not source.is_file():
            self.skipTest(f'official translation source unavailable: {source}')
        lines = source.read_text(encoding='utf-8').splitlines()
        pair = re.compile(r'^\s*t\(\s*"((?:[^"\\]|\\.)*)"\s*,\s*"((?:[^"\\]|\\.)*)"')
        for row in names['names']:
            expected = row['official_line']
            found = next((n for n, line in enumerate(lines, 1) if line == expected), None)
            self.assertIsNotNone(
                found,
                f"{row['native_name']!r}: no line in {source} exactly equals the recorded "
                f'official line {expected!r}')
            current = lines[found - 1]
            parsed = pair.match(current)
            self.assertIsNotNone(
                parsed,
                f"{row['native_name']!r}: line {found} of {source} is not a "
                f't("EN", "ZH"...) pair: {current!r}')
            expected_pair = pair.match(expected)
            self.assertIsNotNone(expected_pair, f'recorded official line is not a pair: {expected!r}')
            self.assertEqual(
                parsed.group(1), row['native_name'],
                f"{row['native_name']!r}: line {found} of {source} has English key {parsed.group(1)!r}")
            self.assertEqual(
                parsed.group(2), expected_pair.group(2),
                f"{row['native_name']!r}: line {found} of {source} has Chinese name {parsed.group(2)!r}, "
                f'expected {expected_pair.group(2)!r}')

    def test_authorized_rework_provenance_and_serial_calls(self):
        intervals = []
        for pack in (ROOT / 'art/production/handoffs').glob('monster-batch-af-*/*'):
            if not (pack / 'inputs.json').is_file(): continue
            calls = list(pack.glob('imagegen-calls/call-*/call.json'))
            inputs = json.loads((pack / 'inputs.json').read_text())
            self.assertLessEqual(len(calls), inputs['task']['max_attempts'])
            for path in calls:
                call = json.loads(path.read_text())
                self.assertEqual(call['codex_model'], 'gpt-6.1-sol')
                self.assertTrue(call['codex_ephemeral'])
                intervals.append((call['timestamp_started'], call['timestamp_finished']))
                if call['outcome'] == 'recorded':
                    name = Path(call['saved_output_path']).name
                    master = ART / 'masters' / name
                    if not master.exists(): master = ART / 'superseded' / name
                    self.assertEqual(hashlib.sha256(master.read_bytes()).hexdigest(), call['sha256'])
                    self.assertTrue(call['provenance']['ok'])
                    self.assertTrue(call['gate_passed'])
        intervals.sort()
        for before, after in zip(intervals, intervals[1:]):
            self.assertLessEqual(before[1], after[0], 'All AF calls remain serial')
        for pack_id in (4,5):
            path = ROOT / f'art/production/batches/monster-batch-af-{pack_id}.json'
            for asset in json.loads(path.read_text())['assets']:
                key = 'refinement' if asset['asset_id'] == 'radiant-horror' else 'retry_authorization'
                self.assertIn(key, asset)
                for pin in asset[key]['evidence']:
                    source = ROOT.parents[2] / pin['path']
                    self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), pin['sha256'])
        for mode in ('color','grayscale'):
            self.assertTrue((ART / f'review/rework-focus-{mode}-48-64-96.png').exists())

    def test_generation_pins_and_budget(self):
        calls = list((ROOT / 'art/production/handoffs').glob('monster-batch-af-[123]/*/imagegen-calls/call-*/call.json'))
        per = {}
        intervals = []
        recorded = {}
        for p in calls:
            d = json.loads(p.read_text())
            per[d['asset_id']] = per.get(d['asset_id'],0)+1
            self.assertEqual(d['codex_model'], 'gpt-6.1-sol')
            self.assertTrue(d['codex_ephemeral'])
            intervals.append((d['timestamp_started'], d['timestamp_finished']))
            if d['outcome'] == 'recorded':
                master = ART / 'masters' / Path(d['saved_output_path']).name
                if not master.exists():
                    # Original drafts failed the unchanged body floor; retain its
                    # master/receipt rather than rewriting generation history.
                    self.assertIn((d['asset_id'], master.name), {('lich','lich-v1.png'),('blood-lich','blood-lich-v1.png'),('animated-blood','animated-blood-v1.png'),('radiant-horror','radiant-horror-v1.png')})
                    master = ART / 'superseded' / master.name
                self.assertEqual(hashlib.sha256(master.read_bytes()).hexdigest(), d['sha256'])
                self.assertTrue(d['provenance']['ok'])
                self.assertTrue(d['gate_passed'])
                recorded[d['asset_id']] = d['sha256']
        self.assertEqual(set(per),set(ATTEMPTED))
        self.assertEqual(set(recorded),set(ATTEMPTED))
        intervals.sort()
        for before, after in zip(intervals, intervals[1:]):
            self.assertLessEqual(before[1],after[0], 'ImageGen calls must be serial')
        self.assertLessEqual(max(per.values()),2)
        self.assertLessEqual(len(calls),18)
        digest = hashlib.sha256(EVIDENCE.read_bytes()).hexdigest()
        for p in (ROOT / 'art/production/batches').glob('monster-batch-af-*.json'):
            for a in json.loads(p.read_text())['assets']:
                self.assertEqual(a['render_evidence'][0]['sha256'],digest)


if __name__ == '__main__': unittest.main()
