-- Verified leaf and inherited base; source hashes in source-contracts.json
newEntity{ base = "BASE_NPC_IRKKK_TOWN",
	name = "yeek mindslayer", color=colors.LIGHT_UMBER,
	resolvers.nice_tile{image="invis.png", add_mos = {{image="npc/humanoid_yeek_yeek_mindslayer.png", display_h=2, display_y=-1}}},
	desc = _t[[A mindslayer in training.]],
	level_range = {1, nil}, exp_worth = 0,
	rarity = 3,
	max_life = resolvers.rngavg(70,80),
	resolvers.equip{
		{type="weapon", subtype="greatsword", not_properties={"unique"}, autoreq=true},
	},
	combat_armor = 2, combat_def = 0,
	resolvers.talents{
		[Talents.T_KINETIC_AURA]={base=1, every=7, max=5},
		[Talents.T_CHARGED_AURA]={base=1, every=7, max=5},
		[Talents.T_KINETIC_SHIELD]={base=2, every=7, max=5},
		[Talents.T_EXOTIC_WEAPONS_MASTERY]={base=1, every=10, max=5},
	},
}
-- INHERITED BASE
newEntity{
	define_as = "BASE_NPC_IRKKK_TOWN",
	type = "humanoid", subtype = "yeek",
	display = "p", color=colors.WHITE,
	faction = "the-way",
	anger_emote = _t"Catch @himher@!",
	exp_worth = 0,
	combat = { dam=resolvers.rngavg(1,2), atk=2, apr=0, dammod={str=0.4} },

	body = { INVEN = 10, MAINHAND=1, OFFHAND=1, BODY=1, QUIVER=1, PSIONIC_FOCUS=1 },
	lite = 3,

	life_rating = 10,
	rank = 2,
	size_category = 2,

	open_door = true,

	resolvers.racial(),
	resolvers.inscriptions(1, "infusion"),

	autolevel = "wildcaster",
	ai = "dumb_talented_simple", ai_state = { ai_move="move_complex", talent_in=3, },
	stats = { str=7, dex=8, mag=6, wil=15, con=10 },

	emote_random = resolvers.emote_random{allow_backup_guardian=true},
}
