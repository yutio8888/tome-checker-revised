-- Offline fixture only (TW6: Irkkk). Reuses the TW5 scene module (stats,
-- identity probe, rule digest, per-kind board/native counts, fixed poses,
-- weather/particle quieting) and adds the jungle and bamboo-hut families to
-- the pixel sampler, floor/hut-wall and water/grass lit-pixel pairs, the six
-- yeek shopkeepers (actors: kept in every photographed window, never edited)
-- and a native door opening (the game's own Grid:block_move with the player
-- as the opener). Never edits a grid rule field; other actors near the
-- photographed window are removed.
local Map=require 'engine.Map'
local Terrain=require 'mod.class.CheckerTerrain'
local tw=dofile('/data-checker-fixture/monster-live_tw5_scene.lua')
local M=setmetatable({},{__index=tw})

local function owned(g)
	local s=g and g._checker_terrain
	return s and g.replace_display==s.display and true or false
end
local function irkkkFamily(m,x,y)
	local g=m(x,y,Map.TERRAIN)
	if not owned(g) then return end
	local img=g.replace_display.image or ''
	if img:match('/bamboo/wall') then return 'hut-wall' end
	if img:match('/bamboo/door%-closed') then return 'hut-door' end
	if img:match('/bamboo/door%-open') then return 'hut-door-open' end
	if img:match('/bamboo/floor') then
		local prop=g.replace_display.add_displays and g.replace_display.add_displays[1]
		if prop then return 'cooking-pit' end
		return 'hut-floor'
	end
	if img:match('/caldera/floor') then return 'jungle-grass' end
	if img:match('/caldera/tree') then return 'jungle-tree' end
	if img:match('/caldera/exit') then return 'exit' end
end
function M.family(m,x,y) return irkkkFamily(m,x,y) or tw.family(m,x,y) end
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
-- Lit-pixel pairs: a visible passable board floor cell (jungle grass, hut
-- floor) orthogonally next to a visible board hut-wall cell, and board water
-- next to board jungle grass; both inside the viewport, nothing on either.
function M.pairs()
	local m=game.level.map
	local size=m.tile_w*m.zoom
	local out={tile=size,pairs={},water={}}
	local function inside(x,y)
		local sx,sy=m:getTileToScreen(x,y)
		return sx>=m.display_x+size and sy>=m.display_y+size and sx+2*size<=m.display_x+m.viewport.width and
			sy+2*size<=m.display_y+m.viewport.height,sx,sy
	end
	local function clear(x,y) return not m(x,y,Map.ACTOR) and not m(x,y,Map.OBJECT) and not m(x,y,Map.TRAP) end
	for x=1,m.w-2 do for y=1,m.h-2 do
		local f=M.family(m,x,y)
		if (f=='jungle-grass' or f=='hut-floor') and Terrain.visible(m,x,y) and clear(x,y) then
			for _,d in ipairs{{0,-1},{1,0},{0,1},{-1,0}} do
				local nx,ny=x+d[1],y+d[2]
				local nf=M.family(m,nx,ny)
				if (nf=='hut-wall' or nf=='water' and f=='jungle-grass') and Terrain.visible(m,nx,ny) and clear(nx,ny) then
					local ok,sx,sy=inside(x,y)
					local ok2,wx,wy=inside(nx,ny)
					if ok and ok2 then
						local list=nf=='water' and out.water or out.pairs
						list[#list+1]={floor={x,y,sx,sy,f},wall={nx,ny,wx,wy}}
					end
				end
			end
		end
	end end
	return out
end
local function free(m,x,y)
	local g=m(x,y,Map.TERRAIN)
	return g and not g.does_block_move and not rawget(g,'block_move') and not rawget(g,'on_move') and
		not g.change_level and not g.change_zone and not m(x,y,Map.ACTOR) and not m(x,y,Map.TRAP)
end
-- Like TW4's poseAt, but the yeek shopkeepers (actors carrying a store) stay.
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
	local moved,kept=0,0
	for _,a in pairs(game.level.entities) do
		if a~=p and a.x and math.abs(a.x-cx)<=21 and math.abs(a.y-cy)<=12 then
			if a.store then kept=kept+1 else game.level:removeEntity(a,true);moved=moved+1 end
		end
	end
	return {found=true,kind=label,x=cx,y=cy,stand=stand,removed_actors=moved,kept_shopkeepers=kept,player={p.x,p.y}}
end
-- Irkkk's cosmetic tropical-bird foreground (zone.lua:62-83) flies over at
-- random; cleared for the whole run so toggle frames compare terrain only
-- (display only, fixture only).
function M.quiet()
	local had=tw.quiet()
	if game.zone.short_name=='town-irkkk' then
		had.birds=game.zone.foreground and true or false
		game.zone.foreground=nil;game.level.bird=nil;game.level.bird_s=nil
	end
	return had
end
-- The six shopkeepers: actor identity, position and the terrain under them
-- (kind, board ownership, rules). Read only.
function M.shops()
	local m=game.level.map
	local zoneName=game.zone.short_name
	local out={}
	for _,a in pairs(game.level.entities) do
		if a.store and a.x then
			local g=m(a.x,a.y,Map.TERRAIN)
			out[#out+1]={name=a.name,x=a.x,y=a.y,image=a.image,faction=a.faction,grid=g and g.define_as or false,
				forest_kind=g and Terrain.batch4Kind(g,zoneName) or false,board=owned(g),
				grid_block_move=g and g.does_block_move and true or false,grid_block_sight=g and g.block_sight and true or false,
				visible=Terrain.visible(m,a.x,a.y),actor_on_cell=m(a.x,a.y,Map.ACTOR)==a}
		end
	end
	table.sort(out,function(a,b) return a.y*100+a.x<b.y*100+b.x end)
	return out
end
-- Door cells (closed or open bamboo doors) with their adapter kind.
function M.doors()
	local m=game.level.map
	local zoneName=game.zone.short_name
	local out={}
	for x=0,m.w-1 do for y=0,m.h-1 do
		local g=m(x,y,Map.TERRAIN)
		if g and g.is_door then
			out[#out+1]={x=x,y=y,id=g.define_as or false,door_opened=g.door_opened or false,door_closed=g.door_closed or false,
				block_sight=g.block_sight and true or false,forest_kind=Terrain.batch4Kind(g,zoneName) or false,board=owned(g),
				image=owned(g) and g.replace_display.image or false}
		end
	end end
	return out
end
-- Fixture-only: open every closed door through the native Grid:block_move
-- (act=true, the player as opener), exactly as walking into it does.
function M.openDoors()
	local m=game.level.map
	local out={}
	for x=0,m.w-1 do for y=0,m.h-1 do
		local g=m(x,y,Map.TERRAIN)
		if g and g.is_door and g.door_opened then
			g:block_move(x,y,game.player,true)
			local n=m(x,y,Map.TERRAIN)
			out[#out+1]={x=x,y=y,from=g.define_as,to=n and n.define_as or false}
		end
	end end
	return out
end
return M
