-- Verified leaf and inherited base; source hashes in source-contracts.json
newEntity{ define_as = "LIMMIR",
	type = "humanoid", subtype = "elf",
	display = "p",
	faction = "sunwall",
	name = "Limmir the Jeweler", color=colors.RED, unique = true,
	desc = _t[[An Elven Anorithil, specializing in the art of jewelry.]],
	level_range = {50, 50}, exp_worth = 2,
	rank = 3,
	size_category = 3,
	max_life = 150, life_rating = 17, fixed_rating = true,
	infravision = 10,
	stats = { str=15, dex=10, cun=12, mag=16, con=14 },
	move_others=true,
	knockback_immune = 1,
	teleport_immune = 1,

	open_door = true,

	resists = { all = 40 },

	autolevel = "caster",
	ai = "move_quest_limmir", ai_state = { },

	body = { INVEN = 10, MAINHAND=1, OFFHAND=1, BODY=1 },

	resolvers.talents{
		[Talents.T_CHANT_OF_LIGHT]=5,
		[Talents.T_HYMN_OF_SHADOWS]=5,
	},
	resolvers.sustains_at_birth(),

	can_talk = "limmir-valley-moon",
	never_anger = true,
	can_craft = true,
	on_die = function(self, who)
		game.level.turn_counter = nil
		game.player:hasQuest("master-jeweler"):ritual_end()
	end,

	on_takehit = function(self, value, who)
		if (self.last_took_hit_cry and game.turn < self.last_took_hit_cry + 100 and (not who or who.type ~= "demon")) or not game.level.turn_counter then return value end
		self.last_took_hit_cry = game.turn

		game.bignews:say(90, "#VIOLET#Limmir is attacked! Defend him!")

		return value
	end,
}
