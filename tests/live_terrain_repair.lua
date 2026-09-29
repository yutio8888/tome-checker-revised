-- Offline fixture only. Trollmire refined terrain after native NicerTiles re-tiles.
-- Every trigger is a native code path; AI stays frozen by the staged fixture.
-- The control step shadows game:checkerRepairTerrain on the instance so the
-- same process shows the unrepaired native result before the repaired one.
local Map=require 'engine.Map'
local DamageType=require 'engine.DamageType'
local M={rows={}}
local function guard()
 assert(require('mod.class.CheckerFixture').enabled() and not profile.auth)
 assert(game.checker_staged and game.paused and game.player==game.checker_hero)
 assert(game.zone.short_name=='trollmire' and not game.zone.is_flooded)
 assert(game.checker_mode=='refined','refined terrain required')
end
local function say(text)
 M.rows[#M.rows+1]=text;print('[TerrainRepair]',text)
 local f=assert(fs.open('/terrain-repair-validation.txt','w'))
 f:write(table.concat(M.rows,'\n')..'\n');f:close()
end
-- A cell is "ours" when the installed display is still attached to the grid.
local function owned(g)
 local s=g and g._checker_terrain
 return s and g.replace_display==s.display and true or false
end
-- Native classes the forest renderer supports (mirrors CheckerTerrain.terrain).
local function supported(g)
 if not g then return false end
 if g.subtype=='grass' then
  if g.change_level or g.change_zone then return false end
  if g.does_block_move then return g.name=='tree' or g.name=='tall thick tree' end
  return g.road or g.name=='flower' or g.name=='grass' and true or false
 end
 return g.subtype=='water' and (g.name=='deep water' or g.name=='bog water')
end
function M.census(x1,y1,x2,y2)
 local m=game.level.map
 x1,y1,x2,y2=x1 or 0,y1 or 0,x2 or m.w-1,y2 or m.h-1
 local c={supported=0,owned=0,native=0,cells={}}
 for x=math.max(x1,0),math.min(x2,m.w-1) do for y=math.max(y1,0),math.min(y2,m.h-1) do
  local g=m(x,y,Map.TERRAIN)
  if supported(g) then
   c.supported=c.supported+1
   if owned(g) then c.owned=c.owned+1 else c.native=c.native+1;c.cells[#c.cells+1]=x..','..y..':'..tostring(g.name) end
  end
 end end
 return c
end
local function rules(x1,y1,x2,y2)
 local m,out=game.level.map,{}
 for x=x1,x2 do for y=y1,y2 do
  local g=m(x,y,Map.TERRAIN)
  out[#out+1]=table.concat({x,y,tostring(g and g.name),tostring(g and g.does_block_move),
   tostring(g and g.block_sight),tostring(g and g.define_as)},'/')
 end end
 return table.concat(out,';')
end
local function state()
 local p=game.player
 return table.concat({game.turn,p.x,p.y,p.life,p.energy.value},'/')
end
function M.refresh()
 local m=game.level.map
 m.clean_fov=true;game.player:playerFOV()
 m.smooth_scroll=0;m:centerViewAround(game.player.x,game.player.y)
 m:redisplay();m.changed=true;game.paused=true;core.display.forceRedraw()
end
-- Diggable trees currently seen near the player, nearest first.
local function trees(skip)
 local m,p,list=game.level.map,game.player,{}
 for x=p.x-6,p.x+6 do for y=p.y-4,p.y+4 do
  local g=m(x,y,Map.TERRAIN)
  if g and g.dig and g.name=='tree' and m.seens(x,y) and not (skip and skip[x..','..y]) then
   list[#list+1]={x=x,y=y,d=math.abs(x-p.x)+math.abs(y-p.y)}
  end
 end end
 table.sort(list,function(a,b) return a.d<b.d or a.d==b.d and (a.x<b.x or a.x==b.x and a.y<b.y) end)
 return list
end
local function dig(x,y)
 DamageType:get(DamageType.DIG).projector(game.player,x,y,DamageType.DIG,1)
end

function M.run()
 guard()
 M.rows={}
 local before=state()
 local full=M.census()
 say(('start supported=%d owned=%d native=%d state=%s'):format(full.supported,full.owned,full.native,before))
 assert(full.native==0,'fresh staged level must be fully refined')
 local used={}
 local candidates=trees(used)
 assert(#candidates>=3,'need three diggable trees near the player')

 -- 1. Control: native DIG with the repair shadowed off shows the regression.
 local a=candidates[1];used[a.x..','..a.y]=true
 game.checkerRepairTerrain=false
 local ok,err=pcall(dig,a.x,a.y)
 game.checkerRepairTerrain=nil
 assert(ok,err)
 local ctl=M.census(a.x-2,a.y-2,a.x+2,a.y+2)
 local nativeRules=rules(a.x-2,a.y-2,a.x+2,a.y+2)
 say(('control dig %d,%d -> %s; window supported=%d native=%d [%s]'):format(a.x,a.y,
  tostring(game.level.map(a.x,a.y,Map.TERRAIN).name),ctl.supported,ctl.native,table.concat(ctl.cells,' ')))
 assert(ctl.native>0,'control must reproduce the native fallback')
 M.control={x=a.x,y=a.y,native=ctl.native}
 -- Repairing that window afterwards restores art without touching rules.
 local fixed=game:checkerRepairTerrain(a.x-2,a.y-2,a.x+2,a.y+2)
 local after=M.census(a.x-2,a.y-2,a.x+2,a.y+2)
 assert(after.native==0,'manual repair restores the control window')
 assert(rules(a.x-2,a.y-2,a.x+2,a.y+2)==nativeRules,'repair must not change grid rules')
 say(('control repaired cells=%d native=%d rules unchanged'):format(fixed,after.native))

 -- 2. Integrated: native DIG through the superloaded NicerTiles.
 local b
 for _,c in ipairs(trees(used)) do
  if math.abs(c.x-a.x)>4 or math.abs(c.y-a.y)>4 then b=c;break end
 end
 b=b or trees(used)[1];used[b.x..','..b.y]=true
 dig(b.x,b.y)
 local w=M.census(b.x-2,b.y-2,b.x+2,b.y+2)
 say(('integrated dig %d,%d -> %s; window supported=%d native=%d'):format(b.x,b.y,
  tostring(game.level.map(b.x,b.y,Map.TERRAIN).name),w.supported,w.native))
 assert(w.native==0,'integrated dig leaves no native cell: '..table.concat(w.cells,' '))
 M.dig={x=b.x,y=b.y}

 -- 3. Generic caller (earth talents, Jumpgate, on_block_change share it).
 local c=trees(used)[1];used[c.x..','..c.y]=true
 game.nicer_tiles:updateAround(game.level,c.x,c.y)
 w=M.census(c.x-2,c.y-2,c.x+2,c.y+2)
 say(('updateAround %d,%d window supported=%d native=%d'):format(c.x,c.y,w.supported,w.native))
 assert(w.native==0,'generic updateAround leaves no native cell')

 -- 4. Mid-game full passes used by timed effects and shadowflame/timetravel.
 game.nicer_tiles:postProcessLevelTilesOnLoad(game.level)
 full=M.census()
 say(('postProcessLevelTilesOnLoad supported=%d native=%d'):format(full.supported,full.native))
 assert(full.native==0,'load-time full re-tile is repainted')
 game.nicer_tiles:postProcessLevelTiles(game.level)
 full=M.census()
 say(('postProcessLevelTiles supported=%d native=%d'):format(full.supported,full.native))
 assert(full.native==0,'full re-tile is repainted')

 -- 5. Mode round trip still owns and releases the repaired cells.
 game:checkerSetMode('vanilla')
 full=M.census()
 assert(full.owned==0,'vanilla releases every repaired cell')
 game.nicer_tiles:updateAround(game.level,b.x,b.y)
 assert(M.census().owned==0,'vanilla re-tile installs nothing')
 game:checkerSetMode('refined')
 full=M.census()
 assert(full.native==0,'refined reinstalls everything')
 say(('mode round trip vanilla owned=0 refined native=%d'):format(full.native))

 local finish=state()
 say(('state before=%s after=%s'):format(before,finish))
 assert(before==finish,'repair must not change turn, position, life or energy')
 M.refresh()
 say('PASS')
 return M
end

M.state=state
-- Put the camera on a cell (default: the integrated dig) for screenshots.
function M.focus(x,y)
 guard()
 x,y=x or M.dig.x,y or M.dig.y
 local m=game.level.map
 m.clean_fov=true;game.player:playerFOV()
 m.smooth_scroll=0;m:centerViewAround(x,y);m:redisplay();m.changed=true
 game.paused=true;core.display.forceRedraw()
 return M.census(x-2,y-2,x+2,y+2)
end
function M.focusDig()
 local w=M.focus(M.dig.x,M.dig.y)
 assert(w.native==0,'integrated dig window must stay refined')
 say(('focus dig %d,%d supported=%d native=%d'):format(M.dig.x,M.dig.y,w.supported,w.native))
 return w
end
-- Screenshot-only control after run(): dig one more tree with the repair
-- shadowed off, leave it unrepaired for the capture, then repair it.
function M.controlShot()
 guard()
 assert(M.dig and M.control,'run() first')
 local t
 for _,c in ipairs(trees()) do
  if (math.abs(c.x-M.dig.x)>4 or math.abs(c.y-M.dig.y)>4) then t=c;break end
 end
 assert(t,'no tree left for the screenshot control')
 game.checkerRepairTerrain=false
 local ok,err=pcall(dig,t.x,t.y)
 game.checkerRepairTerrain=nil
 assert(ok,err)
 M.shotControl={x=t.x,y=t.y,rules=rules(t.x-2,t.y-2,t.x+2,t.y+2)}
 local w=M.focus(t.x,t.y)
 say(('screenshot control dig %d,%d -> %s; window supported=%d native=%d [%s]'):format(t.x,t.y,
  tostring(game.level.map(t.x,t.y,Map.TERRAIN).name),w.supported,w.native,table.concat(w.cells,' ')))
 assert(w.native>0,'screenshot control must show the native fallback')
 return w
end
function M.controlRepair()
 guard()
 local t=M.shotControl
 local n=game:checkerRepairTerrain(t.x-2,t.y-2,t.x+2,t.y+2)
 local w=M.focus(t.x,t.y)
 assert(w.native==0,'screenshot control window repaired')
 assert(rules(t.x-2,t.y-2,t.x+2,t.y+2)==t.rules,'repair must not change grid rules')
 assert(M.census().native==0,'whole map refined after control repair')
 say(('screenshot control repaired cells=%d native=%d rules unchanged'):format(n,w.native))
 return w
end
return M
