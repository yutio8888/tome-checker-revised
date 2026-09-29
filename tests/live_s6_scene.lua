-- Offline fixture only (S6: Eruan L1-3, Gorbat Pride L1-3). Reuses the S5
-- scene module (stats, identity probe, rule digest, per-kind board/native
-- counts, native listing, fixed poses, weather/particle quieting, native-FOV
-- walk) and adds the S6 families to the pixel sampler and the lit-pixel
-- pairs: board sand next to a board palm, mountain, bamboo hut wall or stone
-- wall; board sand/grass next to board deep water. A read-only palm probe
-- lists every palm cell with its native rules and board state. Never edits a
-- grid rule field; actors near the photographed window are removed.
local Map=require 'engine.Map'
local Terrain=require 'mod.class.CheckerTerrain'
local tw=dofile('/data-checker-fixture/monster-live_s5_scene.lua')
local M=setmetatable({},{__index=tw})

local function owned(g)
	local s=g and g._checker_terrain
	return s and g.replace_display==s.display and true or false
end
local function s6Family(m,x,y)
	local g=m(x,y,Map.TERRAIN)
	if not owned(g) then return end
	local img=g.replace_display.image or ''
	if img:match('/eruan/palm') then return 'palm' end
	if img:match('/beach/sand') then return 'sand' end
	if img:match('/daikara/mountain%-wall') or img:match('/caldera/wall') then return 'mountain' end
	if img:match('/bamboo/wall') then return 'hut-wall' end
	if img:match('/bamboo/door%-closed') then return 'hut-door' end
	if img:match('/bamboo/door%-open') then return 'hut-door-open' end
	if img:match('/bamboo/floor') then return 'hut-floor' end
end
function M.family(m,x,y) return s6Family(m,x,y) or tw.family(m,x,y) end
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
local FLOORS={grass=true,sand=true,['stone-floor']=true,['hut-floor']=true}
local WALLS={palm=true,mountain=true,['hut-wall']=true,['stone-wall']=true,['stone-old-wall']=true,tree=true}
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
				local water=nf=='water'
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
-- Every palm cell: native rules (move, sight, sense, ESP, pass_tree, dig)
-- and board state; plus whether it borders deep water. Read only.
function M.palms()
	local m=game.level.map
	local zoneName=game.zone.short_name
	local out={n=0,board=0,native=0,by_rules={},next_to_deep=0,cells={}}
	for x=0,m.w-1 do for y=0,m.h-1 do
		local g=m(x,y,Map.TERRAIN)
		local id=g and g.define_as
		if type(id)=='string' and id:match('^PALMTREE%d*$') then
			out.n=out.n+1
			local b=owned(g)
			if b then out.board=out.board+1 else out.native=out.native+1 end
			local key=('move=%s sight=%s sense=%s esp=%s pass_tree=%s dig=%s'):format(tostring(g.does_block_move),
				tostring(g.block_sight),tostring(g.block_sense),tostring(g.block_esp),tostring(g.can_pass and g.can_pass.pass_tree),tostring(g.dig))
			out.by_rules[key]=(out.by_rules[key] or 0)+1
			local deep=false
			for _,d in ipairs{{0,-1},{1,0},{0,1},{-1,0}} do
				local n=m(x+d[1],y+d[2],Map.TERRAIN)
				if n and n.define_as=='DEEP_OCEAN_WATER' or n and n.define_as=='DEEP_WATER' then deep=true end
			end
			if deep then out.next_to_deep=out.next_to_deep+1 end
			if #out.cells<6 then out.cells[#out.cells+1]={x,y,id,b,Terrain.batch4Kind(g,zoneName) or false} end
		end
	end end
	return out
end
-- Structural layer shapes per grid id (read only): for every cell, the
-- define_as plus each add_displays entry's image/z/offsets/scale/shader and
-- nested add_mos images, and the grid's own add_mos. Distinct shapes counted.
local function shape(g)
	local parts={}
	local function mos(list)
		local t={}
		for _,mo in ipairs(list or {}) do
			local keys={}
			for k in pairs(mo) do keys[#keys+1]=tostring(k) end
			table.sort(keys)
			t[#t+1]=tostring(mo.image)..'{'..table.concat(keys,',')..'}'
		end
		return table.concat(t,'+')
	end
	for i,d in ipairs(g.add_displays or {}) do
		local img=tostring(d.image):gsub('%d+%.png$','N.png')
		parts[#parts+1]=('%s z=%s x=%s y=%s h=%s w=%s sc=%s sh=%s att=%s tint=%s mos=[%s] nd=%s'):format(img,tostring(d.z),
			d.display_x and 'v' or '-',d.display_y and (d.display_y==-1 and '-1' or 'v') or '-',tostring(d.display_h),tostring(d.display_w),
			d.display_scale and 'v' or '-',tostring(d.shader),tostring(d.shader_args and d.shader_args.attenuation),tostring(d.tint),mos(d.add_mos),tostring(d.add_displays and #d.add_displays))
	end
	return table.concat(parts,' | ')..' || own_mos=['..mos(g.add_mos)..']'
end
function M.shapes(pattern)
	local m=game.level.map
	local out={}
	for x=0,m.w-1 do for y=0,m.h-1 do
		local g=m(x,y,Map.TERRAIN)
		local id=g and tostring(g.define_as)
		if id and id:match(pattern) then
			local key=id:gsub('%d+$','#')..' :: '..shape(g)
			out[key]=(out[key] or 0)+1
		end
	end end
	return out
end
-- Full (non-function) field dump of up to n native palm cells and one
-- board palm, for identity diagnosis. Read only.
local function dumpv(v,depth)
	if type(v)~='table' then return type(v)=='function' and 'fn' or v end
	if depth>3 then return '<table>' end
	local out={}
	for k,x in pairs(v) do if type(k)~='string' or (k~='_mo' and k~='_last_mo' and k~='replace_display' and k~='_checker_terrain') then out[tostring(k)]=dumpv(x,depth+1) end end
	return out
end
function M.palmDump(n)
	local m=game.level.map
	local out={native={},board={}}
	for x=0,m.w-1 do for y=0,m.h-1 do
		local g=m(x,y,Map.TERRAIN)
		local id=g and g.define_as
		if type(id)=='string' and id:match('^PALMTREE%d*$') then
			local list=owned(g) and out.board or out.native
			if #list<(owned(g) and 1 or n) then list[#list+1]={x=x,y=y,fields=dumpv(g,0)} end
		end
	end end
	return out
end
-- A photographed window chosen from the generated level (read only):
-- 'grove' = most palms plus palms beside deep water plus exits; 'roost' =
-- most bamboo roost walls/doors; 'gate' = the loose rock door. Returns the
-- window centre (21x13 cells, the 64px 1920x1080 view).
function M.autoPose(kind)
	local m=game.level.map
	local function id(x,y) local g=m(x,y,Map.TERRAIN);return g and tostring(g.define_as) or '' end
	local function score(x,y)
		local i=id(x,y)
		if kind=='grove' then
			if i:match('^PALMTREE') then
				local s=1
				for _,d in ipairs{{0,-1},{1,0},{0,1},{-1,0}} do if id(x+d[1],y+d[2]):match('DEEP') then s=s+4 end end
				return s
			end
			if i:match('^SAND_UP') or i:match('^SAND_DOWN') then return 12 end
			if i:match('DEEP') then return .5 end
		elseif kind=='roost' then
			if i:match('^FENCE_DOOR') then return 6 end
			if i:match('^BHW_') or i=='FENCE_WALL' then return 1 end
		elseif kind=='gate' then
			if i=='ROCK_DOOR' then return 100 end
			if i=='ROCK_LEVER_DOOR' or i:match('^GENERIC_LEVER') then return 20 end
		end
		return 0
	end
	local best,bx,by=-1,math.floor(m.w/2),math.floor(m.h/2)
	for cx=10,m.w-11 do for cy=6,m.h-7 do
		local t=0
		for x=cx-10,cx+10 do for y=cy-6,cy+6 do t=t+score(x,y) end end
		if t>best then best,bx,by=t,cx,cy end
	end end
	return {x=bx,y=by,score=best}
end
-- Fixture only, display only: empty every on-screen message log (uiset
-- LogDisplay objects) before a toggle comparison, so fading item-icon lines
-- in the log overlay do not enter the terrain frame diff.
function M.clearLog()
	local n=0
	for _,host in ipairs{game.uiset or {},game} do
		for _,v in pairs(host) do
			if type(v)=='table' and type(v.empty)=='function' and type(v.log)=='table' then v:empty();n=n+1 end
		end
	end
	return {cleared=n}
end
return M
