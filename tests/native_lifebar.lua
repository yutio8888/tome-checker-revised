-- The board token shows the engine's own tactical life bar. Rather than trust a
-- copied geometry, this parses game/modules/tome/class/Actor.lua at the cited
-- line ranges and asserts that Style.native_life_bar still equals it, then
-- exercises the helper and the native mode choice.
local script=debug.getinfo(1,'S').source:sub(2)
local root=(script:match('^(.*[/\\])') or './')..'../'
local Style=dofile(root..'overload/mod/class/CheckerTokenStyle.lua')
local B=Style.native_life_bar

local path=root..'../../modules/tome/class/Actor.lua'
local f=assert(io.open(path,'r'),'native Actor.lua not found: '..path)
local src=f:read('*a');f:close()
local lines={}
for line in (src..'\n'):gmatch('(.-)\n') do lines[#lines+1]=line end
local function slice(a,b)
 local out={}
 for i=a,b do out[#out+1]=lines[i] or error('native Actor.lua line '..i..' missing') end
 return table.concat(out,'\n')
end
local checks=0
local function contains(text,needle,what)
 assert(text:find(needle,1,true),'native Actor.lua drifted: '..what..' ('..needle..')')
 checks=checks+1
end
local function number(text,value,what)
 local printed=tostring(value)
 if not text:find(printed,1,true) then
  -- Native writes some fractions without the leading zero.
  assert(printed:sub(1,2)=='0.',what..' expects '..printed)
  contains(text,printed:sub(2),what)
 else
  contains(text,printed,what)
  checks=checks+1
 end
end

-- smallTacticalFrame side mode: Actor.lua:1017-1036.
local side=slice(1017,1036)
number(side,B.small_side.sx,'small side sx')
number(side,B.small_side.dx,'small side dx')
number(side,B.small_side.sy,'small side sy')
number(side,B.small_side.dy,'small side dy')
number(side,B.small_side.enemy_sx,'small side enemy sx')
contains(side,'friend < 0','small side enemy test')
-- smallTacticalFrame bottom mode: Actor.lua:1104-1121.
local bottom=slice(1104,1121)
number(bottom,B.small_bottom.sx,'small bottom sx')
number(bottom,B.small_bottom.dx,'small bottom dx')
number(bottom,B.small_bottom.sy,'small bottom sy')
number(bottom,B.small_bottom.dy,'small bottom dy')
-- bigTacticalFrame: Actor.lua:1198-1229.
local big=slice(1198,1229)
number(big,B.big.side_dw,'big side dw')
number(big,B.big.bottom_dh,'big bottom dh')
contains(big,B.big.inset..',','big literal inset')
-- Band thresholds and (track, fill) RGBA for every band.
local bands=slice(1017,1121)
for _,band in ipairs(B.bands) do
 if band.min>-1e9 then
  local t=tostring(band.min)
  contains(bands,'lp > '..(t:sub(1,2)=='0.' and t:sub(2) or t),'band threshold')
 end
 local track=table.concat({band.track[1],band.track[2],band.track[3],B.track_alpha},', ')
 local fill=table.concat({band.fill[1],band.fill[2],band.fill[3],B.fill_alpha},', ')
 contains(bands,track,'track RGBA')
 contains(bands,fill,'fill RGBA')
end
contains(bands,'max(0, self.life) / self.max_life + 0.0001','native fraction')
assert(B.epsilon==0.0001,'native epsilon')
-- Mode choice: Actor.lua:1303-1308.
local choice=slice(1303,1308)
contains(choice,'view_faction','mode view_faction')
contains(choice,'always_target','mode always_target')

-- Native fraction, including the +0.0001 used for the >.75 band.
assert(math.abs(Style.nativeLifeFraction{life=50,max_life=100}-.5001)<1e-9)
assert(math.abs(Style.nativeLifeFraction{life=0,max_life=100}-.0001)<1e-9)
assert(Style.nativeLifeFraction{life=10,max_life=0}==0,'zero max_life must not divide by zero')
checks=checks+3

-- The helper must issue exactly the native drawQuad geometry and colour.
local draws
core={display={drawQuad=function(x,y,w,h,r,g,b,a) draws[#draws+1]={x,y,w,h,r,g,b,a} end}}
config={settings={tome={small_frame_side=false}}}
local function bar(mode,enemy)
 draws={}
 Style.nativeLifeBar({life=50,max_life=100},10,20,64,64,mode,enemy)
 assert(#draws==2,'one track and one fill quad per bar')
 assert(draws[1][5]==175 and draws[1][6]==175 and draws[1][7]==10 and draws[1][8]==128,'yellow track at alpha 128')
 assert(draws[2][5]==240 and draws[2][6]==252 and draws[2][7]==35 and draws[2][8]==255,'yellow fill at alpha 255')
 return draws
end
local d=bar('small-bottom')
assert(math.abs(d[1][1]-(10+64*.078125))<1e-9 and math.abs(d[1][3]-(64*.90625-64*.078125))<1e-9,'small bottom geometry')
local ds=bar('small-side')
assert(math.abs(ds[1][1]-(10+64*.015625))<1e-9,'friend side bar on the left')
local de=bar('small-side',true)
assert(math.abs(de[1][1]-(10+64*.9375))<1e-9,'enemy side bar on the right')
local db=bar('big-bottom')
assert(db[1][1]==13 and db[1][2]==20+64-64*.1 and db[1][3]==64-6,'big bottom uses the literal 3px inset')
local dbs=bar('big-side')
assert(dbs[1][1]==13 and dbs[1][2]==23 and dbs[1][3]==64*.1,'big side uses the literal 3px inset')
checks=checks+8
-- All four bands and their boundaries.
for _,case in ipairs{{.76,129,180,57},{.75,129,180,57},{.51,175,175,10},{.5,175,175,10},{.26,185,88,0},{.25,185,88,0},{0,167,55,39}} do
 draws={};Style.nativeLifeBar({life=case[1]*100,max_life=100},0,0,64,64,'small-bottom')
 assert(draws[1][5]==case[2] and draws[1][6]==case[3] and draws[1][7]==case[4],'band boundary '..case[1])
 checks=checks+1
end

-- Mode choice must match the native branch.
game={always_target=true};
assert(Style.nativeBarMode{view_faction=true}=='small-bottom')
config.settings.tome.small_frame_side=true
assert(Style.nativeBarMode{view_faction=true}=='small-side')
config.settings.tome.small_frame_side=false
game.always_target='old'
assert(Style.nativeBarMode{view_faction=true}=='big-bottom')
game.always_target=true
assert(Style.nativeBarMode{view_faction=false}=='big-bottom','native big bar needs no view_faction')
game.always_target=false
assert(Style.nativeBarMode{view_faction=true}==nil,'no always_target means no bar')
game.always_target=nil
assert(Style.nativeBarMode{view_faction=true}==nil)
checks=checks+6

print('native_lifebar: '..checks..' native geometry, colour, threshold and mode checks passed')
