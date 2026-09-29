#!/usr/bin/env python3
"""Cold-start T5 source and rendered-frame checks in the isolated fixture."""
import argparse,json,shutil,statistics,subprocess,sys,time
from pathlib import Path
from PIL import Image,ImageStat
from capture_korpul import Fixture,HOME,ROOT,SESSION,digest,png_size
from run_norgos_validation import stop_started
OUT=ROOT/'evidence/t5-20260929';SHOTS=OUT/'screenshots'
SCENES=[('lake-nur',1,False),('lake-nur',1,True),('lake-nur',2,False),('lake-nur',2,True),('lake-nur',3,False),('lake-nur',3,True),('temporal-rift',4,None),('last-hope-graveyard',1,None),('last-hope-graveyard',2,None),('abashed-expanse',1,None),('abashed-expanse',2,None),('abashed-expanse',3,None)]
def read(name):
 p=HOME/name;value=json.loads(p.read_text());p.unlink();return value

def capture(zone,level,flooded):
 label=f'{zone}-{("flooded" if flooded else "default") if flooded is not None else "static"}-L{level}'
 f=Fixture();SHOTS.mkdir(exist_ok=True)
 plan=json.loads((SESSION/'launch-plan.json').read_text())
 assert plan['fixture'] and plan['shaders'] and plan['terrain']=='refined'
 assert digest(SESSION/'runtime/game/addons/tome-checker-revised/overload/mod/class/CheckerTerrain.lua')==digest(ROOT/'overload/mod/class/CheckerTerrain.lua')
 for name in ('floor0.png','wall-0-0.png','door-closed0.png'):
  assert digest(SESSION/'runtime/game/addons/tome-checker-revised/data/gfx/refined/underwater'/name)==digest(ROOT/'data/gfx/refined/underwater'/name)
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
 row={'label':label,'zone':zone,'level':level,'flooded':flooded,'launch':plan,'screenshots':[]}
 try:
  f.lua("assert(config.settings.cheat and config.settings.disable_all_connectivity and not profile.auth);assert(core.shader.active(4));ms=dofile('/data-checker-fixture/monster-live_map_survey.lua');ms.setup()")
  opt='{flooded=true}' if flooded is True else '{flooded=false}' if flooded is False else '{}'
  row['enter']=dump(f"ms.enter('{zone}',{level},{opt})",'t5-enter.json')
  f.lua('ms.caveClearDialogs()')
  row['census']=dump('ms.terrainCensus()','t5-census.json')
  row['details']=dump('ms.reuseDetails()','t5-details.json')
  if zone=='lake-nur':row['rules_before']=dump('ms.t5RuleSnapshot()','t5-rules-before.json')
  assert row['census']['supported']>0 and row['census']['native']==0,row['census']
  pose=dump('ms.reusePose(false)','t5-pose.json');row['open_pose']=pose;assert pose['found'],pose
  size(64);lit=dump('ms.reuseLitPairs()','t5-lit.json');row['lit_pairs']=lit
  natural=shot(64,'natural');row['screenshots'].append(natural)
  row['lit_pixels']=pixels(natural,lit)
  for tile in (48,64,96):
   size(tile);f.lua('ms.reuseStageView()')
   staged_lit=dump('ms.reuseLitPairs()','t5-staged-lit.json') if tile==64 else None
   frame=shot(tile,'open');row['screenshots'].append(frame)
   if staged_lit:row['staged_lit_pixels']=pixels(frame,staged_lit)
  if zone=='abashed-expanse' or zone=='last-hope-graveyard' and level==1:
   size(64);row['prop_pose']=dump('ms.t5PropPose()','t5-prop-pose.json')
   assert row['prop_pose']['found'],row['prop_pose']
   row['screenshots'].append(shot(64,'prop-close'))
  elif zone=='last-hope-graveyard':
   size(64);row['screenshots'].append(shot(64,'prop-close'))
  size(64);row['remembered']=dump('ms.reuseRemembered()','t5-memory.json')
  if row['remembered']['found']:row['screenshots'].append(shot(64,'remembered'))
  row['modes']=dump("(function() ms.setMode('vanilla');local v=ms.terrainCensus();ms.setMode('blockout');local b=ms.terrainCensus();ms.setMode('refined');local r=ms.terrainCensus();return {vanilla=v,blockout=b,refined=r} end)()",'t5-modes.json')
  assert row['modes']['vanilla']['owned']==0 and row['modes']['refined']['native']==0,row['modes']
  if zone=='lake-nur':
   row['rules_after']=dump('ms.t5RuleSnapshot()','t5-rules-after.json')
   assert row['rules_before']==row['rules_after'],(row['rules_before'],row['rules_after'])
  return row
 finally:
  (OUT/f'validation-{label}.txt').write_text((''.join(f.transcript)+f.new_log()).rstrip()+'\n')
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--zone');parser.add_argument('--level',type=int);parser.add_argument('--flooded',choices=('true','false'));args=parser.parse_args()
 OUT.mkdir(exist_ok=True);path=OUT/'survey.json';survey=json.loads(path.read_text()) if path.exists() else {'scenes':[]}
 for zone,level,flooded in SCENES:
  if args.zone and args.zone!=zone or args.level and args.level!=level or args.flooded and str(flooded).lower()!=args.flooded:continue
  label=f'{zone}-{("flooded" if flooded else "default") if flooded is not None else "static"}-L{level}'
  if any(s['label']==label for s in survey['scenes']):continue
  launch=subprocess.run([sys.executable,str(ROOT/'tools/launch_fixture.py'),'--shaders','--tiles','64','--terrain','refined','--resolution','1920x1080','--birth','Human:Cornac:Male:Berserker'],cwd=ROOT,capture_output=True,text=True)
  if launch.returncode:raise RuntimeError(launch.stdout+launch.stderr)
  meta=json.loads((SESSION/'processes.json').read_text())
  try:
   time.sleep(2);row=capture(zone,level,flooded);survey['scenes'].append(row);path.write_text(json.dumps(survey,ensure_ascii=False,indent=2)+'\n')
   print('PASS',label,row['census'],row.get('lit_pixels',{}).get('relative_gap'),flush=True)
  finally:stop_started(meta);print('STOP',label,flush=True)
if __name__=='__main__':main()
