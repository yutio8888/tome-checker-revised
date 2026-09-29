-- REAL engine integration checks, loaded only into the disposable offline
-- checker_demo fixture. This file is not part of the distributable addon.
--
-- local audit = dofile('/checker-lifecycle.lua') -- root copies this test here
-- audit.begin()          -- queues a native disk write and returns immediately
-- audit.finish()         -- call on a later command/frame; false means pending
-- audit.runParty()       -- actual addMember/setPlayer round trip, then cleanup
-- audit.runAura()        -- requires a cold launch with core.shader.active(4)
-- audit.beginMovement()  -- move a rendered wolf normally; returns immediately
-- audit.finishMovement() -- next rendered frame, before the 10-second anim ends
--
-- No game/player save is written. The serialized subject is a newly created,
-- briefly rendered then detached native wolf, saved under this isolated virtual
-- home's /tmp directory. Its actual owned body and overlay Entities are saved.
local Map = require 'engine.Map'
local Savefile = require 'engine.Savefile'
local Tokens = require 'mod.class.CheckerTokens'
local M = {results={}}

local function guard()
	assert(config.settings.cheat and config.settings.disable_all_connectivity and not profile.auth,
		'lifecycle audit requires the offline debug fixture')
	assert(__module_extra_info.checker_demo and game.checker_staged and game.zone.short_name == 'trollmire',
		'lifecycle audit requires the staged checker_demo Trollmire')
	assert(game.player == game.checker_hero, 'restore the fixture hero before running a lifecycle check')
	assert(game.checker_mode == 'refined' and not game.checker_native_actors, 'enable refined monster art first')
end

local function record(kind, status, detail)
	M.results[kind] = {status=status, detail=detail}
	print('[MonsterLifecycle]', kind, status, detail)
end

local function freshWolf()
	local prototype
	for _, e in pairs(game.zone.npc_list) do
		if e.name == 'wolf' and e.image == Tokens.by_id.wolf.image and not e.unique then prototype=e; break end
	end
	assert(prototype, 'native wolf prototype is absent')
	local a = game.zone:finishEntity(game.level, 'actor', prototype)
	a.never_act = true
	assert(not a.summoner and not a.x and not a.y, 'serialization subject must start detached from the world')
	assert(game:checkerRefreshActor(a) == 'wolf', 'fresh native wolf did not receive its token')
	return a
end

local function render(a)
	assert(a.x and a.y, 'render check needs a placed actor')
	a:removeAllMOs()
	game.level.map:updateMap(a.x, a.y)
	assert(a._mo, 'visible test actor has no native map object')
end

local function refresh()
	game.player:playerFOV()
	game.level.map:centerViewAround(game.player.x, game.player.y)
	game.level.map:redisplay()
	game.level.map.changed, game.player.changed, game.paused = true, true, true
end

local function position(a)
	local m, p = game.level.map, game.checker_hero
	for r=1,6 do for dx=-r,r do for dy=-r,r do
		local x, y = p.x+dx, p.y+dy
		if m:isBound(x,y) and m.seens(x,y) and not m(x,y,Map.ACTOR) then
			local g=m(x,y,Map.TERRAIN)
			if g and g.subtype ~= 'water' and not m:checkEntity(x,y,Map.TERRAIN,'block_move',a) then return x,y end
		end
	end end end
	error('no visible free land for the temporary lifecycle wolf')
end

local function withWolf(body)
	guard()
	local hero, turn, a = game.checker_hero, game.turn, freshWolf()
	local x,y=position(a)
	game.zone:addEntity(game.level,a,'actor',x,y)
	local ok, result = xpcall(function() return body(a,hero) end, debug.traceback)
	-- Always use the real party API to restore control, including on failure.
	local cleaned, cleanup_error = xpcall(function()
		if game.player ~= hero then assert(game.party:setPlayer(hero,true), 'could not restore hero control') end
		if game.party.members[a] then game.party:removeMember(a,true) end
		if a.x and a.y and game.level.map(a.x,a.y,Map.ACTOR)==a then game.level.map:remove(a.x,a.y,Map.ACTOR) end
		game.level:removeEntity(a,true)
		refresh()
	end,debug.traceback)
	if not cleaned then error('lifecycle cleanup failed; restart the disposable fixture: '..cleanup_error,0) end
	if not ok then error(result,0) end
	assert(game.turn==turn, 'lifecycle audit unexpectedly advanced a world turn')
	return result
end

function M.begin()
	guard()
	assert(not M.pending, 'a serialization check is already pending')
	assert(not M.movement, 'finish the movement check before serializing')
	assert(not savefile_pipe.saving and #savefile_pipe.pipe==0
		and (not savefile_pipe.waiton or not next(savefile_pipe.waiton)),
		'wait for the existing fixture save to finish before this test')
	local a, rendered_overlay
	withWolf(function(wolf)
		render(wolf)
		core.display.forceRedraw()
		local state=assert(wolf._checker_token,'rendered wolf lost token ownership')
		rendered_overlay=assert(state.overlay,'rendered token did not create an overlay Entity')
		assert(state.overlay_active and rendered_overlay._mo,'rendered token overlay has no map object')
		assert(rendered_overlay~=state.display,'overlay must be independent from the body Entity')
		a=wolf
	end)
	-- withWolf removed this temporary actor from both map and level. Clearing
	-- detached coordinates cannot move any world entity or capture a game save.
	a.x,a.y=nil,nil
	assert(a._checker_token.overlay==rendered_overlay,'detaching discarded overlay ownership before serialization')
	assert(a._no_save_fields._checker_token == nil, 'ownership is still excluded from engine serialization')
	local root='/tmp/checker-token-lifecycle/'
	local directory=root..os.time()..'-'..a.uid..'/'
	fs.mkdir('/tmp'); fs.mkdir(root); fs.mkdir(directory)
	local zip=directory..'actor.teae'
	local previous, count = Savefile:getCurrent(), savefile_pipe.current_nb
	local writer, objects
	local ok,err=xpcall(function()
		writer=Savefile.new('checker-token-lifecycle',false)
		writer.save_dir=directory
		objects=writer:saveObject(a,zip..'.tmp')
		assert(objects>=3, 'native serializer did not include actor, body and overlay Entities')
		core.serial.threadSave()
	end,debug.traceback)
	if writer then writer:close() end
	Savefile:setCurrent(previous)
	savefile_pipe.current_nb=count
	if not ok then error(err,0) end
	M.pending={source=a,zip=zip,directory=directory,objects=objects}
	record('serialization','PENDING','native Savefile:saveObject queued '..objects..' objects at '..zip)
	return zip
end

function M.finish()
	guard()
	local job=assert(M.pending, 'call begin() first')
	-- This check never spins or blocks the game. The root invokes it again
	-- after the native save thread reports that its ZIP is closed and renamed.
	local completed=core.serial.popSaveReturn()
	if not completed then return false,'native disk write pending' end
	assert(completed==job.zip,'unexpected save completion during isolated lifecycle audit: '..tostring(completed))
	assert(fs.exists(job.zip),'native disk write completed without its ZIP')
	local previous, reader, mounted = Savefile:getCurrent(), nil, nil
	local loaded
	local ok,err=xpcall(function()
		reader=Savefile.new('checker-token-lifecycle',false)
		reader.save_dir=job.directory
		reader.load_dir=job.directory..'mounted/'
		mounted=assert(fs.getRealPath(job.zip),'temporary ZIP has no physical path')
		fs.mount(mounted,reader.load_dir)
		assert(fs.exists(reader.load_dir..'main'),'temporary ZIP did not mount')
		loaded=assert(reader:loadReal('main'),'native Savefile:loadReal returned no actor')
		for _,obj in ipairs(reader.delayLoad) do obj:loaded() end
		assert(loaded~=job.source,'reader reused the original actor instead of deserializing')
		assert(loaded._checker_token and loaded._checker_token.id=='wolf','serialized ownership was lost')
		assert(loaded._checker_token.display==loaded.replace_display,'ownership and replacement lost shared reference identity')
		assert(loaded.replace_display~=job.source.replace_display,'replacement Entity was not deserialized')
		local overlay=assert(loaded._checker_token.overlay,'rendered overlay ownership was lost during serialization')
		assert(overlay.__CLASSNAME=='engine.Entity','deserialized overlay is not an engine Entity')
		assert(overlay~=job.source._checker_token.overlay and overlay~=loaded.replace_display,
			'overlay was reused from memory or collapsed into the body Entity')
		assert(not overlay._mo,'native map-object userdata must not be serialized')
		local mos={}
		loaded:getMapObjects(game.level.map.tiles,mos,10)
		assert(loaded._checker_token.overlay==overlay,'render rebuild replaced the deserialized overlay Entity')
		assert(mos[11]==overlay._mo and overlay._mo,'deserialized overlay was not reattached to its native actor layer')
		assert(Tokens.identify(loaded,loaded._checker_token.display)=='wolf','loaded native body no longer maps')
	end,debug.traceback)
	if mounted then fs.umount(mounted) end
	if reader then reader:close() end
	Savefile:setCurrent(previous)
	M.pending=nil
	if not ok then error(err,0) end
	-- Use the public mode API and then refresh the detached loaded actor. It is
	-- deliberately absent from level.entities, so the latter call is required.
	local turn=game.turn
	local checked,check_error=xpcall(function()
		game:checkerSetTokensEnabled(false)
		game:checkerRefreshActor(loaded)
		assert(not loaded._checker_token and not loaded.replace_display,'loaded ownership could not restore native display')
		game:checkerSetTokensEnabled(true)
		assert(game:checkerRefreshActor(loaded)=='wolf','loaded actor could not restore its token')
		assert(loaded._checker_token.display==loaded.replace_display,'refreshed ownership is inconsistent')
		assert(game.turn==turn,'serialization mode check advanced the world')
	end,debug.traceback)
	game:checkerSetTokensEnabled(true)
	if not checked then error(check_error,0) end
	M.last_serialized_actor=loaded
	record('serialization','PASS','native ZIP preserved body and rendered overlay Entities; shared ownership and overlay layer reattachment passed; independent token off/on restoration passed; '..job.zip)
	return true
end

function M.runAura()
	guard()
	if not core.shader.active(4) then
		local reason='requires a fresh shader-enabled launch with core.shader.active(4); no core.shader.active mock was used'
		record('aura','SKIP',reason)
		return false,reason
	end
	withWolf(function(a)
		render(a)
		assert(a._checker_token and a._checker_token.id=='wolf','pre-aura token is absent')
		local name='checker_lifecycle_aura'
		assert(a:addShaderAura(name,'awesomeaura',{time_factor=5500,alpha=0.6,flame_scale=0.6},
			'particles_images/arcaneshockwave.png'),'native addShaderAura rejected the shader')
		assert(a.shader_auras and a.shader_auras[name],'native shader state was not activated')
		assert(not a._checker_token and not a.replace_display,'aura did not fall back to the native body')
		render(a)
		local aura
		for _,mo in ipairs(a.add_mos or {}) do if mo._isshaderaura and mo.shader=='awesomeaura' then aura=mo end end
		assert(aura and aura.image==Tokens.by_id.wolf.image,'native aura layer was discarded or attached to obsolete token art')
		assert(aura._shader and aura._shader.shad,'native aura layer did not compile a real shader')
		assert(a._last_mo and a._last_mo~=a._mo,'native aura did not produce its chained map objects')
		a:removeShaderAura(name)
		assert(not a.shader_auras[name],'native aura state was not removed')
		render(a)
		assert(a._checker_token and a._checker_token.id=='wolf','token did not return after aura removal')
		assert(a.replace_display==a._checker_token.display,'aura cleanup left foreign replacement ownership')
		assert(not a.add_mos or not next(a.add_mos),'native aura layers remain after removal')
		assert(not a.replace_display.add_mos or not next(a.replace_display.add_mos),'token retained stale aura layers')
	end)
	record('aura','PASS','real addShaderAura/updateModdableTile and removeShaderAura preserved native aura then restored token')
	return true
end

function M.runParty()
	withWolf(function(a,hero)
		a.faction,a.summoner,a.summon_time=hero.faction,hero,12
		local uid=a.uid
		game.party:addMember(a,{control='full',type='summon',title='Lifecycle test wolf',temporary=true})
		assert(game.party.members[a] and game.party.members[a].control=='full','native addMember failed')
		assert(game.party:setPlayer(a),'native setPlayer rejected the temporary wolf')
		assert(game.player==a and game.party.player==a,'party control did not move to wolf')
		assert(Map.actor_player==a and game.level.map.actor_player==a,'viewer actor did not follow native party control')
		assert(game.uiset.hotkeys_display.actor==a,'hotkeys did not follow the controlled wolf')
		assert(a.__CLASSNAME=='mod.class.Player','native control did not convert the wolf to Player')
		assert(a.uid==uid,'party conversion changed the world entity UID')
		render(a)
		assert(a._checker_token and a._checker_token.id=='wolf','controlled native wolf lost its species token')
		assert(a.replace_display.image==Tokens.image('wolf'),'controlled wolf was rendered as the human hero')
		assert(game.party:setPlayer(hero),'native setPlayer could not restore the hero')
		assert(game.player==hero and game.party.player==hero and Map.actor_player==hero
			and game.level.map.actor_player==hero,'viewer/player did not return to the hero')
		assert(game.uiset.hotkeys_display.actor==hero,'hotkeys did not return to hero')
		render(a)
		assert(a._checker_token and a._checker_token.id=='wolf','formerly controlled wolf lost its token')
		assert(a.uid==uid and game.level.map(a.x,a.y,Map.ACTOR)==a,'party round trip changed actor placement or identity')
	end)
	record('party','PASS','real addMember/setPlayer(wolf)/setPlayer(hero); viewer, hotkeys, UID and creature token verified')
	return true
end

local function movementPositions(a)
	local m,p=game.level.map,game.checker_hero
	local function free(x,y)
		if not m:isBound(x,y) or not m.seens(x,y) or m(x,y,Map.ACTOR) or m(x,y,Map.TRAP) then return false end
		local g=m(x,y,Map.TERRAIN)
		return g and g.subtype~='water' and not m:checkEntity(x,y,Map.TERRAIN,'block_move',a)
	end
	-- Stay close to the hero so both ends are inside the visible viewport. Use
	-- an orthogonal normal step; no forced move, attack, door or trap is tested.
	for r=1,4 do for dx=-r,r do for dy=-r,r do
		local x,y=p.x+dx,p.y+dy
		if free(x,y) then
			for _,d in ipairs{{1,0},{0,1},{-1,0},{0,-1}} do
				if free(x+d[1],y+d[2]) then return x,y,x+d[1],y+d[2] end
			end
		end
	end end end
	error('no adjacent visible free land for the movement audit')
end

local function cleanupMovement(job)
	config.settings.tome.smooth_move=job.smooth_move
	local a,hero=job.actor,job.hero
	if game.player~=hero then assert(game.party:setPlayer(hero,true),'could not restore hero after movement audit') end
	if a.x and a.y and game.level.map(a.x,a.y,Map.ACTOR)==a then game.level.map:remove(a.x,a.y,Map.ACTOR) end
	game.level:removeEntity(a,true)
	refresh()
	assert(game.player==hero and game.turn==job.turn,'movement audit changed hero control or world turn')
end

function M.beginMovement()
	guard()
	assert(not M.movement,'a movement check is already pending')
	assert(not M.pending,'finish the native disk-write check before moving')
	local a=freshWolf()
	local ox,oy,nx,ny=movementPositions(a)
	local job={actor=a,hero=game.checker_hero,turn=game.turn,smooth_move=config.settings.tome.smooth_move,
		ox=ox,oy=oy,nx=nx,ny=ny}
	local ok,err=xpcall(function()
		game.zone:addEntity(game.level,a,'actor',ox,oy)
		render(a)
		-- C map objects cancel motion on their first-ever draw (DL_NONE).
		-- Prime the real renderer before the normal move so the next frame is
		-- an interpolation sample, rather than a never-rendered spawn.
		core.display.forceRedraw()
		local state=assert(a._checker_token,'movement subject lost token ownership')
		assert(state.overlay_active and state.overlay and state.overlay._mo,'movement subject has no active overlay')
		job.body,job.overlay=a._mo,state.overlay._mo
		a.energy.value=game.energy_to_act*2
		local energy=a.energy.value
		config.settings.tome.smooth_move=300 -- native normalized frames, about 10 seconds
		assert(a:move(nx,ny),'native normal move was rejected')
		assert(a.x==nx and a.y==ny and game.level.map(nx,ny,Map.ACTOR)==a,'normal move did not reach its free target')
		assert(a.energy.value<energy,'normal move did not consume native movement energy')
		assert(a._mo==job.body and a._checker_token.overlay._mo==job.overlay,'movement rebuilt the animated map objects')
		assert(game.turn==job.turn and game.player==job.hero,'normal NPC move advanced the world or changed control')
	end,debug.traceback)
	-- The animation stores its duration in native map objects; restore the
	-- user's setting immediately, even while the two-phase sample is pending.
	config.settings.tome.smooth_move=job.smooth_move
	if not ok then cleanupMovement(job); error(err,0) end
	M.movement=job
	record('movement','PENDING',('normal wolf move %d,%d -> %d,%d; sample the next rendered frame'):format(ox,oy,nx,ny))
	return true
end

function M.finishMovement()
	guard()
	local job=assert(M.movement,'call beginMovement() first')
	local a,m=job.actor,game.level.map
	local sample
	local ok,err=xpcall(function()
		assert(a._mo==job.body and a._checker_token and a._checker_token.overlay._mo==job.overlay,
			'pending movement lost its original body/overlay map objects')
		local ground=assert(m(a.x,a.y,Map.TERRAIN),'movement target lost its terrain')
		assert(ground._mo,'movement target has no stationary terrain map object')
		-- getMoveAnim includes camera scroll. Subtract the stationary terrain's
		-- offset, otherwise equal camera motion could hide an unanimated token.
		local gx,gy=ground._mo:getMoveAnim(m._map,a.x,a.y)
		local bx,by=job.body:getMoveAnim(m._map,a.x,a.y)
		local rx,ry=job.overlay:getMoveAnim(m._map,a.x,a.y)
		local epsilon=0.00001
		assert(math.abs(bx-gx)+math.abs(by-gy)>epsilon,
			'body has no nonzero interpolation: allow one rendered frame and finish within 10 seconds')
		assert(math.abs(rx-gx)+math.abs(ry-gy)>epsilon,'overlay remained at rest while the body moved')
		assert(math.abs(bx-rx)<epsilon and math.abs(by-ry)<epsilon,
			('body/overlay interpolation diverged: %.7f,%.7f vs %.7f,%.7f'):format(bx,by,rx,ry))
		sample=('body=(%.7f,%.7f) overlay=(%.7f,%.7f) relative to stationary terrain'):format(bx-gx,by-gy,rx-gx,ry-gy)
		a:resetMoveAnim()
		local b0x,b0y=job.body:getMoveAnim(m._map,a.x,a.y)
		local r0x,r0y=job.overlay:getMoveAnim(m._map,a.x,a.y)
		assert(math.abs(b0x-r0x)<epsilon and math.abs(b0y-r0y)<epsilon,'native resetMoveAnim did not reset both layers equally')
		assert(math.abs(b0x-gx)+math.abs(b0y-gy)<epsilon and math.abs(r0x-gx)+math.abs(r0y-gy)<epsilon,
			'body or overlay retained movement after resetMoveAnim')
		assert(config.settings.tome.smooth_move==job.smooth_move,'smooth_move setting was not restored')
	end,debug.traceback)
	M.movement=nil
	local cleaned,cleanup_error=xpcall(function() cleanupMovement(job) end,debug.traceback)
	if not cleaned then error('movement cleanup failed; restart the disposable fixture: '..cleanup_error,0) end
	if not ok then error(err,0) end
	record('movement','PASS',sample..'; both reset to zero; temporary actor removed; hero and world turn unchanged')
	return true
end

return M
