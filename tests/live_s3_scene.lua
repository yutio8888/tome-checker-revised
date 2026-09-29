-- Offline fixture only (S3: Old Forest crystal patches, forest-zone stone
-- rooms, LAKE_NUR exit). Poses the player, reveals a local window for the
-- screenshot, and reports rule digests / per-family pixel sample cells. It
-- never edits a grid rule field; staging only moves the player and sets the
-- map's seen/remembered flags (fixture-only, like ms.reuseStageView).
local Map=require 'engine.Map'
local Terrain=require 'mod.class.CheckerTerrain'
local ms=dofile('/data-checker-fixture/monster-live_map_survey.lua')
local M={ms=ms}

local function forestOwned(g)
	local s=g and g._checker_terrain
	return s and g.replace_display==s.display and true or false
end
local function stoneKind(m,x,y)
	local r=m._checker_korpul and m._checker_korpul[x+y*m.w]
	return r and r.kind
end
-- Family of a cell as the board draws it; nil = native.
local function family(m,x,y)
	local g=m(x,y,Map.TERRAIN)
	if not g then return end
	if forestOwned(g) then
		local img=g.replace_display.image or ''
		if img:match('/crystal/wall') then return 'crystal-wall' end
		if img:match('/crystal/floor') then return 'crystal-floor' end
		if img:match('/tree') then return 'tree' end
		if img:match('/grass') or img:match('/flower') or img:match('/road') then return 'grass' end
		if img:match('/exit') then return 'exit' end
		return 'forest-other'
	end
	local k=stoneKind(m,x,y)
	if k=='floor' then return 'stone-floor' end
	if k=='wall' or k=='hardwall' then return 'stone-wall' end
	if k and k:match('^door') then return 'stone-door' end
	if k then return 'stone-'..k end
end
M.family=family

-- Fill stone records for the whole level (same forced observe pass as the
-- census) so the pose search can see room cells before they are in FOV.
local function observeAll()
	local m=game.level.map
	if not Terrain.variant(game.zone) then return end
	local real=Terrain.visible
	Terrain.visible=function() return true end
	local ok,err=pcall(function()
		for x=0,m.w-1 do for y=0,m.h-1 do Terrain.observe(m,x,y,m(x,y,Map.TERRAIN)) end end
	end)
	Terrain.visible=real
	assert(ok,err)
end

function M.pose(kind)
	local m,p=game.level.map,game.player
	observeAll()
	local want=kind=='crystal' and {'crystal-wall','crystal-floor'} or kind=='exit' and {'exit'} or {'stone-wall','stone-floor'}
	local best
	if kind=='exit' then
		for x=0,m.w-1 do for y=0,m.h-1 do
			local g=m(x,y,Map.TERRAIN)
			if g and g.define_as=='LAKE_NUR' then best={x=x,y=y,score=1,counts={exit=1},exit={x,y}} end
		end end
		if not best then return {found=false,kind=kind} end
	end
	for x=10,m.w-11 do for y=7,m.h-8 do
		if kind=='exit' then break end
		local counts={}
		for dx=-7,7 do for dy=-5,5 do
			local f=family(m,x+dx,y+dy)
			if f then counts[f]=(counts[f] or 0)+1 end
		end end
		local own=0;for _,f in ipairs(want) do own=own+math.min(counts[f] or 0,40) end
		local forest=math.min((counts.grass or 0),40)+math.min((counts.tree or 0),30)
		local score=own*2+forest+(kind=='crystal' and math.min(counts['crystal-wall'] or 0,20)*3 or math.min(counts['stone-wall'] or 0,20)*2)
		if kind=='exit' then
			local g=m(x,y,Map.TERRAIN)
			score=(g and g.define_as=='LAKE_NUR') and 10000+forest or -1
		end
		if own>0 and forest>0 and (not best or score>best.score) then best={x=x,y=y,score=score,counts=counts} end
	end end
	if not best then return {found=false,kind=kind} end
	-- Stand on the nearest passable, actor-free cell to the chosen centre.
	local stand
	for r=0,6 do
		for dx=-r,r do for dy=-r,r do
			local nx,ny=best.x+dx,best.y+dy
			local g=m(nx,ny,Map.TERRAIN)
			if not stand and g and not g.does_block_move and not g.change_level and not g.change_zone and not m(nx,ny,Map.ACTOR) then stand={nx,ny} end
		end end
		if stand then break end
	end
	assert(stand,'no stand cell')
	-- Keep the photographed window free of creatures (fixture staging only).
	local moved=0
	for _,a in pairs(game.level.entities) do
		if a~=p and a.x and math.abs(a.x-best.x)<=12 and math.abs(a.y-best.y)<=9 then
			game.level:removeEntity(a,true);moved=moved+1
		end
	end
	p:move(stand[1],stand[2],true);p.sight=20
	best.found=true;best.kind=kind;best.stand=stand;best.removed_actors=moved
	ms.focus(best.x,best.y)
	return best
end

function M.stage(cx,cy)
	local m=game.level.map
	for x=math.max(0,cx-17),math.min(m.w-1,cx+17) do for y=math.max(0,cy-12),math.min(m.h-1,cy+12) do
		m.seens(x,y,true);m.infovs(x,y,true);m.remembers(x,y,true)
	end end
	for x=math.max(0,cx-17),math.min(m.w-1,cx+17) do for y=math.max(0,cy-12),math.min(m.h-1,cy+12) do m:updateMap(x,y) end end
	m.smooth_scroll=0;m:centerViewAround(cx,cy);m:redisplay();m.changed=true;core.display.forceRedraw()
	return {fixture_only=true}
end

-- Sample cells per family inside the viewport, with screen coordinates, for
-- luminance comparison (tile centre 40% crop is taken on the Python side).
function M.samples()
	local m=game.level.map
	local size=m.tile_w*m.zoom
	local out={tile=size,cells={}}
	for x=0,m.w-1 do for y=0,m.h-1 do
		if m.seens(x,y) and not m(x,y,Map.ACTOR) and not m(x,y,Map.OBJECT) then
			local f=family(m,x,y)
			if f then
				local sx,sy=m:getTileToScreen(x,y)
				if sx>=m.display_x+size and sy>=m.display_y+size and sx+2*size<=m.display_x+m.viewport.width and sy+2*size<=m.display_y+m.viewport.height then
					out.cells[#out.cells+1]={x=x,y=y,sx=sx,sy=sy,family=f}
				end
			end
		end
	end end
	return out
end

-- Rule digest: every rule field the adapters must never touch.
local ruleKeys={'define_as','type','subtype','does_block_move','block_sight','block_sense','block_esp','air_level','dig','is_door',
	'door_opened','door_closed','change_level','change_zone','change_level_check','force_down','notice','always_remember','special','pass_projectile'}
local function fn(v)
	if type(v)~='function' then return tostring(v) end
	local i=debug.getinfo(v,'S');return 'fn@'..tostring(i and i.short_src)..':'..tostring(i and i.linedefined)
end
function M.rules()
	local m=game.level.map
	local parts,n={},0
	for x=0,m.w-1 do for y=0,m.h-1 do
		local g=m(x,y,Map.TERRAIN)
		if g then
			local row={}
			for _,k in ipairs(ruleKeys) do row[#row+1]=fn(g[k]) end
			local cp={};for k,v in pairs(g.can_pass or {}) do cp[#cp+1]=k..'='..tostring(v) end;table.sort(cp)
			row[#row+1]=table.concat(cp,',')
			for _,k in ipairs{'on_stand','on_move','block_move','on_dig','combatAttack'} do row[#row+1]=fn(rawget(g,k) or g[k]) end
			parts[#parts+1]=table.concat(row,'|');n=n+1
		end
	end end
	local s=table.concat(parts,'\n')
	local h=0
	for i=1,#s do h=(h*31+s:byte(i))%4294967296 end
	return {cells=n,hash=h,length=#s}
end

function M.counts()
	local m=game.level.map
	observeAll()
	local out={crystal_owned=0,crystal_native=0,stone_painted=0,stone_records=0,exit_owned=0,exit_native=0,forest_owned=0}
	for x=0,m.w-1 do for y=0,m.h-1 do
		local g=m(x,y,Map.TERRAIN)
		if g then
			if forestOwned(g) then out.forest_owned=out.forest_owned+1 end
			if g._checker_crystal_source and (g.define_as or ''):match('^CRYSTAL_') and not g.change_level then
				if forestOwned(g) then out.crystal_owned=out.crystal_owned+1 else out.crystal_native=out.crystal_native+1 end
			end
			if g.define_as=='LAKE_NUR' then
				if forestOwned(g) then out.exit_owned=out.exit_owned+1 else out.exit_native=out.exit_native+1 end
			end
			local r=m._checker_korpul and m._checker_korpul[x+y*m.w]
			if r then out.stone_records=out.stone_records+1;if r.painted then out.stone_painted=out.stone_painted+1 end end
		end
	end end
	return out
end
return M
