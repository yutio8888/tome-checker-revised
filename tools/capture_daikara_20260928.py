#!/usr/bin/env python3
"""Daikara live driver; called once per isolated cold start."""
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from capture_korpul import Fixture, HOME, ROOT, SESSION, digest, png_size

OUT = ROOT / 'evidence/daikara-20260928'
SHOTS = OUT / 'screenshots'

def read_json(name):
    path = HOME / name
    data = json.loads(path.read_text())
    path.unlink(missing_ok=True)
    return data

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--layout', choices=('default', 'volcano'), required=True)
    parser.add_argument('--level', type=int, choices=(1, 2, 3, 4), required=True)
    parser.add_argument('--replace', action='store_true', help='replace an earlier validation of this layout and level')
    args = parser.parse_args()
    label = f'daikara-L{args.level}-{args.layout}'
    fixture = Fixture()
    SHOTS.mkdir(parents=True, exist_ok=True)
    plan = json.loads((SESSION / 'launch-plan.json').read_text())
    assert plan.get('fixture') and plan.get('shaders') and plan.get('resolution') == '1920x1080'
    scene = 'live_map_survey'
    installed = SESSION / f'runtime/game/addons/tome-checker-fixture/data/monster-{scene}.lua'
    assert digest(installed) == digest(ROOT / f'tests/{scene}.lua')
    for rel in ('overload/mod/class/CheckerTerrain.lua', 'superload/mod/class/Game.lua',
                'superload/engine/Map.lua'):
        assert digest(SESSION / 'runtime/game/addons/tome-checker-revised' / rel) == digest(ROOT / rel)
    result_path = OUT / 'survey.json'
    result = json.loads(result_path.read_text()) if result_path.exists() else {'zones': []}
    if args.replace:
        result['zones'] = [z for z in result['zones'] if z['label'] != label]
    else:
        assert not any(z['label'] == label for z in result['zones'])
    result.update(scene_sha256=digest(ROOT / f'tests/{scene}.lua'), complete=False)
    result.setdefault('launches', {})[label] = plan

    def save():
        result_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
        (OUT / f'validation-{label}.txt').write_text((''.join(fixture.transcript)+fixture.new_log()).rstrip()+'\n')

    def shot(name):
        source = HOME / (name + '.png')
        source.unlink(missing_ok=True)
        proc = subprocess.run([sys.executable, str(ROOT / 'tools/fixture_command.py'), 'shot', name],
                              capture_output=True, text=True, timeout=25)
        fixture.transcript.append(proc.stdout + proc.stderr)
        fixture.check_log()
        assert proc.returncode == 0 and source.is_file() and png_size(source) == (1920, 1080), name
        target = SHOTS / source.name
        shutil.copy2(source, target)
        return {'file':'screenshots/'+target.name,'sha256':digest(target),'resolution':[1920,1080]}

    try:
        fixture.lua("assert(config.settings.cheat and config.settings.disable_all_connectivity and not profile.auth);"
                    "assert(core.shader.active(4));ms=dofile('/data-checker-fixture/monster-live_map_survey.lua');ms.setup()")
        volcano = 'true' if args.layout == 'volcano' else 'false'
        fixture.lua(f"local enter=ms.enter('daikara',{args.level},{{volcano={volcano}}});"
                    "local terrain=ms.terrainCensus();local details=ms.daikaraDetails();"
                    "ms.dump('/ms-result.json',{enter=enter,terrain=terrain,details=details})")
        data = read_json('ms-result.json')
        entry = {'label':label,'level':args.level,'layout':args.layout,
                 'enter':data['enter'],'terrain':data['terrain'],'details':data['details']}
        assert entry['enter']['is_volcano'] == (args.layout == 'volcano')
        assert entry['terrain']['supported']>0 and entry['terrain']['native']==0, entry['terrain']
        ids = entry['details']['ids']
        for prefix in ('ROCKY_GROUND','MOUNTAIN_WALL','ROCKY_SNOWY_TREE'):
            assert sum(v['count'] for k,v in ids.items() if k.startswith(prefix))>0, (prefix,ids)
        if args.layout=='volcano':
            assert sum(v['count'] for k,v in ids.items() if k.startswith('LAVA_FLOOR'))>0, ids
        if args.layout=='volcano' and args.level==4:
            down=entry['details']['default_down']
            assert down and down['kind']=='lava-floor' and down['owned'] and not down['change_level'], down
        fixture.lua("local pose=ms.daikaraOpenPose(game.zone.is_volcano);ms.dump('/ms-pose.json',pose)")
        entry['open_pose']=read_json('ms-pose.json')
        assert entry['open_pose']['found'] and entry['open_pose']['open']>=30, entry['open_pose']
        shots=[]
        for tile in ((48,64,96) if args.level==1 or (args.layout=='volcano' and args.level==4) else (64,)):
            fixture.lua("game:setResolution('1920x1080 Windowed',true);"
                        f"config.settings.tome.gfx.size='{tile}x{tile}';game:setupDisplayMode(false);"
                        "ms.focus(game.player.x,game.player.y);ms.daikaraStageView()")
            image=shot(f'{label}-open-{tile}');image['tile']=tile;shots.append(image)
        entry['screenshots']=shots
        fixture.lua("ms.setMode('vanilla');local v=ms.terrainCensus();"
                    "ms.setMode('blockout');local b=ms.terrainCensus();"
                    "ms.setMode('refined');local r=ms.terrainCensus();"
                    "ms.dump('/ms-modecheck.json',{vanilla=v,blockout=b,refined=r})")
        entry['mode_round_trip']=read_json('ms-modecheck.json')
        assert entry['mode_round_trip']['vanilla']['owned']==0
        assert entry['mode_round_trip']['blockout']['native']==0
        assert entry['mode_round_trip']['refined']['native']==0
        if args.layout=='default' and args.level==1:
            for kind in ('mountain-wall','snow-tree'):
                fixture.lua(f"local d=ms.digDaikara('{kind}');ms.dump('/ms-dig.json',d)")
                dig=read_json('ms-dig.json')
                assert dig['found'] and dig['after_kind']=='rock-ground' and dig['after_owned'],dig
                entry.setdefault('dig',[]).append(dig)
        result['zones'].append(entry)
        result['complete'] = len(result['zones']) == 8
        save()
        print('OK',label,entry['terrain'],entry['open_pose'],flush=True)
    finally:
        save()

if __name__=='__main__':main()
