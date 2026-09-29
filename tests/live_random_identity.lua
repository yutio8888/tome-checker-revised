-- REAL engine checks for the disposable OFFLINE fixture only. Excluded from
-- the production addon. Copy into the fixture's virtual home, then execute:
-- local audit = dofile('/checker-live-random-identity.lua')
-- audit.run()    -- native generation and finishEntity, detached test actors
-- audit.begin()  -- queue a native temporary ZIP, return without blocking
-- audit.finish() -- call on a later frame; false means the native write waits
--
-- No actor is added to the map and no game/player save is written. These
-- explicit fixture operations consume RNG/UIDs and generate real class data;
-- they are an integration audit, not a combat or campaign-save playthrough.
local Tokens = require 'mod.class.CheckerTokens'
local Style = require 'mod.class.CheckerTokenStyle'
local Entity = require 'engine.Entity'
local Savefile = require 'engine.Savefile'
local M = {results={}, samples={}}

local function guard()
	assert(config.settings.cheat and config.settings.disable_all_connectivity and not profile.auth,
		'random identity audit requires the isolated offline debug fixture')
	assert(__module_extra_info.checker_demo and game.checker_staged and game.zone.short_name=='trollmire',
		'random identity audit requires the staged checker_demo Trollmire')
	assert(game.player==game.checker_hero, 'restore the fixture hero before this audit')
	assert(config.settings.tome.checker_tokens_enabled~=false, 'enable creature tokens before this audit')
end

local function record(kind, status, detail)
	M.results[kind] = {status=status, detail=detail}
	print('[RandomIdentityLive]',kind,status,detail)
end

local function scalarRecord(origin)
	assert(type(origin)=='table' and getmetatable(origin)==nil, 'origin must be a plain table')
	local n=0
	for key,value in pairs(origin) do
		assert(type(key)=='string', 'origin must have string keys')
		local kind=type(value)
		assert(kind=='string' or kind=='number' or kind=='boolean', 'origin contains a display/object reference: '..key)
		n=n+1
	end
	assert(n>0,'origin is empty')
end

local function identify(actor, expected, reason)
	local state=actor._checker_token
	local id,why=Tokens.explain(actor,state and state.display)
	assert(id==expected and why==reason, ('unexpected identity %s/%s, wanted %s/%s'):format(tostring(id),tostring(why),tostring(expected),reason))
end

local function source(id)
	local entry=assert(Tokens.by_id[id])
	for _,actor in pairs(game.zone.npc_list) do
		if actor.name==entry.name and not actor.unique and Tokens.identify(actor)==id then return actor end
	end
	error('native prototype unavailable: '..id)
end

local function generate(id, rank)
	local prototype=source(id)
	local before={name=prototype.name,image=prototype.image,type=prototype.type,subtype=prototype.subtype,
		define_as=prototype.define_as,unique=prototype.unique,rank=prototype.rank,origin=prototype._checker_token_origin}
	-- One actual native martial class keeps this small audit reproducible while
	-- avoiding unrelated aura/shape classes. No generation functions are mocked.
	local boss,boss_id=game.state:createRandomBoss(prototype, {level=5, rank=rank,
		force_classes={'Bulwark'}, nb_classes=0, forbid_equip=true,
		loot_quantity=0, no_loot_randart=true, name_scheme='#rng#'})
	assert(boss~=prototype and boss.define_as==boss_id and boss.unique==boss.name and boss.randboss==true)
	assert(boss.rank==rank, 'identity hook changed native rank')
	assert(boss.descriptor and boss.descriptor.classes and boss.descriptor.classes[1]=='Bulwark',
		'native class application did not run')
	identify(boss,id,'random-origin')
	scalarRecord(boss._checker_token_origin)
	assert(prototype.name==before.name and prototype.image==before.image and prototype.type==before.type
		and prototype.subtype==before.subtype and prototype.define_as==before.define_as
		and prototype.unique==before.unique and prototype.rank==before.rank
		and prototype._checker_token_origin==before.origin, 'identity capture changed the native prototype')
	local actor=game.zone:finishEntity(game.level,'actor',boss)
	assert(actor~=boss and actor._checker_token_origin~=boss._checker_token_origin, 'finishEntity did not clone origin')
	assert(not actor.x and not actor.y and not actor.summoner and not game.level:hasEntity(actor),
		'integration subject must remain detached from the world')
	identify(actor,id,'random-origin')
	return actor
end

function M.run()
	guard()
	assert(not M.pending,'finish the outstanding ZIP audit first')
	local hero,turn=game.player,game.turn
	local x,y,life=hero.x,hero.y,hero.life
	M.samples={}
	for _,sample in ipairs{{'wolf',3.2,'rare'}, {'forest-troll',3.5,'unique'}, {'brown-bear',4,'boss'}} do
		local actor=generate(sample[1],sample[2])
		assert(Style.rankBadge(actor.rank)==sample[3], 'rank UI no longer follows the native rank')
		M.samples[#M.samples+1]=actor
		record(sample[3],'PASS',sample[1]..' / '..actor.name..' / '..actor.define_as)
	end
	local prototype=source('wolf')
	local unknown=prototype:clone()
	unknown.name='Unknown unique using wolf artwork'; unknown.unique=unknown.name; unknown.define_as='CHECKER_UNKNOWN_UNIQUE'
	identify(unknown,nil,'unknown-unique')
	local unknown_boss=game.state:createRandomBoss(unknown,{level=1,nb_classes=0,loot_quantity=0,no_loot_randart=true})
	assert(not unknown_boss._checker_token_origin and not Tokens.identify(unknown_boss),'unknown unique acquired a token origin')
	local transformed=game.state:createRandomBoss(prototype,{level=1,nb_classes=0,loot_quantity=0,no_loot_randart=true,
		post=function(actor) actor.image='npc/canine_gw.png' end})
	assert(not transformed._checker_token_origin and not Tokens.identify(transformed),'post-generation body change was stamped')

	-- Exercise production display ownership on a detached clone, leaving the
	-- subjects intended for serialization free of all temporary display objects.
	local probe=M.samples[1]:clone()
	assert(game:checkerRefreshActor(probe)=='wolf','generated actor did not obtain its token display')
	local image=probe.image
	probe.image='npc/canine_gw.png'
	assert(not game:checkerRefreshActor(probe) and not probe._checker_token and not probe.replace_display,
		'changed generated body retained a stale token')
	probe.image=image
	assert(game:checkerRefreshActor(probe)=='wolf','restored body did not recover its token')
	local foreign=Entity.new{image='npc/canine_gw.png'}
	probe.replace_display=foreign
	assert(not game:checkerRefreshActor(probe) and probe.replace_display==foreign and not probe._checker_token,
		'external replacement was overwritten')
	probe.replace_display=nil
	assert(game:checkerRefreshActor(probe)=='wolf','external replacement removal did not recover the token')
	probe.shader_auras={checker_identity_fixture={}}
	assert(not game:checkerRefreshActor(probe) and not probe._checker_token and not probe.replace_display,
		'aura state retained an unsupported token')
	probe.shader_auras=nil
	assert(game:checkerRefreshActor(probe)=='wolf','aura state removal did not recover the token')
	probe.rank=5
	assert(Tokens.identify(probe,probe.replace_display)=='wolf' and Style.rankBadge(probe.rank)=='elite_boss',
		'rank change invalidated the body or kept an old badge')
	assert(game.player==hero and game.turn==turn and hero.x==x and hero.y==y and hero.life==life,
		'detached identity audit changed the player or world turn')
	record('generation','PASS','native createRandomBoss + finishEntity for ranks 3.2/3.5/4; real Bulwark; unknown unique/post transform fallback; body/display/aura recovery; dynamic rank')
	return true
end

function M.begin()
	guard()
	assert(not M.pending,'a ZIP write is already pending')
	assert(not savefile_pipe.saving and #savefile_pipe.pipe==0
		and (not savefile_pipe.waiton or not next(savefile_pipe.waiton)), 'wait for the fixture save to finish')
	if #M.samples==0 then M.run() end
	local actor=M.samples[1]
	assert(not actor.replace_display and not actor._checker_token,'serialize a detached native body before display installation')
	assert(not (actor._no_save_fields and actor._no_save_fields._checker_token_origin),'origin was excluded from native serialization')
	scalarRecord(actor._checker_token_origin)
	local root='/tmp/checker-random-identity/'
	local directory=root..os.time()..'-'..actor.uid..'/'
	fs.mkdir('/tmp'); fs.mkdir(root); fs.mkdir(directory)
	local zip=directory..'actor.teae'
	local previous,count=Savefile:getCurrent(),savefile_pipe.current_nb
	local writer,objects
	local ok,err=xpcall(function()
		writer=Savefile.new('checker-random-identity',false)
		writer.save_dir=directory
		objects=writer:saveObject(actor,zip..'.tmp')
		assert(objects>=1,'native serializer did not queue the actor')
		core.serial.threadSave()
	end,debug.traceback)
	if writer then writer:close() end
	Savefile:setCurrent(previous)
	savefile_pipe.current_nb=count
	if not ok then error(err,0) end
	M.pending={source=actor,directory=directory,zip=zip,objects=objects}
	record('serialization','PENDING','native temporary ZIP: '..zip..'; objects='..objects)
	return zip
end

function M.finish()
	guard()
	local job=assert(M.pending,'call begin() first')
	local completed=core.serial.popSaveReturn()
	if not completed then return false,'native ZIP write pending' end
	assert(completed==job.zip,'unexpected save completion during the isolated identity audit: '..tostring(completed))
	assert(fs.exists(job.zip),'native ZIP is missing')
	local previous,reader,mounted=Savefile:getCurrent(),nil,nil
	local loaded
	local ok,err=xpcall(function()
		reader=Savefile.new('checker-random-identity',false)
		reader.save_dir=job.directory
		reader.load_dir=job.directory..'mounted/'
		mounted=assert(fs.getRealPath(job.zip),'temporary ZIP has no physical path')
		fs.mount(mounted,reader.load_dir)
		loaded=assert(reader:loadReal('main'),'native reader returned no actor')
		for _,object in ipairs(reader.delayLoad) do object:loaded() end
		assert(loaded~=job.source and loaded._checker_token_origin~=job.source._checker_token_origin,
			'origin was reused from memory instead of deserialized')
		scalarRecord(loaded._checker_token_origin)
		for key,value in pairs(job.source._checker_token_origin) do
			assert(loaded._checker_token_origin[key]==value,'native serialization lost origin field '..key)
		end
		assert(not loaded.replace_display and not loaded._checker_token,'identity serialization unexpectedly stored display objects')
		identify(loaded,'wolf','random-origin')
	end,debug.traceback)
	if mounted then fs.umount(mounted) end
	if reader then reader:close() end
	Savefile:setCurrent(previous)
	M.pending=nil
	if not ok then error(err,0) end
	local turn=game.turn
	assert(game:checkerRefreshActor(loaded)=='wolf','loaded random actor could not build a token')
	assert(loaded._checker_token.display==loaded.replace_display,'loaded token ownership is inconsistent')
	local image=loaded.image
	loaded.image='npc/canine_gw.png'
	assert(not game:checkerRefreshActor(loaded) and not loaded.replace_display,'loaded changed body retained its old token')
	loaded.image=image
	assert(game:checkerRefreshActor(loaded)=='wolf','loaded restored body could not recover')
	assert(game.turn==turn,'serialization identity checks advanced the world')
	M.last_serialized_actor=loaded
	record('serialization','PASS','native ZIP round trip retained scalar origin without display objects; post-load display rebuild and body fallback/recovery; '..job.zip)
	return true
end

return M
