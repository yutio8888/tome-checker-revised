#!/usr/bin/env python3
"""Gloom wall rework live check (2026-09-30) in the isolated fixture only.

Each phase installs a packaged TEAA built from a clean addon copy (HEAD for
`before`, HEAD plus the reworked data/gfx/refined/gloom walls for `after`),
so unrelated uncommitted work in the development tree never enters the
fixture (a directory install always copies the development tree):

    python3 tools/run_gloom_walls_validation.py before --teaa <copy>/dist/<name>.teaa \
        --out evidence/gloom-walls-20260930

One cold launch per phase (shaders on, 1920x1080, Refined terrain). Each scene
is entered after rng.seed(<fixed>) so both phases generate the same map:
Heart of the Gloom L1 gloomy (is_purified=false), L1 dreamy (true) and The
Deep Bellow L1 (plain). The player is moved to the passable cell with the most
board wall cells around it (at least 12 open cells), the surrounding cells are
staged visible (fixture only), and frames are taken at 48/64/96 px, plus a
64 px frame where that ring is only remembered and the player's sight is
cut to 2 cells (fixture only), so most of the crop is the dim remembered state. Wall and
floor mean grey around sampled cells and the wall mask census are recorded.

Before launching, the recorded game/Xvfb pids in session/processes.json are
checked via /proc/<pid>/cmdline (run_tw2_validation.wait_free); only the
processes this tool started are stopped.
"""
import argparse, hashlib, json, subprocess, sys, time, zipfile
from pathlib import Path
from capture_korpul import Fixture, HOME, ROOT, SESSION, digest, png_size
from run_norgos_validation import stop_started
from run_tw2_validation import launch

SEED = 30930
SCENES = (('gloomy-L1', 'heart-gloom', 1, 'false', 'gloomy'),
          ('dreamy-L1', 'heart-gloom', 1, 'true', 'dreamy'),
          ('bellow-L1', 'deep-bellow', 1, None, 'plain'))

POSE = r"""
(function(skin)
 local Map=require 'engine.Map'
 local T=require 'mod.class.CheckerTerrain'
 local m,p=game.level.map,game.player
 local best
 for x=9,m.w-10 do for y=7,m.h-8 do
  local g=m(x,y,Map.TERRAIN)
  if g and not g.does_block_move and not g.change_level and not g.change_zone and not m(x,y,Map.ACTOR) then
   local open,wall=0,0
   for dx=-7,7 do for dy=-5,5 do
    local t=m(x+dx,y+dy,Map.TERRAIN)
    if t and not t.does_block_move then open=open+1 end
    if T.gloomTerrain(t,skin)=='gloom-wall' then wall=wall+1 end
   end end
   if open>=12 then
    local score=wall*10+math.min(open,40)
    if not best or score>best.score then best={x=x,y=y,open=open,wall=wall,score=score} end
   end
  end
 end end
 if not best then return {found=false} end
 p:move(best.x,best.y,true);p.sight=20
 local masks={}
 local dirs={{0,-1},{1,0},{0,1},{-1,0}}
 for x=0,m.w-1 do for y=0,m.h-1 do
  if T.gloomTerrain(m(x,y,Map.TERRAIN),skin)=='gloom-wall' then
   local k=0
   for i,d in ipairs(dirs) do
    local nx,ny=x+d[1],y+d[2]
    if nx>=0 and ny>=0 and nx<m.w and ny<m.h and T.gloomTerrain(m(nx,ny,Map.TERRAIN),skin)=='gloom-wall' then k=k+2^(i-1) end
   end
   masks[tostring(k)]=(masks[tostring(k)] or 0)+1
  end
 end end
 best.found=true;best.masks=masks;best.zone=game.zone.short_name;best.purified=game.zone.is_purified and true or false
 return best
end)('%s')
"""

STAGE = r"""
(function()
 local m,p=game.level.map,game.player
 for x=math.max(0,p.x-17),math.min(m.w-1,p.x+17) do
  for y=math.max(0,p.y-12),math.min(m.h-1,p.y+12) do m.seens(x,y,true);m.infovs(x,y,true);m.remembers(x,y,true) end
 end
 m:redisplay();m.changed=true;core.display.forceRedraw()
 local T=require 'mod.class.CheckerTerrain'
 local Map=require 'engine.Map'
 local cells={}
 local tile=m.tile_w
 for x=math.max(0,p.x-7),math.min(m.w-1,p.x+7) do for y=math.max(0,p.y-5),math.min(m.h-1,p.y+5) do
  local k=T.gloomTerrain(m(x,y,Map.TERRAIN),'%s')
  if k then
   local sx,sy=m:getTileToScreen(x,y,true)
   cells[#cells+1]={family=k,sx=sx,sy=sy,img=m(x,y,Map.TERRAIN).image}
  end
 end end
 return {tile=tile,cells=cells}
end)()
"""

# Same sampling, but cells are only remembered; seen/lit state is reset so
# the player's native FOV recomputation decides what is currently visible.
REMEMBER = STAGE.replace("m.seens(x,y,true);m.infovs(x,y,true);m.remembers(x,y,true)",
                         "m.seens(x,y,false);m.infovs(x,y,false);m.remembers(x,y,true)")
assert REMEMBER != STAGE


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('phase', choices=('before', 'after'))
    ap.add_argument('--out', required=True)
    ap.add_argument('--teaa', required=True)
    a = ap.parse_args()
    out = Path(a.out)
    shots = out / 'screenshots'
    shots.mkdir(parents=True, exist_ok=True)
    meta = launch(a.teaa)
    f = Fixture()
    result = {'phase': a.phase, 'seed': SEED, 'addon_copy': str(ROOT), 'scenes': []}

    def dump(code, name='gw.json'):
        f.lua(f"ms.dump('/{name}',{code})")
        p = HOME / name
        v = json.loads(p.read_text())
        p.unlink()
        return v

    def shot(name):
        src = HOME / (name + '.png')
        src.unlink(missing_ok=True)
        call = subprocess.run([sys.executable, str(ROOT / 'tools/fixture_command.py'), 'shot', name],
                              capture_output=True, text=True, timeout=35)
        f.transcript.append(call.stdout + call.stderr)
        f.check_log()
        assert call.returncode == 0 and src.is_file() and png_size(src) == (1920, 1080), (call.stdout, call.stderr)
        dst = shots / src.name
        dst.write_bytes(src.read_bytes())
        return {'file': 'screenshots/' + dst.name, 'sha256': digest(dst)}

    try:
        plan = json.loads((SESSION / 'launch-plan.json').read_text())
        assert plan['fixture'] and plan['shaders'] and plan['resolution'] == '1920x1080' and plan['terrain'] == 'refined'
        result['launch_plan'] = plan
        installed = plan['teaa_installed']['checker-revised']
        result['teaa'] = installed
        with zipfile.ZipFile(installed['path']) as z:
            result['installed_wall_15_0'] = {}
            for skin in ('gloomy', 'dreamy', 'plain'):
                rel = f'data/gfx/refined/gloom/{skin}/wall-15-0.png'
                assert z.getinfo(rel).compress_type == zipfile.ZIP_STORED, rel
                result['installed_wall_15_0'][skin] = hashlib.sha256(z.read(rel)).hexdigest()
        f.lua("assert(config.settings.cheat and config.settings.disable_all_connectivity and not profile.auth);"
              "assert(core.shader.active(4));ms=dofile('/data-checker-fixture/monster-live_map_survey.lua');ms.setup();"
              "config.settings.tome.weather_effects=false")
        for label, zone, level, purified, skin in SCENES:
            f.lua("game:setResolution('1920x1080 Windowed',true);config.settings.tome.gfx.size='64x64';game:setupDisplayMode(false)")
            f.lua(f'rng.seed({SEED})')
            opts = f"{{purified={purified}}}" if purified else '{}'
            row = {'label': label, 'zone': zone, 'level': level, 'skin': skin}
            row['enter'] = dump(f"ms.enter('{zone}',{level},{opts})")
            f.lua('ms.caveClearDialogs()')
            row['pose'] = dump(POSE % skin)
            assert row['pose']['found'], row['pose']
            row['census'] = dump('ms.terrainCensus()')
            row['frames'] = []
            for tile in (48, 64, 96):
                f.lua(f"game:setResolution('1920x1080 Windowed',true);config.settings.tome.gfx.size='{tile}x{tile}';"
                      "game:setupDisplayMode(false);ms.focus(game.player.x,game.player.y)")
                cells = dump(STAGE % skin)
                time.sleep(.6)
                fr = shot(f'gw-{a.phase}-{label}-{tile}')
                fr['tile'] = tile
                fr['cells'] = cells
                row['frames'].append(fr)
            # Dim/remembered view at 64 px: the staged ring is remembered
            # only; native FOV decides what is currently seen.
            f.lua("game:setResolution('1920x1080 Windowed',true);config.settings.tome.gfx.size='64x64';"
                  "game:setupDisplayMode(false)")
            cells = dump(REMEMBER % skin)
            # Fixture only: a 2-cell sight radius so most of the crop is the
            # dim remembered state rather than current FOV.
            f.lua('game.player.sight=2;ms.focus(game.player.x,game.player.y)')
            time.sleep(.6)
            fr = shot(f'gw-{a.phase}-{label}-remembered-64')
            fr['tile'] = 64
            fr['remembered'] = True
            fr['cells'] = cells
            row['frames'].append(fr)
            f.lua('game.player.sight=20')
            result['scenes'].append(row)
            print('OK', label, row['pose'].get('wall'), row['census'].get('native') if isinstance(row['census'], dict) else None, flush=True)
    except Exception as e:
        result['error'] = repr(e)[:4000]
        print('ERROR', result['error'], flush=True)
    finally:
        (out / f'validation-{a.phase}.txt').write_text((''.join(f.transcript) + f.new_log()).rstrip() + '\n')
        (out / f'live-{a.phase}.json').write_text(json.dumps(result, ensure_ascii=False, indent=1) + '\n')
        stop_started(meta)
        print('STOP', a.phase, flush=True)


if __name__ == '__main__':
    main()
