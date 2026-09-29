-- Offline fixture only (TW4: Shatur, Point Zero). Reuses the TW3 scene module
-- (stats, identity probe, rule digest, per-kind board/native counts) and adds
-- fixed-coordinate poses on the verified static maps, pixel samples for the
-- snow and void families, and a list of Point Zero's runtime beam endpoints.
-- Never edits a grid rule field; actors near the photographed window are
-- removed; the starfield/weather cosmetics can be paused for toggle frames.
local Map=require 'engine.Map'
local Terrain=require 'mod.class.CheckerTerrain'
local tw=dofile('/data-checker-fixture/monster-live_tw3_scene.lua')
local M=setmetatable({},{__index=tw})

local function free(m,x,y)
	local g=m(x,y,Map.TERRAIN)
	return g and not g.does_block_move and not rawget(g,'block_move') and not rawget(g,'on_move') and
		not g.change_level and not g.change_zone and not m(x,y,Map.ACTOR) and not m(x,y,Map.TRAP)
end
-- Window centred on (cx,cy); stand on the free cell nearest (sx,sy) (the
-- window centre when omitted); clear actors from the window.
function M.poseAt(cx,cy,sx,sy,label)
	local m,p=game.level.map,game.player
	sx,sy=sx or cx,sy or cy
	local stand
	for r=0,12 do
		for dx=-r,r do for dy=-r,r do
			if not stand and math.max(math.abs(dx),math.abs(dy))==r and free(m,sx+dx,sy+dy) then stand={sx+dx,sy+dy} end
		end end
		if stand then break end
	end
	assert(stand,'no stand cell')
	p:move(stand[1],stand[2],true)
	local moved=0
	for _,a in pairs(game.level.entities) do
		if a~=p and a.x and math.abs(a.x-cx)<=21 and math.abs(a.y-cy)<=12 then game.level:removeEntity(a,true);moved=moved+1 end
	end
	return {found=true,kind=label,x=cx,y=cy,stand=stand,removed_actors=moved,player={p.x,p.y}}
end

-- Point Zero cosmetics: its starfield background and cloud weather animate
-- every frame; paused for toggle comparisons (display only, fixture only).
function M.quiet()
	local l=game.level
	local had={starfield=l.starfield_shader and true or false,background=l.background_particle and true or false,
		foreground=l.foreground_particle and true or false,weather=l.data and l.data.weather_particle and true or false}
	l.starfield_shader=nil;l.background_particle=nil;l.foreground_particle=nil
	if game.zone.short_name=='town-point-zero' then game.zone.background=nil;game.zone.foreground=nil end
	if l.data then l.data.weather_particle=nil;l.data.weather_shader=nil end
	return had
end

-- Point Zero's seven beam particle emitters animate every frame; hide them
-- (fixture only, display only) around a toggle comparison, then put back.
local paused
function M.pauseParticles(on)
	local m=game.level.map
	if on then
		paused={}
		for _,e in ipairs(m.particles) do paused[#paused+1]={e,e.x,e.y} end
		for _,p in ipairs(paused) do m:removeParticleEmitter(p[1]) end
		return {paused=#paused}
	end
	local n=0
	for _,p in ipairs(paused or {}) do m:addParticleEmitter(p[1],p[2],p[3]);n=n+1 end
	paused=nil
	return {restored=n}
end

local function snowFamily(m,x,y)
	local g=m(x,y,Map.TERRAIN)
	local s=g and g._checker_terrain
	if not (s and g.replace_display==s.display) then return end
	local img=g.replace_display.image or ''
	local prop=g.replace_display.add_displays and g.replace_display.add_displays[1]
	if prop and prop.image=='terrain/statue3.png' then return 'statue' end
	if img:match('/snow/tree') then return 'snow-tree' end
	if img:match('/snow/snow%-ground') then return 'snow-ground' end
	if img:match('/void/space') then return 'space' end
	if img:match('/void/rocks') then return 'rocks' end
	if img:match('/void/rift') then return 'rift' end
	if img:match('/void/floor') then return 'void-floor' end
end
function M.family(m,x,y) return snowFamily(m,x,y) or tw.family(m,x,y) end
function M.samples()
	local m=game.level.map
	local size=m.tile_w*m.zoom
	local out={tile=size,cells={}}
	for x=0,m.w-1 do for y=0,m.h-1 do
		if m.remembers(x,y) and not m(x,y,Map.ACTOR) and not m(x,y,Map.OBJECT) and not m(x,y,Map.TRAP) then
			local f=M.family(m,x,y)
			if f then
				local sx,sy=m:getTileToScreen(x,y)
				if sx>=m.display_x+size and sy>=m.display_y+size and sx+2*size<=m.display_x+m.viewport.width and sy+2*size<=m.display_y+m.viewport.height then
					out.cells[#out.cells+1]={x=x,y=y,sx=sx,sy=sy,family=f..(Terrain.visible(m,x,y) and '' or '-remembered')}
				end
			end
		end
	end end
	return out
end

-- Runtime-placed Point Zero beam endpoints (cloneFull + native block_move).
function M.endpoints()
	local m=game.level.map
	local out={}
	for x=0,m.w-1 do for y=0,m.h-1 do
		local g=m(x,y,Map.TERRAIN)
		local f=g and rawget(g,'block_move')
		if f and g.exit then
			local i=debug.getinfo(f,'S')
			local s=g._checker_terrain
			out[#out+1]={x=x,y=y,id=g.define_as or false,exit={g.exit.x,g.exit.y},source=i and i.source..':'..i.linedefined,
				forest_kind=Terrain.batch4Kind(g,game.zone.short_name) or false,
				board=(s and g.replace_display==s.display) and true or false,replace_display=g.replace_display and true or false}
		end
	end end
	return out
end
return M
