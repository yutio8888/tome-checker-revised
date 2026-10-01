# 怪物棋子批次 AD 选型（2026-09-30／10-01，首个“清单外”地下城池批次，不升版）

来源：主代理指定的清单外调研 `tmp/offlist-survey/final.tsv`（class a：地下城池怪，含 src 文件行），本批取 13 个身份：dúathedlen、daelach、orc grand summoner、orc master wyrmic、orc mage-hunter、ritch larva、ritch hunter、ritch hive mother、snow cat、panther、tiger、sabertooth tiger、ice wyrm。多色龙（multi-hued drakes）与 shadow claw 属另一批，本批不碰。

## 结果：13 个全部收入，无“保持原生”的身份

| 身份 | 中文名（mod-tome.lua） | 源码（行） | 外观合同 | 说明 |
|---|---|---|---|---|
| dúathedlen | 多瑟顿 | major-demon.lua:73 | demon/major，tall，`nice_tile{image="invis.png", add_mos=…}`，native_tall | 名字含 ú：NPC.lua:33 按字节替换为下划线，nicer_tiles 关闭时默认图名是不存在的 `demon_major_d__athedlen.png`，永远不等于目录图，故关闭时不套棋子（保持原生，测试钉住）；开启时（默认）走 native-tall |
| daelach | 达莱奇 | major-demon.lua:162 | demon/major，tall，native_tall | 唯一怪 Corrupted Daelach（valley-moon，另名另图）不在本批，保持原生 |
| orc grand summoner | 高阶兽人召唤师 | orc-gorbat.lua:81 | humanoid/orc，64×64 默认图名 | renegade-wyrmics 的 `Beastmaster #rng#` 随机首领走既有平面 captureRandomOrigin |
| orc master wyrmic | 兽人龙战士大师 | orc-gorbat.lua:114 | 同上 | renegade-wyrmics 的“the Herald”同上 |
| orc mage-hunter | 兽人猎法者 | orc-gorbat.lua:148 | 同上（连字符→下划线） | |
| ritch larva | 里奇幼虫 | ritch.lua:50 | insect/ritch，64×64 | |
| ritch hunter | 里奇猎手 | ritch.lua:66 | 同上 | |
| ritch hive mother | 里奇巢母 | ritch.lua:83 | 同上 | **id 冲突**：唯一怪 Ritch Great Hive Mother（HIVE_MOTHER，显式 image=）与本怪画同一原生 PNG，目录 id `ritch-hive-mother` 已被唯一怪占用，故本条用 id `ritch-hive-mother-pool`、独立画稿；两者名字不同、唯一怪绑 define_as，匹配互不串位（测试有正反例） |
| snow cat | 雪猫 | feline.lua:40 | animal/feline，tall，native_tall | 源码 `nice_tile image="invis.png"` 只是 tall 本体机制（同 dolleg／thaurhereg），原生 PNG 是 64×128 的猫，**不是隐形图**；nicer_tiles 关闭时默认图名即同一 PNG，两条路径都有测试 |
| panther | 黑豹 | feline.lua:57 | animal/feline，64×64 | |
| tiger | 老虎 | feline.lua:73 | 同上 | |
| sabertooth tiger | 剑齿虎 | feline.lua:90 | 同上 | |
| ice wyrm | 冰霜巨龙 | cold-drake.lua:89 | dragon/cold，tall，native_tall | frost-dragon-lair／sleeping-dragons／renegade-wyrmics 按名字取同一叶子；随机首领（tall）保持原生，测试有反例 |

13 条源码逐条核过：无 define_as、无 unique、叶子与 base 无 image=／shader／moddable_tile／anim／add_displays；天赋写入集合与批次 S–AC 相同（Psiblades 的 updateModdableTile 对非 moddable 角色是空操作；Antimagic Shield／龙息只有粒子；Stealth 只读护甲子类），合同见 `evidence/monster-batch-ad-20260930/source-contracts.json`。无召唤／效果／地图复制这 13 个身体：ritch hive mother 的 Summon 与 make_escort 建随机 ritch 叶子（各戴自己的棋子），ice wyrm 的 escort 是 cold drake；因此没有 variants／image_aliases／name_aliases。

## 设计约束与同族区分

沿用批次 R–AC 的评审教训（主体中亮、亮边光、整体缩到盘半径约 0.55 内、盘面不得变暗；dúathedlen、daelach、panther 另加 `DARKFIX`），第一次调用就带校准语。

- 四只猫（姿态不同，不只换色）：snow cat 圆团蹲坐＋灰玫瑰斑＋环纹粗尾；panther 低伏潜行的长身＋S 形尾（淡紫蓝，见返工记录）；tiger 迈步咆哮、一爪抬起、尾上卷；sabertooth tiger 笨重正面＋两根长獠牙＋短尾。对既有橙色 Pumpkin、白／褐狼。
- 三只兽人：orc grand summoner 赤膊兽皮骨甲披风、白蟒＋绿蝰、骷髅图腾杖；orc master wyrmic 青铜／沙金龙鳞甲、龙首盔、四色龙鳞肩甲、大战斧；orc mage-hunter 全封闭淡蓝钢＋银重甲、青绿面缝、同心环圆盾。对既有青色光环鹿角的 orc summoner、红／白 wyrmic、狂战士、精英战士。
- 三只 ritch：larva 软胖的奶黄 C 形幼虫；hunter 细长直立的蓝钢黄蜂形、橙色折线条纹、镰刀前足；hive mother 粗壮的绯红铁锈母体、两只大钳、一只琥珀大眼、肿胀的琥珀褐条纹卵腹。对既有橙色 flamespitter、褐黄 impaler、金色龟壳 chitinous 与砖红 Great Hive Mother。
- 两只恶魔与龙：dúathedlen 灰薰衣草色的细长有角影魔、红眼红掌；daelach 紫李色烟与魔焰团中半现的有角重甲恶魔、剑＋斧；ice wyrm 盘成螺旋的银白与钴蓝蛇形龙、冰晶脊刺、折起的翼。对既有红色 dolleg／thaurhereg、火焰公牛 uruivellas、青色蹲伏 cold drake、红／绿盘龙 fire／venom wyrm 与灰蓝 Rantha。
- 已知的参考图标注偏差：家族参考合成图里 Lithfengel 与 Kryl-Feijan 的两格我在文字里标反了（灰烟鬼魂其实是 Kryl-Feijan，Lithfengel 是褐色野兽）；该文字只用于“不要变成这个”，生成结果不受影响，提示词原文已按实际使用记录，未事后改写。

## ImageGen 记录

**18 次**（`gpt-6.1-sol`＋`--ephemeral`，逐次串行，只用 run_imagegen.py 默认）。十三款各至少 1 次，另五次：

- tiger（2 次）：首次 codex 未返回产物路径（provenance-rejected，未入库）；重跑入选。
- orc mage-hunter（2 次）：同上。
- panther（2 次）：首图通过所有几何门，但掩膜亮度 59.32，低于生产测试的 65 下限（深靛蓝毛色压在深盘上）；**没有放宽阈值**，pack 7 改画成明显更亮的蓝紫灰，入选 85.86；首图移入 `superseded/`。
- ritch hunter（3 次）：首图通过几何门，但亮度 61.31（<65）；pack 8 提亮后 `base_drift +8.77`（盘面被带亮，超出 ±8，未入库）；pack 9 提亮并锁盘面明度，偏移 −2.59，入选，亮度 66.98（贴近下限，所有门通过）；首图移入 `superseded/`。
- 其余九款各 1 次入选。

无 PENDING 请求、无豁免、未降低任何阈值（亮度下限仍是 65）。

## 48px 评审

`review/floor-readability-48.png`（十三行整张）、`floor-readability-48-x2.png`（前七款）与 `floor-readability-48-x2-b.png`（后六款）：十三款放在十张真实精修地板上（黄框为各自区域地板的近似）。掩膜亮度（128px，`review/luminance.json`）：ritch hunter 66.98、dúathedlen 69.03、ritch hive mother 69.15、daelach 71.69、orc master wyrmic 78.23、panther 85.86、orc grand summoner 91.6、sabertooth tiger 97.18、orc mage-hunter 97.47、tiger 104.57、ice wyrm 107.92、ritch larva 135.95、snow cat 142.19。48px 上最弱的是 dúathedlen（灰紫影魔，靠红掌与双角辨认）与 ritch hunter（蓝钢黄蜂，靠橙色条纹辨认）；panther 偏淡紫，但读得清且与其余三猫姿态不同。均未再返修。
