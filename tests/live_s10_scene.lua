-- Offline fixture only (S10a: Grushnak Pride L1-3, Slime Tunnels, Sludgenest
-- L1-3). Reuses the S9 scene module (rule digest, poses, weather/particle
-- quieting, native listing) and adds: a per-level identity histogram (id,
-- S10 kind, stone kind, owner), families for the slime board art, a pose
-- picker by native ids (so the before and after phases pick the same
-- window), lit-pixel pairs between S10 floors and blockers, and a
-- fixture-only switch for Sludgenest's cosmetic colour pulse (zone
-- foreground) so toggle frames compare terrain only. Never edits a grid rule
-- field; actors near the photographed window are removed.
local Map=require 'engine.Map'
local Terrain=require 'mod.class.CheckerTerrain'
local tw=dofile('/data-checker-fixture/monster-live_s9_scene.lua')
local M=setmetatable({},{__index=tw})

local function owned(g)
	local s=g and g._checker_terrain
	return s and g.replace_display==s.display and true or false
end
local function painted(m,x,y)
	local r=m._checker_korpul and m._checker_korpul[x+y*m.w]
	if r and r.painted and r.file then return r end
end
local function s10Kind(g)
	return Terrain.s10Kind and g and Terrain.s10Kind(g,game.zone.short_name) or nil
end
local function s10Family(m,x,y)
	local g=m(x,y,Map.TERRAIN)
	if owned(g) then
		local img=g.replace_display.image or ''
		if img:match('/slime/wall') then return 'slime-wall' end
		if img:match('/slime/floor') or img:match('/slime/stairs') then return 'slime-floor' end
		if img:match('/slime/creep') then return 'creep' end
		if img:match('/slime/slimed%-wall') then return 'slimed-wall' end
		if img:match('/gloom/[%w]+/wall') then return 'mushroom' end
		if img:match('/gloom/[%w]+/floor') then return 'under-floor' end
		if img:match('/caldera/tree') then return 'jungle-tree' end
		if img:match('/caldera/floor') then return 'jungle-grass' end
		if img:match('/korpul/floor') then return 'stone-floor' end
	end
	return tw.family(m,x,y)
end
M.family=s10Family

-- Whole-level histogram by native id (trailing digits folded): count, S10
-- kind, stone kind, owner (board display, stone record, native), and zone
-- stamp. Read only.
function M.ids()
	local m=game.level.map
	local out={zone=game.zone.short_name,level=game.level.level,w=m.w,h=m.h,ids={},owner={board=0,stone=0,native=0}}
	for x=0,m.w-1 do for y=0,m.h-1 do
		local g=m(x,y,Map.TERRAIN)
		if g then
			local id=tostring(g.define_as or ('<'..tostring(g.name)..'>')):gsub('%d+$','#')
			local e=out.ids[id]
			if not e then e={n=0,board=0,stone=0,native=0,s10={},stone_kind={},stamp=0};out.ids[id]=e end
			e.n=e.n+1
			local k=s10Kind(g)
			if k then e.s10[k]=(e.s10[k] or 0)+1 end
			local c=Terrain.classify(g)
			if c then e.stone_kind[c]=(e.stone_kind[c] or 0)+1 end
			if g._checker_zone_source then e.stamp=e.stamp+1 end
			local o=owned(g) and 'board' or painted(m,x,y) and 'stone' or 'native'
			e[o]=e[o]+1;out.owner[o]=out.owner[o]+1
		end
	end end
	return out
end

-- Pose window picker by native ids only. 'slime': SLIME_WALL next to
-- SLIME_FLOOR; 'creep': UNDERGROUND_CREEP next to UNDERGROUND_FLOOR or
-- UNDERGROUND_TREE; 'barracks': WALL/HARDWALL/DOOR next to UNDERGROUND_FLOOR;
-- 'slimed': SLIMED_* wall next to a floor; 'jungle': JUNGLE_TREE next to
-- JUNGLE_GRASS or SLIME_FLOOR; 'stairs': the level's exits.
local EXIT={SLIME_UP=true,SLIME_DOWN=true,UP=true,DOWN=true,UP_WILDERNESS=true,SLIME_TUNNELS=true,UP_GRUSHNAK=true,
	JUNGLE_GRASS_UP_WILDERNESS=true}
function M.pick(kind)
	local m=game.level.map
	local function id(x,y)
		if x<0 or y<0 or x>=m.w or y>=m.h then return '' end
		local g=m(x,y,Map.TERRAIN)
		return g and type(g.define_as)=='string' and g.define_as or ''
	end
	local function role(i)
		if kind=='slime' then
			if i:match('^SLIME_WALL') then return 'wall' end
			if i:match('^SLIME_FLOOR') then return 'floor' end
		elseif kind=='creep' then
			if i:match('^UNDERGROUND_CREEP') then return 'wall' end
			if i:match('^UNDERGROUND_FLOOR') or i:match('^UNDERGROUND_TREE') then return 'floor' end
		elseif kind=='barracks' then
			if i:match('^WALL') or i:match('^HARDWALL') or i:match('^DOOR') then return 'wall' end
			if i:match('^UNDERGROUND_FLOOR') or i=='FLOOR' then return 'floor' end
		elseif kind=='slimed' then
			if i:match('^SLIMED_WALL') or i:match('^SLIMED_HARDWALL') or i:match('^SLIMED_DOOR') then return 'wall' end
			if i=='SLIMED_FLOOR' or i:match('^UNDERGROUND_FLOOR') or i=='FLOOR' then return 'floor' end
		elseif kind=='jungle' then
			if i:match('^JUNGLE_TREE') then return 'wall' end
			if i:match('^JUNGLE_GRASS') or i:match('^SLIME_FLOOR') then return 'floor' end
		elseif kind=='stairs' then
			if EXIT[i] then return 'wall' end
			return 'floor'
		end
	end
	local cells={}
	for x=0,m.w-1 do for y=0,m.h-1 do
		if role(id(x,y))=='wall' then
			local s=kind=='stairs' and 40 or 0
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

-- Lit-pixel pairs: a visible free S10 floor next to a visible S10 blocker.
local FLOORS={['slime-floor']=true,creep=true,['under-floor']=true,['jungle-grass']=true,['stone-floor']=true}
local WALLS={['slime-wall']=true,['slimed-wall']=true,mushroom=true,['jungle-tree']=true,brick=true,hardwall=true,door=true}
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
		local f=s10Family(m,x,y)
		if FLOORS[f] and Terrain.visible(m,x,y) and clear(x,y) then
			for _,d in ipairs{{0,-1},{1,0},{0,1},{-1,0}} do
				local nx,ny=x+d[1],y+d[2]
				local nf=s10Family(m,nx,ny)
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

-- Sludgenest L2/L3 pulse the map's shown/obscure colours from the zone
-- foreground (zone.lua:151-166, run from level.data by Game.lua:1897).
-- Fixture only, display only: hold it at its tick-0 value (sr,sg,sb = 4,3,3
-- normalised) while photographing a toggle so its frames compare terrain
-- only, then give back the foreground and the colours it found.
local savedForeground,savedColours
function M.pulse(on)
	local data,m=game.level.data,game.level.map
	if not on then
		if data.foreground and not savedForeground then
			savedForeground=data.foreground;data.foreground=nil
			savedColours={shown={unpack(m.color_shown or {1,1,1,1})},obscure={unpack(m.color_obscure or {0.6,0.6,0.6,1})}}
			-- Level 1 returns before tinting (zone.lua:153); only L2/L3 pulse.
			if game.zone.short_name=='sludgenest' and game.level.level~=1 then
				m:setShown(1,.75,.75,1);m:setObscure(.6,.45,.45,1)
			end
		end
	elseif savedForeground then
		data.foreground=savedForeground;savedForeground=nil
		m:setShown(unpack(savedColours.shown));m:setObscure(unpack(savedColours.obscure));savedColours=nil
	end
	return {held=savedForeground~=nil,level=game.level.level}
end

-- Native listing with the S10 kind instead of the High Peak cave kind.
function M.natives()
	local out=tw.natives()
	local m=game.level.map
	for key,b in pairs(out.groups) do
		local x,y=b.sample[1][1],b.sample[1][2]
		b.cave_kind=nil
		b.s10_kind=s10Kind(m(x,y,Map.TERRAIN)) or false
	end
	return out
end
-- Distinct native display shapes and rule summaries per folded id (survey:
-- the facts the S10 contracts pin). Read only.
function M.layerSets()
	local m=game.level.map
	local out={}
	local function fn(v)
		local i=debug.getinfo(v,'S')
		return tostring(i and i.short_src)..':'..tostring(i and i.linedefined)
	end
	local function lay(t,pre)
		local parts={}
		for _,mo in ipairs(t.add_mos or {}) do parts[#parts+1]=pre..'m:'..tostring(mo.image)..'@'..tostring(mo.display_x)..','..tostring(mo.display_y) end
		for _,d in ipairs(t.add_displays or {}) do
			parts[#parts+1]=pre..'d:'..tostring(d.image)..'@z'..tostring(d.z)..','..tostring(d.display_x)..','..tostring(d.display_y)..','..tostring(d.display_h)
			for _,p in ipairs(lay(d,pre..'  ')) do parts[#parts+1]=p end
		end
		return parts
	end
	for x=0,m.w-1 do for y=0,m.h-1 do
		local g=m(x,y,Map.TERRAIN)
		if g then
			local id=tostring(g.define_as or ('<'..tostring(g.name)..'>')):gsub('%d+$','#')
			local e=out[id]
			if not e then
				local funcs={}
				for k,v in pairs(g) do if type(v)=='function' then funcs[#funcs+1]=k..'@'..fn(v) end end
				table.sort(funcs)
				local cp={};for k,v in pairs(g.can_pass or {}) do cp[#cp+1]=k..'='..tostring(v) end
				e={n=0,shapes={},nshapes=0,rules={type=g.type,subtype=g.subtype,name=g.name,display=g.display,
					block_move=g.does_block_move,sight=g.block_sight,sense=g.block_sense,esp=g.block_esp,air=g.air_level,
					dig=g.dig,grow=g.grow,is_door=g.is_door,opened=g.door_opened,closed=g.door_closed,z=g.z,
					notice=g.notice,remember=g.always_remember,change_level=g.change_level,change_zone=g.change_zone,
					force_down=g.force_down,special=g.special,pass_projectile=g.pass_projectile,can_pass=table.concat(cp,','),
					functions=table.concat(funcs,' '),shader=g.shader and tostring(g.shader) or nil,
					stamps={}}}
				for k,v in pairs(g) do if type(k)=='string' and k:match('^_checker_') then e.rules.stamps[#e.rules.stamps+1]=k end end
				out[id]=e
			end
			e.n=e.n+1
			local key=tostring(g.image)..' || '..table.concat(lay(g,''),' | ')
			if not e.shapes[key] then
				e.nshapes=e.nshapes+1
				if e.nshapes<=40 then e.shapes[key]={n=0,at={x,y}} end
			end
			if e.shapes[key] then e.shapes[key].n=e.shapes[key].n+1 end
		end
	end end
	return out
end
return M
