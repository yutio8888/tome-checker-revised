# 森林精修地形回退：诊断与下一轮计划

2026-09-27 立项，**排入下一轮工作**，本轮不修改任何运行代码。

> 2026-09-28 更新：方案 A 已实现并实机验证，见 [evidence/terrain-repair-20260928](../../evidence/terrain-repair-20260928/README.md)。方案 B 仍待 G0。

本文记录已核对的根因与证据，供下一轮直接接手；不要重新推导。截图取证与夹具实测由上一轮分析提供，代码断言与像素数据由主代理独立复核。

## 一、两类现象，成因不同

| 现象 | 真实身份 | 性质 |
| --- | --- | --- |
| 大片纯棕色平格 | 插件自己的 `refined/road0.png` / `road1.png` | **不是丢图**。当前道路素材就是近乎无颗粒的平涂泥面 |
| 亮绿、带草叶的格 | 原生 `shockbolt/terrain/grass.png` | **真回退**：精修替换被原生 nice-tiler 重铺格时丢掉 |

## 二、根因：森林走"装一次"的全图实现，被原生重铺覆盖

1. `hooks/load.lua` 只绑定两个时机：`Game:changeLevel` 与 `ToME:runDone`。
2. `ToME:runDone` 的触发点在 `game/modules/tome/class/Game.lua:96-98` 的 `Game:run()`，是**每次游戏启动／读档一次**，不是每回合。因此一旦丢格，**层内永久**，直到换层或重载才恢复。
3. `CheckerTerrain.M.apply`（`overload/mod/class/CheckerTerrain.lua:338-346`）分叉：
   - `M.variant(zone)` 非空（**只有 `ruins-kor-pul`**，见 `:172-176`）→ 走逐格适配器，直接 return；
   - 其余（含 Trollmire）→ 走 `applyForest`（`:49-81`）全图扫描，给每格挂 `replace_display` + `_checker_terrain`。
4. 原生 `NicerTiles:updateAround`（`game/modules/tome/class/NicerTiles.lua:**243**`）对 3×3 邻域重跑 `handle` + `replaceAll`（`:107`），后者用 `level.map(i,j,TERRAIN,<新实体>)` **替换 Grid 对象**。
5. `superload/engine/Map.lua` 的 `active()` 依赖 `Terrain.variant`，因此逐格适配器**只对 Kor'Pul 生效**，森林没有自愈路径。

### 丢失不是全称的（重要）

`replaceAll` 有两条路径，务必区分，否则下一轮容易改错位置：

- **`repl` 路径**：`level.map(r[1],r[2],TERRAIN,no)`，`no` 来自 `handle` 新建实体 → **必丢**。
- **`edits` 路径**：有 `__nice_tile_base` 时 `doclone(base)` → 丢；无 `__nice_tile_base` 时 `doclone(g)` 会把 `replace_display` 与 `_checker_terrain` 一起深拷贝，且同一次 clone 内引用保持一致，`applyForest` 的 `foreign` 检查（`g.replace_display~=state.display`）不会判其外来 → **可能存活**。

### `updateAround` 调用点

全模块约 90 处。运行时常见触发：`data/damage_types.lua:1952`（DIG）、`data/talents/spells/earth.lua:239`、`data/talents/celestial/twilight.lua:141/326`（Jumpgate），以及 **`class/Grid.lua:115`（`on_block_change`，踩格变形）**。`class/Zone.lua:115` 在关卡生成阶段批量调用，早于 `applyForest`，无害。

## 三、已验证证据

像素（主代理实测，PIL）：

| 素材 | 均值 RGB | 备注 |
| --- | --- | --- |
| `refined/grass0` | (109.8, 116.0, 70.8) | 蓝通道≈71 |
| `refined/grass1` | (98.3, 103.8, 63.3) | |
| `refined/road0` | (132.1, 111.0, 75.6) | 通道 std 仅 R4.3 / G3.7 / B2.9 |
| `refined/road1` | (118.3, 99.4, 67.7) | |
| 原生 `terrain/grass.png` | (85.2, 102.6, **0.2**) | 蓝通道≈0 |

扫描插件 `data/gfx/**` 全部 **1956** 张 PNG，满足 `B<25 且 G>90` 的：**0 张**。故截图中的亮绿格不可能是插件素材。

夹具实测（上一轮分析提供，本轮未重跑）：全新 Trollmire 进图为 2375/2375 全精修；一次 `updateAround` 使玩家 3×3 邻域 5 格退回原生（3 草斑 + 1 树 + 1 道路）；手动重跑 `checkerApplySettings()` 立即恢复 2375/2375。

## 四、道路观感：是过渡素材，不是缺陷

- `GRASS_ROAD_DIRT`（`data/general/grids/forest.lua:137-145`，`road="dirt"`、subtype `grass`）经 `CheckerTerrain.terrain()` 归为 `road`，逐格填同一张平土面。
- `demo/checkerboard-v3/README.md` 0.3.3 已记录该决定，并声明"保留与草地一致的格线和明暗交替"。实际渲染确认**奇偶交替存在**（`(x+y)%2` 切 road0/road1）。
- 真正缺的是**纹理**：grass 有斑驳颗粒，road 近乎平涂（std≈4 对 ≈7），这才是被误认为占位图的原因。
- `docs/repaint-plan-20260927/terrain-backlog.csv` 的 G0 `road` 条目已列为待替换母版："完整格位的压实泥纹；共享格边；不加宽"。

**结论：不要"补格线"，要补压实泥纹理。** 这项属于 G0 地形轮，不属于回退修复。

## 五、修复方案与前置条件

### 方案 A（止血，建议下一轮先做）

超载 `NicerTiles:updateAround`，在原生调用后**只对被触碰的 3×3 重铺**精修。

- 不要整图重跑 `applyForest`：2375 格的图上每次挖掘跑一遍不可接受。
- 必须实测 `postProcessLevelTilesOnLoad`（全图重铺）与 `ToME:runDone` 的先后顺序，不要假定。
- 新增 `superload/mod/class/NicerTiles.lua`，与现有 superload 布局一致。

### 方案 B（正解，按新增地形套件量级排期）

把森林从 `replace_display` 迁到 Kor'Pul 的逐格适配器（`Map:updateMap` 观察 + `Grid:getMapObjects` 同步绘制）。

**硬前置（原分析未提）**：逐格适配器依赖 `M.classify` → `_checker_grid_source` 戳记，而戳记目前只覆盖一个身份：

```lua
-- superload/mod/class/Grid.lua:7
if file=='/data/general/grids/basic.lua' then ... Terrain.markSource(...) end
-- overload/mod/class/CheckerTerrain.lua:130-131
local source='/data/general/grids/basic.lua'
local identities={FLOOR='floor'}
```

森林格来自 `/data/general/grids/forest.lua`。走方案 B 必须先把 `markSource` 白名单与 `identities` 扩到 tree / grass / flower / road / deep / bog 全套，并为每类重新确立显示合同。**按"新增一个地形套件"估工，不是"迁移"。**

## 六、下一轮建议顺序

1. 方案 A 局部重铺止血，覆盖挖掘、地系技能、Jumpgate 三类触发，48/64/96 三档地格验证。
2. 方案 B 与 `markSource` 白名单扩展，并入 G0 森林地形轮；道路压实泥纹理同批处理。

## 七、边界与未确认项

- 未能确定用户那一局究竟由哪次原生重铺触发（挖树／地系技能／区域事件均可能）；机制已在夹具确定性复现，但具体触发源未定位。
- 夹具复现用 64px 地格，用户截图为 96px。机制无关地格尺寸，但严格意义上未做同条件复现。
- `docs/p1-korpul/TERRAIN-CONTRACT.md` 已自述："Existing Trollmire installation/restoration remains the previous implementation, including its existing limitations"。本文不改变该合同，只记录待办。
- FLOWER 格在夹具中确认被正确精修，亮绿格不是花草格特例。
