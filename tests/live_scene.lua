-- Disposable, offline Trollmire art fixture. Uses real native actors and terrain;
-- frozen AI and arranged positions are not a gameplay/balance playthrough.
local Map=require 'engine.Map'
local Entity=require 'engine.Entity'
local Tokens=require 'mod.class.CheckerTokens'
local M={actors={},kind='none'}
local groups={
 giants={'forest-troll','stone-troll','cave-troll','prox','bill'},
 beasts={'wolf','great-wolf','fox','brown-bear','black-bear','brown-rat','brown-snake','venus-flytrap'},
 water={'king-cobra','bee-swarm','giant-eel','dragon-turtle'},
 canines={'wolf','great-wolf','dire-wolf','white-wolf','warg','fox'},
 snakes={'brown-snake','king-cobra','white-snake','rattlesnake','giant-eel'},
 swarms={'bee-swarm','midge-swarm','hornet-swarm','white-worm-mass'},
}

local function guard()
 assert(config.settings.cheat and config.settings.disable_all_connectivity and not profile.auth,'offline debug fixture required')
 assert(__module_extra_info.checker_demo and game.checker_staged and game.zone.short_name=='trollmire','stage the isolated Trollmire first')
 assert(game.player==game.checker_hero,'restore original player control before staging')
end
local function refresh()
 game.player:playerFOV();game.level.map:centerViewAround(game.player.x,game.player.y)
 game.level.map:redisplay();game.level.map.changed=true;game.player.changed=true;game.paused=true
 if game.uiset.npcs_display.refresh then game.uiset.npcs_display:refresh() end
end
local function candidates(entry,dx,dy,dense)
 local m,p=game.level.map,game.player
 local best,score
 for x=p.x-6,p.x+6 do for y=p.y-4,p.y+4 do
  if m:isBound(x,y) then
   local g=m(x,y,Map.TERRAIN)
   local water=g and g.subtype=='water'
   if g and m.seens(x,y) and not m(x,y,Map.ACTOR) and not m:checkEntity(x,y,Map.TERRAIN,'block_move',p)
     and (entry.type=='aquatic' and water or entry.type~='aquatic' and not water) then
    local d=(x-p.x-dx)^2+(y-p.y-dy)^2
    if not dense then
     for _,a in ipairs(M.actors) do if math.max(math.abs(x-a.x),math.abs(y-a.y))<=1 then d=d+12 end end
    end
    if not score or d<score then best={x,y};score=d end
   end
  end
 end end
 return assert(best,'not enough visible suitable terrain for '..entry.id)
end
local function sources()
 local out={}
 for _,entry in pairs(game.zone.npc_list) do if entry.name then out[entry.name]=entry end end
 -- The default (non-flooded) Trollmire does not spawn the aquatic set. Load
 -- their native definitions into this test's local table, not the zone pool.
 local aquatic=game.zone.npc_class:loadList('/data/general/npcs/aquatic_critter.lua',true)
 for _,entry in pairs(aquatic) do if entry.name then out[entry.name]=entry end end
 return out
end
local function clear()
 local old={}
 for _,a in pairs(game.level.entities) do if a~=game.checker_hero and a.ai then old[#old+1]=a end end
 for _,a in ipairs(old) do
  if game.level.map(a.x,a.y,Map.ACTOR)==a then game.level.map:remove(a.x,a.y,Map.ACTOR) end
  game.level:removeEntity(a,true)
 end
 M.actors={}
end

function M.setup(kind)
 guard();clear();game:checkerSetMode('refined');M.kind=kind
 local ids=groups[kind]
 if kind=='dense' then ids={};for _,e in ipairs(Tokens.catalog) do ids[#ids+1]=e.id end end
 assert(ids,'unknown monster scene')
 local src=sources()
 for i,id in ipairs(ids) do
  local entry=assert(Tokens.by_id[id])
  local a=game.zone:finishEntity(game.level,'actor',assert(src[entry.name],'missing native prototype: '..entry.name))
  a.never_act=true
  local dx,dy
  if kind=='dense' then dx=(i-1)%6-3;dy=math.floor((i-1)/6)-1
  else dx=((i-1)%4)*2-3;dy=math.floor((i-1)/4)*3-2 end
  local xy=candidates(entry,dx,dy,kind=='dense')
  game.zone:addEntity(game.level,a,'actor',xy[1],xy[2])
  M.actors[#M.actors+1]=a
  local got=game:checkerRefreshActor(a)
  assert(got==id,('native actor did not map: %s => %s; image=%s define=%s'):format(entry.name,tostring(got),tostring(a.image),tostring(a.define_as)))
 end
 game.log('#LIGHT_BLUE#[Monster art fixture] %s: %d native actors; frozen AI; arranged positions.',kind,#M.actors)
 refresh()
 local f=assert(fs.open('/monster-scene-'..kind..'.txt','w'))
 f:write(('kind=%s turn=%s tile=%s actors=%d\n'):format(kind,game.turn,game.level.map.tile_w,#M.actors))
 for _,a in ipairs(M.actors) do
  f:write(('%s\t%s\t%d,%d\trank=%s\tsize_category=%s\tdisplay_scale=%s\tfaction=%s\timage=%s\n'):format(a._checker_token.id,a.name,a.x,a.y,a.rank,tostring(a.size_category),tostring(a._checker_token.scale),a.faction,a.replace_display.image))
 end
 f:close()
 print('[MonsterLive] SCENE',kind,#M.actors,'turn',game.turn)
 return #M.actors
end

function M.audit()
 guard();assert(#M.actors==#Tokens.catalog,'audit the complete dense set')
 local turn,life,x,y=game.turn,game.player.life,game.player.x,game.player.y
 local before={}
 for _,a in ipairs(M.actors) do before[a]={a.x,a.y,a.life,a.max_life,a.faction,a.rank,a.image,a.add_mos} end
 local src=sources()
 for _,name in ipairs{'cave bear','mountain troll','Shax the Slimy','ancient dragon turtle'} do
  local a=game.zone:finishEntity(game.level,'actor',assert(src[name],'missing fallback prototype '..name))
  local image,mos=a.image,a.add_mos
  assert(not game:checkerRefreshActor(a) and not a._checker_token and not a.replace_display,'uncovered native actor received token: '..name)
  assert(a.image==image and a.add_mos==mos,'fallback changed native body: '..name)
 end
 for _,mode in ipairs{'vanilla','refined','blockout','vanilla','refined'} do
  game:checkerSetMode(mode)
  for _,a in ipairs(M.actors) do
   assert(a._checker_token and Tokens.identify(a,a._checker_token.display)==a._checker_token.id,'terrain mode changed token identity')
  end
 end
 for _,enabled in ipairs{false,true} do
  game:checkerSetTokensEnabled(enabled)
  for _,a in ipairs(M.actors) do
   if enabled then assert(a._checker_token,'token did not return after enabling')
   else assert(not a._checker_token and not a.replace_display,'disabled token did not restore native display') end
  end
 end
 local wolf
 for _,a in ipairs(M.actors) do if a.name=='wolf' then wolf=a end end
 assert(wolf)
 local owned=wolf.replace_display
 game:checkerRefreshActor(wolf);assert(wolf.replace_display==owned,'unchanged actor recreated its Entity')
 local external=Entity.new{image='npc/canine_dw.png'}
 wolf.replace_display=external
 game:checkerRefreshActor(wolf);assert(wolf.replace_display==external and not wolf._checker_token,'overwrote external replacement')
 game:checkerSetMode('vanilla');assert(wolf.replace_display==external,'vanilla erased external replacement')
 wolf.replace_display=nil;game:checkerSetMode('refined');assert(wolf._checker_token.id=='wolf','did not recover after transformation')
 local oldimage=wolf.image
 wolf.image='npc/canine_dw.png';game:checkerRefreshActor(wolf)
 assert(not wolf._checker_token and not wolf.replace_display,'new unknown body kept old token')
 wolf.image=oldimage;game:checkerRefreshActor(wolf);assert(wolf._checker_token.id=='wolf')
 -- Viewer/control changes must not turn a wolf into a human token.
 local player=game.player
 game.player=wolf;game:checkerRefreshActor(wolf);assert(wolf._checker_token.id=='wolf')
 game.player=player
 for a,s in pairs(before) do
  assert(a.x==s[1] and a.y==s[2] and a.life==s[3] and a.max_life==s[4] and a.faction==s[5]
   and a.rank==s[6] and a.image==s[7] and a.add_mos==s[8],'rendering changed native actor data')
 end
 assert(game.turn==turn and game.player.life==life and game.player.x==x and game.player.y==y,'actor rendering changed world state')
 refresh()
 print('[MonsterLive] AUDIT PASS:',#M.actors,'native identities; 4 actual uncovered prototypes; exact display ownership; body change and restore; controlled-wolf identity branch; independent terrain and token switches; actor rules unchanged')
end

function M.stateSample()
 guard();assert(M.kind=='dense','state sample requires dense scene')
 local actors={};for _,a in ipairs(M.actors) do actors[a._checker_token.id]=a end
 actors.wolf.faction=game.player.faction;actors.wolf.summoner=game.player;actors.wolf.summon_time=12
 actors.fox.faction='neutral'
 local target=actors['forest-troll']
 -- A real native hit feeds the game log and damage feedback; no AI or world
 -- turns are advanced. Keep this fixture separate from unchanged-rule audit.
 local DamageType=require 'engine.DamageType'
 DamageType:get(DamageType.PHYSICAL).projector(game.player,target.x,target.y,DamageType.PHYSICAL,math.min(15,target.life*.2))
 game:displayDelayedLogMessages();game:displayDelayedLogDamage()
 target:setEffect(target.EFF_DAMAGE_SHIELD,5,{power=30},true)
 target:setEffect(target.EFF_CUT,5,{power=1,src=game.player},true)
 refresh()
 print('[MonsterLive] STATE SAMPLE: friendly summoned wolf; neutral fox; native physical hit, damage shield and bleeding; world turn',game.turn)
end

function M.adjacentSample()
 guard();assert(M.kind=='dense','adjacent sample requires dense scene')
 local wolf,troll
 for _,a in ipairs(M.actors) do
  if a.name=='wolf' then wolf=a elseif a.name=='forest troll' then troll=a end
 end
 assert(wolf and troll)
 local m=game.level.map
 local placed
 for _,d in ipairs{{1,0},{-1,0},{0,1},{0,-1}} do
  local x,y=troll.x+d[1],troll.y+d[2]
  if m:isBound(x,y) and m.seens(x,y) and not m:checkEntity(x,y,Map.TERRAIN,'block_move',wolf) then
   local other=m(x,y,Map.ACTOR)
   if other~=game.player then
    local ox,oy=wolf.x,wolf.y
    m:remove(ox,oy,Map.ACTOR)
    if other and other~=wolf then m:remove(x,y,Map.ACTOR);other:move(ox,oy,true) end
    wolf:move(x,y,true);placed=true;break
   end
  end
 end
 assert(placed and math.max(math.abs(wolf.x-troll.x),math.abs(wolf.y-troll.y))==1,'no adjacent fixture position')
 assert(game.player:reactionToward(wolf)>0 and game.player:reactionToward(troll)<0,'fixture relations incorrect')
 refresh()
 print('[MonsterLive] ADJACENT: friendly wolf',wolf.x,wolf.y,'enemy troll',troll.x,troll.y)
end

function M.healthSample()
 guard();assert(M.kind=='dense','health sample requires dense scene')
 local fractions={['forest-troll']=.75,['stone-troll']=.5,['cave-troll']=.25,
  wolf=.5,['great-wolf']=.1,fox=.25,['brown-bear']=1,['black-bear']=.6,
  ['brown-rat']=.05,['brown-snake']=.4,['venus-flytrap']=.2,prox=.35,bill=.8,
  ['bee-swarm']=.9,['king-cobra']=.65,['giant-eel']=.5,['dragon-turtle']=.1,
  ['dire-wolf']=.75,['white-wolf']=.5,warg=.3,['white-snake']=.65,
  rattlesnake=.7,['midge-swarm']=.35,['hornet-swarm']=.9,['white-worm-mass']=.55}
 local file=assert(fs.open('/monster-health-sample.txt','w'))
 for _,a in ipairs(M.actors) do
  local id=a._checker_token.id
  local low=a.die_at or 0
  a.life=low+(a.max_life-low)*assert(fractions[id])
  if id=='wolf' then a.faction=game.player.faction elseif id=='fox' then a.faction='neutral' end
  file:write(('%s\t%d,%d\tlife=%.4f\tmax=%.4f\tdie_at=%.4f\tfraction=%.2f\n'):format(id,a.x,a.y,a.life,a.max_life,low,fractions[id]))
 end
 file:close()
 game.log('#LIGHT_BLUE#[Health display fixture] Forest troll 75%%; stone troll 50%%; cave troll 25%%.')
 game.log('#LIGHT_BLUE#Friendly wolf 50%%; neutral fox 25%%; great wolf 10%%; rat 5%%.')
 refresh()
 print('[MonsterLive] HEALTH SAMPLE:',#M.actors,'native actors, assigned display-test health 5-100%; world turn',game.turn)
end
return M
