-- S11 (levers, lever doors, Vor's candles). Run from any cwd with Lua 5.1/LuaJIT.
-- The native zone lists are built the way Entity:loadList/Entity:init build
-- them (real engine colours, base import, colour/back colour/tint
-- normalisation and defaults, nested load() mods such as Vor's image rewrite)
-- and stamped in the superload/mod/class/Grid.lua order. The native lever and
-- lever-door callbacks themselves are run against a mocked map, and the
-- superload/engine/Map.lua hooks against a mocked engine Map class.
local root=(debug.getinfo(1,'S').source:sub(2):match('^(.*[/\\])') or './')..'../'
local data=root..'../../modules/tome/data'
local n=0
local function eq(a,b,label) n=n+1;assert(a==b,label..': '..tostring(a)..' ~= '..tostring(b)) end
local function ser(v)
 if type(v)~='table' then return type(v)..':'..tostring(v) end
 local keys={};for k in pairs(v) do if type(k)~='string' or k:sub(1,1)~='_' then keys[#keys+1]=k end end
 table.sort(keys,function(a,b) return tostring(a)<tostring(b) end)
 local out={};for _,k in ipairs(keys) do out[#out+1]=tostring(k)..'='..ser(v[k]) end
 return '{'..table.concat(out,';')..'}'
end
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
eq(colors.UMBER.r..','..colors.UMBER.g..','..colors.UMBER.b,'142,69,0','engine UMBER')

-- Grid instances: methods live on the class (metatable), as in the engine.
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
-- Entity:init (default path): colour tables become channels, defaults filled.
local function init(t)
 if t.color then t.color_r,t.color_g,t.color_b=t.color.r,t.color.g,t.color.b;t.color=nil end
 if t.back_color then t.color_br,t.color_bg,t.color_bb=t.back_color.r,t.back_color.g,t.back_color.b;t.back_color=nil end
 t.display=t.display or '.'
 t.color_r=t.color_r or 0;t.color_g=t.color_g or 0;t.color_b=t.color_b or 0
 t.color_br=t.color_br or -1;t.color_bg=t.color_bg or -1;t.color_bb=t.color_bb or -1
 t.tint_r=t.tint_r or 1;t.tint_g=t.tint_g or 1;t.tint_b=t.tint_b or 1
 return setmetatable(t,meta)
end
local fenvBase={colors=colors,_t=function(s) return s end,
 resolvers=setmetatable({},{__index=function() return function(v) return v end end}),
 engine={DamageType=setmetatable({},{__index=function(_,k) return k end}),Map={TERRAIN=1}},
 rng={percent=function() return false end,range=function(a) return a end},currentZone={}}
-- Entity:loadList: base import (deep clone minus define_as), init, the load
-- mod, nested loads; each finished file is stamped (Grid.lua superload order).
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
-- ToME's string:prefix (engine utils), used by Vor's import rewrite.
string.prefix=string.prefix or function(str,pre) return str:sub(1,#pre)==pre end
local D={tannen=loadDefs('/data/zones/tannen-tower/grids.lua'),gorbat=loadDefs('/data/zones/gorbat-pride/grids.lua'),
 vor=loadDefs('/data/zones/vor-pride/grids.lua'),rak=loadDefs('/data/zones/rak-shor-pride/grids.lua'),
 arena=loadDefs('/data/zones/arena-unlock/grids.lua'),ruined=loadDefs('/data/zones/ruined-dungeon/grids.lua'),
 blood=loadDefs('/data/zones/ring-of-blood/grids.lua'),dreadfell=loadDefs('/data/zones/dreadfell/grids.lua')}
local Z={tannen='tannen-tower',gorbat='gorbat-pride',vor='vor-pride',rak='rak-shor-pride',arena='arena-unlock',ruined='ruined-dungeon',
 blood='ring-of-blood',dreadfell='dreadfell'}
local function place(set,id) return deep(assert(D[set][id],set..' '..id)) end
local function setZone(z) _G.game={zone={short_name=z}} end

-- Stamps: own callbacks (field@file:line) and prompt, per defining file.
local st=D.tannen.GENERIC_LEVER._checker_s11_source
eq(st.file..'|'..st.funcs,'/data/general/grids/basic.lua|block_move@@/data/general/grids/basic.lua:434','stamp GENERIC_LEVER')
st=D.gorbat.GENERIC_LEVER_SAND._checker_s11_source
eq(st.file..'|'..st.id..'|'..st.funcs,'/data/zones/gorbat-pride/grids.lua|GENERIC_LEVER_SAND|block_move@@/data/general/grids/basic.lua:434','stamp lever sand (inherited callback)')
eq(D.vor.GOTHIC_GENERIC_LEVER_DOOR_VERT._checker_s11_source.stop,'This door seems to have been sealed off. You need to find a way to open it.','stamp prompt')
eq(D.vor.GOTHIC_GENERIC_LEVER.image,'terrain/grass_burnt1.png','Vor rewrites the gothic lever floor')
eq(D.vor.CANDLE2._checker_s11_source.funcs,'','candle stamp has no callbacks')
eq(D.tannen.GENERIC_LEVER_DOOR._checker_s11_source,nil,'untiled lever door is not listed')

-- Positives: every reviewed identity in its zone, both adapters.
local forest={ -- set, id, kind, family for batch4/batch5
 {'gorbat','GENERIC_LEVER_SAND','hut-floor','gorbat-pride'},{'gorbat','ROCK_LEVER_DOOR','rock-door','gorbat-pride'},
 {'vor','GOTHIC_GENERIC_LEVER','burnt-floor','vor-pride'},{'vor','GOTHIC_GENERIC_LEVER_DOOR_HORIZ','gothic-door-closed-h','vor-pride'},
 {'vor','GOTHIC_GENERIC_LEVER_DOOR_VERT','gothic-door-closed-v','vor-pride'},{'vor','GOTHIC_GENERIC_LEVER_DOOR_HORIZ_OPEN','gothic-door-open-h','vor-pride'},
 {'vor','GOTHIC_GENERIC_LEVER_DOOR_OPEN_VERT','gothic-door-open-v','vor-pride'},{'vor','CANDLE1','gothic-floor','vor-pride'},
 {'vor','CANDLE2','gothic-floor','vor-pride'},{'vor','CANDLE3','gothic-floor','vor-pride'},
 {'rak','BONE_GENERIC_LEVER','floor','rakshor'},{'rak','BONE_GENERIC_LEVER_DOOR_HORIZ','door-closed','rakshor'},
 {'rak','BONE_GENERIC_LEVER_DOOR_VERT','door-closed','rakshor'}}
local function forestKind(g,fam) if fam=='rakshor' then return T.batch5Kind(g,fam) end;return T.batch4Kind(g,fam) end
local function candleParticle(g) g.embed_particles[1].args.base_size=64;g.embed_particles[1].args.use_shader={type='tentacles'} end
for _,c in ipairs(forest) do
 setZone(Z[c[1]])
 local g=place(c[1],c[2])
 eq(forestKind(g,c[4]),c[3],'S11 '..c[2])
 if c[2]:match('^CANDLE') then candleParticle(g);eq(forestKind(g,c[4]),c[3],'S11 candle with its loader args '..c[2]) end
 eq(T.classify(place(c[1],c[2])),nil,'S11 forest identity is not a stone kind '..c[2])
end
local stone={{'tannen','GENERIC_LEVER','prop'},{'tannen','GENERIC_LEVER_DOOR_HORIZ','lock','horizontal'},
 {'tannen','GENERIC_LEVER_DOOR_VERT','lock','vertical'},{'tannen','GENERIC_LEVER_DOOR_HORIZ_OPEN','door-open','horizontal'},
 {'tannen','GENERIC_LEVER_DOOR_OPEN_VERT','door-open','vertical'},{'arena','GENERIC_LEVER_DOOR_HORIZ','lock','horizontal'},
 {'arena','GENERIC_LEVER_DOOR_VERT','lock','vertical'},{'ruined','GENERIC_LEVER_DOOR_HORIZ','lock','horizontal'}}
for _,c in ipairs(stone) do
 setZone(Z[c[1]])
 local k,o=T.classify(place(c[1],c[2]))
 eq(k,c[3],'S11 stone '..c[1]..' '..c[2])
 if c[3]=='prop' then eq(o.image,'terrain/lever1_state1.png','S11 Tannen lever keeps its native MO') else eq(o,c[4],'S11 orientation '..c[2]) end
end
-- Zone scope: the same definitions elsewhere stay native.
for _,c in ipairs{{'blood','GENERIC_LEVER'},{'blood','GENERIC_LEVER_DOOR'},{'dreadfell','GENERIC_LEVER_DOOR_HORIZ'},
 {'arena','GENERIC_LEVER'},{'ruined','GENERIC_LEVER'}} do
 local g=D[c[1]][c[2]]
 if g then setZone(Z[c[1]]);eq(T.classify(deep(g)),nil,'S11 zone scope '..c[1]..' '..c[2]) end
end
setZone('grushnak-pride');eq(T.batch4Kind(place('vor','GOTHIC_GENERIC_LEVER'),'grushnak-pride'),nil,'S11 gothic lever outside Vor')
setZone('gorbat-pride');eq(T.batch4Kind(place('vor','CANDLE1'),'gorbat-pride'),nil,'S11 candle outside Vor')
setZone('vor-pride');eq(T.batch4Kind(place('gorbat','GENERIC_LEVER_SAND'),'vor-pride'),nil,'S11 lever sand outside Gorbat')
eq(T.batch5Kind(place('vor','GOTHIC_GENERIC_LEVER'),'rakshor'),nil,'S11 gothic lever not a bone kind')
-- Unlisted / unreachable states stay native.
for _,c in ipairs{{'tannen','GENERIC_LEVER_DOOR','tannen-tower'},{'tannen','GENERIC_LEVER_DOOR_OPEN','tannen-tower'},
 {'vor','GOTHIC_GENERIC_LEVER_DOOR','vor-pride'},{'vor','GOTHIC_GENERIC_LEVER_DOOR_OPEN','vor-pride'},{'vor','CANDLE','vor-pride'},
 {'vor','GOTHIC_GENERIC_TRIGGER_BOOL','vor-pride'},{'rak','BONE_GENERIC_LEVER_DOOR','rakshor'},{'rak','BONE_GENERIC_LEVER_DOOR_OPEN','rakshor'},
 {'rak','BONE_GENERIC_LEVER_DOOR_HORIZ_OPEN','rakshor'},{'rak','BONE_GENERIC_LEVER_DOOR_OPEN_VERT','rakshor'}} do
 setZone(Z[c[1]])
 eq(forestKind(place(c[1],c[2]),c[3]),nil,'S11 unlisted '..c[2])
 eq(T.classify(place(c[1],c[2])),nil,'S11 unlisted (stone) '..c[2])
end

-- Mutation negatives: every own field changed, removed, and extra fields.
local function kindOf(set,g)
 local saved=_G.game
 setZone(Z[set])
 local k
 if set=='tannen' or set=='arena' or set=='ruined' then k=T.classify(g) else k=forestKind(g,set=='rak' and 'rakshor' or Z[set]) end
 _G.game=saved
 return k
end
local cases={{'tannen','GENERIC_LEVER'},{'tannen','GENERIC_LEVER_DOOR_VERT'},{'tannen','GENERIC_LEVER_DOOR_HORIZ_OPEN'},
 {'gorbat','GENERIC_LEVER_SAND'},{'gorbat','ROCK_LEVER_DOOR'},{'vor','GOTHIC_GENERIC_LEVER'},{'vor','GOTHIC_GENERIC_LEVER_DOOR_VERT'},
 {'vor','GOTHIC_GENERIC_LEVER_DOOR_OPEN_VERT'},{'vor','CANDLE3'},{'rak','BONE_GENERIC_LEVER'},{'rak','BONE_GENERIC_LEVER_DOOR_HORIZ'},
 {'arena','GENERIC_LEVER_DOOR_HORIZ'}}
local function other(v)
 local t=type(v)
 if t=='string' then return v..'x' elseif t=='number' then return v+1 elseif t=='boolean' then return not v end
 local c=deep(v);c.extra_field=true;return c
end
local mutated=0
for _,c in ipairs(cases) do
 local base=place(c[1],c[2])
 eq(kindOf(c[1],deep(base))~=nil,true,'S11 mutation base accepted '..c[2])
 for k,v in pairs(base) do
  if type(k)=='string' and k:sub(1,1)~='_' and type(v)~='function' then
   local g=deep(base);g[k]=other(v)
   eq(kindOf(c[1],g),nil,'S11 changed '..c[2]..'.'..k);mutated=mutated+1
   g=deep(base);g[k]=nil
   eq(kindOf(c[1],g),nil,'S11 removed '..c[2]..'.'..k);mutated=mutated+1
  end
 end
 for k,v in pairs{does_block_move=true,block_move=function() return true end,on_stand=function() end,on_move=function() end,
  lever_dead=true,shader='lava',textures={},glow=true,change_level=1,change_zone='wilderness',dig='FLOOR',can_pass={pass_wall=1},
  air_level=-10,pass_projectile=true,door_player_check='Open?',on_lever_change=function() end,special_minimap={r=1},z=9,
  display_x=0.1,tint_r=0.5,embed_particles={{name='candle',rad=1,args={candle_id='light1'}}},replace_display={image='x.png'}} do
  if base[k]==nil then
   local g=deep(base);g[k]=v
   eq(kindOf(c[1],g),nil,'S11 extra '..c[2]..'.'..k);mutated=mutated+1
  end
 end
end
eq(mutated>250,true,'S11 mutation count '..mutated)
-- Callbacks: a wrapped callback, one defined at another line, a changed stamp.
do
 local g=place('tannen','GENERIC_LEVER');local orig=g.block_move
 g.block_move=function(...) return orig(...) end
 eq(kindOf('tannen',g),nil,'S11 wrapped lever callback')
 g=place('tannen','GENERIC_LEVER')
 g.block_move=assert(loadstring('\n\nreturn function(self,x,y,e,act) return true end','@/data/general/grids/basic.lua'))()
 eq(kindOf('tannen',g),nil,'S11 lever callback at another line of the same file')
 g=place('vor','GOTHIC_GENERIC_LEVER_DOOR_VERT');g.on_lever_change=place('tannen','GENERIC_LEVER_DOOR_VERT').on_lever_change
 eq(kindOf('vor',g),nil,'S11 gothic door with the basic.lua callback')
 g=place('gorbat','ROCK_LEVER_DOOR');g._checker_s11_source=deep(g._checker_s11_source);g._checker_s11_source.funcs='on_lever_change@@/data/zones/gorbat-pride/grids.lua:134'
 eq(kindOf('gorbat',g),nil,'S11 stamp from a changed definition')
 g=place('vor','GOTHIC_GENERIC_LEVER');g._checker_s11_source=nil
 eq(kindOf('vor',g),nil,'S11 old save (no stamp) lever')
 g=place('tannen','GENERIC_LEVER_DOOR_HORIZ');g._checker_s11_source=nil
 eq(kindOf('tannen',g),nil,'S11 old save (no stamp) lever door')
 g=place('vor','CANDLE1');g._checker_zone_source=nil
 eq(kindOf('vor',g),nil,'S11 Vor cell without the list stamp')
 g=place('rak','BONE_GENERIC_LEVER');g._checker_s11_source=deep(g._checker_s11_source);g._checker_s11_source.id='BONE_GENERIC_LEVER_DOOR_VERT'
 eq(kindOf('rak',g),nil,'S11 stamp of another id')
 g=place('tannen','GENERIC_LEVER_DOOR_VERT');g.door_player_stop='This door is open.'
 eq(kindOf('tannen',g),nil,'S11 prompt differs from the definition')
end
-- Layers.
for label,f in pairs{
 padlockMoved=function(g) g.add_displays[1].add_mos[1].display_x=0 end,
 padlockGone=function(g) g.add_displays[1].add_mos=nil end,
 doorArt=function(g) g.add_displays[1].image='terrain/granite_door1_open_vert.png' end,
 northZ=function(g) g.add_displays[2].z=17 end,
 extraLayer=function(g) g.add_displays[3]={image='terrain/padlock2.png'} end,
 layerShader=function(g) g.add_displays[2].shader='x' end,
 extraMos=function(g) g.add_mos={{image='terrain/padlock2.png'}} end} do
 local g=place('tannen','GENERIC_LEVER_DOOR_VERT');f(g)
 eq(kindOf('tannen',g),nil,'S11 changed lever-door layer '..label)
end
-- Candles: the exact embedded candle particle only.
for label,f in pairs{id=function(p) p.args.candle_id='light2' end,name=function(p) p.name='fire' end,rad=function(p) p.rad=2 end,
 arg=function(p) p.args.dx=1 end,key=function(p) p.shader=true end} do
 local g=place('vor','CANDLE1');candleParticle(g);f(g.embed_particles[1])
 eq(kindOf('vor',g),nil,'S11 candle particle changed '..label)
end
do local g=place('vor','CANDLE1');g.embed_particles[2]=deep(g.embed_particles[1]);eq(kindOf('vor',g),nil,'S11 two candle particles') end

-- The native lever and lever-door callbacks on a mocked map.
local function mockMap(w,h,fill)
 local m={w=w,h=h,map={},attr={},updates={},seen={},rem={}}
 for x=0,w-1 do for y=0,h-1 do m.map[x+y*w]={[1]=fill(x,y)} end end
 m.attrs=function(x,y,k,v) local a=m.attr[x+y*w] or {};m.attr[x+y*w]=a;if v~=nil then a[k]=v end;return a[k] end
 m.seens=function(x,y) return m.seen[x+y*w] and true or false end
 m.infovs=m.seens
 m.remembers=setmetatable({},{__call=function(_,x,y) return m.rem[x+y*w] and true or false end})
 m.updateMap=function(self,x,y) self.updates[#self.updates+1]=x..','..y end
 m.checkEntity=function(self,x,y,pos,what,...) local g=self(x,y,pos);if g then return g:check(what,x,y,...) end end
 return setmetatable(m,{__call=function(self,x,y,layer,g)
  if x<0 or y<0 or x>=w or y>=h then return end
  if g then self.map[x+y*w][layer or 1]=g;self:updateMap(x,y);return end
  return self.map[x+y*w][layer or 1]
 end})
end
-- mod/class/Grid.lua:480-518 (the parts these levels use: radius/spot apply).
methods.leverActivated=function(self,x,y,who)
 self.lever=not self.lever
 local m=game.level.map
 local val=m.attrs(x,y,'lever')
 for i=0,m.w-1 do for j=0,m.h-1 do
  if m.attrs(i,j,'lever_action_kind') then
   local old=m.attrs(i,j,'lever_action_value') or 0
   local new=old+(self.lever and val or -val)
   m.attrs(i,j,'lever_action_value',new)
   m:checkEntity(i,j,1,'on_lever_change',who,new,old)
  end
 end end
end
local who={player=true}
-- engine.Game:onTickEnd (named entries run once, at the end of the tick).
local ticks={}
local function onTickEnd(self,f,name)
 if name then for _,t in ipairs(ticks) do if t.name==name then return end end end
 ticks[#ticks+1]={f=f,name=name}
end
local function tickEnd() local q=ticks;ticks={};for _,t in ipairs(q) do t.f() end;return #q end
local function vorScene()
 -- burnt ground, the lever, the lever door (vertical), a candle, gothic floor
 local plan={';E;','#L#','.C.'}
 local sym={[';']='BURNT_GROUND',E='GOTHIC_GENERIC_LEVER',['#']='GOTHIC_WALL_NORTH2',L='GOTHIC_GENERIC_LEVER_DOOR_VERT',['.']='GOTHIC_FLOOR',C='CANDLE1'}
 local m=mockMap(3,3,function(x,y) local g=place('vor',sym[plan[y+1]:sub(x+1,x+1)]);if g.embed_particles then candleParticle(g) end;return g end)
 m.attrs(1,0,'lever',1);m.attrs(1,1,'lever_action',1);m.attrs(1,1,'lever_action_kind','doors')
 local host={zone={short_name='vor-pride',grid_list=D.vor},level={map=m,data={},level=1}}
 _G.game={zone=host.zone,level=host.level,log=function() end,onTickEnd=onTickEnd}
 game.checkerRepairTerrain=function(self,...) return T.repair(host,...) end
 return m,host
end
local m,host=vorScene()
local rules={}
for x=0,2 do for y=0,2 do local r={};for k,v in pairs(m(x,y,1)) do if type(k)=='string' and k:sub(1,1)~='_' and k~='replace_display' then r[k]=v end end;rules[x..','..y]=r end end
mode='refined';T.apply(host)
local function img(x,y) local g=m(x,y,1);return g.replace_display and g.replace_display.image end
local function top(x,y) local d=m(x,y,1).replace_display;local l=d and d.add_displays and d.add_displays[#d.add_displays];return l and l.image end
eq(img(1,0),'checker-revised+refined/burnt/floor1.png','S11 Vor lever on board burnt ground')
eq(top(1,0),'terrain/lever1_state1.png','S11 Vor lever keeps its native lever MO (off)')
eq(img(1,1),'checker-revised+refined/gothic/door-closed-vertical0.png','S11 Vor lever door is the board gothic door')
eq(top(1,1),'terrain/padlock2.png','S11 Vor lever door keeps the padlock')
eq(img(1,2),'checker-revised+refined/gothic/floor-'..({'a','b','c'})[((17+14)%3)+1]..'1.png','S11 Vor candle cell on board gothic floor')
eq(m(1,2,1).replace_display.add_displays,nil,'S11 candle adds no layer (the particle is the candle)')
eq(m(1,2,1).embed_particles[1].name,'candle','S11 candle keeps its particle definition')
eq(img(0,1),'checker-revised+refined/gothic/wall-2-1.png','S11 wall still joins the lever door')
eq(T.s11Stale(m,1,0),false,'S11 fresh lever display is current')
-- Pull: the native block_move (gothic.lua:328) with act=true.
local lever=m(1,0,1);local ruleBefore=rules['1,0']
m.updates={}
eq(lever:block_move(1,0,who,true),true,'S11 lever blocks the move (native)')
eq(lever.lever,true,'S11 lever state on')
eq(lever.add_mos[1].image,'terrain/lever1_state2.png','S11 native MO switched')
eq(T.s11Stale(m,1,0),true,'S11 board lever display is stale after the native switch')
eq(kindOf('vor',lever),'burnt-floor','S11 lever accepted in its on state')
T.repair(host,1,0,1,0)
eq(top(1,0),'terrain/lever1_state2.png','S11 repaint shows the on lever')
eq(T.s11Stale(m,1,0),false,'S11 repainted lever is current')
-- The lever reached the door: on_lever_change swapped in the open prototype.
local door=m(1,1,1)
eq(door.define_as,'GOTHIC_GENERIC_LEVER_DOOR_OPEN_VERT','S11 native lever door opened')
eq(door==D.vor.GOTHIC_GENERIC_LEVER_DOOR_OPEN_VERT,true,'S11 the zone prototype itself was placed')
eq(door.replace_display,nil,'S11 before the hook the new door is native')
T.s11Changed(m,1,1,D.vor.GOTHIC_GENERIC_LEVER_DOOR_VERT)
eq(img(1,1),'checker-revised+refined/gothic/door-open-vertical0.png','S11 hook draws the board open door')
eq(D.vor.GOTHIC_GENERIC_LEVER_DOOR_OPEN_VERT.replace_display,nil,'S11 the shared prototype is never drawn on')
eq(top(1,1),nil,'S11 open lever door has no padlock')
-- Pull back: the lever turns off and the door closes again.
lever=m(1,0,1);lever:block_move(1,0,who,true)
eq(lever.lever,false,'S11 lever off again')
T.repair(host,1,0,1,0)
eq(top(1,0),'terrain/lever1_state1.png','S11 repaint shows the off lever')
eq(m(1,1,1).define_as,'GOTHIC_GENERIC_LEVER_DOOR_VERT','S11 native door closed again')
T.s11Changed(m,1,1,D.vor.GOTHIC_GENERIC_LEVER_DOOR_OPEN_VERT)
eq(img(1,1),'checker-revised+refined/gothic/door-closed-vertical0.png','S11 hook draws the board closed door again')
-- Rule fields are the natives' own (the lever's are its native state fields).
for _,key in ipairs{'1,2','0,1','2,1'} do
 local x,y=key:match('(%d),(%d)');local g=m(tonumber(x),tonumber(y),1)
 for k,v in pairs(rules[key]) do eq(ser(g[k]),ser(v),'S11 rule field '..key..' '..k) end
end
for k,v in pairs(ruleBefore) do
 eq(ser(lever[k]),ser(v),'S11 lever back to its native off fields '..k)
end
-- A hook call for a non-S11 grid, or an old-save door, changes nothing.
local before=img(1,1)
T.s11Changed(m,1,1,place('vor','GOTHIC_DOOR_VERT'))
eq(img(1,1),before,'S11 hook ignores other grids')
-- Modes: blockout keeps the blocking reading; native restores everything.
mode='blockout';T.apply(host)
eq(img(1,1),'checker-revised+tree0.png','S11 blockout lever door blocks')
eq(top(1,0),'terrain/lever1_state1.png','S11 blockout keeps the lever MO')
mode='vanilla';T.apply(host)
for x=0,2 do for y=0,2 do eq(m(x,y,1).replace_display,nil,'S11 native mode restores '..x..','..y) end end
eq(T.s11Stale(m,1,0),false,'S11 no stale lever in native mode')
mode='refined';T.apply(host)
eq(top(1,0),'terrain/lever1_state1.png','S11 refined restore lever')
-- Old save: an unstamped lever stays native.
local om=mockMap(1,1,function() local g=place('vor','GOTHIC_GENERIC_LEVER');g._checker_s11_source=nil;return g end)
T.apply({zone={short_name='vor-pride'},level={map=om,data={},level=1}})
eq(om(0,0,1).replace_display,nil,'S11 old-save lever stays native')

-- Rak'shor (bone lever: bone.lua:189 applies to its spot itself) and Gorbat's rock.
do
 local plan={'-&-','-*-'}
 local sym={['-']='BONEFLOOR',['&']='BONE_GENERIC_LEVER',['*']='BONE_GENERIC_LEVER_DOOR_HORIZ'}
 local rm=mockMap(3,2,function(x,y) return place('rak',sym[plan[y+1]:sub(x+1,x+1)]) end)
 rm.attrs(1,0,'lever',1);rm.attrs(1,0,'lever_kind','pride-doors');rm.attrs(1,0,'lever_spot',{type='lever'})
 rm.attrs(1,1,'lever_action',1);rm.attrs(1,1,'lever_action_kind','pride-doors')
 local rh={zone={short_name='rak-shor-pride',grid_list=D.rak},level={map=rm,data={},level=1,pickSpot=function() return {x=1,y=1} end}}
 _G.game={zone=rh.zone,level=rh.level,log=function() end,onTickEnd=onTickEnd,checkerRepairTerrain=function(self,...) return T.repair(rh,...) end}
 T.apply(rh)
 local d=rm(1,0,1).replace_display
 eq(d.image,'checker-revised+refined/rakshor/floor1.png','S11 Rak\'shor lever on board bone floor')
 eq(d.add_displays[1].image,'terrain/lever1_state1.png','S11 Rak\'shor lever MO')
 eq(rm(1,1,1).replace_display.image,'checker-revised+refined/rakshor/door-closed0.png','S11 Rak\'shor lever door')
 eq(rm(1,1,1).replace_display.add_displays[1].image,'terrain/padlock2.png','S11 Rak\'shor padlock')
 local lv=rm(1,0,1)
 lv:block_move(1,0,who,true)
 eq(lv.lever,true,'S11 bone lever on');eq(T.s11Stale(rm,1,0),true,'S11 bone lever stale')
 eq(kindOf('rak',lv),'floor','S11 bone lever accepted on')
 T.repair(rh,1,0,1,0);eq(rm(1,0,1).replace_display.add_displays[1].image,'terrain/lever1_state2.png','S11 bone lever repainted')
 eq(rm(1,1,1).define_as,'BONE_DOOR_HORIZ_OPEN','S11 bone lever door opened into the plain bone door')
 T.s11Changed(rm,1,1,D.rak.BONE_GENERIC_LEVER_DOOR_HORIZ)
 eq(rm(1,1,1).replace_display.image,'checker-revised+refined/rakshor/door-open0.png','S11 opened bone door on the board')
end
do
 local gm=mockMap(2,1,function(x) return place('gorbat',x==0 and 'GENERIC_LEVER_SAND' or 'ROCK_LEVER_DOOR') end)
 gm.attrs(0,0,'lever',1);gm.attrs(1,0,'lever_action',1);gm.attrs(1,0,'lever_action_kind','pride-doors')
 local gh={zone={short_name='gorbat-pride',grid_list=D.gorbat},level={map=gm,data={},level=1}}
 _G.game={zone=gh.zone,level=gh.level,log=function() end,onTickEnd=onTickEnd,checkerRepairTerrain=function(self,...) return T.repair(gh,...) end}
 T.apply(gh)
 eq(gm(0,0,1).replace_display.image,'checker-revised+refined/bamboo/floor0.png','S11 Gorbat lever on the board hut floor')
 eq(gm(1,0,1).replace_display.image,'checker-revised+refined/beach/sand1.png','S11 Gorbat lever rock on board sand')
 eq(gm(1,0,1).replace_display.add_displays[1].image,'terrain/huge_rock.png','S11 Gorbat lever rock keeps the native rock')
 gm(0,0,1):block_move(0,0,who,true)
 eq(T.s11Stale(gm,0,0),true,'S11 Gorbat lever stale')
 eq(gm(1,0,1).define_as,'FLOOR','S11 native rock crumbled into FLOOR')
end

-- Stone adapter: Tannen's lever and doors, including a remembered door out of FOV.
do
 setZone('tannen-tower')
 local plan={'#&#','.*.'}
 local sym={['#']='HARDWALL',['&']='GENERIC_LEVER',['.']='FLOOR',['*']='GENERIC_LEVER_DOOR_HORIZ'}
 local tm=mockMap(3,2,function(x,y) return place('tannen',sym[plan[y+1]:sub(x+1,x+1)]) end)
 tm.attrs(1,0,'lever',1);tm.attrs(1,1,'lever_action',1);tm.attrs(1,1,'lever_action_kind','doors')
 local th={zone={short_name='tannen-tower',grid_list=D.tannen},level={map=tm,data={},level=1}}
 _G.game={zone=th.zone,level=th.level,log=function() end,onTickEnd=onTickEnd,checkerRepairTerrain=function(self,...) return T.repair(th,...) end}
 for x=0,2 do for y=0,1 do tm.seen[x+y*3]=true;tm.rem[x+y*3]=true;T.observe(tm,x,y,tm(x,y,1)) end end
 local r=T.render(tm,1,0,tm(1,0,1),'refined')
 eq(r.add_displays[#r.add_displays].image,'terrain/lever1_state1.png','S11 Tannen lever MO over the board floor')
 eq(r.image:match('korpul/floor%-[ab]%-0%-1')~=nil,true,'S11 Tannen lever on the board stone floor '..r.image)
 local d=T.render(tm,1,1,tm(1,1,1),'refined')
 eq(d.image:match('korpul%-?d?a?r?k?/door%-closed%-horizontal')~=nil,true,'S11 Tannen lever door is the board door '..d.image)
 eq(d.add_mos[1].image,'terrain/padlock2.png','S11 Tannen lever door padlock')
 -- The door is out of FOV but remembered when the lever opens it.
 tm.seen[1+1*3]=false
 tm(1,0,1):block_move(1,0,who,true)
 eq(T.observe(tm,1,0,tm(1,0,1)),true,'S11 Tannen lever re-observed after its native switch')
 r=T.render(tm,1,0,tm(1,0,1),'refined')
 eq(r.add_displays[#r.add_displays].image,'terrain/lever1_state2.png','S11 Tannen lever on')
 eq(tm(1,1,1).define_as,'GENERIC_LEVER_DOOR_HORIZ_OPEN','S11 Tannen door opened natively')
 d=T.render(tm,1,1,tm(1,1,1),'refined')
 eq(d.image:match('door%-closed')~=nil,true,'S11 without the hook the hidden door record is stale')
 T.s11Changed(tm,1,1,D.tannen.GENERIC_LEVER_DOOR_HORIZ)
 d=T.render(tm,1,1,tm(1,1,1),'refined')
 eq(d.image:match('door%-open%-horizontal')~=nil,true,'S11 hook re-reads the remembered door '..d.image)
 -- A cell not remembered is never read.
 local um=mockMap(1,1,function() return place('tannen','GENERIC_LEVER_DOOR_HORIZ_OPEN') end)
 _G.game.level={map=um}
 T.s11Changed(um,0,0,D.tannen.GENERIC_LEVER_DOOR_HORIZ)
 eq(um._checker_korpul,nil,'S11 hook creates no knowledge of an unremembered cell')
end

-- superload/engine/Map.lua against a mocked engine Map class.
do
 local calls={}
 local Base={TERRAIN=1}
 function Base:updateMap(x,y) calls[#calls+1]='update '..x..','..y end
 function Base:checkEntity(x,y,pos,what,...) calls[#calls+1]='check '..what;local g=self(x,y,pos);if g then return g:check(what,x,y,...) end end
 for _,k in ipairs{'apply','applyLite','applyExtraLite'} do Base[k]=function() end end
 local menv=setmetatable({loadPrevious=function() return Base end,require=function(name) return assert(modules[name],name) end},{__index=_G})
 local chunk=assert(loadfile(root..'superload/engine/Map.lua'));setfenv(chunk,menv)
 local MapClass=chunk()
 local mm,mh=vorScene()
 setmetatable(mm,{__index=MapClass,__call=getmetatable(mm).__call})
 mm.updateMap=nil;mm.checkEntity=nil
 T.apply(mh)
 local repairs=0
 game.checkerRepairTerrain=function(self,...) repairs=repairs+1;return T.repair(mh,...) end
 calls={};mm:updateMap(1,0)
 eq(repairs,0,'S11 Map hook: a current lever costs no repair')
 local lv=mm(1,0,1)
 mm.attrs(1,1,'lever_action_kind',false) -- first pull: the lever alone
 local seenMid
 local leverActivated=methods.leverActivated
 -- Inside the callback the lever is between states (MO switched, lever not yet toggled).
 methods.leverActivated=function(self,...) seenMid=kindOf('vor',self);return leverActivated(self,...) end
 lv:block_move(1,0,who,true)
 methods.leverActivated=leverActivated
 eq(seenMid,nil,'S11 the mid-callback lever state is not an exact state')
 eq(mm(1,0,1).replace_display.add_displays[1].image,'terrain/lever1_state1.png','S11 Map hook: no repaint inside the callback')
 eq(#ticks,1,'S11 Map hook: one tick-end repaint scheduled')
 mm:updateMap(1,0);eq(#ticks,1,'S11 Map hook: the tick-end repaint is named once per cell')
 tickEnd()
 eq(mm(1,0,1).replace_display.add_displays[1].image,'terrain/lever1_state2.png','S11 Map hook: the native updateMap request repainted the lever at tick end')
 eq(repairs,1,'S11 Map hook: one lever repair')
 eq(mm(1,1,1).define_as,'GOTHIC_GENERIC_LEVER_DOOR_VERT','S11 Map hook: unlinked door untouched')
 -- Second pull (lever off) reaches the door (lever_toggle: any change opens it).
 mm.attrs(1,1,'lever_action_kind','doors');mm.attrs(1,1,'lever_toggle',true)
 repairs=0;mm(1,0,1):block_move(1,0,who,true)
 eq(mm(1,1,1).define_as,'GOTHIC_GENERIC_LEVER_DOOR_OPEN_VERT','S11 Map hook: native door opened')
 eq(mm(1,1,1).replace_display.image,'checker-revised+refined/gothic/door-open-vertical0.png','S11 Map hook: on_lever_change repaint')
 eq(repairs,1,'S11 Map hook: one lever-door repair (it also re-reads the settled lever next to it)')
 eq(mm(1,0,1).replace_display.add_displays[1].image,'terrain/lever1_state1.png','S11 Map hook: lever off, repainted by the door repair')
 eq(tickEnd(),1,'S11 Map hook: the scheduled lever repaint runs');eq(repairs,1,'S11 Map hook: a current lever is not repaired again')
 calls={};repairs=0
 eq(mm:checkEntity(0,0,1,'block_move',who,false),nil,'S11 Map hook: other checks pass through')
 eq(repairs,0,'S11 Map hook: other checks never repair')
 mm:updateMap(0,2);eq(repairs,0,'S11 Map hook: other cells never repair')
end
print('terrain_s11: '..n..' checks passed (native definitions and callbacks + mocked map/renderer; no live-game claim)')
