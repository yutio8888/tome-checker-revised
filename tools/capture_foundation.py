"""Capture a running, newly launched isolated HUD/addon combination."""
from pathlib import Path
import argparse, hashlib, json, shutil, subprocess, sys, time

ROOT=Path(__file__).resolve().parents[1]
SESSION=ROOT.parents[2]/'demo/checkerboard-v3/session'
HOME=SESSION/'home/.t-engine/4.0/tome'
OUT=ROOT/'evidence/runtime-v050'
parser=argparse.ArgumentParser()
parser.add_argument('kind',choices=('tokens-minimalist','board-only','combined'))
args=parser.parse_args()
(OUT/'screenshots').mkdir(parents=True,exist_ok=True)
records=[]
transcript=[]

def lua(code):
    result=subprocess.run([sys.executable,str(ROOT/'tools/fixture_debug.py'),code],check=True,timeout=55,capture_output=True,text=True)
    transcript.append(result.stdout)
    print(result.stdout.strip())

def view(w,h,tile=64):
    lua("game:setResolution('%dx%d Windowed',true);config.settings.tome.gfx.size='%dx%d';game:setupDisplayMode(false);game.player:playerFOV();game.level.map:centerViewAround(game.player.x,game.player.y)"%(w,h,tile,tile))

def shot(name,w,h,tile=64):
    src=HOME/(name+'.png');src.unlink(missing_ok=True)
    subprocess.run([sys.executable,str(ROOT/'tools/fixture_command.py'),'shot',name],check=True,timeout=20)
    target=OUT/'screenshots'/src.name;shutil.copy2(src,target)
    records.append(dict(file='screenshots/'+target.name,resolution=[w,h],tile=tile,shaders=True,edited=False,sha256=hashlib.sha256(target.read_bytes()).hexdigest()))

lua("assert(config.settings.disable_all_connectivity and not profile.auth);assert(core.shader.active(4));if not game.checker_staged then game:checkerStage() end")
if args.kind=='tokens-minimalist':
    lua("""assert(game.uiset.__CLASSNAME=='mod.class.uiset.Minimalist')
assert(not fs.exists('/mod/class/uiset/Board.lua'),'Board must be absent')
assert(game:checkerTokensEnabled() and game.checker_mode=='vanilla')
assert(not game.player._checker_token,'no fixture hero opt-in')
local n=0;for _,a in pairs(game.level.entities) do if a._checker_token then n=n+1 end end;assert(n>=5)
local dialog=require('mod.dialogs.GameOptions').new();local found=false
for _,t in ipairs(dialog.c_tabs.tabs) do if t.title=='Token colors' then found=true end end
assert(found,'Token colors tab unavailable');game:unregisterDialog(dialog)
print('[Foundation] Minimalist; no Board class; native terrain; tokens=',n,'native hero; token options present; native log fade=',game.uiset.logdisplay.logFading)
""")
    starting_resolution=json.loads((SESSION/'launch-plan.json').read_text())['resolution']
    sizes=((1366,768),) if starting_resolution=='1366x768' else ((1920,1080),(1366,768))
    for w,h in sizes:
        tag='resized' if w==1366 and starting_resolution=='1920x1080' else 'cold'
        view(w,h);time.sleep(3.2);shot(tag+'-minimalist-native-'+str(w),w,h)
    lua("game:checkerSetMode('refined');assert(game:checkerTokensEnabled());game:checkerSetTokensEnabled(false);assert(game.checker_mode=='refined');game:checkerSetMode('vanilla');game:checkerSetTokensEnabled(true)")
elif args.kind=='board-only':
    lua("""assert(game.uiset.__CLASSNAME=='mod.class.uiset.Board')
assert(not fs.exists('/mod/class/CheckerTokens.lua'),'Token addon must be absent')
assert(not game.checkerRefreshActor and not game.checkerSetTokensEnabled)
for _,a in pairs(game.level.entities) do assert(not a._checker_token) end
print('[Foundation] Board; no token runtime; native actors and terrain')""")
    shot('cold-board-native-1920',1920,1080)
else:
    lua("""assert(game.uiset.__CLASSNAME=='mod.class.uiset.Board')
monster_scene=assert(loadfile('/data-checker-fixture/monster-live_scene.lua'))()
monster_scene.setup('dense');monster_scene.audit();monster_scene.healthSample();monster_scene.stateSample();monster_scene.adjacentSample()
for _,a in ipairs(monster_scene.actors) do if a.name=='Bill the Stone Troll' then a.can_talk=true end end
print('[Foundation] Both addons; current states, friend, neutral and talking Boss')""")
    for w,h,t in ((1920,1080,64),(1366,768,48),(1920,1080,96)):
        view(w,h,t);shot('joint-states-'+str(w)+'-'+str(t),w,h,t)
    view(1920,1080)
suffix='-1366' if args.kind=='tokens-minimalist' and starting_resolution=='1366x768' else ''
(OUT/('capture-'+args.kind+suffix+'.json')).write_text(json.dumps(dict(launch=json.loads((SESSION/'launch-plan.json').read_text()),shots=records),indent=2)+'\n')
(OUT/('validation-'+args.kind+suffix+'.txt')).write_text('\n'.join(transcript).rstrip()+'\n')
shutil.copy2(SESSION/'game.log',OUT/('game-'+args.kind+suffix+'.log'))
print('Captured',len(records),args.kind)
