-- Verified leaf and inherited base; source hashes in source-contracts.json
newEntity{ define_as = "TANNEN",
	type = "humanoid", subtype = "human", unique = true,
	name = "Tannen",
	display = "p", color=colors.VIOLET,
	desc = _t[[The traitor has been revealed, and he does not intend to let you escape to tell the tale.]],
	killer_message = _t"and was neither found nor heard from again",
	level_range = {35, nil}, exp_worth = 2,
	max_life = 250, life_rating = 16, fixed_rating = true,
	max_mana = 850, mana_regen = 40,
	mana_regen = 15,
	rank = 4,
	size_category = 2,
	infravision = 10,
	stats = { str=10, dex=12, cun=14, mag=25, con=16 },

	instakill_immune = 1,
	blind_immune = 1,

	body = { INVEN = 10, MAINHAND=1, OFFHAND=1, BODY=1, QUIVER=1, },
	resolvers.auto_equip_filters("Alchemist"),
	equipment = resolvers.equip{
		{type="weapon", subtype="staff", force_drop=true, tome_drops="boss", forbid_power_source={antimagic=true}, autoreq=true},
		{type="armor", subtype="cloth", force_drop=true, tome_drops="boss", forbid_power_source={antimagic=true}, autoreq=true},
	},
	resolvers.drops{chance=100, nb=4, {tome_drops="boss"} },
	resolvers.drops{chance=100, nb=1, {defined="ORB_MANY_WAYS2"} },
	resolvers.drops{chance=100, nb=1, {defined="ATHAME_WEST2"} },
	resolvers.drops{chance=100, nb=1, {defined="NOTE4"} },

	resists = { [DamageType.ACID] = 100, },

	resolvers.talents{
		[Talents.T_THROW_BOMB]={base=4, every=6, max=9},
		[Talents.T_CHANNEL_STAFF]={base=5, every=5, max=9},
		[Talents.T_STAFF_MASTERY]={base=3, every=10, max=5},
		[Talents.T_ALCHEMIST_PROTECTION]={base=5, every=5, max=9},
		[Talents.T_SHOCKWAVE_BOMB]={base=4, every=6, max=9},
		[Talents.T_HEAT]={base=4, every=6, max=9},
		[Talents.T_BODY_OF_FIRE]={base=3, every=5, max=9},
		[Talents.T_ACID_INFUSION]={base=5, every=5, max=9},
		[Talents.T_STONE_TOUCH]={base=3, every=5, max=9},
	},

	resolvers.generic(function(self)
		-- Make and wield some alchemist gems
		local t = self:getTalentFromId(self.T_CREATE_ALCHEMIST_GEMS)
		local gem = t.make_gem(self, t, "GEM_BLOODSTONE")
		self:wearObject(gem, true, false)
	end),

	autolevel = "dexmage",
	ai = "tactical", ai_state = {ai_target="target_player_radius", sense_radius=400, talent_in=1, ai_move="move_astar" },
	ai_tactic = resolvers.tactic"ranged",
	resolvers.inscriptions(2, "infusion"),
	resolvers.inscriptions(1, "rune"),
	resolvers.inscriptions(1, {"manasurge rune"}),

	on_die = function(self, who)
		game.player:resolveSource():setQuestStatus("east-portal", engine.Quest.COMPLETED, "tannen-dead")
	end,
}
