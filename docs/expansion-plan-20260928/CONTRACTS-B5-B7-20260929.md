# 批次 5–7 出图前精确合同表（2026-09-29）

调查范围：`docs/expansion-plan-20260928/MONSTER-GAP-20260929.md` 的批次 5（沙虫本体+水晶/植物）、批次 6（独立地城专属首领）、批次 7（次要首领与常驻随从），以及第四节「需要特殊外观合同或建议保持原生的项目」中点名的条目。目标区域限定为当前已接入棋盘地形的区域（见 `hooks/load.lua` 中 `checker_terrain_mode` 的 Refined 说明文案与 `PROGRESS.md`），本轮涉及的 trollmire、old-forest、scintillating-caves、sandworm-lair、slazish-fen、tempest-peak、reknor、reknor-escape、ardhungol、blighted-ruins、crypt-kryl-feijan、golem-graveyard、ritch-tunnels、deep-bellow、last-hope-graveyard、daikara、dreadfell、unremarkable-cave、rhaloren-camp、maze、norgos-lair 均在该清单内；Orc Breeding Pit（不可达）与 Illusory Castle 本身未出现在批次 5–7 范围内，不需要排除。

## 0. 方法论：一个贯穿全篇的关键订正

`modules/tome/class/NPC.lua:33`（`WorldNPC.lua:36` 同理）：

```
if not self.image and self.name ~= "unknown actor" then
  self.image = "npc/"..type.."_"..subtype:lower():gsub(...).."_"..name:lower():gsub(...)..".png"
end
```

**任何 npc 实体只要源码里没有显式 `image=`，且没有 `resolvers.nice_tile` 提前把 `self.image` 设成别的值，运行期都会得到一个确定的默认文件名** `npc/<type>_<subtype>_<name（转小写、非字母数字转下划线）>.png`，与是否存在真实贴图文件无关（找不到文件时原生渲染才退化为 ASCII 字形）。这个函数与角色实例化（`Actor.init`）同阶段执行，晚于 `engine/Entity.lua:745` 的 `resolve()`（`resolvers.nice_tile` 在这一步执行，此时看到的 `self.image` 是源码字面量或 nil，不是 NPC.lua 的兜底值）。

调查底稿（`MONSTER-GAP-20260929.md` 4.2/4.3）多处把"源码里没有 `image=`"直接等同于"没有图片、走原生字形，棋子系统无法介入"。这个假设**不成立**：本轮对每一条"无 image"声明都用该公式反推出确定文件名，再核对 `game/modules/tome/data/gfx/shockbolt/npc/` 目录，结果如下（含目视抽查，见各节）：

| 身份 | 文档原判定 | 反推文件名 | 磁盘状态 | 目视确认 |
| --- | --- | --- | --- | --- |
| Harno, Herald of Last Hope（reknor:119） | 保持原生（无 image，@ 字形） | `npc/humanoid_human_harno__herald_of_last_hope.png` | 存在 | 是，真实肖像（兜帽斗篷男性），非占位图 |
| Lithfengel（reknor:156） | 保持原生（无 image，U 字形） | `npc/demon_major_lithfengel.png` | 存在 | 是，独立恶魔肖像 |
| Norgan（reknor-escape:91） | 保持原生（无 image，@ 字形） | `npc/humanoid_dwarf_norgan.png` | 存在 | 是，矮人肖像 |
| Rhaloren Inquisitor（rhaloren-camp:30，批次7表内） | 需夹具核实渲染路径 | `npc/humanoid_shalore_rhaloren_inquisitor.png` | 存在 | 是，持双手剑的精灵战士肖像 |
| Borfast the Broken（dreadfell:210） | 分区清单："无image走原生" | `npc/undead_ghoul_borfast_the_broken.png` | 存在 | 未抽查，文件名精确匹配公式 |
| Aletta Soultorn（dreadfell:282） | 分区清单："无image走原生" | `npc/undead_ghost_aletta_soultorn.png` | 存在 | 是，幽灵女性肖像 |
| Filio Flightfond（dreadfell:358） | 分区清单："无image走原生" | `npc/undead_skeleton_filio_flightfond.png` | 存在 | 未抽查，文件名精确匹配公式 |
| Necromancer（blighted-ruins:29） | 外观待核实 | `npc/humanoid_human_necromancer.png` | 存在 | 未抽查 |
| fleshy/boney/sanguine experiment（blighted-ruins:127/158/190） | 未特别标注 | `npc/undead_horror_{fleshy,boney,sanguine}_experiment.png` | 均存在 | 未抽查 |

以上 9 条全部应改判为 **READY（单图，无需 unique/native_tall 标记）**，不需要夹具核实，也不需要工程改动。只有 **Melinda**（crypt-kryl-feijan，见 4.2）是任务态运行时改图的真实特例，维持"保持原生"结论不变。

## 1. 批次 5 — 沙虫本体 + 水晶 / 植物

| 身份 | define_as | 区域/关卡 | 类型 | unique | 出现方式 | 外观来源 | 原生贴图 | 判定 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sandworm | 无 | maze、sandworm-lair 随机池 | vermin/sandworm | 否 | `general/npcs/sandworm.lua:51` `rarity=1` 随机 | 无 `image=`，NPC.lua 公式 | `npc/vermin_sandworm_sandworm.png` 存在 | **READY**（单图） |
| sandworm destroyer | 无 | dreadfell、sandworm-lair 随机池 | vermin/sandworm | 否 | `sandworm.lua:57` `rarity=3` 随机 | 同上，公式 | `npc/vermin_sandworm_sandworm_destroyer.png` 存在 | **READY**（单图） |
| sandworm burrower | SANDWORM_TUNNELER | sandworm-lair（Queen 出现前的引路怪，脚本放置，无 `rarity`） | vermin/sandworm | 否 | `zones/sandworm-lair/npcs.lua:32` | 无 `image=`，公式 | `npc/vermin_sandworm_sandworm_burrower.png` 存在 | **READY**（单图，注：`invulnerable=1`/`never_anger`，是不可攻杀的引路演出体，非常规战斗单位） |
| white crystal | 无 | scintillating-caves 随机池 | immovable/crystal | 否 | `general/npcs/crystal.lua:108` `rarity=1`，继承 `BASE_NPC_CRYSTAL` | 未覆盖 `image`，沿用基类 `image="npc/crystal_npc.png"`（`crystal.lua:24`） | 存在 | **READY-有备注**：与未来若收录的 `shimmering crystal`（`crystal.lua:167`，同样未覆盖 image）原生贴图完全相同，二者互为易混淆同源体，需保证新出的棋子图彼此有别（原生贴图本身不构成阻碍） |
| red crystal | 无 | scintillating-caves 随机池 | immovable/crystal | 否 | `crystal.lua:96` `rarity=1` | 显式 `image="npc/crystal_red.png"` | 存在 | **READY**（单图） |
| crimson crystal | 无 | scintillating-caves 随机池 | immovable/crystal | 否 | `crystal.lua:130` `rarity=3` | 显式 `image="npc/crystal_darkred.png"` | 存在 | **READY**（单图） |
| poison ivy | 无 | trollmire、unremarkable-cave 随机池 | immovable/plants | 否 | `general/npcs/plant.lua:75` `rarity=2` | 无 `image=`，公式 | `npc/immovable_plants_poison_ivy.png` 存在 | **READY**（单图） |
| honey tree | 无 | old-forest 随机池 | immovable/plants | 否 | `plant.lua:90` `rarity=3`，`combat=false`（纯召唤体，见 desc） | 无 `image=`，公式 | `npc/immovable_plants_honey_tree.png` 存在 | **READY**（单图） |
| treant | 无 | old-forest 随机池（普查未直接命中，池内存在） | immovable/plants | 否 | `plant.lua:57-63` `rarity=2` | **显式** `resolvers.nice_tile{image="invis.png", add_mos={{image="npc/immovable_plants_treant.png", display_h=2, display_y=-1}}}` | 存在 | **NEEDS-CONTRACT-EXTENSION**（见第 3 节，原调查文档遗漏此条，应与 dremling/shivgoroth 归为同一类缺口，不是单纯出图） |

调查文档把 `treant` 直接放进"只缺美术"的批次 5 列表，但它的显示结构与第四节点名的 6 个"合同缺口"身份完全一致（`invis.png`+单张 `add_mos` 高体、`unique` 不为真）。`tests/token_mapping.lua:249` 已经把 `treant` 列在"未收录同族体"排除测试里，证实当前代码确实拒绝它。**这是本次调查最重要的一处订正**：批次 5 实际是 8 个 READY + 1 个 NEEDS-CONTRACT-EXTENSION，不是文档暗示的 9 个纯美术缺口。

`elemental crystal`（trollmire L3，借用 `trap/trap_beam.png`）未在本轮复核范围内，维持原文档"需先核实是否属于常规怪物渲染路径"的搁置结论。

## 2. 批次 6 — 独立地城专属首领（12 区域门面，逐条复核）

全部为脚本放置的守关/终层唯一首领（源码块内**无 `rarity` 字段**，不进入随机池），全部标准 `invis.png`+单张 `add_mos{display_h=2, display_y=-1}`、`unique=true`，`CheckerTokens.nativeTallImage()`（`overload/mod/class/CheckerTokens.lua:171-184`）已验证支持该形状。逐条核对 file:line 与磁盘贴图后，**12 条全部 READY**，无一例外：

| 首领 | define_as | 区域 | type/subtype | 来源 file:line | 原生贴图 |
| --- | --- | --- | --- | --- | --- |
| Lady Zoisla the Tidebringer | ZOISLA | slazish-fen | humanoid/naga | `zones/slazish-fen/npcs.lua:116-119` | `npc/humanoid_naga_lady_zoisla_the_tidebringer.png` 存在 |
| Urkis, the High Tempest | URKIS | tempest-peak | humanoid/human | `zones/tempest-peak/npcs.lua:29-34` | `npc/humanoid_human_urkis__the_high_tempest.png` 存在（注意名称含逗号，转义后出现双下划线） |
| Golbug the Destroyer | GOLBUG | reknor | humanoid/orc | `zones/reknor/npcs.lua:28-34` | `npc/humanoid_orc_golbug_the_destroyer.png` 存在 |
| Brotoq the Reaver | BROTOQ | reknor-escape | humanoid/orc | `zones/reknor-escape/npcs.lua:38-43` | `npc/humanoid_orc_brotoq_the_reaver.png` 存在 |
| Ungolë | UNGOLE | ardhungol | spiderkin/spider（继承 `BASE_NPC_SPIDER`） | `zones/ardhungol/npcs.lua:26-29` | `npc/spiderkin_spider_ungole.png` 存在 |
| Half-Finished Bone Giant | HALF_BONE_GIANT | blighted-ruins | undead/giant（继承 `BASE_NPC_BONE_GIANT`，注：**不是**"bone_giant"子类型，`general/npcs/bone-giant.lua:23-24` 为 `type="undead", subtype="giant"`） | `zones/blighted-ruins/npcs.lua:73-78` | `npc/undead_giant_half_finished_bone_giant.png` 存在 |
| Kryl-Feijan | KRYL_FEIJAN | crypt-kryl-feijan | demon/major（继承 `BASE_NPC_MAJOR_DEMON`） | `zones/crypt-kryl-feijan/npcs.lua:28-31` | `npc/demon_major_kryl_feijan.png` 存在 |
| Atamathon the Giant Golem | ATAMATHON | golem-graveyard | construct/golem（继承 `BASE_NPC_CONSTRUCT`） | `zones/golem-graveyard/npcs.lua:24-29` | tall 体 `npc/construct_golem_athamathon_the_giant_golem.png` 存在；**另有独立单图** `image="npc/atamathon.png"`（也存在，见备注） |
| Ritch Great Hive Mother | HIVE_MOTHER | ritch-tunnels | insect/ritch（继承 `BASE_NPC_RITCH_REL`） | `zones/ritch-tunnels/npcs.lua:98-100` | **显式单图** `image="npc/insect_ritch_ritch_hive_mother.png"`，非 composite，存在 |
| The Mouth | THE_MOUTH | deep-bellow | horror/corrupted（继承 `BASE_NPC_CORRUPTED_HORROR`） | `zones/deep-bellow/npcs.lua:27-33` | `npc/horror_corrupted_the_mouth.png` 存在 |
| The Abomination | ABOMINATION | deep-bellow | horror/corrupted | `zones/deep-bellow/npcs.lua:133-138` | `npc/horror_corrupted_the_abomination.png` 存在 |
| Celia | CELIA | last-hope-graveyard | humanoid/human | `zones/last-hope-graveyard/npcs.lua:28-34` | 单图与 tall 体同一文件 `npc/humanoid_human_celia.png`，均存在 |

**Atamathon 备注（唯一需要留意的例外）**：`golem-graveyard/npcs.lua:27` 在 `resolvers.nice_tile` 之外**另外**显式设置了 `image="npc/atamathon.png"`——这是 nicer_tiles 关闭时的单格图标，与 tall 体内层图片 `construct_golem_athamathon_the_giant_golem.png` 是**两个不同文件**（本轮复核的其余身份里，单图兜底与 tall 体内层图片要么相同要么不存在第二个显式 image，只有 Atamathon 这样双轨）。`CheckerTokens.appearance()` 的 `"single"` 分支要求 `actor.image == entry.image`，若 `entry.image` 按惯例填 tall 体图片，则 nicer_tiles 关闭时 `actor.image` 是 `"npc/atamathon.png"`，两者不等，also 不是 `"invis.png"`，因此**关闭 nicer_tiles 时 Atamathon 不会被识别为棋子，会退回其原生 `npc/atamathon.png` 图标**（不是变形/报错，只是比其他首领多一种"部分退化"路径）。开启 nicer_tiles（棋盘地形/棋子玩法的通常前提）时与其余 11 个首领完全一致，判定仍为 **READY**，仅记录为已知边界情况。

## 3. 批次 7 — 次要首领与常驻随从（9 条，逐条复核）

| 身份 | 区域 | define_as/备注 | type/subtype | unique | 来源 file:line | 原生贴图 | 判定 |
| --- | --- | --- | --- | --- | --- | --- | --- | 
| Massok the Dragonslayer | daikara（支线唯一，无 rarity） | MASSOK，继承 `BASE_NPC_ORC_GRUSHNAK` | humanoid/orc | 是 | `zones/daikara/npcs.lua:160-163` | `npc/humanoid_orc_massok_the_dragonslayer.png` 存在 | **READY** |
| Spellblaze Crystal | scintillating-caves（守关，无 rarity） | SPELLBLAZE_CRYSTAL，继承 `BASE_NPC_CRYSTAL` | immovable/crystal | 是 | `zones/scintillating-caves/npcs.lua:30-33` | **显式单图** `image="npc/spellblaze_crystal.png"`，非 composite，存在 | **READY**（单图，最省事） |
| Spellblaze Simulacrum | scintillating-caves（后备守关，无 rarity） | SPELLBLAZE_SIMULACRUM | immovable/crystal | 是 | `zones/scintillating-caves/npcs.lua:75-79` | 单图与 tall 体同一文件 `npc/spellblaze_simulacrum.png`，均存在 | **READY** |
| The Master | dreadfell（主线终层首领，无 rarity） | THE_MASTER | undead/vampire | 是 | `zones/dreadfell/npcs.lua:34-38` | **显式单图** `image="npc/the_master.png"`，非 composite，存在 | **READY** |
| Pale Drake | dreadfell（后备守关，无 rarity） | PALE_DRAKE | undead/skeleton | 是 | `zones/dreadfell/npcs.lua:138-144` | `npc/undead_skeleton_pale_drake.png` 存在 | **READY** |
| Fillarel Aldaren | unremarkable-cave（可招募友方，无 rarity） | FILLAREL | humanoid/elf | 是 | `zones/unremarkable-cave/npcs.lua:30-34` | `npc/humanoid_elf_fillarel_aldaren.png` 存在 | **READY** |
| Krogar | unremarkable-cave（可招募友方，无 rarity） | CORRUPTOR | humanoid/orc | 是 | `zones/unremarkable-cave/npcs.lua:101-105` | `npc/humanoid_orc_krogar.png` 存在 | **READY** |
| Z'quikzshl the skeletal mold | 稀有唯一霉菌（`general/npcs/molds.lua`，高罕见度随机） | 约 102 行块，`unique=true` | immovable/molds（继承 `BASE_NPC_MOLD`） | 是 | `general/npcs/molds.lua:102-104` | **显式单图** `image="npc/immovable_molds_skeletal_mold.png"`，非 composite，存在 | **READY** |
| Rhaloren Inquisitor | rhaloren-camp（唯一，无 rarity） | INQUISITOR | humanoid/shalore | 是 | `zones/rhaloren-camp/npcs.lua:30-33` | 全块**无** `image=`/`nice_tile`，NPC.lua 公式给出 `npc/humanoid_shalore_rhaloren_inquisitor.png`，**磁盘存在且目视确认为持剑精灵法战士肖像** | **READY（订正）**——原文档判定"需夹具核实"，本轮用第 0 节方法论+文件存在+目视三重验证后可直接判定为单图 READY，无需夹具 |

批次 7 原文档给出的 9 条**全部 READY**；其中 Rhaloren Inquisitor 是从"待核实"明确订正为"READY"的一条。

## 4. 第四节特殊合同复核

### 4.1 非唯一 native-tall 复合体——精确的代码改动与风险

`CheckerTokens.lua:171-172`：

```lua
local function nativeTallImage(actor, entry)
	if not (entry.unique or entry.native_tall) or actor.image ~= "invis.png" then return false end
	...
```

`entry.native_tall` 字段**已经存在并已投产**：`overload/mod/class/CheckerTokens.lua:26` 的 `ancient-dragon-turtle` 条目就是用 `native_tall=true` 让一个非 unique 身份走 tall 体路径，`tests/token_mapping.lua:240-245`（"exact non-unique tall aquatic body"）已覆盖这条路径的正反用例。

**结论：所需改动不是给 `CheckerTokens.lua` 新增逻辑分支，而是给下列每条目录条目加一个 `native_tall=true` 字段**，与新增普通身份完全相同的改动量：

| 身份 | 区域 | 来源 file:line | 原生贴图（tall 体内层图） |
| --- | --- | --- | --- |
| dremling | maze（`horror-corrupted.lua`，dungeon 内经 `zones/maze` 及 `deep-bellow` 等 `load()` 复用） | `general/npcs/horror-corrupted.lua:79-82` | `npc/horror_corrupted_drem.png` 存在 |
| shivgoroth | norgos-lair | `general/npcs/shivgoroth.lua:56-58` | `npc/elemental_ice_shivgoroth.png` 存在 |
| greater shivgoroth | norgos-lair | `shivgoroth.lua:71-73` | `npc/elemental_ice_greater_shivgoroth.png` 存在 |
| naga tidewarden | slazish-fen | `zones/slazish-fen/npcs.lua:61-64` | `npc/humanoid_naga_naga_tidewarden.png` 存在 |
| naga tidecaller | slazish-fen | `zones/slazish-fen/npcs.lua:78-80` | `npc/humanoid_naga_naga_tidecaller.png` 存在 |
| xhaiak arachnomancer | ardhungol | `zones/ardhungol/npcs.lua:76-79`，用 `resolvers.nice_tile{tall=1}` 简写 | `npc/spiderkin_xhaiak_xhaiak_arachnomancer.png` 存在（文件名与 NPC.lua 公式吻合，见下方置信度说明） |
| shiaak venomblade | ardhungol | `zones/ardhungol/npcs.lua:106-109`，同为 `{tall=1}` 简写 | `npc/spiderkin_shiaak_shiaak_venomblade.png` 存在（同上） |

原文档写"6 个"，实际点名列出的是 7 个身份（dremling 1 + shivgoroth 2 + naga 2 + xhaiak/shiaak 2），本表已按 7 条列全；加上第 1 节订正的 `treant`，这一类"合同缺口"实际共 **8 条**。

**`{tall=1}` 简写形式的置信度说明**：dremling/shivgoroth/naga tidewarden/naga tidecaller 四条在源码里直接写出完整的 `{image="invis.png", add_mos={{image="npc/xxx.png", ...}}}`，内层图片是源码字面量，100% 确定。xhaiak arachnomancer/shiaak venomblade 用的是 `resolvers.nice_tile{tall=1}` 简写，其展开逻辑在 `modules/tome/resolvers.lua:1372-1385`：`t[1].add_mos[1].image` 会被替换成**解析时刻**的 `e.image`。`engine/Entity.lua:745` 的 `resolve()` 与 `NPC.lua:33` 的默认命名回填分属两个不同阶段，静态读码无法 100% 确认 `resolve()` 执行时 `e.image` 是否已经等于 NPC.lua 公式值。本轮改用**磁盘文件名**佐证：`spiderkin_xhaiak_xhaiak_arachnomancer.png`、`spiderkin_shiaak_shiaak_venomblade.png` 都以 NPC.lua 公式的确切拼写存在于 `gfx/shockbolt/npc/`，与"贴图确实按该约定命名"高度吻合，因此本轮判定沿用原文档"合同缺口"结论，但风险评级比另外 5 条（源码字面量）略高一档，建议出图前用隔离夹具对这两条做一次快速渲染核实（不要求现在启动游戏）。

同样使用 `{tall=1}` 简写、且磁盘上同样存在公式化文件名 `npc/humanoid_naga_naga_nereid.png` 的还有 **naga nereid**（`zones/slazish-fen/npcs.lua:98`），原文档标注"需要夹具核实"；本轮判定与 xhaiak/shiaak 同一置信度，也应归入"NEEDS-CONTRACT-EXTENSION"一类，而不是单独的"未知"状态。naga nereid 不在批次 5–7 任何一张表内，此处作为附带发现记录，不计入下方推荐批次。

**风险评估**：`native_tall=true` 只是放宽 `nativeTallImage()` 的 unique 门槛，`appearance()` 对 tall 体形状本身的校验（唯一一个 `add_mos` 元素、仅允许 `tall_keys` 内字段、`display_h==2`、`display_y==-1`、内层 `image` 必须逐字节等于 `entry.image`）不变，`tests/token_mapping.lua:92-99` 的"altered tall body"用例族对这些校验有完整回归覆盖。已知会以 `dremling` 为名字面量出现的地方只有随机池和作为其他首领的护卫召唤（`horror-corrupted.lua:148` 的 `make_escort`），召唤出的护卫是同一模板的克隆，`name`/`type`/`subtype`/`image` 与目录条目完全一致，不会绕过 `exactIdentity()` 的名字匹配。综合判断：**风险低，且已有 `ancient-dragon-turtle` 一年半以上的同类先例**，可以直接照抄该条目的写法。

### 4.2 建议保持原生——复核结果

- **Melinda**（crypt-kryl-feijan）：`crypt-kryl-feijan/npcs.lua:88-119`，初始 `image="terrain/woman_naked_altar.png"`（注意命名空间是 `terrain/` 不是 `npc/`），并有 `resolvers.generic(function(e) if engine.Map.tiles.nicer_tiles then e.display_w=2 end end)` 根据原生"更精细贴图"选项动态改宽度；救援剧情完成后，`ACOLYTE` 的 `on_die`（`crypt-kryl-feijan/npcs.lua:151-181`）直接改写活体 actor：`melinda.image = "npc/woman_redhair_naked.png"; melinda:removeAllMOs()`。**结论不变：KEEP-NATIVE**，本轮精确定位到触发行号，比原文档更具体。
- **Harno, Herald of Last Hope / Lithfengel（reknor）、Norgan（reknor-escape）**：见第 0 节，**订正为 READY**（均为普通单图，`unique=true`，无需 tall 体扩展）。
- **Lost Merchant**（thieves-tunnels）：不在批次 5–7 范围内，未复核，原文档"低优先级友方 NPC"判断保留。

### 4.3 需夹具核实——复核结果

批次 5–7 范围内唯一一条落在此类的是 **Rhaloren Inquisitor**，已在第 3 节订正为 READY，不再需要夹具。范围外的 Necromancer（blighted-ruins，第 1 节已订正为 READY）、Assassin Lord/Subject Z/Yeek Wayist/Grand Corruptor/The Withering Thing/The Dreaming One/Nimisil（thieves-tunnels、halfling-ruins、mark-spellblaze、heart-gloom、maze，均不在批次 5–7 表内）未复核，原文档的"需夹具"标注保留。

## 5. 附带发现：批次 6/7 所在分区内的其他值得记录的身份

以下不在批次 5–7 的正式表格里，但落在批次 6/7 覆盖的具体区域内，且是任务要求核对的"notable non-unique creatures"，一并记录：

| 身份 | 区域 | type/subtype | unique | 来源 file:line | 原生贴图 | 判定 |
| --- | --- | --- | --- | --- | --- | --- |
| Necromancer | blighted-ruins | humanoid/human | 否 | `zones/blighted-ruins/npcs.lua:29-34` | `npc/humanoid_human_necromancer.png` 存在 | READY（单图，注意与 `general/npcs/orc.lua` 的 "orc necromancer"、`rak-shor-pride` 的 "Rak'shor, Grand Necromancer of the Pride" 同主题但图片不同名，不冲突） |
| fleshy experiment | blighted-ruins | undead/horror（继承 `BASE_NPC_HORROR_UNDEAD`） | 否 | `zones/blighted-ruins/npcs.lua:127-135` | `npc/undead_horror_fleshy_experiment.png` 存在 | READY（单图，`never_move=1` 的固定伤害桩） |
| boney experiment | blighted-ruins | undead/horror | 否 | `zones/blighted-ruins/npcs.lua:158-166` | `npc/undead_horror_boney_experiment.png` 存在 | READY（单图） |
| sanguine experiment | blighted-ruins | undead/horror | 否 | `zones/blighted-ruins/npcs.lua:190-198` | `npc/undead_horror_sanguine_experiment.png` 存在 | READY（单图） |
| Acolyte of the Sect of Kryl-Feijan | crypt-kryl-feijan | humanoid/elf | 否 | `zones/crypt-kryl-feijan/npcs.lua:121-124` | **显式**复用 `image="npc/humanoid_shalore_elven_corruptor.png"`——与该区同时加载的 `general/npcs/elven-caster.lua:143-145` "elven corruptor"（无显式 image，公式命中同一文件）原生共用同一张图 | READY（单图，但需注意：native 美术本就与"elven corruptor"完全相同，出图时必须让二者的棋子插画彼此区分，不能照抄原图直接复用） |
| slimy crawler | deep-bellow | horror/corrupted（继承 `BASE_NPC_CORRUPTED_HORROR`） | 否 | `zones/deep-bellow/npcs.lua:91-96` | 无 `image=`，公式给出 `npc/horror_corrupted_slimy_crawler.png`，存在 | READY（单图，The Mouth 的固定召唤物） |
| The Fragmented Essence of Harkor'Zun | tempest-peak | elemental/xorn（继承 `BASE_NPC_XORN`） | 是 | `general/npcs/xorn.lua:92-94` | `npc/elemental_xorn_fragmented_harkor_zun.png` 存在 | READY（见下方订正说明） |
| Harkor'Zun | tempest-peak（`FULL_HARKOR_ZUN`，无 rarity，仅由 5 个残片死亡合体生成） | demon/major（**显式覆盖**为与残片不同的 type/subtype） | 是 | `general/npcs/xorn.lua:166-169` | `npc/elemental_xorn_harkor_zun.png` 存在 | READY（见下方订正说明） |
| Burb the snow giant champion | tempest-peak | giant/ice（继承 `BASE_NPC_SNOW_GIANT`） | 是 | `general/npcs/snow-giant.lua:109-112` | `npc/giant_ice_burb_the_snow_giant_champion.png` 存在 | READY |

**Harkor'Zun 订正说明**：原文档第三、四节都把"残片"与"完整体"称为"需要独立的多阶段外观合同"的特例。核对源码发现两者是**两个完全独立的 unique 目录条目**：残片没有自己的 `define_as`（不作为可 `base=` 复用的注册体），完整体单独有 `define_as="FULL_HARKOR_ZUN"`，二者 `name`、`type`/`subtype`（残片继承 elemental/xorn，完整体显式改写为 demon/major）、`image` 全部不同，且都各自满足普通 unique native-tall 的标准形状。这与已经验证可行的 Prox/Shax（`tests/token_mapping.lua:157-164`，"Shax reuses Prox base image"用例）是同一模式：**只需要给两个身份各建一条普通目录条目，不需要任何"多阶段"专用代码**。残片死亡后合体成完整体只是游戏机制（`on_die` 里 `game.zone:makeEntityByName(...,"FULL_HARKOR_ZUN")`），对 `identify()` 而言只是"旧 actor 消失、新 actor 出现"，与任何其他召唤/替换场景无异。

## 6. 易混淆同族体（供出图差异化参考）

- **水晶家族**（`immovable/crystal`）：本轮新增 white/red/crimson crystal + Spellblaze Crystal/Simulacrum，共 5 个新身份共享同一大类，且 white crystal 与未来的 shimmering crystal 原生贴图完全相同——出图时 5 者之间、以及未来 black/blue/multi-hued crystal（已有独立贴图，不受此影响）都需要清晰的色彩/造型区分。
- **骷髅家族**（`undead/skeleton`）：目录已收录 7 款（degenerated-skeleton-warrior/archer、skeleton-mage、skeleton-warrior、skeleton-archer、armoured-skeleton-warrior、skeleton-master-archer）。Pale Drake（本轮批次7）与目录已有的"弓箭/剑盾"造型都不同（法师化骷髅巫妖），出图时要与已收录 7 款保持明显区分；Filio Flightfond（附带发现，未正式列入本批）同为 undead/skeleton，如未来收录也要一并考虑。
- **恐惧/腐化家族**（`horror/corrupted`）：目录已收录 Horned Horror。本轮新增 The Mouth、The Abomination、dremling（合同缺口）都是同 type/subtype；`horror-corrupted.lua` 里还有一对容易搞混的命名陷阱——**"drem"（小型怪，`horror-corrupted.lua:44-48`）显式用的是 `npc/horror_corrupted_dremling.png`，而"dremling"（`horror-corrupted.lua:79-82`）用的是 `npc/horror_corrupted_drem.png`**，两个身份的原生贴图文件名与角色名恰好对调，出图排期或校验时极易按名字误配文件，务必按本表核对后的 file:line 与图片名为准，不要凭身份名猜测。
- **霉菌家族**（`immovable/molds`）：目录已收录 grey/brown/green/shining mold 4 款素色蘑菇状霉菌。Z'quikzshl the skeletal mold 是骨质主题的稀有唯一，出图需与已收录 4 款的"平实色块"造型拉开明显差异。
- **兽人首领家族**（`humanoid/orc`）：本轮新增 Golbug the Destroyer、Brotoq the Reaver、Massok the Dragonslayer、Krogar 共 4 位独立兽人 boss/同伴，目录里目前没有任何 humanoid/orc 收录，4 者互相之间需要清晰的轮廓/色彩差异（Golbug 持锤+盾、Brotoq 双持斧剑仿制、Massok 龙骨头盔+巨剑、Krogar 法杖+重甲，武器轮廓已天然提供部分区分线索）。
- **人类施法者家族**（`humanoid/human`）：Urkis、Celia、Necromancer 三者都是持法杖/长袍的人类施法者 boss/怪物，出图需要靠姿态、光效主题（Urkis 雷电、Celia 死灵紫黑、Necromancer 普通黑袍）区分；目录已收录的 cutpurse/rogue/thief/bandit 是平民/盗贼造型，风格不同不构成混淆。

## 7. 统计口径与总计

- 批次 5（9 条，含本轮订正后的 treant）：READY 8，NEEDS-CONTRACT-EXTENSION 1。
- 批次 6（12 条）：READY 12。
- 批次 7（9 条）：READY 9。
- 第四节 4.1 点名的合同缺口（原文档称 6 条，实为 7 条）：NEEDS-CONTRACT-EXTENSION 7。
- 第四节 4.2 订正（Harno/Lithfengel/Norgan）：READY 3；Melinda 维持 KEEP-NATIVE 1。
- 附带发现（同一批次区域内的 notable 非唯一/唯一身份，共 10 条）：READY 10（Necromancer、fleshy/boney/sanguine experiment ×3、Acolyte、slimy crawler、Harkor'Zun 残片+完整体、Burb）。

**核心必查项合计（批次5+6+7+4.1，37 条）：READY 29，NEEDS-CONTRACT-EXTENSION 8，KEEP-NATIVE 0。**
**加上第 0/4.2 节订正与第 5 节附带发现（17 条）：READY 16，NEEDS-CONTRACT-EXTENSION 1（naga nereid，附带发现，置信度见 4.1 说明），KEEP-NATIVE 1（Melinda）。**
**全篇合计 54 条：READY 44，NEEDS-CONTRACT-EXTENSION 9，KEEP-NATIVE 1。**

## 8. 推荐下一批出图（≤12，全部 READY，零工程改动）

批次 6 的全部 12 个区域门面首领——本轮逐条复核后**没有一个例外**，且每一个都是"该区域此前完全没有身份感棋子"的唯一/脚本首领（无 `rarity` 字段，玩家通关该区域必定遭遇），与原文档批次 6 的设计初衷完全吻合，直接按原顺序推荐为下一批：

1. Lady Zoisla the Tidebringer（slazish-fen）
2. Urkis, the High Tempest（tempest-peak）
3. Golbug the Destroyer（reknor）
4. Brotoq the Reaver（reknor-escape）
5. Ungolë（ardhungol）
6. Half-Finished Bone Giant（blighted-ruins）
7. Kryl-Feijan（crypt-kryl-feijan）
8. Atamathon the Giant Golem（golem-graveyard，注意 4.2 节 nicer_tiles 关闭时的单图兜底例外）
9. Ritch Great Hive Mother（ritch-tunnels）
10. The Mouth（deep-bellow）
11. The Abomination（deep-bellow）
12. Celia（last-hope-graveyard）

若产能允许拆成两批，优先出 1–9（每区域一款，覆盖面最大化）；10/11 同属 deep-bellow 一个区域，12 可与批次 7 的 Massok/Spellblaze Crystal 等其余 READY 项合并到第三批。
