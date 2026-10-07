-- Verified leaf and inherited base; source hashes in source-contracts.json
newEntity{ base = "BASE_NPC_SUNWALL_TOWN",
	name = "elven sun-mage", subtype = "elf", color=colors.YELLOW,
	desc = _t[[An elf dressed in glowing robes.]],
	level_range = {3, nil}, exp_worth = 1,
	rarity = 3,
	rank = 3,
	ai = "tactical",
	ai_tactic = resolvers.tactic"ranged",
	max_life = resolvers.rngavg(70,80),
	resolvers.equip{
		{type="weapon", subtype="staff", forbid_power_source={antimagic=true}, autoreq=true},
		{type="armor", subtype="cloth", forbid_power_source={antimagic=true}, autoreq=true},
	},
	resolvers.talents{
		[Talents.T_STAFF_MASTERY]={base=1, every=10, max=5},
		[Talents.T_CHANT_OF_LIGHT]={base = 2, every = 7, max = 7},
		[Talents.T_SEARING_LIGHT]={base = 3, every = 8, max = 7},
		[Talents.T_FIREBEAM]={base = 2, every = 7, max = 7},
	},
	resolvers.sustains_at_birth(),
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
