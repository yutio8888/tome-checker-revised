-- Terrain contracts and rendering ownership. No movement/interaction overrides.
local Map={TERRAIN=1} -- Avoid a require cycle with the Map superload.
local Entity=require 'engine.Entity'
local Options=require 'mod.class.CheckerOptions'
local M={}
local auraEffects={
 ['fell-aura']='violet', ['antimagic-bush']='violet',
 ['spellblaze-scar']='crimson', ['bligthed-soil']='crimson',
 ['protective-aura']='teal', ['font-life']='teal',
 ['necrotic-air']='violet', ['whistling-vortex']='violet',
 ['slimey-pool']='violet',
}
function M.auraEvent(g)
 if not g or type(g.on_stand)~='function' then return end
 local info=debug.getinfo(g.on_stand,'S')
 local event=info and info.source and info.source:match('/events/([%w%-]+)%.lua$')
 return event and auraEffects[event] and event
end
function M.auraKind(g)
 local event=M.auraEvent(g)
 return event and auraEffects[event]
end
local function img(n) return 'checker-revised+'..n..'.png' end
local function auraMask(kind)
 if not kind then return end
 return img('aura-'..kind..'-'..Options.auraStyle())
end
local function auraDisplay(kind)
 return Entity.new{image=auraMask(kind),z=2,display_on_seen=true,display_on_remember=true}
end
-- S1: exact provenance of a native aura event's output. Each ring event
-- (data/general/events/<event>.lua) cloneFull()s every cell in its circle and
-- sets g.on_stand=g.on_stand or <its local on_stand>, always_remember=true;
-- on floor-type cells whose on_stand became its own it also renames the grid
-- ("%s (<aura>)" of _t(name)) and sets special_minimap if absent. font-life
-- and spellblaze-scar also set on_stand_safe=true. Walls/doors keep their name.
-- `line` is the on_stand's linedefined in the native file; an overridden or
-- foreign file with the same event name does not match.
local function rgb(r,g,b) return {r=r,g=g,b=b} end
local OLIVE_DRAB,DARK_SLATE_GRAY=rgb(107,142,35),rgb(47,79,79)
local ringEvents={
 ['fell-aura']={line=30,rename='%s (fell aura)',minimap=rgb(60,99,99)},
 ['antimagic-bush']={line=24,rename='%s (antimagic aura)',minimap=rgb(85,35,35),
  centre={name='antimagic bush',display='~',r=0,g=255,b=100,image='terrain/antimagic_bush.png'}},
 ['spellblaze-scar']={line=24,rename='%s (spellblaze aura)',minimap=rgb(50,0,0),safe=true},
 ['bligthed-soil']={line=24,rename='%s (blighted aura)',minimap=DARK_SLATE_GRAY,
  centre={name='blighted soil',display='~',r=0,g=255,b=0,image='terrain/blight_root.png'}},
 ['protective-aura']={line=30,rename='%s (protective aura)',minimap=rgb(110,80,40)},
 ['font-life']={line=24,rename='%s (life aura)',minimap=rgb(127,255,212),safe=true,
  centre={name='font of life',display='&',r=0,g=255,b=0,image='terrain/terrain_pot_03_01_64.png'}},
 ['necrotic-air']={line=30,rename='%s (necrotic air)',minimap=DARK_SLATE_GRAY},
 ['whistling-vortex']={line=26,rename='%s (whistling vortex)',minimap=DARK_SLATE_GRAY},
 ['slimey-pool']={line=26,rename='%s (slimey)',minimap=rgb(143,188,143)},
}
local function ringEvent(fn)
 if type(fn)~='function' then return end
 local info=debug.getinfo(fn,'S')
 local event=info and type(info.source)=='string' and info.source:match('^@?/data/general/events/([%w%-]+)%.lua$')
 local d=event and ringEvents[event]
 if d and info.linedefined==d.line then return event,d end
end
M.ringEvent=ringEvent
local function sameShallow(a,b)
 if a==b then return true end
 if type(a)~='table' or type(b)~='table' then return false end
 for k,v in pairs(a) do if b[k]~=v then return false end end
 for k,v in pairs(b) do if a[k]~=v then return false end end
 return true
end
local function sameColor(c,want)
 if type(c)~='table' then return false end
 for k,v in pairs(c) do if want[k]~=v then return false end end
 return c.r==want.r and c.g==want.g and c.b==want.b
end
local function translate(s)
 local t=_t
 if type(t)=='function' then return t(s) end
 return s
end
local function renamedAs(template,native,name)
 if type(native)~='string' or type(name)~='string' then return false end
 local tformat=string.tformat
 local localized=type(tformat)=='function' and tformat(template,translate(native)) or template:format(translate(native))
 return name==localized or name==template:format(native)
end
M.ringRenamed=renamedAs
local function ringBase(g)
 if not g or g.on_stand==nil then return end
 local event,d=ringEvent(g.on_stand)
 local def=g._checker_def
 if not event or type(def)~='table' or def.id~=g.define_as or def.stand or g.always_remember~=true then return end
 if d.safe then
  if g.on_stand_safe~=true or def.on_stand_safe~=nil then return end
 elseif g.on_stand_safe~=def.on_stand_safe then return end
 local v={}
 for k,x in pairs(g) do v[k]=x end
 v.on_stand=nil;v.always_remember=def.always_remember;v.on_stand_safe=def.on_stand_safe
 return event,d,def,setmetatable(v,getmetatable(g))
end
-- A ring cell as the native definition left it: same grid minus exactly the
-- event's own marks. Every family contract is then applied to that view.
function M.auraRing(g)
 local event,d,def,v=ringBase(g)
 if not v then return end
 if g.type=='floor' then
  if not renamedAs(d.rename,def.name,g.name) then return end
  if def.special_minimap~=nil then
   if not sameShallow(g.special_minimap,def.special_minimap) then return end
  elseif not sameColor(g.special_minimap,d.minimap) then return end
  v.name=def.name;v.special_minimap=def.special_minimap
 elseif g.name~=def.name or not sameShallow(g.special_minimap,def.special_minimap) then return end
 return event,v
end
-- E3: font-life, bligthed-soil and antimagic-bush also mark their centre
-- cell: name/display/colour/notice/minimap and one appended z=5 prop layer.
-- The view removes exactly those; the prop is returned to draw over the board.
function M.auraCentre(g)
 local event,d,def,v=ringBase(g)
 local c=d and d.centre
 if not c or g.type~='floor' or def.notice or
  not renamedAs(d.rename,translate(c.name),g.name) and not renamedAs(d.rename,c.name,g.name) or
  g.display~=c.display or g.color_r~=c.r or g.color_g~=c.g or g.color_b~=c.b or g.notice~=true or
  not sameColor(g.special_minimap,OLIVE_DRAB) then return end
 local ds=g.add_displays
 local prop=type(ds)=='table' and ds[#ds]
 if not prop or prop.image~=c.image or prop.z~=5 or prop.add_mos or prop.add_displays or
  prop.display_x or prop.display_y or prop.display_w or prop.display_h or prop.shader then return end
 local rest=nil
 if #ds>1 then rest={};for i=1,#ds-1 do rest[i]=ds[i] end end
 v.name=def.name;v.display=def.display;v.color_r=def.color_r;v.color_g=def.color_g;v.color_b=def.color_b
 v.notice=def.notice;v.special_minimap=def.special_minimap;v.add_displays=rest
 return event,v,prop
end
local function ringView(g)
 if not g or g.on_stand==nil then return end
 local _,v=M.auraRing(g)
 if v then return v end
 local _,c=M.auraCentre(g)
 return c
end
-- Wrap a family classifier: a cell it rejects is retried once as the view of
-- an exact native ring/centre cell; the family's full contract still decides.
local function ringAware(classify)
 return function(g,...)
  local t=classify(g,...)
  if t~=nil then return t end
  local v=ringView(g)
  if v then return classify(v,...) end
 end
end
M.ringView=ringView
-- Only this forest set has been designed and checked. Unknown vault floors,
-- doors, special grids and other zones retain their native display.
-- BOGTREE/BOGTREE1..20 all share define_as prefix "BOGTREE"; nice_tiler has
-- already resolved the placed grid to one of these by render time (same
-- mechanism as TREE1..30/HARDTREE1..30). subtype+name alone cannot tell
-- BOGTREE from TREE (both use name="tree"; grids.lua:48) so define_as is the
-- disambiguator here, per CONTRACT I1/I3's "don't infer identity from name".
local function isBogtreeId(g)
 local id=g.define_as
 return id~=nil and (id=='BOGTREE' or id:match('^BOGTREE%d+$'))
end
local function nativeRoadDisplays(g)
 if not g.add_displays then return true end
 if #g.add_displays~=1 then return false end
 local d=g.add_displays[1]
 if d.image~='invis.png' or not d.add_mos or #d.add_mos<1 then return false end
 local prefix=g.road=='dirt' and '^terrain/road_dirt/' or
  g.road=='oldstone' and '^terrain/road_stone/'
 if not prefix then return false end
 for _,mo in ipairs(d.add_mos) do
  if type(mo.image)~='string' or not mo.image:match(prefix) then return false end
 end
 return true
end

-- Trollmire FLOODED adds three water-based identities on top of the existing
-- grass/road/exit/tree/deep-water set (CONTRACT.md Section 8): BOGTREE (a
-- wall, willow standing in water), BOGWATER (plain bog floor) and
-- BOGWATER_MISC1..7 (bog floor + a cosmetic add_displays layer, rule-
-- identical to BOGWATER). HARDTREE gets its own identity instead of being
-- merged into 'tree' (CONTRACT I1: HARDTREE has no can_pass/dig and blocks
-- sense/ESP, TREE does neither of the former and does not do the latter).
--
-- G0: Old Forest's DEFAULT layout (old-forest/grids.lua) redefines GRASS/
-- TREE/HARDTREE with subtype "dark_grass" instead of "grass" (its own copy,
-- not a base= override, purely to select a darker nice_editer/floor image);
-- every other field -- name, does_block_move, dig, can_pass, block_sense/esp
-- -- is identical to the CRYSTALINE/Trollmire copies. `allowDarkGrass` folds
-- "dark_grass" into the "grass" branch, but ONLY for the caller's own zone
-- (applyForest passes it in, scoped to zone.short_name=='old-forest'): Heart
-- of the Gloom's unrelated TREE identity also happens to use subtype
-- "dark_grass" (underground_gloomy/dreamy.lua) and must keep its native
-- mushroom-cave look, not be reinterpreted as an Old Forest tree (Section 5
-- of docs/expansion-plan-20260928/TERRAIN-INVENTORY.md). Exit identities
-- (GRASS_UP_WILDERNESS/GRASS_UP4/GRASS_DOWN6/GATES_OF_MORNING) are always
-- plain subtype "grass" in every supported zone, so they never depend on
-- this alias.
local function terrain(g,allowDarkGrass)
 if not g then return end
 local subtype=g.subtype
 if allowDarkGrass and subtype=='dark_grass' then subtype='grass' end
 if subtype=='grass' then
  if g.change_level or g.change_zone then return 'exit' end
  if g.does_block_move then
   if g.name=='tall thick tree' then return 'hardtree' end
   if g.name=='tree' then return 'tree' end
   return
  end
  -- cloneFull event auras keep define_as, subtype and the base gameplay
  -- contract. Their translated tooltip name is deliberately not an identity.
  local aura=M.auraKind(g)
  if g.on_stand and not aura then return end
  local id=g.define_as
  if g.type~='floor' or not id then return end
  if aura and (g.does_block_move or g.block_sight or g.block_sense or g.block_esp or
   g.dig or g.can_pass or g.shader or g.tint or
   (g.add_displays and not ((id=='GRASS_ROAD_STONE' or id=='GRASS_ROAD_DIRT') and nativeRoadDisplays(g)))) then return end
  local grassImage=g.image=='terrain/grass.png' or
   (type(g.image)=='string' and (g.image:match('^terrain/grass/grass_main_%d+%.png$') or
    g.image:match('^terrain/grass/dark_grass_main_%d+%.png$')))
  if id=='GRASS_ROAD_STONE' or id=='GRASS_ROAD_DIRT' then
   if (aura or g.name=='old road') and g.road==(id=='GRASS_ROAD_STONE' and 'oldstone' or 'dirt') and
    (not aura or (grassImage and g.display=='=')) then return 'road' end
  elseif id=='FLOWER' or id:match('^FLOWER%d+$') then
   if (aura or g.name=='flower') and not g.road and (not aura or
    ((g.image=='terrain/flower.png' or grassImage) and g.display==';')) then return 'flower' end
  elseif id=='GRASS' or id=='GRASS_SHORT' or id:match('^GRASS_PATCH%d+$') then
   if (aura or g.name=='grass') and not g.road and
    (not aura or (grassImage and g.display=='.')) then return 'grass' end
  end
 elseif subtype=='water' then
  if g.name=='tree' and isBogtreeId(g) then return 'bog-tree' end
  if g.name=='deep water' then return 'deep' end
  -- BOGWATER_MISC1..7 only add an add_displays layer over BOGWATER
  -- (trollmire/grids.lua:82-86); no other field differs, so its presence is
  -- the reliable signal, same idiom this file already uses for STEW/add_mos.
  if g.name=='bog water' then return g.add_displays and 'bog-misc' or 'bog' end
 end
end

local gloomSources={
 ['/data/general/grids/underground_gloomy.lua']='gloomy',
 ['/data/general/grids/underground_dreamy.lua']='dreamy',
 ['/data/zones/heart-gloom/grids.lua']='zone',
}
local gloomLadders={
 UNDERGROUND_LADDER_UP={'ladder-up',-1,nil,'terrain/ladder_up.png'},
 UNDERGROUND_LADDER_DOWN={'ladder-down',1,nil,'terrain/ladder_down.png'},
 UNDERGROUND_LADDER_UP_WILDERNESS={'ladder-world',1,'wilderness','terrain/ladder_up_wild.png'},
}
local function gloomTerrain(g,skin)
 if not g or not g._checker_gloom_source then return end
 local stamp=g._checker_gloom_source
 local id=g.define_as
 if stamp.id~=id or (stamp.skin~=skin and stamp.skin~='zone' and not (skin=='plain' and stamp.skin=='gloomy')) or
  (stamp.skin=='zone' and stamp.file~='/data/zones/heart-gloom/grids.lua') or
  (g.replace_display and (not g._checker_terrain or g.replace_display~=g._checker_terrain.display)) or
  -- Grid supplies default on_move/block_move functions even on plain floors.
  g.on_stand or g.on_dig or
  g.shader or g.textures or g.special or g.air_level or g.is_door then return end
 local base=(id=='TREE' or type(id)=='string' and id:match('^TREE%d+$')) and 'TREE' or
  type(id)=='string' and (id:match('^UNDERGROUND_[A-Z]+') or '') or ''
 if base=='UNDERGROUND_FLOOR' or base=='UNDERGROUND_CREEP' then
  if g.type~='floor' or g.does_block_move or g.block_sight or g.block_sense or
   g.block_esp or g.can_pass or g.dig or g.change_level or g.change_zone then return end
  if base=='UNDERGROUND_FLOOR' and g.subtype=='underground' and g.name=='floor' and
   type(g.image)=='string' and
   ((skin=='gloomy' or skin=='plain') and g.image:match('^terrain/mushrooms/gloomy_underground_floor%d*%.png$') or
    skin=='dreamy' and g.image:match('^terrain/underground_floor%d*%.png$')) then
   if g.add_displays then return end
   if g.add_mos then
    if #g.add_mos~=1 or type(g.add_mos[1].image)~='string' or
     not g.add_mos[1].image:match('^terrain/mushrooms/deco_floor_'..(skin=='plain' and 'gloomy' or skin)..'_mushroom_0[1-8]%.png$') then return end
   end
   return 'gloom-floor'
  end
  if base=='UNDERGROUND_CREEP' and g.subtype=='creep' and g.name=='mushroom creep' and
   type(g.image)=='string' and g.image:match('^terrain/mushrooms/creep_'..(skin=='plain' and 'gloomy' or skin)..'_mushrooms_main_%d+%.png$') then return 'gloom-creep' end
 elseif base=='UNDERGROUND_TREE' or base=='TREE' then
  if g.type~='wall' or g.does_block_move~=true or g.block_sight~=true or
   not g.can_pass or g.can_pass.pass_tree~=1 or g.dig~='UNDERGROUND_FLOOR' or
   g.block_sense or g.block_esp or g.change_level or g.change_zone or
   g.name~=(base=='TREE' and 'tree' or 'underground thick vegetation') or
   g.subtype~=(base=='TREE' and 'dark_grass' or 'underground') then return end
  if base=='TREE' and stamp.skin~='zone' or base=='UNDERGROUND_TREE' and stamp.skin~=skin and not (skin=='plain' and stamp.skin=='gloomy') then return end
  local nativeFloor=(skin=='gloomy' or skin=='plain') and 'terrain/mushrooms/gloomy_underground_floor.png' or
   'terrain/underground_floor.png'
  if g.image~='terrain/tree.png' and g.image~=nativeFloor then return end
  return 'gloom-wall'
 elseif gloomLadders[id] then
  local d=gloomLadders[id]
  local nativeFloor=(skin=='gloomy' or skin=='plain') and 'terrain/mushrooms/gloomy_underground_floor.png' or
   'terrain/underground_floor.png'
  if (stamp.skin~=skin and not (skin=='plain' and stamp.skin=='gloomy')) or g.type~='floor' or g.subtype~='underground' or
   g.change_level~=d[2] or g.change_zone~=d[3] or g.does_block_move or
   g.block_sight or g.dig or g.can_pass or g.add_mos or not g.add_displays or
   #g.add_displays~=1 or g.add_displays[1].image~=d[4] or g.image~=nativeFloor or
   g.notice~=true or (g.always_remember==true)~=(id~='UNDERGROUND_LADDER_UP_WILDERNESS') then return end
  return d[1]
 end
end
gloomTerrain=ringAware(gloomTerrain)
M.gloomTerrain=gloomTerrain

-- Sandworm Lair shares sand.lua with other zones. The exact ids and native
-- rule/display fields keep those zones and special replacements out of scope.
local sandLadders={
 SAND_LADDER_UP={'ladder-up',-1,nil,'terrain/ladder_up.png'},
 SAND_LADDER_DOWN={'ladder-down',1,nil,'terrain/ladder_down.png'},
 SAND_LADDER_UP_WILDERNESS={'ladder-world',1,'wilderness','terrain/ladder_up_wild.png'},
}
local function nativeSandWallArt(g)
 local function wallImage(path)
  return type(path)=='string' and (path=='terrain/sand.png' or
   path:match('^terrain/sand/sand_[%w_]+%.png$') or
   path:match('^terrain/sand/sandwall_[%w_]+%.png$'))
 end
 if not wallImage(g.image) then return false end
 if g.add_displays then
  if #g.add_displays<1 or #g.add_displays>3 or g.add_displays[1].image~='invis.png' then return false end
  for _,mo in ipairs(g.add_displays[1].add_mos or {}) do if not wallImage(mo.image) then return false end end
  for i=2,#g.add_displays do
   local d=g.add_displays[i]
   if not wallImage(d.image) then return false end
   for _,mo in ipairs(d.add_mos or {}) do if not wallImage(mo.image) then return false end end
  end
 end
 for _,mo in ipairs(g.add_mos or {}) do if not wallImage(mo.image) then return false end end
 return true
end
local function sandTerrain(g)
 if not g or type(g.define_as)~='string' then return end
 local id=g.define_as
 local floorVariant=tonumber(id:match('^UNDERGROUND_SAND(%d+)$'))
 local wallVariant=tonumber(id:match('^SANDWALL(%d+)$'))
 local stableVariant=tonumber(id:match('^SANDWALL_STABLE(%d+)$'))
 if g.subtype~='sand' or g.block_sense or g.block_esp or g.shader or g.textures or g.special then return end
 if id=='UNDERGROUND_SAND' or floorVariant and floorVariant>=1 and floorVariant<=11 then
  if g.type=='floor' and g.name=='sand' and not g.does_block_move and not g.block_sight and
   not g.dig and not g.change_level and not g.change_zone and not g.can_pass and
   not g.add_displays and not g.add_mos and
   type(g.image)=='string' and g.image:match('^terrain/sand_?%d*%.png$') then return 'floor' end
 elseif id=='SANDWALL' or wallVariant and wallVariant>=1 and wallVariant<=6 or
  id=='SANDWALL_STABLE' or stableVariant and stableVariant>=1 and stableVariant<=6 then
  local stable=id=='SANDWALL_STABLE' or stableVariant~=nil
  local info=type(g.dig)=='function' and debug.getinfo(g.dig,'S')
  if g.type=='wall' and g.name=='sandwall' and g.does_block_move==true and
   g.block_sight==true and g.always_remember==true and g.air_level==-10 and
   g.can_pass and g.can_pass.pass_wall==1 and
   (stable and g.dig=='UNDERGROUND_SAND' or not stable and info and
    info.source:match('/data/general/grids/sand%.lua$')) and
   not g.change_level and not g.change_zone and nativeSandWallArt(g) then return 'wall' end
 elseif sandLadders[id] then
  local d=sandLadders[id]
  if g.type=='floor' and g.name and g.does_block_move~=true and not g.block_sight and
   not g.dig and not g.can_pass and g.image=='terrain/sand.png' and
   g.change_level==d[2] and g.change_zone==d[3] and g.notice==true and
   (g.always_remember==true)==(id~='SAND_LADDER_UP_WILDERNESS') and
   g.add_displays and #g.add_displays==1 and g.add_displays[1].image==d[4] and
   not g.add_mos then return d[1] end
 end
end
sandTerrain=ringAware(sandTerrain)
M.sandTerrain=sandTerrain

-- Burntland and molten lava also occur in other zones. Source stamps and
-- final native rules keep this adapter limited to the Spellblaze map.
local burntSources={['/data/general/grids/burntland.lua']=true,
 ['/data/general/grids/lava.lua']=true}
local burntExits={
 BURNT_UP_WILDERNESS={'exit-world',1,'wilderness','terrain/worldmap.png'},
 BURNT_UP4={'exit-up',-1,nil,'terrain/way_next_4.png'},
 BURNT_DOWN6={'exit-down',1,nil,'terrain/way_next_6.png'},
}
local function burntTerrain(g)
 if not g or type(g.define_as)~='string' or not g._checker_burnt_source or
  g._checker_burnt_source.id~=g.define_as or
  (g.replace_display and (not g._checker_terrain or g.replace_display~=g._checker_terrain.display)) or
  g.on_stand or g.on_dig or g.special or g.textures or g.block_sense or g.block_esp then return end
 local id=g.define_as
 local file=g._checker_burnt_source.file
 if file=='/data/general/grids/lava.lua' then
  local n=tonumber(id:match('^LAVA(%d+)$'))
  if id~='LAVA' and not (n and n>=2 and n<=5) then return end
  if g.type~='floor' or g.subtype~='molten_lava' or g.name~='molten lava' or
   g.display~='%' or g.does_block_move~=true or g.block_sight or
   g.pass_projectile~=true or g.shader~='lava' or g.dig or g.can_pass or
   g.change_level or g.change_zone or g.add_mos or
   not g.image:match('^terrain/lava/molten_lava_5_0[1-5]%.png$') then return end
  for _,d in ipairs(g.add_displays or {}) do
   if d.image~='invis.png' and not (type(d.image)=='string' and
    d.image:match('^terrain/lava/molten_lava_[%w_]+%.png$')) then return end
   for _,mo in ipairs(d.add_mos or {}) do
    if type(mo.image)~='string' or not mo.image:match('^terrain/lava/molten_lava_[%w_]+%.png$') then return end
   end
  end
  return 'lava'
 end
 if file~='/data/general/grids/burntland.lua' or g.subtype~='burnt' or
  g.shader or g.change_level_check then return end
 local floorN=tonumber(id:match('^BURNT_GROUND(%d+)$'))
 local treeN=tonumber(id:match('^BURNT_TREE(%d+)$'))
 if id=='BURNT_GROUND' or floorN and floorN>=1 and floorN<=7 then
  if g.type~='floor' or g.name~='burnt ground' or g.display~='.' or
   g.does_block_move or g.block_sight or g.dig or g.can_pass or
   g.change_level or g.change_zone or g.add_displays or
   g.image~='terrain/grass_burnt1.png' then return end
  if floorN then
   if not g.add_mos or #g.add_mos~=1 or
    g.add_mos[1].image~='terrain/burnt_floor_deco'..floorN..'.png' then return end
  elseif g.add_mos then return end
  return 'floor'
 elseif id=='BURNT_TREE' or treeN and treeN>=1 and treeN<=20 then
  if g.type~='wall' or g.name~='burnt tree' or g.display~='#' or
   g.does_block_move~=true or g.block_sight~=true or
   not g.can_pass or g.can_pass.pass_tree~=1 or g.dig~='BURNT_GROUND1' or
   g.change_level or g.change_zone or g.always_remember~=true or
   g.image~='terrain/grass_burnt1.png' or g.add_mos and #g.add_mos>0 then return end
  for _,d in ipairs(g.add_displays or {}) do
   if d.image~='invis.png' and not (type(d.image)=='string' and
    (d.image:match('^terrain/trees/burned_tree_[%w_]+%.png$') or
     d.image:match('^terrain/trees/small_burned_tree_[%w_]+%.png$'))) then return end
   for _,mo in ipairs(d.add_mos or {}) do
    if type(mo.image)~='string' or not (mo.image:match('^terrain/trees/burned_tree_[%w_]+%.png$') or
     mo.image:match('^terrain/trees/small_burned_tree_[%w_]+%.png$')) then return end
   end
  end
  return 'tree'
 elseif burntExits[id] then
  local e=burntExits[id]
  if g.type~='floor' or g.does_block_move or g.block_sight or g.can_pass or
   g.dig or g.add_mos or g.image~='terrain/grass_burnt1.png' or
   g.change_level~=e[2] or g.change_zone~=e[3] or
   g.notice~=true or g.always_remember~=true or not g.add_displays or
   #g.add_displays~=1 or g.add_displays[1].image~=e[4] or
   g.display~=(id=='BURNT_DOWN6' and '>' or '<') then return end
  return e[1]
 end
end
burntTerrain=ringAware(burntTerrain)
M.burntTerrain=burntTerrain

-- A void tile can be walkable (VOID), a solid rift, empty lethal space, or a
-- moving platform. Preserve the native object and all callbacks. In
-- particular, WORMHOLE is intentionally excluded: spell damage changes its
-- destination and its visual state.
local voidSources={['/data/general/grids/void.lua']=true,
 ['/data/zones/unhallowed-morass/grids.lua']=true}
local function nativeRiftArt(g)
 local function native(path)
  return type(path)=='string' and (path=='invis.png' or
   path:match('^terrain/rift/[%w_]+%.png$'))
 end
 if not native(g.image) then return false end
 if g.add_displays then
  if #g.add_displays<1 or #g.add_displays>4 then return false end
  for _,d in ipairs(g.add_displays) do
   if not native(d.image) or d.on_stand or d.damage_project or d.change_level then return false end
   for _,mo in ipairs(d.add_mos or {}) do if not native(mo.image) then return false end end
  end
 end
 return true
end
local function voidTerrain(g,zoneName)
 if not g or not g._checker_void_source or g._checker_void_source.id~=g.define_as or
  (g.replace_display and (not g._checker_terrain or g.replace_display~=g._checker_terrain.display)) or
  g.on_stand or g.on_dig or g.damage_project or g.change_level or g.change_zone or
  g.change_level_check or g.special or g.shader or g.tint or g.textures or
  g.add_mos or rawget(g,'on_move') or rawget(g,'block_move') then return end
 local id=g.define_as
 local file=g._checker_void_source.file
 -- TW4: Point Zero's platform is the same void.lua space/rocks (Abashed
 -- contract) plus its VOID floor and rifts (Temporal Rift contract); its
 -- townKind also requires Point Zero's own list stamp.
 local pointZero=zoneName=='town-point-zero'
 if zoneName=='abashed-expanse' or pointZero then
  if file~='/data/general/grids/void.lua' then return end
  if id=='OUTERSPACE' and g.type=='void' and g.subtype=='void' and g.name=='void' and
   g.display==' ' and not g.image and g._noalpha==false and g.always_remember==true and
   g.does_block_move==true and g.pass_projectile==true and g.air_level==-40 and
   g.is_void==true and g.can_pass and g.can_pass.pass_void==1 and
   not g.block_sight and not g.dig and not g.add_displays then return 'space' end
  if id=='FLOATING_ROCKS' or id=='FLOATING_ROCKS_5' or
   type(id)=='string' and (id:match('^FLOATING_ROCKS_[12346789]1$') or
    id:match('^FLOATING_ROCKS_[1379]I$')) then
   if g.type=='floor' and g.subtype=='rocks' and g.name=='floating rocks' and
    g.display=='.' and g._noalpha==false and not g.does_block_move and
    not g.block_sight and not g.dig and not g.can_pass and not g.add_displays and
    type(g.image)=='string' and g.image:match('^terrain/floating_rocks[%w_]+%.png$') then return 'rocks' end
  end
  if not pointZero then return end
 end
 if zoneName~='unhallowed-morass' and zoneName~='temporal-rift' and not pointZero then return end
 if (zoneName=='temporal-rift' or pointZero) and file~='/data/general/grids/void.lua' then return end
 if id=='VOID' and file=='/data/general/grids/void.lua' and
  g.type=='floor' and g.subtype=='void' and g.name=='void' and
  g.display==' ' and g._noalpha==false and not g.image and
  not g.does_block_move and not g.block_sight and not g.dig and
  not g.can_pass and not g.pass_projectile and not g.air_level and
  not g.add_displays then return 'floor' end
 if id=='SPACETIME_RIFT' and
  (file=='/data/general/grids/void.lua' or
   zoneName=='unhallowed-morass' and file=='/data/zones/unhallowed-morass/grids.lua') and
  g.type=='wall' and g.subtype=='rift' and g.name=='crack in spacetime' and
  g.display=='#' and g.does_block_move==true and g._noalpha==false and
  (g.block_sight==true)==(file=='/data/zones/unhallowed-morass/grids.lua') and
  not g.dig and not g.can_pass and not g.air_level and
  nativeRiftArt(g) then return 'rift' end
end
M.voidTerrain=voidTerrain

-- Abashed Expanse imports the ordinary burnt tree but remaps its ground image
-- to a floating rock. Keep that exact appearance separate from Spellblaze.
local function abashedTreeKind(g)
 if not g or not g._checker_burnt_source or
  g._checker_burnt_source.file~='/data/general/grids/burntland.lua' or
  g._checker_burnt_source.id~=g.define_as or
  (g.replace_display and (not g._checker_terrain or g.replace_display~=g._checker_terrain.display)) or
  g.on_stand or g.on_dig or rawget(g,'block_move') or g.special or g.shader or
  g.change_level or g.change_zone or g.block_sense or g.block_esp then return end
 local id=g.define_as
 local n=type(id)=='string' and tonumber(id:match('^BURNT_TREE(%d+)$'))
 if id~='BURNT_TREE' and not (n and n>=1 and n<=20) then return end
 if g.type~='wall' or g.subtype~='burnt' or g.name~='burnt tree' or
  g.image~='terrain/floating_rocks05_01.png' or g.display~='#' or
  g.does_block_move~=true or g.block_sight~=true or
  g.always_remember~=true or g.dig~='BURNT_GROUND1' or
  not g.can_pass or g.can_pass.pass_tree~=1 or g.add_mos and #g.add_mos>0 then return end
 for _,d in ipairs(g.add_displays or {}) do
  if d.image~='invis.png' and not (type(d.image)=='string' and
   (d.image:match('^terrain/trees/burned_tree_[%w_]+%.png$') or
    d.image:match('^terrain/trees/small_burned_tree_[%w_]+%.png$'))) then return end
  for _,mo in ipairs(d.add_mos or {}) do
   if type(mo.image)~='string' or not (mo.image:match('^terrain/trees/burned_tree_[%w_]+%.png$') or
    mo.image:match('^terrain/trees/small_burned_tree_[%w_]+%.png$')) then return end
  end
 end
 return 'rocks-tree'
end
M.abashedTreeKind=abashedTreeKind

-- Crystal grids are also used outside Scintillating Caves. Require their
-- exact source stamp, identity and native display/rule contract, then gate
-- the caller by zone. The replacement display owns the entire crystal wall:
-- native makeCrystals layers would duplicate its faceted face.
local crystalLadders={
 CRYSTAL_LADDER_UP={'ladder-up',-1,nil,'terrain/crystal_ladder_up.png'},
 CRYSTAL_LADDER_DOWN={'ladder-down',1,nil,'terrain/crystal_ladder_down.png'},
 CRYSTAL_LADDER_UP_WILDERNESS={'ladder-world',1,'wilderness','terrain/crystal_ladder_up.png'},
}
local function crystalTerrain(g)
 if not g or type(g.define_as)~='string' or
  not g._checker_crystal_source or g._checker_crystal_source.id~=g.define_as or
  g.subtype~='underground' or g.shader or g.textures or g.special or
  g.block_sense or g.block_esp or g.add_mos or g.on_stand or g.on_dig or
  (g.replace_display and (not g._checker_terrain or g.replace_display~=g._checker_terrain.display)) then return end
 local id=g.define_as
 local floor=id=='CRYSTAL_FLOOR' or tonumber(id:match('^CRYSTAL_FLOOR(%d+)$'))
 local wall=id=='CRYSTAL_WALL' or tonumber(id:match('^CRYSTAL_WALL(%d+)$'))
 if floor then
  if floor~=true and (floor<1 or floor>8) then return end
  if g.type=='floor' and g.name=='floor' and not g.does_block_move and not g.block_sight and
   not g.can_pass and not g.dig and not g.change_level and not g.change_zone and
   not g.add_displays and type(g.image)=='string' and
   g.image:match('^terrain/crystal_floor[1-8]%.png$') then return 'floor' end
 elseif wall then
  if wall~=true and (wall<2 or wall>20) then return end
  if g.type~='wall' or g.name~='crystals' or g.does_block_move~=true or
   g.block_sight~=true or g.always_remember~=true or g.dig~='CRYSTAL_FLOOR' or
   not g.can_pass or g.can_pass.pass_wall~=1 or g.change_level or g.change_zone or
   g.image~='terrain/crystal_floor1.png' or not g.add_displays or
   #g.add_displays<1 or #g.add_displays>3 then return end
  for _,d in ipairs(g.add_displays) do
   if type(d.image)~='string' or not d.image:match('^terrain/crystal_alpha[1-6]%.png$') or
    d.z==nil or d.z<16 or d.z>18 then return end
  end
  return 'wall'
 elseif crystalLadders[id] then
  local d=crystalLadders[id]
  if g.type=='floor' and g.name and not g.does_block_move and not g.block_sight and
   not g.can_pass and not g.dig and g.image=='terrain/crystal_floor1.png' and
   g.change_level==d[2] and g.change_zone==d[3] and g.notice==true and
   (g.always_remember==true)==(id~='CRYSTAL_LADDER_UP_WILDERNESS') and
   g.add_displays and #g.add_displays==1 and g.add_displays[1].image==d[4] then return d[1] end
 end
end
crystalTerrain=ringAware(crystalTerrain)
M.crystalTerrain=crystalTerrain
-- Old Forest CRYSTALINE: the crystaline-forest event turns forest cells inside
-- a clearing into crystal.lua floors/walls (events/crystaline-forest.lua).
-- Walls must be the event's own stamped copies; floors may also have been
-- rerolled by NicerTiles from the zone's own crystal.lua import (the event's
-- CRYSTAL_FLOORn keeps the native replace nice_tiler). Ladders never come
-- from that event and keep their native display here.
function M.markCrystalOrigin(g,origin)
 local stamp=g and g._checker_crystal_source
 if stamp and stamp.file=='/data/general/grids/crystal.lua' and stamp.id==g.define_as then stamp.origin=origin end
end
local function oldForestCrystal(g)
 local kind=crystalTerrain(g)
 if kind~='floor' and kind~='wall' then return end
 local origin=g._checker_crystal_source.origin
 if origin=='crystaline-forest' or (kind=='floor' and origin=='old-forest-zone') then return kind end
end
M.oldForestCrystal=oldForestCrystal
-- T9: Old Forest L4's only down exit. Both layouts define the same grid in
-- their zone file, differing only in the base grass image.
local oldForestExitImages={['terrain/grass/dark_grass_main_01.png']=true,['terrain/grass.png']=true}
function M.oldForestExit(g)
 local stamp=g and g._checker_oldforest_source
 return stamp and stamp.file=='/data/zones/old-forest/grids.lua' and stamp.id=='LAKE_NUR' and
  g.define_as=='LAKE_NUR' and g.image==stamp.image and oldForestExitImages[g.image] and
  g.name=='way to the lake of Nur' and g.display=='>' and g.notice==true and
  g.always_remember==true and g.change_zone=='lake-nur' and g.change_level==1 and
  g.change_level_check==nil and g.change_level_abs==nil and g.force_down==nil and
  g.keep_old_lev==nil and g.change_zone_auto_stairs==nil and g.change_level_auto_stairs==nil and
  g.change_level_shift_back==nil and g.type==nil and g.subtype==nil and
  g.add_displays and #g.add_displays==1 and g.add_displays[1].image=='terrain/way_next_2.png' and
  not g.add_displays[1].add_mos and not g.does_block_move and not g.block_sight and
  not rawget(g,'block_move') and not rawget(g,'on_move') and not g.add_mos and
  not g.on_stand and not g.shader and not g.tint and not g.special and 'exit' or nil
end

-- cave.lua is shared by many zones; this suite is limited to the one
-- verified Static/Roomer composite map. NicerTiles may change wall display
-- parts, but every accepted part must still be a native cave wall texture.
local caveSource='/data/general/grids/cave.lua'
local function caveArt(g,wall)
 local function allowed(path)
  if type(path)~='string' then return false end
  if wall then return path:match('^terrain/cave/cavewall_[%w_]+%.png$') or
   path:match('^terrain/cave/cave_[%w_]+%.png$') end
  return path:match('^terrain/cave/cave_floor_%d+_01%.png$')~=nil
 end
 if not allowed(g.image) and not (wall and g.image=='terrain/cave/cave_floor_1_01.png' and
  g.add_displays and #g.add_displays>0) then return false end
 for _,mo in ipairs(g.add_mos or {}) do
  if type(mo.image)~='string' or not (mo.image:match('^terrain/cave/cave_rock_%d+_01%.png$') or
   mo.image:match('^terrain/cave/cave_mushroom_%d+_01%.png$')) then return false end
 end
 for _,d in ipairs(g.add_displays or {}) do
  if d.image~='invis.png' and not allowed(d.image) then return false end
  for _,mo in ipairs(d.add_mos or {}) do if not allowed(mo.image) then return false end end
 end
 return true
end
local function caveTerrain(g)
 if not g or type(g.define_as)~='string' or not g._checker_cave_source or
  g._checker_cave_source.id~=g.define_as or g._checker_cave_source.file~=caveSource or
  g.subtype~='cave' or g.shader or g.textures or g.special or g.on_stand or g.on_dig or
  g.block_sense or g.block_esp or
  (g.replace_display and (not g._checker_terrain or g.replace_display~=g._checker_terrain.display)) then return end
 local id=g.define_as
 local n=tonumber(id:match('^CAVEFLOOR(%d+)$'))
 if id=='CAVEFLOOR' or n and n>=1 and n<=18 then
  if g.type~='floor' or g.name~='cave floor' or g.display~='.' or
   g.does_block_move or g.block_sight or g.can_pass or g.dig or
   g.change_level or g.change_zone or g.add_displays or g.air_level or
   not caveArt(g,false) then return end
  local mos=g.add_mos
  if n and n>=8 then
   if not mos or #mos~=1 then return end
   local expected=n<=16 and ('terrain/cave/cave_rock_'..(n-7)..'_01.png') or
    ('terrain/cave/cave_mushroom_'..(n-16)..'_01.png')
   if mos[1].image~=expected then return end
  elseif mos then return end
  return 'floor'
 elseif id=='CAVEWALL' then
  if g.type~='wall' or g.name~='cave walls' or g.display~='#' or
   g.does_block_move~=true or g.block_sight~=true or g.always_remember~=true or
   g.air_level~=-10 or g.dig~='CAVEFLOOR' or not g.can_pass or
   g.can_pass.pass_wall~=1 or g.change_level or g.change_zone or
   g.add_mos or not caveArt(g,true) then return end
  return 'wall'
 elseif id=='CAVE_LADDER_UP_WILDERNESS' or id=='CAVE_LADDER_UP' or id=='CAVE_LADDER_DOWN' then
  local world=id=='CAVE_LADDER_UP_WILDERNESS'
  local up=id=='CAVE_LADDER_UP'
  local expectedImage=id=='CAVE_LADDER_DOWN' and 'terrain/cave/cave_stairs_down_3_01.png' or 'terrain/cave/cave_stairs_up_2_01.png'
  local expectedName=world and 'ladder to worldmap' or up and 'ladder to the previous level' or 'ladder to the next level'
  if g.type~='floor' or g.name~=expectedName or g.display~=(id=='CAVE_LADDER_DOWN' and '>' or '<') or
   g.does_block_move or g.block_sight or g.dig or g.can_pass or g.add_mos or
   g.image~='terrain/cave/cave_floor_1_01.png' or g.change_level~=(up and -1 or 1) or
   g.change_zone~=(world and 'wilderness' or nil) or g.notice~=true or
   (g.always_remember==true)~=not world or
   not g.add_displays or #g.add_displays~=1 or
   g.add_displays[1].image~=expectedImage then return end
  return world and 'ladder-world' or up and 'ladder-up' or 'ladder-down'
 end
end
caveTerrain=ringAware(caveTerrain)
M.caveTerrain=caveTerrain

function M.lakeExit(g)
 return g and g.define_as=='OLD_FOREST' and g.name=='way to the old forest' and
  g.display=='<' and g.notice==true and g.always_remember==true and
  g.change_zone=='old-forest' and g.change_level==4 and g.force_down==true and
  g.change_level_check==nil and g.image=='terrain/grass.png' and
  g.add_displays and #g.add_displays==1 and g.add_displays[1].image=='terrain/way_next_8.png' and
  not g.does_block_move and not g.block_sight and not g.add_mos and
  not g.on_stand and not g.shader and not g.tint and 'exit' or nil
end

-- Lake Nur's lower levels are a separate underwater family. The source stamp
-- prevents an unrelated zone's similarly named room grid from inheriting art.
local function nativeUnderwaterLayers(g)
 for _,d in ipairs(g.add_displays or {}) do
  if type(d.image)~='string' or
   (d.image~='invis.png' and not d.image:match('^terrain/underwater/subsea_[%w_]+%.png$')) then return false end
  for _,mo in ipairs(d.add_mos or {}) do
   if type(mo.image)~='string' or
    not mo.image:match('^terrain/underwater/subsea_[%w_]+%.png$') then return false end
  end
 end
 return true
end
local function underwaterKind(g)
 -- Murgol Lair L1's world exit: the one reviewed underwater transition that
 -- leaves the zone. No level check or alternate destination is accepted.
 if g and g.define_as=='WATER_UP_WILDERNESS' then
  local s=g._checker_water_source
  if s and s.file=='/data/general/grids/water.lua' and s.id=='WATER_UP_WILDERNESS' and s.image==g.image and
   g.type=='floor' and g.subtype=='water' and g.name=='exit to the worldmap' and g.display=='<' and
   g.change_level==1 and g.change_zone=='wilderness' and g.notice==true and g.always_remember==true and
   g.air_level==-5 and g.air_condition=='water' and g.image=='terrain/underwater/subsea_floor_02.png' and
   g.add_mos and #g.add_mos==1 and g.add_mos[1].image=='terrain/underwater/subsea_stair_up_wild.png' and
   not g.add_displays and not g.does_block_move and not g.block_sight and not g.dig and not g.can_pass and
   not g.change_level_check and not g.change_level_abs and not g.keep_old_lev and not g.force_down and
   not g.change_zone_auto_stairs and not g.change_level_auto_stairs and not g.change_level_shift_back and
   not g.shader and not g.tint and not g.on_stand and not g.on_dig and not g.special and
   not rawget(g,'block_move') and not rawget(g,'on_move') then return 'stairs-world' end
  return
 end
 -- S4/T1: the air bubble keeps its native on_stand (charge, swap back);
 -- M.bubbleKind (below, with the S2 specs) is its exact contract.
 if g and g.define_as=='WATER_FLOOR_BUBBLE' then return M.bubbleKind(g) end
 if not g or not g._checker_water_source or
  g._checker_water_source.file~='/data/general/grids/water.lua' or
  g._checker_water_source.id~=g.define_as or
  g._checker_water_source.image~=g.image or
  g.shader or g.tint or g.on_stand or g.on_dig or g.change_zone or
  g.change_level_check or g.special or not nativeUnderwaterLayers(g) then return end
 local id=g.define_as
 if (id=='WATER_FLOOR' or type(id)=='string' and id:match('^WATER_FLOOR[1-5]$')) and
  g.type=='floor' and g.subtype=='underwater' and g.name=='underwater' and
  g.air_level==-5 and g.air_condition=='water' and not g.does_block_move and
  not g.block_sight and not g.add_mos and not g.add_displays and
  type(g.image)=='string' and g.image:match('^terrain/underwater/subsea_floor_02[a-e]?%.png$') then return 'floor' end
 local wallId=id=='WATER_WALL' or type(id)=='string' and
  ((id:match('^WATER_WALL[1-5]$') or id:match('^WATER_WALL_NORTH[1-5]$') or
    id:match('^WATER_WALL_PILLAR_8[1-5]$') or id:match('^WATER_WALL_SOUTH%d+$') and
    tonumber(id:match('^WATER_WALL_SOUTH(%d+)$'))<=14) or
   id=='WATER_WALL_NORTH_SOUTH' or id=='WATER_WALL_SOUTH' or
   id=='WATER_WALL_SMALL_PILLAR' or id=='WATER_WALL_PILLAR_2' or
   id=='WATER_WALL_PILLAR_4' or id=='WATER_WALL_PILLAR_6')
 if wallId and
  g.type=='wall' and g.subtype=='underwater' and g.name=='coral wall' and
  g.does_block_move==true and g.block_sight==true and g.air_level==-20 and
  g.dig=='WATER_FLOOR' and g.can_pass and g.can_pass.pass_wall==1 and
  not g.air_condition and not g.change_level and
  type(g.image)=='string' and g.image:match('^terrain/underwater/subsea_[%w_]+%.png$') then return 'wall' end
 local doors={WATER_DOOR={'closed','WATER_DOOR_OPEN','WATER_FLOOR'},
  WATER_DOOR_HORIZ={'closed','WATER_DOOR_HORIZ_OPEN','WATER_FLOOR'},
  WATER_DOOR_VERT={'closed','WATER_DOOR_OPEN_VERT','WATER_DOOR_OPEN_VERT'},
  WATER_DOOR_OPEN={'open','WATER_DOOR'},WATER_DOOR_HORIZ_OPEN={'open','WATER_DOOR_HORIZ'},
  WATER_DOOR_OPEN_VERT={'open','WATER_DOOR_VERT'}}
 local d=doors[id]
 if d and g.type=='wall' and g.subtype=='underwater' and g.is_door==true and
  g.air_level==-5 and g.air_condition=='water' and not g.does_block_move and
  not g.change_level and type(g.image)=='string' and
  g.image:match('^terrain/underwater/subsea_[%w_]+%.png$') then
  if d[1]=='closed' and g.block_sight==true and g.door_opened==d[2] and
   g.dig==d[3] and not g.door_closed then return 'door-closed' end
  if d[1]=='open' and not g.block_sight and g.door_closed==d[2] and
   not g.dig and not g.door_opened then return 'door-open' end
 end
 local stair=id=='WATER_UP' and -1 or id=='WATER_DOWN' and 1
 if stair and g.type=='floor' and g.subtype=='water' and g.air_level==-5 and
  g.air_condition=='water' and g.change_level==stair and not g.does_block_move and
  not g.block_sight and g.notice==true and g.always_remember==true and
  g.image=='terrain/underwater/subsea_floor_02.png' and g.add_mos and
  #g.add_mos==1 and g.add_mos[1].image==(stair==-1 and
   'terrain/underwater/subsea_stair_up.png' or 'terrain/underwater/subsea_stair_down_03_64.png') then
  return stair==-1 and 'stairs-up' or 'stairs-down'
 end
end
M.underwaterKind=underwaterKind

local function surfaceSandKind(g)
 if not g or not g._checker_surface_sand_source or
  g._checker_surface_sand_source.file~='/data/general/grids/sand.lua' or
  g._checker_surface_sand_source.id~='SAND' or g.define_as~='SAND' or
  g.type~='floor' or g.subtype~='sand' or g.name~='sand' or
  g.image~='terrain/sandfloor.png' or g.display~='.' or
  g.grow~='SANDWALL_STABLE' or g.does_block_move or g.block_sight or
  g.on_stand or g.on_dig or g.add_mos or
  g.change_level or g.change_zone or g.shader or g.tint then return end
 if g.add_displays then
  if #g.add_displays~=1 or g.add_displays[1].image~='invis.png' or
   not g.add_displays[1].add_mos or #g.add_displays[1].add_mos<1 then return end
  for _,mo in ipairs(g.add_displays[1].add_mos) do
   if type(mo.image)~='string' or
    not mo.image:match('^terrain/sand/sand_[%w_]+%.png$') then return end
  end
 end
 return 'surface-sand'
end
M.surfaceSandKind=surfaceSandKind

local function graveyardProp(g)
 if not g or not g._checker_grave_source or
  g._checker_grave_source.file~='/data/zones/last-hope-graveyard/grids.lua' or
  g._checker_grave_source.id~=g.define_as or
  g._checker_grave_source.image~=g.image or
  g._checker_grave_source.block_move~=rawget(g,'block_move') or
  g._checker_grave_source.on_added~=g.on_added or
  g._checker_grave_source.change_level~=g.change_level or
  g._checker_grave_source.lore~=g.lore or
  g.on_stand or g.on_dig or g.change_zone or g.shader or g.tint or g.special then return end
 local id=g.define_as
 local graveN=type(id)=='string' and tonumber(id:match('^GRAVE(%d+)$'))
 if graveN and graveN>=1 and graveN<=44 and
  g.type=='wall' and g.subtype=='grass' and g.name=='grave' and
  g.display=='&' and g.image=='terrain/grass.png' and
  g.does_block_move==true and g.pass_projectile==true and
  type(g.block_move)=='function' and not g.on_added and
  not g.change_level and not g.block_sight and
  g.lore=='last-hope-graveyard-'..graveN and not g.add_mos and g.add_displays then
  local markers=0
  for _,d in ipairs(g.add_displays) do
   if d.z==18 and d.display_y==-1 and d.display_h==2 and
    type(d.image)=='string' and d.image:match('^terrain/grave_unopened_0[1-3]_64%.png$') then
    markers=markers+1
   elseif d.image=='invis.png' and d.add_mos and #d.add_mos==1 and
    type(d.add_mos[1].image)=='string' and
    d.add_mos[1].image:match('^terrain/grass/grass_[1-9]_0[1-2]%.png$') then
    -- Native NicerTiles may add a grass border under the marker.
   else return end
  end
  if markers==1 then return 'grave' end
 end
 if (id=='COFFIN' or id=='COFFIN_OPEN') and g.type=='floor' and
  g.image=='terrain/marble_floor.png' and g.does_block_move==true and
  g.pass_projectile==true and not g.change_level and
  not g.add_displays and g.add_mos and #g.add_mos==1 then
  local mo=g.add_mos[1]
  if mo.display_h==2 and mo.display_y==-1 and
   (id=='COFFIN' and g.name=='coffin' and g.display=='&' and
    g.force_clone==true and type(g.on_added)=='function' and
    type(g.block_move)=='function' and
    mo.image=='terrain/coffin_unopened_01_64.png') then return 'coffin' end
  if id=='COFFIN_OPEN' and g.name=='open coffin' and g.display=='/' and
   not g.on_added and not rawget(g,'block_move') and
   mo.image=='terrain/coffin_opened_01_64.png' then return 'coffin-open' end
 end
 if id=='MAUSOLEUM' and g.type=='floor' and g.subtype=='floor' and
  g.name=='open mausoleum' and g.display=='>' and
  g.image=='terrain/stone_road1.png' and g.notice==true and
  g.always_remember==true and g.change_level==1 and
  not g.on_added and not rawget(g,'block_move') and
  not g.does_block_move and not g.block_sight and not g.add_mos and
  g.add_displays and #g.add_displays==1 and
  g.add_displays[1].z==5 and
  g.add_displays[1].image=='terrain/dungeon_entrance01.png' then return 'mausoleum' end
 if rawget(g,'block_move') or g.on_added or g.change_level then return end
 if id=='ROAD' and g.type=='floor' and g.subtype=='road' and
  g.name=='cobblestone road' and g.image=='terrain/stone_road1.png' and
  not g.does_block_move and not g.block_sight and not g.add_mos and
  not g.add_displays then return 'road' end
 if (id=='SWAMPTREE' or type(id)=='string' and id:match('^SWAMPTREE%d+$') and
  tonumber(id:match('%d+$'))<=20) and g.type=='wall' and
  g.subtype=='grass' and g.name=='tree' and g.does_block_move==true and
  g.block_sight==true and g.dig=='GRASS' and g.can_pass and
  g.can_pass.pass_tree==1 and not g.add_mos and
  (g.image=='terrain/tree.png' or g.image=='terrain/grass.png') then
  for _,d in ipairs(g.add_displays or {}) do
   if type(d.image)~='string' or
    (d.image~='invis.png' and not d.image:match('^terrain/swamptree[%w_]*%.png$')) then return end
   for _,mo in ipairs(d.add_mos or {}) do
    if type(mo.image)~='string' or
     not mo.image:match('^terrain/swamptree[%w_]*%.png$') and
     not (d.image=='invis.png' and
      mo.image:match('^terrain/grass/grass_[1-9]_0[1-2]%.png$')) then return end
   end
  end
  return 'swamp-tree'
 end
end
M.graveyardProp=graveyardProp

-- Norgos imports mountain.lua with a zone-local snowy-ground image rewrite.
-- Match the final Grid contract and explicit ids; subtype "rock" also covers
-- cliffside and mountain walls, which have different movement/sight rules.
local rockyExits={
 ROCKY_UP_WILDERNESS={'stairs-world',1,'wilderness','terrain/worldmap.png'},
 ROCKY_UP2={'stairs-up',-1,nil,'terrain/way_next_2.png'},
 ROCKY_UP4={'stairs-up',-1,nil,'terrain/way_next_4.png'},
 ROCKY_UP6={'stairs-up',-1,nil,'terrain/way_next_6.png'},
 ROCKY_UP8={'stairs-up',-1,nil,'terrain/way_next_8.png'},
 ROCKY_DOWN2={'stairs-down',1,nil,'terrain/way_next_2.png'},
 ROCKY_DOWN4={'stairs-down',1,nil,'terrain/way_next_4.png'},
 ROCKY_DOWN6={'stairs-down',1,nil,'terrain/way_next_6.png'},
 ROCKY_DOWN8={'stairs-down',1,nil,'terrain/way_next_8.png'},
}
local function nativeSnowTreeParts(g)
 local function validMos(list)
  if not list then return true end
  for _,mo in ipairs(list) do
   if type(mo.image)~='string' or not mo.image:match('^terrain/trees/[%w_]+%.png$') then return false end
  end
  return true
 end
 if not validMos(g.add_mos) then return false end
 if not g.add_displays then return g.define_as=='ROCKY_SNOWY_TREE' end
 if #g.add_displays<2 or g.add_displays[1].image~='invis.png' or
  not validMos(g.add_displays[1].add_mos) then return false end
 for i=2,#g.add_displays do
  local part=g.add_displays[i]
  if type(part.image)~='string' or not part.image:match('^terrain/trees/[%w_]+%.png$') then return false end
 end
 return true
end
local function nativeDaikaraWallParts(g)
 if not g.add_displays then return true end
 local ds=g.add_displays
 if #ds<2 or ds[1].image~='invis.png' or ds[2].image~=g.image or ds[2].z~=3 then return false end
 for _,mo in ipairs(ds[1].add_mos or {}) do
  if type(mo.image)~='string' or not mo.image:match('^terrain/mountain%d+i?%.png$') then return false end
 end
 for _,mo in ipairs(ds[2].add_mos or {}) do
  if type(mo.image)~='string' or not mo.image:match('^terrain/mountain%d+i?%.png$') then return false end
 end
 for i=3,#ds do
  local d=ds[i]
  if type(d.image)~='string' or not d.image:match('^terrain/mountain%d+%.png$') or
   (d.z~=16 and d.z~=17 and d.z~=18) or d.add_mos then return false end
 end
 return true
end
local function nativeDaikaraLavaParts(g)
 if not g.add_displays then return true end
 if #g.add_displays~=1 or g.add_displays[1].image~='invis.png' then return false end
 for _,mo in ipairs(g.add_displays[1].add_mos or {}) do
  if type(mo.image)~='string' or not mo.image:match('^terrain/lava/lava_floor_') or
   not mo.image:match('%d+_%d+%.png$') then return false end
 end
 return true
end
local function rockTerrain(g,daikara)
 if not g or g.subtype~='rock' or
  (daikara and g.image~='terrain/rocky_ground.png' and g.image~='terrain/rocky_snowy_tree.png' and
   g.image~='terrain/rocky_mountain.png' and not (type(g.image)=='string' and g.image:match('^terrain/mountain5_[1-6]%.png$')) or
   not daikara and g.image~='terrain/snowy_grass.png' and g.image~='terrain/rocky_snowy_tree.png') or
  g.shader or g.tint or rawget(g,'on_move') or g.special or
  g.block_sense or g.block_esp then return end
 local aura=M.auraKind(g)
 if g.on_stand and not aura then return end
 local id=g.define_as
 local ground=daikara and 'terrain/rocky_ground.png' or 'terrain/snowy_grass.png'
 if id=='ROCKY_GROUND' and g.image==ground and g.type=='floor' and
  (g.name=='rocky ground' or (aura and g.display=='.')) and
  g.display=='.' and not g.does_block_move and not g.block_sight and
  not g.dig and not g.can_pass and not g.add_displays and not g.add_mos and
  not g.change_level and not g.change_zone and not g.air_level then return daikara and 'rock-ground' or 'snow-ground' end
 if type(id)=='string' and (id=='ROCKY_SNOWY_TREE' or
  (id:match('^ROCKY_SNOWY_TREE%d+$') and tonumber(id:match('%d+$'))<=30)) and
  g.type=='wall' and g.name=='snowy tree' and g.display=='#' and
  g.does_block_move and g.block_sight and g.dig=='ROCKY_GROUND' and
  g.can_pass and g.can_pass.pass_tree==1 and nativeSnowTreeParts(g) and
  not g.change_level and not g.change_zone and not g.air_level then return 'snow-tree' end
 if daikara and type(id)=='string' and (id=='MOUNTAIN_WALL' or
  (id:match('^MOUNTAIN_WALL[1-6]$'))) and g.type=='rockwall' and
  g.name=='rocky mountain' and g.display=='#' and g.does_block_move and
  g.block_sight and g.air_level==-20 and g.dig=='ROCKY_GROUND' and
  g.can_pass and g.can_pass.pass_wall==1 and nativeDaikaraWallParts(g) and
  not g.add_mos and not g.change_level and not g.change_zone then return 'mountain-wall' end
 local exit=rockyExits[id]
 if exit and not g.on_stand and g.image==ground and g.type=='floor' and
  not g.change_level_check and not g.change_level_abs and
  not g.change_level_auto_stairs and not g.change_zone_auto_stairs and
  not g.change_level_shift_back and not g.keep_old_lev and not g.force_down and
  not g.does_block_move and not g.block_sight and not g.add_mos and
  not g.dig and not g.can_pass and g.change_level==exit[2] and
  g.change_zone==exit[3] and g.add_displays and #g.add_displays==1 and
  g.add_displays[1].image==exit[4] and not g.add_displays[1].add_mos and
  not g.air_level and g.display==(exit[2]==1 and exit[3] and '<' or exit[2]==1 and '>' or '<') then
  return exit[1]
 end
end
M.rockKind=rockTerrain -- read-only identity probe for fixture census and contract tests
local function lavaTerrain(g)
 if not g or g.subtype~='lava' or g.type~='floor' or g.name~='lava floor' or
  g.display~='.' or g.shader~='lava' or g.on_stand or g.does_block_move or
  g.block_sight or g.block_sense or g.block_esp or g.dig or g.can_pass or
  not nativeDaikaraLavaParts(g) or g.add_mos or g.change_zone or g.special then return end
 local id=g.define_as
 if id~='LAVA_FLOOR' and not (type(id)=='string' and id:match('^LAVA_FLOOR%d+$') and
  tonumber(id:match('%d+$'))<=16) then return end
 if g.image~='terrain/lava_floor.png' and not (type(g.image)=='string' and
  g.image:match('^terrain/lava/lava_floor%d+%.png$')) then return end
 if g.change_level then return end
 return 'lava-floor'
end
lavaTerrain=ringAware(lavaTerrain)
M.lavaKind=lavaTerrain

local dirs={{0,-1},{1,0},{0,1},{-1,0}}

-- Batch 4 (Southern Beach, Tranquil Meadow, Dogroth/Noxious Caldera). Every
-- kind requires the exact source stamp or identity, the native rule fields and
-- only the native layer images observed in the source probe. Callback grids
-- are accepted only where the callback is the unchanged native function
-- (same defining file and line); the adapter never touches it.
local forestSource='/data/general/grids/forest.lua'
local waterSource='/data/general/grids/water.lua'
local jungleSource='/data/general/grids/jungle.lua'
local keepsakeSource='/data/zones/keepsake-meadow/grids.lua'
local beachSource='/data/zones/south-beach/grids.lua'
local transitionKeys={'change_level','change_zone','change_level_check','change_level_abs','keep_old_lev',
 'force_down','change_zone_auto_stairs','change_level_auto_stairs','change_level_shift_back'}
local function noTransition(g)
 for _,k in ipairs(transitionKeys) do if g[k]~=nil then return false end end
 return true
end
local function layersMatch(g,patterns)
 local function ok(path)
  if type(path)~='string' then return false end
  for _,p in ipairs(patterns) do if path:match(p) then return true end end
  return false
 end
 for _,mo in ipairs(g.add_mos or {}) do if not ok(mo.image) then return false end end
 for _,d in ipairs(g.add_displays or {}) do
  if not ok(d.image) then return false end
  for _,mo in ipairs(d.add_mos or {}) do if not ok(mo.image) then return false end end
 end
 return true
end
-- Plain static cell: no callbacks, no special rendering, no air or door rules.
local function plainCell(g)
 return not (g.on_stand or g.on_dig or rawget(g,'block_move') or rawget(g,'on_move') or
  g.on_added or g.special or g.shader or g.tint or g.textures or g.air_level or g.is_door or
  g.block_sense or g.block_esp) and noTransition(g)
end
local function hasMos(g) return g.add_mos and #g.add_mos>0 end
local function stamped(g,field,file)
 local s=g[field]
 return s and s.file==file and s.id==g.define_as
end
-- The stamp records where the native callback was defined. Reference equality
-- would not survive a save/reload; file and line do.
local function sameCallback(fn,source,line)
 if type(fn)~='function' or type(source)~='string' then return false end
 local info=debug.getinfo(fn,'S')
 return info and info.source==source and info.linedefined==line
end
local GRASS_LAYERS={'^invis%.png$','^terrain/grass/grass_[%w_]+%.png$'}
local FLOWER_LAYERS={'^invis%.png$','^terrain/grass/grass_[%w_]+%.png$','^terrain/flower_0[1-6]%.png$','^terrain/mushroom_0[1-7]%.png$'}
local TREE_LAYERS={'^invis%.png$','^terrain/grass/grass_[%w_]+%.png$','^terrain/trees/[%w_]+%.png$'}
local ROAD_LAYERS={'^invis%.png$','^terrain/grass/grass_[%w_]+%.png$','^terrain/road_oldstone/[%w_]+%.png$'}
local function numbered(id,prefix,max)
 if id==prefix then return true end
 local n=type(id)=='string' and tonumber(id:match('^'..prefix..'(%d+)$'))
 return n and n>=1 and n<=max or false
end
local function meadowGrass(g)
 local id=g.define_as
 if not stamped(g,'_checker_forest_source',forestSource) or not numbered(id,'GRASS_PATCH',14) and id~='GRASS' then return end
 local patch=tonumber(id:match('^GRASS_PATCH(%d+)$'))
 if g.type~='floor' or g.subtype~='grass' or g.name~='grass' or g.display~='.' or g.grow~='TREE' or
  g.does_block_move or g.block_sight or g.dig or g.can_pass or g.road or hasMos(g) or not plainCell(g) or
  not (g.image=='terrain/grass.png' or patch and g.image==('terrain/grass/grass_main_%02d.png'):format(patch)) or
  not layersMatch(g,GRASS_LAYERS) then return end
 return 'grass'
end
local function meadowFlower(g)
 if not stamped(g,'_checker_forest_source',forestSource) or not numbered(g.define_as,'FLOWER',13) or
  g.type~='floor' or g.subtype~='grass' or g.name~='flower' or g.display~=';' or g.grow~='TREE' or
  g.does_block_move or g.block_sight or g.dig or g.can_pass or g.road or not plainCell(g) or
  (g.image~='terrain/grass.png' and g.image~='terrain/flower.png') or not layersMatch(g,FLOWER_LAYERS) then return end
 return 'flower'
end
local function forestTree(g,hard)
 local base=hard and 'HARDTREE' or 'TREE'
 if not stamped(g,'_checker_forest_source',forestSource) or not numbered(g.define_as,base,30) or
  g.type~='wall' or g.subtype~='grass' or g.display~='#' or g.always_remember~=true or
  g.does_block_move~=true or g.block_sight~=true or g.road or hasMos(g) or
  g.on_stand or g.on_dig or rawget(g,'block_move') or rawget(g,'on_move') or g.on_added or g.special or
  g.shader or g.tint or g.textures or g.air_level or g.is_door or not noTransition(g) or
  (g.image~='terrain/grass.png' and g.image~='terrain/tree.png') or not layersMatch(g,TREE_LAYERS) then return end
 if hard then
  if g.name=='tall thick tree' and g.block_sense==true and g.block_esp==true and not g.dig and not g.can_pass then return 'hardtree' end
  return
 end
 if g.name~='tree' or g.block_sense or g.block_esp or g.dig~='GRASS' or not g.can_pass or g.can_pass.pass_tree~=1 then return end
 for k in pairs(g.can_pass) do if k~='pass_tree' then return end end
 return 'tree'
end
local deepImages={DEEP_WATER='terrain/water_grass_5_1.png',DEEP_OCEAN_WATER='terrain/ocean_water_grass_5_1.png'}
local function deepWater(g)
 local image=deepImages[g.define_as]
 local s=g._checker_water_source
 if not image or not stamped(g,'_checker_water_source',waterSource) or s.image~=g.image or g.image~=image or
  g.type~='floor' or g.subtype~='water' or g.name~='deep water' or g.display~='~' or
  g.always_remember~=true or g.shader~='water' or g.air_level~=-5 or g.air_condition~='water' or
  g.does_block_move or g.block_sight or g.dig or g.can_pass or hasMos(g) or g.add_displays or
  g.on_stand or g.on_dig or rawget(g,'block_move') or rawget(g,'on_move') or g.special or g.tint or
  g.is_door or not noTransition(g) then return end
 return 'deep'
end
local function stoneRoad(g)
 if g.define_as~='GRASS_ROAD_STONE' or not stamped(g,'_checker_forest_source',forestSource) or
  g.type~='floor' or g.subtype~='grass' or g.road~='oldstone' or g.name~='old road' or g.display~='=' or
  g.image~='terrain/grass.png' or g.always_remember~=true or g.does_block_move or g.block_sight or
  g.dig or g.can_pass or hasMos(g) or not plainCell(g) or not layersMatch(g,ROAD_LAYERS) then return end
 return 'road'
end
local function beachProp(g)
 local id=g.define_as
 if (id~='UMBRELLA' and id~='BASKET') or not stamped(g,'_checker_beach_source',beachSource) or
  g.type~='floor' or g.subtype~='sand' or g.image~='terrain/sandfloor.png' or g.grow~='SANDWALL_STABLE' or
  g.block_sight or g.dig or g.can_pass or g.add_displays or not hasMos(g) or #g.add_mos~=1 or
  not plainCell(g) then return end
 if id=='UMBRELLA' and g.name=='lovely umbrella' and g.display=='~' and g.does_block_move==true and
  g.add_mos[1].image=='terrain/picnic_umbrella.png' then return 'umbrella' end
 if id=='BASKET' and g.name=='picnic basket' and g.display=='_' and not g.does_block_move and
  g.add_mos[1].image=='terrain/picnic_basket.png' then return 'basket' end
end
local meadowExits={
 GRASS_UP_WILDERNESS={forestSource,'exit to the worldmap',1,'wilderness','terrain/worldmap.png'},
 GRASS_UP2_UP2={keepsakeSource,'way to the previous level',-2,nil,'terrain/way_next_2.png'},
}
local function meadowExit(g)
 local e=meadowExits[g.define_as]
 if not e or not stamped(g,e[1]==forestSource and '_checker_forest_source' or '_checker_keepsake_source',e[1]) or
  g.type~='floor' or g.subtype~='grass' or g.name~=e[2] or g.display~='<' or
  g.change_level~=e[3] or g.change_zone~=e[4] or g.image~='terrain/grass.png' or
  g.notice~=true or g.always_remember~=true or not hasMos(g) or #g.add_mos~=1 or
  g.add_mos[1].image~=e[5] or g.add_displays or g.does_block_move or g.block_sight or g.dig or g.can_pass or
  g.on_stand or g.on_dig or rawget(g,'block_move') or rawget(g,'on_move') or g.special or g.shader or g.tint then return end
 for i=3,#transitionKeys do if g[transitionKeys[i]]~=nil then return end end
 return 'exit'
end
-- TW1: static towns. A grid must carry the exact provenance of the current
-- town's own grid list (superload/mod/class/Grid.lua) in addition to the
-- general-file stamp and full rule contract of its forest/water identity.
-- Shops, lore posts and quest NPC doors are trap-layer entities over these
-- grids and are never read or touched here.
local townFiles={['town-derth']='/data/zones/town-derth/grids.lua',
 ['town-lumberjack-village']='/data/zones/town-lumberjack-village/grids.lua',
 ['town-last-hope']='/data/zones/town-last-hope/grids.lua',
 ['town-elvala']='/data/zones/town-elvala/grids.lua',
 -- TW3: Zigur, Angolwen (TMX map; its ids resolve through this list) and
 -- the Iron Council.
 ['town-zigur']='/data/zones/town-zigur/grids.lua',
 ['town-angolwen']='/data/zones/town-angolwen/grids.lua',
 ['town-iron-council']='/data/zones/town-iron-council/grids.lua',
 -- TW4: Shatur (snowy and green elven forest, no stone) and Point Zero
 -- (floating rocks in outer space, stone shop blocks).
 ['town-shatur']='/data/zones/town-shatur/grids.lua',
 ['town-point-zero']='/data/zones/town-point-zero/grids.lua',
 -- TW5: Gates of Morning (stone plaza, building blocks, Sunwall mountain ring).
 ['town-gates-of-morning']='/data/zones/town-gates-of-morning/grids.lua',
 -- TW6: Irkkk (jungle, lake, bamboo huts; no stone, forest-only like Shatur).
 ['town-irkkk']='/data/zones/town-irkkk/grids.lua'}
M.townFiles=townFiles
local function townStamped(g,zoneName)
 local file=townFiles[zoneName]
 return file and stamped(g,'_checker_town_source',file) and true or false
end
M.townStamped=townStamped
-- TW2: Last Hope's own FLOOR_ROAD_STONE (town-last-hope/grids.lua:24-32), the
-- old stone road across the marble plaza. Only its native NicerTiles layers
-- are allowed: the oldstone road pattern and the marble-to-water edge.
local PLAZA_ROAD_LAYERS={'^invis%.png$','^terrain/road_oldstone/[%w_]+%.png$',
 '^terrain/marble_water/marble_floor_2_to_water_outer_[1-9]%.png$'}
local function plazaRoad(g)
 if g.define_as~='FLOOR_ROAD_STONE' or g.type~='floor' or g.subtype~='floor' or g.road~='oldstone' or
  g.name~='old road' or g.image~='terrain/marble_floor.png' or g.display~='=' or g.always_remember~=true or
  g.does_block_move or g.block_sight or g.dig or g.grow or g.can_pass or g.notice or g.orb_portal or
  g.pass_projectile or hasMos(g) or not plainCell(g) or not layersMatch(g,PLAZA_ROAD_LAYERS) then return end
 return 'road'
end
-- TW2: mountain.lua HARDMOUNTAIN_WALL (and its nice_tiler HARDMOUNTAIN_WALL1-6)
-- imported by Last Hope. Unlike Daikara's MOUNTAIN_WALL it is undiggable, has
-- no pass_wall and blocks sense/ESP; its own full contract, Daikara art.
local function hardMountain(g)
 local id=g.define_as
 local n=type(id)=='string' and tonumber(id:match('^HARDMOUNTAIN_WALL([1-6])$'))
 if not (id=='HARDMOUNTAIN_WALL' or n) or
  g.image~=(n and ('terrain/mountain5_%d.png'):format(n) or 'terrain/rocky_mountain.png') or
  g.type~='rockwall' or g.subtype~='rock' or g.name~='hard rocky mountain' or g.display~='#' or
  g.always_remember~=true or g.does_block_move~=true or g.block_sight~=true or g.block_sense~=true or
  g.block_esp~=true or g.air_level~=-20 or g.dig or g.grow or g.can_pass or g.pass_projectile or
  g.notice or g.is_door or hasMos(g) or g.on_stand or g.on_dig or rawget(g,'block_move') or
  rawget(g,'on_move') or g.on_added or g.special or g.shader or g.tint or g.textures or
  not noTransition(g) or not nativeDaikaraWallParts(g) then return end
 return 'mountain'
end
-- TW2: Last Hope's four lore statues are map-file quickEntity grids with no
-- define_as and no list stamp. The block_move closure must be the native one
-- (defining file and line) and the single statue layer must be the one that
-- line draws; the prop is redrawn unchanged over the board grass. Tooltip
-- names are translated, so the line and art are the identity, not the name.
-- TW4: Shatur's moss covered statue (shatur.lua:28, thaloren-lament lore) is
-- the same kind of map-file grid; its layer is a plain statue3 image.
local statueMaps={
 ['town-last-hope']={source='@/data/maps/towns/last-hope.lua',z=18,display_y=-1,display_h=2,
  lines={[20]='terrain/statues/statue_tolak.png',[21]='terrain/statues/statue_toknor.png',
   [22]='terrain/statues/statue_mirvenia.png',[23]='terrain/statues/monument_allied_kingdoms.png'}},
 ['town-shatur']={source='@/data/maps/towns/shatur.lua',lines={[28]='terrain/statue3.png'}}}
local function townStatue(g,zoneName)
 local fn=rawget(g,'block_move')
 local spec=statueMaps[zoneName]
 local info=spec and g.define_as==nil and type(fn)=='function' and debug.getinfo(fn,'S')
 local art=info and info.source==spec.source and spec.lines[info.linedefined]
 local d=art and g.add_displays and #g.add_displays==1 and g.add_displays[1]
 if not d or d.image~=art or d.z~=spec.z or d.display_y~=spec.display_y or d.display_h~=spec.display_h or d.display_x or d.display_w or
  d.add_mos or d.add_displays or d.shader or g.image~='terrain/grass.png' or g.display~='@' or
  g.show_tooltip~=true or hasMos(g) or g.type or g.subtype or g.does_block_move or g.block_sight or
  g.block_sense or g.block_esp or g.dig or g.grow or g.can_pass or g.air_level or g.is_door or
  g.on_stand or g.on_dig or rawget(g,'on_move') or g.on_added or g.special or g.shader or g.tint or
  g.textures or g.road or g.notice or not noTransition(g) then return end
 return 'statue',d
end
M.townStatue=townStatue
-- TW3: identities local to one town's own grid list. Each requires that
-- town's exact list stamp (so it never matches in another town or an old
-- save), its full native rule contract and only its native layers.
local function ownTown(g,zoneName) return townStamped(g,zoneName) and g._checker_town_source.file==townFiles[zoneName] end
local function noRuleExtras(g)
 return not (g.dig or g.grow or g.can_pass or g.pass_projectile or g.block_sense or g.block_esp or g.air_level or
  g.is_door or g.notice or g.road or hasMos(g)) and plainCell(g)
end
-- Zigur LAVA (town-zigur/grids.lua:38-44): a harmless lava pit that only
-- blocks movement (no type, damage, shader or sight rule). Burnt lava art.
local function zigurLava(g,zoneName)
 if zoneName~='town-zigur' or g.define_as~='LAVA' or not ownTown(g,zoneName) or g.name~='lava pit' or
  g.display~='~' or g.image~='terrain/lava_floor.png' or g.type or g.subtype or g.always_remember~=true or
  g.does_block_move~=true or g.block_sight or g.add_displays or g.z or not noRuleExtras(g) then return end
 return 'lava'
end
-- Iron Council CRYSTAL_WALL..20 (town-iron-council/grids.lua:23-36): its own
-- copy over old-stone floor, not crystal.lua's. Board crystal-wall masks.
local function councilCrystal(g,zoneName)
 local id=g.define_as
 local n=type(id)=='string' and tonumber(id:match('^CRYSTAL_WALL(%d+)$'))
 if zoneName~='town-iron-council' or not (id=='CRYSTAL_WALL' or n and n>=2 and n<=20) or not ownTown(g,zoneName) or
  g.type~='wall' or g.subtype~='underground' or g.name~='crystals' or g.display~='#' or
  g.image~='terrain/oldstone_floor.png' or g.always_remember~=true or g.does_block_move~=true or
  g.block_sight~=true or g.dig~='CRYSTAL_FLOOR' or not g.can_pass or g.can_pass.pass_wall~=1 or
  g.grow or g.pass_projectile or g.block_sense or g.block_esp or g.air_level or g.is_door or g.notice or
  hasMos(g) or g.z or not g.add_displays or #g.add_displays<1 or #g.add_displays>3 then return end
 for k in pairs(g.can_pass) do if k~='pass_wall' then return end end
 for _,d in ipairs(g.add_displays) do
  if type(d.image)~='string' or not d.image:match('^terrain/crystal_alpha[1-6]%.png$') or
   d.z==nil or d.z<16 or d.z>18 or d.add_mos or d.add_displays then return end
 end
 if g.on_stand or g.on_dig or rawget(g,'block_move') or rawget(g,'on_move') or g.on_added or g.special or
  g.shader or g.tint or g.textures or not noTransition(g) then return end
 return 'crystal'
end
-- Angolwen's fountain basin (town-angolwen/grids.lua:44-64): DEEP_WATER
-- copies that block movement. FOUNTAIN keeps its native lore block_move
-- (defining line 47); FOUNTAIN_MAIN carries the 6x5 fountain statue, which
-- is redrawn unchanged over the board water.
local fountainSource='@/data/zones/town-angolwen/grids.lua'
local function fountainBase(g,zoneName)
 return zoneName=='town-angolwen' and ownTown(g,zoneName) and g.type=='floor' and g.subtype=='water' and
  g.name=='fountain' and g.display=='~' and g.image=='terrain/water_grass_5_1.png' and g.always_remember==true and
  g.shader=='water' and g.air_level==-5 and g.air_condition=='water' and g.does_block_move==true and
  not (g.block_sight or g.dig or g.grow or g.can_pass or g.pass_projectile or g.block_sense or g.block_esp or
   g.is_door or g.notice or g.road or hasMos(g) or g.z or g.on_stand or g.on_dig or rawget(g,'on_move') or
   g.on_added or g.special or g.tint or g.textures) and noTransition(g)
end
local function angolwenFountain(g,zoneName)
 local id=g.define_as
 if (id~='FOUNTAIN' and id~='FOUNTAIN_MAIN') or not fountainBase(g,zoneName) then return end
 if id=='FOUNTAIN' then
  if g.add_displays or not sameCallback(rawget(g,'block_move'),fountainSource,47) then return end
  return 'fountain'
 end
 local d=g.add_displays and #g.add_displays==1 and g.add_displays[1]
 if rawget(g,'block_move') or not d or d.image~='terrain/statues/angolwen_fountain.png' or d.z~=17 or
  d.display_w~=6 or d.display_h~=5 or d.display_x~=-2.5 or d.display_y~=-2 or d.add_mos or d.add_displays or
  d.shader then return end
 return 'fountain',d
end
-- Props over board grass: Zigur's post sign (on_move lore at
-- town-zigur/grids.lua:33) and Angolwen's three magical rocks.
local postSource='@/data/zones/town-zigur/grids.lua'
local function townGrassProp(g,zoneName)
 local id=g.define_as
 local d=g.add_displays and #g.add_displays==1 and g.add_displays[1]
 if not d or d.add_mos or d.add_displays or d.shader or d.display_x or d.display_y or d.display_w or d.display_h or
  g.image~='terrain/grass.png' or not ownTown(g,zoneName) or g.block_sight or g.dig or g.can_pass or
  g.pass_projectile or g.block_sense or g.block_esp or g.air_level or g.is_door or g.notice or g.road or
  hasMos(g) or g.z or g.on_stand or g.on_dig or rawget(g,'block_move') or g.on_added or g.special or
  g.shader or g.tint or g.textures or not noTransition(g) then return end
 if zoneName=='town-zigur' and id=='POST' and g.lore=='zigur-post' and g.display=='_' and g.always_remember==true and
  g.type==nil and g.subtype==nil and not g.does_block_move and not g.grow and
  d.image=='terrain/signpost.png' and d.z==nil and sameCallback(rawget(g,'on_move'),postSource,33) then return 'post',d end
 if zoneName=='town-angolwen' and id=='ROCK' and g.type=='floor' and g.subtype=='floor' and g.display=='.' and
  g.does_block_move==true and g.grow=='WALL' and not rawget(g,'on_move') and
  d.image=='terrain/maze_rock.png' and d.z==4 then return 'rock',d end
end
-- The native world exit where NicerTiles gave it grass-border carriers
-- (Zigur, Angolwen); only those carriers, otherwise meadowExit's contract.
local function townGrassExit(g)
 if g.define_as~='GRASS_UP_WILDERNESS' or not g.add_displays then return end
 for _,d in ipairs(g.add_displays) do
  if d.image~='invis.png' or d.add_displays or d.z or d.display_x or d.display_y or d.shader then return end
  for _,mo in ipairs(d.add_mos or {}) do
   if type(mo.image)~='string' or not mo.image:match('^terrain/grass/grass_[%w_]+%.png$') then return end
  end
 end
 local v={};for k,value in pairs(g) do v[k]=value end;v.add_displays=nil
 return meadowExit(setmetatable(v,getmetatable(g)))
end
-- TW4: Shatur imports elven_forest.lua and snowy_forest.lua (no general-file
-- stamp), so its trees and snow need Shatur's own list stamp. ELVEN_TREE and
-- SNOW_ELVEN_TREE (elven_forest.lua:30-44, :77-91) share the plain tree rules
-- (pass_tree, dig GRASS, no sense/ESP block); the variants' ground image and
-- nice_editer border family tell green from snow. Only the native layers the
-- fixture probe saw: their own grass/snowy-grass borders and tree parts.
local tw4={} -- one upvalue for the TW4 helpers (the chunk's local budget is shared)
-- S8 (V2): stone zones whose diggable WALL (and the door jambs in it) draws
-- the darker brick. Measured in the fixture (evidence/terrain-s8-20260929):
-- every level with a diggable WALL showed the lit Kor'Pul brick brighter than,
-- or within 5% of, the floor beside it; the forest/cave zones get the brick
-- only in stone vaults. Conclave keeps its own dark set; towns and zones with
-- HARDWALL only (Derth, Last Hope, Zigur, Angolwen ...) are unchanged.
tw4.S8_DARK={}
for _,z in ipairs{
 'ruins-kor-pul','rhaloren-camp','dreadfell','thieves-tunnels','halfling-ruins','reknor','reknor-escape',
 'temporal-rift','ruined-dungeon','blighted-ruins','lake-nur','crypt-kryl-feijan','telmur',
 'ancient-elven-ruins','vor-armoury','orc-breeding-pit','old-forest','trollmire','daikara','tempest-peak',
 'scintillating-caves','town-lumberjack-village','shadow-crypt','tannen-tower','ring-of-blood','gorbat-pride',
 'eruan',
 -- S9: High Peak's Roomer levels (L5-10) and the Sanctum's diggable WALL.
 'high-peak'} do tw4.S8_DARK[z]=true end
tw4.ELVEN_TREE_LAYERS={'^invis%.png$','^terrain/grass/grass_[%w_]+%.png$','^terrain/trees/[%w_]+%.png$'}
tw4.SNOW_TREE_LAYERS={'^invis%.png$','^terrain/grass/snowy_grass_[%w_]+%.png$','^terrain/trees/[%w_]+%.png$'}
function tw4.shaturTree(g,zoneName)
 local id=g.define_as
 if zoneName~='town-shatur' or not ownTown(g,zoneName) then return end
 local snow=numbered(id,'SNOW_ELVEN_TREE',30)
 if not snow and not numbered(id,'ELVEN_TREE',30) then return end
 local ground=snow and 'terrain/grass/snowy_grass_main_01.png' or 'terrain/grass/grass_main_01.png'
 if g.type~='wall' or g.subtype~=(snow and 'snowy_grass' or 'grass') or g.name~='tree' or g.display~='#' or
  g.always_remember~=true or g.does_block_move~=true or g.block_sight~=true or g.dig~='GRASS' or
  not g.can_pass or g.can_pass.pass_tree~=1 or g.grow or g.road or g.pass_projectile or g.notice or hasMos(g) or
  not plainCell(g) or (g.image~='terrain/tree.png' and g.image~=ground) or
  not layersMatch(g,snow and tw4.SNOW_TREE_LAYERS or tw4.ELVEN_TREE_LAYERS) then return end
 for k in pairs(g.can_pass) do if k~='pass_tree' then return end end
 return snow and 'snow-tree' or 'tree'
end
-- Shatur's snowy grass (snowy_forest.lua:22-31 and its SNOWY_PATCH1-14; the
-- native nice_editer is an undefined name there, so no border layers) and
-- the three snow-glade shop cells: mountain.lua ROCKY_GROUND with Shatur's
-- snowy_grass image rewrite (town-shatur/grids.lua:25-29), exactly the
-- Norgos snow ground contract. Both are the snow family's ground.
function tw4.shaturSnow(g,zoneName)
 local id=g.define_as
 if zoneName~='town-shatur' or not ownTown(g,zoneName) then return end
 if id=='ROCKY_GROUND' then
  if g.on_stand or rockTerrain(g,false)~='snow-ground' then return end
  return 'snow-ground'
 end
 local patch=type(id)=='string' and tonumber(id:match('^SNOWY_PATCH(%d+)$'))
 if not (id=='SNOWY_GRASS' or patch and patch>=1 and patch<=14) or g.type~='floor' or g.subtype~='snowy_grass' or
  g.name~='snowy grass' or g.display~='.' or g.grow~='SNOWY_TREE' or
  g.image~=('terrain/grass/snowy_grass_main_%02d.png'):format(patch or 1) or g.always_remember or
  g.does_block_move or g.block_sight or g.dig or g.can_pass or g.road or g.pass_projectile or g.notice or
  hasMos(g) or g.add_displays or not plainCell(g) then return end
 return 'snow-ground'
end
-- Shatur's COBBLESTONE (town-shatur/grids.lua:31-35, a basic.lua FLOOR copy):
-- the lake bridge. Board road, like the other towns' stone roads; only its
-- native marble-to-water edge layers.
tw4.COBBLE_LAYERS={'^invis%.png$','^terrain/marble_water/marble_floor_2_to_water_outer_[1-9]%.png$'}
function tw4.shaturCobble(g,zoneName)
 if zoneName~='town-shatur' or g.define_as~='COBBLESTONE' or not ownTown(g,zoneName) or
  g.type~='floor' or g.subtype~='floor' or g.name~='cobblestone road' or g.display~='.' or
  g.image~='terrain/stone_road1.png' or g.grow~='WALL' or g.always_remember or g.does_block_move or
  g.block_sight or g.dig or g.can_pass or g.road or g.pass_projectile or g.notice or hasMos(g) or
  not plainCell(g) or not layersMatch(g,tw4.COBBLE_LAYERS) then return end
 return 'road'
end
-- TW4 Point Zero: GRASS_SHORT (forest.lua:33-41; world-map grass borders),
-- COLD_FOREST and its 30 variants (town-point-zero/grids.lua:41-60: pass_tree,
-- no dig, dark snowy firs over frozen ground) and the outer-space platform
-- from void.lua (voidTerrain's own contracts, admitted for this town only).
tw4.SHORT_GRASS_LAYERS={'^invis%.png$','^terrain/grass_worldmap/grass_[%w_]+%.png$'}
function tw4.shortGrass(g,zoneName)
 if zoneName~='town-point-zero' or g.define_as~='GRASS_SHORT' or not ownTown(g,zoneName) or
  not stamped(g,'_checker_forest_source',forestSource) or g.type~='floor' or g.subtype~='grass' or
  g.name~='grass' or g.display~='.' or g.grow~='TREE' or g.image~='terrain/grass.png' or g.always_remember or
  g.does_block_move or g.block_sight or g.dig or g.can_pass or g.road or g.pass_projectile or g.notice or
  hasMos(g) or not plainCell(g) or not layersMatch(g,tw4.SHORT_GRASS_LAYERS) then return end
 return 'grass'
end
tw4.COLD_FOREST_LAYERS={'^invis%.png$','^terrain/ice/frozen_ground_[%w_]+%.png$','^terrain/tree_dark_snow%d+%.png$'}
function tw4.coldForest(g,zoneName)
 local id=g.define_as
 local n=type(id)=='string' and tonumber(id:match('^COLD_FOREST(%d+)$'))
 if zoneName~='town-point-zero' or not (id=='COLD_FOREST' or n and n>=1 and n<=30) or not ownTown(g,zoneName) or
  g.type~='wall' or g.subtype~='ice' or g.name~='cold forest' or g.display~='#' or g.always_remember~=true or
  g.does_block_move~=true or g.block_sight~=true or g.dig or g.grow or not g.can_pass or g.can_pass.pass_tree~=1 or
  g.road or g.pass_projectile or g.notice or hasMos(g) or not plainCell(g) or
  g.image~=(n and 'terrain/frozen_ground.png' or 'terrain/tree_dark_snow1.png') or
  not layersMatch(g,tw4.COLD_FOREST_LAYERS) then return end
 for k in pairs(g.can_pass) do if k~='pass_tree' then return end end
 return 'cold-tree'
end
function tw4.pointZeroVoid(g,zoneName)
 if zoneName~='town-point-zero' or not ownTown(g,zoneName) then return end
 local k=voidTerrain(g,zoneName)
 return k=='space' and 'void-space' or k=='rocks' and 'void-rocks' or k=='rift' and 'void-rift' or
  k=='floor' and 'void-floor' or nil
end
-- TW5 Gates of Morning's Sunwall mountain (town-gates-of-morning/grids.lua:
-- 67-82): GOLDEN_MOUNTAIN and its nice_tiler GOLDEN_MOUNTAIN_WALL1-6. Like
-- HARDMOUNTAIN_WALL it is undiggable, has no pass_wall and blocks sense/ESP;
-- only its own gold_mountain border layers (NicerTiles.lua:1069, the same
-- carrier/copy_base/overhang structure as the mountain borders) are allowed.
-- New golden-mountain wall masks. (Helpers kept in the tw4 table: the chunk's
-- local budget is shared.)
function tw4.goldWallParts(g)
 if not g.add_displays then return true end
 local ds=g.add_displays
 if #ds<2 or ds[1].image~='invis.png' or ds[2].image~=g.image or ds[2].z~=3 then return false end
 for i=1,2 do
  for _,mo in ipairs(ds[i].add_mos or {}) do
   if type(mo.image)~='string' or not mo.image:match('^terrain/golden_mountain[1-9]i?%.png$') then return false end
  end
 end
 for i=3,#ds do
  local d=ds[i]
  if type(d.image)~='string' or not d.image:match('^terrain/golden_mountain[789]%.png$') or
   (d.z~=16 and d.z~=17 and d.z~=18) or d.add_mos or d.add_displays then return false end
 end
 return true
end
function tw4.goldMountain(g,zoneName)
 local id=g.define_as
 local n=type(id)=='string' and tonumber(id:match('^GOLDEN_MOUNTAIN_WALL([1-6])$'))
 if zoneName~='town-gates-of-morning' or not (id=='GOLDEN_MOUNTAIN' or n) or not ownTown(g,zoneName) or
  g.image~=('terrain/golden_mountain5_%d.png'):format(n or 1) or
  g.type~='rockwall' or g.subtype~='grass' or g.name~='Sunwall mountain' or g.display~='#' or
  g.always_remember~=true or g.does_block_move~=true or g.block_sight~=true or g.block_sense~=true or
  g.block_esp~=true or g.air_level~=-20 or g.dig or g.grow or g.can_pass or g.pass_projectile or
  g.notice or g.is_door or g.road or hasMos(g) or g.on_stand or g.on_dig or rawget(g,'block_move') or
  rawget(g,'on_move') or g.on_added or g.special or g.shader or g.tint or g.textures or
  not noTransition(g) or not tw4.goldWallParts(g) then return end
 return 'gold-mountain'
end
-- Every native prop a town cell redraws over its board tile (applyForest).
function M.townProp(g,zoneName)
 if g and tw4.S5_FOREST[zoneName] then
  -- S5: the valley's moonstones and portals, also inside an exact aura ring.
  -- S6: Gorbat's loose rock door.
  local function prop(x)
   local k,d=tw4.valleyProp(x,zoneName)
   if not d then k,d=tw4.rockDoor(x,zoneName) end
   return k,d
  end
  local kind,d=prop(g)
  if not d and g.on_stand~=nil then
   local v=M.ringView(g)
   if v then kind,d=prop(v) end
  end
  if d then return kind,d end
  return
 end
 if not g or not townFiles[zoneName] then return end
 if g.define_as==nil then return townStatue(g,zoneName) end
 local kind,d=angolwenFountain(g,zoneName)
 if d then return kind,d end
 -- TW6: Irkkk's cooking pit keeps its native add_mos over the board hut floor.
 kind,d=tw4.bambooHut(g,zoneName)
 if kind=='hut-cooking' then return kind,d end
 return townGrassProp(g,zoneName)
end
local function townKind(g,zoneName)
 if not townStamped(g,zoneName) then return end
 return meadowGrass(g) or meadowFlower(g) or forestTree(g,false) or stoneRoad(g) or deepWater(g) or meadowExit(g) or
  plazaRoad(g) or hardMountain(g) or
  -- TW3: Zigur's sand shore (sand.lua SAND, South Beach art), lava pit and
  -- post sign; Angolwen's fountain and rocks; Iron Council's crystal walls;
  -- the world exit with native grass-border carriers.
  ((zoneName=='town-zigur' or zoneName=='town-gates-of-morning') and surfaceSandKind(g) and 'sand') or zigurLava(g,zoneName) or councilCrystal(g,zoneName) or
  angolwenFountain(g,zoneName) or (townGrassProp(g,zoneName)) or
  ((zoneName=='town-zigur' or zoneName=='town-angolwen') and townGrassExit(g)) or
  -- TW4: Shatur's green/snow elven forest, snow ground and bridge; Point
  -- Zero's short grass, cold forest and outer-space platform.
  tw4.shaturTree(g,zoneName) or tw4.shaturSnow(g,zoneName) or tw4.shaturCobble(g,zoneName) or
  tw4.shortGrass(g,zoneName) or tw4.coldForest(g,zoneName) or tw4.pointZeroVoid(g,zoneName) or
  -- TW5: Gates of Morning's beach sand (South Beach art, as Zigur) and its
  -- Sunwall mountain; its roads, grass, trees and water use the contracts above.
  tw4.goldMountain(g,zoneName) or
  -- TW6: Irkkk's jungle (Caldera art) and its bamboo huts; its deep water
  -- uses the contract above. (Defined below jungleKind.)
  tw4.irkkkJungle(g,zoneName) or tw4.bambooHut(g,zoneName) or nil
end
local function stewProp(g)
 if g.define_as~='STEW' or not stamped(g,'_checker_keepsake_source',keepsakeSource) or
  g.type~='wall' or g.subtype~='grass' or g.name~='troll stew' or g.display~='~' or
  g.image~='terrain/grass.png' or g.does_block_move~=true or g.pass_projectile~=true or
  g.block_sight or g.dig or g.can_pass or g.add_displays or not hasMos(g) or #g.add_mos~=1 or
  g.add_mos[1].image~='terrain/troll_stew.png' or not plainCell(g) then return end
 return 'stew'
end
-- Keepsake story triggers look exactly like grass or cave floor in the native
-- game; drawing them natively would single them out. They are accepted only
-- with their original on_move, and nothing else.
local keepsakeEvents={GRASS_MEADOW='grass',GRASS_DREAM='grass',GRASS_INCHATE='grass',GRASS_CARAVAN='grass',
 CAVEFLOOR_CAVE_ENTRANCE='cave-floor',CAVEFLOOR_CAVE_DESCRIPTION='cave-floor',
 CAVEFLOOR_VAULT_ENTRANCE='cave-floor',CAVEFLOOR_VAULT_TRIGGER='cave-floor',CAVEFLOOR_DOG_VAULT='cave-floor'}
local function keepsakeEvent(g)
 local kind=keepsakeEvents[g.define_as]
 local s=g._checker_keepsake_source
 if not kind or not stamped(g,'_checker_keepsake_source',keepsakeSource) or
  not sameCallback(rawget(g,'on_move'),s.move_source,s.move_line) or
  g.on_stand or g.on_dig or rawget(g,'block_move') or g.on_added or g.special or g.shader or
  g.tint or g.textures or g.air_level or g.is_door or g.block_sense or g.block_esp or
  g.does_block_move or g.block_sight or g.dig or g.can_pass or hasMos(g) or g.grow or
  not noTransition(g) then return end
 if kind=='grass' and g.type=='floor' and g.subtype=='grass' and g.name=='grass' and g.display=='.' and
  g.image=='terrain/grass.png' and layersMatch(g,GRASS_LAYERS) then return 'grass' end
 if kind=='cave-floor' and g.type=='floor' and g.subtype=='dirt' and g.name=='cave floor' and
  g.display=='.' and g.image=='terrain/cave/cave_floor_1_01.png' and g.notice==true and
  g.always_remember==true and not g.add_displays then return 'cave-floor' end
end
M.keepsakeEvent=keepsakeEvent
local JUNGLE_FLOOR_LAYERS={'^invis%.png$','^terrain/jungle/jungle_grass_[%w_]+%.png$',
 '^terrain/jungle/jungle_brush_[%w_]+%.png$','^terrain/jungle/jungle_dirt_var_[%w_]+%.png$',
 '^terrain/jungle/jungle_plant_0[1-4]%.png$'}
local JUNGLE_TREE_LAYERS={'^invis%.png$','^terrain/jungle/jungle_grass_[%w_]+%.png$','^terrain/jungle/jungle_tree_%d+%.png$'}
local jungleExits={
 JUNGLE_GRASS_UP_WILDERNESS={'exit-world','exit to the worldmap',1,'wilderness','terrain/worldmap.png','<'},
 JUNGLE_GRASS_UP4={'exit-up','way to the previous level',-1,nil,'terrain/way_next_4.png','<'},
 JUNGLE_GRASS_DOWN6={'exit-down','way to the next level',1,nil,'terrain/way_next_6.png','>'},
}
local function jungleKind(g)
 local id=g.define_as
 if not stamped(g,'_checker_jungle_source',jungleSource) then return end
 local aura=M.auraKind(g)
 if (g.on_stand and not aura) or g.on_dig or rawget(g,'block_move') or rawget(g,'on_move') or g.on_added or
  g.special or g.shader or g.tint or g.textures or g.air_level or g.is_door or g.block_sense or g.block_esp or
  hasMos(g) and not jungleExits[id] then return end
 if numbered(id,'JUNGLE_GRASS_PATCH',24) or id=='JUNGLE_GRASS' then
  if g.type~='floor' or g.subtype~='grass' or g.display~='.' or (not aura and g.name~='grass') or
   g.image~='terrain/jungle/jungle_grass_floor_01.png' or g.grow~='JUNGLE_TREE' or
   g.does_block_move or g.block_sight or g.dig or g.can_pass or not noTransition(g) or
   not layersMatch(g,JUNGLE_FLOOR_LAYERS) then return end
  return 'floor'
 end
 if numbered(id,'JUNGLE_TREE',30) then
  if g.type~='wall' or g.subtype~='grass' or g.name~='tree' or g.display~='#' or g.always_remember~=true or
   g.does_block_move~=true or g.block_sight~=true or g.dig~='JUNGLE_GRASS' or not g.can_pass or
   g.can_pass.pass_tree~=1 or not noTransition(g) or
   (g.image~='terrain/jungle/jungle_grass_floor_01.png' and g.image~='terrain/tree.png') or
   not layersMatch(g,JUNGLE_TREE_LAYERS) then return end
  for k in pairs(g.can_pass) do if k~='pass_tree' then return end end
  return 'tree'
 end
 local e=jungleExits[id]
 if e and not aura and g.type=='floor' and g.subtype=='grass' and g.name==e[2] and g.display==e[6] and
  g.change_level==e[3] and g.change_zone==e[4] and g.image=='terrain/jungle/jungle_grass_floor_01.png' and
  g.notice==true and g.always_remember==true and g.add_mos and #g.add_mos==1 and g.add_mos[1].image==e[5] and
  not g.add_displays and not g.does_block_move and not g.block_sight and not g.dig and not g.can_pass then
  for i=3,#transitionKeys do if g[transitionKeys[i]]~=nil then return end end
  return e[1]
 end
end
-- TW6 Irkkk: jungle.lua grass, trees and the world exit (jungleKind's full
-- contract and general-file stamp) under Irkkk's own list stamp; drawn with
-- the Noxious Caldera jungle art.
tw4.JUNGLE_KINDS={floor='jungle-grass',tree='jungle-tree',['exit-world']='jungle-exit'}
function tw4.irkkkJungle(g,zoneName)
 if zoneName~='town-irkkk' or not ownTown(g,zoneName) then return end
 return tw4.JUNGLE_KINDS[jungleKind(g) or '']
end
-- TW6 Irkkk bamboo huts (general/grids/jungle_hut.lua, loaded only through
-- Irkkk's list, so its list stamp is the provenance). Every variant must carry
-- exactly the native layers its definition line adds: {image, z, display_y,
-- nested add_mos {image, display_y}}.
function tw4.bamboo(name) return 'terrain/bamboo/'..name..'_01.png' end
tw4.BAMBOO_WALLS={
 BAMBOO_HUT_WALL={},
 BHW_V_FULL1={{'hut_wall_full_hor',16}},
 BHW_H_FULL={{'hut_wall_bottom_hor',16},{'hut_wall_top_hor',17,-1}},
 BHW_N_CROSS1={{'hut_wall_bottom_hor',16},{'hut_corner_vert_south_4_1_2_top',17,-1,{{'hut_wall_top_hor',-1}}}},
 BHW_S_CROSS1={{'hut_wall_bottom_hor',16},{'hut_wall_full_hor',17,nil,{{'hut_wall_top_hor',-1},{'hut_corner_vert_4_7_8_top',-1}}}},
 BHW_E_CROSS1={{'hut_wall_full_hor',17},{'wall_hor_divider_left_bottom',16,nil,{{'wall_hor_divider_left_top',-1}}}},
 BHW_W_CROSS1={{'hut_wall_full_hor',17},{'wall_hor_divider_right_bottom',16,nil,{{'wall_hor_divider_right_top',-1}}}},
 BHW_CROSS1={{'hut_wall_bottom_hor',17},{'hut_wall_top_hor',16,-1,{{'hut_wall_full_hor'},{'hut_corner_vert_4_7_8_top',-1}}}},
 BHW_NE1={{'hut_corner_4_1_2_bottom',17},{'hut_corner_4_1_2_top',16,-1}},
 BHW_NW1={{'hut_corner_6_3_2_bottom',17},{'hut_corner_6_3_2_top',16,-1}},
 BHW_SE1={{'hut_corner_4_7_8_bottom',17},{'hut_corner_4_7_8_top',16,-1}},
 BHW_SW1={{'hut_corner_8_9_6_bottom',17},{'hut_corner_8_9_6_top',16,-1}}}
for i,decor in ipairs{'wall_decor_skin_b','wall_decor_skin_a','wall_decor_spears','wall_decor_sticks',
 'wall_decor_mask_c','wall_decor_mask_b','wall_decor_mask_a','wall_decor_3_masks'} do
 tw4.BAMBOO_WALLS['BHW_H_FULL'..i]={{'hut_wall_bottom_hor',16,nil,{{decor}}},{'hut_wall_top_hor',17,-1}}
end
-- Doors: kind, name, display, door_opened, door_closed, dig, layers.
tw4.BAMBOO_DOORS={
 BAMBOO_HUT_DOOR_HORIZ={'hut-door-h','door','+','BAMBOO_HUT_DOOR_HORIZ_OPEN',nil,'FLOOR',
  {{'hut_wall_door_closed_hor',17},{'hut_wall_top_hor',18,-1}}},
 BAMBOO_HUT_DOOR_VERT={'hut-door-v','door','+','BAMBOO_HUT_DOOR_OPEN_VERT',nil,'BAMBOO_HUT_DOOR_OPEN_VERT',
  {{'palm_door_closed_ver'},{'hut_wall_full_hor',18}}},
 BAMBOO_HUT_DOOR_HORIZ_OPEN={'hut-door-h-open','open door',"'",nil,'BAMBOO_HUT_DOOR_HORIZ',nil,
  {{'hut_door_hor_open_door_palm_leaves'},{'hut_door_hor_open_door',17},{'hut_wall_top_hor',18,-1}}},
 BAMBOO_HUT_DOOR_OPEN_VERT={'hut-door-v-open','open door',"'",nil,'BAMBOO_HUT_DOOR_VERT',nil,
  {{'palm_door_open_bottom_ver'},{'palm_door_open_top_ver',18,-1,{{'hut_wall_full_hor'},{'palm_door_open_bottom_ver_door'}}}}}}
function tw4.bambooLayers(g,spec)
 local ds=g.add_displays or {}
 if #ds~=#spec then return false end
 for i,s in ipairs(spec) do
  local d=ds[i]
  if d.image~=tw4.bamboo(s[1]) or d.z~=s[2] or d.display_y~=s[3] or d.display_x or d.display_w or d.display_h or
   d.shader or d.add_displays or #(d.add_mos or {})~=#(s[4] or {}) then return false end
  for j,mo in ipairs(d.add_mos or {}) do
   for k in pairs(mo) do if k~='image' and k~='display_y' then return false end end
   if mo.image~=tw4.bamboo(s[4][j][1]) or mo.display_y~=s[4][j][2] then return false end
  end
 end
 return true
end
function tw4.bambooHut(g,zoneName)
 local id=g.define_as
 if zoneName~='town-irkkk' or not ownTown(g,zoneName) or g.image~='terrain/bamboo/hut_dirt_floor_01.png' or
  g.on_stand or g.on_dig or rawget(g,'block_move') or rawget(g,'on_move') or g.on_added or g.special or
  g.shader or g.tint or g.textures or g.block_sense or g.block_esp or g.pass_projectile or g.road or g.z or
  not noTransition(g) then return end
 local wall,door=tw4.BAMBOO_WALLS[id],tw4.BAMBOO_DOORS[id]
 if wall then
  if g.type~='wall' or g.subtype~='bamboo hut' or g.name~='bamboo wall' or g.display~='#' or
   g.always_remember~=true or g.does_block_move~=true or g.block_sight~=true or g.air_level~=-5 or
   g.dig~='BAMBOO_HUT_FLOOR' or not g.can_pass or g.can_pass.pass_wall~=1 or g.grow or g.notice or
   g.is_door or g.door_opened or g.door_closed or hasMos(g) or not tw4.bambooLayers(g,wall) then return end
  for k in pairs(g.can_pass) do if k~='pass_wall' then return end end
  return 'hut-wall'
 end
 if door then
  -- Closed doors block sight and are noticed; open doors do neither.
  local closed=door[4]~=nil
  if g.type~='wall' or g.subtype~='bamboo hut' or g.name~=door[2] or g.display~=door[3] or
   g.always_remember~=true or g.is_door~=true or g.door_opened~=door[4] or g.door_closed~=door[5] or
   g.dig~=door[6] or g.block_sight~=(closed or nil) or g.notice~=(closed or nil) or
   g.does_block_move or g.can_pass or g.air_level or g.grow or hasMos(g) or
   not tw4.bambooLayers(g,door[7]) then return end
  return door[1]
 end
 if (id~='BAMBOO_HUT_FLOOR' and id~='BAMBOO_HUT_COOKING3') or g.type~='floor' or g.subtype~='bamboo floor' or
  g.grow~='BAMBOO_HUT_WALL' or g.always_remember or g.does_block_move or g.block_sight or g.dig or g.can_pass or
  g.air_level or g.is_door or g.notice or g.add_displays then return end
 if id=='BAMBOO_HUT_FLOOR' and g.name=='bamboo hut floor' and g.display=='.' and not hasMos(g) then return 'hut-floor' end
 local mo=id=='BAMBOO_HUT_COOKING3' and g.add_mos and #g.add_mos==1 and g.add_mos[1]
 if not mo or g.name~='cooking pit' or g.display~='*' or mo.image~='terrain/bamboo/floor_deco_cooking_pit_c_01.png' then return end
 for k in pairs(mo) do if k~='image' then return end end
 return 'hut-cooking',mo
end
-- Poisoned water is a walkable hazard. Its native on_stand damage and
-- combatAttack stay attached and unchanged; only the display is replaced.
local function poisonWater(g)
 local id=g.define_as
 local n=type(id)=='string' and tonumber(id:match('^POISON_DEEP_WATER([1-6])$'))
 local s=g._checker_water_source
 if not (id=='POISON_DEEP_WATER' or n) or not stamped(g,'_checker_water_source',waterSource) or
  s.image~=g.image or g.image~=('terrain/poisoned_water_0%d.png'):format(n or 1) or
  not sameCallback(g.on_stand,s.stand_source,s.stand_line) or
  not sameCallback(g.combatAttack,s.attack_source,s.attack_line) or
  g.type~='floor' or g.subtype~='water' or g.name~='poisoned deep water' or g.display~='~' or
  g.always_remember~=true or g.air_level~=-5 or g.air_condition~='water' or g.shader~='water' or
  g.does_block_move or g.block_sight or g.dig or g.can_pass or hasMos(g) or g.add_displays or
  g.on_dig or rawget(g,'block_move') or rawget(g,'on_move') or g.on_added or g.special or g.tint or
  g.is_door or not noTransition(g) then return end
 return 'poison'
end
-- S5: six reachable zones on existing families, no new art. Each forest-side
-- zone is its own batch4 family key (its short name); every kind is an
-- existing exact contract, plus a few zone-local identities that also need
-- the zone's own list stamp (superload/mod/class/Grid.lua), so a level
-- generated before that stamp keeps them native. Stone cells use the basic.lua
-- stamps and classify(); levers, lever doors, portals with callbacks, the
-- Ring of Blood's control orb and map-file quickEntity grids stay native.
tw4.S5_FILES={['tannen-tower']='/data/zones/tannen-tower/grids.lua',
 ['valley-moon']='/data/zones/valley-moon/grids.lua',['ring-of-blood']='/data/zones/ring-of-blood/grids.lua',
 -- S6: Eruan and Gorbat Pride. Every S6 identity requires this list stamp.
 eruan='/data/zones/eruan/grids.lua',['gorbat-pride']='/data/zones/gorbat-pride/grids.lua',
 -- S9: High Peak. Every S9 identity (cave, stone, its two stairs) requires
 -- this list stamp; it is not a batch4/S5 forest family (tw4.hpCave).
 ['high-peak']='/data/zones/high-peak/grids.lua'}
tw4.S5_FOREST={['dreadfell-ambush']=true,['tannen-tower']=true,['valley-moon']=true,['ring-of-blood']=true,['arena-unlock']=true,
 eruan=true,['gorbat-pride']=true}
-- Stone zones whose all_remembered levels get the remembered-cell install.
tw4.S5_REMEMBER={['shadow-crypt']=true,['tannen-tower']=true,['ring-of-blood']=true,['arena-unlock']=true}
function tw4.zoneStamped(g,zoneName)
 local file=tw4.S5_FILES[zoneName]
 return file and stamped(g,'_checker_zone_source',file) and true or false
end
-- Valley of the Moon (valley-moon/grids.lua:22-42): the moonstone circle
-- (MOONSTONE1-8, one display_h=2 stone layer, blocks move and sight) and the
-- Fearscape invocation portals (PORTAL_DEMON, one z=5 portal layer, no
-- callback or transition; demons spawn from separate map spots). Both keep
-- their native layer over board grass.
function tw4.valleyProp(g,zoneName)
 local id=g.define_as
 if zoneName~='valley-moon' or not tw4.zoneStamped(g,zoneName) or g.image~='terrain/grass.png' or hasMos(g) or
  g.on_stand or g.on_dig or rawget(g,'block_move') or rawget(g,'on_move') or g.on_added or g.special or
  g.shader or g.tint or g.textures or g.dig or g.grow or g.can_pass or g.pass_projectile or g.block_sense or
  g.block_esp or g.air_level or g.is_door or g.road or g.z or not noTransition(g) then return end
 local d=g.add_displays and #g.add_displays==1 and g.add_displays[1]
 if not d or d.add_mos or d.add_displays or d.shader or d.display_x or d.display_w then return end
 local n=type(id)=='string' and tonumber(id:match('^MOONSTONE([1-8])$'))
 if n then
  if g.name~='moonstone' or g.display~='&' or g.type or g.subtype or g.always_remember~=true or
   g.does_block_move~=true or g.block_sight~=true or g.notice or g.show_tooltip or
   d.image~=('terrain/moonstone_0%d.png'):format(n) or d.z or d.display_h~=2 or d.display_y~=-1 then return end
  return 'moonstone',d
 end
 if id=='PORTAL_DEMON' and g.type=='floor' and g.subtype=='grass' and g.name=='Fearscape Portal' and g.display=='&' and
  g.notice==true and g.always_remember==true and g.show_tooltip==true and not g.does_block_move and
  not g.block_sight and d.image=='terrain/demon_portal3.png' and d.z==5 and not d.display_y and not d.display_h then
  return 'portal',d
 end
end
-- Ring of Blood's lava pits (ring-of-blood/grids.lua:22-37): untyped cells
-- that only block movement; the OPAQUE copy also blocks sight, sense and ESP.
-- Natively both draw the same lava image; both get the burnt lava masks.
function tw4.bloodLava(g,zoneName)
 local id=g.define_as
 if zoneName~='ring-of-blood' or (id~='LAVA_WALL' and id~='LAVA_WALL_OPAQUE') or not tw4.zoneStamped(g,zoneName) then return end
 local opaque=id=='LAVA_WALL_OPAQUE' or nil
 if g.name~='lava pit' or g.display~='~' or g.image~='terrain/lava_floor.png' or g.type or g.subtype or
  g.always_remember~=true or g.does_block_move~=true or g.block_sight~=opaque or g.block_sense~=opaque or
  g.block_esp~=opaque or g.add_displays or g.z or g.dig or g.grow or g.can_pass or g.pass_projectile or
  g.air_level or g.is_door or g.notice or g.road or hasMos(g) or g.on_stand or g.on_dig or
  rawget(g,'block_move') or rawget(g,'on_move') or g.on_added or g.special or g.shader or g.tint or
  g.textures or not noTransition(g) then return end
 return 'lava'
end
-- S6: Eruan (sand.lua desert forest with deep-ocean ponds; L3 static map)
-- and Gorbat Pride (MapScript: sand, hard mountains, basic.lua stone, bamboo
-- drake roosts). Every S6 identity needs the zone's own list stamp (old
-- levels keep native) and, where it has one, the defining file's stamp.
-- Sand, deep water and hard mountain reuse their existing exact contracts.
-- Levers, the lever rock door, the Charred Scar farportals and event cells
-- stay native.
tw4.SAND_FILE='/data/general/grids/sand.lua'
-- PALMTREE1-20 (sand.lua:115-128): the blocking palm, drawn as a new board
-- palm over board beach sand. Only the native makeTrees parts
-- (mod/class/Grid.lua:327-358) of palmtree_alpha1-8 are allowed as layers.
function tw4.palm(g)
 local n=type(g.define_as)=='string' and tonumber(g.define_as:match('^PALMTREE(%d+)$'))
 if not n or n<1 or n>20 or not stamped(g,'_checker_sand_source',tw4.SAND_FILE) or
  g.type~='wall' or g.subtype~='sand' or g.name~='tree' or g.image~='terrain/sandfloor.png' or g.display~='#' or
  g.always_remember~=true or g.does_block_move~=true or g.block_sight~=true or g.dig~='SAND' or
  not g.can_pass or g.can_pass.pass_tree~=1 or g.block_sense or g.block_esp or g.air_level or g.grow or
  g.notice or g.is_door or g.road or g.z or g.pass_projectile or hasMos(g) or g.on_stand or g.on_dig or
  rawget(g,'block_move') or rawget(g,'on_move') or g.on_added or g.special or g.shader or g.tint or
  g.textures or not noTransition(g) then return end
 for k in pairs(g.can_pass) do if k~='pass_tree' then return end end
 local ds=g.add_displays
 if type(ds)~='table' then return end
 -- A palm beside a non-sand cell also gets its own nice_editer carrier
 -- (sand.lua:128, borders_def sand) last: only terrain/sand/sand_* borders.
 local carrier=ds[#ds]
 local parts=#ds
 if carrier and carrier.image=='invis.png' then
  if carrier.z or carrier.display_x or carrier.display_y or carrier.display_w or carrier.display_h or carrier.shader or
   carrier.add_displays or not carrier.add_mos or #carrier.add_mos<1 or
   not layersMatch({add_mos=carrier.add_mos},{'^terrain/sand/sand_[%w_]+%.png$'}) then return end
  parts=parts-1
 end
 if parts<1 or parts>3 then return end
 for i=1,parts do
  local d=ds[i]
  if type(d.image)~='string' or not d.image:match('^terrain/palmtree_alpha[1-8]%.png$') or d.z~=15+i or
   d.shader~='tree' or type(d.shader_args)~='table' or d.shader_args.attenuation~=25 or
   (d.display_h~=1 and d.display_h~=2) or d.display_w or d.tint or d.add_mos or d.add_displays then return end
  for k in pairs(d.shader_args) do if k~='attenuation' then return end end
 end
 return 'palm'
end
-- Eruan's three sand exits (sand.lua:133-206): the world exit on L1, the
-- ways up (L2-L3) and down (L1-L2); one native arrow layer each.
tw4.SAND_EXITS={
 SAND_UP_WILDERNESS={'exit-world','exit to the worldmap',1,'wilderness','terrain/worldmap.png','<'},
 SAND_UP8={'exit-up','way to the previous level',-1,nil,'terrain/way_next_8.png','<'},
 SAND_DOWN2={'exit-down','way to the next level',1,nil,'terrain/way_next_2.png','>'}}
function tw4.sandExit(g)
 local e=tw4.SAND_EXITS[g.define_as]
 local d=e and g.add_displays and #g.add_displays==1 and g.add_displays[1]
 if not d or not stamped(g,'_checker_sand_source',tw4.SAND_FILE) or g.type~='floor' or g.subtype~='sand' or
  g.name~=e[2] or g.display~=e[6] or g.image~='terrain/sandfloor.png' or g.change_level~=e[3] or g.change_zone~=e[4] or
  g.notice~=true or g.always_remember~=true or d.image~=e[5] or d.z or d.display_x or d.display_y or d.display_w or
  d.display_h or d.shader or d.add_mos or d.add_displays or hasMos(g) or g.does_block_move or g.block_sight or
  g.block_sense or g.block_esp or g.dig or g.grow or g.can_pass or g.air_level or g.is_door or g.z or g.road or
  g.on_stand or g.on_dig or rawget(g,'block_move') or rawget(g,'on_move') or g.on_added or g.special or g.shader or
  g.tint or g.textures then return end
 for i=3,#transitionKeys do if g[transitionKeys[i]]~=nil then return end end
 return e[1]
end
-- Gorbat's loose rock door (gorbat-pride/grids.lua:144-154): no lever and no
-- callback; bumping it opens it into FLOOR natively. Board sand plus the
-- native rock layer. (ROCK_LEVER_DOOR has on_lever_change: native.)
function tw4.rockDoor(g,zoneName)
 local d=g.add_displays and #g.add_displays==1 and g.add_displays[1]
 if zoneName~='gorbat-pride' or g.define_as~='ROCK_DOOR' or not d or not tw4.zoneStamped(g,zoneName) or
  g.type~='wall' or g.subtype~='sand' or g.name~='huge loose rock' or g.image~='terrain/sandfloor.png' or
  g.display~='+' or g.notice~=true or g.always_remember~=true or g.block_sight~=true or g.is_door~=true or
  g.door_opened~='FLOOR' or g.door_closed or g.does_block_move or g.block_sense or g.block_esp or g.dig or
  g.grow or g.can_pass or g.air_level or g.z or g.road or g.pass_projectile or g.door_player_stop or
  g.door_player_check~=nil or g.lever or g.lever_action or hasMos(g) or
  d.image~='terrain/huge_rock.png' or d.z~=18 or d.display_x or d.display_y or d.display_w or d.display_h or
  d.shader or d.add_mos or d.add_displays or not noTransition(g) then return end
 for _,v in pairs(g) do if type(v)=='function' then return end end
 return 'rock-door',d
end
-- Gorbat's bamboo drake roosts (gorbat-pride/grids.lua:32-118): its own
-- FENCE_* definitions (subtype roost, own names, dig/grow, roost entrance)
-- whose singleWall/door3d variants add exactly the layers of Irkkk's
-- jungle_hut.lua variants (tw4.BAMBOO_WALLS / BAMBOO_DOORS), plus BHW_SOLO1.
-- Drawn with the TW6 bamboo art.
tw4.FENCE_SOLO={{'south_right_vert_end_bottom',16},{'south_right_vert_end_top',17,-1}}
tw4.FENCE_DOORS={
 FENCE_DOOR_HORIZ={'hut-door-h','door','+','FENCE_DOOR_HORIZ_OPEN',nil,'FLOOR','BAMBOO_HUT_DOOR_HORIZ'},
 FENCE_DOOR_VERT={'hut-door-v','door','+','FENCE_DOOR_OPEN_VERT',nil,'FENCE_DOOR_OPEN_VERT','BAMBOO_HUT_DOOR_VERT'},
 FENCE_DOOR_HORIZ_OPEN={'hut-door-h-open','open door',"'",nil,'FENCE_DOOR_HORIZ',nil,'BAMBOO_HUT_DOOR_HORIZ_OPEN'},
 FENCE_DOOR_OPEN_VERT={'hut-door-v-open','open door',"'",nil,'FENCE_DOOR_VERT',nil,'BAMBOO_HUT_DOOR_OPEN_VERT'}}
function tw4.fenceHut(g,zoneName)
 local id=g.define_as
 if zoneName~='gorbat-pride' or type(id)~='string' or not tw4.zoneStamped(g,zoneName) or
  g.image~='terrain/bamboo/hut_dirt_floor_01.png' or hasMos(g) or
  g.on_stand or g.on_dig or rawget(g,'block_move') or rawget(g,'on_move') or g.on_added or g.special or
  g.shader or g.tint or g.textures or g.block_sense or g.block_esp or g.pass_projectile or g.road or g.z or
  not noTransition(g) then return end
 local wall=id=='FENCE_WALL' and {} or id=='BHW_SOLO1' and tw4.FENCE_SOLO or id:match('^BHW_') and tw4.BAMBOO_WALLS[id]
 local door=tw4.FENCE_DOORS[id]
 if wall then
  if g.type~='wall' or g.subtype~='roost' or g.name~='wall' or g.display~='#' or
   g.always_remember~=true or g.does_block_move~=true or g.block_sight~=true or g.air_level~=-5 or
   g.dig~='FENCE_FLOOR' or not g.can_pass or g.can_pass.pass_wall~=1 or g.grow or g.notice or
   g.is_door or g.door_opened or g.door_closed or g.is_roost_entrance or not tw4.bambooLayers(g,wall) then return end
  for k in pairs(g.can_pass) do if k~='pass_wall' then return end end
  return 'hut-wall'
 end
 if door then
  -- Closed doors block sight, are noticed and mark the roost entrance.
  local closed=door[4]~=nil or nil
  if g.type~='wall' or g.subtype~='roost' or g.name~=door[2] or g.display~=door[3] or
   g.always_remember~=true or g.is_door~=true or g.door_opened~=door[4] or g.door_closed~=door[5] or
   g.dig~=door[6] or g.block_sight~=closed or g.notice~=closed or g.is_roost_entrance~=closed or
   g.does_block_move or g.can_pass or g.air_level or g.grow or
   not tw4.bambooLayers(g,tw4.BAMBOO_DOORS[door[7]][7]) then return end
  return door[1]
 end
 if id=='FENCE_FLOOR' and g.type=='floor' and g.subtype=='floor' and g.name=='floor' and g.display=='.' and
  g.grow=='FENCE_WALL' and not (g.always_remember or g.does_block_move or g.block_sight or g.dig or g.can_pass or
  g.air_level or g.is_door or g.notice or g.is_roost_entrance or g.add_displays) then return 'hut-floor' end
end
function tw4.s6Kind(g,zoneName)
 if not tw4.zoneStamped(g,zoneName) then return end
 if surfaceSandKind(g) then return 'sand' end
 if zoneName=='eruan' then
  -- hardMountain: the dragon-lair greater vault's walls.
  return tw4.palm(g) or deepWater(g) or tw4.sandExit(g) or hardMountain(g) or nil
 end
 -- Gorbat: hard and diggable mountains share the Daikara mountain masks.
 return hardMountain(g) or (rockTerrain(g,true)=='mountain-wall' and 'mountain') or deepWater(g) or
  tw4.fenceHut(g,zoneName) or (tw4.rockDoor(g,zoneName)) or nil
end
-- S9: High Peak L1-4 (Cavern: cave.lua CAVEFLOOR/CAVEWALL) on the existing
-- cave contract, plus the zone's own cave stair (CAVE_HIGH_PEAK_UP,
-- high-peak/grids.lua:274-281, the S2 spec below: native up-ladder image
-- for the climb to the next level). Every cell needs the zone list stamp,
-- so levels generated before it keep native. HARDCAVEWALL, CAVE_ROCK_VAULT
-- and CAVE_DOOR stay native (only reachable in the sub-vault event, which is
-- its own zone).
function tw4.hpCave(g)
 if not g or not tw4.zoneStamped(g,'high-peak') then return end
 local t=caveTerrain(g)
 if t then return t end
 if tw4.s2Forest(g,'high-peak')=='ladder-up' then return 'ladder-up' end
end
M.hpCave=tw4.hpCave
function tw4.s5Kind(g,zoneName)
 if zoneName=='dreadfell-ambush' then
  -- Static GRASS/TREE glade; the world exit is placed by the quest script.
  return meadowGrass(g) or meadowFlower(g) or forestTree(g,false) or meadowExit(g)
 elseif zoneName=='valley-moon' then
  return meadowGrass(g) or meadowFlower(g) or forestTree(g,false) or poisonWater(g) or deepWater(g) or
   (rockTerrain(g,true)=='mountain-wall' and 'wall') or (tw4.valleyProp(g,zoneName)) or nil
 elseif zoneName=='tannen-tower' then
  return meadowGrass(g) or forestTree(g,false) or deepWater(g)
 elseif zoneName=='ring-of-blood' then
  return surfaceSandKind(g) and 'sand' or tw4.bloodLava(g,zoneName)
 elseif zoneName=='arena-unlock' then
  return meadowGrass(g) or forestTree(g,false) or surfaceSandKind(g) and 'sand' or nil
 elseif zoneName=='eruan' or zoneName=='gorbat-pride' then
  return tw4.s6Kind(g,zoneName)
 end
end
-- Exact native ring/centre cells (S1) are judged as the grid they cloned.
tw4.s5Kind=ringAware(tw4.s5Kind)
-- Tannen's Tower (stone view for classify()). TUP/TDOWN (tannen-tower/
-- grids.lua:40-47) are basic.lua UP/DOWN copies with change_level reversed
-- for its reversed level numbering: the view restores the base id and
-- direction. On the flooded floor (map tannen-tower-3) NicerTiles gives the
-- floor and stairs beside deep water one invisible carrier holding only the
-- native marble-to-water edges: the view drops exactly that carrier. The
-- untouched basic.lua contract (signature, art, transitions) then decides.
tw4.TANNEN_EDGE={'^terrain/marble_water/marble_floor_2_to_water_outer_[1-9]%.png$'}
-- S2/T21: the same native marble-to-water edge carrier on plain FLOOR in the
-- stone zones where the census found it (NicerTiles marble_floor borders,
-- NicerTiles.lua:738-767); display only the board floor.
tw4.EDGE_ZONES={dreadfell=true,['vor-armoury']=true,['scintillating-caves']=true,reknor=true,['halfling-ruins']=true}
function tw4.tannenView(g)
 local zone=g and game and game.zone and game.zone.short_name
 local tannen=zone=='tannen-tower'
 if not (tannen or tw4.EDGE_ZONES[zone]) then return end
 local id=g.define_as
 local base=tannen and (id=='TUP' and 'UP' or id=='TDOWN' and 'DOWN')
 local s=g._checker_grid_source
 if base and (not s or not tw4.zoneStamped(g,'tannen-tower') or s.file~='/data/general/grids/basic.lua' or s.id~=base or
  g.change_level~=(base=='UP' and 1 or -1)) then return end
 local ds=g.add_displays
 local d=ds and #ds==1 and ds[1]
 local edge=d and d.image=='invis.png' and d.add_mos and #d.add_mos>0 and not (d.add_displays or d.z or d.display_x or
  d.display_y or d.display_w or d.display_h or d.shader) and layersMatch({add_mos=d.add_mos},tw4.TANNEN_EDGE) and
  (id=='FLOOR' or base)
 if not base and not edge then return end
 local v={};for k,value in pairs(g) do v[k]=value end
 if base then v.define_as=base;v.change_level=-g.change_level end
 if edge then v.add_displays=nil end
 return setmetatable(v,getmetatable(g))
end
local function batch4Kind(g,family)
 if not g or (g.replace_display and (not g._checker_terrain or g.replace_display~=g._checker_terrain.display)) then return end
 if g.define_as==nil and townFiles[family] then return (townStatue(g,family)) end
 if type(g.define_as)~='string' then return end
 if family=='beach' then
  return surfaceSandKind(g) and 'sand' or beachProp(g) or meadowGrass(g) or forestTree(g,false) or
   stoneRoad(g) or deepWater(g) or (tw4.s2Forest(g,'beach')) -- S2/T10: BEACH_UP world exit
 elseif family=='meadow' then
  -- S2/T7, T14: Keepsake's cave doors and the cave marker post.
  local cave=caveTerrain(g) or (tw4.s2Forest(g,'meadow'))
  if cave then return 'cave-'..cave end
  return keepsakeEvent(g) or meadowGrass(g) or meadowFlower(g) or forestTree(g,true) or
   deepWater(g) or meadowExit(g) or stewProp(g)
 elseif family=='caldera' then
  local kind=jungleKind(g) or poisonWater(g) or (tw4.s2Forest(g,'caldera')) -- T16: altar of dreams
  if kind then return kind end
  local rock=rockTerrain(g,true)
  return rock=='mountain-wall' and 'wall' or rock=='rock-ground' and 'rock-ground' or nil
 elseif townFiles[family] then
  return townKind(g,family)
 elseif tw4.S5_FOREST[family] then
  return tw4.s5Kind(g,family)
 end
end
M.batch4Kind=batch4Kind
local function batch4Image(m,x,y,g,mode,family)
 local t=batch4Kind(g,family)
 if not t or mode=='vanilla' then return end
 local parity=(x+y)%2
 if t=='statue' then
  -- Old-save rule: a level generated before the town stamps keeps its native
  -- grass and roads, so its (unstamped) statue stays native too.
  local town=false
  for _,d in ipairs(dirs) do
   local nx,ny=x+d[1],y+d[2]
   if nx>=0 and ny>=0 and nx<m.w and ny<m.h and townStamped(m(nx,ny,Map.TERRAIN) or {},family) then town=true end
  end
  if not town then return end
 end
 local function mask(kind)
  local v=0
  for i,d in ipairs(dirs) do
   local nx,ny=x+d[1],y+d[2]
   if nx>=0 and ny>=0 and nx<m.w and ny<m.h and batch4Kind(m(nx,ny,Map.TERRAIN),family)==kind then v=v+2^(i-1) end
  end
  return v
 end
 if mode=='blockout' then
  local kind=(t=='tree' or t=='hardtree' or t=='wall' or t=='cave-wall' or t=='stew' or t=='umbrella' or
   t=='mountain' or t=='statue' or t=='lava' or t=='crystal' or t=='rock' or
   t=='snow-tree' or t=='cold-tree' or t=='void-space' or t=='void-rift' or t=='gold-mountain' or
   t=='jungle-tree' or t=='hut-wall' or t=='hut-door-h' or t=='hut-door-v' or t=='moonstone' or t=='altar' or
   t=='palm' or t=='rock-door' or
   t:match('^cave%-door%-closed')) and 'tree' or
   (t=='deep' or t=='poison' or t=='fountain') and 'water' or
   (t=='exit' or t=='jungle-exit' or t:match('^exit%-') or t:match('^cave%-ladder%-')) and 'exit' or
   t=='road' and 'road' or 'grass'
  return img(kind..parity)
 end
 -- South Beach has its own calmer sand and cell-filling tree tiles (2026-09-29).
 if t=='sand' then return img('refined/beach/sand'..parity) end
 if t=='umbrella' or t=='basket' then return img('refined/beach/'..t..parity) end
 if t=='stew' then return img('refined/keepsake/stew'..parity) end
 if t=='deep' then return img('refined/deep'..mask('deep')..'-'..parity..'-0') end
 if t:match('^cave%-') then
  local k=t:sub(6)
  if k=='wall' then return img('refined/cave/wall-'..mask('cave-wall')..'-'..parity) end
  if k=='marker' then k='floor' end -- S2: the marker post is redrawn over board cave floor
  local n=k=='floor' and tonumber(g.define_as:match('^CAVEFLOOR(%d+)$'))
  if n and n>=8 and n<=16 then return img('refined/cave/floor-rock-'..(n-7)..'-'..parity) end
  if n and n>=17 and n<=18 then return img('refined/cave/floor-mushroom-'..(n-16)..'-'..parity) end
  return img('refined/cave/'..k..parity)
 end
 -- TW2: Last Hope's hard mountain ring reuses the Daikara mountain-wall masks.
 if t=='mountain' then return img('refined/daikara/mountain-wall-'..mask('mountain')..parity) end
 if t=='statue' then return img('refined/grass'..parity) end
 -- TW3: Zigur lava pit (burnt lava masks), Iron Council crystal walls
 -- (crystal-wall masks), Angolwen fountain basin (board deep water, masked
 -- within the basin), post sign and rocks (props over board grass).
 if t=='lava' then return img('refined/burnt/lava-'..mask('lava')..'-'..parity) end
 if t=='crystal' then return img('refined/crystal/wall-'..mask('crystal')..'-'..parity) end
 if t=='fountain' then return img('refined/deep'..mask('fountain')..'-'..parity..'-0') end
 if t=='post' or t=='rock' then return img('refined/grass'..parity) end
 -- TW4: Shatur's snow glades and Point Zero's cold forest use the existing
 -- snow family (Norgos art: the same pine/elm column rhythm; cold forest is
 -- all dark firs, so pine only). Point Zero's platform uses the void family;
 -- its floating rocks rim only toward outer space (native nice_tiler edges),
 -- so a rock next to a building, grass or a native beam endpoint reads joined.
 if t=='snow-ground' then return img('refined/snow/snow-ground'..parity) end
 if t=='snow-tree' then return img('refined/snow/'..(x%2==0 and 'tree-pine' or 'tree-elm')..parity) end
 if t=='cold-tree' then return img('refined/snow/tree-pine'..parity) end
 if t=='void-space' then return img('refined/void/space'..parity) end
 if t=='void-floor' then return img('refined/void/floor'..parity) end
 if t=='void-rift' then return img('refined/void/rift-'..mask('void-rift')..'-'..parity) end
 -- TW5: Gates of Morning's Sunwall mountain ring (golden-mountain wall masks).
 if t=='gold-mountain' then return img('refined/gold-mountain/wall-'..mask('gold-mountain')..'-'..parity) end
 if t=='void-rocks' then
  local v=0
  for i,d in ipairs(dirs) do
   local nx,ny=x+d[1],y+d[2]
   local n=nx>=0 and ny>=0 and nx<m.w and ny<m.h and m(nx,ny,Map.TERRAIN)
   if n and not (type(n)=='table' and n.is_void==true) and batch4Kind(n,family)~='void-space' then v=v+2^(i-1) end
  end
  return img('refined/void/rocks-'..v..'-'..parity)
 end
 -- TW6: Irkkk's jungle (Noxious Caldera art) and bamboo huts. A hut wall's
 -- mask counts hut walls and hut doors (doors sit in the wall line).
 if t=='jungle-grass' then return img('refined/caldera/floor'..parity) end
 if t=='jungle-tree' then return img('refined/caldera/tree-'..({'a','b','c'})[((x*17+y*7)%3)+1]..parity) end
 if t=='jungle-exit' then return img('refined/caldera/exit-world'..parity) end
 if t=='hut-floor' or t=='hut-cooking' then return img('refined/bamboo/floor'..parity) end
 if t=='hut-wall' then
  local v=0
  for i,d in ipairs(dirs) do
   local nx,ny=x+d[1],y+d[2]
   local k=nx>=0 and ny>=0 and nx<m.w and ny<m.h and batch4Kind(m(nx,ny,Map.TERRAIN),family)
   if k=='hut-wall' or type(k)=='string' and k:match('^hut%-door') then v=v+2^(i-1) end
  end
  return img('refined/bamboo/wall-'..v..'-'..parity)
 end
 local door=t:match('^hut%-door%-([hv])')
 if door then
  return img('refined/bamboo/door-'..(t:match('%-open$') and 'open' or 'closed')..'-'..(door=='h' and 'horizontal' or 'vertical')..parity)
 end
 -- S5: the valley's mountain rim and poisoned lake use the Caldera wall and
 -- poison masks; its moonstones and Fearscape portals keep their native
 -- layer over board grass (applyForest redraws it through M.townProp).
 if t=='moonstone' or t=='portal' then return img('refined/grass'..parity) end
 -- S6: Eruan's palms (new board palm over beach sand, plain/mirrored) and
 -- sand exits; Gorbat's loose rock door (native rock layer over beach sand).
 if t=='palm' then return img('refined/eruan/palm-'..((x*17+y*7)%4<2 and 'a' or 'b')..parity) end
 if family=='eruan' and t:match('^exit%-') then return img('refined/eruan/'..t..parity) end
 if t=='rock-door' then return img('refined/beach/sand'..parity) end
 if tw4.S5_FOREST[family] and (t=='poison' or t=='wall') then return img('refined/caldera/'..t..'-'..mask(t)..'-'..parity) end
 if family~='caldera' then
  if t=='tree' and family=='beach' then return img('refined/beach/'..({'tree-oak','tree-pine','tree-willow'})[((x*17+y*7)%3)+1]..parity) end
  if t=='tree' then return img('refined/'..({'tree-oak','tree-pine','tree-willow'})[((x*17+y*7)%3)+1]..parity) end
  if t=='hardtree' then return img('refined/tree-hard'..parity) end
  return img('refined/'..t..parity)
 end
 if t=='tree' then return img('refined/caldera/tree-'..({'a','b','c'})[((x*17+y*7)%3)+1]..parity) end
 if t=='poison' or t=='wall' then return img('refined/caldera/'..t..'-'..mask(t)..'-'..parity) end
 if t=='rock-ground' then return img('refined/daikara/rock-ground'..parity) end
 if t=='altar' then return img('refined/caldera/floor'..parity) end -- T16: native orb layer on top
 return img('refined/caldera/'..t..parity)
end
-- Batch 5 (Charred Scar, Fearscape, Sher'Tul Fortress). Exact source stamp,
-- identity, native display layers and rules only. LAVA_FLOOR is accepted only
-- in its zone-local harmless form (both zones strip its on_stand when loading
-- lava.lua; the damaging Vor Armoury copy keeps its callback and stays native).
local lavaSource='/data/general/grids/lava.lua'
local fortressSource='/data/general/grids/fortress.lua'
-- No callbacks, transitions, doors or special rendering; air is checked per kind.
local function inertCell(g)
 return not (g.on_stand or g.on_dig or rawget(g,'block_move') or rawget(g,'on_move') or g.on_added or
  g.special or g.shader or g.tint or g.textures or g.is_door) and noTransition(g)
end
local function lavaLayers(g)
 local function ok(path) return type(path)=='string' and (path=='invis.png' or path:match('^terrain/lava/lava_mountain[%w_]*%.png$')) end
 for _,mo in ipairs(g.add_mos or {}) do if not ok(mo.image) then return false end end
 for _,d in ipairs(g.add_displays or {}) do
  if not ok(d.image) or d.on_stand or d.change_level then return false end
  for _,mo in ipairs(d.add_mos or {}) do if not ok(mo.image) then return false end end
 end
 return true
end
local function lavaWall(g)
 local id=g.define_as
 local n=tonumber(id:match('^LAVA_WALL(%d+)$'))
 if id~='LAVA_WALL' and not (n and n>=1 and n<=6) then return end
 local s=g._checker_burnt_source
 if not s or s.file~=lavaSource or s.id~=id or
  g.type~='wall' or g.subtype~='lava' or g.name~='lava wall' or g.display~='#' or
  g.always_remember~=true or g.does_block_move~=true or g.block_sight~=true or g.air_level~=-20 or
  g.dig or g.can_pass or g.pass_projectile or g.block_sense or g.block_esp or
  g.image~=(n and ('terrain/lava/lava_mountain5_%d.png'):format(n) or 'terrain/lava/lava_mountain5.png') or
  not lavaLayers(g) or not inertCell(g) then return end
 return 'lava-wall'
end
local function scorchKind(g)
 local s=g._checker_burnt_source
 if not s or s.file~=lavaSource or s.id~=g.define_as then return end
 if rawget(g,'on_move') or rawget(g,'block_move') or g.on_added or g.special or g.tint or g.textures then return end
 local lava=burntTerrain(g)
 if lava=='lava' then return 'lava' end
 if lavaTerrain(g)=='lava-floor' and not g.change_level_check and not g.air_level then return 'lava-floor' end
 return lavaWall(g)
end
local fortressWalls={SOLID_WALL={'solid_wall_block1',false},SOLID_WALL1={'solid_wall_block1',false},
 SOLID_WALL_NORTH1={'solid_wall_block1',true},SOLID_WALL_PILLAR_81={'solid_wall_block1',true},
 SOLID_WALL_PILLAR_2={'solid_wall1',false},SOLID_WALL_NORTH_SOUTH={'solid_wall1',true},SOLID_WALL_SOUTH={'solid_wall1',false}}
for i=1,7 do fortressWalls['SOLID_WALL_SOUTH'..i]={'solid_wall'..i,false} end
local function fortressKind(g)
 local s=g._checker_fortress_source
 local id=g.define_as
 if not s or s.file~=fortressSource or s.id~=id or s.image~=g.image or not inertCell(g) or
  g.dig or g.can_pass or g.pass_projectile or g.add_mos then return end
 if id=='SOLID_FLOOR' then
  if g.type=='floor' and g.subtype=='floor' and g.name=='floor' and g.display=='.' and
   g.image=='terrain/solidwall/solid_floor1.png' and not g.does_block_move and not g.block_sight and
   not g.block_sense and not g.block_esp and not g.air_level and not g.add_displays then return 'floor' end
  return
 end
 local w=fortressWalls[id]
 if not w or g.type~='wall' or g.subtype~='floor' or g.name~='wall' or g.display~='#' or
  g.always_remember~=true or g.does_block_move~=true or g.block_sight~=true or g.block_sense~=true or
  g.block_esp~=true or g.air_level~=-20 or g.z~=3 or g.image~='terrain/solidwall/'..w[1]..'.png' then return end
 if w[2] then
  local d=g.add_displays and #g.add_displays==1 and g.add_displays[1]
  if not d or d.image~='terrain/solidwall/solid_wall_top_block1.png' or d.z~=18 or d.display_y~=-1 or d.add_mos then return end
 elseif g.add_displays then return end
 return 'wall'
end
-- Rak'Shor Pride (bone.lua). The load-time stamp records the definition's
-- function fields; bone.lua's floor/wall/door/stair definitions have none, so
-- a placed cell is accepted only while it still has none (events, hidden
-- vault triggers and aura rings attach on_stand/block_move/change_level_check
-- to individual BONEFLOOR/BONEWALL cells: those stay native). Levers, lever
-- doors and sealed vault doors are never accepted.
local boneSource='/data/general/grids/bone.lua'
local function functionFields(g)
 local out={}
 for k,v in pairs(g) do if type(v)=='function' then out[#out+1]=tostring(k) end end
 table.sort(out);return table.concat(out,',')
end
M.functionFields=functionFields
local function boneLayers(g,allowed)
 -- Native nice_editer layers only: invis carriers, bone wall pieces, sand
 -- floor borders; no extra callbacks or transitions on any layer.
 local function ok(path)
  if type(path)~='string' then return false end
  for _,p in ipairs(allowed) do if path:match(p) then return true end end
  return false
 end
 for _,mo in ipairs(g.add_mos or {}) do if not ok(mo.image) or mo.add_mos then return false end end
 for _,d in ipairs(g.add_displays or {}) do
  if not ok(d.image) or d.on_stand or d.change_level or d.change_zone then return false end
  for _,mo in ipairs(d.add_mos or {}) do if not ok(mo.image) or mo.add_mos then return false end end
 end
 return true
end
local BONE_WALL_LAYERS={'^invis%.png$','^terrain/bone/bonewall_[%w_]+%.png$','^terrain/bone/bone_V3_[%w_]+%.png$',
 '^terrain/bone/bone_ver_edge_[%w_]+%.png$','^terrain/bone/bone_floor_1_01%.png$'}
local BONE_FLOOR_LAYERS={'^invis%.png$','^terrain/sand/sand_%d+_%d+%.png$'}
local boneStairs={
 BONE_LADDER_UP={'stairs-up',-1,nil,'terrain/bone/bone_stairs_up_1_01.png',true},
 BONE_LADDER_DOWN={'stairs-down',1,nil,'terrain/bone/bone_stairs_down_1_01.png',true},
 BONE_LADDER_UP_WILDERNESS={'stairs-exit',1,'wilderness','terrain/bone/bone_stairs_exit_1_01.png',nil},
 BONE_UP_WILDERNESS={'exit-world',1,'wilderness','terrain/worldmap.png',true},
}
-- id -> {state, name, door_opened/door_closed target, dig, native layers}
local boneDoors={
 BONE_DOOR={'door-closed','door','BONE_DOOR_OPEN','BONEFLOOR','terrain/bone/bone_door1.png',{}},
 BONE_DOOR_HORIZ={'door-closed','door','BONE_DOOR_HORIZ_OPEN','BONEFLOOR','terrain/sandfloor.png',
  {mos={'terrain/bone/bone_door1.png'},displays={{'terrain/bone/bonewall_8_1.png',18,-1}}}},
 BONE_DOOR_VERT={'door-closed','door','BONE_DOOR_OPEN_VERT','BONE_DOOR_OPEN_VERT','terrain/sandfloor.png',
  {displays={{'terrain/bone/bone_door1_vert.png',17},{'terrain/bone/bone_door1_vert_north.png',18,-1}}}},
 BONE_DOOR_OPEN={'door-open','open door','BONE_DOOR',nil,'terrain/bone/bone_door1_open.png',{}},
 BONE_DOOR_HORIZ_OPEN={'door-open','open door','BONE_DOOR_HORIZ',nil,'terrain/sandfloor.png',
  {displays={{'terrain/bone/bone_door1_open.png',17},{'terrain/bone/bonewall_8_1.png',18,-1}}}},
 BONE_DOOR_OPEN_VERT={'door-open','open door','BONE_DOOR_VERT',nil,'terrain/sandfloor.png',
  {displays={{'terrain/bone/bone_door1_open_vert.png',17},{'terrain/bone/bone_door1_open_vert_north.png',18,-1}}}},
 -- S2/T4: sealed vault doors (bone.lua:96-124): the plain door's art and
 -- rules plus sense/ESP blocking and the definition's own prompt string.
 BONE_VAULT_DOOR={'door-closed','door','BONE_VAULT_DOOR_OPEN','BONEFLOOR','terrain/bone/bone_door1.png',{},sealed=true},
 BONE_VAULT_DOOR_HORIZ={'door-closed','door','BONE_VAULT_DOOR_HORIZ_OPEN','BONEFLOOR','terrain/sandfloor.png',
  {mos={'terrain/bone/bone_door1.png'},displays={{'terrain/bone/bonewall_8_1.png',18,-1}}},sealed=true},
 BONE_VAULT_DOOR_VERT={'door-closed','door','BONE_VAULT_DOOR_OPEN_VERT','BONE_VAULT_DOOR_OPEN_VERT','terrain/sandfloor.png',
  {displays={{'terrain/bone/bone_door1_vert.png',17},{'terrain/bone/bone_door1_vert_north.png',18,-1}}},sealed=true},
 BONE_VAULT_DOOR_OPEN={'door-open','open door','BONE_VAULT_DOOR',nil,'terrain/bone/bone_door1_open.png',{}},
 BONE_VAULT_DOOR_HORIZ_OPEN={'door-open','open door','BONE_VAULT_DOOR_HORIZ',nil,'terrain/sandfloor.png',
  {displays={{'terrain/bone/bone_door1_open.png',17},{'terrain/bone/bonewall_8_1.png',18,-1}}}},
 BONE_VAULT_DOOR_OPEN_VERT={'door-open','open door','BONE_VAULT_DOOR_VERT',nil,'terrain/sandfloor.png',
  {displays={{'terrain/bone/bone_door1_open_vert.png',17},{'terrain/bone/bone_door1_open_vert_north.png',18,-1}}}},
}
local function boneDoor(g,d,s)
 local closed=d[1]=='door-closed'
 if g.type~='wall' or g.name~=d[2] or g.is_door~=true or g.always_remember~=true or g.image~=d[5] or
  (closed and (g.door_opened~=d[3] or g.door_closed or g.block_sight~=true or g.notice~=true or g.dig~=d[4])) or
  (not closed and (g.door_closed~=d[3] or g.door_opened or g.block_sight or g.notice or g.dig)) or
  g.does_block_move or g.can_pass or g.air_level or
  g.door_player_stop or g.force_clone or g.lever~=nil then return end
 if d.sealed then
  if g.block_sense~=true or g.block_esp~=true or type(g.door_player_check)~='string' or g.door_player_check~=s.check then return end
 elseif g.block_sense or g.block_esp or g.door_player_check then return end
 local want=d[6]
 local mos,displays=g.add_mos or {},g.add_displays or {}
 if #mos~=#(want.mos or {}) or #displays~=#(want.displays or {}) then return end
 for i,img in ipairs(want.mos or {}) do if mos[i].image~=img or mos[i].add_mos then return end end
 for i,w in ipairs(want.displays or {}) do
  local x=displays[i]
  if x.image~=w[1] or x.z~=w[2] or x.display_y~=w[3] or x.add_mos then return end
 end
 return d[1]
end
local function rakshorKind(g)
 local s=g._checker_bone_source
 local id=g.define_as
 if not s or s.file~=boneSource or s.id~=id or s.functions~='' or functionFields(g)~='' or
  g.subtype~='bone' or g.on_stand or g.on_dig or rawget(g,'block_move') or rawget(g,'on_move') or
  g.on_added or g.on_lever_change or g.special or g.shader or g.tint or g.textures or g.lever_action then return end
 if id=='BONEFLOOR' then
  if g.type=='floor' and g.name=='sand' and g.display=='.' and g.image=='terrain/sandfloor.png' and
   g.grow=='BONEWALL' and not g.always_remember and not g.notice and not g.does_block_move and
   not g.block_sight and not g.block_sense and not g.block_esp and not g.dig and not g.can_pass and
   not g.air_level and not g.is_door and noTransition(g) and boneLayers(g,BONE_FLOOR_LAYERS) then return 'floor' end
  return
 end
 local n=tonumber(id:match('^BONEWALL(%d)$') or id:match('^HARDBONEWALL(%d)$'))
 local hard=id:match('^HARDBONEWALL%d?$')~=nil
 if id=='BONEWALL' or id=='HARDBONEWALL' or n and n>=1 and n<=6 then
  if g.type~='wall' or g.name~='bone walls' or g.display~='#' or g.always_remember~=true or
   g.does_block_move~=true or g.block_sight~=true or not g.can_pass or g.can_pass.pass_wall~=1 or
   g.is_door or g.notice or g.pass_projectile or not noTransition(g) or type(g.image)~='string' or
   not (g.image:match('^terrain/bone/bonewall_5_[1-6]%.png$') or g.image=='terrain/bone/bone_floor_1_01.png') then return end
  for k in pairs(g.can_pass) do if k~='pass_wall' then return end end
  if hard then
   if g.air_level~=-15 or g.block_sense~=true or g.block_esp~=true or g.dig then return end
  elseif g.air_level~=-10 or g.block_sense or g.block_esp or g.dig~='BONEFLOOR' then return end
  if not boneLayers(g,BONE_WALL_LAYERS) then return end
  return 'wall'
 end
 local st=boneStairs[id]
 if st then
  if g.type~='floor' or g.image~='terrain/sandfloor.png' or g.change_level~=st[2] or g.change_zone~=st[3] or
   g.notice~=true or g.always_remember~=st[5] or g.does_block_move or g.block_sight or g.dig or g.can_pass or
   g.is_door or g.air_level or g.add_mos then return end
  for _,k in ipairs(transitionKeys) do if k~='change_level' and k~='change_zone' and g[k]~=nil then return end end
  -- Exactly one native stair layer, optionally after the invis sand-border carrier.
  local found=0
  for _,d in ipairs(g.add_displays or {}) do
   if d.image==st[4] then
    if d.add_mos or d.z or d.display_y or d.display_x then return end
    found=found+1
   elseif d.image=='invis.png' then
    if not boneLayers({add_displays={d}},BONE_FLOOR_LAYERS) then return end
   else return end
  end
  if found~=1 then return end
  return st[1]
 end
 local d=boneDoors[id]
 if d then return boneDoor(g,d,s) end
end
rakshorKind=ringAware(rakshorKind)
local function batch5Kind(g,family)
 if not g or type(g.define_as)~='string' or
  (g.replace_display and (not g._checker_terrain or g.replace_display~=g._checker_terrain.display)) then return end
 if family=='scorch' then return scorchKind(g) end
 if family=='shertul' then return fortressKind(g) end
 if family=='rakshor' then return rakshorKind(g) end
end
M.batch5Kind=batch5Kind
local function batch5Image(m,x,y,g,mode,family,zoneName)
 local t=batch5Kind(g,family)
 if not t or mode=='vanilla' then return end
 local parity=(x+y)%2
 local function mask(kind)
  local v=0
  for i,d in ipairs(dirs) do
   local nx,ny=x+d[1],y+d[2]
   if nx>=0 and ny>=0 and nx<m.w and ny<m.h and batch5Kind(m(nx,ny,Map.TERRAIN),family)==kind then v=v+2^(i-1) end
  end
  return v
 end
 if mode=='blockout' then
  return img(((t=='wall' or t=='lava-wall' or t=='lava' or t=='door-closed') and 'tree' or
   (t:match('^stairs%-') or t=='exit-world') and 'exit' or 'grass')..parity)
 end
 if family=='rakshor' then
  if t=='wall' then return img('refined/rakshor/wall-'..mask('wall')..'-'..parity) end
  return img('refined/rakshor/'..t..parity)
 end
 if t=='lava' then return img('refined/burnt/lava-'..mask('lava')..'-'..parity) end
 if t=='lava-floor' then return img('refined/daikara/lava-floor'..parity) end
 if t=='lava-wall' then
  -- S8 (V7): the Fearscape walks on dark lava floor; its rock draws the
  -- darker basalt recolour (same masks). The Charred Scar keeps the ash rock.
  local dark=family=='scorch' and zoneName=='demon-plane' and
   img('refined/scorch-dark/wall-'..mask('lava-wall')..'-'..parity)
  if dark and M.scorchDarkAssets.files[dark] then return dark end
  return img('refined/scorch/wall-'..mask('lava-wall')..'-'..parity)
 end
 if t=='wall' then return img('refined/shertul/wall-'..mask('wall')..'-'..parity) end
 return img('refined/shertul/floor'..parity)
end
-- Caverns to the hidden valley L2: the zone's own exit to the valley. Same
-- native ladder art as CAVE_LADDER_UP; accepted only with its exact
-- destination and no check, callback or extra layer.
local function valleyExit(g)
 local s=g and g._checker_valley_source
 if not s or s.file~='/data/zones/valley-moon-caverns/grids.lua' or s.id~='UP_VALLEY' or g.define_as~='UP_VALLEY' or
  g.type or g.subtype or g.name~='exit to the lost valley' or g.display~='<' or
  g.image~='terrain/cave/cave_floor_1_01.png' or g.always_remember~=true or g.notice~=true or
  g.change_level~=3 or g.change_zone~='valley-moon' or not g.add_mos or #g.add_mos~=1 or
  g.add_mos[1].image~='terrain/cave/cave_stairs_up_2_01.png' or g.add_displays or
  g.does_block_move or g.block_sight or g.dig or g.can_pass or
  g.on_stand or g.on_dig or rawget(g,'on_move') or rawget(g,'block_move') or g.on_added or
  g.special or g.shader or g.tint or g.textures then return end
 for i=3,#transitionKeys do if g[transitionKeys[i]]~=nil then return end end
 return 'ladder-up'
end
M.valleyExit=valleyExit
-- "Same kind of water" (CONTRACT Section 6): deep water and bog water are
-- never the same body, so a mask bit must only ever mean "this neighbour is
-- the same family". bog/bog-misc/bog-tree ARE the same body (bog-tree's own
-- base is bog water, trollmire/grids.lua:60) so they count towards each
-- other's mask; deep water stays its own exclusive family.
local function sameWaterFamily(family,t)
 if family=='deep' then return t=='deep' end
 return t=='bog' or t=='bog-misc' or t=='bog-tree'
end
-- S1: an exact ring/centre cell is judged as the forest identity it was
-- before the event, but only with the native NicerTiles/misc layers these
-- forest grids carry (the loose path above keeps rejecting other layers).
local FOREST_RING_LAYERS={'^invis%.png$','^terrain/grass/[%w_]+%.png$','^terrain/road_dirt/[%w_]+%.png$',
 '^terrain/road_stone/[%w_]+%.png$','^terrain/flower_0[1-6]%.png$','^terrain/mushroom_0[1-7]%.png$',
 '^terrain/misc_bog[1-7]%.png$'}
local nativeForest=terrain
terrain=function(g,allowDarkGrass)
 local t=nativeForest(g,allowDarkGrass)
 if t then return t end
 local v=ringView(g)
 if v and layersMatch(v,FOREST_RING_LAYERS) then return nativeForest(v,allowDarkGrass) end
end
M.forestKind=terrain
local function waterMask(m,x,y,family,allowDarkGrass)
 local mask=0
 for j,d in ipairs(dirs) do
  local t=terrain(m(x+d[1],y+d[2],Map.TERRAIN),allowDarkGrass)
  if sameWaterFamily(family,t) then mask=mask+2^(j-1) end
 end
 return mask
end

local function terrainImage(m,x,y,g,mode,allowDarkGrass,rock,gloom,sand,crystal,cave,lake,burnt,void,zoneName,underwater,graveProps,lakeSurface,batch4,batch5,oldForest)
 if batch4 then return batch4Image(m,x,y,g,mode,batch4) end
 if batch5 then return batch5Image(m,x,y,g,mode,batch5,zoneName) end
 local t
 local waterKind=(underwater or lakeSurface) and underwaterKind(g)
 local sandKind=lakeSurface and surfaceSandKind(g)
 local floatingTree=void and zoneName=='abashed-expanse' and abashedTreeKind(g)
 if waterKind then t=waterKind
 elseif sandKind then t=sandKind
 elseif underwater then t=nil
 elseif graveProps then t=graveyardProp(g) or terrain(g,allowDarkGrass)
 elseif void then t=floatingTree or voidTerrain(g,zoneName)
 elseif burnt then t=burntTerrain(g) or (tw4.s2Forest(g,'forest',zoneName)=='altar' and 'floor') or nil -- T16
 elseif cave=='high-peak' then t=tw4.hpCave(g) -- S9: zone-stamped cave cells only
 elseif cave then t=caveTerrain(g) or zoneName=='valley-moon-caverns' and valleyExit(g) or nil
 elseif crystal then t=crystalTerrain(g)
 elseif sand then t=sandTerrain(g)
 elseif gloom then t=gloomTerrain(g,gloom) or zoneName=='deep-bellow' and (tw4.s2Forest(g,'deep-bellow')) or nil
 elseif rock=='daikara' then t=lavaTerrain(g) or rockTerrain(g,true)
 elseif rock then t=rockTerrain(g)
 else
  -- Primary forest family; Old Forest adds its crystal patches and exit
  -- as fill families, never overriding a recognised forest identity.
  t=(lake and M.lakeExit(g)) or terrain(g,allowDarkGrass)
  -- S2: forest.lua's loose vault rock (T4) and Trollmire's stew (T24).
  if not t then t=tw4.s2Forest(g,'forest',zoneName) end
  if not t and oldForest then
   t=M.oldForestExit(g)
   if not t and oldForest=='crystaline' then
    t=oldForestCrystal(g)
    if t then crystal=oldForestCrystal end
   end
  end
 end
 if not t or mode=='vanilla' then return end
 local parity=(x+y)%2
 if waterKind then
  if mode=='blockout' then return img((t=='wall' or t=='door-closed') and 'tree'..parity or
   t:match('^stairs%-') and 'exit'..parity or 'grass'..parity) end
  if t=='wall' then
   local mask=0
   for i,d in ipairs(dirs) do
    local nx,ny=x+d[1],y+d[2]
    if nx>=0 and ny>=0 and nx<m.w and ny<m.h and
     underwaterKind(m(nx,ny,Map.TERRAIN))=='wall' then mask=mask+2^(i-1) end
   end
   return img('refined/underwater/wall-'..mask..'-'..parity)
  end
  return img('refined/underwater/'..t..parity)
 end
 if sandKind then
  if mode=='blockout' then return img('grass'..parity) end
  return img('refined/sand/floor'..parity)
 end
 if graveProps and graveyardProp(g) then
  if mode=='blockout' then return img((t=='swamp-tree' or t=='grave' or t=='coffin' or t=='coffin-open') and 'tree'..parity or 'grass'..parity) end
  if t=='road' then return img('refined/korpul/floor-a-0-'..parity) end
  if t=='grave' or t=='coffin' or t=='coffin-open' or t=='mausoleum' then
   return img('refined/graveyard/'..t..parity)
  end
  return img('refined/tree-willow'..parity)
 end
 if void then
  if mode=='blockout' then return img((t=='rift' or t=='space' or t=='rocks-tree') and 'tree'..parity or 'grass'..parity) end
  if t=='rift' or t=='rocks' or t=='rocks-tree' then
   local mask=0
   for i,d in ipairs(dirs) do
    local nx,ny=x+d[1],y+d[2]
    if nx>=0 and ny>=0 and nx<m.w and ny<m.h then
     local neighbor=m(nx,ny,Map.TERRAIN)
     local nk=voidTerrain(neighbor,zoneName) or
      zoneName=='abashed-expanse' and abashedTreeKind(neighbor)
     if nk==t or (t=='rocks' or t=='rocks-tree') and
      (nk=='rocks' or nk=='rocks-tree') then mask=mask+2^(i-1) end
    end
   end
   return img('refined/void/'..t..'-'..mask..'-'..parity)
  end
  return img('refined/void/'..t..parity)
 end
 if burnt then
  if mode=='blockout' then
   local kind=(t=='tree' or t=='lava') and 'tree' or
    (t:match('^exit%-') and 'exit' or 'grass')
   return img(kind..parity)
  end
  if t=='lava' then
   local mask=0
   for i,d in ipairs(dirs) do
    local nx,ny=x+d[1],y+d[2]
    if nx>=0 and ny>=0 and nx<m.w and ny<m.h and
     burntTerrain(m(nx,ny,Map.TERRAIN))=='lava' then mask=mask+2^(i-1) end
   end
   return img('refined/burnt/lava-'..mask..'-'..parity)
  end
  return img('refined/burnt/'..t..parity)
 end
 if cave then
  if mode=='blockout' then return img((t=='wall' and 'tree' or t:match('^ladder%-') and 'exit' or 'grass')..parity) end
  if t=='wall' then
   local mask=0
   for i,d in ipairs(dirs) do
    local nx,ny=x+d[1],y+d[2]
    if nx>=0 and ny>=0 and nx<m.w and ny<m.h and
     caveTerrain(m(nx,ny,Map.TERRAIN))=='wall' then mask=mask+2^(i-1) end
   end
   return img('refined/cave/wall-'..mask..'-'..parity)
  end
  if t=='floor' then
   local n=type(g.define_as)=='string' and tonumber(g.define_as:match('^CAVEFLOOR(%d+)$'))
   if n and n>=8 and n<=16 then return img('refined/cave/floor-rock-'..(n-7)..'-'..parity) end
   if n and n>=17 and n<=18 then return img('refined/cave/floor-mushroom-'..(n-16)..'-'..parity) end
  end
  return img('refined/cave/'..t..parity)
 end
 if crystal then
  if mode=='blockout' then return img((t=='wall' and 'tree' or t:match('^ladder%-') and 'exit' or 'grass')..parity) end
  if t=='wall' then
   local mask=0
   for i,d in ipairs(dirs) do
    local nx,ny=x+d[1],y+d[2]
    -- A fill patch counts only its own event walls; bordering trees are
    -- a different family and never join the crystal wall mask.
    local kindOf=crystal==oldForestCrystal and oldForestCrystal or crystalTerrain
    if nx>=0 and ny>=0 and nx<m.w and ny<m.h and
     kindOf(m(nx,ny,Map.TERRAIN))=='wall' then mask=mask+2^(i-1) end
   end
   return img('refined/crystal/wall-'..mask..'-'..parity)
  end
  return img('refined/crystal/'..t..parity)
 end
 if sand then
  if mode=='blockout' then return img((t=='wall' and 'tree' or t:match('^ladder%-') and 'exit' or 'grass')..parity) end
  if t=='wall' then
   local mask=0
   for i,d in ipairs(dirs) do
    local nx,ny=x+d[1],y+d[2]
    if nx>=0 and ny>=0 and nx<m.w and ny<m.h and
     sandTerrain(m(nx,ny,Map.TERRAIN))=='wall' then mask=mask+2^(i-1) end
   end
   return img('refined/sand/wall-'..mask..'-'..parity)
  end
  return img('refined/sand/'..t..parity)
 end
 if gloom then
  if mode=='blockout' then
   local kind=t=='gloom-wall' and 'tree' or t=='gloom-creep' and 'road' or
    t:match('^ladder%-') and 'exit' or 'grass'
   return img(kind..parity)
  end
  local name=t:gsub('^gloom%-','')
  if name=='creep' or name=='wall' then
   local mask=0
   for i,d in ipairs(dirs) do
    local nx,ny=x+d[1],y+d[2]
    if nx>=0 and ny>=0 and nx<m.w and ny<m.h and
     gloomTerrain(m(nx,ny,Map.TERRAIN),gloom)==t then mask=mask+2^(i-1) end
   end
   name=name..'-'..mask..'-'
  end
  -- Orc Breeding Pit: its own readability suite (calm pale floor, solid dark
  -- walls with a face toward the floor, ladders re-seated on that floor).
  -- underground.lua has no creep grid, so every pit image lives in gloom/pit.
  if gloom=='plain' and zoneName=='orc-breeding-pit' and t~='gloom-creep' then return img('refined/gloom/pit/'..name..parity) end
  return img('refined/gloom/'..gloom..'/'..name..parity)
 end
 if rock then
  if mode=='blockout' then
   local kind=(t=='snow-tree' or t=='mountain-wall') and 'tree' or
    (t=='snow-ground' or t=='rock-ground' or t=='lava-floor') and 'grass' or 'exit'
   return img(kind..parity)
  end
  if rock=='daikara' then
   local kind=t=='snow-tree' and (x%2==0 and 'tree-pine' or 'tree-elm') or t
   if kind=='mountain-wall' then
    local mask=0
    if m then for i,d in ipairs(dirs) do
     local nx,ny=x+d[1],y+d[2]
     if nx>=0 and ny>=0 and nx<m.w and ny<m.h and
      rockTerrain(m(nx,ny,Map.TERRAIN),true)=='mountain-wall' then mask=mask+2^(i-1) end
    end end
    kind=kind..'-'..mask
   end
   return img('refined/daikara/'..kind..parity)
  end
  local kind=t=='snow-tree' and (x%2==0 and 'tree-pine' or 'tree-elm') or t
  return img('refined/snow/'..kind..parity)
 end
 if mode=='blockout' then
  local kind=(t=='deep' or t=='bog' or t=='bog-misc' or t=='bog-tree') and 'water'
   or (t=='hardtree' or t=='stew' or t=='vault-rock') and 'tree' or t=='flower' and 'grass' or t
  return img(kind..parity)
 end
 local file
 if t=='tree' then file=({'tree-oak','tree-pine','tree-willow'})[((x*17+y*7)%3)+1]..parity
 elseif t=='hardtree' then file='tree-hard'..parity
 elseif t=='stew' then file='keepsake/stew'..parity -- S2/T24: Keepsake's stew art
 elseif t=='vault-rock' then file='grass'..parity -- S2/T4: native rock redrawn over it
 elseif t=='deep' then file='deep'..waterMask(m,x,y,'deep',allowDarkGrass)..'-'..parity..'-0'
 elseif t=='bog' then file='bog'..waterMask(m,x,y,'bog',allowDarkGrass)..'-'..parity..'-0'
 elseif t=='bog-misc' then file='bog-misc'..(((x*17+y*7)%3)+1)..'-'..parity..'-0'
 elseif t=='bog-tree' then
  -- Both style-selection coefficients in the 'tree' branch above are odd, so
  -- for a 2-way choice that reduces to (x+y)%2 -- the same value as parity
  -- (x*17+y*7 is odd*x+odd*y, congruent to x+y mod 2) -- which would silently
  -- pin style to parity and leave half of every exported mask (whichever
  -- style-a/b + parity combination that formula can never produce) dead
  -- weight. x%2 alone is not a linear combination of x+y, so it varies
  -- independently of parity across the map.
  local style=({'a','b'})[(x%2)+1]
  file='bog-tree-'..style..waterMask(m,x,y,'bog',allowDarkGrass)..'-'..parity..'-0'
 else file=t..parity end
 return img('refined/'..file)
end

-- G0: explicit zone whitelist for the forest-style adapter (replaces the
-- earlier single-zone `short_name=='trollmire'` gate). Old Forest (both
-- DEFAULT and CRYSTALINE layouts, all 4 levels) and Slazish Fens (all 3
-- levels, no layout variant) reuse the exact same grass/tree/hardtree/exit/
-- deep-water/bog-tree/bog/bog-misc identities Trollmire already established
-- (docs/expansion-plan-20260928/TERRAIN-INVENTORY.md Sections 1 and 2); no
-- new art, no new subtypes except the zone-scoped dark_grass alias below.
-- Adding a zone here is NOT a blanket "trust this zone": terrain()/
-- terrainImage() still only recognise the exact identities they already
-- know, so anything else in these zones (LAKE_NUR, PORTAL, vault pools,
-- ROCK_VAULT, ...) still falls through to nil and stays native.
local FOREST_ZONES={trollmire=true,['old-forest']=true,['slazish-fen']=true,['rhaloren-camp']=true,
 ['lake-nur']=true,['golem-graveyard']=true,['last-hope-graveyard']=true}

-- The optional rectangle limits work to cells a native re-tile touched. Cells
-- whose display changes in place are appended to `changed` for updateMap.
local function applyForest(self,x1,y1,x2,y2,changed)
 if not self.level or not self.level.map then return end
 local m=self.level.map
 -- F1: FLOODED Trollmire is now supported too (CONTRACT.md Section 3.4);
 -- gating is by identity in terrain()/terrainImage(), not by layout flag.
 -- The DEFAULT layout's TREE/DEEP_WATER and FLOODED's BOGTREE/BOGWATER/
 -- BOGWATER_MISC are all recognised; anything terrain() does not recognise
 -- still returns nil and stays native, in either layout. G0: the same is
 -- true across zones now -- CRYSTALINE Old Forest and Slazish Fens reuse
 -- identities terrain() already recognises without any extra flag.
 local zoneName=self.zone and self.zone.short_name
 local rock=zoneName=='norgos-lair' and 'norgos' or
  (zoneName=='daikara' or zoneName=='tempest-peak' or zoneName=='temporal-rift' and self.level.level==3) and 'daikara' or nil
 local gloom=zoneName=='heart-gloom' and type(self.zone.is_purified)=='boolean' and
  (self.zone.is_purified and 'dreamy' or 'gloomy') or (zoneName=='deep-bellow' or zoneName=='orc-breeding-pit' and self.level.level~=1) and 'plain' or nil
 local sand=zoneName=='sandworm-lair' or zoneName=='ritch-tunnels' or zoneName=='briagh-lair'
 local crystal=zoneName=='scintillating-caves'
 local cave=(zoneName=='unremarkable-cave' and self.zone.max_level==1) or zoneName=='ardhungol' or zoneName=='valley-moon-caverns' or
  zoneName=='high-peak' and 'high-peak' -- S9: L1-4 caverns (its stone levels simply match no cave cell)
 local burnt=zoneName=='mark-spellblaze'
 local void=(zoneName=='unhallowed-morass' or zoneName=='abashed-expanse' or
  zoneName=='temporal-rift' and self.level.level==1)
 local lake=zoneName=='lake-nur' or zoneName=='temporal-rift' and self.level.level==4
 local underwater=zoneName=='lake-nur' and (self.level.level==2 or
  self.level.level==3 and self.zone.is_flooded==true) or zoneName=='murgol-lair' or
  zoneName=='flooded-cave' or zoneName=='temple-of-creation'
 local batch4=zoneName=='south-beach' and 'beach' or zoneName=='keepsake-meadow' and 'meadow' or
  zoneName=='noxious-caldera' and 'caldera' or (townFiles[zoneName] or tw4.S5_FOREST[zoneName]) and zoneName or nil
 local batch5=(zoneName=='charred-scar' or zoneName=='demon-plane') and 'scorch' or
  zoneName=='shertul-fortress' and 'shertul' or zoneName=='rak-shor-pride' and 'rakshor' or nil
 local lakeSurface=(zoneName=='lake-nur' and self.level.level==1 or
  zoneName=='temporal-rift' and self.level.level==4)
 local graveProps=zoneName=='last-hope-graveyard'
 local forest=zoneName=='temporal-rift' and (self.level.level==2 or self.level.level==4)
 local oldForest=zoneName=='old-forest' and (self.zone.is_crystaline==true and 'crystaline' or 'default') or nil
 local supported=rock or gloom or sand or crystal or cave or burnt or void or lake or underwater or forest or batch4 or batch5 or
  (zoneName and FOREST_ZONES[zoneName] or false)
 -- Scoped alias, never global (CONTRACT: don't widen an identity across
 -- zones just because the subtype string matches -- see the terrain()
 -- comment above for why Heart of the Gloom must NOT get this).
 local allowDarkGrass=zoneName=='old-forest'
 local mode=supported and Options.terrainMode() or 'vanilla'
 -- A combined zone's level with no forest-family grid (Orc Breeding Pit L1)
 -- keeps the stone adapter's mode, also after a native re-tile repair.
 if supported or not (zoneName and M.combined[zoneName] and M.variant(self.zone)) then self.checker_mode=mode end
 x1,y1=math.max(x1 or 0,0),math.max(y1 or 0,0)
 x2,y2=math.min(x2 or m.w-1,m.w-1),math.min(y2 or m.h-1,m.h-1)
 for x=x1,x2 do for y=y1,y2 do
  local g=m(x,y,Map.TERRAIN)
  if g then
   local state=g._checker_terrain
   local foreign=state and g.replace_display~=state.display
   if foreign then g._checker_terrain=nil;state=nil end
   local lakeExit=lake and g.change_zone
   local lakeExitOK=not lakeExit or M.lakeExit(g)
   local graveyardId=g.define_as
   local graveyardAllowed=zoneName~='last-hope-graveyard' or graveyardProp(g) or
    (type(graveyardId)=='string' and
     ((graveyardId=='GRASS' and g.image=='terrain/grass.png' and g.type=='floor' and
       not g.does_block_move and not g.block_sight and
       not g.on_stand and
       not g.change_level and not g.change_zone) or
      (graveyardId=='GRASS_UP_WILDERNESS' and g.change_zone=='wilderness' and
       g.change_level==1 and g.notice==true and not g.on_stand and
       not g.change_level_check) or
      ((tonumber(graveyardId:match('^GRASS_PATCH(%d+)$')) or 99)<=14 and
       g.type=='floor' and not g.does_block_move and
       not g.block_sight and
       not g.on_stand and not g.change_level and not g.change_zone and
       type(g.image)=='string' and g.image:match('^terrain/grass/grass_main_%d+%.png$')) or
      graveyardId=='DEEP_WATER'))
   local file=not foreign and lakeExitOK and graveyardAllowed and
    terrainImage(m,x,y,g,mode,allowDarkGrass,rock,gloom,sand,crystal,cave,lake,burnt,void,zoneName,underwater,graveProps,lakeSurface,batch4,batch5,oldForest)
   -- A foreign replacement is not ours to reinterpret. Native unmodified
   -- grids can be shared across cells, so clone only when installing art.
   if file and (state or not g.replace_display) then
    if not state then
     g=g:clone();m(x,y,Map.TERRAIN,g)
     state={original=g.replace_display};g._checker_terrain=state
    end
    local aura=M.auraKind(g)
    -- E3: an exact event centre keeps its native prop over the board floor.
    local _,_,prop=M.auraCentre(g)
    -- TW2/TW3: an exact town prop (Last Hope statue, Zigur post, Angolwen
    -- rock or 6x5 fountain) keeps its native layer over the board tile.
    -- S5: so do the valley's moonstones and Fearscape portals.
    local _,statue
    if batch4 and (townFiles[batch4] or tw4.S5_FOREST[batch4]) then _,statue=M.townProp(g,batch4)
    -- S2: Keepsake's marker post and forest.lua's loose vault rock.
    else statue=tw4.s2Prop(g,batch4 or 'forest',zoneName) end
    local visualKey=file..'|'..tostring(aura and auraMask(aura))..'|'..tostring(prop and prop.image)..'|'..tostring(statue and statue.image)
    if state.image~=visualKey then
     g:removeAllMOs()
     if state.display then state.display:removeAllMOs() end
     local layers=aura and {auraDisplay(aura)} or nil
     if prop then
      layers=layers or {}
      layers[#layers+1]=Entity.new{image=prop.image,z=prop.z,display_on_seen=true,display_on_remember=true}
     end
     if statue then
      layers=layers or {}
      layers[#layers+1]=Entity.new{image=statue.image,z=statue.z,display_x=statue.display_x,display_y=statue.display_y,
       display_w=statue.display_w,display_h=statue.display_h,display_on_seen=true,display_on_remember=true}
     end
     state.display=Entity.new{image=file,display='.',color={255,255,255},display_on_seen=true,display_on_remember=true,
      add_displays=layers}
     state.image=visualKey;g.replace_display=state.display
     if changed then changed[#changed+1]={x,y} end
    end
   elseif state then
    g:removeAllMOs();state.display:removeAllMOs()
    g.replace_display=state.original;g._checker_terrain=nil
    if changed then changed[#changed+1]={x,y} end
   end
  end
 end end
end


-- This manifest is intentionally empty. Art integration must populate exact paths
-- and set ready only after the complete export has been reviewed.
M.assets={ready=false, revision='p1-contract-1', files={}}
-- Addon data is mounted here before its superloads run. Missing/invalid exports
-- remain native; packaging must supply the reviewed exact-path manifest.
do
 local path='/data-checker-revised/terrain-korpul-manifest.lua'
 if fs and fs.exists and fs.exists(path) then
  local chunk=loadfile(path)
  local ok,manifest=false,nil
  if chunk then ok,manifest=pcall(chunk) end
  if ok and type(manifest)=='table' and type(manifest.files)=='table' and type(manifest.revision)=='string' then
   local valid,count=true,0
   for file,approved in pairs(manifest.files) do
    local relative=type(file)=='string' and file:match('^checker%-revised%+(refined/korpul/[%w%-]+%.png)$')
    if not relative or approved~=true or not fs.exists('/data-checker-revised/gfx/'..relative) then valid=false;break end
    count=count+1
   end
   if valid and count==196 then M.assets=manifest else M.assets.error='incomplete-runtime-exports' end
  else M.assets.error='invalid-runtime-manifest' end
 end
end
-- Stair art is independently gated: a partial/new install must not disable the
-- already reviewed 196 floor/wall/door exports.
M.stairAssets={ready=false,files={}}
local stairFiles={
 ['checker-revised+refined/korpul/stairs-up.png']=true,
 ['checker-revised+refined/korpul/stairs-down.png']=true,
 ['checker-revised+refined/korpul/stairs-world.png']=true,
}
do
 local path='/data-checker-revised/terrain-korpul-stairs-manifest.lua'
 if fs and fs.exists and fs.exists(path) then
  local chunk=loadfile(path)
  local ok,a=false,nil
  if chunk then ok,a=pcall(chunk) end
  if ok and type(a)=='table' and a.ready==true and type(a.revision)=='string' and type(a.files)=='table' then
   local valid,count=true,0
   for file,approved in pairs(a.files) do
    if not stairFiles[file] or approved~=true or not fs.exists('/data-checker-revised/gfx/'..file:sub(17)) then valid=false;break end
    count=count+1
   end
   if valid and count==3 then M.stairAssets=a end
  end
 end
end
-- Conclave Vault walls: a darker recolour of the 16 reviewed Kor'Pul brick
-- masks, independently gated so a partial install keeps Kor'Pul walls.
M.conclaveAssets={ready=false,files={}}
do
 local path='/data-checker-revised/terrain-conclave-manifest.lua'
 if fs and fs.exists and fs.exists(path) then
  local chunk=loadfile(path)
  local ok,a=false,nil
  if chunk then ok,a=pcall(chunk) end
  if ok and type(a)=='table' and a.ready==true and type(a.revision)=='string' and type(a.files)=='table' then
   local valid,count=true,0
   for file,approved in pairs(a.files) do
    local relative=type(file)=='string' and file:match('^checker%-revised%+(refined/conclave/wall%-%d+%-[01]%.png)$')
    if not relative or approved~=true or not fs.exists('/data-checker-revised/gfx/'..relative) then valid=false;break end
    count=count+1
   end
   if valid and count==32 then M.conclaveAssets=a end
  end
 end
end
-- S8 (V2/V7): darker diggable-wall sets, each independently gated so a
-- partial install keeps the previously shipped wall art. korpul-dark holds
-- the recoloured brick walls and the matching door jambs (same masks);
-- scorch-dark the Fearscape basalt. Presentation only.
M.korpulDarkAssets={ready=false,files={}}
M.scorchDarkAssets={ready=false,files={}}
do
 local function load(path,pattern,want)
  if not (fs and fs.exists and fs.exists(path)) then return end
  local chunk=loadfile(path)
  local ok,a=false,nil
  if chunk then ok,a=pcall(chunk) end
  if not (ok and type(a)=='table' and a.ready==true and type(a.revision)=='string' and type(a.files)=='table') then return end
  local count=0
  for file,approved in pairs(a.files) do
   local relative=type(file)=='string' and file:match(pattern)
   if not relative or approved~=true or not fs.exists('/data-checker-revised/gfx/'..relative) then return end
   count=count+1
  end
  if count==want then return a end
 end
 M.korpulDarkAssets=load('/data-checker-revised/terrain-korpul-dark-manifest.lua',
  '^checker%-revised%+(refined/korpul%-dark/[%w%-]+%-%d+%-[01]%.png)$',160) or M.korpulDarkAssets
 M.scorchDarkAssets=load('/data-checker-revised/terrain-scorch-dark-manifest.lua',
  '^checker%-revised%+(refined/scorch%-dark/wall%-%d+%-[01]%.png)$',32) or M.scorchDarkAssets
end
M.mazeAssets={ready=false,files={}}
do
 local path='/data-checker-revised/terrain-maze-manifest.lua'
 if fs and fs.exists and fs.exists(path) then
  local chunk=loadfile(path)
  local ok,a=false,nil
  if chunk then ok,a=pcall(chunk) end
  if ok and type(a)=='table' and a.ready==true and type(a.files)=='table' then
   local valid,count=true,0
   for file,approved in pairs(a.files) do
    local kind,mask,parity
    if type(file)=='string' then
     kind,mask,parity=file:match('^checker%-revised%+refined/maze/(old%-wall)%-(%d+)%-(%d+)%.png$')
     if not kind then kind,mask,parity=file:match('^checker%-revised%+refined/maze/(cracks)%-(%d+)%-(%d+)%.png$') end
    end
    if not kind or tonumber(mask)>(kind=='cracks' and 0 or 15) or tonumber(parity)>1 or approved~=true or
     not fs.exists('/data-checker-revised/gfx/'..file:sub(17)) then valid=false;break end
    count=count+1
   end
   if valid and count==34 then M.mazeAssets=a end
  end
 end
end
local source='/data/general/grids/basic.lua'
local mazeSource='/data/zones/maze/grids.lua'
local conclaveSource='/data/zones/conclave-vault/grids.lua'
-- Old Conclave Vault: its own WALL family (same rules as basic.lua WALL, ruins
-- south faces) and flat decorated floors that keep their native decoration
-- drawn over the board floor. VAT1/VAT2 are not placed by any vault map.
local conclaveIdentities={}
local identities={FLOOR='floor',OLD_FLOOR='floor',OLD_WALL='old-wall'}
for _,suffix in ipairs{'_NORTH_SOUTH','_SOUTH','_SMALL_PILLAR','_PILLAR_2','_PILLAR_4','_PILLAR_6'} do identities['OLD_WALL'..suffix]='old-wall' end
for i=1,5 do for _,suffix in ipairs{'','_NORTH','_PILLAR_8'} do identities['OLD_WALL'..suffix..i]='old-wall' end end
for i=1,3 do for _,suffix in ipairs{'_SOUTH','_NORTH_SOUTH'} do identities['OLD_WALL'..suffix..i]='old-wall' end end
for _,family in ipairs{'WALL','HARDWALL'} do
 identities[family]=family=='WALL' and 'wall' or 'hardwall'
 for _,suffix in ipairs{'_NORTH_SOUTH','_SOUTH','_SMALL_PILLAR','_PILLAR_2','_PILLAR_4','_PILLAR_6'} do identities[family..suffix]=identities[family] end
 for i=1,5 do for _,suffix in ipairs{'','_NORTH','_PILLAR_8'} do identities[family..suffix..i]=identities[family] end end
 for i=1,17 do identities[family..'_SOUTH'..i]=identities[family] end
end
for id,kind in pairs(identities) do if kind=='wall' then conclaveIdentities[id]='wall' end end
for i=1,5 do conclaveIdentities['RUNE_FLOOR'..i]='deco-floor' end
for i=1,3 do conclaveIdentities['BLOOD_FLOOR'..i]='deco-floor' end
for i=1,8 do conclaveIdentities['DECO_FLOOR'..i]='deco-floor' end
local doors={DOOR={'DOOR_OPEN','FLOOR','horizontal'},DOOR_HORIZ={'DOOR_HORIZ_OPEN','FLOOR','horizontal'},DOOR_VERT={'DOOR_OPEN_VERT','DOOR_OPEN_VERT','vertical'}}
-- S2/T4: basic.lua sealed vault doors (basic.lua:257-273). Natively drawn as
-- the plain door; they also block sense/ESP, have no dig and carry the
-- definition's own door_player_check string (a prompt, not a callback). They
-- open into the ordinary DOOR_OPEN/DOOR_HORIZ_OPEN/DOOR_OPEN_VERT.
doors.DOOR_VAULT={'DOOR_OPEN',nil,'horizontal',sealed=true}
doors.DOOR_VAULT_HORIZ={'DOOR_HORIZ_OPEN',nil,'horizontal',sealed=true}
doors.DOOR_VAULT_VERT={'DOOR_OPEN_VERT',nil,'vertical',sealed=true}
local open={DOOR_OPEN={'DOOR','horizontal'},DOOR_HORIZ_OPEN={'DOOR_HORIZ','horizontal'},DOOR_OPEN_VERT={'DOOR_VERT','vertical'}}
for id in pairs(doors) do identities[id]='door-closed' end
for id in pairs(open) do identities[id]='door-open' end
local stairs={
 UP={kind='stairs-up',level=-1,image='terrain/stair_up.png'},
 DOWN={kind='stairs-down',level=1,image='terrain/stair_down.png'},
 UP_WILDERNESS={kind='stairs-world',level=1,zone='wilderness',image='terrain/stair_up_wild.png'},
}
-- S2/T8: basic.lua map-edge exits (basic.lua:60-151): marble floor with one
-- way_next arrow (or the world-map mark), no callback. Same exact stair
-- contract; they reuse the stair overlays by direction.
stairs.FLAT_UP_WILDERNESS={kind='stairs-world',level=1,zone='wilderness',image='terrain/worldmap.png'}
for _,n in ipairs{2,4,6,8} do
 stairs['FLAT_UP'..n]={kind='stairs-up',level=-1,image='terrain/way_next_'..n..'.png'}
 stairs['FLAT_DOWN'..n]={kind='stairs-down',level=1,image='terrain/way_next_'..n..'.png'}
end
for id,d in pairs(stairs) do identities[id]=d.kind end
local transitionFields={'change_level','change_zone','change_level_abs','change_level_check','keep_old_lev','force_down','change_zone_auto_stairs','change_level_auto_stairs','change_level_shift_back'}
-- Aura events may rename a grid and add on_stand, special_minimap and
-- always_remember; retain every other field in the exact source contract.
local fields={'type','subtype','image','display','color_r','color_g','color_b','color_br','color_bg','color_bb','display_scale','does_block_move','block_sight','block_sense','block_esp','air_level','dig','grow','is_door','door_opened','door_closed','can_pass','add_displays','add_mos','z','shader','shader_args','tint','display_x','display_y','display_w','display_h','on_stand_safe'}
for _,k in ipairs(transitionFields) do fields[#fields+1]=k end
fields[#fields+1]='notice'
local function fingerprint(v,depth)
 local t=type(v)
 if t~='table' then return t..':'..tostring(v) end
 if (depth or 0)>8 then return 'deep' end
 local keys={};for k in pairs(v) do
  if type(k)=='number' or (type(k)=='string' and k:sub(1,1)~='_' and k~='uid' and k~='changed') then keys[#keys+1]=k end
 end
 table.sort(keys,function(a,b) return tostring(a)<tostring(b) end)
 local out={};for _,k in ipairs(keys) do out[#out+1]=tostring(k)..'='..fingerprint(v[k],(depth or 0)+1) end
 return '{'..table.concat(out,';')..'}'
end
local function signature(g)
 local event=M.auraEvent(g)
 local out={};for _,k in ipairs(fields) do
  local value=g[k]
  -- Two native events additionally set this safety hint on their ring cells.
  -- Permit only those exact callbacks and only the native true value.
  if k=='on_stand_safe' and value==true and
   (event=='font-life' or event=='spellblaze-scar') then value=nil end
  out[#out+1]=k..'='..fingerprint(value)
 end
 return table.concat(out,'|')
end
-- S2: exits, callback-free doors and static props inside covered zones.
-- Each identity below is local to one native grid file. markSource stamps
-- the definition with its rule signature, the extra identity fields and every
-- function field's defining file and line (reference equality would not
-- survive a save). A placed grid is accepted only while it still equals that
-- stamp AND every rule field, layer and callback equals the reviewed native
-- definition (spec). Levels generated before the stamp keep native.
-- Spec: kind (+orientation/prop), zone (nil: any caller of that family),
-- want (every tw4.S2_RULES field; absent = nil), mos/layers (exact layer
-- images and offsets), funcs (exact callbacks), lore (Lua pattern).
-- (force_clone is left out: the engine sets it on placed copies, e.g. a room
-- generator's resolved stew; it only asks the map to clone on set.)
tw4.S2_EXTRA={'name','always_remember','special_minimap','pass_projectile','show_tooltip','door_player_check',
 'glow','desc','lever','orb_portal','special'}
tw4.S2_RULES={'type','subtype','name','image','display','does_block_move','block_sight','block_sense','block_esp',
 'air_level','dig','grow','is_door','door_opened','door_closed','can_pass','z','shader','tint','notice',
 'always_remember','pass_projectile','show_tooltip','glow','special','orb_portal','lever',
 'special_minimap','on_stand_safe','display_x','display_y','display_w','display_h'}
for _,k in ipairs(transitionFields) do tw4.S2_RULES[#tw4.S2_RULES+1]=k end
function tw4.s2Extra(g)
 local t={}
 for _,k in ipairs(tw4.S2_EXTRA) do if type(g[k])~='function' then t[k]=g[k] end end
 return fingerprint(t)
end
function tw4.s2Funcs(g)
 local out={}
 for k,v in pairs(g) do if type(v)=='function' then
  local i=debug.getinfo(v,'S')
  out[#out+1]=tostring(k)..'@'..tostring(i and i.source)..':'..tostring(i and i.linedefined)
 end end
 table.sort(out);return table.concat(out,',')
end
-- One layer list against its spec: {image, z, display_x, display_y, mos}.
function tw4.s2Layers(list,spec)
 list=list or {}
 if #list~=#(spec or {}) then return false end
 for i,s in ipairs(spec or {}) do
  local d=list[i]
  if type(d)~='table' or d.image~=s[1] or d.z~=s.z or d.display_x~=s.x or d.display_y~=s.y or d.display_w or
   d.display_h~=s.h or d.shader or d.add_displays or not tw4.s2Layers(d.add_mos,s.mos) then return false end
 end
 return true
end
-- Spec builders are block-scoped (the chunk's local budget is shared).
do
local function s2Door(kind,name,image,opened,closed,dig,layers)
 local closedDoor=opened~=nil or nil
 return {kind=kind,layers=layers,want={type='wall',subtype='floor',name=name,image=image,display=closedDoor and '+' or "'",
  notice=closedDoor,always_remember=true,block_sight=closedDoor,is_door=true,door_opened=opened,door_closed=closed,dig=dig}}
end
local function s2Sign(name,image,line,file,lore,notice,alt)
 return {kind='prop',prop='layer',layers={{'terrain/signpost.png'}},funcs='on_move@@'..file..':'..line,lore=lore,fixed=alt~=nil or nil,alt=alt,
  want={name=name,image=image,display='_',always_remember=true,notice=notice}}
end
local function s2Pentagram(name)
 return {kind='prop',prop='mos',mos={{'terrain/floor_pentagram.png'}},want={name=name,image='terrain/marble_floor.png',display=';',notice=true,always_remember=true}}
end
local function s2QuickExit()
 return {kind='prop',prop='layer',layers={{'terrain/maze_teleport.png'}},want={name='teleporting circle to the surface',
  image='terrain/maze_floor.png',display='>',notice=true,show_tooltip=true,change_level=1,change_zone='wilderness'}}
end
local function s2Council(base)
 return {kind=base=='UP' and 'ladder-up' or 'stairs-down',mos={{base=='UP' and 'terrain/stair_up.png' or 'terrain/stair_down.png'}},
  want={type='floor',subtype='floor',name='The Iron Council (Dwarven empire main city)',image='terrain/marble_floor.png',
   display=base=='UP' and '<' or '>',notice=true,always_remember=true,change_level=1,change_zone='town-iron-council',change_zone_auto_stairs=true}}
end
local function s2Lock(orientation,image,layers,name,z)
 local kryl=name=='sealed door' or nil
 return {kind='lock',orientation=orientation,layers=layers,want={type=kryl and 'floor',subtype=kryl and 'floor',name=name,
  image=image,z=z,display='+',notice=true,always_remember=true,block_sight=true,block_sense=kryl,block_esp=kryl,does_block_move=true}}
end
local caveWall8={'terrain/cave/cavewall_8_1.png',z=18,y=-1}
local padlockTop={'terrain/granite_wall3.png',z=18,y=-1,mos={{'terrain/padlock2.png',y=0.1}}}
tw4.S2_SPEC={
 -- T10: the Iron Council exits (a basic.lua DOWN/UP copy with a fixed
 -- destination and auto stairs), the Maze/Elven Ruins teleport circles (floor
 -- plus their native circle layer), South Beach's world exit (its native
 -- love-melinda change_level_check, south-beach/grids.lua:49).
 ['/data/zones/reknor-escape/grids.lua']={zone='reknor-escape',IRON_COUNCIL=s2Council('DOWN')},
 ['/data/zones/deep-bellow/grids.lua']={zone='deep-bellow',IRON_COUNCIL=s2Council('UP')},
 ['/data/zones/maze/grids.lua']={zone='maze',QUICK_EXIT=s2QuickExit()},
 ['/data/zones/ancient-elven-ruins/grids.lua']={zone='ancient-elven-ruins',QUICK_EXIT=s2QuickExit()},
 ['/data/zones/south-beach/grids.lua']={zone='beach',BEACH_UP={kind='exit',mos={{'terrain/worldmap.png'}},
  funcs='change_level_check@@/data/zones/south-beach/grids.lua:49',want={type='floor',subtype='grass',name='exit to the worldmap',
   image='terrain/grass.png',display='<',always_remember=true,notice=true,change_level=1,change_zone='wilderness'}}},
 -- T6: callback-free blocking locks: board closed door plus the native padlock.
 ['/data/zones/crypt-kryl-feijan/grids.lua']={zone='crypt-kryl-feijan',
  LOCK=s2Lock(nil,'terrain/granite_door1.png',nil,'sealed door'),
  LOCK_HORIZ=s2Lock('horizontal','terrain/granite_door1.png',{padlockTop},'sealed door',3),
  LOCK_VERT=s2Lock('vertical','terrain/marble_floor.png',{{'terrain/granite_door1_vert.png',z=17},
   {'terrain/granite_door1_vert_north.png',z=18,y=-1,mos={{'terrain/padlock2.png',x=0.2,y=-0.4}}}},'sealed door'),
  -- T15: the demonic symbols (static floor decoration).
  PENTAGRAM=s2Pentagram('demonic symbol')},
 ['/data/zones/last-hope-graveyard/grids.lua']={zone='last-hope-graveyard',ALTAR=s2Pentagram('ritualistic symbol')},
 -- T14: lore sign posts (native on_move lore; floor plus the native post).
 ['/data/zones/dreadfell/grids.lua']={zone='dreadfell',LORE_NOTE=s2Sign('sign post with a note','terrain/marble_floor.png',32,
  '/data/zones/dreadfell/grids.lua',{'^dreadfell%-note%-%d+$','^dreadfell%-poem%-master$'})},
 ['/data/zones/reknor/grids.lua']={zone='reknor',IRON_THRONE_EDICT=s2Sign('Iron Throne Edict','terrain/marble_floor.png',73,
  '/data/zones/reknor/grids.lua','^iron%-throne%-reknor%-edict$',nil,false)},
 ['/data/zones/ruined-dungeon/grids.lua']={zone='ruined-dungeon',
  LORE1=s2Sign('inscription','terrain/maze_floor.png',34,'/data/zones/ruined-dungeon/grids.lua','^infinite%-dungeon%-1$',true,true),
  LORE2=s2Sign('inscription','terrain/maze_floor.png',34,'/data/zones/ruined-dungeon/grids.lua','^infinite%-dungeon%-2$',true,true),
  LORE3=s2Sign('inscription','terrain/maze_floor.png',34,'/data/zones/ruined-dungeon/grids.lua','^infinite%-dungeon%-3$',true,true),
  LORE4=s2Sign('inscription','terrain/maze_floor.png',49,'/data/zones/ruined-dungeon/grids.lua','^infinite%-dungeon%-4$',true,true)},
 -- T7: Keepsake's cave doors (keepsake-meadow/grids.lua:190-215) and the
 -- cave marker post (T14, native on_move at :119) in the meadow family.
 ['/data/zones/keepsake-meadow/grids.lua']={zone='meadow',
  CAVE_DOOR=s2Door('door-closed-horizontal','door','terrain/cave/cave_door1.png','CAVE_DOOR_OPEN',nil,'CAVEFLOOR'),
  CAVE_DOOR_OPEN=s2Door('door-open-horizontal','open door','terrain/cave/cave_door1_open.png',nil,'CAVE_DOOR'),
  CAVE_DOOR_HORIZ=s2Door('door-closed-horizontal','door','terrain/cave/cave_door1.png','CAVE_DOOR_HORIZ_OPEN',nil,'CAVEFLOOR',{caveWall8}),
  CAVE_DOOR_HORIZ_OPEN=s2Door('door-open-horizontal','open door','terrain/cave/cave_floor_1_01.png',nil,'CAVE_DOOR_HORIZ',nil,
   {{'terrain/cave/cave_door1_open.png',z=17},caveWall8}),
  CAVE_DOOR_VERT=s2Door('door-closed-vertical','door','terrain/cave/cave_floor_1_01.png','CAVE_DOOR_OPEN_VERT',nil,'CAVE_DOOR_OPEN_VERT',
   {{'terrain/cave/cave_door1_vert.png',z=17},{'terrain/cave/cave_door1_vert_north.png',z=18,y=-1}}),
  CAVE_DOOR_OPEN_VERT=s2Door('door-open-vertical','open door','terrain/cave/cave_floor_1_01.png',nil,'CAVE_DOOR_VERT',nil,
   {{'terrain/cave/cave_door1_open_vert.png',z=17},{'terrain/cave/cave_door1_open_vert_north.png',z=18,y=-1}}),
  CAVEFLOOR_CAVE_MARKER={kind='marker',prop='layer',layers={{'terrain/signpost.png'}},funcs='on_move@@/data/zones/keepsake-meadow/grids.lua:119',
   want={name='cave marker',image='terrain/cave/cave_floor_1_01.png',display='_',always_remember=true,notice=true}}},
 -- T24: Trollmire's troll stew (Prox's hut, the L4 treasure map): Keepsake's
 -- stew contract under Trollmire's own file. T4: forest.lua's loose vault
 -- rock (board grass plus the native rock). Both may carry native grass borders.
 ['/data/zones/trollmire/grids.lua']={zone='trollmire',STEW={kind='stew',border=true,mos={{'terrain/troll_stew.png'}},
  want={type='wall',subtype='grass',name='troll stew',image='terrain/grass.png',display='~',does_block_move=true,pass_projectile=true}}},
 ['/data/general/grids/forest.lua']={ROCK_VAULT={kind='vault-rock',prop='mos',border=true,mos={{'terrain/huge_rock.png'}},check=true,
  want={type='wall',subtype='grass',name='huge loose rock',image='terrain/grass.png',display='+',notice=true,always_remember=true,
   block_sight=true,block_sense=true,block_esp=true,is_door=true,door_opened='GRASS',dig='GRASS'}}},
 -- S4/T1: the underwater air bubble (water.lua:98-116). Its native on_stand
 -- (defined at :106) spends a charge and swaps in WATER_FLOOR; it stays
 -- attached and unwrapped. Family key 'underwater' matches no forest/stone caller.
 ['/data/general/grids/water.lua']={zone='underwater',WATER_FLOOR_BUBBLE={kind='bubble',
  funcs='on_stand@@/data/general/grids/water.lua:106',want={type='floor',subtype='water',name='underwater air bubble',
   image='terrain/underwater/subsea_floor_bubbles.png',display=':',air_level=15,show_tooltip=true}}},
 -- T16: callback altars, board floor plus the native altar layer. Spellblaze
 -- L2's corrupting altar (burntland ALTAR + quest on_move at :28) and the
 -- Caldera L2 altar of dreams (blocking, dream block_move at :35, 2-tall orb).
 ['/data/zones/mark-spellblaze/grids.lua']={zone='mark-spellblaze',ALTAR_CORRUPT={kind='altar',prop='layer',
  layers={{'terrain/floor_pentagram.png'}},funcs='on_move@@/data/zones/mark-spellblaze/grids.lua:28',
  want={type='floor',subtype='burnt',name='corrupted altar',image='terrain/grass_burnt1.png',display=';',notice=true,always_remember=true}}},
 ['/data/zones/noxious-caldera/grids.lua']={zone='caldera',ALTAR={kind='altar',prop='layer',
  layers={{'terrain/pedestal_orb_04.png',z=18,y=-1,h=2}},funcs='block_move@@/data/zones/noxious-caldera/grids.lua:35',
  want={type='wall',subtype='grass',name='altar of dreams',image='terrain/jungle/jungle_grass_floor_01.png',display='&',
   notice=true,always_remember=true,does_block_move=true,block_sight=true}}},
 -- S9: High Peak's two ways to the next level (high-peak/grids.lua:265-281):
 -- no type/subtype, no callback, one native up-stair layer each (the peak is
 -- climbed; drawn with the up art like Tannen's tower). The Roomer one is the
 -- board stairs-up overlay on board stone, the cavern one the cave up-ladder.
 -- PORTAL_BOSS, the farportals, VOID_PORTAL and the ORB_* invocation portals
 -- (callbacks, 3x3 portal bases, quest state) are not listed: native.
 ['/data/zones/high-peak/grids.lua']={zone='high-peak',
  HIGH_PEAK_UP={kind='stairs-up',mos={{'terrain/stair_up.png'}},want={name='next level',image='terrain/marble_floor.png',
   display='>',notice=true,always_remember=true,change_level=1}},
  CAVE_HIGH_PEAK_UP={kind='ladder-up',layers={{'terrain/cave/cave_stairs_up_2_01.png'}},want={name='next level',
   image='terrain/cave/cave_floor_1_01.png',display='>',notice=true,always_remember=true,change_level=1}}},
}
end
-- S4/T1: exact air bubble: the S2 stamp/spec (every rule field, the extra
-- identity fields and the on_stand's file+line) plus the fields S2 leaves out.
function M.bubbleKind(g)
 local spec,zone=tw4.s2(g)
 if spec and zone=='underwater' and spec.kind=='bubble' and g.define_as=='WATER_FLOOR_BUBBLE' and
  g.air_condition==nil and type(g.nb_charges)=='number' and not g.add_displays and not g.add_mos then return 'bubble' end
end
tw4.S2_BORDER={'^invis%.png$','^terrain/grass/grass_[%w_]+%.png$'}
function tw4.s2Lore(lore,patterns)
 for _,p in ipairs(type(patterns)=='table' and patterns or {patterns}) do if lore:match(p) then return true end end
end
-- The stamp and spec a placed grid matches, and the view it was judged as
-- (a native grass-border carrier dropped where the spec allows it).
function tw4.s2(g)
 -- An exact native aura ring (S1) is judged as the grid it cloned.
 -- Any other on_stand stays on g and must then equal the spec's funcs (S4).
 if type(g)=='table' and g.on_stand~=nil then g=M.ringView(g) or g end
 local s=type(g)=='table' and rawget(g,'_checker_s2_source')
 local file=s and tw4.S2_SPEC[s.file]
 local spec=file and s.id==g.define_as and file[s.id]
 if not spec or (g.tint_r~=nil and g.tint_r~=1) or (g.tint_g~=nil and g.tint_g~=1) or (g.tint_b~=nil and g.tint_b~=1) or
  g.textures or g.tilt_angle then return end
 local v=g
 if spec.border and g.add_displays then
  for _,d in ipairs(g.add_displays) do
   if d.image~='invis.png' or d.z or d.display_x or d.display_y or d.add_displays or d.shader or
    not d.add_mos or #d.add_mos==0 or not layersMatch({add_mos=d.add_mos},tw4.S2_BORDER) then return end
  end
  v={};for k,x in pairs(g) do v[k]=x end;v.add_displays=nil;v=setmetatable(v,getmetatable(g))
 end
 if signature(v)~=s.signature or tw4.s2Extra(v)~=s.extra or tw4.s2Funcs(g)~=s.funcs or s.funcs~=(spec.funcs or '') or
  -- Lore: the definition's own value (Ruined Dungeon's may carry the ALT1
  -- clue prefix); Dreadfell's note gets its value from zone.lua after creation.
  (spec.lore and not (type(g.lore)=='string' and (not spec.fixed or g.lore==s.lore) and
   tw4.s2Lore((spec.alt and g.lore:gsub('^alt1%-','') or g.lore),spec.lore))) or
  (not spec.lore and g.lore~=nil) or not tw4.s2Layers(v.add_mos,spec.mos) or not tw4.s2Layers(v.add_displays,spec.layers) then return end
 if spec.check then
  if type(g.door_player_check)~='string' or g.door_player_check~=s.check then return end
 elseif g.door_player_check~=nil then return end
 local want=spec.want
 for _,k in ipairs(tw4.S2_RULES) do
  local x=v[k]
  if type(x)~='function' and fingerprint(x)~=fingerprint(want[k]) then return end
 end
 if g.door_player_stop or g.on_lever_change or g.lever_action then return end
 return spec,file.zone,v
end
-- Stone-side S2 kinds (classify): exits, locks, props over the board floor.
function tw4.s2Stone(g,zoneName)
 local spec,zone=tw4.s2(g)
 if spec and zone==zoneName then
  if spec.kind=='stairs-down' or spec.kind=='stairs-up' or spec.kind=='lock' then return spec.kind,spec.orientation end
  if spec.kind=='prop' then return 'prop',spec.prop=='mos' and g.add_mos[1] or g.add_displays[1] end
 end
 -- T10: the Rel tunnel in Halfling L4 is a map-file quickEntity: its native
 -- yeek-only change_level_check (halfling-ruins-last.lua:31) is the identity.
 if zoneName=='halfling-ruins' and g and g.define_as==nil and
  sameCallback(rawget(g,'change_level_check'),'@/data/maps/zones/halfling-ruins-last.lua',31) and
  tw4.s2Funcs(g)=='change_level_check@@/data/maps/zones/halfling-ruins-last.lua:31' and
  g.image=='terrain/marble_floor.png' and g.display=='>' and g.always_remember==true and g.show_tooltip==true and
  g.notice==true and g.change_level==1 and g.change_zone=='wilderness' and not g.add_mos and
  tw4.s2Layers(g.add_displays,{{'terrain/stair_down.png'}}) and g.type==nil and g.subtype==nil and g.define_as==nil and
  not (g.does_block_move or g.block_sight or g.block_sense or g.block_esp or g.dig or g.can_pass or g.is_door or g.air_level or
   g.pass_projectile or g.z or g.shader or g.special or g.textures or g.door_player_check) and
  (g.tint_r==nil or g.tint_r==1) and (g.tint_g==nil or g.tint_g==1) and (g.tint_b==nil or g.tint_b==1) then
  for i=3,#transitionFields do if transitionFields[i]~='change_level_check' and g[transitionFields[i]]~=nil then return end end
  return 'stairs-down'
 end
end
-- Forest/batch-side S2 kinds: family 'forest' is applyForest's own forest
-- path (zone-less forest.lua identities, or the caller zone's own file).
function tw4.s2Forest(g,family,zoneName)
 local spec,zone=tw4.s2(g)
 if spec and (family=='forest' and (zone==nil or zone==zoneName) or family~='forest' and zone==family) then return spec.kind,spec end
end
-- The native layer a forest-side S2 prop keeps over its board tile.
function tw4.s2Prop(g,family,zoneName)
 local kind,spec=tw4.s2Forest(g,family,zoneName)
 if kind and spec.prop=='mos' then return g.add_mos[1] end
 if kind and spec.prop=='layer' then return g.add_displays[1] end
end
function M.markSource(g,file)
 -- S1: the definition's own values of every field a ring/centre event
 -- rewrites, so an event cell can be compared with the grid it cloned.
 -- A fresh definition is always current; a base= copy is re-stamped here.
 if type(g.define_as)=='string' then
  g._checker_def={id=g.define_as,name=g.name,always_remember=g.always_remember,
   special_minimap=g.special_minimap,on_stand_safe=g.on_stand_safe,stand=g.on_stand~=nil or nil,
   display=g.display,color_r=g.color_r,color_g=g.color_g,color_b=g.color_b,notice=g.notice}
 end
 if file=='/data/general/grids/sand.lua' and g.define_as=='SAND' then
  g._checker_surface_sand_source={file=file,id='SAND'}
 end
 -- S6: the defining file of Eruan's palms and sand exits.
 if file=='/data/general/grids/sand.lua' and type(g.define_as)=='string' then
  g._checker_sand_source={file=file,id=g.define_as}
 end
 if file=='/data/general/grids/water.lua' and type(g.define_as)=='string' then
  g._checker_water_source={file=file,id=g.define_as,image=g.image}
  if g.define_as:match('^POISON_DEEP_WATER[1-6]?$') then
   local s,a=type(g.on_stand)=='function' and debug.getinfo(g.on_stand,'S'),
    type(g.combatAttack)=='function' and debug.getinfo(g.combatAttack,'S')
   local stamp=g._checker_water_source
   stamp.stand_source=s and s.source;stamp.stand_line=s and s.linedefined
   stamp.attack_source=a and a.source;stamp.attack_line=a and a.linedefined
  end
 end
 if (file=='/data/general/grids/forest.lua' or file=='/data/general/grids/jungle.lua') and
  type(g.define_as)=='string' then
  g[file=='/data/general/grids/forest.lua' and '_checker_forest_source' or '_checker_jungle_source']={file=file,id=g.define_as}
 end
 if file=='/data/zones/keepsake-meadow/grids.lua' and type(g.define_as)=='string' and
  (keepsakeEvents[g.define_as] or g.define_as=='STEW' or g.define_as=='GRASS_UP2_UP2') then
  local info=type(rawget(g,'on_move'))=='function' and debug.getinfo(rawget(g,'on_move'),'S')
  g._checker_keepsake_source={file=file,id=g.define_as,move_source=info and info.source,move_line=info and info.linedefined}
 end
 if file==boneSource and type(g.define_as)=='string' then
  g._checker_bone_source={file=file,id=g.define_as,functions=functionFields(g),check=g.door_player_check}
 end
 -- S2: the exact definition of each reviewed zone-local identity.
 local s2=tw4.S2_SPEC[file]
 if s2 and type(g.define_as)=='string' and type(s2[g.define_as])=='table' then
  g._checker_s2_source={file=file,id=g.define_as,signature=signature(g),extra=tw4.s2Extra(g),funcs=tw4.s2Funcs(g),
   check=g.door_player_check,lore=g.lore}
 end
 if file==fortressSource and type(g.define_as)=='string' then
  g._checker_fortress_source={file=file,id=g.define_as,image=g.image}
 end
 if file=='/data/zones/valley-moon-caverns/grids.lua' and g.define_as=='UP_VALLEY' then
  g._checker_valley_source={file=file,id='UP_VALLEY'}
 end
 if file=='/data/zones/south-beach/grids.lua' and (g.define_as=='UMBRELLA' or g.define_as=='BASKET') then
  g._checker_beach_source={file=file,id=g.define_as}
 end
 if file==conclaveSource and type(g.define_as)=='string' and conclaveIdentities[g.define_as] and
  not (g._checker_grid_source and g._checker_grid_source.file==source and g._checker_grid_source.id==g.define_as) then
  -- The vault redefines WALL (its south faces use ruins art) and adds
  -- decorated floors on top of basic.lua; stamp only those local definitions.
  g._checker_grid_source={file=file,id=g.define_as,signature=signature(g),name=g.name,
   always_remember=g.always_remember,special_minimap=g.special_minimap}
 end
 if file=='/data/zones/last-hope-graveyard/grids.lua' and type(g.define_as)=='string' and
  (g.define_as=='ROAD' or g.define_as=='SWAMPTREE' or
   g.define_as:match('^SWAMPTREE%d+$') or
   g.define_as:match('^GRAVE%d+$') or g.define_as=='COFFIN' or
   g.define_as=='COFFIN_OPEN' or g.define_as=='MAUSOLEUM') then
  g._checker_grave_source={file=file,id=g.define_as,image=g.image,
   block_move=rawget(g,'block_move'),on_added=g.on_added,
   change_level=g.change_level,lore=g.lore}
 end
 if voidSources[file] and type(g.define_as)=='string' then
  -- A zone's loadList also returns imported definitions. Keep the precise
  -- general-file stamp for those, while marking its local rift override.
  if file=='/data/general/grids/void.lua' or not g._checker_void_source then
   g._checker_void_source={file=file,id=g.define_as}
  end
 end
 if burntSources[file] and type(g.define_as)=='string' then
  g._checker_burnt_source={file=file,id=g.define_as}
 end
 if file==caveSource and type(g.define_as)=='string' then
  g._checker_cave_source={file=file,id=g.define_as}
 end
 if file=='/data/general/grids/crystal.lua' and type(g.define_as)=='string' then
  g._checker_crystal_source={file=file,id=g.define_as}
 end
 if file=='/data/zones/old-forest/grids.lua' and type(g.define_as)=='string' then
  -- The zone list also returns its nested crystal.lua import (CRYSTALINE).
  local stamp=g._checker_crystal_source
  if stamp and not stamp.origin then M.markCrystalOrigin(g,'old-forest-zone') end
  if g.define_as=='LAKE_NUR' then g._checker_oldforest_source={file=file,id='LAKE_NUR',image=g.image} end
 end
 if gloomSources[file] and type(g.define_as)=='string' then
  -- Grid:loadList for the zone returns nested underground definitions too.
  -- Keep the more precise general-file stamp when that outer call finishes.
  if file~='/data/zones/heart-gloom/grids.lua' or not g._checker_gloom_source then
   g._checker_gloom_source={file=file,id=g.define_as,skin=gloomSources[file]}
  end
 end
 if file==source and identities[g.define_as] then
  -- S2/T4: a sealed door's own prompt string is part of its identity.
  g._checker_grid_source={file=file,id=g.define_as,signature=signature(g),name=g.name,
   always_remember=g.always_remember,special_minimap=g.special_minimap,check=g.door_player_check}
 end
 -- TW1: the outer town list call stamps every definition it returned,
 -- including its nested basic/forest/water imports (already stamped above
 -- by their own calls). Old saves without this stamp keep native towns.
 for _,townFile in pairs(townFiles) do
  if file==townFile and type(g.define_as)=='string' then g._checker_town_source={file=file,id=g.define_as} end
 end
 -- S5: the outer zone list call stamps every definition it returned (nested
 -- imports keep their general-file stamps too).
 for _,zoneFile in pairs(tw4.S5_FILES) do
  if file==zoneFile and type(g.define_as)=='string' then g._checker_zone_source={file=file,id=g.define_as} end
 end
 if file==mazeSource and g.define_as=='CRACKS' then
  local info=type(g.block_move)=='function' and debug.getinfo(g.block_move,'S')
  g._checker_maze_source={file=file,id='CRACKS',block_source=info and info.source,block_line=info and info.linedefined}
 end
end
function M.variant(zone)
 if zone and zone.short_name=='ruins-kor-pul' and (zone.is_hideout==nil or type(zone.is_hideout)=='boolean') then
  return zone.is_hideout and 'HIDEOUT' or 'DEFAULT'
 end
 -- Both camp layouts import the same untouched basic.lua stone grids. Its
 -- OVERGROUND outdoor grids are handled independently by applyForest.
 if zone and zone.short_name=='rhaloren-camp' then return 'RHALOREN' end
 -- Dreadfell's Roomer and its static vaults import basic.lua stone grids;
 -- the source stamp and final-state contract still decide every cell.
 if zone and zone.short_name=='dreadfell' then return 'DREADFELL' end
 -- These zones import the same basic.lua definitions. Every cell still has
 -- to pass the source stamp and exact final-state contract in classify().
 if zone and zone.short_name=='thieves-tunnels' then return 'THIEVES' end
 if zone and zone.short_name=='halfling-ruins' then return 'HALFLING' end
 if zone and zone.short_name=='reknor' then return 'REKNOR' end
 if zone and zone.short_name=='reknor-escape' then return 'REKNOR_ESCAPE' end
 if zone and zone.short_name=='temporal-rift' then return 'TEMPORAL_RIFT' end
 if zone and zone.short_name=='ruined-dungeon' then return 'RUINED_DUNGEON' end
 if zone and zone.short_name=='blighted-ruins' then return 'BLIGHTED_RUINS' end
 if zone and zone.short_name=='last-hope-graveyard' then return 'LAST_HOPE_GRAVEYARD' end
 if zone and zone.short_name=='lake-nur' then return 'LAKE_NUR' end
 if zone and zone.short_name=='crypt-kryl-feijan' then return 'KRYL_FEIJAN' end
 if zone and zone.short_name=='conclave-vault' then return 'CONCLAVE_VAULT' end
 -- Batch 5 stone: untouched basic.lua definitions in these zones. Orc
 -- Breeding Pit L1, the Charred Scar camp and the Sher'Tul Fortress's outer
 -- rock share their level with another family handled by applyForest.
 if zone and zone.short_name=='telmur' then return 'TELMUR' end
 if zone and zone.short_name=='ancient-elven-ruins' then return 'ELVEN_RUINS' end
 if zone and zone.short_name=='vor-armoury' then return 'VOR_ARMOURY' end
 if zone and zone.short_name=='orc-breeding-pit' then return 'ORC_PIT' end
 if zone and zone.short_name=='charred-scar' then return 'CHARRED_SCAR' end
 if zone and zone.short_name=='shertul-fortress' then return 'SHERTUL' end
 -- S3/T23: stone rooms (lesser vaults, Prox's hut, peak buildings) inside
 -- forest, mountain and crystal-cave zones import untouched basic.lua grids.
 -- applyForest keeps owning every outdoor/cave identity on the same level.
 if zone and zone.short_name=='old-forest' then return 'OLD_FOREST' end
 if zone and zone.short_name=='trollmire' then return 'TROLLMIRE' end
 if zone and zone.short_name=='daikara' then return 'DAIKARA' end
 if zone and zone.short_name=='tempest-peak' then return 'TEMPEST_PEAK' end
 if zone and zone.short_name=='scintillating-caves' then return 'SCINTILLATING' end
 -- TW1: static towns import untouched basic.lua stone (building walls, the
 -- Lumberjack cabins). classify() also requires the town's own list stamp.
 if zone and zone.short_name=='town-derth' then return 'TOWN_DERTH' end
 if zone and zone.short_name=='town-lumberjack-village' then return 'LUMBERJACK_VILLAGE' end
 -- TW2: Last Hope's walls, castle and marble plaza; Elvala's walls and old-stone plaza.
 if zone and zone.short_name=='town-last-hope' then return 'TOWN_LAST_HOPE' end
 if zone and zone.short_name=='town-elvala' then return 'TOWN_ELVALA' end
 -- TW3: Zigur's buildings and arena, Angolwen's shop walls, the Iron Council hall.
 if zone and zone.short_name=='town-zigur' then return 'TOWN_ZIGUR' end
 if zone and zone.short_name=='town-angolwen' then return 'TOWN_ANGOLWEN' end
 if zone and zone.short_name=='town-iron-council' then return 'TOWN_IRON_COUNCIL' end
 -- TW4: Point Zero's shop blocks (basic.lua HARDWALL). Shatur has no stone
 -- and stays a forest-only town (no variant).
 if zone and zone.short_name=='town-point-zero' then return 'TOWN_POINT_ZERO' end
 -- TW5: Gates of Morning's stone plaza, building blocks and shop walls.
 if zone and zone.short_name=='town-gates-of-morning' then return 'TOWN_GATES_OF_MORNING' end
 -- S5: the Shadow Crypt's crypt levels, Tannen's Tower (and its reversed
 -- stairs), the Slavers' compound and Ring of Blood arena, and Derth's
 -- southeast arena import untouched basic.lua stone.
 if zone and zone.short_name=='shadow-crypt' then return 'SHADOW_CRYPT' end
 if zone and zone.short_name=='tannen-tower' then return 'TANNEN_TOWER' end
 if zone and zone.short_name=='ring-of-blood' then return 'RING_OF_BLOOD' end
 if zone and zone.short_name=='arena-unlock' then return 'ARENA_UNLOCK' end
 -- S6: Gorbat Pride's gate halls, stairs and sub-vaults, and Eruan's greater
 -- vaults (Forest generator rooms) import basic.lua stone.
 if zone and zone.short_name=='gorbat-pride' then return 'GORBAT_PRIDE' end
 if zone and zone.short_name=='eruan' then return 'ERUAN' end
 -- S9: High Peak's Roomer levels (L5-10), their pits and vaults, and the
 -- Sanctum (static L11) import basic.lua stone; L1-4 caverns are cave cells.
 if zone and zone.short_name=='high-peak' then return 'HIGH_PEAK' end
 if zone and zone.short_name=='maze' and (zone.is_collapsed==nil or type(zone.is_collapsed)=='boolean') then
  return zone.is_collapsed and 'COLLAPSED' or 'DEFAULT'
 end
end
-- Old Forest and Trollmire set nicer_tiler_overlay="DungeonWallsGrass": a
-- re-tiled wall/door whose south neighbour is grass gets one cosmetic grass
-- fringe MO (NicerTilesOverlays.lua dungeonwalls_grass). Classify the grid
-- as if that exact native fringe were absent; any other MO stays native.
local wallFringe={['terrain/granite_door1.png']={'grass_granite_wall2',0.5},['terrain/granite_door1_open.png']={'grass_granite_wall2',0.5},
 ['terrain/granite_wall2.png']={'grass_granite_wall2',0.5},
 ['terrain/granite_wall_pillar_small.png']={'grass_granite_wall_pillar_small',0.3}}
for i=1,17 do wallFringe['terrain/granite_wall2_'..i..'.png']={'grass_granite_wall2',0.5} end
for i=1,3 do wallFringe['terrain/granite_wall_pillar_'..i..'.png']={'grass_granite_wall_pillar_'..i,0.4} end
local function isFringe(image,mos)
 local f=wallFringe[image]
 if not f or type(mos)~='table' or #mos~=1 then return false end
 local mo=mos[1]
 for k in pairs(mo) do if k~='image' and k~='display_y' then return false end end
 return mo.image=='terrain/dungeonwalls_grass/'..f[1]..'.png' and mo.display_y==f[2]
end
local function unfringe(g)
 if not g or not g._checker_grid_source then return g end
 local dropMos=false
 if g.add_mos then
  if not isFringe(g.image,g.add_mos) then return g end
  dropMos=true
 end
 local displays
 for i,d in ipairs(g.add_displays or {}) do
  if d.add_mos then
   if not isFringe(d.image,d.add_mos) then return g end
   displays=displays or {unpack(g.add_displays)}
   local c={};for k,v in pairs(d) do c[k]=v end;c.add_mos=nil
   displays[i]=setmetatable(c,getmetatable(d))
  end
 end
 if not dropMos and not displays then return g end
 local v={};for k,value in pairs(g) do v[k]=value end
 if dropMos then v.add_mos=nil end
 if displays then v.add_displays=displays end
 return setmetatable(v,getmetatable(g))
end
M.unfringe=unfringe
-- TW3: stone-side cells local to one town list (exact list stamp, full rule
-- contract, native layers only). Iron Council's two zone exits are DOWN copies
-- with a fixed destination: Kor'Pul down-stairs art. DEEP_BELLOW's glow=true
-- adds one image-less WildernessGrid display; it only draws while the level
-- has an entrance_glow, which the wilderness alone sets, so it is dropped.
-- Iron Council statues and Zigur's arena rocks keep their native prop over
-- the board floor.
local councilExits={ESCAPE_REKNOR={zone='reknor-escape',level=3,auto=true},
 DEEP_BELLOW={zone='deep-bellow',level=1,glow=true}}
local councilStatues={STATUE1='statue_dwarf_taxman',STATUE2='statue_dwarf_mage',STATUE3='statue_dwarf_axeman',
 STATUE4='statue_dwarf_warrior',STATUE5='statue_dwarf_axeman2',STATUE6='statue_dwarf_archer'}
function M.townStone(g,zoneName)
 if not g or not townFiles[zoneName] or not townStamped(g,zoneName) or type(g.define_as)~='string' then return end
 local id=g.define_as
 for _,v in pairs(g) do if type(v)=='function' then return end end
 if g.on_stand or g.on_dig or g.on_added or g.special or g.shader or g.tint or g.textures or hasMos(g) and not councilExits[id] or
  g.dig or g.grow or g.can_pass or g.pass_projectile or g.is_door or g.road or
  (g.tint_r~=nil and g.tint_r~=1) or (g.tint_g~=nil and g.tint_g~=1) or (g.tint_b~=nil and g.tint_b~=1) then return end
 local e=zoneName=='town-iron-council' and councilExits[id]
 if e then
  if g.type~='floor' or g.subtype~='floor' or g.image~='terrain/marble_floor.png' or g.display~='>' or
   g.notice~=true or g.always_remember~=true or g.does_block_move or g.block_sight or g.block_sense or g.block_esp or
   g.air_level or g.z or g.change_level~=e.level or g.change_zone~=e.zone or g.change_zone_auto_stairs~=e.auto or
   g.change_level_abs or g.change_level_check or g.keep_old_lev or g.force_down or g.change_level_auto_stairs or
   g.change_level_shift_back or fingerprint(g.add_mos)~=fingerprint({{image='terrain/stair_down.png'}}) then return end
  if e.glow then
   if g.glow~=true then return end
   if g.add_displays then
    local d=#g.add_displays==1 and g.add_displays[1]
    if not d or d.image~=nil or d.display~=' ' or d.z~=17 or d.change_zone~=e.zone or d.add_mos or d.add_displays or
     d.shader or d.display_x or d.display_y or d.display_w or d.display_h then return end
   end
  elseif g.glow or g.add_displays then return end
  return 'stairs-down'
 end
 local d=g.add_displays and #g.add_displays==1 and g.add_displays[1]
 if not d or d.add_mos or d.add_displays or d.shader or d.display_x or d.display_w or
  g.image~='terrain/oldstone_floor.png' or g.does_block_move~=true or g.block_sight~=true or noTransition(g)==false or
  g.notice then return end
 local art=zoneName=='town-iron-council' and councilStatues[id]
 if art then
  if d.image~='terrain/statues/'..art..'.png' or d.z~=18 or d.display_y~=-1 or d.display_h~=2 or
   g.type or g.subtype or g.display~='@' or g.z or g.block_sense or g.block_esp or g.air_level or g.always_remember then return end
  return 'prop',d
 end
 if zoneName=='town-zigur' and id=='ROCK' and d.image=='terrain/huge_rock.png' and d.z==2 and not d.display_y and
  not d.display_h and g.type=='wall' and g.subtype=='floor' and g.display=='#' and g.z==1 and g.always_remember==true and
  g.block_sense==true and g.block_esp==true and g.air_level==-20 then return 'prop',d end
end
function M.classify(g)
 local maze=g and g._checker_maze_source
 if maze and maze.file==mazeSource and maze.id=='CRACKS' and g.define_as=='CRACKS' then
  local info=type(g.block_move)=='function' and debug.getinfo(g.block_move,'S')
  if info and info.source==maze.block_source and info.linedefined==maze.block_line and
   g.type=='wall' and g.subtype=='cracks' and g.pass_projectile==true and
   type(g.image)=='string' and g.image:match('^terrain/cracks/[%w_]+%.png$') and
   not g.does_block_move and not g.block_sight and not g.dig and not g.can_pass and
   not g.change_level and not g.change_zone and not g.add_mos and
   (not g.add_displays or (#g.add_displays==1 and g.add_displays[1].image=='invis.png')) and
   not g.replace_display then return 'cracks' end
 end
 g=unfringe(g)
 -- S5: Tannen's reversed stairs and water-edged floor are judged as the
 -- basic.lua grid they are (tw4.tannenView).
 local tannen=tw4.tannenView(g)
 if tannen then return M.classify(tannen) end
 -- E3: an exact event centre is the floor it cloned plus the event's marks.
 if g and g.on_stand~=nil then
  local _,centre=M.auraCentre(g)
  if centre then
   local k=M.classify(centre)
   if k=='floor' or k=='deco-floor' then return k end
   return
  end
 end
 local stamp=g and g._checker_grid_source
 local town=game and game.zone and game.zone.short_name
 if g and town and townFiles[town] and not townStamped(g,town) then return end
 -- S6: Gorbat's and Eruan's stone need the list stamp too (older levels keep native).
 -- S9: so does High Peak's.
 if g and (town=='gorbat-pride' or town=='eruan' or town=='high-peak') and not tw4.zoneStamped(g,town) then return end
 if g and town and townFiles[town] then
  local kind,d=M.townStone(g,town)
  if kind then return kind,d end
 end
 -- S2: zone-local exits, locks and props (exact stamp and native spec).
 local s2,s2o=tw4.s2Stone(g,town)
 if s2 then return s2,s2o end
 if not stamp or (stamp.file~=source and stamp.file~=conclaveSource) or stamp.id~=g.define_as or stamp.signature~=signature(g) then return end
 local kind=stamp.file==source and identities[stamp.id] or stamp.file==conclaveSource and conclaveIdentities[stamp.id]
 local aura=M.auraKind(g)
 -- Aura events also attach their callback to the vault's walls, unrenamed.
 -- In the vault's static entry level the same aura reaches basic.lua hard walls.
 local auraWall=aura and g.name==stamp.name and g.always_remember==true and
  (kind=='wall' and stamp.file==conclaveSource or
   kind=='hardwall' and stamp.file==source and game and game.zone and game.zone.short_name=='conclave-vault')
 -- S1/E2: in every stone zone an exact native ring event (source file and
 -- line) reaches walls and doors unrenamed, and renames stairs like floors.
 local ring,rd=ringEvent(g.on_stand)
 if ring and not auraWall and g.always_remember==true then
  if (kind=='wall' or kind=='hardwall' or kind=='old-wall' or kind=='door-closed' or kind=='door-open') then
   auraWall=g.name==stamp.name and fingerprint(g.special_minimap)==fingerprint(stamp.special_minimap)
  elseif stairs[stamp.id] and g.type=='floor' then
   auraWall=renamedAs(rd.rename,stamp.name,g.name) and (stamp.special_minimap~=nil and
    fingerprint(g.special_minimap)==fingerprint(stamp.special_minimap) or
    stamp.special_minimap==nil and sameColor(g.special_minimap,rd.minimap))
  end
 end
 if not aura and (g.name~=stamp.name or g.always_remember~=stamp.always_remember or
  fingerprint(g.special_minimap)~=fingerprint(stamp.special_minimap)) then return end
 if g.on_stand and not auraWall and (not aura or (kind~='floor' and kind~='deco-floor') or g.name==stamp.name or not g.always_remember or not g.special_minimap) then return end
 if rawget(g,'block_move') or rawget(g,'on_move') or g.on_dig or g.on_door_opened or g.on_lever_change or g.tilt_angle or g.shader or g.tint or (g.tint_r~=nil and g.tint_r~=1) or (g.tint_g~=nil and g.tint_g~=1) or (g.tint_b~=nil and g.tint_b~=1) or g.textures then return end
 -- A sealed vault door's prompt must be its own definition's string.
 if not kind or g.special or g.door_player_stop or g.shader or g.door_player_check~=nil and
  not (doors[stamp.id] and doors[stamp.id].sealed and type(g.door_player_check)=='string' and g.door_player_check==stamp.check) then return end
 local stair=stairs[stamp.id]
 if not stair then
  if g.add_mos then return end
  for _,k in ipairs(transitionFields) do if g[k]~=nil then return end end
 end
 for k,v in pairs(g) do if type(v)=='function' and not (k=='on_stand' and aura) then return end end
 if g.subtype~='floor' then return end
 if stair then
  if g.type~='floor' or g.image~='terrain/marble_floor.png' or g.does_block_move or g.block_sight or g.block_sense or g.block_esp or g.air_level or g.can_pass or g.dig or g.is_door or g.add_displays then return end
  if g.change_level~=stair.level or g.change_zone~=stair.zone or g.notice~=true or g.always_remember~=true then return end
  for i=3,#transitionFields do if g[transitionFields[i]]~=nil then return end end
  -- Exact reviewed single-layer definition; extra layers, transformations and
  -- alternate destinations remain native even if imported under a known name.
  if fingerprint(g.add_mos)~=fingerprint({{image=stair.image}}) then return end
 elseif kind=='floor' then
  if g.type~='floor' or g.does_block_move or g.block_sight or g.block_sense or g.block_esp or g.air_level or g.can_pass or g.dig or g.add_displays then return end
 elseif kind=='deco-floor' then
  -- The signature already pins the one native decoration layer.
  if g.type~='floor' or g.does_block_move or g.block_sight or g.block_sense or g.block_esp or g.air_level or g.can_pass or g.dig or
   not g.add_displays or #g.add_displays~=1 or g.add_displays[1].z~=3 or g.add_displays[1].add_mos or
   type(g.add_displays[1].image)~='string' or not g.add_displays[1].image:match('^terrain/ruins/floor_[%w_]+%.png$') then return end
 elseif kind=='wall' or kind=='hardwall' or kind=='old-wall' then
  if g.type~='wall' or g.does_block_move~=true or g.block_sight~=true or g.air_level~=-20 or g.is_door then return end
  if kind=='wall' then
   if g.dig~='FLOOR' or not g.can_pass or g.can_pass.pass_wall~=1 or (function() local n=0;for _ in pairs(g.can_pass) do n=n+1 end;return n~=1 end)() or g.block_sense or g.block_esp then return end
  elseif kind=='old-wall' then
   if g.dig or g.can_pass or g.block_sense or g.block_esp or g.always_remember~=true then return end
  elseif g.dig or g.can_pass or g.block_sense~=true or g.block_esp~=true then return end
 else
  local sealed=doors[stamp.id] and doors[stamp.id].sealed
  if g.type~='wall' or g.is_door~=true or g.does_block_move or g.can_pass or g.air_level then return end
  if sealed then
   if g.block_sense~=true or g.block_esp~=true or type(g.door_player_check)~='string' then return end
  elseif g.block_sense or g.block_esp then return end
  if doors[stamp.id] then
   local d=doors[stamp.id]
   if g.door_opened~=d[1] or g.dig~=d[2] or g.door_closed or g.block_sight~=true then return end
   return kind,d[3]
  else
   local d=open[stamp.id]
   if g.door_closed~=d[1] or g.door_opened or g.dig or g.block_sight then return end
   return kind,d[2]
  end
 end
 return kind
end

local visualFields={'image','display','color_r','color_g','color_b','back_color','color_br','color_bg','color_bb','z','display_x','display_y','display_w','display_h','display_scale','add_mos','add_displays'}
local function copy(v)
 if type(v)~='table' then return v end
 local out={};for k,value in pairs(v) do
  if type(value)~='function' and (type(k)~='string' or (k:sub(1,1)~='_' and k~='uid' and k~='changed')) then out[k]=copy(value) end
 end
 return out
end
-- A native layer's display_on_* flags are usually Grid class defaults, which
-- copy() (own fields only) would drop: the snapshot must keep them, or native
-- mode loses every nested layer (wall caps, statues, rocks) once painted.
local function layerFlags(src,dst)
 for i,d in ipairs(type(src.add_displays)=='table' and src.add_displays or {}) do
  local c=type(dst.add_displays)=='table' and dst.add_displays[i]
  if type(d)=='table' and type(c)=='table' then
   c.display_on_seen=d.display_on_seen;c.display_on_remember=d.display_on_remember;c.display_on_unknown=d.display_on_unknown
   layerFlags(d,c)
  end
 end
end
local function nativeSnapshot(g)
 local out={display_on_seen=true,display_on_remember=true}
 for _,key in ipairs(visualFields) do out[key]=copy(g[key]) end
 layerFlags(g,out)
 return out
end
local displays=setmetatable({}, {__mode='k'})
local function entity(def)
 local t=copy(def)
 if t.add_displays then for i,d in ipairs(t.add_displays) do t.add_displays[i]=entity(d) end end
 return Entity.new(t)
end
local function display(record,file,overlay,aura)
 local cache=displays[record]
 if not cache then cache={};displays[record]=cache end
 local key=file and (file..'|'..(overlay or '')..'|'..(aura and auraMask(aura) or '')..'|'..(record.prop and record.prop.image or '')) or 'native'
 if not cache[key] then
  local def=file and {image=file,display='.',color_r=255,color_g=255,color_b=255,display_on_seen=true,display_on_remember=true} or record.native
  if file and aura then def.add_displays={{image=auraMask(aura),z=2,display_on_seen=true,display_on_remember=true}} end
  -- Decorated vault floors keep their exact native decoration over the board floor.
  if file and record.kind=='deco-floor' and record.native.add_displays then
   def.add_displays=def.add_displays or {}
   for _,d in ipairs(record.native.add_displays) do
    local layer=copy(d);layer.display_on_seen=true;layer.display_on_remember=true
    def.add_displays[#def.add_displays+1]=layer
   end
  end
  -- E3: an exact event centre keeps its native prop over the board floor.
  if file and record.prop then
   def.add_displays=def.add_displays or {}
   def.add_displays[#def.add_displays+1]={image=record.prop.image,z=record.prop.z,display_y=record.prop.display_y,
    display_h=record.prop.display_h,display_on_seen=true,display_on_remember=true}
  end
  if file and overlay then def.add_mos={{image=overlay}} end
  cache[key]=entity(def)
 end
 return cache[key]
end
function M.visible(m,x,y)
 -- ESP alone is not terrain observation.
 return x>=0 and y>=0 and x<m.w and y<m.h and m.seens and m.seens(x,y) and m.infovs and m.infovs(x,y) and true or false
end
local record
function M.observe(m,x,y,g)
 if not M.visible(m,x,y) then return false end
 return record(m,x,y,g)
end
-- The per-cell record a visible observation creates; also used by the
-- remembered-town install below, which never creates knowledge.
record=function(m,x,y,g)
 local records=m._checker_korpul
 if not records then records={};m._checker_korpul=records end
 local key=x+y*m.w
 local kind,orientation=M.classify(g)
 if g and g.replace_display then kind=nil end
 local old=records[key]
 if not kind then
  if old then records[key]=nil;return true end
  return false
 end
 local sig=signature(g)
 local aura=M.auraKind(g)
 local _,_,centreProp=M.auraCentre(g)
 local prop=centreProp and {image=centreProp.image,z=centreProp.z} or nil
 -- TW3: a town prop cell (statue, rock) keeps its exact native layer.
 -- S2: so do lore posts, pentagrams and teleport circles (classify returns it).
 if kind=='prop' then
  local d=orientation;orientation=nil
  if type(d)~='table' then kind=nil
  else prop={image=d.image,z=d.z,display_y=d.display_y,display_h=d.display_h} end
 end
 if not kind then
  if old then records[key]=nil;return true end
  return false
 end
 if old and old.signature==sig and old.aura==aura and (old.prop and old.prop.image)==(prop and prop.image) then return false end
 records[key]={kind=kind,orientation=orientation,signature=sig,aura=aura,prop=prop,
  source=(g._checker_grid_source or g._checker_maze_source or g._checker_town_source or g._checker_s2_source or {}).id,native=nativeSnapshot(g)}
 return true
end
local offsets={{0,-1},{1,0},{0,1},{-1,0}}
function M.mask(m,x,y)
 local mask=0
 for i,d in ipairs(offsets) do
  local nx,ny=x+d[1],y+d[2]
  local known=nx>=0 and ny>=0 and nx<m.w and ny<m.h and m._checker_korpul and m._checker_korpul[nx+ny*m.w]
  if known and (known.kind=='wall' or known.kind=='hardwall' or known.kind=='old-wall') then mask=mask+2^(i-1) end
 end
 return mask
end
function M.assetPath(kind,orientation,mask,parity,x,y)
 -- S2/T6: a callback-free lock is the board closed door (+ native padlock).
 if kind=='lock' then kind='door-closed' end
 if kind=='floor' or kind=='deco-floor' or kind=='prop' or kind:match('^stairs%-') then kind=((x*17+y*7)%3==0) and 'floor-b' or 'floor-a';mask=0 end
 if orientation then kind=kind..'-'..orientation end
 return img('refined/korpul/'..kind..'-'..mask..'-'..parity)
end
function M.stairsReady()
 return M.ready() and M.stairAssets.ready==true
end
function M.ready()
 return M.assets.ready==true and type(M.assets.files)=='table'
end
-- Board path for a record from its current neighbour records.
local function recordFile(m,x,y,record)
 local stair=record.kind:match('^stairs%-')
 local mazeKind=record.kind=='old-wall' or record.kind=='cracks'
 -- S2/T6: an untiled lock (Kryl-Feijan LOCK before its door3d re-tile)
 -- faces its wall line: vertical between north and south walls only.
 local orientation=record.orientation or record.kind=='lock' and (M.mask(m,x,y)%16==5 and 'vertical' or 'horizontal') or nil
 local path=mazeKind and img('refined/maze/'..record.kind..'-'..(record.kind=='cracks' and 0 or M.mask(m,x,y))..'-'..((x+y)%2)) or
  M.assetPath(record.kind,orientation,M.mask(m,x,y),(x+y)%2,x,y)
 -- TW4: Point Zero's shop blocks stand on grey floating rocks, where the grey
 -- Kor'Pul hard wall (lum. 107) matches the rocks (116) under the purple zone
 -- tint; the existing dark Conclave brick keeps blocking walls legible.
 -- Presentation only: the identity is still the exact basic.lua HARDWALL.
 local pzWall=record.kind=='hardwall' and game and M.variant(game.zone)=='TOWN_POINT_ZERO'
 if (record.kind=='wall' and game and M.variant(game.zone)=='CONCLAVE_VAULT' or pzWall) and M.conclaveAssets.ready then
  local conclave=img('refined/conclave/wall-'..M.mask(m,x,y)..'-'..((x+y)%2))
  if M.conclaveAssets.files[conclave] then path=conclave end
 end
 -- S8 (V2): in the listed stone zones the diggable WALL and the door jambs
 -- beside it draw the darker recolour of the same Kor'Pul masks. HARDWALL,
 -- floors, stairs and exits keep their art. Presentation only.
 local dark=M.korpulDarkAssets.ready and game and game.zone and tw4.S8_DARK[game.zone.short_name] and
  (record.kind=='wall' or record.kind=='lock' or record.kind:match('^door%-')) and path:gsub('%+refined/korpul/','+refined/korpul-dark/',1)
 if dark and M.korpulDarkAssets.files[dark] then path=dark end
 record.file=(mazeKind and M.mazeAssets.files[path] or M.assets.files[path] or M.conclaveAssets.files[path] or M.korpulDarkAssets.files[path]) and path or nil
 record.overlay=stair and img('refined/korpul/'..record.kind) or record.kind=='lock' and 'terrain/padlock2.png' or nil
end
local unknownDisplay
function M.render(m,x,y,g,mode)
 if not g or g.replace_display then return end
 -- The native FBO draws remembered-capable MOs with always_show before applying
 -- its soft visibility mask. Native art in completely unknown cells can bleed
 -- into the visible tile edge. Emit no content for ALL unknown cells, without
 -- reading their identity; do not create knowledge or touch native remember.
 if mode=='refined' and (M.ready() or M.mazeAssets.ready) and not M.visible(m,x,y) and m.remembers and not m.remembers(x,y) then
  if not unknownDisplay then
   unknownDisplay=Entity.new{image='invis.png',display=' ',display_on_seen=false,display_on_remember=false,display_on_unknown=false}
  end
  return unknownDisplay
 end
 local record=m._checker_korpul and m._checker_korpul[x+y*m.w]
 if not record then return end
 local file,overlay
 local stair=record.kind:match('^stairs%-')
 local mazeKind=record.kind=='old-wall' or record.kind=='cracks'
 local ready=mazeKind and M.mazeAssets.ready or M.ready()
 if mode=='refined' and ready and (not stair or M.stairsReady()) then
  -- Never recompute hidden tile edges from newly observed neighbours.
  if M.visible(m,x,y) then recordFile(m,x,y,record) end
  file=record.file
  if file and not (mazeKind and M.mazeAssets.files[file] or M.assets.files[file] or M.conclaveAssets.files[file] or M.korpulDarkAssets.files[file]) then file=nil end
  overlay=record.overlay
  if stair and (not overlay or not M.stairAssets.files[overlay]) then file=nil;overlay=nil end
 end
 -- Native snapshots are used only after this cell has actually been painted.
 if file then record.painted=true end
 if file or record.painted then return display(record,file,overlay,file and record.aura) end
end

-- The context is synchronous and exception-safe; it never enters a save file.
local context
function M.withContext(ctx,fn,...)
 local previous=context;context=ctx
 local result={pcall(fn,...)}
 if ctx.native_cache then
  ctx.grid._mo=ctx.native_cache.mo;ctx.grid._last_mo=ctx.native_cache.last_mo
 end
 context=previous
 if not result[1] then error(result[2],0) end
 return unpack(result,2)
end
function M.context() return context end
-- Zones whose levels mix stone-adapter cells with applyForest families.
M.combined={['rhaloren-camp']=true,['last-hope-graveyard']=true,['lake-nur']=true,['temporal-rift']=true,
 ['orc-breeding-pit']=true,['charred-scar']=true,['shertul-fortress']=true,
 ['old-forest']=true,trollmire=true,daikara=true,['tempest-peak']=true,['scintillating-caves']=true,
 ['town-derth']=true,['town-lumberjack-village']=true,['town-last-hope']=true,['town-elvala']=true,
 ['town-zigur']=true,['town-angolwen']=true,['town-iron-council']=true,['town-point-zero']=true,
 ['town-gates-of-morning']=true,
 -- S5: grass, trees, water, sand and lava pits beside basic.lua stone.
 ['tannen-tower']=true,['ring-of-blood']=true,['arena-unlock']=true,
 -- S6: sand, mountains, bamboo roosts and palms beside basic.lua stone.
 ['gorbat-pride']=true,eruan=true,
 -- S9: High Peak's cavern levels (cave family) beside its stone levels.
 ['high-peak']=true}
-- TW1: Zone:newLevel calls map:rememberAll for all_remembered levels, so a
-- town's whole plan is native knowledge from arrival although its cells were
-- never in FOV (map.seens). observe() only records FOV cells, which left the
-- town's unseen stone native until walked past. For the gated towns only,
-- and only when the level itself is all_remembered, record every cell the
-- map remembers and fix a hidden cell's edges from its static neighbours.
-- Cells the map does not remember are never read; other zones are untouched.
-- S5: also the all_remembered stone levels of the S5 stone zones (Shadow
-- Crypt L3, Tannen's Tower top, the Ring of Blood arena, Derth's arena).
function M.installRemembered(host)
 local level=host.level
 local m=level and level.map
 local zoneName=host.zone and host.zone.short_name
 if not m or not (townFiles[zoneName] or tw4.S5_REMEMBER[zoneName]) or not M.variant(host.zone) or type(level.data)~='table' or
  level.data.all_remembered~=true or not m.remembers then return 0 end
 for x=0,m.w-1 do for y=0,m.h-1 do
  if m.remembers(x,y) then record(m,x,y,m(x,y,Map.TERRAIN)) end
 end end
 local n=0
 for key,rec in pairs(m._checker_korpul or {}) do
  local x,y=key%m.w,math.floor(key/m.w)
  if m.remembers(x,y) and not M.visible(m,x,y) then recordFile(m,x,y,rec);n=n+1 end
 end
 return n
end
function M.apply(host)
 if not host.level or not host.level.map then return end
 if M.variant(host.zone) then
  host.checker_mode=Options.terrainMode()=='refined' and (M.ready() or M.mazeAssets.ready) and 'refined' or 'vanilla'
  if M.combined[host.zone.short_name] then
   -- Forest owns only recognised outdoor identities; the stone adapter keeps
   -- its observed-cell records and handles all remaining basic.lua stones.
   applyForest(host)
  end
  M.installRemembered(host)
  -- Settings/layer changes may refresh once; FOV and mutations are local.
  return
 end
 return applyForest(host)
end
-- Native NicerTiles replaces Grid objects when it re-tiles (digging, earth
-- talents, Jumpgate, on_block_change, mid-game full passes). Kor'Pul's per-cell
-- adapter heals on updateMap; the forest installs replace_display once, so the
-- touched rectangle is re-applied here. Water masks read the four neighbours,
-- so callers pass the native 3x3 grown by one cell.
function M.repair(host,x1,y1,x2,y2)
 if not host.level or not host.level.map or
  (M.variant(host.zone) and not M.combined[host.zone.short_name]) then return end
 local m,changed=host.level.map,{}
 applyForest(host,x1,y1,x2,y2,changed)
 for _,c in ipairs(changed) do m:updateMap(c[1],c[2]) end
 if #changed>0 then m.changed=true end
 return #changed
end
return M
