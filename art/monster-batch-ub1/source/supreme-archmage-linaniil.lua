-- Verified leaf and inherited base; source hashes in source-contracts.json
newEntity{ define_as = "SUPREME_ARCHMAGE_LINANIIL",
	type = "humanoid", subtype = "human",
	display = "p",
	faction = "angolwen",
	name = "Linaniil, Supreme Archmage of Angolwen", color=colors.VIOLET, unique = true,
	resolvers.nice_tile{image="invis.png", add_mos = {{image="npc/humanoid_human_linaniil_supreme_archmage.png", display_h=2, display_y=-1}}},
	desc = _t[[A tall, pale woman dressed in a revealing silk robe. Her gaze is so intense it seems to burn.]],
	level_range = {50, nil}, exp_worth = 2,
	rank = 4,
	size_category = 3,
	female = true,
	mana_regen = 120,
	max_mana = 20000,
	max_life = 750, life_rating = 34, fixed_rating = true,
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
	--ai_tactic = resolvers.tactic"ranged",
	resolvers.inscriptions(5, {}),
	resolvers.inscriptions(1, {"manasurge rune"}),

	body = { INVEN = 10, MAINHAND=1, OFFHAND=1, BODY=1 },
	resolvers.drops{chance=100, nb=5, {tome_drops="boss"} },

	combat_spellcrit = 70,
	combat_spellpower = 60,
	inc_damage = {all=80},

	resists = {[DamageType.ARCANE]=100},

	combat_spellresist = 250,
	combat_mentalresist = 250,
	combat_physresist = 250,

	resolvers.equip{
		{type="weapon", subtype="staff", autoreq=true, forbid_power_source={antimagic=true}, tome_drops="boss"},
		{type="armor", subtype="cloth", autoreq=true, forbid_power_source={antimagic=true}, tome_drops="boss"},
	},

	talent_cd_reduction = {
		all=23,
		[Talents.T_DRACONIC_BODY] = -20,
	},
	resolvers.talents{
		[Talents.T_AETHER_PERMEATION]=1,
		[Talents.T_DRACONIC_BODY]=1,
		[Talents.T_METEORIC_CRASH]=1,
		[Talents.T_LUCKY_DAY]=1,
		[Talents.T_ELEMENTAL_SURGE]=1,
		[Talents.T_EYE_OF_THE_TIGER]=1,
		[Talents.T_WILDFIRE]=5,
		[Talents.T_FLAME]=5,
		[Talents.T_FLAMESHOCK]=5,
		[Talents.T_BURNING_WAKE]=5,
		[Talents.T_CLEANSING_FLAMES]=5,
		[Talents.T_MANATHRUST]=5,
		[Talents.T_ARCANE_POWER]=5,
		[Talents.T_DISRUPTION_SHIELD]=5,
		[Talents.T_FREEZE]=5,
		[Talents.T_SHOCK]=5,
		[Talents.T_TEMPEST]=5,
		[Talents.T_HURRICANE]=5,
		[Talents.T_ESSENCE_OF_SPEED]=5,
		[Talents.T_PHASE_DOOR]=5,
		[Talents.T_TELEPORT]=5,
		[Talents.T_KEEN_SENSES]=5,
		[Talents.T_PREMONITION]=5,
		[Talents.T_HIGH_THAUMATURGIST]=1,
		[Talents.T_ORB_OF_THAUMATURGY]=5,
		[Talents.T_SLIPSTREAM]=5,
		[Talents.T_MULTICASTER]=5,
		[Talents.T_ELEMENTAL_ARRAY_BURST]=5,
	},
	resolvers.sustains_at_birth(),

	can_talk = "angolwen-leader",

	self_resurrect = 5,
	on_resurrect = function(self)
		game.bignews:saySimple(120, "#GOLD#Linaniil concentrates her formidable will to restore her body!")
		self.inc_damage.all = self.inc_damage.all + 35
		self.max_life = self.max_life * 1.3
		self.life = self.life * 1.3
	end,
	on_die = function(self)
		world:gainAchievement("LINANIIL_DEAD", game.player)
	end,
}
-- INHERITED BASE
