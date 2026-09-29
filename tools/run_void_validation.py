#!/usr/bin/env python3
"""Cold-start source and rendered-frame validation for the void family."""
import argparse,json,shutil,statistics,subprocess,sys,time
from pathlib import Path
from PIL import Image,ImageStat
from capture_korpul import Fixture,HOME,ROOT,SESSION,digest,png_size
from run_norgos_validation import stop_started

OUT=ROOT/'evidence/void-20260928';SHOTS=OUT/'screenshots'
SCENES=[('unhallowed-morass',n) for n in range(1,4)]+[('abashed-expanse',n) for n in range(1,4)]+[('temporal-rift',n) for n in range(1,5)]
def read(name):
 p=HOME/name;value=json.loads(p.read_text());p.unlink();return value

def capture(zone,level):
 label=f'{zone}-L{level}';f=Fixture();SHOTS.mkdir(exist_ok=True)
 plan=json.loads((SESSION/'launch-plan.json').read_text())
 assert plan['fixture'] and plan['shaders'] and plan['terrain']=='refined'
 assert digest(SESSION/'runtime/game/addons/tome-checker-revised/overload/mod/class/CheckerTerrain.lua')==digest(ROOT/'overload/mod/class/CheckerTerrain.lua')
 assert digest(SESSION/'runtime/game/addons/tome-checker-fixture/data/monster-live_map_survey.lua')==digest(ROOT/'tests/live_map_survey.lua')
 for name in ('floor0.png','rift-15-0.png','rocks-15-0.png','space0.png'):
  assert digest(SESSION/'runtime/game/addons/tome-checker-revised/data/gfx/refined/void'/name)==digest(ROOT/'data/gfx/refined/void'/name)
 def dump(code,name):
  f.lua(f"ms.dump('/{name}',{code})");return read(name)
 def size(tile):
  f.lua(f"game:setResolution('1920x1080 Windowed',true);config.settings.tome.gfx.size='{tile}x{tile}';game:setupDisplayMode(false);ms.focus(game.player.x,game.player.y)")
 def shot(tile,tag):
  name=f'{label}-{tag}-{tile}';src=HOME/(name+'.png');src.unlink(missing_ok=True)
  call=subprocess.run([sys.executable,str(ROOT/'tools/fixture_command.py'),'shot',name],capture_output=True,text=True,timeout=35)
  f.transcript.append(call.stdout+call.stderr);f.check_log()
  assert call.returncode==0 and src.is_file() and png_size(src)==(1920,1080),(call.stdout,call.stderr)
  dst=SHOTS/src.name;shutil.copy2(src,dst)
  return {'file':'screenshots/'+dst.name,'sha256':digest(dst),'tile':tile,'tag':tag}
 row={'label':label,'zone':zone,'level':level,'launch':plan,'screenshots':[]}
 try:
  f.lua("assert(config.settings.cheat and config.settings.disable_all_connectivity and not profile.auth);assert(core.shader.active(4));ms=dofile('/data-checker-fixture/monster-live_map_survey.lua');ms.setup()")
  row['enter']=dump(f"ms.enter('{zone}',{level})",'void-enter.json')
  f.lua('ms.caveClearDialogs()')
  row['census']=dump('ms.terrainCensus()','void-census.json')
  row['details']=dump('ms.reuseDetails()','void-details.json')
  assert row['census']['supported']>0 and row['census']['native']==0,row['census']
  pose=dump('ms.reusePose(false)','void-pose.json');row['open_pose']=pose;assert pose['found'],pose
  size(64)
  lit=dump('ms.reuseLitPairs()','void-lit.json');row['lit_pairs']=lit
  natural=shot(64,'natural');row['screenshots'].append(natural)
  if level==1:
   im=Image.open(SHOTS/Path(natural['file']).name).convert('L');samples=[]
   for pair in lit['pairs']:
    def mean(cell):
     x,y,s=cell['sx'],cell['sy'],lit['tile']
     return ImageStat.Stat(im.crop((int(x+s*.3),int(y+s*.3),int(x+s*.7),int(y+s*.7)))).mean[0]
    samples.append({'floor':mean(pair['floor']),'wall':mean(pair['wall'])})
   assert len(samples)>=2,(label,len(samples))
   floor=statistics.median(v['floor'] for v in samples);wall=statistics.median(v['wall'] for v in samples)
   row['lit_pixels']={'pairs':len(samples),'floor':floor,'wall':wall,'relative_gap':(floor-wall)/floor,'samples':samples}
   assert row['lit_pixels']['relative_gap']>.18,row['lit_pixels']
   for tile in (48,96):size(tile);row['screenshots'].append(shot(tile,'natural'))
  for tile in ((48,64,96) if level==1 else (64,)):
   size(tile);f.lua('ms.reuseStageView()');row['screenshots'].append(shot(tile,'open'))
  exitpose=dump('ms.voidExitPose()','void-exit.json') if zone!='temporal-rift' or level==1 else dump('ms.reusePose(true)','void-exit.json')
  row['exit_pose']=exitpose
  if exitpose['found'] and (zone=='abashed-expanse' and exitpose.get('id')=='WORMHOLE' or
   row['details']['exits'] and (zone!='temporal-rift' or level==1 or exitpose.get('exit_distance',999)<=8)):
   size(64);f.lua('ms.reuseStageView()');row['screenshots'].append(shot(64,'wormhole' if zone=='abashed-expanse' else 'exit'))
  size(64)
  row['remembered']=dump('ms.reuseRemembered()','void-memory.json')
  if row['remembered']['found']:
   for tile in ((48,64,96) if level==1 else (64,)):
    size(tile);row['screenshots'].append(shot(tile,'remembered'))
  row['modes']=dump("(function() ms.setMode('vanilla');local v=ms.terrainCensus();ms.setMode('blockout');local b=ms.terrainCensus();ms.setMode('refined');local r=ms.terrainCensus();return {vanilla=v,blockout=b,refined=r} end)()",'void-modes.json')
  assert row['modes']['vanilla']['owned']==0 and row['modes']['refined']['native']==0,row['modes']
  if zone!='temporal-rift' or level!=2:assert row['modes']['blockout']['native']==0,row['modes']
  return row
 finally:
  (OUT/f'validation-{label}.txt').write_text((''.join(f.transcript)+f.new_log()).rstrip()+'\n')

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--zone');parser.add_argument('--level',type=int);args=parser.parse_args()
 OUT.mkdir(exist_ok=True);path=OUT/'survey.json';survey=json.loads(path.read_text()) if path.exists() else {'scenes':[]}
 for zone,level in SCENES:
  if args.zone and args.zone!=zone or args.level and args.level!=level:continue
  label=f'{zone}-L{level}'
  if any(s['label']==label for s in survey['scenes']):continue
  launch=subprocess.run([sys.executable,str(ROOT/'tools/launch_fixture.py'),'--shaders','--tiles','64','--terrain','refined','--resolution','1920x1080','--birth','Human:Cornac:Male:Berserker'],cwd=ROOT,capture_output=True,text=True)
  if launch.returncode:raise RuntimeError(launch.stdout+launch.stderr)
  meta=json.loads((SESSION/'processes.json').read_text())
  try:
   time.sleep(2);row=capture(zone,level);survey['scenes'].append(row);path.write_text(json.dumps(survey,ensure_ascii=False,indent=2)+'\n')
   print('PASS',label,row['census'],row.get('lit_pixels',{}).get('relative_gap'),flush=True)
  finally:stop_started(meta);print('STOP',label,flush=True)
if __name__=='__main__':main()
