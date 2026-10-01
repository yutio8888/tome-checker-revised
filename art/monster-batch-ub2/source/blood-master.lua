-- Verified leaf and inherited base; source hashes in source-contracts.json
newEntity{ define_as = "RING_MASTER",
	type = "humanoid", subtype = "yaech", unique = true,
	name = "Blood Master",
	display = "@", color=colors.VIOLET,
	blood_color = colors.BLUE,
	desc = _t[[This small humanoid is covered in silky white fur. Its bulging eyes stare deep into your mind.]],
	level_range = {14, nil}, exp_worth = 2,
	max_life = 150, life_rating = 12, fixed_rating = true,
	rank = 3.5,
	size_category = 2,
	infravision = 10,
	stats = { str=16, dex=12, cun=14, wil=25, con=16 },
	instakill_immune = 1,
	move_others=true,
	psi_regen = 4,

	body = { INVEN = 10, MAINHAND=1, OFFHAND=1, BODY=1, PSIONIC_FOCUS = 1, QS_PSIONIC_FOCUS = 1 },
	resolvers.equip{ {type="weapon", subtype="greatsword", auto_req=true}, {type="armor", subtype="light", autoreq=true}, },
	resolvers.drops{chance=100, nb=3, {tome_drops="boss"} },

	resolvers.inventory{ inven="PSIONIC_FOCUS",
		{type="weapon", subtype="greatsword", autoreq=true},
	},
	resolvers.talents{
		[Talents.T_UNITY]={base=7, every=4, max=10},
		[Talents.T_QUICKENED]={base=3, every=2, max=6},
		[Talents.T_WAYIST]={base=3, every=4, max=5},
		[Talents.T_MINDHOOK]={base=3, every=7, max=5},
		[Talents.T_TELEKINETIC_LEAP]={base=3, every=7, max=5},
		[Talents.T_KINETIC_AURA]={base=3, every=7, max=5},
		[Talents.T_CHARGED_AURA]={base=3, every=7, max=5},
		[Talents.T_KINETIC_SHIELD]={base=3, every=7, max=5},
		[Talents.T_KINETIC_LEECH]={base=5, every=7, max=7},
		[Talents.T_TELEKINETIC_SMASH]={base=5, every=7, max=8},
		[Talents.T_AUGMENTATION]={base=3, every=7, max=5},
		[Talents.T_WEAPONS_MASTERY]={base=4, every=3, max=10},
		[Talents.T_WEAPON_COMBAT]={base=4, every=3, max=10},
	},

	resolvers.inscriptions(2, {"shielding rune", "speed rune"}),

	autolevel = "warriorwill",
	auto_classes={{class="Mindslayer", start_level=22, level_rate=35}},
	ai = "tactical", ai_state = { talent_in=1, ai_move="move_astar", },

	on_die = function(self, who)
		game.player:setQuestStatus("ring-of-blood", engine.Quest.COMPLETED, "killall")
		game.player:setQuestStatus("ring-of-blood", engine.Quest.COMPLETED)
	end,

	faction = "slavers",
	can_talk = "ring-of-blood-master",
}


----------------------------------- Spectators
