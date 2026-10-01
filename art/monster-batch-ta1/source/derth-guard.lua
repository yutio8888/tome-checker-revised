-- Verified leaf and inherited base; source hashes in source-contracts.json
newEntity{ base = "BASE_NPC_DERTH_TOWN",
	name = "derth guard", color=colors.LIGHT_UMBER,
	desc = _t[[A stern-looking guard, he will not let you disturb the town.]],
	level_range = {1, nil}, exp_worth = 0,
	rarity = 3,
	max_life = resolvers.rngavg(70,80),
	resolvers.equip{
		{type="weapon", subtype="longsword", not_properties={"unique"}, autoreq=true},
		{type="armor", subtype="shield", not_properties={"unique"}, autoreq=true},
	},
	combat_armor = 2, combat_def = 0,
	resolvers.talents{ [Talents.T_RUSH]=1, [Talents.T_PERFECT_STRIKE]=1, },
}
-- INHERITED BASE
newEntity{
	define_as = "BASE_NPC_DERTH_TOWN",
	type = "humanoid", subtype = "human",
	display = "p", color=colors.WHITE,
	faction = "allied-kingdoms",
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
	resolvers.inscriptions(1, "infusion"),

	autolevel = "warrior",
	ai = "dumb_talented_simple", ai_state = { ai_move="move_complex", talent_in=3, },
	stats = { str=12, dex=8, mag=6, con=10 },

	emote_random = resolvers.emote_random{allow_backup_guardian=true},

	on_die = function(self)
		game.zone.unclean_derth_savior = true
	end,
}
