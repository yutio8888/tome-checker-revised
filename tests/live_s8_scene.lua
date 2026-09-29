-- Offline fixture only (S8: darker diggable-wall set for the Kor'Pul stone
-- family, V2/V7). Reuses the S6 scene module (stats, identity probe, rule
-- digest, weather/particle quieting, poses, native-FOV walk) and adds:
-- per-level identity counts of diggable WALL versus HARDWALL; a pose picker
-- that looks for floor next to diggable wall (or a door / stairs in a wall
-- line); lit-pixel pairs split by blocking kind (brick WALL, HARDWALL,
-- scorch lava rock) and by floor family; the files each wall record draws;
-- and a fixture-only switch that hides the S8 dark set so the same layout
-- can be photographed with and without it in one process. Never edits a
-- grid rule field; actors near the photographed window are removed.
local Map=require 'engine.Map'
local Terrain=require 'mod.class.CheckerTerrain'
local tw=dofile('/data-checker-fixture/monster-live_s6_scene.lua')
local M=setmetatable({},{__index=tw})

local function owned(g)
	local s=g and g._checker_terrain
	return s and g.replace_display==s.display and true or false
end
local function record(m,x,y)
	local r=m._checker_korpul and m._checker_korpul[x+y*m.w]
	if r and r.painted and r.file then return r end
end
-- Families for S8: stone records by kind; forest-side families from S6.
local function s8Family(m,x,y)
	local r=record(m,x,y)
	if r then
		if r.kind=='wall' then return 'brick' end
		if r.kind=='hardwall' then return 'hardwall' end
		if r.kind=='old-wall' then return 'old-wall' end
		if r.kind=='floor' or r.kind=='deco-floor' then return 'stone-floor' end
		if r.kind:match('^door') or r.kind=='lock' then return 'door' end
		if r.kind:match('^stairs') then return 'stairs' end
		return 'stone-'..r.kind
	end
	local g=m(x,y,Map.TERRAIN)
	if owned(g) then
		local img=g.replace_display.image or ''
		if img:match('/scorch[%w%-]*/wall') then return 'scorch' end
		if img:match('/daikara/lava%-floor') then return 'lava-floor' end
	end
	return tw.family(m,x,y)
end
M.family=s8Family

-- Identity counts over the whole level (read only; classify is the stone
-- adapter's own contract, not the painted state).
function M.kinds()
	local m=game.level.map
	local out={zone=game.zone.short_name,level=game.level.level,w=m.w,h=m.h,kinds={},painted={},files={}}
	for x=0,m.w-1 do for y=0,m.h-1 do
		local g=m(x,y,Map.TERRAIN)
		local k=g and Terrain.classify(g)
		if k then out.kinds[k]=(out.kinds[k] or 0)+1 end
		local r=record(m,x,y)
		if r then
			out.painted[r.kind]=(out.painted[r.kind] or 0)+1
			if r.kind=='wall' or r.kind=='hardwall' or r.kind:match('^door') then
				local folder=r.file:match('refined/([%w%-]+)/') or '?'
				local key=r.kind:gsub('%-.*','')..':'..folder
				out.files[key]=(out.files[key] or 0)+1
			end
		end
		if owned(g) then
			local img=g.replace_display.image or ''
			if img:match('/scorch[%w%-]*/wall') then out.files['scorch:'..(img:match('refined/(scorch[%w%-]*)/') or '?')]=(out.files['scorch:'..(img:match('refined/(scorch[%w%-]*)/') or '?')] or 0)+1 end
		end
	end end
	return out
end

-- Pose window (21x13 cells at 64px). kind: 'wall' = most floor/diggable
-- wall contacts; 'door' = a door with diggable wall beside it; 'stairs' =
-- stairs near diggable wall; 'scorch' = floor next to Fearscape rock.
-- Identity only (classify), so it also works before anything is seen.
function M.pick(kind)
	local m=game.level.map
	local function k(x,y) if x<0 or y<0 or x>=m.w or y>=m.h then return end local g=m(x,y,Map.TERRAIN);return g and Terrain.classify(g) end
	local function scorch(x,y) local g=m(x,y,Map.TERRAIN);return g and g.define_as and tostring(g.define_as):match('^LAVA_WALL') end
	local cells={}
	for x=0,m.w-1 do for y=0,m.h-1 do
		local c=k(x,y)
		local s=0
		if kind=='scorch' then
			if scorch(x,y) then
				for _,d in ipairs{{0,-1},{1,0},{0,1},{-1,0}} do local g=m(x+d[1],y+d[2],Map.TERRAIN);if g and not g.does_block_move then s=s+1 end end
			end
		elseif c=='wall' then
			for _,d in ipairs{{0,-1},{1,0},{0,1},{-1,0}} do
				local n=k(x+d[1],y+d[2])
				if n=='floor' or n=='deco-floor' then s=s+1 end
				if kind=='door' and n and (n:match('^door') or n=='lock') then s=s+30 end
				if kind=='stairs' and n and n:match('^stairs') then s=s+30 end
			end
			if kind=='stairs' then
				for dx=-2,2 do for dy=-2,2 do local n=k(x+dx,y+dy);if n and n:match('^stairs') then s=s+10 end end end
			end
		end
		if s>0 then cells[#cells+1]={x,y,s} end
	end end
	local best,bx,by=0,nil,nil
	for cx=0,m.w-1 do for cy=0,m.h-1 do
		local t=0
		for _,c in ipairs(cells) do if math.abs(c[1]-cx)<=4 and math.abs(c[2]-cy)<=3 then t=t+c[3] end end
		if t>best then best,bx,by=t,cx,cy end
	end end
	if not bx then return {found=false,kind=kind} end
	-- Stand on the free cell nearest the window centre (poseAt).
	return {found=true,kind=kind,x=bx,y=by,score=best}
end

-- Lit-pixel pairs: a visible passable floor next to a visible blocking cell
-- (and next to a visible door), split by blocking family.
local FLOORS={grass=true,sand=true,road=true,['stone-floor']=true,['hut-floor']=true,['lava-floor']=true}
local WALLS={brick=true,hardwall=true,scorch=true,mountain=true,['old-wall']=true,tree=true,door=true}
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
		local f=s8Family(m,x,y)
		if FLOORS[f] and Terrain.visible(m,x,y) and clear(x,y) then
			for _,d in ipairs{{0,-1},{1,0},{0,1},{-1,0}} do
				local nx,ny=x+d[1],y+d[2]
				local nf=s8Family(m,nx,ny)
				if WALLS[nf] and Terrain.visible(m,nx,ny) and clear(nx,ny) then
					local ok,sx,sy=inside(x,y)
					local ok2,wx,wy=inside(nx,ny)
					if ok and ok2 then out.pairs[#out.pairs+1]={floor={x,y,sx,sy,f},wall={nx,ny,wx,wy,nf}} end
				end
			end
		end
	end end
	return out
end

-- Fixture only, display only: hide/restore the S8 dark set (the manifest
-- gate), then repaint the level so the same layout shows the pre-S8 walls.
local saved={}
function M.darkSet(on)
	local keys={'korpulDarkAssets','scorchDarkAssets'}
	local out={}
	for _,key in ipairs(keys) do
		if Terrain[key] ~= nil then
			if not on then
				saved[key]=saved[key] or Terrain[key]
				Terrain[key]={ready=false,files={}}
			elseif saved[key] then
				Terrain[key]=saved[key];saved[key]=nil
			end
			out[key]=Terrain[key].ready==true
		else
			out[key]='absent'
		end
	end
	game:checkerApplySettings()
	return out
end
return M
