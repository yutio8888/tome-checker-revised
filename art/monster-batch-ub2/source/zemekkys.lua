-- Verified leaf and inherited base; source hashes in source-contracts.json
newEntity{ base = "BASE_NPC_POINT_ZERO_TOWN", define_as = "ZEMEKKYS",
	name = "Zemekkys, Grand Keeper of Reality", color=colors.VIOLET, unique = true,
	image = "npc/humanoid_elf_high_chronomancer_zemekkys.png",
	subtype = "shalore",
	desc = _t[[A timeless elf stands before you. Even though his age is impossible to determine, you feel he has seen many things.]],
	level_range = {50, nil}, exp_worth = 1,
	rarity = false,
	max_life = 2000, life_rating = 20,
	life_regen = 50,
	paradox_regen = -10,
	never_move = 1,
	cant_be_moved = 1,

	faction = "keepers-of-reality",

	can_talk = "point-zero-zemekkys",

	ai = "tactical", ai_state = { talent_in=1, ai_move="move_astar", },
	ai_tactic = resolvers.tactic"ranged",
	resolvers.inscriptions(5, {}),
	resolvers.inscriptions(1, "rune"),

	body = { INVEN = 10, MAINHAND=1, OFFHAND=1, BODY=1 },
	resolvers.drops{chance=100, nb=5, {tome_drops="boss"} },

	combat_spellcrit = 70,
	combat_spellpower = 60,
	inc_damage = {all=80},

	resists = {[DamageType.TEMPORAL]=100},

	combat_spellresist = 250,
	combat_mentalresist = 250,
	combat_physresist = 250,

	resolvers.equip{
		{type="weapon", subtype="staff", autoreq=true, forbid_power_source={antimagic=true}, tome_drops="boss"},
		{type="armor", subtype="cloth", autoreq=true, forbid_power_source={antimagic=true}, tome_drops="boss"},
	},

	talent_cd_reduction = {all=23},
	resolvers.talents{
		[Talents.T_TEMPORAL_FORM]=1,
		[Talents.T_DRACONIC_BODY]=1,
		[Talents.T_LUCKY_DAY]=1,
		[Talents.T_ENDLESS_WOES]=1,
		[Talents.T_EYE_OF_THE_TIGER]=1,

		[Talents.T_RETHREAD]=5,
		[Talents.T_TEMPORAL_FUGUE]=5,

		[Talents.T_SPACETIME_STABILITY]=5,
		[Talents.T_STOP]=5,
		[Talents.T_CHRONO_TIME_SHIELD]=5,
		[Talents.T_STATIC_HISTORY]=5,

		[Talents.T_CELERITY]=5,
		[Talents.T_TIME_DILATION]=5,
		[Talents.T_HASTE]=5,

		[Talents.T_REPULSION_BLAST]=5,
		[Talents.T_GRAVITY_SPIKE]=5,
		[Talents.T_GRAVITY_LOCUS]=5,
		[Talents.T_GRAVITY_WELL]=5,

		[Talents.T_ENTROPY]=5,
		[Talents.T_ENERGY_ABSORPTION]=5,
		[Talents.T_REDUX]=5,
	},
	resolvers.sustains_at_birth(),
}
-- INHERITED BASE
newEntity{
	define_as = "BASE_NPC_POINT_ZERO_TOWN",
	type = "humanoid", subtype = "human",
	display = "p", color=colors.WHITE,
	faction = "point-zero-guardians",
	anger_emote = _t"Catch @himher@!",
	hates_antimagic = 1,
	never_anger = 1,

	combat = { dam=resolvers.rngavg(1,2), atk=2, apr=0, dammod={str=0.4} },

	body = { INVEN = 10, MAINHAND=1, OFFHAND=1, BODY=1, QUIVER=1 },
	lite = 3,

	life_rating = 10,
	rank = 2,
	size_category = 3,

	open_door = true,

	resolvers.racial(),

	autolevel = "caster",
	ai = "dumb_talented_simple", ai_state = { ai_move="move_complex", talent_in=3, },
	stats = { str=12, dex=8, mag=6, con=10 },
}
