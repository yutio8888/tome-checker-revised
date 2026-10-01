-- Verified leaf and inherited base; source hashes in source-contracts.json
newEntity{ base = "BASE_NPC_SLAVER",
	name = "slaver", color=colors.TEAL,
	subtype = "yaech",
	desc = _t[[A slaver.]],
	level_range = {10, nil}, exp_worth = 1,
	rarity = 1,
	size_category = 2,
	max_life = resolvers.rngavg(80,90), life_rating = 11,
	resolvers.equip{
		{type="weapon", subtype="staff", forbid_power_source={antimagic=true}, autoreq=true},
	},
	combat_armor = 0, combat_def = 6,
	resolvers.talents{
		[Talents.T_STAFF_MASTERY]={base=1, every=8, max=5},
		[Talents.T_MANATHRUST]={base=3, every=5, max=6},
		[Talents.T_FLAME]={base=3, every=5, max=6},
		[Talents.T_LIGHTNING]={base=3, every=5, max=6},
		[Talents.T_FLAMESHOCK]={base=3, every=5, max=6},
	},

	make_escort = {
		{type="humanoid", subtype="human", name="enthralled slave", number=2, post=function(self, m)
			m.master = self
			m.on_act = function(self)
				if self.master and self.master:attr("dead") then
					self.faction = "neutral"
					self:removeAllEffects()
					self:doEmote(rng.table{_t"I am free!", _t"At last, freedom!", _t"Thanks for this!", _t"The mental hold is gone!"}, 60)
					self.on_act = nil
					self.master = nil
					world:gainAchievement("RING_BLOOD_FREED", game:getPlayer(true))
				end
			end
		end},
	}
}
-- INHERITED BASE
newEntity{
	define_as = "BASE_NPC_SLAVER",
	type = "humanoid", subtype = "human",
	display = "p", color=colors.DARK_KHAKI,
--	faction = "slavers",

	combat = { dam=resolvers.rngavg(5,12), atk=2, apr=6, physspeed=2 },

	body = { INVEN = 10, MAINHAND=1, OFFHAND=1, BODY=1, QUIVER=1, HANDS = 1 },
	resolvers.drops{chance=20, nb=1, {} },
	resolvers.drops{chance=10, nb=1, {type="money"} },
	infravision = 10,
	lite = 1,

	life_rating = 15,
	rank = 2,
	size_category = 3,

	open_door = true,

	resolvers.racial(),
	resolvers.talents{ [Talents.T_ARMOUR_TRAINING]=2, [Talents.T_WEAPON_COMBAT]={base=1, every=10, max=5}, [Talents.T_WEAPONS_MASTERY]={base=1, every=10, max=5} },

	autolevel = "warrior",
	ai = "dumb_talented_simple", ai_state = { ai_move="move_complex", talent_in=3, },
	stats = { str=20, dex=8, mag=6, con=16 },
}
