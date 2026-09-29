#!/usr/bin/env python3
"""Independent shader-enabled Sandworm fixture starts and runtime evidence."""
import argparse,json,shutil,subprocess,sys,time
from pathlib import Path
from capture_korpul import Fixture,HOME,ROOT,SESSION,digest,png_size
from run_norgos_validation import stop_started
OUT=ROOT/'evidence/sandworm-20260928';SHOTS=OUT/'screenshots';PROCESSES=SESSION/'processes.json'

def read(name):
 p=HOME/name;data=json.loads(p.read_text());p.unlink(missing_ok=True);return data

def capture(layout,level,replace=False):
 label=f'{layout}-L{level}';f=Fixture();SHOTS.mkdir(parents=True,exist_ok=True)
 plan=json.loads((SESSION/'launch-plan.json').read_text())
 assert plan['fixture'] and plan['shaders'] and plan['resolution']=='1920x1080'
 assert digest(SESSION/'runtime/game/addons/tome-checker-revised/overload/mod/class/CheckerTerrain.lua')==digest(ROOT/'overload/mod/class/CheckerTerrain.lua')
 assert digest(SESSION/'runtime/game/addons/tome-checker-fixture/data/monster-live_map_survey.lua')==digest(ROOT/'tests/live_map_survey.lua')
 path=OUT/'survey.json';result=json.loads(path.read_text()) if path.exists() else {'zones':[]}
 if replace:result['zones']=[z for z in result['zones'] if z['label']!=label]
 else:assert not any(z['label']==label for z in result['zones'])
 result.setdefault('launches',{})[label]=plan
 def save():
  path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
  (OUT/f'validation-{label}.txt').write_text((''.join(f.transcript)+f.new_log()).rstrip()+'\n')
 def shot(tile,suffix='open'):
  name=f'{label}-{suffix}-{tile}';source=HOME/(name+'.png');source.unlink(missing_ok=True)
  p=subprocess.run([sys.executable,str(ROOT/'tools/fixture_command.py'),'shot',name],capture_output=True,text=True,timeout=35)
  f.transcript.append(p.stdout+p.stderr);f.check_log()
  assert p.returncode==0 and source.is_file() and png_size(source)==(1920,1080),(name,p.stdout,p.stderr)
  target=SHOTS/source.name;shutil.copy2(source,target)
  return {'file':'screenshots/'+target.name,'sha256':digest(target),'tile':tile}
 try:
  f.lua("assert(config.settings.cheat and config.settings.disable_all_connectivity and not profile.auth);assert(core.shader.active(4));ms=dofile('/data-checker-fixture/monster-live_map_survey.lua');ms.setup()")
  big='true' if layout=='bigworm' else 'false'
  f.lua(f"local enter=ms.enter('sandworm-lair',{level},{{bigworm={big}}});local terrain=ms.terrainCensus();local details=ms.sandDetails();ms.dump('/sand-result.json',{{enter=enter,terrain=terrain,details=details}})")
  data=read('sand-result.json');entry={'label':label,'layout':layout,'level':level,**data}
  assert entry['enter']['is_bigworm']==(layout=='bigworm'),entry['enter']
  assert entry['terrain']['supported']>0 and entry['terrain']['native']==0,entry['terrain']
  assert entry['details']['kinds'].get('floor',0)>0 and entry['details']['kinds'].get('wall',0)>0,entry['details']
  f.lua("local m=game.level.map;local out={};local seen={};for x=0,m.w-1 do for y=0,m.h-1 do local g=m(x,y,1);local id=g and g.define_as;if id and (id:match('^SANDWALL') or id:match('^UNDERGROUND_SAND')) and not require('mod.class.CheckerTerrain').sandTerrain(g) then local key=id..':'..tostring(g.image)..':'..tostring(g.add_displays and #g.add_displays);if not seen[key] then seen[key]=true;out[#out+1]={id=id,image=g.image,add_displays=g.add_displays and #g.add_displays or 0,add_mos=g.add_mos and #g.add_mos or 0,first_display=g.add_displays and g.add_displays[1] and g.add_displays[1].image or false,dig_source=type(g.dig)=='function' and debug.getinfo(g.dig,'S').source or false,move=g.does_block_move,sight=g.block_sight,air=g.air_level,pass=g.can_pass and g.can_pass.pass_wall,replace=g.replace_display and true or false} end end end end;ms.dump('/sand-diagnostic.json',out)")
  entry['diagnostic']=read('sand-diagnostic.json')
  f.lua("local p=ms.sandOpenPose();ms.dump('/sand-pose.json',p)")
  entry['open_pose']=read('sand-pose.json')
  assert entry['open_pose']['found'] and entry['open_pose']['floor']>0 and entry['open_pose']['wall']>0,entry['open_pose']
  if level==1: assert entry['open_pose']['near_exit']>0,entry['open_pose']
  entry['screenshots']=[]
  for tile in ((48,64,96) if level==1 else (64,)):
   f.lua("game:setResolution('1920x1080 Windowed',true);"+f"config.settings.tome.gfx.size='{tile}x{tile}';game:setupDisplayMode(false);"+"ms.focus(game.player.x,game.player.y);ms.sandStageView()")
   entry['screenshots'].append(shot(tile))
  if level==1:
   f.lua("game:setResolution('1920x1080 Windowed',true);config.settings.tome.gfx.size='64x64';game:setupDisplayMode(false);ms.focus(game.player.x,game.player.y);ms.sandStageView();local v=ms.sandStageRemembered();ms.dump('/sand-remembered.json',v)")
   entry['remembered_pose']=read('sand-remembered.json')
   assert entry['remembered_pose']['floor']>0 and entry['remembered_pose']['wall']>0,entry['remembered_pose']
   entry['remembered_screenshot']=shot(64,'remembered')
  if entry['open_pose']['near_exit']==0 and entry['details']['ladders']:
   f.lua("local l=ms.sandDetails().ladders[1];local m=game.level.map;for x=math.max(0,l.x-12),math.min(m.w-1,l.x+12) do for y=math.max(0,l.y-9),math.min(m.h-1,l.y+9) do m.seens(x,y,true);m.infovs(x,y,true);m.remembers(x,y,true) end end;ms.focus(l.x,l.y);ms.dump('/sand-exit-pose.json',{x=l.x,y=l.y,kind=l.kind,fixture_only=true})")
   entry['exit_pose']=read('sand-exit-pose.json')
   entry['exit_screenshot']=shot(64,'exit')
  if layout=='bigworm' and level==1:
   f.lua("local p=ms.sandCorridorPose();ms.dump('/sand-corridor.json',p)")
   entry['corridor_pose']=read('sand-corridor.json')
   assert entry['corridor_pose']['found'] and entry['corridor_pose']['x']>=100 and entry['corridor_pose']['x']<=250,entry['corridor_pose']
   f.lua("game:setResolution('1920x1080 Windowed',true);config.settings.tome.gfx.size='64x64';game:setupDisplayMode(false);ms.focus(game.player.x,game.player.y);ms.sandStageView()")
   entry['corridor_screenshot']=shot(64,'corridor')
  f.lua("ms.setMode('vanilla');local v=ms.terrainCensus();ms.setMode('blockout');local b=ms.terrainCensus();ms.setMode('refined');local r=ms.terrainCensus();ms.dump('/sand-modes.json',{vanilla=v,blockout=b,refined=r})")
  entry['modes']=read('sand-modes.json')
  assert entry['modes']['vanilla']['owned']==0 and entry['modes']['blockout']['native']==0 and entry['modes']['refined']['native']==0,entry['modes']
  f.lua("ms.setMode('vanilla');local t=os.clock();ms.setMode('refined');ms.dump('/sand-perf.json',{seconds=os.clock()-t,cells=game.level.map.w*game.level.map.h,kind='vanilla-to-refined'})")
  entry['full_repaint']=read('sand-perf.json')
  f.lua("local d=ms.digSand();ms.dump('/sand-dig.json',d)")
  entry['dig']=read('sand-dig.json')
  assert entry['dig']['found'] and entry['dig']['census']['native']==0,entry['dig']
  assert all(d['is_tunnel'] and d['temporary']==20 and not d['owned'] for d in entry['dig']['dug']),entry['dig']
  result['zones'].append(entry);result['complete']=len(result['zones'])==6;save()
  print('OK',label,entry['terrain'],entry['full_repaint'],flush=True)
 finally:save()

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--layout',choices=('default','bigworm'));ap.add_argument('--level',type=int);ap.add_argument('--replace',action='store_true');args=ap.parse_args()
 scenes=tuple((layout,level) for layout,maxlevel in (('default',4),('bigworm',2)) for level in range(1,maxlevel+1))
 for layout,level in scenes:
  if args.layout and args.layout!=layout or args.level and args.level!=level:continue
  label=f'{layout}-L{level}';path=OUT/'survey.json'
  if not args.replace and path.exists() and any(z['label']==label for z in json.loads(path.read_text())['zones']):continue
  launch=subprocess.run([sys.executable,str(ROOT/'tools/launch_fixture.py'),'--shaders','--tiles','64','--terrain','refined','--resolution','1920x1080','--birth','Human:Cornac:Male:Berserker'],cwd=ROOT,capture_output=True,text=True)
  if launch.returncode:raise RuntimeError(f'{label} launch failed: {launch.stdout} {launch.stderr}')
  meta=json.loads(PROCESSES.read_text())
  try:
   print('START',label,flush=True)
   for _ in range(180):
    if HOME.is_dir():break
    time.sleep(.5)
   else:raise RuntimeError(f'{label}: no fixture home')
   time.sleep(3);capture(layout,level,args.replace)
  finally:stop_started(meta);print('STOP',label,meta['game'],meta['xvfb'],flush=True)
if __name__=='__main__':main()
