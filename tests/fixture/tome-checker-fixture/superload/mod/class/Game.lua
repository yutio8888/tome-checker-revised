-- Deliberately installed test addon: deterministic scene and local command bridge.
-- No dependency on checker-revised or Board HUD; native-art scenes also work.
local _M=loadPrevious(...)
local Map=require 'engine.Map'
local Entity=require 'engine.Entity'
local Fixture=require 'mod.class.CheckerFixture'

-- Legacy scene scripts use this transient override. It is fixture-only;
-- terrain mode never changes the persisted token option.
local tokensEnabled=_M.checkerTokensEnabled
if tokensEnabled then
 function _M:checkerTokensEnabled()
  return not self.checker_native_actors and tokensEnabled(self)
 end
end

-- The demo human is not a species/class mapping. Only this installed fixture
-- plus an explicit launch opt-in may use it for the fixed Cornac Berserker.
-- It takes precedence over any production player-family token.
local refreshActor=_M.checkerRefreshActor
if refreshActor then
 function _M:checkerRefreshActor(e,...)
  if not (Fixture.enabled() and __module_extra_info.checker_hero == true
    and e==self.checker_hero and self:checkerTokensEnabled() and self.level) then
   return refreshActor(self,e,...)
  end
  local state=e._checker_token
  if state and e.replace_display~=state.display then e._checker_token=nil;state=nil end
  if e.replace_display and not state then return refreshActor(self,e,...) end
  if state and state.id=='hero' then return 'hero' end
  if state then
   e:removeAllMOs();state.display:removeAllMOs()
   e.replace_display=state.original;e._checker_token=nil
  end
  local original=e.replace_display
  e:removeAllMOs()
  local display=Entity.new{image='checker-revised+hero.png',display='@',color={255,255,255},display_on_seen=true}
  e.replace_display=display;e._checker_token={id='hero',display=display,original=original}
  return 'hero'
 end
end
local function terrain(g)
 if g.change_level or g.change_zone then return 'exit' end
 if g.door_opened then return 'door' end
 if g.does_block_move then
  if g.name=='tree' or g.name=='tall thick tree' or (g.can_pass and g.can_pass.pass_tree) then return 'tree' end
  return 'obstacle'
 end
 if g.subtype=='water' then return (g.air_level and g.air_level<0) and 'deep' or 'bog' end
 if g.road then return 'road' end
 if g.name=='flower' then return 'flower' end
 return 'grass'
end
function _M:checkerStage()
 assert(Fixture.enabled(), 'offline checker fixture required')
 assert(self.zone and self.zone.short_name=='trollmire' and self.level, 'Trollmire fixture required')
 assert(not self.checker_staged,'Already staged')
 local m=self.level.map
 local bx,by,best,chosen
 for x=12,m.w-13 do for y=9,m.h-10 do
  local center=m(x,y,Map.TERRAIN)
  if terrain(center)~='deep' and terrain(center)~='bog' and not m:checkEntity(x,y,Map.TERRAIN,'block_move',self.player) then
   local cnt={water=0,tree=0,road=0,open=0}
   for dx=-7,7 do for dy=-5,5 do
    local t=terrain(m(x+dx,y+dy,Map.TERRAIN))
    if t=='deep' or t=='bog' then cnt.water=cnt.water+1 elseif t=='tree' then cnt.tree=cnt.tree+1 elseif t=='road' then cnt.road=cnt.road+1 else cnt.open=cnt.open+1 end
   end end
   if cnt.water>=8 and cnt.water<=90 and cnt.tree>=5 and cnt.road>=2 then
    local visible={water=0,tree=0,road=0,open=0}
    core.fov.calc_circle(x,y,m.w,m.h,10,function(_,cx,cy) return m:checkEntity(cx,cy,Map.TERRAIN,'block_sight',self.player) end,
     function(_,cx,cy)
      if math.abs(cx-x)<=7 and math.abs(cy-y)<=5 then
       local t=terrain(m(cx,cy,Map.TERRAIN))
       local key=(t=='deep' or t=='bog') and 'water' or t=='tree' and 'tree' or t=='road' and 'road' or 'open'
       visible[key]=visible[key]+1
      end
     end,nil)
    local score=math.min(visible.water,36)*3+math.min(visible.tree,20)+math.min(visible.road,16)+visible.open*.6-math.abs(y-20)*.2
    if visible.water>=10 and (not best or score>best) then bx,by,best,chosen=x,y,score,visible end
   end
  end
 end end
 assert(bx,'No suitable natural forest/water/road clearing')
 local rem={}
 for _,e in pairs(self.level.entities) do if e~=self.player and e.ai then
  e.never_act=true
  if math.abs(e.x-bx)<12 and math.abs(e.y-by)<9 then rem[#rem+1]=e end
 end end
 for _,e in ipairs(rem) do m:remove(e.x,e.y,Map.ACTOR);self.level:removeEntity(e,true) end
 self.player:move(bx,by,true)
 self.player.sight=20;self.player:playerFOV()
 for _,v in ipairs{{'forest troll',3,-1},{'wolf',-3,-2},{'brown bear',4,2},{'large brown snake',-2,3},{'giant venus flytrap',1,-3}} do
  local src
  for _,e in pairs(self.zone.npc_list) do if e.name==v[1] then src=e;break end end
  if src then
   local nx,ny
   for r=0,5 do for dx=-r,r do for dy=-r,r do
    local x,y=bx+v[2]+dx,by+v[3]+dy
    local g=m(x,y,Map.TERRAIN)
    if not nx and g and m.seens(x,y) and not m(x,y,Map.ACTOR) and terrain(g)~='deep' and terrain(g)~='bog' and not m:checkEntity(x,y,Map.TERRAIN,'block_move',self.player) then nx,ny=x,y end
   end end if nx then break end end
   if nx then local a=self.zone:finishEntity(self.level,'actor',src);a.never_act=true;self.zone:addEntity(self.level,a,'actor',nx,ny);print('[CheckerRefined] STAGED',a.name,nx,ny) end
  end
 end
 self.player.sight=20;self.player:playerFOV();m:centerViewAround(bx,by);self.paused=true;self.checker_staged=true
 print('[CheckerRefined] STAGE',bx,by,'water',chosen.water,'trees',chosen.tree,'road',chosen.road,'turn',self.turn)
end
local display=_M.display
function _M:display(...)
 local r=display(self,...)
 if Fixture.enabled() and self.checker_ready and not self.checker_busy then
  self.checker_busy=true
  local f=fs.exists('/checker-command.txt') and fs.open('/checker-command.txt','r')
  if f then local cmd=f:read(4096);f:close();fs.delete('/checker-command.txt')
   local ok,err=pcall(function()
    if cmd:match('^stage') then self:checkerStage()
    elseif cmd:match('^toggle') then assert(self.checkerToggle, 'tokens addon is not installed')(self)
    elseif cmd:match('^mode ') then assert(self.checkerSetMode, 'tokens addon is not installed')(self,cmd:match('^mode (%w+)'))
    elseif cmd:match('^aura ') then
     local value=cmd:match('^aura (%a+)$')
     assert(value=='subtle' or value=='moderate','use aura subtle/moderate')
     require('mod.class.CheckerOptions').setAuraStyle(value,self)
    elseif cmd:match('^tokens ') then assert(self.checkerSetTokensEnabled, 'tokens addon is not installed')(self,cmd:match('^tokens (%w+)')=='on')
    elseif cmd:match('^player%-tokens ') then assert(self.checkerSetPlayerTokensEnabled, 'tokens addon is not installed')(self,cmd:match('^player%-tokens (%w+)')=='on')
    elseif cmd:match('^zoom ') then
     local z=tonumber(cmd:match('^zoom (%d+)'));assert(z==48 or z==64 or z==96)
     config.settings.tome.gfx.size=z..'x'..z;self:setupDisplayMode(false)
     self.player:playerFOV();self.level.map:centerViewAround(self.player.x,self.player.y)
    elseif cmd:match('^audit') then dofile('/data-checker-fixture/audit.lua')
    elseif cmd:match('^shot ') then local name=cmd:match('^shot ([%w_-]+)');local s=self:takeScreenshot();local o=assert(fs.open('/'..name..'.png','w'));o:write(s);o:close();print('[CheckerRefined] SHOT',name) end
   end)
   if not ok then print('[CheckerRefined] ERROR',err) end
  end
  self.checker_busy=nil
 end
 return r
end
return _M
