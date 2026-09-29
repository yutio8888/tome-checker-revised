-- Forest terrain survives native NicerTiles re-tiling. Run with Lua 5.1 or LuaJIT.
local script=debug.getinfo(1,'S').source:sub(2)
local root=(script:match('^(.*[/\\])') or './')..'../'
local checks=0
local function equal(actual,expected,label)
 checks=checks+1
 assert(actual==expected,label..': expected '..tostring(expected)..', got '..tostring(actual))
end
local env=setmetatable({config={settings={cheat=false,tome={checker_terrain_mode='refined'}}},__module_extra_info={}},{__index=_G})
local function load(path)
 local chunk
 if setfenv then chunk=assert(loadfile(root..path));setfenv(chunk,env)
 else chunk=assert(loadfile(root..path,'t',env)) end
 return chunk()
end
local modules={}
local Entity={new=function(def) def.removeAllMOs=function() end;return def end}
modules['engine.Map']={TERRAIN=1,ACTOR=2};modules['engine.Entity']=Entity
env.require=function(name) return assert(modules[name],'unexpected module '..name) end
env.loadPrevious=function() return {} end
modules['mod.class.CheckerTokens']=load('overload/mod/class/CheckerTokens.lua')
modules['mod.class.CheckerOptions']=load('overload/mod/class/CheckerOptions.lua')
modules['mod.class.CheckerPlayerTokens']=load('overload/mod/class/CheckerPlayerTokens.lua')
modules['mod.class.CheckerTerrain']=load('overload/mod/class/CheckerTerrain.lua')
local Game=load('superload/mod/class/Game.lua')

local gridMethods={removeAllMOs=function() end,clone=function(self)
 local out={};for k,v in pairs(self) do out[k]=v end
 return setmetatable(out,getmetatable(self))
end}
local function grid(fields) return setmetatable(fields,{__index=gridMethods}) end
local function newMap(w,h)
 local map=setmetatable({w=w,h=h,cells={},updated={}},{__call=function(self,x,y,layer,value)
  if x<0 or x>=self.w or y<0 or y>=self.h then return nil end
  local key=x+y*self.w
  if value then self.cells[key]=value;self:updateMap(x,y) end
  return self.cells[key]
 end})
 function map:updateMap(x,y) self.updated[#self.updated+1]=x..','..y end
 function map:redisplay() end
 return map
end
local W,H=9,7
local grass=grid{name='grass',subtype='grass',type='floor',define_as='GRASS',image='terrain/grass.png'}
local map=newMap(W,H)
for i=0,W*H-1 do map.cells[i]=grass end
local water=grid{name='deep water',subtype='water',air_level=-1,image='water.png'}
map.cells[4+1*W]=water -- (4,1), north neighbour of the dig site (4,2)
local level={map=map}
local game=setmetatable({level=level,zone={short_name='trollmire'},turn=7,
 saveSettings=function() end},{__index=Game})
env.game=game
game:checkerApplySettings()
local function image(x,y)
 local d=map(x,y,1).replace_display
 return d and d.image
end
local function refinedCount()
 local n=0
 for i=0,W*H-1 do if map.cells[i].replace_display then n=n+1 end end
 return n
end
equal(refinedCount(),W*H,'fresh level is fully refined')
equal(image(4,1),'checker-revised+refined/deep0-1-0.png','isolated water uses mask 0')

-- Fake native NicerTiles that reproduces both replaceAll paths.
local calls={}
local Native={}
function Native:updateAround(lvl,x,y)
 calls[#calls+1]='around'
 -- repl path: a fresh native entity replaces the grid.
 lvl.map(x,y,1,grid{name='grass',subtype='grass',type='floor',define_as='GRASS',image='terrain/grass.png'})
 -- repl path turning grass into water changes the neighbour water mask.
 lvl.map(x,y-1+2,1,grid{name='deep water',subtype='water',air_level=-1,image='water.png'})
 -- edits path with __nice_tile_base: base clone drops our replacement.
 local base=grid{name='grass',subtype='grass',type='floor',define_as='GRASS',image='terrain/grass.png'}
 local e=base:clone();e.__nice_tile_base=base;lvl.map(x-1,y,1,e)
 -- edits path without a base: plain clone keeps our state consistently.
 local kept=lvl.map(x+1,y,1):clone();lvl.map(x+1,y,1,kept)
end
function Native:postProcessLevelTiles(lvl)
 calls[#calls+1]='full'
 for i=0,lvl.map.w*lvl.map.h-1 do lvl.map.cells[i]=grid{name='grass',subtype='grass',type='floor',define_as='GRASS',image='terrain/grass.png'} end
end
function Native:postProcessLevelTilesOnLoad(lvl)
 calls[#calls+1]='load'
 lvl.map.cells[0]=grid{name='grass',subtype='grass',type='floor',define_as='GRASS',image='terrain/grass.png'}
end
env.loadPrevious=function() return Native end
local Nicer=load('superload/mod/class/NicerTiles.lua')
equal(Nicer,Native,'superload extends the native class in place')
local tiler=setmetatable({},{__index=Nicer})

-- Dig at (4,2): (4,3) becomes water, so (4,2) and (4,4) are mask neighbours.
map.updated={}
local kept=map(5,2,1)
tiler:updateAround(level,4,2)
equal(calls[#calls],'around','native updateAround still runs')
equal(refinedCount(),W*H,'local re-tile leaves no native cell behind')
equal(image(4,2),'checker-revised+refined/grass0.png','repl cell is repainted with parity')
equal(image(3,2),'checker-revised+refined/grass1.png','edits base cell is repainted')
equal(map(5,2,1)._checker_terrain.display,map(5,2,1).replace_display,'cloned state stays owned')
equal(image(4,3),'checker-revised+refined/deep0-1-0.png','new water is refined')
equal(image(4,1),'checker-revised+refined/deep0-1-0.png','untouched water keeps its mask')
equal(map(4,2,1).replace_display.image:match('grass') and true,true,'grass between waters stays grass')
equal(kept~=map(5,2,1),true,'test really replaced the edits cell')
local touched={}
for _,k in ipairs(map.updated) do
 local x,y=k:match('(%d+),(%d+)');x,y=tonumber(x),tonumber(y)
 equal(math.abs(x-4)<=2 and math.abs(y-2)<=2,true,'updates stay inside the 5x5 repair window '..k)
 touched[k]=true
end
equal(touched['4,2'],true,'repaired dig cell is redrawn')

-- Water mask neighbour outside the native 3x3 but inside the repair window.
map.cells[2+4*W]=grid{name='deep water',subtype='water',air_level=-1,image='water.png'}
game:checkerApplySettings()
equal(image(2,4),'checker-revised+refined/deep0-0-0.png','setup: isolated water at (2,4)')
Native.updateAround=function(_,lvl,x,y) lvl.map(x,y,1,grid{name='deep water',subtype='water',air_level=-1,image='water.png'}) end
env.loadPrevious=function() return Native end
Nicer=load('superload/mod/class/NicerTiles.lua')
tiler=setmetatable({},{__index=Nicer})
tiler:updateAround(level,3,4) -- (3,4) water; (2,4) now has an east water neighbour
equal(image(3,4),'checker-revised+refined/deep8-1-0.png','new water sees west neighbour')
equal(image(2,4),'checker-revised+refined/deep2-0-0.png','neighbour mask outside native 3x3 is refreshed')

-- Edges clamp without error.
tiler:updateAround(level,0,0)
equal(image(0,0),'checker-revised+refined/deep0-0-0.png','corner re-tile clamps to the map')

-- Full passes: generation-time and mid-game load-time re-tiles.
tiler:postProcessLevelTiles(level)
equal(refinedCount(),W*H,'full native re-tile is repainted')
tiler:postProcessLevelTilesOnLoad(level)
equal(image(0,0),'checker-revised+refined/grass0.png','load-time re-tile is repainted')

-- Another level (e.g. generation of a level not yet current) is left alone.
local other={map=newMap(3,3)}
for i=0,8 do other.map.cells[i]=grass end
tiler:postProcessLevelTiles(other)
equal(other.map.cells[0].replace_display,nil,'non-current level is not painted')

-- Vanilla mode: re-tiled cells stay native and nothing new is installed.
game:checkerSetMode('vanilla')
equal(refinedCount(),0,'vanilla restored every cell')
map.updated={}
tiler:updateAround(level,4,2)
equal(refinedCount(),0,'vanilla re-tile installs nothing')

-- F1: native DIG on a BOGTREE replaces the grid with BOGWATER; the repair
-- must swap the bog-tree runtime art for plain bog art (CONTRACT.md Section
-- 8), the same way a dug ordinary tree becomes grass above.
game.zone.is_flooded=true
game:checkerSetMode('refined')
map.cells[6+3*W]=grid{name='tree',subtype='water',define_as='BOGTREE',does_block_move=true,block_sight=true,image='bogtree.png'}
game:checkerApplySettings()
equal(image(6,3),'checker-revised+refined/bog-tree-a0-1-0.png','setup: BOGTREE cell painted with bog-tree art')
Native.updateAround=function(_,lvl,x,y) lvl.map(x,y,1,grid{name='bog water',subtype='water',image='bogwater.png'}) end
env.loadPrevious=function() return Native end
Nicer=load('superload/mod/class/NicerTiles.lua')
tiler=setmetatable({},{__index=Nicer})
tiler:updateAround(level,6,3)
equal(image(6,3),'checker-revised+refined/bog0-1-0.png','dig repaint: BOGTREE becomes plain bog water art')
game.zone.is_flooded=nil

-- G0: Old Forest DEFAULT digs a dark_grass TREE into dark_grass GRASS; the
-- repair must swap tree art for grass art, same idiom as the ordinary
-- Trollmire tree dig above, through the zone-scoped dark_grass alias.
game:checkerSetMode('vanilla')
game.zone={short_name='old-forest'}
game:checkerSetMode('refined')
map.cells[3+2*W]=grid{name='tree',subtype='dark_grass',does_block_move=true,block_sight=true,image='terrain/tree.png'}
game:checkerApplySettings()
equal(image(3,2),'checker-revised+refined/tree-willow1.png','setup: Old Forest dark_grass TREE painted with tree art')
Native.updateAround=function(_,lvl,x,y) lvl.map(x,y,1,grid{name='grass',subtype='dark_grass',type='floor',define_as='GRASS',image='terrain/grass/dark_grass_main_01.png'}) end
env.loadPrevious=function() return Native end
Nicer=load('superload/mod/class/NicerTiles.lua')
tiler=setmetatable({},{__index=Nicer})
tiler:updateAround(level,3,2)
equal(image(3,2),'checker-revised+refined/grass1.png','dig repaint: Old Forest dark_grass TREE becomes grass art')
game.zone={short_name='trollmire'}

-- G0: Slazish Fens digs a BOGTREE into BOGWATER exactly like Trollmire
-- FLOODED; only the zone gate differs.
game:checkerSetMode('vanilla')
game.zone={short_name='slazish-fen'}
game:checkerSetMode('refined')
map.cells[2+5*W]=grid{name='tree',subtype='water',define_as='BOGTREE',does_block_move=true,block_sight=true,image='bogtree.png'}
game:checkerApplySettings()
equal(image(2,5),'checker-revised+refined/bog-tree-a0-1-0.png','setup: Slazish Fens BOGTREE painted with bog-tree art')
Native.updateAround=function(_,lvl,x,y) lvl.map(x,y,1,grid{name='bog water',subtype='water',image='bogwater.png'}) end
env.loadPrevious=function() return Native end
Nicer=load('superload/mod/class/NicerTiles.lua')
tiler=setmetatable({},{__index=Nicer})
tiler:updateAround(level,2,5)
equal(image(2,5),'checker-revised+refined/bog0-1-0.png','dig repaint: Slazish Fens BOGTREE becomes plain bog water art')
game.zone={short_name='trollmire'}
game:checkerSetMode('vanilla');game:checkerSetMode('refined')

-- Norgos snow tree DIG uses the same native NicerTiles repair hook.
game:checkerSetMode('vanilla')
game.zone={short_name='norgos-lair',is_invaded=true}
game:checkerSetMode('refined')
map.cells[4+5*W]=grid{define_as='ROCKY_SNOWY_TREE',name='snowy tree',type='wall',subtype='rock',
 image='terrain/rocky_snowy_tree.png',display='#',does_block_move=true,block_sight=true,
 dig='ROCKY_GROUND',can_pass={pass_tree=1}}
game:checkerApplySettings()
equal(image(4,5),'checker-revised+refined/snow/tree-pine1.png','setup: Norgos snow tree painted')
Native.updateAround=function(_,lvl,x,y)
 lvl.map(x,y,1,grid{define_as='ROCKY_GROUND',name='rocky ground',type='floor',subtype='rock',
  image='terrain/snowy_grass.png',display='.'})
end
env.loadPrevious=function() return Native end
Nicer=load('superload/mod/class/NicerTiles.lua')
tiler=setmetatable({},{__index=Nicer})
tiler:updateAround(level,4,5)
equal(image(4,5),'checker-revised+refined/snow/snow-ground1.png','dig repaint: Norgos snow tree becomes snowy floor')
game:checkerSetMode('vanilla')
game.zone={short_name='daikara',is_volcano=true}
game:checkerSetMode('refined')
for _,site in ipairs{{2,5,'MOUNTAIN_WALL','rocky mountain','rockwall','terrain/rocky_mountain.png','pass_wall'},
 {4,5,'ROCKY_SNOWY_TREE','snowy tree','wall','terrain/rocky_snowy_tree.png','pass_tree'}} do
 local x,y,id,name,typ,art,pass=unpack(site)
 map.cells[x+y*W]=grid{define_as=id,name=name,type=typ,subtype='rock',image=art,
  display='#',does_block_move=true,block_sight=true,dig='ROCKY_GROUND',
  can_pass={[pass]=1},air_level=typ=='rockwall' and -20 or nil}
 game:checkerApplySettings()
 equal(image(x,y)~=nil,true,'setup: Daikara blocker painted '..id)
 Native.updateAround=function(_,lvl,px,py)
  lvl.map(px,py,1,grid{define_as='ROCKY_GROUND',name='rocky ground',type='floor',
   subtype='rock',image='terrain/rocky_ground.png',display='.'})
 end
 Nicer=load('superload/mod/class/NicerTiles.lua')
 tiler=setmetatable({},{__index=Nicer})
 tiler:updateAround(level,x,y)
 equal(image(x,y),'checker-revised+refined/daikara/rock-ground'..((x+y)%2)..'.png',
  'dig repaint: Daikara '..id..' becomes bare floor')
end
game.zone={short_name='heart-gloom',is_purified=false}
local Gloom=modules['mod.class.CheckerTerrain']
local wall=grid{define_as='UNDERGROUND_TREE7',name='underground thick vegetation',
 type='wall',subtype='underground',image='terrain/mushrooms/gloomy_underground_floor.png',
 does_block_move=true,block_sight=true,can_pass={pass_tree=1},dig='UNDERGROUND_FLOOR'}
Gloom.markSource(wall,'/data/general/grids/underground_gloomy.lua')
map.cells[4+5*W]=wall
game:checkerApplySettings()
equal(image(4,5),'checker-revised+refined/gloom/gloomy/wall-0-1.png','Gloom wall painted')
Native.updateAround=function(_,lvl,x,y)
 local floor=grid{define_as='UNDERGROUND_FLOOR2',name='floor',type='floor',
  subtype='underground',image='terrain/mushrooms/gloomy_underground_floor2.png'}
 Gloom.markSource(floor,'/data/general/grids/underground_gloomy.lua')
 lvl.map(x,y,1,floor)
end
env.loadPrevious=function() return Native end
Nicer=load('superload/mod/class/NicerTiles.lua')
tiler=setmetatable({},{__index=Nicer})
tiler:updateAround(level,4,5)
equal(image(4,5),'checker-revised+refined/gloom/gloomy/floor1.png','Gloom dig repaint')
local zoneWall=grid{define_as='TREE7',name='tree',type='wall',subtype='dark_grass',
 image='terrain/mushrooms/gloomy_underground_floor.png',does_block_move=true,
 block_sight=true,can_pass={pass_tree=1},dig='UNDERGROUND_FLOOR'}
Gloom.markSource(zoneWall,'/data/zones/heart-gloom/grids.lua')
map.cells[4+5*W]=zoneWall
game:checkerApplySettings()
equal(image(4,5),'checker-revised+refined/gloom/gloomy/wall-0-1.png','Gloom zone TREE painted')
tiler:updateAround(level,4,5)
equal(image(4,5),'checker-revised+refined/gloom/gloomy/floor1.png','Gloom zone TREE dig repaint')
game.zone={short_name='trollmire'}

-- Kor'Pul uses its own self-healing adapter; the forest repair must not run.
game:checkerSetMode('refined')
game.zone={short_name='ruins-kor-pul'}
map.cells[0]=grid{name='grass',subtype='grass',type='floor',define_as='GRASS',image='terrain/grass.png'}
equal(game:checkerRepairTerrain(0,0,1,1),nil,'Kor\'Pul variant skips forest repair')
equal(map.cells[0].replace_display,nil,'Kor\'Pul cells are not forest-painted')
game.zone={short_name='dreadfell'}
equal(game:checkerRepairTerrain(0,0,1,1),nil,'Dreadfell uses stone observation repair')
equal(map.cells[0].replace_display,nil,'Dreadfell does not claim forest cells')

-- S5: the Dreadfell ambush quest sets its world exit with a direct map set
-- (no NicerTiles pass). The onTurn hook repaints that level once, only after
-- the quest records an outcome, only in dreadfell-ambush; the native onTurn
-- always runs first and its result is returned.
do
 local Terrain=modules['mod.class.CheckerTerrain']
 local nativeTurns=0
 env.loadPrevious=function() return {onTurn=function() nativeTurns=nativeTurns+1;return 'native' end} end
 local AGame=load('superload/mod/class/Game.lua')
 local forest='/data/general/grids/forest.lua'
 local agrass=grid{define_as='GRASS',type='floor',subtype='grass',name='grass',display='.',grow='TREE',image='terrain/grass.png'}
 Terrain.markSource(agrass,forest)
 local aexit=grid{define_as='GRASS_UP_WILDERNESS',type='floor',subtype='grass',name='exit to the worldmap',image='terrain/grass.png',
  add_mos={{image='terrain/worldmap.png'}},display='<',always_remember=true,notice=true,change_level=1,change_zone='wilderness'}
 Terrain.markSource(aexit,forest)
 local amap=newMap(4,3)
 for i=0,11 do amap.cells[i]=agrass end
 local status={}
 local quest={isCompleted=function(_,s) return status[s] and true or false end}
 local player={hasQuest=function(_,id) return id=='staff-absorption' and quest or nil end}
 local repairs=0
 local ag=setmetatable({level={map=amap},zone={short_name='dreadfell-ambush'},player=player,turn=1,saveSettings=function() end},{__index=AGame})
 ag.checkerRepairTerrain=function(self,...) repairs=repairs+1;return AGame.checkerRepairTerrain(self,...) end
 env.game=ag
 ag:checkerApplySettings()
 equal(amap(1,1,1).replace_display.image,'checker-revised+refined/grass0.png','S5 ambush glade is board grass')
 equal(ag:onTurn(),'native','S5 hook returns the native onTurn result')
 equal(repairs,0,'S5 no repaint before the quest outcome')
 amap(2,1,1,aexit)
 equal(amap(2,1,1).replace_display,nil,'S5 direct quest exit set is native at first')
 ag:onTurn()
 equal(repairs,0,'S5 no repaint while the quest has no outcome')
 status['survived-ukruk']=true
 ag:onTurn()
 equal(repairs,1,'S5 one repaint once the quest records the outcome')
 equal(amap(2,1,1).replace_display.image,'checker-revised+refined/exit1.png','S5 quest exit painted as the board exit')
 equal(amap(2,1,1).change_zone,'wilderness','S5 quest exit transition untouched')
 equal(aexit.replace_display,nil,'S5 shared exit prototype never painted')
 ag:onTurn()
 equal(repairs,1,'S5 the repaint runs once per level')
 local amap2=newMap(2,1);amap2.cells[0]=agrass;amap2.cells[1]=agrass
 ag.level={map=amap2}
 ag:onTurn()
 equal(repairs,2,'S5 a new level instance (reload) repaints once more')
 ag.zone={short_name='trollmire'};ag.level={map=newMap(1,1)};ag.level.map.cells[0]=agrass
 ag:onTurn()
 equal(repairs,2,'S5 hook is inert outside the ambush zone')
 equal(nativeTurns,6,'S5 native onTurn ran every time')
 env.loadPrevious=function() return {} end
end

-- No level / no map hosts are ignored.
env.game={level=nil}
tiler:updateAround(level,1,1)
equal(game.turn,7,'repair never advances time')
print(('terrain_repair: %d checks passed; local and full NicerTiles re-tiles keep refined forest'):format(checks))
