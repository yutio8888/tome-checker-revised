"""Exercise the real options/picker callbacks and settings across fresh launches."""
from pathlib import Path
import argparse,hashlib,json,re,shutil,struct,subprocess,sys,time

ROOT=Path(__file__).resolve().parents[1]
WORKSPACE=ROOT.parents[2]
SESSION=WORKSPACE/'demo/checkerboard-v3/session'
CAPTURE_HOME=SESSION/'home/.t-engine/4.0/tome'
SETTING=SESSION/'home/.t-engine/4.0/settings/tome.checker_rank_colors.cfg'
RELATION_SETTING=SESSION/'home/.t-engine/4.0/settings/tome.checker_relation_colors.cfg'
parser=argparse.ArgumentParser()
parser.add_argument('--output',default='evidence/options-v050-plus',help='A new evidence directory; historical v046 is frozen')
args=parser.parse_args()
OUT=ROOT/args.output
assert OUT.resolve().is_relative_to((ROOT/'evidence').resolve()) and OUT.name!='runtime-v046'
version='.'.join(re.search(r'addon_version\s*=\s*\{([^}]+)\}',(ROOT/'init.lua').read_text())[1].replace(' ','').split(','))
COMMAND=WORKSPACE/'demo/checkerboard-v3/tools/command.py'
DEBUG=WORKSPACE/'demo/board-hud/tools/debug.py'
(OUT/'screenshots').mkdir(parents=True,exist_ok=True)
shots=[];checks=[]

def run(path,*args):
    subprocess.run([sys.executable,str(path),*args],check=True,timeout=55)

def lua(code):
    run(DEBUG,code)

def shot(name):
    time.sleep(.8)  # Let modal closing/focus transitions settle before capture.
    src=CAPTURE_HOME/(name+'.png');src.unlink(missing_ok=True)
    run(COMMAND,'shot',name)
    raw=src.read_bytes();assert struct.unpack('>II',raw[16:24])==(1920,1080)
    shutil.copy2(src,OUT/'screenshots'/src.name)
    shots.append(dict(file='screenshots/'+src.name,size=[1920,1080],tile=96,shaders=True,
                      addonVersion=version,sha256=hashlib.sha256(raw).hexdigest()))

def stage():
    deadline=time.monotonic()+45
    while time.monotonic()<deadline:
        if '[CheckerFixture] BIRTH' in (SESSION/'game.log').read_text(errors='replace'):break
        time.sleep(.2)
    else:raise SystemExit('Fresh game process did not finish fixture birth')
    run(COMMAND,'stage');run(COMMAND,'mode','refined')
    lua("game:setResolution('1920x1080 Windowed',true);config.settings.tome.gfx.size='96x96';"
        "game:setupDisplayMode(false);rank_scene=assert(loadfile('/data-checker-fixture/monster-live_ranks.lua'))();"
        "rank_scene.setup();game.always_target=true;"
        "rank_scene.actors[1].faction=game.player.faction;rank_scene.actors[2].faction='neutral';"
        "local amounts={.25,.5,.75,1,.9,.1};for i,a in ipairs(rank_scene.actors) do a.life=a.max_life*amounts[i] end;"
        "game.level.map:redisplay();assert(core.shader.active(4) and game.level.map.tile_w==96)")

def options():
    lua("checker_options=require('mod.dialogs.GameOptions').new();game:registerDialog(checker_options);"
        "for _,t in ipairs(checker_options.c_tabs.tabs) do if t.title=='Token colors' then checker_options.c_tabs:select(t.kind) end end;"
        "assert(checker_options.list[1].checker_tokens_enabled and checker_options.list[2].checker_terrain_mode)")

def picker(key='rare',kind='badge'):
    lua("local item;for _,v in ipairs(checker_options.list) do if v.checker_%s=='%s' then item=v end end;"
        "assert(item);item.fct(item);checker_picker=game.dialogs[#game.dialogs];assert(checker_picker.color_key)"%(kind,key))

run(ROOT/'tools/launch_fixture.py','--shaders','--hero-token');stage()
lua("require('mod.class.CheckerTokenStyle').resetColors()")
original=SETTING.read_bytes()
original_relations=RELATION_SETTING.read_bytes()
options()
lua("local o=require('mod.class.CheckerOptions');local t=checker_options.list[1];local m=checker_options.list[2];"
    "t.fct(t);assert(not o.tokensEnabled() and game.checker_mode=='refined');"
    "m.fct(m);assert(not o.tokensEnabled() and game.checker_mode=='vanilla');"
    "t.fct(t);assert(o.tokensEnabled() and game.checker_mode=='vanilla');game:checkerSetMode('refined')")
checks.append('Real options callbacks toggle creature and terrain independently; terrain never re-enables disabled tokens.')
shot('palette-settings-1920')
picker();shot('palette-picker-1920')
lua("checker_picker:setDraft{40,200,230};checker_picker.cancel_button.fct();"
    "assert(require('mod.class.CheckerTokenStyle').rankColor('rare')[1]==250)")
assert SETTING.read_bytes()==original
checks.append('Cancel after editing leaves runtime color and settings file unchanged.')
picker()
lua("checker_picker:setDraft{40,200,230};checker_picker.default_button.fct();"
    "assert(checker_picker.draft[1]==250 and checker_picker.draft[2]==128 and checker_picker.draft[3]==114);"
    "checker_picker:setDraft{40,200,230};checker_picker.apply_button.fct();"
    "local S=require 'mod.class.CheckerTokenStyle';assert(S.rankColor('rare')[1]==40 and S.rankColor('rare')[3]==230);"
    "assert(S.rankColor('boss')[1]==255 and S.rankColor('boss')[2]==119)")
assert b'rare={40,200,230}' in SETTING.read_bytes()
checks.append('Default resets the draft; Apply saves only the edited rank and immediately updates live rendering.')
for key,color in [('friend','30,195,245'),('neutral','180,180,220'),('enemy','230,80,190')]:
    picker(key,'relation')
    lua("assert(checker_picker.kind=='relation' and checker_picker.color_key=='%s');checker_picker:setDraft{%s}"%(key,color))
    if key=='friend': shot('relation-picker-1920')
    lua('checker_picker.apply_button.fct()')
lua("local S=require 'mod.class.CheckerTokenStyle';"
    "assert(S.relationColor('friend')[1]==30 and S.relationColor('neutral')[1]==180 and S.relationColor('enemy')[1]==230);"
    "assert(S.relationColor('player')==S.colors.player and S.colors.player[1]==30);game:unregisterDialog(checker_options)")
checks.append('All three faction settings apply independently to partly wounded live actors; friendly cyan deliberately matches player hue while the player keeps its white inner line.')
shot('palette-custom-1920')
shutil.copy2(SETTING,OUT/'custom-setting.cfg.txt')
shutil.copy2(RELATION_SETTING,OUT/'custom-relations.cfg.txt')
first_log=(SESSION/'game.log').read_text(errors='replace')
assert not re.search(r'Lua Error|stack traceback|CheckerRefined[^\n]*ERROR|\[BoardDebug\][^\n]*FAIL',first_log)
run(WORKSPACE/'demo/checkerboard-v3/tools/stop.py')
from launch_fixture import assert_stopped,start
assert_stopped()
start(json.loads((SESSION/'launch-plan.json').read_text()))
stage()
lua("local S=require 'mod.class.CheckerTokenStyle';local c=S.rankColor('rare');"
    "assert(c[1]==40 and c[2]==200 and c[3]==230);assert(S.rankColor('boss')[2]==119);"
    "assert(S.relationColor('friend')[1]==30 and S.relationColor('neutral')[1]==180 and S.relationColor('enemy')[1]==230)")
checks.append('A fresh game process loads saved rank and all three faction RGB values without manual injection.')
options()
lua("local item=checker_options.list[#checker_options.list];assert(item.checker_reset);item.fct();"
    "local S=require 'mod.class.CheckerTokenStyle';assert(next(config.settings.tome.checker_rank_colors)==nil);"
    "assert(S.rankColor('rare')[1]==250 and S.rankColor('boss')[2]==119);"
    "assert(next(config.settings.tome.checker_relation_colors)==nil and S.relationColor('friend')[2]==210);"
    "assert(not S.rankBadge(2) and not S.rankBadge(3) and S.colors.player[1]==30);game:unregisterDialog(checker_options)")
assert SETTING.read_bytes()==original
assert RELATION_SETTING.read_bytes()==original_relations
checks.append('Restore default colors clears both palettes; warm badges and native faction hues restored, normal/elite unmarked, pearl shield preserved.')
shot('palette-restored-1920')
lua("local f=assert(fs.open('/color-health-sample.txt','w'));local S=require 'mod.class.CheckerTokenStyle';"
    "for i,a in ipairs(rank_scene.actors) do local relation=S.relation(a,game.player,game.player:reactionToward(a));"
    "f:write(('%d rank=%s relation=%s hp=%.0f%% cell=%d,%d\\n'):format(i,tostring(a.rank),relation,S.nativeLifeFraction(a)*100,a.x,a.y)) end;f:close()")
shutil.copy2(CAPTURE_HOME/'color-health-sample.txt',OUT/'color-health-sample.txt')
last_log=(SESSION/'game.log').read_text(errors='replace')
assert not re.search(r'Lua Error|stack traceback|CheckerRefined[^\n]*ERROR|\[BoardDebug\][^\n]*FAIL',last_log)
checks.append('Both final fresh-launch logs have no Lua errors or failed debug assertions.')
checks.append('Interaction tests invoke real menu items, native slider updates and button callbacks; not automated physical mouse dragging.')
(OUT/'validation-live.txt').write_text('\n'.join(checks)+'\n')
(OUT/'capture.json').write_text(json.dumps(dict(runtime=True,edited=False,shots=shots),indent=2)+'\n')
print('\n'.join(checks))
