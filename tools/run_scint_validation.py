#!/usr/bin/env python3
"""Eight independent Scintillating Caves fixture starts, screenshots and census."""
import argparse,json,shutil,statistics,subprocess,sys,time
from pathlib import Path
from PIL import Image,ImageStat
from capture_korpul import Fixture,HOME,ROOT,SESSION,digest,png_size
from run_norgos_validation import stop_started
OUT=ROOT/'evidence/scintillating-20260928';SHOTS=OUT/'screenshots';PROCESSES=SESSION/'processes.json'

def read(name):
 p=HOME/name;value=json.loads(p.read_text());p.unlink(missing_ok=True);return value

def capture(layout,level,natural_fov=False):
 label=f'{layout}-L{level}';f=Fixture();SHOTS.mkdir(parents=True,exist_ok=True)
 plan=json.loads((SESSION/'launch-plan.json').read_text())
 assert plan['fixture'] and plan['shaders'] and plan['resolution']=='1920x1080'
 assert digest(SESSION/'runtime/game/addons/tome-checker-revised/overload/mod/class/CheckerTerrain.lua')==digest(ROOT/'overload/mod/class/CheckerTerrain.lua')
 assert digest(SESSION/'runtime/game/addons/tome-checker-fixture/data/monster-live_map_survey.lua')==digest(ROOT/'tests/live_map_survey.lua')
 for name in ('floor0.png','wall-15-0.png'):
  assert digest(SESSION/'runtime/game/addons/tome-checker-revised/data/gfx/refined/crystal'/name)==digest(ROOT/'data/gfx/refined/crystal'/name)
 survey=OUT/'survey.json';result=json.loads(survey.read_text()) if survey.exists() else {'zones':[]}
 result['zones']=[z for z in result['zones'] if z['label']!=label]
 def save():
  survey.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
  (OUT/f'validation-{label}.txt').write_text((''.join(f.transcript)+f.new_log()).rstrip()+'\n')
 def shot(tile,suffix):
  name=f'{label}-{suffix}-{tile}';source=HOME/(name+'.png');source.unlink(missing_ok=True)
  r=subprocess.run([sys.executable,str(ROOT/'tools/fixture_command.py'),'shot',name],capture_output=True,text=True,timeout=35)
  f.transcript.append(r.stdout+r.stderr);f.check_log()
  assert r.returncode==0 and source.is_file() and png_size(source)==(1920,1080),(name,r.stdout,r.stderr)
  target=SHOTS/source.name;shutil.copy2(source,target)
  return {'file':'screenshots/'+target.name,'sha256':digest(target),'tile':tile}
 try:
  f.lua("assert(config.settings.cheat and config.settings.disable_all_connectivity and not profile.auth);assert(core.shader.active(4));ms=dofile('/data-checker-fixture/monster-live_map_survey.lua');ms.setup()")
  twisted='true' if layout=='twisted' else 'false'
  f.lua(f"local e=ms.enter('scintillating-caves',{level},{{twisted={twisted}}});ms.dump('/scint-result.json',{{enter=e,terrain=ms.terrainCensus(),details=ms.crystalDetails(),max_level=game.zone.max_level}})")
  entry={'label':label,'layout':layout,'level':level,**read('scint-result.json'),'screenshots':[],'launch':plan}
  assert entry['max_level']==(5 if layout=='twisted' else 3)
  assert entry['terrain']['supported']>0 and entry['terrain']['native']==0,entry['terrain']
  assert entry['details']['kinds'].get('floor',0)>0 and entry['details']['kinds'].get('wall',0)>0
  assert entry['details']['ladders']
  f.lua("local p=ms.crystalOpenPose();ms.dump('/scint-pose.json',p)")
  entry['open_pose']=read('scint-pose.json');assert entry['open_pose']['found'] and entry['open_pose']['wall']>0
  for tile in ((48,64,96) if level==1 else (64,)):
   f.lua(f"game:setResolution('1920x1080 Windowed',true);config.settings.tome.gfx.size='{tile}x{tile}';game:setupDisplayMode(false);ms.focus(game.player.x,game.player.y)"+('' if natural_fov else ';ms.crystalStageView()'))
   if tile==64 and natural_fov:
    f.lua("ms.dump('/scint-lit-pairs.json',ms.crystalLitPairs())")
    pairs=read('scint-lit-pairs.json')
   image_info=shot(tile,'open');entry['screenshots'].append(image_info)
   if tile==64 and natural_fov:
    image=Image.open(SHOTS/Path(image_info['file']).name).convert('L')
    values=[]
    for pair in pairs['pairs']:
     def mean(cell):
      x,y,size=cell['sx'],cell['sy'],pairs['tile']
      return ImageStat.Stat(image.crop((int(x+size*.3),int(y+size*.3),int(x+size*.7),int(y+size*.7)))).mean[0]
     values.append({'floor':mean(pair['floor']),'wall':mean(pair['wall']),'floor_cell':pair['floor'],'wall_cell':pair['wall']})
    assert len(values)>=5,len(values)
    floor_mean=statistics.median(v['floor'] for v in values)
    wall_mean=statistics.median(v['wall'] for v in values)
    entry['lit_pixel_check']={'pair_count':len(values),'floor_median':floor_mean,'wall_median':wall_mean,
     'relative_gap':(floor_mean-wall_mean)/floor_mean,'pairs':values,'screenshot':image_info['file'],'natural_fov':True}
    (OUT/f'lit-pixels-{label}.json').write_text(json.dumps(entry['lit_pixel_check'],indent=2)+'\n')
    assert floor_mean-wall_mean>=20 and (floor_mean-wall_mean)/floor_mean>=.35,entry['lit_pixel_check']
  if level==1:
   f.lua("game:setResolution('1920x1080 Windowed',true);config.settings.tome.gfx.size='64x64';game:setupDisplayMode(false);ms.focus(game.player.x,game.player.y);"+('' if natural_fov else 'ms.crystalStageView();')+"ms.dump('/scint-remembered.json',ms.crystalStageRemembered())")
   entry['remembered']=read('scint-remembered.json');assert entry['remembered']['floor']>0 and entry['remembered']['wall']>0
   entry['remembered_screenshot']=shot(64,'remembered')
  if layout=='twisted':
   f.lua("ms.dump('/scint-vault-pose.json',ms.crystalVaultPose())")
   entry['vault_pose']=read('scint-vault-pose.json')
   if entry['vault_pose']['found']:
    if not natural_fov:f.lua("ms.crystalStageView()")
    entry['vault_screenshot']=shot(64,'vault-edge')
  f.lua("ms.setMode('vanilla');local v=ms.terrainCensus();ms.setMode('blockout');local b=ms.terrainCensus();ms.setMode('refined');local r=ms.terrainCensus();ms.dump('/scint-modes.json',{vanilla=v,blockout=b,refined=r})")
  entry['modes']=read('scint-modes.json');assert entry['modes']['vanilla']['owned']==0 and entry['modes']['blockout']['native']==0 and entry['modes']['refined']['native']==0
  f.lua("local m=game.level.map;local before={unpack(m.color_shown or {})};game.zone.foreground(game.level,0,0,0);local after={unpack(m.color_shown or {})};local obscure={unpack(m.color_obscure or {})};ms.dump('/scint-tint.json',{before=before,after=after,obscure=obscure,census=ms.terrainCensus()})")
  entry['tint']=read('scint-tint.json');assert len(entry['tint']['after'])==4 and len(entry['tint']['obscure'])==4 and entry['tint']['census']['native']==0
  entry['tint_screenshot']=shot(64,'tint')
  f.lua("ms.dump('/scint-dig.json',ms.digCrystal())")
  entry['dig']=read('scint-dig.json');assert entry['dig']['found'] and entry['dig']['after_kind']=='floor' and entry['dig']['after_owned'] and entry['dig']['census']['native']==0
  result['zones'].append(entry);result['complete']=len(result['zones'])==8;save()
  print('OK',label,entry['terrain'],entry['details']['kinds'],flush=True)
 finally:save()

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--layout',choices=('default','twisted'));ap.add_argument('--level',type=int);ap.add_argument('--replace',action='store_true');ap.add_argument('--natural-fov',action='store_true');args=ap.parse_args()
 scenes=((layout,level) for layout,maxlevel in (('default',3),('twisted',5)) for level in range(1,maxlevel+1))
 for layout,level in scenes:
  if args.layout and args.layout!=layout or args.level and args.level!=level:continue
  label=f'{layout}-L{level}';survey=OUT/'survey.json'
  if not args.replace and survey.exists() and any(z['label']==label for z in json.loads(survey.read_text())['zones']):continue
  launch=subprocess.run([sys.executable,str(ROOT/'tools/launch_fixture.py'),'--shaders','--tiles','64','--terrain','refined','--resolution','1920x1080','--birth','Human:Cornac:Male:Berserker'],cwd=ROOT,capture_output=True,text=True)
  if launch.returncode:raise RuntimeError(launch.stdout+launch.stderr)
  meta=json.loads(PROCESSES.read_text())
  try:
   print('START',label,flush=True)
   for _ in range(180):
    if HOME.is_dir():break
    time.sleep(.5)
   else:raise RuntimeError('fixture home missing')
   time.sleep(2);capture(layout,level,args.natural_fov)
  finally:stop_started(meta);print('STOP',label,flush=True)
if __name__=='__main__':main()
