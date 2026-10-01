-- Verified leaf and inherited base; source hashes in source-contracts.json
newEntity{ base = "BASE_NPC_ANGOLWEN_TOWN",
	name = "cryomancer", color=colors.LIGHT_BLUE,
	resolvers.nice_tile{image="invis.png", add_mos = {{image="npc/humanoid_human_cryomancer.png", display_h=2, display_y=-1}}},
	desc = _t[[An archmage specializing in ice magic.]],
	level_range = {1, nil}, exp_worth = 0,
	rarity = 3,
	max_life = resolvers.rngavg(70,80),
	resolvers.equip{
		{type="weapon", subtype="staff", forbid_power_source={antimagic=true}, not_properties={"unique"}, autoreq=true},
		{type="armor", subtype="cloth", forbid_power_source={antimagic=true}, not_properties={"unique"}, autoreq=true},
	},
	combat_armor = 2, combat_def = 0,
	resolvers.talents{ [Talents.T_ICE_SHARDS]=3, [Talents.T_UTTERCOLD]=3, [Talents.T_FREEZE]=3, [Talents.T_FROZEN_GROUND]=3, },
}
-- INHERITED BASE
newEntity{
	define_as = "BASE_NPC_ANGOLWEN_TOWN",
	type = "humanoid", subtype = "human",
	display = "p", color=colors.WHITE,
	faction = "angolwen",
	anger_emote = _t"Catch @himher@!",
	hates_antimagic = 1,
	exp_worth = 0,
	resolvers.racial(),

	combat = { dam=resolvers.rngavg(1,2), atk=2, apr=0, dammod={str=0.4} },

	body = { INVEN = 10, MAINHAND=1, OFFHAND=1, BODY=1, QUIVER=1 },
	lite = 3,

	life_rating = 11,
	rank = 2,
	size_category = 3,

	open_door = true,

	autolevel = "caster",
	ai = "dumb_talented_simple", ai_state = { ai_move="move_complex", talent_in=3, },
	stats = { str=8, dex=8, mag=16, wil=18, con=10 },

	emote_random = resolvers.emote_random{allow_backup_guardian=true},
}
