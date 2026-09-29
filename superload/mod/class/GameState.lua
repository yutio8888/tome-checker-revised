local _M = loadPrevious(...)
local Tokens = require 'mod.class.CheckerTokens'
local createRandomBoss = _M.createRandomBoss

function _M:createRandomBoss(base, data, ...)
 -- Native code clones the base before rewriting name/define_as/unique. Capture
 -- before that happens; validate only after init, resolvers, classes and post.
 -- Do not wrap callbacks, edit generation parameters or change actor rules.
 local origin = Tokens.captureRandomOrigin(base)
 local actor, boss_id = createRandomBoss(self, base, data, ...)
 Tokens.recordRandomOrigin(actor, origin, boss_id)
 return actor, boss_id
end
return _M
