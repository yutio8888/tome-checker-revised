# 怪物棋子批次 Z 选型（2026-09-30，接在批次 Y 之后，不升版）

来源：`docs/expansion-plan-20260928/MONSTER-GAP-2-20260929.md` 「### 后续（未排批）」。计分口径与批次 R–Y（`art/monster-batch-y/SELECTION.md`）逐字相同；复算脚本是批次 Y 脚本的拷贝（`art/monster-batch-z/score_candidates.py`，仅改了文档里的路径），按当前 `CheckerTokens.lua`（323 条，含批次 Y）过滤已收录 name，剔除 §7 批次 1–8 已排的身份和 §4 判 I／N／K 的身份，剩 54 条（含 Training Dummy）。

## 结果

Training Dummy（12.0，批次 T 留原生）仍在脚本输出顶端，本批不考虑。其后的排名（本批取到 2.1 分为止，2.2 与 2.1 两档都整档收入，没有并列落选）：

| 排名 | 分值 | 身份 | 中文名（mod-tome.lua） | 说明 |
|---:|---:|---|---|---|
| 1 | 2.7 | black mamba | 黑曼巴 | 批 Y 四方并列 2.7 时按行序（997）落选；noxious-caldera 1.4＋unremarkable-cave 0.9＋lake-nur 0.4；显式 image=darkgrey-snake.png |
| 2 | 2.6 | bandit lord | 强盗首领 | maze 2.1＋thieves-tunnels 0.5（行 597）；bandit-fortress 区与 vault 也按名生成 |
| 3 | 2.6 | orb weaver | 球蛛编织者 | unhallowed-morass 2.6（行 624） |
| 4 | 2.5 | elven elite warrior | 精英精灵战士 | crypt-kryl-feijan 2.5（行 643） |
| 5 | 2.5 | ultimate telugoroth | 究极泰鲁戈洛斯 | temporal-rift 2.5（行 717）；非唯一 tall → native_tall |
| 6 | 2.5 | greater teluvorta | 强化泰鲁沃塔 | temporal-rift 2.5（行 718）；tall |
| 7 | 2.4 | runed bone giant | 符文骨巨人 | rak-shor-pride 2.4（行 801）；tall |
| 8 | 2.2 | void horror | 虚空恐魔 | temporal-rift 2.2（行 695） |
| 9 | 2.2 | swarming horror | 群生恐魔 | lake-nur 2.2（行 725）；tall |
| 10 | 2.2 | ravenous horror | 贪婪恐魔 | lake-nur 2.2（行 726）；tall |
| 11 | 2.1 | rogue sapper | 盗贼工兵 | maze 1.6＋thieves-tunnels 0.5（行 601）；define_as THIEF_SAPPER；显式 image=humanoid_human_assassin.png |
| 12 | 2.1 | fire wyrm | 火焰巨龙 | charred-scar 2.1（行 935）；tall |

注：**void horror 的中文名以 mod-tome.lua 为准（虚空恐魔）**；插件自带 locale 里写作“虚空靨魔”，那是另一份文件，本批文字一律取 mod-tome.lua。

其后梯队：ultimate faeros 2.0、orc berserker 1.8、dredge captain 1.8、polar bear 1.8、anaconda 1.8、ultimate teluvorta 1.7 ……本批之后剩 42 条未映射（含 Training Dummy，即 41 个真实候选）。

排除项（与 R–Y 相同的规则）：Training Dummy；§4 判 I 的身份；§5.1 同名冲突（本批无一命中）；§5.2 KEEP（无）；目录已有：核对 `CheckerTokens.lua`，本批 12 个的 name 均不在其中。

## 选定 12 个（源码逐条重核，合同见 `evidence/monster-batch-z-20260930/source-contracts.json`）

| # | 名称 | define_as | type/subtype | 图像来源 | 分值 |
|---|---|---|---|---|---:|
| 1 | black mamba | — | animal/snake | 显式 image=npc/darkgrey-snake.png | 2.7 |
| 2 | bandit lord | — | humanoid/human | 默认名图 | 2.6 |
| 3 | orb weaver | — | spiderkin/spider | 默认名图 | 2.6 |
| 4 | elven elite warrior | — | humanoid/shalore | 默认名图 | 2.5 |
| 5 | ultimate telugoroth | — | elemental/temporal | **tall**：`nice_tile` 64×128 → `native_tall=true` | 2.5 |
| 6 | greater teluvorta | — | elemental/temporal | **tall** → `native_tall=true` | 2.5 |
| 7 | runed bone giant | — | undead/giant | **tall** → `native_tall=true` | 2.4 |
| 8 | void horror | — | horror/temporal | 默认名图 | 2.2 |
| 9 | swarming horror | — | horror/aquatic | **tall** → `native_tall=true` | 2.2 |
| 10 | ravenous horror | — | horror/aquatic | **tall** → `native_tall=true` | 2.2 |
| 11 | rogue sapper | THIEF_SAPPER | humanoid/human | 显式 image=npc/humanoid_human_assassin.png | 2.1 |
| 12 | fire wyrm | — | dragon/fire | **tall** → `native_tall=true` | 2.1 |

六个是非唯一 native-tall（ultimate telugoroth、greater teluvorta、runed bone giant、swarming horror、ravenous horror、fire wyrm），六个是非唯一 64×64 单图；只有 rogue sapper 绑定 define_as。**同 PNG 处理**：rogue sapper 显式使用刺客的 PNG（`humanoid_human_assassin.png`），而刺客条目（define_as THIEF_ASSASSIN）也用它；两者按 name 和 define_as 区分，测试有互换名字／define_as 的负例；新棋子是卡其护目镜设陷者，不是刺客的换色。召唤／护卫：强盗首领召唤 bandit／thief／rogue（各自已有棋子），群生恐魔自带护卫和 swarm hive 召唤的是同一叶子，fire wyrm 的护卫是 fire drake；renegade-wyrmics 的随机首领 fire wyrm 走“非唯一 tall 保持原生”路径。

## 分包

- Pack 1：black mamba、bandit lord、rogue sapper、orb weaver
- Pack 2：elven elite warrior、fire wyrm、runed bone giant
- Pack 3：ultimate telugoroth、greater teluvorta、void horror
- Pack 4：swarming horror、ravenous horror
- Pack 5 orb weaver 重试（pack 1 无图返回）；Pack 6 elven elite warrior 重试（pack 2 圆盘半径 0.897 超 0.867）；Pack 7 void horror 重试（pack 3 底盘偏移 -8.78 超 ±8）；Pack 8 runed bone giant 重做（pack 2 的图过了全部阻断门控，但 `subject_intrusion` +20.88 超警告线 +20；本批不放行警告，改绘后 +3.71）

## 设计约束（生图前定的，不是事后补）

沿用批次 R–Y 的评审教训：主体大块面一律中亮到亮，沿轮廓一圈亮边光，禁止黑色主体；`DARKFIX` 段用于原图近黑或偏暗的主体（black mamba、rogue sapper、greater teluvorta、void horror、swarming horror、ravenous horror、fire wyrm）。盘面措辞沿用“at reference lightness, a hair lighter, never darker”。tall 主体统一要求“画成一个紧凑的直立单体填满圆盘，不出高画布”；群体（swarming horror）要求一个紧凑的松散环。

同族区分（对照既有棋子，非仅换色）：

- black mamba：冷钢蓝／板岩灰、无花纹、抬起 S 形脖颈；对既有褐、绿风帽、白、花纹响尾蛇、铜色蛇。
- bandit lord：满脸落腮胡、长发、抱臂、赤裸上身、绯红宽裤、金腰带／臂环、腰间佩刀；对既有光头持双刀的 bandit（橙腰带）和兜帽系。
- rogue sapper：蹲伏、卡其橄榄布、琥珀护目镜、黄铜弹簧陷阱子弹带、陷阱工具包、手持钢制捕兽夹；对既有蓝灰兜帽刺客／盗贼。
- orb weaver：淡霜蓝白、圆形腹部有同心银环（蛛网状）、细长带节腿；对既有深钴蓝带白 V 纹的 weaver patriarch、小型旋涡编织者、奶油金 queen、灰 giant spider。
- elven elite warrior：全套重甲（古铜金＋青绿珐琅）、带翅冠盔与白羽饰、上翘肩刺、塔盾青绿日轮、双刃战斧、青绿短披风；对既有较瘦的白金轻甲、持长柄斧和圆盾的 elven warrior。
- ultimate telugoroth：八角星爆时间风暴（白金核心＋放射的金色沙刃，间以琥珀、蓝宝石、紫色沙带）；对既有平面圆形彩虹漩涡 telugoroth、细长金橙火柱 greater telugoroth。
- greater teluvorta：光滑翻涌的深紫风暴云，六根长弯象牙色角围成冠，青色双眼，尘沙与沙漏碎片彗尾；对既有尖刺紫水晶球 teluvorta。
- runed bone giant：驼背，双臂放低，每块骨板刻着发光绯红符文，绯红眼窝，六枚红色悬浮符文环绕、玫瑰色微光；对既有素色骨巨人、金色重甲、淡紫光晕永恒骨巨人。
- void horror：竖立的透镜形时空裂缝，银白发光边框，靛紫星空内部含四芒星耀和星云带，裂纹与银色碎片；对既有粉色 dredgling、苍白 dredge、铬银 temporal stalker、烟雾系 dread／shadow stalker。
- swarming horror：八条银青色小型鱼形恐魔环成松散螺旋，大眼睛、针牙、薄荷色腹部；ravenous horror：一条肥硕的板岩蓝獠牙掠食者，大张的针牙嘴滴柠檬黄酸液、六只苍白眼、骨白色棘鳍扇；两者对既有单体水生棋子（墨鱼、乌贼、鳗、娜迦），彼此一群一独。
- fire wyrm：深猩红蜿蜒盘绕的远古巨龙，竖起长颈、张口、金橙喉光、角冠、半收的破碎翅膜，奶油腹板，无大火锥；对既有橙色蹲伏四足展翼带火锥的 fire drake。

## ImageGen 记录

**16／28 次**（`gpt-6.1-sol`＋`--ephemeral`，逐次串行，只用 run_imagegen.py 默认）。十二款各 1 次入选后，另四次为返工：orb weaver 首次调用 codex 结束回合但没有调用 ImageGen（`image_path` 为空，`provenance-rejected`，未入库），再 1 次入选；elven elite warrior 首图最大不透明半径 0.897（上限 0.867，未入库），缩小图形、斧头收短后入选（-2.94）；void horror 首图底盘偏移 -8.78（超 ±8，未入库），缩小并禁投影后入选（+0.56）；runed bone giant 首图过了全部阻断门控但触发 `subject_intrusion` 警告（+20.88，线 +20），母版移入 `art/monster-batch-z/superseded/`，重做一次（v2，偏移 -0.98、上偏 +3.71）后入选。每款至多 2 次。无 PENDING 请求、无豁免、未降低任何阈值。

**追加（协调者复核）**：rogue sapper v1（亮度 69.24）在 48px 读作褐色一团，经 refinement pack 9 重做（pin v1 母版与首轮记录），v2 亮度 82.36，v1 在 `superseded/`。ImageGen 合计 **17／28**，该资产 2 次。
