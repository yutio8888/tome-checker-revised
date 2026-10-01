"""UA unique/boss source, art and byte admission; frozen AE/AF thresholds."""
import hashlib,importlib.util,json,math,os,re,unittest
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
ART=ROOT/'art/monster-batch-ua'
EVIDENCE=ROOT/'evidence/monster-batch-ua-20261001'
BODY_MINIMUM=65.0
FLOOR=45.0
ALL_IDS=['kra-tor','khulmanar','rungof','grgglck','queen-ant','ak-gishil','ninandra','phoenix','the-shade','ukruk','gorbat','grushnak','vor']
GROUPS=('orc-bosses','insect-bosses','horror-demon-bosses','beast-bosses')
EXPECTED_DEFINES={'phoenix':'NPC_PHOENIX','the-shade':'SHADE','ukruk':'UKRUK','gorbat':'GORBAT','grushnak':'GRUSHNAK','vor':'VOR'}
spec=importlib.util.spec_from_file_location('ua_style',ROOT/'tools/check_token_style.py');style=importlib.util.module_from_spec(spec);spec.loader.exec_module(style)
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def accepted():return read(ART/'final-admission.json')['accepted_ids']
class UAShippedTests(unittest.TestCase):
 def test_original_gates_without_waiver(self):
  selected=read(ART/'selected-masters.json');self.assertEqual(set(selected),set(accepted()))
  self.assertEqual([a['id'] for a in read(ART/'catalog.json')],accepted())
  for i,m in selected.items():
   r=style.check_asset(ART/f'sprites/128/{i}.png',ART/m,i,allow_grandfather=False)
   self.assertTrue(r['passed'],(i,r));self.assertEqual(r['blocking'],[]);self.assertEqual(r['warnings'],[]);self.assertFalse(r['waived'])
  self.assertFalse((ROOT/'art/production/waivers/monster-batch-ua.json').exists())
 def test_body_luminance_original_floor(self):
  lum=read(ART/'review/luminance.json');self.assertEqual(lum['floor_minimum_for_body'],FLOOR)
  for i in accepted():
   with Image.open(ART/f'sprites/128/{i}.png') as im:
    vals=[.299*r+.587*g+.114*b for y in range(128) for x in range(128) for r,g,b,a in [im.getpixel((x,y))] if a>=180 and math.hypot(x+.5-64,y+.5-64)/64<=.55]
   mean=round(sum(vals)/len(vals),2);self.assertEqual(lum['assets'][i],mean);self.assertGreaterEqual(mean,BODY_MINIMUM,i)
 def test_runtime_bytes_and_unchanged_baseline(self):
  manifest=read(ROOT/'data/token-manifest.json');base=read(EVIDENCE/'unchanged-baseline.json')
  first=next(n for n,a in enumerate(manifest['assets']) if a['batch']=='monster-batch-ua')
  prev=manifest['assets'][:first]
  self.assertEqual(len(prev),base['pre_ua_manifest_asset_count'])
  self.assertEqual(hashlib.sha256(json.dumps(prev,sort_keys=True,separators=(',',':')).encode()).hexdigest(),base['pre_ua_manifest_assets_sha256'])
  entries={a['id']:a for a in manifest['assets']};report={a['id']:a for a in read(ART/'export-report.json')['assets']};selected=read(ART/'selected-masters.json')
  for i in accepted():
   self.assertEqual(entries[i]['batch'],'monster-batch-ua');self.assertEqual(entries[i]['runtime_sha256'],sha(ART/f'sprites/128/{i}.png'))
   self.assertEqual(entries[i]['master_sha256'],sha(ART/selected[i]));self.assertEqual((ROOT/f'data/gfx/tokens/{i}.png').read_bytes(),(ART/f'sprites/128/{i}.png').read_bytes());self.assertFalse(report[i]['style_gate']['advisory_downgrade'])
   for sz in (48,64,96,128,256):
    with Image.open(ART/f'sprites/{sz}/{i}.png') as im:
     self.assertEqual(im.size,(sz,sz));self.assertEqual(im.mode,'RGBA');self.assertTrue(all(im.getpixel(p)[3]==0 for p in ((0,0),(0,sz-1),(sz-1,0),(sz-1,sz-1))))
 def test_review_with_shipped_siblings_and_frozen_floors(self):
  for g in GROUPS:
   for mode in ('color','grayscale'):self.assertTrue((ART/f'review/{g}-{mode}-48-64-96.png').is_file())
  for n in ('floor-readability-48.png','floor-readability-48-x2.png','floor-readability-48-x2-b.png'):self.assertTrue((ART/'review'/n).exists())
  for p in read(ART/'review/floor-source-pins.json').values():self.assertEqual(sha(ROOT/p['path']),p['sha256'])
  text=(ART/'make_review_sheets.py').read_text()
  for i in ('orc-master-wyrmic','orc-elite-fighter','giant-army-ant','weaver-queen','weaver-matriarch','blade-horror','nightmare-horror','champion-of-urh-rok','forge-giant','warg','faeros'):self.assertIn("'"+i+"'",text)
class UAContractsTests(unittest.TestCase):
 def test_exact_13_unique_sources_and_define_as(self):
  ev=read(ART/'source-contracts.json');self.assertEqual([i['id'] for i in ev['identities']],ALL_IDS)
  pins=ev['auxiliary_sources']+read(ART/'supplement-source-pins.json');source=(ROOT/'overload/mod/class/CheckerTokens.lua').read_text();ws=ROOT.parents[2]
  for i in ev['identities']:
   self.assertTrue(i['unique']);self.assertEqual(i['define_as'],EXPECTED_DEFINES.get(i['id']));pins+=i['sources']
   self.assertEqual(sha(ws/i['native_image_path']),i['native_image_sha256'])
   with Image.open(ws/i['native_image_path']) as im:self.assertEqual(list(im.size),i['native_image_size'])
   if i['id'] not in accepted():
    self.assertNotIn('{id="'+i['id']+'",',source);continue
   line=next(l for l in source.splitlines() if '{id="'+i['id']+'",' in l)
   self.assertIn('unique=true',line);self.assertNotIn('native_tall=',line);self.assertNotIn('native_shader=',line)
   for key,val in (('name',i['native_name']),('image',i['native_image']),('type',i['type']),('subtype',i['subtype'])):self.assertIn(key+'="'+val+'"',line)
   if i['define_as']:self.assertIn('define_as="'+i['define_as']+'"',line)
   else:self.assertNotIn('define_as=',line)
  for pin in pins:
   p=ws/pin['path'];self.assertEqual(sha(p),pin['sha256']);self.assertIn(pin['anchor'],p.read_text().splitlines()[pin['line']-1])
  shade=next(i for i in ev['identities'] if i['id']=='the-shade');self.assertEqual(shade['shader'],'unique_glow');self.assertIn('unique_glow',read(ART/'final-admission.json')['native']['the-shade'])
 def test_talents_resolve_and_bird_egg_is_native(self):
  talents=read(ART/'talent-contracts.json');self.assertEqual(set(talents),set(ALL_IDS))
  for rows in talents.values():
   for p in rows.values():self.assertEqual(sha(ROOT.parents[2]/'game/modules/tome'/p['path']),p['sha256'])
  self.assertIn('addShaderAura',str(talents['phoenix']['T_BODY_OF_FIRE']['display_hits']))
  txt=(ROOT.parents[2]/'game/modules/tome/data/timed_effects/magical.lua').read_text();self.assertIn('self.image = "object/egg_dragons_egg_06_64.png"',txt)
 def test_serial_builtin_provenance_and_budget(self):
  intervals=[]
  for pack in (ROOT/'art/production/handoffs').glob('monster-batch-ua-*/*'):
   if not (pack/'inputs.json').exists():continue
   calls=list(pack.glob('imagegen-calls/call-*/call.json'));task=read(pack/'inputs.json')['task'];self.assertLessEqual(len(calls),task['max_attempts'])
   for p in calls:
    d=read(p);self.assertEqual(d['codex_model'],'gpt-6.1-sol');self.assertTrue(d['codex_ephemeral']);intervals.append((d['timestamp_started'],d['timestamp_finished']))
    if d['outcome']=='recorded':
     m=ART/'masters'/Path(d['saved_output_path']).name
     if not m.exists():m=ART/'superseded'/m.name
     self.assertEqual(sha(m),d['sha256']);self.assertTrue(d['provenance']['ok']);self.assertTrue(d['gate_passed'])
  intervals.sort()
  for a,b in zip(intervals,intervals[1:]):self.assertLessEqual(a[1],b[0],'UA image calls must be serial')
 def test_official_chinese_names(self):
  names=read(ART/'official-names.json')
  self.assertEqual(names['path'],'/workspace/tome4-chinese-translation/mod-tome.lua')
  self.assertEqual(len(names['names']),13)
  source=Path(os.environ.get('TOME_CHECKER_PINNED_TRANSLATION',names['path']))
  if not source.is_file():
   self.skipTest(f'official translation source unavailable: {source}')
  # Match the recorded full line wherever it moved, then verify the EN/ZH
  # pair. An unrelated edit must not invalidate historical source evidence.
  lines=source.read_text(encoding='utf-8').splitlines()
  pair=re.compile(r'^\s*t\(\s*"((?:[^"\\]|\\.)*)"\s*,\s*"((?:[^"\\]|\\.)*)"')
  for row in names['names']:
   self.assertTrue(row['hits'])
   for hit in row['hits']:
    expected=hit['official_line']
    found=next((n for n,line in enumerate(lines,1) if line==expected),None)
    self.assertIsNotNone(found,f"{row['native_name']!r}: recorded official line missing in {source}: {expected!r}")
    parsed=pair.match(lines[found-1]);expected_pair=pair.match(expected)
    self.assertIsNotNone(parsed,f'official line {found} is not a t("EN", "ZH") pair')
    self.assertIsNotNone(expected_pair,f'recorded official line is not a pair: {expected!r}')
    self.assertEqual(parsed.group(1),row['native_name'])
    self.assertEqual(parsed.group(2),expected_pair.group(2))
 def test_generation_pins_and_retained_provenance_rejections(self):
  calls=list((ROOT/'art/production/handoffs').glob('monster-batch-ua-*/*/imagegen-calls/call-*/call.json'))
  self.assertEqual(len(calls),17)
  outcomes=[read(p)['outcome'] for p in calls]
  self.assertEqual(outcomes.count('recorded'),15)
  self.assertEqual(outcomes.count('provenance-rejected'),2)
  for pack in (ROOT/'art/production/handoffs').glob('monster-batch-ua-*/*'):
   if not (pack/'inputs.json').is_file():continue
   task=read(pack/'inputs.json')['task']
   for pin in task['sources']:
    p=ROOT.parents[2]/pin['path'];self.assertEqual(sha(p),pin['sha256']);self.assertIn(pin['anchor'],p.read_text().splitlines()[pin['line']-1])
   for pin in task['references']+task['render_evidence']:
    self.assertEqual(sha(ROOT.parents[2]/pin['path']),pin['sha256'])
  for n in (1,2):
   ev=read(ART/f'superseded/grushnak-unreported-call-{n}.json')
   self.assertEqual(sha(ROOT/ev['call']),ev['call_sha256'])
   for pin in ev['retained']:
    self.assertFalse(pin['admitted']);self.assertEqual(sha(ROOT/pin['retained']),pin['sha256'])
  self.assertEqual(set(accepted()),set(ALL_IDS)-{'the-shade'})
  for i in ('the-shade',):
   self.assertFalse((ROOT/f'data/gfx/tokens/{i}.png').exists())

 def test_coordinator_rework_lineage_and_unchanged_assets(self):
  selected=read(ART/'selected-masters.json');before=read(ART/'rework/before-selected-masters.json')
  for i in ('rungof','ninandra','grgglck'):
   self.assertEqual(before[i],f'masters/{i}-v1.png')
   self.assertEqual(selected[i],f'masters/{i}-v2.png')
   self.assertNotEqual(sha(ART/before[i]),sha(ART/selected[i]))
  self.assertEqual(selected['grushnak'],'masters/grushnak-v1.png')
  baseline=read(ART/'rework/unchanged-baseline.json')
  for i,h in baseline['unchanged_runtime_sha256'].items():self.assertEqual(sha(ROOT/f'data/gfx/tokens/{i}.png'),h,i)
  entries={a['id']:a for a in read(ROOT/'data/token-manifest.json')['assets']}
  for row in baseline['before_manifest']['assets']:
   if row['id'] not in ('rungof','ninandra','grgglck'):self.assertEqual(entries[row['id']],row)
  for i in set(before)-{'rungof','ninandra','grgglck'}:self.assertEqual(selected[i],before[i])
  self.assertTrue((ART/'review/grushnak-infrastructure-retry-resolved.json').is_file())
  self.assertFalse((ART/'review/grushnak-PENDING-art-admission.json').exists())
  self.assertTrue((ART/'review/rework-before-after-color-48-64-96.png').is_file())
