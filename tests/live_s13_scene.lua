-- Offline fixture only (S13: Ardhungol's unstable wormhole T2 and exact
-- DEEP_WATER in further stone zones). Reuses the S12 scene module (forced
-- vault entry, cell dump, poses, quieting, rule digest, screen rectangles,
-- window pickers) and adds: a dump of every WORMHOLE / water cell with its
-- owner, S12/S13 kind and the grid's own particle emitters (definition,
-- radius, args, alive, whether the grid's current map object carries them),
-- a fixture-only hide/restore of the wormholes' particle emitters around a
-- pixel comparison (display only: the emitters are put back by position), and
-- grey samples that know cave floors. Never edits a grid rule field.
local Map=require 'engine.Map'
local Terrain=require 'mod.class.CheckerTerrain'
local tw=dofile('/data-checker-fixture/monster-live_s12_scene.lua')
local M=setmetatable({},{__index=tw})

local function isS13(g)
	if not g then return false end
	local id=type(g.define_as)=='string' and g.define_as or ''
	return id=='WORMHOLE' or id:match('DEEP_WATER') or g.subtype=='water'
end
function M.kind(g)
	if not g then return false end
	local z=game.zone.short_name
	return Terrain.s13Kind and Terrain.s13Kind(g,z) or Terrain.s12Kind and Terrain.s12Kind(g,z) or false
end
local function particles(g)
	local out={}
	for p in pairs(rawget(g,'__particles') or {}) do
		local args={}
		for k,v in pairs(p.args or {}) do args[#args+1]=tostring(k)..'='..tostring(v) end
		table.sort(args)
		out[#out+1]={def=tostring(p.def),radius=p.radius,args=table.concat(args,','),shader=p.shader and true or false,
			toback=p.toback and true or false,alive=p.ps and p.ps:isAlive() and true or false}
	end
	return out
end
-- Every wormhole / water cell of the level (full dump) and an id histogram.
function M.s13cells(full)
	local m=game.level.map
	local out={zone=game.zone.short_name,level=game.level.level,cells={},ids={}}
	for x=0,m.w-1 do for y=0,m.h-1 do
		local g=m(x,y,Map.TERRAIN)
		if isS13(g) then
			local c=tw.cell(x,y)
			c.s13=M.kind(g)
			c.ps=particles(g)
			c.mo=rawget(g,'_mo') and true or false
			c.replaced=g.replace_display and true or false
			local key=tostring(c.id)..'|'..c.funcs
			local e=out.ids[key] or {n=0,owner={},kind={},ps=0}
			e.n=e.n+1;e.owner[c.owner]=(e.owner[c.owner] or 0)+1
			e.kind[tostring(c.s13)]=(e.kind[tostring(c.s13)] or 0)+1
			e.ps=e.ps+#c.ps
			out.ids[key]=e
			if full~=false then out.cells[#out.cells+1]=c else
				out.cells[#out.cells+1]={x=x,y=y,id=c.id,owner=c.owner,s13=c.s13,funcs=c.funcs,ps=#c.ps,board=c.board}
			end
		end
	end end
	return out
end
-- Fixture only, display only: silence the wormholes' own emitters (on=false)
-- and bring them back (on=true), so a Refined -> Native -> Refined
-- comparison is not a comparison of a spinning particle. The emitter objects
-- stay on their grids (the S13 contract checks them); only their native
-- particle system handle is swapped for a silent stand-in that draws
-- nothing, and put back afterwards. Emitters are shared by the grid's clones,
-- so a mode switch in between keeps the same objects.
local silent={isAlive=function() return true end,toScreen=function() end,die=function() end,shift=function() end}
local hidden
function M.wormholes(on)
	local m=game.level.map
	if not on then
		hidden={}
		for x=0,m.w-1 do for y=0,m.h-1 do
			local g=m(x,y,Map.TERRAIN)
			if g and g.define_as=='WORMHOLE' then
				for p in pairs(rawget(g,'__particles') or {}) do
					if p.ps~=silent then hidden[#hidden+1]={p,p.ps};p.ps=silent end
				end
			end
		end end
		return {hidden=#hidden}
	end
	local n=0
	for _,h in ipairs(hidden or {}) do if h[1].ps==silent then h[1].ps=h[2];n=n+1 end end
	hidden=nil
	return {restored=n}
end
-- Screen rectangles of every wormhole cell (masked frame comparisons).
function M.wormRects()
	local m=game.level.map
	local out={}
	for x=0,m.w-1 do for y=0,m.h-1 do
		local g=m(x,y,Map.TERRAIN)
		if g and g.define_as=='WORMHOLE' then out[#out+1]=tw.screen(x,y) end
	end end
	return out
end
-- The densest wormhole window with a plain cave floor and a wall within 3.
function M.pickWorm()
	return tw.pickWindow('^WORMHOLE$')
end
-- Grey samples around (cx,cy): wormholes, deep water, floors (stone or cave)
-- and walls in FOV within 5.
function M.graySamples(cx,cy)
	local m=game.level.map
	local out={cells={}}
	for x=cx-5,cx+5 do for y=cy-5,cy+5 do
		local g=x>=0 and y>=0 and x<m.w and y<m.h and m(x,y,Map.TERRAIN)
		if g and Terrain.visible(m,x,y) then
			local id=type(g.define_as)=='string' and g.define_as or ''
			local fam=id=='WORMHOLE' and 'wormhole' or id=='DEEP_WATER' and 'water' or
				(id=='FLOOR' or id:match('^FLOOR%d*$') or id=='CAVEFLOOR' or id:match('^CAVEFLOOR%d+$')) and 'floor' or
				(g.does_block_move and g.block_sight and g.type=='wall' and not g.is_door) and 'wall' or nil
			if fam then
				local s=tw.screen(x,y)
				local r=m._checker_korpul and m._checker_korpul[x+y*m.w]
				local st=rawget(g,'_checker_terrain')
				s.family=fam;s.id=id
				s.file=st and g.replace_display==st.display and st.display.image or r and r.painted and r.file or false
				out.cells[#out.cells+1]=s
			end
		end
	end end
	return out
end
-- Forced vault entry with a chosen list key (greater_vaults_list or
-- lesser_vaults_list) and ms.enter options (fixture-only generator probe, as
-- tw.enterForced: the zone table comes from the native Zone.new).
local Zone=require 'mod.class.Zone'
function M.enterList(short,level,key,list,rooms,opts)
	local new=Zone.new
	Zone.new=function(name,...)
		local z=new(name,...)
		if name==short and type(z)=='table' and z.generator and z.generator.map then
			z.generator.map.rooms=rooms
			z.generator.map[key]=list
		end
		return z
	end
	local ok,res=pcall(tw.ms.enter,short,level,opts)
	Zone.new=new
	assert(ok,res)
	return res
end
return M
