-- Offline fixture only. Measurement-only census of native (unconverted) terrain
-- cells per level in Refined mode. Touches no production code and changes no
-- rule field. It only (a) wraps Zone:addEntity and GameState:findEventGrid to
-- remember which cells an aura event rewrote, and (b) reads final grids.
-- "Converted" = the forest adapter owns the cell (_checker_terrain display is
-- installed) or the stone adapter painted it (record.painted after a forced
-- visible observe/render pass, same as tests/live_map_survey.lua).
-- Native group key format = id|name|callbacks|#add_displays (as reuseDetails).
local Map=require 'engine.Map'
local Terrain=require 'mod.class.CheckerTerrain'
local EngineZone=require 'engine.Zone'
local ms=dofile('/data-checker-fixture/monster-live_map_survey.lua')
local M={ms=ms}

local tracked=setmetatable({},{__mode='k'})
local function bucket(level)
	local b=tracked[level]
	if not b then b={cells={},centres={},events={}};tracked[level]=b end
	return b
end
local function callerEvent()
	-- 1 = callerEvent, 2 = wrapper, 3 = caller of the wrapper
	local info=debug.getinfo(3,'S')
	local src=info and (info.short_src or info.source) or ''
	return src:match('events/([%w%-]+)%.lua')
end

function M.setup()
	ms.setup()
	if M.installed then return {ok=true,already=true} end
	M.installed=true
	local addEntity=EngineZone.addEntity
	EngineZone.addEntity=function(self,level,e,typ,x,y,...)
		local ev=typ=='terrain' and level and level.map and callerEvent()
		if ev then
			local b=bucket(level)
			b.cells[x+y*level.map.w]={event=ev,type=e.type,block=(e.does_block_move or e.block_move) and true or false}
			b.events[ev]=b.events[ev] or 0
		end
		return addEntity(self,level,e,typ,x,y,...)
	end
	-- Class-level patch on purpose: an instance field on game.state would be
	-- serialised into the savefile and hang the persistent-zone save pipe.
	local GameState=require 'mod.class.GameState'
	local find=GameState.findEventGrid
	GameState.findEventGrid=function(self,level,...)
		local x,y=find(self,level,...)
		local ev=callerEvent()
		if ev and x and level and level.map then
			local b=bucket(level)
			b.centres[x+y*level.map.w]=ev
			b.events[ev]=(b.events[ev] or 0)+1
		end
		return x,y
	end
	return {ok=true}
end

local function funcsOf(g)
	local funcs={}
	for k,v in pairs(g) do if type(v)=='function' then
		local info=debug.getinfo(v,'S')
		funcs[#funcs+1]=k..'@'..tostring(info and info.short_src)
	end end
	table.sort(funcs)
	return table.concat(funcs,',')
end

function M.census()
	assert(game.checker_mode=='refined','census requires Refined terrain mode, got '..tostring(game.checker_mode))
	local m=game.level.map
	local variant=Terrain.variant(game.zone)
	if variant then
		local realVisible=Terrain.visible
		Terrain.visible=function() return true end
		local ok,err=pcall(function()
			for x=0,m.w-1 do for y=0,m.h-1 do
				local g=m(x,y,Map.TERRAIN)
				Terrain.observe(m,x,y,g)
				Terrain.render(m,x,y,g,game.checker_mode)
			end end
		end)
		Terrain.visible=realVisible
		assert(ok,err)
	end
	local b=tracked[game.level] or {cells={},centres={},events={}}
	local zg=game.zone.generator
	local out={zone=game.zone.short_name,level=game.level.level,w=m.w,h=m.h,total=m.w*m.h,variant=variant or false,
		is_flooded=game.zone.is_flooded and true or false,is_hideout=game.zone.is_hideout and true or false,
		is_crystaline=game.zone.is_crystaline and true or false,is_purified=game.zone.is_purified and true or false,
		is_overground=(zg and zg.map and zg.map.class=='engine.generator.map.Town') and true or false,
		max_level=game.zone.max_level,
		converted=0,native=0,empty=0,converted_stone=0,converted_forest=0,groups={},events=b.events,aura={},centres={}}
	for k,ev in pairs(b.centres) do out.centres[#out.centres+1]={x=k%m.w,y=math.floor(k/m.w),event=ev} end
	for x=0,m.w-1 do for y=0,m.h-1 do
		local g=m(x,y,Map.TERRAIN)
		local key=x+y*m.w
		local rec=b.cells[key]
		local role
		if rec then
			role=b.centres[key] and 'E3-centre' or rec.type=='floor' and 'E1-floor' or rec.block and 'E2-wall' or 'E2-other'
		end
		local converted=false
		if not g then
			out.empty=out.empty+1
		else
			local s=g._checker_terrain
			if s and g.replace_display==s.display then converted=true;out.converted_forest=out.converted_forest+1 end
			local r=m._checker_korpul and m._checker_korpul[key]
			if not converted and r and r.painted then converted=true;out.converted_stone=out.converted_stone+1 end
			if converted then out.converted=out.converted+1 else
				out.native=out.native+1
				local id=g.define_as or g.name or 'nil'
				local gk=id..'|'..tostring(g.name)..'|'..funcsOf(g)..'|'..tostring(g.add_displays and #g.add_displays or 0)
				local grp=out.groups[gk]
				if not grp then
					grp={n=0,type=g.type,subtype=g.subtype,block=(g.does_block_move and true or false),
						exit=(g.change_level or g.change_zone) and true or false,ev={},sample={},layers={}}
					for _,d in ipairs(g.add_displays or {}) do grp.layers[#grp.layers+1]='d:'..tostring(d.image) end
					for _,mo in ipairs(g.add_mos or {}) do grp.layers[#grp.layers+1]='m:'..tostring(mo.image) end
					out.groups[gk]=grp
				end
				grp.n=grp.n+1
				if #grp.sample<3 then grp.sample[#grp.sample+1]={x,y} end
				if role then local t=rec.event..'/'..role;grp.ev[t]=(grp.ev[t] or 0)+1 end
			end
		end
		if role then
			local t=rec.event..'/'..role
			local a=out.aura[t]
			if not a then a={converted=0,native=0};out.aura[t]=a end
			if converted then a.converted=a.converted+1 else a.native=a.native+1 end
		end
	end end
	return out
end

function M.enterAndCensus(short_name,level,opts,path)
	local enter=ms.enter(short_name,level,opts)
	local c=M.census()
	c.enter=enter
	ms.dump(path,c)
end
return M
