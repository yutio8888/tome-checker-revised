# 怪物棋子批次 S 选型（2026-09-29，HEAD 7c92573f，不升版）

来源：`docs/expansion-plan-20260928/MONSTER-GAP-2-20260929.md` 「### 后续（未排批，156 个）」。计分口径与批次 R（`art/monster-batch-r/SELECTION.md`）逐字相同：分值＝§3 逐区枚举里该身份**全部区域**的 E 之和，再加保证首领／剧情／任务／据点身份的加权 12。用脚本对 §4 的 266 个身份重新计分（剔除 §7 批次 1–8 已排的 96 个和目录里已有 name 的身份，剩 157 条，与 R 时的“未排批”余量吻合：R 之后目录 239 款）。

## 结果：12.0 并列组仍排在 11.3 之前

批次 R 记录的“下一梯队”里 naga tide huntress、ancient elven mummy、ritch flamespitter、chitinous ritch 是 **11.3**（纯池怪，无加权），但 R 在同一段里也写明“其余 12.0 并列的剧情 NPC”未选。12.0 > 11.3，按同一口径它们仍先于 11.3 组：

| 分值 | 数量 | 说明 |
|---:|---:|---|
| 25.0 | 2 | shadow claw（SHADOW_CLAW／SHADOW_CASTER）：§5.1 同名冲突，不排期 |
| 12.0 | 27 | 保证／剧情／任务／据点身份，池 E＝0；其中 Chronolith Twin／Clone 是 §4 的 I 类（内层≠默认名），留到最后；余 25 个候选 |
| 11.3 | 4 | naga tide huntress、ancient elven mummy、ritch flamespitter、chitinous ritch |
| 10.9 | 2 | gaeramarth、ninurlhing |

排除项：目录已有 name 的身份（无命中）；§4 判 I 的 6 个（Chronolith Twin、Chronolith Clone、dúathedlen、multi-hued drake hatchling、multi-hued drake、animated blood）；§5.1 同名冲突（shadow claw×2、ogre sentry×2、old vats×2、orc warrior[ORC_ATTACK]）；§5.2 KEEP（Melinda×2、Spacial Disturbance、The Shade、huge sandworm burrower、multi-hued crystal、shimmering crystal）。

## 12.0 并列的 25 个候选与取舍

“同分优先成套家族”。25 个候选按家族分组：

| 家族 | 候选 | 取舍 |
|---|---|---|
| 日盟／Charred Scar 剧情组 | human sun-paladin、High Sun-Paladin Rodmour、Argoniel[T]、Elandar[T]，另有 trollmire 的 Aluin the Fallen（堕落的太阳骑士） | **选 5**：同一批日盟骑士＋两名术士，Aluin 是同职业的堕落者 |
| 琥珀草甸／萨洛尔组 | Berethh、Companion Warrior、Companion Archer、Mindworm（thalore 唯一） | **选 4**：Berethh 与两名同伴同任务；Mindworm 同为 thalore |
| 不死唯一组 | Greater Mummy Lord、Kor's Fury、Borfast the Broken | **选 3**：三个 undead 唯一首领，互异的轮廓（裹布、幽灵、装甲食尸鬼） |
| 商队（未选） | caravan merchant／guard／porter | 三款用同一“观众”系列 PNG，48px 上很可能只差配色；留待以后一组 |
| 据点（未选） | Weirdling Beast、Fortress Shadow、Training Dummy、Pumpkin | 据点内脚本／宠物，低优先级 |
| 其他（未选） | Lost Merchant、Nimisil、Slasul[T]、Draebor、war dog、Yeek Wayist | 无成套同伴；留待下批 |

## 选定 12 个

| # | 名称 | define_as | type/subtype | 裁 | 分值 | 依据 |
|---|---|---|---|:-:|---:|---|
| 1 | human sun-paladin | SUN_PALADIN_DEFENDER | humanoid/human | S | 12.0 | charred-scar 静态图剧情敌军（日盟守卫） |
| 2 | High Sun-Paladin Rodmour | SUN_PALADIN_DEFENDER_RODMOUR | humanoid/human | S | 12.0 | 唯一，charred-scar 剧情 |
| 3 | Aluin the Fallen | ALUIN | humanoid/human | S | 12.0 | 唯一，trollmire 后备守关（东行回访）；与日盟骑士同族 |
| 4 | Argoniel | ARGONIEL | humanoid/human | T | 12.0 | charred-scar 剧情；非唯一，`native_tall=true` |
| 5 | Elandar | ELANDAR | humanoid/shalore | T | 12.0 | charred-scar 剧情；非唯一，`native_tall=true` |
| 6 | Mindworm | MINDWORM | humanoid/thalore | S | 12.0 | 唯一，noxious-caldera 第 2 层保证首领 |
| 7 | Berethh | BERETHH | humanoid/thalore | S | 12.0 | 唯一，keepsake-meadow 任务同伴 |
| 8 | Companion Warrior | BERETHH_WARRIOR | humanoid/thalore | S | 12.0 | keepsake-meadow 任务同伴；显式 image=humanoid_elenulach_thief.png |
| 9 | Companion Archer | BERETHH_ARCHER | humanoid/thalore | S | 12.0 | keepsake-meadow 任务同伴；显式 image=humanoid_elf_elven_archer.png |
| 10 | Greater Mummy Lord | GREATER_MUMMY_LORD | undead/mummy | S | 12.0 | 唯一，ancient-elven-ruins 保证首领 |
| 11 | Kor's Fury | KOR_FURY | undead/ghost | S | 12.0 | 唯一，ruins-kor-pul 后备守关 |
| 12 | Borfast the Broken | BORFAST | undead/ghoul | S | 12.0 | 唯一，dreadfell 稀有唯一（池 rarity 50） |

11.3 组（naga tide huntress、ancient elven mummy、ritch flamespitter、chitinous ritch）与 10.9 组（gaeramarth、ninurlhing）留在下批；剩余 13 个 12.0 候选（商队×3、据点×4、Lost Merchant、Nimisil、Slasul、Draebor、war dog、Yeek Wayist）同排在它们之前，是否先做由用户定。

## 分包

- Pack 1 日盟骑士：human sun-paladin、Rodmour、Aluin
- Pack 2 术士：Argoniel、Elandar、Mindworm
- Pack 3 琥珀草甸：Berethh、Companion Warrior、Companion Archer
- Pack 4 不死：Greater Mummy Lord、Kor's Fury、Borfast

## 设计约束（生图前定的，不是事后补）

- 批次 R 评审教训：近黑毛皮／皮革／长袍在 48px 会与暗盘融为一团，即使遮罩亮度 50–55 也一样。本批每个主体都以**中调或亮调大面**为主（银白／金色板甲、奶白裹布、浅青幽灵、浅灰绿皮肤），目标遮罩亮度 ≥65（幽灵、裹布本就苍白）。评审时凡 48px 地板图上轮廓与圆盘混在一起的草稿一律自行淘汰，不看门控。
- 姿势紧凑、全部收在圆盘内四分之三；武器、法杖、披风尖端不得触及外环。
- 骑士三款互异：守卫＝大塔盾向前、钉头锤举过肩（宽盾轮廓）；Rodmour＝双手拄长剑立于身前、羽冠头盔加宽白披风（竖直轮廓）；Aluin＝佝偻低头、战斧下拖、破损锈斑铠甲（不对称低伏轮廓）。对已有 elven warrior（银金板甲＋圆盾＋斧）另有姿势差。
- 术士互异并区别于已有 elven mage（紫袍竖直法杖）与 Fillarel：Argoniel＝前倾施法、双手托金焰球、法杖斜背；Elandar＝深红披风三角展开、两根短杖胸前交叉成 X；Mindworm＝盘腿悬浮、两块心灵晶石环绕的圆团轮廓。
- 琥珀草甸三款互异：Berethh＝立姿满弓、灰绿兜帽斗篷；Companion Warrior＝低弓步前刺长剑、赤褐皮甲；Companion Archer＝单膝跪地举弓、金绿轻甲。都区别于已有 elven guard（直立绿衣持剑）。
- 不死三款：Greater Mummy Lord＝宽大裹布、青铜冠盔、圆盾长剑、布条被风吹起；Kor's Fury＝骷髅面幽灵、下身盘成螺旋、双爪前伸（对已有 Shade of Telos 的直立冰蓝人形）；Borfast＝矮壮披甲食尸鬼、铁笼胸甲、大盾钉锤（对已有 ghoul／ghoulking 的裸身爬行姿势）。
