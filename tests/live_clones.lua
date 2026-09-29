-- Reproduce the inherited nested-MO bug with actual native cloning APIs.
local Map=require 'engine.Map'
local Fixture=require 'mod.class.CheckerFixture'
local M={}
function M.run()
 assert(Fixture.enabled() and not profile.auth and game.checker_staged)
 assert(game.player==game.checker_hero and game:checkerTokensEnabled())
 local source
 for _,a in pairs(game.zone.npc_list) do if a.name=='wolf' and not a.unique then source=a;break end end
 local actors={}
 local map,turn=game.level.map,game.turn
 local function place(a)
  for dy=-4,4 do for dx=-5,5 do
   local x,y=game.player.x+dx,game.player.y+dy
   if map:isBound(x,y) and map.seens(x,y) and not map(x,y,Map.ACTOR)
    and map(x,y,Map.TERRAIN).subtype~='water' and not map:checkEntity(x,y,Map.TERRAIN,'block_move',a) then
    a.never_act=true;actors[#actors+1]=a;game.zone:addEntity(game.level,a,'actor',x,y)
    map:updateMap(x,y);core.display.forceRedraw();assert(a._mo and a._checker_token.overlay._mo)
    return
   end
  end end
  error('no visible land for clone audit')
 end
 local rows={}
 local ok,err=xpcall(function()
  local parent=game.zone:finishEntity(game.level,'actor',assert(source));place(parent)
  local body,display,overlay=parent._mo,parent._checker_token.display,parent._checker_token.overlay
  for _,method in ipairs{'cloneActor','clone','cloneFull'} do
   local child=parent[method](parent)
   assert(child~=parent and child.uid~=parent.uid and not child._checker_token and not child.replace_display)
   assert(not child._mo and not child._last_mo,'inherited parent map object survived clone')
   assert(parent._mo==body and display._mo==body and parent._checker_token.overlay==overlay,'clone changed parent cache')
   place(child)
   assert(child._checker_token.id=='wolf' and child._checker_token.display~=display and child._mo~=body)
   assert(child._checker_token.overlay~=overlay and child._checker_token.overlay._mo~=overlay._mo)
   assert(child.life==parent.life and child.rank==parent.rank and child.image==parent.image,'visual rebuild changed actor rules')
   rows[#rows+1]=method..': distinct body/display/overlay; parent cache retained; native life/rank/image unchanged'
  end
 end,debug.traceback)
 for _,a in ipairs(actors) do
  if map(a.x,a.y,Map.ACTOR)==a then map:remove(a.x,a.y,Map.ACTOR) end
  game.level:removeEntity(a,true)
 end
 game.player:playerFOV();map:redisplay();game.paused=true
 assert(game.turn==turn)
 if not ok then error(err,0) end
 local f=assert(fs.open('/clone-after.txt','w'));f:write(table.concat(rows,'\n')..'\n');f:close()
 print('[CloneLive] PASS',table.concat(rows,'; '))
 return true
end
return M
