-- Offline display-only legend: six copies of the SAME native wolf with
-- explicit debug rank assignments. This does not modify the NPC generator.
local Map=require 'engine.Map'
local S=require 'mod.class.CheckerTokenStyle'
local M={}
function M.setup()
 assert(config.settings.cheat and config.settings.disable_all_connectivity and not profile.auth)
 assert(__module_extra_info.checker_demo and game.checker_staged and game.checker_mode=='refined')
 local m,p=game.level.map,game.player
 local old={};for _,a in pairs(game.level.entities) do if a~=p and a.ai then old[#old+1]=a end end
 for _,a in ipairs(old) do m:remove(a.x,a.y,Map.ACTOR);game.level:removeEntity(a,true) end
 local bx,by
 for y=p.y-3,p.y+2 do
  for x=p.x-5,p.x do
   local ok=true
   for i=0,5 do
    if not m:isBound(x+i,y) or not m.seens(x+i,y) or m(x+i,y,Map.ACTOR)
     or m:checkEntity(x+i,y,Map.TERRAIN,'block_move',p) then ok=false;break end
   end
   if ok then bx,by=x,y;break end
  end
  if bx then break end
 end
 assert(bx,'no six visible walkable cells for the rank legend')
 local proto
 for _,a in pairs(game.zone.npc_list) do if a.name=='wolf' and not a.unique then proto=a;break end end
 assert(proto)
 local ranks={2,3,3.2,3.5,4,5};local names={'normal','elite','rare','unique','boss','elite boss'}
 M.actors={}
 local f=assert(fs.open('/rank-display-sample.txt','w'))
 for i,rank in ipairs(ranks) do
  local a=game.zone:finishEntity(game.level,'actor',proto)
  a.rank=rank;a.never_act=true
  game.zone:addEntity(game.level,a,'actor',bx+i-1,by)
  assert(game:checkerRefreshActor(a)=='wolf')
  local label=a:textRank();assert(label==names[i],label)
  f:write(('%d %s native_rank=%s badge=%s cell=%d,%d\n'):format(i,label,tostring(rank),S.rankBadge(rank) or 'none',a.x,a.y))
  M.actors[i]=a
 end
 f:close();p:playerFOV();m:centerViewAround(p.x,p.y);m:redisplay();game.paused=true
 game.log('#ANTIQUE_WHITE#Rank legend, left to right: normal | elite | rare | unique | boss | elite boss.')
 print('[RankLegend] PASS: six native textRank labels and token badges; debug rank assignments, frozen AI')
end
return M
