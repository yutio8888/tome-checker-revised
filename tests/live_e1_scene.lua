-- Offline 0.6.13 fixture only. Native Trollmire birth zone (the fixture's own
-- CheckerFixture birth already lands here; no KorPul-style layout loader is
-- needed). Native level and native actors, explicitly arranged. Every arranged
-- actor is frozen with never_act; no live AI turn is claimed.
local Map=require 'engine.Map'
local Tokens=require 'mod.class.CheckerTokens'
local D=require 'engine.DamageType'
local M={actors={},rows={}}
-- The 8 new E1 identities plus two already-mapped anchors from the style brief
-- (green mold: existing amorphous immovable anchor; green worm mass: existing
-- amorphous mobile anchor). "new" means new artwork this round.
local ORDER={
 {'green mold','green-mold'},{'green worm mass','green-worm-mass'},
 {'green jelly','green-jelly'},{'black jelly','black-jelly'},
 {'white jelly','white-jelly'},{'yellow jelly','yellow-jelly'},
 {'black ooze','black-ooze'},{'yellow ooze','yellow-ooze'},
 {'red ooze','red-ooze'},{'blue ooze','blue-ooze'},
}
local NEW={['green jelly']=true,['black jelly']=true,['white jelly']=true,['yellow jelly']=true,
 ['black ooze']=true,['yellow ooze']=true,['red ooze']=true,['blue ooze']=true}
local function guard()
 assert(require('mod.class.CheckerFixture').enabled() and not profile.auth)
 assert(game.player==game.checker_hero and game.checker_staged and game.paused)
 assert(game.zone.short_name=='trollmire' and #Tokens.catalog==54)
end
local function say(text)
 M.rows[#M.rows+1]=text;print('[E1Live]',text)
 local f=assert(fs.open('/e1-validation.txt','w'))
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
function M.enter()
 guard()
 M.rows,M.actors,M.by_name={},{},{}
 local remove={};for _,a in pairs(game.level.entities) do if a.ai and a~=game.player then remove[#remove+1]=a end end
 for _,a in ipairs(remove) do game.level.map:remove(a.x,a.y,Map.ACTOR);game.level:removeEntity(a,true) end
 M.refresh()
 -- Jelly/ooze are not guaranteed in this zone's own npc_list (E1 spans 7 areas,
 -- Trollmire among them but not exclusively); load the source files directly,
 -- same pattern as evidence/e1-art-gate/native-audit.lua and tests/live_coverage.lua.
 local pool={}
 local function loadFamily(path)
  for _,p in pairs(game.zone.npc_class:loadList(path,true)) do
   if type(p)=='table' and p.name then pool[#pool+1]=p end
  end
 end
 loadFamily('/data/general/npcs/jelly.lua')
 loadFamily('/data/general/npcs/ooze.lua')
 loadFamily('/data/general/npcs/molds.lua')
 loadFamily('/data/general/npcs/vermin.lua')
 local source={};for _,p in ipairs(pool) do if not source[p.name] then source[p.name]=p end end
 local p=game.player
 for i,pair in ipairs(ORDER) do
  local name=pair[1]
  local a=game.zone:finishEntity(game.level,'actor',assert(source[name],name));a.never_act=true
  -- Target a 5 x 2 lattice around the hero, then snap to the closest observed
  -- open native floor cell; positions are arranged, not natural spawns.
  local tx=p.x+((i-1)%5)*2-4
  local ty=p.y+math.floor((i-1)/5)*3-2
  local nx,ny,score
  for x=p.x-8,p.x+8 do for y=p.y-6,p.y+6 do
   if free(x,y) then local d=(x-tx)^2+(y-ty)^2;if not score or d<score then nx,ny,score=x,y,d end end
  end end
  assert(nx,'insufficient visible native floor for '..name)
  game.zone:addEntity(game.level,a,'actor',nx,ny)
  M.actors[#M.actors+1]=a;M.by_name[name]=a
 end
 M.refresh()
 local mapped=0
 for _,pair in ipairs(ORDER) do
  local a=M.by_name[pair[1]]
  local s=a._checker_token
  assert(s and s.id==pair[2] and a._mo,pair[1]..' expected token '..pair[2])
  mapped=mapped+1
 end
 say('trollmire native-generation; '..mapped..' arranged identities ('..#ORDER..
  ' requested, 8 new E1 identities + 2 mapped style anchors)')
 M.phase='baseline';M.dump('baseline')
 game.log('#LIGHT_BLUE#E1 gel art test: 8 new jelly/ooze tokens + 2 family anchors; frozen AI.')
end
function M.mode(enabled)
 guard();game:checkerSetTokensEnabled(enabled);M.refresh()
 for _,a in ipairs(M.actors) do
  if enabled then assert(a._checker_token and a._mo,a.name..' missing token')
  else assert(not a._checker_token and not a.replace_display,a.name..' native restore failed') end
 end
end
function M.dump(phase)
 guard();local f=assert(fs.open('/e1-scene-'..phase..'.tsv','w'))
 f:write('name\tuid\tx\ty\timage\ttoken\tnew\tlife\tmax_life\tfaction\trank\tclone_on_hit\tdisplay_uid\n')
 local rules={table.concat({game.turn,game.player.x,game.player.y,game.player.life,game.player.energy.value},'\t')}
 for _,a in ipairs(M.actors) do
  local s=a._checker_token
  local values={a.name,a.uid,a.x,a.y,a.image,s and s.id or 'native',NEW[a.name] and 'new' or 'mapped',
   a.life,a.max_life,a.faction,a.rank,a.clone_on_hit and 'yes' or '',s and s.display.uid}
  local row={};for i=1,13 do row[i]=clean(values[i]) end;f:write(table.concat(row,'\t')..'\n')
  local r={};for _,key in ipairs({'uid','x','y','name','image','life','max_life','faction','rank'}) do r[#r+1]=clean(a[key]) end
  r[#r+1]=clean(a.energy.value);rules[#rules+1]=table.concat(r,'\t')
 end
 f:close();local r=assert(fs.open('/e1-rules-'..phase..'.txt','w'));r:write(table.concat(rules,'\n')..'\n');r:close()
end
-- Real native clone_on_hit split check (Actor.lua:onTakeHit, unmodified code
-- path) via the real physical damage projector (same call as tests/live_shields.lua),
-- not a mocked or hand-rolled split. `chance` is arranged to 100 on the placed
-- test actor only, so the split fires deterministically inside a paused fixture
-- instead of depending on rng.percent(30); the split logic itself is untouched.
function M.split(name)
 guard()
 local a=assert(M.by_name[name],name..' must be arranged before split test')
 assert(a.clone_on_hit,'expected native clone_on_hit contract on '..name)
 local before={};for _,e in pairs(game.level.entities) do before[e]=true end
 a.clone_on_hit.chance=100
 local need=math.ceil(a.clone_on_hit.min_dam_pct*a.max_life/100)
 local amount=math.max(1,math.min(need+2,a.life-1))
 local turn,life_before=game.turn,a.life
 D:get(D.PHYSICAL).projector(game.player,a.x,a.y,D.PHYSICAL,amount)
 assert(game.turn==turn,'native hit must not advance a world turn in the paused fixture')
 local clone
 for _,e in pairs(game.level.entities) do
  if not before[e] and e.name==a.name then clone=e end
 end
 assert(clone,'native clone_on_hit did not produce a clone actor for '..name)
 clone.never_act=true
 local cs=clone._checker_token
 assert(cs and cs.id==M.by_name[name]._checker_token.id and clone._mo,
  'clone must get its own installed token, not inherit the parent Entity')
 assert(clone._mo~=a._mo,'clone token must be an independently installed Entity, not a shared reference')
 M.clone=clone
 M.actors[#M.actors+1]=clone
 M.refresh()
 say('clone_on_hit split: '..name..' parent uid='..a.uid..' life '..life_before..'->'..a.life..
  ' dealt='..amount..' clone uid='..clone.uid..' life='..clone.life..' clone token='..cs.id..
  ' clone has own _mo='..tostring(clone._mo~=a._mo))
 return clone
end
return M
