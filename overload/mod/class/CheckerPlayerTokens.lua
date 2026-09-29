-- Production player tokens: one neutral image per native body family.
-- The family is the expanded native moddable_tile of the birth subrace, keyed
-- by descriptor subrace x sex. Class, equipment and cosmetics are ignored on
-- purpose: the art never follows them. This table is separate from the
-- creature catalog, whose exact-identity/appearance rules reject paper dolls.
-- Faction, life, shields and selection stay in the tactical overlay layers.
local M = {}

-- The 14 base-game body families, i.e. every distinct expanded moddable_tile
-- a native birth subrace can produce. Lich reuses "skeleton" but is converted
-- in play and is intentionally not a key below (it keeps native art).
M.families = {
	'human_male', 'human_female', 'elf_male', 'elf_female',
	'dwarf_male', 'dwarf_female', 'halfling_male', 'halfling_female',
	'ogre_male', 'ogre_female', 'yeek', 'ghoul', 'skeleton', 'runic_golem',
}
local family_set = {}
for _, family in ipairs(M.families) do family_set[family] = true end

-- Native descriptor moddable_tile templates (data/birth/races/*.lua). An
-- actor whose current moddable_tile differs was altered after birth (custom
-- tile, Lich conversion, another addon) and keeps its native display.
M.moddable = {
	Higher = 'human_#sex#', Cornac = 'human_#sex#',
	Shalore = 'elf_#sex#', Thalore = 'elf_#sex#',
	Dwarf = 'dwarf_#sex#', Halfling = 'halfling_#sex#', Ogre = 'ogre_#sex#',
	Yeek = 'yeek', Ghoul = 'ghoul', Skeleton = 'skeleton', ['Runic Golem'] = 'runic_golem',
}

-- Explicit subrace x sex -> family. Keys absent here (Lich, tutorial, DLC
-- subraces, sexes a native descriptor disallows) always keep native art. Add
-- a DLC key only together with its verified moddable template above.
M.keys = {
	['Higher/Male'] = 'human_male', ['Higher/Female'] = 'human_female',
	['Cornac/Male'] = 'human_male', ['Cornac/Female'] = 'human_female',
	['Shalore/Male'] = 'elf_male', ['Shalore/Female'] = 'elf_female',
	['Thalore/Male'] = 'elf_male', ['Thalore/Female'] = 'elf_female',
	['Dwarf/Male'] = 'dwarf_male', ['Dwarf/Female'] = 'dwarf_female',
	['Halfling/Male'] = 'halfling_male', ['Halfling/Female'] = 'halfling_female',
	['Ogre/Male'] = 'ogre_male', ['Ogre/Female'] = 'ogre_female',
	['Yeek/Male'] = 'yeek', ['Yeek/Female'] = 'yeek',
	['Ghoul/Male'] = 'ghoul', ['Skeleton/Male'] = 'skeleton',
	['Runic Golem/Male'] = 'runic_golem',
}

for key, family in pairs(M.keys) do
	local subrace, sex = key:match('^(.+)/(%a+)$')
	local template = assert(M.moddable[subrace], 'player key without moddable template: '..key)
	assert(family_set[family], 'unknown player family: '..family)
	assert(template:gsub('#sex#', sex == 'Female' and 'female' or 'male') == family,
		'player key does not expand to its family: '..key)
end

-- Only families whose runtime export is both listed in the reviewed manifest
-- and present on disk are available. An empty/missing/invalid manifest keeps
-- every player native, so artwork can be added later without code changes.
M.manifest_path = '/data-checker-revised/player-token-manifest.lua'
M.available = {}

function M.imageFile(family)
	return '/data-checker-revised/gfx/tokens/player-'..family..'.png'
end

function M.loadManifest(manifest, exists)
	local available = {}
	if type(manifest) ~= 'table' or type(manifest.families) ~= 'table'
		or type(manifest.revision) ~= 'string' then return available, 'invalid-manifest' end
	for family, approved in pairs(manifest.families) do
		if family_set[family] and approved == true and exists and exists(M.imageFile(family)) then
			available[family] = true
		end
	end
	return available
end

do
	if fs and fs.exists and loadfile and fs.exists(M.manifest_path) then
		local chunk = loadfile(M.manifest_path)
		local ok, manifest = false, nil
		if chunk then ok, manifest = pcall(chunk) end
		if ok then M.available = M.loadManifest(manifest, fs.exists) end
	end
end

local function empty(value)
	return value == nil or (type(value) == 'table' and next(value) == nil)
end

-- Body family of a birth-state player, or nil with a reason. Identity only.
function M.family(actor)
	if type(actor) ~= 'table' then return nil, 'invalid-actor' end
	local d = actor.descriptor
	if type(d) ~= 'table' or type(d.subrace) ~= 'string' or type(d.sex) ~= 'string' then
		return nil, 'no-descriptor'
	end
	local family = M.keys[d.subrace..'/'..d.sex]
	if not family then return nil, 'unmapped-key' end
	-- Birth copies male/female booleans from the sex descriptor; native
	-- rendering expands #sex# from them. Both must agree with the key.
	if d.sex == 'Male' then
		if actor.male ~= true or actor.female then return nil, 'sex-mismatch' end
	elseif actor.female ~= true or actor.male then return nil, 'sex-mismatch' end
	-- Donator custom tiles clear moddable_tile; guard explicitly anyway.
	if actor.has_custom_tile ~= nil then return nil, 'custom-tile' end
	if actor.moddable_tile ~= M.moddable[d.subrace] then return nil, 'moddable-tile' end
	return family
end

-- owned_display: the exact Entity this addon installed, if any.
-- opts.main: actor is game.party's main member. opts.no_moddable: native
-- paper dolls are disabled (ASCII or a tileset without moddable tiles).
function M.explain(actor, owned_display, opts)
	if type(actor) ~= 'table' then return nil, 'invalid-actor' end
	opts = opts or {}
	if opts.main ~= true then return nil, 'not-main' end
	if actor.replace_display and actor.replace_display ~= owned_display then return nil, 'external-display' end
	if opts.no_moddable then return nil, 'no-moddable-tiles' end
	local family, reason = M.family(actor)
	if not family then return nil, reason end
	if actor.shader then return nil, 'shader' end
	if actor.anim then return nil, 'animation' end
	if not empty(actor.add_displays) then return nil, 'add-displays' end
	if not empty(actor.textures) then return nil, 'textures' end
	-- A native shader aura wraps whatever image is on the current display;
	-- keep the token so the aura renders around it instead of falling back.
	if not M.available[family] then return nil, 'no-art' end
	return 'player:'..family, 'player-family'
end

function M.identify(actor, owned_display, opts)
	local id = M.explain(actor, owned_display, opts)
	return id
end

function M.isPlayerId(id)
	return type(id) == 'string' and id:sub(1, 7) == 'player:'
end

function M.image(id)
	local family = type(id) == 'string' and id:match('^player:([%w_]+)$')
	assert(family and family_set[family], 'unknown player token: '..tostring(id))
	return 'checker-revised+tokens/player-'..family..'.png'
end

return M
