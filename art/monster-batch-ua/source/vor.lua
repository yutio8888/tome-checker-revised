-- Verified leaf and inherited base; source hashes in source-contracts.json
newEntity{ base="BASE_NPC_ORC_VOR", define_as = "VOR",
	allow_infinite_dungeon = true,
	name = "Vor, Grand Geomancer of the Pride", color=colors.VIOLET, unique = true,
	desc = _t[[An old orc, wearing multi-colored robes. Ice shards fly around him, leaving a trail of fire and lightning bursts.]],
	killer_message = _t"and used as target practice for initiate mages",
	level_range = {40, nil}, exp_worth = 1,
	rank = 5,
	max_life = 250, life_rating = 19, fixed_rating = true,
	infravision = 10,
	stats = { str=12, dex=10, cun=12, mag=21, con=14 },
	move_others=true,

	combat_armor = 10, combat_def = 10,

	open_door = true,

	autolevel = "caster",
	ai = "tactical", ai_state = { talent_in=1, ai_move="move_astar", },
	ai_tactic = resolvers.tactic"ranged",
	resolvers.inscriptions(1, {"manasurge rune"}),
	resolvers.inscriptions(4, "rune"),
	max_inscriptions = 5,

	body = { INVEN = 20, MAINHAND=1, OFFHAND=1, BODY=1, HEAD=1, TOOL=1 },

	resolvers.equip{
		{type="weapon", subtype="staff", force_drop=true, tome_drops="boss", forbid_power_source={antimagic=true}, autoreq=true},
		{type="armor", subtype="cloth", force_drop=true, tome_drops="boss", forbid_power_source={antimagic=true}, autoreq=true},
		{type="armor", subtype="head", defined="CROWN_ELEMENTS", random_art_replace={chance=75}, autoreq=true},
		{type="charm", subtype="wand"}
	},
	resolvers.drops{chance=100, nb=1, {defined="ORB_ELEMENTS"} },
	resolvers.drops{chance=20, nb=1, {defined="JEWELER_TOME"} },
	resolvers.drops{chance=100, nb=1, {defined="NOTE_LORE"} },
	resolvers.drops{chance=100, nb=5, {tome_drops="boss"} },

	inc_damage = {all=15},

	resolvers.talents{
		[Talents.T_FLAME]={base=5, every=7, max=7},
		[Talents.T_FLAMESHOCK]={base=5, every=7, max=7},
		[Talents.T_FIREFLASH]={base=5, every=7, max=7},
		[Talents.T_INFERNO]={base=5, every=7, max=7},
		[Talents.T_BLASTWAVE]={base=5, every=7, max=7},
		[Talents.T_CLEANSING_FLAMES]={base=5, every=7, max=7},
		[Talents.T_BURNING_WAKE]={base=5, every=7, max=7},

		[Talents.T_FREEZE]={base=5, every=7, max=7},
		[Talents.T_ICE_STORM]={base=5, every=7, max=7},
		[Talents.T_TIDAL_WAVE]={base=5, every=7, max=7},
		[Talents.T_ICE_SHARDS]={base=5, every=7, max=7},
		[Talents.T_FROZEN_GROUND]={base=5, every=7, max=7},

		[Talents.T_LIGHTNING]={base=5, every=7, max=7},
		[Talents.T_CHAIN_LIGHTNING]={base=5, every=7, max=7},

		[Talents.T_SPELLCRAFT]={base=5, every=7, max=7},
		[Talents.T_ESSENCE_OF_SPEED]={base=1, every=6, max=7},
		[Talents.T_PHASE_DOOR]={base=2, every=6, max=5},
		[Talents.T_STAFF_MASTERY]={base=3, every=8, max=5},

		[Talents.T_METEORIC_CRASH]=1,
	},

	resolvers.auto_equip_filters("Archmage"),
	auto_classes={
		{class="Archmage", start_level=40, level_rate=100,
			max_talent_types = 1,  -- Don't waste points on extra elemental trees or learn 20000 sustains
			banned_talents = {
				T_INVISIBILITY=true,  -- Reduces damage dramatically, basically a nerf
				T_PROBABILITY_TRAVEL=true,  -- Does this even work on AI?  Possibly should kill this on all NPCs
				T_DISRUPTION_SHIELD=true,  -- Stupid scaling with infinite mana
			},
		},
	},

	resolvers.sustains_at_birth(),

	on_die = function(self, who)
		game.player:resolveSource():setQuestStatus("orc-pride", engine.Quest.COMPLETED, "vor")
		if not game.player:hasQuest("pre-charred-scar") then
			game.player:grantQuest("pre-charred-scar")
		end
	end,
}
-- INHERITED BASE
newEntity{
	define_as = "BASE_NPC_ORC_VOR",
	type = "humanoid", subtype = "orc",
	display = "o", color=colors.RED,
	faction = "orc-pride", pride = "vor",

	combat = { dam=resolvers.rngavg(5,12), atk=2, apr=6, physspeed=2 },

	body = { INVEN = 10, MAINHAND=1, OFFHAND=1, BODY=1, QUIVER=1, TOOL=1 },
	resolvers.drops{chance=20, nb=1, {} },
	resolvers.drops{chance=10, nb=1, {type="money"} },
	resolvers.auto_equip_filters("Archmage"),
	infravision = 10,
	lite = 1,

	max_mana = 400,
	life_rating = 11,
	rank = 2,
	size_category = 3,

	open_door = true,

	resolvers.racial(),

	resolvers.inscriptions(2, "rune"),

	autolevel = "caster",
	ai = "dumb_talented_simple", ai_state = { ai_move="move_complex", talent_in=1, },
	stats = { str=10, dex=8, mag=20, con=16 },
	ingredient_on_death = "ORC_HEART",
}
