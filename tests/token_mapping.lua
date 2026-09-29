-- Run from any working directory: lua path/to/tests/token_mapping.lua
local script = debug.getinfo(1, "S").source:sub(2)
local here = script:match("^(.*[/\\])") or "./"
local Tokens = dofile(here.."../overload/mod/class/CheckerTokens.lua")
local checks = 0

local function equal(actual, expected, label)
	checks = checks + 1
	assert(actual == expected, label..": expected "..tostring(expected)..", got "..tostring(actual))
end

local function copy(t)
	local out = {}
	for k, v in pairs(t) do out[k] = type(v) == "table" and copy(v) or v end
	return out
end

local function actor(entry)
	return {name=entry.name, image=entry.image, type=entry.type, subtype=entry.subtype,
		define_as=entry.define_as, unique=entry.unique and true or nil, faction="enemies", rank=2}
end

assert(#Tokens.catalog >= 17, "catalog must retain the original identities")
local seen = {}
for _, entry in ipairs(Tokens.catalog) do
	equal(seen[entry.id], nil, "unique id "..entry.id)
	seen[entry.id] = true
	equal(Tokens.by_id[entry.id], entry, "index "..entry.id)
	equal(Tokens.image(entry.id), "checker-revised+tokens/"..entry.id..".png", "runtime image "..entry.id)
	local a = actor(entry)
	equal(Tokens.identify(a), entry.id, "native body "..entry.id)
	for _, relation in ipairs({{"players", 1}, {"neutral", 3.2}, {"enemies", 4}}) do
		a.faction, a.rank = relation[1], relation[2]
		equal(Tokens.identify(a), entry.id, "state independent "..entry.id.." "..relation[1])
	end
	-- Summon allegiance and duration do not turn a verified creature into a
	-- different species. The renderer remains responsible for tactical markers.
	a.summoner, a.summon_time = {faction="players"}, 7
	equal(Tokens.identify(a), entry.id, "summoned identity "..entry.id)
	local own, effect = {}, {image="npc/elemental_temporal_greater_telugoroth.png"}
	a.replace_display = own
	equal(Tokens.identify(a, own), entry.id, "owned display "..entry.id)
	equal(Tokens.identify(a), nil, "unclaimed display "..entry.id)
	a.replace_display = effect
	equal(Tokens.identify(a, own), nil, "external transformation "..entry.id)
	a.replace_display = nil
	equal(Tokens.identify(a, own), entry.id, "transformation ended "..entry.id)
	a.image = "npc/elemental_temporal_greater_telugoroth.png"
	equal(Tokens.identify(a), nil, "changed body "..entry.id)
	a = actor(entry)
	a.name = "different creature with reused artwork"
	equal(Tokens.identify(a), nil, "reused art "..entry.id)
	a = actor(entry)
	a.type = entry.type == "undead" and "animal" or "undead"
	equal(Tokens.identify(a), nil, "changed creature type "..entry.id)
	for _, field in ipairs({"add_mos", "add_displays", "textures"}) do
		a = actor(entry)
		a[field] = {{image="unknown-overlay.png"}}
		equal(Tokens.identify(a), nil, "mixed display "..field.." "..entry.id)
		a[field] = {}
		equal(Tokens.identify(a), entry.id, "empty display container "..field.." "..entry.id)
	end
	-- A native shader aura (addShaderAura) is drawn as a chained overlay around
	-- whatever image is on the display; keep the token instead of falling back.
	a = actor(entry)
	a.shader_auras = {stone_skin={shader="stoneskin"}}
	equal(Tokens.identify(a), entry.id, "active shader aura keeps token "..entry.id)
	a.shader_auras = {}
	equal(Tokens.identify(a), entry.id, "empty shader_auras container "..entry.id)
	-- Native aura bookkeeping (_isshaderaura add_mos entries) the engine wrote
	-- directly onto the actor before any token existed is not a body change.
	a = actor(entry)
	a.shader_auras = {stone_skin={shader="stoneskin"}}
	a.add_mos = {{_isshaderaura=true, image_alter="sdm", image=entry.image, display_h=2, display_y=-1}}
	equal(Tokens.identify(a), entry.id, "pre-existing native aura bookkeeping "..entry.id)
	-- A genuine extra overlay alongside aura bookkeeping is still a body change.
	a.add_mos[2] = {image="unknown-overlay.png"}
	equal(Tokens.identify(a), nil, "aura bookkeeping does not hide a real add_mos change "..entry.id)
	for _, field in ipairs({"shader", "moddable_tile", "anim"}) do
		a = actor(entry)
		a[field] = "unhandled-body-system"
		equal(Tokens.identify(a), nil, "unsupported visual "..field.." "..entry.id)
	end
	if entry.unique or entry.native_tall then
		a = actor(entry)
		a.image = "invis.png"
		a.add_mos = {{image=entry.image, display_h=2, display_y=-1}}
		equal(Tokens.identify(a), entry.id, "resolved nice_tile "..entry.id)
		local high = copy(a)
		high.add_mos[1].display_w, high.add_mos[1].display_x, high.add_mos[1].display_scale = 1, 0, 1
		equal(Tokens.identify(high), entry.id, "explicit default dimensions "..entry.id)
		for _, mutation in ipairs({
			{"display_h", 1}, {"display_y", 0}, {"display_w", 2}, {"display_x", -.5},
			{"display_scale", 1.2}, {"image", "different-body.png"}, {"shader", "state-aura"},
		}) do
			local altered = copy(a)
			altered.add_mos[1][mutation[1]] = mutation[2]
			equal(Tokens.identify(altered), nil, "altered tall body "..entry.id.." "..mutation[1])
		end
		local mixed = copy(a)
		mixed.add_mos[2] = {image="extra-head.png"}
		equal(Tokens.identify(mixed), nil, "second tall body "..entry.id)
		mixed = copy(a)
		mixed.add_mos.hidden = {image="non-array-overlay.png"}
		equal(Tokens.identify(mixed), nil, "non-array tall body "..entry.id)
		-- Native aura bookkeeping around the tall body, before or after it (a
		-- Native->Refined toggle rebuilds the aura first), is not a body change.
		local aura = {_isshaderaura=true, image_alter="sdm", image=entry.image, display_h=2, display_y=-1}
		local wrapped = copy(a)
		wrapped.shader_auras = {stone_skin={shader="stoneskin"}}
		wrapped.add_mos = {copy(aura), copy(a.add_mos[1])}
		equal(Tokens.identify(wrapped), entry.id, "tall body after aura bookkeeping "..entry.id)
		wrapped.add_mos = {copy(a.add_mos[1]), copy(aura)}
		equal(Tokens.identify(wrapped), entry.id, "tall body before aura bookkeeping "..entry.id)
		wrapped.add_mos = {copy(aura)}
		equal(Tokens.identify(wrapped), nil, "aura bookkeeping without a tall body "..entry.id)
		wrapped.add_mos = {copy(aura), copy(a.add_mos[1]), {image="extra-head.png"}}
		equal(Tokens.identify(wrapped), nil, "aura does not hide a second tall body "..entry.id)
		wrapped.add_mos = {copy(aura), copy(a.add_mos[1])}
		wrapped.add_mos[2].display_h = 1
		equal(Tokens.identify(wrapped), nil, "aura does not hide an altered tall body "..entry.id)
		a.define_as = "UNKNOWN_UNIQUE"
		equal(Tokens.identify(a), nil, "unknown tall definition "..entry.id)
	else
		a = actor(entry)
		a.unique = true
		equal(Tokens.identify(a), nil, "unknown unique using ordinary image "..entry.id)
		equal(Tokens.identify(a, nil, true), nil, "player opt-in cannot admit ordinary unique "..entry.id)
		a.unique = "player"
		equal(Tokens.identify(a), nil, "player sentinel denied without verified control "..entry.id)
		equal(Tokens.identify(a, nil, false), nil, "player sentinel explicitly denied "..entry.id)
		equal(Tokens.identify(a, nil, true), entry.id, "verified player sentinel "..entry.id)
		equal(Tokens.identify(a, nil, "yes"), nil, "player identity requires explicit boolean "..entry.id)
		a.unique = "an actual unique creature"
		equal(Tokens.identify(a, nil, true), nil, "player opt-in cannot admit named unique "..entry.id)
		a.unique, a.define_as = nil, "OTHER_DEFINED_CREATURE"
		equal(Tokens.identify(a), nil, "unverified defined actor "..entry.id)
	end
end

-- THIEF_BANDIT is an ordinary definition, never permission to accept an
-- unknown unique or an unverified two-cell body sharing that identifier.
local bandit = actor(Tokens.by_id.bandit)
equal(bandit.unique, nil, "defined bandit is ordinary")
equal(Tokens.identify(bandit), "bandit", "rank-2 defined bandit maps")
bandit.unique = "unverified bandit unique"
equal(Tokens.identify(bandit), nil, "defined ordinary actor cannot admit unknown unique")
bandit.unique = nil
bandit.image = "invis.png"
bandit.add_mos = {{image=Tokens.by_id.bandit.image, display_h=2, display_y=-1}}
equal(Tokens.identify(bandit), nil, "defined ordinary actor cannot admit unverified tall art")

for _, prefix in ipairs({"gloomy ", "deformed ", "sick ", "dreaming ", "slumbering ", "dozing "}) do
	for _, entry in ipairs(Tokens.catalog) do
		local family = entry.type.."/"..entry.subtype
		if (family == "vermin/rodent" or family == "animal/canine" or family == "animal/bear" or family == "immovable/plants")
			and not entry.unique and not entry.define_as then
			local a = actor(entry)
			a.name = prefix..entry.name
			equal(Tokens.identify(a), entry.id, "heart-gloom known rename "..a.name)
			a.image = "npc/other.png"
			equal(Tokens.identify(a), nil, "heart-gloom body changed "..a.name)
			a = actor(entry)
			a.name, a.unique = prefix..entry.name, true
			equal(Tokens.identify(a), nil, "heart-gloom prefix cannot admit unique "..a.name)
		end
	end
end
-- Bear and plant renames come from the same rename-only alter() loader.
local gloom_cases = {
	{"gloomy brown bear", "brown-bear"}, {"deformed black bear", "black-bear"},
	{"dreaming poison ivy", "poison-ivy"}, {"sick giant venus flytrap", "venus-flytrap"},
	{"slumbering honey tree", "honey-tree"}, {"dozing brown bear", "brown-bear"},
}
for _, case in ipairs(gloom_cases) do
	local a = actor(Tokens.by_id[case[2]])
	a.name = case[1]
	equal(Tokens.identify(a), case[2], "heart-gloom covered bear/plant base "..case[1])
end
for _, name in ipairs({"gloomy cave bear", "dreaming war bear", "sick unknown plant"}) do
	local a = actor(Tokens.by_id["brown-bear"])
	a.name = name
	equal(Tokens.identify(a), nil, "uncovered bear/plant base "..name)
end
do
	local a = actor(Tokens.by_id["norgos-guardian"])
	a.name = "gloomy Norgos, the Guardian"
	equal(Tokens.identify(a), nil, "unique define_as base is never a renamed generic")
	a = actor(Tokens.by_id["poison-ivy"])
	a.name, a.subtype = "gloomy poison ivy", "jelly"
	equal(Tokens.identify(a), nil, "gloom plant with wrong subtype")
	a = actor(Tokens.by_id["brown-bear"])
	a.name, a.type = "gloomy brown bear", "vermin"
	equal(Tokens.identify(a), nil, "gloom bear with wrong type")
	a = actor(Tokens.by_id["black-bear"])
	a.name, a.image = "gloomy black bear", "npc/brown_bear.png"
	equal(Tokens.identify(a), nil, "gloom bear with changed image")
end
for _, name in ipairs({"murky wolf", "gloomy unknown wolf", "gloomy  wolf", "gloomy Shax the Slimy"}) do
	local a = actor(Tokens.by_id.wolf)
	a.name = name
	equal(Tokens.identify(a), nil, "unknown prefix/base "..name)
end

local shax = actor(Tokens.by_id.prox)
shax.name, shax.define_as = "Shax the Slimy", "TROLL_SHAX"
equal(Tokens.identify(shax), nil, "Shax reuses Prox base image")
shax.image = "invis.png"
shax.add_mos = {{image="npc/giant_troll_shax_the_slimy.png", display_h=2, display_y=-1}}
equal(Tokens.identify(shax), "shax", "Shax exact tall body")
shax.name, shax.define_as = "Prox the Mighty", "TROLL_PROX"
equal(Tokens.identify(shax), nil, "Prox identity cannot override Shax body")

for _, guardian in ipairs({
	{id="horned-horror", name="Horned Horror", define_as="HORNED_HORROR", image="npc/horror_corrupted_horner_horror.png", type="horror", subtype="corrupted"},
	{id="norgos-guardian", name="Norgos, the Guardian", define_as="NORGOS", image="npc/animal_bear_norgos_the_guardian.png", type="animal", subtype="bear"},
}) do
	local a={name=guardian.name, define_as=guardian.define_as, image="invis.png",
		type=guardian.type, subtype=guardian.subtype, unique=true,
		add_mos={{image=guardian.image, display_h=2, display_y=-1}}}
	equal(Tokens.identify(a), guardian.id, "exact tall guardian "..guardian.name)
	a.add_mos[1].image="npc/other.png"
	equal(Tokens.identify(a), nil, "changed tall guardian body "..guardian.name)
end

-- Batch C: the three bow skeletons are separate exact identities; none borrows
-- another's drawing and a changed name or body keeps the native sprite.
for _, archer in ipairs({
	{id="skeleton-archer", name="skeleton archer", image="npc/skeleton_archer.png"},
	{id="skeleton-master-archer", name="skeleton master archer", image="npc/master_skeleton_archer.png"},
	{id="degenerated-skeleton-archer", name="degenerated skeleton archer", image="npc/undead_skeleton_degenerated_skeleton_archer.png"},
}) do
	local a = {name=archer.name, image=archer.image, type="undead", subtype="skeleton", faction="enemies", rank=3}
	equal(Tokens.identify(a), archer.id, "exact bow skeleton "..archer.name)
	a.image = "npc/skeleton_archer.png"
	if archer.id ~= "skeleton-archer" then
		equal(Tokens.identify(a), nil, "archer body cannot stand in for "..archer.name)
	end
end
equal(Tokens.identify({name="skeleton master archer", image="npc/master_skeleton_warrior.png", type="undead", subtype="skeleton"}), nil,
	"master archer name with another native body stays native")

-- Batch D: red/blue jelly complete the 6-colour jelly family; neither borrows
-- a sibling's drawing (own or another already-shipped colour's).
for _, jelly in ipairs({
	{id="red-jelly", name="red jelly", image="npc/jelly-red.png"},
	{id="blue-jelly", name="blue jelly", image="npc/jelly-blue.png"},
}) do
	local a = {name=jelly.name, image=jelly.image, type="immovable", subtype="jelly", faction="enemies", rank=1}
	equal(Tokens.identify(a), jelly.id, "exact jelly "..jelly.name)
end
for _, borrowed in ipairs({
	{name="red jelly", image="npc/jelly-blue.png"},
	{name="blue jelly", image="npc/jelly-red.png"},
	{name="red jelly", image="npc/jelly-green.png"},
	{name="blue jelly", image="npc/jelly-darkgrey.png"},
}) do
	equal(Tokens.identify({name=borrowed.name, image=borrowed.image, type="immovable", subtype="jelly"}), nil,
		"jelly cannot borrow a sibling's image "..borrowed.name.." <- "..borrowed.image)
end

-- Batch D: all six giant-ant colours are now separate exact identities.
-- giant brown/blue ant were integrated after a reviewer-approved base_drift
-- waiver (art/production/waivers/monster-batch-d.json, reviewer decision
-- 2026-09-29). giant carpenter/black ant's first draft was rejected in that
-- same decision (nearly indistinguishable at 48px); a calibrated redraw
-- (monster-batch-d-4) cleared the style gate cleanly with no waiver
-- (base_drift -7.27/-5.43) and is integrated here too.
for _, ant in ipairs({
	{id="giant-white-ant", name="giant white ant", image="npc/white_ant.png"},
	{id="giant-yellow-ant", name="giant yellow ant", image="npc/yellow_ant.png"},
	{id="giant-brown-ant", name="giant brown ant", image="npc/brown_ant.png"},
	{id="giant-blue-ant", name="giant blue ant", image="npc/blue_ant.png"},
	{id="giant-carpenter-ant", name="giant carpenter ant", image="npc/carpenter_ant.png"},
	{id="giant-black-ant", name="giant black ant", image="npc/black_ant.png"},
}) do
	local a = {name=ant.name, image=ant.image, type="insect", subtype="ant", faction="enemies", rank=1}
	equal(Tokens.identify(a), ant.id, "exact ant "..ant.name)
end
for _, borrowed in ipairs({
	{name="giant white ant", image="npc/yellow_ant.png"},
	{name="giant yellow ant", image="npc/white_ant.png"},
	{name="giant white ant", image="npc/brown_ant.png"},
	{name="giant brown ant", image="npc/white_ant.png"},
	{name="giant brown ant", image="npc/blue_ant.png"},
	{name="giant blue ant", image="npc/brown_ant.png"},
	{name="giant blue ant", image="npc/yellow_ant.png"},
	{name="giant yellow ant", image="npc/blue_ant.png"},
	{name="giant carpenter ant", image="npc/black_ant.png"},
	{name="giant black ant", image="npc/carpenter_ant.png"},
	{name="giant carpenter ant", image="npc/brown_ant.png"},
	{name="giant black ant", image="npc/blue_ant.png"},
}) do
	equal(Tokens.identify({name=borrowed.name, image=borrowed.image, type="insect", subtype="ant"}), nil,
		"ant cannot borrow a sibling's image "..borrowed.name.." <- "..borrowed.image)
end

local ancient = actor(Tokens.by_id["ancient-dragon-turtle"])
ancient.image="invis.png"
ancient.add_mos={{image=Tokens.by_id["ancient-dragon-turtle"].image, display_h=2, display_y=-1}}
equal(Tokens.identify(ancient), "ancient-dragon-turtle", "exact non-unique tall aquatic body")
ancient.add_mos[2]={image="unknown-layer.png"}
equal(Tokens.identify(ancient), nil, "extra aquatic layer falls back")

-- Batch F/K: the drem/dremling swapped-filename trap. drem is a separate,
-- smaller, single-image (non-tall) identity whose own art file is
-- npc/horror_corrupted_dremling.png (named after dremling; mapped in batch K
-- as its own token). It must never wear dremling's tall body, and dremling
-- must never wear drem's file.
equal(Tokens.identify({name="drem", type="horror", subtype="corrupted", image="npc/horror_corrupted_dremling.png"}), "drem",
	"drem's own single-image body (batch K token)")
equal(Tokens.identify({name="dremling", type="horror", subtype="corrupted", image="npc/horror_corrupted_dremling.png"}), nil,
	"dremling cannot borrow drem's single-image file")
equal(Tokens.identify({name="drem", type="horror", subtype="corrupted", image="npc/horror_corrupted_drem.png"}), nil,
	"drem cannot borrow dremling's tall art by name alone")
do
	local swapped = {name="drem", type="horror", subtype="corrupted", image="invis.png",
		add_mos={{image="npc/horror_corrupted_drem.png", display_h=2, display_y=-1}}}
	equal(Tokens.identify(swapped), nil, "drem cannot wear dremling's resolved tall body")
end

-- Batch F: within-family tall bodies must not be borrowable by a same-family
-- sibling (shape/value distinction, not just name), mirroring the batch D
-- ant/jelly "cannot borrow a sibling's image" pattern for native_tall bodies.
-- naga tidewarden/tidecaller cleared the style gate cleanly; shivgoroth/
-- greater shivgoroth shipped under the reviewer-approved base_drift waiver
-- (art/production/waivers/monster-batch-f.json). All four are now wired, so
-- their pairwise borrow tests run for real.
for _, borrowed in ipairs({
	{name="naga tidewarden", type="humanoid", subtype="naga", define_as="NAGA_TIDEWARDEN", image="npc/humanoid_naga_naga_tidecaller.png"},
	{name="naga tidecaller", type="humanoid", subtype="naga", define_as="NAGA_TIDECALLER", image="npc/humanoid_naga_naga_tidewarden.png"},
	{name="shivgoroth", type="elemental", subtype="ice", image="npc/elemental_ice_greater_shivgoroth.png"},
	{name="greater shivgoroth", type="elemental", subtype="ice", image="npc/elemental_ice_shivgoroth.png"},
}) do
	local a = {name=borrowed.name, type=borrowed.type, subtype=borrowed.subtype, define_as=borrowed.define_as,
		image="invis.png", add_mos={{image=borrowed.image, display_h=2, display_y=-1}}}
	equal(Tokens.identify(a), nil, "tall body cannot borrow a sibling's image "..borrowed.name.." <- "..borrowed.image)
end

-- Batch G: xhaiak arachnomancer and shiaak venomblade are wired native-tall
-- bodies now; neither may wear the other's resolved image, nor Ungole's.
for _, borrowed in ipairs({
	{name="xhaiak arachnomancer", type="spiderkin", subtype="xhaiak", image="npc/spiderkin_shiaak_shiaak_venomblade.png"},
	{name="shiaak venomblade", type="spiderkin", subtype="shiaak", image="npc/spiderkin_xhaiak_xhaiak_arachnomancer.png"},
	{name="xhaiak arachnomancer", type="spiderkin", subtype="xhaiak", image="npc/spiderkin_spider_ungole.png"},
	{name="shiaak venomblade", type="spiderkin", subtype="shiaak", image="npc/spiderkin_spider_ungole.png"},
}) do
	local a = {name=borrowed.name, type=borrowed.type, subtype=borrowed.subtype,
		image="invis.png", add_mos={{image=borrowed.image, display_h=2, display_y=-1}}}
	equal(Tokens.identify(a), nil, "spiderkin tall body cannot borrow a sibling's image "..borrowed.name.." <- "..borrowed.image)
end
-- The exact resolved xhaiak/shiaak/dremling native-tall shapes map.
for _, id in ipairs({"xhaiak-arachnomancer", "shiaak-venomblade", "dremling"}) do
	local entry = Tokens.by_id[id]
	local tall = {name=entry.name, type=entry.type, subtype=entry.subtype,
		image="invis.png", add_mos={{image=entry.image, display_h=2, display_y=-1}}}
	equal(Tokens.identify(tall), id, "resolved native-tall body "..id)
end
-- dremling is now wired (pale-stone redraw); drem and its swapped file stay
-- native (tested above). Ungole's round-spider body is not xhaiak/shiaak.
equal(Tokens.identify({name="Ungolë", type="spiderkin", subtype="spider", define_as="UNGOLE", unique=true,
	image="npc/spiderkin_spider_ungole.png"}), "ungole", "ungole keeps its own token")

-- Batch G: Massok the Dragonslayer ships under the reviewer-approved
-- base_drift waiver (art/production/waivers/monster-batch-g.json): his exact
-- native-tall unique shape maps; a changed body or identity does not.
equal(Tokens.identify({name="Massok the Dragonslayer", type="humanoid", subtype="orc", define_as="MASSOK", unique=true,
	image="invis.png", add_mos={{image="npc/humanoid_orc_massok_the_dragonslayer.png", display_h=2, display_y=-1}}}), "massok", "massok native-tall body")
for _, changed in ipairs({
	{label="borrowed krogar body", define_as="MASSOK", image="npc/humanoid_orc_krogar.png"},
	{label="wrong define_as", define_as="CORRUPTOR", image="npc/humanoid_orc_massok_the_dragonslayer.png"},
	{label="borrowed brotoq-style unknown body", define_as="MASSOK", image="npc/humanoid_orc_grushnak_warlord.png"},
}) do
	local a = {name="Massok the Dragonslayer", type="humanoid", subtype="orc", define_as=changed.define_as, unique=true,
		image="invis.png", add_mos={{image=changed.image, display_h=2, display_y=-1}}}
	equal(Tokens.identify(a), nil, "massok changed body/identity rejected: "..changed.label)
end
-- Batch G uniques cannot lend their image to a same-family sibling.
for _, borrowed in ipairs({
	{name="Krogar", type="humanoid", subtype="orc", define_as="CORRUPTOR", image="npc/humanoid_orc_massok_the_dragonslayer.png"},
	{name="Pale Drake", type="undead", subtype="skeleton", define_as="PALE_DRAKE", image="npc/the_master.png"},
	{name="The Master", type="undead", subtype="vampire", define_as="THE_MASTER", image="npc/undead_skeleton_pale_drake.png"},
}) do
	local a = {name=borrowed.name, type=borrowed.type, subtype=borrowed.subtype, define_as=borrowed.define_as, unique=true,
		image="invis.png", add_mos={{image=borrowed.image, display_h=2, display_y=-1}}}
	equal(Tokens.identify(a), nil, "unique cannot borrow a sibling's image "..borrowed.name.." <- "..borrowed.image)
end

-- Batch H: exact single-image entries for ordinary identities. Same-family
-- siblings can neither borrow each other's image nor wear a tall/native-tall
-- shape, and a non-unique entry never admits a unique actor.
local batch_h = {"sandworm", "sandworm-destroyer", "sandworm-burrower", "white-crystal", "red-crystal",
	"crimson-crystal", "poison-ivy", "honey-tree", "necromancer", "fleshy-experiment", "boney-experiment",
	"sanguine-experiment"}
local families = {
	{"sandworm", "sandworm-destroyer", "sandworm-burrower", "sandworm-queen"},
	{"white-crystal", "red-crystal", "crimson-crystal", "spellblaze-crystal"},
	{"poison-ivy", "honey-tree", "venus-flytrap"},
	{"fleshy-experiment", "boney-experiment", "sanguine-experiment"},
}
for _, id in ipairs(batch_h) do
	local entry = Tokens.by_id[id]
	if entry == nil then error("batch H catalog entry missing: "..id) end
	equal(entry.unique, nil, "batch H entry is non-unique "..id)
	equal(entry.native_tall, nil, "batch H entry is single-image "..id)
	local a = actor(entry)
	equal(Tokens.identify(a), id, "batch H exact identity "..id)
	-- Native tint is baked into tint_r/g/b by Entity:resolve; colour only.
	a.tint_r, a.tint_g, a.tint_b = 1, 0.2, 0.2
	equal(Tokens.identify(a), id, "native tint does not change identity "..id)
	a = actor(entry)
	a.unique = true
	equal(Tokens.identify(a), nil, "batch H entry rejects an unknown unique "..id)
	a = actor(entry)
	a.image = "invis.png"
	a.add_mos = {{image=entry.image, display_h=2, display_y=-1}}
	equal(Tokens.identify(a), nil, "batch H single-image entry rejects a tall body "..id)
end
for _, family in ipairs(families) do
	for _, id in ipairs(family) do
		for _, other in ipairs(family) do
			if id ~= other then
				local a = actor(Tokens.by_id[id])
				a.image = Tokens.by_id[other].image
				equal(Tokens.identify(a), nil, "sibling cannot borrow image "..id.." <- "..other)
			end
		end
	end
end
-- define_as is part of the two defined identities.
local burrower = actor(Tokens.by_id["sandworm-burrower"])
burrower.define_as = nil
equal(Tokens.identify(burrower), nil, "burrower requires SANDWORM_TUNNELER")
local plain = actor(Tokens.by_id["sandworm"])
plain.define_as = "SANDWORM_TUNNELER"
equal(Tokens.identify(plain), nil, "plain sandworm cannot claim the burrower definition")
local necro = actor(Tokens.by_id["necromancer"])
necro.define_as = nil
equal(Tokens.identify(necro), nil, "Necromancer requires NECROMANCER")
-- Same-family natives that stay native, including the crystal sharing white
-- crystal's native PNG.
for _, excluded in ipairs({
	{name="shimmering crystal", type="immovable", subtype="crystal", image="npc/crystal_npc.png"},
	{name="black crystal", type="immovable", subtype="crystal", image="npc/crystal_black.png"},
	{name="blue crystal", type="immovable", subtype="crystal", image="npc/crystal_blue.png"},
	-- (the sand-drake was kept native here; batch Q maps it.)
	{name="huge sandworm burrower", type="vermin", subtype="sandworm", image="invis.png", add_mos={{image="npc/vermin_sandworm_huge_sandworm_burrower.png", display_h=2, display_y=-1}}},
	-- (corrosive tunneler and gravity worm were kept native here and in
	-- batch K; batch O maps both, see the batch O section.)
	-- (the orc necromancer was kept native here; batch R maps it.)
	{name="Sandworm Queen", type="vermin", subtype="sandworm", image="npc/vermin_sandworm_sandworm.png", define_as="SANDWORM_QUEEN", unique=true},
}) do
	equal(Tokens.identify(excluded), nil, "batch H sibling stays native "..excluded.name)
end

-- Batch I: exact entries; non-unique
-- ones reject an unknown unique, siblings cannot borrow each other's image,
-- and the tall native body matches only for the native-tall uniques.
local batch_i = {"green-ooze", "crimson-ooze", "gelatinous-cube", "malevolent-dimensional-jelly", "harkor-zun-fragment",
	"harkor-zun", "burb-snow-giant-champion", "norgan", "slimy-crawler", "spellblaze-simulacrum", "kryl-feijan-acolyte", "zquikzshl"}
for _, id in ipairs(batch_i) do
	local entry = Tokens.by_id[id]
	if entry == nil then error("batch I catalog entry missing: "..id) end
	equal(Tokens.identify(actor(entry)), id, "batch I exact identity "..id)
	local a = actor(entry)
	a.tint_r, a.tint_g, a.tint_b = 1, 0.2, 0.2
	equal(Tokens.identify(a), id, "tint does not change identity "..id)
	if not entry.unique then
		a = actor(entry)
		a.unique = true
		equal(Tokens.identify(a), nil, "batch I non-unique entry rejects an unknown unique "..id)
	end
	a = actor(entry)
	a.image = "invis.png"
	a.add_mos = {{image=entry.image, display_h=2, display_y=-1}}
	equal(Tokens.identify(a), entry.unique and id or nil, "batch I tall body only for unique entries (catalog rule) "..id)
	if entry.define_as then
		a = actor(entry)
		a.define_as = nil
		equal(Tokens.identify(a), nil, "batch I needs define_as "..id)
	end
end
for _, family in ipairs({
	{"green-ooze", "crimson-ooze", "gelatinous-cube", "black-ooze", "red-ooze", "yellow-ooze", "blue-ooze"},
	{"malevolent-dimensional-jelly", "black-jelly", "blue-jelly", "green-jelly"},
	{"harkor-zun-fragment", "harkor-zun", "lithfengel"},
	{"norgan", "kryl-feijan-acolyte", "necromancer", "harno"},
	{"spellblaze-simulacrum", "spellblaze-crystal"},
	{"zquikzshl", "boney-experiment", "green-mold"},
}) do
	for _, id in ipairs(family) do
		for _, other in ipairs(family) do
			if id ~= other then
				local a = actor(Tokens.by_id[id])
				a.image = Tokens.by_id[other].image
				equal(Tokens.identify(a), nil, "batch I sibling cannot borrow image "..id.." <- "..other)
			end
		end
	end
end
for _, excluded in ipairs({
	{name="elven corruptor", type="humanoid", subtype="elf", image="npc/humanoid_shalore_elven_corruptor.png"},
	{name="Harkor'Zun", type="elemental", subtype="xorn", image="npc/elemental_xorn_harkor_zun.png", define_as="FULL_HARKOR_ZUN", unique=true},
	-- (brittle clear ooze and slimy ooze were kept native here; batch O maps them.)
	-- (the snow giant chieftain was kept native here; batch P maps it.)
	{name="Spellblaze Simulacrum", type="immovable", subtype="crystal", image="npc/spellblaze_simulacrum.png", define_as="OTHER", unique=true},
	{name="skeletal mold", type="immovable", subtype="molds", image="npc/immovable_molds_skeletal_mold.png"},
	{name="Z'quikzshl the skeletal mold", type="immovable", subtype="molds", image="npc/immovable_molds_skeletal_mold.png", unique=true},
}) do
	equal(Tokens.identify(excluded), nil, "batch I look-alike stays native "..excluded.name)
end

-- Batch J: eleven guaranteed bosses/uniques. Every entry is an exact unique
-- bound to its define_as; Weaver Queen, Lady Nashva and The Possessed also
-- match their explicit nice_tile tall body (all uniques do by catalog rule).
local batch_j = {"shardskin", "the-withering-thing", "the-dreaming-one", "weaver-queen", "murgol", "lady-nashva",
	"the-possessed", "subject-z", "grand-corruptor", "assassin-lord", "ben-cruthdar-abomination"}
for _, id in ipairs(batch_j) do
	local entry = Tokens.by_id[id]
	if entry == nil then error("batch J catalog entry missing: "..id) end
	equal(entry.unique, true, "batch J unique "..id)
	equal(Tokens.identify(actor(entry)), id, "batch J exact identity "..id)
	local a = actor(entry)
	a.tint_r, a.tint_g, a.tint_b = 0.6, 0.2, 0.8
	equal(Tokens.identify(a), id, "tint does not change identity "..id)
	a = actor(entry)
	a.image = "invis.png"
	a.add_mos = {{image=entry.image, display_h=2, display_y=-1}}
	equal(Tokens.identify(a), id, "batch J explicit tall body "..id)
	a.add_mos[1].image = nil
	equal(Tokens.identify(a), nil, "batch J tall body without its image (nice_tile{tall=1} shape) "..id)
	a = actor(entry)
	a.define_as = nil
	equal(Tokens.identify(a), nil, "batch J needs define_as "..id)
	a = actor(entry)
	a.define_as = "OTHER_"..entry.define_as
	equal(Tokens.identify(a), nil, "batch J wrong define_as "..id)
	a = actor(entry)
	a.unique = nil
	equal(Tokens.identify(a), id, "batch J ordinary flag does not matter for a unique entry "..id)
	a = actor(entry)
	a.type = entry.type == "humanoid" and "animal" or "humanoid"
	equal(Tokens.identify(a), nil, "batch J type changed "..id)
	a = actor(entry)
	a.subtype = "other-subtype"
	equal(Tokens.identify(a), nil, "batch J subtype changed "..id)
	for _, prefix in ipairs({"gloomy ", "dreaming "}) do
		a = actor(entry)
		a.name = prefix..entry.name
		equal(Tokens.identify(a), nil, "heart-gloom prefix never renames a unique boss "..a.name)
	end
end
-- town-zigur's second Grand Corruptor: same name, define_as and PNG, only the
-- unique field is a string. Same character design, served by the same entry.
do
	local a = actor(Tokens.by_id["grand-corruptor"])
	a.unique = "Grand Corruptor Zigur"
	equal(Tokens.identify(a), "grand-corruptor", "town-zigur Grand Corruptor (same name/define_as/image)")
end
-- Both Grand Corruptors sustain Flame of Urh'Rok from birth: demon/major over
-- the saved humanoid/shalore pair, image unchanged.
do
	local function demon(entry)
		local a = actor(entry)
		a.__old_type = {entry.type, entry.subtype}
		a.type, a.subtype = "demon", "major"
		a.sustain_talents = {T_FLAME_OF_URH_ROK = {}}
		return a
	end
	local gc = Tokens.by_id["grand-corruptor"]
	equal(Tokens.identify(demon(gc)), "grand-corruptor", "Grand Corruptor in Flame of Urh'Rok form")
	local a = demon(gc)
	a.unique = "Grand Corruptor Zigur"
	equal(Tokens.identify(a), "grand-corruptor", "town-zigur Grand Corruptor in Flame of Urh'Rok form")
	a = demon(gc)
	a.sustain_talents = {}
	equal(Tokens.identify(a), nil, "demon/major without the sustained talent stays native")
	a = demon(gc)
	a.sustain_talents = nil
	equal(Tokens.identify(a), nil, "demon/major with no sustain table stays native")
	a = demon(gc)
	a.__old_type = nil
	equal(Tokens.identify(a), nil, "demon/major without a saved body stays native")
	a = demon(gc)
	a.__old_type = {"humanoid", "elf"}
	equal(Tokens.identify(a), nil, "saved body other than the catalog pair stays native")
	a = demon(gc)
	a.__old_type = {"humanoid", "shalore", "extra"}
	equal(Tokens.identify(a), nil, "saved body with extra fields stays native")
	a = demon(gc)
	a.subtype = "minor"
	equal(Tokens.identify(a), nil, "demon form other than demon/major stays native")
	a = demon(gc)
	a.image = "npc/humanoid_shalore_elven_corruptor.png"
	equal(Tokens.identify(a), nil, "demon form with a changed image stays native")
	-- Opt-in only: another entry whose actor sustains the same talent keeps
	-- native art in demon form.
	equal(Tokens.identify(demon(Tokens.by_id["kryl-feijan-acolyte"])), nil,
		"Flame of Urh'Rok form is not accepted for entries without urh_rok_form")
end
for _, family in ipairs({
	{"shardskin", "white-crystal", "red-crystal", "crimson-crystal", "spellblaze-crystal", "spellblaze-simulacrum"},
	{"the-dreaming-one", "spellblaze-crystal", "malevolent-dimensional-jelly"},
	{"the-withering-thing", "wolf", "great-wolf", "dire-wolf", "white-wolf", "warg", "fox"},
	{"weaver-queen", "ungole"},
	{"murgol", "lady-nashva", "lady-zoisla", "naga-tidewarden", "naga-tidecaller"},
	{"the-possessed", "subject-z", "assassin-lord", "thief", "rogue", "cutpurse", "bandit", "harno"},
	{"grand-corruptor", "rhaloren-inquisitor", "necromancer", "kryl-feijan-acolyte"},
	{"ben-cruthdar-abomination", "krogar", "norgan", "bill", "the-abomination"},
}) do
	for _, id in ipairs(family) do
		for _, other in ipairs(family) do
			if id ~= other and (Tokens.by_id[id].unique or Tokens.by_id[other].unique) then
				local a = actor(Tokens.by_id[id])
				a.image = Tokens.by_id[other].image
				equal(Tokens.identify(a), nil, "batch J sibling cannot borrow image "..id.." <- "..other)
			end
		end
	end
end
for _, excluded in ipairs({
	{name="Ben Cruthdar, the Cursed", type="humanoid", subtype="human", image="npc/humanoid_human_ben_cruthdar__the_cursed.png", unique=true},
	{name="Ben Cruthdar, the Cursed", type="humanoid", subtype="temporal", image="npc/humanoid_human_ben_cruthdar__the_cursed.png", define_as="BEN_CRUTHDAR_ABOMINATION", unique=true, faction="enemies"},
	{name="Kyless", type="humanoid", subtype="human", image="invis.png", define_as="KYLESS", unique=true, add_mos={{display_h=2, display_y=-1}}},
	-- (Berethh was kept native here; batch S maps it.)
	{name="weaver hatchling", type="spiderkin", subtype="spider", image="npc/spiderkin_spider_weaver_hatchling.png"},
	{name="Yeek Wayist", type="humanoid", subtype="yeek", image="npc/humanoid_yeek_yeek_wayist.png", define_as="YEEK_WAYIST", unique=true},
	{name="Grand Corruptor", type="humanoid", subtype="shalore", image="npc/humanoid_shalore_elven_corruptor.png", define_as="GRAND_CORRUPTOR", unique=true},
	{name="The Shade", type="undead", subtype="ghost", image="npc/undead_ghost_the_shade.png", define_as="SHADE", unique=true},
	{name="gloomy The Withering Thing", type="animal", subtype="canine", image="npc/animal_canine_the_withering_thing.png", define_as="WITHERING_THING", unique=true},
	{name="dreaming poison ivy", type="immovable", subtype="plants", image="npc/immovable_plants_poison_ivy.png", define_as="OTHER", unique=true},
}) do
	equal(Tokens.identify(excluded), nil, "batch J look-alike stays native "..excluded.name)
end

-- Batch K: twelve identities of the second survey's batch 2. Ten are plain
-- single-image entries (two of them with an explicit image=, ghoul bound to
-- define_as GHOUL); Walrog is a native-tall unique and the gigantic sandworm
-- tunneler a non-unique native_tall entry, both with an explicit nice_tile
-- PNG. Same-family siblings can neither borrow each other's image nor wear
-- a tall body they do not own.
local batch_k = {"squid", "ink-squid", "water-imp", "walrog", "weaver-hatchling", "orb-spinner", "giant-spider",
	"spitting-spider", "chitinous-spider", "ghoul", "drem", "gigantic-sandworm-tunneler"}
local tall_k = {walrog=true, ["gigantic-sandworm-tunneler"]=true}
for _, id in ipairs(batch_k) do
	local entry = Tokens.by_id[id]
	if entry == nil then error("batch K catalog entry missing: "..id) end
	equal(Tokens.identify(actor(entry)), id, "batch K exact identity "..id)
	local a = actor(entry)
	a.tint_r, a.tint_g, a.tint_b = 0.5, 0.9, 0.3
	equal(Tokens.identify(a), id, "batch K tint is colour only "..id)
	a = actor(entry)
	a.image = "invis.png"
	a.add_mos = {{image=entry.image, display_h=2, display_y=-1}}
	if tall_k[id] then
		equal(Tokens.identify(a), id, "batch K explicit nice_tile tall body "..id)
		a.add_mos[1].image = nil
		equal(Tokens.identify(a), nil, "batch K tall body without its image "..id)
		a.add_mos[1] = {image=entry.image, display_h=2, display_y=-1, display_w=2}
		equal(Tokens.identify(a), nil, "batch K tall body with altered width "..id)
		a = actor(entry)
		equal(Tokens.identify(a), id, "batch K tall entry also accepts the single-cell path "..id)
	else
		equal(Tokens.identify(a), nil, "batch K single entry rejects a tall body "..id)
	end
	a = actor(entry)
	a.type = entry.type == "humanoid" and "animal" or "humanoid"
	equal(Tokens.identify(a), nil, "batch K type changed "..id)
	a = actor(entry)
	a.subtype = "other-subtype"
	equal(Tokens.identify(a), nil, "batch K subtype changed "..id)
	a = actor(entry)
	a.shader = "some_shader"
	equal(Tokens.identify(a), nil, "batch K shader keeps native art "..id)
	if not entry.unique then
		a = actor(entry)
		a.unique = true
		equal(Tokens.identify(a), nil, "batch K non-unique entry rejects an unknown unique "..id)
	end
end
equal(Tokens.by_id.walrog.unique, true, "Walrog is a unique entry")
equal(Tokens.by_id.walrog.define_as, nil, "Walrog has no define_as in source")
equal(Tokens.by_id["gigantic-sandworm-tunneler"].native_tall, true, "tunneler is native_tall")
equal(Tokens.by_id["gigantic-sandworm-tunneler"].unique, nil, "tunneler is non-unique")
for _, id in ipairs({"squid", "ink-squid", "water-imp", "weaver-hatchling", "orb-spinner", "giant-spider", "spitting-spider",
	"chitinous-spider", "ghoul", "drem"}) do
	equal(Tokens.by_id[id].native_tall, nil, "batch K single-image entry "..id)
end
-- Family members cannot borrow each other's file, including the neighbours
-- shipped in earlier batches.
for _, family in ipairs({
	{"squid", "ink-squid", "giant-eel", "electric-eel", "dragon-turtle", "ancient-dragon-turtle", "water-imp"},
	{"weaver-hatchling", "orb-spinner", "giant-spider", "spitting-spider", "chitinous-spider"},
	{"drem", "dremling"},
	{"gigantic-sandworm-tunneler", "sandworm", "sandworm-destroyer", "sandworm-burrower", "sandworm-queen"},
	{"ghoul", "skeleton-warrior", "player-ghoul"},
}) do
	for _, id in ipairs(family) do
		for _, other in ipairs(family) do
			if id ~= other and Tokens.by_id[id] and Tokens.by_id[other] then
				local a = actor(Tokens.by_id[id])
				a.image = Tokens.by_id[other].image
				equal(Tokens.identify(a), nil, "batch K sibling cannot borrow image "..id.." <- "..other)
			end
		end
	end
end
-- The ghoul entry needs define_as GHOUL: the Master of Flesh minion (same
-- name, type and default PNG, no define_as), risen corpse and the Walking
-- Corpse effect minion (same PNG, other names) stay native. (Batch N later
-- mapped ghast and ghoulking, whose native leaves have no define_as, so
-- their Master of Flesh minions are the same body; see the batch N section.)
for _, excluded in ipairs({
	{name="ghoul", type="undead", subtype="ghoul", image="npc/undead_ghoul_ghoul.png"},
	{name="ghoul", type="undead", subtype="ghoul", image="npc/undead_ghoul_ghoul.png", define_as="OTHER_GHOUL"},
	{name="ghoul", type="undead", subtype="ghoul", image="npc/undead_ghoul_ghoul.png", define_as="GHOUL", unique=true},
	{name="Ghoul", type="undead", subtype="ghoul", image="npc/undead_ghoul_ghoul.png", define_as="GHOUL"},
	{name="risen corpse", type="undead", subtype="ghoul", image="npc/undead_ghoul_ghoul.png", define_as="RISEN_CORPSE"},
	{name="walking corpse", type="undead", subtype="ghoul", image="npc/undead_ghoul_ghoul.png"},
	-- ghast and ghoulking were kept native here; batch N maps them.
	-- giant spider: the tutorial variant (define_as TUT_SPIDER_1) and the
	-- wild-gift summon (animal/spider) have the same name and PNG.
	{name="giant spider", type="spiderkin", subtype="spider", image="npc/spiderkin_spider_giant_spider.png", define_as="TUT_SPIDER_1"},
	{name="giant spider", type="animal", subtype="spider", image="npc/spiderkin_spider_giant_spider.png"},
	{name="chittering spider", type="spiderkin", subtype="spider", image="npc/spiderkin_spider_chitinous_spider.png", define_as="TUT_SPIDER_2"},
	{name="orb weaver", type="spiderkin", subtype="spider", image="npc/spiderkin_spider_orb_weaver.png"},
	{name="weaver hatchling", type="spiderkin", subtype="spider", image="npc/spiderkin_spider_orb_spinner.png"},
	{name="weaver hatchling", type="spiderkin", subtype="spider", image="npc/spiderkin_spider_weaver_hatchling.png"},
	{name="Walrog", type="aquatic", subtype="demon", image="npc/aquatic_demon_walrog.png", unique=true, define_as="WALROG"},
	{name="Walrog", type="aquatic", subtype="critter", image="npc/aquatic_demon_walrog.png", unique=true},
	{name="walrog", type="aquatic", subtype="demon", image="npc/aquatic_demon_walrog.png"},
	{name="drem", type="horror", subtype="corrupted", image="npc/horror_corrupted_drem.png"},
	{name="drem", type="horror", subtype="corrupted", image="invis.png", add_mos={{image="npc/horror_corrupted_drem.png", display_h=2, display_y=-1}}},
	{name="gigantic sandworm tunneler", type="vermin", subtype="sandworm", image="invis.png", add_mos={{image="npc/vermin_sandworm_gigantic_corrosive_tunneler.png", display_h=2, display_y=-1}}},
	{name="gigantic sandworm tunneler", type="vermin", subtype="sandworm", image="invis.png", add_mos={{display_h=2, display_y=-1}}},
	{name="gigantic sandworm tunneler", type="vermin", subtype="sandworm", image="npc/vermin_sandworm_gigantic_sandworm_tunneler.png", unique=true},
	{name="ink squid", type="aquatic", subtype="critter", image="npc/aquatic_critter_squid.png"},
	{name="squid", type="aquatic", subtype="critter", image="npc/aquatic_critter_ink_squid.png"},
	{name="water imp", type="aquatic", subtype="critter", image="npc/aquatic_demon_water_imp.png"},
}) do
	equal(Tokens.identify(excluded), nil, "batch K look-alike stays native "..excluded.name.." "..tostring(excluded.define_as))
end
-- No name+define_as key extension: every catalog name is still unique.
do
	local names = {}
	for _, entry in ipairs(Tokens.catalog) do
		equal(names[entry.name], nil, "catalog names stay unique "..entry.name)
		names[entry.name] = true
	end
end

-- Batch L: survey-2 batch 3 plus Kyless. Nine ordinary entries are plain
-- single images (the three orcs bound to define_as, the naga myrmidon with an
-- explicit image=); the naga nereid is a non-unique native_tall entry and
-- Kyless a unique one, both from the {tall=1} shorthand.
local batch_l = {"orc-warrior", "orc-soldier", "orc-archer", "naga-myrmidon", "elven-guard", "mean-looking-elven-guard",
	"naga-nereid", "elven-mage", "elven-tempest", "elven-blood-mage", "yaech-diver", "kyless"}
local tall_l = {["naga-nereid"]=true, kyless=true}
local define_l = {["orc-warrior"]="HILL_ORC_WARRIOR", ["orc-soldier"]="ORC", ["orc-archer"]="HILL_ORC_ARCHER", kyless="KYLESS"}
for _, id in ipairs(batch_l) do
	local entry = Tokens.by_id[id]
	if entry == nil then error("batch L catalog entry missing: "..id) end
	equal(entry.define_as, define_l[id], "batch L define_as "..id)
	equal(Tokens.identify(actor(entry)), id, "batch L exact identity "..id)
	local a = actor(entry)
	a.tint_r, a.tint_g, a.tint_b = 0.5, 0.9, 0.3
	equal(Tokens.identify(a), id, "batch L tint is colour only "..id)
	a = actor(entry)
	a.image = "invis.png"
	a.add_mos = {{image=entry.image, display_h=2, display_y=-1}}
	if tall_l[id] then
		equal(Tokens.identify(a), id, "batch L nice_tile tall body "..id)
		a.add_mos[1].image = nil
		equal(Tokens.identify(a), nil, "batch L tall body without its image "..id)
		a.add_mos[1] = {image=entry.image, display_h=2, display_y=-1, display_w=2}
		equal(Tokens.identify(a), nil, "batch L tall body with altered width "..id)
		a.add_mos[1] = {image="npc/humanoid_human_the_possessed.png", display_h=2, display_y=-1}
		equal(Tokens.identify(a), nil, "batch L tall body of another creature "..id)
		a = actor(entry)
		equal(Tokens.identify(a), id, "batch L tall entry also accepts the single-cell path "..id)
	else
		equal(Tokens.identify(a), nil, "batch L single entry rejects a tall body "..id)
	end
	a = actor(entry)
	a.type = "animal"
	equal(Tokens.identify(a), nil, "batch L type changed "..id)
	a = actor(entry)
	a.subtype = "other-subtype"
	equal(Tokens.identify(a), nil, "batch L subtype changed "..id)
	a = actor(entry)
	a.shader = "some_shader"
	equal(Tokens.identify(a), nil, "batch L shader keeps native art "..id)
	a = actor(entry)
	a.moddable_tile = "some_doll"
	equal(Tokens.identify(a), nil, "batch L paper-doll actor keeps native art "..id)
	if not entry.unique then
		a = actor(entry)
		a.unique = true
		equal(Tokens.identify(a), nil, "batch L non-unique entry rejects an unknown unique "..id)
	end
	if define_l[id] then
		a = actor(entry)
		a.define_as = "OTHER_"..define_l[id]
		equal(Tokens.identify(a), nil, "batch L define_as bound "..id)
		a = actor(entry)
		a.define_as = nil
		equal(Tokens.identify(a), nil, "batch L missing define_as "..id)
	else
		a = actor(entry)
		a.define_as = "SOME_DEFINE_AS"
		equal(Tokens.identify(a), nil, "batch L unexpected define_as "..id)
	end
end
equal(Tokens.by_id.kyless.unique, true, "Kyless is a unique entry")
equal(Tokens.by_id["naga-nereid"].native_tall, true, "nereid is native_tall")
equal(Tokens.by_id["naga-nereid"].unique, nil, "nereid is non-unique")
-- Kyless's runtime shape from the batch J live census (image invis.png, one
-- add_mos with display_h=2/display_y=-1, plus the unique string name).
do
	local live = {name="Kyless", type="humanoid", subtype="human", image="invis.png", define_as="KYLESS", unique="Kyless",
		add_mos={{image="npc/humanoid_human_kyless.png", display_h=2, display_y=-1}}, faction="enemies", rank=4}
	equal(Tokens.identify(live), "kyless", "Kyless live census shape maps to his token")
end
-- Same-family siblings and shipped neighbours cannot borrow each other's file.
for _, family in ipairs({
	{"orc-warrior", "orc-soldier", "orc-archer", "brotoq", "golbug", "krogar", "massok"},
	{"elven-guard", "mean-looking-elven-guard", "elven-mage", "elven-tempest", "elven-blood-mage", "rhaloren-inquisitor",
		"kryl-feijan-acolyte", "grand-corruptor", "fillarel-aldaren"},
	{"naga-myrmidon", "naga-nereid", "naga-tidewarden", "naga-tidecaller", "lady-nashva", "lady-zoisla"},
	{"yaech-diver", "murgol"},
	{"kyless", "the-possessed", "subject-z", "assassin-lord", "harno"},
}) do
	for _, id in ipairs(family) do
		for _, other in ipairs(family) do
			if id ~= other and Tokens.by_id[id] and Tokens.by_id[other] then
				local a = actor(Tokens.by_id[id])
				a.image = Tokens.by_id[other].image
				equal(Tokens.identify(a), nil, "batch L sibling cannot borrow image "..id.." <- "..other)
			end
		end
	end
end
-- Name collisions and look-alikes stay native. The Charred Scar attacker has
-- the same name, type and default PNG as the hill orc warrior but define_as
-- ORC_ATTACK; the exact-identity contract rejects it without any
-- name+define_as key extension. The elven cultist was kept native here until
-- batch M mapped it (its Flame of Urh'Rok form is covered below); the other
-- shalore and naga neighbours stay native.
for _, excluded in ipairs({
	{name="orc warrior", type="humanoid", subtype="orc", image="npc/humanoid_orc_orc_warrior.png", define_as="ORC_ATTACK"},
	{name="orc warrior", type="humanoid", subtype="orc", image="npc/humanoid_orc_orc_warrior.png"},
	{name="orc warrior", type="humanoid", subtype="orc", image="npc/humanoid_orc_orc_soldier.png", define_as="HILL_ORC_WARRIOR"},
	{name="orc soldier", type="humanoid", subtype="orc", image="npc/humanoid_orc_orc_soldier.png", define_as="ORC_ATTACK"},
	{name="orc archer", type="humanoid", subtype="orc", image="npc/humanoid_orc_orc_archer.png", define_as="HILL_ORC_WARRIOR"},
	{name="orc archer", type="humanoid", subtype="orc", image="npc/humanoid_orc_orc_archer.png", define_as="HILL_ORC_ARCHER", unique=true},
	-- (the orc necromancer and the elven warrior were kept native here; batch R maps both.)
	{name="elven guard", type="humanoid", subtype="shalore", image="npc/humanoid_shalore_mean_looking_elven_guard.png"},
	{name="mean looking elven guard", type="humanoid", subtype="shalore", image="npc/humanoid_shalore_elven_guard.png"},
	{name="elven corruptor", type="humanoid", subtype="shalore", image="npc/humanoid_shalore_elven_corruptor.png"},
	{name="elven mage", type="humanoid", subtype="shalore", image="npc/humanoid_shalore_elven_tempest.png"},
	{name="naga myrmidon", type="humanoid", subtype="naga", image="npc/naga_myrmidon_2.png"},
	{name="naga myrmidon", type="humanoid", subtype="naga", image="npc/naga_myrmidon_no_armor.png"},
	{name="naga tide huntress", type="humanoid", subtype="naga", image="npc/naga_tide_huntress.png"},
	{name="naga psyren", type="humanoid", subtype="naga", image="npc/naga_psyren.png"},
	{name="naga nereid", type="humanoid", subtype="naga", image="invis.png", add_mos={{image="npc/humanoid_naga_naga_tidecaller.png", display_h=2, display_y=-1}}},
	{name="naga nereid", type="humanoid", subtype="naga", image="npc/humanoid_naga_naga_nereid.png", unique=true},
	{name="yaech hunter", type="humanoid", subtype="yaech", image="npc/humanoid_yaech_yaech_hunter.png"},
	{name="yaech diver", type="humanoid", subtype="yaech", image="npc/humanoid_yaech_yaech_hunter.png"},
	{name="Kyless", type="humanoid", subtype="human", image="invis.png", define_as="KYLESS", unique="Kyless", add_mos={{display_h=2, display_y=-1}}},
	{name="Kyless", type="humanoid", subtype="human", image="npc/humanoid_human_kyless.png", unique=true},
	{name="Kyless", type="humanoid", subtype="thalore", image="npc/humanoid_human_kyless.png", define_as="KYLESS", unique=true},
	{name="Kyless", type="humanoid", subtype="human", image="npc/humanoid_human_kyless.png", define_as="OTHER_KYLESS", unique=true},
	-- (Berethh was kept native here; batch S maps it.)
}) do
	equal(Tokens.identify(excluded), nil, "batch L look-alike stays native "..excluded.name.." "..tostring(excluded.define_as))
end
-- Batch L kept the elven cultist native; batch M maps it (see the batch M
-- section), so the Flame of Urh'Rok opt-in is now limited to two entries.
for _, entry in ipairs(Tokens.catalog) do
	local opted = entry.id == "grand-corruptor" or entry.id == "elven-cultist" or entry.id == "rak-shor" or entry.id == "kors-fury"
	equal(entry.urh_rok_form, opted and true or nil, "Flame of Urh'Rok opt-in stays limited to the Grand Corruptor, elven cultist, Rak'shor and Kor's Fury "..entry.id)
end

-- Batch M: survey-2 batch 4 (void, temporal, air, fire and xorn elementals)
-- plus the elven cultist that batch L kept native. Nine elementals are plain
-- single images with no define_as; greater and ultimate gwelgoroth are
-- non-unique native_tall entries and Fyrk a unique native-tall entry bound to
-- define_as FYRK, all three naming their tall PNG explicitly in nice_tile.
-- The elven cultist is born demon/major (Flame of Urh'Rok sustained at birth,
-- live-checked in batch L) and opts into urh_rok_form like the Grand Corruptor.
local batch_m = {"losgoroth", "manaworm", "telugoroth", "gwelgoroth", "greater-gwelgoroth", "ultimate-gwelgoroth",
	"faeros", "greater-faeros", "fyrk", "umber-hulk", "xorn", "xaren", "elven-cultist"}
local tall_m = {["greater-gwelgoroth"]=true, ["ultimate-gwelgoroth"]=true, fyrk=true}
for _, id in ipairs(batch_m) do
	local entry = Tokens.by_id[id]
	if entry == nil then error("batch M catalog entry missing: "..id) end
	equal(entry.define_as, id == "fyrk" and "FYRK" or nil, "batch M define_as "..id)
	equal(entry.unique, id == "fyrk" and true or nil, "batch M unique flag "..id)
	equal(entry.native_tall, (id == "greater-gwelgoroth" or id == "ultimate-gwelgoroth") and true or nil, "batch M native_tall flag "..id)
	equal(entry.urh_rok_form, id == "elven-cultist" and true or nil, "batch M urh_rok_form flag "..id)
	equal(Tokens.identify(actor(entry)), id, "batch M exact identity "..id)
	local a = actor(entry)
	a.tint_r, a.tint_g, a.tint_b = 0.5, 0.9, 0.3
	equal(Tokens.identify(a), id, "batch M tint is colour only "..id)
	a = actor(entry)
	a.image = "invis.png"
	a.add_mos = {{image=entry.image, display_h=2, display_y=-1}}
	if tall_m[id] then
		equal(Tokens.identify(a), id, "batch M nice_tile tall body "..id)
		a.add_mos[1].image = nil
		equal(Tokens.identify(a), nil, "batch M tall body without its image "..id)
		a.add_mos[1] = {image=entry.image, display_h=2, display_y=-1, display_w=2}
		equal(Tokens.identify(a), nil, "batch M tall body with altered width "..id)
		a.add_mos[1] = {image="npc/humanoid_human_the_possessed.png", display_h=2, display_y=-1}
		equal(Tokens.identify(a), nil, "batch M tall body of another creature "..id)
		a = actor(entry)
		equal(Tokens.identify(a), id, "batch M tall entry also accepts the single-cell path "..id)
	else
		equal(Tokens.identify(a), nil, "batch M single entry rejects a tall body "..id)
	end
	a = actor(entry)
	a.type = "animal"
	equal(Tokens.identify(a), nil, "batch M type changed "..id)
	a = actor(entry)
	a.subtype = "other-subtype"
	equal(Tokens.identify(a), nil, "batch M subtype changed "..id)
	a = actor(entry)
	a.shader = "some_shader"
	equal(Tokens.identify(a), nil, "batch M shader keeps native art "..id)
	a = actor(entry)
	a.moddable_tile = "some_doll"
	equal(Tokens.identify(a), nil, "batch M paper-doll actor keeps native art "..id)
	if not entry.unique then
		a = actor(entry)
		a.unique = true
		equal(Tokens.identify(a), nil, "batch M non-unique entry rejects an unknown unique "..id)
	end
	if id == "fyrk" then
		a = actor(entry)
		a.define_as = "OTHER_FYRK"
		equal(Tokens.identify(a), nil, "batch M define_as bound "..id)
		a = actor(entry)
		a.define_as = nil
		equal(Tokens.identify(a), nil, "batch M missing define_as "..id)
	else
		a = actor(entry)
		a.define_as = "SOME_DEFINE_AS"
		equal(Tokens.identify(a), nil, "batch M unexpected define_as "..id)
	end
end
equal(Tokens.by_id["greater-gwelgoroth"].unique, nil, "greater gwelgoroth is non-unique")
equal(Tokens.by_id["ultimate-gwelgoroth"].unique, nil, "ultimate gwelgoroth is non-unique")
equal(Tokens.by_id["greater-faeros"].native_tall, nil, "greater faeros is a single 64x64 image, not native_tall")
-- Fyrk sustains Burning Wake from birth: its native shader aura is an extra
-- add_mos entry flagged _isshaderaura, before or after the body, and must not
-- push the tall body out of the match (same rule as Harkor'Zun's Stone Skin).
do
	local fyrk = Tokens.by_id.fyrk
	local a = actor(fyrk)
	a.image = "invis.png"
	a.unique = "Fyrk, Faeros High Guard"
	a.add_mos = {{image=fyrk.image, display_h=2, display_y=-1}, {image="shockbolt/aura.png", _isshaderaura=true}}
	equal(Tokens.identify(a), "fyrk", "Fyrk with its Burning Wake aura after the body")
	a.add_mos = {{image="shockbolt/aura.png", _isshaderaura=true}, {image=fyrk.image, display_h=2, display_y=-1}}
	equal(Tokens.identify(a), "fyrk", "Fyrk with its Burning Wake aura before the body")
	a.add_mos = {{image=fyrk.image, display_h=2, display_y=-1}, {image="npc/other.png", display_h=1}}
	equal(Tokens.identify(a), nil, "Fyrk with an extra non-aura overlay stays native")
end
-- Elven cultist: demon/major over the saved humanoid/shalore pair with the
-- sustained talent, image and define_as unchanged (the batch L live census).
do
	local cultist = Tokens.by_id["elven-cultist"]
	equal(cultist.type, "humanoid", "cultist catalog type is the restored body")
	equal(cultist.subtype, "shalore", "cultist catalog subtype is the restored body")
	local function demon()
		local a = actor(cultist)
		a.__old_type = {cultist.type, cultist.subtype}
		a.type, a.subtype = "demon", "major"
		a.sustain_talents = {T_FLAME_OF_URH_ROK = {}}
		return a
	end
	equal(Tokens.identify(demon()), "elven-cultist", "elven cultist in Flame of Urh'Rok form (live census shape)")
	equal(Tokens.identify(actor(cultist)), "elven-cultist", "elven cultist restored to humanoid/shalore after the sustain ends")
	local a = demon()
	a.sustain_talents = {}
	equal(Tokens.identify(a), nil, "cultist demon/major without the sustained talent stays native")
	a = demon()
	a.sustain_talents = nil
	equal(Tokens.identify(a), nil, "cultist demon/major with no sustain table stays native")
	a = demon()
	a.__old_type = nil
	equal(Tokens.identify(a), nil, "cultist demon/major without a saved body stays native")
	a = demon()
	a.__old_type = {"humanoid", "elf"}
	equal(Tokens.identify(a), nil, "cultist saved body other than the catalog pair stays native")
	a = demon()
	a.__old_type = {"humanoid", "shalore", "extra"}
	equal(Tokens.identify(a), nil, "cultist saved body with extra fields stays native")
	a = demon()
	a.subtype = "minor"
	equal(Tokens.identify(a), nil, "cultist demon form other than demon/major stays native")
	a = demon()
	a.image = "npc/humanoid_shalore_elven_corruptor.png"
	equal(Tokens.identify(a), nil, "cultist demon form with a changed image stays native")
	a = demon()
	a.define_as = "SOME_DEFINE_AS"
	equal(Tokens.identify(a), nil, "cultist demon form with a define_as stays native")
	a = demon()
	a.unique = true
	equal(Tokens.identify(a), nil, "cultist demon form of an unknown unique stays native")
	a = demon()
	a.shader = "some_shader"
	equal(Tokens.identify(a), nil, "cultist demon form with a shader stays native")
	a = demon()
	a.name = "elven cultist "
	equal(Tokens.identify(a), nil, "cultist demon form with another name stays native")
	-- The opt-in is per entry: other shalore casters in demon form stay native.
	for _, id in ipairs({"elven-mage", "elven-tempest", "elven-blood-mage", "elven-guard", "kryl-feijan-acolyte"}) do
		local other = actor(Tokens.by_id[id])
		other.__old_type = {other.type, other.subtype}
		other.type, other.subtype = "demon", "major"
		other.sustain_talents = {T_FLAME_OF_URH_ROK = {}}
		equal(Tokens.identify(other), nil, "Flame of Urh'Rok form is not accepted for "..id)
	end
	-- Another entry's saved pair cannot borrow the cultist entry either.
	a = demon()
	a.name = "elven mage"
	a.image = Tokens.by_id["elven-mage"].image
	equal(Tokens.identify(a), nil, "cultist demon form cannot take the elven mage name")
end
-- Same-family siblings and shipped neighbours cannot borrow each other's file.
for _, family in ipairs({
	{"losgoroth", "manaworm", "telugoroth", "shivgoroth"},
	{"gwelgoroth", "greater-gwelgoroth", "ultimate-gwelgoroth", "shivgoroth", "greater-shivgoroth"},
	{"faeros", "greater-faeros", "fyrk", "greater-shivgoroth"},
	{"umber-hulk", "xorn", "xaren", "harkor-zun", "harkor-zun-fragment"},
	{"elven-cultist", "elven-guard", "elven-mage", "elven-tempest", "elven-blood-mage", "kryl-feijan-acolyte", "grand-corruptor"},
}) do
	for _, id in ipairs(family) do
		for _, other in ipairs(family) do
			if id ~= other and Tokens.by_id[id] and Tokens.by_id[other] then
				local a = actor(Tokens.by_id[id])
				a.image = Tokens.by_id[other].image
				equal(Tokens.identify(a), nil, "batch M sibling cannot borrow image "..id.." <- "..other)
			end
		end
	end
end
-- Look-alikes and same-family neighbours stay native. The Town of Point Zero
-- "monstrous losgoroth" wears the losgoroth PNG under another name and
-- define_as; the ultimate faeros and the greater/ultimate telugoroth have tall
-- bodies of their own. Exact names and bodies reject them without any
-- name+define_as key extension.
for _, excluded in ipairs({
	{name="monstrous losgoroth", type="elemental", subtype="void", image="npc/elemental_void_losgoroth.png", define_as="MONSTROUS_LOSGOROTH"},
	{name="losgoroth", type="elemental", subtype="void", image="npc/elemental_void_losgoroth_corrupted.png"},
	{name="losgoroth", type="elemental", subtype="void", image="npc/elemental_void_manaworm.png"},
	{name="losgoroth", type="elemental", subtype="void", image="npc/elemental_void_losgoroth.png", define_as="MONSTROUS_LOSGOROTH"},
	{name="manaworm", type="elemental", subtype="void", image="npc/elemental_void_losgoroth.png"},
	{name="Spacial Disturbance", type="elemental", subtype="void", image="invis.png", define_as="SPACIAL_DISTURBANCE", unique=true},
	{name="greater telugoroth", type="elemental", subtype="temporal", image="invis.png", add_mos={{image="npc/elemental_temporal_greater_telugoroth.png", display_h=2, display_y=-1}}},
	{name="ultimate telugoroth", type="elemental", subtype="temporal", image="invis.png", add_mos={{image="npc/elemental_temporal_ultimate_telugoroth.png", display_h=2, display_y=-1}}},
	{name="telugoroth", type="elemental", subtype="temporal", image="npc/elemental_temporal_greater_telugoroth.png"},
	{name="telugoroth", type="elemental", subtype="temporal", image="invis.png", add_mos={{image="npc/elemental_temporal_greater_telugoroth.png", display_h=2, display_y=-1}}},
	{name="ultimate faeros", type="elemental", subtype="fire", image="invis.png", add_mos={{image="npc/elemental_fire_ultimate_faeros.png", display_h=2, display_y=-1}}},
	{name="faeros", type="elemental", subtype="fire", image="invis.png", add_mos={{image="npc/elemental_fire_ultimate_faeros.png", display_h=2, display_y=-1}}},
	{name="greater faeros", type="elemental", subtype="fire", image="invis.png", add_mos={{image="npc/elemental_fire_ultimate_faeros.png", display_h=2, display_y=-1}}},
	{name="greater faeros", type="elemental", subtype="fire", image="npc/elemental_fire_faeros.png"},
	{name="Fyrk, Faeros High Guard", type="elemental", subtype="fire", image="invis.png", unique=true, add_mos={{image="npc/elemental_fire_fyrk__faeros_high_guard.png", display_h=2, display_y=-1}}},
	{name="Fyrk, Faeros High Guard", type="elemental", subtype="fire", image="invis.png", define_as="FYRK", unique=true, add_mos={{image="npc/elemental_fire_ultimate_faeros.png", display_h=2, display_y=-1}}},
	{name="Fyrk, Faeros High Guard", type="elemental", subtype="ice", image="invis.png", define_as="FYRK", unique=true, add_mos={{image="npc/elemental_fire_fyrk__faeros_high_guard.png", display_h=2, display_y=-1}}},
	{name="greater gwelgoroth", type="elemental", subtype="air", image="invis.png", add_mos={{image="npc/elemental_air_ultimate_gwelgoroth.png", display_h=2, display_y=-1}}},
	{name="ultimate gwelgoroth", type="elemental", subtype="air", image="invis.png", add_mos={{image="npc/elemental_air_greater_gwelgoroth.png", display_h=2, display_y=-1}}},
	{name="gwelgoroth", type="elemental", subtype="air", image="invis.png", add_mos={{image="npc/elemental_air_greater_gwelgoroth.png", display_h=2, display_y=-1}}},
	{name="gwelgoroth", type="elemental", subtype="air", image="npc/elemental_air_greater_gwelgoroth.png"},
	{name="umber hulk", type="elemental", subtype="xorn", image="npc/elemental_xorn_xorn.png"},
	{name="xorn", type="elemental", subtype="xorn", image="npc/elemental_xorn_xaren.png"},
	{name="xaren", type="elemental", subtype="xorn", image="npc/elemental_xorn_umber_hulk.png"},
	{name="xorn", type="elemental", subtype="xorn", image="invis.png", add_mos={{image="npc/elemental_xorn_fragmented_harkor_zun.png", display_h=2, display_y=-1}}},
	{name="Harkor'Zun", type="elemental", subtype="xorn", image="npc/elemental_xorn_harkor_zun.png", define_as="FULL_HARKOR_ZUN", unique=true},
	{name="elven cultist", type="humanoid", subtype="shalore", image="npc/humanoid_shalore_elven_corruptor.png"},
	{name="elven cultist", type="humanoid", subtype="thalore", image="npc/humanoid_shalore_elven_cultist.png"},
	{name="elven cultist", type="demon", subtype="major", image="npc/humanoid_shalore_elven_cultist.png"},
}) do
	equal(Tokens.identify(excluded), nil, "batch M look-alike stays native "..excluded.name.." "..tostring(excluded.define_as))
end

-- Batch N: survey-2 batch 5 (undead: skeleton magus, ghast, ghoulking, bone
-- giant, the four vampire grades, forest and grave wight, shadow stalker and
-- The Shade of Telos). Ten are plain single images; master vampire and bone
-- giant are non-unique native_tall entries naming their tall PNG explicitly in
-- nice_tile; the shadow stalker is bound to define_as SHADOW_STALKER and the
-- Shade of Telos is a unique bound to SHADE_OF_TELOS. None of them opts into
-- urh_rok_form: no identity of the batch knows Flame of Urh'Rok, and the
-- sustains their vampires start at birth only add particles and temporary
-- values.
local batch_n = {"skeleton-magus", "ghast", "ghoulking", "bone-giant", "lesser-vampire", "vampire", "master-vampire",
	"elder-vampire", "forest-wight", "grave-wight", "shadow-stalker", "shade-of-telos"}
local tall_n = {["master-vampire"]=true, ["bone-giant"]=true}
local define_n = {["shadow-stalker"]="SHADOW_STALKER", ["shade-of-telos"]="SHADE_OF_TELOS"}
for _, id in ipairs(batch_n) do
	local entry = Tokens.by_id[id]
	if entry == nil then error("batch N catalog entry missing: "..id) end
	equal(entry.type, "undead", "batch N type "..id)
	equal(entry.define_as, define_n[id], "batch N define_as "..id)
	equal(entry.unique, id == "shade-of-telos" and true or nil, "batch N unique flag "..id)
	equal(entry.native_tall, tall_n[id] and true or nil, "batch N native_tall flag "..id)
	equal(entry.urh_rok_form, nil, "batch N no urh_rok_form "..id)
	equal(Tokens.identify(actor(entry)), id, "batch N exact identity "..id)
	local a = actor(entry)
	a.tint_r, a.tint_g, a.tint_b = 0.5, 0.9, 0.3
	equal(Tokens.identify(a), id, "batch N tint is colour only "..id)
	a = actor(entry)
	a.image = "invis.png"
	a.add_mos = {{image=entry.image, display_h=2, display_y=-1}}
	if tall_n[id] then
		equal(Tokens.identify(a), id, "batch N nice_tile tall body "..id)
		a.add_mos[1].image = nil
		equal(Tokens.identify(a), nil, "batch N tall body without its image "..id)
		a.add_mos[1] = {image=entry.image, display_h=2, display_y=-1, display_w=2}
		equal(Tokens.identify(a), nil, "batch N tall body with altered width "..id)
		a.add_mos[1] = {image="npc/undead_giant_eternal_bone_giant.png", display_h=2, display_y=-1}
		equal(Tokens.identify(a), nil, "batch N tall body of another creature "..id)
		a = actor(entry)
		equal(Tokens.identify(a), id, "batch N tall entry also accepts the single-cell path "..id)
	elseif not entry.unique then
		equal(Tokens.identify(a), nil, "batch N single entry rejects a tall body "..id)
	end
	a = actor(entry)
	a.type = "animal"
	equal(Tokens.identify(a), nil, "batch N type changed "..id)
	a = actor(entry)
	a.subtype = "other-subtype"
	equal(Tokens.identify(a), nil, "batch N subtype changed "..id)
	a = actor(entry)
	a.shader = "invis_edge"
	equal(Tokens.identify(a), nil, "batch N invisibility-rune shader keeps native art "..id)
	a = actor(entry)
	a.moddable_tile = "some_doll"
	equal(Tokens.identify(a), nil, "batch N paper-doll actor keeps native art "..id)
	a = actor(entry)
	a.replace_display = {image="npc/elemental_ice_greater_shivgoroth.png"}
	equal(Tokens.identify(a), nil, "batch N external replace_display keeps native art "..id)
	if not entry.unique then
		a = actor(entry)
		a.unique = true
		equal(Tokens.identify(a), nil, "batch N non-unique entry rejects an unknown unique "..id)
	end
	if define_n[id] then
		a = actor(entry)
		a.define_as = "OTHER_"..define_n[id]
		equal(Tokens.identify(a), nil, "batch N define_as bound "..id)
		a = actor(entry)
		a.define_as = nil
		equal(Tokens.identify(a), nil, "batch N missing define_as "..id)
	else
		a = actor(entry)
		a.define_as = "SOME_DEFINE_AS"
		equal(Tokens.identify(a), nil, "batch N unexpected define_as "..id)
	end
end
equal(Tokens.by_id["bone-giant"].unique, nil, "bone giant is non-unique")
equal(Tokens.by_id["master-vampire"].unique, nil, "master vampire is non-unique")
equal(Tokens.by_id["elder-vampire"].native_tall, nil, "elder vampire is a plain 64x64 image, not native_tall")
equal(Tokens.by_id["shade-of-telos"].native_tall, nil, "the Shade of Telos is a plain 64x64 image")
-- Vampires start Eternal Night, Blur Sight and Phantasmal Shield at birth:
-- particles and temporary values only, so the body keeps matching; the timed
-- effects a random rune can apply set a shader and fall back to native art.
for _, id in ipairs({"lesser-vampire", "vampire", "master-vampire", "elder-vampire"}) do
	local entry = Tokens.by_id[id]
	local a = actor(entry)
	if tall_n[id] then a.image = "invis.png"; a.add_mos = {{image=entry.image, display_h=2, display_y=-1}} end
	a.sustain_talents = {T_ETERNAL_NIGHT={}, T_BLUR_SIGHT={}, T_PHANTASMAL_SHIELD={}}
	a.__particles = {{}, {}}
	a.inc_damage = {all=10}
	equal(Tokens.identify(a), id, "batch N vampire with its birth sustains "..id)
	a.shader = "invis_edge"
	equal(Tokens.identify(a), nil, "batch N vampire under an invisibility rune "..id)
	a.shader = nil
	equal(Tokens.identify(a), id, "batch N vampire after the rune ends "..id)
end
-- Flame of Urh'Rok is not a supported form of any identity of this batch.
for _, id in ipairs(batch_n) do
	local entry = Tokens.by_id[id]
	local a = actor(entry)
	a.__old_type = {entry.type, entry.subtype}
	a.type, a.subtype = "demon", "major"
	a.sustain_talents = {T_FLAME_OF_URH_ROK = {}}
	equal(Tokens.identify(a), nil, "batch N Flame of Urh'Rok form is not accepted for "..id)
end
-- Shadow stalker: Fade is an EFF_FADED temporary value only, so the body keeps
-- matching; the shadow claw and shadow caster share the base and the name
-- "shadow claw" but have other define_as values and other PNGs.
do
	local stalker = Tokens.by_id["shadow-stalker"]
	local a = actor(stalker)
	a.tmp = {EFF_FADED={dur=1}}
	a.invulnerable = 1
	equal(Tokens.identify(a), "shadow-stalker", "shadow stalker while faded")
	a = actor(stalker)
	a.faction = "enemies"
	a.name = "shadow claw"
	equal(Tokens.identify(a), nil, "shadow stalker cannot take the shadow claw name")
	a = actor(stalker)
	a.image = "npc/shadow-claw.png"
	equal(Tokens.identify(a), nil, "shadow stalker cannot wear the shadow claw PNG")
	a = actor(stalker)
	a.image = "npc/shadow-caster.png"
	a.define_as = "SHADOW_CASTER"
	equal(Tokens.identify(a), nil, "shadow stalker cannot wear the shadow caster PNG")
end
-- Necromancer minions share the name, body and PNG of the native ghast,
-- ghoulking and bone giant and are accepted as the same body; a Lord of Skulls
-- renames its minion and so leaves the exact-name key.
for _, id in ipairs({"ghast", "ghoulking", "bone-giant"}) do
	local entry = Tokens.by_id[id]
	local a = actor(entry)
	a.faction = "players"
	a.summoner, a.summon_time = {faction="players"}, 7
	a.ghoul_minion, a.is_bone_giant = id ~= "bone-giant" and id or nil, id == "bone-giant" and "bone_giant" or nil
	if tall_n[id] then a.image = "invis.png"; a.add_mos = {{image=entry.image, display_h=2, display_y=-1}} end
	equal(Tokens.identify(a), id, "batch N necromancer minion is the same body "..id)
	a.name = "Lord of Skulls (bone giant)"
	equal(Tokens.identify(a), nil, "batch N Lord of Skulls minion is renamed and stays native "..id)
end
-- Same-family siblings and shipped neighbours cannot borrow each other's file.
for _, family in ipairs({
	{"skeleton-magus", "skeleton-mage", "skeleton-warrior", "skeleton-archer"},
	{"ghoul", "ghast", "ghoulking"},
	{"lesser-vampire", "vampire", "master-vampire", "elder-vampire", "the-master"},
	{"forest-wight", "grave-wight"},
	{"shadow-stalker", "shade-of-telos", "grave-wight"},
	{"bone-giant", "half-finished-bone-giant"},
}) do
	for _, id in ipairs(family) do
		for _, other in ipairs(family) do
			if id ~= other and Tokens.by_id[id] and Tokens.by_id[other] then
				local a = actor(Tokens.by_id[id])
				a.image = Tokens.by_id[other].image
				equal(Tokens.identify(a), nil, "batch N sibling cannot borrow image "..id.." <- "..other)
			end
		end
	end
end
-- Look-alikes and neighbours stay native: exact names and bodies reject them
-- without any name+define_as key extension.
for _, excluded in ipairs({
	{name="skeleton magus", type="undead", subtype="skeleton", image="npc/skeleton_mage.png"},
	{name="skeleton mage", type="undead", subtype="skeleton", image="npc/undead_skeleton_skeleton_magus.png"},
	{name="skeleton assassin", type="undead", subtype="skeleton", image="npc/undead_skeleton_skeleton_magus.png"},
	{name="ghast", type="undead", subtype="ghoul", image="npc/undead_ghoul_ghoul.png"},
	{name="ghoul", type="undead", subtype="ghoul", image="npc/undead_ghoul_ghast.png", define_as="GHOUL"},
	{name="risen corpse", type="undead", subtype="ghoul", image="npc/undead_ghoul_ghoul.png", define_as="RISEN_CORPSE"},
	{name="vampire lord", type="undead", subtype="vampire", image="npc/vampire_lord.png"},
	{name="vampire", type="undead", subtype="vampire", image="npc/vampire_lord.png"},
	{name="vampire", type="undead", subtype="vampire", image="npc/master_vampire.png"},
	{name="master vampire", type="undead", subtype="vampire", image="npc/elder_vampire.png"},
	{name="elder vampire", type="undead", subtype="vampire", image="invis.png", add_mos={{image="npc/master_vampire.png", display_h=2, display_y=-1}}},
	{name="vampire rat", type="undead", subtype="rodent", image="npc/undead_rodent_vampire_rat.png"},
	{name="eternal bone giant", type="undead", subtype="giant", image="invis.png", add_mos={{image="npc/undead_giant_eternal_bone_giant.png", display_h=2, display_y=-1}}},
	{name="heavy bone giant", type="undead", subtype="giant", image="invis.png", add_mos={{image="npc/undead_giant_heavy_bone_giant.png", display_h=2, display_y=-1}}},
	{name="bone giant", type="undead", subtype="giant", image="invis.png", add_mos={{image="npc/undead_giant_heavy_bone_giant.png", display_h=2, display_y=-1}}},
	{name="barrow wight", type="undead", subtype="wight", image="invis.png", add_mos={{image="npc/barrow_wight.png", display_h=2, display_y=-1}}},
	{name="emperor wight", type="undead", subtype="wight", image="invis.png", add_mos={{image="npc/emperor_wight.png", display_h=2, display_y=-1}}},
	{name="forest wight", type="undead", subtype="wight", image="npc/grave_wight.png"},
	{name="grave wight", type="undead", subtype="wight", image="npc/forest_wight.png"},
	{name="shadow claw", type="undead", subtype="shadow", image="npc/shadow-claw.png", define_as="SHADOW_CLAW"},
	{name="shadow claw", type="undead", subtype="shadow", image="npc/shadow-caster.png", define_as="SHADOW_CASTER"},
	{name="shadow stalker", type="undead", subtype="shadow", image="npc/shadow-stalker.png", define_as="SHADOW_CLAW"},
	{name="shadow stalker", type="undead", subtype="shadow", image="npc/shadow-stalker.png"},
	{name="The Shade of Telos", type="undead", subtype="ghost", image="npc/undead_ghost_the_shade_of_telos.png", unique=true},
	{name="The Shade of Telos", type="undead", subtype="lich", image="npc/undead_ghost_the_shade_of_telos.png", define_as="SHADE_OF_TELOS", unique=true},
	{name="the shade", type="undead", subtype="skeleton", image="npc/undead_skeleton_the_shade.png", unique=true},
}) do
	equal(Tokens.identify(excluded), nil, "batch N look-alike stays native "..excluded.name.." "..tostring(excluded.define_as))
end

-- Batch O: survey-2 batch 6 (oozes, worms, minor demons, horrors). Eight are
-- plain single images with no define_as; the carrion worm mass is bound to
-- define_as CARRION_WORM_MASS; the two gigantic worms (K kept them native, O
-- maps them) are non-unique native_tall entries with an explicit nice_tile PNG
-- and the onilug is non-unique native_tall through the {tall=1} shorthand.
local batch_o = {"white-ooze", "slimy-ooze", "poison-ooze", "brittle-clear-ooze", "gigantic-corrosive-tunneler",
	"gigantic-gravity-worm", "carrion-worm-mass", "cute-little-bunny", "dredgling", "onilug", "wretchling", "brecklorn"}
local tall_o = {["gigantic-corrosive-tunneler"]=true, ["gigantic-gravity-worm"]=true, onilug=true}
local define_o = {["carrion-worm-mass"]="CARRION_WORM_MASS"}
for _, id in ipairs(batch_o) do
	local entry = Tokens.by_id[id]
	if entry == nil then error("batch O catalog entry missing: "..id) end
	equal(entry.define_as, define_o[id], "batch O define_as "..id)
	equal(entry.unique, nil, "batch O non-unique "..id)
	equal(entry.native_tall, tall_o[id] and true or nil, "batch O native_tall flag "..id)
	equal(entry.urh_rok_form, nil, "batch O no urh_rok_form "..id)
	equal(Tokens.identify(actor(entry)), id, "batch O exact identity "..id)
	local a = actor(entry)
	a.tint_r, a.tint_g, a.tint_b = 0.5, 0.9, 0.3
	equal(Tokens.identify(a), id, "batch O tint is colour only "..id)
	a = actor(entry)
	a.image = "invis.png"
	a.add_mos = {{image=entry.image, display_h=2, display_y=-1}}
	if tall_o[id] then
		equal(Tokens.identify(a), id, "batch O nice_tile tall body "..id)
		a.add_mos[1].image = nil
		equal(Tokens.identify(a), nil, "batch O tall body without its image "..id)
		a.add_mos[1] = {image=entry.image, display_h=2, display_y=-1, display_w=2}
		equal(Tokens.identify(a), nil, "batch O tall body with altered width "..id)
		a.add_mos[1] = {image="npc/vermin_sandworm_huge_sandworm_burrower.png", display_h=2, display_y=-1}
		equal(Tokens.identify(a), nil, "batch O tall body of another creature "..id)
		a = actor(entry)
		equal(Tokens.identify(a), id, "batch O tall entry also accepts the single-cell path "..id)
	else
		equal(Tokens.identify(a), nil, "batch O single entry rejects a tall body "..id)
	end
	a = actor(entry)
	a.type = "animal"
	equal(Tokens.identify(a), nil, "batch O type changed "..id)
	a = actor(entry)
	a.subtype = "other-subtype"
	equal(Tokens.identify(a), nil, "batch O subtype changed "..id)
	a = actor(entry)
	a.shader = "some_shader"
	equal(Tokens.identify(a), nil, "batch O shader keeps native art "..id)
	a = actor(entry)
	a.moddable_tile = "some_doll"
	equal(Tokens.identify(a), nil, "batch O paper-doll actor keeps native art "..id)
	a = actor(entry)
	a.unique = true
	equal(Tokens.identify(a), nil, "batch O non-unique entry rejects an unknown unique "..id)
	if define_o[id] then
		a = actor(entry)
		a.define_as = "OTHER_"..define_o[id]
		equal(Tokens.identify(a), nil, "batch O define_as bound "..id)
		a = actor(entry)
		a.define_as = nil
		equal(Tokens.identify(a), nil, "batch O missing define_as "..id)
	else
		a = actor(entry)
		a.define_as = "SOME_DEFINE_AS"
		equal(Tokens.identify(a), nil, "batch O unexpected define_as "..id)
	end
end
-- K kept the corrosive tunneler and gravity worm native; O maps them, and
-- neither can wear the other's or the batch K tunneler's tall body.
for _, pair in ipairs({
	{"gigantic-corrosive-tunneler", "gigantic-gravity-worm"}, {"gigantic-gravity-worm", "gigantic-corrosive-tunneler"},
	{"gigantic-corrosive-tunneler", "gigantic-sandworm-tunneler"}, {"gigantic-gravity-worm", "gigantic-sandworm-tunneler"},
	{"gigantic-sandworm-tunneler", "gigantic-corrosive-tunneler"}, {"gigantic-sandworm-tunneler", "gigantic-gravity-worm"},
}) do
	local a = actor(Tokens.by_id[pair[1]])
	a.image = "invis.png"
	a.add_mos = {{image=Tokens.by_id[pair[2]].image, display_h=2, display_y=-1}}
	equal(Tokens.identify(a), nil, "batch O worm cannot wear another worm's tall body "..pair[1].." <- "..pair[2])
end
-- The onilug's {tall=1} shorthand expands to invis.png plus add_mos of its own
-- disk-formula PNG; a different PNG under that expansion stays native.
do
	local a = actor(Tokens.by_id.onilug)
	a.image = "invis.png"
	a.add_mos = {{image="npc/demon_minor_wretchling.png", display_h=2, display_y=-1}}
	equal(Tokens.identify(a), nil, "onilug cannot wear the wretchling in its tall expansion")
end
-- Brecklorn starts Gloom (a sustained aura of temporary values and particles):
-- the body keeps matching; dredgling likewise.
for _, id in ipairs({"brecklorn", "dredgling"}) do
	local a = actor(Tokens.by_id[id])
	a.sustain_talents = {T_GLOOM={}}
	a.__particles = {{}}
	a.inc_damage = {all=5}
	equal(Tokens.identify(a), id, "batch O birth sustain keeps the body "..id)
end
-- Flame of Urh'Rok is not a supported form of any identity of this batch.
for _, id in ipairs(batch_o) do
	local entry = Tokens.by_id[id]
	local a = actor(entry)
	a.__old_type = {entry.type, entry.subtype}
	a.type, a.subtype = "demon", "major"
	a.sustain_talents = {T_FLAME_OF_URH_ROK = {}}
	equal(Tokens.identify(a), nil, "batch O Flame of Urh'Rok form is not accepted for "..id)
end
-- Carrion worm mass: the Worm Rot / Infestation summon is now accepted (see
-- the "Same body in another construct" section at the end); multiplied clones
-- keep define_as and stay mapped.
do
	local worm = Tokens.by_id["carrion-worm-mass"]
	local a = actor(worm)
	a.summoner, a.summon_time = {faction="enemies"}, 5
	equal(Tokens.identify(a), "carrion-worm-mass", "native carrion worm with the defining define_as")
end
-- Same-family siblings and shipped neighbours cannot borrow each other's file.
for _, family in ipairs({
	{"white-ooze", "slimy-ooze", "poison-ooze", "brittle-clear-ooze", "green-ooze", "crimson-ooze", "black-ooze", "red-ooze", "yellow-ooze", "blue-ooze", "gelatinous-cube", "white-jelly"},
	{"gigantic-corrosive-tunneler", "gigantic-gravity-worm", "gigantic-sandworm-tunneler", "sandworm", "sandworm-destroyer", "sandworm-burrower", "sandworm-queen"},
	{"carrion-worm-mass", "white-worm-mass", "green-worm-mass", "manaworm"},
	{"cute-little-bunny", "giant-white-mouse", "giant-grey-mouse", "giant-white-rat"},
	{"dredgling", "drem", "dremling"},
	{"brecklorn", "drem", "dremling"},
	{"wretchling", "onilug", "water-imp"},
}) do
	for _, id in ipairs(family) do
		for _, other in ipairs(family) do
			if id ~= other and Tokens.by_id[id] and Tokens.by_id[other] then
				local a = actor(Tokens.by_id[id])
				a.image = Tokens.by_id[other].image
				equal(Tokens.identify(a), nil, "batch O sibling cannot borrow image "..id.." <- "..other)
			end
		end
	end
end
-- Look-alikes stay native: exact names, define_as and bodies reject them.
for _, excluded in ipairs({
	{name="white ooze", type="vermin", subtype="oozes", image="npc/vermin_oozes_slimy_ooze.png"},
	{name="morphic ooze", type="vermin", subtype="oozes", image="npc/vermin_oozes_morphic_ooze.png"},
	{name="bloated ooze", type="vermin", subtype="oozes", image="npc/vermin_oozes_bloated_ooze.png"},
	{name="huge sandworm burrower", type="vermin", subtype="sandworm", image="invis.png", add_mos={{image="npc/vermin_sandworm_huge_sandworm_burrower.png", display_h=2, display_y=-1}}},
	{name="gigantic corrosive tunneler", type="vermin", subtype="sandworm", image="invis.png", add_mos={{image="npc/vermin_sandworm_gigantic_gravity_worm.png", display_h=2, display_y=-1}}},
	{name="carrion worm mass", type="vermin", subtype="worms", image="npc/vermin_worms_carrion_worm_mass.png"},
	{name="carrion worm mass", type="vermin", subtype="worms", image="npc/vermin_worms_carrion_worm_mass.png", define_as="CARRION_WORM_MASS", unique=true},
	{name="carrion worm", type="vermin", subtype="worms", image="npc/vermin_worms_carrion_worm_mass.png", define_as="CARRION_WORM_MASS"},
	{name="cute little bunny", type="vermin", subtype="rodent", image="npc/vermin_rodent_giant_white_mouse.png"},
	{name="dredge", type="horror", subtype="temporal", image="npc/horror_temporal_dredgling.png"},
	{name="dredgling", type="horror", subtype="corrupted", image="npc/horror_temporal_dredgling.png"},
	{name="brecklorn", type="horror", subtype="temporal", image="npc/horror_corrupted_brecklorn.png"},
	{name="wretchling", type="demon", subtype="major", image="npc/demon_minor_wretchling.png"},
	{name="onilug", type="demon", subtype="minor", image="npc/demon_minor_onilug.png", shader="some_shader"},
	{name="fire imp", type="demon", subtype="minor", image="npc/demon_minor_wretchling.png"},
}) do
	equal(Tokens.identify(excluded), nil, "batch O look-alike stays native "..excluded.name.." "..tostring(excluded.define_as))
end

-- Batch P: survey-2 batch 7 (snow giants, minotaur, mountain trolls, ogres,
-- Healer Astelrid). The four snow giants and the minotaur are non-unique
-- native_tall entries with an explicit nice_tile PNG; the four ogres are
-- non-unique native_tall through the {tall=1} shorthand and Healer Astelrid is
-- a unique bound to HEALER_ASTELRID (same shorthand); the two mountain trolls
-- have an explicit 64x64 image= and are plain single entries.
local batch_p = {"snow-giant", "snow-giant-thunderer", "snow-giant-boulder-thrower", "snow-giant-chieftain", "minotaur",
	"mountain-troll", "mountain-troll-thunderer", "ogre-guard", "ogre-mauler", "ogre-rune-spinner", "ogre-pounder", "healer-astelrid"}
local tall_p = {["snow-giant"]=true, ["snow-giant-thunderer"]=true, ["snow-giant-boulder-thrower"]=true, ["snow-giant-chieftain"]=true,
	minotaur=true, ["ogre-guard"]=true, ["ogre-mauler"]=true, ["ogre-rune-spinner"]=true, ["ogre-pounder"]=true}
local define_p = {["healer-astelrid"]="HEALER_ASTELRID"}
for _, id in ipairs(batch_p) do
	local entry = Tokens.by_id[id]
	if entry == nil then error("batch P catalog entry missing: "..id) end
	equal(entry.define_as, define_p[id], "batch P define_as "..id)
	equal(entry.unique, id == "healer-astelrid" and true or nil, "batch P unique flag "..id)
	equal(entry.native_tall, tall_p[id] and true or nil, "batch P native_tall flag "..id)
	equal(entry.urh_rok_form, nil, "batch P no urh_rok_form "..id)
	equal(Tokens.identify(actor(entry)), id, "batch P exact identity "..id)
	local a = actor(entry)
	a.tint_r, a.tint_g, a.tint_b = 0.5, 0.9, 0.3
	equal(Tokens.identify(a), id, "batch P tint is colour only "..id)
	a = actor(entry)
	a.image = "invis.png"
	a.add_mos = {{image=entry.image, display_h=2, display_y=-1}}
	if entry.unique or tall_p[id] then
		equal(Tokens.identify(a), id, "batch P nice_tile tall body "..id)
		a.add_mos[1].image = nil
		equal(Tokens.identify(a), nil, "batch P tall body without its image "..id)
		a.add_mos[1] = {image=entry.image, display_h=2, display_y=-1, display_w=2}
		equal(Tokens.identify(a), nil, "batch P tall body with altered width "..id)
		a.add_mos[1] = {image="npc/undead_giant_bone_giant.png", display_h=2, display_y=-1}
		equal(Tokens.identify(a), nil, "batch P tall body of another creature "..id)
		a = actor(entry)
		equal(Tokens.identify(a), id, "batch P tall entry also accepts the single-cell path "..id)
	else
		equal(Tokens.identify(a), nil, "batch P single entry rejects a tall body "..id)
	end
	a = actor(entry)
	a.type = "animal"
	equal(Tokens.identify(a), nil, "batch P type changed "..id)
	a = actor(entry)
	a.subtype = "other-subtype"
	equal(Tokens.identify(a), nil, "batch P subtype changed "..id)
	a = actor(entry)
	a.shader = "some_shader"
	equal(Tokens.identify(a), nil, "batch P shader keeps native art "..id)
	a = actor(entry)
	a.moddable_tile = "some_doll"
	equal(Tokens.identify(a), nil, "batch P paper-doll actor keeps native art "..id)
	if not entry.unique then
		a = actor(entry)
		a.unique = true
		equal(Tokens.identify(a), nil, "batch P non-unique entry rejects an unknown unique "..id)
	end
	if define_p[id] then
		a = actor(entry)
		a.define_as = "OTHER_"..define_p[id]
		equal(Tokens.identify(a), nil, "batch P define_as bound "..id)
		a = actor(entry)
		a.define_as = nil
		equal(Tokens.identify(a), nil, "batch P missing define_as "..id)
	else
		a = actor(entry)
		a.define_as = "SOME_DEFINE_AS"
		equal(Tokens.identify(a), nil, "batch P unexpected define_as "..id)
	end
end
equal(Tokens.by_id["healer-astelrid"].native_tall, nil, "Astelrid is native-tall through unique, not the flag")
-- Healer Astelrid's live shape: the {tall=1} expansion with the unique string.
do
	local live = {name="Healer Astelrid", type="giant", subtype="ogre", image="invis.png", define_as="HEALER_ASTELRID", unique="Healer Astelrid",
		add_mos={{image="npc/giant_ogre_healer_astelrid.png", display_h=2, display_y=-1}}, faction="enemies", rank=4}
	equal(Tokens.identify(live), "healer-astelrid", "Astelrid tall census shape maps to her token")
	live.define_as = nil
	equal(Tokens.identify(live), nil, "an unbound unique of her name stays native")
end
-- Birth sustains of the ogre body (Arcane Shield, Living Lightning) and the
-- mountain troll thunderer's Thunderstorm are temporary values and particles.
for _, pair in ipairs({{"healer-astelrid", {T_ARCANE_SHIELD={}, T_LIVING_LIGHTNING={}}}, {"mountain-troll-thunderer", {T_THUNDERSTORM={}}}}) do
	local a = actor(Tokens.by_id[pair[1]])
	a.sustain_talents = pair[2]
	a.__particles = {{}}
	a.inc_damage = {all=5}
	equal(Tokens.identify(a), pair[1], "batch P birth sustain keeps the body "..pair[1])
end
-- Flame of Urh'Rok is not a supported form of any identity of this batch.
for _, id in ipairs(batch_p) do
	local entry = Tokens.by_id[id]
	local a = actor(entry)
	a.__old_type = {entry.type, entry.subtype}
	a.type, a.subtype = "demon", "major"
	a.sustain_talents = {T_FLAME_OF_URH_ROK = {}}
	equal(Tokens.identify(a), nil, "batch P Flame of Urh'Rok form is not accepted for "..id)
end
-- Same-name summons and town leaves that share name, type/subtype and the tall
-- body match like the zone leaf; the wild-summon rename is covered in the
-- "Same body in another construct" section at the end.
do
	local minotaur = Tokens.by_id.minotaur
	local summon = actor(minotaur)
	summon.image = "invis.png"
	summon.add_mos = {{image=minotaur.image, display_h=2, display_y=-1}}
	summon.summoner, summon.summon_time, summon.wild_gift_summon = {faction="players"}, 5, true
	equal(Tokens.identify(summon), "minotaur", "Summon Minotaur wild gift (same name/body/art) matches the zone minotaur token")
	local town = actor(Tokens.by_id["ogre-rune-spinner"])
	town.image = "invis.png"
	town.add_mos = {{image=Tokens.by_id["ogre-rune-spinner"].image, display_h=2, display_y=-1}}
	town.female = true
	equal(Tokens.identify(town), "ogre-rune-spinner", "Elvala town ogre rune-spinner (same name/body/art) matches the zone token")
end
-- The four snow giants, Burb and the bone giant; the minotaurs and the Horned
-- Horror; the trolls; and the ogres with Astelrid cannot borrow each other's
-- file or tall body.
for _, family in ipairs({
	{"snow-giant", "snow-giant-thunderer", "snow-giant-boulder-thrower", "snow-giant-chieftain", "burb-snow-giant-champion", "bone-giant"},
	{"minotaur", "minotaur-maze", "horned-horror"},
	{"mountain-troll", "mountain-troll-thunderer", "forest-troll", "stone-troll", "cave-troll", "prox", "bill", "shax"},
	{"ogre-guard", "ogre-mauler", "ogre-rune-spinner", "ogre-pounder", "healer-astelrid", "bone-giant", "mountain-troll-thunderer"},
}) do
	for _, id in ipairs(family) do
		for _, other in ipairs(family) do
			if id ~= other and Tokens.by_id[id] and Tokens.by_id[other] then
				local a = actor(Tokens.by_id[id])
				a.image = Tokens.by_id[other].image
				equal(Tokens.identify(a), nil, "batch P sibling cannot borrow image "..id.." <- "..other)
				a = actor(Tokens.by_id[id])
				a.image = "invis.png"
				a.add_mos = {{image=Tokens.by_id[other].image, display_h=2, display_y=-1}}
				equal(Tokens.identify(a), nil, "batch P sibling cannot wear another tall body "..id.." <- "..other)
			end
		end
	end
end
-- Look-alikes stay native: exact names, define_as and bodies reject them.
for _, excluded in ipairs({
	{name="snow giant", type="giant", subtype="ice", image="npc/giant_ice_snow_giant_thunderer.png"},
	{name="snow giant", type="giant", subtype="troll", image="npc/giant_ice_snow_giant.png"},
	{name="snow giant", type="giant", subtype="ice", image="invis.png", add_mos={{image="npc/giant_ice_snow_giant_chieftain.png", display_h=2, display_y=-1}}},
	{name="snow giant kidney", type="giant", subtype="ice", image="npc/giant_ice_snow_giant.png"},
	{name="Burb the snow giant champion", type="giant", subtype="ice", image="npc/giant_ice_snow_giant_chieftain.png", define_as="BURB_SNOW_GIANT", unique=true},
	{name="maulotaur", type="giant", subtype="minotaur", image="invis.png", add_mos={{image="npc/giant_minotaur_minotaur.png", display_h=2, display_y=-1}}},
	{name="minotaur", type="giant", subtype="troll", image="npc/giant_minotaur_minotaur.png"},
	{name="Minotaur of the Labyrinth", type="giant", subtype="minotaur", image="npc/giant_minotaur_minotaur.png", define_as="MINOTAUR_MAZE", unique=true},
	{name="mountain troll", type="giant", subtype="troll", image="npc/troll_mt.png"},
	{name="mountain troll", type="giant", subtype="troll", image="npc/troll_m.png", unique=true},
	{name="mountain troll thunderer", type="giant", subtype="ogre", image="npc/troll_mt.png"},
	{name="patchwork troll", type="giant", subtype="troll", image="npc/troll_m.png"},
	{name="ogre warmaster", type="giant", subtype="ogre", image="invis.png", add_mos={{image="npc/giant_ogre_ogre_guard.png", display_h=2, display_y=-1}}},
	{name="ogre sentry", type="giant", subtype="ogre", image="npc/giant_ogre_ogre_mauler.png", define_as="OGRE_SENTRY"},
	{name="ogre guard", type="giant", subtype="ogre", image="invis.png", add_mos={{image="npc/giant_ogre_ogre_mauler.png", display_h=2, display_y=-1}}},
	{name="ogre pounder", type="giant", subtype="troll", image="npc/giant_ogre_ogre_pounder.png"},
	{name="Healer Astelrid", type="giant", subtype="ogre", image="npc/giant_ogre_healer_astelrid.png", unique=true},
	{name="Healer Astelrid", type="giant", subtype="ogre", image="npc/giant_ogre_ogre_guard.png", define_as="HEALER_ASTELRID", unique=true},
	{name="ogre rune-spinner", type="giant", subtype="ogre", image="npc/giant_ogre_healer_astelrid.png"},
}) do
	equal(Tokens.identify(excluded), nil, "batch P look-alike stays native "..excluded.name.." "..tostring(excluded.define_as))
end

-- Batch Q: survey-2 batch 8 (four drake hatchlings, four adult drakes, the
-- sand-drake, Ukllmswwik the Wise, Rantha the Abomination, Briagh). Drakes,
-- hatchlings, the sand-drake and Ukllmswwik are 64x64 default-name single
-- images; the fire drake hatchling and the cold drake bind the define_as their
-- leaves carry; Rantha the Abomination and Briagh are uniques whose nice_tile
-- names the tall PNG explicitly.
local batch_q = {"fire-drake-hatchling", "cold-drake-hatchling", "storm-drake-hatchling", "sand-drake", "venom-drake-hatchling",
	"rantha-abomination", "briagh", "ukllmswwik", "fire-drake", "storm-drake", "cold-drake", "venom-drake"}
local define_q = {["fire-drake-hatchling"]="FIRE_DRAKE_HATCHLING", ["cold-drake"]="NPC_COLD_DRAKE", ["rantha-abomination"]="ABOMINATION_RANTHA",
	briagh="BRIAGH", ukllmswwik="UKLLMSWWIK"}
local unique_q = {["rantha-abomination"]=true, briagh=true, ukllmswwik=true}
for _, id in ipairs(batch_q) do
	local entry = Tokens.by_id[id]
	if entry == nil then error("batch Q catalog entry missing: "..id) end
	equal(entry.define_as, define_q[id], "batch Q define_as "..id)
	equal(entry.unique, unique_q[id] and true or nil, "batch Q unique flag "..id)
	equal(entry.native_tall, nil, "batch Q no native_tall flag "..id)
	equal(entry.urh_rok_form, nil, "batch Q no urh_rok_form "..id)
	equal(Tokens.identify(actor(entry)), id, "batch Q exact identity "..id)
	local a = actor(entry)
	a.tint_r, a.tint_g, a.tint_b = 0.5, 0.9, 0.3
	equal(Tokens.identify(a), id, "batch Q tint is colour only "..id)
	a = actor(entry)
	a.image = "invis.png"
	a.add_mos = {{image=entry.image, display_h=2, display_y=-1}}
	if entry.unique then
		equal(Tokens.identify(a), id, "batch Q unique nice_tile tall body "..id)
		a.add_mos[1].image = nil
		equal(Tokens.identify(a), nil, "batch Q tall body without its image "..id)
		a.add_mos[1] = {image=entry.image, display_h=2, display_y=-1, display_w=2}
		equal(Tokens.identify(a), nil, "batch Q tall body with altered width "..id)
		a.add_mos[1] = {image="npc/dragon_ice_rantha_the_worm.png", display_h=2, display_y=-1}
		equal(Tokens.identify(a), nil, "batch Q tall body of another creature "..id)
	else
		equal(Tokens.identify(a), nil, "batch Q single entry rejects a tall body "..id)
	end
	a = actor(entry)
	a.type = "animal"
	equal(Tokens.identify(a), nil, "batch Q type changed "..id)
	a = actor(entry)
	a.subtype = "other-subtype"
	equal(Tokens.identify(a), nil, "batch Q subtype changed "..id)
	a = actor(entry)
	a.shader = "some_shader"
	equal(Tokens.identify(a), nil, "batch Q shader keeps native art "..id)
	a = actor(entry)
	a.moddable_tile = "some_doll"
	equal(Tokens.identify(a), nil, "batch Q paper-doll actor keeps native art "..id)
	if not entry.unique then
		a = actor(entry)
		a.unique = true
		equal(Tokens.identify(a), nil, "batch Q non-unique entry rejects an unknown unique "..id)
	end
	if define_q[id] then
		a = actor(entry)
		a.define_as = "OTHER_"..define_q[id]
		equal(Tokens.identify(a), nil, "batch Q define_as bound "..id)
		a = actor(entry)
		a.define_as = nil
		equal(Tokens.identify(a), nil, "batch Q missing define_as "..id)
	else
		a = actor(entry)
		a.define_as = "SOME_DEFINE_AS"
		equal(Tokens.identify(a), nil, "batch Q unexpected define_as "..id)
	end
	-- Flame of Urh'Rok is not a supported form of any identity of this batch.
	a = actor(entry)
	a.__old_type = {entry.type, entry.subtype}
	a.type, a.subtype = "demon", "major"
	a.sustain_talents = {T_FLAME_OF_URH_ROK = {}}
	equal(Tokens.identify(a), nil, "batch Q Flame of Urh'Rok form is not accepted for "..id)
end
-- Rantha and Briagh: the live nice_tile shape with the unique string.
do
	local rantha = Tokens.by_id["rantha-abomination"]
	local live = {name=rantha.name, type="dragon", subtype="temporal", image="invis.png", define_as="ABOMINATION_RANTHA", unique=rantha.name,
		add_mos={{image=rantha.image, display_h=2, display_y=-1}}, faction="enemies", rank=3.5}
	equal(Tokens.identify(live), "rantha-abomination", "Rantha the Abomination tall shape maps to her token")
	live.define_as = nil
	equal(Tokens.identify(live), nil, "an unbound unique of her name stays native")
	local briagh = Tokens.by_id.briagh
	live = {name=briagh.name, type="dragon", subtype="sand", image="invis.png", define_as="BRIAGH", unique=briagh.name,
		add_mos={{image=briagh.image, display_h=2, display_y=-1}}, faction="enemies", rank=4}
	equal(Tokens.identify(live), "briagh", "Briagh tall shape maps to his token")
	live.shader_auras = {master_summoner={shader="awesomeaura"}}
	equal(Tokens.identify(live), "briagh", "Briagh keeps his token under a Master Summoner shader aura")
end
-- Birth sustains (Icy Skin on Ukllmswwik and Rantha) are temporary values only.
for _, id in ipairs({"ukllmswwik", "rantha-abomination"}) do
	local a = actor(Tokens.by_id[id])
	a.sustain_talents = {T_ICY_SKIN={}}
	a.__particles = {{}}
	a.resists = {COLD=50}
	equal(Tokens.identify(a), id, "batch Q birth sustain keeps the body "..id)
end
-- Same-name summons: the Wyrmic Fire Drake summon has the same name, type,
-- subtype and PNG and no define_as, so it matches the zone fire drake; the
-- Grand Arrival hatchling is covered in the "Same body in another construct"
-- section at the end.
do
	local summon = actor(Tokens.by_id["fire-drake"])
	summon.summoner, summon.summon_time, summon.wild_gift_summon = {faction="players"}, 5, true
	equal(Tokens.identify(summon), "fire-drake", "Wyrmic Fire Drake summon (same name/PNG) matches the zone fire drake token")
end
-- Hatchlings and adults of each element, the drakes of the other elements, the
-- shipped dragons and the sand family cannot borrow each other's file.
for _, family in ipairs({
	{"fire-drake-hatchling", "fire-drake", "varsha"},
	{"cold-drake-hatchling", "cold-drake", "rantha"},
	{"storm-drake-hatchling", "storm-drake"},
	{"venom-drake-hatchling", "venom-drake"},
	{"fire-drake-hatchling", "cold-drake-hatchling", "storm-drake-hatchling", "venom-drake-hatchling", "sand-drake"},
	{"fire-drake", "cold-drake", "storm-drake", "venom-drake", "sand-drake"},
	{"sand-drake", "briagh", "corrupted-sand-wyrm", "sandworm-destroyer", "sandworm", "gigantic-sandworm-tunneler"},
	{"rantha", "rantha-abomination", "ukllmswwik", "cold-drake", "varsha"},
}) do
	for _, id in ipairs(family) do
		for _, other in ipairs(family) do
			if id ~= other and Tokens.by_id[id] and Tokens.by_id[other] then
				local a = actor(Tokens.by_id[id])
				a.image = Tokens.by_id[other].image
				equal(Tokens.identify(a), nil, "batch Q sibling cannot borrow image "..id.." <- "..other)
				a = actor(Tokens.by_id[id])
				a.image = "invis.png"
				a.add_mos = {{image=Tokens.by_id[other].image, display_h=2, display_y=-1}}
				equal(Tokens.identify(a), nil, "batch Q sibling cannot wear another tall body "..id.." <- "..other)
			end
		end
	end
end
-- Look-alikes stay native: exact names, define_as and bodies reject them.
for _, excluded in ipairs({
	{name="fire drake", type="dragon", subtype="fire", image="npc/dragon_fire_fire_drake_hatchling.png"},
	{name="fire drake", type="dragon", subtype="cold", image="npc/dragon_fire_fire_drake.png"},
	{name="fire wyrm", type="dragon", subtype="fire", image="invis.png", add_mos={{image="npc/dragon_fire_fire_wyrm.png", display_h=2, display_y=-1}}},
	{name="fire drake hatchling", type="dragon", subtype="fire", image="npc/dragon_fire_fire_drake_hatchling.png"},
	{name="cold drake", type="dragon", subtype="cold", image="npc/dragon_cold_cold_drake.png"},
	{name="cold drake", type="dragon", subtype="cold", image="npc/dragon_cold_cold_drake_hatchling.png", define_as="NPC_COLD_DRAKE"},
	{name="ice wyrm", type="dragon", subtype="cold", image="invis.png", add_mos={{image="npc/dragon_cold_ice_wyrm.png", display_h=2, display_y=-1}}},
	{name="storm wyrm", type="dragon", subtype="storm", image="invis.png", add_mos={{image="npc/dragon_storm_storm_wyrm.png", display_h=2, display_y=-1}}},
	{name="venom wyrm", type="dragon", subtype="venom", image="invis.png", add_mos={{image="npc/dragon_venom_venom_wyrm.png", display_h=2, display_y=-1}}},
	{name="sand-drake", type="vermin", subtype="sandworm", image="npc/dragon_sand_sand_drake.png"},
	{name="sand-drake", type="dragon", subtype="sand", image="npc/dragon_sand_sand_drake.png", unique=true},
	{name="Briagh, Great Sand Wyrm", type="dragon", subtype="sand", image="invis.png", add_mos={{image="npc/dragon_sand_briagh__great_sand_wyrm.png", display_h=2, display_y=-1}}},
	{name="Briagh, Great Sand Wyrm", type="dragon", subtype="sand", image="npc/dragon_sand_sand_drake.png", define_as="BRIAGH", unique=true},
	{name="Ukllmswwik the Wise", type="dragon", subtype="water", image="npc/dragon_water_ukllmswwik_the_wise.png", unique=true},
	{name="Rantha the Abomination", type="dragon", subtype="ice", image="invis.png", add_mos={{image="npc/dragon_temporal_rantha_the_abomination.png", display_h=2, display_y=-1}}, define_as="ABOMINATION_RANTHA", unique=true},
	{name="Rantha the Worm", type="dragon", subtype="temporal", image="invis.png", add_mos={{image="npc/dragon_temporal_rantha_the_abomination.png", display_h=2, display_y=-1}}, define_as="RANTHA_THE_WORM", unique=true},
}) do
	equal(Tokens.identify(excluded), nil, "batch Q look-alike stays native "..excluded.name.." "..tostring(excluded.define_as))
end

-- Batch R: the twelve next identities by score (orc necromancer, Rak'shor,
-- Warmaster Gnarg, orc assassin, weaver young, fate spinner, giant green and red
-- ants, quasit, elven warrior, corrupted war dog, grannor'vor). All are 64x64
-- single images (default-name PNG or an explicit image=); Gnarg, Rak'shor and
-- the war dog bind the define_as their leaves carry. Nothing here is native-tall.
local batch_r = {"orc-necromancer", "rak-shor", "warmaster-gnarg", "orc-assassin", "weaver-young", "fate-spinner",
	"giant-green-ant", "giant-red-ant", "quasit", "elven-warrior", "corrupted-war-dog", "grannor-vor"}
local define_r = {["rak-shor"]="RAK_SHOR", ["warmaster-gnarg"]="GNARG", ["corrupted-war-dog"]="CORRUPTED_WAR_DOG"}
local unique_r = {["rak-shor"]=true, ["warmaster-gnarg"]=true}
for _, id in ipairs(batch_r) do
	local entry = Tokens.by_id[id]
	if entry == nil then error("batch R catalog entry missing: "..id) end
	equal(entry.define_as, define_r[id], "batch R define_as "..id)
	equal(entry.unique, unique_r[id] and true or nil, "batch R unique flag "..id)
	equal(entry.native_tall, nil, "batch R no native_tall flag "..id)
	equal(entry.urh_rok_form, id == "rak-shor" and true or nil, "batch R urh_rok_form flag "..id)
	equal(Tokens.identify(actor(entry)), id, "batch R exact identity "..id)
	local a = actor(entry)
	a.tint_r, a.tint_g, a.tint_b = 0.5, 0.9, 0.3
	equal(Tokens.identify(a), id, "batch R tint is colour only "..id)
	a = actor(entry)
	a.color_r, a.color_g, a.color_b = 0, 0, 185
	equal(Tokens.identify(a), id, "batch R colour modulation keeps the token "..id)
	a = actor(entry)
	a.image = "invis.png"
	a.add_mos = {{image=entry.image, display_h=2, display_y=-1}}
	if entry.unique then
		equal(Tokens.identify(a), id, "batch R unique nice_tile tall body "..id)
	else
		equal(Tokens.identify(a), nil, "batch R single entry rejects a tall body "..id)
	end
	a = actor(entry)
	a.type = "undead"
	equal(Tokens.identify(a), nil, "batch R type changed "..id)
	a = actor(entry)
	a.subtype = "other-subtype"
	equal(Tokens.identify(a), nil, "batch R subtype changed "..id)
	a = actor(entry)
	a.shader = "some_shader"
	equal(Tokens.identify(a), nil, "batch R shader keeps native art "..id)
	a = actor(entry)
	a.moddable_tile = "some_doll"
	equal(Tokens.identify(a), nil, "batch R paper-doll actor keeps native art "..id)
	a = actor(entry)
	a.add_displays = {{image="npc/iceblock.png"}}
	equal(Tokens.identify(a), nil, "batch R frozen/pinned add_displays keep native art "..id)
	if not entry.unique then
		a = actor(entry)
		a.unique = true
		equal(Tokens.identify(a), nil, "batch R non-unique entry rejects an unknown unique "..id)
	end
	if define_r[id] then
		a = actor(entry)
		a.define_as = "OTHER_"..define_r[id]
		equal(Tokens.identify(a), nil, "batch R define_as bound "..id)
		a = actor(entry)
		a.define_as = nil
		equal(Tokens.identify(a), nil, "batch R missing define_as "..id)
	else
		a = actor(entry)
		a.define_as = "SOME_DEFINE_AS"
		equal(Tokens.identify(a), nil, "batch R unexpected define_as "..id)
	end
	-- Flame of Urh'Rok is not a supported form of any identity of this batch
	-- (Rak'shor could learn it through his Corruptor auto_class: he then shows
	-- native art, body-changed, and the token returns when it ends).
	a = actor(entry)
	a.__old_type = {entry.type, entry.subtype}
	a.type, a.subtype = "demon", "major"
	a.sustain_talents = {T_FLAME_OF_URH_ROK = {}}
	equal(Tokens.identify(a), entry.urh_rok_form and id or nil, "batch R Flame of Urh'Rok form only for opted-in "..id)
	-- A native shader aura (Rampage, Master Summoner...) is bookkeeping, not a new body.
	a = actor(entry)
	a.add_mos = {{_isshaderaura=true, image="shockbolt/aura.png"}}
	equal(Tokens.identify(a), id, "batch R shader aura entry is ignored "..id)
end
-- Birth sustains are temporary values, callbacks and particles only.
for id, talents in pairs({
	["orc-necromancer"]={"T_HIEMAL_SHIELD", "T_NECROTIC_AURA", "T_PUTRESCENT_LIQUEFACTION", "T_SUFFER_FOR_ME"},
	["rak-shor"]={"T_NECROTIC_AURA", "T_DISCARDED_REFUSE", "T_PUTRESCENT_LIQUEFACTION", "T_BONE_SHIELD"},
	["warmaster-gnarg"]={"T_SLOW_MOTION", "T_BERSERKER_RAGE"},
	["orc-assassin"]={"T_STEALTH", "T_APPLY_POISON"},
	["corrupted-war-dog"]={"T_GRAPPLING_STANCE"},
}) do
	local a = actor(Tokens.by_id[id])
	a.sustain_talents = {}
	for _, tid in ipairs(talents) do a.sustain_talents[tid] = {} end
	a.__particles = {{}}
	a.resists = {COLD=50}
	equal(Tokens.identify(a), id, "batch R birth sustain keeps the body "..id)
end
-- Same native PNG, different names: weaver young / weaver hatchling and the
-- corrupted war dog / dire wolf. Each is matched by its own exact name (and the
-- war dog by its define_as); neither can wear the other's identity.
do
	local young, hatchling = Tokens.by_id["weaver-young"], Tokens.by_id["weaver-hatchling"]
	equal(young.image, hatchling.image, "weaver young and hatchling share one native PNG")
	local a = actor(young)
	a.name = "weaver hatchling"
	equal(Tokens.identify(a), "weaver-hatchling", "a weaver hatchling body resolves to the hatchling token, not the young")
	a = actor(hatchling)
	a.name = "weaver young"
	equal(Tokens.identify(a), "weaver-young", "a weaver young body resolves to the young token")
	a = actor(young)
	a.name = "weaver patriarch"
	equal(Tokens.identify(a), nil, "another weaver name on the same PNG stays native")
	local dog, wolf = Tokens.by_id["corrupted-war-dog"], Tokens.by_id["dire-wolf"]
	equal(dog.image, wolf.image, "the war dog and the dire wolf share one native PNG")
	a = actor(dog)
	a.name, a.define_as = "dire wolf", nil
	equal(Tokens.identify(a), "dire-wolf", "a dire wolf body resolves to the dire wolf token")
	a = actor(wolf)
	a.name = "corrupted war dog"
	equal(Tokens.identify(a), nil, "a dire wolf renamed to the dog without define_as stays native")
	a = actor(dog)
	a.name, a.define_as = "war dog", nil
	equal(Tokens.identify(a), nil, "the keepsake-meadow plain war dog stays native")
	a = actor(dog)
	a.name = "war dog"
	equal(Tokens.identify(a), nil, "a plain war dog name with the dog's define_as stays native")
end
-- Same-family siblings (orcs, spiders, ants, imps, elves, canines, horrors)
-- cannot borrow each other's file.
for _, family in ipairs({
	{"orc-necromancer", "rak-shor", "warmaster-gnarg", "orc-assassin", "orc-warrior", "orc-soldier", "orc-archer", "krogar", "massok"},
	{"weaver-young", "fate-spinner", "orb-spinner", "giant-spider", "chitinous-spider", "spitting-spider", "weaver-queen"},
	{"giant-green-ant", "giant-red-ant", "giant-white-ant", "giant-yellow-ant", "giant-brown-ant", "giant-blue-ant", "giant-carpenter-ant", "giant-black-ant"},
	{"quasit", "onilug", "wretchling", "water-imp"},
	{"elven-warrior", "elven-guard", "mean-looking-elven-guard", "elven-mage"},
	{"grannor-vor", "slimy-crawler", "drem", "dremling", "brecklorn"},
}) do
	for _, id in ipairs(family) do
		for _, other in ipairs(family) do
			if id ~= other and Tokens.by_id[id] and Tokens.by_id[other] and Tokens.by_id[id].image ~= Tokens.by_id[other].image then
				local a = actor(Tokens.by_id[id])
				a.image = Tokens.by_id[other].image
				equal(Tokens.identify(a), nil, "batch R sibling cannot borrow image "..id.." <- "..other)
			end
		end
	end
end
-- Look-alikes stay native: exact names, define_as and bodies reject them.
for _, excluded in ipairs({
	{name="orc necromancer", type="humanoid", subtype="orc", image="npc/humanoid_orc_orc_assassin.png"},
	{name="orc necromancer", type="humanoid", subtype="orc", image="npc/humanoid_orc_orc_necromancer.png", unique=true},
	{name="orc master assassin", type="humanoid", subtype="orc", image="npc/humanoid_orc_orc_master_assassin.png"},
	{name="orc assassin", type="humanoid", subtype="orc", image="npc/humanoid_orc_orc_master_assassin.png"},
	{name="Rak'Shor Cultist", type="humanoid", subtype="orc", image="npc/humanoid_orc_rak_shor_cultist.png", define_as="CULTIST_RAK_SHOR", unique=true},
	{name="Rak'shor, Grand Necromancer of the Pride", type="humanoid", subtype="orc", image="npc/humanoid_orc_rak_shor__grand_necromancer_of_the_pride.png", unique=true},
	{name="Rak'shor, Grand Necromancer of the Pride", type="humanoid", subtype="orc", image="npc/humanoid_orc_rak_shor_cultist.png", define_as="RAK_SHOR", unique=true},
	{name="Warmaster Gnarg", type="humanoid", subtype="orc", image="npc/humanoid_orc_warmaster_gnarg.png", unique=true},
	{name="Warmaster Gnarg", type="humanoid", subtype="orc", image="npc/humanoid_orc_orc_soldier.png", define_as="GNARG", unique=true},
	{name="weaver young", type="spiderkin", subtype="spider", image="npc/spiderkin_spider_weaver_patriarch.png"},
	{name="fate weaver", type="spiderkin", subtype="spider", image="npc/spiderkin_spider_fate_weaver.png"},
	{name="fate spinner", type="spiderkin", subtype="spider", image="npc/spiderkin_spider_fate_weaver.png"},
	{name="giant fire ant", type="insect", subtype="ant", image="npc/fire_ant.png"},
	{name="giant green ant", type="insect", subtype="ant", image="npc/red_ant.png"},
	{name="giant red ant", type="insect", subtype="ant", image="npc/green_ant.png"},
	{name="giant green ant", type="insect", subtype="ant", image="npc/green_ant.png", unique=true},
	{name="quasit", type="demon", subtype="minor", image="npc/demon_minor_onilug.png"},
	{name="quasit", type="demon", subtype="major", image="npc/demon_minor_quasit.png"},
	{name="elven elite warrior", type="humanoid", subtype="shalore", image="npc/humanoid_shalore_elven_warrior.png"},
	{name="elven warrior", type="humanoid", subtype="shalore", image="npc/humanoid_shalore_elven_guard.png"},
	{name="grannor'vin", type="horror", subtype="corrupted", image="npc/horror_corrupted_grannor_vor.png"},
	{name="grannor'vor", type="horror", subtype="corrupted", image="npc/horror_corrupted_grannor_vin.png"},
}) do
	equal(Tokens.identify(excluded), nil, "batch R look-alike stays native "..excluded.name.." "..tostring(excluded.define_as))
end

-- Batch S: twelve identities under the batch R score rule (human sun-paladin,
-- Rodmour, Aluin, Argoniel, Elandar, Mindworm, Berethh, Companion Warrior and
-- Archer, Greater Mummy Lord, Kor's Fury, Borfast). Every define_as is bound.
-- Argoniel and Elandar are non-unique native-tall bodies (native_tall=true);
-- the other ten are 64x64 single images.
local batch_s = {"human-sun-paladin", "high-sun-paladin-rodmour", "aluin-the-fallen", "argoniel", "elandar", "mindworm",
	"berethh", "companion-warrior", "companion-archer", "greater-mummy-lord", "kors-fury", "borfast"}
local define_s = {["human-sun-paladin"]="SUN_PALADIN_DEFENDER", ["high-sun-paladin-rodmour"]="SUN_PALADIN_DEFENDER_RODMOUR",
	["aluin-the-fallen"]="ALUIN", argoniel="ARGONIEL", elandar="ELANDAR", mindworm="MINDWORM", berethh="BERETHH",
	["companion-warrior"]="BERETHH_WARRIOR", ["companion-archer"]="BERETHH_ARCHER", ["greater-mummy-lord"]="GREATER_MUMMY_LORD",
	["kors-fury"]="KOR_FURY", borfast="BORFAST"}
local unique_s = {["high-sun-paladin-rodmour"]=true, ["aluin-the-fallen"]=true, mindworm=true, berethh=true,
	["greater-mummy-lord"]=true, ["kors-fury"]=true, borfast=true}
local tall_s = {argoniel=true, elandar=true}
for _, id in ipairs(batch_s) do
	local entry = Tokens.by_id[id]
	if entry == nil then error("batch S catalog entry missing: "..id) end
	equal(entry.define_as, define_s[id], "batch S define_as "..id)
	equal(entry.unique, unique_s[id] and true or nil, "batch S unique flag "..id)
	equal(entry.native_tall, tall_s[id] and true or nil, "batch S native_tall flag "..id)
	equal(entry.urh_rok_form, id == "kors-fury" and true or nil, "batch S urh_rok_form flag "..id)
	equal(Tokens.identify(actor(entry)), id, "batch S exact identity "..id)
	local a = actor(entry)
	a.tint_r, a.tint_g, a.tint_b = 0.5, 0.9, 0.3
	equal(Tokens.identify(a), id, "batch S tint is colour only "..id)
	a = actor(entry)
	a.color_r, a.color_g, a.color_b = 0, 0, 185
	equal(Tokens.identify(a), id, "batch S colour modulation keeps the token "..id)
	a = actor(entry)
	a.image = "invis.png"
	a.add_mos = {{image=entry.image, display_h=2, display_y=-1}}
	if entry.unique or entry.native_tall then
		equal(Tokens.identify(a), id, "batch S tall body accepted "..id)
	else
		equal(Tokens.identify(a), nil, "batch S single entry rejects a tall body "..id)
	end
	a = actor(entry)
	a.type = "animal"
	equal(Tokens.identify(a), nil, "batch S type changed "..id)
	a = actor(entry)
	a.subtype = "other-subtype"
	equal(Tokens.identify(a), nil, "batch S subtype changed "..id)
	a = actor(entry)
	a.shader = "some_shader"
	equal(Tokens.identify(a), nil, "batch S shader keeps native art "..id)
	a = actor(entry)
	a.moddable_tile = "some_doll"
	equal(Tokens.identify(a), nil, "batch S paper-doll actor keeps native art "..id)
	a = actor(entry)
	a.add_displays = {{image="npc/iceblock.png"}}
	equal(Tokens.identify(a), nil, "batch S frozen/pinned add_displays keep native art "..id)
	if not entry.unique then
		a = actor(entry)
		a.unique = true
		equal(Tokens.identify(a), nil, "batch S non-unique entry rejects an unknown unique "..id)
	end
	a = actor(entry)
	a.define_as = "OTHER_"..define_s[id]
	equal(Tokens.identify(a), nil, "batch S define_as bound "..id)
	a = actor(entry)
	a.define_as = nil
	equal(Tokens.identify(a), nil, "batch S missing define_as "..id)
	a = actor(entry)
	a.__old_type = {entry.type, entry.subtype}
	a.type, a.subtype = "demon", "major"
	a.sustain_talents = {T_FLAME_OF_URH_ROK = {}}
	equal(Tokens.identify(a), entry.urh_rok_form and id or nil, "batch S Flame of Urh'Rok form only for opted-in "..id)
	a = actor(entry)
	a.add_mos = tall_s[id] and {{image=entry.image, display_h=2, display_y=-1}, {_isshaderaura=true, image="shockbolt/aura.png"}} or {{_isshaderaura=true, image="shockbolt/aura.png"}}
	if tall_s[id] then a.image = "invis.png" end
	equal(Tokens.identify(a), id, "batch S shader aura entry is ignored "..id)
end
-- Birth sustains are temporary values, callbacks and particles only.
for id, talents in pairs({
	["aluin-the-fallen"]={"T_GLOOM", "T_WEAKNESS", "T_DISMAY", "T_SANCTUARY", "T_CHANT_OF_LIGHT", "T_MARTYRDOM", "T_WEAPON_OF_LIGHT"},
	argoniel={"T_STONE_SKIN", "T_ILLUMINATE", "T_SPELLCRAFT", "T_ARCANE_POWER"},
	elandar={"T_STONE_SKIN", "T_ILLUMINATE", "T_SPELLCRAFT", "T_ARCANE_POWER"},
	["human-sun-paladin"]={"T_WEAPON_OF_LIGHT", "T_CHANT_OF_FORTRESS"},
	["high-sun-paladin-rodmour"]={"T_WEAPON_OF_LIGHT", "T_CHANT_OF_FORTRESS"},
	borfast={"T_SHIELD_WALL"},
}) do
	local a = actor(Tokens.by_id[id])
	a.sustain_talents = {}
	for _, tid in ipairs(talents) do a.sustain_talents[tid] = {} end
	a.__particles = {{}}
	a.resists = {COLD=50}
	equal(Tokens.identify(a), id, "batch S birth sustain keeps the body "..id)
end
-- Same-name definitions. The define_as-less Gates of Morning "human sun-paladin"
-- is pinned by its own leaf numbers (see the "Same body in another construct"
-- section at the end); a bare same-name actor stays native. The High Peak
-- Argoniel and Elandar are the same appearance contract as the Charred Scar
-- ones and wear the same token.
do
	local paladin = Tokens.by_id["human-sun-paladin"]
	local a = actor(paladin)
	a.define_as = nil
	equal(Tokens.identify(a), nil, "a bare define_as-less human sun-paladin stays native")
	for _, id in ipairs({"argoniel", "elandar"}) do
		a = actor(Tokens.by_id[id])
		a.level_range = {75, nil}
		equal(Tokens.identify(a), id, "the High Peak "..id.." has the same appearance contract")
	end
end
-- Same-family siblings cannot borrow each other's file.
for _, family in ipairs({
	{"human-sun-paladin", "high-sun-paladin-rodmour", "aluin-the-fallen", "elven-warrior", "elven-guard"},
	{"argoniel", "elandar", "mindworm", "elven-mage", "elven-blood-mage", "necromancer"},
	{"berethh", "companion-warrior", "companion-archer", "elven-guard"},
	{"greater-mummy-lord", "kors-fury", "borfast", "ghoul", "ghoulking", "shade-of-telos", "armoured-skeleton-warrior"},
}) do
	for _, id in ipairs(family) do
		for _, other in ipairs(family) do
			if id ~= other and Tokens.by_id[id] and Tokens.by_id[other] and Tokens.by_id[id].image ~= Tokens.by_id[other].image then
				local a = actor(Tokens.by_id[id])
				a.image = Tokens.by_id[other].image
				equal(Tokens.identify(a), nil, "batch S sibling cannot borrow image "..id.." <- "..other)
			end
		end
	end
end
-- Look-alikes stay native: exact names, define_as and bodies reject them.
for _, excluded in ipairs({
	{name="human sun-paladin", type="humanoid", subtype="human", image="npc/humanoid_human_human_sun_paladin.png"},
	{name="human sun-paladin", type="humanoid", subtype="human", image="npc/humanoid_human_human_sun_paladin.png", define_as="SUN_PALADIN_DEFENDER_RODMOUR"},
	{name="High Sun Paladin Aeryn", type="humanoid", subtype="human", image="npc/humanoid_human_high_sun_paladin_aeryn.png", define_as="HIGH_SUN_PALADIN_AERYN", unique=true},
	{name="Aluin the Fallen", type="humanoid", subtype="human", image="npc/humanoid_human_aluin_the_fallen.png", unique=true},
	{name="Argoniel", type="humanoid", subtype="human", image="npc/humanoid_human_argoniel.png"},
	{name="Elandar", type="humanoid", subtype="shalore", image="npc/humanoid_shalore_elandar.png"},
	{name="Mindworm", type="humanoid", subtype="thalore", image="npc/humanoid_thalore_mindworm.png", unique=true},
	{name="Berethh", type="humanoid", subtype="thalore", image="npc/humanoid_thalore_berethh.png", unique=true},
	{name="Berethh", type="humanoid", subtype="human", image="npc/humanoid_thalore_berethh.png", define_as="BERETHH", unique=true},
	{name="Companion Warrior", type="humanoid", subtype="thalore", image="npc/humanoid_elf_elven_archer.png", define_as="BERETHH_WARRIOR"},
	{name="Companion Archer", type="humanoid", subtype="thalore", image="npc/humanoid_elenulach_thief.png", define_as="BERETHH_ARCHER"},
	{name="greater mummy", type="undead", subtype="mummy", image="npc/undead_mummy_greater_mummy_lord.png"},
	{name="Greater Mummy Lord", type="undead", subtype="mummy", image="npc/undead_mummy_greater_mummy_lord.png", unique=true},
	{name="The Shade", type="undead", subtype="ghost", image="npc/undead_ghost_kor_s_fury.png", define_as="SHADE", unique=true},
	{name="Kor's Fury", type="undead", subtype="ghost", image="npc/undead_ghost_the_shade.png", define_as="KOR_FURY", unique=true},
	{name="Borfast the Broken", type="undead", subtype="ghoul", image="npc/undead_ghoul_borfast_the_broken.png", unique=true},
}) do
	equal(Tokens.identify(excluded), nil, "batch S look-alike stays native "..excluded.name.." "..tostring(excluded.define_as))
end

-- Same body in another construct (user decisions 2026-09-29): summons wear the
-- token of the monster they copy, and the define_as-less Gates of Morning
-- human sun-paladin wears human-sun-paladin. Every acceptance is keyed by the
-- construct's own fields and rejects a bare same-name actor.
do
	local function summon(id, extra)
		local entry = Tokens.by_id[id]
		local a = actor(entry)
		a.define_as = nil
		a.faction, a.summoner, a.summon_time, a.summoner_gain_exp = "players", {faction="players"}, 5, true
		a.ai = "summoned"
		if entry.native_tall then a.image = "invis.png"; a.add_mos = {{image=entry.image, display_h=2, display_y=-1}} end
		for k, v in pairs(extra) do a[k] = v end
		return a, entry
	end
	local function negatives(label, id, extra, drop)
		local a, entry = summon(id, extra)
		equal(Tokens.identify(a), id, label.." accepted")
		local function check(mut, why)
			local b = summon(id, extra)
			mut(b)
			equal(Tokens.identify(b), nil, label.." rejected: "..why)
		end
		check(function(b) b.summoner = nil end, "no summoner")
		check(function(b) b.summoner = "someone" end, "summoner not an actor")
		check(function(b) b[drop] = nil end, "missing distinctive field "..drop)
		check(function(b) b.define_as = "UNKNOWN_DEFINE_AS" end, "unknown define_as")
		check(function(b) b.unique = true end, "unique flag")
		check(function(b) b.image = "npc/other_image.png" end, "other image")
		check(function(b) b.type = entry.type == "undead" and "animal" or "undead" end, "other type")
		check(function(b) b.subtype = "other-subtype" end, "other subtype")
		check(function(b) b.shader = "some_shader" end, "shader")
		check(function(b) b.add_mos = {{image="unknown-overlay.png"}} end, "extra add_mos")
		check(function(b) b.add_displays = {{image="npc/iceblock.png"}} end, "add_displays")
		check(function(b) b.moddable_tile = "some_doll" end, "moddable tile")
		check(function(b) b.name = b.name.." x" end, "other name")
		-- The bare same-name actor without the construct's fields stays native.
		local bare = actor(entry)
		bare.define_as = nil
		equal(Tokens.identify(bare), nil, label.." bare same-name actor stays native")
		local bare2 = actor(entry)
		bare2.define_as = nil
		bare2.summoner = {faction="players"}
		equal(Tokens.identify(bare2), nil, label.." same-name summoner-only actor stays native")
	end
	-- (1) Necromancer ghoul minion (master-of-flesh.lua via necroSetupSummon)
	negatives("necromancer ghoul", "ghoul", {necrotic_minion=true, ghoul_minion="ghoul", basic_ghoul_minion=true}, "basic_ghoul_minion")
	do
		local a = summon("ghoul", {necrotic_minion=true, ghoul_minion="ghast", basic_ghoul_minion=true})
		equal(Tokens.identify(a), nil, "ghoul minion tag of another minion is rejected")
		a = summon("ghoul", {necrotic_minion=true, ghoul_minion="ghoul", basic_ghoul_minion=true}); a.necrotic_minion = nil
		equal(Tokens.identify(a), nil, "ghoul without necrotic_minion is rejected")
		a = summon("ghoul", {necrotic_minion=true, ghoul_minion="ghoul", basic_ghoul_minion=true}); a.name = "Risen Ghoul"
		equal(Tokens.identify(a), nil, "Risen Ghoul (another creature) stays native")
	end
	-- (2) Worm Rot / Infestation carrion worm mass (rot.lua carrionworm)
	negatives("carrion worm mass summon", "carrion-worm-mass", {carrion_worm=true}, "carrion_worm")
	do
		local a = summon("carrion-worm-mass", {carrion_worm=true}); a.ai = "dumb_talented_simple"
		equal(Tokens.identify(a), nil, "carrion worm with another AI is rejected")
		a = summon("carrion-worm-mass", {carrion_worm=true}); a.ai, a.ai_state = "party_member", {ai_party="summoned"}
		equal(Tokens.identify(a), "carrion-worm-mass", "carrion worm of a party member (PartyMember AI) is accepted")
		a.ai_state.ai_party = "tactical"
		equal(Tokens.identify(a), nil, "party_member carrion worm with another original AI is rejected")
		a.ai_state = nil
		equal(Tokens.identify(a), nil, "party_member carrion worm without ai_state is rejected")
		a = summon("carrion-worm-mass", {carrion_worm=true}); a.summoner_gain_exp = nil
		equal(Tokens.identify(a), nil, "carrion worm without summoner_gain_exp is rejected")
	end
	-- (3) Wyrmic Grand Arrival escort hatchling (summon-distance.lua on_arrival)
	negatives("Grand Arrival fire drake hatchling", "fire-drake-hatchling",
		{wild_gift_summon=true, wild_gift_summon_ignore_cap=true}, "wild_gift_summon_ignore_cap")
	do
		local a = summon("fire-drake-hatchling", {wild_gift_summon=true, wild_gift_summon_ignore_cap=true}); a.wild_gift_summon = nil
		equal(Tokens.identify(a), nil, "hatchling without wild_gift_summon is rejected")
		-- A hatchling must not be accepted as a fire drake (siblings stay apart).
		a = summon("fire-drake-hatchling", {wild_gift_summon=true, wild_gift_summon_ignore_cap=true}); a.ai, a.ai_state = "party_member", {ai_party="summoned"}
		equal(Tokens.identify(a), "fire-drake-hatchling", "hatchling of a party member (PartyMember AI) is accepted")
		a.ai_state.ai_party = "dumb_talented_simple"
		equal(Tokens.identify(a), nil, "party_member hatchling with another original AI is rejected")
		a = summon("fire-drake-hatchling", {wild_gift_summon=true, wild_gift_summon_ignore_cap=true}); a.image = Tokens.by_id["fire-drake"].image
		equal(Tokens.identify(a), nil, "hatchling cannot wear the fire drake PNG")
	end
	-- (4) "(wild summon)" renames: minotaur, black jelly and fire drake only.
	for _, id in ipairs({"minotaur", "black-jelly", "fire-drake"}) do
		local entry = Tokens.by_id[id]
		local label = id.." wild summon"
		local a = summon(id, {wild_gift_summon=true})
		a.name = entry.name.." (wild summon)"
		equal(Tokens.identify(a), id, label.." accepted")
		for _, case in ipairs({
			{"no summoner", function(b) b.summoner = nil end},
			{"no wild_gift_summon", function(b) b.wild_gift_summon = nil end},
			{"other suffix", function(b) b.name = entry.name.." (tame summon)" end},
			{"prefix form", function(b) b.name = "(wild summon) "..entry.name end},
			{"doubled suffix", function(b) b.name = entry.name.." (wild summon) (wild summon)" end},
			{"unknown define_as", function(b) b.define_as = "UNKNOWN" end},
			{"unique flag", function(b) b.unique = true end},
			{"other image", function(b) b.image = "npc/other_image.png"; b.add_mos = nil end},
			{"other type", function(b) b.type = "undead" end},
			{"shader", function(b) b.shader = "some_shader" end},
			{"extra add_mos", function(b) b.add_mos = {{image="unknown-overlay.png"}} end},
		}) do
			local b = summon(id, {wild_gift_summon=true})
			b.name = entry.name.." (wild summon)"
			case[2](b)
			equal(Tokens.identify(b), nil, label.." rejected: "..case[1])
		end
	end
	-- Other renames and other creatures never gain the suffix form.
	for _, id in ipairs({"wolf", "ghoul", "carrion-worm-mass", "giant-spider", "prox", "high-sun-paladin-rodmour"}) do
		local entry = Tokens.by_id[id]
		local a = actor(entry)
		a.summoner, a.wild_gift_summon = {faction="players"}, true
		a.name = entry.name.." (wild summon)"
		equal(Tokens.identify(a), nil, "wild-summon suffix is not accepted for "..id)
	end
	-- Talent giant spider (animal/spider) is a different body from the spiderkin entry.
	do
		local a = actor(Tokens.by_id["giant-spider"])
		a.type, a.summoner, a.wild_gift_summon = "animal", {faction="players"}, true
		equal(Tokens.identify(a), nil, "Giant Spider wild-gift summon (animal/spider) stays native")
		a.name = "giant spider (wild summon)"
		equal(Tokens.identify(a), nil, "renamed wild-gift giant spider stays native")
	end
	-- Uniques are never borrowed by summons or by a stripped define_as.
	for _, entry in ipairs(Tokens.catalog) do
		if entry.unique and entry.define_as then
			local a = actor(entry)
			a.define_as = nil
			a.summoner, a.necrotic_minion, a.ghoul_minion, a.basic_ghoul_minion = {faction="players"}, true, "ghoul", true
			a.carrion_worm, a.summoner_gain_exp, a.ai, a.wild_gift_summon, a.wild_gift_summon_ignore_cap = true, true, "summoned", true, true
			equal(Tokens.identify(a), nil, "a summon cannot borrow the unique token "..entry.id)
		end
	end
	-- (5) Gates of Morning human sun-paladin (general/npcs/sunwall-town.lua).
	local function gates()
		local a = actor(Tokens.by_id["human-sun-paladin"])
		a.define_as = nil
		a.faction, a.rank, a.rarity, a.exp_worth, a.ai = "sunwall", 3, 3, 1, "tactical"
		a.autolevel, a.life_rating, a.size_category, a.level_range = "warrior", 10, 3, {5}
		return a
	end
	equal(Tokens.identify(gates()), "human-sun-paladin", "Gates of Morning human sun-paladin wears the token")
	local a = gates(); a.level_range = {5, nil}
	equal(Tokens.identify(a), "human-sun-paladin", "Gates paladin with an explicit nil upper level")
	for _, case in ipairs({
		{"level_range", function(b) b.level_range = {10} end},
		{"level_range upper bound", function(b) b.level_range = {5, 20} end},
		{"missing level_range", function(b) b.level_range = nil end},
		{"rank (paladin-vs-vampire vault copy)", function(b) b.rank = 2 end},
		{"rarity", function(b) b.rarity = 1 end},
		{"exp_worth", function(b) b.exp_worth = 0 end},
		{"AI (vault copy)", function(b) b.ai = "dumb_talented_simple" end},
		{"autolevel (vault copy)", function(b) b.autolevel = "warriormage" end},
		{"life_rating", function(b) b.life_rating = 12 end},
		{"unknown define_as", function(b) b.define_as = "UNKNOWN_PALADIN" end},
		{"define_as of the Rodmour", function(b) b.define_as = "SUN_PALADIN_DEFENDER_RODMOUR" end},
		{"unique flag", function(b) b.unique = true end},
		{"summoner", function(b) b.summoner = {faction="players"} end},
		{"other image", function(b) b.image = "npc/humanoid_human_aluin_the_fallen.png" end},
		{"other type", function(b) b.type = "undead" end},
		{"other subtype", function(b) b.subtype = "elf" end},
		{"shader", function(b) b.shader = "some_shader" end},
		{"extra add_mos", function(b) b.add_mos = {{image="unknown-overlay.png"}} end},
		{"other name", function(b) b.name = "human sun-mage" end},
	}) do
		local b = gates()
		case[2](b)
		equal(Tokens.identify(b), nil, "Gates paladin rejected: "..case[1])
	end
	-- Sustained Weapon of Light / Chant of Fortress keep the token like the zone leaf.
	a = gates(); a.sustain_talents = {T_WEAPON_OF_LIGHT={}, T_CHANT_OF_FORTRESS={}}; a.__particles = {{}}
	equal(Tokens.identify(a), "human-sun-paladin", "Gates paladin with birth sustains keeps the token")
	-- No other entry is affected by the paladin pin.
	for _, entry in ipairs(Tokens.catalog) do
		if entry.id ~= "human-sun-paladin" and entry.define_as then
			local b = gates()
			b.name, b.image, b.type, b.subtype = entry.name, entry.image, entry.type, entry.subtype
			equal(Tokens.identify(b), nil, "the paladin pin cannot be borrowed by "..entry.id)
		end
	end
	-- Argoniel and Elandar at High Peak keep matching (same contract as Charred Scar).
	for _, id in ipairs({"argoniel", "elandar"}) do
		local b = actor(Tokens.by_id[id]); b.level_range = {75, nil}
		equal(Tokens.identify(b), id, "High Peak "..id.." still matches")
	end
	-- Elvala ogre rune-spinner and the Wild-gift minotaur keep matching.
	do
		local e = Tokens.by_id["ogre-rune-spinner"]
		local b = actor(e); b.image = "invis.png"; b.add_mos = {{image=e.image, display_h=2, display_y=-1}}; b.female = true
		equal(Tokens.identify(b), "ogre-rune-spinner", "Elvala ogre rune-spinner still matches")
	end
end

-- Vault human sun-paladin (maps/vaults/auto/greater/paladin-vs-vampire.lua):
-- a second exact pin, separate from the Gates of Morning one.
do
	local function vault()
		local a = actor(Tokens.by_id["human-sun-paladin"])
		a.define_as = nil
		a.faction, a.hard_faction, a.rank, a.exp_worth, a.ai = "sunwall", "sunwall", 2, 1, "dumb_talented_simple"
		a.autolevel, a.size_category, a.level_range, a.positive_regen = "warriormage", 3, {10}, 10
		return a
	end
	equal(Tokens.identify(vault()), "human-sun-paladin", "vault human sun-paladin wears the token")
	for _, case in ipairs({
		{"level_range", function(b) b.level_range = {5} end},
		{"level_range upper bound", function(b) b.level_range = {10, 30} end},
		{"missing level_range", function(b) b.level_range = nil end},
		{"rank", function(b) b.rank = 3 end},
		{"rarity present", function(b) b.rarity = 3 end},
		{"exp_worth", function(b) b.exp_worth = 0 end},
		{"AI", function(b) b.ai = "tactical" end},
		{"autolevel", function(b) b.autolevel = "warrior" end},
		{"size_category", function(b) b.size_category = 2 end},
		{"hard_faction", function(b) b.hard_faction = nil end},
		{"positive_regen", function(b) b.positive_regen = nil end},
		{"unknown define_as", function(b) b.define_as = "UNKNOWN_PALADIN" end},
		{"unique flag", function(b) b.unique = true end},
		{"summoner", function(b) b.summoner = {faction="players"} end},
		{"other image", function(b) b.image = "npc/humanoid_human_aluin_the_fallen.png" end},
		{"other type", function(b) b.type = "undead" end},
		{"other subtype", function(b) b.subtype = "elf" end},
		{"shader", function(b) b.shader = "some_shader" end},
		{"extra add_mos", function(b) b.add_mos = {{image="unknown-overlay.png"}} end},
		{"other name", function(b) b.name = "human sun-mage" end},
	}) do
		local b = vault()
		case[2](b)
		equal(Tokens.identify(b), nil, "vault paladin rejected: "..case[1])
	end
	-- A mixed field set (Gates rarity/life_rating on the vault numbers) matches neither pin.
	local m = vault(); m.rarity, m.life_rating = 3, 10
	equal(Tokens.identify(m), nil, "vault/Gates hybrid stays native")
end

-- Localized "(wild summon)" names: native builds ("%s (wild summon)"):tformat(_t(name)).
-- Stub _t/tformat with the zh_hans strings of tome4-chinese-translation/mod-tome.lua.
do
	local zh = {["minotaur"]="米诺陶", ["fire drake"]="火龙", ["black jelly"]="黑果冻怪"}
	local old_t, old_tformat = rawget(_G, "_t"), string.tformat
	local function install_zh()
		_G._t = function(str) return zh[str] or str end
		string.tformat = function(fmt, ...)
			if fmt == "%s (wild summon)" then fmt = "%s（野性召唤）" end
			return fmt:format(...)
		end
	end
	local function restore() _G._t, string.tformat = old_t, old_tformat end
	local function wild(id, name)
		local entry = Tokens.by_id[id]
		local a = actor(entry)
		a.define_as = nil
		a.faction, a.summoner, a.wild_gift_summon, a.ai = "players", {faction="players"}, true, "summoned"
		if entry.native_tall then a.image = "invis.png"; a.add_mos = {{image=entry.image, display_h=2, display_y=-1}} end
		a.name = name
		return a
	end
	-- No locale active: English rename accepted, translated one is not.
	restore()
	for _, id in ipairs({"minotaur", "black-jelly", "fire-drake"}) do
		local en = Tokens.by_id[id].name
		equal(Tokens.identify(wild(id, en.." (wild summon)")), id, "English wild rename without locale "..id)
		equal(Tokens.identify(wild(id, zh[en].."（野性召唤）")), nil, "translated rename without locale rejected "..id)
	end
	install_zh()
	local ok, err = pcall(function()
		for _, id in ipairs({"minotaur", "black-jelly", "fire-drake"}) do
			local en = Tokens.by_id[id].name
			equal(Tokens.identify(wild(id, zh[en].."（野性召唤）")), id, "translated wild rename accepted "..id)
			equal(Tokens.identify(wild(id, en.." (wild summon)")), id, "English wild rename still accepted under zh "..id)
			equal(Tokens.identify(wild(id, zh[en].." (wild summon)")), nil, "translated base + English suffix rejected "..id)
			equal(Tokens.identify(wild(id, en.."（野性召唤）")), nil, "English base + translated suffix rejected "..id)
			equal(Tokens.identify(wild(id, zh[en].."（野性召唤）（野性召唤）")), nil, "doubled translated suffix rejected "..id)
			equal(Tokens.identify(wild(id, "（野性召唤）"..zh[en])), nil, "prefix form rejected "..id)
			equal(Tokens.identify(wild(id, zh[en].."（野性召唤）x")), nil, "trailing text rejected "..id)
			local a = wild(id, zh[en].."（野性召唤）"); a.summoner = nil
			equal(Tokens.identify(a), nil, "translated rename without summoner rejected "..id)
			a = wild(id, zh[en].."（野性召唤）"); a.wild_gift_summon = nil
			equal(Tokens.identify(a), nil, "translated rename without wild_gift_summon rejected "..id)
			a = wild(id, zh[en].."（野性召唤）"); a.type = "undead"
			equal(Tokens.identify(a), nil, "translated rename with another type rejected "..id)
		end
		-- Other entries never gain the localized form.
		for _, other in ipairs({"wolf", "ghoul", "giant-spider", "prox"}) do
			local a = actor(Tokens.by_id[other])
			a.summoner, a.wild_gift_summon = {faction="players"}, true
			a.name = (zh[Tokens.by_id[other].name] or Tokens.by_id[other].name).."（野性召唤）"
			equal(Tokens.identify(a), nil, "localized suffix not accepted for "..other)
		end
		-- A translated name of one covered entry cannot wear another entry's token.
		local a = wild("minotaur", zh["fire drake"].."（野性召唤）")
		equal(Tokens.identify(a), nil, "translated fire drake rename on a minotaur body rejected")
	end)
	restore()
	assert(ok, err)
	-- The live zh_hans client (checked in the fixture) renders the suffix as "%s (野性召唤)".
	_G._t = function(str) return zh[str] or str end
	string.tformat = function(fmt, ...)
		if fmt == "%s (wild summon)" then fmt = "%s (野性召唤)" end
		return fmt:format(...)
	end
	ok, err = pcall(function()
		equal(Tokens.identify(wild("minotaur", "米诺陶 (野性召唤)")), "minotaur", "live zh_hans wild rename accepted")
		equal(Tokens.identify(wild("minotaur", "米诺陶（野性召唤）")), nil, "other punctuation rejected under that locale")
	end)
	restore()
	assert(ok, err)
end

-- Flame of Urh'Rok for Rak'shor and Kor's Fury (user decision 2026-09-29): the
-- native talent never changes the sprite, only type/subtype (saved in
-- __old_type) and a particle, exactly as for the Grand Corruptor.
for _, id in ipairs({"rak-shor", "kors-fury"}) do
	local entry = Tokens.by_id[id]
	local function demon()
		local a = actor(entry)
		a.__old_type = {entry.type, entry.subtype}
		a.type, a.subtype = "demon", "major"
		a.sustain_talents = {T_FLAME_OF_URH_ROK = {}}
		return a
	end
	equal(entry.urh_rok_form, true, "urh_rok_form opt-in "..id)
	equal(Tokens.identify(demon()), id, id.." in Flame of Urh'Rok form")
	equal(Tokens.identify(actor(entry)), id, id.." after the form reverts")
	local a = demon(); a.sustain_talents = {}
	equal(Tokens.identify(a), nil, id.." demon/major without the sustained talent stays native")
	a = demon(); a.sustain_talents = nil
	equal(Tokens.identify(a), nil, id.." demon/major with no sustain table stays native")
	a = demon(); a.__old_type = nil
	equal(Tokens.identify(a), nil, id.." demon/major without a saved body stays native")
	a = demon(); a.__old_type = {"humanoid", "elf"}
	equal(Tokens.identify(a), nil, id.." saved body other than the catalog pair stays native")
	a = demon(); a.__old_type = {entry.type, entry.subtype, "extra"}
	equal(Tokens.identify(a), nil, id.." saved body with extra fields stays native")
	a = demon(); a.subtype = "minor"
	equal(Tokens.identify(a), nil, id.." demon form other than demon/major stays native")
	a = demon(); a.image = "npc/humanoid_shalore_elven_corruptor.png"
	equal(Tokens.identify(a), nil, id.." demon form with a changed image stays native")
	a = demon(); a.define_as = "OTHER_"..entry.define_as
	equal(Tokens.identify(a), nil, id.." demon form with another define_as stays native")
	a = demon(); a.shader = "some_shader"
	equal(Tokens.identify(a), nil, id.." demon form with a shader stays native")
	a = demon(); a.add_mos = {{image="unknown-overlay.png"}}
	equal(Tokens.identify(a), nil, id.." demon form with an extra overlay stays native")
end

for _, excluded in ipairs({
	{name="shadow wolf", type="animal", subtype="canine", image="npc/canine_sw.png"},
	{name="giant squid", type="aquatic", subtype="critter", image="npc/aquatic_critter_squid.png"},
	{name="Rungof the Warg Titan", type="animal", subtype="canine", image="npc/canine_rungof.png", unique=true},
}) do
	equal(Tokens.identify(excluded), nil, "uncovered same-family creature "..excluded.name)
end
equal(Tokens.identify(nil), nil, "missing actor")
equal(Tokens.identify(false), nil, "invalid actor")
equal(pcall(Tokens.image, "../../unverified"), false, "unknown token path rejected")

-- Exercise the actual integration method with small engine adapters. This
-- verifies who may grant the pure mapper's exception, rather than duplicating
-- the authorization predicate in a test-only implementation.
local Base = {display=function() end}
local EngineEntity = {new=function(def)
	def.removeAllMOs=function() end
	return def
end}
local environment_config
local PlayerTokens=dofile(here..'../overload/mod/class/CheckerPlayerTokens.lua')
local environment=setmetatable({
	loadPrevious=function() return Base end,
	require=function(name)
		if name=='engine.Map' then return {} end
		if name=='engine.Entity' then return EngineEntity end
		if name=='mod.class.CheckerTokens' then return Tokens end
		if name=='mod.class.CheckerOptions' then return {
			tokensEnabled=function() return environment_config.settings.tome.checker_tokens_enabled~=false end,
			playerTokensEnabled=function() return true end,
		} end
		if name=='mod.class.CheckerPlayerTokens' then return PlayerTokens end
		error('unexpected Game.lua test dependency: '..name)
	end,
	config={settings={cheat=false,tome={}}},
	__module_extra_info={checker_demo=true},
},{__index=_G})
environment_config=environment.config
local game_chunk
if setfenv then
	game_chunk=assert(loadfile(here..'../superload/mod/class/Game.lua'))
	setfenv(game_chunk,environment)
else
	game_chunk=assert(loadfile(here..'../superload/mod/class/Game.lua','t',environment))
end
local Game=game_chunk()
local members={}
local test_game=setmetatable({
	level={},zone={short_name='trollmire'},checker_mode='refined',
	party={hasMember=function(_,a) return members[a] end},
},{__index=Game})
local function controlledWolf(current, previous, member)
	local a=actor(Tokens.by_id.wolf)
	a.unique,a.__CLASSNAME,a.__PREVIOUS_CLASSNAME='player',current,previous
	a.removeAllMOs=function() end
	members[a]=member
	return a
end
for _,previous in ipairs({'mod.class.PartyMember','mod.class.NPC'}) do
	local a=controlledWolf('mod.class.Player',previous,true)
	equal(test_game:checkerRefreshActor(a),'wolf','native control class accepted '..previous)
	equal(a.replace_display.image,Tokens.image('wolf'),'controlled creature retains wolf artwork '..previous)
	local owned=a.replace_display
	a.__CLASSNAME=previous
	equal(test_game:checkerRefreshActor(a),'wolf','formerly controlled member accepted '..previous)
	equal(a.replace_display,owned,'control return reuses owned Entity '..previous)
	members[a]=nil
	equal(test_game:checkerRefreshActor(a),nil,'leaving real party revokes player exception '..previous)
	equal(a.replace_display,nil,'revoked party identity restores native display '..previous)
end
for _,case in ipairs({
	{'mod.class.Player','mod.class.PartyMember',false,'nonmember'},
	{'mod.class.Player',nil,true,'missing control history'},
	{'mod.class.Player','mod.class.ForeignActor',true,'unverified previous class'},
	{'mod.class.ForeignActor','mod.class.PartyMember',true,'unverified current class'},
}) do
	local a=controlledWolf(case[1],case[2],case[3])
	equal(test_game:checkerRefreshActor(a),nil,'integration rejects '..case[4])
end
local controlled=controlledWolf('mod.class.Player','mod.class.PartyMember',true)
controlled.unique='a named unique'
equal(test_game:checkerRefreshActor(controlled),nil,'real member cannot override named unique protection')
controlled.unique='player'
controlled.replace_display={image='npc/elemental_temporal_telugoroth.png'}
local external=controlled.replace_display
equal(test_game:checkerRefreshActor(controlled),nil,'controlled member keeps external transformation')
equal(controlled.replace_display,external,'external transformed display is not erased')
controlled.replace_display=nil
controlled.image='npc/canine_dw.png'
equal(test_game:checkerRefreshActor(controlled),nil,'controlled member cannot reuse wolf identity for another body')
controlled.image=Tokens.by_id.wolf.image
controlled.shader_auras={native_aura={}}
equal(test_game:checkerRefreshActor(controlled),'wolf','controlled member keeps its token with an active native aura')
local aura_owned=controlled.replace_display
equal(aura_owned.image,Tokens.image('wolf'),'token art installed despite the aura')
controlled.shader_auras=nil
equal(test_game:checkerRefreshActor(controlled),'wolf','clearing the aura keeps the same token')
equal(controlled.replace_display,aura_owned,'no duplicate Entity when the aura clears')
test_game.checker_mode='vanilla'
equal(test_game:checkerRefreshActor(controlled),'wolf','native terrain preserves creature tokens')
environment.config.settings.tome.checker_tokens_enabled=false
equal(test_game:checkerRefreshActor(controlled),nil,'independent token switch removes controlled creature tokens')
equal(controlled.replace_display,nil,'token switch restores controlled creature native body')

-- Aura install/removal contract: pre-existing aura, repeated refresh, removal.
local rebuild_calls=0
controlled.updateModdableTile=function() rebuild_calls=rebuild_calls+1 end
-- An aura applied before any token exists writes native bookkeeping directly
-- onto the actor's own add_mos. Reinstalling must clear that stale bookkeeping
-- and rebuild the aura onto the fresh token via updateModdableTile.
controlled.shader_auras={native_aura={}}
controlled.add_mos={{_isshaderaura=true,image=Tokens.by_id.wolf.image,display_h=2,display_y=-1}}
environment.config.settings.tome.checker_tokens_enabled=true
equal(test_game:checkerRefreshActor(controlled,'display'),'wolf','token installs despite a pre-existing native aura')
equal(controlled.add_mos,nil,'stale native aura bookkeeping cleared from the actor')
equal(rebuild_calls,1,'install with a pre-existing aura rebuilds it onto the token')
local aura_token=controlled.replace_display
-- Repeated refresh with the same token/aura state touches nothing further.
equal(test_game:checkerRefreshActor(controlled,'display'),'wolf','unchanged aura state keeps the token')
equal(controlled.replace_display,aura_token,'no duplicate Entity on repeated refresh')
equal(rebuild_calls,1,'no extra rebuild on an unchanged refresh')
-- Removing the token (independent switch off) while the aura is still active
-- lets the native aura return on the native sprite.
environment.config.settings.tome.checker_tokens_enabled=false
equal(test_game:checkerRefreshActor(controlled,'display'),nil,'token switch removes the token with an active aura')
equal(controlled.replace_display,nil,'native display restored')
equal(rebuild_calls,2,'removal with an active aura rebuilds the native aura')
controlled.shader_auras,controlled.updateModdableTile=nil,nil
environment.config.settings.tome.checker_tokens_enabled=true

print(("token_mapping: %d checks passed; all %d identities and guarded fallbacks verified"):format(checks,#Tokens.catalog))
