# F1 洪水沼泽地形 — 生图与导出复核

2026-09-28。配套 [BRIEF.md](BRIEF.md)、[DRYRUN.md](DRYRUN.md)。本文件记录真实生图（`--execute`）的调用来源、门控实测、导出结果与人工视觉复核；不含任何提交操作。

## 1. 六款资产的调用来源

| 资产 | 母版 | 入库来源 | 母版 sha256 | 备注 |
| --- | --- | --- | --- | --- |
| `bog-tree-a` | `masters/bog-tree-a-v1.png` | `imagegen-calls/call-2`（attempt 1） | `428cd6d…` | call-1 被旧的怪物圆盘门控误判（`base_drift +12.02`，判据不适用于地形，见 §2）；call-2 在修复门控后重新实测通过，**没有额外调用**——call-1 已生成的图像同样通过了修复后的门控（sha256 `c6df291…`），但按记账时序，实际入库的是 call-2 产出的字节。 |
| `bog-tree-b` | `masters/bog-tree-b-v1.png` | `imagegen-calls/call-2`（attempt 1，call-1 是修复前的旧门控探测，见下） | `b625c55…` | 该资产只发起过一次真正计入 codex 会话的生成（`call-2`）；`call-1` 目录是门控修复前对同一次任务包状态的一次尝试，实际只消耗了 1 次 codex 调用（见 `imagegen-calls/ledger.jsonl`）。 |
| `bog-misc-1` | `masters/bog-misc-1-v1.png` | `imagegen-calls/call-1`（attempt 1） | `49839e9…` | 一次通过，四角 alpha 全为 0。 |
| `bog-misc-2` | `masters/bog-misc-2-v1.png` | `imagegen-calls/call-1`（attempt 1） | `fd22295…` | 一次通过，四角 alpha 全为 0。 |
| `bog-misc-3` | `masters/bog-misc-3-v1.png` | `imagegen-calls/call-1`（attempt 1） | `87f1975…` | 一次通过，四角 alpha 全为 0；驱赶"像桥"的构图约束生效（见 §4）。 |
| `hardtree` | `masters/hardtree-v1.png` | `imagegen-calls/call-2`（attempt 1，**逐资产豁免**） | `442c841…` | call-1、call-2 均因 A8.1（不贴边）以 <1.1px 之差落败；调用预算 2/2 已耗尽；主代理看图后按 `art/production/waivers/a8-edge-margin.json` 批准逐资产豁免入库，见 §3。 |

全部 6 款均已用 `python3 tools/art_tasks.py record` 逐字节入库（`preserved_original_bytes: true`），回执在 `art/production/handoffs/f1-flooded-v1/{trees,bog-misc}/<asset>/receipts/attempt-1.json`。

## 2. 门控修复（bog-tree-a attempt 1 的教训）

`tools/run_imagegen.py --execute` 原本所有资产统一走 `export_token.c` 的 128px 圆盘裁切 + `check_token_style` 的 8 扇区底盘偏移门控。`bog-tree-a` 第一次真实调用（一棵没有圆盘几何的柳树构件）被该门控以 `base_drift +12.02`（容差 ±8）拒收——这条判据测的是"某个同心圆环恰好落在树冠还是背景上"，对地形构件没有意义。

修复：新增 `terrain_gate()`，按 `kind` 分流，terrain-prop/floor 改用 ACCEPTANCE A1/A2/A8。修复后重新实测 call-1 的原始产物（sha256 `c6df291…`），确认它其实也通过；但因为记账时序已经推进到 call-2，实际入库的是 call-2 的字节，两者内容等价（同一提示词、同一参考图，肉眼判断风格一致，见下方 §5 的图）。完整分流实现、`CORNER_ALPHA_MAX=4` 容差、`bog-misc-*` 接地豁免的实测依据均记在 [ACCEPTANCE.md §7](../../docs/g0-terrain-contract-20260927/ACCEPTANCE.md#7-f1-批次门控实现与已接受实测偏差2026-09-28)。回归测试：`tests/production/test_run_imagegen.py::TerrainGateTests`。

## 3. `hardtree` 逐资产豁免

两次生成都只在 A8.1（画布四边 ≥0.02×N 不贴边）上失手，且都只差 1px 量级：

- call-1：包围盒 `(18,22,1236,1228)`，画布 1254px，要求边距 ≥25.08px；左/上/右三边不足。
- call-2：包围盒 `(38,24,1227,1203)`；仅上边不足（24px vs 25.08px，差 1.08px），左/右/下三边通过且余量充足。

主代理实际看过 call-2 的图（见 §5），确认树冠饱满、主干粗壮扭曲、明显比 oak/pine 更厚重，肉眼看不出贴边，是构图层面的近似命中而非内容缺陷。此时该任务包的 `max_attempts=2` 已耗尽（两次调用都计入预算，无论是否入库），不满足重新生成的条件。

处理：主代理批准 `art/production/waivers/a8-edge-margin.json` 中按 `(asset_id="hardtree", 母版原始输出 sha256="442c8415…")` 精确匹配的一条豁免记录，只改写这一条 `not_edge_touching` 判定，不动 A8.1 阈值本身，也不给其他资产或哈希开口子。隔离性由 `tests/production/test_run_imagegen.py::A8WaiverIsolationTests` 保证（错资产、错哈希、缺文件均不豁免）。`art_tasks.py record` 的记录阶段本身不检查 A8，因此入库这一步不需要豁免即可通过（只检查 A1 母版透明与四角，两者本就合格）。调用预算保持 `2/2`，未重置、未发起第三次调用。

## 4. 视觉复核（B1/B2/B6/B8 摘要，见 `exports/review-sheet-64.png`）

64px 对照图（`grass / tree-oak / tree-pine / hardtree / deep(mask0) / bog(mask0)` 一行，`bog-tree-a(m0) / bog-tree-b(m0) / bog-tree-a(m15) / bog-misc-1/2/3` 一行）人工实际看过：

- **B2（普通树 vs 硬树）**：`hardtree` 在 64px 灰度/彩色下都明显比 `tree-oak`/`tree-pine` 更密实厚重——主干更粗、树冠更圆更满，达到"至少两维不同"（剪影＋明度）。
- **B6（深水 vs 沼泽水危险语义）**：`deep(mask0)` 冷暗蓝绿、`bog(mask0)` 浅灰绿，两者一眼可辨深浅；`bog-tree` 站在 `bog` 水色的底地上，没有被误画成毒水的黄绿色调（对照 `docs/g0-terrain-contract-20260927/BRIEF` 阶段就做过的 `bog-vs-deep-vs-poison-96.png` 数值代理，这次是实际运行贴图的直接目视确认）。
- **B1（通行语义）**：`bog-misc-1/2/3` 三款（芦苇丛、苔藓团、浮木）都读成贴着水面的矮装饰，没有一款读成矮墙/围栏/桥——尤其 `bog-misc-3`（浮木）在提示词里明确要求"短、断裂、斜置，不得贯穿两端"，实际生成结果两端都收束变细并明显折断，不连续跨越格子，通过复核（见 DRYRUN.md 的风险提示）。
- **B8（棋盘明暗）**：`bog-tree-a(m0)` 与 `bog-tree-a(m15)` 对照可见 mask0（四边都补岸）与 mask15（全连通，四边留通）的水岸处理正确——mask0 四周有明显岸线，mask15 边缘直接是开阔水面，符合 CONTRACT §8 的"底地随掩码"设计。
- **A5（掩码位局部性，代码实测，非目测）**：对 `bog-tree-a`/`bog-tree-b` 全部 16 掩码 × 4 位的边界像素比较，`max|ΔRGB|=0`（排除角落 M=12），逐位精确匹配 ACCEPTANCE A5 的判据与既有森林水套件同款结果。
- **A4（棋盘奇偶）**：`bog-tree-a/b`、`bog-misc-1/2/3`、`tree-hard` 的 parity0/1 中位比值全部落在 0.8947–0.8952，与既有森林套件声明的 `k=0.895` 一致（差 ≤0.0005），alpha 通道两侧逐字节相同。
- **A7（岸的存在性）**：`bog-tree-a/b` mask0（北边未连通）实测北边中心亮度差约 18–20（阈值 ≥8），有明显岸线，通过。

尚未做的人工项（超出本轮时间预算，供后续验证记录，见 §6）：把 `bog-tree`/`bog-misc` 铺成整片水域看拼图观感（B5）、把精修格贴在原生格旁边看交界（B9）——这两项要在实机隔离夹具里才能真正看到，不是这一步截图能替代的。

## 5. 母版原图（人工审阅记录）

生成阶段已逐张打开确认：无白/灰/棋盘格假透明背景，主体结构完整（trunk/roots/branches 齐全，不是只有树冠碎片），无阵营色/文字/稀有度标记，无原生规则未声明的危险暗示（沼泽水没有画成毒绿色，浮木没有画成桥）。四角 alpha 详见各资产的 `metrics.corner_alpha`（bog-tree-a/b/hardtree 为 `[0,0,1,0]`，在 `CORNER_ALPHA_MAX=4` 容差内；三款 bog-misc 为 `[0,0,0,0]`）。

## 6. 导出

`tools/export_forest_terrain.c` 扩展为支持两款 `bog-tree` 风格变体（`prop-bog-tree-a.png`/`prop-bog-tree-b.png` → `bog-tree-a<mask>-<parity>-0.png`/`bog-tree-b<mask>-<parity>-0.png`，16 掩码 × 2 奇偶 × 2 变体 = 64 张）与可选的 `hardtree`（`prop-tree-hard.png` 存在则导出 `tree-hard<parity>.png` 2 张，不存在则跳过、身份保持原生——回归测试 `test_forest_exporter.py::test_hardtree_is_optional_and_stays_out_when_its_master_is_absent`/`test_hardtree_is_included_when_its_master_is_present`）。

本轮实际导出：`bog-tree-a`×32 + `bog-tree-b`×32 + `bog-misc-{1,2,3}`×6 + `tree-hard`×2 = **72 张运行件**，已用 `cc -O2 -Wall -Wextra` 编译（零警告）并逐字节写入 `data/gfx/refined/`（现有 78 张非泛滥森林瓦片完全未被这次导出触碰——只读取了它们的既有派生母版作为 MASTERS 输入，OUT 目标写到临时目录，从未覆盖 `data/gfx/refined/` 里已有的 78 个文件）。128px/48px/64px/96px 复核件、A4/A5/A7 代码实测见 §4。

复核缩放件在 `exports/{48,64,96}/*.png`（每个运行件一份，72×3=216 张）与 `exports/review-sheet-64.png`（本文件 §4 引用的对照拼图）。72 个安装文件的完整 sha256 清单在 `export-manifest.sha256`（`data/gfx/refined/<file> = <sha256>`，用于打包阶段的字节校验）。

## 7. 与运行时集成的边界

本文件只记录美术与导出；`overload/mod/class/CheckerTerrain.lua` 的身份分类、门控收紧、`hooks/load.lua` 文案与本地化的改动记录在 `PROGRESS.md` 与相应的 commit message 里，不在本文件重复。
