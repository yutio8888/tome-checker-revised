# 怪物棋子批次 Y 选型（2026-09-30，接在批次 X 之后，不升版）

来源：`docs/expansion-plan-20260928/MONSTER-GAP-2-20260929.md` 「### 后续（未排批）」。计分口径与批次 R–X（`art/monster-batch-x/SELECTION.md`）逐字相同；复算脚本是批次 X 脚本的拷贝（`art/monster-batch-y/score_candidates.py`，仅多打印各行 §4 判定与行号），按当前 `CheckerTokens.lua`（311 条，含批次 X）过滤已收录 name，剔除 §7 批次 1–8 已排的身份和 §4 判 I／N／K 的身份，剩 66 条。

## 结果

Training Dummy（12.0，批次 T 留原生）仍在脚本输出顶端，本批不考虑。其后的排名：

| 排名 | 分值 | 身份 | 说明 |
|---:|---:|---|---|
| 1 | 3.4 | uruivellas | 批 X 三方并列落选（§4 行 830）；valley-moon-caverns 1.9＋demon-plane 1.5；非唯一 tall → native_tall |
| 2 | 3.4 | thaurhereg | 同上（行 831） |
| 3 | 3.3 | orc corruptor | rak-shor-pride 3.3 |
| 4 | 3.2 | temporal stalker | temporal-rift 2.9＋ardhungol 0.3；tall → native_tall |
| 5 | 3.1 | broken golem | golem-graveyard 3.1（行 925） |
| 6 | 3.1 | golem | golem-graveyard 3.1（行 926）；玩家炼金傀儡同名同 type，但图与纸娃娃不同，保持原生 |
| 7 | 2.9 | blade horror | lake-nur 1.3＋…共 5 区；define_as BLADEHORROR；tall |
| 8 | 2.8 | animated mummy wrappings | ancient-elven-ruins 区内 2.8；显式 image=object/mummy_wrappings.png |
| 9 | 2.8 | grizzly bear | old-forest 1.4＋noxious-caldera 1.4；显式 image＋nice_tile tall |
| 10 | 2.7 | weaver patriarch | ardhungol 2.7（行 626） |
| 11 | 2.7 | luminous horror | lake-nur 1.1＋…共 5 区（行 669） |
| 12 | 2.7 | necrotic mass | rak-shor-pride 2.7（行 872）；tall |

第 10–12 名是 weaver patriarch、luminous horror、necrotic mass、black mamba 四方并列（2.7，小数点后六位相同），只剩三个名额，按 §4 表行序（626、669、872、997）取前三；black mamba（997）落选留原生，是下一批候选。其后梯队：black mamba 2.7、bandit lord 2.6、orb weaver 2.6、elven elite warrior 2.5、ultimate telugoroth 2.5、greater teluvorta 2.5。同分 2.8 的 animated mummy wrappings（811）与 grizzly bear（820）、同分 3.1 的 broken golem 与 golem 也按行序排列。

排除项（与 R–X 相同的规则）：Training Dummy；§4 判 I 的身份；§5.1 同名冲突（本批无一命中）；§5.2 KEEP（无）；目录已有：核对 `CheckerTokens.lua`，本批 12 个的 name 均不在其中。

## 选定 12 个（源码逐条重核，合同见 `evidence/monster-batch-y-20260930/source-contracts.json`）

| # | 名称 | 中文名（mod-tome.lua） | define_as | type/subtype | 图像来源 | 分值 |
|---|---|---|---|---|---|---:|
| 1 | uruivellas | 乌尔维拉斯 | — | demon/major | **tall**：`nice_tile` 64×128 → `native_tall=true` | 3.4 |
| 2 | thaurhereg | 修尔希瑞格 | — | demon/major | **tall** → `native_tall=true` | 3.4 |
| 3 | orc corruptor | 兽人堕落者 | — | humanoid/orc | 默认名图 | 3.3 |
| 4 | temporal stalker | 时空猎手 | — | horror/temporal | **tall** → `native_tall=true` | 3.2 |
| 5 | broken golem | 破损的傀儡 | — | construct/golem | 默认名图 | 3.1 |
| 6 | golem | 傀儡 | — | construct/golem | 默认名图 | 3.1 |
| 7 | blade horror | 刀锋恐魔 | BLADEHORROR | horror/eldritch | **tall** → `native_tall=true` | 2.9 |
| 8 | animated mummy wrappings | 蠕动的裹尸布 | — | undead/mummy | 显式 image=object/mummy_wrappings.png | 2.8 |
| 9 | grizzly bear | 灰熊 | — | animal/bear | 显式 image＋`nice_tile` tall → `native_tall=true`（关 nicer_tiles 时走单图路径） | 2.8 |
| 10 | weaver patriarch | 雄性编织者 | — | spiderkin/spider | 默认名图 | 2.7 |
| 11 | luminous horror | 金色恐魔 | — | horror/eldritch | 默认名图 | 2.7 |
| 12 | necrotic mass | 亡灵集合 | — | undead/horror | **tall** → `native_tall=true` | 2.7 |

（中文名逐条取自 `/workspace/tome4-chinese-translation/mod-tome.lua`；棋子代码与 locale 不引入这些名称。）

六个是非唯一 native-tall（uruivellas、thaurhereg、temporal stalker、blade horror、grizzly bear、necrotic mass），六个是非唯一 64×64 单图；只有 blade horror 绑定 define_as。玩家炼金傀儡（`golemancy.lua:30`）与 golem 叶子同 name／type／subtype，但 `image=npc/alchemist_golem.png` 且带 `moddable_tile`，匹配器两处都拒绝，保持原生（测试有正反例）。

## 分包

- Pack 1 tall 大魔：uruivellas、thaurhereg
- Pack 2 兽人与傀儡：orc corruptor、broken golem、golem
- Pack 3 恐魔：temporal stalker、blade horror、luminous horror、necrotic mass
- Pack 4 裹尸布、熊、蜘蛛：animated mummy wrappings、grizzly bear、weaver patriarch
- Pack 5 uruivellas 重试（pack 1 无图返回）；Pack 6 uruivellas 再试（pack 5 底盘偏移 -8.45）；Pack 7 luminous horror 重试（无图）；Pack 8 grizzly bear 重试（无图）；Pack 9 weaver patriarch 重试（无图）

## 设计约束（生图前定的，不是事后补）

沿用批次 R–X 的评审教训，`DARKFIX` 段用于原图偏暗的五个主体（uruivellas、orc corruptor、broken golem、blade horror、grizzly bear）：一律改为中亮度灰／赭／蜜金等主色，沿轮廓一圈亮边光，用鲜亮强调色保住身份；提示词明确禁止黑色／深棕主体。盘面措辞沿用“at reference lightness, a hair lighter, never darker”。tall 主体统一要求“画成一个紧凑的直立单体填满圆盘，不出高画布”。

- uruivellas：灰烬灰与浅陶土色的公牛头大魔，象牙白大角，熔岩色缝隙，紧贴身体的明黄橙火焰光环；区别于米黄的 minotaur、橙红带刺的 dolleg。
- thaurhereg：瘦长驼背的淡玫瑰粉大魔，象牙角冠，鲜红血脉纹路流淌；区别于橘红实心的 dolleg（实测生成结果偏红，见 PROGRESS）。
- orc corruptor：橄榄绿兽人，苔绿与赭黄的腐败长袍，骨白肩刺，短杖顶端病态黄绿光。
- temporal stalker：抛光铬银的细长恐魔，镰刀月牙形头，长刃爪指，青色碎光。
- broken golem：淡石灰灰的倒塌傀儡，裂缝、缺失的前臂、锈橙接缝、无发光；golem：蜜赭黏土的完整傀儡，青色眼睛与符文线，巨锤。
- blade horror：灰蓝白色兜帽飘浮体，紫白眼，环绕的钢剑螺旋环与白风；区别于红眼石板紫的 dread。
- animated mummy wrappings：空的象牙亚麻 S 形绷带卷，中空里紫色奥术微光，无身体。
- grizzly bear：蜜金与黄褐、银白霜尖的灰熊直立起身，肩峰，无项圈；区别于棕、黑、灰、锈橙戴项圈的战熊。
- weaver patriarch：钴蓝宝石色的大蜘蛛，胸部白色人字纹，关节白青发光球，金色时间残影；区别于小型蓝白旋涡编织者与奶油金编织者女王。
- luminous horror：修长的金黄色光体，白热核心；necrotic mass：淤紫与灰粉腐肉堆，黄绿脓疱与苍白骨节。

## ImageGen 记录

17／28 次（`gpt-6.1-sol`＋`--ephemeral`，逐次串行，只用 run_imagegen.py 默认）。十二款各 1 次入选（uruivellas 3 次），另五次为失败重试：uruivellas pack 1、luminous horror、grizzly bear、weaver patriarch 首次调用 codex 结束回合但没有调用 ImageGen（`image_path` 为空，`provenance-rejected`，未入库），各再 1 次即入选；uruivellas pack 5 的一张产物底盘偏移 -8.45（超 ±8，火焰与身体在盘面投下暗影，未入库），pack 6 改为缩小图形、去掉投影后入选。无 PENDING 请求、无豁免、未降低任何阈值。animated mummy wrappings 的底盘偏移 -7.99 恰在容差内。
