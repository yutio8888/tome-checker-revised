-- Disposable offline instrumentation only; no production animation changes.
local Map=require 'engine.Map'
local M={}
local function write(name,s) local f=assert(fs.open('/motion-'..name,'w'));f:write(s);f:close() end
local function guard() assert(require('mod.class.CheckerFixture').enabled() and not profile.auth and config.settings.disable_all_connectivity);assert(game.player==game.checker_hero and game.paused) end
local function clear(x,y)
 local m=game.level.map;local g=m(x,y,Map.TERRAIN)
 return g and not g.change_level and not g.change_zone and not g.door_opened and not m:checkEntity(x,y,Map.TERRAIN,'block_move',game.player)
end
function M.setup(version)
 guard();M.original={smooth=config.settings.tome.smooth_move,twitch=config.settings.tome.twitch_move,scroll=game.level.map.smooth_scroll}
 local rem={};for _,a in pairs(game.level.entities) do if a.ai and a~=game.player then rem[#rem+1]=a end end
 for _,a in ipairs(rem) do game.level.map:remove(a.x,a.y,Map.ACTOR);game.level:removeEntity(a,true) end
 local best,bx,by
 for x=2,game.level.map.w-9 do for y=2,game.level.map.h-5 do
  local ok=true;for dx=0,6 do for dy=0,2 do if not clear(x+dx,y+dy) then ok=false end end end
  local d=(x-game.player.x)^2+(y-game.player.y)^2
  if ok and (not best or d<best) then best,bx,by=d,x,y end
 end end
 assert(bx,'need natural 7x3 clear floor');M.x,M.y=bx,by
 local source;for _,a in pairs(game.zone.npc_list) do if a.name=='copperhead snake' then source=a;break end end
 M.a=game.zone:finishEntity(game.level,'actor',assert(source));M.a.never_act=true;M.a.rank=3.5;M.a.life=M.a.max_life*.4
 game.zone:addEntity(game.level,M.a,'actor',bx+1,by+1)
 M.a.life=M.a.max_life*.4
 core.game.forbidIdleMode(true);core.game.setFPS(30)
 M.a:setEffect(M.a.EFF_DAMAGE_SHIELD,100,{power=40},true)
 -- Native attached emitter, independent of shield replacement.
 M.a:addParticles(require('engine.Particles').new('wildfire',1))
 local p=game.player;p:move(bx+3,by+2,true);p.sight=50;p:resetMoveAnim()
 game.level.map.clean_fov=true;p:playerFOV();game.level.map.smooth_scroll=0;game.level.map:centerViewAround(bx+3,by+1)
 game:checkerRefreshVisuals();M.a:resetMoveAnim();M.a.energy.value=game.energy_to_act
 M.old_display=game.display
 game.display=function(self,n,...)
  local r=M.old_display(self,n,...)
  if M.active then local ok,err=xpcall(function() M.tick(n) end,debug.traceback);if not ok then M.active=false;write(M.clip..'-ERROR.txt',err) end end
  return r
 end
 M.old_frame=M.a.checkerTacticalFrame
 M.draws,M.player_draws=0,0
 M.a.checkerTacticalFrame=function(a,map,x,y,...) M.frame_x,M.frame_y=x,y;M.draws=M.draws+1;return M.old_frame(a,map,x,y,...) end
 M.old_player_frame=p.checkerTacticalFrame
 p.checkerTacticalFrame=function(a,...) M.player_draws=M.player_draws+1;return M.old_player_frame(a,...) end
 write('setup.txt',('version=%s; zone=%s; origin=%d,%d; actor=%s uid=%d; life=%g/%g; rank=%s; shield=40; wildfire native emitter; original smooth=%s twitch=%s scroll=%s\nAI frozen; actions scheduled after rendered frames; energy replenished per requested action; no world-turn/AI/cooldown claim\n'):format(version or '0.6.3',game.zone.short_name,bx,by,M.a.name,M.a.uid,M.a.life,M.a.max_life,tostring(M.a.rank),tostring(M.original.smooth),tostring(M.original.twitch),tostring(M.original.scroll)))
end
local function move(a,dx,dy) a.energy.value=game.energy_to_act;local ox,oy=a.x,a.y;assert(a:move(ox+dx,oy+dy));assert(a.x==ox+dx and a.y==oy+dy);game.paused=true end
local function ev(t,name,f) return {t=t,name=name,f=f} end
function M.start(clip)
 guard();assert(not M.active);M.clip=clip;M.rows={'ms\tframe\tkeyframes\taction\tx\ty\tbody_dx\tbody_dy\toverlay_dx\toverlay_dy\tring_x\tring_y\tmap_x\tmap_y\tflip\tplayer_x\tplayer_y\tstate_draws\tplayer_state_draws\texpected_ring_x\texpected_ring_y\tcenter_error_px\tfacing\ttile_px\ttwitch'};M.events={};M.frame=0;M.i=1;M.label='idle';M.t0=core.game.getTime();M.done=3000;M.draws=0;M.player_draws=0
 local a,p,m=M.a,game.player,game.level.map
 if clip=='walk' then
  M.events={ev(350,'step-right',function() move(a,1,0) end),ev(850,'step-left',function() move(a,-1,0) end),ev(1350,'diagonal-down-right',function() move(a,1,1) end),ev(1850,'diagonal-up-left',function() move(a,-1,-1) end),ev(2300,'rapid-right',function() move(a,1,0) end),ev(2335,'rapid-reverse',function() move(a,-1,0) end)}
 elseif clip=='special' then
  M.events={ev(350,'knockback-3',function() a:knockback(a.x-1,a.y,3);game.paused=true end),ev(1000,'forceMoveAnim-left-3',function() a:forceMoveAnim(a.x-3,a.y);game.paused=true end),ev(1700,'teleport-exact-3',function() assert(a:teleportRandom(a.x+3,a.y,0));game.paused=true end),ev(2200,'teleport-force-anim',function() assert(a:teleportRandom(a.x-3,a.y,0,0,true));game.paused=true end)}
 elseif clip=='twitch-off' then
  config.settings.tome.twitch_move=false
  M.events={ev(350,'no-twitch-right',function() move(a,1,0) end),ev(900,'no-twitch-left',function() move(a,-1,0) end),ev(1450,'smooth-off',function() config.settings.tome.smooth_move=0;move(a,1,0) end),ev(2000,'restore-baseline',function() config.settings.tome.smooth_move=M.original.smooth;config.settings.tome.twitch_move=M.original.twitch;move(a,-1,0) end)}
 elseif clip=='rush' then
  p:move(M.x,M.y+1,true);p:resetMoveAnim();a:move(M.x+6,M.y+1,true);a:resetMoveAnim();a.life=1000;a.max_life=1000
  m.clean_fov=true;p:playerFOV();m:centerViewAround(M.x+3,M.y+1)
  M.events={ev(700,'native-Rush-action',function()
   local t=p:getTalentFromId(p.T_RUSH);local old=p.getTargetLimited;p.getTargetLimited=function() return a.x,a.y,a end
   local ok,result=pcall(t.action,p,t);p.getTargetLimited=old;assert(ok,result);assert(result);game.paused=true
  end)}
 elseif clip=='path-camera' then
  a.faction=p.faction;a:move(M.x+1,M.y+1,true);a:resetMoveAnim();p:move(M.x,M.y+2,true);p:resetMoveAnim();m.smooth_scroll=config.settings.tome.smooth_move;m.clean_fov=true;p:playerFOV();m:centerViewAround(p.x,p.y)
  M.events={ev(450,'native-mouseMove-Astar',function() p.energy.value=game.energy_to_act;p:mouseMove(M.x+6,M.y+2,true);game.paused=true;assert(p.running and p.running.path,'native path was not started') end)}
  for i=1,8 do M.events[#M.events+1]=ev(450+i*180,'native-runStep-'..i,function() p.energy.value=game.energy_to_act;if p.running then p:runStep() end;game.paused=true;m.clean_fov=true;p:playerFOV() end) end
  M.events[#M.events+1]=ev(2300,'native-scrollDir-left',function() m:scrollDir(4) end)
  M.events[#M.events+1]=ev(2650,'native-scrollDir-right',function() m:scrollDir(6) end)
 else error(clip) end
 M.active=true;core.display.forceRedraw()
end
function M.tick(n)
 M.frame=M.frame+1;local t=core.game.getTime()-M.t0;local a=M.a;local s=a._checker_token;local m=game.level.map
 local dx,dy=a._mo:getMoveAnim(m._map,a.x,a.y);local ex,ey=s.overlay._mo:getMoveAnim(m._map,a.x,a.y)
 local sx,sy=m:getTileToScreen(a.x,a.y)
 local expected_x,expected_y=sx+dx*m.tile_w,sy+dy*m.tile_h
 local center_error=M.frame_x and math.max(math.abs(M.frame_x-expected_x),math.abs(M.frame_y-expected_y)) or -1
 M.rows[#M.rows+1]=table.concat({t,M.frame,n or '',M.label,a.x,a.y,dx,dy,ex,ey,M.frame_x or '',M.frame_y or '',m.mx,m.my,tostring(a._flipx),game.player.x,game.player.y,M.draws,M.player_draws,expected_x,expected_y,center_error,require('mod.class.CheckerOptions').tokenFacing(),m.tile_w,tostring(config.settings.tome.twitch_move)},'\t');M.draws=0;M.player_draws=0
 if M.events[M.i] and t>=M.events[M.i].t then local e=M.events[M.i];M.label=e.name;e.f();M.i=M.i+1 end
 if t>=M.done then M.active=false;write(M.clip..'.tsv',table.concat(M.rows,'\n')..'\n');write(M.clip..'-done.txt','PASS\n');game.paused=true end
end
function M.finish()
 assert(not M.active);game.display=M.old_display;M.a.checkerTacticalFrame=M.old_frame;game.player.checkerTacticalFrame=M.old_player_frame;core.game.forbidIdleMode(false);core.game.setFPS(config.settings.display_fps)
 config.settings.tome.smooth_move=M.original.smooth;config.settings.tome.twitch_move=M.original.twitch;game.level.map.smooth_scroll=M.original.scroll;game.paused=true
end
return M
