-- EXPLICIT OFFLINE FIXTURE ONLY. Mutates/restores one clear 3x3 patch.
-- Local test: audit=dofile('/checker-live-korpul-terrain.lua'); audit.run('DEFAULT')
-- Native ZIP round trip: audit.begin(); later audit.finish() (do not busy wait).
local Map=require 'engine.Map'
local Entity=require 'engine.Entity'
local Terrain=require 'mod.class.CheckerTerrain'
local DamageType=require 'engine.DamageType'
local Savefile=require 'engine.Savefile'
local M={}
local function guard(layout)
 assert(config.settings.cheat and config.settings.disable_all_connectivity and profile and not profile.auth,'offline cheat fixture required')
 assert(__module_extra_info and __module_extra_info.checker_demo and game.checker_staged,'explicit staged checker fixture required')
 local actual=assert(Terrain.variant(game.zone),'KorPul required')
 assert(not layout or actual==layout,'layout mismatch')
 assert(Terrain.ready(),'reviewed actual terrain exports must be ready')
 return actual
end
local function copy(t)
 if type(t)~='table' then return t end
 local out={};for k,v in pairs(t) do out[k]=copy(v) end;return out
end
local function plain(t)
 for k,v in pairs(t) do
  assert(type(v)~='function' and type(v)~='userdata','nonserializable knowledge value '..tostring(k))
  if type(v)=='table' then assert(not v.__CLASSNAME,'Entity leaked into knowledge');plain(v) end
 end
end
local function report(text)
 print('[KorPulTerrain]',text)
 local f=assert(fs.open('/korpul-terrain-results.txt','a'));f:write(text..'\n');f:close()
end
local function image(m,x,y,g,mode)
 local display=Terrain.render(m,x,y,g,mode or 'refined')
 return display and display.image,display
end
function M.run(layout)
 layout=guard(layout)
 local m,p=game.level.map,game.player
 local turn,px,py,life,energy=game.turn,p.x,p.y,p.life,p.energy.value
 local x,y
 for i=2,m.w-3 do for j=2,m.h-3 do
  if not x and m.seens(i,j) and m.infovs(i,j) then
   local clear=true
   for dx=-1,1 do for dy=-1,1 do
    if m(i+dx,j+dy,Map.ACTOR) or m(i+dx,j+dy,Map.OBJECT) or m(i+dx,j+dy,Map.TRAP) or m(i+dx,j+dy,Map.TRIGGER) then clear=false end
   end end
   if clear then x,y=i,j end
  end
 end end
 assert(x,'need a visible clear 3x3 fixture patch')
 local key=x+y*m.w
 local original={}
 for dx=-1,1 do for dy=-1,1 do
  local a,b=x+dx,y+dy;original[#original+1]={x=a,y=b,grid=m(a,b,Map.TERRAIN),seen=m.seens(a,b),fov=m.infovs(a,b),remember=m.remembers(a,b),lite=m.lites(a,b)}
 end end
 local oldRecords=m._checker_korpul
 m._checker_korpul=oldRecords and copy(oldRecords) or {}
 local previousMode=config.settings.tome.checker_terrain_mode
 config.settings.tome.checker_terrain_mode='refined'
 local function visible(v)
  m.seens(x,y,v);m.infovs(x,y,v);m.remembers(x,y,true)
 end
 local checks={}
 local function pass(s) checks[#checks+1]=s end
 local ok,err=xpcall(function()
  local closed=assert(game.zone.grid_list.DOOR):cloneFull()
  local opened=assert(game.zone.grid_list.DOOR_OPEN)
  assert(Terrain.classify(closed)=='door-closed','live loadList provenance missing for DOOR')
  local wall=assert(game.zone.grid_list.WALL):cloneFull()
  assert(Terrain.classify(wall)=='wall','live loadList provenance missing for WALL')
  assert(Terrain.classify(game.zone.grid_list.HARDWALL)=='hardwall','HARDWALL contract')
  visible(true);m(x,y,Map.TERRAIN,closed)
  local closedImage=assert(image(m,x,y,closed),'missing reviewed closed-door export')
  assert(closedImage:find('checker%-revised%+refined/korpul/door%-closed'),closedImage)
  local ruleTarget,ruleSight=closed.door_opened,closed.block_sight
  local mover={open_door=true}
  assert(closed:block_move(x,y,mover,false)==true,'closed native door must block non-action movement')
  assert(closed:block_move(x,y,mover,true)==true,'native opening must consume the movement attempt')
  assert(m(x,y,Map.TERRAIN)==opened,'native open target changed')
  assert(closed.door_opened==ruleTarget and closed.block_sight==ruleSight and not closed.replace_display,'render altered closed rules')
  assert(not opened:block_move(x,y,mover,false) and not opened.block_sight,'open door movement/sight rule changed')
  assert(image(m,x,y,opened):find('door%-open'),'visible opening did not update locally')
  pass('native Grid:block_move gate and open target/sight preserved (no claim of full actor energy-loop test)')

  m(x,y,Map.TERRAIN,closed);closedImage=assert(image(m,x,y,closed))
  visible(false);m(x,y,Map.TERRAIN,opened)
  assert(image(m,x,y,opened)==closedImage,'unseen replacement leaked')
  assert(image(m,x,y,opened,'vanilla')==closed.image,'native-mode restore leaked current hidden grid')
  m(x,y,Map.TERRAIN,closed)
  closed.door_opened=nil;closed.block_sight=false;closed.image=opened.image
  m:updateMap(x,y)
  assert(image(m,x,y,closed)==closedImage,'unseen in-place mutation leaked')
  closed.door_opened=ruleTarget;closed.block_sight=ruleSight;closed.image='terrain/granite_door1.png'
  m(x,y,Map.TERRAIN,opened);visible(true);m:updateMap(x,y)
  assert(image(m,x,y,opened):find('door%-open'),'re-observation failed')
  local foreign=opened:cloneFull();foreign.replace_display=Entity.new{image=closed.image}
  m(x,y,Map.TERRAIN,foreign)
  assert(not image(m,x,y,foreign),'foreign display swallowed')
  assert(foreign.replace_display.image==closed.image,'foreign pointer changed')
  pass('hidden replacement, same-object mutation, native restore, re-observation and external ownership')

  m(x,y,Map.TERRAIN,wall)
  local digger=p:cloneFull();digger.turn_procs={};digger.dug_times=0
  DamageType:get(DamageType.DIG).projector(digger,x,y,DamageType.DIG,1)
  local dug=m(x,y,Map.TERRAIN)
  assert(dug~=wall and not dug:check('block_move',x,y,mover),'native DIG did not create passable terrain')
  assert(not dug.block_sight and digger.dug_times==1 and digger.turn_procs.has_dug==1,'native DIG accounting/sight changed')
  assert(wall.dig=='FLOOR' and wall.can_pass.pass_wall==1 and wall.block_sight==true and not wall.replace_display,'wall rules changed')
  -- Nice-editor floor decorations may deliberately fall back to native.
  pass('native DamageType.DIG + nice_tile update retained passability, sight and dug counters')

  m(x,y,Map.TERRAIN,closed);visible(true);m:updateMap(x,y)
  local before=assert(image(m,x,y,closed))
  local record=assert(m._checker_korpul[key]);plain(record)
  M.sample=Entity.new{checker_record=copy(record),checker_grid=closed:cloneFull()}
  M.sample.checker_grid.__SAVEINSTEAD=nil
  local clone=M.sample:cloneFull()
  assert(clone.checker_record~=M.sample.checker_record and clone.checker_record.native~=M.sample.checker_record.native,'native clone shares records')
  local cm={w=m.w,h=m.h,seens=function() return false end,infovs=function() return false end,_checker_korpul={[key]=clone.checker_record}}
  local _,a=image(m,x,y,closed);local ci,b=image(cm,x,y,clone.checker_grid)
  assert(ci==before and a~=b,'native clone shares display cache or loses remembered tile')
  M.sample_key,M.sample_w,M.sample_h=key,m.w,m.h
  pass('native cloneFull separates knowledge and rendering caches; pure record prepared for ZIP')
 end,debug.traceback)
 config.settings.tome.checker_terrain_mode=previousMode
 -- Prevent observations during restoration from rewriting the original snapshot.
 for _,c in ipairs(original) do m.seens(c.x,c.y,false);m.infovs(c.x,c.y,false) end
 for _,c in ipairs(original) do m(c.x,c.y,Map.TERRAIN,c.grid) end
 m._checker_korpul=oldRecords
 for _,c in ipairs(original) do
  m.seens(c.x,c.y,c.seen or false);m.infovs(c.x,c.y,c.fov or false)
  m.remembers(c.x,c.y,c.remember or false);m.lites(c.x,c.y,c.lite or false)
 end
 m:redisplay();game.paused=true
 assert(game.turn==turn and p.x==px and p.y==py and p.life==life and p.energy.value==energy,'test changed player turn/position/life/energy')
 if not ok then report(layout..' FAIL '..err);error(err,0) end
 for _,row in ipairs(checks) do report(layout..' PASS '..row) end
 return true
end
-- Real keyboard-path actor movement, measured against the native mode.
-- This version opens an ordinary door for zero energy, then pays to enter it.
function M.actorDoor(layout)
 layout=guard(layout)
 local p,m=game.player,game.level.map
 assert(p==game.checker_hero and p.open_door and not p.dead,'staged real player with native open_door required')
 assert(not util.isHex(),'square-grid fixture required')
 for _,key in ipairs{'confused','sleep','encased_in_ice','encased','prob_travel','never_move','free_movement','move_stamina_instead_of_energy','walk_sun_path'} do
  assert(not p:attr(key),'movement modifier prevents controlled audit: '..key)
 end
 assert(not next(p.tmp or {}),'run actorDoor with no temporary player effects')
 local px,py=p.x,p.y
 local tx,ty,dir
 for _,d in ipairs{{6,1,0},{4,-1,0},{2,0,1},{8,0,-1}} do
  local a,b=px+d[2],py+d[3]
  if not tx and m:isBound(a,b) and not m(a,b,Map.ACTOR) and not m(a,b,Map.OBJECT) and not m(a,b,Map.TRAP) and not m(a,b,Map.TRIGGER) and not m.attrs(a,b,'vault_id') then tx,ty,dir=a,b,d[1] end
 end
 assert(tx,'need an empty cardinal neighbor beside the real player')
 local original=m(tx,ty,Map.TERRAIN)
 local oldRecords=m._checker_korpul
 local oldMode=config.settings.tome.checker_terrain_mode
 local oldEnergy=copy(p.energy)
 local oldTurn,oldLife,oldPaused=game.turn,p.life,game.paused
 local oldView={m.mx,m.my}
 local oldWalked=m.attrs(tx,ty,'walked')
 local oldFlags={}
 for _,key in ipairs{'old_x','old_y','move_dir','did_energy','doPlayerSlide','zig_zag'} do oldFlags[key]=p[key] end
 local seens,fovs,remembers=m.seens(tx,ty),m.infovs(tx,ty),m.remembers(tx,ty)
 local nativeMove=require('engine.Actor').move
 local rows={}
 local ok,err=xpcall(function()
  for _,mode in ipairs{'vanilla','refined'} do
   assert(p.x==px and p.y==py,'trial must start at original player cell')
   config.settings.tome.checker_terrain_mode=mode
   m._checker_korpul=oldRecords and copy(oldRecords) or {}
   m.seens(tx,ty,true);m.infovs(tx,ty,true);m.remembers(tx,ty,true)
   local closed=game.zone.grid_list.DOOR:cloneFull()
   m(tx,ty,Map.TERRAIN,closed)
   if mode=='refined' then assert(image(m,tx,ty,closed),'real closed-door export missing') end
   local expected=game.energy_to_act*p:combatMovementSpeed(tx,ty)
   assert(expected>0,'positive native movement cost required')
   p.energy.value=math.max(oldEnergy.value,expected*4+game.energy_to_act)
   p.energy.used=false;p.did_energy=nil
   local e0=p.energy.value
   local first=p:moveDir(dir)
   local e1=p.energy.value
   assert(first and p.x==px and p.y==py,'native first attempt must open without displacement')
   assert(m(tx,ty,Map.TERRAIN).door_closed=='DOOR','first moveDir did not open native DOOR')
   assert(e0-e1==0,'this native revision opens ordinary doors without energy debit')
   expected=game.energy_to_act*p:combatMovementSpeed(tx,ty)
   local second=p:moveDir(dir)
   local e2=p.energy.value
   assert(second and p.x==tx and p.y==ty,'second moveDir must enter opened door')
   assert(math.abs((e1-e2)-expected)<1e-7,'entry energy differs from native combatMovementSpeed cost')
   assert(game.turn==oldTurn and p.life==oldLife,'synchronous movement audit advanced world or changed life')
   rows[#rows+1]={mode=mode,opening=e0-e1,entry=e1-e2,expected=expected}
   nativeMove(p,px,py,true)
   p.energy.value=oldEnergy.value;p.energy.used=oldEnergy.used
   game.paused=true
  end
  assert(rows[1].opening==rows[2].opening and math.abs(rows[1].entry-rows[2].entry)<1e-7,'refined changed real player door movement cost')
 end,debug.traceback)
 -- Restore position via native forced movement, never direct x/y assignment.
 if p.x~=px or p.y~=py then nativeMove(p,px,py,true) end
 config.settings.tome.checker_terrain_mode=oldMode
 m.seens(tx,ty,false);m.infovs(tx,ty,false)
 m(tx,ty,Map.TERRAIN,original);m._checker_korpul=oldRecords
 m.seens(tx,ty,seens or false);m.infovs(tx,ty,fovs or false);m.remembers(tx,ty,remembers or false)
 m.attrs(tx,ty,'walked',oldWalked or false)
 for key in pairs(p.energy) do p.energy[key]=nil end;for key,value in pairs(oldEnergy) do p.energy[key]=value end
 for _,key in ipairs{'old_x','old_y','move_dir','did_energy','doPlayerSlide','zig_zag'} do p[key]=oldFlags[key] end
 m.mx,m.my=oldView[1],oldView[2];game.paused=oldPaused;m:redisplay()
 assert(game.turn==oldTurn and p.life==oldLife and p.x==px and p.y==py and p.energy.value==oldEnergy.value,'actorDoor cleanup failed')
 if not ok then report(layout..' ACTOR_DOOR FAIL '..err);error(err,0) end
 for _,r in ipairs(rows) do report(layout..' ACTOR_DOOR PASS '..r.mode..' first_move_displacement=0 opening_energy='..r.opening..' second_move_displacement=1 entry_energy='..r.entry..' expected_native_energy='..r.expected) end
 return rows
end
function M.begin()
 guard();assert(M.sample,'run the rule audit first');assert(not M.pending,'save already pending')
 assert(not savefile_pipe.saving and #savefile_pipe.pipe==0 and (not savefile_pipe.waiton or not next(savefile_pipe.waiton)),'wait for fixture save completion')
 local directory='/tmp/checker-korpul-terrain/'..os.time()..'-'..M.sample.uid..'/'
 fs.mkdir('/tmp');fs.mkdir('/tmp/checker-korpul-terrain');fs.mkdir(directory)
 local zip=directory..'terrain.teae'
 local previous,count=Savefile:getCurrent(),savefile_pipe.current_nb
 local writer
 local ok,err=xpcall(function()
  writer=Savefile.new('checker-korpul-terrain',false);writer.save_dir=directory
  assert(writer:saveObject(M.sample,zip..'.tmp')>=1,'serializer did not queue terrain object')
  core.serial.threadSave()
 end,debug.traceback)
 if writer then writer:close() end
 Savefile:setCurrent(previous);savefile_pipe.current_nb=count
 if not ok then error(err,0) end
 M.pending={source=M.sample,directory=directory,zip=zip}
 report('ZIP PENDING '..zip);return zip
end
function M.finish()
 guard();local job=assert(M.pending,'call begin first')
 local completed=core.serial.popSaveReturn();if not completed then return false,'ZIP still pending' end
 assert(completed==job.zip,'unexpected save completion '..tostring(completed))
 local previous,reader,mounted=Savefile:getCurrent()
 local ok,err=xpcall(function()
  reader=Savefile.new('checker-korpul-terrain',false);reader.save_dir=job.directory;reader.load_dir=job.directory..'mounted/'
  mounted=assert(fs.getRealPath(job.zip));fs.mount(mounted,reader.load_dir)
  local loaded=assert(reader:loadReal('main'))
  for _,e in ipairs(reader.delayLoad) do e:loaded() end
  assert(loaded~=job.source and loaded.checker_record~=job.source.checker_record,'serializer reused memory')
  plain(loaded.checker_record)
  assert(loaded.checker_record.file==job.source.checker_record.file and loaded.checker_record.signature==job.source.checker_record.signature,'saved knowledge changed')
  assert(Terrain.classify(loaded.checker_grid)=='door-closed','Grid provenance/rules lost in native ZIP')
  assert(not loaded.checker_grid.replace_display,'runtime display leaked into Grid save')
  local k=M.sample_key;local x,y=k%M.sample_w,math.floor(k/M.sample_w)
  local m={w=M.sample_w,h=M.sample_h,seens=function() return false end,infovs=function() return false end,_checker_korpul={[k]=loaded.checker_record}}
  assert(image(m,x,y,loaded.checker_grid)==job.source.checker_record.file,'deserialized hidden knowledge cannot rebuild display')
  assert(image(m,x,y,loaded.checker_grid,'vanilla')==job.source.checker_record.native.image,'deserialized native snapshot lost')
  M.loaded_sample=loaded
 end,debug.traceback)
 if mounted then fs.umount(mounted) end;if reader then reader:close() end;Savefile:setCurrent(previous);M.pending=nil
 if not ok then report('ZIP FAIL '..err);error(err,0) end
 report('ZIP PASS native serializer round trip: Grid provenance and pure remembered/native snapshots, fresh display cache')
 return true
end
return M
