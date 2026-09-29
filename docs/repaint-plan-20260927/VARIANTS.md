# 低级主线地城双变体补充方案

2026-09-27。根据用户补充，覆盖单位改为**地城 × 布局**。六个起步区域和四个二阶区域各有DEFAULT及一个替代布局，共20行验收记录。本文修订主方案中“默认布局先完成，变体以后再补”的安排：一个区域必须把两版的普通怪、固定首领、附属怪群和地形都纳入计划，才能称为该区域的完整阶段。

这是源码审阅及制作计划，没有生成新图片、启动游戏或验证20种布局。`DEFAULT`／替代键沿用本地1.7.6源码；例如旧森林的键确实拼作`CRYSTALINE`。正常游玩的变体选择还有访问记录、成就和一阶首领击杀条件；测试时在独立离线夹具中明确选择布局并记录，不靠随机重开猜测。

## 1. 十组布局与怪物差异

下表中的“替换”仅指本区域**直接加载的普通怪物表**；特殊房间、护卫、召唤、`all.lua`高等级补充仍可能引入别的家族，不能把它当作全图禁止名单。

| 地城 | DEFAULT | 替代布局及必须纳入的内容 | 首领处理 |
| --- | --- | --- | --- |
| Trollmire | 鼠、犬、巨魔、蛇、植物、虫群、熊等；森林与深水池 | **FLOODED**：直接表移除鼠／犬、加入水生；giant eel、electric eel、dragon turtle；沼泽水及沼泽树。水生回调排除squid，不为本分支额外画两种鱿鱼 | Prox → **Shax the Slimy**；Bill宝藏支线两版复用现有图。Shax需独立水生巨魔造型，不能套Prox |
| Kor’Pul | 骷髅＋共享鼠、虫、霉菌、蛇 | **HIDEOUT**：骷髅直接表改为盗贼；**cutpurse、rogue、thief、bandit前移**，bandit lord／assassin／shadowblade／rogue sapper记录为较高阶复用候选；末层地图不同 | **The Shade／The Possessed**均单独设计；Possessed的thief护卫也验收。Shade的原生unique_glow先约定保留方式 |
| Norgos | 熊、犬、蛇、虫、植物 | **INVADED**：以**shivgoroth、greater shivgoroth、ultimate shivgoroth**替换直接植物表。三种原生最低等级10／12／15，经本区回调减9成为**1／3／6**；全纳入，不能只做初级冰元素 | **Norgos, the Guardian／Norgos, the Frozen**分别画；冻熊不能仅靠阵营蓝环或护盾白环表达 |
| Heart of the Gloom | 同一组鼠、熊、犬、植物，附加gloomy／deformed／sick前缀与阴郁系随机技能 | **PURIFIED**：同家族附加dreaming／slumbering／dozing前缀与梦境系技能；两条来源映射与技能显示都要测试，不按字符串前缀生成六套重复母版 | **The Withering Thing／The Dreaming One**是不同身份；另计Call Shadows的**shadow**技能召唤物 |
| Scintillating Caves | 晶体与共同小动物；Cavern洞穴布局 | **TWISTED**：共同普通表与首领相同，但Roomer布局加入指定密室列表，可有骷髅、尸鬼、盗贼、bloated horror及snake-pit随机池。补**crimson crystal**，多彩／闪烁晶体及wisp也列入条件／召唤验收 | **Spellblaze Crystal**两版共用一款，不因地图变体重复出图；后期Spellblaze Simulacrum不当作本次替代首领 |
| Rhaloren Camp | 室内营地；精灵战士／法师和共用小怪 | **OVERGROUND**：主要普通表相同，增加建筑／草木交界；房间列表用collapsed-tower代替rat-nest，须覆盖构装体、炮塔等条件敌人 | **Rhaloren Inquisitor**共用一款；房间随机守卫另表管理 |
| Old Forest | 熊、犬、蛇、虫群、植物、蚂蚁 | **CRYSTALINE**：直接犬蛇表改为晶体；复用晶洞的晶体家族，尤其**multi-hued crystal、shimmering crystal**及其**wisp**；不是再画一套“森林晶体” | **Wrathroot／Shardskin**分开设计；Shardskin保留树被晶体包覆的身份，不套普通晶柱 |
| Maze | 盗贼、牛头人、软泥以及鼠虫犬蛇蚁 | **COLLAPSED**：加入**drem、dremling、drem master、brecklorn、grannor’vor、grannor’vin、dredgling、dredge**；dredge captain／temporal stalker／void horror保留为需核对实际等级条件的候选；裂隙向下通路单独设计 | **Minotaur of the Labyrinth／Horned Horror**分别画；恐魔不能用牛头人改色冒充；drem master护卫与时空队长护卫计入 |
| Daikara | 共享雪巨人／xorn；犬与冰龙 | **VOLCANO**：犬／冰龙直接表换为**fire drake hatchling、fire drake、fire wyrm、faeros、greater faeros、ultimate faeros**；共用umber hulk／xorn／xaren也补入；火山末层和岩浆单列 | **Rantha the Worm／Varsha the Writhing**成对设计。faeros声明最低20／25／35，不能仅因导入就称其早期常见；先解析区域层数、等级偏移、生成过滤 |
| Sandworm Lair | 普通引路掘洞虫及沙虫／软泥／胶怪 | **BIGWORM**：首层巨大掘洞虫引路，后续层仍可能用普通掘洞生成；两种引路者和临时通道／坍塌都纳入。普通随机表相同 | **Sandworm Queen**共用，真实召唤出的沙虫也验收；巨大引路虫2×2是显示尺寸，不能直接认定碰撞占四格 |

每一行的源码导入位置、首领定义、变体选择键及房间列表见[20行变体矩阵](zone-variants.csv)。新增／复用身份逐条见[怪物补充清单](variant-monster-backlog.csv)；源码hash见[审计记录](variant-source-audit.json)。这些是源定义清单，最终生成概率和完整区域候选须经过原生解析。

## 2. 把房间、护卫与召唤物放进覆盖分母

新增[房间怪群清单](variant-room-backlog.csv)，记录两种布局显式引用的21个不同lesser-vault模板、来源路径、适用布局、候选怪群和前置条件。房间是一项条件性场景工作，不能把21个房间等同21款怪物，也不能将载入整个NPC脚本等同该房间一定产生所有物种。

优先检查这些容易漏掉的情况：

- **amon-sul-crypt**有四组分支：近战骷髅、法师骷髅、骷髅弓手、ghoul／ghast；含armoured skeleton warrior、skeleton magus、skeleton master archer。它们纳入共享亡灵补全包，不能因Kor’Pul主表改成盗贼就跳过。
- **skeleton-mage-cabal**的候选还包括skeleton warrior、skeleton archer、thief、bloated horror，不能按房间名只做法师。
- **snake-pit**也可能选snow cat、giant spider、ritch flamespitter及虫、蚁、鼠、霉菌、沙虫。需要按实际抽到的完整`mobs`表建立条件性身份任务。
- **collapsed-tower**包含broken golem和动态构造的elemental crystal炮塔。炮塔是Actor，不能当作普通晶体地形；嵌套盗贼区域单记覆盖。
- **honey_glade**中的honey tree会召唤蜂群，且有grizzly bear与等级偏移；**forest-ruined-building2**还会造出gloomy／wet等前缀身份和water imp。区域改名前缀方案不自动解决房间的`on_make`修改，必须记录具体可信来源。
- **snow-giant-camp**含snow giant chieftain及随机unique首领；**circle**对当前表添加17／20等级偏移。不能用区域标称1–7或7–16级一刀切排除这些候选。
- 护卫与召唤使用已有身份时复用美术，但必须验证生成后的身份、等级、阵营及复制缓存；新增身份才增加母版量。典型为Possessed的thief、drem master的drem／dremling、晶体的wisp、Withering Thing的shadow、女王的沙虫。

当前附表没有递归展开所有`all.lua`、全部vault、随机世界事件及嵌套区域，也没有因此声称全覆盖。对应房间任务已纳入计划；在进入该区域制作前解析明确的房间选择池，先补身份清单再出图。未覆盖身份保持原生，截图和统计必须记录回退。

后期backup guardians（如Aluin、Kor’s Fury、Spellblaze Simulacrum、Snaproot、Nimisil、Corrupted Sand Wyrm、Massok）属于回访阶段，**不是低级地城的第二布局首领**，另外排期。

## 3. 制作顺序修订

原M1–M5的40款保留为美术家族分组，编号不再代表“全部画完这组才碰另一组”的顺序。每次仍4款评图、最多8款合批，阶段完成以两种布局验收为准。

| 阶段 | 成对交付目标 | 优先调整 |
| --- | --- | --- |
| P1 Kor’Pul | DEFAULT＋HIDEOUT，G1石质遗迹 | 保留首组3骷髅＋灰霉菌和6地形的技术样板；紧接着做cutpurse／rogue／thief／bandit，再分小批补两版首领、其余M1与亡灵房间候选；盗贼不等到迷宫才画 |
| P2 Trollmire | DEFAULT＋FLOODED，G0 | 复用现有动物，补electric eel与Shax，接通泛滥地形；共同森林密室按条件表补齐 |
| P3 Norgos | DEFAULT＋INVADED，G3的最小雪林子集 | 三档shivgoroth和两版Norgos一起排；普通高图接入前置从M4／M5提前到本阶段；雪地母版也提前 |
| P4 Heart of the Gloom | DEFAULT＋PURIFIED，G2阴郁／梦境子集 | 地区和房间可信改名来源、两版技能、两种首领及shadow；可复用本体不重复画六种前缀 |
| P5 Scintillating Caves | DEFAULT＋TWISTED，G2 | 普通晶体五种、共用首领、扭曲房间附属怪群；高阶晶体与wisp的运行合同在P7前完成 |
| P6 Rhaloren Camp | DEFAULT＋OVERGROUND，G1＋G0 | 精灵与Inquisitor；室内鼠巢／地表坍塌塔差异分别验证 |
| P7 Old Forest | DEFAULT＋CRYSTALINE，G0＋G2 | 原M2剩余森林候选、两版首领；复用P5晶体，同时验证quad_hue、召唤、暗草／春叶场景 |
| P8 Maze | DEFAULT＋COLLAPSED，G1 | 牛头人／软泥和腐化／时空恐魔分别成小批；两版首领、裂隙跳层、护卫、潜行一起纳入 |
| P9 Daikara | DEFAULT＋VOLCANO，G3＋火山补充 | 冰火龙成对，雪巨人／xorn共用；火元素按实际生成条件分批，火山末层单独验收 |
| P10 Sandworm Lair | DEFAULT＋BIGWORM，G4 | 两种引路者、女王和召唤沙虫；正常路径、巨大虫首层、后续层和临时通道变化均有实机证据 |

“首组4怪＋6地形”是技术样板，**不再把它称作Kor’Pul阶段完成**。同理，单张默认森林图不能完成Trollmire阶段。

## 4. 工作量修订与地形变体

怪物附表共有71个核对身份：4个已有、11个已列入原40款、56个此前未列。后者中，2个鱿鱼被本地水生导入过滤、2个Harkor’Zun事件身份单列后期，剩余**52个补充候选**：41个成对场景目标、2个召唤物（wisp／shadow）、9个需要先确认生成条件的高阶候选。它们含16个此前未做的固定主线首领。**52不是本轮立即出图数；40＋52也不是20种布局全部怪物的封顶总量。** 条件房间中未进入身份附表的怪物，在该阶段原生解析后另行去重补入，不能默认为已计入或已完成。

已有素材在两版使用只算一次母版；地区前缀复用算身份映射工作；不同首领算不同母版；同科高阶必须有剪影差异。这样既不把变体漏算，也不把两个布局简单乘二估算美术量。

地形不另造互不兼容的20套，而是在G0–G4公共套件上补以下合同：

| 变体需求 | 归入套件 | 增量设计 |
| --- | --- | --- |
| 泛滥森林 | G0 | 既有深水／沼泽水、透明树木纳入；BOGTREE、BOGWATER_MISC及水岸邻接、地面装饰不挡路 |
| 入侵雪林 | G3前移子集 | 冰元素／冻熊在雪地上仍有轮廓；两档原生雪粒子不能改变状态环语义 |
| 阴郁／净化洞穴 | G2 | 地板／墙面共同几何，按两套区域材质调色；fullgloom／fulldream叠加验收，不能只换怪物名字 |
| 扭曲晶洞与地表营地 | G2／G1＋G0 | 相同规则的格材质复用，补房间门、封门、建筑外墙、室内外连接和狭口 |
| 晶化旧森林 | G0＋G2 | 依原生春叶、草地和光照差异设计；圆盘晶体演员与无底盘地形明显分开，不凭“晶化”新增阻挡规则 |
| 坍塌迷宫 | G1 | **裂隙交互格1项**增量母版；与碎石装饰、楼梯不同；保留Jump／Stay确认和不可正常行走的原生交互 |
| 火山Daikara | G3火山子集 | 先预留**火山岩地／岩浆面2项**增量母版；读取本区实际Grid，本区lava加载已清除on_stand，不能按别区岩浆自动画致命伤害标识 |
| 巨虫沙洞 | G4 | 稳定沙地／临时通道／坍塌沿用同套规则，补首层路径、巨大虫、出口及后续普通虫恢复 |

因此旧G0＋G1共18张只是公共起始套件预算，不能再解释为变体覆盖总预算。裂隙及火山先新增3项明确设计，其余色板复用、房间特殊格和动态状态在原生Grid清单完成后核定，不把换色／16邻接导出分别算成新母版。

## 5. 验收记录改法

1. 每条记录必须包含`zone、layout、层号、seed、角色/区域等级、原生解析身份、来源路径、最终image/叠层、棋子命中或回退原因`；截图文件名带布局键。不能把两版混成一个覆盖百分比。
2. 每版分别列普通自然生成、固定首领、条件房间、护卫／召唤四组。房间未触发记“未验证”，不记“通过”；共享素材去重的是制作量，不是测试行。
3. 原生解析后至少保存两版各自的一个自然生成样本及可重复的规则压力场景；固定种子只保证本布局复现，不假设两版同seed会产生相同坐标。原版／棋盘对照在同一布局同一状态内进行。
4. 每版验收正常移动与攻击、首领与附属怪物、状态层和48／64／96px代表图；地形额外覆盖开关门、挖掘、视线／感知、迷雾记忆、特殊出口及区域特有动态变化。
5. 记录“已有、待制作、待接入、已验证、回退”五类状态。完整区域阶段必须显式交代两版未覆盖项，不能拿原40款或附表71条当作已验证分母。

复跑本次只读审计：`PYTHONDONTWRITEBYTECODE=1 python3 tools/audit_repaint_variants.py`。它检查两版选择键、明确的加载行及身份声明，输出矩阵／补充清单／房间清单和hash；不会执行Lua，也不能代替真实生成测试。
