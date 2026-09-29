-- Pure production player-token checks. Run with Lua 5.1 or LuaJIT.
-- Loads the real CheckerPlayerTokens/CheckerOptions/Game/Actor superloads and
-- the fixture Game wrapper; only engine services are stubbed.
local script=debug.getinfo(1,'S').source:sub(2)
local root=(script:match('^(.*[/\\])') or './')..'../'
local checks=0
local function equal(actual,expected,label)
 checks=checks+1
 assert(actual==expected,label..': expected '..tostring(expected)..', got '..tostring(actual))
end
local env=setmetatable({config={settings={cheat=false,tome={}}},__module_extra_info={}},{__index=_G})
local function load(path)
 local chunk
 if setfenv then chunk=assert(loadfile(root..path));setfenv(chunk,env)
 else chunk=assert(loadfile(root..path,'t',env)) end
 return chunk()
end

-- Manifest gate: listed AND present on disk; empty/missing/invalid = native.
local manifestPath='/data-checker-revised/player-token-manifest.lua'
local files,manifest={},nil
env.fs={exists=function(path) return files[path]==true end}
env.loadfile=function(path)
 if path==manifestPath then return function() return manifest end end
 return loadfile(path)
end
local P=load('overload/mod/class/CheckerPlayerTokens.lua')
equal(next(P.available),nil,'missing manifest keeps every family native')
equal(#P.families,14,'14 base-game body families')
files[manifestPath]=true
manifest={revision='empty',families={}}
P=load('overload/mod/class/CheckerPlayerTokens.lua')
equal(next(P.available),nil,'shipped empty manifest keeps every family native')
manifest={revision='r1',families={human_male=true,elf_female=true,orc_male=true,dwarf_male='yes'}}
files[P.imageFile('human_male')]=true
files['/data-checker-revised/gfx/tokens/player-orc_male.png']=true
files[P.imageFile('dwarf_male')]=true
P=load('overload/mod/class/CheckerPlayerTokens.lua')
equal(P.available.human_male,true,'listed family with runtime export is available')
equal(P.available.elf_female,nil,'listed family without runtime PNG stays native')
equal(P.available.orc_male,nil,'unknown (DLC) family is ignored')
equal(P.available.dwarf_male,nil,'non-boolean approval is ignored')
manifest={families={human_male=true}}
P=load('overload/mod/class/CheckerPlayerTokens.lua')
equal(next(P.available),nil,'manifest without revision is invalid')
manifest=function() error('broken') end
env.loadfile=function(path) if path==manifestPath then return function() error('broken') end end end
P=load('overload/mod/class/CheckerPlayerTokens.lua')
equal(next(P.available),nil,'throwing manifest is invalid')
env.fs,env.loadfile=nil,nil
local all=load('overload/mod/class/CheckerPlayerTokens.lua')
equal(P.image('player:human_male'),'checker-revised+tokens/player-human_male.png','runtime image path convention')
equal(pcall(P.image,'player:orc_male'),false,'unknown family image rejected')

-- Explicit subrace x sex table against native descriptors.
local expected={
 {'Higher','Male','human_male'},{'Higher','Female','human_female'},
 {'Cornac','Male','human_male'},{'Cornac','Female','human_female'},
 {'Shalore','Male','elf_male'},{'Shalore','Female','elf_female'},
 {'Thalore','Male','elf_male'},{'Thalore','Female','elf_female'},
 {'Dwarf','Male','dwarf_male'},{'Dwarf','Female','dwarf_female'},
 {'Halfling','Male','halfling_male'},{'Halfling','Female','halfling_female'},
 {'Ogre','Male','ogre_male'},{'Ogre','Female','ogre_female'},
 {'Yeek','Male','yeek'},{'Yeek','Female','yeek'},
 {'Ghoul','Male','ghoul'},{'Skeleton','Male','skeleton'},{'Runic Golem','Male','runic_golem'},
}
local function hero(subrace,sex,extra)
 local a={descriptor={subrace=subrace,sex=sex,subclass='Berserker'},moddable_tile=all.moddable[subrace] or 'human_#sex#',
  name='Anyname',image='player/human_male/base_shadow_01.png',add_mos={{image='doll.png'}}}
 if sex=='Male' then a.male=true else a.female=true end
 for k,v in pairs(extra or {}) do a[k]=v end
 return a
end
for _,family in ipairs(all.families) do all.available[family]=true end
local families_seen={}
for _,row in ipairs(expected) do
 equal(all.family(hero(row[1],row[2])),row[3],'family '..row[1]..'/'..row[2])
 families_seen[row[3]]=true
 equal(all.identify(hero(row[1],row[2]),nil,{main=true}),'player:'..row[3],'identity '..row[1]..'/'..row[2])
end
local n=0;for _ in pairs(families_seen) do n=n+1 end
equal(n,14,'every family is reachable from a native key')
local nkeys=0;for _ in pairs(all.keys) do nkeys=nkeys+1 end
equal(nkeys,#expected,'no extra keys beyond verified native descriptors')
local function reason(a,opts) local _,r=all.explain(a,nil,opts or {main=true});return r end
equal(reason(hero('Lich','Male',{moddable_tile='skeleton'})),'unmapped-key','Lich stays native')
equal(reason(hero('Doomelf','Female',{moddable_tile='elf_#sex#'})),'unmapped-key','DLC subrace stays native')
equal(reason(hero('Ghoul','Female',{moddable_tile='ghoul'})),'unmapped-key','sex a descriptor disallows stays native')
equal(reason(hero('Cornac','Male',{female=true})),'sex-mismatch','descriptor/boolean sex mismatch')
local swapped=hero('Cornac','Female');swapped.female=nil;swapped.male=true
equal(reason(swapped),'sex-mismatch','female key with male body')
equal(reason(hero('Cornac','Male',{has_custom_tile='donator.png'})),'custom-tile','custom tile stays native')
local cleared=hero('Cornac','Male');cleared.moddable_tile=nil
equal(reason(cleared),'moddable-tile','cleared moddable tile stays native')
equal(reason(hero('Cornac','Male',{moddable_tile='elf_#sex#'})),'moddable-tile','altered moddable tile stays native')
equal(reason(hero('Cornac','Male',{descriptor={subrace='Cornac'}})),'no-descriptor','incomplete descriptor')
equal(reason(hero('Cornac','Male'),{}),'not-main','non-main member stays native')
equal(reason(hero('Cornac','Male'),{main=true,no_moddable=true}),'no-moddable-tiles','ASCII / no moddable tiles stays native')
equal(reason(hero('Cornac','Male',{replace_display={image='tree.png'}})),'external-display','foreign replace_display wins')
for field,value in pairs{shader='x',anim={},add_displays={{}},textures={{}}} do
 equal(all.identify(hero('Cornac','Male',{[field]=value}),nil,{main=true}),nil,'unsupported display field '..field)
end
equal(all.identify(hero('Cornac','Male',{shader_auras={},add_displays={}}),nil,{main=true}),'player:human_male','empty tables are not effects')
-- A native shader aura wraps whatever image is on the display; keep the token.
equal(all.identify(hero('Cornac','Male',{shader_auras={a={}}}),nil,{main=true}),'player:human_male','active shader aura keeps player token')
local owned={image='mine'}
equal(all.identify(hero('Cornac','Male',{replace_display=owned}),owned,{main=true}),'player:human_male','own display is reclaimed')
all.available.elf_female=nil
equal(reason(hero('Shalore','Female')),'no-art','family without reviewed art stays native')

-- Game integration with the real Game/Actor superloads.
local modules={}
local rebuilds=0
local Entity={new=function(def) def.removeAllMOs=function() end;return def end}
local Map={TERRAIN=1,ACTOR=2,tiles={}}
modules['engine.Map']=Map;modules['engine.Entity']=Entity
modules['mod.class.CheckerTokens']=load('overload/mod/class/CheckerTokens.lua')
modules['mod.class.CheckerOptions']=load('overload/mod/class/CheckerOptions.lua')
modules['mod.class.CheckerPlayerTokens']=all
modules['mod.class.CheckerTokenStyle']=load('overload/mod/class/CheckerTokenStyle.lua')
env.require=function(name) return assert(modules[name],'unexpected module '..name) end
env.loadPrevious=function() return {} end
modules['mod.class.CheckerTerrain']=load('overload/mod/class/CheckerTerrain.lua')
local Game=load('superload/mod/class/Game.lua')
local ActorBase={cloned=function() end,updateModdableTile=function(self) rebuilds=rebuilds+1;self.rebuilt=(self.rebuilt or 0)+1 end}
env.loadPrevious=function() return ActorBase end
local Actor=load('superload/mod/class/Actor.lua')
local Options=modules['mod.class.CheckerOptions']
local writes={}
local main=setmetatable(hero('Cornac','Male',{x=1,y=1}),{__index=Actor})
local golem=setmetatable(hero('Cornac','Male',{x=2,y=1,ai='party'}),{__index=Actor})
local map=setmetatable({w=3,h=3,updateMap=function() end,redisplay=function() end},{__call=function() return nil end})
local ticks={}
local game=setmetatable({level={map=map,entities={main,golem}},zone={short_name='derth'},player=main,
 party={findMember=function(_,f) assert(f.main) return main end,hasMember=function() return true end},
 saveSettings=function(_,key,value) writes[#writes+1]={key,value} end},{__index=Game})
env.game=game
function main:removeAllMOs() end
function golem:removeAllMOs() end

equal(Options.playerTokensEnabled(),true,'player token option defaults on')
equal(game:checkerRefreshActor(main),'player:human_male','main hero uses body-family token')
equal(main.replace_display.image,'checker-revised+tokens/player-human_male.png','token display image')
equal(main._checker_token.id,'player:human_male','namespaced ownership id')
local body=main.replace_display
main.descriptor.subclass='Archmage'
equal(game:checkerRefreshActor(main),'player:human_male','class change keeps the neutral token')
equal(main.replace_display,body,'unchanged token is reused')
equal(game:checkerRefreshActor(golem),nil,'controlled non-main party member stays native')
game.player=golem
equal(game:checkerRefreshActor(main),'player:human_male','main hero keeps token while another member is controlled')
game.player=main
equal(rebuilds,0,'no paper-doll rebuild while the token is shown')

-- Equipment change: native updateModdableTile under our token keeps the token.
main:updateModdableTile()
equal(main.replace_display,body,'equipment rebuild keeps token')
equal(rebuilds,1,'native updateModdableTile still runs once')

-- Toggle round trip: removal rebuilds the doll exactly once, no recursion.
rebuilds=0
game:checkerSetPlayerTokensEnabled(false)
equal(main.replace_display,nil,'disable restores native display')
equal(main._checker_token,nil,'disable releases ownership')
equal(rebuilds,1,'removal calls updateModdableTile exactly once')
equal(main._checker_player_rebuild,nil,'rebuild marker consumed')
equal(Options.playerTokensEnabled(),false,'disabled player option in memory')
equal(game:checkerRefreshActor(main),nil,'disabled option stays native')
equal(rebuilds,1,'native refresh does not rebuild again')
game:checkerSetPlayerTokensEnabled(true)
equal(main._checker_token.id,'player:human_male','re-enable reinstalls immediately')
local saved={tome={}}
for _,w in ipairs(writes) do
 equal(w[1],'tome.checker_player_tokens_enabled','player option uses its own key')
 local chunk
 if setfenv then chunk=assert(loadstring(w[2]));setfenv(chunk,saved) else chunk=assert(_G.load(w[2],'s','t',saved)) end
 chunk()
end
equal(saved.tome.checker_player_tokens_enabled,true,'player option serializes')
equal(saved.tome.checker_tokens_enabled,nil,'creature option untouched')
equal(pcall(Options.setPlayerTokensEnabled,'yes'),false,'nonboolean player option rejected')

-- Creature token switch also gates player tokens.
rebuilds=0
game:checkerSetTokensEnabled(false)
equal(main.replace_display,nil,'creature switch off removes player token')
equal(rebuilds,1,'creature switch removal rebuilds doll')
equal(Options.playerTokensEnabled(),true,'player preference kept while creature tokens are off')
game:checkerSetTokensEnabled(true)
equal(main._checker_token.id,'player:human_male','both switches on restores token')

-- Shader aura added: native addShaderAura calls updateModdableTile itself.
-- The token is kept (the 'update' context never acts) and the native call
-- that follows rebuilds the aura onto our display's own image.
rebuilds=0
local aura_body=main.replace_display
main.shader_auras={aura={}}
main:updateModdableTile()
equal(main.replace_display,aura_body,'shader aura keeps the token')
equal(main._checker_token.id,'player:human_male','ownership retained with an active aura')
equal(rebuilds,1,'native updateModdableTile still runs once to build the aura on the token')
-- A plain refresh with the same token/aura state touches nothing further.
equal(game:checkerRefreshActor(main,'display'),'player:human_male','unchanged aura state keeps the token')
equal(main.replace_display,aura_body,'no duplicate Entity while the aura persists')
equal(rebuilds,1,'no extra rebuild from a plain refresh')
main.shader_auras={}
main:updateModdableTile()
equal(main.replace_display,aura_body,'clearing the aura keeps the token')
equal(rebuilds,2,'native updateModdableTile runs once more to remove the aura mo entries')

-- A pre-existing aura when the token is (re)installed after being off: the
-- install rebuilds it onto the fresh token instead of leaving it stranded.
game:checkerSetPlayerTokensEnabled(false)
main.shader_auras={aura={}}
rebuilds=0
game:checkerSetPlayerTokensEnabled(true)
equal(main._checker_token.id,'player:human_male','token installs despite a pre-existing aura')
equal(rebuilds,1,'install with a pre-existing aura rebuilds it onto the token')
main.shader_auras=nil
rebuilds=0

-- Foreign replace_display (shapeshift): yield, then reinstall afterwards.
rebuilds=0
local tree={image='invis.png'}
main.replace_display=tree
equal(game:checkerRefreshActor(main,'display'),nil,'shapeshift display is never overwritten')
equal(main.replace_display,tree,'foreign display preserved')
equal(main._checker_token,nil,'ownership released to the effect')
equal(rebuilds,0,'no rebuild under a foreign display')
main.replace_display=nil -- native deactivate, then updateMap -> getMapObjects
equal(game:checkerRefreshActor(main,'display'),'player:human_male','token returns when the effect ends')
equal(main._checker_player_rebuild,nil,'reinstall clears stale-doll marker')
-- Effect ends while the player option is off: deferred native rebuild.
main.replace_display=tree
game:checkerRefreshActor(main,'display')
env.config.settings.tome.checker_player_tokens_enabled=false
main.replace_display=nil
game.onTickEnd=function(_,f) ticks[#ticks+1]=f end
equal(game:checkerRefreshActor(main,'display'),nil,'effect end with option off stays native')
equal(rebuilds,0,'display-context rebuild is deferred, never nested in updateMap')
equal(#ticks,1,'one deferred rebuild queued')
game:checkerRefreshActor(main,'display')
equal(#ticks,1,'rebuild is not queued twice')
ticks[1]()
equal(rebuilds,1,'deferred rebuild runs updateModdableTile once')
env.config.settings.tome.checker_player_tokens_enabled=nil
game.onTickEnd=nil;ticks={}
game:checkerRefreshActor(main)

-- Display-context removal (e.g. an effect adds a shader) is deferred too.
rebuilds=0
game.onTickEnd=function(_,f) ticks[#ticks+1]=f end
main.shader='shadow'
equal(game:checkerRefreshActor(main,'display'),nil,'shader drops token')
equal(rebuilds,0,'rebuild not nested in getMapObjects')
ticks[1]()
equal(rebuilds,1,'deferred rebuild after display-context removal')
main.shader=nil;game.onTickEnd=nil;ticks={}

-- ASCII / no moddable tiles.
Map.tiles.no_moddable_tiles=true
equal(game:checkerRefreshActor(main),nil,'ASCII mode keeps native')
Map.tiles.no_moddable_tiles=nil
equal(game:checkerRefreshActor(main),'player:human_male','tiles mode restores token')

-- Clones (mirror images, save copies) never inherit the token and rebuild.
local clone=setmetatable({},{__index=Actor})
for k,v in pairs(main) do clone[k]=v end
clone:cloned(main)
equal(clone._checker_token,nil,'clone drops copied ownership')
equal(clone.replace_display,nil,'clone restores native display field')
equal(clone._checker_player_rebuild,true,'clone marks copied doll stale')
clone.rebuilt=0
equal(game:checkerRefreshActor(clone),nil,'clone is not the main hero')
equal(clone.rebuilt,1,'clone rebuilds its paper doll')

-- Fixture hero precedence and scope.
env.config.settings.cheat=true;env.config.settings.disable_all_connectivity=true
env.__module_extra_info={checker_fixture=true}
modules['mod.class.CheckerFixture']=load('tests/fixture/tome-checker-fixture/overload/mod/class/CheckerFixture.lua')
local combined={display=function() end}
for k,v in pairs(Game) do combined[k]=v end
env.loadPrevious=function() return combined end
load('tests/fixture/tome-checker-fixture/superload/mod/class/Game.lua')
local fixture=setmetatable({level=game.level,player=main,checker_hero=main,party=game.party,saveSettings=game.saveSettings},{__index=combined})
env.game=fixture
equal(fixture:checkerRefreshActor(main),'player:human_male','fixture without --hero-token uses production mapping')
env.__module_extra_info.checker_hero=true
equal(fixture:checkerRefreshActor(main),'hero','fixture --hero-token takes precedence')
equal(main.replace_display.image,'checker-revised+hero.png','demo hero art installed')
equal(fixture:checkerRefreshActor(main,'display'),'hero','context is forwarded, hero kept')
env.__module_extra_info.checker_hero=nil
equal(fixture:checkerRefreshActor(main),'player:human_male','leaving hero mode returns to production mapping')
env.config.settings.cheat=false
env.__module_extra_info.checker_hero=true
equal(fixture:checkerRefreshActor(main),'player:human_male','demo hero requires the enabled offline fixture')
print(('player_tokens: %d checks passed; body-family keys, manifest gate, main-only, fallbacks, toggle round trip, doll rebuild and fixture hero precedence'):format(checks))
