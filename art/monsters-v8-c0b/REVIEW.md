# C0b 静态美术审阅：出图 9 款，通过 8 款

2026-09-27。九个身份各自按 `art/production/handoffs/c0b-*/` 的 ready 任务调用
`tools/run_imagegen.py`（内置 ImageGen，`codex exec`）。**全批实际消耗 11 次调用**，
上限为 9×2=18 次。逐次记账在各任务包的 `imagegen-calls/call-N/call.json` 与
`ledger.jsonl`；失败的调用同样计数。

| 身份 | 调用 | attempt | 评审来源 | 结果 | 底盘偏移 | 扇区上偏 | 最大半径 |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| giant white mouse | 1 | 1 | initial | 入库 | +7.58 | +9.49 | 0.8585 |
| giant brown mouse | 1 | 1 | initial | 入库 | +1.76 | +6.92 | 0.8585 |
| giant brown mouse | 2 | 2 | external-review（人工看图） | **母版 RGB，拒收** | — | — | — |
| giant grey mouse | 1 | 1 | initial | 入库 | +6.54 | +6.83 | 0.8576 |
| giant rabbit | 1 | 1 | initial | 入库 | +3.98 | +7.88 | 0.8596 |
| giant crystal rat | 1 | 1 | initial | 入库 | +5.53 | +6.47 | 0.8559 |
| brown mold | 1 | 1 | initial | 入库 | +5.65 | +3.53 | 0.8559 |
| green mold | 1 | 1 | initial | 入库 | +0.65 | +2.05 | 0.8576 |
| shining mold | 1 | 1 | initial | 入库 | +7.87 | +5.17 | 0.8596 |
| skeleton warrior | 1 | 1 | initial | **圆盘越界，拒收** | +4.66 | +4.31 | **1.1049** |
| skeleton warrior | 2 | 1 | initial | **圆盘越界，拒收** | +3.78 | +5.07 | **1.0172** |

判据：底盘偏移 ±8、扇区上偏 ≤+20、最大不透明半径 ≤0.867、母版 RGBA 原生 alpha
且跨 0–255、四角透明、占格 0.83–0.91。**八款入库件全部以 `allow_grandfather=False`
通过**，不吃 GRANDFATHERED 豁免；`tools/check_token_style.py report` 对这八个 id
判定 PASS 且 `grandfathered=false`。`giant white mouse`（+7.58）与 `shining mold`
（+7.87）被报告标为「偏移逼近阈值」，读表时不要当成干净。

工具返回尺寸均为 1254×1254 RGBA，alpha 0–255、四角透明；`record` 核对原图与
保存母版逐字节一致。所有回执保持 `accepted:false`、`visual_review/runtime_review:pending`
的机械原始状态；美术接受以下面的看图结论为准。

## 两个失败与处置

### skeleton warrior —— 两次都圆盘越界，**本批剔除，交回设计**

两次返回的都是造型基本正确的着甲骷髅，但双手巨剑的剑身都伸出圆盘：
最大不透明半径 1.105 与 1.017，判据上限 0.867（提示词已明确写「整条剑刃连剑尖
留在盘内、外环第六留白」）。首轮那张还多画了一条手臂。**两次调用即为该身份的
全部配额，按规范停下，不发起第三次、不另建批次绕过计数。**
它**没有进入 `CheckerTokens.catalog`，没有进入 `data/gfx/tokens`，没有进包**；
运行时该身份继续保留原生贴图，`tests/live_c0b_scene.lua` 对它断言原生回退。

交回设计的具体结论：这套构图里「斜举的双手巨剑」与 0.867 的圆盘半径本身冲突。
下一次的定向 brief 应改动作而不是改判据——例如剑身贴着身体竖持、或沿盘内弦向
横置并缩短刃长、或改画收剑入鞘的站姿。**不要调 `export_token.c` 的
`target_occupancy`，也不要把它加进豁免名单。**

### giant brown mouse —— 返修调用返回 RGB 假透明，保留首轮 v1

首轮 v1 各项机械判据均通过并已入库，但 48px 看图发现它仍是四足横身（见下节）。
因此按仓库流程写了**人工视觉评审** `imagegen-calls/human-review-attempt-2.json`
（`review_scale=48`，缺陷指向实际看过的 48px 导出），用 `art_tasks.py repair`
准备返修，再走包装器发起 attempt 2，记账 `review_source=external-review`。
返修图**姿态确实改对了**（端坐、圆耳抬起），但返回的是 `mode=RGB`、
alpha 恒 255 的图，背景被**画成了棋盘格图案**——正是规范明令禁止的
「抠白底/假透明」，母版 alpha 这一条任何情况下都不放行，因此当场拒收、未入库。
两次配额用尽，**保留首轮 v1**，把姿态问题记为待办（下一轮需要专门的 refinement brief）。

## 实际看图结论（48/64/96px 真实 C 导出）

已打开：八张母版；`exports/{48,64,96,128,256}/*.png` 共 40 张；
`exports/compare-*-{colour,grayscale}.png` 六张对照表（每张三行＝48/64/96px）；
以及已映射锚点 brown-rat / giant-white-rat / giant-grey-rat / grey-mold 的运行贴图。
对照表只用于审阅，不是运行资产。

| 对 | 48px 灰度 | 64px 灰度 | 结论 |
| --- | --- | --- | --- |
| giant white rat ↔ giant white mouse | 鼠是横长低伏条块、头在左下、尾自背上绕过；鼠标是竖立圆团、顶部两个亮圆耳凸起、细尾低垂向右 | 端坐姿态、前爪合拢与圆耳轮廓清楚 | **通过**：剪影（横条 vs 竖团）＋明暗分布（单一大面 vs 亮团＋两个中调耳盘）两维可分 |
| giant brown rat ↔ giant brown mouse | 两者都是四足侧身，**这是本批最弱的一对**；靠朝向相反（鼠头左下／鼠标头右下）、尾在反侧、身躯更短更圆、两只圆耳更大更立、吻部更钝区分 | 64px 上体型比例与耳朵差别明显，棕鼠的深色条纹背与鼠标较浅的圆背明度也不同 | **勉强通过**：可分维度多于两项且灰度成立，但**没有拿到设计想要的竖立姿态**，是全批最接近的一对，已记为待返修 |
| giant grey rat ↔ giant grey mouse | 鼠是暗色长条、头在右；鼠标是竖立圆团、圆耳高举、细尾拖向右下 | 直立抬爪姿态清楚 | **通过**：剪影＋姿态两维可分 |
| giant brown rat ↔ giant rabbit | 兔是低伏团块＋两片细长竖耳，**没有长裸尾**，只有一个圆尾球 | 巨大后腿与耳片更明显 | **通过**：不会读成大老鼠；与端坐圆耳的三款 mouse 也不混（长耳片 vs 圆耳盘、无尾 vs 细长尾） |
| giant white rat ↔ giant crystal rat | 晶鼠背线被硬边锯齿晶簇打断，暗底上一串硬边亮片，整体比白鼠暗 | 晶簇与毛的材质差别清楚 | **通过**：剪影（锯齿背线）＋明暗（暗底高频亮片 vs 均匀大亮面）两维可分，不是换色白鼠 |
| grey mold ↔ brown/green/shining mold | 四款灰度下形态各不相同：灰＝波浪褶莲座、棕＝同心环硬壳、绿＝鼓胀圆瘤堆、亮＝分开的细柱放射簇（最亮） | 同上，更清楚 | **通过**：三款新霉菌彼此之间以及与已映射灰霉菌都靠**形态**而非颜色区分，48px 灰度成立 |

霉菌是否会读成地形装饰：四款都坐在标准暗盘上、有独立投影与立体体块，48px
下仍是「盘上的一个东西」而不是地面污渍。实机截图（见下）里它们与石地板贴图
对比明显，不会被当成地格花纹。但这是静态判断，不含「玩家会不会忽略不动的怪」这一层。

**未解决项：** `giant brown mouse` 的姿态；`skeleton warrior` 整款。
两者都不靠追加调用解决，需要下一轮的定向 refinement brief。
