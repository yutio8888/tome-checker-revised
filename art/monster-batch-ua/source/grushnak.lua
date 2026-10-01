-- Verified leaf and inherited base; source hashes in source-contracts.json
newEntity{ base="BASE_NPC_ORC_GRUSHNAK", define_as = "GRUSHNAK",
	allow_infinite_dungeon = true,
	name = "Grushnak, Battlemaster of the Pride", color=colors.VIOLET, unique = true,
	desc = _t[[An old orc, covered in battle scars, he looks fierce and very, very, dangerous.]],
	killer_message = _t"and mounted on the barracks wall",
	level_range = {45, nil}, exp_worth = 1,
	rank = 5,
	max_life = 700, life_rating = 25, fixed_rating = true,
	infravision = 10,
	stats = { str=15, dex=10, cun=12, wil=45, mag=16, con=14 },
	move_others=true,

	instakill_immune = 1,
	stun_immune = 1,
	combat_armor = 10, combat_def = 10,
	stamina_regen = 40,

	open_door = true,

	autolevel = "warrior",
	ai = "tactical", ai_state = { talent_in=1, ai_move="move_astar", },
	ai_tactic = resolvers.tactic"melee",
	resolvers.inscriptions(4, "infusion"),

	body = { INVEN = 10, MAINHAND=1, OFFHAND=1, BODY=1, HEAD=1, FEET=1, FINGER=2, NECK=1, TOOL=1 },
	resolvers.auto_equip_filters("Bulwark"),
	resolvers.equip{
		{type="weapon", subtype="waraxe", force_drop=true, tome_drops="boss", autoreq=true},
		{type="armor", subtype="shield", force_drop=true, tome_drops="boss", autoreq=true},
		{type="armor", subtype="massive", force_drop=true, tome_drops="boss", autoreq=true},
		{type="armor", subtype="head", force_drop=true, tome_drops="boss", autoreq=true},
		{type="armor", subtype="feet", force_drop=true, tome_drops="boss", autoreq=true},
		{type="charm", subtype="totem"},
--		Commented because this can generate rings of invis or amulets of telepathy and drain the life of the boss
--		{type="jewelry", subtype="amulet", force_drop=true, tome_drops="boss", autoreq=true},
--		{type="jewelry", subtype="ring", force_drop=true, tome_drops="boss", autoreq=true},
		{type="jewelry", subtype="ring", defined="PRIDE_GLORY", random_art_replace={chance=75}, autoreq=true},
	},
	resolvers.drops{chance=100, nb=1, {defined="ORB_DESTRUCTION"} },
	resolvers.drops{chance=100, nb=5, {tome_drops="boss"} },
	resolvers.drops{chance=100, nb=1, {defined="NOTE_LORE"} },

	make_escort = {
		{type="orc", no_subescort=true, number=resolvers.mbonus(6, 5)},
	},

	resolvers.talents{
		[Talents.T_WEAPON_COMBAT]={base=5, every=10, max=7},
		[Talents.T_ARMOUR_TRAINING]={base=5, every=10, max=7},
		[Talents.T_WEAPONS_MASTERY]={base=5, every=10, max=7},
		[Talents.T_RUSH]={base=5, every=6, max=7},
		[Talents.T_BATTLE_CALL]={base=5, every=6, max=7},
		[Talents.T_SHIELD_PUMMEL]={base=4, every=6, max=6},
		[Talents.T_OVERPOWER]={base=5, every=6, max=7},
		[Talents.T_ASSAULT]={base=3, every=6, max=6},
		[Talents.T_SHIELD_EXPERTISE]={base=5, every=6, max=7},
		[Talents.T_BATTLE_SHOUT]={base=3, every=6, max=6},
		[Talents.T_SHIELD_WALL]={base=5, every=6, max=7},
		[Talents.T_SHATTERING_SHOUT]={base=5, every=6, max=7},
		[Talents.T_BATTLE_CRY]={base=5, every=6, max=7},
		[Talents.T_ONSLAUGHT]={base=5, every=6, max=7},
		[Talents.T_SECOND_WIND]={base=5, every=6, max=7},
		[Talents.T_JUGGERNAUT]={base=5, every=6, max=7},
		[Talents.T_UNSTOPPABLE]={base=5, every=6, max=7},
		[Talents.T_MORTAL_TERROR]={base=3, every=6, max=6},
		[Talents.T_BLOODBATH]={base=5, every=6, max=7},
		[Talents.T_ETERNAL_GUARD]=1,
		[Talents.T_UNBREAKABLE_WILL]=1,
		[Talents.T_GIANT_LEAP]=1,
	},

	auto_classes={
		{class="Bulwark", start_level=45, level_rate=75},
	},
	resolvers.sustains_at_birth(),

	on_die = function(self, who)
		game.player:resolveSource():setQuestStatus("orc-pride", engine.Quest.COMPLETED, "grushnak")
		if not game.player:hasQuest("pre-charred-scar") then
			game.player:grantQuest("pre-charred-scar")
		end
	end,
}
-- INHERITED BASE
newEntity{
	define_as = "BASE_NPC_ORC_GRUSHNAK",
	type = "humanoid", subtype = "orc",
	display = "o", color=colors.UMBER,
	faction = "orc-pride", pride = "grushnak",

	combat = { dam=resolvers.rngavg(5,12), atk=2, apr=6, physspeed=2 },

	body = { INVEN = 10, MAINHAND=1, OFFHAND=1, BODY=1, QUIVER=1, TOOL=1 },
	resolvers.drops{chance=20, nb=1, {} },
	resolvers.drops{chance=10, nb=1, {type="money"} },
	infravision = 10,
	lite = 1,

	life_rating = 15,
	rank = 2,
	size_category = 3,

	resolvers.racial(),
	rnd_boss_init = function(self, data)
        self.inc_damage.all = (self.inc_damage.all or 0) - 30  -- Compensate for high base damage talents
    end,
	open_door = true,
	resolvers.sustains_at_birth(),
	resolvers.inscriptions(3, "infusion"),

	autolevel = "warrior",
	ai = "dumb_talented_simple", ai_state = { ai_move="move_complex", talent_in=3, },
	stats = { str=20, dex=8, mag=6, con=16 },
	ingredient_on_death = "ORC_HEART",
}
