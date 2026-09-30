# 怪物棋子批次 AC 选型（2026-09-30，接在批次 AB 之后，最终批，不升版）

来源：`docs/expansion-plan-20260928/MONSTER-GAP-2-20260929.md` 「### 后续（未排批）」。计分口径与批次 R–AB（`art/monster-batch-ab/SELECTION.md`）逐字相同；复算脚本是批次 AB 脚本的拷贝（`art/monster-batch-ac/score_candidates.py`，仅改了输出注释路径），按当前 `CheckerTokens.lua`（359 条，含批次 AB）过滤已收录 name，剔除 §7 批次 1–8 已排的身份和 §4 判 I／N／K 的身份，剩 18 条（含 Training Dummy）。

## 结果

Training Dummy（12.0，批次 T 起留原生）仍在脚本输出顶端，本批不考虑。其余 17 个真实候选**全部**收入（最终批，无需破并列）：

| 排名 | 分值 | 身份 | 中文名（mod-tome.lua） | 说明 |
|---:|---:|---|---|---|
| 1 | 0.6 | Aletta Soultorn | 阿蕾塔·苏尔顿 | 唯一，dreadfell（行 682）；define_as ALETTA；64×64 |
| 2 | 0.6 | ruin banshee | 毁灭女妖 | rak-shor-pride 池＋greater-crypt vault（行 683）；64×64 |
| 3 | 0.6 | Filio Flightfond | 菲里奥·弗莱特冯德 | 唯一，dreadfell（行 884）；define_as FILIO；64×64 |
| 4 | 0.5 | orc high pyromancer | 高阶兽人烈焰术士 | vor-armoury＋renegade-pyromancers vault（行 581）；64×64 |
| 5 | 0.5 | orc high cryomancer | 高阶兽人冰霜术士 | vor-armoury（行 582）；64×64 |
| 6 | 0.5 | Glacial Legion | 冰川军团 | 唯一 tall，rak-shor-pride（行 684）；define_as GLACIAL_LEGION |
| 7 | 0.5 | Arch Zephyr | 阿克·伊法 | 唯一 tall，rak-shor-pride（行 752）；define_as ARCH_ZEPHYR |
| 8 | 0.5 | Rotting Titan | 腐烂泰坦 | 唯一 tall，rak-shor-pride（行 792）；define_as ROTTING_TITAN |
| 9 | 0.5 | Heavy Sentinel | 笨重的森提内尔 | 唯一 tall，rak-shor-pride（行 802）；define_as HEAVY_SENTINEL |
| 10 | 0.5 | Void Spectre | 虚空亡魂 | 唯一 tall，rak-shor-pride（行 893）；**无 define_as**，同 Hedge-Wizard 走唯一高图路径 |
| 11 | 0.4 | oozing horror | 黏液恐魔 | lake-nur（行 670）；64×64 |
| 12 | 0.4 | abyssal horror | 深渊恐魔 | lake-nur（行 730）；tall，nice_tile 显式 → native_tall |
| 13 | 0.3 | ungolmor | 阿格尔莫 | ardhungol（行 627）；64×64 |
| 14 | 0.3 | umbral horror | 暗影恐魔 | lake-nur（行 671）；tall，nice_tile 显式 → native_tall |
| 15 | 0.3 | vampire lord | 吸血鬼领主 | dreadfell 池＋greater crypt／paladin-vs-vampire vault（行 751）；显式 image=；64×64 |
| 16 | 0.0 | degenerated ogric mass | 退化的食人魔肉团 | conclave-vault（行 655）；tall，`nice_tile{tall=1}` → native_tall |
| 17 | 0.0 | ogric abomination | 憎恶食人魔 | conclave-vault（行 656）；tall，`nice_tile{tall=1}` → native_tall |

中文名以 zh_hans 的 `/workspace/tome4-chinese-translation/mod-tome.lua` 为准。

## 保持原生的项

- **Training Dummy**：批次 T 起排除，保持原生（唯一未映射的调研候选）。
- **Vilespawn**（Corpathus 神器召唤的小怪，`world-artifacts.lua:3443`）：用 oozing horror 的 PNG，但名字、字段全是神器里硬编码的另一个单位，不是 oozing horror 的召唤物；映射需要目录目前没有的“名字别名”机制。保持原生，已在测试与证据里记录，供后续决定。
- 无候选因运行时外观变化、纸娃娃或无稳定身份被判不可支持：17 个源码逐条核过（叶子与 base 无 image=／shader／moddable_tile／anim／add_displays；天赋与 timed_effect 的显示写入集合同批次 S–AB，另有 Burning Wake、Crystalline Focus、Golem Reflective Skin 三个原生 shader-aura 记账，匹配器忽略）。

## 选定 17 个（源码逐条重核，合同见 `evidence/monster-batch-ac-20260930/source-contracts.json`）

七个唯一怪各自独立的棋子（Void Spectre 无 define_as），五个唯一高图不带 native_tall（走 unique 路径，同 Hedge-Wizard／Kyless／Walrog），四个非唯一高图带 native_tall=true，八个 64×64 单图（其中两个唯一）；六个绑定 define_as。**同体形／召唤**：vampire lord 的 Summon 建的是随机亡灵叶子（各带自己的棋子）；umbral horror 的 Shadow Warriors／Focus Shadows 建 subtype shadow 盟友，不是自身的副本；orc high pyromancer 的 renegade-pyromancers 随机首领“the Invoker”走既有平面 captureRandomOrigin（测试有正例）；四个非唯一高图的随机首领走既有的“保持原生”（测试有反例）。

## 分包

- Pack 1：Aletta Soultorn、ruin banshee、Glacial Legion、Filio Flightfond
- Pack 2：orc high pyromancer、orc high cryomancer、vampire lord、ungolmor
- Pack 3：Arch Zephyr、Rotting Titan、Heavy Sentinel、Void Spectre
- Pack 4：oozing horror、abyssal horror、umbral horror、degenerated ogric mass
- Pack 5：ogric abomination
- Pack 6 orc high pyromancer 重做（pack 2 半径 0.941，双臂与火球越界）；pack 7 orc high cryomancer 重做（1.034，长杖与冰片越界）；pack 8 vampire lord 重做（1.008，细剑与披风越界）；pack 9 ungolmor 重做（pack 2 未返回路径）；pack 10 Rotting Titan 重做（pack 3 底盘偏移 -9.02，巨体在盘面投下暗影）；pack 11 oozing horror 重做（pack 4 “Selected model is at capacity”，无图）；pack 12 ogric abomination 重做（pack 5 底盘偏移 -10.64＋subject_intrusion 警告）；pack 13 vampire lord 第三次（pack 8 数值全过，但 48px 是小而暗的芥末褐团，亮度 70.4）
- 半径越界连续三次后，尚未运行的 pack 3–5 在第一次调用前就加上了“整体缩到盘半径约 0.58 内、武器与效果贴身”的校准语（整包重新生成，无任何调用被丢弃）。

## 设计约束（生图前定的，不是事后补）

沿用批次 R–AB 的评审教训：主体大块面一律中亮到亮，沿轮廓一圈亮边光，禁止黑色主体；`DARKFIX` 段用于原图近黑或偏暗的主体。幽灵与灵体类另加“整体不透明实体绘制”一句，避免半透明。

同族区分（对照既有棋子，非仅换色）：

- Aletta Soultorn：纤细、尖叫、双臂大张的兰紫与淡紫幽灵女子，银色紫晶发冠、白发飘散；对既有青色 banshee、青绿 Kor's Fury、青白 grave wight、蓝紫兜帽的 dread／dreadmaster。
- ruin banshee：佝偻带爪、尖叫的酸绿与炭橙幽影，恶魔空间蒸汽；对既有直立优雅的青色 banshee。
- Glacial Legion：巨大的霜白冰雾水滴形，深红冰封血球居中；对既有细长青色幽灵与蓝色晶体 Shade of Telos。
- Filio Flightfond：矮小蹑足的象牙白骷髅，软底靴、梅紫围巾，甩弹弓与短匕首；对既有法袍骷髅、金甲弓手骷髅。
- orc high pyromancer：宽袖、双手火球、火焰冠冕、金边肩甲、腰间火环的绯红礼袍兽人；对既有单手小火焰的素袍 pyromancer。
- orc high cryomancer：白与冰蓝礼袍、白毛领、冰晶王冠、雪花晶杖与冰片螺旋的持杖兽人；对既有素蓝袍 cryomancer，与高阶烈焰术士的姿态互异。
- Arch Zephyr：风吹长袍的灰蓝弓手，拉满缠绕闪电的长弓；对既有紫兜帽长老吸血鬼、红／蓝披风吸血鬼。
- Rotting Titan：鼠尾草灰玫瑰色腐肉与石灰岩板融合的巨大躯体，每肢末端巨石拳；对既有瘦长褐色食尸鬼、粉褐肉团、食人魔。
- Heavy Sentinel：灰白骨板被熔橙缝隙熔铸成甲，敞开的肋骨炉膛喷出火柱，有角熔骨头骨；对既有素褐骨巨人、符文骨巨人。
- Void Spectre：玫红与洋红奥术能量的兜帽瘦削幽影，白热面缝，淡紫符文环绕；对既有青、绿、蓝的 wight 与灵体。
- oozing horror：巨大的青柠色黏液丘，七八只橙琥珀色大眼；对既有小型闪亮 ooze／jelly、粉色 bloated horror。
- abyssal horror：靛紫与青石板色的触手团，中心埋着猩红眼睛；对既有石柱青触手 entrenched horror、鱼头 ravenous horror。
- umbral horror：珍珠灰与暮紫烟状阴影的低伏尖刺猎手，钩爪与淡黄眼睛；对既有紫色 horned horror、weirdling beast。
- ungolmor：厚皮层层折叠的低矮圆顶重装蜘蛛，石板蓝灰、银色脊线、琥珀眼；对既有瘦长灰蜘蛛、骨白蜘蛛、黑色 Ungolë。
- vampire lord：赭金长袍贵族，青铜褐披风衬猩红里，举短剑；对既有红／蓝披风、梅紫兜帽吸血鬼。
- degenerated ogric mass：赭褐与鲑肉色塌陷肉堆，肿瘤、畸形融合肢体与半埋的獠牙食人魔脸；对既有直立食人魔与粉褐 necrotic mass。
- ogric abomination：灰紫斑驳的食人魔，一臂换成带紫青符文的巨大石质傀儡臂、螺栓石板与巨槌；对既有褐、红、蓝、板甲食人魔。

## ImageGen 记录

**25／34 次**（`gpt-6.1-sol`＋`--ephemeral`，逐次串行，只用 run_imagegen.py 默认）。十七款各至少 1 次，另八次返工（每款至多 3 次）：

- orc high pyromancer（2 次）：首次最大不透明半径 0.941 越界，未入库；pack 6 手臂内收、火球贴肩，一次入选，掩膜亮度 100.4。
- orc high cryomancer（2 次）：首次 1.034 越界，未入库；pack 7 短杖、冰片紧贴，入选，129.9。
- vampire lord（3 次）：首次 1.008 越界，未入库；pack 8 短剑、披风贴身，数值全过但 48px 小而暗（70.4），移入 `superseded/`；pack 13 亮藏红金＋乳白袍、亮猩红衬里，v2 入选，84.6。
- ungolmor（2 次）：首次未返回路径（provenance-rejected），重跑入选，85.6。
- Rotting Titan（2 次）：首次底盘偏移 -9.02（巨体投影压暗盘面），未入库；pack 10 缩小并禁投影，入选，偏移 -5.36，90.6。
- oozing horror（2 次）：首次“Selected model is at capacity”，无结构化结果；重跑入选，130.1。
- ogric abomination（2 次）：首次底盘偏移 -10.64＋`subject_intrusion` 警告，未入库；pack 12 缩小、短槌、石臂内收，偏移 +1.21、警告消失，90.8。
- 其余十款各 1 次入选。

无 PENDING 请求、无豁免、未降低任何阈值（生产测试的亮度下限仍是 65）。

## 48px 评审

`art/monster-batch-ac/review/floor-readability-48.png`（十七行整张）、`floor-readability-48-x2.png`（前九款）与 `floor-readability-48-x2-b.png`（后八款）：十七款放在十张真实精修地板上（黄框为本区地板，dreadfell 用 korpul 石地板、conclave-vault 用最接近的哥特石地板）。掩膜亮度（128px，`review/luminance.json`）：abyssal horror 75.2、Filio Flightfond 78.1、vampire lord 84.6、ungolmor 85.6、Rotting Titan 90.6、umbral horror 90.7、ogric abomination 90.8、Void Spectre 91.8、orc high pyromancer 100.4、Arch Zephyr 103.3、Heavy Sentinel 110.1、degenerated ogric mass 111.4、ruin banshee 114.9、orc high cryomancer 129.9、oozing horror 130.1、Aletta Soultorn 135.3、Glacial Legion 175.8。48px 上最弱的是 abyssal horror（靛紫触手团，靠红眼与淡紫吸盘辨认），其次是 umbral horror（灰紫对灰石地板对比偏低）与 Arch Zephyr（灰蓝线条纤细，靠闪电辨认）；ruin banshee 在 48px 读作黄绿橙缠绕团，靠尖叫脸与骨爪辨认，均没有再返修。
