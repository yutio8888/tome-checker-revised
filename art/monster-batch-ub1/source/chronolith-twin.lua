-- Verified leaf and inherited base; source hashes in source-contracts.json
newEntity{ base="BASE_NPC_HORROR_TEMPORAL", define_as = "CHRONOLITH_TWIN",
	name = "Chronolith Twin", color=colors.VIOLET, unique = true,
	subtype = "temporal",
	resolvers.nice_tile{image="invis.png", add_mos = {{image="npc/horror_temporal_cronolith_twin.png", display_h=2, display_y=-1}}},
	desc = _t[[A six-armed creature, dressed in robes, with black insectile eyes.]],
	level_range = {20, nil}, exp_worth = 1,
	max_life = 150, life_rating = 15, fixed_rating = true,
	rank = 4,
	size_category = 3,
	stats = { str=10, dex=12, cun=14, mag=25, wil=25, con=16 },

	instakill_immune = 1,
	blind_immune = 0.5,
	silence_immune = 0.5,

	body = { INVEN = 10, MAINHAND=1, OFFHAND=1, BODY=1 },
	equipment = resolvers.equip{
		{type="weapon", subtype="staff", force_drop=true, tome_drops="boss", forbid_power_source={antimagic=true}, autoreq=true},
		{type="armor", subtype="cloth", force_drop=true, tome_drops="boss", forbid_power_source={antimagic=true}, autoreq=true},
	},
	resolvers.drops{chance=100, nb=2, {tome_drops="boss"} },
	resolvers.drops{chance=100, nb=1, {unique=true} },

	resists = { [DamageType.PHYSICAL] = 50, },

	resolvers.talents{
		[Talents.T_STAFF_MASTERY]= {base=2, every=8, max=5},
		[Talents.T_REPULSION_BLAST]={base=3, every=10, max=6},
		[Talents.T_GRAVITY_SPIKE]={base=3, every=10, max=6},
		[Talents.T_GRAVITY_WELL]={base=3, every=10, max=6},
		[Talents.T_GRAVITY_LOCUS]={base=3, every=10, max=6},
	},

	autolevel = "warriormage",
	ai = "tactical", ai_state = { talent_in=1, ai_move="move_astar", },
	ai_tactic = resolvers.tactic "ranged",
	resolvers.inscriptions(1, {"shielding rune"}),

	onTakeHit = twin_take_hit,

	on_die = function(self, who)
		self.brother = nil
		game.player:resolveSource():setQuestStatus("temporal-rift", engine.Quest.COMPLETED, "twin")
	end,
}
-- INHERITED BASE
newEntity{
	define_as = "BASE_NPC_HORROR_TEMPORAL",
	type = "horror", subtype = "temporal",
	display = "h", color=colors.WHITE,
	blood_color = colors.BLUE,
	body = { INVEN = 10 },
	autolevel = "warrior",
	ai = "dumb_talented_simple", ai_state = { ai_move="move_complex", talent_in=3, },

	stats = { str=20, dex=20, wil=20, mag=20, con=20, cun=20 },
	combat_armor = 5, combat_def = 10,
	combat = { dam=5, atk=10, apr=5, dammod={str=0.6} },
	infravision = 10,
	max_life = resolvers.rngavg(10,20),
	rank = 2,
	size_category = 3,

	no_breath = 1,
	cut_immune = 1,
	fear_immune = 1,
	not_power_source = {nature=true},
}

-- temporal horrors
