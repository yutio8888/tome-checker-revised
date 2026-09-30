-- S15 (mode / tutorial and class planes): tutorial L1 on the forest
-- contracts and dreams L1 on the jungle contract, each gated by its zone list
-- stamp. Run from any cwd with Lua 5.1/LuaJIT. The native zone lists are
-- built the way Entity:loadList/Entity:init build them and stamped per
-- finished file (the superload/mod/class/Grid.lua order), as in
-- tests/terrain_s13.lua. Checks: stamps, exact kinds, zone scope, old-save
-- (unstamped) cells, every native-staying id of both lists, field mutations,
-- and a mocked level through T.apply for Refined -> Native -> Refined with
-- the rule fields untouched.
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
local TUT,DRM='/data/zones/tutorial/grids.lua','/data/zones/dreams/grids.lua'
local D={tut=loadDefs(TUT),drm=loadDefs(DRM),forest=loadDefs('/data/general/grids/forest.lua'),
 jungle=loadDefs('/data/general/grids/jungle.lua'),tannen=loadDefs('/data/zones/tannen-tower/grids.lua'),
 caldera=loadDefs('/data/zones/noxious-caldera/grids.lua')}
local function setZone(z) _G.game={zone={short_name=z}} end
local function place(set,id) return deep(assert(D[set][id],set..' '..id)) end
local function kind(g,z) setZone(z);return T.batch4Kind(g,z) end
local function ser(v)
 if type(v)~='table' then return type(v)..':'..tostring(v) end
 local keys={};for k in pairs(v) do if type(k)~='string' or k:sub(1,1)~='_' then keys[#keys+1]=k end end
 table.sort(keys,function(a,b) return tostring(a)<tostring(b) end)
 local out={};for _,k in ipairs(keys) do out[#out+1]=tostring(k)..'='..ser(v[k]) end
 return '{'..table.concat(out,';')..'}'
end

-- Gating: forest-side S5 families, no stone variant, not combined.
for _,z in ipairs{'tutorial','dreams'} do
 eq(T.variant({short_name=z}),nil,'S15 no stone variant '..z)
 eq(T.combined[z],nil,'S15 not combined '..z)
end
-- Out of scope: stay without any S15 gate.
for _,z in ipairs{'tutorial-combat-stats','arena','infinite-dungeon','demon-plane-spell','dreamscape-talent',
 'temporal-reprieve-talent','eidolon-plane','stellar-system-shandral'} do
 eq(T.variant({short_name=z}),nil,'S15 ungated stone '..z)
 eq(T.s15Kind(place('tut','GRASS'),z),nil,'S15 ungated kind '..z)
end

-- Stamps: each list stamps its own and nested definitions; general stamps stay.
eq(D.tut.GRASS._checker_zone_source.file,TUT,'tutorial list stamps GRASS')
eq(D.tut.TREE5._checker_zone_source.id,'TREE5','tutorial list stamps a tree variant')
eq(D.tut.DEEP_WATER._checker_zone_source.file,TUT,'tutorial list stamps DEEP_WATER')
eq(D.tut.GRASS._checker_forest_source.file,'/data/general/grids/forest.lua','tutorial GRASS keeps its forest stamp')
eq(D.tut.DEEP_WATER._checker_water_source.file,'/data/general/grids/water.lua','tutorial DEEP_WATER keeps its water stamp')
eq(D.drm.JUNGLE_GRASS._checker_zone_source.file,DRM,'dreams list stamps JUNGLE_GRASS')
eq(D.drm.JUNGLE_TREE7._checker_zone_source.id,'JUNGLE_TREE7','dreams list stamps a jungle tree variant')
eq(D.drm.JUNGLE_GRASS._checker_jungle_source.file,'/data/general/grids/jungle.lua','dreams JUNGLE_GRASS keeps its jungle stamp')
eq(D.forest.GRASS._checker_zone_source,nil,'plain forest.lua list has no zone stamp')
eq(D.jungle.JUNGLE_GRASS._checker_zone_source,nil,'plain jungle.lua list has no zone stamp')

-- Exact kinds.
eq(kind(place('tut','GRASS'),'tutorial'),'grass','tutorial GRASS')
for i=1,14 do local id='GRASS_PATCH'..i;if D.tut[id] then eq(kind(place('tut',id),'tutorial'),'grass','tutorial '..id) end end
local trees=0
for id,g in pairs(D.tut) do
 if id:match('^TREE%d+$') then eq(kind(deep(g),'tutorial'),'tree','tutorial '..id);trees=trees+1 end
end
eq(trees>0,true,'tutorial tree variants present')
eq(kind(place('tut','DEEP_WATER'),'tutorial'),'deep','tutorial DEEP_WATER')
eq(kind(place('drm','JUNGLE_GRASS'),'dreams'),'jungle-grass','dreams JUNGLE_GRASS')
local jt=0
for id,g in pairs(D.drm) do
 if id:match('^JUNGLE_TREE%d+$') then eq(kind(deep(g),'dreams'),'jungle-tree','dreams '..id);jt=jt+1 end
 if id:match('^JUNGLE_GRASS_PATCH%d+$') then eq(kind(deep(g),'dreams'),'jungle-grass','dreams '..id) end
end
eq(jt>0,true,'dreams jungle tree variants present')

-- Zone scope: the same stamped cells elsewhere, other lists' cells here.
for _,z in ipairs{'trollmire','noxious-caldera','town-irkkk','tannen-tower','dreams'} do
 eq(T.s15Kind(place('tut','GRASS'),z),nil,'S15 tutorial GRASS outside tutorial: '..z)
end
for _,z in ipairs{'noxious-caldera','town-irkkk','tutorial'} do
 eq(T.s15Kind(place('drm','JUNGLE_GRASS'),z),nil,'S15 dreams JUNGLE_GRASS outside dreams: '..z)
end
eq(kind(place('tannen','GRASS'),'tutorial'),nil,'Tannen-stamped GRASS in the tutorial stays native')
eq(kind(place('caldera','JUNGLE_GRASS'),'dreams'),nil,'Caldera-stamped JUNGLE_GRASS in dreams stays native')
eq(kind(place('forest','GRASS'),'tutorial'),nil,'unstamped (old save) GRASS stays native')
eq(kind(place('jungle','JUNGLE_TREE3'),'dreams'),nil,'unstamped (old save) jungle tree stays native')
for label,f in pairs{none=function(g) g._checker_zone_source=nil end,
 file=function(g) g._checker_zone_source={file=DRM,id=g.define_as} end,
 id=function(g) g._checker_zone_source={file=TUT,id='TREE1'} end} do
 local g=place('tut','GRASS');f(g);eq(kind(g,'tutorial'),nil,'S15 tutorial stamp '..label)
end

-- Native-staying cells.
for _,id in ipairs{'DREAM_END','DREAM2_END','DREAM_MOUSE_HOLE','DREAM_STONE','BAMBOO_HUT_FLOOR','BAMBOO_HUT_WALL',
 'BHW_V_FULL1','BHW_H_FULL3','BAMBOO_HUT_DOOR','BAMBOO_HUT_DOOR_HORIZ','BAMBOO_HUT_DOOR_OPEN','BAMBOO_HUT_DOOR_OPEN_VERT',
 'FLOOR','WALL','UP','DOWN','DEEP_WATER','GRASS','TREE','JUNGLE_GRASS_UP_WILDERNESS','JUNGLE_GRASS_DOWN'} do
 if D.drm[id] then eq(kind(place('drm',id),'dreams'),nil,'dreams '..id..' stays native') end
end
for _,id in ipairs{'FLOOR','WALL','UP','DOWN','DOOR','DOOR_OPEN','GRASS_UP_WILDERNESS','GRASS_DOWN6','SHALLOW_WATER','POISON_DEEP_WATER'} do
 if D.tut[id] then eq(kind(place('tut',id),'tutorial'),nil,'tutorial '..id..' stays native') end
end
-- A dreams mouse hole placed as the level post_process places it (clone plus a road layer).
do local g=place('drm','DREAM_MOUSE_HOLE');g.add_displays[#g.add_displays+1]={image='terrain/road_going_left_01.png',z=5}
 g.mouse_hole={x=1,y=1};eq(kind(g,'dreams'),nil,'placed mouse hole stays native') end

-- Mutations: rule and callback changes fall back to native.
for _,c in ipairs{
 {'tut','GRASS','tutorial',function(g) g.does_block_move=true end},{'tut','GRASS','tutorial',function(g) g.on_stand=function() end end},
 {'tut','GRASS','tutorial',function(g) g.change_level=2 end},{'tut','GRASS','tutorial',function(g) g.image='terrain/grass2.png' end},
 {'tut','TREE5','tutorial',function(g) g.block_sight=nil end},{'tut','TREE5','tutorial',function(g) g.dig=nil end},
 {'tut','TREE5','tutorial',function(g) g.can_pass={pass_tree=1,pass_wall=1} end},
 {'tut','DEEP_WATER','tutorial',function(g) g.air_level=-1 end},{'tut','DEEP_WATER','tutorial',function(g) g.on_stand=function() end end},
 {'drm','JUNGLE_GRASS','dreams',function(g) g.does_block_move=true end},{'drm','JUNGLE_GRASS','dreams',function(g) g.on_move=function() end end},
 {'drm','JUNGLE_GRASS','dreams',function(g) g.change_level=2 end},{'drm','JUNGLE_GRASS','dreams',function(g) g.shader='x' end},
 {'drm','JUNGLE_TREE3','dreams',function(g) g.block_sight=nil end},{'drm','JUNGLE_TREE3','dreams',function(g) g.dig=nil end},
 {'drm','JUNGLE_TREE3','dreams',function(g) g.block_move=function() return false end end},
 {'drm','JUNGLE_TREE3','dreams',function(g) g.can_pass={pass_tree=1,pass_wall=1} end}} do
 local g=place(c[1],c[2]);c[4](g);eq(kind(g,c[3]),nil,'S15 altered '..c[3]..' '..c[2]..' stays native')
end

-- Mocked levels through T.apply: board display, rules untouched, toggle restores.
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
local function level(zone,set,plan,sym)
 local m=mockMap(#plan[1],#plan,function(x,y) return place(set,sym[plan[y+1]:sub(x+1,x+1)]) end)
 return {zone={short_name=zone,max_level=1},level={map=m,data={},level=1}},m
end
local function rulesOf(m)
 local out={}
 for x=0,m.w-1 do for y=0,m.h-1 do
  local g=m(x,y,1);local r={}
  for k,v in pairs(g) do if type(k)=='string' and k:sub(1,1)~='_' and k~='replace_display' then r[k]=ser(v) end end
  out[x..','..y]=r
 end end
 return out
end
local function rulesSame(m,before,label)
 local now=rulesOf(m)
 for key,r in pairs(before) do
  for k,v in pairs(r) do eq(now[key][k],v,label..' rule '..key..' '..k) end
  for k in pairs(now[key]) do eq(r[k]~=nil,true,label..' no new field '..key..' '..k) end
 end
end
local function imgs(m)
 local out={}
 for x=0,m.w-1 do for y=0,m.h-1 do local g=m(x,y,1);out[x..','..y]=g.replace_display and g.replace_display.image or false end end
 return out
end
for _,case in ipairs{
 {'tutorial','tut',{'TTT','T,,','T,~'},{T='TREE5',[',']='GRASS',['~']='DEEP_WATER'},
  {['1,1']='checker-revised+refined/grass0.png',['0,0']='tree',['2,2']='deep'},{}},
 {'dreams','drm',{'TTT','T,E','T,H'},{T='JUNGLE_TREE3',[',']='JUNGLE_GRASS',E='DREAM_END',H='DREAM_MOUSE_HOLE'},
  {['1,1']='checker-revised+refined/caldera/floor0.png',['0,0']='checker-revised+refined/caldera/tree-'},{'2,1','2,2'}}} do
 local host,m=level(case[1],case[2],case[3],case[4])
 _G.game={zone=host.zone,level=host.level,log=function() end}
 local before=rulesOf(m)
 mode='refined';T.apply(host)
 local on=imgs(m)
 for key,want in pairs(case[5]) do
  local got=on[key]
  eq(type(got)=='string' and (got==want or got:find(want,1,true)~=nil),true,'S15 '..case[1]..' board '..key..' '..tostring(got))
 end
 for _,key in ipairs(case[6]) do eq(on[key],false,'S15 '..case[1]..' native cell '..key) end
 rulesSame(m,before,'S15 '..case[1]..' refined')
 mode='vanilla';T.apply(host)
 for key,v in pairs(imgs(m)) do eq(v,false,'S15 '..case[1]..' native mode '..key) end
 for x=0,m.w-1 do for y=0,m.h-1 do eq(m(x,y,1)._checker_terrain,nil,'S15 '..case[1]..' native state cleared') end end
 rulesSame(m,before,'S15 '..case[1]..' native')
 mode='refined';T.apply(host)
 for key,v in pairs(imgs(m)) do eq(v,on[key],'S15 '..case[1]..' restored '..key) end
 rulesSame(m,before,'S15 '..case[1]..' restored')
 mode='blockout';T.apply(host)
 eq(m(0,0,1).replace_display.image,'checker-revised+tree0.png','S15 '..case[1]..' blockout wall reads as tree')
 mode='refined';T.apply(host)
end
-- Old-save level: unstamped cells stay native on apply.
do
 local host,m=level('tutorial','forest',{',T'},{[',']='GRASS',T='TREE5'})
 _G.game={zone=host.zone,level=host.level,log=function() end}
 mode='refined';T.apply(host)
 eq(m(0,0,1).replace_display,nil,'S15 old-save tutorial grass stays native')
 eq(m(1,0,1).replace_display,nil,'S15 old-save tutorial tree stays native')
end
print('terrain_s15: '..n..' checks passed (native definitions + mocked map/renderer; no live-game claim)')
