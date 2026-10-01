-- Verified leaf and inherited base; source hashes in source-contracts.json
newEntity{ base = "BASE_NPC_SLAVER",
	name = "enthralled slave", color=colors.KHAKI,
	subtype = "human",
	desc = _t[[A slave.]],
	level_range = {10, nil}, exp_worth = 0,
	rarity = 20,
	max_life = resolvers.rngavg(80,90), life_rating = 13,
	combat_armor = 0, combat_def = 6,

	resolvers.equip{
		{type="armor", subtype="hands", autoreq=true},
	},

	resolvers.talents{
		[Talents.T_DOUBLE_STRIKE] = {base=3, every=5, max=6},
		[Talents.T_UPPERCUT] = {base=3, every=5, max=6},
		[Talents.T_EMPTY_HAND] = 1,
		[Talents.T_CLINCH] = {base=3, every=5, max=6},
		[Talents.T_MAIM] = {base=3, every=5, max=6},
		[Talents.T_UNARMED_MASTERY] = {base=2, every=6, max=4},
		[Talents.T_WEAPON_COMBAT] = {base=2, every=6, max=4},
	},
}
-- INHERITED BASE
newEntity{
	define_as = "BASE_NPC_SLAVER",
	type = "humanoid", subtype = "human",
	display = "p", color=colors.DARK_KHAKI,
--	faction = "slavers",

	combat = { dam=resolvers.rngavg(5,12), atk=2, apr=6, physspeed=2 },

	body = { INVEN = 10, MAINHAND=1, OFFHAND=1, BODY=1, QUIVER=1, HANDS = 1 },
	resolvers.drops{chance=20, nb=1, {} },
	resolvers.drops{chance=10, nb=1, {type="money"} },
	infravision = 10,
	lite = 1,

	life_rating = 15,
	rank = 2,
	size_category = 3,

	open_door = true,

	resolvers.racial(),
	resolvers.talents{ [Talents.T_ARMOUR_TRAINING]=2, [Talents.T_WEAPON_COMBAT]={base=1, every=10, max=5}, [Talents.T_WEAPONS_MASTERY]={base=1, every=10, max=5} },

	autolevel = "warrior",
	ai = "dumb_talented_simple", ai_state = { ai_move="move_complex", talent_in=3, },
	stats = { str=20, dex=8, mag=6, con=16 },
}
