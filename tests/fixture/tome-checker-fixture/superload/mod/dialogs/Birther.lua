local _M = loadPrevious(...)
local Fixture=require 'mod.class.CheckerFixture'

-- Optional launch choice: __module_extra_info.checker_birth =
-- "Race:Subrace:Sex:Class" where Class is a subclass name ("Berserker") or
-- "Class/Subclass" ("Warrior/Berserker"); "None" selects the class-less
-- Runic Golem build. setDescriptor bypasses profile unlocks, so locked races
-- can be created in this offline fixture only. Default: Cornac Male Berserker.
local function birthChoice(self)
 local spec=__module_extra_info.checker_birth
 if spec==nil then return {race='Human',subrace='Cornac',sex='Male',class='Warrior',subclass='Berserker'} end
 if type(spec)~='string' then return nil,'checker_birth must be a string' end
 local race,subrace,sex,class=spec:match('^([^:]+):([^:]+):([^:]+):([^:]+)$')
 if not race then return nil,'expected Race:Subrace:Sex:Class' end
 local defs=self.birth_descriptor_def
 if not defs.race[race] then return nil,'unknown race '..race end
 if not defs.subrace[subrace] then return nil,'unknown subrace '..subrace end
 if sex~='Male' and sex~='Female' then return nil,'sex must be Male or Female' end
 local choices=defs.race[race].descriptor_choices
 local allowed=choices and choices.subrace
 if allowed and allowed[subrace]~='allow' then return nil,subrace..' is not a '..race..' subrace' end
 choices=defs.subrace[subrace].descriptor_choices
 allowed=choices and choices.sex
 if allowed and allowed[sex]~='allow' and not (allowed.__ALL__=='allow' and allowed[sex]==nil) then
  return nil,subrace..' does not allow '..sex
 end
 local subclass
 class,subclass=class:match('^([^/]+)/([^/]+)$'),class:match('^[^/]+/([^/]+)$') or class
 if not class then
  for _,d in ipairs(defs.class) do
   local sc=d.descriptor_choices and d.descriptor_choices.subclass
   -- Native Birther:isDescriptorAllowed treats 'allow', 'allow-nochange' and
   -- 'nolore' as selectable subclasses (dialogs/Birther.lua); 'allow' alone
   -- rejected valid classes such as Mage/Archmage ('allow-nochange').
   local value=sc and sc[subclass]
   if value=='allow' or value=='allow-nochange' or value=='nolore' then class=d.name;break end
  end
 end
 if not class or not defs.class[class] then return nil,'no class for '..tostring(subclass) end
 if not defs.subclass[subclass] then return nil,'unknown subclass '..subclass end
 return {race=race,subrace=subrace,sex=sex,class=class,subclass=subclass}
end

local previous = _M.on_register
function _M:on_register(...)
 local ret = previous(self, ...)
 if not Fixture.enabled() then return ret end
 game:onTickEnd(function()
  local choice,err=birthChoice(self)
  if not choice then print('[CheckerFixture] ERROR invalid checker_birth:',err) return end
  for _,v in ipairs{{'sex',choice.sex},{'world',"Maj'Eyal"},{'difficulty','Normal'},{'permadeath','Adventure'},{'race',choice.race},{'subrace',choice.subrace},{'class',choice.class},{'subclass',choice.subclass}} do self:setDescriptor(v[1],v[2]) end
  rng.seed(260926)
  self:atEnd('created')
 end,'checker_birth')
 return ret
end
return _M
