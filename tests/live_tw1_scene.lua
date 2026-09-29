-- Offline fixture only (TW1: Derth, Lumberjack village). Measures FOV versus
-- remembered stone cells, poses the camera, reports rule digests and pixel
-- sample cells. It never edits a grid rule field. Fixture-only switches:
-- installRemembered can be disabled to observe the pre-TW1 FOV behaviour,
-- actors near the photographed window are removed and Derth's cosmetic
-- eagle foreground is cleared so toggle frames compare terrain only.
local Map=require 'engine.Map'
local Terrain=require 'mod.class.CheckerTerrain'
local ms=dofile('/data-checker-fixture/monster-live_map_survey.lua')
local M={ms=ms}

local realInstall=Terrain.installRemembered
function M.setInstall(on)
	Terrain.installRemembered=on and realInstall or function() return 0 end
	return {install=on and true or false}
end
function M.apply()
	game:checkerApplySettings()
	return {checker_mode=game.checker_mode or false}
end

local function forestOwned(g)
	local s=g and g._checker_terrain
	return s and g.replace_display==s.display and true or false
end
local function family(m,x,y)
	local g=m(x,y,Map.TERRAIN)
	if not g then return end
	if forestOwned(g) then
		local img=g.replace_display.image or ''
		-- TW2: Last Hope statues (prop over board grass) and hard mountain.
		local prop=g.replace_display.add_displays and g.replace_display.add_displays[1]
		if prop and type(prop.image)=='string' and prop.image:match('^terrain/statues/') then return 'statue' end
		-- TW3: Zigur post / Angolwen rocks (props over grass), lava, crystal, sand.
		if prop and (prop.image=='terrain/signpost.png' or prop.image=='terrain/maze_rock.png') then return 'prop' end
		if img:match('/burnt/lava') then return 'lava' end
		if img:match('/crystal/wall') then return 'crystal' end
		if img:match('/beach/sand') then return 'sand' end
		if img:match('/mountain%-wall') then return 'mountain' end
		if img:match('/tree') then return 'tree' end
		if img:match('/deep') then return 'water' end
		if img:match('/road') then return 'road' end
		if img:match('/exit') then return 'exit' end
		if img:match('/grass') or img:match('/flower') then return 'grass' end
		return 'forest-other'
	end
	local r=m._checker_korpul and m._checker_korpul[x+y*m.w]
	if r and r.painted and r.file then
		if r.kind=='hardwall' or r.kind=='wall' then return 'stone-wall' end
		if r.kind=='floor' then return 'stone-floor' end
		if r.kind:match('^door') then return 'stone-door' end
		return 'stone-'..r.kind
	end
end
M.family=family

-- Natural (unforced) state: which stone cells are recorded/painted, split by
-- FOV (map.seens+infovs) and memory (map.remembers).
function M.stats()
	local m=game.level.map
	local zoneName=game.zone.short_name
	local out={zone=zoneName,w=m.w,h=m.h,total=m.w*m.h,level_all_remembered=game.level.data.all_remembered==true,
		zone_all_remembered=game.zone.all_remembered==true,checker_mode=game.checker_mode or false,
		remembered=0,visible=0,stone=0,stone_visible=0,stone_hidden_remembered=0,stone_unremembered=0,
		record_visible=0,record_hidden=0,painted_visible=0,painted_hidden=0,
		hidden_board_render=0,hidden_native_render=0,forest_kind=0,forest_owned=0,forest_hidden_owned=0,
		shops=0,shops_on_stone=0,shop_images={},native_forest={}}
	for x=0,m.w-1 do for y=0,m.h-1 do
		local g=m(x,y,Map.TERRAIN)
		local key=x+y*m.w
		local rem=m.remembers(x,y) and true or false
		local vis=Terrain.visible(m,x,y)
		if rem then out.remembered=out.remembered+1 end
		if vis then out.visible=out.visible+1 end
		local r=m._checker_korpul and m._checker_korpul[key]
		local kind=g and Terrain.classify(g)
		if kind then
			out.stone=out.stone+1
			if vis then out.stone_visible=out.stone_visible+1
			elseif rem then out.stone_hidden_remembered=out.stone_hidden_remembered+1
			else out.stone_unremembered=out.stone_unremembered+1 end
			if r then
				if vis then out.record_visible=out.record_visible+1 else out.record_hidden=out.record_hidden+1 end
				if r.painted then if vis then out.painted_visible=out.painted_visible+1 else out.painted_hidden=out.painted_hidden+1 end end
			end
			if not vis and rem then
				local d=Terrain.render(m,x,y,g,game.checker_mode)
				if d and type(d.image)=='string' and d.image:match('^checker%-revised%+refined/') then out.hidden_board_render=out.hidden_board_render+1
				else out.hidden_native_render=out.hidden_native_render+1 end
			end
		end
		local fk=g and Terrain.batch4Kind(g,zoneName)
		if fk then
			out.forest_kind=out.forest_kind+1
			if forestOwned(g) then out.forest_owned=out.forest_owned+1;if not vis then out.forest_hidden_owned=out.forest_hidden_owned+1 end end
		elseif g and not kind and not forestOwned(g) then
			local id=tostring(g.define_as)
			out.native_forest[id]=(out.native_forest[id] or 0)+1
		end
		local t=m(x,y,Map.TRAP)
		if t and t.is_store or (t and type(t.image)=='string' and t.image:match('^store/')) then
			out.shops=out.shops+1
			if kind then out.shops_on_stone=out.shops_on_stone+1 end
			out.shop_images[#out.shop_images+1]={x=x,y=y,image=t.image,name=t.name,z=t.z,grid=g and g.define_as,kind=kind or false,
				visible=vis,painted=r and r.painted or false}
		end
	end end
	return out
end

-- Camera poses. 'centre': Derth's shop quarter (densest shop/wall/road/water
-- window) or Lumberjack's cabins; 'remembered': a stone window with no cell
-- in the player's FOV, the player left where it stands.
local function score(m,cx,cy,want)
	local c={}
	for dx=-9,9 do for dy=-6,6 do
		local x,y=cx+dx,cy+dy
		if x>=0 and y>=0 and x<m.w and y<m.h then
			local f=family(m,x,y)
			if f then c[f]=(c[f] or 0)+1 end
			-- Pose selection only: stone identity, whether or not it is known yet.
			local k=Terrain.classify(m(x,y,Map.TERRAIN))
			if k then c['id-'..(k:match('^door') and 'door' or k)]=(c['id-'..(k:match('^door') and 'door' or k)] or 0)+1 end
			local t=m(x,y,Map.TRAP)
			if t and type(t.image)=='string' and t.image:match('^store/') then c.shop=(c.shop or 0)+1 end
			if Terrain.visible(m,x,y) then c.visible=(c.visible or 0)+1 end
		end
	end end
	return c
end
function M.pose(kind)
	local m,p=game.level.map,game.player
	local best
	for x=0,m.w-1 do for y=0,m.h-1 do
		local c=score(m,x,y)
		local s
		if kind=='centre' then
			s=(c.shop or 0)*40+math.min((c['id-hardwall'] or 0)+(c['id-wall'] or 0),60)+math.min(c.road or 0,30)*2+math.min(c.water or 0,30)+math.min(c.tree or 0,30)+(c['id-door'] or 0)*10+(c['id-floor'] or 0)
		else
			s=(c.visible or 0)==0 and (math.min(c['stone-wall'] or 0,60)*2+(c.shop or 0)*20+math.min(c.road or 0,20)) or -1
		end
		if s>0 and (not best or s>best.score) then best={x=x,y=y,score=s,counts=c} end
	end end
	if not best then return {found=false,kind=kind} end
	best.found=true;best.kind=kind
	if kind=='centre' then
		-- Stand on a free passable cell near the chosen centre; clear actors from the window.
		local stand
		for r=0,6 do
			for dx=-r,r do for dy=-r,r do
				local nx,ny=best.x+dx,best.y+dy
				local g=m(nx,ny,Map.TERRAIN)
				if not stand and g and not g.does_block_move and not g.change_level and not g.change_zone and not m(nx,ny,Map.ACTOR) and not m(nx,ny,Map.TRAP) then stand={nx,ny} end
			end end
			if stand then break end
		end
		assert(stand,'no stand cell')
		p:move(stand[1],stand[2],true)
		best.stand=stand
	end
	local moved=0
	for _,a in pairs(game.level.entities) do
		if a~=p and a.x and math.abs(a.x-best.x)<=14 and math.abs(a.y-best.y)<=10 then game.level:removeEntity(a,true);moved=moved+1 end
	end
	best.removed_actors=moved
	best.player={p.x,p.y}
	return best
end

-- Fixture staging for levels without all_remembered: walk the player over
-- every free passable cell with native FOV (memory accrues natively; seens
-- are never forced), then return it to (sx,sy).
function M.explore(sx,sy)
	local m,p=game.level.map,game.player
	local n=0
	for x=0,m.w-1 do for y=0,m.h-1 do
		local g=m(x,y,Map.TERRAIN)
		if g and not g.does_block_move and not g.change_level and not g.change_zone and not m(x,y,Map.ACTOR) and not m(x,y,Map.TRAP) then
			p:move(x,y,true);p:doFOV();n=n+1
		end
	end end
	p:move(sx,sy,true);p:doFOV()
	local rem=0;for x=0,m.w-1 do for y=0,m.h-1 do if m.remembers(x,y) then rem=rem+1 end end end
	return {walked=n,remembered=rem,player={p.x,p.y}}
end

-- Re-use a pose recorded by another run (same stand cell, same cleared window).
function M.place(cx,cy,sx,sy)
	local p=game.player
	if sx then p:move(sx,sy,true) end
	for _,a in pairs(game.level.entities) do
		if a~=p and a.x and math.abs(a.x-cx)<=14 and math.abs(a.y-cy)<=10 then game.level:removeEntity(a,true) end
	end
	return {player={p.x,p.y}}
end

-- Natural FOV only: recompute the player's FOV, never force seens.
function M.view(cx,cy)
	local m,p=game.level.map,game.player
	if game.zone.short_name=='town-derth' then game.zone.foreground=nil;game.level.eagle=nil;game.level.eagle_s=nil end
	p:doFOV()
	for x=0,m.w-1 do for y=0,m.h-1 do m:updateMap(x,y) end end
	m.smooth_scroll=0;m:centerViewAround(cx,cy);m:redisplay();m.changed=true;core.display.forceRedraw()
	local vis=0
	for x=math.max(0,cx-9),math.min(m.w-1,cx+9) do for y=math.max(0,cy-6),math.min(m.h-1,cy+6) do if Terrain.visible(m,x,y) then vis=vis+1 end end end
	return {visible_in_window=vis,player={p.x,p.y}}
end

function M.samples()
	local m=game.level.map
	local size=m.tile_w*m.zoom
	local out={tile=size,cells={}}
	for x=0,m.w-1 do for y=0,m.h-1 do
		if m.remembers(x,y) and not m(x,y,Map.ACTOR) and not m(x,y,Map.OBJECT) and not m(x,y,Map.TRAP) then
			local f=family(m,x,y)
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

-- Rule digest: every rule field the adapters must never touch, plus the
-- trap layer (shops) identity.
local ruleKeys={'define_as','type','subtype','does_block_move','block_sight','block_sense','block_esp','air_level','dig','is_door',
	'door_opened','door_closed','change_level','change_zone','change_level_check','force_down','notice','always_remember','special','pass_projectile'}
local function fn(v)
	if type(v)~='function' then return tostring(v) end
	local i=debug.getinfo(v,'S');return 'fn@'..tostring(i and i.short_src)..':'..tostring(i and i.linedefined)
end
function M.rules()
	local m=game.level.map
	local parts,n={},0
	for x=0,m.w-1 do for y=0,m.h-1 do
		local g=m(x,y,Map.TERRAIN)
		if g then
			local row={}
			for _,k in ipairs(ruleKeys) do row[#row+1]=fn(g[k]) end
			local cp={};for k,v in pairs(g.can_pass or {}) do cp[#cp+1]=k..'='..tostring(v) end;table.sort(cp)
			row[#row+1]=table.concat(cp,',')
			for _,k in ipairs{'on_stand','on_move','block_move','on_dig','combatAttack'} do row[#row+1]=fn(rawget(g,k) or g[k]) end
			local t=m(x,y,Map.TRAP)
			if t then row[#row+1]='trap:'..tostring(t.name)..':'..tostring(t.image)..':'..tostring(t.z)..':'..fn(t.block_move) end
			parts[#parts+1]=table.concat(row,'|');n=n+1
		end
	end end
	local s=table.concat(parts,'\n')
	local h=0
	for i=1,#s do h=(h*31+s:byte(i))%4294967296 end
	return {cells=n,hash=h,length=#s}
end
return M
