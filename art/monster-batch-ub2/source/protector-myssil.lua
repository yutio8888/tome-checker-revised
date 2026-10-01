-- Verified leaf and inherited base; source hashes in source-contracts.json
newEntity{ base = "BASE_NPC_ZIGURANTH", define_as = "PROTECTOR_MYSSIL",
	name = "Protector Myssil", color=colors.VIOLET, unique = true,
	desc = _t[[A Halfling Ziguranth, clad in dark steel plates. She is the current leader of Zigur.]],
	female = true, subtype = "halfling",
	level_range = {30, nil}, exp_worth = 1,
	rank = 4,
	size_category = 2,
	stamina_regen = 40,
	no_breath = 1,
	max_life = resolvers.rngavg(300, 310), life_rating = 25,
	resolvers.equip{
		{type="weapon", subtype="greatsword", forbid_power_source={arcane=true}, autoreq=true},
		{type="armor", subtype="massive", forbid_power_source={arcane=true}, autoreq=true},
	},
	resolvers.drops{chance=100, nb=1, {unique=true} },
	resolvers.drops{chance=100, nb=4, {tome_drops="boss"} },

	combat_armor = 5, combat_def = 10,
	resolvers.talents{
		[Talents.T_ARMOUR_TRAINING]=6,
		[Talents.T_WEAPON_COMBAT]=2,
		[Talents.T_WEAPONS_MASTERY]=2,
		[Talents.T_RESOLVE]=5,
		[Talents.T_AURA_OF_SILENCE]=4,
		[Talents.T_ANTIMAGIC_SHIELD]=5,
		[Talents.T_MANA_CLASH]=4,
		[Talents.T_ICE_CLAW]=5,
		[Talents.T_LIGHTNING_SPEED]=5,
		[Talents.T_ICE_BREATH]=5,
		[Talents.T_ICY_SKIN]=5,
		[Talents.T_WAR_HOUND]=5,
		[Talents.T_MINOTAUR]=5,
		[Talents.T_SPIDER]=5,
		[Talents.T_DRACONIC_WILL]=1,
		[Talents.T_SPELL_FEEDBACK]=1,
		[Talents.T_UNBREAKABLE_WILL]=1,
		[Talents.T_TRICKY_DEFENSES]=1,
	},
	resolvers.sustains_at_birth(),

	can_talk = "myssil",

	ai = "tactical", ai_state = { talent_in=1, ai_move="move_astar", },
	ai_tactic = resolvers.tactic"melee",
	resolvers.inscriptions(4, "infusion"),

	on_die = function(self)
		local q = game.player:hasQuest("anti-antimagic")
		if q then q:myssil_dies() end
	end,
}
-- INHERITED BASE
newEntity{
	define_as = "BASE_NPC_ZIGURANTH",
	type = "humanoid", subtype = "human",
	display = "p", color=colors.UMBER,
	faction = "zigur",
	killer_message = _t"and burned on a pyre",

	combat = { dam=resolvers.rngavg(5,12), atk=2, apr=6, physspeed=2 },

	body = { INVEN = 10, MAINHAND=1, OFFHAND=1, BODY=1, QUIVER=1 },
	resolvers.drops{chance=20, nb=1, {} },
	infravision = 10,
	lite = 1,

	life_rating = 15,
	rank = 2,
	size_category = 3,

	open_door = true,

	resolvers.racial(),

	resolvers.talents{ [Talents.T_ARMOUR_TRAINING]=2, },
	resolvers.inscriptions(1, "infusion"),

	autolevel = "warrior",
	ai = "dumb_talented_simple", ai_state = { ai_move="move_complex", talent_in=3, },
	stats = { str=20, dex=15, mag=1, con=16, wil=19 },
	not_power_source = {arcane=true},
}
