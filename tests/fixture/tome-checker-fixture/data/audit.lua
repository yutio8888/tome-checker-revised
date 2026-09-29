-- The only arbitrary Lua command bridge lives in the explicitly installed
-- offline fixture. Runtime token packages contain neither it nor its caller.
assert(require('mod.class.CheckerFixture').enabled(),'offline checker fixture required')
if fs.exists('/board-test-command.txt') then
 local f=assert(fs.open('/board-test-command.txt','r'))
 local src=f:read(200000);f:close();fs.delete('/board-test-command.txt')
 local ok,err=xpcall(function() assert(loadstring(src))() end,debug.traceback)
 local result=(ok and 'PASS' or 'FAIL')..'\n'..(err or '')
 print('[BoardDebug]',result)
 local out=assert(fs.open('/board-test-result.txt','w'));out:write(result);out:close()
else
 dofile('/data-checker-fixture/audit-native.lua')
end
