local _M=loadPrevious(...)
local Map=require 'engine.Map'
local Entity=require 'engine.Entity'
local Tokens=require 'mod.class.CheckerTokens'
local PlayerTokens=require 'mod.class.CheckerPlayerTokens'
local Options=require 'mod.class.CheckerOptions'

function _M:checkerTokensEnabled() return Options.tokensEnabled() end
function _M:checkerSetTokensEnabled(enabled) return Options.setTokensEnabled(enabled,self) end

function _M:checkerPlayerTokensEnabled() return Options.playerTokensEnabled() end
function _M:checkerSetPlayerTokensEnabled(enabled) return Options.setPlayerTokensEnabled(enabled,self) end

-- Party:findMember{main=true} is the birth hero, regardless of which member
-- is currently controlled. Golems, summons and thought-form copies are not.
function _M:checkerMainActor()
 local party=self.party
 return party and party.findMember and party:findMember{main=true} or nil
end

local function noModdableTiles()
 local tiles=Map.tiles
 return tiles and tiles.no_moddable_tiles and true or false
end

local function empty(value)
 return value==nil or (type(value)=='table' and next(value)==nil)
end

-- While a player token is installed, native updateModdableTilePrepare uses our
-- Entity as selfbase and leaves the actor's paper-doll add_mos stale (e.g.
-- after equipment changes). Whenever native art returns, rebuild the doll.
-- context 'update': called from Actor:updateModdableTile, which rebuilds next.
-- context 'display': called from getMapObjects inside Map:updateMap; a nested
-- updateModdableTile would re-enter updateMap, so defer to the tick end.
local pending_rebuild=setmetatable({},{__mode='k'})
local function rebuildPaperDoll(self,e,context)
 e._checker_player_rebuild=nil
 if context=='update' or not e.updateModdableTile then return end
 if context=='display' and self.onTickEnd then
  if pending_rebuild[e] then return end
  pending_rebuild[e]=true
  self:onTickEnd(function()
   pending_rebuild[e]=nil
   if not e._checker_token and e.replace_display==nil then e:updateModdableTile() end
  end)
  return
 end
 e:updateModdableTile()
end

-- Native addShaderAura/removeShaderAura call updateModdableTile themselves,
-- so a live talent/effect toggling an aura on an already-installed token
-- needs nothing from us: the 'update' context below never acts, because the
-- native call that immediately follows our wrapper rebuilds the aura using
-- whichever selfbase (self.replace_display or self) is current by then. This
-- helper only covers the two moments the engine will not revisit on its own:
-- installing a fresh token while an aura already exists (it must be rebuilt
-- onto the new Entity) and reverting to native art while an aura is still
-- active (it must reappear on the native sprite). Deferred the same way as
-- rebuildPaperDoll, for the same re-entrancy reason.
local pending_aura=setmetatable({},{__mode='k'})
local function rebuildAura(self,e,context)
 if context=='update' or not e.updateModdableTile then return end
 if context=='display' and self.onTickEnd then
  if pending_aura[e] then return end
  pending_aura[e]=true
  self:onTickEnd(function()
   pending_aura[e]=nil
   e:updateModdableTile()
  end)
  return
 end
 e:updateModdableTile()
end

-- Own only the display we installed. Transformations and other addons may
-- replace it; their display must never be overwritten by a cached original.
function _M:checkerRefreshActor(e,context)
 local state=e._checker_token
 if state and e.replace_display~=state.display then
  -- Yield to the foreign display, but remember that the doll went stale.
  if PlayerTokens.isPlayerId(state.id) then e._checker_player_rebuild=true end
  e._checker_token=nil;state=nil
 end
 local id
 if self:checkerTokensEnabled() and self.level then
  -- Production player tokens: main hero only, both switches on, verified
  -- body family with reviewed art. Anything else keeps native art.
  if self:checkerPlayerTokensEnabled() and e==self:checkerMainActor() then
   id=PlayerTokens.identify(e,state and state.display,{main=true,no_moddable=noModdableTiles()})
  end
  if not id then
   -- addMember normally converts NPC -> PartyMember, then setPlayer records
   -- that class before converting to Player. The "player" unique sentinel
   -- and the previous class persist when control returns to the main hero.
   local previous=e.__PREVIOUS_CLASSNAME
   local controlled_class=previous=='mod.class.PartyMember' or previous=='mod.class.NPC'
   local allow_player_identity=e.unique=='player' and controlled_class
    and (e.__CLASSNAME=='mod.class.Player' or e.__CLASSNAME==previous)
    and self.party and self.party:hasMember(e) and true or false
   id=Tokens.identify(e,state and state.display,allow_player_identity)
  end
 end
 if state and state.id==id then return id end
 -- true only when a token was installed just before this call (regardless of
 -- whether a different id is about to replace it below).
 local had_token=state~=nil
 if state then
  e:removeAllMOs();state.display:removeAllMOs()
  e.replace_display=state.original;e._checker_token=nil
  if PlayerTokens.isPlayerId(state.id) then e._checker_player_rebuild=true end
 end
 if id then
  local original=e.replace_display
  e:removeAllMOs()
  -- Native aura bookkeeping (_isshaderaura add_mos entries) the engine wrote
  -- directly onto the actor before this token existed. Strip it so the next
  -- updateModdableTile sees an empty add_mos on selfbase (our new Entity, not
  -- this stale table) and rebuilds the aura fresh rather than skipping it,
  -- since native code only inserts when selfbase.add_mos is still nil.
  if not empty(e.add_mos) then
   for i=#e.add_mos,1,-1 do
    if type(e.add_mos[i])=='table' and e.add_mos[i]._isshaderaura then table.remove(e.add_mos,i) end
   end
   if not next(e.add_mos) then e.add_mos=nil end
  end
  local image=PlayerTokens.isPlayerId(id) and PlayerTokens.image(id) or Tokens.image(id)
  local display=Entity.new{image=image,display='@',color={255,255,255},display_on_seen=true}
  e.replace_display=display;e._checker_token={id=id,display=display,original=original}
  e._checker_player_rebuild=nil
  -- The fresh Entity's add_mos starts empty; rebuild any active aura onto it.
  if not empty(e.shader_auras) then rebuildAura(self,e,context) end
 elseif e._checker_player_rebuild and e.replace_display==nil then
  rebuildPaperDoll(self,e,context)
 elseif had_token and e.replace_display==nil and not empty(e.shader_auras) then
  -- Reverted to native art with no doll rebuild pending (a monster token, or
  -- a player token with no_moddable/no-art reasons): let the native aura
  -- reappear on the native sprite.
  rebuildAura(self,e,context)
 end
 return id
end

function _M:checkerApplyTerrain()
 return require('mod.class.CheckerTerrain').apply(self)
end

function _M:checkerRepairTerrain(x1,y1,x2,y2)
 return require('mod.class.CheckerTerrain').repair(self,x1,y1,x2,y2)
end

-- Abashed Expanse swaps entire floating pods in its native zone on_turn.
-- That callback updates destination cells but does not call NicerTiles for
-- vacated cells. Repaint only after a pod actually relocates; gameplay and
-- the native callback run before this display-only pass.
-- S5: the Dreadfell ambush quest places its world exit with a direct map set
-- (quests/staff-absorption.lua:92-97 on the staged death, :113-118 when Ukruk
-- falls), which runs no NicerTiles pass. Display only: once the quest records
-- either outcome, repaint that level once so the exit gets its board tile.
local ambushRepainted=setmetatable({},{__mode='k'})
local onTurn=_M.onTurn
function _M:onTurn(...)
 local level=self.level
 local pods=self.zone and self.zone.short_name=='abashed-expanse' and
  level and level.pods
 local before
 if pods then
  before={}
  for i,pod in ipairs(pods) do before[i]={pod.x1,pod.y1} end
 end
 local result=onTurn(self,...)
 if before and self.level==level and self.zone.short_name=='abashed-expanse' then
  local moved=#pods~=#before
  if not moved then for i,pod in ipairs(pods) do
   if pod.x1~=before[i][1] or pod.y1~=before[i][2] then moved=true;break end
  end end
  if moved then self:checkerRepairTerrain() end
 end
 if self.level==level and level and not ambushRepainted[level] and self.zone and self.zone.short_name=='dreadfell-ambush' then
  local q=self.player and self.player.hasQuest and self.player:hasQuest('staff-absorption')
  if q and (q:isCompleted('ambush-died') or q:isCompleted('survived-ukruk')) then
   ambushRepainted[level]=true
   self:checkerRepairTerrain()
  end
 end
 return result
end

function _M:checkerRefreshVisuals()
 if not self.level or not self.level.map then return end
 local m=self.level.map
 local main=self:checkerMainActor()
 for _,e in pairs(self.level.entities or {}) do
  if e.ai or e==self.player or e==main or e._checker_token or e._checker_player_rebuild then self:checkerRefreshActor(e) end
 end
 for x=0,m.w-1 do for y=0,m.h-1 do m:updateMap(x,y) end end
 m:redisplay();m.changed=true
end

function _M:checkerApplySettings()
 self:checkerApplyTerrain()
 self:checkerRefreshVisuals()
end

-- Public compatibility API: mode now controls terrain only. Tokens have a
-- separate persisted setting; a vanilla terrain switch cannot toggle them.
function _M:checkerSetMode(mode) return Options.setTerrainMode(mode,self) end
function _M:checkerToggle()
 return self:checkerSetMode(Options.terrainMode()=='refined' and 'vanilla' or 'refined')
end
return _M
