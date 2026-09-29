-- Offline fixture only (S9: High Peak L1-11). Reuses the S8 scene module
-- (identity counts, rule digest, poses, weather/particle quieting, native-FOV
-- walk, dark-set switch) and adds the High Peak families: board cave floor,
-- wall and up-ladder (L1-4, tw4.hpCave), board stone and stairs (L5-11); a
-- per-level listing of every cell still native with the reason facts; pose
-- pickers for a cave wall line, a stone wall line, the next-level stairs and
-- the Sanctum's portals; and lit-pixel pairs including the cave family.
-- Never edits a grid rule field; actors near the photographed window are
-- removed.
local Map=require 'engine.Map'
local Terrain=require 'mod.class.CheckerTerrain'
local tw=dofile('/data-checker-fixture/monster-live_s8_scene.lua')
local M=setmetatable({},{__index=tw})

local function owned(g)
	local s=g and g._checker_terrain
	return s and g.replace_display==s.display and true or false
end
local function painted(m,x,y)
	local r=m._checker_korpul and m._checker_korpul[x+y*m.w]
	if r and r.painted and r.file then return r end
end
local function s9Family(m,x,y)
	local g=m(x,y,Map.TERRAIN)
	if owned(g) then
		local img=g.replace_display.image or ''
		if img:match('/cave/wall') then return 'cave-wall' end
		if img:match('/cave/floor') then return 'cave-floor' end
		if img:match('/cave/ladder') then return 'cave-exit' end
	end
	return tw.family(m,x,y)
end
M.family=s9Family

-- Identity and owner counts over the whole level: cave kinds (hpCave), stone
-- kinds (classify), and who draws each cell now (cave display, stone record,
-- native).
function M.hp()
	local m=game.level.map
	local out={zone=game.zone.short_name,level=game.level.level,w=m.w,h=m.h,cave={},stone={},owner={cave=0,stone=0,native=0},
		stamped=0,cells=0}
	for x=0,m.w-1 do for y=0,m.h-1 do
		local g=m(x,y,Map.TERRAIN)
		if g then
			out.cells=out.cells+1
			if g._checker_zone_source and g._checker_zone_source.file=='/data/zones/high-peak/grids.lua' then out.stamped=out.stamped+1 end
			local c=Terrain.hpCave and Terrain.hpCave(g)
			if c then out.cave[c]=(out.cave[c] or 0)+1 end
			local k=Terrain.classify(g)
			if k then out.stone[k]=(out.stone[k] or 0)+1 end
			if owned(g) then out.owner.cave=out.owner.cave+1
			elseif painted(m,x,y) then out.owner.stone=out.owner.stone+1
			else out.owner.native=out.owner.native+1 end
		end
	end end
	return out
end

-- Every cell not drawn by the board right now, grouped by id, with the facts
-- that decide why (callbacks, transitions, layers, adapter kinds, stamp).
function M.natives()
	local m=game.level.map
	local out={zone=game.zone.short_name,level=game.level.level,groups={}}
	for x=0,m.w-1 do for y=0,m.h-1 do
		local g=m(x,y,Map.TERRAIN)
		if g and not owned(g) and not painted(m,x,y) then
			local funcs={}
			for k,v in pairs(g) do if type(v)=='function' then funcs[#funcs+1]=k end end
			table.sort(funcs)
			local key=tostring(g.define_as or ('<'..tostring(g.name)..'>'))
			local b=out.groups[key]
			if not b then
				local ls={}
				for _,d in ipairs(g.add_displays or {}) do ls[#ls+1]='d:'..tostring(d.image) end
				for _,mo in ipairs(g.add_mos or {}) do ls[#ls+1]='m:'..tostring(mo.image) end
				b={n=0,name=g.name,type=g.type or false,subtype=g.subtype or false,image=g.image or false,
					functions=table.concat(funcs,','),change_level=g.change_level or false,change_zone=g.change_zone or false,
					does_block_move=g.does_block_move and true or false,block_sight=g.block_sight and true or false,
					cave_kind=Terrain.hpCave and Terrain.hpCave(g) or false,stone_kind=Terrain.classify(g) or false,
					zone_stamp=g._checker_zone_source and true or false,layers=ls,
					visible=0,remembered=0,unknown=0,sample={}}
				out.groups[key]=b
			end
			b.n=b.n+1
			if Terrain.visible(m,x,y) then b.visible=b.visible+1 elseif m.remembers(x,y) then b.remembered=b.remembered+1 else b.unknown=b.unknown+1 end
			if #b.sample<4 then b.sample[#b.sample+1]={x,y} end
		end
	end end
	return out
end

-- Pose window picker by identity only (works before anything is seen).
-- 'cave': most cave floor/cave wall contacts; 'wall': S8 stone wall line;
-- 'stairs': the level's way to the next level (either High Peak stair,
-- or PORTAL_BOSS on L10); 'sanctum': the Sanctum's centre.
function M.pick(kind)
	local m=game.level.map
	if kind=='sanctum' then return {found=true,kind=kind,x=25,y=11} end
	if kind=='stairs' then
		for x=0,m.w-1 do for y=0,m.h-1 do
			local g=m(x,y,Map.TERRAIN)
			local id=g and g.define_as
			if id=='HIGH_PEAK_UP' or id=='CAVE_HIGH_PEAK_UP' or id=='PORTAL_BOSS' then return {found=true,kind=kind,x=x,y=y,id=id} end
		end end
		return {found=false,kind=kind}
	end
	-- Native ids only, so the before (pre-S9) and after phases pick the same
	-- window: 'cave' = CAVEWALL next to CAVEFLOOR*, 'wall' = diggable basic
	-- WALL* next to FLOOR (doors score too).
	local function k(x,y)
		if x<0 or y<0 or x>=m.w or y>=m.h then return end
		local id=m(x,y,Map.TERRAIN) and m(x,y,Map.TERRAIN).define_as
		if type(id)~='string' then return end
		if kind=='cave' then
			if id=='CAVEWALL' then return 'wall' end
			if id:match('^CAVEFLOOR%d*$') then return 'floor' end
		else
			if id:match('^WALL') then return 'wall' end
			if id=='FLOOR' or id:match('^DOOR') then return 'floor' end
		end
	end
	local cells={}
	for x=0,m.w-1 do for y=0,m.h-1 do
		if k(x,y)=='wall' then
			local s=0
			for _,d in ipairs{{0,-1},{1,0},{0,1},{-1,0}} do if k(x+d[1],y+d[2])=='floor' then s=s+1 end end
			if s>0 then cells[#cells+1]={x,y,s} end
		end
	end end
	local best,bx,by=0,nil,nil
	for cx=4,m.w-5,2 do for cy=3,m.h-4,2 do
		local t=0
		for _,c in ipairs(cells) do if math.abs(c[1]-cx)<=4 and math.abs(c[2]-cy)<=3 then t=t+c[3] end end
		if t>best then best,bx,by=t,cx,cy end
	end end
	if not bx then return {found=false,kind=kind} end
	return {found=true,kind=kind,x=bx,y=by,score=best}
end

-- Lit-pixel pairs: a visible free board floor (cave or stone) next to a
-- visible board blocking cell (cave wall, brick, hard wall, door).
local FLOORS={['cave-floor']=true,['stone-floor']=true}
local WALLS={['cave-wall']=true,brick=true,hardwall=true,door=true}
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
		local f=s9Family(m,x,y)
		if FLOORS[f] and Terrain.visible(m,x,y) and clear(x,y) then
			for _,d in ipairs{{0,-1},{1,0},{0,1},{-1,0}} do
				local nx,ny=x+d[1],y+d[2]
				local nf=s9Family(m,nx,ny)
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
-- Rule digest as tw.rules(), except that the defining line of the addon's own
-- Grid.block_move superload (display-only door repaint, moved by S9's added
-- stamp lines) is not part of the text: the same function in both packages.
function M.rulesNorm()
	local m=game.level.map
	local keys={'define_as','type','subtype','does_block_move','block_sight','block_sense','block_esp','air_level','dig','is_door',
		'door_opened','door_closed','change_level','change_zone','change_level_check','force_down','notice','always_remember','special','pass_projectile'}
	local function fn(v)
		if type(v)~='function' then return tostring(v) end
		local i=debug.getinfo(v,'S')
		local src=tostring(i and i.source)
		if src:match('superload/mod/class/Grid%.lua$') then return 'fn@checker-Grid-superload' end
		return 'fn@'..src..':'..tostring(i and i.linedefined)
	end
	local parts,n={},0
	for x=0,m.w-1 do for y=0,m.h-1 do
		local g=m(x,y,Map.TERRAIN)
		if g then
			local row={}
			for _,k in ipairs(keys) do row[#row+1]=fn(g[k]) end
			local cp={};for k,v in pairs(g.can_pass or {}) do cp[#cp+1]=k..'='..tostring(v) end;table.sort(cp)
			row[#row+1]=table.concat(cp,',')
			for _,k in ipairs{'on_stand','on_move','block_move','on_dig','combatAttack'} do row[#row+1]=fn(rawget(g,k) or g[k]) end
			parts[#parts+1]=table.concat(row,'|');n=n+1
		end
	end end
	local s=table.concat(parts,'\n')
	local h=0
	for i=1,#s do h=(h*31+s:byte(i))%4294967296 end
	return {cells=n,hash=h,length=#s,rows=M.keepRows and parts or nil}
end
return M
