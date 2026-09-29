-- Offline fixture only (TW3: Zigur, Angolwen, Iron Council). Reuses the TW2
-- scene module (stats, identity probe, natural-FOV view, pixel samples, rule
-- digest) and adds poses centred on a town's own features. Never edits a
-- grid rule field; actors near the photographed window are removed.
local Map=require 'engine.Map'
local Terrain=require 'mod.class.CheckerTerrain'
local tw=dofile('/data-checker-fixture/monster-live_tw2_scene.lua')
local M=setmetatable({},{__index=tw})

local function free(m,x,y)
	local g=m(x,y,Map.TERRAIN)
	return g and not g.does_block_move and not rawget(g,'block_move') and not rawget(g,'on_move') and
		not g.change_level and not g.change_zone and not m(x,y,Map.ACTOR) and not m(x,y,Map.TRAP)
end
-- Centre on the centroid of the cells whose define_as matches `pattern`
-- (offset dx,dy), stand on the nearest free cell (or leave the player where
-- it is when stay is set), clear actors from the window.
function M.poseOn(pattern,dx,dy,stay,label)
	local m,p=game.level.map,game.player
	local sx,sy,n=0,0,0
	for x=0,m.w-1 do for y=0,m.h-1 do
		local g=m(x,y,Map.TERRAIN)
		if g and type(g.define_as)=='string' and g.define_as:match(pattern) then sx,sy,n=sx+x,sy+y,n+1 end
	end end
	if n==0 then return {found=false,kind=label or pattern} end
	local cx,cy=math.floor(sx/n+0.5)+(dx or 0),math.floor(sy/n+0.5)+(dy or 0)
	local stand
	if not stay then
		for r=0,10 do
			for ddx=-r,r do for ddy=-r,r do
				if not stand and free(m,cx+ddx,cy+ddy) then stand={cx+ddx,cy+ddy} end
			end end
			if stand then break end
		end
		assert(stand,'no stand cell')
		p:move(stand[1],stand[2],true)
	end
	local moved=0
	for _,a in pairs(game.level.entities) do
		if a~=p and a.x and math.abs(a.x-cx)<=16 and math.abs(a.y-cy)<=10 then game.level:removeEntity(a,true);moved=moved+1 end
	end
	return {found=true,kind=label or pattern,x=cx,y=cy,stand=stand,cells=n,removed_actors=moved,player={p.x,p.y}}
end

-- Which of this town's TW3 identities are drawn as board art right now
-- (forest owner, stone record painted, or native) and the prop layers kept.
function M.tw3()
	local m=game.level.map
	local zoneName=game.zone.short_name
	local out={zone=zoneName,kinds={},props={}}
	for x=0,m.w-1 do for y=0,m.h-1 do
		local g=m(x,y,Map.TERRAIN)
		local fk=g and Terrain.batch4Kind(g,zoneName)
		local sk=g and Terrain.classify(g)
		local k=fk and ('forest:'..fk) or sk and ('stone:'..sk)
		if k then
			local st=g._checker_terrain
			local r=m._checker_korpul and m._checker_korpul[x+y*m.w]
			local owner=(st and g.replace_display==st.display) and 'board' or (r and r.painted and r.file) and 'board' or 'native'
			local e=out.kinds[k] or {board=0,native=0}
			out.kinds[k]=e;e[owner]=e[owner]+1
			local layer
			if st and g.replace_display==st.display then
				for _,d in ipairs(g.replace_display.add_displays or {}) do layer=d end
			elseif r and r.prop then layer=r.prop end
			if layer then
				out.props[#out.props+1]={x=x,y=y,kind=k,image=layer.image,z=layer.z,display_x=layer.display_x,
					display_y=layer.display_y,display_w=layer.display_w,display_h=layer.display_h}
			end
		end
	end end
	return out
end
return M
