-- Verified leaf and inherited base; source hashes in source-contracts.json
newEntity{ define_as = "CORRUPTED_DAELACH",
	type = "demon", subtype = "major", unique = true,
	name = "Corrupted Daelach",
	display = "U", color=colors.VIOLET,
	resolvers.nice_tile{image="invis.png", add_mos = {{image="npc/demon_major_corrupted_daelach.png", display_h=2, display_y=-1}}},
	desc = _t[[Shadow and flames. The huge beast of fire moves speedily toward you, its huge shadowy wings deployed.]],
	level_range = {40, nil}, exp_worth = 2,
	max_life = 250, life_rating = 25, fixed_rating = true,
	rank = 4,
	size_category = 5,
	infravision = 10,
	stats = { str=16, dex=12, cun=14, mag=25, con=16 },
	instakill_immune = 1,
	stun_immune = 1,
	no_breath = 1,
	move_others=true,
	demon = 1,
	invisible = 40,

	on_melee_hit = { [DamageType.FIRE] = 50, [DamageType.LIGHT] = 30, },

	body = { INVEN = 10, MAINHAND=1, OFFHAND=1, BODY=1 },
	resolvers.equip{
		{type="weapon", subtype="whip", defined="WHIP_URH_ROK", random_art_replace={chance=75}, autoreq=true},
	},
	resolvers.drops{chance=100, nb=5, {tome_drops="boss"} },

	resolvers.talents{
		[Talents.T_FIREBEAM]={base=5, every=7, max=7},
		[Talents.T_DARKNESS]=3,
		[Talents.T_FLAME]={base=5, every=7, max=7},
		[Talents.T_POISON_BREATH]={base=5, every=7, max=7},
		[Talents.T_FIRE_BREATH]={base=5, every=7, max=7},
		[Talents.T_GLOOM]={base=5, every=7, max=7},
		[Talents.T_RUSH]=5,
		[Talents.T_WEAPON_COMBAT]=5,
		[Talents.T_EXOTIC_WEAPONS_MASTERY]={base=3, every=10, max=6},
	},
	resolvers.sustains_at_birth(),

	autolevel = "dexmage",
	ai = "tactical", ai_state = { talent_in=2, ai_move="move_astar", },
	ai_tactic = resolvers.tactic"melee",
	resolvers.inscriptions(3, {}),
	resolvers.inscriptions(1, {"manasurge rune"}),

	on_die = function(self, who)
	end,
}
-- INHERITED BASE
