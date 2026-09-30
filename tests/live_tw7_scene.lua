-- Offline fixture only (TW7: town stone roads, Zigur/Angolwen crop fields,
-- Gates of Morning palms). Reuses the TW6 scene module (stats, identity probe,
-- rule digest, per-kind board/native counts, fixed poses, weather/particle
-- quieting) and adds the new families to the pixel sampler, a centroid finder
-- for Angolwen's TMX map, a per-town TW7 census and grayscale value pairs
-- (road/field next to grass, walls, plaza floor; palm next to sand). Never
-- edits a grid rule field; actors near the photographed window are removed.
local Map=require 'engine.Map'
local Terrain=require 'mod.class.CheckerTerrain'
local tw=dofile('/data-checker-fixture/monster-live_tw6_scene.lua')
local M=setmetatable({},{__index=tw})

local function owned(g)
	local s=g and g._checker_terrain
	return s and g.replace_display==s.display and true or false
end
local function tw7Family(m,x,y)
	local g=m(x,y,Map.TERRAIN)
	if not owned(g) then return end
	local img=g.replace_display.image or ''
	if img:match('/town/road') then return 'town-road' end
	if img:match('/town/fields') then return 'fields' end
	if img:match('/eruan/palm') then return 'palm' end
end
function M.family(m,x,y) return tw7Family(m,x,y) or tw.family(m,x,y) end
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
-- Value pairs: a visible TW7 cell (town road, field, palm) orthogonally next
-- to a visible cell of another family; both inside the viewport, nothing on
-- either. The Python side reads the frame and groups by family pair.
local SUBJECT={['town-road']=true,fields=true,palm=true}
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
		if f and SUBJECT[f] and Terrain.visible(m,x,y) and clear(x,y) then
			for _,d in ipairs{{0,-1},{1,0},{0,1},{-1,0}} do
				local nx,ny=x+d[1],y+d[2]
				local nf=M.family(m,nx,ny)
				if nf and nf~=f and Terrain.visible(m,nx,ny) and clear(nx,ny) then
					local ok,sx,sy=inside(x,y)
					local ok2,wx,wy=inside(nx,ny)
					if ok and ok2 then out.pairs[#out.pairs+1]={floor={x,y,sx,sy,f},wall={nx,ny,wx,wy,nf}} end
				end
			end
		end
	end end
	return out
end
-- Centroid of the cells whose define_as matches `pattern`.
function M.centroid(pattern)
	local m=game.level.map
	local sx,sy,n=0,0,0
	for x=0,m.w-1 do for y=0,m.h-1 do
		local g=m(x,y,Map.TERRAIN)
		if g and type(g.define_as)=='string' and g.define_as:match(pattern) then sx,sy,n=sx+x,sy+y,n+1 end
	end end
	if n==0 then return {n=0} end
	return {n=n,x=math.floor(sx/n+0.5),y=math.floor(sy/n+0.5)}
end
-- Per-town TW7 census: every road/field/palm identity cell, its adapter kind,
-- whether it is drawn as board art now (and which picture) or native.
local IDS={'^GRASS_ROAD_STONE$','^FLOOR_ROAD_STONE$','^COBBLESTONE$','^FIELDS%d*$','^PALMTREE%d*$'}
function M.tw7()
	local m=game.level.map
	local zoneName=game.zone.short_name
	local out={zone=zoneName,ids={},images={}}
	for x=0,m.w-1 do for y=0,m.h-1 do
		local g=m(x,y,Map.TERRAIN)
		local id=g and type(g.define_as)=='string' and g.define_as
		local hit
		for _,p in ipairs(IDS) do if id and id:match(p) then hit=p end end
		if hit then
			local key=id:gsub('%d+$','')
			local e=out.ids[key] or {n=0,board=0,native=0,kinds={}}
			out.ids[key]=e;e.n=e.n+1
			local k=tostring(Terrain.batch4Kind(g,zoneName) or false)
			e.kinds[k]=(e.kinds[k] or 0)+1
			if owned(g) then
				e.board=e.board+1
				local img=(g.replace_display.image or ''):gsub('^checker%-revised%+','')
				out.images[img]=(out.images[img] or 0)+1
			else e.native=e.native+1 end
		end
	end end
	return out
end
-- Histogram of board pictures on the level (regression: no town picture
-- outside towns; Eruan palms keep the S6 palm).
function M.imageHist()
	local m=game.level.map
	local out={}
	for x=0,m.w-1 do for y=0,m.h-1 do
		local g=m(x,y,Map.TERRAIN)
		if owned(g) then
			local img=(g.replace_display.image or ''):gsub('^checker%-revised%+',''):gsub('%d*%.png$','')
			out[img]=(out[img] or 0)+1
		end
	end end
	return out
end
return M
