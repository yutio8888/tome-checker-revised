-- Offline 0.6.9 fixture only. Native level and native actors, explicitly arranged.
-- No live AI turn is claimed: every actor is frozen with never_act.
local Map=require 'engine.Map'
local Tokens=require 'mod.class.CheckerTokens'
local M={actors={},rows={}}
-- Nine new C0b identities plus the already mapped same-family anchors they must
-- stay separable from. Order fixes the on-screen layout: each new token sits
-- immediately next to the mapped relative it is most likely to be confused with.
local ORDER={
 {'giant white rat','giant-white-rat'},{'giant white mouse','giant-white-mouse'},
 {'giant brown rat','brown-rat'},{'giant brown mouse','giant-brown-mouse'},
 {'giant grey rat','giant-grey-rat'},{'giant grey mouse','giant-grey-mouse'},
 {'giant rabbit','giant-rabbit'},{'giant crystal rat','giant-crystal-rat'},
 {'grey mold','grey-mold'},{'brown mold','brown-mold'},
 {'green mold','green-mold'},{'shining mold','shining-mold'},
}
local NEW={['giant white mouse']=true,['giant brown mouse']=true,['giant grey mouse']=true,
 ['giant rabbit']=true,['giant crystal rat']=true,['brown mold']=true,['green mold']=true,
 ['shining mold']=true}
local function guard()
 assert(require('mod.class.CheckerFixture').enabled() and not profile.auth)
 assert(game.player==game.checker_hero and game.checker_staged and game.paused)
 assert(game.zone.short_name=='ruins-kor-pul' and #Tokens.catalog==45)
end
local function say(text)
 M.rows[#M.rows+1]=text;print('[C0bLive]',text)
 local f=assert(fs.open('/c0b-validation-'..M.layout:lower()..'.txt','w'))
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
function M.enter(layout,seed)
 local sc=dofile('/data-checker-fixture/monster-live_korpul_scene.lua')
 sc.enter(layout,seed);sc.stage();sc.dismissFixturePrompts()
 M.layout,M.seed,M.rows,M.actors,M.by_name=layout,seed,{},{},{}
 guard()
 local remove={};for _,a in pairs(game.level.entities) do if a.ai and a~=game.player then remove[#remove+1]=a end end
 for _,a in ipairs(remove) do game.level.map:remove(a.x,a.y,Map.ACTOR);game.level:removeEntity(a,true) end
 M.refresh()
 local source={};for _,p in pairs(game.zone.npc_list) do if type(p)=='table' and p.name then source[p.name]=source[p.name] or p end end
 local p=game.player
 for i,pair in ipairs(ORDER) do
  local name=pair[1]
  local a=game.zone:finishEntity(game.level,'actor',assert(source[name],name));a.never_act=true
  -- Target a 7 x 2 lattice around the hero, then snap to the closest observed
  -- open native floor cell; positions are arranged, not natural spawns.
  local tx=p.x+((i-1)%7)*2-6
  local ty=p.y+math.floor((i-1)/7)*3-2
  local nx,ny,score
  for x=p.x-7,p.x+7 do for y=p.y-5,p.y+5 do
   if free(x,y) then local d=(x-tx)^2+(y-ty)^2;if not score or d<score then nx,ny,score=x,y,d end end
  end end
  assert(nx,'insufficient visible native floor for '..name)
  game.zone:addEntity(game.level,a,'actor',nx,ny)
  M.actors[#M.actors+1]=a;M.by_name[name]=a
 end
 M.refresh()
 local mapped,stealthy=0,{}
 for _,pair in ipairs(ORDER) do
  local a=M.by_name[pair[1]]
  local s=a._checker_token
  assert(s and s.id==pair[2] and a._mo,pair[1]..' expected token '..pair[2])
  mapped=mapped+1
  -- Native stealth is honoured by the integration: a hidden actor is not drawn.
  -- Record it instead of asserting visibility.
  if a:attr('stealth') and a:attr('stealth')>0 then stealthy[#stealthy+1]=a.name end
 end
 -- Real still-unmapped family members must keep native art. "skeleton warrior"
 -- passed the C0b admission gate but its art exhausted the two-call budget, so it
 -- is deliberately uncovered; "armoured skeleton warrior" was never in this batch.
 for _,name in ipairs({'skeleton warrior','armoured skeleton warrior'}) do
  local u=game.zone:finishEntity(game.level,'actor',assert(source[name],name))
  assert(not game:checkerRefreshActor(u) and not u.replace_display,name..' must stay native')
 end
 say(layout..' native-generation seed='..seed..'; '..mapped..' arranged identities ('..#ORDER..
  ' requested, 8 new C0b + 4 mapped anchors); uncovered skeleton warrior and armoured skeleton warrior'..
  ' fallback PASS; stealthed='..(#stealthy>0 and table.concat(stealthy,',') or 'none'))
 M.phase='baseline';M.dump('baseline')
 game.log('#LIGHT_BLUE#C0b art test: %s; 8 new tokens + 4 family references; frozen AI.',layout)
end
function M.mode(enabled)
 guard();game:checkerSetTokensEnabled(enabled);M.refresh()
 for _,a in ipairs(M.actors) do
  if enabled then assert(a._checker_token and a._mo,a.name..' missing token')
  else assert(not a._checker_token and not a.replace_display,a.name..' native restore failed') end
 end
end
function M.dump(phase)
 guard();local f=assert(fs.open('/c0b-scene-'..M.layout:lower()..'-'..phase..'.tsv','w'))
 f:write('name\tuid\tx\ty\timage\ttoken\tnew\tlife\tmax_life\tfaction\trank\tnever_move\tstealth\tdisplay_uid\n')
 local rules={table.concat({game.turn,game.player.x,game.player.y,game.player.life,game.player.energy.value},'\t')}
 for _,a in ipairs(M.actors) do
  local s=a._checker_token
  local values={a.name,a.uid,a.x,a.y,a.image,s and s.id or 'native',NEW[a.name] and 'new' or 'mapped',
   a.life,a.max_life,a.faction,a.rank,a.never_move,a:attr('stealth'),s and s.display.uid}
  local row={};for i=1,14 do row[i]=clean(values[i]) end;f:write(table.concat(row,'\t')..'\n')
  local r={};for _,key in ipairs({'uid','x','y','name','image','life','max_life','faction','rank'}) do r[#r+1]=clean(a[key]) end
  r[#r+1]=clean(a.energy.value);rules[#rules+1]=table.concat(r,'\t')
 end
 f:close();local r=assert(fs.open('/c0b-rules-'..M.layout:lower()..'-'..phase..'.txt','w'));r:write(table.concat(rules,'\n')..'\n');r:close()
end
return M
