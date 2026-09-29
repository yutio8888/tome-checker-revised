# 城镇与世界地图棋盘地形重绘调研（只读，2026-09-29）

范围：为“城镇重绘（用户已决定要做）”与“世界地图（仅在工作量小时才做）”给出可执行的分型、套件计划与风险。只读静态调研：未启动游戏（夹具在用）、未生图、未改任何其他文件、未提交。

标记约定：**[已验证]** = 直接读到源码或用脚本实际跑原生地图文件得到；**[推断]** = 由代码阅读推得，尚未实机确认。

路径缩写：`NT` = `game/modules/tome/data`；`CT` = `game/addons/tome-checker-revised/overload/mod/class/CheckerTerrain.lua`；`GRID` = `game/addons/tome-checker-revised/superload/mod/class/Grid.lua`；`MAP` = `game/addons/tome-checker-revised/superload/engine/Map.lua`。

格数统计方法 [已验证]：用 Lua 存根加载各 `NT/maps/towns/*.lua`（`defineTile`/`quickEntity` 打桩）并统计 ASCII 图；Angolwen 是 TMX，用 Python 解 base64+zlib 图层；世界图同法加载 `NT/maps/wilderness/eyal.lua`。统计的是**地图符号所指的基础身份**，`nice_tiler` 的随机变体（`TREE1..30`、`GRASS_PATCH1..14`、`HARDWALL_NORTH*` 等）在关卡生成后才产生，未逐个实例化。

---

## 0. 结论摘要

1. **11 座城镇全部是静态地图，无生成器、无层数变体**：每区 `max_level=1`、`engine.generator.map.Static`。原生没有“被入侵／烧毁的 Derth”，也没有 Last Hope 内部墓地入口——墓地是世界图上的独立入口 `LAST_HOPE_GRAVEYARD`（`NT/maps/wilderness/eyal.lua:179` 的 spot、`NT/zones/wilderness/grids.lua:733` 的同名实体），那个区已由棋子仓库覆盖 [已验证]。
2. **除城镇外，所有城镇的“商店”都是叠在地形格上的陷阱层，不是地形**：`defineTile('2',"HARDWALL",nil,nil,"SWORD_WEAPON_STORE")` 第 5 参数是 trap（`NT/maps/towns/derth.lua:36`），`BASE_STORE` 陷阱 `z=18`、`image=store/shop_door.png`（64×64，实测 67% 像素全透明，只画门板；`NT/general/traps/store.lua`、`NT/resolvers.lua:529-556`）。所以**商店回调、`block_move`、商店界面完全不属于地形适配器**，换底下的 HARDWALL 贴图不会碰它 [已验证]。
3. **Derth 只用到 6 种基础身份（TREE、GRASS、DEEP_WATER、GRASS_ROAD_STONE、HARDWALL、GRASS_UP_WILDERNESS）＋9 个商店陷阱**——`FIELDS`、`COBBLESTONE`、`ROCK`、`LAVA`、`SAND`、`DOOR` 等虽在图例里定义，但 ASCII 图里 0 格 [已验证：`NT/maps/towns/derth.lua:20-34` 定义，统计结果无这些符号]。这些身份全部已有棋盘族：零新图即可覆盖 Derth。
4. **最大架构风险（[推断]，但由代码明确支持）**：石质族（`classify`＋逐格 `observe`）只对“当前视野内”的格建记录，`M.render` 无记录就返回 nil＝原生（`CT:2353-2372`、`CT:2396-2436`、`MAP:6-15`）。城镇几乎都设 `all_remembered=true`（游戏开局整图已记忆但从未被“看见”），所以直接把城镇登记进石质族，会出现“视野外原生、走近才变棋盘”的半新半旧观感。森林族（`applyForest`）一次性对全部格装 `replace_display`，不受此限（`CT:1779-1908`）。因此要先做一个“城镇急切安装”小工程（见 TW1）。
5. **世界地图结论：LARGE**（详见 Part B）。

---

## Part A — 城镇

### A.1 现有机制速览（决定“复用”边界）

| 机制 | 事实 | 出处 |
| --- | --- | --- |
| 区域门控 | 森林族靠 `FOREST_ZONES` 白名单；石质族靠 `M.variant(zone)` 返回非 nil，混合区再登记 `M.combined`；出口／商店等回调格不在门控里，靠身份合同拒绝。 | `CT:1774-1775`、`CT:2131-2176`、`CT:2450-2452` [已验证] |
| 来源印记 | `Grid:loadList` 只对白名单文件的定义调用 `markSource`；基本 `basic.lua`、`forest.lua`、`water.lua`、`jungle.lua`、`sand.lua`、`void.lua`、`burntland.lua` 等已在名单，`mountain.lua`、`snowy_forest.lua`、`elven_forest.lua`、`jungle_hut.lua`、各 `town-*/grids.lua` **不在**。 | `GRID:4-28` [已验证] |
| 森林族识别 | `terrain()` **按运行时字段**判（subtype `grass` 的 wall＋`name=='tree'`→tree；`name=='deep water'`→deep；floor 且 `define_as` 是 GRASS/GRASS_SHORT/GRASS_PATCHn/FLOWERn/GRASS_ROAD_*），不查来源文件。`ELVEN_TREE`（subtype grass, name tree）因此天然命中；`DEEP_OCEAN_WATER`（继承 `WATER_BASE` 的名字 `deep water`）也命中。 | `CT:199-241`；`NT/general/grids/elven_forest.lua:31-46`；`NT/general/grids/water.lua:146-150` [已验证] |
| 石质族身份 | 必须来自 `basic.lua`，白名单：FLOOR、OLD_FLOOR→floor；HARDWALL 全族→hardwall；WALL 全族→wall；OLD_WALL 全族→old-wall；DOOR 系→door；UP/DOWN/UP_WILDERNESS→stairs。`define_as` 与签名、名字、回调、`add_mos` 等全字段精确比对。 | `CT:1981-2003`、`CT:2214-2303` [已验证] |
| 混合区先例 | Rhaloren 营地 OVERGROUND 是 `Town` 生成器，同一层里草地／树走森林族、建筑石头走石质族（`FOREST_ZONES`＋`variant`＝'RHALOREN'）。 | `CT:1774`、`CT:2137`；`PROGRESS.md:252` [已验证] |
| 墙掩码 | 石质族按四邻“墙类记录”算掩码，出 `refined/korpul/hardwall-<mask>-<parity>`（32 张）；`wall`、门各 32 张，`floor-a/b` 各 2 张。 | `CT:2375-2392`；`data/gfx/refined/korpul` 目录实测 [已验证] |
| 草边墙脚 | `DungeonWallsGrass` 叠层（Derth／Elvala／Gates／Zigur 设了 `nicer_tiler_overlay`）已有精确“去草边再判”处理，Old Forest／Trollmire 用过。 | `CT:2178-2212`；`NT/zones/town-derth/zone.lua:38` [已验证] |
| 道具叠层保留 | E3 中心格：底面画棋盘地板，保留原生道具层（只保留 `image`＋`z`）。 | `CT:1858-1874` [已验证]；限制：不保留 `add_displays` 里的展示回调／粒子（见 B） |
| 生图复用规则 | 邻接掩码／棋盘明暗／尺寸复用现有 C 导出，ImageGen 不产 196 格图集；新族至少两维可分。 | `art/production/README.md:173`、`:170` [已验证] |

### A.2 城镇总表（可达性、布局、规模）

“规模”为 ASCII 图统计。所有静态图实际都是 **50×50**（`zone.lua` 里 `width=196,height=80` 是被 Static 生成器忽略的残值 [已验证图尺寸；忽略行为为推断]）。

| 城镇 | zone | 图文件 | 尺寸 | 到达方式 | DLC/不可达？ | 关键 zone 标志 |
| --- | --- | --- | --- | --- | --- | --- |
| Derth | `town-derth` | `maps/towns/derth.lua` | 50×50 | 世界图 `TOWN_DERTH`；`arena-unlock` 结尾也会送回（`NT/chats/arena-unlock.lua:131`） | 基础游戏 | `all_remembered`、`all_lited`、`day_night`、`DungeonWallsGrass`、老鹰前景粒子（`zone.lua:30-38`、`zone.lua:75-97`） |
| Last Hope | `town-last-hope` | `last-hope.lua` | 50×50 | 世界图；`east-portal` 任务（`NT/quests/east-portal.lua:163`） | 基础 | `all_remembered`、`all_lited`、`day_night`（`zone.lua:30-32`） |
| Zigur | `town-zigur` | `zigur.lua` | 50×50 | 世界图（魔法使用者会被 `change_level_check` 拦；`NT/zones/wilderness/grids.lua` 的 `TOWN_ZIGUR`）；`anti-antimagic` 任务 | 基础 | `no_worldport`、`DungeonWallsGrass`、`setStatusAll{no_teleport=true}`（`zigur.lua:20`） |
| Shatur | `town-shatur` | `shatur.lua` | 50×50 | 世界图 | 基础 | `all_remembered`、`day_night` |
| Elvala | `town-elvala` | `elvala.lua` | 50×50 | 世界图 | 基础 | 同上＋`DungeonWallsGrass` |
| Angolwen | `town-angolwen` | `angolwen.tmx` | 50×50（有效城区约 526 格） | 法师开局（`data/birth/classes/mage.lua:218`）／传送天赋（`NT/timed_effects/magical.lua:1210`）／世界图（只有会传送的角色才显示实体，否则显示 `^`：`eyal.lua:82`） | 基础，条件可见 | **`all_remembered` 被注释掉**（`zone.lua:30`）；`on_enter` 里改“回世界图”出口（`zone.lua:61-64`） |
| Gates of Morning | `town-gates-of-morning` | `gates-of-morning.lua` | 50×50 | 世界图；`celestial` 职业开局（`data/birth/classes/celestial.lua:43`）；Slazish 沼泽尾端 | 基础 | `DungeonWallsGrass`；日光族角色 `post_process` 里动态加 `FENS` 入口并重置玩家位置（`zone.lua:56-90`） |
| Lumberjack village | `town-lumberjack-village` | `lumberjack-village.lua` | **25×25** | 仅任务 `lumberjack-cursed` 生成入口（`NT/quests/lumberjack-cursed.lua:38`） | 基础，任务专用 | **无 `all_remembered`**；入场弹窗尖叫（`zone.lua:50-55`） |
| Iron Council | `town-iron-council` | `iron-council.lua` | 50×50 | 世界图 `TOWN_IRON_COUNCIL`（仅矮人 `can_see_iron_council`，否则显示 `#`）；Deep Bellow／Reknor-escape 的出口（`NT/zones/deep-bellow/grids.lua:23`） | 基础，条件可见 | `all_remembered`；**没有 `day_night`**（`zone.lua:30-31`） |
| Irkkk | `town-irkkk` | `irkkk.lua` | 50×50 | 世界图；yeek 开局（`data/birth/races/yeek.lua:47`） | 基础 | 鸟类前景粒子 |
| Point Zero | `town-point-zero` | `point-zero.lua` | 50×50 | 编年师开局（`data/birth/classes/chronomancer.lua:47`）／时间效果（`magical.lua:1254`）／Unhallowed Morass 出口（`NT/zones/unhallowed-morass/grids.lua:43`） | 基础 | 星空 shader／雪粒子、`color_shown` 紫调、7 条“时间光束”高速通道（`zone.lua:59-154`、`point-zero.lua:129-135`） |

- **没有 DLC 城镇** [已验证：11 个目录都在基础模块 `NT/zones/`，`data/birth` 中的 `starting_zone` 只引用了 Irkkk／Gates／Point Zero／Angolwen]。Elvala、Shatur 没有开局引用，只能从世界图进（`playerpop` spot 在世界图上，`eyal.lua:172-178`）。
- 无关卡变体：`zone.lua` 里没有 `alternateZone`／`is_*` 标志（各城 `zone.lua` 全读过，仅 Derth 的 `arena` 引导员为额外 NPC）。

### A.3 各城格身份清单、分型与约束

分型缩写：**R** = FEASIBLE-REUSE（现有族原样复用，只需门控／身份合同）；**N** = NEEDS-NEW-ART；**K** = KEEP-NATIVE。
“新图”按文件数估计；掩码族按现有导出惯例 32 张＝16 掩码×2 奇偶（`refined/korpul` 实测），地板／树 2 张＝奇偶各 1（[已验证的惯例]，具体数量为 [推断]）。

#### A.3.1 Derth（`derth.lua`，7 栋建筑）

| 格组 | 格数 | 身份 | 分型 | 说明 |
| --- | ---: | --- | --- | --- |
| 树 | 1,399 | `TREE`（→`TREE1..30`） | **R** | 森林族 `tree`；整城 56% 是树海，看棋盘观感需实机。`forest.lua:62-77` |
| 草 | 496 | `GRASS`（→`GRASS_PATCHn`） | **R** | `forest.lua:24-32` |
| 深水 | 353 | `DEEP_WATER` | **R** | 深水掩码 32 张已有；`water.lua:136-140` |
| 石板路 | 137 | `GRASS_ROAD_STONE` | **R** | 森林族 `road`（`CT:1103-1108`／`terrain()`） |
| 建筑墙 | 105（含 9 个商店门格） | `HARDWALL`（→`HARDWALL_NORTH*`/`_SOUTH*` 等） | **R**（石质族 `hardwall`） | 7 栋，最大 24 格；四邻掩码可用。**需先做“急切安装”**（A.1 第 4 点）。观感风险见 A.5-5。 |
| 商店门格 | 9 | `HARDWALL`＋trap（剑／匕首／弓／重甲／轻甲／草药／珠宝／工具店＋炼金师） | **K**（陷阱层不动）＋底 HARDWALL 走 R | 炼金师（Stire）是 `chatfeature` 上锁门，`image=shop_door_barred.png`（`traps.lua:66-72`），也是陷阱层。 |
| 出口 | 1 | `GRASS_UP_WILDERNESS` | **R** | `exit`；`CT:1121-1135` 合同 |
| 未用图例 | 0 | `FIELDS`、`COBBLESTONE`、`SAND`、`ROCK`、`LAVA`、`OLD_FLOOR`、`FLOOR`、`POST`、`DOOR` | — | 只是图例，图里没有。 |

约束：`arena` 引导员按 spot 动态生成（`zone.lua:61-72`）、老鹰是 `foreground` 粒子（`zone.lua:75-97`），都与地形无关 [已验证]。无 NPC 触发格、无任务触发格。
新图：**0**。

#### A.3.2 Last Hope（`last-hope.lua`，14 块建筑／城墙）

| 格组 | 格数 | 身份 | 分型 | 说明 |
| --- | ---: | --- | --- | --- |
| 树 | 673 | `TREE` | R | |
| 广场地砖 | 662 | `FLOOR`（空格符号） | R | 石质族 `floor`（Kor'Pul 地砖 a/b）。 |
| 深水 | 498 | `DEEP_WATER` | R | |
| 建筑／城墙 | 421（含 16 个商店格；最大连通块 167 格） | `HARDWALL` | R | 最大连通块是城堡＋城墙。 |
| 石路（城内） | 118 | `FLOOR_ROAD_STONE`（区域本地：`type floor/subtype floor`，`image marble_floor`，`nice_editer2 roads_def oldstone`） | **N（小）** | 不在石质白名单，也不是 grass 子类型；森林 `road` 图是草底道路。建议新增 2 张“地砖上的路”或用 `floor` 图＋道路图案。`town-last-hope/grids.lua:25-33` |
| 石路（草上） | 61 | `GRASS_ROAD_STONE` | R | |
| 山墙 | 38 | `HARDMOUNTAIN_WALL`（区域外来自 `mountain.lua`） | R（新身份分类，图复用 Daikara `mountain-wall`） | 现有 Daikara 分类只认 `MOUNTAIN_WALL`（`can_pass.pass_wall`，`CT:942-984`）；`HARDMOUNTAIN_WALL` 无 `can_pass`、多 `block_sense/esp`（`mountain.lua:88-101`）。要为它加独立身份合同。 |
| 草 | 7 | `GRASS` | R | |
| 雕像／纪念碑 | 5 | `quickEntity` 的 `@`/`Z`/`Y`/`X`：草底＋`add_displays` 大雕像（`display_h=2,display_y=-1,z=18`）＋`block_move` 触发 `learnLore` | **K**（叠层保留）＋草底走 R | 回调与叠层不变；底面换棋盘草。要用“来源文件＋行号”核对回调（`CT:1044-1047` `sameCallback` 惯例）。`last-hope.lua:20-23` |
| 商店／NPC 门 | 16 | 剑、斧、匕首、锤、重甲、轻甲、布甲、草药、符文、弓、图书馆、长老（ELDER）、Tannen、炼金术士、稀有商品、Melinda 之父 | K（陷阱层） | 全在 HARDWALL 格上；`ELDER`/`TANNEN`/`MELINDA_FATHER` 是聊天／任务入口。 |
| 出口 | 1 | `GRASS_UP_WILDERNESS` | R | |
| 动态格 | 0 静态 | `FAR_EAST_PORTAL`／`CFAR_EAST_PORTAL`（任务放置，带 `farportal-base` 3×3 叠层＋粒子＋`orb_portal`） | K | 由 `east-portal` 任务在 spot 上放（`addSpot` 在 `last-hope.lua:61-64`）；叠层与粒子保持原生。 |

新图：**0–2**（“地砖上的路”）。

#### A.3.3 Elvala（`elvala.lua`）

| 格组 | 格数 | 身份 | 分型 |
| --- | ---: | --- | --- |
| 深水 | 952 | `DEEP_WATER` | R |
| 草 | 696 | `GRASS` | R |
| 石板广场 | 415 | `OLD_FLOOR`（`_` 符号） | R（石质白名单已含 OLD_FLOOR→floor） |
| 建筑墙 | 306（含 7 商店格） | `HARDWALL` | R（连通块 113、108、29、29、17、17） |
| 树 | 123 | `TREE` | R |
| 商店 | 7 | 布甲、轻甲、法杖、剑、符文师、图书馆、炼金 | K |
| 出口 | 1 | `GRASS_UP_WILDERNESS` | R |

新图：**0**。

#### A.3.4 Shatur（`shatur.lua`；无 HARDWALL 建筑）

| 格组 | 格数 | 身份 | 分型 | 说明 |
| --- | ---: | --- | --- | --- |
| 绿林树 | 1,073 | `ELVEN_TREE` | R | 森林族松散判定命中（subtype grass, name tree） |
| 雪林树 | 930 | `SNOW_ELVEN_TREE`（subtype `snowy_grass`） | R（新分类）／或 N | 复用 Daikara 雪族 `tree-pine/elm`（`refined/snow` 12 张）需新身份合同；与绿林并置观感待看。`elven_forest.lua:74-90` |
| 深水 | 240 | `DEEP_WATER` | R | |
| 草 | 135 | `GRASS` | R | |
| 雪草 | 103 | `SNOWY_GRASS`（subtype `snowy_grass`） | R（新分类，复用 `snow-ground`） | `snowy_forest.lua:22-31`；`rockTerrain(false)` 已认 `snowy_grass.png` 的 `ROCKY_GROUND` |
| 石子路 | 10 | `COBBLESTONE`（区域本地 FLOOR 基） | N（小） | 沿用地砖 `floor` 图即可，不新增（合同新增）。`town-shatur/grids.lua:31-36` |
| 商店格 | 7 | 剑、锤、弓在 `ROCKY_GROUND`（其 `image` 被改为 `snowy_grass.png`，`grids.lua:20-25`）；重甲、轻甲、草药、心灵石在 `GRASS` | K（陷阱）＋底走 R | 无建筑墙，商店门直接叠在草／雪地上。 |
| 雕像 | 1 | `quickEntity '@'`：苔藓雕像，`block_move` 触发 `learnLore("thaloren-lament")` | K 叠层＋底 R | `shatur.lua:28` |
| 出口 | 1 | `GRASS_UP_WILDERNESS` | R | |

新图：**0–2**。

#### A.3.5 Zigur（`zigur.lua`）

| 格组 | 格数 | 身份 | 分型 | 说明 |
| --- | ---: | --- | --- | --- |
| 草 | 902 | `GRASS` | R | |
| 深洋水 | 610 | `DEEP_OCEAN_WATER` | R | 名字仍是 `deep water` |
| 树 | 459 | `TREE` | R | |
| 沙 | 133 | `SAND` | R | 复用 `refined/beach/sand`；需为该区放开 `surfaceSandKind` 门控（`CT:782-800`）[推断] |
| 旧石地 | 108 | `OLD_FLOOR` | R | |
| 建筑墙 | 106（含 11 商店格） | `HARDWALL` | R | |
| 耕地 | 58 | `FIELDS`（区域本地，`base=GRASS`，`add_mos cultivation01-04`） | **N** | `terrain()` 的草地分支只认 GRASS／FLOWER／ROAD／PATCH 的 `define_as`，`FIELDS` 会返回 nil 保持原生。需 2 种作物地图（4 张含奇偶）。规则与草完全相同。`town-zigur/grids.lua:45-50` |
| 熔岩坑 | 52 | `LAVA`（区域本地：`does_block_move=true`，**无伤害**，`lava_floor.png`） | R（新身份，复用 burnt/scorch 熔岩掩码） | 阻挡但无伤害；棋盘图需让人读成“不可通行”，与既有熔岩图语义一致。`grids.lua:38-44` |
| 地砖 | 17 | `FLOOR` | R | |
| 巨石 | 5 | `ROCK`（`base=HARDWALL`，`huge_rock.png` z=2） | K 或 N | 数量小，保持原生即可。`grids.lua:58-63` |
| 门 | 1 | `DOOR` | R（石质门） | |
| 路牌 | 1 | `POST`：草底＋`signpost.png`＋`on_move` 触发 `learnLore` | K 叠层＋底 R | 需 `sameCallback`。`grids.lua:26-36` |
| 石板路 | 35 | `GRASS_ROAD_STONE` | R | |
| 商店 | 11 | 训练师、剑、斧、锤、匕首、轻／重甲、草药、图书馆、弓、心灵石 | K | |
| Protector Myssil | 1 | 地砖＋NPC | 无地形改动 | |
| 出口 | 1 | `GRASS_UP_WILDERNESS` | R | |
| 未用 | 0 | `CLOSED_GATE`／`OPEN_GATE` | K | 图里 0 格，只有任务可能替换用（`anti-antimagic` 未逐行核对，[推断]）。 |

新图：**2–4**（耕地）。

#### A.3.6 Gates of Morning（`gates-of-morning.lua`）

| 格组 | 格数 | 身份 | 分型 | 说明 |
| --- | ---: | --- | --- | --- |
| 地砖 | 817 | `FLOOR` | R | |
| **金山墙** | **784** | `GOLDEN_MOUNTAIN`（区域本地：wall/`rockwall`，`block_sense/esp`，`golden_mountain5_n.png`） | **N（最大新图项）** | 占全城 31%，是 Sunwall 身份。可复用 Daikara `mountain-wall` 掩码，但会丢“金色”识别；建议出一套金色掩码（32 张）。`town-gates-of-morning/grids.lua:69-83` |
| 草 | 310 | `GRASS`（空格符号） | R | |
| 石路 | 165 | `FLOOR_ROAD_STONE`（区域本地） | N（小） | 同 Last Hope，可共用那 2 张。`grids.lua:27-35` |
| 沙 | 138 | `SAND` | R | |
| 建筑墙 | 113（含 12 商店） | `HARDWALL` | R | |
| 深洋水／深水 | 60／46 | `DEEP_OCEAN_WATER`／`DEEP_WATER` | R | |
| 树／棕榈 | 42／9 | `TREE`／`PALMTREE`（`sand.lua:115-128`） | R／N（1 件） | 棕榈树与 S6（Eruan）计划的 `PALMTREE` 新图相同，可共用（`TERRAIN-GAP-20260929.md` S6 行）。 |
| NPC | 3 | `@`（Aeryn，草底）、`j`、`s` | 无地形改动 | 日光族角色进入会改写位置（`zone.lua:56-90`） |
| 动态格 | 运行时 | `FENS`（洞穴入口，`z=8`，`change_zone`）、`WEST_PORTAL`/`CWEST_PORTAL`（远传门＋粒子） | K | `FENS` 由 `post_process` 用 `makeEntityByName` 加入并 `nicer_tiles:updateAround`（`zone.lua:76-89`）。 |
| 出口 | 1 | `GRASS_UP_WILDERNESS` | R | |

新图：**36–40**（金山墙 32＋路 2＋棕榈 2）。

#### A.3.7 Lumberjack village（`lumberjack-village.lua`，25×25）

| 格组 | 格数 | 身份 | 分型 |
| --- | ---: | --- | --- |
| 树 | 298 | `TREE` | R |
| 草 | 226 | `GRASS` | R |
| 墙 | 52 | `WALL`（可挖，非 HARDWALL） | R（石质 `wall`） |
| 地板 | 41 | `FLOOR` | R |
| 门 | 6 | `DOOR` | R（门 32×2 图已有） |
| Ben Cruthdar | 1 | 草底＋NPC | — |
| 出口 | 1 | `GRASS_UP_WILDERNESS` | R |

100% 命中现有身份；`defineTile` 的 `def={lite=true}` 是状态而非身份。无 `all_remembered`，石质族逐格观察语义可直接用。新图：**0**。最小的一座，适合当基础设施的冒烟区。

#### A.3.8 Iron Council（`iron-council.lua`）

| 格组 | 格数 | 身份 | 分型 | 说明 |
| --- | ---: | --- | --- | --- |
| 旧石地 | 1,441 | `OLD_FLOOR` | R | |
| 墙 | 1,015（含 9 商店；一块 904 格＝外壳，另 8 栋各 15 格） | `HARDWALL` | R | |
| 晶簇墙 | 24 | `CRYSTAL_WALL`（区域本地，subtype `underground`，`image oldstone_floor.png`＋`makeCrystals`，`dig=CRYSTAL_FLOOR`） | R（新身份，复用 `refined/crystal/wall`） | 现有 crystalTerrain 认的是 `crystal.lua` 的定义，这是另一份同名；需独立合同。`town-iron-council/grids.lua:23-36` |
| 雕像 | 9 | `STATUE1..6`：旧石地＋`add_displays` 大雕像＋`does_block_move`/`block_sight`，**无回调** | K 叠层＋底 R（走 E3 道具叠层路径） | `grids.lua:42-` |
| 商店 | 9 | 重甲、轻甲、布甲、斧、锤、剑、符文、宝石、工具 | K | |
| 出口 | 3 | `UP_WILDERNESS`（`<`）、`ESCAPE_REKNOR`、`DEEP_BELLOW`（均 `base=DOWN`，带 `change_zone`） | R（新出口变体） | 现有 stairs 合同要求 `change_zone` 为空（`CT:1999-2003`）；`DEEP_BELLOW` 另有 `glow=true`。 |

新图：**0–2**（出口变体沿用现有 stairs 图）。

#### A.3.9 Irkkk（`irkkk.lua`）

| 格组 | 格数 | 身份 | 分型 | 说明 |
| --- | ---: | --- | --- | --- |
| 丛林草 | 1,590 | `JUNGLE_GRASS` | R | `jungleKind`（`CT:1175-1207`）、Caldera 已有 `refined/caldera/floor` |
| 丛林树 | 367 | `JUNGLE_TREE` | R | Caldera `tree-a/b/c` |
| 深水 | 271 | `DEEP_WATER` | R | 深水掩码原为草岸；接丛林草岸的观感需看 [推断] |
| 竹屋墙 | 139 | `BAMBOO_HUT_WALL`（`bamboo hut` subtype，`singleWall` 掩码 12 种变体，多层 `add_displays`） | **N** | `jungle_hut.lua:35-80`。Gorbat Pride（S6 备注“竹屋墙／门保持原生”）也用这批，做一次两处受益。 |
| 竹屋地 | 119 | `BAMBOO_HUT_FLOOR` | N | 2 张 |
| 竹屋门 | 3 | `BAMBOO_HUT_DOOR`（door3d，是门，`is_door`） | N | 竖／横×开／关，约 8 张 |
| 灶坑 | 4 | `BAMBOO_HUT_COOKING3`（地板＋`add_mos`） | N 或 K | |
| 商店 | 6 | **yeek 商人是 NPC，不是陷阱**（`defineTile('1',"BAMBOO_HUT_FLOOR",nil,"YEEK_STORE_GEM")` 第 4 参数是 actor，`irkkk.lua:35-40`）；底面是竹屋地 | 无地形改动 | 商店走 NPC 对话，与地形无关。 |
| 出口 | 1 | `JUNGLE_GRASS_UP_WILDERNESS` | R | Caldera `exit-world` |

新图：**40–50**（墙 32＋地 2＋门 8＋灶 2＋可选）。

#### A.3.10 Point Zero（`point-zero.lua`）

| 格组 | 格数 | 身份 | 分型 | 说明 |
| --- | ---: | --- | --- | --- |
| 外太空 | 1,794 | `OUTERSPACE` | R | Abashed Expanse 已有 `space`（`CT:465-491`）；另有背景星空 shader／粒子 |
| 浮岩 | 495 | `FLOATING_ROCKS` | R | 同上 `rocks`；`void.lua:60-79` |
| 建筑墙 | 55（含 8 商店） | `HARDWALL` | R | |
| 短草 | 28 | `GRASS_SHORT` | R（森林族 id 已含） | |
| 山墙 | 28 | `HARDMOUNTAIN_WALL` | R（新身份） | 同 Last Hope |
| 树 | 23 | `TREE` | R | |
| 时空裂缝 | 21 | `SPACETIME_RIFT` | R | 虚空族 `rift`（Unhallowed／Temporal Rift 用；需门控加 `town-point-zero`） |
| 深水 | 18 | `DEEP_WATER` | R | |
| 冷杉林 | 15 | `COLD_FOREST`（区域本地，subtype `ice`，`can_pass.pass_tree`，30 变体） | R（新身份，复用雪树图）／N | `town-point-zero/grids.lua:41-60` |
| 虚空地板 | 13＋1 | `VOID`（1 格带 Zemekkys NPC） | R | 虚空族 `floor` |
| 出口 | 1 | `RIFT`（区域本地 `<`，`demon_portal2` add_mos，`change_zone=wilderness`） | N（小）或 K | `grids.lua:27-39`；2 张出口图或保持原生 |
| **时间光束端点** | 14 | 运行时 `cloneFull` 端点格，`block_move` 传送（`zone.lua:85-135`） | **K** | 7 条光束的两端；在 `on_enter` 里由原生 `removeAllMOs`＋`altered` 改造，适配器天然拒绝（`rawget(g,'block_move')`）。粒子发射器不动。 |
| 商店 | 8 | 布甲、剑、匕首、弓、法杖、轻甲、符文师、珠宝 | K | |

约束：`color_shown/color_obscure` 紫调、`effects EFF_ZONE_AURA_OUT_OF_TIME`、星空／雪 shader 是区域／整图层，独立于地形替换；但紫调乘在整图上，棋盘图色要在此调子下验读 [推断]。
新图：**0–4**。

#### A.3.11 Angolwen（`angolwen.tmx`）

| 格组 | 格数 | 身份 | 分型 | 说明 |
| --- | ---: | --- | --- | --- |
| 山墙 | 1,974（绝大多数在城外圈，被 `block_sight` 遮挡不显示） | `HARDMOUNTAIN_WALL` | R（新身份） | 无 `all_remembered`，只有靠近城区才被看见 |
| 草 | 254 | `GRASS` | R | |
| 石板路 | 178 | `GRASS_ROAD_STONE` | R | |
| 耕地 | 48 | `FIELDS` | N（与 Zigur 共用 2–4 张） | |
| 树 | 18 | `TREE` | R | |
| 喷泉 | 12＋1 | `FOUNTAIN`（`DEEP_WATER` 基，`does_block_move`，`block_move` 触发 `learnLore("angolwen-fountain")`）＋`FOUNTAIN_MAIN`（384×320 大喷泉叠层 6×5，`z=17`） | **K**（叠层与回调）＋底走 R | `town-angolwen/grids.lua:44-64`；水底面用 `deep` 掩码需注意大喷泉叠层覆盖 6×5 格 |
| 魔法岩 | 3 | `ROCK`（草底＋`maze_rock.png` z=4，阻挡） | K | |
| 建筑墙 | 11 | `HARDWALL` | R | 只有 4 个商店（珠宝、炼金、图书馆、法杖）＋2 个 NPC（Linaniil、Tarelion） |
| 返回出口 | 1 | TMX 自定义 `grid_class.new{...change_zone=game.player.last_wilderness}`，`worldmap.png` 叠层 | K | 运行时目的地，不改 |

TMX 加载路径（`custom=` 属性）不会经过 `Grid:loadList` 印记，但基础身份来自区域 `grids.lua` 的 `load()`，仍会打印记。新图：**0–2**（耕地与 Zigur 共用）。

### A.4 汇总表（每城一行）

| 城镇 | 主要族 | R 占比（估） | 需新图（文件数） | 关键风险 |
| --- | --- | ---: | ---: | --- |
| Derth | 森林＋石质建筑 | ≈100% | 0 | 急切安装；树海 56%；商店叠层观感 |
| Last Hope | 森林＋石质＋山墙 | ≈95% | 0–2 | 雕像回调核对；`FLOOR_ROAD_STONE` |
| Zigur | 森林＋石质＋沙＋熔岩 | ≈93% | 2–4 | `FIELDS`；`POST` 回调；沙门控 |
| Shatur | 森林＋雪 | ≈100%（新分类） | 0–2 | 绿林／雪林并置；无建筑墙，商店直接在草上 |
| Elvala | 森林＋石质 | 100% | 0 | 水面占 38% |
| Angolwen | 森林＋山墙 | ≈95% | 0–2 | 6×5 大喷泉叠层；`FOUNTAIN` 回调 |
| Gates of Morning | 石质＋沙＋金山 | ≈50%（金山 31% 需新图） | 36–40 | 金山墙识别度；`FENS`／传送门动态 |
| Lumberjack | 森林＋石质 | 100% | 0 | 任务专用、曝光低 |
| Iron Council | 石质＋晶簇＋雕像 | ≈97% | 0–2 | 新出口变体；雕像叠层 |
| Irkkk | 丛林＋竹屋 | ≈65%（竹屋墙／地 22%） | 40–50 | 竹屋族全新；深水观感 |
| Point Zero | 虚空＋森林＋雪树 | ≈95% | 0–4 | 紫调；光束端点保持原生；`COLD_FOREST` |

### A.5 跨城规则、回调约束与风险

1. **商店／聊天陷阱不动** [已验证]：`block_move` 由 `resolvers.calc.store`／`chatfeature` 绑在陷阱实体上（`NT/resolvers.lua:533-556`、`:608-616`），完全与地形替换无关。适配器只换底格，不碰陷阱层。唯一要验的是：**陷阱层在棋盘墙贴图上的观感**——64×64 门板是透明背景，叠在花岗岩上原设计；换成棋盘石墙后需实机看 z 序（陷阱 z=18）是否仍在墙面上方 [推断]。
2. **回调格一律走“精确回调核对”或保持原生**：Zigur `POST.on_move`、Last Hope／Shatur 雕像的 `block_move`、Angolwen `FOUNTAIN.block_move`。棋子仓库已有 `sameCallback(fn,source,line)`（`CT:1044-1047`）；地图文件里的 `quickEntity` 闭包来源是地图文件本身，行号可锁 [推断]。
3. **门控要点**：把每区加入 `FOREST_ZONES`＋`M.variant`＋`M.combined`（`CT:1774`、`2131`、`2450`）；`GRID` 名单需补 `mountain.lua`、`snowy_forest.lua`、`elven_forest.lua`、`jungle_hut.lua` 以及需要精确印记的 `town-*/grids.lua`（`GRID:4-28`）。
4. **`all_remembered` 城镇的急切安装（TW1）** [推断]：为 `all_remembered` 城镇新增“对全图石质格一次性按静态邻居算掩码并 `replace_display`”，行为与森林族一致；`Angolwen`／`Lumberjack` 无此标志，可继续用视野内观察语义。切换 `Refined→Native→Refined` 与 `NicerTiles` 重铺回退已由 `applyForest`＋`superload/mod/class/NicerTiles.lua:14-27` 覆盖。
5. **石质族观感前提**：`V2`（Kor'Pul 石质族墙比地板亮）已被记录为偏离棋盘语言（`TERRAIN-GAP-20260929.md:231`）；城镇建筑若沿用会亮。是否等 S8 暗墙套件再做，属产品决定。
6. **昼夜与 shader**：`day_night=true` 的城镇有整图色调层；`all_lited` 已使全图受光。地形图不应写死光照，色调乘在整图上，需在日夜两态验读 [推断]。
7. **前景粒子**：Derth 老鹰、Irkkk 鸟、Point Zero 雪／星空是区域回调，不受影响 [已验证]。
8. **重叠大图**：Angolwen 大喷泉 384×320（6×5 格）、Last Hope 雕像 64×128；它们是 `add_displays`，适配器保留叠层就不必重画，但底下的“棋盘水／草”必须在被覆盖区之外也连贯 [推断]。

### A.6 套件计划（按曝光排序，每个约一个 agent 的工作量）

曝光排序依据：世界图必经的首个城镇 Derth（A 档）＞ Last Hope（进度主线）＞ 开局城（Angolwen／Gates／Irkkk／Point Zero，仅特定职业或种族）＞ 只能世界图进的 Elvala／Shatur／Zigur／Iron Council ＞ 任务专用 Lumberjack [推断，基于 `data/birth` 引用和 `TERRAIN-GAP-20260929.md:43` 频度档位]。

| 套件 | 内容 | 新图（估） | 主要工作 | 难度 |
| --- | --- | ---: | --- | --- |
| **TW1** | **急切安装基础设施＋Lumberjack（冒烟）＋Derth** | 0 | 门控三处；石质格急切安装；`markSource` 名单；契约测试（商店格拒绝、陷阱层不动、Refined↔Native 往返）；Lumberjack 25×25 先验，再做 Derth 50×50 | 中（一次性成本在此） |
| **TW2** | Last Hope＋Elvala | 0–2 | `HARDMOUNTAIN_WALL` 新身份（复用 Daikara 墙掩码，新增合同）；`FLOOR_ROAD_STONE` 分类＋地砖路 2 张；雕像回调核对 | 低–中 |
| **TW3** | Zigur＋Angolwen＋Iron Council | 4–8 | `FIELDS` 2 种耕地（4 张）；`LAVA`（复用熔岩掩码）；`ROCK`／`FOUNTAIN`／雕像走叠层；出口变体；`CRYSTAL_WALL` 新身份 | 中 |
| **TW4** | Shatur＋Point Zero | 2–4 | 雪族新分类（`SNOWY_GRASS`、`SNOW_ELVEN_TREE`、`COLD_FOREST`）；虚空族门控＋`RIFT` 出口图 2 张；光束端点原生 | 中 |
| **TW5** | Gates of Morning | 36–40 | 金山墙 32 张掩码族（一次生图母版，其余由导出器生成）＋路 2＋棕榈 2（可与 S6 合并） | 中（首次新墙族生图） |
| **TW6** | Irkkk | 40–50 | 竹屋墙 32＋地 2＋门约 8＋灶 2；丛林／深水拼接；可与 S6 Gorbat 竹屋合并复用 | 中–高（新族） |

合计新图约 **85–115 个 PNG 文件**，对应约 **6–10 个母版级生图任务**（掩码由导出器生成；估计基于现有导出惯例，[推断]）。TW1–TW4 合计 ≤ 15 张，是低成本高曝光；TW5／TW6 才有实质生图成本，可推迟。

---

## Part B — 世界地图

### B.1 构建与绘制方式 [已验证]

| 项 | 事实 | 出处 |
| --- | --- | --- |
| 区域 | `wilderness`，`width=170,height=100`，`engine.generator.map.Static`，`map="wilderness/eyal"`；**`all_remembered` 被注释掉**、`all_lited=true`、`day_night` 被注释；视野半径 `wilderness_see_radius=4`。 | `NT/zones/wilderness/zone.lua:21-46` |
| 视野 | 世界图只算半径 4 的 FOV，并按距离给亮度渐变；未探索区域保持未知。 | `game/modules/tome/class/Player.lua:545-560`（`wild_fovdist`、`computeFOV(...wilderness_see_radius...)`） |
| 图 | 17,000 格（170×100）；符号即“区域”，`defineTile` 映射 33 种基础身份＋约 28 个入口／区域 tile。 | `NT/maps/wilderness/eyal.lua:22-92` |
| 图块尺寸 | 沿用全局 `Map.tile_w/h`（默认 64）；`WM_norm_trees_5_01.png` 64×128、`mountain5_1.png` 64×64；**没有世界图专用的瓦片尺寸覆写**（grep `wilderness` 与 tile/scale 无命中）。 | `game/modules/tome/class/Game.lua` grep；贴图实测 |
| 实体 | `zones/wilderness/grids.lua` 共 74 个 `newEntity`（含循环变体，实例化后约数百个 `define_as`）。 | `NT/zones/wilderness/grids.lua` |
| 大图叠层 | 森林类是 `wall`＋`add_displays{z=17, display_h=2, display_y=-1}` 的 64×128 树簇，往上侵入一格；`nice_editer2 method="borders"` 再往**邻格**加 8 个方向的树缘 MO（`WM_*_8/2/4/6/37d/19d/91d/73d`，`z=6/16`）。共 190 张 `worldmap/` 贴图。 | `grids.lua:60-89`、`:108-122`、`:296-326`；`gfx/shockbolt/terrain/worldmap` 计数 |
| 水 | `WATER_BASE` 带 `shader="water"`（动画）；`SEA_EYAL` 等 `does_block_move`＋`can_pass.pass_water`；`RIVER` 可走。名字不是 `deep water`（`sea of Eyal`／`river`／`lake`…）。 | `grids.lua:333-352` |
| 山 | `MOUNTAIN`／`DAIKARA_`／`IRONTHRONE_`／`VOLCANIC_`（循环生成，`rockwall`，`pass_wall`，6 变体）＋`GOLDEN_MOUNTAIN`（`block_sense/esp`）；`nice_editer mountain borders_def`。 | `grids.lua:356-395` |
| 入口 | 城镇＝`TOWN` 基（`PLAINS` 基＋`glow=true`＋`notice`）加 `add_mos/add_displays` 图标；区域入口 `ZONE_PLAINS/DESERT/JUNGLE_PLAINS` 基，各带专属入口叠层（`dungeon_entrance02.png`、`tower_entrance_up02.png`、`road_going_right_01.png` 128×64、`road_upwards_01.png` 64×128 等）。共 **40 个 `change_zone` 定义**，运行时任务还会在 `zone-pop` spot 追加入口。 | `grids.lua:506-`；`eyal.lua:96-135` |
| 入口辉光 | `glow=true` 的入口在初始化时挂 `WildernessGrid` 叠层，用**显示回调**画 `starglow` 粒子，只在“该区未访问过”时显示；悬浮文字“Never visited yet”。 | `game/modules/tome/class/Grid.lua:36-44`、`game/modules/tome/class/WildernessGrid.lua:26-45`、`zone.lua:91` |
| 天气／昼夜 | 无：`day_night` 关、无 `makeWeather`。 | `zone.lua` |
| 小地图 | 由 `special_minimap`／`display` 颜色驱动，不读贴图（森林 `colors.GREEN`、水 `colors.BLUE`）。 | `grids.lua:87,340` |
| 门控现状 | 世界图不在任何适配器名单，全部原生；`terrain()` 的 `name=='deep water'` 判据不会误吞 `sea of Eyal`。 | `CT:1813-1819`、`CT:217-238` |

### B.2 格身份清单（170×100，17,000 格）[已验证：脚本实跑]

| 族 | 身份（格数） | 小计 |
| --- | --- | ---: |
| 海／湖（阻挡，动画水） | SEA_EYAL 10,284；LAKE 59；SEA_SASH 37；LAKE_WESTREACH 35；LAKE_IRONDEEP 21；LAKE_SPELLMURK 13；LAKE_NUR 6 | 10,455 |
| 河（可走水） | RIVER 225 | 225 |
| 冰 | FROZEN_SEA 218；POLAR_CAP 154 | 372 |
| 草地类地板 | PLAINS 1,349；LOW_HILLS 526；CULTIVATION 74；JUNGLE_PLAINS 33 | 1,982 |
| 森林类（大树簇叠层） | FOREST 485；COLD_FOREST 165；PINE_FOREST 162；OLD_FOREST 74；OASIS 69；ELVENWOOD_GREEN 56；ELVENWOOD_SNOW 48；JUNGLE_FOREST 15；BURNT_FOREST 15 | 1,089 |
| 山 | MOUNTAIN 473；VOLCANIC 222；IRONTHRONE 146；DAIKARA 95；GOLDEN 80 | 1,016 |
| 沙漠／焦土 | DESERT 1,780；CHARRED_SCAR 53 | 1,833 |
| 入口／特殊 | 约 28 个（12 座城镇入口、15 区入口、Charred Scar 火山、Murgol 等） | 28 |

### B.3 现有棋盘机制能覆盖多少 [推断]

| 世界图族 | 可复用的现成机制／图 | 缺口 |
| --- | --- | --- |
| 海／河／湖 | 森林族 `deep` 掩码 32 张、`applyForest` 全图 `replace_display` | 新增身份判定（现判据要求 `name=='deep water'`）；无动画水，会失去 `shader=water` 动效（换图后需决定是否保留 shader，与合同“无 shader”冲突 [推断]）；区分海（阻挡）与河（可走）读法 |
| 草地／丘陵／耕地 | `grass` 图 | `PLAINS`/`LOW_HILLS`/`CULTIVATION` 不在 `terrain()` 的 `define_as` 名单；`LOW_HILLS`（6 种丘陵 add_mos）与 `CULTIVATION` 需专图（丘陵 2–3、耕地 2） |
| 森林（9 种） | `tree-oak/pine/willow`、雪树 | 世界尺度下 1 格＝一片林，9 种林（普通／松／古／冷杉／绿精灵／雪精灵／丛林／焦／绿洲）必须保持生态可辨；至少 5 种新树块图（约 10–14 张） |
| 山（5 种） | Daikara `mountain-wall` 掩码 46 张（`CT:942-984`、`refined/daikara`） | 五种山靠色调分：普通、火山、铁王座、Daikara、金色；至少 3 套新掩码族（约 96 张）或色调导出 |
| 沙漠／焦土 | `refined/beach/sand`、`scorch` 熔岩族 | 可复用，需新分类 |
| 冰 | 无 | 冰原／冻海是新族（约 4–8 张） |
| 入口图标（40 个＋动态） | E3 中心格“保留原生道具层” | 只保留 `image+z`（`CT:1858-1874`），**丢显示回调**，故辉光粒子会消失；40 种叠层大小各异（64×64、128×64、64×128、128×128） |
| 探索／记忆态 | 森林族靠原生遮罩，已可用 | 无 `all_remembered`＋FOV 半径 4＋亮度渐变，需要逐态验读 |

### B.4 风险

1. **入口图标是玩家导航**：辉光（未访问提示）靠 `WildernessGrid` 显示回调，现有叠层保留路径不带回调，换图会静默丢失；必须扩展叠层保留机制或让入口格保持原生（后者会在棋盘地形里留下 40 个“原生补丁”，观感冲突）[推断]。
2. **大图叠层跨格**：树簇 64×128 往上溢一格、邻格 borders MO 往外溢；只替换部分群系会让残留叠层压在棋盘格上，必须按群系整片一致替换（含邻格的 `nice_editer` MO 清理）。
3. **世界尺度可读性**：一格＝一个地区，棋盘树块／山块需让 9 种林、5 种山依然可辨；这是美术评审风险，不是代码风险。
4. **规模**：17,000 格全图 `g:clone()`＋`replace_display`（`CT:1853-1866` 逐格克隆）对内存与首帧时间的影响未测 [推断]。
5. **动画水**：海占 61% 的地图且带 `water` shader；换成静态棋盘水会改变整图观感，且“无 shader”合同与原生动画冲突。
6. **动态入口／任务格**：`zone-pop` spot 上任务会加入口，需要每个都过合同（`eyal.lua:96-135`）。
7. **未验证的原生依赖**：`wda={script="eyal"}`（`eyal.lua`）与 `post_nicer_tiles` 的 `attrs`（`zone.lua:37-63`）不属于地形显示，预计无影响 [推断]。

### B.5 判定

**结论：LARGE。**

理由（关键数字）：
- 17,000 格、约 33 种基础身份、40+ 入口叠层，**几乎所有身份都是现有适配器不认的**（`PLAINS`、`FOREST`、`SEA_EYAL`、5 种山、9 种林都要新增分类合同），不是“复用后改门控”。
- 需要至少 **5 套**：W1 水／河／湖／沙／草／丘陵／耕地／焦土（现有图为主）；W2 九种森林；W3 五种山＋冰；W4 入口叠层保留（含辉光回调）与 40 个入口逐个合同；W5 全图性能／探索态／回退验证。
- 新图估计 **150–250 个 PNG**（山掩码 3 套×32≈96、森林块 10–14、冰 4–8、丘陵／耕地 4–6、入口图标视处理而定，[推断]），远超“≤2 套、少量新图”门槛。
- 一个折中——只重绘海／草／沙（约 75% 的格）而保留森林／山／入口原生——会得到“棋盘水草底＋原生大树簇、原生 190 张叠层”的混搭；且原生森林的邻格 MO 会被清理，反而破坏原生林缘，不建议。

建议：世界图暂不做，城镇 TW1–TW4 先行。

---

## 顶层不确定项

1. **石质族急切安装**：本文关于“视野外保持原生”的判断来自读码（`CT:2353-2372`、`CT:2396-2436`、`MAP:6-15`），尚未在 `all_remembered` 城镇实机确认；TW1 的第一个任务应是用隔离夹具在 Derth 上验证，再决定实现路径。
2. **石质墙／地砖套在城镇的美观**：Kor'Pul 暗砖墙＋地砖用作户外建筑外墙和广场，观感是否成立、是否需等 S8 暗墙（V2），属美术评审，本调研无法判定。
3. **商店门叠层 z 序**：陷阱 z=18 门板叠在棋盘墙上的实际观感未验。
4. **日夜色调与 Point Zero 紫调**：整图色调下棋盘图可读性未验。
5. **新图数量**：文件数依现有导出惯例（掩码族 32、地板／树 2）推算，具体取决于母版数与导出器。
6. **世界图**：入口辉光保留、17k 格克隆开销、动画水取舍均未验证。
7. **Zigur 任务门／Angolwen TMX 自定义出口**：`CLOSED_GATE`／`OPEN_GATE` 的使用点和 TMX `custom=` 的印记路径为推断，未逐行核对。
