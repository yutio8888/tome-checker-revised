-- Verified leaf and inherited base; source hashes in source-contracts.json
newEntity{ base = "BASE_NPC_ORC",
	name = "Kra'Tor the Gluttonous", unique = true,
	color=colors.DARK_KHAKI,
	resolvers.nice_tile{image="invis.png", add_mos = {{image="npc/humanoid_orc_kra_tor_the_gluttonous.png", display_h=2, display_y=-1}}},
	desc = _t[[A morbidly obese orc with greasy pockmarked skin and oily long black hair.  He's clad in plate mail and carries a huge granite battleaxe that's nearly as large as he is.]],
	level_range = {38, nil}, exp_worth = 2,
	rarity = 50,
	rank = 3.5,
	max_life = resolvers.rngavg(600, 800),
	life_rating = 22,
	move_others=true,
	resolvers.auto_equip_filters("Berserker"),
	resolvers.equip{
		{type="weapon", subtype="battleaxe", defined="GAPING_MAW", random_art_replace={chance=75}, autoreq=true},
		{type="armor", subtype="massive", tome_drops="boss", autoreq=true},
		{type="charm", forbid_power_source={arcane=true}, autoreq=true}
	},
	resolvers.drops{chance=100, nb=2, {tome_drops="boss"} },

	combat_armor = 2, combat_def = 0,

	blind_immune = 0.5,
	confuse_immune = 0.5,
	stun_immune = 0.7,
	knockback_immune = 1,

	autolevel = "wyrmic",
	ai = "tactical", ai_state = { talent_in=1, ai_move="move_astar", },
	ai_tactic = resolvers.tactic"melee",
	resolvers.inscriptions(4, {"movement infusion", "healing infusion", "regeneration infusion", "wild infusion"}),

	resists = { all=25},

	resolvers.talents{
		[Talents.T_ICE_CLAW]={base=4, every=4, max=8},
		[Talents.T_ICY_SKIN]={base=5, every=4, max=9},
		[Talents.T_SAND_BREATH]={base=5, every=4, max=9},

		[Talents.T_RESOLVE]=5,
		[Talents.T_AURA_OF_SILENCE]=5,
		[Talents.T_MANA_CLASH]={base=5, every=5, max=8},

		[Talents.T_WARSHOUT]={base=4, every=4, max=8},
		[Talents.T_DEATH_DANCE]={base=3, every=4, max=7},
		[Talents.T_BERSERKER]={base=5, every=4, max=10},
		[Talents.T_BATTLE_CALL]={base=5, every=4, max=8},
		[Talents.T_CRUSH]={base=3, every=4, max=8},

		[Talents.T_WEAPON_COMBAT]={base=3, every=8, max=5},
		[Talents.T_WEAPONS_MASTERY]={base=3, every=8, max=5},

		[Talents.T_ARMOUR_TRAINING]={base=3, every=7, max=7},

		[Talents.T_SPELL_FEEDBACK] = 1,
	},
	resolvers.sustains_at_birth(),
}
-- INHERITED BASE
newEntity{
	define_as = "BASE_NPC_ORC",
	type = "humanoid", subtype = "orc",
	display = "o", color=colors.UMBER,
	faction = "orc-pride",

	combat = { dam=resolvers.rngavg(5,12), atk=2, apr=6, physspeed=2 },

	body = { INVEN = 10, MAINHAND=1, OFFHAND=1, BODY=1, QUIVER=1, TOOL=1 },
	resolvers.drops{chance=20, nb=1, {} },
	resolvers.drops{chance=10, nb=1, {type="money"} },
	infravision = 10,
	lite = 2,

	life_rating = 11,
	rank = 2,
	size_category = 3,

	open_door = true,

	autolevel = "warrior",
	ai = "dumb_talented_simple", ai_state = { ai_move="move_complex", talent_in=3, },
	stats = { str=20, dex=8, mag=6, con=16 },
	resolvers.talents{ [Talents.T_WEAPON_COMBAT]={base=1, every=10, max=5}, },
	ingredient_on_death = "ORC_HEART",
}
