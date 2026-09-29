-- Native body coverage audit for the bounded forest/water family inventory.
-- Load only in the disposable offline fixture. Resolves detached actors; does
-- not place them, change monster definitions, or advance a world turn.
local Tokens=require 'mod.class.CheckerTokens'
local M={}
local families={'rodent','vermin','canine','troll','snake','plant','swarm','bear','aquatic_critter'}
local function text(v) return tostring(v or ''):gsub('[\t\r\n]',' ') end

function M.run(filename)
 assert(config.settings.cheat and config.settings.disable_all_connectivity and not profile.auth)
 assert(game.zone and game.zone.short_name=='trollmire' and game.checker_staged)
 assert(type(Tokens.explain)=='function','reason-coded mapper required')
 local turn=game.turn
 local sources,seen={},{}
 local function add(list,source,scope)
  for _,p in pairs(list) do
   if type(p)=='table' and p.name and not seen[p.name] then
    seen[p.name]=true
    sources[#sources+1]={actor=p,source=source,scope=scope}
   end
  end
 end
 for _,family in ipairs(families) do
  local path='/data/general/npcs/'..family..'.lua'
  add(game.zone.npc_class:loadList(path,true),path,'direct-family')
 end
 local uniques={}
 for _,p in pairs(game.zone.npc_list) do
  if type(p)=='table' and p.define_as and p.define_as:find('^TROLL_') then uniques[#uniques+1]=p end
  if type(p)=='table' and p.define_as=='ALUIN' then uniques[#uniques+1]=p end
 end
 add(uniques,'/data/zones/trollmire/npcs.lua','fixed-unique')
 table.sort(sources,function(a,b) return a.actor.name<b.actor.name end)
 local path='/'..(filename or 'token-coverage')..'.tsv'
 local file=assert(fs.open(path,'w'))
 file:write('name\ttype\tsubtype\tdefine_as\trank\tmin_level\tmax_level\timage\ttoken\tstatus\treason\tsource\tscope\n')
 local hits,total,failures=0,0,0
 for _,item in ipairs(sources) do
  local proto=item.actor
  local ok,actor=pcall(function() return game.zone:finishEntity(game.level,'actor',proto) end)
  local id,reason
  if ok then id,reason=Tokens.explain(actor,actor._checker_token and actor._checker_token.display)
  else reason='resolve-error: '..tostring(actor);actor=proto;failures=failures+1 end
  total=total+1
  if id then hits=hits+1 end
  local range=proto.level_range or {}
  local row={actor.name,actor.type,actor.subtype,actor.define_as,actor.rank,range[1],range[2],
   actor.image,id,id and 'covered' or ok and 'fallback' or 'unresolved',reason,item.source,item.scope}
  -- Fixed column count: sparse optional fields must not truncate ipairs.
  local values={};for i=1,13 do values[i]=text(row[i]) end
  file:write(table.concat(values,'\t')..'\n')
 end
 file:close()
 assert(game.turn==turn,'coverage audit advanced the world')
 print('[TokenCoverage]',hits,total,'resolved-errors',failures,'turn',turn,'path',path)
 return {covered=hits,total=total,unresolved=failures,path=path}
end
return M
