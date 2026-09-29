-- lua / luajit tests/random_identity.lua
-- Execute the ACTUAL native createRandomBoss and clone functions with only
-- their engine dependencies mocked. Never starts the game or changes saves.
local script = debug.getinfo(1, "S").source:sub(2)
local here = script:match("^(.*[/\\])") or "./"
local root = here.."../"
local Tokens = dofile(root.."overload/mod/class/CheckerTokens.lua")
local Style = dofile(root.."overload/mod/class/CheckerTokenStyle.lua")
local checks = 0
local function equal(actual, expected, label)
	checks = checks + 1
	assert(actual == expected, label..": expected "..tostring(expected)..", got "..tostring(actual))
end
local function copy(value)
	if type(value) ~= "table" then return value end
	local out = {}
	for key, item in pairs(value) do out[key] = copy(item) end
	return out
end
local function read(path)
	local file = assert(io.open(path, "r"))
	local text = file:read("*a"); file:close()
	return text
end
local function compile(text, name, environment)
	if setfenv then
		local chunk = assert(loadstring(text, name)); setfenv(chunk, environment); return chunk
	end
	return assert(load(text, name, "t", environment))
end
local function section(path, first, after)
	local text = read(path)
	local start = assert(text:find(first, 1, true), "native function moved: "..first)
	local stop = assert(text:find(after, start, true), "native function boundary moved: "..after)
	return text:sub(start, stop-1)
end

local clone_class = {}
compile(section(root.."../../engines/default/engine/class.lua", "local function clonerecurs(d)",
	"--- Automatically called by cloneFull()"), "@native-engine-clone", setmetatable({_M=clone_class}, {__index=_G}))()
local native_state = {birth={}}
local journal, serial = {}, 0
local generator = {new=function() return {generate=function() return "Opaque Generated Name" end} end}
local env = setmetatable({
	_M=native_state, NameGenerator=generator, NameGenerator2=generator,
	_t=function(value) return value end, print=function() end, colors={VIOLET={255,0,255}},
	rng={percent=function() return false end, range=function(low) return low end},
	resolvers={sustains_at_birth=function() return {__resolver="sustains_at_birth"} end,
		drops=function(value) value.__resolver="drops"; return value end,
		drop_randart=function() return {__resolver="drop_randart"} end,
		talented_ai_tactic=function() return {__resolver="talented_ai_tactic"} end},
}, {__index=_G})
compile(section(root.."../../modules/tome/class/GameState.lua", "function _M:createRandomBoss(base, data)",
	"function _M:applyRandomClassNew("), "@native-createRandomBoss", env)()
compile(section(root.."../../modules/tome/class/GameState.lua", "function _M:entityFilterPost(zone, level, type, e, filter)",
	"function _M:egoFilter("), "@native-entityFilterPost", env)()
env.table = setmetatable({clone=copy, merge=function(target, values)
	for key, value in pairs(values) do target[key]=copy(value) end
	return target
end}, {__index=table})
function native_state:getRandartNameRule() return {default={}} end
function native_state:applyRandomClass(actor, data)
	journal[#journal+1] = "classes"
	actor.talents.MOCK_CLASS = 3
	if data.class_effect then data.class_effect(actor, data) end
end
local original_create = native_state.createRandomBoss
local original_tier = function(_, name) return "native:"..name end
native_state.alternateZoneTier1 = original_tier
local hook_env = setmetatable({loadPrevious=function() return native_state end,
	require=function(name) assert(name == "mod.class.CheckerTokens"); return Tokens end}, {__index=_G})
local State = compile(read(root.."superload/mod/class/GameState.lua"), "@checker-GameState", hook_env)()
env.game = {state=State}
equal(State.alternateZoneTier1, original_tier, "production hook leaves zone tier selection intact")

local old_tformat = string.tformat
string.tformat = string.tformat or string.format
local function base(id)
	local entry = assert(Tokens.by_id[id or "wolf"])
	return {name=entry.name, image=entry.image, type=entry.type, subtype=entry.subtype,
		define_as=entry.define_as, unique=entry.unique and true or nil,
		rank=2, life_rating=10, level_range={1,10}, max_life=100, talents={}, ai="dumb_talented_simple",
		combat={dam=8}, body={INVEN=10}, can_multiply=0.5, clone_on_hit=0.2,
		clone=clone_class.clone,
		cloned=function(self) serial=serial+1; self.uid=serial; journal[#journal+1]="clone" end,
		initBody=function(self) self.inven={INVEN={}}; journal[#journal+1]="body" end,
		resolve=function(self)
			journal[#journal+1]="resolve"
			if self.resolve_effect then self.resolve_effect(self) end
		end}
end
local function outcome(actor, expected, reason, label, owned, allow)
	local id, why = Tokens.explain(actor, owned, allow)
	equal(id, expected, label.." id")
	equal(why, reason, label.." reason")
	equal(Tokens.identify(actor, owned, allow), id, label.." explain/identify agreement")
end
local function sameRules(actual, expected, path)
	for key, value in pairs(expected) do
		if key ~= "uid" and key ~= "_checker_token_origin" then
			local field = path.."."..tostring(key)
			if type(value) == "table" then
				equal(type(actual[key]), "table", field.." table"); sameRules(actual[key], value, field)
			elseif type(value) == "function" then equal(type(actual[key]), "function", field.." function")
			else equal(actual[key], value, field) end
		end
	end
	for key in pairs(actual) do
		if key ~= "_checker_token_origin" then equal(type(actual[key]), type(expected[key]), path.." extra "..tostring(key)) end
	end
end

-- Rank is an independent tactical state; names deliberately have no base
-- suffix. Native class application/body/loot/AI and all callback args survive.
for _, rank in ipairs{3.2, 3.5, 4} do
	local source = base()
	local snapshot = copy(source)
	local data = {level=7, rank=rank, name_scheme="#rng#"}
	local vanilla, vanilla_id = original_create(State, source, copy(data))
	local actor, boss_id = State:createRandomBoss(source, data)
	outcome(actor, "wolf", "random-origin", "native rank "..rank)
	equal(boss_id, vanilla_id, "native boss id returned intact")
	equal(actor.name, "Opaque Generated Name", "opaque generated name does not need species suffix")
	equal(actor.unique, actor.name, "native unique unchanged")
	equal(actor.define_as, boss_id, "native define_as unchanged")
	equal(actor.rank, rank, "native rank unchanged")
	sameRules(actor, vanilla, "rank "..rank)
	sameRules(source, snapshot, "untouched base "..rank)
	equal(source._checker_token_origin, nil, "base never receives a marker")
	for _, sample in ipairs{{3.2,"rare"}, {3.5,"unique"}, {4,"boss"}, {5,"elite_boss"}, {2,false}} do
		actor.rank = sample[1]
		equal(Tokens.identify(actor), "wolf", "rank changes keep body identity")
		equal(Style.rankBadge(actor.rank) or false, sample[2], "badge follows current rank")
	end
end

-- The zone's actual post-filter entry chooses rare rank itself and passes
-- random bosses through the engine's two RNG rank branches. Only rare-item
-- count is zeroed in this fixture to avoid requiring an object generator.
local zone = {level_adjust_level=function() return 8 end}
local rare = State:entityFilterPost(zone, {}, "actor", base(), {random_elite={nb_rares=0}})
outcome(rare,"wolf","random-origin","native random_elite filter")
equal(rare.rank,3.2,"native random_elite selects rare rank")
equal(rare.life_rating,17,"native random_elite life formula")
equal(rare._rndboss_resources_boost,1.5,"native random_elite resource boost")
equal(rare._rndboss_talent_cds,3,"native random_elite cooldown factor")
local unique = State:entityFilterPost(zone, {}, "actor", base(), {random_boss=true})
outcome(unique,"wolf","random-origin","native random_boss default unique filter")
equal(unique.rank,3.5,"native random_boss RNG unique rank")
env.rng.percent=function() return true end
local boss = State:entityFilterPost(zone, {}, "actor", base(), {random_boss=true})
outcome(boss,"wolf","random-origin","native random_boss default boss filter")
equal(boss.rank,4,"native random_boss RNG boss rank")
env.rng.percent=function() return false end
local manual_unique=base(); manual_unique.unique=true
equal(State:entityFilterPost(zone, {}, "actor", manual_unique, {random_boss=true}),manual_unique,
	"native filter leaves hand-made unique untouched")
outcome(manual_unique,nil,"unknown-unique","hand-made unique is still unknown")
local transformed_rare=State:entityFilterPost(zone, {}, "actor", base(), {random_elite={nb_rares=0},
	post=function(target) target.image="transformed.png" end})
equal(transformed_rare._checker_token_origin,nil,"native rare user_post body change cannot stamp")
equal(Tokens.identify(transformed_rare),nil,"native rare user_post body falls back")

journal = {}
local source = base()
source.rnd_boss_init = function(actor, data)
	journal[#journal+1]="base-init"; equal(data.tag, "passed", "rnd_boss_init data")
	equal(actor._checker_token_origin, nil, "base-init precedes stamp")
end
local callback_data = {level=3, rank=3.2, tag="passed",
	init=function(data, actor)
		journal[#journal+1]="init"; equal(data.tag, "passed", "init data")
		equal(actor.name, "wolf", "capture does not preempt native init")
	end,
	post=function(actor, data)
		journal[#journal+1]="post"; equal(data.tag, "passed", "post data")
		equal(actor._checker_token_origin, nil, "post precedes stamp")
	end}
local result = State:createRandomBoss(source, callback_data)
equal(table.concat(journal, ","), "clone,init,base-init,body,resolve,classes,post", "actual native lifecycle order")
outcome(result, "wolf", "random-origin", "stamp is applied after native post")

-- All existing visual exclusions apply both before capture and after every
-- native generation phase. A final mutation cannot obtain a valid record.
local mutations = {
	{"image", "different-body.png", "body-changed"}, {"type", "undead", "body-changed"},
	{"subtype", "bear", "body-changed"}, {"display_h", 2, "body-changed"},
	{"replace_display", {image="foreign.png"}, "external-display"},
	{"moddable_tile", "humanoid", "moddable-tile"}, {"shader", "body-effect", "shader"},
	{"anim", {1,2}, "animation"}, {"add_displays", {{image="extra.png"}}, "add-displays"},
	{"textures", {"layer.png"}, "textures"},
	{"add_mos", {{image="extra.png"}}, "add-mos"},
}
for _, mutation in ipairs(mutations) do
	local field, value, reason = mutation[1], mutation[2], mutation[3]
	local actor = State:createRandomBoss(base(), {level=1, rank=3.2})
	local before = actor[field]
	actor[field] = copy(value)
	outcome(actor, nil, reason, "generated actor changes "..field)
	actor[field] = before
	outcome(actor, "wolf", "random-origin", "generated actor restores "..field)
	for _, phase in ipairs{"init", "base-init", "resolve", "classes", "post"} do
		local src, data = base(), {level=1, rank=4}
		local function change(target) target[field] = copy(value) end
		if phase == "init" then data.init=function(_, target) change(target) end
		elseif phase == "base-init" then src.rnd_boss_init=change
		elseif phase == "resolve" then src.resolve_effect=change
		elseif phase == "classes" then data.class_effect=change
		else data.post=change end
		local changed = State:createRandomBoss(src, data)
		equal(changed._checker_token_origin, nil, phase.." changing "..field.." cannot stamp")
		equal(Tokens.identify(changed), nil, phase.." changing "..field.." falls back")
	end
	if field ~= "display_h" then
		local src = base(); src[field]=copy(value)
		local changed = State:createRandomBoss(src, {level=1, post=function(target) target[field]=nil end})
		equal(changed._checker_token_origin, nil, "unverified base "..field.." cannot stamp after being cleared")
	end
end

-- A native shader aura (addShaderAura) wraps the current display's own image;
-- it is not a body change and does not invalidate the random-origin record,
-- whether it appears on the generated actor or a later native mutation.
local aura_actor = State:createRandomBoss(base(), {level=1, rank=3.2})
aura_actor.shader_auras = {stone_skin={shader="stoneskin"}}
outcome(aura_actor, "wolf", "random-origin", "generated actor with an active shader aura")
local aura_mutated = State:createRandomBoss(base(), {level=1, rank=4,
	post=function(target) target.shader_auras = {stone_skin={shader="stoneskin"}} end})
outcome(aura_mutated, "wolf", "random-origin", "native post applying a shader aura keeps the origin")

for _, entry in ipairs(Tokens.catalog) do
	if not entry.define_as then
		local actor = State:createRandomBoss(base(entry.id), {level=1, rank=3.2})
		outcome(actor, entry.id, "random-origin", "all exact ordinary bases "..entry.id)
	end
end
for _, change in ipairs{
	{name="Uncatalogued wolf", unique="Uncatalogued wolf", define_as="UNKNOWN_UNIQUE"},
	{unique=true}, {unique="player"}, {define_as="UNKNOWN_DEFINITION"},
	{name="wolf the wolf"}, {name="unknown canine"},
} do
	local src = base(); for key, value in pairs(change) do src[key]=value end
	equal(Tokens.identify(src), nil, "unknown source does not identify")
	local actor = State:createRandomBoss(src, {level=1})
	equal(actor._checker_token_origin, nil, "unknown source does not acquire provenance")
	equal(Tokens.identify(actor), nil, "unknown generated unique remains native")
end
outcome({name="unpainted animal"}, nil, "no-art", "explanation for unpainted ordinary actor")
outcome({name="unpainted unique",unique=true}, nil, "unknown-unique", "explanation for unpainted unique")
outcome(false, nil, "invalid-actor", "non-table actor")

local generated = State:createRandomBoss(base(), {level=1})
local display = {image=Tokens.image("wolf"), __CLASSNAME="engine.Entity"}
generated.replace_display = display
outcome(generated, "wolf", "random-origin", "owned display", display)
outcome(generated, nil, "external-display", "unclaimed display")
generated.replace_display = nil
for _, mutation in ipairs{{"name","Another name"}, {"define_as","RND_BOSS_DIFFERENT"},
	{"unique",true}, {"randboss",false}} do
	local actor = copy(generated); actor[mutation[1]]=mutation[2]
	outcome(actor, nil, "stale-origin", "generated identity changed "..mutation[1])
end

-- Bad/old records cannot admit a renamed creature. Every field is required,
-- metatables/nested object references/extra keys are rejected, and a changed
-- catalog signature cannot silently reuse the same token id after an update.
for _, bad in ipairs{false, true, 1, "wolf", {}, {version=1,id="wolf"}} do
	local actor = copy(generated); actor._checker_token_origin=bad
	outcome(actor, nil, "invalid-origin", "malformed record "..tostring(bad))
end
for key in pairs(generated._checker_token_origin) do
	local actor = copy(generated); actor._checker_token_origin[key]=nil
	outcome(actor, nil, "invalid-origin", "missing record field "..key)
end
for _, mutation in ipairs{{"version",2}, {"source","other"}, {"id","fox"}, {"base_name","fox"},
	{"base_image","changed.png"}, {"base_type","undead"}, {"base_subtype","bear"},
	{"base_define_as","UNKNOWN"}, {"appearance","native-tall"}, {"unique","Other"},
	{"display_w",math.huge}, {"display_h",0/0}, {"display_x",{}}, {"foreign",display}} do
	local actor = copy(generated); actor._checker_token_origin[mutation[1]]=mutation[2]
	outcome(actor, nil, "invalid-origin", "corrupt record field "..mutation[1])
end
local actor = copy(generated)
setmetatable(actor._checker_token_origin, {__index=generated._checker_token_origin})
outcome(actor, nil, "invalid-origin", "record metatable")
local old_image = Tokens.by_id.wolf.image
Tokens.by_id.wolf.image = "catalog-replaced-body.png"
outcome(generated, nil, "invalid-origin", "catalog changed after generation")
Tokens.by_id.wolf.image = old_image
outcome(generated, "wolf", "random-origin", "catalog restored")
local again = State:createRandomBoss(generated, {level=1})
equal(again._checker_token_origin, nil, "old random marker cannot authenticate new generation")
equal(Tokens.identify(again), nil, "nested re-generation of unknown renamed base falls back")
local bad_source = base(); bad_source.name="unknown"; bad_source._checker_token_origin=copy(generated._checker_token_origin)
equal(State:createRandomBoss(bad_source, {level=1})._checker_token_origin, nil, "inherited stale marker is cleared")

-- Party's existing integration opt-in remains narrow for both ordinary and
-- generated bodies. Rank, source uid, display objects and actor class are not
-- serialized as provenance, so clone/Party class replacement can retain it.
local ordinary = base(); ordinary.unique="player"
outcome(ordinary, "wolf", "exact-identity", "verified ordinary Party control", nil, true)
outcome(ordinary, nil, "unknown-unique", "unverified ordinary Party control")
local controlled = copy(generated); controlled.unique="player"
outcome(controlled, "wolf", "random-origin", "verified generated Party control", nil, true)
outcome(controlled, nil, "stale-origin", "unverified generated Party control")
controlled.unique="arbitrary unique"
outcome(controlled, nil, "stale-origin", "Party opt-in cannot admit arbitrary unique", nil, true)
local tall = base("prox"); tall.image="invis.png"; tall.add_mos={{image=Tokens.by_id.prox.image,display_h=2,display_y=-1}}
outcome(tall, "prox", "exact-identity", "known native tall body retained")
tall.add_mos[1].shader="unknown"
outcome(tall, nil, "native-tall-changed", "unknown tall shader retained")

-- Lua source round trip proves the record is only scalars. The live fixture
-- companion separately exercises the actual native ZIP serializer and loader.
local record = generated._checker_token_origin
local serialized = {"return {"}
for key, value in pairs(record) do
	equal(type(key), "string", "record has string keys")
	assert(type(value)=="string" or type(value)=="boolean" or type(value)=="number", "record must have no display/object table")
	local encoded = type(value)=="string" and string.format("%q",value) or tostring(value)
	serialized[#serialized+1]="["..string.format("%q",key).."]="..encoded..","
end
serialized[#serialized+1]="}"
local restored = copy(generated)
restored._checker_token_origin = compile(table.concat(serialized), "@scalar-origin-roundtrip", {})()
outcome(restored, "wolf", "random-origin", "scalar record round trip")
restored.uid=123456
outcome(restored, "wolf", "random-origin", "load assigns a fresh native uid")
local clone = generated:clone()
assert(clone._checker_token_origin~=record, "native clone must copy the plain record")
outcome(clone, "wolf", "random-origin", "native clone keeps provenance")
local capture = assert(Tokens.captureRandomOrigin(base()))
local stamped = copy(generated); stamped._checker_token_origin=nil
equal(Tokens.recordRandomOrigin(stamped,capture,stamped.define_as),"wolf","explicit stamp")
capture.id="fox"
outcome(stamped, "wolf", "random-origin", "stamp copies capture instead of sharing it")
local recursion
local outer = State:createRandomBoss(base("brown-bear"), {level=1,post=function()
	recursion=State:createRandomBoss(base("fox"), {level=1})
end})
outcome(outer,"brown-bear","random-origin","nested generation outer capture")
outcome(recursion,"fox","random-origin","nested generation inner capture")
local ok, err = pcall(function() State:createRandomBoss(base(), {level=1,post=function() error("native-post-error") end}) end)
equal(ok,false,"native callback errors propagate")
assert(err:find("native%-post%-error"), "native error was replaced")
string.tformat = old_tformat
print(("[RandomIdentity] PASS: %d checks; actual native entityFilterPost/createRandomBoss/clone, lifecycle callbacks, unchanged rules, origin integrity, visual fallback/recovery, Party opt-in and scalar round trip"):format(checks))
