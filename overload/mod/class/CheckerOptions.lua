-- Visual preferences are global ToME settings, independent of the current HUD
-- and of whether a character has been created yet.
local M = {}
local modes = {vanilla=true, blockout=true, refined=true}
local facings = {fixed=true, native=true}
local aura_styles = {subtle=true, moderate=true}

local function settings()
 return config and config.settings and config.settings.tome or {}
end

function M.tokensEnabled()
 return settings().checker_tokens_enabled ~= false
end

-- Production player tokens need this and the creature token setting. Its own
-- key keeps a player's choice when creature tokens are switched off and on.
function M.playerTokensEnabled()
 return settings().checker_player_tokens_enabled ~= false
end

function M.terrainMode()
 local mode = settings().checker_terrain_mode
 return modes[mode] and mode or 'vanilla'
end

function M.tokenFacing()
 local facing = settings().checker_token_facing
 return facings[facing] and facing or 'fixed'
end

function M.auraStyle()
 local style = settings().checker_aura_style
 return aura_styles[style] and style or 'subtle'
end

local function save(host, key, value, serialized)
 assert(config and config.settings, 'ToME settings are not initialized')
 config.settings.tome = config.settings.tome or {}
 config.settings.tome[key] = value
 if host and host.saveSettings then
  host:saveSettings('tome.'..key, 'tome.'..key..' = '..serialized..'\n')
 end
 if host and host.checkerApplySettings then host:checkerApplySettings() end
end

function M.setTokensEnabled(enabled, host)
 assert(type(enabled) == 'boolean', 'token setting must be a boolean')
 save(host, 'checker_tokens_enabled', enabled, tostring(enabled))
 return enabled
end

function M.setPlayerTokensEnabled(enabled, host)
 assert(type(enabled) == 'boolean', 'player token setting must be a boolean')
 save(host, 'checker_player_tokens_enabled', enabled, tostring(enabled))
 return enabled
end

function M.setTerrainMode(mode, host)
 assert(modes[mode], 'terrain mode must be vanilla, blockout or refined')
 save(host, 'checker_terrain_mode', mode, ('%q'):format(mode))
 return mode
end

function M.setTokenFacing(facing, host)
 assert(facings[facing], 'token facing must be fixed or native')
 save(host, 'checker_token_facing', facing, ('%q'):format(facing))
 return facing
end

function M.setAuraStyle(style, host)
 assert(aura_styles[style], 'aura style must be subtle or moderate')
 save(host, 'checker_aura_style', style, ('%q'):format(style))
 return style
end

return M
