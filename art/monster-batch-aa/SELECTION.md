# 怪物棋子批次 AA 选型（2026-09-30，接在批次 Z 之后，不升版）

来源：`docs/expansion-plan-20260928/MONSTER-GAP-2-20260929.md` 「### 后续（未排批）」。计分口径与批次 R–Z（`art/monster-batch-z/SELECTION.md`）逐字相同；复算脚本是批次 Z 脚本的拷贝（`art/monster-batch-aa/score_candidates.py`，仅改了输出注释路径），按当前 `CheckerTokens.lua`（335 条，含批次 Z）过滤已收录 name，剔除 §7 批次 1–8 已排的身份和 §4 判 I／N／K 的身份，剩 42 条（含 Training Dummy）。

## 结果

Training Dummy（12.0，批次 T 起留原生）仍在脚本输出顶端，本批不考虑。其后的排名（本批取到 1.5 分档；1.5 分有 dreadmaster 与 entrenched horror 两个并列，只余一个名额，按行序 681 < 727 取 dreadmaster，entrenched horror 落选，是下一批第一个候选）：

| 排名 | 分值 | 身份 | 中文名（mod-tome.lua） | 说明 |
|---:|---:|---|---|---|
| 1 | 2.0 | ultimate faeros | 究极法罗 | charred-scar 2.0（行 840）；非唯一 tall → native_tall；renegade-pyromancers 随机首领保持原生 |
| 2 | 1.8 | orc berserker | 兽人狂战士 | vor-armoury 1.5＋rak-shor-pride 0.3（行 579）；elite berserker 是另一个叶子，保持原生 |
| 3 | 1.8 | dredge captain | 挖掘魔首领 | temporal-rift 1.8（行 697） |
| 4 | 1.8 | polar bear | 北极熊 | noxious-caldera 0.9＋old-forest 0.9（行 822）；显式 image=polar_bear.png |
| 5 | 1.8 | anaconda | 巨蟒 | noxious-caldera 1.1＋unremarkable-cave 0.7（行 999）；显式 image=yellow-green-snake.png |
| 6 | 1.7 | ultimate teluvorta | 究极泰鲁沃塔 | temporal-rift 1.7（行 720）；tall |
| 7 | 1.7 | necrotic abomination | 亡灵憎恶 | rak-shor-pride 1.7（行 874）；tall |
| 8 | 1.7 | bone horror | 骨灵恐魔 | rak-shor-pride 1.7（行 875）；tall |
| 9 | 1.7 | sanguine horror | 血红恐魔 | rak-shor-pride 1.7（行 876）；tall |
| 10 | 1.7 | barrow wight | 古墓尸妖 | dreadfell 1.3＋ardhungol 0.4（行 893）；tall，image= 加 nice_tile |
| 11 | 1.6 | ogre warmaster | 食人魔战争领主 | crypt-kryl-feijan 1.6（行 655）；tall（nice_tile{tall=1} 简写） |
| 12 | 1.5 | dreadmaster | 噩灵之王 | rak-shor-pride 0.6＋telmur 0.5＋demon-plane 0.4（行 682）；显式 image=dreadmaster.png；死灵法师的 Dread 天赋召唤同名同图仆从，戴同一棋子 |

中文名以 zh_hans 的 `/workspace/tome4-chinese-translation/mod-tome.lua` 为准（下文与 PROGRESS 只引用这些名称）。

其后梯队：entrenched horror 1.5（并列落选）、orc summoner 1.4、greater mummy 1.4、shadowblade 1.2、orc elite fighter／elite berserker 1.1 ……本批之后剩 30 条未映射（含 Training Dummy，即 29 个真实候选）。

排除项（与 R–Z 相同的规则）：Training Dummy；§4 判 I 的身份；§5.1 同名冲突（本批无一命中）；§5.2 KEEP（无）；目录已有：核对 `CheckerTokens.lua`，本批 12 个的 name 均不在其中。

## 选定 12 个（源码逐条重核，合同见 `evidence/monster-batch-aa-20260930/source-contracts.json`）

| # | 名称 | define_as | type/subtype | 图像来源 | 分值 |
|---|---|---|---|---|---:|
| 1 | ultimate faeros | — | elemental/fire | **tall**：`nice_tile` 64×128 → `native_tall=true` | 2.0 |
| 2 | orc berserker | — | humanoid/orc | 默认名图 | 1.8 |
| 3 | dredge captain | — | horror/temporal | 默认名图 | 1.8 |
| 4 | polar bear | — | animal/bear | 显式 image=npc/polar_bear.png | 1.8 |
| 5 | anaconda | — | animal/snake | 显式 image=npc/yellow-green-snake.png | 1.8 |
| 6 | ultimate teluvorta | — | elemental/temporal | **tall** → `native_tall=true` | 1.7 |
| 7 | necrotic abomination | — | undead/horror | **tall** → `native_tall=true` | 1.7 |
| 8 | bone horror | — | undead/horror | **tall** → `native_tall=true` | 1.7 |
| 9 | sanguine horror | — | undead/horror | **tall** → `native_tall=true` | 1.7 |
| 10 | barrow wight | — | undead/wight | **tall**：image= 加 `nice_tile` add_mos → `native_tall=true`（同 master vampire 形态） | 1.7 |
| 11 | ogre warmaster | — | giant/ogre | **tall**：`nice_tile{tall=1}` 简写 → `native_tall=true`（同其余食人魔） | 1.6 |
| 12 | dreadmaster | — | undead/ghost | 显式 image=npc/dreadmaster.png | 1.5 |

七个是非唯一 native-tall，五个是非唯一 64×64 单图；十二个都没有 define_as。**同体形／召唤**：死灵法师的 Dread 天赋召唤的仆从与 dreadmaster 同名同型同图，戴同一棋子；dreadmaster 自身的召唤物是 dread（已有棋子）；挖掘魔首领的护卫是 dredge（已有棋子）；亡灵憎恶／骨灵恐魔／血红恐魔的召唤是 ghoul／skeleton／undead-blood 叶子（各自的棋子或原生）。renegade-pyromancers 的随机首领 ultimate faeros 与 renegade-undead 的随机首领 bone horror／sanguine horror 走“非唯一 tall 保持原生”既有路径（测试有正反例）。orc elite berserker（define_as ORC_ELITE_BERSERKER）是另一叶子，保持原生。

## 分包

- Pack 1：ultimate faeros、ultimate teluvorta、dredge captain、dreadmaster
- Pack 2：orc berserker、ogre warmaster、barrow wight、polar bear
- Pack 3：anaconda、necrotic abomination、bone horror、sanguine horror
- Pack 4 orc berserker 重做（pack 2 圆盘半径 0.939 超 0.867，`subject_intrusion` +31.18）；pack 5 ogre warmaster 重做（pack 2 通过阻断门控但 `subject_intrusion` +38.07 超警告线，且底盘偏移 +7.38 贴近 +8；本批不放行警告）；pack 6 barrow wight 重做（pack 2 底盘偏移 -8.19 超 ±8）；pack 7 sanguine horror 重做（pack 3 掩膜亮度 58.6 低于 65）；pack 8 orc berserker（pack 4 无图返回）；pack 9 sanguine horror 第三次（pack 7 仍 60.8）；pack 10 barrow wight 第三次（pack 6 的 v1 过全部数值门控，但 48px 上是一团灰绿，改为大块亮面的简化版）

## 设计约束（生图前定的，不是事后补）

沿用批次 R–Z 的评审教训：主体大块面一律中亮到亮，沿轮廓一圈亮边光，禁止黑色主体；`DARKFIX` 段用于原图近黑或偏暗的主体（orc berserker、ultimate teluvorta、dreadmaster、barrow wight、necrotic abomination）。盘面措辞沿用“at reference lightness, a hair lighter, never darker”。tall 主体统一要求“画成一个紧凑的直立单体填满圆盘，不出高画布”。

同族区分（对照既有棋子，非仅换色）：

- ultimate faeros：无腿、白热金色核心、七簇火焰冠、盘绕一圈再卷起的火焰尾；对既有橙红有腿呈 X 形的 faeros、体型更大的橙色 greater faeros。
- orc berserker：绿皮兽人、抛光淡钢“massive”重甲、圆刺肩甲、长角盔、绯红腰布、双刃战斧举在盔侧、无盾；对既有持盾灰甲 orc fighter、深色刺甲斧垂 orc soldier、皮甲弯刀 orc warrior、深袍 orc assassin。
- dredge captain：细瘦驼背、大头、长手臂、举起的钢匕首，身体左半灰紫褶皱老化、右半粉嫩年轻；对既有粗壮无武器的粉色 dredge 与小型蹲伏 dredgling。
- polar bear：低身潜行、长颈前伸、头低垂、窄长口鼻、纯白冰蓝阴影和霜晶；对既有棕、黑、灰白驼背 cave bear、直立的 war／grizzly bear。
- anaconda：极粗的黄绿蛇，三圈粗盘叠成竖向绞缠螺旋，宽扁楔形蛇头，双排暗绿褐椭圆环斑，奶黄腹；对既有平铺褐蛇、戴兜帽橄榄绿眼镜王蛇、钢蓝黑曼巴、菱纹响尾蛇。
- ultimate teluvorta：钴蓝与青色沙漏形坍缩旋涡，中间白青收束点，三道断裂银金环和玻璃碎片；对既有紫色尖刺水晶球 teluvorta、深紫六角风暴云 greater teluvorta、金色星爆 ultimate telugoroth、透镜状靛蓝 void horror。
- necrotic abomination：不对称驼背拖行的橄榄绿腐肉巨怪，撕开露出白骨肋，背脊骨刺冠，胸口獠牙裂口，一条下垂缝合巨臂；对既有圆形粉褐团 necrotic mass、粉色触手 fleshy experiment、平铺骨堆 boney experiment、低矮红色穹丘 sanguine experiment。
- bone horror：象牙色巨大肋骨拱，六条细长指骨蜘蛛腿，顶部伸出骷髅手，肋内琥珀色心跳光；对既有平铺骨堆和直立人形骷髅。
- sanguine horror：直立前倾的浪柱状鲜血，内部发光珊瑚粉色心脏，两条滴落触臂；对既有低矮红色穹丘 sanguine experiment（亮度不足两次后改为半透明珊瑚粉果冻质感，红色只在细缝与滴尖）。
- barrow wight：瘦削高大的古墓亡灵，苍白骷髅脸、冰蓝双眼、金色环冠，薄荷铜绿与金铜肩甲胸甲，近白蓝色裹尸披风，双手间冰青色鬼火；对既有绿兜帽持圆盾 forest wight、半透明青色 grave wight 与骷髅。
- ogre warmaster：银白全身板甲加金边、高冠面甲盔配绯红羽饰、金色护颈／护胫／手甲、绯红腰带、两把长直剑贴身；对既有半裸粗壮的蓝／红皮食人魔和古铜色 elven elite warrior。
- dreadmaster：钟形破碎斗篷（苍白石板蓝＋淡紫蓝）、高尖兜帽、兜内发光红色尖叫脸、细长灰白利爪、淡蓝幽灵雾；对既有小型紫灰尖刺毛球 dread、青色女妖 banshee、透明青色 grave wight。

## ImageGen 记录

**19／28 次**（`gpt-6.1-sol`＋`--ephemeral`，逐次串行，只用 run_imagegen.py 默认）。十二款各 1 次，另七次为返工（每款至多 3 次）：

- orc berserker（3 次）：首图最大不透明半径 0.939（上限 0.867）且 `subject_intrusion` +31.18，未入库；pack 4 重做，codex 结束回合但没有调用 ImageGen（`provenance-rejected`，未入库）；pack 8 再做，手持短柄斧、缩小后入选（偏移 +6.56，掩膜亮度 85.1）。
- ogre warmaster（2 次）：首图通过阻断门控但 `subject_intrusion` +38.07（剑尖外伸、人偏中心），母版移入 `superseded/`；v2 居中、双剑收短，偏移 -0.55、上偏 +3.98。
- barrow wight（3 次）：首图底盘偏移 -8.19，未入库；v1（pack 6，偏移 +0.25）过全部数值门控，但 48px 读作灰绿一团（审图，掩膜亮度 101.8 并不说明问题），移入 `superseded/`；v2（pack 10）改成大块亮面：骨白脸、薄荷铜绿甲、金冠、近白披风，偏移 -1.06。
- sanguine horror（3 次）：v1 掩膜亮度 58.6、v2 60.8（均低于 65），均在 `superseded/`；v3 改成半透明珊瑚粉果冻质感，75.9，偏移 -1.49。纯红本身亮度上限低，这一款是本批最暗。

无 PENDING 请求、无豁免、未降低任何阈值（生产测试的亮度下限仍是 65；所有入选件不低于 75.9）。

## 48px 评审

`art/monster-batch-aa/review/floor-readability-48.png`、`floor-readability-48-x2.png`：十二款放在十张真实精修地板上（本区地板黄框）。掩膜亮度：sanguine horror 75.9、orc berserker 85.1、dredge captain 87.8、necrotic abomination 92.5、dreadmaster 96.6、ogre warmaster 97.3、anaconda 100.8、ultimate teluvorta 101.2、barrow wight 101.8、bone horror 106.7、ultimate faeros 155.7、polar bear 167.9。48px 上偏弱的两款：dredge captain（粉灰偏淡、身形细瘦，靠匕首和左右半身两色辨认）与 barrow wight（细节多、色偏冷，靠白脸和冰蓝手光辨认）；与已交付的 rogue sapper v2、forest wight 相当，没有再返修。
