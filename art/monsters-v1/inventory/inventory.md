# 怪物棋子源素材与分批制作盘点

2026-09-26；本地 ToME 1.7.6。依据已有 `documentation/board-visual-audit-2026-09-26/images.csv`，并读取原版 NPC 定义。本轮没有执行 Lua 实体生成、没有追踪实际刷怪、没有重新解码全部图片，也没有审阅全部 DLC 实体脚本。

## 数量口径

| NPC 主图库来源 | 文件数 | 精确 RGBA 去重 |
| --- | ---: | ---: |
| 基础游戏 | 645 | 642 |
| Ashes of Urh'Rok | 7 | 7 |
| Forbidden Cults | 66 | 66 |
| Embers of Rage | 117 | 117 |
| 合计 | **835** | **832** |

只计 `shockbolt/npc`，不累计旧 Mushroom 图库、启动肖像、demo 副本、技能图标及换装部件。去重沿用既有清单的画布尺寸和完整解码 RGBA 哈希，**不是物种数或独立设计数**。835 张中有 510 张 64×64、301 张 64×128，其余 24 张为其他尺寸。高画布常是上方延展的绘制空间，不等于占用两格。

三对精确重复分别是 `dragon_ice_rantha_the_worm`／`dragon_temporal_rantha_the_abomination`、`dread`／`dread_02_64`、`naga_psyren2`／`naga_psyren2_2`。相同像素仍可能对应不同实体或规则，不能据此删路径或合并身份。

## 首批五个精确映射

| 实体 | type / subtype | 原图（相对 NPC 图库） | rank | nice_tile |
| --- | --- | --- | ---: | --- |
| forest troll | giant / troll | `npc/troll_f.png` | 2 | 无 |
| wolf | animal / canine | `npc/canine_w.png` | 1 | 无 |
| brown bear | animal / bear | `npc/brown_bear.png` | 2 | 无 |
| large brown snake | animal / snake | `npc/umber-snake.png` | 2 | 无 |
| giant venus flytrap | immovable / plants | `npc/immovable_plants_giant_venus_flytrap.png` | 1 | 无 |

五张原图全部 64×64。前四个文件名直接写在定义中；捕蝇草通过 `class/NPC.lua:33` 的 `type_subtype_name` 规则得到默认图名，图像确实存在。rank 来自各自基础定义，不能把五种都假设为同一阶级。捕蝇草继承 `never_move=1`，属于可攻击生物；不能因为不移动就画成地形装饰。

接入时以**明确的原图／实体身份白名单**查找，并优先排除未制作的独特者；运行时还需处理变身、幻象与动态 `replace_display`。`subtype` 只辅助核对，不作为整族替换条件。现有 `Game.lua` 中 `troll/canine/bear/snake/plants` 一律替换的原型做法，会抹掉下面的亚种与独特者。

## 巨魔沼泽两种布局加载范围

依据 `data/zones/trollmire/npcs.lua:21`：

- **默认布局直接加载 8 份族群脚本**：rodent、vermin、canine、troll、snake、plant、swarm、bear。
- **泛滥布局直接加载 7 份族群脚本**：vermin、troll、snake、plant、swarm、bear、aquatic_critter；水生脚本中名称含 `squid` 的两个定义被去掉 rarity，因此不加入这次直接随机生成池。
- **两个布局都再加载 `all.lua`**。它按 `loadIfNot` 补入其他候选；所以泛滥布局中 canine／rodent 只是缺少直接高权重加载，不能断言完全不会出现。`rarity(4,35)` 是 `ceil(rarity*35+4)`，不是 35 级门槛（`engine/Entity.lua:1223`）。

九份相关脚本有 **52 个具名定义**，本表再附 4 个区域独特者，共 56 行。这包含高等级变体，**不是低层必刷的 56 种怪**。关卡等级、稀有度、地形、宝库、事件、护送与 DLC 注入会继续影响实际生成；`all.lua` 和宝库的完整闭包尚未展开。

## 可执行生产批次

| 批次 | 可靠的源定义分组 | 制作单位与差异 |
| --- | --- | --- |
| P1：当前样板 | 上表 5 个精确实体 | 五个独立轮廓母版，先验证二足／四足／盘曲／放射形；同一 PNG 不烘焙阵营、rank 或状态。 |
| P2：低层亚种 | 巨魔：stone/cave；犬科：great/dire/white wolf、warg、fox；熊：black/cave/war；蛇：white/copperhead/rattlesnake/king cobra；植物：poison ivy | 可复用对应母版的材质，但不得只给同一剪影换色。狐保留大尾与尖脸；战熊保留獠牙；洞穴巨魔有长矛；眼镜蛇有颈罩；响尾蛇有尾端结构；毒藤应是可攻击的缠绕体。 |
| P2：补充小生物 | rodent 8 定义、vermin 低层两种虫团、swarm 低层三种蜂／蠓群 | 鼠与兔要分轮廓，水晶鼠有晶簇；虫团／蜂群先做可读的群体构图母版。定义数量不等于必须独立从零画这么多母版。 |
| P2：独特巨魔 | Forest Troll Hedge-Wizard、Prox、Shax、Bill | **各自专属图**。法师的佝偻／施法身份、Prox 的体格、Shax 的水生特征、Bill 的树干武器不能被普通巨魔覆盖。 |
| P2：泛滥补充 | giant eel、electric eel、dragon turtle | 至少“鳗形”和“龟形”两个轮廓母版；电鳗不能仅靠微小颜色区别；没有默认巨型鳗与棕蛇互换依据。 |
| P3：高阶同族与跨区 | mountain/thunderer/patchwork troll、Rungof、grizzly/polar bear、black mamba/anaconda、treant/honey tree、carrion worm mass、hummerhorn、ancient dragon turtle | 按实际区域分布安排；树人和蜜树需要新结构，不属于捕蝇草换色。与 P2 共用材质、光线和底盘规范。 |
| 后续：其他区域与 DLC | 仍待实体映射审阅；835 张源文件索引已附 | 先核对具体定义、叠层和运行时图像，再按骷髅／幽灵、蛛虫、构装体、龙类、类人角色分制作队列。此处只是计划方向，未声称已完成全部语义归族。 |

Prox／Shax／Bill 都是 `rank=4`，显示图为 64×128，通过 `nice_tile` 指定 `display_h=2, display_y=-1`。**Shax 的普通 image 字段实际写着 Prox；漂亮贴图模式中 `add_mos` 才替换为 Shax 图。** 只扫描顶层 image 会映射错。Hedge-Wizard 使用 `nice_tile{tall=1}`，同样转为高画布。重画到单格圆盘必须重新安排其独特轮廓，不能直接压扁原图。

Aluin 是本区 35 级后备守护者，独立图名 `npc/humanoid_human_aluin_the_fallen.png`（64×64）存在；本轮延后，不与三位早期巨魔 Boss 合并，也不因此开启换装制作。

## 文件与限制

- `source-summary.csv`：来源与精确去重数量。
- `npc-sources.csv`：835 个源路径、尺寸、原清单哈希；DLC 路径采用 `包路径:包内路径`。
- `trollmire-entities.csv`：56 个具名定义的原 image、漂亮贴图图层、type/subtype、rank、等级范围、生产批次和源码行。
- `build_inventory.py`：可复跑生成上述 CSV。它只对九份已检查脚本与本区独特者做有限词法提取；不执行 Lua，也不是通用语义解析器。字段来源与运行时结果需要区分。

通过小尺寸静态验收后，再逐族检查普通／稀有／独特、友好／敌对／中立、召唤和变身。未覆盖图像保留原图，宁可有风格过渡，也不让新棋子错误表达怪物身份。
