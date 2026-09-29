local script=debug.getinfo(1,'S').source:sub(2)
local root=(script:match('^(.*[/\\])') or './')..'../'
local S=dofile(root..'overload/mod/class/CheckerTokenStyle.lua')
local actor={effects={},sustains={}}
function actor:attr(key) return self[key] end
function actor:hasEffect(key) return self.effects[key] end
function actor:isTalentActive(key) return self.sustains[key] end
function actor:callTalent(key,method) assert(key=='disruption' and method=='getMaxAbsorb');return 80 end
local n=0
local function check(v,m,count)
 local a,b,particles=S.shieldData(actor);assert(a==v and b==m,'shield capacity mismatch')
 local c=0;for _ in pairs(particles) do c=c+1 end;assert(c==count,'must suppress only explicitly owned shield emitters');n=n+1
end
check(0,0,0)
local unrelated={}
actor.EFF_DAMAGE_SHIELD='damage';actor.EFF_PSI_DAMAGE_SHIELD='psi'
actor.damage_shield=100;actor.damage_shield_absorb=35;actor.damage_shield_absorb_max=100
local damage={};actor.effects.damage={particle=damage};check(35,100,1)
assert(select(3,S.shieldData(actor))[damage] and not select(3,S.shieldData(actor))[unrelated])
actor.effects.damage=nil;actor.effects.psi={particle={}};check(35,100,1)
actor.EFF_TIME_SHIELD='time';actor.time_shield=50;actor.time_shield_absorb=40;actor.time_shield_absorb_max=50
actor.effects.time={particle={}};check(75,150,2)
actor.EFF_DISPLACEMENT_SHIELD='displacement';actor.displacement_shield=20;actor.displacement_shield_max=40
actor.effects.displacement={particle={}};check(95,190,3)
actor.T_DISRUPTION_SHIELD='disruption';actor.disruption_shield_power=15
actor.sustains.disruption={particle={}};check(110,270,4)
actor.T_HIEMAL_SHIELD='hiemal';actor.sustains.hiemal={shield=5,original_shield=60,particle={}}
check(115,330,5)
actor.damage_shield_absorb=-3;check(80,330,5)
actor.damage_shield=nil;actor.effects.psi=nil;check(80,230,4)
for _,tile in ipairs{48,64,96} do for size=1,5 do
 local s=S.scale(size,tile);local g=S.geometry(0,0,tile,s)
 assert(g.d+tile*.09<=tile,'outer shield must remain within one tile')
 assert((g.d+tile*.09)*.459>g.d*.495,'shield and faction lanes must not intersect')
 -- One board-piece diameter: size_category and tile size must not change the
 -- painted disc, otherwise neighbouring tokens read as different scales.
 assert(math.abs(S.art_occupancy*s-S.token_diameter)<1e-9,'painted disc must be the declared share of a cell')
 assert(math.abs(g.d/tile-(S.token_diameter+.085))<1e-9,'faction lane keeps its fixed width')
 n=n+1
end end
assert(math.abs(S.scale(1,48)-S.scale(4,96))<1e-12,'every size_category and tile size shares one scale')
assert(S.art_occupancy==.86,'must match target_occupancy in tools/export_token.c')
for rank,badge in pairs{[3.2]='rare',[3.5]='unique',[4]='boss',[5]='elite_boss',[10]='god'} do
 assert(S.rankBadge(rank)==badge);n=n+1
end
assert(not S.rankBadge(1) and not S.rankBadge(2) and not S.rankBadge(3),'critters, normals and elites intentionally have no badge')
print('shield_style: '..n..' capacity, particle ownership, geometry and rank checks passed')
