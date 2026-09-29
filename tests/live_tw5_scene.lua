-- Offline fixture only (TW5: Gates of Morning). Reuses the TW4 scene module
-- (stats, identity probe, rule digest, per-kind board/native counts, fixed
-- poses, weather/particle quieting) and adds the golden-mountain and sand
-- families to the pixel sampler, adjacent floor/mountain lit-pixel pairs and
-- a fixture-only FENS placement that repeats the zone's own post_process
-- steps (sunwall players only in the real game). Never edits a grid rule
-- field; actors near the photographed window are removed.
local Map=require 'engine.Map'
local Terrain=require 'mod.class.CheckerTerrain'
local tw=dofile('/data-checker-fixture/monster-live_tw4_scene.lua')
local M=setmetatable({},{__index=tw})

local function gatesFamily(m,x,y)
	local g=m(x,y,Map.TERRAIN)
	local s=g and g._checker_terrain
	if not (s and g.replace_display==s.display) then return end
	local img=g.replace_display.image or ''
	if img:match('/gold%-mountain/') then return 'gold-mountain' end
	if img:match('/beach/sand') then return 'sand' end
	if img:match('/beach/palm') then return 'palm' end
end
function M.family(m,x,y) return gatesFamily(m,x,y) or tw.family(m,x,y) end
-- Same sampler as TW4, but through this module's family() (the TW4 samples()
-- calls its own local family chain, which does not know the new families).
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
-- Lit-pixel pairs: a visible passable board floor cell (grass, sand, road,
-- stone floor) orthogonally next to a visible board golden-mountain cell,
-- both fully inside the viewport, no actor/object/trap on either.
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
		local f=M.family(m,x,y)
		if (f=='grass' or f=='sand' or f=='road' or f=='stone-floor') and Terrain.visible(m,x,y) and clear(x,y) then
			for _,d in ipairs{{0,-1},{1,0},{0,1},{-1,0}} do
				local nx,ny=x+d[1],y+d[2]
				if M.family(m,nx,ny)=='gold-mountain' and Terrain.visible(m,nx,ny) and clear(nx,ny) then
					local ok,sx,sy=inside(x,y)
					local ok2,wx,wy=inside(nx,ny)
					if ok and ok2 then out.pairs[#out.pairs+1]={floor={x,y,sx,sy,f},wall={nx,ny,wx,wy}} end
				end
			end
		end
	end end
	return out
end
-- Fixture-only: the FENS entrance exactly as zone.lua:84-88 adds it for a
-- sunwall player (makeEntityByName + addEntity + nicer_tiles:updateAround),
-- then report how the adapter treats it (it must stay native).
function M.addFens()
	local spot=game.level:pickSpot{type="pop-birth", subtype="slazish-fens"}
	local g=game.zone:makeEntityByName(game.level,"terrain","FENS")
	game.zone:addEntity(game.level,g,"terrain",spot.x,spot.y)
	game.nicer_tiles:updateAround(game.level,spot.x,spot.y)
	game:checkerApplySettings()
	local c=game.level.map(spot.x,spot.y,Map.TERRAIN)
	local st=c and c._checker_terrain
	return {x=spot.x,y=spot.y,id=c and c.define_as or false,change_zone=c and c.change_zone or false,
		forest_kind=Terrain.batch4Kind(c,game.zone.short_name) or false,stone_kind=Terrain.classify(c) or false,
		board=(st and c.replace_display==st.display) and true or false,replace_display=c and c.replace_display and true or false}
end
return M
