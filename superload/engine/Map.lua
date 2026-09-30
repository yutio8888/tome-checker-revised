local _M=loadPrevious(...)
local Terrain=require 'mod.class.CheckerTerrain'
local Options=require 'mod.class.CheckerOptions'
local updateMap=_M.updateMap
local function active(m)
 return game and game.level and game.level.map==m and Terrain.variant(game.zone) and (Terrain.ready() or Terrain.mazeAssets.ready or m._checker_korpul)
end
function _M:updateMap(x,y)
 -- S11, display only: a board-drawn lever's native block_move switched its MO
 -- (lever1_state1/2) and asked for this updateMap; its board display is
 -- rebuilt once the callback has finished (CheckerTerrain.s11Repaint).
 if x and y and x>=0 and y>=0 and x<self.w and y<self.h and game and game.level and game.level.map==self and
  Terrain.s11Stale(self,x,y) then Terrain.s11Repaint(self,x,y) end
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
-- S11, display only: after a native on_lever_change (a lever pull reaching a
-- lever door) swapped the terrain, re-apply the board around that cell.
local checkEntity=_M.checkEntity
function _M:checkEntity(x,y,pos,what,...)
 if what~='on_lever_change' or pos~=self.TERRAIN or not (game and game.level and game.level.map==self) then
  return checkEntity(self,x,y,pos,what,...)
 end
 local before=self(x,y,pos)
 local result=checkEntity(self,x,y,pos,what,...)
 if before and self(x,y,pos)~=before then Terrain.s11Changed(self,x,y,before) end
 return result
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
