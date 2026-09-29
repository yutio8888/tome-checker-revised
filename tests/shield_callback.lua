-- Exercise the actual display adapter, including native fallback and the
-- addParticles-before-effect.particle assignment used by ToME activation.
local script=debug.getinfo(1,'S').source:sub(2)
local root=(script:match('^(.*[/\\])') or './')..'../'
local Style=dofile(root..'overload/mod/class/CheckerTokenStyle.lua')
local fallback=0
local Base={defineDisplayCallback=function() fallback=fallback+1 end,
 smallTacticalFrame=function() end,bigTacticalFrame=function() end}
local env=setmetatable({loadPrevious=function() return Base end,
 require=function(name)
  if name=='mod.class.CheckerTokenStyle' then return Style end
  if name=='mod.class.CheckerOptions' then return dofile(root..'overload/mod/class/CheckerOptions.lua') end
  if name=='engine.Entity' then return {} end
  error('unexpected dependency '..name)
 end,
 game={always_target=true,level={map={view_faction='players',tile_w=64}}},
},{__index=_G})
local chunk=assert(loadfile(root..'superload/mod/class/Actor.lua'))
if setfenv then setfenv(chunk,env) else chunk=assert(loadfile(root..'superload/mod/class/Actor.lua','t',env)) end
local Actor=chunk()
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
 EFF_DAMAGE_SHIELD=1,replace_display=display,_checker_token={display=display,overlay_active=true},
 _mo={displayCallback=function(self,f) self.callback=f end},
},{__index=Actor})
function a:attr(k) return self[k] end
function a:hasEffect(id) assert(id==1);return effect end
function a:getParticlesList(isback) return isback and {back} or {shield,other} end
function a:removeParticles() error('live emitters must not be removed') end
a:defineDisplayCallback()
assert(fallback==0)
effect.particle=shield -- ToME assigns this AFTER addParticles installs callback.
a._mo.callback(0,0,64,64,1,true,0,0)
assert(shield.draws==0 and other.draws==1 and back.draws==1,'only the known shield emitter may be hidden')
assert(shield.shifts==1 and shield.checks==1,'hidden emitter retains native lifecycle work')
assert(a.rank==4 and a.life==70 and a.damage_shield_absorb==30 and effect.particle==shield,'display cannot mutate rules or emitter ownership')
a._mo.callback(0,0,64,64,1,false,0,0)
assert(shield.draws==1,'off-map display must not silently suppress the native effect')
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
for _,cell in ipairs{48,64,96} do
 local scale=.893;local inset=cell*(1-scale)/2
 a._checker_token.scale=scale
 a._mo.callback(100+inset,200+inset-cell*.1,cell*scale,cell*scale,1,true,100+inset,200+inset)
 assert(math.abs(bubble[1]-101)<1e-8 and math.abs(bubble[2]-(201-cell*.1))<1e-8,
  'speech follows the lifted disk without double-counting its inset')
end
a._checker_token.scale=nil
env.game.always_target=false
a._mo.callback(100,200,64,64,1,true,100,200)
assert(bubble[1]==101 and bubble[2]==201,'speech remains visible with tactical frames off')
a.replace_display={};a:defineDisplayCallback();assert(fallback==1,'foreign display delegates')
a.replace_display=display;a._last_mo={};a:defineDisplayCallback();assert(fallback==2,'unexpected additional layers delegate')
a._last_mo=nil;a._checker_token=nil;a:defineDisplayCallback();assert(fallback==3,'vanilla delegates')
print('shield_callback: live emitter identity, delayed assignment, back/front effects, rule preservation, token speech corner and native fallback passed')
