#!/usr/bin/env python3
"""Six independent Maze cold starts in the isolated offline fixture."""
import argparse, json, shutil, subprocess, sys, time
from pathlib import Path
from capture_korpul import Fixture, HOME, ROOT, SESSION, digest, png_size
from run_norgos_validation import stop_started

OUT=ROOT/'evidence/maze-20260928'; SHOTS=OUT/'screenshots'; PROCESSES=SESSION/'processes.json'

def read(name):
 p=HOME/name;data=json.loads(p.read_text());p.unlink(missing_ok=True);return data

def capture(layout,level,rework=False):
 label=f'maze-{layout}-L{level}';f=Fixture();SHOTS.mkdir(parents=True,exist_ok=True)
 plan=json.loads((SESSION/'launch-plan.json').read_text())
 assert plan['fixture'] and plan['shaders'] and plan['resolution']=='1920x1080'
 for rel in ('overload/mod/class/CheckerTerrain.lua','superload/engine/Map.lua','superload/mod/class/Grid.lua'):
  assert digest(SESSION/'runtime/game/addons/tome-checker-revised'/rel)==digest(ROOT/rel)
 assert digest(SESSION/'runtime/game/addons/tome-checker-fixture/data/monster-live_map_survey.lua')==digest(ROOT/'tests/live_map_survey.lua')
 result_path=OUT/'survey.json';result=json.loads(result_path.read_text()) if result_path.exists() else {'zones':[]}
 if rework:result['zones']=[z for z in result['zones'] if z['label']!=label]
 else:assert not any(z['label']==label for z in result['zones'])
 result.setdefault('launches',{})[label]=plan
 def save():
  result_path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
  (OUT/f'validation-{label}.txt').write_text((''.join(f.transcript)+f.new_log()).rstrip()+'\n')
 def shot(tile):
  name=f'{label}-open-{tile}';source=HOME/(name+'.png');source.unlink(missing_ok=True)
  p=subprocess.run([sys.executable,str(ROOT/'tools/fixture_command.py'),'shot',name],capture_output=True,text=True,timeout=30)
  f.transcript.append(p.stdout+p.stderr);f.check_log()
  assert p.returncode==0 and source.is_file() and png_size(source)==(1920,1080),name
  target=SHOTS/source.name;shutil.copy2(source,target)
  return {'file':'screenshots/'+target.name,'sha256':digest(target),'tile':tile}
 try:
  f.lua("assert(config.settings.cheat and config.settings.disable_all_connectivity and not profile.auth);assert(core.shader.active(4));ms=dofile('/data-checker-fixture/monster-live_map_survey.lua');ms.setup()")
  collapsed='true' if layout=='collapsed' else 'false'
  f.lua(f"local enter=ms.enter('maze',{level},{{collapsed={collapsed}}});local terrain=ms.terrainCensus();local details=ms.mazeDetails();ms.dump('/maze-result.json',{{enter=enter,terrain=terrain,details=details}})")
  data=read('maze-result.json');entry={'label':label,'layout':layout,'level':level,**data}
  assert entry['enter']['is_collapsed']==(layout=='collapsed'),entry['enter']
  assert entry['terrain']['supported']>0 and entry['terrain']['native']==0,entry['terrain']
  ids=entry['details']['ids']
  assert ids.get('OLD_FLOOR',{}).get('supported',0)>0,ids
  assert sum(v['supported'] for k,v in ids.items() if k.startswith('OLD_WALL'))>0,ids
  if layout=='collapsed' and level<4:
   assert entry['details']['cracks'] and all(c['kind']=='cracks' and c['pass_projectile'] and c['block_move']=='function' for c in entry['details']['cracks']),entry['details']['cracks']
  if layout=='default' and level==2:assert ids.get('QUICK_EXIT',{}).get('count',0)>0 and ids['QUICK_EXIT']['supported']==0,ids
  f.lua(f"local p=ms.mazeOpenPose({str(layout=='collapsed').lower()});ms.dump('/maze-pose.json',p)")
  entry['open_pose']=read('maze-pose.json');assert entry['open_pose']['found'] and entry['open_pose']['floor']>0 and entry['open_pose']['wall']>0,entry['open_pose']
  if rework:assert entry['open_pose']['cracks']>0 and entry['open_pose']['nearest_crack']<=2,entry['open_pose']
  entry['screenshots']=[]
  for tile in ((48,64,96) if level==1 or rework else (64,)):
   f.lua("game:setResolution('1920x1080 Windowed',true);"+f"config.settings.tome.gfx.size='{tile}x{tile}';game:setupDisplayMode(false);"+"ms.focus(game.player.x,game.player.y);ms.mazeStageView()")
   entry['screenshots'].append(shot(tile))
  f.lua("ms.setMode('vanilla');local v=ms.terrainCensus();ms.setMode('blockout');local b=ms.terrainCensus();ms.setMode('refined');local r=ms.terrainCensus();ms.dump('/maze-modes.json',{vanilla=v,blockout=b,refined=r})")
  entry['mode_round_trip']=read('maze-modes.json')
  assert entry['mode_round_trip']['vanilla']['owned']==0
  assert entry['mode_round_trip']['blockout']['owned']==0
  assert entry['mode_round_trip']['refined']['native']==0
  if layout=='collapsed' and level==1:
   f.lua("game:changeLevel(2,nil,{direct_switch=true});local m=ms.terrainCensus();local d=ms.mazeDetails();ms.dump('/maze-level-change.json',{level=game.level.level,variant=game.zone.is_collapsed and 'COLLAPSED' or 'DEFAULT',terrain=m,cracks=#d.cracks})")
   forward=read('maze-level-change.json')
   assert forward['level']==2 and forward['variant']=='COLLAPSED' and forward['terrain']['native']==0 and forward['cracks']>0,forward
   f.lua("game:changeLevel(1,nil,{direct_switch=true});local m=ms.terrainCensus();ms.dump('/maze-level-return.json',{level=game.level.level,terrain=m})")
   backward=read('maze-level-return.json')
   assert backward['level']==1 and backward['terrain']['native']==0,backward
   entry['level_change']={'forward':forward,'return':backward}
  result['zones'].append(entry);result['complete']=len(result['zones'])==6;save()
  print('OK',label,entry['terrain'],entry['open_pose'],flush=True)
 finally:save()

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--collapsed-rework',action='store_true');args=parser.parse_args()
 scenes=(('collapsed',1),('collapsed',2),('collapsed',3)) if args.collapsed_rework else tuple((layout,level) for layout,maxlevel in (('default',2),('collapsed',4)) for level in range(1,maxlevel+1))
 for layout,level in scenes:
   label=f'{layout}-L{level}'
   survey=OUT/'survey.json'
   if not args.collapsed_rework and survey.exists() and any(z['label']==f'maze-{label}' for z in json.loads(survey.read_text())['zones']):continue
   launch=subprocess.run([sys.executable,str(ROOT/'tools/launch_fixture.py'),'--shaders','--tiles','64','--terrain','refined','--resolution','1920x1080','--birth','Human:Cornac:Male:Berserker'],cwd=ROOT,capture_output=True,text=True)
   if launch.returncode:raise RuntimeError(f'{label} launch failed: {launch.stdout} {launch.stderr}')
   meta=json.loads(PROCESSES.read_text())
   try:
    print('START',label,launch.stdout.strip(),flush=True)
    for _ in range(180):
     if HOME.is_dir():break
     time.sleep(.5)
    else:raise RuntimeError(f'{label}: no fixture home')
    time.sleep(3);capture(layout,level,args.collapsed_rework)
   finally:
    stop_started(meta);print('STOP',label,meta['game'],meta['xvfb'],flush=True)
if __name__=='__main__':main()
