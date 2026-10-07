-- Layered small-tile trials: runtime geometry and path switching. Loads the
-- real CheckerTokenStyle, CheckerTokens and the Actor superload with a capture
-- harness, so the drawn geometry is the shipped geometry. The R33 boss
-- standee geometry/eligibility lives in tests/token_standee.lua.
local script=debug.getinfo(1,'S').source:sub(2)
local root=(script:match('^(.*[/\\])') or './')..'../'
local Style=dofile(root..'overload/mod/class/CheckerTokenStyle.lua')
local Tokens=dofile(root..'overload/mod/class/CheckerTokens.lua')

-- Two independent switches. The R32 ordinary path is off by default and the
-- R33 boss standee is on; layerImage is a flag-independent file lookup so the
-- audit and the build tool always see every shipped layer.
assert(Tokens.layer_trial==false,'ordinary R32 trial flag must default off')
assert(Tokens.standee_trial==true,'standee trial must default on')
assert(Tokens.layerImage('wolf')=='checker-revised+tokens-layer/wolf.png')
assert(Tokens.layerImage('phoenix')==nil,'archived standee-only id has no layer')
assert(Tokens.layerImage('animated-blood')==nil,'unlisted token must have no layer')
assert(Tokens.layerImage('orc-archer')=='checker-revised+tokens-layer/orc-archer.png')
assert(Tokens.layerDisc()=='checker-revised+tokens-layer/_disc.png')
-- R41: only standees ship a padded aura copy; ordinary layers and archived ids
-- must not resolve one.
assert(Tokens.layerAuraImage('kra-tor')==nil,'R43 archived kra-tor ships no aura texture')
assert(Tokens.layerAuraImage('snow-giant')=='checker-revised+tokens-layer/aura/snow-giant.png')
assert(Tokens.layerAuraImage('wolf')==nil,'ordinary layers ship no aura texture')
assert(Tokens.layerAuraImage('animated-blood')==nil)
assert(Tokens.layerAuraImage(nil)==nil)
-- The ordinary R32 path follows its own switch only.
assert(Tokens.layeredId('wolf')==false,'ordinary path must be off when layer_trial is off')
assert(Tokens.layeredId('phoenix')==false,'archived standee-only id stays ordinary-free')
local saved=Tokens.layer_trial
Tokens.layer_trial=true
assert(Tokens.layeredId('wolf')==true)
assert(Tokens.layeredId('storm-wyrm')==true)
assert(Tokens.layeredId('animated-blood')==false)
Tokens.layer_trial=false
local saved_standee=Tokens.standee_trial
Tokens.standee_trial=false
assert(Tokens.layerDisc()==nil,'both flags off must disable the disc path')
assert(Tokens.layeredId('wolf')==false and Tokens.layeredId('storm-wyrm')==false)
Tokens.layer_trial=saved;Tokens.standee_trial=saved_standee
assert(Tokens.layeredId('wolf')==false and Tokens.layerDisc())

-- Geometry constants: only <=48px cells layer, 1.25x about the same canvas.
assert(Tokens.layer_max_cell==48)
assert(Style.layer_scale==1.25)
local base=Style.token_diameter/Style.art_occupancy
assert(math.abs(Style.layerSize(48,base)-48*base*1.25)<1e-9)
assert(math.abs(Style.layerSize(64,base)-64*base*1.25)<1e-9,'layerSize scales linearly')

-- Capture harness: textured masks, ring arcs and custom-UV quads.
local draws,quads={},{}
local vo_allocs=0
local function newVO()
 vo_allocs=vo_allocs+1
 return {quads={},addQuad=function(self,r,g,b,a,p1,p2,p3,p4)
   self.quads[#self.quads+1]={p1,p2,p3,p4};self.color={r,g,b}
  end,toScreen=function(self,x,y,tex)
   -- Record absolute screen coords (the cached VO is built local to the box
   -- origin and translated by toScreen) so the geometry assertions below see
   -- the same values as before the R41 cache.
   local q={}
   for i,quad in ipairs(self.quads) do
    local qq={}
    for j,pt in ipairs(quad) do qq[j]={pt[1]+x,pt[2]+y,pt[3],pt[4]} end
    q[i]=qq
   end
   draws[tex.name]=q
  end}
end
local map={actor_player={canSee=function() return true end,reactionToward=function() return -1 end},view_faction='players',
 tiles={get=function(_,...)
  local name=select(8,...)
  return {name=name,toScreenFull=function(self,...) draws[name]=(draws[name] or 0)+1;draws['nf:'..name]={...} end},1,1
 end}}
local env=setmetatable({loadPrevious=function() return {} end,
 require=function(name) return name=='mod.class.CheckerTokenStyle' and Style or {} end,
 core={display={newVO=newVO}}},{__index=_G})
config={settings={tome={checker_relation_colors={},checker_rank_colors={}}}}
local chunk=assert(loadfile(root..'superload/mod/class/Actor.lua'));setfenv(chunk,env)
local Actor=chunk()

local function actor(layered,cell)
 local a=setmetatable({life=50,max_life=100,rank=4,cell=cell,
  _checker_token={scale=base,layered=layered and true or nil,layer_id=layered and 'wolf' or nil}},
  {__index=Actor})
 function a:attr(k) return self[k] end
 return a
end

-- Layered at 48px: the ring pass draws the faction arc but not the badge.
local a=actor(true,48)
draws={};a:checkerTacticalFrame(map,0,0,48*base,48*base,true,'ring')
assert(draws['checker-revised+tokens/_relation-back.png'],'ring pass draws the disc backing')
assert(draws['checker-revised+tokens/_relation-enemy.png'],'ring pass draws the full faction ring, with no health arc')
assert(not draws['checker-revised+tokens/_health-band.png'],'the health arc mask must never be drawn')
assert(not draws['checker-revised+tokens/_shield-band.png'],'the shield ring mask must never be drawn')
assert(not draws['checker-revised+tokens/_badge-boss.png'],'ring pass must not draw the badge')
-- The creature layer is drawn clipped to the cell, never outside it.
draws={};a:checkerLayerCreature(map,0,0,48*base,48*base)
local quad=draws['checker-revised+tokens-layer/wolf.png']
assert(quad and #quad==1,'layered creature must draw one clipped quad')
-- R41: a second identical draw reuses the cached vertex object instead of
-- allocating a new one every frame. Move the box origin and the allocation
-- count must not change (vertices are translated by toScreen).
local allocs_before=vo_allocs
draws={};a:checkerLayerCreature(map,7,3,48*base,48*base)
assert(vo_allocs==allocs_before,'layerQuad must reuse its cached VO across frames')
assert(draws['checker-revised+tokens-layer/wolf.png'],'cached VO still draws')
-- A changed destination size is a different geometry and must rebuild.
draws={};a:checkerLayerCreature(map,0,0,32*base,32*base)
assert(vo_allocs>allocs_before,'a different box size must not collide in the VO cache')
for _,p in ipairs(quad[1]) do
 assert(p[1]>=-1e-6 and p[1]<=48+1e-6,'creature x must stay inside the 48px cell')
 assert(p[2]>=-1e-6 and p[2]<=48+1e-6,'creature y must stay inside the 48px cell')
end
-- The badge pass draws only the rank badge.
draws={};a:checkerTacticalFrame(map,0,0,48*base,48*base,true,'badge')
assert(draws['checker-revised+tokens/_badge-boss.png'],'badge pass draws the rank badge')
assert(not draws['checker-revised+tokens/_relation-back.png'],'badge pass must not redraw the ring')
-- The full pass on a layered actor (no overlay) draws both.
draws={};a:checkerTacticalFrame(map,0,0,48*base,48*base,true,'all')
assert(draws['checker-revised+tokens/_relation-back.png'] and draws['checker-revised+tokens/_badge-boss.png'])

-- Non-layered tokens (and 64/96px): no creature quad, and the single full
-- tactical frame is drawn exactly as before.
local b=actor(false,64)
draws={};b:checkerLayerCreature(map,0,0,64*base,64*base)
assert(next(draws)==nil,'non-layered token must not draw a creature layer')
draws={};b:checkerTacticalFrame(map,0,0,64*base,64*base,true)
assert(draws['checker-revised+tokens/_relation-back.png'] and draws['checker-revised+tokens/_badge-boss.png'],
 '64px non-layered token keeps the full frame in one pass')
draws={};b:checkerTacticalFrame(map,0,0,96*base,96*base,true)
assert(draws['checker-revised+tokens/_relation-back.png'] and draws['checker-revised+tokens/_badge-boss.png'],
 '96px non-layered token keeps the full frame in one pass')

-- The engine chains a native shader-aura add_mos to the body object and draws
-- it after the body callback, so a layered creature drawn there would be
-- covered by the aura's disc-shaped copy (the phoenix's body_of_fire). The
-- creature must therefore be drawn on the overlay pass when one exists, and
-- only fall back to the body pass without an overlay.
local f=assert(io.open(root..'superload/mod/class/Actor.lua','r'))
local actor_src=f:read('*a');f:close()
assert(actor_src:find("if s.layered then actor:checkerLayerCreature",1,true),
 'overlay pass must draw the layered creature above native shader auras')
assert(actor_src:find("if not actor._checker_token.overlay_active then",1,true),
 'body pass may draw the layered creature only when no overlay exists')

print('token_layers: flag off keeps old path, 48px ring-under-creature clipped to the cell, layered creature above shader-aura add_mos, 64/96 unchanged')
