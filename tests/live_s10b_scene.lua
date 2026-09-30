-- Offline fixture only (S10b: Vor Pride L1-3, the board gothic family).
-- Reuses the S10a scene module (rule digest, poses, weather/particle
-- quieting, native listing, layer survey) and adds: a per-level identity
-- histogram with the S10b kind, families for the gothic board art, a pose
-- picker by native ids (so the before and after phases pick the same
-- window) and lit-pixel pairs between gothic/burnt floors and blockers.
-- Never edits a grid rule field; actors near the photographed window are
-- removed by the inherited poseAt.
local Map=require 'engine.Map'
local Terrain=require 'mod.class.CheckerTerrain'
local tw=dofile('/data-checker-fixture/monster-live_s10_scene.lua')
local M=setmetatable({},{__index=tw})

local function owned(g)
	local s=g and g._checker_terrain
	return s and g.replace_display==s.display and true or false
end
local function painted(m,x,y)
	local r=m._checker_korpul and m._checker_korpul[x+y*m.w]
	if r and r.painted and r.file then return r end
end
local function s10bKind(g)
	return Terrain.s10bKind and g and Terrain.s10bKind(g,game.zone.short_name) or nil
end
local function family(m,x,y)
	local g=m(x,y,Map.TERRAIN)
	if owned(g) then
		local img=g.replace_display.image or ''
		if img:match('/gothic/wall') then return 'gothic-wall' end
		if img:match('/gothic/door') then return 'gothic-door' end
		if img:match('/gothic/pillar') then return 'gothic-pillar' end
		if img:match('/gothic/floor') or img:match('/gothic/stairs') or img:match('/gothic/exit') then return 'gothic-floor' end
		if img:match('/burnt/tree') then return 'burnt-tree' end
		if img:match('/burnt/floor') or img:match('/burnt/exit') then return 'burnt-floor' end
		if img:match('/deep%d') then return 'deep' end
	end
	return tw.family(m,x,y)
end
M.family=family

-- Whole-level histogram by native id (trailing digits folded): count, S10b
-- kind, stone kind, owner (board display, stone record, native), zone stamp.
function M.ids()
	local m=game.level.map
	local out={zone=game.zone.short_name,level=game.level.level,w=m.w,h=m.h,ids={},owner={board=0,stone=0,native=0}}
	for x=0,m.w-1 do for y=0,m.h-1 do
		local g=m(x,y,Map.TERRAIN)
		if g then
			local id=tostring(g.define_as or ('<'..tostring(g.name)..'>')):gsub('%d+$','#')
			local e=out.ids[id]
			if not e then e={n=0,board=0,stone=0,native=0,s10b={},stone_kind={},stamp=0};out.ids[id]=e end
			e.n=e.n+1
			local k=s10bKind(g)
			if k then e.s10b[k]=(e.s10b[k] or 0)+1 end
			local c=Terrain.classify(g)
			if c then e.stone_kind[c]=(e.stone_kind[c] or 0)+1 end
			if g._checker_zone_source then e.stamp=e.stamp+1 end
			local o=owned(g) and 'board' or painted(m,x,y) and 'stone' or 'native'
			e[o]=e[o]+1;out.owner[o]=out.owner[o]+1
		end
	end end
	return out
end

-- Pose window picker by native ids only. 'hall': GOTHIC_WALL next to
-- GOTHIC_FLOOR; 'door': gothic doors in a wall line; 'burnt': BURNT_TREE
-- next to BURNT_GROUND; 'water': DEEP_WATER next to anything walkable;
-- 'pillar': gothic pillars; 'stairs': the level's way down (FLAT_DOWN4 on
-- the burnt yard); 'upstairs': its way up or out (gothic flat exits).
local EXIT={FLAT_DOWN4=true,GOTHIC_FLAT_DOWN4=true,GOTHIC_DOWN=true}
local UPEXIT={GOTHIC_FLAT_UP_WILDERNESS=true,GOTHIC_FLAT_UP6=true,GOTHIC_UP=true,GOTHIC_UP_WILDERNESS=true}
function M.pick(kind)
	local m=game.level.map
	local function id(x,y)
		if x<0 or y<0 or x>=m.w or y>=m.h then return '' end
		local g=m(x,y,Map.TERRAIN)
		return g and type(g.define_as)=='string' and g.define_as or ''
	end
	local function role(i)
		if kind=='hall' then
			if i:match('^GOTHIC_WALL') then return 'wall' end
			if i=='GOTHIC_FLOOR' then return 'floor' end
		elseif kind=='door' then
			if i:match('^GOTHIC_DOOR') then return 'wall' end
			if i=='GOTHIC_FLOOR' or i:match('^BURNT_GROUND') then return 'floor' end
		elseif kind=='burnt' then
			if i:match('^BURNT_TREE') then return 'wall' end
			if i:match('^BURNT_GROUND') then return 'floor' end
		elseif kind=='water' then
			if i=='DEEP_WATER' then return 'wall' end
			if i:match('^BURNT_GROUND') or i=='GOTHIC_FLOOR' then return 'floor' end
		elseif kind=='pillar' then
			if i:match('^GOTHIC_WALL_PILLAR') or i:match('^GOTHIC_WALL_SMALL') then return 'wall' end
			if i=='GOTHIC_FLOOR' or i:match('^BURNT_GROUND') then return 'floor' end
		elseif kind=='stairs' then
			if EXIT[i] then return 'wall' end
			return 'floor'
		elseif kind=='upstairs' then
			if UPEXIT[i] then return 'wall' end
			return 'floor'
		end
	end
	local cells={}
	for x=0,m.w-1 do for y=0,m.h-1 do
		if role(id(x,y))=='wall' then
			local s=(kind=='stairs' or kind=='upstairs' or kind=='door' or kind=='pillar') and 40 or 0
			for _,d in ipairs{{0,-1},{1,0},{0,1},{-1,0}} do if role(id(x+d[1],y+d[2]))=='floor' then s=s+1 end end
			if s>0 then cells[#cells+1]={x,y,s} end
		end
	end end
	local best,bx,by=0,nil,nil
	for cx=0,m.w-1 do for cy=0,m.h-1 do
		local t=0
		for _,c in ipairs(cells) do if math.abs(c[1]-cx)<=4 and math.abs(c[2]-cy)<=3 then t=t+c[3] end end
		if t>best then best,bx,by=t,cx,cy end
	end end
	if not bx then return {found=false,kind=kind} end
	return {found=true,kind=kind,x=bx,y=by,score=best}
end

-- Lit-pixel pairs: a visible free floor next to a visible blocker or a
-- different floor family.
local FLOORS={['gothic-floor']=true,['burnt-floor']=true,['stone-floor']=true}
local WALLS={['gothic-wall']=true,['gothic-door']=true,['gothic-pillar']=true,['burnt-tree']=true,deep=true,brick=true,hardwall=true,door=true}
function M.pairs()
	local m=game.level.map
	local size=m.tile_w*m.zoom
	local out={tile=size,pairs={}}
	local function inside(x,y)
		local sx,sy=m:getTileToScreen(x,y)
		return sx>=m.display_x+size and sy>=m.display_y+size and sx+2*size<=m.display_x+m.viewport.width and
			sy+2*size<=m.display_y+m.viewport.height,sx,sy
	end
	local function clear(x,y) return not m(x,y,Map.ACTOR) and not m(x,y,Map.OBJECT) and not m(x,y,Map.TRAP) end
	for x=1,m.w-2 do for y=1,m.h-2 do
		local f=family(m,x,y)
		if FLOORS[f] and Terrain.visible(m,x,y) and clear(x,y) then
			for _,d in ipairs{{0,-1},{1,0},{0,1},{-1,0}} do
				local nx,ny=x+d[1],y+d[2]
				local nf=family(m,nx,ny)
				if (WALLS[nf] or FLOORS[nf] and nf~=f) and Terrain.visible(m,nx,ny) and clear(nx,ny) then
					local ok,sx,sy=inside(x,y)
					local ok2,wx,wy=inside(nx,ny)
					if ok and ok2 then out.pairs[#out.pairs+1]={floor={x,y,sx,sy,f},wall={nx,ny,wx,wy,nf}} end
				end
			end
		end
	end end
	return out
end

-- Native listing with the S10b kind.
function M.natives()
	local out=tw.natives()
	local m=game.level.map
	for _,b in pairs(out.groups) do
		local x,y=b.sample[1][1],b.sample[1][2]
		b.s10_kind=nil
		b.s10b_kind=s10bKind(m(x,y,Map.TERRAIN)) or false
	end
	return out
end
return M
