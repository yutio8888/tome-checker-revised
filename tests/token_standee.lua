-- R39 standee redesign: static native-tall eligibility, per-id committed height
-- table, the 24px tile gate and the draw pass. Loads the real CheckerTokenStyle,
-- the committed height table and CheckerTokens so the tested path is shipped.
local script=debug.getinfo(1,'S').source:sub(2)
local root=(script:match('^(.*[/\\])') or './')..'../'
local Style=dofile(root..'overload/mod/class/CheckerTokenStyle.lua')
-- The dofile harness has no fs/loadfile bridge, so publish the committed table
-- the runtime would load from /data-checker-revised/token-standee-heights.lua.
Style.standee_heights=dofile(root..'data/token-standee-heights.lua')
package.loaded['mod.class.CheckerTokenStyle']=Style
local Tokens=dofile(root..'overload/mod/class/CheckerTokens.lua')
local checks=0
local function ok(cond,what) assert(cond,what);checks=checks+1 end

-- 1. Constants. The rank rule, the size table and the demo list are gone.
ok(Tokens.standee_trial==true,'standee trial defaults on')
ok(Tokens.standee_min_cell==24,'standee minimum tile is 24px')
ok(Style.standee_min_cell==24,'style agrees on the 24px floor')
ok(Style.standee_width==1,'approved width cap (native 64x128 tall sprite)')
ok(Style.standee_feet==0.55,'approved feet anchor')
ok(type(Style.standee_height_override)=='table','height override table exists')
-- R43: the override fixes ids whose native bbox top is not the standing body.
-- Every key must be a reviewed native-tall id, every value a cap in [1.0,1.75]
-- that is not larger than the generated cap. kra-tor's axe is above a ~1-cell
-- body (flat), ogre-guard trims the hammer and a floating top speck, and
-- ninandra trims the cool glow above the head, while snow-giant and
-- ravenous-horror keep the derived cap.
local expected_overrides={
 'ak-gishil', 'arch-zephyr', 'archmage-tarelion', 'argoniel', 'blade-horror',
 'boiling-horror', 'burb-snow-giant-champion', 'caldizar', 'celia', 'cryomancer',
 'duathedlen', 'elandar',
 'emperor-wight', 'fallen-sun-paladin-aeryn', 'fillarel-aldaren', 'forge-giant',
 'geomancer', 'gigantic-gravity-worm', 'gigantic-sandworm-tunneler',
 'greater-teluvorta', 'half-finished-bone-giant', 'heavy-sentinel', 'high-sun-paladin-aeryn', 'khulmanar',
 'kra-tor', 'kryl-feijan', 'kyless', 'lady-nashva', 'lady-zoisla', 'naga-nereid',
 'naga-tidecaller', 'naga-tidewarden', 'ninandra', 'norgos-frozen', 'ogre-guard',
 'ogre-rune-spinner', 'ogric-abomination', 'onilug', 'pale-drake', 'shiaak-venomblade',
 'snow-giant-boulder-thrower', 'snow-giant-thunderer', 'tempest', 'urkis',
 'uruivellas', 'void-spectre', 'weaver-queen', 'xhaiak-arachnomancer', 'yeek-mindslayer',
}
local got_overrides={}
for id in pairs(Style.standee_height_override) do got_overrides[id]=true end
for _,id in ipairs(expected_overrides) do
 ok(got_overrides[id],id..' body-only override ships')
 got_overrides[id]=nil
end
ok(next(got_overrides)==nil,'no unexpected height override')
for _,id in ipairs(expected_overrides) do
 ok(type(Style.standee_height_override[id])=='number' and Style.standeeHeight(id)==Style.standee_height_override[id],
  id..' override wins')
 ok(Style.standee_height_override[id]>=1.0 and Style.standee_height_override[id]<=1.75,id..' override clamped')
 ok(Style.standee_height_override[id]<=Style.standee_heights[id],id..' override never raises the cap')
end
-- R42 body rule: raised arms/wings count, so the R41 overrides that trimmed
-- them are dropped and the derived cap is kept.
for _,id in ipairs{'thaurhereg','harkor-zun','spellblaze-simulacrum','corrupted-sand-wyrm','rotting-titan','temporal-defiler','prox'} do
 ok(Style.standee_height_override[id]==nil,id..' R41 raised-body override is dropped')
end
-- R45/R46 sparse/translucent-fringe rule: the body top is the solid top (the
-- first row with >= 6 pixels above alpha 128); the energy bodies whose glow is
-- their body keep the derived cap (decision 3).
ok(Style.standeeHeight('archmage-tarelion')==1.0,'archmage-tarelion warm glow excluded, solid top y=49 -> 0.96875 clamped flat')
ok(Style.standeeHeight('duathedlen')==1.265625,'duathedlen darkness shroud excluded, solid head top y=31')
ok(Style.standeeHeight('onilug')==1.015625,'onilug shadow excluded, solid head spike top y=47')
ok(Style.standeeHeight('weaver-queen')==1.234375,'weaver-queen bristles/specks excluded, solid body top y=33')
ok(Style.standeeHeight('greater-telugoroth')==1.1875 and Style.standeeHeight('ultimate-telugoroth')==1.609375
 and Style.standeeHeight('daelach')==1.71875,'energy/cloud bodies whose glow is the body keep the derived cap')
-- R48 decision 3 extension: elementals whose desc says they ARE the element
-- keep their derived caps and are recorded as energy bodies.
ok(Style.standeeHeight('fyrk')==1.59375 and Style.standeeHeight('ultimate-faeros')==1.34375
 and Style.standeeHeight('ultimate-teluvorta')==1.640625 and Style.standeeHeight('maelstrom')==1.71875
 and Style.standeeHeight('ultimate-gwelgoroth')==1.375 and Style.standeeHeight('glacial-legion')==1.671875
 and Style.standee_height_override['fyrk']==nil and Style.standee_height_override['maelstrom']==nil,
 'elemental bodies whose element is the body keep the derived cap')
-- R48 decisions 1-2: half-finished-bone-giant purple halo and kryl-feijan darkness.
ok(Style.standeeHeight('half-finished-bone-giant')==1.21875,'half-finished-bone-giant purple halo rows 31-33 excluded; skull/head top y=34')
ok(Style.standeeHeight('kryl-feijan')==1.0,'kryl-feijan darkness cloud excluded; first non-darkness body row (blue claw-like limbs) top y=58 -> flat')
ok(Style.standeeHeight('thaurhereg')==1.53125,'thaurhereg horns are body')
ok(Style.standeeHeight('harkor-zun')==1.53125,'harkor-zun horned head is body')
ok(Style.standeeHeight('spellblaze-simulacrum')==1.5625,'spellblaze-simulacrum horned head is body')
ok(Style.standeeHeight('corrupted-sand-wyrm')==1.703125,'corrupted-sand-wyrm curled tail is body')
ok(Style.standeeHeight('rotting-titan')==1.625,'rotting-titan raised arms are body')
ok(Style.standeeHeight('temporal-defiler')==1.234375,'temporal-defiler raised arms are body')
ok(Style.standeeHeight('prox')==1.0625,'prox is a troll; the head is the bbox top')
-- Raised weapons/staves/spells/particles still do not count.
ok(Style.standeeHeight('lady-nashva')==1.234375,'lady-nashva trident trimmed')
ok(Style.standeeHeight('caldizar')==1.25,'caldizar staff/motes trimmed')
ok(Style.standeeHeight('argoniel')==1.0,'argoniel raised sword/staff leaves body ~1 cell')
ok(Style.standeeHeight('ogre-rune-spinner')==1.296875,'ogre-rune-spinner spell vortex trimmed')
ok(Style.standeeHeight('snow-giant-thunderer')==1.40625,'snow-giant-thunderer lightning trimmed; head top y=20')
ok(Style.standeeHeight('pale-drake')==1.0,'pale-drake staff leaves body ~1 cell')
ok(Style.standeeHeight('forge-giant')==1.328125,'forge-giant head flame excluded; head top y=27')
ok(Style.standeeHeight('lady-zoisla')==1.3125,'lady-zoisla trident/staff trimmed')
ok(Style.standeeHeight('snow-giant-boulder-thrower')==1.484375,'snow-giant-boulder-thrower boulder above the raised arms (arm top y=15)')
ok(Style.standeeHeight('celia')==1.390625,'celia staff above the head; the head top y=23 is body')
ok(Style.standeeHeight('naga-tidecaller')==1.078125,'naga-tidecaller trident above the head; head top is body')
ok(Style.standeeHeight('xhaiak-arachnomancer')==1.4375,'xhaiak smoke above the raised legs/arms (limb top y=20)')
ok(Style.standeeHeight('burb-snow-giant-champion')==1.53125,'burb lightning above the dark horns (horn top y=13)')
ok(Style.standeeHeight('gigantic-gravity-worm')==1.40625,'gigantic-gravity-worm lightning above the head (head top y=21)')
ok(Style.standeeHeight('gigantic-sandworm-tunneler')==1.40625,'gigantic-sandworm-tunneler lightning above the head (head top y=21)')
ok(Style.standeeHeight('heavy-sentinel')==1.546875,'heavy-sentinel orange glow above the skull (skull top y=13)')
ok(Style.standeeHeight('uruivellas')==1.296875,'uruivellas fiery aura above the horns (horn top y=29)')
ok(Style.standeeHeight('boiling-horror')==1.0,'boiling-horror steam is a particle; the ball is ~1 cell')
ok(Style.standeeHeight('ogre-warmaster')==1.390625,'ogre-warmaster helmet is the alpha top; derived cap kept')
ok(Style.standee_height_override['ogre-warmaster']==nil,'ogre-warmaster needs no override')
ok(Style.standeeHeight('norgos-frozen')==1.359375,'norgos-frozen ice mist trimmed; ears count')
ok(Style.standeeHeight('ak-gishil')==1.34375,'ak-gishil floating swords trimmed; head/arms count')
-- Body parts count: minotaur horns, walrog head water-horns, burb horned helm.
ok(Style.standeeHeight('minotaur-maze')==1.453125,'minotaur-maze horns count, derived cap kept')
ok(Style.standeeHeight('walrog')==1.609375,'walrog head water-horns count, derived cap kept')
ok(Style.standeeHeight('burb-snow-giant-champion')==1.53125,'burb override drops the lightning above the horns')
ok(Style.standeeHeight('elandar')==1.0,'elandar staff does not count; body is flat')
ok(Style.standeeHeight('emperor-wight')==1.0 and Style.standeeHeight('naga-nereid')==1.0
 and Style.standeeHeight('naga-tidewarden')==1.0,'R40 raised-sword/trident ids stay flat')
ok(Style.standee_height_override['kra-tor']==1.0,'kra-tor axe over a ~1-cell body is flat')
ok(Style.standee_height_override['snow-giant']==nil
 and Style.standee_height_override['ravenous-horror']==nil
 and Style.standee_height_override['ninandra']==1.140625,
 'the remaining shipped weapon standees keep the derived cap; ninandra trims the head glow')
ok(Style.standeeHeight('ogre-guard')==1.078125,'ogre-guard trims the hammer and floating top speck (head top y=43)')
ok(Style.standee_size_height==nil and Style.standee_height_medium==nil,'the size_category table and medium fallback are gone')
ok(Style.standeeSizeAllowed==nil,'the size gate is removed')
ok(Tokens.standee_min_rank==nil and Tokens.standee_demo_ids==nil,'the rank threshold and demo list are removed')

-- 2. Static rule: native-tall only, decided from the committed table.
ok(Tokens.standeeRule(Tokens.by_id['snow-giant'])==true,'native-tall snow-giant is eligible')
ok(Tokens.standeeRule(Tokens.by_id['kra-tor'])==false,'kra-tor body-only cap is 1.0 (flat)')
ok(Tokens.standeeRule(Tokens.by_id['ravenous-horror'])==true,'native-tall ravenous-horror is eligible')
ok(Tokens.standeeRule(Tokens.by_id['phoenix'])==false,'native 1-cell phoenix is not eligible, despite rank 3.5')
ok(Tokens.standeeRule(Tokens.by_id['vor'])==false,'native 1-cell vor is not eligible')
ok(Tokens.standeeRule(Tokens.by_id['wolf'])==false,'a non-tall ordinary body is not eligible')
ok(Tokens.standeeRule(Tokens.by_id['lich'])==false,'a native-tall id with a 1.0 cap is flat')
ok(Tokens.standeeRule(Tokens.by_id['gorbat'])==false,'gorbat is native-tall but flat by height')
ok(Tokens.standeeRule(nil)==false,'missing entry is not eligible')
-- The rule takes only the entry: rank and live size_category are never read.
local geom=dofile(root..'data/token-layer-geometry.lua')
-- Every shipped standee id, read from the runtime module so a new standee is
-- covered automatically instead of a hard-coded list drifting behind it.
local standee_ids={}
for id in pairs(Tokens.standee_ids) do standee_ids[#standee_ids+1]=id end
table.sort(standee_ids)
ok(#standee_ids>0,'the standee id list is non-empty')
-- R46 explicit floor: the original four shipped standee ids remain a subset.
local floor_ids={['ninandra']=true,['ogre-guard']=true,['snow-giant']=true,['ravenous-horror']=true}
for id in pairs(floor_ids) do ok(Tokens.standee_ids[id]==true,id..' original standee id still ships') end
Tokens.layer_geometry=geom
-- R46: for EVERY shipped standee id BOTH gates must be true.
for _,id in ipairs(standee_ids) do
 local entry=Tokens.by_id[id]
 ok(entry~=nil,id..' has a catalogue entry')
 ok(Tokens.standeeRule(entry)==true,id..' standeeRule is true')
 ok(Tokens.standeeEligible({rank=1,size_category=1},entry)==true,id..' standeeEligible is true')
end
ok(Tokens.standeeEligible({rank=10,size_category=6},Tokens.by_id['lich'])==false,'rank/size cannot grant a flat id a standee')
ok(Tokens.standeeEligible({rank=1,size_category=1},Tokens.by_id['snow-giant'])==true,'a small live actor still gets its native-tall standee')
ok(Tokens.standeeEligible({rank=1,size_category=1},Tokens.by_id['ogre-guard'])==true,'a buffed size never flips the token')
ok(Tokens.standeeEligible({rank=10,size_category=6},Tokens.by_id['wolf'])==false,'no standee layer for the id')
ok(Tokens.standeeEligible({rank=10},Tokens.by_id['phoenix'])==false,'rank alone never grants a standee')
Tokens.standee_trial=false
ok(Tokens.standeeEligible({rank=4,size_category=3},Tokens.by_id['snow-giant'])==false,'switch off keeps the flat path')
Tokens.standee_trial=true
ok(Tokens.standeeEligible({rank=4},nil)==false,'missing entry keeps the flat path')

-- 3. Tile gate: standees only at >= 24px, flat below (16px and small customs).
for _,cell in ipairs{24,32,48,64,96,128} do
 ok(Tokens.standeeTileAllowed(cell)==true,'standee allowed at '..cell..'px')
 ok(Style.standeeCellAllowed(cell)==true,'style allows '..cell..'px')
end
for _,cell in ipairs{6,10,16,23,23.9} do
 ok(Tokens.standeeTileAllowed(cell)==false,'flat at '..cell..'px')
 ok(Style.standeeCellAllowed(cell)==false,'style flat at '..cell..'px')
end
ok(Tokens.standeeTileAllowed(nil)==false,'unknown tile size keeps the flat token')
ok(Tokens.standeeTileAllowed('48')==true,'a numeric string is accepted')

-- 4. The generated height table: native-tall set, clamp range, flat markers.
local heights=Style.standee_heights
local total,flats=0,0
for _,value in pairs(heights) do
	total=total+1
	ok(type(value)=='number','the height table holds numbers')
	ok(value>=1.0 and value<=1.75,'height is clamped to [1.0, 1.75]')
	if value<=1.0 then flats=flats+1 end
end
ok(total==151,'151 native-tall ids in the generated table')
ok(flats==31,'31 native-tall ids are flat (cap 1.0)')
ok(heights['snow-giant']==1.40625 and heights['ogre-guard']==1.421875,'snow-giant/ogre-guard committed caps')
ok(heights['kra-tor']==1.140625 and heights['ravenous-horror']==1.25 and heights['ninandra']==1.265625,'kra-tor/ravenous-horror/ninandra committed caps')
ok(heights['gorbat']==1.0 and heights['bone-giant']==1.0 and heights['lich']==1.0,'gorbat/bone-giant/lich are flat')
ok(heights['phoenix']==nil and heights['vor']==nil,'native 1-cell ids have no table entry')
ok(heights['rungof']==nil,'rungof is not native-tall')

-- 5. Pure geometry with a real committed box and cap.
local CELL=48
local DISC_D=CELL*Style.token_diameter
local function close(a,b) return math.abs(a-b)<1e-9 end
local box=geom['ogre-guard']
local cap=Style.standeeHeight('ogre-guard')
local left,top,size=Style.standeeQuad(CELL,box,box.canvas,CELL/2,CELL/2,DISC_D,cap)
local scale=size/box.canvas
-- R42: feet-to-body_top is scaled to the cap; a raised weapon above body_top
-- may stick out above. The whole art is still width-capped.
local body_h=box.bottom-(box.body_top or box.top)
ok(close(body_h*scale,cap*CELL) or (box.right-box.left)*scale<=Style.standee_width*CELL+1e-9,'body height cap or width cap binds')
ok((box.bottom-box.top)*scale>=body_h*scale-1e-9,'the full art is never shorter than the body')
ok((box.right-box.left)*scale<=Style.standee_width*CELL+1e-9,'width stays inside the cap')
ok(close(left+((box.left+box.right)/2)*scale,CELL/2),'creature is horizontally centred on the disc')
ok(close(top+box.bottom*scale,CELL/2+Style.standee_feet*DISC_D/2),'feet sit at disc centre + .55 radius')
ok(size>0,'a valid box draws a quad')
-- Synthetic raised weapon: the body stays at the cap and the weapon sticks out.
local synth={left=88,top=0,right=168,bottom=200,canvas=256,body_top=80}
local _,stop,ssize=Style.standeeQuad(CELL,synth,256,CELL/2,CELL/2,DISC_D,1.5)
local sscale=ssize/256
ok(close((synth.bottom-synth.body_top)*sscale,1.5*CELL),'a raised weapon does not squash the body')
ok((synth.bottom-synth.top)*sscale>1.5*CELL,'the raised weapon sticks out above the body cap')
ok(close(stop+synth.bottom*sscale,CELL/2+Style.standee_feet*DISC_D/2),'the synthetic body still anchors its feet')
-- body_top defaults to the alpha top when the geometry has no reviewed value.
local _,_,dsize=Style.standeeQuad(CELL,{left=88,top=20,right=168,bottom=220,canvas=256},256,CELL/2,CELL/2,DISC_D,1.5)
ok(close((220-20)*(dsize/256),1.5*CELL),'missing body_top defaults to the alpha top')
-- A missing/!number cap or an invalid box returns nil so the caller falls back.
ok(Style.standeeQuad(CELL,box,box.canvas,CELL/2,CELL/2,DISC_D,nil)==nil,'missing cap rejected')
ok(Style.standeeQuad(CELL,box,box.canvas,CELL/2,CELL/2,DISC_D,'x')==nil,'non-number cap rejected')
ok(Style.standeeQuad(CELL,{left=5,top=5,right=5,bottom=5},box.canvas,0,0,DISC_D,cap)==nil,'zero box rejected')
ok(Style.standeeQuad(CELL,nil,box.canvas,0,0,DISC_D,cap)==nil,'missing box rejected')
-- Geometry is a pure cell function and scales linearly.
local _,_,s64=Style.standeeQuad(64,box,box.canvas,32,32,64*Style.token_diameter,cap)
ok(close(s64/size,64/48),'standee scales linearly with the cell')

-- 6. Draw harness: a standee draws its enlarged creature above the own cell in
-- the overlay pass, while the ring/badge/bar stay in the own cell.
local base=Style.token_diameter/Style.art_occupancy
local draws={}
local function newVO()
 return {quads={},addQuad=function(self,r,g,b,a,p1,p2,p3,p4)
   self.quads[#self.quads+1]={p1,p2,p3,p4};self.color={r,g,b}
  end,toScreen=function(self,x,y,tex)
   -- Record absolute screen coords (the cached VO is built local to the box
   -- origin and translated by toScreen) so the geometry assertions below see
   -- the same values as before the R41 cache.
   local q={}
   for i,quad in ipairs(self.quads) do
    local qq={}
    for j,pt in ipairs(quad) do qq[j]={pt[1]+x,pt[2]+y,pt[3],pt[4]} end
    q[i]=qq
   end
   draws[tex.name]=q
  end}
end
local map={actor_player={canSee=function() return true end,reactionToward=function() return -1 end},view_faction='players',
 tiles={get=function(_,...)
  local name=select(8,...)
  return {name=name,toScreenFull=function(self,...) draws[name]=(draws[name] or 0)+1 end},1,1
 end}}
local testOptions={}
local env=setmetatable({loadPrevious=function() return {} end,
 require=function(name) return name=='mod.class.CheckerTokenStyle' and Style or name=='mod.class.CheckerTokens' and Tokens
  or name=='mod.class.CheckerOptions' and testOptions or {} end,
 core={display={newVO=newVO}}},{__index=_G})
config={settings={tome={checker_relation_colors={},checker_rank_colors={}}}}
local chunk=assert(loadfile(root..'superload/mod/class/Actor.lua'));setfenv(chunk,env)
local Actor=chunk()

local function actor(id,standee)
 local a=setmetatable({life=50,max_life=100,rank=4,size_category=1,
  _checker_token={id=id,scale=base,layered=true,layer_id=id,
   standee=standee and true or nil,layer_box=standee and geom[id] or nil}},
  {__index=Actor})
 function a:attr(k) return self[k] end
 return a
end

draws={}
local a=actor('ogre-guard',true)
a:checkerLayerCreature(map,0,0,48*base,48*base)
local quad=draws['checker-revised+tokens-layer/ogre-guard.png']
ok(quad and #quad==1,'standee draws one creature quad')
local miny,maxy=math.huge,-math.huge
for _,p in ipairs(quad[1]) do miny=math.min(miny,p[2]);maxy=math.max(maxy,p[2]) end
ok(miny<-1e-6,'standee extends above its own cell (over the row above)')
ok(maxy>0,'standee overlaps its own cell')
-- The draw path is size_category independent: a size-1 actor draws the same cap.
local before=draws
draws={}
local a1=actor('snow-giant',true)
a1:checkerLayerCreature(map,0,0,48*base,48*base)
ok(draws['checker-revised+tokens-layer/snow-giant.png'] and #draws['checker-revised+tokens-layer/snow-giant.png']==1,'draw path ignores live size')
draws=before
-- The ring pass draws only the ring; the badge pass draws only the badge/bar.
draws={};a:checkerTacticalFrame(map,0,0,48*base,48*base,true,'ring')
ok(draws['checker-revised+tokens/_relation-enemy.png'],'ring pass draws the faction ring in the own cell')
ok(not draws['checker-revised+tokens/_badge-boss.png'],'ring pass does not draw the badge')
draws={};a:checkerTacticalFrame(map,0,0,48*base,48*base,true,'badge')
ok(draws['checker-revised+tokens/_badge-boss.png'],'badge pass draws the rank badge in the own cell')
ok(not draws['checker-revised+tokens/_relation-back.png'],'badge pass does not redraw the ring')
-- The ordinary (non-standee) layer keeps its cell clip.
draws={}
local b=setmetatable({life=50,max_life=100,rank=2,
 _checker_token={scale=base,layered=true,layer_id='wolf',layer_box=geom['wolf']}},{__index=Actor})
function b:attr(k) return self[k] end
b:checkerLayerCreature(map,0,0,48*base,48*base)
local oq=draws['checker-revised+tokens-layer/wolf.png']
ok(oq and #oq==1,'ordinary layer draws one clipped quad')
for _,p in ipairs(oq[1]) do
 ok(p[1]>=-1e-6 and p[1]<=48+1e-6 and p[2]>=-1e-6 and p[2]<=48+1e-6,'ordinary creature stays inside the cell')
end

-- 7. Archived ids are not loaded and cannot request a layer file.
for _,id in ipairs{'rungof','grushnak','vor','phoenix','shardskin','subject-z','gorbat','bone-giant','kra-tor'} do
 ok(Tokens.standee_ids[id]==nil,id..' is not a standee id')
 ok(Tokens.layer_ids[id]==nil,id..' is not an ordinary layer id')
 ok(Tokens.layer_file_ids[id]==nil,id..' is not a layer file id')
 ok(Tokens.layerImage(id)==nil,id..' has no layer image')
end
-- Every shipped standee still resolves to its 256px layer file.
for _,id in ipairs(standee_ids) do
 ok(Tokens.layerImage(id)=='checker-revised+tokens-layer/'..id..'.png',id..' keeps its layer image')
 ok(Tokens.layer_geometry[id].canvas==256,id..' keeps the 256px canvas')
end

-- 8. Source drift: the draw path and the Game.lua gate must stay in step.
local f=assert(io.open(root..'superload/mod/class/Actor.lua','r'))
local src=f:read('*a');f:close()
ok(src:find('if state.standee and state.layer_box then',1,true),'standee branch present')
ok(src:find('Style.standeeQuad',1,true),'standee uses the shared geometry function')
ok(src:find('Style.standeeHeight(state.id)',1,true),'standee height is read statically by id')
ok(not src:find('Style.standeeHeight(self.size_category',1,true),'the live size_category is not consulted')
local g=assert(io.open(root..'superload/mod/class/Game.lua','r'))
local gsrc=g:read('*a');g:close()
ok(gsrc:find('Tokens.standeeEligible(e,entry) and standee_tile_ok',1,true),'Game.lua applies the 24px tile gate to the standee')
ok(gsrc:find('elseif tile_ok and Tokens.layeredId(id) then',1,true),'ordinary path keeps its own switch and <=48px cell gate')

-- 9. Rank badge: scaled to the cell at <=16px so it no longer covers most of
-- the token (R39 fix d).
local bw16,bh16=Style.badgeSize(16)
ok(bw16==6 and bh16==5,'16px rank badge is 6x5')
ok(bw16<16*.5,'the 16px badge covers less than half the token width')
local bw10,bh10=Style.badgeSize(10)
ok(bw10==4 and bh10==3,'10px rank badge scales down to 4x3')
local bw24,bh24=Style.badgeSize(24)
ok(bw24==12 and bh24==9,'24px keeps the historic 12x9 floor')
local bw48,bh48=Style.badgeSize(48)
ok(math.abs(bw48-12)<1e-9 and math.abs(bh48-9)<1e-9,'48px badge 12x9')
ok(src:find('Style.badgeSize(g.cell)',1,true),'Actor.lua draws the badge with the shared helper')

-- 10. Standee auras: the aura box must follow the standee quad. The native
-- aura add_mo (image_alter sdm) is built from the flat disc at a fixed
-- display_h=2/display_y=-1; for a standee it must use the standee layer at the
-- standee quad, in cell units, so a native straight-scaled aura wraps the
-- upright figure.
ok(type(Style.standeeAuraQuad)=='function','standee aura geometry helper exists')
-- R42/R43: the aura is a POT copy of the standee layer scaled so the aura
-- quad is the BODY height plus ~0.4 cell of headroom above body_top, not a pad
-- on every side. The SDM shader draws the flames over the whole aura quad, so
-- the quad diagonal must stay near a native 1x2 tall sprite (2.24 cells); R41's
-- 128px pad on every side made it 4.63 cells and the flames ~2x native. The
-- creature must still line up with the creature quad. The cap comes from the
-- PRODUCTION lookup Style.standeeHeight(id), so a body-only override is tested.
-- AURA_MIN_QUAD_CELLS keeps a small body's aura at native-diagonal size, so
-- every shipped standee's diagonal is inside the 2.2-2.6 target; a small body
-- gets more than the 0.4-cell body headroom and that extra is transparent
-- space. The quad is read EXACTLY as max(body + 0.4, art + gate_headroom, AURA_MIN):
-- body/art are the scaled layer heights and AURA_MIN is parsed from the tool.
local pyh=assert(io.open(root..'tools/build_token_layers.py','r'))
local pytxt=pyh:read('*a');pyh:close()
local AURA_MIN_QUAD_CELLS=tonumber(pytxt:match('AURA_MIN_QUAD_CELLS%s*=%s*([0-9%.]+)'))
ok(AURA_MIN_QUAD_CELLS and math.abs(AURA_MIN_QUAD_CELLS-math.sqrt(2.5))<1e-6,
 'AURA_MIN_QUAD_CELLS equals sqrt(2.5), the native-diagonal square')
-- R46 tall aura shape. H = max(body + 0.4, art + gate_headroom); SQUARE when
-- H*sqrt(2) <= 2.6 with S = max(H, sqrt(2.5)) on a 256x256 texture, else TALL
-- with h = max(H, 2.0), w = h/2 on a 128x256 texture (isotropic, POT). The
-- texture aspect must equal the quad aspect. The constants and the branch are
-- parsed from the tool so the Lua helper tracks build_aura.
local AURA_TALL_DIAG=tonumber(pytxt:match('AURA_TALL_DIAG_CELLS%s*=%s*([0-9%.]+)'))
local AURA_TALL_MIN=tonumber(pytxt:match('AURA_TALL_MIN_CELLS%s*=%s*([0-9%.]+)'))
local tall_w,tall_h=pytxt:match('AURA_TALL_W,%s*AURA_TALL_H%s*=%s*(%d+),%s*(%d+)')
ok(AURA_TALL_DIAG==2.6 and AURA_TALL_MIN==2.0 and tonumber(tall_w)==128 and tonumber(tall_h)==256,
 'tall aura constants: diag 2.6, min h 2.0, texture 128x256')
ok(pytxt:find('h_need * math.sqrt(2) <= AURA_TALL_DIAG_CELLS',1,true)
 and pytxt:find('canvas_w, canvas_h = AURA_TALL_W, AURA_TALL_H',1,true)
 and pytxt:find('if h_need * math.sqrt(2) <= AURA_TALL_DIAG_CELLS:',1,true)
 and pytxt:find("ox = canvas_w / 2 - ((box['left'] + box['right']) / 2) * r",1,true)
 and pytxt:find("oy = canvas_h - box['bottom'] * r",1,true),
 'build_aura has the SQUARE/TALL branch and the tall centring')
-- R50: the builder and live k floor read the same shared contract.
local ch=assert(io.open(root..'tools/standee_aura_contract.json','r'))
local contract=ch:read('*a');ch:close()
local flame_floor=assert(tonumber(contract:match('"AURA_FLAME_ABOVE_TOP_FLOOR_CELLS"%s*:%s*([0-9%.]+)')))
local tip_budget=assert(tonumber(contract:match('"AURA_TIP_BUDGET_CELLS"%s*:%s*([0-9%.]+)')))
local gate_headroom=flame_floor+tip_budget
ok(flame_floor==0.3 and tip_budget==0.2 and gate_headroom==0.5,'shared live floor 0.3 plus tip budget 0.2')
-- Shipped art <=1.75, so h<=1.75+0.5=2.25, diag<=2.25*sqrt(5)/2.
local TALL_DIAG_BOUND=2.25*math.sqrt(5)/2
local function auraShape(body_cells,art_cells)
 local H=math.max(body_cells+0.4,art_cells+gate_headroom)
 if H*math.sqrt(2)<=AURA_TALL_DIAG then
  local S=math.max(H,AURA_MIN_QUAD_CELLS)
  return 256,256,S,S
 end
 local h=math.max(H,AURA_TALL_MIN)
 return 128,256,h/2,h
end
-- Synthetic maximum shipped case: body=art=1.75 -> H=2.25, w=1.125.
local scw,sch,sw,sh=auraShape(1.75,1.75)
ok(scw==128 and sch==256,'synthetic body 1.75 / art 1.75 is TALL')
ok(math.abs(sw-1.125)<0.01 and math.abs(sh-2.25)<0.01,'synthetic TALL w=1.125 h=2.25')
ok(math.abs(math.sqrt(sw*sw+sh*sh)-TALL_DIAG_BOUND)<0.01,'synthetic TALL diagonal 2.25*sqrt(5)/2')
-- Synthetic square case: body=1.0, art=1.0 -> H=1.4 -> S=max(1.4,sqrt(2.5)).
local qcw,qch,qw,qh=auraShape(1.0,1.0)
ok(qcw==256 and qch==256 and math.abs(qw-math.sqrt(2.5))<0.01 and qw==qh,'small body stays the SQUARE min')
for _,id in ipairs(standee_ids) do
 local b=geom[id]
 local aura=b.aura
 ok(type(aura)=='table','POT aura box ships for '..id)
 ok(type(aura.canvas_w)=='number' and type(aura.canvas_h)=='number',id..' records the aura texture size')
 ok(aura.canvas==aura.canvas_h,id..' canvas keeps the texture height')
 ok(type(aura.body_top)=='number' and type(b.body_top)=='number',id..' records body_top for layer and aura')
 ok(b.body_top>=b.top and b.body_top<b.bottom,id..' body_top is inside the layer art')
 ok(aura.body_top>=aura.top and aura.body_top<aura.bottom,id..' aura body_top is inside the aura art')
 local cap=Style.standeeHeight(id)
 local dx,dy,w,h=Style.standeeAuraQuad(aura,aura.canvas_w,aura.canvas_h,cap)
 ok(dx~=nil and dy~=nil and w~=nil and h~=nil and w>0 and h>0,id..' aura box exists')
 local aleft,atop,asize=Style.standeeQuad(48,b,b.canvas,24,24,48*Style.token_diameter,cap)
 local factor=w/aura.canvas_w
 ok(close(factor,h/aura.canvas_h),id..' aura quad aspect equals the texture aspect')
 local cscale=asize/b.canvas
 -- The layer is scaled into the aura canvas; the recorded aura box is that
 -- scaled bbox. The aura factor is the creature scale divided by the layer
 -- scale r, so aura pixels land on the same screen positions.
 local r=(aura.bottom-aura.body_top)/(b.bottom-b.body_top)
 ok(close(factor*48, cscale/r),id..' aura creature scale matches the standee quad')
 local acx=(dx+aura.left*factor)*48
 local ccy=aleft+b.left*cscale
 -- The aura texture is a resampled copy, so its measured bbox can sit up to a
 -- pixel off the exact layer map; require < 0.75px at a 48px cell.
 ok(math.abs(acx-ccy)<0.75 and math.abs((dy+aura.top*factor)*48-(atop+b.top*cscale))<0.75,id..' aura content aligns with the creature quad')
 ok(close(dx,0.5-((aura.left+aura.right)/2)*factor) and close(w,aura.canvas_w*factor) and close(h,aura.canvas_h*factor),id..' aura quad uses the recorded texture size')
 -- Native facing mirrors about the creature axis at the texture centre: the
 -- quad must place that centre at the cell centre within 1 texture px. The
 -- measured aura bbox has integer left/right, so a perfectly centred art
 -- axis can read as exactly 1.0 px off (ravenous-horror sat on this boundary
 -- and passed only by a floating-point rounding of `margin < factor`); the
 -- documented "within 1 texture px" tolerance is therefore inclusive.
 ok(math.abs(dx+w/2-0.5)<=factor*(1+1e-9),id..' aura is centred for the native-facing mirror')
 -- ~0.4 cell of headroom above the body (more when a small body's square is
 -- floored at AURA_MIN_QUAD_CELLS), a positive margin above the art, and the
 -- exact shape formula. The formula is exact in build_aura; the recorded aura
 -- box is a resampled copy, so compare with a small resample tolerance.
 local s_c=math.min(cap/(b.bottom-b.body_top),Style.standee_width/(b.right-b.left))
 local body_cells=(b.bottom-b.body_top)*s_c
 local art_cells=(b.bottom-b.top)*s_c
 local H=math.max(body_cells+0.4,art_cells+gate_headroom)
 local ecw,ech,ew,eh=auraShape(body_cells,art_cells)
 ok(aura.canvas_w==ecw and aura.canvas_h==ech and math.abs(w-ew)<0.01 and math.abs(h-eh)<0.01,id..' aura shape follows H=max(body+0.4, art+gate_headroom)')
 if H*math.sqrt(2)<=AURA_TALL_DIAG then
  ok(aura.canvas_w==256 and aura.canvas_h==256 and math.abs(w-math.max(H,AURA_MIN_QUAD_CELLS))<0.01,id..' SQUARE S=max(H, sqrt(2.5)), 256x256')
 else
  ok(aura.canvas_w==128 and aura.canvas_h==256 and math.abs(h-math.max(H,AURA_TALL_MIN))<0.01 and math.abs(w-h/2)<0.01,id..' TALL h=max(H, 2), w=h/2, 128x256')
 end
 ok(aura.body_top*factor>=0.35,id..' aura keeps at least the R42 headroom above the body')
 ok(aura.top*factor>=gate_headroom-1e-9,id..' aura keeps the shared gate headroom above art')
 ok(aura.top*factor<=math.max(gate_headroom, AURA_TALL_MIN-art_cells)+1e-9,id..' aura top headroom follows the floor and shared budget')
 local diag=math.sqrt(w*w+h*h)
 ok(diag>=2.2 and diag<=2.6,id..' aura quad diagonal stays near native (~2.24 cells)')
 if aura.canvas_w==128 then ok(diag<=TALL_DIAG_BOUND+1e-9,id..' TALL diagonal <= 2.25*sqrt(5)/2') end
end
ok(Style.standeeAuraQuad(geom['ogre-guard'].aura,256,256,nil)==nil,'missing cap rejected for the aura')
ok(Style.standeeAuraQuad(nil,256,256,1.1)==nil,'missing box rejected for the aura')
ok(Style.standeeAuraQuad({left=1,top=1,right=1,bottom=1},256,256,1.1)==nil,'zero aura box rejected')
ok(Style.standeeAuraQuad(geom['ogre-guard'].aura,0,256,1.1)==nil,'zero texture width rejected')
ok(Style.standeeAuraQuad(geom['ogre-guard'].aura,256,nil,1.1)==nil,'missing texture height rejected')
-- Actor rewrite: a standee moves both aura entries onto the standee layer at
-- the standee quad; a flat token and a foreign display are left alone.
local function aura_env()
 return setmetatable({image='checker-revised+tokens-layer/_disc.png',display_h=base,display_y=0,
  add_mos={{_isshaderaura=true,image_alter='sdm',sdm_double=true,image='disc.png',shader='awesomeaura',display_h=2,display_y=-1},
   {_isshaderaura=true,image='disc.png',display_y=base,display_h=base}}},{})
end
local function aura_actor(id,standee)
 local display=aura_env()
 local a=setmetatable({life=50,max_life=100,rank=4,size_category=1,
  _checker_token={id=id,scale=base,layered=true,layer_id=id,standee=standee and true or nil,
   layer_box=standee and geom[id] or nil,layer_aura=standee and geom[id].aura or nil}},{__index=Actor})
 function a:attr(k) return self[k] end
 a.replace_display=display
 a._checker_token.display=display
 return a,display
end
local ad,display=aura_actor('ogre-guard',true)
ad:checkerStandeeAura()
local layer=Tokens.layerAuraImage('ogre-guard')
ok(display.add_mos[1].image==layer,'standee aura uses the POT aura texture')
ok(display.add_mos[2].image=='invis.png','standee base redraw draws nothing (the overlay draws the creature once)')
ok(display.add_mos[1].sdm_double==false,'the 256px square aura keeps sdm_double=false')
ok(display.add_mos[1]._checker_standee_aura==true and display.add_mos[2]._checker_standee_base==true,'both aura entries are marked')
ok(display.add_mos[2]._checker_standee_aura==nil,'the invis base copy is not an sdm aura')
local adx,ady,adw,adh=Style.standeeAuraQuad(geom['ogre-guard'].aura,geom['ogre-guard'].aura.canvas_w,geom['ogre-guard'].aura.canvas_h,Style.standeeHeight('ogre-guard'))
ok(close(display.add_mos[1].display_x,adx) and close(display.add_mos[1].display_y,ady) and close(display.add_mos[1].display_w,adw) and close(display.add_mos[1].display_h,adh),'aura entry display box is the POT aura box')
ok(close(display.add_mos[1].display_w,display.add_mos[1].display_h),'the square shipped aura keeps display_w=display_h')
-- R48 item 4: the TALL 1:2 branch through PRODUCTION code. A synthetic box
-- (canvas 128x256, cap 1.75) must give a non-square display, aspect 1:2, a
-- diagonal <= 2.25*sqrt(5)/2 and a texture-centre cell placed within 1 texture px of 0.5.
local synth_tall={left=12,top=48,right=116,bottom=256,canvas=256,canvas_w=128,canvas_h=256,body_top=48}
local tdx,tdy,tw,th=Style.standeeAuraQuad(synth_tall,128,256,1.75)
ok(tdx~=nil and tdy~=nil and tw~=nil and th~=nil,'synthetic TALL aura box exists')
ok(tw~=th,'synthetic TALL aura display_w ~= display_h')
ok(math.abs(th/tw-2)<0.02,'synthetic TALL aura display aspect is 1:2')
ok(math.sqrt(tw*tw+th*th)<=TALL_DIAG_BOUND+1e-9,'synthetic TALL aura diagonal <= 2.25*sqrt(5)/2')
ok(math.abs(tdx+tw/2-0.5)<1/128,'synthetic TALL aura centred within 1 texture px')
-- The checkerStandeeAura rewrite on a REAL shipped TALL id must set the same
-- non-square display box on the sdm aura add_mo.
local tdd,tld=aura_actor('heavy-bone-giant',true)
tdd:checkerStandeeAura()
local tamo=tld.add_mos[1]
ok(tamo.image==Tokens.layerAuraImage('heavy-bone-giant'),'real TALL aura uses the POT aura texture')
ok(tamo.sdm_double==false,'the TALL aura keeps sdm_double=false')
ok(not close(tamo.display_w,tamo.display_h),'real TALL aura display_w ~= display_h')
ok(math.abs(tamo.display_h/tamo.display_w-2)<0.02,'real TALL aura display aspect is 1:2')
ok(math.sqrt(tamo.display_w^2+tamo.display_h^2)<=TALL_DIAG_BOUND+1e-9,'real TALL aura diagonal <= 2.25*sqrt(5)/2')
ok(math.abs(tamo.display_x+tamo.display_w/2-0.5)<1/128,'real TALL aura centred within 1 texture px')
-- Flat token: untouched.
local fd,fdisp=aura_actor('snow-giant',false)
fd:checkerStandeeAura()
ok(fdisp.add_mos[1].image=='disc.png' and fdisp.add_mos[1].sdm_double==true,'flat token keeps the native disc aura')
-- Foreign display: untouched.
local xd,xdisp=aura_actor('ogre-guard',true)
xd.replace_display=aura_env()
xd:checkerStandeeAura()
ok(xdisp.add_mos[1].image=='disc.png','a foreign display is never rewritten')

-- 10b. Sequential auras: native updateModdableTilePrepare only inserts aura
-- add_mos when the display add_mos is nil, so a later add/remove on an
-- installed token silently keeps the stale set. checkerSyncTokenAura clears
-- the stale entries exactly when the roster changed and leaves it alone
-- otherwise.
local sq,sqdisp=aura_actor('ogre-guard',true)
sqdisp.add_mos={}
sq.shader_auras={}
sq:checkerSyncTokenAura()
ok(sq._checker_token.aura_sig=='','sync records the empty roster')
sq.shader_auras={body_of_fire=1}
sq:checkerSyncTokenAura()
ok(sq._checker_token.aura_sig=='body_of_fire','sync sees the first aura')
sq.shader_auras={body_of_fire=1,essence_of_the_dead=1}
sqdisp.add_mos={{_isshaderaura=true,image='stale'}}
sq:checkerSyncTokenAura()
ok(sq._checker_token.aura_sig=='body_of_fire,essence_of_the_dead','sync sees the second aura')
ok(sqdisp.add_mos==nil,'a changed roster clears the stale _isshaderaura entries')
sqdisp.add_mos={{_isshaderaura=true,image='stale'}}
sq:checkerSyncTokenAura()
ok(sqdisp.add_mos~=nil,'an unchanged roster clears nothing')
sq.shader_auras={}
sq:checkerSyncTokenAura()
ok(sqdisp.add_mos==nil,'removing the last aura clears the stale entries')

-- 11. Native facing: the overlay creature is a separate MO the engine never
-- flips, so the recorded body flip must mirror its texture in place (about the
-- standee box centre) while leaving the destination geometry alone. A fixed
-- body flip (fixed facing) must draw the unmirrored UVs.
local function draw_flipped(flip)
 local act=actor('ogre-guard',true)
 act._checker_token.body_flip=flip
 draws={}
 act:checkerLayerCreature(map,0,0,48*base,48*base)
 return draws['checker-revised+tokens-layer/ogre-guard.png'][1]
end
local q0=draw_flipped(false)
local q1=draw_flipped(true)
ok(q0 and q1,'both facing draws produce a creature quad')
local txsum=q0[1][3]+q0[3][3]
for i=1,4 do
 ok(close(q0[i][1],q1[i][1]) and close(q0[i][2],q1[i][2]),'facing flip never moves the destination quad')
 ok(close(q0[i][3]+q1[i][3],txsum),'facing flip mirrors the U texture coordinate')
end
-- MOflipX records the applied body flip. Native facing follows the requested
-- direction; fixed facing forces the body unflipped and records false.
local mf=actor('ogre-guard',true)
mf._mo={flipX=function(self,v) self.v=v end}
testOptions.tokenFacing=function() return 'native' end
mf:MOflipX(true)
ok(mf._checker_token.body_flip==true,'native MOflipX records the body flip')
mf:MOflipX(false)
ok(mf._checker_token.body_flip==false,'native MOflipX clears the body flip')
testOptions.tokenFacing=function() return 'fixed' end
mf:MOflipX(true)
ok(mf._mo.v==false and mf._checker_token.body_flip==false,'fixed facing forces the body unflipped')
testOptions.tokenFacing=nil

-- 12. Wide-body path: the 1.0-cell width cap actually binds when the alpha
-- bbox is wider than tall, and the aura box follows the width-capped quad.
local wide={left=40,top=60,right=216,bottom=196,canvas=256}
local wcap=1.5
local _,_,wsize=Style.standeeQuad(48,wide,256,24,24,48*Style.token_diameter,wcap)
local wscale=wsize/256
ok(close((wide.right-wide.left)*wscale,Style.standee_width*48),'width cap binds for a wide standee')
ok((wide.bottom-wide.top)*wscale<wcap*48,'wide standee ends up shorter than its height cap')
local wdx,wdy,wdw,wdh=Style.standeeAuraQuad(wide,256,256,wcap)
local wl,wt,ws=Style.standeeQuad(48,wide,256,24,24,48*Style.token_diameter,wcap)
ok(close(wdw*48,ws) and close(wdh*48,ws) and close(wdx*48,wl) and close(wdy*48,wt),'wide aura box follows the width-capped quad')

print('token_standee: '..checks..' static-rule, height-table, tile-gate, geometry, draw-pass, archive, badge, aura and wide-body checks passed')
