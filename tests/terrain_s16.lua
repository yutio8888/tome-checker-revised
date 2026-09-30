-- S16 (talent planes): the Fearscape spell plane (demon-plane-spell) on the
-- Fearscape lava-wall contract plus the S12 hazard lava with the injected
-- on_stand closure (demon-plane-spell/grids.lua:23), Temporal Reprieve on the
-- Point Zero space/rocks and forest grass/hard-tree contracts, each gated by
-- its zone-list stamp; and the direct level-swap hook (Game:tick superload +
-- CheckerTerrain.directSwap) that fires only for those two planes. Run from
-- any cwd with Lua 5.1/LuaJIT. Definitions are built the way Entity:loadList
-- builds them (loader callback per new entity, base copies after it, stamps
-- per finished file in the superload/mod/class/Grid.lua order), as in
-- tests/terrain_s15.lua.
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
T.hazardAssets.ready=true;setmetatable(T.hazardAssets.files,{__index=function() return true end})
T.scorchDarkAssets.ready=true;setmetatable(T.scorchDarkAssets.files,{__index=function() return true end})

local cenv=setmetatable({},{__index=_G})
loadWith(root..'../../engines/default/engine/colors.lua',cenv)
local colors=cenv.colors

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
-- demon-plane-spell/grids.lua:22 reads game.level.plane_owner while loading.
_G.game={level={}}
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
local DPS,TR='/data/zones/demon-plane-spell/grids.lua','/data/zones/temporal-reprieve-talent/grids.lua'
local D={dps=loadDefs(DPS),tr=loadDefs(TR),lava=loadDefs('/data/general/grids/lava.lua'),
 dp=loadDefs('/data/zones/demon-plane/grids.lua'),void=loadDefs('/data/general/grids/void.lua'),
 forest=loadDefs('/data/general/grids/forest.lua'),pz=loadDefs('/data/zones/town-point-zero/grids.lua')}
local function setZone(z) _G.game={zone={short_name=z},level={}} end
-- A placed grid: resolved lava damage (lava.lua:30-31 mbonus 5/15, 10/30).
local function place(set,id)
 local g=deep(assert(D[set][id],set..' '..id))
 if type(g.mindam)=='table' then g.mindam=17 end
 if type(g.maxdam)=='table' then g.maxdam=33 end
 return g
end
local function kind(g,z) setZone(z);return T.s16Kind(g,z) end

-- Stamps and the injected closure.
eq(D.dps.LAVA_FLOOR._checker_zone_source.file,DPS,'spell list stamps LAVA_FLOOR')
eq(D.dps.LAVA_FLOOR7._checker_zone_source.id,'LAVA_FLOOR7','spell list stamps a lava floor variant')
eq(D.dps.LAVA_WALL3._checker_zone_source.file,DPS,'spell list stamps a lava wall variant')
eq(D.dps.LAVA_WALL._checker_burnt_source.file,'/data/general/grids/lava.lua','spell LAVA_WALL keeps its lava stamp')
eq(D.dps.LAVA_FLOOR._checker_s12_source.funcs,T.S16_STAND or 'on_stand@@'..DPS..':23','S12 stamp records the injected closure')
eq(D.dps.LAVA_FLOOR12._checker_s12_source.funcs,'on_stand@@'..DPS..':23','base copies carry the injected closure')
eq(D.tr.FLOATING_ROCKS._checker_zone_source.file,TR,'reprieve list stamps FLOATING_ROCKS')
eq(D.tr.OUTERSPACE._checker_void_source.file,'/data/general/grids/void.lua','reprieve OUTERSPACE keeps its void stamp')
eq(D.tr.HARDTREE._checker_forest_source.file,'/data/general/grids/forest.lua','reprieve HARDTREE keeps its forest stamp')
eq(D.lava.LAVA_FLOOR._checker_zone_source,nil,'plain lava.lua list has no zone stamp')
eq(D.void.OUTERSPACE._checker_zone_source,nil,'plain void.lua list has no zone stamp')

-- Exact kinds.
eq(kind(place('dps','LAVA_FLOOR'),'demon-plane-spell'),'lava-hazard','spell LAVA_FLOOR')
for i=1,16 do eq(kind(place('dps','LAVA_FLOOR'..i),'demon-plane-spell'),'lava-hazard','spell LAVA_FLOOR'..i) end
eq(kind(place('dps','LAVA_WALL'),'demon-plane-spell'),'lava-wall','spell LAVA_WALL')
for i=1,6 do eq(kind(place('dps','LAVA_WALL'..i),'demon-plane-spell'),'lava-wall','spell LAVA_WALL'..i) end
eq(kind(place('tr','OUTERSPACE'),'temporal-reprieve-talent'),'void-space','reprieve OUTERSPACE')
eq(kind(place('tr','FLOATING_ROCKS'),'temporal-reprieve-talent'),'void-rocks','reprieve FLOATING_ROCKS')
local rocks=0
for id in pairs(D.tr) do
 if id:match('^FLOATING_ROCKS_[12346789]1$') or id:match('^FLOATING_ROCKS_[1379]I$') or id=='FLOATING_ROCKS_5' then
  eq(kind(place('tr',id),'temporal-reprieve-talent'),'void-rocks','reprieve '..id);rocks=rocks+1
 end
end
eq(rocks>=8,true,'reprieve rock edge variants present')
eq(kind(place('tr','GRASS'),'temporal-reprieve-talent'),'grass','reprieve GRASS')
eq(kind(place('tr','HARDTREE'),'temporal-reprieve-talent'),'hardtree','reprieve HARDTREE')
for i=1,20 do local id='HARDTREE'..i;if D.tr[id] then eq(kind(place('tr',id),'temporal-reprieve-talent'),'hardtree','reprieve '..id) end end

-- Zone scope and old saves.
for _,z in ipairs{'demon-plane','charred-scar','vor-armoury','temporal-reprieve-talent','dreamscape-talent','eidolon-plane'} do
 eq(T.s16Kind(place('dps','LAVA_FLOOR'),z) or nil,nil,'spell lava floor outside the spell plane: '..z)
end
setZone('demon-plane');eq(T.batch5Kind(place('dps','LAVA_FLOOR'),'scorch'),nil,'spell lava floor on the story Fearscape family stays native')
setZone('vor-armoury');eq(T.s12Kind(place('dps','LAVA_FLOOR'),'vor-armoury'),nil,'spell lava floor on the S12 contract stays native')
for _,z in ipairs{'town-point-zero','abashed-expanse','demon-plane-spell','dreamscape-talent','eidolon-plane'} do
 eq(T.s16Kind(place('tr','FLOATING_ROCKS'),z) or nil,nil,'reprieve rocks outside the reprieve: '..z)
end
eq(kind(place('dp','LAVA_FLOOR'),'demon-plane-spell'),nil,'story Fearscape (stripped) lava floor in the spell plane stays native')
eq(kind(place('lava','LAVA_FLOOR'),'demon-plane-spell'),nil,'unstamped (old save) native lava.lua floor stays native')
eq(kind(place('lava','LAVA_WALL'),'demon-plane-spell'),nil,'unstamped (old save) lava wall stays native')
eq(kind(place('void','OUTERSPACE'),'temporal-reprieve-talent'),nil,'unstamped (old save) space stays native')
eq(kind(place('forest','GRASS'),'temporal-reprieve-talent'),nil,'unstamped (old save) grass stays native')
eq(kind(place('pz','FLOATING_ROCKS'),'temporal-reprieve-talent'),nil,'Point Zero-stamped rocks in the reprieve stay native')
-- Native-staying ids of both lists (void floor/rifts, basic stone, molten lava, ladders).
for _,id in ipairs{'VOID','SPACETIME_RIFT','FLOOR','WALL','UP','DOWN','TREE','TREE5','DEEP_WATER','GRASS_UP_WILDERNESS'} do
 if D.tr[id] then eq(kind(place('tr',id),'temporal-reprieve-talent'),nil,'reprieve '..id..' stays native') end
end
for _,id in ipairs{'LAVA','LAVA3','FLOOR','WALL','UP','DOWN','LAVA_LADDER_DOWN','LAVA_LADDER_UP','LAVA_BOULDER'} do
 if D.dps[id] then eq(kind(place('dps',id),'demon-plane-spell'),nil,'spell plane '..id..' stays native') end
end

-- Mutations: rules, callbacks and extra fields fall back to native.
local other=function() end
for label,f in pairs{
 wrapped=function(g) local s=g.on_stand;g.on_stand=function(...) return s(...) end end,
 native=function(g) g.on_stand=D.lava.LAVA_FLOOR.on_stand end,
 stripped=function(g) g.on_stand=nil end,
 faction=function(g) g.faction={name='owner'} end,
 extraFn=function(g) g.on_move=other end,
 blocks=function(g) g.does_block_move=true end,
 sight=function(g) g.block_sight=true end,
 image=function(g) g.image='terrain/lava/lava_floor99.png' end,
 change=function(g) g.change_level=1 end,
 dam=function(g) g.mindam=99 end,
 unresolved=function(g) g.mindam=nil end,
 air=function(g) g.air_level=-5 end,
 dtype=function(g) g.DamageType='COLD' end,
 zone=function(g) g._checker_zone_source={file=TR,id=g.define_as} end,
 stamp=function(g) g._checker_s12_source=deep(g._checker_s12_source);g._checker_s12_source.funcs='on_stand@@'..DPS..':24' end,
 foreignDisplay=function(g) g.replace_display={image='x'} end} do
 local g=place('dps','LAVA_FLOOR3');f(g);eq(kind(g,'demon-plane-spell'),nil,'S16 altered spell floor ('..label..') stays native')
end
for label,f in pairs{blocks=function(g) g.does_block_move=nil end,sight=function(g) g.block_sight=nil end,
 dig=function(g) g.dig='FLOOR' end,pass=function(g) g.can_pass={pass_wall=1} end,stand=function(g) g.on_stand=other end} do
 local g=place('dps','LAVA_WALL2');f(g);eq(kind(g,'demon-plane-spell'),nil,'S16 altered spell wall ('..label..') stays native')
end
for _,c in ipairs{
 {'OUTERSPACE',function(g) g.does_block_move=nil end},{'OUTERSPACE',function(g) g.on_stand=other end},
 {'FLOATING_ROCKS',function(g) g.does_block_move=true end},{'FLOATING_ROCKS',function(g) g.change_level=1 end},
 {'GRASS',function(g) g.block_sight=true end},{'GRASS',function(g) g.on_stand=other end},
 {'HARDTREE',function(g) g.block_sight=nil end},{'HARDTREE',function(g) g.can_pass={pass_tree=1} end},
 {'HARDTREE',function(g) g.dig='GRASS' end}} do
 local g=place('tr',c[1]);c[2](g);eq(kind(g,'temporal-reprieve-talent'),nil,'S16 altered reprieve '..c[1]..' stays native')
end

-- Mocked plane levels through T.apply: board display, rules untouched, toggle restores.
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
local function ser(v)
 if type(v)~='table' then return type(v)..':'..tostring(v) end
 local keys={};for k in pairs(v) do if type(k)~='string' or k:sub(1,1)~='_' then keys[#keys+1]=k end end
 table.sort(keys,function(a,b) return tostring(a)<tostring(b) end)
 local out={};for _,k in ipairs(keys) do out[#out+1]=tostring(k)..'='..ser(v[k]) end
 return '{'..table.concat(out,';')..'}'
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
local function level(zone,set,plan,sym)
 local m=mockMap(#plan[1],#plan,function(x,y) return place(set,sym[plan[y+1]:sub(x+1,x+1)]) end)
 return {zone={short_name=zone,max_level=1},level={map=m,data={},level=1}},m
end
local R='checker-revised+'
for _,case in ipairs{
 {'demon-plane-spell','dps',{'WWWW','W,,,','W,,L','WW,,'},{W='LAVA_WALL3',[',']='LAVA_FLOOR5',L='LAVA'},
  -- (2,2) has hazard neighbours N, S and W (mask 1+4+8=13); E is molten lava.
  {['2,2']=R..'refined/hazard/lava-',['0,0']=R..'refined/scorch-dark/wall-',['1,1']='-',['2,2|mask']='-13-0'},{'3,2'}},
 {'temporal-reprieve-talent','tr',{'vvvv','v..v','.GX.','vvvv'},{v='OUTERSPACE',['.']='FLOATING_ROCKS',G='GRASS',X='HARDTREE'},
  {['0,0']=R..'refined/void/space0',['1,1']=R..'refined/void/rocks-',['1,2']=R..'refined/grass1',['2,2']=R..'refined/tree-hard0'},{}}} do
 local host,m=level(case[1],case[2],case[3],case[4])
 _G.game={zone=host.zone,level=host.level,log=function() end}
 local before=rulesOf(m)
 mode='refined';T.apply(host)
 local on=imgs(m)
 for key,want in pairs(case[5]) do
  local cell=key:match('^([^|]+)')
  local got=on[cell]
  eq(type(got)=='string' and got:find(want,1,true)~=nil,true,'S16 '..case[1]..' board '..key..' '..tostring(got))
 end
 for _,key in ipairs(case[6]) do eq(on[key],false,'S16 '..case[1]..' native cell '..key) end
 rulesSame(m,before,'S16 '..case[1]..' refined')
 -- A second pass (the hook re-applies on return) keeps every board cell.
 T.apply(host)
 for key,v in pairs(imgs(m)) do eq(v,on[key],'S16 '..case[1]..' idempotent '..key) end
 mode='vanilla';T.apply(host)
 for key,v in pairs(imgs(m)) do eq(v,false,'S16 '..case[1]..' native mode '..key) end
 for x=0,m.w-1 do for y=0,m.h-1 do eq(m(x,y,1)._checker_terrain,nil,'S16 '..case[1]..' native state cleared') end end
 rulesSame(m,before,'S16 '..case[1]..' native')
 mode='refined';T.apply(host)
 for key,v in pairs(imgs(m)) do eq(v,on[key],'S16 '..case[1]..' restored '..key) end
 rulesSame(m,before,'S16 '..case[1]..' restored')
 mode='blockout';T.apply(host)
 eq(m(0,0,1).replace_display.image,R..'tree0.png','S16 '..case[1]..' blockout blocker reads as tree')
 mode='refined';T.apply(host)
end
-- The injected closure itself is untouched by the board install.
do
 local host,m=level('demon-plane-spell','dps',{',,'},{[',']='LAVA_FLOOR'})
 _G.game={zone=host.zone,level=host.level,log=function() end}
 local f=m(0,0,1).on_stand
 T.apply(host)
 eq(m(0,0,1).on_stand,f,'S16 on_stand closure kept')
 eq(m(0,0,1).replace_display~=nil,true,'S16 spell floor drawn')
end
-- Old-save plane levels: unstamped cells stay native on apply.
do
 local host,m=level('demon-plane-spell','lava',{'W,'},{W='LAVA_WALL',[',']='LAVA_FLOOR'})
 _G.game={zone=host.zone,level=host.level,log=function() end}
 mode='refined';T.apply(host)
 eq(m(0,0,1).replace_display,nil,'S16 old-save spell wall stays native')
 local host2,m2=level('temporal-reprieve-talent','void',{'vv'},{v='OUTERSPACE'})
 _G.game={zone=host2.zone,level=host2.level,log=function() end}
 T.apply(host2)
 eq(m2(0,0,1).replace_display,nil,'S16 old-save reprieve space stays native')
end
-- Dreamscape and the eidolon plane: no S16 kind for any definition.
for _,z in ipairs{'dreamscape-talent','eidolon-plane'} do
 for _,set in ipairs{'dps','tr','void'} do for id in pairs(D[set]) do
  eq(T.s16Kind(place(set,id),z) or nil,nil,'S16 no kind in '..z..' for '..set..' '..id)
 end end
end

-- directSwap: only swaps into or out of the two listed planes.
local Z=function(s) return {short_name=s} end
local src,dps,tr=Z('trollmire'),Z('demon-plane-spell'),Z('temporal-reprieve-talent')
eq(T.directSwap(src,dps),true,'swap into the spell plane')
eq(T.directSwap(dps,src),true,'swap back from the spell plane')
eq(T.directSwap(src,tr),true,'swap into the reprieve')
eq(T.directSwap(tr,src),true,'swap back from the reprieve')
eq(T.directSwap(dps,dps),false,'same plane zone')
-- (S17 added dreamscape-talent to the plane list; tests/terrain_s17.lua covers it.)
for _,s in ipairs{'eidolon-plane','demon-plane','dreams','stellar-system-shandral','town-derth'} do
 eq(T.directSwap(src,Z(s)),false,'no hook into '..s)
 eq(T.directSwap(Z(s),src),false,'no hook out of '..s)
end
eq(T.directSwap(nil,dps),true,'swap into the plane with no previous zone')
eq(T.directSwap(src,nil),false,'no zone after')

-- The Game:tick superload: fires once after a tick that swapped into/out of a
-- listed plane, never for a normal changeLevel or the other planes.
do
 local stub={}
 local calls=0
 function stub:tick() if self.next then self.zone,self.level=self.next[1],self.next[2];self.next=nil end;return 'r' end
 function stub:onTurn() end
 local genv=setmetatable({loadPrevious=function() return stub end,
  require=function(name) return modules[name] or {} end},{__index=_G})
 local G=loadWith(root..'superload/mod/class/Game.lua',genv)
 local host=setmetatable({zone=src,level={}},{__index=G})
 host.checkerApplySettings=function() calls=calls+1 end
 eq(host:tick(),'r','tick result passed through')
 eq(calls,0,'no swap, no apply')
 local srcLevel=host.level
 for _,c in ipairs{{dps,{},1},{src,srcLevel,2},{tr,{},3},{src,srcLevel,4},{Z('dreamscape-talent'),{},5},{src,srcLevel,6},
  {Z('eidolon-plane'),{},6},{src,srcLevel,6},{Z('town-derth'),{},6}} do
  host.next={c[1],c[2]};host:tick()
  eq(calls,c[3],'tick hook count after swap to '..c[1].short_name)
 end
 host.next={dps,nil};host:tick();eq(calls,6,'no apply without a level')
end
print('terrain_s16: '..n..' checks passed (native definitions + mocked map/renderer/tick; no live-game claim)')
