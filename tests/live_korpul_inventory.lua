-- Read-only-in-world native identity audit for the isolated OFFLINE Kor'Pul fixture.
-- Run on each layout separately: dofile('/checker-live-korpul-inventory.lua').run('korpul-default', 'DEFAULT')
-- This resolves detached copies of prototypes already in this zone. It does not
-- create a room, place an actor, save a game, or advance a turn. Native resolver
-- calls may consume RNG/UIDs; use a disposable fixture, not a campaign save.
local Tokens = require 'mod.class.CheckerTokens'
local M = {}

local candidates = {
 {scope='direct', layout='DEFAULT', name='degenerated skeleton warrior', source='/data/general/npcs/skeleton.lua:58'},
 {scope='direct', layout='DEFAULT', name='degenerated skeleton archer', source='/data/general/npcs/skeleton.lua:68'},
 {scope='direct', layout='DEFAULT', name='skeleton mage', source='/data/general/npcs/skeleton.lua:82'},
 {scope='direct', layout='BOTH', name='grey mold', source='/data/general/npcs/molds.lua:46'},
 {scope='direct', layout='HIDEOUT', name='cutpurse', source='/data/general/npcs/thieve.lua:62'},
 {scope='direct', layout='HIDEOUT', name='rogue', source='/data/general/npcs/thieve.lua:72'},
 {scope='direct', layout='HIDEOUT', name='thief', source='/data/general/npcs/thieve.lua:82'},
 {scope='direct', layout='HIDEOUT', name='bandit', source='/data/general/npcs/thieve.lua:98'},
 {scope='shared-import', layout='HIDEOUT', name='degenerated skeleton warrior', source='/data/general/npcs/all.lua:69'},
 {scope='shared-import', layout='HIDEOUT', name='degenerated skeleton archer', source='/data/general/npcs/all.lua:69'},
 {scope='shared-import', layout='HIDEOUT', name='skeleton mage', source='/data/general/npcs/all.lua:69'},
 {scope='shared-import', layout='DEFAULT', name='cutpurse', source='/data/general/npcs/all.lua:78'},
 {scope='shared-import', layout='DEFAULT', name='rogue', source='/data/general/npcs/all.lua:78'},
 {scope='shared-import', layout='DEFAULT', name='thief', source='/data/general/npcs/all.lua:78'},
 {scope='shared-import', layout='DEFAULT', name='bandit', source='/data/general/npcs/all.lua:78'},
 {scope='fixed-boss', layout='DEFAULT', define_as='SHADE', source='/data/zones/ruins-kor-pul/npcs.lua:41;/data/maps/zones/ruins-kor-pul-last.lua:24'},
 {scope='fixed-boss', layout='HIDEOUT', define_as='THE_POSSESSED', source='/data/zones/ruins-kor-pul/npcs.lua:93;/data/maps/zones/ruins-kor-pul-invaded-last.lua:24'},
 {scope='conditional-room', layout='BOTH', name='skeleton warrior', source='/data/maps/vaults/amon-sul-crypt.lua:40'},
 {scope='conditional-room', layout='BOTH', name='armoured skeleton warrior', source='/data/maps/vaults/amon-sul-crypt.lua:42'},
 {scope='conditional-room', layout='BOTH', name='skeleton mage', source='/data/maps/vaults/amon-sul-crypt.lua:57;/data/maps/vaults/auto/lesser/skeleton-mage-cabal.lua:33'},
 {scope='conditional-room', layout='BOTH', name='skeleton magus', source='/data/maps/vaults/amon-sul-crypt.lua:58'},
 {scope='conditional-room', layout='BOTH', name='ghoul', source='/data/maps/vaults/amon-sul-crypt.lua:74'},
 {scope='conditional-room', layout='BOTH', name='ghast', source='/data/maps/vaults/amon-sul-crypt.lua:75'},
 {scope='conditional-room', layout='BOTH', name='skeleton archer', source='/data/maps/vaults/amon-sul-crypt.lua:91'},
 {scope='conditional-room', layout='BOTH', name='skeleton master archer', source='/data/maps/vaults/amon-sul-crypt.lua:92'},
 {scope='conditional-room', layout='BOTH', name='thief', source='/data/maps/vaults/auto/lesser/skeleton-mage-cabal.lua:36'},
 {scope='conditional-room', layout='BOTH', name='bloated horror', source='/data/maps/vaults/auto/lesser/skeleton-mage-cabal.lua:37'},
 {scope='conditional-room', layout='BOTH', name='giant white rat', source='/data/maps/vaults/auto/lesser/rat-nest.lua:33'},
 {scope='conditional-room', layout='BOTH', name='giant brown rat', source='/data/maps/vaults/auto/lesser/rat-nest.lua:34'},
 {scope='conditional-room', layout='BOTH', name='giant grey rat', source='/data/maps/vaults/auto/lesser/rat-nest.lua:35'},
 {scope='conditional-room', layout='BOTH', name='rattlesnake', source='/data/maps/vaults/snake-pit.lua:43'},
 {scope='conditional-room', layout='BOTH', name='green worm mass', source='/data/maps/vaults/snake-pit.lua:44'},
 {scope='conditional-room', layout='BOTH', name='giant brown ant', source='/data/maps/vaults/snake-pit.lua:45'},
 {scope='conditional-room', layout='BOTH', name='snow cat', source='/data/maps/vaults/snake-pit.lua:46'},
 {scope='conditional-room', layout='BOTH', name='green mold', source='/data/maps/vaults/snake-pit.lua:47'},
 {scope='conditional-room', layout='BOTH', name='giant spider', source='/data/maps/vaults/snake-pit.lua:49'},
 {scope='conditional-room', layout='BOTH', name='ritch flamespitter', source='/data/maps/vaults/snake-pit.lua:50'},
 {scope='conditional-room', layout='BOTH', name='sandworm', source='/data/maps/vaults/snake-pit.lua:51'},
 {scope='escort', layout='HIDEOUT', name='thief', source='/data/zones/ruins-kor-pul/npcs.lua:114'},
}

local function clean(value)
 return tostring(value == nil and '' or value):gsub('[\t\r\n]', ' ')
end

local function list(value)
 if type(value) ~= 'table' then return clean(value) end
 local out = {}
 for key, item in pairs(value) do
  if type(item) == 'table' then
   out[#out+1] = tostring(key)..'={'..list(item)..'}'
  else out[#out+1] = tostring(key)..'='..clean(item) end
 end
 table.sort(out)
 return table.concat(out, ';')
end

local function guard(expected_layout)
 assert(expected_layout == 'DEFAULT' or expected_layout == 'HIDEOUT', 'pass expected layout')
 assert(config and config.settings and config.settings.cheat and config.settings.disable_all_connectivity
  and profile and not profile.auth, 'requires cheat/offline fixture')
 assert(__module_extra_info and __module_extra_info.checker_demo and game.checker_staged,
  'requires checker_demo staged fixture')
 assert(game.zone and game.zone.short_name == 'ruins-kor-pul' and game.level,
  'requires current ruins-kor-pul zone and level')
 local layout = game.zone.is_hideout and 'HIDEOUT' or 'DEFAULT'
 assert(layout == expected_layout, 'fixture is in '..layout..', expected '..expected_layout)
 assert(type(Tokens.explain) == 'function', 'reason-coded mapper required')
 return layout
end

local fields = {'zone','layout','level','turn','scope','candidate','name','type','subtype','define_as',
 'proto_rank','rank','level_min','level_max','image','add_mos','add_displays','shader','anim',
 'textures','shader_auras','replace_display','moddable_tile','token','status','reason','source'}

function M.run(filename, expected_layout)
 local layout = guard(expected_layout)
 assert(filename == nil or (type(filename) == 'string' and filename:match('^[%w_%-]+$')),
  'filename must be a simple basename')
 local path = '/'..(filename or ('korpul-inventory-'..layout:lower()))..'.tsv'
 local turn, player = game.turn, game.player
 local px, py, life = player.x, player.y, player.life
 local index = {}
 for _, proto in pairs(game.zone.npc_list) do
  if type(proto) == 'table' and proto.name then
   if proto.define_as then index['id:'..proto.define_as] = proto end
   index['name:'..proto.name] = index['name:'..proto.name] or proto
  end
 end
 local file = assert(fs.open(path, 'w'))
 file:write(table.concat(fields, '\t')..'\n')
 local counts = {resolved=0, unavailable=0, errors=0, covered=0, fallback=0}
 for _, c in ipairs(candidates) do
  if c.layout == 'BOTH' or c.layout == layout then
   local proto = index[c.define_as and ('id:'..c.define_as) or ('name:'..c.name)]
   local actor, ok, reason
   if proto then
    ok, actor = pcall(function() return game.zone:finishEntity(game.level, 'actor', proto) end)
    if not ok then reason='resolve-error: '..tostring(actor); actor=proto; counts.errors=counts.errors+1
    else counts.resolved=counts.resolved+1 end
   else
    actor={}; reason='not-in-active-zone-list; room specialList may still load it'
    counts.unavailable=counts.unavailable+1
   end
   local token
   if ok then
    token, reason = Tokens.explain(actor, actor._checker_token and actor._checker_token.display)
    if token then counts.covered=counts.covered+1 else counts.fallback=counts.fallback+1 end
   end
   local range = actor.level_range or (proto and proto.level_range) or {}
   local values = {game.zone.short_name,layout,game.level.level,turn,c.scope,c.name or c.define_as,
    actor.name,actor.type,actor.subtype,actor.define_as,proto and proto.rank,actor.rank,
    range[1],range[2],actor.image,list(actor.add_mos),list(actor.add_displays),actor.shader,
    list(actor.anim),list(actor.textures),list(actor.shader_auras),
    actor.replace_display and 'present' or '',actor.moddable_tile and 'present' or '',token,
    token and 'covered' or ok and 'fallback' or proto and 'unresolved' or 'unavailable',reason,c.source}
   local row = {}
   for i=1,#fields do row[i]=clean(values[i]) end
   file:write(table.concat(row,'\t')..'\n')
  end
 end
 file:close()
 assert(game.turn == turn and game.player == player and player.x == px and player.y == py
  and player.life == life, 'audit changed world turn or player state')
 print('[KorPulInventory]', layout, 'level', game.level.level, 'turn', turn, 'path', path,
  'resolved', counts.resolved, 'unavailable', counts.unavailable, 'errors', counts.errors,
  'covered', counts.covered, 'fallback', counts.fallback)
 counts.path, counts.layout = path, layout
 return counts
end

return M
