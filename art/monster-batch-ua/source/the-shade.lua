-- Verified leaf and inherited base; source hashes in source-contracts.json
newEntity{ define_as = "SHADE",
	allow_infinite_dungeon = true,
	type = "undead", subtype = "skeleton", unique = true,
	name = "The Shade",
	display = "s", color=colors.VIOLET,
	shader = "unique_glow",
	desc = _t[[This skeleton looks nasty. There are red flames in its empty eye sockets. It wields a nasty sword and strides toward you, throwing spells.]],
	killer_message = _t"and left to rot",
	level_range = {7, nil}, exp_worth = 2,
	max_life = 150, life_rating = 15, fixed_rating = true,
	max_mana = 85,
	max_stamina = 85,
	rank = 4,
	tier1 = true,
	size_category = 3,
	undead = 1,
	infravision = 10,
	stats = { str=16, dex=12, cun=14, mag=25, con=16 },
	instakill_immune = 1,
	blind_immune = 1,
	cut_immune = 1,
	move_others=true,
	combat_spellcrit = -20,
	body = { INVEN = 10, MAINHAND=1, OFFHAND=1, BODY=1 },
	equipment = resolvers.equip{ {type="weapon", subtype="staff", defined="STAFF_KOR", random_art_replace={chance=75}, autoreq=true}, {type="armor", subtype="light", forbid_power_source={antimagic=true}, autoreq=true}, },
	resolvers.drops{chance=100, nb=3, {tome_drops="boss"} },

	resolvers.talents{
		[Talents.T_MANATHRUST]=3, [Talents.T_FREEZE]=3, [Talents.T_TIDAL_WAVE]=2,
		[Talents.T_WEAPONS_MASTERY]=2,
	},
	resolvers.inscriptions(1, {"shielding rune", "phase door rune"}),
	resolvers.inscriptions(1, {"manasurge rune"}),
	inc_damage = {all=-40},

	autolevel = "warriormage",
	resolvers.auto_equip_filters("Archmage"),
	auto_classes={{class="Archmage", start_level=12, level_rate=75}},

	ai = "tactical", ai_state = { talent_in=3, ai_move="move_astar", },
	ai_tactic = resolvers.tactic"melee",

	-- Override the recalculated AI tactics to avoid problematic kiting in the early game
	-- In this case safe_range being set while talent_in is above 1 still results in a lot of kiting, so we lower the safe range too
	low_level_tactics_override = {escape=0, safe_range=1},

	on_die = function(self, who)
		game.state:activateBackupGuardian("KOR_FURY", 3, 35, _t".. yes I tell you! The old ruins of Kor'Pul are still haunted!")
		game.player:resolveSource():setQuestStatus("start-allied", engine.Quest.COMPLETED, "kor-pul")
	end,
}

-- INHERITED BASE
