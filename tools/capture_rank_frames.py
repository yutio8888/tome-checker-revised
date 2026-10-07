"""Original PNGs comparing native rank frames and the 0.4.5 token badges."""
from pathlib import Path
import hashlib
import json
import shutil
import struct
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
WORKSPACE=ROOT.parents[2]
OUT=ROOT/'evidence/runtime-v045'
CAPTURE_HOME=WORKSPACE/'demo/checkerboard-v3/session/home/.t-engine/4.0/tome'
DEBUG=WORKSPACE/'demo/board-hud/tools/debug.py'
COMMAND=WORKSPACE/'demo/checkerboard-v3/tools/command.py'
(OUT/'screenshots').mkdir(parents=True,exist_ok=True)
shots=[]

def lua(code):
    subprocess.run([sys.executable,str(DEBUG),code],check=True,timeout=55)

def view(tile):
    lua("game:setResolution('1920x1080 Windowed',true);config.settings.tome.gfx.size='%dx%d';"
        "game:setupDisplayMode(false);game.player:playerFOV();"
        "game.level.map:centerViewAround(game.player.x,game.player.y);"
        "assert(game.level.map.tile_w==%d and core.shader.active(4))"%(tile,tile,tile))

def shot(name,tile,native=False):
    src=CAPTURE_HOME/(name+'.png');src.unlink(missing_ok=True)
    subprocess.run([sys.executable,str(COMMAND),'shot',name],check=True,timeout=25)
    raw=src.read_bytes()
    assert raw[:8]==b'\x89PNG\r\n\x1a\n' and struct.unpack('>II',raw[16:24])==(1920,1080)
    shutil.copy2(src,OUT/'screenshots'/src.name)
    shots.append(dict(file='screenshots/'+src.name,size=[1920,1080],tile=tile,shaders=True,
                      nativeActors=native,addonVersion='0.4.5',sha256=hashlib.sha256(raw).hexdigest()))

lua("assert(core.shader.active(4));game.always_target=true;"
    "rank_scene=assert(loadfile('/data-checker-fixture/monster-live_ranks.lua'))();rank_scene.setup()")
view(96)
lua("game.checker_native_actors=true;game:checkerSetMode('refined')")
shot('native-rank-frames-1920-96',96,True)
lua("game.checker_native_actors=false;game:checkerSetMode('refined')")
for tile in (96,64,48):
    view(tile)
    shot('rank-frame-colors-1920-'+str(tile),tile)
lua("""local S=require 'mod.class.CheckerTokenStyle'
local f=assert(fs.open('/rank-frame-colors.txt','w'))
for _,a in ipairs(rank_scene.actors) do
 local badge=S.rankBadge(a.rank);local color=badge and S.rank_colors[badge]
 assert(a._checker_token and a._checker_token.id=='wolf')
 f:write(('%s rank=%s badge=%s rgb=%s native_danger=%s high_danger=%s\\n'):format(
  a:textRank(),tostring(a.rank),badge or 'none',color and table.concat(color,',') or 'none',
  tostring(game.level.map:faction_danger_check(a)),tostring(game.level.map:faction_danger_check(a,true))))
end
f:close()
assert(not S.rankBadge(2) and not S.rankBadge(3))
assert(S.colors.player[1]==30 and S.colors.friend[2]==210 and S.colors.neutral[3]==245)""")
shutil.copy2(CAPTURE_HOME/'rank-frame-colors.txt',OUT/'rank-frame-colors.txt')
shutil.copy2(CAPTURE_HOME/'rank-display-sample.txt',OUT/'rank-display-sample.txt')
view(64)
(OUT/'capture.json').write_text(json.dumps(dict(runtime=True,edited=False,shots=shots),indent=2)+'\n')
print('Captured native-frame reference and 0.4.5 badges at 96, 64 and 48px.')
