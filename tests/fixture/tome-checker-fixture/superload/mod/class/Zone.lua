local _M=loadPrevious(...)
local Fixture=require 'mod.class.CheckerFixture'
local previous=_M.onLoadZoneFile
function _M:onLoadZoneFile(...)
 local r=previous(self,...)
 if self.short_name=='trollmire' and Fixture.enabled() and self.generator.map.do_ponds then
  self.generator.map.do_ponds.nb={2,2}
 end
 return r
end
return _M
