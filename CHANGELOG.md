# Changes

## 0.6.32 — 2026-10-01

- 怪物 Batch AD、AE、AF、AG、UA、TA-1、UB-1、UB-2（棋子目录 376→**462** 款，共 86 款，本版无新增地形区域）。名单外地城常见怪（AD／AE／AF，如 dúathedlen、daelach、forge giant、storm wyrm、各档 lich 与恐魔）、特殊情况（AG：同名 shadow claw 一对、multi-hued drake 系与水晶）、首领（UA：Kra'Tor、Khulmanar、Rungof、Grgglck、Queen Ant、Ak'Gishil、Ninandra、Phoenix、Ukruk、Gorbat、Grushnak、Vor）、城镇居民（TA-1：Angolwen 四位高图法师与学徒、六种守卫、Ring of Blood 的 slaver 与 enthralled slave）、唯一怪（UB-1：High／Fallen Sun Paladin Aeryn、Caldizar、Chronolith Twin／Clone、Temporal Defiler、Corrupted Daelach、Linaniil、Archmage Tarelion；UB-2：Sun Paladin Guren、Epoch、Corrupted Oozemancer、Zemekkys、Blood Master、Limmir、Protector Myssil、Rak'Shor Cultist、Shady cornac man、Tannen，以及复用憎恶棋子的 Ben Cruthdar, the Cursed）。多款高大原生图只画一枚棋子；所有新棋子均以原版贴图为准重绘并在 48 px 下与同族区分。
- 召唤别名：野性天赋蜘蛛体、void shard、orc spirit、邪恶子嗣（Vilespawn）、Risen Ghoul、walking corpse 与 Blood-Edge 神器召唤的 animated blood 按身份换棋子；别名只认原生构造函数产出的真实召唤字段，唯一怪与带 `define_as` 的演员保持原版。Vilespawn 与 animated blood 的匹配改用固定的 blight 100／nature -100 抗性对（而不是会随等级增长的 max_vim）。
- 时空复制：时空法师的悖论分身（makeParadoxClone，含异常目标）现在覆盖全目录的非唯一条目，复制体戴被复制身体的棋子，唯一怪保持原版。
- 修复：调试「地图全开」与魔法探图类效果（magic map、检测）揭示的棋盘石质格此前会保持空白，现在会立即重建。
- 地形可读性（不新增区域）：黑暗之心与深渊咆哮的菌林墙改为清晰俯视墙顶并分离地板／墙（gloomy／plain ΔE 由约 6–8 提升到约 28）；沙虫巢穴、迷宫与闪光洞穴墙增加亮唇／接触暗边；Kor'Pul 与 Kor'Pul-dark 在不改任何明度门限的前提下改用暖地板／冷砖色相分离（ΔE 约 10→28）。
- 语言：地形设置说明 73 个区域／城镇名再次对照 `mod-tome.lua`，全部命中，无修正。
- 外测指南（新建 `docs/external-test-v0632/`）更新。正式归档、安装冒烟与测试见 [0.6.32 证据](evidence/runtime-v0632/README.md)。

## 0.6.31 — 2026-09-30

- 怪物 Batch Z–AC（棋子目录 323→**376** 款，共 53 款，无新增地形）：Z（black mamba、强盗首领、球蛛编织者、精英精灵战士、究极泰鲁戈洛斯、强化泰鲁沃塔、符文骨巨人、虚空恐魔、群生恐魔、贪婪恐魔、盗贼工兵、火焰巨龙）、AA（究极法罗、兽人狂战士、挖掘魔首领、北极熊、anaconda、究极泰鲁沃塔、necrotic abomination、bone／sanguine horror、barrow wight、ogre warmaster、dreadmaster）、AB（entrenched／boiling horror、兽人召唤师、巨型木乃伊、暗影之刃、精英兽人斗士／狂战士、猛毒巨龙、敌方炼金傀儡、虫群巢穴、森林巨魔野法师、究极西弗格罗斯）、AC（Aletta Soultorn、ruin banshee、Filio Flightfond、高阶兽人烈焰／冰霜术士、Glacial Legion、Arch Zephyr、Rotting Titan、Heavy Sentinel、Void Spectre、oozing／abyssal／umbral horror、ungolmor、吸血鬼领主、degenerated ogric mass、ogric abomination）。其中多款为 native-tall（高大原生图），只画一枚棋子。
- 规则：盗贼工兵（rogue sapper，`THIEF_SAPPER`）与刺客（assassin）共用同一张原生图，按名字各自换棋子；暗影之刃（shadowblade）与刺客同为 `THIEF_ASSASSIN`，同样按名字分辨，竞技场里无 `define_as` 的同名版本保持原生；玩家炼金傀儡保持原生（敌方 alchemist golem 叶子戴棋子）；Corpathus 神器召唤的邪恶子嗣（Vilespawn）保持原生；训练用傀儡（Training Dummy）保持原生；随机首领的 fire wyrm 保持原生。召唤物按自身身份显示棋子：强盗首领（bandit／thief／rogue）、Necromancer 的 Dread 天赋（dreadmaster 仆从）、虫群巢穴（swarming horror）、兽人召唤师的野性天赋（minotaur、ritch flamespitter；giant spider 无棋子）、吸血鬼领主（随机亡灵）。
- 语言：地形设置说明中的“卡·普尔”改为官方“卡·普尔废墟”（简繁）；说明中全部 73 个区域／城镇名已对照 `mod-tome.lua` 核对。
- 外测指南（新建 `docs/external-test-v0631/`）更新。正式归档、安装冒烟与测试见 [0.6.31 证据](evidence/runtime-v0631/README.md)。

## 0.6.30 — 2026-09-30

- 怪物 Batch T–Y（棋子目录 251→**323** 款）：T（商队、迷路商人、战犬、Yeek Wayist、Nimisil、Slasul、Draebor、Weirdling Beast、Fortress Shadow、Pumpkin 等剧情组）、U（娜迦、里奇、木乃伊、兽人刺客大师、火焰小鬼等）、V（黑水晶、faerlhing／losselhing、dredge、drem master、兽人三法师等）、W（兽人龙战士、熊、重型骨巨人、蚁、banshee 等）、X（酸蚁／行军蚁、assassin、greater telugoroth、dread 等）、Y（uruivellas、thaurhereg、orc corruptor、temporal stalker、两种傀儡、blade horror、蠕动的裹尸布、grizzly bear、weaver patriarch、luminous horror、necrotic mass；玩家炼金傀儡保持原生）；召唤物与同体形沿用棋子。
- 地形：TW7（城镇石板路、伊格／安格利文耕地、晨曦之门棕榈）、S10a（格鲁希纳克部落、史莱姆通道、淤泥巢穴，新黏液族）、S10b（沃尔部落，新哥特族）、S11（拉杆、拉杆门、沃尔蜡烛）、S12（伤害岩浆地面、沃尔军械库深水）、S13（阿尔德胡格不稳定虫洞、恐惧王座／巅峰深水）、S14（传送门／远行传送门、巅峰法球门与圣所门）、S15（教程 L1、梦境 L1）、S16（天赋位面换层钩子、恶魔空间法术位面、时空避难所）、S17（梦境空间，新云地板族）。设置说明（棋盘地形）列出新增区域，中英文键结构一致。
- 本版不含：竞技场、无尽地下城；永恒／星系／梦境 L2 保持原生。
- 地名修正：地形设置说明中 9 个区域中文名改为官方译名（古老树林、斯拉伊什沼泽、罗兰精灵营地、恐惧王座、深渊咆哮、不起眼的洞穴、黑暗地宫、宁静的草地、布莱亚的巢穴），简繁同步。
- 外测指南（新建 `docs/external-test-v0630/`）更新。正式归档、安装冒烟与测试见 [0.6.30 证据](evidence/runtime-v0630/README.md)。

## 0.6.29 — 2026-09-29

- 怪物 Batch O–S（棋子目录 191→**251** 款）：O（泥怪、巨型虫、小白兔等 12 款）、P（雪巨人、米诺陶、山岭巨魔、食人魔、孔克雷夫治疗师 12 款）、Q（龙幼仔、成年龙、Rantha、Briagh、Ukllmswwik 12 款）、R（quasit、编织者、兽人系、蚁、战犬、Gnarg、Rak'shor、grannor'vor 12 款）、S（太阳骑士、Charred Scar 精灵、Keepsake 同伴、亡灵唯一怪 12 款）。
- 召唤物与同体形沿用棋子；Rak'shor 与卡·普尔之怒开启乌鲁洛克之焰形态（05a9caaa）。
- 地形：城镇 TW4–TW6（夏特尔、零点圣域、晨曦之门、伊尔克；11 座城镇全部覆盖）、S5（阴影地宫、泰恩之塔、伊塞尔森·月之谷、鲜血之环、德斯竞技场）、S6（艾露安、加伯特部落）、S9（巅峰 L1–L11）、S2（楼梯／宝库门／洞穴门／静态道具）、S4（水下空气泡、带回调祭坛）、S8（Kor'Pul 暗砖墙与恶魔空间玄武岩）。设置说明（棋盘地形）列出新增城镇与区域，中英文键结构一致。
- 外测指南（新建 `docs/external-test-v0629/`）更新。正式归档、安装冒烟与测试见 [0.6.29 证据](evidence/runtime-v0629/README.md)。

## 0.6.28 — 2026-09-29

- 怪物 Batch J–N（棋子目录 131→**191** 款）：J（保证首领／唯一怪 11 款，含 Grand Corruptor 恶魔形态与精灵教徒形态）、K（水生／蛛形／食尸鬼等 12 款）、L（兽人、沙洛尔精灵、纳迦等 12 款）、M（元素与 Fyrk 等 13 款）、N（吸血鬼、亡灵 12 款）。
- 地形：S3（Old Forest 晶簇、森林区石质密室、LAKE_NUR 出口）、S1（事件光环环补齐）、TW1（德斯、伐木工人的小村庄、城镇记忆格安装）、TW2（最后的希望、埃尔瓦拉）、TW3（伊格、安格利文、钢铁议会；原生层标志修复）。设置说明（棋盘地形）列出新增城镇，中英文键结构一致。
- 外测指南（新建 `docs/external-test-v0628/`）更新。正式归档、安装冒烟与测试见 [0.6.28 证据](evidence/runtime-v0628/README.md)。

## 0.6.27 — 2026-09-29

- 纳入已提交的怪物 Batch H（`1a476f1` 十二款 + `f5f01d6` 实机验证）：sandworm、sandworm destroyer、sandworm burrower、white crystal、red crystal、crimson crystal、poison ivy、honey tree、Necromancer、fleshy experiment、boney experiment、sanguine experiment。
- 纳入已提交的怪物 Batch I（`d118b15` 十二款 + `33ac5a2` 实机验证）：green ooze、crimson ooze、gelatinous cube、Malevolent Dimensional Jelly、Fragmented Essence of Harkor'Zun、Harkor'Zun、Burb the snow giant champion、Norgan、slimy crawler、Spellblaze Simulacrum、Kryl-Feijan 侍僧、Z'quikzshl。棋子目录 107→**131** 款。
- 修复（`32f4ec5`）：`CheckerTokens.nativeTallImage` 忽略 Stone Skin 等 `_isshaderaura` 光环条目（仍要求恰有一个未改动的高体）。此前 Harkor'Zun 在怪物棋子 Native→Refined 开关往返后回退原生。
- 无地形改动。外测指南（新建 `docs/external-test-v0627/`）更新棋子数量、新增棋子和修复说明。正式归档、安装冒烟与测试见 [0.6.27 证据](evidence/runtime-v0627/README.md)。

## 0.6.26 — 2026-09-29

- 纳入已提交的怪物 Batch G（`7abe2cf` 十一款 + `bf4ba5c` Massok 经评审批准的底盘偏移豁免接入并实机验证全批）：xhaiak arachnomancer、shiaak venomblade、dremling（浅灰石像重绘）、Massok the Dragonslayer、The Master、Pale Drake、Spellblaze Crystal、Rhaloren Inquisitor、Krogar、Fillarel Aldaren、Harno, Herald of Last Hope、Lithfengel，棋子目录 95→**107** 款；实机复核见 `evidence/monster-live-g-20260929/README.md`。
- 无地形改动。外测指南（新建 `docs/external-test-v0626/`）仅更新棋子数量与新增棋子说明。正式归档、安装冒烟与测试见 [0.6.26 证据](evidence/runtime-v0626/README.md)。

## 0.6.25 — 2026-09-29

- 纳入已提交的怪物 Batch D（`2caaade`/`13e04b2`）：red/blue jelly 补齐六色果冻族；六色巨蚁全部上线（brown/blue ant 经评审豁免，carpenter/black ant 重新设计后上线），棋子目录 70→78 款；实机复核见 `evidence/monster-live-d-20260929/README.md`。
- 纳入已提交的怪物 Batch E（`a3e6fc7` 五款直接过审 + `b536d68` 豁免批准 + `a5a7420` 接入七款豁免并实机验证全部十二名首领）：12 个地城终层首领全部接入（Lady Zoisla、Urkis、Golbug、Brotoq、Ungolë、Half-Finished Bone Giant、Kryl-Feijan、Atamathon、Ritch Great Hive Mother、The Mouth、The Abomination、Celia），其中 7 款经评审批准的底盘偏移豁免接入，目录 78→90 款；实机复核见 `evidence/monster-live-e-20260929/README.md`。
- 纳入已提交的怪物 Batch F（`6965a17` naga tidewarden/tidecaller／treant／重绘 Kryl-Feijan + `d90c791` + `a0fda3d` 接入 shivgoroth 豁免对并实机验证全批）：naga tidewarden/tidecaller、treant 直接过审，shivgoroth/greater shivgoroth 经评审豁免接入，Kryl-Feijan 重绘（旧图 48px 深色地板下几乎读作纯黑团块，新图亮度 +44%，撤销原豁免），目录 90→95 款；xhaiak arachnomancer/shiaak venomblade 仅做运行时探针，未接入目录；实机复核见 `evidence/monster-live-f-20260929/README.md`。
- 无地形改动。外测指南、README 与 Game Options 棋盘地形说明未改动文案（仅棋子数量更新）。正式归档、安装冒烟与测试见 [0.6.25 证据](evidence/runtime-v0625/README.md)。

## 0.6.24 — 2026-09-29

- 纳入已提交的怪物 Batch C（`533341a`）：新增 skeleton master archer（棋子目录 69→70 款），重绘 skeleton archer 与 Horned Horror 以提升可分性；实机复核见 `evidence/monster-live-c-20260929/README.md`。
- 纳入地形批次 4（`688f3eb`）：宁静的草原 L1–L6、孔克雷夫实验室 L1–L4、剧毒火山 L1–L2、穆格尔巢穴双布局三层、南方海滩 L1；随后视觉返工（`87a35e4`）：火山毒水、丛林树、海滩树／沙。
- 纳入地形批次 5（`fdaee0f`）：泰尔玛废墟 L1–L5、精灵废墟 L1–L3、沃尔军械库 L1–L2、布莱亚弗巢穴、隐秘山谷洞穴、淹没的洞穴、造物者神庙、灼烧之痕、恶魔空间、夏·图尔堡垒。
- 纳入拉克·肖部落骨质地形（`7fb72f9`）：L1–L3 骨质地面、墙、门、梯子与世界出口接入新 `rakshor` 组。同一提交内的兽人育种棚 L2–L3 可读性返工（独立 `gloom/pit` 地板／墙组）保留在源码中，但该地城在当前游戏中已不可进入，不计入本轮覆盖声明。
- 外测指南和 README 更新；Game Options 棋盘地形说明未改动文案。正式归档、安装冒烟与测试见 [0.6.24 证据](evidence/runtime-v0624/README.md)。

## 0.6.23 — 2026-09-29

- 纳入已提交的虚空／时空地形（`c19e080`）：混沌之沼 L1–L3、次元浮岛 L1–L3、时空裂隙 L1–L4；T5（`850ba0e`）：纳尔湖 L2–L3 水下与干燥石质格、最后的希望墓地石路／沼泽树、次元浮岛焦树；虚空墙返工与墓园墓碑／棺材／墓堂入口棋盘图（`b2a22e2`）。虫洞、空气泡、祭坛及带剧情规则的格子保持原版。
- 纳入怪物 Batch A（`7e5cd52`）与 Batch B（`f8ba3d8`）共 15 款棋子，目录由 54 款增至 69 款；实机验证见 `eb2b416`。skeleton master archer 与未核准亡灵保持原版。
- 外测指南和 README 更新；Game Options 棋盘地形说明的英文原键与简繁精确键已核对一致。正式归档、安装冒烟与测试见 [0.6.23 证据](evidence/runtime-v0623/README.md)。

## 0.6.22 — 2026-09-28

- 纳入已提交的第三批地形复用（`d53cb11`）：Ritches Tunnels L1–L3、The Deep Bellow L1–L3、Last Hope Graveyard L1–L2；以及 Mark of the Spellblaze L1–L2 的焦土、焦树、抬岸阻挡熔岩及出口（`6db8e5a`）。特殊格、墓地墓碑和不符合精确合同的地格保持原版。
- Game Options 棋盘地形说明的英文原键与简繁精确键同步；外测指南和 README 更新。正式归档、安装冒烟与测试见 [0.6.22 证据](evidence/runtime-v0622/README.md)。

## 0.6.21 — 2026-09-28

- 纳入已提交的 Unremarkable Cave 单层洞穴地形（`d67e5f9`）、零新图复用第一批五区（`9c6e8a2`）与第二批六区及纳尔湖 L1 地表（`b90bf63`）。经来源、身份、规则与外观合同核对的格子显示棋盘贴图；不支持的特殊格与纳尔湖 L2–L3 水下／石质格保持原版。
- Game Options 棋盘地形说明的英文、简体、繁体精确键已核对；README 与外测安装说明更新为 0.6.21。正式归档、实机冒烟、逐字节校验及测试见 [0.6.21 证据](evidence/runtime-v0621/README.md)。

## 0.6.20 — 2026-09-28

- 汇入已提交的迷宫双布局（`5188942`，裂隙返工 `4a7fe99`）、黑暗之心双皮肤（`20e8d1f`）、沙虫巢穴双布局（`d01f67a`）与闪光洞穴双布局（`1dbec49`）地形。仅经身份与外观核对的格子绘制棋盘贴图，其他格保留原版。
- Game Options 的棋盘地形说明及简繁中文精确键列出四片新区和简化模式的格子范围；外测指南与 README 同步更新。正式归档、实机冒烟和校验结果见 [0.6.20 证据](evidence/runtime-v0620/README.md)。

## 0.6.19 — 2026-09-28

- 将 0.6.18 之后已审核提交的事件道路光环修正（`0abe2cc`）、诺尔格斯巢穴双布局 L1–L3 雪岩地形（`179544e`）、岱卡拉双布局 L1–L4 裸岩／山墙／无害熔岩地形（`df5fbf2`）和事件光环格默认柔和／可选适中色边设置（`b5658b7`）合并为外测版本。未知或不支持的地格仍保持原版。
- 更新 Game Options 棋盘地形说明及简繁中文精确键，列明两片新区及简化模式范围；地名沿用游戏已有译名「诺尔格斯巢穴／諾爾格斯巢穴」和「岱卡拉」。更新 README 与外测安装说明。
- 在隔离离线夹具中，以正式 TEAA 独立冷启动核验诺尔格斯巢穴 L1、岱卡拉 VOLCANO L4 和 Trollmire 事件光环格；英文、简体、繁体设置页及默认柔和状态见 [实机证据](evidence/runtime-v0619/README.md)。

## 0.6.18 — 2026-09-28

- 修复原生随机事件 `cloneFull` 改写名称与站立回调后，棋盘森林草地／花地／道路和来源校验的石地板落回原生贴图的问题。森林基础身份按 `define_as` 与规则／外观门控识别，容忍本地化光环后缀；石质来源签名仅放宽事件改写字段，原生 `on_stand_safe` 的两种事件另作精确例外。其他身份或额外视觉变化继续原生。
- 加入默认关闭、仅离线夹具可切换的每格淡色遮罩 A/B；不新增游戏选项、存档设置或规则。三张程序生成遮罩从运行时代码可达，随 TEAA 发布。原生粒子环、提示名和小地图颜色保持独立。
- 24 次独立夹具事件／地表检查绘制 465/465、受支持格原生回退 0；简繁中文冷启动、原生 DIG 后绘制及站立回调、48/64/96px A/B 见 [实机证据](evidence/runtime-v0618/README.md) 和 [视觉对照](evidence/aura-ab-20260928/README.md)。

## 0.6.17 — 2026-09-28

- Dreadfell L1–L9 接入 Kor’Pul 已有石质逐格适配器，仅匹配来源印章与最终状态合同的 basic.lua 格；路牌、密室改写格和其他身份仍保持原生。没有新增美术，也没有修改地形规则。
- 更新设置说明及简繁中文精确键；加入 Dreadfell 身份、原生回退、模式往返和挖掘修复测试。隔离夹具逐层与回归验证见 [实机证据](evidence/runtime-v0617/README.md)。

## 0.6.16 — 2026-09-28

- Rhaloren Camp DEFAULT／OVERGROUND L1–L3 接入现有石质与森林地形贴图；OVERGROUND 同层逐格由来源签名匹配的 basic.lua 石质身份或森林身份拥有，特殊密室和已改写身份保留原生。共用静态 L3 也在两种布局下核对。
- 地形模式切换和原生重铺后的森林格修复现在覆盖 Rhaloren；石质格继续由观察时的逐格适配器修复。Blockout 只覆盖森林格，石质格保持原生。地形规则、门和楼梯交互不变。
- 纯 Lua、生产测试、死资产审计及隔离夹具 11 次摆位通过；详见 [实机证据](evidence/runtime-v0616/README.md)。

## 0.6.15 — 2026-09-28

- **G0 Old Forest 与 Slazish Fens 地形接入。** 两个地城复用现有森林/水体贴图，
  零新美术。`overload/mod/class/CheckerTerrain.lua` 的森林适配器门控从单一
  `zone.short_name=='trollmire'` 换成显式白名单
  `{trollmire, old-forest, slazish-fen}`；`terrain()`/`terrainImage()` 新增
  一个按调用方 zone 传入的 `allowDarkGrass` 参数——只有 `old-forest` 会把
  `subtype=='dark_grass'` 折算成 `grass` 分支（Old Forest DEFAULT 布局的
  GRASS/TREE/HARDTREE 自带一份 `subtype=dark_grass` 的独立定义，字段规则与
  CRYSTALINE/Trollmire 完全一致，只是贴图选择不同）；Heart of the Gloom 自己
  的 TREE 也用 `dark_grass`，但其 zone 不在白名单里，因此仍保持原生，不受
  影响。Old Forest 两种布局（DEFAULT／CRYSTALINE）、L1–L4 全部支持；
  Slazish Fens 三层全部支持，直接复用 Trollmire FLOODED 已验收的
  `bog-tree`/`bog`/`bog-misc`/`exit` 身份，`PORTAL`（`name` 被改写为
  "coral portal"）按设计保持原生。`LAKE_NUR`（Old Forest L4）没有 `subtype`
  字段，天然不落入任何分支，也保持原生。Blockout 模式与精修模式共享同一个
  zone 白名单，因此两个新区域在两种模式下都可用。
- **Game Options 文案。** `hooks/load.lua` 的地形说明改为列出 Trollmire、
  Old Forest、Slazish Fens 三片森林（含 Trollmire 洪水版与 Old Forest
  水晶布局），并说明 Blockout 支持同一批区域而不再是"仅 Trollmire"；
  `data/locales/zh_hans.lua`／`zh_hant.lua` 按精确原文 key 同步更新简繁
  翻译。
- **测试：** `tests/terrain_contract.lua`（+20 项）覆盖 Old Forest 两种布局
  的 dark_grass/grass 身份、LAKE_NUR 保持原生、Slazish Fens 的
  bog-tree/bog/bog-misc/exit 与 PORTAL 保持原生，以及 Heart of the Gloom
  的 dark_grass TREE 不受 zone 别名影响；`tests/terrain_repair.lua`
  （+4 项）覆盖两个新区域挖掘后的自动修复；`tests/runtime_modes.lua`
  （+7 项）通过真实 `game:checkerApplySettings()` 路径复核同一组场景。
  `tests/live_map_survey.lua` 的 `M.enter` 新增 `crystaline` 布局强制
  开关（复用 Kor'Pul HIDEOUT／Trollmire FLOODED 的
  override-then-restore 技巧），census 谓词按 zone 折算 `dark_grass`，
  并新增一个不限定水体家族的通用 `M.digTree()`。全部 Lua 单元测试、
  `python3 -m unittest discover -s tests/production -q`（52 项）与
  `python3 tools/audit_dead_assets.py --check` 均绿；本轮零新增/零死资产。
- **实机**（[evidence/runtime-v0615](evidence/runtime-v0615/README.md)）：
  隔离夹具，`tests/live_map_survey.lua` 强制 Old Forest DEFAULT／CRYSTALINE
  各 L1–L4（共 8 次摆位）、Slazish Fens L1–L3（3 次摆位），加 Trollmire
  DEFAULT／FLOODED L1 与 Kor'Pul DEFAULT L1 三次回归摆位，共 14 次；地毯式
  统计全部 `native=0`（among 已识别身份），模式往返（vanilla 全部释放／
  refined 全部重装）逐次核对；Old Forest DEFAULT L1 对一棵 dark_grass TREE、
  Slazish Fens L1 对一棵 BOGTREE 各做一次原生 DIG，`NicerTiles` 既有的自动
  修复钩子无需手动调用即把画面换成对应的 grass/bog 图。20 张 1920×1080
  未编辑截图（含 48/64/96 三档各一组），逐张目视核查，画面干净，`Lua Error`
  计数 0。确认保持原生且符合预期的身份：Old Forest 的 `LAKE_NUR`（L4，每
  层恰好 1 格）、各 lesser_vault 内的 basic.lua 石地板/墙/门与（CRYSTALINE
  专属）underground.lua 晶洞地板/墙、以及被 vault aura 改写过 `name` 的
  草地格（如 "grass (antimagic aura)"，因 `name` 不再等于纯 `grass` 而不
  匹配）；Slazish Fens 仅 `PORTAL` 一项，符合设计预期（Slazish Fens 没有
  `lesser_vault` 配置，密室相关的原生残留面比 Old Forest 小得多）。
- **打包：** `dist/tome-checker-revised-0.6.15.teaa`，TEAA 冒烟测试通过
  （归档形式加载 Old Forest 一层，census `native=0`，`Lua Error` 计数 0）；
  外测 ZIP 同步更新到 0.6.15，安装说明见
  `docs/external-test-v0615/INSTALL.zh-CN.md`。SHA256 见
  `evidence/runtime-v0615/README.md`。
- **边界：** 只核验了单进程内 14 次摆位与两次挖掘；密室内容（honey_glade、
  troll-hideout、bandit-fortress 等）未逐一进入验证，均按设计保持原生；
  两个区域整片贴图的连片观感（大块 `tree-*`/`bog-tree` 拼图）留给后续人工
  美术复核。

## 0.6.14 — 2026-09-28

- **F1 洪水沼泽地形接入。** Trollmire FLOODED 布局新增三种身份：`bog-tree`
  （沼泽柳树，两款风格变体 a/b）、`bog`（沼泽浅水）、`bog-misc`（沼泽装饰，
  芦苇丛/苔藓团/浮木三种，rule-identical 于 `bog`，只多一层原生
  `add_displays`）；`hardtree`（硬树，DEFAULT/FLOODED 共有）改用独立贴图，
  不再借用普通 `tree` 的画面。生图 6 项（bog-tree-a/b、bog-misc-1/2/3、
  hardtree），实际消耗 8 次调用（含一次门控修复前的误判、一次门控修复后的
  重新实测）：`bog-misc-1/2/3` 各一次首轮通过；`bog-tree-a/b` 各两次调用中
  取可用产物（首次被不适用的怪物圆盘门控误判，门控修复后原图复核也通过，
  但记账入库的是同一任务包第二次调用的字节，内容等价）；`hardtree` 两次
  调用均以 <1.1px 之差未过 A8.1 不贴边判据，按逐资产文档化豁免入库（见
  `art/production/waivers/a8-edge-margin.json`）。完整调用来源、门控实测、
  视觉复核见 `art/terrain-f1-flooded/REVIEW.md`。
- **门控修复：** `tools/run_imagegen.py` 新增按 `kind` 分流的 `terrain_gate()`
  （A1/A2/A8），terrain-prop/floor 不再套用只为怪物棋子圆盘几何设计的
  `check_token_style`；新增 `CORNER_ALPHA_MAX=4`（三次独立生成同一角落
  alpha=1 的编码器伪影容差）与 `bog-misc` 前缀的接地豁免。改动依据、实测
  数据与豁免记录见 `docs/g0-terrain-contract-20260927/ACCEPTANCE.md` §7。
- **导出：** `tools/export_forest_terrain.c` F1 分支支持两款 `bog-tree`
  风格变体与可选的 `hardtree`（母版缺失时该身份保持原生，不影响其余产出）；
  本轮导出 72 张运行件（`bog-tree-a/b`×64、`bog-misc`×6、`tree-hard`×2）
  写入 `data/gfx/refined/`，未触碰既有的 78 张非泛滥森林瓦片。
- **运行时（`overload/mod/class/CheckerTerrain.lua`）：** `terrain()` 改为按
  `define_as`（BOGTREE 及 BOGTREE\<N\>）/`add_displays`（区分 BOGWATER 与
  BOGWATER_MISC）等原生字段识别身份，不再读 `zone.is_flooded`；`applyForest`
  的放行条件从 `zone.short_name=='trollmire' and not is_flooded` 简化为
  `zone.short_name=='trollmire'`。水体掩码按"同一水体家族"语义：`bog`/
  `bog-misc`/`bog-tree` 互相计入掩码位，`deep` 保持独立家族（不与 bog 系互认），
  两者互不相通。Blockout 模式同步支持洪水身份（`bog`/`bog-misc`/`bog-tree`
  映射到既有的 blockout 水贴图，`hardtree` 映射到既有的 blockout 树贴图）。
- **修复一处选图公式缺陷（本轮实现中发现，非历史遗留）：** `bog-tree` 风格
  变体最初按 `(x*17+y*7)%2` 选择，与棋盘奇偶 `(x+y)%2` 代数恒等（两个系数都
  是奇数），导致风格永远和奇偶绑定，导出的 64 张 `bog-tree-a/b` 运行件里有
  32 张（style/parity 的另外两种组合）永远不会被选中。改为按 `x%2` 选择后
  与奇偶解耦，`python3 tools/audit_dead_assets.py --check` 从"32 个死资产
  （1.10 MB）"变为"none"，无需改动审计工具本身的推导逻辑。
- **单元测试：** `tests/runtime_modes.lua`（153 项）、`tests/terrain_contract.lua`
  （251 项）、`tests/terrain_repair.lua`（37 项，新增原生 DIG 把 BOGTREE
  变成 BOGWATER 的集成修复用例）均扩展了洪水身份覆盖并保持全绿；
  `tests/live_map_survey.lua` 的森林身份镜像同步更新（补上 BOGTREE 的
  `define_as` 判定），新增 `M.digBogtree()`/`M.focus()`。
- **文案与本地化：** `hooks/load.lua`、`data/locales/{zh_hans,zh_hant}.lua`、
  `init.lua` 的地形选项说明不再提"non-flooded"，改为明确 Refined 同时支持
  洪水与非洪水版 Trollmire；`README.md` 同步更新。
- **实机**（`evidence/runtime-v0614/README.md`）：隔离夹具，`tests/live_map_survey.lua`
  强制 Trollmire FLOODED L1/L3、FLOODED 区域对象下的静态藏宝图 L4、以及
  DEFAULT L1 回归对照，共四次摆位；地毯式统计 `supported=owned`、`native=0`
  （2590/2590、2598/2598、397/397、2427/2427），`vanilla`/`refined` 模式往返
  逐一验证；FLOODED L1 用与 `tests/live_terrain_repair.lua` 相同的原生 DIG
  入口挖掉一棵 BOGTREE，原生日志输出"Tree turns into bog water."，画面
  从 `bog-tree-b7-0-0.png` 自动换成 `bog7-0-0.png`（`NicerTiles` 既有的
  `checkerRepairTerrain` 自动挂钩，未手动调用修复接口）；48/64/96 三档 +
  一张挖掘聚焦共 13 张 1920×1080 未编辑截图，全程 `Lua Error` 计数 0。
- **打包：** `dist/tome-checker-revised-0.6.14.teaa`，SHA256
  `8587ff5b9e14f3cd0ffbdd1cfd561967d5d1c07951d32e386ec948bf13c5c6e8`；PNG 全部
  ZIP_STORED 且与源码逐字节一致。TEAA 冷启动冒烟
  （`evidence/teaa-install-20260928-v0614/README.md`）：`--teaa
  checker-revised=...0.6.14.teaa` + 强制 FLOODED L1，`Binding addon` 日志确认
  以归档形式加载，census `native=0`，`Lua Error` 计数 0。外测 ZIP
  `dist/tome-checker-revised-external-test-0.6.14-hud-0.2.7.zip`，SHA256
  `72f5b36e781ded8cd29736bfc73b0e7278ca756748da6248a165fb28686eb4a2`；沿用 HUD
  0.2.7（未改动），安装说明
  `docs/external-test-v0614/INSTALL.zh-CN.md`。
- **边界：** 只核验了 Trollmire 单一进程内的四次摆位与一次挖掘，未测自然
  生成的多层连续游玩、存档/读档；FLOODED L3/L4 未额外做挖掘核验（L1 已证明
  集成挖掘路径本身，不依赖具体摆位）；`bog-tree`/`bog-misc` 铺成整片水域的
  拼图观感（B5）与精修格贴在原生格旁边的交界表现（B9）超出本轮截图范围，
  留给后续实机夹具验证，见 `art/terrain-f1-flooded/REVIEW.md` §4。

## 0.6.13 — 2026-09-28

- **E1 胶质接入（46→54）：** green/black/white/yellow jelly（`immovable/jelly`，
  固定不动，无 `can_multiply`/`clone_on_hit`）与 black/yellow/red/blue ooze
  （`vermin/oozes`，会移动，`clone_on_hit={min_dam_pct=15,chance=30}`）。
  生图前准入见 `evidence/e1-art-gate/`：8 项解析后显示修饰逐项为空，当前匹配
  理由均为 `no-art`。8 次调用全部首轮通过风格门控，0 次返修、0 次剔除；
  可分性复核（含最弱的 black jelly / black ooze 一对如实记录）见
  `art/monsters-e1-gel/REVIEW.md`。
- 实机（`evidence/runtime-v0613/`）：隔离夹具 Trollmire，8 新 + 2 已映射风格
  锚点（green mold、green worm mass）摆位，48/64/96 三档 + 原生对照共 5 张
  1920×1080 未编辑截图，`Lua Error` 计数 0；额外用与 `tests/live_shields.lua`
  相同的原生物理伤害入口对 black ooze 做了一次真实 `clone_on_hit` 分裂核验，
  原生日志输出"Black ooze splits in two!"，克隆体获得独立安装的棋子与自己的
  阵营圆环（`display_uid` 与父体不同）。
- 修复 `tests/production/test_art_tasks.py` 的 `PlayerKindTests` 因
  `overload/mod/class/CheckerPlayerTokens.lua` 在 0.6.12（`294b497`）改动而
  过期的 SHA-256 引用锁定（该改动只涉及光环显示分支，未触碰这批引用实际依赖
  的 `M.families`/`M.moddable`/`M.keys` 玩家身体族表）；`python3 -m unittest
  discover -s tests/production -q` 恢复全绿。
- 打包 `dist/tome-checker-revised-0.6.13.teaa`；PNG 全部 ZIP_STORED 且与源码
  逐字节一致。TEAA 冷启动冒烟确认以归档形式加载，8 新棋子渲染正常，
  `Lua Error` 计数 0。外测 ZIP 沿用 HUD（未改动），安装说明见
  `docs/external-test-v0613/INSTALL.zh-CN.md`。SHA256 见 `PROGRESS.md`。

## 0.6.12 — 2026-09-28

- **原生 shader 光环下保留棋子。** 怪物棋子与玩家棋子此前只要 `shader_auras`
  非空（原生 `addShaderAura`）就会整体退回原生美术；现在光环无论在棋子安装前还是
  之后施放，棋子都会保留，光环改为围绕棋子贴图本身重新生成（复用原生
  `updateModdableTilePrepare` 的非可换装分支）。关闭棋子开关时光环正确回到原生
  贴图，重新打开时光环正确回到棋子贴图，`add_mos` 记账条目（`_isshaderaura`）
  不重复、不残留。
- 单元测试更新（`tests/token_mapping.lua`、`tests/player_tokens.lua`、
  `tests/random_identity.lua`）覆盖新契约：光环前/后安装、重复刷新不重建、
  移除棋子后原生光环回归；纯 Lua 13 组回归全部通过。
- 实机验证（4 款光环样本：`stone_skin`/crystalineaura、`body_of_fire`、
  `reflective_skin`、`essence_of_the_dead`，覆盖 wolf/forest troll/brown
  bear/large brown snake/就地生成的 giant crystal rat/玩家共 6 个目标，
  含一条真实 `T_STONE_SKIN` 天赋路径）与 48/64/96 截图见
  `evidence/aura-tokens-20260928/README.md`。

> 关于 0.4.1 – 0.6.7：本文件此前停在 0.4.0，中间各版（棋子接入扩充、地形、楼梯、运动与朝向、状态层重影修复、建角 HUD、PNG Stored 打包修复、简繁汉化等）只记录在 `PROGRESS.md` 与 `evidence/runtime-v04x…v067/`。
> 本轮**不做补记**：逐版重写需要把每个历史提交重新核对一遍，否则写出来的是凭 PROGRESS.md 转述的二手条目，会把未复核的内容伪装成变更记录。
> 需要这一段历史时请查 `PROGRESS.md` 的交付章节与 `git log`，两者均已逐版留档。

## 0.6.11 — 2026-09-28

- **森林精修地形原生重铺后自愈。** Trollmire 精修地形被原生 `NicerTiles` 重铺（挖掘、
  土系天赋、Jumpgate、`on_block_change`、整图重铺）替换 Grid 后此前会永久退回原生贴图；
  现在每条重铺路径都会在同一批次内自动补画，不改地形规则。
- **删除 1611 个不可达死资产（48.8 MB）。** 按死资产审计逐路径核对后移除，保留全部仍被
  引用的贴图；纯 Lua 回归与目录/字节复核均通过。
- **新增玩家正式棋子（13/14 身体族入库，默认开启）。** 按本体 14 个身体族出图、
  中性无装备造型；`halfling_female` 两次生图无产物，保持原生，留待后续补齐。
  新增 Game Options 开关「Player token」（`checker_player_tokens_enabled`，默认开），
  与怪物棋子共用同一棋盘直径与青色玩家环。实机验证覆盖四组独立建角
  （Human/Cornac、Elf/Shalore、Halfling/Halfling 原生对照、Undead/Skeleton）、
  48/64/96 三档地格、开关切换、外部替换显示（原生变身）让位与回收、换装后原生纸娃娃
  重建，见 `evidence/player-tokens-20260928/`。

## 0.6.10 — 2026-09-27

- **`skeleton warrior` 接入，映射 45 → 46。** 它在 C0b 就通过了准入门控，但那一批的
  美术两次都圆盘越界（最大不透明半径 1.105 / 1.017，上限 0.867）、配额用尽被剔除。
  本轮开了**专门的 refinement brief**（`art/monsters-v9-refine/BRIEF.md`）换动作方向：
  双手巨剑从「斜举横过身前」改为**贴身竖持、剑尖朝下、沿身体中轴**。俯视三分之四
  相机下沿竖轴的物体被最大前缩，剑不再向外伸，首轮实测最大半径 **0.8559**。
  这是改构图而不是改判据，也没有靠缩小主体硬塞。
- **`giant brown mouse` 换贴图。** C0b 的 v1 是四足横身，与同色的 `giant brown rat`
  在 48px 灰度下落进同一类剪影；C0b 的返修调用又返回了 RGB 假透明被拒。本轮把姿态
  要求改为白鼷/灰鼷已验证有效的**竖立端坐、双前爪抬到吻边、圆耳高举**，首轮通过。
  身份与 `image`/`type`/`subtype` 映射合同不变，只换像素；C0b 的 v1 母版与导出件原样保留。
- 全批实际消耗 **2 次** ImageGen 调用（上限 4），两款都在 attempt 1 通过，未动用返修配额。
  两款均以 `allow_grandfather=False` 通过风格门控（底盘偏移 +2.00 / +5.32，扇区上偏
  +4.37 / +2.75）。没有把任何身份加进 GRANDFATHERED 名单，没有改判据、冻结基线或
  `export_token.c` 的 `target_occupancy`；其余 44 款贴图与母版一字未动。
- **`templates/repair.txt` 补上透明通道要求。** 它此前只在「保持不变」一句里顺带提了
  native RGBA transparency，没有像 `creature.txt` 那样显式禁止假透明；C0b 的棕鼷返修图
  就因此返回棋盘格背景的 RGB 图被拒、白烧一次配额。现已补齐同等强度的措辞。
- **`art_tasks.py` 新增 `refinement` 声明。** 规范一直写着「现有棋子的重绘需专门的
  refinement brief」，但工具只会对已接入身份报 `already mapped`，没有可走的路。现在
  重复检测仍是默认行为，只有写出 `supersedes` / `previous_batch` /
  `design_change_reason`（≥80 字符）/ 钉住的 `evidence` 才放行这一道，
  `max_attempts` 与按目录计数的调用预算都不变。
- 实机：0.6.10 TEAA 冷启动安装，Kor'Pul DEFAULT 摆位 7 枚（2 新美术 + 5 同族锚点），
  48/64/96 三档各一张 1920×1080 原图加一张原生对照；切换开关与地格尺寸未改变任何
  规则状态。证据见 `evidence/runtime-v0610/`。

## 0.6.9 — 2026-09-27

- **新增 8 款共享小怪棋子，映射总数 37 → 45。** giant white / brown / grey mouse、giant rabbit、giant crystal rat、brown mold、green mold、shining mold。均按精确身份接入（name/type/subtype 与原生逐字对应，`define_as`/`unique` 为空），不做 subtype 全族替换。
- 生图前先做准入门控：在隔离夹具里用原生 `finishEntity` 解析九个脱离地图的副本，逐项确认 `add_mos`/`add_displays`/`shader`/`anim`/`textures`/`shader_auras`/`replace_display`/`moddable_tile` 全空，因此都是可复用的 single-image 合同。`giant crystal rat` 与 `shining mold` 虽然名字暗示特效，实测**没有** shader，合格。证据见 `evidence/c0b-art-gate/`。
- **`skeleton warrior` 通过了准入门控但没有接入。** 两次生成的双手巨剑都伸出圆盘（最大不透明半径 1.105 / 1.017，判据上限 0.867），两次即该身份全部配额，按规范停下并交回设计。该身份继续保留原生贴图。
- 全批实际消耗 **11 次** ImageGen 调用（上限 18）。八款入库件在 `tools/check_token_style.py` 下**不吃 GRANDFATHERED 豁免**而通过；既有 37 款的判据、冻结基线与豁免名单均未改动，`export_token.c` 的 `target_occupancy` 未改。
- 同族可分性按 48/64/96px 真实 C 导出逐对看图（含灰度对照表，见 `art/monsters-v8-c0b/exports/compare-*.png`）：三对 mouse/rat、rabbit/rat、crystal rat/white rat、四款 mold 之间均在两维以上可分。`giant brown mouse` 是最弱的一对（未拿到设计想要的竖立姿态），其返修调用返回了画着棋盘格的 RGB 假透明图而被门控拒收，保留首轮并记为待办。
- 实机：0.6.9 TEAA 冷启动安装，Kor'Pul DEFAULT 摆位 12 枚（8 新 + 4 同族锚点），48/64/96 三档各一张 1920×1080 原图加一张原生对照；切换开关与地格尺寸未改变任何规则状态。本批无潜行导致未渲染的款（夹具解析出的 mouse 为 1 级，尚未获得 `T_STEALTH`；游戏中 2 级以上会获得，届时不渲染属正确行为）。证据见 `evidence/runtime-v069/`。

## 0.6.8 — 2026-09-27

- **棋子直径统一为 0.82 整格。** 取消 `CheckerTokenStyle.M.scale` 按 `size_category` 的三档（.86/.94/1.0）与固定 .95 内缩；同一块 64px 棋盘上原本出现 70.2% / 76.7% / 81.6% 三种圆盘（44.9 / 49.1 / 52.2px，落差 7.3px），现在全部为 82.00%。
- 抽出具名常量 `M.art_occupancy=.86`（必须等于 `tools/export_token.c` 的 `target_occupancy`）与 `M.token_diameter=.82`；`M.scale` 返回 `token_diameter/art_occupancy`，与 `size_category`、地格尺寸无关，参数签名保留以免改动调用点。
- 一并取消 48px 的 `if tile<64 then scale=1 end` 合并分支，三档地格行为一致。格内预算未变：阵营环 90.50%、护盾外环 99.50%，仍在一格之内。
- 夹具演示玩家棋子原有的 `.95` 特例并入统一直径，不再与同屏怪物差一档。
- `tools/export_token.c` 的 `target_occupancy` 保持 0.86：屏幕占比 = occupancy × scale，提高它不会让棋子变大，只会改变母版留白。留道宽度本轮亦未改动。
- 实机覆盖 48/64/96 三档地格、带盾与不带盾两种情况，37 款棋子（size_category 1/2/3/4 齐全）实测统一；证据与对照图见 [evidence/token-scale-20260927](evidence/token-scale-20260927/README.md)。
- 未处理并已记入待办：stone-troll 单图越界返修；Prox / Bill 两格高度（用户决定维持现状）。本轮未生成任何新美术。

## 0.4.0 — 2026-09-26

- 将 17 款 ImageGen 棋子接入隔离 Trollmire 样板；只复制已验证的 128px 导出，按精确身份和原生显示签名替换。
- 去掉 subtype 全族替换；未覆盖对象、外部变身与未知混合显示保留原生。显示所有权按 Entity 指针校验，控制召唤物不会切成人类图。
- 阵营圈由实时关系独立绘制；保留生命条语义和原生粒子／Boss 等级标记。
- 实机完成 17 实体映射、恢复和规则状态断言，采集原生对照、分组、密集、48/64/96px 与原生伤害／效果截图。证据冻结于 evidence/runtime-v040，后续接受独立评审。

## Monster art batch 2 — 2026-09-26

- 按用户决定继续 AI 直出，三名子代理新增 12 款：石巨魔、洞穴巨魔、Prox、Bill、巨狼、狐狸、黑熊、巨型棕鼠、眼镜王蛇、蜂群、巨鳗、龙龟。
- 新增精确身份目录、原图路径和源码依据，保留亚种／独特角色区别。
- 使用 ImageGen 定向修复三名持械巨魔的武器越盘、眼镜蛇盘内姿态及棕鼠尾根连接；保存弃选与选定版本。
- 导出工具支持批次选择，第二批产出 60 个尺寸候选；总计 17 个选定原图、85 个尺寸导出。
- 增加分组、小尺寸、灰度与十七款总览页面，以及带 provenance 的独立素材包工具。运行时游戏代码未改，验证范围见 art/monsters-v2/REVIEW.md。
- 两批审阅页均加载真实小尺寸导出；截图工具等待全部图片与字体解码，避免生成缺图的总览。

## Monster art batch 1 — 2026-09-26

- 建立插件独立 Git 库，保留 0.3.3 森林棋盘基线。
- 制定怪物轮廓、视角、材质、中性底盘、独立动态标记和精确实体映射规范。
- 子代理使用内置 ImageGen 生成森林巨魔、狼、棕熊、棕蛇、捕蝇草；保留源图与全部提示词／返修记录。
- 整理 835 张 NPC 源图索引与 56 个巨魔沼泽相关具名定义；明确文件数不等于物种数。
- 导出五档尺寸并验证 alpha、边界和哈希；创建可切换背景／圈色／灰度的本地审阅页。
- 用户决定继续 AI 直出，暂不执行 Blender 对照。游戏 0.3.3 运行逻辑未改变；见 art/monsters-v1/REVIEW.md 的验证边界。
