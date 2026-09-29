-- Offline fixture only (S5: Dreadfell ambush, Shadow Crypt, Tannen's Tower,
-- Valley of the Moon, Ring of Blood, Derth's southeast arena). Reuses the TW4
-- scene module (stats, identity probe, rule digest, per-kind board/native
-- counts, fixed poses, weather/particle quieting) and adds the S5 families to
-- the pixel sampler, board floor/blocking lit-pixel pairs, a per-level native
-- listing and two fixture replays of native quest terrain placements (the
-- ambush exit through the quest's own killed_ukruk, the Shadow Crypt stairs
-- exactly as the shade's on_die sets them). Never edits a grid rule field;
-- actors near the photographed window are removed.
local Map=require 'engine.Map'
local Terrain=require 'mod.class.CheckerTerrain'
local tw=dofile('/data-checker-fixture/monster-live_tw4_scene.lua')
local M=setmetatable({},{__index=tw})

local function owned(g)
	local s=g and g._checker_terrain
	return s and g.replace_display==s.display and true or false
end
local function s5Family(m,x,y)
	local g=m(x,y,Map.TERRAIN)
	if not owned(g) then return end
	local img=g.replace_display.image or ''
	local prop=g.replace_display.add_displays and g.replace_display.add_displays[#g.replace_display.add_displays]
	if prop and type(prop.image)=='string' and prop.image:match('^terrain/moonstone_') then return 'moonstone' end
	if prop and prop.image=='terrain/demon_portal3.png' then return 'portal' end
	if img:match('/caldera/wall') then return 'mountain' end
	if img:match('/caldera/poison') then return 'poison' end
end
function M.family(m,x,y) return s5Family(m,x,y) or tw.family(m,x,y) end
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
-- Lit-pixel pairs: a visible passable board floor (grass, sand, stone floor)
-- orthogonally next to a visible board blocking cell (mountain, lava pit,
-- stone wall, tree, moonstone); both inside the viewport, nothing on either.
local FLOORS={grass=true,sand=true,['stone-floor']=true}
local WALLS={mountain=true,lava=true,['stone-wall']=true,['stone-old-wall']=true,tree=true,moonstone=true}
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
		if FLOORS[f] and Terrain.visible(m,x,y) and clear(x,y) then
			for _,d in ipairs{{0,-1},{1,0},{0,1},{-1,0}} do
				local nx,ny=x+d[1],y+d[2]
				local nf=M.family(m,nx,ny)
				local water=nf=='water' or nf=='poison'
				if (WALLS[nf] or water) and Terrain.visible(m,nx,ny) and clear(nx,ny) then
					local ok,sx,sy=inside(x,y)
					local ok2,wx,wy=inside(nx,ny)
					if ok and ok2 then
						local list=water and out.water or out.pairs
						list[#list+1]={floor={x,y,sx,sy,f},wall={nx,ny,wx,wy,nf}}
					end
				end
			end
		end
	end end
	return out
end
-- Every cell that is not board right now, grouped by grid id, with the facts
-- that decide why (callbacks, transitions, layers, adapter kinds).
function M.natives()
	local m=game.level.map
	local zoneName=game.zone.short_name
	local out={zone=zoneName,level=game.level.level,groups={}}
	local order={}
	for x=0,m.w-1 do for y=0,m.h-1 do
		local g=m(x,y,Map.TERRAIN)
		local r=m._checker_korpul and m._checker_korpul[x+y*m.w]
		if g and not owned(g) and not (r and r.painted and r.file) then
			local funcs={}
			for k,v in pairs(g) do if type(v)=='function' then funcs[#funcs+1]=k end end
			table.sort(funcs)
			local key=tostring(g.define_as or ('<'..tostring(g.name)..'>'))
			local b=out.groups[key]
			if not b then
				b={n=0,name=g.name,type=g.type or false,subtype=g.subtype or false,image=g.image or false,
					functions=table.concat(funcs,','),change_level=g.change_level or false,change_zone=g.change_zone or false,
					does_block_move=g.does_block_move and true or false,block_sight=g.block_sight and true or false,
					forest_kind=Terrain.batch4Kind(g,zoneName) or false,stone_kind=Terrain.classify(g) or false,
					visible=0,remembered=0,unknown=0,sample={}}
				out.groups[key]=b;order[#order+1]=key
			end
			b.n=b.n+1
			if Terrain.visible(m,x,y) then b.visible=b.visible+1 elseif m.remembers(x,y) then b.remembered=b.remembered+1 else b.unknown=b.unknown+1 end
			if #b.sample<4 then b.sample[#b.sample+1]={x,y} end
		end
	end end
	out.order=order
	return out
end
-- Walk the player over every free passable cell with native FOV (memory
-- accrues natively; seens are never forced), then return to the start.
M.walk=tw.explore
-- Dreadfell ambush: the quest's own killed_ukruk (quests/staff-absorption.lua
-- :107-121) places the world exit under the player with a direct map set;
-- then one game:onTurn runs the display-only repaint hook. Fixture only: the
-- quest is granted to the fixture hero first.
function M.ambushExit()
	local p=game.player
	assert(game.zone.short_name=='dreadfell-ambush')
	local m=game.level.map
	local before=m(p.x,p.y,Map.TERRAIN)
	if not p:hasQuest('staff-absorption') then p:grantQuest('staff-absorption') end
	local q=p:hasQuest('staff-absorption')
	q:killed_ukruk(p)
	tw.ms.caveClearDialogs()
	local placed=m(p.x,p.y,Map.TERRAIN)
	local out={x=p.x,y=p.y,before=before and before.define_as or false,placed=placed and placed.define_as or false,
		kind=Terrain.batch4Kind(placed,'dreadfell-ambush') or false,board_before_turn=owned(placed)}
	game:onTurn()
	placed=m(p.x,p.y,Map.TERRAIN)
	out.board_after_turn=owned(placed)
	out.image=owned(placed) and placed.replace_display.image or false
	out.change_zone=placed.change_zone or false;out.change_level=placed.change_level or false
	return out
end
-- Shadow Crypt L3: the same native terrain set as the shade clone's on_die
-- (zones/shadow-crypt/npcs.lua:105), on a free floor cell next to the player.
function M.cryptExit()
	assert(game.zone.short_name=='shadow-crypt')
	local m,p=game.level.map,game.player
	local spot
	for _,d in ipairs{{1,0},{-1,0},{0,1},{0,-1}} do
		local x,y=p.x+d[1],p.y+d[2]
		local g=m(x,y,Map.TERRAIN)
		if not spot and g and g.define_as=='FLOOR' and not m(x,y,Map.ACTOR) then spot={x,y} end
	end
	assert(spot,'no floor next to the player')
	game.level.map(spot[1],spot[2],game.level.map.TERRAIN,game.zone.grid_list.UP_WILDERNESS)
	local g=m(spot[1],spot[2],Map.TERRAIN)
	local r=m._checker_korpul and m._checker_korpul[spot[1]+spot[2]*m.w]
	return {x=spot[1],y=spot[2],id=g.define_as,stone_kind=Terrain.classify(g) or false,
		recorded=r and r.kind or false,painted=r and r.painted or false,file=r and r.file or false,overlay=r and r.overlay or false}
end
return M
