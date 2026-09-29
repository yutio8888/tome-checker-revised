-- Disposable offline HIDEOUT scene. Actors are native finishEntity instances,
-- arranged for art review with frozen AI. This is not natural-spawn evidence.
local Map = require 'engine.Map'
local Base = assert(loadfile('/data-checker-fixture/monster-live_korpul_scene.lua'))()
local M = {actors = {}, names = {'cutpurse', 'rogue', 'thief', 'bandit'}}

local function guard()
 assert(require('mod.class.CheckerFixture').enabled() and not profile.auth)
 assert(game.checker_staged and game.player == game.checker_hero)
 assert(game.zone and game.zone.short_name == 'ruins-kor-pul' and game.zone.is_hideout)
end

local function passable(map, x, y)
 if not map:isBound(x, y) then return false end
 local g = map(x, y, Map.TERRAIN)
 return g and not g.change_level and not g.change_zone
  and require('mod.class.CheckerTerrain').classify(g) == 'floor'
  and not map:checkEntity(x, y, Map.TERRAIN, 'block_move', game.player)
end

function M.enter(seed)
 assert(type(seed) == 'number')
 assert(not M.detection_handle, 'restore fixture hero detection before reentering')
 Base.enter('HIDEOUT', seed)
 guard()
 M.seed, M.actors, M.detection_handle, M.phase = seed, {}, nil, 'baseline'
end

function M.refresh()
 guard()
 local map = game.level.map
 game.player:playerFOV()
 map.smooth_scroll = 0
 map:centerViewAround(game.player.x, game.player.y)
 map:redisplay(); map.changed = true; game.player.changed = true; game.paused = true
 if game.uiset.npcs_display.refresh then game.uiset.npcs_display:refresh() end
end

function M.dismissFixturePrompts()
 Base.dismissFixturePrompts() -- Only known fixture dialogs and entry flyers.
end

local function observation(actor)
 local map = game.level.map
 local seen, chance = game.player:canSee(actor) -- Cached native roll; do not reroll.
 return {
  active = not not actor:isTalentActive(actor.T_STEALTH),
  stealth = actor:attr('stealth') or 0,
  prevents_targetting = actor:attr('stealthed_prevents_targetting') or 0,
  seen = not not seen, chance = chance or 0,
  fov = not not map.seens(actor.x, actor.y),
  infovs = not not map.infovs(actor.x, actor.y),
 }
end

function M.dump(label)
 guard(); assert(label == M.phase, 'phase mismatch')
 M.refresh()
 local path = '/thief-scene-' .. label .. '.tsv'
 local f = assert(fs.open(path, 'w'))
 local rules = assert(fs.open('/thief-rules-' .. label .. '.txt', 'w'))
 rules:write(table.concat({tostring(game.turn), tostring(game.player.x), tostring(game.player.y),
  tostring(game.player.life), tostring(game.player.max_life),
  tostring(game.player:attr('see_stealth') or 0),
  tostring(game.player.esp and game.player.esp.humanoid or 0)}, '\t') .. '\n')
 f:write('phase\tname\tx\ty\ttype\tsubtype\tdefine_as\timage\tshader\trank\ttalent_stealth\tactive_stealth\tstealth\tprevents_targetting\thero_can_see\tsee_chance\tmap_seens\tmap_infovs\ttoken\n')
 for _, a in ipairs(M.actors) do
  local o = observation(a)
  local fields = {label, a.name, a.x, a.y, a.type, a.subtype, a.define_as or '',
   a.image or '', a.shader or '', a.rank or '', a:getTalentLevelRaw(a.T_STEALTH) or 0,
   o.active, o.stealth, o.prevents_targetting, o.seen, o.chance, o.fov, o.infovs,
   a._checker_token and a._checker_token.id or 'native'}
  for i, value in ipairs(fields) do fields[i] = tostring(value) end
  f:write(table.concat(fields, '\t') .. '\n')
  rules:write(table.concat({tostring(a.name), tostring(a.x), tostring(a.y),
   tostring(a.life), tostring(a.max_life), tostring(a.rank),
   tostring(a:getTalentLevelRaw(a.T_STEALTH) or 0), tostring(o.active),
   tostring(o.stealth), tostring(o.prevents_targetting), tostring(o.seen),
   tostring(o.chance), tostring(o.fov), tostring(o.infovs)}, '\t') .. '\n')
 end
 f:close()
 rules:close()
 print('[ThiefScene] report', label, path)
 return path
end

function M.stage()
 guard(); assert(M.seed and not M.detection_handle)
 local map = game.level.map
 local bx, by, best
 -- Reuse the native map and select an open room where all four actors can be
 -- placed on passable floor without editing terrain or the actors' talents.
 for x = 6, map.w - 7 do for y = 6, map.h - 7 do
  if passable(map, x, y) then
   local open = 0
   for dx = -4, 4 do for dy = -3, 3 do
    if passable(map, x + dx, y + dy) then open = open + 1 end
   end end
   if open >= 25 and (not best or open > best) then bx, by, best = x, y, open end
  end
 end end
 assert(bx, 'no suitable native HIDEOUT room')
 local old = {}
 for _, a in pairs(game.level.entities) do
  if a.ai and a ~= game.player then old[#old + 1] = a end
 end
 for _, a in ipairs(old) do
  map:remove(a.x, a.y, Map.ACTOR); game.level:removeEntity(a, true)
 end
 -- Native sustains_at_birth runs on Zone:addEntity. Keep the hero far enough
 -- away during on_added that ordinary proximity does not block Stealth.
 local hx, hy, far
 for x = 1, map.w - 2 do for y = 1, map.h - 2 do
  if passable(map, x, y) then
   local distance = (x - bx)^2 + (y - by)^2
   if not far or distance > far then hx, hy, far = x, y, distance end
  end
 end end
 assert(hx and far >= 225, 'no distant hero staging cell')
 game.player:move(hx, hy, true)
 game.player.sight = 20
 M.refresh()
 local source = {}
 for _, proto in pairs(game.zone.npc_list) do if proto.name then source[proto.name] = proto end end
 M.actors = {}
 local targets = {{-3,-2}, {3,-2}, {-3,2}, {3,2}}
 for i, name in ipairs(M.names) do
  local a = game.zone:finishEntity(game.level, 'actor', assert(source[name], name))
  assert(a.name == name and a.type == 'humanoid' and a.subtype == 'human')
  a.never_act = true
  local dx, dy = unpack(targets[i])
  local nx, ny, score
  for x = bx - 4, bx + 4 do for y = by - 3, by + 3 do
   if passable(map, x, y) and not map(x, y, Map.ACTOR) then
    local distance = (x - bx - dx)^2 + (y - by - dy)^2
    if not score or distance < score then nx, ny, score = x, y, distance end
   end
  end end
  assert(nx, 'not enough observed open cells')
  game.zone:addEntity(game.level, a, 'actor', nx, ny)
  game:checkerRefreshActor(a)
  M.actors[#M.actors + 1] = a
 end
 game.player:move(bx, by, true)
 game.player:resetCanSeeCache()
 M.refresh()
 M.dismissFixturePrompts()
 print('[ThiefScene] arranged HIDEOUT', M.seed, bx, by, #M.actors)
end

function M.setObservation(phase)
 guard(); assert(phase == 'baseline' or phase == 'detected')
 assert(#M.actors == 4)
 if phase == 'detected' and not M.detection_handle then
  -- Native humanoid ESP affects only the fixture hero's observation. The
  -- thieves retain their native Stealth sustain and every actor rule.
  M.detection_handle = game.player:addTemporaryValue('esp', {humanoid=1})
 elseif phase == 'baseline' and M.detection_handle then
  game.player:removeTemporaryValue('esp', M.detection_handle)
  M.detection_handle = nil
 end
 M.phase = phase
 game.player:resetCanSeeCache()
 M.refresh()
end

return M
