-- Offline fixture only (S11: levers, lever doors and Vor's candles). Reuses
-- the S10b scene module (rule digest, poses, quieting, native listing, layer
-- survey) and adds: a full per-cell dump of every lever, lever door and candle
-- (all own fields, callbacks with file:line, layers, stamps, lever attrs,
-- owner, board image), the lever -> door links, a real lever pull (the player
-- steps next to the lever and bumps it: Actor:move -> the native block_move
-- with act=true), a view that only recentres (no forced updateMap pass, so a
-- missing repaint stays visible), a fixture-only switch that disables the S11
-- lever repaint probe to show the native behaviour, and candle particle state.
-- Never edits a grid rule field; lever state changes only through the pull.
local Map=require 'engine.Map'
local Terrain=require 'mod.class.CheckerTerrain'
local tw=dofile('/data-checker-fixture/monster-live_s10b_scene.lua')
local M=setmetatable({},{__index=tw})

local function fn(v)
	local i=debug.getinfo(v,'S')
	return tostring(i and i.source)..':'..tostring(i and i.linedefined)
end
local function ser(v,depth)
	local t=type(v)
	if t=='function' then return 'fn:'..fn(v) end
	if t~='table' then return t..':'..tostring(v) end
	if (depth or 0)>5 then return 'deep' end
	local keys={}
	for k in pairs(v) do if type(k)~='string' or (k:sub(1,1)~='_' and k~='uid' and k~='changed') then keys[#keys+1]=k end end
	table.sort(keys,function(a,b) return tostring(a)<tostring(b) end)
	local out={}
	for _,k in ipairs(keys) do out[#out+1]=tostring(k)..'='..ser(v[k],(depth or 0)+1) end
	return '{'..table.concat(out,';')..'}'
end
local function owner(m,x,y,g)
	local st=g and rawget(g,'_checker_terrain')
	if st and g.replace_display==st.display then
		local d=g.replace_display
		local layers={}
		for _,l in ipairs(d.add_displays or {}) do layers[#layers+1]=tostring(l.image)..'@'..tostring(l.z) end
		return 'board',{image=d.image,layers=layers,lever=st.lever or false}
	end
	local r=m._checker_korpul and m._checker_korpul[x+y*m.w]
	if r and r.painted and r.file then
		return 'stone',{kind=r.kind,file=r.file,overlay=r.overlay or false,prop=r.prop and r.prop.image or false,
			orientation=r.orientation or false}
	end
	if r then return 'record',{kind=r.kind,file=r.file or false,painted=r.painted or false} end
	return 'native'
end
local ATTRS={'lever','lever_kind','lever_radius','lever_spot','lever_block','lever_only_once','lever_action',
	'lever_action_value','lever_action_kind','lever_toggle','lever_action_only_once','lever_action_custom'}
function M.cell(x,y)
	local m=game.level.map
	local g=m(x,y,Map.TERRAIN)
	if not g then return {x=x,y=y,empty=true} end
	local keys,funcs,stamps={}, {}, {}
	for k,v in pairs(g) do
		if type(k)=='string' and k:match('^_checker_') then stamps[k]=ser(v)
		elseif type(v)=='function' then funcs[#funcs+1]=k..'@'..fn(v)
		elseif type(k)~='string' or (k:sub(1,1)~='_' and k~='uid' and k~='changed') then keys[tostring(k)]=ser(v) end
	end
	table.sort(funcs)
	local attrs={}
	for _,k in ipairs(ATTRS) do local v=m.attrs(x,y,k);if v~=nil then attrs[k]=ser(v) end end
	local who,info=owner(m,x,y,g)
	local ps={}
	for p in pairs(rawget(g,'__particles') or {}) do
		ps[#ps+1]={name=p.def and tostring(p.def) or false,alive=p.ps and p.ps:isAlive() and true or false}
	end
	local kind,extra=Terrain.s11Kind and Terrain.s11Kind(g,game.zone.short_name)
	local stone,so=Terrain.classify(g)
	return {x=x,y=y,id=g.define_as or false,keys=keys,funcs=table.concat(funcs,' '),stamps=stamps,attrs=attrs,
		owner=who,board=info or false,s11=kind or false,stone=stone or false,stone_o=type(so)=='string' and so or false,
		particles=ps,visible=Terrain.visible(m,x,y),remembered=m.remembers(x,y) and true or false}
end
local function interesting(g)
	local id=g and type(g.define_as)=='string' and g.define_as or ''
	return id:match('LEVER') or id:match('^CANDLE') or (g and (rawget(g,'on_lever_change') or rawget(g,'embed_particles')))
end
-- Every lever, lever door and candle of the level, plus any cell carrying a
-- lever attr (a door's spot after it opened into another grid).
function M.s11cells()
	local m=game.level.map
	local out={zone=game.zone.short_name,level=game.level.level,cells={},ids={}}
	for x=0,m.w-1 do for y=0,m.h-1 do
		local g=m(x,y,Map.TERRAIN)
		if interesting(g) or m.attrs(x,y,'lever_action_kind') or m.attrs(x,y,'lever') then
			local c=M.cell(x,y)
			out.cells[#out.cells+1]=c
			local id=tostring(c.id)
			local e=out.ids[id] or {n=0,owner={}}
			e.n=e.n+1;e.owner[c.owner]=(e.owner[c.owner] or 0)+1
			out.ids[id]=e
		end
	end end
	return out
end
local function free(m,x,y)
	if x<0 or y<0 or x>=m.w or y>=m.h then return false end
	local g=m(x,y,Map.TERRAIN)
	return g and not m:checkAllEntities(x,y,'block_move') and not m(x,y,Map.ACTOR) and true or false
end
-- Cells a lever acts on: its spot's cell or the lever_action_kind cells in
-- its radius (read from map attrs only; nothing is changed).
function M.links(x,y)
	local m=game.level.map
	local kind=m.attrs(x,y,'lever_kind')
	if type(kind)=='string' then kind={[kind]=true} end
	local out={}
	for i=0,m.w-1 do for j=0,m.h-1 do
		local ak=m.attrs(i,j,'lever_action_kind')
		if type(ak)=='string' then ak={[ak]=true} end
		if type(ak)=='table' and type(kind)=='table' then
			for k in pairs(kind) do if ak[k] then out[#out+1]={i,j};break end end
		end
	end end
	return out
end
-- All levers of the level with their links.
function M.levers()
	local m=game.level.map
	local out={}
	for x=0,m.w-1 do for y=0,m.h-1 do
		local g=m(x,y,Map.TERRAIN)
		if g and g.type=='lever' then out[#out+1]={x=x,y=y,id=g.define_as or false,links=M.links(x,y)} end
	end end
	return out
end
-- The real pull: stand on a free neighbour, then bump the lever (the native
-- Actor:move -> map:checkAllEntities(x,y,'block_move',player,true) path).
function M.pull(x,y)
	local m,p=game.level.map,game.player
	local stand
	for _,d in ipairs{{0,1},{-1,0},{1,0},{0,-1},{1,1},{-1,1},{1,-1},{-1,-1}} do
		if not stand and free(m,x+d[1],y+d[2]) then stand={x+d[1],y+d[2]} end
	end
	assert(stand,'no stand cell next to the lever')
	if p.x~=stand[1] or p.y~=stand[2] then p:move(stand[1],stand[2],true) end
	local links=M.links(x,y)
	local before={lever=M.cell(x,y),links={}}
	for _,l in ipairs(links) do before.links[#before.links+1]=M.cell(l[1],l[2]) end
	local g=m(x,y,Map.TERRAIN)
	local moved=p:move(x,y)
	local after={lever=M.cell(x,y),links={}}
	for _,l in ipairs(links) do after.links[#after.links+1]=M.cell(l[1],l[2]) end
	return {x=x,y=y,stand=stand,player={p.x,p.y},moved=moved and true or false,same_grid=m(x,y,Map.TERRAIN)==g,
		before=before,after=after}
end
-- Recentre only: no forced updateMap pass over the level (a stale display
-- stays stale). The player's own FOV pass still runs, as after any action.
function M.look(cx,cy)
	local m,p=game.level.map,game.player
	m.smooth_scroll=0;m:centerViewAround(cx,cy);m.changed=true;core.display.forceRedraw()
	return {player={p.x,p.y}}
end
-- Fixture only: disable/restore the S11 lever and lever-door repaint probes
-- (shows what the native swap does to the board display without them).
local savedStale,savedChanged
function M.probe(on)
	if not on and not savedStale then
		savedStale,savedChanged=Terrain.s11Stale,Terrain.s11Changed
		Terrain.s11Stale=function() return false end;Terrain.s11Changed=function() end
	elseif on and savedStale then
		Terrain.s11Stale,Terrain.s11Changed=savedStale,savedChanged;savedStale,savedChanged=nil,nil
	end
	return {disabled=savedStale~=nil}
end
-- Fixture only, display only: stop/restart the candles' embedded particle
-- emitters around a pixel comparison (their flicker is not terrain).
local hidden
function M.candles(on)
	local m=game.level.map
	if not on then
		hidden={}
		for x=0,m.w-1 do for y=0,m.h-1 do
			local g=m(x,y,Map.TERRAIN)
			if g and rawget(g,'__particles') and next(g.__particles) then
				hidden[#hidden+1]={x,y,g.__particles};g.__particles={};m:updateMap(x,y)
			end
		end end
		return {hidden=#hidden}
	end
	local n=0
	-- By position: a mode switch in between may have installed a fresh clone.
	for _,h in ipairs(hidden or {}) do
		local g=m(h[1],h[2],Map.TERRAIN)
		if g and not next(g.__particles or {}) then g.__particles=h[3];n=n+1 end
	end
	hidden=nil
	for x=0,m.w-1 do for y=0,m.h-1 do m:updateMap(x,y) end end
	return {restored=n}
end
-- Screen rectangle of a cell (for crops).
function M.screen(x,y)
	local m=game.level.map
	local sx,sy=m:getTileToScreen(x,y)
	return {x=x,y=y,sx=sx,sy=sy,tile=m.tile_w*m.zoom}
end
return M
