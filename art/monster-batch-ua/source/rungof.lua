-- Verified leaf and inherited base; source hashes in source-contracts.json
newEntity{ base = "BASE_NPC_CANINE",
	name = "Rungof the Warg Titan", color=colors.VIOLET, unique=true, image="npc/canine_rungof.png",
	desc = _t[[It is a large wolf with eyes full of cunning, thrice the size of a normal warg.]],
	level_range = {20, nil}, exp_worth = 2,
	rank = 3.5,
	size_category = 4,
	rarity = 50,
	max_life = 220, life_rating = 18,
	combat_armor = 25, combat_def = 0,
	combat = { dam=resolvers.levelup(20, 1, 1.3), atk=20, apr=16 },

	ai = "tactical",
	auto_classes={
		{class="Brawler", start_level=20, level_rate=75},
	},
	resolvers.drops{chance=100, nb=1, {defined="RUNGOF_FANG"} },

	make_escort = {
		{type="animal", subtype="canine", name="warg", number=6},
	},
	resolvers.inscriptions(2, "infusion"),
	resolvers.talents{
		[Talents.T_RUSH]={base=3, every=10},
		[Talents.T_CRIPPLE]={base=3, every=10},
		[Talents.T_HACK_N_BACK]={base=3, every=10},
		[Talents.T_SET_UP]={base=3, every=10},
		[Talents.T_VITALITY]={base=3, every=8},
		[Talents.T_UNFLINCHING_RESOLVE]={base=3, every=8},
		[Talents.T_DAUNTING_PRESENCE]={base=3, every=8},
		[Talents.T_HOWL]=5,
	},
}
-- INHERITED BASE
newEntity{
	define_as = "BASE_NPC_CANINE",
	type = "animal", subtype = "canine",
	display = "C", color=colors.WHITE,
	body = { INVEN = 10 },
	sound_moam = {"creatures/wolves/wolf_hurt_%d", 1, 2},
	sound_die = {"creatures/wolves/wolf_hurt_%d", 1, 1},
	sound_random = {"creatures/wolves/wolf_howl_%d", 1, 3},

	max_stamina = 150,
	rank = 1,
	size_category = 2,
	infravision = 10,

	autolevel = "warrior",
	ai = "dumb_talented_simple", ai_state = { ai_move="move_complex", talent_in=2, },
	global_speed_base = 1.2,
	stats = { str=10, dex=17, mag=3, con=7 },
	combat = { dammod={str=0.6}, sound="creatures/wolves/wolf_attack_1" },
	combat_armor = 1, combat_def = 1,
	not_power_source = {arcane=true, technique_ranged=true},
}
