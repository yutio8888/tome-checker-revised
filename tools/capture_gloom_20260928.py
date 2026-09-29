#!/usr/bin/env python3
"""Inspect one independently launched Heart of the Gloom map."""
import argparse,json,shutil,subprocess,sys
from pathlib import Path
from capture_korpul import Fixture,HOME,ROOT,SESSION,digest,png_size
OUT=ROOT/'evidence/heart-gloom-20260928'
SHOTS=OUT/'screenshots'

def read(name):
    p=HOME/name; data=json.loads(p.read_text());p.unlink(missing_ok=True);return data

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--skin',choices=('gloomy','dreamy'),required=True)
    ap.add_argument('--level',type=int,choices=(1,2,3),required=True)
    ap.add_argument('--replace',action='store_true');args=ap.parse_args()
    label=f'{args.skin}-L{args.level}'
    fixture=Fixture();SHOTS.mkdir(parents=True,exist_ok=True)
    result_path=OUT/'survey.json'
    result=json.loads(result_path.read_text()) if result_path.exists() else {'zones':[]}
    if args.replace:
        result['zones']=[z for z in result['zones'] if z['label']!=label]
    else:
        assert not any(z['label']==label for z in result['zones']),label
    plan=json.loads((SESSION/'launch-plan.json').read_text())
    assert plan['fixture'] and plan['shaders'] and plan['resolution']=='1920x1080'
    result.setdefault('launches',{})[label]=plan
    def save():
        result_path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
        (OUT/f'validation-{label}.txt').write_text((''.join(fixture.transcript)+fixture.new_log()).rstrip()+'\n')
    def shot(name):
        src=HOME/(name+'.png');src.unlink(missing_ok=True)
        proc=subprocess.run([sys.executable,str(ROOT/'tools/fixture_command.py'),'shot',name],capture_output=True,text=True,timeout=25)
        fixture.transcript.append(proc.stdout+proc.stderr);fixture.check_log()
        assert proc.returncode==0 and src.is_file() and png_size(src)==(1920,1080),(name,proc.stdout,proc.stderr)
        dst=SHOTS/src.name;shutil.copy2(src,dst)
        return {'file':'screenshots/'+dst.name,'sha256':digest(dst)}
    try:
        fixture.lua("assert(config.settings.cheat and config.settings.disable_all_connectivity and not profile.auth);"
                    "assert(core.shader.active(4));ms=dofile('/data-checker-fixture/monster-live_map_survey.lua');ms.setup()")
        purified='true' if args.skin=='dreamy' else 'false'
        fixture.lua(f"local enter=ms.enter('heart-gloom',{args.level},{{purified={purified}}});"
                    "local terrain=ms.terrainCensus();local details=ms.gloomDetails();"
                    "ms.dump('/gloom-data.json',{enter=enter,terrain=terrain,details=details})")
        data=read('gloom-data.json')
        entry={'label':label,'skin':args.skin,'level':args.level,**data}
        if entry['terrain']['supported']==0:
            fixture.lua("local m=game.level.map;local out={};local seen={};for x=0,m.w-1 do for y=0,m.h-1 do "
                        "local g=m(x,y,1);local id=g and g.define_as;"
                        "local family=id and (id:match('^UNDERGROUND_[A-Z]+') or id:match('^TREE')) or false;"
                        "if family and not seen[family] then seen[family]=true; "
                        "out[#out+1]={id=id,image=g.image,subtype=g.subtype,name=g.name,"
                        "stamp=g._checker_gloom_source or false,replace=g.replace_display and true or false," 
                        "add_mos=g.add_mos and #g.add_mos or false,add_displays=g.add_displays and #g.add_displays or false,"
                        "type=g.type,move=g.does_block_move or false,sight=g.block_sight or false,"
                        "pass=g.can_pass and g.can_pass.pass_tree or false,dig=g.dig or false,"
                        "on_stand=type(g.on_stand),on_move=type(g.on_move),on_dig=type(g.on_dig),"
                        "block_move=type(g.block_move),shader=g.shader or false,"
                        "special=g.special or false,air=g.air_level or false,is_door=g.is_door or false} end "
                        "end end;ms.dump('/gloom-diagnostic.json',out)")
            entry['diagnostic']=read('gloom-diagnostic.json')
            result['zones'].append(entry);save()
        assert entry['enter']['is_purified']==(args.skin=='dreamy')
        assert entry['terrain']['supported']>0 and entry['terrain']['native']==0,entry['terrain']
        for kind in ('gloom-floor','gloom-creep','gloom-wall'):
            assert entry['details']['kinds'].get(kind,0)>0,(kind,entry['details'])
        assert entry['details']['ladders'],entry['details']
        fixture.lua("local pose=ms.gloomOpenPose();ms.dump('/gloom-pose.json',pose)")
        entry['open_pose']=read('gloom-pose.json')
        assert (entry['open_pose']['found'] and entry['open_pose']['open']>=20 and
                entry['open_pose']['creep']>0 and entry['open_pose']['wall']>0 and
                entry['open_pose']['near_exit']>0),entry['open_pose']
        shots=[]
        for tile in ((48,64,96) if args.level==1 else (64,)):
            fixture.lua("game:setResolution('1920x1080 Windowed',true);"
                        f"config.settings.tome.gfx.size='{tile}x{tile}';game:setupDisplayMode(false);"
                        "ms.focus(game.player.x,game.player.y);ms.gloomStageView()")
            im=shot(f'{label}-open-{tile}');im['tile']=tile;shots.append(im)
        entry['screenshots']=shots
        fixture.lua("ms.setMode('vanilla');local v=ms.terrainCensus();"
                    "ms.setMode('blockout');local b=ms.terrainCensus();"
                    "ms.setMode('refined');local r=ms.terrainCensus();"
                    "ms.dump('/gloom-modes.json',{vanilla=v,blockout=b,refined=r})")
        entry['modes']=read('gloom-modes.json')
        assert entry['modes']['vanilla']['owned']==0
        assert entry['modes']['blockout']['native']==0
        assert entry['modes']['refined']['native']==0
        if args.level==1:
            fixture.lua("local d=ms.digGloom();ms.dump('/gloom-dig.json',d)")
            entry['dig']=read('gloom-dig.json')
            assert entry['dig']['found'] and entry['dig']['after_kind']=='gloom-floor' and entry['dig']['after_owned'],entry['dig']
        result['zones'].append(entry);result['complete']=len(result['zones'])==6;save()
        print('OK',label,entry['terrain'],entry['details']['kinds'],flush=True)
    finally:save()
if __name__=='__main__':main()
