-- Offline fixture only (S17: the Solipsist Dreamscape plane, entered and left
-- through the real talent/effect). Reuses the S16 scene module (enter, view,
-- rules, quieting, particle pause, log clear, viewport, actor-particle drop)
-- and adds: the per-id S17 kind histogram, fixture-only casting of Dreamscape
-- on the fixture hero (learned at level 1, resources and cooldowns ignored
-- through forceUseTalent's own flags) at a sleeping adjacent monster, leaving
-- through the native EFF_DREAMSCAPE deactivation, and freezing the plane's
-- time-varying foreground tint for toggle frames. Never edits a grid rule
-- field.
local Map=require 'engine.Map'
local Terrain=require 'mod.class.CheckerTerrain'
local tw=dofile('/data-checker-fixture/monster-live_s16_scene.lua')
local M=setmetatable({},{__index=tw})

local function id(g) return g and (type(g.define_as)=='string' and g.define_as or '<'..tostring(g.name)..'>') or '<none>' end
function M.cells()
	local m=game.level.map
	local z=game.zone.short_name
	local out={zone=z,level=game.level.level,w=m.w,h=m.h,ids={},board=0,total=0}
	for x=0,m.w-1 do for y=0,m.h-1 do
		local g=m(x,y,Map.TERRAIN)
		local e=out.ids[id(g)] or {n=0,kind={},board=0,images={}}
		e.n=e.n+1;out.total=out.total+1
		local k=g and Terrain.s17Kind and Terrain.s17Kind(g,z) or false
		e.kind[tostring(k)]=(e.kind[tostring(k)] or 0)+1
		local st=g and g._checker_terrain
		if st and g.replace_display==st.display then
			e.board=e.board+1;out.board=out.board+1
			local img=(g.replace_display.image or ''):match('refined/dream/(%a+%-%a)') or g.replace_display.image
			e.images[img]=(e.images[img] or 0)+1
		end
		out.ids[id(g)]=e
	end end
	return out
end
function M.where()
	local p=game.player
	return {zone=game.zone.short_name,level=game.level.level,x=p.x,y=p.y,checker_mode=game.checker_mode or false,
		dreamscape=p:hasEffect(p.EFF_DREAMSCAPE) and true or false}
end
function M.learnDream()
	local p=game.player
	if not p:knowTalent(p.T_DREAMSCAPE) then p:learnTalent(p.T_DREAMSCAPE,true,1) end
	return {dreamscape=p:knowTalent(p.T_DREAMSCAPE),game_ender=p.game_ender and true or false}
end
-- Dreamscape needs a sleeping hostile non-summon target in range: the nearest
-- one is moved (fixture only) next to the hero and put to sleep (the native
-- EFF_SLEEP, no Insomnia on wake). Done before the source frames, so the
-- source level looks the same before the cast and after the return.
local target
function M.prepareDream()
	local p=game.player
	local best,bd
	for _,a in pairs(game.level.entities) do
		if a~=p and a.x and a.ai and not a.summoner and not a.summon_time and not a.dead and
		 not a:attr('negative_status_effect_immune') and not a:attr('status_effect_immune') and a:canBe('planechange') and
		 p:reactionToward(a)<0 then
			local d=core.fov.distance(p.x,p.y,a.x,a.y)
			if not bd or d<bd then best,bd=a,d end
		end
	end
	assert(best,'no Dreamscape target')
	local x,y
	for _,d in ipairs{{1,0},{-1,0},{0,1},{0,-1},{1,1},{-1,1},{1,-1},{-1,-1}} do
		local nx,ny=p.x+d[1],p.y+d[2]
		if not x and game.level.map:isBound(nx,ny) and not game.level.map(nx,ny,Map.ACTOR) and
		 not game.level.map:checkEntity(nx,ny,Map.TERRAIN,'block_move') then x,y=nx,ny end
	end
	assert(x,'no free cell for the target')
	best:move(x,y,true)
	best:setEffect(best.EFF_SLEEP,100,{src=p,power=100000,insomnia=0,waking=0,contagious=0,no_ct_effect=true})
	target=best
	return {target=best.name,tx=best.x,ty=best.y,px=p.x,py=p.y,sleep=best:attr('sleep') and true or false}
end
function M.castDream()
	local p,best=game.player,assert(target,'prepareDream first')
	p.talents_cd[p.T_DREAMSCAPE]=nil
	-- Same targeting stand-in as S16's Fearscape (an own getTarget for the
	-- duration of the call, then restored).
	local old=rawget(p,'getTarget')
	p.getTarget=function() return best.x,best.y,best end
	local okc,ok=pcall(p.forceUseTalent,p,p.T_DREAMSCAPE,{ignore_energy=true,ignore_ressources=true,ignore_cd=true,force_target=best})
	p.getTarget=old
	assert(okc,ok)
	return {cast=ok and true or false,target=best.name,tx=best.x,ty=best.y,px=p.x,py=p.y,
		effect=p:hasEffect(p.EFF_DREAMSCAPE) and true or false}
end
function M.leaveDream()
	local p=game.player
	p:removeEffect(p.EFF_DREAMSCAPE)
	return {dreamscape=p:hasEffect(p.EFF_DREAMSCAPE) and true or false}
end
function M.resetDreamCooldown()
	local p=game.player
	p.talents_cd[p.T_DREAMSCAPE]=nil
	return {ok=true}
end
-- The plane's foreground (zone.lua:51-65) re-tints the map from the clock
-- every frame and post_process adds cloud weather; for toggle frames the
-- plane's level drops its foreground (the last tint stays) and weather is
-- quieted (display only, fixture only).
function M.quietDream()
	local had=tw.quiet()
	if game.zone.short_name=='dreamscape-talent' then
		-- Game:display calls level.data.foreground (mod/class/Game.lua:1873,1897).
		had.dream_foreground=game.level.data.foreground and true or false
		game.level.data.foreground=nil;game.zone.foreground=nil
	end
	return had
end
-- Grey samples: every visible CLOUD / OUTERSPACE cell in the window around
-- (cx,cy) with its screen rectangle (read only).
function M.samples(cx,cy)
	local m=game.level.map
	local out={tile=m.tile_w*m.zoom,cells={}}
	for x=cx-9,cx+9 do for y=cy-7,cy+7 do
		local g=x>=0 and y>=0 and x<m.w and y<m.h and m(x,y,Map.TERRAIN)
		local f=g and (g.define_as=='CLOUD' and 'cloud' or g.define_as=='OUTERSPACE' and 'void')
		local s=f and not m(x,y,Map.ACTOR) and tw.screen(x,y)
		if s and s.sx>=m.display_x and s.sy>=m.display_y and s.sx+s.tile<=m.display_x+m.viewport.width and
		 s.sy+s.tile<=m.display_y+m.viewport.height then
			s.family=f;out.cells[#out.cells+1]=s
		end
	end end
	return out
end
return M
