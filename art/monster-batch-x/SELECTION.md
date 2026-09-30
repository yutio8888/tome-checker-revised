# 怪物棋子批次 X 选型（2026-09-30，接在批次 W 之后，不升版）

来源：`docs/expansion-plan-20260928/MONSTER-GAP-2-20260929.md` 「### 后续（未排批）」。计分口径与批次 R–W（`art/monster-batch-w/SELECTION.md`）逐字相同；复算脚本是批次 W 脚本的拷贝（`art/monster-batch-x/score_candidates.py`），按当前 `CheckerTokens.lua`（299 条，含批次 W）过滤已收录 name，剔除 §7 批次 1–8 已排的身份和 §4 判 I／N／K 的身份，剩 78 条。

## 结果

Training Dummy（12.0，批次 T 留原生）仍在脚本输出顶端，本批不考虑。其后的排名：

| 排名 | 分值 | 身份 | 说明 |
|---:|---:|---|---|
| 1 | 4.8 | giant acid ant | 批 W 四方并列时落选，本批首位（按任务要求先做；暗色黑黄主体，见下） |
| 2 | 4.7 | yaech psion | murgol-lair 4.7 |
| 3 | 4.7 | skeleton assassin | dreadfell 2.1＋telmur 0.7＋rak-shor-pride 0.7＋…共 5 区；暗色（焦黑） |
| 4 | 4.6 | blue crystal | scintillating-caves 2.6＋old-forest 2.0 |
| 5 | 4.5 | elven corruptor | crypt-kryl-feijan 4.2＋mark-spellblaze 0.3 |
| 6 | 4.4 | giant army ant | 8 区；暗色黑金 |
| 7 | 3.8 | assassin | maze 2.6＋thieves-tunnels 0.9＋ardhungol 0.3；define_as THIEF_ASSASSIN |
| 8 | 3.7 | greater telugoroth | temporal-rift 3.7；非唯一 native-tall |
| 9 | 3.7 | teluvorta | temporal-rift 3.7 |
| 10 | 3.6 | dread | dreadfell 1.3＋rak-shor-pride 0.9＋telmur 0.8＋…共 4 区；纯黑幽灵；死灵法师 Dread 爪牙同名同图 |
| 11 | 3.5 | orc fighter | vor-armoury 2.4＋…共 4 区 |
| 12 | 3.4 | devourer | lake-nur 1.3＋ardhungol 0.5＋dreadfell 0.4＋…共 6 区 |

第 12 名是 devourer、uruivellas、thaurhereg 三方并列（3.4，小数点后四位完全相同），只剩一个名额。三者来自不同文件，没有共同的源码顺序，因此取调研文档 §4 表格的行序（devourer 668 行，uruivellas 830、thaurhereg 831）：devourer 入选。uruivellas 与 thaurhereg（都是非唯一 native-tall 大魔）落选留原生，是下一批候选。其后梯队：uruivellas 3.4、thaurhereg 3.4、temporal stalker 3.2、broken golem 3.1、golem 3.1、blade horror 2.9。

排除项（与 R–W 相同的规则）：Training Dummy；§4 判 I 的身份；§5.1 同名冲突（本批无一命中，assassin 的 define_as 与 shadowblade 重复但名称不同，见合同）；§5.2 KEEP（无）；目录已有：核对 `CheckerTokens.lua`，本批 12 个的 name 均不在其中。

## 选定 12 个（源码逐条重核，合同见 `evidence/monster-batch-x-20260930/source-contracts.json`）

| # | 名称 | 中文名（mod-tome.lua） | define_as | type/subtype | 图像来源 | 分值 |
|---|---|---|---|---|---|---:|
| 1 | giant acid ant | 强酸巨蚁 | — | insect/ant | 显式 image=npc/acid_ant.png | 4.8 |
| 2 | giant army ant | 行军巨蚁 | — | insect/ant | 显式 image=npc/army_ant.png | 4.4 |
| 3 | yaech psion | 夺魂魔灵能力者 | — | humanoid/yaech | 默认名图 | 4.7 |
| 4 | blue crystal | 海蓝水晶体 | — | immovable/crystal | 显式 image=npc/crystal_blue.png（tint 仅着色） | 4.6 |
| 5 | devourer | 吞噬者 | — | horror/eldritch | 默认名图 | 3.4 |
| 6 | skeleton assassin | 骷髅刺客 | — | undead/skeleton | 默认名图 | 4.7 |
| 7 | assassin | 刺客 | THIEF_ASSASSIN | humanoid/human | 默认名图 | 3.8 |
| 8 | elven corruptor | 精灵堕落者 | — | humanoid/shalore | 默认名图 | 4.5 |
| 9 | orc fighter | 兽人斗士 | — | humanoid/orc | 默认名图 | 3.5 |
| 10 | greater telugoroth | 强化泰鲁戈洛斯 | — | elemental/temporal | **tall**：`nice_tile{image="invis.png", add_mos={{image="npc/elemental_temporal_greater_telugoroth.png", display_h=2, display_y=-1}}}`（64×128）→ `native_tall=true` | 3.7 |
| 11 | teluvorta | 泰鲁沃塔 | — | elemental/temporal | 默认名图 | 3.7 |
| 12 | dread | 噩灵 | — | undead/ghost | 显式 image=npc/dread.png；Dread 天赋爪牙、亡灵大师爪牙与召唤同名同型同图 | 3.6 |

（中文名逐条取自 `/workspace/tome4-chinese-translation/mod-tome.lua`；棋子代码与 locale 不引入这些名称。）

十一个是非唯一 64×64 单图；greater telugoroth 是非唯一 native-tall。只有 assassin 绑定 define_as（THIEF_ASSASSIN，后一个 shadowblade 叶子逐字重复它但名称与图不同）；其余十一个无 define_as，按 name＋type＋subtype 匹配。

## 分包

- Pack 1 蚁：giant acid ant、giant army ant
- Pack 2 夺魂魔、水晶、恐魔：yaech psion、blue crystal、devourer
- Pack 3 人形：skeleton assassin、assassin、elven corruptor、orc fighter
- Pack 4 时空与幽灵：greater telugoroth、teluvorta、dread
- Pack 5 elven corruptor 重试（v1 圆盘越界）；Pack 6 orc fighter 重试（v1 底盘偏移 -10.36）

## 设计约束（生图前定的，不是事后补）

沿用批次 R–W 的评审教训并新增 `DARKFIX` 段：本批六个原图近乎全黑的主体（acid ant、army ant、skeleton assassin、assassin、elven corruptor、dread）一律改为中亮度石板灰／古铜／灰白等主色，沿轮廓一圈亮边光，用鲜亮的强调色（酸黄、金带、骨白、酒红腰带、红橙火光）保住身份；提示词明确禁止黑色几丁质、黑衣、黑体。盘面措辞沿用“at reference lightness, a hair lighter, never darker”。

- giant acid ant：石板灰躯壳、隆起的腹部布满酸黄斑点并滴酸，头朝左下；对照既有八＋三款蚁。
- giant army ant：古铜色重甲片＋橙金横带、宽大带角头盾，头朝上对称；与斜放的蚁区分。
- yaech psion：燕麦奶油色绒毛、玫红发带与火焰、淡紫灵气，前倾漂浮一手前伸；区别于既有蓝白 diver／青绿 mindslayer。
- blue crystal：蓝宝石色晶体排成卷浪拱形，区别于白（高塔）、红（扇形）、绯红（双宝石）、黑晶簇。
- devourer：绯红玫瑰色圆胖躯体，整个正面是一张象牙牙圈大口。
- skeleton assassin：蹲伏的骨白骷髅、石板蓝兜帽、双反握匕首。
- assassin：鸽灰／石板蓝紧身衣、蒙面兜帽、酒红腰带，前扑一把长匕首。
- elven corruptor：银发苍白精灵、兰紫／梅红长袍配骨白饰边、骨顶法杖与三片环绕骨片。
- orc fighter：橄榄棕獠牙兽人、枪灰色重型板甲、身前大盾（卡其锈红人字纹，无文字）与低垂战斧。
- greater telugoroth：高窄的金橙色时沙柱、青色条纹与白金核心、沙漏腰；与圆形彩虹旋涡的既有 telugoroth 区分。
- teluvorta：紫罗兰／淡紫尖刺风暴球，钟表指针状碎片放射。
- dread：石板紫灰的破碎烟雾幽灵，红色燃烧眼睛与胸口火核，双爪前伸。

## ImageGen 记录

16／28 次（`gpt-6.1-sol`＋`--ephemeral`，逐次串行，只用 run_imagegen.py 默认）。十二款各 1 次入选，另两次为门控拒收后的重试：elven corruptor 首次圆盘越界 0.877（法杖与环绕骨片越过盘缘，未入库；第二次改短杖并缩小后入选，base_drift -0.65）、orc fighter 首次 base_drift -10.36（大盾与战斧投下暗影，未入库；第二次缩小并去除投影后 -4.11 入选）。无 PENDING 请求、无豁免。

**Refinement（协调者 48px 复核后）**：skeleton assassin v1 与 assassin v1 过了数值门控（遮罩亮度均 62.7），但细长暗色轮廓在各底面上丢失，经带 `refinement` 声明的 pack 7／8 重做（各再 1 次，累计各 2 次）：象牙白骨架＋宽大浅灰淡蓝斗篷（86.7，drift +3.94）、浅石板灰蓝斗篷＋钢刃高光（80.0，drift +7.1）。v1 母版留在 `masters/` 作 SUPERSEDED。
