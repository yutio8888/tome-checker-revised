local _M=loadPrevious(...)
local Style=require 'mod.class.CheckerTokenStyle'
local Entity=require 'engine.Entity'
local Options=require 'mod.class.CheckerOptions'
-- Keep this one-rebuild hint outside the serialized actor/clone graph.
local restore_facing=setmetatable({},{__mode='k'})
-- Save ownership alongside replace_display so both references survive a
-- native actor save/load graph. Otherwise our own display looks foreign.

-- Cloning is different from loading a save: native clone/cloneActor copy
-- nested Entity map-object userdata. A child must build its own token, not
-- invalidate or reuse the parent's body/overlay and their callbacks.
local cloned=_M.cloned
function _M:cloned(src,...)
 local result=cloned(self,src,...)
 local state=self._checker_token
 if state then
  if self.replace_display==state.display then self.replace_display=state.original end
  -- A copied player doll may be stale (native rebuilds skip it under a token).
  if type(state.id)=='string' and state.id:sub(1,7)=='player:' then self._checker_player_rebuild=true end
  self._checker_token=nil
  self._mo,self._last_mo=nil,nil
 end
 return result
end

-- Refresh when the engine rebuilds a display, including newly spawned actors
-- and image-changing transformations. Reuse Entity objects while unchanged.
local getMapObjects=_M.getMapObjects
function _M:getMapObjects(tiles,mos,z)
 if game and game.checkerRefreshActor then game:checkerRefreshActor(self,'display') end
 -- Native updateModdableTilePrepare builds the shader-aura add_mos and calls
 -- updateMap from inside its own body, so any later hook is too late for the
 -- map objects. Rewrite the aura here, immediately before makeMapObject reads
 -- the display Entity's add_mos. Idempotent.
 self:checkerStandeeAura()
 local state=self._checker_token
 if state and self.replace_display==state.display then
  -- Every owned token, including the fixture demonstration piece, uses the
  -- single board-piece diameter. A separate constant for the demo token would
  -- reintroduce exactly the mismatched sizes this unification removes.
  local scale=Style.scale(self.size_category,game.level.map.tile_w)
  if state.scale~=scale then
   self:removeAllMOs();state.display:removeAllMOs()
   state.scale=scale
   state.display.display_w=scale;state.display.display_h=scale
   state.display.display_x=(1-scale)/2;state.display.display_y=(1-scale)/2
  end
  -- The actor callback preserves particles/speech and substitutes only the
  -- identified shield visuals and native rank ornaments below.
  -- A separate actor-layer object draws tactical UI AFTER those effects.
  -- Shield/rank styling stays local to owned tokens; shaders remain enabled.
  if not state.overlay then
   state.overlay=Entity.new{image='invis.png',display=' ',color={255,255,255},display_on_seen=true}
  end
 end
 local result=getMapObjects(self,tiles,mos,z)
 if (state and self.replace_display==state.display) or restore_facing[self] then
  -- Rebuilt map objects start unflipped. Retain the native facing intent even
  -- when fixed token art temporarily ignores it, including native fallback.
  self:MOflipX(self._flipx or false)
  restore_facing[self]=nil
 end
 if state and self.replace_display==state.display then
  -- Map reserves z..z+2 for actors. A covered token has one body object;
  -- leave any unexpected third-party layer alone and use the early path.
  state.overlay_active=not mos[z+1]
  if state.overlay_active then
   local mo=state.overlay:makeMapObject(tiles,1)
   local weak=setmetatable({self},{__mode='v'})
   mo:displayCallback(function(x,y,w,h,zoom,on_map,tlx,tly)
    local actor=weak[1]
    local s=actor and actor._checker_token
    if s and s.overlay_active and actor.replace_display==s.display and on_map
     and game.level and game.level.map then
     local scale=s.scale or 1
     -- Overlay has no inset: x/y are the animated full-cell origin, including
     -- twitch. Use them so all state follows the lifted disk as one piece.
     -- The ring was drawn under the creature by the body callback. A native
     -- shader-aura add_mos (e.g. the phoenix's body_of_fire) is chained to the
     -- body object and drawn after the body callback, so the layered creature
     -- must be drawn here, above that aura, or the aura's disc-shaped copy
     -- covers it. Then the rank badge and native life bar go on top.
     if s.layered then actor:checkerLayerCreature(game.level.map,x,y,w*scale,h*scale) end
     actor:checkerTacticalFrame(game.level.map,x,y,w*scale,h*scale,game.always_target,'badge')
    end
    return true
   end)
   mos[z+1]=mo
  end
 end
 return result
end

local removeAllMOs=_M.removeAllMOs
function _M:removeAllMOs(no_invalidate)
 local s=self._checker_token
 if s and self.replace_display==s.display and self._flipx~=nil then restore_facing[self]=true end
 if s and s.overlay then s.overlay:removeAllMOs(no_invalidate) end
 return removeAllMOs and removeAllMOs(self,no_invalidate)
end

local MOflipX=_M.MOflipX
function _M:MOflipX(value)
 local result=MOflipX and MOflipX(self,value)
 local s=self._checker_token
 if s and self.replace_display==s.display and self._mo then
  local fixed=Options and Options.tokenFacing and Options.tokenFacing()=='fixed'
  if fixed then
   -- Native _flipx remains the last requested direction, for switching back.
   -- Flip only the owned body; tactical arcs never mirror with the artwork.
   self._mo:flipX(false)
  end
  -- Native facing flips the whole body MO chain (src/map.c do_quad), which
  -- mirrors the chained shader aura about its own box centre. The overlay
  -- creature is a separate MO the engine never flips, so record the applied
  -- body flip here and mirror the overlay by the same transform, keeping the
  -- creature and its aura aligned. With fixed facing the body stays unflipped.
  s.body_flip=(not fixed) and (value and true or false) or false
 end
 return result
end

local setMoveAnim=_M.setMoveAnim
function _M:setMoveAnim(oldx,oldy,speed,blur,twitch_dir,twitch,...)
 local result=setMoveAnim(self,oldx,oldy,speed,blur,twitch_dir,twitch,...)
 local s=self._checker_token
 if s and s.overlay and self.replace_display==s.display then
  s.overlay.x,s.overlay.y=self.x,self.y
  -- State belongs to the current interpolated piece only. Native motion
  -- blur redraws callbacks at historical positions, which would duplicate
  -- health/shield/rank UI. Keep body trails and the shared trajectory intact.
  s.overlay:setMoveAnim(oldx,oldy,speed,0,twitch_dir,twitch,...)
 end
 return result
end

local resetMoveAnim=_M.resetMoveAnim
function _M:resetMoveAnim(...)
 local result=resetMoveAnim(self,...)
 local s=self._checker_token
 if s and s.overlay and self.replace_display==s.display then s.overlay:resetMoveAnim(...) end
 return result
end

-- Native updateModdableTilePrepare only inserts the shader-aura add_mos when
-- selfbase.add_mos is still nil. On a token the display Entity keeps its
-- add_mos after the first aura (its image is _disc.png, not invis.png), so a
-- later addShaderAura/removeShaderAura finds it non-nil and silently keeps the
-- stale set: a second aura added after a turn never appears, and removing one
-- of two leaves it drawn. When the aura roster changes, clear the stale
-- _isshaderaura entries so native rebuilds the whole set from the current
-- self.shader_auras, and invalidate the map object so a removal with no aura
-- left disappears at once.
local function auraSignature(actor)
 local kinds={}
 for kind in pairs(actor.shader_auras or {}) do kinds[#kinds+1]=tostring(kind) end
 table.sort(kinds)
 return table.concat(kinds,',')
end
function _M:checkerSyncTokenAura()
 local s=self._checker_token
 if not (s and self.replace_display==s.display) then return end
 local signature=auraSignature(self)
 if s.aura_sig==signature then return end
 s.aura_sig=signature
 local base=s.display
 if not (base and type(base.add_mos)=='table') then return end
 local cleared=false
 for i=#base.add_mos,1,-1 do
  local amo=base.add_mos[i]
  if type(amo)=='table' and amo._isshaderaura then table.remove(base.add_mos,i);cleared=true end
 end
 if not cleared then return end
 if next(base.add_mos)==nil then base.add_mos=nil end
 self:removeAllMOs()
 if self.x and game and game.level then game.level.map:updateMap(self.x,self.y) end
end

-- Native aura construction targets replace_display when one exists. Drop an
-- unsupported token before construction, so the state layer lands on the
-- native actor rather than on an Entity that will immediately be discarded.
-- The 'update' context tells a removed player token that this native rebuild
-- follows immediately, so it must not call updateModdableTile recursively.
local updateModdableTile=_M.updateModdableTile
function _M:updateModdableTile(...)
 if game and game.checkerRefreshActor then game:checkerRefreshActor(self,'update') end
 -- A second (or removed) aura on an installed token must not be skipped by
 -- native updateModdableTilePrepare's nil-add_mos gate.
 self:checkerSyncTokenAura()
 return updateModdableTile and updateModdableTile(self,...)
end

-- Native shader auras are built in Actor:updateModdableTilePrepare from the
-- actor's display image. With a token installed that image is the flat disc, so
-- the aura wraps the own cell instead of the upright standee (R39: flame pixels
-- OFF 226 / ON 90 / NATIVE 396). getMapObjects below calls this for a standee
-- token: carry the aura add_mos over to the standee layer image and the standee
-- quad before the map objects are built. The native path is untouched for flat
-- tokens and when standees are off; no shader file changes. The standee aura
-- keeps sdm_double=false; R46 the texture can be 128x256 for a tall body and
-- the quad aspect matches the texture aspect (the SDM aspect must match its
-- display box). Idempotent and safe to call often.
local Tokens
function _M:checkerStandeeAura()
 local state=self._checker_token
 if not (state and state.standee and state.layer_aura and self.replace_display==state.display) then return end
 local add=state.display and state.display.add_mos
 if type(add)~='table' or not add[1] then return end
 local aura=state.layer_aura
 local dx,dy,w,h=Style.standeeAuraQuad(aura,aura.canvas_w or aura.canvas or 256,aura.canvas_h or aura.canvas or 256,Style.standeeHeight(state.id))
 if not dx then return end
 Tokens=Tokens or require('mod.class.CheckerTokens')
 local layer=Tokens and Tokens.layerAuraImage and Tokens.layerAuraImage(state.id)
 if not layer then return end
 for _,amo in ipairs(add) do
  if type(amo)=='table' and amo._isshaderaura then
   if amo.image_alter=='sdm' then
    -- The shader aura (image_alter sdm) samples the display image and draws
    -- its flames over the standee quad, so it must use the standee layer.
    amo.image=layer
    amo.display_x=dx
    amo.display_y=dy
    amo.display_w=w
    amo.display_h=h
    amo.sdm_double=false
    amo._checker_standee_aura=true
   else
    -- Native appends a plain base-redraw copy from selfbase.image and chains
    -- it to the body. The token overlay already draws the creature exactly
    -- once, so that copy must draw nothing: otherwise native facing mirrors
    -- a second creature while the overlay does not move.
    amo.image='invis.png'
    amo._checker_standee_base=true
   end
  end
 end
end

local function ownsToken(actor,on_map)
 local state=actor._checker_token
 return on_map and state and actor.replace_display==state.display
end

-- Scoped equivalent of ToME 1.7.6 Actor:defineDisplayCallback (GPLv3).
-- Native rank sprites are local to that method, with no individual hook. Use
-- this path only for our single-layer token; all other actors delegate intact.
-- Shield emitters stay alive and attached so native impact/deactivation code,
-- saving, and switching back to vanilla all keep the same particle objects.
local defineDisplayCallback=_M.defineDisplayCallback
function _M:defineDisplayCallback()
 -- Shader auras legitimately chain a shader MO and a plain redraw MO to
 -- an owned token. Delegating that chain to native restores its boss circle
 -- on the last MO. Keep foreign chains native, but own every aura-only chain.
 local aura_chain=false
 if ownsToken(self,true) then
  local add=self._checker_token.display.add_mos
  aura_chain=type(add)=='table' and #add>0
  for _,amo in ipairs(add or {}) do
   if type(amo)~='table' or not amo._isshaderaura then aura_chain=false;break end
  end
 end
 if not ownsToken(self,true) or not self._mo
  or (self._last_mo and self._last_mo~=self._mo and not aura_chain) then
  return defineDisplayCallback(self)
 end
 -- Preserve native z-order: back emitters precede the aura chain, front
 -- emitters follow it on the last MO. The owned last callback omits rank art.
 local split=aura_chain and self._last_mo and self._last_mo~=self._mo
 local weak=setmetatable({self},{__mode='v'})
 local back,front=self:getParticlesList(true),self:getParticlesList()
 local function particles(list,pass,x,y,w,h)
  local actor=weak[1]
  if not actor or not actor._mo then return end
  local dy=h>w and (h-w)/2 or 0
  for _,e in ipairs(list) do
   e:checkDisplay()
   if e.ps:isAlive() then
    if pass==2 and game.level and game.level.map then e:shift(game.level.map,actor._mo) end
    e.ps:toScreen(x+w/2+(e.dx or 0)*w,y+dy+h/2+(e.dy or 0)*h,true,w/(game.level and game.level.map.tile_w or w))
   else actor:removeParticles(e) end
  end
 end
 if split then
  self._last_mo:displayCallback(function(x,y,w,h)
   particles(front,2,x,y,w,h)
   return true
  end)
 end
 self._mo:displayCallback(function(x,y,w,h,zoom,on_map,tlx,tly)
  local actor=weak[1]
  if not actor or not actor._mo then return true end
  local covered=ownsToken(actor,on_map)
  local tx,ty=tlx or x,tly or y
  if covered then
   -- Unlike the unscaled overlay, the body callback already includes its
   -- centered inset. Remove that inset, while retaining animated lift.
   local scale=actor._checker_token.scale or 1
   tx,ty=x-(w/scale-w)/2,y-(h/scale-h)/2
  end
  if covered and actor._checker_token.layered then
   -- Layered trial: draw only the thin faction ring here, on the empty disc.
   -- The native shader-aura add_mos that the engine chains to this body object
   -- are drawn after this callback, so the 1.25x creature is deferred to the
   -- overlay pass (above the aura); it is drawn here only when there is no
   -- overlay, kept after the ring but before the badge/bar.
   actor:checkerTacticalFrame(game.level.map,tx,ty,w,h,game.always_target,'ring')
   if not actor._checker_token.overlay_active then
    actor:checkerLayerCreature(game.level.map,tx,ty,w,h)
    actor:checkerTacticalFrame(game.level.map,tx,ty,w,h,game.always_target,'badge')
   end
  elseif game.level and game.level.map.view_faction and game.always_target and game.always_target~='old' then
   if on_map then actor:smallTacticalFrame(game.level.map,tx,ty,w,h,zoom,on_map) end
  else actor:bigTacticalFrame(tx,ty,w,h,zoom,on_map) end
  if game.level and actor.can_talk then
   local chat=game.level.map.tilesTactic:get('',0,0,0,0,0,0,'speak_bubble.png')
   -- Rank occupies the upper-right corner of a token. Speech has its own
   -- upper-left corner, including when tactical frames are hidden.
   chat:toScreen(tx+(covered and 1 or w-8),ty+(covered and 1 or 0),8,8)
  end
  particles(back,1,x,y,w,h)
  if not split then particles(front,2,x,y,w,h) end
  -- Rank is drawn as a compact badge by the final token overlay. No flame
  -- ellipse, rank mutation, global texture replacement or particle deletion.
  return true
 end)
end

local function texture(map,name,x,y,w,h,c)
 local tex,tx,ty=map.tiles:get('',0,0,0,0,0,0,'checker-revised+tokens/'..name..'.png',false,false,true)
 tex:toScreenFull(x,y,w,h,w/tx,h/ty,c[1]/255,c[2]/255,c[3]/255,1)
end

-- Draw a sub-rectangle of one layered creature texture. The engine's ordinary
-- textured quad cannot clip, so limiting the destination rectangle to the cell
-- and mapping the matching UV rectangle keeps the enlarged creature inside its
-- own cell without any global scissor state. A CPU vertex object is used for
-- the custom UVs; it is cached outside the actor (never serialized) exactly as
-- the old ringArc cached its arc buffer. Vertices are built in the layer's own
-- 0..w x 0..h space and translated by toScreen(x,y), so scrolling or sub-cell
-- twitch reuses the same buffer instead of allocating one per frame. The key
-- is the texture, box size, the cell-relative clip intersection, the color and
-- whether the quad is mirrored; an eviction cap keeps the cache bounded.
local layer_vo_cache={}
local LAYER_VO_CACHE_MAX=512
local function layerQuad(map,name,x,y,w,h,c,clip,flip)
 local tex,tx,ty=map.tiles:get('',0,0,0,0,0,0,'checker-revised+tokens-layer/'..name..'.png',false,false,false)
 if not tex then return end
 local ix0,iy0=math.max(x,clip[1]),math.max(y,clip[2])
 local ix1,iy1=math.min(x+w,clip[1]+clip[3]),math.min(y+h,clip[2]+clip[4])
 if ix1<=ix0 or iy1<=iy0 then return end
 local lx0,ly0,lx1,ly1=ix0-x,iy0-y,ix1-x,iy1-y
 local key=name..'|'..w..'|'..h..'|'..lx0..'|'..ly0..'|'..lx1..'|'..ly1..'|'
  ..c[1]..'|'..c[2]..'|'..c[3]..'|'..tx..'|'..ty..'|'..(flip and 1 or 0)
 local vo=layer_vo_cache[key]
 if not vo then
  local count=0
  for _ in pairs(layer_vo_cache) do count=count+1 end
  if count>=LAYER_VO_CACHE_MAX then layer_vo_cache={} end
  vo=core.display.newVO(4)
  local function point(px,py)
   local u=px/w
   if flip then u=1-u end
   return {px,py,u*tx,py/h*ty}
  end
  vo:addQuad(c[1]/255,c[2]/255,c[3]/255,1,
   point(lx0,ly0),point(lx1,ly0),point(lx1,ly1),point(lx0,ly1))
  layer_vo_cache[key]=vo
 end
 vo:toScreen(x,y,tex)
end

function _M:checkerTacticalFrame(map,x,y,w,h,show_life,pass)
 local state=self._checker_token
 local viewer=map.actor_player
 -- Match native Map:updateMap's actor gate, including ESP and no-viewer
 -- spectators. The body can receive onSeen(false) from a refreshed canSee
 -- cache before the independent overlay MO is rebuilt. Never let that stale
 -- callback draw life, allegiance, shield or rank for an undetected actor.
 -- canSee is cached; do not reroll detection or add a terrain-FOV condition.
 if viewer and not viewer:canSee(self) then return end
 local relation=viewer and viewer:reactionToward(self) or require('engine.Faction'):factionReaction(map.view_faction,self.faction)
 local kind=Style.relation(self,viewer,relation)
 local relation_color=Style.relationColor(kind)
 -- Native tactical callbacks use the tile's origin, but scaled object width.
 local scale=state.scale or 1
 local g=Style.geometry(x,y,w/scale,scale)
 local with_ring=pass~='badge' and map.view_faction
 local with_badge=pass~='ring'
 if with_ring then
  -- Always the full thin faction ring (the old show_life=false branch): the
  -- complete outline encodes allegiance, there is no health arc on the ring.
  texture(map,'_relation-back',g.x,g.y,g.d,g.d,{15,20,20})
  texture(map,'_relation-'..kind,g.x,g.y,g.d,g.d,relation_color)
  if kind=='player' then texture(map,'_player-inner',g.x,g.y,g.d,g.d,{244,244,224}) end
 end
 if with_badge then
  local badge=Style.rankBadge(self.rank)
  if badge then
   local width,height=Style.badgeSize(g.cell)
   local bx,by=x+g.cell-width,y+1
   texture(map,'_badge-back',bx,by,width,height,{20,24,23})
   texture(map,'_badge-'..badge,bx,by,width,height,Style.rankColor(badge))
  end
  -- Native tactical life bar on the top pass, exactly where the engine puts
  -- it: the actor's cell origin and cell size, not the scaled token size.
  local mode=Style.nativeBarMode(map)
  if mode then
   local friend
   if viewer then friend=viewer:reactionToward(self) else friend=require('engine.Faction'):factionReaction(map.view_faction,self.faction) end
   Style.nativeLifeBar(self,x,y,w/scale,w/scale,mode,friend and friend<0)
  end
 end
end

-- Layered trial: the disc is the entity image, the ring is drawn by the body
-- callback before this, and the cut-out is enlarged about the disc centre only
-- after the ring, so the creature reads first. The destination is clipped to
-- the map cell so the 1.25x enlargement can never touch a neighbour.
function _M:checkerLayerCreature(map,x,y,w,h)
 local state=self._checker_token
 if not state or not state.layered or not state.layer_id or not map or not map.tiles then return end
 local scale=state.scale or 1
 local cell=w/scale
 if state.standee and state.layer_box then
  -- Standee: draw the whole cut-out canvas scaled so the creature is at most
  -- the id's committed native-tall height cap (read statically, never from a
  -- live actor field; width capped at 1.0 cell), feet at disc centre + .55R.
  -- It extends up into the cell above; like a native display_h=2 tall sprite
  -- it is never clipped to the own cell, so rows below (drawn later) still
  -- overlap its lower part. Nothing is revealed about the cell above: this is
  -- part of the boss and is drawn only when the boss itself is seen. The
  -- canvas size comes from the per-file geometry entry: standee layers ship on
  -- a 256px canvas, ordinary R32 layers on 128px. Standees are selected only
  -- at tiles >= 24px in Game.lua.
  local cap=Style.standeeHeight(state.id)
  if cap then
   local g=Style.geometry(x,y,cell,scale)
   local disc_d=cell*Style.token_diameter
   local left,top,size=Style.standeeQuad(cell,state.layer_box,state.layer_box.canvas or 128,g.cx,g.cy,disc_d,cap)
   if left then
    layerQuad(map,state.layer_id,left,top,size,size,{255,255,255},{left,top,size,size},state.body_flip)
    return
   end
  end
 end
 local size=Style.layerSize(cell,scale)
 local ox,oy=x+(cell-size)/2,y+(cell-size)/2
 layerQuad(map,state.layer_id,ox,oy,size,size,{255,255,255},{x,y,cell,cell},state.body_flip)
end

local smallTacticalFrame=_M.smallTacticalFrame
function _M:smallTacticalFrame(map,x,y,w,h,zoom,on_map,...)
 if ownsToken(self,on_map) then
  return self:checkerTacticalFrame(map,x,y,w,h,true,self._checker_token.overlay_active and 'ring' or 'all')
 end
 return smallTacticalFrame(self,map,x,y,w,h,zoom,on_map,...)
end

local bigTacticalFrame=_M.bigTacticalFrame
function _M:bigTacticalFrame(x,y,w,h,zoom,on_map,...)
 if ownsToken(self,on_map) then
  return self:checkerTacticalFrame(game.level.map,x,y,w,h,game.always_target,self._checker_token.overlay_active and 'ring' or 'all')
 end
 return bigTacticalFrame(self,x,y,w,h,zoom,on_map,...)
end
return _M
