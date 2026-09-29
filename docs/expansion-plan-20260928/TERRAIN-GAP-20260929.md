# 棋盘地形缺口普查（2026-09-29）

只读调研，未启动游戏、未生图、未改任何源码或其他文档、未提交。目的：回答“还有哪些地形玩家仍会看到原生画面”，并排出小而完整的后续套件。

**引用约定。** `CT:n` = 本仓库 `overload/mod/class/CheckerTerrain.lua` 第 n 行；`Grid.lua:n` = `superload/mod/class/Grid.lua`；`load.lua:n` = `hooks/load.lua`；`ev/<目录>` = `evidence/<目录>/`；无前缀的 `data/...`、`class/...` 路径均相对 `game/modules/tome/`（游戏原版源码）。证据分三级：**［源码］**读过原版源码；**［实机］**来自证据目录中的实机 survey／README；**［推断］**由前两者推得、未直接量到，均逐条标注。

**数据局限（先读）。** ① `survey.json` 的逐身份“保持原生”清单（`details.kept_native`）只从第三批（`ev/batch3-20260928`）起记录；Trollmire、Old Forest、Slazish、Kor'Pul、Rhaloren 等较早批次的 `kept_native` 为 `null`，只能靠源码与 README 推断，见 2.4。② 早期清单会被后续批次取代（如纳尔湖 L2/L3、墓地 GRAVE/COFFIN、次元浮岛 BURNT_TREE 在 T5／墓园道具批中已接入），下文只采用最新一批。③ 旧文档 `ZONE-SURVEY-2.md` 写“共 93 个目录”，实测 `ls data/zones | wc -l` = **89**，以本文为准。④ 行号引用取自调研时的源码，之后若有改动可能偏移几行。

---

## 0. 结论摘要

| 项 | 数 |
| --- | ---: |
| `data/zones/` 目录总数 | 89 |
| 已覆盖区域（含布局变体） | **48**（其中兽人育种棚不可达；可达 47） |
| 未覆盖、正常游戏可达 | **37**（城镇 11、世界地图 1、剧情／可选地城 15、模式／教程 4、职业／天赋位面 6） |
| 未覆盖、无入口或仅开发用 | 4（`illusory-castle`、`gladium`、`void`、`test`） |
| 已覆盖区域内仍原生的“身份类”（2.2＋2.3，去并项后共 39 类） | FEASIBLE **20** ／ NEEDS-DESIGN **11** ／ KEEP-NATIVE **8** |

最大遗漏（按玩家遭遇频度）：

1. 事件光环圈在 gloom／沙／晶／洞／焦土／骨／水下／虚空／堡垒等族里仍原生（约 34/48 个已覆盖区有光环事件）。
2. Old Forest CRYSTALINE 布局的晶簇补丁（约 1/3 的 Old Forest 局，每层数处）。
3. 出口与无回调门／道具（Old Forest→Lake of Nur 下楼口、`FLAT_*` 出口、`DOOR_VAULT`、`LOCK`、Tempest Peak 石梯与 22 扇门）。

推荐前三套（详见第 4 节）：**S1 光环全族补齐**、**S3 Old Forest 晶簇＋外围石质密室**、**S2 出口／无回调门与静态道具**。城镇／世界地图曝光量最大但不在“地城全覆盖”范围内，需用户先定范围（S7）。

---

## 1. 区域覆盖

### 1.1 覆盖如何判定（源码）

- 森林族：`FOREST_ZONES` 白名单，`CT:1584-1585`。
- 其他族由 `applyForest` 内按 `zone.short_name` 计算的标志门控，`CT:1599-1623`。
- 石质（Kor'Pul）族由 `M.variant` 白名单，`CT:1919-1953`；同层混用族登记在 `M.combined`，`CT:2162-2163`。
- 来源戳只在 `Grid.lua:7-27` 列出的文件加载时打；`data/general/grids/` 中其余文件（如 `mountain.lua`、`slime.lua`、`gothic.lua`、`ice.lua`、`jungle_hut.lua`、`snowy_forest.lua` 等）没有戳也没有适配器。
- 设置页说明（`load.lua:32`）列出 47 个区域，与代码一致；兽人育种棚仅存于代码，是有意从说明中移除。

### 1.2 已覆盖 48 区

频度档位：**A** 多数新局必经；**B** 进度地城（`data/birth/worlds.lua:113-117` `zone_tiers`）或主线链；**C** 可选遭遇／任务／固定世界 POI；**D** 仅特定种族／职业起始；**E** 罕见／晚期。

| 区域（level_range） | 已验证层×布局 | 证据 | 到达方式／频度 |
| --- | --- | --- | --- |
| trollmire (1–7) | DEFAULT／FLOODED L1–3；FLOODED L4 宝藏图 | `ev/runtime-v0614` | 多个种族起始＋tier1：**A** |
| ruins-kor-pul (1–7) | DEFAULT／HIDEOUT L1–3 | `ev/runtime-v0617` | 构造体起始＋tier1：**B** |
| rhaloren-camp (1–7) | DEFAULT／OVERGROUND L1–3 | `ev/runtime-v0616` | tier1：**B** |
| norgos-lair (1–7) | DEFAULT／INVADED L1–3 | `ev/norgos-20260928` | 索拉洛起始＋tier1：**B/D** |
| scintillating-caves (1–7) | DEFAULT L1–3／TWISTED L1–5 | `ev/scintillating-20260928` | 沙洛尔／巨人起始＋tier1：**B/D** |
| heart-gloom (1–7) | gloomy／PURIFIED L1–3 | `ev/heart-gloom-20260928` | tier1：**B** |
| slazish-fen (1–7) | L1–3 | `ev/runtime-v0615` | 东部 Gates of Morning 开局：**D** |
| deep-bellow (1–7) | L1–3 | `ev/batch3-20260928` | 矮人 tier1 二选一：**D** |
| ritch-tunnels (1–7) | L1–3 | `ev/batch3-20260928` | 夜鬼起始＋世界点：**D** |
| murgol-lair (1–7) | DEFAULT／INVASION L1–3 | `ev/batch4-20260929` | 夜鬼起始：**D** |
| reknor-escape (1–7) | L1–3 | `ev/reuse-batch-20260928` | 矮人起始：**D** |
| blighted-ruins (1–7) | L1–3 | `ev/reuse-batch2-20260928` | 亡灵起始：**D** |
| abashed-expanse (1–7) | L1–3 | `ev/void-20260928`、`ev/t5-20260929` | 大魔导师职业开局：**D** |
| unhallowed-morass (1–7) | L1–3 | `ev/void-20260928` | 时空职业开局：**D** |
| sandworm-lair (7–16) | DEFAULT L1–4／BIGWORM L1–2 | `ev/sandworm-20260928` | tier2：**B** |
| old-forest (7–16) | DEFAULT／CRYSTALINE L1–4 | `ev/runtime-v0615` | tier2；L4 出口通向 Lake of Nur：**B（高）** |
| maze (7–16) | DEFAULT L1–2／COLLAPSED L1–4 | `ev/maze-20260928` | tier2：**B** |
| daikara (7–16) | DEFAULT／VOLCANO L1–4 | `ev/daikara-20260928` | tier2：**B** |
| halfling-ruins (10–25) | L1–4 | `ev/reuse-batch-20260928` | tier2：**B** |
| thieves-tunnels (14–28) | L1–2 | 同上 | 世界遭遇：**C** |
| dreadfell (15–26) | L1–9 | `ev/runtime-v0617` | tier3＋Staff of Absorption 任务：**B** |
| reknor (18–35) | L1–4 | `ev/reuse-batch-20260928` | tier3：**B/D** |
| unremarkable-cave (25–35) | L1 | `ev/unremarkable-20260928` | tier3：**B** |
| vor-armoury (30–40) | L1–2 | `ev/batch5-20260929` | tier3／west-portal 任务：**B** |
| briagh-lair (30–40) | L1 | 同上 | tier3：**B** |
| tempest-peak (15–22) | L1–2 | `ev/reuse-batch-20260928` | 世界固定 POI＋任务：**C** |
| lake-nur (15–25) | DEFAULT／FLOODED L1–3 | `ev/t5-20260929` | Old Forest L4 出口；Sher'Tul 入口：**B（高）** |
| shertul-fortress (18–25) | L1 | `ev/batch5-20260929` | 任务枢纽：**B** |
| golem-graveyard (14–20) | L1 | `ev/reuse-batch2-20260928` | 世界遭遇：**C** |
| last-hope-graveyard (15–25) | L1–2 | `ev/t5-20260929`、`ev/graveyard-props-20260929` | 固定世界 POI：**C** |
| ruined-dungeon (10–30) | L1 | `ev/reuse-batch2-20260928` | 世界遭遇：**C** |
| crypt-kryl-feijan (25–35) | L1–5 | 同上 | 世界遭遇：**C** |
| ardhungol (25–32) | L1–3 | 同上 | 固定世界 POI：**C** |
| mark-spellblaze (15–25) | L1–2 | `ev/spellblaze-20260928` | 固定区域遭遇：**C** |
| temporal-rift (16–30) | L1–4 | `ev/void-20260928`、`ev/t5-20260929` | 时空术士专属＋Daikara 入口：**D** |
| south-beach (24–35) | L1 | `ev/batch4-20260929` | `love-melinda` 支线：**E** |
| keepsake-meadow (15–25) | L1–6 | 同上 | 世界遭遇：**C** |
| noxious-caldera (25–35) | L1–2 | 同上 | 夜鬼／梦境：**D** |
| conclave-vault (20–30) | 静态 L1／Roomer L2–4 | 同上 | 沙洛尔／奖励区：**E** |
| telmur (30–40) | L1–5 | `ev/batch5-20260929` | east-portal 任务：**C** |
| ancient-elven-ruins (43–52) | L1–3 | 同上 | 世界遭遇：**E** |
| valley-moon-caverns (30–40) | L1–2 | 同上 | 固定世界 POI：**C/E** |
| flooded-cave (30–40) | L1–2 | 同上 | 远东遭遇／任务：**E** |
| temple-of-creation (30–40) | L1–3 | 同上 | 任务：**E** |
| charred-scar (30–50) | L1 | 同上 | 经 Eruan 法阵：**B（主线）** |
| demon-plane (30–40) | L1 | 同上 | Tannen 背叛支线：**E** |
| rak-shor-pride (30–60) | L1–3 | `ev/rakshor-20260929` | 兽人部落任务：**B/C** |
| orc-breeding-pit (30–60) | 代码接入，实机 L1–3 | `ev/batch5-20260929` | **不可达**，见 1.4 |

（到达方式的具体入口文件：起始区见 `data/birth/races/*.lua`、`classes/*.lua`；遭遇见 `data/general/encounters/*.lua`；固定世界点见 `data/zones/wilderness/grids.lua`；任务见 `data/quests/*.lua`。）

### 1.3 未覆盖且可达（37 区）

**A. 剧情／可选地城（15）**

| 区域（level_range，层） | 使用的格子 | 到达方式 | 频度 | 复用判断 |
| --- | --- | --- | --- | --- |
| eruan (30–45, 3) | basic／water／forest／lava／sand／mountain（`data/zones/eruan/grids.lua:20-25`）；生成器 `SAND`／`PALMTREE`／`DEEP_OCEAN_WATER`（`eruan/zone.lua:37-42`）；L3 静态图 `data/maps/zones/eruan-last.lua` | 主线 `pre-charred-scar` 任务；其法阵通往已覆盖的 Charred Scar | **B** | 沙地／深海可复用海滩族；`PALMTREE` 需 1 件新图（T5 曾因无候选而拒收，`ev/t5-20260929/README.md`） |
| gorbat-pride (35–60, 3) | basic／forest／sand／water／mountain；竹屋 `FENCE_*` | 兽人部落任务四部落之一 | **C** | 大半可复用；竹屋墙／门为新族 |
| grushnak-pride (35–60, 3) | basic＋`slimy_walls`＋`underground_slimy` | 同上 | **C** | 需新美术 |
| vor-pride (35–60, 3) | basic＋`gothic.lua`＋forest／water／burntland | 同上 | **C** | 需新美术（哥特墙）；焦土可复用 |
| high-peak (55–80, 10) | basic／water／forest／lava／cave；Roomer＋Cavern；静态终层 | 终局，`orb-command` 任务解封 | **E** | 石质＋洞穴族大量复用；传送门／法球原生 |
| shadow-crypt (34–45, 3) | 仅 basic；静态图 `UP`／`OLD_WALL`／`FLOOR` | 远东开局即放的遭遇 | **C/E** | **零新图** |
| slime-tunnels (45–55, 1) | basic／water／`slime.lua` | 经 grushnak-pride | **E** | 需新美术 |
| sludgenest (35–45, 3) | basic／jungle／`slime.lua` | 等级≥30 世界事件 | **E** | 丛林族可复用，黏液部分新 |
| tannen-tower (35–45, 4) | basic／forest／water／lava／mountain；静态图含杠杆门和 `open sky` | east-portal 任务分支 | **E** | 近零新图 |
| valley-moon (35–45, 1) | 图例 `GRASS`／`TREE`／`MOUNTAIN_WALL`／`POISON_DEEP_WATER` | 经 valley-moon-caverns L2 出口 | **E** | 零新图（火山口族） |
| shertul-fortress-caldizar (100, 1) | basic／fortress／void | 堡垒内触发 | **E** | 堡垒族＋虚空族已有 |
| ring-of-blood (10–25, 3) | 图例 `HARDWALL`／`FLOOR`／`SAND`／`LAVA_WALL` | 开局即放的遭遇 | **C** | 近零新图 |
| arena-unlock (5–12, 1) | basic／sand／forest | Derth 对话（等级≤13） | **C** | 近零新图 |
| dreadfell-ambush (20–50, 1) | 图例仅 `GRASS`／`TREE`（`data/maps/zones/dreadfell-ambush.lua`） | Staff of Absorption 任务中**强制**进入 | **B** | **零新图**：一行森林白名单 |
| paradox-plane (7–16, 1) | basic／forest／water／mountain／sand／void | `paradoxology` 任务 | **D** | 复用为主 |

**B. 城镇与世界地图（12）**

| 区域 | 说明 | 频度 |
| --- | --- | --- |
| town-derth (1–15)、town-last-hope (15–35) | 静态图，由 basic／forest／water／mountain 拼成；Derth 图例 `GRASS`／`TREE`／`DEEP_WATER`／`SAND`／`HARDWALL`／`DOOR` 等＋本区 `FIELDS`／`COBBLESTONE`；旧巡检 `ev/map-survey-20260928/survey.json` 记 town-derth L1 可支持身份 2,385 格、棋盘归属 0 | **A** |
| town-zigur／angolwen／gates-of-morning／elvala／irkkk／iron-council／shatur／point-zero／lumberjack-village | 各含 basic＋forest／water／mountain 及个别新族（`jungle_hut`、`snowy_forest`、`elven_forest`、`underground`） | **B/D** |
| wilderness（世界地图） | 95 个本区 `newEntity`，1 格＝1 区域，是另一套图标语言 | **A** |

**C. 模式／教程（4）。** `arena`、`infinite-dungeon`（战役起点，或经 Ruined Dungeon `INFINITE`）、`tutorial`、`tutorial-combat-stats`。频度 **D/E**。

**D. 职业／天赋位面（6）。** `demon-plane-spell`、`dreamscape-talent`、`temporal-reprieve-talent`、`eidolon-plane`（`class/Party.lua:487`）、`stellar-system-shandral`（`data/talents/misc/misc.lua:452-460`）、`dreams`（Noxious Caldera 梦之祭坛）。均 **D/E**，暴露极低。

### 1.4 不可达 / 不采用

| 区域 | 依据 |
| --- | --- |
| orc-breeding-pit（已覆盖但不可达） | 沿用 `AGENTS.md`／`PROGRESS.md` 既有结论；本轮未重新追触发链［推断］ |
| illusory-castle | 全库无任何 `change_zone`／`changeLevel`／遭遇／对话指向；`ev/batch5-20260929/README.md` 已记录［源码］ |
| gladium | 仅 `data/chats/shertul-fortress-gladium-orb.lua` 里有“返回堡垒”选项，没有指向该区的入口［源码］ |
| void | `data/` 与 `class/` 内未找到指向它的入口［源码；DLC 可能另有入口，未检索］ |
| test | 仅 `class/Game.lua` 开发用途 |

---

## 2. 已覆盖区域内仍原生的格子身份

### 2.1 为什么会原生（分类器规则，源码）

分类器全部是“来源戳＋精确 `define_as`＋规则字段＋原生显示层白名单”，未匹配即保持原生：

- **回调字段一律拒收**，除非有“回调不变”戳：`plainCell`（`CT:871-875`）、`inertCell`（`CT:1132-1135`）、gloom（`CT:139`）、burnt（`CT:257`）、void（`CT:344`）、crystal（`CT:428`）、cave（`CT:488`）、underwater（`CT:574`）、`rakshorKind`（`CT:1262-1264`）、石质 `classify`（`CT:1979-1986`）。
- **光环例外只开在四个族**：森林 `terrain()`（`CT:91-100`）、岩 `rockTerrain`（`CT:789-790`）、丛林 `jungleKind`（`CT:1017-1018`）、石质 `classify` 的地板（`CT:1970-1978`）；事件识别 `auraEffects`，`CT:6-22`，共 9 个事件（fell-aura、antimagic-bush、spellblaze-scar、bligthed-soil、protective-aura、font-life、necrotic-air、whistling-vortex、slimey-pool）。石质**墙**的光环圈只对 Conclave Vault 开放（`CT:1973-1978`）。
- **已有的“回调不变”戳模式**：`sameCallback`（文件＋行号，`CT:883-887`）用于毒水（`CT:1048-1062`）、Keepsake 剧情格（`CT:983-1004`）、墓碑（`CT:643-722`）、`UP_VALLEY`（`CT:1345-1357`）。
- 适配器用 `replace_display` 只换显示，规则字段不动。

### 2.2 事件类（表 A）

事件概率来自各区 `data/zones/<z>/events.lua` 与 `data/general/events/groups/*.lua`；重复规则见 `class/GameState.lua:3107-3137`。

| 编号 | 身份／事件 | 出现区域与频度 | 为何原生 | 棋盘化可行性 | Verdict |
| --- | --- | --- | --- | --- | --- |
| E1 | 光环圈**地板／植被**（fell-aura、bligthed-soil、font-life、spellblaze-scar、necrotic-air、whistling-vortex、protective-aura；半径 1–3） | heart-gloom、deep-bellow、ritch、scintillating、ardhungol（100%）、mark-spellblaze、rak-shor（100%×4＋50%）、blighted 等；实机：Heart of Gloom 6 层合计 110 格原生（`ev/heart-gloom-20260928`）、Rak'shor 每层约 16 格骨地板＋墙门共 32–50 格（`ev/rakshor-20260929/survey.json`） | 上述各族分类器拒 `on_stand`；光环把格子改名，`name` 校验失败 | **FEASIBLE**：沿用 `auraEffects` 的事件源文件识别，叠既有 `aura-*` 遮罩，规则字段与 `on_stand` 不动，与森林／岩做法一致 | FEASIBLE |
| E2 | 光环圈内的**墙／门**（石质族、Rak'shor 骨墙／骨门） | 同上；Reknor、Halfling、Blighted、Dreadfell 的 `WALL_*` 原生［“墙来自光环圈”为**推断**，未逐格核对］ | `auraWall` 仅 conclave（`CT:1973-1978`） | **FEASIBLE**：扩 `auraWall` 到各石质区 | FEASIBLE |
| E3 | 光环**中心格**（font-life 陶罐、blight_root、spellblaze scar 的 `LAVA_FLOOR` 克隆） | 每次事件 1 格；`ev/batch4-20260929/README.md` 明确保持原生 | 带道具层，`on_stand` 闭包在事件文件内 | **FEASIBLE**（静态显示）：`on_stand` 用事件源路径固定，叠棋盘地板＋原生道具层 | FEASIBLE |
| E4 | **glowing chest**（`data/general/events/glowing-chest.lua`） | 16 个已覆盖区：sandworm 100%×多次、maze 100%、kryl-feijan 100%、unremarkable 100%、reknor 80%、golem-graveyard 80% 等；实机 Sandworm 每层 2–6 格、Reknor 每层 3 格 | `special=true`＋`block_move` 函数；开箱时就地改 `add_displays[1].image` 并 `updateMap` | 需先解决“原生道具层就地变更”：适配器只装一次 `replace_display`，没有随 `updateMap` 刷新的点。可行方案：显示键并入原生层签名并在 Map 超载中对该格补刷新 | NEEDS-DESIGN |
| E5 | **glimmerstone**（`events/glimmerstone.lua`） | ardhungol、blighted、dreadfell、reknor（100%×多次）、reknor-escape、rhaloren、valley-moon-caverns（150%×多次）；实机 Valley-moon 每层 4–5 格 | 克隆格转 Object，带 `act` 回调 | **FEASIBLE**：显示是静态层；`act` 用定义文件行号戳，不碰回调 | FEASIBLE |
| E6 | **weird pedestals**（`events/weird-pedestals.lua`） | `majeyal-generic` 组 10%，被多个已覆盖区引用 | `block_move`；击杀后 `on_die` 就地改显示层 | 同 E4 | NEEDS-DESIGN |
| E7 | **tombstones／old-battle-field 墓** | 室外 gloomy 组 10%／5%，被 daikara、golem-graveyard、mark-spellblaze、old-forest、tempest-peak 引用 | 同 E4；battlefield 还把墓变成动态区入口 | 同 E4 | NEEDS-DESIGN |
| E8 | **crystaline-forest 晶簇补丁**（`events/crystaline-forest.lua`）：林地圈内换成 `CRYSTAL_FLOOR*`／`CRYSTAL_WALL*` | 仅 Old Forest CRYSTALINE（约 1/3）；`old-forest/events.lua` 中 `percent=200,max_repeat=3` ⇒ 每层数处。**推断**：CRYSTALINE 受支持格 1,983–2,235，比 DEFAULT 的 2,424–2,481 少约 200–500 格（`ev/runtime-v0615/README.md`），量级吻合；README 只写“`CRYSTAL_*` 原生”，未计数 | Old Forest 不在晶洞族门控内（晶洞仅 scintillating，`CT:1605`），`terrain()` 无晶洞分支 | **FEASIBLE**：晶洞族已有（地板、16 向墙掩码，`CT:424-460`）；需“森林优先、晶洞补位”的组合（类似 `lakeSurface`，`CT:1381-1386`）；来源戳见 `Grid.lua:11` | FEASIBLE |
| E9 | **icy-ground** `ICY_FLOOR` 补丁 | daikara DEFAULT 50%、tempest-peak 40%；`ev/daikara-20260928/README.md` 记原生 | 无适配器；`on_stand` 施加打滑效果 | 需新冰面美术并表达危险；“地面装饰不得暗示原生没有的阻挡或加成”（`AGENTS.md`） | NEEDS-DESIGN |
| E10 | **meteor** 熔岩坑、Daikara VOLCANO 的 pyroclast | 室外 generic 组 7%；VOLCANO 每层 100% | `LAVA_FLOOR:clone()` 保留 `on_stand` 灼烧；棋盘熔岩图无害（Daikara 加载时去掉了，`CT:1127-1128`） | 需要表达“会伤人”的熔岩 | NEEDS-DESIGN |
| E11 | 事件入口格：damp-cave、drake-cave、naga-portal、fearscape-portal、rat-lich 等；实机 Valley-moon L1 一格 `fearscape invasion portal` | 各 5–10% | 单格、多回调、通向动态区，本应突出 | 保持原生 | KEEP-NATIVE |
| E12 | **sub-vault 隐藏宝库入口**（`events/sub-vault.lua`） | 已覆盖区仅 rak-shor：每层 100%；每层 1 格 | `change_level_check`／`real_change` 回调；显示为地板＋楼梯图 | **FEASIBLE**：回调用行号固定，显示静态 | FEASIBLE |
| E13 | 动态小区本体（Hidden Vault、damp cave、dragon cave、fearscape 等） | 见 E11／E12 | `zone.short_name` 是每次生成的 `"…-<turn>"` 串，按 `short_name` 白名单门控（`CT:1599`）永不命中 | 需改为按 `zone.name`／前缀门控＋各自族判定 | NEEDS-DESIGN |

### 2.3 地形／出口／门／道具类（表 B）

计数取各批最新 `survey.json`。

| 编号 | 身份 | 出现区域与频度 | 为何原生（源码） | 棋盘化可行性 | Verdict |
| --- | --- | --- | --- | --- | --- |
| T1 | **空气泡** `WATER_FLOOR_BUBBLE` | Murgol 每层 55–78 格（约 2.3–3.2%）、Lake of Nur L2 64／FLOODED L2 63／FLOODED L3 117（`ev/batch4-20260929`、`ev/t5-20260929`） | `on_stand` 消耗充能并换回 `WATER_FLOOR`（`data/general/grids/water.lua:98-116`）；`tests/terrain_contract.lua:945` 锁定原生 | **FEASIBLE**：`on_stand` 行号戳，显示＝水下地板＋气泡层；耗尽后新格走既有 floor 路径 | FEASIBLE |
| T2 | Ardhungol `WORMHOLE` | 三层各 48／31／12 格（1.3–2.2%；`ev/reuse-batch2-20260928`） | `damage_project` 回调＋粒子（`data/zones/ardhungol/grids.lua`），`CT` 刻意排除（`CT:320-323`） | **FEASIBLE**：显示不随伤害变化；回调行号戳，粒子保持原生 | FEASIBLE |
| T3 | Abashed `WORMHOLE` | 每层 0–1 格 | 被稳定后 `change_level=1` 并改名，是任务出口 | 任务关键，应保持醒目 | KEEP-NATIVE |
| T4 | **封印／推石门**：`DOOR_VAULT*`、`ROCK_VAULT`、`BONE_VAULT_DOOR*` | Halfling L2–L4、Scintillating TWISTED L1、Dreadfell、Rhaloren 每层 0–2 格；Vor Armoury L2 2 格；Trollmire L4 宝藏图 1 格；`tests/terrain_contract.lua:42,577` 锁定原生 | `door_player_check` 是**字符串**（`basic.lua:256-273`、`forest.lua:109-125`），被石质 `classify` 一概拒收（`CT:1979-1986`） | **FEASIBLE**：按 `define_as`＋固定字符串＋`door_opened` 白名单，画封印门；无回调 | FEASIBLE |
| T5 | **杠杆与杠杆门**：`GENERIC_LEVER(_DOOR*)`、`BONE_GENERIC_LEVER(_DOOR*)` | Rak'shor L1 杠杆 2＋杠杆门 1；Ruined Dungeon 1 | 杠杆 `block_move` 就地改 `add_mos` 图；门 `on_lever_change` 直接换格（`basic.lua:372-440`） | 状态显示需跟随（同 E4）；谜题线索依赖原生外观 | NEEDS-DESIGN |
| T6 | `LOCK`／`LOCK_HORIZ`／`LOCK_VERT` | Kryl-Feijan L5 1 格；Ruined Dungeon 1 格 | 无回调，只是不在白名单 | **FEASIBLE**：按阻挡门画 | FEASIBLE |
| T7 | `CAVE_DOOR*` | Keepsake L3 2 格、L6 3 格 | 无回调普通门，但洞穴族没有门图 | **FEASIBLE**：石门着洞色 | FEASIBLE |
| T8 | **基础出口 `FLAT_*`** | Halfling L1 2 格、Conclave L1 2 格 | 石质 `stairs` 表只认 `UP`／`DOWN`／`UP_WILDERNESS`（`CT:1801-1806`）；`tests/terrain_contract.lua:42` 锁原生；实体无回调 | **FEASIBLE**：加方向变体，复用既有图 | FEASIBLE |
| T9 | **Old Forest 下楼口 `LAKE_NUR`** | 每次 Old Forest L4 1 格（两布局，`data/zones/old-forest/grids.lua`；`ev/runtime-v0615/README.md`） | 无 `subtype`，`terrain()` 不命中；`tests/terrain_contract.lua:475-479` 锁原生 | **FEASIBLE**：仿 `lakeExit`（`CT:530-538`）写反向精确合同；翻转该测试 | FEASIBLE |
| T10 | `IRON_COUNCIL`、`QUICK_EXIT`（无回调）；`BEACH_UP`、`REL_TUNNEL`（`change_level_check`） | IRON_COUNCIL：deep-bellow L1、reknor-escape L3 各 1；QUICK_EXIT：Maze DEFAULT L2、Elven Ruins L3 各 1；BEACH_UP：South Beach 唯一出口；REL_TUNNEL：Halfling L4 | 前两者只是不在白名单；后两者有任务检查回调 | 前两者直接接；后两者用行号戳也可接，价值低 | FEASIBLE |
| T11 | `RIFT`（Morass／Temporal Rift L1 出口） | 每层 0–1 格 | 带对话回调，剧情出口 | 保持醒目 | KEEP-NATIVE |
| T12 | **Sher'Tul 堡垒道具**：控制／训练／监视球、图书馆、镜子、9 幅壁画、farportal、封门、`TELEPORT_OUT`；纳尔湖 L3 `SHERTUL_FORTRESS_*` 入口 | 堡垒 L1 共 30 格（0.8%，`ev/batch5-20260929`）；纳尔湖 L3 各 1 | `block_move`／`on_move`／`checkSpecialLocation`；入口带任务检查 | 技术上可戳，但属唯一交互物／多格精灵，应保持醒目 | KEEP-NATIVE |
| T13 | **Farportal**（Reknor L4，9 格） | 每次 Reknor L4 | `orb_portal` 表＋3×3 显示＋粒子 | 同 T12 | KEEP-NATIVE |
| T14 | **路牌／碑文**：`IRON_THRONE_EDICT`、`LORE_NOTE`、`LORE1..4`、`CAVEFLOOR_CAVE_MARKER` | 各 1 格 | `on_move` 学习传说，显示为地板＋路牌层 | **FEASIBLE**：行号戳，叠原生路牌层 | FEASIBLE |
| T15 | **无回调祭坛／五芒星**：Graveyard L2 `ALTAR`×5、Kryl-Feijan L5 `PENTAGRAM`×12 | 每次进入该层 | 不在白名单；无回调 | **FEASIBLE**：地板＋原生层，静态 | FEASIBLE |
| T16 | 带回调祭坛：`ALTAR_CORRUPT`（Spellblaze L2 ×4，`on_move`）、Caldera `ALTAR`（`block_move`） | 每层 1–4 格 | 任务／梦境回调 | **FEASIBLE**（行号戳），价值低 | FEASIBLE |
| T17 | `SUMMON_CIRCLE1..3`（Blighted Ruins L3 静态图 24 格） | 仅亡灵起始者 | `does_block_move`＋candle 粒子 | 需“阻挡圆阵”新图＋粒子叠加 | NEEDS-DESIGN |
| T18 | Ruined Dungeon 六色 `PORTAL` 法球＋`INFINITE` | 每次 6＋1 格 | 解谜状态由 `orb_allowed` 驱动，谜题线索来自原生外观 | 保持原生 | KEEP-NATIVE |
| T19 | Vor Armoury L2 伤害 `LAVA_FLOOR*` | 约 48 格；该层原生合计 130 格＝**11.9%**（`ev/batch5-20260929`） | 熔岩保留 `on_stand`（不同于 Daikara／Charred Scar 的无害版） | 需“危险熔岩”图 | NEEDS-DESIGN |
| T20 | 石质区里的 `DEEP_WATER`（Vor L2 约 48 格） | Kor'Pul 系区的密室池 | 棋盘深水图为草岸，不适合石室 | 需石岸深水图 | NEEDS-DESIGN |
| T21 | **带原生边缘层的 `FLOOR`**（`marble_floor` 邻接水／熔岩时 NicerTiles 追加层，`basic.lua:158-165`） | Dreadfell 每层 5–61 格（`ev/runtime-v0617`）、Vor L2 34、Scintillating TWISTED L1 10、Reknor 每层 3、Halfling L1 3 | 签名含 `add_displays`，石质 `floor` 要求 `not g.add_displays`（`CT:1996`）［机制为**推断**：由 NicerTiles 边缘定义与 Vor 的 `kept_reasons` 推得］ | **FEASIBLE**：为 `floor` 增加“仅原生 marble 边缘层”白名单，显示只用棋盘地板 | FEASIBLE |
| T22 | **`HARDMOUNTAIN_WALL`、`CLIFFSIDE`** | Daikara 27 格／8 层；Tempest Peak L2 | `mountain.lua` 变体；`CLIFFSIDE` 挡移动不挡视线 | 硬墙可复用山墙；`CLIFFSIDE` 需新图 | NEEDS-DESIGN |
| T23 | **非石质区里的石质格**：Tempest Peak L1 `DOWN`（唯一下楼口）、L2 `UP`＋`DOOR`×22；Daikara／Old Forest／Scintillating TWISTED 密室里的 `FLOOR`／`HARDWALL*`／`DOOR*` | `ev/reuse-batch-20260928`、`ev/scintillating-20260928` | 这些区不在 `M.variant`（`CT:1919-1953`），`M.combined` 也没有（`CT:2162-2163`） | **FEASIBLE**：登记为石质＋专用族的同层混用（同 rhaloren-camp 做法） | FEASIBLE |
| T24 | Trollmire `STEW`（Prox 房 1 格，`data/rooms/zones/prox.lua:35`；L4 宝藏图 1 格） | 每局 Trollmire L3 约 1 格（**推断**，未实机核数） | `stewProp` 仅认 Keepsake 来源戳（`CT:975-982`） | **FEASIBLE**：给 Trollmire 的 `STEW` 打戳并复用 Keepsake 的 stew 图（无回调） | FEASIBLE |
| T25 | `open sky`（Tempest Peak L1 333 格＝**53%**，Tannen Tower） | `ev/reuse-batch-20260928`；`data/maps/zones/tempest-peak-top.lua` | `quickEntity` 无 `image`，实机渲染为空 | 没有画面可换 | KEEP-NATIVE |
| T26 | 零星剩余：Noxious `JUNGLE_GRASS_PATCH13` 1 格、Unremarkable 特殊地板 1 格、Conclave L4 `FLOOR` 1 格 | 每层 0–1 格 | 个别被事件改写或签名不符 | 价值极低 | KEEP-NATIVE |

（旧稿的 `ROCK_VAULT` 独立条已并入 T4，故 T 系列为 T1–T26。）

**汇总（E1–E13＋T1–T26，共 39 类）：**

| Verdict | 数量 | 编号 |
| --- | ---: | --- |
| FEASIBLE | 20 | E1、E2、E3、E5、E8、E12；T1、T2、T4、T6、T7、T8、T9、T10、T14、T15、T16、T21、T23、T24 |
| NEEDS-DESIGN | 11 | E4、E6、E7、E9、E10、E13；T5、T17、T19、T20、T22 |
| KEEP-NATIVE | 8 | E11；T3、T11、T12、T13、T18、T25、T26 |

### 2.4 待补实测（数据缺口）

1. Trollmire、Old Forest（DEFAULT 与 CRYSTALINE）、Slazish、Kor'Pul、Rhaloren 的 `kept_native` 从未记录；E8 格数只是间接推断。建议先用批次 5 的 `kept_reasons` 格式（`id|name|callbacks|#add_displays`）对这些区各跑一次，成本低于任何套件。
2. Rhaloren OVERGROUND 在 0.6.16 曾有每层 6–20 格 `GRASS_PATCH*` 原生（`ev/runtime-v0616/survey.json`），推测为“光环＋NicerTiles 边缘层”［推断］，需重跑确认。
3. E2 中 Reknor／Halfling／Blighted 的 `WALL_*` 来自光环圈是推断。

---

## 3. 已记录但未修复的视觉限制

| # | 限制 | 证据 | 可能做法与风险 |
| --- | --- | --- | --- |
| V1 | **混沌之沼／时空裂隙 L1 的原生天气方块**（半透明深色矩形） | `ev/void-20260928/README.md`（关闭 `weather_effects` 后同位方块消失）；`data/zones/unhallowed-morass/zone.lua:72-77`、`temporal-rift/zone.lua:121-129` | 属原生粒子，不在棋盘层内。可选：不改；或降低粒子不透明度（触及原生渲染，与“不改原生行为”原则冲突，**高风险**）。Daikara、Old Forest、Lake of Nur、Slazish、Trollmire 等也用 `makeWeather`，是否也出方块**未验证** |
| V2 | **Kor'Pul 石质族墙与地板亮度关系偏离棋盘语言**（应地板亮、阻挡暗） | `ev/batch5-20260929/README.md`：泰尔玛 8.9–15.0%、精灵废墟最高 18.7%、Vor L1 21.1%、育种棚 L1 4.4%；`ev/reuse-batch-20260928/README.md`：半身人 +3.2%、瑞库纳 +9.2%、逃离瑞库纳 +1.1%；`ev/t5-20260929/README.md`：Lake of Nur DEFAULT L3 −8.6%；`PROGRESS.md` 记“卡·普尔石组墙亮 4–21%”。（符号约定各 README 不同，读数以原文为准） | 先例：Conclave 单独门控的 32 张冷灰砖墙（`CT:1733-1752`）。做法：为这些区域再导一套暗墙（exporter 确定性、0 次 ImageGen），单独 manifest 门控。风险：改变已发布观感，需 32 张图＋测试＋逐区复拍；应按区域门控而非全局重导。**S8 已修**（暗墙导出与逐区实测见 `evidence/terrain-s8-20260929/README.md`） |
| V3 | **Tempest Peak L1 过暗**：`color_shown={0.3,0.3,0.3}` | `data/zones/tempest-peak/zone.lua:74-75`；`ev/reuse-batch-20260928/README.md`（地板／墙 32.14／24.40，差 24.1%） | 原生光照乘在棋盘图上。做法：只为该层导更亮的岩图（约 ×3 补偿，明处会过曝）；或接受。风险中，且该层 53% 是 open sky 空洞（T25） |
| V4 | **Noxious Caldera 的暖色调与橙色蒸汽 shader** | `data/zones/noxious-caldera/zone.lua:32-34,97`；`ev/batch4-20260929/README.md`“视觉返工” | 只能在美术侧预补偿（毒水已返工），不改 shader。风险低，已缓解 |
| V5 | **Rak'shor 事件格跳色**：死灵之气／旋风格、隐藏宝库入口、杠杆显示为原生橙黄沙／骨堆 | `ev/rakshor-20260929/README.md` 末段“限制” | 即 E1／E12／T5；E1、E12 可修，杠杆需设计 |
| V6 | **Sher'Tul 外围 `OLD_WALL` 苔墙风格不同；原生粒子暗斑** | `ev/batch5-20260929/README.md`“审图结论与限制” | 外围苔墙是原游戏古遗迹通道，接受；暗斑属原生粒子，与 V1 同类 |
| V7 | **恶魔空间墙比熔岩地亮 38.6%**（与棋盘语言相反） | `ev/batch5-20260929/README.md` | 如要修需为该区单独重导暗墙，与 V2 同一做法。**S8 已修**（暗墙导出与逐区实测见 `evidence/terrain-s8-20260929/README.md`） |
| V8 | **Vor Armoury L2 伤害熔岩／深水／描边地板保持原生岸带**（11.9%） | `ev/batch5-20260929/README.md` | 即 T19／T20／T21，需危险熔岩与石岸深水图 |
| V9 | **Scintillating 每帧 `setShown` 调色作用于棋盘像素** | `data/zones/scintillating-caves/zone.lua`；`ev/scintillating-20260928/README.md` | 已验证为预期（与原生一致），无需修 |
| V10 | **Deep Bellow 孢子雾、Heart of Gloom 全屏 gloom 粒子** | `data/zones/deep-bellow/zone.lua:86`、`heart-gloom/zone.lua` | 原生粒子；已验证在棋盘上可读，无需修 |

---

## 4. 优先级计划

### 4.1 权重依据

- 光环事件：约 34 个已覆盖区带至少一种光环事件，概率 20–100%/层，且 E1 涉及的族此前都未支持光环。
- Old Forest 是 tier2 中最常走完 4 层并由 L4 出口进入 Lake of Nur 的区域；CRYSTALINE 约占 1/3。
- 出口是每一层都必经的可见格。
- 已覆盖区里 kept-native 总占比多在 0.1–3%（Vor Armoury L2 11.9%、Tempest Peak 是例外，见 T19／T23），补漏类套件单看格数不大，价值在于这些格子是玩家注意力最集中的位置（出口、事件、门、宝箱）。

### 4.2 套件（每个应在一个代理一轮内完成）

| 序 | 套件 | 内容 | 规模／美术 | 风险 | 验收要点 |
| ---: | --- | --- | --- | --- | --- |
| **S1** | **光环全族补齐** | E1（gloom／沙／晶／洞／焦土／骨／水下／虚空／堡垒分类器接受 `auraEffects` 事件）与 E2（石质光环墙／门，`CT:1973-1978`）；E3 中心格如时间允许并入。零新图（复用 `aura-*` 遮罩） | 分类器 8–10 处小改＋测试；无导出器 | 中：放宽 `name`／`on_stand` 校验时须保持“源文件路径＋其余字段全等”，不得吞掉真正带回调的格 | 先对 heart-gloom、deep-bellow、ritch、scintillating、ardhungol、mark-spellblaze、rak-shor、blighted、Reknor/Halfling/Dreadfell 取 `kept_reasons` 基线；改后光环格与墙全部走棋盘且 `on_stand` 引用不变 |
| **S2** | **出口／无回调门／静态道具** | T8、T9（翻转 `terrain_contract.lua:475-479`）、T10、T4、T6、T7、T15、T14、T21、T24 | 复用现有 stairs／door／floor 图；至多为洞门与封印门着色导出（0 次 ImageGen） | 低：无回调或已有戳模式；每类须加“改一项字段即拒收”的负例 | 每个 id 至少实机取到一次；出口目标不变；Old Forest 两布局 L4 |
| **S3** | **Old Forest 晶簇＋外围石质密室** | E8（森林优先、晶洞补位，仿 `lakeSurface`，`CT:1381-1386`）；T23（把 old-forest、daikara、tempest-peak、scintillating-caves 登记为石质混用，`CT:1919-1953,2162-2163`） | 0 新图；运行时中等 | 中：`terrainImage` 族分支互斥（`CT:1381-1396`），要引入“主族＋补位族”；石质墙偏亮（V2）会随之扩到这些区 | 先量 CRYSTALINE 各层晶格数；CRYSTALINE 与 DEFAULT 各 L1–L4；Tempest L1 下楼口与 L2 22 扇门 |
| S4 | **空气泡** | T1：`water.lua:106` 行号戳，显示＝水下地板＋气泡层 | 1 件气泡叠层（可由已有水下母版导出） | 低；`terrain_contract.lua:945` 需改为“行号一致才接受” | Lake of Nur L2/L3 与 Murgol 各一层；充能消耗前后棋盘更新 |
| S5 | **零美术新增区域** | dreadfell-ambush（加入 `FOREST_ZONES`）、shadow-crypt、tannen-tower、valley-moon、ring-of-blood、arena-unlock | 6 区约 14 层；0 新图 | 低：仅门控与逐层普查；杠杆／传送门保持原生 | 每区一次冷启动；Dreadfell 主线必经 |
| S6 | **远东沙漠：Eruan＋Gorbat Pride** | 海滩沙／深海族＋`PALMTREE` 1 件新图；Gorbat 石质／沙／岩山墙复用，竹屋墙／门与杠杆原生 | 1 件新母版＋门控 | 中：Gorbat 的 MapScript 混合多族 | Eruan 经 Charred Scar 与已覆盖区相连，需一起看 |
| S7 | **城镇 Derth＋Last Hope**（**需用户先定范围**） | 全部由已有族拼成，近零新图；需处理 `FIELDS`／`COBBLESTONE`／商店陷阱层的显示 | 中 | 中：持久城镇与商店显示交互；棋盘语言是否覆盖城镇属产品决定 | 曝光量最大，但不属“地城全覆盖” |
| S8 | **Kor'Pul 暗墙重着色**（V2、V7） | 为 Halfling／Reknor／Telmur／Elven／Vor L1／Lake of Nur L3／Demon Plane 单独导一套暗墙，仿 Conclave | 32 张图＋manifest＋测试 | 中：改变既有观感，须逐区复拍 | 地板／墙亮度关系回到棋盘语言 |
| S9 | **High Peak** | 石质＋洞穴族＋静态终层；`HARDCAVEWALL`／传送门／`ORB_*` 原生 | 10 层，0–1 新图 | 中：终局多特殊格 | 晚期，曝光低 |
| S10 | **部落 Grushnak／Vor＋Slime Tunnels／Sludgenest** | 需黏液族、哥特族新美术 | 各 2–4 件母版 | 高：新美术＋多族 | 最后 |

**推荐前三**：S1 → S3 → S2；S4、S5 可作为并行小套件；S6 优先于 S9／S10（位于主线链 `pre-charred-scar`）。S7 需先由用户确认范围。另建议在 S1／S3 开工前先做 2.4 的实测普查。

---

## 5. 不确定项

1. E2 的“墙来自光环圈”和 E8 的“晶簇格数”均为推断，尚无按格 `kept_reasons`。
2. `orc-breeding-pit` 的不可达依据沿用既有记录，本轮未再追触发链。
3. `void`、`gladium` 视为不可达仅基于工作区内 base game 源码；DLC／其他 addon 可能另有入口。
4. 频度档位 A–E 是按入口类型的定性分档，没有游戏内遥测。
5. 事件概率是每层独立抽取的名义值，未实机统计。
6. 本文行号取自调研时的源码，之后若源文件变动可能偏移。
