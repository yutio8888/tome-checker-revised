-- Verified leaf and inherited base; source hashes in source-contracts.json
newEntity{ base = "BASE_NPC_SUNWALL_TOWN",
	name = "human guard", color=colors.LIGHT_UMBER,
	desc = _t[[A stern-looking guard, he will not let you disturb the town.]],
	level_range = {1, nil}, exp_worth = 1,
	rarity = 1,
	max_life = resolvers.rngavg(70,80),
	resolvers.equip{
		{type="weapon", subtype="longsword", autoreq=true},
		{type="armor", subtype="shield", autoreq=true},
	},
	combat_armor = 2, combat_def = 0,
	resolvers.talents{
		[Talents.T_WEAPON_COMBAT]={base=1, every=10, max=6},
		[Talents.T_WEAPONS_MASTERY]={base=1, every=10, max=6},
		[Talents.T_RUSH]={start = 5, base=1, every = 10, max=5},
		[Talents.T_PERFECT_STRIKE]={start = 5, base=1, every = 10, max=5},
	},
}
-- INHERITED BASE
newEntity{
	define_as = "BASE_NPC_SUNWALL_TOWN",
	type = "humanoid", subtype = "human",
	display = "p", color=colors.WHITE,
	faction = "sunwall",

	combat = { dam=resolvers.rngavg(1,2), atk=2, apr=0, dammod={str=0.4} },

	body = { INVEN = 10, MAINHAND=1, OFFHAND=1, BODY=1, QUIVER=1 },
	resolvers.drops{chance=20, nb=1, {} },
	lite = 1,

	life_rating = 10,
	rank = 2,
	size_category = 3,

	open_door = true,

	autolevel = "warrior",
	ai = "dumb_talented_simple", ai_state = { ai_move="move_complex", talent_in=3, },
	stats = { str=12, dex=8, mag=6, con=10 },
}
