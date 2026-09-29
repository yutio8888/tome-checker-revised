-- Offline fixture only (TW2: Last Hope, Elvala). Reuses the TW1 scene module
-- (stats, poses, natural-FOV view, pixel samples, rule digest) and adds an
-- identity probe: every cell's grid id, adapter kind and native layer images,
-- so what stays native is listed with its reason. Never edits a rule field.
local Map=require 'engine.Map'
local Terrain=require 'mod.class.CheckerTerrain'
local tw=dofile('/data-checker-fixture/monster-live_tw1_scene.lua')
local M=setmetatable({},{__index=tw})

local function layers(g)
	local out={}
	for _,mo in ipairs(g.add_mos or {}) do out[#out+1]='mo:'..tostring(mo.image) end
	for _,d in ipairs(g.add_displays or {}) do
		out[#out+1]='d:'..tostring(d.image)..'@'..tostring(d.z)
		for _,mo in ipairs(d.add_mos or {}) do out[#out+1]='d.mo:'..tostring(mo.image) end
	end
	table.sort(out)
	return out
end
local function fnInfo(f)
	if type(f)~='function' then return nil end
	local i=debug.getinfo(f,'S');return tostring(i and i.source)..':'..tostring(i and i.linedefined)
end

-- Per-identity buckets of the whole level. `owner`: forest (batch4 display
-- installed), stone (stone record painted), or native.
function M.probe()
	local m=game.level.map
	local zoneName=game.zone.short_name
	local buckets,order={},{}
	local totals={cells=0,forest=0,stone_kind=0,stone_painted=0,native=0}
	for x=0,m.w-1 do for y=0,m.h-1 do
		local g=m(x,y,Map.TERRAIN)
		if g then
			totals.cells=totals.cells+1
			local fk=Terrain.batch4Kind(g,zoneName)
			local sk=Terrain.classify(g)
			local st=g._checker_terrain
			local owned=st and g.replace_display==st.display
			local r=m._checker_korpul and m._checker_korpul[x+y*m.w]
			local owner=owned and 'forest' or (r and r.painted and r.file) and 'stone' or 'native'
			if owner=='forest' then totals.forest=totals.forest+1 elseif owner=='stone' then totals.stone_painted=totals.stone_painted+1 else totals.native=totals.native+1 end
			if sk then totals.stone_kind=totals.stone_kind+1 end
			local ls=layers(g)
			local key=table.concat({tostring(g.define_as),tostring(g.name),tostring(fk),tostring(sk),owner,table.concat(ls,',')},'|')
			local b=buckets[key]
			if not b then
				b={id=g.define_as or false,name=g.name,image=g.image,forest_kind=fk or false,stone_kind=sk or false,owner=owner,layers=ls,n=0,
					sample={x,y},town_stamp=g._checker_town_source and g._checker_town_source.file or false,
					block_move=fnInfo(rawget(g,'block_move')),on_move=fnInfo(rawget(g,'on_move')),on_stand=fnInfo(g.on_stand),
					type=g.type,subtype=g.subtype,trap=false}
				buckets[key]=b;order[#order+1]=key
			end
			b.n=b.n+1
			local t=m(x,y,Map.TRAP)
			if t then b.trap=(b.trap or 0)+1 end
		end
	end end
	local out={zone=zoneName,totals=totals,buckets={}}
	table.sort(order,function(a,b) return buckets[a].n>buckets[b].n end)
	for _,k in ipairs(order) do out.buckets[#out.buckets+1]=buckets[k] end
	return out
end

-- Last Hope's inner island: centre on the lore statues/mountain ring (the
-- statues are map-file grids without define_as, found by their native layer),
-- stand on the nearest free cell south of it, clear actors from the window.
function M.posePlaza()
	local m,p=game.level.map,game.player
	local sx,sy,n=0,0,0
	for x=0,m.w-1 do for y=6,m.h-1 do
		local g=m(x,y,Map.TERRAIN)
		local d=g and g.add_displays and g.add_displays[1]
		if g and not g.define_as and d and type(d.image)=='string' and d.image:match('^terrain/statues/') then sx,sy,n=sx+x,sy+y,n+1 end
	end end
	if n==0 then return {found=false,kind='plaza'} end
	local cx,cy=math.floor(sx/n+0.5),math.floor(sy/n+0.5)+3
	local stand
	for r=0,8 do
		for dx=-r,r do for dy=-r,r do
			local nx,ny=cx+dx,cy+dy
			local g=m(nx,ny,Map.TERRAIN)
			if not stand and g and not g.does_block_move and not rawget(g,'block_move') and not g.change_level and not g.change_zone and not m(nx,ny,Map.ACTOR) and not m(nx,ny,Map.TRAP) then stand={nx,ny} end
		end end
		if stand then break end
	end
	assert(stand,'no stand cell')
	p:move(stand[1],stand[2],true)
	local moved=0
	for _,a in pairs(game.level.entities) do
		if a~=p and a.x and math.abs(a.x-cx)<=16 and math.abs(a.y-cy)<=10 then game.level:removeEntity(a,true);moved=moved+1 end
	end
	return {found=true,kind='plaza',x=cx,y=cy,stand=stand,statues=n,removed_actors=moved,player={p.x,p.y}}
end

-- Cells of one grid id, for a pose next to them (statues, mountain ring).
function M.cellsOf(id)
	local m=game.level.map
	local out={}
	for x=0,m.w-1 do for y=0,m.h-1 do
		local g=m(x,y,Map.TERRAIN)
		if g and (g.define_as==id or (not g.define_as and g.name==id)) then out[#out+1]={x,y} end
	end end
	return out
end
return M
