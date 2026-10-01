-- Exercise the native replacement-display dispatch (no SDL/game launch).
-- Map-object construction is a recorder; this verifies which Entity supplies
-- shader fields, not a live GL draw. Game installation is tested in runtime_modes.
local script=debug.getinfo(1,'S').source:sub(2)
local root=(script:match('^(.*[/\\])') or './')..'../'
local f=assert(io.open(root..'../../engines/default/engine/Entity.lua'))
local source=f:read('*a');f:close()
local body=assert(source:match('(function _M:getMapObjects%(tiles, mos, z%).-\nend)'))
local native={}
local chunk=assert(loadstring(body))
setfenv(chunk,setmetatable({_M=native},{__index=_G}));chunk()
local checks=0
local function equal(a,b,label) checks=checks+1;assert(a==b,label) end
local function entity(shader)
 local e={shader=shader,calls=0,callbacks=0}
 function e:makeMapObject(tiles,n)
  self.calls=self.calls+1
  if n>1 then return nil end
  return {source=self,shader=self.shader,shader_args=self.shader_args},0,nil
 end
 function e:defineDisplayCallback() self.callbacks=self.callbacks+1 end
 return e
end
for _,mode in ipairs({'quad_hue','shadow_simulacrum'}) do
 local actor=entity(mode);local display=entity(nil);actor.replace_display=display
 native.getMapObjects(actor,{}, {},10)
 equal(display.calls,2,'native builds replacement body only')
 equal(actor.calls,0,'native actor body is not built underneath replacement')
 equal(actor._mo.source,display,'actor map-object pointer belongs to replacement')
 equal(actor._mo.shader,nil,'native actor shader not applied to replacement')
 equal(actor._mo.shader_args,nil,'native actor args not applied to replacement')
 equal(actor.shader,mode,'dispatch preserves native actor shader')
 equal(actor.callbacks,1,'actor callback still installed')
 actor.replace_display=nil
 native.getMapObjects(actor,{}, {},10)
 equal(actor.calls,2,'fallback rebuilds native actor body')
 equal(actor._mo.source,actor,'fallback uses native actor object')
 equal(actor._mo.shader,mode,'fallback retains native actor shader')
end
print(('ag_shader_render: %d checks passed; native replacement dispatch, shader isolation and fallback (no GL draw)'):format(checks))
