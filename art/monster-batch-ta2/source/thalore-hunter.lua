-- Verified leaf and inherited base; source hashes in source-contracts.json
newEntity{ base = "BASE_NPC_ELVALA_TOWN",
	name = "thalore hunter", color=colors.LIGHT_UMBER,
	desc = _t[[A stern-looking guard, he will not let you disturb the town.]],
	level_range = {1, nil}, exp_worth = 0,
	rarity = 3,
	max_life = resolvers.rngavg(70,80),
	resolvers.talents{
		[Talents.T_BOW_MASTERY]={base=1, every=10, max=5},
		[Talents.T_SHOOT]=1,
	},
	ai_state = { talent_in=1, },

	autolevel = "archer",
	resolvers.inscriptions(1, "infusion"),
	resolvers.equip{
		{type="weapon", subtype="longbow", not_properties={"unique"}, autoreq=true},
		{type="ammo", subtype="arrow", not_properties={"unique"}, autoreq=true},
	},
	resolvers.racial(),
}
-- INHERITED BASE
newEntity{
	define_as = "BASE_NPC_ELVALA_TOWN",
	type = "humanoid", subtype = "thalore",
	display = "p", color=colors.WHITE,
	faction = "thalore",
	anger_emote = _t"Catch @himher@!",
	exp_worth = 0,
	combat = { dam=resolvers.rngavg(1,2), atk=2, apr=0, dammod={str=0.4} },

	body = { INVEN = 10, MAINHAND=1, OFFHAND=1, BODY=1, QUIVER=1 },
	lite = 3,

	life_rating = 10,
	rank = 2,
	size_category = 3,

	open_door = true,

	resolvers.racial(),
	resolvers.inscriptions(1, "rune"),

	autolevel = "warrior",
	ai = "dumb_talented_simple", ai_state = { ai_move="move_complex", talent_in=3, },
	stats = { str=12, dex=8, mag=6, con=10 },

	emote_random = resolvers.emote_random{allow_backup_guardian=true},
}
