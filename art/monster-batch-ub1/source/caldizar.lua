-- Verified leaf and inherited base; source hashes in source-contracts.json
newEntity{ base = "BASE_NPC_SHERTUL", define_as = "CALDIZAR",
	name = "Caldizar", color=colors.LIGHT_RED, unique="Caldizar Unknown Fortress",
	resolvers.nice_tile{image="invis.png", add_mos = {{image="npc/horror_sher_tul_caldizar.png", display_h=2, display_y=-1}}},
	desc =_t"A creature stands before you, with long tentacle-like appendages and a squat bump in place of a head. An intense aura of power radiates from this being unlike anything you've ever felt before. It can only be a Sher'Tul. A living Sher'Tul!",
	level_range = {1000, nil}, exp_worth = 5,
	life_rating = 40,
	rank = 11,
	size_category = 4,
	faction = "sher'tul",
	autolevel = "caster",
	combat_armor = 1, combat_def = 0,
	combat = {dam=resolvers.levelup(resolvers.mbonus(25, 15), 1, 1.1), apr=0, atk=resolvers.mbonus(30, 15), dammod={mag=0.6}},

	never_move = 1,
	invulnerable = 1,

	resists = {all = 70},
	can_talk = "shertul-fortress-caldizar",

	seen_by = function(self, who)
		if not game.party:hasMember(who) or not who.player then return end
		self.seen_by = nil
		local chat = require("engine.Chat").new(self.can_talk, self, who, {player=who})
		local d = chat:invoke()
		local level = game.level
		d.innerDisplay = function(d, x, y, nb_keyframes)
			if level == game.level and who.life >= who.max_life * 0.1 then
				who:takeHit(who.max_life * 0.01 * nb_keyframes * 0.5, self)
				if who.updateMainShader then who:updateMainShader() end
			end
		end
	end
}
-- INHERITED BASE
newEntity{
	define_as = "BASE_NPC_SHERTUL",
	type = "horror", subtype = "sher'tul",
	display = "h", color=colors.WHITE,
	blood_color = colors.BLUE,
	body = { INVEN = 10 },
	autolevel = "caster",
	ai = "tactical", ai_state = { ai_move="move_complex",  },

	stats = { str=40, dex=40, wil=40, con=40, mag=40, cun=40, lck=100 },
	combat_armor = 0, combat_def = 0,
	combat = { dam=5, atk=15, apr=7, dammod={str=0.6} },
	infravision = 10,
	max_life = resolvers.rngavg(500,600),
	rank = 3,
	size_category = 3,

	no_breath = 1,
	fear_immune = 1,
}
