-- Offline fixture only. Live check of monster batch A/B tokens (2026-09-29).
-- Requires the map survey module loaded as global `ms` (ms.enter handles the
-- native zone/layout switch). Natural actors are only inspected; the camera
-- and hero may be moved next to them for a picture. Placed actors come from
-- the zone's own npc_list (or an exact native list file) and are flagged
-- `_checker_live_placed` so the census can never report them as natural.
local Map=require 'engine.Map'
local Tokens=require 'mod.class.CheckerTokens'
local M={}

local function guard()
	assert(require('mod.class.CheckerFixture').enabled() and not profile.auth)
	assert(config.settings.cheat)
end

local function mosSummary(mos)
	if type(mos)~='table' then return false end
	local out={}
	for k,mo in pairs(mos) do
		if type(mo)=='table' then
			out[#out+1]={key=tostring(k),image=mo.image or false,display_h=mo.display_h or false,
				display_y=mo.display_y or false,display_w=mo.display_w or false,
				aura=mo._isshaderaura and true or false}
		end
	end
	return out
end

local function row(a)
	pcall(function() game:checkerRefreshActor(a,'display') end)
	local state=a._checker_token
	local owned=state and state.display or nil
	local id,reason=Tokens.explain(a,owned,false)
	local m=game.level.map
	return {name=a.name or '?',define_as=a.define_as or false,unique=a.unique and tostring(a.unique) or false,
		type=a.type or false,subtype=a.subtype or false,image=a.image or false,add_mos=mosSummary(a.add_mos),
		moddable_tile=a.moddable_tile or false,rank=a.rank or false,faction=a.faction or false,
		size_category=a.size_category or false,
		reaction=game.player:reactionToward(a),
		identify=id or false,explain=reason or false,
		rendered_token=state and state.id or false,
		display_image=a.replace_display and a.replace_display.image or false,
		has_mo=a._mo and true or false,
		placed=a._checker_live_placed and true or false,
		x=a.x or false,y=a.y or false,
		seen=(a.x and m.seens(a.x,a.y)) and true or false,
		can_see=game.player:canSee(a) and true or false,
		life=a.life or false,max_life=a.max_life or false,
		screen=a.x and {math.floor(m.display_x+(a.x-m.mx)*m.tile_w),math.floor(m.display_y+(a.y-m.my)*m.tile_h),m.tile_w} or false}
end
M.row=row

-- All actors whose exact name is in `names` (a set), plus a compact census.
function M.find(names)
	guard()
	local rows={}
	for _,a in pairs(game.level.entities) do
		if a.x and a~=game.player and (not names or names[a.name]) then rows[#rows+1]=row(a) end
	end
	table.sort(rows,function(p,q) return p.name<q.name end)
	return rows
end

local function score(u) return (u._checker_live_placed and 2 or 0)+(u._checker_live_pick and 1 or 0) end
local function byName(name)
	local best
	for _,a in pairs(game.level.entities) do
		if a.x and a.name==name and a~=game.player then
			-- Prefer placed actors, then the natural actor last approached.
			if not best or score(a)>score(best) then best=a end
		end
	end
	return best
end
M.byName=byName

local function free(x,y)
	local m=game.level.map
	return x>=0 and y>=0 and x<m.w and y<m.h and not m(x,y,Map.ACTOR)
		and not m:checkEntity(x,y,Map.TERRAIN,'block_move',game.player)
		and not m:checkEntity(x,y,Map.TERRAIN,'change_level')
end

local function refresh()
	local m=game.level.map
	for _,a in pairs(game.level.entities) do if a.ai then a.never_act=true end end
	game.player.invulnerable=1
	m.clean_fov=true;game.player:playerFOV()
	m.smooth_scroll=0;m:centerViewAround(game.player.x,game.player.y)
	m:redisplay();m.changed=true;game.paused=true;core.display.forceRedraw()
end
M.refresh=refresh

-- Move the hero next to the actor on an open, line-of-sight cell 2..4 away.
-- When several natural actors share the name, try each until one is visible
-- from an open cell (one may sit in a closed vault); that one is remembered.
local function approachCell(a)
	local p=game.player
	local best,bd
	for r=2,4 do
		for x=a.x-r,a.x+r do for y=a.y-r,a.y+r do
			if free(x,y) and (x~=a.x or y~=a.y) then
				local ok,lx,ly=p:hasLOS(a.x,a.y,'block_sight',10,x,y)
				ok=ok and lx==a.x and ly==a.y
				local d=math.abs(x-a.x)+math.abs(y-a.y)
				if ok and (not bd or d<bd) then best,bd={x,y},d end
			end
		end end
		if best then break end
	end
	return best
end
function M.approach(name)
	guard()
	local first=assert(byName(name),'no actor '..name)
	local list={first}
	for _,u in pairs(game.level.entities) do
		if u~=first and u.x and u.name==name and not u._checker_live_placed then list[#list+1]=u end
	end
	for _,a in ipairs(list) do
		local best=approachCell(a)
		if best then
			for _,u in ipairs(list) do u._checker_live_pick=nil end
			a._checker_live_pick=true
			game.player:move(best[1],best[2],true)
			refresh()
			return row(a)
		end
	end
	error('no open line-of-sight cell near '..name)
end

-- Place an exact native prototype next to the hero. `source` is nil (zone
-- npc_list) or a native npc list file loaded with the zone's npc class.
function M.place(name,source,dx,dy,define_as)
	guard()
	local proto
	if source then
		-- Zone npc files read the `currentZone` global (set only while a zone
		-- loads); expose the live zone (with is_invaded forced on so the Nashva branch of
		-- murgol-lair/npcs.lua is defined) for the duration of the native load.
		local had=rawget(_G,'currentZone');if not had then rawset(_G,'currentZone',setmetatable({is_invaded=true},{__index=game.zone})) end
		local okl,list=pcall(function() return game.zone.npc_class:loadList(source,true) end)
		if not had then rawset(_G,'currentZone',nil) end
		assert(okl,list)
		for _,p in pairs(list) do if type(p)=='table' and p.name==name and (not define_as or p.define_as==define_as) then proto=p break end end
	else
		for _,p in pairs(game.zone.npc_list) do if type(p)=='table' and p.name==name and (not define_as or p.define_as==define_as) then proto=p break end end
	end
	assert(proto,'no native prototype '..name)
	local a=game.zone:finishEntity(game.level,'actor',proto)
	assert(a.name==name)
	local p=game.player
	local tx,ty=p.x+(dx or 2),p.y+(dy or 0)
	local nx,ny,score
	for x=p.x-6,p.x+6 do for y=p.y-4,p.y+4 do
		if free(x,y) and game.level.map.seens(x,y) then
			local d=(x-tx)^2+(y-ty)^2
			if not score or d<score then nx,ny,score=x,y,d end
		end
	end end
	assert(nx,'no visible free cell for '..name)
	a._checker_live_placed=true
	a.seen_by=nil -- quest hooks (Kyless) need story state the isolated fixture does not have
	a.never_act=true
	game.zone:addEntity(game.level,a,'actor',nx,ny)
	refresh()
	return row(a)
end

function M.tokens(enabled)
	guard();game:checkerSetTokensEnabled(enabled);refresh()
end

-- Exact-cell helpers for packed layouts (the R33 standee crowd needs actors
-- directly above/below each other). freeAt/clearBox are read-only/removal;
-- placeAt asserts the cell is free so a broken layout fails loudly.
function M.freeAt(x,y)
	local m=game.level.map
	return x>=0 and y>=0 and x<m.w and y<m.h and free(x,y) and m.seens(x,y) and true or false
end

function M.clearBox(x0,y0,x1,y1)
	local rm={}
	for _,a in pairs(game.level.entities) do
		if a~=game.player and a.x and a.x>=x0 and a.x<=x1 and a.y>=y0 and a.y<=y1 then rm[#rm+1]=a end
	end
	for _,a in ipairs(rm) do game.level.map:remove(a.x,a.y,Map.ACTOR);game.level:removeEntity(a,true) end
	refresh()
	return #rm
end

-- Find a w x h block of free, visible cells centred as close to (cx,cy) as
-- possible; returns its centre or nil.
function M.freeBlock(cx,cy,w,h)
	local best,bd
	for x=cx-8,cx+8 do for y=cy-6,cy+6 do
		local ok=true
		for dx=-math.floor(w/2),math.ceil(w/2)-1 do for dy=-math.floor(h/2),math.ceil(h/2)-1 do
			if not M.freeAt(x+dx,y+dy) then ok=false break end
		end if not ok then break end end
		if ok then local d=(x-cx)^2+(y-cy)^2;if not bd or d<bd then best,bd={x,y},d end end
	end end
	return best
end

function M.placeAt(name,source,x,y,define_as)
	guard()
	local proto
	if source then
		local had=rawget(_G,'currentZone');if not had then rawset(_G,'currentZone',setmetatable({is_invaded=true},{__index=game.zone})) end
		local okl,list=pcall(function() return game.zone.npc_class:loadList(source,true) end)
		if not had then rawset(_G,'currentZone',nil) end
		assert(okl,list)
		for _,p in pairs(list) do if type(p)=='table' and p.name==name and (not define_as or p.define_as==define_as) then proto=p break end end
	else
		for _,p in pairs(game.zone.npc_list) do if type(p)=='table' and p.name==name and (not define_as or p.define_as==define_as) then proto=p break end end
	end
	assert(proto,'no native prototype '..name)
	assert(M.freeAt(x,y),'cell not free/visible for '..name..' at '..x..','..y)
	local a=game.zone:finishEntity(game.level,'actor',proto)
	a._checker_live_placed=true
	a.seen_by=nil
	a.never_act=true
	game.zone:addEntity(game.level,a,'actor',x,y)
	refresh()
	return row(a)
end

function M.focus(x,y)
	local m=game.level.map
	m.clean_fov=true;game.player:playerFOV()
	m.smooth_scroll=0;m:centerViewAround(x,y);m:redisplay();m.changed=true
	game.paused=true;core.display.forceRedraw()
end

function M.setTile(tile)
	game:setResolution('1920x1080 Windowed',true)
	config.settings.tome.gfx.size=tile..'x'..tile;game:setupDisplayMode(false)
	refresh()
end

-- R40 top-edge: make the named actor's own row the first visible map row. The
-- R39 attempt set m.my directly and then called redisplay(), which re-applied
-- checkMapViewBounded and clamped my back to the map bottom; the actor never
-- reached the top row. Move the actor to the highest free visible cell first,
-- then center and setScroll so the bounded my can equal its row (it cannot
-- scroll higher: the actor is on the top free row). Returns the geometry.
function M.forceTop(name)
	local a=assert(byName(name),name)
	local m=game.level.map
	local best,bx
	for y=0,m.h-1 do for x=0,m.w-1 do if free(x,y) and m.seens(x,y) then best,bx=y,x break end end
		if best then break end end
	assert(best,'no visible free cell for the top row')
	if a.x~=bx or a.y~=best then a:move(bx,best,true) end
	m:centerViewAround(a.x,a.y)
	m:setScroll(math.max(0,math.min(a.x,m.w-m.viewport.mwidth)),best)
	m:redisplay();m.changed=true;game.paused=true;core.display.forceRedraw()
	return {x=a.x,y=a.y,mx=m.mx,my=m.my,tile_w=m.tile_w,tile_h=m.tile_h,
		display_x=m.display_x,display_y=m.display_y,same_row=(m.my==a.y) and true or false,
		viewport_top=m.display_y,top_free_row=best}
end

-- Half the named actor's life so the health arc is partial.
function M.wound(name,frac)
	local a=assert(byName(name),name)
	a.life=math.max(1,math.floor(a.max_life*(frac or .5)))
	refresh()
	return row(a)
end

-- Temporary native invisibility on a token actor (fixture only; the hero has
-- no see_invisible). Returns the row; call again with off=true to restore.
function M.invisible(name,off)
	local a=assert(byName(name),name)
	if off then a:attr('invisible',a._checker_live_invis,true);a._checker_live_invis=nil
	else a._checker_live_invis=1000;a:attr('invisible',1000) end
	-- canSee results are cached per viewer; drop them so the change is observed.
	game.player:resetCanSeeCache();if a.resetCanSeeCacheOf then a:resetCanSeeCacheOf() end
	local m=game.level.map
	m:updateMap(a.x,a.y)
	refresh()
	return row(a)
end

-- Remove every non-hero actor within radius r of the hero (for clean lineups).
function M.clearAround(r)
	local p=game.player
	local rm={}
	for _,a in pairs(game.level.entities) do
		if a~=p and a.x and math.abs(a.x-p.x)<=r and math.abs(a.y-p.y)<=r then rm[#rm+1]=a end
	end
	for _,a in ipairs(rm) do game.level.map:remove(a.x,a.y,Map.ACTOR);game.level:removeEntity(a,true) end
	refresh()
	return #rm
end

return M
