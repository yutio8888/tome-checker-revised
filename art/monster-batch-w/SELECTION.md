# 怪物棋子批次 W 选型（2026-09-30，HEAD 4d03e57d，不升版）

来源：`docs/expansion-plan-20260928/MONSTER-GAP-2-20260929.md` 「### 后续（未排批，156 个）」。计分口径与批次 R／S／T／U／V（`art/monster-batch-v/SELECTION.md`）逐字相同：分值＝§3 逐区枚举里该身份**全部区域**的 E 之和，再加保证首领／剧情／任务／据点身份的加权 12。复算脚本是批次 V 脚本的拷贝（只换路径、把分值多保留到小数点后四位以便看清并列）：`art/monster-batch-w/score_candidates.py`，按当前 `CheckerTokens.lua`（287 条，含批次 V）过滤已收录 name，剔除 §7 批次 1–8 已排的身份和 §4 判 I／N／K 的身份，剩 90 条。

## 结果

Training Dummy（12.0，批次 T 留原生）仍在脚本输出顶端，本批不再考虑。其后的排名：

| 排名 | 分值 | 身份 | 区域（E） |
|---:|---:|---|---|
| 1–2 | 7.4 | fiery orc wyrmic、icy orc wyrmic（批 V 三方并列时被让出的一对） | reknor 4.6＋rak-shor-pride 1.5＋vor-armoury 1.3 |
| 3 | 7.1 | yaech mindslayer | murgol-lair 7.1 |
| 4 | 6.8 | heavy bone giant | rak-shor-pride 4.0＋telmur 1.7＋vor-armoury 1.1 |
| 5–6 | 6.3 | cave bear、war bear | old-forest 2.0＋noxious-caldera 1.8＋scintillating-caves 1.0＋…共 7 区 |
| 7 | 6.0 | grannor'vin | deep-bellow 3.4＋maze 2.6 |
| 8 | 5.7 | rotting mummy | ancient-elven-ruins 5.7 |
| 9 | 5.4 | banshee | dreadfell 2.8＋rak-shor-pride 1.0＋telmur 0.9＋demon-plane 0.7 |
| 10–12 | 4.8 | giant fire ant、giant ice ant、giant lightning ant（四方并列的前三） | 各 9 区：ardhungol 0.9＋dreadfell 0.8＋reknor 0.7＋ruined-dungeon 0.7＋… |

第 10–12 名是 giant fire／ice／lightning／acid ant 四方并列（分值到小数点后四位完全相同，各 9 区、区域与 E 逐项一致），只有三个名额。分值给不出取舍，按确定性的次序规则取源码顺序（`general/npcs/ant.lua` 中 fire 131 行、ice 147、lightning 164、acid 180），因此 **giant acid ant 落选**；这也避开了一个暗色主体（原图是黑底黄斑）。落选者留原生，下一梯队：giant acid ant 4.8、yaech psion 4.7、skeleton assassin 4.7、blue crystal 4.6、elven corruptor 4.5、giant army ant 4.4。

排除项（与 R／S／T／U／V 相同的规则）：Training Dummy（批次 T 留原生）；§4 判 I 的 6 个；§5.1 同名冲突（本批无一命中）；§5.2 KEEP（本批无一命中）；目录已有：核对 `CheckerTokens.lua`，本批 12 个的 name 均不在其中。

## 选定 12 个（源码逐条重核，合同见 `evidence/monster-batch-w-20260930/source-contracts.json`）

| # | 名称 | 中文名（mod-tome.lua） | define_as | type/subtype | 图像来源 | 分值 |
|---|---|---|---|---|---|---:|
| 1 | fiery orc wyrmic | 炽焰兽人龙战士 | ORC_FIRE_WYRMIC | humanoid/orc | 默认名图（base BASE_NPC_ORC） | 7.4 |
| 2 | icy orc wyrmic | 冰霜兽人龙战士 | ORC_ICE_WYRMIC | humanoid/orc | 默认名图 | 7.4 |
| 3 | yaech mindslayer | 夺魂魔心灵杀手 | — | humanoid/yaech | 默认名图 | 7.1 |
| 4 | heavy bone giant | 重型骨巨人 | — | undead/giant | **tall**：`nice_tile{image="invis.png", add_mos={{image="npc/undead_giant_heavy_bone_giant.png", display_h=2, display_y=-1}}}`（64×128）→ `native_tall=true`；死灵法师 Assemble 的同名爪牙同一具身体 | 6.8 |
| 5 | cave bear | 穴居熊 | — | animal/bear | 显式 image=npc/cave_bear.png | 6.3 |
| 6 | war bear | 战熊 | — | animal/bear | 显式 image=npc/war_bear.png（grushnak-armory 的随机首领 Warbear 走既有随机来源路径） | 6.3 |
| 7 | grannor'vin | 格兰诺文 | — | horror/corrupted | 默认名图（出生启动 Call Shadows） | 6.0 |
| 8 | rotting mummy | 腐烂木乃伊 | — | undead/mummy | 默认名图（base BASE_NPC_MUMMY，同批 U 的 ancient elven mummy） | 5.7 |
| 9 | banshee | 哀嚎女妖 | — | undead/ghost | 显式 image=npc/banshee.png（出生启动 Blur Sight） | 5.4 |
| 10 | giant fire ant | 火焰巨蚁 | — | insect/ant | 显式 image=npc/fire_ant.png | 4.8 |
| 11 | giant ice ant | 寒冰巨蚁 | — | insect/ant | 显式 image=npc/ice_ant.png | 4.8 |
| 12 | giant lightning ant | 闪电巨蚁 | — | insect/ant | 显式 image=npc/lightning_ant.png | 4.8 |

十一个是非唯一 64×64 单图；heavy bone giant 是非唯一 native-tall（先例 eternal bone giant、bone giant）。两个兽人龙战士的叶子带 define_as（ORC_FIRE_WYRMIC／ORC_ICE_WYRMIC，reknor-last 静态图按 define_as 放置、两个宝库按名称放置，都指向同一叶子），目录条目精确绑定 define_as；其余十个无 define_as，按 name＋type＋subtype 匹配。

## 分包

- Pack 1 兽人龙战士、夺魂魔与骨巨人：fiery／icy orc wyrmic、yaech mindslayer、heavy bone giant
- Pack 2 熊与恐魔：cave bear、war bear、grannor'vin
- Pack 3 不死：rotting mummy、banshee
- Pack 4 元素蚁：giant fire／ice／lightning ant

## 设计约束（生图前定的，不是事后补）

沿用批次 R–V 的评审教训：暗色主体在 48px 与暗盘混成一团（战犬、drem master 被退回）；每个主体以中调或亮调大面为主并带一圈亮边光，目标遮罩亮度 ≥65；姿势紧凑，尖端收在圆盘内四分之三；盘面措辞“disc at reference lightness, a hair lighter, never darker”。数值闸门看不见局部越过圆盘边缘的问题，所以每张图都看过 128px 导出的边缘。

- **兽人龙战士一对**（既有橄榄色 orc-warrior 弯刀、orc-soldier 深色尖刺、三款长袍施法者）：fiery＝深橙红龙鳞甲＋红色翼鳍肩甲＋角盔，右手战斧斜举、左手小火苗；icy＝苍白冰蓝／白龙鳞甲＋冰晶肩刺，低姿双手横持战斧、口吐霜气；配色之外还靠举斧斜线对低姿横斧区分。
- **yaech mindslayer**（既有 yaech-diver 淡蓝游泳姿、yeek-wayist 白色持匕首、批 V 的 yaech-hunter 赭褐持叉）：海沫青绿毛皮、奶白脸，盘腿悬浮，双掌间一团黄白闪电，身前一圈淡青动能护盾环。
- **heavy bone giant**（既有 bone-giant 淡黄对称垂臂、eternal-bone-giant 象牙白举臂、half-finished 细长紫色）：蜜琥珀色的宽矮弓背骨魔，双臂抱着一捆长股骨（对应 Throw Bones）。
- **熊**（既有 brown-bear 朝左下走、black-bear 正面）：cave bear＝石灰灰色侧身向右低头走、肩背隆起；war bear＝赤褐色人立咆哮、双前爪高举、两根象牙獠牙、铁箍皮项圈。
- **grannor'vin**（既有 grannor-vor 蓝灰盘卷带绿黏液；原图是深色“影蛞蝓”，为免暗色主体改为烟熏薰衣草灰／淡紫、银白高光）：前半身立起成 S 形、苍白人脸，尾部盘成圆涡，几缕深紫影烟。
- **rotting mummy**（既有 ancient-elven-mummy 直立尖耳淡褐）：佝偻蹒跚，脏污黄褐／骨白绷带带棕色污渍与灰绿腐斑，一臂前伸。
- **banshee**：苍白青白半透明的哀嚎女性，长发随风上扬，破裙化作雾缕，双手举在头侧。
- **元素蚁**（既有八款蚁：白、黄、褐、蓝、木匠、黑、绿、红，全是平铺放射姿）：fire＝焦橙朱红发光甲壳，腹部一束火焰羽；ice＝晶体状淡青冰蓝，背脊一排五根短冰晶刺；lightning＝淡薰衣草钢紫，腹部白黄发光，触角与腹部之间跳动黄白电弧光环。

## ImageGen 记录

16／28 次（`gpt-6.1-sol`＋`--ephemeral`，逐次串行）。fiery orc wyrmic 3 次：首次 codex 未返回产物路径（溯源拒收，产物未使用）、第二次圆盘越界 0.9798（战斧越过圆盘边缘）、第三次改短柄手斧后 -2.71 入选；giant ice ant 3 次：首次 base_drift +8.02（霜光让盘面偏亮）、第二次 codex 又未返回路径（拒收）、第三次缩小并去掉雪晶后 +2.06 入选；其余十款各 1 次。无 PENDING 请求、无豁免。
