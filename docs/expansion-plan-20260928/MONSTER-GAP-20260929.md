# 怪物棋子缺口调查（2026-09-29）

## Batch B 离线状态（2026-09-29）

源码与离线美术新增五款：Shax、Horned Horror、Norgos Guardian、skeleton archer、armoured skeleton warrior。三位守关怪的底盘明度逐资产双哈希豁免（`art/production/waivers/monster-batch-b.json`）已于 2026-09-29 经评审批准；全部仍待实机。其余 E2 的 skeleton magus、skeleton assassin、ghoul、ghast、ghoulking 均无显式原生 `image=`，未确认稳定外观合同，保持原生、不生图。skeleton master archer 首稿与普通弓手几乎相同、缺原生黑金甲区分，评审拒收，保持原生待重做。见 `art/monster-batch-b/REVIEW.md` 与 `evidence/monster-batch-b-20260929/source-contracts.json`。以下历史调查数量为 Batch B 之前快照。

## Batch A 离线状态（2026-09-29）

本表以下数量是本次美术之前的调查快照。Batch A 已在源码／离线层接入 Wrathroot、Snaproot、Minotaur、Sandworm Queen、Corrupted Sand Wyrm、Rantha、Varsha、Norgos Frozen、electric eel、ancient dragon turtle 共十款；Shax、Horned Horror、Norgos Guardian 的两次生图仍未通过门控，继续原生。已有 giant eel／dragon turtle 保持原图；Trollmire FLOODED 加载器明确排除 squid／ink squid。heart-gloom 非净化和净化版六种固定前缀已对已收录 rodent／canine 精确基础身份复用棋子，无新图。全部新接入尚待独立实机验证。详见 `art/monster-batch-a/REVIEW.md`、`evidence/monster-batch-a-20260929/source-contracts.json` 与 `<workspace>/tmp/codex-monA/REPORT.md`。

数据来源：`overload/mod/class/CheckerTokens.lua`（43 个已收录身份，按 `name`+`type`+`subtype`+`define_as` 精确匹配）、`data/token-manifest.json`、`docs/expansion-plan-20260928/PLAN.md`、`evidence/map-survey-20260928/`（12 个区域的实机普查，`unmapped-identities.csv`）、以及本轮对 16 个未被实机普查覆盖的区域（`slazish-fen`、`thieves-tunnels`、`tempest-peak`、`halfling-ruins`、`reknor`、`reknor-escape`、`ardhungol`、`lake-nur`、`ruined-dungeon`、`blighted-ruins`、`crypt-kryl-feijan`、`golem-graveyard`、`ritch-tunnels`、`deep-bellow`、`last-hope-graveyard`、`mark-spellblaze`）的 `zone.lua`／`npcs.lua`／`data/general/npcs/*.lua` 源码直读。`ancient-elven-ruins`、`town-derth`、`wilderness` 不在本次棋盘覆盖目标区域清单内，已排除。

## 一、概要统计

- 目标区域：29 个 short_name（含 Trollmire 洪水/非洪水布局与 `trollmire-treasure` 第4层静态图、Kor'Pul DEFAULT/HIDEOUT）。
- 已有实机普查数据的区域：12 个（trollmire、ruins-kor-pul、old-forest、rhaloren-camp、dreadfell、norgos-lair、daikara、maze、heart-gloom、sandworm-lair、scintillating-caves、unremarkable-cave）。
- 仅靠源码直读补全的区域：16 个（其余目标区域，均无独立地形套件，原生地形+原生怪物）。
- 与目标区域相关的未收录身份（含随机池溢出）：**82 个**（来自实机普查 CSV，按目标区域过滤后）+ 本轮源码直读新发现的**约 40 个**专属首领/主题怪物/家族条目 = 合计约 **120 个不同身份** 处于"未收录"状态。
- 其中确认为**零出图改名变体**（同 `image`/`type`/`subtype`，仅运行时前缀改名）：heart-gloom 的 9 个"gloomy/deformed/sick"鼠兔与 1 个"gloomy wolf"，共 **9 个身份**（wolf 变体与 8 个已收录鼠兔的改名版本），只需匹配逻辑扩展，不需要新图。
- 确认为**已支持外观合同（invis.png + 单张 add_mos 高体 tall-image，且 `unique=true`）**、只缺美术的地城首领/守关怪：**约 27 个**，分布在几乎所有目标区域，是最高优先级出图对象。
- 确认为**外观合同存在缺口**（同样是 invis.png + add_mos 高体组合，但 `unique` 不为真，`CheckerTokens.nativeTallImage()` 现在只认 `entry.unique==true`，无法覆盖）：**6 个**——`dremling`（maze）、`shivgoroth`／`greater shivgoroth`（norgos-lair）、`naga tidewarden`／`naga tidecaller`（slazish-fen）、`xhaiak arachnomancer`／`shiaak venomblade`（ardhungol）。这是本轮发现的主要工程缺口，不是单纯的美术缺口。
- 确认为**应保持原生**（无 `image`/`nice_tile`，走原生纸娃娃或默认类型贴图，或运行中途切换贴图）：`Melinda`（crypt-kryl-feijan，任务态切图）、`Harno`/`Lithfengel`（reknor）、`Norgan`（reknor-escape 护送 NPC）等，均无 `image=` 字段，走原生 `@`/字形显示。

## 二、建议出图批次（按优先级排序，每批约 8–12 款）

### 批次 1 — 已支持地形区 + 高频访问区的守关首领（标准 native-tall 合同，只缺美术）

这些首领全部使用与 Prox/Bill 相同的 `image="invis.png"` + 单张 `add_mos{display_h=2, display_y=-1}` 组合、且 `unique=true`，CheckerTokens 的 `nativeTallImage()` 已经验证支持该形状，出图后无需新工程。

| 身份 | define_as | 区域 | type/subtype | 来源 file:line |
| --- | --- | --- | --- | --- |
| Shax the Slimy | TROLL_SHAX | trollmire（洪水布局守关） | giant/troll, unique | `game/modules/tome/data/zones/trollmire/npcs.lua:112` |
| Wrathroot | WRATHROOT | old-forest（守关，晶化布局二选一） | giant/treant, unique | `.../old-forest/npcs.lua:93` |
| Snaproot | SNAPROOT | old-forest（Wrathroot 死后的后备守关） | giant/treant, unique | `.../old-forest/npcs.lua:155` |
| Horned Horror | HORNED_HORROR | maze（第1层守关） | horror/corrupted, unique | `.../maze/npcs.lua:47` |
| Minotaur of the Labyrinth | MINOTAUR_MAZE | maze（深层守关） | giant/minotaur, unique | `.../maze/npcs.lua:101` |
| Sandworm Queen | SANDWORM_QUEEN | sandworm-lair（两处守关） | vermin/sandworm, unique | `.../sandworm-lair/npcs.lua:84` |
| Corrupted Sand Wyrm | CORRUPTED_SAND_WYRM | sandworm-lair（次级唯一） | dragon/sand, unique | `.../sandworm-lair/npcs.lua:173` |
| Rantha the Worm | RANTHA_THE_WORM | daikara（非火山布局守关） | dragon/ice, unique | `.../daikara/npcs.lua:34` |
| Varsha the Writhing | VARSHA_THE_WRITHING | daikara（火山布局守关） | dragon/fire, unique | `.../daikara/npcs.lua:96` |
| Norgos, the Frozen | FROZEN_NORGOS(变体) | norgos-lair | animal/bear, unique | `.../norgos-lair/npcs.lua` 约第2行块 |
| Norgos, the Guardian | NORGOS | norgos-lair（主守关） | animal/bear, unique | `.../norgos-lair/npcs.lua` 约第48行块 |

（共 11 款；`skeleton-warrior`族的 Prox/Bill 已收录，不重复列出。）

### 批次 2 — 胶质收尾（E1b，延续已完成的 E1）

| 身份 | 来源 file:line | 备注 |
| --- | --- | --- |
| green ooze | `data/general/npcs/ooze.lua:56` | sandworm-lair、trollmire(洪水) |
| red jelly | `data/general/npcs/jelly.lua:73` | daikara |
| blue jelly | `data/general/npcs/jelly.lua:89` | unremarkable-cave |
| crimson ooze | `data/general/npcs/ooze.lua:127` | unremarkable-cave |
| gelatinous cube | `data/general/npcs/ooze.lua:116` | sandworm-lair、unremarkable-cave |
| Malevolent Dimensional Jelly | `data/general/npcs/jelly.lua:152`（unique） | 高等级稀有唯一果冻，池内高罕见度 |

PLAN.md 中列出的 white ooze/brittle clear ooze/slimy ooze/poison ooze/morphic ooze 未在任一目标区域实测出现（罕见度高或不在目标区域池表内），暂不列入本批。

### 批次 3 — E2 早期亡灵（骷髅/食尸鬼族，dreadfell、unremarkable-cave、halfling-ruins 共用）

| 身份 | 来源 file:line | 出现区域 |
| --- | --- | --- |
| skeleton archer | `data/general/npcs/skeleton.lua:114` | dreadfell、unremarkable-cave、halfling-ruins池 |
| skeleton magus | `data/general/npcs/skeleton.lua:128` | dreadfell、unremarkable-cave、halfling-ruins池（普查中出现次数最高的单一未收录身份，7次） |
| armoured skeleton warrior | `data/general/npcs/skeleton.lua:149` | dreadfell、halfling-ruins池（CheckerTokens.lua:62 注释已明确其与 skeleton-warrior 是不同、带盾身份） |
| skeleton master archer | `data/general/npcs/skeleton.lua:175` | dreadfell、halfling-ruins池 |
| skeleton assassin | `data/general/npcs/skeleton.lua:193` | halfling-ruins池（稀有） |
| ghoul | `data/general/npcs/ghoul.lua:49`（define_as GHOUL） | daikara、dreadfell、halfling-ruins池 |
| ghast | `data/general/npcs/ghoul.lua:66` | daikara、dreadfell、unremarkable-cave、halfling-ruins池 |
| ghoulking | `data/general/npcs/ghoul.lua:87` | dreadfell、halfling-ruins池 |

### 批次 4 — E3 Rhaloren 营地与蚁类

| 身份 | 来源 file:line | 备注 |
| --- | --- | --- |
| elven guard | `data/general/npcs/elven-warrior.lua:53` | rhaloren-camp 出现次数最高未收录身份（11次） |
| mean looking elven guard | `data/general/npcs/elven-warrior.lua:67` | rhaloren-camp |
| elven mage | `data/general/npcs/elven-caster.lua:55` | rhaloren-camp、mark-spellblaze池 |
| elven tempest | `data/general/npcs/elven-caster.lua:72` | rhaloren-camp、mark-spellblaze池 |
| giant white ant | `data/general/npcs/ant.lua:45` | old-forest、rhaloren-camp、trollmire(洪水) |
| giant carpenter ant | `data/general/npcs/ant.lua:62` | ruins-kor-pul(HIDEOUT)、old-forest、unremarkable-cave |
| giant black ant | `data/general/npcs/ant.lua:119` | old-forest |
| giant yellow ant | `data/general/npcs/ant.lua:107` | unremarkable-cave |
| giant blue ant | `data/general/npcs/ant.lua:95` | unremarkable-cave |
| giant brown ant | `data/general/npcs/ant.lua:53` | scintillating-caves |

精灵 NPC 需要装备/姿态与玩家精灵棋子区分（AGENTS.md 既定要求）。

### 批次 5 — 沙虫本体 + 水晶/植物（合并 E4 本体与 E5）

| 身份 | 来源 file:line | 备注 |
| --- | --- | --- |
| sandworm | `data/general/npcs/sandworm.lua:51` | maze、sandworm-lair |
| sandworm burrower | 未直接定位（vermin/sandworm 家族，sandworm-lair 出现次数第2高，9次） | sandworm-lair |
| sandworm destroyer | `data/general/npcs/sandworm.lua:57` | dreadfell、sandworm-lair |
| white crystal | `data/general/npcs/crystal.lua:108` | scintillating-caves |
| red crystal | `data/general/npcs/crystal.lua:96` | scintillating-caves |
| crimson crystal | `data/general/npcs/crystal.lua:130` | scintillating-caves |
| poison ivy | `data/general/npcs/plant.lua:75` | trollmire、unremarkable-cave |
| honey tree | `data/general/npcs/plant.lua:90` | old-forest |
| treant | `data/general/npcs/plant.lua:57` | old-forest池（普查未直接命中，池内存在） |

`elemental crystal`（construct/crystal，`image="trap/trap_beam.png"`，trollmire L3）实为陷阱贴图借用的显示，不是常规怪物单图，需先核实是否属于"怪物"渲染路径，暂不并入本批。

### 批次 6 — 独立地城专属首领（无地形套件覆盖、无普查数据的 12 个区域，各自"门面"唯一首领）

均为标准 `invis.png` + 单张 `add_mos` 高体组合、`unique=true`，只需新增美术条目：

| 首领 | define_as | 区域 | type/subtype | 来源 file:line |
| --- | --- | --- | --- | --- |
| Lady Zoisla the Tidebringer | ZOISLA | slazish-fen | humanoid/naga, unique | `.../slazish-fen/npcs.lua:116` |
| Urkis, the High Tempest | URKIS | tempest-peak（守关） | humanoid/human, unique | `.../tempest-peak/npcs.lua:29` |
| Golbug the Destroyer | GOLBUG | reknor（第4层静态图首领） | humanoid/orc, unique | `.../reknor/npcs.lua:28` |
| Brotoq the Reaver | BROTOQ | reknor-escape（第1层首领） | humanoid/orc, unique | `.../reknor-escape/npcs.lua:38` |
| Ungolë | UNGOLE | ardhungol（守关） | spiderkin/spider, unique | `.../ardhungol/npcs.lua:26` |
| Half-Finished Bone Giant | HALF_BONE_GIANT | blighted-ruins（守关） | undead/bone_giant, unique | `.../blighted-ruins/npcs.lua:73` |
| Kryl-Feijan | KRYL_FEIJAN | crypt-kryl-feijan（终层首领） | demon/major, unique | `.../crypt-kryl-feijan/npcs.lua:28` |
| Atamathon the Giant Golem | ATAMATHON | golem-graveyard | construct/golem, unique | `.../golem-graveyard/npcs.lua:24` |
| Ritch Great Hive Mother | HIVE_MOTHER | ritch-tunnels（守关） | insect/ritch, unique, 显式单图非composite | `.../ritch-tunnels/npcs.lua:98` |
| The Mouth | THE_MOUTH | deep-bellow（第3层首领） | horror/corrupted, unique | `.../deep-bellow/npcs.lua:27` |
| The Abomination | ABOMINATION | deep-bellow（后备守关） | horror/corrupted, unique | `.../deep-bellow/npcs.lua:133` |
| Celia | CELIA | last-hope-graveyard（墓穴首领） | humanoid/human, unique | `.../last-hope-graveyard/npcs.lua:28` |

这 12 个区域目前均无地形套件、无普查数据、随机池覆盖率也低，出这批图能让每个区域至少有一个"有身份感"的棋子门面，且不依赖地形改动。

### 批次 7 — 次要首领与常驻随从（含外观待核实项）

| 身份 | 区域 | 备注 |
| --- | --- | --- |
| Massok the Dragonslayer | daikara（后期支线唯一） | `.../daikara/npcs.lua:163`，标准 native-tall |
| Spellblaze Crystal | scintillating-caves（守关） | `.../scintillating-caves/npcs.lua:30`，**显式 `image=` 单图，非 composite，出图更简单** |
| Spellblaze Simulacrum | scintillating-caves（后备守关） | `.../scintillating-caves/npcs.lua:78`，标准 native-tall |
| The Master | dreadfell（主线最终首领） | `.../dreadfell/npcs.lua:34`，**显式 `image="npc/the_master.png"` 单图，非 composite** |
| Pale Drake | dreadfell（后备守关） | `.../dreadfell/npcs.lua:138`，标准 native-tall |
| Fillarel Aldaren | unremarkable-cave（可招募同伴） | `.../unremarkable-cave/npcs.lua` 约第30行块，标准 native-tall，友方 |
| Krogar | unremarkable-cave（可招募同伴，define_as CORRUPTOR） | `.../unremarkable-cave/npcs.lua` 约第101行块，标准 native-tall，友方 |
| Z'quikzshl the skeletal mold | `data/general/npcs/molds.lua:101`（unique） | 稀有唯一霉菌，`image="npc/immovable_molds_skeletal_mold.png"` 单图 |
| Rhaloren Inquisitor | rhaloren-camp | **无 `image=`/`nice_tile` 字段**，疑似走原生纸娃娃/默认贴图，出图前需夹具核实渲染路径 |

## 三、分区缺口清单

以下按区域列出**主题/专属**怪物（zone-specific 或该区域特别加载的 general npc 文件里的成员），随机池家族只列文件名不逐条展开。

| 区域 | 主题/专属未收录身份（节选，完整见普查 CSV 或上表） | 随机池家族（简要） |
| --- | --- | --- |
| trollmire（洪水/非洪水共用池） | Shax the Slimy(守关唯一)、Aluin the Fallen(后备守关，原生@字形无image，保持原生)、electric eel(洪水布局特有水生怪，用户报告)、ancient dragon turtle(池内高罕见度，未在L1实测命中)、poison ivy、elemental crystal(陷阱贴图借用)、broken golem | rodent/vermin/canine/troll/snake/plant/swarm/bear + 洪水专属 aquatic_critter(不含乌贼) |
| ruins-kor-pul (DEFAULT/HIDEOUT) | 无区域专属未收录唯一身份；缺口全部是随机池溢出 | giant carpenter ant、black jelly 等来自共享池 |
| old-forest | Wrathroot/Snaproot(守关)、honey tree、treant、giant white/black ant、grizzly bear(`image=invis.png`，需核实是否走 nice_tile tall=1) | plant、ant、bear |
| rhaloren-camp | Rhaloren Inquisitor(唯一，外观待核实)、elven guard 族 4 款 | rodent、vermin、molds、elven-warrior、elven-caster |
| dreadfell | The Master(主线首领)、Pale Drake/Borfast/Aletta/Filio(4 个支线/后备唯一，后三者无image走原生)、skeleton archer/magus/master archer/armoured warrior、ghoul/ghast/ghoulking、lesser vampire/vampire、giant spider/spitting spider | skeleton、ghoul、vampire、spider 家族溢出 |
| norgos-lair | Norgos, the Frozen / the Guardian(2 唯一守关)、shivgoroth/greater shivgoroth(**非唯一 composite，合同缺口**) | shivgoroth 家族 |
| daikara | Rantha the Worm/Varsha the Writhing(二选一守关)、Massok the Dragonslayer(支线唯一)、yellow/red jelly、xaren、fire imp、cold/fire drake hatchling | xorn、demon-minor、dragon-cold/fire 池 |
| maze | Horned Horror/Minotaur of the Labyrinth(2 层守关)、Nimisil(次要唯一，外观待核实)、dremling(**非唯一 composite，合同缺口**)、drem、drem master、brecklorn、dredgling、shadowblade | horror-corrupted、horror_temporal、thieve、ooze、jelly、ant |
| heart-gloom | The Withering Thing/The Dreaming One(2 唯一，需核实外观)、**9 个"gloomy/deformed/sick"改名变体，零出图** | rodent/bear/canine/plant（改名池） |
| sandworm-lair | Sandworm Queen(2 处守关)、Corrupted Sand Wyrm(次要唯一)、sandworm/burrower/destroyer、gelatinous cube、green ooze | sandworm 家族、ooze、jelly 溢出 |
| scintillating-caves | Spellblaze Crystal(守关，单图)、Spellblaze Simulacrum(后备)、white/red/crimson crystal、giant brown ant | crystal 家族 |
| unremarkable-cave | Fillarel Aldaren/Krogar(2 招募同伴，友方)、skeleton archer/magus、ghast、grave/forest wight、orc summoner/necromancer/corruptor、xorn、blinkwyrm(`image=invis.png`)、blade horror(`image=invis.png`) | skeleton、rodent、vermin、molds、snake 溢出 |
| thieves-tunnels | Assassin Lord(唯一首领，外观待核实)、Lost Merchant(友方，低优先级)、bandit lord、assassin/shadowblade(同 define_as THIEF_ASSASSIN)、rogue sapper | thieve.lua（cutpurse/rogue/thief/bandit 已收录） |
| tempest-peak | Urkis, the High Tempest(守关唯一)、Harkor'Zun 两段形态唯一(**需要两阶段外观合同**)、Burb 雪巨人唯一、gwelgoroth/snow-giant/storm-drake/xorn 家族 | gwelgoroth、xorn、snow-giant、storm-drake |
| halfling-ruins | Subject Z/Yeek Wayist(2 唯一，外观待核实)、skeleton archer/magus/armoured warrior/master archer/assassin、ghoul/ghast/ghoulking/risen corpse、bone giant 族 4 款 | skeleton、ghoul、bone-giant（此区不加载 all.lua，池窄） |
| reknor | Golbug the Destroyer(主首领)、Harno/Lithfengel(原生@/U字形，保持原生) | orc、troll |
| reknor-escape | Brotoq the Reaver(主首领)、Norgan(护送同伴，原生@字形，保持原生) | rodent、vermin、molds、orc、snake |
| ardhungol | Ungolë(守关唯一)、xhaiak arachnomancer/shiaak venomblade(**非唯一 composite，合同缺口，且为区域专属，无共享池**)、giant spider | spider |
| lake-nur | 无区域专属唯一/主题身份；静态图无手放 actor | aquatic_critter、aquatic_demon、horror_aquatic、horror、snake、plant、（泛滥密室内 naga 池） |
| ruined-dungeon | 无区域专属唯一身份；守关/惩罚怪均为程序化 random_elite/random_boss（若随机到已收录基础体，理论上已可经 randomOrigin 机制显示） | all、bone-giant、faeros、gwelgoroth、mummy、ritch |
| blighted-ruins | Half-Finished Bone Giant(守关唯一)、Necromancer(外观待核实)、fleshy/boney/sanguine experiment(3 款同族小怪) | rodent、vermin、ghoul、skeleton、bone-giant、horror-undead |
| crypt-kryl-feijan | Kryl-Feijan(终层唯一)、Melinda(**任务态切图，建议保持原生**)、Acolyte of the Sect of Kryl-Feijan(单图) | elven-warrior、elven-caster、minor/major-demon、ogre |
| golem-graveyard | Atamathon the Giant Golem(唯一) | construct |
| ritch-tunnels | Ritch Great Hive Mother(守关唯一)、ritch flamespitter/impaler、chitinous ritch | ritch（通用 ritch.lua 三款等级范围过高，本区基本不触发）、vermin、ant、jelly |
| deep-bellow | The Mouth(主首领)、The Abomination(后备守关)、slimy crawler(The Mouth 召唤，单图) | rodent、horror-corrupted、all |
| last-hope-graveyard | Celia(墓穴唯一首领)、棺材机制程序化随机首领(借用 skeleton/ghoul/vampire/bone-giant/lich 池) | 静态图无常规随机生成(`nb_npc={0,0}`) |
| mark-spellblaze | Grand Corruptor(唯一，外观待核实)、elven cultist/blood mage/corruptor(elven-caster 族剩余成员)、faeros 族 3 款、gwelgoroth 族 3 款(与 tempest-peak 共享) | rodent、vermin、faeros、gwelgoroth、elven-caster |

## 四、需要特殊外观合同或建议保持原生的项目

### 4.1 非唯一 native-tall 复合体——现有合同缺口（不是单纯缺图）

`CheckerTokens.lua` 的 `nativeTallImage()`（第109-122行）只在 `entry.unique==true` 时接受 `invis.png` + 单张 `add_mos` 的高体组合；以下 6 个身份使用完全相同的显示形状，但源码中 `unique` 不为真，因此目前**连"未收录"都算不上，而是被结构性排除**，需要先扩展外观合同（允许特定非唯一目录条目走 native-tall 路径），再谈出图：

- `dremling`（maze，`horror-corrupted.lua:79`，`resolvers.nice_tile{image="invis.png", add_mos={{image="npc/horror_corrupted_drem.png", ...}}}`）
- `shivgoroth` / `greater shivgoroth`（norgos-lair，`shivgoroth.lua:56`/`71`，家族还有 `ultimate shivgoroth` 但未在目标区域池中确认加载）
- `naga tidewarden` / `naga tidecaller`（slazish-fen，`slazish-fen/npcs.lua:61`/`78`，rarity=1，是该区域最常见的主题怪，且该区域随机池被完全清空、100% 依赖这两个身份，优先级高但受限于合同缺口）
- `xhaiak arachnomancer` / `shiaak venomblade`（ardhungol 专属，无共享通用池文件，`resolvers.nice_tile{tall=1}` 经 `resolvers.lua` 在加载期重写为同样的 invis.png+add_mos 形状）

`naga nereid`（slazish-fen）同样使用 `resolvers.nice_tile{tall=1}` 但未显式给出 `add_mos`，具体渲染形状需要夹具核实。

`The Fragmented Essence of Harkor'Zun` → `Harkor'Zun`（tempest-peak）是一对两阶段变形唯一敌人（后者 `type` 从 `elemental/xorn` 变为 `demon/major`），需要独立的"多阶段外观合同"，不能简单套用单形态 native-tall。

### 4.2 建议保持原生（不建议出图）

- **Melinda**（crypt-kryl-feijan）：`image="terrain/woman_naked_altar.png"`，救援剧情触发后中途切换为 `npc/woman_redhair_naked.png` 并清空 `display_w`，同一 actor 在任务过程中有两套原生贴图且运行时会变化，不符合当前"稳定单一外观"合同模型。
- **Harno, Herald of Last Hope** / **Lithfengel**（reknor）、**Norgan**（reknor-escape，护送同伴）：均无 `image=` 字段，走原生 `@`/`U` 字形显示，非图片渲染，棋子系统无从介入。
- **Lost Merchant**（thieves-tunnels）：友方任务 NPC（`faction="victim"`, `is_merchant=true`），非战斗怪物，即使出图优先级也应在所有战斗怪物之后。
- **ruined-dungeon** 的 `random_elite`/`random_boss` 惩罚生成、**last-hope-graveyard** 棺材机制的程序化随机首领：均通过引擎的"随机首领生成"机制现取基础体，不是固定身份；若随机到的基础体恰好在目录内，`CheckerTokens.captureRandomOrigin`/`recordRandomOrigin` 的既有链路理论上已可覆盖，不需要单独新增身份。

### 4.3 出图前需要先在夹具中核实渲染路径（源码未见 `image=`/`nice_tile`，可能是原生纸娃娃或默认类型贴图）

Rhaloren Inquisitor（rhaloren-camp）、Necromancer（blighted-ruins）、Assassin Lord（thieves-tunnels）、Subject Z / Yeek Wayist（halfling-ruins）、Grand Corruptor（mark-spellblaze）、The Withering Thing / The Dreaming One（heart-gloom）、Nimisil（maze）。这些条目在 `npcs.lua` 中没有出现 `image=`、`resolvers.nice_tile`、`shader=`、`moddable_tile=`、`anim=` 等字段，按照 AGENTS.md「装备/纸娃娃变体…不在当前批准的生产路线内」的既有原则，很可能需要在隔离夹具中实例化后才能判断是否可出图，不能直接排期。

### 4.4 零出图：改名变体（heart-gloom）

`heart-gloom/npcs.lua:22-36` 对 `rodent.lua`/`bear.lua`/`canine.lua`/`plant.lua` 池内所有 `rarity` 非空条目统一执行 `e.name = rng.table{"gloomy ", "deformed ", "sick "}..e:getName()`（`is_purified` 布局下改为 "dreaming "/"slumbering "/"dozing "），`image`/`type`/`subtype`/`define_as` 完全不变。普查中实际命中的 9 个实例（sick giant white mouse、sick giant brown rat、sick giant brown mouse、gloomy giant crystal rat、gloomy giant grey rat、deformed giant rabbit、deformed giant white rat、deformed giant grey mouse、gloomy wolf）全部对应**已收录**的基础身份（对应 8 款鼠兔 + wolf）。这是本次调查里最大的"零成本"收益：只需要按已有"改名身份走溯源路径"的既定原则扩展匹配逻辑（例如按 `image`+`type`+`subtype` 忽略名称前缀，或维护一张改名前缀白名单），完全不需要新美术。熊科的 cave bear/war bear/grizzly bear/polar bear 若被同一改名逻辑命中，则是**未收录**基础体的改名版，不适用零出图路径。
