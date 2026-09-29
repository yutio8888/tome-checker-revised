"""Unedited engine captures for a validated batch, with bounded coverage audit."""
from pathlib import Path
import argparse, hashlib, json, shutil, subprocess, sys
ROOT=Path(__file__).resolve().parents[1]
SESSION=ROOT.parents[2]/'demo/checkerboard-v3/session'
HOME=SESSION/'home/.t-engine/4.0/tome'
parser=argparse.ArgumentParser()
parser.add_argument('--round',required=True,choices=('v051','v052'))
parser.add_argument('--groups',nargs='+',default=['canines','snakes'])
args=parser.parse_args()
OUT=ROOT/('evidence/runtime-'+args.round)
(OUT/'screenshots').mkdir(parents=True,exist_ok=True)
shots=[]

def lua(code):
    result=subprocess.run([sys.executable,str(ROOT/'tools/fixture_debug.py'),code],check=True,timeout=55,capture_output=True,text=True)
    print(result.stdout.strip())

def view(w=1920,h=1080,t=64):
    lua("game:setResolution('%dx%d Windowed',true);config.settings.tome.gfx.size='%dx%d';game:setupDisplayMode(false);game.player:playerFOV();game.level.map:centerViewAround(game.player.x,game.player.y)"%(w,h,t,t))

def shot(name,w=1920,h=1080,t=64,**extra):
    src=HOME/(name+'.png');src.unlink(missing_ok=True)
    subprocess.run([sys.executable,str(ROOT/'tools/fixture_command.py'),'shot',name],check=True,timeout=20)
    target=OUT/'screenshots'/src.name;shutil.copy2(src,target)
    shots.append(dict(file='screenshots/'+src.name,resolution=[w,h],tile=t,sha256=hashlib.sha256(target.read_bytes()).hexdigest(),**extra))

lua("assert(core.shader.active(4));if not game.checker_staged then game:checkerStage() end;monster_scene=assert(loadfile('/data-checker-fixture/monster-live_scene.lua'))();monster_scene.setup('dense');monster_scene.audit();monster_scene.healthSample();monster_scene.stateSample();monster_scene.adjacentSample()")
for w,h,t in ((1920,1080,64),(1366,768,64),(1366,768,48)):
    view(w,h,t);shot('dense-'+str(w)+'-'+str(t),w,h,t)
for group in args.groups:
    assert group.replace('-','').isalnum()
    lua("monster_scene.setup('%s')"%group)
    for tile in (96,64,48):
        view(t=tile);shot(group+'-1920-'+str(tile),t=tile)
if args.round=='v052':
    view()
    lua("monster_scene.setup('swarms');multiply_audit=assert(loadfile('/data-checker-fixture/monster-live_multiply.lua'))();assert(multiply_audit.run().status=='PASS')")
    shot('multiply-1920-64',native_multiply=True)
    view(t=96)
    # Finish native smooth scrolling before capture; otherwise the largest
    # tiles can leave the grandchild above the frame during camera movement.
    lua("local m=game.level.map;local p=multiply_audit.actors[2];local smooth=m.smooth_scroll;m.smooth_scroll=0;m:centerViewAround(p.x,p.y);m.smooth_scroll=smooth;core.display.forceRedraw();for _,a in ipairs(multiply_audit.actors) do assert(a.x>=m.mx and a.x<m.mx+m.viewport.mwidth and a.y>=m.my and a.y<m.my+m.viewport.mheight,'Multiply actor outside screenshot') end")
    shot('multiply-1920-96',t=96,native_multiply=True,camera='center on child; native smooth scrolling settled before capture; all three actors asserted inside viewport')
    shutil.copy2(HOME/'multiply-validation.txt',OUT/'multiply-validation.txt')
    lua('multiply_audit.cleanup()')
lua("coverage=assert(loadfile('/data-checker-fixture/monster-live_coverage.lua'))();coverage.run()")
shutil.copy2(HOME/'token-coverage.tsv',OUT/'token-coverage.tsv')
subprocess.run([sys.executable,str(ROOT/'tools/report_coverage.py'),str(OUT/'token-coverage.tsv'),str(OUT/'coverage.md')],check=True)
for file in HOME.glob('monster-*.txt'):shutil.copy2(file,OUT/file.name)
log=(SESSION/'game.log').read_text()
tags=('[MonsterLive]','[MultiplyLive]','[MultiplyCapture]','[TokenCoverage]','[CheckerRefined] ERROR','Lua Error','[BoardDebug]')
(OUT/'validation-live.txt').write_text('\n'.join(l for l in log.splitlines() if any(t in l for t in tags))+'\n')
assert 'Lua Error' not in log and '[CheckerRefined] ERROR' not in log,'inspect game.log'
(OUT/'capture.json').write_text(json.dumps(dict(runtime=True,edited=False,shaders=True,ai_frozen=True,
    manifest=json.loads((ROOT/'data/token-manifest.json').read_text()),
    launch=json.loads((SESSION/'launch-plan.json').read_text()),shots=shots),indent=2)+'\n')
view()
lua("monster_scene.setup('dense');monster_scene.healthSample();monster_scene.stateSample();monster_scene.adjacentSample()")
print('Captured',len(shots),'original engine PNGs in',OUT)
