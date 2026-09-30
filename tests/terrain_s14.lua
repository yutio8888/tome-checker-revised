-- S14 (portal / farportal bridge; High Peak invocation portals and the
-- Sanctum portal). Run from any cwd with Lua 5.1/LuaJIT. The native zone
-- lists are built the way Entity:loadList/Entity:init build them (real engine
-- colours, base import, colour/back colour/tint normalisation) and stamped per
-- finished file (the superload/mod/class/Grid.lua order). The stone side is
-- exercised through T.classify / T.observe / T.render on a mocked level, the
-- forest side (Sher'Tul farportal, Demon Plane return portal) through
-- T.apply on a mocked level. Placements follow the native placement: a clone
-- of the list entity (quest code places one entity on all eight ring cells).
local root=(debug.getinfo(1,'S').source:sub(2):match('^(.*[/\\])') or './')..'../'
local data=root..'../../modules/tome/data'
local n=0
local function eq(a,b,label) n=n+1;assert(a==b,label..': '..tostring(a)..' ~= '..tostring(b)) end
local function readFile(path) local f=assert(io.open(path,'rb'));local s=f:read('*a');f:close();return s end
local Entity={}
function Entity.new(t)
 t.removeAllMOs=function() end
 t.getMapObjects=function(self,tiles,mos,z) self._mo=self.image;mos[z]=self.image end
 return t
end
local mode='refined'
local modules={['engine.Entity']=Entity,['mod.class.CheckerOptions']={terrainMode=function() return mode end,auraStyle=function() return 'subtle' end}}
local env=setmetatable({require=function(name) return assert(modules[name],name) end},{__index=_G})
local function loadWith(path,e) local chunk=assert(loadfile(path));setfenv(chunk,e);return chunk() end
-- The engine's _t / tformat (identity translation here).
_G._t=function(s) return s end
string.tformat=function(fmt,...) return fmt:format(...) end
local T=loadWith(root..'overload/mod/class/CheckerTerrain.lua',env);modules['mod.class.CheckerTerrain']=T
T.assets.ready=true;setmetatable(T.assets.files,{__index=function() return true end})

local cenv=setmetatable({},{__index=_G})
loadWith(root..'../../engines/default/engine/colors.lua',cenv)
local colors=cenv.colors
eq(colors.WHITE.r..','..colors.WHITE.g..','..colors.WHITE.b,'255,255,255','engine WHITE (invocation_close)')
eq(colors.VIOLET.r..','..colors.VIOLET.g..','..colors.VIOLET.b,'192,0,175','engine VIOLET (farportal back colour)')
eq(colors.PURPLE.r..','..colors.PURPLE.g..','..colors.PURPLE.b,'128,0,139','engine PURPLE (invocation back colour)')
eq(colors.LIGHT_BLUE.r..','..colors.LIGHT_BLUE.g..','..colors.LIGHT_BLUE.b,'81,221,255','engine LIGHT_BLUE')
eq(colors.DARK_GREY.r,67,'engine DARK_GREY')

local methods={}
local meta={__index=methods}
local function deep(t)
 if type(t)~='table' then return t end
 local o={};for k,v in pairs(t) do o[deep(k)]=deep(v) end
 return setmetatable(o,getmetatable(t))
end
methods.clone=function(self) return deep(self) end
methods.removeAllMOs=function(self) self._mo=nil end
methods.check=function(self,prop,...) local v=self[prop];if type(v)=='function' then return v(self,...) end;return v end
local function init(t)
 if t.color then t.color_r,t.color_g,t.color_b=t.color.r,t.color.g,t.color.b;t.color=nil end
 if t.back_color then t.color_br,t.color_bg,t.color_bb=t.back_color.r,t.back_color.g,t.back_color.b;t.back_color=nil end
 t.display=t.display or '.'
 t.color_r=t.color_r or 0;t.color_g=t.color_g or 0;t.color_b=t.color_b or 0
 t.color_br=t.color_br or -1;t.color_bg=t.color_bg or -1;t.color_bb=t.color_bb or -1
 t.tint_r=t.tint_r or 1;t.tint_g=t.tint_g or 1;t.tint_b=t.tint_b or 1
 t.__particles=t.__particles or {}
 return setmetatable(t,meta)
end
local resolvers=setmetatable({generic=function(f) return {__resolver='generic',f} end,
 mbonus=function(max,add) return {__resolver='mbonus',__resolve_instant=true,max,add} end},
 {__index=function() return function(v) return v end end})
local fenvBase={colors=colors,_t=function(s) return s end,resolvers=resolvers,
 engine={DamageType=setmetatable({},{__index=function(_,k) return k end}),Map={TERRAIN=1,ACTOR=2}},
 rng={percent=function() return false end,range=function(a) return a end},currentZone={}}
local function loadDefs(file)
 local out,order={}, {}
 local fenv
 local current
 local function run(path,m)
  local first=#order
  local prev=current;current=m
  local chunk=assert(loadstring(readFile(data..path:gsub('^/data','')),'@'..path))
  setfenv(chunk,fenv);chunk()
  current=prev
  for i=first+1,#order do T.markSource(out[order[i]],path) end
 end
 fenv=setmetatable({class={new=function(t) return init(t) end,makeNewTrees=function(_,t) return t end,makeTrees=function() return {} end,
   makeCrystals=function() return {} end},mod={class={Grid={new=function(t) return init(t) end}}},
  load=function(path,f) run(path,f or current) end,loading_list=out,
  newEntity=function(t)
   local g={}
   if t.base then for k,v in pairs(assert(out[t.base],t.base)) do if k~='define_as' then g[k]=deep(v) end end end
   for k,v in pairs(t) do if k~='base' then g[k]=v end end
   init(g)
   if current then current(g) end
   order[#order+1]=t.define_as
   out[t.define_as]=g
  end},{__index=function(_,k) if fenvBase[k]~=nil then return fenvBase[k] end;return _G[k] end})
 run(file)
 return out
end
string.prefix=string.prefix or function(str,pre) return str:sub(1,#pre)==pre end
local F={hp='/data/zones/high-peak/grids.lua',rk='/data/zones/reknor/grids.lua',lh='/data/zones/town-last-hope/grids.lua',
 gm='/data/zones/town-gates-of-morning/grids.lua',tt='/data/zones/tannen-tower/grids.lua',sf='/data/zones/shertul-fortress/grids.lua',
 dp='/data/zones/demon-plane/grids.lua',er='/data/zones/eruan/grids.lua',cs='/data/zones/charred-scar/grids.lua',
 rd='/data/zones/ruined-dungeon/grids.lua'}
local D={}
for k,f in pairs(F) do D[k]=loadDefs(f) end
local ZONE={hp='high-peak',rk='reknor',lh='town-last-hope',gm='town-gates-of-morning',tt='tannen-tower',sf='shertul-fortress',
 dp='demon-plane',er='eruan',cs='charred-scar',rd='ruined-dungeon'}
local function setZone(z) _G.game={zone={short_name=z}} end
local function place(set,id) return deep(assert(D[set][id],set..' '..id)) end
local function kind(g,z) return T.s14Kind(g,z) end
local function why(g,z) return T.s14Why(g,z) end

-- The reviewed callbacks are where the stamps say they are.
local function lineIs(file,line,pattern)
 local src=readFile(data..file:gsub('^/data',''))
 local i=0
 for l in (src..'\n'):gmatch('([^\n]*)\n') do i=i+1;if i==line then return l:match(pattern)~=nil end end
 return false
end
for _,c in ipairs{{F.hp,43,'on_use = function'},{F.hp,50,'on_added = function'},{F.hp,75,'on_use = function'},{F.hp,82,'on_added = function'},
 {F.hp,103,'on_added = function'},{F.hp,111,'local invocation_close = function'},{F.hp,192,'change_level_check = function'},
 {F.hp,197,'on_use = function'},{F.rk,43,'on_use = function'},{F.rk,57,'on_added = function'},{F.lh,51,'on_use = function'},
 {F.lh,58,'on_added = function'},{F.gm,52,'on_use = function'},{F.gm,59,'on_added = function'},{F.tt,35,'on_move = function'},
 {F.sf,119,'checkSpecialLocation = function'},{F.sf,142,'on_move = function'},{F.sf,208,'on_added = function'},{F.dp,32,'on_move = function'}} do
 eq(lineIs(c[1],c[2],c[3]),true,c[1]..':'..c[2]..' is '..c[3])
end

-- Stamps: exactly the listed ids of the listed files.
local listed={hp={'FAR_EAST_PORTAL','CFAR_EAST_PORTAL','WEST_PORTAL','CWEST_PORTAL','VOID_PORTAL','CVOID_PORTAL','ORB_UNDEATH',
 'ORB_ELEMENTS','ORB_DRAGON','ORB_DESTRUCTION','PORTAL_BOSS'},rk={'FAR_EAST_PORTAL','CFAR_EAST_PORTAL'},
 lh={'FAR_EAST_PORTAL','CFAR_EAST_PORTAL'},gm={'WEST_PORTAL','CWEST_PORTAL'},tt={'PORTAL_BACK'},sf={'FARPORTAL','CFARPORTAL'},dp={'PORTAL_BACK'}}
local stamped=0
for set,defs in pairs(D) do
 local want={};for _,id in ipairs(listed[set] or {}) do want[id]=true end
 for id,g in pairs(defs) do
  local s=rawget(g,'_checker_s14_source')
  if want[id] then
   eq(s~=nil and s.file==F[set] and s.id==id,true,'S14 stamp '..set..' '..id);stamped=stamped+1
  else eq(s,nil,'no S14 stamp '..set..' '..id) end
 end
end
eq(stamped,21,'S14 stamped definitions')
eq(D.hp.CFAR_EAST_PORTAL._checker_s14_source.funcs,'on_added@@'..F.hp..':50,orb_portal.on_use@@'..F.hp..':43','S14 centre callbacks (nested)')
eq(D.hp.ORB_DRAGON._checker_s14_source.funcs,'orb_command.special@@'..F.hp..':111','S14 invocation callback')
eq(D.hp.PORTAL_BOSS._checker_s14_source.funcs,'change_level_check@@'..F.hp..':192,orb_portal.on_use@@'..F.hp..':197','S14 Sanctum callbacks')

-- Every listed identity in its zone: the reviewed kind.
local expect={
 hp={FAR_EAST_PORTAL='floor',CFAR_EAST_PORTAL='prop',WEST_PORTAL='floor',CWEST_PORTAL='prop',VOID_PORTAL='floor',CVOID_PORTAL='prop',
  ORB_UNDEATH='prop',ORB_ELEMENTS='prop',ORB_DRAGON='prop',ORB_DESTRUCTION='prop',PORTAL_BOSS='prop'},
 rk={FAR_EAST_PORTAL='floor',CFAR_EAST_PORTAL='prop'},lh={FAR_EAST_PORTAL='floor',CFAR_EAST_PORTAL='prop'},
 gm={WEST_PORTAL='floor',CWEST_PORTAL='prop'},tt={PORTAL_BACK='prop'},sf={FARPORTAL='floor',CFARPORTAL='prop'},dp={PORTAL_BACK='lava-floor'}}
for set,ids in pairs(expect) do
 for id,k in pairs(ids) do
  setZone(ZONE[set])
  eq(kind(place(set,id),ZONE[set]),k,'S14 '..set..' '..id..' ('..tostring(why(place(set,id),ZONE[set]))..')')
  -- Zone scope: every other zone keeps it native.
  for _,z in ipairs{'high-peak','reknor','town-last-hope','town-gates-of-morning','tannen-tower','shertul-fortress','demon-plane',
   'charred-scar','eruan','sub-vault1-1','ruins-kor-pul'} do
   if z~=ZONE[set] then eq(kind(place(set,id),z),nil,'S14 '..set..' '..id..' outside '..z) end
  end
 end
end
-- Left native: Eruan (on_preuse, shoreline base), Charred Scar (lava ring),
-- Ruined Dungeon puzzle orbs.
for _,c in ipairs{{'er','CHARRED_SCAR_PORTAL'},{'er','CCHARRED_SCAR_PORTAL'},{'cs','FAR_EAST_PORTAL'},{'cs','CFAR_EAST_PORTAL'},{'rd','PORTAL'}} do
 setZone(ZONE[c[1]]);eq(kind(place(c[1],c[2]),ZONE[c[1]]),nil,'S14 stays native '..c[1]..' '..c[2])
 eq(T.classify(place(c[1],c[2])),nil,'S14 no stone kind '..c[1]..' '..c[2])
end
-- A copy of a listed definition under another list (the Charred Scar farportal
-- has the same id as High Peak's) is not accepted with that list's stamp.
do setZone('high-peak');local g=place('cs','FAR_EAST_PORTAL');g._checker_s14_source=D.hp.FAR_EAST_PORTAL._checker_s14_source
 eq(kind(g,'high-peak'),nil,'S14 Charred Scar copy with a High Peak stamp') end

-- Stone classify: ring floor, centre prop with the 3x3 base, portals with their layer.
setZone('high-peak')
do
 local k,d=T.classify(place('hp','CFAR_EAST_PORTAL'))
 eq(k,'prop','S14 classify centre');eq(d.image..'|'..d.display_x..'|'..d.display_y..'|'..d.display_w..'|'..d.display_h,
  'terrain/farportal-base.png|-1|-1|3|3','S14 centre layer is the native 3x3 base')
 eq(T.classify(place('hp','FAR_EAST_PORTAL')),'floor','S14 classify ring')
 k,d=T.classify(place('hp','ORB_DRAGON'));eq(k..'|'..d.image,'prop|terrain/demon_portal4.png','S14 classify invocation portal')
 k,d=T.classify(place('hp','PORTAL_BOSS'));eq(k..'|'..d.image,'prop|terrain/demon_portal4.png','S14 classify Sanctum portal')
 setZone('tannen-tower');k,d=T.classify(place('tt','PORTAL_BACK'));eq(k..'|'..d.image,'prop|terrain/demon_portal.png','S14 classify Tannen portal')
 setZone('shertul-fortress');eq(T.classify(place('sf','CFARPORTAL')),nil,'S14 fortress farportal is forest side only')
 setZone('demon-plane');eq(T.classify(place('dp','PORTAL_BACK')),nil,'S14 demon portal is forest side only')
end

-- Old saves and changed stamps.
for label,f in pairs{
 none=function(g) g._checker_s14_source=nil end,
 id=function(g) g._checker_s14_source=deep(g._checker_s14_source);g._checker_s14_source.id='WEST_PORTAL' end,
 file=function(g) g._checker_s14_source=deep(g._checker_s14_source);g._checker_s14_source.file=F.rk end,
 funcs=function(g) g._checker_s14_source=deep(g._checker_s14_source);g._checker_s14_source.funcs='' end,
 canon=function(g) g._checker_s14_source=deep(g._checker_s14_source);g._checker_s14_source.canon.image='string:x' end,
 canon_extra=function(g) g._checker_s14_source=deep(g._checker_s14_source);g._checker_s14_source.canon.lore='string:x' end} do
 setZone('high-peak');local g=place('hp','CFAR_EAST_PORTAL');f(g);eq(kind(g,'high-peak'),nil,'S14 stamp negative '..label)
end

-- Callbacks: wrapped, foreign, removed, added, nested.
do
 setZone('high-peak')
 local g=place('hp','CFAR_EAST_PORTAL');local f=g.on_added;g.on_added=function(...) return f(...) end
 eq(kind(g,'high-peak'),nil,'S14 wrapped on_added')
 g=place('hp','CFAR_EAST_PORTAL');g.on_added=D.rk.CFAR_EAST_PORTAL.on_added;eq(kind(g,'high-peak'),nil,'S14 foreign on_added')
 g=place('hp','CFAR_EAST_PORTAL');g.on_added=nil;eq(kind(g,'high-peak'),nil,'S14 no on_added')
 g=place('hp','FAR_EAST_PORTAL');g.on_move=function() end;eq(kind(g,'high-peak'),nil,'S14 extra callback')
 g=place('hp','FAR_EAST_PORTAL');g.orb_portal.on_use=function() end;eq(kind(g,'high-peak'),nil,'S14 nested on_use replaced')
 g=place('hp','FAR_EAST_PORTAL');g.orb_portal.on_preuse=function() end;eq(kind(g,'high-peak'),nil,'S14 nested on_preuse added')
 g=place('hp','FAR_EAST_PORTAL');g.orb_portal=nil;eq(kind(g,'high-peak'),nil,'S14 orb_portal removed (Eruan-style strip)')
 g=place('hp','FAR_EAST_PORTAL');g.orb_portal.change_zone='charred-scar';eq(kind(g,'high-peak'),nil,'S14 orb destination changed')
 g=place('hp','FAR_EAST_PORTAL');g.orb_portal.message='other words';eq(kind(g,'high-peak'),nil,'S14 orb message differs from the stamp')
 g=place('hp','ORB_DRAGON');g.orb_command.special=function() end;eq(kind(g,'high-peak'),nil,'S14 invocation special replaced')
 g=place('hp','ORB_DRAGON');g.orb_command.summon='undead';eq(kind(g,'high-peak'),nil,'S14 invocation summon changed')
 g=place('hp','ORB_DRAGON');g.orb_portal={nothing=true};eq(kind(g,'high-peak'),nil,'S14 invocation with an orb_portal')
 g=place('hp','ORB_DRAGON');g.on_stand=function() end;g.name='Invocation Portal: Dragons (fell aura)';eq(kind(g,'high-peak'),nil,'S14 aura event')
 g=place('hp','PORTAL_BOSS');g.change_level_check=nil;eq(kind(g,'high-peak'),nil,'S14 Sanctum without its check')
 g=place('hp','PORTAL_BOSS');g.change_level=2;eq(kind(g,'high-peak'),nil,'S14 Sanctum change_level')
end

-- Layers: exactly the native one.
do
 setZone('high-peak')
 for label,f in pairs{
  none=function(g) g.add_displays=nil end,
  two=function(g) g.add_displays[2]=init({image='terrain/farportal-base.png'}) end,
  image=function(g) g.add_displays[1].image='terrain/farportal-void-vortex.png' end,
  z=function(g) g.add_displays[1].z=18 end,
  size=function(g) g.add_displays[1].display_w=2 end,
  offset=function(g) g.add_displays[1].display_x=0 end,
  shader=function(g) g.add_displays[1].shader='x' end,
  mos=function(g) g.add_mos={{image='x.png'}} end,
  nested=function(g) g.add_displays[1].add_mos={{image='x.png'}} end,
  embed=function(g) g.add_displays[1].embed_particles={{name='x'}} end,
  particle=function(g) g.add_displays[1].__particles[{def='x'}]=true end,
  own_particle=function(g) g.__particles[{def='farportal_vortex'}]=true end} do
  local g=place('hp','CFAR_EAST_PORTAL');f(g);eq(kind(g,'high-peak'),nil,'S14 layer negative '..label)
 end
 for label,f in pairs{
  none=function(g) g.add_mos=nil end,two=function(g) g.add_mos[2]={image='terrain/demon_portal4.png'} end,
  image=function(g) g.add_mos[1].image='terrain/demon_portal3.png' end,field=function(g) g.add_mos[1].display_y=-1 end,
  displays=function(g) g.add_displays={init({image='invis.png'})} end} do
  local g=place('hp','ORB_UNDEATH');f(g);eq(kind(g,'high-peak'),nil,'S14 mos negative '..label)
 end
 local g=place('hp','FAR_EAST_PORTAL');g.add_displays={init({image='invis.png'})};eq(kind(g,'high-peak'),nil,'S14 ring with a layer')
end

-- Mutation negatives: every own field changed, removed, and extra fields,
-- on each listed identity.
local function other(v)
 local t=type(v)
 if t=='string' then return v..'x' elseif t=='number' then return v+1 elseif t=='boolean' then return not v end
 local c=deep(v);c.extra_field=true;return c
end
local mutated=0
for set,ids in pairs(expect) do
 setZone(ZONE[set])
 for id in pairs(ids) do
  local base=place(set,id)
  for k,v in pairs(base) do
   if type(k)=='string' and k:sub(1,1)~='_' and type(v)~='function' then
    local g=deep(base);g[k]=other(v)
    eq(kind(g,ZONE[set]),nil,'S14 changed '..set..' '..id..' '..k);mutated=mutated+1
    g=deep(base);g[k]=nil
    eq(kind(g,ZONE[set]),nil,'S14 removed '..set..' '..id..' '..k);mutated=mutated+1
   end
  end
  for k,v in pairs{does_block_move=true,block_move=function() return true end,block_sight=true,on_move=function() end,
   dig='FLOOR',can_pass={pass_wall=1},air_level=-10,pass_projectile=true,change_level=3,change_zone='wilderness',
   special_minimap={r=1},z=9,display_x=0.1,shader='water',textures={},lore='x',x=1,y=1,on_stand_safe=true,block_sense=true,
   type='floor',subtype='floor',special=true,door_opened='X',orbed=true,broken=true,lever=1} do
   if base[k]==nil then
    local g=deep(base);g[k]=v
    eq(kind(g,ZONE[set]),nil,'S14 extra '..set..' '..id..' '..k);mutated=mutated+1
   end
  end
  local g=deep(base);g[1]=true;eq(kind(g,ZONE[set]),nil,'S14 numeric key '..id);mutated=mutated+1
  -- A foreign replacement display is not ours.
  g=deep(base);g.replace_display={image='foreign.png'};eq(kind(g,ZONE[set]),nil,'S14 foreign replace_display '..id);mutated=mutated+1
 end
end
eq(mutated>900,true,'S14 mutation count '..mutated)

-- The one accepted in-place state: invocation_close (high-peak/grids.lua:111-127).
setZone('high-peak')
local function close(g)
 g.name=('%s (disabled)'):tformat(_t(g.name))
 g.color_r=colors.WHITE.r;g.color_g=colors.WHITE.g;g.color_b=colors.WHITE.b
 g:removeAllMOs()
 return g
end
for _,id in ipairs{'ORB_UNDEATH','ORB_ELEMENTS','ORB_DRAGON','ORB_DESTRUCTION'} do
 local g=close(place('hp',id))
 eq(kind(g,'high-peak'),'prop','S14 closed invocation portal keeps its board display '..id)
 local k,d=T.classify(g);eq(k..'|'..d.image,'prop|terrain/demon_portal4.png','S14 closed portal keeps its native art '..id)
 -- Only exactly that write.
 for label,f in pairs{name=function(x) x.name=x.name..'!' end,colour=function(x) x.color_g=254 end,
  back=function(x) x.color_br=0 end,half=function(x) x.name=D.hp[id].name..' (disabled)';x.color_r=1 end,
  other=function(x) x.desc='x' end} do
  local x=close(place('hp',id));f(x);eq(kind(x,'high-peak'),nil,'S14 closed negative '..label..' '..id)
 end
 -- Not for the farportals or the Sanctum portal.
end
for _,id in ipairs{'FAR_EAST_PORTAL','CFAR_EAST_PORTAL','PORTAL_BOSS'} do
 local g=place('hp',id);g.name=('%s (disabled)'):tformat(g.name);g.color_r=255;g.color_g=255;g.color_b=255
 eq(kind(g,'high-peak'),nil,'S14 no closed state for '..id)
end
do local g=place('hp','ORB_UNDEATH');g.name='Invocation Portal: Undeath (disabled)';eq(kind(g,'high-peak'),nil,'S14 renamed without the colour') end

-- Stone adapter: a mocked 5x5 sanctum corner: HARDWALL border, a 3x3 farportal.
local function mockMap(w,h,fill)
 local m={w=w,h=h,map={},attr={},updates={},seen={},rem={}}
 for x=0,w-1 do for y=0,h-1 do m.map[x+y*w]={[1]=fill(x,y)} end end
 m.attrs=function(x,y,k,v) local a=m.attr[x+y*w] or {};m.attr[x+y*w]=a;if v~=nil then a[k]=v end;return a[k] end
 m.seens=function(x,y) return m.seen[x+y*w] and true or false end
 m.infovs=m.seens
 m.remembers=setmetatable({},{__call=function(_,x,y) return m.rem[x+y*w] and true or false end})
 m.updateMap=function(self,x,y) self.updates[#self.updates+1]=x..','..y end
 return setmetatable(m,{__call=function(self,x,y,layer,g)
  if x<0 or y<0 or x>=w or y>=h then return end
  if g then self.map[x+y*w][layer or 1]=g;self:updateMap(x,y);return end
  return self.map[x+y*w][layer or 1]
 end})
end
do
 local ring=place('hp','FAR_EAST_PORTAL') -- one entity on all eight ring cells, as the quest/static placement
 local sm=mockMap(5,5,function(x,y)
  if x==0 or y==0 or x==4 or y==4 then return place('hp','HARDWALL') end
  if x==2 and y==2 then return place('hp','CFAR_EAST_PORTAL') end
  return ring
 end)
 _G.game={zone={short_name='high-peak'},level={map=sm}}
 for x=0,4 do for y=0,4 do sm.seen[x+y*5]=true;sm.rem[x+y*5]=true end end
 local rules={}
 for x=0,4 do for y=0,4 do
  local g=sm(x,y,1);local r={}
  for k,v in pairs(g) do if type(k)=='string' and k:sub(1,1)~='_' then r[k]=v end end;rules[x..','..y]=r
 end end
 for x=0,4 do for y=0,4 do T.observe(sm,x,y,sm(x,y,1)) end end
 local c=T.render(sm,2,2,sm(2,2,1),'refined')
 eq(c.image:match('^checker%-revised%+refined/korpul/floor%-[ab]%-0%-[01]%.png$')~=nil,true,'S14 centre draws board floor '..c.image)
 local d=c.add_displays and c.add_displays[1]
 eq(d and d.image,'terrain/farportal-base.png','S14 centre keeps the native 3x3 base')
 eq(d.display_x..','..d.display_y..','..d.display_w..','..d.display_h,'-1,-1,3,3','S14 base keeps its 3x3 geometry')
 eq(d.z,nil,'S14 base z as native')
 for _,p in ipairs{{1,1},{2,1},{3,1},{1,2},{3,2},{1,3},{2,3},{3,3}} do
  local r=T.render(sm,p[1],p[2],sm(p[1],p[2],1),'refined')
  eq(r.image:match('refined/korpul/floor%-')~=nil and r.add_displays==nil,true,'S14 ring '..p[1]..','..p[2]..' board floor')
 end
 -- Native mode: the native snapshot (marble floor + the same base).
 local nat=T.render(sm,2,2,sm(2,2,1),'vanilla')
 eq(nat.image,'terrain/marble_floor.png','S14 native snapshot image')
 eq(nat.add_displays[1].image..','..nat.add_displays[1].display_w,'terrain/farportal-base.png,3','S14 native snapshot base')
 eq(T.render(sm,1,1,sm(1,1,1),'vanilla').image,'terrain/marble_floor.png','S14 native ring snapshot')
 -- Rules untouched, the shared ring entity untouched.
 for x=0,4 do for y=0,4 do
  local g=sm(x,y,1)
  for k,v in pairs(rules[x..','..y]) do eq(g[k],v,'S14 stone rule '..x..','..y..' '..k) end
  for k in pairs(g) do if type(k)=='string' and k:sub(1,1)~='_' then eq(rules[x..','..y][k]~=nil,true,'S14 stone no new field '..k) end end
  eq(g.replace_display,nil,'S14 stone adapter installs no replace_display '..x..','..y)
 end end
 eq(sm(1,1,1)==ring and sm(3,3,1)==ring,true,'S14 shared ring entity stays shared')
 -- The walls around keep their mask: the portal cells are not walls.
 eq(T.render(sm,2,0,sm(2,0,1),'refined').image:match('refined/korpul/hardwall%-')~=nil,true,'S14 wall beside the portal')
end
-- Invocation portal on the stone side: closing keeps the same board display.
do
 local om=mockMap(1,1,function() return place('hp','ORB_DRAGON') end)
 _G.game={zone={short_name='high-peak'},level={map=om}}
 om.seen[0]=true;om.rem[0]=true
 T.observe(om,0,0,om(0,0,1))
 local a=T.render(om,0,0,om(0,0,1),'refined')
 eq(a.add_displays[1].image,'terrain/demon_portal4.png','S14 invocation portal layer over the board floor')
 close(om(0,0,1));T.observe(om,0,0,om(0,0,1))
 local b=T.render(om,0,0,om(0,0,1),'refined')
 eq(b.image..'|'..b.add_displays[1].image,a.image..'|'..a.add_displays[1].image,'S14 closed invocation portal: same board display')
 eq(om(0,0,1).name,'Invocation Portal: Dragons (disabled)','S14 the native write stays')
 -- An old-save (unstamped) portal stays native.
 local old=place('hp','ORB_DRAGON');old._checker_s14_source=nil;eq(T.classify(old),nil,'S14 old-save invocation portal')
end

-- Forest side: the Sher'Tul exploratory farportal (fortress family).
do
 T.batch5Assets=T.batch5Assets or {}
 local ring=place('sf','FARPORTAL')
 local fm=mockMap(5,5,function(x,y)
  if x==0 or y==0 or x==4 or y==4 then return place('sf','SOLID_FLOOR') end
  if x==2 and y==2 then return place('sf','CFARPORTAL') end
  return ring
 end)
 local host={zone={short_name='shertul-fortress'},level={map=fm,data={},level=1}}
 _G.game={zone=host.zone,level=host.level,log=function() end}
 local function img(x,y) local g=fm(x,y,1);return g.replace_display and g.replace_display.image end
 mode='refined';T.apply(host)
 eq(img(2,2),'checker-revised+refined/shertul/floor0.png','S14 fortress farportal centre on the board floor')
 eq(img(1,1),'checker-revised+refined/shertul/floor0.png','S14 fortress farportal ring on the board floor')
 eq(img(0,0),'checker-revised+refined/shertul/floor0.png','fortress floor (existing)')
 local d=fm(2,2,1).replace_display.add_displays[1]
 eq(d.image..'|'..d.display_x..'|'..d.display_y..'|'..d.display_w..'|'..d.display_h,'terrain/farportal-base.png|-1|-1|3|3','S14 fortress base layer')
 eq(fm(1,1,1).replace_display.add_displays,nil,'S14 fortress ring has no layer')
 eq(kind(fm(2,2,1),'shertul-fortress'),'prop','S14 still exact with its own board display installed')
 eq(fm(1,1,1)~=fm(2,1,1),true,'S14 the forest adapter clones each ring cell before installing')
 mode='vanilla';T.apply(host)
 eq(fm(2,2,1).replace_display,nil,'S14 fortress native mode restores the native display')
 mode='refined';T.apply(host)
 eq(img(2,2),'checker-revised+refined/shertul/floor0.png','S14 fortress restored')
 -- Old save: unstamped farportal stays native.
 local om=mockMap(1,1,function() local g=place('sf','CFARPORTAL');g._checker_s14_source=nil;return g end)
 local oh={zone={short_name='shertul-fortress'},level={map=om,data={},level=1}}
 _G.game={zone=oh.zone,level=oh.level,log=function() end}
 T.apply(oh);eq(om(0,0,1).replace_display,nil,'S14 old-save fortress farportal stays native')
end
-- Forest side: the Demon Plane's return portal (scorch family lava floor).
do
 local dm=mockMap(3,1,function(x) return x==1 and place('dp','PORTAL_BACK') or place('dp','LAVA_FLOOR') end)
 local host={zone={short_name='demon-plane'},level={map=dm,data={},level=1}}
 _G.game={zone=host.zone,level=host.level,log=function() end}
 mode='refined';T.apply(host)
 local g=dm(1,0,1)
 eq(g.replace_display and g.replace_display.image,'checker-revised+refined/daikara/lava-floor1.png','S14 demonic portal on the board lava floor')
 eq(g.replace_display.add_displays[1].image,'terrain/demon_portal.png','S14 demonic portal keeps its native portal layer')
 eq(dm(0,0,1).replace_display.image,'checker-revised+refined/daikara/lava-floor0.png','demon plane lava floor (existing)')
 mode='vanilla';T.apply(host);eq(dm(1,0,1).replace_display,nil,'S14 demon portal native mode')
 mode='refined';T.apply(host)
end

-- Grid.lua stamps the two new lists; Eruan/Charred Scar portals are not listed.
local grid=readFile(root..'superload/mod/class/Grid.lua')
eq(grid:find("file=='/data/zones/shertul-fortress/grids.lua'",1,true)~=nil,true,'Grid.lua stamps shertul-fortress/grids.lua')
eq(grid:find("file=='/data/zones/demon-plane/grids.lua'",1,true)~=nil,true,'Grid.lua stamps demon-plane/grids.lua')
eq(grid:find("charred%-scar")==nil,true,'Grid.lua does not stamp the Charred Scar list')
-- Zone.lua repaints around a forest-side exact portal placed by addEntity
-- (Draebor's on_die places the Demon Plane portal without a NicerTiles pass).
local zsl=readFile(root..'superload/engine/Zone.lua')
eq(zsl:find('Terrain.s14ForestKind(after)',1,true)~=nil,true,'Zone.lua repairs around a placed forest-side portal')
setZone('demon-plane');eq(T.s14ForestKind(place('dp','PORTAL_BACK')),'lava-floor','S14 forest kind for the repaint hook')
setZone('high-peak');eq(T.s14ForestKind(place('hp','CFAR_EAST_PORTAL')),nil,'S14 stone-side portal needs no repaint hook')
setZone('eruan');eq(T.s14ForestKind(place('dp','PORTAL_BACK')),nil,'S14 repaint hook scoped to the zone')
print('terrain_s14: '..n..' checks passed (native definitions and callbacks + mocked map/renderer; no live-game claim)')
