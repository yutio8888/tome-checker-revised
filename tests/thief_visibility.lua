-- Native canSee/cache with the real token overlay callback. No game or saves.
local script=debug.getinfo(1,'S').source:sub(2)
local root=(script:match('^(.*[/\\])') or './')..'../'
local checks,draws,rolls=0,0,0
local function eq(a,b,label) checks=checks+1;assert(a==b,label..': '..tostring(a)..' ~= '..tostring(b)) end
local function read(path) local f=assert(io.open(path));local s=f:read('*a');f:close();return s end
local function compile(s,env)
 if setfenv then local f=assert(loadstring(s));setfenv(f,env);return f() end
 return assert(load(s,'test','t',env))()
end
local native={}
local source=read(root..'../../modules/tome/class/Actor.lua')
local start=assert(source:find('function _M:canSeeNoCache(',1,true))
local stop=assert(source:find('--- Reset the cache of everything else',start,true))
local detection=false
compile(source:sub(start,stop-1),setmetatable({_M=native,rng={percent=function() rolls=rolls+1;return detection end}},{__index=_G}))
local viewer=setmetatable({player=true,esp={},level=1},{__index=native})
function viewer:attr(k) return self[k] end
function viewer:knowTalent() return false end
function viewer:combatSeeStealth() return 1 end
function viewer:checkHitOld() return detection,50 end
function viewer:reactionToward() return -1 end
local map={actor_player=viewer,view_faction='players',tile_w=64,tiles={get=function()
 return {toScreenFull=function() draws=draws+1 end},64,64
end}}
local style=dofile(root..'overload/mod/class/CheckerTokenStyle.lua')
local Entity={new=function(t)
 function t:makeMapObject() self._mo=self._mo or {displayCallback=function(m,f) m.callback=f end};return self._mo end
 return t
end}
local base={getMapObjects=function(a,tiles,mos,z) mos[z]=a._mo end,
 MOflipX=function(a,v) a._flipx=v;a._mo:flipX(v) end}
local env=setmetatable({loadPrevious=function() return base end,game={level={map=map},always_target=true},
 require=function(n)
  if n=='engine.Entity' then return Entity end
  if n=='mod.class.CheckerTokenStyle' then return style end
  if n=='mod.class.CheckerOptions' then return dofile(root..'overload/mod/class/CheckerOptions.lua') end
  if n=='engine.Faction' then return {factionReaction=function() return -1 end} end
  error(n)
 end},{__index=_G})
local Actor=compile(read(root..'superload/mod/class/Actor.lua'),env)
local body={onSeen=function(self,v) self.seen=v end,flipX=function() end}
local display={}
local a=setmetatable({name='rogue',type='humanoid',subtype='human',__is_actor=true,stealth=20,
 faction='enemies',life=100,max_life=100,rank=4,size_category=3,_mo=body,replace_display=display,
 _checker_token={id='rogue',display=display,scale=style.scale(3,64)},attr=function(self,k) return self[k] end},{__index=Actor})
local mos={};a:getMapObjects(map.tiles,mos,10)
local overlay=assert(mos[11]);eq(a._checker_token.overlay_active,true,'real overlay installed')
local function draw() local before=draws;overlay.callback(0,0,64,64,1,true,0,0);return draws-before end
-- First establish visible cached body/overlay, then change native detection
-- without rebuilding map objects: canSee only sends onSeen to the body MO.
detection=true;eq(viewer:canSee(a),true,'native detection succeeds')
eq(draw()>0,true,'visible token gets tactical UI')
local oldrolls=rolls;draw();eq(rolls,oldrolls,'overlay reuses native cached detection')
detection=false;viewer:resetCanSeeCache();eq(viewer:canSee(a),false,'native detection fails')
eq(body.seen,false,'native body onSeen false')
eq(a._checker_token.overlay._mo,overlay,'independent overlay is still cached')
eq(draw(),0,'stale overlay cannot leak life faction rank or shield')
-- A sensed tile is not an identity grant. Neither tile-FOV API is consulted.
map.seens=function() return .6 end;map.infovs=function() return false end
viewer.detect_actor=true;viewer.detect_range=10
eq(draw(),0,'detect_actor sensed tile does not bypass failed native canSee')
viewer.detect_actor=nil;viewer.detect_range=nil
-- Native ESP identifies actors even outside terrain FOV. Do not suppress it.
viewer.esp.humanoid=1;viewer:resetCanSeeCache()
local seen,chance=viewer:canSee(a);eq(seen,true,'native ESP sees stealth');eq(chance,100,'ESP chance')
eq(draw()>0,true,'ESP actor UI survives absent terrain FOV')
viewer.esp={};viewer:resetCanSeeCache();eq(draw(),0,'removing ESP restores hidden state')
-- Detection success is boolean, not a chance threshold.
detection=true;viewer:resetCanSeeCache();seen,chance=viewer:canSee(a)
eq(chance,50,'partial detection chance');eq(draw()>0,true,'successful partial-chance detection draws')
-- No viewer is the native Map spectator branch. Dead/god are not extra gates.
map.actor_player=nil;eq(draw()>0,true,'no-viewer spectator keeps native branch')
map.actor_player=viewer;viewer.dead=true;viewer.god=true
eq(draw()>0,true,'dead/god flags do not override native successful detection')
detection=false;viewer:resetCanSeeCache();eq(draw(),0,'dead/god flags do not invent native detection')
eq(a.stealth,20,'renderer never changes stealth')
eq(a.life,100,'renderer never changes life')
print(('thief_visibility: %d checks; native cached canSee, stale overlay, sense/ESP, spectator and detection semantics passed'):format(checks))
