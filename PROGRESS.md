# 当前进度与续接入口

更新时间：2026-09-29。接续开发先读本文；已验证交付、历史结果与未完成范围分别记录。

## 当前交付：0.6.29 —— 怪物 Batch O–S、召唤物／同体形与地形 TW4–TW6／S2／S4／S5／S6／S8／S9 发布（2026-09-29；按本任务要求不提交）

- 纳入已提交的怪物 Batch O–S（棋子目录 191→**251** 款）、召唤物与同体形沿用棋子（Rak'shor／卡·普尔之怒乌鲁洛克之焰形态）及地形 TW4（夏特尔、零点圣域）、TW5（晨曦之门）、TW6（伊尔克；11 座城镇全部覆盖）、S5（阴影地宫、泰恩之塔、伊塞尔森·月之谷、鲜血之环、德斯竞技场）、S6（艾露安、加伯特部落）、S9（巅峰 L1–L11）、S2、S4、S8。主插件版本、棋子清单版本、README、CHANGELOG、外测安装指南（新建 `docs/external-test-v0629/`）与 `tools/package_external_test.py` 同步至 0.6.29；设置里“棋盘地形”说明（`hooks/load.lua`、`zh_hans.lua`、`zh_hant.lua` 三处键逐字节一致，2,480 字符）新增四座城镇与七个区域，名称取自翻译项目 `mod-tome.lua`。
- 正式 TEAA 安装至隔离离线夹具，shader 开启、1920×1080、64px，9 个场景各自独立冷启动（含中文界面两场）：晨曦之门、伊尔克（zh_hans，设置说明译文实测含新名称）、Kor'Pul 暗砖墙、巅峰 L2、艾露安 L1、召唤物（trollmire）、晨曦之门太阳骑士、Rak'shor（乌鲁洛克之焰）、中文野性召唤米诺陶。**0** 个 Lua 错误，进程均已停止。证据见 [runtime-v0629](evidence/runtime-v0629/README.md)。
- 纯 Lua **13** 个独立脚本通过；生产测试 **257** 项、死资产审计和 `git diff --check`（排除 `evidence/`、`handoffs`）通过。TEAA **1,882** 个成员逐字节匹配源码，**1,856** 张 PNG 全为 ZIP_STORED。TEAA SHA256 `2392a1d0dd377672b27f72fe876dfdf552033046e42c83393137d602b083a063`；外测 ZIP SHA256 `158523df016a0b8e2ba3c9476e1ca5f957cd6d8f54dc96523d17f33bda58fdcd`；HUD 0.2.7 TEAA 沿用未重建。
- 已知限制：晨曦之门棕榈树、巅峰圣所硬墙大块与远传门平台、旧存档中的城镇／区域保持原生；其余沿 0.6.28。本轮为归档安装和暂停夹具场景，未验证完整战役跨进程读档、自然连续战斗或其他游戏版本。

## 追加（2026-09-29，未提交，未升版）：召唤物与同体形沿用棋子

- 用户决定：召唤物／仆从穿其复制对象的棋子；同一副身体在别处同样穿；拉克·肖与卡·普尔之怒开启乌鲁洛克之焰形态。`CheckerTokens.lua` 新增按条目的 `variants`（陵墓召唤食尸鬼、腐肉虫群、`Grand Arrival` 火龙幼仔、晨曦之门人类太阳骑士，均按其构造的独有字段钉扎）与 `wild_summon_ids`（米诺陶、黑果冻怪、火龙的“野性召唤”后缀），`urh_rok_form` 增至四项。反例与逐项来源见 [token-summons-20260929](evidence/token-summons-20260929/README.md)；隔离夹具五场景 0 个 Lua 错误。`paladin-vs-vampire` 保险库里的无 define_as 太阳骑士按其自身字段第二组钉扎；“野性召唤”改名按 `tformat(_t())` 精确重算（含中文客户端，已实机验证）。

## 当前交付：0.6.28 —— 怪物 Batch J–N 与地形 S3／S1／TW1–TW3 发布（2026-09-29；按本任务要求不提交）

- 纳入已提交的怪物 Batch J（11 款，含 Grand Corruptor 与精灵教徒 Urh'Rok 形态）、K（12 款）、L（12 款）、M（13 款，含 elven cultist）、N（12 款）；棋子目录 131→**191** 款。地形：S3（Old Forest 晶簇、森林区石质密室、LAKE_NUR）、S1（事件光环环）、TW1（Derth、Lumberjack、记忆格安装）、TW2（Last Hope、Elvala）、TW3（Zigur、Angolwen、Iron Council；原生层标志修复）。主插件版本、棋子清单版本、README、CHANGELOG、外测安装指南（新建 `docs/external-test-v0628/`）与 `tools/package_external_test.py` 同步至 0.6.28；设置里的“棋盘地形”说明（`hooks/load.lua`、`zh_hans.lua`、`zh_hant.lua` 三处键结构一致）新增七座城镇。
- 正式 TEAA 安装至隔离离线夹具，shader 开启、1920×1080、64px，八场景各自独立冷启动：mark-spellblaze L2（Grand Corruptor，含一次棋子开关往返）、charred-scar L1（Fyrk 带光环）、dreadfell L1（vampire）、Old Forest CRYSTALINE L2（晶簇 303 格，Native 往返恢复一致）、Rak'shor L1（光环环 56／56、阻挡 13／13，往返恢复）、Derth／Last Hope／Iron Council（强制普查 2,500／2,500，原生 0；Derth 含往返）。**0** 个 Lua 错误，进程均已停止。证据见 [runtime-v0628](evidence/runtime-v0628/README.md)。
- 纯 Lua **13** 个独立脚本通过；生产测试 **182** 项、死资产审计（dead assets: none）和 `git diff --check`（排除 `evidence/`、`handoffs`）通过。TEAA **1,533** 个成员逐字节匹配源码，**1,510** 张 PNG 全为 ZIP_STORED；外测 ZIP 白名单、byte-identity 与 SHA256SUMS 通过。TEAA SHA256 `c02672091ecd52995f06deb9fee1de1a9356ebc1ec43e4f1174a550b7b0c8531`；外测 ZIP SHA256 `0db8959f4a57738184eb58f36503e7c8b1d9bcc8a8fa5068111c12712b683277`；HUD 0.2.7 TEAA 沿用未重建。
- 已知限制：dark orc 系 48px 偏暗、forest wight 偏暗；Lumberjack／Zigur／Angolwen 商店墙为亮砖（V2）、城镇棋盘道路偏棕；农田与 Angolwen 传送门保持原生；旧存档中的城镇保持原生；夹具天气方块疑为软件 GL 显示瑕疵，原生天气未改；其余沿 0.6.27。本轮为归档安装和暂停夹具场景，未验证完整战役跨进程读档、自然连续战斗或其他游戏版本。

地形套件 S9（High Peak L1–11；0 新图、0 ImageGen、未提交、未升版、未打包；2026-09-29）：`Grid.lua` 名单加 `high-peak/grids.lua`（`tw4.S5_FILES` 区戳，每个 S9 格都需此戳，旧档保持原生）；L1–4 Cavern 经 `tw4.hpCave`＝区戳＋既有洞穴合同，L5–10 Roomer 与 L11 圣所为 `HIGH_PEAK` 石质变体（`combined`），可挖墙／门框入 `tw4.S8_DARK` 暗砖；`HIGH_PEAK_UP`／`CAVE_HIGH_PEAK_UP` 为 S2 精确规格（按原生上行图画棋盘上梯，`tw4.s2Stone` 可返回 `stairs-up`）。夹具直达全部 11 层：强制普查原生 3750→2–4（L1–8、L10，事件格与 `PORTAL_BOSS`）、L9 3750→34（greater vault 伤害熔岩 31）、L11 1150→31（远传门 27、`ORB_*` 4）；L2／L7／L11 往返逐像素一致、规则摘要一致；Derth 帧 SHA 相同，Dreadfell／Telmur 普查不变（重新生成布局）；0 `Lua Error`。远传门、虚空门、法球门、`PORTAL_BOSS`、事件格与伤害熔岩保持原生；`HARDCAVEWALL` 仅见于 sub-vault 独立区，未处理。弱点：圣所 HARDWALL 大块全黑、远传门平台仍为原生大理石。地形合同 12,887→13,125 项。见 `evidence/terrain-s9-20260929/README.md`。

地形套件 S8（V2／V7 暗墙；0 ImageGen、未提交、未升版、未打包；2026-09-29）：实测每个画可挖 `WALL` 的层卡·普尔亮砖都比旁边地面亮或只差 ≤5%（含 Kor'Pul 本身与 Dreadfell），恶魔空间岩墙比熔岩地亮 51%。`art/terrain-korpul-dark-s8/export.py` 只把墙体材质母版按通道压暗（0.58／0.60／0.66），用未改的 `tools/export_korpul_terrain.c` 重新拼装 160 张 `korpul-dark/`（墙＋四种门，门只改门框矩形；先验证拼装器逐字节复现原 196 张）；恶魔空间另导 32 张 `scorch-dark/` 玄武岩。两套独立 manifest 门控；`CheckerTerrain.lua` `tw4.S8_DARK` 列 27 个石组区（HARDWALL、Conclave、只有硬墙的城镇、Charred Scar 不变），纯显示。64px lit 地／墙差：before −34.7%～+5.0%，after +21.9%～+42.9%（Lumberjack 草／墙 +22.8%，恶魔空间 +38.2%）；5 层 Refined→Native→Refined 逐像素恢复、规则摘要一致；Derth／Last Hope／Zigur／Point Zero／Charred Scar／Ring of Blood L3 跨进程帧 SHA 相同。可挖暗墙现略暗于 HARDWALL，靠纹理区分。见 `evidence/terrain-s8-20260929/README.md`。

地形套件 S6（Erúan L1–3＋Gorbat Pride L1–3；新棕榈 1 张、ImageGen 1／6 次、未提交、未升版、未打包；2026-09-29）：`Grid.lua` 名单加两区 `grids.lua`（`_checker_zone_source`，每个 S6 身份都要此戳，旧档保持原生），sand.lua 定义另记 `_checker_sand_source`；`tw4.S5_FILES`／`S5_FOREST` 加两区，`tw4.s6Kind`（`ringAware`）：沙→海滩沙、`DEEP_OCEAN_WATER`／`DEEP_WATER`→深水掩码、硬山与 `MOUNTAIN_WALL`→Daikara 山体掩码均沿用既有合同；新精确身份 `PALMTREE1-20`（全规则字段＋只许原生 makeTrees 部件与末尾沙边载体）→新棋盘棕榈（`art/terrain-palm-s6/export.py`，海滩沙上正反两款＋三个沙出口，10 张）、Erúan 三个沙出口、Gorbat 自己的 `FENCE_*` 竹巢（subtype roost／dig／grow／`is_roost_entrance` 逐项，层与 Irkkk 同名变体逐项相同，另加 `BHW_SOLO1`）→TW6 竹屋图、无杠杆 `ROCK_DOOR`→棋盘沙＋原生巨石层；`M.variant` 加 `GORBAT_PRIDE`／`ERUAN`（门厅与宝库 basic.lua 石质，均 `combined`，`classify` 另要求本区戳）。前后（HEAD `bb028335` TEAA 对照，之后＝HEAD＋S6 文件 TEAA）：自然原生 Erúan 1,050→0／1／9（L3 远传门 9、L2 事件沙格 1），Gorbat 2,000→5（走查后；杠杆石门、2 杠杆、事件格）；棕榈 289／285／233 全部棋盘化、规则仍挡移动与视线；Charred Scar／Derth／Irkkk 回归不变。Erúan L1、L3 湖岸与 Gorbat L1、L2 Refined→Native→Refined 逐像素一致、规则摘要一致，0 `Lua Error`；lit-pixels 沙／棕榈 26–37%、沙／竹巢墙 53–60%。远传门、杠杆与杠杆石门、事件格保持原生；Gates of Morning 9 棵同身份棕榈可原样套用，按用户未决定未应用。弱点：棕榈沙丘底座偏亮、每格一棵较规整。地形合同 12,149→12,846 项。见 `evidence/terrain-s6-20260929/README.md`。

地形套件 S4（T1 水下空气泡＋T16 带回调祭坛；T2 未做；0 ImageGen、未提交、未升版、未打包；2026-09-29）：`WATER_FLOOR_BUBBLE` 以 `tw4.S2_SPEC` 的 `water.lua` 条目（族键 `underwater`）精确判定：全规则字段签名＋`on_stand` 必须为 `water.lua:106`，另要求无 `air_condition`、`nb_charges` 为数值、无额外层；显示为棋盘水下地板＋从原生气泡格提取的气泡层（`art/terrain-underwater-bubble-s4/export.py`，导出 `refined/underwater/bubble{0,1}`）。原生消耗换格不触发重绘（基线实测换出原生地板），新增 `superload/engine/Zone.lua`：仅当地形确实变化且旧／新格为精确气泡时于原生调用后重绘 3×3（也覆盖 aquatic horror 死亡生成气泡）。T16：Spellblaze L2 `ALTAR_CORRUPT`（`on_move:28`）与 Caldera L2 `ALTAR`（`block_move:35`）为 S2 规格，棋盘地板＋原生五芒星／宝珠层。`terrain_contract.lua` 原“气泡锁原生”改为精确正例＋逐字段反例（合同 12,149 项）。实测：Nur L2 DEFAULT／FLOODED、FLOODED L3、Murgol L2 气泡 73／64／122／59 格全部接管，原生格 64→0、59→0、110→1（Sher'Tul 入口）、62→0；原生 on_stand 逐次耗尽后该格为棋盘地板；Spellblaze 4→1、Caldera 2→1（余为 S1 熔岩中心）；Nur L2、Murgol L2、Caldera L2 往返逐像素一致、规则摘要不变；Derth／Kryl-Feijan L5 回归不变；0 `Lua Error`。T2 `WORMHOLE` 保持原生：粒子挂在格实体 `_mo` 显示回调上，替换显示后需粒子桥接＋实测（约半个套件）。见 `evidence/terrain-s4-20260929/README.md`。

地形套件 S2（已覆盖区域内的出口／无回调门／静态道具：T4、T6、T7、T8、T10、T14、T15、T21、T24，T9 已于 S3 完成并复核；0 ImageGen、未提交、未升版、未打包；2026-09-29）：新 `_checker_s2_source` 戳仅由 `tw4.S2_SPEC` 逐条审定的 id 打上（全规则字段＋函数行号＋传说模式＋`door_player_check`），`FLAT_*`／`DOOR_VAULT*`／`BONE_VAULT_DOOR*` 为新精确身份，T21 边缘地板扩到 Dreadfell／Vor／Scintillating／Reknor／Halfling；洞穴门由 korpul 门图重着色导出 8 张。出口目标、通行、视线与回调不变；旧档保持原生。实测所有 S2 id 捕获，0 `Lua Error`，四层往返逐像素一致。杠杆、事件格、PORTAL、Vor 深水（T20）与伤害熔岩（T19）保持原生（需新图）。地形合同现为 11,981 项。见 `evidence/terrain-s2-20260929/README.md`。

地形套件 S5（六个零新图区域：Dreadfell 伏击、Shadow Crypt L1–3、Tannen's Tower L1–4、Valley of the Moon、Ring of Blood L1–3、Derth 东南竞技场；0 新图、未提交、未升版、未打包；2026-09-29）：`Grid.lua` 名单加 tannen-tower／valley-moon／ring-of-blood 的 `grids.lua`（`_checker_zone_source`，区域局部身份需此戳，旧档保持原生）；`M.variant` 加 SHADOW_CRYPT／TANNEN_TOWER／RING_OF_BLOOD／ARENA_UNLOCK，后三者 `combined`，`installRemembered` 扩到这四区的 all_remembered 层；森林侧每区为自己的 batch4 家族（`tw4.s5Kind`，ringAware），全部复用既有精确合同：草／花／树／世界出口／深水／毒深水（Caldera 毒水掩码）／MOUNTAIN_WALL（Caldera 墙掩码）／SAND（海滩沙）；新精确身份：Valley 月石 MOONSTONE1-8 与 Fearscape 传送门 PORTAL_DEMON（棋盘草＋原样叠原生层）、Ring of Blood 熔岩坑 LAVA_WALL／_OPAQUE（burnt 熔岩掩码）、Tannen TUP/TDOWN（视图还原 UP/DOWN 后走 basic 楼梯原合同）与水层地板／楼梯的原生 marble→water 边缘载体（仅 Tannen）。`Game.lua` 仅显示：ambush 任务直接放置的世界出口在任务记录结果后对该层修复一次。FOREST_ZONES 未加区。实测（HEAD `ee705b8` TEAA 对照，之前全原生）：forced 剩余原生——ambush 0／198、crypt L1–2 0、crypt L3 2（事件格）、tannen L1 8（杠杆＋杠杆门）、L2–L3 0、L4 212（open sky 无图）、valley 1（quickEntity 通道）、blood L1–2 0、L3 1（控制球）、arena 2（无杠杆闸门）；Derth／Old Forest／Dreadfell 回归仅随机事件差异。2 次冷启动 0 `Lua Error`，13 层规则摘要全程一致，Refined→Native→Refined 在 Tannen／Valley／Ring of Blood／arena 逐像素一致（crypt L3 仅 spellblaze 熔岩 shader 格差）。弱点：Valley 大片毒湖像密植、crypt／blood L1–2 可挖 WALL 亮砖（V2）、arena 沙与硬墙同明度。地形合同 6,288→7,171 项、地形修复 53→66 项。设置说明文字未改。见 `evidence/terrain-s5-20260929/README.md`。

地形套件 TW6（Irkkk；新竹屋族、未提交、未升版、未打包；2026-09-29）：最后一座城镇，11 城全部门控。沿用 TW1–TW5 城镇机制，`Grid.lua` 名单加本城 `grids.lua`；与 Shatur 一样只走森林侧（无石质、无 `variant`）。丛林草／树／世界出口在本城戳下复用 `jungleKind` 全合同画 Caldera 图，湖走既有 `deepWater`；新精确身份 `hut-wall`／`hut-floor`／`hut-cooking`（灶坑原样 `add_mos` 叠层）／`hut-door-{h,v}[-open]`，每个 BHW_*／门变体只许其定义行加的原生层。商店是站在竹屋地板上的 actor（非陷阱），不读不写。`Grid.lua` 加仅显示的开门修复（原生开门换格不走 NicerTiles）。新图：ImageGen **4／14** 次（茅草墙顶、竹篱墙段、编席地板、棕叶门扇各一张，首轮全部入选，无豁免），`art/terrain-bamboo-hut-v1/export.py` 导出 42 张（墙 32＋地 2＋门 8；墙内 52.0 对丛林草 96.5／竹屋地 123.4，最亮墙低于最暗地板 40.9%，最小奇偶差 12.8%）。前后（自然态，HEAD `bc130ff` TEAA 对照）：原生 2,500→0；十座已提交城镇计数不变。Refined→Native→Refined 三视图逐像素一致，同进程规则摘要一致，开门后即时画开门图，lit-pixels 草／墙 40.8–46.5%，0 `Lua Error`。弱点：茅草顶 48px 偏碎、门叶小。设置说明文字未改。见 `evidence/terrain-tw6-20260929/README.md`。

地形套件 TW5（Gates of Morning；新金山墙族、未提交、未升版、未打包；2026-09-29）：沿用 TW1–TW4 城镇机制，`Grid.lua` 名单加本城 `grids.lua`，`variant`＝`TOWN_GATES_OF_MORNING`＋`combined`；新精确身份 `gold-mountain`（GOLDEN_MOUNTAIN／_WALL1-6 全规则字段＋本城戳＋只许原生 `gold_mountain` 边界层），沙滩准入从 Zigur 扩到本城，路／草／树／水／出口走既有合同。新图：ImageGen **5／12** 次（3 次 A8.1 右边距不足未入库、原图留存；v4 块体母版＋crest 俯视母版入选，无豁免），`art/terrain-gold-mountain-v1/export.py` 导出 32 张掩码（室内 63.9 对石地 131.8／草 109.0／沙 109.2，最小奇偶差 13.1%）。前后（自然态，HEAD TEAA 对照）：原生 2,500→9（棕榈，需新图）；FENS／远传门运行时保持原生；九座已提交城镇计数不变。Refined→Native→Refined 三视图逐像素一致（沙滩视图差异全在原生棕榈 shader），同进程规则摘要一致，lit-pixels 地面／金山 53.6%／52.0%，0 `Lua Error`。设置说明文字未改。见 `evidence/terrain-tw5-20260929/README.md`。

地形套件 TW4（Shatur＋Point Zero；0 新图、未提交、未升版、未打包；2026-09-29）：沿用 TW1–TW3 城镇机制，`Grid.lua` 名单加两城 `grids.lua`；新精确身份（均需本城名单戳）：Shatur 绿／雪精灵树（雪树画 Norgos 雪族 pine/elm）、雪草与 3 个雪地商店的 ROCKY_GROUND（雪地）、湖桥 COBBLESTONE（棋盘路）、苔藓雕像（`townStatue` 按城参数化，`shatur.lua:28`）；Point Zero GRASS_SHORT、COLD_FOREST（雪族 pine）、void.lua 外太空／浮岩／裂缝／虚空地板（`voidTerrain` 仅对本城放开，浮岩紫边只朝外太空），HARDWALL 走石质 `TOWN_POINT_ZERO`＋记忆安装，并在本城改画既有 Conclave 暗砖（Kor'Pul 暗墙与灰浮岩在紫调下 64px 近乎同亮，换后墙 30.5 对岩 49.7）。前后（自然态，0.6.28 TEAA 对照）：Shatur 原生 2,500→0、Point Zero 2,500→15（14 个运行时光束端点＋RIFT 出口，均保持原生）；0.6.28 七城回归计数不变；15 个商店门在陷阱层不读不写。Refined→Native→Refined 逐像素一致（Point Zero 比较时暂停光束粒子），规则摘要全程一致，0 `Lua Error`。弱点：雪林阻挡只靠小树标、Point Zero 整体偏平偏灰、端点圆边原生块突兀；设置说明文字未改。见 `evidence/terrain-tw4-20260929/README.md`。

地形套件 TW3（Zigur＋Angolwen＋Iron Council；0 新图、未提交、未升版、未打包；2026-09-29）：沿用 TW1/TW2 城镇机制，`Grid.lua` 名单加三城 `grids.lua`（Angolwen 外层戳覆盖嵌套 `mountain.lua`，TMX 的 id 经区域名单实例化），`variant`＝`TOWN_ZIGUR`／`TOWN_ANGOLWEN`／`TOWN_IRON_COUNCIL`＋`combined`。新增精确身份（均需本城名单戳）：Zigur `LAVA`（burnt 熔岩掩码）、`SAND`（仅 Zigur，South Beach 沙）、`POST`（`on_move` 锁 `town-zigur/grids.lua:33`，棋盘草＋原样路牌）、`ROCK`（石质 prop：棋盘地砖＋原样巨石）；Angolwen `FOUNTAIN`（`block_move` 锁第 47 行，棋盘深水）、`FOUNTAIN_MAIN`（原样 6×5 喷泉叠层）、`ROCK`（棋盘草＋`maze_rock`），山墙走 TW2 `hardMountain`；Iron Council `CRYSTAL_WALL`（crystal 墙掩码）、`STATUE1-6`（石质 prop）、`ESCAPE_REKNOR`／`DEEP_BELLOW`（Kor'Pul 下行楼梯；DEEP_BELLOW 的无图 glow 层城内不可见，不重建）；Zigur／Angolwen 带草边载体的世界出口。TW2 雕像叠层推广为 `M.townProp`。**修既有缺陷**：石质原生快照丢失嵌套层的 Grid 类默认 `display_on_*`，切回 Native 后墙顶盖／雕像／巨石消失，`layerFlags` 修复后与 HEAD 原生帧一致。前后（自然态，HEAD `7610575` 以 TEAA 实跑）：Zigur 原生 2,500→58（耕地）、Angolwen 2,500→49（走遍后；耕地 48＋TMX 返回出口 1）、Iron Council 2,500→0；Derth／Last Hope／Elvala 仍 0，Lumberjack 石质按视野，四城强制普查 0。24 个商店门在陷阱层不读不写。2 次冷启动 0 `Lua Error`，同进程规则摘要全程一致，Refined→Native→Refined 与记忆安装开关逐像素一致。保持原生：耕地 106 格（需 4 张作物图）、Angolwen `portal back`、Zigur 任务 COBBLESTONE；TW3 前生成的层。V2 在 Zigur／Angolwen 浅色砖墙可见（未修）。见 `evidence/terrain-tw3-20260929/README.md`。

地形套件 TW2（Last Hope＋Elvala；0 新图、未提交、未升版、未打包；2026-09-29）：沿用 TW1 城镇机制（`townFiles`／`townStamped`／`townKind`／`installRemembered`），`Grid.lua` 名单加两城 `grids.lua`（Last Hope 的外层戳同时覆盖嵌套 `mountain.lua`），`variant`＝`TOWN_LAST_HOPE`／`TOWN_ELVALA`＋`combined`。新增 3 个精确身份：`plazaRoad`（区域本地 FLOOR_ROAD_STONE 全字段，只许原生 `road_oldstone`／`marble_water` 层，画森林族路）；`hardMountain`（HARDMOUNTAIN_WALL／1-6，不可挖、无 pass_wall、block_sense／esp，图号与 id 对应，原生 mountain editer 层，画 Daikara `mountain-wall` 掩码）；`townStatue`（地图 `quickEntity` 雕像：`block_move` 须定义在 `@/data/maps/towns/last-hope.lua` 第 20–23 行且唯一叠层正是该行的雕像图，底面画棋盘草、原样重建 z=18／display_y=−1／display_h=2 雕像叠层）。旧档规则保持：新身份需城镇名单戳，雕像另需四邻有本城戳。16＋7 个商店／聊天门（含 Elder、Tannen、Rich merchant）在陷阱层，不读不写；`east-portal` 动态远东传送门保持原生。前后（自然态，HEAD 以 TEAA 实跑）：Last Hope 原生 2,500→0（森林 1,401＋石质 1,099，其中记忆未见 1,081 由安装接管）、Elvala 2,500→0（森林 1,772＋石质 728）；强制普查两城 0 原生；TW1 两城回归不变。2 次冷启动＋1 次回归探针 0 `Lua Error`，同进程规则摘要（含陷阱层）全程一致，Refined→Native→Refined 三个视图逐像素一致。观感：Last Hope 读作石城（暗硬墙城墙＋浅色地砖广场，与原生明暗相反），**无 V2**（两城只有 HARDWALL）；弱点是两类石路都成褐色土路格，岛内成片褐地、广场上路对比弱（97 对 115），假山环读作岩石花园；雕像完整。Elvala 读作水上石城＋方格草坪，没有精灵特征（原生同为花岗岩＋旧石板），草坪失去有机轮廓。可选新图（非必需）：石板路 2＋草上石径 2。地形合同 3,368→3,592 项；`audit_dead_assets.py` batch4 种类域加城镇族。见 [TW2 证据](evidence/terrain-tw2-20260929/README.md)。

地形套件 TW1（城镇记忆格安装＋Lumberjack 冒烟＋Derth；0 新图、未提交、未升版、未打包；2026-09-29）：**FOV 实测**：Derth（`all_remembered`）进城时 2,500 格全部 `remembers`、视野内仅 33 格，关掉新安装路径时 114 个石质格（105 墙＋9 商店墙）全部是“记忆未见”，0 记录、全部原生——证实调研推断。实现：`Grid.lua` 名单加两城 `grids.lua`，`markSource` 记 `_checker_town_source`；森林侧 `townKind`（batch4 家族，要求城镇名单戳＋已有 meadowGrass／meadowFlower／forestTree／stoneRoad／deepWater／meadowExit 全字段合同）；石质侧 `variant`＝`TOWN_DERTH`／`LUMBERJACK_VILLAGE`＋`combined`，`classify` 在城镇另要求名单戳；新增 `M.installRemembered`：仅门控城镇且 `level.data.all_remembered==true` 时，对 `map.remembers` 为真的格建记录并按静态四邻定墙掩码，未记忆格不读、非城镇区与 Lumberjack（非 all_remembered）不走此路径；`observe`／`render` 仅等价抽出 `record`／`recordFile`。商店是 `Map.TRAP` 层 `BASE_STORE`（z=18），陷阱层不读不写，门板＋招牌完整叠在棋盘墙上。前后（自然态，HEAD 以 TEAA 实跑）：Derth 原生 2,500→0（森林 2,386＋石质 114，记忆未见 114 全部棋盘），Lumberjack 原生 625→森林 526 接管、石质 99 格按视野（走遍后 99/99）；强制普查两城 0 原生。3 场冷启动 0 `Lua Error`，规则摘要（含陷阱层）全程一致，Refined→Native→Refined 两城恢复帧逐像素一致。观感：Derth 树集中在环湖外圈，城内棋盘草坪＋褐色路＋暗色 HARDWALL 石屋，读作桌游城镇；Derth 无 V2；路由原生灰石板变为褐色土路格；Lumberjack 可挖 `WALL` 用亮砖（墙 115.6 对草 96.5），V2 出现，留 S8。限制：TW1 前生成的城镇层无名单戳保持原生（Derth 为持久区）；设置说明未列城镇。地形合同 3,223→3,368 项。见 [TW1 证据](evidence/terrain-tw1-20260929/README.md)。

地形套件 S1（事件光环全族补齐 E1／E2／部分 E3；0 新图、未提交、未升版、未打包；2026-09-29）：新增精确光环来源判定——`on_stand` 必须定义在 `@/data/general/events/<事件>.lua` 且行号等于原生 `local on_stand` 行（外部 addon 同名文件、同路径改行号、其他回调均原生）；`markSource` 给定义记 `_checker_def`（名字、always_remember、小地图色、on_stand_safe、display／颜色／notice），光环格按“恰好撤销事件自身痕迹（on_stand、always_remember、safe 标记；地板另需事件对原名的精确改名与缺省小地图色；墙门名字不变）”得到视图，再交给该族原有全字段合同。接入 gloom、sand、crystal（含 Old Forest 晶簇）、cave、burnt、bone、Daikara 无害熔岩、森林沼水／带原生草边层的草地，石质墙／门／楼梯（E2 扩到全部石质区）；font-life／bligthed-soil／antimagic-bush 中心格（E3）画棋盘地板＋原生道具层；spellblaze-scar 熔岩中心保持原生。underwater／void／fortress 覆盖区无光环事件，未改。实测每层原生均值（前→后）：Rak'shor 56.1→2.2、Ardhungol 45.5→28.0（余为 WORMHOLE）、Blighted 26.8→9.2（余为召唤阵）、Dreadfell 18.7→3.8、Heart of Gloom 16.4／11.6→0.3／0、Reknor 14.9→5.9、Deep Bellow 11.3→0.3、Ritch 9.4→2.3、Spellblaze 6.5→4.0、Halfling 6.4→1.6、Scintillating TWISTED 5.0→0.6、Trollmire FLOODED 7.3→1.5；128 层次中光环格仅剩 15 格原生（熔岩中心、WORMHOLE、SUMMON_CIRCLE、1 个与 font-life 重叠的灌木中心）。4 场冷启动实机（Blighted 石质、Rak'shor 骨质、Ardhungol 洞穴、Heart of Gloom）光环格 150/150 接管、圈内阻挡格 48/48，规则摘要三态一致，0 `Lua Error`；Blighted／Rak'shor 恢复帧逐像素一致，Ardhungol／Heart of Gloom 仅原生 WORMHOLE／gloom 粒子动画差异。观感：圈内与圈外同族连成一片，墙掩码跨圈无缝，消除 Rak'shor 跳色（V5）；光环可见度主要靠原生 shader 粒子，“subtle”遮罩在 48px 几乎不可见。已知限制：语言切换后读旧档，改名按新语言不匹配的光环地板保持原生；旧存档缺定义戳时保持原生。地形合同 963→3,223 项（由原生事件文件实跑生成光环格）。见 [S1 证据](evidence/terrain-s1-20260929/README.md)。

地形套件 S3（Old Forest 晶簇＋森林区石质密室＋LAKE_NUR 出口；0 新图、未提交、未升版、未打包；2026-09-29）：E8——`Grid.lua` 仅在调用者源码精确为 `crystaline-forest` 事件的 `underground.lua` 加载上给 `crystal.lua` 定义加来源 `origin`，Old Forest 区域表导入另记 `old-forest-zone`（NicerTiles 重掷地板用）；`oldForestCrystal` 在原 `crystalTerrain` 全字段合同上再要求来源（墙仅事件来源），Old Forest CRYSTALINE 以“森林主族＋晶洞补位”组合绘制，晶墙掩码不与树连接。T23——old-forest、trollmire、daikara、tempest-peak、scintillating-caves 登记为石质混用区；`classify` 对 Old Forest／Trollmire `DungeonWallsGrass` 的原生草边 MO 精确忽略后判定（`unfringe`）。T9——`LAKE_NUR` 打戳并精确合同，翻转原锁原生测试。实测每层原生均值：Old Forest CRYSTALINE 319.5→6.4、DEFAULT 39.0→6.0，Trollmire DEFAULT 28.7→3.0、FLOODED 31.0→7.3，Scintillating TWISTED 18.8→5.0；剩余为光环（S1）、封印门／巨石（T4）、毒深水、护送门、墓碑、`invis` 边框石地等。5 场冷启动实机 0 `Lua Error`、规则摘要开关前后一致，Refined→Native→Refined 恢复帧与原帧逐像素相同。观感：晶簇边界可读（晶墙最暗，晶地冷灰对草地橄榄绿）；拍到的密室外墙均为 `HARDWALL`，比石地暗，符合棋盘语言，但 loot-vault 内隔墙等可挖 `WALL` 沿用 Kor'Pul 亮砖（比石地亮约 20%），V2 随之扩到这些区，需 S8 暗墙处理。地形合同 848→963 项。见 [S3 证据](evidence/terrain-s3-20260929/README.md)。

怪物 Batch S（勘察二后续名单，沿用批 R 的计分口径：human sun-paladin／人类太阳骑士、High Sun-Paladin Rodmour／高阶太阳骑士罗德莫、Aluin the Fallen／堕落骑士阿鲁因、Argoniel／艾格尼尔、Elandar／埃兰达、Mindworm／心灵蠕虫、Berethh／贝里斯、Companion Warrior／同伴战士、Companion Archer／同伴弓手、Greater Mummy Lord／巨型木乃伊领主、Kor's Fury／卡·普尔之怒、Borfast the Broken／扭曲的波法斯特 共 12 款；离线美术＋映射，未实机、未提交、未打包、未升版；2026-09-29）：选型见 `art/monster-batch-s/SELECTION.md`。重新计分后 12.0（纯保证／剧情加权）并列仍排在批 R 所记 11.3 组（naga tide huntress、ancient elven mummy、ritch flamespitter、chitinous ritch）之前，25 个候选按家族取日盟／Charred Scar 组、琥珀草甸／萨洛尔组与三个不死唯一体；余 13 个 12.0 候选（商队×3、据点×4、Lost Merchant、Nimisil、Slasul、Draebor、war dog、Yeek Wayist）与 11.3／10.9 组留待下批，**先做哪一组由用户定**。合同与哈希钉入 `evidence/monster-batch-s-20260929/source-contracts.json`：十个为 64×64 单图（同伴战士／弓手用显式 `image=`，其余默认名图），Argoniel 与 Elandar 是**非唯一**、显式 `nice_tile` 的 64×128 tall 体，条目带 `native_tall=true`；十二个 `define_as` 全部精确绑定。同名：Gates of Morning 城镇的 “human sun-paladin” 无 `define_as`，被绑定拒绝、保持原生（已钉负例，是否也戴棋子待用户定）；High Peak 最终首领 Argoniel／Elandar 同名同 `define_as` 同图同 tall 体，会与 Charred Scar 版本一起戴同一棋子。突变扫描：无出生写入 type/subtype/image/add_mos；**报告的命中**：Kor's Fury 的 Corruptor auto_class（39 级后）可能学到 Flame of Urh'Rok（demon/major，非出生突变，启动即回退原生贴图，未设 `urh_rok_form`，决定留给用户）；巨型木乃伊领主与 Kor's Fury 施放 Invisibility 时有临时 shader（期间原生）；Solipsist 的思维体只改召唤物。ImageGen 共 **18/28** 次：首轮 12；berethh v1 底盘 -8.19、v2 过补偿 +9.63、v3 入选（-4.78）；borfast v1 -10.61（暗棕铜色）、v2 改淡银灰绿后入选（-6.78）；aluin v1 暗锈褐团（亮度 59.1）、v2 64.0，v3 改浅银钢入选；companion-warrior v1 亮度 62.2、v2 改浅黄褐后入选（70.1）；单件均 ≤3 次，无豁免、无 PENDING 请求，底盘偏移 -6.78…+5.46，半径 0.858–0.860，遮罩体亮度 66.9–141.3。**48px 偏弱**：berethh（橄榄灰，66.9）、borfast（灰褐，83.3）、aluin-the-fallen（70.0，钢灰配红）在暗盘上对比低于同批其余款。同族区分：三位骑士＝金板＋日轮盾＋锤／象牙板＋紫披风＋拄剑／佝偻银钢＋拖斧红盾（对既有 elven warrior 的银板鸢盾斧）；术士＝前倾持火球／深红披风扇＋交叉双杖／盘腿悬浮（对既有 elven mage 的竖直杖）；草甸＝满弓灰绿斗篷／低弓步前刺／单膝举弓；不死＝奶白裹布青铜面／骷髅面螺旋尾幽灵／披甲矮人食尸鬼圆盾（对既有 Shade of Telos 与 ghoul）。棋子目录 239→251 款；`tests/token_mapping.lua` 更新（去掉批 J／L 中 Berethh 原生断言）、`tests/production/test_monster_batch_s.py` 新增。详见 `art/monster-batch-s/review/`。
怪物 Batch R（勘察二后续名单按分值取前 12：quasit／夸塞魔、weaver young／编织者幼体、orc necromancer／兽人死灵法师、orc assassin／兽人刺客、giant green ant／绿色巨蚁、giant red ant／红色巨蚁、fate spinner／命运纺织者、elven warrior／精灵战士、corrupted war dog／腐化的战犬、Warmaster Gnarg／战争领主格纳哥、Rak'shor, Grand Necromancer of the Pride／部落死灵大法师拉克·肖、grannor'vor／格兰诺伏尔 共 12 款；离线美术＋映射，未实机、未提交、未打包、未升版；2026-09-29）：选型见 `art/monster-batch-r/SELECTION.md`（分值＝§3 逐区 E 之和＋首领加权 12；12.0 并列取兽人首领与已选兽人凑成一组，另取 grannor'vor；排除目录已有、§4 内层≠默认名 I 类 6 个、§5.1 同名冲突、§5.2 KEEP）。逐条对照 `game/modules/tome` 源码与原生贴图重核，合同与哈希钉入 `evidence/monster-batch-r-20260929/source-contracts.json`：12 个身份的原生贴图全为 64×64、无 `nice_tile`，没有 native-tall；巨蚁两款与战犬用显式 `image=`，其余为 NPC.lua:33 默认名单图；Gnarg（`GNARG`）、Rak'shor（`RAK_SHOR`）与战犬（`CORRUPTED_WAR_DOG`）精确绑定 `define_as`，Gnarg 与 Rak'shor 为唯一单图。同图不同名：weaver young 与已有 weaver hatchling 共用同一原生 PNG，腐化战犬与 dire wolf（及 keepsake-meadow 的普通 war dog）共用 `canine_dw.png`，均按各自精确名称匹配，互不能冒用（负例已钉）。突变扫描：所有相关天赋只有粒子 shader，无 type/subtype/image/add_mos 出生写入；出生持续技仅为临时数值与粒子（死灵法师系 Hiemal Shield 等、Slow Motion、Stealth／Apply Poison，Stealth 属可见性而非外观）。**两处报告的命中**：Rak'shor 的 Corruptor auto_class 在 35 级之后可能学到 Flame of Urh'Rok（`shadowflame.lua:96`，改 type/subtype 为 demon/major），非出生突变，一旦启动即 body-changed 回退原生贴图、结束后恢复，未设 `urh_rok_form`（静态结论，未实机）；Gnarg 的 Berserker auto_class 可触发 Rampage 光环，属已支持的光环外观。ImageGen 共 **17/28** 次：首轮 12 次；rak-shor v1 骨杖越出圆盘（disc_overflow 0.987）未入库，v2 改短杖后通过；warmaster-gnarg v1 仅因盘面偏暗未过（底盘偏移 -9.24，无其他阻断项，未写豁免），v2 提示盘面不受阴影后通过（+7.70，最接近 ±8 容差）；orc-assassin v1 过门控但近黑深蓝（亮度 48.4，全库第 9 暗）、v2 中亮板岩蓝（54.8）48px 仍近黑，v3 改板岩青皮革、绿皮肤与双匕外伸后入选（-2.39，亮度 55.9，仅小幅提亮，轮廓分离明显好于 v1/v2；目标 ≥65 未达）；corrupted-war-dog v1 过门控但近黑毛（53.5）在 48px 成暗团，v2 改中灰毛、灰白腹口、亮紫绿裂纹、张口侧向扑击后入选（-1.15，亮度 69.7，略低于目标 70）；单件均 ≤3 次，被取代草稿在评审图中保留。成品 12 款无豁免、无 PENDING 请求，底盘偏移 -6.95…+7.70、半径 0.858–0.860、遮罩体亮度 55.0–122.9（均高于 45 地板）。同族区分：巨蚁在已有六款同一直排姿势的换色蚁之外换轮廓（绿：腹部蜷过背的 C 形＋毒滴；红：后肢立起、前肢高举的直立 T 形）；weaver young 是蜷成圆球、腹部带白螺旋的小蛛（对 hatchling 的放射形小蛛），fate spinner 是宽展锯齿腿加丝环的钢蓝大蛛；两个法袍兽人以“驼背无杖托魂火”对“挺立骨杖、尖领骨肩”区分，assassin 是低伏双匕的暗蓝皮，Gnarg 是横握巨剑的紫钢重甲；战犬是灰毛张口侧向扑击、紫绿裂纹加尖刺项圈（对棕色侧向踱步的 dire wolf）。48px 偏弱：orc-assassin（55.9，仍偏暗）、rak-shor（55.0，深紫袍靠骨白）、giant-red-ant（56.3）在深色盘上偏暗；fate-spinner 与 weaver-queen／weaver-hatchling 的 48px 区分主要靠钢蓝色与锯齿腿轮廓，丝环在 48px 很淡；quasit 棕对棕盘、靠圆盾与青铜高光。目录 227→239；纯 Lua 13 个独立脚本通过（`token_mapping` 13,898 项），生产测试 242 项、死资产审计（dead assets: none）与 `git diff --check`（排除 `evidence/`、`handoffs`）通过。
怪物 Batch Q（勘察二 §7 批次 8：fire drake hatchling／火龙幼仔、cold drake hatchling／冰龙幼仔、storm drake hatchling／风暴幼龙、sand-drake／沙龙、venom drake hatchling／毒龙幼仔、Rantha the Abomination／兰莎，憎恶形态、Briagh, Great Sand Wyrm／巨型沙龙布莱亚、Ukllmswwik the Wise／智慧的乌克勒姆斯维奇、fire drake／火龙、storm drake／风暴翼龙、cold drake／冰龙、venom drake／毒龙 共 12 款；离线美术＋映射，未实机、未提交、未打包、未升版；2026-09-29）：逐条对照 `game/modules/tome` 源码与原生贴图重核，合同与哈希钉入 `evidence/monster-batch-q-20260929/source-contracts.json`。八只龙与幼龙、沙龙、乌克勒姆斯维奇为无 `image=`／`nice_tile` 的 64×64 默认名单图；`FIRE_DRAKE_HATCHLING` 与 `NPC_COLD_DRAKE` 两个非唯一叶子自带 `define_as`，条目精确绑定；乌克勒姆斯维奇是唯一单图；兰莎（憎恶形态）与布莱亚是唯一体，`nice_tile` 显式写 tall PNG（64×128），走唯一 native-tall 路径，不设 `native_tall` 标记。运行时突变扫描：全部龙系天赋只有粒子 shader，无 type/subtype/image/add_mos 写入；出生持续技只有 Icy Skin（乌克勒姆斯维奇、兰莎，仅临时数值）；布莱亚的 Summoner auto_class 可能学到 Master Summoner（`addShaderAura`，属已支持的光环外观，静态结论，未实机观察）。同名冲突：Wyrmic 召唤的 fire drake（同名／类型／PNG、无 define_as）沿用现有精确身份行为，会套用区域火龙棋子；Grand Arrival 的 fire drake hatchling 无 define_as，因区域叶子已绑定而保持原生——**召唤物取舍为待决问题，未裁决、未扩展键**。12 张全过风格门控、无豁免；重试：ukllmswwik v1 三叉戟与背鳍越出盘沿（disc_overflow 0.908）返修为 v2；storm-drake v1 过门控但 48px 偏细偏暗，重画为 v2（亮度 70.7→94.7）；共 14 次 ImageGen 调用（上限 28，单件≤2）。同元素幼龙／成年龙以姿态区分（火：直坐圆润 vs 低伏三角展翼喷火；冰：低扑 vs 缩肩折翼的厚重团块；风暴：直立展翼小 T 形 vs 斜向窄翼飞镖；毒：S 形盘绕 vs 宽厚驼背低头喷酸），五系与既有 varsha／rantha／corrupted-sand-wyrm 相区分。48px 偏弱：rantha-abomination（暗石板紫，亮度 70.8，靠青白裂纹）、venom-drake（暗橄榄绿 70.3）、fire-drake（70.1，与 varsha 同为红系但橙红＋黑翼）。棋子目录 215→227 款；`tests/token_mapping.lua` 更新（去掉 batch H 中 sand-drake 原生断言）、`tests/production/test_monster_batch_q.py` 新增。详见 `art/monster-batch-q/review/`。
怪物 Batch P（勘察二 §7 批次 7：snow giant／雪巨人、snow giant thunderer／闪电雪巨人、snow giant boulder thrower／雪巨人投石者、snow giant chieftain／雪巨人酋长、minotaur／米诺陶、mountain troll／山岭巨魔、mountain troll thunderer／闪电山岭巨魔、ogre guard／食人魔守卫、ogre mauler／食人魔重击者、ogre rune-spinner／食人魔符文师、ogre pounder／食人魔摔跤手、Healer Astelrid／孔克雷夫治疗师亚斯特莉 共 12 款；离线美术＋映射，未实机、未提交、未打包；2026-09-29）：逐条对照 `game/modules/tome` 源码与原生贴图重核，合同与哈希钉入 `evidence/monster-batch-p-20260929/source-contracts.json`。四种雪巨人与 minotaur 在 `nice_tile` 中显式写 tall PNG（非唯一，`native_tall=true`）；四种食人魔用 `nice_tile{tall=1}` 简写（非唯一 `native_tall=true`）；Healer Astelrid 是同一简写的唯一身份，绑定 `define_as=HEALER_ASTELRID`（与 Kyless 同类，不设 `native_tall`）。勘察把两只山岭巨魔标为“默认名单图”，源码实为显式 `image="npc/troll_m.png"`／`troll_mt.png`（64×64），按普通单图条目接入。突变扫描：12 个身份无 type/subtype/image/add_mos 出生写入；仅食人魔基类带 `sustains_at_birth`，其中只有 Astelrid 的 Arcane Shield 与 Living Lightning 是持续技（只加护盾、临时值与粒子）；山岭巨魔雷鸣者的 Thunderstorm 为持续技但无出生启动；Warshout 只读 `self.subtype` 选日志文字；Flame of Urh'Rok 不属于本批任何身份（负例覆盖）。**同名待用户决定（保持现有精确匹配行为，未做任何决定，无 name+define_as 键扩展）**：（1）野性召唤“米诺陶”（`talents/gifts/summon-melee.lua:365`）同名、同型、同 tall PNG、无 define_as、带 summoner，因此与区内 minotaur 一样戴该棋子，触发野性召唤改名的“minotaur (wild summon)”保持原生；（2）Elvala 镇的“ogre rune-spinner”（`zones/town-elvala/npcs.lua:106`，`{tall=1}`）同名同型同图同体，无法用任何精确检查区分，也戴同一棋子。`tests/token_mapping.lua` 把这两种当前行为钉成测试，改决定时须同步改。ImageGen 共 **16/28** 次：首轮 12 次；snow giant v1（底盘偏移 -8.16）与 boulder thrower v1（-9.04）仅因盘面偏暗未过门控（无其他阻断项，未入库、未写豁免），v2 仅加“盘面略提亮”后通过；minotaur v1 过门控但与既有 Minotaur of the Labyrinth 在 48px 近似同款（同为暖棕牛头人、斧低垂左侧），v2 改奶白／炭黑斑纹后斧头举高越出圆盘（扇区上偏 +38.5，警告项，未入库），v3 改横持短柄斧、缩小构图后入选。成品 12 款无豁免、无 PENDING 请求，底盘偏移 -7.14…+7.35（snow giant +7.35、ogre guard -7.14 最接近 ±8 容差）、半径 0.856–0.864；遮罩体亮度 63.6–106.2（均高于 45 地板）。同族区分：snow giant＝光头石板蓝灰、短锤低垂；thunderer＝白长须、双拳举起夹黄白闪电；boulder thrower＝暖灰褐皮、双臂抱起大圆石；chieftain＝冰青皮、黑铁牛角盔、白灰毛皮披肩、横持符文大锤（对既有 Burb 的银板甲与闪电）；minotaur＝奶白配炭黑斑纹、黑角、横持双刃斧（对既有 Minotaur of the Labyrinth 的暗棕，及 Horned Horror 的洋红触手冠）；mountain troll＝锈褐鹅卵石疣、双拳护架（对既有森林绿／石灰黑／洞穴米色巨魔）；thunderer＝钢青疣皮、双臂张开夹闪电；guard＝棕黄皮蓝长裤钢肩甲持锤、mauler＝砖红皮金拳套无武器、rune-spinner＝橙红皮金符文、一手举火旋、摔跤手＝亮矢车菊蓝皮双臂张开、Astelrid＝深紫长袍白围裙、石膏手术刀棒。48px 偏弱：Astelrid（紫袍在石质地板上对比低）、mountain troll 与 ogre mauler（棕／红系较暗，遮罩体亮度最低）、mountain troll thunderer 蓝与 ogre pounder 蓝色系靠姿势区分；雪地上浅色雪巨人依赖暗盘。审图 48/64/96 彩色＋灰度三组（含既有相关棋子）、六种真实地板 48px 合成（Daikara 岩地／雪地、korpul 石质 A／B、洞穴岩／蘑菇，含 ×2，含被拒／被取代草稿对照）与 `luminance.json` 见 `art/monster-batch-p/review/`；目录 203→**215** 款，`data/token-manifest.json` 重新生成（version 不变）；`tests/token_mapping.lua` 12,075 项（改写批 I 与旧“未覆盖 mountain troll”两条已过期负例）；新增 `tests/production/test_monster_batch_p.py`；三份工具批次名单加入 `monster-batch-p`。需实机确认：四种雪巨人、minotaur、四种食人魔与 Astelrid 的两格身体替换（简写与显式 PNG 两种展开）、Astelrid 出生持续技期间的匹配、野性召唤米诺陶与 Elvala 符文师的显示。
怪物 Batch O（勘察二 §7 批次 6：white ooze／白泥怪、gigantic corrosive tunneler／巨大腐蚀挖掘者、gigantic gravity worm／巨大重力沙虫、slimy ooze／史莱姆泥怪、poison ooze／剧毒泥怪、carrion worm mass／腐肉虫群、brittle clear ooze／易碎透明泥怪、cute little bunny／可爱的小白兔、dredgling／坠灵恐魔、onilug／欧尼路格、wretchling／小劣魔、brecklorn／布瑞克隆 共 12 款；离线美术＋映射，未实机、未提交、未打包；2026-09-29）：逐条对照 `game/modules/tome` 源码与原生贴图重核，合同与哈希钉入 `evidence/monster-batch-o-20260929/source-contracts.json`。四种软泥、bunny、dredgling、wretchling、brecklorn 为 NPC.lua:33 默认名单图的非唯一单图条目；carrion worm mass 绑定 `define_as=CARRION_WORM_MASS`；两只 gigantic 蠕虫在 `nice_tile` 中显式写 tall PNG（非唯一，`native_tall=true`，批 K 保持原生的两条负例已改写为“K 保持原生、O 映射”并新增互不能借用高身体的负例）；onilug 是 `nice_tile{tall=1}` 简写的非唯一 `native_tall=true` 条目（简写已由批 G 探针与批 L 实机对 xhaiak／shiaak／nereid 确认）。突变扫描：12 个身份无 type/subtype/image/add_mos 出生写入；仅 dredgling 与 brecklorn 带 `sustains_at_birth`，brecklorn 的 Gloom 只加临时值与粒子；gravity worm 的 Gravity Locus 为持续技但无出生启动；Flame of Urh'Rok 不属于本批任何身份（负例覆盖）。**同名待用户决定**：腐肉虫群另有玩家腐化系 Worm Rot／Infestation 召唤物（`talents/corruptions/rot.lua:62`，同名同型同 PNG 但无 define_as、带 summoner），也由 `general/npcs/horror.lua:109` 的受伤生虫恐魔与 Worm Rot 效果生出；按现有 define_as 绑定它被拒绝、保持原生（现有行为，未做任何召唤物决定，无 name+define_as 键扩展），是否让召唤物也戴棋子留待用户裁定。ImageGen 共 **14/28** 次：首轮 12 次；cute little bunny v1 因耳尖越出圆盘（半径 0.879，上限 0.867）未入库，v2 改矮耳后倾并收紧构图后通过；onilug v1 过门控但为细弱暗柱（48px 仅约三分之一盘宽），v2 改为宽肩佝偻粗杖姿势后入选。成品 12 款无豁免、无 PENDING 请求，底盘偏移 -7.01…+4.88（gravity worm 最接近 ±8 容差）、半径 0.858–0.860；遮罩体亮度 70.9–197.2（均高于 45 地板）。同族区分：white ooze＝低平扇边乳白泥坑带三滴（对既有白果冻高圆丘）、slimy＝柠檬黄绿缠绳、poison＝紫红圆丘长孢子伞、brittle clear＝冰青带裂纹尖碎片；corrosive tunneler＝酸绿 S 形盘卷、圆口利齿滴酸（对批 K 橄榄色花瓣口沙虫）、gravity worm＝石板蓝灰紧螺旋、珊瑚花口、环绕悬浮碎石；carrion worm mass＝几条肥胖蜡黄粉褐蠕虫双头昂起（对既有白／绿虫群的一大团细虫）；bunny＝蓬松白兔（对既有白鼠）；dredgling＝赤裸鲑粉爬行者巨眼（对既有 drem 甲士与 dremling 石灰巨人）；wretchling＝橄榄柠檬绿带黄酸泡、尖背扑击；onilug＝灰紫佝偻长臂持骨杖紫晶；brecklorn＝锈橙翼膜蝙蝠身尖叫人脸。48px 偏弱：onilug（灰紫在暗地板上对比低）、gravity worm（暗石板蓝在石地上偏暗）、brecklorn 与 wretchling 在沙地／橙褐地板上对比低、carrion worm mass 在沙地上。审图 48/64/96 彩色＋灰度三组（含既有相关棋子）、九种真实地板 48px 合成（含 ×2，含被拒／被取代草稿对照）与 `luminance.json` 见 `art/monster-batch-o/review/`；目录 191→**203** 款，`data/token-manifest.json` 重新生成（version 不变）；`tests/token_mapping.lua` 11,028 项；新增 `tests/production/test_monster_batch_o.py`；三份工具批次名单加入 `monster-batch-o`。需实机确认：两只 gigantic 蠕虫与 onilug 的两格身体替换、brecklorn 出生 Gloom 期间的匹配、Worm Rot 召唤的腐肉虫显示。
怪物 Batch N（勘察二 §7 批次 5：skeleton magus、ghast、shadow stalker、lesser vampire、forest wight、vampire、master vampire、ghoulking、bone giant、grave wight、elder vampire、The Shade of Telos 共 12 款；离线美术＋映射，未实机、未提交、未打包；2026-09-29）：逐条对照 `game/modules/tome` 源码与原生贴图重核，合同与哈希钉入 `evidence/monster-batch-n-20260929/source-contracts.json`。skeleton magus、ghast、ghoulking、Shade of Telos 为 NPC.lua:33 默认名单图；四档 vampire、forest／grave wight、shadow stalker 显式 `image=`；master vampire（leaf `image=` 加 `nice_tile` 显式 tall PNG）与 bone giant（`nice_tile` 显式 tall PNG）均非唯一，`native_tall=true`；elder vampire 是普通 64x64；shadow stalker 绑定 `define_as=SHADOW_STALKER`，Shade of Telos 为 unique＋`SHADE_OF_TELOS`。突变扫描：本批 12 个身份无 type/subtype/image/add_mos 出生写入；vampire 的 sustains_at_birth（Eternal Night／Blur Sight／Phantasmal Shield）只加粒子和临时值，wight 无持续技，Fade 只挂 EFF_FADED（无形象字段）；随机符文的隐身／虚化会设 shader，匹配器本就回退原生；Lord of Skulls 改名，落出精确名键。同名核查：Necromancer 的 ghast／ghoulking／bone giant 召唤物与原生同名同图无 define_as，无法也无需拒收（按既有“召唤物同身体”合同接受，与批 K 因 define_as=GHOUL 而排除 ghoul 召唤物不同；批 K 原“ghast／ghoulking 保持原生”的两条负例已删除并注明）；shadow claw（SHADOW_CLAW／SHADOW_CASTER）、vampire lord、barrow／emperor wight、eternal／heavy bone giant、skeleton mage 等保持原生并有负例，无 name+define_as 键扩展。ImageGen 共 **25/28** 次（其中 grave wight 首次调用因模型满载 7.8 秒无产出、不含图像，仍按目录记账）：首轮 12 次；门控拒收（半径）skeleton magus v1 1.068 与 v3 1.018、elder vampire v1 0.962、forest wight v1 0.877 与 v3 1.034、Shade of Telos v1 0.940，均以收紧构图重生成；过门控但审图淘汰：vampire v1（遮罩亮度 42.8＜45）、elder vampire v2（42.6）与 v3（49.9，深酒红直立长袍在 48px 像 The Master）、ghoulking v1（50.8）、master vampire v1（58.5，深海军蓝）、skeleton magus v2（图形只占盘约一半）。成品 12 款无豁免、无 PENDING 请求，底盘偏移 -3.38…+4.71，半径 0.858–0.862；skeleton magus 用 v4（改为前臂举于肩前，全新设计）。遮罩体亮度 52.6–137.2；vampire（52.6）与 elder vampire（52.6）虽高于地板 45，但低于本批其余款，靠饱和的猩红／紫红色相与轮廓可读，需实机复核。同族区分：vampire 四档＝橙衣无披风青年／猩红披风蹲伏／钴蓝长披风直立高个（奶白背心）／梅紫连帽长袍持淡紫法球（对既有 The Master 深红持杖）；ghoul 三档＝既有褐黄低伏／ghast 灰绿佝偻长臂／ghoulking 褐皮金冠张臂；skeleton magus＝象牙金骨、肩前双手火焰、钴蓝飘带（对既有披风骷髅法师）；forest wight 绿甲斧盾骷髅／grave wight 淡青透明幽灵／shadow stalker 石板紫烟雾利爪／Shade of Telos 冰蓝紫长袍法师冠与晶杖。48px 偏弱：forest wight（暗橄榄绿、图形较小，在 cave 与 korpul 地板上对比低）、shadow stalker（灰度下偏暗，为烟雾团）、Shade of Telos 与 grave wight 灰度下同为浅色幽灵团（靠青／蓝紫色相区分）、elder vampire 图形偏小、lesser vampire 深发与暗裤。审图 48/64/96 彩色＋灰度三组（含既有 skeleton mage／warrior、ghoul、The Master、half-finished bone giant）、korpul／cave／rakshor／grass／flower 八种真实地板 48px 合成（含 ×2，含被淘汰草稿对照）与 `luminance.json` 见 `art/monster-batch-n/review/`；目录 179→**191** 款，`data/token-manifest.json` 重新生成（version 不变）；`tests/token_mapping.lua` 10,108 项；新增 `tests/production/test_monster_batch_n.py`；三份工具批次名单加入 `monster-batch-n`。需实机确认：master vampire／bone giant 两格身体替换、vampire 出生 sustain 期间的匹配、Necromancer 召唤物的 ghast／ghoulking／bone giant 显示。
怪物 Batch M（勘察二 §7 批次 4：losgoroth、gwelgoroth、manaworm、faeros、umber hulk、greater gwelgoroth、xorn、ultimate gwelgoroth、telugoroth、Fyrk Faeros High Guard、xaren、greater faeros 共 12 款，另含 elven cultist；离线美术＋映射，未实机、未提交、未打包；2026-09-29）：逐条对照 `game/modules/tome` 源码与原生贴图重核，合同与哈希钉入 `evidence/monster-batch-m-20260929/source-contracts.json`。九个元素为 NPC.lua:33 默认名单图的非唯一单图条目；greater／ultimate gwelgoroth 在 `nice_tile` 中显式写 PNG（非唯一，`native_tall=true`），Fyrk（`define_as=FYRK`，unique）同为显式 tall PNG，均可静态钉死；greater faeros 是普通 64x64 单图（tall 的是 ultimate faeros，保持原生并有负例）。runtime 突变扫描：只有 Flame of Urh'Rok 写 type/subtype；ultimate gwelgoroth 的 Hurricane 维持技能什么都不写，greater faeros／Fyrk 的 Fiery Hands／Wildfire 只挂粒子，Fyrk 的 Burning Wake 只加 `_isshaderaura` 条目（`nativeTallImage` 已忽略，同 Harkor'Zun）。**Elven cultist：批 L 保持原生，批 M 映射**——按批 L 实机（出生即 demon/major，`__old_type={humanoid,shalore}`，`T_FLAME_OF_URH_ROK` 维持中，图与 define_as 不变）登记为 humanoid/shalore＋`urh_rok_form=true`，与 Grand Corruptor 同一现有机制，`urh_rok_form` 现仅这两项；`tests/token_mapping.lua` 加入 demon 形态与恢复 humanoid 形态正例及镜像 Grand Corruptor 的负例（无维持技能、无／错／多余 `__old_type`、subtype 非 major、换图、带 define_as、未知 unique、shader、其他精英法师不得借用），并改写批 L 原「cultist 无条目／保持原生」断言。同名核查：town-point-zero 的 "monstrous losgoroth"（同 PNG、另名、define_as）、ultimate faeros、greater／ultimate telugoroth 保持原生并有负例，无 name+define_as 键扩展。ImageGen 共 **14/28** 次：首轮 13 次，仅 greater faeros v1 因火焰越出圆盘（半径 0.874）被拒，且与 Fyrk 同为粗壮火巨人，v2 改为瘦高直立金橙＋单根头焰＋飘曳火披风，并以 Fyrk 导出作对照参考，干净通过；其余 12 款首轮即过门控，底盘偏移 -5.12…+3.97、半径 0.856–0.862、无豁免／PENDING。同族区分：losgoroth＝紫色四弯触手，manaworm＝黄色盘蛇，telugoroth＝金青紫彩带圆旋（对既有 shivgoroth 晶体巨人）；gwelgoroth＝细长浅灰蓝漏斗，greater＝宽胖石板蓝锥带三圈环和褐岩，ultimate＝宽深宝蓝锥带云冠与黄白闪电；faeros＝瘦长 X 形亮橙，greater faeros＝直立金黄橙，Fyrk＝粗壮绯红重肩；umber hulk＝褐甲虫形带象牙大颚，xorn＝赭黄圆桶单眼洞四臂，xaren＝银灰矿石骷髅脸，均与 Harkor'Zun（褐色双臂）分得开。遮罩体亮度 70.7–177.4（均高于 45 地板）。48px 偏弱：gwelgoroth 细小苍白、greater 与 ultimate gwelgoroth 同为锥形（靠宽度、明度、色相区分，是本批最弱一对）、umber hulk 与 xaren 在 daikara 灰岩／burnt 褐地上对比偏低；Fyrk 无可见三叉冠与浅色脸，主要靠绯红色相和体量与 greater faeros 区分。审图 48/64/96 彩色＋灰度（含既有 shivgoroth、Harkor'Zun、精灵棋子）、九种真实地板（void、burnt、daikara、caldera、korpul、grass）48px 合成（含 x2）与 `luminance.json` 见 `art/monster-batch-m/review/`；目录 166→**179** 款，`data/token-manifest.json` 重新生成（version 不变）；`tests/token_mapping.lua` 9,327 项；新增 `tests/production/test_monster_batch_m.py`；三份工具批次名单加入 `monster-batch-m`。需实机确认：Fyrk 带 Burning Wake 光环时的 native-tall 匹配、cultist 在 demon 形态与恢复形态之间的开关往返、ultimate／greater gwelgoroth 两格身体替换。

怪物 Batch L（勘察二 §7 批次 3：兽人三种、沙洛尔精灵四种、纳迦两种、yaech 潜水者，另含 Kyless 共 12 款；离线美术＋映射，未实机、未提交、未打包；2026-09-29）：逐条对照 `game/modules/tome` 源码与原生贴图重核，合同与哈希钉入 `evidence/monster-batch-l-20260929/source-contracts.json`。orc warrior／soldier／archer 分别绑定 `define_as` HILL_ORC_WARRIOR／ORC／HILL_ORC_ARCHER（Charred Scar 另有同名 "orc warrior"，define_as 为 ORC_ATTACK、基类不同，由现有 define_as 检查拒收并有负例，未做 name+define_as 键扩展）；elven guard、mean looking elven guard、elven mage／tempest／blood mage、yaech diver 为默认名单图；naga myrmidon 显式 `image=npc/naga_myrmidon.png`；naga nereid（murgol-lair 与 slazish-fen 两处定义等同）为 `{tall=1}` 简写的非唯一 `native_tall=true` 条目（同一简写已由批 F／G 的 xhaiak／shiaak／tidewarden／tidecaller 实机确认解析为磁盘文件名）；**Kyless 纳入**：批 J 因静态推断保持原生，其实机普查（`evidence/monster-batch-j-live-20260929/census.json`）显示运行时 `image=invis.png` 且唯一 add_mos 为 `{image="npc/humanoid_human_kyless.png", display_h=2, display_y=-1}`，重核天赋（Willful Strike／Deflection／Blast／Unseen Force／Feed 系／Devour Life／Creeping Darkness／Dark Tendrils）与 `sustains_at_birth` 均不写 type/subtype/image，故按普通唯一 native-tall 条目接入（`define_as="KYLESS"`，含实机形态正例，批 J 测试改为记录“J 保持原生、L 接入”）。**保持原生：elven cultist**——掌握 Flame of Urh'Rok（`shadowflame.lua:96-97`）且带 `sustains_at_birth`，出生即可能变为 demon/major（与 a3a0225 的 Grand Corruptor 同类），无实机复核，不臆造规则；若日后实机确认，可对该条目加现有 `urh_rok_form=true`。全库天赋扫描（type/subtype/image、`__old_type`、`replace_display`、add_mos、moddable_tile 写入）除 Flame of Urh'Rok 外只有与本批无关的召唤物写入，本批其余 12 个身份无命中。ImageGen 共 **15/28** 次：首轮 12 次；naga myrmidon v1 因三叉戟与尾越出圆盘（半径 1.161，上限 0.867）未入库，v2 全新生成（收紧构图）后干净通过；Kyless v1（遮罩亮度 48.1）与 elven blood mage v1（51.9）虽过门控，但真实地板 48px 偏暗，自行淘汰并重生成 v2（62.1／61.9）；12 款无豁免、无 PENDING 请求，底盘偏移 -4.43…+3.15，半径 0.858–0.859。同族区分靠轮廓和明度而非仅色相：三兽人＝低挥弯刀（橄榄＋锈褐）／宽斧刃尖刺灰钢甲／高竖弓（卡其皮甲）；两守卫＝挺立、金肩甲、竖剑高盾／佝偻、褐橄榄无金、剑低指；三法师＝靛紫长袍持竖杖／天蓝高举闪电／石板蓝灰红血渍双手下垂滴血（不同于红袍持球的 Kryl-Feijan 侍僧）；myrmidon（钴蓝尾、钢甲、竖三叉戟）与 nereid（淡金尾、淡紫火花法杖）对照已上线的 tidewarden／tidecaller／Nashva／Zoisla。自评 48px 较弱项：Kyless（亮度 62.1、深发与烟雾，草地上偏暗）、naga myrmidon／nereid（图形只占盘面约一半，小）、elven blood mage 与 elven mage 灰度下同为深袍，靠竖杖与佝偻姿态区分，需实机复核。审图表（彩色／灰度 48/64/96 三组、真实地板 48px 合成含 ×2、亮度）在 `art/monster-batch-l/review/`。目录 154→**166** 款，`version` 保持 0.6.27，`data/token-manifest.json` 重新生成。

怪物 Batch K（勘察二 §7 批次 2：水生／蛛形／食尸鬼／drem／沙虫掘进者共 12 款；离线美术＋映射，未实机、未提交、未打包；2026-09-29）：12 个身份均逐条对照 `game/modules/tome` 源码与原生贴图核实（不采信勘察表的风险评级），来源哈希钉入 `evidence/monster-batch-k-20260929/source-contracts.json`：squid、ink squid（aquatic/critter）、water imp（aquatic/demon）、orb spinner、giant／spitting／chitinous spider 为默认名单图；weaver hatchling 用显式 `image=npc/spiderkin_spider_weaver_young.png`；ghoul 绑定 `define_as="GHOUL"`；drem 显式 `image=npc/horror_corrupted_dremling.png`（与 dremling 文件互换，两条目互不能借用对方文件，负例覆盖）；Walrog（unique，无 define_as）与 gigantic sandworm tunneler（非 unique，条目带 `native_tall=true`）均在 `nice_tile` 中显式写 PNG，解析后高身体图可静态钉死（不同于 Kyless／xhaiak 的 `{tall=1}` 简写），两者的单格路径也接受。同名核查：`giant spider` 另有教程区 TUT_SPIDER_1（同 type、define_as 不同）与野性召唤物（type animal），`ghoul` 另有 Master of Flesh 召唤物（同名同图无 define_as）、risen corpse／Walking Corpse（同图异名）；均由现有精确身份合同（define_as／type 不符）拒收，保持原生，因此不需要 name+define_as 键扩展，catalog 名称仍唯一（测试逐名断言）。本批无保留原生项。ImageGen 共 **15/26** 次：首轮 12 次；gigantic sandworm tunneler v1 因花瓣与碎石越出圆盘（半径 0.899，上限 0.867）未入库；Walrog v1 通过门控但身体铺满整盘、主体侵入警告值 31.0（阈值 20）；ink squid v1 只占半个盘面、48px 过细；三款各返修一次（v2 均收敛，v1 保留为被取代草图，不入选）。12 款无豁免、无 PENDING 请求，底盘偏移 −6.02…+1.12，半径 0.858–0.860，主体侵入最大 7.37，遮罩体亮度 59.2–117.1（均高于 45 地板）。同族区分：squid＝圆胖赭褐外套、八条粗短卷腕；ink squid＝细长薰衣草灰尖外套＋三角鳍、长拖须；water imp＝青绿小恶魔、双角蝠耳、举手施法；Walrog＝亮青蓝水体、双弯角、漩涡下身（对冰元素 shivgoroth）；weaver hatchling＝圆润半透明浅蓝、足端发光球（对大只毛茸茸的 Weaver Queen）；orb spinner＝细长分节钢蓝／骨白肋纹腹部、长腿；giant spider＝石板灰＋银色人字纹、细长腿（对 Ungolë 纯黑圆身红眼）；spitting spider＝栗褐多毛、喷酸绿毒液；chitinous spider＝象牙白光滑装甲板、粗短刺腿；ghoul＝驼背赭褐腐尸、长爪垂地；drem＝矮壮斧盾拾荒战士、灰白无脸（对高大浅石灰色 dremling）；tunneler＝粗壮土褐环纹蠕虫、四瓣花状裂口、碎石堆（对橙色 sandworm、环形 destroyer、绿拱 burrower）。48px 偏弱：giant spider（深灰，与 Ungolë 同为深色圆身蜘蛛，靠银纹与长腿区分）、orb spinner（暗钢蓝）、ghoul 与 drem（暖褐色在橙色沙地／洞穴地板上对比较低）；Walrog v2 与 tunneler v2 占盘偏小但轮廓清楚。审图：`art/monster-batch-k/review/`（三组 48/64/96 彩色＋灰度、`floor-readability-48(.png|-x2.png)` 用水下、morass 虚空、ardhungol 洞穴、daikara 岩地、沙地、deep-bellow 幽暗、korpul 石、草地等真实地板、`luminance.json`）。新增测试：`tests/token_mapping.lua`（12 款正例、负例、同族借图、教程蜘蛛／召唤物／召唤食尸鬼、Walrog／tunneler 高身体形态、名称唯一性）与 `tests/production/test_monster_batch_k.py`；原「drem 保持原生」「squid／tunneler 为同族原生」的旧负例已按新事实改写。工具白名单加入 `monster-batch-k`（build_monster_art／check_token_style／prepare_runtime_art）。注意：`art_tasks.py prepare` 会比较 catalog 与 manifest，须在写入 catalog 条目之前生成任务包（本批第 4 包在暂存 catalog 后生成）。

怪物 Batch J（保证首领／唯一怪第 1 批：11 款；离线美术＋映射，未实机、未提交、未打包；2026-09-29）：第一步小改动——`heartGloomBase` 白名单由 vermin/rodent、animal/canine 扩为再加 animal/bear、immovable/plants。核对 `heart-gloom/npcs.lua` 的 `alter()`：只改 name（前缀）、追加一个天赋、改 rarity，type/subtype/image/nice_tile 均不动，bear.lua、plant.lua 与 rodent.lua、canine.lua 走同一 `load(..., alter())`，来源相同；并额外要求基底条目不是 unique 也无 define_as（改名通用怪不可能是 Norgos 之类）。新增正例 gloomy brown bear／deformed black bear／dreaming poison ivy／sick giant venus flytrap／slumbering honey tree 及负例（cave bear、war bear、未知植物、Norgos、错 type、错 subtype、换图）。Batch J：Shardskin、The Withering Thing（紫色 tint 仅为颜色调制）、The Dreaming One（`seed_of_dreams.png`）、Weaver Queen（native-tall，nice_tile 显式写 PNG）、Murgol、Lady Nashva（native-tall）、The Possessed（native-tall）、Subject Z、Grand Corruptor、Assassin Lord、Ben Cruthdar the Abomination 均逐条对照源码和原生贴图核实为精确 unique 条目，来源哈希钉入 `evidence/monster-batch-j-20260929/source-contracts.json`。两处注意：town-zigur 另有同名、同 define_as、同图的 Grand Corruptor（`unique="Grand Corruptor Zigur"`），视为同一角色，由同一条目覆盖并有测试；Ben Cruthdar the Cursed（town-lumberjack-village）与 Abomination 共用 PNG 但名字不同，保持原生（负例）。**Kyless 保持原生**：只用 `nice_tile{tall=1}` 简写、无 image=，解析时刻 e.image 为 nil（与批 F 的 xhaiak／shiaak 同一条追踪），高身体图无法静态钉死，且有 never_act／seen_by／keepsake 任务钩子，未启动游戏不能证实，证据里 `kept_native` 记录原因。ImageGen 共 **17/26** 次（每款不超过 3 次）：首轮 11 次，Murgol（1.052）、Lady Nashva（0.906）、Subject Z（0.995）因武器与肢体越出圆盘（半径上限 0.867）未入库，各返修一次收敛；Grand Corruptor v1 通过门控但亮度 42.7 低于地板 45 且近黑海军蓝，v2 改为亮钴蓝后 58.7；The Possessed v1 亮度 49.4 偏暗，v2 改浅鼠尾草绿披风后 69.9；Subject Z v2 过门控但人物只占盘面三分之一，v3 放大后 73.1。11 款均无豁免、无 PENDING 请求，底盘偏移 -6.96…+2.11，半径 0.858–0.860，Ben 主体侵入警告值 12.97（阈值 20，未触发）。同族区分：Shardskin＝宽扁金色晶堆＋内嵌棕色树桩（对白／红／绯红晶簇、Spellblaze 紫簇、人形 Simulacrum）；Withering Thing＝瘦骨嶙峋、蛆虫蠕动的灰紫恶狼（对五种健康犬类）；Dreaming One＝光滑水青玻璃球＋淡紫漩涡眼；Weaver Queen＝霜白毛绒大蜘蛛（对 Ungolë 黑蜘蛛）；Murgol＝矮壮鱼头带鳍冠、红眼、金三叉戟（非 naga）；Nashva＝青绿尾、水球、青色三叉戟、冠冕（对 Zoisla 橙红尾）；Possessed＝绿骷髅脸＋橙色火焰冠＋鼠尾草绿披风；Subject Z＝僵直站立、奶白束腰衣＋苔绿裤、双短匕（对蜷身的 cutpurse）；Grand Corruptor＝双角钴蓝兜帽＋绯红腰带＋红球法杖；Assassin Lord＝橄榄色毛领披肩、金袖、绯红裤、前冲；Ben＝苍白驼背巨汉，斧、青色时间裂纹（对 krogar、bandit、Abomination 肉塔）。评审图 48/64/96 彩色与灰度（含相关已上线 token）、八种真实地板 48px 合成（含 x2）、`luminance.json` 见 `art/monster-batch-j/review/`，脚本 `make_review_sheets.py`，任务包生成 `make_batches.py`；目录 131→**142** 款；`tests/token_mapping.lua`（6,681 项）新增逐款精确正例、define_as／type／subtype 变更、tall 无 image 形态、同族借图、Zigur 变体和多个原生近似体负例；新增 `tests/production/test_monster_batch_j.py`；三份工具批次名单加入 `monster-batch-j`；运行贴图与 `data/token-manifest.json` 最后一步 `prepare_runtime_art.py` 重生成一次（142 项，version 仍为 0.6.27）。自评弱项：Murgol 48px 偏灰、亮度 76.6，靠鳍冠与金三叉戟辨认；Subject Z 与 cutpurse 同为奶白上衣的小人，靠直立对称姿态和绿裤区分；Possessed 披风在暗灰地板上仍偏暗，靠火焰冠与绿脸辨认；Nashva 较小。均需实机确认，尤其三个 native-tall 条目（Weaver Queen、Nashva、Possessed）在夹具里的两格身体替换，以及 Zigur 的 Grand Corruptor。

怪物 Batch I 实机验证（2026-09-29；已通过）：`run_monster_live_validation.py --batch i` 隔离夹具 6 场冷启动，12 个 token id 全部精确匹配、0 `Lua Error`、进程均已停止（3 自然：green ooze、侍僧；其余摆位）；软泥与 shipped 四色软泥同框可分，Norgan 作 NPC 与入队后（control=order）token 均正常且玩家 token 不变，elven corruptor 保持原生。首轮发现 Harkor'Zun 在 Native↔Refined 往返后因 Stone Skin 光环进入 `add_mos`、`nativeTallImage` 判 `native-tall-changed` 而回退原生；已由 32f4ec5（`nativeTallImage` 忽略光环条目）修复，tempest-peak 场重跑：两轮 Native→Refined 往返后 token 均恢复、光环包在 token 外、无重复原生体，Burb toggle 无回归（首轮失败证据保留在 `history-first-run/`）。见 [实机证据](evidence/monster-live-i-20260929/README.md)。

怪物 Batch I（12 款：四个原生软泥／果冻、Tempest Peak 三首领、Norgan、slimy crawler、Spellblaze Simulacrum、Kryl-Feijan 侍僧、Z'quikzshl；离线美术＋映射，未实机、未提交、未打包；2026-09-29）：green ooze、crimson ooze、gelatinous cube、Malevolent Dimensional Jelly 按 NPC.lua:33 公式静态解出图（ooze.lua／jelly.lua 整条继承链无 image=／nice_tile／add_mos，与已上线的 black/yellow/red/blue ooze 同路径；其余六种 jelly 才是显式 image=），四张 64x64 原生贴图均在盘上；Fragmented Essence 与 Harkor'Zun（`FULL_HARKOR_ZUN`，type 改为 demon/major）是两条独立 unique，Burb（`BURB_SNOW_GIANT`）、Simulacrum（image= 与 nice_tile 指同一 PNG）为 native-tall／单图 unique；Norgan（`NORGAN`）、slimy crawler（`SLIMY_CRAWLER`）、侍僧（显式复用 elven corruptor 图，绑定 `define_as=ACOLYTE`，elven corruptor 保持原生）、Z'quikzshl（type 覆写为 undead/molds，四种 immovable/molds 棋子不会误配）均为精确条目，合同与哈希钉入 `evidence/monster-batch-i-20260929/source-contracts.json`。ImageGen 共 **18/26** 次（每款不超过 2 次；Burb 首轮仅 base_drift -9.76，未入库，按 G 的先例改「校准措辞」重生成后 +3.19）；12 款均无豁免、无 PENDING 请求，底盘偏移 -6.66…+3.19，半径 0.856–0.860。四款 v1 虽过门控但被人工淘汰并重生成：crimson ooze（近黑酒红，亮度 40.1，与 red jelly／sanguine experiment 糊成一团→v2 树莓玫红 53.4）、侍僧（近黑长袍 41.3→v2 淡紫红袍 56.5）、Malevolent Dimensional Jelly（深靛蓝边缘暗淡→v2 紫水晶色 84.9）、Z'quikzshl（v1 灰绿低对比骨堆、v2 绿色圆丘像另一种 green mold，v3 象牙肋骨拱＋骷髅立在绿紫菌垫上，亮度 111.5）。同族区分靠轮廓和明度：软泥＝扁平带三滴＝green／直立浪头带滴珠和分裂芽＝crimson／刚性半透明立方＝cube，果冻＝带星空窗和卷须的扁平水洼；Tempest Peak＝碎片堆（紫裂纹）／灰褐石人（琥珀裂纹）／霜白甲巨人；侍僧＝银发长耳持血球与匕首，与 Necromancer、Harno 及原生 corruptor（尖帽长杖）不同。评审图 48/64/96 彩色与灰度（含既有相关棋子）、六种真实地板 48px 合成图、`luminance.json` 见 `art/monster-batch-i/review/`，脚本 `make_review_sheets.py`，任务包生成 `make_batches.py`；目录 119→**131** 款；`tests/token_mapping.lua`（5,534 项）新增每款精确正例、无 define_as／非 unique 冒充／借用兄弟图／原生近似体负例；新增 `tests/production/test_monster_batch_i.py`；三份工具批次名单加入 `monster-batch-i`；运行贴图与 `data/token-manifest.json` 最后一步 `prepare_runtime_art.py` 重生成一次（131 项，version 仍为 0.6.26）。门控：纯 Lua 13 脚本、生产测试 129 项、死资产审计和 `git diff --check`（排除 `evidence/`、`handoffs`）通过。自评弱项：crimson ooze 与 red ooze 在 48px 同为红色团块，靠偏粉的色相与浪头形；Z'quikzshl 与 boney experiment 灰度下同为骨色团，靠圆环肋骨拱；Simulacrum 细长、48px 偏小；Burb 与 Bill 灰度同为灰色大块。Norgan 是队友（control=order），需实机确认队员上的棋子行为。均需实机确认。

怪物 Batch H 实机验证（2026-09-29；未提交、未打包）：`run_monster_live_validation.py --batch h` 在隔离夹具 5 场冷启动实机核对 12 个 token id 全部精确匹配、0 `Lua Error`、进程均已停止；9 个自然生成（三沙虫、三水晶、三试验体），poison ivy／honey tree／Necromancer 摆位；48px 下沙虫族与水晶族靠形状可分，Necromancer 可读但偏暗，crimson crystal 与 sanguine experiment 不会出现在同一区域（形状与地面亦不同）；shimmering crystal、orc necromancer 保持原生；Native↔Refined 往返 1 次（Necromancer）通过。见 [实机证据](evidence/monster-live-h-20260929/README.md)。

怪物 Batch H（沙虫三种、水晶三种、毒藤、蜜树、Necromancer、三种试验体；离线美术＋映射，未实机、未提交、未打包；2026-09-29）：12 款均为非唯一身份、精确单图条目（无 unique／native_tall），合同已对照源码重核并钉入 `evidence/monster-batch-h-20260929/source-contracts.json`（沙虫 `sandworm.lua`、burrower `SANDWORM_TUNNELER`、水晶 `crystal.lua`（原生 tint 只是调色，不影响匹配）、`plant.lua`、blighted-ruins 的 `NECROMANCER` 与三试验体；均无 image=/nice_tile，NPC.lua:33 公式图或显式图均在盘上）。shimmering crystal 与 white crystal 原生共用同一 PNG，但名字不同，保持原生；black／blue crystal、sand-drake、tall 沙虫挖掘者、orc necromancer 亦保持原生并有负例。未做：slimy crawler、Burb（本轮优先级与预算）。ImageGen 共 **14/26** 次（每款不超过 2 次）；12 款首轮全部过风格门控（底盘偏移 -6.26…+7.10，半径 0.858–0.860，无豁免、无 PENDING 请求）。Necromancer v1（-3.37）与 sanguine experiment v1（-1.49）虽过门控，但人工看图判为深色主体（袍近黑／血块近黑，遮罩亮度 49.4／34.1，后者低于批 F 被拒稿 39.8），自行淘汰并重生：v2 亮度 66.8／54.3，真实地板 48px 明显可辨（灰度下 sanguine 仍偏暗，靠鲜红色相和高光，列为已知较弱项）。同族区分靠轮廓和明度而非仅色相：沙虫＝细长开放 S 形（最浅）／厚甲闭合圆环／两段橄榄绿拱身加沙堆，另与既有 sandworm-queen 对照；水晶＝高直立花束（最浅）／横向长刃扇／两块粗钝棱柱，另与 Spellblaze 圆形紫簇对照；试验体＝不规则粉褐肉丘带触条／象牙色尖刺骨堆／光滑鲜红血块。评审图 48/64/96 彩色与灰度（含既有相关棋子）、六种真实地板 48px 合成图、`luminance.json` 见 `art/monster-batch-h/review/`，脚本 `make_review_sheets.py`；目录 107→**119** 款；`tests/token_mapping.lua` 新增每款精确正例、篡改高体／借用兄弟图／未知 unique 负例与 tint 例（4,939 项）；新增 `tests/production/test_monster_batch_h.py`；`tools/build_monster_art.py`、`prepare_runtime_art.py`、`check_token_style.py` 批次名单加入 `monster-batch-h`。运行贴图与 `data/token-manifest.json` 只在最后一步 `prepare_runtime_art.py` 重生成一次（119 项，version 仍为 0.6.26）。门控：纯 Lua 13 个脚本通过，生产测试 121 项、死资产审计和 `git diff --check`（排除 `evidence/`、`handoffs`）通过。需实机确认项：Necromancer 与 Harno 同为深色人形、sanguine 与 crimson crystal 同为红色系（形状不同）。

怪物 Batch G 收尾（2026-09-29；未提交、未打包）：评审已批准的 Massok（base_drift -10.32）按 F 先例接入新建可信 `art/production/waivers/monster-batch-g.json`（精确绑定母版 dbd11d12… 与 128px 导出 a31830dd…，重导出逐字节一致）、`check_token_style.py` 批次名单、catalog／selection／`CheckerTokens.lua`（目录 106→**107**，`version` 保持 0.6.25）与测试（原「Massok 未接线」改为正例＋换体负例＋篡改字节使豁免失效）；`run_monster_live_validation.py --batch g` 在隔离夹具 8 场冷启动实机核对 12 个 token id 全部精确匹配、0 `Lua Error`、进程均已停止；Harno、xhaiak 在 48px 可读但偏弱，Pale Drake／The Master 并排可分、48px 主要靠色相与原生光环／冠色而非轮廓。见 [实机证据](evidence/monster-live-g-20260929/README.md)。

怪物 Batch G（离线美术＋映射，未实机、未提交、未打包；2026-09-29）：接续被中断的批次并审计前任遗留（合同抽查 Massok／Pale Drake／The Master／Crystal／Inquisitor／Fillarel 行号与哈希吻合）。ImageGen 共 **22/26** 次（含 Massok 被中断的 1 次），每款不超过 3 次。**11 款上线、无豁免**（目录 95→**106**）：xhaiak arachnomancer、shiaak venomblade（v2，v1 近黑淘汰）、dremling（pale-stone 重绘，掩膜体亮度 39.8→**90.6**）、Pale Drake、The Master（v2）、Fillarel Aldaren、Krogar、Spellblaze Crystal、Rhaloren Inquisitor（v2，越盘返修）、Harno、Lithfengel（v2）；xhaiak／shiaak／dremling 为 `native_tall=true`，Pale Drake／Fillarel／Krogar 为 native-tall 唯一，其余唯一单图。**Massok** 仅 base_drift -10.32（三次已满）→ PENDING（`art/production/waivers/monster-batch-g-PENDING-REQUEST.json`），未接线并有测试锁定；前次 dremling 请求已被第 3 次干净结果取代。新增底盘措辞「同参考亮度、宁略亮不更暗」，重生后偏移 -11～-10 降到 +3～-5，未走亮度修补。xhaiak／shiaak 互借与借 Ungolë 负例、drem 负例保留；`data/token-manifest.json` 重新生成为 **106** 项、`version` 保持 **0.6.25**。自评弱项：Harno（亮度 45.7）、xhaiak 偏暗，Pale Drake／The Master 灰度下同为长袍持杖，靠色相与轮廓区分，需实机复核。门控：纯 Lua 13 脚本（棋子映射 **4,345** 项）、生产测试 **112** 项、dead assets: none、`git diff --check` 干净。见 [评审](art/monster-batch-g/REVIEW.md)、[亮度](art/monster-batch-g/review/luminance.json)、[合同](evidence/monster-batch-g-20260929/source-contracts.json)。

怪物 Batch F 豁免接线＋实机探针＋实机验证（2026-09-29；未提交、未打包）：评审已批准的 shivgoroth／greater shivgoroth（-11.23／-9.40，均仅底盘偏移超限）接入新建 `art/production/waivers/monster-batch-f.json`（精确字节绑定 `monster-batch-f-PENDING-REQUEST.json` 原请求哈希）、`check_token_style.py` 批次名单新增 `monster-batch-f`、`art/monster-batch-f/catalog.json`／`selected-masters.json`／`export-report.json`、`overload/mod/class/CheckerTokens.lua`（目录 93→**95** 款）与新测试；`tools/bin/export_token` 重导出的 48/64/96/128/256px 与请求文件逐字节一致，`data/token-manifest.json` 重新生成为 **95** 项、`version` 保持 **0.6.24**；dremling（评审拒绝，暗底暗色同 Kryl-Feijan 旧图缺陷）未接入。隔离夹具 5 场独立冷启动：xhaiak arachnomancer／shiaak venomblade 按 `native` 探针摆位，实测 `add_mos[1].image` 精确解析为磁盘文件名（非静态分析担心的 `nil`），`rendered_token=false` 确认仍保持原生，settles 该静态分析分歧，本轮未接入目录；naga tidewarden／naga tidecaller／shivgoroth／greater shivgoroth 均自然生成，treant／Kryl-Feijan 摆位，`Tokens.explain` 精确 id 全部匹配、0 `Lua Error`；Native↔Refined 往返 1 次（naga tidecaller）通过；naga tidecaller、greater shivgoroth 与重绘 Kryl-Feijan 在真实地板 48px 下逐张目视确认可读（Kryl-Feijan 相比批 E 旧图明显变亮、不再是纯黑团块）。四项门控全过（纯 Lua 13 脚本、棋子映射 **3,896** 项；生产测试 **104** 项；dead assets: none；`git diff --check` 干净）；全部 5 场夹具进程按场次结束即停止，复核无残留。见 [Part 1 评审](art/monster-batch-f/REVIEW.md) 与 [实机证据](evidence/monster-live-f-20260929/README.md)。

怪物 Batch F（`CONTRACTS-B5-B7-20260929.md` 4.1「需要合同扩展」8 款 + Kryl-Feijan 重绘，离线美术，未实机、未提交、未打包）：8 款中 dremling／shivgoroth／greater shivgoroth／naga tidewarden／naga tidecaller／treant 6 款源码逐字面核对（含 drem/dremling 文件名对调陷阱：dremling 真实贴图是 `npc/horror_corrupted_drem.png`，不是同名的 `dremling.png`）确认为 `native_tall=true` 精确目录条目；xhaiak arachnomancer／shiaak venomblade 用 `resolvers.nice_tile{tall=1}` 简写，本轮沿 `engine/Zone.lua:633`（`Zone:finishEntity` 在 NPC.lua 默认命名回填**之前**对未实例化的克隆调用 `resolve()`）追踪一层，得出其 `add_mos` 图片在 resolve 时刻很可能解析为 `nil`（与原调查仅凭磁盘文件名吻合的推断相反），静态读码无法证实，按任务要求保持原生不接入，见 `evidence/monster-batch-f-20260929/source-contracts.json`。出图（预算 20 次，单款≤3，实占 **13 次**）：naga tidewarden／naga tidecaller／treant 首稿即因圆盘越界被拒，各一次定向返修后干净通过（各 2 次，无需豁免）；dremling／shivgoroth／greater shivgoroth 首稿仅底盘偏移单项超限（-8.94／-11.23／-9.40，容差 ±8，其余四项全过），按批 E 先例记入 `art/production/waivers/monster-batch-f-PENDING-REQUEST.json`（已标「reviewer approval requested」，未接入门控/目录/清单，保持原生，各 1 次）。Kryl-Feijan（批 E 已用豁免上线，`evidence/monster-live-e-20260929` 实机 48px 深灰石板地几乎读作纯黑团块）重绘三稿：v1／-b 均维持"中性色底盘"未改暗但**实测主体遮罩区域平均亮度分别为 59.3／59.0，与旧图统计不可分**（门控通过≠视觉变亮，均判为不合格弃用）；第三稿明确要求"苍白风暴灰"取代"炭黑/暗紫灰"措辞后，平均亮度升至 **85.4（+44%）**，`base_drift` -8.00 干净通过，替换旧图并撤销批 E 对应豁免条目（`art/production/waivers/monster-batch-e.json` 移除 kryl-feijan，`tests/production/test_monster_batch_e_waivers.py` 改为验证「已撤销」）。48/64/96 彩色＋灰度同族对比表及 48px 真实深色地板（`gloom`／`korpul` 石板）合成表见 `art/monster-batch-f/review/`（含 Kryl-Feijan 新旧三稿并列，亮度差异肉眼可辨）。接入 `overload/mod/class/CheckerTokens.lua`（目录 90→**93** 款：naga-tidewarden／naga-tidecaller／treant／Kryl-Feijan 重绘），`tests/token_mapping.lua` 新增 drem/dremling 防混淆负例、批内跨身份禁止借用正反例，移除原「treant 未收录」负例；`tools/build_monster_art.py`／`prepare_runtime_art.py` 批次名单接入 `monster-batch-f`，`data/token-manifest.json` 重新生成为 **93** 项、`version` 保持 **0.6.24**。四项门控全过（纯 Lua 12 脚本、棋子映射 **3,816** 项；生产测试 **100** 项；dead assets: none；`git diff --check` 干净）。

怪物 Batch E 豁免接线＋12 首领实机验证（2026-09-29；未提交、未打包）：评审已批准的 7 款底盘偏移豁免（Urkis、Golbug、Ungolë、Half-Finished Bone Giant、Kryl-Feijan、Atamathon、Ritch Great Hive Mother）按 batch D 先例接入 `art/production/waivers/monster-batch-e.json`（精确字节绑定原请求）、`check_token_style.py` 批次名单、`art/monster-batch-e/catalog.json`／`selected-masters.json`、`overload/mod/class/CheckerTokens.lua`（目录 83→**90** 款）与新测试 `tests/production/test_monster_batch_e_waivers.py`；`tools/build_monster_art.py --batch monster-batch-e`／`tools/prepare_runtime_art.py` 重建后 7 款 128px 运行导出的 SHA256 与请求文件逐字节一致，`data/token-manifest.json` 重新生成为 **90** 项、`version` 保持 **0.6.24**。隔离夹具 11 场独立冷启动覆盖全部 12 名首领（8 款自然生成、4 款为多步任务脚本触发的首领改按区域 `npc_list` 摆位并标注），`Tokens.explain` 精确 id 全部匹配、0 `Lua Error`；Native↔Refined 往返 1 次通过；Atamathon 的 `nicer_tiles` 关闭原生回退路径实机复现确认（非仅静态推断）；Ungolë 在真实深绿地板 48px 下保持可读，Kryl-Feijan 在真实深灰石板地 48px 下可读性明显弱于离线评审单（依赖红圈与地板火光定位，美术自身轮廓几乎读作纯黑团块），记为已知限制、未达豁免撤销门槛。四项门控全过（纯 Lua 12 脚本、棋子映射 3,687 项；生产测试 95 项；dead assets: none；`git diff --check` 干净）。见 [Part 1 评审](art/monster-batch-e/REVIEW.md) 与 [实机证据](evidence/monster-live-e-20260929/README.md)。

怪物 Batch E（12 个地城终层首领，离线美术，未实机、未提交、未打包）：目标为 `docs/expansion-plan-20260928/CONTRACTS-B5-B7-20260929.md` §2 推荐的下一批——批次 6 全部 12 名区域门面首领。先对 12 条合同逐一重新核对源码 file:line／`define_as`／`type`／`subtype`／`unique`／`invis.png`+`add_mos{display_h=2,display_y=-1}` 显示结构，并目视核对全部 12 张原生贴图（`evidence/monster-batch-e-20260929/source-contracts.json`），与既有调查结论完全一致，未发现出入；Atamathon 按调查文档记录的例外，只接入已验证的 tall 体合同，`nicer_tiles` 关闭时的 `npc/atamathon.png` 单图回退按文档保持原生、不臆造。底盘构图复用 batch D-4 校准过的底盘偏暗提示词起步（先试「暗 8 单位」，后改「暗 4 单位」），但本批新家族的实测偏移波动明显大于蚂蚁族（-5~-15 不等），证明该提示词只能降低风险、不能保证达标。预算 24 次、单款上限 3 次，实占 **17 次**：Lady Zoisla 因首稿三叉戟／尾冠双双出环，改用全新（非编辑）第三次生成收紧构图后干净通过（3 次）；Brotoq／The Abomination 各自一次定向返修修正圆盘越界后通过（2 次）；The Mouth／Celia 首稿即过（1 次）；Urkis／Golbug／Ungolë／Half-Finished Bone Giant／Kryl-Feijan／Atamathon／Ritch Great Hive Mother 七款仅底盘偏移单项超限（-9.47～-15.18，容差 ±8），其余四项（母版 alpha／圆盘越界／四角透明／占格）全部通过；两次尝试提亮返修（zoisla 攻击性返修与 ungolë）均把「亮 9 左右」的定向修正过冲到 +44～+53，证实编辑类返修在本批不可靠，故这七款不再消耗第二次调用，直接按「仅底盘偏移失败」记入 `art/production/waivers/monster-batch-e-PENDING-REQUEST.json`（精确字节匹配、已标注「reviewer approval requested」，未接入门控/目录/清单，等待用户裁决），期间保持原生。
5 款已通过（Lady Zoisla、Brotoq、The Mouth、The Abomination、Celia）接入 `overload/mod/class/CheckerTokens.lua`（目录 78→**83** 款）；`tests/token_mapping.lua` 的通用目录循环已对每个 `unique=true` 条目自动生成「精确身份匹配」正例与「篡改 tall 体」负例，无需额外手写（与 batch A/B 先例一致），**3,407** 项全过。horror/corrupted 家族三款（既有 Horned Horror／新 The Mouth／新 The Abomination）48/64/96 彩色与灰度审图轮廓互不相似；Urkis 的青白闪电光环与 Celia 的暗淡长袍在同一 humanoid/human 家族内轮廓、明度双重区分；Golbug（金饰兽角肩甲、剑平持）与 Brotoq（近黑全甲、尖盔、剑上举）在待裁决 humanoid/orc 家族内同样可分；其余 5 个新家族（naga／spiderkin／undead-giant／demon-major／construct-golem／insect-ritch）目录内暂无同族先例，逐一确认 48px 单独可读。审图表在 `art/monster-batch-e/review/`（9 组 × 彩色/灰度 = 18 张）。
`tools/build_monster_art.py --batch monster-batch-e`／`tools/prepare_runtime_art.py` 的批次名单已加入 `monster-batch-e`；`data/token-manifest.json` 重新生成为 **83** 项，`version` 保持 **0.6.24** 不变，按要求只跑一次 `prepare_runtime_art.py` 作为收尾步骤。四项门控全过：纯 Lua 13 脚本（棋子映射 3,407 项、其余脚本合计不变）、生产测试 `unittest discover -s tests/production` 87 项、`tools/audit_dead_assets.py --check`（dead assets: none）、`git diff --check`（排除 `evidence/`、`art/production/handoffs/`）。未启动游戏、未提交、未打包。详见 `art/monster-batch-e/REVIEW.md`。

怪物 Batch D 实机验证（2026-09-29）：隔离夹具 2 场独立冷启动（Old Forest DEFAULT L4、Trollmire FLOODED L1）对红／蓝果冻怪与六色巨蚁逐一核实 `Tokens.explain` 精确 id（yellow ant 自然生成，其余摆位并标注），六蚁排／六胶排 48/64/96 与一次 Native↔Refined 往返均通过、0 `Lua Error`；green ooze／crimson ooze／gelatinous cube／Malevolent Dimensional Jelly 四款确认保持原生、无棋子。48px 下 carpenter／black 巨蚁仍是全库最弱一对，实机环境比离线评审单更难分辨，列为已知限制。见 [实机证据](evidence/monster-live-d-20260929/README.md)。

## 当前交付：0.6.27 —— 怪物 Batch H／I 与 native-tall 光环修复发布（2026-09-29；按本任务要求不提交）

- 纳入已提交的怪物 Batch H（`1a476f1`/`f5f01d6`）、Batch I（`d118b15`/`33ac5a2`）与 `32f4ec5`（`nativeTallImage` 忽略 `_isshaderaura` 光环条目，修复 Harkor'Zun 开关往返后回退原生）。主插件版本、棋子清单版本、README、CHANGELOG、外测安装指南（新建 `docs/external-test-v0627/`）同步至 0.6.27；棋子目录 107→**131** 款。
- 正式 TEAA 安装至隔离离线夹具，shader 开启、1920×1080、64px，五场景各自独立冷启动：Sandworm Lair L4（sandworm destroyer 摆位、green ooze 自然）、Scintillating Caves L5（Spellblaze Simulacrum 摆位、white crystal 自然）、Blighted Ruins L2（Necromancer 摆位、fleshy experiment 自然）、Tempest Peak L1（Harkor'Zun 摆位，含一次 Native→Refined 开关，关闭后 `still_mapped=0`，重开后仍为 `harkor-zun`）、Deep Bellow L3（slimy crawler 摆位）。**6,548／6,548** 受支持格绘制，原生回退 0，8 个 token id 精确匹配，0 `Lua Error`；进程按场次停止。证据见 [0.6.27 冒烟](evidence/runtime-v0627/README.md)。
- 纯 Lua **13** 个独立脚本通过；生产测试 **129** 项、死资产审计（dead assets: none）和 `git diff --check`（排除 `evidence/`、`handoffs`）通过。TEAA **1,473** 个成员逐字节匹配源码，**1,450** 张 PNG 全为 ZIP_STORED；外测 ZIP 白名单、byte-identity 与 SHA256SUMS 通过。TEAA SHA256 `ce567eb397c84bd14bda1ccfc50d5a323360551d11db73c64e6bd585a6f8d7be`；外测 ZIP SHA256 `96b2ebbb043a3b1d80b689b523f40adcfecd83b19452bf8cbe298a22a2693709`；HUD 0.2.7 TEAA 未重建（HUD 仓库自上一版仅有文档提交）。
- 已知限制：crimson ooze／red ooze 48px 同为红团，Harkor'Zun 碎片与 Burb 深底深主体 48px 偏暗，Simulacrum 48px 偏小；其余沿 0.6.26。本轮为归档安装和暂停夹具场景，未验证完整战役跨进程读档、自然连续战斗或其他游戏版本。

## 当前交付：0.6.26 —— 怪物 Batch G 发布（2026-09-29；按本任务要求不提交）

- 纳入已提交的怪物 Batch G（`7abe2cf`/`bf4ba5c`）。主插件版本、棋子清单版本、README、CHANGELOG、外测安装指南（新建 `docs/external-test-v0626/`）同步至 0.6.26；棋子目录 95→**107** 款：xhaiak arachnomancer、shiaak venomblade、dremling、Massok（经评审批准的底盘偏移豁免）、The Master、Pale Drake、Spellblaze Crystal、Rhaloren Inquisitor、Krogar、Fillarel Aldaren、Harno、Lithfengel。**本轮无新增地形。** 因测试 `tests/production/test_monster_batch_g.py` 硬编码清单版本，仅将其期望值由 0.6.25 改为 0.6.26（无其他测试／逻辑改动）。
- 正式 TEAA 安装至隔离离线夹具，shader 开启、1920×1080、64px，六场景各自独立冷启动：Dreadfell L9（The Master 自然，Pale Drake 摆位）、Unremarkable Cave L1（Krogar、Fillarel Aldaren 均自然）、Ardhungol L3（xhaiak／shiaak 均摆位）、Daikara DEFAULT L4（Massok 摆位）、Reknor L4（Harno／Lithfengel 均摆位）、Scintillating Caves L5（Spellblaze Crystal 自然）：受支持格 **13,344／13,344** 绘制，原生回退 **0**；10 个身份的 `Tokens.explain` 精确 id 全部匹配，0 `Lua Error`。dremling／Rhaloren Inquisitor 不在本轮指定场景内，沿用 Batch G 实机证据。见 [0.6.26 证据](evidence/runtime-v0626/README.md)。
- 纯 Lua **13** 个独立脚本通过（地形合同 **848**、修复 **53**、棋子映射 **4,388** 项、107 款身份）；生产测试 **113** 项、死资产审计（dead assets: none）和 `git diff --check`（排除 `evidence/`）通过。TEAA **1,449** 个成员逐字节匹配源码，**1,426** 张 PNG 全为 ZIP_STORED；外测 ZIP 白名单、byte-identity 与 SHA256SUMS 通过。TEAA SHA256 `104f21bce9b6423522e7e38a79fe1c053d71a83547bb1a0f3134f1c641d0d586`；外测 ZIP SHA256 `5933ff2b2856ad1904ba18cedf518f337064dda147addbb8520741d446b755ab`。HUD 无运行时改动（`../tome-board-hud` 最新提交仍为 `bc7f69f` 文档提交），沿用 0.2.7 包 `4592696e1dd6b8ec3c72eff8a5062b19b536e50a6a9c833e5d5f0c78b8675bb1`，未重建。
- 已知限制：Harno、xhaiak arachnomancer 为深色主体，48px 下偏弱但可读；Pale Drake 与 The Master 在 48px 下主要靠色相与原生光环／冠色区分；其余限制沿 0.6.25（carpenter／black 巨蚁等）。本轮为归档安装和暂停夹具场景，未验证完整战役跨进程读档、自然连续战斗或其他游戏版本。全部 6 场夹具进程按场次结束即停止（`alive_after_stop=[]`，X socket 已消失）。

## 当前交付：0.6.25 —— 怪物 Batch D／E／F 发布（2026-09-29；按本任务要求不提交）

- 纳入已提交的怪物 Batch D（`2caaade`/`13e04b2`/`05f3a25`）、Batch E（`a3e6fc7`/`b536d68`/`a5a7420`）、Batch F（`6965a17`/`d90c791`/`a0fda3d`）。主插件版本、棋子清单版本、README、CHANGELOG、外测安装指南（新建 `docs/external-test-v0625/`）同步至 0.6.25；棋子目录 70→**95** 款：red/blue jelly 补齐六色果冻族，六色巨蚁全部上线（brown/blue ant 经豁免、carpenter/black ant 重新设计），12 个地城终层首领全部接入（7 款经豁免），naga tidewarden／tidecaller、treant 直接过审，shivgoroth／greater shivgoroth 经豁免接入，Kryl-Feijan 重绘（亮度 +44%，撤销原豁免）。**本轮无新增地形**，地形覆盖区域与 0.6.24 相同。
- 正式 TEAA 安装至隔离离线夹具，shader 开启、1920×1080、64px，八场景各自独立冷启动：Old Forest DEFAULT L4（六色巨蚁，white/blue 自然生成、brown/carpenter/yellow/black 摆位）、Trollmire FLOODED L1（red/blue jelly，均按设计直接摆位）、Reknor L4（Golbug the Destroyer，自然）、Slazish Fen L3（naga tidewarden／tidecaller，均自然）、Norgos Lair INVADED L3（shivgoroth／greater shivgoroth，均自然）、Deep Bellow L3（The Mouth，自然）、Last Hope Graveyard L2（Celia，自然）、Tempest Peak L2（Urkis, the High Tempest，自然）：受支持格 **18,652／18,652** 绘制，原生回退 **0**；16 个身份的 `Tokens.explain` 精确 id 全部匹配预期（`giant-white-ant`／`giant-brown-ant`／`giant-carpenter-ant`／`giant-blue-ant`／`giant-yellow-ant`／`giant-black-ant`／`red-jelly`／`blue-jelly`／`golbug`／`naga-tidewarden`／`naga-tidecaller`／`shivgoroth`／`greater-shivgoroth`／`the-mouth`／`celia`／`urkis`），8 场 `game.log` 均无 `Lua Error`，全部截图逐张目视核对可读。见 [0.6.25 实机证据](evidence/runtime-v0625/README.md)。
- 纯 Lua **13** 个独立脚本通过（地形合同 **848**、修复 **53**、棋子映射 **3,896** 项、95 款身份）；生产测试 **104** 项、死资产审计（dead assets: none）和 `git diff --check`（排除 `evidence/`）通过。TEAA **1,437** 个成员逐字节匹配源码，**1,414** 张 PNG 全为 ZIP_STORED；外测 ZIP 白名单（仅 `init.lua`／`COPYING`／`data`／`hooks`／`overload`／`superload`）、byte-identity 与 SHA256SUMS 均通过。TEAA SHA256 `cf2e689c1bfb1e1869493156abcae040140d3b84eae21218ca1f3170e5345323`；外测 ZIP SHA256 `ae4b9c29257e9b85177d03ed002d24300b359e6e427ed28f177c0712517ab250`。HUD 自 0.6.23 起无运行时改动（`../tome-board-hud` 最新提交仍为 `bc7f69f` 文档提交），仍沿用 0.2.7 包 `4592696e1dd6b8ec3c72eff8a5062b19b536e50a6a9c833e5d5f0c78b8675bb1`，未重建。
- 已知限制：48px 下 carpenter／black 巨蚁仍是全库可分性最弱的一对（0.6.24 已记录，未变）；Ungolë、Kryl-Feijan（重绘前）在深色地板 48px 下可读性偏弱的记录见 0.6.24 及 batch E/F 各自实机证据，Kryl-Feijan 本轮已重绘改善。reknor、tempest-peak 两个区域此前未收到地形请求，本轮 census 显示其常规石质/岩地格已由既有 REKNOR／daikara 岩石适配器覆盖（非本轮改动，如实记录）。本轮为归档安装和暂停夹具场景，未验证完整战役跨进程读档、自然连续战斗或其他游戏版本。全部 8 场夹具进程按场次结束即停止，复核无残留（`alive_after_stop=[]`，X socket 已消失）。

## 当前交付：0.6.24 —— 怪物 Batch C／地形批次 4／地形批次 5／拉克·肖部落发布（2026-09-29；按本任务要求不提交）

- 纳入已提交的怪物 Batch C（`533341a`）、地形批次 4（`688f3eb`，视觉返工 `87a35e4`）、地形批次 5（`fdaee0f`）、兽人育种棚返工与拉克·肖部落骨质地形（`7fb72f9`）。主插件版本、棋子清单版本、README、CHANGELOG、外测安装指南（新建 `docs/external-test-v0624/`）同步至 0.6.24；棋子目录 **70** 款（新增 skeleton master archer）。
- **范围变更（协调方本轮确认）**：Orc Breeding Pit（兽人育种棚）在当前游戏版本中无可达入口，已不可进入。已从本轮冒烟场景、Game Options 棋盘地形说明（`hooks/load.lua` 英文 `_t` 原键与 `data/locales/zh_hans.lua`／`zh_hant.lua` 两个 locale 条目三方逐字节核对一致）、CHANGELOG、README 及外测指南的覆盖声明中移除；仅在限制说明处提及其地形代码（L1 石质复用、L2–L3 `gloom/pit` 返工）仍保留在源码中但处于休眠状态，不作为已验证覆盖范围。CheckerTerrain/CheckerTokens 门控代码与美术资产本身未改动。
- 正式 TEAA 安装至隔离离线夹具，shader 开启、1920×1080、64px，Keepsake Meadow L1、Conclave Vault L1、Noxious Caldera L2、South Beach L1、Murgol Lair L1、Sher'Tul Fortress L1、Charred Scar L1、Rak'Shor Pride L1、Ruins of Telmur L1、Dreadfell L1 各自冷启动：受支持格 **23,121／23,121** 绘制，原生回退 **0**；Dreadfell L1 的 skeleton master archer 与 skeleton archer 均**自然**生成，分别绘制 `skeleton-master-archer`／`skeleton-archer`（冒烟脚本另备 `natural_or_place` 摆位回退，本轮未触发）。英文、简体、繁体 Game Options 另各自冷启动（已移除 Orc breeding pits 文案后重新采集）。见 [0.6.24 实机证据](evidence/runtime-v0624/README.md)。
- 纯 Lua **13** 个独立脚本通过（地形合同 **848**、修复 **53**、模式 **186**、棋子映射 **2,895** 项）；生产测试 **84** 项、死资产审计和 `git diff --check` 通过。TEAA **1,412** 个成员逐字节匹配源码，**1,389** 张 PNG 全为 ZIP_STORED；外测 ZIP 四项和 SHA256SUMS 均通过。TEAA SHA256 `aba76d99d5beae7fa7c12702c030bc2ecc02159e2a6f25198f209f9d69c76784`；外测 ZIP SHA256 `42b8970cc40385950aea67982b3d204a106bd23da9dee81caac999927b1e7ce7`。HUD 自 0.6.23 起无运行时改动（仅 AGENTS.md 文档提交 `bc7f69f`），仍沿用 0.2.7 包 `4592696e1dd6b8ec3c72eff8a5062b19b536e50a6a9c833e5d5f0c78b8675bb1`，未重建。
- 已知限制：Sher'Tul Fortress 实机 census 显示复用 `OLD_WALL*` 石质适配器（`stone`／`forest` 合计 3,570 格），与源码提交信息中"仅 SOLID_FLOOR/SOLID_WALL\*"的早期描述不完全一致，以实机 census 为准；混沌之沼／时空裂隙原生天气云、Horned Horror／skeleton archer 48px 可分性等 0.6.23 已记录限制持续未变。本轮为归档安装和暂停夹具场景，未验证完整战役跨进程读档、自然连续战斗或其他游戏版本。

## 当前交付：0.6.23 —— 虚空／纳尔湖水下／墓园地物与怪物 Batch A／B 发布（2026-09-29；按本任务要求不提交）

- 纳入已提交的虚空／时空地形（`c19e080`）、T5（`850ba0e`）、虚空墙返工与墓园地物（`b2a22e2`）、怪物 Batch A（`7e5cd52`）／B（`f8ba3d8`）及其实机验证（`eb2b416`）。主插件版本、棋子清单版本、README、CHANGELOG、外测安装指南同步至 0.6.23；棋子目录 **69** 款。Game Options 地形说明已含新增区域，英文原键与简繁精确键一致，本轮未改文案。
- 正式 TEAA 安装至隔离离线夹具，shader 开启、1920×1080、64px，混沌之沼 L1、次元浮岛 L1、时空裂隙 L1、纳尔湖 DEFAULT L2、最后的希望墓地 L1／L2、Trollmire FLOODED L3、Norgos Lair DEFAULT L3 各自冷启动：受支持格 **15,679／15,679** 绘制，原生回退 **0**；墓碑 44／44、墓堂入口 1／1、棺材 12／12 采用棋盘图；自然生成的 Shax、electric eel、Norgos the Guardian 分别绘制 `shax`／`electric-eel`／`norgos-guardian`。英文、简体、繁体 Game Options 另各自冷启动。见 [0.6.23 实机证据](evidence/runtime-v0623/README.md)。
- 纯 Lua **13** 个独立脚本通过（地形合同 **680**、修复 **53**、模式 **185**、棋子映射 **2,853** 项）；生产测试 **71** 项、死资产审计和 `git diff --check` 通过。TEAA **1,132** 个成员逐字节匹配源码，**1,110** 张 PNG 全为 ZIP_STORED；外测 ZIP 四项和 SHA256SUMS 均通过。TEAA SHA256 `57d36db273e659a3c7a0e6f09c545357c4678642b9a7d8c4321e4d59316d1fe5`；外测 ZIP SHA256 `fe3265efcebd262ea1d710f0734303df057983c0ce2caf52f31a1bcbfdf2a799`。HUD 无运行时改动，仍为 0.2.7。
- 已知限制：混沌之沼／时空裂隙的原生天气云仍画出暗色方块（原生行为，未改）；Horned Horror 偏暗且 48px 下近似 Minotaur；skeleton archer 与 degenerated skeleton archer 48px 几乎难分；skeleton master archer 与五款 E2 亡灵仍原生。本轮为归档安装和暂停夹具场景，未验证完整战役跨进程读档、自然连续战斗或其他游戏版本。

## 兽人育种棚 L2–L3 可读性返工＋拉克·肖部落骨质地形（2026-09-29；未提交、未升版、未打包）

- 育种棚 L2–L3：旧图地板暗奇偶格与带纹理暗墙混成一片。`art/terrain-batch5-v1/export.py` 改导本区专属 `gloom/pit/*`：平静浅苔灰地板、近均匀暗泥炭墙（北顶线、侧影、南侧暗立面带保留菌柄纹）、梯子重落新地板；无尽深渊不变。各一次冷启动 2,491／2,491、216／216 绘制、回退 0，自然 FOV 地板／阻挡差 46.8%→**71.2%**、57.6%→**70.7%**；旧截图移入 `evidence/batch5-20260929/screenshots/pre-rework/`（L3 本次 15×15 图无记忆测试点）。
- 拉克·肖部落 L1–L3：`bone.lua` 加载时记录定义函数表，仅“定义无回调且格子仍无回调”的 `BONEFLOOR`、`BONEWALL*`/`HARDBONEWALL*`、普通骨门（开／关）、梯子与世界出口接入新 `rakshor` 组；杠杆、杠杆门、封印宝库门、事件光环格与隐藏宝库入口保持原生。0 次 ImageGen，`art/terrain-rakshor-v1/export.py` 由沙虫沙地母版与原生骨墙／门／楼梯重着色导出 46 张，奇偶最小 14.19%。3 次冷启动 5,785／5,785 绘制、回退 0，地板／阻挡差 72.0%–78.6%，往返、规则快照、挖掘、48/64/96、记忆、出口与简繁英选项（精确键，“拉克·肖部落”）均留证。限制：原生事件格在棋盘中明显跳色。地形合同 848 项、生产测试 84 项。见 `evidence/rakshor-20260929/README.md`。

## 第五批地形：30 级巢穴、夏·图尔堡垒、精灵废墟（2026-09-29；未提交、未升版、未打包）

- 接入 11 个地城 24 层：泰尔玛废墟 L1–5、精灵废墟 L1–3、沃尔军械库 L1–2、兽人育种棚 L1（石质）复用卡·普尔石组；布莱亚弗巢穴沙组；隐秘山谷山洞洞穴组（另加 `UP_VALLEY` 精确出口）；淹没的洞穴、造物者神庙水下组；育种棚 L2–3 plain 地下组（墙换较暗副本）；灼烧之痕、恶魔空间的无害熔岩地／熔岩池／新熔岩岩墙；夏·图尔堡垒仅 `SOLID_FLOOR`／`SOLID_WALL*` 与外围石墙，控制球、传送门、壁画、封门、改写楼梯保持原生。幻境城堡在全部源码中无入口，跳过；拉克肖荣耀需新骨质族与逐回调合同，列为剩余。沃尔 L2 带伤害熔岩、深水及其描边地板、各区随机事件格保持原生。
- 0 次 ImageGen：`art/terrain-batch5-v1/export.py` 由岱卡拉岩体、卡·普尔石纹、原生堡垒面板缝和 plain 菌墙确定性导出 98 张图，奇偶最小 11.35%。隔离夹具 shader、1920×1080，24 次独立冷启动 59,546／59,546 支持格绘制、回退 0，往返与规则快照一致，挖掘修复、48/64/96、自然 FOV、记忆、出口与简繁英选项均留证；非石质组自然 FOV 地板／阻挡差 24.9%–66.0%（恶魔空间墙亮 38.6%），卡·普尔石组墙亮 4–21%（沿用已发布石组）。地形合同 790 项、生产测试 79 项、死资产审计通过。详见 `evidence/batch5-20260929/README.md`。

## 怪物 Batch C 实机验证（2026-09-29；未提交）

- 隔离离线夹具、shader、1920×1080，5 场独立冷启动（`tools/run_monster_live_validation.py --batch c`），每场停止本场游戏与 Xvfb，均无 `Lua Error`。skeleton master archer 在 Dreadfell L1 **自然**生成并绘制 `skeleton-master-archer`（48/64/96）；另一场随机池未出时按 npc_list 摆位并标注；Unremarkable Cave L1 本次未出。重绘的 skeleton archer 自然绘制；Maze COLLAPSED L4 自然 Horned Horror 与 Maze DEFAULT L2 Minotaur 各 48/64/96；skeleton magus 自然 4 名＋摆位 1 名全部保持原生。两次 Native↔Refined 往返通过。
- 审图：首领冠标在环外右上，触手冠在环内，不相撞；Horror（灰紫＋洋红触手＋青白拳）与 Minotaur（棕＋斧）三尺寸均可分，48px 靠色块；master archer 实机读作暗铜金甲，与白骨弓手明显不同；archer 与 degenerated 64px 可分、48px 仍需细看；armoured／普通 skeleton warrior 仍偏弱（未改）。`tests/live_monster_batch.lua` 的 `approach` 改为依次尝试同名自然演员。见 [实机证据](evidence/monster-live-c-20260929/README.md)。

## Batch 4 视觉返工：剧毒火山毒水／丛林树、南方海滩树／沙（2026-09-29；未提交、未升版、未打包）

- 源码＋截图核对：火山 L2 大片橙褐杂色区是本插件的毒水图（细碎波纹在原生暖色 `color_shown` 与橙色蒸汽下成噪点），不是原生的熔岩疤痕／枯萎土中心；后两者是带事件 `on_stand` 闭包、刻意突出的单格事件地物，继续原生。毒水改为平静暗绿浑水（浮点环绕模糊），丛林树改用既有 F1 硬木／垂柳母版重着色、满格；海滩 `TREE#` 新增满格 `beach/tree-*`（Trollmire 共用的小图标树未动），海滩专用沙降饱和／对比，阳伞／篮子换新沙底。
- 0 次 ImageGen，exporter 126 张、63 对奇偶最小 11.34%（改动图 14.43%）；火山 L2／海滩各一次独立冷启动：4,897／4,897 与 399／399 绘制、回退 0，自然 FOV 地板／阻挡差 47.4%／38.9%（首轮 39.0%／31.2%），往返、规则快照、挖掘及 48/64/96／记忆截图重拍，旧图移入 `screenshots/pre-rework/`。地形合同 725 项、生产测试 75 项。见 `evidence/batch4-20260929/README.md` “视觉返工”节。

## Batch 4 地形：穆格尔巢穴／南方海滩／宁静的草原／孔克雷夫实验室／剧毒火山（2026-09-29；未提交、未升版、未打包）

五个区域全部接入棋盘地形，只按源码戳＋身份＋显示层＋规则精确匹配：穆格尔 DEFAULT／INVASION L1–L3 复用水下套件并新增世界出口；海滩沙地、深海、草地、树、石路、阳伞／篮子；草原 L1–L6 硬树、草花、深水、出口、炖锅，剧情触发草地／洞穴地板仅在 `on_move` 文件行号一致时替换显示；孔克雷夫 Kor'Pul 变体含区域墙、装饰地板（保留原生装饰层）及光环墙，墙改为单独门控的冷灰砖墙（原墙亮于地板，已返工）；火山丛林地、满格暗丛林树、毒水（伤害／攻击回调文件行号锁定）、岩墙与出口。空气泡、带检查的海滩出口、洞门、路牌、平地出口、祭坛、熔岩疤痕中心等保持原生。0 次 ImageGen，118 张图由 `art/terrain-batch4-v1/export.py` 确定性导出，奇偶最小 11.34%。19 次独立冷启动 36,305／36,305 绘制、0 回退，自然 FOV 地板／阻挡差 23.8%–68.4%，模式往返、规则快照、挖掘修复、48／64／96px 及记忆截图、简繁英选项均核验；地形合同 724 项、生产测试 75 项通过。详见 `evidence/batch4-20260929/README.md`。

## T5 纳尔湖水下与静态地物（2026-09-29；已提交 `850ba0e`／`b2a22e2`，纳入 0.6.23）

2026-09-29 Monster batch D 豁免接入＋carpenter／black ant 重绘（离线美术，未实机、未提交）：brown／blue ant 按评审批准的逐字节豁免（`art/production/waivers/monster-batch-d.json`，基准 `monster-batch-b.json` 格式）接入 `check_token_style.py`／CheckerTokens.lua／棋子清单，目录 76→78 款前的 76 款。carpenter／black ant 原稿（48px 几乎无法区分）未纳入豁免；改按原生 `ant.lua`／`carpenter_ant.png`／`black_ant.png` 重新设计——carpenter 给出象牙灰巨颚（与头部形成明度反差）＋前倾快速站姿，black 给出低伏姿态＋颚色与头部同色（零反差），预算 6 次 ImageGen（每款 3 次）：首轮均只差底盘偏移（+12.14／+12.27）；指标驱动返修按测量值自动加压又双双过冲（−18.90／−20.07）；第三轮按前两轮实测值校准、显式要求底盘小幅（约 8 单位）偏暗，两款干净通过（−7.27／−5.43，容差 ±8，无需豁免）。48/64/96 彩色／灰度审图：新图中 carpenter 的亮色巨颚在三档尺寸、彩色与灰度下均清晰可辨，与 black 的纯暗色轮廓不再混淆；旧稿对比图确认原拒收判断成立。目录 78 款，纯 Lua 13 脚本（棋子映射 3,207 项）与生产测试 84 项通过，棋子清单版本不变（0.6.24）。见 `art/monster-batch-d/REVIEW.md`「Waiver integration + carpenter/black redraw」节。

2026-09-29 Monster batch D（离线美术，未实机）：新增 red jelly、blue jelly（胶质六色补齐）与 giant white ant、giant yellow ant，目录 74 款，全部原门限通过。ImageGen 13/16 次。brown／blue ant 仅底盘明度小幅超限（+8.39／+8.45），评审原则同意豁免、待后续接入；carpenter／black ant 在 48px 几乎无法区分，拒收并保持原生。green／crimson ooze、gelatinous cube、Malevolent Dimensional Jelly 缺可核实的原生图像，四种 Rhaloren 精灵为随机装备纸娃娃，均保持原生。见 `art/monster-batch-d/REVIEW.md`。

2026-09-29 Monster batch C（离线美术，533341a；实机待验）：按实机复核重画三款 48px 易混棋子，ImageGen 4/8 次，全部原门限通过、无豁免。skeleton master archer 以黑漆金边重甲接入精确映射；skeleton archer 改为正面直立持金弓，与蹲姿 degenerated archer 区分；Horned Horror 改为浅色身体、品红触手冠与闪电拳套，与牛头人分开。目录 70 款；batch B 的 horned-horror 豁免已随旧字节失效。待实机：Dreadfell／Unremarkable Cave 骷髅阵列、Maze COLLAPSED L4 Horned Horror（含首领冠标位置）。见 `art/monster-batch-c/REVIEW.md`。

2026-09-29 虚空返工与墓园地物（未打包）：混沌之沼／时空裂隙 L1 的硬边暗方块经 Refined／Vanilla × 天气开关四组同位对照，确认来自原生天气粒子（关闭 `weather_effects` 后两种模式同时消失），插件未改原生天气。虚空墙仅改 exporter 重导为平静、铺满格的裂隙体，Abashed 焦树随浮岩重导；34 对虚空奇偶最低 16.31%，三 L1 自然光地板／阻挡差 80.20%／91.29%／83.08%，支持格 6,497／6,497、回退 0。最后的希望墓地新增墓碑、封闭棺、开启棺、墓堂入口四款 exporter-only 图，实机 L1 44/44 墓碑与 1/1 入口、L2 12/12 棺材采用新图，回调与规则字段前后逐一相同；0 次 ImageGen、无门限或豁免。680＋53＋180 项 Lua 与 71 项生产测试通过。见 `evidence/void-20260928/README.md` 与 `evidence/graveyard-props-20260929/README.md`。

2026-09-29 T5 未打包源码迭代：纳尔湖 DEFAULT／FLOODED L1 的普通地表水墙／门／沙地、L2 与 FLOODED L3 的普通水下格接入棋盘图，DEFAULT L3 普通石质格复用既有套件；同图的时空裂隙 L4 水墙／门／沙地、最后的希望墓地 L1 普通石路／沼泽树、次元浮岛 L1–L3 浮岩焦树亦补齐。回调墓穴、棺材、空气泡、Sher'Tul 入口、虫洞及可通行墓园入口保持原生。3 件新水下母版、42 张水下运行图及复用母版的 32 张焦树图，奇偶最小明度差分别 18.38%／16.74%；ImageGen 4/6 次（3 采纳，1 棕榈预备调用拒收，无运行图）。12 次独立冷启动 26,339／26,339 支持格绘制、0 回退，48／64／96px 开阔区、64px 地物近景、自然／记忆 FOV、模式往返及英文／简繁选项均核验；650＋53＋180 项 Lua 检查和 70 项生产测试通过。旧干燥石墙一次自然光样本亮度反差 −8.6%，墓穴仍原生；未验证正式包、完整读档或连续战斗。详见 `evidence/t5-20260929/README.md`。本批当轮未升版、未打包；后续提交并纳入 0.6.23。

## Monster batch A／B 实机验证（2026-09-29；已提交 `eb2b416`，纳入 0.6.23）

- 隔离离线夹具、shader、1920×1080，14 场独立冷启动（`tools/run_monster_live_validation.py`，每场停止本场游戏与 Xvfb）。15 款新棋子全部按预期 id 实际绘制：Shax、电鳗、Wrathroot、Horned Horror、Minotaur、Sandworm Queen（两布局）、Rantha、Varsha、两名 Norgos、skeleton archer、armoured skeleton warrior 为**自然生成**；Snaproot、Corrupted Sand Wyrm、ancient dragon turtle 为 npc_list 精确原型**摆位**。拒收的 skeleton master archer 在 Dreadfell／Unremarkable Cave 自然生成两次均保持原生。
- Native↔Refined 四次往返、红／绿／蓝阵营环、部分血量弧、原生隐身与 FOV 外演员不绘制均通过；14 场无 `Lua Error`。审图问题（仅报告，未改图／门限／豁免）：Horned Horror 偏暗且剪影近似 Minotaur；skeleton archer 与 degenerated skeleton archer 48px 几乎难分；armoured 与普通 skeleton warrior、ancient 与普通 dragon turtle 区分偏弱。旧 `tests/live_v9_scene.lua` 仍断言 armoured skeleton warrior 保持原生，与 batch B 冲突，未改。未验正式 TEAA、完整读档、连续战斗。详见 [实机证据](evidence/monster-live-20260929/README.md)。

## Monster batch A 源码与离线迭代（2026-09-29；已提交 `7e5cd52`，Batch B `f8ba3d8`，纳入 0.6.23）

- 逐项核对 11 名守关怪和 Trollmire 洪水池的六种 aquatic_critter；giant eel／dragon turtle 已覆盖，squid／ink squid 被原生池排除。heart-gloom 六种已知前缀复用精确鼠／狼身份；只有完全匹配的基础身份、图像、类型和显示合同通过。Ancient dragon turtle 只开放其精确非 unique 高体合同。
- ImageGen 前台单图共 **21/26** 次；13 款候选中 10 款选中（6 款原门限通过、4 款按母版与 128px 导出双 SHA256 的单资产底盘明度豁免），运行目录现为 **64** 款。Shax、Horned Horror、Norgos Guardian 两次调用后仍不合格，保持原生图。共享门限不变；完整调用、失败、选图及 48／64／96px 彩色／灰度审图见 [美术记录](art/monster-batch-a/REVIEW.md)。
- 本轮**没有启动游戏或夹具**；守关怪、Heart of the Gloom 改名、古龙龟高体及洪水池水生怪的实机 shader／分辨率／可见性检查仍待评审执行。纯 Lua 13 脚本、生产 Python 测试 70 项、死资产审计及源码差分检查为离线门禁；尚未进行 TEAA 安装验证。外部中文报告见 `/workspace/t-engine4/tmp/codex-monA/REPORT.md`。

## 虚空／时空地形三地区（2026-09-29；已提交 `c19e080`，纳入 0.6.23）

- 原生源码先审：混沌之沼与时空裂隙 L1 是可通行 `VOID`／不可通行 `SPACETIME_RIFT`；次元浮岛是移动 `FLOATING_ROCKS` 平台／不可通行 `OUTERSPACE`，`WORMHOLE` 的法术稳定回调和传送效果保留原生。时空裂隙 L2 复用伐木村静态图的精确石质／森林格，L3 复用 Daikara 岩组，L4 复用现有纳尔湖静态图地表合同；特殊水墙、沙地及剧情格原生。[身份合同](evidence/void-20260928/identity.md)。
- 三件 ImageGen 不透明母版，前台单图调用 **3/5**，导出 68 张 128px 图；34 对奇偶差最小 **16.29%**，无门限变动／豁免。开放区域 48/64/96px、真正记忆 FOV、虫洞与实际出口留图。三个 L1 的自然 FOV 实机地板／阻挡邻格明度差 **82.96%／91.06%／80.39%**。[美术复核](art/terrain-void-v1/REVIEW.md)。
- 隔离离线夹具、shader 开启，十层独立冷启动：支持格 **21,598／21,598** 绘制，原生回退 **0**；十层 Vanilla→Blockout→Refined 往返通过（L2 石质 Blockout 依既有规则保持原生）。Abashed 原生移动平台受控触发一次实际搬移后，复刷仍 **2,464／2,464**、原生回退 **0**。英文、简繁 Game Options 各独立冷启动。[逐层证据](evidence/void-20260928/README.md)。
- 地形合同 **619** 项、修复 **53** 项、模式 **170** 项、生产测试 **66** 项、死资产审计及 `git diff --check` 通过；未验正式 TEAA、完整读档或连续战斗。该迭代当轮未升版、未打包；后续提交为 `c19e080` 并纳入 0.6.23。

## 当前交付：0.6.22 —— 第三批复用与焦土地形发布（2026-09-28；按本任务要求不提交）

- 纳入已提交的第三批地形复用（`d53cb11`）和 Mark of the Spellblaze（`6db8e5a`）。主插件版本、README、CHANGELOG、外测安装指南同步至 0.6.22；Game Options 的英文原键与简繁精确键一致。
- 正式 TEAA 安装至隔离离线夹具，shader 开启、1920×1080、64px，Ritches Tunnels L1、The Deep Bellow L1、Last Hope Graveyard L1、Mark of the Spellblaze L1（28 个熔岩格）、Trollmire L1 及 Scintillating Caves L1 各自冷启动：受支持格 **11,043／11,043** 绘制，原生回退 **0**。英文、简体、繁体 Game Options 地形说明另各自冷启动。见 [0.6.22 实机证据](evidence/runtime-v0622/README.md)。
- 纯 Lua **13** 个独立脚本通过（地形合同 **604**、修复 **53**、模式 **170** 项）；生产测试 **63** 项、死资产审计和 `git diff --check` 通过。TEAA **967** 个成员逐字节匹配源码，**945** 张 PNG 全为 ZIP_STORED；外测 ZIP 四项和 SHA256SUMS 均通过。TEAA SHA256 `90cae7712dedfed314d836802494de4380328a2a9b1e17db019a7605c6137622`；外测 ZIP SHA256 `4a421e23cb5c85106c8d94f07297dd97d8c7540be6476f54bfe4108e46c4dd4b`。HUD 仍为 0.2.7。
- 本轮为归档安装和暂停夹具场景。第三批八层与 Spellblaze 双层的 48／64／96px、模式往返等结论见原迭代证据；未验证完整战役跨进程读档、自然连续战斗或其他游戏版本。发布文件按本任务要求不提交。

## Mark of the Spellblaze 焦土地形（2026-09-28；已提交 `6db8e5a`，纳入 0.6.22）

- 源码核对 L1 Forest 随机熔岩潭、L2 Forest＋静态祭坛图。`BURNT_GROUND`、可挖 `BURNT_TREE`、世界／上／下出口及 `LAVA` 以区域＋来源＋精确身份／规则接入；祭坛与改写格保留原生。原生 `LAVA` **阻挡移动且无 `on_stand` 伤害**，不同于 Daikara 可通行熔岩。[身份合同](evidence/spellblaze-20260928/identity.md)。
- 根据 `spellblaze-L1-lava-64.png`／`spellblaze-L1-open-48.png` 审图返工：前台单图 ImageGen **2/4** 次，新焦树为有枯枝、树干及树根的透明母版；新熔岩为亮黄橙裂隙、黑色冷壳及仅在外缘显示的抬高石岸，16 向连片，不画站立伤害标志。树母版仅按原图 SHA 豁免 A8.1 顶边距，门限与其余检查不变。导出 **42** 张 128px 运行图，21 对奇偶亮度差至少 **12.55%**，超过原有 10% 门槛。[美术复核](art/terrain-burnt-v1/REVIEW.md)。
- 返工后隔离离线夹具、shader 开启，两层各独立冷启动，且两层均实际生成熔岩：受支持格 **5,734/5,734** 绘制，原生回退 **0**；特殊格 16 格原生。两层 48/64/96px 开阔区、熔岩、自然 FOV、真重算 FOV 记忆及出口重拍；Vanilla→Blockout→Refined 往返与原生 DIG 修复通过。自然 FOV 地板／树中心明度差 L1 **27.09%**、L2 **27.49%**。英文、简繁 Game Options 文案未改，前轮独立冷启动证据仍适用。[逐层证据](evidence/spellblaze-20260928/README.md)。
- 地形合同 **604** 项、生产测试 **63** 项、死资产审计及 `git diff --check` 通过。未验正式 TEAA、完整读档或自然连续战斗。该迭代当轮未升版、未打包；后续提交为 `6db8e5a` 并纳入 0.6.22。

## 地形复用第三批（2026-09-28；已提交 `d53cb11`，纳入 0.6.22）

- 源码先审 Ritches Tunnels 三层、The Deep Bellow 三层及 Last Hope Graveyard 两张静态图。[身份合同](evidence/batch3-20260928/identity.md)纠正旧盘点两点：Ritch 有三层，`SANDWALL_STABLE` 在本版可挖成永久沙地；Deep Bellow 的 `underground.lua` 实际载入 gloomy 原生定义。墓园静态图无水；`GRAVE*`、`COFFIN`、`MAUSOLEUM`、`SWAMPTREE*`、道路和特殊出口保留原生。
- 精确接入 Ritch 沙地／稳定沙墙／楼梯、Deep Bellow neutral plain 地板／蔓延地／菌林墙／普通梯子、墓园 L1 草地与世界出口及 L2 Kor'Pul 石地／硬墙／门／上楼。plain 从三件既有母版确定性调色导出 72 张 128px 图，**0/3** ImageGen 调用；36 对奇偶差最小 **10.92%**，无门限改变或豁免。[美术复核](art/terrain-gloom-v1/REVIEW.md)。
- 隔离离线夹具、shader 开启、八次逐层独立冷启动：**14,139／14,139** 受支持格绘制，原生回退 **0**；各层 64px 开阔区及出口、各区 L1 的 48／96px、自然 FOV、记忆与模式往返留图。Ritch 与 Deep Bellow 原生 DIG 修复后仍零回退。L1 lit-pixels 地板／墙差分别 **29.6%／22.6%**；墓园 L1 墙保持原生，不适用成对棋盘墙比较。英文、简繁 Game Options 各独立冷启动。见[逐区表和原始记录](evidence/batch3-20260928/README.md)。
- 地形合同 **593** 项、修复 **53** 项、模式 **170** 项，生产测试 **62** 项、死资产审计及 `git diff --check` 通过。尚未验证正式 TEAA、完整读档或自然连续战斗。本批当轮未升版、未打包；后续提交为 `d53cb11` 并纳入 0.6.22。

## 当前交付：0.6.21 —— 洞穴与地形复用发布（2026-09-28；按本任务要求不提交）

- 纳入已提交的 Unremarkable Cave（`d67e5f9`）、地形复用第一批（`9c6e8a2`）与第二批（`b90bf63`）。Game Options 地形说明的英文原键与简繁译文精确键一致，列有全部新增区域和 Blockout 范围；README、CHANGELOG、外测安装说明同步至 0.6.21。
- 正式 0.6.21 TEAA 安装到隔离离线夹具，shader 开启、1920×1080、64px，独立冷启动 Unremarkable Cave、Reknor L1、Tempest Peak L1、Ardhungol L2、Lake of Nur FLOODED L1、Crypt of Kryl-Feijan L5 及 Trollmire L1 回归。七场 **16,840／16,840** 受支持格绘制，原生回退 **0**；英文、简体、繁体 Game Options 地形说明各由独立新进程拍摄。见 [0.6.21 实机证据](evidence/runtime-v0621/README.md)。
- 纯 Lua **13** 个独立脚本通过（地形合同 **574**、修复 **53**、模式 **170** 项），生产测试 **62** 项、死资产审计与 `git diff --check` 通过。TEAA **853** 个条目与源码逐字节一致，**831** 张 PNG 全为 ZIP_STORED，白名单无源美术／文档／测试／工具／夹具；外测 ZIP 四项及 SHA256SUMS 均核对。TEAA SHA256 `3d5070ea5b53e43e7b5b4e939a49abfa530679564e2c70fafb573f7bb62d94a7`；外测 ZIP SHA256 `994fb624117824c36512d158866f558cee9daae80c7e99057ae56b271cc838df`，HUD 仍为 0.2.7。
- 本次是归档安装与暂停夹具冒烟。全布局逐层及 48／96px 结论见三个原迭代证据；未验完整战役跨进程读档、自然连续战斗或其他游戏版本。发布文件按本次任务要求不提交。

## 地形复用第二批（2026-09-28；已提交 `b90bf63`，纳入 0.6.21）

- 源码逐区核对双布局、逐层生成器和静态图字符表后，接入废弃地城 L1、荒芜废墟 L1–L3、黑暗地窖 L1–L5、傀儡墓地 L1、阿尔德胡格 L1–L3，以及纳尔湖 DEFAULT／FLOODED 的 L1 地表。纳尔湖 L2 和双布局 L3 的水下或干燥石质格不属于已审森林合同，保持原生；受支持格为 0，不将零回退冒充覆盖。法阵、封锁、传送门、石魔像雕像、虫洞、未确认出口与改写格均保留原生。
- 阿尔德胡格上／下层方向梯子由原洞穴母版与原生下梯子剪影导出，新增 ImageGen **0/2**；洞穴运行图由 58 增至 62，31 对奇偶差最小 **12.8%**，未改门限或豁免。19 次隔离离线夹具独立冷启动、shader 开启、逐层 64px 开阔区、各区 L1 的 48/96px、出口、自然 FOV、L1 模式往返：**27,593／27,593** 受支持格绘制、原生回退 **0**。纳尔湖 L1 两布局的邻格中心亮度差分别 −36.6%／−0.2%，深水与树墙视觉分离不足；荒芜废墟、黑暗地窖的石墙中心亮度也略高于地板，已标记而不改旧素材。[证据及逐区表](evidence/reuse-batch2-20260928/README.md)。
- Game Options 地形说明沿原版简繁地名更新，英文、简体、繁体独立进程拍摄。纯 Lua 地形合同 **574** 项、修复 **53** 项、模式 **170** 项；生产测试 **62** 项、死资产审计与 `git diff --check` 通过。当轮尚未验证正式 TEAA；0.6.21 安装冒烟见上方。没有完整读档或自然连续战斗结论。

## 零新图地形复用批次（2026-09-28；已提交 `9c6e8a2`，纳入 0.6.21）

- 在逐区核对原版身份、生成器、所有层及静态图字符表后，复用 Maze 旧墙／Kor'Pul 石质／Daikara 岩山套件，接入 `thieves-tunnels` L1–L2、`tempest-peak` L1–L2、`halfling-ruins` L1–L4、`reknor` L1–L4、`reknor-escape` L1–L3。严格来源与最终规则合同不变；密室、改写显示、特殊出口及剧情格继续原生。`ardhungol` 因现有 cave 套件缺上／下层不同方向的梯子图而跳过，`WORMHOLE` 也须保持原生。
- 隔离离线夹具、shader 开启、十五次独立冷启动：支持格 **31,383／31,383** 绘制，受支持格原生回退 **0**。逐层 64px 开阔区、每区 L1 的 48／96px、至少一个出口、每区一层 Native→Blockout→Refined 往返均留存。[逐区证据](evidence/reuse-batch-20260928/README.md)。Tempest Peak L1 原版 0.3 光照使复用裸岩图过暗：自然 FOV 的 64px lit-pixels 地板／墙 32.14／24.40，相差仅 24.1%，视觉风险已标记，本轮不改图。石质格 Blockout 沿原套件保持原生，岩山格 Blockout 使用占位图。
- Game Options 说明与简繁精确键采用游戏现有中文地名；英文、简体、繁体独立进程截图见上述证据。`terrain_contract` **559** 项、生产测试 **62** 项、死资产审计及 `git diff --check` 通过。该批次当轮按任务要求不改版本、不构建 TEAA／外测包，后续已提交 `9c6e8a2` 并纳入 0.6.21。没有完整战役读档或自然连续战斗结论。

## Unremarkable Cave 单层洞穴地形迭代（2026-09-28；已提交 `d67e5f9`，纳入 0.6.21）

- `unremarkable-cave` 单层 100×50 Static／Roomer 复合地图，按 zone、`cave.lua` 来源印章、原生身份／规则／外观字段接入洞穴地板及 8–18 装饰变体、16 向连片可挖洞墙、世界出口。未知或额外显示格（每次随机地图各 1 格）保留原生；生成区、x=85–87 接缝、静态首领区分别统计。Refined／Blockout／Vanilla 模式往返及原生 DIG 修复通过。美术 3 件 ImageGen 母版、58 张运行图，前台单图调用 **3/5**；墙和梯子的 A8.1 仅按母版 SHA 豁免，其余门限不变。29 对奇偶差至少 **12.8%**。详情见[美术复核](art/terrain-cave-v1/REVIEW.md)。
- 隔离夹具、shader 开启三次独立冷启动，支持格 **14,997/14,997**、原生回退 **0**；48/64/96px 开阔区及出口、64px 静态图接缝与真正重算 FOV 的记忆图已拍摄。自然 FOV 渲染帧的地板／墙邻格明度差分别 **67.69%／63.22%／59.49%**，均超过 30% 目标。见[实机证据](evidence/unremarkable-20260928/README.md)。纯 Lua 543／53／170 项、62 项生产测试、死资产审计及 `git diff --check` 通过。未验正式 TEAA、完整战役跨进程读档或连续战斗；该迭代当轮按任务要求不改版本、不打包、不提交；后续已提交 `d67e5f9` 并纳入 0.6.21。

## 当前交付：0.6.20 —— 四片新区地形发布（2026-09-28；按本任务要求未提交）

- 汇入已审核提交的迷宫双布局（`5188942`；裂隙返工 `4a7fe99`）、黑暗之心双皮肤（`20e8d1f`）、沙虫巢穴双布局（`d01f67a`）和闪光洞穴双布局（`1dbec49`）。Game Options 地形说明及简繁精确键使用游戏已有地名「迷宫／迷宮」「黑暗之心」「沙虫巢穴／沙蟲巢穴」「闪光洞穴／閃光洞穴」，列出 Refined 覆盖与 Blockout 格子家族；README、更新日志及外测安装说明同步。
- 正式 TEAA 的隔离夹具 1920×1080、64px、shader 开启下，独立冷启动 Maze COLLAPSED L1（含 5 个 CRACKS）、Heart of the Gloom dreamy L1、Sandworm BIGWORM L1、Scintillating TWISTED L1；支持格分别 **1,569／1,569、2,499／2,499、6,997／6,997、861／861**，原生回退全为 0。Trollmire 独立冷启动确认事件光环默认 Subtle，并生成 fell aura：**20／20** 支持事件格绘制、原生回退 0。英文、简体、繁体 Game Options 地形说明由正式 TEAA 新进程拍摄。逐次结果、截图与日志见 [0.6.20 实机证据](evidence/runtime-v0620/README.md)。
- 纯 Lua 13 个脚本通过（地形合同 506、修复 53、模式 170 项），61 项生产测试、死资产审计与 `git diff --check` 通过。TEAA **791** 项逐字节匹配生产源码，**769** 张 PNG 全部 ZIP_STORED，白名单无源美术／文档／测试／工具／夹具；外测 ZIP 四项及 SHA256SUMS 逐项核对。TEAA SHA256 `a67b5e0998f07a30fa0d931829bdb1124f55f6f74e447723b3e69529fdb21172`；外测 ZIP SHA256 `ded60bfa09ef97e3e8c39027f50be54230dff988ec38c52b937424e2d83d6a7a`，HUD 仍为 0.2.7。
- 本轮仅是归档安装冒烟及暂停夹具场景；其他层与 48/96px 视觉结果见四个原迭代证据，未验完整战役跨进程读档或自然连续战斗。本次发布改动按任务要求不提交。

## Scintillating Caves 双布局晶洞地形迭代（已提交 `1dbec49`，纳入 0.6.20）

- DEFAULT Cavern L1–L3 与 TWISTED Roomer L1–L5 按 zone、`crystal.lua` 来源印章及原生身份／规则／显示字段接入晶洞地板、16 向连片晶墙与三种梯子。与 Heart of the Gloom 同为 `underground` subtype，但不会跨区套图；密室及规则改写格保持原生。棋盘墙代替原生 `makeCrystals` 随机叠层，避免双层晶簇。Vanilla 还原、Blockout／Refined 即时刷新，原生 DIG 后自动修复。
- 评审返工未增生图：ImageGen 前台单图仍 **3/6** 次，三件选定母版重新导出 40 张 128px 运行图。地板改为较亮、柔和的洞石；晶墙顶从母版截取随 16 向掩码／奇偶变化的蓝色晶面，并将原生六款晶簇小图烘入**单张墙图**，南侧临地板才显断面，运行时不叠第二层。晶墙母版 A8.1 仅按原 SHA 豁免，其他门限未改。20 对奇偶亮度差至少 **10.23%**，源图内墙比地板暗 **48.55%**；更关键的实机 64px 自然 FOV 邻格采样，DEFAULT L1 地板／墙 **90.24／43.96**（差 **51.28%**），TWISTED L1 **89.82／50.69**（差 **43.56%**）。详见 [美术复核](art/terrain-crystal-v1/REVIEW.md)。
- 隔离夹具、shader 开启，八层各独立冷启动，返工后两布局 L1 又独立冷启动；现行逐层样本支持格 **11,930/11,930**，原生回退 **0**。八层模式往返与原生 DIG 修复通过；返工后两个 L1 的 48/64/96px 自然 FOV 开阔区、64px 真实重算 FOV 的记忆暗光图及调色图已重拍。其余六层旧截图只用于机制佐证。初轮随机八层未抽到 lesser vault，返工 TWISTED L1 随机生成 snake-pit；另有夹具专用原生 Roomer 强制密室边界图。`foreground` 每次均调用 `setShown/setObscure` 并保持棋盘绑定；返工后夹具控制色像素探针复验红／蓝下降、绿值不变。未做连续战斗逐帧闪烁断言。详见 [实机证据](evidence/scintillating-20260928/README.md)。纯 Lua 506／53／170 项、61 项生产测试、死资产审计及 `git diff --check` 通过。该地形迭代当轮未打包，现已纳入 0.6.20。

## Sandworm Lair 双布局地形迭代（已提交 `d01f67a`，纳入 0.6.20）

- DEFAULT L1–L4、BIGWORM L1–L2 按本区精确原生身份接入沙地、16 向连片占格沙墙、上楼／下楼／世界出口；Refined 与 Blockout 有效，Vanilla 还原。BIGWORM L1 为 350×20，L2 为 50×50；原生沙虫临时隧道 Object 保留原生。NicerTiles 的墙体改图形态已核实并纳入严格外观合同；当前六场随机地图有 19 个特殊显示沙格保持原生。
- ImageGen 前台单图 **3/6** 次，两轮返工新增 **0** 次；三件选定母版由导出器重新合成 40 张 128px 运行图。16 向墙掩码在连片内部只画暖赭色低对比度砂岩细纹，南侧临地板才显露断面，无逐行悬崖条纹；墙顶平均灰度比地板暗 **27.4%**。所有 20 对奇偶差至少 **12.36%**。沙墙 A8.1 右边距差 8.08px，经完整轮廓审图后仅按母版哈希豁免；门限未变。48/64/96px 及墙群接缝复核见 [美术记录](art/terrain-sandworm-v1/REVIEW.md)。
- 隔离夹具六层独立冷启动，两轮返工后 DEFAULT L1／BIGWORM L1 再次独立冷启动、shader 开启：当前逐层记录支持格 **19,481/19,481**、原生回退 **0**；每层 Vanilla→Blockout→Refined 往返通过。六层各用真实 tunneler 来源触发三次原生 DIG，18 个 20 回合临时隧道仍为原生 Object，挖掘后支持格回退 0。返工2 BIGWORM L1 的 7,000 格 Vanilla→Refined 全图刷新 CPU **0.412 秒**，其余层 0.152–0.170 秒；暂停场景未见持续卡顿，不代表连续战斗帧时。L1 两布局 48/64/96px 新开阔区图、真正重算 FOV 的记忆／暗光 64px 图、BIGWORM 中段长廊图、逐层数据及限制见 [实机证据](evidence/sandworm-20260928/README.md)。其余四层旧截图只证明未变的机制。纯 Lua 448／53／170 项、**58** 项生产测试、死资产审计及 `git diff --check` 通过。该地形迭代当轮未打包，现已纳入 0.6.20。

**本次会话的完整脉络见[交接文档](docs/handoff-20260927/HANDOFF.md)**：失败过的度量方法、门控与冻结基线的设计理由、refinement 逃生口的正当用法、生产链路与 codex 侧已知失败模式、死资产审计结论、以及各项结论的边界。本文只记交付状态，不重复那些内容。

## Heart of the Gloom 双皮肤地形迭代（已提交 `20e8d1f`，纳入 0.6.20）

- DEFAULT gloomy／PURIFIED dreamy 各 L1–L3 已按原生来源和规则合同接入地板、creep 邻接边缘、`UNDERGROUND_TREE` 与本区 `dark_grass` `TREE` 的菌林墙，以及上楼／下楼／世界出口。未知、改写及密室格保留原生；Old Forest 原有 `dark_grass` 语义未改。Vanilla 还原、Blockout 与 Refined 即时刷新，原生 DIG 后自动修复。
- ImageGen 前台单图调用 **7/10**：六件选定母版，另一次墙体调用中断无图；两件透明墙体各有逐哈希 A8.1 小边距豁免，未改门限。导出 **144 张** 128px 运行图，含每皮肤 16 种四向连通菌林墙×两奇偶；墙体填满阻挡格，内部纹理柔化以减少重复。沿用森林套件 0.895 奇偶乘数，在整张地板、creep、墙与梯子图完成合成后应用；地板平均亮度差 gloomy **11.23%**、dreamy **10.89%**，新增生产测试要求至少 10%。48/64/96px 与暗光／FOV 实机已复核。详见 [美术复核](art/terrain-gloom-v1/REVIEW.md)。
- 隔离夹具、shader 开启、返工后六次独立冷启动：受支持格 **14,890/14,890** 绘制、原生回退 **0**；110 格严格合同外地格保持原生（含事件／密室）。各层模式往返、两种皮肤 L1 的原生 DIG 修复及两皮肤 48/64/96px 开阔区截图重测通过；截图摆位要求梯子在 96px 视口内。纯 Lua 415／53／170 项、**55** 项生产测试、死资产审计及 `git diff --check` 通过。详见 [实机证据](evidence/heart-gloom-20260928/README.md)。未测正式 TEAA、完整存档读档或自然连续战斗；该地形迭代当轮未打包，现已纳入 0.6.20。

## The Maze 双布局地形迭代（已提交 `5188942`，裂隙返工 `4a7fe99`，纳入 0.6.20）

- DEFAULT L1–L2 与 COLLAPSED L1–L4 接入精确身份的旧石地、独立地衣旧墙、裂隙与原生楼梯／世界出口。`QUICK_EXIT` 和未知地格保持原生。COLLAPSED 的 `OLD_FLOOR` 楼层连接位不画虚构楼梯。旧墙与 Ancient Elven Ruins 未来共用，但该区自身尚未接入验证。
- 旧墙顶面与边缘首轮通过。首版 CRACKS 在 48/64px 实机审图中被评为细划痕，返工以大面积暗洞、亮破边取代。`tools/run_imagegen.py` 前台单图调用累计 **4/6**，新增调用 **1/2**；新母版通过原有地形门控且无豁免，旧稿完整留档。Kor'Pul 连接几何导出 32 张旧墙掩码图，裂隙 2 张，共 34 张 128px PNG。提示词、来源、哈希与新旧对照见 [Maze 美术复核](art/terrain-maze-v1/REVIEW.md)。
- 返工后 COLLAPSED L1–L3 重新各自独立冷启动、shader 开启；连同未改资源的 DEFAULT L1–L2 与 COLLAPSED L4，现行六场景支持格 **10,359/10,359**，原生回退 **0**。返工三层的 `doQuake` 后写入裂隙共 19 格，全部识别并绘制；L4 无裂隙。各层 Vanilla→Blockout→Refined 往返正常；返工后同进程 L1→L2→L1 换层重新绘制且回退为 0。返工三层各有 CRACKS 距玩家一格的 48/64/96px 开阔区原图；逐层数字、出口与局限见 [实机证据](evidence/maze-20260928/README.md)。纯 Lua 地形合同 386、修复 49、模式 170 项，53 项生产测试、死资产审计及 `git diff --check` 通过。未测试裂隙弹窗实际下跳、正式 TEAA 或完整战役读档。该地形迭代当轮未打包，现已纳入 0.6.20。

## 当前交付：0.6.19 —— 雪岩／岱卡拉地形与事件色边（2026-09-28）

- 汇入已提交的事件道路光环修正 `0abe2cc`、诺尔格斯巢穴双布局三层 `179544e`、岱卡拉双布局四层 `df5fbf2`、事件光环地格默认柔和／可选适中色边 `b5658b7`。Game Options 的地形说明及简繁中文精确键已补齐两片新区；地名采用原版简繁译名「诺尔格斯巢穴／諾爾格斯巢穴」和「岱卡拉」。
- 隔离夹具安装正式 0.6.19 TEAA，着色器开启、64px、1920×1080；独立冷启动 Norgos DEFAULT L1 为 **2,500/2,500**、Daikara VOLCANO L4 为 **2,488/2,488**，受支持格原生回退均 **0**。Trollmire fell aura 21/21 支持格绘制，默认 `subtle` 遮罩加载检查 21/21，无错误；英文、简体、繁体 Game Options 的地形说明与事件色边选项均有原始截图。详情、逐次绑定路径、日志及局限见 [0.6.19 实机证据](evidence/runtime-v0619/README.md)。
- 纯 Lua 13 脚本通过（地形合同 372、修复 49、模式 170 项），53 项生产测试、死资产审计及 `git diff --check` 通过。TEAA 有 532 个与源码逐字节相同的条目，511 张 PNG 全部 ZIP_STORED，白名单无源码美术／文档／测试／工具／夹具。TEAA SHA256 `7fc35ebeab696ff9d77f1c77dfe8e0f7904a030485a9b6223354a5b187859ea8`；外测 ZIP SHA256 `3d903b4a5ee85c8f1b31fa7ded81642b1c583783e590bb20e78da68b642f1527`；HUD 保持 0.2.7。外测安装说明见 [0.6.19](docs/external-test-v0619/INSTALL.zh-CN.md)。此轮按任务要求不提交。
- 本次是暂停夹具场景与归档安装冒烟，未检验完整战役读档或自然连续战斗；Norgos 与 Daikara 之前各布局全层的详细验证仍以各自迭代证据为准。未知或不支持的地格保持原生。

## 事件光环地格用户设置（已提交 b5658b7，2026-09-28）

- 事件格色边由夹具专用开关改为正式 `tome.checker_aura_style` 设置，Game Options「Event aura grid」可在 **B 柔和（默认）** 与 **B1 适中** 间切换。沿用地形模式的即时整层刷新与 `saveSettings`；原版地形及不支持的地格继续原生。六张运行遮罩改为 `aura-<kind>-subtle/moderate.png`，B2 强遮罩从 `data/gfx` 移除；生成器仍可按需输出 B2 到独立目录。
- 64px／shader 隔离夹具的英文新进程确认默认 B；Trollmire protective aura 9/9 支持格在 B→B1→B 三阶段均加载 128px 棋盘遮罩，原生站立效果及邻格 DIG 后绘制检查通过。另一次 Trollmire fell aura 的 21/21 支持格由实际 Game Options 行切 B→B1→B，截图可见边框变化，角色坐标与回合不变。配置写入 `moderate`，新进程读取成功，再切回 B 并写入 `subtle`。英文、简体、繁体三语言设置页截图与细节见 [证据](evidence/aura-option-20260928/README.md)。这些是暂停夹具场景与新进程设置读取，不代表完整战役读档或正式 TEAA 安装核验。
- `terrain_contract.lua` 372 项、`runtime_modes.lua` 170 项、53 项生产测试、死资产审计和 `git diff --check` 通过。六张遮罩与生成器逐字节一致，无 B2 运行文件。该迭代当轮不改版本、不打包、不提交；相关内容后续已提交并纳入 0.6.19。

## Daikara 双布局四层地形迭代（已提交 df5fbf2，2026-09-28）

- DEFAULT／VOLCANO L1–L4 已接入精确身份的裸岩地板、岩山墙（16 个邻接掩码×两种棋盘奇偶）、无害熔岩、复用雪树与出口构件。`LAVA_FLOOR` 在本区加载时清除 `on_stand`；VOLCANO L4 Caldera 的 `down_center` 是普通熔岩格，原生没有下层跳转，因此不画虚构楼梯。密室 basic 身份、`HARDMOUNTAIN_WALL`、`CLIFFSIDE`、`RIFT` 等保持原生。Blockout／Refined 支持，Vanilla 还原；Norgos 原逻辑保持。
- 审图返工后，ImageGen 前台单图调用共 **7/8 次**（原轮 3 次，返工 4 次／允许最多 5 次）。旧岩墙的尖簇与旧熔岩的红土观感均退选；当前岩墙为占格的升高整块岩体，16 向掩码把同一石材连至相邻格，熔岩为带低亮暗红裂缝的冷却玄武岩。返工首件岩墙因 A8.1 右边距差 1.08px 退选，最终岩墙无豁免通过原门控；**旧岩墙逐哈希 A8.1 豁免已从活动文件移除**，历史保存在 [美术复核](art/terrain-daikara-v1/REVIEW.md)。46 张 128px 运行图与导出逐字节一致；48/64/96px 已审阅。裸岩地板单独制作，因为 Daikara 原生岩地没有 Norgos 的积雪重写。
- 返工最终图以八次隔离夹具独立冷启动重新核验：受支持地格 **19,973/19,973** 绘制、原生回退 **0**；全部普通岩山墙变体均接入。八层模式往返、DEFAULT L1 岩墙与雪树原生 DIG 自动修复、VOLCANO L4 Caldera 中央无跳转熔岩、48/64/96px 开阔区与楼梯／出口补充截图均重新拍摄。27 个随机生成的特殊／密室格保留原生；首轮旧图基线为 19,787／213，不能与本轮随机地图逐格直接比较。详情见 [实机证据](evidence/daikara-20260928/README.md)。纯 Lua 合同 373 项、修复 49 项、模式 160 项、53 项生产测试与死资产审计通过。按本次任务要求**不提交、不改版本、不打包**。

## Norgos' Lair 雪岩地形迭代（已提交 179544e，2026-09-28）

- DEFAULT／INVADED 两布局 L1–L3 接入独立的雪岩地形族：雪岩地板、两种轮廓的雪树、上楼／下楼／世界出口。按 `norgos-lair` 与原生身份、规则、显示字段精确判定；该提交当时尚未启用同名的 Daikara 身份，未知地格及特殊事件中心保留原生。Blockout 与 Native 模式往返可用，Native 还原原版图。
- 内置 ImageGen 前台单图调用 7 次，选出 6 件母版；经森林导出管线生成两种棋盘奇偶共 12 张 128px 运行图，48/64/96px 已复核。一次雪树边距按资产哈希精确豁免；地板门控工具误套 alpha 检查已修复。提示词、原图、门控、导出哈希与美术限制见 [美术复核](art/terrain-norgos-snow-v1/REVIEW.md)。
- 隔离夹具六次独立冷启动，支持格 **14,994/14,994** 绘制，支持格原生回退 **0**；两种布局每层均完成 Native→Refined 往返，L1 树木经原生 DIG 自动修复。另在上楼、下楼和世界出口附近核验 Refined，并对世界出口核验 Blockout／Native。1920×1080 截图覆盖两布局 L1 的 48/64/96px、全部六场景的 64px、记忆／未探索和挖掘。详情见 [实机证据](evidence/norgos-20260928/README.md)。
- 当轮 `terrain_contract.lua` 355 项、`terrain_repair.lua` 45 项、`runtime_modes.lua` 160 项、53 项生产测试及死资产审计通过；后续提交为 `179544e`，未改版本、未打包。0.6.18 归档及其 SHA 不包含本迭代。Blockout 沿用通用占位色；未验证正式 TEAA 或完整存档重载。

## 0.6.18 提交后的 B2 视觉修正（已后续提交，2026-09-28）

- 0.6.18 原提交保留。修复事件克隆道路带原生 `add_displays` 时误回退的问题，并把遮罩物理路径改为游戏可加载的 `/data-checker-revised/gfx/aura-*.png`；遮罩改用地形 Z=2 的独立显示层。该轮内部开关仍默认关闭，无 Options 项、版本变更或当轮打包；后续正式设置见上文 0.6.19 记录。
- A／旧 B／B1 中等／B2 强四列同场景对照见 [v2 拼版](evidence/aura-ab-20260928/ab-sheet-v2.png)，旧 v1 保留。48/64/96px 及 Kor'Pul 石地已目视；48px 的 4 个事件道路格在五阶段都绑定棋盘纹理。六事件×四地表独立冷启动最终 468/468 支持格绘制，五阶段实际请求的地形与 128px 遮罩纹理均无不符；24 次站立效果、近邻 DIG 检查通过。纯 Lua、52 项生产测试、死资产审计通过。细节与随机零格场景重试记录见 [v2 证据](evidence/aura-ab-20260928/README.md)。

## 当前交付：0.6.18 —— 原生随机事件光环地格（2026-09-28）

- 原生事件改写 `cloneFull` 地格的名称、站立效果与小地图颜色后，森林与石质受支持地格继续绘制棋盘地形；特殊事件中心仍原生。内部 A/B 每格淡色预览默认关闭，未加设置或保存。
- 隔离夹具六事件×四地表 24 次独立冷启动：465/465 个受支持事件格绘制，原生回退 0；近邻 DIG 后仍保持棋盘绘制，24 次原生站立回调入口获得对应效果。英文与简繁中文名称均不参与身份判断。粒子环、提示名和小地图颜色保留。原生 NicerTiles 在少数 DIG 邻格重铺时会丢失原事件回调；本插件不改规则，完整存档重载未验。逐格数据、边界与截图见 [实机证据](evidence/runtime-v0618/README.md)；五对 48/64/96px 视觉图见 [A/B 拼版](evidence/aura-ab-20260928/ab-sheet.png)。
- 纯 Lua、52 项生产测试和死资产审计通过。TEAA SHA256 `67d2f898f589a7de9f411adc028eee5fbd0eae66c5c4da99c449d767bac69522`，外测 ZIP SHA256 `6836d00b63a1be4a017a8166173c1dba8be2476f67123c094c88fb891dd24d9a`；450 张 PNG 均 ZIP_STORED 且与源码同字节，TEAA Kor’Pul 光环格冷启动 18/18。HUD 维持 0.2.7。**0.6.18 已单独提交；以上 B2 修正不在该提交和归档内。**

## 当前交付：0.6.17 —— Dreadfell 九层石质地形（2026-09-28）

- Dreadfell L1–L9 接入原有 basic.lua 来源印章石质适配器，零新美术；普通地板、墙、硬墙、门及上楼／下楼／世界出口按原有精确合同绘制。路牌、密室改写格和特殊传送格保留原生；Dreadfell 无布局变体或整层静态图，Roomer 可嵌入静态密室。
- 隔离夹具九层与六个回归场景实机统计，Dreadfell 22,103/22,103 个支持格绘制，支持格回退原生 0；Native／Blockout／Refined 往返及一面普通石墙的原生 DIG 自动修复通过。逐层数字、原生保留格、19 张截图及边界见 [evidence/runtime-v0617](evidence/runtime-v0617/README.md)。Lua Error 0。
- 全部纯 Lua 测试、52 项生产测试、死资产审计通过；447 个 PNG 在 TEAA 中均 ZIP_STORED 且与源码同字节。TEAA 冷启动 Dreadfell L1 为 2464/2464；TEAA SHA256 `dd1836c86823a39b324f673700a6f7091834e405c164f9e7f387040e2a89aea7`，外测 ZIP SHA256 `0e5b290eae8bb801a934b2dba76f4e8f25f7b4359ad74f564767b225bd66f5af`。HUD 仍为 0.2.7。

## 当前交付：0.6.16 —— Rhaloren Camp 双适配器地形（2026-09-28）

- Rhaloren Camp DEFAULT／OVERGROUND L1–L3 已接入，OVERGROUND L1/L2 的森林与石质格在同一层分别由原有适配器负责；L3 为两布局共用静态图。仅来源与外观合同符合的 basic.lua 石格进入石质适配器，森林仍按已验身份识别；其余原生。
- Blockout 在 Rhaloren 只画森林，石质保持原生；Native 全部还原。原生 DIG 后森林树和石墙各一次自动修复通过。
- 纯 Lua 测试、52 项生产测试、死资产审计通过；隔离夹具 11 次摆位、17 张截图（含 TEAA 冒烟）、所支持格 `native=0`，0 Lua Error。逐层数字、原生保留格与视觉结论见 [evidence/runtime-v0616](evidence/runtime-v0616/README.md)。
- TEAA SHA256 `c5ffa18cf4922d752de5abfd167d0b9b06c169808e190111373cca886cad049e`；外测 ZIP SHA256 `0bf06e268b0aabcb8fb330225d3f7ff32a0872f861d03c45111ee1355e8a6d9e`。归档冒烟通过；本轮未修改 HUD，也未生成美术。

## 当前交付：0.6.15 —— G0 Old Forest 与 Slazish Fens 地形接入（2026-09-28）

- Old Forest（两种布局 DEFAULT／CRYSTALINE，L1–L4 全部）与 Slazish Fens
  （无布局变体，L1–L3 全部）新增棋盘地形支持，零新美术，完全复用 Trollmire
  已验收的 `grass/tree-*/tree-hard/exit/deep/bog-tree/bog/bog-misc` 族。
  `overload/mod/class/CheckerTerrain.lua` 的森林门控从单一
  `zone.short_name=='trollmire'` 改为显式白名单，并加入一个**按 zone 限定**
  的 `dark_grass→grass` subtype 别名（只对 `old-forest` 生效，Heart of the
  Gloom 同名 subtype 的 TREE 不受影响，仍保持原生）。详见
  [CHANGELOG](CHANGELOG.md#0615--2026-09-28)。
- 单元测试：`tests/terrain_contract.lua`（+20）、`tests/terrain_repair.lua`
  （+4）、`tests/runtime_modes.lua`（+7）全绿；`python3 -m unittest discover
  -s tests/production -q`（52 项）与 `python3 tools/audit_dead_assets.py
  --check` 均干净。
- 实机（[evidence/runtime-v0615](evidence/runtime-v0615/README.md)）：隔离
  夹具，14 次摆位（Old Forest 两布局×4层、Slazish Fens 3层、加 Trollmire
  DEFAULT/FLOODED 与 Kor'Pul DEFAULT 三项回归），地毯式统计全部
  `native=0`；两次原生 DIG（Old Forest 树、Slazish Fens BOGTREE）自动修复
  确认；20 张 1920×1080 截图逐张目视核查，画面干净；`Lua Error` 计数 0。
  保持原生且符合预期：`LAKE_NUR`（Old Forest L4，每层 1 格，无 subtype）、
  各 lesser_vault 内的原版石头房间／CRYSTALINE 专属晶洞密室、被光环改写过
  `name` 的草地格、以及 Slazish Fens 末层的 `PORTAL`（唯一按设计保留原生
  的身份）。
- 打包：`dist/tome-checker-revised-0.6.15.teaa`，SHA256
  `ed2d5a6bad55c4d7de7c50a757ae0a479757a28361823a2fa7592eee7b051909`。TEAA
  冒烟（归档形式加载 Old Forest DEFAULT L1，census `native=0`，`Lua Error`
  计数 0）。外测 ZIP
  `dist/tome-checker-revised-external-test-0.6.15-hud-0.2.7.zip`，SHA256
  `173cdeccf67b574e29448059f453bf86511fb423b77f7eb88c7e94002243747f`；沿用
  HUD 0.2.7（未改动），安装说明
  [docs/external-test-v0615/INSTALL.zh-CN.md](docs/external-test-v0615/INSTALL.zh-CN.md)。
- 边界：密室内容未逐一核实内部细节，只确认整体保持原生；两区域整片贴图的
  连片观感留给后续人工美术复核。

## 当前交付：0.6.14 —— F1 洪水沼泽地形接入（2026-09-28）

- Trollmire FLOODED 布局新增 `bog-tree`（沼泽柳树，两款风格变体）、`bog`
  （沼泽浅水）、`bog-misc`（沼泽装饰，三种）三种身份；`hardtree` 改用独立
  贴图，不再借用普通树画面。身份识别改按 `define_as`/`add_displays` 等
  原生字段判定，`applyForest` 不再读 `zone.is_flooded`；Blockout 模式同步
  支持洪水身份。详细改动、门控修复（新增按 `kind` 分流的 terrain 专用门控、
  `CORNER_ALPHA_MAX` 容差、`hardtree` 逐资产 A8.1 豁免）、导出扩展、以及
  实现中发现并修复的一处选图公式缺陷（32/64 张 `bog-tree` 运行件此前因
  风格公式与棋盘奇偶代数恒等而永远选不中，现已解耦、审计工具确认零死
  资产）见 [CHANGELOG](CHANGELOG.md#0614--2026-09-28)。
- 生图与导出复核：[art/terrain-f1-flooded/REVIEW.md](art/terrain-f1-flooded/REVIEW.md)（含
  逐资产调用来源、门控实测、`hardtree` 豁免详情、B1/B2/B6/B8 视觉复核）。
  门控实现依据与已接受实测偏差：[ACCEPTANCE.md §7](docs/g0-terrain-contract-20260927/ACCEPTANCE.md#7-f1-批次门控实现与已接受实测偏差2026-09-28)。
- 单元测试：`tests/runtime_modes.lua`（153 项）、`tests/terrain_contract.lua`
  （251 项）、`tests/terrain_repair.lua`（37 项，新增 BOGTREE→BOGWATER 挖掘
  修复用例）全绿；`python3 tools/audit_dead_assets.py --check` 干净
  （`forest:refined` 从 118 变为 150，`dead assets: none`）。
- 实机（[evidence/runtime-v0614](evidence/runtime-v0614/README.md)）：隔离
  夹具，`tests/live_map_survey.lua` 强制 Trollmire FLOODED L1/L3、FLOODED
  区域对象下的静态藏宝图 L4、DEFAULT L1 回归对照共四次摆位，地毯式统计
  `native=0`（2590/2590、2598/2598、397/397、2427/2427）、模式往返验证；
  FLOODED L1 用原生 DIG 挖掉一棵 BOGTREE，`NicerTiles` 既有的自动修复挂钩
  把画面从 `bog-tree-b7-0-0.png` 换成 `bog7-0-0.png`，未手动调用修复接口；
  13 张 1920×1080 未编辑截图，`Lua Error` 计数 0。
- 打包：`dist/tome-checker-revised-0.6.14.teaa`，SHA256
  `8587ff5b9e14f3cd0ffbdd1cfd561967d5d1c07951d32e386ec948bf13c5c6e8`。TEAA
  冷启动冒烟（[evidence/teaa-install-20260928-v0614](evidence/teaa-install-20260928-v0614/README.md)）：
  归档形式加载确认，强制 FLOODED L1 census `native=0`，`Lua Error` 计数 0。
  外测 ZIP `dist/tome-checker-revised-external-test-0.6.14-hud-0.2.7.zip`，
  SHA256 `72f5b36e781ded8cd29736bfc73b0e7278ca756748da6248a165fb28686eb4a2`；
  沿用 HUD 0.2.7（未改动），安装说明
  [docs/external-test-v0614/INSTALL.zh-CN.md](docs/external-test-v0614/INSTALL.zh-CN.md)。
- 边界：只核验了单进程内四次摆位与一次挖掘；FLOODED L3/L4 未额外挖掘核验；
  `bog-tree`/`bog-misc` 整片水域拼图观感（B5）与精修/原生交界表现（B9）
  留给后续实机夹具。

## 当前交付：0.6.13 —— E1 胶质接入（46→54），jelly/ooze 8 款（2026-09-28）

- **生图前准入**：8 个身份（green/black/white/yellow jelly、black/yellow/red/blue
  ooze）在隔离夹具用 `game.zone.npc_class:loadList` 直接从 `jelly.lua`／`ooze.lua`
  取原型（这两族不在 Trollmire 自身 `npc_list` 里）、原生 `finishEntity` 解析
  8 个离地图副本，逐项核对显示修饰全空、当前匹配理由均为 `no-art`；jelly
  确认 `never_move=1` 且无 `can_multiply`/`clone_on_hit`（不分裂），ooze 确认
  `clone_on_hit={min_dam_pct=15,chance=30}`（会分裂）。证据见
  `evidence/e1-art-gate/`。8 项全部合格，无剔除。
- **生图**：两个任务包（`e1-gel-jellies-v1`、`e1-gel-oozes-v1`），每款
  `max_attempts=2`，实际消耗 **8 次调用，全部首轮通过，零次返修**。风格门控
  `allow_grandfather=False` 全部通过（底盘偏移 -2.15…+3.00，最大不透明半径
  ≤0.8596，均在 ≤0.867 阈值内）。可分性复核见 `art/monsters-e1-gel/REVIEW.md`：
  黄色一对（jelly 对称丘状 vs ooze 定向拖尾）区分度很强；**黑色一对（black
  jelly / black ooze）是本轮最弱的一对**，如实记录——两者都是深色高光泽团块，
  48px 灰度下第一眼接近，放大后仍可辨（jelly 更紧凑居中，ooze 更狭长带
  方向性伪足），满足最低两维差异但不如其余各对干脆。
- **接入**：`overload/mod/class/CheckerTokens.lua` 目录 46→54；
  `tools/prepare_runtime_art.py` 加入 `monsters-e1-gel` 批次，`data/gfx/tokens/`
  新增 8 张运行贴图，`data/token-manifest.json` 更新到 0.6.13／54 项。纯 Lua
  13 组回归、`python3 tools/audit_dead_assets.py --check`（`token:creature` 54，
  dead assets: none）全部通过。
- **修复**：`tests/production/test_art_tasks.py` 的 `PlayerKindTests` 此前因
  `overload/mod/class/CheckerPlayerTokens.lua` 在 0.6.12（`294b497`）的光环显示
  分支改动而使已提交的 `art/production/batches/player-tokens-v1-human-elf.json`
  里的 `render_evidence` SHA-256 引用过期而全部报错；该改动只涉及
  `M.explain` 的 `shader_auras` 判定，未触碰这批引用实际依赖的
  `M.families`/`M.moddable`/`M.keys` 玩家身体族表，因此只重新计算并更新引用
  的 SHA-256（4 处），不改设计或判定逻辑。`python3 -m unittest discover -s
  tests/production -q`（34 项）恢复全绿。
- **实机**（[evidence/runtime-v0613](evidence/runtime-v0613/README.md)）：隔离
  夹具 Trollmire（`--shaders --tiles 64 --terrain refined --resolution
  1920x1080`），8 新棋子 + 2 已映射风格锚点（green mold、green worm mass）摆位，
  48/64/96 三档 + 原生对照共 5 张 1920×1080 未编辑截图，棋子开关切换前后规则
  快照逐字节相同，`Lua Error` 计数 0。另用与 `tests/live_shields.lua` 相同的
  原生物理伤害入口对 black ooze 做了一次真实 `clone_on_hit` 分裂核验（`chance`
  临时提到 100 以在暂停夹具内确定性触发，分裂代码本身未改动）：原生日志输出
  "Black ooze splits in two!"，克隆体 `display_uid` 与父体不同，证明拿到独立
  安装的棋子与阵营圆环。
- **打包**：`dist/tome-checker-revised-0.6.13.teaa`，SHA256
  `78f15844cd152f6353cbaf3f6005fcef1432ecdcb3a1f813ce917beb32fd0c0a`；PNG 全部
  ZIP_STORED 且与源码逐字节一致。TEAA 冷启动冒烟
  （[evidence/teaa-install-20260928-e1](evidence/teaa-install-20260928-e1/README.md)）：
  `--teaa checker-revised=...0.6.13.teaa` + 夹具建角，`Binding addon` 日志确认
  以归档形式加载，8 新棋子渲染正常，`Lua Error` 计数 0。外测 ZIP
  `dist/tome-checker-revised-external-test-0.6.13-hud-0.2.7.zip`，SHA256
  `8f8e2337af8c7815c2e392f1a1477a3e06bd786e50b92c5e28bbcdd369361dee`；沿用 HUD
  0.2.7（未改动），安装说明
  [docs/external-test-v0613/INSTALL.zh-CN.md](docs/external-test-v0613/INSTALL.zh-CN.md)。
- **边界**：只测试了 Trollmire 单一进程、单一摆位布局，未测自然生成/自然遭遇
  概率、更高等级实例、存档/读档；`clone_on_hit` 只验证了父→子一级分裂，未验证
  子体再分裂；green ooze、red/blue jelly、crimson ooze、gelatinous cube 按计划
  延入 E1b，未接入。运行 `tools/prepare_runtime_art.py` 时观察到 20 个几何
  UI 遮罩字节变化（`_badge-*`/`_relation-*`/`_shield-*`/`_health-band`/
  `_player-inner`），与 0.6.9 记录的现象一致：本机 zlib 版本与生成这些文件时
  不同，逐张核对像素完全相同，不是本轮改动引入的差异。

## 当前交付：0.6.12 —— 原生 shader 光环下保留棋子（2026-09-28）

- **改法（plan A）**：`CheckerTokens.appearance()`／`CheckerPlayerTokens.explain()` 去掉对非空
  `shader_auras` 的整体拒绝；`add_mos` 判空改为忽略原生 `_isshaderaura` 记账条目（光环施放于
  棋子安装之前时，记账落在真实 actor 自己的 `add_mos` 上）。`Game:checkerRefreshActor` 新增：
  安装棋子时若光环记账落在真实 actor 上，先清空、再在 `shader_auras` 非空时触发一次
  `updateModdableTile`，让光环在棋子贴图上重建；棋子被移除且未换新棋子时，若光环仍在，同样
  触发一次 `updateModdableTile` 让光环回到原生贴图。`'update'` 语境本身不做事——紧随其后的
  原生调用自会用最新 `replace_display` 重建。玩家纸娃娃既有的 `rebuildPaperDoll` 路径不变，
  两条路径按 `elseif` 互斥。`superload/mod/class/Actor.lua` 未改动。
- **单元测试**：`tests/token_mapping.lua`、`tests/player_tokens.lua`、`tests/random_identity.lua`
  更新为新契约（光环前/后安装、重复刷新不重建、移除后原生光环回归、`_isshaderaura` 记账不误判
  为身体变化）；纯 Lua 13 组回归（`lua5.1 tests/*.lua`，跳过 `live_*` 与 `lifecycle.lua`）全部通过。
- **实机**（[evidence/aura-tokens-20260928](evidence/aura-tokens-20260928/README.md)）：隔离夹具
  `--shaders --tiles 64 --terrain refined --resolution 1920x1080`，`checkerStage()` 冻结 AI，
  施放 4 种原生光环样本（`stone_skin`/crystalineaura、`body_of_fire`、`reflective_skin`、
  `essence_of_the_dead`，参数取自原生天赋/效果代码）到 wolf/forest troll/brown bear/large
  brown snake/就地生成的 giant crystal rat/玩家共 6 个目标，另在 crystal rat 上跑通真实
  `learnTalent`+`forceUseTalent(T_STONE_SKIN)` 天赋路径。结果：全部保留棋子，`add_mos` 记账
  安装/移除各恰好 2→0 条、重复刷新不叠加；关闭棋子开关后原生贴图正确显示各自原生光环，重新
  打开后棋子恢复且不重复；地形 vanilla/refined 切换不影响光环状态。48/64/96 三档 +「关闭前」+
  「棋子关闭原生光环」共 5 张 1920×1080 未编辑截图；`Lua Error` 计数 0。
- **打包**：`dist/tome-checker-revised-0.6.12.teaa`，SHA256
  `593762025e2c7feeb4d3f9b36d1197672c7fdfb682aa821218cac4e01565b0e5`；PNG 全部 ZIP_STORED 且与
  源码逐字节一致。TEAA 冷启动冒烟（`--birth "Human:Cornac:Male:Berserker"`）：从归档形式加载
  确认（`Binding addon .../tome-checker-revised-0.6.12.teaa`），对 wolf 与玩家各施放一次
  `stone_skin`，棋子与圆环正常、`Lua Error` 计数 0。外测 ZIP
  `dist/tome-checker-revised-external-test-0.6.12-hud-0.2.7.zip`，SHA256
  `7cf7db338115c9eb46e55e2dc5a5cbad9639eb91ad84f82d4a3fc8582ddf9f90`；沿用 HUD 0.2.7（未改动），
  安装说明 [docs/external-test-v0612/INSTALL.zh-CN.md](docs/external-test-v0612/INSTALL.zh-CN.md)。
- **边界**：狼的 `stone_skin` 光环在本轮全部截图（棋子模式与原生模式）里都没有看到明显尖刺，
  逐字段核对过 `add_mos` 记账与玩家/水晶鼠完全一致，判断是 `crystalineaura` 按 `time_factor`
  周期性生长、捕获时机不巧（狼施放时间远早于玩家/鼠），而非本次改动的缺陷，未做进一步 GLSL
  时间轴验证。未覆盖同一 actor 同时叠加两种光环（原生 `updateModdableTilePrepare` 非可换装
  分支本身只在 `add_mos` 为空时插入，第二个光环不会单独重绘，这是原生引擎既有行为，未改动）。
  未扩展支持 unique/`invis.png` 两格身体在光环先于棋子存在时的识别（保守退回原生美术，不崩溃、
  不误判）。只测试了 Trollmire 精修地形夹具场景、单一进程；未测试存档/读档。


## 追加：正式存档读档验收（0.6.11，2026-09-28）

- 用 0.6.11 TEAA（另装 HUD 0.2.7 TEAA）在隔离环境建 Cornac 男狂战士，Trollmire 内以原生 `moveDir`、原生 DIG、AI 不冻结走约 10 回合，改等级徽章色与棋子朝向，原生 `saveGame` 存档并正常退出；新进程走引擎原生读档分支（去掉 `-n`，未触发夹具建角），再存再读一次。
- 结果：回合／位置／生命／区域一致；`player:human_male` 棋子保留；精修地形 2443/2443、原生 0，挖掘格仍为草地且归插件所有；徽章色与朝向持久；两次读档快照一致、无重复叠加；关开关后纸娃娃带装备恢复。怪物棋子 31→30 系晶鼠在真实回合中获得原生 `T_STONE_SKIN` 着色器、按设计让位，非缺陷。
- 存档副本（2.6 MB）与证据见 [evidence/save-load-20260928](evidence/save-load-20260928/README.md)；启动器新增测试用 `--keep-home`、`--load`。
- **边界**：夹具命令桥需 `cheat=true`，存档带作弊标记；未做无夹具真人键鼠建角的读档；仅 Trollmire 1 层、单种子、单角色；未核 HUD 自身设置持久化。

## 当前交付：0.6.11 —— 玩家棋子实机验证、打包与外测（2026-09-28）

- 把此前分三条记录的「玩家正式棋子（未实机验证）」「死资产删除（未打包）」「地形自愈（未打包）」合并进 0.6.11 正式发布；三项下方各自的详细记录保留，仅更新其打包/验证状态。
- **玩家棋子实机验证**：四组独立冷启动建角（Human/Cornac/Berserker、Elf/Shalore/Archmage、Halfling/Halfling 原生对照、Undead/Skeleton），覆盖身份契约、48/64/96 三档、开关切换、外部替换显示（原生变身）让位与回收、换装后原生纸娃娃重建；全程 `Lua Error` 计数 0。证据与截图见 [evidence/player-tokens-20260928](evidence/player-tokens-20260928/README.md)。过程中修好了测试夹具 `tests/fixture/.../Birther.lua` 的 `--birth` 职业匹配漏洞（漏判 `allow-nochange`/`nolore`，非生产代码）。
- **打包**：`dist/tome-checker-revised-0.6.11.teaa`，388 个成员，SHA256 `549c2af54015952aeb3b27ac9eec74a9cad3fbcb59d8bef3f683494d16dc0d62`；PNG 全部 ZIP_STORED 且与源码逐字节一致，不含 `art/`／`tests/`／`tools/`／`docs/`／`evidence/`／`.git`。
- **TEAA 冷启动冒烟**：`--teaa checker-revised=...0.6.11.teaa` + 夹具建角，确认以归档形式加载（`Binding addon .../tome-checker-revised-0.6.11.teaa`，安装目录无同名文件夹）、玩家棋子生效、42 只原生怪物中 32 只棋子画面完整（非黑图）、精修地形与棋子共存、`Lua Error` 计数 0。见 [evidence/teaa-install-20260928](evidence/teaa-install-20260928/README.md)。
- **外测 ZIP**：`dist/tome-checker-revised-external-test-0.6.11-hud-0.2.7.zip`，SHA256 `b81a5f3e08d8564ea0fb27879428429268395d2c0f96766f47e093208cd87652`；沿用 HUD 0.2.7（未改动），安装说明更新至 [docs/external-test-v0611/INSTALL.zh-CN.md](docs/external-test-v0611/INSTALL.zh-CN.md)。
- **边界**：玩家棋子只测目录安装的开关/变身/换装序列（TEAA 冒烟只核验身份与截图，未重跑完整序列）；b/c/d 三组只做建角后单帧核验；未做完整存档/读档序列化；`halfling_female` 仍缺美术、继续原生。

## 已交付：死资产删除（0.6.11，已打包）

- 按 [死资产审计](docs/dead-assets-20260927/FINDINGS.md) 删除 `data/gfx/` 下 **1611 个不可达文件 / 48.8 MB**（A 批 deep/bog `-1` 64、B 批 route/path 1536、C 批 refined bog/water 0/1 共 4、D 批顶层 wall 与 5 个占位 7），清单为审计脚本自身输出，逐路径 `git rm`，明细见 `docs/dead-assets-20260927/DELETED.txt`。保留 blockout 10 张（含顶层 water0/1）、korpul 199、tokens、`hero.png`；剩余 354 个文件，`audit_dead_assets.py --check` 通过。
- 纯 Lua 12 组回归通过；临时构建包 373 个成员、10.8 MB（0.6.10 为 59.8 MB），PNG 全部 ZIP_STORED 且与源码一致。
- 实机（[evidence/dead-assets-20260928](evidence/dead-assets-20260928/README.md)，子代理执行、主代理抽看截图验收）：干净快照、64px、shader 开，blockout／refined／vanilla 各一次冷启动 × Trollmire／Kor'Pul DEFAULT；Trollmire blockout 2445/2445 使用顶层瓦片，refined 2445 格与 Kor'Pul 193 格＋2 出口，缺图 0，日志中加载的贴图均不在删除清单。
- **边界**：只测 64px、目录安装；未测 Kor'Pul HIDEOUT、旧存档残留引用；`art/monsters-v1`、`v2` 旧评审页引用的 `refined/water0.png` 背景随之失效（不进包，未修）。

## 已交付：森林精修地形原生重铺后自愈（0.6.11，已打包）

- 修复 [terrain-fallback 诊断](docs/terrain-fallback-20260927/FINDINGS.md) 方案 A：Trollmire 精修地形被原生 `NicerTiles` 重铺（挖掘、土系天赋、Jumpgate、`on_block_change`、游戏中途整图重铺）替换 Grid 后不再永久退回原生贴图。
- 改法：`CheckerTerrain` 的 `applyForest` 可限定矩形，新增 `M.repair`（只对就地改变的格调 `updateMap`；Kor'Pul 逐格适配器本就自愈，直接跳过）；`Game:checkerRepairTerrain`；新增 `superload/mod/class/NicerTiles.lua` 包装 `updateAround`（原生 3×3 外扩一圈到 5×5，因水体掩码读四邻）、`postProcessLevelTiles`、`postProcessLevelTilesOnLoad`（整图），均只在 `game.level==level` 时执行。读档顺序经源码核对：`runReal()` 末尾的整图重铺先于 `ToME:runDone`，两者都是幂等整图应用。
- 单元：新增 `tests/terrain_repair.lua` 35 项（repl／edits 两条路径、邻格掩码、边界裁剪、非当前层、原生模式、Kor'Pul 跳过）；其余 11 组纯 Lua 回归全部通过。
- 实机（[evidence/terrain-repair-20260928](evidence/terrain-repair-20260928/README.md)，子代理执行、主代理看图验收）：同一进程内对照——遮蔽修复时原生 DIG 使 5×5 窗口出现 **6** 个原生格，修复后 0 且格规则逐格不变；集成 DIG、通用 `updateAround`、两种整图重铺后原生格均为 0（整图 2443 格）；模式往返正确；回合／位置／生命／能量不变。48/64/96 三档加对照共 5 张 1920×1080 未编辑截图。
- 测试工具：`tools/launch_fixture.py` 仅在 `ldd` 报库缺失时才追加 `.build-deps` 库目录（本机系统已有 SDL2 系列，`.build-deps` 的 SDL2_image 反而依赖缺失的 libjxl 导致游戏起不来）；新增 `tools/capture_terrain_repair.py`、`tests/live_terrain_repair.lua`。
- **边界**：本节实机记录仍是当轮目录安装、夹具暂停场景、AI 冻结、单一种子；已随 0.6.11 打包并过 TEAA 冒烟（见上方 0.6.11 小节），但 TEAA 冒烟未重跑本节的挖掘/`updateAround`/整图重铺对照。Stone Wall 到期、Jumpgate、`on_block_change` 共用 `updateAround` 但未逐一施放；真实读档未实测。道路压实泥纹理与方案 B 仍属 G0。

## 当前交付：V9-refine 两款定向返修（0.6.10，2026-09-27）

- **映射 45 → 46**：`skeleton warrior` 接入；`giant brown mouse` 换贴图（身份与映射合同不变，只换像素）。其余 44 款贴图与母版**一字未动**，C0b 的任务包、回执、`imagegen-calls/` 记账与 `art/monsters-v8-c0b/` 全部原样保留。
- **这是 refinement brief，不是第三次重试。** 两款在 C0b 的 2 次配额都已用尽，规范禁止用新目录洗掉返修计数，同时明确允许「现有棋子的重绘需专门的 refinement brief」。新批次 [art/monsters-v9-refine/BRIEF.md](art/monsters-v9-refine/BRIEF.md) 逐项写清旧 brief 的缺陷、新方向、为什么能解决，并由任务包的 `refinement` 声明按 SHA-256 钉住 C0b 的 REVIEW 与回执——事后改旧记录来凑理由会在 `record` 阶段被发现。
- **`skeleton warrior` 换的是动作，不是判据**：双手巨剑从「斜举横过身前」改为**贴身竖持、剑尖朝下、沿身体中轴，剑尖止于脚踝**。俯视三分之四相机下，沿身体竖轴的物体被最大前缩，剑不再给人形轮廓增加外延；旧 brief 的斜举剑近似躺在地平面里、以接近全长投影，这正是 1.105 / 1.017 两个越界半径的来源。首轮实测最大半径 **0.8559**（上限 0.867）。**没有靠缩小主体硬塞**，占格 0.8594 与同类一致。
- **`giant brown mouse` 换的是姿态方向**：从「前倾嗅地的四足」改为白鼷/灰鼷已验证有效的**竖立端坐、双前爪抬到吻边、圆耳高举、尾向前勾一个紧圈**，参考图把已通过的 `giant-grey-mouse` 母版挂成姿态锚点、`brown-rat` 降为必须区分开的同色对照。
- **调用预算**：上限 2 款 × 2 次 = 4 次，**实际消耗 2 次**，两款都在 attempt 1 通过门控并入库，未动用返修配额。另有一次 `--execute` 位置写错的命令被 argparse 在发起前拒绝，未建 `call-*` 目录、未消耗额度。
- **风格门控**：两款均以 `allow_grandfather=False` 通过，`grandfathered=false`、`waived=false`（底盘偏移 +2.00 / +5.32，扇区上偏 +4.37 / +2.75，最大半径 0.8576 / 0.8559，占格均 0.8594）。**没有把任何身份加进 GRANDFATHERED 名单，没有改判据、冻结基线或 `export_token.c` 的 `target_occupancy`。**
- **同族可分性**（见 [art/monsters-v9-refine/REVIEW.md](art/monsters-v9-refine/REVIEW.md)）：`giant brown rat ↔ giant brown mouse` 在 48px 灰度下由「同为四足横身」变为「横长条块 vs 竖立圆团＋双大圆耳」，剪影与明暗两维可分，C0b 记录的最弱对已解决。`skeleton warrior ↔ degenerated skeleton warrior` 以「紧凑直立暗甲＋正中竖直亮剑条」对「低伏散架亮骨＋斜剑」两维可分。**新出现的最近对是 `giant brown mouse ↔ giant grey mouse`**（都竖立、都是中调），靠头部姿态、体态与尾形区分，彩色里另有冷灰 vs 暖棕，如实记为勉强通过。
- **一条如实记录的软缺陷**：`skeleton warrior` 的头盔顶盖压在圆盘斜边上。阻断判据未触发（最大半径 0.8559 ≤ 0.867，主体没越出圆盘轮廓），`subject_intrusion` 实测 +2.75，是 46 款里第五低——因为该判据取扇区中位、对窄角度侵入本来就不敏感，**这是判据的已知钝角**，不要把 +2.75 读成「离盘边很远」。本轮没有为此动用第二次调用。
- **规范/工具修补**：`art/production/templates/repair.txt` 补上与 `creature.txt` 同等强度的原生透明要求（缺口由 C0b 棕鼷返修返回棋盘格 RGB 假透明实测暴露）；`tools/art_tasks.py` 新增 `refinement` 声明，把「专门的 refinement brief」从口头约定变成任务包里必须写出来的、带钉住证据的字段，重复检测本身没有放宽，并补了单元测试。
- **实机**（[evidence/runtime-v0610](evidence/runtime-v0610/README.md)）：0.6.10 TEAA 冷启动安装（日志 `Binding addon … /addons/tome-checker-revised-0.6.10.teaa`），Kor'Pul DEFAULT 摆位 7 枚（2 新美术 + 5 同族锚点），48/64/96 三档各一张 1920×1080 未编辑原图加一张原生对照；四张截图的规则快照哈希完全相同。三档下 7 枚全部渲染，`stealthed=none`；`armoured skeleton warrior` 仍未覆盖并断言原生回退通过。
- **打包**：`dist/tome-checker-revised-0.6.10.teaa`，SHA256 `3cb626bc7500a0930bfb6dffed8aeb516240aa00cba47b495cece9561d01f3be`。1983 个成员，1965 个 PNG **全部 ZIP_STORED**，与源码逐字节相符；`.git` `art/` `tests/` `tools/` `docs/` `evidence/` 与夹具代码均未进包。与 0.6.9 包相比**只有** 1 个新增成员（`data/gfx/tokens/skeleton-warrior.png`）和 4 个字节变化的成员（`giant-brown-mouse.png`、`token-manifest.json`、`init.lua`、`CheckerTokens.lua`）——本轮几何 UI 遮罩重新生成后字节完全相同，没有 0.6.9 那轮的 zlib 版本噪声。
- **本轮边界**：只做 DEFAULT 一种布局；只做摆位静态画面；没有做地形（G0 另一轮）、没有清理死资产（另一轮）；没有改 `check_token_style.py`、`creature.txt`、`terrain-prop.txt`、`launch_fixture.py`；没有改 HUD 仓库、原生 tome 模块与 C 引擎；没有发邮件；没有 amend 历史提交。本轮启动的隔离游戏与 Xvfb 已全部关闭，`/tmp/.X11-unix/` 无本轮残留 socket。
- **本轮新增的历史驱动冻结**：`tools/capture_c0b.py` 与 `tests/live_c0b_scene.lua` 固定断言 0.6.9 的 45 款 catalog 并把 `skeleton warrior` 当作未覆盖样本，46 款之后不能再按原样重跑；本轮另出 `tools/capture_v9.py` 与 `tests/live_v9_scene.lua`，与 `capture_korpul.py`（29 款）、`capture_c0.py`（37 款）的做法一致。

## 上一交付：C0b 八款共享小怪（0.6.9，2026-09-27）

- **映射 37 → 45**：giant white mouse、giant brown mouse、giant grey mouse、giant rabbit、giant crystal rat、brown mold、green mold、shining mold。按精确身份接入，不做 subtype 全族替换。
- **准入门控先于生图**（[evidence/c0b-art-gate](evidence/c0b-art-gate/README.md)）：隔离夹具进 Kor'Pul DEFAULT（seed 537401），用原生 `finishEntity` 解析九个脱离地图的副本，逐项核对 `add_mos`/`add_displays`/`shader`/`anim`/`textures`/`shader_auras`/`replace_display`/`moddable_tile` 全空、`define_as`/`unique` 为空、当前匹配理由为 `no-art`。九项**全部合格**，没有因不支持的显示合同被剔除。被点名要小心的两款实测都没有 shader：`giant crystal rat` 的晶体只是描述与 `T_STONE_SKIN`，`shining mold` 的「luminescent」只在 desc 里。解析前后回合、玩家位置与生命不变。
- **`skeleton warrior` 通过门控但没有接入。** 两次生成的双手巨剑都伸出圆盘（最大不透明半径 **1.105 / 1.017**，判据上限 0.867），两次即该身份的全部配额，**按规范停下、交回设计，没有发起第三次，也没有另建批次绕过计数**。该身份不在 catalog、不在 `data/gfx/tokens`、不在 teaa；运行时保留原生贴图，场景脚本对它断言原生回退并通过。交回设计的结论是「斜举的双手巨剑」与 0.867 的盘半径本身冲突，需要改动作而不是改判据。
- **调用预算**：全批 9 个身份、上限 18 次，**实际消耗 11 次**（8 次首轮通过入库、skeleton warrior 2 次全败、giant brown mouse 1 次返修被拒）。逐次记账在各任务包的 `imagegen-calls/`，失败的调用同样计数。
- **风格门控**：八款入库件在 `tools/check_token_style.py` 下以 `allow_grandfather=False` 全部通过（底盘偏移 +0.65…+7.87，扇区上偏 ≤+9.49，最大半径 ≤0.8596）。`giant white mouse` 与 `shining mold` 被报告标为「偏移逼近阈值」。**没有把任何新身份加进 GRANDFATHERED 名单，没有改判据、冻结基线或 `export_token.c` 的 `target_occupancy`；现有 37 款贴图与母版一字未动。**
- **同族可分性**（本轮最大的美术风险，见 [art/monsters-v8-c0b/REVIEW.md](art/monsters-v8-c0b/REVIEW.md)）：按 48/64/96px 真实 C 导出逐对看图，另有六张彩色/灰度对照表 `art/monsters-v8-c0b/exports/compare-*.png`。三款 mouse 改为竖立端坐＋放大圆耳，与同色 rat 的横长四足在剪影与明暗两维可分；兔以两片竖耳＋无长尾区分；晶鼠以锯齿背线＋暗底硬边亮片区分；四款 mold 靠形态（褶莲座／同心环／圆瘤堆／细柱放射）而非颜色区分，48px 灰度成立。**`giant brown mouse` 是全批最弱的一对**：它没有拿到设计想要的竖立姿态，仍是四足横身，靠朝向、体型比例、圆耳与尾侧区分；其返修调用返回了**画着棋盘格的 RGB 假透明图**，被母版 alpha 判据当场拒收，配额用尽后保留首轮，记为下一轮的 refinement brief。
- **实机**（[evidence/runtime-v069](evidence/runtime-v069/README.md)）：0.6.9 TEAA 冷启动安装（日志 `Binding addon … /addons/tome-checker-revised-0.6.9.teaa`），Kor'Pul DEFAULT 摆位 12 枚（8 新 + 4 同族锚点），48/64/96 三档各一张 1920×1080 未编辑原图加一张原生对照；截图前后规则快照逐字节相同。**三档下 12 枚全部渲染，本批无潜行导致未渲染的款**——夹具解析出的 mouse 是 1 级、尚未获得 `T_STEALTH`（`{base=0, every=2}`），游戏里 2 级以上会获得并可能不渲染，那是正确行为，本轮未复现也未测试。
- **打包**：`dist/tome-checker-revised-0.6.9.teaa`，SHA256 `239041570699c7a8af7078a1d128c96acc0f2bc522bc1370c3066805f816f292`。1982 个成员，1964 个 PNG **全部 ZIP_STORED**，与源码逐字节相符；`.git` `art/` `tests/` `tools/` `docs/` `evidence/` 与夹具代码均未进包。与 0.6.8 包相比新增 8 个棋子 PNG，另有 23 个成员字节变化：`init.lua`、`CheckerTokens.lua`、`token-manifest.json` 是本轮的实际改动，其余 20 个是 `prepare_runtime_art.py` 重新生成的几何 UI 遮罩——逐张核对**像素完全相同**，只是本机 zlib 版本不同导致压缩流不同，**没有任何既有生物棋子的字节被改动**。
- **本轮边界**：只做 DEFAULT 一种布局；只做摆位静态画面，没有战斗、增殖、孢子技能、动态角标或读档；没有做地形，没有清理死资产；没有改 HUD 仓库、原生 tome 模块与 C 引擎；没有发邮件；没有 amend 历史提交。本轮启动的隔离游戏与 Xvfb 已全部关闭，`/tmp/.X11-unix/` 无本轮残留 socket。
- **已知失效的历史驱动**：`tools/capture_c0.py` 与 `tests/live_c0_scene.lua` 固定断言 0.6.3 的 37 款 catalog，并把 `giant grey mouse` 当作未覆盖样本；45 款之后它们不能再按原样重跑。这与 `capture_korpul.py`（29 款）、`capture_thieves.py`（33 款）已有的做法一致：历史采集驱动随其证据冻结，不逐轮改写。

## 上一交付：棋子直径统一 0.82（0.6.8，2026-09-27）

- 用户报告「怪物棋子比原版贴图小，而且棋子之间大小不齐」。根因在运行时几何而非美术：`CheckerTokenStyle.M.scale` 原按 `size_category` 分三档（.86/.94/1.0）再乘固定 .95，同一块 64px 棋盘上出现 70.2% / 76.7% / 81.6% 三种圆盘（44.9 / 49.1 / 52.2px，落差 7.3px）。
- **改法：取消分档，所有棋子统一 0.82 整格。** 抽出具名常量 `M.art_occupancy=.86` 与 `M.token_diameter=.82`，`M.scale` 返回 `token_diameter/art_occupancy`（≈.9535），与 `size_category`、地格尺寸无关，参数签名保留。48px 原先的 `if tile<64 then scale=1 end` 合并分支一并取消。夹具演示玩家棋子的 `.95` 特例并入统一值。
- **格内预算未变**：阵营环 = cell×(art_occupancy×scale+0.085) = 90.50%；护盾外环 = 阵营环 + cell×0.09 = 99.50%。护盾外环不得超过约 0.995 整格，故 0.82 就是圆盘上限。`tools/export_token.c` 的 `target_occupancy` **保持 0.86 不改**——屏幕占比 = occupancy × scale，提高它不会让棋子变大，只会改变母版留白。
- **实机验证**：隔离夹具 1920×1080、shader 开启，48/64/96 三档地格、带盾与不带盾各一组，37 款棋子（size_category 1/2/3/4 各 10/13/7/7 枚）实测 scale 完全一致，圆盘 82.00%、阵营环 90.50%、护盾外环 99.50%，护盾环不越格。`--hero-token` 单独冷启动确认演示玩家棋子与同屏巨魔同径。`monster_scene.audit()` 在 64px 重跑通过。证据见 [evidence/token-scale-20260927](evidence/token-scale-20260927/README.md)。
- **决策对照**：`tools/render_token_scale_compare.py` 生成三张离线对照图，四列分别为现状三档 / 方案(a) 统一 0.82 / 方案(b) 0.88 削薄留道 / 方案(b') 0.88 削薄并外推护盾遮罩。用户看图后决定本轮只落 (a)，不改留道宽度；(b)/(b') 仅作证据保留，未进产品代码。
- **打包**：`dist/tome-checker-revised-0.6.8.teaa`，SHA256 `3e9e10ec6ee8962be9ed344949c1c071ada1110e022e58784ac9b1ee9ce10fba`。1974 个成员，1956 个 PNG 全部 ZIP_STORED，与源码逐字节一致；`tests/` `tools/` `docs/` `evidence/` `art/` `.git` 与夹具代码均未进包。与 0.6.7 包相比只有 `init.lua`、`CheckerTokenStyle.lua`、`superload/mod/class/Actor.lua` 三个文件字节变化，成员清单完全相同。
- **TEAA 冷启动安装冒烟（2026-09-27 补做，通过）**：不重新打包，直接装 0.6.8 那个字节（哈希前后各核对一次均相符）。两次冷启动：`--without-fixture`（1920×1080、64px、shaders 开启、cheat 关闭、无命令桥、正常建角 Cornac Berserker、真实鼠标键盘）与 TEAA＋独立夹具（产品插件仍是 TEAA，夹具只放测试 Lua）。以三条独立证据确认确系归档加载：安装目录下只有 `.teaa` 无同名目录；`Binding addon … /addons/tome-checker-revised-0.6.8.teaa` 的 `add.teaa` 非 nil（同日志里目录安装的夹具该列为 `nil`）；`fs.getRealPath` 显示棋子 PNG 解自 `subdir:/data/|….teaa/…`。四项结论：无 Lua 报错（仅原生 `aiParseTalent` 既有噪声 12 条，与旧归档日志条数相同）；**棋子贴图不是黑图**——37 款密集摆位在 48／64／96 三档下全黑棋子 0 枚，中心区峰值亮度 138–253，ZIP_STORED 绕开黑图问题在安装态成立；统一直径成立——可见 34 枚 scale 全为 0.953488，与 size_category 无关，三档圆盘／阵营环／护盾外环与目录安装那轮逐位相同，截图像素复核阵营环 48px 43–44、64px 57–58、96px 84；地形精修与 Board HUD 0.2.7 的 TEAA 共存正常，当层 refined→vanilla→refined 往返正确，`monster_scene.audit()` 在安装态重跑通过。另 3 枚（thief／rogue／bandit）未渲染，查明是原生潜行（`canSee` 为 false，stealth 28／20／33，格子可见而生物不可见），不是缺陷。证据见 [evidence/teaa-install-20260927](evidence/teaa-install-20260927/README.md)。
- **本轮边界**：未生成新美术、未改 HUD 仓库／原生 tome 模块／C 引擎、未发邮件。TEAA 冒烟的正常游戏段只是 Trollmire 内约十分钟短程游玩，不构成完整战役读档或复杂职业长期游玩结论。本轮启动的隔离游戏与 Xvfb 已全部关闭。
- **已记入、本轮不修的两条**：
  - **stone-troll 越界**：以 alpha≥128 计量，最大半径 90.47%，是 37 款中唯一明显越界者（次高 black-bear 86.55%，中位 85.85%），78 个像素越出 0.86 圆盘，疑似武器出界。待后续单图返修。（越界像素数同时取决于 alpha 阈值与半径阈值：alpha≥128 时 d>0.860 为 78、d>0.867 为 53、d>0.870 为 47；alpha≥250 且 d>0.860 为 45。记录时两个阈值都须注明；建议统一用 alpha≥128 且 d>0.867，与 export_token.c 的 target_occupancy=0.86 名义盘缘对齐。）
  - **Prox / Bill 两格高度**：原生用 `display_h=2, display_y=-1` 画两格高（见 `overload/mod/class/CheckerTokens.lua` 的 `nativeTallImage`），接入后被压成单格。**用户决定维持现状。** 注意现有 128×128 方形圆盘母版纵向拉伸 2 倍会把圆盘压成椭圆，恢复两格高需为这两款另出 1:2 美术。
- **测试工具改动（非产品改动）**：`tools/launch_fixture.py` 新增 `--teaa ADDON=PATH`（限 `checker-revised`／`board-hud`，可重复），把已构建好的归档原样复制进隔离运行时的 `game/addons/` 并删除同名目录安装，复制后比对源／目标 SHA256 并写入 `launch-plan.json`，使引擎只能从 `.teaa` 发现该插件；文件名须为 `tome-<addon>-<version>.teaa`，因为 `engine/Module.lua` 的 `parse()` 只扫 `tome-` 前缀条目。原有把已存在 `.teaa` 移出发现范围的逻辑保留。产品代码与 `init.lua` 版本号均未改。
- **环境修补（非产品改动）**：本机 `libselinux` 缺失使打包的 `Xvfb-local` 无法启动，`tools/launch_fixture.py` 回退到系统 Xvfb；同一台机器上旧 deps profile 也不再提供 `libSDL2_ttf`，改为在 `LD_LIBRARY_PATH` 末尾追加工作区 `.build-deps/root/usr/lib`（存在时才追加）。`processes.json` 同时记录实际使用的 Xvfb 路径，`assert_stopped` 按它判断，避免回退时漏检残留显示服务。只影响夹具启动，不影响任何游戏代码或产物。

## 上一交付：中文修复与角色栏纵向空间（2026-09-27）

- 用户确认中文模式面板空白／可能报错，随后要求 sol 汉化插件、合并资源行并解决纵向空间不足。独立内置 `/root/addon_localization_sol`（gpt-6-sol high）完成简繁词条，主代理完成字体、布局、语义复核、生产包实机和提交；代理已结束。
- **Board HUD 0.2.7，提交 `1d292a5`**：FontPackage语言字体修复中文缺字；自定义标题、Gold和六属性、导航／提示／设置简繁汉化。资源合成单行，常规生命＋体力省30px；小地图可收起并持久化，角色正文增加200px，不改变主地图视口。默认仍展开。
- **棋子0.6.7**：棋子颜色、地形、朝向与RGB编辑器增加简繁中文，保留英文fallback和既有配置键。37款素材、身份映射及地形范围不变。安装说明明确即时刷新已进入的受支持地图。
- 生产TEAA直接冷启动：简体1366×768、繁体1920×1080、英文1366×768；真实鼠标折叠／新进程恢复、六资源排版、中文属性、设置及颜色弹窗通过。相关自动回归通过。完整证据在[HUD0.2.7验证](../tome-board-hud/docs/validation/0.2.7.md)，棋子打包摘要在[evidence/runtime-v067](evidence/runtime-v067/README.md)。
- **新外测包**：`dist/tome-checker-revised-external-test-0.6.7-hud-0.2.7.zip`，SHA256 `ac4c4fae01b73230c922301f940f9cd2cda717624b3fcd16f1ec907841597eee`；[中文安装说明](docs/external-test-v067/INSTALL.zh-CN.md)。保留PNG Stored兼容修复，未包含夹具、测试或源码仓库。
- 已结束所有本轮隔离游戏／Xvfb；未发邮件、未生图。未复现另一种未知Lua报错，不能宣称修复所有报错；未新增复杂职业长期游玩或整局读档结论。后续优先收集外测反馈，再按贴图补完／动画计划推进，玩家正式棋子映射仍未完成。

## 上一交付：重启后 Board 菜单整理（2026-09-27）

- 用户要求暂停时已记录安全点（`25cf2b4`），之后明确“请继续”。本轮完成此前待办的 Board 菜单整理，HUD 提交 `7c8abe4`；没有继续暂停。
- **Game Options → Board HUD** 集中提供原有8项设置，Game Menu不再逐项列出。保留就地行数／聊天控件、即时布局、旧配置键和取消语义；右栏宽度可恢复Automatic。
- 1920×1080和1366×768实机通过；实际鼠标选择18px日志字号并在新进程自动恢复。证据见[HUD 0.2.6验证](../tome-board-hud/docs/validation/0.2.6.md)。测试只用生产TEAA和独立离线夹具；完成后已关闭隔离游戏／Xvfb。
- 新外测包：`dist/tome-checker-revised-external-test-0.6.6-hud-0.2.6.zip`，SHA256 `7df4dfa0f9fed06f4714649af0128890f294cf35d7d67a46bd25978b971f6308`。棋子0.6.6包原样复用，仅更新HUD和安装说明。
- 玩家正式棋子映射仍未完成。固定Cornac演示棋子仅由夹具启用；固定玩家棋子是不考虑换装时的后续候选，本轮没有强行使用演示战士替代所有种族职业。
- 本轮没有新的子代理、生图或邮件发送。后续按用户外测反馈及下方计划推进，不依赖当前进程内状态。

## 0.6.10 阶段历史快照

| 独立插件 | 版本 | 提交入口 | 范围 |
| --- | --- | --- | --- |
| tome-checker-revised | 0.6.10 | 本轮提交（git log） | 46款怪物棋子（新增 skeleton warrior，重绘 giant brown mouse）；几何与直径不变 |
| tome-board-hud | 0.2.7 | 1d292a5 | 中文字体、简繁词条、资源单行、小地图折叠 |

两个插件仍独立。Minimalist仅要求棋子兼容，不另做完整主题。装备换装不在本阶段范围。

交付包：`dist/tome-checker-revised-0.6.9.teaa`，SHA256 `239041570699c7a8af7078a1d128c96acc0f2bc522bc1370c3066805f816f292`（0.6.8 为 `3e9e10ec6ee8962be9ed344949c1c071ada1110e022e58784ac9b1ee9ce10fba`）。外测包仍是 0.6.7-hud-0.2.7，本轮未重打。HUD0.2.7包在相邻仓库dist，SHA256 `4592696e1dd6b8ec3c72eff8a5062b19b536e50a6a9c833e5d5f0c78b8675bb1`。dist为本地构建产物，不进入Git；源码及证据均提交。

## 上一交付：建角HUD与压缩包读取（HUD 0.2.5／棋子 0.6.6）

- HUD按原生 `creating_player` 标志隐藏完整面板及鼠标区域；完成初始加点和介绍后自动恢复；普通游戏菜单保持HUD。不以临时玩家或地图是否存在判断。
- 从TEAA完成正常创建时发现旧压缩PNG黑图。同一PNG Stored成功／Deflated失败，fs.readAll及内存解码成功；证据限本机引擎，未修改引擎或泛称所有平台都不支持压缩图。
- PNG条目改用 ZIP_STORED，Lua／JSON继续压缩。1972成员中1956个PNG字节全部不变；与0.6.5解包仅init.lua版本号变化。怪物仍37款，未启动美术任务。
- [最终正常开局证据](evidence/runtime-v066/README.md)：最终ZIP内TEAA直接安装，1920×1080、64px、shader开启、cheat=false、无夹具，Cornac／Berserker／Normal／Adventure。地形和自然怪物棋子正常；建角隐藏、游戏恢复、鼠标翻组／增行／聊天展开与普通菜单保留HUD均确认。
- 外测ZIP：`dist/tome-checker-revised-external-test-0.6.6-hud-0.2.5.zip`，SHA256 `e21c4e11db7bfe2244249aca6cc280a6932d530b53d558cfbcce549ba5f990e8`；[中文说明](docs/external-test-v066/INSTALL.zh-CN.md)。替代旧0.6.5外测包；未发邮件。
- **用户追问玩家为何不是棋子：正式玩家映射确实尚未完成。** 固定Cornac演示棋子只在专用夹具启用。下一轮候选是不做换装的固定玩家棋子及正式选择／映射；本轮没有把所有种族职业强行映射为演示战士。

## 上一交付：整体移动／朝向（0.6.5）与外部安装包

- 主代理完成整体轻抬：血量／护盾／角标使用包含原生twitch的坐标；缩放主体后备路径校正内缩，说话气泡跟随。仅影响绘制，原生速度、位置、回合和粒子规则保持。
- 新增持久化 **Token facing：Fixed / Follow movement**，默认固定照明朝向；保存原生`_flipx`意图，切换选项或回退原图时恢复。37款怪物和既有gfx全部未重绘。
- [实机记录](evidence/runtime-v065/README.md)：6段1920×1080原始APNG，556个渲染采样，含Board48／64／96px、native/fixed、关闭起伏/平滑、old战术框以及**停用Board后Minimalist独立冷启动**。主体/overlay位移差0，环心最大误差约0.00003px，每帧状态仍最多一套。相关单元回归通过。
- 真实GameOptions朝向行、棋子关闭/重开、实际CFG保存验证通过；没有新增整局跨进程读档结论。一次手动热切Minimalist初始化失败保留为测试诊断，正式按原生要求冷启动通过。
- 由内置 **gpt-6-sol** `/root/external_test_bundle_sol` 独立完成安装说明和外测打包脚本；主代理审查、构建并以只有TEAA、无checker-fixture、cheat=false的正常角色创建验证安装。
- 外测包：`dist/tome-checker-revised-external-test-0.6.5.zip`，SHA256 `df5f1ca1bafeb9f6c7e9fad56cb8a078c60dd08543855a0175518b7dec7005dd`。包内为稳定名称的主插件TEAA、可选HUD0.2.4 TEAA、中文说明和校验文件；没有调试桥、引擎、存档或用户设置。用户需解压外ZIP后把TEAA放入game/addons；不要再次解压TEAA。
- 目前普通玩家主体仍原生，外测包不是演示角色或全游戏美术替换。主体特殊位移残影仍保留；下一轮才对照单棋子滑行。本轮不额外发送邮件。

## 上一交付：状态层重影修复（0.6.4）及 Opus 运动设计

- 用户批准修复并指定 Opus 5.5 设计。主代理只修改拥有棋子的 overlay `setMoveAnim` blur 参数为0，主体参数和原生规则不变；无新增美术或HUD修改。
- [修复证据](evidence/runtime-v064/README.md)：完整1920×1080、64px、Board0.2.4、shader开启，五段正式APNG共464个渲染采样。NPC／玩家每帧状态绘制由最多6次降为1次；主体／overlay位移差0。2621项定向回归通过，1972个生产文件源码／冷启动安装／TEAA一致。
- 初次冷启动窗口偏移与夹具片段顺序失误保留在diagnostics；最终记录按正确顺序完整重拍。前后自然地图不同，不冒充同回合像素对照或绝对时长等同。
- **Opus 5.5最终复核接受WP0。** 代理 `d8958b62-514f-41bb-9b92-a57df788b72f` 的[原稿、补充和主代理收敛方案](docs/motion-design-20260927/PLAN.md)已留档。
- 当时下一轮候选为整枚轻抬＋固定朝向，现已在0.6.5实现；单棋子特殊位移、近战与传送提示仍未实现。主体原生副本保留，不宣称所有运动视觉问题已解决。无需逐物种走路帧；未发起新ImageGen任务。
- 原生 `map.seens` 是当前视野，记忆是 `remembers/has_seens`；主代理曾在评审提示中混淆，最终方案已纠正。新运动效果还要结合单位潜行／隐身／感知判定，不能只看格子视野。

## 上一交付：C0 四款接入（0.6.3）

- 按用户指定，新建独立内置 **gpt-6-sol**：`/root/c0_shared_monsters_sol`（无历史对话继承）。任务：giant white rat、giant grey rat、green worm mass、copperhead snake。
- 主代理已完成[当前原生实例准入](evidence/c0-art-gate/README.md)：四款均为可复用single-image合同，生成前仅因no-art回退；本轮已按精确身份接入。
- [C0美术批次](art/monsters-v7-c0-sol/REVIEW.md)已完成：四款各一次内置ImageGen，共4次，无返修；原生透明母版与完整提示/回执保留，20张48/64/96/128/256候选导出。主代理已复看四款64px及48/96灰度对照，重新核验原图字节与C导出，静态候选接受。
- 子代理已completed；主代理完成精确映射、128px运行素材、0.6.3安装包与[双变体实机验证](evidence/runtime-v063/README.md)。**运行覆盖37款**，旧33款素材哈希不变。8张1920×1080原图，shader开启，含48／64／96px及友方绿圈、中立蓝圈、珍珠白护盾。
- 真实绿虫团两代Multiply的子体各有独立主体／状态层；原生酸性攻击、毒咬动作均执行，DEFAULT出现实际伤害与中毒，HIDEOUT两次未造成伤害，原样记录。调用的是action，不宣称完整AI回合／冷却验证。
- 对照切换前后回合、位置、生命、能量等快照一致；1972个生产文件在源码、冷启动安装与TEAA中逐字节一致。生产工具示例改用固定历史注册表测试，实际重复生图门控继续生效。

## 追加：独立移动审查（未修改生产动画）

- 用户随后要求派发动画检查，独立内置gpt-6-astra `/root/movement_review_astra`完成[源码与实机审阅](evidence/motion-review-v063/README.md)。五段1920×1080原始APNG、464个渲染帧遥测、关键静帧均留档；只操作:162隔离夹具。
- 普通／斜步／快速反向、击退、强制位移、静止起步精准传送、原生Rush动作、A*六格寻路和镜头滚动已采样。蛇本体与overlay的getMoveAnim每帧差0；不能据此推定所有单位或完整自然混战通过。
- **审查时确认、0.6.4已修复状态部分：** 原生blur会复制多套生命／护盾环和等级标记，击退与Rush中清楚可见；停稳会消失。0.6.4已隔离状态层重影，主体的速度感和原生动作语义保留。
- 原版已有twitch起伏，主体相对地面状态环抬起；左右移动还会镜像烘焙光照。这是表现规则选择，未当成位置失同步。暂不立项逐帧走路、旋转或额外弹跳；新方案拟让状态层跟随已有twitch实现整枚轻抬，不叠加另一套弹跳；保持原动作参数、可中断。
- 审阅后临时回调、FPS／idle、smooth／twitch及镜头设置均恢复；仍为暂停的改造测试场景。生产文件及0.6.3包不变，审阅证据另行提交。

## 规划与工具基线（历史快照）

- 新的[系统补完计划](docs/completion-plan-20260927/PLAN.md)替代旧计划的数量基线：33款已映射，111个待处理候选（含条件生成/房间/延后对象，不是全游戏缺图总数），十区域二十布局及21显式房间模板。本轮[当前覆盖快照](evidence/runtime-v063/coverage-current/summary.json)为37款已映射、107个待处理候选；历史计划不改写。
- [生产规范与脚本](art/production/README.md)：怪物、地板、透明构件、定向返修四种模板；来源/参考哈希、重复身份、两维家族差异、生成前合同门控、原图alpha与回执记录。示例白鼠/灰鼠任务均hold，未调用ImageGen。
- [验证记录](docs/completion-plan-20260927/VALIDATION.md)：工具单测、任务包重复生成、发布排除规则通过；不修改运行贴图、插件版本或HUD。
- 规划工具阶段由主代理完成盘点和脚本，当时未派发新子代理、未重拍实机、未邮件发送。

## 上一轮运行交付（0.6.2 / HUD 0.2.4）

1. **三种Kor’Pul出口**：上楼抬升亮阶、下楼暗井、世界出口亮拱门。内置ImageGen每款独立生成，完整提示、母版、原生alpha、C导出及灰度审阅保存在[美术目录](art/terrain-korpul-exits-v1/BRIEF.md)。三张透明前景叠现有石地板；旧196张地形及33款怪物主体不变。
2. **精确接入**：仅允许原生basic.lua的UP／DOWN／UP_WILDERNESS，核对来源、目的地、规则及单层add_mos签名。独立三图清单缺失时回退原生；特殊回调、未知显示和其他来源继续回退，不改换层规则。
3. **实机验证**：[0.6.2证据](evidence/runtime-v062/README.md)。两变体三层楼梯清单、十次真实CHANGE_LEVEL到达、真实未知格不泄露与离开视野后的记忆保留通过。17张1920×1080原始PNG，shader开启，含64／48／96地格与大字号日志。
4. **HUD日志字号**：Esc菜单选择14／16默认／18／20px，保留历史及当前阅读条目，更新换行和行高，聊天字体不变。1920／1366／800三种窗口通过；保存18px后新进程自动恢复通过。见[HUD验证](../tome-board-hud/docs/validation/0.2.4.md)。
5. **提交前核对**：地形合同244项、模式101项及配色设置通过；HUD日志、1728组布局及现有显示回归通过。贴图1968个、HUD12个运行文件在源码、冷启动安装和ZIP中一致。

0.6.2时怪物清单仍是0.6.1的33款，不把三个建筑件算作怪物扩库；本轮0.6.3新增四款。四盗贼潜行和身份结果见[0.6.1](evidence/runtime-v061/README.md)；地板/墙/门/真实开门挖掘结果见[0.6.0](evidence/runtime-v060/README.md)。本轮未重复宣称这些历史测试均重新执行。

## 范围与限制

- Kor’Pul DEFAULT/HIDEOUT：普通地板、墙、硬墙、开闭门及三种石质出口已覆盖。条件房间、未覆盖首领、鼠蛇虫变体、护送NPC等仍原生。不能用通用怪物图掩盖缺口。
- 非泛滥Trollmire精修地形保留；旧森林出口仍把左右通路与世界标记合并，待拆分。FLOODED整体仍原生。
- 阵营红敌／绿友／蓝中立／青玩家白内环、逆时针生命弧、珍珠白护盾和可配置等级颜色均保持；normal/elite无等级标记。
- Board仍为不遮棋盘的三栏，快捷栏默认一行、列数按原生12键组，日志独立、聊天离线自动收起。
- 实机地图和楼梯自然生成，英雄位置及视距是受控夹具操作，AI冻结。没有长时间混战、全战役跨进程读档、在线收发或外部玩家盲测结论。
- 0.6.5仍沿用原版主体平滑移动与twitch，状态层跟随起伏且禁用blur，固定朝向可切换；初始C0场景冻结AI，后续独立审查补了受控连续位移，尚无完整自然混战结论。DEFAULT中原生高门遮住一枚增殖子体的部分下缘；未覆盖地物和地面物品的叠层需后续地形轮处理。
- 首次第三层原生unique_glow编译出现OpenGL sampler验证警告，保留诊断，不宣称已修复原生shader。新楼梯正式截图未见破图。
- 0.6.2早期两次试拍分别因摆位不幂等、暂停夹具未置原生FOV脏标志而作废；已修复并完整重拍。仅`evidence/runtime-v062/screenshots/`的17张和对应capture JSON是最终证据；diagnostics不可混用。

## 下一轮顺序

**Trollmire 精修地形回退方案 A 已在源码修复（2026-09-28，见上方当前交付）**；待随下一次打包出 0.6.11 并做 TEAA 冒烟。方案 B 并入 G0。

0. 状态重影、整枚轻抬／朝向对照已交付；按[运动方案](docs/motion-design-20260927/PLAN.md)下一步比较单棋子特殊位移，无残影先行，再决定是否需要擦痕；近战和传送提示后置。用户开始外测后优先处理可复现反馈。
1. C0首四款已集成，下一批从未覆盖鼠类／霉菌／骷髅按原生显示合同准入；使用生产模板时选择尚未映射身份，不重复生成白鼠和灰鼠。
2. G0核对普通/硬树、深水/沼泽水及FLOODED规则，拆分森林东西向通路与世界出口；复用已验石质楼梯，不重复生成。保留隐藏宝藏揭示和确认回调。
3. 收口Kor’Pul两首领/条件房间与Trollmire两版，再推进Norgos起的[成对地区计划](docs/completion-plan-20260927/PLAN.md)。真实混战和整局读档在机制/阶段里程碑验证。

用户既定分工：简单清单/导出交gpt-6-sol，复杂美术/运行语义交gpt-6-astra；主代理控制实机、整合和每轮独立commit。上一运行轮由p2_stairs_art_astra、p2_stairs_runtime_astra完成楼梯；当时Sol派发受线程上限拒绝，HUD由主代理执行。当前四款美术由独立gpt-6-sol完成；本轮主代理负责接入、实机与提交，没有额外生图调用。

## 交付与历史归档

- 0.6.8的几何改动、对照图、实机探针与截图、CHANGELOG 与本文更新随本轮提交；dist 为本地构建产物，不进入Git。`CHANGELOG.md` 此前停在 0.4.0，本轮只追加 0.6.8 并加了一条说明，不补记 0.4.1–0.6.7：逐版补写需要重新核对每个历史提交，否则只是凭本文转述的二手条目。
- 0.6.5代码、六段APNG、设置页、正常TEAA安装冒烟和外测说明随本轮提交；外测ZIP留在dist。
- 0.6.4修复、五段最终APNG、回归、Opus复核与设计文档在5664e12；HUD无改动，本轮没有邮件发送。
- 0.6.3代码、测试与8张最终截图随此前集成提交；美术在83ad5d0，计划与工具在6bf8fe1。HUD保持0.2.4，无本轮修改。
- 历史九名Paseo评审及上一轮内置子任务的记录见[归档文档](docs/agent-archive-20260927.md)。内置接口仍无客户端归档功能，不以completed冒充archived。
- 0.6.0六张图已邮件发送，工作区receipt为`demo/checkerboard-v3/delivery-v060.json`。
- 0.6.1六张图、0.6.2十七张图及0.6.3八张图保存于仓库；截至本记录均未邮件发送。
- 运行实验只用`demo/checkerboard-v3`隔离离线夹具，不操作普通玩家存档。

## Monster batch B 源码与离线迭代（2026-09-29；未升版、未打包）

- 原生源码核对 11 名目标：Shax、Horned Horror、Guardian Norgos 与两名显式单图骷髅（弓箭手、重甲战士）接入为精确候选，运行目录从 64 增至 **69** 款；skeleton magus、skeleton assassin、ghoul、ghast、ghoulking 缺显式 `image=`，不推断外观，保持原生。
- ImageGen 前台单图 **10/24** 次；六款候选中三款原门限通过、三款 Shax／Horned Horror／Guardian Norgos 以母版及 128px 双 SHA256 锁定的底盘明度豁免经评审 2026-09-29 批准。全局门限未变；skeleton master archer 首稿与普通弓箭手几乎同形同色，缺少原生版的黑金重甲区分，评审拒收并撤回映射，保持原生（二稿 0.881 圆盘越界亦拒收）；待重做。[审图与调用](art/monster-batch-b/REVIEW.md)。
- **本轮没有启动游戏或夹具。** 纯 Lua 11 脚本、地形 Lua 两脚本、生产 Python 71 项、死资产审计及源码差分检查通过；实机 shader／多尺寸／可见性与 TEAA 安装仍待验证。外部中文报告 `/workspace/t-engine4/tmp/codex-monB/REPORT.md`。
