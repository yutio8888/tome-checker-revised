# 地形套件扩充盘点（2026-09-28，HEAD `cfa1fb4`）

只读静态分析：未启动游戏、未生成美术、未提交。数据来源为 `game/modules/tome/data/zones/<zone>/{zone,grids}.lua`、`data/general/grids/*.lua`、`data/maps/zones/*.lua`、`data/rooms/*.lua`、`data/tilesets/*`，对照本仓库 `overload/mod/class/CheckerTerrain.lua`、`superload/engine/Map.lua`、`superload/mod/class/Grid.lua`。配套 [PLAN.md](PLAN.md)；原则不变：**支持一个地城 = 覆盖全部布局变体与全部层**。

## 0. 两个现有适配器的准入条件（判定依据）

| | 森林式（`applyForest` + `terrain()`） | Kor'Pul 式（`markSource` + `classify()` + 逐格渲染） |
| --- | --- | --- |
| 门控 | `zone.short_name=='trollmire'`（`CheckerTerrain.lua:106`） | `M.variant()` 只认 `ruins-kor-pul`（`:230-234`）；`Map.lua:6` 仅在 `variant` 成立时走逐格路径 |
| 识别依据 | 运行时字段：`subtype=='grass'`（exit / tree / hardtree / road / flower / grass）、`subtype=='water'`（bog-tree / deep / bog / bog-misc）；**不看来源文件** | 必须由 `/data/general/grids/basic.lua` 加载，`define_as` 在白名单（FLOOR、WALL*/HARDWALL* 全部 wall3d 变体、DOOR*、UP/DOWN/UP_WILDERNESS），签名与原版逐字段一致；有 shader、tint、函数字段或本区覆盖的一律回退原生 |
| 画法 | 装一次 `replace_display`；水体按同族四邻掩码 | 按四邻墙掩码加奇偶，逐格取 `refined/korpul/*` |
| 同层混用 | **不支持**：`M.apply` 在 `variant` 成立时直接返回，不跑 `applyForest`；反过来森林区不进逐格路径 | 同左 |

由此得到三条横向结论：

1. **`exit` 判定嵌在 `subtype=='grass'` 分支内**。新 subtype（rock / underground / sand / cave / crystal）需要各自的出口分支，或把 `change_level/change_zone → exit` 提到前置检查。前置时注意排除 LAKE_NUR、QUICK_EXIT、RIFT 这类单格特殊出口。
2. **basic.lua 里还有 `OLD_FLOOR`/`OLD_WALL` 家族**（`basic.lua:279-310`）。它们会经过 `markSource`，但不在 `identities` 白名单中。`OLD_WALL` 没有 `dig`/`can_pass`，也没有 `block_sense/esp`，既不满足 `wall` 也不满足 `hardwall` 的判据，需要新 kind，例如 `wall-nodig`。
3. **同层双适配器**是 Rhaloren OVERGROUND、Maze COLLAPSED（CRACKS）和 Daikara 密室的共同前置。建议作为一个独立的运行时工作包（“逐格优先、森林补位”的调度层），不要在每个地城里临时拼接。

---

## 1. Old Forest（`old-forest`，level_range 7–16）

**布局与层**：`alternateZone(short_name,{"CRYSTALINE",2})`，得到 DEFAULT 约 2/3、CRYSTALINE 约 1/3，首次进入强制 DEFAULT。两种布局都是 4 层、`engine.generator.map.Roomer`（`forest_clearing` 加 `lesser_vault`），没有静态地图。L1 的 `up=GRASS_UP_WILDERNESS`；L4 为 `edge_entrances={4,2}`、`down=LAKE_NUR`、`force_last_stair`。区域级 `nicer_tiler_overlay="DungeonWallsGrass"`，与 Trollmire FLOODED 相同。

**身份**（`grids.lua` 按 `currentZone.is_crystaline` 分两套）：

| define_as | 来源 | type/subtype/name | 规则 | 显示 | 归类 |
| --- | --- | --- | --- | --- | --- |
| GRASS（+GRASS_PATCH1-14） | DEFAULT：区域本地；CRYSTALINE：forest.lua | floor / **dark_grass**（DEFAULT）或 grass / "grass" | 可走，`grow=TREE` | nice_tiler replace×14、nice_editer borders_def | 复用 `grass` |
| TREE（+TREE1-30） | 同上 | wall / dark_grass 或 grass / "tree" | block_move、block_sight、`can_pass.pass_tree`、`dig=GRASS` | makeNewTrees：oldforest 树种，DEFAULT 为夏季／枯叶，CRYSTALINE 为春季／枯叶 | 复用 `tree-oak/pine/willow` |
| HARDTREE（+1-30） | 同上 | wall / 同上 / "tall thick tree" | 另有 block_sense、block_esp，不可挖 | 同上 | 复用 `tree-hard`（0.6.14 已独立） |
| GRASS_UP4 / GRASS_DOWN6 | forest.lua（DEFAULT 在加载时只改 image 和 editer） | floor / **grass** / "way to…" | change_level ∓1 | add_mos 箭头 | 复用 `exit` |
| GRASS_UP_WILDERNESS | DEFAULT 在区域本地 `base=` 覆盖；CRYSTALINE 用 forest.lua | floor / grass | change_zone=wilderness | add_mos worldmap | 复用 `exit` |
| LAKE_NUR（仅 L4） | 区域本地，无 base | **无 subtype** / "way to the lake of Nur" | change_zone=lake-nur | add_displays way_next_2 | 保持原生，`terrain()` 天然不命中 |
| 密室（honey_glade、troll-hideout、bandit-fortress、ROCK_VAULT 等） | vault 池 | — | ROCK_VAULT 为 is_door 推石谜题 | — | 保持原生 |

**适配器**：森林式。CRYSTALINE 的 subtype 全为 `grass`，只要放宽门控就能全量命中。DEFAULT 的 GRASS/TREE/HARDTREE 为 `dark_grass`，需要让 `terrain()` 的草地分支同时接受 `dark_grass`（出口本身仍是 `grass`）。
**成本**：新母版 0，导出器 0；运行时改门控，加一个 subtype 别名，补测试。风险：Roomer 的矩形空地与 Trollmire 的有机林地拼图观感不同，需实机看 `tree-*` 大块连片的效果；原生地板有深浅两套，棋盘统一成一种 `grass` 属于有意取舍，需在验收记录中写明。

## 2. Slazish Fens（`slazish-fen`，level_range 1–7，tier1；原候选清单外，新增）

**布局与层**：无变体，3 层，`engine.generator.map.Forest`，参数与 Trollmire FLOODED 几乎相同（`floor2=BOGWATER/BOGWATER_MISC`、`wall=BOGTREE`、`floor=GRASS/FLOWER`）。L1 的 `up=GATES_OF_MORNING`；L3 用 `end_road_room="zones/zoisla"`（`data/rooms/zones/zoisla.lua`，4×4 的 near_portal=BOGWATER 加一格 PORTAL），`down=GRASS`，没有静态地图。

**身份**：GRASS、FLOWER（forest.lua）；GRASS_UP4、GRASS_DOWN6；GATES_OF_MORNING（`base=GRASS_UP_WILDERNESS`，subtype grass，带 change_zone，归入 `exit`）；BOGTREE（+1-40，区域本地，wall/water/"tree"，`shader=water`，`dig=BOGWATER`，`define_as` 前缀为 BOGTREE，可命中 `isBogtreeId`）；BOGWATER（WATER_BASE，floor/water/"bog water"，`shader=water`）；BOGWATER_MISC1-7（add_displays）；PORTAL（`base=BOGWATER`，但 `name="coral portal"`，`block_move` 为函数，叠加双格高传送门）。
**归类**：除 PORTAL 外都能复用 Trollmire FLOODED 的 `grass/flower/exit/bog-tree/bog/bog-misc`。PORTAL 因 name 不是 "bog water" 会回退原生，这是正确结果，属于任务唯一要素。
**成本**：新母版 0，只改门控。风险：原生水面贴图为 `poisoned_water`，而棋盘沿用 `bog`，要确认这里没有中毒规则（WATER_BASE 本身无伤害字段，需实机复核）；只有东部 Gates of Morning 开局才会进入，**玩家暴露面低于 Trollmire/Old Forest**。

## 3. Rhaloren Camp（`rhaloren-camp`，level_range 1–7，tier1）

**布局与层**：`alternateZoneTier1(short_name,{"OVERGROUND",1})`。DEFAULT 使用 Roomer（`random_room`、`money_vault`、`lesser_vault`：circle、amon-sul-crypt、rat-nest、skeleton-mage-cabal），3 层。OVERGROUND 使用 `engine.generator.map.Town`（`floor=FLOOR`、`wall=WALL`、`door=DOOR`，`external_floor` 为 15×GRASS 加 1×TREE，另有 collapsed-tower 等密室），3 层。**两种布局的 L3 共用静态地图 `zones/rhaloren-camp-last`**，图例为 `.`→FLOOR、`#`→WALL、`+`→DOOR，内嵌 Roomer 子生成器（FLOOR/WALL/UP/DOOR），另有 `!`/`P`/`p` 只是在 FLOOR 上放物件或 NPC。

**身份**：`grids.lua` 只有 `load(basic)` 和 `load(forest)`，没有任何本区覆盖。

| 身份 | 适用布局 | 归类／适配器 |
| --- | --- | --- |
| FLOOR、WALL（wall3d 全族）、DOOR（door3d）、UP、DOWN、UP_WILDERNESS | DEFAULT 全部；OVERGROUND 建筑内部；L3 | 复用 Kor'Pul 石头组，原版签名，零改动命中 |
| GRASS、TREE、GRASS_UP4、GRASS_DOWN6、GRASS_UP_WILDERNESS | OVERGROUND 户外 | 复用森林 `grass/tree/exit` |
| 密室内容 | 两种布局 | 保持原生（未逐一审计） |

**成本**：新母版 0。DEFAULT 只需扩 `M.variant`（它没有 `is_hideout` 这类字段，variant 可按 `is_*` 或 layout 返回）。**OVERGROUND 必须先做同层双适配器调度**，是本仓库的第一项架构改动。风险：Kor'Pul 石墙与森林草地交界处缺少过渡；Town 生成器的建筑外墙贴着草地，墙掩码只统计墙邻居，理论可行，但需实机检查。

## 4. Norgos' Lair（`norgos-lair`，level_range 1–7，tier1）

**布局与层**：`alternateZoneTier1(short_name,{"INVADED",1})`。INVADED 只更换守卫（FROZEN_NORGOS）和降雪强度，**地形完全相同**。3 层，Roomer（`forest_clearing`，没有 `rooms_config`），没有静态地图，没有密室。L1 的 `up=ROCKY_UP_WILDERNESS`。
**身份**（mountain.lua，加载回调把 `rocky_ground.png` 改为 `snowy_grass.png`）：ROCKY_GROUND（floor/**rock**/"rocky ground"，兼作 door）；ROCKY_SNOWY_TREE 基体及 1–30 号（wall/rock/"snowy tree"，block_move、block_sight、`pass_tree`、`dig=ROCKY_GROUND`，冬季 makeNewTrees；生成器明列基体及 2–20 号）；ROCKY_UP6、ROCKY_DOWN4、ROCKY_UP_WILDERNESS（floor/rock，add_displays 箭头或 worldmap）。
**状态（2026-09-28，已提交 `179544e`，未打包）**：DEFAULT／INVADED L1–L3 已接入独立雪岩族，运行时按 `norgos-lair` 门控，并逐一核对原生身份、规则和显示合同，不按 `subtype=='rock'` 整族接管。六次独立冷启动共 14,994/14,994 个支持格绘制，原生回退 0；树木原生 DIG 自动修复、Native／Blockout／Refined 模式及 48/64/96px 已核验。[实机证据](../../evidence/norgos-20260928/README.md)、[美术复核](../../art/terrain-norgos-snow-v1/REVIEW.md)。
**制作量**：ImageGen 7 次调用选出地板、雪松、冬榆及三个出口，共 6 件母版；森林导出器新增雪岩入口，两种棋盘奇偶导出 12 张运行图。此处原估约 3 件母版已被实际数量替代。Daikara 的独立裸岩、岩墙与熔岩接入见第 9 节。

## 5. Heart of the Gloom（`heart-gloom`，level_range 1–7，tier1）

**布局与层**：`alternateZone(short_name,{"PURIFIED",2})`。两种布局是同一个 `engine.generator.map.Octopus` 结构，只换皮肤、守卫和粒子，3 层，没有静态地图。L1 的 `up=UNDERGROUND_LADDER_UP_WILDERNESS`。
**身份**：`grids.lua` 按 `is_purified` 加载 `underground_gloomy.lua` 或 `underground_dreamy.lua`（两者字段同构、贴图不同），另在本区定义 TREE。
- UNDERGROUND_FLOOR（+20）：floor/underground，兼作 door
- UNDERGROUND_CREEP（+4）：floor/**creep**，borders_def
- UNDERGROUND_TREE（+30）：wall/underground/"underground thick vegetation"，`pass_tree`、`dig`
- TREE（本区，+30）：wall/**dark_grass**/"tree"
- UNDERGROUND_LADDER_UP、UNDERGROUND_LADDER_DOWN、UNDERGROUND_LADDER_UP_WILDERNESS

**归类**：全部需要新美术，包括地面、苔藓地（带边缘）、菌林墙、梯子出口，每项都要 gloomy 和 dreamy 两套皮肤，适配器用森林式。注意本区 TREE 的 subtype 为 `dark_grass`：若 Old Forest 已经放宽 `dark_grass`，它会被识别成普通 `tree`，这在地下菌洞里不合题材。必须**按 zone 门控**，或在 heart-gloom 中改判为菌林墙。
**成本**：新母版约 8（4 族×2 皮肤）；CREEP 需要边缘掩码导出；运行时需新增 subtype 分支和 `is_purified` 皮肤选择。风险中等。

**实施结果（2026-09-28，未提交／未打包）**：六件新母版（双皮肤地板、creep、菌林墙），7/10 次 ImageGen 调用含一次中断无图；原生梯子结构按皮肤调色并在世界出口加天光。导出 144 张 128px 运行图，creep 与菌林墙均使用 16 种 N/E/S/W 邻接掩码×两奇偶×两皮肤；整图奇偶乘数 0.895，双皮肤地板平均亮度差 11.23%／10.89%。`TREE` 按 `heart-gloom` 来源和外观合同改判为本区菌林墙，Old Forest 不受影响。返工后隔离夹具两布局×三层各自冷启动、shader 开启，支持格 14,890/14,890、原生回退 0；110 格严格合同外地格保留原生（含事件／密室），两次植被 DIG 和全部模式往返通过。详情见 `evidence/heart-gloom-20260928/README.md`；正式 TEAA 和完整存档未验。

## 6. Scintillating Caves（`scintillating-caves`，level_range 1–7，tier1）

**布局与层**：`alternateZone(short_name,{"TWISTED",2})`。DEFAULT 为 `engine.generator.map.Cavern`，3 层，没有密室；TWISTED 为 Roomer，**5 层**，含 amon-sul-crypt、skeleton-mage-cabal、crystal-cabal、snake-pit 密室。两者都没有静态地图。`foreground` 会周期性调用 `setShown/setObscure` 给全图调色。
**身份**：来自 crystal.lua，经 underground.lua 间接加载。CRYSTAL_FLOOR（+8，floor/underground，兼作 door）；CRYSTAL_WALL（+20，wall/underground/"crystals"，`pass_wall`、`dig`，add_displays 为 makeCrystals 叠层，没有 nice_tiler）；CRYSTAL_LADDER_UP、CRYSTAL_LADDER_DOWN、CRYSTAL_LADDER_UP_WILDERNESS。
**归类**：全部需要新美术（晶洞）。来源不是 basic.lua，Kor'Pul 适配器无法打标；subtype 为 `underground`，与 Heart of the Gloom 撞名，**必须按 zone 加 name 联合判定**。墙在 Cavern 生成器下呈有机轮廓，适合按墙掩码画（沿用 Kor'Pul 的掩码画法，但需要新的识别路径）。
**成本**：地板 1、晶墙掩码组、梯子 1–2，母版约 4–5；导出件若照 Kor'Pul 做全掩码则有几十张。运行时要新建一条非 basic.lua 的逐格识别路径，还要覆盖 Cavern 与 Roomer 两种墙形。全图调色与 `replace_display` 的叠加需实机验证。**本组成本最高的 tier1 地城。**
**实施（2026-09-28，未提交／未打包）**：`crystal.lua` 精确来源印章＋zone 白名单＋规则／外观合同接入三种原生族；`CRYSTAL_FLOOR1…8`、`CRYSTAL_WALL…20`、三种梯子获 40 张独立晶洞图。返工后地板为较亮的柔和洞石，墙顶有随掩码／奇偶变化的蓝色晶面和烘入单图的晶簇；晶墙连接掩码占满阻挡格，原生 `makeCrystals` 随机叠层在棋盘显示时由 `replace_display` 整体代替，Vanilla 仍显示原生叠层。DEFAULT 三层与 TWISTED 五层独立冷启动，返工两布局 L1 后现行逐层样本支持格 11,930/11,930、回退 0；实机自然 FOV 地板／墙差 51.28%／43.56%。原生 DIG、模式往返、动态全图调色通过。初轮随机五场 TWISTED 未抽到 lesser vault；返工 L1 随机生成 snake-pit，另以夹具强制 Roomer 生成原生密室并检查其边界；详细来源、截图和限制见[实机证据](../../evidence/scintillating-20260928/README.md)。

## 7. Sandworm Lair（`sandworm-lair`，level_range 7–16）

**布局与层**：`alternateZone(short_name,{"BIGWORM",2})`。DEFAULT 为 4 层 50×50；BIGWORM 为 2 层，L1 是 **350×20** 长廊，L2 恢复 50×50。全部使用 Roomer（`forest_clearing`），没有静态地图。`grids.lua` 只有 basic 和 sand 两项加载。
**身份**：UNDERGROUND_SAND（+11，floor/sand，兼作 door）；SANDWALL（+6，wall/sand，`pass_wall`，`air_level=-10`，**`dig` 为函数**：挖开后生成 20 回合的临时隧道 Object，坍塌时造成窒息）；SAND_LADDER_UP、SAND_LADDER_DOWN、SAND_LADDER_UP_WILDERNESS。沙虫 tunneler 会在运行中持续改动地形。
**归类**：全部需要新美术（沙地、沙墙、沙梯）。已采用本区精确 ID／规则／外观合同，不按 `subtype=='sand'` 整组识别。沙墙是连续墙体，采用 16 向连通掩码；原生 nice_tiler 的随机池不限制棋盘画法。挖掘产生的临时 Object 保持原生。
**成本**：母版约 3–4。运行时需重点确认 tunneler 连续挖墙时 NicerTiles 修复钩子的覆盖，以及 350×20 大图的性能。风险中高，主要来自动态地形。

**2026-09-28 实施状态**：DEFAULT L1–L4／BIGWORM L1–L2 已完成未提交的 Refined＋Blockout 接入，Vanilla 可还原。按精确 ID 和规则／原生显示合同识别地下沙地、可挖沙墙及三种沙梯；未采纳上文“只加 `subtype=='sand'`”的宽泛建议。沙墙 16 向连片；临时隧道 Object 留原生。六次隔离夹具独立冷启动 19,479/19,479 支持格绘制、回退 0，18 次以 tunneler 为源的原生 DIG 后仍回退 0；BIGWORM L1 7,000 格 Vanilla→Refined 全图刷新 CPU 0.371 秒。40 张图的奇偶差均 ≥12.36%；详见 [实机证据](../../evidence/sandworm-20260928/README.md)和[美术复核](../../art/terrain-sandworm-v1/REVIEW.md)。不改版本、不打包、不提交。

## 8. The Maze（`maze`，level_range 7–16）

**布局与层**：`alternateZone(short_name,{"COLLAPSED",2})`，两种布局结构不同。COLLAPSED 为 4 层 40×40，`engine.generator.map.Maze`，`up/down/floor=OLD_FLOOR`（**没有楼梯贴图**），`wall=OLD_WALL`，L1 的 `up=UP_WILDERNESS`，L4 设 `no_level_connectivity`；`post_process_map` 用 doQuake 直接写入 CRACKS 和 OLD_FLOOR，绕过生成器字符表。DEFAULT 为 2 层 60×60，Maze 生成器，`up=UP`、`down=DOWN`，L2 为 20×20 且 `down=QUICK_EXIT`。两者都没有静态地图。
**身份**：`grids.lua` 只有 basic 加本区的 QUICK_EXIT、CRACKS。OLD_FLOOR（floor/floor，无 editer）；OLD_WALL（wall3d 族，地衣花岗岩，无 dig、无 can_pass）；UP、DOWN、UP_WILDERNESS（原版）；QUICK_EXIT（无 subtype，maze_teleport 叠层）；CRACKS（wall/**cracks**，`block_move` 为函数，弹窗询问是否跳层，`pass_projectile`，borders_def blackcracks）。
**归类**：UP、DOWN、UP_WILDERNESS 直接复用 Kor'Pul 楼梯。OLD_FLOOR 只需在白名单里加一行，即可复用 Kor'Pul floor。OLD_WALL 需要新增 kind：用 Kor'Pul 石墙图属于风格决定，另画“地衣旧墙”则需要一套掩码组。CRACKS 需要新美术，属于危险地形，而且逐格路径拒绝函数字段，只能走森林式新分支。QUICK_EXIT 保持原生。
**成本**：用 Kor'Pul 墙时新母版为 1（CRACKS）；另画旧墙时为 2 加一整套掩码导出。运行时需要 `identities` 扩展、新 kind、同层双适配器，并确认事后写入的格子会触发 `updateMap/repair`。
**实施（2026-09-28，未提交／未打包）**：选用独立旧地衣墙，不回退到 Kor'Pul 普通墙。ImageGen 前台单图调用累计 4 次：旧墙顶面、旧墙边缘、裂隙首版及一次 CRACKS 视觉返工；首版在 48/64px 仅呈细划痕，现用大面积开口版本。旧墙沿用 Kor'Pul 16 掩码×两种奇偶，裂隙为两种奇偶，共 34 张运行 PNG。`OLD_FLOOR` 精确身份复用 Kor'Pul 地板；原版三种楼梯／世界出口复用 Kor'Pul 构件；`CRACKS` 使用 Maze grids.lua 来源印章、原生函数位置与规则合同独立识别，接受 NicerTiles 增加的 `invis.png` 边框占位层。`QUICK_EXIT` 原生。返工后 COLLAPSED L1–L3 独立冷启动重新核验，现行六场景支持格 10,359/10,359、原生回退 0，三层事后写入裂隙分别为 5／6／8 格；L4 原生零裂隙。COLLAPSED 同进程 L1→L2→L1 换层重新绘制，详见 [Maze 证据](../../evidence/maze-20260928/README.md)。

## 9. Daikara（`daikara`，level_range 7–16）

**布局与层**：`alternateZone(short_name,{"VOLCANO",2})`。两种布局同为 4 层 Roomer（`forest_clearing`、`rocky_snowy_trees`，lesser_vault 有 snow-giant-camp 和 perilous-cliffs）。VOLCANO 下 `'.'` 以 `5+6×层数`% 的概率生成 LAVA_FLOOR，且 **L4 换用 `mod.class.generator.map.Caldera`**（mountain、tree、grass=60% 岩地／40% 熔岩，water=LAVA_FLOOR，`down=LAVA_FLOOR` 加 `down_center`）。没有顶层静态地图。
**身份**：ROCKY_GROUND（floor/rock，**未改成雪地贴图**）；MOUNTAIN_WALL（+6，type 为 **rockwall**，subtype rock，`pass_wall`、`dig`、borders_def mountain）；ROCKY_SNOWY_TREE（+30）；LAVA_FLOOR（+16，floor/lava，`shader=lava`，**`grids.lua:22` 加载时执行 `on_stand=nil`，因此本区熔岩不造成伤害**）；ROCKY_UP2、ROCKY_DOWN8、ROCKY_UP4、ROCKY_UP_WILDERNESS；RIFT（post_process 生成的单格时空裂隙，保持原生）。密室额外带来 FLOOR、HARDWALL、DOOR、DOOR_VAULT（basic）、HARDMOUNTAIN_WALL、CLIFFSIDE（阻挡移动但不挡视线的半墙）。
**实施（2026-09-28，未提交／未打包）**：原生 `ROCKY_GROUND` 没有 Norgos 的 `snowy_grass.png` 重写，因此新制裸岩地板，不复用积雪地板；雪树和三款出口的透明构件在裸岩上重新导出。新制岩山墙（16 个不同邻接掩码×两种奇偶）及无害熔岩，总计 46 张运行 PNG。`MOUNTAIN_WALL` 的原生 `borders_def` 附加层和 `LAVA_FLOOR` 的原生边缘层按图像路径及规则合同精确识别，未按 subtype 整族放行。`LAVA_FLOOR.on_stand=nil` 已由 `grids.lua:22` 和实机核验；棋盘熔岩不用危险标记。Caldera 的 `down_center` 把中央地格设为普通 `LAVA_FLOOR`，原生 **没有** `change_level`，所以不画额外出口。密室 basic 身份、`HARDMOUNTAIN_WALL`、`CLIFFSIDE` 与 `RIFT` 保留原生。实机逐层数字与截图见 [Daikara 证据](../../evidence/daikara-20260928/README.md)。
**成本**：在雪岩族之外，还需岩山墙掩码组和熔岩地板（带边缘），母版约 3。风险：Caldera 的“下楼点”其实是熔岩格；熔岩危险语义的表达。

## 10. Dreadfell（`dreadfell`，level_range 15–26）

**布局与层**：无变体，**9 层**，全部 Roomer（random_room、money_vault、undead pit、greater_vault）；没有整层静态地图，但生成的 lesser/greater vault 可以嵌入静态房间。L1 的 `up=UP_WILDERNESS`。0.6.17 已逐层验证，见 `../../evidence/runtime-v0617/README.md`。
**身份**：FLOOR、WALL、DOOR、UP、DOWN、UP_WILDERNESS 均为原版 basic.lua，`grids.lua` 没有覆盖。另有本区 LORE_NOTE（`on_move` 加路牌，保持原生）。water、forest、lava、mountain 的加载只为 greater_vault 池服务。
**归类**：零新美术，直接复用 Kor'Pul 石头组，只需扩 `M.variant`。风险：9 层都要验收；greater vault 会带进非 basic 身份，这些回退原生属于预期；是否需要一套墓穴色调是风格决定，不是技术前提。

## 11. Unremarkable Cave（`unremarkable-cave`，level_range 25–35）

**布局与层**：无变体，**1 层**。静态地图 `zones/unremarkable-cave`（`.`/`+`/`@`/`M`→CAVEFLOOR，`#`→CAVEWALL），左侧 86×50 由 Roomer 子生成器生成（`up=CAVE_LADDER_UP_WILDERNESS`），右侧为手绘首领区。
**身份**：CAVEFLOOR（+18，floor/cave，部分带 add_mos 碎石或蘑菇）；CAVEWALL（wall/cave，`pass_wall`、`dig`，`air_level=-10`，nice_editer 为 sandWalls_def）；CAVE_LADDER_UP_WILDERNESS。
**归类**：全部需要新美术，是通用“洞穴”族：地板、掩码墙、出口。cave.lua 为多个地城共用，可以做成通用洞穴族。风险：子生成区与手绘区接缝处的掩码。等级晚，暴露面低。
**本区进度（2026-09-28）**：已按 `unremarkable-cave` 门控与 `cave.lua` 来源印章接入地板（含原生岩块／蘑菇装饰）、16 掩码洞墙及世界出口，3 件新母版导出 58 张图；其他复用 `cave.lua` 的地城仍未接入。三次隔离冷启动支持格 14,997/14,997、回退 0，静态／生成区接缝及渲染帧 ≥59.49% 地板／墙明度差见[证据](../../evidence/unremarkable-20260928/README.md)。本轮未打包、未提交。

## 12. Ancient Elven Ruins（`ancient-elven-ruins`，level_range 43–52）

**布局与层**：无变体，3 层，`engine.generator.map.TileSet`。L1–2 使用 3x3 的 base、tunnel、windy_tunnel；L3 为 100×100，使用 5x5 拼块（含 crypt），`down=QUICK_EXIT`。拼块字符只有 `.`、`#`、`+`、`'`，**词表很小，TileSet 不构成覆盖障碍**。
**身份**：OLD_FLOOR（地板全部是它）；`#` 以 1/5 概率取 OLD_WALL、4/5 概率取 WALL；DOOR、UP、DOWN、UP_WILDERNESS 为原版；QUICK_EXIT 保持原生。
**归类**：WALL、DOOR、楼梯复用 Kor'Pul；OLD_FLOOR 和 OLD_WALL 与 Maze 共用同一项扩展。先完成 Maze，本区就几乎免费。等级极晚，暴露面最低。
**共享进度（2026-09-28）**：Maze 已导出并实机验证 `OLD_WALL` 专用地衣墙和 `OLD_FLOOR` 复用合同；本区自身尚未接入或逐层验证，不能将 Maze 验证计作 Ancient Elven Ruins 覆盖。

## 13. 其余 tier1 地城（轻量筛查，未做全表）

| 地城 | 生成器 | 初判 |
| --- | --- | --- |
| blighted-ruins | Roomer，L3 为静态地图 | 只加载 basic，可能接近 Kor'Pul 零美术；需核查 L3 静态地图 |
| reknor-escape | TileSet，L3 为静态地图 | 只加载 basic，与 Ancient Elven Ruins 类似 |
| murgol-lair | Roomer，INVASION 变体 | basic 加 water；水下巢穴，需单独核查 |
| ritch-tunnels | Roomer | basic 加 sand，可与 Sandworm 共用沙族 |
| deep-bellow | Cavern，L3 为静态地图 | basic 加 underground，与 Heart of the Gloom 属同一地下族 |
| abashed-expanse | Roomer | burnt 加 void 浮岩，非现有两族 |
| unhallowed-morass | Cavern | basic 加 void，非现有两族 |

建议下一轮先用 20 分钟核实 blighted-ruins 和 reknor-escape 的 L3 静态地图图例，它们可能是“Kor'Pul 门控加一行”的候选。

---

## 2026-09-28 零新图复用进度

`thieves-tunnels` L1–L2、`tempest-peak` L1–L2、`halfling-ruins` L1–L4、`reknor` L1–L4、`reknor-escape` L1–L3 已按既有身份／来源合同接入源码并逐层独立冷启动核验；合计 **31,383／31,383** 支持格，原生回退 **0**。`thieves-tunnels` L2 静态图实际是 basic 石质格；`reknor` L4 静态图的剧情门户仍原生；`halfling-ruins` L4 的砂地、封锁门及 Yeek 特殊出口仍原生。`tempest-peak` L1 原版调色 0.3 使复用岩地／墙过暗，已标记视觉风险。`ardhungol` 需要尚未审核的 cave 上／下梯子图，本批跳过。来源、原始截图及逐层统计见 [复用批次实机证据](../../evidence/reuse-batch-20260928/README.md)。本节之后的排序表是实施前规划快照。

## 汇总排序

排序依据：①新美术量（越少越前）；②现有美术复用率；③暴露面／早期度（tier1、level_range 下限、是否主线必经）。“运行时”列标出架构前置。

| 排名 | 地城 | 最早等级 | 布局×层 | 新母版（估） | 复用率（核心身份） | 适配器 | 运行时前置 |
| ---: | --- | ---: | --- | ---: | ---: | --- | --- |
| 1 | **Old Forest** | 7 | 2 × 4 | 0 | 100%（LAKE_NUR 原生） | 森林式 | 门控加 `dark_grass` 别名 |
| 2 | **Rhaloren Camp** | 1 | 2 × 3（L3 共用静态图） | 0 | 100% | Kor'Pul 与森林同层 | **双适配器调度**（OVERGROUND） |
| 3 | Slazish Fens | 1 | 1 × 3 | 0 | 100%（PORTAL 原生） | 森林式 | 仅门控；暴露面低（东部开局） |
| 4 | Dreadfell | 15 | 1 × 9 | 0 | 100% | Kor'Pul | 仅 `M.variant`；层数多，墓穴风格待定 |
| 5 | **Norgos' Lair（已实现，未打包）** | 1 | 2 × 3（INVADED 只换 NPC／降雪） | 6（已制作） | 雪岩族已覆盖支持身份 | 森林式雪岩分支 | 精确身份门控，实机 14,994/14,994 |
| 6 | Maze（已实现，未打包） | 7 | 2 × 4/2 | 3（已制作） | 楼梯、OLD_FLOOR 复用 | Kor'Pul 石格＋CRACKS 专支 | OLD_* kind、函数格识别、事后写格刷新 |
| 7 | Daikara（已实现，未打包） | 7 | 2 × 4（VOLCANO L4 为 Caldera） | 新制 3（另复用雪树／出口构件） | 受支持身份实机回退 0 | 森林式 Daikara 专用身份合同 | 裸岩、岩山墙 16 掩码、无害熔岩；密室格原生 |
| 8 | Heart of the Gloom | 1 | 2 皮肤 × 3 | 约 8 | 0% | 森林式 | underground/creep 分支、按皮肤选图、TREE 改判 |
| 9 | Sandworm Lair（已实现，未打包） | 7 | 2 × 4/2 | 3（已制作） | 核准身份全覆盖，特殊格原生 | 森林式独立沙族＋16 掩码 | 18 次原生 DIG 修复；350×20 全图 CPU 0.371 秒 |
| 10 | **Scintillating Caves（已实现，未打包）** | 1 | 2 × 3/5 | 3（已制作，40 张运行图） | 受支持身份实机回退 0 | `crystal.lua` 精确来源＋晶墙 16 掩码 | 11,930/11,930；返工后 L1 自然 FOV 明度、全图调色及密室边界已验 |
| 11 | Unremarkable Cave（已实现，未打包） | 25 | 1 × 1 | 3（已制作，58 张运行图） | 本区受支持身份回退 0 | `cave.lua` 来源＋独立洞墙 16 掩码 | 14,997/14,997；静态／生成区接缝、DIG 与渲染帧明度已验 |
| 12 | Ancient Elven Ruins | 43 | 1 × 3 | 0–1（借用 Maze） | 约 80% | Kor'Pul | 与 Maze 共享 OLD_* 扩展 |

## 推荐：前两个套件

**第一套：Old Forest（DEFAULT 与 CRYSTALINE 两种布局，L1–L4）。**
- 零新美术、零导出器工作：身份完全落在已验收的 `grass/tree-*/tree-hard/exit` 族上，F1 刚把 `hardtree` 独立出来，正好用上。
- 运行时改动最小，限于 `applyForest` 的门控和草地分支接受 `dark_grass`，风险可控，也能先把“森林适配器多区域化”的门控结构理顺，为 Norgos、Daikara、Heart of the Gloom 的 subtype 分支打底。
- 暴露面大：level 7–16，是 Trollmire/Kor'Pul 之后的常规路线；原生外观也与 Trollmire 同源，棋盘语言连续。
- 同一批可以顺手加入 Slazish Fens（零美术，只改门控），但它只在东部开局出现，建议作为附带项，不单独算一个套件。
- 验收要点：两种布局各测 L1 和 L4；LAKE_NUR 保持原生；`dark_grass` 别名只在门控内的地城生效，**Heart of the Gloom 的 `dark_grass` TREE 不得被误伤**。

**第二套：Rhaloren Camp（DEFAULT 与 OVERGROUND 两种布局，L1–L3 加共用静态图 `rhaloren-camp-last`）。**
- 同样零新美术：DEFAULT 全部是原版 basic.lua，可直接复用 Kor'Pul 石头组；OVERGROUND 由 Kor'Pul 建筑和森林户外拼成。
- tier1、level 1–7，与已支持的两个地城同属早期，而且 PLAN.md 的 E3 怪物批次正好在做 Rhaloren 精灵，地形与怪物可以同一版本交付。
- 它迫使我们实现**同层双适配器调度**，这是 Maze、Daikara 密室和 Ancient Elven Ruins 的共同前置。用一个零美术的地城去验证这项架构，风险最低、收益最大。
- 代价：调度层是真正的运行时改动，需要把 `M.apply`/`Map.lua:6` 的“二选一”改为逐格“Kor'Pul 优先，未命中再由森林补位”，并确保模式切换和原生回退两条路径都覆盖。如果本轮不想碰架构，**备选是 Dreadfell**（只需扩 `M.variant`，零美术），但它从 level 15 起、有 9 层、墓穴风格待定，暴露面和性价比都不如 Rhaloren。

**第一个真正需要新美术的套件**，建议放在上面两项之后，做“雪岩”族（Norgos 全部，再延伸到 Daikara 的非熔岩部分）：一套 3 件左右的母版覆盖两个地城，可沿用 `export_forest_terrain.c` 的“地板加透明构件”管线。
