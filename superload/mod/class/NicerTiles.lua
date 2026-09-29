local _M=loadPrevious(...)

-- Re-apply board terrain after native re-tiling; see CheckerTerrain.repair.
-- Only the current level is ours to repaint.
local function repair(level,x1,y1,x2,y2)
 if game and game.level==level and game.checkerRepairTerrain then game:checkerRepairTerrain(x1,y1,x2,y2) end
end

local updateAround=_M.updateAround
function _M:updateAround(level,x,y)
 local ret=updateAround(self,level,x,y)
 repair(level,x-2,y-2,x+2,y+2)
 return ret
end

local postProcessLevelTiles=_M.postProcessLevelTiles
function _M:postProcessLevelTiles(level)
 local ret=postProcessLevelTiles(self,level)
 repair(level)
 return ret
end

local postProcessLevelTilesOnLoad=_M.postProcessLevelTilesOnLoad
function _M:postProcessLevelTilesOnLoad(level)
 local ret=postProcessLevelTilesOnLoad(self,level)
 repair(level)
 return ret
end
return _M
