"""Arrange offline native actor fixtures and copy unedited engine screenshots."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import sys

ADDON=Path(__file__).resolve().parents[1]
WORKSPACE=ADDON.parents[2]
SESSION=WORKSPACE/'demo/checkerboard-v3/session'
CAPTURE_HOME=SESSION/'home/.t-engine/4.0/tome'
parser=argparse.ArgumentParser()
parser.add_argument('--round',default='v041')
parser.add_argument('--shader-only',action='store_true',help='Capture the separate shader-enabled state/adjacency check')
args=parser.parse_args()
assert args.round.replace('-','').isalnum()
OUT=ADDON/('evidence/runtime-'+args.round)
assert args.round!='v040','0.4.0 evidence is frozen; choose a new round'
(OUT/'screenshots').mkdir(parents=True,exist_ok=True)
DEBUG=WORKSPACE/'demo/board-hud/tools/debug.py'
COMMAND=WORKSPACE/'demo/checkerboard-v3/tools/command.py'
shots=[]

def lua(code):
    subprocess.run([sys.executable,str(DEBUG),code],check=True,timeout=55)

def view(width=1920,height=1080,tile=64):
    lua("game:setResolution('%dx%d Windowed',true); config.settings.tome.gfx.size='%dx%d'; game:setupDisplayMode(false); game.player:playerFOV(); game.level.map:centerViewAround(game.player.x,game.player.y)"%(width,height,tile,tile))

def shot(name,**info):
    src=CAPTURE_HOME/(name+'.png')
    src.unlink(missing_ok=True)
    subprocess.run([sys.executable,str(COMMAND),'shot',name],check=True,timeout=20)
    target=OUT/'screenshots'/src.name
    shutil.copy2(src,target)
    shots.append({'file':'screenshots/'+src.name,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'shaders':args.shader_only,**info})

lua("assert(core.shader.active(4)==%s,'cold-launch shader configuration does not match this capture run')"%('true' if args.shader_only else 'false'))
lua("monster_scene=assert(loadfile('/data-checker-fixture/monster-live_scene.lua'))(); monster_scene.setup('dense'); monster_scene.audit()")
view()
if args.shader_only:
    lua('monster_scene.stateSample()')
    shot('shader-states-1920-64',scene='dense-state-sample',size=[1920,1080],tile=64)
    lua('monster_scene.adjacentSample()')
    shot('shader-adjacent-1920-64',scene='adjacent-friend-enemy',size=[1920,1080],tile=64)
    lua("game.always_target='old';game.level.map:redisplay()")
    shot('shader-old-tactical-1920-64',scene='adjacent-friend-enemy',size=[1920,1080],tile=64,tactical='old')
    lua('game.always_target=true;game.level.map:redisplay()')
    (OUT/'capture-shader.json').write_text(json.dumps({'runtime':True,'edited':False,'shots':shots},ensure_ascii=False,indent=2)+'\n')
    print('Captured',len(shots),'unedited shader-enabled engine screenshots in',OUT)
    sys.exit(0)
shot('dense-1920-64',scene='dense',size=[1920,1080],tile=64)
lua("game.checker_native_actors=true; for _,a in pairs(game.level.entities) do if a.ai then game:checkerRefreshActor(a);game.level.map:updateMap(a.x,a.y) end end;game.level.map:redisplay()")
shot('native-actors-1920-64',scene='dense',size=[1920,1080],tile=64,nativeActors=True)
lua("game.checker_native_actors=nil;game:checkerSetMode('refined')")
view(tile=96)
shot('dense-1920-96',scene='dense',size=[1920,1080],tile=96)
for kind in ('giants','beasts','water'):
    lua("monster_scene.setup('%s')"%kind)
    shot(kind+'-1920-96',scene=kind,size=[1920,1080],tile=96)
lua("monster_scene.setup('dense');monster_scene.audit()")
view(1366,768,64)
shot('dense-1366-64',scene='dense',size=[1366,768],tile=64)
view(1366,768,48)
shot('dense-1366-48',scene='dense',size=[1366,768],tile=48)
view()
lua("monster_scene.stateSample()")
shot('states-1920-64',scene='dense-state-sample',size=[1920,1080],tile=64)
lua("monster_scene.adjacentSample()")
shot('adjacent-1920-64',scene='adjacent-friend-enemy',size=[1920,1080],tile=64)
lua("game.always_target='old';game.level.map:redisplay()")
shot('old-tactical-1920-64',scene='adjacent-friend-enemy',size=[1920,1080],tile=64,tactical='old')
lua("game.always_target=true;game.level.map:redisplay()")
for p in CAPTURE_HOME.glob('monster-scene-*.txt'):
    shutil.copy2(p,OUT/p.name)
(OUT/'capture.json').write_text(json.dumps({'runtime':True,'edited':False,'shots':shots},ensure_ascii=False,indent=2)+'\n')
print('Captured',len(shots),'unedited engine screenshots in',OUT)
