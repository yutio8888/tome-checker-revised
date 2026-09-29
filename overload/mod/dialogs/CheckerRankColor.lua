require 'engine.class'
local Dialog=require 'engine.ui.Dialog'
local NumberSlider=require 'engine.ui.NumberSlider'
local Textzone=require 'engine.ui.Textzone'
local Empty=require 'engine.ui.Empty'
local Button=require 'engine.ui.Button'
local Style=require 'mod.class.CheckerTokenStyle'
module(...,package.seeall,class.inherit(Dialog))

function _M:init(key,title,on_apply,kind)
 self.kind=kind or 'rank'
 self.defaults=self.kind=='relation' and Style.relation_color_defaults or Style.rank_colors
 assert(self.defaults[key])
 self.badge,self.color_key,self.on_apply=self.kind=='rank' and key or nil,key,on_apply
 local c=self.kind=='relation' and Style.relationColor(key) or Style.rankColor(key)
 self.draft={c[1],c[2],c[3]}
 Dialog.init(self,title..' - '.._t'Color',460,320)
 local info=Textzone.new{width=440,auto_height=true,text=_t'Adjust red, green and blue. Apply saves this color; Cancel keeps your current color.'}
 self.readout=Textzone.new{width=440,height=24,text=''}
 local function load(name)
  local image=assert(core.display.loadImage('/data-checker-revised/gfx/tokens/'..name..'.png'))
  image:alpha(true)
  local iw,ih=image:getSize()
  local tex,tw,th=image:glTexture()
  return function(x,y,w,h,color)
   tex:toScreenFull(x,y,w,h,tw*w/iw,th*h/ih,color[1]/255,color[2]/255,color[3]/255,1)
  end
 end
 local mark,back,band
 if self.kind=='relation' then
  back,band,mark=load('_relation-back'),load('_health-band'),load('_relation-edge-'..key)
 else mark=load('_badge-'..key) end
 local preview=Empty.new{width=440,height=70}
 preview.display=function(_,x,y)
  local color=self.draft
  core.display.drawQuad(x,y,440,70,20,24,23,255)
  core.display.drawQuad(x+12,y+12,110,46,color[1],color[2],color[3],255)
  if back then
   for _,p in ipairs{{166,21,28},{254,9,52}} do
    back(x+p[1],y+p[2],p[3],p[3],{15,20,20})
    band(x+p[1],y+p[2],p[3],p[3],color)
    mark(x+p[1],y+p[2],p[3],p[3],color)
   end
  else
   mark(x+166,y+24,28,22,color)
   mark(x+254,y+10,64,50,color)
  end
 end
 self.sliders={}
 local ui={{left=0,top=0,ui=info},{left=0,top=info.h+8,ui=preview},
  {left=0,top=info.h+86,ui=self.readout}}
 local top=info.h+116
 for i,label in ipairs{_t'R: ',_t'G: ',_t'B: '} do
  local channel=i
  local slider=NumberSlider.new{title=label,value=c[i],min=0,max=255,step=1,w=440,
   on_change=function(value) self.draft[channel]=value;self:updatePreview() end}
  self.sliders[i]=slider
  ui[#ui+1]={left=0,top=top,ui=slider}
  top=top+slider.h+12
 end
 self.apply_button=Button.new{text=_t'Apply',fct=function() self:applyColor() end}
 self.default_button=Button.new{text=_t'Default',fct=function() self:setDraft(self.defaults[self.color_key]) end}
 self.cancel_button=Button.new{text=_t'Cancel',fct=function() self:cancelColor() end}
 ui[#ui+1]={left=0,top=top+8,ui=self.apply_button}
 ui[#ui+1]={hcenter=0,top=top+8,ui=self.default_button}
 ui[#ui+1]={right=0,top=top+8,ui=self.cancel_button}
 self:loadUI(ui)
 self:setupUI(true,true)
 self:setFocus(self.sliders[1])
 self.key:addBinds{EXIT=function() self:cancelColor() end}
 self:updatePreview()
end

function _M:updatePreview()
 local c=self.draft
 self.readout.text=('RGB %d, %d, %d     Hex %02X%02X%02X'):tformat(c[1],c[2],c[3],c[1],c[2],c[3])
 self.readout:generate()
end

function _M:setDraft(color)
 for i,slider in ipairs(self.sliders) do
  slider.nbox:updateText(color[i]-slider.nbox.number)
  slider:onChange()
 end
end

function _M:applyColor()
 -- Read typed numbers as well as dragged slider values before saving.
 for _,slider in ipairs(self.sliders) do slider:onChange() end
 local setter=self.kind=='relation' and Style.setRelationColor or Style.setRankColor
 if not setter(self.color_key,self.draft) then return end
 game:unregisterDialog(self)
 if self.on_apply then self.on_apply() end
end

function _M:cancelColor()
 game:unregisterDialog(self)
end
