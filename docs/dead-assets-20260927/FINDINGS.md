# 死资产可达性审计（2026-09-27）

本轮是**只读分析**：没有删除任何文件、没有重新打包、没有升版本号、没有启动游戏、没有改动任何渲染逻辑。
版本保持 **0.6.10**，`dist/` 保持原状（`tome-checker-revised-0.6.10.teaa`，SHA256 `3cb626bc7500a0930bfb6dffed8aeb516240aa00cba47b495cece9561d01f3be`）。

产出：

- `tools/audit_dead_assets.py` —— 只读审计脚本，可达集**从渲染器源码派生并实际执行**，支持 `--json` 与 `--check`。
- `evidence/dead-assets-20260927/` —— 本次审计的机读结果与逐文件候选清单。

放在 `docs/` 而不是 `evidence/`：本文是**给下一轮照做的结论与风险分级**，与 `docs/g0-terrain-contract-20260927/` 同类；
`evidence/` 只放这次跑出来的原始数据。

---

## 0. 结论速览

| | 文件数 | 字节 |
| --- | ---: | ---: |
| `data/gfx/` 磁盘实测 | **1965** | 59 517 636（56.76 MB） |
| 渲染器可达（§1） | **353** | 10 676 080（10.18 MB） |
| 仅被夹具代码引用（§4） | **1** | 26 860 |
| **不可达**（§3） | **1611** | **48 814 696（46.55 MB）** |

`data/gfx/` 里 **82.0% 的文件、82.0% 的字节**是任何代码路径都请求不到的。

复现：

```
python3 tools/audit_dead_assets.py           # 人读
python3 tools/audit_dead_assets.py --json    # 机读
python3 tools/audit_dead_assets.py --check   # 有死资产时退出码 1（可接打包回归）
```

---

## 1. 可达集：353 张，逐类

| 来源 | 张数 | 字节 | 构造位置 |
| --- | ---: | ---: | --- |
| `forest:blockout` | 10 | 0.01 MB | `CheckerTerrain.lua:38-40` |
| `forest:refined` | 78 | 2.31 MB | `CheckerTerrain.lua:41-46` |
| `korpul:floor-wall-door` | 196 | 6.43 MB | `CheckerTerrain.lua:280-284`（`M.assetPath`） |
| `korpul:stair-foreground` | 3 | 0.26 MB | `CheckerTerrain.lua:313`（`M.render` 的前景 `add_mos`） |
| `token:creature` | 46 | 1.10 MB | `CheckerTokens.lua:246-249`（`M.image`） |
| `token:overlay-mask` | 20 | 0.08 MB | `superload/mod/class/Actor.lua:190-268` |
| **合计** | **353** | **10.18 MB** | |

### 1.1 森林 refined：78 张 —— 与交接数字一致

`terrainImage`（`CheckerTerrain.lua:35-47`）在 `mode=='refined'` 下的完整输出：

- `tree-{oak,pine,willow}{0,1}` —— 6（`:43`，变体由 `(x*17+y*7)%3` 选，奇偶由 `(x+y)%2` 选）
- `{deep,bog}<mask 0..15>-<parity 0,1>-0` —— 64（`:44`，**末位恒为 `-0`**）
- `{exit,road,flower,grass}{0,1}` —— 8（`:45`）

合计 **78**，与交接给的 78 张**完全一致**，没有差异。
`terrain()`（`:9-23`）能返回的身份闭集是 `{exit, tree, road, flower, grass, deep, bog}` 七个，
脚本是从 `terrain()` 每条 `return` 语句里抽字面量得到的，不是手抄。

### 1.2 森林 blockout：10 张 —— 交接完全没算这一块

`CheckerTerrain.lua:38-40`：

```lua
if mode=='blockout' then
 return img(((t=='deep' or t=='bog') and 'water' or t=='flower' and 'grass' or t)..parity)
end
```

七个身份经这条映射折叠成五个基名（`deep`/`bog` → `water`，`flower` → `grass`），带奇偶 = **10 张**，
路径**不带 `refined/` 前缀**，落在 `data/gfx/` 顶层：

```
exit0 exit1  grass0 grass1  road0 road1  tree0 tree1  water0 water1
```

**blockout 是玩家可选档**：`CheckerOptions.lua:4` 的 `local modes={vanilla=true, blockout=true, refined=true}`
三档都有效，`M.terrainMode()`（`:15-17`）只把**不在表里**的值回落成 `vanilla`。
`applyForest`（`:49-79`）对 Trollmire 非泛滥布局直接使用该模式，`tests/runtime_modes.lua:100` 也断言
`checker-revised+grass0.png`。

→ **这 10 张 0.3.x 素材仍在用，不许删。**

### 1.3 Kor'Pul：196 + 3 = 199 张，全部可达

交接完全没验这条路径。独立算法如下。

`M.assetPath(kind, orientation, mask, parity, x, y)`（`:280-284`）：

```lua
if kind=='floor' or kind:match('^stairs%-') then kind=((x*17+y*7)%3==0) and 'floor-b' or 'floor-a';mask=0 end
if orientation then kind=kind..'-'..orientation end
return img('refined/korpul/'..kind..'-'..mask..'-'..parity)
```

入参域完全由模块自己的表决定：

- `kind` 来自 `identities`（`:132-141`）的值域：`floor`、`wall`、`hardwall`、`door-closed`、`door-open`、`stairs-up`、`stairs-down`、`stairs-world`。
- `orientation` 只在门分支产生（`M.classify` `:250` / `:255`），取自 `doors[id][3]` 与 `open[id][2]`，值域 `{horizontal, vertical}`。
- `mask` 由 `M.mask`（`:274-279`）在 `offsets` 四邻域上累加 → `0..15`。
- `parity` = `(x+y)%2` → `{0,1}`。

展开：

| kind（`assetPath` 改写后） | mask 域 | 张数 |
| --- | --- | ---: |
| `floor-a` / `floor-b`（`floor` 与三种 `stairs-*` 全部折叠到这里，mask 强制 0） | {0} | 2 × 1 × 2 = 4 |
| `wall` | 0..15 | 32 |
| `hardwall` | 0..15 | 32 |
| `door-closed-horizontal` / `door-closed-vertical` | 0..15 | 64 |
| `door-open-horizontal` / `door-open-vertical` | 0..15 | 64 |
| **小计** | | **196** |

再加 `M.render:313` 的楼梯前景 `img('refined/korpul/'..record.kind)` → `stairs-{up,down,world}.png` **3 张**。

**196 + 3 = 199，正好等于 `data/gfx/refined/korpul/` 磁盘上的 199 个文件，一张不多一张不少。**

两处独立互证：

1. `CheckerTerrain.lua:104` 的清单校验硬性要求 `count==196`，`:126` 要求 `count==3`；少一张就整体降级回原生。
2. 脚本把派生结果与 `data/terrain-korpul-manifest.lua`（196 条）、`data/terrain-korpul-stairs-manifest.lua`（3 条）做**对称差**比对，本次差集为空。

→ **korpul/ 下 199 个文件全部可达，一个都不能动。**

### 1.4 棋子与 UI 遮罩：46 + 20 = 66 张，无孤儿

- 怪物棋子：对 `CheckerTokens.M.by_id` 的**每个 id** 实际调用 `M.image(id)`（`:246-249`），得 46 条
  `checker-revised+tokens/<id>.png`。`tests/token_mapping.lua:29` 已在做同一比对。
- UI 遮罩：从 `Actor.lua` 源码里扫 `'_名字'` 字面量与 `'_前缀'..变量` 拼接，后缀域由**实际调用**
  `CheckerTokenStyle.relation()`（→ `player/friend/neutral/enemy`）和 `rankBadge()`（→ `rare/unique/boss/elite_boss/god`）枚举得到：

  ```
  _relation-back  _relation-{player,friend,neutral,enemy}  _relation-edge-{同四种}
  _player-inner   _health-band
  _shield-track   _shield-band   _shield-ticks
  _badge-back     _badge-{rare,unique,boss,elite_boss,god}
  ```

  共 **20**。`overload/mod/dialogs/CheckerRankColor.lua:21-32` 用的是同一批（其 `key` 域受
  `Style.relation_color_defaults` / `Style.rank_colors` 约束，是上面的子集），脚本会断言它没有引入新家族。

- 磁盘 `data/gfx/tokens/` 共 66 个文件 = 46 + 20。**双向比对无差集，没有孤儿，也没有缺图。**

---

## 2. `data/gfx/` 顶层 18 个文件的逐个结论

| 文件 | 结论 | 依据 |
| --- | --- | --- |
| `exit{0,1}` `grass{0,1}` `road{0,1}` `tree{0,1}` `water{0,1}`（10） | **可达** | blockout 模式在用（§1.2），blockout 是玩家可选档 |
| `hero.png`（1） | **保留**（非渲染器可达，但被代码引用） | `tests/fixture/tome-checker-fixture/superload/mod/class/Game.lua:36` 的固定演示玩家棋子 |
| `bear.png` `plant.png` `snake.png` `troll.png` `wolf.png`（5） | **不可达** | 0.3.x 时期的 blockout 生物占位图。生物美术现在**完全**走 `CheckerTokens` → `data/gfx/tokens/`，与地形模式无关；全仓 `.lua` 搜不到任何 `checker-revised+{bear,plant,snake,troll,wolf}.png` 字面量 |
| `wall{0,1}`（2） | **不可达** | blockout 分支的身份域里根本没有 `wall`（§1.2）；Kor'Pul 的墙走 `M.render`，而 `M.apply:341` 对 Kor'Pul 只允许 `refined` 或 `vanilla`，blockout 在该区直接回落 vanilla |

**回答「blockout 模式是否仍在用 0.3.x 素材」：是，但只用其中 10 张地形瓦片。**
同目录的 5 张生物图和 2 张墙图不属于 blockout 地形集，blockout 不会请求它们。

---

## 3. 不可达清单（1611 个，48 814 696 字节 / 46.55 MB）

| 类别 | 张数 | 字节 | MB | 为什么请求不到 |
| --- | ---: | ---: | ---: | --- |
| `refined/route<0..511>-{0,1}.png` | 1024 | 31 059 690 | 29.62 | 0.3.1/0.3.2 的连续路带方案。全仓（含 `tests/`、`hooks/`、`superload/`、`overload/`、清单 `.lua`）**没有任何 `route` 字符串**；渲染器的前缀闭集只有 `tree-oak/pine/willow`、`deep`、`bog`、`exit`、`road`、`flower`、`grass` |
| `refined/path<0..255>-{0,1}.png` | 512 | 15 490 915 | 14.77 | 同上，legacy。`tools/audit_repaint_sources.py:70` 已标为 legacy |
| `refined/{deep,bog}<mask>-<parity>-1.png` | 64 | 2 001 150 | 1.91 | `:44` 的路径末位**硬编码为 `-0`**，不是变量；且实测 64 对全部与 `-0` **逐字节相同**（`cmp` 64/64 通过） |
| `refined/bog{0,1}.png`、`refined/water{0,1}.png` | 4 | 121 321 | 0.12 | refined 分支里水永远带掩码后缀（`bog<m>-<p>-0`），不会产生裸 `bog0`；`water` 只出现在 blockout 分支，而 blockout 路径**不带 `refined/` 前缀**，用的是顶层那两张 |
| `gfx/wall{0,1}.png` | 2 | 2 386 | 0.00 | §2 |
| `gfx/{bear,plant,snake,troll,wolf}.png` | 5 | 139 234 | 0.13 | §2 |
| **合计** | **1611** | **48 814 696** | **46.55** | |

逐文件清单：`evidence/dead-assets-20260927/dead-candidates.txt`。

---

## 4. 不确定 / 建议保留的

| 项 | 为什么不建议删 |
| --- | --- |
| `data/gfx/hero.png`（26 860 B） | 渲染器不可达，但 `tests/fixture/.../Game.lua:36` 用 `checker-revised+hero.png` 做固定演示玩家棋子。夹具 superload 本身不入包，可它引用的是**产品包里的**这张图；删了实机夹具就缺图。为 26 KB 冒这个险不值得 |
| 全部 `refined/korpul/`（199） | 清单校验是**全有或全无**：少一张 `count==196` 就不成立，整个 Kor'Pul 精修直接降级原生 |
| 全部 `data/gfx/tokens/`（66） | 双向比对无孤儿 |
| blockout 10 张顶层瓦片 | 玩家可选档在用 |

另有一条**残余风险**，不影响本轮结论但删除前应知道（见 §5）：
`applyForest` 把生成的图名写进 `g._checker_terrain.image` 与 `replace_display` 这个 `Entity`（`:68-73`），
而 grid 会进存档。0.3.x 存档里可能残留 `route*`/`path*` 的 `replace_display`。
读档后 `applyForest` 会在同一帧把它改写成当前图名（`state.image~=file` 分支），
但**在 `M.apply` 跑到之前**若有一次 MO 构建，引擎会去找一张不存在的 PNG。
T-Engine 对缺图是回落而不是崩溃，且跨 0.3 → 0.6 的存档兼容本就没有承诺，所以这是**低风险**，
但它是唯一一条「删掉的文件仍可能被请求」的理论路径，记录备查。

---

## 5. 下一轮真要删时：建议顺序与风险分级

按「风险从低到高」分四批，每批之间都应能独立回退。

### 批次 A —— 零风险，收益 1.91 MB

`refined/{deep,bog}<mask>-<parity>-1.png`（64 张）

- 路径末位在 `:44` 是**字面常量 `-0`**，不是变量，不存在任何输入能让它变成 `-1`。
- 64 对全部与 `-0` 逐字节相同：即便真有路径请求到它们，内容也没有区别。
- 验证成本最低：refined 模式下 Trollmire DEFAULT 的池塘边缘正常即可。

### 批次 B —— 极低风险，收益 44.39 MB（收益主体）

`refined/route*`（1024）+ `refined/path*`（512）

- 依据是**渲染器不可能构造这两个前缀**：`terrainImage` 的前缀来自 `terrain()` 的七个身份闭集，
  `M.assetPath` 的前缀来自 `identities` 的八个值域，两者都不含 `route`/`path`。
- 全仓 `.lua` 字面量搜索为零命中。
- 唯一理论风险是 §4 末尾的旧存档残留，属可接受。
- 建议与批次 A 同一次提交，这样一次实机验证覆盖两批。

### 批次 C —— 低风险，收益 0.12 MB

`refined/bog{0,1}.png`、`refined/water{0,1}.png`（4 张）

- 风险点是**同名不同目录**：顶层 `data/gfx/water0.png` 是 blockout 在用的，
  `data/gfx/refined/water0.png` 不是。删的时候必须带完整相对路径，
  不能用 `find -name 'water*.png'` 这类会误伤顶层的写法。
- 实机必须**专门看一遍 blockout 模式**，refined 模式看不出这类误删。

### 批次 D —— 低风险但收益微小，收益 0.14 MB

`gfx/wall{0,1}.png`（2）+ `gfx/{bear,plant,snake,troll,wolf}.png`（5）

- 结论本身是确定的（§2），但 141 KB 的收益换一次完整三模式回归，性价比最低。
- **务必不要顺手把 `hero.png` 一起删**（§4），它和这 5 张生物图在同一目录、同一时期、同一尺寸量级。
- 建议单独成批，或者干脆留着。

### 每批都必须做的验证

1. `python3 tools/audit_dead_assets.py --check` 退出码为 0（无死资产、无缺图、清单无差集）。
2. `tools/package_runtime.py` 重新打包，PNG 全部 ZIP_STORED、与源码逐字节一致、
   `art/ tests/ tools/ docs/ evidence/ .git` 未入包。
3. 回归：`lua5.1` 跑 `terrain_contract`、`runtime_modes`、`token_mapping`
   （系统默认 lua 5.5 缺 `setfenv`，必须用 `lua5.1`）；`python3 -m unittest discover -s tests/production`。
4. 实机：隔离夹具 TEAA 冷启动，**`vanilla` / `blockout` / `refined` 三档各一遍**，
   Trollmire 与 Kor'Pul DEFAULT 两张图，48/64/96 三档地格。
   **blockout 这一档不能省** —— 批次 C/D 的误删只在 blockout 下才看得见。

### 预估收益（已实测，见 §6）

四批全做：包内成员 1983 → 372，包体积 **57.07 MB → 10.30 MB，减少 46.76 MB（81.9%）**。

---

## 6. 本轮做过又已回退的试删

为了给上面的预估一个实测数字，本轮曾按 §3 清单执行过一次删除 + 打包试验，**随后全部回退**：

- `git checkout -- data/gfx` 还原全部 1611 个文件，`data/gfx` 回到 1965 个 / 59 517 636 字节，
  `git status -- data/gfx` 为空。
- `init.lua` 的 `addon_version` 从试验中的 `{0,6,11}` 改回 `{0,6,10}`。
- 删除试验产物 `dist/tome-checker-revised-0.6.11.teaa`，
  `dist/runtime-SHA256SUMS` 重新指向 `tome-checker-revised-0.6.10.teaa`，
  SHA256 `3cb626bc7500a0930bfb6dffed8aeb516240aa00cba47b495cece9561d01f3be`，
  与 `PROGRESS.md` 记录的值一致。
- **没有**启动过游戏或 Xvfb。

试验期间打出的 0.6.11 包曾通过这些校验：372 个成员 / 354 个 PNG 全部 ZIP_STORED、
全部条目与源码逐字节一致、`art/ tests/ tools/ docs/ evidence/ .git` 未入包。
数据保留在 `evidence/dead-assets-20260927/trial-*`，
**仅作为下一轮的收益预估依据，不代表当前仓库状态**。

---

## 7. 脚本的可达集是怎么从代码派生的

`tools/audit_dead_assets.py` 的原则：**不手抄清单，让渲染器自己算路径**。
任何一处结构假设不成立就抛异常，而不是悄悄报一个更小的可达集。

| 环节 | 做法 |
| --- | --- |
| 森林 | 按行锚点从 `CheckerTerrain.lua` 切出 `local function img(` … `local function applyForest(` 这段源码，在 `lua5.1` 里 `loadstring` 执行。再用 `debug.setupvalue` 把 `terrainImage` 的 `terrain` upvalue 换成「原样返回身份」、`waterMask` upvalue 换成「返回指定掩码」，于是**真正的 `terrainImage` 函数体**在枚举域（7 身份 × 掩码 0..2^#dirs−1 × 12×12 格 × 三种模式）上跑一遍，输出的就是它能构造的全部路径 |
| 身份闭集 | 从 `terrain()` 函数体每条 `return` 语句后面抽单引号字面量。空集即报错 |
| 模式集 | 从 `CheckerOptions.lua` 的 `local modes={...}` 抽 `xxx=true` 的键 |
| 掩码位宽 | 森林取 `#dirs`、Kor'Pul 取 `#offsets`，都从模块自己的表读，不写死 4 |
| Kor'Pul | 同法切出 `local source=` … `function M.stairsReady(` 这段执行，然后**直接调用真正的 `M.assetPath`**。(kind, orientation) 对由模块自己的 `identities` / `doors` / `open` 按 `M.classify` 的同一规则重建；楼梯前景按 `M.render` 的写法由 `stairs` 表生成，并与源码里 `stairFiles` 的三条硬编码做**集合相等**断言 |
| 怪物棋子 | `loadfile` 加载 `CheckerTokens.lua`，对 `by_id` 每个 id 调用真正的 `M.image(id)` |
| UI 遮罩 | 从 `Actor.lua` 正则扫 `'_名字'` 与 `'_前缀'..变量`；后缀域由**实际调用** `CheckerTokenStyle.relation()`（穷举 reaction 与 actor==viewer）和 `.rankBadge()`（穷举 rank 0..20 步进 0.1）得到。遇到未登记的拼接变量名直接报错 |
| 字面量兜底 | 全仓 `*.lua` 搜 `checker-revised+<file>.png`，命中且确实存在于磁盘的标为「被引用」而非死资产（`hero.png` 就是这样活下来的） |
| 双向核对 | 派生集 ↔ 磁盘：多出来的是死资产，少掉的报 `missing_from_disk`；派生的 Kor'Pul 集 ↔ 两份 manifest 做对称差 |

因此**渲染器一改，脚本要么跟着变、要么抛错**，不会继续输出一份过期的手抄清单。
`--check` 在存在死资产、缺图或清单差集时返回 1，可以直接挂进打包流程做回归（本轮未接入）。

### 已知边界

- 脚本靠**行首锚点**切源码。若 `CheckerTerrain.lua` 里那几个函数改名或缩进，切片会失败并抛
  `source markers not found` —— 是显式失败，不是静默漏报。
- 脚本只覆盖本插件自己构造的路径。原生素材（`terrain/stair_up.png`、`invis.png` 等）不在范围内。
- 它判定的是「渲染器能不能构造这个路径」，不是「运行时是否真的请求过」。
  对删除决策这是更强的判据：构造不出来 = 一定请求不到。
