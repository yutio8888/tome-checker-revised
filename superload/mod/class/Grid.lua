local _M=loadPrevious(...)
local Terrain=require 'mod.class.CheckerTerrain'
local loadList=_M.loadList
function _M:loadList(file,no_default,res,mod,loaded)
 local first=res and #res or 0
 local result=loadList(self,file,no_default,res,mod,loaded)
 if file=='/data/general/grids/basic.lua' or file=='/data/zones/maze/grids.lua' or
  file=='/data/general/grids/underground_gloomy.lua' or
  file=='/data/general/grids/underground_dreamy.lua' or
  file=='/data/general/grids/cave.lua' or
  file=='/data/general/grids/crystal.lua' or
  file=='/data/general/grids/burntland.lua' or
  file=='/data/general/grids/lava.lua' or
  file=='/data/general/grids/void.lua' or
  file=='/data/general/grids/water.lua' or
  file=='/data/general/grids/sand.lua' or
  file=='/data/general/grids/forest.lua' or
  file=='/data/general/grids/jungle.lua' or
  file=='/data/general/grids/fortress.lua' or
  file=='/data/general/grids/bone.lua' or
  file=='/data/zones/valley-moon-caverns/grids.lua' or
  file=='/data/zones/keepsake-meadow/grids.lua' or
  file=='/data/zones/south-beach/grids.lua' or
  file=='/data/zones/conclave-vault/grids.lua' or
  file=='/data/zones/last-hope-graveyard/grids.lua' or
  file=='/data/zones/unhallowed-morass/grids.lua' or
  file=='/data/zones/heart-gloom/grids.lua' or
  file=='/data/zones/old-forest/grids.lua' or
  -- S1: Trollmire's own BOGWATER/BOGTREE definitions (aura bog water).
  file=='/data/zones/trollmire/grids.lua' or
  -- TW1: town zone lists. Their nested basic/forest/water imports keep their
  -- general-file stamps; the outer call adds the exact town provenance.
  file=='/data/zones/town-derth/grids.lua' or
  file=='/data/zones/town-lumberjack-village/grids.lua' or
  -- TW2: Last Hope (also stamps its nested mountain.lua import) and Elvala.
  file=='/data/zones/town-last-hope/grids.lua' or
  file=='/data/zones/town-elvala/grids.lua' or
  -- TW3: Zigur, Angolwen (also stamps its nested mountain.lua import; the
  -- TMX map's ids resolve through this list) and the Iron Council.
  file=='/data/zones/town-zigur/grids.lua' or
  file=='/data/zones/town-angolwen/grids.lua' or
  file=='/data/zones/town-iron-council/grids.lua' or
  -- TW4: Shatur (also stamps its nested elven_forest/snowy_forest/mountain
  -- imports) and Point Zero (nested void.lua keeps its general stamp too).
  file=='/data/zones/town-shatur/grids.lua' or
  file=='/data/zones/town-point-zero/grids.lua' or
  -- TW5: Gates of Morning (stamps its nested basic/forest/mountain/water/sand
  -- imports; each keeps its general-file stamp too).
  file=='/data/zones/town-gates-of-morning/grids.lua' or
  -- TW6: Irkkk (stamps its nested basic/jungle/jungle_hut/water imports;
  -- jungle.lua and water.lua keep their general-file stamps too).
  file=='/data/zones/town-irkkk/grids.lua' or
  -- S5: zone lists whose own definitions get exact board identities
  -- (Tannen's reversed stairs, the valley's moonstones and Fearscape portals,
  -- the Ring of Blood's lava pits). Nested imports keep their general stamps.
  file=='/data/zones/tannen-tower/grids.lua' or
  file=='/data/zones/valley-moon/grids.lua' or
  file=='/data/zones/ring-of-blood/grids.lua' or
  -- S6: Eruan and Gorbat Pride (nested imports keep their general stamps).
  file=='/data/zones/eruan/grids.lua' or
  file=='/data/zones/gorbat-pride/grids.lua' or
  -- S9: High Peak (its nested basic/cave imports keep their general stamps;
  -- its two next-level stairs get the S2 stamp).
  file=='/data/zones/high-peak/grids.lua' or
  -- S2: zone lists defining reviewed exits, locks and props (Iron Council
  -- exits, Elven Ruins teleport circle, Kryl-Feijan locks and symbols,
  -- lore posts). Only their own spec ids get the S2 stamp.
  file=='/data/zones/reknor-escape/grids.lua' or
  file=='/data/zones/deep-bellow/grids.lua' or
  file=='/data/zones/ancient-elven-ruins/grids.lua' or
  file=='/data/zones/crypt-kryl-feijan/grids.lua' or
  file=='/data/zones/dreadfell/grids.lua' or
  file=='/data/zones/reknor/grids.lua' or
  file=='/data/zones/ruined-dungeon/grids.lua' or
  -- T16: callback altars (Spellblaze L2 corrupting altar, Caldera altar of dreams).
  file=='/data/zones/mark-spellblaze/grids.lua' or
  file=='/data/zones/noxious-caldera/grids.lua' then
  for i=first+1,#result do Terrain.markSource(result[i],file) end
 end
 -- Old Forest CRYSTALINE's crystaline-forest event loads its own copy of
 -- underground.lua. Record that exact native caller on the crystal.lua
 -- definitions it receives; an overridden or foreign event stays unstamped.
 if file=='/data/general/grids/underground.lua' then
  for level=2,4 do
   local info=debug.getinfo(level,'S')
   if not info then break end
   if type(info.source)=='string' and info.source:match('^@?/data/general/events/crystaline%-forest%.lua$') then
    for i=first+1,#result do Terrain.markCrystalOrigin(result[i],'crystaline-forest') end
    break
   end
  end
 end
 return result
end
-- TW6: a native door opening (mod/class/Grid.lua:60-88) swaps the terrain
-- in place without a NicerTiles pass, so a board-drawn door would keep its
-- closed-door display. Display only: after the native call has run and
-- returned, re-apply board terrain around a cell whose grid it replaced
-- (the same repair NicerTiles:updateAround triggers).
local blockMove=_M.block_move
function _M:block_move(x,y,e,act,couldpass)
 if not (act and self.door_opened and game and game.level and game.level.map) then return blockMove(self,x,y,e,act,couldpass) end
 local level=game.level
 local before=level.map(x,y,level.map.TERRAIN)
 local result=blockMove(self,x,y,e,act,couldpass)
 if game.level==level and level.map(x,y,level.map.TERRAIN)~=before and game.checkerRepairTerrain then
  game:checkerRepairTerrain(x-1,y-1,x+1,y+1)
 end
 return result
end
local getMapObjects=_M.getMapObjects
function _M:getMapObjects(tiles,mos,z)
 local ctx=Terrain.context()
 local replacement=ctx and ctx.grid==self and Terrain.render(ctx.map,ctx.x,ctx.y,self,ctx.mode)
 if not replacement then return getMapObjects(self,tiles,mos,z) end
 replacement:getMapObjects(tiles,mos,z)
 -- Native Grid prototypes can be shared between cells. Keep their own native
 -- cache intact after Map.updateMap finishes, including exceptional exits.
 if not ctx.native_cache then ctx.native_cache={mo=self._mo,last_mo=self._last_mo} end
 -- Native minimap setup still receives the actual Grid and its rules.
 self._mo=replacement._mo;self._last_mo=replacement._last_mo
end
return _M
