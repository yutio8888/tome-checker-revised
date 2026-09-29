#!/usr/bin/env python3
"""Two independent offline Spellblaze starts with rendered-frame checks."""
import json,shutil,statistics,subprocess,sys,time
from pathlib import Path
from PIL import Image,ImageStat
from capture_korpul import Fixture,HOME,ROOT,SESSION,digest,png_size
from run_norgos_validation import stop_started

OUT=ROOT/'evidence/spellblaze-20260928';SHOTS=OUT/'screenshots'
class NoLava(Exception): pass
def read(name):
    p=HOME/name;value=json.loads(p.read_text());p.unlink();return value
def capture(level):
    label=f'spellblaze-rework-L{level}';f=Fixture();SHOTS.mkdir(parents=True,exist_ok=True)
    plan=json.loads((SESSION/'launch-plan.json').read_text())
    assert plan['fixture'] and plan['shaders'] and plan['resolution']=='1920x1080'
    assert digest(SESSION/'runtime/game/addons/tome-checker-revised/overload/mod/class/CheckerTerrain.lua')==digest(ROOT/'overload/mod/class/CheckerTerrain.lua')
    assert digest(SESSION/'runtime/game/addons/tome-checker-fixture/data/monster-live_map_survey.lua')==digest(ROOT/'tests/live_map_survey.lua')
    for name in ('floor0.png','tree0.png','lava-15-0.png','exit-world0.png'):
        assert digest(SESSION/'runtime/game/addons/tome-checker-revised/data/gfx/refined/burnt'/name)==digest(ROOT/'data/gfx/refined/burnt'/name)
    def dump(code,name):
        f.lua(f"ms.dump('/{name}',{code})");return read(name)
    def shot(tile,tag):
        name=f'{label}-{tag}-{tile}';source=HOME/(name+'.png');source.unlink(missing_ok=True)
        r=subprocess.run([sys.executable,str(ROOT/'tools/fixture_command.py'),'shot',name],capture_output=True,text=True,timeout=35)
        f.transcript.append(r.stdout+r.stderr);f.check_log()
        assert r.returncode==0 and source.is_file() and png_size(source)==(1920,1080),(r.stdout,r.stderr)
        target=SHOTS/source.name;shutil.copy2(source,target)
        return {'file':'screenshots/'+target.name,'sha256':digest(target),'tile':tile,'tag':tag}
    def size(tile):
        f.lua(f"game:setResolution('1920x1080 Windowed',true);config.settings.tome.gfx.size='{tile}x{tile}';game:setupDisplayMode(false);ms.focus(game.player.x,game.player.y)")
    row={'label':label,'launch':plan,'screenshots':[]}
    try:
        f.lua("assert(config.settings.cheat and config.settings.disable_all_connectivity and not profile.auth);assert(core.shader.active(4));ms=dofile('/data-checker-fixture/monster-live_map_survey.lua');ms.setup()")
        row['enter']=dump(f"ms.enter('mark-spellblaze',{level})",'sb-enter.json')
        row['census']=dump('ms.terrainCensus()','sb-census.json')
        row['details']=dump('ms.spellblazeDetails()','sb-details.json')
        if level==1 and not row['details']['kinds'].get('lava'):
            raise NoLava('Level 1 generated without a lava pool')
        assert row['census']['supported']>0 and row['census']['native']==0,row['census']
        assert row['details']['kinds']['floor']>0 and row['details']['kinds']['tree']>0
        row['open_pose']=dump('ms.spellblazePose(false)','sb-pose.json');assert row['open_pose']['found']
        size(64);row['lit_pairs']=dump('ms.spellblazeLitPairs()','sb-pairs.json')
        natural=shot(64,'natural');row['screenshots'].append(natural)
        im=Image.open(SHOTS/Path(natural['file']).name).convert('L');samples=[]
        for pair in row['lit_pairs']['pairs']:
            def mean(cell):
                x,y,s=cell['sx'],cell['sy'],row['lit_pairs']['tile']
                return ImageStat.Stat(im.crop((int(x+s*.3),int(y+s*.3),int(x+s*.7),int(y+s*.7)))).mean[0]
            samples.append({'floor':mean(pair['floor']),'tree':mean(pair['wall'])})
        assert len(samples)>=2,len(samples)
        floor=statistics.median(v['floor'] for v in samples);tree=statistics.median(v['tree'] for v in samples)
        row['lit_pixels']={'pairs':len(samples),'floor':floor,'tree':tree,'gap':(floor-tree)/floor,'samples':samples}
        assert abs(row['lit_pixels']['gap'])>=.18,row['lit_pixels']
        for tile in (48,96):
            size(tile);row['screenshots'].append(shot(tile,'natural'))
        for tile in (48,64,96):
            size(tile);f.lua('ms.reuseStageView()');row['screenshots'].append(shot(tile,'open'))
        row['exit_pose']=dump("ms.spellblazePose('exit')",'sb-exit.json')
        if row['exit_pose']['exits']:
            for tile in (48,64,96):
                size(tile);f.lua('ms.reuseStageView()');row['screenshots'].append(shot(tile,'exit'))
        row['lava_pose']=dump("ms.spellblazePose('lava')",'sb-lava.json')
        if row['lava_pose']['lava']:
            for tile in (48,64,96):
                size(tile);f.lua('ms.reuseStageView()');row['screenshots'].append(shot(tile,'lava'))
        size(64);row['remembered']=dump('ms.reuseRemembered()','sb-memory.json')
        assert row['remembered']['found'] and row['remembered']['old']['remembered'] and not row['remembered']['old'].get('visible')
        for tile in (48,64,96):
            size(tile);row['screenshots'].append(shot(tile,'remembered'))
        row['modes']=dump("(function() ms.setMode('vanilla');local v=ms.terrainCensus();ms.setMode('blockout');local b=ms.terrainCensus();ms.setMode('refined');local r=ms.terrainCensus();return {vanilla=v,blockout=b,refined=r} end)()",'sb-modes.json')
        assert row['modes']['vanilla']['owned']==0 and row['modes']['blockout']['native']==0 and row['modes']['refined']['native']==0
        row['dig']=dump('ms.spellblazeDig()','sb-dig.json')
        assert row['dig']['found'] and row['dig']['after_kind']=='floor' and row['dig']['owned'] and row['dig']['census']['native']==0
        return row
    finally:
        (OUT/f'validation-{label}.txt').write_text((''.join(f.transcript)+f.new_log()).rstrip()+'\n')
def main():
    OUT.mkdir(parents=True,exist_ok=True);survey={'scenes':[]}
    for level in (1,2):
        for attempt in range(1,13):
            launch=subprocess.run([sys.executable,str(ROOT/'tools/launch_fixture.py'),'--shaders','--tiles','64','--terrain','refined','--resolution','1920x1080','--birth','Human:Cornac:Male:Berserker'],cwd=ROOT,capture_output=True,text=True)
            if launch.returncode: raise RuntimeError(launch.stdout+launch.stderr)
            meta=json.loads((SESSION/'processes.json').read_text())
            try:
                time.sleep(2);row=capture(level)
                survey['scenes'].append(row)
                (OUT/'survey.json').write_text(json.dumps(survey,indent=2)+'\n')
                print('PASS',row['label'],row['census'],row['lit_pixels']['gap'],flush=True)
                break
            except NoLava:
                print('RETRY level 1 without lava',attempt,flush=True)
            finally:stop_started(meta)
        else: raise AssertionError('No level 1 lava pool in 12 cold starts')
if __name__=='__main__':main()
