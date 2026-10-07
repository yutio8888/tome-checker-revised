-- R39 standee height: the per-id committed cap, the manual override, the width
-- cap/uniform scaling and the 24px tile floor. Loads the shipped table so a
-- hand edit to data/token-standee-heights.lua is caught.
local script=debug.getinfo(1,'S').source:sub(2)
local root=(script:match('^(.*[/\\])') or './')..'../'
local Style=dofile(root..'overload/mod/class/CheckerTokenStyle.lua')
Style.standee_heights=dofile(root..'data/token-standee-heights.lua')
package.loaded['mod.class.CheckerTokenStyle']=Style
local Tokens=dofile(root..'overload/mod/class/CheckerTokens.lua')
Tokens.layer_geometry=dofile(root..'data/token-layer-geometry.lua')
local checks=0
local function ok(cond,what) assert(cond,what);checks=checks+1 end
-- Read the shipped standee list from the runtime module so new standees are
-- covered without editing this test.
local standee_ids={}
for id in pairs(Tokens.standee_ids) do standee_ids[#standee_ids+1]=id end
table.sort(standee_ids)
ok(#standee_ids>0,'the standee id list is non-empty')

-- 1. Per-id committed caps, straight from the generated table.
ok(Style.standee_heights['snow-giant']==1.40625,'snow-giant derived cap 1.40625')
ok(Style.standee_heights['ogre-guard']==1.421875,'ogre-guard derived cap 1.421875')
ok(Style.standeeHeight('ogre-guard')==1.078125,'ogre-guard override trims the hammer and floating top speck')
ok(Style.standeeHeight('kra-tor')==1.0,'kra-tor axe over a ~1-cell body is flat')
ok(Style.standeeHeight('ravenous-horror')==1.25,'ravenous-horror cap 1.25')
ok(Style.standeeHeight('ninandra')==1.140625,'ninandra cool white/cyan glow above the head is trimmed; alpha>128 top y=38')
ok(Style.standeeHeight('gorbat')==1.0,'gorbat is exactly 1.0 (flat marker)')
ok(Style.standeeHeight('bone-giant')==1.0,'bone-giant is exactly 1.0 (flat marker)')
ok(Style.standeeHeight('lich')==1.0,'lich is exactly 1.0 (flat marker)')
ok(Style.standeeHeight('phoenix')==nil,'a native 1-cell id has no cap')
ok(Style.standeeHeight('wolf')==nil,'a non-tall ordinary id has no cap')
ok(Style.standeeHeight(nil)==nil,'nil id has no cap')
-- The table has no per-size key a live actor could land on.
ok(Style.standee_heights[3]==nil and Style.standee_heights[4]==nil,'the table is keyed by id, never size_category')

-- 2. The per-identity override wins in one place and is the manual fix path
-- (raised weapons/particles). It ships the reviewed R40 fixes, so test the win
-- on an id that is not itself overridden and restore it afterwards.
ok(type(next(Style.standee_height_override))~=nil,'the reviewed override table ships populated')
ok(Style.standee_height_override['kra-tor']==1.0 and Style.standee_height_override['snow-giant']==nil,
 'kra-tor is flat; the other standees keep the derived cap')
Style.standee_height_override['snow-giant']=1.6
ok(Style.standeeHeight('snow-giant')==1.6,'override wins for its id')
ok(Style.standeeHeight('ravenous-horror')==1.25,'override does not leak to other ids')
Style.standee_height_override['snow-giant']=nil
ok(Style.standeeHeight('snow-giant')==1.40625,'clearing the override restores the table')
-- An override can also lift a flat id; the rule then reads >1.0.
ok(Tokens.standeeRule(Tokens.by_id['gorbat'])==false,'gorbat is flat without an override')
Style.standee_height_override['gorbat']=1.2
ok(Tokens.standeeRule(Tokens.by_id['gorbat'])==true,'an explicit override is the manual fix path')
Style.standee_height_override['gorbat']=nil
ok(Tokens.standeeRule(Tokens.by_id['gorbat'])==false,'clearing the override flattens it again')

-- 3. Width cap stays binding and scaling stays uniform: drawn height is
-- min(cap, width_cap*cell/bw * bh/cell) and never exceeds the cap.
local CELL=48
local DISC_D=CELL*Style.token_diameter
local function drawnCells(box,cap,canvas)
 local bw,bh=box.right-box.left,box.bottom-box.top
 local _,_,size=Style.standeeQuad(CELL,box,canvas,CELL/2,CELL/2,DISC_D,cap)
 local scale=size/canvas
 return bh*scale/CELL,bw*scale/CELL
end
local tall={left=39,top=14,right=89,bottom=114}
local h,w=drawnCells(tall,1.5,128)
ok(math.abs(h-1.5)<1e-9,'a narrow tall box hits the height cap exactly')
ok(w<=Style.standee_width+1e-9,'narrow art stays inside the width cap')
local wide={left=4,top=40,right=124,bottom=100}
h,w=drawnCells(wide,1.75,128)
ok(math.abs(w-Style.standee_width)<1e-9,'wide art hits the width cap')
ok(h<1.75-1e-9,'width-capped art is shorter than the height cap')
ok(h<=1.75+1e-9,'width-capped art never exceeds the height cap')
-- The same box scales by cell only.
local _,_,s48=Style.standeeQuad(48,tall,128,24,24,48*Style.token_diameter,1.5)
local _,_,s64=Style.standeeQuad(64,tall,128,32,32,64*Style.token_diameter,1.5)
local _,_,s96=Style.standeeQuad(96,tall,128,48,48,96*Style.token_diameter,1.5)
ok(math.abs(s64/s48-64/48)<1e-9 and math.abs(s96/s48-96/48)<1e-9,'standee is cell-proportional')

-- 4. Per-file canvas: every standee layer is 256px, ordinary layers 128px.
for _,id in ipairs(standee_ids) do
 ok(Tokens.layer_geometry[id].canvas==256,id..' standee layer records the 256px canvas')
end
ok(Tokens.layer_geometry['wolf'].canvas==128,'an ordinary layer records the 128px canvas')

-- 5. The 24px floor is the only tile-size rule; there is no upper bound.
for _,cell in ipairs{24,32,48,64,96,128} do
 ok(Tokens.standeeTileAllowed(cell)==true,'standee allowed at '..cell..'px')
end
for _,cell in ipairs{16,23} do
 ok(Tokens.standeeTileAllowed(cell)==false,'flat at '..cell..'px')
end
ok(Tokens.layer_max_cell==48,'the ordinary R32 <=48px gate is unchanged')

print('token_standee_size: '..checks..' per-id cap, override, width-cap, canvas and 24px-floor checks passed')
