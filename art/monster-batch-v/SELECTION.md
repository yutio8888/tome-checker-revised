# 怪物棋子批次 V 选型（2026-09-30，HEAD f2cc2efa，不升版）

来源：`docs/expansion-plan-20260928/MONSTER-GAP-2-20260929.md` 「### 后续（未排批，156 个）」。计分口径与批次 R／S／T／U（`art/monster-batch-u/SELECTION.md`）逐字相同：分值＝§3 逐区枚举里该身份**全部区域**的 E 之和，再加保证首领／剧情／任务／据点身份的加权 12。复算脚本是批次 U 脚本的逐字拷贝（只换了路径）：`art/monster-batch-v/score_candidates.py`，按当前 `CheckerTokens.lua`（275 条，含批次 U）过滤已收录 name，剔除 §7 批次 1–8 已排的身份和 §4 判 I／N／K 的身份，剩 102 条。

## 结果

Training Dummy（12.0，批次 T 留原生）仍出现在脚本输出顶端，本批不再考虑。其后的排名：

| 排名 | 分值 | 身份 | 区域（E） |
|---:|---:|---|---|
| 1 | 8.5 | black crystal | scintillating-caves 4.4＋old-forest 4.1（上批与 fate weaver 并列时落选，现居首位） |
| 2–3 | 8.2 | faerlhing、losselhing | ardhungol 池 |
| 4–5 | 8.1 | dredge（temporal-rift 6.1＋ardhungol 0.5＋dreadfell 0.4＋…共 6 区）、dolleg（valley-moon-caverns 3.5＋demon-plane 3.2＋ardhungol 0.4＋…共 6 区） | |
| 6 | 8.0 | eternal bone giant | rak-shor-pride 4.5＋telmur 1.8＋vor-armoury 1.7 |
| 7 | 7.9 | drem master | deep-bellow 4.5＋maze 3.4 |
| 8–10 | 7.7 | orc pyromancer、orc cryomancer（vor-armoury 7.4＋rak-shor-pride 0.3）、bloated horror（lake-nur 2.5＋ardhungol 0.9＋ruined-dungeon 0.8＋…共 10 区） | |
| 11 | 7.5 | yaech hunter | murgol-lair 7.5 |
| 12 | 7.4 | fiery orc wyrmic、icy orc wyrmic、orc blood mage 三方并列，取 **orc blood mage**（rak-shor-pride 6.7＋ardhungol 0.4＋reknor 0.3） | |

第 12 名的并列取舍按“成套家族”：orc blood mage 与已入选的 orc pyromancer、orc cryomancer 同为兽人法师，凑成三款一组（三个都是 `humanoid/orc` 施法者、各自一个明显的轮廓：斜持法杖／双臂展开冰片扇／双手捧血球）；两款 orc wyrmic 是一对，只能各取一个而拆散，留待以后成对入选。下一梯队（未选）：fiery／icy orc wyrmic 7.4、yaech mindslayer 7.1、heavy bone giant 6.8、cave bear／war bear 6.3、grannor'vin 6.0。

排除项（与 R／S／T／U 相同的规则）：Training Dummy（批次 T 留原生）；§4 判 I 的 6 个（Chronolith Twin、Chronolith Clone、dúathedlen、multi-hued drake hatchling、multi-hued drake、animated blood）；§5.1 同名冲突（shadow claw×2、ogre sentry×2、old vats×2、orc warrior[ORC_ATTACK]，本批无一命中）；§5.2 KEEP（Melinda×2、Spacial Disturbance、The Shade、huge sandworm burrower、multi-hued crystal、shimmering crystal，本批无一命中）；目录已有：核对 `CheckerTokens.lua`，本批 12 个的 name 均不在其中。

## 选定 12 个（源码逐条重核，合同见 `evidence/monster-batch-v-20260930/source-contracts.json`）

| # | 名称 | define_as | type/subtype | 唯一 | 图像来源 | 分值 |
|---|---|---|---|:-:|---|---:|
| 1 | black crystal | — | immovable/crystal | 否 | 显式 image=npc/crystal_black.png（64×64，base BASE_NPC_CRYSTAL 的 crystal_npc.png 被覆盖；另有 `tint`，只作用于原生 MO） | 8.5 |
| 2 | faerlhing | — | spiderkin/spider | 否 | 默认名图（base BASE_NPC_SPIDER，出生启动 Phantasmal／Disruption Shield、Arcane Power） | 8.2 |
| 3 | losselhing | — | spiderkin/spider | 否 | 默认名图（出生启动 Icy Skin、Frost Hands） | 8.2 |
| 4 | dredge | — | horror/temporal | 否 | 默认名图 | 8.1 |
| 5 | dolleg | — | demon/major | 否 | **tall**：`nice_tile{image="invis.png", add_mos={{image="npc/demon_major_dolleg.png", display_h=2, display_y=-1}}}`（64×128）→ `native_tall=true` | 8.1 |
| 6 | eternal bone giant | — | undead/giant | 否 | **tall**：同上，`npc/undead_giant_eternal_bone_giant.png`（64×128）→ `native_tall=true`；死灵法师 Assemble 的同名爪牙同一具身体 | 8.0 |
| 7 | drem master | — | horror/corrupted | 否 | 默认名图 | 7.9 |
| 8 | orc pyromancer | — | humanoid/orc | 否 | 默认名图（base BASE_NPC_ORC_VOR） | 7.7 |
| 9 | orc cryomancer | — | humanoid/orc | 否 | 默认名图 | 7.7 |
| 10 | bloated horror | — | horror/eldritch | 否 | 默认名图（zones/dreams 的 “lost wife” 只是 subtype 写成 "bloated horror"，名称与 define_as 都不同，保持原生） | 7.7 |
| 11 | yaech hunter | — | humanoid/yaech | 否 | 默认名图 | 7.5 |
| 12 | orc blood mage | — | humanoid/orc | 否 | 默认名图（base BASE_NPC_ORC_RAK_SHOR） | 7.4 |

十个是非唯一 64×64 单图；dolleg 与 eternal bone giant 是非唯一 native-tall（先例 bone giant、master vampire、onilug）：`nice_tile` 显式写出 tall PNG，可静态钉住，条目带 `native_tall=true`，`nativeTallImage()` 只接受 image=invis.png＋唯一一条 `display_h=2, display_y=-1` 的 add_mos。无 define_as 可绑，全部按 name＋type＋subtype 匹配，各自名称在源码里唯一（eternal bone giant 另在 `talents/spells/master-of-bones.lua:393` 有一份爪牙定义，同名同型同图，见下）。

## 分包

- Pack 1 水晶与蜘蛛：black crystal、faerlhing、losselhing
- Pack 2 恐魔：dredge、drem master、bloated horror
- Pack 3 兽人法师：orc pyromancer、orc cryomancer、orc blood mage
- Pack 4 巨人、小魔与水栖：dolleg、eternal bone giant、yaech hunter

## 设计约束（生图前定的，不是事后补）

- 沿用批次 R／S／T／U 的评审教训：暗色主体在 48px 与暗盘混成一团；每个主体以中调或亮调大面为主，目标遮罩亮度 ≥65（天然苍白者除外）；评审时凡轮廓与圆盘融合的草稿一律自行淘汰。盘面措辞用“disc at reference lightness, a hair lighter, never darker”。姿势紧凑，所有尖端收在圆盘内四分之三；**批次 U 的教训**：数值闸门看不见局部越过圆盘边缘、被 bbox 归一化掩盖的问题（orc master assassin v1 的高马尾），所以每张图自己看 128px 导出的边缘，任何尖端／发／杖越过外环带一律淘汰。
- **black crystal**（既有：white-crystal 竖立透明棱柱簇、red-crystal 红色放射扇、crimson-crystal 单颗深红宝石、spellblaze-crystal 紫色尖刺球）：烟熏石英／枪灰色的粗六棱晶簇，一根大的倾斜主晶柱加两根短晶柱，底部碎石，晶面带明亮的银白高光面与冷紫色边缘光线（灰调是中调，不是黑）；不是放射扇、不是竖立白簇、不是单颗宝石。
- **faerlhing**（既有蜘蛛九款＋批次 U 的三款；fate-weaver 是奶白／薰衣草，nimisil 是银色宝冠）：**深紫红／紫水晶色**半透明奥术蜘蛛，腹部一个发光的青白符文环，细长的腿高高拱起像一顶笼子，前足之间捧着一团青白色法力球（圆顶／笼形轮廓）；不是奶白、不是钢蓝。
- **losselhing**（雪星蜘蛛）：**冰青／海蓝白**，蓬松的白霜绒毛，粗短结霜的腿，背上一圈冰晶冠刺呈扇形张开（宽而低、背上有尖冠的轮廓）；对 chitinous-spider（奶白放射）、weaver-young（白蓝球）、fate-spinner（钢蓝锯齿）要有轮廓差异，不是放射蜘蛛。
- **恐魔**（既有 dredgling 粉色小蹲姿、drem 棕甲持盾、dremling 灰白毛怪、weirdling-beast 粉褐章鱼状、horned-horror）：**dredge**＝巨大的鲑鱼肉色驼背巨猿状，粗如树干的双臂拄地，小头缩在肩间，皮肤有缝线皱纹与浅灰硬茬（宽厚圆润的一团，对比 dredgling 的小巧瘦蹲）；**drem master**＝矮壮的无面苍白灰头缝口，钢蓝灰的补丁锈甲，一只拳头高举发令、另一手拎缺口战斧朝下（不对称的举拳轮廓，对 drem 的深棕持盾）；**bloated horror**＝奶白发黄的臃肿梨形身体，红色脓疮，孩童般的光头大脸，小手，悬浮（对粉色的 dredgling／weirdling-beast，皮肤是苍白而不是粉色）。
- **兽人法师三款＋既有 orc-necromancer（深蓝兜帽袍）、orc-archer／assassin／warrior／soldier、批次 U 的两款刺客**：都不戴兜帽，橄榄绿肤；**pyromancer**＝橙红长袍金边，光头红色战纹，右手把法杖斜举、杖头一团橙色火球（斜线＋圆火球）；**cryomancer**＝冰蓝长袍织白色符文，一条白辫垂在肩前，双臂向两侧张开、掌心外推，手前扇形展开一圈冰片（宽而低的扇形，无法杖）；**blood mage**＝玫红与骨白的长袍（不是黑红），骨环头饰，佝偻前倾，双手捧一团悬浮的血红球（圆球加前倾轮廓）。
- **dolleg**（tall 原图是暗红棕色多刺恶魔，须状长角；既有小魔 wretchling 是黄绿蹲爬、quasit 铜色持盾牛头、fire-imp 亮朱橙飞翼）：粗壮直立的**砖红／陶土色**恶魔，遍身浅琥珀色骨刺（肩、臂、背的星芒轮廓），头上两根卷曲的须角，刺尖滴着酸绿色液滴；不是黄绿、不是小个子。
- **eternal bone giant**（既有 bone-giant 浅棕黄色壮硕对称双臂垂下，half-finished-bone-giant 细长紫色骷髅）：**象牙白**巨大骨骼傀儡，肩与胸嵌满一圈小颅骨，一条巨臂由熔合的股骨拧成、高举过肩像锤，另一臂垂下，眼窝里冷紫光，身后一缕淡紫色不洁灵光；不对称的举臂轮廓，对 bone-giant 的双臂垂下。
- **yaech hunter**（既有 yaech-diver 淡蓝毛绒游泳姿、yeek-wayist 白色持匕首）：**赭褐／土黄**毛皮，奶白肚子，浅黄眼，贝壳与珊瑚小护甲，一条腰间渔网卷，双手持三叉戟沿对角线向前刺出（斜线轮廓，对 diver 的淡蓝色）。
