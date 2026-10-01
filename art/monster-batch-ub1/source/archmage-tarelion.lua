-- Verified leaf and inherited base; source hashes in source-contracts.json
newEntity{ define_as = "TARELION",
	type = "humanoid", subtype = "shalore",
	display = "p",
	faction = "angolwen",
	name = "Archmage Tarelion", color=colors.CRIMSON, unique = true,
	resolvers.nice_tile{tall=true},
	desc = _t[[A tall Shalore in a flowing robe, he looks calm and at peace, but you can feel his tremendous power.]],
	level_range = {30, nil}, exp_worth = 2,
	rank = 4,
	size_category = 3,
	mana_regen = 120,
	max_mana = 2000,
	max_life = 350, life_rating = 24, fixed_rating = true,
	infravision = 10,
	stats = { str=10, dex=15, cun=42, mag=26, con=14 },
	instakill_immune = 1,
	teleport_immune = 1,
	move_others=true,
	combat_spellpower = 30,
	anger_emote = _t"Remove @himher@!",
	hates_antimagic = 1,

	open_door = true,

	autolevel = "caster",
	ai = "tactical", ai_state = { talent_in=1, ai_move="move_astar", },
	ai_tactic = resolvers.tactic"ranged",
	resolvers.inscriptions(3, "rune"),
	resolvers.inscriptions(1, {"manasurge rune"}),

	body = { INVEN = 10, MAINHAND=1, OFFHAND=1, BODY=1 },
	resolvers.drops{chance=100, nb=5, {tome_drops="boss"} },

	resolvers.equip{
		{type="weapon", subtype="staff", autoreq=true, forbid_power_source={antimagic=true}, tome_drops="store"},
		{type="armor", subtype="cloth", autoreq=true, forbid_power_source={antimagic=true}, tome_drops="store"},
	},

	resolvers.talents{
		[Talents.T_CRYSTALLINE_FOCUS]=5,
		[Talents.T_STRIKE]=5,
		[Talents.T_EARTHEN_MISSILES]=5,
		[Talents.T_EARTHQUAKE]=5,
		[Talents.T_BODY_OF_STONE]=5,
		[Talents.T_MANATHRUST]=5,
		[Talents.T_ARCANE_POWER]=5,
		[Talents.T_DISRUPTION_SHIELD]=5,
		[Talents.T_ESSENCE_OF_SPEED]=5,
		[Talents.T_PHASE_DOOR]=5,
		[Talents.T_TELEPORT]=5,
		[Talents.T_KEEN_SENSES]=5,
		[Talents.T_PREMONITION]=5,
	},
	resolvers.sustains_at_birth(),

	can_talk = "tarelion",
}
-- INHERITED BASE
