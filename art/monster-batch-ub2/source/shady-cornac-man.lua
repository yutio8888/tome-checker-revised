-- Verified leaf and inherited base; source hashes in source-contracts.json
newEntity{ base = "BASE_NPC_DERTH_TOWN",
	define_as ="ARENA_AGENT",
	name = "Shady cornac man", color=colors.DARK_BLUE, unique = true,
	level_range = {1, nil}, exp_worth = 0,
	can_talk = "arena-unlock",
	can_quest = true,
	never_move = 1,
	rarity = false,
	max_life = resolvers.rngavg(70,80),
	seen_by = function(self, who)
		if not game.party:hasMember(who) then return end
		self.seen_by = nil
		self:doEmote(_t"Hey you. Come here.", 60)
	end,
	on_die = false,
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
