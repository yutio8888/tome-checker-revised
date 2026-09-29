# F1：泛滥（FLOODED）Trollmire 地形 — 出图前简报（仅预演，未生图）

2026-09-28。配套 [docs/g0-terrain-contract-20260927/CONTRACT.md](../../docs/g0-terrain-contract-20260927/CONTRACT.md)（§3、§8 表）、[ACCEPTANCE.md](../../docs/g0-terrain-contract-20260927/ACCEPTANCE.md)（A7/A8/B1/B6）、[EXPORTER.md](../../docs/g0-terrain-contract-20260927/EXPORTER.md)（母版命名、F1 占位验证）、[docs/expansion-plan-20260928/PLAN.md](../../docs/expansion-plan-20260928/PLAN.md) F1 节。

**本轮没有调用 ImageGen，没有 `--execute`，没有改动 `data/gfx` 或任何运行时 Lua，没有提交。** 全部任务包已 `prepare` 并跑过 `run_imagegen.py status`／不带 `--execute` 的 `generate` 预演，提示词汇总见 [DRYRUN.md](DRYRUN.md)。主代理应先读完本文件与 DRYRUN.md 再决定是否放行任何一张的真实生成。

## 0. 范围与身份来源

FLOODED 布局相对 DEFAULT 新增的三个地形身份，全部来自 `game/modules/tome/data/zones/trollmire/grids.lua`：`BOGTREE`（:45-74）、`BOGWATER`（:76-80）、`BOGWATER_MISC`1..7（:82-86）。另外按本任务要求核对了 `HARDTREE`（`game/modules/tome/data/general/grids/forest.lua:79-95`），因为它虽不是泛滥专属，但在 Trollmire 第 4 层静态宝藏图（两种布局共用，FLOODED 玩家同样会走到）里占了约 200 格墙体。

## 1. 逐身份美术需求

### 1.1 `BOGTREE`（柳树，站在水里）

原生规则（`grids.lua:45-58`）：`does_block_move=true`、`can_pass={pass_tree=1}`（仅 `pass_tree>=1` 的行动者能穿过，与普通 `TREE` 门槛相同）、`block_sight=true`、**不挡感知/ESP**（未设 `block_sense`/`block_esp`）、`dig="BOGWATER"`（可挖成沼泽水）、`shader="water"`（显示层信息，会被 `replace_display` 丢失，必须由母版本身画出水线效果来补回，对应 CONTRACT I9）、无 `air_level`，不是危险格。

与普通树的关键差异：**底地是水不是草**（`subtype="water"`），且柳树家族（willow/small_willow/带 moss 变体）原生只属于 `BOGTREE`，不再用于非泛滥的 `TREE`（`forest.lua` 的 `treesdef` 里没有 willow）。因此柳树造型本身已经是与 oak/pine/cypress 区分开的家族，不需要额外发明剪影差异，只需要让底部露出水线／涟漪，证明它站在水里而不是草地上。

**产出**：2 个 `bog-tree` 变体（复用原生自身的多样性口径——原生 `BOGTREE1..20` 本来就在 bare/spring 两种 foliage 与是否带 moss 之间循环取样，见 `grids.lua:60-73`）：
- `bog-tree-a`：稀疏光秃（`small_willow`+`foliage_bare`，对应 `grids.lua:61`）。
- `bog-tree-b`：茂密带苔（`small_willow_moss`+`foliage_spring`，对应 `grids.lua:66`）。

风格锚点：`art/terrain-forest-v1/masters-derived/prop-tree-willow.png`（已验证过导出管线的柳树透明构件母版）。身份参考：原生 `terrain/trees/willow_waterripples.png`（水线／涟漪部件，柳树独有，普通树没有）及对应 foliage 部件。

导出：`prop-bog-tree` 系列母版，由 `tools/export_forest_terrain.c`（已实现，见 EXPORTER.md）叠加在 **`bog-water` 掩码地板**之上而不是草地——这是它比普通树贵的原因（CONTRACT §8 硬约束 2）。命名 `bog-tree<mask>-<parity>-0.png`，16 掩码 × 2 奇偶，两个风格变体由导出器按格位确定性选择（同 `CheckerTerrain.lua:43` 现有做法）。

### 1.2 `BOGWATER`（沼泽水地板）— 复用决定

**决定：复用现有 64 张 `data/gfx/refined/bog*`／`deep*`（含四方向岸贴），不新画地板母版。**

依据：
- ACCEPTANCE A4（棋盘奇偶）、A5（掩码位局部性）、A6（接缝连续性）、A7（岸的存在性）已在 CONTRACT §7 与 EXPORTER.md §3 用像素实测核对过现有 78 张在用瓦片（含 `bog0..15`），全部通过，且 EXPORTER.md 用独立复现的导出器重新跑过一遍同样通过（A4 median 0.8939–0.8952，A5 全掩码 `max|ΔRGB|=0`，A6 比值 1.24–1.27，均在阈值内）。
- 本轮为完成 ACCEPTANCE §9.3 点名"下一轮补齐"的 B6（危险语义可辨识）做了一次数值代理核验：见 `review/bog-vs-deep-vs-poison-96.png`（5 张 96px 缩略对照：`deep0`/`deep15`/`bog0`/`bog15`/原生 `poisoned_water_01`，未纳入本批生成范围，仅作对照）。
  - 中心亮度：`deep` 系 L≈59.7（更暗、更沉），`bog` 系 L≈103.4（明显更亮），符合"深水危险、沼泽水无害"的明暗直觉。
  - 中心 RGB：`deep`≈(27,62,69) 冷暗蓝绿；`bog`≈(86,116,92) 浅灰绿；原生毒水 `poisoned_water_01`≈(67,72,51) 偏黄绿。`bog` 比毒水更蓝、更亮、饱和度更低，数值上不像"毒绿冒泡"那种读法，但**这只是数值代理，不能替代 ACCEPTANCE B6 要求的实际 64px 并排人工判定**（把棋子放进两片水域里看）。请主代理在批准复用前至少扫一眼这张对照图，必要时再补一次真正的 B1/B6 人工看图。
- 复用意味着 F1 这一层**不产生任何新的地板生成任务**，`bog-water` 不在本批 `art_tasks.py` 任务包内。

### 1.3 `BOGWATER_MISC`1..7（水面装饰）

原生规则（`grids.lua:82-86`）：`base="BOGWATER"`，除一层 `add_displays`（`terrain/misc_bog{1..7}.png`）外**没有任何字段差异**——不挡移动、不挡视线、不挡感知/ESP、无危险、无交互回调。纯装饰。

实地查看 7 张原生图（`data/gfx/shockbolt/terrain/misc_bog{1..7}.png`，64×64）后分为三组：
- `misc_bog1`/`misc_bog2`：稀疏浅色芦苇/草茎丛。
- `misc_bog3`/`misc_bog4`：更密的橄榄绿苔藓/草丛团块。
- `misc_bog5`/`misc_bog6`/`misc_bog7`：漂浮的深色枯枝/浮木碎段。

按 CONTRACT §9.4（同族规则完全相同，允许一张母版覆盖多个原生装饰）与本任务给的变体上限，出 **3 个 `bog-misc` 变体**，每个代表一组：
- `bog-misc-1`：芦苇丛（对应 `misc_bog1`+`misc_bog2`）。
- `bog-misc-2`：苔藓/草团（对应 `misc_bog3`+`misc_bog4`）。
- `bog-misc-3`：浮木（对应 `misc_bog5`+`misc_bog6`；`misc_bog7` 未单独覆盖，留给导出器的三选一选择器兜底，不额外加母版）。

**必须遵守的约束**（AGENTS.md 地形铁律 + ACCEPTANCE B1）：装饰不能暗示阻挡或移动加成。三个变体各自的提示词都写明"纯装饰、不得画出发光/冒泡/尖刺/毒色暗示"；`bog-misc-3`（浮木）额外写明**不得画成贯穿格子两端的直木板**，否则会被误读成一条本身不存在的过桥通道——这是我认为最需要主代理重点看图的一条，已经在批次 JSON 的 `gate_reason` 与 DRYRUN.md 的"需要重点核查"里单独标出。

风格锚点用 `prop-exit.png`（同为"贴在地板上的小型透明构件"的构图参照，不借用其身份），身份参考用对应的原生 `misc_bogN.png`。

导出：`prop-bog-misc-{1,2,3}` 命名直接沿用 EXPORTER.md §4 已经拿占位母版跑通过的同一套命名（该文档验证过"多变体×奇偶"命名机制），叠加在 `bog-water` 地板上，不依赖掩码（浮在水面，不像 `bog-tree` 要求底地随掩码）。

### 1.4 `HARDTREE`（非泛滥专属，但纳入本次核查）

读 `forest.lua:61-95` 逐字段核对：`TREE` 有 `can_pass={pass_tree=1}`（:68）与 `dig="GRASS"`（:71）；`HARDTREE`**完全没有 `can_pass` 表**（:79-92 全段无该字段，`Grid.lua:95-100` 的门槛判断整段跳过，意味着无论行动者自身 `can_pass` 是什么值都过不去，不是"门槛更高"而是"该分支完全不生效"）、**没有 `dig`**（不可挖）、且额外设了 `block_sense=true`／`block_esp=true`（:88-89），`TREE` 两者都没有。

**结论：规则确实不同，且差异不小（不可挖 + 挡感知/ESP + `pass_tree` 完全失效），不能按"规则相同、跳过"处理。** 但原生美术对 `TREE`/`HARDTREE` 用的是同一份 `treesdef`（`forest.lua:44-59`，两处 `makeNewTrees` 调用参数完全相同），也就是说**原生没有任何可复制的"硬树专属"图源**——这正是 CONTRACT I1 记录的缺陷本体。

`HARDTREE` 按 CONTRACT §9.1 属于 G0 T1（非泛滥规则缺口）批次的母版 #4，不是泛滥专属身份。放进本次 F1 简报，是因为任务明确要求核查它，且它在 Trollmire 第 4 层静态宝藏图（`data/maps/zones/trollmire-treasure.lua:27`，两种布局共用同一张图）里占了约 200 格、是全图墙体的绝大部分（EXPORTER.md §5 已核实该层完全没有 `BOGTREE`/`BOGWATER`/`BOGWATER_MISC`，纯陆地地形）。

**产出**：1 个 `hardtree` 变体——更粗壮扭曲的单一主干、更密实不透光的暗色树冠，在 48px 灰度下要比 oak/pine/cypress 三款普通树明显更"重"（剪影+明度两维差异，满足 README"同族至少两维不同"）。风格锚点用 `prop-tree-oak.png`；身份参考用原生 `oak_trunk_01.png`——**特意用它来记录"原生没有专属素材"这一事实**，不是当作要复刻的目标。

主代理若已排期独立的 G0 T1 批次，请协调避免为同一个 `hardtree` 身份重复出图；本包可以直接被 T1 复用或作废重排。

## 2. 任务包与路径

| 批次 JSON | 交接目录 | 资产 | 张数 |
| --- | --- | --- | --- |
| `art/production/batches/f1-flooded-trees-v1.json` | `art/production/handoffs/f1-flooded-v1/trees/` | `bog-tree-a`、`bog-tree-b`、`hardtree` | 3 |
| `art/production/batches/f1-flooded-bog-misc-v1.json` | `art/production/handoffs/f1-flooded-v1/bog-misc/` | `bog-misc-1`、`bog-misc-2`、`bog-misc-3` | 3 |

两包均已 `python3 tools/art_tasks.py prepare` 通过（`"ready": 3, "hold": 0`），每个资产都用 `python3 tools/run_imagegen.py status <pack>` 核对过 `calls_used: 0`，并用不带 `--execute` 的 `generate --saved art/terrain-f1-flooded/masters/<id>-v1.png` 跑过预演（全部返回 `"mode": "dry-run"`，未创建 `masters/` 目录、未消耗任何额度）。完整提示词与需要重点核查的三条见 [DRYRUN.md](DRYRUN.md)。

`bog-water` 地板不在任何任务包内——按 §1.2 的复用决定，本轮不为它准备生成任务。

## 3. 调用预算

6 个资产 × `max_attempts=2` = **上限 12 次调用**（每款都返修一次的最坏情况）。若全部一次通过，只需 **6 次**。两个任务包各 ≤4 项，符合 README 的批次上限。

## 4. 待主代理确认后才能做的事

1. 打开 `art/production/handoffs/f1-flooded-v1/{trees,bog-misc}/<asset>/prompt.txt` 逐条审阅（与 DRYRUN.md 内容一致，DRYRUN.md 只是汇总副本）。
2. 决定是否接受 `bog-water`/`deep-water` 复用决定，或要求先做一次真正的人工 64px 并排评审（B1/B6）。
3. 确认是否要为 `hardtree` 单独走 G0 T1 批次而不是挂在本 F1 包下；若维持现状，本包可直接放行。
4. 批准后再对逐个资产运行 `python3 tools/run_imagegen.py generate <pack> --saved ... --execute`，每次调用后照常走 `record`/`repair`/门控流程——本任务未做，也不应由本次交付默认放行。
