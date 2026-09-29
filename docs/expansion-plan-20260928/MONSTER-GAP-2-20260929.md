# 怪物棋子缺口调查 II（2026-09-29）

本文续 `MONSTER-GAP-20260929.md` 与 `CONTRACTS-B5-B7-20260929.md`，只做只读源码调查：未启动游戏、未生图、未改任何代码或数据、未提交。目录基线为 `overload/mod/class/CheckerTokens.lua` 的 **131** 款身份（`PROGRESS.md` 0.6.27）。范围是 `hooks/load.lua:32` 的 Board terrain 说明与 `CheckerTerrain.lua` 区域门控共同覆盖的 **47 个区域**（`orc-breeding-pit` 与 `illusory-castle` 按要求排除；后者在地形门控里本来就没有条目，前者虽在 `CheckerTerrain.lua` 有条目但当前版本不可达）。


## 0. 摘要

- **总计**：47 个区域里，玩家实际会遇到（保证首领／剧情／任务，或按引擎权重模型单区完整通关预期遇见数 E≥0.3 的池内怪）的**不同身份共 392 个**，其中 **126 个已在目录**，**266 个未收录**。这 266 个的裁决为：**READY 252**（其中单图 178、非唯一 native-tall 需带 `native_tall=true` 68、tall 内层图≠默认名或仅 nicer_tiles 下可命中 6）、**NEEDS-CONTRACT-EXTENSION 7**、**KEEP-NATIVE 7**。E<0.3 的纯稀有尾部另有 41 个身份（含 Queen Ant、Phoenix、lich 系等 rarity 上千的超稀有唯一），不列入。
- **最大的一批「近零工程」收益**不在美术：Heart of the Gloom 的改名变体前缀映射（`CheckerTokens.lua:328-337` 只放行 vermin/rodent 与 animal/canine 基底）没有放行目录里已有基底的 `animal/bear`（brown bear、black bear）和 `immovable/plants`（poison ivy、giant venus flytrap）。把这两个 type 加进白名单（一处条件），即可让这四种变体（合计 E≈13.2）立刻出棋子，见 §6。
- **上一轮的「合同缺口」已被 `native_tall` 字段吸收**（`CheckerTokens.lua:361`，先例 `ancient-dragon-turtle`、`treant`、`shivgoroth`、`dremling` 等）。本轮所有「非唯一 + invis.png + 单个 `add_mos{display_h=2,display_y=-1}` + 内层图==默认名」的身份都按 READY 判定，只需给目录条目加 `native_tall=true`，不需要改代码。
- 真正需要动 `CheckerTokens.lua` 的只有一类：**同名不同 define_as**（catalog 以 name 为唯一键，`CheckerTokens.lua:313-317` 断言不许重名，`exactIdentity` `:385-387` 只按名取一个条目）——`shadow claw`×2、`ogre sentry`×2、`old vats`×2（VAT1/VAT2）、`orc warrior` 的 ORC_ATTACK，共 7 条 NEEDS。其中 `orc warrior` 只要先收 HILL_ORC_WARRIOR 就不是阻塞（ORC_ATTACK 会按 identity-changed 保持原生）。
- **KEEP-NATIVE 7 条**：Melinda[MELINDA]、Melinda[MELINDA_BEACH]、Spacial Disturbance[SPACIAL_DISTURBANCE]、The Shade[SHADE]、huge sandworm burrower[SANDWORM_TUNNELER_HUGE]、multi-hued crystal、shimmering crystal。原因分别是 2×2 无敌引路虫、粒子主体、运行期换图／纸娃娃、`shader` 字段（`identify()` 明确拒绝，`CheckerTokens.lua:405-406`）；`dreaming horror`（shader+粒子）在任何单区 E 都低于 0.3，未入表但同理保持原生。
- 一批**源码陷阱**（均已用行号核实，见 §8）：reknor 末层静态图引用了并不存在的 define_as `ORC_ARCHER`/`ORC_GUARD`（`maps/zones/reknor-last.lua:31`、`reknor-escape-last.lua:34`），这两处摆不出怪；`OVERPOWERED_WYRM`（vor-armoury）`rarity=false` 只被 eruan 的 sleeping-dragons 保险库引用，范围内不可达，已排除。
- **推荐下一批**：§7 批次 1（12 名保证首领／唯一怪：Shardskin、The Withering Thing、The Dreaming One、Weaver Queen、Murgol、Nashva、The Possessed、Subject Z、Grand Corruptor、Kyless、Assassin Lord、Ben Cruthdar），全部 READY、零工程改动；批次 2 起按 type 族群（elemental、giant、humanoid、aquatic……）出常见池怪，见 §7。


## 1. 方法与口径

### 1.1 怎么得到「玩家实际遇到的生物」

不推断、不凭名字：我在 `/tmp` 里写了一个**只读的独立 LuaJIT 复现器**（不进仓库、不启动游戏），逐行复刻引擎的实体加载路径，然后对 47 个区域（含 trollmire／old-forest／norgos／daikara／maze／heart-gloom／murgol／kor-pul 等的双布局，共 55 次运行）加载各自的 `npcs.lua`：

- `Entity:loadList` 的 `newEntity`／`base` 继承（`engine/Entity.lua:73-80` importBase、`:1179-1272` loadList；`load`/`loadIfNot`/`rarity(add,mult)`/`switchRarity` 语义照抄 `:1215-1258`，`all.lua` 的 `loadIfNot` 只补载尚未载入的文件）。
- `NPC:init` 的默认图公式 `modules/tome/class/NPC.lua:33`（无显式 `image` 且名字不是 "unknown actor" 时，`image = "npc/<type>_<subtype>_<name 小写、非字母数字→_>.png"`），并保留 importBase 会继承**具名基底已回填的 image** 这一细节（表中标「继承 base 的 image」）。
- `resolvers.nice_tile`（`modules/tome/resolvers.lua:1372-1385`，`tall=1` 简写用 `e.image`）在 nicer_tiles 开／关两种状态下的结果。
- 区域权重：`engine/Zone.lua:214-258` 的 `computeRarities`（每条 `max/rarity`，低于 `level_range` 下限时 `max=10000/(ood_factor*差)`，高于上限时 `10000/差`），`max_ood` 过滤 `:315`；引导者 `guardian` 在 `zone.max_level` 层生成（`engine/generator/actor/Random.lua:48-56`）。
- 所有 `file:line` 都是复现器记录的 `newEntity{` 调用起始行，我抽查了十余条（unhallowed-morass/npcs.lua:41、losgoroth.lua:59、naga.lua:52 等）与源码一致。

### 1.2 频度模型 E

E ＝ 该身份在一个区域**完整通关（各层）**的预期遇见数 ≈ 层数 × `nb_npc` 区间中值 × 该身份在当层池内的权重占比（参考玩家等级取区域下限与中值，取两者较大值；`max_ood=2` 的区域按 `Zone.lua:315` 过滤）。它是模型估算，只用于**排序与分档**，不是实测。未建模：random elite／random boss 改写（`generator/actor/Random.lua:33-45` 的 25% 稀有概率沿用既有 `captureRandomOrigin` 路径）、`data/general/events`、保险库内的固定放置（保险库怪从同一批通用文件里按名字／type 抽取，已经计入池权重）。特殊池区域另算：keepsake-meadow 洞穴层（`cave_rarity`）、lake-nur 水下层（`water_rarity`／`horror_water_rarity`，`lake-nur/zone.lua:86-112`）、temporal-rift 各层类型过滤（`zone.lua:61,74,95`）。

分档：**保证首领／剧情**（`guardian`、末层静态图、任务、脚本生成）；**常见池** ΣE≥6；**偶见池** 1.5≤ΣE<6；**稀有池** ΣE<1.5（仍≥0.3 的区）；**后备守关**（东行后回访才出）。

通用文件以 `rarity(4,35)` 载入的 `all.lua` 让几乎所有区域都带着约 150 个身份的「稀有拖尾」（单个 E 约 0.3–1，集合起来占单区生成量的约一成）；本文只在某区 E≥0.3 时才把它算作「遇到」，尾部按区汇总在 §2 表内。

### 1.3 合同判定（对照 `CheckerTokens.lua` 现状）

- **READY（单图）**：`appearance()`（`:398-421`）返回 `single`：`actor.image==entry.image`，无 `moddable_tile`（:405）、`shader`（:406）、`anim`（:407）、`add_displays`（:408）、`textures`（:409），`add_mos` 为空（忽略 `_isshaderaura` 光环条目，`:349-358`）。
- **READY（native_tall）**：`nativeTallImage()`（`:360-383`）：`invis.png` + 恰好一个非光环 `add_mos`，键仅限 `image/display_h/display_y/display_w/display_x/display_scale`，且 `display_h==2`、`display_y==-1`、内层 `image==entry.image`；**唯一身份自动允许，非唯一身份要在目录条目写 `native_tall=true`**。nicer_tiles 关闭时同一身份回到 `single` 分支，同样命中。
- **READY（内层图≠默认名）**：tall 内层图与 NPC.lua:33 默认名不同（Atamathon 先例）。nicer_tiles 开启时命中；关闭时 `actor.image` 是默认名≠`entry.image`，回退原生，不报错。
- **NEEDS-CONTRACT-EXTENSION**：当前 `identify()`/目录结构无法表达，需要具体的代码改动（每条写明）。
- **KEEP-NATIVE**：`identify()` 会拒绝，或外观由运行期状态决定，不建议做。
- `{tall=1}` 简写：`xhaiak arachnomancer`／`shiaak venomblade` 的隔离夹具探针（`CheckerTokens.lua:222-229` 注释所引 `evidence/monster-live-f-20260929/`）已证实展开为 `invis.png+add_mos{display_h=2,display_y=-1}` 且内层图＝按公式的磁盘文件名，本表 `tall=1` 的其余身份沿用该结论。


## 2. 分区覆盖表与总计

列说明：**遇到**＝该区保证／剧情身份＋池内 E≥0.3 身份（含已收录）；**已收录**＝其中已在目录的；READY／NEEDS／KEEP 只统计未收录的；**池覆盖**＝按 E 加权，该区随机池权重里已被目录覆盖的百分比（不含保证首领）；**尾部**＝E<0.3 的池内未收录身份数／其 E 之和。

| 区域（short_name） | 等级／层／布局 | 遇到 | 已收录 | READY | NEEDS | KEEP | 池覆盖 | 尾部 | 最大缺口（按 E 或保证首领） |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| Trollmire（`trollmire`） | 1–7／3层／FLOODED / DEFAULT | 55 | 53 | 2 | 0 | 0 | 99% | 18／1.5 | white ooze、Aluin the Fallen |
| Old Forest（`old-forest`） | 7–16／4层／CRYSTALINE / DEFAULT | 49 | 33 | 14 | 0 | 2 | 81% | 113／5.5 | Shardskin(首领)、black crystal(E4)、giant green ant(E3)、giant red ant(E3) |
| Slazish Fens（`slazish-fen`） | 1–7／3层／— | 4 | 3 | 1 | 0 | 0 | 69% | 0／0.0 | naga nereid(E8) |
| Rhaloren Camp（`rhaloren-camp`） | 1–7／3层／OVERGROUND / DEFAULT | 48 | 43 | 5 | 0 | 0 | 50% | 18／1.1 | elven guard(E17)、mean looking elven guard(E13)、elven mage(E7)、elven tempest(E7) |
| Dreadfell（`dreadfell`） | 15–26／9层／— | 106 | 52 | 54 | 0 | 0 | 50% | 93／10.4 | ghoul(E15)、skeleton magus(E10)、ghast(E8)、forest wight(E8) |
| Norgos Lair（`norgos-lair`） | 1–7／3层／INVADED / DEFAULT | 45 | 41 | 4 | 0 | 0 | 98% | 16／0.7 | ultimate shivgoroth、cave bear、war bear、white ooze |
| Daikara（`daikara`） | 7–16／4层／VOLCANO / DEFAULT | 89 | 55 | 34 | 0 | 0 | 50% | 91／5.2 | snow giant(E26)、fire drake hatchling(E11)、cold drake hatchling(E7)、umber hulk(E5) |
| The Maze（`maze`） | 7–16／3层／COLLAPSED / DEFAULT | 78 | 59 | 19 | 0 | 0 | 67% | 108／6.9 | drem(E10)、minotaur(E10)、brecklorn(E5)、grannor'vor(E5) |
| Heart of the Gloom（`heart-gloom`） | 1–7／3层／PURIFIED / DEFAULT | 22 | 18 | 4 | 0 | 0 | 99% | 0／0.0 | The Withering Thing(首领)、The Dreaming One(首领)、cave bear、war bear |
| Sandworm lair（`sandworm-lair`） | 7–16／3层／BIGWORM / DEFAULT | 25 | 19 | 5 | 0 | 1 | 70% | 4／0.4 | gigantic sandworm tunneler(E13)、gigantic corrosive tunneler(E9)、sand-drake(E5)、gigantic gravity worm(E5) |
| Ritches Tunnels（`ritch-tunnels`） | 1–7／3层／— | 20 | 15 | 5 | 0 | 0 | 58% | 0／0.0 | ritch flamespitter(E11)、chitinous ritch(E11)、ritch impaler(E9)、giant green ant(E2) |
| The Deep Bellow（`deep-bellow`） | 1–7／3层／— | 49 | 43 | 6 | 0 | 0 | 54% | 18／1.2 | drem(E17)、brecklorn(E8)、grannor'vor(E7)、drem master(E5) |
| Last Hope Graveyard（`last-hope-graveyard`） | 15–25／2层／— | 1 | 1 | 0 | 0 | 0 | — | 0／0.0 | — |
| Scintillating Caves（`scintillating-caves`） | 1–7／4层／TWISTED / DEFAULT | 53 | 48 | 5 | 0 | 0 | 88% | 16／1.5 | black crystal(E4)、blue crystal(E3)、cave bear、war bear |
| Unremarkable Cave（`unremarkable-cave`） | 25–35／1层／— | 89 | 44 | 45 | 0 | 0 | 59% | 105／7.0 | skeleton magus(E1)、carrion worm mass、black mamba、anaconda |
| Unknown tunnels（`thieves-tunnels`） | 14–28／2层／— | 10 | 4 | 6 | 0 | 0 | 78% | 0／0.0 | Assassin Lord(首领)、assassin、shadowblade、bandit lord |
| Tempest Peak（`tempest-peak`） | 15–22／2层／— | 77 | 40 | 37 | 0 | 0 | 17% | 96／4.4 | gwelgoroth(E13)、snow giant(E13)、storm drake hatchling(E6)、greater gwelgoroth(E4) |
| Ruined halfling complex（`halfling-ruins`） | 10–25／4层／— | 14 | 7 | 7 | 0 | 0 | 77% | 4／0.3 | Subject Z(首领)、Yeek Wayist(首领)、ghoul(E8)、skeleton magus(E8) |
| Lost Dwarven Kingdom of Reknor（`reknor`） | 18–35／4层／— | 95 | 42 | 53 | 0 | 0 | 42% | 91／10.3 | orc warrior(E27)、orc soldier(E14)、orc archer(E9)、orc assassin(E9) |
| Escape from Reknor（`reknor-escape`） | 1–7／3层／— | 56 | 49 | 7 | 0 | 0 | 82% | 15／0.5 | orc warrior(E18)、orc soldier(E9)、orc archer(E6)、white ooze |
| Lake of Nur（`lake-nur`） | 15–25／3层／FLOODED / DRY | 29 | 13 | 16 | 0 | 0 | 32% | 13／0.8 | squid(E8)、water imp(E8)、ink squid(E4)、bloated horror(E3) |
| Ruined Dungeon（`ruined-dungeon`） | 10–30／1层／ALT1（clues_layout） | 85 | 45 | 40 | 0 | 0 | 51% | 129／9.0 | giant green ant、giant red ant、cold drake hatchling、fire drake hatchling |
| Blighted Ruins（`blighted-ruins`） | 1–7／3层／— | 20 | 19 | 1 | 0 | 0 | 99% | 0／0.0 | ghoul |
| Dark crypt（`crypt-kryl-feijan`） | 25–35／5层／— | 21 | 2 | 18 | 0 | 1 | 0% | 0／0.0 | Melinda(首领)、elven cultist(E13)、elven blood mage(E13)、elven guard(E13) |
| Golem Graveyard（`golem-graveyard`） | 14–20／1层／— | 4 | 1 | 3 | 0 | 0 | 0% | 0／0.0 | broken golem(E3)、golem(E3)、alchemist golem |
| Ardhungol（`ardhungol`） | 25–32／3层／— | 122 | 47 | 75 | 0 | 0 | 14% | 70／7.4 | giant spider(E35)、spitting spider(E35)、chitinous spider(E35)、weaver young(E18) |
| Mark of the Spellblaze（`mark-spellblaze`） | 15–25／2层／— | 21 | 9 | 12 | 0 | 0 | 20% | 1／0.1 | Grand Corruptor(首领)、gwelgoroth(E10)、faeros(E9)、elven mage(E8) |
| Unhallowed Morass（`unhallowed-morass`） | 1–7／3层／— | 6 | 0 | 6 | 0 | 0 | 0% | 0／0.0 | Weaver Queen(首领)、weaver hatchling(E31)、orb spinner(E31)、fate spinner(E13) |
| Abashed Expanse（`abashed-expanse`） | 1–7／3层／— | 3 | 0 | 2 | 0 | 1 | 0% | 0／0.0 | Spacial Disturbance(首领)、losgoroth(E44)、manaworm(E20) |
| Temporal Rift（`temporal-rift`） | 16–30／4层／— | 15 | 0 | 15 | 0 | 0 | 0% | 0／0.0 | Ben Cruthdar, the Abomination(首领)、Rantha the Abomination(首领)、Chronolith Twin(首领)、Chronolith Clone(首领) |
| Murgol Lair（`murgol-lair`） | 1–7／3层／INVASION / DEFAULT | 14 | 5 | 9 | 0 | 0 | 38% | 0／0.0 | Murgol, the Yaech Lord(首领)、Lady Nashva the Streambender(首领)、yaech diver(E15)、squid(E15) |
| Southern Beach（`south-beach`） | 24–35／1层／— | 1 | 0 | 0 | 0 | 1 | — | 0／0.0 | Melinda |
| Tranquil Meadow（`keepsake-meadow`） | 15–25／6层／— | 12 | 0 | 10 | 2 | 0 | 0% | 0／0.0 | Kyless(首领)、Berethh(首领)、corrupted war dog(E12)、shadow claw(E12) |
| Noxious Caldera（`noxious-caldera`） | 25–35／2层／— | 30 | 17 | 13 | 0 | 0 | 61% | 137／8.4 | Mindworm(首领)、venom drake hatchling(E5)、faeros(E5)、cave bear(E2) |
| Old Conclave Vault（`conclave-vault`） | 20–30／4层／— | 24 | 13 | 7 | 4 | 0 | 78% | 0／0.0 | Healer Astelrid(首领)、slimy ooze(E5)、poison ooze(E5)、white ooze(E4) |
| Ruins of Telmur（`telmur`） | 30–40／5层／— | 18 | 6 | 12 | 0 | 0 | 36% | 146／18.1 | The Shade of Telos(首领)、ghoul(E11)、skeleton magus(E4)、ghast(E4) |
| Elven Ruins（`ancient-elven-ruins`） | 43–52／3层／— | 12 | 4 | 8 | 0 | 0 | 25% | 153／19.8 | Greater Mummy Lord(首领)、ancient elven mummy(E11)、rotting mummy(E6)、animated mummy wrappings(E3) |
| Vor Armoury（`vor-armoury`） | 30–40／2层／— | 75 | 17 | 58 | 0 | 0 | 12% | 97／6.4 | Warmaster Gnarg(首领)、orc pyromancer(E7)、orc cryomancer(E7)、orc warrior(E3) |
| Briagh's Lair（`briagh-lair`） | 30–40／1层／— | 7 | 2 | 5 | 0 | 0 | 52% | 0／0.0 | Briagh, Great Sand Wyrm(首领)、gigantic sandworm tunneler(E14)、gigantic corrosive tunneler(E9)、sand-drake(E5) |
| Caverns to the hidden valley（`valley-moon-caverns`） | 30–40／2层／— | 8 | 0 | 8 | 0 | 0 | 7% | 141／12.3 | wretchling(E14)、onilug(E14)、quasit(E14)、fire imp(E5) |
| Flooded Cave（`flooded-cave`） | 30–40／2层／— | 9 | 4 | 5 | 0 | 0 | 38% | 0／0.0 | Ukllmswwik the Wise(首领)、squid(E17)、water imp(E17)、ink squid(E9) |
| Temple of Creation（`temple-of-creation`） | 30–40／3层／— | 12 | 4 | 8 | 0 | 0 | 20% | 0／0.0 | Slasul(首领)、naga myrmidon(E54)、naga tide huntress(E11)、squid(E9) |
| Charred Scar（`charred-scar`） | 30–50／1层／— | 12 | 0 | 11 | 1 | 0 | 0% | 0／0.0 | High Sun-Paladin Rodmour(首领)、Elandar(首领)、Argoniel(首领)、Fyrk, Faeros High Guard(首领) |
| Fearscape（`demon-plane`） | 30–40／1层／— | 12 | 0 | 12 | 0 | 0 | 0% | 5／0.2 | Draebor, the Imp(首领)、wretchling(E10)、onilug(E10)、quasit(E10) |
| Yiilkgur, the Sher'Tul Fortress（`shertul-fortress`） | 18–25／1层／— | 4 | 0 | 4 | 0 | 0 | — | 0／0.0 | Weirdling Beast(首领)、Fortress Shadow、Training Dummy、Pumpkin, the little kitty |
| Rak'shor Pride（`rak-shor-pride`） | 30–60／3层／— | 95 | 20 | 75 | 0 | 0 | 13% | 96／7.6 | Rak'shor, Grand Necromancer of the Pride(首领)、bone giant(E13)、orc necromancer(E13)、orc blood mage(E7) |
| Ruins of Kor'Pul（`ruins-kor-pul`） | 1–7／3层／HIDEOUT / DEFAULT | 30 | 27 | 2 | 0 | 1 | 99% | 19／1.0 | The Shade(首领)、The Possessed(首领)、Kor's Fury |
| **合计（区域×身份对）** | | **1686** | **924** | **748** | **7** | **7** | | | |

**去重后的总计**：遇到 392 个不同身份 = 已收录 126 + 未收录 266（READY 252／NEEDS 7／KEEP 7）。目录 131 款里另有 5 款（Burb、Harkor'Zun 残片与完整体、Malevolent Dimensional Jelly、Z'quikzshl）在任何单区都低于 E 阈值，所以不在「遇到」里；它们是通用文件里 rarity≥数十的稀有唯一。

读表要点：覆盖最差的是地形已支持但**几乎没有怪物棋子**的区域——unhallowed-morass、abashed-expanse、temporal-rift、charred-scar、demon-plane、crypt-kryl-feijan、keepsake-meadow、golem-graveyard 池覆盖为 0%；ardhungol、vor-armoury、rak-shor-pride、valley-moon-caverns、tempest-peak 因为 spider／orc／undead／demon 大家族未收录而在 7–17%。反过来 trollmire／norgos-lair／heart-gloom／blighted-ruins／ruins-kor-pul 已在 98–99%。


## 3. 按区域枚举（只列未收录身份；合同细节见 §4）

写法：`名称（E）` 为池内怪；保证／剧情类写明来源。裁决标记：无标记＝READY；`[N]`＝NEEDS；`[K]`＝KEEP。已收录身份不再列出。

### 3.1 Trollmire（`trollmire`）
- 等级 1–7，3 层（`zone.lua`），`nb_npc`≈25／层，`max_ood=2`，布局 FLOODED / DEFAULT；guardian：TROLL_PROX、TROLL_SHAX。
- 载入的通用文件（`trollmire/npcs.lua`）：rodent[rarity(5)]，vermin[rarity(2)]，canine[rarity(0)]，troll[rarity(0)]，snake[rarity(3)]，plant[rarity(0)]，swarm[rarity(3)]，bear[rarity(2)]，all[rarity(4, 35)]，bear[rarity(5)]，aquatic_critter[fn]。
- 说明：FLOODED 布局排除 squid／ink squid（`trollmire/npcs.lua:38-39`）。
- 保证／剧情／后备（未收录）：
  - **Aluin the Fallen**（ALUIN，后备守关(回访)）：Shax/Prox 死亡时 activateBackupGuardian("ALUIN",2,35)（trollmire/npcs.lua:107,173）；GameState.lua:119-131 只登记，:144-159 仅在 is_advanced（已东行）时于第 2 层生成并把区域基准等级抬到 35。
- 稀有池（0.3≤E<1.5）：white ooze（0.3）。
- 统计：遇到 55／已收录 53／READY 2／NEEDS 0／KEEP 0；池覆盖 99%；尾部 18 个 ΣE≈1.5。

### 3.2 Old Forest（`old-forest`）
- 等级 7–16，4 层（`zone.lua`），`nb_npc`≈25／层，布局 CRYSTALINE / DEFAULT；guardian：SHARDSKIN、WRATHROOT。
- 载入的通用文件（`old-forest/npcs.lua`）：bear[rarity(1)]，vermin[rarity(3)]，canine[rarity(0)]，snake[rarity(0)]，swarm[rarity(1)]，plant[rarity(0)]，ant[rarity(2)]，all[rarity(4, 35)]，crystal[rarity(0)]。
- 保证／剧情／后备（未收录）：
  - **Shardskin**（SHARDSKIN，保证首领(CRYSTALINE 布局)）：old-forest/zone.lua:59 `guardian = is_crystaline and "SHARDSKIN" or "WRATHROOT"`；布局 alternateZone(...,{"CRYSTALINE",2}) (zone.lua:20-21)。
- 偶见池（1.5≤E<6）：black crystal（4.1）、giant green ant（2.7）、giant red ant（2.7）、cave bear（2.0）、war bear（2.0）、blue crystal（2.0）、multi-hued crystal[K]（1.8）。
- 稀有池（0.3≤E<1.5）：grizzly bear（1.4）、shimmering crystal[K]（1.4）、polar bear（0.9）、giant fire ant（0.4）、giant ice ant（0.4）、giant lightning ant（0.4）、giant acid ant（0.4）、cute little bunny（0.0）。
- 统计：遇到 49／已收录 33／READY 14／NEEDS 0／KEEP 2；池覆盖 81%；尾部 113 个 ΣE≈5.5。

### 3.3 Slazish Fens（`slazish-fen`）
- 等级 1–7，3 层（`zone.lua`），`nb_npc`≈8.5／层，`max_ood=2`。
- 载入的通用文件（`slazish-fen/npcs.lua`）：rodent[rarity(5)]，vermin[rarity(2)]，canine[rarity(0)]，troll[rarity(0)]，snake[rarity(3)]，plant[rarity(0)]，swarm[rarity(3)]，bear[rarity(2)]，all[rarity(4, 35)]。
- 说明：本区没有 `load()`，池只有 naga tidewarden／tidecaller（已收录）与 naga nereid；末层 Lady Zoisla 已收录。
- 常见池（E≥6）：naga nereid（8.5）。
- 统计：遇到 4／已收录 3／READY 1／NEEDS 0／KEEP 0；池覆盖 69%；尾部 0 个 ΣE≈0.0。

### 3.4 Rhaloren Camp（`rhaloren-camp`）
- 等级 1–7，3 层（`zone.lua`），`nb_npc`≈25／层，`max_ood=2`，布局 OVERGROUND / DEFAULT。
- 载入的通用文件（`rhaloren-camp/npcs.lua`）：rodent[rarity(5)]，vermin[rarity(5)]，molds[rarity(5)]，elven-warrior[rarity(0)]，elven-caster[rarity(0)]，all[rarity(4, 35)]。
- 说明：末层静态图另放 Rhaloren Inquisitor（已收录）与 `faction=="rhalore"` 的随机怪（`maps/zones/rhaloren-camp-last.lua:24-25`）。
- 常见池（E≥6）：elven guard（17.0）、mean looking elven guard（13.1）、elven mage（6.6）、elven tempest（6.6）。
- 稀有池（0.3≤E<1.5）：white ooze（0.4）。
- 统计：遇到 48／已收录 43／READY 5／NEEDS 0／KEEP 0；池覆盖 50%；尾部 18 个 ΣE≈1.1。

### 3.5 Dreadfell（`dreadfell`）
- 等级 15–26，9 层（`zone.lua`），`nb_npc`≈25／层；guardian：THE_MASTER。
- 载入的通用文件（`dreadfell/npcs.lua`）：skeleton[rarity(0)]，ghoul[rarity(1)]，wight[rarity(3)]，vampire[rarity(3)]，ghost[rarity(3)]，all[rarity(4, 35)]，bone-giant[fn]。
- 首领召唤／护卫：The Master 召唤 undead×2（dreadfell/npcs.lua:63，取本区 undead 池）；Pale Drake 召唤 bone giant×2（:164，`special_rarity="bonegiant_rarity"`），因此 `bone giant`（undead/giant，`general/npcs/bone-giant.lua:59`）在本区只经这条召唤路径出现。
- 保证／剧情／后备（未收录）：
  - **Borfast the Broken**（BORFAST，稀有唯一(池 rarity 50)）：dreadfell/npcs.lua:210 起，`rarity=50, level_range 20+`。
- 常见池（E≥6）：ghoul（15.4）、skeleton magus（10.3）、ghast（7.7）、forest wight（7.7）、lesser vampire（7.7）、vampire（7.7）、master vampire（7.7）、grave wight（6.4）。
- 偶见池（1.5≤E<6）：ghoulking（4.4）、elder vampire（4.1）、banshee（2.8）、skeleton assassin（2.1）。
- 稀有池（0.3≤E<1.5）：barrow wight（1.3）、dread（1.3）、giant green ant（0.8）、giant red ant（0.8）、giant fire ant（0.8）、giant ice ant（0.8）、giant lightning ant（0.8）、giant acid ant（0.8）、giant army ant（0.8）、cold drake hatchling（0.8）、fire drake hatchling（0.8）、bloated horror（0.8）、dredgling（0.8）、wretchling（0.8）、onilug（0.8）、quasit（0.8）、minotaur（0.8）、multi-hued drake hatchling（0.8）、orc warrior（0.8）、snow giant（0.8）、giant spider（0.8）、spitting spider（0.8）、chitinous spider（0.8）、storm drake hatchling（0.8）、venom drake hatchling（0.8）、umber hulk（0.8）、xorn（0.8）、white ooze（0.8）、Aletta Soultorn（0.6）、Filio Flightfond（0.6）、slimy ooze（0.4）、poison ooze（0.4）、orc necromancer（0.4）、luminous horror（0.4）、devourer（0.4）、blade horror（0.4）、dredge（0.4）、orc soldier（0.4）、gigantic sandworm tunneler（0.4）、weaver young（0.4）、vampire lord（0.3）。
- 统计：遇到 106／已收录 52／READY 54／NEEDS 0／KEEP 0；池覆盖 50%；尾部 93 个 ΣE≈10.4。

### 3.6 Norgos Lair（`norgos-lair`）
- 等级 1–7，3 层（`zone.lua`），`nb_npc`≈25／层，`max_ood=2`，布局 INVADED / DEFAULT；guardian：FROZEN_NORGOS、NORGOS。
- 载入的通用文件（`norgos-lair/npcs.lua`）：bear[rarity(0)]，vermin[rarity(3)]，canine[rarity(1)]，snake[rarity(0)]，plant[rarity(0)]，all[rarity(4, 35)]，shivgoroth[fn]。
- 稀有池（0.3≤E<1.5）：ultimate shivgoroth（0.7）、cave bear（0.4）、war bear（0.4）、white ooze（0.4）。
- 统计：遇到 45／已收录 41／READY 4／NEEDS 0／KEEP 0；池覆盖 98%；尾部 16 个 ΣE≈0.7。

### 3.7 Daikara（`daikara`）
- 等级 7–16，4 层（`zone.lua`），`nb_npc`≈25／层，布局 VOLCANO / DEFAULT；guardian：RANTHA_THE_WORM、VARSHA_THE_WRITHING。
- 载入的通用文件（`daikara/npcs.lua`）：xorn[rarity(4)]，snow-giant[rarity(0)]，canine[rarity(2)]，cold-drake[rarity(2)]，fire-drake[rarity(2)]，faeros[rarity(0)]，all[rarity(4, 35)]。
- 常见池（E≥6）：snow giant（26.4）、fire drake hatchling（11.1）、cold drake hatchling（7.5）。
- 偶见池（1.5≤E<6）：umber hulk（5.3）、snow giant thunderer（3.3）、fire drake（2.0）、cold drake（1.5）。
- 稀有池（0.3≤E<1.5）：snow giant boulder thrower（1.5）、faeros（1.2）、giant green ant（1.1）、giant red ant（1.1）、ghoul（1.1）、white ooze（1.1）、giant spider（1.1）、spitting spider（1.1）、xorn（0.9）、storm drake hatchling（0.9）、venom drake hatchling（0.9）、bloated horror（0.7）、dredgling（0.7）、onilug（0.7）、minotaur（0.7）、orc warrior（0.7）、lesser vampire（0.7）、xaren（0.6）、snow giant chieftain（0.6）、gigantic sandworm tunneler（0.6）、weaver young（0.6）、chitinous spider（0.6）、cave bear（0.4）、war bear（0.4）、gigantic corrosive tunneler（0.4）、devourer（0.4）、orc soldier（0.4）。
- 统计：遇到 89／已收录 55／READY 34／NEEDS 0／KEEP 0；池覆盖 50%；尾部 91 个 ΣE≈5.2。

### 3.8 The Maze（`maze`）
- 等级 7–16，3 层（`zone.lua`），`nb_npc`≈45／层，布局 COLLAPSED / DEFAULT；guardian：HORNED_HORROR、MINOTAUR_MAZE。
- 载入的通用文件（`maze/npcs.lua`）：vermin[rarity(5)]，rodent[rarity(5)]，canine[rarity(6)]，snake[rarity(4)]，ooze[rarity(3)]，jelly[rarity(3)]，ant[rarity(4)]，thieve[rarity(0)]，minotaur[rarity(0)]，all[rarity(4, 35)]，horror-corrupted[rarity(0)]，horror_temporal[rarity(1)]。
- 说明：COLLAPSED 布局守关 HORNED_HORROR、DEFAULT 布局守关 MINOTAUR_MAZE（均已收录）。
- 保证／剧情／后备（未收录）：
  - **Nimisil**（NIMISIL，后备守关(回访)）：maze/npcs.lua:93,146 activateBackupGuardian("NIMISIL",2,40)，仅东行后再入第 2 层。
- 常见池（E≥6）：drem（10.3）、minotaur（10.3）。
- 偶见池（1.5≤E<6）：brecklorn（5.2）、grannor'vor（5.2）、dredgling（4.7）、drem master（3.4）、white ooze（2.9）、assassin（2.6）、grannor'vin（2.6）、giant green ant（2.3）、giant red ant（2.3）、bandit lord（2.1）、rogue sapper（1.6）。
- 稀有池（0.3≤E<1.5）：shadowblade（0.5）、dredge（0.4）、ghoul（0.3）、giant spider（0.3）、spitting spider（0.3）。
- 统计：遇到 78／已收录 59／READY 19／NEEDS 0／KEEP 0；池覆盖 67%；尾部 108 个 ΣE≈6.9。

### 3.9 Heart of the Gloom（`heart-gloom`）
- 等级 1–7，3 层（`zone.lua`），`nb_npc`≈25／层，`max_ood=2`，布局 PURIFIED / DEFAULT；guardian：DREAMING_ONE、WITHERING_THING。
- 载入的通用文件（`heart-gloom/npcs.lua`）：rodent[alter(0)]，bear[alter(3)]，canine[alter(1)]，plant[alter(0)]，all[rarity(4, 35)]。
- 说明：`alter()` 给所有带 rarity 的通用怪加前缀（`heart-gloom/npcs.lua:24-50`），详见 §6。
- 保证／剧情／后备（未收录）：
  - **The Withering Thing**（WITHERING_THING，保证首领(非净化布局)）：heart-gloom/zone.lua:78 `guardian = is_purified and "DREAMING_ONE" or "WITHERING_THING"`。
  - **The Dreaming One**（DREAMING_ONE，保证首领(净化布局)）：同上 zone.lua:78。
- 稀有池（0.3≤E<1.5）：cave bear（0.4）、war bear（0.4）。
- 统计：遇到 22／已收录 18／READY 4／NEEDS 0／KEEP 0；池覆盖 99%；尾部 0 个 ΣE≈0.0。

### 3.10 Sandworm lair（`sandworm-lair`）
- 等级 7–16，3 层（`zone.lua`），`nb_npc`≈40／层，布局 BIGWORM / DEFAULT；guardian：SANDWORM_QUEEN。
- 载入的通用文件（`sandworm-lair/npcs.lua`）：vermin[rarity(7)]，ooze[rarity(5)]，jelly[rarity(7)]，sandworm[rarity(0)]，all[rarity(4, 35)]。
- 说明：`Sandworm` 生成器；BIGWORM 布局只有 2 层但 `nb_npc={70,80}`，本表 E 按 3 层×40 折中。
- 首领召唤／护卫：Sandworm Queen 召唤 vermin/sandworm×4（sandworm-lair/npcs.lua:122-124）。
- 保证／剧情／后备（未收录）：
  - **huge sandworm burrower**[K]（SANDWORM_TUNNELER_HUGE，脚本引路体）：sandworm-lair/zone.lua:185,200 由脚本生成，L1 每 ≥800 回合再生成（zone.lua:191-206）。
- 常见池（E≥6）：gigantic sandworm tunneler（13.1）、gigantic corrosive tunneler（8.7）。
- 偶见池（1.5≤E<6）：sand-drake（5.2）、gigantic gravity worm（5.2）、white ooze（4.4）。
- 统计：遇到 25／已收录 19／READY 5／NEEDS 0／KEEP 1；池覆盖 70%；尾部 4 个 ΣE≈0.4。

### 3.11 Ritches Tunnels（`ritch-tunnels`）
- 等级 1–7，3 层（`zone.lua`），`nb_npc`≈25／层，`max_ood=2`；guardian：HIVE_MOTHER。
- 载入的通用文件（`ritch-tunnels/npcs.lua`）：ritch[rarity(0)]，vermin[rarity(0)]，ant[rarity(2)]，jelly[rarity(3)]。
- 首领召唤／护卫：Ritch Great Hive Mother 召唤 insect/ritch×1（ritch-tunnels/npcs.lua:137-139），来自本区三种 ritch。
- 常见池（E≥6）：ritch flamespitter（11.3）、chitinous ritch（11.3）、ritch impaler（9.1）。
- 偶见池（1.5≤E<6）：giant green ant（2.3）、giant red ant（2.3）。
- 统计：遇到 20／已收录 15／READY 5／NEEDS 0／KEEP 0；池覆盖 58%；尾部 0 个 ΣE≈0.0。

### 3.12 The Deep Bellow（`deep-bellow`）
- 等级 1–7，3 层（`zone.lua`），`nb_npc`≈25／层，`max_ood=2`。
- 载入的通用文件（`deep-bellow/npcs.lua`）：rodent[rarity(5)]，horror-corrupted[rarity(0)]，all[rarity(4, 35)]。
- 首领召唤／护卫：The Mouth 的召唤物 slimy crawler 已收录。
- 常见池（E≥6）：drem（16.6）、brecklorn（8.3）、grannor'vor（6.8）。
- 偶见池（1.5≤E<6）：drem master（4.5）、grannor'vin（3.4）。
- 稀有池（0.3≤E<1.5）：white ooze（0.4）。
- 统计：遇到 49／已收录 43／READY 6／NEEDS 0／KEEP 0；池覆盖 54%；尾部 18 个 ΣE≈1.2。

### 3.13 Last Hope Graveyard（`last-hope-graveyard`）
- 等级 15–25，2 层（`zone.lua`），`nb_npc`≈0／层。
- 载入的通用文件（`last-hope-graveyard/npcs.lua`）：skeleton，ghoul，vampire，bone-giant，lich。
- 说明：`nb_npc={0,0}`，怪物只来自棺材机制：`zone.lua:100,165` 以 `properties={"undead"}` 现抽随机首领，不产生固定身份；Celia 已收录。
- 本区在阈值内没有未收录身份。
- 统计：遇到 1／已收录 1／READY 0／NEEDS 0／KEEP 0；池覆盖 —；尾部 0 个 ΣE≈0.0。

### 3.14 Scintillating Caves（`scintillating-caves`）
- 等级 1–7，4 层（`zone.lua`），`nb_npc`≈19／层，`max_ood=2`，布局 TWISTED / DEFAULT；guardian：SPELLBLAZE_CRYSTAL。
- 载入的通用文件（`scintillating-caves/npcs.lua`）：rodent[rarity(5)]，vermin[rarity(2)]，snake[rarity(3)]，bear[rarity(2)]，crystal[rarity(1)]，all[rarity(4, 35)]。
- 偶见池（1.5≤E<6）：black crystal（4.4）、blue crystal（2.6）。
- 稀有池（0.3≤E<1.5）：cave bear（1.0）、war bear（1.0）、white ooze（0.4）。
- 统计：遇到 53／已收录 48／READY 5／NEEDS 0／KEEP 0；池覆盖 88%；尾部 16 个 ΣE≈1.5。

### 3.15 Unremarkable Cave（`unremarkable-cave`）
- 等级 25–35，1 层（`zone.lua`），`nb_npc`≈55／层。
- 载入的通用文件（`unremarkable-cave/npcs.lua`）：rodent[rarity(0)]，vermin[rarity(0)]，molds[rarity(0)]，skeleton[rarity(0)]，snake[rarity(0)]，all[rarity(0, 10)]。
- 说明：`all.lua` 以 `rarity(0,10)` 载入（尾部比其他区厚约 4 倍）；Fillarel Aldaren、Krogar 已收录。
- 稀有池（0.3≤E<1.5）：skeleton magus（1.2）、carrion worm mass（0.9）、black mamba（0.9）、anaconda（0.7）、giant green ant（0.4）、giant red ant（0.4）、giant fire ant（0.4）、giant ice ant（0.4）、giant lightning ant（0.4）、giant acid ant（0.4）、giant army ant（0.4）、cold drake hatchling（0.4）、fire drake hatchling（0.4）、ghoul（0.4）、bloated horror（0.4）、dredgling（0.4）、wretchling（0.4）、onilug（0.4）、quasit（0.4）、dolleg（0.4）、dúathedlen（0.4）、minotaur（0.4）、multi-hued drake hatchling（0.4）、naga myrmidon（0.4）、slimy ooze（0.4）、poison ooze（0.4）、orc fighter（0.4）、orc summoner（0.4）、orc warrior（0.4）、orc necromancer（0.4）、snow giant（0.4）、giant spider（0.4）、spitting spider（0.4）、chitinous spider（0.4）、storm drake hatchling（0.4）、lesser vampire（0.4）、vampire（0.4）、master vampire（0.4）、elder vampire（0.4）、venom drake hatchling（0.4）、forest wight（0.4）、grave wight（0.4）、umber hulk（0.4）、xorn（0.4）、white ooze（0.3）。
- 统计：遇到 89／已收录 44／READY 45／NEEDS 0／KEEP 0；池覆盖 59%；尾部 105 个 ΣE≈7.0。

### 3.16 Unknown tunnels（`thieves-tunnels`）
- 等级 14–28，2 层（`zone.lua`），`nb_npc`≈6／层。
- 载入的通用文件（`thieves-tunnels/npcs.lua`）：thieve。
- 保证／剧情／后备（未收录）：
  - **Assassin Lord**（ASSASSIN_LORD，任务关(第 2 层静态图)）：thieves-tunnels/zone.lua:47-58 第 2 层 Static 图 quests/lost-merchant；maps/quests/lost-merchant.lua:27 摆放。
  - **Lost Merchant**（MERCHANT，任务关(友方)）：maps/quests/lost-merchant.lua:29 摆放；npcs.lua:113。
- 稀有池（0.3≤E<1.5）：assassin（0.9）、shadowblade（0.7）、bandit lord（0.5）、rogue sapper（0.5）。
- 统计：遇到 10／已收录 4／READY 6／NEEDS 0／KEEP 0；池覆盖 78%；尾部 0 个 ΣE≈0.0。

### 3.17 Tempest Peak（`tempest-peak`）
- 等级 15–22，2 层（`zone.lua`），`nb_npc`≈45／层；guardian：URKIS。
- 载入的通用文件（`tempest-peak/npcs.lua`）：gwelgoroth[rarity(0)]，xorn[rarity(2)]，snow-giant[rarity(0)]，storm-drake[rarity(1)]，all[rarity(4, 35)]。
- 常见池（E≥6）：gwelgoroth（12.8）、snow giant（12.8）、storm drake hatchling（6.4）。
- 偶见池（1.5≤E<6）：greater gwelgoroth（4.3）、umber hulk（4.3）、xorn（4.3）、snow giant thunderer（4.3）、snow giant boulder thrower（4.3）、storm drake（3.2）、ultimate gwelgoroth（2.6）、xaren（2.6）、snow giant chieftain（1.8）。
- 稀有池（0.3≤E<1.5）：giant green ant（0.3）、giant red ant（0.3）、giant fire ant（0.3）、giant ice ant（0.3）、giant lightning ant（0.3）、giant acid ant（0.3）、giant army ant（0.3）、cold drake hatchling（0.3）、fire drake hatchling（0.3）、ghoul（0.3）、bloated horror（0.3）、dredgling（0.3）、wretchling（0.3）、onilug（0.3）、minotaur（0.3）、multi-hued drake hatchling（0.3）、white ooze（0.3）、orc warrior（0.3）、giant spider（0.3）、spitting spider（0.3）、chitinous spider（0.3）、lesser vampire（0.3）、vampire（0.3）、venom drake hatchling（0.3）、forest wight（0.3）。
- 统计：遇到 77／已收录 40／READY 37／NEEDS 0／KEEP 0；池覆盖 17%；尾部 96 个 ΣE≈4.4。

### 3.18 Ruined halfling complex（`halfling-ruins`）
- 等级 10–25，4 层（`zone.lua`），`nb_npc`≈25／层。
- 载入的通用文件（`halfling-ruins/npcs.lua`）：skeleton[rarity(0)]，ghoul[rarity(2)]，bone-giant[rarity(8)]。
- 保证／剧情／后备（未收录）：
  - **Subject Z**（SUBJECT_Z，保证首领(末层静态图)）：halfling-ruins/zone.lua:87 末层图；maps/zones/halfling-ruins-last.lua:50。
  - **Yeek Wayist**（YEEK_WAYIST，剧情NPC(末层静态图)）：maps/zones/halfling-ruins-last.lua:51。
- 常见池（E≥6）：ghoul（8.5）、skeleton magus（7.8）。
- 偶见池（1.5≤E<6）：ghast（5.1）、ghoulking（2.9）。
- 稀有池（0.3≤E<1.5）：skeleton assassin（0.6）。
- 统计：遇到 14／已收录 7／READY 7／NEEDS 0／KEEP 0；池覆盖 77%；尾部 4 个 ΣE≈0.3。

### 3.19 Lost Dwarven Kingdom of Reknor（`reknor`）
- 等级 18–35，4 层（`zone.lua`），`nb_npc`≈55／层。
- 载入的通用文件（`reknor/npcs.lua`）：orc[rarity(0)]，troll[rarity(0)]，all[rarity(4, 35)]。
- 说明：末层静态图 `reknor-last.lua:30-34` 摆 GOLBUG（已收录）、ORC、ORC_FIRE_WYRMIC、ORC_ICE_WYRMIC 以及**不存在**的 `ORC_ARCHER`（见 §8）。
- 常见池（E≥6）：orc warrior（27.5）、orc soldier（13.7）、orc archer（9.2）、orc assassin（9.2）、mountain troll（9.2）、orc master assassin（6.9）。
- 偶见池（1.5≤E<6）：orc grand master assassin（5.5）、mountain troll thunderer（5.4）、fiery orc wyrmic（4.6）、icy orc wyrmic（4.6）。
- 稀有池（0.3≤E<1.5）：giant green ant（0.7）、giant red ant（0.7）、giant fire ant（0.7）、giant ice ant（0.7）、giant lightning ant（0.7）、giant acid ant（0.7）、giant army ant（0.7）、cold drake hatchling（0.7）、fire drake hatchling（0.7）、ghoul（0.7）、bloated horror（0.7）、dredgling（0.7）、wretchling（0.7）、onilug（0.7）、minotaur（0.7）、multi-hued drake hatchling（0.7）、white ooze（0.7）、snow giant（0.7）、giant spider（0.7）、spitting spider（0.7）、chitinous spider（0.7）、storm drake hatchling（0.7）、lesser vampire（0.7）、vampire（0.7）、venom drake hatchling（0.7）、forest wight（0.7）、umber hulk（0.7）、xorn（0.7）、quasit（0.7）、slimy ooze（0.7）、poison ooze（0.7）、orc necromancer（0.7）、master vampire（0.7）、elder vampire（0.7）、grave wight（0.7）、Forest Troll Hedge-Wizard（0.7）、devourer（0.4）、blade horror（0.4）、dredge（0.4）、gigantic sandworm tunneler（0.4）、weaver young（0.4）、luminous horror（0.4）、orc blood mage（0.3）。
- 统计：遇到 95／已收录 42／READY 53／NEEDS 0／KEEP 0；池覆盖 42%；尾部 91 个 ΣE≈10.3。

### 3.20 Escape from Reknor（`reknor-escape`）
- 等级 1–7，3 层（`zone.lua`），`nb_npc`≈55／层，`max_ood=2`。
- 载入的通用文件（`reknor-escape/npcs.lua`）：rodent[rarity(0)]，vermin[rarity(2)]，molds[rarity(1)]，orc[fn]，snake[rarity(2)]，all[rarity(4, 35)]。
- 说明：末层静态图摆 `ORC_GUARD`（不存在，见 §8）与 BROTOQ（已收录）。
- 常见池（E≥6）：orc warrior（18.0）、orc soldier（9.0）。
- 偶见池（1.5≤E<6）：orc archer（6.0）。
- 稀有池（0.3≤E<1.5）：white ooze（0.5）、giant green ant（0.4）、giant red ant（0.4）、giant spider（0.4）。
- 统计：遇到 56／已收录 49／READY 7／NEEDS 0／KEEP 0；池覆盖 82%；尾部 15 个 ΣE≈0.5。

### 3.21 Lake of Nur（`lake-nur`）
- 等级 15–25，3 层（`zone.lua`），`nb_npc`≈22／层，布局 FLOODED / DRY。
- 载入的通用文件（`lake-nur/npcs.lua`）：aquatic_critter[fn]，aquatic_demon[fn]，horror_aquatic[fn]，horror[rarity(0)]，snake[rarity(3)]，plant[rarity(3)]。
- 说明：第 1 层静态无怪；第 2 层只抽 `water_rarity`；第 3 层 FLOODED 布局抽 `water_rarity`／`horror_water_rarity`，DRY 布局走常规池（`lake-nur/zone.lua:86-112`：第 2 层 `filters` 在 :95，第 3 层在 :111-112）。E 已按此拆算，FLOODED/DRY 各 0.5。
- 常见池（E≥6）：squid（7.7）、water imp（7.7）。
- 偶见池（1.5≤E<6）：ink squid（3.9）、bloated horror（2.5）、swarming horror（2.2）、ravenous horror（2.2）。
- 稀有池（0.3≤E<1.5）：entrenched horror（1.5）、devourer（1.3）、blade horror（1.3）、luminous horror（1.1）、boiling horror（1.1）、swarm hive（0.7）、abyssal horror（0.4）、oozing horror（0.4）、black mamba（0.4）、umbral horror（0.3）。
- 统计：遇到 29／已收录 13／READY 16／NEEDS 0／KEEP 0；池覆盖 32%；尾部 13 个 ΣE≈0.8。

### 3.22 Ruined Dungeon（`ruined-dungeon`）
- 等级 10–30，1 层（`zone.lua`），`nb_npc`≈60／层，布局 ALT1（clues_layout）。
- 载入的通用文件（`ruined-dungeon/npcs.lua`）：all，bone-giant，faeros，gwelgoroth，mummy，ritch。
- 说明：池是「全部通用怪」（`all.lua` 不加 rarity 乘数再加 bone-giant/faeros/gwelgoroth/mummy/ritch），单个身份 E 都很低；守关／惩罚怪是程序化 random_elite（`ruined-dungeon/zone.lua:82-92`）。
- 稀有池（0.3≤E<1.5）：giant green ant（0.8）、giant red ant（0.8）、cold drake hatchling（0.8）、fire drake hatchling（0.8）、ghoul（0.8）、bloated horror（0.8）、dredgling（0.8）、onilug（0.8）、minotaur（0.8）、white ooze（0.8）、orc warrior（0.8）、snow giant（0.8）、giant spider（0.8）、spitting spider（0.8）、storm drake hatchling（0.8）、lesser vampire（0.8）、venom drake hatchling（0.8）、umber hulk（0.8）、gwelgoroth（0.8）、giant fire ant（0.7）、giant ice ant（0.7）、giant lightning ant（0.7）、giant acid ant（0.7）、giant army ant（0.7）、wretchling（0.7）、quasit（0.7）、multi-hued drake hatchling（0.7）、chitinous spider（0.7）、vampire（0.7）、master vampire（0.7）、forest wight（0.7）、xorn（0.7）、faeros（0.7）、devourer（0.4）、orc soldier（0.4）、gigantic sandworm tunneler（0.4）、weaver young（0.4）、luminous horror（0.3）、blade horror（0.3）、dredge（0.3）。
- 统计：遇到 85／已收录 45／READY 40／NEEDS 0／KEEP 0；池覆盖 51%；尾部 129 个 ΣE≈9.0。

### 3.23 Blighted Ruins（`blighted-ruins`）
- 等级 1–7，3 层（`zone.lua`），`nb_npc`≈25／层，`max_ood=2`；guardian：HALF_BONE_GIANT。
- 载入的通用文件（`blighted-ruins/npcs.lua`）：rodent[rarity(1)]，vermin[rarity(2)]，ghoul[rarity(3)]，skeleton[rarity(1)]，bone-giant[fn]，horror-undead[fn]。
- 稀有池（0.3≤E<1.5）：ghoul（0.5）。
- 统计：遇到 20／已收录 19／READY 1／NEEDS 0／KEEP 0；池覆盖 99%；尾部 0 个 ΣE≈0.0。

### 3.24 Dark crypt（`crypt-kryl-feijan`）
- 等级 25–35，5 层（`zone.lua`），`nb_npc`≈20／层。
- 载入的通用文件（`crypt-kryl-feijan/npcs.lua`）：elven-caster[rarity(0)]，elven-warrior[rarity(0)]，minor-demon[rarity(5)]，major-demon[fn]，ogre[fn]。
- 保证／剧情／后备（未收录）：
  - **Melinda**[K]（MELINDA，任务NPC(末层)）：maps/zones/crypt-kryl-feijan-last.lua:27。
- 常见池（E≥6）：elven cultist（12.7）、elven blood mage（12.7）、elven guard（12.7）、mean looking elven guard（12.7）、elven warrior（12.7）、elven mage（6.3）、elven tempest（6.3）。
- 偶见池（1.5≤E<6）：elven corruptor（4.2）、elven elite warrior（2.5）、wretchling（2.1）、onilug（2.1）、quasit（2.1）、ogre guard（2.1）、ogre mauler（2.1）、ogre rune-spinner（2.1）、ogre pounder（1.8）、fire imp（1.6）、ogre warmaster（1.6）。
- 统计：遇到 21／已收录 2／READY 18／NEEDS 0／KEEP 1；池覆盖 0%；尾部 0 个 ΣE≈0.0。

### 3.25 Golem Graveyard（`golem-graveyard`）
- 等级 14–20，1 层（`zone.lua`），`nb_npc`≈7／层。
- 载入的通用文件（`golem-graveyard/npcs.lua`）：construct。
- 偶见池（1.5≤E<6）：broken golem（3.1）、golem（3.1）。
- 稀有池（0.3≤E<1.5）：alchemist golem（0.8）。
- 统计：遇到 4／已收录 1／READY 3／NEEDS 0／KEEP 0；池覆盖 0%；尾部 0 个 ΣE≈0.0。

### 3.26 Ardhungol（`ardhungol`）
- 等级 25–32，3 层（`zone.lua`），`nb_npc`≈75／层；guardian：UNGOLE。
- 载入的通用文件（`ardhungol/npcs.lua`）：spider[rarity(0)]，all[rarity(4, 35)]。
- 首领召唤／护卫：Ungolë 护卫 spiderkin/spider×2（ardhungol/npcs.lua:89-91）、召唤 spiderkin/spider×3（:92-94）。
- 常见池（E≥6）：giant spider（35.2）、spitting spider（35.2）、chitinous spider（35.2）、weaver young（17.6）、gaeramarth（10.9）、ninurlhing（10.9）、faerlhing（8.2）、losselhing（8.2）。
- 偶见池（1.5≤E<6）：weaver patriarch（2.7）。
- 稀有池（0.3≤E<1.5）：giant green ant（0.9）、giant red ant（0.9）、giant fire ant（0.9）、giant ice ant（0.9）、giant lightning ant（0.9）、giant acid ant（0.9）、giant army ant（0.9）、cold drake hatchling（0.9）、fire drake hatchling（0.9）、ghoul（0.9）、bloated horror（0.9）、dredgling（0.9）、wretchling（0.9）、onilug（0.9）、quasit（0.9）、minotaur（0.9）、multi-hued drake hatchling（0.9）、slimy ooze（0.9）、poison ooze（0.9）、orc warrior（0.9）、orc necromancer（0.9）、snow giant（0.9）、storm drake hatchling（0.9）、lesser vampire（0.9）、vampire（0.9）、master vampire（0.9）、elder vampire（0.9）、venom drake hatchling（0.9）、forest wight（0.9）、grave wight（0.9）、umber hulk（0.9）、xorn（0.9）、white ooze（0.8）、luminous horror（0.5）、devourer（0.5）、blade horror（0.5）、dredge（0.5）、orc soldier（0.5）、gigantic sandworm tunneler（0.5）、orc blood mage（0.4）、barrow wight（0.4）、dolleg（0.4）、dúathedlen（0.4）、naga myrmidon（0.4）、orc fighter（0.4）、orc summoner（0.4）、cave bear（0.3）、war bear（0.3）、cold drake（0.3）、fire drake（0.3）、ghast（0.3）、temporal stalker（0.3）、fire imp（0.3）、multi-hued drake（0.3）、orc archer（0.3）、orc assassin（0.3）、gigantic corrosive tunneler（0.3）、skeleton magus（0.3）、snow giant thunderer（0.3）、snow giant boulder thrower（0.3）、storm drake（0.3）、assassin（0.3）、mountain troll（0.3）、venom drake（0.3）、xaren（0.3）、ungolmor（0.3）。
- 统计：遇到 122／已收录 47／READY 75／NEEDS 0／KEEP 0；池覆盖 14%；尾部 70 个 ΣE≈7.4。

### 3.27 Mark of the Spellblaze（`mark-spellblaze`）
- 等级 15–25，2 层（`zone.lua`），`nb_npc`≈25／层。
- 载入的通用文件（`mark-spellblaze/npcs.lua`）：rodent[rarity(5)]，vermin[rarity(5)]，faeros[rarity(2)]，gwelgoroth[rarity(2)]，elven-caster[rarity(2)]，all[rarity(4, 65)]。
- 保证／剧情／后备（未收录）：
  - **Grand Corruptor**（GRAND_CORRUPTOR，保证首领(末层静态图)）：maps/zones/mark-spellblaze-last.lua:43；quests/anti-antimagic.lua:78 亦可生成。
- 常见池（E≥6）：gwelgoroth（10.1）、faeros（9.1）、elven mage（7.6）、elven tempest（7.6）、greater gwelgoroth（6.1）。
- 偶见池（1.5≤E<6）：ultimate gwelgoroth（4.3）、carrion worm mass（3.0）。
- 稀有池（0.3≤E<1.5）：elven cultist（0.7）、elven blood mage（0.7）、greater faeros（0.4）、elven corruptor（0.3）。
- 统计：遇到 21／已收录 9／READY 12／NEEDS 0／KEEP 0；池覆盖 20%；尾部 1 个 ΣE≈0.1。

### 3.28 Unhallowed Morass（`unhallowed-morass`）
- 等级 1–7，3 层（`zone.lua`），`nb_npc`≈25／层，`max_ood=2`；guardian：WEAVER_QUEEN。
- 首领召唤／护卫：Weaver Queen 召唤 weaver hatchling×1（unhallowed-morass/npcs.lua:142）；weaver hatchling 自带 hatchling 护卫×2（:49-51），orb spinner 自带 orb weaver×1（:68-70）。
- 保证／剧情／后备（未收录）：
  - **Weaver Queen**（WEAVER_QUEEN，保证首领）：unhallowed-morass/zone.lua:52 guardian；自带护卫 make_escort weaver hatchling×2（npcs.lua:49-51）。
- 常见池（E≥6）：weaver hatchling（30.9）、orb spinner（30.9）、fate spinner（12.8）、fate weaver（8.5）。
- 偶见池（1.5≤E<6）：orb weaver（2.6）。
- 统计：遇到 6／已收录 0／READY 6／NEEDS 0／KEEP 0；池覆盖 0%；尾部 0 个 ΣE≈0.0。

### 3.29 Abashed Expanse（`abashed-expanse`）
- 等级 1–7，3 层（`zone.lua`），`nb_npc`≈20／层，`max_ood=2`；guardian：SPACIAL_DISTURBANCE。
- 载入的通用文件（`abashed-expanse/npcs.lua`）：rodent[rarity(5)]，vermin[rarity(2)]，snake[rarity(3)]，bear[rarity(2)]，crystal[rarity(10)]，losgoroth[rarity(1)]，all[rarity(4, 35)]。
- 保证／剧情／后备（未收录）：
  - **Spacial Disturbance**[K]（SPACIAL_DISTURBANCE，保证首领）：abashed-expanse/zone.lua:56 guardian。
- 常见池（E≥6）：losgoroth（43.8）、manaworm（20.0）。
- 统计：遇到 3／已收录 0／READY 2／NEEDS 0／KEEP 1；池覆盖 0%；尾部 0 个 ΣE≈0.0。

### 3.30 Temporal Rift（`temporal-rift`）
- 等级 16–30，4 层（`zone.lua`），`nb_npc`≈20／层。
- 载入的通用文件（`temporal-rift/npcs.lua`）：telugoroth[rarity(0)]，horror_temporal[rarity(0)]。
- 说明：第 1 层仅 elemental/temporal（telugoroth 系），第 2 层 3 只 horror/temporal，第 3 层 horror/temporal，第 4 层无随机怪（`temporal-rift/zone.lua:61,74,95`，第 4 层 `nb_npc={0,0}`）。
- 保证／剧情／后备（未收录）：
  - **Ben Cruthdar, the Abomination**（BEN_CRUTHDAR_ABOMINATION，保证首领(第 2 层首次进入)）：temporal-rift/zone.lua:143 generateGuardian。
  - **Rantha the Abomination**（ABOMINATION_RANTHA，保证首领(第 3 层首次进入)）：temporal-rift/zone.lua:147 generateGuardian。
  - **Chronolith Twin**（CHRONOLITH_TWIN，保证首领(第 4 层，与 CLONE 成对)）：temporal-rift/zone.lua:152-155 固定坐标 (26,8)/(29,8)。
  - **Chronolith Clone**（CHRONOLITH_CLONE，保证首领(第 4 层，与 TWIN 成对)）：temporal-rift/zone.lua:154-155。
- 常见池（E≥6）：dredgling（12.3）、telugoroth（7.4）、dredge（6.1）。
- 偶见池（1.5≤E<6）：greater telugoroth（3.7）、teluvorta（3.7）、temporal stalker（2.9）、ultimate telugoroth（2.5）、greater teluvorta（2.5）、void horror（2.2）、dredge captain（1.8）、ultimate teluvorta（1.7）。
- 统计：遇到 15／已收录 0／READY 15／NEEDS 0／KEEP 0；池覆盖 0%；尾部 0 个 ΣE≈0.0。

### 3.31 Murgol Lair（`murgol-lair`）
- 等级 1–7，3 层（`zone.lua`），`nb_npc`≈25／层，`max_ood=2`，布局 INVASION / DEFAULT；guardian：MURGOL、NASHVA。
- 载入的通用文件（`murgol-lair/npcs.lua`）：yaech[fn]，aquatic_critter[fn]。
- 保证／剧情／后备（未收录）：
  - **Murgol, the Yaech Lord**（MURGOL，保证首领(非 INVASION 布局)）：murgol-lair/zone.lua:58 `guardian = is_invaded and "NASHVA" or "MURGOL"`。
  - **Lady Nashva the Streambender**（NASHVA，保证首领(INVASION 布局)）：同上 zone.lua:58；该实体仅在 is_invaded 时定义（murgol-lair/npcs.lua:76 起）。
- 常见池（E≥6）：yaech diver（15.0）、squid（15.0）、naga nereid（9.1）、yaech hunter（7.5）、ink squid（7.5）、yaech mindslayer（7.1）。
- 偶见池（1.5≤E<6）：yaech psion（4.7）。
- 统计：遇到 14／已收录 5／READY 9／NEEDS 0／KEEP 0；池覆盖 38%；尾部 0 个 ΣE≈0.0。

### 3.32 Southern Beach（`south-beach`）
- 等级 24–35，1 层（`zone.lua`），`nb_npc`≈0／层。
- 载入的通用文件（`south-beach/npcs.lua`）：yaech。
- 说明：`nb_npc={0,0}`；只有任务 Melinda 与按 `humanoid/yaech` 现抽的 yaech（`zone.lua:110,131`）。
- 保证／剧情／后备（未收录）：
  - **Melinda**[K]（MELINDA_BEACH，任务NPC）：south-beach/zone.lua:87 makeEntityByName。
- 统计：遇到 1／已收录 0／READY 0／NEEDS 0／KEEP 1；池覆盖 —；尾部 0 个 ΣE≈0.0。

### 3.33 Tranquil Meadow（`keepsake-meadow`）
- 等级 15–25，6 层（`zone.lua`），`nb_npc`≈25／层。
- 载入的通用文件（`keepsake-meadow/npcs.lua`）：canine[rarity(0)]。
- 说明：只有第 4、5 层是随机洞穴层（`cave_rarity` 过滤见 `keepsake-meadow/zone.lua:32`；第 1、2、3、6 层在 `:47-108` 里是 Static 图且 `nb_npc={0,0}`）。
- 保证／剧情／后备（未收录）：
  - **Kyless**（KYLESS，保证首领(末层静态图)）：maps/zones/keepsake-cave-last.lua:36。
  - **Berethh**（BERETHH，任务同伴）：quests/keepsake.lua:238。
  - **caravan merchant**（CARAVAN_MERCHANT，剧情NPC(梦境层静态图)）：maps/zones/keepsake-dream.lua:32。
  - **caravan guard**（CARAVAN_GUARD，剧情NPC(梦境层静态图)）：maps/zones/keepsake-dream.lua:33。
  - **caravan porter**（CARAVAN_PORTER，剧情NPC(梦境层静态图)）：maps/zones/keepsake-dream.lua:34。
  - **Companion Warrior**（BERETHH_WARRIOR，任务同伴）：quests/keepsake.lua:296。
  - **Companion Archer**（BERETHH_ARCHER，任务同伴）：quests/keepsake.lua:302。
  - **war dog**（WAR_DOG，洞穴入口/末层静态摆放）：maps/zones/keepsake-cave-entrance.lua:33 起为 CORRUPTED_WAR_DOG；WAR_DOG 自身无 rarity，仅脚本引用。
- 常见池（E≥6）：corrupted war dog（12.5）、shadow claw[N]（12.5）、shadow stalker（12.5）、shadow claw[N]（12.5）。
- 统计：遇到 12／已收录 0／READY 10／NEEDS 2／KEEP 0；池覆盖 0%；尾部 0 个 ΣE≈0.0。

### 3.34 Noxious Caldera（`noxious-caldera`）
- 等级 25–35，2 层（`zone.lua`），`nb_npc`≈40／层。
- 载入的通用文件（`noxious-caldera/npcs.lua`）：bear[rarity(0)]，vermin[rarity(3)]，canine[rarity(1)]，snake[rarity(0)]，plant[rarity(0)]，venom-drake[rarity(0)]，faeros[rarity(0)]，all[rarity(4, 35)]。
- 保证／剧情／后备（未收录）：
  - **Mindworm**（MINDWORM，保证首领(第 2 层)）：noxious-caldera/zone.lua:110 于第 2 层下楼梯附近生成。
- 偶见池（1.5≤E<6）：venom drake hatchling（5.4）、faeros（5.4）、cave bear（1.8）、war bear（1.8）、venom drake（1.8）、greater faeros（1.8）。
- 稀有池（0.3≤E<1.5）：grizzly bear（1.4）、black mamba（1.4）、anaconda（1.1）、venom wyrm（1.1）、polar bear（0.9）、carrion worm mass（0.8）。
- 统计：遇到 30／已收录 17／READY 13／NEEDS 0／KEEP 0；池覆盖 61%；尾部 137 个 ΣE≈8.4。

### 3.35 Old Conclave Vault（`conclave-vault`）
- 等级 20–30，4 层（`zone.lua`），`nb_npc`≈13／层。
- 载入的通用文件（`conclave-vault/npcs.lua`）：jelly，ooze，mold，slime，ogre[switchRarity("special_rarity")]。
- 说明：房间生怪：六个小房各放 `vat_rarity` 池（`rooms/room1-6.lua`），boss 房放 Healer Astelrid 与 `special_rarity` 的 ogre（`rooms/boss.lua:40,48`）；`mold.lua`/`slime.lua` 两个文件在本版本不存在（`conclave-vault/npcs.lua:22-23`，无怪）。
- 保证／剧情／后备（未收录）：
  - **Healer Astelrid**（HEALER_ASTELRID，保证首领(boss 房)）：conclave-vault/rooms/boss.lua:40。
- 偶见池（1.5≤E<6）：slimy ooze（4.8）、poison ooze（4.8）、white ooze（4.1）。
- 稀有池（0.3≤E<1.5）：brittle clear ooze（0.5）、old vats[N]（0.0）、old vats[N]（0.0）、degenerated ogric mass（0.0）、ogric abomination（0.0）、ogre sentry[N]（0.0）、ogre sentry[N]（0.0）。
- 统计：遇到 24／已收录 13／READY 7／NEEDS 4／KEEP 0；池覆盖 78%；尾部 0 个 ΣE≈0.0。

### 3.36 Ruins of Telmur（`telmur`）
- 等级 30–40，5 层（`zone.lua`），`nb_npc`≈14／层；guardian：SHADE_OF_TELOS。
- 载入的通用文件（`telmur/npcs.lua`）：skeleton[rarity(0)]，ghoul[rarity(0)]，ghost[rarity(4)]，bone-giant[rarity(3)]，all[rarity(4, 35)]。
- 保证／剧情／后备（未收录）：
  - **The Shade of Telos**（SHADE_OF_TELOS，保证首领）：telmur/zone.lua:49 guardian。
- 常见池（E≥6）：ghoul（10.6）。
- 偶见池（1.5≤E<6）：skeleton magus（3.5）、ghast（3.5）、bone giant（2.7）、ghoulking（1.8）、eternal bone giant（1.8）、heavy bone giant（1.7）。
- 稀有池（0.3≤E<1.5）：banshee（0.9）、dread（0.8）、skeleton assassin（0.7）、dreadmaster（0.5）。
- 统计：遇到 18／已收录 6／READY 12／NEEDS 0／KEEP 0；池覆盖 36%；尾部 146 个 ΣE≈18.1。

### 3.37 Elven Ruins（`ancient-elven-ruins`）
- 等级 43–52，3 层（`zone.lua`），`nb_npc`≈20／层；guardian：GREATER_MUMMY_LORD。
- 载入的通用文件（`ancient-elven-ruins/npcs.lua`）：rodent[rarity(4)]，vermin[rarity(4)]，molds[rarity(3)]，mummy[rarity(0)]，skeleton[rarity(3)]，all[rarity(4, 35)]。
- 说明：等级 43–52，玩家通常极少到达。
- 保证／剧情／后备（未收录）：
  - **Greater Mummy Lord**（GREATER_MUMMY_LORD，保证首领）：ancient-elven-ruins/zone.lua:49 guardian。
- 常见池（E≥6）：ancient elven mummy（11.3）。
- 偶见池（1.5≤E<6）：rotting mummy（5.7）、animated mummy wrappings（2.8）、skeleton magus（1.9）。
- 稀有池（0.3≤E<1.5）：carrion worm mass（1.4）、greater mummy（1.4）、skeleton assassin（0.6）。
- 统计：遇到 12／已收录 4／READY 8／NEEDS 0／KEEP 0；池覆盖 25%；尾部 153 个 ΣE≈19.8。

### 3.38 Vor Armoury（`vor-armoury`）
- 等级 30–40，2 层（`zone.lua`），`nb_npc`≈25／层。
- 载入的通用文件（`vor-armoury/npcs.lua`）：orc[rarity(3)]，orc-vor[rarity(0)]，orc-grushnak[rarity(4)]，bone-giant[rarity(4)]，all[rarity(4, 35)]。
- 保证／剧情／后备（未收录）：
  - **Warmaster Gnarg**（GNARG，保证首领(末层静态图)）：maps/zones/vor-armoury-last.lua:37；zone.lua:82。
- 常见池（E≥6）：orc pyromancer（7.4）、orc cryomancer（7.4）。
- 偶见池（1.5≤E<6）：orc warrior（3.0）、orc soldier（2.4）、orc fighter（2.4）、bone giant（2.4）、orc archer（2.0）、orc assassin（2.0）、orc master assassin（1.7）、eternal bone giant（1.7）。
- 稀有池（0.3≤E<1.5）：orc grand master assassin（1.5）、orc berserker（1.5）、fiery orc wyrmic（1.3）、icy orc wyrmic（1.3）、orc elite fighter（1.1）、orc elite berserker（1.1）、heavy bone giant（1.1）、orc high pyromancer（0.5）、orc high cryomancer（0.5）、giant green ant（0.3）、giant red ant（0.3）、giant fire ant（0.3）、giant ice ant（0.3）、giant lightning ant（0.3）、giant acid ant（0.3）、giant army ant（0.3）、cold drake hatchling（0.3）、fire drake hatchling（0.3）、ghoul（0.3）、bloated horror（0.3）、dredgling（0.3）、wretchling（0.3）、onilug（0.3）、quasit（0.3）、dolleg（0.3）、dúathedlen（0.3）、minotaur（0.3）、multi-hued drake hatchling（0.3）、naga myrmidon（0.3）、slimy ooze（0.3）、poison ooze（0.3）、orc summoner（0.3）、orc necromancer（0.3）、snow giant（0.3）、giant spider（0.3）、spitting spider（0.3）、chitinous spider（0.3）、storm drake hatchling（0.3）、lesser vampire（0.3）、vampire（0.3）、master vampire（0.3）、elder vampire（0.3）、venom drake hatchling（0.3）、forest wight（0.3）、grave wight（0.3）、umber hulk（0.3）、xorn（0.3）。
- 统计：遇到 75／已收录 17／READY 58／NEEDS 0／KEEP 0；池覆盖 12%；尾部 97 个 ΣE≈6.4。

### 3.39 Briagh's Lair（`briagh-lair`）
- 等级 30–40，1 层（`zone.lua`），`nb_npc`≈70／层；guardian：BRIAGH。
- 载入的通用文件（`briagh-lair/npcs.lua`）：sandworm[rarity(0)]。
- 首领召唤／护卫：Briagh 召唤 vermin/sandworm×8（briagh-lair/npcs.lua:70-72）。
- 保证／剧情／后备（未收录）：
  - **Briagh, Great Sand Wyrm**（BRIAGH，保证首领）：briagh-lair/zone.lua:48 guardian。
- 常见池（E≥6）：gigantic sandworm tunneler（13.6）、gigantic corrosive tunneler（9.1）。
- 偶见池（1.5≤E<6）：sand-drake（5.5）、gigantic gravity worm（5.5）。
- 统计：遇到 7／已收录 2／READY 5／NEEDS 0／KEEP 0；池覆盖 52%；尾部 0 个 ΣE≈0.0。

### 3.40 Caverns to the hidden valley（`valley-moon-caverns`）
- 等级 30–40，2 层（`zone.lua`），`nb_npc`≈35／层。
- 载入的通用文件（`valley-moon-caverns/npcs.lua`）：minor-demon[rarity(0)]，major-demon[rarity(3)]，all[rarity(4, 65)]。
- 说明：`all.lua` 以 `rarity(4,65)` 载入。
- 常见池（E≥6）：wretchling（13.9）、onilug（13.9）、quasit（13.9）。
- 偶见池（1.5≤E<6）：fire imp（4.6）、dolleg（3.5）、dúathedlen（3.5）、uruivellas（1.9）、thaurhereg（1.9）。
- 统计：遇到 8／已收录 0／READY 8／NEEDS 0／KEEP 0；池覆盖 7%；尾部 141 个 ΣE≈12.3。

### 3.41 Flooded Cave（`flooded-cave`）
- 等级 30–40，2 层（`zone.lua`），`nb_npc`≈35／层。
- 载入的通用文件（`flooded-cave/npcs.lua`）：aquatic_critter[rarity(0)]，aquatic_demon[rarity(0)]。
- 保证／剧情／后备（未收录）：
  - **Ukllmswwik the Wise**（UKLLMSWWIK，保证首领(末层静态图)）：maps/zones/flooded-cave-last.lua:23；zone.lua:76（zone.lua:53 的 guardian 行被注释）。
- 常见池（E≥6）：squid（17.3）、water imp（17.3）、ink squid（8.6）。
- 稀有池（0.3≤E<1.5）：Walrog（0.3）。
- 统计：遇到 9／已收录 4／READY 5／NEEDS 0／KEEP 0；池覆盖 38%；尾部 0 个 ΣE≈0.0。

### 3.42 Temple of Creation（`temple-of-creation`）
- 等级 30–40，3 层（`zone.lua`），`nb_npc`≈35／层。
- 载入的通用文件（`temple-of-creation/npcs.lua`）：aquatic_critter[rarity(5)]，aquatic_demon[rarity(7)]，naga[rarity(0)]。
- 保证／剧情／后备（未收录）：
  - **Slasul**（SLASUL，保证首领(末层静态图)）：maps/zones/temple-of-creation-last.lua:26；zone.lua:80。
- 常见池（E≥6）：naga myrmidon（54.1）、naga tide huntress（11.3）、squid（9.0）、naga psyren（8.7）、ink squid（7.7）、water imp（6.8）。
- 稀有池（0.3≤E<1.5）：Walrog（0.8）。
- 统计：遇到 12／已收录 4／READY 8／NEEDS 0／KEEP 0；池覆盖 20%；尾部 0 个 ΣE≈0.0。

### 3.43 Charred Scar（`charred-scar`）
- 等级 30–50，1 层（`zone.lua`），`nb_npc`≈30／层。
- 载入的通用文件（`charred-scar/npcs.lua`）：faeros[rarity(0)]，fire_elemental[rarity(0)]，molten_golem[rarity(0)]，fire-drake[rarity(0)]。
- 说明：`fire_elemental.lua`／`molten_golem.lua` 在本版本不存在（`charred-scar/npcs.lua:21-22`，无怪）；静态图摆放见 `maps/zones/charred-scar.lua:24-29`。
- 保证／剧情／后备（未收录）：
  - **Fyrk, Faeros High Guard**（FYRK，任务首领）：quests/charred-scar.lua:68 makeEntityByName。
  - **High Sun-Paladin Rodmour**（SUN_PALADIN_DEFENDER_RODMOUR，剧情NPC(静态图)）：maps/zones/charred-scar.lua:25。
  - **Elandar**（ELANDAR，剧情NPC(静态图)）：maps/zones/charred-scar.lua:28。
  - **Argoniel**（ARGONIEL，剧情NPC(静态图)）：maps/zones/charred-scar.lua:29。
  - **human sun-paladin**（SUN_PALADIN_DEFENDER，剧情NPC(静态图)）：maps/zones/charred-scar.lua:24。
  - **orc warrior**[N]（ORC_ATTACK，剧情敌军(静态图)）：maps/zones/charred-scar.lua:26。
- 常见池（E≥6）：faeros（10.4）、fire drake hatchling（10.4）。
- 偶见池（1.5≤E<6）：greater faeros（3.5）、fire drake（3.5）、fire wyrm（2.1）、ultimate faeros（2.0）。
- 统计：遇到 12／已收录 0／READY 11／NEEDS 1／KEEP 0；池覆盖 0%；尾部 0 个 ΣE≈0.0。

### 3.44 Fearscape（`demon-plane`）
- 等级 30–40，1 层（`zone.lua`），`nb_npc`≈40／层；guardian：DRAEBOR。
- 载入的通用文件（`demon-plane/npcs.lua`）：ghost[rarity(5)]，major-demon[rarity(2)]，minor-demon[rarity(0)]。
- 首领召唤／护卫：Draebor 召唤 demon×1（demon-plane/npcs.lua:58-60）。
- 保证／剧情／后备（未收录）：
  - **Draebor, the Imp**（DRAEBOR，保证首领）：demon-plane/zone.lua:58 guardian。
- 常见池（E≥6）：wretchling（9.6）、onilug（9.6）、quasit（9.6）。
- 偶见池（1.5≤E<6）：dolleg（3.2）、dúathedlen（3.2）、fire imp（3.2）。
- 稀有池（0.3≤E<1.5）：uruivellas（1.5）、thaurhereg（1.5）、banshee（0.7）、dread（0.6）、dreadmaster（0.4）。
- 统计：遇到 12／已收录 0／READY 12／NEEDS 0／KEEP 0；池覆盖 0%；尾部 5 个 ΣE≈0.2。

### 3.45 Yiilkgur, the Sher'Tul Fortress（`shertul-fortress`）
- 等级 18–25，1 层（`zone.lua`），`nb_npc`≈0／层。
- 载入的通用文件（`shertul-fortress/npcs.lua`）：horror，feline[fn]。
- 说明：据点，`nb_npc={0,0}`；这里只列脚本／任务生物，低优先级。
- 保证／剧情／后备（未收录）：
  - **Weirdling Beast**（WEIRDLING_BEAST，据点内静态图首领）：maps/zones/shertul-fortress.tmx:155。
  - **Fortress Shadow**（BUTLER，据点管家(任务)）：quests/shertul-fortress.lua:88。
  - **Training Dummy**（TRAINING_DUMMY，据点训练假人）：shertul-fortress/npcs.lua:142。
  - **Pumpkin, the little kitty**（KITTY，据点宠物）：shertul-fortress/zone.lua:94 makeEntityByName。
- 统计：遇到 4／已收录 0／READY 4／NEEDS 0／KEEP 0；池覆盖 —；尾部 0 个 ΣE≈0.0。

### 3.46 Rak'shor Pride（`rak-shor-pride`）
- 等级 30–60，3 层（`zone.lua`），`nb_npc`≈37／层；guardian：RAK_SHOR。
- 载入的通用文件（`rak-shor-pride/npcs.lua`）：bone-giant[rarity(0)]，ghoul[rarity(5)]，ghost[rarity(5)]，skeleton[rarity(5)]，orc[rarity(3)]，horror-undead[rarity(1)]，orc-rak-shor[rarity(0)]，all[rarity(4, 35)]。
- 首领召唤／护卫：Rak'shor 召唤 undead×2、护卫 undead×(4..8)（rak-shor-pride/npcs.lua:70-75）。
- 保证／剧情／后备（未收录）：
  - **Rak'shor, Grand Necromancer of the Pride**（RAK_SHOR，保证首领）：rak-shor-pride/zone.lua:60 guardian。
- 常见池（E≥6）：bone giant（13.4）、orc necromancer（13.4）、orc blood mage（6.7）。
- 偶见池（1.5≤E<6）：eternal bone giant（4.5）、heavy bone giant（4.0）、orc warrior（3.3）、orc corruptor（3.3）、orc soldier（2.7）、necrotic mass（2.7）、runed bone giant（2.4）、ghoul（2.2）、orc archer（2.2）、orc assassin（2.2）、orc master assassin（1.9）、ghast（1.7）、skeleton magus（1.7）、orc grand master assassin（1.7）、necrotic abomination（1.7）、bone horror（1.7）、sanguine horror（1.7）。
- 稀有池（0.3≤E<1.5）：fiery orc wyrmic（1.5）、icy orc wyrmic（1.5）、ghoulking（1.2）、banshee（1.0）、dread（0.9）、skeleton assassin（0.7）、animated blood（0.6）、dreadmaster（0.6）、ruin banshee（0.6）、Rotting Titan（0.5）、Glacial Legion（0.5）、Heavy Sentinel（0.5）、Arch Zephyr（0.5）、Void Spectre（0.5）、giant green ant（0.3）、giant red ant（0.3）、giant fire ant（0.3）、giant ice ant（0.3）、giant lightning ant（0.3）、giant acid ant（0.3）、giant army ant（0.3）、cold drake hatchling（0.3）、fire drake hatchling（0.3）、bloated horror（0.3）、dredgling（0.3）、wretchling（0.3）、onilug（0.3）、quasit（0.3）、dolleg（0.3）、dúathedlen（0.3）、minotaur（0.3）、multi-hued drake hatchling（0.3）、naga myrmidon（0.3）、slimy ooze（0.3）、poison ooze（0.3）、orc fighter（0.3）、orc summoner（0.3）、snow giant（0.3）、giant spider（0.3）、spitting spider（0.3）、chitinous spider（0.3）、storm drake hatchling（0.3）、lesser vampire（0.3）、vampire（0.3）、master vampire（0.3）、elder vampire（0.3）、venom drake hatchling（0.3）、forest wight（0.3）、grave wight（0.3）、umber hulk（0.3）、xorn（0.3）、orc berserker（0.3）、orc pyromancer（0.3）、orc cryomancer（0.3）。
- 统计：遇到 95／已收录 20／READY 75／NEEDS 0／KEEP 0；池覆盖 13%；尾部 96 个 ΣE≈7.6。

### 3.47 Ruins of Kor'Pul（`ruins-kor-pul`）
- 等级 1–7，3 层（`zone.lua`），`nb_npc`≈25／层，`max_ood=2`，布局 HIDEOUT / DEFAULT。
- 载入的通用文件（`ruins-kor-pul/npcs.lua`）：rodent[rarity(0)]，vermin[rarity(2)]，molds[rarity(1)]，skeleton[rarity(0)]，snake[rarity(2)]，all[rarity(4, 35)]，thieve[rarity(0)]。
- 保证／剧情／后备（未收录）：
  - **The Shade**[K]（SHADE，保证首领(DEFAULT 布局末层)）：maps/zones/ruins-kor-pul-last.lua:24；zone.lua:79。
  - **The Possessed**（THE_POSSESSED，保证首领(HIDEOUT 布局末层)）：maps/zones/ruins-kor-pul-invaded-last.lua:25,28；zone.lua:79。
  - **Kor's Fury**（KOR_FURY，后备守关(回访)）：ruins-kor-pul/npcs.lua:88,132 activateBackupGuardian("KOR_FURY",3,35)，仅东行后。
- 统计：遇到 30／已收录 27／READY 2／NEEDS 0／KEEP 1；池覆盖 99%；尾部 19 个 ΣE≈1.0。


## 4. 全部未收录身份的合同表（266 条）

列：名称／define_as（空＝无 define_as，按名称）／`type/subtype`／唯一·rank／源码位置（`newEntity` 起始行）／出现方式与频度（保证＝首领/静态图/召唤，池＝随机池 E，区内＝区内 npcs.lua 私有池，仅列前 3 区）／外观解析／图存在（在 `gfx/shockbolt/` 校验，全部命中）／裁决（S＝单图，T＝native_tall，I＝tall 内层≠默认名，N＝NEEDS，K＝KEEP）／同子类已收录的邻近者（外观易混对照，取名字词重合最多者）。「外观解析」＝进入 `identify()` 后目录需匹配的图。

裁决计数：单图 S 178，native_tall T 68，内层≠默认名 I 6，NEEDS 7，KEEP 7；合计 266。所有身份在多个区域／布局的多条 `newEntity` 记录里解析出的图**完全一致**（脚本已逐条比对，无一例分歧）。


### 4.humanoid/orc（23）

| 名称 | define_as | 唯一/rank | 源码 | 出现（频度） | 外观解析 | 裁 | 同类已收录 |
|---|---|---|---|---|---|:-:|---|
| orc warrior | HILL_ORC_WARRIOR | —/2 | `general/npcs/orc.lua:49` | reknor:池E27.5；reknor-escape:池E18.0；rak-shor-pride:池E3.3；…共10区 | 默认名 humanoid_orc_orc_warrior.png | S | Brotoq the Reaver、Golbug the Destroyer、Krogar（共4） |
| orc soldier | ORC | —/2 | `general/npcs/orc.lua:94` | reknor:池E13.7；reknor-escape:池E9.0；rak-shor-pride:池E2.7；…共8区 | 默认名 humanoid_orc_orc_soldier.png | S | Brotoq the Reaver、Golbug the Destroyer、Krogar（共4） |
| orc archer | HILL_ORC_ARCHER | —/2 | `general/npcs/orc.lua:70` | reknor:池E9.2；reknor-escape:池E6.0；rak-shor-pride:池E2.2；…共5区 | 默认名 humanoid_orc_orc_archer.png | S | Brotoq the Reaver、Golbug the Destroyer、Krogar（共4） |
| orc assassin | — | —/2 | `general/npcs/orc.lua:174` | reknor:池E9.2；rak-shor-pride:池E2.2；vor-armoury:池E2.0；…共4区 | 默认名 humanoid_orc_orc_assassin.png | S | Brotoq the Reaver、Golbug the Destroyer、Krogar（共4） |
| orc necromancer | — | —/2 | `general/npcs/orc-rak-shor.lua:52` | rak-shor-pride:池E13.4；ardhungol:池E0.9；reknor:池E0.7；…共6区 | 默认名 humanoid_orc_orc_necromancer.png | S | Brotoq the Reaver、Golbug the Destroyer、Krogar（共4） |
| orc master assassin | — | —/3 | `general/npcs/orc.lua:204` | reknor:池E6.9；rak-shor-pride:池E1.9；vor-armoury:池E1.7 | 默认名 humanoid_orc_orc_master_assassin.png | S | Brotoq the Reaver、Golbug the Destroyer、Krogar（共4） |
| Warmaster Gnarg | GNARG | 唯一/4 | `zones/vor-armoury/npcs.lua:29` | vor-armoury:保证首领(末层静态图) | 默认名 humanoid_orc_warmaster_gnarg.png | S | Brotoq the Reaver、Golbug the Destroyer、Krogar（共4） |
| Rak'shor, Grand Necromancer of the Pride | RAK_SHOR | 唯一/5 | `zones/rak-shor-pride/npcs.lua:32` | rak-shor-pride:保证首领 | 默认名 humanoid_orc_rak_shor__grand_necromancer_of_the_pride.png | S | Brotoq the Reaver、Golbug the Destroyer、Massok the Dragonslayer（共4） |
| orc grand master assassin | — | —/3 | `general/npcs/orc.lua:240` | reknor:池E5.5；rak-shor-pride:池E1.7；vor-armoury:池E1.5 | 默认名 humanoid_orc_orc_grand_master_assassin.png | S | Brotoq the Reaver、Golbug the Destroyer、Krogar（共4） |
| fiery orc wyrmic | ORC_FIRE_WYRMIC | —/3 | `general/npcs/orc.lua:114` | reknor:池E4.6；rak-shor-pride:池E1.5；vor-armoury:池E1.3 | 默认名 humanoid_orc_fiery_orc_wyrmic.png | S | Brotoq the Reaver、Golbug the Destroyer、Krogar（共4） |
| icy orc wyrmic | ORC_ICE_WYRMIC | —/3 | `general/npcs/orc.lua:144` | reknor:池E4.6；rak-shor-pride:池E1.5；vor-armoury:池E1.3 | 默认名 humanoid_orc_icy_orc_wyrmic.png | S | Brotoq the Reaver、Golbug the Destroyer、Krogar（共4） |
| orc blood mage | — | —/2 | `general/npcs/orc-rak-shor.lua:115` | rak-shor-pride:池E6.7；ardhungol:池E0.4；reknor:池E0.3 | 默认名 humanoid_orc_orc_blood_mage.png | S | Brotoq the Reaver、Golbug the Destroyer、Krogar（共4） |
| orc pyromancer | — | —/2 | `general/npcs/orc-vor.lua:54` | vor-armoury:池E7.4；rak-shor-pride:池E0.3 | 默认名 humanoid_orc_orc_pyromancer.png | S | Brotoq the Reaver、Golbug the Destroyer、Krogar（共4） |
| orc cryomancer | — | —/2 | `general/npcs/orc-vor.lua:108` | vor-armoury:池E7.4；rak-shor-pride:池E0.3 | 默认名 humanoid_orc_orc_cryomancer.png | S | Brotoq the Reaver、Golbug the Destroyer、Krogar（共4） |
| orc warrior | ORC_ATTACK | —/2 | `zones/charred-scar/npcs.lua:135` | charred-scar:剧情敌军(静态图) | 见 §5 | N | Brotoq the Reaver、Golbug the Destroyer、Krogar（共4） |
| orc fighter | — | —/2 | `general/npcs/orc-grushnak.lua:54` | vor-armoury:池E2.4；ardhungol:池E0.4；unremarkable-cave:池E0.4；…共4区 | 默认名 humanoid_orc_orc_fighter.png | S | Brotoq the Reaver、Golbug the Destroyer、Krogar（共4） |
| orc corruptor | — | —/3 | `general/npcs/orc-rak-shor.lua:139` | rak-shor-pride:池E3.3 | 默认名 humanoid_orc_orc_corruptor.png | S | Brotoq the Reaver、Golbug the Destroyer、Krogar（共4） |
| orc summoner | — | —/2 | `general/npcs/orc-gorbat.lua:53` | ardhungol:池E0.4；unremarkable-cave:池E0.4；rak-shor-pride:池E0.3；…共4区 | 默认名 humanoid_orc_orc_summoner.png | S | Brotoq the Reaver、Golbug the Destroyer、Krogar（共4） |
| orc berserker | — | —/2 | `general/npcs/orc-grushnak.lua:111` | vor-armoury:池E1.5；rak-shor-pride:池E0.3 | 默认名 humanoid_orc_orc_berserker.png | S | Brotoq the Reaver、Golbug the Destroyer、Krogar（共4） |
| orc elite fighter | ORC_ELITE_FIGHTER | —/3 | `general/npcs/orc-grushnak.lua:79` | vor-armoury:池E1.1 | 默认名 humanoid_orc_orc_elite_fighter.png | S | Brotoq the Reaver、Golbug the Destroyer、Krogar（共4） |
| orc elite berserker | ORC_ELITE_BERSERKER | —/3 | `general/npcs/orc-grushnak.lua:134` | vor-armoury:池E1.1 | 默认名 humanoid_orc_orc_elite_berserker.png | S | Brotoq the Reaver、Golbug the Destroyer、Krogar（共4） |
| orc high pyromancer | — | —/3 | `general/npcs/orc-vor.lua:77` | vor-armoury:池E0.5 | 默认名 humanoid_orc_orc_high_pyromancer.png | S | Brotoq the Reaver、Golbug the Destroyer、Krogar（共4） |
| orc high cryomancer | — | —/3 | `general/npcs/orc-vor.lua:131` | vor-armoury:池E0.5 | 默认名 humanoid_orc_orc_high_cryomancer.png | S | Brotoq the Reaver、Golbug the Destroyer、Krogar（共4） |

### 4.humanoid/human（18）

| 名称 | define_as | 唯一/rank | 源码 | 出现（频度） | 外观解析 | 裁 | 同类已收录 |
|---|---|---|---|---|---|:-:|---|
| The Possessed | THE_POSSESSED | 唯一/4 | `zones/ruins-kor-pul/npcs.lua:93` | ruins-kor-pul:保证首领(HIDEOUT 布局末层) | tall：invis+add_mos→humanoid_human_the_possessed.png | T | cutpurse、rogue、thief（共8） |
| Subject Z | SUBJECT_Z | 唯一/4 | `zones/halfling-ruins/npcs.lua:26` | halfling-ruins:保证首领(末层静态图) | 默认名 humanoid_human_subject_z.png | S | cutpurse、rogue、thief（共8） |
| Kyless | KYLESS | 唯一/4 | `zones/keepsake-meadow/npcs.lua:320` | keepsake-meadow:保证首领(末层静态图) | tall：invis+add_mos→humanoid_human_kyless.png | T | cutpurse、rogue、thief（共8） |
| Assassin Lord | ASSASSIN_LORD | 唯一/4 | `zones/thieves-tunnels/npcs.lua:24` | thieves-tunnels:任务关(第 2 层静态图) | 默认名 humanoid_human_assassin_lord.png | S | cutpurse、rogue、thief（共8） |
| assassin | THIEF_ASSASSIN | —/2 | `general/npcs/thieve.lua:139` | maze:池E2.6；thieves-tunnels:池E0.9；ardhungol:池E0.3 | 默认名 humanoid_human_assassin.png | S | cutpurse、rogue、thief（共8） |
| Melinda | MELINDA | —/2 | `zones/crypt-kryl-feijan/npcs.lua:88` | crypt-kryl-feijan:任务NPC(末层) | 见 §5 | K | cutpurse、rogue、thief（共8） |
| caravan merchant | CARAVAN_MERCHANT | —/2 | `zones/keepsake-meadow/npcs.lua:62` | keepsake-meadow:剧情NPC(梦境层静态图) | 显式 humanoid_human_spectator02.png | S | cutpurse、rogue、thief（共8） |
| caravan guard | CARAVAN_GUARD | —/2 | `zones/keepsake-meadow/npcs.lua:75` | keepsake-meadow:剧情NPC(梦境层静态图) | 显式 humanoid_human_spectator.png | S | cutpurse、rogue、thief（共8） |
| caravan porter | CARAVAN_PORTER | —/2 | `zones/keepsake-meadow/npcs.lua:91` | keepsake-meadow:剧情NPC(梦境层静态图) | 显式 humanoid_human_spectator03.png | S | cutpurse、rogue、thief（共8） |
| bandit lord | — | —/2 | `general/npcs/thieve.lua:112` | maze:池E2.1；thieves-tunnels:池E0.5 | 默认名 humanoid_human_bandit_lord.png | S | bandit、cutpurse、rogue（共8） |
| High Sun-Paladin Rodmour | SUN_PALADIN_DEFENDER_RODMOUR | 唯一/3 | `zones/charred-scar/npcs.lua:80` | charred-scar:剧情NPC(静态图) | 默认名 humanoid_human_high_sun_paladin_rodmour.png | S | Urkis, the High Tempest、cutpurse、rogue（共8） |
| Argoniel | ARGONIEL | —/5 | `zones/charred-scar/npcs.lua:218` | charred-scar:剧情NPC(静态图) | tall：invis+add_mos→humanoid_human_argoniel.png | T | cutpurse、rogue、thief（共8） |
| Melinda | MELINDA_BEACH | —/2 | `zones/south-beach/npcs.lua:24` | south-beach:任务NPC | 见 §5 | K | cutpurse、rogue、thief（共8） |
| rogue sapper | THIEF_SAPPER | —/2 | `general/npcs/thieve.lua:190` | maze:池E1.6；thieves-tunnels:池E0.5 | 显式 humanoid_human_assassin.png | S | rogue、cutpurse、thief（共8） |
| Aluin the Fallen | ALUIN | 唯一/4 | `zones/trollmire/npcs.lua:223` | trollmire:后备守关(回访) | 默认名 humanoid_human_aluin_the_fallen.png | S | Urkis, the High Tempest、cutpurse、rogue（共8） |
| Lost Merchant | MERCHANT | —/ | `zones/thieves-tunnels/npcs.lua:113` | thieves-tunnels:任务关(友方) | 默认名 humanoid_human_lost_merchant.png | S | cutpurse、rogue、thief（共8） |
| human sun-paladin | SUN_PALADIN_DEFENDER | —/3 | `zones/charred-scar/npcs.lua:50` | charred-scar:剧情NPC(静态图) | 默认名 humanoid_human_human_sun_paladin.png | S | cutpurse、rogue、thief（共8） |
| shadowblade | THIEF_ASSASSIN | —/2 | `general/npcs/thieve.lua:162` | thieves-tunnels:池E0.7；maze:池E0.5 | 默认名 humanoid_human_shadowblade.png | S | cutpurse、rogue、thief（共8） |

### 4.spiderkin/spider（17）

| 名称 | define_as | 唯一/rank | 源码 | 出现（频度） | 外观解析 | 裁 | 同类已收录 |
|---|---|---|---|---|---|:-:|---|
| weaver hatchling | — | —/1 | `zones/unhallowed-morass/npcs.lua:41` | unhallowed-morass:区内E30.9 | 显式 spiderkin_spider_weaver_young.png | S | Ungolë |
| orb spinner | — | —/1 | `zones/unhallowed-morass/npcs.lua:57` | unhallowed-morass:区内E30.9 | 默认名 spiderkin_spider_orb_spinner.png | S | Ungolë |
| giant spider | — | —/1 | `general/npcs/spider.lua:49` | ardhungol:池E35.2；daikara:池E1.1；ruined-dungeon:池E0.8；…共11区 | 默认名 spiderkin_spider_giant_spider.png | S | Ungolë |
| spitting spider | — | —/1 | `general/npcs/spider.lua:66` | ardhungol:池E35.2；daikara:池E1.1；ruined-dungeon:池E0.8；…共10区 | 默认名 spiderkin_spider_spitting_spider.png | S | Ungolë |
| chitinous spider | — | —/1 | `general/npcs/spider.lua:84` | ardhungol:池E35.2；dreadfell:池E0.8；reknor:池E0.7；…共9区 | 默认名 spiderkin_spider_chitinous_spider.png | S | Ungolë |
| fate spinner | — | —/2 | `zones/unhallowed-morass/npcs.lua:87` | unhallowed-morass:区内E12.8 | 默认名 spiderkin_spider_fate_spinner.png | S | Ungolë |
| weaver young | — | —/1 | `general/npcs/spider.lua:244` | ardhungol:池E17.6；daikara:池E0.6；dreadfell:池E0.4；…共5区 | 默认名 spiderkin_spider_weaver_young.png | S | Ungolë |
| Weaver Queen | WEAVER_QUEEN | 唯一/4 | `zones/unhallowed-morass/npcs.lua:119` | unhallowed-morass:保证首领 | tall：invis+add_mos→spiderkin_spider_weaver_queen.png | T | Ungolë |
| fate weaver | — | —/2 | `zones/unhallowed-morass/npcs.lua:102` | unhallowed-morass:区内E8.5 | 默认名 spiderkin_spider_fate_weaver.png | S | Ungolë |
| gaeramarth | — | —/2 | `general/npcs/spider.lua:101` | ardhungol:池E10.9 | 默认名 spiderkin_spider_gaeramarth.png | S | Ungolë |
| ninurlhing | — | —/2 | `general/npcs/spider.lua:127` | ardhungol:池E10.9 | 默认名 spiderkin_spider_ninurlhing.png | S | Ungolë |
| faerlhing | — | —/3 | `general/npcs/spider.lua:152` | ardhungol:池E8.2 | 默认名 spiderkin_spider_faerlhing.png | S | Ungolë |
| losselhing | — | —/3 | `general/npcs/spider.lua:210` | ardhungol:池E8.2 | 默认名 spiderkin_spider_losselhing.png | S | Ungolë |
| orb weaver | — | —/1 | `zones/unhallowed-morass/npcs.lua:73` | unhallowed-morass:区内E2.6 | 默认名 spiderkin_spider_orb_weaver.png | S | Ungolë |
| Nimisil | NIMISIL | 唯一/4 | `zones/maze/npcs.lua:152` | maze:后备守关(回访) | 默认名 spiderkin_spider_nimisil.png | S | Ungolë |
| weaver patriarch | — | —/2 | `general/npcs/spider.lua:266` | ardhungol:池E2.7 | 默认名 spiderkin_spider_weaver_patriarch.png | S | Ungolë |
| ungolmor | — | —/3 | `general/npcs/spider.lua:182` | ardhungol:池E0.3 | 默认名 spiderkin_spider_ungolmor.png | S | Ungolë |

### 4.humanoid/shalore（11）

| 名称 | define_as | 唯一/rank | 源码 | 出现（频度） | 外观解析 | 裁 | 同类已收录 |
|---|---|---|---|---|---|:-:|---|
| elven guard | — | —/2 | `general/npcs/elven-warrior.lua:53` | rhaloren-camp:池E17.0；crypt-kryl-feijan:池E12.7 | 默认名 humanoid_shalore_elven_guard.png | S | Rhaloren Inquisitor |
| mean looking elven guard | — | —/2 | `general/npcs/elven-warrior.lua:67` | rhaloren-camp:池E13.1；crypt-kryl-feijan:池E12.7 | 默认名 humanoid_shalore_mean_looking_elven_guard.png | S | Rhaloren Inquisitor |
| elven mage | — | —/2 | `general/npcs/elven-caster.lua:55` | mark-spellblaze:池E7.6；rhaloren-camp:池E6.6；crypt-kryl-feijan:池E6.3 | 默认名 humanoid_shalore_elven_mage.png | S | Rhaloren Inquisitor |
| elven tempest | — | —/2 | `general/npcs/elven-caster.lua:72` | mark-spellblaze:池E7.6；rhaloren-camp:池E6.6；crypt-kryl-feijan:池E6.3 | 默认名 humanoid_shalore_elven_tempest.png | S | Rhaloren Inquisitor |
| Grand Corruptor | GRAND_CORRUPTOR | 唯一/4 | `zones/mark-spellblaze/npcs.lua:30` | mark-spellblaze:保证首领(末层静态图) | 默认名 humanoid_shalore_grand_corruptor.png | S | Rhaloren Inquisitor |
| elven cultist | — | —/2 | `general/npcs/elven-caster.lua:92` | crypt-kryl-feijan:池E12.7；mark-spellblaze:池E0.7 | 默认名 humanoid_shalore_elven_cultist.png | S | Rhaloren Inquisitor |
| elven blood mage | — | —/2 | `general/npcs/elven-caster.lua:118` | crypt-kryl-feijan:池E12.7；mark-spellblaze:池E0.7 | 默认名 humanoid_shalore_elven_blood_mage.png | S | Rhaloren Inquisitor |
| elven warrior | — | —/2 | `general/npcs/elven-warrior.lua:81` | crypt-kryl-feijan:池E12.7 | 默认名 humanoid_shalore_elven_warrior.png | S | Rhaloren Inquisitor |
| elven corruptor | — | —/3 | `general/npcs/elven-caster.lua:143` | crypt-kryl-feijan:池E4.2；mark-spellblaze:池E0.3 | 默认名 humanoid_shalore_elven_corruptor.png | S | Rhaloren Inquisitor |
| Elandar | ELANDAR | —/5 | `zones/charred-scar/npcs.lua:160` | charred-scar:剧情NPC(静态图) | tall：invis+add_mos→humanoid_shalore_elandar.png | T | Rhaloren Inquisitor |
| elven elite warrior | — | —/3 | `general/npcs/elven-warrior.lua:97` | crypt-kryl-feijan:池E2.5 | 默认名 humanoid_shalore_elven_elite_warrior.png | S | Rhaloren Inquisitor |

### 4.giant/ogre（10）

| 名称 | define_as | 唯一/rank | 源码 | 出现（频度） | 外观解析 | 裁 | 同类已收录 |
|---|---|---|---|---|---|:-:|---|
| Healer Astelrid | HEALER_ASTELRID | 唯一/4 | `zones/conclave-vault/npcs.lua:140` | conclave-vault:保证首领(boss 房) | tall：invis+add_mos→giant_ogre_healer_astelrid.png | T | 无同子类已收录 |
| ogre guard | — | —/2 | `general/npcs/ogre.lua:45` | crypt-kryl-feijan:池E2.1 | tall：invis+add_mos→giant_ogre_ogre_guard.png | T | 无同子类已收录 |
| ogre mauler | — | —/2 | `general/npcs/ogre.lua:86` | crypt-kryl-feijan:池E2.1 | tall：invis+add_mos→giant_ogre_ogre_mauler.png | T | 无同子类已收录 |
| ogre rune-spinner | — | —/3 | `general/npcs/ogre.lua:124` | crypt-kryl-feijan:池E2.1 | tall：invis+add_mos→giant_ogre_ogre_rune_spinner.png | T | 无同子类已收录 |
| ogre pounder | — | —/3 | `general/npcs/ogre.lua:103` | crypt-kryl-feijan:池E1.8 | tall：invis+add_mos→giant_ogre_ogre_pounder.png | T | 无同子类已收录 |
| ogre warmaster | — | —/3 | `general/npcs/ogre.lua:62` | crypt-kryl-feijan:池E1.6 | tall：invis+add_mos→giant_ogre_ogre_warmaster.png | T | 无同子类已收录 |
| degenerated ogric mass | — | —/2 | `zones/conclave-vault/npcs.lua:61` | conclave-vault:区内E0.0 | tall：invis+add_mos→giant_ogre_degenerated_ogric_mass.png | T | 无同子类已收录 |
| ogric abomination | — | —/3 | `zones/conclave-vault/npcs.lua:79` | conclave-vault:区内E0.0 | tall：invis+add_mos→giant_ogre_ogric_abomination.png | T | 无同子类已收录 |
| ogre sentry | OGRE_SENTRY | —/3 | `zones/conclave-vault/npcs.lua:102` | conclave-vault:区内E0.0 | 见 §5 | N | 无同子类已收录 |
| ogre sentry | OGRE_SENTRY2 | —/3 | `zones/conclave-vault/npcs.lua:127` | conclave-vault:区内E0.0 | 见 §5 | N | 无同子类已收录 |

### 4.horror/eldritch（8）

| 名称 | define_as | 唯一/rank | 源码 | 出现（频度） | 外观解析 | 裁 | 同类已收录 |
|---|---|---|---|---|---|:-:|---|
| The Dreaming One | DREAMING_ONE | 唯一/4 | `zones/heart-gloom/npcs.lua:104` | heart-gloom:保证首领(净化布局) | 显式 seed_of_dreams.png | S | 无同子类已收录 |
| bloated horror | — | —/2 | `general/npcs/horror.lua:115` | lake-nur:池E2.5；ardhungol:池E0.9；ruined-dungeon:池E0.8；…共10区 | 默认名 horror_eldritch_bloated_horror.png | S | 无同子类已收录 |
| Weirdling Beast | WEIRDLING_BEAST | 唯一/3.5 | `zones/shertul-fortress/npcs.lua:24` | shertul-fortress:据点内静态图首领 | 默认名 horror_eldritch_weirdling_beast.png | S | 无同子类已收录 |
| devourer | — | —/2 | `general/npcs/horror.lua:483` | lake-nur:池E1.3；ardhungol:池E0.5；dreadfell:池E0.4；…共6区 | 默认名 horror_eldritch_devourer.png | S | 无同子类已收录 |
| blade horror | BLADEHORROR | —/2 | `general/npcs/horror.lua:514` | lake-nur:池E1.3；ardhungol:池E0.5；dreadfell:池E0.4；…共5区 | tall：invis+add_mos→horror_eldritch_blade_horror.png | T | 无同子类已收录 |
| luminous horror | — | —/2 | `general/npcs/horror.lua:408` | lake-nur:池E1.1；ardhungol:池E0.5；dreadfell:池E0.4；…共5区 | 默认名 horror_eldritch_luminous_horror.png | S | 无同子类已收录 |
| oozing horror | — | —/3 | `general/npcs/horror.lua:554` | lake-nur:池E0.4 | 默认名 horror_eldritch_oozing_horror.png | S | 无同子类已收录 |
| umbral horror | — | —/3 | `general/npcs/horror.lua:613` | lake-nur:池E0.3 | tall：invis+add_mos→horror_eldritch_umbral_horror.png | T | 无同子类已收录 |

### 4.undead/ghost（8）

| 名称 | define_as | 唯一/rank | 源码 | 出现（频度） | 外观解析 | 裁 | 同类已收录 |
|---|---|---|---|---|---|:-:|---|
| The Shade of Telos | SHADE_OF_TELOS | 唯一/4 | `zones/telmur/npcs.lua:29` | telmur:保证首领 | 默认名 undead_ghost_the_shade_of_telos.png | S | 无同子类已收录 |
| banshee | — | —/2 | `general/npcs/ghost.lua:108` | dreadfell:池E2.8；rak-shor-pride:池E1.0；telmur:池E0.9；…共4区 | 显式 banshee.png | S | 无同子类已收录 |
| dread | — | —/2 | `general/npcs/ghost.lua:63` | dreadfell:池E1.3；rak-shor-pride:池E0.9；telmur:池E0.8；…共4区 | 显式 dread.png | S | 无同子类已收录 |
| Kor's Fury | KOR_FURY | 唯一/4 | `zones/ruins-kor-pul/npcs.lua:138` | ruins-kor-pul:后备守关(回访) | 默认名 undead_ghost_kor_s_fury.png | S | 无同子类已收录 |
| dreadmaster | — | —/3 | `general/npcs/ghost.lua:81` | rak-shor-pride:池E0.6；telmur:池E0.5；demon-plane:池E0.4 | 显式 dreadmaster.png | S | 无同子类已收录 |
| Aletta Soultorn | ALETTA | 唯一/3.5 | `zones/dreadfell/npcs.lua:282` | dreadfell:区内E0.6 | 默认名 undead_ghost_aletta_soultorn.png | S | 无同子类已收录 |
| ruin banshee | — | —/3 | `general/npcs/ghost.lua:129` | rak-shor-pride:池E0.6 | 默认名 undead_ghost_ruin_banshee.png | S | 无同子类已收录 |
| Glacial Legion | GLACIAL_LEGION | 唯一/3.5 | `zones/rak-shor-pride/npcs.lua:195` | rak-shor-pride:区内E0.5 | tall：invis+add_mos→undead_ghost_glacial_legion.png | T | 无同子类已收录 |

### 4.horror/temporal（7）

| 名称 | define_as | 唯一/rank | 源码 | 出现（频度） | 外观解析 | 裁 | 同类已收录 |
|---|---|---|---|---|---|:-:|---|
| dredgling | — | —/2 | `general/npcs/horror_temporal.lua:48` | temporal-rift:池E12.3；maze:池E4.7；ardhungol:池E0.9；…共11区 | 默认名 horror_temporal_dredgling.png | S | 无同子类已收录 |
| Chronolith Twin | CHRONOLITH_TWIN | 唯一/4 | `zones/temporal-rift/npcs.lua:137` | temporal-rift:保证首领(第 4 层，与 CLONE 成对) | tall 内层 horror_temporal_cronolith_twin.png（≠默认名） | I | 无同子类已收录 |
| Chronolith Clone | CHRONOLITH_CLONE | 唯一/4 | `zones/temporal-rift/npcs.lua:183` | temporal-rift:保证首领(第 4 层，与 TWIN 成对) | tall 内层 horror_temporal_cronolith_clone.png（≠默认名） | I | 无同子类已收录 |
| dredge | — | —/2 | `general/npcs/horror_temporal.lua:70` | temporal-rift:池E6.1；ardhungol:池E0.5；dreadfell:池E0.4；…共6区 | 默认名 horror_temporal_dredge.png | S | 无同子类已收录 |
| temporal stalker | — | —/2 | `general/npcs/horror_temporal.lua:129` | temporal-rift:池E2.9；ardhungol:池E0.3 | tall：invis+add_mos→horror_temporal_temporal_stalker.png | T | 无同子类已收录 |
| void horror | — | —/2 | `general/npcs/horror_temporal.lua:160` | temporal-rift:池E2.2 | 默认名 horror_temporal_void_horror.png | S | 无同子类已收录 |
| dredge captain | — | —/3 | `general/npcs/horror_temporal.lua:98` | temporal-rift:池E1.8 | 默认名 horror_temporal_dredge_captain.png | S | 无同子类已收录 |

### 4.insect/ant（7）

| 名称 | define_as | 唯一/rank | 源码 | 出现（频度） | 外观解析 | 裁 | 同类已收录 |
|---|---|---|---|---|---|:-:|---|
| giant green ant | — | —/1 | `general/npcs/ant.lua:71` | old-forest:池E2.7；maze:池E2.3；ritch-tunnels:池E2.3；…共13区 | 显式 green_ant.png | S | giant white ant、giant yellow ant、giant brown ant（共6） |
| giant red ant | — | —/1 | `general/npcs/ant.lua:83` | old-forest:池E2.7；maze:池E2.3；ritch-tunnels:池E2.3；…共13区 | 显式 red_ant.png | S | giant white ant、giant yellow ant、giant brown ant（共6） |
| giant fire ant | — | —/1 | `general/npcs/ant.lua:131` | ardhungol:池E0.9；dreadfell:池E0.8；reknor:池E0.7；…共9区 | 显式 fire_ant.png | S | giant white ant、giant yellow ant、giant brown ant（共6） |
| giant ice ant | — | —/1 | `general/npcs/ant.lua:147` | ardhungol:池E0.9；dreadfell:池E0.8；reknor:池E0.7；…共9区 | 显式 ice_ant.png | S | giant white ant、giant yellow ant、giant brown ant（共6） |
| giant lightning ant | — | —/1 | `general/npcs/ant.lua:164` | ardhungol:池E0.9；dreadfell:池E0.8；reknor:池E0.7；…共9区 | 显式 lightning_ant.png | S | giant white ant、giant yellow ant、giant brown ant（共6） |
| giant acid ant | — | —/1 | `general/npcs/ant.lua:180` | ardhungol:池E0.9；dreadfell:池E0.8；reknor:池E0.7；…共9区 | 显式 acid_ant.png | S | giant white ant、giant yellow ant、giant brown ant（共6） |
| giant army ant | — | —/1 | `general/npcs/ant.lua:196` | ardhungol:池E0.9；dreadfell:池E0.8；reknor:池E0.7；…共8区 | 显式 army_ant.png | S | giant white ant、giant yellow ant、giant brown ant（共6） |

### 4.elemental/temporal（6）

| 名称 | define_as | 唯一/rank | 源码 | 出现（频度） | 外观解析 | 裁 | 同类已收录 |
|---|---|---|---|---|---|:-:|---|
| telugoroth | — | —/2 | `general/npcs/telugoroth.lua:101` | temporal-rift:池E7.4 | 默认名 elemental_temporal_telugoroth.png | S | 无同子类已收录 |
| greater telugoroth | — | —/2 | `general/npcs/telugoroth.lua:115` | temporal-rift:池E3.7 | tall：invis+add_mos→elemental_temporal_greater_telugoroth.png | T | 无同子类已收录 |
| teluvorta | — | —/2 | `general/npcs/telugoroth.lua:154` | temporal-rift:池E3.7 | 默认名 elemental_temporal_teluvorta.png | S | 无同子类已收录 |
| ultimate telugoroth | — | —/3 | `general/npcs/telugoroth.lua:132` | temporal-rift:池E2.5 | tall：invis+add_mos→elemental_temporal_ultimate_telugoroth.png | T | 无同子类已收录 |
| greater teluvorta | — | —/2 | `general/npcs/telugoroth.lua:180` | temporal-rift:池E2.5 | tall：invis+add_mos→elemental_temporal_greater_teluvorta.png | T | 无同子类已收录 |
| ultimate teluvorta | — | —/3 | `general/npcs/telugoroth.lua:207` | temporal-rift:池E1.7 | tall：invis+add_mos→elemental_temporal_ultimate_teluvorta.png | T | 无同子类已收录 |

### 4.horror/aquatic（6）

| 名称 | define_as | 唯一/rank | 源码 | 出现（频度） | 外观解析 | 裁 | 同类已收录 |
|---|---|---|---|---|---|:-:|---|
| swarming horror | — | —/1 | `general/npcs/horror_aquatic.lua:91` | lake-nur:池E2.2 | tall：invis+add_mos→horror_aquatic_swarming_horror.png | T | 无同子类已收录 |
| ravenous horror | — | —/2 | `general/npcs/horror_aquatic.lua:114` | lake-nur:池E2.2 | tall：invis+add_mos→horror_aquatic_ravenous_horror.png | T | 无同子类已收录 |
| entrenched horror | — | —/3 | `general/npcs/horror_aquatic.lua:62` | lake-nur:池E1.5 | tall：invis+add_mos→horror_aquatic_entrenched_horror.png | T | 无同子类已收录 |
| boiling horror | — | —/2 | `general/npcs/horror_aquatic.lua:133` | lake-nur:池E1.1 | tall：invis+add_mos→horror_aquatic_boiling_horror.png | T | 无同子类已收录 |
| swarm hive | — | —/3 | `general/npcs/horror_aquatic.lua:162` | lake-nur:池E0.7 | tall：invis+add_mos→horror_aquatic_swarm_hive.png | T | 无同子类已收录 |
| abyssal horror | — | —/3 | `general/npcs/horror_aquatic.lua:192` | lake-nur:池E0.4 | tall：invis+add_mos→horror_aquatic_abyssal_horror.png | T | 无同子类已收录 |

### 4.humanoid/naga（6）

| 名称 | define_as | 唯一/rank | 源码 | 出现（频度） | 外观解析 | 裁 | 同类已收录 |
|---|---|---|---|---|---|:-:|---|
| naga myrmidon | — | —/2 | `general/npcs/naga.lua:52` | temple-of-creation:池E54.1；ardhungol:池E0.4；unremarkable-cave:池E0.4；…共5区 | 显式 naga_myrmidon.png | S | naga tidewarden、naga tidecaller、Lady Zoisla the Tidebringer |
| naga nereid | — | —/2 | `zones/slazish-fen/npcs.lua:97` | murgol-lair:区内E9.1；slazish-fen:区内E8.5 | tall：invis+add_mos→humanoid_naga_naga_nereid.png | T | naga tidewarden、naga tidecaller、Lady Zoisla the Tidebringer |
| Lady Nashva the Streambender | NASHVA | 唯一/4 | `zones/murgol-lair/npcs.lua:160` | murgol-lair:保证首领(INVASION 布局) | tall：invis+add_mos→humanoid_naga_lady_nashva_the_streambender.png | T | Lady Zoisla the Tidebringer、naga tidewarden、naga tidecaller |
| Slasul | SLASUL | 唯一/4 | `zones/temple-of-creation/npcs.lua:26` | temple-of-creation:保证首领(末层静态图) | tall：invis+add_mos→humanoid_naga_slasul.png | T | Lady Zoisla the Tidebringer、naga tidewarden、naga tidecaller |
| naga tide huntress | — | —/3 | `general/npcs/naga.lua:73` | temple-of-creation:池E11.3 | 显式 naga_tide_huntress.png | S | naga tidewarden、naga tidecaller、Lady Zoisla the Tidebringer |
| naga psyren | — | —/3 | `general/npcs/naga.lua:102` | temple-of-creation:池E8.7 | 显式 naga_psyren.png | S | naga tidewarden、naga tidecaller、Lady Zoisla the Tidebringer |

### 4.undead/vampire（6）

| 名称 | define_as | 唯一/rank | 源码 | 出现（频度） | 外观解析 | 裁 | 同类已收录 |
|---|---|---|---|---|---|:-:|---|
| lesser vampire | — | —/2 | `general/npcs/vampire.lua:64` | dreadfell:池E7.7；ardhungol:池E0.9；ruined-dungeon:池E0.8；…共9区 | 显式 lesser_vampire.png | S | The Master |
| vampire | — | —/2 | `general/npcs/vampire.lua:78` | dreadfell:池E7.7；ardhungol:池E0.9；reknor:池E0.7；…共8区 | 显式 vampire.png | S | The Master |
| master vampire | — | —/2 | `general/npcs/vampire.lua:94` | dreadfell:池E7.7；ardhungol:池E0.9；reknor:池E0.7；…共7区 | tall：invis+add_mos→master_vampire.png | T | The Master |
| elder vampire | — | —/3 | `general/npcs/vampire.lua:112` | dreadfell:池E4.1；ardhungol:池E0.9；reknor:池E0.7；…共6区 | 显式 elder_vampire.png | S | The Master |
| vampire lord | — | —/3 | `general/npcs/vampire.lua:135` | dreadfell:池E0.3 | 显式 vampire_lord.png | S | The Master |
| Arch Zephyr | ARCH_ZEPHYR | 唯一/3.5 | `zones/rak-shor-pride/npcs.lua:304` | rak-shor-pride:区内E0.5 | tall：invis+add_mos→undead_vampire_arch_zephyr.png | T | The Master |

### 4.demon/minor（5）

| 名称 | define_as | 唯一/rank | 源码 | 出现（频度） | 外观解析 | 裁 | 同类已收录 |
|---|---|---|---|---|---|:-:|---|
| onilug | — | —/3 | `general/npcs/minor-demon.lua:91` | valley-moon-caverns:池E13.9；demon-plane:池E9.6；crypt-kryl-feijan:池E2.1；…共12区 | tall：invis+add_mos→demon_minor_onilug.png | T | 无同子类已收录 |
| wretchling | — | —/2 | `general/npcs/minor-demon.lua:66` | valley-moon-caverns:池E13.9；demon-plane:池E9.6；crypt-kryl-feijan:池E2.1；…共11区 | 默认名 demon_minor_wretchling.png | S | 无同子类已收录 |
| quasit | — | —/2 | `general/npcs/minor-demon.lua:122` | valley-moon-caverns:池E13.9；demon-plane:池E9.6；crypt-kryl-feijan:池E2.1；…共10区 | 默认名 demon_minor_quasit.png | S | 无同子类已收录 |
| Draebor, the Imp | DRAEBOR | 唯一/4 | `zones/demon-plane/npcs.lua:26` | demon-plane:保证首领 | 默认名 demon_minor_draebor__the_imp.png | S | 无同子类已收录 |
| fire imp | — | —/2 | `general/npcs/minor-demon.lua:47` | valley-moon-caverns:池E4.6；demon-plane:池E3.2；crypt-kryl-feijan:池E1.6；…共4区 | 默认名 demon_minor_fire_imp.png | S | 无同子类已收录 |

### 4.horror/corrupted（5）

| 名称 | define_as | 唯一/rank | 源码 | 出现（频度） | 外观解析 | 裁 | 同类已收录 |
|---|---|---|---|---|---|:-:|---|
| drem | — | —/2 | `general/npcs/horror-corrupted.lua:44` | deep-bellow:池E16.6；maze:池E10.3 | 显式 horror_corrupted_dremling.png | S | Horned Horror、The Mouth、The Abomination（共5） |
| brecklorn | — | —/2 | `general/npcs/horror-corrupted.lua:160` | deep-bellow:池E8.3；maze:池E5.2 | 默认名 horror_corrupted_brecklorn.png | S | Horned Horror、The Mouth、The Abomination（共5） |
| grannor'vor | — | —/2 | `general/npcs/horror-corrupted.lua:188` | deep-bellow:池E6.8；maze:池E5.2 | 默认名 horror_corrupted_grannor_vor.png | S | Horned Horror、The Mouth、The Abomination（共5） |
| drem master | — | —/2 | `general/npcs/horror-corrupted.lua:116` | deep-bellow:池E4.5；maze:池E3.4 | 默认名 horror_corrupted_drem_master.png | S | Horned Horror、The Mouth、The Abomination（共5） |
| grannor'vin | — | —/2 | `general/npcs/horror-corrupted.lua:216` | deep-bellow:池E3.4；maze:池E2.6 | 默认名 horror_corrupted_grannor_vin.png | S | Horned Horror、The Mouth、The Abomination（共5） |

### 4.humanoid/yaech（5）

| 名称 | define_as | 唯一/rank | 源码 | 出现（频度） | 外观解析 | 裁 | 同类已收录 |
|---|---|---|---|---|---|:-:|---|
| yaech diver | — | —/2 | `general/npcs/yaech.lua:48` | murgol-lair:池E15.0 | 默认名 humanoid_yaech_yaech_diver.png | S | 无同子类已收录 |
| Murgol, the Yaech Lord | MURGOL | 唯一/4 | `zones/murgol-lair/npcs.lua:25` | murgol-lair:保证首领(非 INVASION 布局) | 默认名 humanoid_yaech_murgol__the_yaech_lord.png | S | 无同子类已收录 |
| yaech hunter | — | —/2 | `general/npcs/yaech.lua:63` | murgol-lair:池E7.5 | 默认名 humanoid_yaech_yaech_hunter.png | S | 无同子类已收录 |
| yaech mindslayer | — | —/2 | `general/npcs/yaech.lua:79` | murgol-lair:池E7.1 | 默认名 humanoid_yaech_yaech_mindslayer.png | S | 无同子类已收录 |
| yaech psion | — | —/2 | `general/npcs/yaech.lua:97` | murgol-lair:池E4.7 | 默认名 humanoid_yaech_yaech_psion.png | S | 无同子类已收录 |

### 4.undead/ghoul（5）

| 名称 | define_as | 唯一/rank | 源码 | 出现（频度） | 外观解析 | 裁 | 同类已收录 |
|---|---|---|---|---|---|:-:|---|
| ghoul | GHOUL | —/2 | `general/npcs/ghoul.lua:49` | dreadfell:池E15.4；telmur:池E10.6；halfling-ruins:池E8.5；…共13区 | 默认名 undead_ghoul_ghoul.png | S | 无同子类已收录 |
| ghast | — | —/2 | `general/npcs/ghoul.lua:66` | dreadfell:池E7.7；halfling-ruins:池E5.1；telmur:池E3.5；…共5区 | 默认名 undead_ghoul_ghast.png | S | 无同子类已收录 |
| ghoulking | — | —/3 | `general/npcs/ghoul.lua:87` | dreadfell:池E4.4；halfling-ruins:池E2.9；telmur:池E1.8；…共4区 | 默认名 undead_ghoul_ghoulking.png | S | 无同子类已收录 |
| Borfast the Broken | BORFAST | 唯一/3.5 | `zones/dreadfell/npcs.lua:210` | dreadfell:稀有唯一(池 rarity 50) | 默认名 undead_ghoul_borfast_the_broken.png | S | 无同子类已收录 |
| Rotting Titan | ROTTING_TITAN | 唯一/3.5 | `zones/rak-shor-pride/npcs.lua:119` | rak-shor-pride:区内E0.5 | tall：invis+add_mos→undead_ghoul_rotting_titan.png | T | 无同子类已收录 |

### 4.undead/giant（5）

| 名称 | define_as | 唯一/rank | 源码 | 出现（频度） | 外观解析 | 裁 | 同类已收录 |
|---|---|---|---|---|---|:-:|---|
| bone giant | — | —/2 | `general/npcs/bone-giant.lua:59` | rak-shor-pride:池E13.4；telmur:池E2.7；vor-armoury:池E2.4 | tall：invis+add_mos→undead_giant_bone_giant.png | T | Half-Finished Bone Giant |
| eternal bone giant | — | —/2 | `general/npcs/bone-giant.lua:71` | rak-shor-pride:池E4.5；telmur:池E1.8；vor-armoury:池E1.7 | tall：invis+add_mos→undead_giant_eternal_bone_giant.png | T | Half-Finished Bone Giant |
| heavy bone giant | — | —/2 | `general/npcs/bone-giant.lua:85` | rak-shor-pride:池E4.0；telmur:池E1.7；vor-armoury:池E1.1 | tall：invis+add_mos→undead_giant_heavy_bone_giant.png | T | Half-Finished Bone Giant |
| runed bone giant | — | —/3 | `general/npcs/bone-giant.lua:97` | rak-shor-pride:池E2.4 | tall：invis+add_mos→undead_giant_runed_bone_giant.png | T | Half-Finished Bone Giant |
| Heavy Sentinel | HEAVY_SENTINEL | 唯一/3.5 | `zones/rak-shor-pride/npcs.lua:258` | rak-shor-pride:区内E0.5 | tall：invis+add_mos→undead_giant_heavy_sentinel.png | T | Half-Finished Bone Giant |

### 4.undead/mummy（5）

| 名称 | define_as | 唯一/rank | 源码 | 出现（频度） | 外观解析 | 裁 | 同类已收录 |
|---|---|---|---|---|---|:-:|---|
| Greater Mummy Lord | GREATER_MUMMY_LORD | 唯一/4 | `zones/ancient-elven-ruins/npcs.lua:35` | ancient-elven-ruins:保证首领 | 默认名 undead_mummy_greater_mummy_lord.png | S | 无同子类已收录 |
| ancient elven mummy | — | —/2 | `zones/ancient-elven-ruins/npcs.lua:107` | ancient-elven-ruins:区内E11.3 | 默认名 undead_mummy_ancient_elven_mummy.png | S | 无同子类已收录 |
| rotting mummy | — | —/2 | `zones/ancient-elven-ruins/npcs.lua:154` | ancient-elven-ruins:区内E5.7 | 默认名 undead_mummy_rotting_mummy.png | S | 无同子类已收录 |
| animated mummy wrappings | — | —/2 | `zones/ancient-elven-ruins/npcs.lua:130` | ancient-elven-ruins:区内E2.8 | 显式 object/mummy_wrappings.png | S | 无同子类已收录 |
| greater mummy | GREATER_MUMMY | —/3 | `zones/ancient-elven-ruins/npcs.lua:176` | ancient-elven-ruins:区内E1.4 | 显式 undead_mummy_greater_mummy.png | S | 无同子类已收录 |

### 4.animal/bear（4）

| 名称 | define_as | 唯一/rank | 源码 | 出现（频度） | 外观解析 | 裁 | 同类已收录 |
|---|---|---|---|---|---|:-:|---|
| cave bear | — | —/2 | `general/npcs/bear.lua:72` | old-forest:池E2.0；noxious-caldera:池E1.8；scintillating-caves:池E1.0；…共7区 | 显式 cave_bear.png | S | brown bear、black bear、Norgos, the Frozen（共4） |
| war bear | — | —/2 | `general/npcs/bear.lua:83` | old-forest:池E2.0；noxious-caldera:池E1.8；scintillating-caves:池E1.0；…共7区 | 显式 war_bear.png | S | brown bear、black bear、Norgos, the Frozen（共4） |
| grizzly bear | — | —/2 | `general/npcs/bear.lua:94` | old-forest:池E1.4；noxious-caldera:池E1.4 | tall：invis+add_mos→grizzly_bear.png | T | brown bear、black bear、Norgos, the Frozen（共4） |
| polar bear | — | —/2 | `general/npcs/bear.lua:106` | noxious-caldera:池E0.9；old-forest:池E0.9 | 显式 polar_bear.png | S | brown bear、black bear、Norgos, the Frozen（共4） |

### 4.demon/major（4）

| 名称 | define_as | 唯一/rank | 源码 | 出现（频度） | 外观解析 | 裁 | 同类已收录 |
|---|---|---|---|---|---|:-:|---|
| dolleg | — | —/2 | `general/npcs/major-demon.lua:50` | valley-moon-caverns:池E3.5；demon-plane:池E3.2；ardhungol:池E0.4；…共6区 | tall：invis+add_mos→demon_major_dolleg.png | T | Kryl-Feijan、Lithfengel、Harkor'Zun |
| dúathedlen | — | —/2 | `general/npcs/major-demon.lua:73` | valley-moon-caverns:池E3.5；demon-plane:池E3.2；ardhungol:池E0.4；…共6区 | tall 内层 demon_major_duathedlen.png（≠默认名） | I | Kryl-Feijan、Lithfengel、Harkor'Zun |
| uruivellas | — | —/3 | `general/npcs/major-demon.lua:95` | valley-moon-caverns:池E1.9；demon-plane:池E1.5 | tall：invis+add_mos→demon_major_uruivellas.png | T | Kryl-Feijan、Lithfengel、Harkor'Zun |
| thaurhereg | — | —/3 | `general/npcs/major-demon.lua:128` | valley-moon-caverns:池E1.9；demon-plane:池E1.5 | tall：invis+add_mos→demon_major_thaurhereg.png | T | Kryl-Feijan、Lithfengel、Harkor'Zun |

### 4.elemental/fire（4）

| 名称 | define_as | 唯一/rank | 源码 | 出现（频度） | 外观解析 | 裁 | 同类已收录 |
|---|---|---|---|---|---|:-:|---|
| faeros | — | —/2 | `general/npcs/faeros.lua:56` | charred-scar:池E10.4；mark-spellblaze:池E9.1；noxious-caldera:池E5.4；…共5区 | 默认名 elemental_fire_faeros.png | S | 无同子类已收录 |
| Fyrk, Faeros High Guard | FYRK | 唯一/5 | `zones/charred-scar/npcs.lua:271` | charred-scar:任务首领 | tall：invis+add_mos→elemental_fire_fyrk__faeros_high_guard.png | T | 无同子类已收录 |
| greater faeros | — | —/2 | `general/npcs/faeros.lua:70` | charred-scar:池E3.5；noxious-caldera:池E1.8；mark-spellblaze:池E0.4 | 默认名 elemental_fire_greater_faeros.png | S | 无同子类已收录 |
| ultimate faeros | — | —/3 | `general/npcs/faeros.lua:86` | charred-scar:池E2.0 | tall：invis+add_mos→elemental_fire_ultimate_faeros.png | T | 无同子类已收录 |

### 4.giant/ice（4）

| 名称 | define_as | 唯一/rank | 源码 | 出现（频度） | 外观解析 | 裁 | 同类已收录 |
|---|---|---|---|---|---|:-:|---|
| snow giant | — | —/2 | `general/npcs/snow-giant.lua:51` | daikara:池E26.4；tempest-peak:池E12.8；ardhungol:池E0.9；…共9区 | tall：invis+add_mos→giant_ice_snow_giant.png | T | Burb the snow giant champion |
| snow giant thunderer | — | —/2 | `general/npcs/snow-giant.lua:63` | tempest-peak:池E4.3；daikara:池E3.3；ardhungol:池E0.3 | tall：invis+add_mos→giant_ice_snow_giant_thunderer.png | T | Burb the snow giant champion |
| snow giant boulder thrower | — | —/2 | `general/npcs/snow-giant.lua:76` | tempest-peak:池E4.3；daikara:池E1.5；ardhungol:池E0.3 | tall：invis+add_mos→giant_ice_snow_giant_boulder_thrower.png | T | Burb the snow giant champion |
| snow giant chieftain | — | —/3 | `general/npcs/snow-giant.lua:88` | tempest-peak:池E1.8；daikara:池E0.6 | tall：invis+add_mos→giant_ice_snow_giant_chieftain.png | T | Burb the snow giant champion |

### 4.humanoid/thalore（4）

| 名称 | define_as | 唯一/rank | 源码 | 出现（频度） | 外观解析 | 裁 | 同类已收录 |
|---|---|---|---|---|---|:-:|---|
| Mindworm | MINDWORM | 唯一/3.5 | `zones/noxious-caldera/npcs.lua:37` | noxious-caldera:保证首领(第 2 层) | 默认名 humanoid_thalore_mindworm.png | S | 无同子类已收录 |
| Berethh | BERETHH | 唯一/4 | `zones/keepsake-meadow/npcs.lua:388` | keepsake-meadow:任务同伴 | 默认名 humanoid_thalore_berethh.png | S | 无同子类已收录 |
| Companion Warrior | BERETHH_WARRIOR | —/2 | `zones/keepsake-meadow/npcs.lua:273` | keepsake-meadow:任务同伴 | 显式 humanoid_elenulach_thief.png | S | 无同子类已收录 |
| Companion Archer | BERETHH_ARCHER | —/2 | `zones/keepsake-meadow/npcs.lua:296` | keepsake-meadow:任务同伴 | 显式 humanoid_elf_elven_archer.png | S | 无同子类已收录 |

### 4.immovable/crystal（4）

| 名称 | define_as | 唯一/rank | 源码 | 出现（频度） | 外观解析 | 裁 | 同类已收录 |
|---|---|---|---|---|---|:-:|---|
| black crystal | — | —/2 | `general/npcs/crystal.lua:119` | scintillating-caves:池E4.4；old-forest:池E4.1 | 显式 crystal_black.png | S | white crystal、red crystal、crimson crystal（共5） |
| blue crystal | — | —/2 | `general/npcs/crystal.lua:141` | scintillating-caves:池E2.6；old-forest:池E2.0 | 显式 crystal_blue.png | S | white crystal、red crystal、crimson crystal（共5） |
| multi-hued crystal | — | —/2 | `general/npcs/crystal.lua:152` | old-forest:池E1.8 | 见 §5 | K | white crystal、red crystal、crimson crystal（共5） |
| shimmering crystal | — | —/2 | `general/npcs/crystal.lua:167` | old-forest:池E1.4 | 见 §5 | K | white crystal、red crystal、crimson crystal（共5） |

### 4.undead/horror（4）

| 名称 | define_as | 唯一/rank | 源码 | 出现（频度） | 外观解析 | 裁 | 同类已收录 |
|---|---|---|---|---|---|:-:|---|
| necrotic mass | — | —/1 | `general/npcs/horror-undead.lua:46` | rak-shor-pride:池E2.7 | tall：invis+add_mos→undead_horror_necrotic_mass.png | T | fleshy experiment、boney experiment、sanguine experiment |
| necrotic abomination | — | —/3 | `general/npcs/horror-undead.lua:61` | rak-shor-pride:池E1.7 | tall：invis+add_mos→undead_horror_necrotic_abomination.png | T | fleshy experiment、boney experiment、sanguine experiment |
| bone horror | — | —/3 | `general/npcs/horror-undead.lua:105` | rak-shor-pride:池E1.7 | tall：invis+add_mos→undead_horror_bone_horror.png | T | fleshy experiment、boney experiment、sanguine experiment |
| sanguine horror | — | —/3 | `general/npcs/horror-undead.lua:150` | rak-shor-pride:池E1.7 | tall：invis+add_mos→undead_horror_sanguine_horror.png | T | sanguine experiment、fleshy experiment、boney experiment |

### 4.undead/skeleton（4）

| 名称 | define_as | 唯一/rank | 源码 | 出现（频度） | 外观解析 | 裁 | 同类已收录 |
|---|---|---|---|---|---|:-:|---|
| skeleton magus | — | —/2 | `general/npcs/skeleton.lua:128` | dreadfell:池E10.3；halfling-ruins:池E7.8；telmur:池E3.5；…共7区 | 默认名 undead_skeleton_skeleton_magus.png | S | degenerated skeleton warrior、degenerated skeleton archer、skeleton mage（共8） |
| The Shade | SHADE | 唯一/4 | `zones/ruins-kor-pul/npcs.lua:41` | ruins-kor-pul:保证首领(DEFAULT 布局末层) | 见 §5 | K | degenerated skeleton warrior、degenerated skeleton archer、skeleton mage（共8） |
| skeleton assassin | — | —/3 | `general/npcs/skeleton.lua:193` | dreadfell:池E2.1；telmur:池E0.7；rak-shor-pride:池E0.7；…共5区 | 默认名 undead_skeleton_skeleton_assassin.png | S | degenerated skeleton warrior、degenerated skeleton archer、skeleton mage（共8） |
| Filio Flightfond | FILIO | 唯一/3.5 | `zones/dreadfell/npcs.lua:358` | dreadfell:区内E0.6 | 默认名 undead_skeleton_filio_flightfond.png | S | degenerated skeleton warrior、degenerated skeleton archer、skeleton mage（共8） |

### 4.undead/wight（4）

| 名称 | define_as | 唯一/rank | 源码 | 出现（频度） | 外观解析 | 裁 | 同类已收录 |
|---|---|---|---|---|---|:-:|---|
| forest wight | — | —/2 | `general/npcs/wight.lua:65` | dreadfell:池E7.7；ardhungol:池E0.9；reknor:池E0.7；…共8区 | 显式 forest_wight.png | S | 无同子类已收录 |
| grave wight | — | —/2 | `general/npcs/wight.lua:79` | dreadfell:池E6.4；ardhungol:池E0.9；reknor:池E0.7；…共6区 | 显式 grave_wight.png | S | 无同子类已收录 |
| barrow wight | — | —/2 | `general/npcs/wight.lua:92` | dreadfell:池E1.3；ardhungol:池E0.4 | tall：invis+add_mos→barrow_wight.png | T | 无同子类已收录 |
| Void Spectre | — | 唯一/3.5 | `zones/rak-shor-pride/npcs.lua:355` | rak-shor-pride:区内E0.5 | tall：invis+add_mos→undead_wight_void_spectre.png | T | 无同子类已收录 |

### 4.vermin/oozes（4）

| 名称 | define_as | 唯一/rank | 源码 | 出现（频度） | 外观解析 | 裁 | 同类已收录 |
|---|---|---|---|---|---|:-:|---|
| white ooze | — | —/1 | `general/npcs/ooze.lua:85` | sandworm-lair:池E4.4；conclave-vault:池E4.1；maze:池E2.9；…共16区 | 默认名 vermin_oozes_white_ooze.png | S | black ooze、yellow ooze、red ooze（共7） |
| slimy ooze | — | —/2 | `general/npcs/ooze.lua:150` | conclave-vault:池E4.8；ardhungol:池E0.9；reknor:池E0.7；…共7区 | 默认名 vermin_oozes_slimy_ooze.png | S | black ooze、yellow ooze、red ooze（共7） |
| poison ooze | — | —/2 | `general/npcs/ooze.lua:164` | conclave-vault:池E4.8；ardhungol:池E0.9；reknor:池E0.7；…共7区 | 默认名 vermin_oozes_poison_ooze.png | S | black ooze、yellow ooze、red ooze（共7） |
| brittle clear ooze | — | —/2 | `general/npcs/ooze.lua:138` | conclave-vault:池E0.5 | 默认名 vermin_oozes_brittle_clear_ooze.png | S | black ooze、yellow ooze、red ooze（共7） |

### 4.vermin/sandworm（4）

| 名称 | define_as | 唯一/rank | 源码 | 出现（频度） | 外观解析 | 裁 | 同类已收录 |
|---|---|---|---|---|---|:-:|---|
| gigantic sandworm tunneler | — | —/2 | `general/npcs/sandworm.lua:87` | briagh-lair:池E13.6；sandworm-lair:池E13.1；daikara:池E0.6；…共7区 | tall：invis+add_mos→vermin_sandworm_gigantic_sandworm_tunneler.png | T | sandworm、sandworm destroyer、sandworm burrower（共4） |
| gigantic corrosive tunneler | — | —/2 | `general/npcs/sandworm.lua:134` | briagh-lair:池E9.1；sandworm-lair:池E8.7；daikara:池E0.4；…共4区 | tall：invis+add_mos→vermin_sandworm_gigantic_corrosive_tunneler.png | T | Sandworm Queen、sandworm、sandworm destroyer（共4） |
| gigantic gravity worm | — | —/2 | `general/npcs/sandworm.lua:113` | briagh-lair:池E5.5；sandworm-lair:池E5.2 | tall：invis+add_mos→vermin_sandworm_gigantic_gravity_worm.png | T | Sandworm Queen、sandworm、sandworm destroyer（共4） |
| huge sandworm burrower | SANDWORM_TUNNELER_HUGE | —/5 | `zones/sandworm-lair/npcs.lua:57` | sandworm-lair:脚本引路体 | 见 §5 | K | sandworm burrower、sandworm、sandworm destroyer（共4） |

### 4.animal/canine（3）

| 名称 | define_as | 唯一/rank | 源码 | 出现（频度） | 外观解析 | 裁 | 同类已收录 |
|---|---|---|---|---|---|:-:|---|
| The Withering Thing | WITHERING_THING | 唯一/4 | `zones/heart-gloom/npcs.lua:59` | heart-gloom:保证首领(非净化布局) | 默认名 animal_canine_the_withering_thing.png | S | wolf、great wolf、fox（共6） |
| corrupted war dog | CORRUPTED_WAR_DOG | —/1 | `zones/keepsake-meadow/npcs.lua:118` | keepsake-meadow:区内E12.5 | 显式 canine_dw.png | S | wolf、great wolf、fox（共6） |
| war dog | WAR_DOG | —/1 | `zones/keepsake-meadow/npcs.lua:104` | keepsake-meadow:洞穴入口/末层静态摆放 | 显式 canine_dw.png | S | wolf、great wolf、fox（共6） |

### 4.construct/golem（3）

| 名称 | define_as | 唯一/rank | 源码 | 出现（频度） | 外观解析 | 裁 | 同类已收录 |
|---|---|---|---|---|---|:-:|---|
| broken golem | — | —/2 | `general/npcs/construct.lua:58` | golem-graveyard:池E3.1 | 默认名 construct_golem_broken_golem.png | S | Atamathon the Giant Golem |
| golem | — | —/2 | `general/npcs/construct.lua:75` | golem-graveyard:池E3.1 | 默认名 construct_golem_golem.png | S | Atamathon the Giant Golem |
| alchemist golem | — | —/3 | `general/npcs/construct.lua:93` | golem-graveyard:池E0.8 | 默认名 construct_golem_alchemist_golem.png | S | Atamathon the Giant Golem |

### 4.dragon/fire（3）

| 名称 | define_as | 唯一/rank | 源码 | 出现（频度） | 外观解析 | 裁 | 同类已收录 |
|---|---|---|---|---|---|:-:|---|
| fire drake hatchling | FIRE_DRAKE_HATCHLING | —/1 | `general/npcs/fire-drake.lua:46` | daikara:池E11.1；charred-scar:池E10.4；ardhungol:池E0.9；…共10区 | 默认名 dragon_fire_fire_drake_hatchling.png | S | Varsha the Writhing |
| fire drake | — | —/2 | `general/npcs/fire-drake.lua:62` | charred-scar:池E3.5；daikara:池E2.0；ardhungol:池E0.3 | 默认名 dragon_fire_fire_drake.png | S | Varsha the Writhing |
| fire wyrm | — | —/3 | `general/npcs/fire-drake.lua:84` | charred-scar:池E2.1 | tall：invis+add_mos→dragon_fire_fire_wyrm.png | T | Varsha the Writhing |

### 4.dragon/venom（3）

| 名称 | define_as | 唯一/rank | 源码 | 出现（频度） | 外观解析 | 裁 | 同类已收录 |
|---|---|---|---|---|---|:-:|---|
| venom drake hatchling | — | —/1 | `general/npcs/venom-drake.lua:46` | noxious-caldera:池E5.4；ardhungol:池E0.9；daikara:池E0.9；…共10区 | 默认名 dragon_venom_venom_drake_hatchling.png | S | 无同子类已收录 |
| venom drake | — | —/2 | `general/npcs/venom-drake.lua:62` | noxious-caldera:池E1.8；ardhungol:池E0.3 | 默认名 dragon_venom_venom_drake.png | S | 无同子类已收录 |
| venom wyrm | — | —/3 | `general/npcs/venom-drake.lua:84` | noxious-caldera:池E1.1 | tall：invis+add_mos→dragon_venom_venom_wyrm.png | T | 无同子类已收录 |

### 4.elemental/air（3）

| 名称 | define_as | 唯一/rank | 源码 | 出现（频度） | 外观解析 | 裁 | 同类已收录 |
|---|---|---|---|---|---|:-:|---|
| gwelgoroth | — | —/2 | `general/npcs/gwelgoroth.lua:55` | tempest-peak:池E12.8；mark-spellblaze:池E10.1；ruined-dungeon:池E0.8 | 默认名 elemental_air_gwelgoroth.png | S | 无同子类已收录 |
| greater gwelgoroth | — | —/2 | `general/npcs/gwelgoroth.lua:69` | mark-spellblaze:池E6.1；tempest-peak:池E4.3 | tall：invis+add_mos→elemental_air_greater_gwelgoroth.png | T | 无同子类已收录 |
| ultimate gwelgoroth | — | —/3 | `general/npcs/gwelgoroth.lua:86` | mark-spellblaze:池E4.3；tempest-peak:池E2.6 | tall：invis+add_mos→elemental_air_ultimate_gwelgoroth.png | T | 无同子类已收录 |

### 4.elemental/void（3）

| 名称 | define_as | 唯一/rank | 源码 | 出现（频度） | 外观解析 | 裁 | 同类已收录 |
|---|---|---|---|---|---|:-:|---|
| losgoroth | — | —/2 | `general/npcs/losgoroth.lua:59` | abashed-expanse:池E43.8 | 默认名 elemental_void_losgoroth.png | S | 无同子类已收录 |
| manaworm | — | —/2 | `general/npcs/losgoroth.lua:72` | abashed-expanse:池E20.0 | 默认名 elemental_void_manaworm.png | S | 无同子类已收录 |
| Spacial Disturbance | SPACIAL_DISTURBANCE | 唯一/4 | `zones/abashed-expanse/npcs.lua:31` | abashed-expanse:保证首领 | 见 §5 | K | 无同子类已收录 |

### 4.elemental/xorn（3）

| 名称 | define_as | 唯一/rank | 源码 | 出现（频度） | 外观解析 | 裁 | 同类已收录 |
|---|---|---|---|---|---|:-:|---|
| umber hulk | — | —/2 | `general/npcs/xorn.lua:59` | daikara:池E5.3；tempest-peak:池E4.3；ardhungol:池E0.9；…共9区 | 默认名 elemental_xorn_umber_hulk.png | S | The Fragmented Essence of Harkor'Zun |
| xorn | — | —/2 | `general/npcs/xorn.lua:70` | tempest-peak:池E4.3；ardhungol:池E0.9；daikara:池E0.9；…共9区 | 默认名 elemental_xorn_xorn.png | S | The Fragmented Essence of Harkor'Zun |
| xaren | — | —/2 | `general/npcs/xorn.lua:81` | tempest-peak:池E2.6；daikara:池E0.6；ardhungol:池E0.3 | 默认名 elemental_xorn_xaren.png | S | The Fragmented Essence of Harkor'Zun |

### 4.giant/troll（3）

| 名称 | define_as | 唯一/rank | 源码 | 出现（频度） | 外观解析 | 裁 | 同类已收录 |
|---|---|---|---|---|---|:-:|---|
| mountain troll | — | —/2 | `general/npcs/troll.lua:84` | reknor:池E9.2；ardhungol:池E0.3 | 显式 troll_m.png | S | forest troll、stone troll、cave troll（共6） |
| mountain troll thunderer | — | —/3 | `general/npcs/troll.lua:94` | reknor:池E5.4 | 显式 troll_mt.png | S | forest troll、stone troll、cave troll（共6） |
| Forest Troll Hedge-Wizard | — | 唯一/3.5 | `general/npcs/troll.lua:145` | reknor:池E0.7 | tall：invis+add_mos→giant_troll_forest_troll_hedge_wizard.png | T | Bill the Stone Troll、forest troll、stone troll（共6） |

### 4.insect/ritch（3）

| 名称 | define_as | 唯一/rank | 源码 | 出现（频度） | 外观解析 | 裁 | 同类已收录 |
|---|---|---|---|---|---|:-:|---|
| ritch flamespitter | — | —/2 | `zones/ritch-tunnels/npcs.lua:53` | ritch-tunnels:区内E11.3 | 默认名 insect_ritch_ritch_flamespitter.png | S | Ritch Great Hive Mother |
| chitinous ritch | — | —/2 | `zones/ritch-tunnels/npcs.lua:84` | ritch-tunnels:区内E11.3 | 默认名 insect_ritch_chitinous_ritch.png | S | Ritch Great Hive Mother |
| ritch impaler | — | —/2 | `zones/ritch-tunnels/npcs.lua:69` | ritch-tunnels:区内E9.1 | 默认名 insect_ritch_ritch_impaler.png | S | Ritch Great Hive Mother |

### 4.undead/shadow（3）

| 名称 | define_as | 唯一/rank | 源码 | 出现（频度） | 外观解析 | 裁 | 同类已收录 |
|---|---|---|---|---|---|:-:|---|
| shadow claw | SHADOW_CLAW | —/2 | `zones/keepsake-meadow/npcs.lua:171` | keepsake-meadow:区内E12.5 | 见 §5 | N | 无同子类已收录 |
| shadow stalker | SHADOW_STALKER | —/2 | `zones/keepsake-meadow/npcs.lua:193` | keepsake-meadow:区内E12.5 | 显式 shadow-stalker.png | S | 无同子类已收录 |
| shadow claw | SHADOW_CASTER | —/2 | `zones/keepsake-meadow/npcs.lua:226` | keepsake-meadow:区内E12.5 | 见 §5 | N | 无同子类已收录 |

### 4.animal/snake（2）

| 名称 | define_as | 唯一/rank | 源码 | 出现（频度） | 外观解析 | 裁 | 同类已收录 |
|---|---|---|---|---|---|:-:|---|
| black mamba | — | —/2 | `general/npcs/snake.lua:102` | noxious-caldera:池E1.4；unremarkable-cave:池E0.9；lake-nur:池E0.4 | 显式 darkgrey-snake.png | S | large brown snake、king cobra、large white snake（共5） |
| anaconda | — | —/3 | `general/npcs/snake.lua:115` | noxious-caldera:池E1.1；unremarkable-cave:池E0.7 | 显式 yellow-green-snake.png | S | large brown snake、king cobra、large white snake（共5） |

### 4.aquatic/critter（2）

| 名称 | define_as | 唯一/rank | 源码 | 出现（频度） | 外观解析 | 裁 | 同类已收录 |
|---|---|---|---|---|---|:-:|---|
| squid | — | —/1 | `general/npcs/aquatic_critter.lua:90` | flooded-cave:池E17.3；murgol-lair:池E15.0；temple-of-creation:池E9.0；…共4区 | 默认名 aquatic_critter_squid.png | S | giant eel、dragon turtle、electric eel（共4） |
| ink squid | — | —/1 | `general/npcs/aquatic_critter.lua:99` | flooded-cave:池E8.6；temple-of-creation:池E7.7；murgol-lair:池E7.5；…共4区 | 默认名 aquatic_critter_ink_squid.png | S | giant eel、dragon turtle、electric eel（共4） |

### 4.aquatic/demon（2）

| 名称 | define_as | 唯一/rank | 源码 | 出现（频度） | 外观解析 | 裁 | 同类已收录 |
|---|---|---|---|---|---|:-:|---|
| water imp | — | —/2 | `general/npcs/aquatic_demon.lua:44` | flooded-cave:池E17.3；lake-nur:池E7.7；temple-of-creation:池E6.8 | 默认名 aquatic_demon_water_imp.png | S | 无同子类已收录 |
| Walrog | — | 唯一/3.5 | `general/npcs/aquatic_demon.lua:61` | temple-of-creation:池E0.8；flooded-cave:池E0.3 | tall：invis+add_mos→aquatic_demon_walrog.png | T | 无同子类已收录 |

### 4.dragon/cold（2）

| 名称 | define_as | 唯一/rank | 源码 | 出现（频度） | 外观解析 | 裁 | 同类已收录 |
|---|---|---|---|---|---|:-:|---|
| cold drake hatchling | — | —/1 | `general/npcs/cold-drake.lua:46` | daikara:池E7.5；ardhungol:池E0.9；ruined-dungeon:池E0.8；…共9区 | 默认名 dragon_cold_cold_drake_hatchling.png | S | 无同子类已收录 |
| cold drake | NPC_COLD_DRAKE | —/2 | `general/npcs/cold-drake.lua:65` | daikara:池E1.5；ardhungol:池E0.3 | 默认名 dragon_cold_cold_drake.png | S | 无同子类已收录 |

### 4.dragon/multihued（2）

| 名称 | define_as | 唯一/rank | 源码 | 出现（频度） | 外观解析 | 裁 | 同类已收录 |
|---|---|---|---|---|---|:-:|---|
| multi-hued drake hatchling | — | —/1 | `general/npcs/multihued-drake.lua:46` | ardhungol:池E0.9；dreadfell:池E0.8；reknor:池E0.7；…共8区 | tall 内层 dragon_multihued_multi_hued_drake_hatchling.png（≠默认名） | I | 无同子类已收录 |
| multi-hued drake | — | —/2 | `general/npcs/multihued-drake.lua:67` | ardhungol:池E0.3 | tall 内层 dragon_multihued_multi_hued_drake.png（≠默认名） | I | 无同子类已收录 |

### 4.dragon/sand（2）

| 名称 | define_as | 唯一/rank | 源码 | 出现（频度） | 外观解析 | 裁 | 同类已收录 |
|---|---|---|---|---|---|:-:|---|
| sand-drake | — | —/3 | `general/npcs/sandworm.lua:69` | briagh-lair:池E5.5；sandworm-lair:池E5.2 | 默认名 dragon_sand_sand_drake.png | S | Corrupted Sand Wyrm |
| Briagh, Great Sand Wyrm | BRIAGH | 唯一/4 | `zones/briagh-lair/npcs.lua:25` | briagh-lair:保证首领 | tall：invis+add_mos→dragon_sand_briagh__great_sand_wyrm.png | T | Corrupted Sand Wyrm |

### 4.dragon/storm（2）

| 名称 | define_as | 唯一/rank | 源码 | 出现（频度） | 外观解析 | 裁 | 同类已收录 |
|---|---|---|---|---|---|:-:|---|
| storm drake hatchling | — | —/1 | `general/npcs/storm-drake.lua:46` | tempest-peak:池E6.4；ardhungol:池E0.9；daikara:池E0.9；…共9区 | 默认名 dragon_storm_storm_drake_hatchling.png | S | 无同子类已收录 |
| storm drake | — | —/2 | `general/npcs/storm-drake.lua:62` | tempest-peak:池E3.2；ardhungol:池E0.3 | 默认名 dragon_storm_storm_drake.png | S | 无同子类已收录 |

### 4.structure/vat（2）

| 名称 | define_as | 唯一/rank | 源码 | 出现（频度） | 外观解析 | 裁 | 同类已收录 |
|---|---|---|---|---|---|:-:|---|
| old vats | VAT1 | —/2 | `zones/conclave-vault/npcs.lua:42` | conclave-vault:区内E0.0 | 见 §5 | N | 无同子类已收录 |
| old vats | VAT2 | —/2 | `zones/conclave-vault/npcs.lua:51` | conclave-vault:区内E0.0 | 见 §5 | N | 无同子类已收录 |

### 4.animal/feline（1）

| 名称 | define_as | 唯一/rank | 源码 | 出现（频度） | 外观解析 | 裁 | 同类已收录 |
|---|---|---|---|---|---|:-:|---|
| Pumpkin, the little kitty | KITTY | 唯一/2 | `zones/shertul-fortress/npcs.lua:176` | shertul-fortress:据点宠物 | 显式 sage_kitty.png | S | 无同子类已收录 |

### 4.dragon/temporal（1）

| 名称 | define_as | 唯一/rank | 源码 | 出现（频度） | 外观解析 | 裁 | 同类已收录 |
|---|---|---|---|---|---|:-:|---|
| Rantha the Abomination | ABOMINATION_RANTHA | 唯一/3.5 | `zones/temporal-rift/npcs.lua:73` | temporal-rift:保证首领(第 3 层首次进入) | tall：invis+add_mos→dragon_temporal_rantha_the_abomination.png | T | 无同子类已收录 |

### 4.dragon/water（1）

| 名称 | define_as | 唯一/rank | 源码 | 出现（频度） | 外观解析 | 裁 | 同类已收录 |
|---|---|---|---|---|---|:-:|---|
| Ukllmswwik the Wise | UKLLMSWWIK | 唯一/4 | `zones/flooded-cave/npcs.lua:25` | flooded-cave:保证首领(末层静态图) | 默认名 dragon_water_ukllmswwik_the_wise.png | S | 无同子类已收录 |

### 4.elemental/ice（1）

| 名称 | define_as | 唯一/rank | 源码 | 出现（频度） | 外观解析 | 裁 | 同类已收录 |
|---|---|---|---|---|---|:-:|---|
| ultimate shivgoroth | — | —/3 | `general/npcs/shivgoroth.lua:88` | norgos-lair:池E0.7 | tall：invis+add_mos→elemental_ice_ultimate_shivgoroth.png | T | shivgoroth、greater shivgoroth |

### 4.giant/crystal（1）

| 名称 | define_as | 唯一/rank | 源码 | 出现（频度） | 外观解析 | 裁 | 同类已收录 |
|---|---|---|---|---|---|:-:|---|
| Shardskin | SHARDSKIN | 唯一/4 | `zones/old-forest/npcs.lua:43` | old-forest:保证首领(CRYSTALINE 布局) | 显式 immovable_crystal_golden_crystal.png | S | 无同子类已收录 |

### 4.giant/minotaur（1）

| 名称 | define_as | 唯一/rank | 源码 | 出现（频度） | 外观解析 | 裁 | 同类已收录 |
|---|---|---|---|---|---|:-:|---|
| minotaur | — | —/2 | `general/npcs/minotaur.lua:57` | maze:池E10.3；ardhungol:池E0.9；ruined-dungeon:池E0.8；…共10区 | tall：invis+add_mos→giant_minotaur_minotaur.png | T | Minotaur of the Labyrinth |

### 4.horror/Sher'Tul（1）

| 名称 | define_as | 唯一/rank | 源码 | 出现（频度） | 外观解析 | 裁 | 同类已收录 |
|---|---|---|---|---|---|:-:|---|
| Fortress Shadow | BUTLER | —/3 | `zones/shertul-fortress/npcs.lua:128` | shertul-fortress:据点管家(任务) | 默认名 horror_sher_tul_fortress_shadow.png | S | 无同子类已收录 |

### 4.humanoid/temporal（1）

| 名称 | define_as | 唯一/rank | 源码 | 出现（频度） | 外观解析 | 裁 | 同类已收录 |
|---|---|---|---|---|---|:-:|---|
| Ben Cruthdar, the Abomination | BEN_CRUTHDAR_ABOMINATION | 唯一/3.5 | `zones/temporal-rift/npcs.lua:25` | temporal-rift:保证首领(第 2 层首次进入) | 显式 humanoid_human_ben_cruthdar__the_cursed.png | S | 无同子类已收录 |

### 4.humanoid/yeek（1）

| 名称 | define_as | 唯一/rank | 源码 | 出现（频度） | 外观解析 | 裁 | 同类已收录 |
|---|---|---|---|---|---|:-:|---|
| Yeek Wayist | YEEK_WAYIST | 唯一/3 | `zones/halfling-ruins/npcs.lua:117` | halfling-ruins:剧情NPC(末层静态图) | 默认名 humanoid_yeek_yeek_wayist.png | S | 无同子类已收录 |

### 4.training/dummy（1）

| 名称 | define_as | 唯一/rank | 源码 | 出现（频度） | 外观解析 | 裁 | 同类已收录 |
|---|---|---|---|---|---|:-:|---|
| Training Dummy | TRAINING_DUMMY | —/3 | `zones/shertul-fortress/npcs.lua:142` | shertul-fortress:据点训练假人 | 显式 lure.png | S | 无同子类已收录 |

### 4.undead/blood（1）

| 名称 | define_as | 唯一/rank | 源码 | 出现（频度） | 外观解析 | 裁 | 同类已收录 |
|---|---|---|---|---|---|:-:|---|
| animated blood | — | —/1 | `general/npcs/horror-undead.lua:193` | rak-shor-pride:池E0.6 | tall 内层 undead_horror_animated_blood.png（≠默认名） | I | 无同子类已收录 |

### 4.vermin/rodent（1）

| 名称 | define_as | 唯一/rank | 源码 | 出现（频度） | 外观解析 | 裁 | 同类已收录 |
|---|---|---|---|---|---|:-:|---|
| cute little bunny | — | —/1 | `zones/old-forest/npcs.lua:143` | old-forest:区内E0.0 | 默认名 vermin_rodent_cute_little_bunny.png | S | giant brown rat、giant white rat、giant grey rat（共8） |

### 4.vermin/worms（1）

| 名称 | define_as | 唯一/rank | 源码 | 出现（频度） | 外观解析 | 裁 | 同类已收录 |
|---|---|---|---|---|---|:-:|---|
| carrion worm mass | CARRION_WORM_MASS | —/1 | `general/npcs/vermin.lua:67` | mark-spellblaze:池E3.0；ancient-elven-ruins:池E1.4；unremarkable-cave:池E0.9；…共4区 | 默认名 vermin_worms_carrion_worm_mass.png | S | white worm mass、green worm mass |

## 5. NEEDS-CONTRACT-EXTENSION 与 KEEP-NATIVE 明细

### 5.1 NEEDS-CONTRACT-EXTENSION

| 身份 | define_as | 区域 | 阻塞点（源码） | 需要的改动 |
|---|---|---|---|---|
| shadow claw | SHADOW_CLAW | keepsake-meadow（keepsake-meadow:区内E12.5） | 与 SHADOW_CASTER 同名 "shadow claw"，两者 define_as/贴图不同（keepsake-meadow/npcs.lua:171,226）；catalog 以 name 为唯一键（CheckerTokens.lua:313-317 断言不许重名）且 exactIdentity() 只按 name 取一个条目（:385-387），需要把 by_name 改为 name→{define_as 条目表}再按 define_as 选择 | `by_name` 改成 name→条目表并让 `exactIdentity()` 用 define_as 选取；或给两条目分别加 `define_as` 字段。 |
| shadow claw | SHADOW_CASTER | keepsake-meadow（keepsake-meadow:区内E12.5） | 同 SHADOW_CLAW：同名不同 define_as，需 by_name 支持 name+define_as 复合键 | 同上，与 SHADOW_CLAW 一起做。 |
| old vats | VAT1 | conclave-vault（conclave-vault:区内E0.0） | VAT1/VAT2 同名 "old vats"（conclave-vault/npcs.lua:42,51），且 BASE_NPC_VAT 也同名；场景容器而非生物，需 name+define_as 复合键；优先级最低 | 同一改动；且是场景容器，最后做。 |
| old vats | VAT2 | conclave-vault（conclave-vault:区内E0.0） | 同 VAT1 | 同上。 |
| ogre sentry | OGRE_SENTRY | conclave-vault（conclave-vault:区内E0.0） | 与 OGRE_SENTRY2 同名同图（conclave-vault/npcs.lua:102,127；后者 INH 继承）；两个 define_as 需要同一条目覆盖，需要 by_name 支持多 define_as（或给条目加 define_as 列表） | 条目允许 `define_as` 列表，一条覆盖两个 define_as。 |
| ogre sentry | OGRE_SENTRY2 | conclave-vault（conclave-vault:区内E0.0） | 同 OGRE_SENTRY | 同上。 |
| orc warrior | ORC_ATTACK | charred-scar（charred-scar:剧情敌军(静态图)） | 与已待补的 HILL_ORC_WARRIOR 同名 "orc warrior"、同一默认贴图（charred-scar/npcs.lua:135）；只要 by_name 仍是 name 唯一键，两者只能收录其一；HILL_ORC_WARRIOR 先收录则 ORC_ATTACK 按 identity-changed 保持原生 | 先收录 HILL_ORC_WARRIOR；ORC_ATTACK 同名，需 define_as 区分后才可收录。 |

合并后的工程：**一次** `by_name`→复合键（name+define_as）改动即可同时解锁以上 7 条，代价是修改 `CheckerTokens.lua:313-317` 的唯一性断言与 `:385-387` 的查找，并补对应纯 Lua 测试；其中 shadow claw／shadow caster 在 keepsake-meadow 区内池 E 12.5（`keepsake-meadow/npcs.lua:171,226`），是唯一有实际频度的一对。

### 5.2 KEEP-NATIVE

| 身份 | define_as | 区域 | 原因（源码） |
|---|---|---|---|
| multi-hued crystal | — | old-forest（old-forest:池E1.8） | shader="quad_hue"（general/npcs/crystal.lua:154），无 nice_tile{shader=false} 清除；identify() 拒绝 shader（CheckerTokens.lua:406） |
| shimmering crystal | — | old-forest（old-forest:池E1.4） | shader="quad_hue"（crystal.lua:169）且无显式 image（继承 BASE_NPC_CRYSTAL 的 crystal_npc.png，与已收录 white crystal 同一贴图）；shader 被拒 |
| huge sandworm burrower | SANDWORM_TUNNELER_HUGE | sandworm-lair（sandworm-lair:脚本引路体） | display_w/h=2、display_x/y=-0.5（sandworm-lair/npcs.lua:60）+ invulnerable=1（:71）+ never_anger（:68）；identify() 不检查显示尺寸，单格 token 会把 2×2 身体缩成一格，且是不可攻击的引路道具，保持原生 |
| Melinda | MELINDA | crypt-kryl-feijan（crypt-kryl-feijan:任务NPC(末层)） | image=terrain/woman_naked_altar.png，nicer_tiles 下 display_w=2（crypt-kryl-feijan/npcs.lua:88-93），救援后 melinda.image 被改写并 removeAllMOs（:174-176）；运行期换图，沿用 CONTRACTS-B5-B7 §4.2 结论 |
| Spacial Disturbance | SPACIAL_DISTURBANCE | abashed-expanse（abashed-expanse:保证首领） | `resolvers.nice_tile{image="invis.png"}` 无 add_mos（abashed-expanse/npcs.lua:35）+ resolvers.generic 在 nicer_tiles 下 addParticles("wormhole")（:36）；主体是粒子，无可替换单图，identify() 也判为 body-changed |
| Melinda | MELINDA_BEACH | south-beach（south-beach:任务NPC） | moddable_tile="human_female"+base/hair/nude（south-beach/npcs.lua:29-33）；identify() 因 moddable_tile 拒绝（CheckerTokens.lua:405），纸娃娃不在批准路线 |
| The Shade | SHADE | ruins-kor-pul（ruins-kor-pul:保证首领(DEFAULT 布局末层)） | shader="unique_glow"（ruins-kor-pul/npcs.lua:46）；identify() 因 actor.shader 拒绝（CheckerTokens.lua:406） |

注：multi-hued crystal／shimmering crystal 只在 old-forest 水晶布局池里（E 1.8／1.5），若以后接受 `shader` 类身份（例如 quad_hue 只是色相闪烁），可以另立合同；当前不建议。


## 6. 改名变体与前缀映射（heart-gloom 先例）

`heart-gloom/npcs.lua:24-50` 的 `alter()` 对每条带 `rarity` 的通用怪追加天赋并给名字加前缀：未净化用 `gloomy `／`deformed `／`sick `，净化后（`currentZone.is_purified`）用 `dreaming `／`slumbering `／`dozing `。`CheckerTokens.lua:328-337` 的 `heartGloomBase()` 只承认这六个前缀，且只在基底为 **vermin/rodent 或 animal/canine** 时还原，其余仍要过 `identify()` 的类型／图像／显示合同。

本区实际加载四个通用文件（`heart-gloom/npcs.lua:52-55`）：rodent、bear、canine、plant。当前映射只覆盖前两类，因此 **bear 与 plant 的改名变体今天不会被识别**：

| 基底 | type/subtype | 目录是否已有基底 | 该区 E | 备注 |
|---|---|---|---:|---|
| poison ivy | immovable/plants | 是（poison-ivy） | 6.7 | 需放宽 `heartGloomBase` 的子类白名单 |
| brown bear | animal/bear | 是（brown-bear） | 2.7 | 需放宽 `heartGloomBase` 的子类白名单 |
| giant venus flytrap | immovable/plants | 是（venus-flytrap） | 2.4 | 需放宽 `heartGloomBase` 的子类白名单 |
| black bear | animal/bear | 是（black-bear） | 1.4 | 需放宽 `heartGloomBase` 的子类白名单 |
| cave bear | animal/bear | 否，READY，见 §4 | 0.4 | 需放宽 `heartGloomBase` 的子类白名单 |
| war bear | animal/bear | 否，READY，见 §4 | 0.4 | 需放宽 `heartGloomBase` 的子类白名单 |

建议（**合同微扩展，不属于 NEEDS 的 7 条**）：把 `heartGloomBase` 的条件从「rodent 或 canine」放宽为再加 `animal/bear` 与 `immovable/plants`。由于这四类都是同一个 `alter()` 只改名不改图的通用文件，且原判定仍要求类型、图像、显示合同与基底逐项一致，风险与 rodent/canine 相同。放宽后 heart-gloom 的可识别池 E 增加约 13.2（brown bear 2.7、black bear 1.4、poison ivy 6.7、giant venus flytrap 2.4，均已有基底图；cave bear 0.4、war bear 0.4 仍需先补图，见 §4 animal/bear）。**注意**：本文 §2 里 heart-gloom 的「池覆盖」按目录里存在基底计算，对 bear／plant 是偏高估计，放宽映射前实际覆盖更低。

其余区域没有同类前缀改名（我检查了 47 个区所有 `npcs.lua` 里的 `e.name =`／`alter`／`name =` 覆写：只有 heart-gloom 使用 `alter()`），其它「同名变体」都是带 define_as 的独立身份，已在 §4 逐条列出。另有一个近似情形：`orc warrior`（HILL_ORC_WARRIOR 与 ORC_ATTACK）同名，见 §5.1。


## 7. 分批美术计划

批次 1 固定为保证首领；其后各批按 Σ分值从高到低排列。排序原则：**确定性优先**（S 单图＞T native_tall＞I 内层≠默认名）、**频度其次**（保证首领／稀有拖尾；按 §4 的分值＝Σ区内 E＋首领加权 12）。每批 ≤12 个 READY 身份，同批尽量同 type 以保持画风；NEEDS／KEEP 不入批。所有批次前提：沿用 `art/production/README.md` 的生图规范与 TEAA 实机验证。

### 批次 1：保证首领／唯一怪（12 个，Σ分值 128）

| # | 名称 | define_as | type/subtype | 裁 | 主要区域 | 合同风险 |
|---|---|---|---|:-:|---|---|
| 1 | Shardskin | SHARDSKIN | giant/crystal | S | old-forest | 低：默认名单图 |
| 2 | The Withering Thing | WITHERING_THING | animal/canine | S | heart-gloom | 低：默认名单图 |
| 3 | The Dreaming One | DREAMING_ONE | horror/eldritch | S | heart-gloom | 低：默认名单图 |
| 4 | Weaver Queen | WEAVER_QUEEN | spiderkin/spider | T | unhallowed-morass | 低：native_tall，先例 treant／shivgoroth |
| 5 | Murgol, the Yaech Lord | MURGOL | humanoid/yaech | S | murgol-lair | 低：默认名单图 |
| 6 | Lady Nashva the Streambender | NASHVA | humanoid/naga | T | murgol-lair | 低：native_tall，先例 treant／shivgoroth |
| 7 | The Possessed | THE_POSSESSED | humanoid/human | T | ruins-kor-pul | 低：native_tall，先例 treant／shivgoroth |
| 8 | Subject Z | SUBJECT_Z | humanoid/human | S | halfling-ruins | 低：默认名单图 |
| 9 | Grand Corruptor | GRAND_CORRUPTOR | humanoid/shalore | S | mark-spellblaze | 低：默认名单图 |
| 10 | Kyless | KYLESS | humanoid/human | T | keepsake-meadow | 低：native_tall，先例 treant／shivgoroth |
| 11 | Assassin Lord | ASSASSIN_LORD | humanoid/human | S | thieves-tunnels | 低：默认名单图 |
| 12 | Ben Cruthdar, the Abomination | BEN_CRUTHDAR_ABOMINATION | humanoid/temporal | S | temporal-rift | 低：默认名单图 |

### 批次 2：aquatic 系起头，余量按分值补足（12 个，Σ分值 282）

| # | 名称 | define_as | type/subtype | 裁 | 主要区域 | 合同风险 |
|---|---|---|---|:-:|---|---|
| 1 | squid | — | aquatic/critter | S | flooded-cave、murgol-lair | 低：默认名单图 |
| 2 | ink squid | — | aquatic/critter | S | flooded-cave、temple-of-creation | 低：默认名单图 |
| 3 | water imp | — | aquatic/demon | S | flooded-cave、lake-nur | 低：默认名单图 |
| 4 | Walrog | — | aquatic/demon | T | temple-of-creation、flooded-cave | 低：native_tall，先例 treant／shivgoroth |
| 5 | weaver hatchling | — | spiderkin/spider | S | unhallowed-morass | 低：默认名单图 |
| 6 | orb spinner | — | spiderkin/spider | S | unhallowed-morass | 低：默认名单图 |
| 7 | ghoul | GHOUL | undead/ghoul | S | dreadfell、telmur | 低：默认名单图 |
| 8 | drem | — | horror/corrupted | S | deep-bellow、maze | 低：默认名单图 |
| 9 | giant spider | — | spiderkin/spider | S | ardhungol、daikara | 低：默认名单图 |
| 10 | spitting spider | — | spiderkin/spider | S | ardhungol、daikara | 低：默认名单图 |
| 11 | chitinous spider | — | spiderkin/spider | S | ardhungol、dreadfell | 低：默认名单图 |
| 12 | gigantic sandworm tunneler | — | vermin/sandworm | T | briagh-lair、sandworm-lair | 低：native_tall，先例 treant／shivgoroth |

### 批次 3：humanoid 系起头，余量按分值补足（12 个，Σ分值 225）

| # | 名称 | define_as | type/subtype | 裁 | 主要区域 | 合同风险 |
|---|---|---|---|:-:|---|---|
| 1 | orc warrior | HILL_ORC_WARRIOR | humanoid/orc | S | reknor、reknor-escape | 低：默认名单图 |
| 2 | elven guard | — | humanoid/shalore | S | rhaloren-camp、crypt-kryl-feijan | 低：默认名单图 |
| 3 | naga myrmidon | — | humanoid/naga | S | temple-of-creation、ardhungol | 低：默认名单图 |
| 4 | mean looking elven guard | — | humanoid/shalore | S | rhaloren-camp、crypt-kryl-feijan | 低：默认名单图 |
| 5 | orc soldier | ORC | humanoid/orc | S | reknor、reknor-escape | 低：默认名单图 |
| 6 | naga nereid | — | humanoid/naga | T | murgol-lair、slazish-fen | 低：native_tall，先例 treant／shivgoroth |
| 7 | elven mage | — | humanoid/shalore | S | mark-spellblaze、rhaloren-camp | 低：默认名单图 |
| 8 | elven tempest | — | humanoid/shalore | S | mark-spellblaze、rhaloren-camp | 低：默认名单图 |
| 9 | yaech diver | — | humanoid/yaech | S | murgol-lair | 低：默认名单图 |
| 10 | orc archer | HILL_ORC_ARCHER | humanoid/orc | S | reknor、reknor-escape | 低：默认名单图 |
| 11 | elven cultist | — | humanoid/shalore | S | crypt-kryl-feijan、mark-spellblaze | 低：默认名单图 |
| 12 | elven blood mage | — | humanoid/shalore | S | crypt-kryl-feijan、mark-spellblaze | 低：默认名单图 |

### 批次 4：elemental 系起头，余量按分值补足（12 个，Σ分值 151）

| # | 名称 | define_as | type/subtype | 裁 | 主要区域 | 合同风险 |
|---|---|---|---|:-:|---|---|
| 1 | losgoroth | — | elemental/void | S | abashed-expanse | 低：默认名单图 |
| 2 | gwelgoroth | — | elemental/air | S | tempest-peak、mark-spellblaze | 低：默认名单图 |
| 3 | manaworm | — | elemental/void | S | abashed-expanse | 低：默认名单图 |
| 4 | faeros | — | elemental/fire | S | charred-scar、mark-spellblaze | 低：默认名单图 |
| 5 | umber hulk | — | elemental/xorn | S | daikara、tempest-peak | 低：默认名单图 |
| 6 | greater gwelgoroth | — | elemental/air | T | mark-spellblaze、tempest-peak | 低：native_tall，先例 treant／shivgoroth |
| 7 | xorn | — | elemental/xorn | S | tempest-peak、ardhungol | 低：默认名单图 |
| 8 | ultimate gwelgoroth | — | elemental/air | T | mark-spellblaze、tempest-peak | 低：native_tall，先例 treant／shivgoroth |
| 9 | telugoroth | — | elemental/temporal | S | temporal-rift | 低：默认名单图 |
| 10 | Fyrk, Faeros High Guard | FYRK | elemental/fire | T | charred-scar | 低：native_tall，先例 treant／shivgoroth |
| 11 | xaren | — | elemental/xorn | S | tempest-peak、daikara | 低：默认名单图 |
| 12 | greater faeros | — | elemental/fire | S | charred-scar、noxious-caldera | 低：默认名单图 |

### 批次 5：undead 系起头，余量按分值补足（12 个，Σ分值 115）

| # | 名称 | define_as | type/subtype | 裁 | 主要区域 | 合同风险 |
|---|---|---|---|:-:|---|---|
| 1 | skeleton magus | — | undead/skeleton | S | dreadfell、halfling-ruins | 低：默认名单图 |
| 2 | ghast | — | undead/ghoul | S | dreadfell、halfling-ruins | 低：默认名单图 |
| 3 | shadow stalker | SHADOW_STALKER | undead/shadow | S | keepsake-meadow | 低：默认名单图 |
| 4 | lesser vampire | — | undead/vampire | S | dreadfell、ardhungol | 低：默认名单图 |
| 5 | forest wight | — | undead/wight | S | dreadfell、ardhungol | 低：默认名单图 |
| 6 | vampire | — | undead/vampire | S | dreadfell、ardhungol | 低：默认名单图 |
| 7 | master vampire | — | undead/vampire | T | dreadfell、ardhungol | 低：native_tall，先例 treant／shivgoroth |
| 8 | ghoulking | — | undead/ghoul | S | dreadfell、halfling-ruins | 低：默认名单图 |
| 9 | bone giant | — | undead/giant | T | rak-shor-pride、telmur | 低：native_tall，先例 treant／shivgoroth |
| 10 | grave wight | — | undead/wight | S | dreadfell、ardhungol | 低：默认名单图 |
| 11 | elder vampire | — | undead/vampire | S | dreadfell、ardhungol | 低：默认名单图 |
| 12 | The Shade of Telos | SHADE_OF_TELOS | undead/ghost | S | telmur | 低：默认名单图 |

### 批次 6：vermin 系起头，余量按分值补足（12 个，Σ分值 108）

| # | 名称 | define_as | type/subtype | 裁 | 主要区域 | 合同风险 |
|---|---|---|---|:-:|---|---|
| 1 | white ooze | — | vermin/oozes | S | sandworm-lair、conclave-vault | 低：默认名单图 |
| 2 | gigantic corrosive tunneler | — | vermin/sandworm | T | briagh-lair、sandworm-lair | 低：native_tall，先例 treant／shivgoroth |
| 3 | gigantic gravity worm | — | vermin/sandworm | T | briagh-lair、sandworm-lair | 低：native_tall，先例 treant／shivgoroth |
| 4 | slimy ooze | — | vermin/oozes | S | conclave-vault、ardhungol | 低：默认名单图 |
| 5 | poison ooze | — | vermin/oozes | S | conclave-vault、ardhungol | 低：默认名单图 |
| 6 | carrion worm mass | CARRION_WORM_MASS | vermin/worms | S | mark-spellblaze、ancient-elven-ruins | 低：默认名单图 |
| 7 | brittle clear ooze | — | vermin/oozes | S | conclave-vault | 低：默认名单图 |
| 8 | cute little bunny | — | vermin/rodent | S | old-forest | 低：默认名单图 |
| 9 | dredgling | — | horror/temporal | S | temporal-rift、maze | 低：默认名单图 |
| 10 | onilug | — | demon/minor | T | valley-moon-caverns、demon-plane | 低：native_tall，先例 treant／shivgoroth |
| 11 | wretchling | — | demon/minor | S | valley-moon-caverns、demon-plane | 低：默认名单图 |
| 12 | brecklorn | — | horror/corrupted | S | deep-bellow、maze | 低：默认名单图 |

### 批次 7：giant 系起头，余量按分值补足（12 个，Σ分值 90）

| # | 名称 | define_as | type/subtype | 裁 | 主要区域 | 合同风险 |
|---|---|---|---|:-:|---|---|
| 1 | snow giant | — | giant/ice | T | daikara、tempest-peak | 低：native_tall，先例 treant／shivgoroth |
| 2 | minotaur | — | giant/minotaur | T | maze、ardhungol | 低：native_tall，先例 treant／shivgoroth |
| 3 | snow giant thunderer | — | giant/ice | T | tempest-peak、daikara | 低：native_tall，先例 treant／shivgoroth |
| 4 | Healer Astelrid | HEALER_ASTELRID | giant/ogre | T | conclave-vault | 低：native_tall，先例 treant／shivgoroth |
| 5 | mountain troll | — | giant/troll | S | reknor、ardhungol | 低：默认名单图 |
| 6 | snow giant boulder thrower | — | giant/ice | T | tempest-peak、daikara | 低：native_tall，先例 treant／shivgoroth |
| 7 | mountain troll thunderer | — | giant/troll | S | reknor | 低：默认名单图 |
| 8 | snow giant chieftain | — | giant/ice | T | tempest-peak、daikara | 低：native_tall，先例 treant／shivgoroth |
| 9 | ogre guard | — | giant/ogre | T | crypt-kryl-feijan | 低：native_tall，先例 treant／shivgoroth |
| 10 | ogre mauler | — | giant/ogre | T | crypt-kryl-feijan | 低：native_tall，先例 treant／shivgoroth |
| 11 | ogre rune-spinner | — | giant/ogre | T | crypt-kryl-feijan | 低：native_tall，先例 treant／shivgoroth |
| 12 | ogre pounder | — | giant/ogre | T | crypt-kryl-feijan | 低：native_tall，先例 treant／shivgoroth |

### 批次 8：dragon 系起头，余量按分值补足（12 个，Σ分值 79）

| # | 名称 | define_as | type/subtype | 裁 | 主要区域 | 合同风险 |
|---|---|---|---|:-:|---|---|
| 1 | fire drake hatchling | FIRE_DRAKE_HATCHLING | dragon/fire | S | daikara、charred-scar | 低：默认名单图 |
| 2 | cold drake hatchling | — | dragon/cold | S | daikara、ardhungol | 低：默认名单图 |
| 3 | storm drake hatchling | — | dragon/storm | S | tempest-peak、ardhungol | 低：默认名单图 |
| 4 | sand-drake | — | dragon/sand | S | briagh-lair、sandworm-lair | 低：默认名单图 |
| 5 | venom drake hatchling | — | dragon/venom | S | noxious-caldera、ardhungol | 低：默认名单图 |
| 6 | Rantha the Abomination | ABOMINATION_RANTHA | dragon/temporal | T | temporal-rift | 低：native_tall，先例 treant／shivgoroth |
| 7 | Briagh, Great Sand Wyrm | BRIAGH | dragon/sand | T | briagh-lair | 低：native_tall，先例 treant／shivgoroth |
| 8 | Ukllmswwik the Wise | UKLLMSWWIK | dragon/water | S | flooded-cave | 低：默认名单图 |
| 9 | fire drake | — | dragon/fire | S | charred-scar、daikara | 低：默认名单图 |
| 10 | storm drake | — | dragon/storm | S | tempest-peak、ardhungol | 低：默认名单图 |
| 11 | cold drake | NPC_COLD_DRAKE | dragon/cold | S | daikara、ardhungol | 低：默认名单图 |
| 12 | venom drake | — | dragon/venom | S | noxious-caldera、ardhungol | 低：默认名单图 |

### 后续（未排批，156 个）

按 §4 各子类表的分值继续每批 12 个；内层≠默认名的 I 类（6 个）放最后，先做一次夹具确认。剩余身份：quasit、fate spinner、weaver young、giant green ant、giant red ant、grannor'vor、ritch flamespitter、chitinous ritch、corrupted war dog、ritch impaler、fate weaver、black crystal、drem master、elven warrior、yaech hunter、orc assassin、yaech mindslayer、orc necromancer、gaeramarth、ninurlhing、bloated horror、Mindworm、grannor'vin、orc master assassin、cave bear、war bear、Yeek Wayist、Berethh、dredge、faerlhing、losselhing、Warmaster Gnarg、Slasul、Draebor, the Imp、Rak'shor, Grand Necromancer of the Pride、yaech psion、blue crystal、orc grand master assassin、naga tide huntress、fire imp……。

批次内部顺序不影响正确性；每批应在同一次夹具中一起验证。同名冲突（§5.1）与 KEEP（§5.2）不排期。


## 8. 不确定项与源码陷阱

1. **E 是模型不是实测**：按 `Zone.computeRarities`（`engine/Zone.lua:214-258`）加权、`nb_npc` 中值、层数估算，忽略 `max_ood`（:315）之外的随机因素和事件生怪；用于排序足够，不应当作精确概率。BIGWORM 布局层数与 `nb_npc` 不一致的区（sandworm-lair）取折中。
2. **静态图里引用不存在的 define_as**：`maps/zones/reknor-last.lua:31` 的 `ORC_ARCHER`、`maps/zones/reknor-escape-last.lua:34` 的 `ORC_GUARD` 在整个 `data/` 里没有 `define_as`（`HILL_ORC_ARCHER` 才存在于 `general/npcs/orc.lua:71`），原生也生不出来，不计入缺口。
3. **加载了不存在文件的区域**：`charred-scar/npcs.lua:21-22`（fire_elemental.lua、molten_golem.lua）、`conclave-vault/npcs.lua:22-23`（mold.lua、slime.lua）；`general/npcs/` 只有 `molds.lua`。这些行在引擎里被静默跳过，因此这两区的池比看上去小。
4. **随机首领不产生固定身份**：last-hope-graveyard 棺材、ruined-dungeon 的 random_elite、south-beach 的 yaech 都是按 type/properties 现抽，无法以 name 收录，也不计入缺口。
5. **同名唯一性**：`by_name` 是 name→条目单键（`CheckerTokens.lua:313-317`），所以 §5.1 的 7 条不能靠加图解决；另外 §4 里所有 READY 条目已核对与现有目录**无重名**。
6. **heart-gloom 池覆盖偏高估计**：见 §6，bear／plant 改名后不被识别。
7. **未测**：本文所有 READY 都是「按源码合同判定」，未在游戏里放置验证；I 类（内层图≠默认名）尤其应先跑夹具。keepsake-meadow 等使用静态图的区，静态图放置由 `maps/zones` 决定，本文只据源码列举，未启动地图生成核实。
8. **NEEDS/KEEP 的分类是保守的**：quad_hue 水晶、`unique_glow` 的 The Shade 若日后放宽 `identify()` 的 shader 拒绝，可以重新评估。

