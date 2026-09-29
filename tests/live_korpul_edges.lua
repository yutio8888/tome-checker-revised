-- Read-only renderer diagnosis, only in the explicit offline test fixture.
local T=require 'mod.class.CheckerTerrain'
local M={}
function M.run()
 assert(config.settings.cheat and config.settings.disable_all_connectivity and profile and not profile.auth)
 assert(__module_extra_info.checker_demo and game.checker_staged and T.variant(game.zone))
 local m,p=game.level.map,game.player
 local records=m._checker_korpul or {}
 local cells={}
 for key,r in pairs(records) do
  local x,y=key%m.w,math.floor(key/m.w)
  if r.painted and math.abs(x-p.x)<=12 and math.abs(y-p.y)<=12 then
   for dx=-1,1 do for dy=-1,1 do local a,b=x+dx,y+dy
    if m:isBound(a,b) then cells[a+b*m.w]=true end
   end end
  end
 end
 local path='/korpul-edges-'..T.variant(game.zone):lower()..'.tsv'
 local f=assert(fs.open(path,'w'))
 f:write('x\ty\tseen\tfov\tremember\thasseen\tcategory\tnative_id\tclassify\trecorded\tpainted\tfile\timage\tadd_displays\n')
 local counts={}
 for key in pairs(cells) do
  local x,y=key%m.w,math.floor(key/m.w)
  local g,r=m(x,y,1),records[key]
  local seen,fov,remember=m.seens(x,y),m.infovs(x,y),m.remembers(x,y)
  local category=T.visible(m,x,y) and 'visible' or remember and 'remembered' or 'unknown'
  category=category..(r and r.painted and '-painted' or '-native')
  counts[category]=(counts[category] or 0)+1
  local overlays={}
  for _,e in ipairs(g.add_displays or {}) do overlays[#overlays+1]=tostring(e.image)..'@'..tostring(e.display_x or 0)..','..tostring(e.display_y or 0)..'/'..tostring(e.display_h or 1) end
  local values={x,y,tostring(seen),tostring(fov),tostring(remember),tostring(m.has_seens and m.has_seens(x,y)),category,g.define_as or '',T.classify(g) or '',r and r.kind or '',tostring(r and r.painted),r and r.file or '',g.image or '',table.concat(overlays,';')}
  for i,v in ipairs(values) do values[i]=tostring(v):gsub('[\r\n\t]',' ') end
  f:write(table.concat(values,'\t')..'\n')
 end
 f:close();print('[KorPulEdges]',path)
 for category,count in pairs(counts) do print('[KorPulEdges]',category,count) end
 return path,counts
end
return M
