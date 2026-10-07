-- Verified leaf and inherited base; source hashes in source-contracts.json
newEntity{ base = "BASE_NPC_ELVALA_TOWN",
	name = "shalore rune master", color=colors.RED,
	desc = _t[[A tall Elf, his skin covered in runes.]],
	level_range = {1, nil}, exp_worth = 0,
	rarity = 3,
	max_life = resolvers.rngavg(50,60),
	ai_state = { talent_in=1, },
	autolevel = "caster",
	resolvers.inscriptions(3, {"heat beam rune", "frozen spear rune", "acid wave rune", "lightning rune"}),
}
-- INHERITED BASE
newEntity{
	define_as = "BASE_NPC_ELVALA_TOWN",
	type = "humanoid", subtype = "shalore",
	display = "p", color=colors.WHITE,
	faction = "shalore",
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
