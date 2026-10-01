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
	local own, effect = {}, {image="npc/unmapped_native_test_image.png"}
	a.replace_display = own
	equal(Tokens.identify(a, own), entry.id, "owned display "..entry.id)
	equal(Tokens.identify(a), nil, "unclaimed display "..entry.id)
	a.replace_display = effect
	equal(Tokens.identify(a, own), nil, "external transformation "..entry.id)
	a.replace_display = nil
	equal(Tokens.identify(a, own), entry.id, "transformation ended "..entry.id)
	a.image = "npc/unmapped_native_test_image.png"
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
-- Same-family natives that stay native (AG now maps shimmering crystal).
for _, excluded in ipairs({
	-- Shimmering crystal now has its own name-keyed AG token despite sharing the white-crystal PNG.
	-- (the black crystal was kept native here; batch V maps it.)
	-- (the blue crystal was kept native here; batch X maps it.)
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
	-- (Yeek Wayist was kept native here; batch T maps it.)
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
	-- (the orb weaver was kept native here; batch Z maps it.)
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
-- Names remain unique unless the catalog explicitly opts into a composite key.
do
	local names = {}
	for _, entry in ipairs(Tokens.catalog) do
		equal(names[entry.shared_name and (entry.name..":"..entry.define_as) or entry.name], nil, "catalog composite identities stay unique "..entry.name)
		names[entry.shared_name and (entry.name..":"..entry.define_as) or entry.name] = true
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
	-- (the elven corruptor was kept native here; batch X maps it.)
	{name="elven mage", type="humanoid", subtype="shalore", image="npc/humanoid_shalore_elven_tempest.png"},
	{name="naga myrmidon", type="humanoid", subtype="naga", image="npc/naga_myrmidon_2.png"},
	{name="naga myrmidon", type="humanoid", subtype="naga", image="npc/naga_myrmidon_no_armor.png"},
	-- (the naga tide huntress and psyren were kept native here; batch U maps both.)
	{name="naga nereid", type="humanoid", subtype="naga", image="invis.png", add_mos={{image="npc/humanoid_naga_naga_tidecaller.png", display_h=2, display_y=-1}}},
	{name="naga nereid", type="humanoid", subtype="naga", image="npc/humanoid_naga_naga_nereid.png", unique=true},
	-- (the yaech hunter was kept native here; batch V maps it.)
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
	local opted = entry.id == "grand-corruptor" or entry.id == "elven-cultist" or entry.id == "rak-shor" or entry.id == "kors-fury" or entry.id == "weirdling-beast"
	equal(entry.urh_rok_form, opted and true or nil, "Flame of Urh'Rok opt-in stays limited to the Grand Corruptor, elven cultist, Rak'shor, Kor's Fury and the Weirdling Beast "..entry.id)
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
	-- (the greater telugoroth was kept native here; batch X maps it as native-tall.)
	-- (the ultimate telugoroth was kept native here; batch Z maps it as native-tall.)
	{name="telugoroth", type="elemental", subtype="temporal", image="npc/elemental_temporal_greater_telugoroth.png"},
	{name="telugoroth", type="elemental", subtype="temporal", image="invis.png", add_mos={{image="npc/elemental_temporal_greater_telugoroth.png", display_h=2, display_y=-1}}},
-- (the ultimate faeros was kept native here; batch AA maps it as native-tall.)
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
	-- (the vampire lord was kept native here; batch AC maps it on its own PNG.)
	{name="vampire", type="undead", subtype="vampire", image="npc/vampire_lord.png"},
	{name="vampire", type="undead", subtype="vampire", image="npc/master_vampire.png"},
	{name="master vampire", type="undead", subtype="vampire", image="npc/elder_vampire.png"},
	{name="elder vampire", type="undead", subtype="vampire", image="invis.png", add_mos={{image="npc/master_vampire.png", display_h=2, display_y=-1}}},
	{name="vampire rat", type="undead", subtype="rodent", image="npc/undead_rodent_vampire_rat.png"},
	-- (the eternal bone giant was kept native here; batch V maps it as native-tall.)
	-- (the heavy bone giant was kept native here; batch W maps it as native-tall.)
	{name="bone giant", type="undead", subtype="giant", image="invis.png", add_mos={{image="npc/undead_giant_heavy_bone_giant.png", display_h=2, display_y=-1}}},
-- (the barrow wight was kept native here; batch AA maps it as native-tall.)
	-- emperor wight is now mapped by batch AE through its verified single-body tall contract.
	{name="forest wight", type="undead", subtype="wight", image="npc/grave_wight.png"},
	{name="grave wight", type="undead", subtype="wight", image="npc/forest_wight.png"},
	-- AG shadows use exact composite identities; stalker cannot borrow either.
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
	-- (the fire wyrm was kept native here; batch Z maps it as native-tall.)
	{name="fire drake hatchling", type="dragon", subtype="fire", image="npc/dragon_fire_fire_drake_hatchling.png"},
	{name="cold drake", type="dragon", subtype="cold", image="npc/dragon_cold_cold_drake.png"},
	{name="cold drake", type="dragon", subtype="cold", image="npc/dragon_cold_cold_drake_hatchling.png", define_as="NPC_COLD_DRAKE"},
	-- (the ice wyrm was kept native here; batch AD maps it as native-tall.)
	-- Storm wyrm is mapped by batch AE as a supported native tall body.
-- (the venom wyrm was kept native here; batch AB maps it as native-tall.)
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
	equal(Tokens.identify(a), nil, "a dire wolf body named war dog without WAR_DOG stays native (batch T maps the real one)")
	a = actor(dog)
	a.name = "war dog"
	equal(Tokens.identify(a), nil, "a war dog name with the corrupted dog's define_as stays native")
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
	-- (the orc master assassin was kept native here; batch U maps it.)
	{name="orc assassin", type="humanoid", subtype="orc", image="npc/humanoid_orc_orc_master_assassin.png"},
	-- (Rak'Shor Cultist was kept native here; batch UB-2 maps it.)
	{name="Rak'shor, Grand Necromancer of the Pride", type="humanoid", subtype="orc", image="npc/humanoid_orc_rak_shor__grand_necromancer_of_the_pride.png", unique=true},
	{name="Rak'shor, Grand Necromancer of the Pride", type="humanoid", subtype="orc", image="npc/humanoid_orc_rak_shor_cultist.png", define_as="RAK_SHOR", unique=true},
	{name="Warmaster Gnarg", type="humanoid", subtype="orc", image="npc/humanoid_orc_warmaster_gnarg.png", unique=true},
	{name="Warmaster Gnarg", type="humanoid", subtype="orc", image="npc/humanoid_orc_orc_soldier.png", define_as="GNARG", unique=true},
	{name="weaver young", type="spiderkin", subtype="spider", image="npc/spiderkin_spider_weaver_patriarch.png"},
	-- (the fate weaver was kept native here; batch U maps it.)
	{name="fate spinner", type="spiderkin", subtype="spider", image="npc/spiderkin_spider_fate_weaver.png"},
	-- (the giant fire ant was kept native here; batch W maps it.)
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
	for _, id in ipairs({"wolf", "ghoul", "carrion-worm-mass", "prox", "high-sun-paladin-rodmour"}) do
		local entry = Tokens.by_id[id]
		local a = actor(entry)
		a.summoner, a.wild_gift_summon = {faction="players"}, true
		a.name = entry.name.." (wild summon)"
		equal(Tokens.identify(a), nil, "wild-summon suffix is not accepted for "..id)
	end
	-- A partial animal/spider shape (no gift fields) stays native; the full real summon is covered by the summon-alias block at the end.
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
		for _, other in ipairs({"wolf", "ghoul", "prox"}) do
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
	{name="Unknown Warg Titan", type="animal", subtype="canine", image="npc/canine_rungof.png", unique=true},
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

-- Batch T: the remaining 12.0-tier story identities (caravan merchant, guard and
-- porter, Lost Merchant, Nimisil, Slasul, Draebor, war dog, Yeek Wayist, Weirdling
-- Beast, Fortress Shadow, Pumpkin). Every define_as is bound. Slasul is a UNIQUE
-- native-tall body (no native_tall flag); the Weirdling Beast opts into
-- urh_rok_form (Corruptor auto_class); Training Dummy stays native.
local batch_t = {"caravan-merchant", "caravan-guard", "caravan-porter", "lost-merchant", "war-dog", "yeek-wayist",
	"nimisil", "slasul", "draebor", "weirdling-beast", "fortress-shadow", "pumpkin"}
local define_t = {["caravan-merchant"]="CARAVAN_MERCHANT", ["caravan-guard"]="CARAVAN_GUARD", ["caravan-porter"]="CARAVAN_PORTER",
	["lost-merchant"]="MERCHANT", ["war-dog"]="WAR_DOG", ["yeek-wayist"]="YEEK_WAYIST", nimisil="NIMISIL", slasul="SLASUL",
	draebor="DRAEBOR", ["weirdling-beast"]="WEIRDLING_BEAST", ["fortress-shadow"]="BUTLER", pumpkin="KITTY"}
local unique_t = {["yeek-wayist"]=true, nimisil=true, slasul=true, draebor=true, ["weirdling-beast"]=true, pumpkin=true}
for _, id in ipairs(batch_t) do
	local entry = Tokens.by_id[id]
	if entry == nil then error("batch T catalog entry missing: "..id) end
	equal(entry.define_as, define_t[id], "batch T define_as "..id)
	equal(entry.unique, unique_t[id] and true or nil, "batch T unique flag "..id)
	equal(entry.native_tall, nil, "batch T no native_tall flag "..id)
	equal(entry.urh_rok_form, id == "weirdling-beast" and true or nil, "batch T urh_rok_form flag "..id)
	equal(Tokens.identify(actor(entry)), id, "batch T exact identity "..id)
	local a = actor(entry)
	a.tint_r, a.tint_g, a.tint_b = 0.5, 0.9, 0.3
	equal(Tokens.identify(a), id, "batch T tint is colour only "..id)
	a = actor(entry)
	a.color_r, a.color_g, a.color_b = 0, 0, 185
	equal(Tokens.identify(a), id, "batch T colour modulation keeps the token "..id)
	a = actor(entry)
	a.image = "invis.png"
	a.add_mos = {{image=entry.image, display_h=2, display_y=-1}}
	if entry.unique then
		equal(Tokens.identify(a), id, "batch T unique tall body accepted "..id)
	else
		equal(Tokens.identify(a), nil, "batch T non-unique single entry rejects a tall body "..id)
	end
	a = actor(entry)
	a.type = entry.type == "animal" and "humanoid" or "animal"
	equal(Tokens.identify(a), nil, "batch T type changed "..id)
	a = actor(entry)
	a.subtype = "other-subtype"
	equal(Tokens.identify(a), nil, "batch T subtype changed "..id)
	a = actor(entry)
	a.shader = "some_shader"
	equal(Tokens.identify(a), nil, "batch T shader keeps native art "..id)
	a = actor(entry)
	a.moddable_tile = "some_doll"
	equal(Tokens.identify(a), nil, "batch T paper-doll actor keeps native art "..id)
	a = actor(entry)
	a.add_displays = {{image="npc/iceblock.png"}}
	equal(Tokens.identify(a), nil, "batch T frozen/pinned add_displays keep native art "..id)
	if not entry.unique then
		a = actor(entry)
		a.unique = true
		equal(Tokens.identify(a), nil, "batch T non-unique entry rejects an unknown unique "..id)
	end
	a = actor(entry)
	a.define_as = "OTHER_"..define_t[id]
	equal(Tokens.identify(a), nil, "batch T define_as bound "..id)
	a = actor(entry)
	a.define_as = nil
	equal(Tokens.identify(a), nil, "batch T missing define_as "..id)
	a = actor(entry)
	a.image = "npc/some_other_image.png"
	equal(Tokens.identify(a), nil, "batch T other image keeps native art "..id)
	a = actor(entry)
	a.__old_type = {entry.type, entry.subtype}
	a.type, a.subtype = "demon", "major"
	a.sustain_talents = {T_FLAME_OF_URH_ROK = {}}
	equal(Tokens.identify(a), entry.urh_rok_form and id or nil, "batch T Flame of Urh'Rok form only for opted-in "..id)
	a = actor(entry)
	a.add_mos = {{_isshaderaura=true, image="shockbolt/aura.png"}}
	equal(Tokens.identify(a), id, "batch T shader aura entry is ignored "..id)
end
-- The three caravan people, on distinct explicit PNGs, cannot borrow each other.
for _, id in ipairs({"caravan-merchant", "caravan-guard", "caravan-porter"}) do
	for _, other in ipairs({"caravan-merchant", "caravan-guard", "caravan-porter"}) do
		if id ~= other then
			local a = actor(Tokens.by_id[id])
			a.image = Tokens.by_id[other].image
			equal(Tokens.identify(a), nil, "batch T caravan sibling cannot borrow image "..id.." <- "..other)
			a = actor(Tokens.by_id[id])
			a.name, a.define_as = Tokens.by_id[other].name, Tokens.by_id[other].define_as
			equal(Tokens.identify(a), nil, "batch T caravan body cannot wear another entry "..id.." as "..other)
		end
	end
end
do
	-- The war dog shares canine_dw.png with the dire wolf and the corrupted war dog.
	local war, cdog, wolf = Tokens.by_id["war-dog"], Tokens.by_id["corrupted-war-dog"], Tokens.by_id["dire-wolf"]
	equal(war.image, cdog.image, "the war dog and the corrupted war dog share one native PNG")
	equal(war.image, wolf.image, "the war dog and the dire wolf share one native PNG")
	local a = actor(cdog); a.name = "war dog"
	equal(Tokens.identify(a), nil, "a corrupted war dog body (its define_as) named war dog stays native")
	a = actor(wolf); a.name, a.define_as = "war dog", nil
	equal(Tokens.identify(a), nil, "a dire wolf body renamed war dog without WAR_DOG stays native")
	a = actor(war); a.name, a.define_as = "dire wolf", nil
	equal(Tokens.identify(a), "dire-wolf", "a dire wolf body resolves to the dire wolf token")
	a = actor(war); a.name = "dire wolf"
	equal(Tokens.identify(a), nil, "a dire wolf name carrying WAR_DOG stays native")
	a = actor(war); a.name = "corrupted war dog"
	equal(Tokens.identify(a), nil, "a corrupted war dog name carrying WAR_DOG stays native")
	a = actor(cdog)
	equal(Tokens.identify(a), "corrupted-war-dog", "the corrupted war dog keeps its own token")
end
do
	local shadow = Tokens.by_id["fortress-shadow"]
	equal(shadow.subtype, "Sher'Tul", "the Fortress Shadow subtype is the exact native string")
	for _, subtype in ipairs({"sher'tul", "Sher Tul", "sher_tul", "SHER'TUL", "Sher'tul", "eldritch"}) do
		local a = actor(shadow); a.subtype = subtype
		equal(Tokens.identify(a), nil, "Fortress Shadow subtype "..subtype.." stays native")
	end
	local a = actor(Tokens.by_id["weirdling-beast"]); a.subtype = "Sher'Tul"
	equal(Tokens.identify(a), nil, "the Weirdling Beast cannot become a Sher'Tul body")
	a = actor(Tokens.by_id["pumpkin"]); a.name = "Lost Kitty"; a.define_as, a.unique = nil, nil
	equal(Tokens.identify(a), nil, "the Lost Kitty encounter (another name, same PNG) stays native")
	local slasul = actor(Tokens.by_id["slasul"])
	slasul.image = "invis.png"
	slasul.add_mos = {{image="npc/humanoid_naga_slasul.png", display_h=2, display_y=-1}, {image="npc/other.png"}}
	equal(Tokens.identify(slasul), nil, "Slasul with an extra chained overlay keeps native art")
	slasul.add_mos = {{image="npc/humanoid_naga_slasul.png", display_h=3, display_y=-1}}
	equal(Tokens.identify(slasul), nil, "Slasul with an altered tall body keeps native art")
end
for _, excluded in ipairs({
	{name="Training Dummy", type="training", subtype="dummy", image="npc/lure.png", define_as="TRAINING_DUMMY"},
	{name="Training Dummy", type="training", subtype="dummy", image="npc/lure.png"},
	{name="Lost Merchant", type="humanoid", subtype="human", image="npc/humanoid_human_lost_merchant.png", define_as="MERCHANT", unique=true, faction="victim"},
	{name="Yeek Wayist", type="humanoid", subtype="yeek", image="npc/humanoid_yeek_yeek_wayist.png", unique=true},
	{name="Nimisil", type="spiderkin", subtype="spider", image="npc/spiderkin_spider_nimisil.png", unique=true},
	{name="shadow claw", type="undead", subtype="shadow", image="npc/humanoid_human_spectator02.png", define_as="SHADOW_CLAW"},
}) do
	equal(Tokens.identify(excluded), nil, "batch T look-alike stays native "..excluded.name.." "..tostring(excluded.define_as))
end

-- Batch U: the twelve identities after the finished 12.0 tier (naga tide
-- huntress, ancient elven mummy, ritch flamespitter, chitinous ritch, gaeramarth,
-- ninurlhing, orc master assassin, fire imp, ritch impaler, orc grand master
-- assassin, naga psyren, fate weaver). All are non-unique 64x64 single images
-- WITHOUT a define_as (matched by exact name, type and subtype); nothing is
-- native-tall and none can reach Flame of Urh'Rok, so there is no opt-in.
local batch_u = {"ritch-flamespitter", "ritch-impaler", "chitinous-ritch", "naga-tide-huntress", "naga-psyren",
	"ancient-elven-mummy", "orc-master-assassin", "orc-grand-master-assassin", "fire-imp", "gaeramarth", "ninurlhing",
	"fate-weaver"}
local names_u = {["ritch-flamespitter"]="ritch flamespitter", ["ritch-impaler"]="ritch impaler", ["chitinous-ritch"]="chitinous ritch",
	["naga-tide-huntress"]="naga tide huntress", ["naga-psyren"]="naga psyren", ["ancient-elven-mummy"]="ancient elven mummy",
	["orc-master-assassin"]="orc master assassin", ["orc-grand-master-assassin"]="orc grand master assassin", ["fire-imp"]="fire imp",
	gaeramarth="gaeramarth", ninurlhing="ninurlhing", ["fate-weaver"]="fate weaver"}
for _, id in ipairs(batch_u) do
	local entry = Tokens.by_id[id]
	if entry == nil then error("batch U catalog entry missing: "..id) end
	equal(entry.name, names_u[id], "batch U exact name "..id)
	equal(entry.define_as, nil, "batch U define_as-less "..id)
	equal(entry.unique, nil, "batch U non-unique "..id)
	equal(entry.native_tall, nil, "batch U no native_tall flag "..id)
	equal(entry.urh_rok_form, nil, "batch U no urh_rok_form flag "..id)
	equal(Tokens.identify(actor(entry)), id, "batch U exact identity "..id)
	local a = actor(entry)
	a.tint_r, a.tint_g, a.tint_b = 0.5, 0.9, 0.3
	equal(Tokens.identify(a), id, "batch U tint is colour only "..id)
	a = actor(entry)
	a.color_r, a.color_g, a.color_b = 0, 0, 185
	equal(Tokens.identify(a), id, "batch U colour modulation keeps the token "..id)
	a = actor(entry)
	a.image = "invis.png"
	a.add_mos = {{image=entry.image, display_h=2, display_y=-1}}
	equal(Tokens.identify(a), nil, "batch U single entry rejects a tall body "..id)
	a = actor(entry)
	a.type = entry.type == "undead" and "humanoid" or "undead"
	equal(Tokens.identify(a), nil, "batch U type changed "..id)
	a = actor(entry)
	a.subtype = "other-subtype"
	equal(Tokens.identify(a), nil, "batch U subtype changed "..id)
	a = actor(entry)
	a.shader = "some_shader"
	equal(Tokens.identify(a), nil, "batch U shader keeps native art "..id)
	a = actor(entry)
	a.moddable_tile = "some_doll"
	equal(Tokens.identify(a), nil, "batch U paper-doll actor keeps native art "..id)
	a = actor(entry)
	a.add_displays = {{image="npc/iceblock.png"}}
	equal(Tokens.identify(a), nil, "batch U frozen/pinned add_displays keep native art "..id)
	a = actor(entry)
	a.unique = true
	equal(Tokens.identify(a), nil, "batch U non-unique entry rejects an unknown unique "..id)
	a = actor(entry)
	a.define_as = "SOME_DEFINE_AS"
	equal(Tokens.identify(a), nil, "batch U unexpected define_as "..id)
	a = actor(entry)
	a.image = "npc/some_other_image.png"
	equal(Tokens.identify(a), nil, "batch U other image keeps native art "..id)
	a = actor(entry)
	a.__old_type = {entry.type, entry.subtype}
	a.type, a.subtype = "demon", "major"
	a.sustain_talents = {T_FLAME_OF_URH_ROK = {}}
	equal(Tokens.identify(a), nil, "batch U Flame of Urh'Rok form is not supported "..id)
	a = actor(entry)
	a.add_mos = {{_isshaderaura=true, image="shockbolt/aura.png"}}
	equal(Tokens.identify(a), id, "batch U shader aura entry is ignored "..id)
	-- A summon shape (summoner table, summoned AI) never borrows a zone leaf's token
	-- through a variant: none of these entries has a variants function.
	a = actor(entry)
	a.summoner, a.ai, a.wild_gift_summon = {}, "summoned", true
	equal(Tokens.identify(a), id, "batch U a same-body summon is still the same exact leaf "..id)
	a.define_as = nil
	a.name = entry.name.." (wild summon)"
	equal(Tokens.identify(a), id == "ritch-flamespitter" and id or nil, "batch U the wild-summon rename is covered only for the ritch flamespitter "..id)
end
-- Birth sustains are temporary values, callbacks and particles only.
for id, talents in pairs({
	["orc-master-assassin"]={"T_STEALTH", "T_APPLY_POISON"},
	["orc-grand-master-assassin"]={"T_STEALTH", "T_APPLY_POISON"},
	gaeramarth={"T_STEALTH"},
	ninurlhing={"T_ACIDIC_SKIN"},
}) do
	local a = actor(Tokens.by_id[id])
	a.sustain_talents = {}
	for _, tid in ipairs(talents) do a.sustain_talents[tid] = {} end
	a.__particles = {{}}
	a.resists = {COLD=50}
	equal(Tokens.identify(a), id, "batch U birth sustain keeps the body "..id)
end
-- The three ritches, two nagas, two orc assassins and three spiders cannot borrow each other.
for _, group in ipairs({{"ritch-flamespitter", "ritch-impaler", "chitinous-ritch"}, {"naga-tide-huntress", "naga-psyren"},
	{"orc-master-assassin", "orc-grand-master-assassin"}, {"gaeramarth", "ninurlhing", "fate-weaver"}}) do
	for _, id in ipairs(group) do
		for _, other in ipairs(group) do
			if id ~= other then
				local a = actor(Tokens.by_id[id])
				a.image = Tokens.by_id[other].image
				equal(Tokens.identify(a), nil, "batch U sibling cannot borrow image "..id.." <- "..other)
				a = actor(Tokens.by_id[id])
				a.name = Tokens.by_id[other].name
				equal(Tokens.identify(a), nil, "batch U body cannot wear another sibling's name "..id.." as "..other)
			end
		end
	end
end
do
	-- The Wild Gift Ritch Flamespitter summon (talents/gifts/summon-distance.lua:446) has the same
	-- name and type but image npc/summoner_ritch.png. It wears the flamespitter token through the
	-- per-entry image alias, and only when every distinctive constructor field is present.
	local flame = Tokens.by_id["ritch-flamespitter"]
	local function summon(f)
		local m = {name="ritch flamespitter", type="insect", subtype="ritch", image="npc/summoner_ritch.png", summoner={}, ai="summoned",
			wild_gift_summon=true, summoner_gain_exp=true, is_nature_summon=true, wild_gift_detonate="T_RITCH_FLAMESPITTER", faction="enemies"}
		if f then f(m) end
		return m
	end
	equal(Tokens.identify(summon()), "ritch-flamespitter", "the Ritch Flamespitter summon wears the flamespitter token")
	equal(Tokens.identify(summon(function(m) m.name = "ritch flamespitter (wild summon)" end)), "ritch-flamespitter", "the English wild-summon Ritch Flamespitter wears the token")
	equal(Tokens.identify(summon(function(m) m.ai, m.ai_state = "party_member", {ai_party="summoned"} end)), "ritch-flamespitter", "a party-converted Ritch Flamespitter summon wears the token")
	equal(Tokens.identify(summon(function(m) m.add_mos = {{_isshaderaura=true, image="shockbolt/aura.png"}} end)), "ritch-flamespitter", "shader aura bookkeeping on the summon is ignored")
	equal(Tokens.identify(summon(function(m) m.name = "ritch flamespitter (wild summon) (wild summon)" end)), nil, "doubled wild-summon suffix stays native")
	equal(Tokens.identify(summon(function(m) m.name = "(wild summon) ritch flamespitter" end)), nil, "prefix wild-summon form stays native")
	-- Negatives: the alias image never works outside that exact constructor.
	for label, f in pairs({
		["not a summon (no summoner)"] = function(m) m.summoner = nil end,
		["summoner not a table"] = function(m) m.summoner = true end,
		["not summoned AI"] = function(m) m.ai = "tactical" end,
		["no wild_gift_summon"] = function(m) m.wild_gift_summon = nil end,
		["no summoner_gain_exp"] = function(m) m.summoner_gain_exp = nil end,
		["no is_nature_summon"] = function(m) m.is_nature_summon = nil end,
		["another gift's detonate id"] = function(m) m.wild_gift_detonate = "T_FIRE_DRAKE" end,
		["missing detonate id"] = function(m) m.wild_gift_detonate = nil end,
		["unique"] = function(m) m.unique = true end,
		["define_as"] = function(m) m.define_as = "RITCH_SUMMON" end,
		["extra add_mos"] = function(m) m.add_mos = {{image="npc/other.png"}} end,
		["shader"] = function(m) m.shader = "some_shader" end,
		["moddable_tile"] = function(m) m.moddable_tile = "some_doll" end,
		["add_displays"] = function(m) m.add_displays = {{image="npc/iceblock.png"}} end,
		["animation"] = function(m) m.anim = {} end,
		["subtype changed"] = function(m) m.subtype = "other-subtype" end,
		["type changed"] = function(m) m.type = "animal" end,
		["other name"] = function(m) m.name = "ritch impaler" end,
		["other image"] = function(m) m.image = "npc/summoner_hydra.png" end,
		["tall body carrying the alias"] = function(m) m.image, m.add_mos = "invis.png", {{image="npc/summoner_ritch.png", display_h=2, display_y=-1}} end,
	}) do
		equal(Tokens.identify(summon(f)), nil, "ritch summon alias negative: "..label)
	end
	-- A plain (non-summon) actor named ritch flamespitter on the alias PNG is not the zone leaf.
	equal(Tokens.identify({name="ritch flamespitter", type="insect", subtype="ritch", image="npc/summoner_ritch.png", faction="enemies"}), nil,
		"the alias PNG on a non-summon actor stays native")
	-- The alias never lets another entry borrow summoner_ritch.png, and it grants nothing else.
	for _, id in ipairs({"ritch-impaler", "chitinous-ritch", "ritch-hive-mother", "fire-imp", "naga-psyren"}) do
		local entry = Tokens.by_id[id]
		local m = summon(function(m) m.name, m.type, m.subtype = entry.name, entry.type, entry.subtype
			m.define_as, m.unique = entry.define_as, entry.unique and true or nil end)
		equal(Tokens.identify(m), nil, "another entry cannot borrow summoner_ritch.png: "..id)
	end
	local a = actor(flame)
	a.image = "npc/summoner_ritch.png"
	equal(Tokens.identify(a), nil, "a zone-style leaf drawn with the summon PNG (no summon fields) stays native")
	-- Other summon PNGs of native constructors are not aliased.
	for _, png in ipairs({"npc/summoner_wardog.png", "npc/summoner_golem.png", "npc/summoner_turtle.png", "npc/summoner_hydra.png"}) do
		local m = summon(function(m) m.image = png end)
		equal(Tokens.identify(m), nil, "unrelated summoner PNG is not an alias: "..png)
	end
end
-- Look-alikes stay native (tutorial hairy spider on the ninurlhing PNG, other names on the same PNG).
for _, excluded in ipairs({
	{name="hairy spider", type="spiderkin", subtype="spider", image="npc/spiderkin_spider_ninurlhing.png", define_as="TUT_SPIDER_3"},
	{name="ritch hunter", type="insect", subtype="ritch", image="npc/insect_ritch_ritch_impaler.png"},
	{name="ritch impaler", type="insect", subtype="ritch", image="npc/insect_ritch_ritch_flamespitter.png"},
	{name="chitinous spider", type="spiderkin", subtype="spider", image="npc/spiderkin_spider_gaeramarth.png"},
	{name="naga myrmidon", type="humanoid", subtype="naga", image="npc/naga_psyren.png"},
	{name="Greater Mummy Lord", type="undead", subtype="mummy", image="npc/undead_mummy_ancient_elven_mummy.png"},
	{name="rotting mummy", type="undead", subtype="mummy", image="npc/undead_mummy_ancient_elven_mummy.png"},
	{name="orc assassin", type="humanoid", subtype="orc", image="npc/humanoid_orc_orc_grand_master_assassin.png"},
	{name="orc master assassin", type="humanoid", subtype="orc", image="npc/humanoid_orc_orc_grand_master_assassin.png"},
	{name="fire imp", type="demon", subtype="major", image="npc/demon_minor_fire_imp.png"},
	{name="imp", type="demon", subtype="minor", image="npc/demon_minor_fire_imp.png"},
}) do
	equal(Tokens.identify(excluded), nil, "batch U look-alike stays native "..excluded.name.." "..tostring(excluded.define_as))
end

-- Batch V: the twelve identities after batch U (black crystal, faerlhing,
-- losselhing, dredge, dolleg, eternal bone giant, drem master, orc pyromancer,
-- orc cryomancer, bloated horror, yaech hunter, orc blood mage). All are
-- non-unique and WITHOUT a define_as (exact name, type and subtype). Dolleg and
-- the eternal bone giant are native-tall (native_tall=true); none can reach
-- Flame of Urh'Rok, so there is no opt-in.
local batch_v = {"black-crystal", "faerlhing", "losselhing", "dredge", "dolleg", "eternal-bone-giant", "drem-master",
	"orc-pyromancer", "orc-cryomancer", "bloated-horror", "yaech-hunter", "orc-blood-mage"}
local names_v = {["black-crystal"]="black crystal", faerlhing="faerlhing", losselhing="losselhing", dredge="dredge",
	dolleg="dolleg", ["eternal-bone-giant"]="eternal bone giant", ["drem-master"]="drem master", ["orc-pyromancer"]="orc pyromancer",
	["orc-cryomancer"]="orc cryomancer", ["bloated-horror"]="bloated horror", ["yaech-hunter"]="yaech hunter", ["orc-blood-mage"]="orc blood mage"}
local tall_v = {dolleg=true, ["eternal-bone-giant"]=true}
for _, id in ipairs(batch_v) do
	local entry = Tokens.by_id[id]
	if entry == nil then error("batch V catalog entry missing: "..id) end
	equal(entry.name, names_v[id], "batch V exact name "..id)
	equal(entry.define_as, nil, "batch V define_as-less "..id)
	equal(entry.unique, nil, "batch V non-unique "..id)
	equal(entry.native_tall, tall_v[id] and true or nil, "batch V native_tall flag "..id)
	equal(entry.urh_rok_form, nil, "batch V no urh_rok_form flag "..id)
	equal(Tokens.identify(actor(entry)), id, "batch V exact identity "..id)
	local a = actor(entry)
	a.tint_r, a.tint_g, a.tint_b = 0, 0, 0
	equal(Tokens.identify(a), id, "batch V tint is colour only "..id)
	a = actor(entry)
	a.color_r, a.color_g, a.color_b = 0, 0, 185
	equal(Tokens.identify(a), id, "batch V colour modulation keeps the token "..id)
	a = actor(entry)
	a.image = "invis.png"
	a.add_mos = {{image=entry.image, display_h=2, display_y=-1}}
	equal(Tokens.identify(a), tall_v[id] and id or nil, "batch V tall body accepted only for native_tall entries "..id)
	if tall_v[id] then
		a.add_mos = {{image=entry.image, display_h=2, display_y=-1}, {image="npc/other.png"}}
		equal(Tokens.identify(a), nil, "batch V tall body with a second overlay stays native "..id)
		a.add_mos = {{image="npc/other.png", display_h=2, display_y=-1}}
		equal(Tokens.identify(a), nil, "batch V tall body naming another PNG stays native "..id)
		a.add_mos = {{image=entry.image, display_h=2, display_y=-1, shader="x"}}
		equal(Tokens.identify(a), nil, "batch V tall body with extra keys stays native "..id)
		a.add_mos = {{image=entry.image, display_h=3, display_y=-1}}
		equal(Tokens.identify(a), nil, "batch V tall body with other dimensions stays native "..id)
		a.add_mos = {{image=entry.image, display_h=2, display_y=-1}, {_isshaderaura=true, image="shockbolt/aura.png"}}
		equal(Tokens.identify(a), id, "batch V tall body with shader aura bookkeeping "..id)
	end
	a = actor(entry)
	a.type = entry.type == "undead" and "humanoid" or "undead"
	equal(Tokens.identify(a), nil, "batch V type changed "..id)
	a = actor(entry)
	a.subtype = "other-subtype"
	equal(Tokens.identify(a), nil, "batch V subtype changed "..id)
	a = actor(entry)
	a.shader = "some_shader"
	equal(Tokens.identify(a), nil, "batch V shader keeps native art "..id)
	a = actor(entry)
	a.moddable_tile = "some_doll"
	equal(Tokens.identify(a), nil, "batch V paper-doll actor keeps native art "..id)
	a = actor(entry)
	a.anim = {}
	equal(Tokens.identify(a), nil, "batch V animation keeps native art "..id)
	a = actor(entry)
	a.add_displays = {{image="npc/iceblock.png"}}
	equal(Tokens.identify(a), nil, "batch V frozen/pinned add_displays keep native art "..id)
	a = actor(entry)
	a.unique = true
	equal(Tokens.identify(a), nil, "batch V non-unique entry rejects an unknown unique "..id)
	a = actor(entry)
	a.define_as = "SOME_DEFINE_AS"
	equal(Tokens.identify(a), nil, "batch V unexpected define_as "..id)
	a = actor(entry)
	a.image = "npc/some_other_image.png"
	equal(Tokens.identify(a), nil, "batch V other image keeps native art "..id)
	a = actor(entry)
	a.__old_type = {entry.type, entry.subtype}
	a.type, a.subtype = "demon", "major"
	a.sustain_talents = {T_FLAME_OF_URH_ROK = {}}
	-- (the dolleg is itself demon/major, so the shape is just its own body)
	equal(Tokens.identify(a), id == "dolleg" and "dolleg" or nil, "batch V Flame of Urh'Rok form is not supported "..id)
	a = actor(entry)
	a.add_mos = {{_isshaderaura=true, image="shockbolt/aura.png"}}
	equal(Tokens.identify(a), id, "batch V shader aura entry is ignored "..id)
	-- No variants or aliases: a summon shape carrying a wild-summon rename or another PNG stays native.
	a = actor(entry)
	a.summoner, a.ai, a.wild_gift_summon = {}, "summoned", true
	equal(Tokens.identify(a), id, "batch V a same-body summon is the same exact leaf "..id)
	a.name = entry.name.." (wild summon)"
	equal(Tokens.identify(a), nil, "batch V the wild-summon rename is not covered "..id)
	a = actor(entry)
	a.summoner, a.ai, a.summoner_gain_exp, a.wild_gift_summon = {}, "summoned", true, true
	a.image = "npc/summoner_ritch.png"
	equal(Tokens.identify(a), nil, "batch V no summon PNG alias "..id)
end
-- Birth sustains are temporary values, shields and particles only.
for id, talents in pairs({
	faerlhing={"T_PHANTASMAL_SHIELD", "T_DISRUPTION_SHIELD", "T_ARCANE_POWER"},
	losselhing={"T_ICY_SKIN", "T_FROST_HANDS"},
	["orc-pyromancer"]={"T_SPELLCRAFT"},
	["orc-cryomancer"]={"T_SPELLCRAFT"},
	dolleg={"T_ACIDIC_SKIN"},
}) do
	local entry = Tokens.by_id[id]
	local a = actor(entry)
	if tall_v[id] then a.image = "invis.png"; a.add_mos = {{image=entry.image, display_h=2, display_y=-1}} end
	a.sustain_talents = {}
	for _, tid in ipairs(talents) do a.sustain_talents[tid] = {} end
	a.__particles = {{}}
	a.resists = {COLD=50}
	equal(Tokens.identify(a), id, "batch V birth sustain keeps the body "..id)
end
-- Necromancer Assemble minion (talents/spells/master-of-bones.lua:393): same name, body and nice_tile, no
-- define_as, so it wears the eternal bone giant token by the ordinary key; a Lord of Skulls renames it.
do
	local entry = Tokens.by_id["eternal-bone-giant"]
	local a = actor(entry)
	a.image, a.add_mos = "invis.png", {{image=entry.image, display_h=2, display_y=-1}}
	a.faction, a.summoner, a.summon_time = "players", {faction="players"}, 7
	a.necrotic_minion, a.summoner_gain_exp, a.is_bone_giant = true, true, "e_bone_giant"
	equal(Tokens.identify(a), "eternal-bone-giant", "batch V Assemble minion is the same body as the eternal bone giant")
	a.name = "Lord of Skulls (bone giant)"
	equal(Tokens.identify(a), nil, "batch V Lord of Skulls minion is renamed and stays native")
	a = actor(entry)
	-- (the heavy bone giant stayed native here; batch W maps it and tests the Assemble minion.)
	a = actor(Tokens.by_id["bone-giant"])
	a.image, a.add_mos = "invis.png", {{image=entry.image, display_h=2, display_y=-1}}
	equal(Tokens.identify(a), nil, "batch V a bone giant cannot wear the eternal bone giant body")
	-- A random boss made from a non-unique native-tall body keeps native art (only unique tall bodies qualify).
	for _, id in ipairs({"dolleg", "eternal-bone-giant"}) do
		local e = Tokens.by_id[id]
		local base = actor(e)
		base.image, base.add_mos = "invis.png", {{image=e.image, display_h=2, display_y=-1}}
		local capture = Tokens.captureRandomOrigin(base)
		local boss = actor(e)
		boss.image, boss.add_mos = "invis.png", {{image=e.image, display_h=2, display_y=-1}}
		boss.name, boss.define_as, boss.unique, boss.randboss = "Inquisitor Test", "RANDOM_BOSS_V", "Inquisitor Test", true
		equal(Tokens.recordRandomOrigin(boss, capture, "RANDOM_BOSS_V"), nil, "batch V non-unique tall random boss stays native "..id)
		equal(Tokens.identify(boss), nil, "batch V non-unique tall random boss identify "..id)
	end
end
-- The three spiders/crystal, three horrors, three orc casters and giant/demon/yaech cannot borrow each other.
for _, group in ipairs({{"black-crystal", "faerlhing", "losselhing"}, {"dredge", "drem-master", "bloated-horror"},
	{"orc-pyromancer", "orc-cryomancer", "orc-blood-mage"}, {"dolleg", "eternal-bone-giant", "yaech-hunter"},
	{"faerlhing", "losselhing", "gaeramarth", "ninurlhing", "fate-weaver"}, {"dredge", "dredgling"}, {"orc-pyromancer", "orc-necromancer", "orc-master-assassin"},
	{"eternal-bone-giant", "bone-giant", "half-finished-bone-giant"}}) do
	for _, id in ipairs(group) do
		for _, other in ipairs(group) do
			if id ~= other and Tokens.by_id[id] and Tokens.by_id[other] then
				local a = actor(Tokens.by_id[id])
				a.image = Tokens.by_id[other].image
				equal(Tokens.identify(a), nil, "batch V sibling cannot borrow image "..id.." <- "..other)
				a = actor(Tokens.by_id[id])
				a.name = Tokens.by_id[other].name
				equal(Tokens.identify(a), nil, "batch V body cannot wear another sibling's name "..id.." as "..other)
			end
		end
	end
end
-- Look-alikes stay native (dreams "lost wife" with subtype bloated horror, other names on the same PNGs).
for _, excluded in ipairs({
	{name="lost wife", type="humanoid", subtype="bloated horror", image="invis.png", define_as="WIFE", add_mos={{image="npc/humanoid_orc_orc_mother.png", display_h=2, display_y=-1}}},
	{name="bloated horror", type="humanoid", subtype="bloated horror", image="npc/horror_eldritch_bloated_horror.png"},
	{name="dredge captain", type="horror", subtype="temporal", image="npc/horror_temporal_dredge.png"},
	{name="dredge", type="horror", subtype="temporal", image="npc/horror_temporal_dredge_captain.png"},
	{name="drem", type="horror", subtype="corrupted", image="npc/horror_corrupted_drem_master.png"},
	{name="orc high pyromancer", type="humanoid", subtype="orc", image="npc/humanoid_orc_orc_pyromancer.png"},
	{name="orc high cryomancer", type="humanoid", subtype="orc", image="npc/humanoid_orc_orc_cryomancer.png"},
	{name="orc corruptor", type="humanoid", subtype="orc", image="npc/humanoid_orc_orc_blood_mage.png"},
	{name="yaech diver", type="humanoid", subtype="yaech", image="npc/humanoid_yaech_yaech_hunter.png"},
	{name="yaech mindslayer", type="humanoid", subtype="yaech", image="npc/humanoid_yaech_yaech_hunter.png"},
	{name="blue crystal", type="immovable", subtype="crystal", image="npc/crystal_black.png"},
	{name="black crystal", type="immovable", subtype="crystal", image="npc/crystal_blue.png"},
	{name="dolleg", type="demon", subtype="minor", image="invis.png", add_mos={{image="npc/demon_major_dolleg.png", display_h=2, display_y=-1}}},
	{name="uruivellas", type="demon", subtype="major", image="invis.png", add_mos={{image="npc/demon_major_dolleg.png", display_h=2, display_y=-1}}},
	{name="losselhing", type="spiderkin", subtype="spider", image="npc/spiderkin_spider_faerlhing.png"},
}) do
	equal(Tokens.identify(excluded), nil, "batch V look-alike stays native "..excluded.name.." "..tostring(excluded.define_as))
end

-- Batch W: the twelve identities after batch V (fiery/icy orc wyrmic, yaech
-- mindslayer, heavy bone giant, cave bear, war bear, grannor'vin, rotting
-- mummy, banshee, giant fire/ice/lightning ant). All are non-unique. The two
-- orc wyrmics bind their define_as (ORC_FIRE_WYRMIC, ORC_ICE_WYRMIC); the other
-- ten have none. The heavy bone giant is native-tall (native_tall=true); none
-- can reach Flame of Urh'Rok, so there is no opt-in.
local batch_w = {"fiery-orc-wyrmic", "icy-orc-wyrmic", "yaech-mindslayer", "heavy-bone-giant", "cave-bear", "war-bear",
	"grannor-vin", "rotting-mummy", "banshee", "giant-fire-ant", "giant-ice-ant", "giant-lightning-ant"}
local names_w = {["fiery-orc-wyrmic"]="fiery orc wyrmic", ["icy-orc-wyrmic"]="icy orc wyrmic", ["yaech-mindslayer"]="yaech mindslayer",
	["heavy-bone-giant"]="heavy bone giant", ["cave-bear"]="cave bear", ["war-bear"]="war bear", ["grannor-vin"]="grannor'vin",
	["rotting-mummy"]="rotting mummy", banshee="banshee", ["giant-fire-ant"]="giant fire ant", ["giant-ice-ant"]="giant ice ant",
	["giant-lightning-ant"]="giant lightning ant"}
local defines_w = {["fiery-orc-wyrmic"]="ORC_FIRE_WYRMIC", ["icy-orc-wyrmic"]="ORC_ICE_WYRMIC"}
local tall_w = {["heavy-bone-giant"]=true}
for _, id in ipairs(batch_w) do
	local entry = Tokens.by_id[id]
	if entry == nil then error("batch W catalog entry missing: "..id) end
	equal(entry.name, names_w[id], "batch W exact name "..id)
	equal(entry.define_as, defines_w[id], "batch W define_as binding "..id)
	equal(entry.unique, nil, "batch W non-unique "..id)
	equal(entry.native_tall, tall_w[id] and true or nil, "batch W native_tall flag "..id)
	equal(entry.urh_rok_form, nil, "batch W no urh_rok_form flag "..id)
	equal(Tokens.identify(actor(entry)), id, "batch W exact identity "..id)
	local a = actor(entry)
	a.tint_r, a.tint_g, a.tint_b = 0, 0, 0
	equal(Tokens.identify(a), id, "batch W tint is colour only "..id)
	a = actor(entry)
	a.color_r, a.color_g, a.color_b = 0, 0, 185
	equal(Tokens.identify(a), id, "batch W colour modulation keeps the token "..id)
	a = actor(entry)
	a.image = "invis.png"
	a.add_mos = {{image=entry.image, display_h=2, display_y=-1}}
	equal(Tokens.identify(a), tall_w[id] and id or nil, "batch W tall body accepted only for native_tall entries "..id)
	if tall_w[id] then
		a.add_mos = {{image=entry.image, display_h=2, display_y=-1}, {image="npc/other.png"}}
		equal(Tokens.identify(a), nil, "batch W tall body with a second overlay stays native "..id)
		a.add_mos = {{image="npc/other.png", display_h=2, display_y=-1}}
		equal(Tokens.identify(a), nil, "batch W tall body naming another PNG stays native "..id)
		a.add_mos = {{image=entry.image, display_h=2, display_y=-1, shader="x"}}
		equal(Tokens.identify(a), nil, "batch W tall body with extra keys stays native "..id)
		a.add_mos = {{image=entry.image, display_h=3, display_y=-1}}
		equal(Tokens.identify(a), nil, "batch W tall body with other dimensions stays native "..id)
		a.add_mos = {{image=entry.image, display_h=2, display_y=-1}, {_isshaderaura=true, image="shockbolt/aura.png"}}
		equal(Tokens.identify(a), id, "batch W tall body with shader aura bookkeeping "..id)
	end
	a = actor(entry)
	a.type = entry.type == "undead" and "humanoid" or "undead"
	equal(Tokens.identify(a), nil, "batch W type changed "..id)
	a = actor(entry)
	a.subtype = "other-subtype"
	equal(Tokens.identify(a), nil, "batch W subtype changed "..id)
	a = actor(entry)
	a.shader = "some_shader"
	equal(Tokens.identify(a), nil, "batch W shader keeps native art "..id)
	a = actor(entry)
	a.moddable_tile = "some_doll"
	equal(Tokens.identify(a), nil, "batch W paper-doll actor keeps native art "..id)
	a = actor(entry)
	a.anim = {}
	equal(Tokens.identify(a), nil, "batch W animation keeps native art "..id)
	a = actor(entry)
	a.add_displays = {{image="npc/iceblock.png"}}
	equal(Tokens.identify(a), nil, "batch W frozen/pinned add_displays keep native art "..id)
	a = actor(entry)
	a.unique = true
	equal(Tokens.identify(a), nil, "batch W non-unique entry rejects an unknown unique "..id)
	a = actor(entry)
	a.define_as = "SOME_DEFINE_AS"
	equal(Tokens.identify(a), nil, "batch W unexpected define_as "..id)
	if defines_w[id] then
		a = actor(entry)
		a.define_as = nil
		equal(Tokens.identify(a), nil, "batch W bound entry needs its define_as "..id)
	end
	a = actor(entry)
	a.image = "npc/some_other_image.png"
	equal(Tokens.identify(a), nil, "batch W other image keeps native art "..id)
	a = actor(entry)
	a.__old_type = {entry.type, entry.subtype}
	a.type, a.subtype = "demon", "major"
	a.sustain_talents = {T_FLAME_OF_URH_ROK = {}}
	equal(Tokens.identify(a), nil, "batch W Flame of Urh'Rok form is not supported "..id)
	a = actor(entry)
	a.add_mos = {{_isshaderaura=true, image="shockbolt/aura.png"}}
	equal(Tokens.identify(a), id, "batch W shader aura entry is ignored "..id)
	-- No variants or aliases: a summon shape carrying a wild-summon rename or another PNG stays native.
	a = actor(entry)
	a.summoner, a.ai, a.wild_gift_summon = {}, "summoned", true
	equal(Tokens.identify(a), id, "batch W a same-body summon is the same exact leaf "..id)
	a.name = entry.name.." (wild summon)"
	equal(Tokens.identify(a), nil, "batch W the wild-summon rename is not covered "..id)
	a = actor(entry)
	a.summoner, a.ai, a.summoner_gain_exp, a.wild_gift_summon = {}, "summoned", true, true
	a.image = "npc/summoner_ritch.png"
	equal(Tokens.identify(a), nil, "batch W no summon PNG alias "..id)
end
-- Birth sustains are temporary values, shields and particles only.
for id, talents in pairs({banshee={"T_BLUR_SIGHT"}, ["grannor-vin"]={"T_CALL_SHADOWS"}}) do
	local entry = Tokens.by_id[id]
	local a = actor(entry)
	a.sustain_talents = {}
	for _, tid in ipairs(talents) do a.sustain_talents[tid] = {} end
	a.__particles = {{}}
	a.resists = {COLD=50}
	equal(Tokens.identify(a), id, "batch W birth sustain keeps the body "..id)
end
-- Necromancer Assemble minion (talents/spells/master-of-bones.lua:429): same name, body and nice_tile, no
-- define_as, so it wears the heavy bone giant token by the ordinary key; a Lord of Skulls renames it.
do
	local entry = Tokens.by_id["heavy-bone-giant"]
	local a = actor(entry)
	a.image, a.add_mos = "invis.png", {{image=entry.image, display_h=2, display_y=-1}}
	a.faction, a.summoner, a.summon_time = "players", {faction="players"}, 7
	a.necrotic_minion, a.summoner_gain_exp, a.is_bone_giant = true, true, "h_bone_giant"
	equal(Tokens.identify(a), "heavy-bone-giant", "batch W Assemble minion is the same body as the heavy bone giant")
	a.name = "Lord of Skulls (bone giant)"
	equal(Tokens.identify(a), nil, "batch W Lord of Skulls minion is renamed and stays native")
	a = actor(entry)
	a.name, a.image, a.add_mos = "eternal bone giant", "invis.png", {{image=entry.image, display_h=2, display_y=-1}}
	equal(Tokens.identify(a), nil, "batch W an eternal bone giant cannot wear the heavy bone giant body")
	a = actor(Tokens.by_id["eternal-bone-giant"])
	a.image, a.add_mos = "invis.png", {{image=entry.image, display_h=2, display_y=-1}}
	equal(Tokens.identify(a), nil, "batch W the eternal bone giant cannot wear the heavy bone giant PNG")
	a = actor(Tokens.by_id["bone-giant"])
	a.image, a.add_mos = "invis.png", {{image=entry.image, display_h=2, display_y=-1}}
	equal(Tokens.identify(a), nil, "batch W a bone giant cannot wear the heavy bone giant body")
	-- A random boss made from the non-unique native-tall body keeps native art (only unique tall bodies qualify).
	local base = actor(entry)
	base.image, base.add_mos = "invis.png", {{image=entry.image, display_h=2, display_y=-1}}
	local capture = Tokens.captureRandomOrigin(base)
	local boss = actor(entry)
	boss.image, boss.add_mos = "invis.png", {{image=entry.image, display_h=2, display_y=-1}}
	boss.name, boss.define_as, boss.unique, boss.randboss = "Inquisitor Test", "RANDOM_BOSS_W", "Inquisitor Test", true
	equal(Tokens.recordRandomOrigin(boss, capture, "RANDOM_BOSS_W"), nil, "batch W non-unique tall random boss stays native")
	equal(Tokens.identify(boss), nil, "batch W non-unique tall random boss identify")
end
-- A random boss made from a flat entry (the grushnak-armory 'Warbear') keeps the war bear token.
do
	local entry = Tokens.by_id["war-bear"]
	local capture = Tokens.captureRandomOrigin(actor(entry))
	local boss = actor(entry)
	boss.name, boss.define_as, boss.unique, boss.randboss = "Warbear Test", "RANDOM_BOSS_WB", "Warbear Test", true
	equal(Tokens.recordRandomOrigin(boss, capture, "RANDOM_BOSS_WB"), "war-bear", "batch W flat random boss keeps the war bear token")
	equal(Tokens.identify(boss), "war-bear", "batch W flat random boss identify")
end
-- The wyrmic pair, the bears, the three ants and the giants cannot borrow each other.
for _, group in ipairs({{"fiery-orc-wyrmic", "icy-orc-wyrmic"}, {"cave-bear", "war-bear", "brown-bear", "black-bear"},
	{"giant-fire-ant", "giant-ice-ant", "giant-lightning-ant", "giant-red-ant", "giant-blue-ant", "giant-white-ant"},
	{"heavy-bone-giant", "eternal-bone-giant", "bone-giant", "half-finished-bone-giant"},
	{"fiery-orc-wyrmic", "orc-warrior", "orc-soldier", "orc-pyromancer"}, {"icy-orc-wyrmic", "orc-cryomancer", "orc-archer"},
	{"grannor-vin", "grannor-vor"}, {"rotting-mummy", "ancient-elven-mummy"}, {"yaech-mindslayer", "yaech-hunter", "yaech-diver"}}) do
	for _, id in ipairs(group) do
		for _, other in ipairs(group) do
			if id ~= other and Tokens.by_id[id] and Tokens.by_id[other] then
				local a = actor(Tokens.by_id[id])
				a.image = Tokens.by_id[other].image
				equal(Tokens.identify(a), nil, "batch W sibling cannot borrow image "..id.." <- "..other)
				a = actor(Tokens.by_id[id])
				a.name = Tokens.by_id[other].name
				equal(Tokens.identify(a), nil, "batch W body cannot wear another sibling's name "..id.." as "..other)
			end
		end
	end
end
-- Look-alikes stay native (other names on the same PNGs, the dropped acid ant, ruin banshee, yeek mindslayer).
for _, excluded in ipairs({
	-- (the giant acid ant was kept native here; batch X maps it.)
	-- (the giant army ant was kept native here; batch X maps it.)
	{name="giant fire ant", type="insect", subtype="ant", image="npc/ice_ant.png"},
	{name="giant ice ant", type="insect", subtype="ant", image="npc/lightning_ant.png"},
	{name="ruin banshee", type="undead", subtype="ghost", image="npc/banshee.png"},
	{name="banshee", type="undead", subtype="ghost", image="npc/undead_ghost_ruin_banshee.png"},
	{name="yeek mindslayer", type="humanoid", subtype="yeek", image="npc/humanoid_yaech_yaech_mindslayer.png"},
	{name="grizzly bear", type="animal", subtype="bear", image="npc/cave_bear.png"},
	{name="brown bear", type="animal", subtype="bear", image="npc/war_bear.png"},
	{name="animated mummy wrappings", type="undead", subtype="mummy", image="npc/undead_mummy_rotting_mummy.png"},
	{name="greater mummy", type="undead", subtype="mummy", image="npc/undead_mummy_rotting_mummy.png"},
	{name="fiery orc wyrmic", type="humanoid", subtype="orc", image="npc/humanoid_orc_fiery_orc_wyrmic.png"},
	{name="icy orc wyrmic", type="humanoid", subtype="orc", image="npc/humanoid_orc_icy_orc_wyrmic.png", define_as="ORC_FIRE_WYRMIC"},
	{name="orc master wyrmic", type="humanoid", subtype="orc", image="npc/humanoid_orc_fiery_orc_wyrmic.png", define_as="ORC_FIRE_WYRMIC"},
	{name="runed bone giant", type="undead", subtype="giant", image="invis.png", add_mos={{image="npc/undead_giant_heavy_bone_giant.png", display_h=2, display_y=-1}}},
}) do
	equal(Tokens.identify(excluded), nil, "batch W look-alike stays native "..excluded.name.." "..tostring(excluded.define_as))
end

-- Batch X: the twelve identities after batch W (giant acid ant, giant army ant,
-- yaech psion, blue crystal, devourer, skeleton assassin, assassin, elven
-- corruptor, orc fighter, greater telugoroth, teluvorta, dread). All are
-- non-unique. Only the assassin binds a define_as (THIEF_ASSASSIN, repeated by
-- the shadowblade leaf under another name); the greater telugoroth is
-- native-tall (native_tall=true); none can reach Flame of Urh'Rok, so there is
-- no opt-in.
local batch_x = {"giant-acid-ant", "giant-army-ant", "yaech-psion", "blue-crystal", "devourer", "skeleton-assassin",
	"assassin", "elven-corruptor", "orc-fighter", "greater-telugoroth", "teluvorta", "dread"}
local names_x = {["giant-acid-ant"]="giant acid ant", ["giant-army-ant"]="giant army ant", ["yaech-psion"]="yaech psion",
	["blue-crystal"]="blue crystal", devourer="devourer", ["skeleton-assassin"]="skeleton assassin", assassin="assassin",
	["elven-corruptor"]="elven corruptor", ["orc-fighter"]="orc fighter", ["greater-telugoroth"]="greater telugoroth",
	teluvorta="teluvorta", dread="dread"}
local defines_x = {assassin="THIEF_ASSASSIN"}
local tall_x = {["greater-telugoroth"]=true}
for _, id in ipairs(batch_x) do
	local entry = Tokens.by_id[id]
	if entry == nil then error("batch X catalog entry missing: "..id) end
	equal(entry.name, names_x[id], "batch X exact name "..id)
	equal(entry.define_as, defines_x[id], "batch X define_as binding "..id)
	equal(entry.unique, nil, "batch X non-unique "..id)
	equal(entry.native_tall, tall_x[id] and true or nil, "batch X native_tall flag "..id)
	equal(entry.urh_rok_form, nil, "batch X no urh_rok_form flag "..id)
	equal(Tokens.identify(actor(entry)), id, "batch X exact identity "..id)
	local a = actor(entry)
	a.tint_r, a.tint_g, a.tint_b = 0, 0, 0
	equal(Tokens.identify(a), id, "batch X tint is colour only "..id)
	a = actor(entry)
	a.color_r, a.color_g, a.color_b = 0, 0, 185
	equal(Tokens.identify(a), id, "batch X colour modulation keeps the token "..id)
	a = actor(entry)
	a.image = "invis.png"
	a.add_mos = {{image=entry.image, display_h=2, display_y=-1}}
	equal(Tokens.identify(a), tall_x[id] and id or nil, "batch X tall body accepted only for native_tall entries "..id)
	if tall_x[id] then
		a.add_mos = {{image=entry.image, display_h=2, display_y=-1}, {image="npc/other.png"}}
		equal(Tokens.identify(a), nil, "batch X tall body with a second overlay stays native "..id)
		a.add_mos = {{image="npc/other.png", display_h=2, display_y=-1}}
		equal(Tokens.identify(a), nil, "batch X tall body naming another PNG stays native "..id)
		a.add_mos = {{image=entry.image, display_h=2, display_y=-1, shader="x"}}
		equal(Tokens.identify(a), nil, "batch X tall body with extra keys stays native "..id)
		a.add_mos = {{image=entry.image, display_h=3, display_y=-1}}
		equal(Tokens.identify(a), nil, "batch X tall body with other dimensions stays native "..id)
		a.add_mos = {{image=entry.image, display_h=2, display_y=-1}, {_isshaderaura=true, image="shockbolt/aura.png"}}
		equal(Tokens.identify(a), id, "batch X tall body with shader aura bookkeeping "..id)
	end
	a = actor(entry)
	a.type = entry.type == "undead" and "humanoid" or "undead"
	equal(Tokens.identify(a), nil, "batch X type changed "..id)
	a = actor(entry)
	a.subtype = "other-subtype"
	equal(Tokens.identify(a), nil, "batch X subtype changed "..id)
	a = actor(entry)
	a.shader = "some_shader"
	equal(Tokens.identify(a), nil, "batch X shader keeps native art "..id)
	a = actor(entry)
	a.moddable_tile = "some_doll"
	equal(Tokens.identify(a), nil, "batch X paper-doll actor keeps native art "..id)
	a = actor(entry)
	a.anim = {}
	equal(Tokens.identify(a), nil, "batch X animation keeps native art "..id)
	a = actor(entry)
	a.add_displays = {{image="npc/iceblock.png"}}
	equal(Tokens.identify(a), nil, "batch X frozen/pinned add_displays keep native art "..id)
	a = actor(entry)
	a.unique = true
	equal(Tokens.identify(a), nil, "batch X non-unique entry rejects an unknown unique "..id)
	a = actor(entry)
	a.define_as = "SOME_DEFINE_AS"
	equal(Tokens.identify(a), nil, "batch X unexpected define_as "..id)
	if defines_x[id] then
		a = actor(entry)
		a.define_as = nil
		equal(Tokens.identify(a), nil, "batch X bound entry needs its define_as "..id)
	end
	a = actor(entry)
	a.image = "npc/some_other_image.png"
	equal(Tokens.identify(a), nil, "batch X other image keeps native art "..id)
	a = actor(entry)
	a.__old_type = {entry.type, entry.subtype}
	a.type, a.subtype = "demon", "major"
	a.sustain_talents = {T_FLAME_OF_URH_ROK = {}}
	equal(Tokens.identify(a), nil, "batch X Flame of Urh'Rok form is not supported "..id)
	a = actor(entry)
	a.add_mos = {{_isshaderaura=true, image="shockbolt/aura.png"}}
	equal(Tokens.identify(a), id, "batch X shader aura entry is ignored "..id)
	-- No variants or aliases: a summon shape carrying a wild-summon rename or another PNG stays native.
	a = actor(entry)
	a.summoner, a.ai, a.wild_gift_summon = {}, "summoned", true
	equal(Tokens.identify(a), id, "batch X a same-body summon is the same exact leaf "..id)
	a.name = entry.name.." (wild summon)"
	equal(Tokens.identify(a), nil, "batch X the wild-summon rename is not covered "..id)
	a = actor(entry)
	a.summoner, a.ai, a.summoner_gain_exp, a.wild_gift_summon = {}, "summoned", true, true
	a.image = "npc/summoner_ritch.png"
	equal(Tokens.identify(a), nil, "batch X no summon PNG alias "..id)
end
-- Birth sustains are temporary values, shields and particles only.
for id, talents in pairs({dread={"T_BLUR_SIGHT"}, ["skeleton-assassin"]={"T_STEALTH", "T_SHADOW_COMBAT"}, assassin={"T_STEALTH"},
	["elven-corruptor"]={"T_BONE_SHIELD"}}) do
	local entry = Tokens.by_id[id]
	local a = actor(entry)
	a.sustain_talents = {}
	for _, tid in ipairs(talents) do a.sustain_talents[tid] = {} end
	a.__particles = {{}}
	a.resists = {COLD=50}
	a.stealth = 30
	equal(Tokens.identify(a), id, "batch X birth sustain keeps the body "..id)
end
-- Dread-talent minion (talents/spells/dreadmaster.lua:35), dreadmaster minion and the dreadmaster's summon
-- (general/npcs/ghost.lua:96): same name, type, subtype and image, no define_as, so they wear the dread token by the
-- ordinary key; a dreadmaster (other name) stays native even on the dread PNG.
do
	local entry = Tokens.by_id["dread"]
	local a = actor(entry)
	a.faction, a.summoner, a.summon_time = "players", {faction="players"}, 8
	a.dread_minion, a.no_boneyard_resurrect, a.exp_worth = "dread", true, 0
	a.necrotic_minion, a.summoner_gain_exp = true, true
	equal(Tokens.identify(a), "dread", "batch X Dread-talent minion wears the dread token")
	a = actor(entry)
	a.summoner, a.ai, a.exp_worth = {}, "summoned", 0
	equal(Tokens.identify(a), "dread", "batch X dreadmaster-summoned dread wears the dread token")
	a.name = "dreadmaster"
	equal(Tokens.identify(a), nil, "batch X a dreadmaster on the dread PNG stays native")
	a = actor(entry)
	a.name, a.image = "dreadmaster", "npc/dreadmaster.png"
	equal(Tokens.identify(a), "dreadmaster", "batch X the dreadmaster (mapped by batch AA) wears its own token, not the dread's")
end
-- Assassin: the shadowblade repeats define_as THIEF_ASSASSIN under another name and PNG; only the exact name wears the token.
do
	local entry = Tokens.by_id["assassin"]
	local a = actor(entry)
	a.name, a.image = "shadowblade", "npc/humanoid_human_shadowblade.png"
	equal(Tokens.identify(a), "shadowblade", "batch X the shadowblade sharing THIEF_ASSASSIN (mapped by batch AB) wears its own token")
	a = actor(entry)
	a.name = "shadowblade"
	equal(Tokens.identify(a), nil, "batch X the assassin body cannot wear the shadowblade name")
	a = actor(entry)
	a.name = "Assassin Lord"
	equal(Tokens.identify(a), nil, "batch X the assassin body cannot wear the Assassin Lord name")
	equal(Tokens.identify(actor(Tokens.by_id["assassin-lord"])), "assassin-lord", "batch X the Assassin Lord keeps its own token")
end
-- A random boss made from the non-unique native-tall greater telugoroth keeps native art (only unique tall bodies qualify).
do
	local entry = Tokens.by_id["greater-telugoroth"]
	local base = actor(entry)
	base.image, base.add_mos = "invis.png", {{image=entry.image, display_h=2, display_y=-1}}
	local capture = Tokens.captureRandomOrigin(base)
	local boss = actor(entry)
	boss.image, boss.add_mos = "invis.png", {{image=entry.image, display_h=2, display_y=-1}}
	boss.name, boss.define_as, boss.unique, boss.randboss = "Inquisitor Test", "RANDOM_BOSS_X", "Inquisitor Test", true
	equal(Tokens.recordRandomOrigin(boss, capture, "RANDOM_BOSS_X"), nil, "batch X non-unique tall random boss stays native")
	equal(Tokens.identify(boss), nil, "batch X non-unique tall random boss identify")
end
-- A random boss made from a flat entry keeps that token.
do
	local entry = Tokens.by_id["orc-fighter"]
	local capture = Tokens.captureRandomOrigin(actor(entry))
	local boss = actor(entry)
	boss.name, boss.define_as, boss.unique, boss.randboss = "Fighter Test", "RANDOM_BOSS_XF", "Fighter Test", true
	equal(Tokens.recordRandomOrigin(boss, capture, "RANDOM_BOSS_XF"), "orc-fighter", "batch X flat random boss keeps the orc fighter token")
	equal(Tokens.identify(boss), "orc-fighter", "batch X flat random boss identify")
end
-- The new bodies cannot borrow their siblings' names or images.
for _, group in ipairs({{"giant-acid-ant", "giant-army-ant", "giant-black-ant", "giant-carpenter-ant", "giant-fire-ant", "giant-green-ant"},
	{"telugoroth", "greater-telugoroth", "teluvorta"}, {"skeleton-assassin", "skeleton-warrior", "skeleton-magus"},
	{"assassin", "rogue", "thief", "assassin-lord", "orc-assassin"}, {"orc-fighter", "orc-warrior", "orc-soldier", "orc-archer"},
	{"blue-crystal", "white-crystal", "red-crystal", "black-crystal", "crimson-crystal"},
	{"yaech-psion", "yaech-mindslayer", "yaech-hunter", "yaech-diver"}, {"elven-corruptor", "elven-mage", "elven-cultist", "grand-corruptor"},
	{"dread", "banshee", "shade-of-telos", "kors-fury"}, {"devourer", "bloated-horror", "weirdling-beast"}}) do
	for _, id in ipairs(group) do
		for _, other in ipairs(group) do
			if id ~= other and Tokens.by_id[id] and Tokens.by_id[other] then
				local a = actor(Tokens.by_id[id])
				a.image = Tokens.by_id[other].image
				equal(Tokens.identify(a), nil, "batch X sibling cannot borrow image "..id.." <- "..other)
				a = actor(Tokens.by_id[id])
				a.name = Tokens.by_id[other].name
				equal(Tokens.identify(a), nil, "batch X body cannot wear another sibling's name "..id.." as "..other)
			end
		end
	end
end
-- Look-alikes stay native (other names on the same PNGs, neighbours that were not selected).
for _, excluded in ipairs({
	{name="giant acid ant", type="insect", subtype="ant", image="npc/black_ant.png"},
	{name="giant army ant", type="insect", subtype="ant", image="npc/acid_ant.png"},
	{name="giant black ant", type="insect", subtype="ant", image="npc/acid_ant.png"},
	-- (the ultimate telugoroth and greater teluvorta were not selected here; batch Z maps them as native-tall.)
	{name="teluvorta", type="elemental", subtype="temporal", image="npc/elemental_temporal_greater_telugoroth.png"},
	{name="greater telugoroth", type="elemental", subtype="temporal", image="npc/elemental_temporal_telugoroth.png"},
	{name="shadowblade", type="humanoid", subtype="human", image="npc/humanoid_human_assassin.png", define_as="THIEF_ASSASSIN"},
	{name="assassin", type="humanoid", subtype="human", image="npc/humanoid_human_assassin.png"},
	{name="orc elite fighter", type="humanoid", subtype="orc", image="npc/humanoid_orc_orc_fighter.png", define_as="ORC_ELITE_FIGHTER"},
	{name="orc fighter", type="humanoid", subtype="orc", image="npc/humanoid_orc_orc_soldier.png"},
	{name="multi-hued crystal", type="immovable", subtype="crystal", image="npc/crystal_blue.png"},
	{name="skeleton assassin", type="undead", subtype="skeleton", image="npc/undead_skeleton_skeleton_warrior.png"},
	{name="elven corruptor", type="humanoid", subtype="elf", image="npc/humanoid_shalore_elven_corruptor.png"},
	{name="yaech psion", type="humanoid", subtype="yeek", image="npc/humanoid_yaech_yaech_psion.png"},
	{name="devourer", type="horror", subtype="corrupted", image="npc/horror_eldritch_devourer.png"},
	-- (uruivellas was not selected here; batch Y maps it as native-tall.)
}) do
	equal(Tokens.identify(excluded), nil, "batch X look-alike stays native "..excluded.name.." "..tostring(excluded.define_as))
end

-- Batch Y: the twelve identities after batch X (uruivellas, thaurhereg, orc
-- corruptor, temporal stalker, broken golem, golem, blade horror, animated mummy
-- wrappings, grizzly bear, weaver patriarch, luminous horror, necrotic mass). All
-- are non-unique. Only the blade horror binds a define_as (BLADEHORROR); six are
-- native-tall (native_tall=true); none can reach Flame of Urh'Rok, so there is no
-- opt-in.
local batch_y = {"uruivellas", "thaurhereg", "orc-corruptor", "temporal-stalker", "broken-golem", "golem", "blade-horror",
	"animated-mummy-wrappings", "grizzly-bear", "weaver-patriarch", "luminous-horror", "necrotic-mass"}
local names_y = {uruivellas="uruivellas", thaurhereg="thaurhereg", ["orc-corruptor"]="orc corruptor", ["temporal-stalker"]="temporal stalker",
	["broken-golem"]="broken golem", golem="golem", ["blade-horror"]="blade horror", ["animated-mummy-wrappings"]="animated mummy wrappings",
	["grizzly-bear"]="grizzly bear", ["weaver-patriarch"]="weaver patriarch", ["luminous-horror"]="luminous horror", ["necrotic-mass"]="necrotic mass"}
local defines_y = {["blade-horror"]="BLADEHORROR"}
local tall_y = {uruivellas=true, thaurhereg=true, ["temporal-stalker"]=true, ["blade-horror"]=true, ["grizzly-bear"]=true, ["necrotic-mass"]=true}
for _, id in ipairs(batch_y) do
	local entry = Tokens.by_id[id]
	if entry == nil then error("batch Y catalog entry missing: "..id) end
	equal(entry.name, names_y[id], "batch Y exact name "..id)
	equal(entry.define_as, defines_y[id], "batch Y define_as binding "..id)
	equal(entry.unique, nil, "batch Y non-unique "..id)
	equal(entry.native_tall, tall_y[id] and true or nil, "batch Y native_tall flag "..id)
	equal(entry.urh_rok_form, nil, "batch Y no urh_rok_form flag "..id)
	equal(Tokens.identify(actor(entry)), id, "batch Y exact identity "..id)
	local a = actor(entry)
	a.tint_r, a.tint_g, a.tint_b = 0, 0, 0
	equal(Tokens.identify(a), id, "batch Y tint is colour only "..id)
	a = actor(entry)
	a.color_r, a.color_g, a.color_b = 0, 0, 185
	equal(Tokens.identify(a), id, "batch Y colour modulation keeps the token "..id)
	a = actor(entry)
	a.image = "invis.png"
	a.add_mos = {{image=entry.image, display_h=2, display_y=-1}}
	equal(Tokens.identify(a), tall_y[id] and id or nil, "batch Y tall body accepted only for native_tall entries "..id)
	if tall_y[id] then
		a.add_mos = {{image=entry.image, display_h=2, display_y=-1}, {image="npc/other.png"}}
		equal(Tokens.identify(a), nil, "batch Y tall body with a second overlay stays native "..id)
		a.add_mos = {{image="npc/other.png", display_h=2, display_y=-1}}
		equal(Tokens.identify(a), nil, "batch Y tall body naming another PNG stays native "..id)
		a.add_mos = {{image=entry.image, display_h=2, display_y=-1, shader="x"}}
		equal(Tokens.identify(a), nil, "batch Y tall body with extra keys stays native "..id)
		a.add_mos = {{image=entry.image, display_h=3, display_y=-1}}
		equal(Tokens.identify(a), nil, "batch Y tall body with other dimensions stays native "..id)
		a.add_mos = {{image=entry.image, display_h=2, display_y=-1}, {_isshaderaura=true, image="shockbolt/aura.png"}}
		equal(Tokens.identify(a), id, "batch Y tall body with shader aura bookkeeping "..id)
		-- Single image (nicer_tiles off): the flat native image is accepted too.
		a = actor(entry)
		a.image, a.add_mos = entry.image, nil
		equal(Tokens.identify(a), id, "batch Y single native image with nicer_tiles off "..id)
	end
	a = actor(entry)
	a.type = entry.type == "undead" and "humanoid" or "undead"
	equal(Tokens.identify(a), nil, "batch Y type changed "..id)
	a = actor(entry)
	a.subtype = "other-subtype"
	equal(Tokens.identify(a), nil, "batch Y subtype changed "..id)
	a = actor(entry)
	a.shader = "some_shader"
	equal(Tokens.identify(a), nil, "batch Y shader keeps native art "..id)
	a = actor(entry)
	a.moddable_tile = "some_doll"
	equal(Tokens.identify(a), nil, "batch Y paper-doll actor keeps native art "..id)
	a = actor(entry)
	a.anim = {}
	equal(Tokens.identify(a), nil, "batch Y animation keeps native art "..id)
	a = actor(entry)
	a.add_displays = {{image="npc/iceblock.png"}}
	equal(Tokens.identify(a), nil, "batch Y frozen/pinned add_displays keep native art "..id)
	a = actor(entry)
	a.unique = true
	equal(Tokens.identify(a), nil, "batch Y non-unique entry rejects an unknown unique "..id)
	a = actor(entry)
	a.define_as = "SOME_DEFINE_AS"
	equal(Tokens.identify(a), nil, "batch Y unexpected define_as "..id)
	if defines_y[id] then
		a = actor(entry)
		a.define_as = nil
		equal(Tokens.identify(a), nil, "batch Y bound entry needs its define_as "..id)
	end
	a = actor(entry)
	a.image = "npc/some_other_image.png"
	equal(Tokens.identify(a), nil, "batch Y other image keeps native art "..id)
	a = actor(entry)
	a.__old_type = {entry.type, entry.subtype}
	a.type, a.subtype = "demon", "major"
	a.sustain_talents = {T_FLAME_OF_URH_ROK = {}}
	-- A demon/major entry already is that body, so the sentinel changes nothing; every other body must stay native.
	equal(Tokens.identify(a), entry.type == "demon" and id or nil, "batch Y Flame of Urh'Rok form is not supported "..id)
	a = actor(entry)
	a.add_mos = {{_isshaderaura=true, image="shockbolt/aura.png"}}
	equal(Tokens.identify(a), id, "batch Y shader aura entry is ignored "..id)
	-- No variants or aliases: a summon shape carrying a wild-summon rename or another PNG stays native.
	a = actor(entry)
	a.summoner, a.ai, a.wild_gift_summon = {}, "summoned", true
	equal(Tokens.identify(a), id, "batch Y a same-body summon is the same exact leaf "..id)
	a.name = entry.name.." (wild summon)"
	equal(Tokens.identify(a), nil, "batch Y the wild-summon rename is not covered "..id)
	a = actor(entry)
	a.summoner, a.ai, a.summoner_gain_exp, a.wild_gift_summon = {}, "summoned", true, true
	a.image = "npc/summoner_ritch.png"
	equal(Tokens.identify(a), nil, "batch Y no summon PNG alias "..id)
end
-- Birth sustains are temporary values, shields and particles only.
for id, talents in pairs({thaurhereg={"T_BONE_SHIELD"}, ["orc-corruptor"]={"T_BONE_SHIELD"}, ["temporal-stalker"]={"T_STEALTH"},
	["blade-horror"]={"T_KINETIC_AURA", "T_KINETIC_SHIELD"}, ["luminous-horror"]={"T_CHANT_OF_FORTITUDE", "T_PROVIDENCE"},
	["weaver-patriarch"]={"T_SPIN_FATE"}}) do
	local a = actor(Tokens.by_id[id])
	a.sustain_talents = {}
	for _, tid in ipairs(talents) do a.sustain_talents[tid] = {} end
	a.__particles = {{}}
	a.resists = {COLD=50}
	a.stealth = 30
	equal(Tokens.identify(a), id, "batch Y birth sustain keeps the body "..id)
end
-- The player's alchemist golem (talents/spells/golemancy.lua) shares the golem name, type and subtype but uses another
-- PNG and a paper doll, so it keeps its native display.
do
	local a = actor(Tokens.by_id["golem"])
	a.image, a.moddable_tile = "npc/alchemist_golem.png", "runic_golem"
	equal(Tokens.identify(a), nil, "batch Y the alchemist golem of the player stays native")
	a = actor(Tokens.by_id["golem"])
	a.image = "npc/alchemist_golem.png"
	equal(Tokens.identify(a), nil, "batch Y an alchemist golem PNG alone is not the golem token")
	a = actor(Tokens.by_id["golem"])
	a.moddable_tile = "runic_golem"
	equal(Tokens.identify(a), nil, "batch Y a paper-doll golem stays native")
end
-- heart-gloom renames non-unique bears; the renamed grizzly (a native-tall body) keeps the grizzly token.
do
	local a = actor(Tokens.by_id["grizzly-bear"])
	a.name = "gloomy grizzly bear"
	equal(Tokens.identify(a), "grizzly-bear", "batch Y a gloomy grizzly bear wears the grizzly token")
	a.image, a.add_mos = "invis.png", {{image="npc/grizzly_bear.png", display_h=2, display_y=-1}}
	equal(Tokens.identify(a), "grizzly-bear", "batch Y a gloomy native-tall grizzly wears the grizzly token")
end
-- A random boss made from a non-unique native-tall entry keeps native art (only unique tall bodies qualify).
do
	local entry = Tokens.by_id["uruivellas"]
	local base = actor(entry)
	base.image, base.add_mos = "invis.png", {{image=entry.image, display_h=2, display_y=-1}}
	local capture = Tokens.captureRandomOrigin(base)
	local boss = actor(entry)
	boss.image, boss.add_mos = "invis.png", {{image=entry.image, display_h=2, display_y=-1}}
	boss.name, boss.define_as, boss.unique, boss.randboss = "Demon Test", "RANDOM_BOSS_Y", "Demon Test", true, true
	equal(Tokens.recordRandomOrigin(boss, capture, "RANDOM_BOSS_Y"), nil, "batch Y non-unique tall random boss stays native")
	equal(Tokens.identify(boss), nil, "batch Y non-unique tall random boss identify")
end
-- A random boss made from a flat entry keeps that token.
do
	local entry = Tokens.by_id["orc-corruptor"]
	local capture = Tokens.captureRandomOrigin(actor(entry))
	local boss = actor(entry)
	boss.name, boss.define_as, boss.unique, boss.randboss = "Corruptor Test", "RANDOM_BOSS_YF", "Corruptor Test", true
	equal(Tokens.recordRandomOrigin(boss, capture, "RANDOM_BOSS_YF"), "orc-corruptor", "batch Y flat random boss keeps the orc corruptor token")
	equal(Tokens.identify(boss), "orc-corruptor", "batch Y flat random boss identify")
end
-- The new bodies cannot borrow their siblings' names or images.
for _, group in ipairs({{"uruivellas", "thaurhereg", "dolleg", "kryl-feijan", "minotaur"}, {"broken-golem", "golem", "atamathon"},
	{"orc-corruptor", "orc-warrior", "orc-blood-mage", "orc-necromancer"}, {"temporal-stalker", "shadow-stalker", "dread"},
	{"blade-horror", "luminous-horror", "necrotic-mass", "dread"},
	{"grizzly-bear", "brown-bear", "black-bear", "cave-bear", "war-bear"},
	{"weaver-patriarch", "weaver-young", "weaver-queen"},
	{"animated-mummy-wrappings", "rotting-mummy", "ancient-elven-mummy"}}) do
	for _, id in ipairs(group) do
		for _, other in ipairs(group) do
			if id ~= other and Tokens.by_id[id] and Tokens.by_id[other] then
				local a = actor(Tokens.by_id[id])
				a.image = Tokens.by_id[other].image
				equal(Tokens.identify(a), nil, "batch Y sibling cannot borrow image "..id.." <- "..other)
				a = actor(Tokens.by_id[id])
				a.name = Tokens.by_id[other].name
				equal(Tokens.identify(a), nil, "batch Y body cannot wear another sibling's name "..id.." as "..other)
			end
		end
	end
end
-- Look-alikes stay native (other names on the same PNGs, neighbours that were not selected).
for _, excluded in ipairs({
	{name="Ak'Gishil", type="horror", subtype="eldritch", image="invis.png", unique=true, add_mos={{image="npc/horror_eldritch_blade_horror.png", display_h=2, display_y=-1}}},
	{name="blade horror", type="horror", subtype="eldritch", image="invis.png", add_mos={{image="npc/horror_eldritch_blade_horror.png", display_h=2, display_y=-1}}},
-- (the alchemist golem was kept native here; batch AB maps it.)
	{name="golem", type="construct", subtype="golem", image="npc/construct_golem_broken_golem.png"},
	{name="broken golem", type="construct", subtype="golem", image="npc/construct_golem_golem.png"},
	-- weaver matriarch is now mapped by batch AE through its verified single-body tall contract.
	{name="weaver patriarch", type="spiderkin", subtype="spider", image="npc/spiderkin_spider_weaver_young.png"},
	{name="animated mummy wrappings", type="undead", subtype="mummy", image="npc/undead_mummy_animated_mummy_wrappings.png"},
-- (the polar bear was kept native here; batch AA maps it.)
	{name="grizzly bear", type="animal", subtype="bear", image="npc/polar_bear.png"},
-- (the necrotic abomination was kept native here; batch AA maps it.)
	{name="necrotic mass", type="undead", subtype="horror", image="invis.png", add_mos={{image="npc/undead_horror_bone_horror.png", display_h=2, display_y=-1}}},
	{name="uruivellas", type="demon", subtype="major", image="invis.png", add_mos={{image="npc/demon_major_thaurhereg.png", display_h=2, display_y=-1}}},
	{name="thaurhereg", type="demon", subtype="major", image="invis.png", add_mos={{image="npc/demon_major_uruivellas.png", display_h=2, display_y=-1}}},
	{name="orc corruptor", type="humanoid", subtype="orc", image="npc/humanoid_orc_orc_blood_mage.png"},
	{name="luminous horror", type="horror", subtype="corrupted", image="npc/horror_eldritch_luminous_horror.png"},
}) do
	equal(Tokens.identify(excluded), nil, "batch Y look-alike stays native "..excluded.name.." "..tostring(excluded.define_as))
end

-- Batch Z: the twelve identities after batch Y (black mamba, bandit lord, orb
-- weaver, elven elite warrior, ultimate telugoroth, greater teluvorta, runed bone
-- giant, void horror, swarming horror, ravenous horror, rogue sapper, fire
-- wyrm). All are non-unique. Only the rogue sapper binds a define_as
-- (THIEF_SAPPER); six are native-tall (native_tall=true); none can reach Flame of
-- Urh'Rok, so there is no opt-in.
local batch_z = {"black-mamba", "bandit-lord", "orb-weaver", "elven-elite-warrior", "ultimate-telugoroth", "greater-teluvorta",
	"runed-bone-giant", "void-horror", "swarming-horror", "ravenous-horror", "rogue-sapper", "fire-wyrm"}
local names_z = {["black-mamba"]="black mamba", ["bandit-lord"]="bandit lord", ["orb-weaver"]="orb weaver", ["elven-elite-warrior"]="elven elite warrior",
	["ultimate-telugoroth"]="ultimate telugoroth", ["greater-teluvorta"]="greater teluvorta", ["runed-bone-giant"]="runed bone giant",
	["void-horror"]="void horror", ["swarming-horror"]="swarming horror", ["ravenous-horror"]="ravenous horror", ["rogue-sapper"]="rogue sapper", ["fire-wyrm"]="fire wyrm"}
local defines_z = {["rogue-sapper"]="THIEF_SAPPER"}
local tall_z = {["ultimate-telugoroth"]=true, ["greater-teluvorta"]=true, ["runed-bone-giant"]=true, ["swarming-horror"]=true, ["ravenous-horror"]=true, ["fire-wyrm"]=true}
for _, id in ipairs(batch_z) do
	local entry = Tokens.by_id[id]
	if entry == nil then error("batch Z catalog entry missing: "..id) end
	equal(entry.name, names_z[id], "batch Z exact name "..id)
	equal(entry.define_as, defines_z[id], "batch Z define_as binding "..id)
	equal(entry.unique, nil, "batch Z non-unique "..id)
	equal(entry.native_tall, tall_z[id] and true or nil, "batch Z native_tall flag "..id)
	equal(entry.urh_rok_form, nil, "batch Z no urh_rok_form flag "..id)
	equal(Tokens.identify(actor(entry)), id, "batch Z exact identity "..id)
	local a = actor(entry)
	a.tint_r, a.tint_g, a.tint_b = 0, 0, 0
	equal(Tokens.identify(a), id, "batch Z tint is colour only "..id)
	a = actor(entry)
	a.color_r, a.color_g, a.color_b = 0, 0, 185
	equal(Tokens.identify(a), id, "batch Z colour modulation keeps the token "..id)
	a = actor(entry)
	a.image = "invis.png"
	a.add_mos = {{image=entry.image, display_h=2, display_y=-1}}
	equal(Tokens.identify(a), tall_z[id] and id or nil, "batch Z tall body accepted only for native_tall entries "..id)
	if tall_z[id] then
		a.add_mos = {{image=entry.image, display_h=2, display_y=-1}, {image="npc/other.png"}}
		equal(Tokens.identify(a), nil, "batch Z tall body with a second overlay stays native "..id)
		a.add_mos = {{image="npc/other.png", display_h=2, display_y=-1}}
		equal(Tokens.identify(a), nil, "batch Z tall body naming another PNG stays native "..id)
		a.add_mos = {{image=entry.image, display_h=2, display_y=-1, shader="x"}}
		equal(Tokens.identify(a), nil, "batch Z tall body with extra keys stays native "..id)
		a.add_mos = {{image=entry.image, display_h=3, display_y=-1}}
		equal(Tokens.identify(a), nil, "batch Z tall body with other dimensions stays native "..id)
		a.add_mos = {{image=entry.image, display_h=2, display_y=-1}, {_isshaderaura=true, image="shockbolt/aura.png"}}
		equal(Tokens.identify(a), id, "batch Z tall body with shader aura bookkeeping "..id)
		-- Single image (nicer_tiles off): the flat native image is accepted too.
		a = actor(entry)
		a.image, a.add_mos = entry.image, nil
		equal(Tokens.identify(a), id, "batch Z single native image with nicer_tiles off "..id)
	end
	a = actor(entry)
	a.type = entry.type == "undead" and "humanoid" or "undead"
	equal(Tokens.identify(a), nil, "batch Z type changed "..id)
	a = actor(entry)
	a.subtype = "other-subtype"
	equal(Tokens.identify(a), nil, "batch Z subtype changed "..id)
	a = actor(entry)
	a.shader = "some_shader"
	equal(Tokens.identify(a), nil, "batch Z shader keeps native art "..id)
	a = actor(entry)
	a.moddable_tile = "some_doll"
	equal(Tokens.identify(a), nil, "batch Z paper-doll actor keeps native art "..id)
	a = actor(entry)
	a.anim = {}
	equal(Tokens.identify(a), nil, "batch Z animation keeps native art "..id)
	a = actor(entry)
	a.add_displays = {{image="npc/iceblock.png"}}
	equal(Tokens.identify(a), nil, "batch Z frozen/pinned add_displays keep native art "..id)
	a = actor(entry)
	a.unique = true
	equal(Tokens.identify(a), nil, "batch Z non-unique entry rejects an unknown unique "..id)
	a = actor(entry)
	a.define_as = "SOME_DEFINE_AS"
	equal(Tokens.identify(a), nil, "batch Z unexpected define_as "..id)
	if defines_z[id] then
		a = actor(entry)
		a.define_as = nil
		equal(Tokens.identify(a), nil, "batch Z bound entry needs its define_as "..id)
	end
	a = actor(entry)
	a.image = "npc/some_other_image.png"
	equal(Tokens.identify(a), nil, "batch Z other image keeps native art "..id)
	a = actor(entry)
	a.__old_type = {entry.type, entry.subtype}
	a.type, a.subtype = "demon", "major"
	a.sustain_talents = {T_FLAME_OF_URH_ROK = {}}
	-- A demon/major entry already is that body, so the sentinel changes nothing; every other body must stay native.
	equal(Tokens.identify(a), entry.type == "demon" and id or nil, "batch Z Flame of Urh'Rok form is not supported "..id)
	a = actor(entry)
	a.add_mos = {{_isshaderaura=true, image="shockbolt/aura.png"}}
	equal(Tokens.identify(a), id, "batch Z shader aura entry is ignored "..id)
	-- No variants or aliases: a summon shape carrying a wild-summon rename or another PNG stays native.
	a = actor(entry)
	a.summoner, a.ai, a.wild_gift_summon = {}, "summoned", true
	equal(Tokens.identify(a), id, "batch Z a same-body summon is the same exact leaf "..id)
	a.name = entry.name.." (wild summon)"
	equal(Tokens.identify(a), nil, "batch Z the wild-summon rename is not covered "..id)
	a = actor(entry)
	a.summoner, a.ai, a.summoner_gain_exp, a.wild_gift_summon = {}, "summoned", true, true
	a.image = "npc/summoner_ritch.png"
	equal(Tokens.identify(a), nil, "batch Z no summon PNG alias "..id)
end
-- Birth sustains are temporary values, shields and particles only.
for id, talents in pairs({["bandit-lord"]={"T_STEALTH", "T_TOTAL_THUGGERY"}, ["rogue-sapper"]={"T_STEALTH"}, ["greater-teluvorta"]={"T_REALITY_SMEARING"},
	["runed-bone-giant"]={"T_ARCANE_POWER"}, ["void-horror"]={"T_ENERGY_DECOMPOSITION"}}) do
	local a = actor(Tokens.by_id[id])
	a.sustain_talents = {}
	for _, tid in ipairs(talents) do a.sustain_talents[tid] = {} end
	a.__particles = {{}}
	a.resists = {COLD=50}
	a.stealth = 30
	equal(Tokens.identify(a), id, "batch Z birth sustain keeps the body "..id)
end
-- The rogue sapper reuses the assassin's PNG (explicit image=) but is told apart by name and define_as.
do
	local sapper, assassin = Tokens.by_id["rogue-sapper"], Tokens.by_id["assassin"]
	equal(sapper.image, assassin.image, "batch Z the sapper names the assassin PNG")
	local a = actor(sapper)
	equal(Tokens.identify(a), "rogue-sapper", "batch Z sapper wears the sapper token")
	a = actor(assassin)
	equal(Tokens.identify(a), "assassin", "batch Z assassin keeps the assassin token")
	a = actor(sapper)
	a.name = "assassin"
	equal(Tokens.identify(a), nil, "batch Z sapper define_as under the assassin name stays native")
	a = actor(assassin)
	a.name = "rogue sapper"
	equal(Tokens.identify(a), nil, "batch Z assassin define_as under the sapper name stays native")
	a = actor(sapper)
	a.define_as = nil
	equal(Tokens.identify(a), nil, "batch Z a sapper without THIEF_SAPPER stays native")
	a = actor(assassin)
	a.define_as = "THIEF_SAPPER"
	equal(Tokens.identify(a), nil, "batch Z an assassin bound to THIEF_SAPPER stays native")
end
-- The bandit lord's Summon and the hive summons build other exact leaves; each wears its own token.
do
	for id, entry_id in pairs({["bandit"]="bandit", ["thief"]="thief", ["rogue"]="rogue", ["swarming-horror"]="swarming-horror", ["fire-drake"]="fire-drake"}) do
		local entry = Tokens.by_id[id]
		local a = actor(entry)
		if tall_z[id] then a.image, a.add_mos = "invis.png", {{image=entry.image, display_h=2, display_y=-1}} end
		a.summoner, a.ai = {}, "summoned"
		equal(Tokens.identify(a), entry_id, "batch Z a summoned copy wears its own token "..id)
	end
end
-- A random boss made from a non-unique native-tall entry keeps native art (only unique tall bodies qualify).
do
	local entry = Tokens.by_id["fire-wyrm"]
	local base = actor(entry)
	base.image, base.add_mos = "invis.png", {{image=entry.image, display_h=2, display_y=-1}}
	local capture = Tokens.captureRandomOrigin(base)
	local boss = actor(entry)
	boss.image, boss.add_mos = "invis.png", {{image=entry.image, display_h=2, display_y=-1}}
	boss.name, boss.define_as, boss.unique, boss.randboss = "Flame Terror Test", "RANDOM_BOSS_Z", "Flame Terror Test", true, true
	equal(Tokens.recordRandomOrigin(boss, capture, "RANDOM_BOSS_Z"), nil, "batch Z non-unique tall random boss stays native")
	equal(Tokens.identify(boss), nil, "batch Z non-unique tall random boss identify")
end
-- A random boss made from a flat entry keeps that token.
do
	local entry = Tokens.by_id["bandit-lord"]
	local capture = Tokens.captureRandomOrigin(actor(entry))
	local boss = actor(entry)
	boss.name, boss.define_as, boss.unique, boss.randboss = "Lord Test", "RANDOM_BOSS_ZF", "Lord Test", true
	equal(Tokens.recordRandomOrigin(boss, capture, "RANDOM_BOSS_ZF"), "bandit-lord", "batch Z flat random boss keeps the bandit lord token")
	equal(Tokens.identify(boss), "bandit-lord", "batch Z flat random boss identify")
end
-- The new bodies cannot borrow their siblings' names or images (the assassin/sapper pair shares one PNG on purpose).
for _, group in ipairs({{"black-mamba", "brown-snake", "king-cobra", "white-snake", "rattlesnake", "copperhead-snake"},
	{"bandit-lord", "bandit", "thief", "rogue", "cutpurse", "rogue-sapper"}, {"orb-weaver", "weaver-patriarch", "weaver-young", "weaver-queen", "giant-spider"},
	{"elven-elite-warrior", "elven-warrior", "elven-guard"}, {"ultimate-telugoroth", "greater-telugoroth", "telugoroth", "greater-teluvorta", "teluvorta"},
	{"runed-bone-giant", "bone-giant", "heavy-bone-giant", "eternal-bone-giant"}, {"void-horror", "dredge", "dredgling", "temporal-stalker"},
	{"swarming-horror", "ravenous-horror", "ink-squid"}, {"fire-wyrm", "fire-drake", "fire-drake-hatchling"}}) do
	for _, id in ipairs(group) do
		for _, other in ipairs(group) do
			if id ~= other and Tokens.by_id[id] and Tokens.by_id[other] then
				local a = actor(Tokens.by_id[id])
				a.image = Tokens.by_id[other].image
				if Tokens.by_id[id].image ~= Tokens.by_id[other].image then
					equal(Tokens.identify(a), nil, "batch Z sibling cannot borrow image "..id.." <- "..other)
				end
				a = actor(Tokens.by_id[id])
				a.name = Tokens.by_id[other].name
				equal(Tokens.identify(a), nil, "batch Z body cannot wear another sibling's name "..id.." as "..other)
			end
		end
	end
end
-- Look-alikes stay native (other names on the same PNGs, neighbours that were not selected).
for _, excluded in ipairs({
	{name="black mamba", type="animal", subtype="snake", image="npc/umber-snake.png"},
	{name="anaconda", type="animal", subtype="snake", image="npc/darkgrey-snake.png"},
	{name="bandit lord", type="humanoid", subtype="human", image="npc/humanoid_human_bandit.png"},
	{name="bandit", type="humanoid", subtype="human", image="npc/humanoid_human_bandit_lord.png", define_as="THIEF_BANDIT"},
	{name="rogue sapper", type="humanoid", subtype="human", image="npc/humanoid_human_assassin.png"},
	{name="orb spinner", type="spiderkin", subtype="spider", image="npc/spiderkin_spider_orb_weaver.png"},
	{name="orb weaver", type="spiderkin", subtype="spider", image="npc/spiderkin_spider_weaver_patriarch.png"},
	{name="elven warrior", type="humanoid", subtype="shalore", image="npc/humanoid_shalore_elven_elite_warrior.png"},
	{name="elven elite warrior", type="humanoid", subtype="shalore", image="npc/humanoid_shalore_elven_guard.png"},
-- (the ultimate teluvorta was kept native here; batch AA maps it as native-tall.)
	{name="ultimate telugoroth", type="elemental", subtype="temporal", image="invis.png", add_mos={{image="npc/elemental_temporal_greater_teluvorta.png", display_h=2, display_y=-1}}},
	{name="greater teluvorta", type="elemental", subtype="temporal", image="invis.png", add_mos={{image="npc/elemental_temporal_ultimate_telugoroth.png", display_h=2, display_y=-1}}},
	{name="Half-Finished Bone Giant", type="undead", subtype="giant", image="invis.png", unique=true, add_mos={{image="npc/undead_giant_runed_bone_giant.png", display_h=2, display_y=-1}}},
	{name="runed bone giant", type="undead", subtype="giant", image="invis.png", add_mos={{image="npc/undead_giant_eternal_bone_giant.png", display_h=2, display_y=-1}}},
	{name="void horror", type="horror", subtype="temporal", image="npc/horror_temporal_dredge.png"},
	{name="dredge captain", type="horror", subtype="temporal", image="npc/horror_temporal_void_horror.png"},
	{name="entrenched horror", type="horror", subtype="aquatic", image="invis.png", add_mos={{image="npc/horror_aquatic_swarming_horror.png", display_h=2, display_y=-1}}},
	{name="swarming horror", type="horror", subtype="aquatic", image="invis.png", add_mos={{image="npc/horror_aquatic_ravenous_horror.png", display_h=2, display_y=-1}}},
	{name="ravenous horror", type="horror", subtype="aquatic", image="invis.png", add_mos={{image="npc/horror_aquatic_swarming_horror.png", display_h=2, display_y=-1}}},
	{name="Varsha the Writhing", type="dragon", subtype="fire", image="invis.png", unique=true, add_mos={{image="npc/dragon_fire_fire_wyrm.png", display_h=2, display_y=-1}}},
	{name="fire wyrm", type="dragon", subtype="cold", image="invis.png", add_mos={{image="npc/dragon_fire_fire_wyrm.png", display_h=2, display_y=-1}}},
}) do
	equal(Tokens.identify(excluded), nil, "batch Z look-alike stays native "..excluded.name.." "..tostring(excluded.define_as))
end

-- Batch AA: the twelve identities after batch Z (ultimate faeros, orc
-- berserker, dredge captain, polar bear, anaconda, ultimate teluvorta, necrotic
-- abomination, bone horror, sanguine horror, barrow wight, ogre warmaster,
-- dreadmaster). All are non-unique and none binds a define_as; seven are
-- native-tall (native_tall=true); none can reach Flame of Urh'Rok, so there is
-- no opt-in.
local batch_aa = {"ultimate-faeros", "orc-berserker", "dredge-captain", "polar-bear", "anaconda", "ultimate-teluvorta", "necrotic-abomination",
	"bone-horror", "sanguine-horror", "barrow-wight", "ogre-warmaster", "dreadmaster"}
local names_aa = {["ultimate-faeros"]="ultimate faeros", ["orc-berserker"]="orc berserker", ["dredge-captain"]="dredge captain", ["polar-bear"]="polar bear",
	["anaconda"]="anaconda", ["ultimate-teluvorta"]="ultimate teluvorta", ["necrotic-abomination"]="necrotic abomination", ["bone-horror"]="bone horror",
	["sanguine-horror"]="sanguine horror", ["barrow-wight"]="barrow wight", ["ogre-warmaster"]="ogre warmaster", ["dreadmaster"]="dreadmaster"}
local defines_aa = {}
local tall_aa = {["ultimate-faeros"]=true, ["ultimate-teluvorta"]=true, ["necrotic-abomination"]=true, ["bone-horror"]=true, ["sanguine-horror"]=true,
	["barrow-wight"]=true, ["ogre-warmaster"]=true}
for _, id in ipairs(batch_aa) do
	local entry = Tokens.by_id[id]
	if entry == nil then error("batch AA catalog entry missing: "..id) end
	equal(entry.name, names_aa[id], "batch AA exact name "..id)
	equal(entry.define_as, defines_aa[id], "batch AA define_as binding "..id)
	equal(entry.unique, nil, "batch AA non-unique "..id)
	equal(entry.native_tall, tall_aa[id] and true or nil, "batch AA native_tall flag "..id)
	equal(entry.urh_rok_form, nil, "batch AA no urh_rok_form flag "..id)
	equal(Tokens.identify(actor(entry)), id, "batch AA exact identity "..id)
	local a = actor(entry)
	a.tint_r, a.tint_g, a.tint_b = 0, 0, 0
	equal(Tokens.identify(a), id, "batch AA tint is colour only "..id)
	a = actor(entry)
	a.color_r, a.color_g, a.color_b = 0, 0, 185
	equal(Tokens.identify(a), id, "batch AA colour modulation keeps the token "..id)
	a = actor(entry)
	a.image = "invis.png"
	a.add_mos = {{image=entry.image, display_h=2, display_y=-1}}
	equal(Tokens.identify(a), tall_aa[id] and id or nil, "batch AA tall body accepted only for native_tall entries "..id)
	if tall_aa[id] then
		a.add_mos = {{image=entry.image, display_h=2, display_y=-1}, {image="npc/other.png"}}
		equal(Tokens.identify(a), nil, "batch AA tall body with a second overlay stays native "..id)
		a.add_mos = {{image="npc/other.png", display_h=2, display_y=-1}}
		equal(Tokens.identify(a), nil, "batch AA tall body naming another PNG stays native "..id)
		a.add_mos = {{image=entry.image, display_h=2, display_y=-1, shader="x"}}
		equal(Tokens.identify(a), nil, "batch AA tall body with extra keys stays native "..id)
		a.add_mos = {{image=entry.image, display_h=3, display_y=-1}}
		equal(Tokens.identify(a), nil, "batch AA tall body with other dimensions stays native "..id)
		a.add_mos = {{image=entry.image, display_h=2, display_y=-1}, {_isshaderaura=true, image="shockbolt/aura.png"}}
		equal(Tokens.identify(a), id, "batch AA tall body with shader aura bookkeeping "..id)
		-- Single image (nicer_tiles off): the flat native image is accepted too.
		a = actor(entry)
		a.image, a.add_mos = entry.image, nil
		equal(Tokens.identify(a), id, "batch AA single native image with nicer_tiles off "..id)
	end
	a = actor(entry)
	a.type = entry.type == "undead" and "humanoid" or "undead"
	equal(Tokens.identify(a), nil, "batch AA type changed "..id)
	a = actor(entry)
	a.subtype = "other-subtype"
	equal(Tokens.identify(a), nil, "batch AA subtype changed "..id)
	a = actor(entry)
	a.shader = "some_shader"
	equal(Tokens.identify(a), nil, "batch AA shader keeps native art "..id)
	a = actor(entry)
	a.moddable_tile = "some_doll"
	equal(Tokens.identify(a), nil, "batch AA paper-doll actor keeps native art "..id)
	a = actor(entry)
	a.anim = {}
	equal(Tokens.identify(a), nil, "batch AA animation keeps native art "..id)
	a = actor(entry)
	a.add_displays = {{image="npc/iceblock.png"}}
	equal(Tokens.identify(a), nil, "batch AA frozen/pinned add_displays keep native art "..id)
	a = actor(entry)
	a.unique = true
	equal(Tokens.identify(a), nil, "batch AA non-unique entry rejects an unknown unique "..id)
	a = actor(entry)
	a.define_as = "SOME_DEFINE_AS"
	equal(Tokens.identify(a), nil, "batch AA unexpected define_as "..id)
	if defines_aa[id] then
		a = actor(entry)
		a.define_as = nil
		equal(Tokens.identify(a), nil, "batch AA bound entry needs its define_as "..id)
	end
	a = actor(entry)
	a.image = "npc/some_other_image.png"
	equal(Tokens.identify(a), nil, "batch AA other image keeps native art "..id)
	a = actor(entry)
	a.__old_type = {entry.type, entry.subtype}
	a.type, a.subtype = "demon", "major"
	a.sustain_talents = {T_FLAME_OF_URH_ROK = {}}
	-- A demon/major entry already is that body, so the sentinel changes nothing; every other body must stay native.
	equal(Tokens.identify(a), entry.type == "demon" and id or nil, "batch AA Flame of Urh'Rok form is not supported "..id)
	a = actor(entry)
	a.add_mos = {{_isshaderaura=true, image="shockbolt/aura.png"}}
	equal(Tokens.identify(a), id, "batch AA shader aura entry is ignored "..id)
	-- No variants or aliases: a summon shape carrying a wild-summon rename or another PNG stays native.
	a = actor(entry)
	a.summoner, a.ai, a.wild_gift_summon = {}, "summoned", true
	equal(Tokens.identify(a), id, "batch AA a same-body summon is the same exact leaf "..id)
	a.name = entry.name.." (wild summon)"
	equal(Tokens.identify(a), nil, "batch AA the wild-summon rename is not covered "..id)
	a = actor(entry)
	a.summoner, a.ai, a.summoner_gain_exp, a.wild_gift_summon = {}, "summoned", true, true
	a.image = "npc/summoner_ritch.png"
	equal(Tokens.identify(a), nil, "batch AA no summon PNG alias "..id)
end
-- Birth sustains are temporary values, shields and particles only.
for id, talents in pairs({["ultimate-faeros"]={"T_FIERY_HANDS"}, ["orc-berserker"]={"T_BERSERKER"}, ["ultimate-teluvorta"]={"T_REALITY_SMEARING"},
	["bone-horror"]={"T_BONE_SHIELD"}, ["sanguine-horror"]={"T_BLOOD_FURY"}, ["dreadmaster"]={"T_BLUR_SIGHT"}}) do
	local a = actor(Tokens.by_id[id])
	a.sustain_talents = {}
	for _, tid in ipairs(talents) do a.sustain_talents[tid] = {} end
	a.__particles = {{}}
	a.resists = {COLD=50}
	a.stealth = 30
	equal(Tokens.identify(a), id, "batch AA birth sustain keeps the body "..id)
end
-- The Necromancer Dread talent minion and the dreadmaster's own Summon: same name, type, subtype and image; they wear the token.
do
	local entry = Tokens.by_id["dreadmaster"]
	local a = actor(entry)
	a.summoner, a.ai, a.exp_worth = {faction="players"}, "summoned", 0
	a.dread_minion, a.no_boneyard_resurrect, a.summoner_gain_exp = "dread", true, true
	equal(Tokens.identify(a), "dreadmaster", "batch AA Dread-talent dreadmaster minion wears the dreadmaster token")
	a = actor(Tokens.by_id["dread"])
	a.summoner, a.ai, a.exp_worth = {}, "summoned", 0
	equal(Tokens.identify(a), "dread", "batch AA the dreadmaster's summoned dread keeps the dread token")
	a.name = "dreadmaster"
	equal(Tokens.identify(a), nil, "batch AA a dreadmaster on the dread PNG stays native")
	a = actor(entry)
	a.name = "dread"
	equal(Tokens.identify(a), nil, "batch AA a dread on the dreadmaster PNG stays native")
end
-- The elite berserker (define_as ORC_ELITE_BERSERKER, mapped by batch AB) and the plain berserker are different leaves; a berserker escort stays exact.
do
	local a = actor(Tokens.by_id["orc-berserker"])
	a.name, a.define_as = "orc elite berserker", "ORC_ELITE_BERSERKER"
	equal(Tokens.identify(a), nil, "batch AA an orc berserker body cannot wear the elite berserker name (batch AB maps the elite leaf on its own PNG)")
	a = actor(Tokens.by_id["orc-berserker"])
	a.summoner, a.ai = {}, "summoned"
	equal(Tokens.identify(a), "orc-berserker", "batch AA a summoned orc berserker wears the berserker token")
end
-- The dredge captain's escort and the summons of the horrors build other exact leaves; each wears its own token.
do
	for _, id in ipairs({"dredge", "ghoul", "skeleton-warrior"}) do
		local entry = Tokens.by_id[id]
		if entry then
			local a = actor(entry)
			a.summoner, a.ai = {}, "summoned"
			equal(Tokens.identify(a), id, "batch AA a summoned copy wears its own token "..id)
		end
	end
end
-- A random boss made from a non-unique native-tall entry keeps native art (only unique tall bodies qualify).
for _, id in ipairs({"bone-horror", "ultimate-faeros", "sanguine-horror"}) do
	local entry = Tokens.by_id[id]
	local base = actor(entry)
	base.image, base.add_mos = "invis.png", {{image=entry.image, display_h=2, display_y=-1}}
	local capture = Tokens.captureRandomOrigin(base)
	local boss = actor(entry)
	boss.image, boss.add_mos = "invis.png", {{image=entry.image, display_h=2, display_y=-1}}
	boss.name, boss.define_as, boss.unique, boss.randboss = "Vault Boss Test", "RANDOM_BOSS_AA", "Vault Boss Test", true, true
	equal(Tokens.recordRandomOrigin(boss, capture, "RANDOM_BOSS_AA"), nil, "batch AA non-unique tall random boss stays native "..id)
	equal(Tokens.identify(boss), nil, "batch AA non-unique tall random boss identify "..id)
end
-- A random boss made from a flat entry keeps that token.
do
	local entry = Tokens.by_id["orc-berserker"]
	local capture = Tokens.captureRandomOrigin(actor(entry))
	local boss = actor(entry)
	boss.name, boss.define_as, boss.unique, boss.randboss = "Berserker Test", "RANDOM_BOSS_AAF", "Berserker Test", true
	equal(Tokens.recordRandomOrigin(boss, capture, "RANDOM_BOSS_AAF"), "orc-berserker", "batch AA flat random boss keeps the orc berserker token")
	equal(Tokens.identify(boss), "orc-berserker", "batch AA flat random boss identify")
end
-- The new bodies cannot borrow their siblings' names or images.
for _, group in ipairs({{"ultimate-faeros", "faeros", "greater-faeros", "fyrk"}, {"orc-berserker", "orc-fighter", "orc-soldier", "orc-warrior", "orc-assassin"},
	{"dredge-captain", "dredge", "dredgling"}, {"polar-bear", "brown-bear", "black-bear", "cave-bear", "war-bear", "grizzly-bear"},
	{"anaconda", "brown-snake", "king-cobra", "black-mamba", "rattlesnake", "white-snake"},
	{"ultimate-teluvorta", "teluvorta", "greater-teluvorta", "ultimate-telugoroth", "greater-telugoroth"},
	{"necrotic-abomination", "bone-horror", "sanguine-horror", "necrotic-mass", "fleshy-experiment", "boney-experiment", "sanguine-experiment"},
	{"barrow-wight", "forest-wight", "grave-wight"}, {"ogre-warmaster", "ogre-guard", "ogre-mauler", "ogre-pounder"}, {"dreadmaster", "dread", "banshee"}}) do
	for _, id in ipairs(group) do
		for _, other in ipairs(group) do
			if id ~= other and Tokens.by_id[id] and Tokens.by_id[other] then
				local a = actor(Tokens.by_id[id])
				a.image = Tokens.by_id[other].image
				if Tokens.by_id[id].image ~= Tokens.by_id[other].image then
					equal(Tokens.identify(a), nil, "batch AA sibling cannot borrow image "..id.." <- "..other)
				end
				a = actor(Tokens.by_id[id])
				a.name = Tokens.by_id[other].name
				equal(Tokens.identify(a), nil, "batch AA body cannot wear another sibling's name "..id.." as "..other)
			end
		end
	end
end
-- Look-alikes stay native (other names on the same PNGs, neighbours that were not selected).
for _, excluded in ipairs({
	{name="ultimate faeros", type="elemental", subtype="fire", image="invis.png", add_mos={{image="npc/elemental_fire_greater_faeros.png", display_h=2, display_y=-1}}},
	{name="greater faeros", type="elemental", subtype="fire", image="invis.png", add_mos={{image="npc/elemental_fire_ultimate_faeros.png", display_h=2, display_y=-1}}},
	{name="Fyrk, Faeros High Guard", type="elemental", subtype="fire", image="invis.png", define_as="FYRK", unique=true, add_mos={{image="npc/elemental_fire_ultimate_faeros.png", display_h=2, display_y=-1}}},
	{name="orc berserker", type="humanoid", subtype="orc", image="npc/humanoid_orc_orc_fighter.png"},
	{name="orc elite berserker", type="humanoid", subtype="orc", image="npc/humanoid_orc_orc_berserker.png", define_as="ORC_ELITE_BERSERKER"},
	{name="orc fighter", type="humanoid", subtype="orc", image="npc/humanoid_orc_orc_berserker.png"},
	{name="dredge captain", type="horror", subtype="temporal", image="npc/horror_temporal_dredge.png"},
	{name="dredge", type="horror", subtype="temporal", image="npc/horror_temporal_dredge_captain.png"},
	{name="polar bear", type="animal", subtype="bear", image="npc/cave_bear.png"},
	{name="cave bear", type="animal", subtype="bear", image="npc/polar_bear.png"},
	{name="Norgos, the Frozen", type="animal", subtype="bear", image="npc/polar_bear.png", define_as="FROZEN_NORGOS", unique=true},
	{name="anaconda", type="animal", subtype="snake", image="npc/green-snake.png"},
	{name="king cobra", type="animal", subtype="snake", image="npc/yellow-green-snake.png"},
	{name="ultimate teluvorta", type="elemental", subtype="temporal", image="invis.png", add_mos={{image="npc/elemental_temporal_greater_teluvorta.png", display_h=2, display_y=-1}}},
	{name="greater teluvorta", type="elemental", subtype="temporal", image="invis.png", add_mos={{image="npc/elemental_temporal_ultimate_teluvorta.png", display_h=2, display_y=-1}}},
	{name="necrotic abomination", type="undead", subtype="horror", image="invis.png", add_mos={{image="npc/undead_horror_necrotic_mass.png", display_h=2, display_y=-1}}},
	{name="necrotic mass", type="undead", subtype="horror", image="invis.png", add_mos={{image="npc/undead_horror_necrotic_abomination.png", display_h=2, display_y=-1}}},
	{name="bone horror", type="undead", subtype="horror", image="invis.png", add_mos={{image="npc/undead_horror_sanguine_horror.png", display_h=2, display_y=-1}}},
	{name="sanguine horror", type="undead", subtype="horror", image="invis.png", add_mos={{image="npc/undead_horror_bone_horror.png", display_h=2, display_y=-1}}},
	{name="sanguine horror", type="undead", subtype="blood", image="invis.png", add_mos={{image="npc/undead_horror_sanguine_horror.png", display_h=2, display_y=-1}}},
	{name="barrow wight", type="undead", subtype="wight", image="npc/grave_wight.png"},
	{name="emperor wight", type="undead", subtype="wight", image="invis.png", add_mos={{image="npc/barrow_wight.png", display_h=2, display_y=-1}}},
	{name="ogre warmaster", type="giant", subtype="ogre", image="invis.png", add_mos={{image="npc/giant_ogre_ogre_guard.png", display_h=2, display_y=-1}}},
	{name="ogre guard", type="giant", subtype="ogre", image="invis.png", add_mos={{image="npc/giant_ogre_ogre_warmaster.png", display_h=2, display_y=-1}}},
	{name="dreadmaster", type="undead", subtype="ghost", image="npc/dread.png"},
	{name="dreadmaster", type="undead", subtype="ghost", image="npc/dreadmaster.png", unique=true},
	{name="entrenched horror", type="horror", subtype="aquatic", image="invis.png", add_mos={{image="npc/horror_aquatic_abyssal_horror.png", display_h=2, display_y=-1}}},
}) do
	equal(Tokens.identify(excluded), nil, "batch AA look-alike stays native "..excluded.name.." "..tostring(excluded.define_as))
end


-- Batch AB: the twelve identities after batch AA (entrenched horror, orc
-- summoner, greater mummy, shadowblade, orc elite fighter, orc elite berserker,
-- boiling horror, venom wyrm, alchemist golem, swarm hive, Forest Troll
-- Hedge-Wizard, ultimate shivgoroth). Four bind a define_as (shadowblade,
-- orc elite fighter, orc elite berserker, greater mummy); five are non-unique
-- native-tall (native_tall=true); the Hedge-Wizard is a unique tall body
-- (unique=true, no native_tall flag); none can reach Flame of Urh'Rok, so there
-- is no opt-in.
local batch_ab = {"entrenched-horror", "orc-summoner", "greater-mummy", "shadowblade", "orc-elite-fighter", "orc-elite-berserker",
	"boiling-horror", "venom-wyrm", "alchemist-golem", "swarm-hive", "forest-troll-hedge-wizard", "ultimate-shivgoroth"}
local names_ab = {["entrenched-horror"]="entrenched horror", ["orc-summoner"]="orc summoner", ["greater-mummy"]="greater mummy", ["shadowblade"]="shadowblade",
	["orc-elite-fighter"]="orc elite fighter", ["orc-elite-berserker"]="orc elite berserker", ["boiling-horror"]="boiling horror", ["venom-wyrm"]="venom wyrm",
	["alchemist-golem"]="alchemist golem", ["swarm-hive"]="swarm hive", ["forest-troll-hedge-wizard"]="Forest Troll Hedge-Wizard", ["ultimate-shivgoroth"]="ultimate shivgoroth"}
local defines_ab = {["greater-mummy"]="GREATER_MUMMY", ["shadowblade"]="THIEF_ASSASSIN", ["orc-elite-fighter"]="ORC_ELITE_FIGHTER", ["orc-elite-berserker"]="ORC_ELITE_BERSERKER"}
local tall_ab = {["entrenched-horror"]=true, ["boiling-horror"]=true, ["venom-wyrm"]=true, ["swarm-hive"]=true, ["ultimate-shivgoroth"]=true}
local unique_ab = {["forest-troll-hedge-wizard"]=true}
for _, id in ipairs(batch_ab) do
	local entry = Tokens.by_id[id]
	if entry == nil then error("batch AB catalog entry missing: "..id) end
	local tall = tall_ab[id] or unique_ab[id]
	equal(entry.name, names_ab[id], "batch AB exact name "..id)
	equal(entry.define_as, defines_ab[id], "batch AB define_as binding "..id)
	equal(entry.unique, unique_ab[id], "batch AB unique flag "..id)
	equal(entry.native_tall, tall_ab[id] and true or nil, "batch AB native_tall flag "..id)
	equal(entry.urh_rok_form, nil, "batch AB no urh_rok_form flag "..id)
	equal(Tokens.identify(actor(entry)), id, "batch AB exact identity "..id)
	local a = actor(entry)
	a.tint_r, a.tint_g, a.tint_b = 0, 0, 0
	equal(Tokens.identify(a), id, "batch AB tint is colour only "..id)
	a = actor(entry)
	a.color_r, a.color_g, a.color_b = 0, 0, 185
	equal(Tokens.identify(a), id, "batch AB colour modulation keeps the token "..id)
	a = actor(entry)
	a.image = "invis.png"
	a.add_mos = {{image=entry.image, display_h=2, display_y=-1}}
	equal(Tokens.identify(a), tall and id or nil, "batch AB tall body accepted only for tall entries "..id)
	if tall then
		a.add_mos = {{image=entry.image, display_h=2, display_y=-1}, {image="npc/other.png"}}
		equal(Tokens.identify(a), nil, "batch AB tall body with a second overlay stays native "..id)
		a.add_mos = {{image="npc/other.png", display_h=2, display_y=-1}}
		equal(Tokens.identify(a), nil, "batch AB tall body naming another PNG stays native "..id)
		a.add_mos = {{image=entry.image, display_h=2, display_y=-1, shader="x"}}
		equal(Tokens.identify(a), nil, "batch AB tall body with extra keys stays native "..id)
		a.add_mos = {{image=entry.image, display_h=3, display_y=-1}}
		equal(Tokens.identify(a), nil, "batch AB tall body with other dimensions stays native "..id)
		a.add_mos = {{image=entry.image, display_h=2, display_y=-1}, {_isshaderaura=true, image="shockbolt/aura.png"}}
		equal(Tokens.identify(a), id, "batch AB tall body with shader aura bookkeeping "..id)
		a.add_mos = {{_isshaderaura=true, image="shockbolt/aura.png"}, {image=entry.image, display_h=2, display_y=-1}}
		equal(Tokens.identify(a), id, "batch AB tall body with shader aura bookkeeping first "..id)
		-- Single image (nicer_tiles off): the flat native image is accepted too.
		a = actor(entry)
		a.image, a.add_mos = entry.image, nil
		equal(Tokens.identify(a), id, "batch AB single native image with nicer_tiles off "..id)
	end
	a = actor(entry)
	a.type = entry.type == "undead" and "humanoid" or "undead"
	equal(Tokens.identify(a), nil, "batch AB type changed "..id)
	a = actor(entry)
	a.subtype = "other-subtype"
	equal(Tokens.identify(a), nil, "batch AB subtype changed "..id)
	a = actor(entry)
	a.shader = "some_shader"
	equal(Tokens.identify(a), nil, "batch AB shader keeps native art "..id)
	a = actor(entry)
	a.moddable_tile = "some_doll"
	equal(Tokens.identify(a), nil, "batch AB paper-doll actor keeps native art "..id)
	a = actor(entry)
	a.anim = {}
	equal(Tokens.identify(a), nil, "batch AB animation keeps native art "..id)
	a = actor(entry)
	a.add_displays = {{image="npc/iceblock.png"}}
	equal(Tokens.identify(a), nil, "batch AB frozen/pinned add_displays keep native art "..id)
	if not entry.unique then
		a = actor(entry)
		a.unique = true
		equal(Tokens.identify(a), nil, "batch AB non-unique entry rejects an unknown unique "..id)
	end
	a = actor(entry)
	a.define_as = "SOME_DEFINE_AS"
	equal(Tokens.identify(a), nil, "batch AB unexpected define_as "..id)
	if defines_ab[id] then
		a = actor(entry)
		a.define_as = nil
		equal(Tokens.identify(a), nil, "batch AB bound entry needs its define_as "..id)
	end
	a = actor(entry)
	a.image = "npc/some_other_image.png"
	equal(Tokens.identify(a), nil, "batch AB other image keeps native art "..id)
	a = actor(entry)
	a.__old_type = {entry.type, entry.subtype}
	a.type, a.subtype = "demon", "major"
	a.sustain_talents = {T_FLAME_OF_URH_ROK = {}}
	equal(Tokens.identify(a), nil, "batch AB Flame of Urh'Rok form is not supported "..id)
	a = actor(entry)
	a.add_mos = {{_isshaderaura=true, image="shockbolt/aura.png"}}
	equal(Tokens.identify(a), id, "batch AB shader aura entry is ignored "..id)
	-- No variants or aliases: a summon shape carrying a wild-summon rename or another PNG stays native.
	a = actor(entry)
	a.summoner, a.ai, a.wild_gift_summon = {}, "summoned", true
	equal(Tokens.identify(a), id, "batch AB a same-body summon shape is the same exact leaf "..id)
	a.name = entry.name.." (wild summon)"
	equal(Tokens.identify(a), nil, "batch AB the wild-summon rename is not covered "..id)
	a = actor(entry)
	a.summoner, a.ai, a.summoner_gain_exp, a.wild_gift_summon = {}, "summoned", true, true
	a.image = "npc/summoner_ritch.png"
	equal(Tokens.identify(a), nil, "batch AB no summon PNG alias "..id)
end
-- Birth sustains are temporary values, shields and particles only (Burning Wake adds native shader-aura bookkeeping).
for id, talents in pairs({["boiling-horror"]={"T_THERMAL_AURA", "T_BURNING_WAKE"}, ["orc-summoner"]={"T_PSIBLADES"}, ["orc-elite-fighter"]={"T_SHIELD_WALL"},
	["orc-elite-berserker"]={"T_BERSERKER", "T_JUGGERNAUT"}, ["shadowblade"]={"T_STEALTH", "T_SHADOW_COMBAT"}}) do
	local a = actor(Tokens.by_id[id])
	a.sustain_talents = {}
	for _, tid in ipairs(talents) do a.sustain_talents[tid] = {} end
	a.__particles = {{}}
	a.resists = {COLD=50}
	a.stealth = 30
	equal(Tokens.identify(a), id, "batch AB birth sustain keeps the body "..id)
end
do
	local entry = Tokens.by_id["boiling-horror"]
	local a = actor(entry)
	a.image = "invis.png"
	a.shader_auras = {burning_wake={shader="awesomeaura"}}
	a.add_mos = {{_isshaderaura=true, image="particles_images/wings.png"}, {image=entry.image, display_h=2, display_y=-1}}
	equal(Tokens.identify(a), "boiling-horror", "batch AB Burning Wake aura around the tall body keeps the token")
end
-- Shadowblade and assassin share define_as THIEF_ASSASSIN but each is bound to its own name and PNG; the arena's unrelated shadowblade has no define_as.
do
	local a = actor(Tokens.by_id["shadowblade"])
	a.name = "assassin"
	equal(Tokens.identify(a), nil, "batch AB a shadowblade body cannot wear the assassin name")
	a = actor(Tokens.by_id["assassin"])
	a.name = "shadowblade"
	equal(Tokens.identify(a), nil, "batch AB an assassin body cannot wear the shadowblade name")
	a = actor(Tokens.by_id["shadowblade"])
	a.define_as = nil
	equal(Tokens.identify(a), nil, "batch AB the arena shadowblade (no define_as) stays native")
	a.define_as = "THIEF_SAPPER"
	equal(Tokens.identify(a), nil, "batch AB a shadowblade bound to THIEF_SAPPER stays native")
	a = actor(Tokens.by_id["rogue-sapper"])
	a.name = "shadowblade"
	equal(Tokens.identify(a), nil, "batch AB a sapper body cannot wear the shadowblade name")
end
-- The elite orcs are define_as-bound leaves of their own; the plain fighter and berserker keep their tokens and cannot swap.
do
	local pairs_ab = {{"orc-elite-fighter", "orc-fighter"}, {"orc-elite-berserker", "orc-berserker"}, {"orc-elite-fighter", "orc-elite-berserker"}}
	for _, pair in ipairs(pairs_ab) do
		local x, y = Tokens.by_id[pair[1]], Tokens.by_id[pair[2]]
		local a = actor(x)
		a.name, a.define_as = y.name, y.define_as
		equal(Tokens.identify(a), nil, "batch AB "..x.id.." body cannot wear the "..y.id.." name")
		a = actor(y)
		a.name, a.define_as = x.name, x.define_as
		equal(Tokens.identify(a), nil, "batch AB "..y.id.." body cannot wear the "..x.id.." name")
		a = actor(x)
		a.image = y.image
		equal(Tokens.identify(a), nil, "batch AB "..x.id.." cannot borrow the "..y.id.." PNG")
	end
	local a = actor(Tokens.by_id["orc-elite-fighter"])
	a.summoner, a.ai = {}, "summoned"
	equal(Tokens.identify(a), "orc-elite-fighter", "batch AB a summoned elite fighter wears the elite fighter token")
end
-- The greater mummy and the greater mummy lord are different leaves with different PNGs and define_as values.
do
	local a = actor(Tokens.by_id["greater-mummy"])
	a.define_as = "GREATER_MUMMY_LORD"
	equal(Tokens.identify(a), nil, "batch AB a greater mummy bound to the lord's define_as stays native")
	a = actor(Tokens.by_id["greater-mummy-lord"])
	a.name = "greater mummy"
	equal(Tokens.identify(a), nil, "batch AB a lord body cannot wear the greater mummy name")
	a = actor(Tokens.by_id["greater-mummy"])
	a.name = "greater mummy lord"
	equal(Tokens.identify(a), nil, "batch AB a greater mummy body cannot wear the lord name")
end
-- The player's alchemist golem uses the name golem, another PNG and a paper doll; the alchemist golem NPC keeps only its own name and PNG.
do
	local a = actor(Tokens.by_id["golem"])
	a.image, a.moddable_tile = "npc/alchemist_golem.png", "runic_golem"
	equal(Tokens.identify(a), nil, "batch AB the player's alchemist golem stays native")
	a = actor(Tokens.by_id["alchemist-golem"])
	a.name = "golem"
	equal(Tokens.identify(a), nil, "batch AB an alchemist golem PNG named golem stays native")
	a = actor(Tokens.by_id["golem"])
	a.name = "alchemist golem"
	equal(Tokens.identify(a), nil, "batch AB a golem PNG named alchemist golem stays native")
end
-- The swarm hive's swarming horror summon keeps the batch Z token.
do
	local a = actor(Tokens.by_id["swarming-horror"])
	a.image, a.add_mos = "invis.png", {{image=Tokens.by_id["swarming-horror"].image, display_h=2, display_y=-1}}
	a.summoner, a.ai, a.exp_worth = {}, "summoned", 0
	equal(Tokens.identify(a), "swarming-horror", "batch AB a hive-summoned swarming horror wears its own token")
end
-- A random boss made from a non-unique native-tall entry keeps native art; one made from a flat entry (including a define_as-bound elite orc) keeps that token.
for _, id in ipairs({"venom-wyrm", "boiling-horror", "entrenched-horror"}) do
	local entry = Tokens.by_id[id]
	local base = actor(entry)
	base.image, base.add_mos = "invis.png", {{image=entry.image, display_h=2, display_y=-1}}
	local capture = Tokens.captureRandomOrigin(base)
	local boss = actor(entry)
	boss.image, boss.add_mos = "invis.png", {{image=entry.image, display_h=2, display_y=-1}}
	boss.name, boss.define_as, boss.unique, boss.randboss = "Vault Boss Test", "RANDOM_BOSS_AB", "Vault Boss Test", true
	equal(Tokens.recordRandomOrigin(boss, capture, "RANDOM_BOSS_AB"), nil, "batch AB non-unique tall random boss stays native "..id)
	equal(Tokens.identify(boss), nil, "batch AB non-unique tall random boss identify "..id)
end
for _, id in ipairs({"orc-elite-fighter", "orc-elite-berserker", "orc-summoner", "shadowblade"}) do
	local entry = Tokens.by_id[id]
	local capture = Tokens.captureRandomOrigin(actor(entry))
	local boss = actor(entry)
	boss.name, boss.define_as, boss.unique, boss.randboss = "Berserker Test "..id, "RANDOM_BOSS_ABF", "Berserker Test "..id, true
	equal(Tokens.recordRandomOrigin(boss, capture, "RANDOM_BOSS_ABF"), id, "batch AB flat random boss keeps the token "..id)
	equal(Tokens.identify(boss), id, "batch AB flat random boss identify "..id)
end
-- The new bodies cannot borrow their siblings' names or images.
for _, group in ipairs({{"orc-elite-fighter", "orc-elite-berserker", "orc-fighter", "orc-berserker", "orc-soldier", "orc-warrior", "orc-assassin"},
	{"orc-summoner", "orc-corruptor", "orc-necromancer", "orc-pyromancer", "orc-cryomancer", "orc-blood-mage"},
	{"greater-mummy", "greater-mummy-lord", "rotting-mummy", "ancient-elven-mummy", "animated-mummy-wrappings"},
	{"shadowblade", "assassin", "rogue", "thief", "rogue-sapper", "cutpurse"},
	{"entrenched-horror", "boiling-horror", "swarm-hive", "swarming-horror", "ravenous-horror", "bloated-horror"},
	{"venom-wyrm", "fire-wyrm", "venom-drake", "fire-drake", "cold-drake"},
	{"alchemist-golem", "golem", "broken-golem"},
	{"ultimate-shivgoroth", "greater-shivgoroth", "shivgoroth"},
	{"forest-troll-hedge-wizard", "forest-troll", "cave-troll", "stone-troll", "mountain-troll"}}) do
	for _, id in ipairs(group) do
		for _, other in ipairs(group) do
			if id ~= other and Tokens.by_id[id] and Tokens.by_id[other] then
				local a = actor(Tokens.by_id[id])
				a.image = Tokens.by_id[other].image
				if Tokens.by_id[id].image ~= Tokens.by_id[other].image then
					equal(Tokens.identify(a), nil, "batch AB sibling cannot borrow image "..id.." <- "..other)
				end
				a = actor(Tokens.by_id[id])
				a.name = Tokens.by_id[other].name
				equal(Tokens.identify(a), nil, "batch AB body cannot wear another sibling's name "..id.." as "..other)
				a = actor(Tokens.by_id[id])
				a.image, a.add_mos = "invis.png", {{image=Tokens.by_id[other].image, display_h=2, display_y=-1}}
				equal(Tokens.identify(a), nil, "batch AB body cannot wear another sibling's tall PNG "..id.." <- "..other)
			end
		end
	end
end
-- Look-alikes stay native (other names on the same PNGs, neighbours that were not selected).
for _, excluded in ipairs({
	{name="entrenched horror", type="horror", subtype="aquatic", image="invis.png", add_mos={{image="npc/horror_aquatic_boiling_horror.png", display_h=2, display_y=-1}}},
	{name="boiling horror", type="horror", subtype="aquatic", image="invis.png", add_mos={{image="npc/horror_aquatic_entrenched_horror.png", display_h=2, display_y=-1}}},
	{name="swarm hive", type="horror", subtype="aquatic", image="invis.png", add_mos={{image="npc/horror_aquatic_swarming_horror.png", display_h=2, display_y=-1}}},
	{name="swarming horror", type="horror", subtype="aquatic", image="invis.png", add_mos={{image="npc/horror_aquatic_swarm_hive.png", display_h=2, display_y=-1}}},
	-- (the abyssal horror was kept native here; batch AC maps it as native-tall.)
	{name="venom wyrm", type="dragon", subtype="venom", image="npc/dragon_venom_venom_drake.png"},
	{name="venom drake", type="dragon", subtype="venom", image="invis.png", add_mos={{image="npc/dragon_venom_venom_wyrm.png", display_h=2, display_y=-1}}},
	{name="venom wyrm", type="dragon", subtype="fire", image="invis.png", add_mos={{image="npc/dragon_venom_venom_wyrm.png", display_h=2, display_y=-1}}},
	{name="ultimate shivgoroth", type="elemental", subtype="ice", image="invis.png", add_mos={{image="npc/elemental_ice_greater_shivgoroth.png", display_h=2, display_y=-1}}},
	{name="greater shivgoroth", type="elemental", subtype="ice", image="invis.png", add_mos={{image="npc/elemental_ice_ultimate_shivgoroth.png", display_h=2, display_y=-1}}},
	{name="Forest Troll Hedge-Wizard", type="giant", subtype="troll", image="npc/troll_f.png", unique=true},
	{name="Forest Troll Hedge-Wizard", type="giant", subtype="troll", image="invis.png", unique=true, define_as="OTHER", add_mos={{image="npc/giant_troll_forest_troll_hedge_wizard.png", display_h=2, display_y=-1}}},
	{name="Forest Troll Hedge-Wizard", type="giant", subtype="troll", image="invis.png", unique=true, add_mos={{image="npc/giant_troll_forest_troll_hedge_wizard.png", display_h=2, display_y=-1}, {image="npc/other.png"}}},
	{name="forest troll", type="giant", subtype="troll", image="invis.png", add_mos={{image="npc/giant_troll_forest_troll_hedge_wizard.png", display_h=2, display_y=-1}}},
	{name="orc elite fighter", type="humanoid", subtype="orc", image="npc/humanoid_orc_orc_elite_fighter.png"},
	{name="orc elite fighter", type="humanoid", subtype="orc", image="npc/humanoid_orc_orc_elite_fighter.png", define_as="ORC_ELITE_BERSERKER"},
	{name="orc elite berserker", type="humanoid", subtype="orc", image="npc/humanoid_orc_orc_elite_berserker.png"},
	{name="orc fighter", type="humanoid", subtype="orc", image="npc/humanoid_orc_orc_elite_fighter.png", define_as="HILL_ORC_FIGHTER"},
	{name="orc summoner", type="humanoid", subtype="orc", image="npc/humanoid_orc_orc_grand_summoner.png"},
	{name="orc grand summoner", type="humanoid", subtype="orc", image="npc/humanoid_orc_orc_summoner.png"},
	{name="greater mummy", type="undead", subtype="mummy", image="npc/undead_mummy_greater_mummy.png"},
	{name="greater mummy", type="undead", subtype="mummy", image="npc/undead_mummy_greater_mummy.png", define_as="GREATER_MUMMY_LORD"},
	{name="greater mummy lord", type="undead", subtype="mummy", image="npc/undead_mummy_greater_mummy.png", define_as="GREATER_MUMMY_LORD", unique=true},
	{name="shadowblade", type="humanoid", subtype="human", image="npc/humanoid_human_shadowblade.png"},
	{name="shadowblade", type="humanoid", subtype="human", image="npc/humanoid_human_shadowblade.png", define_as="THIEF_ASSASSIN", unique=true},
	{name="assassin", type="humanoid", subtype="human", image="npc/humanoid_human_shadowblade.png", define_as="THIEF_ASSASSIN"},
	{name="alchemist golem", type="construct", subtype="golem", image="npc/alchemist_golem.png"},
	{name="alchemist golem", type="construct", subtype="golem", image="npc/construct_golem_alchemist_golem.png", moddable_tile="runic_golem"},
	{name="golem", type="construct", subtype="golem", image="npc/construct_golem_alchemist_golem.png"},
	-- (the ruin banshee was kept native here; batch AC maps it.)
}) do
	equal(Tokens.identify(excluded), nil, "batch AB look-alike stays native "..excluded.name.." "..tostring(excluded.define_as))
end

-- Batch AC (the final batch): the seventeen identities that remain after batch
-- AB, everything except Training Dummy. Seven are uniques (Aletta Soultorn and
-- Filio Flightfond are flat define_as-bound bodies; Glacial Legion, Arch Zephyr,
-- Rotting Titan and Heavy Sentinel are define_as-bound tall bodies; Void
-- Spectre is a tall unique with no define_as). The five unique tall bodies
-- carry unique=true and no native_tall flag; four non-unique tall bodies
-- carry native_tall=true; none can reach Flame of Urh'Rok, so there is no opt-in.
local batch_ac = {"aletta-soultorn", "ruin-banshee", "filio-flightfond", "orc-high-pyromancer", "orc-high-cryomancer", "glacial-legion", "arch-zephyr",
	"rotting-titan", "heavy-sentinel", "void-spectre", "oozing-horror", "abyssal-horror", "ungolmor", "umbral-horror", "vampire-lord",
	"degenerated-ogric-mass", "ogric-abomination"}
local names_ac = {["aletta-soultorn"]="Aletta Soultorn", ["ruin-banshee"]="ruin banshee", ["filio-flightfond"]="Filio Flightfond",
	["orc-high-pyromancer"]="orc high pyromancer", ["orc-high-cryomancer"]="orc high cryomancer", ["glacial-legion"]="Glacial Legion",
	["arch-zephyr"]="Arch Zephyr", ["rotting-titan"]="Rotting Titan", ["heavy-sentinel"]="Heavy Sentinel", ["void-spectre"]="Void Spectre",
	["oozing-horror"]="oozing horror", ["abyssal-horror"]="abyssal horror", ["ungolmor"]="ungolmor", ["umbral-horror"]="umbral horror",
	["vampire-lord"]="vampire lord", ["degenerated-ogric-mass"]="degenerated ogric mass", ["ogric-abomination"]="ogric abomination"}
local defines_ac = {["aletta-soultorn"]="ALETTA", ["filio-flightfond"]="FILIO", ["glacial-legion"]="GLACIAL_LEGION", ["arch-zephyr"]="ARCH_ZEPHYR",
	["rotting-titan"]="ROTTING_TITAN", ["heavy-sentinel"]="HEAVY_SENTINEL"}
local unique_ac = {["aletta-soultorn"]=true, ["filio-flightfond"]=true, ["glacial-legion"]=true, ["arch-zephyr"]=true, ["rotting-titan"]=true,
	["heavy-sentinel"]=true, ["void-spectre"]=true}
local tall_ac = {["abyssal-horror"]=true, ["umbral-horror"]=true, ["degenerated-ogric-mass"]=true, ["ogric-abomination"]=true}
local unique_tall_ac = {["glacial-legion"]=true, ["arch-zephyr"]=true, ["rotting-titan"]=true, ["heavy-sentinel"]=true, ["void-spectre"]=true}
for _, id in ipairs(batch_ac) do
	local entry = Tokens.by_id[id]
	if entry == nil then error("batch AC catalog entry missing: "..id) end
	local tall = tall_ac[id] or unique_tall_ac[id]
	equal(entry.name, names_ac[id], "batch AC exact name "..id)
	equal(entry.define_as, defines_ac[id], "batch AC define_as binding "..id)
	equal(entry.unique, unique_ac[id], "batch AC unique flag "..id)
	equal(entry.native_tall, tall_ac[id] and true or nil, "batch AC native_tall flag "..id)
	equal(entry.urh_rok_form, nil, "batch AC no urh_rok_form flag "..id)
	equal(Tokens.identify(actor(entry)), id, "batch AC exact identity "..id)
	local a = actor(entry)
	a.tint_r, a.tint_g, a.tint_b = 0, 0, 0
	equal(Tokens.identify(a), id, "batch AC tint is colour only "..id)
	a = actor(entry)
	a.color_r, a.color_g, a.color_b = 0, 0, 185
	equal(Tokens.identify(a), id, "batch AC colour modulation keeps the token "..id)
	if tall or not unique_ac[id] then
		a = actor(entry)
		a.image = "invis.png"
		a.add_mos = {{image=entry.image, display_h=2, display_y=-1}}
		equal(Tokens.identify(a), tall and id or nil, "batch AC tall body accepted only for tall entries "..id)
	end
	if tall then
		a = actor(entry)
		a.image = "invis.png"
		a.add_mos = {{image=entry.image, display_h=2, display_y=-1}, {image="npc/other.png"}}
		equal(Tokens.identify(a), nil, "batch AC tall body with a second overlay stays native "..id)
		a.add_mos = {{image="npc/other.png", display_h=2, display_y=-1}}
		equal(Tokens.identify(a), nil, "batch AC tall body naming another PNG stays native "..id)
		a.add_mos = {{image=entry.image, display_h=2, display_y=-1, shader="x"}}
		equal(Tokens.identify(a), nil, "batch AC tall body with extra keys stays native "..id)
		a.add_mos = {{image=entry.image, display_h=3, display_y=-1}}
		equal(Tokens.identify(a), nil, "batch AC tall body with other dimensions stays native "..id)
		a.add_mos = {{image=entry.image, display_h=2, display_y=-1}, {_isshaderaura=true, image="shockbolt/aura.png"}}
		equal(Tokens.identify(a), id, "batch AC tall body with shader aura bookkeeping "..id)
		a.add_mos = {{_isshaderaura=true, image="shockbolt/aura.png"}, {image=entry.image, display_h=2, display_y=-1}}
		equal(Tokens.identify(a), id, "batch AC tall body with shader aura bookkeeping first "..id)
		-- Single image (nicer_tiles off): the flat native image is accepted too.
		a = actor(entry)
		a.image, a.add_mos = entry.image, nil
		equal(Tokens.identify(a), id, "batch AC single native image with nicer_tiles off "..id)
	end
	a = actor(entry)
	a.type = entry.type == "undead" and "humanoid" or "undead"
	equal(Tokens.identify(a), nil, "batch AC type changed "..id)
	a = actor(entry)
	a.subtype = "other-subtype"
	equal(Tokens.identify(a), nil, "batch AC subtype changed "..id)
	a = actor(entry)
	a.shader = "some_shader"
	equal(Tokens.identify(a), nil, "batch AC shader keeps native art "..id)
	a = actor(entry)
	a.moddable_tile = "some_doll"
	equal(Tokens.identify(a), nil, "batch AC paper-doll actor keeps native art "..id)
	a = actor(entry)
	a.anim = {}
	equal(Tokens.identify(a), nil, "batch AC animation keeps native art "..id)
	a = actor(entry)
	a.add_displays = {{image="npc/iceblock.png"}}
	equal(Tokens.identify(a), nil, "batch AC frozen/pinned add_displays keep native art "..id)
	if not entry.unique then
		a = actor(entry)
		a.unique = true
		equal(Tokens.identify(a), nil, "batch AC non-unique entry rejects an unknown unique "..id)
	end
	a = actor(entry)
	a.define_as = "SOME_DEFINE_AS"
	equal(Tokens.identify(a), nil, "batch AC unexpected define_as "..id)
	if defines_ac[id] then
		a = actor(entry)
		a.define_as = nil
		equal(Tokens.identify(a), nil, "batch AC bound entry needs its define_as "..id)
	end
	a = actor(entry)
	a.image = "npc/some_other_image.png"
	equal(Tokens.identify(a), nil, "batch AC other image keeps native art "..id)
	a = actor(entry)
	a.__old_type = {entry.type, entry.subtype}
	a.type, a.subtype = "demon", "major"
	a.sustain_talents = {T_FLAME_OF_URH_ROK = {}}
	equal(Tokens.identify(a), nil, "batch AC Flame of Urh'Rok form is not supported "..id)
	a = actor(entry)
	a.add_mos = {{_isshaderaura=true, image="shockbolt/aura.png"}}
	equal(Tokens.identify(a), id, "batch AC shader aura entry is ignored "..id)
	-- No variants or aliases: a summon shape carrying a wild-summon rename or another PNG stays native.
	a = actor(entry)
	a.summoner, a.ai, a.wild_gift_summon = {}, "summoned", true
	equal(Tokens.identify(a), id, "batch AC a same-body summon shape is the same exact leaf "..id)
	a.name = entry.name.." (wild summon)"
	equal(Tokens.identify(a), nil, "batch AC the wild-summon rename is not covered "..id)
	a = actor(entry)
	a.summoner, a.ai, a.summoner_gain_exp, a.wild_gift_summon = {}, "summoned", true, true
	a.image = "npc/summoner_ritch.png"
	equal(Tokens.identify(a), nil, "batch AC no summon PNG alias "..id)
end
-- Birth sustains are temporary values, shields and particles only (Burning Wake, Crystalline Focus and Golem Reflective Skin add native shader-aura bookkeeping).
for id, talents in pairs({["aletta-soultorn"]={"T_GLOOM"}, ["orc-high-pyromancer"]={"T_BURNING_WAKE", "T_SPELLCRAFT", "T_ESSENCE_OF_SPEED"},
	["orc-high-cryomancer"]={"T_SPELLCRAFT", "T_ESSENCE_OF_SPEED"}, ["glacial-legion"]={"T_UTTERCOLD", "T_SPELLCRAFT", "T_FROST_HANDS"},
	["arch-zephyr"]={"T_BLUR_SIGHT", "T_PHANTASMAL_SHIELD", "T_FEATHER_WIND", "T_THUNDERSTORM", "T_TEMPEST", "T_HURRICANE"},
	["rotting-titan"]={"T_CRYSTALLINE_FOCUS", "T_ONSLAUGHT"}, ["heavy-sentinel"]={"T_ARCANE_POWER", "T_BURNING_WAKE", "T_WILDFIRE", "T_ARCANE_COMBAT", "T_SPELLCRAFT", "T_FIERY_HANDS"},
	["void-spectre"]={"T_ARCANE_POWER", "T_SPELLCRAFT", "T_SHIELDING", "T_ARCANE_SHIELD", "T_PURE_AETHER"}, ["umbral-horror"]={"T_CALL_SHADOWS", "T_STEALTH"},
	["vampire-lord"]={"T_BLUR_SIGHT", "T_PHANTASMAL_SHIELD", "T_HIEMAL_SHIELD"}, ["ogric-abomination"]={"T_GOLEM_REFLECTIVE_SKIN"}}) do
	local a = actor(Tokens.by_id[id])
	a.sustain_talents = {}
	for _, tid in ipairs(talents) do a.sustain_talents[tid] = {} end
	a.__particles = {{}}
	a.resists = {COLD=50}
	a.stealth = 30
	equal(Tokens.identify(a), id, "batch AC birth sustain keeps the body "..id)
end
for id, aura in pairs({["heavy-sentinel"]="burning_wake", ["rotting-titan"]="stone_skin", ["ogric-abomination"]="reflective_skin"}) do
	local entry = Tokens.by_id[id]
	local a = actor(entry)
	a.image = "invis.png"
	a.shader_auras = {[aura]={shader="awesomeaura"}}
	a.add_mos = {{_isshaderaura=true, image="particles_images/wings.png"}, {image=entry.image, display_h=2, display_y=-1}}
	equal(Tokens.identify(a), id, "batch AC shader aura around the tall body keeps the token "..id)
end
-- The orc high casters are ordinary leaves with their own names and PNGs; the plain pyromancer and cryomancer keep their tokens and cannot swap.
do
	for _, pair in ipairs({{"orc-high-pyromancer", "orc-pyromancer"}, {"orc-high-cryomancer", "orc-cryomancer"}, {"orc-high-pyromancer", "orc-high-cryomancer"}}) do
		local x, y = Tokens.by_id[pair[1]], Tokens.by_id[pair[2]]
		local a = actor(x)
		a.name = y.name
		equal(Tokens.identify(a), nil, "batch AC "..x.id.." body cannot wear the "..y.id.." name")
		a = actor(y)
		a.name = x.name
		equal(Tokens.identify(a), nil, "batch AC "..y.id.." body cannot wear the "..x.id.." name")
		a = actor(x)
		a.image = y.image
		equal(Tokens.identify(a), nil, "batch AC "..x.id.." cannot borrow the "..y.id.." PNG")
	end
end
-- The unique bodies never wear another actor's token, and no non-listed unique borrows theirs.
for id in pairs(unique_ac) do
	local entry = Tokens.by_id[id]
	local a = actor(entry)
	a.name = "Some Other Unique"
	equal(Tokens.identify(a), nil, "batch AC an unknown unique on the "..id.." PNG stays native")
end
-- The Corpathus artifact's Vilespawn minion reuses the oozing horror PNG under its own name and stays native.
do
	local a = {name="Vilespawn", type="horror", subtype="eldritch", image="npc/horror_eldritch_oozing_horror.png", summoner={}, ai="summoned", faction="players"}
	equal(Tokens.identify(a), nil, "batch AC the Corpathus Vilespawn minion stays native")
end
-- Training Dummy is the only survey-2 candidate that stays unmapped.
equal(Tokens.identify({name="Training Dummy", type="training", subtype="dummy", image="npc/training_training_dummy.png", faction="enemies", rank=2}), nil, "batch AC Training Dummy stays native")
-- A random boss made from a non-unique native-tall entry keeps native art; one made from a flat entry keeps that token.
for _, id in ipairs({"abyssal-horror", "umbral-horror", "degenerated-ogric-mass", "ogric-abomination"}) do
	local entry = Tokens.by_id[id]
	local base = actor(entry)
	base.image, base.add_mos = "invis.png", {{image=entry.image, display_h=2, display_y=-1}}
	local capture = Tokens.captureRandomOrigin(base)
	local boss = actor(entry)
	boss.image, boss.add_mos = "invis.png", {{image=entry.image, display_h=2, display_y=-1}}
	boss.name, boss.define_as, boss.unique, boss.randboss = "Vault Boss Test", "RANDOM_BOSS_AC", "Vault Boss Test", true
	equal(Tokens.recordRandomOrigin(boss, capture, "RANDOM_BOSS_AC"), nil, "batch AC non-unique tall random boss stays native "..id)
	equal(Tokens.identify(boss), nil, "batch AC non-unique tall random boss identify "..id)
end
for _, id in ipairs({"orc-high-pyromancer", "orc-high-cryomancer", "ruin-banshee", "oozing-horror", "ungolmor", "vampire-lord"}) do
	local entry = Tokens.by_id[id]
	local capture = Tokens.captureRandomOrigin(actor(entry))
	local boss = actor(entry)
	boss.name, boss.define_as, boss.unique, boss.randboss = "Invoker Test "..id, "RANDOM_BOSS_ACF", "Invoker Test "..id, true
	equal(Tokens.recordRandomOrigin(boss, capture, "RANDOM_BOSS_ACF"), id, "batch AC flat random boss keeps the token "..id)
	equal(Tokens.identify(boss), id, "batch AC flat random boss identify "..id)
end
-- The new bodies cannot borrow their siblings' names or images.
for _, group in ipairs({{"orc-high-pyromancer", "orc-high-cryomancer", "orc-pyromancer", "orc-cryomancer", "orc-summoner", "orc-corruptor"},
	{"vampire-lord", "arch-zephyr", "vampire", "master-vampire", "elder-vampire", "lesser-vampire", "the-master"},
	{"aletta-soultorn", "ruin-banshee", "glacial-legion", "banshee", "dread", "dreadmaster", "kors-fury"},
	{"filio-flightfond", "skeleton-mage", "skeleton-magus", "skeleton-master-archer", "skeleton-warrior"},
	{"rotting-titan", "heavy-sentinel", "bone-giant", "heavy-bone-giant", "ghoul", "ghast", "ghoulking"},
	{"void-spectre", "forest-wight", "grave-wight", "barrow-wight"},
	{"oozing-horror", "abyssal-horror", "umbral-horror", "entrenched-horror", "bloated-horror", "green-ooze"},
	{"ungolmor", "giant-spider", "chitinous-spider", "ungole"},
	{"degenerated-ogric-mass", "ogric-abomination", "ogre-guard", "ogre-mauler", "ogre-pounder", "ogre-warmaster"}}) do
	for _, id in ipairs(group) do
		for _, other in ipairs(group) do
			if id ~= other and Tokens.by_id[id] and Tokens.by_id[other] then
				local a = actor(Tokens.by_id[id])
				a.image = Tokens.by_id[other].image
				if Tokens.by_id[id].image ~= Tokens.by_id[other].image then
					equal(Tokens.identify(a), nil, "batch AC sibling cannot borrow image "..id.." <- "..other)
				end
				a = actor(Tokens.by_id[id])
				a.name = Tokens.by_id[other].name
				equal(Tokens.identify(a), nil, "batch AC body cannot wear another sibling's name "..id.." as "..other)
				a = actor(Tokens.by_id[id])
				a.image, a.add_mos = "invis.png", {{image=Tokens.by_id[other].image, display_h=2, display_y=-1}}
				equal(Tokens.identify(a), nil, "batch AC body cannot wear another sibling's tall PNG "..id.." <- "..other)
			end
		end
	end
end
-- Look-alikes stay native (other names on the same PNGs, neighbours that were not selected).
for _, excluded in ipairs({
	{name="vampire lord", type="undead", subtype="vampire", image="npc/vampire.png"},
	{name="vampire", type="undead", subtype="vampire", image="npc/vampire_lord.png"},
	{name="vampire lord", type="undead", subtype="vampire", image="npc/vampire_lord.png", define_as="SOME_LORD"},
	{name="ruin banshee", type="undead", subtype="ghost", image="npc/banshee.png"},
	{name="banshee", type="undead", subtype="ghost", image="npc/undead_ghost_ruin_banshee.png"},
	{name="orc high pyromancer", type="humanoid", subtype="orc", image="npc/humanoid_orc_orc_pyromancer.png"},
	{name="orc pyromancer", type="humanoid", subtype="orc", image="npc/humanoid_orc_orc_high_pyromancer.png"},
	{name="orc high cryomancer", type="humanoid", subtype="orc", image="npc/humanoid_orc_orc_cryomancer.png"},
	{name="orc cryomancer", type="humanoid", subtype="orc", image="npc/humanoid_orc_orc_high_cryomancer.png"},
	{name="abyssal horror", type="horror", subtype="aquatic", image="invis.png", add_mos={{image="npc/horror_aquatic_entrenched_horror.png", display_h=2, display_y=-1}}},
	{name="entrenched horror", type="horror", subtype="aquatic", image="invis.png", add_mos={{image="npc/horror_aquatic_abyssal_horror.png", display_h=2, display_y=-1}}},
	{name="umbral horror", type="horror", subtype="eldritch", image="npc/horror_eldritch_bloated_horror.png"},
	{name="ungolmor", type="spiderkin", subtype="spider", image="npc/spiderkin_spider_ungole.png"},
	{name="Ungolë", type="spiderkin", subtype="spider", image="npc/spiderkin_spider_ungolmor.png", define_as="UNGOLE", unique=true},
	{name="Void Spectre", type="undead", subtype="wight", image="invis.png", unique=true, add_mos={{image="npc/undead_wight_barrow_wight.png", display_h=2, display_y=-1}}},
	{name="Void Spectre", type="undead", subtype="ghost", image="invis.png", unique=true, add_mos={{image="npc/undead_wight_void_spectre.png", display_h=2, display_y=-1}}},
	{name="Heavy Sentinel", type="undead", subtype="giant", image="invis.png", unique=true, define_as="HALF_BONE_GIANT", add_mos={{image="npc/undead_giant_heavy_sentinel.png", display_h=2, display_y=-1}}},
	{name="heavy bone giant", type="undead", subtype="giant", image="invis.png", add_mos={{image="npc/undead_giant_heavy_sentinel.png", display_h=2, display_y=-1}}},
	{name="Rotting Titan", type="undead", subtype="ghoul", image="npc/undead_ghoul_ghoul.png", unique=true, define_as="ROTTING_TITAN"},
	{name="ghoulking", type="undead", subtype="ghoul", image="invis.png", add_mos={{image="npc/undead_ghoul_rotting_titan.png", display_h=2, display_y=-1}}},
	{name="Arch Zephyr", type="undead", subtype="vampire", image="invis.png", unique=true, define_as="THE_MASTER", add_mos={{image="npc/undead_vampire_arch_zephyr.png", display_h=2, display_y=-1}}},
	{name="Glacial Legion", type="undead", subtype="ghost", image="npc/undead_ghost_aletta_soultorn.png", unique=true, define_as="GLACIAL_LEGION"},
	{name="Aletta Soultorn", type="undead", subtype="ghost", image="npc/undead_ghost_ruin_banshee.png", unique=true, define_as="ALETTA"},
	{name="Filio Flightfond", type="undead", subtype="skeleton", image="npc/skeleton_mage.png", unique=true, define_as="FILIO"},
	{name="skeleton mage", type="undead", subtype="skeleton", image="npc/undead_skeleton_filio_flightfond.png"},
	{name="oozing horror", type="horror", subtype="eldritch", image="npc/vermin_oozes_green_ooze.png"},
	{name="green ooze", type="vermin", subtype="oozes", image="npc/horror_eldritch_oozing_horror.png"},
	{name="degenerated ogric mass", type="giant", subtype="ogre", image="invis.png", add_mos={{image="npc/giant_ogre_ogric_abomination.png", display_h=2, display_y=-1}}},
	{name="ogric abomination", type="giant", subtype="ogre", image="invis.png", add_mos={{image="npc/giant_ogre_degenerated_ogric_mass.png", display_h=2, display_y=-1}}},
	{name="ogre pounder", type="giant", subtype="ogre", image="invis.png", add_mos={{image="npc/giant_ogre_ogric_abomination.png", display_h=2, display_y=-1}}},
}) do
	equal(Tokens.identify(excluded), nil, "batch AC look-alike stays native "..excluded.name.." "..tostring(excluded.define_as))
end

-- Batch AD (first off-list dungeon-pool batch): thirteen non-unique leaves, none
-- binding a define_as. Four are tall nice_tile bodies carrying native_tall=true
-- (duathedlen, daelach, ice wyrm, snow cat); nine are flat 64x64 default-name
-- images. None can reach Flame of Urh'Rok, so there is no opt-in, and none is
-- copied by a summon, so there is no variant or alias.
local batch_ad = {"duathedlen", "daelach", "orc-grand-summoner", "orc-master-wyrmic", "orc-mage-hunter", "ritch-larva", "ritch-hunter",
	"ritch-hive-mother-pool", "snow-cat", "panther", "tiger", "sabertooth-tiger", "ice-wyrm"}
local names_ad = {["duathedlen"]="d\195\186athedlen", ["daelach"]="daelach", ["orc-grand-summoner"]="orc grand summoner",
	["orc-master-wyrmic"]="orc master wyrmic", ["orc-mage-hunter"]="orc mage-hunter", ["ritch-larva"]="ritch larva", ["ritch-hunter"]="ritch hunter",
	["ritch-hive-mother-pool"]="ritch hive mother", ["snow-cat"]="snow cat", ["panther"]="panther", ["tiger"]="tiger",
	["sabertooth-tiger"]="sabertooth tiger", ["ice-wyrm"]="ice wyrm"}
local tall_ad = {["duathedlen"]=true, ["daelach"]=true, ["snow-cat"]=true, ["ice-wyrm"]=true}
equal(#batch_ad, 13, "batch AD has thirteen identities")
equal(#Tokens.catalog, 462, "the catalog holds 376 + 13 AD + 12 AE + 9 AF + 7 AG + 12 UA + 13 TA-1 + 9 UB-1 + 10 UB-2 + 1 UB-2 wiring identity")
for _, id in ipairs(batch_ad) do
	local entry = Tokens.by_id[id]
	if entry == nil then error("batch AD catalog entry missing: "..id) end
	local tall = tall_ad[id]
	equal(entry.name, names_ad[id], "batch AD exact name "..id)
	equal(entry.define_as, nil, "batch AD no define_as binding "..id)
	equal(entry.unique, nil, "batch AD non-unique "..id)
	equal(entry.native_tall, tall and true or nil, "batch AD native_tall flag "..id)
	equal(entry.urh_rok_form, nil, "batch AD no urh_rok_form flag "..id)
	equal(Tokens.identify(actor(entry)), id, "batch AD exact identity "..id)
	local a = actor(entry)
	a.tint_r, a.tint_g, a.tint_b = 0, 0, 0
	equal(Tokens.identify(a), id, "batch AD tint is colour only "..id)
	a = actor(entry)
	a.color_r, a.color_g, a.color_b = 0, 0, 185
	equal(Tokens.identify(a), id, "batch AD colour modulation keeps the token "..id)
	a = actor(entry)
	a.image = "invis.png"
	a.add_mos = {{image=entry.image, display_h=2, display_y=-1}}
	equal(Tokens.identify(a), tall and id or nil, "batch AD tall body accepted only for tall entries "..id)
	if tall then
		a = actor(entry)
		a.image = "invis.png"
		a.add_mos = {{image=entry.image, display_h=2, display_y=-1}, {image="npc/other.png"}}
		equal(Tokens.identify(a), nil, "batch AD tall body with a second overlay stays native "..id)
		a.add_mos = {{image="npc/other.png", display_h=2, display_y=-1}}
		equal(Tokens.identify(a), nil, "batch AD tall body naming another PNG stays native "..id)
		a.add_mos = {{image=entry.image, display_h=2, display_y=-1, shader="x"}}
		equal(Tokens.identify(a), nil, "batch AD tall body with extra keys stays native "..id)
		a.add_mos = {{image=entry.image, display_h=3, display_y=-1}}
		equal(Tokens.identify(a), nil, "batch AD tall body with other dimensions stays native "..id)
		a.add_mos = {{image=entry.image, display_h=2, display_y=-1}, {_isshaderaura=true, image="shockbolt/aura.png"}}
		equal(Tokens.identify(a), id, "batch AD tall body with shader aura bookkeeping "..id)
		a.add_mos = {{_isshaderaura=true, image="shockbolt/aura.png"}, {image=entry.image, display_h=2, display_y=-1}}
		equal(Tokens.identify(a), id, "batch AD tall body with shader aura bookkeeping first "..id)
		-- Single image (nicer_tiles off): the flat native image is accepted too.
		a = actor(entry)
		a.image, a.add_mos = entry.image, nil
		equal(Tokens.identify(a), id, "batch AD single native image with nicer_tiles off "..id)
	end
	a = actor(entry)
	a.type = entry.type == "undead" and "humanoid" or "undead"
	equal(Tokens.identify(a), nil, "batch AD type changed "..id)
	a = actor(entry)
	a.subtype = "other-subtype"
	equal(Tokens.identify(a), nil, "batch AD subtype changed "..id)
	a = actor(entry)
	a.shader = "some_shader"
	equal(Tokens.identify(a), nil, "batch AD shader keeps native art "..id)
	a = actor(entry)
	a.moddable_tile = "some_doll"
	equal(Tokens.identify(a), nil, "batch AD paper-doll actor keeps native art "..id)
	a = actor(entry)
	a.anim = {}
	equal(Tokens.identify(a), nil, "batch AD animation keeps native art "..id)
	a = actor(entry)
	a.add_displays = {{image="npc/iceblock.png"}}
	equal(Tokens.identify(a), nil, "batch AD frozen/pinned add_displays keep native art "..id)
	a = actor(entry)
	a.unique = true
	equal(Tokens.identify(a), nil, "batch AD non-unique entry rejects an unknown unique "..id)
	a = actor(entry)
	a.define_as = "SOME_DEFINE_AS"
	equal(Tokens.identify(a), nil, "batch AD unexpected define_as "..id)
	a = actor(entry)
	a.image = "npc/some_other_image.png"
	equal(Tokens.identify(a), nil, "batch AD other image keeps native art "..id)
	if entry.type ~= "demon" or entry.subtype ~= "major" then
		-- (the duathedlen and daelach already are demon/major: the form changes nothing for them)
		a = actor(entry)
		a.__old_type = {entry.type, entry.subtype}
		a.type, a.subtype = "demon", "major"
		a.sustain_talents = {T_FLAME_OF_URH_ROK = {}}
		equal(Tokens.identify(a), nil, "batch AD Flame of Urh'Rok form is not supported "..id)
	end
	a = actor(entry)
	a.add_mos = {{_isshaderaura=true, image="shockbolt/aura.png"}}
	equal(Tokens.identify(a), id, "batch AD shader aura entry is ignored "..id)
	-- No variants or aliases: a summon shape carrying a wild-summon rename or another PNG stays native.
	a = actor(entry)
	a.summoner, a.ai, a.wild_gift_summon = {}, "summoned", true
	equal(Tokens.identify(a), id, "batch AD a same-body summon shape is the same exact leaf "..id)
	a.name = entry.name.." (wild summon)"
	equal(Tokens.identify(a), nil, "batch AD the wild-summon rename is not covered "..id)
	a = actor(entry)
	a.summoner, a.ai, a.summoner_gain_exp, a.wild_gift_summon = {}, "summoned", true, true
	a.image = "npc/summoner_ritch.png"
	equal(Tokens.identify(a), nil, "batch AD no summon PNG alias "..id)
end
-- Birth sustains are temporary values, shields and particles only (Stealth of the felines, Psiblades, Icy Skin, Antimagic Shield).
for id, talents in pairs({["snow-cat"]={"T_STEALTH"}, ["panther"]={"T_STEALTH"}, ["tiger"]={"T_STEALTH"}, ["sabertooth-tiger"]={"T_STEALTH"},
	["orc-grand-summoner"]={"T_PSIBLADES"}, ["orc-master-wyrmic"]={"T_ICY_SKIN"}, ["orc-mage-hunter"]={"T_ANTIMAGIC_SHIELD"}, ["ice-wyrm"]={"T_ICY_SKIN"}}) do
	local a = actor(Tokens.by_id[id])
	a.sustain_talents = {}
	for _, tid in ipairs(talents) do a.sustain_talents[tid] = {} end
	a.__particles = {{}}
	a.resists = {COLD=50}
	a.stealth = 30
	equal(Tokens.identify(a), id, "batch AD birth sustain keeps the body "..id)
end
-- The ritch hive mother and the unique Ritch Great Hive Mother draw the same native PNG under different names:
-- each name keeps its own catalog id, and neither can wear the other's token or lose its define_as binding.
do
	local pool, unique = Tokens.by_id["ritch-hive-mother-pool"], Tokens.by_id["ritch-hive-mother"]
	equal(pool.image, unique.image, "batch AD the pool hive mother and the Great Hive Mother share the native PNG")
	equal(Tokens.identify(actor(pool)), "ritch-hive-mother-pool", "batch AD the pool hive mother keeps its id")
	equal(Tokens.identify(actor(unique)), "ritch-hive-mother", "batch AD the Great Hive Mother keeps its id")
	local a = actor(pool)
	a.define_as = unique.define_as
	equal(Tokens.identify(a), nil, "batch AD a hive mother bound to HIVE_MOTHER stays native")
	a = actor(unique)
	a.define_as = nil
	equal(Tokens.identify(a), nil, "batch AD the Great Hive Mother needs its define_as")
	a = actor(pool)
	a.name = unique.name
	equal(Tokens.identify(a), nil, "batch AD a pool hive mother cannot wear the Great Hive Mother name")
	a = actor(unique)
	a.name = pool.name
	equal(Tokens.identify(a), nil, "batch AD the Great Hive Mother cannot wear the pool name")
end
-- The duathedlen's name is not ASCII: with nicer_tiles off the engine's default-name image is the nonexistent
-- npc/demon_major_d__athedlen.png, which never equals the catalog image, so the token is not applied there.
do
	local entry = Tokens.by_id["duathedlen"]
	local a = actor(entry)
	a.image, a.add_mos = "npc/demon_major_d__athedlen.png", nil
	equal(Tokens.identify(a), nil, "batch AD duathedlen with the nicer_tiles-off default-name image stays native")
	a = actor(entry)
	a.name = "duathedlen"
	equal(Tokens.identify(a), nil, "batch AD an ASCII spelling of the name is another actor")
end
-- The Corrupted Daelach is now mapped (UB-1); it must still reject a borrowed
-- daelach body. The Arena's ice wyrmic is another name and stays native.
equal(Tokens.identify({name="Corrupted Daelach", type="demon", subtype="major", define_as="CORRUPTED_DAELACH", unique=true, image="invis.png",
	add_mos={{image="npc/demon_major_daelach.png", display_h=2, display_y=-1}}, faction="enemies"}), nil, "batch AD the Corrupted Daelach cannot borrow the daelach PNG")
-- A random boss made from a tall native-tall entry keeps native art; one made from a flat entry keeps that token.
for _, id in ipairs({"duathedlen", "daelach", "snow-cat", "ice-wyrm"}) do
	local entry = Tokens.by_id[id]
	local base = actor(entry)
	base.image, base.add_mos = "invis.png", {{image=entry.image, display_h=2, display_y=-1}}
	local capture = Tokens.captureRandomOrigin(base)
	local boss = actor(entry)
	boss.image, boss.add_mos = "invis.png", {{image=entry.image, display_h=2, display_y=-1}}
	boss.name, boss.define_as, boss.unique, boss.randboss = "Vault Boss Test", "RANDOM_BOSS_AD", "Vault Boss Test", true
	equal(Tokens.recordRandomOrigin(boss, capture, "RANDOM_BOSS_AD"), nil, "batch AD non-unique tall random boss stays native "..id)
	equal(Tokens.identify(boss), nil, "batch AD non-unique tall random boss identify "..id)
end
for _, id in ipairs({"orc-grand-summoner", "orc-master-wyrmic", "orc-mage-hunter", "ritch-larva", "ritch-hunter", "ritch-hive-mother-pool", "panther", "tiger", "sabertooth-tiger"}) do
	local entry = Tokens.by_id[id]
	local capture = Tokens.captureRandomOrigin(actor(entry))
	local boss = actor(entry)
	boss.name, boss.define_as, boss.unique, boss.randboss = "Herald Test "..id, "RANDOM_BOSS_ADF", "Herald Test "..id, true
	equal(Tokens.recordRandomOrigin(boss, capture, "RANDOM_BOSS_ADF"), id, "batch AD flat random boss keeps the token "..id)
	equal(Tokens.identify(boss), id, "batch AD flat random boss identify "..id)
end
-- The new bodies cannot borrow their siblings' names or images.
for _, group in ipairs({{"orc-grand-summoner", "orc-master-wyrmic", "orc-mage-hunter", "orc-summoner", "fiery-orc-wyrmic", "icy-orc-wyrmic", "orc-berserker", "orc-elite-fighter"},
	{"ritch-larva", "ritch-hunter", "ritch-hive-mother-pool", "ritch-hive-mother", "ritch-flamespitter", "ritch-impaler", "chitinous-ritch"},
	{"snow-cat", "panther", "tiger", "sabertooth-tiger", "pumpkin", "white-wolf", "dire-wolf"},
	{"duathedlen", "daelach", "dolleg", "uruivellas", "thaurhereg", "lithfengel", "kryl-feijan"},
	{"ice-wyrm", "cold-drake", "fire-wyrm", "venom-wyrm", "rantha", "cold-drake-hatchling"}}) do
	for _, id in ipairs(group) do
		for _, other in ipairs(group) do
			if id ~= other and Tokens.by_id[id] and Tokens.by_id[other] then
				local a = actor(Tokens.by_id[id])
				a.image = Tokens.by_id[other].image
				if Tokens.by_id[id].image ~= Tokens.by_id[other].image then
					equal(Tokens.identify(a), nil, "batch AD sibling cannot borrow image "..id.." <- "..other)
				end
				a = actor(Tokens.by_id[id])
				a.name = Tokens.by_id[other].name
				equal(Tokens.identify(a), nil, "batch AD body cannot wear another sibling's name "..id.." as "..other)
				if Tokens.by_id[id].image ~= Tokens.by_id[other].image then
					a = actor(Tokens.by_id[id])
					a.image, a.add_mos = "invis.png", {{image=Tokens.by_id[other].image, display_h=2, display_y=-1}}
					equal(Tokens.identify(a), nil, "batch AD body cannot wear another sibling's tall PNG "..id.." <- "..other)
				end
			end
		end
	end
end
-- Look-alikes stay native (other names on the same PNGs, neighbours that were not selected).
for _, excluded in ipairs({
	{name="snow cat", type="animal", subtype="feline", image="npc/animal_feline_panther.png"},
	{name="snow cat", type="animal", subtype="canine", image="npc/animal_feline_snow_cat.png"},
	{name="panther", type="animal", subtype="feline", image="npc/animal_feline_tiger.png"},
	{name="tiger", type="animal", subtype="feline", image="npc/animal_feline_sabertooth_tiger.png"},
	{name="sabertooth tiger", type="animal", subtype="feline", image="npc/animal_feline_tiger.png"},
	{name="tabby", type="animal", subtype="feline", image="npc/animal_feline_tiger.png"},
	{name="wolf", type="animal", subtype="canine", image="npc/animal_feline_panther.png"},
	{name="ice wyrm", type="dragon", subtype="cold", image="invis.png", add_mos={{image="npc/dragon_cold_cold_drake.png", display_h=2, display_y=-1}}},
	{name="cold drake", type="dragon", subtype="cold", image="invis.png", add_mos={{image="npc/dragon_cold_ice_wyrm.png", display_h=2, display_y=-1}}, define_as="NPC_COLD_DRAKE"},
	{name="ice wyrmic", type="humanoid", subtype="human", image="npc/dragon_cold_ice_wyrm.png"},
	{name="ice wyrm", type="dragon", subtype="ice", image="invis.png", add_mos={{image="npc/dragon_cold_ice_wyrm.png", display_h=2, display_y=-1}}},
	{name="daelach", type="demon", subtype="major", image="invis.png", add_mos={{image="npc/demon_major_uruivellas.png", display_h=2, display_y=-1}}},
	{name="uruivellas", type="demon", subtype="major", image="invis.png", add_mos={{image="npc/demon_major_daelach.png", display_h=2, display_y=-1}}},
	{name="daelach", type="demon", subtype="minor", image="invis.png", add_mos={{image="npc/demon_major_daelach.png", display_h=2, display_y=-1}}},
	{name="d\195\186athedlen", type="demon", subtype="major", image="invis.png", add_mos={{image="npc/demon_major_dolleg.png", display_h=2, display_y=-1}}},
	{name="orc grand summoner", type="humanoid", subtype="orc", image="npc/humanoid_orc_orc_master_wyrmic.png"},
	{name="orc summoner", type="humanoid", subtype="orc", image="npc/humanoid_orc_orc_grand_summoner.png"},
	{name="orc master wyrmic", type="humanoid", subtype="orc", image="npc/humanoid_orc_orc_mage_hunter.png"},
	{name="orc mage-hunter", type="humanoid", subtype="orc", image="npc/humanoid_orc_orc_berserker.png"},
	{name="orc mage hunter", type="humanoid", subtype="orc", image="npc/humanoid_orc_orc_mage_hunter.png"},
	{name="fiery orc wyrmic", type="humanoid", subtype="orc", image="npc/humanoid_orc_orc_master_wyrmic.png", define_as="ORC_FIRE_WYRMIC"},
	{name="ritch larva", type="insect", subtype="ritch", image="npc/insect_ritch_ritch_hunter.png"},
	{name="ritch hunter", type="insect", subtype="ritch", image="npc/insect_ritch_ritch_larva.png"},
	{name="ritch hive mother", type="insect", subtype="ritch", image="npc/insect_ritch_chitinous_ritch.png"},
	{name="ritch hive mother", type="insect", subtype="ritch", image="npc/insect_ritch_ritch_hive_mother.png", unique=true},
	{name="ritch impaler", type="insect", subtype="ritch", image="npc/insect_ritch_ritch_hive_mother.png"},
	{name="ritch larva", type="insect", subtype="ant", image="npc/insect_ritch_ritch_larva.png"},
}) do
	equal(Tokens.identify(excluded), nil, "batch AD look-alike stays native "..excluded.name.." "..tostring(excluded.define_as))
end

-- Summon aliases (user decision 2026-09-30, "summons wear the token of the
-- monster they copy"; evidence/summon-aliases-20260930/README.md). Shapes below
-- are the real constructors' fields (source cited per case).
do
	local function build(base, f)
		local m = copy(base)
		m.faction = "players"
		if f then f(m) end
		return m
	end
	-- Wild Gift Spider, talents/gifts/summon-utility.lua:276-302 (animal/spider, T_SPIDER).
	local spider = {name="giant spider", type="animal", subtype="spider", image="npc/spiderkin_spider_giant_spider.png",
		summoner={faction="players"}, ai="summoned", wild_gift_summon=true, summoner_gain_exp=true,
		is_nature_summon=true, wild_gift_detonate="T_SPIDER"}
	equal(Tokens.identify(build(spider)), "giant-spider", "the Wild Gift spider summon wears the giant spider token")
	equal(Tokens.identify(build(spider, function(m) m.name = "giant spider (wild summon)" end)), "giant-spider", "the English wild-summon spider wears the token")
	equal(Tokens.identify(build(spider, function(m) m.ai, m.ai_state = "party_member", {ai_party="summoned"} end)), "giant-spider", "a party-converted spider summon wears the token")
	equal(Tokens.identify(build(spider, function(m) m.add_mos = {{_isshaderaura=true, image="shockbolt/aura.png"}} end)), "giant-spider", "aura bookkeeping on the spider summon is ignored")
	for label, f in pairs({
		["not a summon"] = function(m) m.summoner = nil end,
		["summoner not a table"] = function(m) m.summoner = true end,
		["not summoned AI"] = function(m) m.ai = "tactical" end,
		["no wild_gift_summon"] = function(m) m.wild_gift_summon = nil end,
		["no summoner_gain_exp"] = function(m) m.summoner_gain_exp = nil end,
		["no is_nature_summon"] = function(m) m.is_nature_summon = nil end,
		["another gift's detonate id"] = function(m) m.wild_gift_detonate = "T_RITCH_FLAMESPITTER" end,
		["missing detonate id"] = function(m) m.wild_gift_detonate = nil end,
		["define_as"] = function(m) m.define_as = "TUT_SPIDER_1" end,
		["unique"] = function(m) m.unique = true end,
		["renamed"] = function(m) m.name = "giant spiderling" end,
		["stripped of wild-summon tail"] = function(m) m.name = "giant spider (wild summon" end,
		["doubled suffix"] = function(m) m.name = "giant spider (wild summon) (wild summon)" end,
		["other subtype"] = function(m) m.subtype = "canine" end,
		["other type"] = function(m) m.type = "vermin" end,
		["other image"] = function(m) m.image = "npc/spiderkin_spider_spitting_spider.png" end,
		["shader"] = function(m) m.shader = "some_shader" end,
		["extra add_mos"] = function(m) m.add_mos = {{image="npc/other.png"}} end,
	}) do
		equal(Tokens.identify(build(spider, f)), nil, "spider summon negative: "..label)
	end
	-- Non-summon animal/spider with the same name, and the tutorial giant spider (spiderkin, define_as).
	equal(Tokens.identify({name="giant spider", type="animal", subtype="spider", image=spider.image, faction="enemies"}), nil, "a non-summon animal/spider giant spider stays native")
	equal(Tokens.identify({name="giant spider", type="spiderkin", subtype="spider", image=spider.image, define_as="TUT_SPIDER_1", faction="enemies", ai="tactical"}), nil, "the tutorial TUT_SPIDER_1 stays native")
	equal(Tokens.identify({name="giant spider", type="spiderkin", subtype="spider", image=spider.image, define_as="TUT_SPIDER_1", summoner={}, ai="summoned",
		wild_gift_summon=true, summoner_gain_exp=true, is_nature_summon=true, wild_gift_detonate="T_SPIDER"}), nil, "define_as beats the spider summon fields")
	-- The relaxation is per entry: no other spider entry accepts animal/spider.
	for _, id in ipairs({"spitting-spider", "chitinous-spider", "orb-spinner", "weaver-hatchling"}) do
		local e = Tokens.by_id[id]
		equal(Tokens.identify(build(spider, function(m) m.name, m.image = e.name, e.image end)), nil, "animal/spider summon shape is not relaxed for "..id)
	end

	-- Name aliases. Each shape copies the constructor cited.
	local cases = {
		{id="void-horror", name="void shard", type="horror", subtype="temporal", image="npc/horror_temporal_void_horror.png", zh="虚空碎片", -- horrors.lua:299
			fields={summoner={faction="players"}, ai="summoned", ai_real="dumb_talented_simple", summoner_gain_exp=true, autolevel="summoner",
				size_category=1, life_rating=2, fear_immune=1, rank=2, exp_worth=0},
			negatives={["size of a void horror"]=function(m) m.size_category = 2 end, ["no summoner_gain_exp"]=function(m) m.summoner_gain_exp = nil end,
				["tactical real ai"]=function(m) m.ai_real = "tactical" end}},
		{id="orc-berserker", name="orc spirit", type="humanoid", subtype="orc", image="npc/humanoid_orc_orc_berserker.png", zh="兽人之魂", -- damage_types.lua:3453
			fields={summoner={faction="players"}, ai="summoned", ai_real="dumb_talented_simple", autolevel="warrior", life_rating=12, exp_worth=0, rank=2},
			negatives={["native berserker life rating"]=function(m) m.life_rating = 14 end, ["other autolevel"]=function(m) m.autolevel = "rogue" end,
				["gains exp like a gift summon"]=function(m) m.summoner_gain_exp = true end}},
		{id="oozing-horror", name="Vilespawn", type="horror", subtype="eldritch", image="npc/horror_eldritch_oozing_horror.png", zh="邪污之子", -- world-artifacts.lua:3439
			fields={summoner={faction="players"}, ai="summoned", ai_real="tactical", autolevel="dexmage", summoner_gain_exp=true, life_rating=8,
				max_vim=204, resists={BLIGHT=100, NATURE=-100}, silent_levelup=true, rank=2, exp_worth=0},
			negatives={["other autolevel"]=function(m) m.autolevel = "wildcaster" end, ["no resists"]=function(m) m.resists = nil end,
				["native oozing horror resists"]=function(m) m.resists = {BLIGHT=100} end, ["nature not weak"]=function(m) m.resists = {BLIGHT=100, NATURE=0} end,
				["native life rating"]=function(m) m.life_rating = 10 end}},
		{id="ghoul", name="Risen Ghoul", type="undead", subtype="ghoul", image="npc/undead_ghoul_ghoul.png", zh="复生食尸鬼", -- ghoul.lua:159
			fields={summoner={faction="players"}, ai="summoned", ai_real="tactical", autolevel="ghoul", summoner_gain_exp=true, silent_levelup=true,
				combat_armor_hardiness=40, rank=2},
			negatives={["no armour hardiness"]=function(m) m.combat_armor_hardiness = nil end, ["walking corpse AI"]=function(m) m.ai_real = "dumb_talented_simple" end,
				["not silent"]=function(m) m.silent_levelup = nil end}},
		{id="ghoul", name="walking corpse", type="undead", subtype="ghoul", image="npc/undead_ghoul_ghoul.png", zh="行尸", -- other.lua:1025
			fields={summoner={faction="players"}, ai="summoned", ai_real="dumb_talented_simple", autolevel="ghoul", summoner_gain_exp=true, no_drops=true, rank=2},
			negatives={["drops loot"]=function(m) m.no_drops = nil end, ["Risen Ghoul AI"]=function(m) m.ai_real = "tactical" end,
				["Risen Ghoul silent levelup"]=function(m) m.silent_levelup = true end}},
	}
	local function shape(c, f)
		local m = {name=c.name, type=c.type, subtype=c.subtype, image=c.image, faction="players"}
		for k, v in pairs(copy(c.fields)) do m[k] = v end
		if f then f(m) end
		return m
	end
	local old_t = rawget(_G, "_t")
	for _, c in ipairs(cases) do
		local tag = c.name.." -> "..c.id
		_G._t = old_t
		equal(Tokens.identify(shape(c)), c.id, "alias positive: "..tag)
		equal(Tokens.identify(shape(c, function(m) m.ai, m.ai_state = "party_member", {ai_party="summoned"} end)), c.id, "alias party-converted: "..tag)
		equal(Tokens.identify(shape(c, function(m) m.add_mos = {{_isshaderaura=true, image="shockbolt/aura.png"}} end)), c.id, "alias aura bookkeeping ignored: "..tag)
		-- Localized client: native code stores _t(name).
		_G._t = function(str) return str == c.name and c.zh or str end
		local ok, err = pcall(function()
			equal(Tokens.identify(shape(c, function(m) m.name = c.zh end)), c.id, "alias localized name: "..tag)
			equal(Tokens.identify(shape(c)), c.id, "alias English name under a locale: "..tag)
			equal(Tokens.identify(shape(c, function(m) m.name = c.zh.."x" end)), nil, "alias localized name with trailing text: "..tag)
			equal(Tokens.identify(shape(c, function(m) m.name = c.zh; m.summoner = nil end)), nil, "localized non-summon: "..tag)
		end)
		_G._t = old_t
		assert(ok, err)
		equal(Tokens.identify(shape(c, function(m) m.name = c.zh end)), nil, "alias localized name rejected without that locale: "..tag)
		-- Negatives shared by every alias.
		local shared = {
			["not a summon"] = function(m) m.summoner = nil end,
			["summoner not a table"] = function(m) m.summoner = true end,
			["not summoned AI"] = function(m) m.ai = "tactical" end,
			["renamed"] = function(m) m.name = c.name.."s" end,
			["stripped name"] = function(m) m.name = c.name:sub(1, -2) end,
			["capitalised differently"] = function(m) m.name = c.name:sub(1, 1):upper()..c.name:sub(2):lower() == c.name and c.name:upper() or c.name:sub(1, 1):upper()..c.name:sub(2):lower() end,
			["unique"] = function(m) m.unique = true end,
			["define_as"] = function(m) m.define_as = "X_SUMMON" end,
			["other type"] = function(m) m.type = "animal" end,
			["other subtype"] = function(m) m.subtype = "other-subtype" end,
			["other image"] = function(m) m.image = "npc/summoner_wardog.png" end,
			["shader"] = function(m) m.shader = "some_shader" end,
			["moddable_tile"] = function(m) m.moddable_tile = "some_doll" end,
			["extra add_mos"] = function(m) m.add_mos = {{image="npc/other.png"}} end,
			["animation"] = function(m) m.anim = {} end,
		}
		for label, f in pairs(shared) do
			equal(Tokens.identify(shape(c, f)), nil, "alias negative ("..label.."): "..tag)
		end
		for label, f in pairs(c.negatives) do
			equal(Tokens.identify(shape(c, f)), nil, "alias negative ("..label.."): "..tag)
		end
		-- A same-name non-summon and an alias-named actor carrying only the PNG stay native.
		equal(Tokens.identify({name=c.name, type=c.type, subtype=c.subtype, image=c.image, faction="enemies"}), nil, "same-name non-summon stays native: "..tag)
		-- The alias never lets a summon of this name wear a different entry.
		for _, other in ipairs({"wolf", "assassin", "orc-pyromancer", "dredge"}) do
			local e = Tokens.by_id[other]
			if e.id ~= c.id then
				equal(Tokens.identify(shape(c, function(m) m.type, m.subtype, m.image = e.type, e.subtype, e.image end)), nil, "alias cannot borrow "..other..": "..tag)
			end
		end
	end
	-- Shadowy assassin (traps.lua:318) carries shader shadow_simulacrum: native, never aliased.
	local assassin = {name="shadowy assassin", type="humanoid", subtype="human", image="npc/humanoid_human_assassin.png", shader="shadow_simulacrum",
		summoner={faction="players"}, ai="dumb_talented_simple", summoner_gain_exp=true, faction="players", rank=2}
	equal(Tokens.identify(assassin), nil, "the shadowy assassin stays native")
	assassin.shader = nil
	equal(Tokens.identify(assassin), nil, "even without the shader the shadowy assassin has no alias")
	-- Terror / tormentor borrow the nightmare horror PNG; no token yet.
	for _, name in ipairs({"terror", "tormentor"}) do
		equal(Tokens.identify({name=name, type="horror", subtype="eldritch", image="npc/horror_eldritch_nightmare_horror.png", summoner={}, ai="summoned", faction="players"}), nil,
			name.." stays native")
	end
	-- The alias names are not catalogued names themselves.
	for _, name in ipairs({"void shard", "orc spirit", "Vilespawn", "Risen Ghoul", "walking corpse"}) do
		for _, entry in ipairs(Tokens.catalog) do equal(entry.name == name, false, "alias name is not a catalog entry: "..name) end
	end
end

-- Batch AE: twelve exact off-list pool identities; Arena HEADLESSHORROR stays native.
local batch_ae = {"champion-of-urh-rok", "forge-giant", "hummerhorn", "weaver-matriarch", "patchwork-troll", "maulotaur", "worm-that-walks", "headless-horror", "storm-wyrm", "spire-dragon", "blinkwyrm", "emperor-wight"}
local names_ae = {["champion-of-urh-rok"]="champion of Urh'Rok", ["forge-giant"]="forge-giant", ["hummerhorn"]="hummerhorn", ["weaver-matriarch"]="weaver matriarch", ["patchwork-troll"]="patchwork troll", ["maulotaur"]="maulotaur", ["worm-that-walks"]="worm that walks", ["headless-horror"]="headless horror", ["storm-wyrm"]="storm wyrm", ["spire-dragon"]="spire dragon", ["blinkwyrm"]="blinkwyrm", ["emperor-wight"]="emperor wight"}
local tall_ae = {["champion-of-urh-rok"]=true, ["forge-giant"]=true, ["weaver-matriarch"]=true, ["patchwork-troll"]=true, ["maulotaur"]=true, ["storm-wyrm"]=true, ["spire-dragon"]=true, ["blinkwyrm"]=true, ["emperor-wight"]=true}
equal(#batch_ae, 12, "batch AE has twelve identities")
for _, id in ipairs(batch_ae) do
	local entry = Tokens.by_id[id]
	if entry == nil then error("batch AE catalog entry missing: "..id) end
	local tall = tall_ae[id]
	equal(entry.name, names_ae[id], "batch AE exact name "..id)
	equal(entry.define_as, nil, "batch AE no define_as binding "..id)
	equal(entry.unique, nil, "batch AE non-unique "..id)
	equal(entry.native_tall, tall and true or nil, "batch AE native_tall flag "..id)
	equal(entry.urh_rok_form, nil, "batch AE no urh_rok_form flag "..id)
	equal(Tokens.identify(actor(entry)), id, "batch AE exact identity "..id)
	local a = actor(entry)
	a.tint_r, a.tint_g, a.tint_b = 0, 0, 0
	equal(Tokens.identify(a), id, "batch AE tint is colour only "..id)
	a = actor(entry)
	a.color_r, a.color_g, a.color_b = 0, 0, 185
	equal(Tokens.identify(a), id, "batch AE colour modulation keeps the token "..id)
	a = actor(entry)
	a.image = "invis.png"
	a.add_mos = {{image=entry.image, display_h=2, display_y=-1}}
	equal(Tokens.identify(a), tall and id or nil, "batch AE tall body accepted only for tall entries "..id)
	if tall then
		a = actor(entry)
		a.image = "invis.png"
		a.add_mos = {{image=entry.image, display_h=2, display_y=-1}, {image="npc/other.png"}}
		equal(Tokens.identify(a), nil, "batch AE tall body with a second overlay stays native "..id)
		a.add_mos = {{image="npc/other.png", display_h=2, display_y=-1}}
		equal(Tokens.identify(a), nil, "batch AE tall body naming another PNG stays native "..id)
		a.add_mos = {{image=entry.image, display_h=2, display_y=-1, shader="x"}}
		equal(Tokens.identify(a), nil, "batch AE tall body with extra keys stays native "..id)
		a.add_mos = {{image=entry.image, display_h=3, display_y=-1}}
		equal(Tokens.identify(a), nil, "batch AE tall body with other dimensions stays native "..id)
		a.add_mos = {{image=entry.image, display_h=2, display_y=-1}, {_isshaderaura=true, image="shockbolt/aura.png"}}
		equal(Tokens.identify(a), id, "batch AE tall body with shader aura bookkeeping "..id)
		a.add_mos = {{_isshaderaura=true, image="shockbolt/aura.png"}, {image=entry.image, display_h=2, display_y=-1}}
		equal(Tokens.identify(a), id, "batch AE tall body with shader aura bookkeeping first "..id)
		-- Single image (nicer_tiles off): the flat native image is accepted too.
		a = actor(entry)
		a.image, a.add_mos = entry.image, nil
		equal(Tokens.identify(a), id, "batch AE single native image with nicer_tiles off "..id)
	end
	a = actor(entry)
	a.type = entry.type == "undead" and "humanoid" or "undead"
	equal(Tokens.identify(a), nil, "batch AE type changed "..id)
	a = actor(entry)
	a.subtype = "other-subtype"
	equal(Tokens.identify(a), nil, "batch AE subtype changed "..id)
	a = actor(entry)
	a.shader = "some_shader"
	equal(Tokens.identify(a), nil, "batch AE shader keeps native art "..id)
	a = actor(entry)
	a.moddable_tile = "some_doll"
	equal(Tokens.identify(a), nil, "batch AE paper-doll actor keeps native art "..id)
	a = actor(entry)
	a.anim = {}
	equal(Tokens.identify(a), nil, "batch AE animation keeps native art "..id)
	a = actor(entry)
	a.add_displays = {{image="npc/iceblock.png"}}
	equal(Tokens.identify(a), nil, "batch AE frozen/pinned add_displays keep native art "..id)
	a = actor(entry)
	a.unique = true
	equal(Tokens.identify(a), nil, "batch AE non-unique entry rejects an unknown unique "..id)
	a = actor(entry)
	a.define_as = "SOME_DEFINE_AS"
	equal(Tokens.identify(a), nil, "batch AE unexpected define_as "..id)
	a = actor(entry)
	a.image = "npc/some_other_image.png"
	equal(Tokens.identify(a), nil, "batch AE other image keeps native art "..id)
	if entry.type ~= "demon" or entry.subtype ~= "major" then
		-- (the duathedlen and daelach already are demon/major: the form changes nothing for them)
		a = actor(entry)
		a.__old_type = {entry.type, entry.subtype}
		a.type, a.subtype = "demon", "major"
		a.sustain_talents = {T_FLAME_OF_URH_ROK = {}}
		equal(Tokens.identify(a), nil, "batch AE Flame of Urh'Rok form is not supported "..id)
	end
	a = actor(entry)
	a.add_mos = {{_isshaderaura=true, image="shockbolt/aura.png"}}
	equal(Tokens.identify(a), id, "batch AE shader aura entry is ignored "..id)
	-- No variants or aliases: a summon shape carrying a wild-summon rename or another PNG stays native.
	a = actor(entry)
	a.summoner, a.ai, a.wild_gift_summon = {}, "summoned", true
	equal(Tokens.identify(a), id, "batch AE a same-body summon shape is the same exact leaf "..id)
	a.name = entry.name.." (wild summon)"
	equal(Tokens.identify(a), nil, "batch AE the wild-summon rename is not covered "..id)
	a = actor(entry)
	a.summoner, a.ai, a.summoner_gain_exp, a.wild_gift_summon = {}, "summoned", true, true
	a.image = "npc/summoner_ritch.png"
	equal(Tokens.identify(a), nil, "batch AE no summon PNG alias "..id)
end
-- Batch AF: nine admitted pool identities; dreaming horror stays native.
local batch_af = {"nightmare-horror", "radiant-horror", "maelstrom", "parasitic-horror", "lich", "ancient-lich", "archlich", "blood-lich", "animated-blood"}
local names_af = {["nightmare-horror"]="nightmare horror", ["radiant-horror"]="radiant horror", ["maelstrom"]="maelstrom", ["parasitic-horror"]="parasitic horror", ["lich"]="lich", ["ancient-lich"]="ancient lich", ["archlich"]="archlich", ["blood-lich"]="blood lich", ["animated-blood"]="animated blood"}
local tall_af = {["maelstrom"]=true, ["parasitic-horror"]=true, ["lich"]=true, ["ancient-lich"]=true, ["archlich"]=true, ["animated-blood"]=true}
equal(#batch_af, 9, "batch AF has nine admitted identities")
for _, id in ipairs(batch_af) do
	local entry = Tokens.by_id[id]
	if entry == nil then error("batch AF catalog entry missing: "..id) end
	local tall = tall_af[id]
	equal(entry.name, names_af[id], "batch AF exact name "..id)
	equal(entry.define_as, nil, "batch AF no define_as binding "..id)
	equal(entry.unique, nil, "batch AF non-unique "..id)
	equal(entry.native_tall, tall and true or nil, "batch AF native_tall flag "..id)
	equal(entry.urh_rok_form, nil, "batch AF no urh_rok_form flag "..id)
	equal(Tokens.identify(actor(entry)), id, "batch AF exact identity "..id)
	local a = actor(entry)
	a.tint_r, a.tint_g, a.tint_b = 0, 0, 0
	equal(Tokens.identify(a), id, "batch AF tint is colour only "..id)
	a = actor(entry)
	a.color_r, a.color_g, a.color_b = 0, 0, 185
	equal(Tokens.identify(a), id, "batch AF colour modulation keeps the token "..id)
	a = actor(entry)
	a.image = "invis.png"
	a.add_mos = {{image=entry.image, display_h=2, display_y=-1}}
	equal(Tokens.identify(a), tall and id or nil, "batch AF tall body accepted only for tall entries "..id)
	if tall then
		a = actor(entry)
		a.image = "invis.png"
		a.add_mos = {{image=entry.image, display_h=2, display_y=-1}, {image="npc/other.png"}}
		equal(Tokens.identify(a), nil, "batch AF tall body with a second overlay stays native "..id)
		a.add_mos = {{image="npc/other.png", display_h=2, display_y=-1}}
		equal(Tokens.identify(a), nil, "batch AF tall body naming another PNG stays native "..id)
		a.add_mos = {{image=entry.image, display_h=2, display_y=-1, shader="x"}}
		equal(Tokens.identify(a), nil, "batch AF tall body with extra keys stays native "..id)
		a.add_mos = {{image=entry.image, display_h=3, display_y=-1}}
		equal(Tokens.identify(a), nil, "batch AF tall body with other dimensions stays native "..id)
		a.add_mos = {{image=entry.image, display_h=2, display_y=-1}, {_isshaderaura=true, image="shockbolt/aura.png"}}
		equal(Tokens.identify(a), id, "batch AF tall body with shader aura bookkeeping "..id)
		a.add_mos = {{_isshaderaura=true, image="shockbolt/aura.png"}, {image=entry.image, display_h=2, display_y=-1}}
		equal(Tokens.identify(a), id, "batch AF tall body with shader aura bookkeeping first "..id)
		-- Single image (nicer_tiles off): the flat native image is accepted too.
		a = actor(entry)
		a.image, a.add_mos = entry.image, nil
		equal(Tokens.identify(a), id, "batch AF single native image with nicer_tiles off "..id)
	end
	a = actor(entry)
	a.type = entry.type == "undead" and "humanoid" or "undead"
	equal(Tokens.identify(a), nil, "batch AF type changed "..id)
	a = actor(entry)
	a.subtype = "other-subtype"
	equal(Tokens.identify(a), nil, "batch AF subtype changed "..id)
	a = actor(entry)
	a.shader = "some_shader"
	equal(Tokens.identify(a), nil, "batch AF shader keeps native art "..id)
	a = actor(entry)
	a.moddable_tile = "some_doll"
	equal(Tokens.identify(a), nil, "batch AF paper-doll actor keeps native art "..id)
	a = actor(entry)
	a.anim = {}
	equal(Tokens.identify(a), nil, "batch AF animation keeps native art "..id)
	a = actor(entry)
	a.add_displays = {{image="npc/iceblock.png"}}
	equal(Tokens.identify(a), nil, "batch AF frozen/pinned add_displays keep native art "..id)
	a = actor(entry)
	a.unique = true
	equal(Tokens.identify(a), nil, "batch AF non-unique entry rejects an unknown unique "..id)
	a = actor(entry)
	a.define_as = "SOME_DEFINE_AS"
	equal(Tokens.identify(a), nil, "batch AF unexpected define_as "..id)
	a = actor(entry)
	a.image = "npc/some_other_image.png"
	equal(Tokens.identify(a), nil, "batch AF other image keeps native art "..id)
	if entry.type ~= "demon" or entry.subtype ~= "major" then
		-- (the duathedlen and daelach already are demon/major: the form changes nothing for them)
		a = actor(entry)
		a.__old_type = {entry.type, entry.subtype}
		a.type, a.subtype = "demon", "major"
		a.sustain_talents = {T_FLAME_OF_URH_ROK = {}}
		equal(Tokens.identify(a), nil, "batch AF Flame of Urh'Rok form is not supported "..id)
	end
	a = actor(entry)
	a.add_mos = {{_isshaderaura=true, image="shockbolt/aura.png"}}
	equal(Tokens.identify(a), id, "batch AF shader aura entry is ignored "..id)
	-- No variants or aliases: a summon shape carrying a wild-summon rename or another PNG stays native.
	a = actor(entry)
	a.summoner, a.ai, a.wild_gift_summon = {}, "summoned", true
	equal(Tokens.identify(a), id, "batch AF a same-body summon shape is the same exact leaf "..id)
	a.name = entry.name.." (wild summon)"
	equal(Tokens.identify(a), nil, "batch AF the wild-summon rename is not covered "..id)
	a = actor(entry)
	a.summoner, a.ai, a.summoner_gain_exp, a.wild_gift_summon = {}, "summoned", true, true
	a.image = "npc/summoner_ritch.png"
	equal(Tokens.identify(a), nil, "batch AF no summon PNG alias "..id)
end

equal(Tokens.identify({name="dreaming horror", type="horror", subtype="eldritch", image="invis.png",
    shader="shadow_simulacrum", add_mos={{image="npc/horror_eldritch_dreaming_horror.png", display_h=2, display_y=-1}}}), nil, "AF dreaming horror keeps native shader")
equal(Tokens.identify({name="dreaming horror", type="horror", subtype="eldritch", image="npc/horror_eldritch_dreaming_horror.png"}), nil, "AF no dreaming horror mapping even without shader")
do
    local e = Tokens.by_id["animated-blood"]
    local function bloodedge()
        local a = actor(e)
        a.image, a.add_mos = "invis.png", {{image=e.image, display_h=1, display_y=0}}
        a.summoner, a.summoner_gain_exp = {}, true
        a.ai, a.ai_real, a.autolevel = "summoned", "tactical", "dexmage"
        a.max_vim, a.rank, a.exp_worth, a.life_rating = 256, 3, 0, 10 -- live level-up value
        a.resists = {BLIGHT=100, NATURE=-100}
        a.negative_status_effect_immune, a.silent_levelup, a.summon_time = 1, true, 9
        return a
    end
    equal(Tokens.identify(bloodedge()), "animated-blood", "AF same-body Blood-Edge summon")
    local a = bloodedge(); a.ai, a.ai_state = "party_member", {ai_party="summoned"}
    equal(Tokens.identify(a), "animated-blood", "AF Blood-Edge party conversion")
    a = bloodedge(); a.add_mos[2] = {_isshaderaura=true, image="aura.png"}
    equal(Tokens.identify(a), "animated-blood", "AF Blood-Edge native aura")
    for _, change in ipairs({{"summoner",false},{"summoner_gain_exp",false},{"ai","tactical"},
        {"ai_real","other"},{"autolevel","caster"},{"resists",false},{"resists",{BLIGHT=100}},{"resists",{BLIGHT=100,NATURE=0}},{"rank",1},{"exp_worth",1},
        {"life_rating",7},{"negative_status_effect_immune",0},{"silent_levelup",false},{"summon_time",10},
        {"unique",true},{"define_as","OTHER"},{"shader","shadow_simulacrum"},{"anim",{}},
        {"moddable_tile","x"},{"add_displays",{{image="x"}}},{"textures",{"x"}},{"image","npc/other.png"},
        {"type","horror"},{"subtype","lich"}}) do
        a=bloodedge();a[change[1]]=change[2]
        equal(Tokens.identify(a),nil,"AF Blood-Edge constructor/appearance guard "..change[1])
    end
    for _, change in ipairs({{"image","npc/other.png"},{"display_h",3},{"display_y",-1},
        {"display_x",1},{"display_w",2},{"display_scale",2},{"shader","x"},{"particle",true}}) do
        a=bloodedge();a.add_mos[1][change[1]]=change[2]
        equal(Tokens.identify(a),nil,"AF Blood-Edge body guard "..change[1])
    end
    a=bloodedge();a.add_mos[2]={image=e.image,display_h=1,display_y=0}
    equal(Tokens.identify(a),nil,"AF Blood-Edge extra real body stays native")
    a=actor(e);a.image="npc/undead_blood_animated_blood.png"
    equal(Tokens.identify(a),nil,"AF missing native default PNG is not invented art")
    -- Official source only: mod-tome.lua entity-name and _t keys both 活化血液.
    local old_t=_G._t
    _G._t=function(n) return n=="animated blood" and "活化血液" or n end
    a=bloodedge();a.name="活化血液"
    equal(Tokens.identify(a),"animated-blood","AF localized Blood-Edge name")
    a.shader="shadow_simulacrum"
    equal(Tokens.identify(a),nil,"AF localized Blood-Edge shader fallback")
    _G._t=old_t
end
-- No AF temporal-clone code: verify the existing whole-catalog constructor.
for _, id in ipairs(batch_af) do
    local e=Tokens.by_id[id]
    local a=actor(e)
    a.name=e.name.."'s temporal clone"
    a.summoner,a.summoner_gain_exp={},true
    a.ai,a.ai_real,a.ai_tactic="summoned","tactical",{escape=0}
    a.summon_time,a.exp_worth,a.level,a.max_level=4,0,42,42
    equal(Tokens.identify(a),id,"AF generic temporal clone flat "..id)
    a.image,a.add_mos="invis.png",{{image=e.image,display_h=2,display_y=-1}}
    equal(Tokens.identify(a),tall_af[id] and id or nil,"AF generic temporal clone tall "..id)
end
for _, family in ipairs({{"lich","ancient-lich","archlich","blood-lich","animated-blood"},
    {"nightmare-horror","radiant-horror","maelstrom","parasitic-horror","luminous-horror","oozing-horror","abyssal-horror","umbral-horror","bone-horror","sanguine-horror","dread"}}) do
    for _,id in ipairs(family) do for _,other in ipairs(family) do if id~=other then
        local a=actor(Tokens.by_id[id]);a.image=Tokens.by_id[other].image
        equal(Tokens.identify(a),nil,"AF sibling PNG guard "..id.." / "..other)
    end end end
end


equal(Tokens.identify({name="blood lich", type="undead", subtype="lich", image="npc/undead_lich_blood_lich.png"}), "blood-lich", "AF blood lich accepted after infrastructure retry without waiver")
-- Same-name Arena leaf and unsupported appearances cannot borrow the pool token.
equal(Tokens.identify({name="headless horror", define_as="HEADLESSHORROR", type="horror", subtype="eldritch", image="npc/horror_eldritch_headless_horror.png"}), nil, "AE Arena headless horror remains native")
-- Multiplication preserves the hummerhorn body; escorts and carrion worms have their own bodies.
do
    local a = actor(Tokens.by_id["hummerhorn"])
    a.can_multiply, a.exp_worth = 3, 0.1
    equal(Tokens.identify(a), "hummerhorn", "AE multiplied hummerhorn wears same token")
    local a = actor(Tokens.by_id["worm-that-walks"])
    a.image = "npc/carrion_worm_mass.png"
    equal(Tokens.identify(a), nil, "AE spawned carrion worm cannot borrow caster token")
end
-- Birth sustains add values/particles; forge-giant Burning Wake is ignored shader-aura bookkeeping.
for id, talents in pairs({["forge-giant"]={"T_BURNING_WAKE","T_WILDFIRE"}, ["worm-that-walks"]={"T_RUIN"},
    ["spire-dragon"]={"T_KINETIC_AURA","T_KINETIC_SHIELD"}, ["blinkwyrm"]={"T_DISRUPTION_SHIELD","T_ARCANE_POWER","T_SPELLCRAFT","T_ESSENCE_OF_SPEED"},
    ["emperor-wight"]={"T_THUNDERSTORM"}}) do
    local a = actor(Tokens.by_id[id])
    a.sustain_talents = {}
    for _, t in ipairs(talents) do a.sustain_talents[t] = {} end
    a.__particles = {{}}
    a.add_mos = {{_isshaderaura=true, image="particles_images/wings.png"}}
    equal(Tokens.identify(a), id, "AE birth sustains preserve flat body "..id)
    a.image = "invis.png"
    a.add_mos = {{image=Tokens.by_id[id].image, display_h=2, display_y=-1}, {_isshaderaura=true, image="particles_images/wings.png"}}
    equal(Tokens.identify(a), tall_ae[id] and id or nil, "AE birth sustains preserve tall body "..id)
end
-- Preserve the AD tall random-boss policy for renamed forge giants and Storm Terrors.
for _, id in ipairs(batch_ae) do
    local e = Tokens.by_id[id]
    local base, boss = actor(e), actor(e)
    if tall_ae[id] then
        base.image, base.add_mos = "invis.png", {{image=e.image, display_h=2, display_y=-1}}
        boss.image, boss.add_mos = "invis.png", {{image=e.image, display_h=2, display_y=-1}}
    end
    local capture = Tokens.captureRandomOrigin(base)
    boss.name, boss.define_as, boss.unique, boss.randboss = "AE Vault Boss", "RANDOM_BOSS_AE", "AE Vault Boss", true
    equal(Tokens.recordRandomOrigin(boss, capture, "RANDOM_BOSS_AE"), (not tall_ae[id]) and id or nil, "AE random origin respects appearance "..id)
    equal(Tokens.identify(boss), (not tall_ae[id]) and id or nil, "AE random boss respects appearance "..id)
end
for _, group in ipairs({{"champion-of-urh-rok","forge-giant","dolleg","uruivellas","duathedlen","daelach"},
    {"storm-wyrm","spire-dragon","blinkwyrm","storm-drake","fire-wyrm","venom-wyrm","ice-wyrm"},
    {"patchwork-troll","forest-troll","stone-troll"}, {"maulotaur","minotaur","minotaur-maze"},
    {"hummerhorn","hornet-swarm","ritch-hunter"}, {"weaver-matriarch","weaver-young","giant-spider","weaver-queen"},
    {"worm-that-walks","headless-horror","emperor-wight","forest-wight","grave-wight","barrow-wight"}}) do
    for _, id in ipairs(group) do for _, other in ipairs(group) do if id ~= other then
        local e, o = Tokens.by_id[id], Tokens.by_id[other]
        local a = actor(e)
        a.image = o.image
        equal(Tokens.identify(a), nil, "AE sibling PNG guard "..id.." / "..other)
        a = actor(e)
        a.name = o.name
        equal(Tokens.identify(a), nil, "AE sibling name guard "..id.." / "..other)
        a = actor(e)
        a.image, a.add_mos = "invis.png", {{image=o.image, display_h=2, display_y=-1}}
        equal(Tokens.identify(a), nil, "AE sibling tall body guard "..id.." / "..other)
    end end end
end

-- Temporal clone constructor preserves bodies under exact English/localized names.
for _, id in ipairs(batch_ae) do
    local e = Tokens.by_id[id]
    local function clone()
        local a = actor(e)
        a.name = e.name.."'s temporal clone"
        a.summoner, a.summoner_gain_exp = {}, true
        a.ai, a.ai_real, a.ai_tactic = "summoned", "tactical", {escape=0}
        a.summon_time, a.exp_worth, a.level, a.max_level = 4, 0, 42, 42
        return a
    end
    equal(Tokens.identify(clone()), id, "AE same-body temporal clone "..id)
    local a = clone()
    a.image, a.add_mos = "invis.png", {{image=e.image, display_h=2, display_y=-1}}
    equal(Tokens.identify(a), tall_ae[id] and id or nil, "AE temporal clone tall contract "..id)
    for _, change in ipairs({{"summoner",false},{"summoner_gain_exp",false},{"ai","tactical"},{"ai_real","other"},
        {"exp_worth",1},{"summon_time",false},{"max_level",41},{"ai_tactic",{}},{"define_as","OTHER"},{"unique",true},
        {"shader","shadow_simulacrum"},{"type","image"},{"subtype","ghost"},{"image","npc/other.png"},
        {"moddable_tile","other"},{"anim",{}},{"add_displays",{{image="other"}}}}) do
        a = clone(); a[change[1]] = change[2]
        equal(Tokens.identify(a), nil, "AE temporal clone constructor/appearance guard "..id.." "..change[1])
    end
    a = clone(); a.name = e.name.."'s Inner Demon"; a.shader = "shadow_simulacrum"
    equal(Tokens.identify(a), nil, "AE inner demon retains native shader "..id)
end
-- Locale strings come only from the official mod-tome.lua and native translation path.
do
    local old_t, old_format = _G._t, string.tformat
    local names = { ["champion of Urh'Rok"]="乌鲁洛克的冠军", ["forge-giant"]="锻造巨人", ["hummerhorn"]="大黄蜂",
        ["weaver matriarch"]="雌性编织者", ["patchwork troll"]="拼凑巨魔", ["maulotaur"]="玛诺陶",
        ["worm that walks"]="蠕虫合体", ["headless horror"]="无头恐魔", ["storm wyrm"]="风暴巨龙",
        ["spire dragon"]="螺旋巨龙", ["blinkwyrm"]="相位巨龙", ["emperor wight"]="帝王尸妖" }
    _G._t = function(s) return names[s] or s end
    string.tformat = function(s, name) if s == "%s's temporal clone" then return name.."的时空克隆体" end return s:format(name) end
    local traditional = { ["champion of Urh'Rok"]="烏魯洛克的冠軍", ["forge-giant"]="鍛造巨人", ["hummerhorn"]="大黃蜂",
        ["weaver matriarch"]="雌性編織者", ["patchwork troll"]="拼湊巨魔", ["maulotaur"]="瑪諾陶",
        ["worm that walks"]="蠕蟲合體", ["headless horror"]="無頭恐魔", ["storm wyrm"]="風暴巨龍",
        ["spire dragon"]="螺旋巨龍", ["blinkwyrm"]="相位巨龍", ["emperor wight"]="帝王屍妖" }
    for _, language in ipairs({{names,"的时空克隆体"},{traditional,"的時空克隆體"}}) do
    names = language[1]
    string.tformat = function(s, name) if s == "%s's temporal clone" then return name..language[2] end return s:format(name) end
    for _, id in ipairs(batch_ae) do
        local e = Tokens.by_id[id]
        local a = actor(e)
        a.name = names[e.name]..language[2]
        a.summoner, a.summoner_gain_exp = {}, true
        a.ai, a.ai_real, a.ai_tactic = "summoned", "tactical", {escape=0}
        a.summon_time, a.exp_worth, a.level, a.max_level = 4, 0, 42, 42
        equal(Tokens.identify(a), id, "AE localized temporal clone "..id)
    end
    end
    _G._t, string.tformat = old_t, old_format
end

-- Temporal clones apply to every covered non-unique entry, not to one batch
-- (makeParadoxClone clones any target; same-body copies wear its token).
do
	local function clone(e)
		local a = actor(e)
		a.name = e.name.."'s temporal clone"
		a.summoner, a.summoner_gain_exp = {}, true
		a.ai, a.ai_real, a.ai_tactic = "summoned", "tactical", {escape=0}
		a.summon_time, a.exp_worth, a.level, a.max_level = 4, 0, 30, 30
		return a
	end
	local covered, natives = 0, 0
	for _, e in ipairs(Tokens.catalog) do
		local a = clone(e)
		if e.unique then
			equal(Tokens.identify(a), nil, "unique temporal clone stays native "..e.id); natives = natives + 1
		else
			equal(Tokens.identify(a), e.id, "temporal clone wears its body's token "..e.id); covered = covered + 1
			a = clone(e); a.define_as = (e.define_as or "X").."_OTHER"
			equal(Tokens.identify(a), nil, "temporal clone with another define_as stays native "..e.id)
			a = clone(e); a.max_level = 31
			equal(Tokens.identify(a), nil, "temporal clone constructor guard "..e.id)
		end
	end
	assert(covered > 300 and natives > 0, "temporal clone coverage spans the whole catalog")
	-- An English name that is not "<catalog name>'s temporal clone" never matches.
	local e = Tokens.by_id["orc-berserker"]
	local a = clone(e); a.name = "orc berserker's temporal clone (copy)"
	equal(Tokens.identify(a), nil, "temporal clone suffix must be exact")
	a = clone(e); a.name = "orc berserker's Temporal Clone"
	equal(Tokens.identify(a), nil, "temporal clone case must be exact")
end

-- AG special cases: exact shader opt-in, composite names, unchanged fallback.
local batch_ag = {"multi-hued-drake-hatchling", "multi-hued-drake", "greater-multi-hued-wyrm", "shadow-claw", "shadow-caster", "multi-hued-crystal", "shimmering-crystal"}
for _, id in ipairs(batch_ag) do
    local e = assert(Tokens.by_id[id])
    local a = actor(e)
    equal(Tokens.identify(a), id, "AG shader-disabled/native body "..id)
    a.shader = "quad_hue"
    equal(Tokens.identify(a), e.native_shader and id or nil, "AG exact shader allow-list "..id)
    for _, args in ipairs({{}, {color1={1,0,0,1}}, false, "default"}) do
        a.shader_args = args
        equal(Tokens.identify(a), nil, "AG non-nil shader args rejected "..id)
    end
    a.shader_args = nil; a.shader = "shadow_simulacrum"
    equal(Tokens.identify(a), nil, "AG different shader rejected "..id)
    if e.native_tall then
        a = actor(e); a.image = "invis.png"
        a.add_mos = {{image=e.image, display_h=2, display_y=-1}}
        equal(Tokens.identify(a), id, "AG nicer_tiles tall native shader=false "..id)
        a.shader = "quad_hue"
        equal(Tokens.identify(a), id, "AG exact shader on supported tall body "..id)
        a.add_mos[1].shader = "quad_hue"
        equal(Tokens.identify(a), nil, "AG body-layer shader still rejected "..id)
    end
    if e.shared_name then
        for _, def in ipairs({false,"OTHER","shared_name_index","entries", id == "shadow-claw" and "SHADOW_CASTER" or "SHADOW_CLAW"}) do
            a = actor(e); a.define_as = def or nil
            equal(Tokens.identify(a), nil, "AG missing/wrong composite definition "..id)
        end
        a = actor(e); a.image = id == "shadow-claw" and "npc/shadow-caster.png" or "npc/shadow-claw.png"
        equal(Tokens.identify(a), nil, "AG swapped shadow body "..id)
    end
end
-- quad_hue cannot open any other existing entry.
for _, e in ipairs(Tokens.catalog) do
    if not e.native_shader then
        local a = actor(e); a.shader = "quad_hue"
        equal(Tokens.identify(a), nil, "AG no blanket shader acceptance "..e.id)
    end
end
equal(Tokens.identify({name="shadowy assassin",type="humanoid",subtype="human",image="npc/humanoid_human_assassin.png",shader="shadow_simulacrum"}),nil,"AG shadowy assassin stays native")
equal(Tokens.identify({name="dreaming horror",type="horror",subtype="eldritch",image="npc/horror_eldritch_dreaming_horror.png",shader="shadow_simulacrum"}),nil,"AG dreaming horror stays native")
-- Catalog duplicates must still fail unless both entries explicitly opt in and
-- bind distinct non-empty define_as values. Execute the real index builder.
do
    local f = assert(io.open(here.."../overload/mod/class/CheckerTokens.lua")); local source=f:read("*a"); f:close()
    equal(pcall(assert(loadstring(source))), true, "AG distinct composite definitions accepted by index")
    for _, replacement in ipairs({
        (source:gsub('define_as="SHADOW_CASTER", shared_name=true','define_as="SHADOW_CLAW", shared_name=true')),
        (source:gsub('define_as="SHADOW_CASTER", shared_name=true','shared_name=true')),
        (source:gsub('define_as="SHADOW_CASTER", shared_name=true','define_as="SHADOW_CASTER"')),
        (source:gsub('define_as="SHADOW_CLAW", shared_name=true','define_as="SHADOW_CLAW"')),
    }) do
        local ok = pcall(assert(loadstring(replacement)))
        equal(ok, false, "AG duplicate catalog invariant")
    end
end

-- Both official translations have the same shadow name; define_as still
-- selects the right same-body temporal clone in each language.
do
    local old_t, old_format = _G._t, string.tformat
    for _, language in ipairs({{"阴影之爪","的时空克隆体"},{"陰影之爪","的時空克隆體"}}) do
        _G._t = function(s) return s == "shadow claw" and language[1] or s end
        string.tformat = function(s,name) return s == "%s's temporal clone" and (name..language[2]) or s:format(name) end
        for _,id in ipairs({"shadow-claw","shadow-caster"}) do
            local a = actor(Tokens.by_id[id]); a.name = language[1]..language[2]
            a.summoner, a.summoner_gain_exp = {}, true
            a.ai,a.ai_real,a.ai_tactic="summoned","tactical",{escape=0}
            a.summon_time,a.exp_worth,a.level,a.max_level=4,0,30,30
            equal(Tokens.identify(a),id,"AG localized composite clone "..id)
            a.define_as=nil
            equal(Tokens.identify(a),nil,"AG localized ambiguous clone stays native "..id)
        end
    end
    _G._t,string.tformat=old_t,old_format
end
equal(Tokens.identify({name="shadow claw",type="undead",subtype="shadow",image="npc/shadow-caster.png",define_as="SHADOW_CASTER"}),"shadow-caster","AG caster composite identity admitted")

-- UA: exact unique identities, body safety and native constructor rename cases.
do
local ua_ids = {"kra-tor","khulmanar","rungof","grgglck","queen-ant","ak-gishil","ninandra","phoenix","ukruk","gorbat","grushnak","vor"}
local ua_tall = {['kra-tor']=true,khulmanar=true,grgglck=true,['queen-ant']=true,['ak-gishil']=true,ninandra=true,gorbat=true}
for _,id in ipairs(ua_ids) do
 local entry=Tokens.by_id[id]
 equal(entry.unique,true,'UA unique entry '..id)
 equal(entry.native_tall,nil,'UA unique tall precedent '..id)
 local a=actor(entry);a.unique=entry.name
 equal(Tokens.identify(a),id,'UA resolved unique marker '..id)
 if entry.define_as then
  a.define_as=nil;equal(Tokens.identify(a),nil,'UA no unbound zone boss '..id)
  a.define_as='WRONG_UA';equal(Tokens.identify(a),nil,'UA wrong define_as '..id)
  a.define_as=entry.define_as
 else
  a.define_as='UA_INVENTED';equal(Tokens.identify(a),nil,'UA no invented define_as '..id);a.define_as=nil
 end
 a.shader='unique_glow';equal(Tokens.identify(a),nil,'UA actor shader native '..id);a.shader=nil
 a.moddable_tile='humanoid';equal(Tokens.identify(a),nil,'UA paper doll native '..id);a.moddable_tile=nil
 a.name='Unknown '..entry.name;equal(Tokens.identify(a),nil,'UA arbitrary renamed unique native '..id);a.name=entry.name
 if ua_tall[id] then
  a.image='invis.png';a.add_mos={{image=entry.image,display_h=2,display_y=-1}}
  equal(Tokens.identify(a),id,'UA exact unique tall '..id)
  a.add_mos[1].display_h=3;equal(Tokens.identify(a),nil,'UA tall dimensions native '..id);a.add_mos[1].display_h=2
  a.add_mos[2]={image='npc/extra.png'};equal(Tokens.identify(a),nil,'UA extra composite native '..id);a.add_mos[2]=nil
  a.add_mos[2]={_isshaderaura=true,image='particles_images/wings.png'};equal(Tokens.identify(a),id,'UA independent native aura '..id)
 end
 -- The existing random-boss origin guard remains the only way to admit an
 -- opaque random name; exact verified unique tall sources already qualify.
 local capture=Tokens.captureRandomOrigin(a)
 local boss=copy(a);boss.randboss=true;boss.name='UA opaque random '..id;boss.unique=boss.name;boss.define_as='UA_RANDOM_'..id
 equal(Tokens.recordRandomOrigin(boss,capture,boss.define_as),id,'UA verified random provenance '..id)
 equal(Tokens.identify(boss),id,'UA recorded random copy '..id)
 boss._checker_token_origin=nil;equal(Tokens.identify(boss),nil,'UA random without provenance native '..id)
end
local bird=actor(Tokens.by_id.phoenix)
bird.image='object/egg_dragons_egg_06_64.png';equal(Tokens.identify(bird),nil,'UA Phoenix real egg remains native')
bird.image=Tokens.by_id.phoenix.image;equal(Tokens.identify(bird),'phoenix','UA Phoenix restored bird body')
equal(Tokens.identify({name='Grushnak, Battlemaster of the Pride',define_as='GRUSHNAK',unique=true,type='humanoid',subtype='orc',image='npc/humanoid_orc_grushnak__battlemaster_of_the_pride.png'}),'grushnak','UA Grushnak admitted after infrastructure retry')
equal(Tokens.identify({name='The Shade',define_as='SHADE',unique='The Shade',type='undead',subtype='skeleton',image='npc/undead_skeleton_the_shade.png',shader='unique_glow'}),nil,'UA unsupported Shade native')
-- Execute the two ACTUAL native Heart Gloom alter callbacks. Entity construction
-- has already stored unique as the original name before this load modifier.
local file=assert(io.open(here..'../../../modules/tome/data/zones/heart-gloom/npcs.lua','r'));local native=file:read('*a');file:close()
local first=assert(native:find('if not currentZone.is_purified then',1,true));local last=assert(native:find('load("/data/general/npcs/rodent.lua"',first,true))
local modifier=native:sub(first,last-1)
local old_t=_G._t
local prefix_names={'gloomy ','deformed ','sick ','dreaming ','slumbering ','dozing '}
local zh_prefixes={'黑暗的','畸形的','病态的','睡梦的','沉眠的','瞌睡的'} -- mod-tome.lua:38668–38673
for _,localized in ipairs({false,true}) do
 local translate=function(s)
  if not localized then return s end
  if s=='Rungof the Warg Titan' then return '泰坦座狼郎格夫' end -- mod-tome.lua:8060
  for n,p in ipairs(prefix_names) do if s==p then return zh_prefixes[n] end end
  return s
 end
 _G._t=translate
 for _,purified in ipairs({false,true}) do
  for n=1,3 do
   local env=setmetatable({currentZone={is_purified=purified},_t=translate,Talents=setmetatable({},{__index=function(_,k)return k end}),
    rng={table=function(t)return t[1]:sub(1,2)=='T_' and t[1] or t[n] end},resolvers={talents=function(t)return t end}}, {__index=_G})
   local chunk=assert(loadstring(modifier,'@native-heart-gloom-alter'));setfenv(chunk,env);chunk()
   local e=actor(Tokens.by_id.rungof);e.unique=e.name;e.life_rating=18;e.size_category=4;e.level_range={20};e.rarity=50
   e.getName=function(self)return translate(self.name) end
   env.alter(1)(e)
   equal(Tokens.identify(e),'rungof','UA native Heart Gloom same body '..tostring(localized)..' '..tostring(purified)..' '..n)
   local changed=copy(e);changed.unique=changed.name;equal(Tokens.identify(changed),nil,'UA no prefixed unique forgery')
   changed=copy(e);changed.life_rating=19;equal(Tokens.identify(changed),nil,'UA no wrong constructor life rating')
   changed=copy(e);changed.size_category=3;equal(Tokens.identify(changed),nil,'UA no wrong constructor size')
   changed=copy(e);changed.level_range={1};equal(Tokens.identify(changed),nil,'UA no wrong constructor range')
   changed=copy(e);changed.shader='shadow_simulacrum';equal(Tokens.identify(changed),nil,'UA prefix does not bypass shader')
   changed=copy(e);changed.image='npc/canine_warg.png';equal(Tokens.identify(changed),nil,'UA prefix does not bypass body')
   changed=copy(e);changed.define_as='FAKE_RUNGOF';equal(Tokens.identify(changed),nil,'UA prefix does not bypass define_as')
  end
 end
end
_G._t=old_t
local other=actor(Tokens.by_id['norgos-guardian']);other.name='dreaming '..other.name;equal(Tokens.identify(other),nil,'UA other unique prefixes remain native')
local Style=dofile(here..'../overload/mod/class/CheckerTokenStyle.lua')
for _,r in ipairs({{3.5,'unique'},{4,'boss'},{5,'elite_boss'}}) do equal(Style.rankBadge(r[1]),r[2],'UA rank layer stays independent '..r[1]) end

end

-- TA-1: town residents. Four native-tall Angolwen mages, six flat town guards
-- and the two Ring of Blood residents. All are non-unique with no define_as;
-- the slaver's make_escort copies are the same enthralled-slave body.
do
local ta1_ids = {"apprentice-mage","pyromancer","cryomancer","geomancer","tempest","human-guard","derth-guard","last-hope-guard","halfling-guard","dwarven-guard","elvala-guard","slaver","enthralled-slave"}
local ta1_tall = {pyromancer=true,cryomancer=true,geomancer=true,tempest=true}
local ta1_sub = {["halfling-guard"]="halfling",["dwarven-guard"]="dwarf",["elvala-guard"]="shalore",["slaver"]="yaech"}
for _,id in ipairs(ta1_ids) do
 local entry=Tokens.by_id[id]
 equal(entry~=nil,true,'TA1 catalog entry '..id)
 equal(entry.unique,nil,'TA1 non-unique entry '..id)
 equal(entry.define_as,nil,'TA1 no define_as '..id)
 equal(entry.native_tall==true,ta1_tall[id]==true,'TA1 native_tall flag '..id)
 equal(entry.subtype,ta1_sub[id] or 'human','TA1 subtype '..id)
 local a=actor(entry)
 equal(Tokens.identify(a),id,'TA1 exact identity '..id)
 a.define_as='INVENTED';equal(Tokens.identify(a),nil,'TA1 no invented define_as '..id);a.define_as=nil
 a.unique=entry.name;equal(Tokens.identify(a),nil,'TA1 no unique marker '..id);a.unique=nil
 a.shader='quad_hue';equal(Tokens.identify(a),nil,'TA1 any shader native '..id);a.shader=nil
 a.moddable_tile='humanoid';equal(Tokens.identify(a),nil,'TA1 paper doll native '..id);a.moddable_tile=nil
 a.anim='run';equal(Tokens.identify(a),nil,'TA1 animation native '..id);a.anim=nil
 local renamed=actor(entry);renamed.name='different town creature';equal(Tokens.identify(renamed),nil,'TA1 reused name native '..id)
 local changed=actor(entry);changed.type='undead';equal(Tokens.identify(changed),nil,'TA1 changed type native '..id)
 local moved=actor(entry);moved.image='npc/humanoid_human_human_citizen.png';equal(Tokens.identify(moved),nil,'TA1 changed body native '..id)
 if ta1_tall[id] then
  a.image='invis.png';a.add_mos={{image=entry.image,display_h=2,display_y=-1}}
  equal(Tokens.identify(a),id,'TA1 native-tall body '..id)
  local alt=copy(a);alt.add_mos[1].display_h=1;equal(Tokens.identify(alt),nil,'TA1 altered tall dimensions native '..id)
  alt=copy(a);alt.add_mos[1].image='npc/other.png';equal(Tokens.identify(alt),nil,'TA1 altered tall image native '..id)
  alt=copy(a);alt.add_mos[2]={image='npc/extra.png'};equal(Tokens.identify(alt),nil,'TA1 extra tall composite native '..id)
  alt=copy(a);alt.add_mos={{_isshaderaura=true,image=entry.image,display_h=2,display_y=-1},copy(a.add_mos[1])}
  equal(Tokens.identify(alt),id,'TA1 aura around tall body keeps token '..id)
 else
  local inv=actor(entry);inv.image='invis.png';equal(Tokens.identify(inv),nil,'TA1 flat body made invisible native '..id)
 end
end
-- The slaver make_escort builds type=humanoid, subtype=human, name="enthralled slave"
-- with the same default image, so the escort wears the enthralled-slave token.
local escort={name='enthralled slave',type='humanoid',subtype='human',image='npc/humanoid_human_enthralled_slave.png',faction='enemies',rank=2}
equal(Tokens.identify(escort),'enthralled-slave','TA1 slaver escort wears the slave token')
local impostor=copy(escort);impostor.image='npc/humanoid_human_human_citizen.png';equal(Tokens.identify(impostor),nil,'TA1 escort with another body native')
-- Any same-body copy of a resident keeps the token; a different name reusing the
-- apprentice mage sprite (e.g. the unmapped "Novice mage") stays native.
equal(Tokens.identify({name='human guard',type='humanoid',subtype='human',image='npc/humanoid_human_human_guard.png',faction='enemies',rank=2}),'human-guard','TA1 same-body copy keeps token')
equal(Tokens.identify({name='Novice mage',type='humanoid',subtype='human',image='npc/humanoid_human_apprentice_mage.png'}),nil,'TA1 different-name sprite reuse native')
end

-- UB-1: nine exact native-tall unique/boss bodies. High Aeryn is bound at two
-- native define sites with the same define_as, so one entry covers both.
-- Caldizar's two define sites share one byte-identical body: one shared token
-- is bound to CALDIZAR plus the second define_as CALDIZAR_AOADS.
do
local ub1_ids = {"high-sun-paladin-aeryn","fallen-sun-paladin-aeryn","caldizar","chronolith-twin","chronolith-clone","temporal-defiler","corrupted-daelach","supreme-archmage-linaniil","archmage-tarelion"}
local ub1_def = {["high-sun-paladin-aeryn"]="HIGH_SUN_PALADIN_AERYN",["fallen-sun-paladin-aeryn"]="FALLEN_SUN_PALADIN_AERYN",caldizar="CALDIZAR",["chronolith-twin"]="CHRONOLITH_TWIN",["chronolith-clone"]="CHRONOLITH_CLONE",["temporal-defiler"]="TEMPORAL_DEFILER",["corrupted-daelach"]="CORRUPTED_DAELACH",["supreme-archmage-linaniil"]="SUPREME_ARCHMAGE_LINANIIL",["archmage-tarelion"]="TARELION"}
local ub1_type = {["high-sun-paladin-aeryn"]={"humanoid","human"},["fallen-sun-paladin-aeryn"]={"humanoid","human"},caldizar={"horror","sher'tul"},["chronolith-twin"]={"horror","temporal"},["chronolith-clone"]={"horror","temporal"},["temporal-defiler"]={"horror","temporal"},["corrupted-daelach"]={"demon","major"},["supreme-archmage-linaniil"]={"humanoid","human"},["archmage-tarelion"]={"humanoid","shalore"}}
for _,id in ipairs(ub1_ids) do
 local entry=Tokens.by_id[id]
 equal(entry~=nil,true,'UB1 catalog entry '..id)
 equal(entry.unique,true,'UB1 unique entry '..id)
 equal(entry.native_tall,nil,'UB1 unique tall precedent without native_tall '..id)
 equal(entry.define_as,ub1_def[id],'UB1 define_as '..id)
 equal(entry.type,ub1_type[id][1],'UB1 type '..id)
 equal(entry.subtype,ub1_type[id][2],'UB1 subtype '..id)
 equal(entry.native_shader,nil,'UB1 no native shader '..id)
 equal(entry.urh_rok_form,nil,'UB1 no urh_rok_form opt-in '..id)
 if id=='caldizar' then equal(entry.shared_name,true,'UB1 caldizar shared token');equal(entry.define_as_alias,'CALDIZAR_AOADS','UB1 caldizar second bound define_as')
 else equal(entry.shared_name,nil,'UB1 single shared token '..id) end
 -- exact one-body native-tall contract (invis.png + a single add_mos)
 local a=actor(entry);a.unique=true;a.image='invis.png';a.add_mos={{image=entry.image,display_h=2,display_y=-1}}
 equal(Tokens.identify(a),id,'UB1 exact native-tall body '..id)
 local alt=copy(a);alt.add_mos[1].display_h=3;equal(Tokens.identify(alt),nil,'UB1 altered tall dimensions native '..id)
 alt=copy(a);alt.add_mos[1].display_y=0;equal(Tokens.identify(alt),nil,'UB1 altered tall offset native '..id)
 alt=copy(a);alt.add_mos[1].image='npc/other.png';equal(Tokens.identify(alt),nil,'UB1 altered tall image native '..id)
 alt=copy(a);alt.add_mos[2]={image='npc/extra.png'};equal(Tokens.identify(alt),nil,'UB1 extra composite native '..id)
 alt=copy(a);alt.add_mos[2]={_isshaderaura=true,image='particles_images/wings.png'};equal(Tokens.identify(alt),id,'UB1 independent native aura '..id)
 alt=copy(a);alt.add_mos[1].shader='quad_hue';equal(Tokens.identify(alt),nil,'UB1 body-layer shader native '..id)
 -- actor-level visual modifiers
 local full=actor(entry);full.unique=true
 full.shader='unique_glow';equal(Tokens.identify(full),nil,'UB1 actor shader native '..id);full.shader=nil
 full.moddable_tile='humanoid';equal(Tokens.identify(full),nil,'UB1 paper doll native '..id);full.moddable_tile=nil
 full.anim='run';equal(Tokens.identify(full),nil,'UB1 animation native '..id);full.anim=nil
 full.add_displays={{image='x.png'}};equal(Tokens.identify(full),nil,'UB1 add-displays native '..id);full.add_displays=nil
 -- define_as is required and exact
 full.define_as=nil;equal(Tokens.identify(full),nil,'UB1 missing define_as native '..id)
 full.define_as='WRONG_UB1';equal(Tokens.identify(full),nil,'UB1 wrong define_as native '..id)
 full.define_as=ub1_def[id];equal(Tokens.identify(full),id,'UB1 restored define_as '..id)
 -- an arbitrary renamed unique stays native
 local renamed=actor(entry);renamed.unique=true;renamed.name='Unknown '..entry.name;equal(Tokens.identify(renamed),nil,'UB1 arbitrary renamed unique native '..id)
end
-- High Aeryn's second native define site and unique marker string still resolve
-- to the same single entry.
do
 local gom={name='High Sun Paladin Aeryn',type='humanoid',subtype='human',image='npc/humanoid_human_high_sun_paladin_aeryn.png',define_as='HIGH_SUN_PALADIN_AERYN',unique=true}
 equal(Tokens.identify(gom),'high-sun-paladin-aeryn','UB1 gates-of-morning high Aeryn')
 gom.unique='High Sun Paladin Aeryn High Peak Help'
 equal(Tokens.identify(gom),'high-sun-paladin-aeryn','UB1 high-peak marker string high Aeryn')
 gom.image='npc/humanoid_human_fallen_sun_paladin_aeryn.png'
 equal(Tokens.identify(gom),nil,'UB1 high Aeryn cannot take the fallen body')
end
-- The one shared Caldizar token serves both byte-identical bodies.
do
 local fortress={name='Caldizar',type='horror',subtype="sher'tul",image='npc/horror_sher_tul_caldizar.png',define_as='CALDIZAR',unique='Caldizar Unknown Fortress'}
 local ao={name='Caldizar',type='horror',subtype="sher'tul",image='npc/horror_sher_tul_caldizar.png',define_as='CALDIZAR_AOADS',unique='Caldizar AOADS'}
 equal(Tokens.identify(fortress),'caldizar','UB1 fortress Caldizar shared token')
 equal(Tokens.identify(ao),'caldizar','UB1 AOADS Caldizar shared token')
 local fake=copy(fortress);fake.define_as='CALDIZAR_INVENTED';equal(Tokens.identify(fake),nil,'UB1 caldizar no invented define_as')
 local swapped=copy(ao);swapped.image='npc/horror_temporal_temporal_defiler.png';equal(Tokens.identify(swapped),nil,'UB1 caldizar shared token needs the shared body')
 local wrong=copy(fortress);wrong.type='demon';equal(Tokens.identify(wrong),nil,'UB1 caldizar shared token needs horror/sher-tul body')
end
-- Twin vs Clone are separate bodies; the Corrupted Daelach is not the daelach.
do
 local twin=Tokens.by_id['chronolith-twin'];local clone=Tokens.by_id['chronolith-clone']
 equal(twin.image~=clone.image,true,'UB1 twin and clone have distinct native bodies')
 local wrong=actor(twin);wrong.unique=true;wrong.image=clone.image;equal(Tokens.identify(wrong),nil,'UB1 twin cannot wear the clone body')
 local daelach={name='daelach',type='demon',subtype='major',image='npc/demon_major_daelach.png',native_tall=true}
 equal(Tokens.identify(daelach),'daelach','UB1 daelach keeps its own token')
 local corrupt=actor(Tokens.by_id['corrupted-daelach']);corrupt.unique=true
 equal(Tokens.identify(corrupt),'corrupted-daelach','UB1 corrupted daelach exact')
 corrupt.image='npc/demon_major_daelach.png';equal(Tokens.identify(corrupt),nil,'UB1 corrupted daelach cannot wear the daelach body')
end
-- Tarelion resolves its {tall=true} shorthand to the same single body (R20).
do
 local t=actor(Tokens.by_id['archmage-tarelion']);t.unique=true
 t.image='invis.png';t.add_mos={{image='npc/humanoid_shalore_archmage_tarelion.png',display_h=2,display_y=-1}}
 equal(Tokens.identify(t),'archmage-tarelion','UB1 tarelion tall shorthand body')
 t.add_mos[1].display_h=1;equal(Tokens.identify(t),nil,'UB1 tarelion altered shorthand native')
end
-- Rank badges stay an independent layer, as UA/TA-1.
local UBStyle=dofile(here..'../overload/mod/class/CheckerTokenStyle.lua')
for _,r in ipairs({{3.5,'unique'},{4,'boss'},{5,'elite_boss'}}) do equal(UBStyle.rankBadge(r[1]),r[2],'UB1 rank layer stays independent '..r[1]) end
end

-- UB-2: ten flat 64x64 unique/boss identities, each with an exact define_as,
-- plus the wiring-only Ben Cruthdar, the Cursed.
do
local ub2_ids = {"sun-paladin-guren","epoch","corrupted-oozemancer","zemekkys","blood-master","limmir-the-jeweler","protector-myssil","rak-shor-cultist","shady-cornac-man","tannen"}
local ub2_def = {["sun-paladin-guren"]="SUN_PALADIN_GUREN",epoch="EPOCH",["corrupted-oozemancer"]="CORRUPTED_OOZEMANCER",zemekkys="ZEMEKKYS",["blood-master"]="RING_MASTER",["limmir-the-jeweler"]="LIMMIR",["protector-myssil"]="PROTECTOR_MYSSIL",["rak-shor-cultist"]="CULTIST_RAK_SHOR",["shady-cornac-man"]="ARENA_AGENT",tannen="TANNEN"}
local ub2_type = {["sun-paladin-guren"]={"humanoid","human"},epoch={"elemental","temporal"},["corrupted-oozemancer"]={"giant","troll"},zemekkys={"humanoid","shalore"},["blood-master"]={"humanoid","yaech"},["limmir-the-jeweler"]={"humanoid","elf"},["protector-myssil"]={"humanoid","halfling"},["rak-shor-cultist"]={"humanoid","orc"},["shady-cornac-man"]={"humanoid","human"},tannen={"humanoid","human"}}
for _,id in ipairs(ub2_ids) do
 local entry=Tokens.by_id[id]
 equal(entry~=nil,true,'UB2 catalog entry '..id)
 equal(entry.unique,true,'UB2 unique entry '..id)
 equal(entry.native_tall,nil,'UB2 flat body without a native_tall flag '..id)
 equal(entry.define_as,ub2_def[id],'UB2 define_as '..id)
 equal(entry.type,ub2_type[id][1],'UB2 type '..id)
 equal(entry.subtype,ub2_type[id][2],'UB2 subtype '..id)
 equal(entry.native_shader,nil,'UB2 no native shader '..id)
 equal(entry.urh_rok_form,nil,'UB2 no urh_rok_form opt-in '..id)
 equal(entry.shared_name,nil,'UB2 no shared name '..id)
 local a=actor(entry)
 equal(Tokens.identify(a),id,'UB2 exact flat identity '..id)
 a.define_as=nil;equal(Tokens.identify(a),nil,'UB2 missing define_as native '..id);a.define_as=ub2_def[id]
 a.define_as='WRONG_UB2';equal(Tokens.identify(a),nil,'UB2 wrong define_as native '..id);a.define_as=ub2_def[id]
 a.unique=true;equal(Tokens.identify(a),id,'UB2 unique marker '..id)
 a.shader='unique_glow';equal(Tokens.identify(a),nil,'UB2 actor shader native '..id);a.shader=nil
 a.moddable_tile='humanoid';equal(Tokens.identify(a),nil,'UB2 paper doll native '..id);a.moddable_tile=nil
 a.anim='run';equal(Tokens.identify(a),nil,'UB2 animation native '..id);a.anim=nil
 a.add_displays={{image='x.png'}};equal(Tokens.identify(a),nil,'UB2 add-displays native '..id);a.add_displays=nil
 a.image='npc/other.png';equal(Tokens.identify(a),nil,'UB2 changed body native '..id);a.image=entry.image
 local renamed=actor(entry);renamed.name='Unknown '..entry.name;equal(Tokens.identify(renamed),nil,'UB2 arbitrary renamed unique native '..id)
 local changed=actor(entry);changed.type='undead';equal(Tokens.identify(changed),nil,'UB2 changed type native '..id)
 local mixed=actor(entry);mixed.add_mos={{image='unknown-overlay.png'}};equal(Tokens.identify(mixed),nil,'UB2 extra body overlay native '..id)
end
-- Ben Cruthdar, the Cursed is wiring-only: it reuses the Abomination token and
-- the Abomination entry stays exactly as shipped.
do
 local cursed=Tokens.by_id['ben-cruthdar-the-cursed']
 local abom=Tokens.by_id['ben-cruthdar-abomination']
 equal(cursed~=nil,true,'UB2 cursed catalog entry')
 equal(cursed.unique,true,'UB2 cursed unique')
 equal(cursed.define_as,'BEN_CRUTHDAR','UB2 cursed define_as')
 equal(cursed.type,'humanoid','UB2 cursed type')
 equal(cursed.subtype,'human','UB2 cursed subtype')
 equal(cursed.image,abom.image,'UB2 cursed and abomination share the native PNG')
 equal(abom.name,'Ben Cruthdar, the Abomination','UB2 abomination name unchanged')
 equal(abom.define_as,'BEN_CRUTHDAR_ABOMINATION','UB2 abomination define_as unchanged')
 equal(abom.type,'humanoid','UB2 abomination type unchanged')
 equal(abom.subtype,'temporal','UB2 abomination subtype unchanged')
 equal(abom.unique,true,'UB2 abomination unique unchanged')
 local c=actor(cursed);c.unique=true
 equal(Tokens.identify(c),'ben-cruthdar-the-cursed','UB2 cursed exact name+define_as')
 local a=actor(abom);a.unique=true
 equal(Tokens.identify(a),'ben-cruthdar-abomination','UB2 abomination still exact')
 equal(Tokens.identify({name='Ben Cruthdar, the Cursed',type='humanoid',subtype='temporal',image=cursed.image,define_as='BEN_CRUTHDAR',unique=true}),nil,'UB2 cursed wrong subtype native')
 equal(Tokens.identify({name='Ben Cruthdar, the Abomination',type='humanoid',subtype='temporal',image=abom.image,define_as='BEN_CRUTHDAR',unique=true}),nil,'UB2 abomination wrong define_as native')
 local swapped=copy(c);swapped.define_as='BEN_CRUTHDAR_ABOMINATION';equal(Tokens.identify(swapped),nil,'UB2 cursed cannot take the abomination define_as')
 local framed=copy(c);framed.image='npc/humanoid_human_ben_cruthdar__the_cursed.png';framed.define_as='BEN_CRUTHDAR'
 equal(Tokens.identify(framed),'ben-cruthdar-the-cursed','UB2 cursed restores exact body')
end

-- Rank badges stay an independent layer, as UA/TA-1/UB-1.
local UB2Style=dofile(here..'../overload/mod/class/CheckerTokenStyle.lua')
for _,r in ipairs({{3.5,'unique'},{4,'boss'},{5,'elite_boss'}}) do equal(UB2Style.rankBadge(r[1]),r[2],'UB2 rank layer stays independent '..r[1]) end
end


print(("token_mapping: %d checks passed; all %d identities and guarded fallbacks verified"):format(checks,#Tokens.catalog))
