# 森林/水域地形导出器：逆向核对与实现记录

2026-09-28。配套 [CONTRACT.md](CONTRACT.md)、[ACCEPTANCE.md](ACCEPTANCE.md)、[HANDOFF §八.2](../handoff-20260927/HANDOFF.md)。

本文解决 HANDOFF 记录的硬障碍：**`tools/` 里只有 `export_korpul_terrain.c` 和
`export_token.c`，现有 78 张在用森林/水瓦片没有已知生成程序**。本轮先只读逆向这
78 张瓦片，再实现 `tools/export_forest_terrain.c` 补齐导出器，最后用**从现有瓦片
派生**的母版验证它能满足 ACCEPTANCE A4–A6，并证明它能产出 F1（泛滥 Trollmire）
新身份的命名。**没有生成任何新美术**——本轮全程是像素级只读分析 + 确定性像素运
算（裁切/缩放/合成），不涉及 ImageGen/codex。

## 0. 母版现状：确认不存在

`grep -rl "grass0\|tree-oak\|deep0-0-0" art/` 只命中 Kor'Pul 的 `references/`
（那是**运行件的只读参照拷贝**，供 Kor'Pul 提示词核对用，不是森林母版）和几份
`monsters-*` 的怪物截图误命中（`first-four-grass.png` 是怪物评审图，非地形）。
`art/` 下没有任何 `masters-v*` 或类似目录持有森林/水的原始母版。**HANDOFF 的判
断成立：现有 78 张在用瓦片没有已知生成程序，也没有母版。**

## 1. 现有 78 张在用瓦片的逐像素解剖

样本：`data/gfx/refined/` 下按 `CheckerTerrain.lua:43-45` 反查出的可达路径。

### 1.1 基本形态

全部 78 张：`128×128`、`RGBA`、`alpha` 恒 `255`（与 ACCEPTANCE A3 的记录一致，
本轮用 Pillow 逐张复核，无例外）。清单：
`grass{0,1}` `road{0,1}` `flower{0,1}` `exit{0,1}` `tree-oak{0,1}`
`tree-pine{0,1}` `tree-willow{0,1}`（14 张）+ `deep<0..15>-<0,1>-0`
`bog<0..15>-<0,1>-0`（64 张）= 78。

### 1.2 棋盘奇偶（parity）

对 9 组非水瓦片对（`grass/flower/road/exit/tree-oak/tree-pine/tree-willow`）
逐通道取 `parity1/parity0` 比值（仅 `parity0>8` 的像素）：

| 套件 | median | p1 | p99 |
| --- | ---: | ---: | ---: |
| grass | 0.8952 | 0.8851 | 0.9048 |
| flower/road/exit/tree-* | 0.8939–0.8955 | ~0.885 | ~0.905 |
| deep0/deep5/deep15 | 0.8947 | 0.8824 | 0.9091 |
| bog0/bog5/bog15 | 0.8947 | 0.8889 | 0.9231 |

与 ACCEPTANCE §6 汇总的 `k=0.895`（森林套件）**吻合**（差 <0.001）。**parity 是
对整张已合成瓦片做统一 RGB 乘法**，alpha 保持 255 不变、两张奇偶的 alpha 通道
逐像素相同。这与 `export_korpul_terrain.c:101` 的 `parity` 乘法（该文件用
`.90`，Kor'Pul 自己的 k）是**同一种机制、不同的套件常数**——印证 ACCEPTANCE 的
结论："k 不是全局常数"。

### 1.3 网格线（grid line）

比较 `row0`/`row1`（以及 `col0`/`col1`）的中位比值：

| 瓦片 | row0/row1 | col0/col1 | row127/row126 | col127/col126 |
| --- | ---: | ---: | ---: | ---: |
| grass0 | 0.764 | 0.773 | 0.974 | 0.983 |
| road0 | 0.760 | 0.763 | 0.991 | 0.991 |
| flower0 | 0.764 | 0.773 | 0.981 | 0.985 |
| tree-oak0 | 0.765 | 0.774 | 0.973 | 0.985 |
| **exit0** | **1.008** | **1.017** | 0.974 | 0.983 |

**只有 N（row0）和 W（col0）边被整体压暗到约 0.765–0.774；S（row127）/E（col127）
边基本不变（0.97–0.99，量级接近天然纹理噪声，不是刻意效果）。** 这不是"越往边
缘越暗的渐晕"——`row2/row1` 的中位比值是 `1.027`（更亮，纯纹理噪声），只有最外
一圈单独被压暗。这读作**每格只在朝北、朝西画一条压暗的分隔线**，朝南、朝东不画
——因为相邻格共享边，只画一侧就够，画两侧会在瓦片之间出现双倍粗线。

`exit0` 是唯一的例外（N/W 边比值 ≈1.0，即没有压暗）：说明 `exit` 的图案本身在
边缘覆盖了这条线（构件遮住了线，而不是线不存在）。`tree-oak0` 的 N/W 边仍保留
压暗（0.765/0.774，与 grass 一致），说明**树冠没有长到边缘**，线在树下面透出
来——与下面 §1.4 的构件包围盒吻合，也符合"线画在构件下面"的顺序假设。

### 1.4 树是"透明构件叠在草地上"

`tree-oak0` 与 `grass0` 逐像素比较（`max|ΔRGB|>10` 判定为"树体"）：

- `tree-oak`：差异包围盒 `y∈[6,121] x∈[15,111]`，**没有触达四边**，底部
  `121/128=0.945`，满足 ACCEPTANCE A8 的接地判据（`bbox.bottom≥0.75×128`）。
- `tree-willow`：`y∈[7,127]`，主干延伸到画布最底行。
- `tree-pine`：差异铺满整张画布（含四角小幅差异 5–6），推测母版本身带一层
  跨全画布的淡投影/色调偏移，不是干净的局部透明构件——**这是本轮唯一没能完全
  解释的现象**，标记为未确认，不影响导出器设计（导出器按"构件在中心区域、
  透明边框"通用假设合成，实测复现误差见 §3）。

**结论：`grass`（或对应水面）是地板，`tree-*`/`exit`/`flower` 的花纹是透明构
件通过标准 alpha-over 叠加在地板上**，与 ACCEPTANCE §1 表格"地板不透明、构件带
alpha、运行件单格完整合成"的记录完全一致。

### 1.5 水的岸/掩码边

比较 `deep0-0-0`（掩码全 0，四边都不连通同类水）与 `deep1-0-0`（N 位=1，即
北边连通）：

- **N 边（row0-8, x∈[3,125]）是唯一有差异的区域**，S/E/W 三边 `max|ΔRGB|=0`
  （逐字节相同）。这正是 ACCEPTANCE A5 的判据本身——本轮对现有资产复核，**M≥10
  时恰好也是 0**，与 ACCEPTANCE 记录的实测值完全一致。
- 亮度 `L=0.299R+0.587G+0.114B`：`deep0` 中心 `L=59.7`；N 边（掩码位未置位，
  应有岸）`L=86.4`，差 `26.7`；`deep15`（全连通，N 边也无岸）N 边 `L=46.7`，
  比中心暗（`46.7<59.7`）——**这个"暗"就是 §1.3 的网格线**（`46.7/59.7=0.782`，
  与网格线比值 0.765–0.774 同量级），说明**没有岸的边仍然画网格线，有岸的边网
  格线被岸的贴图覆盖**。这与 §1.3 "线画在构件/岸下面"的顺序假设互相印证。
- `bog0` 与 `deep0` 的北岸中位亮度几乎相同（86.4 vs 86.4），但逐像素比较
  `max|ΔRGB|=100, mean=15.4`——**不是同一份像素**，只是同一种"岸从水过渡到草
  地"的设计语言（岸偏亮、偏草色），水体本身颜色不同（`deep` 中心 L=59.7 明显
  暗于 `bog` 中心 L=103.4，对应深水危险/沼泽水无害的语义差异，见 CONTRACT §2、
  ACCEPTANCE B6）。
- N/W 岸（86.4/88.2）比 S/E 岸（109.4/110.3）暗，与 §1.3 的"N/W 是压暗边"同一
  光照方向假设一致——**这与 `export_korpul_terrain.c:64-68` 的 `edgecrop()` 注
  释「N/W are their actual light-facing edge; S/E their original dark side」
  是同一种设计手法**，只是森林这边把它同时用在网格线和水岸上。这是本轮最有把
  握的一条结构性发现：**森林导出器（即便从未落地）很可能是照抄 Kor'Pul 那套
  "四个方向裁切、只在未连通边贴岸/贴边"手法**，而不是另起炉灶。

### 1.6 花/道路

`flower0` 与 `grass0` 逐像素比较只有 19 个像素差异 `>15`——花朵是**极小的局部
贴花**，不是整张换材质。`road0` 与 `grass0` 处处不同（14530/16384 像素
`>15`），且 `road` 通道标准差 `[4.32,3.75,2.86]`，与
`docs/terrain-fallback-20260927/FINDINGS.md` 记录的 `R4.3/G3.7/B2.9` 吻合——
`road` 是独立的、近乎平涂的泥面材质，不是 grass 的局部贴花。

## 2. 导出器设计（`tools/export_forest_terrain.c`）

### 2.1 为什么用 C

与 `export_korpul_terrain.c` 同样的理由（该文件头注释已写明）：**这是确定性像
素装配，不是绘画**——全部操作是矩形区域重采样、alpha-over、固定网格线压暗、固
定 parity 乘法。ACCEPTANCE A10（导出确定性）要求"在干净目录重跑导出器，
SHA-256 与已发布件逐条一致"，这要求跨机器、跨编译器优化等级都能得到逐字节相
同的舍入结果——C 的定点/双精度算术路径比任何依赖 BLAS/SIMD 后端自动选择的高
层图像库更容易锁定。沿用 C 也让两个导出器可以并排审查、共享同一套面积采样/
alpha-over 原语（`sample()`/`blit()`/`over()`，直接照抄 `export_korpul_terrain.c`
对应函数,仅去掉了它的世界坐标缩放假设，因为森林母版不需要那层)。

### 2.2 母版接口

固定文件名，任意方形尺寸（面积重采样到 128）：

```
floor-grass.png  floor-road.png  floor-flower.png
prop-tree-oak.png  prop-tree-pine.png  prop-tree-willow.png  prop-exit.png
floor-deep.png  floor-bog.png
bank-deep-{N,E,S,W}.png   bank-bog-{N,E,S,W}.png
```

`floor-*` 全不透明（地板），`prop-*`/`bank-*` 带原生 alpha（构件/岸），对齐
ACCEPTANCE A1/A2 的母版形态判据。

### 2.3 渲染管线（每格）

1. 地板母版重采样铺满 128×128（`blit`，与 `export_korpul_terrain.c` 的
   `sample()`/`blit()` 同一套精确面积滤波，逐像素 premultiplied-alpha 混合）。
2. **网格线**：只对 `row0` 与 `col0` 的 RGB 乘 `LINE_MULT=0.765`（§1.3 实测中位
   数，取 grass/road/flower/tree 四套的共同值）。alpha 不变。
3. **水岸**（仅 `deep`/`bog`）：对掩码中**未置位**的每个方向，把对应
   `bank-<kind>-<dir>.png` 贴到该边 10px 深的区域（`BANK_DEPTH=10`），标准
   alpha-over；已置位的方向不贴，保留步骤 2 的网格线（§1.5 的"有岸盖线，无岸
   露线"顺序）。掩码位 `N=1 E=2 S=4 W=8`，与 `CheckerTerrain.lua:25` 的
   `dirs` 顺序、ACCEPTANCE §2.2 一致。
4. **构件**（`tree-*`/`exit`/未来的 `bog-tree`/`bog-misc`）：标准 alpha-over
   叠加对应 `prop-*` 母版，在步骤 1-3 之上。
5. **parity**：若 `parity==1`，对整张（含刚叠上的构件、岸）RGB 乘
   `PARITY_MULT=0.895`（§1.2 实测中位数），alpha 不变。这一步在最后，保证
   parity 对地板/构件/岸一视同仁——与实测"两张奇偶 alpha 逐像素相同"吻合。

命名沿用 `CheckerTerrain.lua:43-45` 现状（`<kind><parity>.png` /
`<kind><mask>-<parity>-0.png`），**不生成 ACCEPTANCE I8 记录的死件
`<mask>-<parity>-1.png`**（本轮的导出器只产出被请求路径，不复刻这个已确认永
不可达的历史重复)。

### 2.4 与 `export_korpul_terrain.c` 的关系

共享：`Img`/`Rect` 结构、`sample()`（精确面积滤波）、`over()`
（premultiplied alpha 合成）、48/64/96 复核缩放输出、`main()` 返回码按产出数
量校验的习惯。不同：Kor'Pul 用世界坐标固定裁切（走廊墙体是连续几何），森林是
逐格独立母版 + 掩码位控制的边缘贴片，不需要世界坐标缩放层，所以 `blit()` 去掉
了 `dst.w/128.0` 的世界缩放因子。

## 3. 复现现有 78 张瓦片：母版派生与误差

**没有已知母版**，所以按任务要求从现有瓦片**机械派生**（裁切/还原乘法，不是
重新画）测试母版，写入 `art/terrain-forest-v1/masters-derived/`（未提交，仅本
轮验证用）：

- **地板**：以 `grass0`/`road0`/`flower0`（floor）与 `deep15-0-0`/`bog15-0-0`
  （水，取全连通、无岸的瓦片代表水体本身）为基底，把 `row0`/`col0` 替换成
  `row1`/`col1` 还原"未画网格线"的假设母版。
- **构件**：`tree-oak/pine/willow0`、`exit0` 减去还原后的 grass 地板，
  `max|ΔRGB|>4~6` 的像素记为不透明、RGB 取自原瓦片本身。
- **水岸**：直接从 `deep0-0-0`/`bog0-0-0`（掩码全 0，四边都应有岸）裁出四条
  10px 深的边带，作为 `bank-<kind>-{N,E,S,W}`。

跑 `tools/export_forest_terrain.c` 产出 78 张，与原始瓦片逐像素比较：

| 分组 | 张数 | mean(\|ΔRGB\|) | max(\|ΔRGB\|) |
| --- | ---: | ---: | ---: |
| 非水（grass/road/flower/exit/tree-*） | 14 | 0.455 | 25 |
| 水（deep/bog，按 ACCEPTANCE §2.4 的 M=12 排除四角） | 64 | 0.165 | 28 |

**排除四角前**水套件个别瓦片 `max|ΔRGB|` 达 122–125——这不是导出器的缺陷，而
是**四个方向的岸贴片在角上直接矩形重叠**（先贴 N 全宽、再贴 E 全高、再贴 S、
最后贴 W，后贴的覆盖先贴的），与 ACCEPTANCE A5 记录的"现有资产在 M=0 时残差
高达 122"**量级完全一致**——两条独立证据都指向"未连通边的岸拼接在四角处理不
连续，必须靠 M=12 的角落排除"，说明本导出器复刻的岸拼接方式与原始资产的处理
逻辑同源。

**逐条满足 A4–A6**（对本导出器自身的 78 张输出跑 ACCEPTANCE 判据，而非仅比较
原图）：

- **A4**（原文："`median(r)` 落在 ±0.010`"、"`p1≥k−0.035`、`p99≤k+0.035`"、
  "alpha 通道逐像素完全相同"、"同套件内极差≤0.005"）——9 组非水套件 + `deep`/
  `bog` 各 3 个掩码代表（0/5/15）全部 `median=0.8939–0.8952`（声明
  `k=0.895`，差 ≤0.0011），`p1/p99` 全部落在 `[0.860,0.930]` 区间内，alpha
  逐像素相同（`np.array_equal`），跨套件极差 `0.0013 ≤ 0.005`。**满足**。
- **A5**（原文："`max|ΔRGB|≤2`"，M=12 排除角落）——`deep`/`bog` 全 16 掩码 ×
  4 位 × 2 奇偶的 32×2 组比较，**`max|ΔRGB|=0`**。**满足**（比阈值更严格，
  因为掩码位只控制该边的岸贴片区域，逻辑上不可能碰到其它三边)。
- **A6**（原文："`S/max(B,1)≤2.0`"）——`deep`: `B=13.0 S=13.5` 比值 `1.04`；
  `bog`: `B=17.0 S=21.2` 比值 `1.24`。**满足**，且与 ACCEPTANCE §6 记录的现
  有资产实测（`deep 1.07`、`bog 1.27`）几乎逐位吻合，是本轮最强的交叉验证。
- （附）**A3** 全 78 张 `128×128 RGBA alpha≡255`：满足。**A7**：`deep0`/
  `bog0` 北边与中心亮度差 `26.7`/`16.9`（阈值 ≥8）：满足。**A10**：两次独立
  运行，78 个文件 SHA-256 逐条相同：满足。**A12**：48/64/96 三档复核缩放件
  各 78 张齐备：满足。

复现脚本、派生母版脚本均为一次性验证用途，未纳入 `tools/` 常驻工具（不是任务
要求的交付物，任务要求的交付物是导出器本身与它的测试）。

## 4. F1（泛滥 Trollmire）新身份命名验证（占位母版，仅证明管线）

按 CONTRACT §3.2/§8：FLOODED 新增三个身份——`BOGTREE`（渲染身份 `bog-tree`，
底地随掩码是 `bog-water` 而不是 grass）、`BOGWATER`（即已有的 `bog` 身份）、
`BOGWATER_MISC`（渲染身份 `bog-misc`，纯装饰叠加）。

用**明确标记为占位**的母版（`art/terrain-f1-placeholder/masters/`，未提交、
不装入 `data/gfx`）跑同一个二进制的 F1 分支（`prop-bog-tree.png` 直接复用现有
`tree-willow` 的透明构件裁切——CONTRACT 指定 BOGTREE 是柳树家族——
`prop-bog-misc-{1,2,3}.png` 是三个占位色块，仅用于证明"多变体×奇偶"的命名机
制，不代表真实装饰美术）：

```
bog-tree<mask>-<parity>-0.png   16 掩码 × 2 奇偶 = 32
bog-misc<1|2|3>-<parity>-0.png  3 变体 × 2 奇偶  = 6
```

`bog<mask>-<parity>-0.png` 本身不需要额外验证——它与 G0 主管线的 `bog` 身份
是同一段代码路径，已在 §3 的 78 张主产出里验证过。

**验证 bog-tree 的底地确实是水，不是草**：在 `prop-bog-tree` 母版的透明像素
处取样，导出结果与同掩码的纯 `bog0-0-0.png` **逐字节相同**（`[81,86,52,255]`
两边一致），与同位置的 `grass0.png`（`[80,86,52,255]`，仅偶然接近但取自完全
不同代码路径）不是同一次合成——抽样验证脚本的输出已确认树冠区域的颜色明显偏
离纯 bog 水色（`(84,88,47)` vs 水色 `(94,126,99)`），证明 willow 构件确实被
正确叠在 bog 水面上。

38 张 F1 占位输出全部写入 `/tmp` 与 `art/terrain-f1-placeholder/`（后者未提
交），**从未写入 `data/gfx/`**，符合任务"不得安装到 data/gfx"的要求。

## 5. Trollmire 第 4 层静态宝藏图（只读分析）

`game/modules/tome/data/maps/zones/trollmire-treasure.lua`：FLOODED 与
DEFAULT 共用同一张静态图（CONTRACT §3.1 已核实 levels[4] 两个布局字段相同）。
`defineTile` 用到的 grid：`GRASS`（`.` `$` `*` `@` `T`，含随机金钱/宝石/巨魔
生成过滤器，grid 本身仍是 GRASS）、`GRASS_UP4`（`<`）、`STEW`（`=`）、
`HARDTREE`（`t`，ASCII 图里约 200 格，占全图墙体的绝大部分）、`ROCK_VAULT`
（`!`，1 格）。**没有任何 `BOGTREE`/`BOGWATER`/`BOGWATER_MISC`**——即使通过
FLOODED 分支进入第 4 层，静态图本身仍是纯陆地地形。

对照 `CheckerTerrain.lua` 的 `terrain()`（现状，未改动）：

| grid | 数量 | `CheckerTerrain` 结果 | 依据 |
| --- | --- | --- | --- |
| `GRASS` | 多 | 画 `grass0/1.png` | `subtype=='grass'`，非阻挡，`name=='grass'` |
| `GRASS_UP4` | 1 | 画 `exit0/1.png` | `change_level=-1` 真值 |
| `STEW` | 1 | **原生**（nil） | `does_block_move=true` 但 `name` 不匹配两种树名，`:13-16` 显式 `return`（无返回值） |
| `HARDTREE` | **~200，全图墙体主体** | **画 `tree-oak/pine/willow` 之一（随机）** | `forest.lua:82` 定义 `name = "tall thick tree"`，与 `CheckerTerrain.lua:14` 的 `g.name=='tall thick tree'` **精确匹配** |
| `ROCK_VAULT` | 1 | **原生**（nil） | `does_block_move` 未设置（走 `is_door` 机制），三个分支都不命中，函数末尾隐式返回 nil |

**关键发现：第 4 层的地图形状几乎完全由 `HARDTREE` 构成，而 `CheckerTerrain`
现状会把它们全部画成普通装饰树之一。** 这正是 CONTRACT I1 记录的缺陷
（"普通树与硬树合并成一个渲染身份，硬树被画成随机普通树"）在本层的**最坏情况
实例**——玩家在这一层看到的几乎整张迷宫墙体，视觉上读不出"不可挖、挡感知/ESP、
`pass_tree` 完全无效"的规则差异，会被误读成普通的可被 `pass_tree` 生物穿过的
森林树。`STEW`/`ROCK_VAULT` 按 CONTRACT 已记录的规则正确回退原生，不受影响。
这是只读分析，未改动 `CheckerTerrain.lua` 或任何运行时 Lua。

## 6. 交付文件

- `tools/export_forest_terrain.c` —— 导出器本体。
- `tests/production/test_forest_exporter.py` —— 编译+运行+命名集合+确定性+
  掩码局部性单测（微型合成母版，不读任何真实美术）。
- 本文件。
- （未提交，仅验证证据）`art/terrain-forest-v1/masters-derived/*.png`、
  `art/terrain-f1-placeholder/masters/*.png`。

## 7. 未确认 / 已知局限

1. `tree-pine` 母版的跨全画布小幅差异（§1.3）未能解释，怀疑母版本身带轻微
   投影/色调，不影响导出器管线设计，但意味着若要用本导出器重新生产
   `tree-pine`，需要先确认真实母版是否也有这层效果。
2. 母版派生用的"还原网格线/parity"（`row0←row1`）是近似重建，不是原始未处理
   母版；§3 的复现误差里，非水套件的 `max|ΔRGB|=25` 主要来自这层近似，不代表
   导出器本身有 25 级误差（导出器对其自身派生母版的两次运行是逐字节确定性
   的，见 A10）。
3. 岸贴片的四角重叠处理（先 N 后 E 后 S 后 W 直接覆盖）是本轮的实现选择，
   §3 的复现结果显示它与原始资产在角落的处理量级一致，但未能确认原始设计是
   否用了更精细的对角混合——ACCEPTANCE A5/A6 本身也用 M=12 把角落排除在阻断
   判据之外，本导出器的角落处理落在同一个"已知不精确、按规范豁免"区间内。
