-- Verified leaf and inherited base; source hashes in source-contracts.json
newEntity{ base = "BASE_NPC_MAJOR_DEMON",
	name = "Khulmanar, General of Urh'Rok",
	color=colors.DARK_RED, unique=true,
	resolvers.nice_tile{image="invis.png", add_mos = {{image="npc/demon_major_general_of_urh_rok.png", display_h=2, display_y=-1}}},
	desc = _t[[This massive form, sheathed in dark flames, stands tall above a legion of lesser demons. In his hands he holds a massive blackened battleaxe, flames dancing around the blades.]],
	level_range = {40, nil}, exp_worth = 1,
	rarity = 50,
	rank = 3.5,
	global_speed_base = 1,
	size_category = 5,
	autolevel = "warriormage",
	life_rating = 35,
	combat_armor = 50, combat_def = 40, combat_atk=50,
	mana_regen = 100, stamina_regen = 100,

	ai = "tactical",

	resolvers.auto_equip_filters{MAINHAND = {properties = {"twohanded"}}, },
	resolvers.equip{ {type="weapon", subtype="battleaxe", defined="KHULMANAR_WRATH", random_art_replace={chance=30}, autoreq=true, force_drop=true}, },

	resists={[DamageType.PHYSICAL] = resolvers.mbonus(8, 8), [DamageType.FIRE] = 100},
	on_melee_hit = {[DamageType.FIRE]=resolvers.mbonus(25, 25)},
	melee_project = {[DamageType.FIRE]=resolvers.mbonus(25, 35)},

	knockback_immune = 1,

	summon = {
		{type="demon", number=2, hasxp=false},
	},
	make_escort = {
		{type="demon", no_subescort=true, number=resolvers.mbonus(4, 4)},
	},

	resolvers.talents{
		[Talents.T_SUMMON]=1,
			--Melee
		[Talents.T_WEAPON_COMBAT]={base=8, every=5, max=12},
		[Talents.T_WEAPONS_MASTERY]={base=8, every=8, max=12},
		[Talents.T_RUSH]={base=5, every=7, max=8},
		[Talents.T_BATTLE_CRY]={base=4, every=5, max=9},
		[Talents.T_BATTLE_CALL]={base=2, every=3, max=8},
		[Talents.T_STUNNING_BLOW]={base=5, every=8, max=7},
		[Talents.T_KNOCKBACK]={base=4, every=4, max=8},
			--Magic
		[Talents.T_FIRE_STORM]={base=4, every=6, max=8},
		[Talents.T_WILDFIRE]={base=3, every=8, max=6},
		[Talents.T_FLAME]={base=5, every=8, max=10},
			--Special
		[Talents.T_INFERNAL_BREATH]={base=3, every=5, max=7},

		[Talents.T_ELEMENTAL_SURGE]=1,
		[Talents.T_SPELL_FEEDBACK]=1,
	},
	resolvers.sustains_at_birth(),
	resolvers.drops{chance=100, nb=3, {tome_drops="boss"} },
}
-- INHERITED BASE
newEntity{
	define_as = "BASE_NPC_MAJOR_DEMON",
	type = "demon", subtype = "major",
	display = "U", color=colors.WHITE,
	blood_color = colors.GREEN,
	faction = "fearscape",
	body = { INVEN = 10 },
	autolevel = "warrior",
	ai = "dumb_talented_simple", ai_state = { ai_move="move_complex", talent_in=1, },
	stats = { str=22, dex=10, mag=20, con=13 },
	combat_armor = 1, combat_def = 1,
	body = { INVEN = 10, MAINHAND=1, OFFHAND=1, BODY=1, QUIVER=1 },
	combat = { dam=resolvers.mbonus(46, 20), atk=15, apr=7, dammod={str=0.7} },
	max_life = resolvers.rngavg(100,120),
	infravision = 10,
	open_door = true,
	rank = 2,
	size_category = 3,
	no_breath = 1,
	demon = 1,
	random_name_def = "demon",

	resolvers.inscriptions(1, "rune"),
	ingredient_on_death = "GREATER_DEMON_BILE",
}
