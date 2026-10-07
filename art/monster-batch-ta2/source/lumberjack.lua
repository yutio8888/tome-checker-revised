-- Verified leaf and inherited base; source hashes in source-contracts.json
newEntity{ defined_as = "LUMBERJACK",
	type = "humanoid", subtype = "human",
	name = "lumberjack",
	display = "p", color=colors.UMBER, faction = "allied-kingdoms",
	desc = _t[[A lumberjack. Cutting wood is his job, dream and passion.]],
	level_range = {1, 1}, exp_worth = 1,
	rarity = 1,
	max_life = 100, life_rating = 10,
	stats = { str=20 },
	rank = 2,
	size_category = 3,
	infravision = 10,

	body = { INVEN = 10, MAINHAND=1, OFFHAND=1, BODY=1 },

	autolevel = "warrior",
	ai = "dumb_talented_simple", ai_state = { talent_in=2, ai_move="flee_dmap", },

	on_die = function(self, who)
		game.player:resolveSource():hasQuest("lumberjack-cursed"):lumberjack_dead()
	end,
}
