local _M=loadPrevious(...)
local Terrain=require 'mod.class.CheckerTerrain'
local Options=require 'mod.class.CheckerOptions'
local updateMap=_M.updateMap
local function active(m)
 return game and game.level and game.level.map==m and Terrain.variant(game.zone) and (Terrain.ready() or Terrain.mazeAssets.ready or m._checker_korpul)
end
function _M:updateMap(x,y)
 if not active(self) or not x or not y or x<0 or y<0 or x>=self.w or y>=self.h then return updateMap(self,x,y) end
 local g=self(x,y,self.TERRAIN)
 local changed=Terrain.observe(self,x,y,g)
 Terrain.withContext({map=self,x=x,y=y,grid=g,mode=Options.terrainMode()},updateMap,self,x,y)
 if changed and not self._checker_updating_neighbors then
  self._checker_updating_neighbors=true
  local ok,err=pcall(function()
   for dx=-1,1 do for dy=-1,1 do
    if (dx~=0 or dy~=0) and Terrain.visible(self,x+dx,y+dy) then self:updateMap(x+dx,y+dy) end
   end end
  end)
  self._checker_updating_neighbors=nil
  if not ok then error(err,0) end
 end
end
-- Native FOV callbacks remain authoritative; refresh only terrain actually seen.
for _,name in ipairs{'apply','applyLite','applyExtraLite'} do
 local base=_M[name]
 _M[name]=function(self,x,y,...)
  local result=base(self,x,y,...)
  if active(self) and Terrain.visible(self,x,y) then self:updateMap(x,y) end
  return result
 end
end
return _M
