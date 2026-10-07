-- Geometry contract after the health/shield lanes were removed: the flat piece
-- grows to .92 cell inside a .035 cell faction ring (outer edge .955 cell), at
-- every tile size and size_category. art_occupancy must stay the exporter's.
local script=debug.getinfo(1,'S').source:sub(2)
local root=(script:match('^(.*[/\\])') or './')..'../'
local S=dofile(root..'overload/mod/class/CheckerTokenStyle.lua')
local checks=0
local function eq(a,b,what) assert(math.abs(a-b)<1e-9,what..' ('..a..'~='..b..')');checks=checks+1 end

eq(S.art_occupancy,.86,'art_occupancy must match target_occupancy in tools/export_token.c')
eq(S.token_diameter,.92,'painted disc share of a cell')
eq(S.ring_lane,.035,'faction ring lane as a diameter addition')
eq(S.token_diameter+S.ring_lane,.955,'outer edge share of a cell')

for _,tile in ipairs{48,64,96} do
 for size=1,5 do
  local scale=S.scale(size,tile)
  local g=S.geometry(0,0,tile,scale)
  eq(S.art_occupancy*scale,S.token_diameter,'painted disc is the declared share of a cell')
  eq(g.d/tile,S.token_diameter+S.ring_lane,'mask canvas is exactly the ring outer edge')
  assert(g.d<=tile,'the ring outer edge must fit inside one cell')
  assert(g.cx==tile/2 and g.cy==tile/2,'mask centre')
  checks=checks+2
 end
end
eq(S.scale(1,48),S.scale(4,96),'one board-piece diameter')

-- The faction masks are generated on the ring-outer canvas. Parse the exporter
-- so a geometry change cannot leave the masks behind.
local src=assert(io.open(root..'tools/prepare_runtime_art.py','r')):read('*a')
local inner=tonumber('.'..assert(src:match("mask%('_relation%-'%+relation,%[%(%.([%d]+),%.5%)%]")))
local expected_inner=(S.token_diameter-S.ring_lane)/2/(S.token_diameter+S.ring_lane)
assert(math.abs(inner-expected_inner)<1e-4,'relation mask inner radius ('..inner..'~='..expected_inner..')')
checks=checks+1
assert(not src:find("mask%('_health%-band'"),'health mask must not be generated')
assert(not src:find("mask%('_shield"),'shield masks must not be generated')
assert(not src:find("mask%('_relation%-edge"),'the old health-rim mask must not be generated')
checks=checks+3
assert(src:find("mask%('_player%-inner'"),'player inner line must remain')

for rank,badge in pairs{[3.2]='rare',[3.5]='unique',[4]='boss',[5]='elite_boss',[10]='god'} do
 assert(S.rankBadge(rank)==badge);checks=checks+1
end
assert(not S.rankBadge(1) and not S.rankBadge(2) and not S.rankBadge(3),'critters, normals and elites stay unmarked')
checks=checks+1
assert(S.shieldData==nil and S.lifeFraction==nil,'dead shield and old radial life helpers must be removed')
checks=checks+1
print('token_geometry: '..checks..' disc, ring lane, mask and badge checks passed')
