# 可复用的 ImageGen 任务包

本工具只准备任务和审计文件，不生图、不启动游戏、不提交Git。生产代码在`data/hooks/overload/superload`之外，本目录不进入teaa。仓库根`AGENTS.md`及已安装的imagegen技能仍适用。

0.6.3更新：白鼠/灰鼠示例及C0批次已经生成并接入，历史hold任务包保留供阅读；对它们再次prepare会因“already mapped”拒绝，这是预期。新任务请复制schema并填入尚未覆盖的真实身份，不要删掉重复检测。

## 快速使用

在插件仓库根目录执行：

```sh
python3 tools/audit_completion.py
python3 tools/art_tasks.py prepare art/production/batches/shared-rodents-pilot-v1.json --out art/production/handoffs/shared-rodents-pilot-v2
python3 tools/check_token_style.py report
python3 -m unittest discover -s tests/production -p 'test_*.py'
```

已提交的[白鼠/灰鼠样例](batches/shared-rodents-pilot-v1.json)为`hold`；已经准备好的[交接目录](handoffs/shared-rodents-pilot-v1/)只有提示词预览，没有ImageGen调用文件。它们尚未生成，引用图也没有因“准备任务”而自动完成视觉审阅。

先在隔离夹具中确认最终原生身份、image/add_mos、shader/动画/潜行、来源和当前匹配返回理由，把记录放进证据目录；主代理审核后填写`render_evidence`（工作区相对路径＋SHA256），改为`ready`并使用新的任务包版本。地形需同样记录移动、视线、危险、交互与导出合同。**不要为了让脚本通过，把任意文件填成渲染证据。** 脚本只能验证文件未变，不能判定证据内容为真。

ready输出`imagegen-request.json`，只含内置工具支持的`prompt`、`referenced_image_paths`参数。接收代理必须先读取技能并实际打开所有参考图，再调用内置ImageGen。工具通常保存在Codex生成目录；将返回原图逐字节复制到新的`art/<batch>/masters/<id>-v1.png`。不要抠白底冒充原生alpha，不覆盖已选母版，不用Python绘图补画怪物。

```sh
python3 tools/art_tasks.py record art/production/handoffs/BATCH/ASSET --original /absolute/tool/output.png --saved art/BATCH/masters/ASSET-v1.png --attempt 1
```

`record`依赖Pillow，仅只读检查PNG。它核对原图与保存件字节一致、方形且至少512px、透明图**存储时就带原生alpha通道**（mode为RGBA/LA/PA或带tRNS的P；纯RGB直接拒收，不看`convert('RGBA')`之后的结果）、alpha取值跨0–255、四角透明、地板全不透明；不要求alpha最大值等于255（原生输出可能为252，判据取240），不强行把1254px缩成提示里的1024px。圆盘越界与底盘明度漂移要等128px导出件存在才能测，由`tools/build_monster_art.py`的门控负责，见下文[可测风格约束与门控](#可测风格约束与门控)。通过时仍写`accepted:false`、视觉/运行`pending`；透明角合格不等于无裁切、无棋盘假背景或小尺寸好认。

定向返修使用[repair.txt](templates/repair.txt)。写一个review.json，四字段均必填：`review_scale`、`observed_failure`、`required_change`、`invariants`；缺陷应指向已实际查看的小尺寸，例如“64px尾与躯干黏连”，不能只写“更好看”。

0.6.10 补口：`repair.txt` 原先只在「保持不变」那句里顺带提了 native RGBA transparency，
没有像 `creature.txt` 那样**显式禁止假透明**。这个缺口是实测复现出来的——C0b 的
`giant brown mouse` 返修图**姿态确实改对了**，但返回的是 `mode=RGB`、背景被画成棋盘格的
假透明图，被母版 alpha 判据当场拒收，白白烧掉该身份最后一次调用（见
`art/monsters-v8-c0b/REVIEW.md` 与该任务包的 `imagegen-calls/call-2/call.json`）。
现已把与 `creature.txt` 同等强度的要求补进 `repair.txt`：必须返回带原生 alpha 通道的
RGBA PNG，不得画白/灰/黑/棋盘格背景再让人抠，也不得返回不透明 RGB 图。

```sh
python3 tools/art_tasks.py repair art/production/handoffs/BATCH/ASSET path/to/review.json
# 实际打开首轮母版及风格参考；调用repair/imagegen-request.json，另存-v2原图。
python3 tools/art_tasks.py record art/production/handoffs/BATCH/ASSET --original /absolute/tool/output2.png --saved art/BATCH/masters/ASSET-v2.png --attempt 2
```

脚本保留首轮和返修的实际提示、引用和原图哈希；拒绝覆盖已有任务包/回执，拒绝第三次或跳号记录。它不是外部调用拦截器：未记账的调用、另建批次等仍须主代理审计，禁止用新目录洗掉返修计数。第二次失败交回设计；现有棋子的重绘需专门的refinement brief，本工具不会因名称重复自动放行。

0.6.10 起，这条「专门的 refinement brief」从口头约定变成**任务包里必须写出来的声明**。
重复检测本身**没有放宽**：没有声明时，已接入身份照旧被 `already mapped` 拒绝。
声明也**不是第三次尝试**——它要求写清换的是**设计方向**，并把上一批实际怎么收场
钉死在证据里，`record` 阶段会重新校验这些钉住的文件，事后改旧批次的回执来凑理由会被发现。

## 字段约定

- `schema:1`，`batch_id`及`asset_id`为小写字母/数字/连字符；每包1–4项，`max_attempts`为1或2。
- `native_name`精确原生身份；`scope`注明地区/变体/房间；不是运行替换键。
- `kind`：`creature`、`terrain-floor`、`terrain-prop`。`gate`为`hold`或`ready`，附`gate_reason`。
- `sources`：工作区相对`path`、`sha256`、1起始`line`、该行包含的`anchor`。有继承/回调时把相关文件都钉住。
- `references`：1–3张PNG，工作区相对路径/哈希/`role`/`note`。角色必须有`style`与`identity`，可另有`family`；不要传一整张图库让模型猜目标。
- `prompt_fields`：`subject`、`contrast`、`composition`、`palette`；地形另需`mechanics`。所有字段写最终要画的内容，不能夹带猜测规则。
- 角色`contrast_dimensions`至少二项：`silhouette`、`value`、`hue`。这是设计要求检查，不是脚本已经测出图像有区别。
- 地形`grid_contract`五项：`movement`、`sight`、`danger`、`interaction`、`export`。危险取决于实际Grid及地区回调；深水/沼泽水、普通树/硬树、炖锅不能混为一类。
- `refinement`：**仅当**`native_name`已在运行catalog里时必填，其余情况填了就报错。四个键缺一不可：
  `supersedes`（被取代的运行token id，须与catalog一致）、`previous_batch`（配额已用尽的那一批）、
  `design_change_reason`（≥80字符，写**设计方向**怎么变，不是「再试一次」）、
  `evidence`（≥1条钉住的路径/哈希，指向上一批的REVIEW或回执）。它只解开重复检测这一道，
  `max_attempts`仍是1或2，新批次的调用照样按目录计数。
- `render_evidence`：ready必需，路径/哈希列表。记录原生实例、资格及拟采用的精确接入合同，不要求还未存在的新图先通过实机。

任务输出为prompt、inputs、HANDOFF以及ready才有的调用JSON；所有调用由代理执行，脚本不启动SDK/CLI，不需要API key。

## 可测风格约束与门控

前面的规范是设计语言，这一节是**可测的数值判据**。判据由只读检查器
`tools/check_token_style.py` 实现，并作为阻断门控接在
`tools/build_monster_art.py` 的 128px 导出之后。提示词模板已经按这些判据改写，
目标是让生成阶段就朝合规去，而不是靠事后拦截。

### 度量方法（唯一口径）

对 128px 运行贴图：

1. 取环带 `0.72 <= d <= 0.84`，其中 `d = hypot(x+0.5-64, y+0.5-64)/64`，只计 `alpha >= 128` 的像素。
2. 按角度切 8 个扇区，扇区 0 从左侧起顺时针：`ang = (atan2(dy,dx)+pi)/(2*pi)`，`sector = min(7, int(ang*8))`。
3. 每扇区取亮度中位数，亮度 `L = 0.299R + 0.587G + 0.114B`。
4. 每扇区减去**冻结基线**的同扇区值，得 8 个偏移。
5. 取这 8 个偏移的**中位数**作为该款的底盘偏移。

第 5 步取中位而非均值是关键：它对 1–2 个被主体侵入或接触阴影污染的扇区免疫。

### 冻结基线

基线是写死在 `tools/check_token_style.py` 里的常量，**不在运行时从当前贴图集合重算**：

```
S0=72.09  S1=71.16  S2=64.66  S3=62.97
S4=65.21  S5=67.05  S6=74.33  S7=76.42
```

若基线随贴图集合重算，每加入一张有漂移的新图都会把基线朝它拉一点，跑够多批之后
门控就会被它本该拦截的资产驯化——这是反馈回路失效，必须用常量切断。溯源（37 个
token id、`data/token-manifest.json` 的 SHA-256、冻结日期、重算政策）与常量放在一起，
用 `python3 tools/check_token_style.py baseline` 打印。只有在对**现有**美术开过返修
批次并整体重导之后，才由人用 `baseline --recompute <dir>` 核对、手工改常量并同步溯源；
新增资产一律不重算。

### 验收表

| 检查项 | 判据 | 级别 |
| --- | --- | --- |
| 母版透明通道 | 母版必须是带原生 alpha 的 RGBA PNG，alpha 实际取值跨 0–255（上限容差 240，原生输出可能为 252）；纯 RGB 不合格 | 阻断 |
| 圆盘越界 | 最大不透明半径（alpha>=128）`d <= 0.867` | 阻断 |
| 底盘偏移 | 上述 8 扇区偏移中位落在 `[-8, +8]` | 阻断 |
| 主体侵入外环 | `max(单扇区偏移 - 本款中位) <= +20` | 警告 |
| 四角透明 | 四角 alpha = 0 | 阻断 |

母版透明通道这一条不是形式检查：实测本机 ImageGen 在提示词未明确要求透明时会返回
不含 alpha 的 RGB 图，而本文件明确禁止“抠白底冒充原生alpha”。`art_tasks.py record`
在收据阶段就按母版文件的实际 mode 判定，不看 `convert('RGBA')` 之后的结果；
圆盘与底盘偏移要等 128px 导出件存在才能测，由 `build_monster_art.py` 负责。

### 门控接在哪里

- `tools/build_monster_art.py`：128px 导出之后立刻调 `check_token_style.gate`。
  这里是“将来被逐字节拷进 `data/gfx/tokens` 的像素第一次存在”的时刻，
  且已有四角 alpha 与 occupancy 断言，风格判据与它们同层。不合格直接退出并给出实测值。
- `tools/art_tasks.py record`：只做母版原生 alpha 这一条，越早越好——
  RGB 母版在收据阶段就被拒，不会白白烧掉一次返修配额。
- `tools/prepare_runtime_art.py` 不重测像素：它按 `export-report.json` 的 SHA-256
  校验后逐字节拷贝，导出期的门控已经覆盖同一批字节；它只额外拒绝
  `style_gate.passed == false` 的条目，堵住“降级导出再悄悄发布”这条路。

判据本身**始终测量，无法跳过**。`--style-gate-advisory` 只把阻断降级为记录在案的
警告（`export-report.json` 里会出现 `advisory_downgrade: true`），用于诊断尚未定稿
的草图；这样的批次会被 `prepare_runtime_art.py` 拒绝，进不了 `data/gfx/tokens`。

现有 37 款中有 11 款按 `[-8,+8]` 口径不合规、1 款（`stone-troll`，0.905）圆盘越界。
用户已决定本轮不返修，因此 `check_token_style.GRANDFATHERED` 显式列出这 37 个 id
及冻结当天的实测值与运行 PNG 的 SHA-256，按 id 放行。豁免只覆盖
`disc_overflow` 与 `base_drift` 两项历史欠账；母版原生 alpha 与四角透明任何情况下
都不放行。字节或数值变化会在报告里被指出；某款返修达标后应把它从名单中删除，
而不是留着继续豁免。`--strict-style` / `--no-grandfather` 可查看不带豁免的原始判定。

### 报告模式

```sh
python3 tools/check_token_style.py report                  # 全部运行贴图，带豁免
python3 tools/check_token_style.py report --no-grandfather # 不带豁免，供决定是否开返修批次
python3 tools/check_token_style.py report --json
python3 tools/check_token_style.py check data/gfx/tokens/fox.png --master art/monsters-v2/masters/fox-v1.png
```

报告按底盘偏移排序，逐款给出实测值与判定，并单独标出“逼近阈值”的款
（例如 `bill` 的扇区上偏 +19.96，差 0.04 未触发警告；读表时不要把它当成干净）。
退出码：0 通过，1 有未豁免的阻断项，2 用法或读取错误。

### 失败过的三种度量方法（不要重走）

1. **直接取整盘均值**——会把“白色生物本来就白”误判成“底盘被调亮”，曾经误判四款。
2. **用面积反推半径** `R = sqrt(N/pi)` 再取 `0.74–0.82 x R`——环带会内移到 0.63–0.70，与主体重叠。
3. **跨图中位建模来分割主体与底盘**——会把底盘边缘的光照差异误判成主体。

另外已经排除的解释：这个漂移不是光照、不是接触阴影、也不是环境遮蔽，
已分别用 8 扇区归一化与内外带对照排除。底盘几何本身是统一的（由
`tools/export_token.c` 的 `target_occupancy` 保证），漂移只在底盘明度上。

## 固定美术规范

风格为有材质的桌游物件；森林感减少不是缺陷。**底盘是中性物理件**：它的暗盘与铜灰斜边明度不随生物本身明暗被带偏，白生物不许把盘调亮、黑生物不许把盘压暗，容差见上一节的验收表（相对冻结基线 ±8，不写死具体 RGB）。**主体不得伸入底盘外缘环带，也不得越出圆盘边缘**（`stone-troll` 是现存的越界个例）。**母版必须输出原生透明 alpha**，禁止交白底/棋盘底再抠。单体图保持统一俯视三分之四相机、左上光、暗盘与低调铜灰斜边；身份放在轮廓与大面明度，阵营/血弧/珍珠白护盾/等级由程序绘制。普通和elite不烘焙等级标识。完整轮廓留在自己的格内，右上等级/左上交互标记留余量。

同族至少两维不同。暗色生物必须有缩小后仍可辨的大面明部或边缘；不能用更亮的阵营环掩盖主体混成团的问题。晶体本来带色可保留低饱和身份色，但颜色不是唯一线索。灰度只是辅助，人仍需看实际48/64/96px导出。新家族先通过锚点及最难区分的一对，再展开。

地板为纯俯视低对比平面；构件透明、包含树干/支撑等完整结构，底地独立。通行、视线、危险分开编码；自然装饰不能像阻挡件。路线沿棋盘格组织，不能擅自修改地图路格布局来变窄。邻接掩码/棋盘明暗/尺寸复用现有C导出，不让ImageGen产出196格atlas。

## 交接与计费边界

接收代理只需本说明、单任务HANDOFF、来源片段、2–3张参考、验收表，不需要几十轮历史。Sol负责确定性准备与成熟模板执行；Astra负责新家族、复杂造型/规则合同。单批失败及时停止，主代理集成和提交。更多代理仍会消耗额度；本规范只能减少可避免的调用和重复上下文，没有实测前不宣称节省百分比。

回报格式：生成次数/原图路径/提示词路径/保留alpha/48、64、96的实际看图结论/同族混淆/未解决项。未经实机不得写“已覆盖区域”；未调用不得写“已生成”。

## 生成端包装器 `tools/run_imagegen.py`

前面的流程里，`art_tasks.py` 只准备任务包和审计文件，ready 时输出
`imagegen-request.json`，实际调用由人或代理手动执行、产物再手动 `record` 入库。
`tools/run_imagegen.py` 把这一段包起来，让「调用 → 门控 → 入库」变成一条可审计的命令。
它**不自己画像素**，也**不另建一套返修计数**：入库、回执、返修一律走
`art_tasks.py` 的既有接口，风格判据一律走 `check_token_style.py`。

### 链路

```
读 <pack>/imagegen-request.json（返修读 <pack>/repair/imagegen-request.json）
  ↓ codex exec --model gpt-6.1-sol --ephemeral -i <每张参考图> --output-schema … -o result.json --skip-git-repo-check
    （2026-09-30 起默认固定 gpt-6.1-sol 并带 --ephemeral，调用记录写入 codex_model／codex_ephemeral；
     此前的调用未指定模型，实际为 codex 默认 gpt-6-astra。`--model` 可覆盖，`--no-ephemeral` 可保留会话文件）
① 溯源校验：产物路径必须在 ~/.codex/generated_images/ 之下，文件名必须是 exec-<uuid>.png，
   且必须是本次调用期间新出现的
② 母版 alpha：mode 必须是 RGBA/LA/PA 或带 tRNS 的 P，alpha 跨 0–255
③④ 按 kind 分流（`gate_master()`）：
   - `creature`/`player` 走原有口径：tools/export_token.c 编出的 128px 圆盘导出 +
     check_token_style.check_asset（8 扇区底盘偏移、圆盘越界、占格），新资产**不吃
     GRANDFATHERED 豁免**。
   - `terrain-prop`/`terrain-floor` 走 `terrain_gate()`（地形没有圆盘几何，套用怪物
     门控只是巧合式误判，实测见下）：ACCEPTANCE A1（母版原生 alpha，角点容差
     `CORNER_ALPHA_MAX=4`）/A2（地板全不透明）/A8（构件不贴边、除
     `direction-mark`/`bog-misc-*` 白名单外须触底 25%）。
  ↓ 通过 → art_tasks.py record 逐字节入库，写回执与双份哈希
  ↓ 不通过 → 不入库，已复制的母版回滚删除，走返修
```

**为什么地形另开一条门控**：F1 批次（`art/terrain-f1-flooded/`）第一次真实调用
（`bog-tree-a` attempt 1）撞上 `base_drift +12.02`（容差 ±8）——这条判据测的是
"128px 画布某个同心圆环恰好落在树冠还是背景上"，对没有圆盘几何的树/浮木构件没有
意义。`terrain_gate()` 改用地形本来就该测的判据（ACCEPTANCE §7 有完整记录，含
`CORNER_ALPHA_MAX` 与 `bog-misc` 接地豁免各自的三次独立实测依据），`art_tasks.py
record` 的检查项不变、不受影响。回归测试：
`tests/production/test_run_imagegen.py::TerrainGateTests`。

**逐资产豁免是最后手段，不是常规路径**：`hardtree` 两次生成都在 A8.1（不贴边）上
以不到 1.1px（约 0.09%）之差落败，调用预算耗尽后由主代理逐张看图批准了一条
`art/production/waivers/a8-edge-margin.json` 里按 `(asset_id, 母版输出 sha256)`
精确匹配的豁免记录（详见 ACCEPTANCE §7.4）。这不是放宽 A8.1、不是给某个 asset_id
前缀开后门；隔离性由 `tests/production/test_run_imagegen.py::A8WaiverIsolationTests`
保证——错资产、错哈希、缺文件都不触发豁免。除非再有类似的、经主代理逐条书面批准
的个案，否则不要往这个文件里加新条目。

Monster batch A 的四项底盘明度例外另记于 `waivers/monster-batch-a.json`：逐项锁定母版与 128px 导出 SHA256、实测偏移和唯一获准的 `base_drift` 检查。`check_token_style.py` 仍报告原始不合规数值，只有双哈希相符且没有其他阻断项才标记通过；`run_imagegen.py` 对导出占幅额外检查也不能被豁免。其他失败图不得借此入库。

提示词按 `--output-last-message` 拿结构化结果，**不刮 stdout**。返回 JSON Schema 固定四字段：
`image_path`、`image_generation_tool_used`、`transparent_background`、`notes`。

codex 默认以 `--sandbox read-only`、`--cd <临时目录>` 运行，本任务包的提示词逐字嵌在信封的
`IMAGE BRIEF` 里；信封只约束「怎么调工具、怎么回话」，不改美术方向，两者分别记哈希
（`task_prompt_sha256` / `envelope_prompt_sha256`）。

### 溯源校验是防线，不是形式

`~/.codex/generated_images/` 只有内置 ImageGen 会写。本文件禁止「用 Python 绘图补画怪物」，
但**提示词层面的禁止不可靠**——codex 跑的是完整 agent，它完全可能自己写代码画图再保存。
因此产物必须溯源到该目录，实际路径与 codex 会话 id 一并写进记账；不在该目录就判失败并报
「疑似非 ImageGen 产出」。read-only 沙箱是第二道：agent 在沙箱里根本写不出文件。
残余风险：这条防线证明的是「文件由 CLI 的内置工具写出」，不证明画面内容没有被提示词诱导。

### dry-run 与 `--execute`

**默认 dry-run**，真正发起生成必须显式 `--execute`。dry-run 打印将要执行的完整命令、
参考图清单与哈希、入库目标路径、预计调用次数与剩余预算、以及完整的信封提示词，
不创建任何目录、不消耗额度。

```sh
# 预演
python3 tools/run_imagegen.py generate art/production/handoffs/BATCH/ASSET \
    --saved art/BATCH/masters/ASSET-v1.png
# 真的调用（消耗用户的 ChatGPT 订阅额度）
python3 tools/run_imagegen.py generate art/production/handoffs/BATCH/ASSET \
    --saved art/BATCH/masters/ASSET-v1.png --execute
# 看回执、返修与调用预算
python3 tools/run_imagegen.py status art/production/handoffs/BATCH/ASSET
```

`--no-record` 只跑到门控为止、不入库，用于链路自检；它照样消耗额度、照样记账。
`--request` 覆盖请求文件只允许配 `--no-record`——否则回执里的 `full_prompt` 取自任务包的
`prompt.txt`，与实际发出的提示词不符，回执就成了假的。

### 每次调用都记账，包括失败的

记账落在 `<pack>/imagegen-calls/`：每次调用一个 `call-N/` 目录，内含
`call.json`（完整记账）、`envelope-prompt.txt`、`output-schema.json`、`result.json`、
`stdout.log`、`stderr.log`、`export-128.png`（送进门控的那张导出件），
外加一行追加到 `ledger.jsonl`。`call.json` 至少记录：

| 字段 | 内容 |
| --- | --- |
| `task_prompt` / `task_prompt_sha256` | 任务包提示词全文与哈希 |
| `envelope_prompt_sha256` | 实际发出的信封哈希 |
| `references` | 每张参考图的绝对路径与 SHA-256 |
| `command` | 实际执行的 argv |
| `codex_session_id` | 由产物路径的父目录名得到 |
| `provenance` | 报称路径、解析路径、本次新出现的文件清单、判定与理由 |
| `original_output_path` / `sha256` | 产物原始路径与哈希 |
| `master_metrics` / `master_alpha_finding` | 母版 mode、alpha 取值域与判定 |
| `style_gate` | 冻结基线、8 扇区偏移、底盘偏移、最大半径、扇区上偏、占格、逐条判定 |
| `attempt` / `call_index` / `review_source` | 尝试序号、调用序号、评审来源 |
| `timestamp_started` / `timestamp_finished` / `duration_seconds` / `exit_code` | 时间与退出码 |
| `outcome` / `failure` | `recorded`、`gated-only`、`provenance-rejected`、`master-alpha-rejected`、`style-gate-rejected`、`record-rejected`、`codex-timeout`… |

失败的调用同样消耗了订阅额度，所以同样计数：**预算按 `call-*` 目录数算，不按 `call.json` 数算**，
即使记账文件因崩溃没写出来，这一次也不白送。

### 返修与 2 次上限

返修就是仓库既有的 v1→v2 定向流程，包装器只是自动化它：
`repair` 子命令重新实测已入库的首轮母版（不依赖上次运行的内存状态），
把门控实测值填成 review 的四个必填字段，调 `art_tasks.py repair` 生成
`repair/imagegen-request.json`，再跑一次同样的链路记 attempt 2。
首轮母版作为 **image 1（编辑目标）**发回去——这正是「在失败图的基础上修改」。

```sh
python3 tools/run_imagegen.py repair art/production/handoffs/BATCH/ASSET            # 预演
python3 tools/run_imagegen.py repair art/production/handoffs/BATCH/ASSET --execute
```

把失败图当参考会反向强化缺陷（例如底盘偏亮被一起继承），所以自动填的 review 把
**保持什么**（`invariants`：身份、姿态、镜头、构图、以及每一条**已通过**判据的实测值）
与**改什么**（`required_change`：具体到「压暗约 N 个亮度单位」「最大不透明半径从 X 降到
0.867 以内」）分开写，并明确声明编辑目标图上被点名的那几项**不得原样继承**。

**上限沿用既有的 2 次**，三处一起守：

- `art_tasks.py` 自身：`max_attempts` 只能是 1 或 2，拒绝覆盖已有任务包/回执，拒绝第三次或跳号；
- `repair` 子命令：只在 attempt-1 回执存在、attempt-2 回执不存在、`repair/` 未准备时才动手；
- 包装器的调用预算：单个任务包的 codex 调用总数硬顶在 `max_attempts`，**没有任何 `--force` 开关**。

预演不创建 `repair/`、不消耗预算。首轮若连收据都没过（例如 RGB 母版），`repair` 直接拒绝
——没有可编辑的目标，请按报告交回设计，不要用返修流程绕过。**第二次仍失败就停下**，
报告并交回设计；规范同样禁止用新目录洗掉返修计数。

### 「指标驱动返修」不等于「看图评审」

本文件要求 `observed_failure` 指向**实际看过的小尺寸缺陷**（例如「64px 尾与躯干黏连」），
不能只写「更好看」。而门控失败是**数值结论**，不是看图看出来的。两者必须能区分开：

- `observed_failure` 正文固定带前缀 `[metric/128px 自动判定，未经人工看图]`。
  这段字会进 `repair/review.json`、返修提示词和 attempt-2 回执的 `full_prompt`，抹不掉。
- 另写 `<pack>/imagegen-calls/repair-review-source.json`，含
  `review_source: "metric"`、`human_visual_review: false`、测量工具与尺度、首轮实测值。
- 记账与 `status` 输出里的 `review_source` 同为 `metric`。
  人工写 review 后直接调 `art_tasks.py repair` 的，包装器记为 `external-review`。

（`art_tasks.py repair` 强制 review.json **恰好**四个键，所以标记只能走正文＋旁注文件＋记账，
不能塞进 review.json。）

指标驱动返修**不替代**视觉评审：占格、圆盘、底盘明度合规，跟 48/64/96px 认不认得出、
同族会不会混、有没有裁切，是两回事。回执里的 `visual_review`/`runtime_review` 仍是
`pending`，`accepted` 仍是 `false`，仍要人实际看图。

### 已知限制

- 记账证明「文件由内置工具写出、字节没被改过」，不证明画面内容对。
- 本机 ImageGen 返回 1254×1254，不是提示词里的 1024；`record` 不强行缩放，导出器按 bbox 放置。
- 实测发现：**附上 RGBA 风格参考时，即使提示词没明确要求透明，也可能返回 RGBA**；
  「不要求透明就返回 RGB」这条失败模式依然存在，只是不是每次都复现。
  因此 ② 这道检查照常必要，不能因为「这次是 RGBA」就当它是形式。
