# 怪物棋子批次 AB 选型（2026-09-30，接在批次 AA 之后，不升版）

来源：`docs/expansion-plan-20260928/MONSTER-GAP-2-20260929.md` 「### 后续（未排批）」。计分口径与批次 R–AA（`art/monster-batch-aa/SELECTION.md`）逐字相同；复算脚本是批次 AA 脚本的拷贝（`art/monster-batch-ab/score_candidates.py`，仅改了输出注释路径），按当前 `CheckerTokens.lua`（347 条，含批次 AA）过滤已收录 name，剔除 §7 批次 1–8 已排的身份和 §4 判 I／N／K 的身份，剩 30 条（含 Training Dummy）。

## 结果

Training Dummy（12.0，批次 T 起留原生）仍在脚本输出顶端，本批不考虑。其后按脚本顺序取 12 个：上一批并列落选的 entrenched horror（1.5）居首，随后 1.4、1.4、1.2、1.1×2、1.1×2、0.8，最后 0.7 档三个（swarm hive、Forest Troll Hedge-Wizard、ultimate shivgoroth）恰好填满最后三个名额，无需破并列。

| 排名 | 分值 | 身份 | 中文名（mod-tome.lua） | 说明 |
|---:|---:|---|---|---|
| 1 | 1.5 | entrenched horror | 巨石恐魔 | lake-nur 1.5（行 728，批次 AA 并列落选）；tall，nice_tile 显式 → native_tall |
| 2 | 1.4 | orc summoner | 兽人召唤师 | ardhungol 0.4＋unremarkable-cave 0.4＋rak-shor-pride 0.3＋另 1 区（行 578） |
| 3 | 1.4 | greater mummy | 巨型木乃伊 | ancient-elven-ruins 1.4（行 813）；绑定 define_as GREATER_MUMMY；显式 image= |
| 4 | 1.2 | shadowblade | 暗影之刃 | thieves-tunnels 0.7＋maze 0.5（行 606）；绑定 define_as THIEF_ASSASSIN（与 assassin 叶子同值）；竞技场另有无 define_as 的同名叶子，保持原生 |
| 5 | 1.1 | orc elite fighter | 精英兽人斗士 | vor-armoury 1.1（行 580）；绑定 define_as ORC_ELITE_FIGHTER |
| 6 | 1.1 | orc elite berserker | 精英兽人狂战士 | vor-armoury 1.1（行 581）；绑定 define_as ORC_ELITE_BERSERKER |
| 7 | 1.1 | boiling horror | 沸腾恐魔 | lake-nur 1.1（行 729）；tall，nice_tile 显式 → native_tall |
| 8 | 1.1 | venom wyrm | 猛毒巨龙 | noxious-caldera 1.1（行 944）；tall，`nice_tile{tall=1}` 简写 → native_tall |
| 9 | 0.8 | alchemist golem | 炼金傀儡 | golem-graveyard 0.8（行 928）；玩家自己的炼金傀儡名为 golem，另图另带纸娃娃，不受影响 |
| 10 | 0.7 | swarm hive | 虫群巢穴 | lake-nur 0.7（行 730）；tall，nice_tile 显式 → native_tall；召唤物 swarming horror 走批次 Z 的棋子 |
| 11 | 0.7 | Forest Troll Hedge-Wizard | 森林巨魔野法师 | reknor 0.7（行 976）；**唯一**，无 define_as，`nice_tile{tall=1}`，走 unique 高图路径（`unique=true`，无 native_tall，同 Walrog／Kyless） |
| 12 | 0.7 | ultimate shivgoroth | 究极西弗格罗斯 | norgos-lair 0.7（行 1072）；tall，nice_tile 显式 → native_tall |

中文名以 zh_hans 的 `/workspace/tome4-chinese-translation/mod-tome.lua` 为准（下文与 PROGRESS 只引用这些名称；游戏自带 locale 的“育种恐魔”“影武者”“海哲·维萨德”等与之不同，不采用）。

其后梯队：Aletta Soultorn、ruin banshee、Filio Flightfond 0.6（前后均为唯一或并列）、orc high pyromancer／cryomancer 0.5 ……本批之后剩 18 条未映射（含 Training Dummy，即 17 个真实候选）。

排除项（与 R–AA 相同的规则）：Training Dummy；§4 判 I 的身份；§5.1 同名冲突（本批：竞技场的 shadowblade 由 define_as 绑定排除）；§5.2 KEEP（无）；目录已有：核对 `CheckerTokens.lua`，本批 12 个的 name 均不在其中。

## 选定 12 个（源码逐条重核，合同见 `evidence/monster-batch-ab-20260930/source-contracts.json`）

| # | 名称 | define_as | type/subtype | 图像来源 | 分值 |
|---|---|---|---|---|---:|
| 1 | entrenched horror | — | horror/aquatic | **tall**：默认名图＋`nice_tile` 显式 64×128 → `native_tall=true` | 1.5 |
| 2 | orc summoner | — | humanoid/orc | 默认名图 | 1.4 |
| 3 | greater mummy | GREATER_MUMMY | undead/mummy | 显式 image=npc/undead_mummy_greater_mummy.png | 1.4 |
| 4 | shadowblade | THIEF_ASSASSIN | humanoid/human | 默认名图 | 1.2 |
| 5 | orc elite fighter | ORC_ELITE_FIGHTER | humanoid/orc | 默认名图 | 1.1 |
| 6 | orc elite berserker | ORC_ELITE_BERSERKER | humanoid/orc | 默认名图 | 1.1 |
| 7 | boiling horror | — | horror/aquatic | **tall** 显式 nice_tile → `native_tall=true` | 1.1 |
| 8 | venom wyrm | — | dragon/venom | **tall** `nice_tile{tall=1}` → `native_tall=true` | 1.1 |
| 9 | alchemist golem | — | construct/golem | 默认名图 | 0.8 |
| 10 | swarm hive | — | horror/aquatic | **tall** 显式 nice_tile → `native_tall=true` | 0.7 |
| 11 | Forest Troll Hedge-Wizard | —（唯一） | giant/troll | **tall** `nice_tile{tall=1}`，唯一路径，`unique=true` | 0.7 |
| 12 | ultimate shivgoroth | — | elemental/ice | **tall** 显式 nice_tile → `native_tall=true` | 0.7 |

五个非唯一 native-tall，一个唯一 tall，六个 64×64 单图；四个绑定 define_as，一个是唯一怪。**同体形／召唤**：swarm hive 的召唤物是 swarming horror（批次 Z 棋子）；orc summoner 的 Minotaur／Ritch Flamespitter／Spider 召唤各走自己的叶子；没有任何天赋、效果或事件用别的原生 PNG 造出这十二个名字。venom wyrm 的 renegade-wyrmics 随机首领走“非唯一 tall 保持原生”既有路径（测试有正反例），grushnak-pride 的随机精英兽人由 define_as 反查，走 `captureRandomOrigin`（测试有正例）。

## 分包

- Pack 1：entrenched horror、boiling horror、swarm hive、ultimate shivgoroth
- Pack 2：orc elite fighter、orc elite berserker、orc summoner、greater mummy
- Pack 3：shadowblade、venom wyrm、alchemist golem、Forest Troll Hedge-Wizard
- Pack 4 orc elite fighter 重做（pack 2 调用报“Selected model is at capacity”，无图）；pack 5 orc summoner 重做（pack 2 最大不透明半径 1.003 超 0.867，图腾杖与灵体越过盘沿）；pack 6 greater mummy 重做（pack 2 未返回路径，无图）；pack 7 greater mummy 第三次（pack 6 半径 1.024，大剑与裹布越界）；pack 8 orc summoner 第三次（pack 5 过全部数值门控，但 48px 是一团橄榄褐，改成大块亮面）；pack 9 shadowblade 重做（v1 48px 是一团深靛蓝）；pack 10 shadowblade 第三次（pack 9 亮但底盘偏移 +9.96 超 ±8，缩小并锁盘面亮度）

## 设计约束（生图前定的，不是事后补）

沿用批次 R–AA 的评审教训：主体大块面一律中亮到亮，沿轮廓一圈亮边光，禁止黑色主体；`DARKFIX` 段用于原图近黑或偏暗的主体（entrenched horror、swarm hive、orc elite 两款、orc summoner、greater mummy、shadowblade、alchemist golem、hedge-wizard、ultimate shivgoroth）。盘面措辞沿用“at reference lightness, a hair lighter, never darker”。tall 主体统一要求“画成一个紧凑的直立单体填满圆盘，不出高画布”。

同族区分（对照既有棋子，非仅换色）：

- entrenched horror：粗短的淡石灰岩柱，覆盖藤壶状突起，板缝里有脉动的青绿光，周围环生八条向外卷曲又钩回的青绿色触手；对既有獠牙鱼头 ravenous horror、银鱼环 swarming horror、粉色婴儿脸团 bloated horror。
- boiling horror：悬浮的水绿色沸腾水球，顶部白色泡沫与蒸汽，透出橙金热核；对既有靛蓝透镜 void horror 与上述水生恐魔。
- swarm hive：珍珠灰的脉动肉丘，遍布粉色口器，口中涌出小银鱼状恐魔；对既有粉色团块 bloated horror、粉褐色带骷髅的 necrotic mass。
- ultimate shivgoroth：直立的深蓝宝石色冰巨像，胸口青白核心，冰锥冠，环绕一圈冰片与白雪；对既有蹲伏的浅蓝 shivgoroth 与白色冰巨人 greater shivgoroth（后者无冠、无环、偏白）。
- orc elite fighter：抛光钢甲配宝蓝珐琅与金边，封闭大盔顶白色马毛冠（无角），巨大长方形塔盾带尖刺盾心立在身前，战斧收在盾后；对既有灰甲、有角盔、圆形红条盾的 orc fighter 与淡钢直角持短斧的 orc berserker。
- orc elite berserker：前倾冲锋的兽人，朱橙色漆面重甲配金铆钉，奶白毛皮披肩，骷髅冠盔加两支向前的盘绕羊角，骷髅串链，单月牙刃巨斧在身后低扫；对既有直立淡钢甲、直角、短斧的 orc berserker。
- orc summoner：野性兽灵萨满，斑纹兽皮披肩，鹿角与獠牙头饰，骨珠项链，手持缀羽兽颅图腾杖，三缕青绿色灵体缠绕；对既有全部着色长袍的 orc corruptor／necromancer／pyromancer／cryomancer／blood mage。
- greater mummy：高瘦、象牙色干净亚麻裹布，蓝金条纹法老头饰，绿松石金项圈，青铜大剑扛肩，另一手举起冰蓝光；对既有平淡褐绷带 rotting mummy、苍白精灵 ancient elven mummy、金甲圆盾 greater mummy lord。
- shadowblade：跃起的双弯刀暗影决斗者，交叉成 X 的两把银色弯刀，白色半面具，飘曳的淡紫蓝围巾与斗篷，淡丁香色影之弯月；对既有灰斗篷红腰带单匕首 assassin、深蓝兜帽 rogue、棕斗篷 thief、护目镜 rogue sapper。
- venom wyrm：后腿蹲坐、身体直立的 S 形长颈毒龙，宽扇形棘冠鬃毛，颚间滴落酸液，尾巴向上卷；对既有橄榄绿贴地带翼 venom drake 与红色盘环 fire wyrm。
- alchemist golem：修长、抛光的浅褐砂岩傀儡，金色符文镶嵌，单圆青眼与胸口青色宝珠，双臂下垂无武器；对既有橙色持锤 golem 与灰色碎石 broken golem。
- Forest Troll Hedge-Wizard：同为黄绿皮肤，但是干瘦驼背的老巨魔，身披梅紫色花纹礼袍与黑色扣带，白色乱眉，双手间燃着橙黄火焰；对既有腰布壮汉 forest troll、褐色持矛 cave troll、灰色 stone troll。

## ImageGen 记录

**19／28 次**（`gpt-6.1-sol`＋`--ephemeral`，逐次串行，只用 run_imagegen.py 默认）。十二款各 1 次，另七次为返工（每款至多 3 次）：

- orc elite fighter（2 次）：首次“Selected model is at capacity”，无图（no-structured-result）；pack 4 重做，一次入选，掩膜亮度 87.5。
- orc summoner（3 次）：首图最大不透明半径 1.003（上限 0.867），杖与灵体越界，未入库；pack 5 缩小短杖后入库（v1，数值全过，48px 却是一团橄榄褐，移入 `superseded/`）；pack 8 换成亮青柠皮肤、奶蜜色毛皮、白骨鹿角与大块青绿灵光，v2 入选，100.7。
- greater mummy（3 次）：首次未返回路径（provenance-rejected）；pack 6 半径 1.024，大剑与裹布越界，未入库；pack 7 短剑紧贴肩、缩小后入选，103.1。
- shadowblade（3 次）：v1 掩膜亮度 77.7，但 48px 是一团深靛蓝，移入 `superseded/`；pack 9 提亮版底盘偏移 +9.96（超 ±8），未入库；pack 10 缩小并锁盘面亮度，v2 入选，偏移 -0.37，97.6。

无 PENDING 请求、无豁免、未降低任何阈值（生产测试的亮度下限仍是 65；所有入选件不低于 77.4）。

## 48px 评审

`art/monster-batch-ab/review/floor-readability-48.png`、`floor-readability-48-x2.png`：十二款放在十张真实精修地板上（黄框为本区地板，golem-graveyard 与 reknor 用最接近的哥特／Kor'Pul 石地板）。掩膜亮度：Forest Troll Hedge-Wizard 77.4、orc elite berserker 82.7、orc elite fighter 87.5、alchemist golem 95.7、shadowblade 97.6、orc summoner 100.7、venom wyrm 101.7、greater mummy 103.1、entrenched horror 105.4、ultimate shivgoroth 109.8、swarm hive 139.8、boiling horror 164.7。48px 上最弱的是 Forest Troll Hedge-Wizard（梅紫礼袍偏暗，靠黄绿皮肤与橙色火焰辨认），其次是 orc elite berserker（橙红与金色在暖色地板上略融）；与已交付的 rogue sapper v2、forest wight 相当，没有再返修。
