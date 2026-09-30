-- S13 (Ardhungol's unstable wormhole T2; S12 stone-kerb deep water in
-- Dreadfell and High Peak). Run from any cwd with Lua 5.1/LuaJIT. The native
-- zone lists are built the way Entity:loadList/Entity:init build them (real
-- engine colours, base import, colour/back colour/tint normalisation,
-- resolvers kept as tables until placement) and stamped per finished file (the
-- superload/mod/class/Grid.lua order). A placed wormhole resolves its generic
-- resolver the way Entity:resolve does (the numeric slot is cleared and the
-- grid gets its own "wormhole" emitter, whose args gain the particle file's
-- base_size=64). The cave family is exercised through T.apply / T.repair on a
-- mocked Ardhungol level, the deep water through the stone adapter.
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
local T=loadWith(root..'overload/mod/class/CheckerTerrain.lua',env);modules['mod.class.CheckerTerrain']=T
T.assets.ready=true;setmetatable(T.assets.files,{__index=function() return true end})

local cenv=setmetatable({},{__index=_G})
loadWith(root..'../../engines/default/engine/colors.lua',cenv)
local colors=cenv.colors
eq(colors.GREY.r..','..colors.DARK_UMBER.r..','..colors.DARK_UMBER.g..','..colors.DARK_UMBER.b,'127,87,94,37','engine GREY / DARK_UMBER')

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
-- engine/resolvers.lua:172 (generic keeps its table until Entity:resolve).
local resolvers=setmetatable({generic=function(f) return {__resolver='generic',f} end,
 mbonus=function(max,add) return {__resolver='mbonus',__resolve_instant=true,max,add} end},
 {__index=function() return function(v) return v end end})
local Particles={new=function(def,radius,args) return {def=def,radius=radius or 1,args=args or {}} end}
local fenvBase={colors=colors,_t=function(s) return s end,resolvers=resolvers,
 engine={DamageType=setmetatable({},{__index=function(_,k) return k end}),Map={TERRAIN=1,ACTOR=2},Particles=Particles},
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
local ARD='/data/zones/ardhungol/grids.lua'
local D={ard=loadDefs(ARD),abashed=loadDefs('/data/zones/abashed-expanse/grids.lua'),
 dread=loadDefs('/data/zones/dreadfell/grids.lua'),hp=loadDefs('/data/zones/high-peak/grids.lua'),
 water=loadDefs('/data/general/grids/water.lua'),vor=loadDefs('/data/zones/vor-armoury/grids.lua'),
 tannen=loadDefs('/data/zones/tannen-tower/grids.lua')}
local function setZone(z) _G.game={zone={short_name=z}} end
-- A placed grid: a clone, resolved (Entity:resolve: generic runs, its slot
-- becomes nil; the emitter is the grid's own, args with the loader's base_size).
local function place(set,id)
 local g=deep(assert(D[set][id],set..' '..id))
 for k,v in pairs(g) do
  if type(v)=='table' and v.__resolver=='generic' then
   g[k]=nil
   local self={addParticles=function(_,p) p.args.base_size=64;g.__particles[p]=true;return p end}
   v[1](self)
  end
 end
 return g
end
local function kind(g,z) return T.s13Kind(g,z or 'ardhungol') end
local function ser(v)
 if type(v)~='table' then return type(v)..':'..tostring(v) end
 local keys={};for k in pairs(v) do if type(k)~='string' or k:sub(1,1)~='_' then keys[#keys+1]=k end end
 table.sort(keys,function(a,b) return tostring(a)<tostring(b) end)
 local out={};for _,k in ipairs(keys) do out[#out+1]=tostring(k)..'='..ser(v[k]) end
 return '{'..table.concat(out,';')..'}'
end

-- Stamps: only ardhungol/grids.lua's WORMHOLE, with its own callback and image.
local st=D.ard.WORMHOLE._checker_s13_source
eq(st.file..'|'..st.id..'|'..st.funcs..'|'..st.image,ARD..'|WORMHOLE|damage_project@@'..ARD..':28|terrain/cave/cave_floor_1_01.png','stamp WORMHOLE')
eq(D.ard.CAVEFLOOR._checker_s13_source,nil,'cave floor not stamped')
eq(D.ard.CAVEWALL._checker_s13_source,nil,'cave wall not stamped')
eq(D.abashed.WORMHOLE._checker_s13_source,nil,'Abashed wormhole (T3, quest exit) not stamped')
eq(D.ard.WORMHOLE._checker_cave_source.id,'CAVEFLOOR','the base import keeps the CAVEFLOOR cave stamp (id differs: caveTerrain rejects)')
eq(D.ard.CAVEFLOOR._checker_def.id,'CAVEFLOOR','nested definitions keep their own def stamp')

-- The placed wormhole (as surveyed live): exact, one native emitter.
setZone('ardhungol')
local w=place('ard','WORMHOLE')
eq(w[1],nil,'resolver slot cleared')
do local c=0;for p in pairs(w.__particles) do c=c+1;eq(p.def,'wormhole','emitter definition') end;eq(c,1,'one emitter') end
eq(kind(w),'floor','S13 wormhole is cave floor on the board')
eq(T.caveTerrain(w),nil,'caveTerrain alone still rejects the wormhole')
eq(T.classify(w),nil,'no stone kind for the wormhole')
-- Zone scope.
for _,z in ipairs{'abashed-expanse','high-peak','unremarkable-cave','valley-moon-caverns','dreadfell','ruins-kor-pul','sub-vault1-1'} do
 eq(kind(w,z),nil,'S13 wormhole outside Ardhungol: '..z)
end
eq(kind(place('abashed','WORMHOLE'),'ardhungol'),nil,'Abashed wormhole copy stays native')
eq(kind(place('abashed','WORMHOLE'),'abashed-expanse'),nil,'Abashed wormhole stays native')
eq(kind(place('ard','CAVEFLOOR')),nil,'plain cave floor is not an S13 kind')

-- Old saves and changed stamps.
for label,f in pairs{
 none=function(g) g._checker_s13_source=nil end,
 id=function(g) g._checker_s13_source=deep(g._checker_s13_source);g._checker_s13_source.id='CAVEFLOOR' end,
 file=function(g) g._checker_s13_source=deep(g._checker_s13_source);g._checker_s13_source.file='/data/zones/abashed-expanse/grids.lua' end,
 funcs=function(g) g._checker_s13_source=deep(g._checker_s13_source);g._checker_s13_source.funcs='' end,
 image=function(g) g._checker_s13_source=deep(g._checker_s13_source);g._checker_s13_source.image='terrain/cave/cave_floor_2_01.png' end} do
 local g=place('ard','WORMHOLE');f(g);eq(kind(g),nil,'S13 stamp negative '..label)
end

-- Callbacks: wrapped, foreign, removed, added (the fell-aura event cell).
do
 local g=place('ard','WORMHOLE');local f=g.damage_project;g.damage_project=function(...) return f(...) end
 eq(kind(g),nil,'S13 wrapped damage_project')
 g=place('ard','WORMHOLE');g.damage_project=D.abashed.WORMHOLE.damage_project;eq(kind(g),nil,'S13 foreign damage_project')
 g=place('ard','WORMHOLE');g.damage_project=nil;eq(kind(g),nil,'S13 no damage_project')
 g=place('ard','WORMHOLE');g.on_stand=function() end;g.name='unstable wormhole (fell aura)';g.always_remember=true
 eq(kind(g),nil,'S13 aura event wormhole stays native')
 g=place('ard','WORMHOLE');g.on_move=function() end;eq(kind(g),nil,'S13 extra callback')
end

-- The emitter: exactly the native one.
for label,f in pairs{
 none=function(g) g.__particles={} end,
 missing=function(g) g.__particles=nil end,
 two=function(g) g.__particles[{def='wormhole',radius=1,args={base_size=64}}]=true end,
 def=function(g) next(g.__particles).def='generic_sploom' end,
 radius=function(g) next(g.__particles).radius=2 end,
 shader=function(g) next(g.__particles).shader={type='x'} end,
 toback=function(g) next(g.__particles).toback=true end,
 sub=function(g) next(g.__particles).subps={} end,
 args_extra=function(g) next(g.__particles).args.image='x' end,
 args_size=function(g) next(g.__particles).args.base_size=32 end,
 args_missing=function(g) next(g.__particles).args=nil end,
 value=function(g) local p=next(g.__particles);g.__particles[p]=1 end,
 embed=function(g) g.embed_particles={{name='wormhole'}} end} do
 local g=place('ard','WORMHOLE');f(g);eq(kind(g),nil,'S13 emitter '..label)
end
do local g=place('ard','WORMHOLE');next(g.__particles).args.base_size=nil;eq(kind(g),'floor','S13 emitter args before the loader ran') end

-- Mutation negatives: every own field changed, removed, and extra fields.
local function other(v)
 local t=type(v)
 if t=='string' then return v..'x' elseif t=='number' then return v+1 elseif t=='boolean' then return not v end
 local c=deep(v);c.extra_field=true;return c
end
local mutated=0
do
 local base=place('ard','WORMHOLE')
 for k,v in pairs(base) do
  if type(k)=='string' and k:sub(1,1)~='_' and type(v)~='function' then
   local g=deep(base);g[k]=other(v)
   eq(kind(g),nil,'S13 changed '..k);mutated=mutated+1
   g=deep(base);g[k]=nil
   eq(kind(g),nil,'S13 removed '..k);mutated=mutated+1
  end
 end
 for k,v in pairs{does_block_move=true,block_move=function() return true end,block_sight=true,on_move=function() end,
  dig='CAVEFLOOR',can_pass={pass_wall=1},air_level=-10,pass_projectile=true,change_level=1,change_zone='wilderness',
  special_minimap={r=1},z=9,display_x=0.1,shader='water',textures={},add_mos={{image='terrain/cave/cave_rock_1_01.png'}},
  add_displays={{image='invis.png'}},replace_display={image='x.png'},notice=true,always_remember=true,special=true,lore='x',
  x=1,y=1,on_stand_safe=true,block_sense=true} do
  local g=deep(base);g[k]=v
  eq(kind(g),nil,'S13 extra '..k);mutated=mutated+1
 end
 local g=deep(base);g[1]=true;eq(kind(g),nil,'S13 numeric key');mutated=mutated+1
end
eq(mutated>55,true,'S13 mutation count '..mutated)

-- Cave family: a mocked Ardhungol level through T.apply / T.repair.
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
local plan={'###','#*.','#.*'}
local sym={['#']='CAVEWALL',['.']='CAVEFLOOR',['*']='WORMHOLE'}
local m=mockMap(3,3,function(x,y) return place('ard',sym[plan[y+1]:sub(x+1,x+1)]) end)
local host={zone={short_name='ardhungol',max_level=3},level={map=m,data={},level=1}}
_G.game={zone=host.zone,level=host.level,log=function() end}
local emitters,rules={}, {}
for x=0,2 do for y=0,2 do
 local g=m(x,y,1)
 emitters[x..','..y]=g.define_as=='WORMHOLE' and next(g.__particles) or nil
 local r={};for k,v in pairs(g) do if type(k)=='string' and k:sub(1,1)~='_' and k~='replace_display' then r[k]=v end end;rules[x..','..y]=r
end end
local function img(x,y) local g=m(x,y,1);return g.replace_display and g.replace_display.image end
local function same(x,y) local g=m(x,y,1);local p=next(g.__particles or {});return p~=nil and p.def==emitters[x..','..y].def and next(g.__particles,p)==nil end
mode='refined';T.apply(host)
eq(img(1,1),'checker-revised+refined/cave/floor0.png','S13 wormhole (1,1) on board cave floor')
eq(img(2,2),'checker-revised+refined/cave/floor0.png','S13 wormhole (2,2) on board cave floor')
eq(img(2,1),'checker-revised+refined/cave/floor1.png','plain cave floor unchanged')
eq(img(0,0):match('refined/cave/wall%-')~=nil,true,'cave wall unchanged')
eq(m(1,1,1).replace_display.add_displays,nil,'S13 wormhole adds no board layer (the emitter is the wormhole)')
eq(same(1,1),true,'S13 the grid keeps its one native emitter')
eq(same(2,2),true,'S13 the grid keeps its one native emitter (2,2)')
eq(kind(m(1,1,1)),'floor','S13 still exact with its own board display installed')
do local g=m(1,1,1);local d=g.replace_display;g.replace_display={image='foreign.png'};eq(kind(g),nil,'S13 foreign replace_display');g.replace_display=d end
-- A wall next to the wormhole does not count it as wall.
eq(img(1,0),'checker-revised+refined/cave/wall-'..(2+8+0)..'-1.png','wall mask ignores the wormhole (E+W walls)')
-- Rules untouched.
local function rulesSame(label)
 for x=0,2 do for y=0,2 do
  local g=m(x,y,1)
  for k,v in pairs(rules[x..','..y]) do eq(ser(g[k]),ser(v),label..' rule '..x..','..y..' '..k) end
  for k in pairs(g) do if type(k)=='string' and k:sub(1,1)~='_' and k~='replace_display' then eq(rules[x..','..y][k]~=nil,true,label..' no new field '..k) end end
 end end
end
rulesSame('refined')
-- Refined -> Native -> Refined: native display back, emitter kept, then the same board file.
mode='vanilla';T.apply(host)
eq(m(1,1,1).replace_display,nil,'S13 native mode restores the native display')
eq(m(1,1,1)._checker_terrain,nil,'S13 native mode clears the board state')
eq(same(1,1),true,'S13 native mode keeps the emitter')
rulesSame('native')
mode='refined';T.apply(host)
eq(img(1,1),'checker-revised+refined/cave/floor0.png','S13 restored board floor')
eq(same(1,1),true,'S13 restored emitter')
rulesSame('restored')
-- The native spell interaction never changes the grid; a NicerTiles-style
-- replacement by another grid is repaired by the existing repair path.
m(2,2,1,place('ard','CAVEFLOOR'));T.repair(host,1,1,2,2)
eq(img(2,2),'checker-revised+refined/cave/floor0.png','repair: a replaced wormhole cell draws its new cave floor')
-- Old-save wormhole on a live level stays native (no board display).
do
 local om=mockMap(1,1,function() local g=place('ard','WORMHOLE');g._checker_s13_source=nil;return g end)
 local oh={zone={short_name='ardhungol',max_level=3},level={map=om,data={},level=1}}
 _G.game={zone=oh.zone,level=oh.level,log=function() end}
 T.apply(oh);eq(om(0,0,1).replace_display,nil,'S13 old-save wormhole stays native')
end
-- Blockout mode draws the grass of the blockout set (existing cave rule).
_G.game={zone=host.zone,level=host.level,log=function() end}
mode='blockout';T.apply(host);eq(img(1,1),'checker-revised+grass0.png','blockout wormhole');mode='refined';T.apply(host)

-- Deep water: the S12 contract now also in Dreadfell and High Peak.
for _,c in ipairs{{'dread','dreadfell'},{'hp','high-peak'},{'water','dreadfell'},{'water','high-peak'},{'vor','vor-armoury'}} do
 setZone(c[2]);local g=place(c[1],'DEEP_WATER')
 eq(T.classify(g),'deep-stone','S13 deep water '..c[1]..' in '..c[2])
 eq(T.s12Kind(g,c[2]),'deep-stone','S13 deep water kind '..c[1]..' in '..c[2])
end
for _,c in ipairs{{'tannen','tannen-tower'},{'water','rhaloren-camp'},{'water','ruins-kor-pul'},{'water','eruan'},
 {'water','vor-pride'},{'water','gorbat-pride'},{'water','grushnak-pride'},{'water','halfling-ruins'},{'water','sub-vault1-1'},
 {'water','trollmire'},{'water','old-forest'},{'water','lake-nur'}} do
 setZone(c[2]);eq(T.s12Kind(place(c[1],'DEEP_WATER'),c[2]),nil,'S13 deep water scope '..c[1]..' in '..c[2])
end
for _,z in ipairs{'dreadfell','high-peak'} do
 setZone(z)
 for label,f in pairs{stamp=function(g) g._checker_s12_source=nil end,image=function(g) g.image='terrain/water_floor.png' end,
  callback=function(g) g.on_stand=function() end end,extra=function(g) g.lore='x' end,layer=function(g) g.add_displays={{image='invis.png'}} end,
  shader=function(g) g.shader=nil end,air=function(g) g.air_level=-10 end} do
  local g=place('water','DEEP_WATER');f(g);eq(T.classify(g),nil,'S13 deep water negative '..label..' in '..z)
 end
 for _,id in ipairs{'DEEP_OCEAN_WATER','SHALLOW_WATER','POISON_DEEP_WATER'} do
  if D.water[id] then eq(T.s12Kind(place('water',id),z),nil,'S13 other water stays native '..id..' in '..z) end
 end
 do local g=place('dread','LAVA_FLOOR5');g.mindam,g.maxdam=17,34;eq(T.s12Kind(g,z),'lava-hazard','S12 lava in '..z..' unchanged') end
end
-- The stone adapter draws the kerbed water in a Dreadfell vault pool.
do
 T.hazardAssets.ready=true;setmetatable(T.hazardAssets.files,{__index=function(_,k) return k:match('^checker%-revised%+refined/hazard/') and true or nil end})
 local vm=mockMap(3,1,function(x) return place('dread',x==0 and 'HARDWALL' or 'DEEP_WATER') end)
 _G.game={zone={short_name='dreadfell'},level={map=vm}}
 for x=0,2 do vm.seen[x]=true;vm.rem[x]=true end
 for x=0,2 do T.observe(vm,x,0,vm(x,0,1)) end
 eq(T.render(vm,1,0,vm(1,0,1),'refined').image,'checker-revised+refined/hazard/deep-2-1.png','S13 Dreadfell pool mask E')
 eq(T.render(vm,2,0,vm(2,0,1),'refined').image,'checker-revised+refined/hazard/deep-8-0.png','S13 Dreadfell pool mask W')
 eq(T.render(vm,1,0,vm(1,0,1),'vanilla').shader,'water','S13 native snapshot keeps the water shader')
 eq(vm(1,0,1).replace_display,nil,'S13 stone adapter installs no replace_display')
end

-- The plain FLOOR beside a High Peak pool: the native marble-to-water edge
-- carrier (T21 rule, as in Dreadfell) is board floor; any other layer or
-- zone keeps native.
do
 local function edged(set,mo)
  local g=place(set,'FLOOR')
  g.add_displays={setmetatable({image='invis.png',add_mos=mo or {{image='terrain/marble_water/marble_floor_2_to_water_outer_4.png'},
   {image='terrain/marble_water/marble_floor_2_to_water_outer_8.png'}}},meta)}
  return g
 end
 setZone('high-peak');eq(T.classify(place('hp','FLOOR')),'floor','High Peak plain floor (existing)')
 eq(T.classify(edged('hp')),'floor','S13 High Peak floor with the native water edge')
 eq(T.classify(edged('hp',{{image='terrain/lava/lava_floor_2_02.png'}})),nil,'S13 High Peak floor with a foreign edge')
 do local g=edged('hp');g.add_displays[1].z=3;eq(T.classify(g),nil,'S13 High Peak edge carrier with z') end
 do local g=edged('hp');g.add_displays[2]=setmetatable({image='invis.png'},meta);eq(T.classify(g),nil,'S13 High Peak two carriers') end
 do local g=edged('hp');g._checker_zone_source=nil;eq(T.classify(g),nil,'S13 High Peak edge floor without the zone stamp (old save)') end
 setZone('dreadfell');eq(T.classify(edged('dread')),'floor','Dreadfell edge floor (existing T21)')
 setZone('eruan');eq(T.classify(edged('hp')),nil,'S13 edge floor outside the edge zones stays native')
end

-- Grid.lua stamps Ardhungol's list; the Abashed list stays unstamped.
local grid=readFile(root..'superload/mod/class/Grid.lua')
eq(grid:find("file=='/data/zones/ardhungol/grids.lua'",1,true)~=nil,true,'Grid.lua stamps ardhungol/grids.lua')
eq(grid:find("abashed%-expanse")==nil,true,'Grid.lua does not stamp the Abashed list')
-- The definition line the stamp pins.
local src=readFile(data..'/zones/ardhungol/grids.lua')
local line=0;for l in (src..'\n'):gmatch('([^\n]*)\n') do line=line+1;if line==28 then eq(l:match('damage_project = function')~=nil,true,'ardhungol/grids.lua:28 is damage_project') end end
print('terrain_s13: '..n..' checks passed (native definitions and callbacks + mocked map/renderer; no live-game claim)')
