-- Verified leaf and inherited base; source hashes in source-contracts.json
newEntity{ base = "BASE_NPC_SPIDER",
	name = "Ninandra, the Great Weaver", female=1, unique = true,
	color = colors.VIOLET,
	rarity = 50,
	resolvers.nice_tile{image="invis.png", add_mos = {{image="npc/spiderkin_spider_ninandra_the_great_weaver.png", display_h=2, display_y=-1}}},
	desc = _t[[A huge blue and white spiderkin whose form shifts and shimmers in and out of reality.  She spins the threads of fate and binds the destiny of all within her web.]],
	level_range = {45, nil}, exp_worth = 4,
	max_life = 400, life_rating = 25, fixed_rating = true,
	rank = 3.5,
	size_category = 4,

	body = { INVEN = 10, MAINHAND=1, OFFHAND=1, BODY=1, CLOAK=1 },
	resolvers.drops{chance=100, nb=1, {defined="THREADS_FATE", random_art_replace={chance=65}}},
	resolvers.drops{chance=100, nb=5, {ego_chance=100} },

	ai = "tactical",
	ai_tactic = resolvers.tactic"melee", ai_state = { ai_move="move_complex", talent_in=1, },

	combat = { dam=resolvers.levelup(resolvers.mbonus(100, 15), 1, 0.9), atk=16, apr=9, damtype=DamageType.WASTING, dammod={dex=1.2} },

	combat_armor = 7, combat_def = 17,
	resists = { [DamageType.PHYSICAL] = 20, [DamageType.TEMPORAL] = 20, },
	combat_physresist = 50,
	combat_spellresist = 50,
	combat_mentalresist = 50,
	combat_spellpower = 50,
	see_invisible = 18,

	make_escort = {
		{type = "spiderkin", name="weaver patriarch", number=2, no_subescort=true},
	},

	summon = {
		{type = "spiderkin", subtype = "spider", name="weaver young", number=4, hasxp=false},
	},

	resolvers.talents{
		[Talents.T_SPIDER_WEB]={base=7, every=6},
		[Talents.T_LAY_WEB]={base=7, every=6},

		-- She is the fateweaver, chronomancers learned these talents by emulating her
		[Talents.T_SPIN_FATE]={base=7, every=6},
		[Talents.T_WEBS_OF_FATE]={base=7, every=6},
		[Talents.T_FATEWEAVER]={base=7, every=6},
		[Talents.T_SEAL_FATE]={base=7, every=6},

		[Talents.T_STOP]={base=7, every=6},
		[Talents.T_STATIC_HISTORY]={base=7, every=6},
		[Talents.T_CHRONO_TIME_SHIELD]={base=7, every=6},
		[Talents.T_SPACETIME_STABILITY]={base=7, every=6},

		[Talents.T_DIMENSIONAL_STEP]=4,  -- At five this turns to swap, we want her to close with it
		[Talents.T_PHASE_PULSE]={base=7, every=6},
		[Talents.T_DIMENSIONAL_SHIFT]={base=7, every=6},

		[Talents.T_RETHREAD]={base=7, every=6},

		[Talents.T_SUMMON]=1,

		[Talents.T_LUCKY_DAY] = 1,
	},
}
-- INHERITED BASE
newEntity{
	define_as = "BASE_NPC_SPIDER",
	type = "spiderkin", subtype = "spider",
	display = "S", color=colors.WHITE,
	desc = _t[[Arachnophobia...]],

	combat = { dam=resolvers.levelup(resolvers.mbonus(40, 70), 1, 0.9), atk=16, apr=9, damtype=DamageType.NATURE, dammod={dex=1.2} },

	body = { INVEN = 10, MAINHAND=1, OFFHAND=1, BODY=1 },

	infravision = 10,
	size_category = 2,
	rank = 1,

	autolevel = "spider",
	ai = "dumb_talented_simple", ai_state = { ai_move="move_complex", talent_in=4, },
	global_speed_base = 1.2,
	stats = { str=15, dex=15, mag=8, con=10 },

	resolvers.inscriptions(2, "infusion"),

	resolvers.sustains_at_birth(),

	poison_immune = 0.9,
	resists = { [DamageType.NATURE] = 20, [DamageType.LIGHT] = -20 },
}
