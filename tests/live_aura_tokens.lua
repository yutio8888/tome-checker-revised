-- Offline fixture only. Exercises "keep the token when the actor has native
-- shader_auras" (plan A): staged monsters, a spawned giant crystal rat and
-- the player token get native addShaderAura auras applied through the debug
-- bridge, one real talent path (T_STONE_SKIN via forceUseTalent) proves the
-- non-debug case, then every aura is removed. Every trigger is a native code
-- path; AI stays frozen (never_act/checkerStage) throughout.
local Map=require 'engine.Map'
local Talents=require 'engine.interface.ActorTalents'
local M={rows={}}

local function guard()
	assert(require('mod.class.CheckerFixture').enabled() and not profile.auth)
	assert(game.checker_staged and game.paused and game.player==game.checker_hero)
	assert(game.zone.short_name=='trollmire' and not game.zone.is_flooded)
end

local function say(text)
	M.rows[#M.rows+1]=text;print('[AuraTokens]',text)
	local f=assert(fs.open('/aura-tokens-validation.txt','w'))
	f:write(table.concat(M.rows,'\n')..'\n');f:close()
end

-- Exact native aura defs sampled from addShaderAura call sites under
-- game/modules/tome/data (kind, shader, shader_args, texture). stone_skin
-- (Earth spell "Stone Skin", data/talents/spells/earth.lua) is required by
-- the task; the other three are visually distinct native samples.
M.auras={
	stone_skin={shader='crystalineaura',
		args={time_factor=1500, spikeOffset=0.123123, spikeLength=0.9, spikeWidth=3, growthSpeed=2, color={0xD7/255,0x8E/255,0x45/255}},
		tex='particles_images/spikes.png'},
	body_of_fire={shader='awesomeaura', args={time_factor=3500, alpha=1, flame_scale=1.1}, tex='particles_images/wings.png'},
	reflective_skin={shader='awesomeaura', args={time_factor=5500, alpha=0.6, flame_scale=0.6}, tex='particles_images/arcaneshockwave.png'},
	essence_of_the_dead={shader='awesomeaura', args={time_factor=4000, alpha=0.6}, tex='particles_images/darkwings.png'},
}

local function auraEntries(actor)
	local host=actor.replace_display or actor
	local n=0
	if type(host.add_mos)=='table' then
		for _,mo in pairs(host.add_mos) do if type(mo)=='table' and mo._isshaderaura then n=n+1 end end
	end
	return n
end

local function ownsToken(actor)
	local s=actor._checker_token
	return s and actor.replace_display==s.display and s.id or nil
end

function M.actors()
	guard()
	local by_name={}
	for _,e in pairs(game.level.entities) do
		if e.ai and by_name[e.name]==nil then
			for _,n in ipairs{'wolf','forest troll','brown bear','large brown snake'} do
				if e.name==n then by_name[n]=e end
			end
		end
	end
	M.cache=by_name
	return by_name
end

-- Spawn a giant crystal rat next to the player, the same way checkerStage
-- places its own creatures (game.zone:finishEntity + addEntity).
function M.spawnCrystalRat()
	guard()
	local m=game.level.map
	local px,py=game.player.x,game.player.y
	local src
	for _,e in pairs(game.zone.npc_list) do if e.name=='giant crystal rat' then src=e;break end end
	assert(src,'giant crystal rat not in this zone npc list')
	local nx,ny
	for r=1,7 do for dx=-r,r do for dy=-r,r do
		local x,y=px+dx,py+dy
		if not nx and m(x,y,Map.TERRAIN) and m.seens(x,y) and not m(x,y,Map.ACTOR)
			and not m:checkEntity(x,y,Map.TERRAIN,'block_move',game.player) then nx,ny=x,y end
	end end if nx then break end end
	assert(nx,'no free tile for giant crystal rat')
	local a=game.zone:finishEntity(game.level,'actor',src)
	a.never_act=true
	game.zone:addEntity(game.level,a,'actor',nx,ny)
	M.rat=a
	say(('spawned giant crystal rat at %d,%d'):format(nx,ny))
	return a
end

function M.run()
	guard()
	M.actors()
	M.spawnCrystalRat()
	local names={}
	for n in pairs(M.cache) do names[#names+1]=n end
	table.sort(names)
	say('staged: '..table.concat(names,', ')..', giant crystal rat, player')
end

local function target(name)
	if name=='player' then return game.player end
	if name=='giant crystal rat' then return assert(M.rat,'call M.spawnCrystalRat first') end
	return assert(M.cache and M.cache[name], 'unknown staged actor '..tostring(name))
end
M.target=target

function M.focus(name)
	guard()
	local a=target(name)
	game.player.sight=20;game.player:playerFOV()
	game.level.map:centerViewAround(a.x,a.y)
end

function M.apply(name,kind)
	guard()
	local a=target(name)
	local def=assert(M.auras[kind],'unknown aura '..tostring(kind))
	local before=auraEntries(a)
	local ok=a:addShaderAura(kind,def.shader,def.args,def.tex)
	assert(ok~=false,'addShaderAura rejected for '..name..'/'..kind..' (shaders inactive?)')
	local after=auraEntries(a)
	-- Native updateModdableTilePrepare (non-moddable branch) inserts the sdm
	-- aura wrap AND re-wraps the base image itself as a second _isshaderaura
	-- add_mos entry (image_alter absent, image=base) so the plain image keeps
	-- drawing under the aura chain; a first aura on a fresh (add_mos-less)
	-- display always adds exactly 2 marked entries, never a duplicate wrap.
	assert(after==before+2,('aura entry count %d -> %d, expected +2 for %s'):format(before,after,name))
	say(('apply    %-20s %-20s token=%-18s aura_entries=%d overlay_active=%s'):format(
		name,kind,tostring(ownsToken(a)),after,tostring(a._checker_token and a._checker_token.overlay_active)))
	return after
end

function M.remove(name,kind)
	guard()
	local a=target(name)
	a:removeShaderAura(kind)
	local left=auraEntries(a)
	say(('remove   %-20s %-20s token=%-18s aura_entries=%d'):format(name,kind,tostring(ownsToken(a)),left))
	assert(left==0,'aura entries did not clear for '..name)
end

-- Real native talent path (not debug-applied): learn + force-activate the
-- actual sustained Stone Skin talent, the same call the talent's own
-- activate() makes.
function M.realStoneSkin(name)
	guard()
	local a=target(name)
	local tid=Talents.T_STONE_SKIN
	if not a:knowTalent(tid) then a:learnTalent(tid,true,1) end
	local before=auraEntries(a)
	a:forceUseTalent(tid,{ignore_energy=true,ignore_cooldown=true,ignore_ressources=true})
	local after=auraEntries(a)
	say(('real T_STONE_SKIN %-20s token=%-18s active=%s aura_entries=%d->%d'):format(
		name,tostring(ownsToken(a)),tostring(a:isTalentActive(tid)),before,after))
	return after
end

function M.deactivateStoneSkin(name)
	guard()
	local a=target(name)
	local tid=Talents.T_STONE_SKIN
	if a:isTalentActive(tid) then a:forceUseTalent(tid,{ignore_energy=true,ignore_cooldown=true,ignore_ressources=true}) end
	say(('deactivate T_STONE_SKIN %-20s token=%-18s active=%s aura_entries=%d'):format(
		name,tostring(ownsToken(a)),tostring(a:isTalentActive(tid)),auraEntries(a)))
end

function M.report()
	guard()
	local lines={}
	for _,name in ipairs{'wolf','forest troll','brown bear','large brown snake','giant crystal rat','player'} do
		local ok,a=pcall(target,name)
		if ok then
			lines[#lines+1]=('%-20s token=%-18s aura_entries=%d'):format(name,tostring(ownsToken(a)),auraEntries(a))
		end
	end
	say('--- report ---\n'..table.concat(lines,'\n'))
end

return M
