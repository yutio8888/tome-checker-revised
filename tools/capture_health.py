"""Capture the ring-health fixture at actual 48/64/96px tile sizes."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
WORKSPACE=ROOT.parents[2]
OUT=ROOT/'evidence/runtime-v042'
CAPTURE_HOME=WORKSPACE/'demo/checkerboard-v3/session/home/.t-engine/4.0/tome'
parser=argparse.ArgumentParser()
parser.add_argument('--shader',action='store_true')
args=parser.parse_args()
DEBUG=WORKSPACE/'demo/board-hud/tools/debug.py'
COMMAND=WORKSPACE/'demo/checkerboard-v3/tools/command.py'
(OUT/'screenshots').mkdir(parents=True,exist_ok=True)
shots=[]
def lua(code): subprocess.run([sys.executable,str(DEBUG),code],check=True,timeout=55)
def view(width,height,tile):
    lua("game:setResolution('%dx%d Windowed',true);config.settings.tome.gfx.size='%dx%d';game:setupDisplayMode(false);game.player:playerFOV();game.level.map:centerViewAround(game.player.x,game.player.y);assert(game.level.map.tile_w==%d)"%(width,height,tile,tile,tile))
def shot(name,width,height,tile,**extra):
    src=CAPTURE_HOME/(name+'.png');src.unlink(missing_ok=True)
    subprocess.run([sys.executable,str(COMMAND),'shot',name],check=True,timeout=20)
    dest=OUT/'screenshots'/src.name;shutil.copy2(src,dest)
    shots.append(dict(file='screenshots/'+src.name,size=[width,height],tile=tile,shaders=args.shader,
                      addonVersion='0.4.2',sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),**extra))
lua("assert(core.shader.active(4)==%s);monster_scene=assert(loadfile('/data-checker-fixture/monster-live_scene.lua'))();monster_scene.setup('dense');monster_scene.healthSample()"%str(args.shader).lower())
if args.shader:
    view(1920,1080,64)
    lua("for _,a in ipairs(monster_scene.actors) do if a.name=='forest troll' then a:setEffect(a.EFF_DAMAGE_SHIELD,5,{power=30},true) end end;monster_scene.adjacentSample()")
    shot('health-ring-shield-1920-64',1920,1080,64)
    view(1920,1080,96)
    shot('health-ring-shield-1920-96',1920,1080,96)
    view(1920,1080,64)
else:
    for width,height,tile in ((1920,1080,64),(1920,1080,96),(1366,768,48)):
        view(width,height,tile)
        shot('health-ring-%d-%d'%(width,tile),width,height,tile)
    view(1920,1080,64)
    lua("game.always_target='old';game.level.map:redisplay()")
    shot('health-ring-old-1920-64',1920,1080,64,tactical='old')
    lua('game.always_target=false;game.level.map:redisplay()')
    shot('health-hidden-1920-64',1920,1080,64,tactical=False)
    lua('game.always_target=true;game.level.map:redisplay()')
shutil.copy2(CAPTURE_HOME/'monster-health-sample.txt',OUT/('health-sample-shader.txt' if args.shader else 'health-sample-after.txt'))
(OUT/('capture-shader.json' if args.shader else 'capture-after.json')).write_text(json.dumps(dict(runtime=True,edited=False,shots=shots),indent=2)+'\n')
print('Captured',len(shots),'ring-health engine screenshots')
