-- Load only through the existing isolated debug fixture, never in a user save.
local S=require 'mod.class.CheckerTokenStyle'
local D=require 'engine.DamageType'
local M={}
local function guard()
 assert(config.settings.cheat and config.settings.disable_all_connectivity and not profile.auth)
 assert(__module_extra_info.checker_demo and game.checker_staged and game.checker_mode=='refined')
 assert(monster_scene and monster_scene.kind=='dense')
end
function M.begin()
 guard()
 for _,a in ipairs(monster_scene.actors) do if a.name=='forest troll' then M.actor=a end end
 local a=assert(M.actor);local eff=assert(a:hasEffect(a.EFF_DAMAGE_SHIELD))
 M.particle=assert(eff.particle);M.life,M.rank,M.turn=a.life,a.rank,game.turn
 M.initial=assert(a.damage_shield_absorb)
 assert(a.__particles[M.particle] and M.particle.ps:isAlive())
 local value,maximum,hidden=S.shieldData(a)
 assert(value==M.initial and maximum==a.damage_shield_absorb_max and hidden[M.particle])
 D:get(D.PHYSICAL).projector(game.player,a.x,a.y,D.PHYSICAL,10)
 M.remaining=a.damage_shield_absorb
 assert(M.remaining>0 and M.remaining<M.initial and a.life==M.life,'shield must absorb the native hit')
 assert(a.rank==M.rank and game.turn==M.turn and a:hasEffect(a.EFF_DAMAGE_SHIELD).particle==M.particle)
 game:displayDelayedLogMessages();game:displayDelayedLogDamage();game.level.map:redisplay()
 print('[ShieldLive] ABSORB',M.initial,M.remaining,'life unchanged',a.life,'rank',a.rank)
end
function M.deplete()
 guard();local a=assert(M.actor)
 -- A hit strictly exceeding the remaining capacity exercises native shield
 -- break/deactivation, not an artificial edit to damage_shield_absorb.
 D:get(D.PHYSICAL).projector(game.player,a.x,a.y,D.PHYSICAL,60)
 assert(not a:hasEffect(a.EFF_DAMAGE_SHIELD),'native hit must break the shield')
 local value,maximum,hidden=S.shieldData(a)
 assert(value==0 and maximum==0 and not next(hidden))
 assert(not a.__particles[M.particle] and not M.particle.ps,'native deactivation cleans its own emitter')
 assert(a.life>0 and a.life<M.life and a.rank==M.rank and game.turn==M.turn)
 M.broken_life=a.life
 game:displayDelayedLogMessages();game:displayDelayedLogDamage();game.level.map:redisplay()
 print('[ShieldLive] DEPLETED','life',a.life,'shield absent; native emitter cleaned')
end
function M.restoreAndFallback()
 guard();local a=assert(M.actor)
 a:setEffect(a.EFF_DAMAGE_SHIELD,5,{power=40},true)
 local p=assert(a:hasEffect(a.EFF_DAMAGE_SHIELD).particle)
 game.checker_native_actors=true;game:checkerSetMode('refined')
 assert(not a._checker_token and a.__particles[p] and a:hasEffect(a.EFF_DAMAGE_SHIELD).particle==p)
 game.checker_native_actors=false;game:checkerSetMode('refined')
 assert(a._checker_token and a.__particles[p] and a:hasEffect(a.EFF_DAMAGE_SHIELD).particle==p)
 assert(a.rank==M.rank and a.life==M.broken_life and game.turn==M.turn)
 local f=assert(fs.open('/shield-live-validation.txt','w'))
 f:write(('shader=%s\nNative hit: shield %.6f -> %.6f; life unchanged %.6f\nNative depletion: shield removed, life %.6f, emitter deactivated by native effect\nReapply plus vanilla/refined round trip: same emitter, unchanged life/rank/turn\n'):format(tostring(core.shader.active(4)),M.initial,M.remaining,M.life,M.broken_life));f:close()
 print('[ShieldLive] RESTORE/FALLBACK PASS; same native emitter, unchanged actor rules')
end
return M
