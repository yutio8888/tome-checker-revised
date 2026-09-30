-- Run from any cwd with Lua 5.1/LuaJIT. Executes the native basic.lua definitions.
local root=(debug.getinfo(1,'S').source:sub(2):match('^(.*[/\\])') or './')..'../'
local n=0
local function eq(a,b,label) n=n+1;assert(a==b,label..': '..tostring(a)..' ~= '..tostring(b)) end
local function copy(t)
 if type(t)~='table' then return t end
 local out={};for k,v in pairs(t) do out[k]=copy(v) end;return out
end
local Entity={}
function Entity.new(t)
 t.removeAllMOs=function() end
 t.getMapObjects=function(self,tiles,mos,z) self._mo=self.image;mos[z]=self.image end
 return t
end
local mode='refined'
local auraStyle='subtle'
local modules={['engine.Entity']=Entity,['mod.class.CheckerOptions']={terrainMode=function() return mode end,auraStyle=function() return auraStyle end}}
local env=setmetatable({require=function(name) return assert(modules[name],name) end},{__index=_G})
local function load(path,e)
 local chunk=assert(loadfile(path));setfenv(chunk,e or env);return chunk()
end
local T=load(root..'overload/mod/class/CheckerTerrain.lua');modules['mod.class.CheckerTerrain']=T
local grids={}
local native=setmetatable({class=Entity,colors=setmetatable({},{__index=function() return {} end}),_t=function(v) return v end},{__index=_G})
native.newEntity=function(t)
 local g=t.base and copy(assert(grids[t.base])) or {}
 for k,v in pairs(t) do g[k]=v end
 -- Entity methods live on its class, not the definition instance.
 g.removeAllMOs=nil;g.getMapObjects=nil
 -- engine.Entity:init normalizes absent tint channels to multiplicative 1.
 g.tint_r=g.tint_r or 1;g.tint_g=g.tint_g or 1;g.tint_b=g.tint_b or 1
 grids[t.define_as]=g
end
load(root..'../../modules/tome/data/general/grids/basic.lua',native)
for _,g in pairs(grids) do T.markSource(g,'/data/general/grids/basic.lua') end
for _,id in ipairs{'WALL','WALL_NORTH1','WALL_PILLAR_85','WALL_SOUTH17','HARDWALL_SMALL_PILLAR'} do
 eq(T.classify(grids[id]),id:match('^HARD') and 'hardwall' or 'wall','native nice tile '..id)
end
for _,id in ipairs{'DOOR','DOOR_HORIZ','DOOR_VERT'} do eq(T.classify(grids[id]),'door-closed',id) end
for _,id in ipairs{'DOOR_OPEN','DOOR_HORIZ_OPEN','DOOR_OPEN_VERT'} do eq(T.classify(grids[id]),'door-open',id) end
eq(T.classify(grids.FLOOR),'floor','native floor')
for _,id in ipairs{'GENERIC_LEVER_DOOR','GENERIC_LEVER_DOOR_HORIZ','GENERIC_LEVER','GLASSWALL','GLASSDOOR'} do eq(T.classify(grids[id]),nil,'unsupported '..id) end
-- S2/T8: FLAT_* map-edge exits are exact stairs by direction (flipped from native).
for id,kind in pairs{FLAT_UP_WILDERNESS='stairs-world',FLAT_UP8='stairs-up',FLAT_UP2='stairs-up',FLAT_UP4='stairs-up',FLAT_UP6='stairs-up',
 FLAT_DOWN8='stairs-down',FLAT_DOWN2='stairs-down',FLAT_DOWN4='stairs-down',FLAT_DOWN6='stairs-down'} do
 eq(T.classify(grids[id]),kind,'S2 flat exit '..id)
end
-- S2/T4: sealed vault doors are the board closed door (flipped from native).
eq(T.classify(grids.DOOR_VAULT),'door-closed','S2 sealed door DOOR_VAULT')
eq(select(2,T.classify(grids.DOOR_VAULT_HORIZ)),'horizontal','S2 sealed door horizontal')
eq(select(2,T.classify(grids.DOOR_VAULT_VERT)),'vertical','S2 sealed door vertical')
for _,id in ipairs{'DOOR_VAULT','DOOR_VAULT_HORIZ','DOOR_VAULT_VERT'} do
 for label,mutation in pairs{
  unstamped=function(g) g._checker_grid_source=nil end,
  prompt=function(g) g.door_player_check='Another prompt.' end,
  noprompt=function(g) g.door_player_check=nil end,
  promptfn=function(g) g.door_player_check=function() return true end end,
  sense=function(g) g.block_sense=nil end, esp=function(g) g.block_esp=nil end,
  sight=function(g) g.block_sight=nil end, move=function(g) g.does_block_move=true end,
  opened=function(g) g.door_opened='DOOR' end, dig=function(g) g.dig='FLOOR' end,
  notice=function(g) g.notice=nil end, remember=function(g) g.always_remember=nil end,
  name=function(g) g.name='door' end, image=function(g) g.image='terrain/granite_wall1.png' end,
  stop=function(g) g.door_player_stop='Stop.' end, level=function(g) g.change_level=1 end,
  lever=function(g) g.on_lever_change=function() end end,
 } do
  local changed=copy(grids[id]);mutation(changed)
  eq(T.classify(changed),nil,'S2 altered sealed door '..id..' '..label)
 end
end
local plainPrompt=copy(grids.DOOR);plainPrompt.door_player_check='This door seems to have been sealed off. You think you can open it.'
eq(T.classify(plainPrompt),nil,'S2 a prompt on a plain door stays native')
for _,id in ipairs{'FLAT_UP_WILDERNESS','FLAT_UP4','FLAT_DOWN6'} do
 for label,mutation in pairs{
  unstamped=function(g) g._checker_grid_source=nil end, level=function(g) g.change_level=g.change_level+1 end,
  zone=function(g) g.change_zone='other-zone' end, check=function(g) g.change_level_check=function() end end,
  arrow=function(g) g.add_mos[1].image='terrain/way_next_2.png' end, extra=function(g) g.add_mos[2]={image='terrain/worldmap.png'} end,
  layer=function(g) g.add_displays={{image='terrain/signpost.png'}} end, notice=function(g) g.notice=nil end,
  remember=function(g) g.always_remember=nil end, move=function(g) g.does_block_move=true end,
  image=function(g) g.image='terrain/oldstone_floor.png' end, stand=function(g) g.on_stand=function() end end,
 } do
  local changed=copy(grids[id]);mutation(changed)
  eq(T.classify(changed),nil,'S2 altered flat exit '..id..' '..label)
 end
end
eq(T.classify(grids.OLD_FLOOR),'floor','exact old floor reuse')
for _,id in ipairs{'OLD_WALL','OLD_WALL_NORTH1','OLD_WALL_SOUTH3','OLD_WALL_PILLAR_85'} do eq(T.classify(grids[id]),'old-wall','old lichen wall '..id) end
local changedOld=copy(grids.OLD_WALL);changedOld.dig='OLD_FLOOR';eq(T.classify(changedOld),nil,'diggable old wall stays native')
local crack={define_as='CRACKS',type='wall',subtype='cracks',image='terrain/cracks/ground_9_01.png',pass_projectile=true,block_move=function() return true end}
T.markSource(crack,'/data/zones/maze/grids.lua')
eq(T.classify(crack),'cracks','exact Maze crack callback')
local tiledCrack=copy(crack);tiledCrack.block_move=crack.block_move;tiledCrack.add_displays={{image='invis.png'}}
eq(T.classify(tiledCrack),'cracks','NicerTiles crack invisible border holder')
local changedCrack=copy(tiledCrack);changedCrack.block_move=function() return true end
eq(T.classify(changedCrack),nil,'foreign crack interaction stays native')
changedCrack=copy(tiledCrack);changedCrack.add_displays={{image='foreign.png'}}
eq(T.classify(changedCrack),nil,'foreign crack art stays native')
eq(T.classify({define_as='CRACKS',type='wall',subtype='cracks',image='terrain/cracks/ground_9_01.png',pass_projectile=true,block_move=crack.block_move}),nil,'unstamped crack stays native')
for id,kind in pairs{UP='stairs-up',DOWN='stairs-down',UP_WILDERNESS='stairs-world'} do
 eq(T.classify(grids[id]),kind,'native exact stair '..id)
 local changed=copy(grids[id]);changed._checker_grid_source=nil
 eq(T.classify(changed),nil,'stairs require source '..id)
 for _,mutation in ipairs{
  function(g) g.change_level=4 end,
  function(g) g.change_zone='other-zone' end,
  function(g) g.change_level_abs=true end,
  function(g) g.change_level_check=function() return true end end,
  function(g) g.change_level_shift_back=true end,
  function(g) g.change_level_auto_stairs='UP' end,
  function(g) g.change_zone_auto_stairs='UP' end,
  function(g) g.force_down=true end,
  function(g) g.keep_old_lev=true end,
  function(g) g.notice=false end,
  function(g) g.always_remember=false end,
  function(g) g.add_mos[1].image='foreign.png' end,
  function(g) g.add_mos[1].display_y=-1 end,
  function(g) g.add_mos[2]={image='foreign.png'} end,
  function(g) g.add_displays={{image='foreign.png'}} end,
  function(g) g.on_stand=function() end end,
  function(g) g.shader='foreign' end,
 } do
  changed=copy(grids[id]);mutation(changed)
  eq(T.classify(changed),nil,'post-import changed stair '..id)
  T.markSource(changed,'/data/general/grids/basic.lua')
  eq(T.classify(changed),nil,'changed source definition cannot widen stair contract '..id)
 end
end
local fake=copy(grids.WALL);fake._checker_grid_source=nil
eq(T.classify(fake),nil,'same name and art has no provenance')
fake=copy(grids.WALL);fake.block_esp=true
eq(T.classify(fake),nil,'changed final semantics')
fake=copy(grids.WALL);fake.tint_r=0.5
eq(T.classify(fake),nil,'nonidentity native tint remains unsupported')
fake=copy(grids.DOOR);fake.on_stand=function() end
eq(T.classify(fake),nil,'custom interaction')
eq(T.variant({short_name='ruins-kor-pul'}),'DEFAULT','default layout')
eq(T.variant({short_name='ruins-kor-pul',is_hideout=true}),'HIDEOUT','hideout layout')
eq(T.variant({short_name='dreadfell'}),'DREADFELL','Dreadfell stone adapter')
eq(T.variant({short_name='dreadfell',is_hideout=true}),'DREADFELL','Dreadfell has no layout override')
for zone,variant in pairs{
 ['thieves-tunnels']='THIEVES', ['halfling-ruins']='HALFLING',
 reknor='REKNOR', ['reknor-escape']='REKNOR_ESCAPE',
 ['ruined-dungeon']='RUINED_DUNGEON', ['blighted-ruins']='BLIGHTED_RUINS',
 ['crypt-kryl-feijan']='KRYL_FEIJAN',
} do eq(T.variant({short_name=zone}),variant,zone..' exact basic source gate') end
for _,zone in ipairs{'ardhungol','other-tunnels','other-ruins','other-peak'} do
 eq(T.variant({short_name=zone}),nil,zone..' cannot borrow stone gate')
end
eq(T.variant({short_name='maze'}),'DEFAULT','maze default')
eq(T.variant({short_name='maze',is_collapsed=true}),'COLLAPSED','maze collapsed')
local crystalSource='/data/general/grids/crystal.lua'
local function crystal(id,kind)
 local g={define_as=id,subtype='underground',image='terrain/crystal_floor1.png'}
 if kind=='floor' then g.type='floor';g.name='floor'
 elseif kind=='wall' then
  g.type='wall';g.name='crystals';g.does_block_move=true;g.block_sight=true
  g.always_remember=true;g.dig='CRYSTAL_FLOOR';g.can_pass={pass_wall=1}
  g.add_displays={{image='terrain/crystal_alpha1.png',z=16}}
 else
  local up=kind=='ladder-up';local world=kind=='ladder-world'
  g.type='floor';g.name=world and 'ladder to worldmap' or up and 'ladder to the previous level' or 'ladder to the next level'
  g.change_level=up and -1 or 1;g.change_zone=world and 'wilderness' or nil
  g.notice=true;g.always_remember=not world
  g.add_displays={{image=(up or world) and 'terrain/crystal_ladder_up.png' or 'terrain/crystal_ladder_down.png'}}
 end
 T.markSource(g,crystalSource)
 return g
end
for _,pair in ipairs{{'CRYSTAL_FLOOR1','floor'},{'CRYSTAL_FLOOR8','floor'},
 {'CRYSTAL_WALL','wall'},{'CRYSTAL_WALL20','wall'},
 {'CRYSTAL_LADDER_UP','ladder-up'},{'CRYSTAL_LADDER_DOWN','ladder-down'},
 {'CRYSTAL_LADDER_UP_WILDERNESS','ladder-world'}} do
 local g=crystal(pair[1],pair[2]);eq(T.crystalTerrain(g),pair[2],pair[1])
 local changed=copy(g);changed._checker_crystal_source=nil
 eq(T.crystalTerrain(changed),nil,'crystal source required')
 changed=copy(g);changed.subtype='creep'
 eq(T.crystalTerrain(changed),nil,'crystal exact subtype')
end
local crystalWall=crystal('CRYSTAL_WALL2','wall')
crystalWall.add_displays[1].image='foreign.png'
eq(T.crystalTerrain(crystalWall),nil,'foreign crystal overlay remains native')
local crystalFloor=crystal('CRYSTAL_FLOOR2','floor')
crystalFloor.on_stand=function() end
eq(T.crystalTerrain(crystalFloor),nil,'modified crystal floor remains native')
native.class.makeCrystals=function() return {{image='terrain/crystal_alpha1.png',z=16}} end
load(root..'../../modules/tome/data/general/grids/crystal.lua',native)
for id,g in pairs(grids) do
 if type(id)=='string' and id:match('^CRYSTAL_') then T.markSource(g,crystalSource) end
end
for i=1,20 do
 local id='CRYSTAL_WALL'..(i>1 and i or '')
 eq(T.crystalTerrain(grids[id]),'wall','native crystal wall '..id)
end
for i=1,8 do eq(T.crystalTerrain(grids['CRYSTAL_FLOOR'..i]),'floor','native crystal floor '..i) end
local gloomySource='/data/general/grids/underground_gloomy.lua'
local dreamySource='/data/general/grids/underground_dreamy.lua'
local zoneSource='/data/zones/heart-gloom/grids.lua'
local function gloom(id,skin,source)
 local g={define_as=id,type='floor',subtype='underground',name='floor',
  image=skin=='gloomy' and 'terrain/mushrooms/gloomy_underground_floor.png' or 'terrain/underground_floor.png'}
 T.markSource(g,source or (skin=='gloomy' and gloomySource or dreamySource))
 return g
end
for _,skin in ipairs{'gloomy','dreamy'} do
 local src=skin=='gloomy' and gloomySource or dreamySource
 local floor=gloom('UNDERGROUND_FLOOR1',skin,src)
 eq(T.gloomTerrain(floor,skin),'gloom-floor',skin..' floor')
 T.markSource(floor,zoneSource)
 eq(T.gloomTerrain(floor,skin),'gloom-floor','outer zone load preserves underground source stamp')
 eq(T.gloomTerrain(floor,skin=='gloomy' and 'dreamy' or 'gloomy'),nil,'skin cannot cross')
 local creep=gloom('UNDERGROUND_CREEP3',skin,src)
 creep.name='mushroom creep';creep.subtype='creep'
 creep.image='terrain/mushrooms/creep_'..skin..'_mushrooms_main_03.png'
 eq(T.gloomTerrain(creep,skin),'gloom-creep',skin..' creep')
 local wall=gloom('UNDERGROUND_TREE17',skin,src)
 wall.type='wall';wall.name='underground thick vegetation';wall.does_block_move=true
 wall.block_sight=true;wall.can_pass={pass_tree=1};wall.dig='UNDERGROUND_FLOOR'
 eq(T.gloomTerrain(wall,skin),'gloom-wall',skin..' vegetation')
 local changed=copy(wall);changed.dig=nil
 eq(T.gloomTerrain(changed,skin),nil,'undiggable variant remains native')
 changed=copy(wall);changed.block_sight=nil
 eq(T.gloomTerrain(changed,skin),nil,'sight-changing variant remains native')
 changed=copy(wall);changed.special=true
 eq(T.gloomTerrain(changed,skin),nil,'vault-special vegetation remains native')
 local ladder=gloom('UNDERGROUND_LADDER_DOWN',skin,src)
 ladder.add_displays={{image='terrain/ladder_down.png'}};ladder.change_level=1;ladder.notice=true;ladder.always_remember=true
 eq(T.gloomTerrain(ladder,skin),'ladder-down',skin..' down ladder')
 changed=copy(ladder);changed.change_level=2
 eq(T.gloomTerrain(changed,skin),nil,'changed destination remains native')
 local up=gloom('UNDERGROUND_LADDER_UP',skin,src)
 up.add_displays={{image='terrain/ladder_up.png'}};up.change_level=-1;up.notice=true;up.always_remember=true
 eq(T.gloomTerrain(up,skin),'ladder-up',skin..' up ladder')
 local world=gloom('UNDERGROUND_LADDER_UP_WILDERNESS',skin,src)
 world.add_displays={{image='terrain/ladder_up_wild.png'}};world.change_level=1;world.change_zone='wilderness';world.notice=true
 eq(T.gloomTerrain(world,skin),'ladder-world',skin..' world ladder')
end
local plainFloor=gloom('UNDERGROUND_FLOOR1','gloomy',gloomySource)
eq(T.gloomTerrain(plainFloor,'plain'),'gloom-floor','Deep Bellow exact native floor in plain skin')
local plainChanged=copy(plainFloor);plainChanged.image='terrain/underground_floor.png'
eq(T.gloomTerrain(plainChanged,'plain'),nil,'plain skin rejects dreamy native floor')
local zoneTree=gloom('TREE7','gloomy',zoneSource)
zoneTree.type='wall';zoneTree.subtype='dark_grass';zoneTree.name='tree'
zoneTree.does_block_move=true;zoneTree.block_sight=true
zoneTree.can_pass={pass_tree=1};zoneTree.dig='UNDERGROUND_FLOOR'
eq(T.gloomTerrain(zoneTree,'gloomy'),'gloom-wall','zone TREE is local vegetation wall')
local dreamyZoneTree=copy(zoneTree);dreamyZoneTree.image='terrain/underground_floor.png'
eq(T.gloomTerrain(dreamyZoneTree,'dreamy'),'gloom-wall','zone TREE shares local wall family')
eq(T.gloomTerrain(copy(zoneTree),'gloomy'),'gloom-wall','cloned zone TREE retains provenance')
zoneTree._checker_gloom_source=nil
eq(T.gloomTerrain(zoneTree,'gloomy'),nil,'unstamped dark_grass not accepted')
local vault=gloom('UNDERGROUND_VAULT','gloomy',gloomySource)
vault.type='wall';vault.name='huge loose rock';vault.is_door=true
eq(T.gloomTerrain(vault,'gloomy'),nil,'gloom vault rock stays native')
eq(T.ready(),false,'no placeholder assets')
local manifest={ready=true,revision='test-reviewed-export',files={}}
for _,material in ipairs{'floor-a','floor-b','wall','hardwall','door-closed-horizontal','door-closed-vertical','door-open-horizontal','door-open-vertical'} do
 for mask=0,(material:match('^floor') and 0 or 15) do for parity=0,1 do
  manifest.files['checker-revised+refined/korpul/'..material..'-'..mask..'-'..parity..'.png']=true
 end end
end
local missing
local manifestPath='/data-checker-revised/terrain-korpul-manifest.lua'
env.fs={exists=function(path) return path~=missing end}
env.loadfile=function(path) if path==manifestPath then return function() return manifest end end;return loadfile(path) end
local complete=load(root..'overload/mod/class/CheckerTerrain.lua')
eq(complete.ready(),true,'complete mounted manifest accepted')
missing='/data-checker-revised/gfx/refined/korpul/wall-0-0.png'
local incomplete=load(root..'overload/mod/class/CheckerTerrain.lua')
eq(incomplete.ready(),false,'missing runtime PNG closes readiness gate')
missing=nil;manifest.files['checker-revised+../escape.png']=true
local invalid=load(root..'overload/mod/class/CheckerTerrain.lua')
eq(invalid.ready(),false,'manifest cannot escape addon terrain directory')
manifest.files['checker-revised+../escape.png']=nil
local stairManifest={ready=true,revision='test-stairs',files={}}
for _,kind in ipairs{'up','down','world'} do stairManifest.files['checker-revised+refined/korpul/stairs-'..kind..'.png']=true end
local stairManifestPath='/data-checker-revised/terrain-korpul-stairs-manifest.lua'
env.loadfile=function(path)
 if path==manifestPath then return function() return manifest end end
 if path==stairManifestPath then return function() return stairManifest end end
 return loadfile(path)
end
local stairComplete=load(root..'overload/mod/class/CheckerTerrain.lua')
eq(stairComplete.stairsReady(),true,'complete separate stair manifest accepted')
missing='/data-checker-revised/gfx/refined/korpul/stairs-world.png'
local partial=load(root..'overload/mod/class/CheckerTerrain.lua')
eq(partial.stairsReady(),false,'partial stair install stays native')
eq(partial.ready(),true,'partial stair install preserves existing terrain')
missing=nil;stairManifest.files['checker-revised+refined/korpul/foreign.png']=true
local stray=load(root..'overload/mod/class/CheckerTerrain.lua')
eq(stray.stairsReady(),false,'stair manifest accepts only three exact files')
stairManifest.files['checker-revised+refined/korpul/foreign.png']=nil
T.stairAssets=copy(stairManifest)
env.fs=nil;env.loadfile=nil

local seen,fov={},{}
local m={w=5,h=5,seens=function(x,y) return seen[x+y*5] end,infovs=function(x,y) return fov[x+y*5] end}
local x,y,key=2,2,12
seen[key]=true;fov[key]=true
T.observe(m,x,y,grids.DOOR)
eq(T.render(m,x,y,grids.DOOR,'refined'),nil,'not ready keeps native')
T.assets.ready=true
T.mazeAssets.ready=true
local oldPath='checker-revised+refined/maze/old-wall-0-0.png'
local crackPath='checker-revised+refined/maze/cracks-0-0.png'
T.mazeAssets.files[oldPath]=true;T.mazeAssets.files[crackPath]=true
local mazeMap={w=3,h=3,seens=function() return true end,infovs=function() return true end}
T.observe(mazeMap,0,0,grids.OLD_WALL)
eq(T.render(mazeMap,0,0,grids.OLD_WALL,'refined').image,oldPath,'old wall uses Maze mask art')
T.observe(mazeMap,0,0,crack)
eq(T.render(mazeMap,0,0,crack,'refined').image,crackPath,'crack uses dedicated Maze art')
eq(T.render(mazeMap,0,0,crack,'vanilla').image,crack.image,'vanilla restores native crack')
T.mazeAssets.ready=false
local path=T.assetPath('door-closed','horizontal',0,0,x,y)
T.assets.files[path]=true
local board=T.render(m,x,y,grids.DOOR,'refined')
eq(board.image,path,'approved asset installed only in drawing')
eq(grids.DOOR.replace_display,nil,'rule object untouched')
seen[key]=false;fov[key]=false
T.observe(m,x,y,grids.DOOR_OPEN)
eq(T.render(m,x,y,grids.DOOR_OPEN,'refined').image,path,'hidden replacement retains last seen door')
local mutated=copy(grids.DOOR)
seen[key]=true;fov[key]=true;T.observe(m,x,y,mutated)
T.render(m,x,y,mutated,'refined')
seen[key]=false;fov[key]=false
mutated.door_opened=nil;mutated.block_sight=false
T.observe(m,x,y,mutated)
eq(T.render(m,x,y,mutated,'refined').image,path,'hidden in-place mutation retains last seen door')
eq(T.render(m,x,y,mutated,'vanilla').image,'terrain/granite_door1.png','mode off restores last seen native door')
local foreign=copy(mutated);foreign.replace_display={image='external.png'}
eq(T.render(m,x,y,foreign,'refined'),nil,'external display owns rendering')
local unknown={w=5,h=5,seens=function() return false end,infovs=function() return false end,remembers=function() return false end}
local blank=T.render(unknown,2,2,{name='unrecognized hidden hazard'},'refined')
eq(blank.image,'invis.png','unknown content is uniformly blank without classification')
eq(blank.display_on_seen,false,'unknown blank is never drawn as seen')
eq(blank.display_on_remember,false,'unknown blank cannot bleed through FBO always_show')
eq(blank.display_on_unknown,false,'unknown blank has no unknown display')
eq(unknown._checker_korpul,nil,'blanking creates no terrain knowledge')
eq(T.render(unknown,2,2,grids.WALL,'refined'),blank,'unknown shape never depends on hidden type')
eq(T.render(unknown,2,2,foreign,'refined'),nil,'external display wins for unknown cell')
eq(T.render(unknown,2,2,grids.WALL,'vanilla'),nil,'native mode retains native fog rendering')
unknown.remembers=function() return true end
eq(T.render(unknown,2,2,grids.WALL,'refined'),nil,'remembered native cells are not erased')

eq(foreign.replace_display.image,'external.png','external display untouched')
seen[key]=true;fov[key]=true
T.observe(m,x,y,grids.DOOR_OPEN)
local openpath=T.assetPath('door-open','horizontal',0,0,x,y);T.assets.files[openpath]=true
eq(T.render(m,x,y,grids.DOOR_OPEN,'refined').image,openpath,'revisible observes open door')
-- Stairs use an independent foreground over the same deterministic floor.
for id,kind in pairs{UP='stairs-up',DOWN='stairs-down',UP_WILDERNESS='stairs-world'} do
 local g=grids[id]
 local before=copy(g)
 seen[key]=true;fov[key]=true
 T.observe(m,x,y,g)
 local floor=T.assetPath('floor',nil,0,(x+y)%2,x,y);T.assets.files[floor]=true
 local d=T.render(m,x,y,g,'refined')
 eq(d.image,floor,'stair shares floor parity '..id)
 eq(d.add_mos[1].image,'checker-revised+refined/korpul/'..kind..'.png','distinct foreground '..id)
 eq(g.replace_display,nil,'stair Grid is never replaced '..id)
 eq(g.change_level,before.change_level,'unchanged delta '..id)
 eq(g.change_zone,before.change_zone,'unchanged zone '..id)
 eq(g.add_mos[1].image,before.add_mos[1].image,'native overlay untouched '..id)
 seen[key]=false;fov[key]=false
 T.observe(m,x,y,grids.FLOOR)
 eq(T.render(m,x,y,grids.FLOOR,'refined'),d,'hidden replacement retains exact observed stair '..id)
 local native=T.render(m,x,y,grids.FLOOR,'vanilla')
 eq(native.image,g.image,'native remembered floor '..id)
 eq(native.add_mos[1].image,g.add_mos[1].image,'native remembered stair layer '..id)
 eq(T.render(m,x,y,g,'blockout'),native,'unsupported terrain mode retains complete native stair '..id)
 T.stairAssets.ready=false
 eq(T.render(m,x,y,g,'refined'),native,'lost stair readiness restores native layers '..id)
 T.stairAssets.ready=true
 eq(T.render(m,x,y,g,'refined'),d,'setting/readiness returns remembered board stair '..id)
 local foreign=copy(g);foreign.replace_display={image='external.png'}
 eq(T.render(m,x,y,foreign,'refined'),nil,'external stair drawing wins '..id)
 local unknown={w=5,h=5,seens=function() return false end,infovs=function() return false end,remembers=function() return false end}
 eq(T.render(unknown,x,y,g,'refined').image,'invis.png','unknown stair remains blank '..id)
 eq(unknown._checker_korpul,nil,'unknown stair creates no knowledge '..id)
 seen[key]=true;fov[key]=true;T.observe(m,x,y,grids.FLOOR)
 eq(T.render(m,x,y,grids.FLOOR,'refined').add_mos,nil,'re-observed floor removes stair foreground '..id)
end
-- Knowledge masks never read the current hidden map. Test all sixteen masks.
for mask=0,15 do
 m._checker_korpul={}
 for i,d in ipairs{{0,-1},{1,0},{0,1},{-1,0}} do
  if math.floor(mask/2^(i-1))%2==1 then m._checker_korpul[(x+d[1])+(y+d[2])*5]={kind='wall'} end
 end
 eq(T.mask(m,x,y),mask,'N/E/S/W mask '..mask)
end
m._checker_korpul=nil;T.observe(m,x,y,grids.DOOR)
T.render(m,x,y,grids.DOOR,'refined');seen[key]=false;fov[key]=false
m._checker_korpul[key-5]={kind='wall'}
eq(T.render(m,x,y,grids.DOOR,'refined').image,path,'hidden edges do not follow newly learned neighbors')
local cloned=copy(m);cloned.seens=m.seens;cloned.infovs=m.infovs
local originalDisplay=T.render(m,x,y,grids.DOOR,'refined')
local cloneDisplay=T.render(cloned,x,y,grids.DOOR,'refined')
eq(originalDisplay==cloneDisplay,false,'cloned/save-restored pure records rebuild separate display caches')
local function pure(t)
 for _,v in pairs(t) do assert(type(v)~='function' and type(v)~='userdata','save snapshot contains executable/runtime data');if type(v)=='table' then pure(v) end end
end
pure(m._checker_korpul);n=n+1
local success=pcall(function() T.withContext({test=true},function() error('intentional') end) end)
eq(success,false,'draw error propagates');eq(T.context(),nil,'draw context clears on error')
-- Exercise the actual superload chain with a small renderer/path-cache stand-in.
local nativeDraws,updates=0,0
local baseGrid={getMapObjects=function(self,tiles,mos,z)
 nativeDraws=nativeDraws+1;mos[z]=(self.replace_display or self).image
end,loadList=function(_,file,_,res) return res end}
env.loadPrevious=function() return baseGrid end
local Grid=load(root..'superload/mod/class/Grid.lua')
local cellDoor=setmetatable(copy(grids.DOOR),{__index=Grid})
local cells={[12]=cellDoor}
local seen2,fov2={},{}
local am=setmetatable({w=5,h=5,TERRAIN=1,seens=function(a,b) return seen2[a+b*5] end,infovs=function(a,b) return fov2[a+b*5] end},{__call=function(_,a,b) return cells[a+b*5] end})
local baseMap={updateMap=function(self,a,b)
 updates=updates+1
 local g=self(a,b,1);local mos={};if g then g:getMapObjects({},mos,1) end
 self.last=mos[1]
end}
for _,method in ipairs{'apply','applyLite','applyExtraLite'} do baseMap[method]=function(_,a,b) seen2[a+b*5]=true;fov2[a+b*5]=true;return 'native-result' end end
env.loadPrevious=function() return baseMap end
local Adapter=load(root..'superload/engine/Map.lua')
getmetatable(am).__index=Adapter
env.game={zone={short_name='ruins-kor-pul'},level={map=am}}
eq(am:apply(2,2),'native-result','FOV native return preserved')
eq(am.last,path,'FOV callback installs display locally')
eq(updates,1,'single observed grid update without full scan')
eq(cellDoor.replace_display,nil,'adapter never owns actual replace_display')
eq(cellDoor._mo,nil,'shared native Grid cache is restored after drawing')
eq(cellDoor.door_opened,'DOOR_OPEN','adapter preserves native door action target')
seen2[12]=false;fov2[12]=false
cells[12]=setmetatable(copy(grids.DOOR_OPEN),{__index=Grid})
am:updateMap(2,2);eq(am.last,path,'map mutation in darkness retains drawing')
mode='vanilla';am:updateMap(2,2)
eq(am.last,'terrain/granite_door1.png','adapter mode off restores remembered native')
mode='refined';am:applyLite(2,2)
eq(am.last,openpath,'adapter re-observation sees native replacement')
cells[12].replace_display={image='foreign.png'}
am:updateMap(2,2);eq(am.last,'foreign.png','adapter yields to external display')
eq(T.context(),nil,'adapter context never escapes native update')
T.assets.ready=false;am._checker_korpul=nil
local before=updates;am:apply(2,2)
eq(updates,before,'no asset readiness means no added FOV work')
T.assets.ready=true
-- Preserve the established forest selector and ownership behavior.
local grass={name='grass',subtype='grass',type='floor',define_as='GRASS'}
function grass:clone() local g={};for k,v in pairs(self) do g[k]=v end;return g end
function grass:removeAllMOs() end
local cell=grass
local forest=setmetatable({w=1,h=1},{__call=function(_,a,b,layer,g) if a~=0 or b~=0 then return end;if g then cell=g end;return cell end})
local host={zone={short_name='trollmire'},level={map=forest}}
T.apply(host)
eq(cell.replace_display.image,'checker-revised+refined/grass0.png','forest refined parity')
eq(grass.replace_display,nil,'forest native shared prototype remains unmodified')
mode='vanilla';T.apply(host);eq(cell.replace_display,nil,'forest native restoration')

-- F1: FLOODED Trollmire identities go through the exact same T.apply path;
-- gating is by grid identity (define_as/name/add_displays), not the zone's
-- is_flooded flag (CONTRACT.md Section 8).
local function newGrid(t)
 t.removeAllMOs=function() end
 t.clone=function(self) local g={};for k,v in pairs(self) do g[k]=v end;return g end
 return t
end
host.zone.is_flooded=true
mode='refined'
local bogtree=newGrid{name='tree',subtype='water',define_as='BOGTREE',does_block_move=true,block_sight=true}
cell=bogtree;T.apply(host)
eq(cell.replace_display.image,'checker-revised+refined/bog-tree-a0-0-0.png','F1 BOGTREE (define_as) gets bog-tree art, not plain tree')

local bogwater=newGrid{name='bog water',subtype='water'}
cell=bogwater;T.apply(host)
eq(cell.replace_display.image,'checker-revised+refined/bog0-0-0.png','F1 BOGWATER gets bog art')

local bogmisc=newGrid{name='bog water',subtype='water',add_displays={{image='terrain/misc_bog1.png'}}}
cell=bogmisc;T.apply(host)
eq(cell.replace_display.image,'checker-revised+refined/bog-misc1-0-0.png','F1 BOGWATER_MISC (add_displays) gets bog floor + misc variant')
eq(cell.add_displays[1].image,'terrain/misc_bog1.png','F1 native misc layer stays on the grid; our replace_display owns the look')

local hardtree=newGrid{name='tall thick tree',subtype='grass',does_block_move=true}
cell=hardtree;T.apply(host)
local hardtreeImage=cell.replace_display.image
eq(hardtreeImage,'checker-revised+refined/tree-hard0.png','F1 HARDTREE gets its own art')

local tree=newGrid{name='tree',subtype='grass',does_block_move=true}
cell=tree;T.apply(host)
eq(cell.replace_display.image,'checker-revised+refined/tree-oak0.png','F1 ordinary TREE keeps plain tree family art even when flooded')
eq(cell.replace_display.image~=hardtreeImage,true,'F1 hardtree and tree render distinct art (CONTRACT I1)')

host.zone.is_flooded=nil
mode='vanilla'

-- G0: Old Forest (docs/expansion-plan-20260928/TERRAIN-INVENTORY.md Section
-- 1). DEFAULT layout's GRASS/TREE/HARDTREE use subtype "dark_grass" (its own
-- copy of the fields, not a base= override); the zone-scoped alias in
-- terrain() must fold that into the same grass/tree/hardtree identities as
-- every other supported zone, without changing any rule field.
mode='refined'
host.zone={short_name='old-forest'}
local ofGrass=newGrid{name='grass',subtype='dark_grass',type='floor',define_as='GRASS'}
cell=ofGrass;T.apply(host)
eq(cell.replace_display.image,'checker-revised+refined/grass0.png','Old Forest DEFAULT dark_grass GRASS reuses grass art')
local ofTree=newGrid{name='tree',subtype='dark_grass',does_block_move=true,block_sight=true,can_pass={pass_tree=1},dig='GRASS'}
cell=ofTree;T.apply(host)
eq(cell.replace_display.image,'checker-revised+refined/tree-oak0.png','Old Forest DEFAULT dark_grass TREE reuses tree art')
eq(ofTree.does_block_move,true,'Old Forest tree collision rule is unchanged')
eq(ofTree.block_sight,true,'Old Forest tree sight-block rule is unchanged')
local ofHardtree=newGrid{name='tall thick tree',subtype='dark_grass',does_block_move=true,block_sight=true,block_sense=true,block_esp=true}
cell=ofHardtree;T.apply(host)
eq(cell.replace_display.image,'checker-revised+refined/tree-hard0.png','Old Forest DEFAULT dark_grass HARDTREE gets its own hardtree art')
eq(ofHardtree.block_sense,true,'Old Forest hardtree ESP-block rule is unchanged')
local ofExit=newGrid{name='way to the previous level',subtype='grass',change_level=-1}
cell=ofExit;T.apply(host)
eq(cell.replace_display.image,'checker-revised+refined/exit0.png','Old Forest GRASS_UP4/DOWN6 (plain subtype grass) reuses exit art')
local ofWild=newGrid{name='exit to the worldmap',subtype='grass',change_zone='wilderness'}
cell=ofWild;T.apply(host)
eq(cell.replace_display.image,'checker-revised+refined/exit0.png','Old Forest GRASS_UP_WILDERNESS reuses exit art')
-- T9/S3: LAKE_NUR has no subtype (old-forest/grids.lua), so terrain() never
-- claims it. Only the zone-file stamped, unchanged exit becomes a board exit.
local lakeNur=newGrid{name='way to the lake of Nur',change_level=1,change_zone='lake-nur'}
cell=lakeNur;T.apply(host)
eq(lakeNur.replace_display,nil,'unstamped Old Forest LAKE_NUR look-alike stays native')
local function nurExit(image)
 local g={define_as='LAKE_NUR',name='way to the lake of Nur',display='>',color_r=255,color_g=255,color_b=0,
  image=image,add_displays={{image='terrain/way_next_2.png'}},notice=true,always_remember=true,
  change_level=1,change_zone='lake-nur'}
 T.markSource(g,'/data/zones/old-forest/grids.lua')
 return g
end
for _,image in ipairs{'terrain/grass/dark_grass_main_01.png','terrain/grass.png'} do
 eq(T.oldForestExit(nurExit(image)),'exit','stamped LAKE_NUR exact exit '..image)
 cell=newGrid(nurExit(image));T.apply(host)
 eq(cell.replace_display.image,'checker-revised+refined/exit0.png','Old Forest LAKE_NUR board exit '..image)
 eq(cell.change_zone,'lake-nur','LAKE_NUR destination untouched');eq(cell.change_level,1,'LAKE_NUR level untouched')
end
for label,mutate in pairs{
 check=function(g) g.change_level_check=function() return true end end,
 zone=function(g) g.change_zone='other' end,
 level=function(g) g.change_level=2 end,
 force=function(g) g.force_down=true end,
 layer=function(g) g.add_displays[1].image='terrain/way_next_8.png' end,
 extra=function(g) g.add_displays[2]={image='foreign.png'} end,
 image=function(g) g.image='terrain/sand.png' end,
 stand=function(g) g.on_stand=function() end end,
 block=function(g) g.does_block_move=true end,
 unstamped=function(g) g._checker_oldforest_source=nil end,
} do
 local g=nurExit('terrain/grass.png');mutate(g)
 eq(T.oldForestExit(g),nil,'changed LAKE_NUR stays native: '..label)
end
host.zone={short_name='trollmire'};cell=newGrid(nurExit('terrain/grass.png'));T.apply(host)
eq(cell.replace_display,nil,'LAKE_NUR exit art scoped to Old Forest')
host.zone={short_name='old-forest'}

-- CRYSTALINE layout is plain subtype "grass" already (same as Trollmire),
-- so it must work with no alias at all -- only the zone whitelist widening.
local ofCrystalTree=newGrid{name='tree',subtype='grass',does_block_move=true,block_sight=true}
cell=ofCrystalTree;T.apply(host)
eq(cell.replace_display.image,'checker-revised+refined/tree-oak0.png','Old Forest CRYSTALINE plain-grass TREE reuses tree art')

-- The dark_grass alias is scoped to old-forest ONLY. Heart of the Gloom's
-- own TREE identity also happens to use subtype "dark_grass" (unrelated
-- underground_gloomy/dreamy.lua definition); heart-gloom is not in the
-- zone whitelist, so it must stay fully native, not be reinterpreted as an
-- Old Forest tree (TERRAIN-INVENTORY.md Section 5's explicit caution).
host.zone={short_name='heart-gloom'}
local hogTree=newGrid{name='tree',subtype='dark_grass',does_block_move=true,block_sight=true}
local hogBefore=hogTree.image
cell=hogTree;T.apply(host)
eq(hogTree.replace_display,nil,'Heart of the Gloom dark_grass TREE is never painted')
eq(hogTree.image,hogBefore,'Heart of the Gloom TREE keeps its native image untouched')

-- G0: Slazish Fens (TERRAIN-INVENTORY.md Section 2) reuses Trollmire
-- FLOODED's identities directly -- no dark_grass alias needed, only the
-- zone whitelist.
host.zone={short_name='slazish-fen'}
local sfBogtree=newGrid{name='tree',subtype='water',define_as='BOGTREE7',does_block_move=true,block_sight=true}
cell=sfBogtree;T.apply(host)
eq(cell.replace_display.image:match('^checker%-revised%+refined/bog%-tree'),'checker-revised+refined/bog-tree','Slazish Fens BOGTREE reuses bog-tree art')
local sfBogwater=newGrid{name='bog water',subtype='water'}
cell=sfBogwater;T.apply(host)
eq(cell.replace_display.image,'checker-revised+refined/bog0-0-0.png','Slazish Fens BOGWATER reuses bog art')
local sfBogmisc=newGrid{name='bog water',subtype='water',add_displays={{image='terrain/misc_bog4.png'}}}
cell=sfBogmisc;T.apply(host)
eq(cell.replace_display.image:match('^checker%-revised%+refined/bog%-misc'),'checker-revised+refined/bog-misc','Slazish Fens BOGWATER_MISC reuses bog-misc art')
local sfGrass=newGrid{name='grass',subtype='grass',type='floor',define_as='GRASS'}
cell=sfGrass;T.apply(host)
eq(cell.replace_display.image,'checker-revised+refined/grass0.png','Slazish Fens GRASS reuses grass art')
local sfExit=newGrid{name='way to the previous level',subtype='grass',change_level=-1}
cell=sfExit;T.apply(host)
eq(cell.replace_display.image,'checker-revised+refined/exit0.png','Slazish Fens GRASS_UP4/DOWN6 reuses exit art')
local sfGates=newGrid{name='exit to the worldmap',subtype='grass',change_zone='town-gates-of-morning',change_zone_auto_stairs=true}
cell=sfGates;T.apply(host)
eq(cell.replace_display.image,'checker-revised+refined/exit0.png','Slazish Fens GATES_OF_MORNING (base=GRASS_UP_WILDERNESS) reuses exit art')
-- PORTAL is base=BOGWATER but overrides name to "coral portal", so it fails
-- the water branch's name check and stays native; block_move is a function
-- (native puzzle gate) that terrain() never reads. This is the task's
-- explicit "must stay native" case for Slazish Fens.
local sfPortal=newGrid{name='coral portal',subtype='water',does_block_move=true,block_move=function() return true end}
local sfPortalImage=sfPortal.image
cell=sfPortal;T.apply(host)
eq(sfPortal.replace_display,nil,'Slazish Fens PORTAL (coral portal) stays native')
eq(sfPortal.image,sfPortalImage,'Slazish Fens PORTAL keeps native image untouched')

-- Rhaloren puts untouched basic.lua stone and forest grids on one map.
local campCells={[0]=grids.FLOOR,[1]=newGrid{name='tree',subtype='grass',does_block_move=true,dig='GRASS'},[2]=grids.WALL}
local camp=setmetatable({w=3,h=1,seens=function() return true end,infovs=function() return true end},
 {__call=function(self,cx,cy,layer,value)
  if cy~=0 or cx<0 or cx>2 then return end
  if value then campCells[cx]=value end
  return campCells[cx]
 end})
function camp:updateMap() end
host.zone={short_name='rhaloren-camp'};host.level.map=camp;mode='refined'
eq(T.variant(host.zone),'RHALOREN','camp enables stone adapter on both layouts')
T.apply(host)
eq(campCells[1].replace_display.image,'checker-revised+refined/tree-willow1.png','camp outdoor tree uses forest adapter')
eq(campCells[0].replace_display,nil,'camp stone is not claimed by forest adapter')
for cx=0,2,2 do
 local g=campCells[cx];eq(T.observe(camp,cx,0,g),true,'camp observes stone cell '..cx)
 local kind=T.classify(g);local path=T.assetPath(kind,nil,T.mask(camp,cx,0),cx%2,cx,0)
 T.assets.files[path]=true
 eq(T.render(camp,cx,0,g,'refined').image,path,'camp stone art '..cx)
end
eq(camp._checker_korpul[1],nil,'forest cell has no stone record')
mode='blockout';T.apply(host)
eq(campCells[1].replace_display.image,'checker-revised+tree1.png','camp blockout keeps forest art')
eq(T.render(camp,0,0,campCells[0],'blockout').image,grids.FLOOR.image,'camp blockout stone uses native snapshot')
mode='vanilla';T.apply(host)
eq(campCells[1].replace_display,nil,'camp vanilla releases forest art')
eq(T.render(camp,0,0,campCells[0],'vanilla').image,grids.FLOOR.image,'camp vanilla restores stone snapshot')
mode='refined';T.apply(host)
eq(campCells[1].replace_display.image,'checker-revised+refined/tree-willow1.png','camp forest round trip')
campCells[1]=newGrid{name='grass',subtype='grass',type='floor',define_as='GRASS'}
eq(T.repair(host,1,0,1,0),1,'camp forest dig repairs replacement grid')
eq(campCells[1].replace_display.image,'checker-revised+refined/grass1.png','camp forest dig displays grass')
campCells[2]=grids.FLOOR
eq(T.observe(camp,2,0,campCells[2]),true,'camp stone dig replaces wall record')
local dugPath=T.assetPath('floor',nil,T.mask(camp,2,0),0,2,0);T.assets.files[dugPath]=true
eq(T.render(camp,2,0,campCells[2],'refined').image,dugPath,'camp stone dig displays floor')
host.level.map=forest

-- Dreadfell uses the same stamped, exact basic.lua identities, including
-- stairs. Static vault changes and foreign identities remain native.
host.zone={short_name='dreadfell'};host.level.map=camp;mode='refined'
T.apply(host)
eq(host.checker_mode,'refined','Dreadfell refined mode')
eq(T.repair(host,0,0,2,0),nil,'Dreadfell skips forest repair')
local dreadwall=copy(grids.WALL);dreadwall.name='vault wall'
eq(T.classify(dreadwall),nil,'Dreadfell changed vault identity stays native')
eq(T.classify(grids.DOOR_VAULT),'door-closed','S2/T4 Dreadfell sealed vault door is the board closed door (flipped)')
eq(T.classify(grids.GENERIC_LEVER_DOOR),nil,'Dreadfell lever door stays native')
eq(T.classify(grids.UP_WILDERNESS),'stairs-world','Dreadfell L1 world exit')
mode='blockout';T.apply(host)
eq(host.checker_mode,'vanilla','Dreadfell blockout uses native stone')
mode='vanilla';T.apply(host)
eq(host.checker_mode,'vanilla','Dreadfell native round trip')
mode='refined';T.apply(host)
eq(host.checker_mode,'refined','Dreadfell refined restored')

host.zone={short_name='trollmire'};host.level.map=forest;mode='vanilla'
-- Native random-event callbacks keep their source path when cloneFull copies
-- the grid. A translated tooltip is intentionally irrelevant to identity.
local fell=assert(loadstring('return function(self,x,y,who) who:setEffect(who.EFF_FELL_AURA,1,{}) end',
 '@/data/general/events/fell-aura.lua'))()
local stoneAura=copy(grids.FLOOR)
stoneAura.name='石地（堕落光环）';stoneAura.on_stand=fell
stoneAura.special_minimap={r=60,g=99,b=99};stoneAura.always_remember=true
eq(auraStyle,'subtle','event aura defaults to subtle')
eq(T.auraKind(stoneAura),'violet','event source determines polarity independent of locale')
eq(T.classify(stoneAura),'floor','translated event stone keeps base floor identity')
local traditional=copy(stoneAura);traditional.name='石地（毀滅光環）'
eq(T.classify(traditional),'floor','traditional Chinese event stone keeps identity')
local auraMap={w=1,h=1,seens=function() return true end,infovs=function() return true end,
 remembers=function() return true end}
eq(T.observe(auraMap,0,0,stoneAura),true,'stone aura is observed')
local auraPath=T.assetPath('floor',nil,0,0,0,0);T.assets.files[auraPath]=true
eq(T.render(auraMap,0,0,stoneAura,'refined').add_displays[1].image,
 'checker-revised+aura-violet-subtle.png','stone defaults to subtle aura mask')
auraStyle='moderate'
eq(T.render(auraMap,0,0,stoneAura,'refined').add_displays[1].image,
 'checker-revised+aura-violet-moderate.png','stone setting refreshes mask')
auraStyle='subtle'
eq(T.render(auraMap,0,0,stoneAura,'vanilla').add_displays,nil,'native stone has no board overlay')
local target={EFF_FELL_AURA=17,setEffect=function(self,id,duration) self.applied=id end}
stoneAura.on_stand(stoneAura,1,1,target)
eq(target.applied,17,'native on_stand callback remains attached')
for field,value in pairs{image='changed.png',dig='FLOOR',block_sight=true,display_scale=2} do
 local changed=copy(stoneAura);changed[field]=value
 eq(T.classify(changed),nil,'event stone changed other field '..field)
end
local unsafe=copy(stoneAura);unsafe.on_stand_safe=true
eq(T.classify(unsafe),nil,'non-native safety hint remains outside stone contract')
local life=copy(stoneAura)
life.on_stand=assert(loadstring('return function() end','@/data/general/events/font-life.lua'))()
life.name='floor (life aura)';life.on_stand_safe=true
eq(T.classify(life),'floor','native life-aura safety hint is accepted')
local unrelated=copy(stoneAura)
unrelated.on_stand=function() end
eq(T.classify(unrelated),nil,'unknown on_stand source remains native')
local grassAura=newGrid{name='草地（反魔法光环）',type='floor',subtype='grass',
 define_as='GRASS_PATCH3',image='terrain/grass/grass_main_03.png',display='.',on_stand=assert(loadstring('return function() end',
 '@/data/general/events/antimagic-bush.lua'))(),special_minimap={r=85,g=35,b=35},always_remember=true}
cell=grassAura;mode='refined';T.apply(host)
eq(cell.replace_display.image,'checker-revised+refined/grass0.png','translated forest aura is painted by define_as')
local traditionalGrass=newGrid{name='草地（反魔法光環）',type='floor',subtype='grass',
 define_as='GRASS_PATCH3',image='terrain/grass/grass_main_03.png',display='.',
 on_stand=grassAura.on_stand,special_minimap={r=85,g=35,b=35},always_remember=true}
cell=traditionalGrass;T.apply(host)
eq(cell.replace_display.image,'checker-revised+refined/grass0.png','traditional Chinese forest aura keeps identity')
cell=grassAura;T.apply(host)
eq(cell.replace_display.add_displays[1].image,'checker-revised+aura-violet-subtle.png','forest defaults to subtle mask')
auraStyle='moderate';T.apply(host)
eq(cell.replace_display.add_displays[1].image,'checker-revised+aura-violet-moderate.png','moderate setting refreshes forest mask')
auraStyle='subtle';T.apply(host)
eq(cell.replace_display.add_displays[1].image,'checker-revised+aura-violet-subtle.png','subtle setting restores forest mask')
mode='vanilla';T.apply(host)
eq(cell.replace_display,nil,'native forest restores original presentation')
mode='refined';T.apply(host)
local foreignAura=newGrid{name='草地（反魔法光环）',type='floor',subtype='grass',
 define_as='FOREIGN',on_stand=grassAura.on_stand}
cell=foreignAura;T.apply(host)
eq(cell.replace_display,nil,'unknown forest identity remains native')
local alteredAura=newGrid{name='草地（反魔法光环）',type='floor',subtype='grass',
 define_as='GRASS_PATCH3',image='foreign.png',display='.',on_stand=grassAura.on_stand}
cell=alteredAura;T.apply(host)
eq(cell.replace_display,nil,'changed event forest appearance remains native')
for _,sample in ipairs{
 {id='GRASS_SHORT',name='草地（反魔法光环）',image='terrain/grass.png',display='.',expected='grass'},
 {id='FLOWER7',name='花朵（反魔法光环）',image='terrain/grass.png',display=';',expected='flower'},
 {id='GRASS_ROAD_DIRT',name='道路（反魔法光环）',image='terrain/grass.png',display='=',road='dirt',expected='road'},
 {id='GRASS_ROAD_STONE',name='道路（反魔法光环）',image='terrain/grass.png',display='=',road='oldstone',expected='road'},
} do
 cell=newGrid{name=sample.name,type='floor',subtype='grass',define_as=sample.id,
  image=sample.image,display=sample.display,road=sample.road,on_stand=grassAura.on_stand}
 T.apply(host)
 eq(cell.replace_display.image,'checker-revised+refined/'..sample.expected..'0.png',
  'translated event forest family '..sample.id)
end
cell=newGrid{name='old road (protective aura)',type='floor',subtype='grass',
 define_as='GRASS_ROAD_DIRT',image='terrain/grass.png',display='=',road='dirt',
 on_stand=assert(loadstring('return function() end','@/data/general/events/protective-aura.lua'))(),
 add_displays={{image='invis.png',add_mos={{image='terrain/road_dirt/road_turn_a_02.png'}}}}}
T.apply(host)
eq(cell.replace_display.image,'checker-revised+refined/road0.png',
 'native NicerTiles road decoration is replaced by board road after event clone')
cell.add_displays[1].add_mos[1].image='foreign/road.png';cell.replace_display=nil;cell._checker_terrain=nil
T.apply(host)
eq(cell.replace_display,nil,'foreign road decoration remains native')

-- Snow-rock family: exact mountain identities, only in Norgos for now.
host.zone={short_name='norgos-lair',is_invaded=false};mode='refined'
local snowGround=newGrid{define_as='ROCKY_GROUND',name='rocky ground',type='floor',subtype='rock',
 image='terrain/snowy_grass.png',display='.'}
cell=snowGround;T.apply(host)
eq(cell.replace_display.image,'checker-revised+refined/snow/snow-ground0.png','Norgos snowy floor')
eq(T.rockKind(cell),'snow-ground','census uses exact runtime snow-ground identity')
local snowAura=copy(snowGround);snowAura.on_stand=grassAura.on_stand
snowAura.name='rocky ground (antimagic aura)';snowAura.replace_display=nil;snowAura._checker_terrain=nil
cell=newGrid(snowAura);T.apply(host)
eq(T.rockKind(cell),'snow-ground','known event ring keeps snow floor identity')
eq(cell.replace_display.image,'checker-revised+refined/snow/snow-ground0.png','snow event ring repainted')
local snowAuraCenter=copy(snowAura);snowAuraCenter.add_displays={{image='terrain/antimagic_bush.png'}}
cell=newGrid(snowAuraCenter);T.apply(host)
eq(T.rockKind(cell),nil,'special snow event center remains native')
eq(cell.replace_display,nil,'special snow event center display preserved')
cell=newGrid(copy(snowGround))
host.zone.is_invaded=true;T.apply(host)
eq(cell.replace_display.image,'checker-revised+refined/snow/snow-ground0.png','INVADED uses same terrain')
local snowTree=newGrid{define_as='ROCKY_SNOWY_TREE12',name='snowy tree',type='wall',subtype='rock',
 image='terrain/snowy_grass.png',display='#',does_block_move=true,block_sight=true,
 dig='ROCKY_GROUND',can_pass={pass_tree=1},add_mos={},
 add_displays={{image='invis.png',add_mos={{image='terrain/trees/pine_trunk.png'}}},
  {image='terrain/trees/pine_foliage_winter_01.png'}}}
cell=snowTree;T.apply(host)
eq(cell.replace_display.image,'checker-revised+refined/snow/tree-pine0.png','Norgos blocking snow tree')
eq(T.rockKind(cell),'snow-tree','census uses exact runtime snow-tree identity')
local snowTreeAura=copy(snowTree);snowTreeAura.on_stand=grassAura.on_stand
snowTreeAura.replace_display=nil;snowTreeAura._checker_terrain=nil
cell=newGrid(snowTreeAura);T.apply(host)
eq(T.rockKind(cell),'snow-tree','known event ring keeps blocking snow tree identity')
local snowUnknown=copy(snowTree);snowUnknown.on_stand=function() end
snowUnknown.replace_display=nil;snowUnknown._checker_terrain=nil
cell=newGrid(snowUnknown);T.apply(host)
eq(T.rockKind(cell),nil,'unknown snow-tree callback remains native')
for _,entry in ipairs{{'ROCKY_UP6',-1,nil,'terrain/way_next_6.png','stairs-up','<'},
  {'ROCKY_DOWN4',1,nil,'terrain/way_next_4.png','stairs-down','>'},
  {'ROCKY_UP_WILDERNESS',1,'wilderness','terrain/worldmap.png','stairs-world','<'}} do
 local id,level,zone,image,kind,display=entry[1],entry[2],entry[3],entry[4],entry[5],entry[6]
 local g=newGrid{define_as=id,name='way',type='floor',subtype='rock',image='terrain/snowy_grass.png',
  display=display,change_level=level,change_zone=zone,add_displays={{image=image}}}
 cell=g;T.apply(host)
 eq(cell.replace_display.image,'checker-revised+refined/snow/'..kind..'0.png','Norgos '..id)
end
for field,value in pairs{dig='OTHER',block_sight=false,subtype='grass',image='terrain/rocky_ground.png'} do
 local g=copy(snowTree);g[field]=value;g.replace_display=nil;g._checker_terrain=nil
 cell=newGrid(g);T.apply(host)
 eq(cell.replace_display,nil,'altered snow tree '..field..' stays native')
end
for _,id in ipairs{'MOUNTAIN_WALL','CLIFFSIDE','HARDMOUNTAIN_WALL','ROCKY_SNOWY_TREE31'} do
 cell=newGrid{define_as=id,name='snowy tree',type='wall',subtype='rock',image='terrain/snowy_grass.png',
  display='#',does_block_move=true,block_sight=true,dig='ROCKY_GROUND',can_pass={pass_tree=1}}
 T.apply(host);eq(cell.replace_display,nil,'unsupported rock identity '..id)
end
cell=newGrid(copy(snowGround));host.zone={short_name='daikara'};T.apply(host)
eq(cell.replace_display,nil,'Daikara does not borrow the snowy Norgos floor identity')
local rockGround=copy(snowGround);rockGround.image='terrain/rocky_ground.png'
cell=newGrid(rockGround);T.apply(host)
eq(cell.replace_display.image,'checker-revised+refined/daikara/rock-ground0.png','Daikara bare rock')
eq(T.rockKind(cell,true),'rock-ground','Daikara bare-rock census')
local tempestExit=newGrid{define_as='ROCKY_UP_WILDERNESS',name='exit to the worldmap',
 type='floor',subtype='rock',image='terrain/rocky_ground.png',display='<',
 change_level=1,change_zone='wilderness',add_displays={{image='terrain/worldmap.png'}}}
eq(T.rockKind(tempestExit,true),'stairs-world','unchanged mountain world exit is reusable')
tempestExit.change_level_check=function() end
eq(T.rockKind(tempestExit,true),nil,'Tempest quest-modified exit stays native')
local rockTree=copy(snowTree);rockTree.image='terrain/rocky_ground.png'
cell=newGrid(rockTree);T.apply(host)
eq(cell.replace_display.image,'checker-revised+refined/daikara/tree-pine0.png','Daikara snow tree over bare rock')
local mountain=newGrid{define_as='MOUNTAIN_WALL2',name='rocky mountain',type='rockwall',
 subtype='rock',image='terrain/mountain5_2.png',display='#',does_block_move=true,
 block_sight=true,air_level=-20,dig='ROCKY_GROUND',can_pass={pass_wall=1}}
cell=mountain;T.apply(host)
eq(cell.replace_display.image,'checker-revised+refined/daikara/mountain-wall-00.png','Daikara mountain wall')
eq(T.rockKind(cell,true),'mountain-wall','Daikara wall census')
local borderedMountain=copy(mountain)
borderedMountain.add_displays={{image='invis.png'},
 {image='terrain/mountain5_2.png',z=3,add_mos={{image='terrain/mountain4.png'},
  {image='terrain/mountain7i.png'}}},
 {image='terrain/mountain8.png',z=16,display_y=-1},
 {image='terrain/mountain9.png',z=18,display_x=-1}}
cell=newGrid(borderedMountain);T.apply(host)
eq(T.rockKind(cell,true),'mountain-wall','native mountain border is recognised')
local foreignMountain=copy(borderedMountain);foreignMountain.add_displays[3].image='foreign.png'
cell=newGrid(foreignMountain);T.apply(host)
eq(cell.replace_display,nil,'foreign mountain border remains native')
local lava=newGrid{define_as='LAVA_FLOOR12',name='lava floor',type='floor',subtype='lava',
 image='terrain/lava/lava_floor12.png',display='.',shader='lava'}
cell=lava;T.apply(host)
eq(cell.replace_display.image,'checker-revised+refined/daikara/lava-floor0.png','harmless Daikara lava')
eq(T.lavaKind(cell),'lava-floor','harmless lava census')
local borderedLava=copy(lava);borderedLava.add_displays={{image='invis.png',
 add_mos={{image='terrain/lava/lava_floor_2_05.png'},
 {image='terrain/lava/lava_floor_inner_7_04.png'}}}}
cell=newGrid(borderedLava);T.apply(host)
eq(T.lavaKind(cell),'lava-floor','native lava borders are recognised')
local foreignLava=copy(borderedLava);foreignLava.add_displays[1].add_mos[1].image='foreign.png'
cell=newGrid(foreignLava);T.apply(host)
eq(cell.replace_display,nil,'foreign lava border remains native')
local lavaDown=copy(lava);lavaDown.change_level=1
cell=newGrid(lavaDown);T.apply(host)
eq(cell.replace_display,nil,'lava with invented transition remains native')
for _,id in ipairs{'RIFT','HARDMOUNTAIN_WALL','CLIFFSIDE'} do
 cell=newGrid{define_as=id,name='other',type='rockwall',subtype='rock',image='terrain/rocky_mountain.png'}
 T.apply(host);eq(cell.replace_display,nil,'Daikara unsupported '..id)
end
mode='blockout';cell=newGrid(copy(mountain));T.apply(host)
eq(cell.replace_display.image,'checker-revised+tree0.png','Daikara wall blockout')
mode='vanilla';T.apply(host);eq(cell.replace_display,nil,'Daikara native restoration')
mode='refined';T.apply(host)
eq(cell.replace_display.image,'checker-revised+refined/daikara/mountain-wall-00.png','Daikara refined restored')
host.zone={short_name='norgos-lair'};cell=newGrid(copy(snowTree))
mode='blockout';T.apply(host)
eq(cell.replace_display.image,'checker-revised+tree0.png','snow tree blockout')
mode='vanilla';T.apply(host);eq(cell.replace_display,nil,'snow native restoration')
mode='refined';T.apply(host)
eq(cell.replace_display.image,'checker-revised+refined/snow/tree-pine0.png','snow refined restored')
host.zone={short_name='tempest-peak'};cell=newGrid(copy(rockGround))
T.apply(host)
eq(cell.replace_display.image,'checker-revised+refined/daikara/rock-ground0.png','Tempest reuses exact Daikara rock')
cell=newGrid(copy(mountain));T.apply(host)
eq(cell.replace_display.image,'checker-revised+refined/daikara/mountain-wall-00.png','Tempest reuses exact mountain wall')
mode='blockout';T.apply(host)
eq(cell.replace_display.image,'checker-revised+tree0.png','Tempest mountain blockout')
mode='vanilla';T.apply(host);eq(cell.replace_display,nil,'Tempest vanilla restores mountain')
mode='refined';T.apply(host)
eq(cell.replace_display.image,'checker-revised+refined/daikara/mountain-wall-00.png','Tempest refined round trip')
host.zone={short_name='other-peak'};T.apply(host)
eq(cell.replace_display,nil,'mountain source cannot cross zone')
-- Sandworm uses exact native sand.lua identities, including the function dig.
native.class.makeTrees=function() return {} end
load(root..'../../modules/tome/data/general/grids/sand.lua',native)
for i=1,11 do eq(T.sandTerrain(grids['UNDERGROUND_SAND'..i]),'floor','sand floor '..i) end
for i=1,6 do eq(T.sandTerrain(grids['SANDWALL'..i]),'wall','sand wall '..i) end
local unknownSand=copy(grids.UNDERGROUND_SAND);unknownSand.define_as='UNDERGROUND_SAND12'
eq(T.sandTerrain(unknownSand),nil,'unknown sand floor variant remains native')
unknownSand=copy(grids.SANDWALL);unknownSand.define_as='SANDWALL7'
eq(T.sandTerrain(unknownSand),nil,'unknown sand wall variant remains native')
eq(T.sandTerrain(grids.SANDWALL),'wall','sand base wall')
for id,kind in pairs{SAND_LADDER_UP='ladder-up',SAND_LADDER_DOWN='ladder-down',SAND_LADDER_UP_WILDERNESS='ladder-world'} do
 eq(T.sandTerrain(grids[id]),kind,'sand ladder '..id)
 local changed=copy(grids[id]);changed.change_level=99
 eq(T.sandTerrain(changed),nil,'changed sand exit '..id)
end
for _,id in ipairs{'SAND','PALMTREE'} do eq(T.sandTerrain(grids[id]),nil,'unapproved sand '..id) end
eq(T.sandTerrain(grids.SANDWALL_STABLE),'wall','stable wall shares reviewed sand art')
for i=1,6 do eq(T.sandTerrain(grids['SANDWALL_STABLE'..i]),'wall','stable sand wall '..i) end
local stableChanged=copy(grids.SANDWALL_STABLE);stableChanged.dig=nil
eq(T.sandTerrain(stableChanged),nil,'changed stable dig contract remains native')
local sandWall=copy(grids.SANDWALL);sandWall.add_displays={{image='invis.png'},{image='terrain/sand/sandwall_8_1.png'}}
eq(T.sandTerrain(sandWall),'wall','native edited sand wall')
sandWall.add_displays[2].image='foreign.png';eq(T.sandTerrain(sandWall),nil,'foreign wall art stays native')
local changedSand=copy(grids.SANDWALL);changedSand.dig='UNDERGROUND_SAND'
eq(T.sandTerrain(changedSand),nil,'changed dig contract stays native')
local chestSand=copy(grids.UNDERGROUND_SAND);chestSand.add_displays={{image='object/chest3.png'}}
eq(T.sandTerrain(chestSand),nil,'chest floor remains native')
host.zone={short_name='ritch-tunnels'};mode='refined'
cell=newGrid(grids.SANDWALL_STABLE);T.apply(host)
eq(cell.replace_display.image,'checker-revised+refined/sand/wall-0-0.png','Ritch stable sand wall')
mode='blockout';T.apply(host)
eq(cell.replace_display.image,'checker-revised+tree0.png','Ritch wall blockout')
mode='vanilla';T.apply(host)
eq(cell.replace_display,nil,'Ritch wall native restore')
mode='refined';T.apply(host)
-- Crystal replacement owns the wall display, including makeCrystals layers;
-- mode and zone gates must preserve the native wall on fallback.
host.zone={short_name='scintillating-caves'};mode='refined'
cell=newGrid(crystal('CRYSTAL_WALL','wall'));T.apply(host)
eq(cell.replace_display.image,'checker-revised+refined/crystal/wall-0-0.png','crystal refined wall')
eq(cell.replace_display.add_displays,nil,'native crystal overlays are not doubled')
mode='blockout';T.apply(host)
eq(cell.replace_display.image,'checker-revised+tree0.png','crystal blockout wall')
mode='vanilla';T.apply(host)
eq(cell.replace_display,nil,'crystal vanilla restores native wall')
mode='refined';T.apply(host)
eq(cell.replace_display.image,'checker-revised+refined/crystal/wall-0-0.png','crystal refined round trip')
cell=newGrid(crystal('CRYSTAL_FLOOR3','floor'));T.apply(host)
eq(cell.replace_display.image,'checker-revised+refined/crystal/floor0.png','crystal floor')
host.zone={short_name='heart-gloom'};T.apply(host)
eq(cell.replace_display,nil,'underground subtype collision stays native outside crystal zone')
host.zone={short_name='deep-bellow'};mode='refined'
cell=newGrid(plainFloor);T.apply(host)
eq(cell.replace_display.image,'checker-revised+refined/gloom/plain/floor0.png','Deep Bellow plain floor')
mode='blockout';T.apply(host)
eq(cell.replace_display.image,'checker-revised+grass0.png','Deep Bellow blockout')
mode='vanilla';T.apply(host)
eq(cell.replace_display,nil,'Deep Bellow native restore')
mode='refined';T.apply(host)
local caveSource='/data/general/grids/cave.lua'
load(root..'../../modules/tome/data/general/grids/cave.lua',native)
for id,g in pairs(grids) do
 if type(id)=='string' and id:match('^CAVE') then T.markSource(g,caveSource) end
end
eq(T.caveTerrain(grids.CAVEFLOOR),'floor','native cave floor')
for i=1,18 do eq(T.caveTerrain(grids['CAVEFLOOR'..i]),'floor','native cave floor variant '..i) end
eq(T.caveTerrain(grids.CAVEWALL),'wall','native diggable cave wall')
eq(T.caveTerrain(grids.CAVE_LADDER_UP_WILDERNESS),'ladder-world','native cave world exit')
eq(T.caveTerrain(grids.CAVE_LADDER_UP),'ladder-up','native cave up ladder')
eq(T.caveTerrain(grids.CAVE_LADDER_DOWN),'ladder-down','native cave down ladder')
local caveChanged=copy(grids.CAVE_LADDER_DOWN);caveChanged.change_level=-1
eq(T.caveTerrain(caveChanged),nil,'changed cave ladder direction remains native')
local caveEdit=copy(grids.CAVEWALL)
caveEdit.image='terrain/cave/cave_V3_8_02.png'
caveEdit.add_displays={{image='invis.png'},{image='terrain/cave/cave_V3_inner_7_01.png',z=16}}
eq(T.caveTerrain(caveEdit),'wall','native cave NicerTiles art')
for _,mutation in ipairs{
 function(g) g._checker_cave_source=nil end,
 function(g) g.dig='OTHER' end,
 function(g) g.block_sight=false end,
 function(g) g.image='foreign.png' end,
 function(g) g.add_displays[2].image='object/chest3.png' end,
 function(g) g.replace_display=Entity.new{image='foreign.png'} end,
} do local g=copy(caveEdit);mutation(g);eq(T.caveTerrain(g),nil,'changed cave wall stays native') end
local caveChest=copy(grids.CAVEFLOOR)
caveChest.add_displays={{image='object/chest3.png'}}
eq(T.caveTerrain(caveChest),nil,'special cave floor remains native')
local caveExit=copy(grids.CAVE_LADDER_UP_WILDERNESS);caveExit.change_zone='other'
eq(T.caveTerrain(caveExit),nil,'changed cave destination remains native')
host.zone={short_name='unremarkable-cave',max_level=1};mode='refined'
cell=newGrid(grids.CAVEWALL);T.apply(host)
eq(cell.replace_display.image,'checker-revised+refined/cave/wall-0-0.png','cave refined wall')
mode='blockout';T.apply(host)
eq(cell.replace_display.image,'checker-revised+tree0.png','cave blockout wall')
mode='vanilla';T.apply(host)
eq(cell.replace_display,nil,'cave vanilla restores native wall')
mode='refined';T.apply(host)
eq(cell.replace_display.image,'checker-revised+refined/cave/wall-0-0.png','cave round trip')
cell=newGrid(grids.CAVEFLOOR8);T.apply(host)
eq(cell.replace_display.image,'checker-revised+refined/cave/floor-rock-1-0.png','cave rock decoration retained')
cell=newGrid(grids.CAVEFLOOR18);T.apply(host)
eq(cell.replace_display.image,'checker-revised+refined/cave/floor-mushroom-2-0.png','cave mushroom decoration retained')
host.zone={short_name='ardhungol',max_level=3};T.apply(host)
cell=newGrid(grids.CAVE_LADDER_UP);T.apply(host)
eq(cell.replace_display.image,'checker-revised+refined/cave/ladder-up0.png','Ardhungol up ladder')
cell=newGrid(grids.CAVE_LADDER_DOWN);T.apply(host)
eq(cell.replace_display.image,'checker-revised+refined/cave/ladder-down0.png','Ardhungol down ladder')
host.zone={short_name='other-cave',max_level=3};T.apply(host)
eq(cell.replace_display,nil,'cave suite remains zone gated')
host.zone={short_name='other-cave',max_level=1};T.apply(host)
eq(cell.replace_display,nil,'cave source cannot cross zone')
local lakeExit={define_as='OLD_FOREST',name='way to the old forest',image='terrain/grass.png',
 add_displays={{image='terrain/way_next_8.png'}},change_level=4,change_zone='old-forest',force_down=true,
 display='<',notice=true,always_remember=true}
eq(T.lakeExit(lakeExit),'exit','Lake of Nur exact Old Forest exit')
local changedLakeExit=copy(lakeExit);changedLakeExit.change_level_check=function() end
eq(T.lakeExit(changedLakeExit),nil,'Lake of Nur changed exit stays native')
eq(T.lakeExit({define_as='SHERTUL_FORTRESS_DRY',change_zone='shertul-fortress'}),nil,'Sher Tul gated exit stays native')
local waterSource='/data/general/grids/water.lua'
local waterFloor={define_as='WATER_FLOOR1',type='floor',subtype='underwater',name='underwater',
 image='terrain/underwater/subsea_floor_02a.png',air_level=-5,air_condition='water'}
local waterWall={define_as='WATER_WALL_NORTH1',type='wall',subtype='underwater',name='coral wall',
 image='terrain/underwater/subsea_granite_wall1_1.png',does_block_move=true,block_sight=true,
 air_level=-20,dig='WATER_FLOOR',can_pass={pass_wall=1}}
local waterDoor={define_as='WATER_DOOR',type='wall',subtype='underwater',name='door',
 image='terrain/underwater/subsea_stone_wall_door_closed.png',is_door=true,block_sight=true,
 air_level=-5,air_condition='water',door_opened='WATER_DOOR_OPEN',dig='WATER_FLOOR'}
for _,g in ipairs{waterFloor,waterWall,waterDoor} do T.markSource(g,waterSource) end
eq(T.underwaterKind(waterFloor),'floor','stamped underwater floor')
eq(T.underwaterKind(waterWall),'wall','stamped underwater blocking wall')
eq(T.underwaterKind(waterDoor),'door-closed','stamped underwater closed door')
local waterChanged=copy(waterFloor);waterChanged.air_condition=nil
eq(T.underwaterKind(waterChanged),nil,'changed air condition stays native')
waterChanged=copy(waterWall);waterChanged.block_sight=false
eq(T.underwaterKind(waterChanged),nil,'changed sight rule stays native')
waterChanged=copy(waterDoor);waterChanged.door_opened='OTHER'
eq(T.underwaterKind(waterChanged),nil,'changed door target stays native')
waterChanged=copy(waterWall);waterChanged.add_displays={{image='foreign.png'}}
eq(T.underwaterKind(waterChanged),nil,'foreign underwater wall layer native')
eq(T.underwaterKind({define_as='WATER_FLOOR',type='floor',subtype='underwater'}),nil,'unstamped underwater cell native')
-- S4/T1 flipped the bubble lock: exact native bubble (file+line) is board; see the S4 block.
eq(T.underwaterKind({define_as='WATER_FLOOR_BUBBLE',on_stand=function() end}),nil,'unstamped air bubble with a foreign callback native')
host.zone={short_name='lake-nur'};mode='refined'
host.level.level=2
cell=newGrid(copy(waterFloor));T.apply(host)
eq(cell.replace_display.image,'checker-revised+refined/underwater/floor0.png','underwater board floor')
cell=newGrid(copy(waterWall));T.apply(host)
eq(cell.replace_display.image,'checker-revised+refined/underwater/wall-0-0.png','underwater board wall')
mode='vanilla';T.apply(host);eq(cell.replace_display,nil,'underwater vanilla restores native')
mode='blockout';T.apply(host)
eq(cell.replace_display.image,'checker-revised+tree0.png','underwater blocked blockout')
mode='refined';host.level.level=3;host.zone.is_flooded=false
eq(T.variant(host.zone),'LAKE_NUR','Lake of Nur stone adapter registered')
cell=newGrid(copy(waterFloor));T.apply(host)
eq(cell.replace_display,nil,'dry L3 underwater floor remains native')
host.level.level=1
local surfaceSand={define_as='SAND',type='floor',subtype='sand',name='sand',
 image='terrain/sandfloor.png',display='.',grow='SANDWALL_STABLE'}
T.markSource(surfaceSand,'/data/general/grids/sand.lua')
eq(T.surfaceSandKind(surfaceSand),'surface-sand','source-stamped static lake sand')
cell=newGrid(copy(surfaceSand));T.apply(host)
eq(cell.replace_display.image,'checker-revised+refined/sand/floor0.png','Lake L1 surface sand board')
cell=newGrid(copy(waterWall));T.apply(host)
eq(cell.replace_display.image,'checker-revised+refined/underwater/wall-0-0.png','Lake L1 underwater wall board')
host.zone={short_name='temporal-rift'};host.level.level=4
cell=newGrid(copy(surfaceSand));T.apply(host)
eq(cell.replace_display.image,'checker-revised+refined/sand/floor0.png','Temporal Rift L4 shared sand board')
host.zone={short_name='lake-nur'};host.level.level=1
cell=newGrid(lakeExit);T.apply(host)
eq(cell.replace_display.image,'checker-revised+refined/exit0.png','Lake of Nur reviewed exit')
host.zone={short_name='golem-graveyard'};T.apply(host)
cell=newGrid{name='grass',subtype='grass',type='floor',define_as='GRASS'};T.apply(host)
eq(cell.replace_display.image,'checker-revised+refined/grass0.png','Golem Graveyard forest floor')
host.zone={short_name='last-hope-graveyard'};T.apply(host)
local graveSource='/data/zones/last-hope-graveyard/grids.lua'
local road={define_as='ROAD',type='floor',subtype='road',name='cobblestone road',image='terrain/stone_road1.png'}
local swamp={define_as='SWAMPTREE1',type='wall',subtype='grass',name='tree',image='terrain/grass.png',
 does_block_move=true,block_sight=true,dig='GRASS',can_pass={pass_tree=1}}
T.markSource(road,graveSource);T.markSource(swamp,graveSource)
eq(T.graveyardProp(road),'road','exact static graveyard road')
eq(T.graveyardProp(swamp),'swamp-tree','exact blocking swamp tree')
local tiledSwamp=copy(swamp);tiledSwamp.add_displays={{image='invis.png',add_mos={{image='terrain/grass/grass_7_01.png'}}}}
eq(T.graveyardProp(tiledSwamp),'swamp-tree','native swamp tree grass border')
cell=newGrid(copy(road));T.apply(host)
eq(cell.replace_display.image,'checker-revised+refined/korpul/floor-a-0-0.png','graveyard board cobblestone road')
cell=newGrid(copy(swamp));T.apply(host)
eq(cell.replace_display.image,'checker-revised+refined/tree-willow0.png','graveyard board tree')
local graveChanged=copy(swamp);graveChanged.dig=nil
eq(T.graveyardProp(graveChanged),nil,'changed swamp tree dig native')
graveChanged=copy(swamp);graveChanged.add_displays={{image='foreign.png'}}
eq(T.graveyardProp(graveChanged),nil,'foreign swamp tree overlay native')
eq(T.graveyardProp({define_as='GRAVE1',block_move=function() end}),nil,'lore grave callback native')
eq(T.graveyardProp({define_as='COFFIN',on_added=function() end}),nil,'coffin callback native')
local graveCallback=function() return true end
local coffinAdded=function() end
local coffinBlock=function() return true end
local props={
 {define_as='GRAVE1',type='wall',subtype='grass',name='grave',display='&',image='terrain/grass.png',
  does_block_move=true,pass_projectile=true,block_move=graveCallback,lore='last-hope-graveyard-1',
  add_displays={{z=18,display_y=-1,display_h=2,image='terrain/grave_unopened_01_64.png'}}},
 {define_as='COFFIN',type='floor',name='coffin',display='&',image='terrain/marble_floor.png',
  does_block_move=true,pass_projectile=true,force_clone=true,on_added=coffinAdded,block_move=coffinBlock,
  add_mos={{display_h=2,display_y=-1,image='terrain/coffin_unopened_01_64.png'}}},
 {define_as='COFFIN_OPEN',type='floor',name='open coffin',display='/',image='terrain/marble_floor.png',
  does_block_move=true,pass_projectile=true,
  add_mos={{display_h=2,display_y=-1,image='terrain/coffin_opened_01_64.png'}}},
 {define_as='MAUSOLEUM',type='floor',subtype='floor',name='open mausoleum',display='>',
  image='terrain/stone_road1.png',notice=true,always_remember=true,change_level=1,
  add_displays={{z=5,image='terrain/dungeon_entrance01.png'}}},
}
local propKinds={'grave','coffin','coffin-open','mausoleum'}
for i,prop in ipairs(props) do
 T.markSource(prop,graveSource)
 eq(T.graveyardProp(prop),propKinds[i],'exact graveyard prop '..i)
 local before={}
 for _,key in ipairs{'block_move','on_added','lore','change_level','does_block_move','pass_projectile','force_clone'} do before[key]=prop[key] end
 cell=newGrid(copy(prop));T.apply(host)
 eq(cell.replace_display.image,'checker-revised+refined/graveyard/'..propKinds[i]..'0.png','graveyard board prop '..i)
 for key,value in pairs(before) do eq(cell[key],value,'graveyard rule field '..key..' '..i) end
 mode='vanilla';T.apply(host);eq(cell.replace_display,nil,'graveyard native restore '..i);mode='refined'
 local altered=copy(prop);altered.image='foreign.png'
 eq(T.graveyardProp(altered),nil,'foreign graveyard art '..i)
 if prop.block_move then
  altered=copy(prop);altered.block_move=function() return true end
  eq(T.graveyardProp(altered),nil,'changed graveyard callback '..i)
 end
end
local floatingTree={define_as='BURNT_TREE1',type='wall',subtype='burnt',name='burnt tree',
 display='#',image='terrain/floating_rocks05_01.png',does_block_move=true,block_sight=true,
 always_remember=true,dig='BURNT_GROUND1',can_pass={pass_tree=1}}
T.markSource(floatingTree,'/data/general/grids/burntland.lua')
eq(T.abashedTreeKind(floatingTree),'rocks-tree','Abashed remapped static tree')
local changedFloating=copy(floatingTree);changedFloating.dig='OTHER'
eq(T.abashedTreeKind(changedFloating),nil,'Abashed changed tree dig native')
host.zone={short_name='abashed-expanse'};host.level.level=1
cell=newGrid(copy(floatingTree));T.apply(host)
eq(cell.replace_display.image,'checker-revised+refined/void/rocks-tree-0-0.png','Abashed board tree on rock')
host.zone={short_name='last-hope-graveyard'}
cell=newGrid{name='grass',subtype='grass',type='floor',define_as='GRASS_PATCH1',image='terrain/grass/grass_main_01.png'};T.apply(host)
eq(cell.replace_display.image,'checker-revised+refined/grass0.png','Last Hope Graveyard exact grass')
cell=newGrid{name='tree',subtype='grass',type='wall',define_as='SWAMPTREE1',does_block_move=true};T.apply(host)
eq(cell.replace_display,nil,'graveyard swamp tree remains native')
cell=newGrid{name='grave',subtype='grass',type='wall',define_as='GRAVE1',does_block_move=true};T.apply(host)
eq(cell.replace_display,nil,'graveyard grave remains native')
cell=newGrid{name='exit',subtype='grass',type='floor',define_as='GRASS_UP_WILDERNESS',image='terrain/grass.png',change_zone='other',change_level=1,notice=true,add_mos={{image='terrain/worldmap.png'}}};T.apply(host)
eq(cell.replace_display,nil,'changed graveyard world exit remains native')
host.zone={short_name='other-forest'};T.apply(host)
eq(cell.replace_display,nil,'forest gate remains scoped')
local burntFloor={define_as='BURNT_GROUND',type='floor',subtype='burnt',name='burnt ground',
 display='.',image='terrain/grass_burnt1.png'}
local burntTree={define_as='BURNT_TREE1',type='wall',subtype='burnt',name='burnt tree',
 display='#',image='terrain/grass_burnt1.png',does_block_move=true,block_sight=true,
 always_remember=true,can_pass={pass_tree=1},dig='BURNT_GROUND1'}
local burntLava={define_as='LAVA2',type='floor',subtype='molten_lava',name='molten lava',
 display='%',image='terrain/lava/molten_lava_5_02.png',does_block_move=true,
 pass_projectile=true,shader='lava'}
for _,g in ipairs{burntFloor,burntTree,burntLava} do
 T.markSource(g,g==burntLava and '/data/general/grids/lava.lua' or '/data/general/grids/burntland.lua')
end
eq(T.burntTerrain(burntFloor),'floor','burnt floor exact source')
eq(T.burntTerrain(burntTree),'tree','burnt diggable tree exact source')
eq(T.burntTerrain(burntLava),'lava','molten lava blocks movement without damage')
local altered=copy(burntLava);altered.on_stand=function() end
eq(T.burntTerrain(altered),nil,'damaging lava variant remains native')
altered=copy(burntTree);altered.dig=nil
eq(T.burntTerrain(altered),nil,'undiggable tree remains native')
altered=copy(burntFloor);altered.add_mos={{image='foreign.png'}}
eq(T.burntTerrain(altered),nil,'foreign floor decoration remains native')
host.zone={short_name='mark-spellblaze'};mode='refined'
cell=newGrid(burntFloor);T.apply(host)
eq(cell.replace_display.image,'checker-revised+refined/burnt/floor0.png','Spellblaze refined floor')
mode='blockout';T.apply(host)
eq(cell.replace_display.image,'checker-revised+grass0.png','Spellblaze blockout floor')
mode='vanilla';T.apply(host)
eq(cell.replace_display,nil,'Spellblaze vanilla restore')
mode='refined';T.apply(host)
eq(cell.replace_display.image,'checker-revised+refined/burnt/floor0.png','Spellblaze round trip')
host.zone={short_name='vor-pride'};T.apply(host)
eq(cell.replace_display,nil,'burntland reused elsewhere remains native')
local voidGrids={}
local voidEnv=setmetatable({newEntity=function(def)
 local g=def.base and copy(assert(voidGrids[def.base])) or {}
 for k,v in pairs(def) do g[k]=v end
 voidGrids[def.define_as]=g
end,colors={YELLOW={}}},{__index=_G})
load(root..'../../modules/tome/data/general/grids/void.lua',voidEnv)
for _,g in pairs(voidGrids) do T.markSource(g,'/data/general/grids/void.lua') end
eq(T.voidTerrain(voidGrids.VOID,'unhallowed-morass'),'floor','walkable void floor')
eq(T.voidTerrain(voidGrids.SPACETIME_RIFT,'temporal-rift'),'rift','blocked spacetime rift')
eq(T.voidTerrain(voidGrids.OUTERSPACE,'abashed-expanse'),'space','blocked outer space')
eq(T.voidTerrain(voidGrids.FLOATING_ROCKS_5,'abashed-expanse'),'rocks','walkable floating rock')
eq(T.voidTerrain(voidGrids.OUTERSPACE,'temporal-rift'),nil,'space stays scoped')
local voidAltered=copy(voidGrids.VOID);voidAltered.on_stand=function() end
eq(T.voidTerrain(voidAltered,'unhallowed-morass'),nil,'damaging void variant native')
voidAltered=copy(voidGrids.OUTERSPACE);voidAltered.does_block_move=nil
eq(T.voidTerrain(voidAltered,'abashed-expanse'),nil,'passable outer space variant native')
voidAltered=copy(voidGrids.FLOATING_ROCKS);voidAltered.define_as='WORMHOLE'
voidAltered.damage_project=function() end
eq(T.voidTerrain(voidAltered,'abashed-expanse'),nil,'wormhole callback native')
local morassRift=copy(voidGrids.SPACETIME_RIFT)
morassRift.block_sight=true
morassRift._checker_void_source=nil
T.markSource(morassRift,'/data/zones/unhallowed-morass/grids.lua')
eq(T.voidTerrain(morassRift,'unhallowed-morass'),'rift','morass sight blocking rift')
eq(T.voidTerrain(morassRift,'temporal-rift'),nil,'morass override scoped')
host.zone={short_name='unhallowed-morass'};mode='refined'
cell=newGrid(voidGrids.VOID);T.apply(host)
eq(cell.replace_display.image,'checker-revised+refined/void/floor0.png','void refined floor')
mode='blockout';T.apply(host)
eq(cell.replace_display.image,'checker-revised+grass0.png','void blockout floor')
mode='vanilla';T.apply(host)
eq(cell.replace_display,nil,'void vanilla restore')
mode='refined';T.apply(host)
eq(cell.replace_display.image,'checker-revised+refined/void/floor0.png','void mode round trip')
host.zone={short_name='other-zone'};T.apply(host)
eq(cell.replace_display,nil,'void family zone scoped')

-- Batch 4: Southern Beach, Tranquil Meadow, Dogroth Caldera, Murgol Lair, Conclave Vault.
local forestSrc,jungleSrc='/data/general/grids/forest.lua','/data/general/grids/jungle.lua'
local b4Tree={define_as='TREE1',type='wall',subtype='grass',name='tree',display='#',image='terrain/grass.png',
 always_remember=true,does_block_move=true,block_sight=true,dig='GRASS',can_pass={pass_tree=1},add_mos={},
 add_displays={{image='invis.png',add_mos={{image='terrain/trees/oak_trunk_01.png'}}},{image='terrain/trees/oak_foliage_summer_01.png'}}}
T.markSource(b4Tree,forestSrc)
eq(T.batch4Kind(b4Tree,'beach'),'tree','beach exact forest tree (native empty add_mos)')
local b4Changed=copy(b4Tree);b4Changed.dig=nil
eq(T.batch4Kind(b4Changed,'beach'),nil,'beach tree changed dig native')
b4Changed=copy(b4Tree);b4Changed.add_mos={{image='terrain/foreign.png'}}
eq(T.batch4Kind(b4Changed,'beach'),nil,'beach tree extra layer native')
b4Changed=copy(b4Tree);b4Changed.add_displays[2].image='terrain/foreign.png'
eq(T.batch4Kind(b4Changed,'beach'),nil,'beach tree foreign foliage native')
b4Changed=copy(b4Tree);b4Changed._checker_forest_source=nil
eq(T.batch4Kind(b4Changed,'beach'),nil,'unstamped tree native')
b4Changed=copy(b4Tree);b4Changed.subtype='dark_grass'
eq(T.batch4Kind(b4Changed,'beach'),nil,'tree subtype change native')
local umbrella={define_as='UMBRELLA',type='floor',subtype='sand',name='lovely umbrella',display='~',image='terrain/sandfloor.png',
 grow='SANDWALL_STABLE',does_block_move=true,add_mos={{image='terrain/picnic_umbrella.png'}}}
T.markSource(umbrella,'/data/zones/south-beach/grids.lua')
eq(T.batch4Kind(umbrella,'beach'),'umbrella','exact blocking parasol')
b4Changed=copy(umbrella);b4Changed.does_block_move=nil
eq(T.batch4Kind(b4Changed,'beach'),nil,'passable parasol variant native')
local basket={define_as='BASKET',type='floor',subtype='sand',name='picnic basket',display='_',image='terrain/sandfloor.png',
 grow='SANDWALL_STABLE',add_mos={{image='terrain/picnic_basket.png'}}}
T.markSource(basket,'/data/zones/south-beach/grids.lua')
eq(T.batch4Kind(basket,'beach'),'basket','exact passable basket')
local beachUp={define_as='BEACH_UP',change_level=1,change_level_check=function() end}
eq(T.batch4Kind(beachUp,'beach'),nil,'beach exit callback native')
host.zone={short_name='south-beach'};mode='refined'
cell=newGrid(copy(b4Tree));T.apply(host)
eq(cell.replace_display.image:match('^checker%-revised%+refined/beach/tree%-%a+0%.png$')~=nil,true,'beach board cell-filling tree')
cell=newGrid(copy(surfaceSand));T.apply(host)
eq(cell.replace_display.image,'checker-revised+refined/beach/sand0.png','beach board calm sand')
cell=newGrid(copy(umbrella));T.apply(host)
eq(cell.replace_display.image,'checker-revised+refined/beach/umbrella0.png','beach board parasol')
mode='blockout';T.apply(host);eq(cell.replace_display.image,'checker-revised+tree0.png','parasol blockout is blocking')
mode='vanilla';T.apply(host);eq(cell.replace_display,nil,'beach vanilla restore')
mode='refined';host.zone={short_name='other-zone'};cell=newGrid(copy(umbrella));T.apply(host)
eq(cell.replace_display,nil,'beach prop zone scoped')

local hardtree={define_as='HARDTREE3',type='wall',subtype='grass',name='tall thick tree',display='#',image='terrain/grass.png',
 always_remember=true,does_block_move=true,block_sight=true,block_sense=true,block_esp=true,
 add_displays={{image='terrain/trees/oak_foliage_summer_01.png'}}}
T.markSource(hardtree,forestSrc)
eq(T.batch4Kind(hardtree,'meadow'),'hardtree','meadow exact hard tree')
b4Changed=copy(hardtree);b4Changed.block_esp=nil
eq(T.batch4Kind(b4Changed,'meadow'),nil,'hard tree changed esp rule native')
local meadowMove=function() end
local meadowEvent={define_as='GRASS_MEADOW',type='floor',subtype='grass',name='grass',display='.',image='terrain/grass.png',on_move=meadowMove}
T.markSource(meadowEvent,'/data/zones/keepsake-meadow/grids.lua')
eq(T.batch4Kind(meadowEvent,'meadow'),'grass','story trigger keeps native on_move and draws as grass')
b4Changed=copy(meadowEvent);b4Changed.on_move=function() end
eq(T.batch4Kind(b4Changed,'meadow'),nil,'replaced story callback native')
b4Changed=copy(meadowEvent);b4Changed.on_stand=function() end
eq(T.batch4Kind(b4Changed,'meadow'),nil,'story trigger with added stand callback native')
local stew={define_as='STEW',type='wall',subtype='grass',name='troll stew',display='~',image='terrain/grass.png',
 does_block_move=true,pass_projectile=true,add_mos={{image='terrain/troll_stew.png'}}}
T.markSource(stew,'/data/zones/keepsake-meadow/grids.lua')
eq(T.batch4Kind(stew,'meadow'),'stew','exact troll stew')
b4Changed=copy(stew);b4Changed.pass_projectile=nil
eq(T.batch4Kind(b4Changed,'meadow'),nil,'stew projectile rule change native')
eq(T.batch4Kind({define_as='CAVEFLOOR_CAVE_MARKER',on_move=function() end},'meadow'),nil,'signpost callback native')
host.zone={short_name='keepsake-meadow'};cell=newGrid(copy(stew));T.apply(host)
eq(cell.replace_display.image,'checker-revised+refined/keepsake/stew0.png','meadow board stew')
cell=newGrid(copy(meadowEvent));T.apply(host)
eq(cell.on_move,meadowMove,'story trigger callback untouched')

local jungleTree={define_as='JUNGLE_TREE4',type='wall',subtype='grass',name='tree',display='#',always_remember=true,
 image='terrain/jungle/jungle_grass_floor_01.png',does_block_move=true,block_sight=true,dig='JUNGLE_GRASS',can_pass={pass_tree=1},
 add_displays={{image='terrain/jungle/jungle_tree_4.png'}}}
T.markSource(jungleTree,jungleSrc)
eq(T.batch4Kind(jungleTree,'caldera'),'tree','caldera exact jungle tree')
b4Changed=copy(jungleTree);b4Changed.can_pass={pass_tree=1,pass_wall=1}
eq(T.batch4Kind(b4Changed,'caldera'),nil,'jungle tree extra pass rule native')
local poisonStand,poisonAttack=function() end,function() end
local poison={define_as='POISON_DEEP_WATER2',type='floor',subtype='water',name='poisoned deep water',display='~',
 image='terrain/poisoned_water_02.png',always_remember=true,air_level=-5,air_condition='water',shader='water',
 on_stand=poisonStand,combatAttack=poisonAttack}
T.markSource(poison,waterSource)
eq(T.batch4Kind(poison,'caldera'),'poison','poison water with native hazard callbacks')
b4Changed=copy(poison);b4Changed.on_stand=function() end
eq(T.batch4Kind(b4Changed,'caldera'),nil,'replaced poison damage native')
b4Changed=copy(poison);b4Changed.combatAttack=function() end
eq(T.batch4Kind(b4Changed,'caldera'),nil,'replaced poison attack native')
b4Changed=copy(poison);b4Changed.image='terrain/poisoned_water_03.png'
eq(T.batch4Kind(b4Changed,'caldera'),nil,'poison image drift native')
eq(T.batch4Kind(copy(poison),'beach'),nil,'poison family scoped')
host.zone={short_name='noxious-caldera'};cell=newGrid(copy(poison));T.apply(host)
eq(cell.replace_display.image,'checker-revised+refined/caldera/poison-0-0.png','caldera board poison')
eq(cell.on_stand,poisonStand,'poison damage callback untouched')
cell=newGrid(copy(jungleTree));T.apply(host)
eq(cell.replace_display.image:match('^checker%-revised%+refined/caldera/tree%-[abc]0%.png$')~=nil,true,'caldera board tree')
mode='vanilla';T.apply(host);eq(cell.replace_display,nil,'caldera vanilla restore')
mode='refined'

local murgolExit={define_as='WATER_UP_WILDERNESS',type='floor',subtype='water',name='exit to the worldmap',display='<',
 image='terrain/underwater/subsea_floor_02.png',add_mos={{image='terrain/underwater/subsea_stair_up_wild.png'}},
 always_remember=true,notice=true,change_level=1,change_zone='wilderness',air_level=-5,air_condition='water'}
T.markSource(murgolExit,waterSource)
eq(T.underwaterKind(murgolExit),'stairs-world','Murgol exact world exit')
b4Changed=copy(murgolExit);b4Changed.change_level_check=function() end
eq(T.underwaterKind(b4Changed),nil,'checked world exit native')
b4Changed=copy(murgolExit);b4Changed.change_zone='other'
eq(T.underwaterKind(b4Changed),nil,'world exit destination drift native')
host.zone={short_name='murgol-lair'};cell=newGrid(copy(murgolExit));T.apply(host)
eq(cell.replace_display.image,'checker-revised+refined/underwater/stairs-world0.png','Murgol board world exit')

local conclaveSrc='/data/zones/conclave-vault/grids.lua'
local rune={define_as='RUNE_FLOOR2',type='floor',subtype='floor',name='floor',image='terrain/marble_floor.png',display='.',
 add_displays={{image='terrain/ruins/floor_rune_02.png',z=3}}}
T.markSource(rune,conclaveSrc)
eq(T.classify(rune),'deco-floor','Conclave exact decorated floor')
b4Changed=copy(rune);b4Changed.add_displays[1].image='terrain/ruins/floor_other.png'
eq(T.classify(b4Changed),nil,'Conclave decoration drift native')
b4Changed=copy(rune);b4Changed.on_move=function() end
eq(T.classify(b4Changed),nil,'Conclave floor callback native')
eq(T.variant({short_name='conclave-vault'}),'CONCLAVE_VAULT','Conclave stone adapter registered')

;(function()
-- Batch 5: Charred Scar / Fearscape lava, Sher'Tul Fortress, reuse gates.
local b5grids={}
local b5mod
local b5native=setmetatable({class=Entity,colors=setmetatable({},{__index=function() return {} end}),_t=function(v) return v end,
 resolvers={mbonus=function(v) return v end},engine={DamageType={FIRE='FIRE'}}},{__index=_G})
b5native.newEntity=function(t)
 local g=t.base and copy(assert(b5grids[t.base])) or {}
 for k,v in pairs(t) do g[k]=v end
 g.tint_r=g.tint_r or 1;g.tint_g=g.tint_g or 1;g.tint_b=g.tint_b or 1
 if b5mod then b5mod(g) end
 b5grids[t.define_as]=g
end
local lavaFile,fortressFile='/data/general/grids/lava.lua','/data/general/grids/fortress.lua'
-- Charred Scar / demon plane grids.lua: load(lava.lua, function(e) if LAVA_FLOOR then on_stand=nil end)
b5mod=function(e) if e.define_as=='LAVA_FLOOR' then e.on_stand=nil end end
load(root..'../../modules/tome/data/general/grids/lava.lua',b5native)
b5mod=nil
for id,g in pairs(b5grids) do T.markSource(g,lavaFile) end
local harmless=copy(b5grids.LAVA_FLOOR7);harmless.add_displays={{image='invis.png',add_mos={{image='terrain/lava/lava_floor_inner_1_02.png'}}}}
eq(T.batch5Kind(harmless,'scorch'),'lava-floor','harmless zone lava floor (native border layer)')
eq(T.batch5Kind(copy(b5grids.LAVA_FLOOR),'scorch'),'lava-floor','harmless base lava floor')
local burning=copy(b5grids.LAVA_FLOOR3);burning.on_stand=function() end
eq(T.batch5Kind(burning,'scorch'),nil,'damaging lava floor (Vor Armoury copy) native')
local unstamped=copy(b5grids.LAVA_FLOOR3);unstamped._checker_burnt_source=nil
eq(T.batch5Kind(unstamped,'scorch'),nil,'unstamped lava floor native')
for _,id in ipairs{'LAVA_WALL','LAVA_WALL1','LAVA_WALL6'} do eq(T.batch5Kind(copy(b5grids[id]),'scorch'),'lava-wall','exact lava wall '..id) end
local lw=copy(b5grids.LAVA_WALL2);lw.add_displays={{image='invis.png',add_mos={{image='terrain/lava/lava_mountain5_2.png'}}},{image='terrain/lava/lava_mountain8.png',z=18,display_y=-1}}
eq(T.batch5Kind(lw,'scorch'),'lava-wall','lava wall with native nice-editer layers')
local lwc=copy(lw);lwc.add_displays[2].image='terrain/foreign.png'
eq(T.batch5Kind(lwc,'scorch'),nil,'lava wall foreign layer native')
lwc=copy(b5grids.LAVA_WALL);lwc.dig='LAVA_FLOOR'
eq(T.batch5Kind(lwc,'scorch'),nil,'diggable lava wall variant native')
lwc=copy(b5grids.LAVA_WALL);lwc.image='terrain/lava/lava_mountain5_3.png'
eq(T.batch5Kind(lwc,'scorch'),nil,'lava wall image/id drift native')
lwc=copy(b5grids.LAVA_WALL);lwc.block_sight=nil
eq(T.batch5Kind(lwc,'scorch'),nil,'lava wall sight rule change native')
eq(T.batch5Kind(copy(b5grids.LAVA),'scorch'),'lava','exact molten lava')
eq(T.batch5Kind(copy(b5grids.LAVA),'shertul'),nil,'lava family scoped')
for _,id in ipairs{'LAVA_LADDER_DOWN','LAVA_LADDER_UP_WILDERNESS'} do eq(T.batch5Kind(copy(b5grids[id]),'scorch'),nil,'lava ladder not in scope '..id) end
b5grids={}
load(root..'../../modules/tome/data/general/grids/fortress.lua',b5native)
for id,g in pairs(b5grids) do T.markSource(g,fortressFile) end
eq(T.batch5Kind(copy(b5grids.SOLID_FLOOR),'shertul'),'floor','exact Sher\'Tul floor')
for _,id in ipairs{'SOLID_WALL','SOLID_WALL1','SOLID_WALL_NORTH1','SOLID_WALL_PILLAR_81','SOLID_WALL_PILLAR_2','SOLID_WALL_NORTH_SOUTH','SOLID_WALL_SOUTH','SOLID_WALL_SOUTH4'} do
 eq(T.batch5Kind(copy(b5grids[id]),'shertul'),'wall','exact Sher\'Tul wall '..id)
end
for _,id in ipairs{'SOLID_DOOR','SOLID_DOOR_OPEN','SOLID_DOOR_SEALED','SOLID_DOOR_SEALED_VERT','SOLID_VAULTDOOR','SOLID_DOOR_HORIZ'} do
 eq(T.batch5Kind(copy(b5grids[id]),'shertul'),nil,'fortress door native '..id)
end
local fw=copy(b5grids.SOLID_WALL_NORTH1);fw.add_displays[1].image='terrain/foreign.png'
eq(T.batch5Kind(fw,'shertul'),nil,'fortress wall foreign cap native')
fw=copy(b5grids.SOLID_WALL);fw.block_move=function() return true end
eq(T.batch5Kind(fw,'shertul'),nil,'fortress wall callback native (mural pattern)')
fw=copy(b5grids.SOLID_FLOOR);fw.on_move=function() end
eq(T.batch5Kind(fw,'shertul'),nil,'fortress floor with on_move (farportal pattern) native')
fw=copy(b5grids.SOLID_FLOOR);fw.change_level=1;fw.change_zone='wilderness'
eq(T.batch5Kind(fw,'shertul'),nil,'fortress teleport circle native')
fw=copy(b5grids.SOLID_FLOOR);fw.image='terrain/solidwall/solid_floor2.png'
eq(T.batch5Kind(fw,'shertul'),nil,'fortress floor image drift native')
host.zone={short_name='shertul-fortress'};host.level.level=1;mode='refined'
cell=newGrid(copy(b5grids.SOLID_FLOOR));T.apply(host)
eq(cell.replace_display.image,'checker-revised+refined/shertul/floor0.png','Sher\'Tul board floor')
cell=newGrid(copy(b5grids.SOLID_WALL));T.apply(host)
eq(cell.replace_display.image,'checker-revised+refined/shertul/wall-0-0.png','Sher\'Tul board wall')
mode='blockout';T.apply(host);eq(cell.replace_display.image,'checker-revised+tree0.png','Sher\'Tul wall blockout blocking')
mode='vanilla';T.apply(host);eq(cell.replace_display,nil,'Sher\'Tul vanilla restore')
mode='refined';host.zone={short_name='other-zone'};cell=newGrid(copy(b5grids.SOLID_FLOOR));T.apply(host)
eq(cell.replace_display,nil,'Sher\'Tul family zone scoped')

-- Rak'Shor Pride (bone.lua): only callback-free cells whose definition had no
-- callbacks; levers, lever doors, sealed vault doors and event cells native.
local boneFile='/data/general/grids/bone.lua'
b5grids={}
load(root..'../../modules/tome/data/general/grids/bone.lua',b5native)
for id,g in pairs(b5grids) do T.markSource(g,boneFile) end
local function bone(id) return copy(b5grids[id]) end
eq(T.batch5Kind(bone('BONEFLOOR'),'rakshor'),'floor','exact bone-zone sand floor')
local bf=bone('BONEFLOOR');bf.add_displays={{image='invis.png',add_mos={{image='terrain/sand/sand_2_1.png'}}}}
eq(T.batch5Kind(bf,'rakshor'),'floor','bone floor with native sand border layer')
for _,id in ipairs{'BONEWALL','BONEWALL1','BONEWALL6','HARDBONEWALL','HARDBONEWALL4'} do
 eq(T.batch5Kind(bone(id),'rakshor'),'wall','exact bone wall '..id)
end
local bw=bone('BONEWALL3');bw.image='terrain/bone/bone_floor_1_01.png'
bw.add_displays={{image='invis.png',add_mos={{image='terrain/bone/bone_V3_inner_7_01.png'}}},{image='terrain/bone/bonewall_8_1.png',z=16,display_y=-1},{image='terrain/bone/bone_ver_edge_left_01.png',display_x=-1}}
eq(T.batch5Kind(bw,'rakshor'),'wall','bone wall with native nice-editer layers')
local bx=copy(bw);bx.add_displays[2].image='terrain/foreign.png'
eq(T.batch5Kind(bx,'rakshor'),nil,'bone wall foreign layer native')
bx=bone('BONEWALL');bx.on_stand=function() end
eq(T.batch5Kind(bx,'rakshor'),nil,'bone wall with a foreign on_stand native')
bx=bone('BONEFLOOR');bx.on_stand=function() end;bx.name='sand (whistling vortex)'
eq(T.batch5Kind(bx,'rakshor'),nil,'renamed bone floor with a foreign on_stand native')
bx=bone('BONEFLOOR');bx.block_move=function() return true end
eq(T.batch5Kind(bx,'rakshor'),nil,'bone floor block_move native')
bx=bone('BONEFLOOR');bx.change_level_check=function() end;bx.real_change=function() end;bx.change_level=1
eq(T.batch5Kind(bx,'rakshor'),nil,'hidden vault trigger floor native')
bx=bone('BONEFLOOR');bx._checker_bone_source.functions='on_stand'
eq(T.batch5Kind(bx,'rakshor'),nil,'definition with callbacks never accepted')
bx=bone('BONEFLOOR');bx._checker_bone_source=nil
eq(T.batch5Kind(bx,'rakshor'),nil,'unstamped bone floor native')
bx=bone('BONEWALL');bx.dig=nil
eq(T.batch5Kind(bx,'rakshor'),nil,'bone wall dig rule drift native')
bx=bone('HARDBONEWALL');bx.block_esp=nil
eq(T.batch5Kind(bx,'rakshor'),nil,'hard bone wall rule drift native')
for id,k in pairs{BONE_DOOR='door-closed',BONE_DOOR_HORIZ='door-closed',BONE_DOOR_VERT='door-closed',
 BONE_DOOR_OPEN='door-open',BONE_DOOR_HORIZ_OPEN='door-open',BONE_DOOR_OPEN_VERT='door-open',
 BONE_LADDER_UP='stairs-up',BONE_LADDER_DOWN='stairs-down',BONE_LADDER_UP_WILDERNESS='stairs-exit',BONE_UP_WILDERNESS='exit-world'} do
 eq(T.batch5Kind(bone(id),'rakshor'),k,'exact bone '..id)
end
-- S2/T4: sealed bone vault doors (flipped): board door art, plus the rules
-- that make them sealed (sense/ESP block, the definition's own prompt).
for id,k in pairs{BONE_VAULT_DOOR='door-closed',BONE_VAULT_DOOR_HORIZ='door-closed',BONE_VAULT_DOOR_VERT='door-closed',
 BONE_VAULT_DOOR_OPEN='door-open',BONE_VAULT_DOOR_HORIZ_OPEN='door-open',BONE_VAULT_DOOR_OPEN_VERT='door-open'} do
 eq(T.batch5Kind(bone(id),'rakshor'),k,'S2 exact bone vault door '..id)
 eq(T.batch5Kind(bone(id),'scorch'),nil,'S2 bone vault door is Rak\'shor only '..id)
end
for _,id in ipairs{'BONE_VAULT_DOOR','BONE_VAULT_DOOR_HORIZ','BONE_VAULT_DOOR_VERT'} do
 for label,m in pairs{prompt=function(g) g.door_player_check='Other.' end,noprompt=function(g) g.door_player_check=nil end,
  sense=function(g) g.block_sense=nil end,esp=function(g) g.block_esp=nil end,sight=function(g) g.block_sight=nil end,
  opened=function(g) g.door_opened='BONE_DOOR_OPEN' end,dig=function(g) g.dig=nil end,move=function(g) g.does_block_move=true end,
  stamp=function(g) g._checker_bone_source=nil end,callback=function(g) g.block_move=function() return true end end,
  stop=function(g) g.door_player_stop='Stop.' end,image=function(g) g.image='terrain/bone/bone_floor_1_01.png' end} do
  local c=bone(id);m(c)
  eq(T.batch5Kind(c,'rakshor'),nil,'S2 altered bone vault door '..id..' '..label)
 end
end
local bdp=bone('BONE_DOOR');bdp.door_player_check='This door seems to have been sealed off. You think you can open it.'
eq(T.batch5Kind(bdp,'rakshor'),nil,'S2 prompt on a plain bone door stays native')
local bvo=bone('BONE_VAULT_DOOR_OPEN');bvo.door_closed='BONE_DOOR'
eq(T.batch5Kind(bvo,'rakshor'),nil,'S2 bone vault open door closing into another door stays native')
-- S11: the placed bone lever and lever doors are exact S11 cells (tests/terrain_s11.lua).
for _,id in ipairs{
 'BONE_GENERIC_LEVER_DOOR','BONE_GENERIC_LEVER_DOOR_OPEN',
 'BONE_GENERIC_LEVER_DOOR_HORIZ_OPEN','BONE_GENERIC_LEVER_DOOR_OPEN_VERT','BONE_UP8','BONE_DOWN6'} do
 eq(T.batch5Kind(bone(id),'rakshor'),nil,'bone special stays native '..id)
end
bx=bone('BONE_DOOR_VERT');bx.on_stand=function() end
eq(T.batch5Kind(bx,'rakshor'),nil,'bone door with a foreign callback native')
bx=bone('BONE_DOOR_HORIZ');bx.add_mos[1].add_mos={{image='terrain/padlock2.png'}}
eq(T.batch5Kind(bx,'rakshor'),nil,'padlocked bone door native')
bx=bone('BONE_LADDER_DOWN');bx.change_level=2
eq(T.batch5Kind(bx,'rakshor'),nil,'bone ladder destination drift native')
bx=bone('BONE_LADDER_DOWN');bx.add_displays={{image='invis.png',add_mos={{image='terrain/sand/sand_8_1.png'}}},bx.add_displays[1]}
eq(T.batch5Kind(bx,'rakshor'),'stairs-down','bone ladder with native sand border layer')
eq(T.batch5Kind(bone('BONEWALL'),'shertul'),nil,'bone family scoped')
-- Engine Grid methods live on the class (metatable), not on the instance.
local methods={removeAllMOs=function() end}
methods.clone=function(self) local g={};for k,v in pairs(self) do g[k]=v end;return setmetatable(g,getmetatable(self)) end
local function newBone(t) return setmetatable(t,{__index=methods}) end
host.zone={short_name='rak-shor-pride'};host.level.level=2;mode='refined'
cell=newBone(bone('BONEFLOOR'));T.apply(host)
eq(cell.replace_display.image,'checker-revised+refined/rakshor/floor0.png','Rak\'Shor board floor')
cell=newBone(bone('BONEWALL2'));T.apply(host)
eq(cell.replace_display.image,'checker-revised+refined/rakshor/wall-0-0.png','Rak\'Shor board wall')
mode='blockout';T.apply(host);eq(cell.replace_display.image,'checker-revised+tree0.png','Rak\'Shor wall blockout blocking')
mode='vanilla';T.apply(host);eq(cell.replace_display,nil,'Rak\'Shor vanilla restore')
mode='refined';cell=newBone(bone('BONE_DOOR_VERT'));T.apply(host)
eq(cell.replace_display.image,'checker-revised+refined/rakshor/door-closed0.png','Rak\'Shor board door')
-- S11: Rak'Shor's lever is drawn by the S11 contract (tests/terrain_s11.lua).
host.zone={short_name='other-zone'};cell=newBone(bone('BONEFLOOR'));T.apply(host)
eq(cell.replace_display,nil,'Rak\'Shor family zone scoped')
eq(T.variant({short_name='rak-shor-pride'}),nil,'no stone adapter in Rak\'Shor')
eq(T.variant({short_name='shertul-fortress'}),'SHERTUL','fortress outer stone adapter registered')
for z,v in pairs{telmur='TELMUR',['ancient-elven-ruins']='ELVEN_RUINS',['vor-armoury']='VOR_ARMOURY',['orc-breeding-pit']='ORC_PIT',['charred-scar']='CHARRED_SCAR'} do
 eq(T.variant({short_name=z}),v,'batch 5 stone adapter '..z)
end
for _,z in ipairs{'orc-breeding-pit','charred-scar','shertul-fortress'} do eq(T.combined[z],true,'combined family zone '..z) end
eq(T.variant({short_name='illusory-castle'}),nil,'unreachable Illusory Castle not registered')
local valley={define_as='UP_VALLEY',name='exit to the lost valley',display='<',image='terrain/cave/cave_floor_1_01.png',
 add_mos={{image='terrain/cave/cave_stairs_up_2_01.png'}},always_remember=true,notice=true,change_level=3,change_zone='valley-moon'}
T.markSource(valley,'/data/zones/valley-moon-caverns/grids.lua')
eq(T.valleyExit(valley),'ladder-up','exact valley exit')
local vc=copy(valley);vc.change_level_check=function() end
eq(T.valleyExit(vc),nil,'checked valley exit native')
vc=copy(valley);vc.change_zone='other'
eq(T.valleyExit(vc),nil,'valley exit destination drift native')
vc=copy(valley);vc._checker_valley_source=nil
eq(T.valleyExit(vc),nil,'unstamped valley exit native')
host.zone={short_name='valley-moon-caverns'};host.level.level=2;cell=newGrid(copy(valley));T.apply(host)
eq(cell.replace_display.image,'checker-revised+refined/cave/ladder-up0.png','valley exit board ladder')
host.zone={short_name='ardhungol'};cell=newGrid(copy(valley));T.apply(host)
eq(cell.replace_display,nil,'valley exit scoped to its zone')
host.zone={short_name='charred-scar'};cell=newGrid(copy(lw));T.apply(host)
eq(cell.replace_display.image,'checker-revised+refined/scorch/wall-0-0.png','Charred Scar board lava wall')
host.zone={short_name='demon-plane'};cell=newGrid(copy(harmless));T.apply(host)
eq(cell.replace_display.image,'checker-revised+refined/daikara/lava-floor0.png','Fearscape board lava floor')
-- S8 (V7): the Fearscape rock draws the dark basalt when its manifest is
-- installed; the Charred Scar keeps the ash rock.
do
 local savedScorch=T.scorchDarkAssets
 T.scorchDarkAssets={ready=true,files=setmetatable({},{__index=function(_,k) return type(k)=='string' and k:match('^checker%-revised%+refined/scorch%-dark/') and true or nil end})}
 host.zone={short_name='demon-plane'};cell=newGrid(copy(lw));T.apply(host)
 eq(cell.replace_display.image,'checker-revised+refined/scorch-dark/wall-0-0.png','S8 Fearscape rock is dark basalt')
 eq(cell.does_block_move,lw.does_block_move,'S8 Fearscape rock rules untouched')
 host.zone={short_name='charred-scar'};cell=newGrid(copy(lw));T.apply(host)
 eq(cell.replace_display.image,'checker-revised+refined/scorch/wall-0-0.png','S8 Charred Scar keeps the ash rock')
 T.scorchDarkAssets={ready=false,files={}}
 host.zone={short_name='demon-plane'};cell=newGrid(copy(lw));T.apply(host)
 eq(cell.replace_display.image,'checker-revised+refined/scorch/wall-0-0.png','S8 no basalt manifest keeps the ash rock')
 T.scorchDarkAssets=savedScorch
end
host.zone={short_name='vor-armoury'};cell=newGrid(copy(harmless));T.apply(host)
eq(cell.replace_display,nil,'Vor Armoury lava not in the scorch family')
local pitWall={define_as='UNDERGROUND_TREE',type='wall',subtype='underground',name='underground thick vegetation',
 image='terrain/mushrooms/gloomy_underground_floor.png',does_block_move=true,block_sight=true,dig='UNDERGROUND_FLOOR',can_pass={pass_tree=1},
 _checker_gloom_source={file='/data/general/grids/underground_gloomy.lua',id='UNDERGROUND_TREE',skin='gloomy'}}
host.zone={short_name='orc-breeding-pit'};host.level.level=2;cell=newGrid(copy(pitWall));T.apply(host)
eq(cell.replace_display.image,'checker-revised+refined/gloom/pit/wall-0-0.png','Orc pit darker wall copy')
host.zone={short_name='deep-bellow'};cell=newGrid(copy(pitWall));T.apply(host)
eq(cell.replace_display.image,'checker-revised+refined/gloom/plain/wall-0-0.png','Deep Bellow keeps plain wall')
local pitFloor={define_as='UNDERGROUND_FLOOR',type='floor',subtype='underground',name='floor',
 image='terrain/mushrooms/gloomy_underground_floor.png',
 _checker_gloom_source={file='/data/general/grids/underground_gloomy.lua',id='UNDERGROUND_FLOOR',skin='gloomy'}}
local pitLadder={define_as='UNDERGROUND_LADDER_UP',type='floor',subtype='underground',name='ladder to the previous level',
 image='terrain/mushrooms/gloomy_underground_floor.png',add_displays={{image='terrain/ladder_up.png'}},
 notice=true,always_remember=true,change_level=-1,
 _checker_gloom_source={file='/data/general/grids/underground_gloomy.lua',id='UNDERGROUND_LADDER_UP',skin='gloomy'}}
host.zone={short_name='orc-breeding-pit'};cell=newGrid(copy(pitFloor));T.apply(host)
eq(cell.replace_display.image,'checker-revised+refined/gloom/pit/floor0.png','Orc pit calm pale floor')
cell=newGrid(copy(pitLadder));T.apply(host)
eq(cell.replace_display.image,'checker-revised+refined/gloom/pit/ladder-up0.png','Orc pit ladder on pit floor')
host.zone={short_name='deep-bellow'};cell=newGrid(copy(pitFloor));T.apply(host)
eq(cell.replace_display.image,'checker-revised+refined/gloom/plain/floor0.png','Deep Bellow keeps plain floor')
cell=newGrid(copy(pitLadder));T.apply(host)
eq(cell.replace_display.image,'checker-revised+refined/gloom/plain/ladder-up0.png','Deep Bellow keeps plain ladder')
host.zone={short_name='orc-breeding-pit'};host.level.level=1;cell=newGrid(copy(pitWall));T.apply(host)
eq(cell.replace_display,nil,'Orc pit L1 is stone only')
host.zone={short_name='orc-breeding-pit'};host.level.level=1;host.checker_mode='refined'
cell=newGrid(copy(grids.FLOOR));T.repair(host)
eq(host.checker_mode,'refined','combined level without forest grids keeps stone mode after repair')
eq(cell.replace_display,nil,'stone floor untouched by forest pass')
host.zone={short_name='trollmire'};host.level.level=nil;host.checker_mode=nil
end)()
;(function()
-- S3/E8: Old Forest CRYSTALINE crystal patches. crystal.lua definitions carry
-- the crystaline-forest event origin (Grid.lua loadList caller stamp); rerolled
-- floors may come from the zone's own crystal.lua import. Forest stays primary.
local crystalSource='/data/general/grids/crystal.lua'
local function fresh(id) local g=copy(grids[id]);T.markSource(g,crystalSource);return g end
local function event(id) local g=fresh(id);T.markCrystalOrigin(g,'crystaline-forest');return g end
local function zoneCopy(id) local g=fresh(id);T.markSource(g,'/data/zones/old-forest/grids.lua');return g end
-- The real superload: only the native event file's underground.lua call is stamped.
local Base={}
function Base:loadList(file,no_default,res)
 res=res or {}
 if file=='/data/general/grids/underground.lua' then
  for _,id in ipairs{'CRYSTAL_WALL7','CRYSTAL_FLOOR3','CRYSTAL_LADDER_DOWN'} do
   local g=copy(grids[id]);T.markSource(g,crystalSource);res[#res+1]=g;res[id]=g
  end
 end
 return res
end
local genv=setmetatable({loadPrevious=function() return Base end},{__index=env})
local GridSuper=load(root..'superload/mod/class/Grid.lua',genv)
local function viaChunk(name)
 local f=assert(loadstring('local G=...;local list=G:loadList("/data/general/grids/underground.lua");return list',name))
 return f(GridSuper)
end
local evList=viaChunk('@/data/general/events/crystaline-forest.lua')
eq(evList.CRYSTAL_WALL7._checker_crystal_source.origin,'crystaline-forest','event loadList stamps crystal wall origin')
eq(evList.CRYSTAL_FLOOR3._checker_crystal_source.origin,'crystaline-forest','event loadList stamps crystal floor origin')
eq(T.oldForestCrystal(evList.CRYSTAL_WALL7),'wall','event-stamped native wall is an Old Forest patch wall')
eq(T.oldForestCrystal(evList.CRYSTAL_LADDER_DOWN),nil,'event list ladder is never a patch cell')
local otherList=viaChunk('@/data/general/events/other-event.lua')
eq(otherList.CRYSTAL_WALL7._checker_crystal_source.origin,nil,'foreign caller does not stamp crystal origin')
local addonList=viaChunk('@/data-other/general/events/crystaline-forest.lua')
eq(addonList.CRYSTAL_WALL7._checker_crystal_source.origin,nil,'overridden addon event is not the native source')
eq(T.oldForestCrystal(otherList.CRYSTAL_WALL7),nil,'crystal wall outside the event source stays native')
eq(T.oldForestCrystal(fresh('CRYSTAL_FLOOR2')),nil,'plain crystal.lua floor has no Old Forest origin')
eq(T.oldForestCrystal(zoneCopy('CRYSTAL_FLOOR2')),'floor','zone reroll floor accepted')
eq(T.oldForestCrystal(zoneCopy('CRYSTAL_WALL9')),nil,'zone-list wall is never an event patch wall')
local zoneThenEvent=zoneCopy('CRYSTAL_FLOOR4');T.markCrystalOrigin(zoneThenEvent,'crystaline-forest')
eq(T.oldForestCrystal(zoneThenEvent),'floor','origin overwrite keeps floor kind')
for label,mutate in pairs{
 dig=function(g) g.dig=nil end,
 sight=function(g) g.block_sight=false end,
 move=function(g) g.does_block_move=false end,
 pass=function(g) g.can_pass={pass_wall=2} end,
 stand=function(g) g.on_stand=function() end end,
 layer=function(g) g.add_displays[1].image='foreign.png' end,
 mos=function(g) g.add_mos={{image='terrain/grass/grass_2_01.png'}} end,
 level=function(g) g.change_level=1 end,
 source=function(g) g._checker_crystal_source=nil end,
 id=function(g) g.define_as='CRYSTAL_WALL3' end,
} do
 local g=event('CRYSTAL_WALL7');mutate(g)
 eq(T.oldForestCrystal(g),nil,'altered event crystal wall stays native: '..label)
end
for label,mutate in pairs{
 grass=function(g) g.subtype='grass' end,
 block=function(g) g.does_block_move=true end,
 exit=function(g) g.change_zone='lake-nur' end,
 image=function(g) g.image='terrain/grass.png' end,
 aura=function(g) g.on_stand=assert(loadstring('return function() end','@/data/general/events/antimagic-bush.lua'))() end,
} do
 local g=event('CRYSTAL_FLOOR5');mutate(g)
 eq(T.oldForestCrystal(g),nil,'altered event crystal floor stays native: '..label)
end
-- Map composition: tree | crystal wall | crystal wall | crystal floor | grass
local cells={}
local function mk(t) t.removeAllMOs=function() end;t.clone=function(self) local g={};for k,v in pairs(self) do g[k]=v end;return g end;return t end
local function reset()
 cells[0]=mk{name='tree',subtype='grass',type='wall',does_block_move=true,block_sight=true,dig='GRASS',can_pass={pass_tree=1}}
 cells[1]=mk(event('CRYSTAL_WALL7'));cells[2]=mk(event('CRYSTAL_WALL12'))
 cells[3]=mk(zoneCopy('CRYSTAL_FLOOR6'));cells[4]=mk{name='grass',subtype='grass',type='floor',define_as='GRASS'}
 cells[5]=copy(grids.FLOOR)
end
reset()
local strip=setmetatable({w=6,h=1,seens=function() return true end,infovs=function() return true end,remembers=function() return true end},
 {__call=function(_,cx,cy,layer,value) if cy~=0 or cx<0 or cx>5 then return end;if value then cells[cx]=value end;return cells[cx] end})
function strip:updateMap() end
local h={zone={short_name='old-forest',is_crystaline=true},level={map=strip,level=2}}
mode='refined';T.apply(h)
eq(cells[0].replace_display.image,'checker-revised+refined/tree-oak0.png','forest tree stays primary at patch boundary')
eq(cells[1].replace_display.image,'checker-revised+refined/crystal/wall-2-1.png','boundary crystal wall joins only its crystal neighbour')
eq(cells[2].replace_display.image,'checker-revised+refined/crystal/wall-8-0.png','inner crystal wall mask ignores floor')
eq(cells[2].replace_display.add_displays,nil,'native makeCrystals layers are not doubled')
eq(cells[3].replace_display.image,'checker-revised+refined/crystal/floor1.png','patch floor uses crystal family')
eq(cells[4].replace_display.image,'checker-revised+refined/grass0.png','forest grass beside patch')
eq(cells[5].replace_display,nil,'basic.lua stone room floor is left to the stone adapter')
eq(cells[1].does_block_move,true,'crystal wall movement rule untouched');eq(cells[1].block_sight,true,'crystal wall sight rule untouched')
eq(cells[1].dig,'CRYSTAL_FLOOR','crystal wall dig target untouched')
eq(cells[3].does_block_move,nil,'crystal floor passability untouched')
mode='blockout';T.apply(h)
eq(cells[1].replace_display.image,'checker-revised+tree1.png','patch wall blockout reads as blocking')
eq(cells[3].replace_display.image,'checker-revised+grass1.png','patch floor blockout reads as floor')
mode='vanilla';T.apply(h)
for x=0,4 do eq(cells[x].replace_display,nil,'native restore cell '..x) end
mode='refined';T.apply(h)
eq(cells[1].replace_display.image,'checker-revised+refined/crystal/wall-2-1.png','patch round trip')
-- Dig: crystal wall -> CRYSTAL_FLOOR from the zone list (native dig target).
cells[2]=mk(zoneCopy('CRYSTAL_FLOOR'));T.repair(h,1,0,3,0)
eq(cells[2].replace_display.image,'checker-revised+refined/crystal/floor0.png','dug patch wall repaints as patch floor')
eq(cells[1].replace_display.image,'checker-revised+refined/crystal/wall-0-1.png','neighbour wall mask follows dig')
-- Gates: DEFAULT layout, other zones and Scintillating's own (unstamped) crystals.
reset();h.zone={short_name='old-forest'};T.apply(h)
eq(cells[1].replace_display,nil,'DEFAULT Old Forest never uses crystal fill')
eq(cells[0].replace_display.image,'checker-revised+refined/tree-oak0.png','DEFAULT Old Forest forest unaffected')
reset();h.zone={short_name='trollmire'};T.apply(h)
eq(cells[1].replace_display,nil,'event crystal outside Old Forest stays native')
reset();h.zone={short_name='heart-gloom'};T.apply(h)
eq(cells[3].replace_display,nil,'crystal floor in Heart of the Gloom stays native')
reset();h.zone={short_name='old-forest',is_crystaline=true}
cells[1]=mk(fresh('CRYSTAL_WALL7'));cells[3]=mk(fresh('CRYSTAL_FLOOR6'));T.apply(h)
eq(cells[1].replace_display,nil,'unoriginated crystal wall in Old Forest stays native')
eq(cells[3].replace_display,nil,'unoriginated crystal floor in Old Forest stays native')
eq(cells[2].replace_display.image,'checker-revised+refined/crystal/wall-0-0.png','native neighbour does not join mask')
h.zone={short_name='scintillating-caves'};reset();T.apply(h)
eq(cells[1].replace_display.image,'checker-revised+refined/crystal/wall-2-1.png','Scintillating crystal family unchanged')

-- S3/T23: stone rooms in forest/mountain/crystal zones via the combined adapter.
for z,v in pairs{['old-forest']='OLD_FOREST',trollmire='TROLLMIRE',daikara='DAIKARA',['tempest-peak']='TEMPEST_PEAK',['scintillating-caves']='SCINTILLATING'} do
 eq(T.variant({short_name=z}),v,'S3 stone adapter '..z)
 eq(T.combined[z],true,'S3 combined family zone '..z)
end
for _,z in ipairs{'slazish-fen','golem-graveyard','norgos-lair','ritch-tunnels'} do eq(T.variant({short_name=z}),nil,z..' still has no stone adapter') end
reset();h.zone={short_name='old-forest',is_crystaline=true};mode='refined'
eq(T.apply(h),nil,'combined apply returns')
eq(cells[1].replace_display.image,'checker-revised+refined/crystal/wall-2-1.png','combined Old Forest still paints crystal fill')
eq(T.observe(strip,5,0,cells[5]),true,'stone room floor observed')
local path=T.assetPath('floor',nil,T.mask(strip,5,0),1,5,0);T.assets.files[path]=true
eq(T.render(strip,5,0,cells[5],'refined').image,path,'stone room floor board art in Old Forest')
eq(T.render(strip,1,0,cells[1],'refined'),nil,'stone adapter never claims a forest-owned cell')
eq(T.render(strip,5,0,cells[5],'vanilla').image,grids.FLOOR.image,'stone room vanilla restores native snapshot')
eq(T.observe(strip,0,0,cells[0]),false,'forest tree has no stone record')
local roomWall=copy(grids.HARDWALL_NORTH_SOUTH);roomWall.name='vault wall'
eq(T.classify(roomWall),nil,'renamed room wall stays native')
local roomFloor=copy(grids.FLOOR);roomFloor.add_displays={{image='terrain/marble_floor.png'}}
eq(T.classify(roomFloor),nil,'decorated room floor stays native')
eq(T.classify(grids.DOOR_VAULT),'door-closed','S2/T4 Old Forest room sealed door is the board door (flipped)')
local fringedVault=copy(grids.DOOR_VAULT_HORIZ);fringedVault.add_mos={{image='terrain/dungeonwalls_grass/grass_granite_wall2.png',display_y=0.5}}
eq(T.classify(fringedVault),'door-closed','S2/T4 sealed door with the native grass fringe')
-- DungeonWallsGrass (Old Forest/Trollmire nicer_tiler_overlay) grass fringe.
local fringed=copy(grids.HARDWALL_SOUTH);fringed.add_mos={{image='terrain/dungeonwalls_grass/grass_granite_wall2.png',display_y=0.5}}
eq(T.classify(fringed),'hardwall','native grass fringe on south wall keeps stone identity')
eq(#fringed.add_mos,1,'fringe classification never mutates the grid')
local f2=copy(grids.WALL_SOUTH7);f2.add_mos={{image='terrain/dungeonwalls_grass/grass_granite_wall2.png',display_y=0.5}}
eq(T.classify(f2),'wall','native grass fringe on numbered south wall')
local fp=copy(grids.HARDWALL_PILLAR_2);fp.add_displays[1].add_mos={{image='terrain/dungeonwalls_grass/grass_granite_wall_pillar_2.png',display_y=0.4}}
eq(T.classify(fp),'hardwall','native grass fringe on pillar layer')
local fd=copy(grids.DOOR);fd.add_mos={{image='terrain/dungeonwalls_grass/grass_granite_wall2.png',display_y=0.5}}
eq(T.classify(fd),'door-closed','native grass fringe on closed door')
for label,mos in pairs{
 foreign={{image='foreign.png',display_y=0.5}},
 offset={{image='terrain/dungeonwalls_grass/grass_granite_wall2.png',display_y=0.4}},
 extra={{image='terrain/dungeonwalls_grass/grass_granite_wall2.png',display_y=0.5,z=18}},
 two={{image='terrain/dungeonwalls_grass/grass_granite_wall2.png',display_y=0.5},{image='terrain/dungeonwalls_grass/grass_granite_wall2.png',display_y=0.5}},
 wrongimage={{image='terrain/dungeonwalls_grass/grass_granite_wall_pillar_1.png',display_y=0.4}},
} do
 local g=copy(grids.HARDWALL_SOUTH);g.add_mos=mos
 eq(T.classify(g),nil,'non-native wall MO stays native: '..label)
end
local fpBad=copy(grids.HARDWALL_PILLAR_2);fpBad.add_displays[1].add_mos={{image='terrain/dungeonwalls_grass/grass_granite_wall2.png',display_y=0.5}}
eq(T.classify(fpBad),nil,'mismatched pillar fringe stays native')
local fFloor=copy(grids.FLOOR);fFloor.add_mos={{image='terrain/dungeonwalls_grass/grass_granite_wall2.png',display_y=0.5}}
eq(T.classify(fFloor),nil,'fringe never widens floors')
local fStair=copy(grids.DOWN);fStair.add_mos[2]={image='terrain/dungeonwalls_grass/grass_granite_wall2.png',display_y=0.5}
eq(T.classify(fStair),nil,'fringe never widens stairs')
local fUnstamped=copy(fringed);fUnstamped._checker_grid_source=nil
eq(T.classify(fUnstamped),nil,'unstamped fringed wall stays native')
local trollHost={zone={short_name='trollmire'},level={map=strip,level=1}}
reset();T.apply(trollHost)
eq(trollHost.checker_mode,'refined','Trollmire combined mode follows forest')
eq(cells[0].replace_display.image,'checker-revised+refined/tree-oak0.png','Trollmire forest unchanged by stone registration')
eq(T.repair(trollHost,0,0,1,0)~=nil,true,'combined Trollmire still repairs forest')
h.zone={short_name='old-forest'};mode='vanilla'
end)()
;(function()
-- S1: aura rings and centres produced by the native event files themselves
-- (loaded with their real chunk name, so file and line are the game's), over
-- grids defined by the native grid files. Each family must see the event's
-- output as the identity it cloned; anything not exactly that stays native.
local data=root..'../../modules/tome/data'
local COLORS={OLIVE_DRAB={r=107,g=142,b=35},DARK_SLATE_GRAY={r=47,g=79,b=79},VERY_DARK_RED={r=50,g=0,b=0},
 DARK_TAN={r=110,g=80,b=40},AQUAMARINE={r=127,g=255,b=212},DARK_SEA_GREEN={r=143,g=188,b=143}}
local colors=setmetatable({},{__index=function(_,k) return COLORS[k] or {r=9,g=9,b=9} end})
local tr=function(s) return s end
local methods={}
local meta={__index=methods}
local function deep(t)
 if type(t)~='table' then return t end
 local o={};for k,v in pairs(t) do o[k]=deep(v) end
 return setmetatable(o,getmetatable(t))
end
methods.cloneFull=function(self) return deep(self) end
methods.clone=function(self) local o={};for k,v in pairs(self) do o[k]=v end;return setmetatable(o,getmetatable(self)) end
methods.removeAllMOs=function() end;methods.altered=function() end;methods.resolve=function() end
local function readFile(path) local f=assert(io.open(path,'rb'));local s=f:read('*a');f:close();return s end
-- Emulates Grid:loadList: nested files are stamped when they finish, then the
-- outer file stamps its whole result (superload/mod/class/Grid.lua order).
local function loadDefs(file,mod)
 local out,order={},{}
 local fenv
 -- A nested load(path,f) applies f to that file's definitions (as
 -- Entity:loadList passes new_mod or mod); without f the caller's mod.
 local current=mod
 local function run(path,m)
  local first=#order
  local prev=current;current=m
  local chunk=assert(loadstring(readFile(data..path:gsub('^/data','')),'@'..path))
  setfenv(chunk,fenv);chunk()
  current=prev
  for i=first+1,#order do T.markSource(out[order[i]],path) end
 end
 fenv=setmetatable({colors=colors,_t=function(s) return s end,
  class={new=function(t) return setmetatable(t,meta) end,makeNewTrees=function(_,t) return t end,
   makeTrees=function() return {} end,makeCrystals=function() return {{image='terrain/crystal_alpha1.png',z=16}} end},
  resolvers=setmetatable({},{__index=function() return function(v) return v end end}),engine={DamageType=setmetatable({},{__index=function(_,k) return k end})},
  rng={percent=function() return false end,range=function(a) return a end},mod={class={Grid={new=function(t) return setmetatable(t,meta) end}}},currentZone={is_purified=false},
  load=function(path,f) run(path,f or current) end,loading_list=out,
  newEntity=function(t)
   local g=t.base and deep(assert(out[t.base],t.base)) or {}
   for k,v in pairs(t) do g[k]=v end
   g.tint_r=g.tint_r or 1;g.tint_g=g.tint_g or 1;g.tint_b=g.tint_b or 1
   if current then current(g) end
   if not out[t.define_as] then order[#order+1]=t.define_as end
   out[t.define_as]=setmetatable(g,meta)
  end},{__index=_G})
 run(file,mod)
 return out
end
local function mapOf(w,h,cells)
 local m={w=w,h=h,particleEmitter=function() end}
 return setmetatable(m,{__call=function(_,x,y,layer,g)
  if x<0 or y<0 or x>=w or y>=h then return end
  if g then cells[x+y*w]=g end
  return cells[x+y*w]
 end})
end
-- w x h map, fill(x,y) -> definition; placed grids are clones like Zone:makeEntity.
local function scene(w,h,fill)
 local cells={}
 for x=0,w-1 do for y=0,h-1 do cells[x+y*w]=methods.clone(fill(x,y)) end end
 return mapOf(w,h,cells),cells
end
local lavaDefs=loadDefs('/data/general/grids/lava.lua')
local function runEvent(name,m,cx,cy,chunkname)
 local zone={}
 zone.addEntity=function(_,_,g,_,x,y) m(x,y,1,g) end
 local level={map=m}
 local ev=setmetatable({level=level,zone=zone,colors=colors,_t=function(s) return tr(s) end,print=function() end,
  game={level=level,zone=zone,state={findEventGrid=function() return cx,cy end},nicer_tiles={updateAround=function() end}},
  core={shader={active=function() return false end},fov={circle_grids=function(x,y,r)
   local out={}
   for i=-r,r do for j=-r,r do
    if i*i+j*j<=r*r+r and m(x+i,y+j,1) then out[x+i]=out[x+i] or {};out[x+i][y+j]=true end
   end end
   return out
  end}},
  engine={Map={TERRAIN=1,tiles={nicer_tiles=true}}},
  mod={class={Grid={new=function(t) return setmetatable(t,meta) end,loadList=function() return lavaDefs end}}}},{__index=_G})
 local chunk=assert(loadstring(readFile(data..'/general/events/'..name..'.lua'),chunkname or ('@/data/general/events/'..name..'.lua')))
 setfenv(chunk,ev)
 eq(chunk(),true,'native event ran '..name)
end
string.tformat=function(s,...) return tr(s):format(...) end
local function host(zone,m,level) return {zone=zone,level={map=m,level=level or 1}} end
local function mask(event) return 'checker-revised+aura-'..({['fell-aura']='violet',['antimagic-bush']='violet',['necrotic-air']='violet',
 ['whistling-vortex']='violet',['spellblaze-scar']='crimson',['bligthed-soil']='crimson',['font-life']='teal',['protective-aura']='teal'})[event]..'-subtle.png' end
mode='refined'
-- Every ring cell painted, by its family art, with the event mask; centres
-- also carry their native prop; the grid itself is never changed.
local function checkRing(label,m,h,event,expect,centre)
 local before={}
 for x=0,m.w-1 do for y=0,m.h-1 do
  local g=m(x,y,1)
  if g.on_stand then before[x+y*m.w]={on_stand=g.on_stand,dbm=g.does_block_move,bs=g.block_sight,dig=g.dig,name=g.name,cl=g.change_level} end
 end end
 T.apply(h)
 local ring=0
 for key,b in pairs(before) do
  local x,y=key%m.w,math.floor(key/m.w)
  local g=m(x,y,1)
  local want=expect(x,y,g)
  if want then
   ring=ring+1
   local d=g.replace_display
   eq(d and d.image:match('^checker%-revised%+refined/'..want)~=nil,true,label..' ring cell '..x..','..y..' painted as '..want..' got '..tostring(d and d.image))
   eq(d.add_displays[1].image,mask(event),label..' aura mask '..x..','..y)
   if centre and x==centre[1] and y==centre[2] then
    eq(d.add_displays[2] and d.add_displays[2].image,centre[3],label..' centre keeps native prop')
    eq(d.add_displays[2].z,5,label..' centre prop native z')
   else eq(d.add_displays[2],nil,label..' ring cell has no extra layer') end
  else eq(g.replace_display,nil,label..' excluded cell stays native '..x..','..y) end
  eq(g.on_stand,b.on_stand,label..' on_stand untouched');eq(g.does_block_move,b.dbm,label..' passability untouched')
  eq(g.block_sight,b.bs,label..' sight untouched');eq(g.dig,b.dig,label..' dig untouched')
  eq(g.name,b.name,label..' name untouched');eq(g.change_level,b.cl,label..' transition untouched')
 end
 return ring
end
local target={EFF_BLIGHTED_SOIL=1,EFF_FONT_OF_LIFE=2,EFF_FELL_AURA=3,EFF_SPELLBLAZE_SCAR=4,EFF_NECROTIC_AIR=5,EFF_WHISTLING_VORTEX=6,EFF_ANTIMAGIC_BUSH=7,EFF_PROTECTIVE_AURA=8,
 setEffect=function(self,id) self.applied=id end}

-- Gloom (Heart of the Gloom): blighted soil over floor, creep and vegetation.
local gloomDefs=loadDefs('/data/zones/heart-gloom/grids.lua')
local m=scene(7,7,function(x,y) return x==5 and gloomDefs.UNDERGROUND_TREE7 or y==1 and gloomDefs.UNDERGROUND_CREEP2 or gloomDefs['UNDERGROUND_FLOOR'..(x+1)] end)
runEvent('bligthed-soil',m,3,3)
eq(m(3,3,1).name,'blighted soil (blighted aura)','native blighted-soil centre name')
eq(m(3,2,1).name,'floor (blighted aura)','native blighted-soil ring name')
eq(m(5,3,1).name,'underground thick vegetation','native ring leaves vegetation name')
eq(T.gloomTerrain(m(3,2,1),'gloomy'),'gloom-floor','E1 gloom ring floor')
eq(T.gloomTerrain(m(3,1,1),'gloomy'),'gloom-creep','E1 gloom ring creep')
eq(T.gloomTerrain(m(5,3,1),'gloomy'),'gloom-wall','E2 gloom ring vegetation')
eq(T.gloomTerrain(m(3,3,1),'gloomy'),'gloom-floor','E3 gloom centre floor')
m(3,2,1).on_stand(m(3,2,1),3,2,target);eq(target.applied,1,'gloom ring keeps native blighted-soil effect')
local gh=host({short_name='heart-gloom',is_purified=false},m)
eq(checkRing('gloom',m,gh,'bligthed-soil',function(x,y,g) return x==5 and 'gloom/gloomy/wall%-' or y==1 and 'gloom/gloomy/creep%-' or 'gloom/gloomy/floor' end,
 {3,3,'terrain/blight_root.png'})>20,true,'gloom ring coverage')
mode='vanilla';T.apply(gh);eq(m(3,2,1).replace_display,nil,'gloom ring native restore')
eq(m(3,3,1).replace_display,nil,'gloom centre native restore');mode='refined';T.apply(gh)
eq(m(3,3,1).replace_display.add_displays[2].image,'terrain/blight_root.png','gloom centre prop after round trip')
local other=host({short_name='other-zone'},m);mode='vanilla';T.apply(gh);mode='refined';T.apply(other)
eq(m(3,2,1).replace_display,nil,'gloom ring in an ungated zone stays native')
eq(m(5,3,1).replace_display,nil,'gloom vegetation ring in an ungated zone stays native')
-- Deep Bellow's plain skin uses the same gloomy definitions.
local dm=scene(5,5,function(x,y) return gloomDefs.UNDERGROUND_FLOOR end)
runEvent('bligthed-soil',dm,2,2)
checkRing('deep-bellow',dm,host({short_name='deep-bellow'},dm),'bligthed-soil',function() return 'gloom/plain/floor' end,{2,2,'terrain/blight_root.png'})

-- Negatives on one exact ring floor.
local ringFloor=m(3,2,1)
local function variant(g,f) local c=deep(g);c.replace_display=nil;c._checker_terrain=nil;f(c);return c end
local function pad(line,src) return (('\n'):rep(line-1))..(src or 'return function(self,x,y,who) end') end
eq(T.gloomTerrain(variant(ringFloor,function(c) end),'gloomy'),'gloom-floor','exact ring copy accepted')
local neg={
 ['altered on_stand']=function(c) c.on_stand=function() end end,
 ['same file, other line']=function(c) c.on_stand=assert(loadstring(pad(1),'@/data/general/events/bligthed-soil.lua'))() end,
 ['overridden file, shifted line']=function(c) c.on_stand=assert(loadstring(pad(25),'@/data/general/events/bligthed-soil.lua'))() end,
 ['foreign addon event file']=function(c) c.on_stand=assert(loadstring(pad(24),'@/data-foreign/general/events/bligthed-soil.lua'))() end,
 ['unknown event file']=function(c) c.on_stand=assert(loadstring(pad(24),'@/data/general/events/glowing-chest.lua'))() end,
 ['extra display layer']=function(c) c.add_displays={{image='terrain/foreign.png'}} end,
 ['extra mo layer']=function(c) c.add_mos={{image='terrain/foreign.png'}} end,
 ['name not the event rename']=function(c) c.name='floor (fell aura)' end,
 ['unrenamed floor']=function(c) c.name='floor' end,
 ['foreign minimap']=function(c) c.special_minimap={r=1,g=2,b=3} end,
 ['minimap extra key']=function(c) c.special_minimap={r=47,g=79,b=79,br=1} end,
 ['not remembered']=function(c) c.always_remember=nil end,
 ['safety hint on unsafe event']=function(c) c.on_stand_safe=true end,
 ['no definition stamp']=function(c) c._checker_def=nil end,
 ['definition of another id']=function(c) c._checker_def.id='UNDERGROUND_FLOOR99' end,
 ['definition had its own on_stand']=function(c) c._checker_def.stand=true end,
 ['blocks sight']=function(c) c.block_sight=true end,
 ['blocks movement']=function(c) c.does_block_move=true end,
 ['transition']=function(c) c.change_level=1 end,
 ['extra callback']=function(c) c.on_dig=function() end end,
} for label,f in pairs(neg) do eq(T.gloomTerrain(variant(ringFloor,f),'gloomy'),nil,'gloom ring negative: '..label) end
local wallRing=m(5,3,1)
eq(T.gloomTerrain(variant(wallRing,function(c) c.name='underground thick vegetation (blighted aura)' end),'gloomy'),nil,'renamed ring wall stays native')
eq(T.gloomTerrain(variant(wallRing,function(c) c.dig=nil end),'gloomy'),nil,'ring wall rule drift stays native')
local centreCell=m(3,3,1)
for label,f in pairs{
 ['foreign prop']=function(c) c.add_displays[#c.add_displays].image='terrain/foreign.png' end,
 ['prop z']=function(c) c.add_displays[#c.add_displays].z=4 end,
 ['layer after prop']=function(c) c.add_displays[#c.add_displays+1]={image='terrain/blight_root.png',z=5} end,
 ['prop offset']=function(c) c.add_displays[#c.add_displays].display_y=-1 end,
 ['centre colour']=function(c) c.color_g=254 end,
 ['centre glyph']=function(c) c.display='&' end,
 ['centre not noticed']=function(c) c.notice=nil end,
 ['centre minimap']=function(c) c.special_minimap={r=47,g=79,b=79} end,
 ['centre name']=function(c) c.name='blighted soil' end,
 ['other event centre prop']=function(c) c.add_displays[#c.add_displays].image='terrain/terrain_pot_03_01_64.png' end,
} do eq(T.gloomTerrain(variant(centreCell,f),'gloomy'),nil,'gloom centre negative: '..label) end

-- Sand (Ritch Tunnels): font of life over sand floor and stable sandwall.
local sandDefs=loadDefs('/data/general/grids/sand.lua')
m=scene(6,5,function(x,y) return x==4 and sandDefs.SANDWALL_STABLE or sandDefs['UNDERGROUND_SAND'..(x+1)] end)
runEvent('font-life',m,2,2)
eq(m(2,2,1).on_stand_safe,true,'font-life marks its ring safe')
eq(T.sandTerrain(m(2,1,1)),'floor','E1 sand ring floor')
eq(T.sandTerrain(m(4,2,1)),'wall','E2 sand ring wall')
eq(T.sandTerrain(m(2,2,1)),'floor','E3 sand centre')
eq(T.sandTerrain(variant(m(2,1,1),function(c) c.on_stand_safe=nil end)),nil,'font-life ring without its safety hint stays native')
checkRing('sand',m,host({short_name='ritch-tunnels'},m),'font-life',function(x) return x==4 and 'sand/wall%-' or 'sand/floor' end,
 {2,2,'terrain/terrain_pot_03_01_64.png'})

-- Crystal (Scintillating Caves): spellblaze scar; its lava centre stays native.
local crystalDefs=loadDefs('/data/general/grids/crystal.lua')
m=scene(5,5,function(x,y) return x==3 and crystalDefs.CRYSTAL_WALL5 or crystalDefs['CRYSTAL_FLOOR'..(y+1)] end)
runEvent('spellblaze-scar',m,2,2)
eq(m(2,2,1).define_as,'LAVA_FLOOR','spellblaze centre is the native lava clone')
eq(T.crystalTerrain(m(2,1,1)),'floor','E1 crystal ring floor')
eq(T.crystalTerrain(m(3,2,1)),'wall','E2 crystal ring wall')
eq(T.crystalTerrain(m(2,2,1)),nil,'spellblaze lava centre stays native')
checkRing('crystal',m,host({short_name='scintillating-caves'},m),'spellblaze-scar',function(x,y) if x==2 and y==2 then return end return x==3 and 'crystal/wall%-' or 'crystal/floor' end)
eq(m(2,2,1).replace_display,nil,'spellblaze centre native display')
-- Old Forest CRYSTALINE: the patch's event-stamped crystals under an aura.
local ofDefs=loadDefs('/data/general/grids/crystal.lua')
for _,g in pairs(ofDefs) do T.markCrystalOrigin(g,'crystaline-forest') end
m=scene(7,7,function(x,y) return x==5 and ofDefs.CRYSTAL_WALL8 or ofDefs.CRYSTAL_FLOOR2 end)
runEvent('antimagic-bush',m,3,3)
eq(T.oldForestCrystal(m(3,2,1)),'floor','Old Forest ring crystal floor')
eq(T.oldForestCrystal(m(5,3,1)),'wall','Old Forest ring crystal wall')
checkRing('old-forest crystal',m,host({short_name='old-forest',is_crystaline=true},m),'antimagic-bush',
 function(x) return x==5 and 'crystal/wall%-' or 'crystal/floor' end,{3,3,'terrain/antimagic_bush.png'})
local noOrigin=variant(m(5,3,1),function(c) c._checker_crystal_source.origin=nil end)
eq(T.oldForestCrystal(noOrigin),nil,'Old Forest ring wall still needs event origin')

-- Cave (Ardhungol): fell aura over cave floor, rock floor and cave wall.
local caveDefs=loadDefs('/data/general/grids/cave.lua')
m=scene(6,5,function(x,y) return x==4 and caveDefs.CAVEWALL or y==0 and caveDefs.CAVEFLOOR12 or caveDefs.CAVEFLOOR end)
runEvent('fell-aura',m,2,2)
eq(T.caveTerrain(m(2,2,1)),'floor','E1 cave ring floor (fell aura has no centre prop)')
eq(T.caveTerrain(m(2,0,1)),'floor','E1 cave ring rock floor')
eq(T.caveTerrain(m(4,2,1)),'wall','E2 cave ring wall')
checkRing('cave',m,host({short_name='ardhungol'},m),'fell-aura',function(x,y) return x==4 and 'cave/wall%-' or y==0 and 'cave/floor%-rock%-5' or 'cave/floor' end)
m(2,2,1).on_stand(m(2,2,1),2,2,target);eq(target.applied,3,'cave ring keeps native fell-aura effect')

-- Burnt (Mark of the Spellblaze): spellblaze scar over burnt ground and trees.
local burntDefs=loadDefs('/data/general/grids/burntland.lua')
m=scene(5,5,function(x,y) return x==3 and burntDefs.BURNT_TREE5 or burntDefs.BURNT_GROUND end)
runEvent('spellblaze-scar',m,2,2)
eq(T.burntTerrain(m(2,1,1)),'floor','E1 burnt ring floor')
eq(T.burntTerrain(m(3,2,1)),'tree','E2 burnt ring tree')
checkRing('burnt',m,host({short_name='mark-spellblaze'},m),'spellblaze-scar',function(x,y) if x==2 and y==2 then return end return x==3 and 'burnt/tree' or 'burnt/floor' end)

-- Bone (Rak'Shor Pride): necrotic air over bone floor, walls and a door.
local boneDefs=loadDefs('/data/general/grids/bone.lua')
m=scene(6,5,function(x,y) return x==4 and (y==2 and boneDefs.BONE_DOOR_HORIZ or boneDefs.BONEWALL3) or boneDefs.BONEFLOOR end)
runEvent('necrotic-air',m,2,2)
eq(T.batch5Kind(m(2,2,1),'rakshor'),'floor','E1 bone ring floor')
eq(T.batch5Kind(m(4,1,1),'rakshor'),'wall','E2 bone ring wall')
eq(T.batch5Kind(m(4,2,1),'rakshor'),'door-closed','E2 bone ring door')
checkRing('bone',m,host({short_name='rak-shor-pride'},m),'necrotic-air',function(x,y) return x==4 and (y==2 and 'rakshor/door%-closed' or 'rakshor/wall%-') or 'rakshor/floor' end)
local lever=variant(m(4,1,1),function(c) c.on_lever_change=function() end end)
eq(T.batch5Kind(lever,'rakshor'),nil,'lever-like bone ring wall stays native')
m=scene(8,8,function() return boneDefs.BONEFLOOR end)
runEvent('whistling-vortex',m,4,4)
checkRing('bone vortex',m,host({short_name='rak-shor-pride'},m),'whistling-vortex',function() return 'rakshor/floor' end)

-- Forest (Trollmire FLOODED): life aura over bog water, misc bog and grass
-- with its native border layer; the pot stays over the centre.
local trollDefs=loadDefs('/data/zones/trollmire/grids.lua')
local borderGrass=methods.clone(trollDefs.GRASS_PATCH11)
borderGrass.add_displays={setmetatable({image='invis.png',add_mos={{image='terrain/grass/grass_2_01.png',display_y=-1}}},meta)}
m=scene(5,5,function(x,y) return y==0 and borderGrass or x==0 and trollDefs.BOGWATER_MISC1 or trollDefs.BOGWATER end)
runEvent('font-life',m,2,2)
eq(m(2,2,1).name,'font of life (life aura)','native font-life centre on bog')
eq(T.forestKind(m(2,1,1)),'bog','E1 bog ring')
eq(T.forestKind(m(0,2,1)),'bog-misc','E1 misc bog ring keeps its variant')
eq(T.forestKind(m(2,0,1)),'grass','E1 bordered grass ring')
eq(T.forestKind(m(2,2,1)),'bog','E3 bog centre is bog, not misc')
checkRing('trollmire',m,host({short_name='trollmire',is_flooded=true},m),'font-life',function(x,y) return y==0 and 'grass' or x==0 and 'bog%-misc' or 'bog' end,
 {2,2,'terrain/terrain_pot_03_01_64.png'})
eq(T.forestKind(variant(m(2,0,1),function(c) c.add_displays[1].add_mos[1].image='terrain/foreign.png' end)),nil,'forest ring with a foreign border stays native')
eq(T.forestKind(variant(m(2,1,1),function(c) c.name='bog water (fell aura)' end)),nil,'forest bog ring with another rename stays native')
local strayBog=methods.clone(trollDefs.BOGWATER);strayBog.name='bog water (life aura)';strayBog.always_remember=true
strayBog.on_stand=m(2,1,1).on_stand;strayBog.on_stand_safe=true;strayBog.special_minimap=COLORS.AQUAMARINE;strayBog._checker_def=nil
eq(T.forestKind(strayBog),nil,'forest ring without definition stamp stays native')

-- Stone (Dreadfell): necrotic air reaches walls, a door and stairs; a
-- blighted-soil centre keeps its root over the board floor.
local s1grids=loadDefs('/data/general/grids/basic.lua')
m=scene(7,5,function(x,y) return x==5 and (y==2 and s1grids.DOOR or s1grids['WALL_NORTH'..(y+1)]) or x==6 and s1grids.HARDWALL or (x==1 and y==1) and s1grids.UP or s1grids.FLOOR end)
runEvent('necrotic-air',m,3,2)
eq(T.classify(m(3,2,1)),'floor','E1 stone ring floor (existing path)')
eq(T.classify(m(5,1,1)),'wall','E2 stone ring wall')
eq(T.classify(m(5,2,1)),'door-closed','E2 stone ring door')
eq(T.classify(m(1,1,1)),'stairs-up','stone ring stairs')
eq(m(1,1,1).name,'previous level (necrotic air)','native ring renames stairs')
local ringWall=m(5,1,1)
eq(T.classify(variant(ringWall,function(c) c.on_stand=assert(loadstring(pad(1),'@/data/general/events/necrotic-air.lua'))() end)),nil,'stone ring wall with a shifted event line stays native')
eq(T.classify(variant(ringWall,function(c) c.on_stand=assert(loadstring(pad(30),'@/data-foreign/general/events/necrotic-air.lua'))() end)),nil,'stone ring wall from a foreign event file stays native')
eq(T.classify(variant(ringWall,function(c) c.name='wall (necrotic air)' end)),nil,'renamed stone ring wall stays native')
eq(T.classify(variant(ringWall,function(c) c.special_minimap={r=47,g=79,b=79} end)),nil,'stone ring wall minimap drift stays native')
eq(T.classify(variant(ringWall,function(c) c.add_displays[#c.add_displays+1]={image='terrain/foreign.png'} end)),nil,'stone ring wall with an extra layer stays native')
eq(T.classify(variant(ringWall,function(c) c.always_remember=nil end)),nil,'unremembered stone ring wall stays native')
eq(T.classify(variant(m(1,1,1),function(c) c.name='previous level' end)),nil,'unrenamed stone ring stairs stay native')
eq(T.classify(variant(m(1,1,1),function(c) c.change_level=2 end)),nil,'stone ring stairs destination drift stays native')
local cm=scene(5,5,function() return s1grids.FLOOR end)
runEvent('bligthed-soil',cm,2,2)
eq(T.classify(cm(2,2,1)),'floor','E3 stone centre floor')
eq(T.classify(variant(cm(2,2,1),function(c) c.add_displays[1].image='terrain/foreign.png' end)),nil,'stone centre foreign prop stays native')
eq(T.classify(variant(cm(2,2,1),function(c) c.add_displays[2]={image='terrain/foreign.png'} end)),nil,'stone centre extra layer stays native')
local seen={w=cm.w,h=cm.h,seens=function() return true end,infovs=function() return true end,remembers=function() return true end}
setmetatable(seen,getmetatable(cm))
eq(T.observe(seen,2,2,cm(2,2,1)),true,'stone centre observed')
local cpath=T.assetPath('floor',nil,T.mask(seen,2,2),0,2,2);T.assets.files[cpath]=true
local cd=T.render(seen,2,2,cm(2,2,1),'refined')
eq(cd.image,cpath,'stone centre board floor')
eq(cd.add_displays[1].image,mask('bligthed-soil'),'stone centre aura mask')
eq(cd.add_displays[2].image,'terrain/blight_root.png','stone centre native root')
eq(T.render(seen,2,2,cm(2,2,1),'vanilla').add_displays[1].image,'terrain/blight_root.png','stone centre vanilla restores native snapshot')
eq(T.observe(seen,1,2,cm(1,2,1)),true,'stone ring floor observed')
eq(T.render(seen,1,2,cm(1,2,1),'refined').add_displays[2],nil,'stone ring floor has no prop')

-- Translated names: the event's own tformat/_t of the native name.
local zh={['%s (fell aura)']='%s（邪恶光环）',['cave floor']='洞穴地面'}
tr=function(s) return zh[s] or s end;env._t=tr
m=scene(3,3,function() return caveDefs.CAVEFLOOR end)
runEvent('fell-aura',m,1,1)
eq(m(1,1,1).name,'洞穴地面（邪恶光环）','localized native rename')
eq(T.caveTerrain(m(1,1,1)),'floor','localized ring keeps cave identity')
tr=function(s) return s end;env._t=nil
eq(T.caveTerrain(m(1,1,1)),nil,'ring renamed under another locale stays native (no guessing)')
-- TW1: static towns (Derth, Lumberjack village). Native town lists loaded
-- the way Grid:loadList does (nested imports stamped first, then the town
-- file). Identity needs the general-file stamp, the town's own list stamp
-- and the unchanged rule contract; shops stay on the trap layer.
local derthDefs=loadDefs('/data/zones/town-derth/grids.lua')
local lumberDefs=loadDefs('/data/zones/town-lumberjack-village/grids.lua')
local derthFile,lumberFile='/data/zones/town-derth/grids.lua','/data/zones/town-lumberjack-village/grids.lua'
eq(derthDefs.HARDWALL._checker_town_source.file,derthFile,'TW1 town list stamps nested basic.lua walls')
eq(derthDefs.HARDWALL._checker_grid_source.file,'/data/general/grids/basic.lua','TW1 nested wall keeps general stamp')
eq(derthDefs.TREE7._checker_forest_source.file,'/data/general/grids/forest.lua','TW1 nested tree keeps forest stamp')
eq(derthDefs.DEEP_WATER._checker_town_source.id,'DEEP_WATER','TW1 town stamp id is the definition id')
for id,kind in pairs{GRASS='grass',GRASS_PATCH3='grass',TREE7='tree',GRASS_ROAD_STONE='road',DEEP_WATER='deep',GRASS_UP_WILDERNESS='exit'} do
 eq(T.batch4Kind(methods.clone(derthDefs[id]),'town-derth'),kind,'TW1 Derth exact '..id)
 eq(T.batch4Kind(methods.clone(lumberDefs[id]),'town-lumberjack-village'),kind,'TW1 Lumberjack exact '..id)
 local c=deep(derthDefs[id]);c._checker_town_source=nil
 eq(T.batch4Kind(c,'town-derth'),nil,'TW1 unstamped town grid stays native '..id)
 eq(T.batch4Kind(methods.clone(derthDefs[id]),'town-lumberjack-village'),nil,'TW1 other town list stays native '..id)
 eq(T.batch4Kind(methods.clone(derthDefs[id]),'south-beach'),nil,'TW1 town family is zone scoped '..id)
end
for id in pairs{FIELDS=1,COBBLESTONE=1,HARDTREE3=1,FLOWER2=1,SAND=1} do
 if derthDefs[id] and id~='FLOWER2' then eq(T.batch4Kind(methods.clone(derthDefs[id]),'town-derth'),nil,'TW1 unused/unsupported town identity native '..id) end
end
eq(T.batch4Kind(methods.clone(derthDefs.FLOWER2),'town-derth'),'flower','TW1 exact forest flower')
for _,mutation in ipairs{
 {'TREE7',function(c) c.does_block_move=nil end},{'TREE7',function(c) c.can_pass={pass_tree=1,pass_wall=1} end},
 {'TREE7',function(c) c.block_sight=nil end},{'GRASS',function(c) c.does_block_move=true end},
 {'GRASS',function(c) c.on_move=function() end end},{'DEEP_WATER',function(c) c.air_level=-1 end},
 {'DEEP_WATER',function(c) c.on_stand=function() end end},{'GRASS_ROAD_STONE',function(c) c.block_sight=true end},
 {'GRASS_UP_WILDERNESS',function(c) c.change_zone='other' end},{'GRASS_UP_WILDERNESS',function(c) c.change_level_check=function() end end},
} do
 local c=deep(derthDefs[mutation[1]]);mutation[2](c)
 eq(T.batch4Kind(c,'town-derth'),nil,'TW1 altered rule field stays native '..mutation[1])
end
eq(T.variant({short_name='town-derth'}),'TOWN_DERTH','TW1 Derth stone gate')
eq(T.variant({short_name='town-lumberjack-village'}),'LUMBERJACK_VILLAGE','TW1 Lumberjack stone gate')
-- TW3 gated Zigur, Angolwen and the Iron Council; TW4 Shatur (forest only, no
-- stone variant) and Point Zero; TW5 Gates of Morning; TW6 Irkkk (forest only,
-- no stone variant). No town stays ungated; non-town zones still have no town
-- list and no town variant.
for _,zone in ipairs{'town-derth','town-lumberjack-village','town-last-hope','town-elvala','town-zigur','town-angolwen',
 'town-iron-council','town-shatur','town-point-zero','town-gates-of-morning','town-irkkk'} do
 eq(T.townFiles[zone],'/data/zones/'..zone..'/grids.lua','TW6 every town is gated '..zone)
end
local nTowns=0;for _ in pairs(T.townFiles) do nTowns=nTowns+1 end
eq(nTowns,11,'TW6 exactly the eleven towns have town lists')
for _,zone in ipairs{'town-irkkk','town-shatur'} do eq(T.variant({short_name=zone}),nil,'TW6 forest-only town has no stone variant '..zone) end
for _,zone in ipairs{'gorbat-pride','noxious-caldera','wilderness','trollmire'} do
 eq(T.townFiles[zone],nil,'TW6 non-town zone has no town list '..zone)
 -- S6: Gorbat Pride is now a combined (non-town) zone.
 eq(T.combined[zone] and zone~='trollmire' and zone~='gorbat-pride' or nil,nil,'TW6 non-town zone is not a combined town '..zone)
end
-- S10a: Grushnak Pride is now a combined (non-town) stone zone. S10b: so is
-- Vor Pride (not a town); an unsupported zone still has no variant.
eq(T.variant({short_name='infinite-dungeon'}),nil,'TW6 non-town zone stays without a town variant')
eq(T.variant({short_name='vor-pride'}),'VOR_PRIDE','S10b Vor Pride stone gate')
eq(T.townFiles['vor-pride'],nil,'S10b Vor Pride is not a town')
eq(T.townFiles['grushnak-pride'],nil,'S10a Grushnak Pride is not a town')
eq(T.combined['town-derth'] and T.combined['town-lumberjack-village'],true,'TW1 towns combine forest and stone')
local savedGame=env.game
env.game={zone={short_name='town-derth'}}
for _,id in ipairs{'HARDWALL','HARDWALL_NORTH2','HARDWALL_SOUTH5','HARDWALL_PILLAR_6'} do eq(T.classify(methods.clone(derthDefs[id])),'hardwall','TW1 Derth exact '..id) end
local wall=deep(derthDefs.HARDWALL);wall._checker_town_source=nil
eq(T.classify(wall),nil,'TW1 wall without town list stamp stays native in town')
eq(T.classify(methods.clone(s1grids.HARDWALL)),nil,'TW1 plain basic.lua wall (no town list) stays native in town')
wall=deep(derthDefs.HARDWALL);wall.block_sense=nil
eq(T.classify(wall),nil,'TW1 altered town wall stays native')
eq(T.classify(methods.clone(derthDefs.COBBLESTONE)),nil,'TW1 COBBLESTONE base=FLOOR copy stays native')
env.game={zone={short_name='town-lumberjack-village'}}
eq(T.classify(methods.clone(lumberDefs.WALL)),'wall','TW1 Lumberjack diggable cabin wall')
eq(T.classify(methods.clone(lumberDefs.FLOOR)),'floor','TW1 Lumberjack cabin floor')
eq(T.classify(methods.clone(lumberDefs.DOOR)),'door-closed','TW1 Lumberjack cabin door')
eq(T.classify(methods.clone(derthDefs.HARDWALL)),nil,'TW1 Derth-listed wall is not a Lumberjack wall')
env.game={zone={short_name='ruins-kor-pul'}}
eq(T.classify(methods.clone(s1grids.HARDWALL)),'hardwall','TW1 non-town zones need no town stamp')

-- Remembered-town install. Layered map: 1 terrain, 3 trap.
local TRAP=3
local function townMap(w,h,fill)
 local layers={[1]={},[TRAP]={}}
 for x=0,w-1 do for y=0,h-1 do layers[1][x+y*w]=methods.clone(fill(x,y)) end end
 local seen,rem={},{}
 local tm={w=w,h=h,seen=seen,rem=rem,layers=layers,
  seens=function(x,y) return seen[x+y*w] and true or false end,infovs=function(x,y) return seen[x+y*w] and true or false end}
 tm.remembers=setmetatable({},{__call=function(_,x,y) return rem[x+y*w]~=false end})
 return setmetatable(tm,{__call=function(_,x,y,layer,g)
  if x<0 or y<0 or x>=w or y>=h then return end
  local l=layers[layer or 1];if not l then return end
  if g then l[x+y*w]=g end
  return l[x+y*w]
 end})
end
-- Derth-like block: row 1-2 walls with a shop door at (2,2); trees west, road, water east.
local plan={
 't..~~',
 '.##_~',
 '.#2_~',
 '<.._.'}
local sym={t='TREE7',['.']='GRASS',['~']='DEEP_WATER',['#']='HARDWALL',['2']='HARDWALL',['_']='GRASS_ROAD_STONE',['<']='GRASS_UP_WILDERNESS'}
local function derthMap() return townMap(5,4,function(x,y) return derthDefs[sym[plan[y+1]:sub(x+1,x+1)]] end) end
local tm=derthMap()
local shop={define_as='SWORD_WEAPON_STORE',name='store',image='store/shop_door.png',z=18,block_move=function() return true end}
tm(2,2,TRAP,shop)
local shopRules={};for k,v in pairs(tm(2,2,1)) do shopRules[k]=v end
local savedAssets=T.assets
T.assets={ready=true,revision='tw1-test',files=setmetatable({},{__index=function(_,k) return type(k)=='string' and k:match('^checker%-revised%+refined/korpul/') and true or nil end})}
env.game={zone={short_name='town-derth'}}
mode='refined'
-- Native FOV behaviour first: nothing in FOV, so observe records nothing.
for x=0,4 do for y=0,3 do eq(T.observe(tm,x,y,tm(x,y,1)),false,'TW1 unseen cell is not observed') end end
eq(T.render(tm,1,1,tm(1,1,1),'refined'),nil,'TW1 remembered but unseen wall stays native without the install')
local th={zone={short_name='town-derth'},level={map=tm,data={all_remembered=true}}}
T.apply(th)
eq(th.checker_mode,'refined','TW1 Derth refined mode')
eq(tm(0,0,1).replace_display.image:match('^checker%-revised%+refined/tree%-')~=nil,true,'TW1 Derth tree is board tree')
eq(tm(1,0,1).replace_display.image,'checker-revised+refined/grass1.png','TW1 Derth grass')
eq(tm(3,1,1).replace_display.image,'checker-revised+refined/town/road0.png','TW1 Derth stone road (TW7 board stone slabs)')
eq(tm(0,3,1).replace_display.image,'checker-revised+refined/exit1.png','TW1 Derth world exit')
eq(tm(4,1,1).replace_display.image,'checker-revised+refined/deep5-1-0.png','TW1 Derth deep water mask (N,S)')
eq(tm(1,1,1).replace_display,nil,'TW1 stone never takes a forest replace_display')
local w11=T.render(tm,1,1,tm(1,1,1),'refined')
eq(w11.image,T.assetPath('hardwall',nil,6,0,1,1),'TW1 hidden remembered wall uses its static mask (E,S)')
eq(T.render(tm,2,1,tm(2,1,1),'refined').image,T.assetPath('hardwall',nil,12,1,2,1),'TW1 hidden wall mask (S,W)')
eq(T.render(tm,2,2,tm(2,2,1),'refined').image,T.assetPath('hardwall',nil,9,0,2,2),'TW1 shop wall mask (N,W)')
eq(tm(2,2,TRAP),shop,'TW1 shop trap-layer object untouched')
eq(shop.image,'store/shop_door.png','TW1 shop door art untouched')
for k,v in pairs(shopRules) do eq(tm(2,2,1)[k],v,'TW1 shop wall field '..tostring(k)) end
eq(T.classify(tm(2,2,1)),'hardwall','TW1 shop cell grid is plain HARDWALL')
eq(tm._checker_korpul[1+1*5].painted,true,'TW1 painted after render')
-- Native restore then board again: same display entity.
mode='vanilla';T.apply(th)
eq(T.render(tm,1,1,tm(1,1,1),'vanilla').image,derthDefs.HARDWALL.image,'TW1 native mode restores native wall snapshot')
eq(tm(0,0,1).replace_display,nil,'TW1 native mode restores tree')
mode='refined';T.apply(th)
eq(T.render(tm,1,1,tm(1,1,1),'refined'),w11,'TW1 refined restore returns the identical board wall')
-- Unexplored cells are never read or exposed.
tm=derthMap();tm.rem[1+1*5]=false
th.level.map=tm;T.apply(th)
eq(tm._checker_korpul[1+1*5],nil,'TW1 unremembered wall gets no record')
eq(T.render(tm,1,1,tm(1,1,1),'refined').image,'invis.png','TW1 unremembered wall stays unknown')
eq(T.render(tm,2,1,tm(2,1,1),'refined').image,T.assetPath('hardwall',nil,4,1,2,1),'TW1 neighbour mask ignores the unknown wall')
-- Level not all_remembered (and Lumberjack): FOV semantics unchanged.
tm=derthMap();th.level={map=tm,data={}};T.apply(th)
eq(tm._checker_korpul,nil,'TW1 not all_remembered: no install')
eq(T.installRemembered(th),0,'TW1 not all_remembered: install count 0')
-- Non-town zones: install path inert even when all_remembered.
for _,zone in ipairs{'ruins-kor-pul','trollmire','dreadfell'} do
 local om=derthMap()
 local oh={zone={short_name=zone},level={map=om,data={all_remembered=true}}}
 env.game={zone=oh.zone}
 eq(T.installRemembered(oh),0,'TW1 install inert in '..zone)
 T.apply(oh)
 eq(om._checker_korpul,nil,'TW1 no hidden records in '..zone)
end
-- Lumberjack: cabins via FOV only (the level is not all_remembered).
env.game={zone={short_name='town-lumberjack-village'}}
local lplan={'T;;;','####','#..+','####'}
local lsym={T='TREE7',[';']='GRASS',['#']='WALL',['.']='FLOOR',['+']='DOOR'}
local lm=townMap(4,4,function(x,y) return lumberDefs[lsym[lplan[y+1]:sub(x+1,x+1)]] end)
local lh={zone={short_name='town-lumberjack-village'},level={map=lm,data={}}}
T.apply(lh)
eq(lm(0,0,1).replace_display.image:match('^checker%-revised%+refined/tree%-')~=nil,true,'TW1 Lumberjack tree')
eq(lm._checker_korpul,nil,'TW1 Lumberjack hidden cabin stays native until seen')
lm.seen[3+2*4]=true
eq(T.observe(lm,3,2,lm(3,2,1)),true,'TW1 Lumberjack seen door observed')
eq(T.render(lm,3,2,lm(3,2,1),'refined').image:match('^checker%-revised%+refined/korpul/door%-closed')~=nil,true,'TW1 Lumberjack board door')

-- TW2: Last Hope and Elvala. Town lists loaded like Grid:loadList (Last Hope
-- also imports mountain.lua); Last Hope's statues come from its real map file
-- run with its real chunk name, so callback file and line are the game's.
local lhFile,elFile='/data/zones/town-last-hope/grids.lua','/data/zones/town-elvala/grids.lua'
local lhDefs=loadDefs(lhFile)
local elDefs=loadDefs(elFile)
eq(lhDefs.HARDMOUNTAIN_WALL._checker_town_source.file,lhFile,'TW2 Last Hope list stamps nested mountain.lua')
eq(lhDefs.HARDMOUNTAIN_WALL4._checker_town_source.id,'HARDMOUNTAIN_WALL4','TW2 nice_tiler mountain variant stamped')
eq(lhDefs.FLOOR_ROAD_STONE._checker_town_source.file,lhFile,'TW2 zone-local plaza road stamped')
eq(lhDefs.HARDWALL._checker_grid_source.file,'/data/general/grids/basic.lua','TW2 nested wall keeps general stamp')
eq(elDefs.OLD_FLOOR._checker_town_source.file,elFile,'TW2 Elvala list stamps nested basic.lua')
eq(elDefs.FLOOR_ROAD_STONE,nil,'TW2 Elvala has no plaza road definition')
-- Runtime NicerTiles layers seen in the fixture probe.
local function mountainRuntime(id)
 local g=deep(lhDefs[id])
 g.add_displays={setmetatable({image='invis.png',add_mos={{image='terrain/mountain4.png'},{image='terrain/mountain3i.png'}}},meta),
  setmetatable({image=g.image,z=3},meta),setmetatable({image='terrain/mountain7.png',z=17},meta),setmetatable({image='terrain/mountain9.png',z=18},meta)}
 return g
end
local function roadRuntime()
 local g=deep(lhDefs.FLOOR_ROAD_STONE)
 g.add_displays={setmetatable({image='invis.png',add_mos={{image='terrain/marble_water/marble_floor_2_to_water_outer_4.png'},
  {image='terrain/road_oldstone/road_vertical_a_03.png'}}},meta)}
 return g
end
for id,kind in pairs{GRASS='grass',GRASS_PATCH3='grass',TREE7='tree',GRASS_ROAD_STONE='road',DEEP_WATER='deep',
 GRASS_UP_WILDERNESS='exit',FLOOR_ROAD_STONE='road',HARDMOUNTAIN_WALL='mountain',HARDMOUNTAIN_WALL3='mountain'} do
 eq(T.batch4Kind(methods.clone(lhDefs[id]),'town-last-hope'),kind,'TW2 Last Hope exact '..id)
 local c=deep(lhDefs[id]);c._checker_town_source=nil
 eq(T.batch4Kind(c,'town-last-hope'),nil,'TW2 unstamped (old-save) Last Hope grid stays native '..id)
 eq(T.batch4Kind(methods.clone(lhDefs[id]),'town-elvala'),nil,'TW2 Last Hope list is not Elvala '..id)
 eq(T.batch4Kind(methods.clone(lhDefs[id]),'town-derth'),nil,'TW2 Last Hope list is not Derth '..id)
 eq(T.batch4Kind(methods.clone(lhDefs[id]),'caldera'),nil,'TW2 town family is zone scoped '..id)
end
for id,kind in pairs{GRASS='grass',GRASS_PATCH9='grass',TREE12='tree',DEEP_WATER='deep',GRASS_UP_WILDERNESS='exit'} do
 eq(T.batch4Kind(methods.clone(elDefs[id]),'town-elvala'),kind,'TW2 Elvala exact '..id)
 eq(T.batch4Kind(methods.clone(elDefs[id]),'town-last-hope'),nil,'TW2 Elvala list is not Last Hope '..id)
end
eq(T.batch4Kind(roadRuntime(),'town-last-hope'),'road','TW2 plaza road with native road/marble-water layers')
eq(T.batch4Kind(mountainRuntime('HARDMOUNTAIN_WALL'),'town-last-hope'),'mountain','TW2 mountain with native editer layers')
eq(T.batch4Kind(mountainRuntime('HARDMOUNTAIN_WALL5'),'town-last-hope'),'mountain','TW2 mountain variant with native layers')
for _,id in ipairs{'MOUNTAIN_WALL','MOUNTAIN_WALL2','ROCKY_GROUND','ROCKY_SNOWY_TREE','ROCKY_UP_WILDERNESS','FLOOR','HARDWALL','OLD_FLOOR','FAR_EAST_PORTAL','CFAR_EAST_PORTAL'} do
 if lhDefs[id] then eq(T.batch4Kind(methods.clone(lhDefs[id]),'town-last-hope'),nil,'TW2 other identity not a forest/mountain kind '..id) end
end
eq(T.rockKind(mountainRuntime('HARDMOUNTAIN_WALL'),true),nil,'TW2 hard mountain is not Daikara MOUNTAIN_WALL')
for _,mutation in ipairs{
 {'FLOOR_ROAD_STONE',function(c) c.block_sight=true end},{'FLOOR_ROAD_STONE',function(c) c.does_block_move=true end},
 {'FLOOR_ROAD_STONE',function(c) c.road='dirt' end},{'FLOOR_ROAD_STONE',function(c) c.change_level=1 end},
 {'FLOOR_ROAD_STONE',function(c) c.notice=true end},{'FLOOR_ROAD_STONE',function(c) c.orb_portal={change_zone='wilderness'} end},
 {'FLOOR_ROAD_STONE',function(c) c.on_stand=function() end end},{'FLOOR_ROAD_STONE',function(c) c.image='terrain/oldstone_floor.png' end},
 {'FLOOR_ROAD_STONE',function(c) c.add_displays={{image='terrain/farportal-base.png',display_x=-1,display_y=-1,display_w=3,display_h=3}} end},
 {'FLOOR_ROAD_STONE',function(c) c.add_mos={{image='terrain/road_oldstone/road_vertical_a_01.png'}} end},
 {'HARDMOUNTAIN_WALL',function(c) c.dig='ROCKY_GROUND' end},{'HARDMOUNTAIN_WALL',function(c) c.can_pass={pass_wall=1} end},
 {'HARDMOUNTAIN_WALL',function(c) c.block_esp=nil end},{'HARDMOUNTAIN_WALL',function(c) c.block_sense=nil end},
 {'HARDMOUNTAIN_WALL',function(c) c.does_block_move=nil end},{'HARDMOUNTAIN_WALL',function(c) c.air_level=-10 end},
 {'HARDMOUNTAIN_WALL',function(c) c.pass_projectile=true end},{'HARDMOUNTAIN_WALL',function(c) c.on_stand=function() end end},
 {'HARDMOUNTAIN_WALL3',function(c) c.image='terrain/mountain5_4.png' end},
 {'HARDMOUNTAIN_WALL',function(c) c.add_displays={{image='invis.png'},{image='terrain/rocky_mountain.png',z=3},{image='terrain/lava.png',z=17}} end},
} do
 local c=deep(lhDefs[mutation[1]]);mutation[2](c)
 eq(T.batch4Kind(c,'town-last-hope'),nil,'TW2 altered rule field stays native '..mutation[1])
end
-- Statues from the real map file (quickEntity: Grid.new of the literal table).
local qe,tiles={},{}
do
 local chunk=assert(loadstring(readFile(data..'/maps/towns/last-hope.lua'),'@/data/maps/towns/last-hope.lua'))
 setfenv(chunk,setmetatable({colors=colors,_t=function(s) return s end,mod={class={Grid={new=function(t) return setmetatable(t,meta) end}}},
  quickEntity=function(c,e) qe[c]=setmetatable(e,meta) end,defineTile=function(c,g,o,a,trap) tiles[c]={g,trap} end,
  addSpot=function() end,addZone=function() end},{__index=_G}))
 chunk()
end
local statueArt={['@']='statue_tolak',Z='statue_toknor',Y='statue_mirvenia',X='monument_allied_kingdoms'}
for c,art in pairs(statueArt) do
 local kind,layer=T.townStatue(methods.clone(qe[c]),'town-last-hope')
 eq(kind,'statue','TW2 exact Last Hope statue '..c)
 eq(layer.image,'terrain/statues/'..art..'.png','TW2 statue keeps its native art '..c)
 eq(T.batch4Kind(methods.clone(qe[c]),'town-last-hope'),'statue','TW2 statue batch kind '..c)
 eq(T.batch4Kind(methods.clone(qe[c]),'town-elvala'),nil,'TW2 statue only in Last Hope '..c)
 eq(T.batch4Kind(methods.clone(qe[c]),'town-derth'),nil,'TW2 statue not in Derth '..c)
 eq(T.batch4Kind(methods.clone(qe[c]),'beach'),nil,'TW2 statue not in other families '..c)
end
for _,mutation in ipairs{
 function(c) c.block_move=function() return true end end,
 function(c) c.add_displays={setmetatable({image='terrain/statues/statue_toknor.png',z=18,display_y=-1,display_h=2},meta)} end,
 function(c) c.add_displays[1]=deep(c.add_displays[1]);c.add_displays[1].display_y=0 end,
 function(c) c.add_displays[#c.add_displays+1]={image='terrain/lava.png'} end,
 function(c) c.does_block_move=true end,function(c) c.block_sight=true end,function(c) c.on_stand=function() end end,
 function(c) c.change_level=1 end,function(c) c.define_as='STATUE' end,function(c) c.image='terrain/marble_floor.png' end,
 function(c) c.add_mos={{image='terrain/flower_01.png'}} end,function(c) c.type='wall' end,
} do
 local c=deep(qe['@']);mutation(c)
 eq(T.batch4Kind(c,'town-last-hope'),nil,'TW2 altered statue stays native')
end
eq(tiles['1'][2],'SWORD_WEAPON_STORE','TW2 Last Hope shops are trap-layer entities over HARDWALL')
eq(tiles['E'][1],'HARDWALL','TW2 Elder door is a HARDWALL grid with a trap-layer chat entity')
-- Stone gates and exact classify.
eq(T.variant({short_name='town-last-hope'}),'TOWN_LAST_HOPE','TW2 Last Hope stone gate')
eq(T.variant({short_name='town-elvala'}),'TOWN_ELVALA','TW2 Elvala stone gate')
eq(T.combined['town-last-hope'] and T.combined['town-elvala'],true,'TW2 towns combine forest and stone')
env.game={zone={short_name='town-last-hope'}}
for id,kind in pairs{HARDWALL='hardwall',HARDWALL_SOUTH5='hardwall',HARDWALL_NORTH3='hardwall',HARDWALL_PILLAR_6='hardwall',FLOOR='floor'} do
 eq(T.classify(methods.clone(lhDefs[id])),kind,'TW2 Last Hope exact '..id)
 eq(T.classify(methods.clone(elDefs[id])),nil,'TW2 Elvala-listed '..id..' is not Last Hope stone')
end
local lhWall=deep(lhDefs.HARDWALL);lhWall._checker_town_source=nil
eq(T.classify(lhWall),nil,'TW2 old-save wall (no town stamp) stays native')
eq(T.classify(methods.clone(lhDefs.FLOOR_ROAD_STONE)),nil,'TW2 plaza road is not stone floor')
-- S14 draws the exact stamped quest farportal (tests/terrain_s14.lua); without
-- its S14 stamp (a pre-S14 save) the TW2 town contract keeps it native.
for _,id in ipairs{'CFAR_EAST_PORTAL','FAR_EAST_PORTAL'} do
 local c=methods.clone(lhDefs[id]);c._checker_s14_source=nil
 eq(T.classify(c),nil,'TW2 quest farportal without the S14 stamp stays native '..id)
end
eq(T.classify(mountainRuntime('HARDMOUNTAIN_WALL')),nil,'TW2 mountain is not a stone wall')
env.game={zone={short_name='town-elvala'}}
eq(T.classify(methods.clone(elDefs.OLD_FLOOR)),'floor','TW2 Elvala old-stone plaza')
eq(T.classify(methods.clone(elDefs.HARDWALL_NORTH2)),'hardwall','TW2 Elvala wall')
local fr=deep(elDefs.HARDWALL_SOUTH);fr.add_mos={{image='terrain/dungeonwalls_grass/grass_granite_wall2.png',display_y=0.5}}
eq(T.classify(fr),'hardwall','TW2 Elvala wall with the exact native grass fringe')
fr=deep(elDefs.HARDWALL_SOUTH);fr.add_mos={{image='terrain/dungeonwalls_grass/grass_granite_wall2.png',display_y=0.4}}
eq(T.classify(fr),nil,'TW2 Elvala wall with a changed fringe stays native')

-- Scene: Last Hope window (road across plaza, walls with a shop, mountain
-- pair, statue among grass). Remembered install, refined/native/refined.
T.assets={ready=true,revision='tw2-test',files=setmetatable({},{__index=function(_,k) return type(k)=='string' and k:match('^checker%-revised%+refined/korpul/') and true or nil end})}
local lplan2={
 '.@.&&',
 '._ &.',
 '#_  ~',
 '#1#_~'}
local lsym2={['.']='GRASS',['&']='HARDMOUNTAIN_WALL',['_']='FLOOR_ROAD_STONE',[' ']='FLOOR',['#']='HARDWALL',['1']='HARDWALL',['~']='DEEP_WATER'}
local function lhMap()
 return townMap(5,4,function(x,y)
  local c=lplan2[y+1]:sub(x+1,x+1)
  if c=='@' then return qe['@'] end
  if c=='&' then return mountainRuntime('HARDMOUNTAIN_WALL') end
  if c=='_' then return roadRuntime() end
  return lhDefs[lsym2[c]]
 end)
end
local sm=lhMap()
local store={define_as='SWORD_WEAPON_STORE',name='store',image='store/shop_door.png',z=18,block_move=function() return true end}
sm(1,3,TRAP,store)
local storeRules={};for k,v in pairs(sm(1,3,1)) do storeRules[k]=v end
local statueFn=rawget(sm(1,0,1),'block_move')
env.game={zone={short_name='town-last-hope'}}
mode='refined'
local sh={zone={short_name='town-last-hope'},level={map=sm,data={all_remembered=true}}}
T.apply(sh)
eq(sh.checker_mode,'refined','TW2 Last Hope refined mode')
eq(sm(0,0,1).replace_display.image,'checker-revised+refined/grass0.png','TW2 grass')
local st=sm(1,0,1).replace_display
eq(st.image,'checker-revised+refined/grass1.png','TW2 statue base is board grass')
eq(st.add_displays and #st.add_displays,1,'TW2 statue keeps exactly its prop layer')
eq(st.add_displays[1].image,'terrain/statues/statue_tolak.png','TW2 statue prop art')
eq(st.add_displays[1].z,18,'TW2 statue prop z')
eq(st.add_displays[1].display_y,-1,'TW2 statue prop display_y')
eq(st.add_displays[1].display_h,2,'TW2 statue prop display_h')
eq(rawget(sm(1,0,1),'block_move'),statueFn,'TW2 statue lore callback untouched')
eq(sm(1,0,1).add_displays[1].image,'terrain/statues/statue_tolak.png','TW2 statue grid layers untouched')
eq(sm(3,0,1).replace_display.image,'checker-revised+refined/daikara/mountain-wall-61.png','TW2 mountain mask (E,S) Daikara art')
eq(sm(4,0,1).replace_display.image,'checker-revised+refined/daikara/mountain-wall-80.png','TW2 mountain mask (W)')
eq(sm(3,1,1).replace_display.image,'checker-revised+refined/daikara/mountain-wall-10.png','TW2 mountain mask (N)')
eq(sm(1,1,1).replace_display.image,'checker-revised+refined/town/road0.png','TW2 plaza road is board road (TW7 stone slabs)')
eq(sm(3,3,1).replace_display.image,'checker-revised+refined/town/road0.png','TW2 plaza road by water (TW7 stone slabs)')
eq(sm(4,2,1).replace_display.image:match('^checker%-revised%+refined/deep')~=nil,true,'TW2 moat water')
eq(sm(2,1,1).replace_display,nil,'TW2 plaza floor is stone, not forest')
eq(T.render(sm,2,1,sm(2,1,1),'refined').image:match('^checker%-revised%+refined/korpul/floor')~=nil,true,'TW2 remembered plaza floor is board floor')
eq(T.render(sm,0,2,sm(0,2,1),'refined').image,T.assetPath('hardwall',nil,4,0,0,2),'TW2 remembered wall mask (S)')
eq(T.render(sm,1,3,sm(1,3,1),'refined').image,T.assetPath('hardwall',nil,10,0,1,3),'TW2 shop wall mask (E,W)')
eq(sm(1,3,TRAP),store,'TW2 shop trap-layer object untouched')
for k,v in pairs(storeRules) do eq(sm(1,3,1)[k],v,'TW2 shop wall field '..tostring(k)) end
local r10=sm(1,0,1).replace_display
mode='blockout';T.apply(sh)
eq(sm(1,0,1).replace_display.image,'checker-revised+tree1.png','TW2 blockout statue reads as blocking')
eq(sm(3,0,1).replace_display.image,'checker-revised+tree1.png','TW2 blockout mountain reads as blocking')
mode='vanilla';T.apply(sh)
eq(sm(1,0,1).replace_display,nil,'TW2 native mode restores statue')
eq(sm(3,0,1).replace_display,nil,'TW2 native mode restores mountain')
eq(sm(1,1,1).replace_display,nil,'TW2 native mode restores plaza road')
eq(T.render(sm,0,2,sm(0,2,1),'vanilla').image,lhDefs.HARDWALL.image,'TW2 native mode restores wall snapshot')
mode='refined';T.apply(sh)
eq(sm(1,0,1).replace_display.image,r10.image,'TW2 refined restore statue base')
eq(sm(1,0,1).replace_display.add_displays[1].image,'terrain/statues/statue_tolak.png','TW2 refined restore statue prop')
-- Old save: the level's grids carry no town stamp; the statue stays native too.
local om=townMap(3,3,function(x,y)
 if x==1 and y==1 then return qe['@'] end
 local g=deep(lhDefs.GRASS);g._checker_town_source=nil;return g
end)
local oh={zone={short_name='town-last-hope'},level={map=om,data={all_remembered=true}}}
T.apply(oh)
for x=0,2 do for y=0,2 do eq(om(x,y,1).replace_display,nil,'TW2 old-save Last Hope stays native '..x..','..y) end end
-- Elvala window: old-stone plaza, walls with fringe, grass, water.
local eplan={'~..#','.__#','t_2#'}
local esym={['~']='DEEP_WATER',['.']='GRASS',['#']='HARDWALL',['2']='HARDWALL',['_']='OLD_FLOOR',t='TREE7'}
local em=townMap(4,3,function(x,y) return elDefs[esym[eplan[y+1]:sub(x+1,x+1)]] end)
em(2,2,TRAP,store)
env.game={zone={short_name='town-elvala'}}
local eh={zone={short_name='town-elvala'},level={map=em,data={all_remembered=true}}}
T.apply(eh)
eq(em(1,0,1).replace_display.image,'checker-revised+refined/grass1.png','TW2 Elvala grass')
eq(em(0,2,1).replace_display.image:match('^checker%-revised%+refined/tree%-')~=nil,true,'TW2 Elvala tree')
eq(T.render(em,1,1,em(1,1,1),'refined').image:match('^checker%-revised%+refined/korpul/floor')~=nil,true,'TW2 Elvala old-stone plaza board floor')
eq(T.render(em,3,1,em(3,1,1),'refined').image,T.assetPath('hardwall',nil,5,0,3,1),'TW2 Elvala wall mask (N,S)')
eq(em(2,2,TRAP),store,'TW2 Elvala shop trap untouched')
-- Other gated towns and other zones: the TW2 identities do not leak.
env.game={zone={short_name='town-derth'}}
eq(T.classify(methods.clone(lhDefs.HARDWALL)),nil,'TW2 Last Hope wall is not a Derth wall')
local dz={zone={short_name='daikara'},level={map=townMap(2,1,function() return mountainRuntime('HARDMOUNTAIN_WALL') end),data={}}}
env.game={zone=dz.zone}
T.apply(dz)
eq(dz.level.map(0,0,1).replace_display,nil,'TW2 hard mountain stays native in Daikara')

-- TW3: Zigur, Angolwen and the Iron Council. Town lists loaded like
-- Grid:loadList with their real chunk names (callback file and line are the
-- game's). Every TW3 identity needs its own town's list stamp, its full rule
-- contract and only its native layers; shops stay on the trap layer.
local zgFile,anFile,icFile='/data/zones/town-zigur/grids.lua','/data/zones/town-angolwen/grids.lua','/data/zones/town-iron-council/grids.lua'
local zgDefs,anDefs,icDefs=loadDefs(zgFile),loadDefs(anFile),loadDefs(icFile)
eq(zgDefs.LAVA._checker_town_source.file,zgFile,'TW3 Zigur list stamps its lava pit')
eq(zgDefs.SAND._checker_town_source.file,zgFile,'TW3 Zigur list stamps nested sand.lua')
eq(zgDefs.SAND._checker_surface_sand_source.file,'/data/general/grids/sand.lua','TW3 nested sand keeps its sand.lua stamp')
eq(anDefs.HARDMOUNTAIN_WALL2._checker_town_source.file,anFile,'TW3 Angolwen list stamps nested mountain.lua')
eq(anDefs.FOUNTAIN._checker_town_source.id,'FOUNTAIN','TW3 Angolwen fountain stamped')
eq(icDefs.CRYSTAL_WALL12._checker_town_source.file,icFile,'TW3 Iron Council crystal wall stamped')
eq(icDefs.DEEP_BELLOW._checker_grid_source.id,'DOWN','TW3 council exit inherits only the DOWN general stamp')
eq(icDefs.STATUE3._checker_grid_source,nil,'TW3 council statue has no general stamp')
eq(zgDefs.CLOSED_GATE~=nil and zgDefs.OPEN_GATE~=nil,true,'TW3 Zigur gates are defined (the map never places them)')
-- Runtime NicerTiles layers seen in the fixture probe.
local function carriers(g,mos)
 g=deep(g);local ms={};for i,img in ipairs(mos) do ms[i]={image=img} end
 g.add_displays={setmetatable({image='invis.png',add_mos=ms},meta)};return g
end
local function sandRuntime() return carriers(zgDefs.SAND,{'terrain/sand/sand_2_01.png','terrain/sand/sand_inner_7_01.png'}) end
local function exitRuntime(defs) return carriers(defs.GRASS_UP_WILDERNESS,{'terrain/grass/grass_2_01.png','terrain/grass/grass_inner_3_01.png'}) end
local function anMountain(id)
 local g=deep(anDefs[id])
 g.add_displays={setmetatable({image='invis.png',add_mos={{image='terrain/mountain4.png'}}},meta),
  setmetatable({image=g.image,z=3},meta),setmetatable({image='terrain/mountain8.png',z=17},meta)}
 return g
end
local function glowExit()
 local g=deep(icDefs.DEEP_BELLOW)
 g.add_displays={setmetatable({display=' ',z=17,change_zone='deep-bellow'},meta)}
 return g
end
local tw3forest={
 {'town-zigur',zgDefs,{GRASS='grass',GRASS_PATCH4='grass',TREE12='tree',DEEP_OCEAN_WATER='deep',GRASS_ROAD_STONE='road',
  GRASS_UP_WILDERNESS='exit',LAVA='lava',POST='post'}},
 {'town-angolwen',anDefs,{GRASS='grass',TREE3='tree',GRASS_ROAD_STONE='road',GRASS_UP_WILDERNESS='exit',
  HARDMOUNTAIN_WALL='mountain',HARDMOUNTAIN_WALL5='mountain',FOUNTAIN='fountain',FOUNTAIN_MAIN='fountain',ROCK='rock'}},
 {'town-iron-council',icDefs,{CRYSTAL_WALL='crystal',CRYSTAL_WALL12='crystal',CRYSTAL_WALL20='crystal'}},
}
local allTowns={'town-derth','town-lumberjack-village','town-last-hope','town-elvala','town-zigur','town-angolwen','town-iron-council',
 'town-shatur','town-point-zero'}
for _,row in ipairs(tw3forest) do
 local zone,defs=row[1],row[2]
 for id,kind in pairs(row[3]) do
  eq(T.batch4Kind(methods.clone(defs[id]),zone),kind,'TW3 exact '..zone..' '..id)
  local c=deep(defs[id]);c._checker_town_source=nil
  eq(T.batch4Kind(c,zone),nil,'TW3 unstamped (old-save) grid stays native '..zone..' '..id)
  for _,other in ipairs(allTowns) do
   if other~=zone then eq(T.batch4Kind(methods.clone(defs[id]),other),nil,'TW3 '..zone..' list is not '..other..' '..id) end
  end
  eq(T.batch4Kind(methods.clone(defs[id]),'caldera'),nil,'TW3 town family is zone scoped '..id)
  eq(T.classify(methods.clone(defs[id])),nil,'TW3 forest identity is not stone '..id)
 end
end
eq(T.batch4Kind(sandRuntime(),'town-zigur'),'sand','TW3 Zigur sand with native sand-edge carriers')
eq(T.batch4Kind(methods.clone(zgDefs.SAND),'town-zigur'),'sand','TW3 Zigur plain sand')
eq(T.batch4Kind(methods.clone(zgDefs.SAND),'beach'),'sand','TW3 South Beach sand path unchanged')
eq(T.batch4Kind(exitRuntime(zgDefs),'town-zigur'),'exit','TW3 Zigur world exit with grass-border carriers')
eq(T.batch4Kind(exitRuntime(anDefs),'town-angolwen'),'exit','TW3 Angolwen world exit with grass-border carriers')
eq(T.batch4Kind(exitRuntime(derthDefs),'town-derth'),nil,'TW3 carrier exit stays scoped to Zigur/Angolwen (Derth unchanged)')
local fe=exitRuntime(zgDefs);fe.add_displays[1].add_mos[1].image='terrain/road_dirt/road_a_01.png'
eq(T.batch4Kind(fe,'town-zigur'),nil,'TW3 exit carrier with foreign art stays native')
fe=exitRuntime(zgDefs);fe.add_displays[1].z=3
eq(T.batch4Kind(fe,'town-zigur'),nil,'TW3 exit carrier with a changed field stays native')
fe=exitRuntime(zgDefs);fe.change_zone='town-derth'
eq(T.batch4Kind(fe,'town-zigur'),nil,'TW3 exit with another destination stays native')
eq(T.batch4Kind(anMountain('HARDMOUNTAIN_WALL'),'town-angolwen'),'mountain','TW3 Angolwen mountain with native editer layers')
local fs0=sandRuntime();fs0.add_displays[1].add_mos[1].image='terrain/lava/lava_floor.png'
eq(T.batch4Kind(fs0,'town-zigur'),nil,'TW3 sand with a foreign layer stays native')
for _,id in ipairs{'FIELDS','COBBLESTONE','ROCK','CLOSED_GATE','OPEN_GATE','HARDWALL','OLD_FLOOR','FLOOR','DOOR'} do
 if zgDefs[id] then eq(T.batch4Kind(methods.clone(zgDefs[id]),'town-zigur'),nil,'TW3 Zigur non-forest/unsupported identity '..id) end
end
for _,id in ipairs{'FIELDS','COBBLESTONE','HARDWALL'} do
 eq(T.batch4Kind(methods.clone(anDefs[id]),'town-angolwen'),nil,'TW3 Angolwen non-forest/unsupported identity '..id)
end
for _,id in ipairs{'OLD_FLOOR','HARDWALL','UP_WILDERNESS','DEEP_BELLOW','ESCAPE_REKNOR','STATUE1','STATUE6'} do
 eq(T.batch4Kind(methods.clone(icDefs[id]),'town-iron-council'),nil,'TW3 Iron Council stone identity not forest '..id)
end
-- FIELDS = GRASS rules plus one cultivation MO (TW7 draws FIELDS1-4 as the board crop field; the untiled base stays native).
eq(zgDefs.FIELDS2.add_mos[1].image,'terrain/cultivation02.png','TW3 fields native crop layer')
eq(T.crystalTerrain(methods.clone(icDefs.CRYSTAL_WALL)),nil,'TW3 council crystal is not crystal.lua (no crystal stamp)')
local _,fprop=T.townProp(methods.clone(anDefs.FOUNTAIN_MAIN),'town-angolwen')
eq(fprop.image,'terrain/statues/angolwen_fountain.png','TW3 main fountain prop art')
eq(fprop.display_w..'x'..fprop.display_h..'@'..fprop.display_x..','..fprop.display_y..'z'..fprop.z,'6x5@-2.5,-2z17','TW3 main fountain prop geometry')
eq(select(2,T.townProp(methods.clone(anDefs.FOUNTAIN),'town-angolwen')),nil,'TW3 basin cell has no prop')
eq(select(2,T.townProp(methods.clone(zgDefs.POST),'town-zigur')).image,'terrain/signpost.png','TW3 post prop art')
eq(select(2,T.townProp(methods.clone(anDefs.ROCK),'town-angolwen')).image,'terrain/maze_rock.png','TW3 rock prop art')
eq(T.townProp(methods.clone(zgDefs.POST),'town-angolwen'),nil,'TW3 post prop only in Zigur')
for _,m in ipairs{
 {zgDefs,'LAVA','town-zigur',function(c) c.block_sight=true end},{zgDefs,'LAVA','town-zigur',function(c) c.does_block_move=nil end},
 {zgDefs,'LAVA','town-zigur',function(c) c.pass_projectile=true end},{zgDefs,'LAVA','town-zigur',function(c) c.on_stand=function() end end},
 {zgDefs,'LAVA','town-zigur',function(c) c.shader='lava' end},{zgDefs,'LAVA','town-zigur',function(c) c.type='floor' end},
 {zgDefs,'LAVA','town-zigur',function(c) c.add_displays={{image='terrain/lava/lava_floor1.png'}} end},
 {zgDefs,'LAVA','town-zigur',function(c) c.change_level=1 end},
 {zgDefs,'POST','town-zigur',function(c) c.on_move=function() end end},{zgDefs,'POST','town-zigur',function(c) c.on_move=nil end},
 {zgDefs,'POST','town-zigur',function(c) c.does_block_move=true end},{zgDefs,'POST','town-zigur',function(c) c.lore='zigur-other' end},
 {zgDefs,'POST','town-zigur',function(c) c.add_displays[2]={image='terrain/signpost.png'} end},
 {zgDefs,'POST','town-zigur',function(c) c.add_displays={setmetatable({image='terrain/lava.png'},meta)} end},
 {zgDefs,'POST','town-zigur',function(c) c.add_mos={{image='terrain/flower_01.png'}} end},
 {anDefs,'FOUNTAIN','town-angolwen',function(c) c.block_move=function() return true end end},
 {anDefs,'FOUNTAIN','town-angolwen',function(c) c.block_move=nil end},{anDefs,'FOUNTAIN','town-angolwen',function(c) c.does_block_move=nil end},
 {anDefs,'FOUNTAIN','town-angolwen',function(c) c.add_displays={{image='terrain/statues/angolwen_fountain.png',z=17}} end},
 {anDefs,'FOUNTAIN','town-angolwen',function(c) c.air_level=nil end},{anDefs,'FOUNTAIN','town-angolwen',function(c) c.on_stand=function() end end},
 {anDefs,'FOUNTAIN_MAIN','town-angolwen',function(c) c.add_displays[1]=deep(c.add_displays[1]);c.add_displays[1].display_w=5 end},
 {anDefs,'FOUNTAIN_MAIN','town-angolwen',function(c) c.add_displays[1]=deep(c.add_displays[1]);c.add_displays[1].z=18 end},
 {anDefs,'FOUNTAIN_MAIN','town-angolwen',function(c) c.add_displays[2]={image='terrain/lava.png'} end},
 {anDefs,'FOUNTAIN_MAIN','town-angolwen',function(c) c.block_move=function() return true end end},
 {anDefs,'FOUNTAIN_MAIN','town-angolwen',function(c) c.does_block_move=nil end},
 {anDefs,'ROCK','town-angolwen',function(c) c.block_sight=true end},{anDefs,'ROCK','town-angolwen',function(c) c.does_block_move=nil end},
 {anDefs,'ROCK','town-angolwen',function(c) c.add_displays={setmetatable({image='terrain/huge_rock.png',z=4},meta)} end},
 {icDefs,'CRYSTAL_WALL','town-iron-council',function(c) c.dig=nil end},
 {icDefs,'CRYSTAL_WALL','town-iron-council',function(c) c.can_pass={pass_wall=1,pass_tree=1} end},
 {icDefs,'CRYSTAL_WALL','town-iron-council',function(c) c.image='terrain/crystal_floor1.png' end},
 {icDefs,'CRYSTAL_WALL','town-iron-council',function(c) c.add_mos={{image='terrain/crystal_alpha1.png'}} end},
 {icDefs,'CRYSTAL_WALL','town-iron-council',function(c) c.add_displays={{image='terrain/crystal_alpha1.png',z=10}} end},
 {icDefs,'CRYSTAL_WALL','town-iron-council',function(c) c.block_sense=true end},
 {icDefs,'CRYSTAL_WALL','town-iron-council',function(c) c.does_block_move=nil end},
} do
 local c=deep(m[1][m[2]]);m[4](c)
 eq(T.batch4Kind(c,m[3]),nil,'TW3 altered rule field stays native '..m[2])
end
-- Stone gates and exact classify.
eq(T.variant({short_name='town-zigur'}),'TOWN_ZIGUR','TW3 Zigur stone gate')
eq(T.variant({short_name='town-angolwen'}),'TOWN_ANGOLWEN','TW3 Angolwen stone gate')
eq(T.variant({short_name='town-iron-council'}),'TOWN_IRON_COUNCIL','TW3 Iron Council stone gate')
eq(T.combined['town-zigur'] and T.combined['town-angolwen'] and T.combined['town-iron-council'],true,'TW3 towns combine forest and stone')
local tw3stone={
 {'town-zigur',zgDefs,{HARDWALL='hardwall',HARDWALL_SOUTH3='hardwall',HARDWALL_NORTH2='hardwall',OLD_FLOOR='floor',FLOOR='floor',
  DOOR_HORIZ='door-closed',ROCK='prop'}},
 {'town-angolwen',anDefs,{HARDWALL='hardwall',HARDWALL_NORTH_SOUTH='hardwall',HARDWALL_PILLAR_6='hardwall'}},
 {'town-iron-council',icDefs,{HARDWALL='hardwall',HARDWALL_SOUTH11='hardwall',OLD_FLOOR='floor',UP_WILDERNESS='stairs-world',
  ESCAPE_REKNOR='stairs-down',DEEP_BELLOW='stairs-down',STATUE1='prop',STATUE2='prop',STATUE3='prop',STATUE4='prop',STATUE5='prop',STATUE6='prop'}},
}
for _,row in ipairs(tw3stone) do
 local zone,defs=row[1],row[2]
 for id,kind in pairs(row[3]) do
  env.game={zone={short_name=zone}}
  eq(T.classify(methods.clone(defs[id])),kind,'TW3 exact stone '..zone..' '..id)
  local c=deep(defs[id]);c._checker_town_source=nil
  eq(T.classify(c),nil,'TW3 old-save stone stays native '..zone..' '..id)
  for _,other in ipairs(allTowns) do
   if other~=zone then env.game={zone={short_name=other}};eq(T.classify(methods.clone(defs[id])),nil,'TW3 '..zone..' stone is not '..other..' '..id) end
  end
 end
end
env.game={zone={short_name='town-iron-council'}}
eq(T.classify(glowExit()),'stairs-down','TW3 Deep Bellow with its image-less glow display')
for _,f in ipairs{
 function(c) c.change_zone='wilderness' end,function(c) c.change_level=2 end,function(c) c.change_level_check=function() end end,
 function(c) c.glow=nil end,function(c) c.add_displays[1]=deep(c.add_displays[1]);c.add_displays[1].image='terrain/lava.png' end,
 function(c) c.add_displays[2]={image='terrain/worldmap.png'} end,function(c) c.add_mos={{image='terrain/stair_up.png'}} end,
 function(c) c.does_block_move=true end,function(c) c.on_stand=function() end end,function(c) c.image='terrain/oldstone_floor.png' end,
} do
 local c=glowExit();f(c)
 eq(T.classify(c),nil,'TW3 altered council exit stays native')
end
local ex=deep(icDefs.ESCAPE_REKNOR);ex.change_zone_auto_stairs=nil
eq(T.classify(ex),nil,'TW3 Reknor escape without auto stairs stays native')
ex=deep(icDefs.ESCAPE_REKNOR);ex.glow=true
eq(T.classify(ex),nil,'TW3 Reknor escape with a glow stays native')
ex=deep(icDefs.ESCAPE_REKNOR);ex.change_level=1
eq(T.classify(ex),nil,'TW3 Reknor escape to another level stays native')
for _,f in ipairs{
 function(c) c.block_move=function() return true end end,function(c) c.does_block_move=nil end,function(c) c.block_sight=nil end,
 function(c) c.add_displays={setmetatable({image='terrain/statues/statue_dwarf_mage.png',z=18,display_y=-1,display_h=2},meta)} end,
 function(c) c.add_displays[1]=deep(c.add_displays[1]);c.add_displays[1].display_y=0 end,
 function(c) c.add_displays[2]={image='terrain/lava.png'} end,function(c) c.image='terrain/marble_floor.png' end,
 function(c) c.change_level=1 end,function(c) c.on_stand=function() end end,function(c) c.dig='OLD_FLOOR' end,
} do
 local c=deep(icDefs.STATUE1);f(c)
 eq(T.classify(c),nil,'TW3 altered council statue stays native')
end
env.game={zone={short_name='town-zigur'}}
for _,f in ipairs{function(c) c.block_sight=nil end,function(c) c.z=3 end,function(c) c.dig='FLOOR' end,
 function(c) c.add_displays={setmetatable({image='terrain/maze_rock.png',z=2},meta)} end,function(c) c.block_esp=nil end} do
 local c=deep(zgDefs.ROCK);f(c)
 eq(T.classify(c),nil,'TW3 altered Zigur rock stays native')
end
for _,id in ipairs{'COBBLESTONE','CLOSED_GATE','OPEN_GATE','LAVA','POST','FIELDS3'} do eq(T.classify(methods.clone(zgDefs[id])),nil,'TW3 Zigur '..id..' is not stone') end
env.game={zone={short_name='town-angolwen'}}
for _,id in ipairs{'COBBLESTONE','ROCK','FOUNTAIN','FIELDS'} do eq(T.classify(methods.clone(anDefs[id])),nil,'TW3 Angolwen '..id..' is not stone') end

-- Zigur window: lava ring round the arena floor with a rock, the post on
-- grass, sand shore, and a shop wall (trap layer).
local zplan={
 ',~.&.',
 ',.==.',
 '#=:R=',
 '#2==.'}
local zsym={[',']='SAND',['~']='DEEP_OCEAN_WATER',['.']='GRASS',['&']='POST',['=']='LAVA',[':']='OLD_FLOOR',R='ROCK',['#']='HARDWALL',['2']='HARDWALL'}
local zm=townMap(5,4,function(x,y) return zgDefs[zsym[zplan[y+1]:sub(x+1,x+1)]] end)
local zstore={define_as='SWORD_WEAPON_STORE',name='store',image='store/shop_door.png',z=18,block_move=function() return true end}
zm(1,3,TRAP,zstore)
local zStoreRules={};for k,v in pairs(zm(1,3,1)) do zStoreRules[k]=v end
local postFn=rawget(zm(3,0,1),'on_move')
env.game={zone={short_name='town-zigur'}}
mode='refined'
local zh={zone={short_name='town-zigur'},level={map=zm,data={all_remembered=true}}}
T.apply(zh)
eq(zh.checker_mode,'refined','TW3 Zigur refined mode')
eq(zm(0,0,1).replace_display.image,'checker-revised+refined/beach/sand0.png','TW3 Zigur sand shore (South Beach sand)')
eq(zm(1,0,1).replace_display.image:match('^checker%-revised%+refined/deep')~=nil,true,'TW3 Zigur ocean')
local post=zm(3,0,1).replace_display
eq(post.image,'checker-revised+refined/grass1.png','TW3 post base is board grass')
eq(#post.add_displays,1,'TW3 post keeps exactly its sign')
eq(post.add_displays[1].image,'terrain/signpost.png','TW3 post sign art')
eq(post.add_displays[1].z,nil,'TW3 post sign z unchanged')
eq(rawget(zm(3,0,1),'on_move'),postFn,'TW3 post lore callback untouched')
eq(zm(2,1,1).replace_display.image,'checker-revised+refined/burnt/lava-2-1.png','TW3 lava mask (E)')
eq(zm(3,1,1).replace_display.image,'checker-revised+refined/burnt/lava-8-0.png','TW3 lava mask (W)')
eq(zm(1,3,1).replace_display,nil,'TW3 shop wall is stone, not forest')
eq(zm(2,2,1).replace_display,nil,'TW3 arena floor is stone')
eq(T.render(zm,2,2,zm(2,2,1),'refined').image:match('^checker%-revised%+refined/korpul/floor')~=nil,true,'TW3 remembered arena floor is board floor')
local rock=T.render(zm,3,2,zm(3,2,1),'refined')
eq(rock.image:match('^checker%-revised%+refined/korpul/floor')~=nil,true,'TW3 rock base is board floor')
eq(rock.add_displays and #rock.add_displays,1,'TW3 rock keeps exactly its prop')
eq(rock.add_displays[1].image..'@'..rock.add_displays[1].z,'terrain/huge_rock.png@2','TW3 rock prop art and z')
eq(zm(3,2,1).add_displays[1].image,'terrain/huge_rock.png','TW3 rock grid layer untouched')
eq(T.render(zm,0,3,zm(0,3,1),'refined').image,T.assetPath('hardwall',nil,3,1,0,3),'TW3 Zigur wall mask (N,E)')
eq(zm(1,3,TRAP),zstore,'TW3 Zigur shop trap-layer object untouched')
for k,v in pairs(zStoreRules) do eq(zm(1,3,1)[k],v,'TW3 Zigur shop wall field '..tostring(k)) end
local zr=zm(2,1,1).replace_display
mode='blockout';T.apply(zh)
eq(zm(2,1,1).replace_display.image,'checker-revised+tree1.png','TW3 blockout lava reads as blocking')
eq(zm(3,0,1).replace_display.image,'checker-revised+grass1.png','TW3 blockout post reads as walkable')
mode='vanilla';T.apply(zh)
for _,c in ipairs{{0,0},{2,1},{3,0}} do eq(zm(c[1],c[2],1).replace_display,nil,'TW3 native mode restores Zigur '..c[1]..','..c[2]) end
eq(T.render(zm,3,2,zm(3,2,1),'vanilla').add_displays[1].image,'terrain/huge_rock.png','TW3 native mode restores rock snapshot')
eq(T.render(zm,3,2,zm(3,2,1),'vanilla').image,'terrain/oldstone_floor.png','TW3 native mode restores rock base')
mode='refined';T.apply(zh)
eq(zm(2,1,1).replace_display.image,zr.image,'TW3 refined restore lava')
eq(zm(3,0,1).replace_display.add_displays[1].image,'terrain/signpost.png','TW3 refined restore post sign')
eq(T.render(zm,3,2,zm(3,2,1),'refined').add_displays[1].image,'terrain/huge_rock.png','TW3 refined restore rock prop')
-- Old save: no town stamps anywhere; nothing is drawn.
local zo=townMap(3,2,function(x,y) local g=deep(zgDefs[({'LAVA','POST','SAND'})[x+1]]);g._checker_town_source=nil;return g end)
local zoh={zone={short_name='town-zigur'},level={map=zo,data={all_remembered=true}}}
T.apply(zoh)
for x=0,2 do for y=0,1 do eq(zo(x,y,1).replace_display,nil,'TW3 old-save Zigur stays native '..x..','..y) end end

-- Angolwen window: fountain basin (4 basin cells round the main one), a rock,
-- mountain, road and a shop wall. Not all_remembered: stone waits for sight.
local aplan={
 '^_F_#',
 '_FMF4',
 'R_F_.'}
local asym={['^']='HARDMOUNTAIN_WALL',['_']='GRASS_ROAD_STONE',F='FOUNTAIN',M='FOUNTAIN_MAIN',['#']='HARDWALL',['4']='HARDWALL',R='ROCK',['.']='GRASS'}
local am=townMap(5,3,function(x,y) return anDefs[asym[aplan[y+1]:sub(x+1,x+1)]] end)
local astore={define_as='STAVES',name='store',image='store/shop_door.png',z=18,block_move=function() return true end}
am(4,1,TRAP,astore)
local fountainFn=rawget(am(2,0,1),'block_move')
env.game={zone={short_name='town-angolwen'}}
local ah={zone={short_name='town-angolwen'},level={map=am,data={}}}
T.apply(ah)
eq(ah.checker_mode,'refined','TW3 Angolwen refined mode')
eq(am(0,0,1).replace_display.image,'checker-revised+refined/daikara/mountain-wall-00.png','TW3 Angolwen mountain (Daikara art)')
eq(am(2,0,1).replace_display.image,'checker-revised+refined/deep4-0-0.png','TW3 basin cell deep mask (S)')
eq(am(1,1,1).replace_display.image,'checker-revised+refined/deep2-0-0.png','TW3 basin cell deep mask (E)')
local main=am(2,1,1).replace_display
eq(main.image,'checker-revised+refined/deep15-1-0.png','TW3 main fountain is basin water (all four)')
eq(#main.add_displays,1,'TW3 main fountain keeps exactly its statue')
local fd=main.add_displays[1]
eq(fd.image..'|'..fd.z..'|'..fd.display_x..'|'..fd.display_y..'|'..fd.display_w..'|'..fd.display_h,
 'terrain/statues/angolwen_fountain.png|17|-2.5|-2|6|5','TW3 main fountain 6x5 overlay exact')
eq(am(2,0,1).replace_display.add_displays,nil,'TW3 basin cell has no extra layer')
eq(rawget(am(2,0,1),'block_move'),fountainFn,'TW3 fountain lore callback untouched')
eq(am(2,0,1).does_block_move,true,'TW3 fountain still blocks movement')
local ar=am(0,2,1).replace_display
eq(ar.image,'checker-revised+refined/grass0.png','TW3 rock base is board grass')
eq(ar.add_displays[1].image..'@'..ar.add_displays[1].z,'terrain/maze_rock.png@4','TW3 magical rock prop')
eq(am(4,0,1).replace_display,nil,'TW3 Angolwen shop wall is stone')
eq(am._checker_korpul,nil,'TW3 Angolwen (not all_remembered) creates no hidden records')
eq(T.render(am,4,0,am(4,0,1),'refined'),nil,'TW3 Angolwen unseen wall stays native')
am.seen[4+0*5]=true;am.seen[4+1*5]=true
eq(T.observe(am,4,0,am(4,0,1)),true,'TW3 Angolwen seen wall observed')
T.observe(am,4,1,am(4,1,1))
eq(T.render(am,4,1,am(4,1,1),'refined').image,T.assetPath('hardwall',nil,1,1,4,1),'TW3 Angolwen shop wall mask (N)')
eq(am(4,1,TRAP),astore,'TW3 Angolwen shop trap untouched')
mode='blockout';T.apply(ah)
eq(am(2,1,1).replace_display.image,'checker-revised+water1.png','TW3 blockout fountain reads as water')
eq(am(0,2,1).replace_display.image,'checker-revised+tree0.png','TW3 blockout rock reads as blocking')
mode='vanilla';T.apply(ah)
for _,c in ipairs{{0,0},{2,0},{2,1},{0,2}} do eq(am(c[1],c[2],1).replace_display,nil,'TW3 native mode restores Angolwen '..c[1]..','..c[2]) end
mode='refined';T.apply(ah)
eq(am(2,1,1).replace_display.add_displays[1].image,'terrain/statues/angolwen_fountain.png','TW3 refined restore fountain overlay')
local ao=townMap(2,1,function(x,y) local g=deep(anDefs[x==0 and 'FOUNTAIN_MAIN' or 'ROCK']);g._checker_town_source=nil;return g end)
T.apply({zone={short_name='town-angolwen'},level={map=ao,data={}}})
eq(ao(0,0,1).replace_display,nil,'TW3 old-save fountain stays native');eq(ao(1,0,1).replace_display,nil,'TW3 old-save rock stays native')

-- Iron Council window: crystal cluster, statue, exits in the wall, shop wall.
local iplan={
 '#>#R#',
 '#.&&.',
 'A.&..',
 '#9#<.'}
local isym={['#']='HARDWALL',['9']='HARDWALL',['>']='DEEP_BELLOW',R='ESCAPE_REKNOR',['.']='OLD_FLOOR',['&']='CRYSTAL_WALL7',A='STATUE1',['<']='UP_WILDERNESS'}
local im=townMap(5,4,function(x,y) return icDefs[isym[iplan[y+1]:sub(x+1,x+1)]] end)
im(1,3,TRAP,zstore)
env.game={zone={short_name='town-iron-council'}}
local ih={zone={short_name='town-iron-council'},level={map=im,data={all_remembered=true}}}
T.apply(ih)
eq(ih.checker_mode,'refined','TW3 Iron Council refined mode')
eq(im(2,1,1).replace_display.image,'checker-revised+refined/crystal/wall-6-1.png','TW3 crystal wall mask (E,S)')
eq(im(3,1,1).replace_display.image,'checker-revised+refined/crystal/wall-8-0.png','TW3 crystal wall mask (W)')
eq(im(1,1,1).replace_display,nil,'TW3 council floor is stone')
local sd=T.render(im,0,2,im(0,2,1),'refined')
eq(sd.image:match('^checker%-revised%+refined/korpul/floor')~=nil,true,'TW3 statue base is board floor')
eq(#sd.add_displays,1,'TW3 statue keeps exactly its prop')
local sp=sd.add_displays[1]
eq(sp.image..'|'..sp.z..'|'..sp.display_y..'|'..sp.display_h,'terrain/statues/statue_dwarf_taxman.png|18|-1|2','TW3 statue prop exact')
eq(im(0,2,1).does_block_move and im(0,2,1).block_sight,true,'TW3 statue rules untouched')
local down=T.render(im,1,0,im(1,0,1),'refined')
eq(down.image:match('^checker%-revised%+refined/korpul/floor')~=nil,true,'TW3 Deep Bellow base is board floor')
eq(down.add_mos[1].image,'checker-revised+refined/korpul/stairs-down.png','TW3 Deep Bellow down-stairs overlay')
eq(T.render(im,3,0,im(3,0,1),'refined').add_mos[1].image,'checker-revised+refined/korpul/stairs-down.png','TW3 Reknor escape down-stairs overlay')
eq(T.render(im,3,3,im(3,3,1),'refined').add_mos[1].image,'checker-revised+refined/korpul/stairs-world.png','TW3 council world exit')
eq(im(1,0,1).change_zone..'|'..im(3,0,1).change_zone..'|'..im(3,0,1).change_level,'deep-bellow|reknor-escape|3','TW3 exit destinations untouched')
eq(T.render(im,1,3,im(1,3,1),'refined').image,T.assetPath('hardwall',nil,10,0,1,3),'TW3 council shop wall mask (E,W)')
eq(im(1,3,TRAP),zstore,'TW3 council shop trap untouched')
mode='vanilla';T.apply(ih)
eq(im(2,1,1).replace_display,nil,'TW3 native mode restores crystal')
eq(T.render(im,0,2,im(0,2,1),'vanilla').add_displays[1].image,'terrain/statues/statue_dwarf_taxman.png','TW3 native statue snapshot')
eq(T.render(im,1,0,im(1,0,1),'vanilla').add_mos[1].image,'terrain/stair_down.png','TW3 native exit snapshot')
mode='refined';T.apply(ih)
eq(im(2,1,1).replace_display.image,'checker-revised+refined/crystal/wall-6-1.png','TW3 refined restore crystal')
eq(T.render(im,0,2,im(0,2,1),'refined').add_displays[1].image,'terrain/statues/statue_dwarf_taxman.png','TW3 refined restore statue')
local io=townMap(3,1,function(x,y) local g=deep(icDefs[({'CRYSTAL_WALL','STATUE2','DEEP_BELLOW'})[x+1]]);g._checker_town_source=nil;return g end)
T.apply({zone={short_name='town-iron-council'},level={map=io,data={all_remembered=true}}})
eq(io(0,0,1).replace_display,nil,'TW3 old-save crystal stays native')
eq(next(io._checker_korpul or {}),nil,'TW3 old-save statue and exit get no stone record')

-- Native mode keeps nested native layers: their display_on_* flags are Grid
-- class defaults (not own fields) and must survive the snapshot.
local gridClass={__index=setmetatable({display_on_seen=true,display_on_remember=true,display_on_unknown=false},{__index=methods})}
local capWall=deep(icDefs.HARDWALL_NORTH2);capWall.add_displays={setmetatable({image='terrain/granite_wall3.png',z=18,display_y=-1},gridClass)}
local capStatue=deep(icDefs.STATUE4);capStatue.add_displays={setmetatable(deep(capStatue.add_displays[1]),gridClass)}
setmetatable(capStatue.add_displays[1],gridClass)
local fm=townMap(2,1,function(x) return x==0 and capWall or capStatue end)
env.game={zone={short_name='town-iron-council'}}
local fh={zone={short_name='town-iron-council'},level={map=fm,data={all_remembered=true}}}
mode='refined';T.apply(fh)
T.render(fm,0,0,fm(0,0,1),'refined');T.render(fm,1,0,fm(1,0,1),'refined')
local nw=T.render(fm,0,0,fm(0,0,1),'vanilla').add_displays[1]
eq(nw.image..'|'..tostring(nw.display_on_seen)..'|'..tostring(nw.display_on_remember)..'|'..tostring(nw.display_on_unknown),
 'terrain/granite_wall3.png|true|true|false','native mode keeps the wall cap layer visible (class default flags)')
local ns=T.render(fm,1,0,fm(1,0,1),'vanilla').add_displays[1]
eq(ns.image..'|'..tostring(ns.display_on_seen)..'|'..tostring(ns.display_on_remember),
 'terrain/statues/statue_dwarf_warrior.png|true|true','TW3 native mode keeps the statue visible')

-- Other towns and zones: TW3 identities never leak.
env.game={zone={short_name='town-derth'}}
eq(T.classify(methods.clone(icDefs.STATUE1)),nil,'TW3 council statue is not Derth stone')
eq(T.classify(methods.clone(zgDefs.HARDWALL)),nil,'TW3 Zigur wall is not a Derth wall')
local ld={zone={short_name='last-hope-graveyard'},level={map=townMap(2,1,function(x) return x==0 and zgDefs.LAVA or anDefs.FOUNTAIN_MAIN end),data={}}}
env.game={zone=ld.zone}
T.apply(ld)
eq(ld.level.map(0,0,1).replace_display,nil,'TW3 Zigur lava stays native elsewhere')
eq(ld.level.map(1,0,1).replace_display,nil,'TW3 Angolwen fountain stays native elsewhere')

-- TW4: Shatur and Point Zero. Town lists loaded like Grid:loadList (Shatur's
-- nested mountain.lua keeps its snowy_grass image rewrite); Shatur's statue
-- comes from its real map file. Every TW4 identity needs its own town's list
-- stamp, its full rule contract and only the native layers the fixture probe
-- saw; shops stay on the trap layer; Point Zero's runtime beam endpoints
-- (cloneFull + block_move) stay native. Own function: the enclosing one is
-- at Lua's 200-local limit.
;(function()
local shFile,pzFile='/data/zones/town-shatur/grids.lua','/data/zones/town-point-zero/grids.lua'
local shDefs,pzDefs=loadDefs(shFile),loadDefs(pzFile)
eq(shDefs.SNOW_ELVEN_TREE12._checker_town_source.file,shFile,'TW4 Shatur list stamps nested elven_forest.lua')
eq(shDefs.SNOWY_PATCH3._checker_town_source.id,'SNOWY_PATCH3','TW4 Shatur list stamps nested snowy_forest.lua')
eq(shDefs.ROCKY_GROUND.image,'terrain/snowy_grass.png','TW4 Shatur mountain.lua import keeps its snowy_grass rewrite')
eq(shDefs.ROCKY_GROUND._checker_town_source.file,shFile,'TW4 Shatur list stamps nested mountain.lua')
eq(shDefs.ELVEN_TREE7._checker_forest_source,nil,'TW4 elven tree has no forest.lua stamp')
eq(pzDefs.FLOATING_ROCKS_91._checker_void_source.file,'/data/general/grids/void.lua','TW4 Point Zero rocks keep the void.lua stamp')
eq(pzDefs.FLOATING_ROCKS_91._checker_town_source.file,pzFile,'TW4 Point Zero list stamps nested void.lua')
eq(pzDefs.COLD_FOREST7._checker_town_source.file,pzFile,'TW4 Point Zero cold forest stamped')
eq(pzDefs.HARDWALL._checker_grid_source.file,'/data/general/grids/basic.lua','TW4 Point Zero wall keeps its basic.lua stamp')
-- Runtime layer shapes from the fixture probe (NicerTiles borders + tree parts).
local function layered(g,displays)
 for i,d in ipairs(displays) do displays[i]=setmetatable(d,meta) end
 g.add_displays=displays;return g
end
local function elvenRuntime(id)
 return layered(deep(shDefs[id]),{{image='invis.png',z=3,add_mos={{image='terrain/grass/grass_2_01.png'},{image='terrain/trees/oak_shadow.png'},
  {image='terrain/trees/oak_trunk_01.png'}}},{image='invis.png'},{image='terrain/trees/oak_foliage_summer_03.png',z=16}})
end
local function snowRuntime(id)
 return layered(deep(shDefs[id]),{{image='invis.png',z=3,add_mos={{image='terrain/grass/snowy_grass_8_01.png'},
  {image='terrain/grass/snowy_grass_inner_1_01.png'},{image='terrain/trees/fat_elventree_shadow.png'},{image='terrain/trees/fat_elventree_trunk.png'}}},
  {image='terrain/trees/fat_elventree_foliage_winter.png',z=16}})
end
local function cobbleRuntime()
 return layered(deep(shDefs.COBBLESTONE),{{image='invis.png',add_mos={{image='terrain/marble_water/marble_floor_2_to_water_outer_4.png'}}}})
end
local function shortRuntime()
 return layered(deep(pzDefs.GRASS_SHORT),{{image='invis.png',z=3,add_mos={{image='terrain/grass_worldmap/grass_2_01.png'},
  {image='terrain/grass_worldmap/grass_inner_1_01.png'}}}})
end
local function coldRuntime(id)
 return layered(deep(pzDefs[id]),{{image='invis.png',add_mos={{image='terrain/ice/frozen_ground_8_01.png'}}},
  {image='terrain/tree_dark_snow3.png',z=17},{image='terrain/tree_dark_snow11.png',z=18}})
end
local function riftRuntime()
 local g=layered(deep(pzDefs.SPACETIME_RIFT),{{image='invis.png'},{image='terrain/rift/rift_V3_inner_7_01.png',z=17},
  {image='terrain/rift/rift_ver_edge_left_01.png'}})
 g.image='terrain/rift/rift_V3_8_01.png';return g
end
local function pzMountain(id)
 return layered(deep(pzDefs[id]),{{image='invis.png',add_mos={{image='terrain/mountain2.png'},{image='terrain/mountain3i.png'}}},
  {image=pzDefs[id].image,z=3},{image='terrain/mountain8.png',z=17}})
end
-- A beam endpoint exactly as zone.lua:99-116 builds it (cloneFull of the
-- rock, renamed, removeAllMOs/altered, exit and a block_move closure).
local function endpoint(id)
 local g=deep(pzDefs[id or 'FLOATING_ROCKS_5'])
 g.name='temporal beam endpoint';g.nice_tiler=nil;g.exit={x=1,y=1}
 g.block_move=function(self,x,y,who,act) return false end
 return g
end
local shTowns={'town-derth','town-lumberjack-village','town-last-hope','town-elvala','town-zigur','town-angolwen',
 'town-iron-council','town-shatur','town-point-zero'}
local tw4forest={
 {'town-shatur',shDefs,{GRASS='grass',GRASS_PATCH5='grass',ELVEN_TREE='tree',ELVEN_TREE12='tree',SNOW_ELVEN_TREE='snow-tree',
  SNOW_ELVEN_TREE7='snow-tree',SNOWY_GRASS='snow-ground',SNOWY_PATCH9='snow-ground',SNOWY_PATCH14='snow-ground',
  ROCKY_GROUND='snow-ground',DEEP_WATER='deep',COBBLESTONE='road',GRASS_UP_WILDERNESS='exit'}},
 {'town-point-zero',pzDefs,{GRASS_SHORT='grass',TREE9='tree',DEEP_WATER='deep',HARDMOUNTAIN_WALL='mountain',HARDMOUNTAIN_WALL3='mountain',
  COLD_FOREST='cold-tree',COLD_FOREST12='cold-tree',COLD_FOREST30='cold-tree',OUTERSPACE='void-space',FLOATING_ROCKS='void-rocks',
  FLOATING_ROCKS_5='void-rocks',FLOATING_ROCKS_91='void-rocks',FLOATING_ROCKS_3I='void-rocks',SPACETIME_RIFT='void-rift',VOID='void-floor'}},
}
for _,row in ipairs(tw4forest) do
 local zone,defs=row[1],row[2]
 for id,kind in pairs(row[3]) do
  eq(T.batch4Kind(methods.clone(defs[id]),zone),kind,'TW4 exact '..zone..' '..id)
  local c=deep(defs[id]);c._checker_town_source=nil
  eq(T.batch4Kind(c,zone),nil,'TW4 unstamped (old-save) grid stays native '..zone..' '..id)
  for _,other in ipairs(shTowns) do
   if other~=zone then eq(T.batch4Kind(methods.clone(defs[id]),other),nil,'TW4 '..zone..' list is not '..other..' '..id) end
  end
  eq(T.batch4Kind(methods.clone(defs[id]),'caldera'),nil,'TW4 town family is zone scoped '..id)
  if kind~='grass' and kind~='deep' and kind~='exit' and kind~='tree' then
   for _,fam in ipairs{'beach','meadow'} do eq(T.batch4Kind(methods.clone(defs[id]),fam),nil,'TW4 town-only kind is zone scoped '..fam..' '..id) end
  end
  env.game={zone={short_name=zone}}
  eq(T.classify(methods.clone(defs[id])),nil,'TW4 forest identity is not stone '..id)
 end
end
eq(T.batch4Kind(elvenRuntime('ELVEN_TREE9'),'town-shatur'),'tree','TW4 elven tree with native border and tree layers')
eq(T.batch4Kind(snowRuntime('SNOW_ELVEN_TREE14'),'town-shatur'),'snow-tree','TW4 snow elven tree with native snowy border and tree layers')
eq(T.batch4Kind(cobbleRuntime(),'town-shatur'),'road','TW4 Shatur bridge with its marble-to-water edge')
eq(T.batch4Kind(shortRuntime(),'town-point-zero'),'grass','TW4 short grass with world-map grass borders')
eq(T.batch4Kind(coldRuntime('COLD_FOREST4'),'town-point-zero'),'cold-tree','TW4 cold forest with ice borders and dark snowy firs')
eq(T.batch4Kind(riftRuntime(),'town-point-zero'),'void-rift','TW4 rift with native sandWalls layers')
eq(T.batch4Kind(pzMountain('HARDMOUNTAIN_WALL5'),'town-point-zero'),'mountain','TW4 Point Zero mountain with native editer layers')
-- Exactness: foreign layers, altered rules, wrong zone, runtime endpoints.
local ef=elvenRuntime('ELVEN_TREE9');ef.add_displays[1].add_mos[1].image='terrain/grass/snowy_grass_8_01.png'
eq(T.batch4Kind(ef,'town-shatur'),nil,'TW4 green elven tree with a snowy border stays native')
local sf=snowRuntime('SNOW_ELVEN_TREE14');sf.add_displays[1].add_mos[1].image='terrain/grass/grass_2_01.png'
eq(T.batch4Kind(sf,'town-shatur'),nil,'TW4 snow elven tree with a green border stays native')
sf=snowRuntime('SNOW_ELVEN_TREE14');sf.add_displays[2].image='terrain/lava/lava_floor1.png'
eq(T.batch4Kind(sf,'town-shatur'),nil,'TW4 snow tree with a foreign layer stays native')
local cf=coldRuntime('COLD_FOREST4');cf.add_displays[2].image='terrain/trees/elm_foliage_winter.png'
eq(T.batch4Kind(cf,'town-point-zero'),nil,'TW4 cold forest with a foreign tree layer stays native')
local nr=deep(shDefs.ROCKY_GROUND);nr.image='terrain/rocky_ground.png'
eq(T.batch4Kind(nr,'town-shatur'),nil,'TW4 ROCKY_GROUND without the snowy rewrite stays native')
eq(T.batch4Kind(methods.clone(shDefs.ROCKY_SNOWY_TREE),'town-shatur'),nil,'TW4 unused mountain.lua snowy tree is not claimed')
eq(T.batch4Kind(methods.clone(shDefs.MOUNTAIN_WALL),'town-shatur'),nil,'TW4 unused mountain wall is not claimed')
eq(T.batch4Kind(methods.clone(shDefs.HARDSNOWY_TREE),'town-shatur'),nil,'TW4 unused hard snowy tree is not claimed')
eq(T.batch4Kind(methods.clone(shDefs.HARDELVEN_TREE),'town-shatur'),nil,'TW4 unused hard elven tree is not claimed')
eq(T.batch4Kind(methods.clone(shDefs.AUTUMN_ELVEN_TREE),'town-shatur'),nil,'TW4 unused autumn elven tree is not claimed')
eq(T.batch4Kind(methods.clone(shDefs.snowy_UP_WILDERNESS),'town-shatur'),nil,'TW4 unused snowy exit is not claimed')
eq(T.batch4Kind(methods.clone(shDefs.SNOWY_TREE3),'town-shatur'),nil,'TW4 unused winter tree is not claimed')
eq(T.batch4Kind(methods.clone(pzDefs.RIFT),'town-point-zero'),nil,'TW4 Point Zero RIFT exit stays native')
eq(T.batch4Kind(methods.clone(pzDefs.POLAR_CAP),'town-point-zero'),nil,'TW4 unused polar cap is not claimed')
eq(T.batch4Kind(methods.clone(pzDefs.HARDWALL),'town-point-zero'),nil,'TW4 Point Zero wall is not forest')
for _,id in ipairs{'FLOATING_ROCKS_5','FLOATING_ROCKS_11','FLOATING_ROCKS_3I'} do
 eq(T.batch4Kind(endpoint(id),'town-point-zero'),nil,'TW4 runtime beam endpoint stays native '..id)
end
local ep=endpoint();ep.name='floating rocks'
eq(T.batch4Kind(ep,'town-point-zero'),nil,'TW4 endpoint keeps native even under the original name (block_move)')
ep=deep(pzDefs.FLOATING_ROCKS_5);ep.exit={x=1,y=1}
eq(T.batch4Kind(ep,'town-point-zero'),'void-rocks','TW4 an exit field alone is not a callback (rules decide)')
for _,m in ipairs{
 {shDefs,'ELVEN_TREE4','town-shatur',function(c) c.dig=nil end},{shDefs,'ELVEN_TREE4','town-shatur',function(c) c.can_pass={pass_tree=1,pass_wall=1} end},
 {shDefs,'ELVEN_TREE4','town-shatur',function(c) c.block_sense=true end},{shDefs,'ELVEN_TREE4','town-shatur',function(c) c.on_stand=function() end end},
 {shDefs,'ELVEN_TREE4','town-shatur',function(c) c.subtype='snowy_grass' end},{shDefs,'SNOW_ELVEN_TREE4','town-shatur',function(c) c.subtype='grass' end},
 {shDefs,'SNOW_ELVEN_TREE4','town-shatur',function(c) c.image='terrain/grass/grass_main_01.png' end},
 {shDefs,'SNOW_ELVEN_TREE4','town-shatur',function(c) c.does_block_move=nil end},{shDefs,'SNOW_ELVEN_TREE4','town-shatur',function(c) c.change_level=1 end},
 {shDefs,'SNOW_ELVEN_TREE4','town-shatur',function(c) c.add_mos={{image='terrain/trees/elm_trunk.png'}} end},
 {shDefs,'SNOWY_PATCH4','town-shatur',function(c) c.does_block_move=true end},{shDefs,'SNOWY_PATCH4','town-shatur',function(c) c.image='terrain/grass/snowy_grass_main_05.png' end},
 {shDefs,'SNOWY_PATCH4','town-shatur',function(c) c.add_displays={setmetatable({image='terrain/grass/snowy_grass_8_01.png'},meta)} end},
 {shDefs,'SNOWY_PATCH4','town-shatur',function(c) c.on_move=function() end end},{shDefs,'SNOWY_PATCH4','town-shatur',function(c) c.notice=true end},
 {shDefs,'ROCKY_GROUND','town-shatur',function(c) c.does_block_move=true end},{shDefs,'ROCKY_GROUND','town-shatur',function(c) c.on_stand=function() end end},
 {shDefs,'ROCKY_GROUND','town-shatur',function(c) c.change_zone='wilderness' end},
 {shDefs,'COBBLESTONE','town-shatur',function(c) c.block_sight=true end},{shDefs,'COBBLESTONE','town-shatur',function(c) c.image='terrain/marble_floor.png' end},
 {shDefs,'COBBLESTONE','town-shatur',function(c) c.add_mos={{image='terrain/road_oldstone/road_vertical_a_01.png'}} end},
 {shDefs,'COBBLESTONE','town-shatur',function(c) c.change_level=1 end},{shDefs,'COBBLESTONE','town-shatur',function(c) c.name='floor' end},
 {pzDefs,'GRASS_SHORT','town-point-zero',function(c) c.does_block_move=true end},
 {pzDefs,'GRASS_SHORT','town-point-zero',function(c) c.add_displays={setmetatable({image='terrain/grass/grass_2_01.png'},meta)} end},
 {pzDefs,'COLD_FOREST9','town-point-zero',function(c) c.dig='GRASS' end},{pzDefs,'COLD_FOREST9','town-point-zero',function(c) c.can_pass={pass_wall=1} end},
 {pzDefs,'COLD_FOREST9','town-point-zero',function(c) c.block_sight=nil end},{pzDefs,'COLD_FOREST9','town-point-zero',function(c) c.image='terrain/tree_dark_snow1.png' end},
 {pzDefs,'OUTERSPACE','town-point-zero',function(c) c.does_block_move=nil end},{pzDefs,'OUTERSPACE','town-point-zero',function(c) c.air_level=-5 end},
 {pzDefs,'OUTERSPACE','town-point-zero',function(c) c.on_stand=function() end end},
 {pzDefs,'FLOATING_ROCKS_91','town-point-zero',function(c) c.does_block_move=true end},
 {pzDefs,'FLOATING_ROCKS_91','town-point-zero',function(c) c.change_zone='wilderness' end},
 {pzDefs,'FLOATING_ROCKS_91','town-point-zero',function(c) c.add_mos={{image='terrain/demon_portal2.png'}} end},
 {pzDefs,'SPACETIME_RIFT','town-point-zero',function(c) c.block_sight=true end},
 {pzDefs,'SPACETIME_RIFT','town-point-zero',function(c) c.image='terrain/lava_floor.png' end},
 {pzDefs,'VOID','town-point-zero',function(c) c.does_block_move=true end},
 {pzDefs,'VOID','town-point-zero',function(c) c.add_displays={setmetatable({image='terrain/rift/rift_V3_1_01.png'},meta)} end},
} do
 local c=deep(m[1][m[2]]);m[4](c)
 eq(T.batch4Kind(c,m[3]),nil,'TW4 altered rule field stays native '..m[2])
end
-- The void family's own zones are unchanged; Point Zero's admission is town-scoped.
eq(T.voidTerrain(methods.clone(pzDefs.OUTERSPACE),'abashed-expanse'),'space','TW4 Abashed space contract unchanged')
eq(T.voidTerrain(methods.clone(pzDefs.VOID),'abashed-expanse'),nil,'TW4 Abashed still has no VOID floor')
eq(T.voidTerrain(methods.clone(pzDefs.VOID),'temporal-rift'),'floor','TW4 Temporal Rift VOID contract unchanged')
eq(T.voidTerrain(methods.clone(pzDefs.OUTERSPACE),'temporal-rift'),nil,'TW4 Temporal Rift still has no outer space')
eq(T.voidTerrain(methods.clone(pzDefs.OUTERSPACE),'town-derth'),nil,'TW4 void identities stay out of other towns')
local foreignRift=deep(pzDefs.SPACETIME_RIFT);foreignRift._checker_void_source={file='/data/zones/unhallowed-morass/grids.lua',id='SPACETIME_RIFT'}
foreignRift.block_sight=true
eq(T.batch4Kind(foreignRift,'town-point-zero'),nil,'TW4 Point Zero accepts only void.lua rifts')
-- Shatur's statue from its real map file (shatur.lua:28).
local sqe,stiles={},{}
do
 local chunk=assert(loadstring(readFile(data..'/maps/towns/shatur.lua'),'@/data/maps/towns/shatur.lua'))
 setfenv(chunk,setmetatable({colors=colors,_t=function(s) return s end,mod={class={Grid={new=function(t) return setmetatable(t,meta) end}}},
  quickEntity=function(c,e) sqe[c]=setmetatable(e,meta) end,defineTile=function(c,g,o,a,trap) stiles[c]={g,trap} end,
  addSpot=function() end,addZone=function() end},{__index=_G}))
 chunk()
end
local sk,sl=T.townStatue(methods.clone(sqe['@']),'town-shatur')
eq(sk,'statue','TW4 exact Shatur moss covered statue')
eq(sl.image..'|'..tostring(sl.z)..'|'..tostring(sl.display_y)..'|'..tostring(sl.display_h),'terrain/statue3.png|nil|nil|nil','TW4 Shatur statue layer is its plain native image')
eq(T.batch4Kind(methods.clone(sqe['@']),'town-shatur'),'statue','TW4 Shatur statue batch kind')
for _,other in ipairs{'town-last-hope','town-derth','town-point-zero','beach'} do
 eq(T.batch4Kind(methods.clone(sqe['@']),other),nil,'TW4 Shatur statue only in Shatur ('..other..')')
end
eq(T.batch4Kind(methods.clone(qe['@']),'town-shatur'),nil,'TW4 Last Hope statue is not a Shatur statue')
for _,mutation in ipairs{
 function(c) c.block_move=function() return true end end,
 function(c) c.add_displays[1]=deep(c.add_displays[1]);c.add_displays[1].z=18 end,
 function(c) c.add_displays[1]=deep(c.add_displays[1]);c.add_displays[1].display_y=-1 end,
 function(c) c.add_displays[1]=deep(c.add_displays[1]);c.add_displays[1].image='terrain/statue1.png' end,
 function(c) c.add_displays[2]={image='terrain/lava.png'} end,function(c) c.define_as='STATUE' end,
 function(c) c.does_block_move=true end,function(c) c.on_stand=function() end end,function(c) c.image='terrain/snowy_grass.png' end,
} do
 local c=deep(sqe['@']);mutation(c)
 eq(T.batch4Kind(c,'town-shatur'),nil,'TW4 altered Shatur statue stays native')
end
-- Shops and the world exits are map-defined: shops are trap-layer entities.
eq(stiles['2'][1]..'|'..stiles['2'][2],'ROCKY_GROUND|SWORD_WEAPON_STORE','TW4 Shatur snow shop is a trap over ROCKY_GROUND')
eq(stiles['5'][1]..'|'..stiles['5'][2],'GRASS|HEAVY_ARMOR_STORE','TW4 Shatur glade shop is a trap over GRASS')
eq(stiles['s'][1]..'|'..stiles['-'][1]..'|'..stiles['_'][1],'SNOW_ELVEN_TREE|SNOWY_GRASS|COBBLESTONE','TW4 Shatur map legend')
local ptiles={}
do
 local chunk=assert(loadstring(readFile(data..'/maps/towns/point-zero.lua'),'@/data/maps/towns/point-zero.lua'))
 setfenv(chunk,setmetatable({colors=colors,_t=function(s) return s end,quickEntity=function() end,
  defineTile=function(c,g,o,a,trap) ptiles[c]={g,trap,a} end,addSpot=function() end,addZone=function() end},{__index=_G}))
 chunk()
end
eq(ptiles['1'][1]..'|'..ptiles['1'][2],'HARDWALL|CLOTH_ARMOR_STORE','TW4 Point Zero shop is a trap over HARDWALL')
eq(ptiles['Z'][1]..'|'..ptiles['Z'][3],'VOID|ZEMEKKYS','TW4 Zemekkys stands on a plain VOID floor (actor layer)')
eq(ptiles['<'][1],'RIFT','TW4 Point Zero world exit is the zone-local RIFT')
-- Stone gates: Point Zero's shop blocks; Shatur is forest only.
eq(T.variant({short_name='town-point-zero'}),'TOWN_POINT_ZERO','TW4 Point Zero stone gate')
eq(T.combined['town-point-zero'],true,'TW4 Point Zero combines forest and stone')
eq(T.variant({short_name='town-shatur'}),nil,'TW4 Shatur has no stone variant (no stone grids)')
eq(T.combined['town-shatur'],nil,'TW4 Shatur is not a combined zone')
env.game={zone={short_name='town-point-zero'}}
for id,kind in pairs{HARDWALL='hardwall',HARDWALL_SOUTH='hardwall',HARDWALL_SOUTH7='hardwall',HARDWALL_NORTH3='hardwall',HARDWALL_PILLAR_6='hardwall',HARDWALL_PILLAR_4='hardwall'} do
 eq(T.classify(methods.clone(pzDefs[id])),kind,'TW4 exact Point Zero stone '..id)
 local c=deep(pzDefs[id]);c._checker_town_source=nil
 eq(T.classify(c),nil,'TW4 old-save Point Zero wall stays native '..id)
 for _,other in ipairs(shTowns) do
  if other~='town-point-zero' then env.game={zone={short_name=other}};eq(T.classify(methods.clone(pzDefs[id])),nil,'TW4 Point Zero wall is not '..other..' '..id) end
 end
 env.game={zone={short_name='town-point-zero'}}
end
for _,id in ipairs{'OUTERSPACE','FLOATING_ROCKS_5','VOID','SPACETIME_RIFT','RIFT','COLD_FOREST3','GRASS_SHORT'} do
 eq(T.classify(methods.clone(pzDefs[id])),nil,'TW4 Point Zero non-stone identity '..id)
end
eq(T.classify(endpoint()),nil,'TW4 beam endpoint is not stone')

-- Scene: Shatur window across the snow/green edge (statue, snow shop trap on
-- ROCKY_GROUND, bridge, lake, exit). No stone: forest install only.
local splan={
 's-R-s',
 'ss-~~',
 't._~t',
 't@..<'}
local ssym={s='SNOW_ELVEN_TREE7',['-']='SNOWY_PATCH2',R='ROCKY_GROUND',t='ELVEN_TREE3',['.']='GRASS',['_']='COBBLESTONE',['~']='DEEP_WATER',['<']='GRASS_UP_WILDERNESS'}
local sm=townMap(5,4,function(x,y)
 local c=splan[y+1]:sub(x+1,x+1)
 if c=='@' then return sqe['@'] end
 return shDefs[ssym[c]]
end)
local sstore={define_as='SWORD_WEAPON_STORE',name='store',image='store/shop_door.png',z=18,block_move=function() return true end}
sm(2,0,TRAP,sstore)
local shopRulesS={};for k,v in pairs(sm(2,0,1)) do shopRulesS[k]=v end
local statueFn=rawget(sm(1,3,1),'block_move')
env.game={zone={short_name='town-shatur'}}
local shh={zone={short_name='town-shatur'},level={map=sm,data={all_remembered=true}}}
mode='refined';T.apply(shh)
eq(shh.checker_mode,'refined','TW4 Shatur refined mode')
eq(sm(0,0,1).replace_display.image,'checker-revised+refined/snow/tree-pine0.png','TW4 Shatur snow tree (even column pine)')
eq(sm(1,1,1).replace_display.image,'checker-revised+refined/snow/tree-elm0.png','TW4 Shatur snow tree (odd column elm)')
eq(sm(1,0,1).replace_display.image,'checker-revised+refined/snow/snow-ground1.png','TW4 Shatur snowy grass')
eq(sm(2,0,1).replace_display.image,'checker-revised+refined/snow/snow-ground0.png','TW4 Shatur snow shop ground')
eq(sm(2,0,TRAP),sstore,'TW4 Shatur shop trap-layer object untouched')
for k,v in pairs(shopRulesS) do if k~='replace_display' and k~='_checker_terrain' then eq(sm(2,0,1)[k],v,'TW4 Shatur shop cell field '..tostring(k)) end end
eq(sm(0,2,1).replace_display.image:match('^checker%-revised%+refined/tree%-')~=nil,true,'TW4 Shatur green elven tree is a board forest tree')
eq(sm(2,2,1).replace_display.image,'checker-revised+refined/town/road0.png','TW4 Shatur bridge is board road (TW7 stone slabs)')
eq(sm(3,2,1).replace_display.image,'checker-revised+refined/deep1-1-0.png','TW4 Shatur lake mask (N)')
eq(sm(4,3,1).replace_display.image,'checker-revised+refined/exit1.png','TW4 Shatur world exit')
local ss=sm(1,3,1).replace_display
eq(ss.image,'checker-revised+refined/grass0.png','TW4 Shatur statue base is board grass')
eq(#ss.add_displays..'|'..ss.add_displays[1].image..'|'..tostring(ss.add_displays[1].z),'1|terrain/statue3.png|nil','TW4 Shatur statue prop exact')
eq(rawget(sm(1,3,1),'block_move'),statueFn,'TW4 Shatur statue lore callback untouched')
eq(T.installRemembered(shh),0,'TW4 Shatur has no stone install')
eq(sm._checker_korpul,nil,'TW4 Shatur creates no stone records')
mode='blockout';T.apply(shh)
eq(sm(0,0,1).replace_display.image,'checker-revised+tree0.png','TW4 blockout snow tree reads as blocking')
eq(sm(1,0,1).replace_display.image,'checker-revised+grass1.png','TW4 blockout snow ground reads as floor')
mode='vanilla';T.apply(shh)
for x=0,4 do for y=0,3 do eq(sm(x,y,1).replace_display,nil,'TW4 native mode restores Shatur '..x..','..y) end end
mode='refined';T.apply(shh)
eq(sm(0,0,1).replace_display.image,'checker-revised+refined/snow/tree-pine0.png','TW4 refined restore Shatur snow tree')
eq(sm(1,3,1).replace_display.add_displays[1].image,'terrain/statue3.png','TW4 refined restore Shatur statue')
local so=townMap(3,1,function(x) if x==0 then return sqe['@'] end local g=deep(shDefs[x==1 and 'SNOWY_PATCH2' or 'SNOW_ELVEN_TREE7']);g._checker_town_source=nil;return g end)
T.apply({zone={short_name='town-shatur'},level={map=so,data={all_remembered=true}}})
for x=0,2 do eq(so(x,0,1).replace_display,nil,'TW4 old-save Shatur cell stays native '..x) end

-- Scene: Point Zero platform window (outer space, rocks, shop block, native
-- beam endpoint, rift, short grass, cold forest, mountain, void floor).
local pplan={
 '**--**',
 '*-#1-*',
 '*-E-=*',
 '*.s^_*'}
local psym={['*']='OUTERSPACE',['-']='FLOATING_ROCKS_5',['#']='HARDWALL',['1']='HARDWALL',['=']='SPACETIME_RIFT',
 ['.']='GRASS_SHORT',s='COLD_FOREST3',['^']='HARDMOUNTAIN_WALL',['_']='VOID'}
local pm=townMap(6,4,function(x,y)
 local c=pplan[y+1]:sub(x+1,x+1)
 if c=='E' then return endpoint() end
 return pzDefs[psym[c]]
end)
local pstore={define_as='CLOTH_ARMOR_STORE',name='store',image='store/shop_door.png',z=18,block_move=function() return true end}
pm(3,1,TRAP,pstore)
local epFn,epExit=rawget(pm(2,2,1),'block_move'),pm(2,2,1).exit
env.game={zone={short_name='town-point-zero'}}
local pzh={zone={short_name='town-point-zero'},level={map=pm,data={all_remembered=true}}}
mode='refined';T.apply(pzh)
eq(pzh.checker_mode,'refined','TW4 Point Zero refined mode')
eq(pm(0,0,1).replace_display.image,'checker-revised+refined/void/space0.png','TW4 Point Zero outer space')
eq(pm(2,0,1).replace_display.image,'checker-revised+refined/void/rocks-6-0.png','TW4 rocks rim only toward space (E rock, S building)')
eq(pm(1,1,1).replace_display.image,'checker-revised+refined/void/rocks-6-0.png','TW4 rocks joined to the building (E) and rock (S)')
eq(pm(1,2,1).replace_display.image,'checker-revised+refined/void/rocks-7-1.png','TW4 rocks joined to the native endpoint and grass')
eq(pm(3,2,1).replace_display.image,'checker-revised+refined/void/rocks-15-1.png','TW4 rocks inside the platform have no rim')
eq(pm(4,1,1).replace_display.image,'checker-revised+refined/void/rocks-12-1.png','TW4 rocks rim toward space N and E')
eq(pm(4,2,1).replace_display.image,'checker-revised+refined/void/rift-0-0.png','TW4 Point Zero rift (rift-only mask)')
eq(pm(1,3,1).replace_display.image,'checker-revised+refined/grass0.png','TW4 Point Zero short grass')
eq(pm(2,3,1).replace_display.image,'checker-revised+refined/snow/tree-pine1.png','TW4 Point Zero cold forest is a snow pine')
eq(pm(3,3,1).replace_display.image,'checker-revised+refined/daikara/mountain-wall-00.png','TW4 Point Zero mountain')
eq(pm(4,3,1).replace_display.image,'checker-revised+refined/void/floor1.png','TW4 Point Zero void floor')
eq(pm(2,2,1).replace_display,nil,'TW4 beam endpoint keeps its native display')
eq(rawget(pm(2,2,1),'block_move'),epFn,'TW4 beam endpoint callback untouched')
eq(pm(2,2,1).exit,epExit,'TW4 beam endpoint exit untouched')
eq(pm(2,1,1).replace_display,nil,'TW4 Point Zero wall is stone, not forest')
eq(T.render(pm,2,1,pm(2,1,1),'refined').image,T.assetPath('hardwall',nil,2,1,2,1),'TW4 hidden remembered wall mask (E)')
eq(T.render(pm,3,1,pm(3,1,1),'refined').image,T.assetPath('hardwall',nil,8,0,3,1),'TW4 shop wall mask (W)')
eq(pm(3,1,TRAP),pstore,'TW4 Point Zero shop trap untouched')
eq(T.classify(pm(3,1,1)),'hardwall','TW4 shop cell grid is plain HARDWALL')
-- With the Conclave brick export present, Point Zero's hard walls draw it
-- (same mask); other towns' hard walls keep Kor'Pul art.
local savedConclave=T.conclaveAssets
T.conclaveAssets={ready=true,files=setmetatable({},{__index=function(_,k) return type(k)=='string' and k:match('^checker%-revised%+refined/conclave/wall%-') and true or nil end})}
T.installRemembered(pzh)
eq(T.render(pm,2,1,pm(2,1,1),'refined').image,'checker-revised+refined/conclave/wall-2-1.png','TW4 Point Zero hard wall uses the dark Conclave brick (E)')
eq(T.render(pm,3,1,pm(3,1,1),'refined').image,'checker-revised+refined/conclave/wall-8-0.png','TW4 Point Zero shop wall uses the Conclave brick (W)')
eq(pm(3,1,TRAP),pstore,'TW4 shop trap untouched by the wall art choice')
local cdm=townMap(2,1,function() return derthDefs.HARDWALL end)
env.game={zone={short_name='town-derth'}}
T.installRemembered({zone={short_name='town-derth'},level={map=cdm,data={all_remembered=true}}})
eq(T.render(cdm,0,0,cdm(0,0,1),'refined').image,T.assetPath('hardwall',nil,2,0,0,0),'TW4 Derth hard wall keeps Kor\'Pul art')
env.game={zone={short_name='town-point-zero'}}
T.conclaveAssets=savedConclave
T.installRemembered(pzh)
mode='blockout';T.apply(pzh)
eq(pm(0,0,1).replace_display.image,'checker-revised+tree0.png','TW4 blockout space reads as blocking')
eq(pm(2,0,1).replace_display.image,'checker-revised+grass0.png','TW4 blockout rocks read as floor')
eq(pm(4,2,1).replace_display.image,'checker-revised+tree0.png','TW4 blockout rift reads as blocking')
eq(pm(2,3,1).replace_display.image,'checker-revised+tree1.png','TW4 blockout cold forest reads as blocking')
mode='vanilla';T.apply(pzh)
for x=0,5 do for y=0,3 do eq(pm(x,y,1).replace_display,nil,'TW4 native mode restores Point Zero '..x..','..y) end end
eq(T.render(pm,2,1,pm(2,1,1),'vanilla').image,pzDefs.HARDWALL.image,'TW4 native mode restores the wall snapshot')
mode='refined';T.apply(pzh)
eq(pm(1,2,1).replace_display.image,'checker-revised+refined/void/rocks-7-1.png','TW4 refined restore rocks')
eq(pm(2,2,1).replace_display,nil,'TW4 refined restore leaves the endpoint native')
local po=townMap(4,1,function(x) local g=deep(pzDefs[({'OUTERSPACE','FLOATING_ROCKS_5','COLD_FOREST3','HARDWALL'})[x+1]]);g._checker_town_source=nil;return g end)
T.apply({zone={short_name='town-point-zero'},level={map=po,data={all_remembered=true}}})
for x=0,3 do eq(po(x,0,1).replace_display,nil,'TW4 old-save Point Zero cell stays native '..x) end
eq(next(po._checker_korpul or {}),nil,'TW4 old-save Point Zero wall gets no stone record')

-- Other towns and zones: TW4 identities never leak.
local lz={zone={short_name='last-hope-graveyard'},level={map=townMap(3,1,function(x) return ({shDefs.SNOW_ELVEN_TREE7,pzDefs.COLD_FOREST3,pzDefs.OUTERSPACE})[x+1] end),data={}}}
env.game={zone=lz.zone}
T.apply(lz)
for x=0,2 do eq(lz.level.map(x,0,1).replace_display,nil,'TW4 identity stays native elsewhere '..x) end
local dz={zone={short_name='town-derth'},level={map=townMap(3,1,function(x) return ({shDefs.GRASS,pzDefs.GRASS_SHORT,shDefs.DEEP_WATER})[x+1] end),data={all_remembered=true}}}
env.game={zone=dz.zone}
T.apply(dz)
for x=0,2 do eq(dz.level.map(x,0,1).replace_display,nil,'TW4 Shatur/Point Zero list grids stay native in Derth '..x) end
end)()
-- TW5: Gates of Morning. Town list loaded like Grid:loadList (nested basic,
-- forest, mountain, water and sand imports keep their general stamps and get
-- the Gates list stamp). New exact identity: the zone-local Sunwall mountain
-- (GOLDEN_MOUNTAIN and GOLDEN_MOUNTAIN_WALL1-6) with only its gold_mountain
-- border layers; the town's sand joins Zigur's beach-sand admission; roads,
-- grass, trees, water and the exit use the existing contracts. Palms, the
-- FENS entrance and the farportals stay native. Own function (local limit).
;(function()
local gFile='/data/zones/town-gates-of-morning/grids.lua'
local gDefs=loadDefs(gFile)
eq(gDefs.GOLDEN_MOUNTAIN._checker_town_source.file,gFile,'TW5 Gates list stamps its own Sunwall mountain')
eq(gDefs.GOLDEN_MOUNTAIN_WALL4._checker_town_source.id,'GOLDEN_MOUNTAIN_WALL4','TW5 Gates stamp id is the variant id')
eq(gDefs.HARDWALL._checker_grid_source.file,'/data/general/grids/basic.lua','TW5 Gates wall keeps its basic.lua stamp')
eq(gDefs.HARDWALL._checker_town_source.file,gFile,'TW5 Gates list stamps nested basic.lua walls')
eq(gDefs.SAND._checker_surface_sand_source.file,'/data/general/grids/sand.lua','TW5 Gates sand keeps its sand.lua stamp')
eq(gDefs.SAND._checker_town_source.file,gFile,'TW5 Gates list stamps nested sand.lua')
eq(gDefs.DEEP_OCEAN_WATER._checker_water_source.file,'/data/general/grids/water.lua','TW5 Gates ocean keeps its water.lua stamp')
eq(gDefs.FLOOR_ROAD_STONE._checker_town_source.file,gFile,'TW5 Gates road is its own list entry')
local function layered(g,displays)
 for i,d in ipairs(displays) do displays[i]=setmetatable(d,meta) end
 g.add_displays=displays;return g
end
-- Runtime layer shapes from the fixture probe (gold_mountain borders).
local function goldRuntime(id,extra)
 local g=deep(gDefs[id])
 local ds={{image='invis.png',add_mos={{image='terrain/golden_mountain2.png'},{image='terrain/golden_mountain9i.png'}}},
  {image=g.image,z=3,add_mos={{image='terrain/golden_mountain6.png'}}},{image='terrain/golden_mountain8.png',z=16}}
 for _,d in ipairs(extra or {}) do ds[#ds+1]=d end
 return layered(g,ds)
end
local function roadRuntime()
 return layered(deep(gDefs.FLOOR_ROAD_STONE),{{image='invis.png',add_mos={{image='terrain/road_oldstone/road_t_section_b_01.png'}}}})
end
local function sandRuntime()
 return layered(deep(gDefs.SAND),{{image='invis.png',add_mos={{image='terrain/sand/sand_8_01.png'},{image='terrain/sand/sand_inner_1_01.png'}}}})
end
local gTowns={'town-derth','town-lumberjack-village','town-last-hope','town-elvala','town-zigur','town-angolwen',
 'town-iron-council','town-shatur','town-point-zero','town-gates-of-morning'}
local gForest={GRASS='grass',GRASS_PATCH7='grass',TREE12='tree',DEEP_WATER='deep',DEEP_OCEAN_WATER='deep',SAND='sand',
 FLOOR_ROAD_STONE='road',GRASS_UP_WILDERNESS='exit',GOLDEN_MOUNTAIN='gold-mountain'}
for i=1,6 do gForest['GOLDEN_MOUNTAIN_WALL'..i]='gold-mountain' end
for id,kind in pairs(gForest) do
 eq(T.batch4Kind(methods.clone(gDefs[id]),'town-gates-of-morning'),kind,'TW5 exact Gates '..id)
 local c=deep(gDefs[id]);c._checker_town_source=nil
 eq(T.batch4Kind(c,'town-gates-of-morning'),nil,'TW5 unstamped (old-save) grid stays native '..id)
 for _,other in ipairs(gTowns) do
  if other~='town-gates-of-morning' then eq(T.batch4Kind(methods.clone(gDefs[id]),other),nil,'TW5 Gates list is not '..other..' '..id) end
 end
 for _,fam in ipairs{'beach','meadow','caldera'} do
  if not ((fam=='beach' and (kind=='sand' or kind=='deep' or kind=='grass' or kind=='tree')) or
   (fam=='meadow' and (kind=='grass' or kind=='deep' or kind=='exit'))) then
   eq(T.batch4Kind(methods.clone(gDefs[id]),fam),nil,'TW5 town-only kind is zone scoped '..fam..' '..id)
  end
 end
 env.game={zone={short_name='town-gates-of-morning'}}
 eq(T.classify(methods.clone(gDefs[id])),nil,'TW5 forest identity is not stone '..id)
end
eq(T.batch4Kind(goldRuntime('GOLDEN_MOUNTAIN'),'town-gates-of-morning'),'gold-mountain','TW5 Sunwall mountain with native border layers')
eq(T.batch4Kind(goldRuntime('GOLDEN_MOUNTAIN_WALL5',{{image='terrain/golden_mountain7.png',z=17},{image='terrain/golden_mountain9.png',z=18}}),'town-gates-of-morning'),
 'gold-mountain','TW5 Sunwall mountain variant with all three overhangs')
eq(T.batch4Kind(roadRuntime(),'town-gates-of-morning'),'road','TW5 Gates road with native oldstone road layers')
eq(T.batch4Kind(sandRuntime(),'town-gates-of-morning'),'sand','TW5 Gates sand with native sand borders')
-- Exactness: foreign layers, altered rules, unused and runtime grids.
local gf=goldRuntime('GOLDEN_MOUNTAIN');gf.add_displays[1].add_mos[1].image='terrain/mountain2.png'
eq(T.batch4Kind(gf,'town-gates-of-morning'),nil,'TW5 mountain with a grey mountain border stays native')
gf=goldRuntime('GOLDEN_MOUNTAIN');gf.add_displays[3].image='terrain/golden_cave_entrance02.png'
eq(T.batch4Kind(gf,'town-gates-of-morning'),nil,'TW5 mountain with a foreign overhang stays native')
gf=goldRuntime('GOLDEN_MOUNTAIN');gf.add_displays[3].z=8
eq(T.batch4Kind(gf,'town-gates-of-morning'),nil,'TW5 mountain overhang at another depth stays native')
gf=goldRuntime('GOLDEN_MOUNTAIN_WALL2');gf.add_displays[2].image='terrain/golden_mountain5_1.png'
eq(T.batch4Kind(gf,'town-gates-of-morning'),nil,'TW5 copy_base layer must be the cell image')
local rf=roadRuntime();rf.add_displays[1].add_mos[1].image='terrain/marble_water/marble_floor_2_to_water_outer_4.png'
eq(T.batch4Kind(rf,'town-gates-of-morning'),'road','TW5 Gates road may carry the marble edge the shared road contract allows')
rf=roadRuntime();rf.add_displays[1].add_mos[1].image='terrain/lava/lava_floor1.png'
eq(T.batch4Kind(rf,'town-gates-of-morning'),nil,'TW5 Gates road with a foreign layer stays native')
for _,id in ipairs{'PALMTREE','PALMTREE5','PALMTREE20','FENS','WEST_PORTAL','CWEST_PORTAL','HARDWALL','FLOOR','MOUNTAIN_WALL',
 'ROCKY_GROUND','SAND_UP_WILDERNESS','SANDWALL','HARDTREE3'} do
 if gDefs[id] then eq(T.batch4Kind(methods.clone(gDefs[id]),'town-gates-of-morning'),nil,'TW5 not claimed as a Gates forest kind '..id) end
end
env.game={zone={short_name='town-gates-of-morning'}}
for _,id in ipairs{'FENS','WEST_PORTAL','CWEST_PORTAL','PALMTREE5','GOLDEN_MOUNTAIN','GOLDEN_MOUNTAIN_WALL3','FLOOR_ROAD_STONE','SAND'} do
 -- (S14: the farportal is an S14 cell with its own stamp, tests/terrain_s14.lua.)
 local c=methods.clone(gDefs[id]);c._checker_s14_source=nil
 eq(T.classify(c),nil,'TW5 not a Gates stone kind '..id)
end
for _,m in ipairs{
 {'GOLDEN_MOUNTAIN',function(c) c.dig='FLOOR' end},{'GOLDEN_MOUNTAIN',function(c) c.can_pass={pass_wall=1} end},
 {'GOLDEN_MOUNTAIN',function(c) c.block_sense=nil end},{'GOLDEN_MOUNTAIN',function(c) c.block_esp=nil end},
 {'GOLDEN_MOUNTAIN',function(c) c.block_sight=nil end},{'GOLDEN_MOUNTAIN',function(c) c.does_block_move=nil end},
 {'GOLDEN_MOUNTAIN',function(c) c.air_level=-5 end},{'GOLDEN_MOUNTAIN',function(c) c.on_stand=function() end end},
 {'GOLDEN_MOUNTAIN',function(c) c.block_move=function() return true end end},{'GOLDEN_MOUNTAIN',function(c) c.change_zone='slazish-fen' end},
 {'GOLDEN_MOUNTAIN',function(c) c.name='rocky mountain' end},{'GOLDEN_MOUNTAIN',function(c) c.subtype='rock' end},
 {'GOLDEN_MOUNTAIN',function(c) c.type='wall' end},{'GOLDEN_MOUNTAIN',function(c) c.add_mos={{image='terrain/golden_mountain2.png'}} end},
 {'GOLDEN_MOUNTAIN',function(c) c.shader='water' end},{'GOLDEN_MOUNTAIN',function(c) c.notice=true end},
 {'GOLDEN_MOUNTAIN_WALL3',function(c) c.image='terrain/golden_mountain5_1.png' end},
 {'GOLDEN_MOUNTAIN_WALL3',function(c) c.grow='GOLDEN_MOUNTAIN' end},
 {'FLOOR_ROAD_STONE',function(c) c.does_block_move=true end},{'FLOOR_ROAD_STONE',function(c) c.change_zone='slazish-fen' end},
 {'FLOOR_ROAD_STONE',function(c) c.image='terrain/golden_cave_entrance02.png' end},
 {'SAND',function(c) c.does_block_move=true end},{'SAND',function(c) c.on_stand=function() end end},
 {'DEEP_OCEAN_WATER',function(c) c.air_level=-1 end},
} do
 local c=deep(gDefs[m[1]]);m[2](c)
 eq(T.batch4Kind(c,'town-gates-of-morning'),nil,'TW5 altered rule field stays native '..m[1])
end
-- Sand admission stays scoped: other towns' and zones' sand is untouched.
eq(T.batch4Kind(methods.clone(gDefs.SAND),'town-derth'),nil,'TW5 Gates sand is not Derth sand')
-- Map legend from the real map file: shops are trap-layer entities over HARDWALL.
local gtiles={}
do
 local chunk=assert(loadstring(readFile(data..'/maps/towns/gates-of-morning.lua'),'@/data/maps/towns/gates-of-morning.lua'))
 setfenv(chunk,setmetatable({colors=colors,_t=function(s) return s end,mod={class={NPC={new=function(t) return t end}}},
  quickEntity=function() end,defineTile=function(c,g,o,a,trap) gtiles[c]={g,trap,a} end,
  addSpot=function() end,addZone=function() end},{__index=_G}))
 gtiles.map=chunk()
end
for _,c in ipairs{'1','2','3','4','5','A','6','7','8','9','0','Z'} do
 eq(gtiles[c][1],'HARDWALL','TW5 Gates shop '..c..' stands on HARDWALL')
 eq(type(gtiles[c][2]),'string','TW5 Gates shop '..c..' is a trap-layer entity')
end
eq(gtiles.m[1]..'|'..gtiles.p[1]..'|'..gtiles['*'][1]..'|'..gtiles[':'][1]..'|'..gtiles._[1],
 'GOLDEN_MOUNTAIN|PALMTREE|SAND|DEEP_OCEAN_WATER|FLOOR_ROAD_STONE','TW5 Gates map legend')
local mc=0;for _ in gtiles.map:gmatch('m') do mc=mc+1 end
eq(mc,784,'TW5 Gates map has 784 Sunwall mountain cells')
-- Stone gate: plaza floor, building blocks, shop walls.
eq(T.variant({short_name='town-gates-of-morning'}),'TOWN_GATES_OF_MORNING','TW5 Gates stone gate')
eq(T.combined['town-gates-of-morning'],true,'TW5 Gates combines forest and stone')
env.game={zone={short_name='town-gates-of-morning'}}
for id,kind in pairs{FLOOR='floor',HARDWALL='hardwall',HARDWALL_SOUTH='hardwall',HARDWALL_SOUTH3='hardwall',HARDWALL_NORTH2='hardwall',
 HARDWALL_SMALL_PILLAR='hardwall',HARDWALL_PILLAR_4='hardwall'} do
 if gDefs[id] then
  eq(T.classify(methods.clone(gDefs[id])),kind,'TW5 exact Gates stone '..id)
  local c=deep(gDefs[id]);c._checker_town_source=nil
  eq(T.classify(c),nil,'TW5 old-save Gates stone stays native '..id)
  for _,other in ipairs(gTowns) do
   if other~='town-gates-of-morning' then env.game={zone={short_name=other}};eq(T.classify(methods.clone(gDefs[id])),nil,'TW5 Gates stone is not '..other..' '..id) end
  end
  env.game={zone={short_name='town-gates-of-morning'}}
 end
end

-- Scene: the mountain ring round a plaza corner (floor, building with a shop
-- trap, road), the beach (sand, palm, ocean) and the world exit.
local gplan={
 'mmmmmm',
 'm.#2_m',
 'm..__m',
 '<*sp:m',
 'mMmmmm'}
local gsym={m='GOLDEN_MOUNTAIN_WALL3',M='GOLDEN_MOUNTAIN',['.']='FLOOR',['#']='HARDWALL',['2']='HARDWALL',['_']='FLOOR_ROAD_STONE',
 ['<']='GRASS_UP_WILDERNESS',['*']='SAND',s='SAND',p='PALMTREE5',[':']='DEEP_OCEAN_WATER'}
local gm=townMap(6,5,function(x,y) return gDefs[gsym[gplan[y+1]:sub(x+1,x+1)]] end)
local gstore={define_as='SWORD_WEAPON_STORE',name='store',image='store/shop_door.png',z=18,block_move=function() return true end}
gm(3,1,TRAP,gstore)
local shopRulesG={};for k,v in pairs(gm(3,1,1)) do shopRulesG[k]=v end
local mountainRules={};for k,v in pairs(gm(0,0,1)) do mountainRules[k]=v end
env.game={zone={short_name='town-gates-of-morning'}}
local gh={zone={short_name='town-gates-of-morning'},level={map=gm,data={all_remembered=true}}}
mode='refined';T.apply(gh)
eq(gh.checker_mode,'refined','TW5 Gates refined mode')
local function gi(x,y) return gm(x,y,1).replace_display and gm(x,y,1).replace_display.image end
eq(gi(0,0),'checker-revised+refined/gold-mountain/wall-6-0.png','TW5 mountain corner (E,S)')
eq(gi(1,0),'checker-revised+refined/gold-mountain/wall-10-1.png','TW5 mountain over the plaza (E,W)')
eq(gi(0,1),'checker-revised+refined/gold-mountain/wall-5-1.png','TW5 mountain beside the plaza (N,S)')
eq(gi(0,2),'checker-revised+refined/gold-mountain/wall-1-0.png','TW5 mountain above the world exit (N)')
eq(gi(5,3),'checker-revised+refined/gold-mountain/wall-5-0.png','TW5 mountain beside the ocean (N,S)')
eq(gi(1,4),'checker-revised+refined/gold-mountain/wall-10-1.png','TW5 base GOLDEN_MOUNTAIN joins its variants (E,W)')
eq(gi(5,4),'checker-revised+refined/gold-mountain/wall-9-1.png','TW5 mountain corner (N,W)')
for k,v in pairs(mountainRules) do if k~='replace_display' and k~='_checker_terrain' then eq(gm(0,0,1)[k],v,'TW5 mountain rule field '..tostring(k)) end end
eq(gi(4,1),'checker-revised+refined/town/road1.png','TW5 Gates road is board road (TW7 stone slabs)')
eq(gi(0,3),'checker-revised+refined/exit1.png','TW5 Gates world exit')
eq(gi(1,3),'checker-revised+refined/beach/sand0.png','TW5 Gates sand is beach sand')
eq(gi(2,3),'checker-revised+refined/beach/sand1.png','TW5 Gates sand parity')
eq(gm(3,3,1).replace_display,nil,'TW5 Gates palm without its native makeTrees parts stays native (TW7 needs them)')
eq(gi(4,3),'checker-revised+refined/deep0-1-0.png','TW5 Gates ocean (no water neighbour)')
eq(gm(1,1,1).replace_display,nil,'TW5 plaza floor is stone, not forest')
eq(gm(2,1,1).replace_display,nil,'TW5 building wall is stone, not forest')
eq(T.render(gm,1,1,gm(1,1,1),'refined').image,T.assetPath('floor',nil,0,0,1,1),'TW5 hidden remembered plaza floor')
eq(T.render(gm,2,1,gm(2,1,1),'refined').image,T.assetPath('hardwall',nil,2,1,2,1),'TW5 hidden building wall mask (E)')
eq(T.render(gm,3,1,gm(3,1,1),'refined').image,T.assetPath('hardwall',nil,8,0,3,1),'TW5 shop wall mask (W)')
eq(gm(3,1,TRAP),gstore,'TW5 Gates shop trap-layer object untouched')
for k,v in pairs(shopRulesG) do if k~='replace_display' and k~='_checker_terrain' then eq(gm(3,1,1)[k],v,'TW5 Gates shop cell field '..tostring(k)) end end
eq(T.classify(gm(3,1,1)),'hardwall','TW5 shop cell grid is plain HARDWALL')
-- The stone wall mask counts stone walls only; the mountain is forest art.
eq(T.mask(gm,1,1),2,'TW5 stone mask ignores the neighbouring mountain')
mode='blockout';T.apply(gh)
eq(gi(0,0),'checker-revised+tree0.png','TW5 blockout mountain reads as blocking')
eq(gi(1,3),'checker-revised+grass0.png','TW5 blockout sand reads as floor')
mode='vanilla';T.apply(gh)
for x=0,5 do for y=0,4 do eq(gm(x,y,1).replace_display,nil,'TW5 native mode restores Gates '..x..','..y) end end
eq(T.render(gm,2,1,gm(2,1,1),'vanilla').image,gDefs.HARDWALL.image,'TW5 native mode restores the wall snapshot')
mode='refined';T.apply(gh)
eq(gi(0,0),'checker-revised+refined/gold-mountain/wall-6-0.png','TW5 refined restore mountain')
eq(gi(1,3),'checker-revised+refined/beach/sand0.png','TW5 refined restore sand')
eq(gm(3,3,1).replace_display,nil,'TW5 refined restore leaves the partless palm native')
-- Old save: a Gates level generated before the list stamp stays native.
local go=townMap(4,1,function(x) local g=deep(gDefs[({'GOLDEN_MOUNTAIN','SAND','FLOOR_ROAD_STONE','HARDWALL'})[x+1]]);g._checker_town_source=nil;return g end)
T.apply({zone={short_name='town-gates-of-morning'},level={map=go,data={all_remembered=true}}})
for x=0,3 do eq(go(x,0,1).replace_display,nil,'TW5 old-save Gates cell stays native '..x) end
eq(next(go._checker_korpul or {}),nil,'TW5 old-save Gates wall gets no stone record')
-- Other towns and zones: TW5 identities never leak; earlier town art unchanged.
local lz={zone={short_name='last-hope-graveyard'},level={map=townMap(3,1,function(x) return ({gDefs.GOLDEN_MOUNTAIN,gDefs.SAND,gDefs.FLOOR_ROAD_STONE})[x+1] end),data={}}}
env.game={zone=lz.zone}
T.apply(lz)
for x=0,2 do eq(lz.level.map(x,0,1).replace_display,nil,'TW5 identity stays native elsewhere '..x) end
local dz={zone={short_name='town-derth'},level={map=townMap(3,1,function(x) return ({gDefs.GOLDEN_MOUNTAIN,gDefs.SAND,gDefs.GRASS})[x+1] end),data={all_remembered=true}}}
env.game={zone=dz.zone}
T.apply(dz)
for x=0,2 do eq(dz.level.map(x,0,1).replace_display,nil,'TW5 Gates list grids stay native in Derth '..x) end
local lhDefs=loadDefs('/data/zones/town-last-hope/grids.lua')
eq(T.batch4Kind(methods.clone(lhDefs.HARDMOUNTAIN_WALL3),'town-last-hope'),'mountain','TW5 Last Hope hard mountain unchanged')
eq(T.batch4Kind(methods.clone(lhDefs.FLOOR_ROAD_STONE),'town-last-hope'),'road','TW5 Last Hope plaza road unchanged')
end)()
-- TW6: Irkkk. Town list loaded like Grid:loadList (nested basic, jungle,
-- jungle_hut and water imports; jungle.lua and water.lua keep their general
-- stamps, everything gets the Irkkk list stamp). Jungle grass, trees and the
-- world exit reuse jungleKind's contract with Caldera art; deep water uses the
-- existing contract; the bamboo huts are a new exact family (walls with only
-- the native layers their definition line adds, floor, cooking pit prop,
-- horizontal/vertical doors open and closed). Shops are actors on hut floor.
;(function()
local iFile='/data/zones/town-irkkk/grids.lua'
local iDefs=loadDefs(iFile)
eq(iDefs.JUNGLE_GRASS._checker_jungle_source.file,'/data/general/grids/jungle.lua','TW6 jungle grass keeps its jungle.lua stamp')
eq(iDefs.JUNGLE_GRASS._checker_town_source.file,iFile,'TW6 Irkkk list stamps nested jungle.lua')
eq(iDefs.DEEP_WATER._checker_water_source.file,'/data/general/grids/water.lua','TW6 lake keeps its water.lua stamp')
eq(iDefs.BAMBOO_HUT_WALL._checker_town_source.file,iFile,'TW6 Irkkk list stamps nested jungle_hut.lua')
eq(iDefs.BHW_H_FULL5._checker_town_source.id,'BHW_H_FULL5','TW6 stamp id is the variant id')
eq(iDefs.BAMBOO_HUT_COOKING3._checker_town_source.file,iFile,'TW6 cooking pit is its own list entry')
local function layered(g,displays)
 for i,d in ipairs(displays) do displays[i]=setmetatable(d,meta) end
 g.add_displays=displays;return g
end
-- Runtime jungle grass with its native jungle_grass borders (fixture probe).
local function grassRuntime(id)
 return layered(deep(iDefs[id]),{{image='invis.png',add_mos={{image='terrain/jungle/jungle_grass_8_01.png'},{image='terrain/jungle/jungle_grass_inner_1_01.png'}}}})
end
local iTowns={'town-derth','town-lumberjack-village','town-last-hope','town-elvala','town-zigur','town-angolwen',
 'town-iron-council','town-shatur','town-point-zero','town-gates-of-morning','town-irkkk'}
local iForest={JUNGLE_GRASS='jungle-grass',JUNGLE_GRASS_PATCH3='jungle-grass',JUNGLE_GRASS_PATCH19='jungle-grass',
 JUNGLE_TREE='jungle-tree',JUNGLE_TREE7='jungle-tree',JUNGLE_GRASS_UP_WILDERNESS='jungle-exit',DEEP_WATER='deep',
 BAMBOO_HUT_FLOOR='hut-floor',BAMBOO_HUT_COOKING3='hut-cooking',BAMBOO_HUT_WALL='hut-wall',
 BHW_V_FULL1='hut-wall',BHW_H_FULL='hut-wall',BHW_N_CROSS1='hut-wall',BHW_S_CROSS1='hut-wall',BHW_E_CROSS1='hut-wall',
 BHW_W_CROSS1='hut-wall',BHW_CROSS1='hut-wall',BHW_NE1='hut-wall',BHW_NW1='hut-wall',BHW_SE1='hut-wall',BHW_SW1='hut-wall',
 BAMBOO_HUT_DOOR_HORIZ='hut-door-h',BAMBOO_HUT_DOOR_VERT='hut-door-v',
 BAMBOO_HUT_DOOR_HORIZ_OPEN='hut-door-h-open',BAMBOO_HUT_DOOR_OPEN_VERT='hut-door-v-open'}
for i=1,8 do iForest['BHW_H_FULL'..i]='hut-wall' end
for id,kind in pairs(iForest) do
 eq(T.batch4Kind(methods.clone(iDefs[id]),'town-irkkk'),kind,'TW6 exact Irkkk '..id)
 local c=deep(iDefs[id]);c._checker_town_source=nil
 eq(T.batch4Kind(c,'town-irkkk'),nil,'TW6 unstamped (old-save) grid stays native '..id)
 for _,other in ipairs(iTowns) do
  if other~='town-irkkk' then eq(T.batch4Kind(methods.clone(iDefs[id]),other),nil,'TW6 Irkkk list is not '..other..' '..id) end
 end
 for _,fam in ipairs{'beach','meadow','caldera','gorbat-pride'} do
  local got=T.batch4Kind(methods.clone(iDefs[id]),fam)
  -- Caldera's own jungle contract (jungle.lua stamp) is untouched by TW6.
  if fam=='caldera' and id:match('^JUNGLE') then eq(got=='floor' or got=='tree' or got=='exit-world',true,'TW6 Caldera jungle unchanged '..id)
  elseif not (fam=='beach' or fam=='meadow') or kind~='deep' then eq(got,nil,'TW6 town-only kind is zone scoped '..fam..' '..id) end
 end
 env.game={zone={short_name='town-irkkk'}}
 eq(T.classify(methods.clone(iDefs[id])),nil,'TW6 forest identity is not stone '..id)
end
eq(T.batch4Kind(grassRuntime('JUNGLE_GRASS'),'town-irkkk'),'jungle-grass','TW6 jungle grass with native border layers')
local gp=layered(deep(iDefs.JUNGLE_GRASS_PATCH19),{{image='terrain/jungle/jungle_dirt_var_3_64_01.png',z=3}})
eq(T.batch4Kind(gp,'town-irkkk'),'jungle-grass','TW6 jungle grass patch with its native dirt layer')
gp=layered(deep(iDefs.JUNGLE_GRASS),{{image='terrain/grass/grass_main_01.png'}})
eq(T.batch4Kind(gp,'town-irkkk'),nil,'TW6 jungle grass with a foreign layer stays native')
-- Exactness of the hut layers: foreign image, depth, offset, decoration, extra layer.
local function hutMut(id,f) local c=deep(iDefs[id]);f(c);return T.batch4Kind(c,'town-irkkk') end
eq(hutMut('BHW_V_FULL1',function(c) c.add_displays[1].image='terrain/bamboo/hut_wall_bottom_hor_01.png' end),nil,'TW6 wall with a foreign layer image stays native')
eq(hutMut('BHW_V_FULL1',function(c) c.add_displays[1].z=18 end),nil,'TW6 wall layer at another depth stays native')
eq(hutMut('BHW_H_FULL',function(c) c.add_displays[2].display_y=nil end),nil,'TW6 wall top without its overhang offset stays native')
eq(hutMut('BHW_H_FULL3',function(c) c.add_displays[1].add_mos[1].image='terrain/bamboo/wall_decor_sticks_01.png' end),nil,'TW6 wall with another variant decoration stays native')
eq(hutMut('BHW_H_FULL3',function(c) c.add_displays[1].add_mos[1].display_x=0.5 end),nil,'TW6 wall decoration moved stays native')
eq(hutMut('BHW_NE1',function(c) c.add_displays[3]=setmetatable({image='terrain/bamboo/hut_corner_4_1_2_top_01.png',z=18},meta) end),nil,'TW6 wall with an extra layer stays native')
eq(hutMut('BHW_CROSS1',function(c) c.add_displays[2].add_mos[2]=nil end),nil,'TW6 cross wall missing a nested layer stays native')
eq(hutMut('BAMBOO_HUT_DOOR_HORIZ',function(c) c.add_displays[1].image='terrain/bamboo/hut_wall_door_open_hor_01.png' end),nil,'TW6 closed door with open-door art stays native')
eq(hutMut('BAMBOO_HUT_DOOR_OPEN_VERT',function(c) c.add_displays[2].add_mos={} end),nil,'TW6 open door missing its nested layers stays native')
for _,m in ipairs{
 {'BHW_V_FULL1',function(c) c.dig=nil end},{'BHW_V_FULL1',function(c) c.dig='FLOOR' end},{'BHW_V_FULL1',function(c) c.can_pass=nil end},
 {'BHW_V_FULL1',function(c) c.can_pass={pass_wall=1,pass_tree=1} end},{'BHW_V_FULL1',function(c) c.block_sight=nil end},
 {'BHW_V_FULL1',function(c) c.does_block_move=nil end},{'BHW_V_FULL1',function(c) c.block_sense=true end},
 {'BHW_V_FULL1',function(c) c.block_esp=true end},{'BHW_V_FULL1',function(c) c.air_level=-20 end},
 {'BHW_V_FULL1',function(c) c.on_stand=function() end end},{'BHW_V_FULL1',function(c) c.block_move=function() return true end end},
 {'BHW_V_FULL1',function(c) c.on_move=function() end end},{'BHW_V_FULL1',function(c) c.change_zone='wilderness' end},
 {'BHW_V_FULL1',function(c) c.name='stone wall' end},{'BHW_V_FULL1',function(c) c.subtype='floor' end},
 {'BHW_V_FULL1',function(c) c.image='terrain/granite_wall1.png' end},{'BHW_V_FULL1',function(c) c.add_mos={{image='terrain/bamboo/wall_decor_spears_01.png'}} end},
 {'BHW_V_FULL1',function(c) c.shader='water' end},{'BHW_V_FULL1',function(c) c.is_door=true end},{'BHW_V_FULL1',function(c) c.always_remember=nil end},
 {'BAMBOO_HUT_DOOR_HORIZ',function(c) c.block_sight=nil end},{'BAMBOO_HUT_DOOR_HORIZ',function(c) c.door_opened='BAMBOO_HUT_DOOR_OPEN' end},
 {'BAMBOO_HUT_DOOR_HORIZ',function(c) c.dig='BAMBOO_HUT_FLOOR' end},{'BAMBOO_HUT_DOOR_HORIZ',function(c) c.notice=nil end},
 {'BAMBOO_HUT_DOOR_HORIZ',function(c) c.is_door=nil end},{'BAMBOO_HUT_DOOR_HORIZ',function(c) c.does_block_move=true end},
 {'BAMBOO_HUT_DOOR_HORIZ',function(c) c.door_player_check=nil;c.block_move=function() return true end end},
 {'BAMBOO_HUT_DOOR_VERT',function(c) c.dig='FLOOR' end},{'BAMBOO_HUT_DOOR_VERT',function(c) c.door_opened='BAMBOO_HUT_DOOR_HORIZ_OPEN' end},
 {'BAMBOO_HUT_DOOR_HORIZ_OPEN',function(c) c.block_sight=true end},{'BAMBOO_HUT_DOOR_HORIZ_OPEN',function(c) c.door_closed='BAMBOO_HUT_DOOR' end},
 {'BAMBOO_HUT_DOOR_OPEN_VERT',function(c) c.does_block_move=true end},{'BAMBOO_HUT_DOOR_OPEN_VERT',function(c) c.notice=true end},
 {'BAMBOO_HUT_FLOOR',function(c) c.does_block_move=true end},{'BAMBOO_HUT_FLOOR',function(c) c.block_sight=true end},
 {'BAMBOO_HUT_FLOOR',function(c) c.on_move=function() end end},{'BAMBOO_HUT_FLOOR',function(c) c.grow=nil end},
 {'BAMBOO_HUT_FLOOR',function(c) c.add_mos={{image='terrain/bamboo/floor_deco_cooking_pit_c_01.png'}} end},
 {'BAMBOO_HUT_FLOOR',function(c) c.add_displays={setmetatable({image='terrain/bamboo/bed_middle_floor_01.png'},meta)} end},
 {'BAMBOO_HUT_FLOOR',function(c) c.change_level=1 end},{'BAMBOO_HUT_FLOOR',function(c) c.always_remember=true end},
 {'BAMBOO_HUT_COOKING3',function(c) c.add_mos={{image='terrain/bamboo/floor_deco_cooking_pit_a_01.png'}} end},
 {'BAMBOO_HUT_COOKING3',function(c) c.add_mos[2]={image='terrain/bamboo/floor_deco_cooking_pit_b_01.png'} end},
 {'BAMBOO_HUT_COOKING3',function(c) c.add_mos[1].display_y=-1 end},{'BAMBOO_HUT_COOKING3',function(c) c.on_stand=function() end end},
 {'BAMBOO_HUT_COOKING3',function(c) c.name='bamboo hut floor' end},
 {'JUNGLE_TREE7',function(c) c.dig=nil end},{'JUNGLE_GRASS',function(c) c.does_block_move=true end},
 {'JUNGLE_GRASS_UP_WILDERNESS',function(c) c.change_zone='gorbat-pride' end},{'DEEP_WATER',function(c) c.air_level=-1 end},
} do
 local c=deep(iDefs[m[1]]);m[2](c)
 eq(T.batch4Kind(c,'town-irkkk'),nil,'TW6 altered rule field stays native '..m[1])
end
for _,id in ipairs{'FLOOR','WALL','DOOR','GRASS','JUNGLE_DIRT','UP','DOWN','SHALLOW_WATER','POISON_DEEP_WATER',
 'BAMBOO_HUT_DOOR','BAMBOO_HUT_DOOR_OPEN'} do
 if iDefs[id] then eq(T.batch4Kind(methods.clone(iDefs[id]),'town-irkkk'),nil,'TW6 not claimed as an Irkkk kind '..id) end
end
-- The cooking pit is the one Irkkk prop: its exact native add_mos is kept.
local ck,cmo=T.townProp(methods.clone(iDefs.BAMBOO_HUT_COOKING3),'town-irkkk')
eq(ck..'|'..cmo.image,'hut-cooking|terrain/bamboo/floor_deco_cooking_pit_c_01.png','TW6 cooking pit prop layer')
eq(T.townProp(methods.clone(iDefs.BAMBOO_HUT_FLOOR),'town-irkkk'),nil,'TW6 plain hut floor has no prop')
eq(T.townProp(methods.clone(iDefs.BAMBOO_HUT_COOKING3),'town-gates-of-morning'),nil,'TW6 cooking prop is Irkkk only')
-- Map legend from the real map file: shops are actors (4th argument) on hut floor, no trap.
local itiles={}
do
 local chunk=assert(loadstring(readFile(data..'/maps/towns/irkkk.lua'),'@/data/maps/towns/irkkk.lua'))
 setfenv(chunk,setmetatable({colors=colors,_t=function(s) return s end,
  quickEntity=function() end,defineTile=function(c,g,o,a,trap) itiles[c]={g,o,a,trap} end,
  addSpot=function() end,addZone=function() end},{__index=_G}))
 itiles.map=chunk()
end
for c,actor in pairs{['1']='YEEK_STORE_GEM',['2']='YEEK_STORE_2HANDS',['3']='YEEK_STORE_CLOTH',['4']='YEEK_STORE_1HAND',
 ['5']='YEEK_STORE_LEATHER',['6']='YEEK_STORE_NATURE'} do
 eq(itiles[c][1]..'|'..tostring(itiles[c][2])..'|'..itiles[c][3]..'|'..tostring(itiles[c][4]),'BAMBOO_HUT_FLOOR|nil|'..actor..'|nil',
  'TW6 Irkkk shop '..c..' is an actor on hut floor, no trap')
end
eq(itiles['#'][1]..'|'..itiles['_'][1]..'|'..itiles['+'][1]..'|'..itiles['*'][1]..'|'..itiles['~'][1]..'|'..itiles['.'][1]..'|'..itiles.t[1]..'|'..itiles['<'][1],
 'BAMBOO_HUT_WALL|BAMBOO_HUT_FLOOR|BAMBOO_HUT_DOOR|BAMBOO_HUT_COOKING3|DEEP_WATER|JUNGLE_GRASS|JUNGLE_TREE|JUNGLE_GRASS_UP_WILDERNESS','TW6 Irkkk map legend')
local counts={}
for ch in itiles.map:gmatch('[^\n]') do counts[ch]=(counts[ch] or 0)+1 end
eq(counts['#']..'/'..counts['_']..'/'..counts['+']..'/'..counts['*']..'/'..counts['~']..'/'..counts['.']..'/'..counts.t,
 '139/119/3/4/271/1590/367','TW6 Irkkk map cell counts')

-- Scene: a hut (walls, a horizontal door in the south wall, a vertical door in
-- the east wall, floor, a cooking pit, a shopkeeper actor on the floor) on
-- jungle grass by the lake, a tree and the world exit.
local iplan={
 '~~..t',
 '~#H##',
 '~#_*V',
 '~#1_#',
 '~#D#<'}
local isym={['~']='DEEP_WATER',['.']='JUNGLE_GRASS',t='JUNGLE_TREE7',['#']='BHW_V_FULL1',H='BHW_H_FULL2',['_']='BAMBOO_HUT_FLOOR',
 ['*']='BAMBOO_HUT_COOKING3',['1']='BAMBOO_HUT_FLOOR',V='BAMBOO_HUT_DOOR_VERT',D='BAMBOO_HUT_DOOR_HORIZ',['<']='JUNGLE_GRASS_UP_WILDERNESS'}
local im=townMap(5,5,function(x,y) return iDefs[isym[iplan[y+1]:sub(x+1,x+1)]] end)
local ACTOR=100
im.layers[ACTOR]={}
local updated={};im.updateMap=function(_,x,y) updated[#updated+1]=x..','..y end
local keeper={define_as='YEEK_STORE_GEM',name='gem crafter',image='npc/humanoid_yeek_yeek_psionic.png',store={},faction='the-way'}
local keeperFields={};for k,v in pairs(keeper) do keeperFields[k]=v end
im(2,3,ACTOR,keeper)
local shopFloorRules={};for k,v in pairs(im(2,3,1)) do shopFloorRules[k]=v end
local wallRules={};for k,v in pairs(im(1,1,1)) do wallRules[k]=v end
local doorRules={};for k,v in pairs(im(2,4,1)) do doorRules[k]=v end
env.game={zone={short_name='town-irkkk'}}
local ih={zone={short_name='town-irkkk'},level={map=im,data={all_remembered=true}}}
mode='refined';T.apply(ih)
eq(ih.checker_mode,'refined','TW6 Irkkk refined mode')
local function ii(x,y) return im(x,y,1).replace_display and im(x,y,1).replace_display.image end
eq(ii(1,1),'checker-revised+refined/bamboo/wall-6-0.png','TW6 hut corner (E,S)')
eq(ii(2,1),'checker-revised+refined/bamboo/wall-10-1.png','TW6 decorated north wall (E,W)')
eq(ii(3,1),'checker-revised+refined/bamboo/wall-10-0.png','TW6 north wall over the cooking pit (E,W)')
eq(ii(4,1),'checker-revised+refined/bamboo/wall-12-1.png','TW6 hut corner over the vertical door (S,W)')
eq(ii(1,2),'checker-revised+refined/bamboo/wall-5-1.png','TW6 hut side wall (N,S)')
eq(ii(4,3),'checker-revised+refined/bamboo/wall-1-1.png','TW6 wall below the vertical door counts it (N)')
eq(ii(1,4),'checker-revised+refined/bamboo/wall-3-1.png','TW6 wall beside the horizontal door counts it (N,E)')
eq(ii(3,4),'checker-revised+refined/bamboo/wall-8-1.png','TW6 wall east of the horizontal door counts it (W)')
eq(ii(2,4),'checker-revised+refined/bamboo/door-closed-horizontal0.png','TW6 closed horizontal door')
eq(ii(4,2),'checker-revised+refined/bamboo/door-closed-vertical0.png','TW6 closed vertical door')
eq(ii(2,2),'checker-revised+refined/bamboo/floor0.png','TW6 hut floor')
eq(ii(2,3),'checker-revised+refined/bamboo/floor1.png','TW6 shop cell is plain board hut floor')
eq(ii(3,2),'checker-revised+refined/bamboo/floor1.png','TW6 cooking pit floor')
local pit=im(3,2,1).replace_display.add_displays
eq(pit and #pit==1 and pit[1].image,'terrain/bamboo/floor_deco_cooking_pit_c_01.png','TW6 cooking pit keeps its native prop')
eq(im(2,2,1).replace_display.add_displays,nil,'TW6 plain floor carries no prop')
eq(ii(2,0),'checker-revised+refined/caldera/floor0.png','TW6 jungle grass is Caldera floor')
eq(ii(3,0),'checker-revised+refined/caldera/floor1.png','TW6 jungle grass parity')
eq(ii(4,0):match('^checker%-revised%+refined/caldera/tree%-[abc]0%.png$')~=nil,true,'TW6 jungle tree is a Caldera tree')
eq(ii(4,4),'checker-revised+refined/caldera/exit-world0.png','TW6 jungle world exit')
eq(ii(0,0),'checker-revised+refined/deep6-0-0.png','TW6 lake corner beside jungle grass (E,S)')
eq(ii(0,2),'checker-revised+refined/deep5-0-0.png','TW6 lake beside a hut wall (N,S)')
eq(im(2,3,ACTOR),keeper,'TW6 shopkeeper actor untouched')
for k,v in pairs(keeperFields) do eq(keeper[k],v,'TW6 shopkeeper field '..k) end
for k,v in pairs(shopFloorRules) do if k~='replace_display' and k~='_checker_terrain' then eq(im(2,3,1)[k],v,'TW6 shop floor rule field '..tostring(k)) end end
for k,v in pairs(wallRules) do if k~='replace_display' and k~='_checker_terrain' then eq(im(1,1,1)[k],v,'TW6 wall rule field '..tostring(k)) end end
for k,v in pairs(doorRules) do if k~='replace_display' and k~='_checker_terrain' then eq(im(2,4,1)[k],v,'TW6 door rule field '..tostring(k)) end end
eq(T.classify(im(1,1,1)),nil,'TW6 hut wall is forest art, not a stone record')
eq(next(im._checker_korpul or {}),nil,'TW6 Irkkk has no stone records')
-- Door opening swaps the grid in place (mod/class/Grid.lua:82); a repair of
-- the touched rectangle draws the open door and keeps the wall masks.
im(2,4,1,methods.clone(iDefs.BAMBOO_HUT_DOOR_HORIZ_OPEN))
im(4,2,1,methods.clone(iDefs.BAMBOO_HUT_DOOR_OPEN_VERT))
T.repair(ih,1,3,4,4);T.repair(ih,3,1,4,3)
eq(table.concat(updated,' '),'2,4 4,2','TW6 repair redraws exactly the two opened doors')
eq(ii(2,4),'checker-revised+refined/bamboo/door-open-horizontal0.png','TW6 opened horizontal door')
eq(ii(4,2),'checker-revised+refined/bamboo/door-open-vertical0.png','TW6 opened vertical door')
eq(ii(1,4),'checker-revised+refined/bamboo/wall-3-1.png','TW6 wall still joins the open door')
eq(ii(4,1),'checker-revised+refined/bamboo/wall-12-1.png','TW6 corner still joins the open vertical door')
mode='blockout';T.apply(ih)
eq(ii(1,1),'checker-revised+tree0.png','TW6 blockout hut wall reads as blocking')
eq(ii(2,2),'checker-revised+grass0.png','TW6 blockout hut floor reads as floor')
eq(ii(2,4),'checker-revised+grass0.png','TW6 blockout open door reads as floor')
eq(ii(4,4),'checker-revised+exit0.png','TW6 blockout jungle exit')
mode='vanilla';T.apply(ih)
for x=0,4 do for y=0,4 do eq(im(x,y,1).replace_display,nil,'TW6 native mode restores Irkkk '..x..','..y) end end
mode='refined';T.apply(ih)
eq(ii(1,1),'checker-revised+refined/bamboo/wall-6-0.png','TW6 refined restore wall')
eq(ii(3,2),'checker-revised+refined/bamboo/floor1.png','TW6 refined restore cooking floor')
eq(im(3,2,1).replace_display.add_displays[1].image,'terrain/bamboo/floor_deco_cooking_pit_c_01.png','TW6 refined restore cooking prop')
eq(im(2,3,ACTOR),keeper,'TW6 shopkeeper actor still untouched after the round trip')
-- The Grid superload's door hook: display-only repair after the native
-- open, same return value, and nothing for a door that did not change.
do
 local calls={}
 local opened=methods.clone(iDefs.BAMBOO_HUT_DOOR_HORIZ_OPEN)
 local level={map=im}
 local base={loadList=function() return {} end,getMapObjects=function() end}
 function base.block_move(self,x,y,e,act)
  if act and self.door_opened and e.open_door then level.map(x,y,1,opened) end
  return true
 end
 local genv=setmetatable({loadPrevious=function() return base end,require=function() return T end},{__index=_G})
 genv.game={level=level,checkerRepairTerrain=function(_,...) calls[#calls+1]={...} end}
 local chunk=assert(loadfile(root..'superload/mod/class/Grid.lua'));setfenv(chunk,genv)
 local G=chunk()
 local closed=methods.clone(iDefs.BAMBOO_HUT_DOOR_HORIZ);im(2,4,1,closed)
 eq(G.block_move(closed,2,4,{open_door=true},false),true,'TW6 hook: a non-acting probe returns the native result')
 eq(#calls,0,'TW6 hook: no repair without a door opening')
 eq(G.block_move(closed,2,4,{},true),true,'TW6 hook: an actor that cannot open doors')
 eq(#calls,0,'TW6 hook: no repair when the grid did not change')
 eq(G.block_move(closed,2,4,{open_door=true},true),true,'TW6 hook: native open returns the native result')
 eq(im(2,4,1),opened,'TW6 hook: the native call placed the open door')
 eq(#calls==1 and table.concat(calls[1],','),'1,3,3,5','TW6 hook: repair of the 3x3 round the door')
 local wall=methods.clone(iDefs.BHW_V_FULL1)
 eq(G.block_move(wall,1,1,{open_door=true},true),true,'TW6 hook: a wall uses the native path unchanged')
 eq(#calls,1,'TW6 hook: no repair for a grid without door_opened')
end
-- Old save: an Irkkk level generated before the list stamp stays native.
local io2=townMap(4,1,function(x) local g=deep(iDefs[({'BHW_V_FULL1','BAMBOO_HUT_FLOOR','JUNGLE_GRASS','BAMBOO_HUT_DOOR_HORIZ'})[x+1]]);g._checker_town_source=nil;return g end)
T.apply({zone={short_name='town-irkkk'},level={map=io2,data={all_remembered=true}}})
for x=0,3 do eq(io2(x,0,1).replace_display,nil,'TW6 old-save Irkkk cell stays native '..x) end
-- Other towns and zones: TW6 identities never leak; a non-town zone is unaffected.
for _,zone in ipairs{'gorbat-pride','town-derth','town-gates-of-morning'} do
 local oz={zone={short_name=zone},level={map=townMap(4,1,function(x) return ({iDefs.BHW_V_FULL1,iDefs.BAMBOO_HUT_FLOOR,iDefs.BAMBOO_HUT_DOOR_HORIZ,iDefs.BAMBOO_HUT_COOKING3})[x+1] end),data={all_remembered=true}}}
 env.game={zone=oz.zone}
 T.apply(oz)
 for x=0,3 do eq(oz.level.map(x,0,1).replace_display,nil,'TW6 Irkkk hut stays native in '..zone..' '..x) end
end
local cz={zone={short_name='noxious-caldera'},level={map=townMap(2,1,function(x) return ({iDefs.JUNGLE_GRASS,iDefs.BHW_V_FULL1})[x+1] end),data={}}}
env.game={zone=cz.zone}
T.apply(cz)
eq(cz.level.map(0,0,1).replace_display.image,'checker-revised+refined/caldera/floor0.png','TW6 Caldera jungle grass unchanged')
eq(cz.level.map(1,0,1).replace_display,nil,'TW6 hut wall stays native in the Caldera')
local gDefs=loadDefs('/data/zones/town-gates-of-morning/grids.lua')
eq(T.batch4Kind(methods.clone(gDefs.GOLDEN_MOUNTAIN_WALL3),'town-gates-of-morning'),'gold-mountain','TW6 Gates mountain unchanged')
eq(T.batch4Kind(methods.clone(gDefs.DEEP_WATER),'town-gates-of-morning'),'deep','TW6 Gates water unchanged')
end)()
-- S5: six reachable zones on existing families, no new art. Zone lists are
-- loaded like Grid:loadList (nested imports stamped, then the outer list;
-- Tannen's Tower, the valley and the Ring of Blood add their own list stamp).
-- Each forest-side zone is its own batch4 family; stone uses basic.lua
-- stamps; zone-local identities also need the zone list stamp (old saves).
;(function()
local s5Zones={'dreadfell-ambush','shadow-crypt','tannen-tower','valley-moon','ring-of-blood','arena-unlock'}
local aDefs=loadDefs('/data/zones/dreadfell-ambush/grids.lua')
local cDefs=loadDefs('/data/zones/shadow-crypt/grids.lua')
local tDefs=loadDefs('/data/zones/tannen-tower/grids.lua')
local vDefs=loadDefs('/data/zones/valley-moon/grids.lua')
local rDefs=loadDefs('/data/zones/ring-of-blood/grids.lua')
local uDefs=loadDefs('/data/zones/arena-unlock/grids.lua')
local tFile,vFile,rFile='/data/zones/tannen-tower/grids.lua','/data/zones/valley-moon/grids.lua','/data/zones/ring-of-blood/grids.lua'
-- Gating: four stone zones, three of them combined; two forest-only zones.
eq(T.variant({short_name='shadow-crypt'}),'SHADOW_CRYPT','S5 Shadow Crypt stone gate')
eq(T.variant({short_name='tannen-tower'}),'TANNEN_TOWER','S5 Tannen stone gate')
eq(T.variant({short_name='ring-of-blood'}),'RING_OF_BLOOD','S5 Ring of Blood stone gate')
eq(T.variant({short_name='arena-unlock'}),'ARENA_UNLOCK','S5 Derth arena stone gate')
for _,zone in ipairs{'dreadfell-ambush','valley-moon'} do eq(T.variant({short_name=zone}),nil,'S5 forest-only zone has no stone variant '..zone) end
for _,zone in ipairs{'tannen-tower','ring-of-blood','arena-unlock'} do eq(T.combined[zone],true,'S5 combined '..zone) end
for _,zone in ipairs{'shadow-crypt','dreadfell-ambush','valley-moon'} do eq(T.combined[zone],nil,'S5 not combined '..zone) end
for _,zone in ipairs{'arena','sludgenest','infinite-dungeon','valley-moon-caverns'} do -- S6 gates gorbat-pride and eruan
 eq(T.variant({short_name=zone}),nil,'S5 ungated zone stays without stone '..zone)
end
-- Stamps: the zone list stamps its own and nested definitions; general
-- stamps survive; zones without a zone-local identity get no zone stamp.
eq(tDefs.TUP._checker_zone_source.file,tFile,'S5 Tannen list stamps TUP')
eq(tDefs.TUP._checker_grid_source.id,'UP','S5 TUP keeps the inherited basic.lua UP stamp')
eq(tDefs.FLOOR._checker_grid_source.file,'/data/general/grids/basic.lua','S5 nested basic keeps its stamp')
eq(tDefs.DEEP_WATER._checker_water_source.file,'/data/general/grids/water.lua','S5 nested water keeps its stamp')
eq(vDefs.MOONSTONE3._checker_zone_source.id,'MOONSTONE3','S5 valley list stamps a moonstone variant')
eq(vDefs.GRASS._checker_forest_source.file,'/data/general/grids/forest.lua','S5 valley grass keeps its forest stamp')
eq(rDefs.LAVA_WALL_OPAQUE._checker_zone_source.file,rFile,'S5 Ring list stamps its lava pit')
eq(rDefs.SAND._checker_surface_sand_source.id,'SAND','S5 Ring sand keeps its sand.lua stamp')
eq(aDefs.GRASS._checker_zone_source,nil,'S5 ambush list has no zone stamp (no local identity)')
eq(uDefs.WALL_SEE._checker_zone_source,nil,'S5 Derth arena list has no zone stamp')
eq(cDefs.QUICK_EXIT._checker_zone_source,nil,'S5 Shadow Crypt list has no zone stamp')
-- Exact forest-side kinds per zone.
local function k(defs,id,zone) return T.batch4Kind(methods.clone(defs[id]),zone) end
local positive={
 {'dreadfell-ambush',aDefs,{GRASS='grass',GRASS_PATCH3='grass',GRASS_PATCH14='grass',FLOWER2='flower',TREE='tree',TREE17='tree',GRASS_UP_WILDERNESS='exit'}},
 {'valley-moon',vDefs,{GRASS='grass',GRASS_PATCH7='grass',TREE='tree',TREE30='tree',POISON_DEEP_WATER='poison',POISON_DEEP_WATER4='poison',
  DEEP_WATER='deep',MOUNTAIN_WALL='wall',MOUNTAIN_WALL6='wall',MOONSTONE1='moonstone',MOONSTONE8='moonstone',PORTAL_DEMON='portal'}},
 {'tannen-tower',tDefs,{GRASS='grass',TREE='tree',TREE9='tree',DEEP_WATER='deep'}},
 {'ring-of-blood',rDefs,{SAND='sand',LAVA_WALL='lava',LAVA_WALL_OPAQUE='lava'}},
 {'arena-unlock',uDefs,{GRASS='grass',GRASS_PATCH2='grass',TREE='tree',TREE4='tree',SAND='sand'}},
}
for _,p in ipairs(positive) do
 for id,kind in pairs(p[3]) do
  eq(k(p[2],id,p[1]),kind,'S5 exact '..p[1]..' '..id)
  for _,other in ipairs(s5Zones) do
   if other~=p[1] then
    local got=k(p[2],id,other)
    -- A general identity may be shared with another S5 zone's exact list;
    -- a zone-local one never is.
    if kind=='moonstone' or kind=='portal' or kind=='lava' or kind=='poison' or kind=='wall' then eq(got,nil,'S5 '..p[1]..' '..id..' not claimed by '..other) end
   end
  end
  for _,fam in ipairs{'beach','meadow','caldera','town-derth','town-zigur','gorbat-pride'} do
   local got=k(p[2],id,fam)
   if kind=='moonstone' or kind=='portal' or (kind=='lava' and fam~='caldera') then eq(got,nil,'S5 zone-local '..id..' stays native in '..fam) end
  end
 end
end
eq(k(vDefs,'MOONSTONE','valley-moon'),nil,'S5 untiled MOONSTONE base (no stone layer) stays native')
-- Old save: zone-local identities without the zone list stamp stay native.
for _,c in ipairs{{vDefs,'MOONSTONE5','valley-moon'},{vDefs,'PORTAL_DEMON','valley-moon'},{rDefs,'LAVA_WALL','ring-of-blood'},{rDefs,'LAVA_WALL_OPAQUE','ring-of-blood'}} do
 local g=deep(c[1][c[2]]);g._checker_zone_source=nil
 eq(T.batch4Kind(g,c[3]),nil,'S5 old-save (unstamped) '..c[2]..' stays native')
 g=deep(c[1][c[2]]);g._checker_zone_source={file='/data/zones/other/grids.lua',id=c[2]}
 eq(T.batch4Kind(g,c[3]),nil,'S5 foreign list stamp '..c[2]..' stays native')
end
-- Altered rule fields and layers stay native.
for _,m in ipairs{
 {vDefs,'MOONSTONE2','valley-moon',function(c) c.does_block_move=nil end},{vDefs,'MOONSTONE2','valley-moon',function(c) c.block_sight=nil end},
 {vDefs,'MOONSTONE2','valley-moon',function(c) c.add_displays[1].image='terrain/moonstone_03.png' end},
 {vDefs,'MOONSTONE2','valley-moon',function(c) c.add_displays[1].display_h=1 end},
 {vDefs,'MOONSTONE2','valley-moon',function(c) c.add_displays[2]=setmetatable({image='terrain/moonstone_02.png'},meta) end},
 {vDefs,'MOONSTONE2','valley-moon',function(c) c.block_move=function() return true end end},
 {vDefs,'MOONSTONE2','valley-moon',function(c) c.on_stand=function() end end},
 {vDefs,'MOONSTONE2','valley-moon',function(c) c.dig='GRASS' end},{vDefs,'MOONSTONE2','valley-moon',function(c) c.change_level=1 end},
 {vDefs,'PORTAL_DEMON','valley-moon',function(c) c.on_move=function() end end},{vDefs,'PORTAL_DEMON','valley-moon',function(c) c.change_zone='demon-plane' end},
 {vDefs,'PORTAL_DEMON','valley-moon',function(c) c.does_block_move=true end},{vDefs,'PORTAL_DEMON','valley-moon',function(c) c.add_displays[1].z=18 end},
 {vDefs,'PORTAL_DEMON','valley-moon',function(c) c.add_displays[1].image='terrain/demon_portal.png' end},
 {vDefs,'PORTAL_DEMON','valley-moon',function(c) c.orb_portal={} ; c.special=true end},
 {vDefs,'POISON_DEEP_WATER3','valley-moon',function(c) c.on_stand=function() end end},
 {vDefs,'MOUNTAIN_WALL3','valley-moon',function(c) c.dig=nil end},{vDefs,'MOUNTAIN_WALL3','valley-moon',function(c) c.can_pass=nil end},
 {vDefs,'TREE5','valley-moon',function(c) c.dig=nil end},{vDefs,'GRASS','valley-moon',function(c) c.does_block_move=true end},
 {rDefs,'LAVA_WALL','ring-of-blood',function(c) c.block_sight=true end},{rDefs,'LAVA_WALL','ring-of-blood',function(c) c.does_block_move=nil end},
 {rDefs,'LAVA_WALL_OPAQUE','ring-of-blood',function(c) c.block_esp=nil end},{rDefs,'LAVA_WALL_OPAQUE','ring-of-blood',function(c) c.block_sense=nil end},
 {rDefs,'LAVA_WALL','ring-of-blood',function(c) c.on_stand=function() end end},{rDefs,'LAVA_WALL','ring-of-blood',function(c) c.type='floor' end},
 {rDefs,'LAVA_WALL','ring-of-blood',function(c) c.shader='lava' end},{rDefs,'LAVA_WALL','ring-of-blood',function(c) c.add_mos={{image='terrain/lava_floor.png'}} end},
 {rDefs,'SAND','ring-of-blood',function(c) c.does_block_move=true end},
 {aDefs,'GRASS_UP_WILDERNESS','dreadfell-ambush',function(c) c.change_zone='dreadfell' end},
 {aDefs,'GRASS_UP_WILDERNESS','dreadfell-ambush',function(c) c.change_level_check=function() end end},
 {aDefs,'TREE8','dreadfell-ambush',function(c) c.can_pass={pass_tree=1,pass_wall=1} end},
 {uDefs,'TREE8','arena-unlock',function(c) c.block_sight=nil end},{uDefs,'SAND','arena-unlock',function(c) c.on_stand=function() end end},
 {tDefs,'DEEP_WATER','tannen-tower',function(c) c.air_level=-1 end},
} do
 local c=deep(m[1][m[2]]);m[4](c)
 eq(T.batch4Kind(c,m[3]),nil,'S5 altered '..m[3]..' '..m[2]..' stays native')
end
-- Callback, lever, portal and transition cells keep native on both adapters.
-- S11: Tannen's levers and the tiled lever doors (Tannen, arena) are exact
-- S11 cells (tests/terrain_s11.lua); the untiled bases stay native.
local natives={{tDefs,'tannen-tower',{'PORTAL_BACK','GENERIC_LEVER_DOOR',
  'GENERIC_LEVER_DOOR_OPEN','LAVA_FLOOR','ROCKY_GROUND'}},
 {rDefs,'ring-of-blood',{'CONTROL_ORB','GENERIC_LEVER','GENERIC_LEVER_DOOR'}},
 {uDefs,'arena-unlock',{'GENERIC_LEVER_DOOR','LOCK','WALL_SEE'}},
 {vDefs,'valley-moon',{'MOONSTONE','ROCKY_GROUND','SHALLOW_WATER'}},
 {cDefs,'shadow-crypt',{'QUICK_EXIT','GENERIC_LEVER_DOOR'}}}
for _,c in ipairs(natives) do
 env.game={zone={short_name=c[2]}}
 for _,id in ipairs(c[3]) do
  if c[1][id] then
   eq(T.batch4Kind(methods.clone(c[1][id]),c[2]),nil,'S5 '..c[2]..' '..id..' not a forest kind')
   -- (S14: Tannen's return portal is an S14 cell with its own stamp, tests/terrain_s14.lua.)
   local g=methods.clone(c[1][id]);g._checker_s14_source=nil
   eq(T.classify(g),nil,'S5 '..c[2]..' '..id..' not a stone kind')
  end
 end
end
-- Map-file quickEntity grids (no define_as): Tannen's open sky, the valley's
-- passage to the caverns (its native image key is misspelt 'iamge').
-- The valley has no stone variant: its imported basic.lua grids are not
-- forest kinds either, so they would stay native.
for _,id in ipairs{'UP','DOWN','FLOOR','WALL'} do eq(T.batch4Kind(methods.clone(vDefs[id]),'valley-moon'),nil,'S5 valley basic '..id..' not a forest kind') end
local sky=setmetatable({name='open sky',display=' ',does_block_move=true},meta)
local passage=setmetatable({always_remember=true,type='floor',subtype='grass',show_tooltip=true,name='Passage to the caverns',
 display='>',notice=true,change_level=2,change_zone='valley-moon-caverns',keep_old_lev=true,iamge='terrain/grass.png',add_mos={{image='terrain/stair_down.png'}}},meta)
eq(T.batch4Kind(sky,'tannen-tower'),nil,'S5 open sky stays native')
eq(T.batch4Kind(passage,'valley-moon'),nil,'S5 valley passage quickEntity stays native')
env.game={zone={short_name='tannen-tower'}}
eq(T.classify(sky),nil,'S5 open sky is not stone')
-- Stone side: exact basic.lua identities in each stone zone; Tannen's
-- reversed stairs through their base contract.
for zone,defs in pairs{['shadow-crypt']=cDefs,['tannen-tower']=tDefs,['ring-of-blood']=rDefs,['arena-unlock']=uDefs} do
 env.game={zone={short_name=zone}}
 for id,kind in pairs{FLOOR='floor',OLD_FLOOR='floor',HARDWALL='hardwall',HARDWALL_SOUTH3='hardwall',WALL='wall',WALL_NORTH2='wall',
  OLD_WALL='old-wall',DOOR='door-closed',DOOR_OPEN='door-open',UP='stairs-up',DOWN='stairs-down',UP_WILDERNESS='stairs-world'} do
  eq(T.classify(methods.clone(defs[id])),kind,'S5 '..zone..' stone '..id)
 end
end
env.game={zone={short_name='tannen-tower'}}
eq(T.classify(methods.clone(tDefs.TUP)),'stairs-up','S5 Tannen TUP (up art, change_level +1)')
eq(T.classify(methods.clone(tDefs.TDOWN)),'stairs-down','S5 Tannen TDOWN (down art, change_level -1)')
eq(methods.clone(tDefs.TUP).change_level,1,'S5 TUP rule untouched by the view')
for _,m in ipairs{
 function(c) c._checker_zone_source=nil end,function(c) c._checker_zone_source={file='/data/zones/other/grids.lua',id='TUP'} end,
 function(c) c._checker_grid_source=nil end,function(c) c.change_level=-1 end,function(c) c.change_level=2 end,
 function(c) c.change_zone='wilderness' end,function(c) c.add_mos[1].image='terrain/stair_down.png' end,
 function(c) c.add_mos[2]={image='terrain/padlock2.png'} end,function(c) c.on_move=function() end end,
 function(c) c.notice=nil end,function(c) c.does_block_move=true end,function(c) c.change_level_check=function() end end,
} do
 local c=deep(tDefs.TUP);m(c)
 eq(T.classify(c),nil,'S5 altered or unstamped TUP stays native')
end
local tdown=deep(tDefs.TDOWN);tdown.change_level=1
eq(T.classify(tdown),nil,'S5 TDOWN with the unreversed direction stays native')
for _,zone in ipairs{'dreadfell','ruins-kor-pul','shadow-crypt','town-derth'} do
 env.game={zone={short_name=zone}}
 eq(T.classify(methods.clone(tDefs.TUP)),nil,'S5 TUP is Tannen only ('..zone..')')
end
env.game={zone={short_name='tannen-tower'}}
do local g=methods.clone(tDefs.PORTAL_BACK);g._checker_s14_source=nil
 eq(T.classify(g),nil,'S5 Tannen portal back without the S14 stamp stays native') end
-- The flooded floor's native marble-to-water edge carrier (fixture probe).
local function edged(id,mos,extra)
 local g=deep(tDefs[id]);local d={image='invis.png',add_mos=mos}
 for key,v in pairs(extra or {}) do d[key]=v end
 g.add_displays={setmetatable(d,meta)};return g
end
local edge={{image='terrain/marble_water/marble_floor_2_to_water_outer_2.png'},{image='terrain/marble_water/marble_floor_2_to_water_outer_8.png'}}
eq(T.classify(edged('FLOOR',edge)),'floor','S5 Tannen floor with its native water edge')
eq(T.classify(edged('TUP',{{image='terrain/marble_water/marble_floor_2_to_water_outer_6.png'}})),'stairs-up','S5 Tannen TUP with its native water edge')
eq(T.classify(edged('TDOWN',{{image='terrain/marble_water/marble_floor_2_to_water_outer_4.png'}})),'stairs-down','S5 Tannen TDOWN with its native water edge')
eq(T.classify(edged('FLOOR',{{image='terrain/grass/grass_2_01.png'}})),nil,'S5 Tannen floor with a foreign edge stays native')
eq(T.classify(edged('FLOOR',edge,{z=18})),nil,'S5 Tannen floor edge carrier at a depth stays native')
eq(T.classify(edged('FLOOR',{})),nil,'S5 Tannen floor with an empty carrier stays native')
eq(T.classify(edged('HARDWALL',edge)),nil,'S5 Tannen edge view is for floor and stairs only')
local twoCarriers=edged('FLOOR',edge);twoCarriers.add_displays[2]=twoCarriers.add_displays[1]
eq(T.classify(twoCarriers),nil,'S5 Tannen floor with two carriers stays native')
-- S2/T21 (flipped for the census zones): the same native edge carrier on plain
-- FLOOR is judged as the floor in Dreadfell, Vor, Scintillating, Reknor and
-- Halfling ruins; towns and other zones keep native. Stairs keep Tannen-only.
for _,zone in ipairs{'dreadfell','vor-armoury','scintillating-caves','reknor','halfling-ruins'} do
 env.game={zone={short_name=zone}}
 eq(T.classify(edged('FLOOR',edge)),'floor','S2/T21 water-edged floor view in '..zone)
 eq(T.classify(edged('FLOOR',{{image='terrain/grass/grass_2_01.png'}})),nil,'S2/T21 foreign edge stays native in '..zone)
 eq(T.classify(edged('FLOOR',edge,{z=18})),nil,'S2/T21 edge carrier with a depth stays native in '..zone)
 eq(T.classify(edged('FLOOR',edge,{image='terrain/marble_floor.png'})),nil,'S2/T21 visible carrier stays native in '..zone)
 eq(T.classify(edged('FLOOR',{})),nil,'S2/T21 empty carrier stays native in '..zone)
 eq(T.classify(edged('HARDWALL',edge)),nil,'S2/T21 edge view is floor only in '..zone)
 eq(T.classify(edged('UP',edge)),nil,'S2/T21 edged stairs stay native in '..zone)
 local wet=edged('FLOOR',edge);wet.block_sight=true
 eq(T.classify(wet),nil,'S2/T21 edged floor with a changed rule stays native in '..zone)
 local two=edged('FLOOR',edge);two.add_displays[2]=two.add_displays[1]
 eq(T.classify(two),nil,'S2/T21 two carriers stay native in '..zone)
end
for _,zone in ipairs{'town-last-hope','shadow-crypt','ruins-kor-pul','rhaloren-camp'} do
 env.game={zone={short_name=zone}}
 eq(T.classify(edged('FLOOR',edge)),nil,'S5/S2 water-edged floor view stays native in '..zone)
end
env.game={zone={short_name='tannen-tower'}}
-- Remembered install: the S5 stone zones' all_remembered levels only.
local cm=townMap(3,1,function(x) return ({cDefs.OLD_WALL,cDefs.FLOOR,cDefs.UP})[x+1] end)
env.game={zone={short_name='shadow-crypt'}}
local ch={zone={short_name='shadow-crypt'},level={map=cm,data={all_remembered=true}}}
eq(T.installRemembered(ch),3,'S5 Shadow Crypt L3 installs every remembered stone cell')
cm=townMap(3,1,function(x) return ({cDefs.OLD_WALL,cDefs.FLOOR,cDefs.UP})[x+1] end)
ch.level={map=cm,data={}}
eq(T.installRemembered(ch),0,'S5 Shadow Crypt L1/L2 (not all_remembered) keep FOV semantics')
for _,zone in ipairs{'valley-moon','dreadfell-ambush','dreadfell','ruins-kor-pul'} do
 local om=townMap(2,1,function(x) return ({cDefs.OLD_WALL,cDefs.FLOOR})[x+1] end)
 env.game={zone={short_name=zone}}
 eq(T.installRemembered({zone={short_name=zone},level={map=om,data={all_remembered=true}}}),0,'S5 install inert in '..zone)
end

-- Scene 1: Valley of the Moon. Mountain rim, grass, trees, poisoned lake,
-- a moonstone and a Fearscape portal; the rules never change.
local vplan={
 '#####',
 '#.T&#',
 '#~~M#',
 '#~~.#'}
local vsym={['#']='MOUNTAIN_WALL3',['.']='GRASS',T='TREE12',['&']='PORTAL_DEMON',['~']='POISON_DEEP_WATER2',M='MOONSTONE4'}
local vm=townMap(5,4,function(x,y) return vDefs[vsym[vplan[y+1]:sub(x+1,x+1)]] end)
local vRules={}
for x=0,4 do for y=0,3 do local r={};for key,v in pairs(vm(x,y,1)) do r[key]=v end;vRules[x+y*5]=r end end
local vh={zone={short_name='valley-moon'},level={map=vm,data={}}}
env.game={zone=vh.zone};mode='refined';T.apply(vh)
eq(vh.checker_mode,'refined','S5 valley refined mode')
local function vi(x,y) return vm(x,y,1).replace_display and vm(x,y,1).replace_display.image end
eq(vi(0,0),'checker-revised+refined/caldera/wall-6-0.png','S5 valley mountain corner (E,S) Caldera wall')
eq(vi(2,0),'checker-revised+refined/caldera/wall-10-0.png','S5 valley mountain rim (E,W)')
eq(vi(0,2),'checker-revised+refined/caldera/wall-5-0.png','S5 valley mountain side (N,S)')
eq(vi(1,1),'checker-revised+refined/grass0.png','S5 valley grass is forest grass')
eq(vi(2,1):match('^checker%-revised%+refined/tree%-[%a]+1%.png$')~=nil,true,'S5 valley tree is a forest tree')
eq(vi(1,2),'checker-revised+refined/caldera/poison-6-1.png','S5 valley poisoned lake corner (E,S)')
eq(vi(2,3),'checker-revised+refined/caldera/poison-9-1.png','S5 valley poisoned lake (N,W)')
eq(vi(3,1),'checker-revised+refined/grass0.png','S5 valley portal floor is board grass')
local pl=vm(3,1,1).replace_display.add_displays
eq(pl and #pl==1 and pl[1].image,'terrain/demon_portal3.png','S5 valley portal keeps its native layer')
eq(pl[1].z,5,'S5 valley portal layer native depth')
eq(vi(3,2),'checker-revised+refined/grass1.png','S5 valley moonstone floor is board grass')
local ml=vm(3,2,1).replace_display.add_displays
eq(ml and #ml==1 and ml[1].image,'terrain/moonstone_04.png','S5 valley moonstone keeps its native stone')
eq(ml[1].display_h..','..ml[1].display_y,'2,-1','S5 valley moonstone native size and offset')
eq(vi(3,3),'checker-revised+refined/grass0.png','S5 valley grass beside the stone')
for x=0,4 do for y=0,3 do
 for key,v in pairs(vRules[x+y*5]) do if key~='replace_display' and key~='_checker_terrain' then eq(vm(x,y,1)[key],v,'S5 valley rule field '..tostring(key)) end end
end end
eq(next(vm._checker_korpul or {}),nil,'S5 valley has no stone records')
mode='blockout';T.apply(vh)
eq(vi(3,2),'checker-revised+tree1.png','S5 blockout moonstone reads as blocking')
eq(vi(3,1),'checker-revised+grass0.png','S5 blockout portal reads as passable')
eq(vi(1,2),'checker-revised+water1.png','S5 blockout poison reads as water')
mode='vanilla';T.apply(vh)
for x=0,4 do for y=0,3 do eq(vm(x,y,1).replace_display,nil,'S5 native mode restores the valley '..x..','..y) end end
mode='refined';T.apply(vh)
eq(vi(0,0),'checker-revised+refined/caldera/wall-6-0.png','S5 refined restore valley wall')
eq(vm(3,2,1).replace_display.add_displays[1].image,'terrain/moonstone_04.png','S5 refined restore moonstone')
-- Old save: an unstamped moonstone/portal stays native beside board grass.
local vo=townMap(3,1,function(x) local g=deep(vDefs[({'MOONSTONE1','PORTAL_DEMON','GRASS'})[x+1]]);if x<2 then g._checker_zone_source=nil end;return g end)
T.apply({zone={short_name='valley-moon'},level={map=vo,data={}}})
eq(vo(0,0,1).replace_display,nil,'S5 old-save moonstone stays native')
eq(vo(1,0,1).replace_display,nil,'S5 old-save portal stays native')
eq(vo(2,0,1).replace_display.image,'checker-revised+refined/grass0.png','S5 old-save valley grass (general stamp) is board')
-- The valley's own fell auras (zones/valley-moon/events.lua, 100%) run over
-- grass, a tree, the poisoned lake, the mountain and a moonstone: every ring
-- cell keeps its family art under the aura mask; the moonstone keeps its prop.
m=scene(7,7,function(x,y) return x==0 and vDefs.MOUNTAIN_WALL2 or (x==3 and y==3) and vDefs.MOONSTONE6 or
 (x==5 and y==3) and vDefs.TREE4 or y==5 and vDefs.POISON_DEEP_WATER3 or vDefs.GRASS end)
local mooned=m(3,3,1)
runEvent('fell-aura',m,3,3)
eq(T.batch4Kind(m(3,4,1),'valley-moon'),'grass','S5 ring grass is valley grass')
eq(T.batch4Kind(m(3,3,1),'valley-moon'),'moonstone','S5 ring moonstone is still a moonstone')
eq(m(3,3,1).on_stand~=nil,true,'S5 the aura reached the moonstone')
local vr=host({short_name='valley-moon'},m)
T.apply(vr)
eq(m(3,4,1).replace_display.image,'checker-revised+refined/grass1.png','S5 ring grass painted')
eq(m(3,4,1).replace_display.add_displays[1].image,mask('fell-aura'),'S5 ring grass carries the aura mask')
local rs=m(3,3,1).replace_display.add_displays
eq(rs[1].image..'|'..rs[2].image,mask('fell-aura')..'|terrain/moonstone_06.png','S5 ring moonstone: aura mask then native stone')
eq(m(5,3,1).replace_display.image:match('/tree%-')~=nil,true,'S5 ring tree painted')
eq(m(3,5,1).replace_display.image:match('/caldera/poison%-')~=nil,true,'S5 ring poison painted')
eq(m(0,3,1).replace_display.image:match('/caldera/wall%-')~=nil,true,'S5 ring mountain painted')
eq(mooned.on_stand,nil,'S5 the aura event cloned the grid (source definition untouched)')

-- Scene 2: Ring of Blood arena (L3, all_remembered): hard walls, floor, lava
-- pits (both kinds join one mask), sand, the stairs and the control orb.
local rplan={
 '##..#',
 '#~~&.',
 '.~--O',
 '<~&-.'}
local rsym={['#']='HARDWALL',['.']='FLOOR',['~']='LAVA_WALL',['&']='LAVA_WALL_OPAQUE',['-']='SAND',O='CONTROL_ORB',['<']='UP'}
local rm=townMap(5,4,function(x,y) return rDefs[rsym[rplan[y+1]:sub(x+1,x+1)]] end)
local orb=rm(4,2,1)
local orbRules={};for key,v in pairs(orb) do orbRules[key]=v end
env.game={zone={short_name='ring-of-blood'}}
local rh={zone={short_name='ring-of-blood'},level={map=rm,data={all_remembered=true}}}
mode='refined';T.apply(rh)
local function ri(x,y) return rm(x,y,1).replace_display and rm(x,y,1).replace_display.image end
eq(ri(1,1),'checker-revised+refined/burnt/lava-6-0.png','S5 Ring lava corner (E,S) joins the opaque pit')
eq(ri(3,1),'checker-revised+refined/burnt/lava-8-0.png','S5 Ring opaque pit (W)')
eq(ri(2,3),'checker-revised+refined/burnt/lava-8-1.png','S5 Ring opaque pit (W) bottom row')
eq(ri(2,2),'checker-revised+refined/beach/sand0.png','S5 Ring sand is beach sand')
eq(ri(4,2),nil,'S5 Ring control orb stays native')
eq(rm(4,2,1),orb,'S5 Ring control orb grid is the same object')
for key,v in pairs(orbRules) do eq(orb[key],v,'S5 Ring control orb field '..tostring(key)) end
eq(ri(0,0),nil,'S5 Ring hard wall is stone, not forest')
eq(T.render(rm,0,0,rm(0,0,1),'refined').image,T.assetPath('hardwall',nil,6,0,0,0),'S5 Ring remembered wall installed (E,S)')
eq(T.render(rm,2,0,rm(2,0,1),'refined').image,T.assetPath('floor',nil,0,0,2,0),'S5 Ring remembered floor installed')
local ru=T.render(rm,0,3,rm(0,3,1),'refined')
eq(ru and ru.add_mos and ru.add_mos[1].image,'checker-revised+refined/korpul/stairs-up.png','S5 Ring up stairs keep the board stair overlay')
eq(rm._checker_korpul[4+2*5],nil,'S5 Ring control orb gets no stone record')
mode='vanilla';T.apply(rh)
eq(ri(1,1),nil,'S5 Ring native mode restores lava')
eq(T.render(rm,0,0,rm(0,0,1),'vanilla').image,rDefs.HARDWALL.image,'S5 Ring native mode restores the wall snapshot')
mode='refined';T.apply(rh)
eq(ri(1,1),'checker-revised+refined/burnt/lava-6-0.png','S5 Ring refined restore lava')

-- Scene 3: Tannen's Tower L1 corner: a lever door and lever stay native; the
-- reversed stairs, walls, floor and grove are board.
local tplan={
 'XX*<X',
 'X..&X',
 'X,T~X'}
local tsym={X='HARDWALL',['*']='GENERIC_LEVER_DOOR_HORIZ',['<']='TUP',['.']='FLOOR',['&']='GENERIC_LEVER',[',']='GRASS',T='TREE3',['~']='DEEP_WATER'}
local tm2=townMap(5,3,function(x,y) return tDefs[tsym[tplan[y+1]:sub(x+1,x+1)]] end)
for x=0,4 do for y=0,2 do tm2.seen[x+y*5]=true end end
local lever=tm2(3,1,1)
env.game={zone={short_name='tannen-tower'}}
local th2={zone={short_name='tannen-tower'},level={map=tm2,data={}}}
mode='refined';T.apply(th2)
for x=0,4 do for y=0,2 do T.observe(tm2,x,y,tm2(x,y,1)) end end
local function tr2(x,y) local d=T.render(tm2,x,y,tm2(x,y,1),'refined');return d and d.image end
eq(tr2(2,0),nil,'S5 Tannen lever door stays native')
eq(tr2(3,1),nil,'S5 Tannen lever stays native')
eq(tm2(3,1,1),lever,'S5 Tannen lever grid untouched')
eq(tm2._checker_korpul[2],nil,'S5 Tannen lever door gets no record')
local tu=T.render(tm2,3,0,tm2(3,0,1),'refined')
eq(tu and tu.add_mos and tu.add_mos[1].image,'checker-revised+refined/korpul/stairs-up.png','S5 Tannen TUP drawn as board up stairs')
eq(tm2(3,0,1).change_level,1,'S5 Tannen TUP still leads up (change_level +1)')
eq(tr2(1,1),T.assetPath('floor',nil,0,0,1,1),'S5 Tannen floor')
eq(tm2(1,2,1).replace_display.image,'checker-revised+refined/grass1.png','S5 Tannen grove grass')
eq(tm2(2,2,1).replace_display.image:match('/tree%-')~=nil,true,'S5 Tannen grove tree')
eq(tm2(3,2,1).replace_display.image:match('^checker%-revised%+refined/deep')~=nil,true,'S5 Tannen pool water')
eq(tm2(0,0,1).replace_display,nil,'S5 Tannen wall is stone only')

-- Scene 4: Derth's southeast arena: grass fringe on the walls, sand pit,
-- lever-door gate native.
local uplan={
 ':T:+:',
 ':###:',
 ':#..-'}
local usym={[':']='GRASS',T='TREE6',['+']='GENERIC_LEVER_DOOR',['#']='HARDWALL',['.']='SAND',['-']='FLOOR'}
local um=townMap(5,3,function(x,y) return uDefs[usym[uplan[y+1]:sub(x+1,x+1)]] end)
env.game={zone={short_name='arena-unlock'}}
local uh={zone={short_name='arena-unlock'},level={map=um,data={all_remembered=true}}}
mode='refined';T.apply(uh)
local function ui(x,y) return um(x,y,1).replace_display and um(x,y,1).replace_display.image end
eq(ui(0,0),'checker-revised+refined/grass0.png','S5 arena grass')
eq(ui(1,0):match('/tree%-')~=nil,true,'S5 arena tree')
eq(ui(2,2),'checker-revised+refined/beach/sand0.png','S5 arena sand pit')
eq(ui(3,0),nil,'S5 arena lever-door gate stays native')
eq(T.render(um,3,0,um(3,0,1),'refined'),nil,'S5 arena lever-door gate has no stone record')
eq(T.render(um,2,1,um(2,1,1),'refined').image,T.assetPath('hardwall',nil,10,1,2,1),'S5 arena remembered wall installed (E,W)')
eq(T.render(um,4,2,um(4,2,1),'refined').image,T.assetPath('floor',nil,0,0,4,2),'S5 arena floor')

-- Scene 5: Dreadfell ambush glade, then the quest's direct exit placement:
-- native until a repair of the level (Game.lua runs it once per level).
local am=townMap(3,2,function(x,y) return y==0 and aDefs.TREE11 or aDefs.GRASS end)
local ah={zone={short_name='dreadfell-ambush'},level={map=am,data={}}}
env.game={zone=ah.zone};mode='refined';T.apply(ah)
eq(am(1,1,1).replace_display.image,'checker-revised+refined/grass0.png','S5 ambush glade grass')
eq(am(1,0,1).replace_display.image:match('/tree%-')~=nil,true,'S5 ambush tree')
am(1,1,1,aDefs.GRASS_UP_WILDERNESS)
eq(am(1,1,1).replace_display,nil,'S5 direct quest exit set is native until repaired')
am.updateMap=function() end
T.repair(ah,0,0,2,1)
eq(am(1,1,1).replace_display.image,'checker-revised+refined/exit0.png','S5 ambush quest exit painted after repair')
eq(am(1,1,1).change_zone..am(1,1,1).change_level,'wilderness1','S5 ambush exit transition untouched')
eq(aDefs.GRASS_UP_WILDERNESS.replace_display,nil,'S5 ambush shared exit prototype never painted')

-- Other zones and families: S5 identities never leak, earlier families unchanged.
for _,zone in ipairs{'noxious-caldera','town-zigur','trollmire','gorbat-pride'} do
 local oz={zone={short_name=zone},level={map=townMap(4,1,function(x) return ({vDefs.MOONSTONE2,vDefs.PORTAL_DEMON,rDefs.LAVA_WALL,rDefs.LAVA_WALL_OPAQUE})[x+1] end),data={}}}
 env.game={zone=oz.zone}
 T.apply(oz)
 for x=0,3 do eq(oz.level.map(x,0,1).replace_display,nil,'S5 zone-local identity stays native in '..zone..' '..x) end
end
local cz2={zone={short_name='noxious-caldera'},level={map=townMap(2,1,function(x) return ({vDefs.POISON_DEEP_WATER2,vDefs.MOUNTAIN_WALL2})[x+1] end),data={}}}
env.game={zone=cz2.zone};T.apply(cz2)
eq(cz2.level.map(0,0,1).replace_display.image,'checker-revised+refined/caldera/poison-0-0.png','S5 Caldera poison unchanged')
eq(cz2.level.map(1,0,1).replace_display.image,'checker-revised+refined/caldera/wall-0-1.png','S5 Caldera mountain unchanged')
eq(T.batch4Kind(methods.clone(vDefs.GRASS),'caldera'),nil,'S5 Caldera still does not claim forest grass')
env.game={zone={short_name='dreadfell'}}
eq(T.classify(methods.clone(cDefs.HARDWALL)),'hardwall','S5 Dreadfell stone unchanged')
end)()
-- S2: exits, callback-free doors and static props inside covered zones.
-- Zone lists are loaded like Grid:loadList (nested stamped, then the outer
-- list). Only each file's own reviewed ids get the S2 stamp; every rule field,
-- layer, callback line and lore of the placed grid must equal the native
-- definition; one changed field keeps the cell native. Old saves (no stamp)
-- keep native.
;(function()
local savedStairs=T.stairAssets
T.stairAssets={ready=true,files=setmetatable({},{__index=function(_,k) return type(k)=='string' and k:match('^checker%-revised%+refined/korpul/stairs%-') and true or nil end})}
local F={}
for _,z in ipairs{'reknor-escape','deep-bellow','maze','ancient-elven-ruins','south-beach','crypt-kryl-feijan',
 'last-hope-graveyard','dreadfell','reknor','ruined-dungeon','keepsake-meadow','trollmire'} do F[z]=loadDefs('/data/zones/'..z..'/grids.lua') end
local forestDefs=loadDefs('/data/general/grids/forest.lua')
-- Stamps: own reviewed ids only; nested and other ids have none.
local own={['reknor-escape']={'IRON_COUNCIL'},['deep-bellow']={'IRON_COUNCIL'},maze={'QUICK_EXIT'},['ancient-elven-ruins']={'QUICK_EXIT'},
 ['south-beach']={'BEACH_UP'},['crypt-kryl-feijan']={'LOCK','LOCK_HORIZ','LOCK_VERT','PENTAGRAM'},
 ['last-hope-graveyard']={'ALTAR'},dreadfell={'LORE_NOTE'},reknor={'IRON_THRONE_EDICT'},['ruined-dungeon']={'LORE1','LORE2','LORE3','LORE4'},
 ['keepsake-meadow']={'CAVE_DOOR','CAVE_DOOR_OPEN','CAVE_DOOR_HORIZ','CAVE_DOOR_HORIZ_OPEN','CAVE_DOOR_VERT','CAVE_DOOR_OPEN_VERT','CAVEFLOOR_CAVE_MARKER'},
 trollmire={'STEW'}}
for z,ids in pairs(own) do
 for _,id in ipairs(ids) do eq(F[z][id]._checker_s2_source.file,'/data/zones/'..z..'/grids.lua','S2 stamp '..z..' '..id) end
 for id,g in pairs(F[z]) do
  local listed=false;for _,o in ipairs(ids) do if o==id then listed=true end end
  if not listed then eq(g._checker_s2_source and g._checker_s2_source.file=='/data/zones/'..z..'/grids.lua' or false,false,'S2 no zone stamp on unreviewed '..z..' '..id) end
 end
end
eq(forestDefs.ROCK_VAULT._checker_s2_source.file,'/data/general/grids/forest.lua','S2 forest.lua stamps ROCK_VAULT')
eq(F.trollmire.ROCK_VAULT._checker_s2_source.file,'/data/general/grids/forest.lua','S2 nested forest.lua keeps its ROCK_VAULT stamp')
eq(F['keepsake-meadow'].STEW._checker_s2_source,nil,'S2 Keepsake stew keeps its own (earlier) contract')
eq(F.dreadfell.FLOOR._checker_grid_source.file,'/data/general/grids/basic.lua','S2 nested basic stamp survives the outer list')
-- Stone positives.
local stone={
 {'reknor-escape','IRON_COUNCIL','stairs-down'},{'maze','QUICK_EXIT','prop','terrain/maze_teleport.png'},
 {'ancient-elven-ruins','QUICK_EXIT','prop','terrain/maze_teleport.png'},
 {'crypt-kryl-feijan','LOCK','lock'},{'crypt-kryl-feijan','LOCK_HORIZ','lock','horizontal'},{'crypt-kryl-feijan','LOCK_VERT','lock','vertical'},
 {'crypt-kryl-feijan','PENTAGRAM','prop','terrain/floor_pentagram.png'},
 {'last-hope-graveyard','ALTAR','prop','terrain/floor_pentagram.png'},{'reknor','IRON_THRONE_EDICT','prop','terrain/signpost.png'},
 {'ruined-dungeon','LORE1','prop','terrain/signpost.png'},{'ruined-dungeon','LORE3','prop','terrain/signpost.png'},
 {'ruined-dungeon','LORE4','prop','terrain/signpost.png'},
}
local function stoneKind(z,g)
 env.game={zone={short_name=z}}
 return T.classify(g)
end
local function dreadNote(lore) local g=methods.clone(F.dreadfell.LORE_NOTE);g.lore=lore;return g end
for _,c in ipairs(stone) do
 local k,o=stoneKind(c[1],methods.clone(F[c[1]][c[2]]))
 eq(k,c[3],'S2 exact stone '..c[1]..' '..c[2])
 if c[3]=='prop' then eq(o.image,c[4],'S2 prop layer '..c[2]) elseif c[3]=='lock' then eq(o,c[4],'S2 lock orientation '..c[2]) end
 for _,other in ipairs{'dreadfell','ruins-kor-pul','halfling-ruins','crypt-kryl-feijan','maze','reknor'} do
  if other~=c[1] then eq(stoneKind(other,methods.clone(F[c[1]][c[2]])),nil,'S2 '..c[2]..' of '..c[1]..' not claimed in '..other) end
 end
end
eq(stoneKind('dreadfell',dreadNote('dreadfell-note-3')),'prop','S2 Dreadfell lore note with its zone.lua lore')
eq(stoneKind('dreadfell',dreadNote('dreadfell-poem-master')),'prop','S2 Dreadfell L3 master poem note (zone.lua:88)')
eq(stoneKind('dreadfell',dreadNote('dreadfell-poem-master2')),nil,'S2 Dreadfell note lore is exact')
eq(stoneKind('dreadfell',dreadNote('other-lore')),nil,'S2 Dreadfell note with a foreign lore stays native')
eq(stoneKind('dreadfell',methods.clone(F.dreadfell.LORE_NOTE)),nil,'S2 Dreadfell note without lore stays native')
local alt=deep(F['ruined-dungeon'].LORE2);alt.lore='alt1-infinite-dungeon-2';alt._checker_s2_source.lore='alt1-infinite-dungeon-2'
eq(stoneKind('ruined-dungeon',alt),'prop','S2 Ruined Dungeon ALT1 clue post')
alt=deep(F['ruined-dungeon'].LORE2);alt.lore='alt1-infinite-dungeon-2'
eq(stoneKind('ruined-dungeon',alt),nil,'S2 lore changed after load stays native')
-- Rule-field, layer, callback, stamp and zone negatives (one change each).
local flips={type='wall',subtype='other',name='other',image='terrain/other.png',display='x',does_block_move='flip',block_sight='flip',
 block_sense='flip',block_esp='flip',air_level=-3,dig='FLOOR',grow='WALL',is_door='flip',door_opened='DOOR_OPEN',door_closed='DOOR',
 can_pass={pass_wall=1},z=7,shader='water',notice='flip',always_remember='flip',pass_projectile='flip',show_tooltip='flip',
 glow='flip',special='flip',orb_portal={},lever='flip',special_minimap={r=1,g=2,b=3},on_stand_safe='flip',display_x=1,display_y=1,
 change_level=9,change_zone='other-zone',change_level_abs='flip',keep_old_lev='flip',force_down='flip',
 change_zone_auto_stairs='flip',change_level_auto_stairs='flip',change_level_shift_back='flip'}
local function mutants(g)
 local out={}
 for k,v in pairs(flips) do
  local c=deep(g)
  if v=='flip' then c[k]=not c[k] and true or nil elseif c[k]==v then c[k]=type(v)=='string' and v..'2' or v+1 else c[k]=v end
  if k=='z' and g.z==7 then c.z=nil end
  out[#out+1]={k,c}
 end
 local c=deep(g);c._checker_s2_source=nil;out[#out+1]={'unstamped',c}
 c=deep(g);c._checker_s2_source.file='/data/zones/other/grids.lua';out[#out+1]={'foreign stamp',c}
 c=deep(g);c._checker_s2_source.id='OTHER';out[#out+1]={'stamp id',c}
 c=deep(g);c.on_stand=function() end;out[#out+1]={'on_stand',c}
 c=deep(g);c.block_move=function() return true end;out[#out+1]={'block_move',c}
 c=deep(g);c.on_move=function() end;out[#out+1]={'on_move',c}
 c=deep(g);c.change_level_check=function() end;out[#out+1]={'change_level_check',c}
 c=deep(g);c.door_player_check='Prompt.';out[#out+1]={'prompt',c}
 c=deep(g);c.tint_r=0.5;out[#out+1]={'tint',c}
 c=deep(g);c.add_mos=c.add_mos or {};c.add_mos[#c.add_mos+1]={image='terrain/foreign.png'};out[#out+1]={'extra mos',c}
 c=deep(g);c.add_displays=c.add_displays or {};c.add_displays[#c.add_displays+1]=setmetatable({image='terrain/foreign.png'},meta);out[#out+1]={'extra layer',c}
 if g.add_mos then c=deep(g);c.add_mos[1].image='terrain/foreign.png';out[#out+1]={'mos image',c} end
 if g.add_displays then
  c=deep(g);c.add_displays[1].image='terrain/foreign.png';out[#out+1]={'layer image',c}
  c=deep(g);c.add_displays[1].z=(g.add_displays[1].z or 0)+1;out[#out+1]={'layer z',c}
  c=deep(g);c.add_displays[1].display_x=0.5;out[#out+1]={'layer offset',c}
 end
 if g.lore then c=deep(g);c.lore=g.lore..'x';out[#out+1]={'lore',c} end
 return out
end
local function rejected(label,list,kind)
 for _,m in ipairs(list) do eq(kind(m[2]),nil,label..' altered '..m[1]) end
end
for _,c in ipairs(stone) do
 rejected('S2 '..c[1]..' '..c[2],mutants(F[c[1]][c[2]]),function(g) return (stoneKind(c[1],g)) end)
end
rejected('S2 dreadfell LORE_NOTE',mutants(dreadNote('dreadfell-note-1')),function(g) return (stoneKind('dreadfell',g)) end)
-- A changed source definition cannot widen the contract (the spec is native).
for _,c in ipairs(stone) do
 local g=deep(F[c[1]][c[2]]);g._checker_s2_source=nil;g.name='other'
 T.markSource(g,'/data/zones/'..c[1]..'/grids.lua')
 eq(stoneKind(c[1],g),nil,'S2 changed definition '..c[2]..' is not the reviewed native one')
end
-- Rel tunnel: Halfling L4's map-file quickEntity with its native yeek check.
local rqe={}
do
 local chunk=assert(loadstring(readFile(data..'/maps/zones/halfling-ruins-last.lua'),'@/data/maps/zones/halfling-ruins-last.lua'))
 setfenv(chunk,setmetatable({colors=colors,_t=function(s) return s end,mod={class={Grid={new=function(t) return setmetatable(t,meta) end}}},
  quickEntity=function(c,e) rqe[c]=setmetatable(e,meta) end},{__index=function(_,k) return _G[k] or function() end end}))
 chunk()
end
eq(stoneKind('halfling-ruins',methods.clone(rqe['>'])),'stairs-down','S2 Rel tunnel (quickEntity, native check line 31)')
eq(stoneKind('dreadfell',methods.clone(rqe['>'])),nil,'S2 Rel tunnel is Halfling only')
for label,m in pairs{check=function(g) g.change_level_check=function() end end,zone=function(g) g.change_zone='other' end,
 level=function(g) g.change_level=2 end,move=function(g) g.does_block_move=true end,layer=function(g) g.add_displays[1].image='terrain/stair_up.png' end,
 extra=function(g) g.add_mos={{image='terrain/stair_down.png'}} end,id=function(g) g.define_as='REL' end,image=function(g) g.image='terrain/grass.png' end,
 notice=function(g) g.notice=nil end,auto=function(g) g.change_zone_auto_stairs=true end,stand=function(g) g.on_stand=function() end end} do
 local g=deep(rqe['>']);m(g)
 eq(stoneKind('halfling-ruins',g),nil,'S2 altered Rel tunnel '..label)
end
-- Forest and batch positives: South Beach exit, Keepsake cave doors and
-- marker, Trollmire stew, forest.lua vault rock, Deep Bellow's Iron Council.
env.game={zone={short_name='south-beach'}}
eq(T.batch4Kind(methods.clone(F['south-beach'].BEACH_UP),'beach'),'exit','S2 South Beach world exit (native check line 49)')
eq(T.batch4Kind(methods.clone(F['south-beach'].BEACH_UP),'meadow'),nil,'S2 BEACH_UP is beach only')
rejected('S2 BEACH_UP',mutants(F['south-beach'].BEACH_UP),function(g) return T.batch4Kind(g,'beach') end)
for id,k in pairs{CAVE_DOOR='cave-door-closed-horizontal',CAVE_DOOR_OPEN='cave-door-open-horizontal',CAVE_DOOR_HORIZ='cave-door-closed-horizontal',
 CAVE_DOOR_HORIZ_OPEN='cave-door-open-horizontal',CAVE_DOOR_VERT='cave-door-closed-vertical',CAVE_DOOR_OPEN_VERT='cave-door-open-vertical',
 CAVEFLOOR_CAVE_MARKER='cave-marker'} do
 eq(T.batch4Kind(methods.clone(F['keepsake-meadow'][id]),'meadow'),k,'S2 Keepsake '..id)
 eq(T.batch4Kind(methods.clone(F['keepsake-meadow'][id]),'beach'),nil,'S2 Keepsake '..id..' meadow only')
 rejected('S2 Keepsake '..id,mutants(F['keepsake-meadow'][id]),function(g) return T.batch4Kind(g,'meadow') end)
end
-- Forest path scene: Trollmire grass, stew (with a native grass border) and
-- a loose vault rock (prop); Old Forest takes the rock too; nowhere else.
local function forestScene(zone,defs,extra)
 local fm=townMap(3,1,function(x) return ({defs.GRASS,defs.STEW or F.trollmire.STEW,defs.ROCK_VAULT})[x+1] end)
 if extra then extra(fm) end
 local fh={zone={short_name=zone,is_crystaline=false,is_flooded=false},level={map=fm,data={},level=3}}
 env.game={zone=fh.zone};mode='refined';T.apply(fh)
 local function im(x) local d=fm(x,0,1).replace_display;return d and d.image,d and d.add_displays end
 return im,fm,fh
end
local im,fm,fh=forestScene('trollmire',F.trollmire,function(m)
 local s=m(1,0,1);s.add_displays={setmetatable({image='invis.png',add_mos={{image='terrain/grass/grass_2_01.png',display_y=-1}}},meta)}
end)
eq(im(0),'checker-revised+refined/grass0.png','S2 Trollmire grass unchanged')
eq(im(1),'checker-revised+refined/keepsake/stew1.png','S2/T24 Trollmire stew (grass-bordered) uses the Keepsake stew art')
local rockImage,rockLayers=im(2)
eq(rockImage,'checker-revised+refined/grass0.png','S2/T4 vault rock board grass')
eq(rockLayers and rockLayers[#rockLayers].image,'terrain/huge_rock.png','S2/T4 vault rock keeps the native rock')
eq(fm(2,0,1).is_door==true and fm(2,0,1).door_opened=='GRASS' and fm(2,0,1).block_sight==true,true,'S2 vault rock rules untouched')
mode='vanilla';T.apply(fh)
for x=0,2 do eq(fm(x,0,1).replace_display,nil,'S2 Trollmire vanilla restore '..x) end
mode='blockout';T.apply(fh)
eq(im(1),'checker-revised+tree1.png','S2 stew blocks in blockout')
eq(im(2),'checker-revised+tree0.png','S2 vault rock blocks in blockout')
mode='refined'
im=forestScene('old-forest',F.trollmire)
eq(im(2),'checker-revised+refined/grass0.png','S2/T4 Old Forest vault rock')
eq(im(1),nil,'S2 Trollmire stew is Trollmire only (Old Forest)')
for _,z in ipairs{'slazish-fen','lake-nur','rhaloren-camp'} do
 im=forestScene(z,F.trollmire)
 eq(im(1),nil,'S2 Trollmire stew native in '..z)
end
-- (A grass-subtype mutant with a transition is the legacy forest exit kind;
-- the S2 art itself -- stew tile, redrawn rock -- must be gone.)
rejected('S2 Trollmire STEW',mutants(F.trollmire.STEW),function(g)
 local m=townMap(1,1,function() return g end);local h={zone={short_name='trollmire'},level={map=m,data={},level=3}}
 env.game={zone=h.zone};T.apply(h);local d=m(0,0,1).replace_display
 return d and d.image:match('/keepsake/stew') and d or nil end)
rejected('S2 ROCK_VAULT',mutants(forestDefs.ROCK_VAULT),function(g)
 local m=townMap(1,1,function() return g end);local h={zone={short_name='trollmire'},level={map=m,data={},level=3}}
 env.game={zone=h.zone};T.apply(h);local d=m(0,0,1).replace_display
 return d and d.add_displays and d.add_displays[#d.add_displays].image=='terrain/huge_rock.png' and d or nil end)
local badBorder=methods.clone(forestDefs.ROCK_VAULT);badBorder.add_displays={setmetatable({image='invis.png',add_mos={{image='terrain/sand/sand_2_1.png'}}},meta)}
eq(T.forestKind(badBorder),nil,'S2 vault rock is not a plain forest kind')
local bm=townMap(1,1,function() return badBorder end);local bh={zone={short_name='trollmire'},level={map=bm,data={},level=3}}
env.game={zone=bh.zone};T.apply(bh);eq(bm(0,0,1).replace_display,nil,'S2 vault rock with a foreign border stays native')
-- Keepsake scene: cave walls round a horizontal door, the marker post.
local kd=F['keepsake-meadow']
local km=townMap(4,1,function(x) return ({kd.CAVEWALL,kd.CAVE_DOOR_HORIZ,kd.CAVEWALL,kd.CAVEFLOOR_CAVE_MARKER})[x+1] end)
local kh={zone={short_name='keepsake-meadow'},level={map=km,data={},level=3}}
env.game={zone=kh.zone};mode='refined';T.apply(kh)
eq(km(1,0,1).replace_display.image,'checker-revised+refined/cave/door-closed-horizontal1.png','S2/T7 cave door board art')
eq(km(0,0,1).replace_display.image:match('/cave/wall%-')~=nil,true,'S2 cave wall beside the door')
eq(km(3,0,1).replace_display.image,'checker-revised+refined/cave/floor1.png','S2/T14 cave marker board floor')
local kl=km(3,0,1).replace_display.add_displays
eq(kl and kl[#kl].image,'terrain/signpost.png','S2/T14 cave marker keeps the native post')
km(1,0,1,methods.clone(kd.CAVE_DOOR_HORIZ_OPEN));km.updateMap=function() end
T.repair(kh,0,0,3,0)
eq(km(1,0,1).replace_display.image,'checker-revised+refined/cave/door-open-horizontal1.png','S2/T7 opened cave door repainted')
eq(km(1,0,1).door_closed,'CAVE_DOOR_HORIZ','S2 cave door rule untouched')
-- Deep Bellow's Iron Council exit on the plain gloom suite.
local dbm=townMap(1,1,function() return F['deep-bellow'].IRON_COUNCIL end)
local dbh={zone={short_name='deep-bellow'},level={map=dbm,data={},level=1}}
env.game={zone=dbh.zone};T.apply(dbh)
eq(dbm(0,0,1).replace_display.image,'checker-revised+refined/gloom/plain/ladder-up0.png','S2/T10 Deep Bellow Iron Council exit')
eq(dbm(0,0,1).change_zone..dbm(0,0,1).change_level,'town-iron-council1','S2 Iron Council exit target untouched')
rejected('S2 deep-bellow IRON_COUNCIL',mutants(F['deep-bellow'].IRON_COUNCIL),function(g)
 local m=townMap(1,1,function() return g end);local h={zone={short_name='deep-bellow'},level={map=m,data={},level=1}}
 env.game={zone=h.zone};T.apply(h);return m(0,0,1).replace_display end)
local om=townMap(1,1,function() return F['reknor-escape'].IRON_COUNCIL end)
local oh={zone={short_name='deep-bellow'},level={map=om,data={},level=1}}
env.game={zone=oh.zone};T.apply(oh);eq(om(0,0,1).replace_display,nil,'S2 the Reknor-escape copy is not Deep Bellow\'s exit')
-- Stone scene: Kryl-Feijan L5 walls round a padlocked horizontal lock, a
-- demonic symbol and floor; the Derth arena gate between north/south walls.
local kf=F['crypt-kryl-feijan']
local lm=townMap(3,2,function(x,y) return y==1 and ({kf.PENTAGRAM,kf.FLOOR,kf.FLOOR})[x+1] or ({kf.WALL,kf.LOCK_HORIZ,kf.WALL})[x+1] end)
for i=0,5 do lm.seen[i]=true end
env.game={zone={short_name='crypt-kryl-feijan'}}
for x=0,2 do for y=0,1 do T.observe(lm,x,y,lm(x,y,1)) end end
local lock=T.render(lm,1,0,lm(1,0,1),'refined')
eq(lock.image,T.assetPath('door-closed','horizontal',10,1,1,0),'S2/T6 lock is the board closed door between walls')
eq(lock.add_mos and lock.add_mos[1].image,'terrain/padlock2.png','S2/T6 lock keeps a padlock')
local sym=T.render(lm,0,1,lm(0,1,1),'refined')
eq(sym.image,T.assetPath('prop',nil,0,1,0,1),'S2/T15 symbol board floor')
eq(sym.add_displays[#sym.add_displays].image,'terrain/floor_pentagram.png','S2/T15 symbol keeps the native pentagram')
eq(T.render(lm,1,0,lm(1,0,1),'vanilla').image,'terrain/granite_door1.png','S2 lock native restore')
eq(lm(1,0,1).does_block_move==true and lm(1,0,1).block_sight==true,true,'S2 lock rules untouched')
-- An untiled Kryl-Feijan LOCK (before its door3d re-tile) between north and
-- south walls faces that wall line.
local vm2=townMap(3,3,function(x,y) return x==1 and (y==1 and kf.LOCK or kf.WALL) or kf.FLOOR end)
for i=0,8 do vm2.seen[i]=true end
env.game={zone={short_name='crypt-kryl-feijan'}}
for x=0,2 do for y=0,2 do T.observe(vm2,x,y,vm2(x,y,1)) end end
eq(T.render(vm2,1,1,vm2(1,1,1),'refined').image,T.assetPath('door-closed','vertical',5,0,1,1),'S2/T6 untiled lock faces its wall line')
-- Derth's arena LOCK is never placed by the arena map; it stays native.
env.game={zone={short_name='arena-unlock'}}
eq(T.classify(methods.clone(loadDefs('/data/zones/arena-unlock/grids.lua').LOCK)),nil,'S2 unplaced arena LOCK stays native')
-- A lore post inside an exact native fell-aura ring (event file and line)
-- keeps its S2 identity; the ring adds the aura mask.
do
 local edict=methods.clone(F.reknor.IRON_THRONE_EDICT)
 local fn
 -- A closure with the event's chunk name defined at its native on_stand line.
 local src=readFile(data..'/general/events/fell-aura.lua')
 local line=0;for l in src:gmatch('[^\n]*\n') do line=line+1;if l:match('^local on_stand') then break end end
 fn=assert(loadstring(string.rep('\n',line-1)..'return function() end','@/data/general/events/fell-aura.lua'))()
 edict.on_stand=fn;edict.always_remember=true
 eq(stoneKind('reknor',edict),'prop','S2 lore post inside a native fell-aura ring')
 local foreign=methods.clone(F.reknor.IRON_THRONE_EDICT);foreign.on_stand=function() end
 eq(stoneKind('reknor',foreign),nil,'S2 lore post with a foreign on_stand stays native')
end
-- Halfling FLAT exits and the Rel tunnel get the stair overlays.
local hd=loadDefs('/data/zones/halfling-ruins/grids.lua')
local hm=townMap(3,1,function(x) return ({hd.FLAT_UP_WILDERNESS,hd.FLAT_DOWN4,rqe['>']})[x+1] end)
for i=0,2 do hm.seen[i]=true end
env.game={zone={short_name='halfling-ruins'}}
for x=0,2 do T.observe(hm,x,0,hm(x,0,1)) end
eq(T.render(hm,0,0,hm(0,0,1),'refined').add_mos[1].image,'checker-revised+refined/korpul/stairs-world.png','S2/T8 flat world exit overlay')
eq(T.render(hm,1,0,hm(1,0,1),'refined').add_mos[1].image,'checker-revised+refined/korpul/stairs-down.png','S2/T8 flat down exit overlay')
eq(T.render(hm,2,0,hm(2,0,1),'refined').add_mos[1].image,'checker-revised+refined/korpul/stairs-down.png','S2/T10 Rel tunnel overlay')
eq(hm(1,0,1).change_level,1,'S2 flat exit target untouched')
-- A placed copy the engine flagged force_clone (room generator) is the same grid.
local fc=methods.clone(F.trollmire.STEW);fc.force_clone=true
local fcm=townMap(1,1,function() return fc end);local fch={zone={short_name='trollmire'},level={map=fcm,data={},level=3}}
env.game={zone=fch.zone};T.apply(fch)
eq(fcm(0,0,1).replace_display.image:match('/keepsake/stew')~=nil,true,'S2 force_clone placed stew')
-- Old save: an S2 id without its stamp keeps native on every path.
for _,c in ipairs{{'crypt-kryl-feijan','LOCK_HORIZ'},{'dreadfell','LORE_NOTE'},{'maze','QUICK_EXIT'}} do
 local g=deep(F[c[1]][c[2]]);g._checker_s2_source=nil;g.lore=g.lore or 'dreadfell-note-1'
 eq(stoneKind(c[1],g),nil,'S2 old-save '..c[2]..' stays native')
end
local oldFlat=deep(hd.FLAT_DOWN4);oldFlat._checker_grid_source=nil
eq(stoneKind('halfling-ruins',oldFlat),nil,'S2 old-save flat exit stays native')
local oldCave=deep(kd.CAVE_DOOR_HORIZ);oldCave._checker_s2_source=nil
eq(T.batch4Kind(oldCave,'meadow'),nil,'S2 old-save cave door stays native')
-- Earlier families unchanged: Keepsake stew, plain doors, Kryl-Feijan floor.
eq(T.batch4Kind(methods.clone(kd.STEW),'meadow'),'stew','S2 Keepsake stew unchanged')
eq(stoneKind('crypt-kryl-feijan',methods.clone(kf.DOOR)),'door-closed','S2 Kryl-Feijan plain door unchanged')
eq(stoneKind('crypt-kryl-feijan',methods.clone(kf.ALTAR_BARE)),nil,'S2 Kryl-Feijan wide altar stays native (display_w=2)')
eq(stoneKind('ruined-dungeon',methods.clone(F['ruined-dungeon'].INFINITE)),nil,'S2 Ruined Dungeon infinite stair (on_move) stays native')
eq(stoneKind('ruined-dungeon',methods.clone(F['ruined-dungeon'].LOCK)),nil,'S2 Ruined Dungeon LOCK (unplaced) stays native')
eq(stoneKind('reknor',methods.clone(F.reknor.FLOOR)),'floor','S2 Reknor floor unchanged')
T.stairAssets=savedStairs
end)()
-- S4/T1: the underwater air bubble, loaded from the native water.lua with its
-- real chunk name. Exact identity = the S2 stamp/spec (every rule field, the
-- extra identity fields, the on_stand's file AND line 106) plus air_condition,
-- nb_charges and layers; any single change stays native. Its native on_stand
-- still spends charges and swaps in WATER_FLOOR; the engine Zone superload
-- repaints only that 3x3 area, and only when the terrain actually changed.
;(function()
local wd=loadDefs('/data/general/grids/water.lua')
local bubble=wd.WATER_FLOOR_BUBBLE
local src=debug.getinfo(bubble.on_stand,'S')
eq(src.source..':'..src.linedefined,'@/data/general/grids/water.lua:106','S4 native bubble on_stand is water.lua:106')
eq(rawget(bubble,'_checker_s2_source')~=nil,true,'S4 bubble definition stamped')
for id,g in pairs(wd) do if id~='WATER_FLOOR_BUBBLE' then eq(rawget(g,'_checker_s2_source'),nil,'S4 no stamp on '..id) end end
local function placed() local g=methods.clone(bubble);g.nb_charges=5;return g end
eq(T.underwaterKind(placed()),'bubble','S4 exact placed bubble')
local forced=placed();forced.force_clone=true
eq(T.underwaterKind(forced),'bubble','S4 force_clone copy is the same bubble')
local spent=placed();spent.nb_charges=0
eq(T.underwaterKind(spent),'bubble','S4 charge count is runtime state, not identity')
local function pad(line,body) return (('\n'):rep(line-1))..(body or 'return function(self,x,y,who) end') end
local neg={
 unstamped=function(g) g._checker_s2_source=nil end,
 ['foreign stamp file']=function(g) g._checker_s2_source=deep(g._checker_s2_source);g._checker_s2_source.file='/data/general/grids/basic.lua' end,
 ['same file, other line']=function(g) g.on_stand=assert(loadstring(pad(105),'@/data/general/grids/water.lua'))() end,
 ['same file, shifted line']=function(g) g.on_stand=assert(loadstring(pad(107),'@/data/general/grids/water.lua'))() end,
 ['foreign file, same line']=function(g) g.on_stand=assert(loadstring(pad(106),'@/data-foreign/general/grids/water.lua'))() end,
 ['wrapped callback']=function(g) local f=g.on_stand;g.on_stand=function(...) return f(...) end end,
 ['no callback']=function(g) g.on_stand=nil end,
 ['extra callback']=function(g) g.on_move=function() end end,
 ['aura ring callback']=function(g) g.on_stand=assert(loadstring(pad(30),'@/data/general/events/fell-aura.lua'))() end,
 name=function(g) g.name='air bubble' end, image=function(g) g.image='terrain/underwater/subsea_floor_02.png' end,
 display=function(g) g.display='.' end, air=function(g) g.air_level=5 end,
 condition=function(g) g.air_condition='water' end, tooltip=function(g) g.show_tooltip=nil end,
 desc=function(g) g.desc='Something else.' end, type=function(g) g.type='wall' end,
 subtype=function(g) g.subtype='underwater' end, move=function(g) g.does_block_move=true end,
 sight=function(g) g.block_sight=true end, remember=function(g) g.always_remember=true end,
 notice=function(g) g.notice=true end, level=function(g) g.change_level=1 end,
 dig=function(g) g.dig='WATER_FLOOR' end, special=function(g) g.special=true end,
 shader=function(g) g.shader='water' end, tint=function(g) g.tint_r=0.5 end,
 charges=function(g) g.nb_charges=nil end, mos=function(g) g.add_mos={{image='terrain/underwater/subsea_floor_bubbles.png'}} end,
 layer=function(g) g.add_displays={{image='terrain/underwater/subsea_floor_02.png'}} end,
 minimap=function(g) g.special_minimap={r=1,g=2,b=3} end, z=function(g) g.z=3 end,
 id=function(g) g.define_as='WATER_FLOOR' end,
}
for label,f in pairs(neg) do local g=placed();f(g);eq(T.underwaterKind(g),nil,'S4 altered bubble stays native: '..label) end
-- The family key 'underwater' matches no forest/batch/stone caller.
eq((T.batch4Kind(placed(),'meadow')),nil,'S4 bubble not a meadow kind')
eq(T.classify(placed()),nil,'S4 bubble not a stone kind')
-- Rendering: board floor + bubble tile in the underwater zones only.
local function scene(zone,level,flooded,g)
 local tm=townMap(3,3,function(x,y) return (x==1 and y==1) and g or wd.WATER_FLOOR end)
 tm(1,1,1,g);tm.updateMap=function() end
 local h={zone={short_name=zone,is_flooded=flooded},level={map=tm,level=level,data={}}}
 env.game={zone=h.zone,level=h.level};T.apply(h)
 return tm,h
end
mode='refined'
local tm,h=scene('lake-nur',2,nil,placed())
eq(tm(1,1,1).replace_display.image,'checker-revised+refined/underwater/bubble0.png','S4 Lake of Nur L2 board bubble')
eq(tm(0,1,1).replace_display.image,'checker-revised+refined/underwater/floor1.png','S4 neighbour board floor')
eq(tm(1,1,1).on_stand,bubble.on_stand,'S4 native on_stand kept')
eq(tm(1,1,1).air_level,15,'S4 native air rule kept')
mode='vanilla';T.apply(h);eq(tm(1,1,1).replace_display,nil,'S4 native restore')
mode='blockout';T.apply(h);eq(tm(1,1,1).replace_display.image,'checker-revised+grass0.png','S4 blockout floor')
mode='refined';T.apply(h);eq(tm(1,1,1).replace_display.image,'checker-revised+refined/underwater/bubble0.png','S4 round trip')
tm=scene('lake-nur',3,true,placed());eq(tm(1,1,1).replace_display.image,'checker-revised+refined/underwater/bubble0.png','S4 FLOODED L3 bubble')
tm=scene('lake-nur',3,false,placed());eq(tm(1,1,1).replace_display,nil,'S4 dry L3 stays native')
tm=scene('murgol-lair',1,nil,placed());eq(tm(1,1,1).replace_display.image,'checker-revised+refined/underwater/bubble0.png','S4 Murgol bubble')
tm=scene('trollmire',1,nil,placed());eq(tm(1,1,1).replace_display,nil,'S4 bubble outside underwater zones stays native')
local oldSave=placed();oldSave._checker_s2_source=nil
tm=scene('lake-nur',2,nil,oldSave);eq(tm(1,1,1).replace_display,nil,'S4 old-save bubble stays native')
-- Consumption through the real native on_stand and the Zone superload.
local repairs={}
local baseZone={addEntity=function(self,level,e,typ,x,y) if typ=='terrain' or typ=='grid' then level.map(x,y,1,e) end end}
env.loadPrevious=function() return baseZone end
local Zone=setmetatable({},{__index=load(root..'superload/engine/Zone.lua')})
tm,h=scene('lake-nur',2,nil,placed())
tm(1,1,1).nb_charges=2
local g=setmetatable({level=h.level,zone=h.zone,logSeen=function() end,
 checkerRepairTerrain=function(self,x1,y1,x2,y2) repairs[#repairs+1]={x1,y1,x2,y2};return T.repair(h,x1,y1,x2,y2) end},{})
g.zone.makeEntityByName=function() return methods.clone(wd.WATER_FLOOR) end
g.zone.addEntity=function(z,...) return Zone.addEntity(z,...) end
local savedG=rawget(_G,'game');_G.game=g;env.game=g
local who={can_breath={},attr=function() end}
local cell=tm(1,1,1)
cell.on_stand(cell,1,1,who)
eq(tm(1,1,1),cell,'S4 first charge: bubble stays');eq(cell.nb_charges,1,'S4 charge spent natively');eq(#repairs,0,'S4 no repaint without a change')
cell.on_stand(cell,1,1,who)
eq(tm(1,1,1).define_as,'WATER_FLOOR','S4 depleted bubble swapped natively')
eq(#repairs,1,'S4 one repaint on swap');eq(table.concat(repairs[1],','),'0,0,2,2','S4 repaint is the 3x3 area')
eq(tm(1,1,1).replace_display.image,'checker-revised+refined/underwater/floor0.png','S4 swapped cell is the board floor')
local breather={can_breath={water=1},attr=function() end}
tm(1,1,1,placed());T.apply(h);cell=tm(1,1,1);cell.nb_charges=1;repairs={}
cell.on_stand(cell,1,1,breather);eq(tm(1,1,1),cell,'S4 water breather spends nothing');eq(#repairs,0,'S4 no repaint for a breather')
-- Horror death: a bubble added onto a board floor is repainted as a bubble.
local ng=methods.clone(bubble);ng.nb_charges=4
Zone.addEntity(g.zone,h.level,ng,'terrain',0,0)
eq(#repairs,1,'S4 spawned bubble repaints');eq(tm(0,0,1).replace_display.image,'checker-revised+refined/underwater/bubble0.png','S4 spawned bubble is board')
-- Gates: other swaps, other levels, other entity types, no change.
repairs={}
Zone.addEntity(g.zone,h.level,methods.clone(wd.WATER_FLOOR),'terrain',2,2);eq(#repairs,0,'S4 floor-to-floor swap: no repaint')
Zone.addEntity(g.zone,h.level,tm(2,1,1),'terrain',2,1);eq(#repairs,0,'S4 same grid re-added: no repaint')
Zone.addEntity(g.zone,{map=tm},methods.clone(wd.WATER_FLOOR),'terrain',0,0);eq(#repairs,0,'S4 other level: no repaint')
Zone.addEntity(g.zone,h.level,{},'actor',1,1);eq(#repairs,0,'S4 actor add: no repaint')
_G.game=savedG
-- T16: callback altars. Board floor of the family plus the native altar layer;
-- the callback (file+line), every rule field and the layer must be exact.
local sd=loadDefs('/data/zones/mark-spellblaze/grids.lua')
local cd=loadDefs('/data/zones/noxious-caldera/grids.lua')
eq(rawget(sd.ALTAR_CORRUPT,'_checker_s2_source')~=nil,true,'T16 corrupting altar stamped')
eq(rawget(sd.ALTAR,'_checker_s2_source'),nil,'T16 plain burntland altar not stamped')
eq(rawget(cd.ALTAR,'_checker_s2_source')~=nil,true,'T16 altar of dreams stamped')
eq(select(1,T.batch4Kind(methods.clone(cd.ALTAR),'caldera')),'altar','T16 Caldera altar kind')
eq(select(1,T.batch4Kind(methods.clone(cd.ALTAR),'meadow')),nil,'T16 Caldera altar is Caldera-only')
eq(select(1,T.batch4Kind(methods.clone(sd.ALTAR_CORRUPT),'caldera')),nil,'T16 corrupting altar not a Caldera kind')
local function altarScene(zone,level,defs,id,fill)
 local tm=townMap(3,3,function(x,y) return (x==1 and y==1) and defs[id] or defs[fill] end);tm.updateMap=function() end
 local h={zone={short_name=zone},level={map=tm,level=level,data={}}}
 env.game={zone=h.zone,level=h.level};T.apply(h)
 return tm,h
end
mode='refined'
local am,ah=altarScene('mark-spellblaze',2,sd,'ALTAR_CORRUPT','BURNT_GROUND')
local rd=am(1,1,1).replace_display
eq(rd and rd.image,'checker-revised+refined/burnt/floor0.png','T16 Spellblaze altar board floor')
eq(rd and rd.add_displays and rd.add_displays[1].image,'terrain/floor_pentagram.png','T16 Spellblaze altar keeps native pentagram')
eq(am(1,1,1).on_move,sd.ALTAR_CORRUPT.on_move,'T16 Spellblaze quest callback kept')
mode='vanilla';T.apply(ah);eq(am(1,1,1).replace_display,nil,'T16 Spellblaze altar native restore');mode='refined'
local cm,ch=altarScene('noxious-caldera',2,cd,'ALTAR','JUNGLE_GRASS')
rd=cm(1,1,1).replace_display
eq(rd and rd.image,'checker-revised+refined/caldera/floor0.png','T16 Caldera altar board floor')
local orb=rd and rd.add_displays and rd.add_displays[1]
eq(orb and orb.image..'|'..orb.z..'|'..orb.display_y..'|'..orb.display_h,'terrain/pedestal_orb_04.png|18|-1|2','T16 Caldera altar keeps native 2-tall orb')
eq(cm(1,1,1).does_block_move,true,'T16 Caldera altar still blocks')
mode='blockout';T.apply(ch);eq(cm(1,1,1).replace_display.image,'checker-revised+tree0.png','T16 Caldera altar blockout is a blocker')
mode='vanilla';T.apply(ch);eq(cm(1,1,1).replace_display,nil,'T16 Caldera altar native restore');mode='refined'
eq(altarScene('mark-spellblaze',2,sd,'ALTAR','BURNT_GROUND')(1,1,1).replace_display,nil,'T16 plain burntland altar (not reviewed) stays native')
local function altarNeg(defs,id,family,label,f)
 local g=deep(defs[id]);g.replace_display=nil;g._checker_terrain=nil;f(g)
 local tm=townMap(1,1,function() return g end);tm.updateMap=function() end
 local zone=family=='caldera' and 'noxious-caldera' or 'mark-spellblaze'
 local h={zone={short_name=zone},level={map=tm,level=2,data={}}};env.game={zone=h.zone,level=h.level};T.apply(h)
 eq(tm(0,0,1).replace_display,nil,'T16 altered '..id..' stays native: '..label)
end
for _,c in ipairs{{sd,'ALTAR_CORRUPT','burnt','on_move','@/data/zones/mark-spellblaze/grids.lua',28},{cd,'ALTAR','caldera','block_move','@/data/zones/noxious-caldera/grids.lua',35}} do
 local defs,id,family,fn,file,line=c[1],c[2],c[3],c[4],c[5],c[6]
 eq(debug.getinfo(defs[id][fn],'S').linedefined,line,'T16 native '..id..' '..fn..' line')
 for label,f in pairs{
  unstamped=function(g) g._checker_s2_source=nil end,
  ['shifted line']=function(g) g[fn]=assert(loadstring(pad(line+1),file))() end,
  ['foreign file']=function(g) g[fn]=assert(loadstring(pad(line),'@/data-foreign'..file:sub(2)))() end,
  ['extra callback']=function(g) g.on_stand=function() end end,
  name=function(g) g.name='altar' end, notice=function(g) g.notice=nil end,
  layer=function(g) g.add_displays[1].image='terrain/floor_pentagram2.png' end,
  ['extra layer']=function(g) g.add_displays[2]={image='terrain/signpost.png'} end,
  ['layer height']=function(g) g.add_displays[1].display_h=(g.add_displays[1].display_h or 1)+1 end,
  move=function(g) g.does_block_move=not g.does_block_move or nil end,
  level=function(g) g.change_level=1 end,
 } do altarNeg(defs,id,family,label,f) end
end
end)()
-- S6: Eruan (sand, palms, deep ocean, sand exits) and Gorbat Pride (sand,
-- mountains, bamboo drake roosts, loose rock door, basic.lua stone). Every S6
-- identity needs the zone list stamp; palms and sand exits also the sand.lua
-- stamp. Levers, the lever rock door and the Charred Scar farportals stay native.
;(function()
local eFile,gFile,sandFile='/data/zones/eruan/grids.lua','/data/zones/gorbat-pride/grids.lua','/data/general/grids/sand.lua'
local eDefs=loadDefs(eFile)
local oDefs=loadDefs(gFile)
-- Stamps: zone list over nested imports; sand.lua keeps its own file stamp.
eq(eDefs.PALMTREE5._checker_sand_source.file,sandFile,'S6 palm keeps its sand.lua stamp')
eq(eDefs.PALMTREE5._checker_sand_source.id,'PALMTREE5','S6 palm stamp id is the variant id')
eq(eDefs.PALMTREE5._checker_zone_source.file,eFile,'S6 Eruan list stamps nested sand.lua')
eq(eDefs.DEEP_OCEAN_WATER._checker_water_source.file,'/data/general/grids/water.lua','S6 Eruan ocean keeps its water.lua stamp')
eq(eDefs.CHARRED_SCAR_PORTAL._checker_zone_source.file,eFile,'S6 Eruan portal carries the list stamp (still native)')
eq(oDefs.FENCE_WALL._checker_zone_source.file,gFile,'S6 Gorbat list stamps its own roost walls')
eq(oDefs.FLOOR._checker_grid_source.file,'/data/general/grids/basic.lua','S6 Gorbat nested basic keeps its stamp')
eq(oDefs.FLOOR._checker_zone_source.file,gFile,'S6 Gorbat list stamps nested basic.lua')
-- Gating: Gorbat is a combined stone zone; Eruan is forest-only.
eq(T.variant({short_name='gorbat-pride'}),'GORBAT_PRIDE','S6 Gorbat stone gate')
eq(T.combined['gorbat-pride'],true,'S6 Gorbat combines forest and stone')
eq(T.variant({short_name='eruan'}),'ERUAN','S6 Eruan vault stone gate')
eq(T.combined.eruan,true,'S6 Eruan combines forest and vault stone')
for _,zone in ipairs{'grushnak-pride','vor-pride','high-peak','charred-scar'} do
 eq(T.batch4Kind(methods.clone(eDefs.SAND),zone),nil,'S6 sand not claimed by ungated '..zone)
end
-- Runtime palms: 1-3 native makeTrees parts (mod/class/Grid.lua:327-358).
local function palm(id,parts)
 local g=deep(eDefs[id]);local ds={}
 for i=1,parts do ds[i]=setmetatable({image='terrain/palmtree_alpha'..(i*3-1)..'.png',z=15+i,display_scale=0.8,display_x=0.1,
  display_y=-0.05,display_h=i==2 and 2 or 1,display_on_seen=true,display_on_remember=true,shader='tree',shader_args={attenuation=25}},meta) end
 g.add_displays=ds;return g
end
local function bordered(defs,id)
 local g=deep(defs[id]);g.add_displays={setmetatable({image='invis.png',add_mos={{image='terrain/sand/sand_8_01.png'},{image='terrain/sand/sand_inner_1_01.png'}}},meta)};return g
end
local eKinds={{deep(eDefs.SAND),'sand'},{bordered(eDefs,'SAND'),'sand'},{palm('PALMTREE1',1),'palm'},{palm('PALMTREE9',2),'palm'},
 {palm('PALMTREE20',3),'palm'},{deep(eDefs.DEEP_OCEAN_WATER),'deep'},{deep(eDefs.SAND_UP_WILDERNESS),'exit-world'},
 {deep(eDefs.SAND_UP8),'exit-up'},{deep(eDefs.SAND_DOWN2),'exit-down'},{deep(eDefs.HARDMOUNTAIN_WALL),'mountain'}}
for _,c in ipairs(eKinds) do
 local id=c[1].define_as
 eq(T.batch4Kind(c[1],'eruan'),c[2],'S6 exact Eruan '..id)
 local u=deep(c[1]);u._checker_zone_source=nil
 eq(T.batch4Kind(u,'eruan'),nil,'S6 unstamped (old-save) Eruan grid stays native '..id)
 for _,fam in ipairs{'beach','caldera','meadow','town-gates-of-morning','town-zigur','ring-of-blood','gorbat-pride'} do
  local got=T.batch4Kind(deep(c[1]),fam)
  if c[2]=='palm' or c[2]:match('^exit%-') then eq(got,nil,'S6 Eruan '..c[2]..' not claimed by '..fam..' '..id) end
 end
end
for _,id in ipairs{'PALMTREE5','SAND_UP8'} do
 local u=id=='PALMTREE5' and palm(id,1) or deep(eDefs[id]);u._checker_sand_source=nil
 eq(T.batch4Kind(u,'eruan'),nil,'S6 grid without its sand.lua stamp stays native '..id)
end
-- The base PALMTREE (never placed: nice_tiler replaces it) and untiled variants.
eq(T.batch4Kind(deep(eDefs.PALMTREE),'eruan'),nil,'S6 base PALMTREE stays native')
eq(T.batch4Kind(deep(eDefs.PALMTREE3),'eruan'),nil,'S6 palm without its native parts stays native')
-- A palm beside a non-sand cell carries its own sand-border carrier last.
local function edged(p0,img)
 local g=palm('PALMTREE6',p0);g.add_displays[#g.add_displays+1]=setmetatable({image='invis.png',add_mos={{image=img or 'terrain/sand/sand_2_01.png',display_y=1},{image='terrain/sand/sand_inner_3_01.png',display_x=1,display_y=1}}},meta);return g
end
eq(T.batch4Kind(edged(2),'eruan'),'palm','S6 palm with its native sand-border carrier')
eq(T.batch4Kind(edged(3),'eruan'),'palm','S6 three-part palm with its native sand-border carrier')
eq(T.batch4Kind(edged(2,'terrain/grass/grass_2_01.png'),'eruan'),nil,'S6 palm carrier with a foreign border stays native')
local ec=edged(1);ec.add_displays[2].z=3
eq(T.batch4Kind(ec,'eruan'),nil,'S6 palm carrier with a depth stays native')
ec=edged(1);ec.add_displays[2].add_mos={}
eq(T.batch4Kind(ec,'eruan'),nil,'S6 empty palm carrier stays native')
ec=edged(1);table.insert(ec.add_displays,1,setmetatable({image='invis.png',add_mos={{image='terrain/sand/sand_2_01.png'}}},meta))
eq(T.batch4Kind(ec,'eruan'),nil,'S6 palm carrier not last stays native')
for _,id in ipairs{'CHARRED_SCAR_PORTAL','CCHARRED_SCAR_PORTAL','SANDWALL','SANDWALL_STABLE2','UNDERGROUND_SAND3','SAND_UP2','SAND_DOWN8',
 'LAVA_FLOOR','TREE3','GRASS','MOUNTAIN_WALL','ROCKY_GROUND'} do
 if eDefs[id] then eq(T.batch4Kind(methods.clone(eDefs[id]),'eruan'),nil,'S6 not an Eruan board kind '..id) end
end
-- Palm rule/layer negatives: every field altered alone stays native.
for label,f in pairs{
 move=function(g) g.does_block_move=nil end, sight=function(g) g.block_sight=nil end,
 sense=function(g) g.block_sense=true end, esp=function(g) g.block_esp=true end,
 pass=function(g) g.can_pass={pass_tree=1,pass_wall=1} end, nopass=function(g) g.can_pass=nil end,
 dig=function(g) g.dig='FLOOR' end, air=function(g) g.air_level=-5 end, name=function(g) g.name='palm' end,
 subtype=function(g) g.subtype='grass' end, image=function(g) g.image='terrain/palmtree.png' end,
 stand=function(g) g.on_stand=function() end end, block=function(g) g.block_move=function() return true end end,
 level=function(g) g.change_level=1 end, remember=function(g) g.always_remember=nil end, mos=function(g) g.add_mos={{image='terrain/flower.png'}} end,
 part=function(g) g.add_displays[1].image='terrain/tree_alpha3.png' end, parts4=function(g) for i=1,4 do g.add_displays[i]=setmetatable({image='terrain/palmtree_alpha1.png',z=15+i,shader='tree',shader_args={attenuation=25},display_h=1},meta) end end,
 shader=function(g) g.add_displays[1].shader=nil end, att=function(g) g.add_displays[1].shader_args={attenuation=30} end,
 z=function(g) g.add_displays[1].z=18 end, h=function(g) g.add_displays[1].display_h=3 end,
 tint=function(g) g.add_displays[1].tint={r=1,g=0,b=0} end, border=function(g) g.add_displays[2]=setmetatable({image='invis.png'},meta) end,
} do local g=palm('PALMTREE7',1);f(g);eq(T.batch4Kind(g,'eruan'),nil,'S6 altered palm stays native: '..label) end
for label,f in pairs{
 level=function(g) g.change_level=2 end, zone=function(g) g.change_zone='charred-scar' end, name=function(g) g.name='x' end,
 layer=function(g) g.add_displays[1].image='terrain/way_next_2.png' end, extra=function(g) g.add_displays[2]=setmetatable({image='invis.png'},meta) end,
 check=function(g) g.change_level_check=function() end end, move=function(g) g.does_block_move=true end, notice=function(g) g.notice=nil end,
} do local g=deep(eDefs.SAND_UP8);f(g);eq(T.batch4Kind(g,'eruan'),nil,'S6 altered sand exit stays native: '..label) end
for _,c in ipairs{{'SAND',function(g) g.does_block_move=true end},{'DEEP_OCEAN_WATER',function(g) g.air_level=-1 end},
 {'HARDMOUNTAIN_WALL',function(g) g.dig='FLOOR' end}} do
 local g=deep(eDefs[c[1]]);c[2](g);eq(T.batch4Kind(g,'eruan'),nil,'S6 altered Eruan '..c[1]..' stays native')
end
-- Gorbat forest side.
local oKinds={SAND='sand',HARDMOUNTAIN_WALL='mountain',HARDMOUNTAIN_WALL3='mountain',MOUNTAIN_WALL='mountain',DEEP_WATER='deep',
 FENCE_WALL='hut-wall',FENCE_FLOOR='hut-floor',BHW_V_FULL1='hut-wall',BHW_H_FULL='hut-wall',BHW_N_CROSS1='hut-wall',BHW_S_CROSS1='hut-wall',
 BHW_E_CROSS1='hut-wall',BHW_W_CROSS1='hut-wall',BHW_CROSS1='hut-wall',BHW_SOLO1='hut-wall',BHW_NE1='hut-wall',BHW_NW1='hut-wall',
 BHW_SE1='hut-wall',BHW_SW1='hut-wall',FENCE_DOOR_HORIZ='hut-door-h',FENCE_DOOR_VERT='hut-door-v',
 FENCE_DOOR_HORIZ_OPEN='hut-door-h-open',FENCE_DOOR_OPEN_VERT='hut-door-v-open',ROCK_DOOR='rock-door'}
for i=1,8 do oKinds['BHW_H_FULL'..i]='hut-wall' end
for id,kind in pairs(oKinds) do
 eq(T.batch4Kind(methods.clone(oDefs[id]),'gorbat-pride'),kind,'S6 exact Gorbat '..id)
 local u=deep(oDefs[id]);u._checker_zone_source=nil
 eq(T.batch4Kind(u,'gorbat-pride'),nil,'S6 unstamped (old-save) Gorbat grid stays native '..id)
 if kind:match('^hut') or kind=='rock-door' then
  for _,fam in ipairs{'town-irkkk','eruan','beach','caldera','ring-of-blood'} do
   eq(T.batch4Kind(methods.clone(oDefs[id]),fam),nil,'S6 Gorbat '..kind..' not claimed by '..fam..' '..id)
  end
 end
end
eq(T.batch4Kind(methods.clone(oDefs.FENCE_DOOR),'gorbat-pride'),nil,'S6 unresolved door3d base stays native')
-- S11: ROCK_LEVER_DOOR and GENERIC_LEVER_SAND are exact S11 cells (tests/terrain_s11.lua).
for _,id in ipairs{'FLOOR','DOOR','FLAT_UP6','UP_WILDERNESS','PALMTREE5','TREE3'} do
 if oDefs[id] then eq(T.batch4Kind(methods.clone(oDefs[id]),'gorbat-pride'),nil,'S6 not a Gorbat forest kind '..id) end
end
-- Irkkk's jungle_hut grids never become Gorbat roosts (and vice versa above).
local iDefs2=loadDefs('/data/zones/town-irkkk/grids.lua')
for _,id in ipairs{'BAMBOO_HUT_WALL','BHW_V_FULL1','BAMBOO_HUT_FLOOR','BAMBOO_HUT_DOOR_HORIZ'} do
 eq(T.batch4Kind(methods.clone(iDefs2[id]),'gorbat-pride'),nil,'S6 Irkkk hut not a Gorbat roost '..id)
end
for label,c in pairs{
 wallSubtype={'BHW_V_FULL1',function(g) g.subtype='bamboo hut' end}, wallName={'FENCE_WALL',function(g) g.name='bamboo wall' end},
 wallDig={'BHW_NE1',function(g) g.dig='BAMBOO_HUT_FLOOR' end}, wallAir={'BHW_SW1',function(g) g.air_level=-20 end},
 wallPass={'BHW_SE1',function(g) g.can_pass={pass_wall=1,pass_tree=1} end}, wallSense={'BHW_NW1',function(g) g.block_sense=true end},
 wallMove={'BHW_H_FULL',function(g) g.does_block_move=nil end}, wallRoost={'FENCE_WALL',function(g) g.is_roost_entrance=true end},
 wallLayer={'BHW_V_FULL1',function(g) g.add_displays[1].image='terrain/bamboo/hut_wall_bottom_hor_01.png' end},
 wallLayerZ={'BHW_SOLO1',function(g) g.add_displays[2].z=18 end}, wallDecor={'BHW_H_FULL3',function(g) g.add_displays[1].add_mos[1].image='terrain/bamboo/wall_decor_mask_a_01.png' end},
 wallStand={'BHW_H_FULL5',function(g) g.on_stand=function() end end},
 doorRoost={'FENCE_DOOR_HORIZ',function(g) g.is_roost_entrance=nil end}, doorSight={'FENCE_DOOR_VERT',function(g) g.block_sight=nil end},
 doorOpened={'FENCE_DOOR_HORIZ',function(g) g.door_opened='BAMBOO_HUT_DOOR_HORIZ_OPEN' end}, doorDig={'FENCE_DOOR_VERT',function(g) g.dig='FLOOR' end},
 doorMove={'FENCE_DOOR_HORIZ',function(g) g.does_block_move=true end}, doorCheck={'FENCE_DOOR_HORIZ',function(g) g.block_move=function() return true end end},
 openRoost={'FENCE_DOOR_HORIZ_OPEN',function(g) g.is_roost_entrance=true end}, openClosed={'FENCE_DOOR_OPEN_VERT',function(g) g.door_closed='FENCE_DOOR_HORIZ' end},
 openSight={'FENCE_DOOR_HORIZ_OPEN',function(g) g.block_sight=true end},
 floorGrow={'FENCE_FLOOR',function(g) g.grow='BAMBOO_HUT_WALL' end}, floorName={'FENCE_FLOOR',function(g) g.name='bamboo hut floor' end},
 floorMos={'FENCE_FLOOR',function(g) g.add_mos={{image='terrain/bamboo/floor_deco_cooking_pit_c_01.png'}} end},
 rockOpened={'ROCK_DOOR',function(g) g.door_opened='SAND' end}, rockLever={'ROCK_DOOR',function(g) g.on_lever_change=function() end end},
 rockStop={'ROCK_DOOR',function(g) g.door_player_stop='sealed' end}, rockLayer={'ROCK_DOOR',function(g) g.add_displays[1].z=5 end},
 rockSense={'ROCK_DOOR',function(g) g.block_sense=true end}, rockMove={'ROCK_DOOR',function(g) g.does_block_move=true end},
 sandMove={'SAND',function(g) g.does_block_move=true end}, mountainDig={'HARDMOUNTAIN_WALL',function(g) g.dig='FLOOR' end},
 waterAir={'DEEP_WATER',function(g) g.air_level=-1 end},
} do local g=deep(oDefs[c[1]]);c[2](g);eq(T.batch4Kind(g,'gorbat-pride'),nil,'S6 altered Gorbat grid stays native: '..label) end
-- Gorbat stone (classify under the zone): exact basic.lua identities with the list stamp.
local saved=env.game
env.game={zone={short_name='gorbat-pride'}}
for id,kind in pairs{FLOOR='floor',FLAT_DOWN4='stairs-down',FLAT_UP6='stairs-up',UP_WILDERNESS='stairs-world',HARDWALL='hardwall',DOOR='door-closed'} do
 local got=T.classify(methods.clone(oDefs[id]))
 eq(got,kind,'S6 Gorbat stone '..id)
 local u=deep(oDefs[id]);u._checker_zone_source=nil
 eq(T.classify(u),nil,'S6 Gorbat stone without the list stamp stays native '..id)
end
for _,id in ipairs{'ROCK_LEVER_DOOR','GENERIC_LEVER_SAND','ROCK_DOOR','FENCE_FLOOR','SAND'} do
 eq(T.classify(methods.clone(oDefs[id])),nil,'S6 not a Gorbat stone kind '..id)
end
env.game={zone={short_name='eruan'}}
for _,id in ipairs{'SAND','PALMTREE5','CHARRED_SCAR_PORTAL','CCHARRED_SCAR_PORTAL'} do eq(T.classify(methods.clone(eDefs[id])),nil,'S6 not an Eruan stone kind '..id) end
for id,kind in pairs{FLOOR='floor',HARDWALL='hardwall',WALL='wall',DOOR='door-closed'} do
 eq(T.classify(methods.clone(eDefs[id])),kind,'S6 Eruan vault stone '..id)
 local u=deep(eDefs[id]);u._checker_zone_source=nil
 eq(T.classify(u),nil,'S6 Eruan vault stone without the list stamp stays native '..id)
end
-- Scene: an Eruan shore (palms, sand, ocean, exits, the farportal) through
-- Refined -> Blockout -> Native -> Refined; rule fields never change.
local eplan={'pSp~','SpS~','<S>&'}
local esym={S='SAND',['~']='DEEP_OCEAN_WATER',['<']='SAND_UP8',['>']='SAND_DOWN2',['&']='CHARRED_SCAR_PORTAL'}
local em=townMap(4,3,function(x,y) local c=eplan[y+1]:sub(x+1,x+1);if c=='p' then return palm('PALMTREE'..(x+y+1),2) end;return eDefs[esym[c]] end)
local eRules={}
for x=0,3 do for y=0,2 do local r={};for key,v in pairs(em(x,y,1)) do r[key]=v end;eRules[x+y*4]=r end end
local eh={zone={short_name='eruan'},level={map=em,data={}}}
env.game={zone=eh.zone};mode='refined';T.apply(eh)
eq(eh.checker_mode,'refined','S6 Eruan refined mode')
local function ei(x,y) return em(x,y,1).replace_display and em(x,y,1).replace_display.image end
eq(ei(0,0),'checker-revised+refined/eruan/palm-a0.png','S6 palm (0,0) plain parity 0')
eq(ei(1,1),'checker-revised+refined/eruan/palm-a0.png','S6 palm (1,1) plain parity 0')
eq(ei(2,0),'checker-revised+refined/eruan/palm-b0.png','S6 palm (2,0) mirrored, same parity')
eq(ei(1,0),'checker-revised+refined/beach/sand1.png','S6 Eruan sand is beach sand')
eq(ei(3,0):match('^checker%-revised%+refined/deep%d+%-1%-0%.png$')~=nil,true,'S6 Eruan ocean is board deep water')
eq(ei(0,2),'checker-revised+refined/eruan/exit-up0.png','S6 Eruan way up')
eq(ei(2,2),'checker-revised+refined/eruan/exit-down0.png','S6 Eruan way down')
eq(ei(3,2),nil,'S6 Charred Scar farportal stays native')
local pm=townMap(2,1,function(x) return palm('PALMTREE4',1) end)
T.apply({zone={short_name='eruan'},level={map=pm,data={}}})
eq(pm(1,0,1).replace_display.image,'checker-revised+refined/eruan/palm-a1.png','S6 plain palm at parity 1 (variant independent of parity)')
for x=0,3 do for y=0,2 do
 for key,v in pairs(eRules[x+y*4]) do if key~='replace_display' and key~='_checker_terrain' then eq(em(x,y,1)[key],v,'S6 Eruan rule field '..tostring(key)) end end
end end
mode='blockout';T.apply(eh)
eq(ei(0,0),'checker-revised+tree0.png','S6 blockout palm reads as blocking')
eq(ei(0,2),'checker-revised+exit0.png','S6 blockout sand exit reads as exit')
mode='vanilla';T.apply(eh)
for x=0,3 do for y=0,2 do eq(em(x,y,1).replace_display,nil,'S6 native mode restores Eruan '..x..','..y) end end
mode='refined';T.apply(eh)
eq(ei(0,0),'checker-revised+refined/eruan/palm-a0.png','S6 refined restore palm')
-- Scene: a Gorbat roost (walls, a closed door, floor) on sand, the rock door
-- and a mountain; the rock keeps its native layer over board sand.
local gplan={'^^^^^','|!|/.','|:|S^'}
local gsym={['^']='HARDMOUNTAIN_WALL',['|']='FENCE_WALL',['!']='FENCE_DOOR_HORIZ',[':']='FENCE_FLOOR',S='SAND',['/']='ROCK_DOOR',['.']='SAND'}
local gm=townMap(5,3,function(x,y) return oDefs[gsym[gplan[y+1]:sub(x+1,x+1)]] end)
local gh={zone={short_name='gorbat-pride'},level={map=gm,data={}}}
env.game={zone=gh.zone};mode='refined';T.apply(gh)
local function gi(x,y) return gm(x,y,1).replace_display and gm(x,y,1).replace_display.image end
eq(gi(0,0),'checker-revised+refined/daikara/mountain-wall-20.png','S6 Gorbat mountain (E) Daikara masks')
eq(gi(0,1),'checker-revised+refined/bamboo/wall-6-1.png','S6 roost wall joins the door (E) and wall (S)')
eq(gi(1,1),'checker-revised+refined/bamboo/door-closed-horizontal0.png','S6 roost door board closed door')
eq(gi(1,2),'checker-revised+refined/bamboo/floor1.png','S6 roost floor board hut floor')
eq(gi(3,1),'checker-revised+refined/beach/sand0.png','S6 rock door floor is board sand')
local rl=gm(3,1,1).replace_display.add_displays
eq(rl and #rl==1 and rl[1].image,'terrain/huge_rock.png','S6 rock door keeps its native rock')
eq(rl[1].z,18,'S6 rock layer native depth')
mode='blockout';T.apply(gh)
eq(gi(3,1),'checker-revised+tree0.png','S6 blockout rock door reads as blocking')
eq(gi(1,1),'checker-revised+tree0.png','S6 blockout closed roost door reads as blocking')
mode='vanilla';T.apply(gh)
for x=0,4 do for y=0,2 do eq(gm(x,y,1).replace_display,nil,'S6 native mode restores Gorbat '..x..','..y) end end
mode='refined';T.apply(gh)
eq(gm(3,1,1).replace_display.add_displays[1].image,'terrain/huge_rock.png','S6 refined restore rock door')
-- Old save: unstamped roost/sand cells beside stamped ones stay native.
local go=townMap(3,1,function(x) local g=deep(oDefs[({'FENCE_WALL','SAND','ROCK_DOOR'})[x+1]]);g._checker_zone_source=nil;return g end)
T.apply({zone={short_name='gorbat-pride'},level={map=go,data={}}})
for x=0,2 do eq(go(x,0,1).replace_display,nil,'S6 old-save Gorbat cell stays native '..x) end
-- TW7: Gates of Morning's palms use this exact S6 palm contract under the town stamp; its other kinds unchanged.
local gates=loadDefs('/data/zones/town-gates-of-morning/grids.lua')
local gp=deep(gates.PALMTREE5);gp.add_displays={setmetatable({image='terrain/palmtree_alpha2.png',z=16,shader='tree',shader_args={attenuation=25},display_h=1},meta)}
eq(T.batch4Kind(gp,'town-gates-of-morning'),'palm','TW7 Gates of Morning palm on the S6 palm contract')
eq(T.batch4Kind(methods.clone(gates.SAND),'town-gates-of-morning'),'sand','S6 Gates sand unchanged')
env.game=saved;mode='refined'
end)()
-- S8 (V2/V7): in listed stone zones the diggable WALL and the door jambs draw
-- the darker korpul-dark recolour (same mask/parity); HARDWALL and floors keep
-- Kor'Pul art; unlisted zones, and a missing/partial manifest, keep the old
-- brick. Rules are never touched.
;(function()
 local sg=env.game
 local savedDark=T.korpulDarkAssets
 local function dm()
  -- row 0: WALL DOOR WALL / row 1: FLOOR FLOOR HARDWALL
  local cells={[0]=grids.WALL,[1]=grids.DOOR,[2]=grids.WALL,[3]=grids.FLOOR,[4]=grids.FLOOR,[5]=grids.HARDWALL}
  local mm={w=3,h=2,seens=function() return true end,infovs=function() return true end}
  for k,g in pairs(cells) do T.observe(mm,k%3,math.floor(k/3),g) end
  return mm,cells
 end
 local function images(zone)
  env.game={zone={short_name=zone}}
  local mm,cells=dm()
  local out={}
  for k,g in pairs(cells) do local d=T.render(mm,k%3,math.floor(k/3),g,'refined');out[k]=d and d.image end
  return out
 end
 T.korpulDarkAssets={ready=true,files=setmetatable({},{__index=function(_,k) return type(k)=='string' and k:match('^checker%-revised%+refined/korpul%-dark/') and true or nil end})}
 local rulesBefore=tostring(grids.WALL.does_block_move)..tostring(grids.WALL.block_sight)..tostring(grids.WALL.dig)
 for _,zone in ipairs{'ruins-kor-pul','telmur','dreadfell','shadow-crypt','lake-nur','ring-of-blood'} do
  local im=images(zone)
  eq(im[0],'checker-revised+refined/korpul-dark/wall-0-0.png','S8 dark diggable wall '..zone)
  eq(im[2],'checker-revised+refined/korpul-dark/wall-4-0.png','S8 dark wall keeps its mask '..zone)
  eq(im[1],(T.assetPath('door-closed','horizontal',10,1,1,0):gsub('/korpul/','/korpul-dark/')),'S8 door jambs match the dark wall '..zone)
  eq(im[5],T.assetPath('hardwall',nil,1,1,2,1),'S8 HARDWALL keeps Kor\'Pul art '..zone)
  eq(im[3],T.assetPath('floor',nil,0,1,0,1),'S8 floor unchanged '..zone)
 end
 -- Lumberjack's cabin wall (town list stamp) also draws the dark brick.
 env.game={zone={short_name='town-lumberjack-village'}}
 local lm={w=1,h=1,seens=function() return true end,infovs=function() return true end}
 local lw=methods.clone(lumberDefs.WALL)
 T.observe(lm,0,0,lw)
 eq(T.render(lm,0,0,lw,'refined').image,'checker-revised+refined/korpul-dark/wall-0-0.png','S8 Lumberjack cabin wall is dark brick')
 for _,zone in ipairs{'town-derth','town-zigur','last-hope-graveyard','charred-scar'} do
  local im=images(zone)
  if im[0] then eq(im[0]:match('korpul%-dark'),nil,'S8 unlisted zone keeps the old brick '..zone) end
 end
 T.korpulDarkAssets={ready=false,files={}}
 local im=images('telmur')
 eq(im[0],'checker-revised+refined/korpul/wall-0-0.png','S8 missing dark manifest keeps the shipped brick')
 T.korpulDarkAssets={ready=true,files={}}
 im=images('telmur')
 eq(im[0],'checker-revised+refined/korpul/wall-0-0.png','S8 dark file not in the manifest keeps the shipped brick')
 eq(tostring(grids.WALL.does_block_move)..tostring(grids.WALL.block_sight)..tostring(grids.WALL.dig),rulesBefore,'S8 rules untouched')
 eq(grids.WALL.replace_display,nil,'S8 rule object has no display')
 T.korpulDarkAssets=savedDark
 env.game=sg
end)()
-- S9: High Peak. L1-4 caverns on the exact cave contract, L5-10 Roomer and
-- the Sanctum (L11) on the basic.lua stone contract with the S8 dark brick,
-- and its two next-level stairs as exact S2 specs. Every S9 cell needs the
-- zone list stamp (old saves keep native). Portals, farportals, the void
-- portal and the ORB_* invocation portals stay native. Rules never change.
;(function()
local sg,savedStairs,savedDark=env.game,T.stairAssets,T.korpulDarkAssets
local hFile='/data/zones/high-peak/grids.lua'
local hDefs=loadDefs(hFile)
T.stairAssets={ready=true,files=setmetatable({},{__index=function(_,k) return type(k)=='string' and k:match('^checker%-revised%+refined/korpul/stairs%-') and true or nil end})}
T.korpulDarkAssets={ready=true,files=setmetatable({},{__index=function(_,k) return type(k)=='string' and k:match('^checker%-revised%+refined/korpul%-dark/') and true or nil end})}
-- Stamps: the zone list over its nested imports; the general stamps survive.
eq(hDefs.FLOOR._checker_zone_source.file,hFile,'S9 list stamps nested basic.lua FLOOR')
eq(hDefs.FLOOR._checker_grid_source.file,'/data/general/grids/basic.lua','S9 FLOOR keeps its basic.lua stamp')
eq(hDefs.CAVEWALL._checker_zone_source.file,hFile,'S9 list stamps nested cave.lua CAVEWALL')
eq(hDefs.CAVEWALL._checker_cave_source.file,'/data/general/grids/cave.lua','S9 CAVEWALL keeps its cave.lua stamp')
eq(hDefs.HIGH_PEAK_UP._checker_s2_source.id,'HIGH_PEAK_UP','S9 Roomer stairs carry the S2 stamp')
eq(hDefs.CAVE_HIGH_PEAK_UP._checker_s2_source.id,'CAVE_HIGH_PEAK_UP','S9 cavern stairs carry the S2 stamp')
for _,id in ipairs{'PORTAL_BOSS','FAR_EAST_PORTAL','VOID_PORTAL','ORB_UNDEATH'} do
 eq(hDefs[id]._checker_s2_source,nil,'S9 no S2 spec for '..id)
end
-- Gating.
eq(T.variant({short_name='high-peak'}),'HIGH_PEAK','S9 High Peak stone gate')
eq(T.combined['high-peak'],true,'S9 High Peak combines cave and stone levels')
-- Stone kinds under the zone, and the same cell without the list stamp.
env.game={zone={short_name='high-peak'}}
for id,kind in pairs{FLOOR='floor',WALL='wall',HARDWALL='hardwall',DOOR='door-closed',DOOR_OPEN='door-open',
 UP='stairs-up',HIGH_PEAK_UP='stairs-up',DOOR_VAULT='door-closed'} do
 eq(T.classify(methods.clone(hDefs[id])),kind,'S9 stone '..id)
 local u=deep(hDefs[id]);u._checker_zone_source=nil
 eq(T.classify(u),nil,'S9 stone without the list stamp stays native '..id)
end
for _,id in ipairs{'PORTAL_BOSS','FAR_EAST_PORTAL','CFAR_EAST_PORTAL','WEST_PORTAL','CWEST_PORTAL','VOID_PORTAL','CVOID_PORTAL',
 'ORB_UNDEATH','ORB_ELEMENTS','ORB_DRAGON','ORB_DESTRUCTION','CAVEFLOOR','CAVEWALL','HARDCAVEWALL','CAVE_ROCK_VAULT',
 'CAVE_DOOR','CAVE_HIGH_PEAK_UP'} do
 eq(T.classify(methods.clone(hDefs[id])),nil,'S9 not a stone kind '..id)
end
-- HIGH_PEAK_UP: one changed rule field, layer or callback keeps it native.
for label,c in pairs{
 level=function(g) g.change_level=-1 end, zone=function(g) g.change_zone='wilderness' end,
 check=function(g) g.change_level_check=function() return true end end, abs=function(g) g.change_level_abs=true end,
 name=function(g) g.name='previous level' end, image=function(g) g.image='terrain/cave/cave_floor_1_01.png' end,
 display=function(g) g.display='<' end, notice=function(g) g.notice=nil end, remember=function(g) g.always_remember=nil end,
 move=function(g) g.does_block_move=true end, sight=function(g) g.block_sight=true end, type=function(g) g.type='floor';g.subtype='floor' end,
 mos=function(g) g.add_mos={{image='terrain/stair_down.png'}} end, mos2=function(g) g.add_mos[2]={image='terrain/demon_portal4.png'} end,
 layer=function(g) g.add_displays={setmetatable({image='terrain/stair_up.png'},meta)} end,
 stand=function(g) g.on_stand=function() end end, bump=function(g) g.block_move=function() end end,
 portal=function(g) g.orb_portal={nothing=true} end, tooltip=function(g) g.show_tooltip=true end,
 lore=function(g) g.lore='x' end, stop=function(g) g.door_player_stop='x' end,
} do local g=deep(hDefs.HIGH_PEAK_UP);c(g);eq(T.classify(g),nil,'S9 altered Roomer stairs stay native: '..label) end
env.game={zone={short_name='dreadfell'}}
eq(T.classify(methods.clone(hDefs.HIGH_PEAK_UP)),nil,'S9 Roomer stairs are not claimed outside High Peak')
-- Cave cells (tw4.hpCave) under the zone.
eq(T.hpCave(methods.clone(hDefs.CAVEFLOOR)),'floor','S9 cave floor')
eq(T.hpCave(methods.clone(hDefs.CAVEFLOOR12)),'floor','S9 cave rock floor')
eq(T.hpCave(methods.clone(hDefs.CAVEWALL)),'wall','S9 cave wall')
eq(T.hpCave(methods.clone(hDefs.CAVE_HIGH_PEAK_UP)),'ladder-up','S9 cavern stairs are the cave up-ladder')
for _,id in ipairs{'HARDCAVEWALL','CAVE_ROCK_VAULT','CAVE_DOOR','HIGH_PEAK_UP','FLOOR','PORTAL_BOSS','VOID_PORTAL','ORB_DRAGON'} do
 eq(T.hpCave(methods.clone(hDefs[id])),nil,'S9 not a cave kind '..id)
end
for _,id in ipairs{'CAVEFLOOR','CAVEWALL','CAVE_HIGH_PEAK_UP'} do
 local u=deep(hDefs[id]);u._checker_zone_source=nil
 eq(T.hpCave(u),nil,'S9 cave cell without the list stamp stays native '..id)
end
for label,c in pairs{
 level=function(g) g.change_level=2 end, zone=function(g) g.change_zone='wilderness' end, name=function(g) g.name='ladder to the next level' end,
 display=function(g) g.display='<' end, layer=function(g) g.add_displays[1].image='terrain/cave/cave_stairs_down_3_01.png' end,
 layer2=function(g) g.add_displays[2]=setmetatable({image='terrain/cave/cavewall_8_1.png',z=18},meta) end,
 layerZ=function(g) g.add_displays[1].z=18 end, type=function(g) g.type='floor';g.subtype='cave' end,
 stand=function(g) g.on_stand=function() end end, check=function(g) g.change_level_check=function() end end,
 sight=function(g) g.block_sight=true end, remember=function(g) g.always_remember=nil end,
} do local g=deep(hDefs.CAVE_HIGH_PEAK_UP);c(g);eq(T.hpCave(g),nil,'S9 altered cavern stairs stay native: '..label) end
-- Scene L1-4: cave wall, floor and the cavern stairs through Refined ->
-- Blockout -> Native -> Refined; rule fields never change.
local cplan={'###','.>.'}
local csym={['#']='CAVEWALL',['.']='CAVEFLOOR',['>']='CAVE_HIGH_PEAK_UP'}
local cm=townMap(3,2,function(x,y) return hDefs[csym[cplan[y+1]:sub(x+1,x+1)]] end)
local cRules={}
for x=0,2 do for y=0,1 do local r={};for key,v in pairs(cm(x,y,1)) do r[key]=v end;cRules[x+y*3]=r end end
local ch={zone={short_name='high-peak'},level={map=cm,data={}}}
env.game={zone=ch.zone};mode='refined';T.apply(ch)
local function ci(x,y) return cm(x,y,1).replace_display and cm(x,y,1).replace_display.image end
eq(ci(0,0),'checker-revised+refined/cave/wall-2-0.png','S9 cave wall joins its east neighbour')
eq(ci(1,0),'checker-revised+refined/cave/wall-10-1.png','S9 cave wall joins east and west')
eq(ci(0,1),'checker-revised+refined/cave/floor1.png','S9 cave floor')
eq(ci(1,1),'checker-revised+refined/cave/ladder-up0.png','S9 cavern stairs drawn as the board up-ladder')
eq(cm(1,1,1).change_level,1,'S9 cavern stairs still lead to the next level')
for x=0,2 do for y=0,1 do
 for key,v in pairs(cRules[x+y*3]) do if key~='replace_display' and key~='_checker_terrain' then eq(cm(x,y,1)[key],v,'S9 cave rule field '..tostring(key)) end end
end end
mode='blockout';T.apply(ch)
eq(ci(0,0),'checker-revised+tree0.png','S9 blockout cave wall reads as blocking')
eq(ci(1,1),'checker-revised+exit0.png','S9 blockout cavern stairs read as exit')
mode='vanilla';T.apply(ch)
for x=0,2 do for y=0,1 do eq(cm(x,y,1).replace_display,nil,'S9 native mode restores cave '..x..','..y) end end
mode='refined';T.apply(ch)
eq(ci(1,1),'checker-revised+refined/cave/ladder-up0.png','S9 refined restore cavern stairs')
-- Old save: unstamped cave cells stay native.
local co=townMap(3,1,function(x) local g=deep(hDefs[({'CAVEWALL','CAVEFLOOR','CAVE_HIGH_PEAK_UP'})[x+1]]);g._checker_zone_source=nil;return g end)
T.apply({zone={short_name='high-peak'},level={map=co,data={}}})
for x=0,2 do eq(co(x,0,1).replace_display,nil,'S9 old-save cave cell stays native '..x) end
-- A Roomer level has no cave cell for applyForest to claim.
local rplan={'#+#','.>&'}
local rsym={['#']='WALL',['+']='DOOR',['.']='FLOOR',['>']='HIGH_PEAK_UP',['&']='PORTAL_BOSS'}
local rm=townMap(3,2,function(x,y) return hDefs[rsym[rplan[y+1]:sub(x+1,x+1)]] end)
for x=0,2 do for y=0,1 do rm.seen[x+y*3]=true end end
local rh={zone={short_name='high-peak'},level={map=rm,data={}}}
env.game={zone=rh.zone};mode='refined';T.apply(rh)
for x=0,2 do for y=0,1 do eq(rm(x,y,1).replace_display,nil,'S9 Roomer cell not claimed by the cave family '..x..','..y) end end
-- Stone adapter: dark brick walls and jambs, board stairs-up overlay, native portal.
for x=0,2 do for y=0,1 do T.observe(rm,x,y,rm(x,y,1)) end end
local function rr(x,y) local d=T.render(rm,x,y,rm(x,y,1),'refined');return d end
eq(rr(0,0).image,'checker-revised+refined/korpul-dark/wall-0-0.png','S9 diggable WALL draws the S8 dark brick')
eq(rr(1,0).image:match('^checker%-revised%+refined/korpul%-dark/door%-closed%-')~=nil,true,'S9 door jambs match the dark brick')
eq(rr(0,1).image,T.assetPath('floor',nil,0,1,0,1),'S9 Roomer floor')
local up=rr(1,1)
eq(up and up.add_mos and up.add_mos[1].image,'checker-revised+refined/korpul/stairs-up.png','S9 Roomer stairs drawn as board up stairs')
eq(rm(1,1,1).change_level,1,'S9 Roomer stairs still lead to the next level')
eq(rr(2,1),nil,'S9 Sanctum portal stays native')
eq(rm._checker_korpul[2+1*3],nil,'S9 portal gets no record')
-- Old save: an unstamped Roomer level stays native.
local ro=townMap(2,1,function(x) local g=deep(hDefs[({'WALL','HIGH_PEAK_UP'})[x+1]]);g._checker_zone_source=nil;return g end)
for x=0,1 do ro.seen[x]=true;T.observe(ro,x,0,ro(x,0,1));eq(T.render(ro,x,0,ro(x,0,1),'refined'),nil,'S9 old-save stone stays native '..x) end
T.stairAssets,T.korpulDarkAssets=savedStairs,savedDark
env.game=sg;mode='refined'
end)()
-- TW7: town roads draw board stone slabs (every other zone keeps the dirt
-- road), Zigur/Angolwen FIELDS1-4 draw the board crop field on an exact
-- plain-grass contract, and Gates of Morning's palms use S6's exact palm
-- contract under the town stamp. Rules are never touched.
;(function()
local sg=env.game
local zFile,aFile,gFile='/data/zones/town-zigur/grids.lua','/data/zones/town-angolwen/grids.lua','/data/zones/town-gates-of-morning/grids.lua'
local zDefs,aDefs,gDefs=loadDefs(zFile),loadDefs(aFile),loadDefs(gFile)
local dDefs=loadDefs('/data/zones/town-derth/grids.lua')
eq(zDefs.FIELDS3._checker_town_source.file,zFile,'TW7 Zigur list stamps its fields')
eq(aDefs.FIELDS1._checker_town_source.id,'FIELDS1','TW7 Angolwen stamp id is the variant id')
eq(zDefs.FIELDS3._checker_forest_source.id,'GRASS','TW7 fields inherit only the GRASS forest stamp')
local function field(defs,id,borders)
 local g=deep(defs[id])
 if borders then
  local ms={};for i,img in ipairs(borders) do ms[i]={image=img} end
  g.add_displays={setmetatable({image='invis.png',add_mos=ms},meta)}
 end
 return g
end
for i=1,4 do
 eq(T.batch4Kind(field(zDefs,'FIELDS'..i),'town-zigur'),'fields','TW7 Zigur FIELDS'..i)
 eq(T.batch4Kind(field(aDefs,'FIELDS'..i),'town-angolwen'),'fields','TW7 Angolwen FIELDS'..i)
 eq(T.batch4Kind(field(aDefs,'FIELDS'..i,{'terrain/grass/grass_7_01.png'}),'town-angolwen'),'fields','TW7 Angolwen FIELDS'..i..' with its grass-border carrier')
 local u=field(zDefs,'FIELDS'..i);u._checker_town_source=nil
 eq(T.batch4Kind(u,'town-zigur'),nil,'TW7 unstamped (old-save) field stays native '..i)
 eq(T.batch4Kind(field(zDefs,'FIELDS'..i),'town-angolwen'),nil,'TW7 Zigur field is not an Angolwen field '..i)
 eq(T.batch4Kind(field(aDefs,'FIELDS'..i),'town-zigur'),nil,'TW7 Angolwen field is not a Zigur field '..i)
 eq(T.batch4Kind(field(dDefs,'FIELDS'..i),'town-derth'),nil,'TW7 Derth (0 map cells) fields stay native '..i)
 for _,fam in ipairs{'beach','meadow','caldera','town-gates-of-morning','valley-moon'} do
  eq(T.batch4Kind(field(zDefs,'FIELDS'..i),fam),nil,'TW7 fields are town scoped '..fam..' '..i)
 end
 env.game={zone={short_name='town-zigur'}}
 eq(T.classify(field(zDefs,'FIELDS'..i)),nil,'TW7 field is not stone '..i)
end
eq(T.batch4Kind(field(zDefs,'FIELDS'),'town-zigur'),nil,'TW7 untiled FIELDS base stays native')
for _,m in ipairs{
 {'wrong crop number',function(c) c.add_mos[1].image='terrain/cultivation03.png' end},
 {'no crop layer',function(c) c.add_mos=nil end},
 {'second crop layer',function(c) c.add_mos[2]={image='terrain/cultivation01.png'} end},
 {'crop layer offset',function(c) c.add_mos[1].display_y=-1 end},
 {'foreign carrier art',function(c) c.add_displays={setmetatable({image='invis.png',add_mos={{image='terrain/road_dirt/road_a_01.png'}}},meta)} end},
 {'carrier with depth',function(c) c.add_displays={setmetatable({image='invis.png',z=3,add_mos={{image='terrain/grass/grass_2_01.png'}}},meta)} end},
 {'prop display',function(c) c.add_displays={setmetatable({image='terrain/signpost.png'},meta)} end},
 {'blocks move',function(c) c.does_block_move=true end},{'blocks sight',function(c) c.block_sight=true end},
 {'diggable',function(c) c.dig='GRASS' end},{'can_pass',function(c) c.can_pass={pass_tree=1} end},
 {'grows other',function(c) c.grow='FIELDS' end},{'road',function(c) c.road='dirt' end},
 {'on_move',function(c) c.on_move=function() end end},{'on_stand',function(c) c.on_stand=function() end end},
 {'block_move',function(c) c.block_move=function() return true end end},{'transition',function(c) c.change_zone='wilderness' end},
 {'renamed',function(c) c.name='grass' end},{'redisplayed',function(c) c.display='.' end},
 {'retyped',function(c) c.subtype='floor' end},{'other image',function(c) c.image='terrain/cultivation.png' end},
 {'remembered',function(c) c.always_remember=true end},{'noticed',function(c) c.notice=true end},
 {'air',function(c) c.air_level=-5 end},{'shader',function(c) c.shader='water' end},
} do
 local c=field(zDefs,'FIELDS2');m[2](c)
 eq(T.batch4Kind(c,'town-zigur'),nil,'TW7 altered field stays native: '..m[1])
end
-- Gates of Morning palms: the S6 contract (makeTrees parts, optional sand carrier) under the town stamp.
local function gpalm(id,parts,carrier)
 local g=deep(gDefs[id]);local ds={}
 for i=1,parts do ds[i]=setmetatable({image='terrain/palmtree_alpha'..i..'.png',z=15+i,shader='tree',shader_args={attenuation=25},display_h=i==1 and 1 or 2},meta) end
 if carrier then ds[#ds+1]=setmetatable({image='invis.png',add_mos={{image='terrain/sand/sand_2_01.png'}}},meta) end
 g.add_displays=ds;return g
end
eq(gDefs.PALMTREE13._checker_sand_source.file,'/data/general/grids/sand.lua','TW7 Gates palm keeps its sand.lua stamp')
eq(gDefs.PALMTREE13._checker_town_source.file,gFile,'TW7 Gates list stamps its nested palms')
eq(T.batch4Kind(gpalm('PALMTREE13',2),'town-gates-of-morning'),'palm','TW7 Gates palm (two parts)')
eq(T.batch4Kind(gpalm('PALMTREE17',1),'town-gates-of-morning'),'palm','TW7 Gates palm (one part)')
eq(T.batch4Kind(gpalm('PALMTREE4',1,true),'town-gates-of-morning'),'palm','TW7 Gates palm with its sand-border carrier')
local up=gpalm('PALMTREE9',2);up._checker_town_source=nil
eq(T.batch4Kind(up,'town-gates-of-morning'),nil,'TW7 unstamped (old-save) Gates palm stays native')
local us=gpalm('PALMTREE9',2);us._checker_sand_source=nil
eq(T.batch4Kind(us,'town-gates-of-morning'),nil,'TW7 Gates palm without the sand.lua stamp stays native')
for _,other in ipairs{'town-zigur','town-derth','town-irkkk','town-last-hope'} do
 eq(T.batch4Kind(gpalm('PALMTREE9',2),other),nil,'TW7 Gates palm is scoped to its town '..other)
end
eq(T.batch4Kind(deep(gDefs.PALMTREE),'town-gates-of-morning'),nil,'TW7 base PALMTREE stays native')
for _,m in ipairs{
 {'passable',function(c) c.does_block_move=nil end},{'see-through',function(c) c.block_sight=nil end},
 {'dig',function(c) c.dig='FLOOR' end},{'pass_wall',function(c) c.can_pass={pass_tree=1,pass_wall=1} end},
 {'foreign part',function(c) c.add_displays[1].image='terrain/trees/pine_01.png' end},
 {'part depth',function(c) c.add_displays[1].z=5 end},{'callback',function(c) c.on_stand=function() end end},
 {'four parts',function(c) for i=3,4 do c.add_displays[i]=setmetatable({image='terrain/palmtree_alpha1.png',z=15+i,shader='tree',shader_args={attenuation=25},display_h=2},meta) end end},
} do
 local c=gpalm('PALMTREE12',2);m[2](c)
 eq(T.batch4Kind(c,'town-gates-of-morning'),nil,'TW7 altered Gates palm stays native: '..m[1])
end
-- Scene: a Zigur plot with road and grass; Gates beach with a palm.
local zplan={'.__-','.-.-','t_--'}
local zsym={['.']='GRASS',_='GRASS_ROAD_STONE',t='TREE3'}
local fn=0
local zm=townMap(4,3,function(x,y)
 local c=zplan[y+1]:sub(x+1,x+1)
 if c=='-' then fn=fn%4+1;return field(zDefs,'FIELDS'..fn) end
 return zDefs[zsym[c]]
end)
local rules={}
for x=0,3 do for y=0,2 do local r={};for k,v in pairs(zm(x,y,1)) do r[k]=v end;rules[x+y*4]=r end end
env.game={zone={short_name='town-zigur'}}
local zh={zone={short_name='town-zigur'},level={map=zm,data={}}}
mode='refined';T.apply(zh)
local function zi(x,y) return zm(x,y,1).replace_display and zm(x,y,1).replace_display.image end
eq(zi(3,0),'checker-revised+refined/town/fields1.png','TW7 Zigur field is the board crop field')
eq(zi(1,1),'checker-revised+refined/town/fields0.png','TW7 field parity')
eq(zi(1,0),'checker-revised+refined/town/road1.png','TW7 Zigur road is board stone slabs')
eq(zi(2,0),'checker-revised+refined/town/road0.png','TW7 road parity')
eq(zi(0,0),'checker-revised+refined/grass0.png','TW7 Zigur grass unchanged')
eq(zm(3,0,1).replace_display.add_mos,nil,'TW7 native crop layer is not redrawn over the board field')
for x=0,3 do for y=0,2 do
 for k,v in pairs(rules[x+y*4]) do if k~='replace_display' and k~='_checker_terrain' then eq(zm(x,y,1)[k],v,'TW7 rule field unchanged '..x..','..y..' '..tostring(k)) end end
end end
mode='blockout';T.apply(zh)
eq(zi(3,0),'checker-revised+grass1.png','TW7 blockout field reads as walkable ground')
eq(zi(1,0),'checker-revised+road1.png','TW7 blockout road')
mode='vanilla';T.apply(zh)
for x=0,3 do for y=0,2 do eq(zm(x,y,1).replace_display,nil,'TW7 native mode restores Zigur '..x..','..y) end end
mode='refined';T.apply(zh)
eq(zi(3,0),'checker-revised+refined/town/fields1.png','TW7 refined restore field')
eq(zi(1,0),'checker-revised+refined/town/road1.png','TW7 refined restore road')
local gplan={'*p_','*p*'}
local gm=townMap(3,2,function(x,y)
 local c=gplan[y+1]:sub(x+1,x+1)
 if c=='p' then return gpalm(y==0 and 'PALMTREE13' or 'PALMTREE17',y==0 and 2 or 1) end
 return gDefs[c=='*' and 'SAND' or 'FLOOR_ROAD_STONE']
end)
env.game={zone={short_name='town-gates-of-morning'}}
local gh={zone={short_name='town-gates-of-morning'},level={map=gm,data={all_remembered=true}}}
mode='refined';T.apply(gh)
local function gi(x,y) return gm(x,y,1).replace_display and gm(x,y,1).replace_display.image end
eq(gi(1,0),'checker-revised+refined/eruan/palm-a1.png','TW7 Gates palm draws the S6 board palm')
eq(gi(1,1),'checker-revised+refined/eruan/palm-a0.png','TW7 Gates palm parity follows S6')
eq(gi(2,0),'checker-revised+refined/town/road0.png','TW7 Gates plaza road is board stone slabs')
eq(gi(0,0),'checker-revised+refined/beach/sand0.png','TW7 Gates sand unchanged')
eq(gm(1,0,1).does_block_move,true,'TW7 Gates palm still blocks movement')
eq(gm(1,0,1).block_sight,true,'TW7 Gates palm still blocks sight')
mode='blockout';T.apply(gh)
eq(gi(1,0),'checker-revised+tree1.png','TW7 blockout palm reads as blocking')
mode='vanilla';T.apply(gh)
for x=0,2 do for y=0,1 do eq(gm(x,y,1).replace_display,nil,'TW7 native mode restores Gates '..x..','..y) end end
-- Other zones keep the forest dirt road: South Beach and Old Forest style families.
local bh=townMap(1,1,function() return dDefs.GRASS_ROAD_STONE end)
local bc=bh(0,0,1);bc._checker_town_source=nil
env.game={zone={short_name='south-beach'}};mode='refined'
T.apply({zone={short_name='south-beach'},level={map=bh,data={}}})
eq(bh(0,0,1).replace_display and bh(0,0,1).replace_display.image,'checker-revised+refined/road0.png','TW7 South Beach road keeps the dirt road tile')
-- Old save: unstamped Zigur plot cells stay native.
local zo=townMap(2,1,function(x) local g=x==0 and field(zDefs,'FIELDS1') or deep(zDefs.GRASS_ROAD_STONE);g._checker_town_source=nil;return g end)
env.game={zone={short_name='town-zigur'}}
T.apply({zone={short_name='town-zigur'},level={map=zo,data={}}})
for x=0,1 do eq(zo(x,0,1).replace_display,nil,'TW7 old-save Zigur cell stays native '..x) end
env.game=sg;mode='refined'
end)()
-- S10a: Grushnak Pride L1-3, Slime Tunnels, Sludgenest L1-3. The new board
-- slime family (floor, wall masks, stairs, creep over board stone) and the
-- reused families (Kor'Pul stone incl. the SLIMED_* corner, gloom plain
-- thicket, Caldera jungle, training dummy prop). Every S10a cell needs its
-- zone list stamp and its defining file's stamp; callbacks stay native.
;(function()
local sg,savedStairs,savedDark=env.game,T.stairAssets,T.korpulDarkAssets
local gFile,sFile,nFile='/data/zones/grushnak-pride/grids.lua','/data/zones/slime-tunnels/grids.lua','/data/zones/sludgenest/grids.lua'
local gD,sD,nD=loadDefs(gFile),loadDefs(sFile),loadDefs(nFile)
T.stairAssets={ready=true,files=setmetatable({},{__index=function(_,k) return type(k)=='string' and k:match('^checker%-revised%+refined/korpul/stairs%-') and true or nil end})}
T.korpulDarkAssets={ready=true,files=setmetatable({},{__index=function(_,k) return type(k)=='string' and k:match('^checker%-revised%+refined/korpul%-dark/') and true or nil end})}
-- Stamps: general-file stamps survive the outer zone list stamp.
eq(sD.SLIME_WALL3._checker_slime_source.file,'/data/general/grids/slime.lua','S10a slime.lua stamps its wall variants')
eq(sD.SLIME_WALL3._checker_zone_source.file,sFile,'S10a Slime Tunnels list stamps nested slime.lua')
eq(nD.SLIME_FLOOR2._checker_zone_source.file,nFile,'S10a Sludgenest list stamps nested slime.lua')
eq(nD.JUNGLE_TREE7._checker_jungle_source.file,'/data/general/grids/jungle.lua','S10a Sludgenest jungle keeps its jungle.lua stamp')
eq(gD.UNDERGROUND_CREEP2._checker_slime_source.file,'/data/general/grids/underground_slimy.lua','S10a underground_slimy.lua stamp')
eq(gD.SLIMED_WALL_NORTH3._checker_slime_source.file,'/data/general/grids/slimy_walls.lua','S10a slimy_walls.lua stamp')
eq(gD.SLIMED_FLOOR.image,'terrain/underground_floor.png','S10a Grushnak rewrites the slimed floor image')
eq(gD.FLOOR.image,'terrain/underground_floor.png','S10a Grushnak rewrites basic.lua FLOOR image')
eq(gD.FLOOR._checker_grid_source.file,'/data/general/grids/basic.lua','S10a Grushnak FLOOR keeps its basic.lua stamp')
eq(gD.TRAINING_DUMMY._checker_zone_source.id,'TRAINING_DUMMY','S10a Grushnak list stamps its dummy')
eq(sD.UP_GRUSHNAK._checker_slime_source.id,'SLIME_UP','S10a UP_GRUSHNAK carries only the inherited SLIME_UP stamp')
-- Gating: Grushnak combines stone with the slime/underground cells; the
-- tunnels and the nest are forest-style families only.
eq(T.variant({short_name='grushnak-pride'}),'GRUSHNAK_PRIDE','S10a Grushnak stone gate')
eq(T.combined['grushnak-pride'],true,'S10a Grushnak combined')
for _,z in ipairs{'slime-tunnels','sludgenest'} do eq(T.variant({short_name=z}),nil,'S10a no stone variant '..z) end
local K=T.batch4Kind
local function kinds(defs,zone,list,label)
 for id,kind in pairs(list) do eq(K(methods.clone(assert(defs[id],id)),zone),kind,'S10a '..label..' '..id) end
end
kinds(sD,'slime-tunnels',{SLIME_FLOOR='slime-floor',SLIME_FLOOR4='slime-floor',SLIME_WALL='slime-wall',SLIME_WALL5='slime-wall',
 UP_GRUSHNAK='slime-up',SLIME_UP='slime-up',SLIME_DOWN='slime-down'},'tunnels')
kinds(nD,'sludgenest',{SLIME_FLOOR2='slime-floor',SLIME_WALL1='slime-wall',SLIME_UP='slime-up',SLIME_DOWN='slime-down',
 JUNGLE_GRASS='jungle-grass',JUNGLE_GRASS_PATCH3='jungle-grass',JUNGLE_TREE12='jungle-tree',JUNGLE_GRASS_UP_WILDERNESS='jungle-exit'},'nest')
kinds(gD,'grushnak-pride',{UNDERGROUND_FLOOR='under-floor',UNDERGROUND_FLOOR7='under-floor',UNDERGROUND_CREEP='creep',
 UNDERGROUND_CREEP3='creep',UNDERGROUND_TREE='thicket',UNDERGROUND_TREE9='thicket',TRAINING_DUMMY='dummy',SLIME_TUNNELS='slime-down'},'grushnak')
-- Callback cells, doors, unused and foreign definitions stay native.
for _,id in ipairs{'ORB_DRAGON','ORB_UNDEATH','ORB_ELEMENTS','ORB_DESTRUCTION','PEAK_STAIR','PEAK_STAIR_FAKE','FAKE_WALL','PEAK_DOOR',
 'SLIME_DOOR','SLIME_DOOR_HORIZ','SLIME_DOOR_VERT','SLIME_DOOR_OPEN','SLIME_DOOR_HORIZ_OPEN','SLIME_DOOR_OPEN_VERT','FLOOR','WALL'} do
 eq(K(methods.clone(sD[id]),'slime-tunnels'),nil,'S10a tunnels native '..id)
end
eq(K(methods.clone(nD.UP_GRUSHNAK),'sludgenest'),nil,'S10a Sludgenest\'s unused UP_GRUSHNAK (level 6) stays native')
eq(K(methods.clone(nD.PEAK_STAIR),'sludgenest'),nil,'S10a Sludgenest peak stair (callback) native')
for _,id in ipairs{'UNDERGROUND_HARDTREE','UNDERGROUND_HARDTREE4','UNDERGROUND_VAULT','UNDERGROUND_LADDER_DOWN','UNDERGROUND_LADDER_UP_WILDERNESS',
 'SLIMED_WALL','SLIMED_FLOOR','SLIMED_DOOR','FLOOR','WALL','HARDWALL','UP','DOWN','LAVA_FLOOR','DEEP_WATER','GRASS','TREE'} do
 if gD[id] then eq(K(methods.clone(gD[id]),'grushnak-pride'),nil,'S10a grushnak not a forest kind '..id) end
end
-- Zone scope: slime cells in Grushnak, underground cells elsewhere, and
-- every S10a cell outside its three zones stay native.
eq(K(methods.clone(sD.SLIME_FLOOR),'grushnak-pride'),nil,'S10a slime floor not claimed in Grushnak')
eq(K(methods.clone(gD.UNDERGROUND_CREEP),'slime-tunnels'),nil,'S10a creep not claimed in the tunnels')
eq(K(methods.clone(gD.TRAINING_DUMMY),'sludgenest'),nil,'S10a dummy not claimed outside Grushnak')
for _,z in ipairs{'infinite-dungeon','vor-pride','gorbat-pride','high-peak'} do
 eq(K(methods.clone(sD.SLIME_WALL),z),nil,'S10a slime wall ungated in '..z)
 eq(K(methods.clone(gD.UNDERGROUND_CREEP),z),nil,'S10a creep ungated in '..z)
end
-- Old save: without the zone list stamp or the general-file stamp, native.
for _,c in ipairs{{sD,'SLIME_WALL','slime-tunnels'},{sD,'UP_GRUSHNAK','slime-tunnels'},{nD,'JUNGLE_TREE3','sludgenest'},
 {gD,'UNDERGROUND_CREEP1','grushnak-pride'},{gD,'TRAINING_DUMMY','grushnak-pride'},{gD,'SLIME_TUNNELS','grushnak-pride'}} do
 local u=deep(c[1][c[2]]);u._checker_zone_source=nil
 eq(K(u,c[3]),nil,'S10a unstamped (old save) stays native '..c[2])
end
for _,c in ipairs{{sD,'SLIME_WALL','slime-tunnels'},{nD,'SLIME_DOWN','sludgenest'},{gD,'UNDERGROUND_TREE4','grushnak-pride'}} do
 local u=deep(c[1][c[2]]);u._checker_slime_source=nil
 eq(K(u,c[3]),nil,'S10a without the general-file stamp stays native '..c[2])
end
-- Native NicerTiles layers are accepted exactly; anything else is native.
local function withDisplays(g,list) g=deep(g);g.add_displays={};for i,d in ipairs(list) do g.add_displays[i]=setmetatable(d,meta) end;return g end
local wallEdge=withDisplays(sD.SLIME_WALL2,{{image='invis.png',add_mos={{image='terrain/slime/slime_edge_vertical_left_01.png',display_x=-0.03125}}},
 {image='terrain/slime/slime_wall_V2_top_01.png',z=18,display_y=-1},{image='terrain/slime/floor_wall_slime_02.png',display_y=1}})
wallEdge.image='terrain/slime/slime_wall_V2_8_01.png'
eq(K(wallEdge,'slime-tunnels'),'slime-wall','S10a slime wall with native slime_wall edges')
local creepEdge=withDisplays(gD.UNDERGROUND_CREEP4,{{image='invis.png',add_mos={{image='terrain/mushrooms/creep_slimy_mushrooms_2_01.png',display_y=-1},
 {image='terrain/mushrooms/creep_slimy_mushrooms_inner_7_01.png',display_x=-1,display_y=-1}}}})
eq(K(creepEdge,'grushnak-pride'),'creep','S10a creep with native slimy-creep borders')
local upEdge=withDisplays(sD.UP_GRUSHNAK,{{image='terrain/slime/slime_stairs_up_left_01.png'},
 {image='invis.png',add_mos={{image='terrain/mushrooms/creep_slimy_mushrooms_6_01.png',display_x=-1}}}})
eq(K(upEdge,'slime-tunnels'),'slime-up','S10a Grushnak exit with its native creep carrier')
local treeParts=withDisplays(gD.UNDERGROUND_TREE5,{{image='invis.png',z=3,add_mos={{image='terrain/mushrooms/slimy_mushroom_02_trunk.png'}}},
 {image='terrain/mushrooms/slimy_mushroom_02_head_02.png',z=16,display_y=-0.92,display_h=2}})
eq(K(treeParts,'grushnak-pride'),'thicket','S10a thicket with its native mushroom parts')
local deco=deep(gD.UNDERGROUND_FLOOR5);deco.add_mos={{image='terrain/mushrooms/deco_floor_slimy_mushroom_04.png'}}
eq(K(deco,'grushnak-pride'),'under-floor','S10a underground floor with its native floor mushroom')
for label,g in pairs{
 wallForeign=withDisplays(sD.SLIME_WALL2,{{image='terrain/granite_wall3.png',z=18,display_y=-1}}),
 wallMos=(function() local g=deep(sD.SLIME_WALL);g.add_mos={{image='terrain/slime/slime_edge_upper_left_01.png'}};return g end)(),
 creepSlimeCarrier=withDisplays(gD.UNDERGROUND_CREEP4,{{image='invis.png',add_mos={{image='terrain/slime/slime_edge_upper_left_01.png'}}}}),
 creepDisplay=withDisplays(gD.UNDERGROUND_CREEP4,{{image='terrain/mushrooms/creep_slimy_mushrooms_2_01.png'}}),
 creepCarrierZ=withDisplays(gD.UNDERGROUND_CREEP4,{{image='invis.png',z=3,add_mos={{image='terrain/mushrooms/creep_slimy_mushrooms_2_01.png'}}}}),
 upNoStairs=withDisplays(sD.UP_GRUSHNAK,{{image='invis.png',add_mos={{image='terrain/mushrooms/creep_slimy_mushrooms_6_01.png'}}}}),
 upWrongStairs=withDisplays(sD.SLIME_UP,{{image='terrain/slime/slime_stair_down_01.png'}}),
 upStairsZ=withDisplays(sD.SLIME_UP,{{image='terrain/slime/slime_stairs_up_left_01.png',z=5}}),
 treeForeign=withDisplays(gD.UNDERGROUND_TREE5,{{image='terrain/trees/oak_01.png',z=16}}),
 decoTwo=(function() local g=deep(gD.UNDERGROUND_FLOOR5);g.add_mos={{image='terrain/mushrooms/deco_floor_slimy_mushroom_04.png'},{image='terrain/mushrooms/deco_floor_slimy_mushroom_05.png'}};return g end)(),
 decoShift=(function() local g=deep(gD.UNDERGROUND_FLOOR5);g.add_mos={{image='terrain/mushrooms/deco_floor_slimy_mushroom_04.png',display_y=-1}};return g end)(),
 floorStairs=withDisplays(gD.UNDERGROUND_FLOOR7,{{image='terrain/stair_down.png',z=5}}),
 dummyTwo=withDisplays(gD.TRAINING_DUMMY,{{image='npc/lure.png',z=9},{image='npc/lure.png',z=10}}),
 dummyZ=withDisplays(gD.TRAINING_DUMMY,{{image='npc/lure.png',z=18}}),
} do eq(K(g,label:match('^up') and 'slime-tunnels' or label:match('^wall') and 'slime-tunnels' or 'grushnak-pride'),nil,'S10a foreign layer stays native: '..label) end
-- One changed rule field or a callback keeps each kind native.
local mutations={
 stand=function(g) g.on_stand=function() end end, bump=function(g) g.block_move=function() end end,
 move=function(g) g.on_move=function() end end, special=function(g) g.special=true end, shader=function(g) g.shader='water' end,
 level=function(g) g.change_level=(g.change_level or 0)+1 end, zone=function(g) g.change_zone='wilderness' end,
 check=function(g) g.change_level_check=function() return true end end, name=function(g) g.name='x' end,
 display=function(g) g.display='?' end, image=function(g) g.image='terrain/marble_floor.png' end,
 blockmove=function(g) g.does_block_move=not g.does_block_move or nil end, sight=function(g) g.block_sight=not g.block_sight or nil end,
 sense=function(g) g.block_sense=true end, air=function(g) g.air_level=(g.air_level or 0)-5 end,
 dig=function(g) g.dig=g.dig and 'FLOOR' or 'SLIME_FLOOR' end, canpass=function(g) g.can_pass=g.can_pass or {};g.can_pass.pass_void=1 end,
 door=function(g) g.is_door=true end, subtype=function(g) g.subtype='floor' end, type=function(g) g.type=g.type=='wall' and 'floor' or 'wall' end,
 grow=function(g) g.grow='WALL' end, remember=function(g) g.always_remember=not g.always_remember or nil end,
 projectile=function(g) g.pass_projectile=not g.pass_projectile or nil end, z=function(g) g.z=7 end,
 abs=function(g) g.change_level_abs=true end,
}
for _,c in ipairs{{sD,'SLIME_FLOOR3','slime-tunnels'},{sD,'SLIME_WALL4','slime-tunnels'},{sD,'UP_GRUSHNAK','slime-tunnels'},
 {nD,'SLIME_DOWN','sludgenest'},{gD,'UNDERGROUND_FLOOR3','grushnak-pride'},{gD,'UNDERGROUND_CREEP5','grushnak-pride'},
 {gD,'UNDERGROUND_TREE12','grushnak-pride'},{gD,'TRAINING_DUMMY','grushnak-pride'},{gD,'SLIME_TUNNELS','grushnak-pride'}} do
 local base=K(methods.clone(c[1][c[2]]),c[3])
 assert(base,c[2])
 for label,mut in pairs(mutations) do
  local g=deep(c[1][c[2]]);mut(g)
  eq(K(g,c[3]),nil,'S10a altered '..c[2]..' stays native: '..label)
 end
end
-- Stone adapter in Grushnak: basic.lua with the rewritten base image, and
-- the SLIMED_* corner as stone kinds.
env.game={zone={short_name='grushnak-pride'}}
for id,kind in pairs{FLOOR='floor',WALL='wall',WALL_NORTH3='wall',HARDWALL='hardwall',DOOR='door-closed',DOOR_OPEN='door-open',
 UP='stairs-up',DOWN='stairs-down',UP_WILDERNESS='stairs-world',SLIMED_FLOOR='floor',SLIMED_WALL='wall',SLIMED_WALL3='wall',
 SLIMED_WALL_NORTH2='wall',SLIMED_WALL_SOUTH12='wall',SLIMED_WALL_NORTH_SOUTH='wall',SLIMED_WALL_PILLAR_6='wall',SLIMED_WALL_SMALL_PILLAR='wall',
 SLIMED_HARDWALL='hardwall',SLIMED_HARDWALL_PILLAR_85='hardwall',SLIMED_DOOR='door-closed',SLIMED_DOOR_HORIZ='door-closed',
 SLIMED_DOOR_VERT='door-closed',SLIMED_DOOR_OPEN='door-open',SLIMED_DOOR_HORIZ_OPEN='door-open',SLIMED_DOOR_OPEN_VERT='door-open'} do
 eq(T.classify(methods.clone(assert(gD[id],id))),kind,'S10a Grushnak stone '..id)
 local u=deep(gD[id]);u._checker_zone_source=nil
 eq(T.classify(u),nil,'S10a Grushnak stone without the list stamp stays native '..id)
end
eq(select(2,T.classify(methods.clone(gD.SLIMED_DOOR_VERT))),'vertical','S10a slimed vertical door orientation')
eq(select(2,T.classify(methods.clone(gD.SLIMED_DOOR_HORIZ_OPEN))),'horizontal','S10a slimed open door orientation')
for _,id in ipairs{'SLIMED_DOOR_VAULT','SLIMED_DOOR_VAULT_VERT','SLIMED_GENERIC_LEVER_DOOR','SLIMED_GENERIC_LEVER_DOOR_HORIZ',
 'SLIMED_GENERIC_LEVER_DOOR_OPEN','SLIMED_GENERIC_LEVER','SLIMED_GENERIC_TRIGGER_BOOL','SLIMED_UP','SLIMED_DOWN','SLIMED_UP_WILDERNESS',
 'SLIMED_FLAT_UP8','TRAINING_DUMMY','SLIME_TUNNELS','UNDERGROUND_FLOOR','UNDERGROUND_CREEP','UNDERGROUND_TREE'} do
 if gD[id] then eq(T.classify(methods.clone(gD[id])),nil,'S10a Grushnak not a stone kind '..id) end
end
for label,c in pairs{
 dig=function(g) g.dig='FLOOR' end, pass=function(g) g.can_pass.pass_void=1 end, sense=function(g) g.block_sense=true end,
 image=function(g) g.image='terrain/granite_wall1.png' end, layer=function(g) g.add_displays={setmetatable({image='terrain/granite_wall3.png',z=18,display_y=-1},meta)} end,
 mos=function(g) g.add_mos={{image='terrain/slimed_walls/granite_wall3.png'}} end, stand=function(g) g.on_stand=function() end end,
 air=function(g) g.air_level=-10 end, notice=function(g) g.notice=true end, unslimed=function(g) g._checker_slime_source=nil end,
} do local g=deep(gD.SLIMED_WALL2);c(g);eq(T.classify(g),nil,'S10a altered slimed wall stays native: '..label) end
for label,c in pairs{
 opened=function(g) g.door_opened='SLIMED_DOOR_OPEN' end, dig=function(g) g.dig='SLIMED_FLOOR' end, sight=function(g) g.block_sight=nil end,
 check=function(g) g.door_player_check='x' end, stop=function(g) g.door_player_stop='x' end, notice=function(g) g.notice=nil end,
 move=function(g) g.does_block_move=true end,
} do local g=deep(gD.SLIMED_DOOR_VERT);c(g);eq(T.classify(g),nil,'S10a altered slimed door stays native: '..label) end
-- The rewritten stairs base is accepted only in Grushnak.
env.game={zone={short_name='dreadfell'}}
for _,id in ipairs{'UP','DOWN','SLIMED_WALL','SLIMED_FLOOR'} do eq(T.classify(methods.clone(gD[id])),nil,'S10a Grushnak copy not claimed in Dreadfell '..id) end
-- Scene: Slime Tunnels. Refined -> Blockout -> Native -> Refined; rules unchanged.
local function scene(zone,defs,plan,sym)
 local m=townMap(#plan[1],#plan,function(x,y) return assert(defs[sym[plan[y+1]:sub(x+1,x+1)]],plan[y+1]:sub(x+1,x+1)) end)
 local rules={}
 for x=0,m.w-1 do for y=0,m.h-1 do local r={};for key,v in pairs(m(x,y,1)) do r[key]=v end;rules[x+y*m.w]=r end end
 local h={zone={short_name=zone},level={map=m,data={}}}
 return m,h,rules
end
local function img(m,x,y) local g=m(x,y,1);return g.replace_display and g.replace_display.image end
local function sameRules(m,rules,label)
 for x=0,m.w-1 do for y=0,m.h-1 do
  for key,v in pairs(rules[x+y*m.w]) do if key~='replace_display' and key~='_checker_terrain' then eq(m(x,y,1)[key],v,label..' rule '..tostring(key)) end end
 end end
end
local sm,sh,srules=scene('slime-tunnels',sD,{'###','.<.','#&.'},{['#']='SLIME_WALL2',['.']='SLIME_FLOOR3',['<']='UP_GRUSHNAK',['&']='ORB_DRAGON'})
env.game={zone=sh.zone};mode='refined';T.apply(sh)
eq(img(sm,0,0),'checker-revised+refined/slime/wall-2-0.png','S10a slime wall joins east only')
eq(img(sm,1,0),'checker-revised+refined/slime/wall-10-1.png','S10a slime wall joins east and west')
eq(img(sm,0,1),'checker-revised+refined/slime/floor1.png','S10a slime floor')
eq(img(sm,1,1),'checker-revised+refined/slime/stairs-up0.png','S10a Grushnak exit on board slime stairs')
eq(img(sm,0,2),'checker-revised+refined/slime/wall-0-0.png','S10a lone slime wall')
eq(img(sm,1,2),nil,'S10a orb pedestal (callback) stays native')
eq(sm(1,1,1).change_zone,'grushnak-pride','S10a exit still leads to Grushnak')
sameRules(sm,srules,'S10a tunnels')
mode='blockout';T.apply(sh)
eq(img(sm,0,0),'checker-revised+tree0.png','S10a blockout slime wall blocks')
eq(img(sm,1,1),'checker-revised+exit0.png','S10a blockout slime stairs exit')
mode='vanilla';T.apply(sh)
for x=0,2 do for y=0,2 do eq(sm(x,y,1).replace_display,nil,'S10a native mode restores tunnels '..x..','..y) end end
mode='refined';T.apply(sh)
eq(img(sm,1,0),'checker-revised+refined/slime/wall-10-1.png','S10a refined restore slime wall')
sameRules(sm,srules,'S10a tunnels after toggles')
-- Scene: Sludgenest L1: jungle rim beside the slime lake; masks per family.
local nm,nh,nrules=scene('sludgenest',nD,{'T#.','g#>','gGT'},{T='JUNGLE_TREE4',['#']='SLIME_WALL',['.']='SLIME_FLOOR1',['>']='SLIME_DOWN',
 g='JUNGLE_GRASS',G='JUNGLE_GRASS_UP_WILDERNESS'})
env.game={zone=nh.zone};T.apply(nh)
eq(img(nm,1,0),'checker-revised+refined/slime/wall-4-1.png','S10a slime wall ignores the jungle tree beside it')
eq(img(nm,1,1),'checker-revised+refined/slime/wall-1-0.png','S10a slime wall joins north')
eq(img(nm,0,0),'checker-revised+refined/caldera/tree-a0.png','S10a Sludgenest jungle tree on Caldera art')
eq(img(nm,0,1),'checker-revised+refined/caldera/floor1.png','S10a Sludgenest jungle grass on Caldera art')
eq(img(nm,1,2),'checker-revised+refined/caldera/exit-world1.png','S10a Sludgenest world exit')
eq(img(nm,2,1),'checker-revised+refined/slime/stairs-down1.png','S10a Sludgenest slime stairs down')
eq(img(nm,2,0),'checker-revised+refined/slime/floor0.png','S10a Sludgenest slime floor')
sameRules(nm,nrules,'S10a nest')
-- Sludgenest's on_turn turns a wall into fresh slime floor and re-tiles
-- around it (NicerTiles:updateAround -> repair): the board follows.
nm(1,1,1,methods.clone(nD.SLIME_FLOOR2))
nm.updateMap=function() end;T.repair(nh,0,0,2,2)
eq(img(nm,1,1),'checker-revised+refined/slime/floor0.png','S10a spawned slime floor gets the board floor')
eq(img(nm,1,0),'checker-revised+refined/slime/wall-0-1.png','S10a neighbour wall mask follows the new floor')
-- Scene: Grushnak's slime pit and barracks edge (combined zone).
local gm,gh,grules=scene('grushnak-pride',gD,{'TT;;','T;>;','.t;T'},{T='UNDERGROUND_TREE3',[';']='UNDERGROUND_CREEP2',['>']='SLIME_TUNNELS',
 ['.']='UNDERGROUND_FLOOR4',t='TRAINING_DUMMY'})
env.game={zone=gh.zone};T.apply(gh)
eq(img(gm,0,0),'checker-revised+refined/gloom/plain/wall-6-0.png','S10a thicket joins east and south')
eq(img(gm,2,0),'checker-revised+refined/slime/creep-6-0.png','S10a creep joins creep east and the slime stairs south')
eq(img(gm,1,1),'checker-revised+refined/slime/creep-2-0.png','S10a creep joins only the slime stairs east')
eq(img(gm,2,1),'checker-revised+refined/slime/stairs-down1.png','S10a slime pit entrance is board slime stairs')
eq(img(gm,0,2),'checker-revised+refined/korpul/floor-a-0-0.png','S10a underground floor is the board stone floor')
eq(img(gm,1,2),'checker-revised+refined/korpul/floor-a-0-1.png','S10a dummy stands on the board stone floor')
local dl=gm(1,2,1).replace_display.add_displays
eq(dl and #dl==1 and dl[1].image,'npc/lure.png','S10a dummy keeps its native lure layer')
eq(dl[1].z,9,'S10a dummy layer keeps its z')
eq(gm(1,2,1).does_block_move,true,'S10a dummy still blocks movement')
eq(gm(1,2,1).pass_projectile,true,'S10a dummy still passes projectiles')
eq(gm(2,1,1).change_zone,'slime-tunnels','S10a pit entrance still leads to the tunnels')
sameRules(gm,grules,'S10a grushnak pit')
mode='vanilla';T.apply(gh)
for x=0,3 do for y=0,2 do eq(gm(x,y,1).replace_display,nil,'S10a native mode restores Grushnak '..x..','..y) end end
mode='refined';T.apply(gh)
eq(img(gm,1,2),'checker-revised+refined/korpul/floor-a-0-1.png','S10a refined restore Grushnak dummy')
-- Stone adapter: a SLIMED wall joins the basic.lua wall beside it (dark brick).
local bm=townMap(3,2,function(x,y) return gD[({{'WALL','SLIMED_WALL','SLIMED_WALL'},{'FLOOR','SLIMED_FLOOR','UP'}})[y+1][x+1]] end)
for x=0,2 do for y=0,1 do bm.seen[x+y*3]=true end end
for x=0,2 do for y=0,1 do T.observe(bm,x,y,bm(x,y,1)) end end
eq(T.render(bm,0,0,bm(0,0,1),'refined').image,'checker-revised+refined/korpul-dark/wall-2-0.png','S10a basic wall joins the slimed wall east')
eq(T.render(bm,1,0,bm(1,0,1),'refined').image,'checker-revised+refined/korpul-dark/wall-10-1.png','S10a slimed wall joins both sides')
eq(T.render(bm,1,1,bm(1,1,1),'refined').image,'checker-revised+refined/korpul/floor-b-0-0.png','S10a slimed floor is the board stone floor')
eq(T.render(bm,2,1,bm(2,1,1),'refined').image,'checker-revised+refined/korpul/floor-a-0-1.png','S10a Grushnak stairs on the board floor')
-- Old save: unstamped cells on every S10a family stay native.
local om=townMap(3,1,function(x) local g=deep(({sD.SLIME_WALL,sD.SLIME_FLOOR,sD.UP_GRUSHNAK})[x+1]);g._checker_zone_source=nil;return g end)
env.game={zone={short_name='slime-tunnels'}};T.apply({zone={short_name='slime-tunnels'},level={map=om,data={}}})
for x=0,2 do eq(om(x,0,1).replace_display,nil,'S10a old-save tunnel cell stays native '..x) end
T.stairAssets,T.korpulDarkAssets=savedStairs,savedDark
env.game=sg;mode='refined'
end)()
T.assets=savedAssets;env.game=savedGame

-- S10b: Vor Pride L1-3. The new board gothic family (floor variants, wall
-- masks incl. pillars, four door states, flat exits, books) and the reused
-- families (Spellblaze burnt ground/trees and exit-down for basic.lua
-- FLAT_DOWN4, deep water/grass/trees, Kor'Pul stone for the vault). Every
-- S10b cell needs the Vor list stamp, gothic cells the gothic.lua stamp;
-- levers, lever doors, sealed doors and candles stay native.
;(function()
local sg=env.game
local vFile,gothic='/data/zones/vor-pride/grids.lua','/data/general/grids/gothic.lua'
-- ToME's string:prefix (engine utils), used by Vor's import rewrite.
local savedPrefix=string.prefix
string.prefix=function(str,pre) return str:sub(1,#pre)==pre end
local vD=loadDefs(vFile)
local rD=loadDefs(gothic)
-- Stamps: the gothic.lua stamp survives the outer zone list stamp; Vor's
-- import rewrite is visible in the definitions the contract pins.
eq(vD.GOTHIC_WALL3._checker_gothic_source.file,gothic,'S10b gothic.lua stamps its walls')
eq(vD.GOTHIC_WALL3._checker_zone_source.file,vFile,'S10b Vor list stamps nested gothic.lua')
eq(vD.BURNT_TREE7._checker_burnt_source.file,'/data/general/grids/burntland.lua','S10b Vor burnt tree keeps its burntland stamp')
eq(vD.BURNT_TREE7._checker_zone_source.file,vFile,'S10b Vor list stamps nested burntland.lua')
eq(vD.FLAT_DOWN4._checker_grid_source.file,'/data/general/grids/basic.lua','S10b Vor FLAT_DOWN4 keeps its basic.lua stamp')
eq(vD.GENERIC_BOOK2._checker_zone_source.id,'GENERIC_BOOK2','S10b Vor list stamps its own books')
eq(vD.GENERIC_BOOK2._checker_gothic_source,nil,'S10b books are not gothic.lua definitions')
eq(vD.GOTHIC_DOOR_VERT.image,'terrain/grass_burnt1.png','S10b Vor rewrites the vertical door base')
eq(vD.GOTHIC_WALL_SMALL_PILLAR.image,'terrain/grass_burnt1.png','S10b Vor rewrites the pillar base')
eq(vD.GOTHIC_FLOOR.image,'terrain/gothic_walls/marble_floor.png','S10b Vor keeps the gothic floor image')
eq(vD.GOTHIC_FLAT_UP6.image,'terrain/gothic_walls/marble_floor.png','S10b Vor keeps the flat exit base')
eq(rD.GOTHIC_WALL._checker_zone_source,nil,'S10b a bare gothic.lua list carries no Vor stamp')
-- Gating.
eq(T.variant({short_name='vor-pride'}),'VOR_PRIDE','S10b Vor stone gate')
eq(T.combined['vor-pride'],true,'S10b Vor combines the gothic family and stone')
local K=T.batch4Kind
local kinds={GOTHIC_FLOOR='gothic-floor',GOTHIC_WALL='gothic-wall',GOTHIC_WALL3='gothic-wall',GOTHIC_WALL_NORTH2='gothic-wall',
 GOTHIC_WALL_PILLAR_84='gothic-wall',GOTHIC_WALL_NORTH_SOUTH='gothic-wall',GOTHIC_WALL_SOUTH='gothic-wall',GOTHIC_WALL_SOUTH12='gothic-wall',
 GOTHIC_WALL_SOUTH17='gothic-wall',GOTHIC_WALL_SMALL_PILLAR='gothic-wall',GOTHIC_WALL_PILLAR_2='gothic-wall',GOTHIC_WALL_PILLAR_4='gothic-wall',
 GOTHIC_WALL_PILLAR_6='gothic-wall',GOTHIC_DOOR='gothic-door-closed',GOTHIC_DOOR_HORIZ='gothic-door-closed-h',
 GOTHIC_DOOR_VERT='gothic-door-closed-v',GOTHIC_DOOR_OPEN='gothic-door-open',GOTHIC_DOOR_HORIZ_OPEN='gothic-door-open-h',
 GOTHIC_DOOR_OPEN_VERT='gothic-door-open-v',GOTHIC_FLAT_UP_WILDERNESS='gothic-exit-world',GOTHIC_FLAT_UP6='gothic-exit-up',
 GOTHIC_FLAT_UP2='gothic-exit-up',GOTHIC_FLAT_DOWN4='gothic-exit-down',GOTHIC_FLAT_DOWN8='gothic-exit-down',
 GENERIC_BOOK1='gothic-book',GENERIC_BOOK2='gothic-book',GENERIC_BOOK3='gothic-book',BURNT_GROUND='burnt-floor',
 BURNT_GROUND3='burnt-floor',BURNT_TREE='burnt-tree',BURNT_TREE7='burnt-tree',FLAT_DOWN4='burnt-exit-down',DEEP_WATER='deep',
 TREE3='tree',GRASS='grass'}
for id,kind in pairs(kinds) do eq(K(methods.clone(assert(vD[id],id)),'vor-pride'),kind,'S10b Vor '..id) end
eq(select(2,T.townProp(methods.clone(vD.GENERIC_BOOK3),'vor-pride')).image,'terrain/book_generic3.png','S10b book keeps its native layer')
-- Callback, prompt, particle, unused and foreign definitions stay native.
-- S11: the lever, tiled lever doors and CANDLE1-3 are exact S11 cells (tests/terrain_s11.lua).
for _,id in ipairs{'GOTHIC_GENERIC_LEVER_DOOR',
 'GOTHIC_GENERIC_LEVER_DOOR_OPEN','GOTHIC_GENERIC_TRIGGER_BOOL',
 'GOTHIC_DOOR_VAULT','GOTHIC_DOOR_VAULT_HORIZ','GOTHIC_DOOR_VAULT_VERT','CANDLE','GOTHIC_HARDWALL','GOTHIC_HARDWALL3',
 'GOTHIC_HARDWALL_NORTH2','GOTHIC_HARDWALL_SMALL_PILLAR','GOTHIC_UP','GOTHIC_DOWN','GOTHIC_UP_WILDERNESS','FLOOR','WALL','HARDWALL','DOOR',
 'UP','DOWN','FLAT_UP6','FLAT_DOWN6','FLAT_UP_WILDERNESS','BURNT_UP4','BURNT_DOWN6','BURNT_UP_WILDERNESS','POISON_DEEP_WATER'} do
 if vD[id] then eq(K(methods.clone(vD[id]),'vor-pride'),nil,'S10b Vor native '..id) end
end
-- Zone scope: gothic cells and Vor's reused cells outside Vor stay native.
for _,z in ipairs{'rak-shor-pride','grushnak-pride','infinite-dungeon','gorbat-pride','high-peak','vor-armoury'} do
 for _,id in ipairs{'GOTHIC_FLOOR','GOTHIC_WALL3','GOTHIC_DOOR_VERT','GOTHIC_FLAT_UP6','GENERIC_BOOK1','FLAT_DOWN4','BURNT_TREE7'} do
  eq(K(methods.clone(vD[id]),z),nil,'S10b Vor cell ungated in '..z..' '..id)
 end
end
for _,id in ipairs{'GOTHIC_FLOOR','GOTHIC_WALL3','GOTHIC_DOOR_HORIZ'} do eq(K(methods.clone(rD[id]),'vor-pride'),nil,'S10b bare gothic.lua (no Vor stamp) native '..id) end
-- Old save: without the Vor list stamp, or a gothic cell without its file stamp.
for _,id in ipairs{'GOTHIC_FLOOR','GOTHIC_WALL_NORTH3','GOTHIC_DOOR_VERT','GOTHIC_FLAT_UP_WILDERNESS','GENERIC_BOOK2','BURNT_GROUND2',
 'BURNT_TREE12','FLAT_DOWN4','DEEP_WATER'} do
 local u=deep(vD[id]);u._checker_zone_source=nil
 eq(K(u,'vor-pride'),nil,'S10b unstamped (old save) stays native '..id)
end
for _,id in ipairs{'GOTHIC_FLOOR','GOTHIC_WALL_PILLAR_6','GOTHIC_DOOR_OPEN_VERT','GOTHIC_FLAT_DOWN2'} do
 local u=deep(vD[id]);u._checker_gothic_source=nil
 eq(K(u,'vor-pride'),nil,'S10b without the gothic.lua stamp stays native '..id)
end
local u=deep(vD.FLAT_DOWN4);u._checker_grid_source=nil
eq(K(u,'vor-pride'),nil,'S10b FLAT_DOWN4 without its basic.lua stamp stays native')
-- Exact native layers; anything else is native.
local function withDisplays(g,list) g=deep(g);g.add_displays={};for i,d in ipairs(list) do g.add_displays[i]=setmetatable(d,meta) end;return g end
for label,c in pairs{
 wallExtra={'GOTHIC_WALL_NORTH3',{{image='terrain/gothic_walls/granite_wall3.png',z=18,display_y=-1},{image='terrain/gothic_walls/granite_wall3.png',z=18,display_y=-1}}},
 wallZ={'GOTHIC_WALL_NORTH3',{{image='terrain/gothic_walls/granite_wall3.png',z=17,display_y=-1}}},
 wallY={'GOTHIC_WALL_NORTH3',{{image='terrain/gothic_walls/granite_wall3.png',z=18,display_y=-2}}},
 wallX={'GOTHIC_WALL_NORTH3',{{image='terrain/gothic_walls/granite_wall3.png',z=18,display_y=-1,display_x=0.5}}},
 wallForeign={'GOTHIC_WALL_NORTH3',{{image='terrain/granite_wall3.png',z=18,display_y=-1}}},
 plainWallTop={'GOTHIC_WALL3',{{image='terrain/gothic_walls/granite_wall3.png',z=18,display_y=-1}}},
 pillarMissing={'GOTHIC_WALL_SMALL_PILLAR',{{image='terrain/gothic_walls/granite_wall_pillar_small.png',z=3}}},
 pillarSwap={'GOTHIC_WALL_PILLAR_6',{{image='terrain/gothic_walls/granite_wall_pillar_1.png',z=3},{image='terrain/gothic_walls/granite_wall_pillar_7.png',z=18,display_y=-1}}},
 doorPadlock={'GOTHIC_DOOR_VERT',{{image='terrain/gothic_walls/granite_door1_vert.png',z=17,add_mos={{image='terrain/padlock2.png'}}},
  {image='terrain/gothic_walls/granite_door1_vert_north.png',z=18,display_y=-1}}},
 floorEvent={'GOTHIC_FLOOR',{{image='terrain/stair_down.png',z=5},{z=17}}},
 floorPortal={'GOTHIC_FLOOR',{{image='terrain/demon_portal3.png'},{z=17}}},
 burntChest={'BURNT_GROUND',{{image='object/chest3.png',z=5}}},
 exitLayer={'GOTHIC_FLAT_UP6',{{image='terrain/gothic_walls/granite_wall3.png',z=18,display_y=-1}}},
 bookLayer={'GENERIC_BOOK1',{{image='terrain/book_generic1.png',z=5}}},
 flatLayer={'FLAT_DOWN4',{{image='invis.png',add_mos={{image='terrain/marble_water/marble_floor_2_to_water_outer_1.png'}}}}},
} do eq(K(withDisplays(vD[c[1]],c[2]),'vor-pride'),nil,'S10b foreign layer stays native: '..label) end
for label,c in pairs{
 floorMos={'GOTHIC_FLOOR',{{image='terrain/book_generic1.png'}}},
 exitTwo={'GOTHIC_FLAT_UP6',{{image='terrain/way_next_6.png'},{image='terrain/way_next_4.png'}}},
 exitWrong={'GOTHIC_FLAT_UP6',{{image='terrain/way_next_4.png'}}},
 exitShift={'GOTHIC_FLAT_UP6',{{image='terrain/way_next_6.png',display_y=-1}}},
 bookWrong={'GENERIC_BOOK1',{{image='terrain/book_generic2.png'}}},
 flatWrong={'FLAT_DOWN4',{{image='terrain/way_next_6.png'}}},
 wallMos={'GOTHIC_WALL3',{{image='terrain/gothic_walls/granite_wall3.png'}}},
} do local g=deep(vD[c[1]]);g.add_mos=c[2];eq(K(g,'vor-pride'),nil,'S10b foreign MO stays native: '..label) end
-- One changed rule field or a callback keeps each kind native.
local mutations={
 stand=function(g) g.on_stand=function() end end, bump=function(g) g.block_move=function() end end,
 move=function(g) g.on_move=function() end end, special=function(g) g.special=true end, shader=function(g) g.shader='water' end,
 level=function(g) g.change_level=(g.change_level or 0)+1 end, zone=function(g) g.change_zone='wilderness-x' end,
 check=function(g) g.change_level_check=function() return true end end, name=function(g) g.name='x' end,
 display=function(g) g.display='?' end, image=function(g) g.image='terrain/foreign.png' end,
 blockmove=function(g) g.does_block_move=not g.does_block_move or nil end, sight=function(g) g.block_sight=not g.block_sight or nil end,
 sense=function(g) g.block_sense=true end, esp=function(g) g.block_esp=true end, air=function(g) g.air_level=(g.air_level or 0)-5 end,
 dig=function(g) g.dig=g.dig and 'FLOOR' or 'GOTHIC_FLOOR' end, canpass=function(g) g.can_pass=g.can_pass and deep(g.can_pass) or {};g.can_pass.pass_void=1 end,
 door=function(g) g.is_door=not g.is_door or nil end, subtype=function(g) g.subtype='x' end, type=function(g) g.type=g.type=='wall' and 'floor' or 'wall' end,
 grow=function(g) g.grow='WALL' end, remember=function(g) g.always_remember=not g.always_remember or nil end,
 notice=function(g) g.notice=not g.notice or nil end, projectile=function(g) g.pass_projectile=not g.pass_projectile or nil end,
 z=function(g) g.z=7 end, abs=function(g) g.change_level_abs=true end, down=function(g) g.force_down=true end,
 opened=function(g) g.door_opened='X' end, closed=function(g) g.door_closed='X' end, prompt=function(g) g.door_player_check='x' end,
 stop=function(g) g.door_player_stop='x' end, particles=function(g) g.embed_particles={{name='candle'}} end, tint=function(g) g.tint={} end,
}
for _,id in ipairs{'GOTHIC_FLOOR','GOTHIC_WALL_NORTH3','GOTHIC_WALL_SOUTH9','GOTHIC_WALL_SMALL_PILLAR','GOTHIC_WALL_PILLAR_4','GOTHIC_DOOR',
 'GOTHIC_DOOR_HORIZ','GOTHIC_DOOR_VERT','GOTHIC_DOOR_OPEN','GOTHIC_DOOR_HORIZ_OPEN','GOTHIC_DOOR_OPEN_VERT','GOTHIC_FLAT_UP_WILDERNESS',
 'GOTHIC_FLAT_UP6','GOTHIC_FLAT_DOWN4','GENERIC_BOOK2','FLAT_DOWN4'} do
 assert(K(methods.clone(vD[id]),'vor-pride'),id)
 for label,mut in pairs(mutations) do
  local g=deep(vD[id]);mut(g)
  eq(K(g,'vor-pride'),nil,'S10b altered '..id..' stays native: '..label)
 end
end
-- Stone adapter in Vor: basic.lua stone of the vault needs the list stamp;
-- gothic cells are never stone kinds.
env.game={zone={short_name='vor-pride'}}
for id,kind in pairs{HARDWALL='hardwall',WALL='wall',FLOOR='floor',DOOR='door-closed',DOOR_OPEN='door-open',DOOR_VAULT='door-closed'} do
 eq(T.classify(methods.clone(vD[id])),kind,'S10b Vor vault stone '..id)
 local v=deep(vD[id]);v._checker_zone_source=nil
 eq(T.classify(v),nil,'S10b Vor stone without the list stamp stays native '..id)
end
for _,id in ipairs{'GOTHIC_FLOOR','GOTHIC_WALL','GOTHIC_WALL_NORTH2','GOTHIC_DOOR_VERT','GOTHIC_FLAT_UP6','GENERIC_BOOK1','BURNT_GROUND'} do
 eq(T.classify(methods.clone(vD[id])),nil,'S10b Vor not a stone kind '..id)
end
-- Scene: a hall with a lever door, pillar, books, a candle and the burnt yard.
local plan={'#####L#','#.o.+.#','#B.C#..','#|##-.<',';T;>;.W','E;;;;;;'}
local sym={['#']='GOTHIC_WALL_NORTH2',['.']='GOTHIC_FLOOR',o='GOTHIC_WALL_SMALL_PILLAR',['+']='GOTHIC_DOOR_VERT',['|']='GOTHIC_DOOR_OPEN_VERT',
 ['-']='GOTHIC_DOOR_HORIZ',L='GOTHIC_GENERIC_LEVER_DOOR_VERT',B='GENERIC_BOOK2',C='CANDLE1',[';']='BURNT_GROUND',T='BURNT_TREE4',['>']='FLAT_DOWN4',
 ['<']='GOTHIC_FLAT_UP6',W='GOTHIC_FLAT_UP_WILDERNESS',E='GOTHIC_GENERIC_LEVER'}
local vm=townMap(#plan[1],#plan,function(x,y) return assert(vD[sym[plan[y+1]:sub(x+1,x+1)]],plan[y+1]:sub(x+1,x+1)) end)
local rules={}
for x=0,vm.w-1 do for y=0,vm.h-1 do local r={};for key,v in pairs(vm(x,y,1)) do r[key]=v end;rules[x+y*vm.w]=r end end
local vh={zone={short_name='vor-pride'},level={map=vm,data={}}}
local function img(x,y) local g=vm(x,y,1);return g.replace_display and g.replace_display.image end
local function sameRules(label)
 for x=0,vm.w-1 do for y=0,vm.h-1 do
  for key,v in pairs(rules[x+y*vm.w]) do if key~='replace_display' and key~='_checker_terrain' then eq(vm(x,y,1)[key],v,label..' rule '..tostring(key)) end end
 end end
end
local G='checker-revised+refined/gothic/'
local function floorImg(x,y) return G..'floor-'..({'a','b','c'})[((x*17+y*7)%3)+1]..((x+y)%2)..'.png' end
mode='refined';T.apply(vh)
eq(vh.checker_mode,'refined','S10b Vor refined mode')
eq(img(0,0),G..'wall-6-0.png','S10b corner wall joins east and south')
eq(img(4,0),G..'wall-14-0.png','S10b wall beside the lever door joins it (E,S,W)')
eq(img(6,0),G..'wall-12-0.png','S10b wall joins the lever door west and wall south')
eq(img(1,1),floorImg(1,1),'S10b gothic floor variant')
eq(img(2,1),G..'wall-1-1.png','S10b pillar joins the wall to its north only')
eq(img(4,1),G..'door-closed-vertical1.png','S10b vertical door')
eq(img(4,2),G..'wall-5-0.png','S10b wall joins the doors north and south')
eq(img(1,3),G..'door-open-vertical0.png','S10b open vertical door')
eq(img(4,3),G..'door-closed-horizontal1.png','S10b horizontal door')
eq(img(1,2),floorImg(1,2),'S10b book cell draws the gothic floor')
eq(vm(1,2,1).replace_display.add_displays[1].image,'terrain/book_generic2.png','S10b book keeps its native layer on top')
eq(img(6,3),G..'exit-up1.png','S10b flat up exit on the board stairs piece')
eq(img(6,4),G..'exit-world0.png','S10b world exit on the board stairs piece')
eq(img(0,4),'checker-revised+refined/burnt/floor0.png','S10b burnt ground on Spellblaze art')
eq(img(1,4),'checker-revised+refined/burnt/tree1.png','S10b burnt tree on Spellblaze art')
eq(img(3,4),'checker-revised+refined/burnt/exit-down1.png','S10b FLAT_DOWN4 on the burnt exit-down')
eq(vm(6,4,1).change_zone,'wilderness','S10b world exit still leads to the world map')
sameRules('S10b Vor')
mode='blockout';T.apply(vh)
eq(img(0,0),'checker-revised+tree0.png','S10b blockout gothic wall blocks')
eq(img(4,1),'checker-revised+tree1.png','S10b blockout closed door blocks sight')
eq(img(1,3),'checker-revised+grass0.png','S10b blockout open door is open ground')
eq(img(1,4),'checker-revised+tree1.png','S10b blockout burnt tree blocks')
eq(img(6,3),'checker-revised+exit1.png','S10b blockout flat exit')
eq(img(3,4),'checker-revised+exit1.png','S10b blockout burnt exit-down')
mode='vanilla';T.apply(vh)
for x=0,vm.w-1 do for y=0,vm.h-1 do eq(vm(x,y,1).replace_display,nil,'S10b native mode restores Vor '..x..','..y) end end
mode='refined';T.apply(vh)
eq(img(4,0),G..'wall-14-0.png','S10b refined restore gothic wall')
eq(img(1,2),floorImg(1,2),'S10b refined restore book floor')
sameRules('S10b Vor after toggles')
-- Old save: a level generated before the stamps keeps every cell native.
local om=townMap(3,1,function(x) local g=deep(vD[({'GOTHIC_WALL3','GOTHIC_FLOOR','BURNT_GROUND'})[x+1]]);g._checker_zone_source=nil;return g end)
T.apply({zone={short_name='vor-pride'},level={map=om,data={}}})
for x=0,2 do eq(om(x,0,1).replace_display,nil,'S10b old-save Vor cell stays native '..x) end
string.prefix=savedPrefix
env.game=sg;mode='refined'
end)()
string.tformat=nil
mode='vanilla'
end)()
print('terrain_contract: '..n..' checks passed (native definitions + mocked renderer; no live-game claim)')
