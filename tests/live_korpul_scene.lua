-- Disposable offline fixture. Native zone generation, explicit forced variant,
-- deterministic input seed; arranged actors are not natural spawn evidence.
local Map=require 'engine.Map'
local M={actors={}}
local function guard()
 assert(require('mod.class.CheckerFixture').enabled() and not profile.auth)
 assert(game.checker_staged and game.player==game.checker_hero)
end
function M.enter(layout,seed)
 guard();assert(layout=='DEFAULT' or layout=='HIDEOUT')
 config.settings.tome.quest_popup=false -- disposable fixture setting, not saved
 if game.zone.temp_shift_zone then
  game:changeLevel(1,'useless',{temporary_zone_shift_back=true,direct_switch=true})
 end
 local Z=require 'engine.Zone'
 Z:removeLastPersistZone('ruins-kor-pul')
 local alternate,load=game.state.alternateZone,savefile_pipe.doLoad
 game.state.alternateZone=function(self,name,...)
  if name=='ruins-kor-pul' then return layout end
  return alternate(self,name,...)
 end
 savefile_pipe.doLoad=function(self,save,kind,arg,id,...)
  if kind=='zone' and id=='ruins-kor-pul' then return nil end
  return load(self,save,kind,arg,id,...)
 end
 rng.seed(seed)
 local ok,z=pcall(function() return require('mod.class.Zone').new('ruins-kor-pul') end)
 game.state.alternateZone,savefile_pipe.doLoad=alternate,load
 assert(ok,z)
 assert((z.is_hideout and 'HIDEOUT' or 'DEFAULT')==layout,'fresh zone variant mismatch')
 game:changeLevel(1,z,{temporary_zone_shift=true,direct_switch=true})
 M.layout,M.seed,M.actors=layout,seed,{}
 assert(game.zone==z)
 local f=assert(fs.open('/korpul-natural-'..layout:lower()..'.tsv','w'))
 f:write('name\tx\ty\trank\timage\ttoken\n')
 for _,a in pairs(game.level.entities) do if a.ai then
  a.never_act=true
  f:write(table.concat({a.name,tostring(a.x),tostring(a.y),tostring(a.rank),tostring(a.image),a._checker_token and a._checker_token.id or 'native'},'\t')..'\n')
 end end
 f:close();game.paused=true
 print('[KorPulScene] native generation',layout,'seed',seed,'level',game.level.level)
end
function M.dismissFixturePrompts()
 guard()
 for i=#game.dialogs,1,-1 do
  local d=game.dialogs[i]
  assert(d.__CLASSNAME=='mod.dialogs.Chat' or d.__CLASSNAME=='mod.dialogs.QuestPopup',
   'unexpected dialog must be inspected: '..tostring(d.__CLASSNAME))
  game:unregisterDialog(d)
 end
 game.bignews.list=nil
 game.flyers:empty() -- clear transient level-entry text equally in both art modes
end
local function passable(m,x,y)
 if not m:isBound(x,y) then return false end
 local g=m(x,y,Map.TERRAIN)
 -- Keep the art samples off stairs/exits; those intentionally retain native art.
 return g and not g.change_level and not g.change_zone
  and require('mod.class.CheckerTerrain').classify(g)=='floor'
  and not m:checkEntity(x,y,Map.TERRAIN,'block_move',game.player)
end
function M.refresh()
 local m=game.level.map
 game.player:playerFOV();m.smooth_scroll=0;m:centerViewAround(game.player.x,game.player.y)
 m:redisplay();m.changed=true;game.player.changed=true;game.paused=true
 if game.uiset.npcs_display.refresh then game.uiset.npcs_display:refresh() end
end
function M.stage()
 guard();assert(game.zone.short_name=='ruins-kor-pul')
 local m=game.level.map
 local bx,by,best
 for x=6,m.w-7 do for y=6,m.h-7 do if passable(m,x,y) then
  local area,doors,walls=0,0,0
  for dx=-4,4 do for dy=-3,3 do
   local g=m(x+dx,y+dy,Map.TERRAIN)
   if passable(m,x+dx,y+dy) then area=area+1
   elseif g and g.door_opened then doors=doors+1
   else walls=walls+1 end
  end end
  local center=0
  for dx=-2,2 do for dy=-1,1 do if passable(m,x+dx,y+dy) then center=center+1 end end end
  local score=area+math.min(doors,2)*8+math.min(walls,16)+center*2
  if center>=13 and (not best or score>best) then bx,by,best=x,y,score end
 end end end
 assert(bx,'no suitable native room')
 local old={}
 for _,a in pairs(game.level.entities) do if a.ai and a~=game.player then old[#old+1]=a end end
 for _,a in ipairs(old) do m:remove(a.x,a.y,Map.ACTOR);game.level:removeEntity(a,true) end
 game.player:move(bx,by,true);game.player.sight=20;M.refresh()
 local names={'degenerated skeleton warrior','degenerated skeleton archer','skeleton mage','grey mold'}
 if M.layout=='HIDEOUT' then names[#names+1]='cutpurse';names[#names+1]='bandit' end
 local source={};for _,p in pairs(game.zone.npc_list) do if p.name then source[p.name]=p end end
 M.actors={}
 for i,name in ipairs(names) do
  local a=game.zone:finishEntity(game.level,'actor',assert(source[name],name))
  a.never_act=true
  local dx=((i-1)%3-1)*2;local dy=math.floor((i-1)/3)*2-1
  local nx,ny,score
  for x=bx-4,bx+4 do for y=by-3,by+3 do
   if passable(m,x,y) and m.seens(x,y) and not m(x,y,Map.ACTOR) then
    local d=(x-bx-dx)^2+(y-by-dy)^2
    if not score or d<score then nx,ny,score=x,y,d end
   end
  end end
  assert(nx,'not enough observed open cells')
  game.zone:addEntity(game.level,a,'actor',nx,ny);game:checkerRefreshActor(a)
  M.actors[#M.actors+1]=a
 end
 game.log('#LIGHT_BLUE#Kor\'Pul art test: %s; arranged native actors; frozen AI.',M.layout)
 M.refresh()
 local f=assert(fs.open('/korpul-scene-'..M.layout:lower()..'.tsv','w'))
 f:write('name\tx\ty\timage\ttoken\n')
 for _,a in ipairs(M.actors) do f:write(table.concat({a.name,tostring(a.x),tostring(a.y),a.image,a._checker_token and a._checker_token.id or 'native'},'\t')..'\n') end
 f:close()
 print('[KorPulScene] arranged',M.layout,'seed',M.seed,'center',bx,by,'actors',#M.actors)
 M.dismissFixturePrompts()
end
return M
