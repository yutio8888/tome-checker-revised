#!/usr/bin/env python3
"""Batch 4 terrain: source probe and per-level cold-start validation.

Isolated offline fixture only (tools/launch_fixture.py). Every validation scene
is its own cold start; the probe visits all scenes in one process because it
only reads final native grids. Every process this tool starts is stopped.
"""
import argparse,json,shutil,statistics,subprocess,sys,time
from pathlib import Path
from PIL import Image,ImageStat
from capture_korpul import Fixture,HOME,ROOT,SESSION,digest,png_size
from run_norgos_validation import stop_started
OUT=ROOT/'evidence/batch4-20260929';SHOTS=OUT/'screenshots'
# (zone, level, enter options, label suffix)
SCENES=[
 ('murgol-lair',1,{'invasion':False},'default'),('murgol-lair',2,{'invasion':False},'default'),
 ('murgol-lair',3,{'invasion':False},'default'),('murgol-lair',1,{'invasion':True},'invasion'),
 ('murgol-lair',2,{'invasion':True},'invasion'),('murgol-lair',3,{'invasion':True},'invasion'),
 ('south-beach',1,{},'static'),
 ('keepsake-meadow',1,{},'static'),('keepsake-meadow',2,{},'static'),('keepsake-meadow',3,{},'static'),
 ('keepsake-meadow',4,{},'cavern'),('keepsake-meadow',5,{},'cavern'),('keepsake-meadow',6,{},'static'),
 ('conclave-vault',1,{},'static'),('conclave-vault',2,{},'roomer'),('conclave-vault',3,{},'roomer'),
 ('conclave-vault',4,{},'roomer'),
 ('noxious-caldera',1,{},'tunnel'),('noxious-caldera',2,{},'caldera'),
]
def label(zone,level,suffix):return f'{zone}-{suffix}-L{level}'
def lua_opts(opts):
 return '{'+','.join(f"{k}={'true' if v else 'false'}" for k,v in opts.items())+'}'
def read(name):
 p=HOME/name;value=json.loads(p.read_text());p.unlink();return value
def launch():
 running=[]
 for proc in Path('/proc').iterdir():
  try:argv0=(proc/'cmdline').read_bytes().split(b'\0')[0].decode(errors='replace')
  except OSError:continue
  if argv0.endswith('session/runtime/t-engine') or argv0.endswith('Xvfb-local'):running.append(proc.name)
 if running:raise RuntimeError('another fixture process is running: '+' '.join(running))
 call=subprocess.run([sys.executable,str(ROOT/'tools/launch_fixture.py'),'--shaders','--tiles','64','--terrain','refined',
  '--resolution','1920x1080','--birth','Human:Cornac:Male:Berserker'],cwd=ROOT,capture_output=True,text=True)
 if call.returncode:raise RuntimeError(call.stdout+call.stderr)
 time.sleep(2)
 return json.loads((SESSION/'processes.json').read_text())

def probe(args):
 OUT.mkdir(parents=True,exist_ok=True);meta=launch();f=Fixture();result={'scenes':[]}
 try:
  f.lua("ms=dofile('/data-checker-fixture/monster-live_map_survey.lua');ms.setup()")
  for zone,level,opts,suffix in SCENES:
   if args.zone and args.zone!=zone:continue
   f.lua(f"ms.dump('/b4-enter.json',ms.enter('{zone}',{level},{lua_opts(opts)}))");enter=read('b4-enter.json')
   f.lua("ms.caveClearDialogs();ms.dump('/b4-probe.json',ms.batch4Probe())");rows=read('b4-probe.json')
   result['scenes'].append({'label':label(zone,level,suffix),'enter':enter,'probe':rows})
   print('PROBE',label(zone,level,suffix),len(rows['rows']),flush=True)
  (OUT/('probe.json' if not args.zone else f'probe-{args.zone}.json')).write_text(json.dumps(result,ensure_ascii=False,indent=1)+'\n')
 finally:
  (OUT/'probe-transcript.txt').write_text((''.join(f.transcript)+f.new_log()).rstrip()+'\n')
  stop_started(meta);print('STOP probe',flush=True)

def capture(zone,level,opts,suffix):
 name=label(zone,level,suffix)
 f=Fixture();SHOTS.mkdir(parents=True,exist_ok=True)
 plan=json.loads((SESSION/'launch-plan.json').read_text())
 assert plan['fixture'] and plan['shaders'] and plan['terrain']=='refined' and plan['resolution']=='1920x1080'
 assert digest(SESSION/'runtime/game/addons/tome-checker-revised/overload/mod/class/CheckerTerrain.lua')==digest(ROOT/'overload/mod/class/CheckerTerrain.lua')
 def dump(code,file):
  f.lua(f"ms.dump('/{file}',{code})");return read(file)
 def size(tile):
  f.lua(f"game:setResolution('1920x1080 Windowed',true);config.settings.tome.gfx.size='{tile}x{tile}';game:setupDisplayMode(false);ms.focus(game.player.x,game.player.y)")
 def shot(tile,tag):
  file=f'{name}-{tag}-{tile}';src=HOME/(file+'.png');src.unlink(missing_ok=True)
  call=subprocess.run([sys.executable,str(ROOT/'tools/fixture_command.py'),'shot',file],capture_output=True,text=True,timeout=35)
  f.transcript.append(call.stdout+call.stderr);f.check_log()
  assert call.returncode==0 and src.is_file() and png_size(src)==(1920,1080),(call.stdout,call.stderr)
  dst=SHOTS/src.name;shutil.copy2(src,dst)
  return {'file':'screenshots/'+dst.name,'sha256':digest(dst),'tile':tile,'tag':tag}
 def pixels(frame,lit):
  im=Image.open(SHOTS/Path(frame['file']).name).convert('L');samples=[]
  for pair in lit['pairs']:
   def mean(cell):
    x,y,s=cell['sx'],cell['sy'],lit['tile']
    return ImageStat.Stat(im.crop((int(x+s*.3),int(y+s*.3),int(x+s*.7),int(y+s*.7)))).mean[0]
   samples.append({'floor':mean(pair['floor']),'wall':mean(pair['wall'])})
  if len(samples)<2:return {'pairs':len(samples)}
  floor=statistics.median(v['floor'] for v in samples);wall=statistics.median(v['wall'] for v in samples)
  return {'pairs':len(samples),'floor':floor,'wall':wall,'relative_gap':(floor-wall)/floor}
 row={'label':name,'zone':zone,'level':level,'options':opts,'launch':plan,'screenshots':[]}
 try:
  f.lua("assert(config.settings.cheat and config.settings.disable_all_connectivity and not profile.auth);assert(core.shader.active(4));ms=dofile('/data-checker-fixture/monster-live_map_survey.lua');ms.setup()")
  row['enter']=dump(f"ms.enter('{zone}',{level},{lua_opts(opts)})",'b4-enter.json')
  f.lua('ms.caveClearDialogs()')
  row['census']=dump('ms.terrainCensus()','b4-census.json')
  row['details']=dump('ms.reuseDetails()','b4-details.json')
  row['rules_before']=dump('ms.batch4RuleSnapshot()','b4-rules-before.json')
  assert row['census']['supported']>0 and row['census']['native']==0,row['census']
  pose=dump('ms.reusePose(false)','b4-pose.json');row['open_pose']=pose;assert pose['found'],pose
  size(64);lit=dump('ms.reuseLitPairs()','b4-lit.json');row['lit_pairs']=lit
  natural=shot(64,'natural');row['screenshots'].append(natural)
  row['lit_pixels']=pixels(natural,lit)
  for tile in (48,64,96):
   size(tile);f.lua('ms.reuseStageView()')
   staged=dump('ms.reuseLitPairs()','b4-staged-lit.json') if tile==64 else None
   frame=shot(tile,'open');row['screenshots'].append(frame)
   if staged:row['staged_lit_pixels']=pixels(frame,staged)
  size(64);row['feature_pose']=dump('ms.batch4FeaturePose()','b4-feature.json')
  if row['feature_pose']['found']:row['screenshots'].append(shot(64,'feature'))
  size(64);row['exit_pose']=dump('ms.reusePose(true)','b4-exit.json')
  if row['exit_pose'].get('exit'):row['screenshots'].append(shot(64,'exit'))
  size(64);row['remembered']=dump('ms.reuseRemembered()','b4-memory.json')
  if row['remembered']['found']:row['screenshots'].append(shot(64,'remembered'))
  turn_before=dump('{turn=game.turn,x=game.player.x,y=game.player.y,level=game.level.level,zone=game.zone.short_name}','b4-turn-a.json')
  row['modes']=dump("(function() ms.setMode('vanilla');local v=ms.terrainCensus();ms.setMode('blockout');local b=ms.terrainCensus();ms.setMode('refined');local r=ms.terrainCensus();return {vanilla=v,blockout=b,refined=r} end)()",'b4-modes.json')
  turn_after=dump('{turn=game.turn,x=game.player.x,y=game.player.y,level=game.level.level,zone=game.zone.short_name}','b4-turn-b.json')
  row['round_trip']={'before':turn_before,'after':turn_after,'same':turn_before==turn_after}
  assert row['round_trip']['same'],row['round_trip']
  assert row['modes']['vanilla']['owned']==0 and row['modes']['refined']['native']==0,row['modes']
  row['rules_after']=dump('ms.batch4RuleSnapshot()','b4-rules-after.json')
  assert row['rules_before']==row['rules_after'],'rule snapshot changed'
  row['dig']=dump('ms.batch4Dig()','b4-dig.json')
  if row['dig'].get('found'):
   assert row['dig']['census']['native']==0,row['dig']
   row['screenshots'].append(shot(64,'dig'))
  return row
 finally:
  (OUT/f'validation-{name}.txt').write_text((''.join(f.transcript)+f.new_log()).rstrip()+'\n')

def validate(args):
 OUT.mkdir(parents=True,exist_ok=True);path=OUT/'survey.json'
 survey=json.loads(path.read_text()) if path.exists() else {'scenes':[]}
 for zone,level,opts,suffix in SCENES:
  name=label(zone,level,suffix)
  if args.zone and args.zone!=zone or args.level and args.level!=level or args.suffix and args.suffix!=suffix:continue
  if args.redo:survey['scenes']=[s for s in survey['scenes'] if s['label']!=name]
  elif any(s['label']==name for s in survey['scenes']):continue
  meta=launch()
  try:
   row=capture(zone,level,opts,suffix);survey['scenes'].append(row)
   path.write_text(json.dumps(survey,ensure_ascii=False,indent=1)+'\n')
   print('PASS',name,row['census']['supported'],row['census']['owned'],row['census']['native'],
    row.get('lit_pixels',{}).get('relative_gap'),flush=True)
  finally:stop_started(meta);print('STOP',name,flush=True)

def main():
 p=argparse.ArgumentParser();p.add_argument('command',choices=('probe','validate'))
 p.add_argument('--zone');p.add_argument('--level',type=int);p.add_argument('--suffix');p.add_argument('--redo',action='store_true')
 a=p.parse_args()
 (probe if a.command=='probe' else validate)(a)
if __name__=='__main__':main()
