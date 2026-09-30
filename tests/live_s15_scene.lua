-- Offline fixture only (S15: tutorial L1 forest and dreams L1 jungle maze).
-- Reuses the S13 scene module (enter, cell dump, poses, quieting, rule
-- digest, screen rectangles, particle pause) and adds: an id histogram with
-- the S15 kind and whether the board display is installed, a deterministic
-- window picker, and grey samples by board family. Never edits a grid rule
-- field.
local Map=require 'engine.Map'
local Terrain=require 'mod.class.CheckerTerrain'
local tw=dofile('/data-checker-fixture/monster-live_s13_scene.lua')
local M=setmetatable({},{__index=tw})

local function id(g) return g and (type(g.define_as)=='string' and g.define_as or '<'..tostring(g.name)..'>') or '<none>' end
local function family(i)
	return (i:match('^TREE') or i:match('^JUNGLE_TREE')) and 'tree' or i:match('DEEP_WATER') and 'water' or
		(i:match('^GRASS') or i:match('^JUNGLE_GRASS')) and 'floor' or nil
end
-- Every cell: id -> {n, s15 kind histogram, board display installed}.
function M.s15cells()
	local m=game.level.map
	local z=game.zone.short_name
	local out={zone=z,level=game.level.level,ids={}}
	for x=0,m.w-1 do for y=0,m.h-1 do
		local g=m(x,y,Map.TERRAIN)
		local e=out.ids[id(g)] or {n=0,kind={},board=0}
		e.n=e.n+1
		local k=g and Terrain.s15Kind and Terrain.s15Kind(g,z) or false
		e.kind[tostring(k)]=(e.kind[tostring(k)] or 0)+1
		local st=g and g._checker_terrain
		if st and g.replace_display==st.display then e.board=e.board+1 end
		out.ids[id(g)]=e
	end end
	return out
end
-- First cell (scan order) with id pattern `a` that has an 8-neighbour with id
-- pattern `b`, optionally inside a rectangle.
function M.pick(a,b,x1,y1,x2,y2)
	local m=game.level.map
	x1,y1,x2,y2=x1 or 0,y1 or 0,x2 or m.w-1,y2 or m.h-1
	for y=y1,y2 do for x=x1,x2 do
		if id(m(x,y,Map.TERRAIN)):match(a) then
			if not b then return {x=x,y=y} end
			for dx=-1,1 do for dy=-1,1 do
				local nx,ny=x+dx,y+dy
				if (dx~=0 or dy~=0) and nx>=0 and ny>=0 and nx<m.w and ny<m.h and id(m(nx,ny,Map.TERRAIN)):match(b) then return {x=x,y=y} end
			end end
		end
	end end
	return {x=false}
end
function M.graySamples(cx,cy)
	local m=game.level.map
	local out={cells={}}
	for x=cx-5,cx+5 do for y=cy-5,cy+5 do
		local g=x>=0 and y>=0 and x<m.w and y<m.h and m(x,y,Map.TERRAIN)
		local f=g and Terrain.visible(m,x,y) and family(id(g))
		if f then
			local s=tw.screen(x,y)
			s.family=f;s.id=id(g)
			out.cells[#out.cells+1]=s
		end
	end end
	return out
end
-- Fixture only: enter a zone with its zone-level on_enter removed from the
-- native Zone.new table (dreams' on_enter only swaps control to a dream
-- avatar, which the fixture's hero guard rejects; it never edits terrain).
-- Generation, post_process (the mouse holes) and the grids are untouched.
local Zone=require 'mod.class.Zone'
function M.enterQuiet(short,level)
	local new=Zone.new
	Zone.new=function(name,...)
		local z=new(name,...)
		if name==short and type(z)=='table' then z.on_enter=nil end
		return z
	end
	local ok,res=pcall(tw.ms.enter,short,level)
	Zone.new=new
	assert(ok,res)
	return res
end
function M.player() local p=game.player;return {x=p.x,y=p.y,name=p.name,zone=game.zone.short_name,level=game.level.level} end
return M
