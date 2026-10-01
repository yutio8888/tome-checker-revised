-- Verified leaf and inherited base; source hashes in source-contracts.json
newEntity{ base="BASE_NPC_ORC_GORBAT", define_as = "GORBAT",
	allow_infinite_dungeon = true,
	name = "Gorbat, Supreme Wyrmic of the Pride", color=colors.VIOLET, unique = true,
	resolvers.nice_tile{image="invis.png", add_mos = {{image="npc/humanoid_orc_gorbat__supreme_wyrmic_of_the_pride.png", display_h=2, display_y=-1}}},
	desc = _t[[An orc with scaly skin, claws and a pair of small wings on his back.]],
	killer_message = _t"and fed to the hatchlings",
	level_range = {40, nil}, exp_worth = 1,
	rank = 5,
	max_life = 250, life_rating = 29, fixed_rating = true,
	infravision = 10,
	stats = { str=12, dex=10, cun=100, mag=21, con=14 },
	move_others=true,

	combat_armor = 10, combat_def = 10,

	open_door = true,

	autolevel = "wyrmic",
	ai = "tactical", ai_state = { talent_in=1, ai_move="move_astar", },
	resolvers.inscriptions(4, "infusion"),

	body = { INVEN = 10, MAINHAND=1, OFFHAND=1, BODY=1, HEAD=1, TOOL=1 },

	resolvers.equip{
		{type="weapon", subtype="greatmaul", force_drop=true, tome_drops="boss", autoreq=true},
		{type="armor", subtype="light", defined="CHROMATIC_HARNESS", random_art_replace={chance=75}, autoreq=true},
		{type="charm", subtype="totem"}
	},
	resolvers.drops{chance=100, nb=1, {defined="ORB_DRAGON"} },
	resolvers.drops{chance=100, nb=5, {tome_drops="boss"} },
	resolvers.drops{chance=100, nb=1, {defined="NOTE_LORE"} },

	talent_cd_reduction={[Talents.T_ICE_BREATH]=3, [Talents.T_FIRE_BREATH]=3, [Talents.T_SAND_BREATH]=3, },
	equilibrium_regen = -10,

	resolvers.talents{
		[Talents.T_NATURE_TOUCH]={base=5, every=6, max=7},

		[Talents.T_ICE_BREATH]={base=10, every=6, max=12},
		[Talents.T_FIRE_BREATH]={base=10, every=6, max=12},
		[Talents.T_SAND_BREATH]={base=10, every=6, max=12},

		[Talents.T_ICY_SKIN]={base=5, every=6, max=7},
		[Talents.T_ICE_CLAW]={base=7, every=6, max=10},

		[Talents.T_BELLOWING_ROAR]={base=7, every=6, max=10},
		[Talents.T_WING_BUFFET]={base=5, every=6, max=7},

		[Talents.T_RIMEBARK]={base=7, every=6, max=10},
		[Talents.T_RITCH_FLAMESPITTER]={base=10, every=6, max=12},
		[Talents.T_RAGE]={base=5, every=6, max=7},
		[Talents.T_RESILIENCE]={base=5, every=6, max=7},
		[Talents.T_MASTER_SUMMONER]={base=5, every=6, max=7},
		[Talents.T_WILD_SUMMON]={base=5, every=6, max=7},
		[Talents.T_GRAND_ARRIVAL]={base=2, every=18, max=4},


		[Talents.T_HOWL]=3,

		[Talents.T_DISARM]={base=5, every=6, max=7},
		[Talents.T_WEAPON_COMBAT]={base=3, every=8, max=5},
		[Talents.T_WEAPONS_MASTERY]={base=3, every=8, max=5},

		[Talents.T_ARMOUR_TRAINING]=3,

		[Talents.T_SPELL_FEEDBACK]=1,
		[Talents.T_MASSIVE_BLOW]=1,
	},

	auto_classes={
		{class="Wyrmic", start_level=40, level_rate=50},
		{class="Summoner", start_level=40, level_rate=50},
	},
	resolvers.sustains_at_birth(),

	on_die = function(self, who)
		game.player:resolveSource():setQuestStatus("orc-pride", engine.Quest.COMPLETED, "gorbat")
		if not game.player:hasQuest("pre-charred-scar") then
			game.player:grantQuest("pre-charred-scar")
		end
	end,
}
-- INHERITED BASE
newEntity{
	define_as = "BASE_NPC_ORC_GORBAT",
	type = "humanoid", subtype = "orc",
	display = "o", color=colors.GREEN,
	faction = "orc-pride", pride = "gorbat",

	combat = { dam=resolvers.rngavg(5,12), atk=2, apr=6, physspeed=2 },

	body = { INVEN = 10, MAINHAND=1, OFFHAND=1, BODY=1, QUIVER=1, TOOL=1},
	resolvers.drops{chance=20, nb=1, {} },
	resolvers.drops{chance=10, nb=1, {type="money"} },
	infravision = 10,
	lite = 1,

	life_rating = 15,
	rank = 2,
	size_category = 3,

	resolvers.racial(),

	open_door = true,
	resolvers.sustains_at_birth(),

	resolvers.inscriptions(2, "infusion"),

	autolevel = "warrior",
	ai = "dumb_talented_simple", ai_state = { ai_move="move_complex", talent_in=3, },
	stats = { str=20, dex=8, mag=6, con=16 },
	ingredient_on_death = "ORC_HEART",
}
