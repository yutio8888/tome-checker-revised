# G0 森林水域：规则核对与地形契约

2026-09-27。本轮是**只读源码核对**，没有生成任何美术、没有改动任何运行代码、没有启动游戏。产出供下一轮直接照做。

配套文档：[验收判据](ACCEPTANCE.md)。

引用约定：`game/modules/tome/...` 与 `game/engines/default/...` 为原生路径，其余为本插件相对路径。行号为核对当日实测。

## 0. 纪律与本文的边界

- **通行、视线、危险三者分开记录**，任何一格都不写成"能不能走"。另外单列**感知/ESP**与**投射物**，因为原生确实把它们与视线分开实现。
- **每条结论都有源码依据**。没有源码依据的写"未确认"，不补全。
- 不凭颜色、不凭名字推断规则。名字在原生里**会重复**（见 §1.3、§2.4），本文把"名字"只当线索，不当身份。
- [森林精修回退问题](../terrain-fallback-20260927/FINDINGS.md)本轮不修。但本契约的导出/母版设计已按"迟早要迁到逐格适配器"来写：所有母版都是**单格完整合成**的输入，不依赖 `replace_display` 这条特定安装路径。

---

## 1. 普通树 vs 硬树

### 1.1 Trollmire 实际会出现的树

| grid | 定义 | type/subtype | 通行 | 视线 | 感知/ESP | 可挖 | 危险 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `TREE` + `TREE1..30` | `data/general/grids/forest.lua:61-77` | wall / grass | `does_block_move=true`；`can_pass={pass_tree=1}`（:68）→ 自身 `can_pass.pass_tree>=1` 的行动者可穿 | `block_sight=true`（:70） | **不挡**（未设 `block_sense`/`block_esp`） | `dig="GRASS"`（:71） | 无 |
| `HARDTREE` + `HARDTREE1..30` | `forest.lua:79-95` | wall / grass | `does_block_move=true`（:86）；**无 `can_pass`** → `pass_tree` 无效 | `block_sight=true`（:87） | `block_sense=true`、`block_esp=true`（:88-89） | **无 `dig` → 不可挖** | 无 |
| `BOGTREE` + `BOGTREE1..20` | `data/zones/trollmire/grids.lua:45-74` | wall / **water** | `does_block_move=true`（:53）；`can_pass={pass_tree=1}`（:52） | `block_sight=true`（:54） | **不挡** | `dig="BOGWATER"`（:55） | **无 `air_level` → 不窒息** |

`can_pass` 的判定在 `modules/tome/class/Grid.lua:95-100`：`if self.can_pass[what] and self.can_pass[what] <= check then return false end`，`check` 取自行动者自身的 `can_pass`。所以 `pass_tree=1` 是"门槛 1"，不是"允许通过"的布尔。`HARDTREE` 没有 `can_pass` 表，这条分支整段跳过。

`makeNewTrees`（`forest.lua:76`、`:94`）对 `TREE` 和 `HARDTREE` 传入**同一个 `treesdef`**（`:44-59`），所以两者的原生美术素材完全一样，原生只靠 `nice_tiler` 的贴图池区分不了它们——**硬树在原生里本来就和普通树长得一样**。这不是本插件要复刻的缺陷；桌游语言下必须把"不可挖、挡感知"的硬树画成看得出来的另一种物件。

`treesdef`（`forest.lua:44-59`）的家族只有四类：`small_elm`/`elm`、`light_pine`/`light_small_wider_pine`/`light_small_narrow_pine`、`cypress`/`small_cypress`/`tiny_cypress`、`oak`/`small_oak`。**没有 willow**。willow 只出现在 `BOGTREE`（`trollmire/grids.lua:60-73`）。

### 1.2 硬树在 Trollmire 是否真的可达 —— 是

不是理论漏洞，四处实证：

- `data/maps/vaults/honey_glade.lua:37` `defineTile('#', "HARDTREE")`（`honey_glade` 在两个布局的 `lesser_vaults_list` 里，`zone.lua:66` / `:194`）
- `data/maps/vaults/forest-ruined-building1.lua:33`
- `data/maps/vaults/forest-ruined-building3.lua:42`
- `data/maps/zones/trollmire-treasure.lua:27` `defineTile("t", "HARDTREE")` —— 第四层宝藏图**整圈边界**都是硬树

同图还有 `ROCK_VAULT`（`honey_glade.lua:35`、`trollmire-treasure.lua:29`），见 §5.3。

### 1.3 现有实现漏掉了什么

`overload/mod/class/CheckerTerrain.lua:14`：

```lua
if g.name=='tree' or g.name=='tall thick tree' then return 'tree' end
```

- **两者合并成同一个渲染身份**，随后 `:43` 用 `(x*17+y*7)%3` 从 `tree-oak` / `tree-pine` / `tree-willow` 里挑一张。硬树被画成随机一棵普通树。这正是 PLAN 第 3 节"普通/硬树区分不足"的实体。
- 过滤靠 `g.subtype=='grass'`（`:11`）。`data/zones/trollmire/grids.lua:22` 把 `autumn_forest.lua` 也 load 进了本区 grid_list，其中 `HARDAUTUMN_TREE`（`autumn_forest.lua:57-71`）的 `name` **同样是 `"tall thick tree"`**，只因 `subtype="autumn_grass"` 才被挡在外面。也就是说现在挡住它靠的是 subtype 巧合，不是身份校验。
- `BOGTREE` 的 `subtype="water"`（`trollmire/grids.lua:47`），`name="tree"`。它走不到 grass 分支，又不匹配 `:20` 的两个水名，所以返回 nil → 原生。当前 FLOODED 整区原生（`:52`），这条没有实际影响；但支持 FLOODED 时必须显式加身份，**不能靠把 `subtype=='water'` 放宽**。

**结论**：树类渲染身份应为 4 个而不是 1 个：`tree-broadleaf`、`tree-pine`、`tree-cypress`（三者共享 `TREE` 的规则）、`hardtree`（`HARDTREE`），FLOODED 再加 `bog-tree`（`BOGTREE`）。

---

## 2. 深水 / 沼泽水

### 2.1 原生规则

| grid | 定义 | type/subtype | 通行 | 视线 | 危险 | on_stand | 备注 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `WATER_BASE` | `data/general/grids/water.lua:122-130` | floor / water | 不挡 | 不挡 | **无 `air_level`** | 无 | `name="deep water"`、`shader="water"`、`special_minimap=BLUE`、`always_remember`。是模板，通常不直接放置 |
| `DEEP_WATER` | `water.lua:136-140` | floor / water | 不挡 | 不挡 | `air_level=-5`、`air_condition="water"` | 无 | Trollmire DEFAULT 的池塘（`zone.lua:189`） |
| `DEEP_OCEAN_WATER` | `water.lua:146-150` | floor / water | 不挡 | 不挡 | `air_level=-5`、`air_condition="water"` | 无 | **`name` 同样是 `"deep water"`**，只是 image 不同 |
| `BOGWATER` | `data/zones/trollmire/grids.lua:76-80` | floor / water | 不挡 | 不挡 | **无 `air_level` → 不窒息、无伤害** | 无 | 继承 `WATER_BASE`，只改 `name="bog water"` 和 image |
| `BOGWATER_MISC` + `1..7` | `trollmire/grids.lua:82-86` | 同上 | 同上 | 同上 | 同上 | 无 | 只多一层 `add_displays`（`misc_bog1..7.png`） |
| `POISON_DEEP_WATER` + `1..6` | `water.lua:156-180` | floor / water | 不挡 | 不挡 | `air_level=-5` **加** `on_stand` 施加 POISON 伤害（`:169-175`，`mindam/maxdam` 由 `resolvers.mbonus` 决定） | **有** | `name="poisoned deep water"` |
| `WATER_FLOOR_BUBBLE` | `water.lua:98-116` | floor / water | 不挡 | 不挡 | `air_level=+15`（**回气**） | **有**（消耗 charges 后变回 `WATER_FLOOR`） | Trollmire 不用 |

**窒息机制的唯一入口**是 `modules/tome/class/Actor.lua:628-634`：

```lua
local air_level, air_condition = game.level.map:checkEntity(self.x, self.y, Map.TERRAIN, "air_level"), ...
if air_level then
  if not air_condition or not self.can_breath[air_condition] or self.can_breath[air_condition] <= 0 then
    self.is_suffocating = true
    self:suffocate(-air_level, self, air_condition == "water" and _t"drowned to death" or nil)
```

所以：

- **深水的危险 = 每 base turn 对不会水下呼吸的行动者 `suffocate(5)`**，死亡文案 "drowned to death"。不是伤害地格，不是陷阱。
- **沼泽水没有任何危险**。它和草地在通行、视线、危险三项上**完全等价**，差别只有外观、`special_minimap` 和 `always_remember`。
- 另有一条独立门槛在 `Grid.lua:103-109`：还没放上地图的行动者（`e.__is_actor and not e.x`）不能被放进会窒息的格。这是生成期约束，不是玩家移动规则。

### 2.2 现有实现的准确性

`CheckerTerrain.lua:20-21`：

```lua
elseif g.subtype=='water' and (g.name=='deep water' or g.name=='bog water') then
 return (g.air_level and g.air_level<0) and 'deep' or 'bog'
```

对 Trollmire 实际放置的两个 grid（`DEEP_WATER`、`BOGWATER`/`BOGWATER_MISC`）**判定结果正确**。但它是**按属性猜身份**，不是身份校验，有三处已确认的错判：

1. `DEEP_OCEAN_WATER`（`water.lua:146-150`）名字同为 `"deep water"`、`air_level=-5` → 被判为 `deep`，套用 Trollmire 的深水美术。
2. `WATER_BASE`（`water.lua:122-130`）名字同为 `"deep water"`、**无** `air_level` → 被判为 `bog`。
3. 任何第三方插件或后续区域新建的、名字撞上这两个字符串的 grid，都会直接被接管。

当前 `applyForest` 只在 `zone.short_name=='trollmire'` 且非泛滥时才真正上色（`:52`），所以 1/2/3 都不会发生在实机。**但这套判据与 Kor'Pul 的 `markSource` + `signature` 身份校验（`:167-217`）不是一个等级**，把森林迁到逐格适配器时必须换掉（回退文档 §五·方案 B 已点到 `markSource` 白名单只覆盖 `basic.lua`）。

另有一条：`POISON_DEEP_WATER` 因为名字不匹配而落回原生——这是**正确**的行为，下一轮不要"顺手"把它并进来。毒水有 `on_stand` 伤害，是第三类危险，必须单独立合同。

### 2.3 水的邻接掩码不区分水种

`CheckerTerrain.lua:26-33` 的 `waterMask` 把 `deep` 和 `bog` 都计为"有水"。Trollmire DEFAULT 只有深水、FLOODED 只有沼泽水，当前无影响。**一旦同图混用就会出现深水瓦片与沼泽水瓦片直接拼边**。掩码语义必须在契约里写死为"同种水"，见 §6。

越界邻居：`engine/Map.lua:559-560` 对越界返回 nil，所以地图边缘的水格会在朝图外的一侧画岸。这是既有行为，记录备查。

---

## 3. FLOODED 布局

### 3.1 与 DEFAULT 的生成器差集

两个布局是 `data/zones/trollmire/zone.lua` 里的两段独立返回（FLOODED `:22-150`，DEFAULT `:152-278`），由 `:20` 的 `game.state:alternateZoneTier1(short_name, {"FLOODED", 1})` 选择。

| 生成器键 | FLOODED | DEFAULT | 差异 |
| --- | --- | --- | --- |
| `floor` | `FLOWER` 20% / `GRASS`（:56） | 同（:179） | 相同 |
| `floor2` | `BOGWATER_MISC` 20% / `BOGWATER`（:55） | **不存在** | FLOODED 独有 |
| `sqrt_percent2` | `25`（:53） | **不存在** | 触发 `floor2` 的门限 |
| `wall` | `BOGTREE`（:57） | `TREE`（:180） | **不同树** |
| `door` | `BOGWATER`（:60） | `GRASS`（:183） | 隧道填充格不同 |
| `do_ponds` | **不存在** | `DEEP_WATER` 池塘（:186-190） | 深水只在 DEFAULT |
| `up` / `down` | `GRASS_UP4` / `GRASS_DOWN6`（:58-59） | 同（:181-182） | 相同 |
| `road` | `GRASS_ROAD_DIRT`（:61） | 同（:184） | 相同 |
| `zoom` | `7`（:51） | `4`（:176） | 噪声尺度，不影响素材 |
| `is_flooded` | `true`（:45） | 无 | 本插件的门控依据 |
| `nicer_tiler_overlay` | `"DungeonWallsGrass"`（:46） | 无 | 见 §3.3 |
| `lesser_vaults_list` | 同一批 7 个（:66） | 同（:194） | 相同 |
| levels[1].up | `GRASS_UP_WILDERNESS`（:91） | 同（:219） | 相同 |
| levels[3] | `end_road`/`end_road_room="zones/prox"`/`force_last_stair`/`down="GRASS"`/`stew="STEW"`（:96-101） | 同（:224-228） | 相同 |
| levels[4] | 静态图 `zones/trollmire-treasure`（:104-115） | 同（:232-243） | 相同 |
| guardian | `TROLL_SHAX`（:74） | `TROLL_PROX`（:202） | 怪物，不属本轮 |

### 3.2 支持 FLOODED 需要的新地形身份

**只有三个**，全部来自 `data/zones/trollmire/grids.lua`：

1. `BOGTREE` + `BOGTREE1..20`（`:45-74`）—— willow 家族，站在水里，`subtype="water"`，`shader="water"`，底图是 `terrain/water_grass_5_1.png`。规则同普通树（挡移动、挡视线、可穿 `pass_tree`、可挖成 `BOGWATER`），**但底地是水不是草**。
2. `BOGWATER`（`:76-80`）—— 沼泽水本体。现有 `bog*` 精修瓦片已经存在（64 张，见 §5.4），但从未在实机启用过。
3. `BOGWATER_MISC` + `1..7`（`:82-86`）—— 沼泽水上的 7 种装饰（`terrain/misc_bog1..7.png`，已确认存在于 `modules/tome/data/gfx/shockbolt/terrain/`）。纯 `add_displays`，**无任何规则差异**。

DEFAULT 独有、FLOODED 不出现的：`TREE`、`DEEP_WATER`。

其余（`GRASS`、`FLOWER`、`GRASS_ROAD_DIRT`、三个出口、`STEW`、`HARDTREE`、`ROCK_VAULT`、各 lesser vault 的石质格）两个布局完全共用。

### 3.3 `nicer_tiler_overlay = "DungeonWallsGrass"`

实现在 `modules/tome/class/NicerTilesOverlays.lua:50-69`。它只在 `mode=="replace"` 且**南邻格 `subtype=="grass"`** 时生效，对花岗岩墙/门的 image 追加一层草裙 `add_mos`，并且 `g:cloneFull()` + `removeAllMOs()`。

对本轮的意义有两条：

- 它只动 vault 的石质格，不动森林格本身；森林母版不需要为它出图。
- 它会 **clone 整个 Grid**，与回退文档 §二记录的 `replaceAll` clone 路径同类。下一轮做 FLOODED 时要知道 vault 边界上的格会被换对象。

### 3.4 FLOODED 的门控现状

`CheckerTerrain.lua:52`：`local supported = self.zone and self.zone.short_name=='trollmire' and not self.zone.is_flooded`。整个 FLOODED 布局走原生，与 PLAN 记录一致。

---

## 4. 森林通路与世界出口

### 4.1 原生出口 grid 全表

`data/general/grids/forest.lua` 一共定义 **9 个** grass 出口：

| grid | 定义 | `change_level` | `change_zone` | `add_mos` | 方向语义 |
| --- | --- | ---: | --- | --- | --- |
| `GRASS_UP_WILDERNESS` | `:150-160` | **+1** | `"wilderness"` | `terrain/worldmap.png` | 无方向 |
| `GRASS_UP8` | `:162-171` | −1 | 无 | `terrain/way_next_8.png` | 8 = 北 |
| `GRASS_UP2` | `:172-181` | −1 | 无 | `way_next_2.png` | 2 = 南 |
| `GRASS_UP4` | `:182-191` | −1 | 无 | `way_next_4.png` | 4 = 西 |
| `GRASS_UP6` | `:192-201` | −1 | 无 | `way_next_6.png` | 6 = 东 |
| `GRASS_DOWN8` | `:203-212` | +1 | 无 | `way_next_8.png` | 8 = 北 |
| `GRASS_DOWN2` | `:213-222` | +1 | 无 | `way_next_2.png` | 2 = 南 |
| `GRASS_DOWN4` | `:223-232` | +1 | 无 | `way_next_4.png` | 4 = 西 |
| `GRASS_DOWN6` | `:233-242` | +1 | 无 | `way_next_6.png` | 6 = 东 |

三条必须记住的事实：

1. **`GRASS_UP_WILDERNESS` 的 `change_level` 是 +1，不是 −1**（`:157`）。它靠 `change_zone="wilderness"` 离区，`change_level` 是进入世界地图后的层号。用 `change_level` 的符号推断"上/下"会推错。
2. **UP 与 DOWN 在同一方向上使用完全相同的 `add_mos` 图**（`way_next_N.png`）。原生只用 ASCII `display`（`'<'` vs `'>'`）和 `change_level` 区分，**tiles 模式下上行口和下行口是同一张图**。
3. 三者的**通行/视线/危险都相同**：`type="floor"`、不挡移动、不挡视线、无 `air_level`、无 `on_stand`。全部 `notice=true`、`always_remember=true`。出口不是危险格，也不是阻挡格。

### 4.2 数字方向的真实含义

放置路径：`engine/generator/map/Forest.lua:271-272` → `makeStairsSides`（`Forest.lua:497-538`）。

```lua
if     sides[1] == 4 then ux, uy = 0, rng.range(0, self.map.h - 1)
elseif sides[1] == 6 then ux, uy = self.map.w - 1, ...
```

Trollmire 的 `edge_entrances = {4,6}`（`zone.lua:50` / `:175`）：**上行口固定落在西边缘 x=0，下行口固定落在东边缘 x=w−1**。搭配 `up="GRASS_UP4"`、`down="GRASS_DOWN6"`，数字**与所在边一致**——它是"这个口贴在地图哪条边上"，不是"目的地在哪个方向"。

### 4.3 Trollmire 实际只会出现 3 个出口 grid

| 层 | 上行口 | 下行口 | 依据 |
| --- | --- | --- | --- |
| 1 | `GRASS_UP_WILDERNESS`（西缘） | `GRASS_DOWN6`（东缘） | `zone.lua:91` / `:219` 覆盖 `up` |
| 2 | `GRASS_UP4`（西缘） | `GRASS_DOWN6`（东缘） | `zone.lua:58-59` / `:181-182` |
| 3 | `GRASS_UP4`（西缘） | **无** —— `down="GRASS"`，东缘放普通草地 | `zone.lua:99` / `:227`，配 `force_last_stair`（`:98`/`:226`）与 `end_road_room="zones/prox"`（`:97`/`:225`） |
| 4（宝藏，静态图） | `GRASS_UP4` | 无 | `data/maps/zones/trollmire-treasure.lua:23` |

所以 `GRASS_UP2/6/8` 与 `GRASS_DOWN2/4/8` 在 Trollmire **不可达**。要不要为它们出图，取决于 G0 是否从一开始就覆盖其他森林区（老森林、Norgos 雪林等也用同一套 `way_next_N`）。

### 4.4 现有实现

`CheckerTerrain.lua:12`：`if g.change_level or g.change_zone then return 'exit' end`，然后 `:45` 走 `file='exit'..parity` → `data/gfx/refined/exit0.png` / `exit1.png`。**一张图覆盖全部 9 个 grid**，世界出口和上下行通路视觉完全相同。这正是 PLAN 第 3 节"森林左右通路/世界出口共图"。

### 4.5 拆分所需的最小母版数

按**语义**拆，不按 grid 数量拆：

| 渲染身份 | 覆盖的 grid | 语义 | 母版 |
| --- | --- | --- | --- |
| `world-exit` | `GRASS_UP_WILDERNESS` | 离开本区 → 世界地图（`change_zone` 非空） | 1 |
| `level-passage` | `GRASS_UP{2,4,6,8}` + `GRASS_DOWN{2,4,6,8}` | 同区换层（`change_level=±1`、`change_zone` 为空） | 1 |
| 方向标记 | 上表 8 个的 `way_next_{2,4,6,8}` | 贴在哪条边 | 1（4 向） |

**最小 3 张母版**，导出 3（Trollmire 实际用到的 `world-exit` / `passage-4` / `passage-6`）× 2 奇偶 = 6 张运行件；若一并覆盖 2/8 方向则 5 × 2 = 10 张。

两个必须由样板决定、现在**不能拍板**的点：

- **方向标记能否用一张母版旋转 4 次**。`art/production/README.md` 固定规范明确写了"光照有方向的构件不可为了省图随意旋转"。可行路径是在提示词里把方向标记约束成**无方向光的平面刻记**（刻进地面的箭头槽 / 平涂漆标），使旋转合法。若样板显示旋转后仍穿帮，母版数从 1 升到 4，出口合计变成 6 张。
- **要不要在视觉上区分上行/下行**。原生不区分（§4.1 第 2 点）。区分是**增加原生没有的信息**，不改规则但改信息量，属于用户决策。默认**不做**，与原生一致；若用户要做，再加 1 张上/下标记母版。

---

## 5. 炖锅（cauldron）

### 5.1 身份

`data/zones/trollmire/grids.lua:33-41`，`define_as = "STEW"`，`name = "troll stew"`（本地化：简体"巨魔的肉汤" `data/locales/zh_hans.lua:38820`、`:40603`）。

它**不在** `data/general/grids/forest.lua` 里，是 Trollmire 区自己的 grid。

### 5.2 规则（通行 / 视线 / 危险 / 交互 分开）

| 维度 | 值 | 依据 |
| --- | --- | --- |
| type / subtype | `wall` / `grass` | `:35` |
| **通行** | `does_block_move = true`，**无 `can_pass`** → 任何 `pass_*` 都穿不过 | `:38` |
| **视线** | **不挡**。未设 `block_sight` | `:33-41` 全段无该字段 |
| 感知 / ESP | **不挡**。未设 `block_sense` / `block_esp` | 同上 |
| **投射物** | `pass_projectile = true` → 投射物与瞄准线穿过 | `:39`；判定在 `engine/Actor.lua:527,533`、`engine/Target.lua:507,523,574,583`、`engine/Projectile.lua:187,196` |
| **危险** | **无**。无 `on_stand`、无 `air_level`、无 `mindam/maxdam`、无 `DamageType` | `:33-41` |
| **交互** | **无回调**。无 `is_door`、`door_opened`、`on_dig`、`on_lever_change`、`on_block_change` | `:33-41` |

**全库只有两处引用**（`grep -rn "stew"`，排除 locales 与 png）：

- `data/rooms/zones/prox.lua:35` —— 第三层 prox 首领房的 3×3 里随机挑一格 `gen:resolve('stew')`
- `data/maps/zones/trollmire-treasure.lua:25` —— 第四层宝藏静态图的 `'='`

`zone.lua:100` / `:228` 只是把 `stew = "STEW"` 挂到 levels[3] 的 generator 数据上。没有任务钩子，没有"把锅打翻"这类事件。

### 5.3 归类：透明构件

原生写法是 `image = "terrain/grass.png"` **加** `add_mos = {{image="terrain/troll_stew.png"}}`（`:36`），即**草地地板 + 锅构件**两层。

所以本插件的母版必须是**带原生 alpha 的透明锅**，由导出器叠在草地母版上合成为单格运行件。不是地板。

顺带记录两个**当前回退正确、不要误改**的相邻格：

- `STEW` 走 `CheckerTerrain.lua:13-16`：`subtype=='grass'` 成立、`does_block_move` 为真、名字不是两种树 → `return`（nil）→ 原生。
- `ROCK_VAULT`（`forest.lua:108-123`，"huge loose rock"）**没有** `does_block_move`（它靠 `is_door=true` + `Grid:block_move` 的开门路径 `Grid.lua:60-90` 来挡人），所以它掉到 `:17-19`，三个名字判断都不中 → nil → 原生。它挡视线/感知/ESP（`:116-118`）、`dig="GRASS"`（`:121`）、有 `door_player_check` 弹窗（`:119`）。**它是交互件不是普通墙**，G0 不出图。

---

## 6. 与现有 `CheckerTerrain.lua` 不一致之处汇总

按严重度排序。全部**只是记录**，本轮不改代码。

| # | 位置 | 现象 | 证据 |
| --- | --- | --- | --- |
| I1 | `:14` | 普通树与硬树合并成一个渲染身份，硬树被画成随机普通树 | §1.1 / §1.2；硬树在 Trollmire 四处可达 |
| I2 | `:43` | 非泛滥森林用 `tree-willow`，但原生 `treesdef`（`forest.lua:44-59`）**没有 willow**，willow 只属于 `BOGTREE` | §1.1 |
| I3 | `:12` | 9 个出口 grid 合并成一张 `exit` 图 | §4.1 / §4.4 |
| I4 | `:20-21` | 水身份靠 `name` + `air_level` 符号猜，不是身份校验；`DEEP_OCEAN_WATER` 会被误判为 `deep`，`WATER_BASE` 会被误判为 `bog` | §2.2 |
| I5 | `:17` | `if g.road then` 对 `road="dirt"` 与 `road="oldstone"`（`forest.lua:128-136`）同样返回 `road`。Trollmire 只用 dirt，判据应收紧为 `g.road=='dirt'` | `forest.lua:130`、`:139` |
| I6 | `:18` | `g.name=='flower'` 同时覆盖 `FLOWER1..6`（花）与 `FLOWER7..13`（蘑菇，`forest.lua:106`）。**无规则差异**，纯视觉 | `forest.lua:103,106` |
| I7 | `:26-33` | `waterMask` 把 deep 与 bog 都当"有水"，不区分水种 | §2.3 |
| I8 | `:44` | 水路径末尾恒为 `-0`，`deep<m>-<p>-1.png` / `bog<m>-<p>-1.png` 共 **32 张永不被请求**，且实测与 `-0` **逐字节相同** | 见 §7 |
| I9 | `:64-77` | 安装走 `replace_display`。`engine/Entity.lua:523` 完全替换绘制源、`:572` 连 `add_displays` 一起替换。所以 `FLOWER` 的 `add_mos`、出口的 `add_mos`、`BOGWATER_MISC` 的 `add_displays`、`DEEP_WATER` 的 `shader="water"` **全部丢失**——这是"单格完整合成"合同要求的结果，但意味着这些信息**必须由母版补回来** | §8 |
| I10 | `:52` | FLOODED 整区原生 | §3.4 |

---

## 7. 现有 `data/gfx/refined/` 资产实测盘点

`data/gfx/refined/` 共 **1683** 个条目（含 `korpul/` 目录 1 项）。按渲染器实际可达路径反查：

| 类别 | 张数 | 是否可达 |
| --- | ---: | --- |
| `tree-oak{0,1}` `tree-pine{0,1}` `tree-willow{0,1}` | 6 | 可达（`:43`） |
| `grass{0,1}` `flower{0,1}` `road{0,1}` `exit{0,1}` | 8 | 可达（`:45`） |
| `deep<0..15>-<0,1>-0` | 32 | 可达（`:44`） |
| `bog<0..15>-<0,1>-0` | 32 | 可达（`:44`） |
| `deep<m>-<p>-1` / `bog<m>-<p>-1` | 32 | **不可达**，且与 `-0` 逐字节相同 |
| `refined/bog{0,1}.png` `refined/water{0,1}.png` | 4 | **不可达**（同名文件在 `data/gfx/` 顶层，blockout 模式用的是顶层那份） |
| `route*-{0,1}.png` | 1024 | **不可达**（`tools/audit_repaint_sources.py:70` 称为 legacy） |
| `path*-{0,1}.png` | 512 | **不可达**（同上） |
| `korpul/` | 199 文件 | Kor'Pul 合同，与 G0 无关 |

**实际在用的森林精修瓦片只有 78 张**；`refined/` 顶层 1604 张是遗留或重复。这不是本轮要清理的事（`data/` 是产品目录），但**下一轮的清单校验必须做双向比对**（见 [ACCEPTANCE.md](ACCEPTANCE.md) A9），否则打包会继续带着 1.5 千张死图。

全部在用的 78 张实测均为 **128×128、RGBA、alpha 恒 255**（完全不透明的单格合成件）。也就是说：**母版透明，运行件不透明**——这是两条不同的判据，见 ACCEPTANCE A1/A2/A3。

---

## 8. G0 拆分方案：渲染身份表

下一轮按这张表建身份，**不要**再用 `name` 字符串匹配。每一行都要有对应的来源校验（`define_as` + 字段指纹，参照 `CheckerTerrain.lua:167-217` 的 Kor'Pul 做法）。

| 渲染身份 | 覆盖的原生 grid | 通行 | 视线 | 感知/ESP | 危险 | 导出方式 | 底层 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `grass` | `GRASS`、`GRASS_PATCH1..14`、`GRASS_SHORT` | 通 | 通 | 通 | 无 | 奇偶 ×2 | 地板 |
| `flower` | `FLOWER`、`FLOWER1..13` | 通 | 通 | 通 | 无 | 奇偶 ×2 | 地板（含蘑菇，见 I6） |
| `road-dirt` | `GRASS_ROAD_DIRT` | 通 | 通 | 通 | 无 | 奇偶 ×2 | 地板 |
| `tree-broadleaf` / `tree-pine` / `tree-cypress` | `TREE`、`TREE1..30` | **挡**（`pass_tree>=1` 可穿） | **挡** | 通 | 无 | 3 种 × 奇偶 = 6 | 透明构件 ⊕ `grass` |
| `hardtree` | `HARDTREE`、`HARDTREE1..30` | **挡**（无豁免） | **挡** | **挡** | 无 | 奇偶 ×2 | 透明构件 ⊕ `grass` |
| `deep-water` | `DEEP_WATER` | 通 | 通 | 通 | **窒息 5/回合**（`air_condition="water"` 可免） | 16 掩码 × 奇偶 = 32 | 地板（掩码） |
| `bog-water` | `BOGWATER`、`BOGWATER_MISC`、`BOGWATER_MISC1..7` | 通 | 通 | 通 | **无** | 16 掩码 × 奇偶 = 32 | 地板（掩码） |
| `bog-misc` | `BOGWATER_MISC1..7` 的 `add_displays` | 同上 | 同上 | 同上 | 同上 | 奇偶 ×2（叠在 `bog-water` 上） | 透明构件 |
| `bog-tree` | `BOGTREE`、`BOGTREE1..20` | **挡**（`pass_tree>=1` 可穿） | **挡** | 通 | 无 | 16 掩码 × 奇偶 = 32（底地是水，须随掩码） | 透明构件 ⊕ `bog-water` |
| `stew` | `STEW` | **挡** | 通（投射物亦通） | 通 | 无 | 奇偶 ×2 | 透明构件 ⊕ `grass` |
| `level-passage-{2,4,6,8}` | `GRASS_UP{n}`、`GRASS_DOWN{n}` | 通 | 通 | 通 | 无 | 方向 × 奇偶 | 透明构件 ⊕ `grass` |
| `world-exit` | `GRASS_UP_WILDERNESS` | 通 | 通 | 通 | 无 | 奇偶 ×2 | 透明构件 ⊕ `grass` |
| （不接管） | `ROCK_VAULT`、`POISON_DEEP_WATER`、`DEEP_OCEAN_WATER`、`GRASS_ROAD_STONE`、autumn/elven/jungle 全部、各 lesser vault 石质格 | — | — | — | — | — | 保持原生 |

三条硬约束：

1. **掩码语义 = 同一渲染身份的邻接**。`deep-water` 的掩码位只在邻居也是 `deep-water` 时置 1；`bog-water` 同理。不得把两种水合并计数（修 I7）。
2. **`bog-tree` 的底地随掩码**。它站在沼泽水里（`trollmire/grids.lua:60` 的 base image 是 `water_grass_5_1.png`），所以它的运行件必须是「`bog-water` 的对应掩码瓦片 ⊕ 透明柳树」，不能直接叠在草地上。这是它比 `tree-*`（32 张）贵得多的原因。
3. **单格完整合成**。所有 `add_mos` / `add_displays` / `shader` 都在 `replace_display` 处丢失（I9），母版必须自带这些信息；运行件必须完全不透明、所有阴影在格内、不跨格外溢。与 [Kor'Pul 合同](../p1-korpul/TERRAIN-CONTRACT.md#art-integration-interface)同款约束。

---

## 9. 母版清单与数量

### 9.1 清单

| # | 母版 id | 类型 | 对应原生 | 新增/替换 | 层级 |
| ---: | --- | --- | --- | --- | --- |
| 1 | `tree-broadleaf` | terrain-prop | `TREE` 的 elm/oak 家族 | 替换 `tree-oak` | T1 |
| 2 | `tree-pine` | terrain-prop | `TREE` 的 pine 家族 | 替换 | T1 |
| 3 | `tree-cypress` | terrain-prop | `TREE` 的 cypress 家族 | 替换 `tree-willow` | T1 |
| 4 | `hardtree` | terrain-prop | `HARDTREE` | **新增** | T1 |
| 5 | `deep-water` | terrain-floor | `DEEP_WATER` | 替换（复核优先，见 9.3） | T1 |
| 6 | `road-dirt` | terrain-floor | `GRASS_ROAD_DIRT` | **替换（已证据化必要）** | T1 |
| 7 | `troll-stew` | terrain-prop | `STEW` | **新增** | T1 |
| 8 | `level-passage` | terrain-prop | `GRASS_UP/DOWN{2,4,6,8}` | **新增**（从 `exit` 拆出） | T2 |
| 9 | `direction-mark` | terrain-prop | `way_next_{2,4,6,8}` 的方向语义 | **新增** | T2 |
| 10 | `world-exit` | terrain-prop | `GRASS_UP_WILDERNESS` | 替换 `exit` | T2 |
| 11 | `bog-water` | terrain-floor | `BOGWATER` | 替换（复核优先，见 9.3） | T3 |
| 12 | `bog-tree` | terrain-prop | `BOGTREE` | **新增** | T3 |
| 13 | `bog-misc` | terrain-prop | `BOGWATER_MISC1..7` | **新增**（1 张归并 7 种，见 9.4） | T3 |

**上界 13 张，下界 11 张**（若 #5 与 #11 复核通过免画）。

层级建议：T1（7 张）= 非泛滥 Trollmire 的规则缺口；T2（3 张）= 出口拆分；T3（3 张）= FLOODED。三层可分批交付，每层都是一个可验收的完整单元。

### 9.2 与 PLAN 7–8 张的差异及理由

PLAN 第 3 节 G0 行写的是「透明完整树 3＋硬树 1＋深水/沼泽水各 1＋炖锅 1，道路 1 视复核决定，共 7–8」。**这个数量不对**，理由逐条：

| 差异 | 张数 | 理由 |
| --- | ---: | --- |
| 出口拆分未被计入 | **+3** | 同一行的要求原文就是「拆分森林东西向通路与世界出口」，但 7–8 的构成里没有为它留名额。§4.5 核出最小 3 张（通路 1＋方向标记 1＋世界出口 1）。 |
| FLOODED 专属素材未被计入 | **+2** | 7–8 里只有"沼泽水 1"，而沼泽水**只在 FLOODED 出现**（§3.1）。既然要为 FLOODED 出沼泽水，就必须同时出 `BOGTREE` 和 `BOGWATER_MISC`，否则 FLOODED 的墙格（生成器 `wall="BOGTREE"`，是整图的主要阻挡物）依然原生，混杂反而更明显。`docs/repaint-plan-20260927/terrain-backlog.csv` 的 `G0-variant` 行已把它们记为 `accepted_master_count=0`，即"没预算"。 |
| 道路从"视复核决定"变为确定 | ±0 | [回退文档 §四](../terrain-fallback-20260927/FINDINGS.md)已用像素实测定案：`road0/1` 通道标准差仅 R4.3/G3.7/B2.9，是近乎平涂的泥面，被用户误认为占位图。这已经是复核结论，不需要再"视复核决定"。取 PLAN 区间上界。 |
| 树种家族重新分配 | ±0 | 3 张不变，但从 oak/pine/willow 改为 broadleaf/pine/cypress。willow 不属于非泛滥森林（§1.1），它去当 `bog-tree`（#12）。 |

7–8 → **11–13**。

### 9.3 `deep-water` / `bog-water` 的"复核优先"

现有 `deep*` 与 `bog*` 各 32 张可达瓦片已经存在。其中 `bog*` **从未在实机启用过**（FLOODED 门控）。所以：

**下一轮第一步不是画水，是把这 64 张按 [ACCEPTANCE.md](ACCEPTANCE.md) 的 A 类判据跑一遍。** 本文档核对时已实测过其中几条（A4 奇偶比、A5 掩码位局部性、A6 接缝连续性），全部通过。剩下的 A 类项与全部 B 类项（尤其 B6：深水/沼泽水的危险语义必须能分辨，且不能靠水色暗示额外规则）需要下一轮补齐。若 B 类通过，#5 和 #11 免画，G0 总量降到 11。

### 9.4 `bog-misc` 归并 7 种的理由与风险

`BOGWATER_MISC1..7`（`trollmire/grids.lua:86`）是 7 个**规则完全相同**的装饰变体，只有 `add_displays` 的图不同。按 AGENTS「地形按规则套件而非逐 PNG 重画」，1 张母版覆盖 7 种是合理的。

**风险**：一张装饰重复铺 7 处会出现明显的重复感（FLOODED 的 `floor2` 有 20% 概率出 MISC，`zone.lua:55`，在 65×40 的图上量不小）。缓解方案是**母版画成一张含 3–4 个互不相同装饰元素的组合片**，由导出器按格位确定性取其中一个（同 `CheckerTerrain.lua:43` 的 `(x*17+y*7)%3` 手法）。这不增加母版数。是否够用由样板决定，**未确认**。

### 9.5 复用、不出图

- `grass{0,1}`、`flower{0,1}` 按 PLAN「草地/花先复用」保留现状。
- 花/蘑菇合并（I6）**不进入本轮预算**。无规则差异，纯观感。但导出契约里要写明"`flower` 身份同时覆盖 6 花 + 7 蘑菇"，免得下一轮以为漏了。
- `GRASS_ROAD_STONE`（oldstone）不在 Trollmire 出现，本轮不出图；但判据要从 `g.road` 收紧为 `g.road=='dirt'`（I5），否则将来进别的森林区会拿泥路图去铺石路。

---

## 10. 未确认项

以下各项**核对未能得出结论**，写在这里而不是猜一个答案：

1. **方向标记能否旋转复用**。§4.5。取决于样板的实际光照表现，必须看图才能定。母版数因此是 3 或 6。
2. **是否要在视觉上区分上行/下行**。原生 tiles 不区分（§4.1）。这是"增加原生没有的信息"，属用户决策，不是核对能定的。
3. **`bog-misc` 一张母版够不够**。§9.4。
4. **lesser vault 内部的森林格**。7 个 lesser vault（`zone.lua:66`/`:194`）里，`honey_glade`、`forest-ruined-building1/2/3` 确认使用 `HARDTREE`/`ROCK_VAULT`/`GRASS`；`snake-pit`、`mage-hideout`、`collapsed-tower` 的地形清单**本轮未逐一展开**。它们可能引入石质格（走 G1）或本区未列的格。
5. **`GRASS_UP2/6/8`、`GRASS_DOWN2/4/8` 是否要在 G0 出图**。Trollmire 不可达（§4.3）。要不要现在就覆盖，取决于 G0 是否一次性服务所有用 `forest.lua` 的区域（老森林、Norgos 等），这超出本轮核对范围。
6. **`GRASS_SHORT`（`forest.lua:34-42`）在 Trollmire 是否可达**。生成器不放置它，但静态图/vault 是否用到未逐一核。它的 `name` 同为 `"grass"`，即使出现也会被正确归为 `grass`，所以风险为零，只是清单不完整。
7. **1604 张遗留 `route*`/`path*`/重复水图是否仍在打包产物里**。本轮只清点了源目录，没有拆开 `dist/` 下的 TEAA 核对。
8. **森林/水的导出器不存在**。`tools/` 下只有 `export_korpul_terrain.c`（+ `.cjs`）与 `export_token.c`，**没有森林/水的导出器**。现有 78 张森林瓦片的生成程序在当前仓库里找不到（`git log --all` 未见过同类文件）。下一轮必须新写一个，参数口径见 [ACCEPTANCE.md](ACCEPTANCE.md) §2。另：实测现有森林瓦片的奇偶系数约 **0.8952**，而 `export_korpul_terrain.c:101` 用的是 **0.90**，两套不一致；新导出器要显式声明用哪个常量。
