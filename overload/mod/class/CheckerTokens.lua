-- Creature identity only. Faction, rank, visibility and display ownership are
-- handled by the actor integration; none belongs in the artwork lookup key.
local M = {}

-- The standee size gate and its height table live in CheckerTokenStyle so there
-- is a single source of truth. Normal runtime resolution is require; the
-- dofile/loadfile unit harnesses fall back to the module sitting next to this
-- file so the gate they exercise is the shipped one.
local function loadStyle()
	local ok,mod=pcall(require,'mod.class.CheckerTokenStyle')
	if ok and type(mod)=='table' then return mod end
	local source=debug.getinfo(1,'S').source
	if type(source)=='string' and source:sub(1,1)=='@' then
		local dir=source:sub(2):match('^(.*[/\\])') or './'
		local fn=loadfile(dir..'CheckerTokenStyle.lua')
		if fn then
			local ok2,mod2=pcall(fn)
			if ok2 and type(mod2)=='table' then return mod2 end
		end
	end
end
local Style=loadStyle()

M.catalog = {
	{id="forest-troll", name="forest troll", image="npc/troll_f.png", type="giant", subtype="troll"},
	{id="wolf", name="wolf", image="npc/canine_w.png", type="animal", subtype="canine"},
	{id="brown-bear", name="brown bear", image="npc/brown_bear.png", type="animal", subtype="bear"},
	{id="brown-snake", name="large brown snake", image="npc/umber-snake.png", type="animal", subtype="snake"},
	{id="venus-flytrap", name="giant venus flytrap", image="npc/immovable_plants_giant_venus_flytrap.png", type="immovable", subtype="plants"},
	{id="stone-troll", name="stone troll", image="npc/troll_s.png", type="giant", subtype="troll"},
	{id="cave-troll", name="cave troll", image="npc/troll_c.png", type="giant", subtype="troll"},
	{id="prox", name="Prox the Mighty", image="npc/giant_troll_prox_the_mighty.png", type="giant", subtype="troll", define_as="TROLL_PROX", unique=true},
	{id="bill", name="Bill the Stone Troll", image="npc/troll_bill.png", type="giant", subtype="troll", define_as="TROLL_BILL", unique=true},
	{id="great-wolf", name="great wolf", image="npc/canine_gw.png", type="animal", subtype="canine"},
	{id="fox", name="fox", image="npc/canine_fox.png", type="animal", subtype="canine"},
	{id="black-bear", name="black bear", image="npc/black_bear.png", type="animal", subtype="bear"},
	{id="brown-rat", name="giant brown rat", image="npc/vermin_rodent_giant_brown_rat.png", type="vermin", subtype="rodent"},
	{id="king-cobra", name="king cobra", image="npc/green-snake.png", type="animal", subtype="snake"},
	{id="bee-swarm", name="bee swarm", image="npc/bee_swarm.png", type="insect", subtype="swarms"},
	{id="giant-eel", name="giant eel", image="npc/aquatic_critter_giant_eel.png", type="aquatic", subtype="critter"},
	{id="dragon-turtle", name="dragon turtle", image="npc/aquatic_critter_dragon_turtle.png", type="aquatic", subtype="critter"},
	-- Source-verified flooded Trollmire pool members; ordinary squids are excluded
	-- by the native zone loader. Ancient turtle alone has a non-unique tall body.
	{id="electric-eel", name="electric eel", image="npc/aquatic_critter_electric_eel.png", type="aquatic", subtype="critter"},
	{id="ancient-dragon-turtle", name="ancient dragon turtle", image="npc/aquatic_critter_ancient_dragon_turtle.png", type="aquatic", subtype="critter", native_tall=true},
	{id="dire-wolf", name="dire wolf", image="npc/canine_dw.png", type="animal", subtype="canine"},
	{id="white-wolf", name="white wolf", image="npc/canine_ww.png", type="animal", subtype="canine"},
	{id="warg", name="warg", image="npc/canine_warg.png", type="animal", subtype="canine"},
	{id="white-snake", name="large white snake", image="npc/white-snake.png", type="animal", subtype="snake"},
	{id="rattlesnake", name="rattlesnake", image="npc/firebrick-snake.png", type="animal", subtype="snake"},
	{id="midge-swarm", name="midge swarm", image="npc/midge_swarm.png", type="insect", subtype="swarms"},
	{id="hornet-swarm", name="hornet swarm", image="npc/hornet_swarm.png", type="insect", subtype="swarms"},
	{id="white-worm-mass", name="white worm mass", image="npc/vermin_worms_white_worm_mass.png", type="vermin", subtype="worms"},
	-- Resolved in isolated KorPul DEFAULT/HIDEOUT fixtures (native final identity).
	{id="degenerated-skeleton-warrior", name="degenerated skeleton warrior", image="npc/degenerated_skeleton_warrior.png", type="undead", subtype="skeleton"},
	{id="degenerated-skeleton-archer", name="degenerated skeleton archer", image="npc/undead_skeleton_degenerated_skeleton_archer.png", type="undead", subtype="skeleton"},
	{id="skeleton-mage", name="skeleton mage", image="npc/skeleton_mage.png", type="undead", subtype="skeleton"},
	{id="grey-mold", name="grey mold", image="npc/immovable_molds_grey_mold.png", type="immovable", subtype="molds"},
	{id="cutpurse", name="cutpurse", image="npc/humanoid_human_cutpurse.png", type="humanoid", subtype="human"},
	{id="rogue", name="rogue", image="npc/humanoid_human_rogue.png", type="humanoid", subtype="human"},
	{id="thief", name="thief", image="npc/humanoid_human_thief.png", type="humanoid", subtype="human"},
	-- A native definition identifier is not a unique/boss marker.
	{id="bandit", name="bandit", image="npc/humanoid_human_bandit.png", type="humanoid", subtype="human", define_as="THIEF_BANDIT"},
	-- C0: ordinary single-image bodies, resolved in both KorPul layouts.
	{id="giant-white-rat", name="giant white rat", image="npc/vermin_rodent_giant_white_rat.png", type="vermin", subtype="rodent"},
	{id="giant-grey-rat", name="giant grey rat", image="npc/vermin_rodent_giant_grey_rat.png", type="vermin", subtype="rodent"},
	{id="green-worm-mass", name="green worm mass", image="npc/vermin_worms_green_worm_mass.png", type="vermin", subtype="worms"},
	{id="copperhead-snake", name="copperhead snake", image="npc/salmon-snake.png", type="animal", subtype="snake"},
	-- C0b: the rest of the shared rodent table plus three more molds. All resolved
	-- detached in KorPul DEFAULT; every display modifier empty, so each is a plain
	-- single-image body. See evidence/c0b-art-gate/.
	{id="giant-white-mouse", name="giant white mouse", image="npc/vermin_rodent_giant_white_mouse.png", type="vermin", subtype="rodent"},
	{id="giant-brown-mouse", name="giant brown mouse", image="npc/vermin_rodent_giant_brown_mouse.png", type="vermin", subtype="rodent"},
	{id="giant-grey-mouse", name="giant grey mouse", image="npc/vermin_rodent_giant_grey_mouse.png", type="vermin", subtype="rodent"},
	{id="giant-rabbit", name="giant rabbit", image="npc/vermin_rodent_giant_rabbit.png", type="vermin", subtype="rodent"},
	{id="giant-crystal-rat", name="giant crystal rat", image="npc/vermin_rodent_giant_crystal_rat.png", type="vermin", subtype="rodent"},
	{id="brown-mold", name="brown mold", image="npc/immovable_molds_brown_mold.png", type="immovable", subtype="molds"},
	{id="green-mold", name="green mold", image="npc/immovable_molds_green_mold.png", type="immovable", subtype="molds"},
	{id="shining-mold", name="shining mold", image="npc/immovable_molds_shining_mold.png", type="immovable", subtype="molds"},
	-- 0.6.10 V9-refine: "skeleton warrior" passed the same C0b admission gate but
	-- its C0b art exhausted that batch's two-call budget on disc overflow. A
	-- separately reviewed refinement brief changed the pose (greatsword held
	-- vertical, point down, along the body axis) and the new art clears the gate,
	-- so the identity is covered from here on. "armoured skeleton warrior" is a
	-- different, shield-carrying identity and stays uncovered.
	{id="skeleton-warrior", name="skeleton warrior", image="npc/skeleton_warrior.png", type="undead", subtype="skeleton"},
	-- E1: jelly (immovable/jelly, never_move=1, no can_multiply/clone_on_hit) and
	-- ooze (vermin/oozes, mobile, clone_on_hit={min_dam_pct=15,chance=30}) resolved
	-- detached from direct npc_class:loadList (neither family is in KorPul's own
	-- npc_list); every display modifier empty. See evidence/e1-art-gate/. Only the
	-- 4 jelly + 4 ooze colours admitted this round; green ooze, red/blue jelly,
	-- crimson ooze and gelatinous cube are deferred to E1b.
	{id="green-jelly", name="green jelly", image="npc/jelly-green.png", type="immovable", subtype="jelly"},
	{id="black-jelly", name="black jelly", image="npc/jelly-darkgrey.png", type="immovable", subtype="jelly"},
	{id="white-jelly", name="white jelly", image="npc/jelly-white.png", type="immovable", subtype="jelly"},
	{id="yellow-jelly", name="yellow jelly", image="npc/jelly-yellow.png", type="immovable", subtype="jelly"},
	{id="black-ooze", name="black ooze", image="npc/vermin_oozes_black_ooze.png", type="vermin", subtype="oozes"},
	{id="yellow-ooze", name="yellow ooze", image="npc/vermin_oozes_yellow_ooze.png", type="vermin", subtype="oozes"},
	{id="red-ooze", name="red ooze", image="npc/vermin_oozes_red_ooze.png", type="vermin", subtype="oozes"},
	{id="blue-ooze", name="blue ooze", image="npc/vermin_oozes_blue_ooze.png", type="vermin", subtype="oozes"},
	-- E1b (batch D): completes the 6-colour jelly family. green ooze, crimson
	-- ooze, gelatinous cube and Malevolent Dimensional Jelly have no image= in
	-- source (leaf or BASE_NPC_OOZE/BASE_NPC_JELLY) and verifying their
	-- resolved appearance needs the isolated fixture the way E1's four ooze
	-- colours were verified (evidence/e1-art-gate); this art-only, no-fixture
	-- batch cannot repeat that step, so those four stay native. See
	-- evidence/monster-batch-d-20260929/.
	{id="red-jelly", name="red jelly", image="npc/jelly-red.png", type="immovable", subtype="jelly"},
	{id="blue-jelly", name="blue jelly", image="npc/jelly-blue.png", type="immovable", subtype="jelly"},
	-- E3 (batch D): new giant-ant family, all six colours now shipped. giant
	-- white/yellow ant cleared the style gate on first/second pass with no
	-- waiver. giant brown/blue ant cleared every gate except base_drift (both
	-- attempts each, +8.39/+8.45, tolerance +-8) and are admitted under the
	-- reviewer-approved exact-byte waiver in
	-- art/production/waivers/monster-batch-d.json (reviewer decision
	-- 2026-09-29, see art/monster-batch-d/REVIEW.md). giant carpenter/black
	-- ant's first draft was rejected in that same decision (nearly
	-- indistinguishable at 48px, both black with pincers too small to read);
	-- a calibrated redraw (monster-batch-d-4, giving carpenter huge pale
	-- ivory-grey mandibles as a value cue plus a raised stance, and giving
	-- black a hunched posture with mandibles the same dark tone as its head)
	-- cleared the gate cleanly with no waiver (base_drift -7.27/-5.43). elven
	-- guard/mean looking elven guard/elven mage/elven tempest have no image=
	-- and draw native paper-doll equipment from the item pool
	-- (resolvers.equip), so they stay native too; see
	-- evidence/monster-batch-d-20260929/.
	{id="giant-white-ant", name="giant white ant", image="npc/white_ant.png", type="insect", subtype="ant"},
	{id="giant-yellow-ant", name="giant yellow ant", image="npc/yellow_ant.png", type="insect", subtype="ant"},
	{id="giant-brown-ant", name="giant brown ant", image="npc/brown_ant.png", type="insect", subtype="ant"},
	{id="giant-blue-ant", name="giant blue ant", image="npc/blue_ant.png", type="insect", subtype="ant"},
	{id="giant-carpenter-ant", name="giant carpenter ant", image="npc/carpenter_ant.png", type="insect", subtype="ant"},
	{id="giant-black-ant", name="giant black ant", image="npc/black_ant.png", type="insect", subtype="ant"},
	-- Batch A guardians: source-verified unique native-tall identities. Failed
	-- art candidates remain absent here so they keep their native presentation.
	{id="wrathroot", name="Wrathroot", image="npc/giant_treant_wrathroot.png", type="giant", subtype="treant", define_as="WRATHROOT", unique=true},
	{id="snaproot", name="Snaproot", image="npc/giant_treant_snaproot.png", type="giant", subtype="treant", define_as="SNAPROOT", unique=true},
	{id="minotaur-maze", name="Minotaur of the Labyrinth", image="npc/giant_minotaur_minotaur_of_the_labyrinth.png", type="giant", subtype="minotaur", define_as="MINOTAUR_MAZE", unique=true},
	{id="sandworm-queen", name="Sandworm Queen", image="npc/vermin_sandworm_sandworm_queen.png", type="vermin", subtype="sandworm", define_as="SANDWORM_QUEEN", unique=true},
	{id="corrupted-sand-wyrm", name="Corrupted Sand Wyrm", image="npc/dragon_sand_corrupted_sand_wyrm.png", type="dragon", subtype="sand", define_as="CORRUPTED_SAND_WYRM", unique=true},
	{id="rantha", name="Rantha the Worm", image="npc/dragon_ice_rantha_the_worm.png", type="dragon", subtype="ice", define_as="RANTHA_THE_WORM", unique=true},
	{id="varsha", name="Varsha the Writhing", image="npc/dragon_fire_varsha_the_writhing.png", type="dragon", subtype="fire", define_as="VARSHA_THE_WRITHING", unique=true},
	{id="norgos-frozen", name="Norgos, the Frozen", image="npc/animal_bear_norgos_the_frozen.png", type="animal", subtype="bear", define_as="FROZEN_NORGOS", unique=true},
	-- Batch B: exact native identities. The three guardians retain their verified
	-- native-tall appearance contract; no subtype-wide substitution is used.
	{id="shax", name="Shax the Slimy", image="npc/giant_troll_shax_the_slimy.png", type="giant", subtype="troll", define_as="TROLL_SHAX", unique=true},
	{id="horned-horror", name="Horned Horror", image="npc/horror_corrupted_horner_horror.png", type="horror", subtype="corrupted", define_as="HORNED_HORROR", unique=true},
	{id="norgos-guardian", name="Norgos, the Guardian", image="npc/animal_bear_norgos_the_guardian.png", type="animal", subtype="bear", define_as="NORGOS", unique=true},
	{id="skeleton-archer", name="skeleton archer", image="npc/skeleton_archer.png", type="undead", subtype="skeleton"},
	{id="armoured-skeleton-warrior", name="armoured skeleton warrior", image="npc/armored_skeleton_warrior.png", type="undead", subtype="skeleton"},
	-- Batch C: the black-and-gold armoured redraw replaces the rejected batch-B draft.
	{id="skeleton-master-archer", name="skeleton master archer", image="npc/master_skeleton_archer.png", type="undead", subtype="skeleton"},
	-- Batch E: all 12 recommended zone-finale bosses (CONTRACTS-B5-B7-20260929.md
	-- §2). 5 cleared the style gate outright or via a targeted repair, no
	-- waiver. The other 7 (urkis, golbug, ungole, half-finished-bone-giant,
	-- kryl-feijan, atamathon, ritch-hive-mother) failed only base_drift and
	-- ship under the reviewer-approved exact-byte waiver in
	-- art/production/waivers/monster-batch-e.json (reviewer decision
	-- 2026-09-29, see art/monster-batch-e/REVIEW.md and
	-- evidence/monster-batch-e-20260929/source-contracts.json). Atamathon maps
	-- only the verified native-tall body (invis.png + add_mos); its documented
	-- nicer_tiles-off npc/atamathon.png single-icon fallback is intentionally
	-- left native and unmapped. Ritch Great Hive Mother has no nice_tile/
	-- add_mos on its leaf (a plain top-level image=) and resolves via the same
	-- generic actor.image==entry.image "single" path as every non-tall entry
	-- above, not nativeTallImage. Ungolë and Kryl-Feijan are dark subjects on
	-- the dark base disc and were specifically checked at 48px on real floor
	-- tiles in the isolated fixture; see evidence/monster-live-e-20260929/.
	{id="lady-zoisla", name="Lady Zoisla the Tidebringer", image="npc/humanoid_naga_lady_zoisla_the_tidebringer.png", type="humanoid", subtype="naga", define_as="ZOISLA", unique=true},
	{id="brotoq", name="Brotoq the Reaver", image="npc/humanoid_orc_brotoq_the_reaver.png", type="humanoid", subtype="orc", define_as="BROTOQ", unique=true},
	{id="the-mouth", name="The Mouth", image="npc/horror_corrupted_the_mouth.png", type="horror", subtype="corrupted", define_as="THE_MOUTH", unique=true},
	{id="the-abomination", name="The Abomination", image="npc/horror_corrupted_the_abomination.png", type="horror", subtype="corrupted", define_as="ABOMINATION", unique=true},
	{id="celia", name="Celia", image="npc/humanoid_human_celia.png", type="humanoid", subtype="human", define_as="CELIA", unique=true},
	{id="urkis", name="Urkis, the High Tempest", image="npc/humanoid_human_urkis__the_high_tempest.png", type="humanoid", subtype="human", define_as="URKIS", unique=true},
	{id="golbug", name="Golbug the Destroyer", image="npc/humanoid_orc_golbug_the_destroyer.png", type="humanoid", subtype="orc", define_as="GOLBUG", unique=true},
	{id="ungole", name="Ungolë", image="npc/spiderkin_spider_ungole.png", type="spiderkin", subtype="spider", define_as="UNGOLE", unique=true},
	{id="half-finished-bone-giant", name="Half-Finished Bone Giant", image="npc/undead_giant_half_finished_bone_giant.png", type="undead", subtype="giant", define_as="HALF_BONE_GIANT", unique=true},
	-- Batch F redraw (identity/display contract unchanged from batch E above):
	-- the batch-E master read as an almost pure black blob at 48px on a real
	-- dark stone floor in the isolated fixture (evidence/monster-live-e-20260929
	-- /crops/kryl-feijan-placed-crypt-kryl-feijan-L5-48-crop.png), a known
	-- limitation recorded but not fixed at the time. Three redraw attempts:
	-- v1 kept the same near-black body (rejected, unchanged problem); -b
	-- cleared the style gate by leaving the disc unmodified but measured
	-- pixel luminance found its creature body statistically as dark as the
	-- original (mean 59.0 vs 59.3, rejected -- the gate pass did not fix the
	-- actual defect); -c explicitly asked for a pale storm-cloud-grey body
	-- and measured mean luminance 85.4 (+44% over the original), a genuine,
	-- verified brightening that also cleared the style gate (base_drift
	-- -8.00) with no waiver. The batch-E base_drift waiver entry for
	-- kryl-feijan is superseded and no longer needed. See
	-- art/monster-batch-f/REVIEW.md.
	{id="kryl-feijan", name="Kryl-Feijan", image="npc/demon_major_kryl_feijan.png", type="demon", subtype="major", define_as="KRYL_FEIJAN", unique=true},
	{id="atamathon", name="Atamathon the Giant Golem", image="npc/construct_golem_athamathon_the_giant_golem.png", type="construct", subtype="golem", define_as="ATAMATHON", unique=true},
	{id="ritch-hive-mother", name="Ritch Great Hive Mother", image="npc/insect_ritch_ritch_hive_mother.png", type="insect", subtype="ritch", define_as="HIVE_MOTHER", unique=true},
	-- Batch F: three of the CONTRACTS-B5-B7-20260929.md 4.1
	-- "NEEDS-CONTRACT-EXTENSION" identities -- non-unique native-tall bodies
	-- (invis.png+add_mos, source literal), following the ancient-dragon-turtle
	-- precedent (native_tall=true above) rather than a code change. All three
	-- shipped art cleared the style gate cleanly (no waiver): naga tidewarden
	-- (armed warrior, trident+shield) and naga tidecaller (robed staff
	-- caster) read as clearly different silhouettes at every size, and both
	-- differ from the existing unique naga (lady-zoisla) too. xhaiak
	-- arachnomancer and shiaak venomblade use the resolvers.nice_tile{tall=1}
	-- shorthand with no image= literal anywhere in their inheritance chain;
	-- tracing engine/Zone.lua:633 (Zone:finishEntity resolves a
	-- pre-instantiation clone, before mod/class/NPC.lua:33's default-name
	-- backfill can have run) could not establish their resolved add_mos image
	-- with confidence, so both stay native and unmapped -- see
	-- evidence/monster-batch-f-20260929/source-contracts.json and
	-- evidence/monster-live-f-20260929/ for the runtime probe.
	{id="naga-tidewarden", name="naga tidewarden", image="npc/humanoid_naga_naga_tidewarden.png", type="humanoid", subtype="naga", define_as="NAGA_TIDEWARDEN", native_tall=true},
	{id="naga-tidecaller", name="naga tidecaller", image="npc/humanoid_naga_naga_tidecaller.png", type="humanoid", subtype="naga", define_as="NAGA_TIDECALLER", native_tall=true},
	-- Batch F: treant (CONTRACTS-B5-B7-20260929.md section 1 correction --
	-- originally miscategorised in the pure-art "batch 5" list, actually the
	-- same invis.png+add_mos contract-extension shape as the identities
	-- above). Ships clean, no waiver.
	{id="treant", name="treant", image="npc/immovable_plants_treant.png", type="immovable", subtype="plants", native_tall=true},
	-- Batch F: shivgoroth and greater shivgoroth, the remaining two of the
	-- three same-shape contract-verified NEEDS-CONTRACT-EXTENSION candidates
	-- above. Both first-elemental/ice identities missed only base_drift on
	-- the style gate (magnitude 3.23 / 1.40 over the +-8 tolerance) and ship
	-- under the reviewer-approved exact-byte waiver in
	-- art/production/waivers/monster-batch-f.json (reviewer decision
	-- 2026-09-29, see art/monster-batch-f/REVIEW.md). Family separation
	-- (shape and value, not only size) holds at 48/64/96px in both color and
	-- grayscale: shivgoroth is lean, low and hunched translucent mid-blue;
	-- greater shivgoroth is broad, upright and bright frost-white. The third
	-- candidate in the same request, dremling, was rejected by the reviewer
	-- (dark subject on a dark base, the same 48px failure as the superseded
	-- monster-batch-e kryl-feijan master) and stays native and unmapped --
	-- see art/production/waivers/monster-batch-f-PENDING-REQUEST.json.
	{id="shivgoroth", name="shivgoroth", image="npc/elemental_ice_shivgoroth.png", type="elemental", subtype="ice", native_tall=true},
	{id="greater-shivgoroth", name="greater shivgoroth", image="npc/elemental_ice_greater_shivgoroth.png", type="elemental", subtype="ice", native_tall=true},
	-- Batch G: the two spiderkin bodies and the redrawn dremling. xhaiak
	-- arachnomancer and shiaak venomblade use resolvers.nice_tile{tall=1};
	-- the isolated-fixture probe in evidence/monster-live-f-20260929/ settled
	-- that both resolve to invis.png + add_mos{display_h=2, display_y=-1} of
	-- the disk-filename-formula image, the same native-tall shape as
	-- ancient-dragon-turtle, so native_tall=true applies. They are separated
	-- from each other and from Ungole by silhouette, not colour alone
	-- (xhaiak: spindly pale-cloth spider-humanoid; shiaak: squat sage-green
	-- thorn mass with two blades; Ungole: round black spider) and neither can
	-- wear the other's resolved body (tests/token_mapping.lua). dremling was
	-- redrawn in pale weathered stone after batch F rejected the near-black
	-- draft as dark-on-dark; masked-body luminance rose from 39.8 to 90.6 and
	-- the style gate passes cleanly (base_drift +3.37, no waiver). Its real
	-- art file is npc/horror_corrupted_drem.png (the filename swap with drem
	-- is unchanged; batch K later mapped drem itself to its own
	-- horror_corrupted_dremling.png single-cell body).
	{id="xhaiak-arachnomancer", name="xhaiak arachnomancer", image="npc/spiderkin_xhaiak_xhaiak_arachnomancer.png", type="spiderkin", subtype="xhaiak", native_tall=true},
	{id="shiaak-venomblade", name="shiaak venomblade", image="npc/spiderkin_shiaak_shiaak_venomblade.png", type="spiderkin", subtype="shiaak", native_tall=true},
	{id="dremling", name="dremling", image="npc/horror_corrupted_drem.png", type="horror", subtype="corrupted", native_tall=true},
	-- Batch G uniques (sources and display contracts re-verified in
	-- evidence/monster-batch-g-20260929/source-contracts.json). Pale Drake,
	-- Fillarel Aldaren and Krogar are native-tall (invis.png + add_mos) and
	-- Spellblaze Crystal, The Master, Rhaloren Inquisitor, Harno and
	-- Lithfengel are single-image; all pass the style gate with no waiver.
	-- Massok the Dragonslayer (daikara/npcs.lua:163, native-tall
	-- invis.png + add_mos) ships under the reviewer-approved exact-byte
	-- base_drift waiver (-10.32) in art/production/waivers/monster-batch-g.json
	-- (decision 2026-09-29, art/monster-batch-g/REVIEW.md).
	-- Pale Drake (undead/skeleton, robed archmage with skull staff), The Master
	-- (undead/vampire, crimson-and-ivory robe) and the seven shipped skeletons
	-- are separated by silhouette and value; see art/monster-batch-g/REVIEW.md.
	{id="pale-drake", name="Pale Drake", image="npc/undead_skeleton_pale_drake.png", type="undead", subtype="skeleton", define_as="PALE_DRAKE", unique=true},
	{id="the-master", name="The Master", image="npc/the_master.png", type="undead", subtype="vampire", define_as="THE_MASTER", unique=true},
	{id="fillarel-aldaren", name="Fillarel Aldaren", image="npc/humanoid_elf_fillarel_aldaren.png", type="humanoid", subtype="elf", define_as="FILLAREL", unique=true},
	{id="krogar", name="Krogar", image="npc/humanoid_orc_krogar.png", type="humanoid", subtype="orc", define_as="CORRUPTOR", unique=true},
	{id="spellblaze-crystal", name="Spellblaze Crystal", image="npc/spellblaze_crystal.png", type="immovable", subtype="crystal", define_as="SPELLBLAZE_CRYSTAL", unique=true},
	{id="rhaloren-inquisitor", name="Rhaloren Inquisitor", image="npc/humanoid_shalore_rhaloren_inquisitor.png", type="humanoid", subtype="shalore", define_as="INQUISITOR", unique=true},
	{id="harno", name="Harno, Herald of Last Hope", image="npc/humanoid_human_harno__herald_of_last_hope.png", type="humanoid", subtype="human", define_as="HARNO", unique=true},
	{id="lithfengel", name="Lithfengel", image="npc/demon_major_lithfengel.png", type="demon", subtype="major", define_as="LITHFENGEL", unique=true},
	{id="massok", name="Massok the Dragonslayer", image="npc/humanoid_orc_massok_the_dragonslayer.png", type="humanoid", subtype="orc", define_as="MASSOK", unique=true},
	-- Batch H: twelve ordinary (non-unique) identities, each an exact
	-- single-image entry re-verified against source in
	-- evidence/monster-batch-h-20260929/source-contracts.json (no image=/
	-- nice_tile/add_mos on any of them; whole subtypes are never mapped).
	-- Sandworms: sandworm, destroyer and the scripted sandworm-lair burrower
	-- (define_as SANDWORM_TUNNELER) sit beside sandworm-queen and differ by
	-- silhouette (slim S-curve, closed armoured ring, two green arches over a
	-- sand heap) and value, not hue alone. sand-drake (dragon/sand), the
	-- corrosive tunneler, gravity worm and the huge burrower remain native
	-- (batch K mapped only the gigantic sandworm tunneler).
	{id="sandworm", name="sandworm", image="npc/vermin_sandworm_sandworm.png", type="vermin", subtype="sandworm"},
	{id="sandworm-destroyer", name="sandworm destroyer", image="npc/vermin_sandworm_sandworm_destroyer.png", type="vermin", subtype="sandworm"},
	{id="sandworm-burrower", name="sandworm burrower", image="npc/vermin_sandworm_sandworm_burrower.png", type="vermin", subtype="sandworm", define_as="SANDWORM_TUNNELER"},
	-- Crystals: white/red/crimson are told apart from each other and from
	-- Spellblaze Crystal by shape (tall vertical bouquet, long horizontal
	-- blade fan, two blocky prisms vs a round purple cluster) and value. The
	-- native tint is a colour modulation only and does not affect the match.
	-- shimmering crystal natively shares white crystal's PNG but is another
	-- name and stays native; black/blue crystal are not covered.
	{id="white-crystal", name="white crystal", image="npc/crystal_npc.png", type="immovable", subtype="crystal"},
	{id="red-crystal", name="red crystal", image="npc/crystal_red.png", type="immovable", subtype="crystal"},
	{id="crimson-crystal", name="crimson crystal", image="npc/crystal_darkred.png", type="immovable", subtype="crystal"},
	-- Plants next to the venus flytrap: an open vine web and a real tree.
	{id="poison-ivy", name="poison ivy", image="npc/immovable_plants_poison_ivy.png", type="immovable", subtype="plants"},
	{id="honey-tree", name="honey tree", image="npc/immovable_plants_honey_tree.png", type="immovable", subtype="plants"},
	-- Blighted-ruins: the non-unique Necromancer (define_as NECROMANCER; the
	-- orc necromancer and Rak'shor are different names) and the three
	-- stationary experiments: lumpy flesh mound, ivory spiky bone pile and a
	-- smooth glossy scarlet clot.
	{id="necromancer", name="Necromancer", image="npc/humanoid_human_necromancer.png", type="humanoid", subtype="human", define_as="NECROMANCER"},
	{id="fleshy-experiment", name="fleshy experiment", image="npc/undead_horror_fleshy_experiment.png", type="undead", subtype="horror"},
	{id="boney-experiment", name="boney experiment", image="npc/undead_horror_boney_experiment.png", type="undead", subtype="horror"},
	{id="sanguine-experiment", name="sanguine experiment", image="npc/undead_horror_sanguine_experiment.png", type="undead", subtype="horror"},
	-- Batch I: twelve exact identities re-verified statically against source
	-- (evidence/monster-batch-i-20260929/source-contracts.json). green/crimson
	-- ooze and gelatinous cube have no image=/nice_tile anywhere in their
	-- chain, so NPC.lua:33 gives npc/vermin_oozes_<name>.png exactly as it did
	-- for the shipped black/yellow/red/blue ooze; Malevolent Dimensional Jelly
	-- (unique, no define_as) likewise gets npc/immovable_jelly_*.png while
	-- the other jellies carry explicit images. The Tempest Peak trio and the
	-- Simulacrum are unique native-tall (nice_tile); Harkor'Zun's fragments
	-- and the full demon are two separate entries. Norgan, the acolyte
	-- (explicit corruptor portrait, bound to define_as ACOLYTE so the elven
	-- corruptor stays native), slimy crawler and Z'quikzshl (type overridden
	-- to undead/molds) are exact single images.
	{id="green-ooze", name="green ooze", image="npc/vermin_oozes_green_ooze.png", type="vermin", subtype="oozes"},
	{id="crimson-ooze", name="crimson ooze", image="npc/vermin_oozes_crimson_ooze.png", type="vermin", subtype="oozes"},
	{id="gelatinous-cube", name="gelatinous cube", image="npc/vermin_oozes_gelatinous_cube.png", type="vermin", subtype="oozes"},
	{id="malevolent-dimensional-jelly", name="Malevolent Dimensional Jelly", image="npc/immovable_jelly_malevolent_dimensional_jelly.png", type="immovable", subtype="jelly", unique=true},
	{id="harkor-zun-fragment", name="The Fragmented Essence of Harkor'Zun", image="npc/elemental_xorn_fragmented_harkor_zun.png", type="elemental", subtype="xorn", unique=true},
	{id="harkor-zun", name="Harkor'Zun", image="npc/elemental_xorn_harkor_zun.png", type="demon", subtype="major", define_as="FULL_HARKOR_ZUN", unique=true},
	{id="burb-snow-giant-champion", name="Burb the snow giant champion", image="npc/giant_ice_burb_the_snow_giant_champion.png", type="giant", subtype="ice", define_as="BURB_SNOW_GIANT", unique=true},
	{id="norgan", name="Norgan", image="npc/humanoid_dwarf_norgan.png", type="humanoid", subtype="dwarf", define_as="NORGAN", unique=true},
	{id="slimy-crawler", name="slimy crawler", image="npc/horror_corrupted_slimy_crawler.png", type="horror", subtype="corrupted", define_as="SLIMY_CRAWLER"},
	{id="spellblaze-simulacrum", name="Spellblaze Simulacrum", image="npc/spellblaze_simulacrum.png", type="immovable", subtype="crystal", define_as="SPELLBLAZE_SIMULACRUM", unique=true},
	{id="kryl-feijan-acolyte", name="Acolyte of the Sect of Kryl-Feijan", image="npc/humanoid_shalore_elven_corruptor.png", type="humanoid", subtype="elf", define_as="ACOLYTE"},
	{id="zquikzshl", name="Z'quikzshl the skeletal mold", image="npc/immovable_molds_skeletal_mold.png", type="undead", subtype="molds", unique=true},
	-- Batch J: the guaranteed bosses/uniques of the second gap survey,
	-- re-verified against source (evidence/monster-batch-j-20260929/
	-- source-contracts.json). Shardskin, The Withering Thing (purple tint is
	-- only colour modulation), The Dreaming One, Murgol, Subject Z, the Grand
	-- Corruptor (town-zigur defines a second same-named, same-define_as,
	-- same-image Grand Corruptor with unique="Grand Corruptor Zigur"; it is
	-- the same character, so this entry serves it too), Assassin Lord and Ben
	-- Cruthdar the Abomination are single-image uniques. Weaver Queen, Lady
	-- Nashva and The Possessed are unique native-tall: nice_tile names the PNG
	-- explicitly. Ben Cruthdar the Cursed (town-lumberjack-village) shares
	-- Ben's PNG but is another name; since UB-2 it has its own exact
	-- name+define_as entry (BEN_CRUTHDAR) that reuses the abomination runtime
	-- token. Kyless uses the
	-- nice_tile{tall=1} shorthand with no image= (resolve-time image is nil,
	-- see batch F) and stays native.
	{id="shardskin", name="Shardskin", image="npc/immovable_crystal_golden_crystal.png", type="giant", subtype="crystal", define_as="SHARDSKIN", unique=true},
	{id="the-withering-thing", name="The Withering Thing", image="npc/animal_canine_the_withering_thing.png", type="animal", subtype="canine", define_as="WITHERING_THING", unique=true},
	{id="the-dreaming-one", name="The Dreaming One", image="npc/seed_of_dreams.png", type="horror", subtype="eldritch", define_as="DREAMING_ONE", unique=true},
	{id="weaver-queen", name="Weaver Queen", image="npc/spiderkin_spider_weaver_queen.png", type="spiderkin", subtype="spider", define_as="WEAVER_QUEEN", unique=true},
	{id="murgol", name="Murgol, the Yaech Lord", image="npc/humanoid_yaech_murgol__the_yaech_lord.png", type="humanoid", subtype="yaech", define_as="MURGOL", unique=true},
	{id="lady-nashva", name="Lady Nashva the Streambender", image="npc/humanoid_naga_lady_nashva_the_streambender.png", type="humanoid", subtype="naga", define_as="NASHVA", unique=true},
	{id="the-possessed", name="The Possessed", image="npc/humanoid_human_the_possessed.png", type="humanoid", subtype="human", define_as="THE_POSSESSED", unique=true},
	{id="subject-z", name="Subject Z", image="npc/humanoid_human_subject_z.png", type="humanoid", subtype="human", define_as="SUBJECT_Z", unique=true},
	{id="grand-corruptor", name="Grand Corruptor", image="npc/humanoid_shalore_grand_corruptor.png", type="humanoid", subtype="shalore", define_as="GRAND_CORRUPTOR", unique=true, urh_rok_form=true},
	{id="assassin-lord", name="Assassin Lord", image="npc/humanoid_human_assassin_lord.png", type="humanoid", subtype="human", define_as="ASSASSIN_LORD", unique=true},
	{id="ben-cruthdar-abomination", name="Ben Cruthdar, the Abomination", image="npc/humanoid_human_ben_cruthdar__the_cursed.png", type="humanoid", subtype="temporal", define_as="BEN_CRUTHDAR_ABOMINATION", unique=true},
	-- Batch K: twelve identities of the second survey's batch 2, each
	-- re-verified against source (evidence/monster-batch-k-20260929/
	-- source-contracts.json). squid, ink squid, water imp, orb spinner,
	-- giant/spitting/chitinous spider are default-name single images; weaver
	-- hatchling and drem carry an explicit image= (drem's is the PNG named
	-- after dremling; dremling resolves to horror_corrupted_drem.png, so the
	-- two entries swap files and neither can wear the other's). ghoul is
	-- bound to define_as GHOUL: the Master of Flesh minion shares its name,
	-- type and PNG but has no define_as; the "ghoul" variant accepts it. The tutorial's
	-- "giant spider" (define_as TUT_SPIDER_1) and the wild-gift summon
	-- (type animal) are rejected by define_as / type. Walrog (unique, no
	-- define_as) and the gigantic sandworm tunneler (non-unique,
	-- native_tall) name their PNG explicitly in nice_tile, so the resolved
	-- tall body is static (unlike the {tall=1} shorthand of batch F/J).
	{id="squid", name="squid", image="npc/aquatic_critter_squid.png", type="aquatic", subtype="critter"},
	{id="ink-squid", name="ink squid", image="npc/aquatic_critter_ink_squid.png", type="aquatic", subtype="critter"},
	{id="water-imp", name="water imp", image="npc/aquatic_demon_water_imp.png", type="aquatic", subtype="demon"},
	{id="walrog", name="Walrog", image="npc/aquatic_demon_walrog.png", type="aquatic", subtype="demon", unique=true},
	{id="weaver-hatchling", name="weaver hatchling", image="npc/spiderkin_spider_weaver_young.png", type="spiderkin", subtype="spider"},
	{id="orb-spinner", name="orb spinner", image="npc/spiderkin_spider_orb_spinner.png", type="spiderkin", subtype="spider"},
	{id="giant-spider", name="giant spider", image="npc/spiderkin_spider_giant_spider.png", type="spiderkin", subtype="spider"},
	{id="spitting-spider", name="spitting spider", image="npc/spiderkin_spider_spitting_spider.png", type="spiderkin", subtype="spider"},
	{id="chitinous-spider", name="chitinous spider", image="npc/spiderkin_spider_chitinous_spider.png", type="spiderkin", subtype="spider"},
	{id="ghoul", name="ghoul", image="npc/undead_ghoul_ghoul.png", type="undead", subtype="ghoul", define_as="GHOUL"},
	{id="drem", name="drem", image="npc/horror_corrupted_dremling.png", type="horror", subtype="corrupted"},
	{id="gigantic-sandworm-tunneler", name="gigantic sandworm tunneler", image="npc/vermin_sandworm_gigantic_sandworm_tunneler.png", type="vermin", subtype="sandworm", native_tall=true},
	-- Batch L: survey-2 batch 3 (orcs, shalore elves, nagas, yaech diver) plus
	-- Kyless, each re-verified against source (evidence/monster-batch-l-
	-- 20260929/source-contracts.json). The three ordinary orcs are bound to
	-- their define_as values (HILL_ORC_WARRIOR, ORC, HILL_ORC_ARCHER): the
	-- Charred Scar attacker is also named "orc warrior" but has define_as
	-- ORC_ATTACK and stays native. The elves and the yaech diver are
	-- default-name single images; the naga myrmidon names its PNG explicitly
	-- (npc/naga_myrmidon.png). The naga nereid (two zone definitions, one
	-- identity) is non-unique native_tall through the {tall=1} shorthand, the
	-- same expansion live-confirmed for xhaiak/shiaak/tidewarden/tidecaller;
	-- Kyless uses that shorthand as a unique and the batch J live census
	-- showed his add_mos naming npc/humanoid_human_kyless.png, so he is an
	-- ordinary unique native-tall entry. The elven cultist was kept native
	-- by batch L (Flame of Urh'Rok at birth, no live check yet); batch M maps
	-- it after the batch L live check recorded its demon/major form.
	{id="orc-warrior", name="orc warrior", image="npc/humanoid_orc_orc_warrior.png", type="humanoid", subtype="orc", define_as="HILL_ORC_WARRIOR"},
	{id="orc-soldier", name="orc soldier", image="npc/humanoid_orc_orc_soldier.png", type="humanoid", subtype="orc", define_as="ORC"},
	{id="orc-archer", name="orc archer", image="npc/humanoid_orc_orc_archer.png", type="humanoid", subtype="orc", define_as="HILL_ORC_ARCHER"},
	{id="naga-myrmidon", name="naga myrmidon", image="npc/naga_myrmidon.png", type="humanoid", subtype="naga"},
	{id="elven-guard", name="elven guard", image="npc/humanoid_shalore_elven_guard.png", type="humanoid", subtype="shalore"},
	{id="mean-looking-elven-guard", name="mean looking elven guard", image="npc/humanoid_shalore_mean_looking_elven_guard.png", type="humanoid", subtype="shalore"},
	{id="naga-nereid", name="naga nereid", image="npc/humanoid_naga_naga_nereid.png", type="humanoid", subtype="naga", native_tall=true},
	{id="elven-mage", name="elven mage", image="npc/humanoid_shalore_elven_mage.png", type="humanoid", subtype="shalore"},
	{id="elven-tempest", name="elven tempest", image="npc/humanoid_shalore_elven_tempest.png", type="humanoid", subtype="shalore"},
	{id="elven-blood-mage", name="elven blood mage", image="npc/humanoid_shalore_elven_blood_mage.png", type="humanoid", subtype="shalore"},
	{id="yaech-diver", name="yaech diver", image="npc/humanoid_yaech_yaech_diver.png", type="humanoid", subtype="yaech"},
	{id="kyless", name="Kyless", image="npc/humanoid_human_kyless.png", type="humanoid", subtype="human", define_as="KYLESS", unique=true},
	-- Batch M: survey-2 batch 4 (void, temporal, air, fire and xorn elementals)
	-- plus the elven cultist, each re-verified against source (evidence/
	-- monster-batch-m-20260929/source-contracts.json). Nine elementals are
	-- default-name single images with no define_as. Greater and ultimate
	-- gwelgoroth are non-unique native_tall entries and Fyrk (define_as FYRK) a
	-- unique one; all three name their tall PNG explicitly in nice_tile, so the
	-- body is statically pinnable (greater faeros is a plain 64x64 image; the
	-- tall one is ultimate faeros, which stays native). Fyrk's Burning Wake
	-- aura is an ignored _isshaderaura entry. Name look-alikes such as
	-- "monstrous losgoroth" differ in name and stay native. The elven cultist
	-- is born demon/major with Flame of Urh'Rok sustained (live-checked in
	-- batch L), the same form as the Grand Corruptor, so it opts into
	-- urh_rok_form; batch L kept it native and batch M maps it.
	{id="losgoroth", name="losgoroth", image="npc/elemental_void_losgoroth.png", type="elemental", subtype="void"},
	{id="manaworm", name="manaworm", image="npc/elemental_void_manaworm.png", type="elemental", subtype="void"},
	{id="telugoroth", name="telugoroth", image="npc/elemental_temporal_telugoroth.png", type="elemental", subtype="temporal"},
	{id="gwelgoroth", name="gwelgoroth", image="npc/elemental_air_gwelgoroth.png", type="elemental", subtype="air"},
	{id="greater-gwelgoroth", name="greater gwelgoroth", image="npc/elemental_air_greater_gwelgoroth.png", type="elemental", subtype="air", native_tall=true},
	{id="ultimate-gwelgoroth", name="ultimate gwelgoroth", image="npc/elemental_air_ultimate_gwelgoroth.png", type="elemental", subtype="air", native_tall=true},
	{id="faeros", name="faeros", image="npc/elemental_fire_faeros.png", type="elemental", subtype="fire"},
	{id="greater-faeros", name="greater faeros", image="npc/elemental_fire_greater_faeros.png", type="elemental", subtype="fire"},
	{id="fyrk", name="Fyrk, Faeros High Guard", image="npc/elemental_fire_fyrk__faeros_high_guard.png", type="elemental", subtype="fire", define_as="FYRK", unique=true},
	{id="umber-hulk", name="umber hulk", image="npc/elemental_xorn_umber_hulk.png", type="elemental", subtype="xorn"},
	{id="xorn", name="xorn", image="npc/elemental_xorn_xorn.png", type="elemental", subtype="xorn"},
	{id="xaren", name="xaren", image="npc/elemental_xorn_xaren.png", type="elemental", subtype="xorn"},
	{id="elven-cultist", name="elven cultist", image="npc/humanoid_shalore_elven_cultist.png", type="humanoid", subtype="shalore", urh_rok_form=true},
	-- Batch N: survey-2 batch 5 (undead), each re-verified against source
	-- (evidence/monster-batch-n-20260929/source-contracts.json). Skeleton
	-- magus, ghast, ghoulking and The Shade of Telos use the NPC.lua:33
	-- default-name image; the vampires, wights and shadow stalker name their
	-- PNG explicitly. Master vampire and bone giant are non-unique native_tall
	-- entries whose nice_tile names the tall PNG explicitly; elder vampire is a
	-- plain 64x64 image. The shadow stalker (define_as SHADOW_STALKER) shares
	-- its base with the two "shadow claw" siblings, which have other PNGs and
	-- stay native, and the Shade of Telos is a unique bound to SHADE_OF_TELOS. The vampires' birth
	-- sustains (Eternal Night, Blur Sight, Phantasmal Shield) add only
	-- particles and temporary values, and no identity here knows Flame of
	-- Urh'Rok. Necromancer minions named ghast, ghoulking and bone giant are
	-- the same body and art; a Lord of Skulls renames its minion and stays
	-- native.
	{id="skeleton-magus", name="skeleton magus", image="npc/undead_skeleton_skeleton_magus.png", type="undead", subtype="skeleton"},
	{id="ghast", name="ghast", image="npc/undead_ghoul_ghast.png", type="undead", subtype="ghoul"},
	{id="ghoulking", name="ghoulking", image="npc/undead_ghoul_ghoulking.png", type="undead", subtype="ghoul"},
	{id="bone-giant", name="bone giant", image="npc/undead_giant_bone_giant.png", type="undead", subtype="giant", native_tall=true},
	{id="lesser-vampire", name="lesser vampire", image="npc/lesser_vampire.png", type="undead", subtype="vampire"},
	{id="vampire", name="vampire", image="npc/vampire.png", type="undead", subtype="vampire"},
	{id="master-vampire", name="master vampire", image="npc/master_vampire.png", type="undead", subtype="vampire", native_tall=true},
	{id="elder-vampire", name="elder vampire", image="npc/elder_vampire.png", type="undead", subtype="vampire"},
	{id="forest-wight", name="forest wight", image="npc/forest_wight.png", type="undead", subtype="wight"},
	{id="grave-wight", name="grave wight", image="npc/grave_wight.png", type="undead", subtype="wight"},
	{id="shadow-stalker", name="shadow stalker", image="npc/shadow-stalker.png", type="undead", subtype="shadow", define_as="SHADOW_STALKER"},
	{id="shade-of-telos", name="The Shade of Telos", image="npc/undead_ghost_the_shade_of_telos.png", type="undead", subtype="ghost", define_as="SHADE_OF_TELOS", unique=true},
	-- Batch O: survey-2 batch 6 (oozes, worms, minor demons, horrors), each
	-- re-verified against source (evidence/monster-batch-o-20260929/
	-- source-contracts.json). The four oozes, bunny, dredgling, wretchling and
	-- brecklorn use the NPC.lua:33 default-name image. The carrion worm mass is
	-- bound to define_as CARRION_WORM_MASS: the Worm Rot / Infestation summon
	-- shares its name, type and PNG but has no define_as; the "carrion-worm-mass"
	-- variant accepts it.
	-- The two gigantic worms (batch K kept them native) are non-unique
	-- native_tall entries whose nice_tile names the tall PNG explicitly; the
	-- onilug is non-unique native_tall through the {tall=1} shorthand
	-- (live-confirmed for xhaiak, shiaak and the naga nereid). Brecklorn's
	-- Gloom and every other talent here write no type/subtype/image/add_mos.
	{id="white-ooze", name="white ooze", image="npc/vermin_oozes_white_ooze.png", type="vermin", subtype="oozes"},
	{id="slimy-ooze", name="slimy ooze", image="npc/vermin_oozes_slimy_ooze.png", type="vermin", subtype="oozes"},
	{id="poison-ooze", name="poison ooze", image="npc/vermin_oozes_poison_ooze.png", type="vermin", subtype="oozes"},
	{id="brittle-clear-ooze", name="brittle clear ooze", image="npc/vermin_oozes_brittle_clear_ooze.png", type="vermin", subtype="oozes"},
	{id="gigantic-corrosive-tunneler", name="gigantic corrosive tunneler", image="npc/vermin_sandworm_gigantic_corrosive_tunneler.png", type="vermin", subtype="sandworm", native_tall=true},
	{id="gigantic-gravity-worm", name="gigantic gravity worm", image="npc/vermin_sandworm_gigantic_gravity_worm.png", type="vermin", subtype="sandworm", native_tall=true},
	{id="carrion-worm-mass", name="carrion worm mass", image="npc/vermin_worms_carrion_worm_mass.png", type="vermin", subtype="worms", define_as="CARRION_WORM_MASS"},
	{id="cute-little-bunny", name="cute little bunny", image="npc/vermin_rodent_cute_little_bunny.png", type="vermin", subtype="rodent"},
	{id="dredgling", name="dredgling", image="npc/horror_temporal_dredgling.png", type="horror", subtype="temporal"},
	{id="onilug", name="onilug", image="npc/demon_minor_onilug.png", type="demon", subtype="minor", native_tall=true},
	{id="wretchling", name="wretchling", image="npc/demon_minor_wretchling.png", type="demon", subtype="minor"},
	{id="brecklorn", name="brecklorn", image="npc/horror_corrupted_brecklorn.png", type="horror", subtype="corrupted"},
	-- Batch P: survey-2 batch 7 (snow giants, minotaur, mountain trolls,
	-- ogres and Healer Astelrid), each re-verified against source (evidence/
	-- monster-batch-p-20260929/source-contracts.json). The four snow giants and
	-- the minotaur are non-unique native_tall entries whose nice_tile names the
	-- tall PNG explicitly; the four ogres are non-unique native_tall through
	-- the {tall=1} shorthand (live-confirmed for xhaiak, shiaak, the naga
	-- nereid and Kyless) and Healer Astelrid, a unique bound to
	-- HEALER_ASTELRID, uses the same shorthand. The two mountain trolls carry
	-- an explicit 64x64 image= and are plain single entries. Astelrid's
	-- birth sustains (Arcane Shield, Living Lightning) and every other talent
	-- write no type/subtype/image/add_mos. Same-name look-alikes with the
	-- same body and art (the Summon Minotaur wild gift, the Elvala town ogre
	-- rune-spinner) match like the zone leaves; an open decision.
	{id="snow-giant", name="snow giant", image="npc/giant_ice_snow_giant.png", type="giant", subtype="ice", native_tall=true},
	{id="snow-giant-thunderer", name="snow giant thunderer", image="npc/giant_ice_snow_giant_thunderer.png", type="giant", subtype="ice", native_tall=true},
	{id="snow-giant-boulder-thrower", name="snow giant boulder thrower", image="npc/giant_ice_snow_giant_boulder_thrower.png", type="giant", subtype="ice", native_tall=true},
	{id="snow-giant-chieftain", name="snow giant chieftain", image="npc/giant_ice_snow_giant_chieftain.png", type="giant", subtype="ice", native_tall=true},
	{id="minotaur", name="minotaur", image="npc/giant_minotaur_minotaur.png", type="giant", subtype="minotaur", native_tall=true},
	{id="mountain-troll", name="mountain troll", image="npc/troll_m.png", type="giant", subtype="troll"},
	{id="mountain-troll-thunderer", name="mountain troll thunderer", image="npc/troll_mt.png", type="giant", subtype="troll"},
	{id="ogre-guard", name="ogre guard", image="npc/giant_ogre_ogre_guard.png", type="giant", subtype="ogre", native_tall=true},
	{id="ogre-mauler", name="ogre mauler", image="npc/giant_ogre_ogre_mauler.png", type="giant", subtype="ogre", native_tall=true},
	{id="ogre-rune-spinner", name="ogre rune-spinner", image="npc/giant_ogre_ogre_rune_spinner.png", type="giant", subtype="ogre", native_tall=true},
	{id="ogre-pounder", name="ogre pounder", image="npc/giant_ogre_ogre_pounder.png", type="giant", subtype="ogre", native_tall=true},
	{id="healer-astelrid", name="Healer Astelrid", image="npc/giant_ogre_healer_astelrid.png", type="giant", subtype="ogre", define_as="HEALER_ASTELRID", unique=true},
	-- Batch Q: survey-2 batch 8 (the four drake hatchlings and adults, the
	-- sand-drake, Ukllmswwik the Wise, Rantha the Abomination and Briagh), each
	-- re-verified against source (evidence/monster-batch-q-20260929/
	-- source-contracts.json). The drakes, hatchlings, sand-drake and Ukllmswwik
	-- have no image=/nice_tile: the NPC.lua:33 default-name PNG is a single
	-- 64x64 image. The fire drake hatchling (FIRE_DRAKE_HATCHLING) and the cold
	-- drake (NPC_COLD_DRAKE) leaves carry a define_as that the entries bind
	-- exactly; the Wyrmic Grand Arrival hatchling (no define_as) is accepted by
	-- the "fire-drake-hatchling" variant, and the Wyrmic Fire Drake summon
	-- (same name/type/PNG, no define_as) matches the zone fire drake. Ukllmswwik is a
	-- unique single image. Rantha the Abomination and Briagh are uniques whose
	-- nice_tile names the tall PNG explicitly (unique native-tall like Walrog).
	-- Their birth sustains (Icy Skin) and every talent write no type/subtype/
	-- image/add_mos; Briagh's Summoner auto_class may add a Master Summoner
	-- shader aura, an already supported appearance.
	{id="fire-drake-hatchling", name="fire drake hatchling", image="npc/dragon_fire_fire_drake_hatchling.png", type="dragon", subtype="fire", define_as="FIRE_DRAKE_HATCHLING"},
	{id="cold-drake-hatchling", name="cold drake hatchling", image="npc/dragon_cold_cold_drake_hatchling.png", type="dragon", subtype="cold"},
	{id="storm-drake-hatchling", name="storm drake hatchling", image="npc/dragon_storm_storm_drake_hatchling.png", type="dragon", subtype="storm"},
	{id="sand-drake", name="sand-drake", image="npc/dragon_sand_sand_drake.png", type="dragon", subtype="sand"},
	{id="venom-drake-hatchling", name="venom drake hatchling", image="npc/dragon_venom_venom_drake_hatchling.png", type="dragon", subtype="venom"},
	{id="rantha-abomination", name="Rantha the Abomination", image="npc/dragon_temporal_rantha_the_abomination.png", type="dragon", subtype="temporal", define_as="ABOMINATION_RANTHA", unique=true},
	{id="briagh", name="Briagh, Great Sand Wyrm", image="npc/dragon_sand_briagh__great_sand_wyrm.png", type="dragon", subtype="sand", define_as="BRIAGH", unique=true},
	{id="ukllmswwik", name="Ukllmswwik the Wise", image="npc/dragon_water_ukllmswwik_the_wise.png", type="dragon", subtype="water", define_as="UKLLMSWWIK", unique=true},
	{id="fire-drake", name="fire drake", image="npc/dragon_fire_fire_drake.png", type="dragon", subtype="fire"},
	{id="storm-drake", name="storm drake", image="npc/dragon_storm_storm_drake.png", type="dragon", subtype="storm"},
	{id="cold-drake", name="cold drake", image="npc/dragon_cold_cold_drake.png", type="dragon", subtype="cold", define_as="NPC_COLD_DRAKE"},
	{id="venom-drake", name="venom drake", image="npc/dragon_venom_venom_drake.png", type="dragon", subtype="venom"},
	-- Batch R: the twelve next identities by score of the second survey's
	-- follow-up list (art/monster-batch-r/SELECTION.md), each re-verified
	-- against source (evidence/monster-batch-r-20260929/source-contracts.json).
	-- None is native-tall: every native sprite is 64x64 with no nice_tile. The
	-- orc necromancer, orc assassin, weaver young, fate spinner, quasit, elven
	-- warrior, grannor'vor, Warmaster Gnarg and Rak'shor use the NPC.lua:33
	-- default-name PNG; the giant green and red ants and the corrupted war dog
	-- name their PNG explicitly with image=. Gnarg (GNARG), Rak'shor (RAK_SHOR)
	-- and the war dog (CORRUPTED_WAR_DOG) are bound to their define_as. Weaver
	-- young shares its native PNG with the weaver hatchling and the war dog
	-- shares canine_dw.png with the dire wolf: different names, separate
	-- entries, each matched by its own name. Rak'shor's Corruptor auto_class
	-- could teach Flame of Urh'Rok after level 35; that turns him demon/major
	-- with the sprite untouched, so he opts into urh_rok_form (2026-09-29).
	{id="orc-necromancer", name="orc necromancer", image="npc/humanoid_orc_orc_necromancer.png", type="humanoid", subtype="orc"},
	{id="rak-shor", name="Rak'shor, Grand Necromancer of the Pride", image="npc/humanoid_orc_rak_shor__grand_necromancer_of_the_pride.png", type="humanoid", subtype="orc", define_as="RAK_SHOR", unique=true, urh_rok_form=true},
	{id="warmaster-gnarg", name="Warmaster Gnarg", image="npc/humanoid_orc_warmaster_gnarg.png", type="humanoid", subtype="orc", define_as="GNARG", unique=true},
	{id="orc-assassin", name="orc assassin", image="npc/humanoid_orc_orc_assassin.png", type="humanoid", subtype="orc"},
	{id="weaver-young", name="weaver young", image="npc/spiderkin_spider_weaver_young.png", type="spiderkin", subtype="spider"},
	{id="fate-spinner", name="fate spinner", image="npc/spiderkin_spider_fate_spinner.png", type="spiderkin", subtype="spider"},
	{id="giant-green-ant", name="giant green ant", image="npc/green_ant.png", type="insect", subtype="ant"},
	{id="giant-red-ant", name="giant red ant", image="npc/red_ant.png", type="insect", subtype="ant"},
	{id="quasit", name="quasit", image="npc/demon_minor_quasit.png", type="demon", subtype="minor"},
	{id="elven-warrior", name="elven warrior", image="npc/humanoid_shalore_elven_warrior.png", type="humanoid", subtype="shalore"},
	{id="corrupted-war-dog", name="corrupted war dog", image="npc/canine_dw.png", type="animal", subtype="canine", define_as="CORRUPTED_WAR_DOG"},
	{id="grannor-vor", name="grannor'vor", image="npc/horror_corrupted_grannor_vor.png", type="horror", subtype="corrupted"},
	-- Batch S: the next twelve identities under the batch R score rule
	-- (art/monster-batch-s/SELECTION.md; ties at 12.0 taken as families), each
	-- re-verified against source (evidence/monster-batch-s-20260929/
	-- source-contracts.json). Every define_as is bound. Argoniel and Elandar are
	-- NON-unique explicit nice_tile tall bodies (64x128), so they carry
	-- native_tall=true; they also cover the identical High Peak final bosses.
	-- The Companion Warrior and Archer name their PNG with image=; the rest use
	-- the NPC.lua:33 default-name PNG. The Gates of Morning "human sun-paladin"
	-- has no define_as and is accepted by the pinned "human-sun-paladin"
	-- variant below (2026-09-29). Kor's Fury could learn Flame of Urh'Rok
	-- through its Corruptor auto_class after level 39; the sprite is
	-- untouched, so it opts into urh_rok_form (2026-09-29).
	{id="human-sun-paladin", name="human sun-paladin", image="npc/humanoid_human_human_sun_paladin.png", type="humanoid", subtype="human", define_as="SUN_PALADIN_DEFENDER"},
	{id="high-sun-paladin-rodmour", name="High Sun-Paladin Rodmour", image="npc/humanoid_human_high_sun_paladin_rodmour.png", type="humanoid", subtype="human", define_as="SUN_PALADIN_DEFENDER_RODMOUR", unique=true},
	{id="aluin-the-fallen", name="Aluin the Fallen", image="npc/humanoid_human_aluin_the_fallen.png", type="humanoid", subtype="human", define_as="ALUIN", unique=true},
	{id="argoniel", name="Argoniel", image="npc/humanoid_human_argoniel.png", type="humanoid", subtype="human", define_as="ARGONIEL", native_tall=true},
	{id="elandar", name="Elandar", image="npc/humanoid_shalore_elandar.png", type="humanoid", subtype="shalore", define_as="ELANDAR", native_tall=true},
	{id="mindworm", name="Mindworm", image="npc/humanoid_thalore_mindworm.png", type="humanoid", subtype="thalore", define_as="MINDWORM", unique=true},
	{id="berethh", name="Berethh", image="npc/humanoid_thalore_berethh.png", type="humanoid", subtype="thalore", define_as="BERETHH", unique=true},
	{id="companion-warrior", name="Companion Warrior", image="npc/humanoid_elenulach_thief.png", type="humanoid", subtype="thalore", define_as="BERETHH_WARRIOR"},
	{id="companion-archer", name="Companion Archer", image="npc/humanoid_elf_elven_archer.png", type="humanoid", subtype="thalore", define_as="BERETHH_ARCHER"},
	{id="greater-mummy-lord", name="Greater Mummy Lord", image="npc/undead_mummy_greater_mummy_lord.png", type="undead", subtype="mummy", define_as="GREATER_MUMMY_LORD", unique=true},
	{id="kors-fury", name="Kor's Fury", image="npc/undead_ghost_kor_s_fury.png", type="undead", subtype="ghost", define_as="KOR_FURY", unique=true, urh_rok_form=true},
	{id="borfast", name="Borfast the Broken", image="npc/undead_ghoul_borfast_the_broken.png", type="undead", subtype="ghoul", define_as="BORFAST", unique=true},
	-- Batch T: the remaining 12.0-tier story identities (art/monster-batch-t/
	-- SELECTION.md; Training Dummy is left native), each re-verified against
	-- source (evidence/monster-batch-t-20260930/source-contracts.json). Every
	-- define_as is bound. The caravan people, war dog and Pumpkin name their PNG
	-- with image=; the rest use the NPC.lua:33 default-name PNG. Slasul is a
	-- UNIQUE explicit nice_tile tall body (no native_tall flag, like Walrog).
	-- The war dog shares canine_dw.png with the dire wolf and the corrupted war
	-- dog; each matches only its own exact name and define_as. The Fortress
	-- Shadow's subtype is exactly "Sher'Tul". The Weirdling Beast can learn Flame
	-- of Urh'Rok through its Corruptor auto_class, so it opts into urh_rok_form.
	{id="caravan-merchant", name="caravan merchant", image="npc/humanoid_human_spectator02.png", type="humanoid", subtype="human", define_as="CARAVAN_MERCHANT"},
	{id="caravan-guard", name="caravan guard", image="npc/humanoid_human_spectator.png", type="humanoid", subtype="human", define_as="CARAVAN_GUARD"},
	{id="caravan-porter", name="caravan porter", image="npc/humanoid_human_spectator03.png", type="humanoid", subtype="human", define_as="CARAVAN_PORTER"},
	{id="lost-merchant", name="Lost Merchant", image="npc/humanoid_human_lost_merchant.png", type="humanoid", subtype="human", define_as="MERCHANT"},
	{id="nimisil", name="Nimisil", image="npc/spiderkin_spider_nimisil.png", type="spiderkin", subtype="spider", define_as="NIMISIL", unique=true},
	{id="slasul", name="Slasul", image="npc/humanoid_naga_slasul.png", type="humanoid", subtype="naga", define_as="SLASUL", unique=true},
	{id="draebor", name="Draebor, the Imp", image="npc/demon_minor_draebor__the_imp.png", type="demon", subtype="minor", define_as="DRAEBOR", unique=true},
	{id="war-dog", name="war dog", image="npc/canine_dw.png", type="animal", subtype="canine", define_as="WAR_DOG"},
	{id="yeek-wayist", name="Yeek Wayist", image="npc/humanoid_yeek_yeek_wayist.png", type="humanoid", subtype="yeek", define_as="YEEK_WAYIST", unique=true},
	{id="weirdling-beast", name="Weirdling Beast", image="npc/horror_eldritch_weirdling_beast.png", type="horror", subtype="eldritch", define_as="WEIRDLING_BEAST", unique=true, urh_rok_form=true},
	{id="fortress-shadow", name="Fortress Shadow", image="npc/horror_sher_tul_fortress_shadow.png", type="horror", subtype="Sher'Tul", define_as="BUTLER"},
	{id="pumpkin", name="Pumpkin, the little kitty", image="npc/sage_kitty.png", type="animal", subtype="feline", define_as="KITTY", unique=true},
	-- Batch U: the twelve identities after the finished 12.0 tier in the
	-- survey-2 unscheduled list (art/monster-batch-u/SELECTION.md), each
	-- re-verified against source (evidence/monster-batch-u-20260930/
	-- source-contracts.json). All are non-unique leaves WITHOUT define_as, so
	-- they match by exact name, type and subtype like the orc assassin; each
	-- name has a single definition. The nagas name their PNG with image=, the
	-- rest use the NPC.lua:33 default-name PNG (all 64x64, no tall bodies, no
	-- native_tall). Two birth sustains only touch temporary values (Stealth,
	-- Apply Poison, Acidic Skin). None has an auto_class that can reach Flame
	-- of Urh'Rok, so there is no urh_rok_form. The Wild Gift "ritch
	-- flamespitter" summon has the same name and type but its own PNG
	-- (summoner_ritch.png); it wears this token through the per-entry
	-- image_aliases rule below (real summon fields only, plus its exact
	-- "(wild summon)" rename). The tutorial "hairy spider" wears the
	-- ninurlhing PNG under another name and stays native.
	{id="ritch-flamespitter", name="ritch flamespitter", image="npc/insect_ritch_ritch_flamespitter.png", type="insect", subtype="ritch"},
	{id="ritch-impaler", name="ritch impaler", image="npc/insect_ritch_ritch_impaler.png", type="insect", subtype="ritch"},
	{id="chitinous-ritch", name="chitinous ritch", image="npc/insect_ritch_chitinous_ritch.png", type="insect", subtype="ritch"},
	{id="naga-tide-huntress", name="naga tide huntress", image="npc/naga_tide_huntress.png", type="humanoid", subtype="naga"},
	{id="naga-psyren", name="naga psyren", image="npc/naga_psyren.png", type="humanoid", subtype="naga"},
	{id="ancient-elven-mummy", name="ancient elven mummy", image="npc/undead_mummy_ancient_elven_mummy.png", type="undead", subtype="mummy"},
	{id="orc-master-assassin", name="orc master assassin", image="npc/humanoid_orc_orc_master_assassin.png", type="humanoid", subtype="orc"},
	{id="orc-grand-master-assassin", name="orc grand master assassin", image="npc/humanoid_orc_orc_grand_master_assassin.png", type="humanoid", subtype="orc"},
	{id="fire-imp", name="fire imp", image="npc/demon_minor_fire_imp.png", type="demon", subtype="minor"},
	{id="gaeramarth", name="gaeramarth", image="npc/spiderkin_spider_gaeramarth.png", type="spiderkin", subtype="spider"},
	{id="ninurlhing", name="ninurlhing", image="npc/spiderkin_spider_ninurlhing.png", type="spiderkin", subtype="spider"},
	{id="fate-weaver", name="fate weaver", image="npc/spiderkin_spider_fate_weaver.png", type="spiderkin", subtype="spider"},
	-- Batch V: the twelve identities after batch U in the survey-2 unscheduled
	-- list (art/monster-batch-v/SELECTION.md), each re-verified against source
	-- (evidence/monster-batch-v-20260930/source-contracts.json). All are
	-- non-unique leaves WITHOUT define_as, matched by exact name, type and
	-- subtype; each name has a single leaf definition. The black crystal names
	-- its PNG with image=; the rest use the NPC.lua:33 default-name PNG.
	-- Dolleg and eternal bone giant are non-unique native_tall entries whose
	-- nice_tile names the tall PNG explicitly (like bone giant); the Assemble
	-- minion "eternal bone giant" (same name, type, subtype and body, no
	-- define_as) wears the same token through the ordinary key, a Lord of Skulls
	-- renames its minion and stays native. Birth sustains only touch temporary
	-- values. No identity has an auto_class that can reach Flame of Urh'Rok, so
	-- there is no urh_rok_form. The dreams "lost wife" (subtype "bloated horror")
	-- has another name and stays native.
	{id="black-crystal", name="black crystal", image="npc/crystal_black.png", type="immovable", subtype="crystal"},
	{id="faerlhing", name="faerlhing", image="npc/spiderkin_spider_faerlhing.png", type="spiderkin", subtype="spider"},
	{id="losselhing", name="losselhing", image="npc/spiderkin_spider_losselhing.png", type="spiderkin", subtype="spider"},
	{id="dredge", name="dredge", image="npc/horror_temporal_dredge.png", type="horror", subtype="temporal"},
	{id="dolleg", name="dolleg", image="npc/demon_major_dolleg.png", type="demon", subtype="major", native_tall=true},
	{id="eternal-bone-giant", name="eternal bone giant", image="npc/undead_giant_eternal_bone_giant.png", type="undead", subtype="giant", native_tall=true},
	{id="drem-master", name="drem master", image="npc/horror_corrupted_drem_master.png", type="horror", subtype="corrupted"},
	{id="orc-pyromancer", name="orc pyromancer", image="npc/humanoid_orc_orc_pyromancer.png", type="humanoid", subtype="orc"},
	{id="orc-cryomancer", name="orc cryomancer", image="npc/humanoid_orc_orc_cryomancer.png", type="humanoid", subtype="orc"},
	{id="bloated-horror", name="bloated horror", image="npc/horror_eldritch_bloated_horror.png", type="horror", subtype="eldritch"},
	{id="yaech-hunter", name="yaech hunter", image="npc/humanoid_yaech_yaech_hunter.png", type="humanoid", subtype="yaech"},
	{id="orc-blood-mage", name="orc blood mage", image="npc/humanoid_orc_orc_blood_mage.png", type="humanoid", subtype="orc"},
	-- Batch W: the twelve identities after batch V in the survey-2 unscheduled
	-- list (art/monster-batch-w/SELECTION.md), each re-verified against source
	-- (evidence/monster-batch-w-20260930/source-contracts.json). All are
	-- non-unique single-definition leaves matched by exact name, type and
	-- subtype. The two orc wyrmics bind their define_as (ORC_FIRE_WYRMIC,
	-- ORC_ICE_WYRMIC; reknor-last builds them by define_as, the vaults by name,
	-- both reaching the same leaf); the other ten have no define_as. The bears,
	-- banshee and three ants name their PNG with image=; the rest use the
	-- NPC.lua:33 default-name PNG. The heavy bone giant is a non-unique
	-- native_tall entry whose nice_tile names the tall PNG explicitly (like the
	-- eternal bone giant); the Assemble minion "heavy bone giant" (same name,
	-- type, subtype and body, no define_as) wears the same token through the
	-- ordinary key, a Lord of Skulls renames its minion and stays native. Birth
	-- sustains (banshee Blur Sight, grannor'vin Call Shadows) only add particles
	-- and temporary values. No identity has an auto_class that can reach Flame of
	-- Urh'Rok, so there is no urh_rok_form. The acid ant (tied at 4.8, dropped by
	-- source order) stays native.
	{id="fiery-orc-wyrmic", name="fiery orc wyrmic", image="npc/humanoid_orc_fiery_orc_wyrmic.png", type="humanoid", subtype="orc", define_as="ORC_FIRE_WYRMIC"},
	{id="icy-orc-wyrmic", name="icy orc wyrmic", image="npc/humanoid_orc_icy_orc_wyrmic.png", type="humanoid", subtype="orc", define_as="ORC_ICE_WYRMIC"},
	{id="yaech-mindslayer", name="yaech mindslayer", image="npc/humanoid_yaech_yaech_mindslayer.png", type="humanoid", subtype="yaech"},
	{id="heavy-bone-giant", name="heavy bone giant", image="npc/undead_giant_heavy_bone_giant.png", type="undead", subtype="giant", native_tall=true},
	{id="cave-bear", name="cave bear", image="npc/cave_bear.png", type="animal", subtype="bear"},
	{id="war-bear", name="war bear", image="npc/war_bear.png", type="animal", subtype="bear"},
	{id="grannor-vin", name="grannor'vin", image="npc/horror_corrupted_grannor_vin.png", type="horror", subtype="corrupted"},
	{id="rotting-mummy", name="rotting mummy", image="npc/undead_mummy_rotting_mummy.png", type="undead", subtype="mummy"},
	{id="banshee", name="banshee", image="npc/banshee.png", type="undead", subtype="ghost"},
	{id="giant-fire-ant", name="giant fire ant", image="npc/fire_ant.png", type="insect", subtype="ant"},
	{id="giant-ice-ant", name="giant ice ant", image="npc/ice_ant.png", type="insect", subtype="ant"},
	{id="giant-lightning-ant", name="giant lightning ant", image="npc/lightning_ant.png", type="insect", subtype="ant"},
	-- Batch X: the twelve identities after batch W in the survey-2 unscheduled
	-- list (art/monster-batch-x/SELECTION.md), each re-verified against source
	-- (evidence/monster-batch-x-20260930/source-contracts.json). All are
	-- non-unique single-definition leaves matched by exact name, type and
	-- subtype. Only the assassin binds a define_as (THIEF_ASSASSIN, which the
	-- later "shadowblade" leaf repeats under another name and PNG, so that
	-- leaf stays native); the other eleven have none. The ants, blue crystal
	-- and dread name their PNG with image=; the rest use the NPC.lua:33
	-- default-name PNG. The greater telugoroth is a non-unique native_tall
	-- entry whose nice_tile names the tall PNG explicitly (like the heavy bone
	-- giant); the plain telugoroth has its own token and the ultimate
	-- telugoroth and the greater/ultimate teluvortas stay native. The
	-- necromancer Dread talent minion, the dreadmaster's minions and its
	-- summon are actors named "dread" with the same type, subtype and image and
	-- no define_as, so they wear the same token through the ordinary key.
	-- Birth sustains (Blur Sight, Stealth, Shadow Combat, Bone Shield) only add
	-- particles and temporary values. No identity has an auto_class that can
	-- reach Flame of Urh'Rok, so there is no urh_rok_form.
	{id="giant-acid-ant", name="giant acid ant", image="npc/acid_ant.png", type="insect", subtype="ant"},
	{id="giant-army-ant", name="giant army ant", image="npc/army_ant.png", type="insect", subtype="ant"},
	{id="yaech-psion", name="yaech psion", image="npc/humanoid_yaech_yaech_psion.png", type="humanoid", subtype="yaech"},
	{id="blue-crystal", name="blue crystal", image="npc/crystal_blue.png", type="immovable", subtype="crystal"},
	{id="devourer", name="devourer", image="npc/horror_eldritch_devourer.png", type="horror", subtype="eldritch"},
	{id="skeleton-assassin", name="skeleton assassin", image="npc/undead_skeleton_skeleton_assassin.png", type="undead", subtype="skeleton"},
	{id="assassin", name="assassin", image="npc/humanoid_human_assassin.png", type="humanoid", subtype="human", define_as="THIEF_ASSASSIN"},
	{id="elven-corruptor", name="elven corruptor", image="npc/humanoid_shalore_elven_corruptor.png", type="humanoid", subtype="shalore"},
	{id="orc-fighter", name="orc fighter", image="npc/humanoid_orc_orc_fighter.png", type="humanoid", subtype="orc"},
	{id="greater-telugoroth", name="greater telugoroth", image="npc/elemental_temporal_greater_telugoroth.png", type="elemental", subtype="temporal", native_tall=true},
	{id="teluvorta", name="teluvorta", image="npc/elemental_temporal_teluvorta.png", type="elemental", subtype="temporal"},
	{id="dread", name="dread", image="npc/dread.png", type="undead", subtype="ghost"},
	-- Batch Y: the twelve identities after batch X in the survey-2 unscheduled
	-- list (art/monster-batch-y/SELECTION.md), each re-verified against source
	-- (evidence/monster-batch-y-20260930/source-contracts.json). All are
	-- non-unique single-definition leaves matched by exact name, type and
	-- subtype. Only the blade horror binds a define_as (BLADEHORROR); the other
	-- eleven have none. Six are non-unique native_tall bodies whose nice_tile
	-- names the tall PNG explicitly (like the greater telugoroth): uruivellas,
	-- thaurhereg, temporal stalker, blade horror, grizzly bear (which also has
	-- image= and so keeps the single path with nicer_tiles off) and necrotic
	-- mass. The animated mummy wrappings names object/mummy_wrappings.png. The
	-- player's alchemist golem shares the golem name, type and subtype but uses
	-- npc/alchemist_golem.png and a moddable_tile, so it stays native. Birth
	-- sustains (Bone Shield, Stealth, Kinetic Aura/Shield, Chant of Fortitude,
	-- Providence, Spin Fate) are temporary values and particles only. No
	-- identity has an auto_class that can reach Flame of Urh'Rok, so there is
	-- no urh_rok_form.
	{id="uruivellas", name="uruivellas", image="npc/demon_major_uruivellas.png", type="demon", subtype="major", native_tall=true},
	{id="thaurhereg", name="thaurhereg", image="npc/demon_major_thaurhereg.png", type="demon", subtype="major", native_tall=true},
	{id="orc-corruptor", name="orc corruptor", image="npc/humanoid_orc_orc_corruptor.png", type="humanoid", subtype="orc"},
	{id="temporal-stalker", name="temporal stalker", image="npc/horror_temporal_temporal_stalker.png", type="horror", subtype="temporal", native_tall=true},
	{id="broken-golem", name="broken golem", image="npc/construct_golem_broken_golem.png", type="construct", subtype="golem"},
	{id="golem", name="golem", image="npc/construct_golem_golem.png", type="construct", subtype="golem"},
	{id="blade-horror", name="blade horror", image="npc/horror_eldritch_blade_horror.png", type="horror", subtype="eldritch", define_as="BLADEHORROR", native_tall=true},
	{id="animated-mummy-wrappings", name="animated mummy wrappings", image="object/mummy_wrappings.png", type="undead", subtype="mummy"},
	{id="grizzly-bear", name="grizzly bear", image="npc/grizzly_bear.png", type="animal", subtype="bear", native_tall=true},
	{id="weaver-patriarch", name="weaver patriarch", image="npc/spiderkin_spider_weaver_patriarch.png", type="spiderkin", subtype="spider"},
	{id="luminous-horror", name="luminous horror", image="npc/horror_eldritch_luminous_horror.png", type="horror", subtype="eldritch"},
	{id="necrotic-mass", name="necrotic mass", image="npc/undead_horror_necrotic_mass.png", type="undead", subtype="horror", native_tall=true},
	-- Batch Z: the twelve identities after batch Y in the survey-2 unscheduled
	-- list (art/monster-batch-z/SELECTION.md), each re-verified against source
	-- (evidence/monster-batch-z-20260930/source-contracts.json). All are
	-- non-unique single-definition leaves matched by exact name, type and
	-- subtype. Only the rogue sapper binds a define_as (THIEF_SAPPER); it names
	-- the assassin's PNG through image=, so the sapper and the assassin (define_as
	-- THIEF_ASSASSIN) are told apart by name and define_as. Six are non-unique
	-- native_tall bodies whose nice_tile names the tall PNG explicitly (like the
	-- greater telugoroth): ultimate telugoroth, greater teluvorta, runed bone
	-- giant, swarming horror, ravenous horror and fire wyrm. The black mamba names
	-- darkgrey-snake.png with image=. Birth sustains (Stealth, Total Thuggery,
	-- Reality Smearing, Arcane Power, Energy Decomposition) are temporary values
	-- only. No identity has an auto_class that can reach Flame of Urh'Rok, so
	-- there is no urh_rok_form.
	{id="black-mamba", name="black mamba", image="npc/darkgrey-snake.png", type="animal", subtype="snake"},
	{id="bandit-lord", name="bandit lord", image="npc/humanoid_human_bandit_lord.png", type="humanoid", subtype="human"},
	{id="orb-weaver", name="orb weaver", image="npc/spiderkin_spider_orb_weaver.png", type="spiderkin", subtype="spider"},
	{id="elven-elite-warrior", name="elven elite warrior", image="npc/humanoid_shalore_elven_elite_warrior.png", type="humanoid", subtype="shalore"},
	{id="ultimate-telugoroth", name="ultimate telugoroth", image="npc/elemental_temporal_ultimate_telugoroth.png", type="elemental", subtype="temporal", native_tall=true},
	{id="greater-teluvorta", name="greater teluvorta", image="npc/elemental_temporal_greater_teluvorta.png", type="elemental", subtype="temporal", native_tall=true},
	{id="runed-bone-giant", name="runed bone giant", image="npc/undead_giant_runed_bone_giant.png", type="undead", subtype="giant", native_tall=true},
	{id="void-horror", name="void horror", image="npc/horror_temporal_void_horror.png", type="horror", subtype="temporal"},
	{id="swarming-horror", name="swarming horror", image="npc/horror_aquatic_swarming_horror.png", type="horror", subtype="aquatic", native_tall=true},
	{id="ravenous-horror", name="ravenous horror", image="npc/horror_aquatic_ravenous_horror.png", type="horror", subtype="aquatic", native_tall=true},
	{id="rogue-sapper", name="rogue sapper", image="npc/humanoid_human_assassin.png", type="humanoid", subtype="human", define_as="THIEF_SAPPER"},
	{id="fire-wyrm", name="fire wyrm", image="npc/dragon_fire_fire_wyrm.png", type="dragon", subtype="fire", native_tall=true},
	-- Batch AA: the twelve identities after batch Z in the survey-2 unscheduled
	-- list (art/monster-batch-aa/SELECTION.md), each re-verified against source
	-- (evidence/monster-batch-aa-20260930/source-contracts.json). All are
	-- non-unique single-definition leaves matched by exact name, type and
	-- subtype, and none binds a define_as. Seven are non-unique native_tall
	-- bodies: the ultimate faeros, ultimate teluvorta, necrotic abomination, bone
	-- horror, sanguine horror and barrow wight name their tall PNG explicitly in
	-- nice_tile (the barrow wight also with image=, like the master vampire), and
	-- the ogre warmaster uses the nice_tile{tall=1} shorthand like the other
	-- ogres. The polar bear, anaconda and dreadmaster name their PNG with image=.
	-- The Necromancer's Dread talent builds a minion with the dreadmaster's exact
	-- name, type, subtype and image, which wears the same token. Birth sustains
	-- (Fiery Hands, Berserker, Reality Smearing, Bone Shield, Blood Fury, Blur
	-- Sight) are particles and temporary values only. No identity has an
	-- auto_class that can reach Flame of Urh'Rok, so there is no urh_rok_form.
	{id="ultimate-faeros", name="ultimate faeros", image="npc/elemental_fire_ultimate_faeros.png", type="elemental", subtype="fire", native_tall=true},
	{id="orc-berserker", name="orc berserker", image="npc/humanoid_orc_orc_berserker.png", type="humanoid", subtype="orc"},
	{id="dredge-captain", name="dredge captain", image="npc/horror_temporal_dredge_captain.png", type="horror", subtype="temporal"},
	{id="polar-bear", name="polar bear", image="npc/polar_bear.png", type="animal", subtype="bear"},
	{id="anaconda", name="anaconda", image="npc/yellow-green-snake.png", type="animal", subtype="snake"},
	{id="ultimate-teluvorta", name="ultimate teluvorta", image="npc/elemental_temporal_ultimate_teluvorta.png", type="elemental", subtype="temporal", native_tall=true},
	{id="necrotic-abomination", name="necrotic abomination", image="npc/undead_horror_necrotic_abomination.png", type="undead", subtype="horror", native_tall=true},
	{id="bone-horror", name="bone horror", image="npc/undead_horror_bone_horror.png", type="undead", subtype="horror", native_tall=true},
	{id="sanguine-horror", name="sanguine horror", image="npc/undead_horror_sanguine_horror.png", type="undead", subtype="horror", native_tall=true},
	{id="barrow-wight", name="barrow wight", image="npc/barrow_wight.png", type="undead", subtype="wight", native_tall=true},
	{id="ogre-warmaster", name="ogre warmaster", image="npc/giant_ogre_ogre_warmaster.png", type="giant", subtype="ogre", native_tall=true},
	{id="dreadmaster", name="dreadmaster", image="npc/dreadmaster.png", type="undead", subtype="ghost"},
	-- Batch AB: the twelve identities after batch AA in the survey-2 unscheduled
	-- list (art/monster-batch-ab/SELECTION.md), each re-verified against source
	-- (evidence/monster-batch-ab-20260930/source-contracts.json), matched by
	-- exact name, type and subtype. Four bind a define_as: the shadowblade
	-- (THIEF_ASSASSIN, which the assassin leaf also uses under another name and
	-- PNG, and which the arena zone's unrelated define_as-less "shadowblade"
	-- lacks), the orc elite fighter (ORC_ELITE_FIGHTER), the orc elite berserker
	-- (ORC_ELITE_BERSERKER) and the greater mummy (GREATER_MUMMY; the greater
	-- mummy lord is another leaf). Six are tall bodies: the entrenched horror,
	-- boiling horror, swarm hive and ultimate shivgoroth name their tall PNG
	-- explicitly in nice_tile and the venom wyrm uses the nice_tile{tall=1}
	-- shorthand (all non-unique native_tall); the Forest Troll Hedge-Wizard uses
	-- the same shorthand as a unique, so like Walrog and Kyless it carries
	-- unique=true and no native_tall flag. The greater mummy names its PNG with
	-- image=; the rest use the NPC.lua:33 default-name PNG. Birth sustains
	-- (Thermal Aura, Burning Wake, Psiblades, Shield Wall, Berserker, Juggernaut,
	-- Stealth, Shadow Combat) are particles, shader-aura bookkeeping the matcher
	-- ignores, and temporary values only. No identity has an auto_classes that
	-- can reach Flame of Urh'Rok, so there is no urh_rok_form.
	{id="entrenched-horror", name="entrenched horror", image="npc/horror_aquatic_entrenched_horror.png", type="horror", subtype="aquatic", native_tall=true},
	{id="orc-summoner", name="orc summoner", image="npc/humanoid_orc_orc_summoner.png", type="humanoid", subtype="orc"},
	{id="greater-mummy", name="greater mummy", image="npc/undead_mummy_greater_mummy.png", type="undead", subtype="mummy", define_as="GREATER_MUMMY"},
	{id="shadowblade", name="shadowblade", image="npc/humanoid_human_shadowblade.png", type="humanoid", subtype="human", define_as="THIEF_ASSASSIN"},
	{id="orc-elite-fighter", name="orc elite fighter", image="npc/humanoid_orc_orc_elite_fighter.png", type="humanoid", subtype="orc", define_as="ORC_ELITE_FIGHTER"},
	{id="orc-elite-berserker", name="orc elite berserker", image="npc/humanoid_orc_orc_elite_berserker.png", type="humanoid", subtype="orc", define_as="ORC_ELITE_BERSERKER"},
	{id="boiling-horror", name="boiling horror", image="npc/horror_aquatic_boiling_horror.png", type="horror", subtype="aquatic", native_tall=true},
	{id="venom-wyrm", name="venom wyrm", image="npc/dragon_venom_venom_wyrm.png", type="dragon", subtype="venom", native_tall=true},
	{id="alchemist-golem", name="alchemist golem", image="npc/construct_golem_alchemist_golem.png", type="construct", subtype="golem"},
	{id="swarm-hive", name="swarm hive", image="npc/horror_aquatic_swarm_hive.png", type="horror", subtype="aquatic", native_tall=true},
	{id="forest-troll-hedge-wizard", name="Forest Troll Hedge-Wizard", image="npc/giant_troll_forest_troll_hedge_wizard.png", type="giant", subtype="troll", unique=true},
	{id="ultimate-shivgoroth", name="ultimate shivgoroth", image="npc/elemental_ice_ultimate_shivgoroth.png", type="elemental", subtype="ice", native_tall=true},
	-- Batch AC (the final batch): the seventeen identities that remain after
	-- batch AB in the survey-2 unscheduled list, everything except Training
	-- Dummy (art/monster-batch-ac/SELECTION.md), each re-verified against source
	-- (evidence/monster-batch-ac-20260930/source-contracts.json), matched by
	-- exact name, type and subtype. Seven are uniques: Aletta Soultorn (ALETTA)
	-- and Filio Flightfond (FILIO) are flat 64x64 bodies; Glacial Legion,
	-- Arch Zephyr, Rotting Titan and Heavy Sentinel are tall bodies bound to
	-- their define_as; Void Spectre is a tall unique without a define_as. The
	-- unique tall bodies carry unique=true and no native_tall flag (nativeTallImage
	-- accepts them through the unique path, like the Hedge-Wizard). Four
	-- non-unique tall bodies carry native_tall=true (abyssal horror, umbral
	-- horror, degenerated ogric mass, ogric abomination). The vampire lord names
	-- its PNG with image=; the rest use the NPC.lua:33 default-name PNG. Birth
	-- sustains (Gloom, Burning Wake, Crystalline Focus, Golem Reflective Skin,
	-- Stealth and the rest) are particles, shader-aura bookkeeping the matcher
	-- ignores, and temporary values only. No identity has an auto_classes that
	-- can reach Flame of Urh'Rok, so there is no urh_rok_form. The Corpathus
	-- artifact's Vilespawn minion reuses the oozing horror PNG under another
	-- name and stays native.
	{id="aletta-soultorn", name="Aletta Soultorn", image="npc/undead_ghost_aletta_soultorn.png", type="undead", subtype="ghost", define_as="ALETTA", unique=true},
	{id="ruin-banshee", name="ruin banshee", image="npc/undead_ghost_ruin_banshee.png", type="undead", subtype="ghost"},
	{id="filio-flightfond", name="Filio Flightfond", image="npc/undead_skeleton_filio_flightfond.png", type="undead", subtype="skeleton", define_as="FILIO", unique=true},
	{id="orc-high-pyromancer", name="orc high pyromancer", image="npc/humanoid_orc_orc_high_pyromancer.png", type="humanoid", subtype="orc"},
	{id="orc-high-cryomancer", name="orc high cryomancer", image="npc/humanoid_orc_orc_high_cryomancer.png", type="humanoid", subtype="orc"},
	{id="glacial-legion", name="Glacial Legion", image="npc/undead_ghost_glacial_legion.png", type="undead", subtype="ghost", define_as="GLACIAL_LEGION", unique=true},
	{id="arch-zephyr", name="Arch Zephyr", image="npc/undead_vampire_arch_zephyr.png", type="undead", subtype="vampire", define_as="ARCH_ZEPHYR", unique=true},
	{id="rotting-titan", name="Rotting Titan", image="npc/undead_ghoul_rotting_titan.png", type="undead", subtype="ghoul", define_as="ROTTING_TITAN", unique=true},
	{id="heavy-sentinel", name="Heavy Sentinel", image="npc/undead_giant_heavy_sentinel.png", type="undead", subtype="giant", define_as="HEAVY_SENTINEL", unique=true},
	{id="void-spectre", name="Void Spectre", image="npc/undead_wight_void_spectre.png", type="undead", subtype="wight", unique=true},
	{id="oozing-horror", name="oozing horror", image="npc/horror_eldritch_oozing_horror.png", type="horror", subtype="eldritch"},
	{id="abyssal-horror", name="abyssal horror", image="npc/horror_aquatic_abyssal_horror.png", type="horror", subtype="aquatic", native_tall=true},
	{id="ungolmor", name="ungolmor", image="npc/spiderkin_spider_ungolmor.png", type="spiderkin", subtype="spider"},
	{id="umbral-horror", name="umbral horror", image="npc/horror_eldritch_umbral_horror.png", type="horror", subtype="eldritch", native_tall=true},
	{id="vampire-lord", name="vampire lord", image="npc/vampire_lord.png", type="undead", subtype="vampire"},
	{id="degenerated-ogric-mass", name="degenerated ogric mass", image="npc/giant_ogre_degenerated_ogric_mass.png", type="giant", subtype="ogre", native_tall=true},
	{id="ogric-abomination", name="ogric abomination", image="npc/giant_ogre_ogric_abomination.png", type="giant", subtype="ogre", native_tall=true},
	-- Batch AD (first off-list dungeon-pool batch): thirteen non-unique leaves,
	-- none binding a define_as (art/monster-batch-ad/SELECTION.md), each
	-- re-verified against source (evidence/monster-batch-ad-20260930/
	-- source-contracts.json) and matched by exact name, type and subtype. Four
	-- are tall nice_tile bodies and carry native_tall=true: duathedlen and
	-- daelach (demon/major), ice wyrm (dragon/cold) and snow cat (animal/feline;
	-- its nice_tile image="invis.png" is only the tall-body mechanism, like
	-- dolleg). The duathedlen's name is not ASCII (u-acute, written as the UTF-8
	-- bytes \195\186 so every Lua accepts it), so with nicer_tiles off its
	-- default-name image is the nonexistent npc/demon_major_d__athedlen.png and
	-- the token is simply not applied. The other nine are 64x64 default-name
	-- images: orc grand summoner, orc master wyrmic and orc mage-hunter (Gorbat
	-- pride), ritch larva, ritch hunter and ritch hive mother, panther, tiger and
	-- sabertooth tiger. The non-unique "ritch hive mother" draws the same PNG as
	-- the unique "Ritch Great Hive Mother" (id ritch-hive-mother, define_as
	-- HIVE_MOTHER), so it takes the id ritch-hive-mother-pool; the names differ,
	-- so name lookup never crosses. None has an auto_class that can reach Flame of
	-- Urh'Rok, so there is no urh_rok_form; no summon, effect or vault builds a
	-- copy of these bodies, so no variant or alias is added.
	{id="duathedlen", name="d\195\186athedlen", image="npc/demon_major_duathedlen.png", type="demon", subtype="major", native_tall=true},
	{id="daelach", name="daelach", image="npc/demon_major_daelach.png", type="demon", subtype="major", native_tall=true},
	{id="orc-grand-summoner", name="orc grand summoner", image="npc/humanoid_orc_orc_grand_summoner.png", type="humanoid", subtype="orc"},
	{id="orc-master-wyrmic", name="orc master wyrmic", image="npc/humanoid_orc_orc_master_wyrmic.png", type="humanoid", subtype="orc"},
	{id="orc-mage-hunter", name="orc mage-hunter", image="npc/humanoid_orc_orc_mage_hunter.png", type="humanoid", subtype="orc"},
	{id="ritch-larva", name="ritch larva", image="npc/insect_ritch_ritch_larva.png", type="insect", subtype="ritch"},
	{id="ritch-hunter", name="ritch hunter", image="npc/insect_ritch_ritch_hunter.png", type="insect", subtype="ritch"},
	{id="ritch-hive-mother-pool", name="ritch hive mother", image="npc/insect_ritch_ritch_hive_mother.png", type="insect", subtype="ritch"},
	{id="snow-cat", name="snow cat", image="npc/animal_feline_snow_cat.png", type="animal", subtype="feline", native_tall=true},
	{id="panther", name="panther", image="npc/animal_feline_panther.png", type="animal", subtype="feline"},
	{id="tiger", name="tiger", image="npc/animal_feline_tiger.png", type="animal", subtype="feline"},
	{id="sabertooth-tiger", name="sabertooth tiger", image="npc/animal_feline_sabertooth_tiger.png", type="animal", subtype="feline"},
	{id="ice-wyrm", name="ice wyrm", image="npc/dragon_cold_ice_wyrm.png", type="dragon", subtype="cold", native_tall=true},
	-- Batch AE: twelve exact off-list pool leaves (source-contracts.json).
	-- Nine supported single-body tall entries; three flat entries. Arena
	-- HEADLESSHORROR and renamed tall random bosses retain native art.
	-- Burning Wake aura bookkeeping is supported by the existing guard;
	-- same-body hummerhorn multiplication wears its exact token.
	{id="champion-of-urh-rok", name="champion of Urh'Rok", image="npc/demon_major_champion_of_urh_rok.png", type="demon", subtype="major", native_tall=true},
	{id="forge-giant", name="forge-giant", image="npc/demon_major_forge_giant.png", type="demon", subtype="major", native_tall=true},
	{id="hummerhorn", name="hummerhorn", image="npc/hummerhorn.png", type="insect", subtype="swarms"},
	{id="weaver-matriarch", name="weaver matriarch", image="npc/spiderkin_spider_weaver_matriarch.png", type="spiderkin", subtype="spider", native_tall=true},
	{id="patchwork-troll", name="patchwork troll", image="npc/giant_troll_patchwork_troll.png", type="giant", subtype="troll", native_tall=true},
	{id="maulotaur", name="maulotaur", image="npc/giant_minotaur_maulotaur.png", type="giant", subtype="minotaur", native_tall=true},
	{id="worm-that-walks", name="worm that walks", image="npc/horror_eldritch_worm_that_walks.png", type="horror", subtype="eldritch"},
	{id="headless-horror", name="headless horror", image="npc/horror_eldritch_headless_horror.png", type="horror", subtype="eldritch"},
	{id="storm-wyrm", name="storm wyrm", image="npc/dragon_storm_storm_wyrm.png", type="dragon", subtype="storm", native_tall=true},
	{id="spire-dragon", name="spire dragon", image="npc/dragon_wild_spire_dragon.png", type="dragon", subtype="wild", native_tall=true},
	{id="blinkwyrm", name="blinkwyrm", image="npc/dragon_wild_blinkwyrm.png", type="dragon", subtype="wild", native_tall=true},
	{id="emperor-wight", name="emperor wight", image="npc/emperor_wight.png", type="undead", subtype="wight", native_tall=true},

	-- Batch AF: nine admitted source-verified off-list pool bodies. Dreaming horror
	-- retains native art because of its actor shader. Blood lich was admitted
	-- after coordinator-authorized infrastructure retry. No clone-specific rules.
	{id="nightmare-horror", name="nightmare horror", image="npc/horror_eldritch_nightmare_horror.png", type="horror", subtype="eldritch"},
	{id="radiant-horror", name="radiant horror", image="npc/horror_eldritch_radiant_horror.png", type="horror", subtype="eldritch"},
	{id="maelstrom", name="maelstrom", image="npc/horror_eldritch_maelstrom.png", type="horror", subtype="eldritch", native_tall=true},
	{id="parasitic-horror", name="parasitic horror", image="npc/horror_eldritch_parasitic_horror.png", type="horror", subtype="eldritch", native_tall=true},
	{id="lich", name="lich", image="npc/undead_lich_lich.png", type="undead", subtype="lich", native_tall=true},
	{id="ancient-lich", name="ancient lich", image="npc/undead_lich_ancient_lich.png", type="undead", subtype="lich", native_tall=true},
	{id="archlich", name="archlich", image="npc/undead_lich_archlich.png", type="undead", subtype="lich", native_tall=true},
	{id="blood-lich", name="blood lich", image="npc/undead_lich_blood_lich.png", type="undead", subtype="lich"},
	{id="animated-blood", name="animated blood", image="npc/undead_horror_animated_blood.png", type="undead", subtype="blood", native_tall=true},
	-- AG: exact quad_hue/no-args identities; iridescence is painted in the
	-- body, never applied to the neutral replacement disc. Two distinct
	-- keepsake shadows share a name; each binds its exact define_as.
	{id="multi-hued-drake-hatchling", name="multi-hued drake hatchling", image="npc/dragon_multihued_multi_hued_drake_hatchling.png", type="dragon", subtype="multihued", native_shader="quad_hue"},
	{id="multi-hued-drake", name="multi-hued drake", image="npc/dragon_multihued_multi_hued_drake.png", type="dragon", subtype="multihued", native_shader="quad_hue"},
	{id="greater-multi-hued-wyrm", name="greater multi-hued wyrm", image="npc/dragon_multihued_greater_multi_hued_wyrm.png", type="dragon", subtype="multihued", define_as="GREATER_MULTI_HUED_WYRM", native_tall=true, native_shader="quad_hue"},
	{id="shadow-claw", name="shadow claw", image="npc/shadow-claw.png", type="undead", subtype="shadow", define_as="SHADOW_CLAW", shared_name=true},
	{id="shadow-caster", name="shadow claw", image="npc/shadow-caster.png", type="undead", subtype="shadow", define_as="SHADOW_CASTER", shared_name=true},
	{id="multi-hued-crystal", name="multi-hued crystal", image="npc/crystal_violet.png", type="immovable", subtype="crystal", native_shader="quad_hue"},
	{id="shimmering-crystal", name="shimmering crystal", image="npc/crystal_npc.png", type="immovable", subtype="crystal", native_shader="quad_hue"},
	-- UA: exact off-list unique/boss bodies. Shade unique_glow stays native;
	-- tall uniques reuse the verified 2x/-1 path, without a native_tall flag.
	-- Phoenix egg and all extra/shader/paper-doll appearances stay native.
	{id="kra-tor", name="Kra'Tor the Gluttonous", image="npc/humanoid_orc_kra_tor_the_gluttonous.png", type="humanoid", subtype="orc", unique=true},
	{id="khulmanar", name="Khulmanar, General of Urh'Rok", image="npc/demon_major_general_of_urh_rok.png", type="demon", subtype="major", unique=true},
	{id="rungof", name="Rungof the Warg Titan", image="npc/canine_rungof.png", type="animal", subtype="canine", unique=true},
	{id="grgglck", name="Grgglck the Devouring Darkness", image="npc/horror_eldritch_grgglck.png", type="horror", subtype="eldritch", unique=true},
	{id="queen-ant", name="Queen Ant", image="npc/insect_ant_queen_ant.png", type="insect", subtype="ant", unique=true},
	{id="ak-gishil", name="Ak'Gishil", image="npc/horror_eldritch_ak_gishil.png", type="horror", subtype="eldritch", unique=true},
	{id="ninandra", name="Ninandra, the Great Weaver", image="npc/spiderkin_spider_ninandra_the_great_weaver.png", type="spiderkin", subtype="spider", unique=true},
	{id="phoenix", name="Phoenix", image="npc/animal_bird_phoenix.png", type="animal", subtype="bird", define_as="NPC_PHOENIX", unique=true},
	{id="ukruk", name="Ukruk the Fierce", image="npc/humanoid_orc_ukruk_the_fierce.png", type="humanoid", subtype="orc", define_as="UKRUK", unique=true},
	{id="gorbat", name="Gorbat, Supreme Wyrmic of the Pride", image="npc/humanoid_orc_gorbat__supreme_wyrmic_of_the_pride.png", type="humanoid", subtype="orc", define_as="GORBAT", unique=true},
	{id="grushnak", name="Grushnak, Battlemaster of the Pride", image="npc/humanoid_orc_grushnak__battlemaster_of_the_pride.png", type="humanoid", subtype="orc", define_as="GRUSHNAK", unique=true},
	{id="vor", name="Vor, Grand Geomancer of the Pride", image="npc/humanoid_orc_vor__grand_geomancer_of_the_pride.png", type="humanoid", subtype="orc", define_as="VOR", unique=true},
	-- TA-1: first town-resident batch. Angolwen mages (four native-tall
	-- nice_tile bodies), six town guards and the two Ring of Blood residents.
	-- All are non-unique with no define_as; native equipment is not a
	-- paper-doll, so the drawn body never changes. The slaver's make_escort
	-- copies are the same enthralled-slave body and wear the same token.
	{id="apprentice-mage", name="apprentice mage", image="npc/humanoid_human_apprentice_mage.png", type="humanoid", subtype="human"},
	{id="pyromancer", name="pyromancer", image="npc/humanoid_human_pyromancer.png", type="humanoid", subtype="human", native_tall=true},
	{id="cryomancer", name="cryomancer", image="npc/humanoid_human_cryomancer.png", type="humanoid", subtype="human", native_tall=true},
	{id="geomancer", name="geomancer", image="npc/humanoid_human_geomancer.png", type="humanoid", subtype="human", native_tall=true},
	{id="tempest", name="tempest", image="npc/humanoid_human_tempest.png", type="humanoid", subtype="human", native_tall=true},
	{id="human-guard", name="human guard", image="npc/humanoid_human_human_guard.png", type="humanoid", subtype="human"},
	{id="derth-guard", name="derth guard", image="npc/humanoid_human_derth_guard.png", type="humanoid", subtype="human"},
	{id="last-hope-guard", name="last hope guard", image="npc/humanoid_human_last_hope_guard.png", type="humanoid", subtype="human"},
	{id="halfling-guard", name="halfling guard", image="npc/humanoid_halfling_halfling_guard.png", type="humanoid", subtype="halfling"},
	{id="dwarven-guard", name="dwarven guard", image="npc/humanoid_dwarf_dwarven_guard.png", type="humanoid", subtype="dwarf"},
	{id="elvala-guard", name="elvala guard", image="npc/humanoid_shalore_elvala_guard.png", type="humanoid", subtype="shalore"},
	{id="slaver", name="slaver", image="npc/humanoid_yaech_slaver.png", type="humanoid", subtype="yaech"},
	{id="enthralled-slave", name="enthralled slave", image="npc/humanoid_human_enthralled_slave.png", type="humanoid", subtype="human"},
	-- UB-1: second uniques/bosses batch, nine exact native-tall unique bodies.
	-- Each resolves to one nice_tile body (image=invis.png + a single add_mos
	-- display_h=2/display_y=-1); unique=true admits it without a native_tall flag.
	-- Aeryn's High form is bound at two define sites (high-peak, gates-of-morning)
	-- with the same name/define_as/PNG, so one entry covers both. Caldizar's two
	-- define sites share one byte-identical body, so one shared token is bound to
	-- CALDIZAR plus a second bound define_as CALDIZAR_AOADS (shared_name).
	{id="high-sun-paladin-aeryn", name="High Sun Paladin Aeryn", image="npc/humanoid_human_high_sun_paladin_aeryn.png", type="humanoid", subtype="human", define_as="HIGH_SUN_PALADIN_AERYN", unique=true},
	{id="fallen-sun-paladin-aeryn", name="Fallen Sun Paladin Aeryn", image="npc/humanoid_human_fallen_sun_paladin_aeryn.png", type="humanoid", subtype="human", define_as="FALLEN_SUN_PALADIN_AERYN", unique=true},
	{id="caldizar", name="Caldizar", image="npc/horror_sher_tul_caldizar.png", type="horror", subtype="sher'tul", define_as="CALDIZAR", define_as_alias="CALDIZAR_AOADS", shared_name=true, unique=true},
	{id="chronolith-twin", name="Chronolith Twin", image="npc/horror_temporal_cronolith_twin.png", type="horror", subtype="temporal", define_as="CHRONOLITH_TWIN", unique=true},
	{id="chronolith-clone", name="Chronolith Clone", image="npc/horror_temporal_cronolith_clone.png", type="horror", subtype="temporal", define_as="CHRONOLITH_CLONE", unique=true},
	{id="temporal-defiler", name="Temporal Defiler", image="npc/horror_temporal_temporal_defiler.png", type="horror", subtype="temporal", define_as="TEMPORAL_DEFILER", unique=true},
	{id="corrupted-daelach", name="Corrupted Daelach", image="npc/demon_major_corrupted_daelach.png", type="demon", subtype="major", define_as="CORRUPTED_DAELACH", unique=true},
	{id="supreme-archmage-linaniil", name="Linaniil, Supreme Archmage of Angolwen", image="npc/humanoid_human_linaniil_supreme_archmage.png", type="humanoid", subtype="human", define_as="SUPREME_ARCHMAGE_LINANIIL", unique=true},
	{id="archmage-tarelion", name="Archmage Tarelion", image="npc/humanoid_shalore_archmage_tarelion.png", type="humanoid", subtype="shalore", define_as="TARELION", unique=true},
	-- UB-2: third uniques/bosses batch. Ten flat 64x64 unique identities (six
	-- default name images, four explicit image=/base pairs) plus the wiring-only
	-- Ben Cruthdar, the Cursed. The Cursed shares the byte-identical native PNG
	-- with the Abomination, so it reuses the abomination runtime token; the
	-- abomination entry above is unchanged.
	{id="sun-paladin-guren", name="Sun Paladin Guren", image="npc/humanoid_human_sun_paladin_guren.png", type="humanoid", subtype="human", define_as="SUN_PALADIN_GUREN", unique=true},
	{id="epoch", name="Epoch", image="npc/elemental_temporal_epoch.png", type="elemental", subtype="temporal", define_as="EPOCH", unique=true},
	{id="corrupted-oozemancer", name="Corrupted Oozemancer", image="npc/giant_troll_corrupted_oozemancer.png", type="giant", subtype="troll", define_as="CORRUPTED_OOZEMANCER", unique=true},
	{id="zemekkys", name="Zemekkys, Grand Keeper of Reality", image="npc/humanoid_elf_high_chronomancer_zemekkys.png", type="humanoid", subtype="shalore", define_as="ZEMEKKYS", unique=true},
	{id="blood-master", name="Blood Master", image="npc/humanoid_yaech_blood_master.png", type="humanoid", subtype="yaech", define_as="RING_MASTER", unique=true},
	{id="limmir-the-jeweler", name="Limmir the Jeweler", image="npc/humanoid_elf_limmir_the_jeweler.png", type="humanoid", subtype="elf", define_as="LIMMIR", unique=true},
	{id="protector-myssil", name="Protector Myssil", image="npc/humanoid_halfling_protector_myssil.png", type="humanoid", subtype="halfling", define_as="PROTECTOR_MYSSIL", unique=true},
	{id="rak-shor-cultist", name="Rak'Shor Cultist", image="npc/humanoid_orc_rak_shor_cultist.png", type="humanoid", subtype="orc", define_as="CULTIST_RAK_SHOR", unique=true},
	{id="shady-cornac-man", name="Shady cornac man", image="npc/humanoid_human_shady_cornac_man.png", type="humanoid", subtype="human", define_as="ARENA_AGENT", unique=true},
	{id="tannen", name="Tannen", image="npc/humanoid_human_tannen.png", type="humanoid", subtype="human", define_as="TANNEN", unique=true},
	{id="ben-cruthdar-the-cursed", name="Ben Cruthdar, the Cursed", image="npc/humanoid_human_ben_cruthdar__the_cursed.png", type="humanoid", subtype="human", define_as="BEN_CRUTHDAR", unique=true},
	-- TA-2: second town-resident batch. Thirteen new non-unique bodies with no
	-- define_as (two native-tall nice_tile bodies) plus the wiring-only elven
	-- archer, whose byte-identical native PNG is already the companion-archer
	-- token; the resident reuses that token and the companion entry is unchanged.
	-- The Arena halfling slinger (define_as="SLINGER") and the different-name
	-- PNG reuses (gem crafter, shalore scribe, YEEK_STORE_*) stay native.
	{id="human-citizen", name="human citizen", image="npc/humanoid_human_human_citizen.png", type="humanoid", subtype="human"},
	{id="halfling-citizen", name="halfling citizen", image="npc/humanoid_halfling_halfling_citizen.png", type="humanoid", subtype="halfling"},
	{id="human-farmer", name="human farmer", image="npc/humanoid_human_human_farmer.png", type="humanoid", subtype="human"},
	{id="halfling-gardener", name="halfling gardener", image="npc/humanoid_halfling_halfling_gardener.png", type="humanoid", subtype="halfling"},
	{id="lumberjack", name="lumberjack", image="npc/humanoid_human_lumberjack.png", type="humanoid", subtype="human"},
	{id="halfling-slinger", name="halfling slinger", image="npc/humanoid_halfling_halfling_slinger.png", type="humanoid", subtype="halfling"},
	{id="dwarven-earthwarden", name="dwarven earthwarden", image="npc/humanoid_dwarf_dwarven_earthwarden.png", type="humanoid", subtype="dwarf"},
	{id="yeek-mindslayer", name="yeek mindslayer", image="npc/humanoid_yeek_yeek_mindslayer.png", type="humanoid", subtype="yeek", native_tall=true},
	{id="yeek-psionic", name="yeek psionic", image="npc/humanoid_yeek_yeek_psionic.png", type="humanoid", subtype="yeek"},
	{id="thalore-hunter", name="thalore hunter", image="npc/humanoid_thalore_thalore_hunter.png", type="humanoid", subtype="thalore"},
	{id="thalore-wilder", name="thalore wilder", image="npc/humanoid_thalore_thalore_wilder.png", type="humanoid", subtype="thalore", native_tall=true},
	{id="elven-sun-mage", name="elven sun-mage", image="npc/humanoid_elf_elven_sun_mage.png", type="humanoid", subtype="elf"},
	{id="shalore-rune-master", name="shalore rune master", image="npc/humanoid_shalore_shalore_rune_master.png", type="humanoid", subtype="shalore"},
	{id="elven-archer", name="elven archer", image="npc/humanoid_elf_elven_archer.png", type="humanoid", subtype="elf"},
}

M.by_id = {}
local by_name = {}
for _, entry in ipairs(M.catalog) do
	assert(not M.by_id[entry.id], "duplicate token identity")
	local old = by_name[entry.name]
	if entry.shared_name then
		assert(type(entry.define_as) == "string" and entry.define_as ~= "", "shared token name needs define_as")
		assert(not old or old.shared_name_index, "duplicate token identity")
		old = old or {shared_name_index=true, entries={}}
		assert(not old.entries[entry.define_as], "duplicate token identity")
		old.entries[entry.define_as] = entry
		-- One shared token may be bound to a second native define_as (UB-1
		-- Caldizar: CALDIZAR + CALDIZAR_AOADS, byte-identical art).
		if entry.define_as_alias ~= nil then
			assert(type(entry.define_as_alias) == "string" and entry.define_as_alias ~= "", "shared token alias needs define_as")
			assert(not old.entries[entry.define_as_alias], "duplicate token identity")
			old.entries[entry.define_as_alias] = entry
		end
		by_name[entry.name] = old
	else
		assert(not old, "duplicate token identity")
		by_name[entry.name] = entry
	end
	M.by_id[entry.id] = entry
end

local function namedEntry(index, name, define_as)
	local entry = index[name]
	if entry and entry.shared_name_index then return entry.entries[define_as] end
	return entry
end

-- heart-gloom/npcs.lua prepends one of these exact words to an otherwise
-- unchanged loaded creature (alter() only edits name, talents and rarity in
-- the rodent, bear, canine and plant files it loads). Resolve only covered
-- base names of those four families; unique or define_as entries are never
-- renamed generics. Type, subtype, image and the rest of the appearance
-- contract are still checked below. This is a name provenance rule, not a
-- subtype fallback.
local heart_gloom_families = {
	["vermin/rodent"] = true, ["animal/canine"] = true,
	["animal/bear"] = true, ["immovable/plants"] = true,
}
local heart_gloom_prefixes = {
	"gloomy ", "deformed ", "sick ",
	"dreaming ", "slumbering ", "dozing ",
}
local function heartGloomBase(name)
	if type(name) ~= "string" then return nil end
	for _, prefix in ipairs(heart_gloom_prefixes) do
		if name:sub(1, #prefix) == prefix then
			local entry = namedEntry(by_name, name:sub(#prefix + 1), nil)
			if entry and not entry.unique and not entry.define_as
				and heart_gloom_families[entry.type.."/"..entry.subtype] then return entry end
		end
	end
end

-- Heart Gloom's native load modifier runs AFTER Entity:init has converted
-- unique=true to the original name (engine/Entity.lua). Unlike the generic
-- prefix rule above, this one exact unique must retain that original marker
-- plus Rungof's fixed constructor fields. Both modifiers leave its body alone.
-- Localized prefix/base name strings are built as the native callback builds
-- them; do not strip arbitrary words from unknown unique names.
local function heartGloomRungof(actor)
	local entry = M.by_id.rungof
	if not entry or actor.unique ~= entry.name or actor.define_as ~= nil
		or actor.life_rating ~= 18 or actor.size_category ~= 4
		or type(actor.level_range) ~= "table" or actor.level_range[1] ~= 20
		or actor.level_range[2] ~= nil then return nil end
	for _, prefix in ipairs(heart_gloom_prefixes) do
		if actor.name == prefix .. entry.name then return entry end
		if type(_t) == "function" then
			local ok, localized = pcall(function() return _t(prefix) .. _t(entry.name, "entity name") end)
			if ok and actor.name == localized then return entry end
		end
	end
end


local function empty(value)
	return value == nil or (type(value) == "table" and next(value) == nil)
end

-- Native addShaderAura/removeShaderAura (Actor.lua updateModdableTilePrepare,
-- non-moddable branch) write add_mos entries marked _isshaderaura directly
-- onto whatever was selfbase (self.replace_display or self) at the time. If
-- an aura was applied before a token existed, those entries land on the
-- actor itself; ignore them when judging add_mos "empty" so a genuine extra
-- overlay is still rejected but aura bookkeeping alone is not.
local function emptyIgnoringAura(value)
	if value == nil then return true end
	if type(value) ~= "table" then return false end
	for _, mo in pairs(value) do
		if type(mo) ~= "table" or not mo._isshaderaura then return false end
	end
	return true
end

local tall_keys = {image=true, display_h=true, display_y=true, display_w=true, display_x=true, display_scale=true}

-- Flame of Urh'Rok (data/talents/corruptions/shadowflame.lua) stores the
-- original body as __old_type = {type, subtype}, sets demon/major while it is
-- sustained and restores the pair on deactivation; the image is untouched.
-- Opt-in per entry (urh_rok_form): only that exact talent state, over the
-- catalog's own type/subtype, counts as the same body.
local function urhRokForm(actor, entry)
	if not entry.urh_rok_form or actor.type ~= "demon" or actor.subtype ~= "major" then return false end
	local old = actor.__old_type
	if type(old) ~= "table" or getmetatable(old) ~= nil or old[1] ~= entry.type or old[2] ~= entry.subtype then return false end
	for key in pairs(old) do if key ~= 1 and key ~= 2 then return false end end
	local sustains = actor.sustain_talents
	return type(sustains) == "table" and sustains.T_FLAME_OF_URH_ROK and true or false
end

local bodyAlias -- defined with the other summon aliases below

local function sameBody(actor, entry)
	return (actor.type == entry.type and actor.subtype == entry.subtype) or urhRokForm(actor, entry)
		or bodyAlias(actor, entry)
end

local function nativeTallImage(actor, entry)
	if not (entry.unique or entry.native_tall) or actor.image ~= "invis.png" then return false end
	local mos = actor.add_mos
	if type(mos) ~= "table" then return false end
	-- Native shader-aura bookkeeping may sit before or after the body (a toggle
	-- to native art rebuilds the aura first); skip it as emptyIgnoringAura does.
	-- Exactly one non-aura entry, the body, must remain.
	local mo
	for key, value in pairs(mos) do
		if type(key) ~= "number" or type(value) ~= "table" then return false end
		if not value._isshaderaura then
			if mo then return false end
			mo = value
		end
	end
	if not mo then return false end
	-- Only the verified nice_tile body is supported. Other chained art, auras,
	-- shaders, particles or altered dimensions must retain their native display.
	for key in pairs(mo) do if not tall_keys[key] then return false end end
	return mo.image == entry.image and mo.display_h == 2 and mo.display_y == -1
		and (mo.display_w == nil or mo.display_w == 1)
		and (mo.display_x == nil or mo.display_x == 0)
		and (mo.display_scale == nil or mo.display_scale == 1)
end

-- Same body in another construct (user decisions 2026-09-29). Each catalogued
-- entry below is bound to a zone define_as, but a summon or a define_as-less
-- native leaf builds the identical body (same name, type, subtype and image).
-- The variant is keyed by entry id and must recognise that construct's own
-- distinctive fields; it never accepts a bare same-name actor, a unique, or an
-- actor that has any define_as. Type, subtype, image and the appearance
-- contract are still checked by the caller.
local function summoned(actor) return type(actor.summoner) == "table" end
-- A summon of a party member is converted by PartyMember:init: ai becomes
-- "party_member" and the constructor's own ai is kept in ai_state.ai_party.
local function summonedAI(actor)
	return actor.ai == "summoned"
		or (actor.ai == "party_member" and type(actor.ai_state) == "table" and actor.ai_state.ai_party == "summoned")
end

local variants = {
	-- master-of-flesh.lua minions_list.ghoul via necroSetupSummon (spells.lua)
	ghoul = function(a)
		return summoned(a) and a.necrotic_minion == true and a.ghoul_minion == "ghoul" and a.basic_ghoul_minion == true
	end,
	-- rot.lua carrionworm() (Worm Rot / Infestation, horror.lua spawn)
	["carrion-worm-mass"] = function(a)
		return summoned(a) and a.carrion_worm == true and summonedAI(a) and a.summoner_gain_exp == true
	end,
	-- summon-distance.lua Fire Drake on_arrival (Wyrmic Grand Arrival escort)
	["fire-drake-hatchling"] = function(a)
		return summoned(a) and summonedAI(a) and a.wild_gift_summon == true and a.wild_gift_summon_ignore_cap == true
	end,
	-- general/npcs/sunwall-town.lua: the Gates of Morning leaf has no define_as
	-- (the Charred Scar one binds SUN_PALADIN_DEFENDER; the paladin-vs-vampire
	-- vault copy differs in rank, level range and AI). Pinned by the leaf's own
	-- numbers instead of the name alone.
	["human-sun-paladin"] = function(a)
		local lr = a.level_range
		if a.summoner or type(lr) ~= "table" or lr[2] ~= nil then return false end
		-- Gates of Morning leaf (sunwall-town.lua)
		if a.rank == 3 and a.rarity == 3 and a.exp_worth == 1 and a.ai == "tactical"
			and a.autolevel == "warrior" and a.life_rating == 10 and a.size_category == 3 and lr[1] == 5 then return true end
		-- maps/vaults/auto/greater/paladin-vs-vampire.lua inline actor (tile 'S'):
		-- rank 2, level 10+, dumb_talented_simple AI, warriormage, hard sunwall faction, no rarity.
		return a.rank == 2 and a.rarity == nil and a.exp_worth == 1 and a.ai == "dumb_talented_simple"
			and a.autolevel == "warriormage" and a.size_category == 3 and a.hard_faction == "sunwall"
			and a.positive_regen == 10 and lr[1] == 10
	end,
}

-- Image aliases (user decision 2026-09-30, "summons wear the token of the
-- monster they copy"): a summon constructor may draw the same creature with
-- another native PNG. The alias is per entry, names exactly one extra PNG and
-- is honoured ONLY when the actor is that constructor's real summon (its own
-- distinctive fields); appearance() consults it after the ordinary
-- actor.image==entry.image path and never for uniques or define_as actors.
-- summon-distance.lua Ritch Flamespitter (wild gift): image npc/summoner_ritch.png.
local image_aliases = {
	["ritch-flamespitter"] = {
		image = "npc/summoner_ritch.png",
		check = function(a)
			return summoned(a) and summonedAI(a) and a.wild_gift_summon == true and a.summoner_gain_exp == true
				and a.is_nature_summon == true and a.wild_gift_detonate == "T_RITCH_FLAMESPITTER"
		end,
	},
}
local function aliasImage(actor, entry)
	local alias = image_aliases[entry.id]
	return alias ~= nil and actor.image == alias.image and not entry.unique and actor.define_as == nil
		and actor.unique == nil and alias.check(actor) and true or false
end

-- Body aliases (user decision 2026-09-30): a summon constructor may give the
-- copied creature another type/subtype. talents/gifts/summon-utility.lua:276
-- builds the Spider summon as animal/spider with the giant spider's name and
-- PNG, while the catalogued zone spider is spiderkin/spider. The relaxed pair
-- is honoured only for that real Wild Gift summon (its own fields and the
-- Spider talent id T_SPIDER, summon-utility.lua:216,293-302) and never for
-- uniques or define_as actors, so the tutorial TUT_SPIDER_1 (spiderkin,
-- define_as) keeps its native art and a bare animal/spider "giant spider" too.
local body_aliases = {
	["giant-spider"] = {
		type = "animal", subtype = "spider",
		check = function(a)
			return summoned(a) and summonedAI(a) and a.wild_gift_summon == true and a.summoner_gain_exp == true
				and a.is_nature_summon == true and a.wild_gift_detonate == "T_SPIDER"
		end,
	},
}
bodyAlias = function(actor, entry)
	local alias = body_aliases[entry.id]
	return alias ~= nil and actor.type == alias.type and actor.subtype == alias.subtype
		and not entry.unique and actor.define_as == nil and actor.unique == nil and alias.check(actor) and true or false
end

-- The nature summons of talents/gifts rename themselves to
-- "<name> (wild summon)" when the caster has the wild_summon attribute.
-- Only these covered same-body summons accept that exact form.
local wild_summon_ids = {minotaur=true, ["black-jelly"]=true, ["fire-drake"]=true, ["ritch-flamespitter"]=true}
-- The Wild Gift Spider (body alias above) builds the same localized rename.
wild_summon_ids["giant-spider"] = true
-- Native code builds the name as ("%s (wild summon)"):tformat(_t(m.name)), so
-- the stored string depends on the active locale. Rebuild the expected string
-- exactly that way for each covered entry and accept only equality with it,
-- or with the English form (what tformat returns when no locale is active).
local function wildSummonNames(entry)
	local names = {[entry.name .. " (wild summon)"] = true}
	if type(_t) == "function" and type(("").tformat) == "function" then
		local ok, localized = pcall(function() return ("%s (wild summon)"):tformat(_t(entry.name)) end)
		if ok and type(localized) == "string" then names[localized] = true end
	end
	return names
end
local wild_summon_entries = {}
for id in pairs(wild_summon_ids) do wild_summon_entries[#wild_summon_entries + 1] = M.by_id[id] end
local function wildSummonBase(actor)
	local name = actor.name
	if type(name) ~= "string" or not summoned(actor) or actor.wild_gift_summon ~= true then return nil end
	for _, entry in ipairs(wild_summon_entries) do
		if not entry.unique and not entry.define_as and wildSummonNames(entry)[name] then return entry end
	end
end

-- Name aliases (user decision 2026-09-30, "summons wear the token of the
-- monster they copy"): a summon or minion constructor may draw a catalogued
-- monster's body (same type, subtype and PNG) under another name. Each alias
-- names exactly one extra name and is honoured ONLY for that constructor's real
-- summon (its own distinctive fields); it never applies to uniques or define_as
-- actors, and type/subtype/image/appearance are still checked by the caller.
-- Native code builds these names with _t"..." so the stored string depends on
-- the locale; accept the English name and its _t() form, as wildSummonNames does.
-- Not aliased (stay native): shadowy assassin (traps.lua:318 sets shader
-- shadow_simulacrum, a different appearance), terror and tormentor (nightmare
-- horror PNG, no token yet).
-- max_vim=200 on the Corpathus / Blood-Edge constructors grows with level-ups
-- (live: Vilespawn 204, Blood-Edge animated blood 256); their blight 100 /
-- nature -100 resist pair is fixed, so the summon guards use that instead.
local function blightNatureResists(a)
	return type(a.resists) == "table" and a.resists.BLIGHT == 100 and a.resists.NATURE == -100
end
local name_aliases = {
	-- Blood-Edge uses _t"animated blood" at construction (pool leaf is English).
	{name = "animated blood", id = "animated-blood", check = function(a)
		return summoned(a) and summonedAI(a) and a.ai_real == "tactical"
			and a.autolevel == "dexmage" and blightNatureResists(a)
			and a.negative_status_effect_immune == 1 and a.summoner_gain_exp == true
	end},
	-- talents/misc/horrors.lua:299 Void Shard (void horror body, smaller)
	{name = "void shard", id = "void-horror", check = function(a)
		return summoned(a) and summonedAI(a) and a.summoner_gain_exp == true and a.ai_real == "dumb_talented_simple"
			and a.autolevel == "summoner" and a.size_category == 1 and a.life_rating == 2 and a.fear_immune == 1
	end},
	-- damage_types.lua:3453 Garkul's orc spirit (berserker body)
	{name = "orc spirit", id = "orc-berserker", check = function(a)
		return summoned(a) and summonedAI(a) and a.ai_real == "dumb_talented_simple" and a.autolevel == "warrior"
			and a.life_rating == 12 and a.exp_worth == 0 and a.summoner_gain_exp == nil
	end},
	-- world-artifacts.lua:3439 Corpathus' Vilespawn (oozing horror body, image= set explicitly)
	{name = "Vilespawn", id = "oozing-horror", check = function(a)
		return summoned(a) and summonedAI(a) and a.ai_real == "tactical" and a.autolevel == "dexmage"
			and a.summoner_gain_exp == true and a.life_rating == 8 and a.silent_levelup == true
			and blightNatureResists(a)
	end},
	-- talents/undeads/ghoul.lua:159 Gnaw's Risen Ghoul
	{name = "Risen Ghoul", id = "ghoul", check = function(a)
		return summoned(a) and summonedAI(a) and a.ai_real == "tactical" and a.autolevel == "ghoul"
			and a.summoner_gain_exp == true and a.silent_levelup == true and a.combat_armor_hardiness == 40
	end},
	-- timed_effects/other.lua:1025 Curse of Corpses' walking corpse
	{name = "walking corpse", id = "ghoul", check = function(a)
		return summoned(a) and summonedAI(a) and a.ai_real == "dumb_talented_simple" and a.autolevel == "ghoul"
			and a.summoner_gain_exp == true and a.no_drops == true and a.silent_levelup == nil
	end},
}
local function nameAlias(actor)
	local name = actor.name
	if type(name) ~= "string" or actor.define_as ~= nil or actor.unique ~= nil then return nil end
	for _, alias in ipairs(name_aliases) do
		local match = name == alias.name
		if not match and type(_t) == "function" then
			local ok, localized = pcall(_t, alias.name)
			match = ok and localized == name
		end
		if match then
			local entry = M.by_id[alias.id]
			if entry and not entry.unique and alias.check(actor) then return entry end
			return nil
		end
	end
end

local function sameBodyVariant(actor, entry)
	local check = variants[entry.id]
	return check ~= nil and not entry.unique and actor.define_as == nil and actor.unique == nil and check(actor) and true or false
end

-- Temporal clones (chronomancy/chronomancer.lua:240 makeParadoxClone, used by
-- Paradox talents and anomalies on any nearby actor) copy the target with
-- cloneActor and rename it ("%s's temporal clone"):tformat(target:getName()).
-- Policy: a same-body copy wears the copied creature's token, so this applies
-- to every covered non-unique entry, not to one batch. The clone keeps the
-- target's define_as, which must equal the entry's; uniques stay native, and
-- type/subtype/image/appearance are still checked by the caller. The name map
-- is rebuilt when the active _t / tformat functions change (locale switch).
local cloneNames, cloneNamesT, cloneNamesF
local function temporalCloneNames()
	local t, f = _t, string.tformat
	if cloneNames and cloneNamesT == t and cloneNamesF == f then return cloneNames end
	cloneNames, cloneNamesT, cloneNamesF = {}, t, f
	local function add(name, entry)
		if type(name) ~= "string" then return end
		local old = cloneNames[name]
		if entry.shared_name and (old == nil or (type(old) == "table" and old.shared_name_index)) then
			old = old or {shared_name_index=true, entries={}}
			old.entries[entry.define_as] = entry
			cloneNames[name] = old
		elseif old == nil then cloneNames[name] = entry
		elseif old ~= entry then cloneNames[name] = false end -- ambiguous: stay native
	end
	for _, entry in ipairs(M.catalog) do
		if not entry.unique then
			add(entry.name .. "'s temporal clone", entry)
			if type(t) == "function" and type(f) == "function" then
				local ok, localized = pcall(function()
					return ("%s's temporal clone"):tformat(_t(entry.name, "entity name"))
				end)
				if ok and localized ~= entry.name .. "'s temporal clone" then add(localized, entry) end
			end
		end
	end
	return cloneNames
end
local function temporalClone(actor)
	if actor.unique ~= nil or not summoned(actor) or not summonedAI(actor)
		or actor.summoner_gain_exp ~= true or actor.ai_real ~= "tactical" or actor.exp_worth ~= 0
		or type(actor.summon_time) ~= "number" or actor.summon_time < 0
		or type(actor.max_level) ~= "number" or actor.max_level ~= actor.level
		or type(actor.ai_tactic) ~= "table" or actor.ai_tactic.escape ~= 0 then return nil end
	local entry = type(actor.name) == "string" and namedEntry(temporalCloneNames(), actor.name, actor.define_as)
	if entry and actor.define_as == entry.define_as then return entry end
end

local function exactIdentity(actor, allow_player_identity)
	local entry = namedEntry(by_name, actor.name, actor.define_as) or heartGloomBase(actor.name) or heartGloomRungof(actor) or wildSummonBase(actor)
	local aliased = false
	if not entry then entry = nameAlias(actor) or temporalClone(actor); aliased = entry ~= nil end
	if not entry then return nil, actor.unique and "unknown-unique" or "no-art" end
	if not sameBody(actor, entry) then return nil, "body-changed" end
	local bound = actor.define_as == entry.define_as
		or (entry.define_as_alias ~= nil and actor.define_as == entry.define_as_alias)
	if not bound and not aliased and not sameBodyVariant(actor, entry) then return nil, "identity-changed" end
	-- Native Party:setPlayer converts a normal creature to Player and sets the
	-- literal "player" sentinel. Only the integration can verify party/control
	-- history; callers cannot use this opt-in to admit any other unique actor.
	if actor.unique and not entry.unique
		and not (allow_player_identity == true and actor.unique == "player") then return nil, "unknown-unique" end
	return entry
end

-- Blood-Edge (world-artifacts-far-east.lua): same animated-blood PNG at
-- 1x dimensions, not the pool's 2x tall layout. Accept only this constructor's
-- summoned dexmage and exactly one unmodified body; aura bookkeeping is kept.
local function bloodEdgeBody(actor, entry)
	if entry.id ~= "animated-blood" or actor.image ~= "invis.png"
		or actor.define_as ~= nil or actor.unique ~= nil or type(actor.summoner) ~= "table"
		or not summonedAI(actor) or actor.ai_real ~= "tactical" or actor.autolevel ~= "dexmage"
		or actor.summoner_gain_exp ~= true or actor.negative_status_effect_immune ~= 1
		or not blightNatureResists(actor) or actor.rank ~= 3 or actor.exp_worth ~= 0
		or actor.silent_levelup ~= true or actor.life_rating ~= 10
		or type(actor.summon_time) ~= "number" or actor.summon_time < 0 or actor.summon_time > 9
		or type(actor.add_mos) ~= "table" then return false end
	local body
	for key, value in pairs(actor.add_mos) do
		if type(key) ~= "number" or type(value) ~= "table" then return false end
		if not value._isshaderaura then
			if body then return false end
			body = value
		end
	end
	if not body then return false end
	for key in pairs(body) do if not tall_keys[key] then return false end end
	return body.image == entry.image and body.display_h == 1 and body.display_y == 0
		and (body.display_w == nil or body.display_w == 1)
		and (body.display_x == nil or body.display_x == 0)
		and (body.display_scale == nil or body.display_scale == 1)
end

local function appearance(actor, entry, owned_display)
	-- Never claim an effect's or another addon's display. The owner passes the
	-- exact Entity it installed, not a boolean or a saved display from startup.
	if actor.replace_display and actor.replace_display ~= owned_display then return nil, "external-display" end
	if not sameBody(actor, entry) then return nil, "body-changed" end
	-- These visual systems can communicate state or a different body. Preserve
	-- them until there is an explicit rendering contract for that appearance.
	if actor.moddable_tile then return nil, "moddable-tile" end
	-- quad_hue is a cosmetic native colour cycle only for these pinned bodies.
	-- Entity:getMapObjects builds the fresh replacement Entity without shader;
	-- applying the actor shader there would tint the neutral physical disc.
	if actor.shader and not (entry.native_shader == "quad_hue"
		and actor.shader == entry.native_shader and actor.shader_args == nil) then return nil, "shader" end
	if entry.native_shader and actor.shader_args ~= nil then return nil, "shader-args" end
	if actor.anim then return nil, "animation" end
	if not empty(actor.add_displays) then return nil, "add-displays" end
	if not empty(actor.textures) then return nil, "textures" end
	-- A native shader aura (addShaderAura) is drawn as a chained overlay
	-- wrapped around whatever image is on the current display. Keep the token
	-- installed so the aura wraps our art instead of falling back to native
	-- art; the integration rebuilds the aura mo entries onto our Entity.
	if actor.image == entry.image or aliasImage(actor, entry) then
		if emptyIgnoringAura(actor.add_mos) then return "single" end
		return nil, "add-mos"
	end
	if nativeTallImage(actor, entry) then return "native-tall" end
	if bloodEdgeBody(actor, entry) then return "single-body-summon" end
	if actor.image == "invis.png" and (entry.unique or entry.native_tall) then return nil, "native-tall-changed" end
	return nil, "body-changed"
end

-- This is a serializable provenance record, never a cached rendering Entity.
-- Bind it to both the catalog body and the generated native identity. Keeping
-- rank/faction/uid out allows live rank changes, cloning and native save/load.
local origin_fields = {
	version=true, source=true, id=true, base_name=true, base_image=true,
	base_type=true, base_subtype=true, base_define_as=true, appearance=true,
	display_w=true, display_h=true, display_x=true, display_y=true, display_scale=true,
}
local generated_fields = {name=true, define_as=true, unique=true}
local dimensions = {display_w=1, display_h=1, display_x=0, display_y=0, display_scale=1}

local function finite(value)
	return type(value) == "number" and value == value and value ~= math.huge and value ~= -math.huge
end

local function originEntry(origin, generated)
	if type(origin) ~= "table" or getmetatable(origin) ~= nil then return nil end
	for key in pairs(origin) do
		if not origin_fields[key] and not (generated and generated_fields[key]) then return nil end
	end
	if origin.version ~= 1 or origin.source ~= "createRandomBoss" or type(origin.id) ~= "string" then return nil end
	local entry = M.by_id[origin.id]
	if not entry or origin.base_name ~= entry.name or origin.base_image ~= entry.image
		or origin.base_type ~= entry.type or origin.base_subtype ~= entry.subtype
		or origin.base_define_as ~= (entry.define_as or false) then return nil end
	if origin.appearance ~= "single" and not (origin.appearance == "native-tall" and entry.unique) then return nil end
	for key in pairs(dimensions) do if not finite(origin[key]) then return nil end end
	if generated and (type(origin.name) ~= "string" or origin.name == ""
		or type(origin.define_as) ~= "string" or origin.define_as == ""
		or origin.unique ~= origin.name) then return nil end
	return entry
end

local function originAppearance(actor, entry, origin, owned_display)
	local form, reason = appearance(actor, entry, owned_display)
	if not form then return nil, reason end
	if form ~= origin.appearance then return nil, "body-changed" end
	for key, default in pairs(dimensions) do
		local value = actor[key]
		if value == nil then value = default end
		if value ~= origin[key] then return nil, "body-changed" end
	end
	return form
end

local function ownedDisplay(actor)
	local state = actor._checker_token
	return type(state) == "table" and state.display or nil
end

function M.captureRandomOrigin(base)
	if type(base) ~= "table" then return nil, "invalid-actor" end
	-- Deliberately do not use identify/explain: an old random-origin marker is
	-- not evidence for a new generation. Only a known, exact base qualifies.
	local entry, reason = exactIdentity(base, false)
	if not entry then return nil, reason end
	local form, reason = appearance(base, entry, ownedDisplay(base))
	if not form then return nil, reason end
	local origin = {version=1, source="createRandomBoss", id=entry.id,
		base_name=entry.name, base_image=entry.image, base_type=entry.type,
		base_subtype=entry.subtype, base_define_as=entry.define_as or false, appearance=form}
	for key, default in pairs(dimensions) do
		local value = base[key]
		if value == nil then value = default end
		if not finite(value) then return nil, "body-changed" end
		origin[key] = value
	end
	return origin
end

function M.recordRandomOrigin(actor, capture, boss_id)
	if type(actor) ~= "table" then return nil, "invalid-actor" end
	-- Native clone copies plain tables. Discard any inherited record even when
	-- this generation is ineligible; it must not authenticate the new actor.
	actor._checker_token_origin = nil
	local entry = originEntry(capture, false)
	if not entry then return nil, "invalid-origin" end
	local form, reason = originAppearance(actor, entry, capture, ownedDisplay(actor))
	if not form then return nil, reason end
	if actor.randboss ~= true or type(actor.name) ~= "string" or actor.name == ""
		or actor.unique ~= actor.name or type(boss_id) ~= "string" or boss_id == ""
		or actor.define_as ~= boss_id then return nil, "stale-origin" end
	local origin = {}
	for key in pairs(origin_fields) do origin[key] = capture[key] end
	origin.name, origin.define_as, origin.unique = actor.name, boss_id, actor.unique
	actor._checker_token_origin = origin
	return entry.id, "random-origin"
end

function M.explain(actor, owned_display, allow_player_identity)
	if type(actor) ~= "table" then return nil, "invalid-actor" end
	if actor.replace_display and actor.replace_display ~= owned_display then return nil, "external-display" end
	local entry, reason = exactIdentity(actor, allow_player_identity)
	if entry then
		local form, reason = appearance(actor, entry, owned_display)
		if form then return entry.id, "exact-identity" end
		return nil, reason
	end
	local origin = actor._checker_token_origin
	if origin == nil then return nil, reason end
	entry = originEntry(origin, true)
	if not entry then return nil, "invalid-origin" end
	if actor.randboss ~= true or actor.name ~= origin.name or actor.define_as ~= origin.define_as
		or (actor.unique ~= origin.unique and not (allow_player_identity == true and actor.unique == "player")) then
		return nil, "stale-origin"
	end
	local form, reason = originAppearance(actor, entry, origin, owned_display)
	if not form then return nil, reason end
	return entry.id, "random-origin"
end

function M.identify(actor, owned_display, allow_player_identity)
	local id = M.explain(actor, owned_display, allow_player_identity)
	return id
end

function M.image(id)
	assert(M.by_id[id], "unknown monster token: "..tostring(id))
	return "checker-revised+tokens/"..id..".png"
end

-- Two independent small-tile trials. Every unlisted cell size and every
-- unlisted token keeps the flattened token at 64/96px and above 48px cells.
--
-- R32 ordinary layers (creature 1.25x inside its own cell) are OFF by default;
-- the 19 layer PNGs stay shipped so M.layer_trial=true restores them.
-- R33 boss standees (native-tall creature over the own-cell board piece) have
-- their own switch and do not depend on M.layer_trial.
M.layer_trial = false
M.standee_trial = true
-- Ordinary R32 small-cell threshold only (R38). The standee keeps its own
-- minimum tile gate (M.standee_min_cell), so it must not read this.
M.layer_max_cell = 48

-- Ordinary (R32) ids.
M.layer_ids = {
	wolf=true, warg=true, ["great-wolf"]=true, ["orc-warrior"]=true,
	["orc-archer"]=true, ["orc-assassin"]=true, ["skeleton-warrior"]=true,
	["skeleton-mage"]=true, ["skeleton-archer"]=true, ["giant-spider"]=true,
	ungole=true, ["weaver-queen"]=true, ["storm-wyrm"]=true,
	["human-guard"]=true, ["derth-guard"]=true, ["elven-mage"]=true,
	necromancer=true, pyromancer=true, ["yeek-mindslayer"]=true,
}

-- Standee ids: every id with a shipped upright standee layer. Eligibility is
-- static and decided from the catalogue entry alone (M.standeeRule): the id
-- must be natively tall (a generated token-standee-heights entry) and taller
-- than one cell, and it must ship layer art. Rank and the live size_category
-- are not consulted, so a size-changing buff cannot flip a token mid-fight.
-- The R43 original four and the R47 batch-1 seventeen ship art (21 total).
-- kra-tor's axe blade sits above a ~1-cell body, so it is flat and its
-- layer/aura are archived; it must not be added here.
M.standee_ids = {
	ninandra=true, ["ogre-guard"]=true,
	["snow-giant"]=true, ["ravenous-horror"]=true,
	-- R47 batch 1 (17 ids): bone giants, golems, snow giants, uniques and
	-- giants whose masters were accepted by the R47 art review.
	["heavy-bone-giant"]=true, ["runed-bone-giant"]=true,
	["eternal-bone-giant"]=true, atamathon=true, ["heavy-sentinel"]=true,
	["burb-snow-giant-champion"]=true, archlich=true,
	["snow-giant-chieftain"]=true, ["snow-giant-boulder-thrower"]=true,
	["snow-giant-thunderer"]=true, ["minotaur-maze"]=true,
	["champion-of-urh-rok"]=true, ["ogre-warmaster"]=true, celia=true,
	dremling=true, ["forge-giant"]=true, ["healer-astelrid"]=true,
	-- R50 batch 2: 18 accepted upright masters; native identity contracts unchanged.
	["treant"]=true,
	["wrathroot"]=true,
	["ogre-mauler"]=true,
	["ogre-rune-spinner"]=true,
	["ultimate-shivgoroth"]=true,
	["ogric-abomination"]=true,
	["half-finished-bone-giant"]=true,
	["norgos-guardian"]=true,
	["norgos-frozen"]=true,
	["horned-horror"]=true,
	["harkor-zun"]=true,
	["dolleg"]=true,
	["duathedlen"]=true,
	["thaurhereg"]=true,
	["uruivellas"]=true,
	["xhaiak-arachnomancer"]=true,
	["rotting-titan"]=true,
	["corrupted-daelach"]=true,
	-- R51 batch 3: 13 accepted native-tall upright masters.
	["rantha"]=true,
	["varsha"]=true,
	["fire-wyrm"]=true,
	["ice-wyrm"]=true,
	["storm-wyrm"]=true,
	["venom-wyrm"]=true,
	["greater-multi-hued-wyrm"]=true,
	["ultimate-faeros"]=true,
	["fyrk"]=true,
	["snaproot"]=true,
	["temporal-defiler"]=true,
	["arch-zephyr"]=true,
	["ak-gishil"]=true,
	-- R52 final optional batch: six accepted native-tall masters.
	["prox"]=true,
	["bill"]=true,
	["shax"]=true,
	["onilug"]=true,
	["chronolith-twin"]=true,
	["chronolith-clone"]=true,
	-- R53 accepted native-tall sand wyrm.
	["briagh"]=true,
}
-- Standees render only at tiles >= this many pixels; below that (16px, small
-- custom sizes) the flat token is used.
M.standee_min_cell = 24

-- Union of every id with a layer file. The build tool and the production asset
-- tests read this, so a layer can be built and shipped while a trial switch is
-- off (the R32 files stay reachable for M.layer_trial=false).
M.layer_file_ids = {}
for id in pairs(M.layer_ids) do M.layer_file_ids[id] = true end
for id in pairs(M.standee_ids) do M.layer_file_ids[id] = true end

-- Display-geometry manifest (the alpha bbox of each layer plus that file's
-- canvas size in px), generated by tools/build_token_layers.py. Standee layers ship on a 256px
-- canvas (R38, so a standee at a 128px tile is not upscaled); ordinary R32
-- layers stay at 128px. A missing box means the standee has no known feet
-- anchor and stays on the flattened path.
M.layer_geometry_path = '/data-checker-revised/token-layer-geometry.lua'
M.layer_geometry = {}
do
	if fs and fs.exists and loadfile and fs.exists(M.layer_geometry_path) then
		local chunk = loadfile(M.layer_geometry_path)
		local ok, geometry = false, nil
		if chunk then ok, geometry = pcall(chunk) end
		if ok and type(geometry) == 'table' then M.layer_geometry = geometry end
	end
end

-- Layer file lookup. This is flag-independent on purpose: the audit and the
-- build tool must see every shipped layer, and Game.lua applies the switches.
function M.layerImage(id)
	if not M.layer_file_ids[id] then return nil end
	assert(M.by_id[id], "unknown layered monster token: "..tostring(id))
	return "checker-revised+tokens-layer/"..id..".png"
end
-- POT shader-aura copy of a standee layer (R42). Only standees ship one:
-- the aura needs transparent headroom above the body that the 256px creature
-- layer does not have, and the aura quad must stay near native size (R41's
-- pad on every side drew the flames ~2x too large). The aura quad reads the
-- same geometry at the POT canvas, so the creature stays aligned.
function M.layerAuraImage(id)
	if not (id and M.standee_ids[id]) then return nil end
	assert(M.by_id[id], "unknown layered monster token: "..tostring(id))
	return "checker-revised+tokens-layer/aura/"..id..".png"
end
function M.layerAuraGeometry(id)
	local box=M.layer_geometry[id]
	local aura=type(box)=='table' and box.aura
	if type(aura)~='table' then return nil end
	-- R46: the aura texture can be non-square (128x256 for a tall body). Default
	-- the width/height to the committed square canvas for older geometry.
	aura.canvas_w=aura.canvas_w or aura.canvas
	aura.canvas_h=aura.canvas_h or aura.canvas
	return aura
end
function M.layerDisc()
	if not (M.layer_trial or M.standee_trial) then return nil end
	return "checker-revised+tokens-layer/_disc.png"
end
-- Ordinary R32 path only (independent of the standee switch).
function M.layeredId(id)
	return (M.layer_trial and M.layer_ids[id]) and true or false
end
function M.layerGeometry(id)
	local box = M.layer_geometry[id]
	return type(box) == 'table' and box or nil
end

-- The standee eligibility rule lives in this ONE function and is decided
-- statically from the catalogue entry: natively tall (a generated height-table
-- entry) and taller than one cell. It never reads the actor, so rank and any
-- live size_category change are irrelevant.
function M.standeeRule(entry)
	local height=entry and Style and Style.standeeHeight(entry.id)
	return height~=nil and height>1.0
end
-- Standees only at tiles >= M.standee_min_cell pixels (flat below).
function M.standeeTileAllowed(cell)
	return Style and Style.standeeCellAllowed(cell) and true or false
end
function M.standeeEligible(actor, entry)
	-- The actor argument is accepted for call-site compatibility only and is
	-- never consulted: eligibility is static.
	if not M.standee_trial then return false end
	if not (entry and M.standee_ids[entry.id]) then return false end
	if not M.layerGeometry(entry.id) then return false end
	return M.standeeRule(entry) and true or false
end

return M
