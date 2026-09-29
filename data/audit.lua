local function snapshot()
 local m=game.level.map
 local rows={'turn='..game.turn,'hp='..game.player.life,'air='..game.player.air,'zone='..game.zone.short_name}
 for x=0,m.w-1 do for y=0,m.h-1 do
  local g=m(x,y,m.TERRAIN)
  rows[#rows+1]=table.concat({x,y,g.name,tostring((m:checkEntity(x,y,m.TERRAIN,'block_move',game.player))),tostring((m:checkEntity(x,y,m.TERRAIN,'block_sight',game.player))),tostring(g.air_level),tostring(g.air_condition),tostring(g.change_zone),tostring(g.change_level),tostring(m.seens(x,y))},':')
 end end
 local actors={}
 for _,e in pairs(game.level.entities) do if e.ai or e==game.player then actors[#actors+1]=table.concat({e.name,e.x,e.y,e.life},':') end end
 table.sort(actors)
 return table.concat(rows,'|')..table.concat(actors,'|')
end
local before=snapshot()
for _,mode in ipairs{'vanilla','blockout','refined','vanilla','refined'} do
 game:checkerSetMode(mode)
 assert(snapshot()==before,'Rules, FOV or actor state changed in '..mode)
end
local m=game.level.map
local v={deep=0,tree=0,road=0,flower=0}
for x=0,m.w-1 do for y=0,m.h-1 do if m.seens(x,y) then local g=m(x,y,m.TERRAIN)
 if g.air_level and g.air_level<0 then v.deep=v.deep+1;assert(not m:checkEntity(x,y,m.TERRAIN,'block_move',game.player));assert(not g.block_sight)
 elseif g.name=='tree' then v.tree=v.tree+1
 elseif g.road then v.road=v.road+1
 elseif g.name=='flower' then v.flower=v.flower+1 end
end end end
assert(v.deep>=10 and v.tree>0 and v.road>0,'Missing visible sample categories')
print('[CheckerRefined] AUDIT PASS', 'turn',game.turn,'visible deep',v.deep,'tree',v.tree,'road',v.road,'flower',v.flower)
for k in pairs(game.__mod_info.addons) do print('[CheckerRefined] ADDON',k) end
