#!/usr/bin/env python3
"""Staged exit, Blockout and Native visuals in one isolated fixture process."""
import json
import shutil
import subprocess
import sys

from capture_korpul import Fixture, HOME, ROOT, SESSION, digest, png_size

OUT = ROOT / 'evidence/norgos-20260928'
SHOTS = OUT / 'screenshots'


def main():
    fixture = Fixture()
    plan = json.loads((SESSION / 'launch-plan.json').read_text())
    assert plan['fixture'] and plan['shaders'] and plan['resolution'] == '1920x1080'
    fixture.lua("ms=dofile('/data-checker-fixture/monster-live_map_survey.lua');ms.setup();"
        "function norgosPose(id) local m=game.level.map;local T=require('mod.class.CheckerTerrain');"
        "for x=0,m.w-1 do for y=0,m.h-1 do local g=m(x,y,1);if g and g.define_as==id then "
        "for _,d in ipairs{{1,0},{-1,0},{0,1},{0,-1}} do local nx,ny=x+d[1],y+d[2];"
        "local floor=nx>=0 and ny>=0 and nx<m.w and ny<m.h and m(nx,ny,1);"
        "if floor and not floor.does_block_move and not m(nx,ny,2) then "
        "game.player:move(nx,ny,true);ms.focus(x,y);"
        "return {id=id,x=x,y=y,player_x=game.player.x,player_y=game.player.y,"
        "kind=T.rockKind(m(x,y,1)),owned=m(x,y,1)._checker_terrain~=nil} end end end end end "
        "return {id=id,found=false} end")
    rows = []

    def read(name):
        p = HOME / name
        data = json.loads(p.read_text());p.unlink()
        return data

    def shot(label):
        source = HOME / (label + '.png')
        source.unlink(missing_ok=True)
        result = subprocess.run([sys.executable, str(ROOT / 'tools/fixture_command.py'),
                                 'shot', label], capture_output=True, text=True, timeout=25)
        fixture.transcript.append(result.stdout + result.stderr)
        fixture.check_log()
        assert result.returncode == 0 and source.is_file() and png_size(source) == (1920, 1080)
        target = SHOTS / source.name
        shutil.copy2(source, target)
        return {'file': 'screenshots/' + target.name, 'sha256': digest(target)}

    def pose(id, level):
        fixture.lua(f"ms.enter('norgos-lair',{level},{{invaded=false}});ms.setMode('refined');"
                    f"ms.dump('/norgos-pose.json',norgosPose('{id}'))")
        data = read('norgos-pose.json')
        assert data.get('kind') and data.get('owned'), data
        return data

    try:
        world = pose('ROCKY_UP_WILDERNESS', 1)
        world['refined'] = shot('norgos-world-refined-64')
        fixture.lua("ms.setMode('blockout');ms.dump('/norgos-mode.json',ms.terrainCensus())")
        world['blockout_census'] = read('norgos-mode.json')
        assert world['blockout_census']['native'] == 0
        world['blockout'] = shot('norgos-world-blockout-64')
        fixture.lua("ms.setMode('vanilla');ms.dump('/norgos-mode.json',ms.terrainCensus())")
        world['vanilla_census'] = read('norgos-mode.json')
        assert world['vanilla_census']['owned'] == 0
        world['vanilla'] = shot('norgos-world-vanilla-64')
        rows.append(world)
        down = pose('ROCKY_DOWN4', 1)
        down['refined'] = shot('norgos-down-refined-64')
        rows.append(down)
        up = pose('ROCKY_UP6', 2)
        up['refined'] = shot('norgos-up-refined-64')
        rows.append(up)
        (OUT / 'exit-poses.json').write_text(json.dumps(rows, indent=2) + '\n')
        print('PASS', len(rows), 'exits; blockout/native/refined photographed')
    finally:
        (OUT / 'validation-exit-poses.txt').write_text(
            (''.join(fixture.transcript) + fixture.new_log()).rstrip() + '\n')


if __name__ == '__main__':
    main()
