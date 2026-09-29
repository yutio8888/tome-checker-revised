#!/usr/bin/env python3
"""Repeat L1 void captures and compare native/weather passes on the same map."""
import json,shutil,subprocess,sys,time
from pathlib import Path
from capture_korpul import Fixture,HOME,ROOT,SESSION,digest,png_size
from run_void_validation import capture,OUT,SHOTS,read
from run_norgos_validation import stop_started
SCENES=['unhallowed-morass','abashed-expanse','temporal-rift']

def same_scene(zone):
 f=Fixture();label=zone+'-L1';comparison=[]
 def dump(expr,name):
  f.lua(f"ms.dump('/{name}',{expr})");return read(name)
 def shot(tag):
  name=f'{label}-{tag}-64';src=HOME/(name+'.png');src.unlink(missing_ok=True)
  cmd=subprocess.run([sys.executable,str(ROOT/'tools/fixture_command.py'),'shot',name],capture_output=True,text=True,timeout=35)
  f.transcript.append(cmd.stdout+cmd.stderr);f.check_log()
  assert cmd.returncode==0 and src.is_file() and png_size(src)==(1920,1080),(cmd.stdout,cmd.stderr)
  dst=SHOTS/src.name;shutil.copy2(src,dst)
  return {'file':'screenshots/'+dst.name,'sha256':digest(dst)}
 f.lua("game:setResolution('1920x1080 Windowed',true);config.settings.tome.gfx.size='64x64';game:setupDisplayMode(false);ms.reuseStageView();ms.setMode('refined')")
 state=dump("{x=game.player.x,y=game.player.y,turn=game.turn,zone=game.zone.short_name,level=game.level.level,weather=config.settings.tome.weather_effects,foreground=game.level.foreground_particle and true or false,background=game.level.background_particle and true or false,starfield=game.level.starfield_shader and true or false}",'void-comparison-state.json')
 for mode,weather,tag in [('refined',True,'compare-refined-weather-on'),('vanilla',True,'compare-vanilla-weather-on'),('vanilla',False,'compare-vanilla-weather-off'),('refined',False,'compare-refined-weather-off')]:
  f.lua(f"config.settings.tome.weather_effects={'true' if weather else 'false'};ms.setMode('{mode}');ms.reuseStageView()")
  comparison.append({'mode':mode,'weather':weather,**shot(tag),'census':dump('ms.terrainCensus()','void-comparison-census.json')})
 assert dump("{x=game.player.x,y=game.player.y,turn=game.turn,zone=game.zone.short_name,level=game.level.level}",'void-comparison-final.json')=={k:state[k] for k in ('x','y','turn','zone','level')}
 return {'state':state,'shots':comparison}

def main():
 SHOTS.mkdir(parents=True,exist_ok=True);old=SHOTS/'pre-rework';old.mkdir(exist_ok=True)
 survey=json.loads((OUT/'survey.json').read_text());comparisons={}
 for zone in SCENES:
  label=zone+'-L1'
  for path in SHOTS.glob(label+'-*.png'):
   if not path.name.startswith(label+'-compare-'):
    if (old/path.name).exists():path.unlink()
    else:shutil.move(str(path),old/path.name)
  launch=subprocess.run([sys.executable,str(ROOT/'tools/launch_fixture.py'),'--shaders','--tiles','64','--terrain','refined','--resolution','1920x1080','--birth','Human:Cornac:Male:Berserker'],cwd=ROOT,capture_output=True,text=True)
  if launch.returncode:raise RuntimeError(launch.stdout+launch.stderr)
  meta=json.loads((SESSION/'processes.json').read_text())
  try:
   time.sleep(2)
   row=capture(zone,1)
   comparisons[label]=same_scene(zone)
   survey['scenes']=[row if scene['label']==label else scene for scene in survey['scenes']]
   (OUT/'survey.json').write_text(json.dumps(survey,ensure_ascii=False,indent=2)+'\n')
   (OUT/'rework-comparisons.json').write_text(json.dumps(comparisons,ensure_ascii=False,indent=2)+'\n')
   print('PASS',label,row['census'],row['lit_pixels']['relative_gap'],flush=True)
  finally:stop_started(meta);print('STOP',label,flush=True)
if __name__=='__main__':main()
