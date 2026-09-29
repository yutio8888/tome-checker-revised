-- Offline fixture only. Production player token validation across any
-- --birth character: identity mapping, toggle, an external-display override
-- (native shapeshift), and equipment-driven paper-doll rebuild. Every check
-- reads the actual running actor; nothing here is staged/frozen combat.
local M={rows={}}
local function guard()
 assert(require('mod.class.CheckerFixture').enabled() and not profile.auth)
 assert(game.checker_ready and game.player==game.checker_hero)
end
local function say(text)
 M.rows[#M.rows+1]=text;print('[PlayerTokens]',text)
 local f=assert(fs.open('/player-tokens-validation.txt','w'))
 f:write(table.concat(M.rows,'\n')..'\n');f:close()
end
local function state()
 local p=game.player
 return table.concat({game.turn,p.x,p.y,p.life,p.energy.value},'/')
end
M.state=state

-- Birth/zone-entry text (Chat/QuestPopup/etc.) would otherwise sit on top of
-- the screenshot. Best-effort only: dismissing an unrecognized dialog cannot
-- hide a real defect, since none of the assertions below depend on dialogs.
function M.dismissPrompts()
 guard()
 local dismissed={}
 for i=#game.dialogs,1,-1 do
  local d=game.dialogs[i]
  dismissed[#dismissed+1]=d.__CLASSNAME
  game:unregisterDialog(d)
 end
 game.bignews.list=nil
 if game.flyers and game.flyers.empty then game.flyers:empty() end
 return dismissed
end

-- Freeze the display for a stable screenshot without staging monsters; the
-- player keeps acting normally otherwise (this is real character creation).
function M.refresh()
 guard()
 M.dismissPrompts()
 local p,m=game.player,game.level.map
 m.clean_fov=true;p:playerFOV()
 m.smooth_scroll=0;m:centerViewAround(p.x,p.y)
 m:updateMap(p.x,p.y);m:redisplay();m.changed=true
 game.paused=true;core.display.forceRedraw()
end

function M.snapshot()
 guard()
 local p=game.player
 local t=p._checker_token
 local addmos=0
 if p.add_mos then for _ in pairs(p.add_mos) do addmos=addmos+1 end end
 return {id=t and t.id or nil, image=t and t.display and t.display.image or nil,
  scale=t and t.scale or nil, add_mos=addmos, replace_display=p.replace_display~=nil,
  subrace=p.descriptor.subrace, sex=p.descriptor.sex, class=p.descriptor.subclass,
  zone=game.zone and game.zone.short_name}
end

function M.report(label)
 local s=M.snapshot()
 say(('%s id=%s image=%s scale=%s add_mos=%d replace_display=%s subrace=%s sex=%s class=%s zone=%s state=%s')
  :format(label,tostring(s.id),tostring(s.image),tostring(s.scale),s.add_mos,tostring(s.replace_display),
   s.subrace,s.sex,s.class,tostring(s.zone),state()))
 return s
end

-- Assert the identity contract the production runtime promises: either a
-- verified player family token, matching CheckerPlayerTokens.image(), or a
-- fully native fallback (nil id, native replace_display state).
function M.assertIdentity(expected_family)
 guard()
 local s=M.snapshot()
 if expected_family then
  assert(s.id=='player:'..expected_family, 'expected player:'..expected_family..' got '..tostring(s.id))
  local PlayerTokens=require('mod.class.CheckerPlayerTokens')
  assert(s.image==PlayerTokens.image(s.id), 'token image path mismatch: '..tostring(s.image))
  assert(s.scale~=nil, 'owned token must carry the shared board-piece scale')
 else
  assert(s.id==nil, 'expected native (nil) player token, got '..tostring(s.id))
 end
 return s
end

function M.setPlayerTokens(enabled)
 guard();game:checkerSetPlayerTokensEnabled(enabled);M.refresh()
end

function M.setZoom(px)
 guard()
 config.settings.tome.gfx.size=px..'x'..px
 game:setupDisplayMode(false)
 M.refresh()
end

-- A native transformation that installs its own replace_display outside our
-- code (Wilder-independent: any class can receive it via setEffect). While
-- active the token must yield; once it clears, the token must come back.
function M.applyShapeshift()
 guard();game.player:setEffect(game.player.EFF_TREE_OF_LIFE,4,{});M.refresh()
end
function M.removeShapeshift()
 guard();game.player:removeEffect(game.player.EFF_TREE_OF_LIFE);M.refresh()
end

-- Take off the mainhand weapon (present on every starting build with a melee
-- weapon) so the native doll, once revealed, must differ from birth gear.
function M.changeEquipment()
 guard()
 local p=game.player
 local slot=p.INVEN_MAINHAND
 assert(slot,'no mainhand inventory slot on this build')
 local inven=p:getInven(slot)
 assert(inven and #inven>0,'no mainhand item to remove for the equipment check')
 local item=inven[1]
 M.removed_item={name=item.name,uid=item.uid}
 p:takeoffObject(slot,1)
 M.refresh()
 return M.removed_item
end

M.guard=guard
return M
