-- lua5.1 / luajit tests/clone_display.lua
-- Execute native class clone/cloneFull/cloneCustom/cloneForSave, native
-- Actor:cloneActor and Entity map-object methods with the actual addon hooks.
-- Only graphics, construction and unrelated actor services are adapted. The
-- fake C map objects are USERDATA: table fakes would hide the shared-MO bug.
local script=debug.getinfo(1,'S').source:sub(2)
local root=(script:match('^(.*[/\\])') or './')..'../'
local engine=root..'../../engines/default/engine/'
local checks=0
local function equal(actual,expected,label)
 checks=checks+1
 assert(actual==expected,label..': expected '..tostring(expected)..', got '..tostring(actual))
end
local function different(a,b,label) equal(a~=b,true,label) end
local function read(path)
 local f=assert(io.open(path,'r'));local text=f:read('*a');f:close();return text
end
local function section(path,first,after)
 local source=read(path)
 local start=assert(source:find(first,1,true),'native section moved: '..first)
 local stop=assert(source:find(after,start, true),'native boundary moved: '..after)
 return source:sub(start,stop-1)
end
local function compile(source,name,environment)
 if setfenv then
  local chunk=assert(loadstring(source,name));setfenv(chunk,environment);return chunk
 end
 return assert(load(source,name,'t',environment))
end
local function scope(values) return setmetatable(values or {},{__index=_G}) end

local nativeTable=setmetatable({},{__index=table})
local utilities=scope{table=nativeTable}
compile(section(engine..'utils.lua','function table.clone(', 'function table.mergeAppendArray('),
 '@native-table-clone-merge',utilities)()
compile(section(engine..'utils.lua','function table.update(', '--- Creates a read-only table'),
 '@native-table-update',utilities)()
local Class={}
compile(section(engine..'class.lua','local function clonerecurs(d)', '--- Replaces the object with an other'),
 '@native-class-clones',scope{_M=Class,table=nativeTable})()
compile(section(engine..'class.lua','function _M:isClassName(', 'function _M:runInherited('),
 '@native-class-identity',scope{_M=Class})()

assert(type(newproxy)=='function','run with Lua 5.1 or LuaJIT: userdata proxy required')
local moState=setmetatable({},{__mode='k'})
local moMethods={}
function moMethods:isValid() return moState[self].valid end
function moMethods:invalidate()
 local s=moState[self];s.valid=false;s.invalidations=s.invalidations+1
end
function moMethods:displayCallback(callback)
 local s=moState[self];s.callback=callback;s.callback_writes=s.callback_writes+1
end
function moMethods:tint(...) moState[self].tint={...} end
function moMethods:texture(...) moState[self].texture={...} end
function moMethods:setMoveAnim(...) moState[self].movement={...} end
function moMethods:resetMoveAnim() moState[self].movement=nil end
function moMethods:flipX(value) moState[self].flip=value end
local function newMO(uid)
 local mo=newproxy(true)
 getmetatable(mo).__index=moMethods
 moState[mo]={uid=uid,valid=true,invalidations=0,callback_writes=0}
 return mo
end
local env=scope{
 config={settings={cheat=false,tome={checker_tokens_enabled=true}}},
 __module_extra_info={},
 core={map={newObject=newMO},shader={active=function() return false end}},
}
local Entity=setmetatable({_NAME='engine.Entity'},{__index=Class})
local uids={}
local entityEnv=scope{_M=Entity,__uids=uids,core=env.core}
compile('local next_uid=1\n'..section(engine..'Entity.lua','function _M:cloned(src)',
 '--- If we are replaced'), '@native-Entity-cloned',entityEnv)()
compile(section(engine..'Entity.lua','function _M:makeMapObject(', '--- Setup movement animation'),
 '@native-Entity-map-objects',entityEnv)()
compile(section(engine..'Entity.lua','function _M:setMoveAnim(', '--- Sets the flip state'),
 '@native-Entity-move-animation',entityEnv)()
compile(section(engine..'Entity.lua','function _M:MOflipX(', '--- Sets the flip state of MO and associated MOs\n-- @param v passed to the map object\'s flipY()'),
 '@native-Entity-flip',entityEnv)()
compile(section(engine..'Entity.lua','function _M:check(prop,', '--- temporary values storage'),
 '@native-Entity-check',entityEnv)()
function Entity:defineDisplayCallback() end
function Entity.new(fields)
 fields.__CLASSNAME='engine.Entity';fields.__ATOMIC=true
 setmetatable(fields,{__index=Entity});Entity.cloned(fields)
 return fields
end
local ActorBase=setmetatable({_NAME='mod.class.Actor'},{__index=Entity})
compile(section(engine..'Actor.lua','_M.clone_nodes =', '--- Setup minimap color for this entity'),
 '@native-Actor-cloneActor',scope{_M=ActorBase,table=nativeTable})()
local delegated=setmetatable({},{__mode='k'})
local nativeResult={}
local function delegate(self,source,...)
 -- Observe delegation without replacing native UID/changed semantics.
 local prior=delegated[self]
 delegated[self]={calls=(prior and prior.calls or 0)+1,source=source,args={...},
  had_token=self._checker_token~=nil}
 Entity.cloned(self,source)
 return nativeResult
end
ActorBase.cloned=delegate
local drawn
function ActorBase:bigTacticalFrame() drawn=self end
function ActorBase:smallTacticalFrame() drawn=self end
function ActorBase:getParticlesList() return {} end
function ActorBase:attr(key) return self[key] end
function ActorBase:hasEffect() return nil end
function ActorBase:removeParticles() error('clone/render must not remove a particle') end
local dollRebuilds=setmetatable({},{__mode='k'})
function ActorBase:updateModdableTile() dollRebuilds[self]=(dollRebuilds[self] or 0)+1 end
local modules={['engine.Map']={},['engine.Entity']=Entity}
for name,file in pairs{
 ['mod.class.CheckerTokens']='CheckerTokens.lua',
 ['mod.class.CheckerTokenStyle']='CheckerTokenStyle.lua',
 ['mod.class.CheckerOptions']='CheckerOptions.lua',
 ['mod.class.CheckerPlayerTokens']='CheckerPlayerTokens.lua',
} do modules[name]=compile(read(root..'overload/mod/class/'..file),'@'..file,env)() end
env.require=function(name) return assert(modules[name],'unexpected dependency '..name) end
env.loadPrevious=function() return ActorBase end
local Actor=compile(read(root..'superload/mod/class/Actor.lua'),'@checker-Actor',env)()
env.loadPrevious=function() return {} end
local Game=compile(read(root..'superload/mod/class/Game.lua'),'@checker-Game',env)()
local game=setmetatable({level={map={tile_w=64}},always_target=false},{__index=Game})
env.game=game
local Tokens=modules['mod.class.CheckerTokens']
local tiles={use_images=true,get=function() return 'texture',1,1,64,64,0,0 end}
local function actor()
 local entry=assert(Tokens.by_id.wolf)
 local a=setmetatable({__CLASSNAME='mod.class.NPC',__ATOMIC=true,
  name=entry.name,image=entry.image,type=entry.type,subtype=entry.subtype,
  ai='test',rank=2,life=37,max_life=60,size_category=2,x=4,y=5,
 },{__index=Actor})
 Entity.cloned(a)
 return a
end
local function render(a)
 local mos={};a:getMapObjects(tiles,mos,10)
 equal(mos[10],a._mo,'native actor layer points at body')
 if a._checker_token then equal(mos[11],a._checker_token.overlay._mo,'overlay uses next actor layer') end
 return mos
end
local function snapshot(a)
 local s=a._checker_token
 return {state=s,display=a.replace_display,body=a._mo,last=a._last_mo,
  body_callback=moState[a._mo].callback,body_writes=moState[a._mo].callback_writes,
  overlay=s.overlay,overlay_mo=s.overlay._mo,overlay_callback=moState[s.overlay._mo].callback,
  overlay_writes=moState[s.overlay._mo].callback_writes,origin=a._checker_token_origin,
  uid=a.uid,life=a.life,max_life=a.max_life,rank=a.rank,x=a.x,y=a.y}
end
local function parentUnchanged(a,before,label)
 equal(a._checker_token,before.state,label..' parent state identity')
 equal(a.replace_display,before.display,label..' parent display identity')
 equal(a._mo,before.body,label..' parent body cache')
 equal(a._last_mo,before.last,label..' parent last cache')
 equal(moState[a._mo].callback,before.body_callback,label..' parent body callback')
 equal(moState[a._mo].callback_writes,before.body_writes,label..' parent callback never rebound')
 equal(moState[a._mo].invalidations,0,label..' parent body never invalidated')
 equal(a._mo:isValid(),true,label..' parent body stays valid')
 equal(before.state.overlay,before.overlay,label..' parent overlay identity')
 equal(before.overlay._mo,before.overlay_mo,label..' parent overlay cache')
 equal(moState[before.overlay_mo].callback,before.overlay_callback,label..' parent overlay callback')
 equal(moState[before.overlay_mo].callback_writes,before.overlay_writes,label..' parent overlay never rebound')
 equal(moState[before.overlay_mo].invalidations,0,label..' parent overlay never invalidated')
 equal(before.overlay_mo:isValid(),true,label..' parent overlay stays valid')
 equal(a._checker_token_origin,before.origin,label..' parent origin record')
 for _,key in ipairs{'uid','life','max_life','rank','x','y'} do equal(a[key],before[key],label..' parent '..key) end
end
local modes={
 {name='clone',run=function(a,post) return a:clone(post) end},
 {name='cloneFull',run=function(a,post) return a:cloneFull(post) end},
 {name='cloneCustom',run=function(a,post)
  return a:cloneCustom({_mo=false,_last_mo=false},nil,post)
 end},
 {name='cloneActor',run=function(a,post) return a:cloneActor(post) end},
}

-- Negative control: bypass only the new hook in this local class. The actual
-- native cloneActor plus existing rendering reproduces both shared userdata
-- and a changed parent callback. No production source is edited or copied.
local fixedCloned=Actor.cloned
Actor.cloned=delegate
local unfixed=actor();render(unfixed)
local unfixedBody=unfixed._mo
local unfixedCallback=moState[unfixedBody].callback
local unfixedChild=unfixed:cloneActor();render(unfixedChild)
equal(unfixedChild._mo,unfixedBody,'negative control reproduces shared body MO')
different(moState[unfixedBody].callback,unfixedCallback,'negative control catches overwritten parent callback')
Actor.cloned=fixedCloned

for _,mode in ipairs(modes) do
 local label=mode.name
 local parent=actor();render(parent)
 local before=snapshot(parent)
 local child=mode.run(parent)
 different(child,parent,label..' produces a different actor')
 equal(delegated[child].calls,1,label..' original cloned invoked once')
 equal(delegated[child].source,parent,label..' original cloned receives source')
 equal(delegated[child].had_token,true,label..' delegate runs before token cleanup')
 different(child.uid,parent.uid,label..' native cloned allocates a fresh uid')
 equal(uids[child.uid],child,label..' native UID registry retained')
 equal(child.changed,true,label..' native changed flag retained')
 equal(child._checker_token,nil,label..' clone drops inherited token ownership')
 equal(child.replace_display,nil,label..' clone restores native body before rebuilding')
 equal(child._mo,nil,label..' clone drops borrowed root body cache')
 equal(child._last_mo,nil,label..' clone drops borrowed root last cache')
 parentUnchanged(parent,before,label..' after clone')
 render(child)
 equal(child._checker_token.id,'wolf',label..' clone is identified from its actual body')
 different(child._checker_token.display,before.display,label..' owns a new body Entity')
 different(child._checker_token.overlay,before.overlay,label..' owns a new overlay Entity')
 different(child._mo,before.body,label..' owns independent body userdata')
 different(child._checker_token.overlay._mo,before.overlay_mo,label..' owns independent overlay userdata')
 equal(child.replace_display,child._checker_token.display,label..' body ownership consistent')
 equal(child._mo,child.replace_display._mo,label..' native body/cache references consistent')
 equal(moState[child._mo].uid,child.replace_display.uid,label..' body MO belongs to the new Entity uid')
 parentUnchanged(parent,before,label..' after render')
 local callback=moState[child._mo].callback
 callback(0,0,64,64,1,false,0,0)
 equal(drawn,child,label..' child callback captures child')
 before.body_callback(0,0,64,64,1,false,0,0)
 equal(drawn,parent,label..' parent callback still captures parent')
 child.x,child.y=6,5;child:setMoveAnim(5,5,8)
 equal(moState[before.body].movement,nil,label..' child movement does not animate parent body')
 equal(moState[before.overlay_mo].movement,nil,label..' child movement does not animate parent overlay')
 equal(moState[child._mo].movement[3],6,label..' native movement targets child coordinates')
 child:removeAllMOs()
 parentUnchanged(parent,before,label..' after child invalidation')
 equal(moState[before.body].texture[1],0,label..' parent texture remains bound')

 -- An owned original replacement is restored and then conservatively kept.
 local original=Entity.new{image='external-original.png'}
 parent._checker_token.original=original
 local restored=mode.run(parent)
 equal(restored.replace_display.image,original.image,label..' owned original display restored')
 equal(game:checkerRefreshActor(restored),nil,label..' restored external body stays native')
 equal(restored._checker_token,nil,label..' restored original is not claimed')
 if label=='clone' then equal(restored.replace_display,original,label..' shallow original reference retained')
 else different(restored.replace_display,original,label..' native deep clone of original retained') end
 parent._checker_token.original=nil
 parentUnchanged(parent,before,label..' after original restoration')

 -- The clone body can change in a native post-copy. Never resurrect its old
 -- wolf token based only on inherited state.id or cached artwork.
 local unknown=mode.run(parent,{name='uncovered creature with wolf artwork'})
 equal(game:checkerRefreshActor(unknown),nil,label..' unknown post-copy body keeps native display')
 equal(unknown._checker_token,nil,label..' unknown clone has no token')
 equal(unknown.replace_display,nil,label..' unknown clone does not retain inherited art')
 equal(unknown.image,parent.image,label..' unknown clone native image is preserved')
 parentUnchanged(parent,before,label..' after unknown clone')

 -- A replacement installed externally after the token must survive cloning.
 local foreign=Entity.new{image='external-transformation.png'}
 parent.replace_display=foreign
 local transformed=mode.run(parent)
 equal(transformed._checker_token,nil,label..' stale token state discarded')
 equal(transformed.replace_display.image,foreign.image,label..' foreign display preserved')
 if label=='clone' then equal(transformed.replace_display,foreign,label..' shallow foreign reference retained')
 else different(transformed.replace_display,foreign,label..' deep foreign Entity retained') end
 equal(game:checkerRefreshActor(transformed),nil,label..' foreign body cannot be remapped')
 equal(parent.replace_display,foreign,label..' source external display untouched')
 parent.replace_display=before.display
 parentUnchanged(parent,before,label..' after foreign clone')

 -- With tokens disabled, cloning still discards borrowed caches and the
 -- actual render path rebuilds a native actor instead of an old token.
 env.config.settings.tome.checker_tokens_enabled=false
 local disabled=mode.run(parent);render(disabled)
 equal(disabled._checker_token,nil,label..' disabled clone stays native')
 equal(disabled.replace_display,nil,label..' disabled clone has no token replacement')
 different(disabled._mo,before.body,label..' disabled native render has its own body MO')
 parentUnchanged(parent,before,label..' with tokens disabled')
 env.config.settings.tome.checker_tokens_enabled=true

 -- Random-origin records are scalar provenance, not render ownership. Keep
 -- an independent native copy that still authenticates the generated body.
 local random=actor()
 local capture=assert(Tokens.captureRandomOrigin(random))
 random.name,random.unique,random.define_as,random.randboss='Opaque Clone','Opaque Clone','RND_BOSS_CLONE',true
 equal(Tokens.recordRandomOrigin(random,capture,'RND_BOSS_CLONE'),'wolf',label..' random origin setup')
 render(random)
 local randomBefore=snapshot(random)
 local randomChild=mode.run(random)
 different(randomChild._checker_token_origin,random._checker_token_origin,label..' origin table independently copied')
 for key,value in pairs(random._checker_token_origin) do
  equal(type(value)=='string' or type(value)=='number' or type(value)=='boolean',true,label..' origin remains scalar '..key)
  equal(randomChild._checker_token_origin[key],value,label..' origin field preserved '..key)
 end
 equal(game:checkerRefreshActor(randomChild),'wolf',label..' random clone identifies from copied origin')
 render(randomChild)
 different(randomChild._mo,randomBefore.body,label..' random clone body independent')
 parentUnchanged(random,randomBefore,label..' random-origin clone')
end

-- A non-token actor must not gain this cleanup or have its external display
-- erased merely because the base cloned method ran.
local native=actor();native.name='unknown native creature'
local external=Entity.new{image='native-external.png'}
native.replace_display=external
local nativeBody=newMO(native.uid)
native._mo,native._last_mo=nativeBody,nativeBody
local oldUid=native.uid
local result=native:cloned(native,'forwarded',17)
equal(result,nativeResult,'original cloned return value preserved')
equal(delegated[native].args[1],'forwarded','original cloned receives first extra argument')
equal(delegated[native].args[2],17,'original cloned receives second extra argument')
different(native.uid,oldUid,'native-only delegation still allocates uid')
equal(native._mo,nativeBody,'non-token actor root cache is left to native behavior')
equal(native._last_mo,nativeBody,'non-token actor last cache is untouched')
equal(native.replace_display,external,'non-token external display unchanged')
equal(native._checker_token,nil,'non-token actor gains no token state')
equal(moState[nativeBody].invalidations,0,'non-token cache not invalidated by hook')

-- Native save cloning suppresses cloned callbacks. Ownership must remain in
-- that graph so a later serialized readback can restore native/token display.
local source=actor();render(source)
local before=snapshot(source)
local saved,count=source:cloneForSave()
equal(delegated[saved],nil,'save clone does not run actor cloned hook')
equal(saved.uid,source.uid,'save clone preserves native actor uid')
equal(saved._checker_token.display,saved.replace_display,'save graph keeps shared ownership reference')
different(saved._checker_token,source._checker_token,'save graph owns a copied state table')
different(saved.replace_display,source.replace_display,'save graph copies body Entity')
different(saved._checker_token.overlay,source._checker_token.overlay,'save graph copies overlay Entity')
equal(count>=3,true,'save clone includes actor, body and overlay Entities')
parentUnchanged(source,before,'save clone')
-- Exercise the real native Entity movement forwarding through this addon.
-- Body trails stay native; tactical state is never drawn as a blur replica.
local moving=actor();render(moving)
for _,motion in ipairs{{8,5,8,.15},{9,5,2,0},{3,0,8,.15},{3}} do
 moving:setMoveAnim(2,3,unpack(motion))
 local body=moState[moving._mo].movement
 local overlay=moState[moving._checker_token.overlay._mo].movement
 local expected={2,3,moving.x,moving.y,unpack(motion)}
 for i=1,8 do
  equal(body[i],expected[i],'body preserves native move argument '..i)
  equal(overlay[i],i==6 and 0 or expected[i],'overlay preserves trajectory, excludes blur '..i)
 end
 moving:resetMoveAnim()
 equal(moState[moving._mo].movement,nil,'reset body motion')
 equal(moState[moving._checker_token.overlay._mo].movement,nil,'reset overlay motion')
end
native:setMoveAnim(1,2,9,5,8,.15)
equal(moState[nativeBody].movement[6],5,'uncovered actor keeps native blur')
local ownedOverlay=moving._checker_token.overlay._mo
moving.replace_display=external
moving:setMoveAnim(1,2,9,5,8,.15)
equal(moState[moving._mo].movement[6],5,'foreign replacement keeps native blur')
equal(moState[ownedOverlay].movement,nil,'stale overlay is not animated after foreign replacement')
local Options=modules['mod.class.CheckerOptions']
local facing=actor();render(facing)
facing:MOflipX(true)
equal(facing._flipx,true,'fixed facing remembers native intent')
equal(moState[facing._mo].flip,false,'fixed facing does not mirror owned artwork')
Options.setTokenFacing('native')
render(facing)
equal(moState[facing._mo].flip,true,'native facing immediately restores last intent')
facing:MOflipX(false)
equal(moState[facing._mo].flip,false,'native facing follows the next direction')
facing:MOflipX(true)
Options.setTokenFacing('fixed');render(facing)
equal(moState[facing._mo].flip,false,'switching back fixes the art immediately')
local savedFacing=facing:cloneForSave();render(savedFacing)
equal(savedFacing._flipx,true,'save graph retains native intent')
equal(moState[savedFacing._mo].flip,false,'reconstructed fixed token is unmirrored')
Options.setTokensEnabled(false);game:checkerRefreshActor(facing);render(facing)
equal(facing._checker_token,nil,'disable restores native identity')
equal(moState[facing._mo].flip,true,'native fallback restores requested direction after rebuild')
native:MOflipX(true)
equal(moState[native._mo].flip,true,'uncovered actor retains native flip')
Options.setTokensEnabled(true)

-- Callback inputs reproduce the actual C contract: body x/y include inset
-- and twitch, overlay x/y are the lifted full-cell origin, tlx/tly omit lift.
-- Compare both callback paths to the independently known full-cell center.
game.level.map.view_faction='players'
local framed=actor();local sample
function framed:checkerTacticalFrame(map,x,y,w,h) sample={x=x,y=y,w=w,h=h} end
for _,cell in ipairs{48,64,96} do
 for _,size in ipairs{1,2,4} do
  game.level.map.tile_w=cell;framed.size_category=size;render(framed)
  local s=framed._checker_token;local width=cell*s.scale;local inset=(cell-width)/2
  for _,lift in ipairs{0,cell*.1} do
   local x,y=123,245-lift
   moState[s.overlay._mo].callback(x,y,cell,cell,1,true,123,245)
   equal(math.abs(sample.x+sample.w/s.scale/2-(123+cell/2))<1e-8,true,'overlay horizontal center')
   equal(math.abs(sample.y+sample.h/s.scale/2-(245+cell/2-lift))<1e-8,true,'overlay follows disk lift')
   for _,target in ipairs{'old',true} do
    game.always_target=target;s.overlay_active=false
    moState[framed._mo].callback(x+inset,y+inset,width,width,1,true,123+inset,245+inset)
    equal(math.abs(sample.x+sample.w/s.scale/2-(123+cell/2))<1e-8,true,'fallback inset-corrected horizontal center')
    equal(math.abs(sample.y+sample.h/s.scale/2-(245+cell/2-lift))<1e-8,true,'fallback follows lift without double inset')
   end
   s.overlay_active=true
  end
 end
end
-- A production player token uses exactly the same owned-token render path as
-- creatures and the fixture hero: one diameter, overlay layer, cyan player
-- ring (relation from the viewer, not the token id). Clones rebuild a doll.
game.always_target=true
local PlayerTokens=modules['mod.class.CheckerPlayerTokens']
local Style=modules['mod.class.CheckerTokenStyle']
PlayerTokens.available.human_male=true
local heroActor=setmetatable({__CLASSNAME='mod.class.Player',__ATOMIC=true,name='Anyname',
 image='player/human_male/base_shadow_01.png',add_mos={{image='doll.png'}},moddable_tile='human_#sex#',male=true,
 descriptor={subrace='Cornac',sex='Male',subclass='Berserker'},rank=2,life=50,max_life=60,size_category=3,x=2,y=2},{__index=Actor})
Entity.cloned(heroActor)
game.party={findMember=function() return heroActor end,hasMember=function() return true end}
game.level.map.tile_w=64
render(heroActor)
equal(heroActor._checker_token.id,'player:human_male','main hero renders a production player token')
equal(heroActor._checker_token.scale,Style.scale(heroActor.size_category,64),'player token shares the board-piece diameter')
equal(heroActor._checker_token.overlay_active,true,'player token uses the tactical overlay layer')
equal(Style.relation(heroActor,heroActor,0),'player','player ring comes from the viewer relation')
local heroClone=heroActor:cloneActor()
equal(heroClone._checker_token,nil,'player clone drops the token state')
equal(heroClone._checker_player_rebuild,true,'player clone marks its copied doll stale')
local before=dollRebuilds[heroClone] or 0
-- The native paper doll chains its add_mos layers; accept that for the clone.
moMethods.chain=moMethods.chain or function() end
render(heroClone)
equal(heroClone._checker_token,nil,'player clone is not the main hero')
equal((dollRebuilds[heroClone] or 0)-before,1,'player clone rebuilds its paper doll once')
equal(heroActor._checker_token.id,'player:human_male','parent keeps its player token')
game.party=nil;PlayerTokens.available.human_male=nil
print(('clone_display: %d checks passed; native clones/motion/facing, owned overlay lift, scaled fallback centers, saved facing and native restoration'):format(checks))
