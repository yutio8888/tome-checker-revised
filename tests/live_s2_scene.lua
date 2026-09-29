-- Offline fixture only (S2: exits, callback-free doors and static props inside
-- covered zones). Reuses the S5 scene module (stats, identity probe, rule
-- digest, natives listing, poses, particle pause) and adds a per-cell report
-- of every S2 candidate identity: its ids, its adapter kind on both paths, who
-- owns the display (forest replace_display / painted stone record / native),
-- the board file, overlay and redrawn native prop, and the rule fields that
-- must never change (transitions, movement, sight, door targets, callbacks).
-- Never edits a grid rule field; actors near the photographed window are removed.
local Map=require 'engine.Map'
local Terrain=require 'mod.class.CheckerTerrain'
local tw=dofile('/data-checker-fixture/monster-live_s5_scene.lua')
local M=setmetatable({},{__index=tw})

local IDS={}
for _,id in ipairs{'FLAT_UP_WILDERNESS','FLAT_UP2','FLAT_UP4','FLAT_UP6','FLAT_UP8','FLAT_DOWN2','FLAT_DOWN4','FLAT_DOWN6','FLAT_DOWN8',
	'LAKE_NUR','IRON_COUNCIL','QUICK_EXIT','BEACH_UP','DOOR_VAULT','DOOR_VAULT_HORIZ','DOOR_VAULT_VERT','ROCK_VAULT',
	'BONE_VAULT_DOOR','BONE_VAULT_DOOR_HORIZ','BONE_VAULT_DOOR_VERT','BONE_VAULT_DOOR_OPEN','BONE_VAULT_DOOR_HORIZ_OPEN','BONE_VAULT_DOOR_OPEN_VERT',
	'LOCK','LOCK_HORIZ','LOCK_VERT','CAVE_DOOR','CAVE_DOOR_OPEN','CAVE_DOOR_HORIZ','CAVE_DOOR_HORIZ_OPEN','CAVE_DOOR_VERT','CAVE_DOOR_OPEN_VERT',
	'ALTAR','PENTAGRAM','IRON_THRONE_EDICT','LORE_NOTE','LORE1','LORE2','LORE3','LORE4','CAVEFLOOR_CAVE_MARKER','STEW'} do IDS[id]=true end
M.IDS=IDS
local function fnInfo(f)
	if type(f)~='function' then return false end
	local i=debug.getinfo(f,'S');return tostring(i and i.source)..':'..tostring(i and i.linedefined)
end
local function relTunnel(g)
	return g and g.define_as==nil and fnInfo(rawget(g,'change_level_check'))=='@/data/maps/zones/halfling-ruins-last.lua:31'
end
-- T21: a plain FLOOR with a native NicerTiles marble-to-water edge carrier.
local function edgedFloor(g)
	local d=g and g.define_as=='FLOOR' and g.add_displays and g.add_displays[1]
	if not d or d.image~='invis.png' then return false end
	for _,mo in ipairs(d.add_mos or {}) do
		if type(mo.image)=='string' and mo.image:match('^terrain/marble_water/') then return true end
	end
	return false
end
local function owner(m,x,y,g)
	local st=g._checker_terrain
	if st and g.replace_display==st.display then return 'forest',g.replace_display end
	local r=m._checker_korpul and m._checker_korpul[x+y*m.w]
	if r and r.painted and r.file then return 'stone',r end
	return 'native'
end
local function cell(m,x,y,g,zoneName,key)
	local who,d=owner(m,x,y,g)
	local c={id=key,x=x,y=y,owner=who,visible=Terrain.visible(m,x,y),remembered=m.remembers(x,y) and true or false,
		stone_kind=Terrain.classify(g) or false,forest_kind=Terrain.batch4Kind(g,zoneName) or false,
		change_level=g.change_level or false,change_zone=g.change_zone or false,auto=g.change_zone_auto_stairs or false,
		check=fnInfo(rawget(g,'change_level_check')),on_move=fnInfo(rawget(g,'on_move')),block_move=fnInfo(rawget(g,'block_move')),
		does_block_move=g.does_block_move and true or false,block_sight=g.block_sight and true or false,
		block_sense=g.block_sense and true or false,is_door=g.is_door and true or false,door_opened=g.door_opened or false,
		door_closed=g.door_closed or false,door_player_check=type(g.door_player_check)=='string',lore=g.lore or false,
		s2_stamp=g._checker_s2_source and g._checker_s2_source.file or false}
	if who=='forest' then
		c.image=d.image
		local l=d.add_displays and d.add_displays[#d.add_displays]
		c.prop=l and l.image or false
	elseif who=='stone' then
		c.image=d.file;c.overlay=d.overlay or false;c.prop=d.prop and d.prop.image or false;c.kind=d.kind
	end
	return c
end
-- Every S2 candidate cell of the level (plus T21 edged floors, counted).
function M.s2cells()
	local m=game.level.map
	local zoneName=game.zone.short_name
	local out={zone=zoneName,level=game.level.level,cells={},edged={n=0,board=0,visible=0,sample=false},by_id={}}
	for x=0,m.w-1 do for y=0,m.h-1 do
		local g=m(x,y,Map.TERRAIN)
		local key=g and (IDS[g.define_as] and g.define_as or relTunnel(g) and '<rel tunnel>')
		if key then
			local c=cell(m,x,y,g,zoneName,key)
			out.cells[#out.cells+1]=c
			local b=out.by_id[key] or {n=0,board=0}
			b.n=b.n+1;if c.owner~='native' then b.board=b.board+1 end
			out.by_id[key]=b
		elseif edgedFloor(g) then
			local who=owner(m,x,y,g)
			out.edged.n=out.edged.n+1
			if who~='native' then out.edged.board=out.edged.board+1 end
			if Terrain.visible(m,x,y) then out.edged.visible=out.edged.visible+1 end
			if not out.edged.sample then out.edged.sample={x,y} end
		end
	end end
	return out
end
-- One cell's report (after a pose and a frame).
function M.s2cell(x,y)
	local m=game.level.map
	local g=m(x,y,Map.TERRAIN)
	return cell(m,x,y,g,game.zone.short_name,g.define_as or (relTunnel(g) and '<rel tunnel>') or tostring(g.name))
end
-- Re-enter until the level holds one of the wanted ids (random vault content).
function M.hunt(zone,level,ids,opts,tries)
	local want={}
	for _,id in ipairs(ids) do want[id]=true end
	local enter
	for i=1,tries or 6 do
		enter=tw.ms.enter(zone,level,opts)
		tw.ms.caveClearDialogs()
		local m=game.level.map
		for x=0,m.w-1 do for y=0,m.h-1 do
			local g=m(x,y,Map.TERRAIN)
			if g and (want[g.define_as] or want['<rel tunnel>'] and relTunnel(g) or want['<edged floor>'] and edgedFloor(g)) then
				enter.tries=i;enter.found={x,y,g.define_as or '<quick>'};return enter
			end
		end end
	end
	enter.tries=tries or 6;enter.found=false
	return enter
end
-- A native NicerTiles re-tile of the cell's surroundings (the path a door
-- opening or dig takes), then the display repair; rules must be unchanged.
function M.open(x,y)
	local m=game.level.map
	local g=m(x,y,Map.TERRAIN)
	local before=g.define_as
	local target=g.door_opened and game.zone.grid_list[g.door_opened]
	if not target then return {opened=false,id=before} end
	m(x,y,Map.TERRAIN,target:clone())
	if game.nicer_tiles then game.nicer_tiles:updateAround(game.level,x,y) end
	if game.checkerRepairTerrain then game:checkerRepairTerrain(x-1,y-1,x+1,y+1) end
	m:updateMap(x,y);m.changed=true
	return {opened=true,before=before,after=m(x,y,Map.TERRAIN).define_as}
end
return M
