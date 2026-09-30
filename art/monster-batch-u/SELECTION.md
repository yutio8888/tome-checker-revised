# 怪物棋子批次 U 选型（2026-09-30，HEAD 24cf2dcb，不升版）

来源：`docs/expansion-plan-20260928/MONSTER-GAP-2-20260929.md` 「### 后续（未排批，156 个）」。计分口径与批次 R／S／T（`art/monster-batch-r/SELECTION.md`、`art/monster-batch-s/SELECTION.md`、`art/monster-batch-t/SELECTION.md`）逐字相同：分值＝§3 逐区枚举里该身份**全部区域**的 E 之和，再加保证首领／剧情／任务／据点身份的加权 12。用脚本重算（§4 的 266 个身份，剔除 §7 批次 1–8 已排的 96 个、目录里已有 name 的 263 款、§4 判 I／N／K 的 20 个），剩 114 条。复算脚本：`art/monster-batch-u/score_candidates.py`（先生成 `/tmp/tot.json`，再按当前 `CheckerTokens.lua` 过滤）。

## 结果

12.0 剧情组已随批次 T 收尾（Training Dummy 是唯一没入选的 12.0 候选，批次 T 明确留原生，本批不再考虑）。现在最高分即 11.3 组：

| 排名 | 分值 | 身份 | 区域（E） |
|---:|---:|---|---|
| 1–4 | 11.3 | naga tide huntress、ancient elven mummy、ritch flamespitter、chitinous ritch | 各自区内池（temple-of-creation／ancient-elven-ruins／ritch-tunnels ×2） |
| 5–6 | 10.9 | gaeramarth、ninurlhing | ardhungol 池 |
| 7 | 10.5 | orc master assassin | reknor 6.9＋rak-shor-pride 1.9＋vor-armoury 1.7 |
| 8 | 9.7 | fire imp | valley-moon-caverns 4.6＋demon-plane 3.2＋crypt-kryl-feijan 1.6＋ardhungol 0.3 |
| 9 | 9.1 | ritch impaler | ritch-tunnels 9.1 |
| 10–11 | 8.7 | orc grand master assassin（reknor 5.5＋1.7＋1.5）、naga psyren（temple-of-creation 8.7） | 并列，两个都入选 |
| 12 | 8.5 | fate weaver（unhallowed-morass 区内 8.5）、black crystal（old-forest 4.1＋scintillating-caves 4.4） | 并列，取一个 |

12＝前 11 名＋并列 8.5 中的 **fate weaver**：并列按“成套家族”取舍，fate weaver 与已入选的 gaeramarth、ninurlhing 同为 spiderkin/spider，凑成蜘蛛一组三款；black crystal 是 immovable/crystal，家族里没有其他同伴，留待以后。下一梯队（未选）：black crystal 8.5、faerlhing／losselhing 8.2、dredge 8.1、dolleg 8.1、eternal bone giant 8.0、drem master 7.9。

排除项（与 R／S／T 相同的规则）：Training Dummy（批次 T 留原生）；§4 判 I 的 6 个（Chronolith Twin、Chronolith Clone、dúathedlen、multi-hued drake hatchling、multi-hued drake、animated blood）；§5.1 同名冲突（shadow claw×2、ogre sentry×2、old vats×2、orc warrior[ORC_ATTACK]，本批无一命中）；§5.2 KEEP（Melinda×2、Spacial Disturbance、The Shade、huge sandworm burrower、multi-hued crystal、shimmering crystal）；目录已有：核对 `CheckerTokens.lua`（263 条），本批 12 个的 name 均不在其中。

## 选定 12 个（源码逐条重核，合同见 `evidence/monster-batch-u-20260930/source-contracts.json`）

| # | 名称 | define_as | type/subtype | 唯一 | 图像来源 | 分值 |
|---|---|---|---|:-:|---|---:|
| 1 | naga tide huntress | — | humanoid/naga | 否 | 显式 image=npc/naga_tide_huntress.png（64×64，base BASE_NPC_NAGA） | 11.3 |
| 2 | ancient elven mummy | — | undead/mummy | 否 | NPC.lua:33 默认名图（base BASE_NPC_MUMMY） | 11.3 |
| 3 | ritch flamespitter | — | insect/ritch | 否 | 默认名图（base BASE_NPC_RITCH_REL） | 11.3 |
| 4 | chitinous ritch | — | insect/ritch | 否 | 默认名图 | 11.3 |
| 5 | gaeramarth | — | spiderkin/spider | 否 | 默认名图（base BASE_NPC_SPIDER，出生启动 Stealth） | 10.9 |
| 6 | ninurlhing | — | spiderkin/spider | 否 | 默认名图（出生启动 Acidic Skin）；教程的 “hairy spider”（TUT_SPIDER_3）借用同 PNG 但名称不同，保持原生 | 10.9 |
| 7 | orc master assassin | — | humanoid/orc | 否 | 默认名图 | 10.5 |
| 8 | fire imp | — | demon/minor | 否 | 默认名图（base BASE_NPC_DEMON） | 9.7 |
| 9 | ritch impaler | — | insect/ritch | 否 | 默认名图 | 9.1 |
| 10 | orc grand master assassin | — | humanoid/orc | 否 | 默认名图 | 8.7 |
| 11 | naga psyren | — | humanoid/naga | 否 | 显式 image=npc/naga_psyren.png | 8.7 |
| 12 | fate weaver | — | spiderkin/spider | 否 | 默认名图（unhallowed-morass 区内 BASE_NPC_SPIDER） | 8.5 |

十二个都是非唯一、无 define_as、64×64 单图、无 `native_tall`：没有 tall 体。目录条目按 name＋type＋subtype 匹配（无 define_as 可绑，与批次 R 的 orc assassin 等同一路径），各自名称在源码里唯一。

## 分包

- Pack 1 里奇：ritch flamespitter、ritch impaler、chitinous ritch
- Pack 2 水族与亡者：naga tide huntress、naga psyren、ancient elven mummy
- Pack 3 兽人与小魔：orc master assassin、orc grand master assassin、fire imp
- Pack 4 蜘蛛：gaeramarth、ninurlhing、fate weaver

## 设计约束（生图前定的，不是事后补）

- 沿用批次 R／S／T 的评审教训：暗色主体在 48px 与暗盘混成一团；每个主体以中调或亮调大面为主，目标遮罩亮度 ≥65（天然苍白者除外）；评审时凡轮廓与圆盘融合的草稿一律自行淘汰。盘面措辞用“disc at reference lightness, a hair lighter, never darker”。姿势紧凑，所有尖端收在圆盘内四分之三。
- **里奇三款互异（轮廓，不只是颜色）**：flamespitter＝猩红橙色，后半身直立成 S 形，口中一团小火球（高、竖的轮廓）；impaler＝铜褐色，身体低伏向前突刺，一只巨大的骨白矛形前螯沿对角线前指（长斜线轮廓）；chitinous＝金黄色圆顶重甲，六足收在壳下，两只短弯角螯，像甲虫／犰狳的圆团轮廓。对既有 ritch-hive-mother（橘红蟹形辐射体）与 chitinous-spider（奶白蜘蛛）也要拉开：三款都不是辐射蟹形。
- **娜迦两款＋既有七款**：tide huntress＝冰白银鳞尾、银白发辫、拉满的短弓＋冰晶箭（斜线弓形；既有七款无一持弓）；psyren＝玫紫渐变珠光尾盘成上升螺旋、长发如翼散开、双手托起紫白心灵球（螺旋加发翼轮廓）。二者互异，也不同于 nereid 的黄尾金发、myrmidon 的蓝尾三叉戟。
- **远古精灵木乃伊**：修长瘦高，奶白与旧茶色绷带，绷带下透出尖耳，褪色金冠饰＋玉叶宝石，绿光眼窝，双臂平伸向前，绷带尾拖在身后；无盾无甲（对 greater-mummy-lord 的宽厚金甲持盾轮廓）。
- **兽人刺客两款＋既有 orc-assassin（蓝灰兜帽、蹲踞、双弯刀）**：master＝光头顶髻（无兜帽），橄榄绿肤，天蓝与奶白绑带，正对观者宽站，双匕首在胸前交叉成 X（紧凑的 X 轮廓）；grand master＝更高更直，象牙白骨面具带弯角，肩甲尖刺，青绿披挂拖尾，双臂向两侧张开、双刃向外下方斜指（宽 A 形轮廓）。
- **fire imp**：猩红皮肤、炭黑弯角、小蝠翼折在背后，双臂高举过头掷出一团火球，长细尾尖带火苗（Y 形轮廓，对 draebor 的白毛蹲踞单手火苗、quasit 的持盾牛头、wretchling 的黄绿蹲爬）。
- **蜘蛛三款＋既有九款**：gaeramarth＝骨白与灰烬色，腹背有象牙色骷髅纹，两只长前足高举、其余足收拢（前足立起的三角轮廓；对 giant-spider 的黑灰平伏）；ninurlhing＝病绿奶黄半透明胀腹，腐蚀孔洞、滴酸、头顶一小团蒸汽，粗短足八字外撑（圆胀＋滴落轮廓；对 spitting-spider 的棕身喷绿液）；fate weaver＝奶白与薰衣草紫毛蜘蛛，腹上金色钟面／沙漏纹，前足间织着一圈金色丝线的猫摇篮（与 fate-spinner 的钢蓝锯齿足＋丝环、weaver-young 的白螺旋球不同）。
