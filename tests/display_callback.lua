-- Exercise the display adapter after the health/shield rings were removed:
-- the body pass draws only the thin faction ring, the badge pass draws the
-- rank badge, native emitters (including damage shields) all stay visible,
-- speech keeps its corner and foreign displays delegate to native.
local script=debug.getinfo(1,'S').source:sub(2)
local root=(script:match('^(.*[/\\])') or './')..'../'
local Style=dofile(root..'overload/mod/class/CheckerTokenStyle.lua')
local fallback=0
local draws={}
local Base={defineDisplayCallback=function() fallback=fallback+1 end,
 smallTacticalFrame=function() end,bigTacticalFrame=function() end}
local env=setmetatable({loadPrevious=function() return Base end,
 require=function(name)
  if name=='mod.class.CheckerTokenStyle' then return Style end
  if name=='mod.class.CheckerOptions' then return dofile(root..'overload/mod/class/CheckerOptions.lua') end
  if name=='engine.Entity' then return {} end
  error('unexpected dependency '..name)
 end,
 core={display={drawQuad=function() end}},
 game={always_target=true,level={map={view_faction='players',tile_w=64,
  actor_player={canSee=function() return true end,reactionToward=function() return -1 end}}}},
},{__index=_G})
local chunk=assert(loadfile(root..'superload/mod/class/Actor.lua'))
if setfenv then setfenv(chunk,env) else chunk=assert(loadfile(root..'superload/mod/class/Actor.lua','t',env)) end
local Actor=chunk()
env.game.level.map.tiles={get=function(_,...)
 local name=select(8,...)
 if not name then return nil end
 return {name=name,toScreenFull=function() draws[name]=(draws[name] or 0)+1 end},1,1
end}
local function emitter()
 local e={draws=0,shifts=0,checks=0}
 e.ps={isAlive=function() return true end,toScreen=function() e.draws=e.draws+1 end}
 function e:shift() self.shifts=self.shifts+1 end
 function e:checkDisplay() self.checks=self.checks+1 end
 return e
end
local shield,other,back=emitter(),emitter(),emitter()
local display={};local effect={}
local a=setmetatable({rank=4,life=70,damage_shield=40,damage_shield_absorb=30,damage_shield_absorb_max=40,
 EFF_DAMAGE_SHIELD=1,replace_display=display,_checker_token={display=display,overlay_active=true,scale=1},
 _mo={displayCallback=function(self,f) self.callback=f end},
},{__index=Actor})
function a:attr(k) return self[k] end
function a:hasEffect(id) assert(id==1);return effect end
function a:getParticlesList(isback) return isback and {back} or {shield,other} end
function a:removeParticles() error('live emitters must not be removed') end
a:defineDisplayCallback()
assert(fallback==0)
effect.particle=shield -- ToME assigns this AFTER addParticles installs callback.
draws={}
a._mo.callback(0,0,64,64,1,true,0,0)
assert(shield.draws==1 and other.draws==1 and back.draws==1,'every native emitter draws; damage shields are no longer hidden')
assert(shield.shifts==1 and shield.checks==1,'native emitter lifecycle work is preserved')
assert(draws['checker-revised+tokens/_relation-enemy.png']==1,'body pass draws the thin faction ring')
assert(not draws['checker-revised+tokens/_badge-boss.png'],'body pass must not draw the badge')
assert(not draws['checker-revised+tokens/_health-band.png'] and not draws['checker-revised+tokens/_shield-band.png'],
 'no health or shield ring may ever be drawn')
assert(a.rank==4 and a.life==70 and a.damage_shield_absorb==30 and effect.particle==shield,'display cannot mutate rules or emitter ownership')
a._mo.callback(0,0,64,64,1,false,0,0)
assert(shield.draws==2,'off-map display must not suppress the native effect')

-- The badge pass draws the rank badge and the native life bar, never the ring.
draws={}
a:checkerTacticalFrame(env.game.level.map,0,0,64,64,true,'badge')
assert(draws['checker-revised+tokens/_badge-boss.png']==1,'badge pass draws the rank badge')
assert(not draws['checker-revised+tokens/_relation-back.png'],'badge pass must not redraw the ring')

-- Speech keeps the upper-left corner for a covered token.
local bubble
env.game.level.map.tilesTactic={get=function()
 return {toScreen=function(_,x,y,w,h) bubble={x,y,w,h} end}
end}
a.can_talk=true
for _,cell in ipairs{48,64,96} do
 a._mo.callback(100,200,cell,cell,1,true,100,200)
 assert(bubble[1]==101 and bubble[2]==201 and bubble[3]==8 and bubble[4]==8,
  'on-map token speech must use upper-left, leaving the rank corner free')
end
a._mo.callback(100,200,64,64,1,false,100,200)
assert(bubble[1]==156 and bubble[2]==200,'off-map native speech position preserved')
-- A legitimate aura chain must not restore the native boss ornament on its
-- last MO. Exercise both rank 4 and rank 2, preserving native emitters once.
local last={displayCallback=function(self,f) self.callback=f end}
display.add_mos={{_isshaderaura=true,image_alter='sdm'},{_isshaderaura=true,image='invis.png'}}
a._last_mo=last
for _,rank in ipairs{4,3.5,3.2,2} do
 a.rank=rank
 last.callback=function() error('stale native boss callback must be replaced') end
 local before=shield.draws
 a:defineDisplayCallback()
 assert(fallback==0,'owned shader chain must not delegate to native rank rendering')
 local bbefore=back.draws
 local cbefore=shield.checks
 local sbefore=shield.shifts
 a._mo.callback(0,0,64,64,1,true,0,0)
 assert(back.draws==bbefore+1,'back particles draw before the chained aura')
 assert(shield.draws==before and shield.checks==cbefore,'front particles wait for the last MO after the aura')
 last.callback(0,0,64,64,1,true,0,0)
 assert(back.draws==bbefore+1,'last callback must not repeat back particles')
 assert(shield.checks==cbefore+1 and shield.shifts==sbefore+1,'front lifecycle and shift run exactly once on last MO')
 assert(shield.draws==before+1,'chained aura retains each native emitter exactly once')
end
display.add_mos=nil;a._last_mo=nil
a.replace_display={};a:defineDisplayCallback();assert(fallback==1,'foreign display delegates')
a.replace_display=display;a._last_mo={};a:defineDisplayCallback();assert(fallback==2,'unexpected additional layers delegate')
a._last_mo=nil;a._checker_token=nil;a:defineDisplayCallback();assert(fallback==3,'vanilla delegates')
print('display_callback: ring-only body pass, badge pass, shield particles, speech corner and native fallback passed')
