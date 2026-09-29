"""Capture original engine PNGs for native faction hues and pearl shields."""
from pathlib import Path
import hashlib
import json
import shutil
import struct
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parents[2]
OUT = ROOT/'evidence/runtime-v044'
CAPTURE_HOME = WORKSPACE/'demo/checkerboard-v3/session/home/.t-engine/4.0/tome'
DEBUG = WORKSPACE/'demo/board-hud/tools/debug.py'
COMMAND = WORKSPACE/'demo/checkerboard-v3/tools/command.py'
(OUT/'screenshots').mkdir(parents=True, exist_ok=True)
shots = []


def lua(code):
    subprocess.run([sys.executable, str(DEBUG), code], check=True, timeout=55)


def view(tile):
    lua("game:setResolution('1920x1080 Windowed',true);"
        "config.settings.tome.gfx.size='%dx%d';game:setupDisplayMode(false);"
        "game.player:playerFOV();game.level.map:centerViewAround(game.player.x,game.player.y);"
        "assert(game.level.map.tile_w==%d and core.shader.active(4))" % (tile, tile, tile))


def shot(name, tile):
    src = CAPTURE_HOME/(name+'.png')
    src.unlink(missing_ok=True)
    subprocess.run([sys.executable, str(COMMAND), 'shot', name], check=True, timeout=25)
    raw = src.read_bytes()
    assert raw[:8] == b'\x89PNG\r\n\x1a\n'
    size = struct.unpack('>II', raw[16:24])
    assert size == (1920, 1080), size
    dst = OUT/'screenshots'/src.name
    shutil.copy2(src, dst)
    shots.append(dict(file='screenshots/'+src.name, size=size, tile=tile, shaders=True,
                      addonVersion='0.4.4', sha256=hashlib.sha256(raw).hexdigest()))


lua("assert(core.shader.active(4));"
    "monster_scene=assert(loadfile('/data-checker-fixture/monster-live_scene.lua'))();"
    "monster_scene.setup('dense');monster_scene.healthSample();game.always_target=true")
lua("""local S=require 'mod.class.CheckerTokenStyle'
assert(S.colors.friend[2]==210 and S.colors.neutral[3]==245 and S.colors.shield[1]==236)
local fractions={['forest troll']=1,wolf=.5,fox=.5,['stone troll']=.25,['Prox the Mighty']=.75}
for _,a in ipairs(monster_scene.actors) do
 local ratio=fractions[a.name]
 if ratio then a:setEffect(a.EFF_DAMAGE_SHIELD,5,{power=40},true);a.damage_shield_absorb=a.damage_shield_absorb_max*ratio end
end
monster_scene.adjacentSample()
local f=assert(fs.open('/palette-display-sample.txt','w'))
for _,a in ipairs(monster_scene.actors) do
 local relation=S.relation(a,game.player,game.player:reactionToward(a))
 f:write(('%s relation=%s rank=%s badge=%s cell=%d,%d life=%.3f shield=%.3f/%.3f\\n'):format(
  a.name,relation,tostring(a.rank),S.rankBadge(a.rank) or 'none',a.x,a.y,a.life,
  a.damage_shield_absorb or 0,a.damage_shield_absorb_max or 0))
end
f:close()
game.log('#ANTIQUE_WHITE#Pearl-white shield. Friendly wolf: green. Neutral fox: blue. Hostile: red.')
game.level.map:redisplay()""")
for tile in (64, 96, 48):
    view(tile)
    shot('faction-palette-1920-'+str(tile), tile)
shutil.copy2(CAPTURE_HOME/'palette-display-sample.txt', OUT/'palette-display-sample.txt')

lua("rank_scene=assert(loadfile('/data-checker-fixture/monster-live_ranks.lua'))();rank_scene.setup()")
for tile in (96, 64, 48):
    view(tile)
    shot('ranks-1920-'+str(tile), tile)
shutil.copy2(CAPTURE_HOME/'rank-display-sample.txt', OUT/'rank-display-sample.txt')
view(64)
(OUT/'capture.json').write_text(json.dumps(dict(runtime=True, edited=False, shots=shots), indent=2)+'\n')
print('Captured', len(shots), 'original 1920x1080 engine screenshots with shader level 4 active.')
