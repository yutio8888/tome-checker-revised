-- Offline 0.6.3 fixture only. Native levels and actors, explicitly arranged.
-- No live AI turn is claimed: skill tests call native action handlers directly.
local Map=require 'engine.Map'
local Tokens=require 'mod.class.CheckerTokens'
local Style=require 'mod.class.CheckerTokenStyle'
local M={actors={},rows={}}
local C0={['giant white rat']='giant-white-rat',['giant grey rat']='giant-grey-rat',
 ['green worm mass']='green-worm-mass',['copperhead snake']='copperhead-snake'}
local function guard()
 assert(require('mod.class.CheckerFixture').enabled() and not profile.auth)
 assert(game.player==game.checker_hero and game.checker_staged and game.paused)
 assert(game.zone.short_name=='ruins-kor-pul' and #Tokens.catalog==37)
end
local function say(text)
 M.rows[#M.rows+1]=text;print('[C0Live]',text)
 local f=assert(fs.open('/c0-validation-'..M.layout:lower()..'.txt','w'))
 f:write(table.concat(M.rows,'\n')..'\n');f:close()
end
local function clean(v) return tostring(v==nil and '' or v):gsub('[\t\r\n]',' ') end
function M.refresh()
 local m=game.level.map;m.clean_fov=true
 game.player:playerFOV();m.smooth_scroll=0;m:centerViewAround(game.player.x,game.player.y)
 game:checkerRefreshVisuals();m:redisplay();m.changed=true;game.paused=true
 core.display.forceRedraw()
end
local function free(x,y)
 local m=game.level.map
 if not m:isBound(x,y) or m(x,y,Map.ACTOR) or not m.seens(x,y) then return false end
 local g=m(x,y,Map.TERRAIN)
 return g and not g.change_level and not g.change_zone and not m:checkEntity(x,y,Map.TERRAIN,'block_move',game.player)
end
local function nearby(tx,ty)
 local x0,y0,score
 local p=game.player
 for x=p.x-4,p.x+4 do for y=p.y-3,p.y+3 do
  if free(x,y) then local d=(x-tx)^2+(y-ty)^2;if not score or d<score then x0,y0,score=x,y,d end end
 end end
 assert(x0,'insufficient visible native floor');return x0,y0
end
function M.enter(layout,seed)
 local sc=dofile('/data-checker-fixture/monster-live_korpul_scene.lua')
 sc.enter(layout,seed);sc.stage();sc.dismissFixturePrompts()
 M.layout,M.seed,M.rows,M.actors,M.by_name=layout,seed,{}, {}, {}
 guard()
 local remove={};for _,a in pairs(game.level.entities) do if a.ai and a~=game.player then remove[#remove+1]=a end end
 for _,a in ipairs(remove) do game.level.map:remove(a.x,a.y,Map.ACTOR);game.level:removeEntity(a,true) end
 M.refresh()
 local source={};for _,p in pairs(game.zone.npc_list) do if type(p)=='table' and p.name then source[p.name]=p end end
 local names={'giant brown rat','giant white rat','giant grey rat','white worm mass','green worm mass','large brown snake','copperhead snake'}
 for i,name in ipairs(names) do
  local a=game.zone:finishEntity(game.level,'actor',assert(source[name],name));a.never_act=true
  local x,y=nearby(game.player.x+(i-1)%4*2-3,game.player.y+math.floor((i-1)/4)*3-2)
  game.zone:addEntity(game.level,a,'actor',x,y)
  M.actors[#M.actors+1]=a;M.by_name[name]=a
 end
 M.refresh()
 for name,id in pairs(C0) do local a=M.by_name[name];assert(a._checker_token and a._checker_token.id==id and a._mo) end
 -- Real unresolved family member must keep native art; do not show an
 -- intentionally uncovered actor in the comparison gallery.
 local a=game.zone:finishEntity(game.level,'actor',assert(source['giant grey mouse']))
 assert(not game:checkerRefreshActor(a) and not a.replace_display,'uncovered mouse must stay native')
 say(layout..' native-generation seed='..seed..'; seven arranged native identities; C0 mapped; unknown mouse fallback PASS')
 M.phase='baseline';M.dump('baseline')
 game.log('#LIGHT_BLUE#C0 art test: %s; 4 new tokens + 3 family references; frozen AI.',layout)
end
function M.mode(enabled)
 guard();game:checkerSetTokensEnabled(enabled);M.refresh()
 for _,a in ipairs(M.actors) do
  if enabled then assert(a._checker_token and a._mo,a.name..' missing token')
  else assert(not a._checker_token and not a.replace_display,a.name..' native restore failed') end
 end
end
function M.dump(phase)
 guard();local f=assert(fs.open('/c0-scene-'..M.layout:lower()..'-'..phase..'.tsv','w'))
 f:write('name\tuid\tx\ty\timage\ttoken\tlife\tmax_life\tfaction\trank\tcan_multiply\tdisplay_uid\toverlay_uid\tshield\tshield_max\n')
 local rules={table.concat({game.turn,game.player.x,game.player.y,game.player.life,game.player.energy.value},'\t')}
 for _,a in ipairs(M.actors) do
  local s=a._checker_token;local shield,maxshield=Style.shieldData(a)
  local values={a.name,a.uid,a.x,a.y,a.image,s and s.id or 'native',a.life,a.max_life,a.faction,a.rank,a.can_multiply,s and s.display.uid,s and s.overlay and s.overlay.uid,shield,maxshield}
  local row={};for i=1,15 do row[i]=clean(values[i]) end;f:write(table.concat(row,'\t')..'\n')
  local r={};for _,key in ipairs({'uid','x','y','name','image','life','max_life','faction','rank','can_multiply'}) do r[#r+1]=clean(a[key]) end
  r[#r+1]=clean(a.energy.value);r[#r+1]=clean(shield);rules[#rules+1]=table.concat(r,'\t')
 end
 f:close();local r=assert(fs.open('/c0-rules-'..M.layout:lower()..'-'..phase..'.txt','w'));r:write(table.concat(rules,'\n')..'\n');r:close()
end
function M.multiply()
 guard();assert(game:checkerTokensEnabled())
 local parent=M.by_name['green worm mass'];assert(parent:knowTalent(parent.T_MULTIPLY))
 parent.life=parent.max_life*.65
 M.refresh()
 local family={parent};local turn=game.turn
 for step=1,2 do
  local source=family[#family];local t=source:getTalentFromId(source.T_MULTIPLY)
  assert(debug.getinfo(t.action,'S').source:find('talents/misc/npcs.lua',1,true),'not native Multiply')
  local before={};for _,a in pairs(game.level.entities) do before[a]=true end
  local budget=source.can_multiply;local energy=source.energy.value;local cooldown=source.talents_cd[t.id]
  assert(t.action(source,t)==true,'native Multiply could not find space')
  local children={};for _,a in pairs(game.level.entities) do if not before[a] then children[#children+1]=a end end
  assert(#children==1,'expected exactly one native child')
  local child=children[1];child.never_act=true
  assert(child.name==parent.name and child.image==parent.image and child.uid~=source.uid)
  assert(source.can_multiply==budget-1 and child.can_multiply==budget-2)
  assert(child.exp_worth==.1 and child.no_drops and child.immune_possession==1 and child.energy.value==0)
  assert(source.energy.value==energy and source.talents_cd[t.id]==cooldown)
  family[#family+1]=child;M.actors[#M.actors+1]=child
  M.refresh()
  for i,a in ipairs(family) do
   local s=assert(a._checker_token);assert(s.id=='green-worm-mass' and s.overlay and s.overlay_active and a._mo)
   for j=1,i-1 do local other=family[j]._checker_token
    assert(s.display~=other.display and s.overlay~=other.overlay and a._mo~=family[j]._mo)
   end
  end
  say(('Multiply %d: parent=%d child=%d; budget=%d->%d/%d; own body/overlay PASS'):format(step,source.uid,child.uid,budget,source.can_multiply,child.can_multiply))
 end
 assert(game.turn==turn)
 M.phase='multiply';M.dump(M.phase)
 say('Native T_MULTIPLY.action twice; no useTalent cooldown/energy wrapper or world tick claimed')
end
function M.states()
 guard();assert(game:checkerTokensEnabled())
 local white,grey,worm=M.by_name['giant white rat'],M.by_name['giant grey rat'],M.by_name['green worm mass']
 white.faction=game.player.faction;white.life=white.max_life*.75
 grey.faction='neutral';grey.life=grey.max_life*.4
 assert(Style.relation(white,game.player,game.player:reactionToward(white))=='friend')
 assert(Style.relation(grey,game.player,game.player:reactionToward(grey))=='neutral')
 assert(Style.relation(worm,game.player,game.player:reactionToward(worm))=='enemy')
 worm.life=worm.max_life*.55;worm:setEffect(worm.EFF_DAMAGE_SHIELD,5,{power=40},true)
 local D=require 'engine.DamageType';local life=worm.life
 D:get(D.PHYSICAL).projector(game.player,worm.x,worm.y,D.PHYSICAL,10)
 local shield,total=Style.shieldData(worm)
 assert(shield>0 and shield<40 and total==40 and worm.life==life)
 M.phase='states';M.refresh();M.dump(M.phase)
 say('State setup: friendly white rat ('..white.faction..'); neutral grey rat; enemy worm; native reactions asserted; native shield damaged 40->'..shield..'; life unchanged; shader='..tostring(core.shader.active(4)))
end
function M.skills()
 guard();assert(game:checkerTokensEnabled());local turn=game.turn
 local victim=M.by_name['giant white rat']
 -- Explicit durable target for the isolated action test; not normal monster stats.
 victim.max_life=1000;victim.life=1000;victim.faction=game.player.faction
 for _,pair in ipairs{{'green worm mass','T_CRAWL_ACID'},{'copperhead snake','T_BITE_POISON'}} do
  local a=M.by_name[pair[1]];local tx,ty
  for dx=-1,1 do for dy=-1,1 do if not tx and (dx~=0 or dy~=0) and free(victim.x+dx,victim.y+dy) then tx,ty=victim.x+dx,victim.y+dy end end end
  assert(tx,'no adjacent native skill test cell');a:move(tx,ty,true);a:resetMoveAnim();a:doFOV();a:setTarget(victim)
  local t=a:getTalentFromId(a[pair[2]]);assert(a:knowTalent(t.id))
  assert(debug.getinfo(t.action,'S').source:find('talents/misc/npcs.lua',1,true))
  local apr,energy,life=a.combat_apr,a.energy.value,victim.life
  assert(t.action(a,t)==true,'native skill action failed')
  assert(a.combat_apr==apr and a.energy.value==energy and victim.life>0)
  M.refresh();assert(a._checker_token and victim._checker_token)
  say(pair[2]..' native action PASS; victim life '..life..'->'..victim.life..'; poison='..tostring(victim:hasEffect(victim.EFF_POISONED)~=nil)..'; no world tick/cooldown wrapper claimed')
 end
 assert(game.turn==turn);M.phase='skills';M.dump(M.phase)
end
return M
