#!/usr/bin/env python3
"""Three independent offline Unremarkable Cave starts and rendered-frame checks."""
import json,shutil,statistics,subprocess,sys,time
from pathlib import Path
from PIL import Image,ImageStat
from capture_korpul import Fixture,HOME,ROOT,SESSION,digest,png_size
from run_norgos_validation import stop_started

OUT=ROOT/'evidence/unremarkable-20260928';SHOTS=OUT/'screenshots';PROCESSES=SESSION/'processes.json'

def read(name):
    p=HOME/name;result=json.loads(p.read_text());p.unlink(missing_ok=True);return result

def shot(f,name,tile):
    source=HOME/(name+'.png');source.unlink(missing_ok=True)
    r=subprocess.run([sys.executable,str(ROOT/'tools/fixture_command.py'),'shot',name],capture_output=True,text=True,timeout=35)
    f.transcript.append(r.stdout+r.stderr);f.check_log()
    assert r.returncode==0 and source.is_file() and png_size(source)==(1920,1080),(name,r.stdout,r.stderr)
    target=SHOTS/source.name;SHOTS.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
    return {'file':'screenshots/'+target.name,'sha256':digest(target),'tile':tile}

def measure(info,pairs):
    image=Image.open(OUT/info['file']).convert('L');values=[]
    for pair in pairs['pairs']:
        def mean(cell):
            x,y,size=cell['sx'],cell['sy'],pairs['tile']
            return ImageStat.Stat(image.crop((int(x+size*.3),int(y+size*.3),int(x+size*.7),int(y+size*.7)))).mean[0]
        values.append({'floor':mean(pair['floor']),'wall':mean(pair['wall']),
                       'floor_cell':pair['floor'],'wall_cell':pair['wall']})
    assert len(values)>=5,len(values)
    floor=statistics.median(v['floor'] for v in values)
    wall=statistics.median(v['wall'] for v in values)
    result={'pair_count':len(values),'floor_median':floor,'wall_median':wall,
            'relative_gap':(floor-wall)/floor,'pairs':values,'screenshot':info['file'],
            'natural_fov':True}
    assert floor-wall>=20 and result['relative_gap']>=.30,result
    return result

def capture(index):
    f=Fixture();label=f'cold-{index}';plan=json.loads((SESSION/'launch-plan.json').read_text())
    assert plan['fixture'] and plan['shaders'] and plan['resolution']=='1920x1080'
    assert digest(SESSION/'runtime/game/addons/tome-checker-revised/overload/mod/class/CheckerTerrain.lua')==digest(ROOT/'overload/mod/class/CheckerTerrain.lua')
    assert digest(SESSION/'runtime/game/addons/tome-checker-fixture/data/monster-live_map_survey.lua')==digest(ROOT/'tests/live_map_survey.lua')
    for name in ('floor0.png','wall-15-0.png','ladder-world0.png'):
        assert digest(SESSION/'runtime/game/addons/tome-checker-revised/data/gfx/refined/cave'/name)==digest(ROOT/'data/gfx/refined/cave'/name)
    record={'label':label,'launch':plan,'screenshots':[]}
    def save():
        (OUT/f'validation-{label}.txt').write_text((''.join(f.transcript)+f.new_log()).rstrip()+'\n')
    try:
        f.lua("assert(config.settings.cheat and config.settings.disable_all_connectivity and not profile.auth);assert(core.shader.active(4));ms=dofile('/data-checker-fixture/monster-live_map_survey.lua');ms.setup()")
        f.lua("local e=ms.enter('unremarkable-cave',1,{});ms.dump('/cave-entry.json',{enter=e,terrain=ms.terrainCensus(),details=ms.caveDetails()})")
        record.update(read('cave-entry.json'))
        assert record['enter']['w']==100 and record['enter']['h']==50 and record['enter']['level']==1
        assert record['terrain']['supported']>=4900 and record['terrain']['native']==0,record['terrain']
        assert record['details']['kinds']['ladder-world']==1
        assert record['details']['regions']['generated']['wall']>0 and record['details']['regions']['static']['wall']>0
        assert record['details']['regions']['seam']['wall']>0 and record['details']['regions']['seam']['floor']>0
        f.lua("ms.dump('/cave-pose.json',ms.cavePose(false))")
        record['open_pose']=read('cave-pose.json');assert record['open_pose']['found']
        # The 64px frame check uses native FOV and the live shader-lit image.
        f.lua("game:setResolution('1920x1080 Windowed',true);config.settings.tome.gfx.size='64x64';game:setupDisplayMode(false);ms.focus(game.player.x,game.player.y);ms.dump('/cave-pairs.json',ms.caveLitPairs())")
        pairs=read('cave-pairs.json');natural=shot(f,f'{label}-natural-64',64);record['screenshots'].append(natural)
        record['lit_pixel_check']=measure(natural,pairs)
        (OUT/f'lit-pixels-{label}.json').write_text(json.dumps(record['lit_pixel_check'],indent=2)+'\n')
        # A disposable view reveal shows the edge exit and an open wall field
        # together at all three sizes; it is labelled staged in the evidence.
        for tile in (48,64,96):
            f.lua(f"game:setResolution('1920x1080 Windowed',true);config.settings.tome.gfx.size='{tile}x{tile}';game:setupDisplayMode(false);ms.focus(game.player.x,game.player.y);ms.caveStageView()")
            record['screenshots'].append(shot(f,f'{label}-open-{tile}',tile))
        f.lua("ms.dump('/cave-exit-pose.json',ms.caveExitPose())")
        record['exit_pose']=read('cave-exit-pose.json')
        for tile in (48,64,96):
            f.lua(f"game:setResolution('1920x1080 Windowed',true);config.settings.tome.gfx.size='{tile}x{tile}';game:setupDisplayMode(false);ms.focus(game.player.x,game.player.y);ms.caveStageView()")
            record['screenshots'].append(shot(f,f'{label}-exit-{tile}',tile))
        f.lua("ms.dump('/cave-pose.json',ms.cavePose(false))")
        record['memory_start_pose']=read('cave-pose.json')
        f.lua("game:setResolution('1920x1080 Windowed',true);config.settings.tome.gfx.size='64x64';game:setupDisplayMode(false);ms.focus(game.player.x,game.player.y);ms.dump('/cave-memory.json',ms.caveRemembered())")
        record['remembered']=read('cave-memory.json');assert record['remembered']['floor']>0 and record['remembered']['wall']>0
        record['screenshots'].append(shot(f,f'{label}-remembered-64',64))
        f.lua("ms.dump('/cave-seam.json',ms.cavePose(true))")
        record['seam_pose']=read('cave-seam.json');assert record['seam_pose']['found'] and 83<=record['seam_pose']['x']<=91
        f.lua("ms.caveStageView();ms.caveClearDialogs()")
        record['screenshots'].append(shot(f,f'{label}-seam-64',64))
        f.lua("ms.setMode('vanilla');local v=ms.terrainCensus();ms.setMode('blockout');local b=ms.terrainCensus();ms.setMode('refined');local r=ms.terrainCensus();ms.dump('/cave-modes.json',{vanilla=v,blockout=b,refined=r})")
        record['modes']=read('cave-modes.json')
        assert record['modes']['vanilla']['owned']==0 and record['modes']['blockout']['native']==0 and record['modes']['refined']['native']==0
        f.lua("ms.dump('/cave-dig.json',ms.digCave())")
        record['dig']=read('cave-dig.json')
        assert record['dig']['found'] and record['dig']['after_kind']=='floor' and record['dig']['after_owned'] and record['dig']['census']['native']==0
        print('PASS',label,record['terrain'],record['lit_pixel_check']['relative_gap'],flush=True)
        return record
    finally:save()

def main():
    OUT.mkdir(parents=True,exist_ok=True);survey={'zones':[]}
    for index in range(1,4):
        launch=subprocess.run([sys.executable,str(ROOT/'tools/launch_fixture.py'),'--shaders','--tiles','64','--terrain','refined','--resolution','1920x1080','--birth','Human:Cornac:Male:Berserker'],cwd=ROOT,capture_output=True,text=True)
        if launch.returncode:raise RuntimeError(launch.stdout+launch.stderr)
        meta=json.loads(PROCESSES.read_text())
        try:
            time.sleep(3)
            survey['zones'].append(capture(index))
            (OUT/'survey.json').write_text(json.dumps(survey,indent=2)+'\n')
        finally:stop_started(meta)
    survey['complete']=True;(OUT/'survey.json').write_text(json.dumps(survey,indent=2)+'\n')

if __name__=='__main__':main()
