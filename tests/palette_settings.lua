local script=debug.getinfo(1,'S').source:sub(2)
local root=(script:match('^(.*[/\\])') or './')..'../'
local S=dofile(root..'overload/mod/class/CheckerTokenStyle.lua')
assert(S.rankColor('rare')[1]==250,'no configuration must use restored defaults')
config={settings={tome={unrelated='keep'}}}
local writes,redraws=0,0
local serialized
game={saveSettings=function(_,key,value)
 assert(key=='tome.checker_rank_colors' or key=='tome.checker_relation_colors');serialized=value;writes=writes+1
end,level={map={redisplay=function() redraws=redraws+1 end}}}
local input={12,34,56}
assert(S.setRankColor('rare',input))
input[1]=200
assert(S.rankColor('rare')[1]==12 and S.rank_colors.rare[1]==250,'draft must not alias saved settings or defaults')
assert(S.setRankColor('boss',{0,255,255}))
assert(S.rankColor('rare')[2]==34 and S.rankColor('unique')[1]==244,'editing one rank preserves other ranks')
for _,bad in ipairs{false,'12,34,56',{256,0,0},{-1,0,0},{0.5,0,0},{0/0,0,0},{math.huge,0,0},{1,2}} do
 assert(not S.setRankColor('rare',bad),'invalid RGB should be rejected')
end
assert(not S.setRankColor('elite',{0,0,0}) and writes==2,'invalid keys and values must not save')
local env={tome={}}
local chunk=assert(loadstring(serialized));setfenv(chunk,env);chunk()
config.settings.tome.checker_rank_colors=env.tome.checker_rank_colors
assert(S.rankColor('rare')[1]==12 and S.rankColor('boss')[3]==255,'serialized settings must round-trip')
config.settings.tome.checker_rank_colors={rare='broken',unique={1,2,300},untrusted='ignored'}
assert(S.rankColor('rare')[1]==250 and S.rankColor('unique')[1]==244,'bad saved data must safely use defaults')
assert(S.setRankColor('boss',{1,2,3}) and not serialized:find('untrusted',1,true),'save must whitelist supported ranks')
S.resetRankColors()
assert(next(config.settings.tome.checker_rank_colors)==nil and S.rankColor('boss')[1]==255)
assert(config.settings.tome.unrelated=='keep' and writes==4 and redraws==4)
assert(not S.rankBadge(2) and not S.rankBadge(3) and S.colors.player[1]==30)
assert(S.setRelationColor('friend',{30,195,245}))
assert(S.setRelationColor('neutral',{120,100,220}))
assert(S.relationColor('friend')[1]==30 and S.relationColor('enemy')[1]==225)
assert(not S.setRelationColor('player',{0,0,0}),'player identity must not be configurable through other relations')
assert(S.relationColor('player')==S.colors.player and S.colors.player[1]==30)
env={tome={}};chunk=assert(loadstring(serialized));setfenv(chunk,env);chunk()
config.settings.tome.checker_relation_colors=env.tome.checker_relation_colors
assert(S.relationColor('neutral')[2]==100,'relation overrides must round-trip separately')
S.resetColors()
assert(next(config.settings.tome.checker_relation_colors)==nil and S.relationColor('friend')[2]==210)
assert(S.rankColor('rare')[1]==250 and config.settings.tome.unrelated=='keep')
print('palette_settings: defaults, validation, independent rank/faction settings, serialization, player identity and reset passed')
