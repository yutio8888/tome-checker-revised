class:bindHook('Game:changeLevel',function(self)
 self:checkerApplySettings()
end)
class:bindHook('ToME:runDone',function(self)
 if game and game.checkerApplySettings then game:checkerApplySettings() end
end)

class:bindHook('GameOptions:tabs',function(self,data)
 data.tab(_t'Token colors',function(dialog)
  local Options=require 'mod.class.CheckerOptions'
  local Style=require 'mod.class.CheckerTokenStyle'
  local Textzone=require 'engine.ui.Textzone'
  local ColorDialog=require 'mod.dialogs.CheckerRankColor'
  local names={rare=_t'Rare',unique=_t'Unique',boss=_t'Boss',elite_boss=_t'Elite boss',god=_t'God'}
  local list={}
  list[#list+1]={name=_t'Creature tokens',checker_tokens_enabled=true,
   zone=Textzone.new{width=dialog.c_desc.w,height=dialog.c_desc.h,text=_t'Use tokens for verified creature identities. Unknown creatures and unsupported appearances keep their native art. This setting is independent of terrain and HUD style, takes effect immediately, and is saved for future games.'},
   status=function() return Options.tokensEnabled() and _t'Enabled' or _t'Disabled' end,
   fct=function(item)
    Options.setTokensEnabled(not Options.tokensEnabled(),game)
    dialog.c_list:drawItem(item)
   end}
  list[#list+1]={name=_t'Player token',checker_player_tokens_enabled=true,
   zone=Textzone.new{width=dialog.c_desc.w,height=dialog.c_desc.h,text=_t'Show your main character as a neutral token chosen by race body and sex. It does not follow equipment or class. Shapeshifts, custom tiles and uncovered races keep their native appearance. Creature tokens must also be enabled. This setting takes effect immediately and is saved for future games.'},
   status=function() return Options.playerTokensEnabled() and _t'Enabled' or _t'Disabled' end,
   fct=function(item)
    Options.setPlayerTokensEnabled(not Options.playerTokensEnabled(),game)
    dialog.c_list:drawItem(item)
   end}
  local mode_names={vanilla=_t'Native',blockout=_t'Blockout',refined=_t'Refined'}
  local next_mode={vanilla='blockout',blockout='refined',refined='vanilla'}
  list[#list+1]={name=_t'Board terrain',checker_terrain_mode=true,
   zone=Textzone.new{width=dialog.c_desc.w,height=dialog.c_desc.h,text=_t'Cycle Native, Blockout and Refined terrain. Refined supports Trollmire, Old Forest, Slazish Fens, both Rhaloren Camp layouts, Dreadfell, both Norgos\' Lair layouts, both Daikara layouts, The Maze, Heart of the Gloom, Sandworm Lair, Ritches Tunnels, The Deep Bellow, Last Hope Graveyard, Scintillating Caves, Unremarkable Cave, Unknown tunnels, Tempest Peak, Ruined halfling complex, Lost Dwarven Kingdom of Reknor, Escape from Reknor, Lake of Nur surface, underwater and dry stone grids, Ruined Dungeon, Blighted Ruins, Dark crypt, Golem Graveyard, Ardhungol, Mark of the Spellblaze, Unhallowed Morass, Abashed Expanse, Temporal Rift L1-L4, Murgol Lair, Southern Beach, Tranquil Meadow, Noxious Caldera, Old Conclave Vault, Ruins of Telmur, Elven Ruins, Vor Armoury, Briagh\'s Lair, Caverns to the hidden valley, Flooded Cave, Temple of Creation, Charred Scar, the Fearscape, Sher\'Tul Fortress floors and walls, Rak\'shor Pride floors, walls, doors and stairs, and selected stone floors, walls, doors and stairs in both Kor\'Pul layouts, and selected town grids in Derth, Lumberjack Town, Last Hope, Elvala, Zigur, Angolwen, Iron Council, Shatur, Point Zero, Gates of Morning and Irkkk, and selected grids in Shadow Crypt, Tannen\'s Tower, Ithilthum, Valley of the Moon, Ring of Blood, Erúan, Gorbat Pride, High Peak, Grushnak Pride, Slime Tunnels, Sludgenest, Vor Pride, Tutorial, Dreams, and the Temporal Reprieve and Dreamscape planes, including town roads and farmland, levers, lever doors, candles, portals and lava floors. Rhaloren Camp combines forest and stone art on the same level. Blockout supports forest, Norgos\' Lair snow-rock, Daikara and Tempest Peak rock and mountain wall, Daikara lava, Heart of the Gloom ground, creep, walls and exits, Sandworm Lair, Ritches Tunnels and Briagh\'s Lair sand, walls and exits, The Deep Bellow floors, creep, walls and ladders, and Scintillating Caves floors, walls and ladders, and Unremarkable Cave floors, walls and world exit, plus Ardhungol and hidden valley cave floors, walls and ladders, and Mark of the Spellblaze burnt ground, trees, lava and exits, plus void platforms and rift edges, and Lake of Nur, Murgol Lair, Flooded Cave and Temple of Creation underwater floors, walls, doors and stairs, plus Southern Beach, Tranquil Meadow and Noxious Caldera ground, trees, walls, water, props and exits, plus Charred Scar and Fearscape lava floors, lava and rock walls, and Sher\'Tul Fortress floors and walls, and Rak\'shor Pride floors, walls, doors and stairs; stone cells, including The Maze, keep native art. Unsupported grids keep their native art. Creature tokens use their own setting. Changes take effect immediately and are saved.'},
   status=function() return mode_names[Options.terrainMode()] end,
   fct=function(item)
    Options.setTerrainMode(next_mode[Options.terrainMode()],game)
    dialog.c_list:drawItem(item)
   end}
  list[#list+1]={name=_t'Event aura grid',checker_aura_style=true,
   zone=Textzone.new{width=dialog.c_desc.w,height=dialog.c_desc.h,text=_t'Show a subtle or moderate colored border on supported event aura grids when board terrain is active. Native terrain and unsupported grids keep their original art. Changes take effect immediately and are saved.'},
   status=function() return Options.auraStyle()=='subtle' and _t'Subtle' or _t'Moderate' end,
   fct=function(item)
    Options.setAuraStyle(Options.auraStyle()=='subtle' and 'moderate' or 'subtle',game)
    dialog.c_list:drawItem(item)
   end}
  list[#list+1]={name=_t'Token facing',checker_token_facing=true,
   zone=Textzone.new{width=dialog.c_desc.w,height=dialog.c_desc.h,text=_t'Fixed keeps token artwork and its painted light direction unchanged. Follow movement uses native horizontal flipping when moving or attacking. Only covered creature tokens are affected; native appearances keep their own facing. This setting takes effect immediately and is saved. Smooth movement and twitch remain controlled by the native game options.'},
   status=function() return Options.tokenFacing()=='fixed' and _t'Fixed' or _t'Follow movement' end,
   fct=function(item)
    Options.setTokenFacing(Options.tokenFacing()=='fixed' and 'native' or 'fixed',game)
    dialog.c_list:drawItem(item)
   end}
  for _,key in ipairs(Style.rank_color_order) do
   local badge=key
   list[#list+1]={name=names[badge],checker_badge=badge,
    zone=Textzone.new{width=dialog.c_desc.w,height=dialog.c_desc.h,text=_t'Change this rank badge color. Adjust the RGB sliders and preview the badge, then choose Apply. Colors are saved for future games. Normal and elite creatures remain unmarked.'},
    status=function()
     local c=Style.rankColor(badge)
     return ('RGB %d, %d, %d'):tformat(c[1],c[2],c[3])
    end,
    fct=function(item)
     game:registerDialog(ColorDialog.new(badge,names[badge],function() dialog.c_list:drawItem(item) end))
    end}
  end
  local relations={friend=_t'Friendly ring',neutral=_t'Neutral ring',enemy=_t'Hostile ring'}
  for _,key in ipairs(Style.relation_color_order) do
   local relation=key
   list[#list+1]={name=relations[relation],checker_relation=relation,
    zone=Textzone.new{width=dialog.c_desc.w,height=dialog.c_desc.h,text=_t'Change the faction ring color. The player keeps a cyan ring with a white inner line. Friendly units have a solid ring, neutral units a dashed ring, and hostile units four notches.'},
    status=function()
     local c=Style.relationColor(relation)
     return ('RGB %d, %d, %d'):tformat(c[1],c[2],c[3])
    end,
    fct=function(item)
     game:registerDialog(ColorDialog.new(relation,relations[relation],function() dialog.c_list:drawItem(item) end,'relation'))
    end}
  end
  list[#list+1]={name=_t'Restore default colors',checker_reset=true,
   zone=Textzone.new{width=dialog.c_desc.w,height=dialog.c_desc.h,text=_t'Restore warm rank badges and the default green friendly, blue neutral and red hostile rings. The player keeps its cyan ring and white inner line.'},
   status=function() return _t'Reset all' end,
   fct=function()
    Style.resetColors()
    for _,item in ipairs(list) do dialog.c_list:drawItem(item) end
   end}
  dialog.list=list
 end)
end)
