local _M=loadPrevious(...)
local Terrain=require 'mod.class.CheckerTerrain'
-- S4/T1: native air bubbles are placed and removed with a direct terrain
-- addEntity and no NicerTiles pass: the bubble's own on_stand swaps in
-- WATER_FLOOR when its charges run out (data/general/grids/water.lua:106-115),
-- and a dying aquatic horror spawns bubbles around itself
-- (data/general/npcs/horror_aquatic.lua:45-58). Display only: after the native
-- call has run, re-apply board terrain around the cell when its grid actually
-- changed and the old or new grid is an exact bubble.
-- S14: the same for a forest-side exact portal placed this way (the Demon
-- Plane's return portal from Draebor's on_die, zones/demon-plane/npcs.lua:81-89).
local addEntity=_M.addEntity
function _M:addEntity(level,e,typ,x,y,...)
 local map=(typ=='terrain' or typ=='grid') and x and y and level and level.map
 if not (map and game and game.level==level) then return addEntity(self,level,e,typ,x,y,...) end
 local before=map(x,y,map.TERRAIN)
 local result=addEntity(self,level,e,typ,x,y,...)
 local after=map(x,y,map.TERRAIN)
 if game.level==level and after~=before and game.checkerRepairTerrain and
  (Terrain.underwaterKind(before)=='bubble' or Terrain.underwaterKind(after)=='bubble' or Terrain.s14ForestKind(after)) then
  game:checkerRepairTerrain(x-1,y-1,x+1,y+1)
 end
 return result
end
return _M
