# 怪物棋子批次 T 选型（2026-09-30，HEAD 6da5e626，不升版）

来源：`docs/expansion-plan-20260928/MONSTER-GAP-2-20260929.md`，计分口径与批次 R／S（`art/monster-batch-r/SELECTION.md`、`art/monster-batch-s/SELECTION.md`）逐字相同：分值＝§3 逐区枚举里该身份全部区域的 E 之和，再加保证首领／剧情／任务／据点身份的加权 12。用户已确认顺序：**12.0 剧情组先于 11.3 组**（naga tide huntress、ancient elven mummy、ritch flamespitter、chitinous ritch 与 10.9 组的 gaeramarth、ninurlhing 留到下一批）。

## 范围

批次 S 的 SELECTION.md 记录的“未排批”12.0 候选共 13 个（池 E＝0，全部靠 +12 加权，因此分值同为 **12.0**；并列，按家族成套取舍）。本批取 12 个，留 1 个：

| 家族 | 身份 | 说明 |
|---|---|---|
| 商队与商人（4） | caravan merchant、caravan guard、caravan porter（keepsake-dream 静态层，各用一张 humanoid_human_spectator 系显式 image=）；Lost Merchant（thieves-tunnels 任务关友方，默认名图） | **选 4**：同为人类商人／随行，四款要靠姿势、配件与轮廓区分（帽＋钱袋、盾＋剑、背箱、蜷缩提灯），并与已有 cutpurse／rogue／thief／bandit 拉开 |
| Yiilkgur 据点（3 of 4） | Weirdling Beast（唯一首领）、Fortress Shadow（BUTLER，据点管家）、Pumpkin, the little kitty（唯一宠物） | **选 3**：三者都是据点内的固定角色，各自形体差异大（无头多足体、半透明影子、橙猫） |
| Yiilkgur 据点（**留下 1**） | **Training Dummy**（`type=training`/`subtype=dummy`，显式 `lure.png`，300000 生命的练习靶） | **留原生**：不是生物，是无阵营、无故事的练习靶；与其余三款没有形体家族，也是这 13 个里最不需要棋子身份的一个；`lure.png` 是通用诱饵图，画成“生物棋子”反而误导 |
| 后备守关／保证首领 | Nimisil（maze 后备守关，唯一）、Slasul（temple-of-creation 保证首领，唯一，tall）、Draebor, the Imp（demon-plane 保证首领，唯一） | **选 3**：三款各自独立的唯一首领 |
| 其他 | war dog（keepsake-meadow，任务同伴的战犬，与批次 S 的 Berethh／Companion Warrior／Archer 同一场景）、Yeek Wayist（halfling-ruins 末层剧情，唯一） | **选 2** |

12 个＝商队 3＋Lost Merchant＋据点 3＋Nimisil＋Slasul＋Draebor＋war dog＋Yeek Wayist。

## 选定 12 个（源码逐条重核，合同见 `evidence/monster-batch-t-20260930/source-contracts.json`）

| # | 名称 | define_as | type/subtype | 唯一 | 图像来源 | 原生贴图 | 分值 |
|---|---|---|---|:-:|---|---|---:|
| 1 | caravan merchant | CARAVAN_MERCHANT | humanoid/human | 否 | 显式 image=npc/humanoid_human_spectator02.png | 64×64 | 12.0 |
| 2 | caravan guard | CARAVAN_GUARD | humanoid/human | 否 | 显式 image=npc/humanoid_human_spectator.png | 64×64 | 12.0 |
| 3 | caravan porter | CARAVAN_PORTER | humanoid/human | 否 | 显式 image=npc/humanoid_human_spectator03.png | 64×64 | 12.0 |
| 4 | Lost Merchant | MERCHANT | humanoid/human | 否 | NPC.lua:33 默认名图 | 64×64 | 12.0 |
| 5 | Nimisil | NIMISIL | spiderkin/spider | 是 | NPC.lua:33 默认名图（base BASE_NPC_SPIDER） | 64×64 | 12.0 |
| 6 | Slasul | SLASUL | humanoid/naga | 是 | nice_tile tall（invis.png＋显式 add_mos，display_h=2） | 64×128 | 12.0 |
| 7 | Draebor, the Imp | DRAEBOR | demon/minor | 是 | NPC.lua:33 默认名图（无 base） | 64×64 | 12.0 |
| 8 | war dog | WAR_DOG | animal/canine | 否 | 显式 image=npc/canine_dw.png（与 dire wolf、corrupted war dog 同 PNG） | 64×64 | 12.0 |
| 9 | Yeek Wayist | YEEK_WAYIST | humanoid/yeek | 是 | NPC.lua:33 默认名图 | 64×64 | 12.0 |
| 10 | Weirdling Beast | WEIRDLING_BEAST | horror/eldritch | 是 | NPC.lua:33 默认名图（base BASE_NPC_HORROR） | 64×64 | 12.0 |
| 11 | Fortress Shadow | BUTLER | horror/Sher'Tul（大小写与撇号原样） | 否 | NPC.lua:33 默认名图 | 64×64 | 12.0 |
| 12 | Pumpkin, the little kitty | KITTY | animal/feline | 是 | 显式 image=npc/sage_kitty.png | 64×64 | 12.0 |

## 设计约束（生图前定的，不是事后补）

- 沿用批次 R／S 的评审教训：暗色主体在 48px 与暗盘混成一团；每个主体以中调或亮调大面为主，目标遮罩亮度 ≥65（天然苍白者除外）；评审时凡轮廓与圆盘融合的草稿一律自行淘汰。盘面措辞用“at reference lightness, a hair lighter, never darker”，不用会导致过补偿的“lighter”。姿势紧凑，所有尖端收在圆盘内四分之三。
- 商队四款互异（**轮廓**而非颜色）：merchant＝宽檐帽＋圆肚＋高举鼓胀钱袋（宽帽加圆团轮廓）；guard＝铁壶盔＋大长方盾正对前方＋长剑前指（矩形盾块）；porter＝驼背背负两只捆绳木箱（背上方块轮廓，斧下垂）；Lost Merchant＝无帽秃头灰须，蜷缩、单手高举提灯、背大背包（下蹲圆团）。对既有 cutpurse／rogue／thief／bandit（瘦削、双匕首、斗篷或秃头持匕）：本批四款都没有双匕首，也不是斗篷刺客姿势。
- Yiilkgur 据点：Weirdling Beast＝无头、四条触手作四肢（两臂两腿成 X）、躯干满是疣状肿块的实体肉色体（对既有 the-mouth、horned-horror 等红／紫触手）；Fortress Shadow＝半透明青白色钟形罩体加下垂多触须（水母形；对既有 shade-of-telos 的直立冰蓝人形、the-dreaming-one 的蓝色旋球）；Pumpkin＝橙色虎斑猫，白星胸斑，小而清楚，要放大占格（小体型也要在 48px 有存在感）。
- Nimisil：浅银灰身、背上一圈发光晶菌瘤团（青、粉、金），腿短粗放射成环（对既有 giant-spider 黑灰、ungole 全黑、fate-spinner 钢蓝锯齿腿、weaver 系）。Slasul：正面直立雄性那迦，铜冠盔带鳍冠、胸口大珍珠、圆盾与重锤，尾部盘成底座（对既有 naga-myrmidon 的持三叉戟蓝尾、tidewarden 的棕色持盾、nereid、zoisla、nashva、tidecaller，另加金饰与冠盔的轮廓）。Draebor：灰毛蹲踞的恶作剧小魔，宽脸尖牙（native 是灰色毛团）；手中冒火苗作施法姿势（对既有 quasit 的持盾牛头小魔、water-imp 的青蓝小魔、wretchling 的黄绿）。Yeek Wayist：白毛长臂的叶克，一柄大剑悬浮在身前（不持握）（native 特色），与已有 yeek 无先例。
- **war dog 必须与两个同 PNG 的棋子在 48px 清楚区分**：dire wolf＝棕毛长吻侧向踱步；corrupted war dog＝灰毛紫绿裂纹张口扑击、尖刺项圈。war dog＝**沙黄／奶油色短毛獒犬**，正面朝观者低头蹲踞的“顶住”姿势（前腿撑开，宽肩），短宽吻、垂耳，**铆钉皮胸甲＋链甲护面／红色布披挂**；轮廓是宽肩三角＋正对观者的宽脸，而非侧影，且色调是暖亮的沙黄（与棕、灰两款拉开明度与色相，也不靠单色）。
