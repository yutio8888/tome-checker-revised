local M={}
function M.enabled()
 return config and config.settings and config.settings.cheat
  and config.settings.disable_all_connectivity
  and __module_extra_info and __module_extra_info.checker_fixture == true
end
return M
