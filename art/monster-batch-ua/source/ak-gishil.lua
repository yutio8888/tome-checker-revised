-- Verified leaf and inherited base; source hashes in source-contracts.json
newEntity{ base = "BASE_NPC_HORROR",
	name = "Ak'Gishil", color=colors.GREY, unique = true,
	desc = _t"This Blade Horror has been infused with intense temporal magic, causing its power to increase dramatically. Rifts in space open around it constantly, summoning and banishing blades before vanishing as quickly as they appear.",
	resolvers.nice_tile{tall=1},
	level_range = {30, nil}, exp_worth = 2,
	rarity = 45,
	rank = 3.5,
	levitate=1,
	max_psi= 320,
	psi_regen= 5,
	size_category = 4,
	autolevel = "wildcaster",
	max_life = resolvers.rngavg(150, 180),
	life_rating = 32,
	life_regen = 0.25,
	global_speed_base = 1.2,
	combat_armor = 30, combat_def = 18,
	is_akgishil = true,
	can_spawn = 1,
	psionic_shield_override = 1,

	body = { TOOL=1 },
	resolvers.equip{
		{type="tool", ego_chance = 100, defined="BLADE_RIFT", random_art_replace={chance=25, filter = {type = "charm", subtype = "torque", no_tome_drops=true, unique=true, not_properties={"lore"}, special = function(o) return not table.get(o, "power_source", "antimagic") end}}, autoreq=true},
	},

	ai = "tactical", ai_state = { ai_move="move_complex", talent_in=2, ally_compassion=0 },

	melee_project = {[DamageType.PHYSICALBLEED]=resolvers.mbonus(32, 5)},
	combat = { dam=resolvers.levelup(resolvers.rngavg(20,28), 1, 1.5), physspeed = 0.25,atk=resolvers.levelup(24, 1.2, 1.2), apr=4, dammod={wil=0.3, cun=0.15}, damtype=engine.DamageType.PHYSICALBLEED, },
	--combat_physspeed = 4, --Crazy fast attack rate

	resists = {[DamageType.PHYSICAL] = 15, [DamageType.MIND] = 50, [DamageType.TEMPORAL] = 30, [DamageType.ARCANE] = -20},

	on_added_to_level = function(self)
		self.blades = 0
	end,

	on_act = function(self)
		if not self:attr("can_spawn") then return end
		if self.blades > 3 or not rng.percent(28/(self.blades+1)) then return end
		self.can_spawn = nil
		self.blades = self.blades + 1
		self:forceUseTalent(self.T_ANIMATE_BLADE, {ignore_cd=true, ignore_energy=true, force_level=1})
		self.can_spawn = 1
	end,

	resolvers.talents{
		--Original Blade Horror talents, beefed up
		[Talents.T_KNIFE_STORM]={base=5, every=5, max=8},
		[Talents.T_IMPLODE]={base=2, every=6, max=5},
		[Talents.T_RAZOR_KNIFE]={base=3, every=4, max=7},
		[Talents.T_PSIONIC_PULL]={base=5, every=3, max=7},
		[Talents.T_KINETIC_AURA]={base=4, every=3, max=8},
		[Talents.T_KINETIC_SHIELD]={base=5, every=2, max=9},
		[Talents.T_THERMAL_SHIELD]={base=5, every=2, max=9},
		[Talents.T_CHARGED_SHIELD]={base=5, every=2, max=9},
		[Talents.T_KINETIC_LEECH]={base=3, every=3, max=5},
		--TEMPORAL
		[Talents.T_INDUCE_ANOMALY]={base=1, every=4, max=5},
		[Talents.T_QUANTUM_SPIKE]={base=1, every=4, max=5},
		[Talents.T_WEAPON_FOLDING]={base=1, every=4, max=5},
		[Talents.T_RETHREAD]={base=2, every=4, max=5},
		[Talents.T_DIMENSIONAL_STEP]={base=3, every=4, max=5},

		[Talents.T_THROUGH_THE_CROWD]=1,
	},
	resolvers.sustains_at_birth(),
}

-- INHERITED BASE
newEntity{
	define_as = "BASE_NPC_HORROR",
	type = "horror", subtype = "eldritch",
	display = "h", color=colors.WHITE,
	blood_color = colors.BLUE,
	body = { INVEN = 10 },
	autolevel = "warrior",
	ai = "dumb_talented_simple", ai_state = { ai_move="move_complex", talent_in=3, },
	faction = "horrors",

	stats = { str=20, dex=20, wil=20, mag=20, con=20, cun=20 },
	combat_armor = 5, combat_def = 10,
	combat = { dam=5, atk=10, apr=5, dammod={str=0.6} },
	infravision = 10,
	max_life = resolvers.rngavg(10,20),
	rank = 2,
	size_category = 3,

	no_breath = 1,
	fear_immune = 1,
}
