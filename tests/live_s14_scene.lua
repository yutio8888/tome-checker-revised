-- Offline fixture only (S14: portal / farportal bridge, High Peak invocation
-- portals and the Sanctum portal). Reuses the S13 scene module (forced list
-- entry, poses, quieting, rule digest, screen rectangles, the S11 per-cell
-- dump with callbacks file:line, stamps and owner) and adds:
-- * a dump of every portal-like cell (define_as containing PORTAL, ORB_*,
--   any orb_portal / orb_command) with its S14 kind, the stone classify
--   result and the per-field comparison against its S14 definition stamp;
-- * staged native placements for quest-made portals: the exact addEntity
--   sequence of the native quest code (east-portal create_portal,
--   west-portal create_portal, east-portal tannen_exit, charred-scar
--   on_win, the Draebor on_die), fixture only, without the quest state
--   changes around them;
-- * the native invocation-portal shutdown (Player:useCommandOrb's call
--   g.orb_command:special(player, g), high-peak/grids.lua:113-128) on one
--   ORB_* cell after granting the high-peak quest in the fixture;
-- * the map particle emitters that sit on portal cells.
-- Never edits a grid rule field; the shutdown changes only what its native
-- callback changes.
local Map=require 'engine.Map'
local Terrain=require 'mod.class.CheckerTerrain'
local tw=dofile('/data-checker-fixture/monster-live_s13_scene.lua')
local M=setmetatable({},{__index=tw})

local function portalLike(g)
	if not g then return false end
	local id=type(g.define_as)=='string' and g.define_as or ''
	return id:match('PORTAL') or id:match('^ORB_') or g.orb_portal~=nil or g.orb_command~=nil
end
M.portalLike=portalLike
function M.kind(g)
	if not g then return false end
	local z=game.zone.short_name
	return Terrain.s14Kind and Terrain.s14Kind(g,z) or false
end
-- Map particle emitters whose origin is (x,y).
local function mapParticles(x,y)
	local out={}
	for _,e in ipairs(game.level.map.particles or {}) do
		if e.x==x and e.y==y then out[#out+1]=tostring(e.def)..'@'..tostring(e.radius) end
	end
	table.sort(out)
	return out
end
function M.s14cells(full)
	local m=game.level.map
	local out={zone=game.zone.short_name,level=game.level.level,cells={},ids={}}
	for x=0,m.w-1 do for y=0,m.h-1 do
		local g=m(x,y,Map.TERRAIN)
		if portalLike(g) then
			local c=tw.cell(x,y)
			c.s14=M.kind(g)
			c.s14why=Terrain.s14Why and Terrain.s14Why(g,game.zone.short_name) or false
			c.map_ps=mapParticles(x,y)
			local key=tostring(c.id)..'|'..c.funcs
			local e=out.ids[key] or {n=0,owner={},kind={},why={}}
			e.n=e.n+1;e.owner[c.owner]=(e.owner[c.owner] or 0)+1
			e.kind[tostring(c.s14)]=(e.kind[tostring(c.s14)] or 0)+1
			e.why[tostring(c.s14why)]=(e.why[tostring(c.s14why)] or 0)+1
			out.ids[key]=e
			if full~=false then out.cells[#out.cells+1]=c else
				out.cells[#out.cells+1]={x=x,y=y,id=c.id,owner=c.owner,s14=c.s14,why=c.s14why,funcs=c.funcs,map_ps=c.map_ps}
			end
		end
	end end
	return out
end
-- Staged native placements (fixture only). Each follows its quest's own
-- makeEntityByName / addEntity lines; no quest status, NPC or dialog.
local function put(id,cells,typ)
	local g=game.zone:makeEntityByName(game.level,typ or 'terrain',id)
	assert(g,id)
	for _,c in ipairs(cells) do game.zone:addEntity(game.level,g,typ or 'terrain',c[1],c[2]) end
	return g
end
local function ring(x,y,portal,centre)
	-- quests/east-portal.lua:75-86 and west-portal.lua:74-111 (same order).
	local g1=game.zone:makeEntityByName(game.level,'terrain',portal)
	local g2=game.zone:makeEntityByName(game.level,'terrain',centre)
	assert(g1 and g2,portal)
	for _,c in ipairs{{0,0},{1,0},{2,0},{0,1}} do game.zone:addEntity(game.level,g1,'terrain',x+c[1],y+c[2]) end
	game.zone:addEntity(game.level,g2,'terrain',x+1,y+1)
	for _,c in ipairs{{2,1},{0,2},{1,2},{2,2}} do game.zone:addEntity(game.level,g1,'terrain',x+c[1],y+c[2]) end
	return {x=x+1,y=y+1}
end
function M.stage(what)
	local l=game.level
	if what=='last-hope' then
		local s=l:pickSpot{type='pop-quest',subtype='farportal'}
		return ring(s.x,s.y,'FAR_EAST_PORTAL','CFAR_EAST_PORTAL')
	elseif what=='gates' then
		local s=l:pickSpot{type='pop-quest',subtype='farportal'}
		return ring(s.x,s.y,'WEST_PORTAL','CWEST_PORTAL')
	elseif what=='tannen' then
		-- quests/east-portal.lua:155-159 (tannen_exit).
		put('PORTAL_BACK',{{12,12}})
		return {x=12,y=12}
	elseif what=='charred' then
		-- quests/charred-scar.lua:56-66 (same cells; nicer_tiles passes as there).
		local portal=game.zone:makeEntityByName(l,'grid','FAR_EAST_PORTAL')
		for _,c in ipairs{{5,455,5,455},{6,455,6,455},{7,455,7,455},{5,454,6,454},{7,454,7,454},{5,453,5,453},{6,453,6,453},{7,453,7,453}} do
			game.zone:addEntity(l,portal,'grid',c[1],c[2]);game.nicer_tiles:updateAround(l,c[3],c[4])
		end
		local cp=game.zone:makeEntityByName(l,'grid','CFAR_EAST_PORTAL')
		game.zone:addEntity(l,cp,'grid',6,454)
		return {x=6,y=454}
	elseif what=='demon' then
		-- zones/demon-plane/npcs.lua:81-89 (Draebor's on_die) at a free floor
		-- cell near the player.
		local p=game.player
		local x,y=util.findFreeGrid(p.x+3,p.y,10,true,{[Map.ACTOR]=true})
		assert(x,'no free cell')
		put('PORTAL_BACK',{{x,y}})
		return {x=x,y=y}
	end
	error('unknown stage '..tostring(what))
end
-- The native shutdown of one invocation portal: Player:useCommandOrb runs
-- g.orb_command:special(player, g) (class/Player.lua:1674-1676); the callback
-- (high-peak/grids.lua invocation_close) needs the high-peak quest.
function M.closeOrb(x,y)
	local m,p=game.level.map,game.player
	local g=m(x,y,Map.TERRAIN)
	assert(g and g.orb_command,'no invocation portal at '..x..','..y)
	if not p:hasQuest('high-peak') then p:grantQuest('high-peak') end
	local before=tw.cell(x,y)
	g.orb_command:special(p,g)
	return {x=x,y=y,before=before,after=tw.cell(x,y),s14_after=M.kind(m(x,y,Map.TERRAIN)),
		why_after=Terrain.s14Why and Terrain.s14Why(m(x,y,Map.TERRAIN),game.zone.short_name) or false}
end
-- First cell of an id (for windows).
function M.find(id)
	local m=game.level.map
	for x=0,m.w-1 do for y=0,m.h-1 do
		local g=m(x,y,Map.TERRAIN)
		if g and g.define_as==id then return {x=x,y=y} end
	end end
	return {x=false}
end
-- Screen rectangles of every portal-like cell (masked frame comparisons).
function M.portalRects()
	local m=game.level.map
	local out={}
	for x=0,m.w-1 do for y=0,m.h-1 do
		if portalLike(m(x,y,Map.TERRAIN)) then out[#out+1]=tw.screen(x,y) end
	end end
	return out
end
-- Grey samples around (cx,cy): portal cells, plain floors and walls in FOV.
function M.graySamples(cx,cy)
	local m=game.level.map
	local out={cells={}}
	for x=cx-5,cx+5 do for y=cy-5,cy+5 do
		local g=x>=0 and y>=0 and x<m.w and y<m.h and m(x,y,Map.TERRAIN)
		if g and Terrain.visible(m,x,y) then
			local id=type(g.define_as)=='string' and g.define_as or ''
			local fam=portalLike(g) and 'portal' or (id=='FLOOR' or id:match('^FLOOR%d*$') or id=='SOLID_FLOOR') and 'floor' or
				(g.does_block_move and g.block_sight and g.type=='wall' and not g.is_door) and 'wall' or nil
			if fam then
				local s=tw.screen(x,y)
				s.family=fam;s.id=id
				out.cells[#out.cells+1]=s
			end
		end
	end end
	return out
end
return M
