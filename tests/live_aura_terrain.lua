-- Isolated checker-fixture only. Invoked through audit.lua's local bridge.
local Survey=dofile('/data-checker-fixture/monster-live_map_survey.lua')
local Terrain=require 'mod.class.CheckerTerrain'
local Map=require 'engine.Map'
local M={}

local surfaces={
 trollmire={'trollmire',{}},
 oldforest={'old-forest',{crystaline=false}},
 korpul={'ruins-kor-pul',{hideout=false}},
 rhaloren={'rhaloren-camp',{overground=true}},
}
local effects={['fell-aura']='EFF_FELL_AURA',['antimagic-bush']='EFF_ANTIMAGIC_BUSH',
 ['spellblaze-scar']='EFF_SPELLBLAZE_SCAR',['bligthed-soil']='EFF_BLIGHTED_SOIL',
 ['protective-aura']='EFF_PROTECTIVE_AURA',['font-life']='EFF_FONT_OF_LIFE'}
local function eventOnStand(g,event)
 local info=g and g.on_stand and debug.getinfo(g.on_stand,'S')
 local suffix='/events/'..event..'.lua'
 return info and info.source and info.source:sub(-#suffix)==suffix and true or false
end
local function owned(g,m,x,y)
 local state=g._checker_terrain
 if state and g.replace_display==state.display then return true end
 local record=m._checker_korpul and m._checker_korpul[x+y*m.w]
 if record and record.kind=='floor' then
  local d=Terrain.render(m,x,y,g,'refined')
  return d and d.image and d.image:match('checker%-revised%+refined/korpul/') and true or false
 end
 return false
end
-- Inspect the texture requested while rebuilding the actual map object for
-- this cell. An owned replacement alone missed native roads in the old B shot:
-- the previous board MO stayed on screen until a full settings refresh.
local function drawn(m,x,y,g)
 local replacement=g.replace_display or Terrain.render(m,x,y,g,'refined')
 local expected=replacement and replacement.image
 local mask=replacement and replacement.add_displays and replacement.add_displays[1] and replacement.add_displays[1].image
 if not expected then return false,nil,expected end
 if replacement.removeAllMOs then replacement:removeAllMOs() end
 if g.removeAllMOs then g:removeAllMOs() end
 local old=m.tiles.get
 local images={}
 m.tiles.get=function(self,display,r,green,b,br,bg,bb,image,...)
  local result={old(self,display,r,green,b,br,bg,bb,image,...)}
  images[#images+1]={image=image,w=result[4],h=result[5]}
  return unpack(result)
 end
 local ok,err=pcall(m.updateMap,m,x,y)
 m.tiles.get=old
 if not ok then error(err) end
 local maskSeen=not mask
 for _,item in ipairs(images) do
  if item.image==mask and item.w==128 and item.h==128 then maskSeen=true end
 end
 return images[1] and images[1].image==expected and maskSeen,
  images[1] and images[1].image,expected,mask,maskSeen
end
local function textureCensus(m,rows)
 local count,bad=0,{}
 local visible=Terrain.visible
 Terrain.visible=function() return true end
 for _,row in ipairs(rows) do if row.supported then
  local g=m(row.x,row.y,Map.TERRAIN)
  local ok,actual,expected,mask,maskSeen=drawn(m,row.x,row.y,g)
  count=count+1
  if not ok or not expected or not expected:match('^checker%-revised%+') then
   bad[#bad+1]={x=row.x,y=row.y,id=row.id,actual=actual,expected=expected,mask=mask,maskSeen=maskSeen}
  end
 end end
 Terrain.visible=visible
 return {count=count,bad=bad}
end
local function supported(g)
 if Terrain.classify(g)=='floor' then return true end
 local id=g and g.define_as
 local road=id=='GRASS_ROAD_STONE' or id=='GRASS_ROAD_DIRT'
 local displaysOk=not g.add_displays or road and #g.add_displays==1 and
  g.add_displays[1].image=='invis.png' and g.add_displays[1].add_mos and
  #g.add_displays[1].add_mos>0
 return id and g.type=='floor' and not g.notice and displaysOk and
  not g.does_block_move and (id=='GRASS' or id=='GRASS_SHORT' or
  id:match('^GRASS_PATCH%d+$') or id=='FLOWER' or id:match('^FLOWER%d+$') or
  id=='GRASS_ROAD_STONE' or id=='GRASS_ROAD_DIRT') and true or false
end
local function refresh(x,y)
 local m=game.level.map
 m.clean_fov=true;game.player:playerFOV()
 m.smooth_scroll=0;m:centerViewAround(x,y);m:redisplay();m.changed=true
 game.paused=true;core.display.forceRedraw()
end
local function shot(name)
 local data=game:takeScreenshot()
 local f=assert(fs.open('/'..name..'.png','w'));f:write(data);f:close()
end
local function choose(surface,preferRoad)
 local m=game.level.map
 local best
 for x=5,m.w-6 do for y=5,m.h-6 do
  local g=m(x,y,Map.TERRAIN)
  local forest=g and g.type=='floor' and g.subtype=='grass' or
   g and g.type=='floor' and g.subtype=='dark_grass'
  local stone=g and g._checker_grid_source and g._checker_grid_source.id=='FLOOR'
  if g and (not preferRoad or g.define_as=='GRASS_ROAD_DIRT' or g.define_as=='GRASS_ROAD_STONE') and
   game.state:canEventGrid(game.level,x,y) and
   (surface=='korpul' and stone or surface~='korpul' and (forest or stone)) then
   local score=0
   for dx=-2,2 do for dy=-2,2 do
    local n=m(x+dx,y+dy,Map.TERRAIN)
    if n and n.type=='floor' and game.state:canEventGrid(game.level,x+dx,y+dy) then score=score+1 end
   end end
   score=score*100-math.abs(x-game.player.x)-math.abs(y-game.player.y)
   if not best or score>best.score then best={x=x,y=y,score=score,id=g.define_as} end
  end
 end end
 return best
end

function M.run(event,surface,prefix,capture,preferRoad)
 assert(require('mod.class.CheckerFixture').enabled() and not profile.auth)
 assert(type(event)=='string' and event:match('^[%w%-]+$'))
 local config=assert(surfaces[surface],surface)
 local entry=Survey.enter(config[1],1,config[2])
 game:checkerSetMode('refined')
 require('mod.class.CheckerOptions').setAuraStyle('subtle',game)
 local center=assert(choose(surface,preferRoad),'no suitable event floor')
 local find=game.state.findEventGrid
 game.state.findEventGrid=function() return center.x,center.y end
 local oldLevel,oldZone=_G.level,_G.zone
 _G.level=game.level;_G.zone=game.zone
 local ok,ret=xpcall(function() return dofile('/data/general/events/'..event..'.lua') end,debug.traceback)
 game.state.findEventGrid=find;_G.level=oldLevel;_G.zone=oldZone
 assert(ok and ret,'event failed: '..tostring(ret))
 local m=game.level.map
 local rows={}
 local total=0
 -- Same census convention as live_map_survey: make every cell observable for
 -- one read-only coverage sweep, then restore real FOV before screenshots.
 local visible=Terrain.visible
 Terrain.visible=function() return true end
 for x=0,m.w-1 do for y=0,m.h-1 do
  local g=m(x,y,Map.TERRAIN)
  if eventOnStand(g,event) then
   total=total+1
   if Terrain.variant(game.zone) then Terrain.observe(m,x,y,g) end
   rows[#rows+1]={x=x,y=y,id=g.define_as,kind=Terrain.classify(g),
    name=g.name,supported=supported(g),owned=owned(g,m,x,y),minimap=g.special_minimap and true or false,
    on_stand=g.on_stand and true or false}
  end
 end end
 Terrain.visible=visible
 local count,painted=0,0
 for _,row in ipairs(rows) do if row.supported then count=count+1;if row.owned then painted=painted+1 end end end
 local textures={b=textureCensus(m,rows)}
 -- Move to a nearby passable tile so the ring is in view. This remains a
 -- paused fixture scene; the real movement/effect check follows the captures.
 local px,py
 for radius=3,6 do
  for dx=-radius,radius do for dy=-radius,radius do
   local x,y=center.x+dx,center.y+dy
   if not px and x>=0 and y>=0 and x<m.w and y<m.h and
    not m:checkEntity(x,y,Map.TERRAIN,'block_move',game.player) and not m(x,y,Map.ACTOR) then px,py=x,y end
  end end
  if px then break end
 end
 if px then game.player:move(px,py,true) end
 refresh(center.x,center.y)
 if capture then shot(prefix..'-b') end
 require('mod.class.CheckerOptions').setAuraStyle('moderate',game);refresh(center.x,center.y)
 textures.b1=textureCensus(m,rows)
 if capture then shot(prefix..'-b1') end
 require('mod.class.CheckerOptions').setAuraStyle('subtle',game);refresh(center.x,center.y)
 textures.b_again=textureCensus(m,rows)
 -- DIG a native diggable grid just outside the event footprint. The existing
 -- NicerTiles hook must repaint any neighbouring aura cells it re-tiles.
 local dig={found=false}
 local DamageType=require 'engine.DamageType'
 for radius=3,7 do
  if dig.found then break end
  for dx=-radius,radius do for dy=-radius,radius do
   local x,y=center.x+dx,center.y+dy
   local g=m(x,y,Map.TERRAIN)
   if not dig.found and g and g.dig and not g.on_stand and
    math.max(math.abs(dx),math.abs(dy))==radius then
    dig={found=true,x=x,y=y,before=g.define_as or g.name}
    DamageType:get(DamageType.DIG).projector(game.player,x,y,DamageType.DIG,1)
    local after=m(x,y,Map.TERRAIN)
    dig.after=after and (after.define_as or after.name)
   end
  end end
 end
 local afterPainted,afterCallbacks=0,0
 local seenAgain=Terrain.visible
 Terrain.visible=function() return true end
 for _,row in ipairs(rows) do
  if row.supported then
   local g=m(row.x,row.y,Map.TERRAIN)
   if Terrain.variant(game.zone) then Terrain.observe(m,row.x,row.y,g) end
   if g and owned(g,m,row.x,row.y) then afterPainted=afterPainted+1 end
   if eventOnStand(g,event) then afterCallbacks=afterCallbacks+1 end
  end
 end
 Terrain.visible=seenAgain
 -- Check the original native callback through a real adjacent step.
 local stepped=false;local effect=false;local attempted=false
 for _,row in ipairs(rows) do
  if not attempted and row.supported and eventOnStand(m(row.x,row.y,Map.TERRAIN),event) then
   local x,y=row.x,row.y
   for _,d in ipairs{{1,0},{-1,0},{0,1},{0,-1}} do
    local ax,ay=x+d[1],y+d[2]
    if ax>=0 and ay>=0 and ax<m.w and ay<m.h and
     not m:checkEntity(ax,ay,Map.TERRAIN,'block_move',game.player) and
     not m:checkEntity(x,y,Map.TERRAIN,'block_move',game.player) and not m(x,y,Map.ACTOR) then
     game.player:move(ax,ay,true)
     game.player:move(x,y,false)
     attempted=true
     stepped=game.player.x==x and game.player.y==y
     -- Actor:actBase calls this exact native map entry once per real turn.
     -- The paused fixture does not advance that turn after the test step.
     if stepped then m:checkEntity(x,y,Map.TERRAIN,'on_stand',game.player) end
     local id=effects[event]
     effect=id and game.player:hasEffect(game.player[id]) and true or false
     break
    end
   end
  end
 end
 local result={event=event,surface=surface,entry=entry,center=center,event_cells=total,cells=count,
  painted=painted,native=count-painted,rows=rows,stepped=stepped,effect=effect,
  dig=dig,after_dig_painted=afterPainted,after_dig_callbacks=afterCallbacks,
  aura_style_default='subtle',textures=textures}
 Survey.dump('/'..prefix..'.json',result)
 return result
end
return M
