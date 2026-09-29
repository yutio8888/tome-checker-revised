# 怪物棋子批次 R 选型（2026-09-29，HEAD b4659217，不升版）

来源：`docs/expansion-plan-20260928/MONSTER-GAP-2-20260929.md` 「### 后续（未排批，156 个）」。

## 分值口径

§4 各子类表没有单独的分值列，只给了前三个区域的 E；§7 写明分值＝Σ区内 E＋首领加权 12（保证首领／剧情／任务／据点＋12）。本批用 §3 逐区枚举里每个身份的**全部区域** E 求和（§4 的「…共N区」被截断，直接相加会低估，例如巨蚁 13 区），再加首领权重。脚本复算 156 条后与文档「后续」名单一致，排序前列如下（去掉目录里已有的、§4 判 I 的 6 条、§5.1 同名冲突、§5.2 KEEP）。

排除项：
- 内层≠默认名 I 类（留到最后）：Chronolith Twin、Chronolith Clone、dúathedlen、multi-hued drake hatchling、multi-hued drake、animated blood。
- §5.1 同名冲突：shadow claw×2、ogre sentry×2、old vats×2、orc warrior[ORC_ATTACK]（本批无一命中）。
- §5.2 KEEP：Melinda×2、Spacial Disturbance、The Shade、huge sandworm burrower、multi-hued crystal、shimmering crystal。
- 目录已有：核对 `CheckerTokens.lua`（227 条），本批 12 个的 name 均不在其中。

## 选定 12 个

| # | 名称 | define_as | type/subtype | 裁 | 分值 | 依据 |
|---|---|---|---|:-:|---:|---|
| 1 | quasit | — | demon/minor | S | 29.7 | valley-moon-caverns E13.9、demon-plane E9.6 等 10 区，全表第一 |
| 2 | weaver young | — | spiderkin/spider | S | 19.4 | ardhungol E17.6＋4 区；与已有 weaver hatchling 同一原生 PNG（同图不同名），见风险 |
| 3 | orc necromancer | — | humanoid/orc | S | 16.1 | rak-shor-pride E13.4＋5 区 |
| 4 | orc assassin | — | humanoid/orc | S | 13.7 | reknor E9.2、rak-shor-pride E2.2、vor-armoury E2.0 等 |
| 5 | giant green ant | — | insect/ant | S | 13.3 | 13 区，显式 image=green_ant.png |
| 6 | giant red ant | — | insect/ant | S | 13.3 | 13 区，显式 image=red_ant.png |
| 7 | fate spinner | — | spiderkin/spider | S | 12.8 | unhallowed-morass 区内 E12.8 |
| 8 | elven warrior | — | humanoid/shalore | S | 12.7 | crypt-kryl-feijan E12.7 |
| 9 | corrupted war dog | CORRUPTED_WAR_DOG | animal/canine | S | 12.5 | keepsake-meadow 区内 E12.5；显式 image=canine_dw.png（与 dire wolf 同 PNG，不同名） |
| 10 | Warmaster Gnarg | GNARG | humanoid/orc | S | 12.0 | 唯一，vor-armoury 保证首领；12.0 并列中与兽人家族同组 |
| 11 | Rak'shor, Grand Necromancer of the Pride | RAK_SHOR | humanoid/orc | S | 12.0 | 唯一，rak-shor-pride 保证首领；同上，兽人家族 |
| 12 | grannor'vor | — | horror/corrupted | S | 12.0 | deep-bellow E6.8＋maze E5.2 |

12.0 并列共二十余个（多为剧情 NPC／同伴）。按“同分优先成套家族”选：兽人首领 Gnarg、Rak'shor 与已入选的 orc necromancer、orc assassin 凑成兽人一组四个（Pack 1）；第三个名额取仅有的非剧情池怪 grannor'vor（E 合计 12.0，且与已有 corrupted horror 同族）。下一梯队（未选）：naga tide huntress 11.3、ancient elven mummy 11.3、ritch flamespitter／chitinous ritch 11.3、gaeramarth／ninurlhing 10.9、orc master assassin 10.5，以及其余 12.0 并列的剧情 NPC。

## 分包

- Pack 1 兽人：orc necromancer、Rak'shor、Warmaster Gnarg、orc assassin
- Pack 2 蛛／蚁：weaver young、fate spinner、giant green ant、giant red ant
- Pack 3 其余：quasit、elven warrior、corrupted war dog、grannor'vor

## 设计约束（生图前定的，不是事后补）

- 巨蚁：目录里已有 white/yellow/brown/blue/black/carpenter 六款同一俯视直排姿势的换色蚁；green/red 必须换轮廓，不能只换色：green＝腹部蜷起、毒滴的 C 形，red＝后肢立起、前肢高举、大颚张开的直立 T 形，两者互异。
- weaver young 相对 weaver hatchling（同原生图）：不同轮廓（蜷缩球形＋大螺旋腹），并与 fate spinner（长腿宽展＋丝环）互异。
- 两个法袍兽人：orc necromancer＝驼背前倾、无杖、掌托魂火；Rak'shor＝挺立、骨杖竖持、高领骨肩甲。
- corrupted war dog 相对已有 dire wolf 令牌：扑击后蹲的轮廓，黑毛＋腐化脉络，不同于侧向踱步的棕狼。
