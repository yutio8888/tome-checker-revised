# E1 胶质（jelly / ooze）八款 —— 生成结果与可分性复核

2026-09-28。生图前准入见 `evidence/e1-art-gate/`；设计说明见 `BRIEF.md`；完整提示词
预演见 `DRYRUN.md`（已在 `750e987` 提交审核通过）。本节记录**实际生图**结果。

## 调用与门控

8 个身份，每款 `max_attempts=2`（上限 16 次），**实际消耗 8 次：全部首轮通过，零次返修**。
逐次记账在各任务包的 `imagegen-calls/`；风格门控 `allow_grandfather=False`：

| 身份 | 底盘偏移 | 最大不透明半径 | 单扇区最大上偏 | 128px 占格 | 判定 |
| --- | --- | --- | --- | --- | --- |
| green-jelly | +0.07 | 0.8576 | +3.74 | 0.8594 | 通过 |
| black-jelly | -0.32 | 0.8576 | +2.82 | 0.8594 | 通过 |
| white-jelly | -2.15 | 0.8576 | +5.05 | 0.8594 | 通过 |
| yellow-jelly | +3.00 | 0.8576 | +3.31 | 0.8594 | 通过 |
| black-ooze | +0.83 | 0.8596 | +4.51 | 0.8594 | 通过 |
| yellow-ooze | +1.25 | 0.8585 | +5.30 | 0.8594 | 通过 |
| red-ooze | +0.35 | 0.8596 | +5.17 | 0.8594 | 通过 |
| blue-ooze | -1.27 | 0.8596 | +8.50 | 0.8594 | 通过 |

阈值：圆盘越界 ≤0.867，底盘偏移 ±8，单扇区上偏警戒 +20（本批全部远低于警戒线），
占格区间 0.83–0.91。8 款全部在阈值内，没有告警（`warnings` 均为空），
没有使用 GRANDFATHERED 豁免（新资产本就不吃这条）。母版全部 RGBA 原生 alpha、
alpha 跨 0–255、四角透明、方形 ≥512px（实测 1254×1254，逐字节保留原图）。

## 同族可分性（真实 48/64/96px C 导出，色彩＋灰度）

对照表：`art/monsters-e1-gel/exports/compare-{jellies,oozes,black-pair-dark-subject,
yellow-pair}-{colour,grayscale}.png`（由 `compare.py` 生成，只读既有导出，不是运行资产）。

### 四款 jelly（`compare-jellies-*`）

灰度下四款轮廓清楚可分：green 是表面带斑点颗粒的圆润土丘；black 是最矮最摊的
不规则沥青堆，顶部有一道明显亮边打断纯暗轮廓；white 是带棱角切面的偏高圆顶；
yellow 是花瓣状多瘤块的开放轮廓，明显比其余三款"更炸"。48px 下四者仍可一眼分开，
没有互相混淆的风险。black jelly 在深色底盘上仍可读：亮边高光确实起了作用，
没有整体糊成一团暗色。

### 四款 ooze（`compare-oozes-*`）

黑/黄两款轮廓辨识度最高：black ooze 是低伏带一个明显伪足尖端的暗色团块；
yellow ooze 是最"锐利"的火焰状拖尾，一眼就能认出方向性。red 与 blue 是本组里
相对**较接近的一对**：两者都是圆润团块带若干小裂片，48px 灰度下主要靠"blue 的
裂片更尖锐、更像放射状霜棱，red 的裂片更圆润下垂"来分，色相辅助明显（暖红 vs
冷白蓝），单看灰度剪影时二者的可分性弱于 black/yellow 与其余款的差距，但仍能
分辨出 blue 的锯齿感比 red 的圆润感更强，达到设计要求的"至少两维"（silhouette
+ value：blue 整体明度更高更冷、裂片更硬）。

### jelly vs ooze 同色对照（`compare-black-pair-dark-subject-*`、`compare-yellow-pair-*`）

**yellow 对照很强**：yellow jelly 是紧凑对称的圆顶花瓣团块，yellow ooze 是明显
向一侧拖出的尖锐火焰状拖尾，48px 灰度下两者的剪影语言（对称丘状 vs 定向拖曳）
一眼可分，符合"jelly 固定不动、ooze 会动"的设计意图。

**black 对照是本批最弱的一对，如实记录**：black jelly 与 black ooze 都是深色、
高光泽、依赖亮边轮廓的暗色团块，48px 灰度下第一眼的"暗色发亮的团"观感确实接近。
放大细看仍可分辨——jelly 更居中、更紧凑，顶部亮边把轮廓切成几个圆润凸起；
ooze 明显向左下方拖出一个更细长的伪足尖端，整体呈现更狭长不对称的形状——
但这个差异比其余任何一对（green/white/yellow jelly 之间、black/yellow ooze
之间）都更依赖仔细看而不是一瞥可分。两者都各自单独满足契约要求的两维差异
（silhouette：紧凑团块 vs 拖长伪足；value：两者都是近黑打亮边，value 维度上
彼此之间反而区分度不足，主要靠 silhouette），因此判定**可接受但是本批可分性
最弱的一对**，如果后续实机 48px 观感仍不理想，应优先安排 black-ooze 或
black-jelly 的定向重绘（不是本轮：本轮两者都过了机械/风格门控，没有触发返修
条件，没有消耗额外调用）。

## 结论

8/8 接受入库，0 次返修，0 剔除。母版路径 `art/monsters-e1-gel/masters/<id>-v1.png`，
128px 运行导出 `art/monsters-e1-gel/exports/128/<id>.png`，完整记账见各任务包的
`imagegen-calls/`（`call-1/export-128.png` 即门控实测的那张图）。下一步：接入
`overload/mod/class/CheckerTokens.lua` 目录与 `data/token-manifest.json`，见
`PROGRESS.md` 0.6.13 小节与 `evidence/runtime-v0613/`。
