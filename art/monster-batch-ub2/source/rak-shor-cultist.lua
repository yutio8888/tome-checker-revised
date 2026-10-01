-- Verified leaf and inherited base; source hashes in source-contracts.json
newEntity{ base="BASE_NPC_ORC_RAK_SHOR", define_as = "CULTIST_RAK_SHOR",
	name = "Rak'Shor Cultist", color=colors.VIOLET, unique = true,
	desc = _t[[An old orc, wearing black robes. He seems to be responsible for the creation of the shades.]],
	killer_message = _t"but nobody knew why they suddenly became evil",
	level_range = {35, nil}, exp_worth = 2,
	rank = 4,
	max_life = 150, life_rating = 17, fixed_rating = true,
	infravision = 10,
	stats = { str=15, dex=10, cun=42, mag=16, con=14 },
	move_others=true,

	instakill_immune = 1,
	disease_immune = 1,
	confusion_immune = 1,
	combat_armor = 10, combat_def = 10,

	open_door = true,

	autolevel = "caster",
	ai = "tactical", ai_state = { talent_in=1, ai_move="move_astar", },
	ai_tactic = resolvers.tactic"ranged",
	resolvers.inscriptions(3, "rune"),

	body = { INVEN = 10, MAINHAND=1, OFFHAND=1, BODY=1 },

	resolvers.equip{
		{type="weapon", subtype="staff", force_drop=true, tome_drops="boss", forbid_power_source={antimagic=true}, autoreq=true},
	},
	resolvers.drops{chance=20, nb=1, {defined="JEWELER_TOME"} },
	resolvers.drops{chance=100, nb=1, {defined="LIFE_DRINKER", random_art_replace={chance=75}} },
	resolvers.drops{chance=100, nb=5, {tome_drops="boss"} },

	inc_damage = {[DamageType.BLIGHT] = -30},

	resolvers.talents{
		[Talents.T_STAFF_MASTERY]={base=3, every=7, max=5},
		[Talents.T_SOUL_ROT]={base=5, every=10, max=7},
		[Talents.T_BLOOD_GRASP]={base=5, every=10, max=7},
		[Talents.T_BONE_SHIELD]={base=5, every=10, max=7},
		[Talents.T_EVASION]={base=5, every=10, max=7},
		[Talents.T_VIRULENT_DISEASE]={base=5, every=10, max=7},
		[Talents.T_CYST_BURST]={base=3, every=10, max=7},
		[Talents.T_EPIDEMIC]={base=4, every=10, max=7},
		[Talents.T_WORM_ROT]={base=4, every=10, max=7},
	},
	resolvers.sustains_at_birth(),

	on_takehit = function(self, value, src)
		local p = self.sustain_talents[self.T_BONE_SHIELD]

		-- When the bone shield is taken down, copy the player
		if (not p or p.nb <= 0) and not self.copied_player then
			local Talents = require("engine.interface.ActorTalents")
			local a = mod.class.NPC.new{}
			local plr = game.player:resolveSource()

			local is_yeek = false
			if plr.descriptor and plr.descriptor.subrace == "Yeek" then is_yeek = true end

			a:replaceWith(plr:cloneActor({rank=4,
				level_range=self.level_range,
				is_player_doomed_shade = true,
				faction = is_yeek and plr.faction or self.faction,
				life=plr.max_life*1.2,	max_life=plr.max_life*1.2, die_at=plr.die_at*1.2,
				max_level=table.NIL_MERGE,
				name = is_yeek and ("Wayist Shade of %s"):format(plr.name) or ("Doomed Shade of %s"):format(plr.name),
				desc = is_yeek and ([[%s under the mental protection of The Way could not be swayed and sided with you against the Cultist!]]):format(plr.name) or ([[The Dark Side of %s, completely consumed by hate...]]):format(plr.name),
				killer_message = _t"but nobody knew why they suddenly became evil",
				color_r = 150, color_g = 150, color_b = 150,
				ai = "tactical", ai_state = {talent_in=1},
				}))
			mod.class.NPC.castAs(a)
			engine.interface.ActorAI.init(a, a)
			a.inc_damage.all = (a.inc_damage.all or 0) - 40
			a.on_die = function(self)
				world:gainAchievement("SHADOW_CLONE", game.player)
				game:setAllowedBuild("afflicted")
				game:setAllowedBuild("afflicted_doomed", true)
				game.level.map(self.x, self.y, game.level.map.TERRAIN, game.zone.grid_list.UP_WILDERNESS)
				game.logSeen(self, "As your shade dies, the magical veil protecting the stairs out vanishes.")
			end

			-- Remove any disallowed talents
			a:unlearnTalentsOnClone()
			-- Add some hate-based talents
			table.insert(a, resolvers.talents{
				[Talents.T_UNNATURAL_BODY]={base=5, every=10, max=7},
				[Talents.T_RELENTLESS]={base=5, every=10, max=7},
				[Talents.T_FEED_POWER]={base=5, every=10, max=5},
				[Talents.T_FEED_STRENGTHS]={base=5, every=10, max=5},
				[Talents.T_DARK_TENDRILS]={base=5, every=10, max=5},
				[Talents.T_WILLFUL_STRIKE]={base=5, every=10, max=7},
				[Talents.T_REPROACH]={base=5, every=10, max=5},
				[Talents.T_CALL_SHADOWS]={base=5, every=10, max=5},
			})
			a:incStat("wil", a.level)
			local x, y = util.findFreeGrid(self.x, self.y, 10, true, {[engine.Map.ACTOR]=true})
			if x and y then
				self:logCombat(game.player, "#GREY#The #Source# looks deep into your eyes. You feel torn apart!")
				self:doEmote(_t"Ra'kk kor merk ZUR!!!", 120)
				game.zone:addEntity(game.level, a, "actor", x, y)
				a:removeTimedEffectsOnClone()
				a:resolve()
				if is_yeek then
					a:doEmote(_t"FOR THE WAY! Die cultist!", 120)
					a.can_talk = "shadow-crypt-yeek-clone"
					self:logCombat(game.player, "#PURPLE#The #Source# looks afraid, he did not plan on his creation turning against him!")
				end
				self.copied_player = true
			end

			if plr.alchemy_golem then
				a.alchemy_golem = nil
				local t = a:getTalentFromId(a.T_REFIT_GOLEM)
				t.action(a, t)
			end
		end
		return value
	end,
}
-- INHERITED BASE
newEntity{
	define_as = "BASE_NPC_ORC_RAK_SHOR",
	type = "humanoid", subtype = "orc",
	display = "o", color=colors.DARK_GREY,
	faction = "orc-pride", pride = "rak-shor",

	combat = { dam=resolvers.rngavg(5,12), atk=2, apr=6, physspeed=2 },

	body = { INVEN = 10, MAINHAND=1, OFFHAND=1, BODY=1, QUIVER=1, TOOL=1 },
	resolvers.drops{chance=20, nb=1, {} },
	resolvers.drops{chance=10, nb=1, {type="money"} },
	resolvers.auto_equip_filters("Necromancer"),
	infravision = 10,
	lite = 1,

	life_rating = 11,
	rank = 2,
	size_category = 3,

	resolvers.racial(),

	open_door = true,
	resolvers.inscriptions(3, "rune"),

	autolevel = "caster",
	ai = "dumb_talented_simple", ai_state = { ai_move="move_complex", talent_in=1, },
	stats = { str=20, dex=8, mag=6, con=16 },
	ingredient_on_death = "ORC_HEART",
}
