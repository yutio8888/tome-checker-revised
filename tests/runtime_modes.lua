-- Pure production/fixture integration checks. Run with Lua 5.1 or LuaJIT.
local script=debug.getinfo(1,'S').source:sub(2)
local root=(script:match('^(.*[/\\])') or './')..'../'
local checks=0
local function equal(actual,expected,label)
 checks=checks+1
 assert(actual==expected,label..': expected '..tostring(expected)..', got '..tostring(actual))
end
local env=setmetatable({config={settings={cheat=false,tome={unrelated='keep'}}},__module_extra_info={}},{__index=_G})
local function load(path)
 local chunk
 if setfenv then chunk=assert(loadfile(root..path));setfenv(chunk,env)
 else chunk=assert(loadfile(root..path,'t',env)) end
 return chunk()
end
local modules={}
local Entity={new=function(def) def.removeAllMOs=function() end;return def end}
local Map={TERRAIN=1,ACTOR=2}
modules['engine.Map']=Map;modules['engine.Entity']=Entity
modules['mod.class.CheckerTokens']=load('overload/mod/class/CheckerTokens.lua')
modules['mod.class.CheckerOptions']=load('overload/mod/class/CheckerOptions.lua')
modules['mod.class.CheckerPlayerTokens']=load('overload/mod/class/CheckerPlayerTokens.lua')
local Tokens,Options=modules['mod.class.CheckerTokens'],modules['mod.class.CheckerOptions']
local PlayerTokens=modules['mod.class.CheckerPlayerTokens']
env.require=function(name) return assert(modules[name],'unexpected module '..name) end
env.loadPrevious=function() return {} end
modules['mod.class.CheckerTerrain']=load('overload/mod/class/CheckerTerrain.lua')
local Game=load('superload/mod/class/Game.lua')
local gridMethods={removeAllMOs=function() end,clone=function(self)
 local out={};for k,v in pairs(self) do out[k]=v end
 return setmetatable(out,getmetatable(self))
end}
local function grid(fields) return setmetatable(fields,{__index=gridMethods}) end
local grass=grid{name='grass',subtype='grass',type='floor',define_as='GRASS',image='terrain/grass.png',block_sight=false}
local map=setmetatable({w=3,h=2,cells={},updates=0,redraws=0},{__call=function(self,x,y,layer,value)
 if x<0 or x>=self.w or y<0 or y>=self.h then return nil end
 local key=x+y*self.w
 if value then self.cells[key]=value end
 return self.cells[key]
end})
function map:updateMap() self.updates=self.updates+1 end
function map:redisplay() self.redraws=self.redraws+1 end
for i=0,5 do map.cells[i]=grass end
map.cells[1]=grid{name='vault floor',subtype='stone',image='vault.png'}
map.cells[2]=grid{name='deep water',subtype='water',air_level=-1,image='water.png'}
map.cells[3]=grid{name='tree',subtype='grass',does_block_move=true,block_sight=true,image='tree.png'}
map.cells[4]=grid{name='troll stew',subtype='grass',does_block_move=true,image='stew.png'}
local writes={}
local player={name='normal halfling archmage',unique='player',type='humanoid',subtype='halfling',
 image='player/halfling.png',removeAllMOs=function() end,life=83,x=0,y=0,
 descriptor={subrace='Halfling',sex='Male',subclass='Archmage'},male=true,moddable_tile='halfling_#sex#',
 updateModdableTile=function() end}
local party={findMember=function(_,filter) assert(filter.main) return player end,hasMember=function() return true end}
local game=setmetatable({level={map=map,entities={player}},zone={short_name='derth'},player=player,party=party,
 checker_hero=player,checker_mode='refined',turn=19,
 saveSettings=function(_,key,value) writes[#writes+1]={key,value} end},{__index=Game})
env.game=game
local function actor(entry)
 return {name=entry.name,type=entry.type,subtype=entry.subtype,image=entry.image,
  define_as=entry.define_as,unique=entry.unique and true or nil,ai='test',
  life=41,max_life=79,x=1,y=0,removeAllMOs=function() end}
end

equal(Options.tokensEnabled(),true,'tokens enabled by default')
equal(Options.auraStyle(),'subtle','aura style defaults to B')
equal(Options.terrainMode(),'vanilla','terrain defaults to native')
equal(Options.tokenFacing(),'fixed','facing defaults to fixed lighting')
equal(Options.playerTokensEnabled(),true,'player token defaults on')
equal(next(PlayerTokens.available),nil,'no reviewed player art is available by default')
for _,entry in ipairs(Tokens.catalog) do
 local a=actor(entry);game.level.entities[#game.level.entities+1]=a
 equal(game:checkerRefreshActor(a),entry.id,'no cheat/demo/zone gate '..entry.id)
end
-- A mapped key without reviewed art stays native; the demo hero is never a
-- production fallback, even for the exact Cornac Berserker it depicts.
equal(game:checkerRefreshActor(player),nil,'mapped key without art keeps native player')
equal(player.replace_display,nil,'ordinary player keeps native appearance')
PlayerTokens.available.halfling_male=true
equal(game:checkerRefreshActor(player),'player:halfling_male','reviewed body-family art is used for the main hero')
equal(player.replace_display.image,'checker-revised+tokens/player-halfling_male.png','production player art, not the demo hero')
game:checkerSetPlayerTokensEnabled(false)
equal(game:checkerRefreshActor(player),nil,'player toggle off keeps native player')
equal(player.replace_display,nil,'player toggle off restores native appearance')
game:checkerSetPlayerTokensEnabled(true)
player.descriptor={subrace='Cornac',sex='Male',subclass='Berserker'};player.moddable_tile='human_#sex#'
equal(game:checkerRefreshActor(player),nil,'Cornac Berserker without reviewed art never uses fixed demo hero')
equal(player.replace_display,nil,'demo hero art is not a production fallback')
player.descriptor={subrace='Halfling',sex='Male',subclass='Archmage'};player.moddable_tile='halfling_#sex#'
PlayerTokens.available.halfling_male=nil
equal(game:checkerRefreshActor(player),nil,'removing art restores native player')
local unknown=actor(Tokens.by_id.wolf);unknown.name='unknown wolf species'
equal(game:checkerRefreshActor(unknown),nil,'unknown same-family creature stays native')
local wolf=game.level.entities[3]
equal(wolf._checker_token.id,'wolf','test subject is the exact native wolf')
local body=wolf.replace_display
game:checkerSetMode('vanilla')
equal(wolf.replace_display,body,'vanilla terrain does not disable tokens')
equal(map.cells[0],grass,'outside Trollmire terrain remains untouched')
game:checkerSetTokensEnabled(false)
equal(wolf.replace_display,nil,'explicit disable immediately restores actor')
equal(Options.tokensEnabled(),false,'disabled token option persists in memory')
game:checkerSetMode('refined')
equal(wolf.replace_display,nil,'refined terrain cannot turn tokens back on')
equal(map.cells[0],grass,'unsupported zone is never painted grass')
equal(game.checker_mode,'vanilla','effective terrain remains native outside verified zone')
equal(Options.terrainMode(),'refined','preferred terrain mode remains independent')
game.zone.short_name='trollmire'
game:checkerApplySettings()
equal(map.cells[0].replace_display.image,'checker-revised+refined/grass0.png','mode applies when entering supported zone')
equal(map.cells[5].replace_display.image,'checker-revised+refined/grass1.png','shared native prototype gets per-cell parity')
equal(grass.replace_display,nil,'shared native prototype remains untouched')
equal(map.cells[1].replace_display,nil,'unknown vault floor remains native')
equal(map.cells[4].replace_display,nil,'special stew grid remains native')
equal(map.cells[2].replace_display.image,'checker-revised+refined/deep0-0-0.png','verified deep water uses water art')
equal(map.cells[3].block_sight,true,'tree line of sight rules are unchanged')
equal(map.cells[3].does_block_move,true,'tree collision rules are unchanged')
local terrainBody=map.cells[0].replace_display
game:checkerSetTokensEnabled(true)
equal(map.cells[0].replace_display,terrainBody,'token switch does not recreate terrain')
equal(wolf._checker_token.id,'wolf','explicit token enable refreshes level actors')
body=wolf.replace_display
game:checkerSetMode('blockout')
equal(map.cells[0].replace_display.image,'checker-revised+grass0.png','blockout terrain remains available')
equal(wolf.replace_display,body,'blockout keeps actor ownership')
game:checkerSetMode('vanilla')
equal(map.cells[0].replace_display,nil,'vanilla restores only terrain')
equal(wolf.replace_display,body,'vanilla keeps actor ownership')
equal(map.cells[0]._checker_terrain,nil,'restored terrain relinquishes ownership')
-- F1: FLOODED Trollmire is now supported (CONTRACT.md Section 3.4/8). Gating
-- is by grid identity, not the zone's is_flooded flag, so grass keeps getting
-- painted, and BOGTREE/BOGWATER/BOGWATER_MISC/HARDTREE each get their own
-- distinct art through the same replace_display path used above.
game.zone.is_flooded=true
map.cells[1]=grid{name='tree',subtype='water',define_as='BOGTREE3',does_block_move=true,block_sight=true,image='bogtree.png'}
map.cells[2]=grid{name='bog water',subtype='water',image='bogwater.png'}
map.cells[3]=grid{name='bog water',subtype='water',add_displays={{image='terrain/misc_bog3.png'}},image='bogwater.png'}
map.cells[4]=grid{name='tall thick tree',subtype='grass',does_block_move=true,image='hardtree.png'}
game:checkerSetMode('refined')
equal(map.cells[0].replace_display.image,'checker-revised+refined/grass0.png','F1: flooded layout now paints already-recognised identities too')
equal(map.cells[1].replace_display.image,'checker-revised+refined/bog-tree-b2-1-0.png','F1: BOGTREE (define_as pattern) gets bog-tree art, not plain tree')
equal(map.cells[2].replace_display.image,'checker-revised+refined/bog8-0-0.png','F1: BOGWATER gets bog art and counts BOGTREE as the same water family')
equal(map.cells[3].replace_display.image,'checker-revised+refined/bog-misc2-1-0.png','F1: BOGWATER_MISC gets bog floor + misc variant, distinct from plain bog')
equal(map.cells[3].add_displays[1].image,'terrain/misc_bog3.png','F1: native misc add_displays layer stays on the grid; our replace_display owns the look, not a doubled draw')
equal(map.cells[4].replace_display.image,'checker-revised+refined/tree-hard0.png','F1: HARDTREE gets its own art, distinct from ordinary tree')
equal(wolf.replace_display,body,'flooded layout still uses verified creatures')
game.zone.is_flooded=nil
game:checkerApplySettings()

-- G0: Old Forest and Slazish Fens widen the same explicit zone whitelist
-- (docs/expansion-plan-20260928/TERRAIN-INVENTORY.md Sections 1/2), reusing
-- terrain() end to end through the real game:checkerApplySettings() path.
game.zone={short_name='old-forest'}
map.cells[0]=grid{name='grass',subtype='dark_grass',type='floor',define_as='GRASS',image='terrain/grass/dark_grass_main_01.png'}
map.cells[1]=grid{name='tree',subtype='dark_grass',does_block_move=true,block_sight=true,image='terrain/tree.png'}
map.cells[2]=grid{name='way to the lake of Nur',change_level=1,change_zone='lake-nur',image='terrain/grass/dark_grass_main_01.png'}
game:checkerApplySettings()
equal(map.cells[0].replace_display.image,'checker-revised+refined/grass0.png','Old Forest DEFAULT dark_grass GRASS is painted through the real settings path')
equal(map.cells[1].replace_display.image,'checker-revised+refined/tree-willow1.png','Old Forest DEFAULT dark_grass TREE is painted through the real settings path')
equal(map.cells[2].replace_display,nil,'Old Forest LAKE_NUR (no subtype) stays native through the real settings path')

game.zone={short_name='slazish-fen'}
map.cells[0]=grid{name='grass',subtype='grass',type='floor',define_as='GRASS',image='terrain/grass.png'}
map.cells[1]=grid{name='coral portal',subtype='water',does_block_move=true,image='terrain/poisoned_water_01.png'}
game:checkerApplySettings()
equal(map.cells[0].replace_display.image,'checker-revised+refined/grass0.png','Slazish Fens GRASS is painted through the real settings path')
equal(map.cells[1].replace_display,nil,'Slazish Fens PORTAL stays native through the real settings path')

-- The dark_grass alias must not leak into an unrelated zone that happens to
-- share the subtype string (Heart of the Gloom's own TREE).
game.zone={short_name='heart-gloom'}
map.cells[0]=grid{name='tree',subtype='dark_grass',does_block_move=true,block_sight=true,image='terrain/underground_tree.png'}
game:checkerApplySettings()
equal(map.cells[0].replace_display,nil,'Heart of the Gloom dark_grass TREE is not in the forest whitelist and stays native')
equal(game.checker_mode,'vanilla','unsupported zone reports vanilla effective mode even with refined preferred')

game.zone={short_name='trollmire'}
game:checkerApplySettings()
local external=Entity.new{image='external.png'}
map.cells[0].replace_display=external
wolf.replace_display=external
game:checkerSetTokensEnabled(false)
equal(wolf.replace_display,external,'token disable preserves external actor replacement')
equal(map.cells[0].replace_display,external,'terrain refresh preserves external terrain replacement')
game:checkerSetMode('vanilla')
equal(map.cells[0].replace_display,external,'terrain disable preserves external replacement')
equal(game.turn,19,'visual settings do not advance world time')
equal(player.life,83,'visual settings preserve player health')
equal(wolf.life,41,'visual settings preserve creature health')
equal(wolf.max_life,79,'visual settings preserve creature max health')
equal(env.config.settings.tome.unrelated,'keep','unrelated settings stay unchanged')
local beforeX,beforeY=player.x,player.y
local beforeBlock=map.cells[3].does_block_move
Options.setAuraStyle('moderate',game)
equal(Options.auraStyle(),'moderate','aura setting applies immediately')
equal(player.x,beforeX,'aura setting preserves player x')
equal(player.y,beforeY,'aura setting preserves player y')
equal(map.cells[3].does_block_move,beforeBlock,'aura setting preserves passability')
equal(pcall(function() Options.setAuraStyle('strong',game) end),false,'unshipped strong style rejected')
Options.setTokenFacing('native',game)
equal(Options.tokenFacing(),'native','native facing preference accepted')
equal(pcall(function() Options.setTokenFacing('bogus',game) end),false,'invalid facing rejected')
equal(map.redraws>0,true,'option changes immediately redraw the map')
local saved={tome={}}
for _,write in ipairs(writes) do
 equal(write[1]=='tome.checker_aura_style' or write[1]=='tome.checker_tokens_enabled' or write[1]=='tome.checker_terrain_mode' or write[1]=='tome.checker_token_facing' or write[1]=='tome.checker_player_tokens_enabled',true,'owned setting namespace')
 local chunk
 if setfenv then chunk=assert(loadstring(write[2]));setfenv(chunk,saved)
 else chunk=assert(_G.load(write[2],'settings','t',saved)) end
 chunk()
end
equal(saved.tome.checker_aura_style,'moderate','aura style serializes independently')
equal(saved.tome.checker_tokens_enabled,false,'token settings serialize independently')
equal(saved.tome.checker_terrain_mode,'vanilla','terrain setting serializes independently')
equal(saved.tome.checker_token_facing,'native','facing preference serializes independently')
equal(saved.tome.checker_player_tokens_enabled,true,'player token preference serializes independently')
equal(pcall(function() game:checkerSetMode('bogus') end),false,'invalid mode rejected')
equal(pcall(function() game:checkerSetTokensEnabled('yes') end),false,'nonboolean token switch rejected')

-- Exercise the real settings hook, including a boot/menu host without a map.
local hooks={}
env.class={bindHook=function(_,name,callback) hooks[name]=callback end}
env._t=function(value) return value end
modules['mod.class.CheckerTokenStyle']=load('overload/mod/class/CheckerTokenStyle.lua')
modules['engine.ui.Textzone']={new=function(def) return def end}
modules['mod.dialogs.CheckerRankColor']={new=function() error('mode switches must not open the RGB dialog') end}
load('hooks/load.lua')
equal(hooks['ToME:birthDone'],nil,'production has no birth hook')
local tab_title,generate
hooks['GameOptions:tabs'](nil,{tab=function(title,callback) tab_title,generate=title,callback end})
equal(tab_title,'Token colors','options no longer imply Board HUD ownership')
local dialog={c_desc={w=100,h=100},c_list={drawItem=function() end}}
generate(dialog)
equal(dialog.list[1].checker_tokens_enabled,true,'independent token row is available')
equal(dialog.list[2].checker_player_tokens_enabled,true,'independent player token row is available')
equal(dialog.list[3].checker_terrain_mode,true,'independent terrain row is available')
equal(dialog.list[4].checker_aura_style,true,'aura row is available')
equal(dialog.list[5].checker_token_facing,true,'facing row is available')
equal(dialog.list[2].status(),'Enabled','player token row shows default on')
local boot={saveSettings=game.saveSettings}
env.game=boot
dialog.list[1].fct(dialog.list[1]);dialog.list[3].fct(dialog.list[3])
dialog.list[4].fct(dialog.list[4]);dialog.list[5].fct(dialog.list[5])
dialog.list[2].fct(dialog.list[2])
equal(Options.playerTokensEnabled(),false,'boot/menu player row toggles without a running map')
equal(dialog.list[2].status(),'Disabled','player token row status follows the option')
dialog.list[2].fct(dialog.list[2])
equal(Options.playerTokensEnabled(),true,'player token row round trip')
equal(Options.auraStyle(),'subtle','boot/menu aura row toggles without a running map')
equal(Options.tokenFacing(),'fixed','boot/menu facing row toggles without a running map')
equal(Options.tokensEnabled(),true,'boot/menu can save token option without a running map')
equal(Options.terrainMode(),'blockout','boot/menu can save terrain option without a running map')

-- The fixture has no hard dependency on either production addon or a HUD.
modules['mod.class.CheckerFixture']=load('tests/fixture/tome-checker-fixture/overload/mod/class/CheckerFixture.lua')
local displayCalls=0
local Native={display=function() displayCalls=displayCalls+1;return 37 end}
env.loadPrevious=function() return Native end
local FixtureGame=load('tests/fixture/tome-checker-fixture/superload/mod/class/Game.lua')
local native=setmetatable({},{__index=FixtureGame})
equal(native:display(),37,'fixture delegates native display without token addon')
equal(native.checkerRefreshActor,nil,'fixture does not invent a production token dependency')
equal(pcall(function() native:checkerStage() end),false,'fixture mutators reject missing explicit enablement')
equal(displayCalls,1,'native display runs once')
env.config.settings.cheat=true;env.config.settings.disable_all_connectivity=true
env.__module_extra_info={checker_fixture=true,checker_demo=true}
equal(modules['mod.class.CheckerFixture'].enabled(),true,'fixture explicitly enabled offline')
local combined={display=Native.display}
for k,v in pairs(Game) do combined[k]=v end
env.loadPrevious=function() return combined end
load('tests/fixture/tome-checker-fixture/superload/mod/class/Game.lua')
local demo=setmetatable({level=game.level,player=player,checker_hero=player,party=party},{__index=combined})
equal(demo:checkerRefreshActor(player),nil,'installed fixture still defaults to native player')
env.__module_extra_info.checker_hero=true
equal(demo:checkerRefreshActor(player),'hero','explicit fixture hero mode installs demo art')
env.__module_extra_info.checker_hero=nil
equal(demo:checkerRefreshActor(player),nil,'leaving hero mode restores native player')
equal(player.replace_display,nil,'hero display ownership is correctly released')
PlayerTokens.available.halfling_male=true
env.__module_extra_info.checker_hero=true
equal(demo:checkerRefreshActor(player),'hero','fixture hero keeps priority over production player art')
env.__module_extra_info.checker_hero=nil
equal(demo:checkerRefreshActor(player),'player:halfling_male','production mapping resumes after hero mode')
PlayerTokens.available.halfling_male=nil
print(('runtime_modes: %d checks passed; independent options, scoped terrain, native players, settings UI and optional fixture'):format(checks))
