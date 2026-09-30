-- S12 (damaging lava floor T19, Vor Armoury deep water T20). Run from any cwd
-- with Lua 5.1/LuaJIT. The native zone lists are built the way
-- Entity:loadList/Entity:init build them (real engine colours, base import,
-- colour/back colour/tint normalisation, nested load() mods such as Daikara's
-- and the Fearscape's on_stand strip) and stamped in the
-- superload/mod/class/Grid.lua order; placed cells get the mbonus resolvers
-- resolved as Entity:resolve does and, optionally, the native NicerTiles lava
-- border layer. The native lava on_stand itself runs against a mocked
-- DamageType. The stone adapter is exercised through observe/render on a
-- mocked map.
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

-- Real engine colours (engines/default/engine/colors.lua).
local cenv=setmetatable({},{__index=_G})
loadWith(root..'../../engines/default/engine/colors.lua',cenv)
local colors=cenv.colors
eq(colors.RED.r..','..colors.RED.g..','..colors.RED.b,'201,0,0','engine RED')
eq(colors.DARK_GREY.r..','..colors.AQUAMARINE.g..','..colors.DARK_BLUE.b..','..colors.BLUE.b,'67,255,147,227','engine water/lava colours')

local methods={}
local meta={__index=methods}
local function deep(t)
 if type(t)~='table' then return t end
 local o={};for k,v in pairs(t) do o[k]=deep(v) end
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
 return setmetatable(t,meta)
end
-- engine/resolvers.lua:87 (mbonus keeps its table until Entity:resolve).
local resolvers=setmetatable({mbonus=function(max,add) return {__resolver='mbonus',__resolve_instant=true,max,add} end},
 {__index=function() return function(v) return v end end})
local projected={}
local DamageType=setmetatable({get=function(self,t) return {projector=function(src,x,y,typ,dam) projected[#projected+1]={src=src,x=x,y=y,typ=typ,dam=dam};return 0 end} end},
 {__index=function(_,k) return k end})
local fenvBase={colors=colors,_t=function(s) return s end,resolvers=resolvers,
 engine={DamageType=DamageType,Map={TERRAIN=1}},
 rng={percent=function() return false end,range=function(a,b) return a end},currentZone={}}
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
local D={vor=loadDefs('/data/zones/vor-armoury/grids.lua'),hp=loadDefs('/data/zones/high-peak/grids.lua'),
 dread=loadDefs('/data/zones/dreadfell/grids.lua'),lava=loadDefs('/data/general/grids/lava.lua'),
 daikara=loadDefs('/data/zones/daikara/grids.lua'),scar=loadDefs('/data/zones/charred-scar/grids.lua'),
 demon=loadDefs('/data/zones/demon-plane/grids.lua'),spell=(function() _G.game={level={}};local d=loadDefs('/data/zones/demon-plane-spell/grids.lua');_G.game=nil;return d end)(),
 tannen=loadDefs('/data/zones/tannen-tower/grids.lua'),grushnak=loadDefs('/data/zones/grushnak-pride/grids.lua'),
 eruan=loadDefs('/data/zones/eruan/grids.lua'),water=loadDefs('/data/general/grids/water.lua')}
local Z={vor='vor-armoury',hp='high-peak',dread='dreadfell',lava='high-peak',daikara='daikara',scar='charred-scar',demon='demon-plane',
 spell='demon-plane-spell',tannen='tannen-tower',grushnak='grushnak-pride',eruan='eruan',water='vor-armoury'}
local function setZone(z) _G.game={zone={short_name=z}} end
-- A placed cell: clone + Entity:resolve of the mbonus resolvers (15-20 / 30-40).
local function place(set,id,mindam,maxdam)
 local g=deep(assert(D[set][id],set..' '..id))
 if type(g.mindam)=='table' then g.mindam=mindam or 17 end
 if type(g.maxdam)=='table' then g.maxdam=maxdam or 34 end
 return g
end
-- The native NicerTiles lava border (as surveyed): invis.png + edge MOs.
local function border(g)
 g.add_displays={init{image='invis.png',force_clone=true,add_mos={{image='terrain/lava/lava_floor_2_02.png',display_y=-1},
  {image='terrain/lava/lava_floor_6_04.png',display_x=-1},{image='terrain/lava/lava_floor_inner_9_03.png',display_x=1,display_y=-1}}}}
 g.force_clone=true
 return g
end

-- Stamps: own callbacks (field@file:line) and damage resolvers, per defining file.
local LAVA='/data/general/grids/lava.lua'
local st=D.vor.LAVA_FLOOR9._checker_s12_source
eq(st.file..'|'..st.id..'|'..st.funcs,LAVA..'|LAVA_FLOOR9|on_stand@@'..LAVA..':33','stamp LAVA_FLOOR9')
eq(st.mindam..'|'..st.maxdam,'mbonus{1=number:5;2=number:15}|mbonus{1=number:10;2=number:30}','stamp damage resolvers')
eq(D.daikara.LAVA_FLOOR3._checker_s12_source.funcs,'','Daikara strips the callback (stamp records it)')
eq(D.scar.LAVA_FLOOR._checker_s12_source.funcs,'','Charred Scar strips the base callback')
eq(D.spell.LAVA_FLOOR._checker_s12_source.funcs:match('demon%-plane%-spell/grids%.lua')~=nil,true,'Fearscape spell copy has its own callback')
eq(D.vor.DEEP_WATER._checker_s12_source.image,'terrain/water_grass_5_1.png','stamp DEEP_WATER image')
eq(D.vor.LAVA_WALL._checker_s12_source,nil,'lava wall not stamped')
eq(D.vor.LAVA._checker_s12_source,nil,'molten lava not stamped')
eq(D.vor.DEEP_OCEAN_WATER._checker_s12_source,nil,'ocean water not stamped')
eq(D.vor.FLOOR._checker_s12_source,nil,'floor not stamped')

-- Positives: every lava id in the three zones, with and without the border
-- layer and after the native on_stand ran; deep water in Vor Armoury.
local ids={'LAVA_FLOOR'};for i=1,16 do ids[#ids+1]='LAVA_FLOOR'..i end
for _,set in ipairs{'vor','hp','dread','lava'} do
 for _,z in ipairs{'vor-armoury','high-peak','dreadfell'} do
  setZone(z)
  for _,id in ipairs(ids) do
   eq(T.classify(place(set,id)),'lava-hazard','S12 lava '..set..' '..z..' '..id)
   eq(T.classify(border(place(set,id))),'lava-hazard','S12 lava with border '..set..' '..z..' '..id)
  end
 end
end
setZone('vor-armoury')
for _,d in ipairs{{15,30},{20,40},{15,40},{20,30}} do eq(T.classify(place('vor','LAVA_FLOOR5',d[1],d[2])),'lava-hazard','S12 lava damage bound '..d[1]..'/'..d[2]) end
do
 local g=border(place('vor','LAVA_FLOOR7'))
 projected={}
 g:on_stand(4,6,{player=false,reactionToward=function() return -1 end})
 eq(#projected,1,'native lava on_stand projects fire');eq(projected[1].typ,'FIRE','fire damage type')
 eq(projected[1].dam,17,'damage rng.range(mindam,maxdam)')
 eq(g.x..','..g.y,'4,6','native on_stand writes self.x/self.y')
 eq(T.classify(g),'lava-hazard','S12 lava still exact after the native on_stand')
 eq(T.s12Kind(g,'vor-armoury'),'lava-hazard','S12 kind probe')
end
eq(T.classify(place('vor','DEEP_WATER')),'deep-stone','S12 Vor Armoury deep water')
eq(T.classify(place('water','DEEP_WATER')),'deep-stone','S12 deep water from water.lua in Vor Armoury')

-- Zone scope and foreign copies stay native. (S13 extends the deep water to
-- Dreadfell and High Peak; tests/terrain_s13.lua checks those two zones.)
for _,c in ipairs{{'tannen','DEEP_WATER','tannen-tower'},
 {'vor','LAVA_FLOOR3','ruins-kor-pul'},{'vor','LAVA_FLOOR3','vor-pride'},{'grushnak','LAVA_FLOOR3','grushnak-pride'},
 {'tannen','LAVA_FLOOR3','tannen-tower'},{'eruan','LAVA_FLOOR3','eruan'},{'vor','LAVA_FLOOR3','gorbat-pride'},
 {'vor','LAVA_FLOOR3','sub-vault1234-5'},{'vor','LAVA_FLOOR3','charred-scar'},{'vor','LAVA_FLOOR3','daikara'},
 {'daikara','LAVA_FLOOR3','vor-armoury'},{'scar','LAVA_FLOOR','vor-armoury'},{'scar','LAVA_FLOOR3','high-peak'},
 {'demon','LAVA_FLOOR','dreadfell'},{'spell','LAVA_FLOOR','vor-armoury'},{'spell','LAVA_FLOOR','demon-plane-spell'},
 {'vor','LAVA','vor-armoury'},{'vor','LAVA_WALL3','vor-armoury'},{'vor','LAVA_LADDER_DOWN','vor-armoury'},
 {'vor','DEEP_OCEAN_WATER','vor-armoury'},{'vor','POISON_DEEP_WATER','vor-armoury'},{'vor','SHALLOW_WATER','vor-armoury'}} do
 local g=D[c[1]][c[2]]
 if g then setZone(c[3]);eq(T.s12Kind(place(c[1],c[2]),c[3]),nil,'S12 scope '..c[1]..' '..c[2]..' in '..c[3]) end
end
-- The harmless zone-local lava keeps its existing board kind, not the hazard.
setZone('charred-scar');eq(T.batch5Kind(place('scar','LAVA_FLOOR7'),'scorch'),'lava-floor','harmless Charred Scar lava unchanged')
eq(T.classify(place('scar','LAVA_FLOOR7')),nil,'harmless lava is not a stone hazard')
setZone('vor-armoury');eq(T.batch4Kind(place('vor','LAVA_FLOOR7'),'vor-armoury'),nil,'hazard lava has no forest kind')

-- Old saves / changed stamps.
setZone('vor-armoury')
for _,f in ipairs{function(g) g._checker_s12_source=nil end,
 function(g) g._checker_s12_source=deep(g._checker_s12_source);g._checker_s12_source.id='LAVA_FLOOR2' end,
 function(g) g._checker_s12_source=deep(g._checker_s12_source);g._checker_s12_source.file='/data/zones/vor-armoury/grids.lua' end,
 function(g) g._checker_s12_source=deep(g._checker_s12_source);g._checker_s12_source.funcs='' end,
 function(g) g._checker_s12_source=deep(g._checker_s12_source);g._checker_s12_source.mindam='mbonus{1=number:6;2=number:15}' end,
 function(g) g._checker_s12_source=deep(g._checker_s12_source);g._checker_s12_source.maxdam='number' end} do
 local g=place('vor','LAVA_FLOOR4');f(g);eq(T.classify(g),nil,'S12 stamp negative')
end
do local g=place('vor','DEEP_WATER');g._checker_s12_source=nil;eq(T.classify(g),nil,'S12 old-save deep water stays native') end
do local g=place('vor','DEEP_WATER');g._checker_s12_source=deep(g._checker_s12_source);g._checker_s12_source.image='terrain/water_floor.png'
 eq(T.classify(g),nil,'S12 deep water stamp image') end

-- Callbacks: wrapped, moved, removed, added.
do
 local g=place('vor','LAVA_FLOOR4');local f=g.on_stand;g.on_stand=function(...) return f(...) end
 eq(T.classify(g),nil,'S12 wrapped on_stand')
 g=place('vor','LAVA_FLOOR4');g.on_stand=D.spell.LAVA_FLOOR.on_stand;eq(T.classify(g),nil,'S12 foreign on_stand')
 g=place('vor','LAVA_FLOOR4');g.on_stand=nil;eq(T.classify(g),nil,'S12 no on_stand')
 g=place('vor','LAVA_FLOOR4');g.on_move=function() end;eq(T.classify(g),nil,'S12 extra callback')
 g=place('vor','DEEP_WATER');g.on_stand=function() end;eq(T.classify(g),nil,'S12 deep water with a callback')
end

-- Damage values.
for _,d in ipairs{{14,34},{21,34},{17,29},{17,41},{17.5,34},{17,'34'},{nil,34},{17,nil},{{__resolver='mbonus',5,15},34}} do
 local g=place('vor','LAVA_FLOOR4');g.mindam=d[1];g.maxdam=d[2]
 eq(T.classify(g),nil,'S12 damage '..tostring(d[1])..'/'..tostring(d[2]))
end

-- Mutation negatives: every own field changed, removed, and extra fields.
local function other(v)
 local t=type(v)
 if t=='string' then return v..'x' elseif t=='number' then return v+1 elseif t=='boolean' then return not v end
 local c=deep(v);c.extra_field=true;return c
end
local mutated=0
for _,c in ipairs{{'vor','LAVA_FLOOR',true},{'vor','LAVA_FLOOR11',true},{'hp','LAVA_FLOOR2',false},{'dread','LAVA_FLOOR16',true},
 {'vor','DEEP_WATER',false}} do
 local base=place(c[1],c[2]);if c[3] then border(base) end
 if base.on_stand then base.x,base.y=3,4 end
 local z=Z[c[1]]
 setZone(z)
 eq(T.classify(deep(base))~=nil,true,'S12 mutation base accepted '..c[2])
 for k,v in pairs(base) do
  if type(k)=='string' and k:sub(1,1)~='_' and type(v)~='function' then
   local g=deep(base);g[k]=other(v)
   -- x/y are any cell position and mindam/maxdam any resolved value in the
   -- native range: another integer there is the same rule (range: above).
   if k=='x' or k=='y' or k=='mindam' or k=='maxdam' then eq(T.classify(g)~=nil,true,'S12 same-rule value '..k) else
    eq(T.classify(g),nil,'S12 changed '..c[2]..'.'..k);mutated=mutated+1 end
   g=deep(base);g[k]=nil
   eq(T.classify(g),nil,'S12 removed '..c[2]..'.'..k);mutated=mutated+1
  end
 end
 for k,v in pairs{does_block_move=true,block_move=function() return true end,block_sight=true,on_move=function() end,
  faction='orc-pride',dig='FLOOR',can_pass={pass_wall=1},air_level=-10,pass_projectile=true,change_level=1,change_zone='wilderness',
  special_minimap={r=1},z=9,display_x=0.1,tint_r=0.5,textures={},shader_args={},add_mos={{image='terrain/lava/lava_floor_2_01.png'}},
  replace_display={image='x.png'},notice=true,always_remember=true,special=true,embed_particles={{name='x'}},lore='x',
  DamageType='FIRE',mindam=17,nice_tiler={},x=1} do
  if base[k]==nil then
   local g=deep(base);g[k]=v
   eq(T.classify(g),nil,'S12 extra '..c[2]..'.'..k);mutated=mutated+1
  end
 end
end
eq(mutated>150,true,'S12 mutation count '..mutated)

-- Border layer negatives.
setZone('vor-armoury')
for label,f in pairs{
 layer_extra=function(g) g.add_displays[1].z=3 end,layer_image=function(g) g.add_displays[1].image='terrain/lava/lava_floor1.png' end,
 layer_shader=function(g) g.add_displays[1].shader='lava' end,layer_display=function(g) g.add_displays[1].display='#' end,
 layer_colour=function(g) g.add_displays[1].color_r=5 end,layer_force=function(g) g.add_displays[1].force_clone=nil end,
 two_layers=function(g) g.add_displays[2]=deep(g.add_displays[1]) end,keyed=function(g) g.add_displays.x=1 end,
 no_mos=function(g) g.add_displays[1].add_mos=nil end,empty_mos=function(g) g.add_displays[1].add_mos={} end,
 mo_image=function(g) g.add_displays[1].add_mos[1].image='terrain/lava/molten_lava_5_01.png' end,
 mo_foreign=function(g) g.add_displays[1].add_mos[1].image='terrain/padlock2.png' end,
 mo_offset=function(g) g.add_displays[1].add_mos[1].display_y=2 end,mo_zero=function(g) g.add_displays[1].add_mos[1].display_x=0 end,
 mo_extra=function(g) g.add_displays[1].add_mos[1].z=5 end,mo_keyed=function(g) g.add_displays[1].add_mos.x={image='terrain/lava/lava_floor_2_02.png'} end,
 mo_function=function(g) g.add_displays[1].add_mos[1].f=function() end end,
 no_force=function(g) g.force_clone=nil end,force_false=function(g) g.force_clone=false end,
 layer_nested=function(g) g.add_displays[1].add_displays={} end} do
 local g=border(place('vor','LAVA_FLOOR8'));f(g)
 eq(T.classify(g),nil,'S12 border '..label)
end
do local g=place('vor','LAVA_FLOOR8');g.force_clone=true;eq(T.classify(g),nil,'S12 force_clone without the border layer') end
do local g=place('vor','LAVA_FLOOR8');g.x=2;eq(T.classify(g),nil,'S12 x without y') end
do local g=place('vor','LAVA_FLOOR8');g.x,g.y=2.5,1;eq(T.classify(g),nil,'S12 fractional position') end
do local g=place('vor','LAVA_FLOOR8');g.x,g.y=-1,1;eq(T.classify(g),nil,'S12 negative position') end
do local g=place('vor','LAVA_FLOOR8');g[1]=true;eq(T.classify(g),nil,'S12 numeric key') end

-- Stone adapter: mask, variants, parity, native snapshot and asset gate.
local function mockMap(w,h,fill)
 local m={w=w,h=h,map={},seen={},rem={}}
 for x=0,w-1 do for y=0,h-1 do m.map[x+y*w]={[1]=fill(x,y)} end end
 m.seens=function(x,y) return m.seen[x+y*w] and true or false end
 m.infovs=m.seens
 m.remembers=setmetatable({},{__call=function(_,x,y) return m.rem[x+y*w] and true or false end})
 return setmetatable(m,{__call=function(self,x,y,layer) if x<0 or y<0 or x>=w or y>=h then return end;return self.map[x+y*w][layer or 1] end})
end
local plan={'#####','#LL.#','#.L~#','#.~~#','#####'}
local sym={['#']='HARDWALL',L='LAVA_FLOOR5',['.']='FLOOR',['~']='DEEP_WATER'}
local function scene()
 setZone('vor-armoury')
 local m=mockMap(5,5,function(x,y) local g=place('vor',sym[plan[y+1]:sub(x+1,x+1)]);if g.define_as=='LAVA_FLOOR5' then border(g) end;return g end)
 _G.game.level={map=m}
 for x=0,4 do for y=0,4 do m.seen[x+y*5]=true;m.rem[x+y*5]=true end end
 for x=0,4 do for y=0,4 do T.observe(m,x,y,m(x,y,1)) end end
 return m
end
-- Assets not installed: the records exist but nothing is painted (native).
local m=scene()
eq(T.hazardAssets.ready,false,'hazard assets absent in the mock')
eq(T.render(m,1,1,m(1,1,1),'refined'),nil,'S12 without its asset set the cell stays native')
T.hazardAssets.ready=true;setmetatable(T.hazardAssets.files,{__index=function(_,k) return k:match('^checker%-revised%+refined/hazard/') and true or nil end})
m=scene()
local function file(x,y) local d=T.render(m,x,y,m(x,y,1),'refined');return d and d.image end
local function vari(x,y) return ({'a','b','c'})[((x*17+y*7)%3)+1] end
-- (1,1): E lava (2) -> mask 2; (2,1): W lava (8) + S lava (4) -> 12; (2,2): N lava (1) -> 1.
eq(file(1,1),'checker-revised+refined/hazard/lava-'..vari(1,1)..'-2-0.png','S12 lava mask E')
eq(file(2,1),'checker-revised+refined/hazard/lava-'..vari(2,1)..'-12-1.png','S12 lava mask W+S')
eq(file(2,2),'checker-revised+refined/hazard/lava-'..vari(2,2)..'-1-0.png','S12 lava mask N')
-- (3,2): S water (4) -> 4; (2,3): E water (2) -> 2; (3,3): N (1) + W (8) -> 9.
eq(file(3,2),'checker-revised+refined/hazard/deep-4-1.png','S12 water mask S')
eq(file(2,3),'checker-revised+refined/hazard/deep-2-1.png','S12 water mask E')
eq(file(3,3),'checker-revised+refined/hazard/deep-9-0.png','S12 water mask N+W')
eq(file(1,2):match('korpul/floor%-[ab]%-0%-1')~=nil,true,'floor unchanged')
eq(file(0,0):match('korpul/hardwall%-')~=nil,true,'hard wall unchanged')
eq(T.mask(m,1,2),8,'lava/water never count as wall neighbours (W wall only)')
-- A hidden neighbour (no record) is not water: the kerb stays (no knowledge).
do
 setZone('vor-armoury')
 local hm=mockMap(2,1,function(x) return place('vor','DEEP_WATER') end)
 _G.game.level={map=hm}
 hm.seen[0]=true;hm.rem[0]=true
 T.observe(hm,0,0,hm(0,0,1));T.observe(hm,1,0,hm(1,0,1))
 eq(T.render(hm,0,0,hm(0,0,1),'refined').image,'checker-revised+refined/hazard/deep-0-0.png','S12 unseen water neighbour keeps the kerb')
 eq(hm._checker_korpul[1],nil,'S12 unseen cell not recorded')
 eq(T.render(hm,1,0,hm(1,0,1),'refined').image,'invis.png','S12 unknown cell draws nothing (existing rule)')
end
-- Native mode after painting: the snapshot keeps the native look and shader.
m=scene();file(1,1);file(3,3)
local nd=T.render(m,1,1,m(1,1,1),'vanilla')
eq(nd.image,'terrain/lava/lava_floor5.png','S12 native snapshot image');eq(nd.shader,'lava','S12 native snapshot keeps the lava shader')
eq(nd.add_displays[1].image,'invis.png','S12 native snapshot keeps the border layer')
eq(T.render(m,3,3,m(3,3,1),'vanilla').shader,'water','S12 native snapshot keeps the water shader')
eq(m._checker_korpul[1+1*5].native.shader,'lava','record snapshot shader')
eq(m._checker_korpul[1+2*5].native.shader,nil,'floor snapshot has no shader field')
-- Rules untouched by drawing.
local before={}
for k,v in pairs(m(1,1,1)) do if type(k)=='string' and k:sub(1,1)~='_' then before[k]=v end end
file(1,1);T.render(m,1,1,m(1,1,1),'vanilla')
for k,v in pairs(before) do eq(m(1,1,1)[k],v,'S12 rule field untouched '..k) end
eq(m(1,1,1).replace_display,nil,'S12 stone adapter installs no replace_display')
-- An observed native on_stand (x/y) does not change the record signature.
do
 local g=m(1,1,1);local sig=m._checker_korpul[1+1*5].signature
 g:on_stand(1,1,{player=false})
 eq(T.observe(m,1,1,g),false,'S12 on_stand position write needs no re-observe')
 eq(m._checker_korpul[1+1*5].signature,sig,'S12 signature unchanged')
end
-- The Grid.lua superload list stamps both defining files.
local grid=readFile(root..'superload/mod/class/Grid.lua')
eq(grid:find("file=='/data/general/grids/lava.lua'",1,true)~=nil,true,'Grid.lua stamps lava.lua')
eq(grid:find("file=='/data/general/grids/water.lua'",1,true)~=nil,true,'Grid.lua stamps water.lua')
-- The runtime manifest: exactly the 128 exported files, all present.
local man=loadfile(root..'data/terrain-hazard-manifest.lua')()
local c=0
for f,ok in pairs(man.files) do
 c=c+1;eq(ok,true,'manifest entry '..f)
 local rel=f:match('^checker%-revised%+(refined/hazard/[%w%-]+%-%d+%-[01]%.png)$')
 eq(rel~=nil,true,'manifest path '..f)
 eq(io.open(root..'data/gfx/'..rel,'rb')~=nil,true,'manifest file exists '..f)
end
eq(c,128,'manifest count');eq(man.ready,true,'manifest ready')
print('terrain_s12: '..n..' checks passed (native definitions and callbacks + mocked map/renderer; no live-game claim)')
