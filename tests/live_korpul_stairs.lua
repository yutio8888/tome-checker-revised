-- EXPLICIT DISPOSABLE OFFLINE FIXTURE ONLY. Never load in a normal campaign.
-- Mount/copy as /checker-live-korpul-stairs.lua after a cold runtime start.
-- sc=dofile('/checker-live-korpul-scene.lua'); st=dofile('/checker-live-korpul-stairs.lua')
-- For EACH layout DEFAULT/HIDEOUT, use a fresh sc.enter(layout, seed), then:
--   st.audit(); st.contracts(); st.stage('UP_WILDERNESS') -- L1 capture
--   st.travel('DOWN'); st.arrive(); st.audit(); st.contracts()
--   st.stage('UP'); st.stage('DOWN') -- separate L2 captures
--   st.travel('DOWN'); st.arrive(); st.audit(); st.stage('UP') -- L3 return capture
--   st.travel('UP'); st.arrive(); st.travel('UP'); st.arrive()
--   st.travel('UP_WILDERNESS'); st.arrive() -- MUST reach wilderness level 1
-- Pause at each command boundary for dialogs/loading; no busy loops. travel()
-- calls the real CHANGE_LEVEL keybind. arrive() checks actual resulting state.
-- stage() force-positions the hero next to a real native stair for capture;
-- it never changes the native stair. Frozen AI and forced movement are fixture
-- arrangements, not natural movement/combat coverage. Level 3 bosses stay native.
-- Real FOV memory capture (same level, no turns):
--   st.auditUnknown() -- run immediately after fresh entry, BEFORE staging exits
--   st.mode('refined'); st.stage('UP'); st.stageRemembered('UP')
--   -- capture remembered refined; optionally st.mode('vanilla') and capture
--   st.mode('refined'); st.checkRemembered(); st.restoreRemembered()
-- stageRemembered saves sight/position/mode and leaves the hero on safe floor
-- with sight=1 until restoreRemembered. Never writes map visibility flags.
-- Repeat for DOWN / UP_WILDERNESS where present. Zero unknown exits means
-- SKIP unknown evidence, not PASS; auditUnknown never manufactures unknown cells.
local Map=require 'engine.Map'
local Entity=require 'engine.Entity'
local T=require 'mod.class.CheckerTerrain'
local M={}
local expected={UP={kind='stairs-up',delta=-1},DOWN={kind='stairs-down',delta=1},UP_WILDERNESS={kind='stairs-world',delta=1,zone='wilderness'}}
local function guard(korpul)
 assert(config.settings.cheat and config.settings.disable_all_connectivity and profile and not profile.auth,'offline cheat fixture required')
 assert(__module_extra_info and __module_extra_info.checker_demo and game and game.checker_staged,'staged disposable fixture required')
 assert(game and game.zone and game.level and game.level.map and game.player,'loaded fixture map required')
 assert(game.player==game.checker_hero,'fixture hero required')
 if korpul then assert(T.variant(game.zone),'KorPul required');assert(T.stairsReady(),'cold-loaded reviewed stair assets required') end
end
local function report(s)
 print('[KorPulStairs]',s)
 local f=assert(fs.open('/korpul-stairs-results.txt','a'));f:write(s..'\n');f:close()
end
local function copy(v)
 if type(v)~='table' then return v end
 local out={};for k,x in pairs(v) do out[k]=copy(x) end;return out
end
local function pure(v)
 if type(v)~='table' then assert(type(v)~='function' and type(v)~='userdata');return end
 assert(not v.__CLASSNAME,'runtime Entity in remembered record')
 for _,x in pairs(v) do pure(x) end
end
local function cells()
 local out={}
 local m=game.level.map
 for x=0,m.w-1 do for y=0,m.h-1 do
  local g=m(x,y,Map.TERRAIN)
  if g and (g.change_level or g.change_zone) then out[#out+1]={x=x,y=y,g=g} end
 end end
 return out
end
local function find(id)
 local found
 for _,c in ipairs(cells()) do if c.g.define_as==id then assert(not found,'ambiguous native stair '..id);found=c end end
 return assert(found,'native stair absent: '..id)
end
local function freeze()
 for _,a in pairs(game.level.entities) do if a.ai and a~=game.player then a.never_act=true end end
 game.paused=true
end
local function refresh()
 -- Paused fixture movement skips the normal map/FOV dirty cycle. Ask
 -- native cleanFOV to clear old visibility before playerFOV recomputes it.
 -- Its sight computeFOV uses force=true, so fov_computed needs no override.
 game.level.map.clean_fov=true
 game.player:playerFOV();game.level.map.smooth_scroll=0
 game.level.map:centerViewAround(game.player.x,game.player.y)
 game:checkerApplySettings();game.level.map:redisplay();game.paused=true
end
function M.mode(mode)
 guard(true);assert(mode=='refined' or mode=='vanilla' or mode=='blockout')
 -- Same runtime setting and refresh route, without persisting fixture preference.
 config.settings.tome.checker_terrain_mode=mode;refresh()
end
function M.audit()
 guard(true)
 local layout,level=T.variant(game.zone),game.level.level
 assert(level>=1 and level<=3)
 local counts={}
 local path='/korpul-stairs-'..layout:lower()..'-'..level..'.tsv'
 local f=assert(fs.open(path,'w'))
 f:write('layout\tlevel\tx\ty\tdefine_as\tclassify\tdelta\tzone\ttarget_level\tvisible\tremembered\tnative_image\tnative_overlay\tboard_floor\tboard_overlay\n')
 for _,c in ipairs(cells()) do
  local g,e=c.g,expected[c.g.define_as]
  if e then
   assert(T.classify(g)==e.kind,'native generated stair violates exact source/rule/layer contract: '..tostring(g.define_as))
   assert(g.change_level==e.delta and g.change_zone==e.zone,'native destination mismatch')
   counts[g.define_as]=(counts[g.define_as] or 0)+1
  end
  local d=T.render(game.level.map,c.x,c.y,g,'refined')
  local vals={layout,level,c.x,c.y,g.define_as or '',T.classify(g) or 'native',g.change_level or '',g.change_zone or '',(g.change_zone or g.change_level_abs) and g.change_level or level+(g.change_level or 0),tostring(T.visible(game.level.map,c.x,c.y)),tostring(game.level.map.remembers(c.x,c.y)),g.image or '',g.add_mos and g.add_mos[1] and g.add_mos[1].image or '',d and d.image or '',d and d.add_mos and d.add_mos[1].image or ''}
  for i,v in ipairs(vals) do vals[i]=tostring(v):gsub('[\t\r\n]',' ') end
  f:write(table.concat(vals,'\t')..'\n')
 end
 f:close()
 assert((counts.UP_WILDERNESS or 0)==(level==1 and 1 or 0),'world exit must exist only on level 1')
 assert((counts.UP or 0)==(level>1 and 1 or 0),'ordinary return stairs mismatch')
 assert((counts.DOWN or 0)==(level<3 and 1 or 0),'level 3 must not gain a fourth-level stair')
 report(layout..' L'..level..' PASS natural generated stair identities and rule destinations '..path..' (field audit; not transition evidence)')
 M.auditUnknown()
 return path
end
-- Inspect actual native FOV/remember state. In KorPul all_remembered and prior
-- exploration may mean there are no genuinely unknown exits in this instance.
function M.auditUnknown()
 guard(true)
 local m=game.level.map
 local checked,external=0,0
 for _,c in ipairs(cells()) do
  if not T.visible(m,c.x,c.y) and not m.remembers(c.x,c.y) then
   local key=c.x+c.y*m.w
   local before=m._checker_korpul and m._checker_korpul[key]
   local d=T.render(m,c.x,c.y,c.g,'refined')
   assert(not d or (d.image=='invis.png' and not d.add_mos and not d.add_displays and not d.display_on_seen and not d.display_on_remember and not d.display_on_unknown),'actual unknown exit exposes content')
   assert((m._checker_korpul and m._checker_korpul[key])==before,'unknown rendering creates knowledge')
   if c.g.replace_display then external=external+1 else checked=checked+1 end
   report(T.variant(game.zone)..' L'..game.level.level..' UNKNOWN '..tostring(c.g.define_as)..' at '..c.x..','..c.y..' seen='..tostring(m.seens(c.x,c.y))..' infov='..tostring(m.infovs(c.x,c.y))..' remember='..tostring(m.remembers(c.x,c.y))..' render='..tostring(d and d.image)..(c.g.replace_display and ' EXTERNAL ownership only' or ' PASS no content'))
  end
 end
 report(T.variant(game.zone)..' L'..game.level.level..' '..(checked>0 and 'PASS' or 'SKIP')..' actual unknown exits checked='..checked..' external='..external..' (no visibility flags changed)')
 return checked,external
end
function M.contracts()
 guard(true)
 local m={w=3,h=3};local visible,remember=true,true
 m.seens=function() return visible end;m.infovs=function() return visible end;m.remembers=function() return remember end
 local floor=assert(game.zone.grid_list.FLOOR)
 local savedMode=config.settings.tome.checker_terrain_mode
 local p=game.player;local turn,life,energy,x,y=game.turn,p.life,p.energy.value,p.x,p.y
 local ok,err=xpcall(function()
  for id,e in pairs(expected) do
   local g=assert(game.zone.grid_list[id])
   assert(T.classify(g)==e.kind,'cold loadList stamp absent '..id)
   local delta,zone,overlay=g.change_level,g.change_zone,g.add_mos
   m._checker_korpul=nil;visible=true;remember=true;T.observe(m,1,1,g)
   M.mode('refined')
   local d=assert(T.render(m,1,1,g,'refined'))
   assert(d.image==T.assetPath('floor',nil,0,0,1,1),'floor composition')
   assert(d.add_mos and d.add_mos[1].image=='checker-revised+refined/korpul/'..e.kind..'.png','foreground identity')
   -- Build actual engine MOs, not merely a path string.
   local mos={};d:getMapObjects(Map.tiles,mos,1);assert(d._mo,'native MO construction failed')
   visible=false;T.observe(m,1,1,floor)
   assert(T.render(m,1,1,floor,'refined')==d,'hidden replacement revealed')
   M.mode('vanilla')
   local native=assert(T.render(m,1,1,floor,'vanilla'))
   assert(native.image==g.image and native.add_mos[1].image==g.add_mos[1].image,'native remembered layers lost')
   local nmos={};native:getMapObjects(Map.tiles,nmos,1)
   M.mode('blockout');assert(T.render(m,1,1,g,'blockout')==native)
   M.mode('refined');assert(T.render(m,1,1,g,'refined')==d)
   local record=copy(m._checker_korpul[4]);pure(record)
   local restored={w=3,h=3,seens=m.seens,infovs=m.infovs,remembers=m.remembers,_checker_korpul={[4]=record}}
   local rd=assert(T.render(restored,1,1,floor,'refined'))
   assert(rd~=d and rd.add_mos[1].image==d.add_mos[1].image,'remembered cache reconstruction failed')
   local foreign=g:cloneFull();foreign.replace_display=Entity.new{image='invis.png'}
   assert(T.render(m,1,1,foreign,'refined')==nil,'external display overridden')
   remember=false
   local blank=assert(T.render(m,1,1,g,'refined'))
   assert(blank.image=='invis.png' and not blank.display_on_unknown and not blank.display_on_remember,'unknown stair disclosed')
   assert(T.render(m,1,1,floor,'refined')==blank,'unknown content depends on hidden identity')
   visible=true;remember=true;T.observe(m,1,1,floor)
   assert(not T.render(m,1,1,floor,'refined').add_mos,'re-observed plain floor retains stale stairs')
   assert(g.change_level==delta and g.change_zone==zone and g.add_mos==overlay and not g.replace_display,'renderer mutated rule Grid')
   report(T.variant(game.zone)..' PASS '..id..' live MO + visible/remembered/unknown + vanilla/blockout/refined + external display + pure cache reconstruction')
  end
 end,debug.traceback)
 config.settings.tome.checker_terrain_mode=savedMode;refresh()
 assert(game.turn==turn and p.life==life and p.energy.value==energy and p.x==x and p.y==y,'contract check altered hero state')
 if not ok then report('CONTRACT FAIL '..err);error(err,0) end
 return true
end
function M.stage(id)
 guard(true);assert(expected[id]);assert(not M.remembered,'restoreRemembered before restaging');freeze()
 local c=find(id);local m,p=game.level.map,game.player
 local px,py
 for _,d in ipairs{{0,1},{1,0},{-1,0},{0,-1},{1,1},{-1,1},{1,-1},{-1,-1}} do
  local x,y=c.x+d[1],c.y+d[2]
  if not px and m:isBound(x,y) and (not m(x,y,Map.ACTOR) or m(x,y,Map.ACTOR)==p) and not m(x,y,Map.TRAP) and not m:checkEntity(x,y,Map.TERRAIN,'block_move',p) then px,py=x,y end
 end
 assert(px,'no empty passable neighbor for stair capture')
 p:move(px,py,true);refresh()
 assert(T.visible(m,c.x,c.y),'stair is not naturally observed from stage position')
 local d=assert(T.render(m,c.x,c.y,c.g,'refined'))
 assert(d.add_mos and d.add_mos[1].image=='checker-revised+refined/korpul/'..expected[id].kind..'.png','staged foreground absent')
 report(T.variant(game.zone)..' L'..game.level.level..' STAGE '..id..' at '..c.x..','..c.y..' hero '..p.x..','..p.y)
 return c.x,c.y
end
function M.checkRemembered()
 guard(true)
 local job=assert(M.remembered,'stageRemembered first')
 assert(game.level==job.level and game.level.map==job.map,'remembered capture must stay on its original level')
 local m=job.map
 assert(m(job.cx,job.cy,Map.TERRAIN)==job.grid,'native target Grid changed during capture')
 assert(not T.visible(m,job.cx,job.cy) and not m.infovs(job.cx,job.cy),'target has not left actual terrain FOV')
 assert(m.remembers(job.cx,job.cy),'native FOV failed to retain target memory')
 local d=assert(T.render(m,job.cx,job.cy,job.grid,'refined'),'remembered board display missing')
 assert(d.image==job.floor and d.add_mos and d.add_mos[1].image==job.overlay,'remembered foreground differs from observed stair')
 assert(game.turn==job.turn and game.player.life==job.life and game.player.energy.value==job.energy,'remembered capture advanced turn/life/energy')
 report(T.variant(game.zone)..' L'..game.level.level..' REMEMBERED PASS '..job.id..' at '..job.cx..','..job.cy..' hero='..game.player.x..','..game.player.y..' sight='..tostring(game.player.sight)..' seen='..tostring(m.seens(job.cx,job.cy))..' infov='..tostring(m.infovs(job.cx,job.cy))..' remember='..tostring(m.remembers(job.cx,job.cy))..' foreground='..job.overlay..' (real playerFOV; no flag writes)')
 return job.cx,job.cy
end
function M.restoreRemembered()
 guard(true)
 local job=assert(M.remembered,'no remembered capture to restore')
 assert(game.level==job.level and game.level.map==job.map,'restore before leaving the original level')
 local p=game.player
 assert(not job.map(job.x,job.y,Map.ACTOR) or job.map(job.x,job.y,Map.ACTOR)==p,'original hero cell became occupied')
 p.sight=job.sight
 config.settings.tome.checker_terrain_mode=job.mode
 p:move(job.x,job.y,true);refresh()
 assert(p.x==job.x and p.y==job.y and p.sight==job.sight,'hero sight/position restoration failed')
 assert(game.turn==job.turn and p.life==job.life and p.energy.value==job.energy,'capture changed turn/life/energy')
 M.remembered=nil
 report(T.variant(game.zone)..' L'..game.level.level..' RESTORE PASS '..job.id..' hero='..p.x..','..p.y..' sight='..tostring(p.sight))
 return true
end
function M.stageRemembered(id)
 guard(true);assert(expected[id]);assert(not M.remembered,'restoreRemembered before another memory capture');assert(not M.pending,'finish pending travel first')
 local c=find(id);local m,p=game.level.map,game.player
 assert(T.visible(m,c.x,c.y),'call stage(id) to naturally observe this stair first')
 assert(not p:attr('blind') and not p:attr('omnivision'),'ordinary sight required for controlled memory capture')
 local d=assert(T.render(m,c.x,c.y,c.g,'refined'))
 assert(d.add_mos and d.add_mos[1].image=='checker-revised+refined/korpul/'..expected[id].kind..'.png','observed stair foreground missing')
 local candidates={}
 for x=math.max(0,c.x-8),math.min(m.w-1,c.x+8) do for y=math.max(0,c.y-6),math.min(m.h-1,c.y+6) do
  local g=m(x,y,Map.TERRAIN);local distance=math.max(math.abs(x-c.x),math.abs(y-c.y))
  if distance>=4 and T.classify(g)=='floor' and not g.change_level and not g.change_zone and not m(x,y,Map.ACTOR) and not m(x,y,Map.OBJECT) and not m(x,y,Map.TRAP) and not m(x,y,Map.TRIGGER) and not m.attrs(x,y,'vault_id') and not m:checkEntity(x,y,Map.TERRAIN,'block_move',p) then
   candidates[#candidates+1]={x=x,y=y,distance=distance}
  end
 end end
 assert(#candidates>0,'no safe native floor within capture range; choose another stair/fixture')
 table.sort(candidates,function(a,b) if a.distance~=b.distance then return a.distance<b.distance end;if a.x~=b.x then return a.x<b.x end;return a.y<b.y end)
 M.remembered={id=id,level=game.level,map=m,grid=c.g,cx=c.x,cy=c.y,x=p.x,y=p.y,sight=p.sight,mode=config.settings.tome.checker_terrain_mode,turn=game.turn,life=p.life,energy=p.energy.value,floor=d.image,overlay=d.add_mos[1].image}
 freeze()
 local ok,err=xpcall(function()
  p.sight=1;config.settings.tome.checker_terrain_mode='refined'
  local hidden=false
  for _,candidate in ipairs(candidates) do
   p:move(candidate.x,candidate.y,true);refresh()
   if not T.visible(m,c.x,c.y) and not m.infovs(c.x,c.y) then hidden=true;break end
  end
  assert(hidden,'native FOV still observes the target; inspect perception effects')
  M.checkRemembered()
 end,debug.traceback)
 if not ok then
  local restored,restoreErr=pcall(M.restoreRemembered)
  if not restored then err=err..'\nRESTORE FAILED: '..tostring(restoreErr)..'; remembered job retained for inspection' end
  error(err,0)
 end
 return c.x,c.y
end
function M.travel(id)
 guard(true);assert(not M.remembered,'restoreRemembered before leaving this level');assert(not M.pending,'call arrive before another departure');assert(expected[id]);freeze()
 local c=find(id);local p,m=game.player,game.level.map
 assert(T.classify(c.g)==expected[id].kind,'only exact native stairs may be tested')
 assert(not m(c.x,c.y,Map.ACTOR) or m(c.x,c.y,Map.ACTOR)==p,'stair occupied')
 assert(not p:attr('never_move'),'hero cannot leave level')
 assert(p:enoughEnergy(),'hero needs native action energy; do not bypass the keybind gate')
 if c.g.change_zone then
  for eff in pairs(p.tmp) do local e=p.tempeffect_def[eff];assert(e.status~='detrimental' or e.no_stop_enter_worlmap,'native detrimental effect blocks world travel') end
 end
 p:move(c.x,c.y,true);refresh()
 local layout,level=T.variant(game.zone),game.level.level
 local targetZone=c.g.change_zone or game.zone.short_name
 local targetLevel=c.g.change_zone and c.g.change_level or level+c.g.change_level
 M.pending={layout=layout,from=level,id=id,zone=targetZone,level=targetLevel,oldlevel=game.level}
 report(layout..' L'..level..' DEPART '..id..' expected '..targetZone..':'..targetLevel..' via native CHANGE_LEVEL')
 game.key:triggerVirtual('CHANGE_LEVEL')
 game.paused=true
 -- Do not silently call game:changeLevel if a native guard/dialog blocks travel.
 return targetZone,targetLevel
end
function M.arrive()
 guard(false);local job=assert(M.pending,'no native departure pending')
 assert(game.level~=job.oldlevel,'native CHANGE_LEVEL has not changed level; inspect pending dialogs/guards')
 assert(game.zone.short_name==job.zone and game.level.level==job.level,'wrong real transition destination')
 if job.zone=='ruins-kor-pul' then assert(T.variant(game.zone)==job.layout,'variant changed during native transition') end
 freeze();refresh()
 report(job.layout..' L'..job.from..' '..job.id..' PASS actual native CHANGE_LEVEL arrived '..game.zone.short_name..':'..game.level.level)
 M.pending=nil
 return true
end
return M
