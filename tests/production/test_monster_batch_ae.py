"""AE: twelve exact off-list pool identities; unchanged AD style/luminance floors.
Static validation only. Live installation/combat validation is a separate task.
"""
import hashlib
import importlib.util
import json
import math
import unittest
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
ART = ROOT / 'art/monster-batch-ae'
EVIDENCE = ROOT / 'evidence/monster-batch-ae-20261001/source-contracts.json'
spec = importlib.util.spec_from_file_location('ae_style', ROOT / 'tools/check_token_style.py')
style = importlib.util.module_from_spec(spec)
spec.loader.exec_module(style)
IDS = ['champion-of-urh-rok', 'forge-giant', 'hummerhorn', 'weaver-matriarch', 'patchwork-troll', 'maulotaur',
       'worm-that-walks', 'headless-horror', 'storm-wyrm', 'spire-dragon', 'blinkwyrm', 'emperor-wight']
TALL = set(IDS) - {'hummerhorn', 'worm-that-walks', 'headless-horror'}
GROUPS = ('demons-giants', 'dragons', 'insects-horrors-wights')
FLOOR = 45.0  # same real-floor baseline as AD
BODY_MINIMUM = 65.0  # unchanged shipped body gate


class MonsterBatchAEShippedTests(unittest.TestCase):
    def test_exact_selection_and_style_with_no_waiver(self):
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
        for name in ('monster-batch-ae.json', 'monster-batch-ae-PENDING-REQUEST.json'):
            self.assertFalse((ROOT / 'art/production/waivers' / name).exists())

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
        for i in IDS:
            self.assertEqual(entries[i]['batch'], 'monster-batch-ae')
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
        for i in ('storm-drake','ice-wyrm','fire-wyrm','venom-wyrm','duathedlen','daelach','barrow-wight','weaver-young','minotaur'):
            self.assertIn("'"+i+"'", script)


class MonsterBatchAEContractsTests(unittest.TestCase):
    def test_source_contracts_and_exact_catalog(self):
        ev = json.loads(EVIDENCE.read_text())
        workspace = ROOT.parents[2]
        self.assertEqual([i['id'] for i in ev['identities']], IDS)
        source = (ROOT / 'overload/mod/class/CheckerTokens.lua').read_text()
        pins = ev['auxiliary_sources'][:] + json.loads((EVIDENCE.parent / 'clone-contracts.json').read_text())
        for i in ev['identities']:
            id_ = i['id']
            pins += [i['source'],i['base_source']] + i['extra_sources']
            sprite = workspace / i['native_image_path']
            self.assertEqual(hashlib.sha256(sprite.read_bytes()).hexdigest(), i['native_image_sha256'])
            with Image.open(sprite) as im:
                self.assertEqual(list(im.size), i['native_image_size'])
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
        self.assertIn('HEADLESSHORROR', str(ev['name_collisions_checked']))
        # Temporal clones are handled for the whole catalog (generalized from AE).
        self.assertIn('local function temporalClone(actor)', source)
        self.assertIn('nameAlias(actor) or temporalClone(actor)', source)
        for term in ('can_multiply','CARRION_WORM_MASS','is_eldritch_eye','captureRandomOrigin','weaver young','storm drakes'):
            self.assertIn(term,str(ev['summons_and_same_body_copies']))

    def test_resolved_talents_and_appearance_hits(self):
        talents = json.loads((EVIDENCE.parent / 'talent-contracts.json').read_text())
        self.assertEqual(set(talents), set(IDS))
        for id_, rows in talents.items():
            for t, pin in rows.items():
                self.assertNotIn('unresolved', pin, (id_,t))
                path = ROOT.parents[2] / 'game/modules/tome' / pin['path']
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), pin['sha256'])
        self.assertEqual(talents['patchwork-troll']['T_FAST_METABOLISM']['mode'], 'passive')
        self.assertEqual(talents['emperor-wight']['T_THUNDERSTORM']['mode'], 'sustained')
        self.assertEqual(talents['blinkwyrm']['T_SPELLCRAFT']['mode'], 'sustained')
        self.assertIn('addShaderAura', str(talents['forge-giant']['T_BURNING_WAKE']['display_hits']))

    def test_generation_pins_and_budget(self):
        calls = list((ROOT / 'art/production/handoffs').glob('monster-batch-ae-*/*/imagegen-calls/call-*/call.json'))
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
                    # Retain the coordinator-rejected first storm design and its
                    # immutable receipt after selecting the refinement master.
                    self.assertEqual((d['asset_id'], master.name),
                                     ('storm-wyrm', 'storm-wyrm-v1.png'))
                    master = ART / 'superseded' / master.name
                self.assertEqual(hashlib.sha256(master.read_bytes()).hexdigest(), d['sha256'])
                self.assertTrue(d['provenance']['ok'])
                self.assertTrue(d['gate_passed'])
                recorded[d['asset_id']] = d['sha256']
        self.assertEqual(set(per),set(IDS))
        self.assertEqual(set(recorded),set(IDS))
        intervals.sort()
        for before, after in zip(intervals, intervals[1:]):
            self.assertLessEqual(before[1],after[0], 'ImageGen calls must be serial')
        self.assertLessEqual(max(per.values()),3)
        self.assertLessEqual(len(calls),24)
        digest = hashlib.sha256(EVIDENCE.read_bytes()).hexdigest()
        for p in (ROOT / 'art/production/batches').glob('monster-batch-ae-*.json'):
            for a in json.loads(p.read_text())['assets']:
                self.assertEqual(a['render_evidence'][0]['sha256'],digest)


if __name__ == '__main__': unittest.main()
