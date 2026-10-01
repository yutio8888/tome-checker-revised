-- Verified leaf and inherited base; source hashes in source-contracts.json
newEntity{ define_as = "HIGH_SUN_PALADIN_AERYN",
	type = "humanoid", subtype = "human",
	display = "p",
	faction = "sunwall",
	name = "High Sun Paladin Aeryn", color=colors.VIOLET, unique = "High Sun Paladin Aeryn High Peak Help",
	resolvers.nice_tile{image="invis.png", add_mos = {{image="npc/humanoid_human_high_sun_paladin_aeryn.png", display_h=2, display_y=-1}}},
	desc = _t[[A beautiful woman, clad in shining plate armour. Power radiates from her.]],
	level_range = {56, nil}, exp_worth = 2,
	rank = 5,
	size_category = 3,
	female = true,
	max_life = 250, life_rating = 30, fixed_rating = true,
	infravision = 10,
	stats = { str=15, dex=10, cun=12, mag=16, con=14 },
	instakill_immune = 1,
	stun_immune = 0.5,
	move_others=true,
	never_anger = true,

	open_door = true,

	no_auto_resists = true,

	auto_classes={{class="Sun Paladin", start_level=57, level_rate=50,
			banned_talents = {
				T_SUNCLOAK=true,  -- Hyperscaler for survivability
			},
		}
	},

	autolevel = "warriormage",
	ai = "tactical", ai_state = { talent_in=1, ai_move="move_astar", },
	ai_tactic = resolvers.tactic"melee",
	resolvers.inscriptions(4, {}),

	body = { INVEN = 10, MAINHAND=1, OFFHAND=1, BODY=1, HEAD=1, FEET=1 },
	resolvers.auto_equip_filters("Sun Paladin"),
	resolvers.drops{chance=100, nb=3, {tome_drops="boss"} },

	resolvers.equip{
		{type="weapon", subtype="mace", force_drop=true, tome_drops="boss", forbid_power_source={antimagic=true}, autoreq=true},
		{type="armor", subtype="shield", force_drop=true, tome_drops="boss", forbid_power_source={antimagic=true}, autoreq=true},
		{type="armor", subtype="massive", force_drop=true, tome_drops="boss", forbid_power_source={antimagic=true}, autoreq=true},
		{type="armor", subtype="feet", force_drop=true, tome_drops="boss", forbid_power_source={antimagic=true}, autoreq=true},
		{type="armor", subtype="head", force_drop=true, tome_drops="boss", forbid_power_source={antimagic=true}, autoreq=true},
	},

	resolvers.talents{
		[Talents.T_ARMOUR_TRAINING]=4,
		[Talents.T_WEAPON_COMBAT]=5,
		[Talents.T_WEAPONS_MASTERY]=5,
		[Talents.T_RUSH]=3,

		[Talents.T_CHANT_OF_FORTRESS]=1,
		[Talents.T_SUN_BEAM]=7,
		[Talents.T_BARRIER]=7,
		[Talents.T_WEAPON_OF_LIGHT]=7,
		[Talents.T_HEALING_LIGHT]=7,
		[Talents.T_CRUSADE]=7,
		[Talents.T_SHIELD_OF_LIGHT]=1,
		[Talents.T_SECOND_LIFE]=7,
		[Talents.T_BATHE_IN_LIGHT]=3,
		[Talents.T_PROVIDENCE]=3,
		[Talents.T_THICK_SKIN]=5,

		[Talents.T_IRRESISTIBLE_SUN]=1,
	},
	resolvers.sustains_at_birth(),
}

-- For the sunpala evo ending
load("/data/general/npcs/shertul.lua")
-- INHERITED BASE
