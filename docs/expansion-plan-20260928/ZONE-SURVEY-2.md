# 未支持地城普查（2026-09-28，base game，level_range 下限 ≤30）

**第三批后续状态（2026-09-28）：** `ritch-tunnels` 实际为 L1–L3，`SANDWALL_STABLE` 在本版源码可挖成永久沙地，与临时隧道 `SANDWALL` 规则不同但可共用外观；`deep-bellow` L1–L3 增加中性 plain 地下皮肤；`last-hope-graveyard` L1 森林草地／世界出口、L2 基础石质格接入，墓碑、棺材、沼泽树、道路与陵寝入口原生，两张静态图均无水格。八次独立冷启动支持格 14,139／14,139、回退 0；详见[第三批证据](../../evidence/batch3-20260928/README.md)。本批不改版本、不打包、不提交。

**第二批后续状态（2026-09-28）：** `ruined-dungeon`、`blighted-ruins`、`crypt-kryl-feijan`、`golem-graveyard`、`ardhungol` 已按精确身份接入并独立逐层验证；`lake-nur` 双布局仅 L1 地表有森林套件覆盖，L2 与两布局 L3 需水下新美术或干燥石质混合适配，仍原生。19 个场景受支持格 27,593／27,593 绘制、回退 0；其中纳尔湖四个下层场景支持格为 0。上／下层洞穴梯子由既有母版和原生剪影导出，零次新生图。详情见[第二批实机证据](../../evidence/reuse-batch2-20260928/README.md)。本批按任务不改版本、不打包、不提交。

**后续实施状态（2026-09-28）：** 本文下方排序是当时的静态候选快照；其中 `thieves-tunnels`、`tempest-peak`、`halfling-ruins`、`reknor`、`reknor-escape` 已在源码通过逐层实机复用核验，合计 15 层、31,383／31,383 支持格绘制、回退 0，未打包／未提交。`ardhungol` 因洞穴上／下梯子缺已审图而跳过；`lake-nur` 等其余候选仍未接入。逐层证据见 [复用批次](../../evidence/reuse-batch-20260928/README.md)。游戏原版地名分别是「未知通道」「风暴之巅」「半身人废墟」「瑞库纳·失落的矮人王国」「从瑞库纳逃亡」「阿尔德胡格」；下方早期中文简称仅作历史调查标签。

只读静态分析：未启动游戏、未生成美术、未提交。数据来源为 `game/modules/tome/data/zones/<zone>/{zone,grids}.lua`、`data/general/grids/*.lua`、`data/maps/wilderness/eyal.lua`、`data/general/encounters/maj-eyal.lua`。方法与格式沿用 `game/addons/tome-checker-revised/docs/expansion-plan-20260928/TERRAIN-INVENTORY.md`，"已支持"以其列出的十二个地城为准（trollmire、ruins-kor-pul、old-forest、slazish-fen、rhaloren-camp、dreadfell、norgos-lair、daikara、maze、heart-gloom、sandworm-lair、scintillating-caves），unremarkable-cave（进行中）与 ancient-elven-ruins（计划中，等级 43+ 本次不含）不重复列出。

未检索到 base game 之外符合"官方 DLC 地城目录"的 `game/addons/*` 目录（如 tome-orcs、tome-ashes-urhrok），当前 `game/addons/` 下只有两个棋盘插件自身，因此本轮无额外 DLC 条目。

## 0. 范围与排除

`game/modules/tome/data/zones/` 共 93 个目录。按 `level_range` 下限 ≤30 筛选后，排除：
- 世界地图／城镇专用：`wilderness`、`town-*`（8 个，见文末简列）；
- 挑战／竞技非地城：`arena`、`arena-unlock`、`ring-of-blood`；
- 职业／种族个人位面或占位关卡：`paradox-plane`、`demon-plane-spell`、`temporal-reprieve-talent`、`dreamscape-talent`、`dreams`、`eidolon-plane`、`gladium`、`infinite-dungeon`、`stellar-system-shandral`；
- 单层剧情插曲：`dreadfell-ambush`（附属于已支持的 Dreadfell）；
- 测试用：`test`、`tutorial`、`tutorial-combat-stats`。

以上均非"玩家在其中战斗探索的地城"主体或暴露面极低，仅在文末简列，不进入排名表。

`level_range` 下限恰为 30 的一批（`briagh-lair`、`orc-breeding-pit`、`telmur`、`temple-of-creation`、`valley-moon-caverns`、`vor-armoury`、`charred-scar`、`flooded-cave`、`rak-shor-pride`、`demon-plane`）多为中后期"boss 巢穴"型一次性地城（Cavern/Roomer/Static 生成，类似已支持的 Norgos' Lair 但等级更高），处于任务给定阈值边界，本轮只列目录未展开身份分析，见第 4 节。

以下 25 个是本轮实际展开分析的候选（含 `docs/expansion-plan-20260928/TERRAIN-INVENTORY.md` 第 13 节已轻筛但未展开的 7 个）。

## 1. 排序表

排序依据：①在固定地图或高频随机遭遇上的暴露面（②）；②新美术估算（越少越前）；③等级越早越靠前。"复用来源"指已在棋子仓库实现或规划中的身份族。

| 排名 | 地城 | short_name | 等级 | 布局×层 | 暴露面 | 复用来源 | 新母版估计 | 风险 |
| ---: | --- | --- | --- | --- | --- | --- | ---: | --- |
| 1 | 未知隧道 | thieves-tunnels | 14–28 | 1×2 | 随机世界遭遇（常见池，`maj-eyal.lua`） | Maze `OLD_FLOOR`/`OLD_WALL`（0.6.20 已发布） | 0 | 低：L2 是任务静态小图 `quests/lost-merchant`，需确认其字符集也落在 basic |
| 2 | 风暴之巅 | tempest-peak | 15–22 | 1×2 | 固定世界地图 POI（`addSpot 60,9`） | Daikara 裸岩+岩山墙（0.6.20 已发布） | 0 | 低：无雪岩重皮，与 Daikara 身份幅面几乎一致，仅需核对 `MOUNTAIN_WALL` 掩码形态是否一致（Roomer vs Roomer） |
| 3 | 努尔湖 | lake-nur | 15–25（FLOODED×2） | 2×3 | **主线毗邻**：Old Forest L4 下楼直达，且是 Sher'Tul Fortress 入口 | 森林式 grass/tree/exit + water/bog | 0–1 | 低：与 Old Forest 同族，需确认 `OLD_FOREST`/`SHERTUL_FORTRESS_*` 出口归入 `exit` |
| 4 | 半身人遗迹 | halfling-ruins | 10–25 | 1×4 | 固定世界地图 POI（`addSpot 37,32` + `defineTile`） | Kor'Pul 石头组（basic.lua 零覆盖） | 0 | 低：`lesser_vault`/`greater_vault` 密室内容保持原生 |
| 5 | 雷肯诺矮人王国 | reknor | 18–35 | 1×4（L4 静态图） | 固定世界地图 POI（`addSpot 69,22`），矮人主线终点 | Kor'Pul 石头组 | 0 | 低：L4 静态图 `zones/reknor-last` 字符集待核实，但生成器同样只声明 FLOOR/WALL/DOOR/UP/DOWN |
| 6 | 阿德红戈尔 | ardhungol | 25–32 | 1×3 | 固定世界地图 POI（`addSpot 162,28`） | Unremarkable Cave 的 `cave.lua`（CAVEFLOOR/CAVEWALL/CAVE_LADDER，进行中）+ water | 0（借用后） | 低：`WORMHOLE` 需类比 Abashed Expanse 的同名处理，保持原生 |
| 7 | 废弃地牢 | ruined-dungeon | 10–30（ALT1×1） | 1×1 静态图 | 随机世界遭遇（常见池，是经典"法阵解谜"地城） | Kor'Pul 石头组（basic.lua） | 0–1 | 低中：`LORE*`/`LOCK`/`PORTAL` 为本区悬浮法阵装饰，回退原生属预期 |
| 8 | 逃离雷肯诺 | reknor-escape | 1–7 | 1×3 | 矮人种族开局链（`birth/races/dwarf.lua`），随后接 `reknor`/`ardhungol` | Kor'Pul 石头组 | 0 | 低；暴露面窄（限矮人种族开局），但与 #5/#6 同批做可摊薄成本 |
| 9 | 荒芜废墟 | blighted-ruins | 1–7 tier1 | 1×3 | 种族开局相关（`birth/races/undead.lua`引用） | Kor'Pul 石头组 | 0 | 低；`SUMMON_CIRCLE*` 装饰回退原生 |
| 10 | 克里尔·费依安暗穴 | crypt-kryl-feijan | 25–35 | 1×5 | 随机世界遭遇 | Kor'Pul 石头组 | 0–1 | 低中：`LOCK`/`ALTAR`/`PENTAGRAM` 本区覆盖，回退原生 |
| 11 | 最后的希望墓地 | last-hope-graveyard | 15–25 | 1×2 | 固定世界地图 POI（`addSpot 62,39`），紧邻主城 Last Hope | L1 森林式草地／世界出口 + L2 Kor'Pul 石质格（仅 UP） | 1–2 | 中：`GRAVE*`(44 个)/`COFFIN`/`MAUSOLEUM`/`SWAMPTREE` 均按第三批决定保留原生；静态图无水格；L1 草地与 L2 石质格已验证 |
| 12 | 石魔像墓地 | golem-graveyard | 14–20 | 1×1 | 随机世界遭遇 | 森林式 grass/tree/exit | 0 | 低：`ATAMATHON_BROKEN`（boss 雕像）回退原生 |
| 13 | 无尽深渊 | deep-bellow | 1–7 | 1×3 | 矮人种族开局（连接 `town-iron-council`） | Heart of Gloom 的 underground 支架，但已新增 plain 中性皮肤（非 gloomy/dreamy） | 2–3 | 中：本版 `underground.lua` 实际载入 gloomy 原生定义；第三批以来源和最终规则门控，再用中性配色显示 |
| 14 | 里奇通道 | ritch-tunnels | 1–7 tier1 | 1×3 | 固定世界地图 POI（`defineTile`） | Sandworm Lair 的 sand 组（0.6.20 已发布），`SANDWALL_STABLE` 可挖成永久沙地，临时隧道规则仍仅属于 `SANDWALL` | 0（借用后） | 低：第三批已确认墙图可复用、规则合同分支门控；三层验证 |
| 15 | 幻境城堡 | illusory-castle | 25–30 | 1×5 | **暴露面≈0**：未在任何世界地图、随机遭遇池、quest/chat 引用中找到入口，疑似遗留/未接入内容 | Kor'Pul 石头组（basic.lua 纯净） | 0 | 低成本但优先级最低：先确认游戏内是否有实际入口，否则不值得投入验收工时 |

以下等级更早、进入常规路线，但需要新美术族或结构较复杂，单列于表外：

| 地城 | short_name | 等级 | 暴露面 | 复用要点 | 新母版估计 | 风险 |
| --- | --- | --- | --- | --- | --- | --- |
| 咒符斗篷法印 | mark-spellblaze | 15–25 | 固定区域世界遭遇（41–46,40–45 一整片） | `BURNT_GROUND`/`BURNT_TREE`（burntland.lua）新族；潭中 `LAVA` | 3–4 | 中：需要新"焦土"族，森林适配器要再加一个 subtype 分支 |

| 古老议会金库 | conclave-vault | 20–30 | 随机世界遭遇 | 结构身份（FLOOR/WALL/UP/DOWN）复用 Kor'Pul，但 `WALL*`/`RUNE_FLOOR`/`BLOOD_FLOOR`/`DECO_FLOOR*` 全部本区覆盖（重新贴图），回退原生比例高 | 0（结构）＋大量原生回退 | 中：入口静态图 `!conclave-vault-entrance` 待核实 |
| 静谧草甸 | keepsake-meadow | 15–25 | 随机世界遭遇（"传送门重制品"任务链） | 主层 Cavern 复用 cave.lua（同 Ardhungol/Unremarkable）；4 个静态叙事层（草甸/梦境/洞口/洞穴终局）几乎全本区覆盖 | 4–6 | 中高：多层混合，静态叙事层价值低但工作量不小 |
| 时空裂隙 | temporal-rift | 16–30 | **已完成本轮精确支持**（时空术士专属） | L1 void 新族；L2 伐木村石质／森林；L3 Daikara 岩组；L4 纳尔湖已支持地表格 | 3 件新母版由三区共用 | 十层实机记录见 `evidence/void-20260928/README.md`；特殊格原生 |
| 幽灵沼泽 | murgol-lair | 1–7 tier1 | 未见于固定地图/常见遭遇池，暴露面待查 | `WATER_FLOOR`/`WATER_WALL` 为"整层泡在水里"，不同于 Trollmire 的局部沼泽，需要新的"水下地城"族 | 3–4 | 中高：与既有 water/bog 适配器语义不同，不能直接套 |
| 混沌之沼 | unhallowed-morass | 1–7 tier1 | **已完成本轮精确支持**（时空术士开局） | `VOID`／`SPACETIME_RIFT` 共用 void 族；剧情 RIFT 原生 | 三区共用 3 件 | 三层独立冷启动 7,498／7,498，零回退 |
| 次元浮岛 | abashed-expanse | 1–7 tier1 | **已完成本轮精确支持**（大魔导师开局） | `FLOATING_ROCKS`／`OUTERSPACE`；`WORMHOLE` 与枯树原生 | 三区共用 3 件 | 三层独立冷启动 7,403／7,403，移动平台复刷零回退 |
| 恶臭火山口 | noxious-caldera | 25–35 | 随机世界遭遇 | `mountain.lua` 部分可搭 Daikara 岩组；`jungle.lua` 为全新丛林族，之前任何已支持/进行中地城都未用过 | 3–5 | 中高：`GenericTunnel` 自定义生成器，墙体连通形态未知，需先核实 |
| 南滩 | south-beach | 24–35 | 低：仅见于 `love-melinda.lua`（梅琳达同伴支线），单层静态图 | 未查身份，需要单独核对 `zones/south-beach` 静态图图例 | 待查 | 低优先：暴露面窄，先不展开 |
| 谢尔图尔要塞 | shertul-fortress | 18–25 | **剧情枢纽**：多个职业问答支线、法印任务归宿、可回程往返努尔湖 | 使用独立 `fortress.lua`（`solid_floor1.png` 科技风），非 basic.lua，且大量函数格（FARPORTAL/COMMAND_ORB/LIBRARY/训练靶场），逐格适配器难以命中 | 5+ | 高：叙事权重最大但改造成本也最高，建议单列专项，不与本批打包 |

2026-09-28 状态更新：`mark-spellblaze` 焦土族已以既有母版和原生材质导出 42 张运行图（ImageGen 0/4），接入 L1 Forest 与 L2 Forest＋静态祭坛图；`LAVA` 在本区阻挡移动、无站立伤害，与 Daikara 可通行熔岩不同。隔离夹具两层独立冷启动支持格 5,731/5,731、原生回退 0；祭坛与特殊改写格保持原生。详见 [实机证据](../../evidence/spellblaze-20260928/README.md)。本表的“新母版估计”和风险栏保留立项时预测，不代表当前剩余工作。

## 2. 各地城简注

**thieves-tunnels（未知隧道，14–28）**：`TileSet`（3x3/base+tunnel+windy_tunnel），`grids.lua` 只 `load(basic)`，身份精确为 `OLD_FLOOR`/`OLD_WALL`/`DOOR`/`DOWN`，`up=OLD_FLOOR`（无独立楼梯贴图，与 Maze COLLAPSED 同款设计）。L2 是固定支线小图 `quests/lost-merchant`（“失踪商人”），敌对阵营改判为 `assassin-lair`，地形字符待核实但大概率仍是 basic 家族。一旦 Maze 的 `OLD_*` 精确身份适配器落地，本区扩一行门控即可。

**tempest-peak（风暴之巅，15–22）**：Roomer（`lesser_vault`: circle、perilous-cliffs），身份为 `ROCKY_GROUND`（floor/rock）、`MOUNTAIN_WALL`（wall/rockwall，Roomer 墙形），无雪皮重写、无熔岩，形态与 Daikara 非熔�onic 部分（第 9 节实现）几乎同构。`guardian=URKIS`。风险主要是核对墙体连通掩码在 Roomer 与 Daikara Roomer 下是否一致（理论应一致，因为都是同一 Roomer 生成器）。

**lake-nur（努尔湖，15–25，FLOODED 变体）**：`alternateZone`，Roomer，`grids.lua` 加载 basic+forest+water+sand。本区定义 `OLD_FOREST`（`change_level=4, change_zone="old-forest"`，即 Old Forest L4 的对向出口）与两个 `SHERTUL_FORTRESS_*` 入口（`change_zone="shertul-fortress"`）。是唯一一个与已支持地城直接地图相连、又通向下一步规划目标（Sher'Tul Fortress）的候选，建议优先做。需要与 Old Forest 用同一套 `dark_grass`/`grass` 判据核对，FLOODED 变体可能引入 bog 系水体（与 Trollmire 同族）。

**halfling-ruins（半身人遗迹，10–25）**：Roomer（`greater_vault`: living-weapons），`grids.lua` 只 `load(basic, forest, water)`，但地图字符只声明 `FLOOR`/`WALL`/`UP`/`DOWN`/`DOOR`，forest/water 应仅供密室池使用（与 Dreadfell 同类模式）。零覆盖、零新美术。

**reknor（雷肯诺矮人王国，18–35）**：`TileSet`（7x7/base+tunnel），`grids.lua` 只 `load(basic)`，本区新增 `FAR_EAST_PORTAL`（通向 `unremarkable-cave`，`level_name="wilderness-1"` 意味着从世界地图重新出发）及 `IRON_THRONE_EDICT` 剧情格。L4 换用静态图 `zones/reknor-last`（70×70），字符集未直接核实但生成器缺省字段同样只有 FLOOR/WALL/DOOR/UP/DOWN，风险可控。矮人主线终点，叙事权重高。

**ardhungol（阿德红戈尔，25–32）**：Cavern，`grids.lua` 加载 basic+cave+water，身份精确复刻 Unremarkable Cave 的 `CAVEFLOOR`/`CAVEWALL`/`CAVE_LADDER_UP/DOWN`，另有 `WORMHOLE`（`base="CAVEFLOOR"`, `nice_tiler=false`，类似 Abashed Expanse 的同名装置，保持原生）。一旦 Unremarkable Cave 的洞穴族完工，本区几乎零成本复用；本身也是固定世界地图 POI。

**ruined-dungeon（废弃地牢，10–30，ALT1 变体）**：唯一层，静态图 `zones/ruined-dungeon`，`grids.lua` 只 `load(basic)`，本区覆盖为 `LORE*`（题词，`terrain/maze_floor.png`，注意用了迷宫地板贴图而非 basic 地板，需按名称/来源判定回退原生）、`LOCK`（封印门）、`PORTAL`（六色法阵球）、`INFINITE`（通往 Infinite Dungeon 的隐藏楼梯）。结构墙/地/门/楼梯若走 basic 家族即可复用 Kor'Pul，装饰格按合同回退原生，属于预期结果。是随机世界遭遇中较有名的解谜地城。

**reknor-escape / blighted-ruins / deep-bellow / murgol-lair / ritch-tunnels / unhallowed-morass**：这 6 个是 `docs/expansion-plan-20260928/TERRAIN-INVENTORY.md` 第 13 节已轻筛的 tier1 地城，本轮补充：
- `reknor-escape`（1–7）：`TileSet`，`grids.lua` 仅 `load(basic)`，唯一覆盖 `IRON_COUNCIL`（返回 `town-iron-council` 的楼梯），零新美术；矮人种族开局关卡，随后接 `reknor`。
- `blighted-ruins`（1–7，tier1）：Roomer，`grids.lua` 仅 `load(basic)`，覆盖为 `SUMMON_CIRCLE*`（地板叠层，非新 kind），零新美术；种族相关但具体触发链未逐一核实。
- `deep-bellow`（1–7）：L1–L2 Cavern、L3 静态图；`grids.lua` 的 `underground.lua` 在本版继续载入 `underground_gloomy.lua` 原生定义。第三批已以精确来源和最终规则接入 plain 中性显示皮肤；返回 `town-iron-council` 的特殊出口原生。
- `murgol-lair`（1–7，tier1）：Roomer，`grids.lua` 为 basic+water，`underwater=true`，地板本身就是 `WATER_FLOOR`（非局部沼泽），与已有 bog/water 适配器语义不同（那是"陆地夹杂水塘"，这是"整层水下"），需要专门的水下地城族，成本中高；未在固定地图或随机遭遇池中找到入口，暴露面待查。
- `ritch-tunnels`（1–7，tier1）：三层 Roomer，`grids.lua` 为 basic+sand；第三批确认 `SANDWALL_STABLE` 在本版可挖成永久 `UNDERGROUND_SAND`，与 `SANDWALL` 的临时隧道不同。规则分别门控、显示复用 Sandworm 沙墙；世界地图固定位置（`defineTile`）。
- `unhallowed-morass`（1–7，tier1）：Cavern，`grids.lua` 为 basic+void，身份为 `VOID`（floor）、`SPACETIME_RIFT`（wall/rift）、`RIFT`（down），与 Temporal Rift L1 共用同一 void 族；三区迭代已完成，`RIFT` 剧情出口保留原生，三层支持格 7,498／7,498、回退 0；时空术士开局关卡。

**其余（表外，新族或复杂结构）**：`conclave-vault`、`keepsake-meadow`、`noxious-caldera`、`south-beach`、`shertul-fortress` 见上表简注。`mark-spellblaze`、`temporal-rift` 与 `abashed-expanse` 已在后续迭代完成精确支持；特殊格继续原生。

## 3. 城镇（简列，不展开）

以下 8 个 `town-*` 是城镇/据点，非玩家常规战斗地城，等级下限均 ≤30（`town-derth`/`town-elvala`/`town-irkkk`/`town-iron-council`/`town-point-zero`/`town-shatur` 均为 1–15，`town-lumberjack-village` 8–14，`town-last-hope` 15–35，`town-zigur` 15–50，`town-angolwen` 20–50，`town-gates-of-morning` 33–50）。它们不属于本次盘点范围，未展开身份分析。

## 4. 等级下限恰为 30 的边界地城（仅列目录，未展开）

`briagh-lair`（30–40）、`orc-breeding-pit`（30–60）、`telmur`（30–40）、`temple-of-creation`（30–40）、`valley-moon-caverns`（30–40）、`vor-armoury`（30–40）、`charred-scar`（30–50）、`flooded-cave`（30–40）、`rak-shor-pride`（30–60）、`demon-plane`（30–40，法系职业个人位面）。多为 Cavern/Roomer/Static 生成的中后期"首领巢穴"型一次性地城，性质更接近已支持的 Norgos' Lair 而非常规多层地城，正好卡在任务给定的 ≤30 阈值边缘，建议下一轮单独评估是否值得纳入。

## 5. 结论：前五推荐

1. **thieves-tunnels** — Maze 的 `OLD_FLOOR`/`OLD_WALL` 已产出未打包，直接复用零成本，随机世界遭遇暴露面尚可。
2. **tempest-peak** — Daikara 裸岩+岩山墙已产出未打包，固定世界地图 POI，零新美术。
3. **lake-nur** — 与已支持的 Old Forest 直接地图相连（L4 出口对接），森林式适配器可大比例复用，且是通往规划中 Sher'Tul Fortress 的门户。
4. **halfling-ruins** — 纯 basic.lua，零覆盖零新美术，固定世界地图 POI，等级低（10–25）。
5. **reknor / ardhungol / reknor-escape 三连** — 矮人主线一条龙：`reknor-escape`（种族开局，纯 basic）→`reknor`（固定地图 POI，纯 basic，仅 L4 静态图待核实）→`ardhungol`（固定地图 POI，直接复用 Unremarkable Cave 的洞穴族），三区叙事连贯，可打包成一个"矮人套件"一次性验收。

## 2026-09-29 T5 状态补记

纳尔湖 DEFAULT/FLOODED 的 L1–L2 与 FLOODED L3 已按原生 `water.lua` 精确身份接入水下地板、阻挡视线与移动的珊瑚墙、开闭门及普通上下楼；水下空气消耗、挖掘和门的切换目标都保留原生规则。L1 静态图的普通沙地复用既有沙地套件；时空裂隙 L4 的同一静态图也采用精确水墙／门／沙地合同。DEFAULT L3 的普通石质格使用既有 Kor'Pul 石组；两个谢尔图尔要塞入口有任务检查回调，继续原生。带消耗回调的空气泡也原生。详见 [T5 身份与实机证据](../../evidence/t5-20260929/README.md)。

最后的希望墓地 L1 新接入普通石路与可挖沼泽树；L2 石质硬墙原已由基础石组覆盖。`GRAVE1..44` 的阻路回调会学习传说，闭合棺材的创建／打开回调涉及亡灵或物品，保持原生。L1 `MAUSOLEUM` 实际是可通行换层入口而非墙，不能画成阻挡墙。旧表的“保留原生”栏是立项时快照，不表示本补记后的当前覆盖。

次元浮岛三层出现的 `BURNT_TREE*` 原生图底板改写为浮岩；本批使用既有透明焦树母版与连片浮岩图逐掩码合成，保持阻挡、视线、穿树与挖掘规则。`PALMTREE` 虽是静态树，在本批已覆盖的沙虫巢穴与里奇通道生成器／地图中没有实际候选，未纳入运行美术。
