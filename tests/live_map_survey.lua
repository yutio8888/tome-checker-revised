-- Offline fixture only. Multi-zone terrain/actor coverage survey. Every zone
-- switch is native game:changeLevel; forced variants (Kor'Pul HIDEOUT,
-- Trollmire FLOODED) reuse the same alternateZone/alternateZoneTier1
-- override-then-restore trick as tests/live_korpul_scene.lua. AI is frozen
-- and the player made unkillable purely for safety; no gameplay rule changes.
local Map=require 'engine.Map'
local Tokens=require 'mod.class.CheckerTokens'
local Terrain=require 'mod.class.CheckerTerrain'
local EngineZone=require 'engine.Zone' -- removeLastPersistZone only; base class table
local Zone=require 'mod.class.Zone' -- actual construction, like tests/live_korpul_scene.lua
local M={}

local function guard()
	assert(require('mod.class.CheckerFixture').enabled() and not profile.auth)
	assert(config.settings.cheat)
	assert(game.checker_hero==game.player, 'fixture hero not bound to current player')
end

-- Minimal ad hoc JSON encoder for controlled internal data only (no untrusted
-- keys, no NaN/inf). Good enough for this survey's own dump files.
local function jenc(v)
	local t=type(v)
	if v==nil then return 'null' end
	if t=='boolean' then return v and 'true' or 'false' end
	if t=='number' then
		if v~=v or v==math.huge or v==-math.huge then return 'null' end
		return tostring(v)
	end
	if t=='string' then
		return '"'..v:gsub('[\\"]','\\%0'):gsub('\n','\\n'):gsub('\r',''):gsub('\t','\\t')..'"'
	end
	if t=='table' then
		local n=#v
		if n>0 then
			local parts={}
			for i=1,n do parts[#parts+1]=jenc(v[i]) end
			return '['..table.concat(parts,',')..']'
		elseif next(v)==nil then
			return '[]'
		else
			local parts={}
			for k,val in pairs(v) do parts[#parts+1]='"'..tostring(k)..'":'..jenc(val) end
			return '{'..table.concat(parts,',')..'}'
		end
	end
	return 'null'
end

function M.dump(path,tbl)
	local f=assert(fs.open(path,'w'))
	f:write(jenc(tbl))
	f:close()
end

function M.setup()
	guard()
	config.settings.tome.quest_popup=false -- disposable fixture setting, not saved
	game.player.invulnerable=1
	if game.player.max_life then game.player.life=game.player.max_life end
	game.paused=true
	return {ok=true}
end

local function freezeAndSurvive()
	for _,a in pairs(game.level.entities) do
		if a.ai then a.never_act=true end
		-- Fixture heroes do not carry zone quests; Kyless's native sight hook
		-- (keepsake-meadow L6) would index the missing quest. Actors only.
		if a.seen_by and game.zone and game.zone.short_name=='keepsake-meadow' then a.seen_by=nil end
	end
	game.player.invulnerable=1
	if game.player.max_life then game.player.life=game.player.max_life end
end

local function refreshView()
	local m=game.level.map
	m.clean_fov=true;game.player:playerFOV()
	m.smooth_scroll=0;m:centerViewAround(game.player.x,game.player.y)
	m:redisplay();m.changed=true;game.paused=true;core.display.forceRedraw()
end

local function dismissDialogs()
	for i=#game.dialogs,1,-1 do
		local d=game.dialogs[i]
		print('[MapSurvey] dismissing dialog',d.__CLASSNAME)
		game:unregisterDialog(d)
	end
	game.bignews.list=nil
	if game.flyers and game.flyers.empty then game.flyers:empty() end
end

-- opts: {hideout=true/false} forces ruins-kor-pul variant;
-- {flooded=true/false} forces trollmire variant; {crystaline=true/false}
-- forces old-forest variant (game.state:alternateZone, same call shape as
-- Kor'Pul's HIDEOUT/DEFAULT -- old-forest/zone.lua:20). All three use the
-- same override-then-restore technique as tests/live_korpul_scene.lua.
-- Slazish Fens has no layout variant, so it is entered with opts=nil/{}.
function M.enter(short_name,level,opts)
	guard()
	opts=opts or {}
	dismissDialogs()
	-- Persistent zones (trollmire, ruins-kor-pul, ...) reuse a cached instance
	-- instead of re-running zone.lua; drop it so each survey entry gets a
	-- fresh, deterministic generation with any variant override honoured.
	EngineZone:removeLastPersistZone(short_name)
	-- The birth save already persisted a "zone" savefile chunk for the start
	-- zone; Zone:load() prefers that over re-running zone.lua, which would
	-- silently ignore both removeLastPersistZone and any variant override
	-- below. Same technique as tests/live_korpul_scene.lua.
	local doLoad=savefile_pipe.doLoad
	savefile_pipe.doLoad=function(self,save,kind,arg,id,...)
		if kind=='zone' and id==short_name then return nil end
		return doLoad(self,save,kind,arg,id,...)
	end
	local ok,err=pcall(function()
		local zone
		if opts.hideout~=nil then
			assert(short_name=='ruins-kor-pul')
			local alternate=game.state.alternateZone
			game.state.alternateZone=function(self,name,...)
				if name=='ruins-kor-pul' then return opts.hideout and 'HIDEOUT' or 'DEFAULT' end
				return alternate(self,name,...)
			end
			local ok2,z=pcall(function() return Zone.new(short_name) end)
			game.state.alternateZone=alternate
			assert(ok2,z)
			zone=z
			assert((zone.is_hideout and true or false)==(opts.hideout and true or false),'HIDEOUT/DEFAULT variant mismatch')
		elseif opts.flooded~=nil then
			assert(short_name=='trollmire' or short_name=='lake-nur')
			local method=short_name=='trollmire' and 'alternateZoneTier1' or 'alternateZone'
			local alt=game.state[method]
			game.state[method]=function(self,name,...)
				if name==short_name then return opts.flooded and 'FLOODED' or 'DEFAULT' end
				return alt(self,name,...)
			end
			local ok2,z=pcall(function() return Zone.new(short_name) end)
			game.state[method]=alt
			assert(ok2,z)
			zone=z
			assert((zone.is_flooded and true or false)==(opts.flooded and true or false),'FLOODED variant mismatch')
		elseif opts.crystaline~=nil then
			assert(short_name=='old-forest')
			local alt=game.state.alternateZone
			game.state.alternateZone=function(self,name,...)
				if name=='old-forest' then return opts.crystaline and 'CRYSTALINE' or 'DEFAULT' end
				return alt(self,name,...)
			end
			local ok2,z=pcall(function() return Zone.new(short_name) end)
			game.state.alternateZone=alt
			assert(ok2,z)
			zone=z
			assert((zone.is_crystaline and true or false)==(opts.crystaline and true or false),'CRYSTALINE/DEFAULT variant mismatch')
		elseif opts.overground~=nil then
			assert(short_name=='rhaloren-camp')
			local alt=game.state.alternateZoneTier1
			game.state.alternateZoneTier1=function(self,name,...)
				if name=='rhaloren-camp' then return opts.overground and 'OVERGROUND' or 'DEFAULT' end
				return alt(self,name,...)
			end
			local ok2,z=pcall(function() return Zone.new(short_name) end)
			game.state.alternateZoneTier1=alt
			assert(ok2,z)
			zone=z
			assert((zone.generator.map.class=='engine.generator.map.Town')==(opts.overground and true or false),'OVERGROUND/DEFAULT variant mismatch')
		elseif opts.invasion~=nil then
			assert(short_name=='murgol-lair')
			local alt=game.state.alternateZone
			game.state.alternateZone=function(self,name,...)
				if name=='murgol-lair' then return opts.invasion and 'INVASION' or 'DEFAULT' end
				return alt(self,name,...)
			end
			local ok2,z=pcall(function() return Zone.new(short_name) end)
			game.state.alternateZone=alt
			assert(ok2,z);zone=z
			assert((zone.is_invaded and true or false)==(opts.invasion and true or false),'Murgol INVASION/DEFAULT mismatch')
		elseif opts.invaded~=nil then
			assert(short_name=='norgos-lair')
			local alt=game.state.alternateZoneTier1
			game.state.alternateZoneTier1=function(self,name,...)
				if name=='norgos-lair' then return opts.invaded and 'INVADED' or 'DEFAULT' end
				return alt(self,name,...)
			end
			local ok2,z=pcall(function() return Zone.new(short_name) end)
			game.state.alternateZoneTier1=alt
			assert(ok2,z);zone=z
			assert((zone.is_invaded and true or false)==(opts.invaded and true or false),'INVADED/DEFAULT mismatch')
		elseif opts.volcano~=nil then
			assert(short_name=='daikara')
			local alt=game.state.alternateZone
			game.state.alternateZone=function(self,name,...)
				if name=='daikara' then return opts.volcano and 'VOLCANO' or 'DEFAULT' end
				return alt(self,name,...)
			end
			local ok2,z=pcall(function() return Zone.new(short_name) end)
			game.state.alternateZone=alt
			assert(ok2,z);zone=z
			assert((zone.is_volcano and true or false)==(opts.volcano and true or false),'VOLCANO/DEFAULT variant mismatch')
		elseif opts.collapsed~=nil then
			assert(short_name=='maze')
			local alt=game.state.alternateZone
			game.state.alternateZone=function(self,name,...)
				if name=='maze' then return opts.collapsed and 'COLLAPSED' or 'DEFAULT' end
				return alt(self,name,...)
			end
			local ok2,z=pcall(function() return Zone.new(short_name) end)
			game.state.alternateZone=alt
			assert(ok2,z);zone=z
			assert((zone.is_collapsed and true or false)==(opts.collapsed and true or false),'Maze layout mismatch')
		elseif opts.bigworm~=nil then
			assert(short_name=='sandworm-lair')
			local alt=game.state.alternateZone
			game.state.alternateZone=function(self,name,...)
				if name=='sandworm-lair' then return opts.bigworm and 'BIGWORM' or 'DEFAULT' end
				return alt(self,name,...)
			end
			local ok2,z=pcall(function() return Zone.new(short_name) end)
			game.state.alternateZone=alt
			assert(ok2,z);zone=z
			assert((zone.max_level==2)==(opts.bigworm and true or false),'Sandworm layout mismatch')
		elseif opts.twisted~=nil then
			assert(short_name=='scintillating-caves')
			local alt=game.state.alternateZone
			game.state.alternateZone=function(self,name,...)
				if name=='scintillating-caves' then return opts.twisted and 'TWISTED' or 'DEFAULT' end
				return alt(self,name,...)
			end
			local ok2,z=pcall(function() return Zone.new(short_name) end)
			game.state.alternateZone=alt
			assert(ok2,z);zone=z
			assert((zone.max_level==5)==(opts.twisted and true or false),'Crystal layout mismatch')
		elseif opts.purified~=nil then
			assert(short_name=='heart-gloom')
			local alt=game.state.alternateZone
			game.state.alternateZone=function(self,name,...)
				if name=='heart-gloom' then return opts.purified and 'PURIFIED' or 'DEFAULT' end
				return alt(self,name,...)
			end
			local ok2,z=pcall(function() return Zone.new(short_name) end)
			game.state.alternateZone=alt
			assert(ok2,z);zone=z
			assert((zone.is_purified and true or false)==(opts.purified and true or false),'Gloom layout mismatch')
		else
			zone=short_name
		end
		if opts.force_crystal_vault then
			assert(short_name=='scintillating-caves' and opts.twisted==true)
			-- Fixture-only generator probe: guarantee a native lesser vault so its
			-- boundary can be inspected even if random TWISTED starts omit one.
			zone.generator.map.rooms={{'lesser_vault',100},'random_room'}
		end
		game:changeLevel(level,zone,{direct_switch=true})
	end)
	savefile_pipe.doLoad=doLoad
	assert(ok,err)
	assert(game.zone.short_name==short_name,'zone mismatch after changeLevel: '..tostring(game.zone and game.zone.short_name))
	-- Entering a level can itself pop a quest-intro chat/dialog; dismiss again
	-- now that it has had a chance to appear (the pre-switch call only clears
	-- whatever was left over from the previous zone).
	dismissDialogs()
	freezeAndSurvive()
	refreshView()
	local m=game.level.map
	return {zone=game.zone.short_name,level=game.level.level,w=m.w,h=m.h,
		variant=Terrain.variant(game.zone) or false,checker_mode=game.checker_mode or false,
		is_flooded=(game.zone.is_flooded and true or false),
		is_hideout=(game.zone.is_hideout and true or false),
		is_invaded=(game.zone.is_invaded and true or false),
		is_volcano=(game.zone.is_volcano and true or false),
		is_collapsed=(game.zone.is_collapsed and true or false),
		is_bigworm=(game.zone.max_level==2),
		is_purified=(game.zone.is_purified and true or false),
		player_x=game.player.x,player_y=game.player.y,turn=game.turn}
end

function M.setMode(mode)
	guard();game:checkerSetMode(mode);refreshView()
	return {checker_mode=game.checker_mode or false}
end

-- Forest census predicate mirrors the private terrain() identity rules in
-- CheckerTerrain.lua (kept in sync by hand; tests/terrain_contract.lua and
-- tests/terrain_repair.lua exercise the real function directly). F1 adds
-- BOGTREE (subtype water, name 'tree', disambiguated from TREE by
-- define_as, same idiom the renderer uses) on top of the pre-existing
-- grass/road/flower/tree/hardtree/deep-water/bog-water set. G0 widens the
-- zone gate to old-forest/slazish-fen and, ONLY for old-forest, folds
-- subtype "dark_grass" into "grass" -- the same zone-scoped alias as
-- CheckerTerrain.lua's terrain(); Heart of the Gloom's own dark_grass TREE
-- must NOT match here either.
local function isBogtreeId(g)
	local id=g.define_as
	return id~=nil and (id=='BOGTREE' or id:match('^BOGTREE%d+$'))
end
local batch4Families={['south-beach']='beach',['keepsake-meadow']='meadow',['noxious-caldera']='caldera'}
local batch5Families={['charred-scar']='scorch',['demon-plane']='scorch',['shertul-fortress']='shertul',['rak-shor-pride']='rakshor'}
local underwaterZones={['murgol-lair']=true,['flooded-cave']=true,['temple-of-creation']=true}
local function forestSupported(g,zoneName)
	if not g then return false end
	if batch5Families[zoneName] then return Terrain.batch5Kind(g,batch5Families[zoneName])~=nil end
	if zoneName=='flooded-cave' or zoneName=='temple-of-creation' then return Terrain.underwaterKind(g)~=nil end
	if zoneName=='briagh-lair' then return Terrain.sandTerrain(g)~=nil end
	if zoneName=='valley-moon-caverns' then return Terrain.caveTerrain(g)~=nil or Terrain.valleyExit(g)~=nil end
	if zoneName=='orc-breeding-pit' then return game.level.level~=1 and Terrain.gloomTerrain(g,'plain')~=nil end
	if zoneName=='murgol-lair' then return Terrain.underwaterKind(g)~=nil end
	if batch4Families[zoneName] then return Terrain.batch4Kind(g,batch4Families[zoneName])~=nil end
	if zoneName=='lake-nur' and game.level.level==1 or
		zoneName=='temporal-rift' and game.level.level==4 then
		if Terrain.underwaterKind(g) or Terrain.surfaceSandKind(g) then return true end
	end
	if zoneName=='lake-nur' and (game.level.level==2 or
		game.level.level==3 and game.zone.is_flooded) then
		return Terrain.underwaterKind(g)~=nil
	end
	if zoneName=='unhallowed-morass' or zoneName=='abashed-expanse' or
		zoneName=='temporal-rift' and game.level.level==1 then
		return Terrain.voidTerrain(g,zoneName)~=nil or
			zoneName=='abashed-expanse' and Terrain.abashedTreeKind(g)~=nil
	end
	if zoneName=='temporal-rift' and game.level.level==3 then
		return Terrain.rockKind(g,true)~=nil
	end
	if zoneName=='temporal-rift' and game.level.level~=2 and game.level.level~=4 then return false end
	if zoneName=='heart-gloom' then
		return Terrain.gloomTerrain(g,game.zone.is_purified and 'dreamy' or 'gloomy')~=nil
	end
	if zoneName=='deep-bellow' then return Terrain.gloomTerrain(g,'plain')~=nil end
	if zoneName=='sandworm-lair' or zoneName=='ritch-tunnels' then return Terrain.sandTerrain(g)~=nil end
	if zoneName=='mark-spellblaze' then return Terrain.burntTerrain(g)~=nil end
	if zoneName=='scintillating-caves' then return Terrain.crystalTerrain(g)~=nil end
	if zoneName=='unremarkable-cave' or zoneName=='ardhungol' then return Terrain.caveTerrain(g)~=nil end
	if zoneName=='norgos-lair' then
		return Terrain.rockKind(g)~=nil
	end
	if zoneName=='tempest-peak' then return Terrain.rockKind(g,true)~=nil end
	if zoneName=='daikara' then
		return Terrain.rockKind(g,true)~=nil or Terrain.lavaKind(g)~=nil
	end
	local subtype=g.subtype
	if zoneName=='last-hope-graveyard' then
		if Terrain.graveyardProp(g) then return true end
		local id=g.define_as or ''
		local patch=tonumber(id:match('^GRASS_PATCH(%d+)$'))
		if id~='GRASS' and id~='GRASS_UP_WILDERNESS' and not (patch and patch<=14) and
			id~='DEEP_WATER' then return false end
	end
	if (zoneName=='lake-nur' or zoneName=='temporal-rift' and game.level.level==4) and g.change_zone then
		return Terrain.lakeExit(g)~=nil
	end
	if zoneName=='old-forest' and subtype=='dark_grass' then subtype='grass' end
	if subtype=='grass' then
		if g.change_level or g.change_zone then return true end
		if g.does_block_move then return g.name=='tree' or g.name=='tall thick tree' end
		return g.road or g.name=='flower' or g.name=='grass' and true or false
	end
	if subtype=='water' then
		if g.name=='tree' then return isBogtreeId(g) end
		return g.name=='deep water' or g.name=='bog water'
	end
	return false
end
local function forestOwned(g)
	local s=g and g._checker_terrain
	return s and g.replace_display==s.display and true or false
end

function M.norgosDetails()
	guard();assert(game.zone.short_name=='norgos-lair')
	local m=game.level.map
	local ids,visibility={}, {visible=0,remembered=0,unexplored=0}
	for x=0,m.w-1 do for y=0,m.h-1 do
		local g=m(x,y,Map.TERRAIN)
		local id=g and (g.define_as or g.name) or 'nil'
		local row=ids[id] or {count=0,supported=0,owned=0};ids[id]=row
		row.count=row.count+1
		if Terrain.rockKind(g) then row.supported=row.supported+1 end
		if forestOwned(g) then row.owned=row.owned+1 end
		if m.seens and m.seens(x,y) then visibility.visible=visibility.visible+1
		elseif m.remembers and m.remembers(x,y) then visibility.remembered=visibility.remembered+1
		else visibility.unexplored=visibility.unexplored+1 end
	end end
	return {ids=ids,visibility=visibility}
end

function M.daikaraDetails()
	guard();assert(game.zone.short_name=='daikara')
	local m=game.level.map
	local ids,exits={},{}
	for x=0,m.w-1 do for y=0,m.h-1 do
		local g=m(x,y,Map.TERRAIN)
		local id=g and (g.define_as or g.name) or 'nil'
		local row=ids[id] or {count=0,supported=0,owned=0};ids[id]=row
		row.count=row.count+1
		if forestSupported(g,'daikara') then row.supported=row.supported+1 end
		if forestOwned(g) then row.owned=row.owned+1 end
		if g and (g.change_level or g.change_zone) then
			exits[#exits+1]={x=x,y=y,id=id,level=g.change_level or false,
			 zone=g.change_zone or false,kind=Terrain.lavaKind(g) or Terrain.rockKind(g,true) or false,
			 owned=forestOwned(g)}
		end
	end end
	local down=game.level.default_down
	local center=false
	if down and down.x and down.y then
		local g=m(down.x,down.y,Map.TERRAIN)
		center={x=down.x,y=down.y,id=g and g.define_as or false,
			kind=Terrain.lavaKind(g) or Terrain.rockKind(g,true) or false,
			owned=forestOwned(g),change_level=g and g.change_level or false}
	end
	return {ids=ids,exits=exits,default_down=center}
end

function M.mazeDetails()
	guard();assert(game.zone.short_name=='maze')
	local m=game.level.map
	local ids,exits,cracks={},{},{}
	for x=0,m.w-1 do for y=0,m.h-1 do
		local g=m(x,y,Map.TERRAIN)
		local id=g and (g.define_as or g.name) or 'nil'
		local row=ids[id] or {count=0,supported=0};ids[id]=row
		row.count=row.count+1
		local kind=Terrain.classify(g)
		if kind then row.supported=row.supported+1 end
		if g and (g.change_level or g.change_zone) then exits[#exits+1]={x=x,y=y,id=id,kind=kind or false,change_level=g.change_level or false,change_zone=g.change_zone or false} end
		if id=='CRACKS' then local displays={};for _,d in ipairs(g.add_displays or {}) do displays[#displays+1]=d.image or '?' end
			cracks[#cracks+1]={x=x,y=y,kind=kind or false,pass_projectile=g.pass_projectile and true or false,block_move=type(g.block_move),image=g.image or false,stamp=g._checker_maze_source or false,does_block_move=g.does_block_move or false,block_sight=g.block_sight or false,add_mos=g.add_mos and #g.add_mos or false,displays=displays} end
	end end
	return {ids=ids,exits=exits,cracks=cracks}
end

function M.mazeOpenPose(preferCracks)
	guard();assert(game.zone.short_name=='maze')
	local m,p=game.level.map,game.player
	local best
	local xmin,xmax=m.w>=30 and 12 or 5,m.w>=30 and m.w-13 or m.w-6
	local ymin,ymax=m.h>=30 and 10 or 5,m.h>=30 and m.h-11 or m.h-6
	for x=xmin,xmax do for y=ymin,ymax do
		local g=m(x,y,Map.TERRAIN)
		if g and Terrain.classify(g)=='floor' and not m(x,y,Map.ACTOR) then
			local floor,wall,crack,nearest=0,0,0,99
			for dx=-4,4 do for dy=-4,4 do
				local k=Terrain.classify(m(x+dx,y+dy,Map.TERRAIN))
				if k=='floor' then floor=floor+1 elseif k=='old-wall' then wall=wall+1 elseif k=='cracks' then
					crack=crack+1;nearest=math.min(nearest,math.abs(dx)+math.abs(dy))
				end
			end end
			local score=floor+wall+(preferCracks and (crack*12+(nearest<=2 and 100-nearest*20 or 0)) or 0)+math.min(x,m.w-1-x,y,m.h-1-y)
			if not best or score>best.score then best={x=x,y=y,score=score,floor=floor,wall=wall,cracks=crack,nearest_crack=nearest} end
		end
	end end
	if not best then return {found=false} end
	p:move(best.x,best.y,true);p.sight=20;refreshView();best.found=true;return best
end

function M.mazeStageView()
	guard();assert(game.zone.short_name=='maze')
	local m,p=game.level.map,game.player
	local count=0
	for x=math.max(0,p.x-17),math.min(m.w-1,p.x+17) do for y=math.max(0,p.y-12),math.min(m.h-1,p.y+12) do
		m.seens(x,y,true);m.infovs(x,y,true);m.remembers(x,y,true);count=count+1
	end end
	m:redisplay();m.changed=true;core.display.forceRedraw()
	return {staged_cells=count,fixture_only=true}
end

function M.daikaraDiagnostics()
	guard();assert(game.zone.short_name=='daikara')
	local m=game.level.map
	local groups={}
	for x=0,m.w-1 do for y=0,m.h-1 do
		local g=m(x,y,Map.TERRAIN)
		if g and ((g.define_as or ''):match('^MOUNTAIN_WALL') or
		 (g.define_as or ''):match('^LAVA_FLOOR')) then
			local kind=Terrain.rockKind(g,true) or Terrain.lavaKind(g) or 'native'
			local displays={}
			for _,d in ipairs(g.add_displays or {}) do displays[#displays+1]=d.image or '?' end
			local key=table.concat({g.define_as or '',kind,g.image or '',g.type or '',g.name or '',
			 tostring(g.shader),tostring(g.air_level),tostring(g.dig),
			 tostring(g.on_stand),table.concat(displays,',')},'|')
			local row=groups[key] or {count=0,x=x,y=y,id=g.define_as or '',kind=kind,
			 image=g.image or false,name=g.name or false,typ=g.type or false,
			 shader=g.shader or false,air_level=g.air_level or false,dig=g.dig or false,
			 has_on_stand=g.on_stand and true or false,displays=displays,
			 add_mos=g.add_mos and #g.add_mos or 0,
			 change_level=g.change_level or false}
			row.count=row.count+1;groups[key]=row
		end
	end end
	local rows={};for _,v in pairs(groups) do rows[#rows+1]=v end
	return rows
end

function M.daikaraOpenPose(preferLava)
	guard();assert(game.zone.short_name=='daikara')
	local m,p=game.level.map,game.player
	local best
	for x=8,m.w-9 do for y=8,m.h-9 do
		local g=m(x,y,Map.TERRAIN)
		if g and not g.does_block_move and not m(x,y,Map.ACTOR) then
			local open,lava,adj=0,0,0
			for dx=-5,5 do for dy=-5,5 do
				local t=m(x+dx,y+dy,Map.TERRAIN)
				if t and not t.does_block_move then open=open+1 end
				if Terrain.lavaKind(t) then
					lava=lava+1
					for _,d in ipairs{{0,-1},{1,0},{0,1},{-1,0}} do
						if Terrain.rockKind(m(x+dx+d[1],y+dy+d[2],Map.TERRAIN),true)=='mountain-wall' then
							adj=adj+1;break
						end
					end
				end
			end end
			local score=open+(preferLava and (lava*2+adj*12) or 0)
			if not best or score>best.score then best={x=x,y=y,score=score,open=open,lava=lava,adjacent=adj} end
		end
	end end
	if not best then return {found=false} end
	p:move(best.x,best.y,true)
	-- Widen only this disposable, paused fixture's view for visual inspection;
	-- census and gameplay contract checks above run before this staged pose.
	p.sight=20
	refreshView()
	best.found=true;return best
end

function M.daikaraStageView()
	guard();assert(game.zone.short_name=='daikara')
	local m,p=game.level.map,game.player
	local count=0
	for x=math.max(0,p.x-17),math.min(m.w-1,p.x+17) do
		for y=math.max(0,p.y-12),math.min(m.h-1,p.y+12) do
			m.seens(x,y,true);m.infovs(x,y,true);m.remembers(x,y,true)
			count=count+1
		end
	end
	m:redisplay();m.changed=true;core.display.forceRedraw()
	return {staged_cells=count,fixture_only=true}
end

-- A fixture-only visibility pose: move to a reachable, passable snowy floor
-- using the native Actor:move entry point, then recompute native FOV. AI is
-- frozen. This tests remembered/unknown drawing, not continuous combat.
function M.norgosMemoryPose()
	guard();assert(game.zone.short_name=='norgos-lair')
	local m,p=game.level.map,game.player
	local queue,head,seen={{p.x,p.y,0}},1,{}
	seen[p.x+p.y*m.w]=true
	local chosen
	while queue[head] do
		local q=queue[head];head=head+1
		if q[3]>=20 and q[3]<=28 and not m(q[1],q[2],Map.ACTOR) then chosen=q;break end
		if q[3]<28 then
			for _,d in ipairs{{1,0},{-1,0},{0,1},{0,-1}} do
				local x,y=q[1]+d[1],q[2]+d[2]
				local key=x+y*m.w
				local g=x>=0 and y>=0 and x<m.w and y<m.h and m(x,y,Map.TERRAIN)
				if g and not g.does_block_move and not seen[key] then
					seen[key]=true;queue[#queue+1]={x,y,q[3]+1}
				end
			end
		end
	end
	if not chosen then return {found=false} end
	local from={p.x,p.y}
	local staged=0
	for x=0,m.w-1 do for y=0,m.h-1 do
		if m.seens(x,y) then m.remembers(x,y,true);staged=staged+1 end
	end end
	p:move(chosen[1],chosen[2],true)
	refreshView()
	return {found=true,from=from,to={p.x,p.y},staged_remembered=staged,
		details=M.norgosDetails()}
end

-- For the Kor'Pul per-cell adapter, painted coverage only accumulates as the
-- native FOV reveals cells (superload/engine/Map.lua). To measure whole-map
-- coverage for the expansion plan (not to simulate real play), force
-- Terrain.visible true for one sweep, then restore it immediately after.
function M.terrainCensus()
	guard()
	local m=game.level.map
	local variant=Terrain.variant(game.zone)
	local out={variant=variant or false,checker_mode=game.checker_mode or false}
	if variant then
		local realVisible=Terrain.visible
		Terrain.visible=function() return true end
		local ok,err=pcall(function()
			for x=0,m.w-1 do for y=0,m.h-1 do
				local g=m(x,y,Map.TERRAIN)
				Terrain.observe(m,x,y,g)
				Terrain.render(m,x,y,g,game.checker_mode)
			end end
		end)
		Terrain.visible=realVisible
		assert(ok,err)
		-- record.painted is sticky (never cleared once a cell was drawn in
		-- refined mode); a vanilla-mode read must still count those cells as
		-- native, matching what M.render actually shows in vanilla mode.
		local supported,owned,native=0,0,0
		local refined=game.checker_mode=='refined'
		for _,record in pairs(m._checker_korpul or {}) do
			supported=supported+1
			if refined and record.painted then owned=owned+1 else native=native+1 end
		end
		out.supported,out.owned,out.native=supported,owned,native
		if game.zone.short_name=='dreadfell' or Terrain.combined[game.zone.short_name] then
			local forestTotal,forestOwnedCount=0,0
			local stoneTotal,stoneOwned=0,0
			local kept,supportedIds={},{}
			for x=0,m.w-1 do for y=0,m.h-1 do
				local g=m(x,y,Map.TERRAIN)
				local key=x+y*m.w
				local record=m._checker_korpul and m._checker_korpul[key]
				if record then
					stoneTotal=stoneTotal+1
					local id=record.source or 'unknown'
					supportedIds[id]=(supportedIds[id] or 0)+1
					if refined and record.painted then stoneOwned=stoneOwned+1 end
				elseif Terrain.combined[game.zone.short_name] and forestSupported(g,game.zone.short_name) then
					forestTotal=forestTotal+1
					if forestOwned(g) then forestOwnedCount=forestOwnedCount+1 end
				else
					local id=g and (g.define_as or g.name) or 'nil'
					kept[id]=(kept[id] or 0)+1
				end
			end end
			out.adapters={stone={supported=stoneTotal,owned=stoneOwned,native=stoneTotal-stoneOwned},
				forest={supported=forestTotal,owned=forestOwnedCount,native=forestTotal-forestOwnedCount}}
			out.supported=stoneTotal+forestTotal
			out.owned=stoneOwned+forestOwnedCount
			out.native=out.supported-out.owned
			out.kept_native=kept
			out.supported_ids=supportedIds
		end
	else
		local supported,owned=0,0
		for x=0,m.w-1 do for y=0,m.h-1 do
			local g=m(x,y,Map.TERRAIN)
			if forestSupported(g,game.zone.short_name) then
				supported=supported+1
				if forestOwned(g) then owned=owned+1 end
			end
		end end
		local stray=0
		if m._checker_korpul then for _ in pairs(m._checker_korpul) do stray=stray+1 end end
		out.supported,out.owned,out.native=supported,owned,supported-owned
		out.stray_korpul_records=stray
	end
	return out
end

-- Real production identity path: game:checkerRefreshActor mirrors exactly
-- what runs every tick. For anything left unmapped, CheckerTokens.explain is
-- called again (pure, no side effect) purely to recover a fallback reason.
function M.actorCensus()
	guard()
	local rows={}
	for _,a in pairs(game.level.entities) do
		if a.x and a.y then
			pcall(function() game:checkerRefreshActor(a,'display') end)
			local state=a._checker_token
			local id=state and state.id or false
			local reason=false
			if not id then
				local allow=(a.unique=='player')
				local _,r=Tokens.explain(a,nil,allow)
				reason=r or 'unknown'
			end
			rows[#rows+1]={name=a.name or '?',define_as=a.define_as or false,
				type=a.type or false,subtype=a.subtype or false,image=a.image or false,
				unique=a.unique and tostring(a.unique) or false,rank=a.rank or false,
				x=a.x,y=a.y,id=id,reason=reason,is_player=(a==game.player)}
		end
	end
	local pstate=game.player._checker_token
	return {actors=rows,player_id=(pstate and pstate.id) or false,player_name=game.player.name}
end

-- F1: native DIG on a BOGTREE cell (FLOODED Trollmire only). NicerTiles'
-- superload already calls game:checkerRepairTerrain after every native
-- re-tile (superload/mod/class/NicerTiles.lua), so a plain DIG is the
-- integrated path, same idiom as tests/live_terrain_repair.lua section 2 --
-- no manual repair call here proves the automatic hook, not just M.repair
-- in isolation (that is already covered by tests/terrain_repair.lua).
local DamageType=require 'engine.DamageType'
local function nearestBogtree()
	-- Not gated on current FOV/m.seens: this is a controlled fixture check of
	-- the repair mechanism (same DIG projector entry point as
	-- tests/live_terrain_repair.lua), not a simulation of what the player can
	-- presently see.
	local m,p=game.level.map,game.player
	local best
	for x=0,m.w-1 do for y=0,m.h-1 do
		local g=m(x,y,Map.TERRAIN)
		if g and g.dig and g.subtype=='water' and g.name=='tree' and isBogtreeId(g) then
			local d=math.abs(x-p.x)+math.abs(y-p.y)
			if not best or d<best.d then best={x=x,y=y,d=d,dig=g.dig} end
		end
	end end
	return best
end
function M.focus(x,y)
	guard()
	local m=game.level.map
	m.clean_fov=true;game.player:playerFOV()
	m.smooth_scroll=0;m:centerViewAround(x,y);m:redisplay();m.changed=true
	game.paused=true;core.display.forceRedraw()
end
function M.digBogtree()
	guard()
	local target=nearestBogtree()
	if not target then return {found=false} end
	local before=game.level.map(target.x,target.y,Map.TERRAIN)
	local beforeImage=before.replace_display and before.replace_display.image or false
	DamageType:get(DamageType.DIG).projector(game.player,target.x,target.y,DamageType.DIG,1)
	local after=game.level.map(target.x,target.y,Map.TERRAIN)
	local owned=forestOwned(after)
	return {found=true,x=target.x,y=target.y,dig_target=target.dig,
		before_name='tree',before_image=beforeImage,
		after_name=after.name,after_image=after.replace_display and after.replace_display.image or false,
		after_supported=forestSupported(after,game.zone.short_name),after_owned=owned}
end

-- G0: generic diggable-tree dig for any supported zone, not just water-family
-- bog trees. Covers Old Forest's ordinary TREE (subtype grass in CRYSTALINE,
-- dark_grass in DEFAULT) as well as any zone's BOGTREE, through the same
-- integrated NicerTiles->checkerRepairTerrain hook.
local function nearestDiggableTree(zoneName)
	local m,p=game.level.map,game.player
	local best
	for x=0,m.w-1 do for y=0,m.h-1 do
		local g=m(x,y,Map.TERRAIN)
		if g and g.dig and (g.name=='tree' or (zoneName=='norgos-lair' and g.name=='snowy tree')) then
			local diggable=(g.subtype=='water' and isBogtreeId(g))
				or g.subtype=='grass'
				or (zoneName=='old-forest' and g.subtype=='dark_grass')
				or (zoneName=='norgos-lair' and g.subtype=='rock' and g.dig=='ROCKY_GROUND')
			if diggable then
				local d=math.abs(x-p.x)+math.abs(y-p.y)
				if not best or d<best.d then best={x=x,y=y,d=d,dig=g.dig} end
			end
		end
	end end
	return best
end
function M.digTree()
	guard()
	local zoneName=game.zone.short_name
	local target=nearestDiggableTree(zoneName)
	if not target then return {found=false} end
	local before=game.level.map(target.x,target.y,Map.TERRAIN)
	local beforeImage=before.replace_display and before.replace_display.image or false
	DamageType:get(DamageType.DIG).projector(game.player,target.x,target.y,DamageType.DIG,1)
	local after=game.level.map(target.x,target.y,Map.TERRAIN)
	local owned=forestOwned(after)
	return {found=true,x=target.x,y=target.y,dig_target=target.dig,
		before_name='tree',before_image=beforeImage,
		after_name=after.name,after_image=after.replace_display and after.replace_display.image or false,
		after_supported=forestSupported(after,zoneName),after_owned=owned}
end

function M.digDaikara(kind)
	guard();assert(game.zone.short_name=='daikara')
	assert(kind=='mountain-wall' or kind=='snow-tree')
	local m,p=game.level.map,game.player
	local target
	for x=0,m.w-1 do for y=0,m.h-1 do
		local g=m(x,y,Map.TERRAIN)
		if g and g.dig=='ROCKY_GROUND' and Terrain.rockKind(g,true)==kind then
			local dist=math.abs(x-p.x)+math.abs(y-p.y)
			if not target or dist<target.dist then target={x=x,y=y,dist=dist} end
		end
	end end
	if not target then return {found=false} end
	M.focus(target.x,target.y)
	local before=m(target.x,target.y,Map.TERRAIN)
	local beforeImage=before.replace_display and before.replace_display.image or false
	DamageType:get(DamageType.DIG).projector(p,target.x,target.y,DamageType.DIG,1)
	local after=m(target.x,target.y,Map.TERRAIN)
	return {found=true,x=target.x,y=target.y,before_kind=kind,before_image=beforeImage,
		after_kind=Terrain.rockKind(after,true) or false,
		after_owned=forestOwned(after),
		after_image=after.replace_display and after.replace_display.image or false}
end

function M.gloomDetails()
	guard();assert(game.zone.short_name=='heart-gloom')
	local m=game.level.map
	local ids,kinds,ladders,kept={},{},{},{}
	local skin=game.zone.is_purified and 'dreamy' or 'gloomy'
	for x=0,m.w-1 do for y=0,m.h-1 do
		local g=m(x,y,Map.TERRAIN)
		local k=Terrain.gloomTerrain(g,skin)
		local id=g and g.define_as or 'nil'
		if k then
			ids[id]=(ids[id] or 0)+1;kinds[k]=(kinds[k] or 0)+1
			if k:match('^ladder%-') then ladders[#ladders+1]={x=x,y=y,id=id,kind=k,
				change_level=g.change_level,change_zone=g.change_zone or false,owned=forestOwned(g)} end
		else kept[id]=(kept[id] or 0)+1 end
	end end
	return {ids=ids,kinds=kinds,ladders=ladders,kept_native=kept}
end

function M.gloomOpenPose()
	guard();assert(game.zone.short_name=='heart-gloom')
	local m,p=game.level.map,game.player
	local skin=game.zone.is_purified and 'dreamy' or 'gloomy'
	local best
	for x=8,m.w-9 do for y=8,m.h-9 do
		local g=m(x,y,Map.TERRAIN)
		if g and not g.does_block_move and not g.change_level and not g.change_zone and not m(x,y,Map.ACTOR) then
			local open,creep,wall,exit,near_exit=0,0,0,0,0
			for dx=-6,6 do for dy=-5,5 do
				local t=m(x+dx,y+dy,Map.TERRAIN)
				if t and not t.does_block_move then open=open+1 end
				local k=Terrain.gloomTerrain(t,skin)
				if k=='gloom-creep' then creep=creep+1 elseif k=='gloom-wall' then wall=wall+1
				elseif k and k:match('^ladder%-') then
					exit=exit+1
					if math.abs(dx)<=3 and math.abs(dy)<=3 then near_exit=near_exit+1 end
				end
			end end
			local score=math.min(open,70)+math.min(creep,8)*4+math.min(wall,8)*2+near_exit*1000+exit*100
			if not best or score>best.score then best={x=x,y=y,open=open,creep=creep,wall=wall,exit=exit,near_exit=near_exit,score=score} end
		end
	end end
	if not best then return {found=false} end
	p:move(best.x,best.y,true);p.sight=20;refreshView()
	best.found=true;return best
end

function M.gloomStageView()
	guard();assert(game.zone.short_name=='heart-gloom')
	local m,p=game.level.map,game.player
	local count=0
	for x=math.max(0,p.x-17),math.min(m.w-1,p.x+17) do
		for y=math.max(0,p.y-12),math.min(m.h-1,p.y+12) do
			m.seens(x,y,true);m.infovs(x,y,true);m.remembers(x,y,true)
			count=count+1
		end
	end
	m:redisplay();m.changed=true;core.display.forceRedraw()
	return {staged_cells=count,fixture_only=true}
end

function M.digGloom()
	guard();assert(game.zone.short_name=='heart-gloom')
	local m,p=game.level.map,game.player
	local skin=game.zone.is_purified and 'dreamy' or 'gloomy'
	local target
	for x=0,m.w-1 do for y=0,m.h-1 do
		local g=m(x,y,Map.TERRAIN)
		if Terrain.gloomTerrain(g,skin)=='gloom-wall' then
			local d=math.abs(x-p.x)+math.abs(y-p.y)
			if not target or d<target.d then target={x=x,y=y,d=d} end
		end
	end end
	if not target then return {found=false} end
	M.focus(target.x,target.y)
	local before=m(target.x,target.y,Map.TERRAIN)
	DamageType:get(DamageType.DIG).projector(p,target.x,target.y,DamageType.DIG,1)
	local after=m(target.x,target.y,Map.TERRAIN)
	return {found=true,x=target.x,y=target.y,before_id=before.define_as,
		after_kind=Terrain.gloomTerrain(after,skin) or false,after_owned=forestOwned(after),
		after_id=after.define_as or false}
end

function M.sandDetails()
	guard();assert(game.zone.short_name=='sandworm-lair')
	local m=game.level.map
	local ids,kinds,ladders,kept={},{},{},{}
	for x=0,m.w-1 do for y=0,m.h-1 do
		local g=m(x,y,Map.TERRAIN)
		local k=Terrain.sandTerrain(g)
		local id=g and g.define_as or 'nil'
		if k then
			ids[id]=(ids[id] or 0)+1;kinds[k]=(kinds[k] or 0)+1
			if k:match('^ladder%-') then ladders[#ladders+1]={x=x,y=y,id=id,kind=k,
				change_level=g.change_level,change_zone=g.change_zone or false,owned=forestOwned(g)} end
		else kept[id]=(kept[id] or 0)+1 end
	end end
	return {ids=ids,kinds=kinds,ladders=ladders,kept_native=kept}
end

function M.sandOpenPose()
	guard();assert(game.zone.short_name=='sandworm-lair')
	local m,p=game.level.map,game.player
	local staged_actors=0
	-- Screenshot fixture only: reveal the ladder construction if a monster
	-- happened to spawn directly on the exit in this random map.
	for x=0,m.w-1 do for y=0,m.h-1 do
		local g=m(x,y,Map.TERRAIN)
		if Terrain.sandTerrain(g) and Terrain.sandTerrain(g):match('^ladder%-') then
			local a=m(x,y,Map.ACTOR)
			if a and a~=p then
				for radius=5,12 do
					local moved=false
					for dx=-radius,radius do for dy=-radius,radius do
						local nx,ny=x+dx,y+dy
						if nx>=1 and nx<m.w-1 and ny>=1 and ny<m.h-1 and not m(nx,ny,Map.ACTOR) and
						 Terrain.sandTerrain(m(nx,ny,Map.TERRAIN))=='floor' then
							a:move(nx,ny,true);staged_actors=staged_actors+1;moved=true;break
						end
					end if moved then break end end
					if moved then break end
				end
			end
		end
	end end
	local best
	for x=7,m.w-8 do for y=(m.h<=20 and 4 or 7),(m.h<=20 and m.h-5 or m.h-8) do
		local g=m(x,y,Map.TERRAIN)
		if Terrain.sandTerrain(g)=='floor' and not m(x,y,Map.ACTOR) then
			local floor,wall,exit,near_exit=0,0,0,0
			for dx=-6,6 do for dy=-4,4 do
				local nx,ny=x+dx,y+dy
				if nx>=0 and nx<m.w and ny>=0 and ny<m.h then
					local k=Terrain.sandTerrain(m(nx,ny,Map.TERRAIN))
					if k=='floor' then floor=floor+1 elseif k=='wall' then wall=wall+1
					elseif k and k:match('^ladder%-') and not m(nx,ny,Map.ACTOR) then
						exit=exit+1;if math.abs(dx)<=3 and math.abs(dy)<=3 then near_exit=near_exit+1 end
					end
				end
			end end
			local score=near_exit*1000+exit*100+math.min(floor,70)*2+math.min(wall,8)*3
			if not best or score>best.score then best={x=x,y=y,floor=floor,wall=wall,exit=exit,near_exit=near_exit,score=score} end
		end
	end end
	if not best then return {found=false} end
	p:move(best.x,best.y,true);p.sight=20;refreshView();best.found=true;best.staged_actors=staged_actors;return best
end

function M.sandStageView()
	guard();assert(game.zone.short_name=='sandworm-lair')
	local m,p=game.level.map,game.player
	for x=math.max(0,p.x-17),math.min(m.w-1,p.x+17) do
		for y=math.max(0,p.y-12),math.min(m.h-1,p.y+12) do
			m.seens(x,y,true);m.infovs(x,y,true);m.remembers(x,y,true)
		end
	end
	m:redisplay();m.changed=true;core.display.forceRedraw()
	return {fixture_only=true}
end

function M.sandStageRemembered()
	guard();assert(game.zone.short_name=='sandworm-lair')
	local m,p=game.level.map,game.player
	-- Move within the previously visible open area, then recompute native FOV.
	-- This yields a real remembered region instead of toggling map flags alone.
	local from={p.x,p.y};local best
	for x=math.max(1,p.x-10),math.min(m.w-2,p.x+10) do
		for y=math.max(1,p.y-6),math.min(m.h-2,p.y+6) do
			local distance=math.abs(x-p.x)+math.abs(y-p.y)
			if distance>=7 and Terrain.sandTerrain(m(x,y,Map.TERRAIN))=='floor' and not m(x,y,Map.ACTOR) then
				if not best or distance>best.distance then best={x=x,y=y,distance=distance} end
			end
		end
	end
	assert(best,'no second sand floor pose')
	p:move(best.x,best.y,true);p.sight=5;refreshView()
	local floor,wall=0,0
	for x=math.max(0,p.x-10),math.min(m.w-1,p.x+10) do
		for y=math.max(0,p.y-6),math.min(m.h-1,p.y+6) do
			if m.remembers(x,y) and not m.seens(x,y) then
				local kind=Terrain.sandTerrain(m(x,y,Map.TERRAIN))
				if kind=='floor' then floor=floor+1 elseif kind=='wall' then wall=wall+1 end
			end
		end
	end
	return {fixture_only=true,from=from,to={p.x,p.y},floor=floor,wall=wall}
end

function M.sandCorridorPose()
	guard();assert(game.zone.short_name=='sandworm-lair' and game.level.map.w==350)
	local m,p=game.level.map,game.player
	local best
	for x=100,250 do for y=5,14 do
		if Terrain.sandTerrain(m(x,y,Map.TERRAIN))=='floor' and not m(x,y,Map.ACTOR) then
			local floor,wall=0,0
			for dx=-5,5 do for dy=-4,4 do
				local k=Terrain.sandTerrain(m(x+dx,y+dy,Map.TERRAIN))
				if k=='floor' then floor=floor+1 elseif k=='wall' then wall=wall+1 end
			end end
			local score=math.min(floor,65)+math.min(wall,20)
			if not best or score>best.score then best={x=x,y=y,floor=floor,wall=wall,score=score} end
		end
	end end
	if not best then return {found=false} end
	p:move(best.x,best.y,true);refreshView();best.found=true;return best
end

function M.digSand()
	guard();assert(game.zone.short_name=='sandworm-lair')
	local m,p=game.level.map,game.player
	local source
	for _,e in pairs(game.level.entities) do
		if e.define_as=='SANDWORM_TUNNELER' or e.define_as=='SANDWORM_TUNNELER_HUGE' then source=e;break end
	end
	if not source then return {found=false,reason='no tunneler'} end
	local targets={}
	for x=1,m.w-2 do for y=1,m.h-2 do
		local g=m(x,y,Map.TERRAIN)
		if Terrain.sandTerrain(g)=='wall' then targets[#targets+1]={x=x,y=y} end
	end end
	local dug={}
	for i=1,math.min(3,#targets) do
		local t=targets[math.floor(i*#targets/4)]
		local before=m(t.x,t.y,Map.TERRAIN)
		DamageType:get(DamageType.DIG).projector(source,t.x,t.y,DamageType.DIG,1)
		local after=m(t.x,t.y,Map.TERRAIN)
		dug[#dug+1]={x=t.x,y=t.y,before_id=before.define_as,after_name=after.name,
			is_tunnel=after.tunneler_dig==1,temporary=after.temporary or false,
			owned=forestOwned(after)}
	end
	return {found=true,source=source.define_as,dug=dug,census=M.terrainCensus()}
end

function M.digStone()
	guard()
	local m,p=game.level.map,game.player
	local target
	for x=0,m.w-1 do for y=0,m.h-1 do
		local g=m(x,y,Map.TERRAIN)
		if g and g.dig=='FLOOR' and Terrain.classify(g)=='wall' then
			local d=math.abs(x-p.x)+math.abs(y-p.y)
			if not target or d<target.d then target={x=x,y=y,d=d} end
		end
	end end
	if not target then return {found=false} end
	M.focus(target.x,target.y)
	local before=m(target.x,target.y,Map.TERRAIN)
	local beforeKind=Terrain.classify(before)
	DamageType:get(DamageType.DIG).projector(p,target.x,target.y,DamageType.DIG,1)
	local after=m(target.x,target.y,Map.TERRAIN)
	local record=m._checker_korpul and m._checker_korpul[target.x+target.y*m.w]
	return {found=true,x=target.x,y=target.y,before_kind=beforeKind,
		after_kind=Terrain.classify(after),after_record=record and record.kind or false,
		after_image=Terrain.render(m,target.x,target.y,after,game.checker_mode) and
			Terrain.render(m,target.x,target.y,after,game.checker_mode).image or false}
end

function M.digCrystal()
	guard();assert(game.zone.short_name=='scintillating-caves')
	local m,p=game.level.map,game.player
	local target
	for x=0,m.w-1 do for y=0,m.h-1 do
		local g=m(x,y,Map.TERRAIN)
		if Terrain.crystalTerrain(g)=='wall' then
			local d=math.abs(x-p.x)+math.abs(y-p.y)
			if not target or d<target.d then target={x=x,y=y,d=d} end
		end
	end end
	if not target then return {found=false} end
	M.focus(target.x,target.y)
	local before=m(target.x,target.y,Map.TERRAIN)
	DamageType:get(DamageType.DIG).projector(p,target.x,target.y,DamageType.DIG,1)
	local after=m(target.x,target.y,Map.TERRAIN)
	return {found=true,x=target.x,y=target.y,before_id=before.define_as,
		after_kind=Terrain.crystalTerrain(after) or false,after_owned=forestOwned(after),
		after_id=after.define_as or false,census=M.terrainCensus()}
end

function M.crystalDetails()
	guard();assert(game.zone.short_name=='scintillating-caves')
	local m=game.level.map
	local ids,kinds,ladders,kept={},{},{},{}
	for x=0,m.w-1 do for y=0,m.h-1 do
		local g=m(x,y,Map.TERRAIN)
		local k=Terrain.crystalTerrain(g)
		local id=g and g.define_as or 'nil'
		if k then
			ids[id]=(ids[id] or 0)+1;kinds[k]=(kinds[k] or 0)+1
			if k:match('^ladder%-') then ladders[#ladders+1]={x=x,y=y,id=id,kind=k,
				change_level=g.change_level,change_zone=g.change_zone or false,owned=forestOwned(g)} end
		else kept[id]=(kept[id] or 0)+1 end
	end end
	return {ids=ids,kinds=kinds,ladders=ladders,kept_native=kept}
end

function M.crystalOpenPose()
	guard();assert(game.zone.short_name=='scintillating-caves')
	local m,p=game.level.map,game.player
	local staged_actors=0
	-- Screenshot fixture only: reveal the ladder construction if a monster
	-- happened to spawn directly on the exit in this random map.
	for x=0,m.w-1 do for y=0,m.h-1 do
		local g=m(x,y,Map.TERRAIN)
		if Terrain.crystalTerrain(g) and Terrain.crystalTerrain(g):match('^ladder%-') then
			local a=m(x,y,Map.ACTOR)
			if a and a~=p then
				for radius=5,12 do
					local moved=false
					for dx=-radius,radius do for dy=-radius,radius do
						local nx,ny=x+dx,y+dy
						if nx>=1 and nx<m.w-1 and ny>=1 and ny<m.h-1 and not m(nx,ny,Map.ACTOR) and
						 Terrain.crystalTerrain(m(nx,ny,Map.TERRAIN))=='floor' then
							a:move(nx,ny,true);staged_actors=staged_actors+1;moved=true;break
						end
					end if moved then break end end
					if moved then break end
				end
			end
		end
	end end
	local best
	for x=7,m.w-8 do for y=(m.h<=20 and 4 or 7),(m.h<=20 and m.h-5 or m.h-8) do
		local g=m(x,y,Map.TERRAIN)
		if Terrain.crystalTerrain(g)=='floor' and not m(x,y,Map.ACTOR) then
			local floor,wall,exit,near_exit=0,0,0,0
			for dx=-6,6 do for dy=-4,4 do
				local nx,ny=x+dx,y+dy
				if nx>=0 and nx<m.w and ny>=0 and ny<m.h then
					local k=Terrain.crystalTerrain(m(nx,ny,Map.TERRAIN))
					if k=='floor' then floor=floor+1 elseif k=='wall' then wall=wall+1
					elseif k and k:match('^ladder%-') and not m(nx,ny,Map.ACTOR) then
						exit=exit+1;if math.abs(dx)<=3 and math.abs(dy)<=3 then near_exit=near_exit+1 end
					end
				end
			end end
			local score=near_exit*1000+exit*100+math.min(floor,70)*2+math.min(wall,8)*3
			if not best or score>best.score then best={x=x,y=y,floor=floor,wall=wall,exit=exit,near_exit=near_exit,score=score} end
		end
	end end
	if not best then return {found=false} end
	p:move(best.x,best.y,true);p.sight=20;refreshView();best.found=true;best.staged_actors=staged_actors;return best
end

function M.crystalStageView()
	guard();assert(game.zone.short_name=='scintillating-caves')
	local m,p=game.level.map,game.player
	for x=math.max(0,p.x-17),math.min(m.w-1,p.x+17) do
		for y=math.max(0,p.y-12),math.min(m.h-1,p.y+12) do
			m.seens(x,y,true);m.infovs(x,y,true);m.remembers(x,y,true)
		end
	end
	m:redisplay();m.changed=true;core.display.forceRedraw()
	return {fixture_only=true}
end

function M.crystalStageRemembered()
	guard();assert(game.zone.short_name=='scintillating-caves')
	local m,p=game.level.map,game.player
	-- Move within the previously visible open area, then recompute native FOV.
	-- This yields a real remembered region instead of toggling map flags alone.
	local from={p.x,p.y};local best
	for x=math.max(1,p.x-10),math.min(m.w-2,p.x+10) do
		for y=math.max(1,p.y-6),math.min(m.h-2,p.y+6) do
			local distance=math.abs(x-p.x)+math.abs(y-p.y)
			if distance>=7 and Terrain.crystalTerrain(m(x,y,Map.TERRAIN))=='floor' and not m(x,y,Map.ACTOR) then
				if not best or distance>best.distance then best={x=x,y=y,distance=distance} end
			end
		end
	end
	assert(best,'no second crystal floor pose')
	p:move(best.x,best.y,true);p.sight=5;refreshView()
	local floor,wall=0,0
	for x=math.max(0,p.x-10),math.min(m.w-1,p.x+10) do
		for y=math.max(0,p.y-6),math.min(m.h-1,p.y+6) do
			if m.remembers(x,y) and not m.seens(x,y) then
				local kind=Terrain.crystalTerrain(m(x,y,Map.TERRAIN))
				if kind=='floor' then floor=floor+1 elseif kind=='wall' then wall=wall+1 end
			end
		end
	end
	return {fixture_only=true,from=from,to={p.x,p.y},floor=floor,wall=wall}
end

function M.crystalVaultPose()
	guard();assert(game.zone.short_name=='scintillating-caves' and game.zone.max_level==5)
	local m,p=game.level.map,game.player
	local best
	for x=4,m.w-5 do for y=4,m.h-5 do
		local g=m(x,y,Map.TERRAIN)
		if Terrain.crystalTerrain(g)=='floor' and not m(x,y,Map.ACTOR) then
			local native,wall=0,0
			for dx=-5,5 do for dy=-4,4 do
				local nx,ny=x+dx,y+dy
				local t=m(nx,ny,Map.TERRAIN)
				if t and not Terrain.crystalTerrain(t) then native=native+1 end
				if Terrain.crystalTerrain(t)=='wall' then wall=wall+1 end
			end end
			if native>0 and wall>0 and (not best or native+wall>best.score) then
				best={x=x,y=y,native=native,wall=wall,score=native+wall}
			end
		end
	end end
	if not best then return {found=false} end
	p:move(best.x,best.y,true);p.sight=20;refreshView();best.found=true;return best
end

function M.crystalLitPairs()
	guard();assert(game.zone.short_name=='scintillating-caves')
	local m=game.level.map
	local size=m.tile_w*m.zoom
	local function candidate(x,y,kind)
		if x<0 or y<0 or x>=m.w or y>=m.h or not m.seens(x,y) or not m.infovs(x,y) then return end
		if Terrain.crystalTerrain(m(x,y,Map.TERRAIN))~=kind or m(x,y,Map.ACTOR) or m(x,y,Map.OBJECT) then return end
		local sx,sy=m:getTileToScreen(x,y)
		if sx<m.display_x+size or sy<m.display_y+size or
		 sx+size>m.display_x+m.viewport.width-size or sy+size>m.display_y+m.viewport.height-size then return end
		return {x=x,y=y,sx=sx,sy=sy}
	end
	local pairs={}
	for x=1,m.w-2 do for y=1,m.h-2 do
		local floor=candidate(x,y,'floor')
		if floor then
			for _,d in ipairs{{0,-1},{1,0},{0,1},{-1,0}} do
				local wall=candidate(x+d[1],y+d[2],'wall')
				if wall then pairs[#pairs+1]={floor=floor,wall=wall} end
			end
		end
	end end
	return {tile=size,pairs=pairs,shown=m.color_shown}
end


function M.caveDetails()
	guard();assert(game.zone.short_name=='unremarkable-cave')
	local m=game.level.map
	local ids,kinds,regions,kept,exits={},{},{generated={},seam={},static={}},{},{}
	for x=0,m.w-1 do for y=0,m.h-1 do
		local g=m(x,y,Map.TERRAIN);local id=g and g.define_as or 'nil'
		local k=Terrain.caveTerrain(g)
		local region=x<85 and 'generated' or x<=87 and 'seam' or 'static'
		if k then
			ids[id]=(ids[id] or 0)+1;kinds[k]=(kinds[k] or 0)+1
			regions[region][k]=(regions[region][k] or 0)+1
			if k=='ladder-world' then exits[#exits+1]={x=x,y=y,id=id,owned=forestOwned(g),zone=g.change_zone,level=g.change_level} end
		else kept[id]=(kept[id] or 0)+1 end
	end end
	return {ids=ids,kinds=kinds,regions=regions,kept_native=kept,exits=exits}
end

function M.cavePose(seam)
	guard();assert(game.zone.short_name=='unremarkable-cave')
	local m,p=game.level.map,game.player;local best
	local exitx,exity
	for x=0,m.w-1 do for y=0,m.h-1 do
		if Terrain.caveTerrain(m(x,y,Map.TERRAIN))=='ladder-world' then exitx,exity=x,y end
	end end
	local xmin,xmax=seam and 76 or 5,seam and 91 or 17
	for x=xmin,xmax do for y=(seam and 5 or 1),(seam and m.h-6 or m.h-2) do
		if Terrain.caveTerrain(m(x,y,Map.TERRAIN))=='floor' and not m(x,y,Map.ACTOR) then
			local floor,wall,exit=0,0,0
			for dx=-5,5 do for dy=-4,4 do
				local nx,ny=x+dx,y+dy
				if nx>=0 and ny>=0 and nx<m.w and ny<m.h then
					local k=Terrain.caveTerrain(m(nx,ny,Map.TERRAIN))
					if k=='floor' then floor=floor+1 elseif k=='wall' then wall=wall+1 elseif k=='ladder-world' then exit=exit+1 end
				end
			end end
			local nearExit=exitx and math.abs(x-exitx)<=12 and math.abs(y-exity)<=10
			local score=math.min(floor,50)*2+math.min(wall,10)*3+
			 (seam and (x>=83 and 200 or 0) or nearExit and 500 or 0)
			if floor>4 and wall>0 and (not best or score>best.score) then best={x=x,y=y,floor=floor,wall=wall,exit=exit,near_exit=nearExit and true or false,score=score} end
		end
	end end
	if not best then return {found=false} end
	p:move(best.x,best.y,true);p.sight=20;dismissDialogs();refreshView();dismissDialogs();core.display.forceRedraw();best.found=true;best.seam=seam and true or false
	return best
end

function M.caveExitPose()
	guard();assert(game.zone.short_name=='unremarkable-cave')
	local m,p=game.level.map,game.player;local ex,ey
	for x=0,m.w-1 do for y=0,m.h-1 do
		if Terrain.caveTerrain(m(x,y,Map.TERRAIN))=='ladder-world' then ex,ey=x,y end
	end end
	assert(ex,'world ladder missing')
	local best
	for x=math.max(0,ex-5),math.min(m.w-1,ex+5) do for y=math.max(0,ey-5),math.min(m.h-1,ey+5) do
		if Terrain.caveTerrain(m(x,y,Map.TERRAIN))=='floor' and not m(x,y,Map.ACTOR) then
			local d=math.abs(x-ex)+math.abs(y-ey)
			if not best or d<best.d then best={x=x,y=y,d=d} end
		end
	end end
	assert(best,'no floor next to cave exit')
	p:move(best.x,best.y,true);p.sight=20;dismissDialogs();refreshView()
	return {exit={ex,ey},player={best.x,best.y},distance=best.d}
end

function M.caveLitPairs()
	guard();assert(game.zone.short_name=='unremarkable-cave')
	local m=game.level.map;local size=m.tile_w*m.zoom
	local function candidate(x,y,kind)
		if x<0 or y<0 or x>=m.w or y>=m.h or not m.seens(x,y) or not m.infovs(x,y) then return end
		if Terrain.caveTerrain(m(x,y,Map.TERRAIN))~=kind or m(x,y,Map.ACTOR) or m(x,y,Map.OBJECT) then return end
		local sx,sy=m:getTileToScreen(x,y)
		if sx<m.display_x+size or sy<m.display_y+size or
		 sx+size>m.display_x+m.viewport.width-size or sy+size>m.display_y+m.viewport.height-size then return end
		return {x=x,y=y,sx=sx,sy=sy}
	end
	local pairs={}
	for x=1,m.w-2 do for y=1,m.h-2 do
		local floor=candidate(x,y,'floor')
		if floor then for _,d in ipairs{{0,-1},{1,0},{0,1},{-1,0}} do
			local wall=candidate(x+d[1],y+d[2],'wall')
			if wall then pairs[#pairs+1]={floor=floor,wall=wall} end
		end end
	end end
	return {tile=size,pairs=pairs,shown=m.color_shown}
end

function M.caveStageView()
	guard();assert(game.zone.short_name=='unremarkable-cave')
	local m,p=game.level.map,game.player
	for x=math.max(0,p.x-17),math.min(m.w-1,p.x+17) do
		for y=math.max(0,p.y-12),math.min(m.h-1,p.y+12) do
			m.seens(x,y,true);m.infovs(x,y,true);m.remembers(x,y,true)
		end
	end
	m:redisplay();m.changed=true;core.display.forceRedraw()
	return {fixture_only=true}
end

function M.caveClearDialogs()
	guard();dismissDialogs();core.display.forceRedraw()
	return {fixture_only=true}
end

function M.caveRemembered()
	guard();assert(game.zone.short_name=='unremarkable-cave')
	local m,p=game.level.map,game.player;local from={p.x,p.y};local best
	for x=math.max(1,p.x-11),math.min(m.w-2,p.x+11) do for y=math.max(1,p.y-7),math.min(m.h-2,p.y+7) do
		local distance=math.abs(x-p.x)+math.abs(y-p.y)
		if distance>=7 and Terrain.caveTerrain(m(x,y,Map.TERRAIN))=='floor' and not m(x,y,Map.ACTOR) and
		 (not best or distance>best.distance) then best={x=x,y=y,distance=distance} end
	end end
	assert(best,'no second cave floor pose')
	p:move(best.x,best.y,true);p.sight=5;refreshView()
	local floor,wall=0,0
	for x=math.max(0,p.x-12),math.min(m.w-1,p.x+12) do for y=math.max(0,p.y-8),math.min(m.h-1,p.y+8) do
		if m.remembers(x,y) and not m.seens(x,y) then
			local k=Terrain.caveTerrain(m(x,y,Map.TERRAIN))
			if k=='floor' then floor=floor+1 elseif k=='wall' then wall=wall+1 end
		end
	end end
	return {from=from,to={p.x,p.y},floor=floor,wall=wall,native_fov_recomputed=true}
end

function M.digCave()
	guard();assert(game.zone.short_name=='unremarkable-cave')
	local m,p=game.level.map,game.player;local target
	for x=1,m.w-2 do for y=1,m.h-2 do
		if Terrain.caveTerrain(m(x,y,Map.TERRAIN))=='wall' then
			local d=math.abs(x-p.x)+math.abs(y-p.y)
			if not target or d<target.d then target={x=x,y=y,d=d} end
		end
	end end
	if not target then return {found=false} end
	M.focus(target.x,target.y)
	local before=m(target.x,target.y,Map.TERRAIN)
	DamageType:get(DamageType.DIG).projector(p,target.x,target.y,DamageType.DIG,1)
	local after=m(target.x,target.y,Map.TERRAIN)
	return {found=true,x=target.x,y=target.y,before_id=before.define_as,after_id=after.define_as,
	 after_kind=Terrain.caveTerrain(after) or false,after_owned=forestOwned(after),census=M.terrainCensus()}
end

-- Reuse-batch fixture probes. These use the production identity predicates;
-- only the view pose and screenshots are staged in this disposable fixture.
local function reuseKind(g)
	local zone=game.zone.short_name
	if batch5Families[zone] then
		local stone=Terrain.variant(game.zone) and Terrain.classify(g)
		if stone then return stone end
		local k=Terrain.batch5Kind(g,batch5Families[zone])
		if not k then return end
		if k:match('^stairs%-') or k=='exit-world' then return 'exit' end
		return (k=='wall' or k=='lava-wall' or k=='door-closed') and 'wall' or (k=='floor' or k=='lava-floor' or k=='door-open') and 'floor' or k
	end
	if zone=='briagh-lair' then local k=Terrain.sandTerrain(g);return k and k:match('^ladder') and 'exit' or k end
	if zone=='valley-moon-caverns' then
		local k=Terrain.caveTerrain(g) or Terrain.valleyExit(g)
		return k and k:match('^ladder') and 'exit' or k
	end
	if zone=='orc-breeding-pit' and game.level.level~=1 then
		local kind=Terrain.gloomTerrain(g,'plain')
		return kind=='gloom-wall' and 'wall' or (kind=='gloom-floor' or kind=='gloom-creep') and 'floor' or kind and 'exit'
	end
	if underwaterZones[zone] then
		local k=Terrain.underwaterKind(g)
		return k=='door-closed' and 'wall' or k=='door-open' and 'floor' or
			k and k:match('^stairs%-') and 'exit' or k
	end
	if batch4Families[zone] then
		local k=Terrain.batch4Kind(g,batch4Families[zone])
		if not k then return end
		if k=='tree' or k=='hardtree' or k=='wall' or k=='cave-wall' or k=='stew' or k=='umbrella' then return 'wall' end
		if k=='exit' or k:match('^exit%-') or k:match('^cave%-ladder') then return 'exit' end
		if k=='deep' or k=='poison' then return 'water' end
		return 'floor'
	end
	if zone=='lake-nur' and game.level.level==1 or
		zone=='temporal-rift' and game.level.level==4 then
		local k=Terrain.underwaterKind(g)
		if k then return k=='door-closed' and 'wall' or k=='door-open' and 'floor' or
			k=='wall' and 'wall' or k and k:match('^stairs%-') and 'exit' or 'floor' end
		if Terrain.surfaceSandKind(g) then return 'floor' end
	end
	if zone=='lake-nur' and (game.level.level==2 or
		game.level.level==3 and game.zone.is_flooded) then
		local k=Terrain.underwaterKind(g)
		return k=='door-closed' and 'wall' or k=='door-open' and 'floor' or
			k and k:match('^stairs%-') and 'exit' or k
	end
	if zone=='lake-nur' and game.level.level==3 then return Terrain.classify(g) end
	if zone=='unhallowed-morass' or zone=='abashed-expanse' or
		zone=='temporal-rift' and game.level.level==1 then
		if zone=='abashed-expanse' and Terrain.abashedTreeKind(g) then return 'wall' end
		local kind=Terrain.voidTerrain(g,zone)
		return (kind=='floor' or kind=='rocks') and 'floor' or
			(kind=='rift' or kind=='space') and 'wall' or nil
	end
	if zone=='temporal-rift' and game.level.level==3 then return Terrain.rockKind(g,true) end
	if game.zone.short_name=='tempest-peak' then return Terrain.rockKind(g,true) end
	if game.zone.short_name=='ardhungol' then return Terrain.caveTerrain(g) end
	if game.zone.short_name=='deep-bellow' then
		local kind=Terrain.gloomTerrain(g,'plain')
		return kind=='gloom-wall' and 'wall' or (kind=='gloom-floor' or kind=='gloom-creep') and 'floor' or kind
	end
	if game.zone.short_name=='ritch-tunnels' then return Terrain.sandTerrain(g) end
	if game.zone.short_name=='last-hope-graveyard' then
		local stone=Terrain.classify(g)
		if stone then return stone end
		local prop=Terrain.graveyardProp(g)
		if prop then return prop=='swamp-tree' and 'wall' or 'floor' end
		if not forestSupported(g,game.zone.short_name) then return end
	end
	if zone=='temporal-rift' then
		local stone=Terrain.classify(g)
		if stone then return stone end
	end
	if game.zone.short_name=='lake-nur' or game.zone.short_name=='golem-graveyard' or game.zone.short_name=='last-hope-graveyard' or zone=='temporal-rift' then
		local state=g and g._checker_terrain
		if not state or g.replace_display~=state.display then return end
		local image=state.display.image or ''
		if image:find('/tree') or image:find('/bog%-tree') then return 'wall' end
		if image:find('/exit') then return 'exit' end
		return 'floor'
	end
	return Terrain.classify(g)
end
function M.reuseDetails()
	guard()
	local m=game.level.map;local ids,kept,exits,why={},{},{},{}
	for x=0,m.w-1 do for y=0,m.h-1 do
		local g=m(x,y,Map.TERRAIN);local id=g and (g.define_as or g.name) or 'nil'
		local kind=reuseKind(g)
		local bucket=kind and ids or kept;bucket[id]=(bucket[id] or 0)+1
		if g and not kind then
			-- Why a cell stays native: its name and callbacks (event sources).
			local funcs={}
			for k,v in pairs(g) do if type(v)=='function' then
				local info=debug.getinfo(v,'S');funcs[#funcs+1]=k..'@'..tostring(info and info.short_src)
			end end
			table.sort(funcs)
			local key=id..'|'..tostring(g.name)..'|'..table.concat(funcs,',')..'|'..tostring(g.add_displays and #g.add_displays or 0)
			why[key]=(why[key] or 0)+1
		end
		if g and (g.change_level or g.change_zone) then exits[#exits+1]={x=x,y=y,id=id,kind=kind or false} end
	end end
	return {supported_ids=ids,kept_native=kept,kept_reasons=why,exits=exits}
end
function M.t5PropPose()
	guard()
	local zone=game.zone.short_name
	assert(zone=='abashed-expanse' or zone=='last-hope-graveyard')
	local m,p=game.level.map,game.player
	local target
	for x=1,m.w-2 do for y=1,m.h-2 do
		local g=m(x,y,Map.TERRAIN)
		local kind=zone=='abashed-expanse' and Terrain.abashedTreeKind(g) or Terrain.graveyardProp(g)
		if kind=='rocks-tree' or kind=='swamp-tree' or kind=='road' then
			for _,d in ipairs{{0,1},{1,0},{0,-1},{-1,0}} do
				local px,py=x+d[1],y+d[2]
				local nextg=m(px,py,Map.TERRAIN)
				if nextg and not nextg.does_block_move and not m(px,py,Map.ACTOR) then
					target={x=x,y=y,pose={px,py},kind=kind};break
				end
			end
		end
		if target then break end
	end if target then break end end
	if not target then return {found=false} end
	p:move(target.pose[1],target.pose[2],true);p.sight=20;refreshView()
	target.found=true
	return target
end
function M.t5RuleSnapshot()
	guard();assert(game.zone.short_name=='lake-nur')
	local m=game.level.map
	local out={}
	for x=0,m.w-1 do for y=0,m.h-1 do
		local g=m(x,y,Map.TERRAIN)
		local id=g and g.define_as or ''
		local family=id:match('^WATER_FLOOR[1-5]?$') and 'floor' or
			id:match('^WATER_WALL') and 'wall' or
			id:match('^WATER_DOOR') and 'door' or
			id=='WATER_FLOOR_BUBBLE' and 'bubble'
		if family and not out[family] then
			out[family]={id=id,air_level=g.air_level or false,
				air_condition=g.air_condition or false,does_block_move=g.does_block_move or false,
				block_sight=g.block_sight or false,dig=type(g.dig)=='string' and g.dig or false,
				pass_wall=g.can_pass and g.can_pass.pass_wall or false,
				is_door=g.is_door or false,door_opened=g.door_opened or false,
				door_closed=g.door_closed or false,has_on_stand=type(g.on_stand)=='function'}
		end
	end end
	return out
end
function M.reusePose(exit)
	guard()
	local m,p=game.level.map,game.player;local best
	local exits={}
	if exit then for ex=0,m.w-1 do for ey=0,m.h-1 do
		local t=m(ex,ey,Map.TERRAIN)
		if t and (t.change_level or t.change_zone) then exits[#exits+1]={x=ex,y=ey} end
	end end end
	for x=2,m.w-3 do for y=2,m.h-3 do
		local g=m(x,y,Map.TERRAIN)
		if g and not g.does_block_move and not m(x,y,Map.ACTOR) then
			local floors,walls=0,0
			for dx=-4,4 do for dy=-4,4 do
				local t=m(x+dx,y+dy,Map.TERRAIN)
				local k=reuseKind(t)
				if k=='floor' or k=='rock-ground' then floors=floors+1
				elseif k=='wall' or k=='old-wall' or k=='mountain-wall' then walls=walls+1 end
			end end
			local nearest=999
			if exit then for _,e in ipairs(exits) do nearest=math.min(nearest,math.abs(x-e.x)+math.abs(y-e.y)) end end
			local wanted=exit and (1000-nearest*50) or 0
			local score=wanted+floors+math.min(walls,12)*3
			if floors>0 and (not best or score>best.score) then best={x=x,y=y,score=score,floors=floors,walls=walls,exit=nearest<=8,exit_distance=nearest} end
		end
	end end
	if not best then return {found=false} end
	p:move(best.x,best.y,true);p.sight=20;refreshView();best.found=true;return best
end
function M.reuseStageView()
	guard()
	local m,p=game.level.map,game.player
	for x=math.max(0,p.x-17),math.min(m.w-1,p.x+17) do for y=math.max(0,p.y-12),math.min(m.h-1,p.y+12) do
		m.seens(x,y,true);m.infovs(x,y,true);m.remembers(x,y,true)
	end end
	m:redisplay();m.changed=true;core.display.forceRedraw()
end
function M.reuseRemembered()
	guard()
	local m,p=game.level.map,game.player
	local oldx,oldy=p.x,p.y
	local best
	for x=1,m.w-2 do for y=1,m.h-2 do
		local g=m(x,y,Map.TERRAIN)
		local d=math.abs(x-oldx)+math.abs(y-oldy)
		if g and not g.does_block_move and not m(x,y,Map.ACTOR) and d>=18 and d<=26 and
			(not best or d<best.distance) then best={x=x,y=y,distance=d} end
	end end
	if not best then return {found=false} end
	p:move(best.x,best.y,true);p.sight=7;refreshView()
	return {found=true,old={x=oldx,y=oldy,remembered=m.remembers(oldx,oldy),visible=m.seens(oldx,oldy)},
		new={x=best.x,y=best.y}}
end
function M.batch3Dig()
	guard()
	local zone=game.zone.short_name
	assert(zone=='ritch-tunnels' or zone=='deep-bellow')
	local m,p=game.level.map,game.player
	local target
	for x=1,m.w-2 do for y=1,m.h-2 do
		local g=m(x,y,Map.TERRAIN)
		local kind=zone=='ritch-tunnels' and Terrain.sandTerrain(g) or Terrain.gloomTerrain(g,'plain')
		if kind==(zone=='ritch-tunnels' and 'wall' or 'gloom-wall') and g.dig and
			(not target or math.abs(x-p.x)+math.abs(y-p.y)<target.distance) then
			target={x=x,y=y,distance=math.abs(x-p.x)+math.abs(y-p.y)}
		end
	end end
	if not target then return {found=false} end
	M.focus(target.x,target.y)
	local before=m(target.x,target.y,Map.TERRAIN)
	DamageType:get(DamageType.DIG).projector(p,target.x,target.y,DamageType.DIG,1)
	local after=m(target.x,target.y,Map.TERRAIN)
	return {found=true,before=before.define_as,after=after.define_as,
		after_kind=zone=='ritch-tunnels' and (Terrain.sandTerrain(after) or false) or
			(Terrain.gloomTerrain(after,'plain') or false),owned=forestOwned(after),census=M.terrainCensus()}
end
function M.reuseLitPairs()
	guard()
	local m=game.level.map;local size=m.tile_w*m.zoom;local pairs={}
	local function candidate(x,y,kinds)
		if x<0 or y<0 or x>=m.w or y>=m.h or not m.seens(x,y) or not m.infovs(x,y) then return end
		local kind=reuseKind(m(x,y,Map.TERRAIN))
		if not kinds[kind] or m(x,y,Map.ACTOR) or m(x,y,Map.OBJECT) then return end
		local sx,sy=m:getTileToScreen(x,y)
		if sx<m.display_x+size or sy<m.display_y+size or sx+size>m.display_x+m.viewport.width-size or sy+size>m.display_y+m.viewport.height-size then return end
		return {x=x,y=y,sx=sx,sy=sy}
	end
	for x=1,m.w-2 do for y=1,m.h-2 do
		local floor=candidate(x,y,{floor=true,['rock-ground']=true})
		if floor then for _,d in ipairs{{0,-1},{1,0},{0,1},{-1,0}} do
			local wall=candidate(x+d[1],y+d[2],{wall=true,hardwall=true,['old-wall']=true,['mountain-wall']=true})
			if wall then pairs[#pairs+1]={floor=floor,wall=wall} end
		end end
	end end
	return {tile=size,pairs=pairs,shown=m.color_shown}
end

function M.voidExitPose()
	guard()
	local m,p=game.level.map,game.player
	local target
	for x=0,m.w-1 do for y=0,m.h-1 do
		local g=m(x,y,Map.TERRAIN)
		if g and (g.define_as=='RIFT' or g.define_as=='RIFT_HOME' or g.define_as=='WORMHOLE') then
			target={x=x,y=y,id=g.define_as,change_level=g.change_level or false,
				callback=type(g.damage_project)=='function' or type(g.change_level_check)=='function'}
		end
	end end
	if not target then return {found=false} end
	local best
	for x=math.max(0,target.x-5),math.min(m.w-1,target.x+5) do
	for y=math.max(0,target.y-5),math.min(m.h-1,target.y+5) do
		local g=m(x,y,Map.TERRAIN)
		local d=math.abs(x-target.x)+math.abs(y-target.y)
		if g and not g.does_block_move and not m(x,y,Map.ACTOR) and d>0 and
			(not best or d<best.d) then best={x=x,y=y,d=d} end
	end end
	if not best then return {found=false,reason='no adjacent walkable pose'} end
	p:move(best.x,best.y,true);p.sight=20;refreshView()
	target.found=true;target.pose=best
	return target
end

function M.spellblazeDetails()
	guard();assert(game.zone.short_name=='mark-spellblaze')
	local m=game.level.map;local ids,kept,kinds,exits={},{},{},{}
	for x=0,m.w-1 do for y=0,m.h-1 do
		local g=m(x,y,Map.TERRAIN);local id=g and (g.define_as or g.name) or 'nil'
		local k=Terrain.burntTerrain(g)
		local bucket=k and ids or kept;bucket[id]=(bucket[id] or 0)+1
		if k then kinds[k]=(kinds[k] or 0)+1 end
		if g and (g.change_level or g.change_zone) then exits[#exits+1]={x=x,y=y,id=id,kind=k or false} end
	end end
	return {supported_ids=ids,kept_native=kept,kinds=kinds,exits=exits}
end
function M.spellblazePose(prefer)
	guard();assert(game.zone.short_name=='mark-spellblaze')
	local m,p=game.level.map,game.player;local best
	for x=3,m.w-4 do for y=3,m.h-4 do
		if Terrain.burntTerrain(m(x,y,Map.TERRAIN))=='floor' and not m(x,y,Map.ACTOR) then
			local floors,trees,lava,exits=0,0,0,0
			for dx=-7,7 do for dy=-5,5 do
				local xx,yy=x+dx,y+dy
				if xx>=0 and yy>=0 and xx<m.w and yy<m.h then
					local k=Terrain.burntTerrain(m(xx,yy,Map.TERRAIN))
					if k=='floor' then floors=floors+1 elseif k=='tree' then trees=trees+1
					elseif k=='lava' then lava=lava+1 elseif k and k:match('^exit%-') then exits=exits+1 end
				end
			end end
			local score=floors+math.min(trees,12)*4+(prefer=='lava' and lava*8 or 0)+(prefer=='exit' and exits*100 or 0)
			if floors>=20 and trees>=2 and (not best or score>best.score) then
				best={x=x,y=y,floors=floors,trees=trees,lava=lava,exits=exits,score=score}
			end
		end
	end end
	if not best then return {found=false} end
	p:move(best.x,best.y,true);p.sight=20;refreshView();best.found=true;return best
end
function M.spellblazeLitPairs()
	guard();assert(game.zone.short_name=='mark-spellblaze')
	local m=game.level.map;local size=m.tile_w*m.zoom;local pairs={}
	local function candidate(x,y,kind)
		if x<0 or y<0 or x>=m.w or y>=m.h or not m.seens(x,y) or not m.infovs(x,y) then return end
		if Terrain.burntTerrain(m(x,y,Map.TERRAIN))~=kind or m(x,y,Map.ACTOR) or m(x,y,Map.OBJECT) then return end
		local sx,sy=m:getTileToScreen(x,y)
		if sx<m.display_x+size or sy<m.display_y+size or
		 sx+size>m.display_x+m.viewport.width-size or sy+size>m.display_y+m.viewport.height-size then return end
		return {x=x,y=y,sx=sx,sy=sy}
	end
	for x=1,m.w-2 do for y=1,m.h-2 do
		local floor=candidate(x,y,'floor')
		if floor then for _,d in ipairs{{0,-1},{1,0},{0,1},{-1,0}} do
			local tree=candidate(x+d[1],y+d[2],'tree')
			if tree then pairs[#pairs+1]={floor=floor,wall=tree} end
		end end
	end end
	return {tile=size,pairs=pairs}
end
function M.spellblazeDig()
	guard();assert(game.zone.short_name=='mark-spellblaze')
	local m,p=game.level.map,game.player;local target
	for x=1,m.w-2 do for y=1,m.h-2 do
		if Terrain.burntTerrain(m(x,y,Map.TERRAIN))=='tree' then
			local d=math.abs(x-p.x)+math.abs(y-p.y)
			if not target or d<target.d then target={x=x,y=y,d=d} end
		end
	end end
	if not target then return {found=false} end
	M.focus(target.x,target.y)
	local before=m(target.x,target.y,Map.TERRAIN)
	DamageType:get(DamageType.DIG).projector(p,target.x,target.y,DamageType.DIG,1)
	local after=m(target.x,target.y,Map.TERRAIN)
	return {found=true,before=before.define_as,after=after.define_as,
		after_kind=Terrain.burntTerrain(after) or false,owned=forestOwned(after),census=M.terrainCensus()}
end

-- Batch 4 source probe: one descriptor per distinct final identity/appearance.
local function layerImages(list)
	local out={}
	for _,d in ipairs(list or {}) do
		local row={image=d.image or false,z=d.z or false,display_x=d.display_x or false,
			display_y=d.display_y or false,display_w=d.display_w or false,
			display_h=d.display_h or false,shader=d.shader or false}
		local mos={}
		for _,mo in ipairs(d.add_mos or {}) do mos[#mos+1]=mo.image or false end
		row.add_mos=mos
		out[#out+1]=row
	end
	return out
end
function M.batch4Probe()
	guard()
	local m=game.level.map;local seen,rows={}, {}
	for x=0,m.w-1 do for y=0,m.h-1 do
		local g=m(x,y,Map.TERRAIN)
		if g then
			local funcs={}
			for k,v in pairs(g) do if type(v)=='function' then funcs[#funcs+1]=k end end
			table.sort(funcs)
			local shape={}
			for _,d in ipairs(g.add_displays or {}) do
				shape[#shape+1]=tostring(d.image)
				for _,mo in ipairs(d.add_mos or {}) do shape[#shape+1]='+'..tostring(mo.image) end
			end
			for _,mo in ipairs(g.add_mos or {}) do shape[#shape+1]='mo:'..tostring(mo.image) end
			local key=tostring(g.define_as)..'|'..tostring(g.image)..'|'..table.concat(shape,',')..'|'..table.concat(funcs,',')
			if not seen[key] then
				seen[key]={id=g.define_as or false,name=g.name or false,type=g.type or false,
					subtype=g.subtype or false,image=g.image or false,display=g.display or false,
					does_block_move=g.does_block_move or false,block_sight=g.block_sight or false,
					pass_projectile=g.pass_projectile or false,dig=type(g.dig)=='string' and g.dig or (g.dig and 'fn') or false,
					can_pass=g.can_pass or false,change_level=g.change_level or false,
					change_zone=g.change_zone or false,notice=g.notice or false,
					always_remember=g.always_remember or false,air_level=g.air_level or false,
					air_condition=g.air_condition or false,shader=g.shader or false,
					tint=g.tint or false,z=g.z or false,grow=g.grow or false,
					is_door=g.is_door or false,door_opened=g.door_opened or false,door_closed=g.door_closed or false,
					block_sense=g.block_sense or false,block_esp=g.block_esp or false,
					special=g.special or false,functions=funcs,
					add_displays=layerImages(g.add_displays),add_mos=layerImages(g.add_mos),
					stamps={grid=g._checker_grid_source and g._checker_grid_source.file or false,
						cave=g._checker_cave_source and g._checker_cave_source.file or false,
						water=g._checker_water_source and g._checker_water_source.file or false,
						sand=g._checker_surface_sand_source and g._checker_surface_sand_source.file or false},
					replaced=g.replace_display and true or false,count=0,first={x=x,y=y}}
				rows[#rows+1]=seen[key]
			end
			seen[key].count=seen[key].count+1
		end
	end end
	return {zone=game.zone.short_name,level=game.level.level,w=m.w,h=m.h,rows=rows}
end

-- Batch 4 rule/callback snapshot: first cell of every identity, including the
-- callback grids the adapter must leave untouched. Function bodies are
-- compared by a checksum of string.dump plus their defining file/line.
local function dumpSum(fn)
	if type(fn)~='function' then return false end
	local ok,code=pcall(string.dump,fn)
	if not ok then return 'undumpable' end
	local a,b=1,0
	for i=1,#code do a=(a+code:byte(i))%65521;b=(b+a)%65521 end
	local info=debug.getinfo(fn,'S')
	return ('%d:%d:%s:%d'):format(#code,b*65536+a,info.source,info.linedefined)
end
function M.batch4RuleSnapshot()
	guard()
	local m=game.level.map;local out={}
	local keys={'type','subtype','does_block_move','block_sight','pass_projectile','block_sense','block_esp',
		'dig','air_level','air_condition','change_level','change_zone','is_door','door_opened','door_closed',
		'notice','always_remember','mindam','maxdam','nb_charges','grow','triggered','on_stand_safe'}
	for x=0,m.w-1 do for y=0,m.h-1 do
		local g=m(x,y,Map.TERRAIN)
		local id=g and (g.define_as or g.name)
		if id and not out[id] then
			local row={count=0}
			for _,k in ipairs(keys) do local v=g[k];row[k]=type(v)=='table' and 'table' or v==nil and false or v end
			row.can_pass=g.can_pass and table.concat((function() local t={} for k,v in pairs(g.can_pass) do t[#t+1]=k..'='..tostring(v) end table.sort(t) return t end)(),',') or false
			for _,k in ipairs{'on_stand','on_move','block_move','change_level_check','combatAttack','on_added','on_dig'} do
				row[k]=dumpSum(rawget(g,k) or (k~='on_move' and k~='block_move' and g[k]) or nil)
			end
			out[id]=row
		end
		if id then out[id].count=out[id].count+1 end
	end end
	return out
end
local function batch4Feature(g)
	local zone=game.zone.short_name
	if zone=='charred-scar' or zone=='demon-plane' then return Terrain.batch5Kind(g,'scorch')=='lava' and 'lava' end
	if zone=='shertul-fortress' then return g and g.define_as=='COMMAND_ORB' and 'native-orb' end
	if zone=='rak-shor-pride' then
		if g and g.define_as=='BONE_GENERIC_LEVER' then return 'native-lever' end
		local k=Terrain.batch5Kind(g,'rakshor');return (k=='door-closed' or k=='stairs-down' or k=='stairs-up') and k
	end
	if zone=='valley-moon-caverns' then
		return (Terrain.valleyExit(g) and 'exit-valley') or (g and g.name=='glimmerstone' and 'native-glimmerstone')
	end
	if zone=='ancient-elven-ruins' then return g and g.define_as=='QUICK_EXIT' and 'native-exit' end
	if zone=='vor-armoury' then return g and (g.define_as=='DOOR_VAULT_VERT' or g.define_as=='DOOR_VAULT_HORIZ') and 'native-door' or
		Terrain.classify(g)=='door-closed' and 'door-closed' end
	if zone=='telmur' or zone=='orc-breeding-pit' and game.level.level==1 then
		local k=Terrain.classify(g);return (k=='door-closed' or k and k:match('^stairs%-')) and k
	end
	if zone=='orc-breeding-pit' then local k=Terrain.gloomTerrain(g,'plain');return k and k:match('^ladder') and k end
	if zone=='briagh-lair' then local k=Terrain.sandTerrain(g);return k and k:match('^ladder') and k end
	if underwaterZones[zone] then
		local k=Terrain.underwaterKind(g)
		return (k=='stairs-world' or k=='door-closed' or k=='stairs-down' or k=='stairs-up') and k
	end
	if zone=='conclave-vault' then
		local k=Terrain.classify(g)
		return (k=='deco-floor' or k=='door-closed' or k and k:match('^stairs%-')) and k
	end
	local k=batch4Families[zone] and Terrain.batch4Kind(g,batch4Families[zone])
	if not k then return end
	if zone=='south-beach' then return (k=='umbrella' or k=='basket' or k=='deep') and k end
	if zone=='keepsake-meadow' then
		return (k=='stew' or Terrain.keepsakeEvent(g) or k=='deep' or k:match('^cave%-ladder') or k=='exit') and k
	end
	return (k=='poison' or k:match('^exit%-')) and k
end
function M.batch4FeaturePose()
	guard()
	local m,p=game.level.map,game.player
	local priority={['exit-valley']=1,['native-orb']=1,['native-lever']=1,['native-exit']=1,['native-door']=1,['native-glimmerstone']=3,lava=1,
		['ladder-world']=2,['ladder-up']=2,['ladder-down']=2,['stairs-up']=3,['stairs-down']=3,['stairs-world']=1,umbrella=1,stew=1,['deco-floor']=1,poison=2,['cave-floor']=1,grass=1,
		['exit-world']=3,['exit-up']=3,['exit-down']=3,deep=4,basket=2,exit=3,['door-closed']=4}
	-- Candidates in rank order; the first with a free walkable pose nearby.
	local candidates={}
	for x=1,m.w-2 do for y=1,m.h-2 do
		local g=m(x,y,Map.TERRAIN);local k=batch4Feature(g)
		if k then candidates[#candidates+1]={x=x,y=y,kind=k,id=g.define_as,rank=priority[k] or 5} end
	end end
	table.sort(candidates,function(a,b) if a.rank~=b.rank then return a.rank<b.rank end;if a.y~=b.y then return a.y<b.y end;return a.x<b.x end)
	if #candidates==0 then return {found=false} end
	local target,best
	for _,c in ipairs(candidates) do
		for x=math.max(0,c.x-3),math.min(m.w-1,c.x+3) do
		for y=math.max(0,c.y-3),math.min(m.h-1,c.y+3) do
			local g=m(x,y,Map.TERRAIN)
			local d=math.abs(x-c.x)+math.abs(y-c.y)
			if g and not g.does_block_move and not g.change_level and not g.change_zone and
				not m(x,y,Map.ACTOR) and d>0 and (not best or d<best.d) then best={x=x,y=y,d=d} end
		end end
		if best then target=c;break end
	end
	if not best then return {found=false,target=candidates[1]} end
	p:move(best.x,best.y,true);p.sight=20;refreshView()
	target.found=true;target.pose=best
	return target
end
function M.batch4Dig()
	guard()
	local zone=game.zone.short_name
	local m,p=game.level.map,game.player
	local function diggable(g)
		if not g or not g.dig then return false end
		if underwaterZones[zone] then return Terrain.underwaterKind(g)=='wall' end
		if zone=='conclave-vault' then return Terrain.classify(g)=='wall' end
		if zone=='briagh-lair' then return Terrain.sandTerrain(g)=='wall' end
		if zone=='valley-moon-caverns' then return Terrain.caveTerrain(g)=='wall' end
		if zone=='rak-shor-pride' then return Terrain.batch5Kind(g,'rakshor')=='wall' end
		if zone=='orc-breeding-pit' and game.level.level~=1 then return Terrain.gloomTerrain(g,'plain')=='gloom-wall' end
		if Terrain.variant(game.zone) then return Terrain.classify(g)=='wall' end
		local k=batch4Families[zone] and Terrain.batch4Kind(g,batch4Families[zone])
		return k=='wall' or k=='cave-wall' or k=='tree'
	end
	local target
	for x=1,m.w-2 do for y=1,m.h-2 do
		if diggable(m(x,y,Map.TERRAIN)) then
			local d=math.abs(x-p.x)+math.abs(y-p.y)
			if not target or d<target.d then target={x=x,y=y,d=d} end
		end
	end end
	if not target then return {found=false} end
	M.focus(target.x,target.y)
	local before=m(target.x,target.y,Map.TERRAIN)
	DamageType:get(DamageType.DIG).projector(p,target.x,target.y,DamageType.DIG,1)
	local after=m(target.x,target.y,Map.TERRAIN)
	local stone=Terrain.variant(game.zone) and not (zone=='orc-breeding-pit' and game.level.level~=1)
	local kind=underwaterZones[zone] and Terrain.underwaterKind(after) or stone and Terrain.classify(after) or
		zone=='briagh-lair' and Terrain.sandTerrain(after) or zone=='valley-moon-caverns' and Terrain.caveTerrain(after) or
		zone=='orc-breeding-pit' and Terrain.gloomTerrain(after,'plain') or
		zone=='rak-shor-pride' and Terrain.batch5Kind(after,'rakshor') or
		batch4Families[zone] and Terrain.batch4Kind(after,batch4Families[zone])
	-- Stone-adapter cells are drawn per observed cell by the Map superload,
	-- not via replace_display; their census record is the ownership proof.
	local census=M.terrainCensus()
	local record=stone and game.level.map._checker_korpul and game.level.map._checker_korpul[target.x+target.y*game.level.map.w]
	return {found=true,x=target.x,y=target.y,before=before.define_as,after=after.define_as,
		after_kind=kind or false,owned=stone and (record and record.painted or false) or forestOwned(after),census=census}
end

return M
