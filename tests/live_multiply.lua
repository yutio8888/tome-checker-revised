-- Offline fixture only. No mocked clone or substitute talent implementation.
-- local audit = dofile('/checker-live-multiply.lua')
-- audit.run()     -- real Multiply action twice; retain three frozen actors
--                 -- take the screenshot, then audit.cleanup()
-- audit.run(false)-- same checks, immediately clean up after recording
-- Report: /multiply-validation.txt. No world tick or player save is requested.
local Map = require 'engine.Map'
local Tokens = require 'mod.class.CheckerTokens'
local Fixture = require 'mod.class.CheckerFixture'
local M = {path='/multiply-validation.txt', actors={}, rows={}}
local id = 'white-worm-mass'
local rule_fields = {'name','type','subtype','image','define_as','unique','rank','level',
	'life','max_life','die_at','life_rating','size_category','faction','global_speed_base'}

local function guard()
	assert(Fixture.enabled() and __module_extra_info.checker_fixture==true and not profile.auth,
		'Multiply audit requires the isolated offline checker_fixture')
	assert(game.level and game.zone.short_name=='trollmire' and game.checker_staged,
		'stage the isolated Trollmire before the Multiply audit')
	assert(game.player==game.checker_hero and game.paused,'restore the fixture hero and pause before this audit')
	assert(game:checkerTokensEnabled(),'enable creature tokens before the Multiply audit')
	assert(Tokens.by_id[id],'white-worm-mass must be in the next catalog before running this audit')
end

local function clean(value)
	return tostring(value==nil and '' or value):gsub('[\t\r\n]',' ')
end

local function writeReport(status, detail)
	M.status,M.detail=status,detail
	local file=assert(fs.open(M.path,'w'))
	file:write('status='..status..'\n'..detail..'\n')
	file:write('scope=real T_MULTIPLY.action; no useTalent cooldown/energy wrapper; no world tick\n')
	file:write('setup=parent life explicitly set to 55% of its native living range; test actors frozen\n')
	file:write('native_action='..clean(M.action_source)..'\n')
	file:write('turn_before='..clean(M.turn)..' turn_after='..clean(game.turn)..'\n')
	file:write('retained='..tostring(M.job~=nil)..' tile='..clean(game.level.map.tile_w)..'\n')
	for _,sample in ipairs(M.callbacks or {}) do
		file:write(('callback uid=%s body=%d overlay=%d\n'):format(sample.uid,sample.body,sample.overlay))
	end
	file:write('phase\trole\tuid\tparent_uid\tx\ty\trank\tlevel\tlife\tmax_life\tcan_multiply\texp_worth\tenergy\thas_multiply\ttoken\treason\tdisplay_uid\toverlay_uid\timage\tactor_mo\tdisplay_mo\toverlay_mo\n')
	for _,row in ipairs(M.rows) do
		local values={}
		for i=1,22 do values[i]=clean(row[i]) end
		file:write(table.concat(values,'\t')..'\n')
	end
	file:close()
	print('[MultiplyLive]',status,detail,'report',M.path)
end

local function snapshot(actor)
	local out={}
	for _,key in ipairs(rule_fields) do out[key]=actor[key] end
	return out
end

local function sameRules(actor, before, label)
	for _,key in ipairs(rule_fields) do
		assert(actor[key]==before[key], label..' changed '..key..': '..tostring(before[key])..' -> '..tostring(actor[key]))
	end
end

local function presentEntities()
	local out={}
	for _,entity in pairs(game.level.entities) do out[entity]=true end
	return out
end

local function worldUnchanged(job, cleaned)
	assert(game.level==job.level and game.player==job.hero and game.turn==job.turn,'audit changed the level, hero or world turn')
	for entity, before in pairs(job.baseline) do
		assert(job.level:hasEntity(entity),'audit removed a pre-existing entity')
		assert(entity.x==before.x and entity.y==before.y and entity.life==before.life and entity.max_life==before.max_life,
			'audit changed a pre-existing entity')
	end
	assert(job.hero.energy.value==job.hero_energy,'audit changed player energy')
	for _,entity in pairs(job.level.entities) do
		assert(job.baseline[entity] or (not cleaned and job.created[entity]),'unexpected entity outside this audit')
	end
end

local function refresh()
	game.player:playerFOV()
	game.level.map:centerViewAround(game.player.x,game.player.y)
	game.level.map:redisplay()
	game.level.map.changed=true
	game.player.changed=true
	game.paused=true
end

local function cleanupJob(job)
	assert(game.level==job.level,'clean the Multiply actors before leaving this fixture level')
	local map=job.level.map
	for actor in pairs(job.created) do
		if actor.x and actor.y and map(actor.x,actor.y,Map.ACTOR)==actor then map:remove(actor.x,actor.y,Map.ACTOR) end
		if job.level:hasEntity(actor) then job.level:removeEntity(actor,true) end
		actor:removeAllMOs()
	end
	refresh()
	worldUnchanged(job,true)
	M.job=nil
	M.actors={}
end

function M.cleanup()
	guard()
	if not M.job then return true end
	cleanupJob(M.job)
	writeReport(M.status or 'PASS',(M.detail or '')..'; all three test actors removed without death/drops')
	return true
end

local function prototype()
	-- Keep this list local; the test must not change the zone's spawn pool.
	local list=game.zone.npc_class:loadList('/data/general/npcs/vermin.lua',true)
	for _,actor in pairs(list) do
		if actor.name=='white worm mass' and not actor.unique then return actor end
	end
	error('native white worm mass prototype is absent')
end

-- Match the native free-grid terrain/occupancy test without calling the RNG.
-- Reject a location if ANY potential first/second spawn could land on water,
-- a trap, or outside the visible area. No terrain/actor is moved to make room.
local function nativeFree(x,y)
	local map=game.level.map
	return map:isBound(x,y) and not map(x,y,Map.ACTOR)
		and not map:checkEntity(x,y,Map.TERRAIN,'block_move')
end

local function safeCell(x,y)
	local map=game.level.map
	local terrain=map(x,y,Map.TERRAIN)
	return map.seens(x,y) and terrain and terrain.subtype~='water' and not terrain.change_level
		and not terrain.change_zone and not map(x,y,Map.TRAP) and not map(x,y,Map.TRIGGER)
end

local function availableAround(x,y,excluded_x,excluded_y)
	local out={}
	for gx,column in pairs(core.fov.circle_grids(x,y,1,true)) do
		for gy in pairs(column) do
			if not (gx==x and gy==y) and not (gx==excluded_x and gy==excluded_y) and nativeFree(gx,gy) then
				if not safeCell(gx,gy) then return nil end
				out[#out+1]={gx,gy}
			end
		end
	end
	return out
end

local function position()
	local hero=game.player
	-- The shoreline fixture has very little safe land in its central band;
	-- search the full visible 64px viewport before declaring it unsuitable.
	for radius=1,8 do
		for dx=-radius,radius do for dy=-math.min(radius,6),math.min(radius,6) do
			local x,y=hero.x+dx,hero.y+dy
			if nativeFree(x,y) and safeCell(x,y) then
				local first=availableAround(x,y)
				local good=first and #first>0
				for _,cell in ipairs(first or {}) do
					local second=availableAround(cell[1],cell[2],x,y)
					if not second or #second==0 then good=false; break end
				end
				if good then return x,y end
			end
		end end
	end
	error('no safe visible Multiply cluster; use a less crowded staged scene without moving existing actors')
end

local function render(actor)
	local before=snapshot(actor)
	assert(game:checkerRefreshActor(actor)==id,'native worm did not receive the white-worm-mass token')
	actor:removeAllMOs()
	game.level.map:updateMap(actor.x,actor.y)
	core.display.forceRedraw()
	local state=assert(actor._checker_token,'rendering lost token ownership')
	local token,reason=Tokens.explain(actor,state.display)
	assert(token==id and reason=='exact-identity','Multiply must preserve exact ordinary identity')
	assert(not actor._checker_token_origin,'ordinary Multiply unexpectedly required a random identity marker')
	assert(actor.replace_display==state.display and actor._mo,'rendered token body/ownership is missing')
	assert(state.display._mo==actor._mo,'actor and its own token display disagree on the body map object')
	assert(state.overlay and state.overlay_active and state.overlay._mo,'rendered tactical overlay is missing')
	sameRules(actor,before,'token rendering')
	return state
end

local function row(phase,role,actor,parent)
	local state=actor._checker_token
	local token,reason=Tokens.explain(actor,state and state.display)
	M.rows[#M.rows+1]={phase,role,actor.uid,parent and parent.uid,actor.x,actor.y,actor.rank,actor.level,
		actor.life,actor.max_life,actor.can_multiply,actor.exp_worth,actor.energy.value,
		actor:knowTalent(actor.T_MULTIPLY) and true or false,token,reason,
		state and state.display and state.display.uid,state and state.overlay and state.overlay.uid,actor.image,
		tostring(actor._mo),tostring(state and state.display._mo),tostring(state and state.overlay and state.overlay._mo)}
end

local function auditCallbacks(actors)
	local originals,counts,handles={},{},{}
	local function countMethod(actor,method,kind)
		local implementation=assert(actor[method],'missing callback target '..method)
		originals[#originals+1]={actor=actor,method=method,raw=rawget(actor,method)}
		-- This is an observation wrapper, installed only AFTER native cloning.
		-- Run the original method and restore the instance field even on failure.
		actor[method]=function(self,...)
			assert(self==actor,'render callback invoked a different actor')
			counts[actor][kind]=counts[actor][kind]+1
			return implementation(self,...)
		end
	end
	local ok,err=xpcall(function()
		for _,actor in ipairs(actors) do
			local state=actor._checker_token
			counts[actor]={body=0,overlay=0}
			handles[actor]={actor._mo,state.display._mo,state.overlay._mo}
			countMethod(actor,'smallTacticalFrame','body')
			countMethod(actor,'bigTacticalFrame','body')
			countMethod(actor,'checkerTacticalFrame','overlay')
		end
		refresh()
		core.display.forceRedraw()
		for _,actor in ipairs(actors) do
			local sample,state=counts[actor],actor._checker_token
			assert(sample.body>0 and sample.overlay>0,'body/overlay callback no longer belongs to actor uid '..actor.uid)
			assert(actor._mo==handles[actor][1] and state.display._mo==handles[actor][2]
				and state.overlay._mo==handles[actor][3],'a subsequent family redraw replaced another actor\'s map object')
			M.callbacks[#M.callbacks+1]={uid=actor.uid,body=sample.body,overlay=sample.overlay}
		end
	end,debug.traceback)
	for _,saved in ipairs(originals) do saved.actor[saved.method]=saved.raw end
	if not ok then error(err,0) end
end

local function multiply(actor,talent,job)
	assert(not actor.clone_base,'ordinary fixture worm must clone its own native body')
	assert(actor:knowTalent(talent.id) and talent.on_pre_use(actor,talent),'native Multiply precondition failed')
	local before,remaining,energy=snapshot(actor),actor.can_multiply,actor.energy.value
	local cooldown=actor.talents_cd[talent.id]
	local entities=presentEntities()
	-- Calling the actual action intentionally isolates clone creation from the
	-- turn/cooldown wrapper. The action itself creates and adds the real child.
	local ok,result=xpcall(function() return talent.action(actor,talent) end,debug.traceback)
	local children={}
	for _,entity in pairs(job.level.entities) do
		if not entities[entity] then job.created[entity]=true; children[#children+1]=entity end
	end
	if not ok then error(result,0) end
	assert(result==true and #children==1,'native Multiply did not create exactly one new entity')
	local child=children[1]
	assert(child~=actor and child.uid~=actor.uid and child.__CLASSNAME=='mod.class.NPC','Multiply did not create a distinct native NPC')
	assert(job.level.map(child.x,child.y,Map.ACTOR)==child and safeCell(child.x,child.y),'native child is not in a safe visible map cell')
	assert(math.max(math.abs(child.x-actor.x),math.abs(child.y-actor.y))==1,'native child is not adjacent')
	assert(actor.can_multiply==remaining-1 and child.can_multiply==remaining-2,'native multiplication budget changed')
	assert(child.exp_worth==0.1 and child.no_drops==true and child.immune_possession==1,'native clone rule fields changed')
	assert(child.energy.value==0,'native clone must begin with zero energy')
	assert(actor.energy.value==energy and actor.talents_cd[talent.id]==cooldown,'direct action unexpectedly changed parent energy/cooldown')
	assert(child.never_act==true and not child.player and not child.summoner,'clone lost fixture freeze or gained player/summon status')
	assert((child:knowTalent(talent.id) and true or false)==(child.can_multiply>0),'native chain Multiply talent learning/removal changed')
	sameRules(actor,before,'Multiply parent')
	sameRules(child,before,'Multiply child inheritance')
	assert(child.combat.dam==actor.combat.dam and child.combat.atk==actor.combat.atk
		and child.combat.apr==actor.combat.apr,'native clone combat values changed')
	render(child)
	worldUnchanged(job,false)
	return child
end

function M.run(keep_for_screenshot)
	guard()
	assert(not M.job,'call cleanup() before starting another Multiply audit')
	local job={level=game.level,hero=game.player,turn=game.turn,hero_energy=game.player.energy.value,
		created={},baseline={}}
	for _,entity in pairs(game.level.entities) do
		job.baseline[entity]={x=entity.x,y=entity.y,life=entity.life,max_life=entity.max_life}
	end
	M.job,M.rows,M.actors,M.turn=job,{}, {},job.turn
	M.action_source,M.status,M.detail=nil,nil,nil
	M.callbacks={}
	local ok,err=xpcall(function()
		local parent=game.zone:finishEntity(game.level,'actor',prototype())
		assert(parent.rank==1 and parent.can_multiply==4,'native white worm base rank/multiplication budget differs from the audited definition')
		assert(not parent.unique and not parent.randboss,'test source must be the ordinary native white worm')
		parent.never_act=true -- fixture-only freeze, inherited by native clones
		job.created[parent]=true
		local x,y=position()
		game.zone:addEntity(game.level,parent,'actor',x,y)
		local low=parent.die_at or 0
		assert(parent.max_life>low,'native parent has no living life range')
		parent.life=low+(parent.max_life-low)*0.55 -- explicit injured fixture state
		local talent=parent:getTalentFromId(parent.T_MULTIPLY)
		assert(talent and type(talent.action)=='function','native Multiply talent is unavailable')
		local info=debug.getinfo(talent.action,'Sl')
		M.action_source=info.source..':'..info.linedefined
		assert(info.source:find('talents/misc/npcs.lua',1,true),'Multiply action is not the inspected native implementation')
		refresh(); render(parent); row('before-action','parent',parent)
		local child=multiply(parent,talent,job)
		local grandchild=multiply(child,talent,job)
		M.actors={parent,child,grandchild}
		local roles={'parent','child','grandchild'}
		for i,actor in ipairs(M.actors) do
			local state=render(actor)
			for j=1,i-1 do
				local other=M.actors[j]
				assert(state~=other._checker_token and state.display~=other.replace_display and actor._mo~=other._mo,
					'cloned actors share token state/body rendering objects')
				assert(state.display._mo~=other._checker_token.display._mo,
					'cloned display Entities retained the same native body map object')
				assert(state.overlay~=other._checker_token.overlay and state.overlay._mo~=other._checker_token.overlay._mo,
					'cloned actors share tactical overlay rendering objects')
			end
			row('after-two-actions',roles[i],actor,M.actors[i-1])
		end
		assert(parent.can_multiply==3 and child.can_multiply==1 and grandchild.can_multiply==0,'two-generation final budget mismatch')
		assert(not talent.on_pre_use(grandchild,talent),'exhausted grandchild can still pass native Multiply precheck')
		auditCallbacks(M.actors)
		refresh(); worldUnchanged(job,false)
	end,debug.traceback)
	if not ok then
		local cleaned,cleanup_error=xpcall(function() cleanupJob(job) end,debug.traceback)
		local detail=err..(cleaned and '; test entities cleaned' or '; cleanup failed: '..cleanup_error)
		writeReport('FAIL',detail)
		error(detail,0)
	end
	if keep_for_screenshot==false then cleanupJob(job) end
	writeReport('PASS','two actual native Multiply actions; exact identity; separate actor/display/overlay map objects and per-actor callback dispatch; native rank/life/level/combat inheritance; budget 4 -> 3/2 -> 3/1/0; unchanged world turn')
	return {status=M.status,path=M.path,actors=M.actors,retained=M.job~=nil,turn=job.turn}
end

return M
