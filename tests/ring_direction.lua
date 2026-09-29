-- Verify the actual renderer's occupied quadrants, rather than duplicating
-- its trigonometry. Quarter/half HP must occupy the left side of the token.
local script=debug.getinfo(1,'S').source:sub(2)
local root=(script:match('^(.*[/\\])') or './')..'../'
local Style=dofile(root..'overload/mod/class/CheckerTokenStyle.lua')
local draws,colors={},{}
local map={actor_player={canSee=function() return true end,reactionToward=function() return -1 end},tiles={get=function(_,...)
 local name=select(8,...)
 return {name=name,toScreenFull=function() end},1,1
end}}
local env=setmetatable({loadPrevious=function() return {} end,
 require=function(name) return name=='mod.class.CheckerTokenStyle' and Style or {} end,
 core={display={newVO=function()
  return {quads={},addQuad=function(self,r,g,b,a,center,p,q)
   self.color={r,g,b}
   self.quads[#self.quads+1]={center,p,q}
  end,toScreen=function(self,x,y,tex) draws[tex.name]=self.quads;colors[tex.name]=self.color end}
 end}},
},{__index=_G})
local chunk=assert(loadfile(root..'superload/mod/class/Actor.lua'));setfenv(chunk,env)
local Actor=chunk()
local a=setmetatable({life=25,max_life=100,rank=2,_checker_token={scale=.95}}, {__index=Actor})
function a:attr(k) return self[k] end
local function checkQuarter(quads,left)
 assert(quads and #quads>0)
 for _,q in ipairs(quads) do for i=2,3 do
  assert(q[i][2]<=q[1][2]+1e-6,'quarter arc must remain in upper half')
  if left then assert(q[i][1]<=q[1][1]+1e-6,'HP must grow into the left side')
  else assert(q[i][1]>=q[1][1]-1e-6,'shield keeps its own clockwise direction') end
 end end
end
a:checkerTacticalFrame(map,0,0,64*.95,64*.95,true)
checkQuarter(draws['checker-revised+tokens/_health-band.png'],true)
a.life=50;a:checkerTacticalFrame(map,0,0,64*.95,64*.95,true)
for _,q in ipairs(draws['checker-revised+tokens/_health-band.png']) do for i=2,3 do
 assert(q[i][1]<=q[1][1]+1e-6,'half HP must fill the left semicircle')
end end
a.life=75;a:checkerTacticalFrame(map,0,0,64*.95,64*.95,true)
local right=false
for _,q in ipairs(draws['checker-revised+tokens/_health-band.png']) do for i=2,3 do
 if q[i][1]>q[1][1]+1e-6 then right=true;assert(q[i][2]>=q[1][2]-1e-6,'75% HP leaves the upper-right quadrant empty') end
end end
assert(right)
a.damage_shield=40;a.damage_shield_absorb=10;a.damage_shield_absorb_max=40
a:checkerTacticalFrame(map,0,0,64*.95,64*.95,true)
checkQuarter(draws['checker-revised+tokens/_shield-band.png'],false)
assert(a.life==75 and a.damage_shield_absorb==10,'display must not modify health or shield')
config={settings={tome={checker_relation_colors={enemy={0,128,255}}}}}
a:checkerTacticalFrame(map,0,0,64*.95,64*.95,true)
local c=colors['checker-revised+tokens/_health-band.png']
assert(c[1]==0 and c[2]==128/255 and c[3]==1,'same-HP cached arc must recolor immediately')
config.settings.tome.checker_relation_colors={}
a:checkerTacticalFrame(map,0,0,64*.95,64*.95,true)
c=colors['checker-revised+tokens/_health-band.png']
assert(c[1]==225/255 and c[3]==40/255,'reset must also recolor an existing arc')
print('ring_direction: CCW HP quadrants, shield direction, immediate cached recolor/reset and combat values passed')
