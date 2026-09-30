-- S17 (Solipsist Dreamscape plane, dreamscape-talent): the zone-local CLOUD
-- floor on an exact field whitelist and void.lua OUTERSPACE on the space
-- contract, each gated by the plane's zone-list stamp and the dream manifest;
-- the plane joins the S16 direct-swap hook (tw4.S16_PLANES). Run from any cwd
-- with Lua 5.1/LuaJIT. Definitions are built the way Entity:loadList builds
-- them, as in tests/terrain_s16.lua (same harness); the manifest check at the
-- end reads the real data/terrain-dream-manifest.lua and data/gfx files.
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
-- The S17 manifest is exercised both mocked-complete and empty (native fallback).
local dreamFiles={}
T.dreamAssets.ready=true;T.dreamAssets.files=dreamFiles
local function dreamOn(on) setmetatable(dreamFiles,on and {__index=function() return true end} or nil) end
dreamOn(true)

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
local DS='/data/zones/dreamscape-talent/grids.lua'
local D={ds=loadDefs(DS),void=loadDefs('/data/general/grids/void.lua'),
 tr=loadDefs('/data/zones/temporal-reprieve-talent/grids.lua'),dreams=loadDefs('/data/zones/dreams/grids.lua')}
local function setZone(z) _G.game={zone={short_name=z},level={}} end
local function place(set,id) return deep(assert(D[set][id],set..' '..id)) end
local function kind(g,z) setZone(z);return T.s17Kind(g,z) end
local Z='dreamscape-talent'

-- Stamps.
eq(D.ds.CLOUD._checker_zone_source.file,DS,'dreamscape list stamps CLOUD')
eq(D.ds.OUTERSPACE._checker_zone_source.file,DS,'dreamscape list stamps nested OUTERSPACE')
eq(D.ds.OUTERSPACE._checker_void_source.file,'/data/general/grids/void.lua','dreamscape OUTERSPACE keeps its void stamp')
eq(D.void.OUTERSPACE._checker_zone_source,nil,'plain void.lua list has no zone stamp')
eq(D.ds.CLOUD.color_br,67,'back_color DARK_GREY initialised to color_br')
eq(D.ds.CLOUD.shader,'cloud_anim','native CLOUD animates through its shader')

-- Exact kinds.
eq(kind(place('ds','CLOUD'),Z),'dream-cloud','dreamscape CLOUD')
eq(kind(place('ds','OUTERSPACE'),Z),'dream-void','dreamscape OUTERSPACE')
local native=0
for id in pairs(D.ds) do
 if id~='CLOUD' and id~='OUTERSPACE' then native=native+1;eq(kind(place('ds',id),Z),nil,'dreamscape '..id..' stays native') end
end
eq(native>=10,true,'nested basic/void definitions checked')
-- Scope: other zones, other stamps, old saves.
for _,z in ipairs{'temporal-reprieve-talent','eidolon-plane','dreams','demon-plane-spell','town-point-zero','abashed-expanse'} do
 eq(T.s17Kind(place('ds','CLOUD'),z) or nil,nil,'dreamscape CLOUD outside the plane: '..z)
 eq(T.s17Kind(place('ds','OUTERSPACE'),z) or nil,nil,'dreamscape OUTERSPACE outside the plane: '..z)
end
eq(kind(place('void','OUTERSPACE'),Z),nil,'unstamped (old save) space stays native')
eq(kind(place('tr','OUTERSPACE'),Z),nil,'reprieve-stamped space in the dreamscape stays native')
do local g=place('ds','CLOUD');g._checker_zone_source=nil;eq(kind(g,Z),nil,'unstamped (old save) cloud stays native') end
do local g=place('ds','CLOUD');g._checker_zone_source={file='/data/zones/dreams/grids.lua',id='CLOUD'};eq(kind(g,Z),nil,'foreign-stamped cloud stays native') end
-- The S16 kinds stay off the dreamscape and the eidolon plane stays unlisted.
eq(T.s16Kind(place('ds','CLOUD'),Z) or nil,nil,'no S16 kind for CLOUD')
eq(T.s17Kind(place('ds','CLOUD'),'eidolon-plane') or nil,nil,'eidolon plane stays native')

-- Mutations: any rule, callback, layer or extra field falls back to native.
local other=function() end
for label,f in pairs{
 blocks=function(g) g.does_block_move=true end,sight=function(g) g.block_sight=true end,
 stand=function(g) g.on_stand=other end,move=function(g) g.on_move=other end,
 change=function(g) g.change_level=1 end,zone=function(g) g.change_zone='wilderness' end,
 pass=function(g) g.can_pass={pass_void=1} end,air=function(g) g.air_level=-40 end,
 image=function(g) g.image='terrain/clouds/cloud_normal_001.png' end,shader=function(g) g.shader=nil end,
 shaderArgs=function(g) g.shader_args={a=1} end,layer=function(g) g.add_displays={{image='x.png'}} end,
 mos=function(g) g.add_mos={{image='x.png'}} end,display=function(g) g.display='.' end,
 back=function(g) g.color_br=0 end,color=function(g) g.color_g=0 end,tint=function(g) g.tint_b=.5 end,
 name=function(g) g.name='cloud' end,subtype=function(g) g.subtype='void' end,ftype=function(g) g.type='wall' end,
 notice=function(g) g.notice=true end,remember=function(g) g.always_remember=true end,
 desc=function(g) g.desc='x' end,trap=function(g) g.special=true end,
 foreignDisplay=function(g) g.replace_display={image='x'} end,id=function(g) g.define_as='CLOUD2' end} do
 local g=place('ds','CLOUD');f(g);eq(kind(g,Z),nil,'S17 altered CLOUD ('..label..') stays native')
end
for label,f in pairs{blocks=function(g) g.does_block_move=nil end,sight=function(g) g.block_sight=true end,
 stand=function(g) g.on_stand=other end,pass=function(g) g.can_pass=nil end,image=function(g) g.image='x.png' end,
 air=function(g) g.air_level=nil end} do
 local g=place('ds','OUTERSPACE');f(g);eq(kind(g,Z),nil,'S17 altered OUTERSPACE ('..label..') stays native')
end

-- Mocked plane level through T.apply.
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
local R='checker-revised+refined/dream/'
local plan={'vvvvv','v~~~v','v~~vv','v~v~v','vvvvv'}
local function level(set)
 local m=mockMap(#plan[1],#plan,function(x,y) return place(set,plan[y+1]:sub(x+1,x+1)=='~' and 'CLOUD' or 'OUTERSPACE') end)
 return {zone={short_name=Z,max_level=1},level={map=m,data={},level=1}},m
end
do
 local host,m=level('ds')
 _G.game={zone=host.zone,level=host.level,log=function() end}
 local before=rulesOf(m)
 mode='refined';T.apply(host)
 local on=imgs(m)
 -- Masks (N=1 E=2 S=4 W=8, cloud neighbours), variant (x*17+y*7)%3, parity (x+y)%2.
 local function cloud(x,y,mask) return R..'cloud-'..({'a','b','c'})[((x*17+y*7)%3)+1]..'-'..mask..'-'..((x+y)%2)..'.png' end
 local function void(x,y) return R..'void-'..({'a','b'})[((x*17+y*7)%2)+1]..'-'..((x+y)%2)..'.png' end
 eq(on['1,1'],cloud(1,1,2+4),'S17 NW cloud corner')
 eq(on['2,1'],cloud(2,1,2+4+8),'S17 north cloud edge')
 eq(on['3,1'],cloud(3,1,8),'S17 NE cloud (open N/E/S)')
 eq(on['1,2'],cloud(1,2,1+2+4),'S17 west cloud edge')
 eq(on['2,2'],cloud(2,2,1+8),'S17 cloud with void E and S')
 eq(on['1,3'],cloud(1,3,1),'S17 cloud peninsula')
 eq(on['3,3'],cloud(3,3,0),'S17 lone cloud cell')
 eq(on['0,0'],void(0,0),'S17 void corner')
 eq(on['4,2'],void(4,2),'S17 void')
 eq(on['2,3'],void(2,3),'S17 void notch')
 rulesSame(m,before,'S17 refined')
 T.apply(host)
 for key,v in pairs(imgs(m)) do eq(v,on[key],'S17 idempotent '..key) end
 mode='vanilla';T.apply(host)
 for key,v in pairs(imgs(m)) do eq(v,false,'S17 native mode '..key) end
 for x=0,m.w-1 do for y=0,m.h-1 do eq(m(x,y,1)._checker_terrain,nil,'S17 native state cleared') end end
 rulesSame(m,before,'S17 native')
 mode='refined';T.apply(host)
 for key,v in pairs(imgs(m)) do eq(v,on[key],'S17 restored '..key) end
 rulesSame(m,before,'S17 restored')
 mode='blockout';T.apply(host)
 eq(m(0,0,1).replace_display.image,'checker-revised+tree0.png','S17 blockout void reads as blocker')
 eq(m(1,1,1).replace_display.image,'checker-revised+grass0.png','S17 blockout cloud reads as floor')
 -- Missing/partial manifest: the dream cells return to native.
 mode='refined';dreamOn(false);T.apply(host)
 for key,v in pairs(imgs(m)) do eq(v,false,'S17 no manifest native '..key) end
 rulesSame(m,before,'S17 no manifest')
 dreamOn(true);T.apply(host)
 for key,v in pairs(imgs(m)) do eq(v,on[key],'S17 manifest back '..key) end
end
-- Old-save plane: unstamped cells stay native.
do
 local m=mockMap(2,1,function(x) return x==0 and deep(D.void.OUTERSPACE) or (function() local g=place('ds','CLOUD');g._checker_zone_source=nil;return g end)() end)
 local host={zone={short_name=Z,max_level=1},level={map=m,data={},level=1}}
 _G.game={zone=host.zone,level=host.level,log=function() end}
 mode='refined';T.apply(host)
 eq(m(0,0,1).replace_display,nil,'S17 old-save space stays native')
 eq(m(1,0,1).replace_display,nil,'S17 old-save cloud stays native')
end

-- directSwap: the dreamscape now installs/restores; the eidolon plane does not.
local Zt=function(s) return {short_name=s} end
local src,ds=Zt('trollmire'),Zt(Z)
eq(T.directSwap(src,ds),true,'swap into the dreamscape')
eq(T.directSwap(ds,src),true,'swap back from the dreamscape')
eq(T.directSwap(ds,ds),false,'same plane zone')
eq(T.directSwap(src,Zt('eidolon-plane')),false,'no hook into the eidolon plane')
eq(T.directSwap(Zt('eidolon-plane'),src),false,'no hook out of the eidolon plane')
eq(T.directSwap(src,Zt('dreams')),false,'no hook into the dreams zone')

-- The real manifest: exactly the 100 exported files, all present.
do
 local f=assert(loadfile(root..'data/terrain-dream-manifest.lua'))()
 eq(f.ready,true,'dream manifest ready')
 local count=0
 for file,ok in pairs(f.files) do
  count=count+1
  local rel=file:match('^checker%-revised%+(refined/dream/[%w%-]+%-[01]%.png)$')
  eq(rel~=nil and ok,true,'dream manifest entry '..file)
  local h=io.open(root..'data/gfx/'..rel,'rb');eq(h~=nil,true,'dream file exists '..rel);if h then h:close() end
 end
 eq(count,100,'dream manifest count')
 for _,v in ipairs{'a','b','c'} do for mask=0,15 do for p=0,1 do
  eq(f.files['checker-revised+refined/dream/cloud-'..v..'-'..mask..'-'..p..'.png'],true,'cloud '..v..mask..p)
 end end end
 for _,v in ipairs{'a','b'} do for p=0,1 do eq(f.files['checker-revised+refined/dream/void-'..v..'-'..p..'.png'],true,'void '..v..p) end end
end
print('terrain_s17: '..n..' checks passed (native definitions + mocked map/renderer; no live-game claim)')
