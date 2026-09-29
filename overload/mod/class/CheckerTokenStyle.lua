-- Display geometry only. Never change the actor's size_category or combat data.
local M={}
-- Keep the native tactical meanings: green friend, blue neutral, red enemy.
M.colors={enemy={225,55,40},friend={72,210,105},neutral={65,125,245},player={30,195,245},shield={236,234,225},shield_ticks={255,253,245}}
-- Restore the 0.4.4 palette by user preference; keep the existing badge shapes.
-- These are native Actor:textRank colors, distinct from tactical frame hues.
M.rank_colors={rare={250,128,114},unique={244,164,96},boss={255,119,0},elite_boss={255,215,0},god={255,64,0}}
M.rank_color_order={'rare','unique','boss','elite_boss','god'}
M.relation_color_order={'friend','neutral','enemy'}
M.relation_color_defaults={friend=M.colors.friend,neutral=M.colors.neutral,enemy=M.colors.enemy}

local function validColor(c)
 if type(c)~='table' then return false end
 for i=1,3 do
  local v=c[i]
  if type(v)~='number' or v~=v or v<0 or v>255 or v~=math.floor(v) then return false end
 end
 return true
end

local function configuredColor(field,key,defaults)
 local settings=config and config.settings and config.settings.tome
 local palette=settings and settings[field]
 local color=type(palette)=='table' and palette[key]
 return validColor(color) and color or defaults[key]
end

function M.rankColor(badge)
 return configuredColor('checker_rank_colors',badge,M.rank_colors)
end

function M.relationColor(kind)
 if kind=='player' then return M.colors.player end
 return configuredColor('checker_relation_colors',kind,M.relation_color_defaults)
end

local function savePalette(palette,field,order)
 -- Serialize only known keys and validated RGB integers, never user text.
 local clean,lines={}, {'tome.'..field..' = {'}
 for _,key in ipairs(order) do
  local color=palette[key]
  if validColor(color) then
   clean[key]={color[1],color[2],color[3]}
   lines[#lines+1]=(' %s={%d,%d,%d},'):format(key,color[1],color[2],color[3])
  end
 end
 lines[#lines+1]='}\n'
 game:saveSettings('tome.'..field,table.concat(lines,'\n'))
 config.settings.tome[field]=clean
 if game.level and game.level.map then game.level.map:redisplay() end
end

local function setColor(key,color,field,order,defaults)
 if not defaults[key] or not validColor(color) then return false end
 local previous=config.settings.tome[field]
 local palette={}
 for _,name in ipairs(order) do
  palette[name]=type(previous)=='table' and previous[name] or nil
 end
 palette[key]=color
 savePalette(palette,field,order)
 return true
end

function M.setRankColor(badge,color)
 return setColor(badge,color,'checker_rank_colors',M.rank_color_order,M.rank_colors)
end

function M.setRelationColor(kind,color)
 return setColor(kind,color,'checker_relation_colors',M.relation_color_order,M.relation_color_defaults)
end

function M.resetRankColors()
 savePalette({},'checker_rank_colors',M.rank_color_order)
end

function M.resetColors()
 M.resetRankColors()
 savePalette({},'checker_relation_colors',M.relation_color_order)
end

-- The mechanical exporter centres each master's visible bounds and fits them
-- to this share of the square canvas. It must stay equal to target_occupancy
-- in tools/export_token.c: the faction ring is positioned from this constant,
-- so changing one side alone would detach the rim from the painted disc.
M.art_occupancy=.86
-- Painted disc diameter on screen, as a share of one map cell. The UI rim
-- outside the disc is fixed: .085 cell for the faction/health lane (see
-- M.geometry) plus .09 cell for the shield lane (see checkerTacticalFrame),
-- so .82+.175=.995 cell is the largest disc that still fits inside a cell.
M.token_diameter=.82

function M.scale(size,tile)
 -- One board piece, one diameter. size_category and tile size describe the
 -- creature and the viewport, not the playing piece: tiering them made
 -- neighbouring tokens differ by 7px at 64px cells and read as misaligned.
 -- The arguments are kept so existing call sites stay unchanged.
 return M.token_diameter/M.art_occupancy
end

function M.relation(actor,viewer,reaction)
 return actor==viewer and 'player' or reaction<0 and 'enemy' or reaction>0 and 'friend' or 'neutral'
end

function M.lifeFraction(actor)
 -- Match the native Minimalist/Board life scale, including actors able to
 -- survive below zero HP. This calculation never changes their life rules.
 local low,high=actor.die_at or 0,actor.max_life or 0
 if high<=low then return 0 end
 return math.max(0,math.min(1,((actor.life or 0)-low)/(high-low)))
end

function M.geometry(x,y,cell,scale)
 -- AI artwork occupies M.art_occupancy of its square. The wider UI rim sits
 -- outside it; keep this constant equal to the exporter's target occupancy.
 local diameter=cell*(M.art_occupancy*scale+.085)
 return {x=x+(cell-diameter)/2,y=y+(cell-diameter)/2,d=diameter,
  cx=x+cell/2,cy=y+cell/2,cell=cell}
end

-- The same quantified shield families as the native Minimalist HUD. Their
-- mitigation rules differ; these are remaining capacities, not effective HP.
-- Particle identity is taken from the active effect, never from its filename:
-- unrelated healing, storm and transformation visuals must remain visible.
function M.shieldData(actor)
 local current,maximum,particles=0,0,{}
 local function add(value,total,effect)
  current=current+math.max(0,value or 0)
  maximum=maximum+math.max(0,total or 0)
  if effect and effect.particle then particles[effect.particle]=true end
 end
 local function effect(name)
  local id=actor['EFF_'..name]
  return id and actor:hasEffect(id)
 end
 if actor:attr('damage_shield') then
  add(actor.damage_shield_absorb,actor.damage_shield_absorb_max,effect('DAMAGE_SHIELD') or effect('PSI_DAMAGE_SHIELD'))
 end
 if actor:attr('time_shield') then add(actor.time_shield_absorb,actor.time_shield_absorb_max,effect('TIME_SHIELD')) end
 if actor:attr('displacement_shield') then add(actor.displacement_shield,actor.displacement_shield_max,effect('DISPLACEMENT_SHIELD')) end
 if actor.T_DISRUPTION_SHIELD and actor:attr('disruption_shield_power') then
  add(actor.disruption_shield_power,actor:callTalent(actor.T_DISRUPTION_SHIELD,'getMaxAbsorb'),actor:isTalentActive(actor.T_DISRUPTION_SHIELD))
 end
 local hiemal=actor.T_HIEMAL_SHIELD and actor:isTalentActive(actor.T_HIEMAL_SHIELD)
 if hiemal then add(hiemal.shield,hiemal.original_shield,hiemal) end
 return current,maximum,particles
end

function M.rankBadge(rank)
 -- Critter (1), normal (2) and elite (3) intentionally share an unmarked base.
 -- Elite boss (5) is a separate native rank and retains its crown.
 if rank==3.2 then return 'rare' end
 if rank==3.5 then return 'unique' end
 if rank==4 then return 'boss' end
 if rank==5 then return 'elite_boss' end
 if rank==10 then return 'god' end
end

return M
