# V9-refine 静态美术审阅：出图 2 款，全部首轮通过

2026-09-27。两个身份各按 `art/production/handoffs/v9-refine-v1/` 的 ready 任务调用
`tools/run_imagegen.py`（内置 ImageGen，`codex exec`）。**全批实际消耗 2 次调用**，
上限为 2×2=4 次，两款都在 attempt 1 通过，**没有动用返修配额**。
逐次记账在各任务包的 `imagegen-calls/call-1/call.json` 与 `ledger.jsonl`。

| 身份 | 调用 | attempt | 评审来源 | 结果 | 底盘偏移 | 扇区上偏 | 最大半径 | 占格 |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: | ---: |
| giant brown mouse | 1 | 1 | initial | 入库 | +2.00 | +4.37 | 0.8576 | 0.8594 |
| skeleton warrior | 1 | 1 | initial | 入库 | +5.32 | +2.75 | 0.8559 | 0.8594 |

判据：底盘偏移 ±8、扇区上偏 ≤+20、最大不透明半径 ≤0.867、母版 RGBA 原生 alpha
且跨 0–255、四角透明、占格 0.83–0.91。**两款都以 `allow_grandfather=False` 通过**，
`grandfathered=false`、`waived=false`；没有把任何身份加进 GRANDFATHERED 名单，
没有改判据、冻结基线或 `export_token.c` 的 `target_occupancy`。
两张母版均为 1254×1254 RGBA、alpha 0–255、四角透明；`record` 核对原图与保存件逐字节一致。
回执保持 `accepted:false`、`visual_review/runtime_review:pending` 的机械原始状态；
美术接受以下面的看图结论为准。

另有一次 `--execute` 位置写错的命令（`generate ... --execute`）被 argparse 在发起前
拒绝（退出码 2，`imagegen-calls/` 未建目录），**没有消耗额度**，不计入上表。

## 与上一批的关系

本批是 **refinement brief**，不是 C0b 那两个 brief 的第三次重试；换设计方向的逐项
理由写在 [BRIEF.md](BRIEF.md)，并由任务包的 `refinement` 声明按 SHA-256 钉住
C0b 的 REVIEW 与回执。C0b 的任务包、回执与 `imagegen-calls/` 记账**一字未改**，
`art/monsters-v8-c0b/` 下的 8 张母版与全部导出件也**一字未改**——
`giant-brown-mouse` 的 C0b v1 仍在原处，只是不再被 `prepare_runtime_art.py` 选中。

## 实际看图结论（48/64/96px 真实 C 导出）

已打开：两张母版（1254px）；`exports/{48,64,96,128,256}/*.png` 共 10 张；
`exports/compare-*-{colour,grayscale}.png` 四张对照表（每张三行＝48/64/96px）；
C0b 的 `giant-brown-mouse` 48/64px 旧导出件（作为新旧对照）；
以及已映射锚点 `brown-rat` / `giant-white-mouse` / `giant-grey-mouse` /
`degenerated-skeleton-warrior` / `skeleton-mage` 的运行贴图。
另按 5 倍最近邻放大单独看了 48px 灰度三联图（brown rat / brown mouse v1 / brown mouse v9）
与（degenerated / warrior / mage）。对照表只用于审阅，不是运行资产。

| 对 | 48px 灰度 | 64px 灰度 | 结论 |
| --- | --- | --- | --- |
| giant brown rat ↔ giant brown mouse **v1（旧）** | 两者都是低伏四足横身，只有朝向相反、尾在反侧、背略圆 | 体型比例与耳朵能分，但仍是同一类剪影 | **这是 C0b 记录的最弱对**，本轮替换的原因 |
| giant brown rat ↔ giant brown mouse **v9（新）** | 鼠是横长低伏条块、头在左下、粗尾自背上绕过；鼠标是竖立圆团、头低向抬起的双前爪、两只大圆耳高举破开顶部轮廓、细尾向右下勾一个紧圈 | 竖 vs 横的体块差与「亮圆背＋两个中调耳盘＋胸下深核阴影」vs「单一均匀大面」的明暗差都更清楚 | **通过**：剪影＋明暗分布两维可分，且不靠体型大小 |
| giant brown mouse v9 ↔ giant white mouse | 白鼠标整体最亮、前爪低收于胸、头侧转、长尾向右画大弧 | 同上更清楚 | **通过**：明度档＋姿态两维可分 |
| giant brown mouse v9 ↔ giant grey mouse | **本批最弱的一对**：两者都是竖立中调团块。可分点是头部姿态（棕＝低头、双爪并到吻边形成一个暗缺口；灰＝抬头直立、单爪抬起）、体态（棕更矮胖、颈短；灰更瘦高）、尾（棕＝紧勾圈；灰＝拖向右下的直尾） | 64px 上头部姿态与尾形差别明确 | **勉强通过**：灰度下可分维度有姿态与体态两项，彩色里另有冷灰 vs 暖棕。这是换姿态之后新出现的最近对，如实记录 |
| degenerated skeleton warrior ↔ skeleton warrior | 退化者是低伏、宽、斜向散架的亮骨剪影，剑斜横过圆盘；本款是紧凑对称的竖直暗甲块，正中一条竖直亮钢条加一道横剑格 | 64px 上锈甲暗块与亮骨颅/前臂/胫骨的分区、以及剑格横杠都清楚 | **通过**：剪影（竖直紧凑 vs 低伏散架）＋明暗（暗甲为主 vs 通体亮骨）两维可分 |
| skeleton mage ↔ skeleton warrior | 法师是深袍＋法杖的斜向瘦削剪影，本款是方肩直立的硬边金属块 | 同上 | **通过** |

「双手巨剑」在 48px 下仍读得出来：剑贴身竖持后，画面上是一条从胸口贯到脚踝的
**冷灰亮竖条**压在锈红暗胸甲上，顶端一道横剑格。这正是为抵消「贴身＝糊成一团」
的风险而在 brief 里要求的明度与形状措施，实测成立。

## 一条如实记录的软缺陷

skeleton warrior 的**头盔顶盖压在圆盘斜边上**（生成端自己也在 `notes` 里提了这点）。
阻断判据没有触发：最大不透明半径 0.8559 ≤ 0.867，主体没有越出圆盘轮廓；
`subject_intrusion` 这项警告级判据实测 **+2.75**，是当前 46 款里第五低
（全集中位 +6.47，最差的 `forest-troll` 为 +34.93），因为头盔只占一个很窄的角度扇区，
而该判据取扇区中位、对窄角度侵入本来就不敏感——**这一点本身就是判据的已知钝角**，
记在这里以免后人把「+2.75」读成「头盔离盘边很远」。
本轮没有为此动用第二次调用：它既不违反任何阻断判据，也不比既有 46 款里任何一款更靠外，
而返修一张已经全项通过的图在 C0b 已经有过反噬记录（返修返回 RGB 假透明）。

**未解决项：** 无新增。`giant brown mouse` 的姿态与 `skeleton warrior` 的接入
这两条 C0b 待办本轮均已结清。新记入的软缺陷是上面那条头盔压斜边，以及
`giant brown mouse ↔ giant grey mouse` 成为灰度下的新最近对。
