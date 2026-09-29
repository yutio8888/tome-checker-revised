"""Original engine PNGs for the shield lane and rank badge iteration."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parents[1];WORKSPACE=ROOT.parents[2]
OUT=ROOT/'evidence/runtime-v043';CAPTURE_HOME=WORKSPACE/'demo/checkerboard-v3/session/home/.t-engine/4.0/tome'
parser=argparse.ArgumentParser();parser.add_argument('--before',action='store_true');parser.add_argument('--no-shaders',action='store_true')
args=parser.parse_args();tag='before' if args.before else 'after-no-shader' if args.no_shaders else 'after'
DEBUG=WORKSPACE/'demo/board-hud/tools/debug.py';COMMAND=WORKSPACE/'demo/checkerboard-v3/tools/command.py'
(OUT/'screenshots').mkdir(parents=True,exist_ok=True);shots=[]
def lua(code):subprocess.run([sys.executable,str(DEBUG),code],check=True,timeout=55)
def view(tile):
    lua("game:setResolution('1920x1080 Windowed',true);config.settings.tome.gfx.size='%dx%d';game:setupDisplayMode(false);game.player:playerFOV();game.level.map:centerViewAround(game.player.x,game.player.y);assert(game.level.map.tile_w==%d)"%(tile,tile,tile))
def shot(name,tile,**extra):
    src=CAPTURE_HOME/(name+'.png');src.unlink(missing_ok=True)
    subprocess.run([sys.executable,str(COMMAND),'shot',name],check=True,timeout=20)
    dst=OUT/'screenshots'/src.name;shutil.copy2(src,dst)
    shots.append(dict(file='screenshots/'+src.name,size=[1920,1080],tile=tile,shaders=not args.no_shaders,
                      addonVersion='0.4.2' if args.before else '0.4.3',sha256=hashlib.sha256(dst.read_bytes()).hexdigest(),**extra))
lua("assert(core.shader.active(4)==%s);monster_scene=assert(loadfile('/data-checker-fixture/monster-live_scene.lua'))();monster_scene.setup('dense');monster_scene.healthSample();game.always_target=true"%str(not args.no_shaders).lower())
lua("""local fractions={['forest troll']=1,wolf=.5,['stone troll']=.25,['Prox the Mighty']=.75}
local f=assert(fs.open('/shield-display-sample.txt','w'))
for _,a in ipairs(monster_scene.actors) do
 local ratio=fractions[a.name]
 if ratio then a:setEffect(a.EFF_DAMAGE_SHIELD,5,{power=40},true);a.damage_shield_absorb=a.damage_shield_absorb_max*ratio end
 f:write(('%s rank=%s life=%.3f shield=%.3f/%.3f\\n'):format(a.name,tostring(a.rank),a.life,a.damage_shield_absorb or 0,a.damage_shield_absorb_max or 0))
end
f:close();monster_scene.adjacentSample();game.log('#LIGHT_BLUE#Shield sample: forest troll 100%%, friendly wolf 50%%, stone troll 25%%, Prox 75%%.');game.level.map:redisplay()""")
for tile in ((64,96) if args.before or args.no_shaders else (64,96,48)):
    view(tile);shot('shield-'+tag+'-1920-'+str(tile),tile)
if not args.before and not args.no_shaders:
    view(64)
    lua("game.always_target='old';game.level.map:redisplay()")
    shot('shield-old-1920-64',64,tactical='old')
    lua('game.always_target=false;game.level.map:redisplay()')
    shot('shield-hidden-values-1920-64',64,tactical=False)
    lua("game.always_target=true;game.checker_native_actors=true;game:checkerSetMode('refined')")
    shot('shield-native-fallback-1920-64',64,nativeActors=True)
    lua("game.checker_native_actors=false;game:checkerSetMode('refined')")
view(64)
shutil.copy2(CAPTURE_HOME/'shield-display-sample.txt',OUT/('shield-sample-'+tag+'.txt'))
(OUT/('capture-'+tag+'.json')).write_text(json.dumps(dict(runtime=True,edited=False,shots=shots),indent=2)+'\n')
print('Captured',len(shots),'engine screenshots:',tag)
