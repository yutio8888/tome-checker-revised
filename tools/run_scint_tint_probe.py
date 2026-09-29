#!/usr/bin/env python3
"""Controlled fixture-only color probe of crystal board pixels and map ownership."""
import json,shutil,subprocess,sys,time
from pathlib import Path
from PIL import Image,ImageStat
from capture_korpul import Fixture,HOME,ROOT,SESSION,digest
from run_norgos_validation import stop_started
OUT=ROOT/'evidence/scintillating-20260928';PROCESS=SESSION/'processes.json'

def main():
 launch=subprocess.run([sys.executable,str(ROOT/'tools/launch_fixture.py'),'--shaders','--tiles','64','--terrain','refined','--resolution','1920x1080','--birth','Human:Cornac:Male:Berserker'],capture_output=True,text=True)
 assert launch.returncode==0,launch.stdout+launch.stderr
 meta=json.loads(PROCESS.read_text())
 try:
  time.sleep(2);f=Fixture()
  f.lua("assert(core.shader.active(4));ms=dofile('/data-checker-fixture/monster-live_map_survey.lua');ms.setup();ms.enter('scintillating-caves',1,{twisted=false});ms.crystalOpenPose();ms.crystalStageView();game.level.data.foreground=function() end;local m=game.level.map;m:setShown(1,1,1,1);m:setObscure(.6,.6,.6,1);m:redisplay();core.display.forceRedraw();ms.dump('/scint-tint-probe-a.json',{shown=m.color_shown,census=ms.terrainCensus()})")
  outputs=[]
  for label in ('neutral','green'):
   if label=='green':
    f.lua("local m=game.level.map;m:setShown(.55,1,.55,1);m:setObscure(.33,.6,.33,1);m:redisplay();core.display.forceRedraw();ms.dump('/scint-tint-probe-b.json',{shown=m.color_shown,census=ms.terrainCensus()})")
   name='scint-tint-probe-'+label;shot=HOME/(name+'.png');shot.unlink(missing_ok=True)
   r=subprocess.run([sys.executable,str(ROOT/'tools/fixture_command.py'),'shot',name],capture_output=True,text=True)
   assert r.returncode==0,r.stdout+r.stderr
   target=OUT/'screenshots'/(name+'.png');shutil.copy2(shot,target)
   rgb=ImageStat.Stat(Image.open(target).convert('RGB').crop((320,15,1460,980))).mean
   outputs.append({'label':label,'file':'screenshots/'+target.name,'sha256':digest(target),'map_mean_rgb':rgb})
  a=json.loads((HOME/'scint-tint-probe-a.json').read_text());b=json.loads((HOME/'scint-tint-probe-b.json').read_text())
  assert a['census']['native']==b['census']['native']==0
  assert a['shown']==[1,1,1,1] and b['shown']==[.55,1,.55,1],(a,b)
  assert outputs[1]['map_mean_rgb'][0]<.8*outputs[0]['map_mean_rgb'][0],outputs
  assert outputs[1]['map_mean_rgb'][2]<.8*outputs[0]['map_mean_rgb'][2],outputs
  (OUT/'tint-pixel-probe.json').write_text(json.dumps({'fixture_only':True,'native_foreground_paused_during_controlled_probe':True,'neutral':a,'green':b,'captures':outputs},indent=2)+'\n')
  (OUT/'validation-tint-pixel-probe.txt').write_text((''.join(f.transcript)+f.new_log()).rstrip()+'\n')
  print(outputs)
 finally:stop_started(meta)
if __name__=='__main__':main()
