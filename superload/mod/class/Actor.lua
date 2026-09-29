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
     and game.level and game.level.map.view_faction then
     local scale=s.scale or 1
     -- Overlay has no inset: x/y are the animated full-cell origin, including
     -- twitch. Use them so all state follows the lifted disk as one piece.
     actor:checkerTacticalFrame(game.level.map,x,y,w*scale,h*scale,game.always_target)
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
 return removeAllMOs(self,no_invalidate)
end

local MOflipX=_M.MOflipX
function _M:MOflipX(value)
 local result=MOflipX(self,value)
 local s=self._checker_token
 if s and self.replace_display==s.display and self._mo and Options.tokenFacing()=='fixed' then
  -- Native _flipx remains the last requested direction, for switching back.
  -- Flip only the owned body; tactical arcs never mirror with the artwork.
  self._mo:flipX(false)
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

-- Native aura construction targets replace_display when one exists. Drop an
-- unsupported token before construction, so the state layer lands on the
-- native actor rather than on an Entity that will immediately be discarded.
-- The 'update' context tells a removed player token that this native rebuild
-- follows immediately, so it must not call updateModdableTile recursively.
local updateModdableTile=_M.updateModdableTile
function _M:updateModdableTile(...)
 if game and game.checkerRefreshActor then game:checkerRefreshActor(self,'update') end
 return updateModdableTile(self,...)
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
 if not ownsToken(self,true) or not self._mo or (self._last_mo and self._last_mo~=self._mo) then
  return defineDisplayCallback(self)
 end
 local weak=setmetatable({self},{__mode='v'})
 local back,front=self:getParticlesList(true),self:getParticlesList()
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
  if game.level and game.level.map.view_faction and game.always_target and game.always_target~='old' then
   if on_map then actor:smallTacticalFrame(game.level.map,tx,ty,w,h,zoom,on_map) end
  else actor:bigTacticalFrame(tx,ty,w,h,zoom,on_map) end
  if game.level and actor.can_talk then
   local chat=game.level.map.tilesTactic:get('',0,0,0,0,0,0,'speak_bubble.png')
   -- Rank occupies the upper-right corner of a token. Speech has its own
   -- upper-left corner, including when tactical frames are hidden.
   chat:toScreen(tx+(covered and 1 or w-8),ty+(covered and 1 or 0),8,8)
  end
  local hidden={}
  if covered then local _,_,p=Style.shieldData(actor);hidden=p end
  local dy=h>w and (h-w)/2 or 0
  for pass,list in ipairs{back,front} do
   for _,e in ipairs(list) do
    e:checkDisplay()
    if e.ps:isAlive() then
     if pass==2 and game.level and game.level.map then e:shift(game.level.map,actor._mo) end
     if not hidden[e] then
      e.ps:toScreen(x+w/2+(e.dx or 0)*w,y+dy+h/2+(e.dy or 0)*h,true,w/(game.level and game.level.map.tile_w or w))
     end
    else actor:removeParticles(e) end
   end
  end
  -- Rank is drawn as a compact badge by the final token overlay. No flame
  -- ellipse, rank mutation, global texture replacement or particle deletion.
  return true
 end)
end

local function texture(map,name,x,y,w,h,c)
 local tex,tx,ty=map.tiles:get('',0,0,0,0,0,0,'checker-revised+tokens/'..name..'.png',false,false,true)
 tex:toScreenFull(x,y,w,h,w/tx,h/ty,c[1]/255,c[2]/255,c[3]/255,1)
end

-- CPU vertex objects are cached outside actors, so they are not serialized.
-- The texture supplies antialiased ring edges; the fan only clips its angle.
-- This uses the engine's ordinary textured quads, with no shader dependency.
local health_cache=setmetatable({},{__mode='k'})
local function ringArc(actor,map,g,key,name,c,fraction,counterclockwise)
 if fraction<=0 then return end
 if fraction>=1 then
  texture(map,name,g.x,g.y,g.d,g.d,c)
  return
 end
 local tex,tx,ty=map.tiles:get('',0,0,0,0,0,0,'checker-revised+tokens/'..name..'.png',false,false,false)
 local cache=health_cache[actor] or {};health_cache[actor]=cache
 local cached=cache[key]
 if not cached or cached.fraction~=fraction or cached.d~=g.d or cached.tx~=tx or cached.ty~=ty or cached.counterclockwise~=counterclockwise
  or cached.r~=c[1] or cached.g~=c[2] or cached.b~=c[3] then
  local segments=math.max(1,math.ceil(64*fraction))
  local vo=core.display.newVO(segments*4)
  local center={g.d/2,g.d/2,tx/2,ty/2}
  local function point(angle)
   local u,v=.5+(counterclockwise and -.5 or .5)*math.sin(angle),.5-.5*math.cos(angle)
   return {u*g.d,v*g.d,u*tx,v*ty}
  end
  for i=1,segments do
   local first,last=point((i-1)/segments*fraction*2*math.pi),point(i/segments*fraction*2*math.pi)
   -- Preserve the original triangle winding when mirroring the arc.
   if counterclockwise then first,last=last,first end
   vo:addQuad(c[1]/255,c[2]/255,c[3]/255,1,center,first,last,center)
  end
  cached={fraction=fraction,d=g.d,tx=tx,ty=ty,vo=vo,counterclockwise=counterclockwise,r=c[1],g=c[2],b=c[3]};cache[key]=cached
 end
 cached.vo:toScreen(g.x,g.y,tex)
end

function _M:checkerTacticalFrame(map,x,y,w,h,show_life)
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
 texture(map,'_relation-back',g.x,g.y,g.d,g.d,{15,20,20})
 if show_life then
  -- Color and the complete thin edge encode allegiance; bright arc length
  -- encodes life counterclockwise from twelve: left, bottom, then right.
  ringArc(self,map,g,'life-'..kind,'_health-band',relation_color,Style.lifeFraction(self),true)
  texture(map,'_relation-edge-'..kind,g.x,g.y,g.d,g.d,relation_color)
 else
  texture(map,'_relation-'..kind,g.x,g.y,g.d,g.d,relation_color)
 end
 if kind=='player' then texture(map,'_player-inner',g.x,g.y,g.d,g.d,{244,244,224}) end
 local shield,maximum=Style.shieldData(self)
 if maximum>0 then
  local d=g.d+g.cell*.09
  local outer={x=g.cx-d/2,y=g.cy-d/2,d=d}
  texture(map,'_shield-track',outer.x,outer.y,d,d,{25,28,27})
  local fraction=show_life and math.max(0,math.min(1,shield/maximum)) or 1
  ringArc(self,map,outer,'shield','_shield-band',Style.colors.shield,fraction)
  -- Pearl-white capacity and pale ticks are independent of faction hues.
  texture(map,'_shield-ticks',outer.x,outer.y,d,d,Style.colors.shield_ticks)
 end
 local badge=Style.rankBadge(self.rank)
 if badge then
  local width,height=math.max(12,g.cell*.23),math.max(9,g.cell*.18)
  local bx,by=x+g.cell-width,y+1
  texture(map,'_badge-back',bx,by,width,height,{20,24,23})
  texture(map,'_badge-'..badge,bx,by,width,height,Style.rankColor(badge))
 end
end

local smallTacticalFrame=_M.smallTacticalFrame
function _M:smallTacticalFrame(map,x,y,w,h,zoom,on_map,...)
 if ownsToken(self,on_map) then
  if not self._checker_token.overlay_active then return self:checkerTacticalFrame(map,x,y,w,h,true) end
  return
 end
 return smallTacticalFrame(self,map,x,y,w,h,zoom,on_map,...)
end

local bigTacticalFrame=_M.bigTacticalFrame
function _M:bigTacticalFrame(x,y,w,h,zoom,on_map,...)
 if ownsToken(self,on_map) and game.level and game.level.map.view_faction then
  if not self._checker_token.overlay_active then return self:checkerTacticalFrame(game.level.map,x,y,w,h,game.always_target) end
  return
 end
 return bigTacticalFrame(self,x,y,w,h,zoom,on_map,...)
end
return _M
