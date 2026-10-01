-- Verified leaf and inherited base; source hashes in source-contracts.json
newEntity{ base="BASE_NPC_ORC", define_as = "UKRUK",
	unique = true,
	name = "Ukruk the Fierce",
	faction = "orc-pride",
	color=colors.VIOLET,
	desc = _t[[This ugly orc looks really nasty and vicious. He is obviously looking for something and bears an unknown symbol on his shield.]],
	level_range = {30, nil}, exp_worth = 2,
	max_life = 1500, life_rating = 18, fixed_rating = true,
	rank = 4,
	size_category = 3,
	infravision = 10,
	move_others=true,

	instakill_immune = 1,
	stun_immune = 1,
	blind_immune = 1,
	combat_spellresist = 70,
	combat_mentalresist = 70,
	combat_physresist = 70,
	see_invisible = 38,

	resolvers.equip{
		{type="weapon", subtype="longsword", force_drop=true, tome_drops="boss", autoreq=true},
		{type="armor", subtype="shield", force_drop=true, tome_drops="boss", autoreq=true},
		{type="armor", subtype="massive", tome_drops="boss", autoreq=true, }

	},
	resolvers.drop_randart{},
	resolvers.drops{chance=100, nb=3, {tome_drops="boss"} },
	resolvers.drops{chance=100, nb=1, {defined="UKRUK_NOTE"} },

	resolvers.talents{
		[Talents.T_WEAPONS_MASTERY]=5, [Talents.T_ASSAULT]=5, [Talents.T_SHIELD_SLAM]=5, [Talents.T_RUSH]=5,
	},

	auto_classes={
		{class="Bulwark", start_level=30, level_rate=75},
	},

	autolevel = "warrior",
	ai = "tactical", ai_state = { talent_in=1, ai_move="move_astar", },
	ai_tactic = resolvers.tactic"melee",
	resolvers.inscriptions(6, {}),

	on_die = function(self, who)
		world:gainAchievement("KILL_UKRUK", game.player)
		local q = game.player:resolveSource():hasQuest("staff-absorption")
		if q then q:killed_ukruk(game.player:resolveSource()) end
	end,
}
-- INHERITED BASE
newEntity{
	define_as = "BASE_NPC_ORC",
	type = "humanoid", subtype = "orc",
	display = "o", color=colors.UMBER,
	faction = "orc-pride",

	combat = { dam=resolvers.rngavg(5,12), atk=2, apr=6, physspeed=2 },

	body = { INVEN = 10, MAINHAND=1, OFFHAND=1, BODY=1, QUIVER=1, TOOL=1 },
	resolvers.drops{chance=20, nb=1, {} },
	resolvers.drops{chance=10, nb=1, {type="money"} },
	infravision = 10,
	lite = 2,

	life_rating = 11,
	rank = 2,
	size_category = 3,

	open_door = true,

	autolevel = "warrior",
	ai = "dumb_talented_simple", ai_state = { ai_move="move_complex", talent_in=3, },
	stats = { str=20, dex=8, mag=6, con=16 },
	resolvers.talents{ [Talents.T_WEAPON_COMBAT]={base=1, every=10, max=5}, },
	ingredient_on_death = "ORC_HEART",
}
