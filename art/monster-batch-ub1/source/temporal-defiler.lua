-- Verified leaf and inherited base; source hashes in source-contracts.json
newEntity{ define_as = "TEMPORAL_DEFILER",
	type = "horror", subtype = "temporal", unique = true,
	name = "Temporal Defiler",
	display = "h", color=colors.VIOLET,
	resolvers.nice_tile{image="invis.png", add_mos = {{image="npc/horror_temporal_temporal_defiler.png", display_h=2, display_y=-1}}},
	desc = _t[[A huge, slender, metallic monstrosity with long claws in place of fingers, and razor-sharp teeth. It seems to seek something here.]],
	level_range = {50, nil}, exp_worth = 0.1,
	max_life = 1500, life_rating = 35, fixed_rating = true,
	stats = { str=20, dex=10, cun=8, mag=10, con=20 },
	rank = 4,
	size_category = 4,
	infravision = 10,
	instakill_immune = 1,
	move_others=true,

	global_speed_base = 1.2,
	autolevel = "rogue",
	ai = "dumb_talented_simple", ai_state = { ai_move="move_complex", talent_in=2, },
	combat_armor = 10, combat_def = 10,
	combat = { dam=resolvers.levelup(resolvers.rngavg(25,100), 1, 1.2), atk=resolvers.rngavg(25,100), apr=25, dammod={dex=1.1} },

	body = { INVEN = 10, MAINHAND=1, OFFHAND=1, BODY=1, TOOL=1 },
	resolvers.equip{{defined="TIME_SHARD"}, autoreq=true},
	resolvers.drops{chance=100, nb=3, {tome_drops="boss"} },

	inc_damage = {all = -30},

	resolvers.talents{
		[Talents.T_FATEWEAVER]={base=3, every=7, max=5},
		[Talents.T_SPIN_FATE]={base=3, every=7, max=5},
		[Talents.T_STEALTH]={base=1, every=7, max=5},
		[Talents.T_SHADOWSTRIKE]={base=1, every=7, max=5},
		[Talents.T_UNSEEN_ACTIONS]={base=1, every=7, max=5},
	},

	resolvers.inscriptions(1, "rune"),
	resolvers.inscriptions(1, "infusion"),

	resolvers.sustains_at_birth(),

	on_die = function(self, who)
		game.player:resolveSource():setQuestStatus("start-point-zero", engine.Quest.COMPLETED, "saved")
	end,
}
-- INHERITED BASE
