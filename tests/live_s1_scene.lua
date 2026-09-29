-- Offline fixture only (S1: native aura events in every covered family).
-- Poses the player next to an aura circle that crosses blocking cells,
-- reveals a local window for the screenshot, and reports ring coverage and
-- the rule digest. It never edits a grid rule field; staging only moves the
-- player and sets the map's seen/remembered flags (fixture-only).
local Map=require 'engine.Map'
local Terrain=require 'mod.class.CheckerTerrain'
local s3=dofile('/data-checker-fixture/monster-live_s3_scene.lua')
local ms=s3.ms
local M={ms=ms,s3=s3,stage=s3.stage,rules=s3.rules}

local function forestOwned(g)
	local s=g and g._checker_terrain
	return s and g.replace_display==s.display and true or false
end
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
-- Board ownership of one cell: forest adapter display or a stone record.
local function owned(m,x,y,g)
	if forestOwned(g) then return true,g.replace_display.image end
	local r=m._checker_korpul and m._checker_korpul[x+y*m.w]
	if r then return true,'stone:'..r.kind end
	return false
end
-- Aura cells as the native events left them (exact event file and line).
local function ring(g)
	return g and g.on_stand and Terrain.ringEvent(g.on_stand)
end
local function blocking(g) return g.does_block_move or g.block_sight or g.is_door end

function M.counts()
	local m=game.level.map
	observeAll()
	local out={ring=0,ring_owned=0,ring_blocking=0,ring_blocking_owned=0,centres=0,centres_owned=0,native_ring={},events={}}
	for x=0,m.w-1 do for y=0,m.h-1 do
		local g=m(x,y,Map.TERRAIN)
		local ev=ring(g)
		if ev then
			local own=owned(m,x,y,g)
			out.ring=out.ring+1;out.events[ev]=(out.events[ev] or 0)+1
			if own then out.ring_owned=out.ring_owned+1 end
			if blocking(g) then
				out.ring_blocking=out.ring_blocking+1
				if own then out.ring_blocking_owned=out.ring_blocking_owned+1 end
			end
			if select(3,Terrain.auraCentre(g)) then
				out.centres=out.centres+1
				if own then out.centres_owned=out.centres_owned+1 end
			end
			if not own then
				local k=tostring(g.define_as)..'|'..tostring(g.name)
				out.native_ring[k]=(out.native_ring[k] or 0)+1
			end
		end
	end end
	return out
end

-- Centre of the densest aura window with blocking ring cells.
function M.pose()
	local m,p=game.level.map,game.player
	observeAll()
	local best
	for x=10,m.w-11 do for y=7,m.h-8 do
		local floors,walls=0,0
		for dx=-4,4 do for dy=-4,4 do
			local g=m(x+dx,y+dy,Map.TERRAIN)
			if ring(g) then if blocking(g) then walls=walls+1 else floors=floors+1 end end
		end end
		local score=floors+walls*3
		if walls>0 and floors>0 and (not best or score>best.score) then best={x=x,y=y,score=score,ring_floors=floors,ring_blocking=walls} end
	end end
	if not best then return {found=false} end
	local stand
	for r=2,8 do
		for dx=-r,r do for dy=-r,r do
			local nx,ny=best.x+dx,best.y+dy
			local g=m(nx,ny,Map.TERRAIN)
			if not stand and g and not ring(g) and not g.does_block_move and not g.change_level and not g.change_zone and not m(nx,ny,Map.ACTOR) then stand={nx,ny} end
		end end
		if stand then break end
	end
	stand=stand or {best.x,best.y}
	local moved=0
	for _,a in pairs(game.level.entities) do
		if a~=p and a.x and math.abs(a.x-best.x)<=12 and math.abs(a.y-best.y)<=9 then
			game.level:removeEntity(a,true);moved=moved+1
		end
	end
	p:move(stand[1],stand[2],true);p.sight=20
	best.found=true;best.stand=stand;best.removed_actors=moved
	ms.focus(best.x,best.y)
	return best
end

-- Screen sample cells: ring floor / ring blocking / non-ring floor / wall.
function M.samples()
	local m=game.level.map
	local size=m.tile_w*m.zoom
	local out={tile=size,cells={}}
	for x=0,m.w-1 do for y=0,m.h-1 do
		local g=m(x,y,Map.TERRAIN)
		if g and m.seens(x,y) and not m(x,y,Map.ACTOR) and not m(x,y,Map.OBJECT) and owned(m,x,y,g) then
			local sx,sy=m:getTileToScreen(x,y)
			if sx>=m.display_x+size and sy>=m.display_y+size and sx+2*size<=m.display_x+m.viewport.width and sy+2*size<=m.display_y+m.viewport.height then
				local f=(ring(g) and 'ring-' or '')..(blocking(g) and 'blocking' or 'floor')
				out.cells[#out.cells+1]={x=x,y=y,sx=sx,sy=sy,family=f}
			end
		end
	end end
	return out
end
return M
