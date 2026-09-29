-- Offline fixture only (S4/T1 air bubbles, T16 callback altars). Reuses the
-- S2 scene module (poses, rule digest, particle pause, cell owner report) and
-- adds a per-level bubble/altar report and the native bubble consumption:
-- Actor:act's own call, map:checkEntity(x,y,TERRAIN,'on_stand',who), repeated
-- until the native on_stand swaps in WATER_FLOOR. Never edits a rule field;
-- nb_charges only changes through the native callback.
local Map=require 'engine.Map'
local Terrain=require 'mod.class.CheckerTerrain'
local tw=dofile('/data-checker-fixture/monster-live_s2_scene.lua')
local M=setmetatable({},{__index=tw})

local function fnInfo(f)
	if type(f)~='function' then return false end
	local i=debug.getinfo(f,'S');return tostring(i and i.source)..':'..tostring(i and i.linedefined)
end
local function owner(g)
	local st=g._checker_terrain
	if st and g.replace_display==st.display then return 'board',g.replace_display end
	return 'native'
end
local function report(m,x,y)
	local g=m(x,y,Map.TERRAIN)
	local who,d=owner(g)
	local layer=d and d.add_displays and d.add_displays[#d.add_displays]
	return {x=x,y=y,id=g.define_as or false,owner=who,image=d and d.image or false,prop=layer and layer.image or false,
		kind=Terrain.underwaterKind(g) or Terrain.batch4Kind(g,game.zone.short_name=='noxious-caldera' and 'caldera' or game.zone.short_name) or false,
		charges=g.nb_charges or false,air_level=g.air_level or false,air_condition=g.air_condition or false,
		on_stand=fnInfo(g.on_stand),on_move=fnInfo(rawget(g,'on_move')),block_move=fnInfo(rawget(g,'block_move')),
		does_block_move=g.does_block_move and true or false,block_sight=g.block_sight and true or false,
		s2_stamp=g._checker_s2_source and g._checker_s2_source.file or false,visible=Terrain.visible(m,x,y),
		remembered=m.remembers(x,y) and true or false}
end
M.report=function(x,y) return report(game.level.map,x,y) end
local ALTARS={ALTAR_CORRUPT='mark-spellblaze',ALTAR='noxious-caldera'}
-- Every bubble and reviewed altar of the level.
function M.s4cells()
	local m=game.level.map
	local out={zone=game.zone.short_name,level=game.level.level,flooded=game.zone.is_flooded and true or false,
		bubbles={n=0,board=0,exact=0,sample={}},altars={}}
	for x=0,m.w-1 do for y=0,m.h-1 do
		local g=m(x,y,Map.TERRAIN)
		if g and g.define_as=='WATER_FLOOR_BUBBLE' then
			local b=out.bubbles
			b.n=b.n+1
			if owner(g)=='board' then b.board=b.board+1 end
			if Terrain.underwaterKind(g)=='bubble' then b.exact=b.exact+1 end
			if #b.sample<3 then b.sample[#b.sample+1]=report(m,x,y) end
		elseif g and ALTARS[g.define_as]==game.zone.short_name then
			out.altars[#out.altars+1]=report(m,x,y)
		end
	end end
	return out
end
-- A bubble with a free, non-bubble floor neighbour for the player to stand
-- on (the token must not cover the bubble), away from the map edge.
function M.pickBubble(skip)
	local m=game.level.map
	skip=skip or {}
	-- Prefer a bubble the view can centre on (away from the map edge).
	for _,edge in ipairs{{12,8},{3,3}} do
	for x=edge[1],m.w-1-edge[1] do for y=edge[2],m.h-1-edge[2] do
		local g=m(x,y,Map.TERRAIN)
		if g and g.define_as=='WATER_FLOOR_BUBBLE' and not skip[x..','..y] and not m(x,y,Map.ACTOR) then
			for _,d in ipairs{{0,1},{1,0},{-1,0},{0,-1}} do
				local n=m(x+d[1],y+d[2],Map.TERRAIN)
				if n and Terrain.underwaterKind(n)=='floor' and not m(x+d[1],y+d[2],Map.ACTOR) then
					return {x=x,y=y,sx=x+d[1],sy=y+d[2]}
				end
			end
		end
	end end
	end
	return false
end
-- Native consumption: the exact call Actor:act makes each turn for the actor
-- standing on (x,y), with the player as `who` (a non-water-breather).
function M.consume(x,y)
	local m,p=game.level.map,game.player
	assert(not p:attr('no_breath') and not (p.can_breath.water and p.can_breath.water>0),'player breathes water')
	local g=m(x,y,Map.TERRAIN)
	local out={before=report(m,x,y),charges={g.nb_charges},calls=0}
	for i=1,12 do
		m:checkEntity(x,y,Map.TERRAIN,'on_stand',p)
		out.calls=i
		local now=m(x,y,Map.TERRAIN)
		if now~=g then break end
		out.charges[#out.charges+1]=g.nb_charges
	end
	m:redisplay();m.changed=true;core.display.forceRedraw()
	out.after=report(m,x,y)
	out.neighbours={}
	for dx=-1,1 do for dy=-1,1 do if dx~=0 or dy~=0 then
		local r=report(m,x+dx,y+dy);out.neighbours[#out.neighbours+1]={r.id,r.owner,r.image}
	end end end
	return out
end
return M
