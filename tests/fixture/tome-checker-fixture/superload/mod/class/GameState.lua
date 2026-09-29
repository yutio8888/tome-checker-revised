local _M=loadPrevious(...)
local Fixture=require 'mod.class.CheckerFixture'
local previous=_M.alternateZoneTier1
function _M:alternateZoneTier1(name,...)
 if name=='trollmire' and Fixture.enabled() then return 'DEFAULT' end
 return previous(self,name,...)
end
return _M
