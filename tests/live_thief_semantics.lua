-- Disposable OFFLINE checker fixture only; never install in production.
-- audit=dofile('/checker-live-thief-semantics.lua'); audit.run()
-- Spawns/removes four native temporary NPCs. Only these test NPCs undergo
-- native breakStealth/cooldownTalents/useTalent; never use this for art captures.
-- No turn advances, no saves, no forced detection on the real player.
local Map=require 'engine.Map'
local Tokens=require 'mod.class.CheckerTokens'
local M={results={}}
local ids={'cutpurse','rogue','thief','bandit'}
local function guard()
 assert(config.settings.cheat and config.settings.disable_all_connectivity and profile and not profile.auth,'isolated offline debug fixture required')
 assert(__module_extra_info.checker_demo and game.checker_staged and game.zone.short_name=='ruins-kor-pul' and game.zone.is_hideout,'staged HIDEOUT fixture required')
 assert(game.player==game.checker_hero and game:checkerTokensEnabled(),'restore fixture hero and enable tokens first')
end
local function record(id,state,detail)
 M.results[#M.results+1]={id=id,state=state,detail=detail}
 print('[ThiefSemantics]',id,state,detail)
 local f=assert(fs.open('/thief-semantics-results.txt','a'));f:write(id..'\t'..state..'\t'..detail..'\n');f:close()
end
function M.report(a)
 local viewer=game.level.map.actor_player
 local seen,chance=true,100
 if viewer then seen,chance=viewer:canSee(a) end
 local id,why=Tokens.explain(a,a._checker_token and a._checker_token.display)
 return {name=a.name,id=id,reason=why,known=a:knowTalent(a.T_STEALTH) and true or false,
  active=a:isTalentActive(a.T_STEALTH) and true or false,stealth=a:attr('stealth'),
  visible=seen,chance=chance,shader=a.shader,rank=a.rank,unique=a.unique,define_as=a.define_as}
end
local function source(id)
 local entry=Tokens.by_id[id]
 for _,p in pairs(game.zone.npc_list) do
  if p.name==entry.name and p.define_as==entry.define_as and not p.unique then return p end
 end
 error('missing native prototype '..id)
end
local function free(a)
 local map=game.level.map
 -- Prefer remote ground, avoiding player movement, terrain edits and traps.
 for x=1,map.w-2 do for y=1,map.h-2 do
  local g=map(x,y,Map.TERRAIN)
  if math.max(math.abs(x-game.player.x),math.abs(y-game.player.y))>12
   and g and not g.change_level and not g.change_zone and not map(x,y,Map.ACTOR)
   and not map(x,y,Map.TRAP) and not map(x,y,Map.TRIGGER)
   and not map:checkEntity(x,y,Map.TERRAIN,'block_move',a,false) then return x,y end
 end end
 error('no remote free fixture cell')
end
local function render(a)
 local mos={};a:getMapObjects(game.level.map.tiles,mos,10)
 return mos
end
function M.run()
 guard();M.results={}
 local hero,turn=game.player,game.turn
 local hx,hy,life,energy=hero.x,hero.y,hero.life,hero.energy.value
 -- A detached native observer tests deterministic blindness / ESP and
 -- probabilistic stronger stealth detection. It never becomes map.actor_player or changes hero stats.
 local observer=hero:clone()
 observer.player=nil;observer.esp={};observer.esp_all=nil
 local subject
 local ok,err=xpcall(function()
  for _,id in ipairs(ids) do
   local a=game.zone:finishEntity(game.level,'actor',source(id));subject=a
   assert(a.rank==2 and not a.unique,'native ordinary rank/unique changed: '..id)
   assert((a.define_as or false)==(Tokens.by_id[id].define_as or false),'definition changed')
   local x,y=free(a);game.zone:addEntity(game.level,a,'actor',x,y)
   local born=M.report(a)
   assert(game:checkerRefreshActor(a)==id,'native body failed exact registration: '..id)
   render(a)
   if id=='cutpurse' then
    assert(not born.known and not born.active and not born.stealth,'cutpurse acquired stealth')
    record(id,'PASS','native cutpurse has no Stealth; rank 2; exact token')
   else
    assert(born.known and born.active and born.stealth and born.stealth>0,'native on_added did not activate Stealth: '..id)
    local initial=a:attr('stealth')
    observer.blind=1;observer:resetCanSeeCache()
    assert(not observer:canSee(a),'native blind observer sees stealth actor')
    observer.esp.humanoid=1;observer:resetCanSeeCache()
    local seen,chance=observer:canSee(a)
    assert(seen and chance==100,'native ESP should identify actor even with blindness')
    observer.esp={};observer.blind=nil;observer:resetCanSeeCache()
    local baseline_seen,baseline_chance=observer:canSee(a)
    local detection=observer:addTemporaryValue('see_stealth',1000000)
    observer:resetCanSeeCache();seen,chance=observer:canSee(a)
    -- Native combat scaling/checkHitOld can approach 100 without reaching it.
    -- Improved detection raises the chance; it does not promise this roll hits.
    assert(type(chance)=='number' and chance>baseline_chance and chance<=100,
     'native high detection did not improve stealth detection probability')
    record(id,'PASS',('native detection baseline=%s chance=%s; boosted=%s chance=%s; ESP separately verified at 100'):format(tostring(baseline_seen),tostring(baseline_chance),tostring(seen),tostring(chance)))
    assert(a:isTalentActive(a.T_STEALTH) and a:attr('stealth')==initial,'being detected cancelled native stealth')
    observer:removeTemporaryValue('see_stealth',detection);observer:resetCanSeeCache()
    -- Native lifecycle only, on temporary subjects. Cooldowns elapse only on
    -- this isolated NPC; the world and real player's clocks do not move.
    a:breakStealth()
    assert(not a:isTalentActive(a.T_STEALTH) and not a:attr('stealth'),'native breakStealth failed')
    assert(game:checkerRefreshActor(a)==id,'exit from stealth lost identity')
    a:cooldownTalents(100)
    assert(a:useTalent(a.T_STEALTH,nil,nil,nil,nil,true),'native stealth re-entry rejected; leave this audit failed, never force it')
    assert(a:isTalentActive(a.T_STEALTH) and a:attr('stealth')==initial,'native re-entry changed stealth power')
    assert(game:checkerRefreshActor(a)==id,'stealth re-entry lost verified token')
    render(a)
    record(id,'PASS',('native birth, blind/ESP/detection, break and re-entry; stealth=%s; real hero sees=%s chance=%s; actor shader=%s'):format(initial,tostring(born.visible),tostring(born.chance),tostring(a.shader)))
   end
   if id=='rogue' and core.shader.active(4) then
    local kind='checker_thief_audit'
    assert(a:addShaderAura(kind,'awesomeaura',{time_factor=5500,alpha=.6,flame_scale=.6},'particles_images/arcaneshockwave.png'))
    assert(not a._checker_token and not a.replace_display,'real shader aura retained token')
    render(a)
    assert(a.shader_auras[kind] and a:isTalentActive(a.T_STEALTH),'shader fallback changed stealth')
    a:removeShaderAura(kind);render(a)
    assert(a._checker_token and a._checker_token.id==id,'removing real aura did not restore token')
    record(id,'PASS','real native shader aura fallback/recovery preserves active Stealth')
   elseif id=='rogue' then record(id,'SKIP','shader aura needs core.shader.active(4); no shader mock used') end
   local px,py=a.x,a.y
   game.level.map:remove(px,py,Map.ACTOR);game.level:removeEntity(a,true);subject=nil
   game.level.map:updateMap(px,py)
  end
 end,debug.traceback)
 if subject then
  if subject.x and game.level.map(subject.x,subject.y,Map.ACTOR)==subject then game.level.map:remove(subject.x,subject.y,Map.ACTOR) end
  game.level:removeEntity(subject,true)
  if subject.x then game.level.map:updateMap(subject.x,subject.y) end
 end
 game.level.map:redisplay()
 assert(game.player==hero and game.turn==turn and hero.x==hx and hero.y==hy and hero.life==life and hero.energy.value==energy,'audit altered hero or world turn')
 if not ok then error(err,0) end
 record('audit','PASS','temporary actors removed; hero position/life/energy and world turn unchanged; no save written')
 return true
end
return M
