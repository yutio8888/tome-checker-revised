-- Offline fixture only (S16: the Fearscape spell plane and Temporal Reprieve,
-- entered and left through the real talents). Reuses the S15 scene module
-- (enter, view, rules, quieting, particle pause, log clear) and adds: the
-- per-id S16 kind histogram, fixture-only casting of the two talents on the
-- fixture hero (learned at level 1, resources and cooldowns ignored through
-- forceUseTalent's own flags), leaving each plane through the native
-- deactivation, an actor-particle pause (the Fearscape bloodwings), and the
-- map viewport rectangle. Never edits a grid rule field.
local Map=require 'engine.Map'
local Terrain=require 'mod.class.CheckerTerrain'
local tw=dofile('/data-checker-fixture/monster-live_s15_scene.lua')
local M=setmetatable({},{__index=tw})

local function id(g) return g and (type(g.define_as)=='string' and g.define_as or '<'..tostring(g.name)..'>') or '<none>' end
function M.cells()
	local m=game.level.map
	local z=game.zone.short_name
	local out={zone=z,level=game.level.level,w=m.w,h=m.h,ids={},board=0,total=0}
	for x=0,m.w-1 do for y=0,m.h-1 do
		local g=m(x,y,Map.TERRAIN)
		local e=out.ids[id(g)] or {n=0,kind={},board=0}
		e.n=e.n+1;out.total=out.total+1
		local k=g and Terrain.s16Kind and Terrain.s16Kind(g,z) or false
		e.kind[tostring(k)]=(e.kind[tostring(k)] or 0)+1
		local st=g and g._checker_terrain
		if st and g.replace_display==st.display then e.board=e.board+1;out.board=out.board+1 end
		out.ids[id(g)]=e
	end end
	return out
end
function M.where()
	local p=game.player
	return {zone=game.zone.short_name,level=game.level.level,x=p.x,y=p.y,checker_mode=game.checker_mode or false,
		fearscape=p:isTalentActive(p.T_DEMON_PLANE) and true or false,reprieve=p:hasEffect(p.EFF_TEMPORAL_REPRIEVE) and true or false}
end
function M.viewport()
	local m=game.level.map
	return {x=m.display_x,y=m.display_y,w=m.viewport.width,h=m.viewport.height}
end
-- Fixture hero learns both plane talents (level 1). Learned once per run,
-- before the source frame, so the hotbar is the same before and after.
function M.learn()
	local p=game.player
	for _,t in ipairs{p.T_DEMON_PLANE,p.T_TEMPORAL_REPRIEVE} do
		if not p:knowTalent(t) then p:learnTalent(t,true,1) end
	end
	return {fearscape=p:knowTalent(p.T_DEMON_PLANE),reprieve=p:knowTalent(p.T_TEMPORAL_REPRIEVE)}
end
-- Fearscape needs a target within range 5: the nearest non-summon actor is
-- moved (fixture only) to a free cell next to the hero. Vim is only checked
-- by on_pre_use, so the fixture hero gets a vim pool of 50. The target is
-- placed before the source frames are taken (it returns to the same cell).
local target
function M.prepareFearscape()
	local p=game.player
	local best,bd
	for _,a in pairs(game.level.entities) do
		if a~=p and a.x and a.ai and not a.summoner and not a.summon_time and not a.dead and
		 not a:attr('negative_status_effect_immune') and not a:attr('status_effect_immune') and a:canBe('planechange') then
			local d=core.fov.distance(p.x,p.y,a.x,a.y)
			if not bd or d<bd then best,bd=a,d end
		end
	end
	assert(best,'no Fearscape target')
	-- An adjacent free cell, so the 'hit' targeting always projects.
	local x,y
	for _,d in ipairs{{1,0},{-1,0},{0,1},{0,-1},{1,1},{-1,1},{1,-1},{-1,-1}} do
		local nx,ny=p.x+d[1],p.y+d[2]
		if not x and game.level.map:isBound(nx,ny) and not game.level.map(nx,ny,Map.ACTOR) and
		 not game.level.map:checkEntity(nx,ny,Map.TERRAIN,'block_move') then x,y=nx,ny end
	end
	assert(x,'no free cell for the target')
	best:move(x,y,true)
	target=best
	return {target=best.name,tx=best.x,ty=best.y,px=p.x,py=p.y}
end
function M.castFearscape()
	local p,best=game.player,assert(target,'prepareFearscape first')
	p.max_vim=math.max(p.max_vim or 0,100);p.vim=50
	p.talents_cd[p.T_DEMON_PLANE]=nil
	-- useTalent's force_target stub only covers activated talents; for this
	-- sustained one the fixture supplies the player's target choice the same
	-- way (an own getTarget for the duration of the call, then restored).
	local old=rawget(p,'getTarget')
	p.getTarget=function() return best.x,best.y,best end
	local okc,ok=pcall(p.forceUseTalent,p,p.T_DEMON_PLANE,{ignore_energy=true,ignore_ressources=true,ignore_cd=true,force_target=best})
	p.getTarget=old
	assert(okc,ok)
	return {cast=ok and true or false,target=best.name,tx=best.x,ty=best.y,px=p.x,py=p.y,game_ender=p.game_ender and true or false,
		active=p:isTalentActive(p.T_DEMON_PLANE) and true or false}
end
function M.leaveFearscape()
	local p=game.player
	local ok=p:forceUseTalent(p.T_DEMON_PLANE,{ignore_energy=true,ignore_ressources=true,ignore_cd=true})
	return {ok=ok and true or false,active=p:isTalentActive(p.T_DEMON_PLANE) and true or false}
end
function M.castReprieve()
	local p=game.player
	p.talents_cd[p.T_TEMPORAL_REPRIEVE]=nil
	local ok=p:forceUseTalent(p.T_TEMPORAL_REPRIEVE,{ignore_energy=true,ignore_ressources=true,ignore_cd=true})
	return {cast=ok and true or false}
end
function M.leaveReprieve()
	local p=game.player
	p:removeEffect(p.EFF_TEMPORAL_REPRIEVE)
	return {reprieve=p:hasEffect(p.EFF_TEMPORAL_REPRIEVE) and true or false}
end
-- Cooldowns the casts started (fixture only) so the hotbar matches the frame
-- taken before the cast.
function M.resetCooldowns()
	local p=game.player
	p.talents_cd[p.T_DEMON_PLANE]=nil;p.talents_cd[p.T_TEMPORAL_REPRIEVE]=nil
	return {ok=true}
end
-- Actor particles (the Fearscape bloodwings) animate every frame; detach them
-- for the rest of the plane visit so toggle frames compare terrain only
-- (display only; the native deactivation's removeParticles of an already
-- detached emitter is a no-op).
function M.dropActorParticles()
	local held={}
	for _,a in pairs(game.level.entities) do
		for ps in pairs(a.__particles or {}) do held[#held+1]={a,ps} end
	end
	for _,h in ipairs(held) do h[1]:removeParticles(h[2]) end
	return {dropped=#held}
end
return M
