"""Read-only dead-asset audit: which shipped images can the renderer request?

The reachable set is *derived from the runtime source*, never transcribed by
hand, so a renderer change cannot silently leave this audit lying:

* forest terrain -- the real `terrainImage` / `terrain` / `waterMask` bodies are
  sliced out of `overload/mod/class/CheckerTerrain.lua` and executed in Lua.
  `terrain` and `waterMask` are swapped out through `debug.setupvalue`, so the
  renderer's own path arithmetic runs over an enumerated identity/mask domain.
* Kor'Pul terrain -- the real `M.assetPath` is executed, over the (kind,
  orientation) pairs that `M.classify` can return, rebuilt from the module's own
  `identities` / `doors` / `open` / `stairs` tables. The neighbour-mask width
  comes from the module's own `offsets` table.
* creature tokens -- `CheckerTokens.image()` is called for every id in the
  module's own `by_id` catalogue.
* player tokens -- `CheckerPlayerTokens.lua` is executed with a real `fs.exists`
  and `loadfile` bound to this repo's actual `data/` tree (same manifest-gate
  logic the runtime uses, over the real `data/player-token-manifest.lua`), then
  `M.image()` is called for every family the module's own `M.available` (built
  from that real manifest) approves.
* overlay masks -- the `'_name'` literals and `'_prefix'..var` concatenations are
  scanned out of `superload/mod/class/Actor.lua`; the suffix domains come from
  calling `CheckerTokenStyle.relation()` and `.rankBadge()`.

Every structural assumption is asserted against the source. If a slice marker,
an upvalue, a prefix variable or a manifest count moves, this tool raises rather
than reporting a smaller reachable set.

Anything only referenced by a literal `checker-revised+<file>.png` elsewhere in
the repository (for example the offline fixture's demonstration player token) is
reported as referenced, not dead.

Usage:
    python3 tools/audit_dead_assets.py            # human readable report
    python3 tools/audit_dead_assets.py --json     # machine readable
    python3 tools/audit_dead_assets.py --check    # exit 1 if dead assets exist
"""
from pathlib import Path
import argparse
import json
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
LUA = 'lua5.1'
GFX = ROOT / 'data/gfx'
TERRAIN = ROOT / 'overload/mod/class/CheckerTerrain.lua'
OPTIONS = ROOT / 'overload/mod/class/CheckerOptions.lua'
TOKENS = ROOT / 'overload/mod/class/CheckerTokens.lua'
PLAYER_TOKENS = ROOT / 'overload/mod/class/CheckerPlayerTokens.lua'
STYLE = ROOT / 'overload/mod/class/CheckerTokenStyle.lua'
ACTOR = ROOT / 'superload/mod/class/Actor.lua'
DIALOG = ROOT / 'overload/mod/dialogs/CheckerRankColor.lua'
PREFIX = 'checker-revised+'
# Enough cells to cover every (x+y)%2 parity and every (x*17+y*7)%3 variant.
CELLS = 12


class AuditError(RuntimeError):
    pass


def lua(chunk):
    done = subprocess.run([LUA, '-'], input=chunk, cwd=ROOT,
                          capture_output=True, text=True)
    if done.returncode != 0:
        raise AuditError('lua harness failed:\n' + done.stderr.strip())
    return done.stdout


def slice_source(text, start, stop):
    """Return the source between two anchored line markers, exclusive of stop."""
    lines = text.splitlines()
    begin = end = None
    for index, line in enumerate(lines):
        if line.startswith(start) and begin is None:
            begin = index
        elif begin is not None and line.startswith(stop):
            end = index
            break
    if begin is None or end is None:
        raise AuditError(f'source markers not found: {start!r} .. {stop!r}')
    return '\n'.join(lines[begin:end])


def terrain_identities(text):
    """The closed set of strings the renderer's `terrain()` can return."""
    body = slice_source(text, 'local function terrain(', 'local dirs=')
    # The Sandworm classifier is a separate exact-id family in this source
    # span. Its string literals are not forest/rock return identities.
    sand_start = body.find('-- Sandworm Lair shares sand.lua')
    sand_end = body.find('-- Norgos imports mountain.lua')
    if sand_start < 0 or sand_end < sand_start:
        raise AuditError('Sandworm classifier slice markers not found')
    body = body[:sand_start] + body[sand_end:]
    found = []
    for statement in re.findall(r'\breturn\b(.*)', body):
        found.extend(value for value in re.findall(r"'([^']*)'", statement)
                     if value == value.lower())
    rocky = re.search(r'local rockyExits=\{(.*?)\n\}', body, re.S)
    if rocky:
        found.extend(re.findall(r"\{\s*'(stairs-[a-z]+)'", rocky[1]))
    if not found:
        raise AuditError('no terrain identities recovered from terrain()')
    return sorted(v for v in set(found) if not v.startswith(('gloom-', 'ladder-')))


def terrain_modes(text):
    match = re.search(r'local modes\s*=\s*\{([^}]*)\}', text)
    if not match:
        raise AuditError('terrain mode table not found in CheckerOptions.lua')
    modes = re.findall(r'(\w+)\s*=\s*true', match[1])
    if not modes:
        raise AuditError('no terrain modes recovered')
    return modes


def quote(values):
    return '{' + ','.join("'%s'" % v for v in values) + '}'


BATCH4_KINDS = {
    # S2: South Beach's BEACH_UP (forest world exit art); Keepsake's cave doors
    # (S2 cave door tiles) and cave marker post (board cave floor + native post).
    'beach': ('sand', 'umbrella', 'basket', 'grass', 'tree', 'road', 'deep', 'exit'),
    'meadow': ('cave-floor', 'cave-wall', 'cave-ladder-up', 'cave-ladder-down', 'cave-ladder-world',
               'grass', 'flower', 'hardtree', 'deep', 'exit', 'stew',
               'cave-door-closed-horizontal', 'cave-door-closed-vertical', 'cave-door-open-horizontal',
               'cave-door-open-vertical', 'cave-marker'),
    'caldera': ('floor', 'tree', 'exit-up', 'exit-down', 'exit-world', 'poison', 'wall', 'rock-ground'),
    # TW1/TW2 static towns (townKind): forest kinds plus Last Hope's hard
    # mountain (Daikara mountain-wall masks) and lore statues (board grass).
    'town-last-hope': ('grass', 'flower', 'tree', 'road', 'deep', 'exit', 'mountain', 'statue'),
    # TW3: Zigur sand shore (beach sand), lava pit (burnt lava masks) and post
    # sign; Angolwen fountain basin (deep masks) and rocks; Iron Council
    # crystal walls (crystal-wall masks).
    # TW7: town roads draw board stone slabs (refined/town/road); Zigur and
    # Angolwen FIELDS1-4 the board crop field; Gates palms the S6 board palm.
    'town-zigur': ('grass', 'tree', 'road', 'deep', 'exit', 'sand', 'lava', 'post', 'fields'),
    'town-angolwen': ('grass', 'tree', 'road', 'exit', 'mountain', 'fountain', 'rock', 'fields'),
    'town-iron-council': ('crystal',),
    # TW4: Shatur snow glades (snow family ground and trees); Point Zero cold
    # forest (snow pines) and its outer-space platform (void family).
    'town-shatur': ('snow-ground', 'snow-tree'),
    'town-point-zero': ('cold-tree', 'void-space', 'void-rocks', 'void-rift', 'void-floor'),
    # TW5: Gates of Morning forest kinds, beach sand and the Sunwall mountain
    # (golden-mountain wall masks).
    'town-gates-of-morning': ('grass', 'tree', 'road', 'deep', 'exit', 'sand', 'gold-mountain', 'palm'),
    # TW6: Irkkk jungle (Caldera floor/tree/exit art), lake, and the bamboo
    # huts (bamboo wall masks, hut floor, cooking pit floor, four door states).
    'town-irkkk': ('jungle-grass', 'jungle-tree', 'jungle-exit', 'deep', 'hut-floor', 'hut-cooking', 'hut-wall',
                   'hut-door-h', 'hut-door-v', 'hut-door-h-open', 'hut-door-v-open'),
    # S5: zones on existing families. Valley of the Moon: forest grass/trees,
    # Caldera mountain-wall and poison masks, board deep water, moonstones and
    # Fearscape portals (props over board grass); Ring of Blood: beach sand and
    # burnt lava masks; the ambush glade, Tannen's grove/pools and Derth's arena.
    'dreadfell-ambush': ('grass', 'flower', 'tree', 'exit'),
    'valley-moon': ('grass', 'flower', 'tree', 'poison', 'deep', 'wall', 'moonstone', 'portal'),
    'tannen-tower': ('grass', 'tree', 'deep'),
    'ring-of-blood': ('sand', 'lava'),
    'arena-unlock': ('grass', 'tree', 'sand'),
    # S6: Eruan beach sand, the new board palm (plain/mirrored), board deep
    # water, its own sand exits and hard mountain (Daikara masks); Gorbat
    # Pride beach sand, Daikara mountain masks, deep water, the TW6 bamboo
    # roosts (wall masks, floor, four door states) and the loose rock door.
    'eruan': ('sand', 'palm', 'deep', 'exit-world', 'exit-up', 'exit-down', 'mountain'),
    'gorbat-pride': ('sand', 'mountain', 'deep', 'hut-wall', 'hut-floor', 'hut-door-h', 'hut-door-v',
                     'hut-door-h-open', 'hut-door-v-open', 'rock-door'),
    # S10a: the board slime family (floor, wall masks, stairs, creep masks over
    # board stone) in Slime Tunnels and Sludgenest (plus Caldera jungle), and
    # Grushnak's underground floor (board stone), gloom-plain thicket masks,
    # training dummy (board stone + native layer) and slime-pit entrance.
    'slime-tunnels': ('slime-floor', 'slime-wall', 'slime-up'),
    'sludgenest': ('slime-floor', 'slime-wall', 'slime-up', 'slime-down', 'jungle-grass', 'jungle-tree', 'jungle-exit'),
    'grushnak-pride': ('under-floor', 'creep', 'thicket', 'dummy', 'slime-down'),
    # S10b: Vor Pride's board gothic family (three floor variants, wall masks,
    # four door states, flat exits on the Kor'Pul stair pieces, books over
    # board floor) and its burnt yard (Spellblaze floor/tree/exit-down), plus
    # the (unobserved) forest/water cells on their existing art.
    'vor-pride': ('gothic-floor', 'gothic-book', 'gothic-wall', 'gothic-door-closed', 'gothic-door-closed-h',
                  'gothic-door-closed-v', 'gothic-door-open', 'gothic-door-open-h', 'gothic-door-open-v',
                  'gothic-exit-up', 'gothic-exit-down', 'gothic-exit-world', 'burnt-floor', 'burnt-tree',
                  'burnt-exit-down', 'deep', 'tree', 'grass'),
}


def batch4_kinds(text):
    """Per-family kind domain for batch4Image, checked against the classifiers.

    Every lowercase literal returned by a batch 4 classifier must belong to some
    family domain, so a new kind cannot ship without being enumerated here.
    """
    body = slice_source(text, '-- Batch 4 (Southern Beach', 'local function batch4Image(')
    returned = set()
    for statement in re.findall(r'\breturn\b(.*)', body):
        # Returned values only: a literal right after `return` or `and`, not a
        # string concatenation prefix, comparison operand or field name.
        returned.update(re.findall(r"(?:^\s*|\band\s+)'([a-z-]+)'(?!\s*\.\.)", statement))
    for table in re.findall(r"local jungleExits=\{(.*?)\n\}", body, re.S):
        returned.update(re.findall(r"=\{'([a-z-]+)'", table))
    cave = {'floor', 'wall', 'ladder-up', 'ladder-down', 'ladder-world'}  # caveTerrain(), prefixed 'cave-'
    known = set().union(*BATCH4_KINDS.values()) | cave | {'mountain-wall'}
    unknown = returned - known
    if unknown:
        raise AuditError(f'batch 4 classifier returns unenumerated kinds {sorted(unknown)}')
    if "return img('refined/caldera/'..t..parity)" not in text or "local function batch4Image(" not in text:
        raise AuditError('batch 4 renderer reachability contract changed')
    return '{' + ','.join(f"[{k!r}]={{{','.join(repr(v) for v in vs)}}}" for k, vs in BATCH4_KINDS.items()) + '}'


BATCH5_KINDS = {
    'scorch': ('lava', 'lava-floor', 'lava-wall'),
    'shertul': ('floor', 'wall'),
    'rakshor': ('floor', 'wall', 'door-closed', 'door-open', 'stairs-up', 'stairs-down', 'stairs-exit', 'exit-world'),
}


def batch5_kinds(text):
    """Per-family kind domain for batch5Image, checked against the classifiers."""
    body = slice_source(text, '-- Batch 5 (Charred Scar', 'local function batch5Image(')
    returned = set()
    for statement in re.findall(r'\breturn\b(.*)', body):
        returned.update(re.findall(r"(?:^\s*|\band\s+)'([a-z-]+)'(?!\s*\.\.)", statement))
    unknown = returned - set().union(*BATCH5_KINDS.values())
    if unknown:
        raise AuditError(f'batch 5 classifier returns unenumerated kinds {sorted(unknown)}')
    if "return img('refined/shertul/floor'..parity)" not in text or "local function batch5Image(" not in text:
        raise AuditError('batch 5 renderer reachability contract changed')
    return '{' + ','.join(f"{k}={{{','.join(repr(v) for v in vs)}}}" for k, vs in BATCH5_KINDS.items()) + '}'


def renderer_paths(identities, modes):
    """Run the renderer's own path arithmetic over the enumerated domain."""
    text = TERRAIN.read_text()
    forest = slice_source(text, 'local function img(', 'local function applyForest(')
    korpul = slice_source(text, "local source=", 'function M.stairsReady(')
    batch4_domain = batch4_kinds(text)
    batch5_domain = batch5_kinds(text)
    harness = f"""
local M={{}}
local Map={{TERRAIN=1}}
{forest}
{korpul}
local function rebind(f,name,value)
 local i=1
 while true do
  local key=debug.getupvalue(f,i)
  if not key then error('upvalue not found: '..name,0) end
  if key==name then debug.setupvalue(f,i,value) return end
  i=i+1
 end
end
-- Feed the identity straight through and pin the neighbour mask, so the real
-- terrainImage body decides every filename it can ever ask for.
local mask=0
rebind(terrainImage,'terrain',function(g) return g end)
rebind(terrainImage,'rockTerrain',function(g) return g end)
rebind(terrainImage,'lavaTerrain',function(g) return g end)
rebind(terrainImage,'waterMask',function() return mask end)
local water_masks=2^#dirs-1
local cx,cy=0,0
local fake_map=setmetatable({{}}, {{__call=function(_,x,y)
 for i,d in ipairs(dirs) do
  if x==cx+d[1] and y==cy+d[2] and mask%(2^i)>=2^(i-1) then return 'mountain-wall' end
 end
 return 'rock-ground'
end}})
fake_map.w=100;fake_map.h=100
for _,mode in ipairs({quote(modes)}) do
 for _,identity in ipairs({quote(identities)}) do
  for m=0,water_masks do
   mask=m
   for x=0,{CELLS - 1} do for y=0,{CELLS - 1} do
    local daikara=identity=='rock-ground' or identity=='mountain-wall' or identity=='lava-floor'
    local rock=daikara and 'daikara' or (identity=='snow-ground' or identity=='snow-tree' or identity:match('^stairs%-')) and 'norgos'
    cx,cy=x+1,y+1
    local path=terrainImage(daikara and fake_map or nil,cx,cy,identity,mode,false,rock)
    if path then print('forest\\t'..mode..'\\t'..path) end
    if identity:match('^stairs%-') or identity=='snow-tree' then
     local daikara_stair=terrainImage(nil,cx,cy,identity,mode,false,'daikara')
     if daikara_stair then print('forest\\t'..mode..'\\t'..daikara_stair) end
    end
   end end
  end
 end
end
rebind(terrainImage,'gloomTerrain',function(g) return g end)
local neighbor_identity
local gloom_map=setmetatable({{}}, {{__call=function(_,x,y)
 for i,d in ipairs(dirs) do
  if x==cx+d[1] and y==cy+d[2] and mask%(2^i)>=2^(i-1) then return neighbor_identity end
 end
 return 'gloom-floor'
end}})
gloom_map.w=100;gloom_map.h=100
for _,skin in ipairs({{'gloomy','dreamy','plain'}}) do
 for _,mode in ipairs({quote(modes)}) do
  for _,identity in ipairs({{'gloom-floor','gloom-creep','gloom-wall','ladder-up','ladder-down','ladder-world'}}) do
   neighbor_identity=identity
   for m=0,15 do
    mask=m
    for x=0,3 do for y=0,3 do
     cx,cy=x+10,y+10
     local path=terrainImage(gloom_map,cx,cy,identity,mode,false,nil,skin)
     if path then print('forest\\t'..mode..'\\t'..path) end
     if skin=='plain' then
      -- Orc Breeding Pit draws the plain suite with its own wall copy.
      local pit=terrainImage(gloom_map,cx,cy,identity,mode,false,nil,skin,nil,nil,nil,nil,nil,nil,'orc-breeding-pit')
      if pit then print('forest\\t'..mode..'\\t'..pit) end
     end
    end end
   end
  end
 end
end
rebind(terrainImage,'sandTerrain',function(g) return g end)
rebind(terrainImage,'burntTerrain',function(g) return g end)
rebind(terrainImage,'voidTerrain',function(g) return g end)
local burnt_map=setmetatable({{}}, {{__call=function(_,x,y)
 for i,d in ipairs(dirs) do
  if x==cx+d[1] and y==cy+d[2] and mask%(2^i)>=2^(i-1) then return 'lava' end
 end
 return 'floor'
end}})
burnt_map.w=100;burnt_map.h=100
rebind(terrainImage,'crystalTerrain',function(g) return g end)
rebind(terrainImage,'caveTerrain',function(g) return type(g)=='table' and g.kind or g end)
local sand_map=setmetatable({{}}, {{__call=function(_,x,y)
 for i,d in ipairs(dirs) do
  if x==cx+d[1] and y==cy+d[2] and mask%(2^i)>=2^(i-1) then return 'wall' end
 end
 return 'floor'
end}})
sand_map.w=100;sand_map.h=100
for _,mode in ipairs({quote(modes)}) do
 for _,identity in ipairs({{'floor','wall','ladder-up','ladder-down','ladder-world'}}) do
  for m=0,15 do
   mask=m
   for x=0,3 do for y=0,3 do
    cx,cy=x+10,y+10
    local path=terrainImage(sand_map,cx,cy,identity,mode,false,nil,nil,true)
    if path then print('forest\t'..mode..'\t'..path) end
   end end
  end
 end
end
for _,mode in ipairs({quote(modes)}) do
 for _,identity in ipairs({{'floor','tree','lava','exit-up','exit-down','exit-world'}}) do
  for m=0,15 do
   mask=m
   for x=0,1 do for y=0,1 do
    cx,cy=x+10,y+10
    local path=terrainImage(burnt_map,cx,cy,identity,mode,false,nil,nil,nil,nil,nil,nil,true)
    if path then print('forest\t'..mode..'\t'..path) end
   end end
  end
 end
end
local void_map=setmetatable({{}}, {{__call=function(_,x,y)
 for i,d in ipairs(dirs) do
  if x==cx+d[1] and y==cy+d[2] and mask%(2^i)>=2^(i-1) then return neighbor_identity end
 end
 return 'other'
end}})
void_map.w=100;void_map.h=100
for _,mode in ipairs({quote(modes)}) do
 for _,identity in ipairs({{'floor','rift','rocks','space'}}) do
  neighbor_identity=identity
  for m=0,15 do
   mask=m
   for x=0,1 do for y=0,1 do
    cx,cy=x+10,y+10
    local path=terrainImage(void_map,cx,cy,identity,mode,false,nil,nil,nil,nil,nil,nil,nil,true,'abashed-expanse')
    if path then print('forest\t'..mode..'\t'..path) end
   end end
  end
 end
end
for _,mode in ipairs({quote(modes)}) do
 for _,identity in ipairs({{'floor','wall','ladder-up','ladder-down','ladder-world'}}) do
  for m=0,15 do
   mask=m
   for x=0,3 do for y=0,3 do
    cx,cy=x+10,y+10
    local path=terrainImage(sand_map,cx,cy,identity,mode,false,nil,nil,nil,nil,true)
    if path then print('forest\t'..mode..'\t'..path) end
   end end
  end
 end
end
for _,mode in ipairs({quote(modes)}) do
 for n=8,18 do
  local g={{kind='floor',define_as='CAVEFLOOR'..n}}
  for x=0,1 do for y=0,1 do
   local path=terrainImage(sand_map,x+10,y+10,g,mode,false,nil,nil,nil,nil,true)
   if path then print('forest\t'..mode..'\t'..path) end
  end end
 end
end
for _,mode in ipairs({quote(modes)}) do
 for _,identity in ipairs({{'floor','wall','ladder-up','ladder-down','ladder-world'}}) do
  for m=0,15 do
   mask=m
   for x=0,3 do for y=0,3 do
    cx,cy=x+10,y+10
    local path=terrainImage(sand_map,cx,cy,identity,mode,false,nil,nil,nil,true)
    if path then print('forest\t'..mode..'\t'..path) end
   end end
  end
 end
end
-- Batch 4 families: the real batch4Image path arithmetic over each family's
-- kind domain (BATCH4_KINDS, cross-checked against the classifier source).
rebind(batch4Image,'batch4Kind',function(g) return type(g)=='table' and g.kind or g end)
local b4_neighbor
local b4_map=setmetatable({{}}, {{__call=function(_,x,y)
 for i,d in ipairs(dirs) do
  if x==cx+d[1] and y==cy+d[2] and mask%(2^i)>=2^(i-1) then return b4_neighbor end
 end
 return 'other'
end}})
b4_map.w=100;b4_map.h=100
for family,kinds in pairs({batch4_domain}) do
 for _,mode in ipairs({quote(modes)}) do
  for _,kind in ipairs(kinds) do
   b4_neighbor={{kind=kind,define_as=''}}
   for m=0,15 do
    mask=m
    for x=0,5 do for y=0,5 do
     cx,cy=x+10,y+10
     local path=terrainImage(b4_map,cx,cy,{{kind=kind,define_as=''}},mode,false,nil,nil,nil,nil,nil,nil,nil,nil,nil,nil,nil,nil,family)
     if path then print('forest\t'..mode..'\t'..path) end
    end end
   end
   if kind=='cave-floor' then for n=8,18 do for x=0,1 do for y=0,1 do
    local path=terrainImage(b4_map,x+10,y+10,{{kind=kind,define_as='CAVEFLOOR'..n}},mode,false,nil,nil,nil,nil,nil,nil,nil,nil,nil,nil,nil,nil,family)
    if path then print('forest\t'..mode..'\t'..path) end
   end end end end
  end
 end
end
-- Batch 5 families: the real batch5Image path arithmetic over each kind.
rebind(batch5Image,'batch5Kind',function(g) return type(g)=='table' and g.kind or g end)
for family,kinds in pairs({batch5_domain}) do
 for _,mode in ipairs({quote(modes)}) do
  for _,kind in ipairs(kinds) do
   b4_neighbor={{kind=kind,define_as=''}}
   for m=0,15 do
    mask=m
    for x=0,1 do for y=0,1 do
     cx,cy=x+10,y+10
     local path=terrainImage(b4_map,cx,cy,{{kind=kind,define_as=''}},mode,false,nil,nil,nil,nil,nil,nil,nil,nil,nil,nil,nil,nil,nil,family)
     if path then print('forest\t'..mode..'\t'..path) end
    end end
   end
  end
 end
end
-- classify() returns (kind, orientation); rebuild that pairing from the very
-- tables classify reads, rather than from a transcribed list of kinds.
local wall_masks=2^#offsets-1
local combos={{}}
for id,kind in pairs(identities) do
 if kind~='old-wall' then
 local orientation
 if doors[id] then orientation=doors[id][3] elseif open[id] then orientation=open[id][2] end
 combos[kind..'\\0'..(orientation or '')]={{kind,orientation}}
 end
end
for _,combo in pairs(combos) do
 for mask=0,wall_masks do for parity=0,1 do
  for x=0,{CELLS - 1} do for y=0,{CELLS - 1} do
   print('korpul\\t'..M.assetPath(combo[1],combo[2],mask,parity,x,y))
  end end
 end end
end
-- M.render draws a stair foreground as img('refined/korpul/'..record.kind).
for _,stair in pairs(stairs) do print('korpul-stair\\t'..img('refined/korpul/'..stair.kind)) end
"""
    forest_paths, korpul_paths, stair_paths = {}, set(), set()
    for line in lua(harness).splitlines():
        parts = line.split('\t')
        if parts[0] == 'forest':
            forest_paths.setdefault(parts[1], set()).add(parts[2])
        elif parts[0] == 'korpul':
            korpul_paths.add(parts[1])
        elif parts[0] == 'korpul-stair':
            stair_paths.add(parts[1])
    if not forest_paths or not korpul_paths or not stair_paths:
        raise AuditError('renderer harness produced no paths')
    # Cross-check the stair foregrounds against the module's own gate table.
    gated = set(re.findall(r"\['(checker-revised\+refined/korpul/stairs-[a-z]+\.png)'\]=true", text))
    if gated != stair_paths:
        raise AuditError(f'stair foreground gate {sorted(gated)} != rendered {sorted(stair_paths)}')
    return forest_paths, korpul_paths, stair_paths


def token_paths():
    out = lua(f"""
local Tokens=assert(loadfile('{TOKENS.relative_to(ROOT)}'))()
local Style=assert(loadfile('{STYLE.relative_to(ROOT)}'))()
for id in pairs(Tokens.by_id) do print('token\\t'..Tokens.image(id)) end
local actor={{}}
local seen={{}}
for _,reaction in ipairs{{-1,0,1}} do seen[Style.relation(actor,{{}},reaction)]=true end
seen[Style.relation(actor,actor,0)]=true
for kind in pairs(seen) do print('relation\\t'..kind) end
local badges={{}}
for i=0,200 do local badge=Style.rankBadge(i/10) if badge then badges[badge]=true end end
for badge in pairs(badges) do print('badge\\t'..badge) end
""")
    tokens, relations, badges = set(), set(), set()
    for line in out.splitlines():
        kind, value = line.split('\t')
        {'token': tokens, 'relation': relations, 'badge': badges}[kind].add(value)
    if not tokens or not relations or not badges:
        raise AuditError('token harness produced an empty domain')
    return tokens, sorted(relations), sorted(badges)


def player_token_paths():
    """Run CheckerPlayerTokens.lua for real over the real player-token manifest.

    `fs.exists` and `loadfile` are bound to this repo's actual `data/` tree
    (mapping the virtual `/data-checker-revised/...` prefix onto it) instead of
    the test suite's in-memory stub, so this reads the manifest that will
    actually ship, not a fixture.
    """
    out = lua(f"""
local function resolve(path)
 local rest=path:match('^/data%-checker%-revised/(.*)$')
 return rest and ('data/'..rest) or path
end
local real_loadfile=loadfile
fs={{exists=function(path)
 local f=io.open(resolve(path),'rb')
 if f then f:close() return true end
 return false
end}}
loadfile=function(path,...) return real_loadfile(resolve(path),...) end
local P=assert(real_loadfile('{PLAYER_TOKENS.relative_to(ROOT)}'))()
for family in pairs(P.available) do print('player\\t'..P.image('player:'..family)) end
""")
    tokens = set()
    for line in out.splitlines():
        kind, value = line.split('\t')
        if kind != 'player':
            raise AuditError(f'unexpected player-token harness output: {line!r}')
        tokens.add(value)
    return tokens


def overlay_masks(relations, badges):
    """Derive the `_`-prefixed UI masks from the overlay source itself."""
    text = ACTOR.read_text()
    match = re.search(r"'(checker-revised\+[a-z/]+/)'\s*\.\.\s*name\s*\.\.\s*'(\.png)'", text)
    if not match:
        raise AuditError('overlay texture path format not found in Actor.lua')
    head, tail = match[1], match[2]
    suffixes = {'kind': relations, 'badge': badges}
    literals, prefixes = set(), set()
    for name, _, variable in re.findall(r"'(_[\w-]*)'(\s*\.\.\s*(\w+))?", text):
        if variable:
            if variable not in suffixes:
                raise AuditError(f'unknown overlay suffix variable {variable!r} for {name!r}')
            prefixes.add((name, variable))
        else:
            literals.add(name)
    if not literals or not prefixes:
        raise AuditError('no overlay masks recovered from Actor.lua')
    names = set(literals)
    for prefix, variable in prefixes:
        names.update(prefix + suffix for suffix in suffixes[variable])
    # The colour dialog previews the same masks; it must not invent new ones.
    dialog = DIALOG.read_text()
    for name, _, variable in re.findall(r"'(_[\w-]*)'(\s*\.\.\s*(\w+))?", dialog):
        if variable:
            if not any(name == prefix for prefix, _ in prefixes):
                raise AuditError(f'dialog requests unknown mask family {name!r}')
        elif name not in literals:
            raise AuditError(f'dialog requests unknown mask {name!r}')
    return {head + name + tail for name in names}


def to_relative(path):
    if not path.startswith(PREFIX) or not path.endswith('.png'):
        raise AuditError(f'unexpected image path {path!r}')
    return 'data/gfx/' + path[len(PREFIX):]


def literal_references():
    """Any `checker-revised+<file>.png` literal anywhere in the repository."""
    found = {}
    for source in sorted(ROOT.rglob('*.lua')):
        if '/.git/' in source.as_posix():
            continue
        relative = source.relative_to(ROOT).as_posix()
        for match in re.findall(r"checker-revised\+([\w./-]+\.png)", source.read_text()):
            found.setdefault('data/gfx/' + match, set()).add(relative)
    return found


def manifest_entries(path, pattern):
    return set(re.findall(pattern, path.read_text()))


def audit():
    identities = terrain_identities(TERRAIN.read_text())
    modes = terrain_modes(OPTIONS.read_text())
    forest, korpul, stairs = renderer_paths(identities, modes)
    tokens, relations, badges = token_paths()
    masks = overlay_masks(relations, badges)
    player_tokens = player_token_paths()

    reachable = {}
    for mode, paths in forest.items():
        for path in paths:
            reachable.setdefault(to_relative(path), set()).add('forest:' + mode)
    for path in korpul:
        reachable.setdefault(to_relative(path), set()).add('korpul:floor-wall-door')
    for path in stairs:
        reachable.setdefault(to_relative(path), set()).add('korpul:stair-foreground')
    maze_source = TERRAIN.read_text()
    if "img('refined/maze/'..record.kind" not in maze_source or "M.mazeAssets.files[path]" not in maze_source:
        raise AuditError('Maze renderer reachability contract changed')
    maze = {f'data/gfx/refined/maze/old-wall-{mask}-{parity}.png'
            for mask in range(16) for parity in range(2)}
    maze.update(f'data/gfx/refined/maze/cracks-0-{parity}.png' for parity in range(2))
    for path in maze:
        reachable.setdefault(path, set()).add('maze:wall-chasm')
    if ("img('refined/conclave/wall-'..M.mask(m,x,y)..'-'..((x+y)%2))" not in maze_source or
            "M.variant(game.zone)=='CONCLAVE_VAULT'" not in maze_source):
        raise AuditError('Conclave wall renderer reachability contract changed')
    conclave = {f'data/gfx/refined/conclave/wall-{mask}-{parity}.png'
                for mask in range(16) for parity in range(2)}
    for path in conclave:
        reachable.setdefault(path, set()).add('conclave:wall')
    # S8: the darker Kor'Pul brick/door-jamb set (listed stone zones) and the
    # Fearscape basalt, both behind their own manifests.
    if ("path:gsub('%+refined/korpul/','+refined/korpul-dark/',1)" not in maze_source or
            "img('refined/scorch-dark/wall-'..mask('lava-wall')..'-'..parity)" not in maze_source):
        raise AuditError('S8 dark wall renderer reachability contract changed')
    korpul_dark = {f'data/gfx/refined/korpul-dark/{kind}-{mask}-{parity}.png'
                   for kind in ('wall', 'door-closed-horizontal', 'door-closed-vertical',
                                'door-open-horizontal', 'door-open-vertical')
                   for mask in range(16) for parity in range(2)}
    scorch_dark = {f'data/gfx/refined/scorch-dark/wall-{mask}-{parity}.png'
                   for mask in range(16) for parity in range(2)}
    for path in korpul_dark:
        reachable.setdefault(path, set()).add('korpul-dark:wall-door')
    for path in scorch_dark:
        reachable.setdefault(path, set()).add('scorch-dark:wall')
    # S12: hazard lava (three variants) and stone-kerb deep water, stone
    # adapter, behind their own manifest.
    if ("img('refined/hazard/lava-'..({'a','b','c'})[((x*17+y*7)%3)+1]..'-'..mask..'-'..p)" not in maze_source or
            "img('refined/hazard/deep-'..mask..'-'..p)" not in maze_source or
            "M.hazardAssets.files[path]" not in maze_source):
        raise AuditError('S12 hazard renderer reachability contract changed')
    hazard = {f'data/gfx/refined/hazard/lava-{v}-{mask}-{parity}.png'
              for v in 'abc' for mask in range(16) for parity in range(2)}
    hazard.update(f'data/gfx/refined/hazard/deep-{mask}-{parity}.png' for mask in range(16) for parity in range(2))
    for path in hazard:
        reachable.setdefault(path, set()).add('hazard:lava-deep')
    # S17: Dreamscape cloud floor (three variants x 16 masks) and dream void
    # (two variants), forest adapter, behind their own manifest.
    if ("img('refined/dream/cloud-'..({'a','b','c'})[((x*17+y*7)%3)+1]..'-'..mask..'-'..parity)" not in maze_source or
            "img('refined/dream/void-'..({'a','b'})[((x*17+y*7)%2)+1]..'-'..parity)" not in maze_source or
            "M.dreamAssets.files[p]" not in maze_source):
        raise AuditError('S17 dream renderer reachability contract changed')
    dream = {f'data/gfx/refined/dream/cloud-{v}-{mask}-{parity}.png'
             for v in 'abc' for mask in range(16) for parity in range(2)}
    dream.update(f'data/gfx/refined/dream/void-{v}-{parity}.png' for v in 'ab' for parity in range(2))
    for path in dream:
        reachable.setdefault(path, set()).add('dream:cloud-void')
    if ("img('refined/underwater/wall-'..mask..'-'..parity)" not in maze_source or
            "img('refined/underwater/'..t..parity)" not in maze_source):
        raise AuditError('underwater renderer reachability contract changed')
    underwater = {f'data/gfx/refined/underwater/wall-{mask}-{parity}.png'
                  for mask in range(16) for parity in range(2)}
    underwater.update(f'data/gfx/refined/underwater/{stem}{parity}.png'
                      for stem in ('floor', 'door-closed', 'door-open', 'stairs-up', 'stairs-down', 'stairs-world')
                      for parity in range(2))
    # S4/T1: the exact air bubble (M.bubbleKind) through the same renderer.
    if "then return M.bubbleKind(g) end" not in maze_source or "return 'bubble' end" not in maze_source:
        raise AuditError('underwater bubble reachability contract changed')
    underwater.update(f'data/gfx/refined/underwater/bubble{parity}.png' for parity in range(2))
    for path in underwater:
        reachable.setdefault(path, set()).add('underwater:floor-wall-door-stair')
    if "zoneName=='abashed-expanse' and abashedTreeKind(g)" not in maze_source:
        raise AuditError('Abashed tree renderer reachability contract changed')
    for mask in range(16):
        for parity in range(2):
            path=f'data/gfx/refined/void/rocks-tree-{mask}-{parity}.png'
            reachable.setdefault(path, set()).add('void:rock-tree')
    if "return img('refined/graveyard/'..t..parity)" not in maze_source:
        raise AuditError('graveyard prop renderer reachability contract changed')
    for stem in ('grave', 'coffin', 'coffin-open', 'mausoleum'):
        for parity in range(2):
            path=f'data/gfx/refined/graveyard/{stem}{parity}.png'
            reachable.setdefault(path, set()).add('graveyard:prop')
    for path in tokens:
        reachable.setdefault(to_relative(path), set()).add('token:creature')
    for path in masks:
        reachable.setdefault(to_relative(path), set()).add('token:overlay-mask')
    for path in player_tokens:
        reachable.setdefault(to_relative(path), set()).add('token:player')
    # Both persisted styles can reach each procedural aura mask.
    aura_source = TERRAIN.read_text()
    aura_block = aura_source.split('local auraEffects={', 1)[1].split('\n}', 1)[0]
    aura_colors = set(re.findall(r"\['[\w-]+'\]='([\w-]+)'", aura_block))
    if not aura_colors or "return img('aura-'..kind..'-'..Options.auraStyle())" not in aura_source:
        raise AuditError('aura mask reachability contract changed')
    for color in aura_colors:
        for style in ('subtle', 'moderate'):
            reachable.setdefault(f'data/gfx/aura-{color}-{style}.png', set()).add('terrain:aura-' + style)

    # The Kor'Pul manifests gate the same 196 + 3 files; they must agree.
    manifest = manifest_entries(ROOT / 'data/terrain-korpul-manifest.lua',
                                r"\['checker-revised\+([\w./-]+\.png)'\]=true")
    stair_manifest = manifest_entries(ROOT / 'data/terrain-korpul-stairs-manifest.lua',
                                      r"\['checker-revised\+([\w./-]+\.png)'\]=true")
    manifest_mismatch = sorted(
        {'data/gfx/' + n for n in manifest} ^ {to_relative(p) for p in korpul})
    stair_mismatch = sorted(
        {'data/gfx/' + n for n in stair_manifest} ^ {to_relative(p) for p in stairs})
    maze_manifest = manifest_entries(ROOT / 'data/terrain-maze-manifest.lua',
                                     r"\['checker-revised\+([\w./-]+\.png)'\]=true")
    maze_mismatch = sorted({'data/gfx/' + n for n in maze_manifest} ^ maze)
    conclave_manifest = manifest_entries(ROOT / 'data/terrain-conclave-manifest.lua',
                                         r"\['checker-revised\+([\w./-]+\.png)'\]=true")
    maze_mismatch += sorted({'data/gfx/' + n for n in conclave_manifest} ^ conclave)
    for name, expected in (('terrain-korpul-dark-manifest.lua', korpul_dark), ('terrain-scorch-dark-manifest.lua', scorch_dark),
                           ('terrain-hazard-manifest.lua', hazard), ('terrain-dream-manifest.lua', dream)):
        entries = manifest_entries(ROOT / 'data' / name, r"\['checker-revised\+([\w./-]+\.png)'\]=true")
        maze_mismatch += sorted({'data/gfx/' + n for n in entries} ^ expected)

    literals = literal_references()
    on_disk = {p.relative_to(ROOT).as_posix() for p in GFX.rglob('*') if p.is_file()}

    # Test-only negative fixtures reference paths that never exist; only a file
    # that is really shipped can be kept alive by a literal.
    referenced = {}
    for name, sources in literals.items():
        if name not in reachable and name in on_disk:
            referenced[name] = sorted(sources)

    dead = sorted(on_disk - set(reachable) - set(referenced))
    missing = sorted(set(reachable) - on_disk)

    def size(names):
        return sum((ROOT / n).stat().st_size for n in names if (ROOT / n).is_file())

    groups = {}
    for name in dead:
        stem = re.sub(r'[0-9].*$', '', Path(name).name) or Path(name).name
        key = Path(name).parent.as_posix() + '/' + stem + '*'
        groups.setdefault(key, []).append(name)

    return dict(
        terrain_identities=identities,
        terrain_modes=sorted(modes),
        relation_kinds=relations,
        rank_badges=badges,
        reachable_total=len(reachable),
        reachable_by_origin={origin: sorted(n for n, o in reachable.items() if origin in o)
                             for origin in sorted({o for tags in reachable.values() for o in tags})},
        reachable_bytes=size(reachable),
        referenced_only=referenced,
        on_disk_total=len(on_disk),
        on_disk_bytes=size(on_disk),
        dead_total=len(dead),
        dead_bytes=size(dead),
        dead_groups={k: dict(count=len(v), bytes=size(v)) for k, v in sorted(groups.items())},
        dead_files=dead,
        missing_from_disk=missing,
        korpul_manifest_mismatch=manifest_mismatch,
        korpul_stair_manifest_mismatch=stair_mismatch,
        maze_manifest_mismatch=maze_mismatch,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--json', action='store_true', help='emit the full report as JSON')
    parser.add_argument('--check', action='store_true',
                        help='exit 1 when dead or missing assets exist (packaging regression)')
    args = parser.parse_args()
    report = audit()
    if args.json:
        json.dump(report, sys.stdout, ensure_ascii=False, indent=2, sort_keys=True)
        sys.stdout.write('\n')
    else:
        print(f'terrain identities : {" ".join(report["terrain_identities"])}')
        print(f'terrain modes      : {" ".join(report["terrain_modes"])}')
        print(f'relation / badges  : {" ".join(report["relation_kinds"])} | '
              f'{" ".join(report["rank_badges"])}')
        print()
        for origin, names in report['reachable_by_origin'].items():
            print(f'  reachable {origin:<28} {len(names):>5}')
        print(f'  reachable total                      {report["reachable_total"]:>5}'
              f'  {report["reachable_bytes"] / 1048576:8.2f} MB')
        for name, sources in sorted(report['referenced_only'].items()):
            print(f'  referenced only by {", ".join(sources)}: {name}')
        print(f'  on disk                              {report["on_disk_total"]:>5}'
              f'  {report["on_disk_bytes"] / 1048576:8.2f} MB')
        print()
        if report['dead_total']:
            print('dead assets (no code path can request them):')
            for group, info in report['dead_groups'].items():
                print(f'  {group:<44} {info["count"]:>5}  {info["bytes"] / 1048576:8.2f} MB')
            print(f'  {"total":<44} {report["dead_total"]:>5}'
                  f'  {report["dead_bytes"] / 1048576:8.2f} MB')
        else:
            print('dead assets: none')
        for label, key in (('missing from disk', 'missing_from_disk'),
                           ('kor-pul manifest mismatch', 'korpul_manifest_mismatch'),
                           ('kor-pul stair manifest mismatch', 'korpul_stair_manifest_mismatch'),
                           ('maze manifest mismatch', 'maze_manifest_mismatch')):
            if report[key]:
                print(f'{label}: {report[key]}')
    if args.check and (report['dead_total'] or report['missing_from_disk']
                       or report['korpul_manifest_mismatch']
                       or report['korpul_stair_manifest_mismatch'] or report['maze_manifest_mismatch']):
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
