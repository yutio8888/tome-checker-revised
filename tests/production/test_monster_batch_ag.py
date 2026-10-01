"""AG: seven special-case pool identities; unchanged AD style/luminance floors.
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
ART = ROOT / 'art/monster-batch-ag'
EVIDENCE = ROOT / 'evidence/monster-batch-ag-20261001/source-contracts.json'
spec = importlib.util.spec_from_file_location('ag_style', ROOT / 'tools/check_token_style.py')
style = importlib.util.module_from_spec(spec)
spec.loader.exec_module(style)
IDS = ['multi-hued-drake-hatchling','multi-hued-drake','greater-multi-hued-wyrm','shadow-claw','shadow-caster','multi-hued-crystal','shimmering-crystal']
SCOPE = IDS[:]
TALL = {'greater-multi-hued-wyrm'}
SHADERS = set(IDS) - {'shadow-claw','shadow-caster'}
GROUPS = ('multihued','shadows','crystals')
FLOOR = 45.0  # same real-floor baseline as AD
BODY_MINIMUM = 65.0  # unchanged shipped body gate


class MonsterBatchAGShippedTests(unittest.TestCase):
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
        for name in ('monster-batch-ag.json', 'monster-batch-ag-PENDING-REQUEST.json'):
            self.assertFalse((ROOT / 'art/production/waivers' / name).exists())

    def test_coordinator_refinement_and_unchanged_six(self):
        evidence=ROOT/'evidence/monster-batch-ag-rework-20261001'
        prior=json.loads((evidence/'unchanged-six.json').read_text())
        self.assertEqual(len(prior['verified_assets']),6)
        manifest={a['id']:a for a in json.loads((ROOT/'data/token-manifest.json').read_text())['assets']}
        selected=json.loads((ART/'selected-masters.json').read_text())
        for entry in prior['verified_assets']:
            i=entry['id']
            self.assertEqual(manifest[i],entry)
            self.assertEqual(hashlib.sha256((ROOT/f'data/gfx/tokens/{i}.png').read_bytes()).hexdigest(),entry['runtime_sha256'])
            self.assertEqual(hashlib.sha256((ART/selected[i]).read_bytes()).hexdigest(),entry['master_sha256'])
        asset=json.loads((ROOT/'art/production/batches/monster-batch-ag-4.json').read_text())['assets'][0]
        self.assertEqual(asset['refinement']['supersedes'],'shadow-caster')
        self.assertEqual(asset['refinement']['previous_batch'],'monster-batch-ag-3')
        self.assertEqual(asset['max_attempts'],2)
        for pin in asset['refinement']['evidence']:
            self.assertEqual(hashlib.sha256((ROOT.parents[2]/pin['path']).read_bytes()).hexdigest(),pin['sha256'])

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
        admission=json.loads((ART/'final-admission.json').read_text())
        self.assertEqual(admission['accepted_ids'],IDS)
        self.assertEqual(admission['native_retry_ids'],[])
        selected = json.loads((ART / 'selected-masters.json').read_text())
        for i in IDS:
            self.assertEqual(entries[i]['batch'], 'monster-batch-ag')
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
        for i in ('storm-drake','ice-wyrm','fire-wyrm','shadow-stalker','white-crystal','blue-crystal','black-crystal'):
            self.assertIn("'"+i+"'", script)


class MonsterBatchAGContractsTests(unittest.TestCase):
    def test_source_contracts_and_exact_catalog(self):
        ev = json.loads(EVIDENCE.read_text())
        workspace = ROOT.parents[2]
        self.assertEqual([i['id'] for i in ev['identities']], SCOPE)
        source = (ROOT / 'overload/mod/class/CheckerTokens.lua').read_text()
        pins = ev['auxiliary_sources'][:] + json.loads((EVIDENCE.parent / 'render-supplement-pins.json').read_text())
        for i in ev['identities']:
            id_ = i['id']
            pins += [i['source'],i['base_source']] + i['extra_sources']
            sprite = workspace / i['native_image_path']
            self.assertEqual(hashlib.sha256(sprite.read_bytes()).hexdigest(), i['native_image_sha256'])
            with Image.open(sprite) as im:
                self.assertEqual(list(im.size), i['native_image_size'])
            self.assertEqual(i['native_image_size'], [64,128] if id_ in TALL else [64,64])
            self.assertEqual(i['native_tall'], id_ in TALL)
            self.assertEqual(i['define_as'], {'greater-multi-hued-wyrm':'GREATER_MULTI_HUED_WYRM','shadow-claw':'SHADOW_CLAW','shadow-caster':'SHADOW_CASTER'}.get(id_))
            self.assertFalse(i['unique'])
            for key in ('moddable_tile','anim','add_displays'):
                self.assertIsNone(i[key])
            if id_ in SHADERS:
                self.assertEqual(i['shader']['value'], 'quad_hue')
                self.assertIsNone(i['shader']['shader_args'])
            else: self.assertIsNone(i['shader'])
            line = next(l for l in source.splitlines() if '{id="'+id_+'",' in l)
            for key, value in (('name',i['native_name']),('image',i['native_image']),('type',i['type']),('subtype',i['subtype'])):
                self.assertIn(f'{key}="{value}"', line)
            self.assertEqual('native_tall=true' in line, id_ in TALL)
            if i['define_as']: self.assertIn('define_as="'+i['define_as']+'"',line)
            else: self.assertNotIn('define_as',line)
            self.assertEqual('native_shader="quad_hue"' in line,id_ in SHADERS)
            self.assertEqual('shared_name=true' in line,id_ in {'shadow-claw','shadow-caster'})
            self.assertNotIn('unique=', line)
            self.assertNotIn('urh_rok_form', line)
        for pin in pins:
            path = workspace / pin['path']
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), pin['sha256'])
            self.assertIn(pin['anchor'], path.read_text().splitlines()[pin['line']-1])
        self.assertIn('local function temporalClone(actor)', source)
        self.assertIn('nameAlias(actor) or temporalClone(actor)', source)
        self.assertIn('actor.shader_args == nil', source)
        self.assertIn('shared_name_index', source)

    def test_resolved_talents_and_appearance_hits(self):
        talents = json.loads((EVIDENCE.parent / 'talent-contracts.json').read_text())
        self.assertEqual(set(talents),set(SCOPE))
        for id_, rows in talents.items():
            for t,pin in rows.items():
                self.assertNotIn('unresolved',pin,(id_,t))
                path = ROOT.parents[2] / 'game/modules/tome' / pin['path']
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),pin['sha256'])
                self.assertEqual(pin['display_hits'],[],(id_,t))
        self.assertIn('T_MIND_SEAR',talents['shadow-caster'])
        self.assertIn('T_KEEPSAKE_BLINDSIDE',talents['shadow-claw'])

    def test_planning_duplicate_invariant(self):
        import sys
        from unittest import mock
        sys.path.insert(0,str(ROOT/'tools'))
        import audit_completion as audit
        lines = [
            '{id="shadow-claw", name="shadow claw", define_as="SHADOW_CLAW", shared_name=true},',
            '{id="shadow-caster", name="shadow claw", define_as="SHADOW_CASTER", shared_name=true},',
        ]
        manifest = json.dumps({'assets':[{'id':'shadow-claw'},{'id':'shadow-caster'}]})
        def check(source):
            with mock.patch.object(Path,'read_text',side_effect=[source,manifest]):
                return audit.current_catalog()
        self.assertEqual(check('\n'.join(lines)),{'shadow claw':'shadow-claw;shadow-caster'})
        for source in (
            '\n'.join(lines).replace('shared_name=true','shared_name=false',1),
            '\n'.join(lines).replace('SHADOW_CASTER','SHADOW_CLAW'),
            '\n'.join(lines).replace('define_as="SHADOW_CASTER", ',''),
        ):
            with self.assertRaises(ValueError): check(source)

    def test_shared_name_refinement_selects_one_identity(self):
        import sys
        from unittest import mock
        sys.path.insert(0,str(ROOT/'tools'))
        import art_tasks
        catalog={'shadow claw':'shadow-claw;shadow-caster'}
        for id_ in ('shadow-claw','shadow-caster'):
            asset={'asset_id':id_,'kind':'creature','refinement':{
                'supersedes':id_,'previous_batch':'monster-batch-ag',
                'design_change_reason':'A separately reviewed change of creature silhouette and pose. '*3,
                'evidence':[{'path':'pinned-review','sha256':'0'*64}]}}
            with mock.patch.object(art_tasks,'pinned'):
                art_tasks.refinement_gate(asset,'shadow claw',catalog)
            asset['refinement']['supersedes']='shadow-caster' if id_=='shadow-claw' else 'shadow-claw'
            with self.assertRaisesRegex(ValueError,'must supersede'):
                art_tasks.refinement_gate(asset,'shadow claw',catalog)

    def test_generation_pins_and_budget(self):
        calls = list((ROOT / 'art/production/handoffs').glob('monster-batch-ag-*/*/imagegen-calls/call-*/call.json'))
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
                self.assertEqual(hashlib.sha256(master.read_bytes()).hexdigest(), d['sha256'])
                self.assertTrue(d['provenance']['ok'])
                self.assertTrue(d['gate_passed'])
                recorded[d['asset_id']] = d['sha256']
        self.assertEqual(set(per),set(SCOPE))
        self.assertEqual(set(recorded),set(IDS))
        failed2=json.loads((ROOT/'art/production/handoffs/monster-batch-ag-3/shadow-caster/imagegen-calls/call-2/call.json').read_text())
        self.assertEqual(failed2['outcome'],'style-gate-rejected')
        self.assertEqual(hashlib.sha256((ART/'superseded/shadow-caster-v2.png').read_bytes()).hexdigest(),failed2['sha256'])
        abandoned=ROOT/'art/production/handoffs/monster-batch-ag-1/multi-hued-drake-hatchling/imagegen-calls/call-1'
        self.assertTrue((abandoned/'envelope-prompt.txt').is_file())
        self.assertFalse((abandoned/'result.json').exists())
        self.assertEqual(json.loads((ART/'handover-call-audit.json').read_text())['classification'],'RETRY')
        rejected=ART/'superseded/shadow-caster-v1.png'
        failed=json.loads((ROOT/'art/production/handoffs/monster-batch-ag-3/shadow-caster/imagegen-calls/call-1/call.json').read_text())
        self.assertEqual(failed['outcome'],'style-gate-rejected')
        self.assertEqual(failed['style_gate']['blocking'],['base_drift'])
        self.assertEqual(hashlib.sha256(rejected.read_bytes()).hexdigest(),failed['sha256'])
        self.assertNotIn('superseded/shadow-caster-v1.png',json.loads((ART/'selected-masters.json').read_text()).values())
        intervals.sort()
        for before, after in zip(intervals, intervals[1:]):
            self.assertLessEqual(before[1],after[0], 'ImageGen calls must be serial')
        dirs=list((ROOT/'art/production/handoffs').glob('monster-batch-ag-*/*/imagegen-calls/call-*'))
        counts={}
        for folder in dirs:
            asset=folder.parents[1].name
            counts[asset]=counts.get(asset,0)+1
        self.assertEqual(set(counts),set(SCOPE))
        request=json.loads((ROOT/'evidence/monster-batch-ag-rework-20261001/review-request.json').read_text())
        self.assertEqual(request['authorized_additional_serial_calls'],4)
        self.assertLessEqual(counts['shadow-caster']-2,4)
        for asset,count in counts.items():
            if asset!='shadow-caster': self.assertLessEqual(count,2)
        for pack in (ROOT/'art/production/handoffs').glob('monster-batch-ag-*/*'):
            folders=list((pack/'imagegen-calls').glob('call-*'))
            if folders: self.assertLessEqual(len(folders),2)
        self.assertLessEqual(len(calls),18)
        digest = hashlib.sha256(EVIDENCE.read_bytes()).hexdigest()
        for p in (ROOT / 'art/production/batches').glob('monster-batch-ag-*.json'):
            for a in json.loads(p.read_text())['assets']:
                self.assertEqual(a['render_evidence'][0]['sha256'],digest)


if __name__ == '__main__': unittest.main()
