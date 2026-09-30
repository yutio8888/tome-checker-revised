-- Offline fixture only (S12: damaging lava floor T19, Vor Armoury deep water
-- T20). Reuses the S11 scene module (cell dump, poses, quieting, rule digest,
-- screen rectangles) and adds: a forced-vault entry (fixture-only generator
-- probe: the level's greater-vault room list is pinned before generation, the
-- same technique as live_map_survey's force_crystal_vault), a per-level dump
-- of every lava / deep-water cell with its S12 kind and owner, the native
-- on_stand call (Actor.lua:759, exactly as Actor:act runs it) for a standing
-- actor, and window pickers for the photographs. Never edits a grid rule
-- field; the only terrain-side effect is the native on_stand's own.
local Map=require 'engine.Map'
local Terrain=require 'mod.class.CheckerTerrain'
local Zone=require 'mod.class.Zone'
local tw=dofile('/data-checker-fixture/monster-live_s11_scene.lua')
local M=setmetatable({},{__index=tw})

-- Enter a level whose generator gets the given greater-vault room list
-- (fixture only; the zone table is built by the native Zone.new, then only
-- its generator.map.rooms / greater_vaults_list are pinned).
function M.enterForced(short,level,vaults,rooms)
	local new=Zone.new
	Zone.new=function(name,...)
		local z=new(name,...)
		if name==short and type(z)=='table' and z.generator and z.generator.map then
			z.generator.map.rooms=rooms or {{'greater_vault',100},'random_room'}
			z.generator.map.greater_vaults_list=vaults
		end
		return z
	end
	local ok,res=pcall(tw.ms.enter,short,level)
	Zone.new=new
	assert(ok,res)
	return res
end

local function isS12(g)
	if not g then return false end
	local id=type(g.define_as)=='string' and g.define_as or ''
	return id:match('^LAVA') or id:match('DEEP_WATER') or g.subtype=='lava' or g.subtype=='molten_lava' or g.subtype=='water'
end
function M.kind(g)
	return Terrain.s12Kind and g and Terrain.s12Kind(g,game.zone.short_name) or false
end
-- Every lava / water cell of the level (full dump) and an id histogram.
function M.s12cells(full)
	local m=game.level.map
	local out={zone=game.zone.short_name,level=game.level.level,cells={},ids={}}
	for x=0,m.w-1 do for y=0,m.h-1 do
		local g=m(x,y,Map.TERRAIN)
		if isS12(g) then
			local c=tw.cell(x,y)
			c.s12=M.kind(g)
			local key=tostring(c.id)..'|'..c.funcs
			local e=out.ids[key] or {n=0,owner={},s12={}}
			e.n=e.n+1;e.owner[c.owner]=(e.owner[c.owner] or 0)+1
			e.s12[tostring(c.s12)]=(e.s12[tostring(c.s12)] or 0)+1
			out.ids[key]=e
			if full~=false then out.cells[#out.cells+1]=c else out.cells[#out.cells+1]={x=x,y=y,id=c.id,owner=c.owner,s12=c.s12,funcs=c.funcs} end
		end
	end end
	return out
end
-- The native terrain hook of Actor:act (Actor.lua:759) for the player on (x,y).
function M.stand(x,y)
	local m,p=game.level.map,game.player
	p:move(x,y,true)
	local before=tw.cell(x,y)
	local life=p.life
	m:checkEntity(p.x,p.y,Map.TERRAIN,'on_stand',p)
	return {x=x,y=y,player={p.x,p.y},life_before=life,life_after=p.life,before=before,after=tw.cell(x,y)}
end
-- The densest window of a kind: the cell of that S12 kind (or native id
-- pattern, for the before phase) with the most same-kind cells within 3,
-- that also has a floor and a wall within 3.
function M.pickWindow(pattern)
	local m=game.level.map
	local function match(g) return g and type(g.define_as)=='string' and g.define_as:match(pattern) end
	local best,score
	for x=1,m.w-2 do for y=1,m.h-2 do
		if match(m(x,y,Map.TERRAIN)) then
			local s,floor,wall=0,false,false
			for dx=-3,3 do for dy=-3,3 do
				local g=m(x+dx,y+dy,Map.TERRAIN)
				if match(g) then s=s+1
				elseif g and g.type=='floor' and not g.does_block_move then floor=true
				elseif g and g.does_block_move then wall=true end
			end end
			if floor and wall and (not score or s>score) then best,score={x,y},s end
		end
	end end
	return best and {x=best[1],y=best[2],score=score} or {x=false}
end
-- A free non-hazard floor cell orthogonally next to a cell matching pattern
-- (the player stands next to the hazard in the photographs).
function M.besideHazard(pattern,cx,cy)
	local m=game.level.map
	local function match(g) return g and type(g.define_as)=='string' and g.define_as:match(pattern) end
	for r=0,10 do
		for dx=-r,r do for dy=-r,r do
			local x,y=cx+dx,cy+dy
			if math.max(math.abs(dx),math.abs(dy))==r and x>=0 and y>=0 and x<m.w and y<m.h then
				local g=m(x,y,Map.TERRAIN)
				if g and not match(g) and g.type=='floor' and not m:checkAllEntities(x,y,'block_move') and not m(x,y,Map.ACTOR) then
					for _,d in ipairs{{0,-1},{1,0},{0,1},{-1,0}} do
						if match(m(x+d[1],y+d[2],Map.TERRAIN)) then return {x=x,y=y,hazard={x+d[1],y+d[2]}} end
					end
				end
			end
		end end
	end
	return {x=false}
end
-- Grey-level sample cells around a window: hazard lava, deep water, floor and
-- wall cells in FOV within 5 of (cx,cy), with their screen rectangles and the
-- owner/board file (the runner measures the frame).
function M.graySamples(cx,cy)
	local m=game.level.map
	local out={cells={}}
	for x=cx-5,cx+5 do for y=cy-5,cy+5 do
		local g=x>=0 and y>=0 and x<m.w and y<m.h and m(x,y,Map.TERRAIN)
		if g and Terrain.visible(m,x,y) then
			local id=type(g.define_as)=='string' and g.define_as or ''
			local fam=id:match('^LAVA_FLOOR') and 'lava' or id=='DEEP_WATER' and 'water' or
				(id=='FLOOR' or id:match('^FLOOR%d*$')) and 'floor' or (g.does_block_move and g.block_sight and g.type=='wall' and not g.is_door) and 'wall' or nil
			if fam then
				local s=tw.screen(x,y)
				local r=m._checker_korpul and m._checker_korpul[x+y*m.w]
				s.family=fam;s.id=id;s.file=r and r.painted and r.file or false
				out.cells[#out.cells+1]=s
			end
		end
	end end
	return out
end
-- Place the player on (x,y) (a teleport-free move, as poseAt) and clear
-- nearby actors; the view is not refreshed here.
function M.placePlayer(x,y,cx,cy)
	local r=tw.poseAt(cx or x,cy or y,x,y,'s12')
	return r
end
return M
