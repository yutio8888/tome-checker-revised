# 开发记录索引（原 README）

当前交接入口：[PROGRESS.md](PROGRESS.md)（版本、验证、未完成项及邮件状态）；[子代理归档记录](docs/agent-archive-20260927.md)。

本目录是独立 Git 工作库。棋盘原型 0.6.30 含 323 款怪物棋子（0.6.30 新增 Batch T–Y 共 72 款、含召唤物与同体形；地形新增 TW7 城镇石板路／耕地／棕榈、格鲁希纳克部落、史莱姆通道、淤泥巢穴、沃尔部落、拉杆／拉杆门／蜡烛、伤害岩浆地面与沃尔军械库深水、阿尔德胡格虫洞、传送门／远行传送门与巅峰法球门、教程 L1、梦境 L1、恶魔空间与时空避难所天赋位面、梦境空间；竞技场与无尽地下城本版不含；0.6.29 的 251 款：0.6.29 新增 Batch O–S 共 60 款、召唤物与同体形沿用棋子，并新增夏特尔／零点圣域／晨曦之门／伊尔克城镇（11 座城镇全部覆盖）、阴影地宫、泰恩之塔、伊塞尔森·月之谷、鲜血之环、艾露安、加伯特部落、巅峰 L1–L11 地形及暗砖墙、楼梯、宝库门与水下气泡；0.6.28 的 191 款：新增 Batch J–N 共 60 款，并新增 Old Forest 晶簇、事件光环环及德斯／伐木工人的小村庄／最后的希望／埃尔瓦拉／伊格／安格利文／钢铁议会城镇地形；0.6.27 的 131 款：Batch H 新增 12 款：三种沙虫、三种水晶、poison ivy、honey tree、Necromancer、三种试验体；Batch I 新增 12 款：green ooze、crimson ooze、gelatinous cube、Malevolent Dimensional Jelly、Harkor'Zun 与其碎片、Burb、Norgan、slimy crawler、Spellblaze Simulacrum、Kryl-Feijan 侍僧、Z'quikzshl；0.6.26 的 Batch G 新增 12 款：xhaiak arachnomancer、shiaak venomblade、dremling、Massok、The Master、Pale Drake、Spellblaze Crystal、Rhaloren Inquisitor、Krogar、Fillarel Aldaren、Harno、Lithfengel；0.6.25 的 Batch D／E／F 新增 25 款：六色巨蚁齐全、六色果冻齐全、12 个地城终层首领、naga tidewarden／tidecaller、treant、shivgoroth 一对，以及重绘 Kryl-Feijan）；棋子、地形与 HUD 各有独立开关。0.6.27 本轮无新增地形，覆盖区域与 0.6.24／0.6.25 相同：宁静的草原 L1–L6、孔克雷夫实验室 L1–L4、剧毒火山 L1–L2、穆格尔巢穴双布局三层、南方海滩、泰尔玛废墟 L1–L5、精灵废墟 L1–L3、沃尔军械库 L1–L2、布莱亚弗巢穴、隐秘山谷洞穴、淹没的洞穴、造物者神庙、灼烧之痕、恶魔空间、夏·图尔堡垒及拉克·肖部落三层（兽人育种棚在当前游戏中已不可进入，其地形代码保留但未纳入本轮覆盖声明，见 PROGRESS.md）；0.6.23 已新增混沌之沼 L1–L3、次元浮岛 L1–L3、时空裂隙 L1–L4、纳尔湖 L2–L3 水下与干燥石质格，以及最后的希望墓地石路、沼泽树、墓碑、棺材与墓堂入口。只替换通过精确来源、身份、规则与外观合同的格子，特殊格继续原版。

- [怪物 Batch H 实机验证](evidence/monster-live-h-20260929/README.md)、[怪物 Batch I 实机验证](evidence/monster-live-i-20260929/README.md)：目录 107→131 款；Batch I 首轮发现的 Harkor'Zun 开关回退已由 `32f4ec5` 修复并复测。以上纳入 0.6.27 外测包。
- [怪物 Batch G 实机验证](evidence/monster-live-g-20260929/README.md)：xhaiak arachnomancer／shiaak venomblade／dremling／Massok（底盘偏移豁免）／The Master／Pale Drake／Spellblaze Crystal／Rhaloren Inquisitor／Krogar／Fillarel Aldaren／Harno／Lithfengel 共 12 款接入，目录 95→107 款。此迭代已提交 `7abe2cf`/`bf4ba5c`，并纳入 0.6.26 外测包。
- [怪物 Batch D 实机验证](evidence/monster-live-d-20260929/README.md)：red/blue jelly 补齐六色果冻族，六色巨蚁全部上线（brown/blue ant 经豁免，carpenter/black ant 重新设计），目录 70→78 款。此迭代已提交 `2caaade`/`13e04b2`，并纳入 0.6.25 外测包。
- [怪物 Batch E 实机验证](evidence/monster-live-e-20260929/README.md)：12 个地城终层首领全部接入，7 款经评审豁免，目录 78→90 款。此迭代已提交 `a3e6fc7`/`a5a7420`，并纳入 0.6.25 外测包。
- [怪物 Batch F 实机验证](evidence/monster-live-f-20260929/README.md)：naga tidewarden/tidecaller、treant 直接过审，shivgoroth/greater shivgoroth 经豁免接入，Kryl-Feijan 重绘撤销原豁免，目录 90→95 款。此迭代已提交 `6965a17`/`a0fda3d`，并纳入 0.6.25 外测包。

第三批与 Spellblaze 的逐层记录分别见[第三批实机证据](evidence/batch3-20260928/README.md)和[Spellblaze 实机证据](evidence/spellblaze-20260928/README.md)。0.6.30 正式归档结果见[发布证据](evidence/runtime-v0630/README.md)，0.6.29 见[上一版证据](evidence/runtime-v0629/README.md)，0.6.28 见[更早版本证据](evidence/runtime-v0628/README.md)。整体仍是内部原型，不是全游戏美术替换。

- [怪物 Batch C 实机验证](evidence/monster-live-c-20260929/README.md)：新增 skeleton master archer（棋子目录 69→70 款），重绘 skeleton archer 与 Horned Horror；隔离夹具 5 场独立冷启动，均无 Lua Error。此迭代已提交 `533341a`，并纳入 0.6.24 外测包。
- [地形批次 4：宁静的草原／孔克雷夫实验室／剧毒火山／穆格尔巢穴／南方海滩](evidence/batch4-20260929/README.md)：五区接入棋盘地形，19 次独立冷启动 36,305／36,305 支持格绘制、0 回退；随后视觉返工火山毒水、丛林树与海滩树／沙。此迭代已提交 `688f3eb`（返工 `87a35e4`），并纳入 0.6.24 外测包。
- [地形批次 5：泰尔玛废墟／精灵废墟／沃尔军械库／布莱亚弗巢穴／隐秘山谷／淹没的洞穴／造物者神庙／灼烧之痕／恶魔空间／夏·图尔堡垒](evidence/batch5-20260929/README.md)：11 个地城 24 层，24 次独立冷启动 59,546／59,546 支持格绘制、0 回退。此迭代已提交 `fdaee0f`，并纳入 0.6.24 外测包。源码中同批接入的兽人育种棚 L1 石质格已不计入本轮覆盖声明，见下方限制说明。
- [拉克·肖部落骨质地形](evidence/rakshor-20260929/README.md)：L1–L3 骨质地面、墙、门、梯子与世界出口接入新 `rakshor` 组，杠杆／封印宝库门／事件格保持原生。该迭代同时返工了兽人育种棚 L2–L3 为独立 `gloom/pit` 地板／墙组（自然 FOV 地板／阻挡明度差提升至 71.2%／70.7%），但该地城在当前游戏中已不可进入，本轮不作覆盖声明。此迭代已提交 `7fb72f9`，并纳入 0.6.24 外测包。
- [虚空／时空地形三地区](evidence/void-20260928/README.md)：混沌之沼三层、次元浮岛三层及异构时空裂隙四层按精确身份接入；三件新母版与现有石质／森林／岩山套件复用，十次独立冷启动支持格 21,598／21,598、原生回退 0，移动平台搬移后仍零回退。WORMHOLE 和剧情传送口保持原生。此迭代已提交 `c19e080`（虚空墙返工 `b2a22e2`），并纳入 0.6.23 外测包。
- [Unremarkable Cave 单层洞穴地形](evidence/unremarkable-20260928/README.md)：100×50 静态／Roomer 复合地图，接入暖色洞穴地板及原生岩块／蘑菇装饰、16 向连片可挖洞墙和世界出口；三次隔离冷启动共 14,997/14,997 支持格、原生回退 0。实机 64px 自然 FOV 地板／墙明度差 59.49%–67.69%，接缝、48/64/96px、记忆、模式往返和 DIG 已核验。三件母版与 58 张运行图见[美术复核](art/terrain-cave-v1/REVIEW.md)。此迭代已提交 `d67e5f9`，并纳入 0.6.21 外测包。
- [Scintillating Caves 晶洞地形返工](evidence/scintillating-20260928/README.md)：DEFAULT 三层／TWISTED 五层接入独立晶地、16 向连片晶墙和上／下／世界梯子。返工将地板提亮为柔和洞石，墙顶改为蓝色晶面与掩码变化的单层晶簇；两布局 L1 的实机自然 FOV 地板／墙明度差分别为 51.28%／43.56%。八层现行逐层隔离冷启动样本支持格 11,930/11,930、回退 0；另验原生密室边界和全图调色。三件母版、40 张运行图及 48/64/96px 审图见[美术复核](art/terrain-crystal-v1/REVIEW.md)。此迭代已提交 `1dbec49`，并纳入 0.6.20 外测包。
- [T5 纳尔湖水下与静态地物](evidence/t5-20260929/README.md)：两种纳尔湖布局的水下层、干燥石质 L3、墓地普通石路／树及次元浮岛浮岩焦树按精确合同接入；12 次独立冷启动 26,339／26,339 支持格、原生回退 0。带回调或剧情规则的格子保留原生。此迭代已提交 `850ba0e`，并纳入 0.6.23 外测包。
- [Sandworm Lair 沙墙返工](evidence/sandworm-20260928/README.md)：源码中双布局六层接入沙地、16 向连片沙墙与楼梯；两轮评审后仅用原母版重新导出，连片墙顶改为较地板明显更暗的暖赭色砂岩细纹，南侧临地板才显断面。DEFAULT／BIGWORM L1 的 48/64/96px 与记忆暗光图已重拍，详见[美术复核](art/terrain-sandworm-v1/REVIEW.md)。此迭代已提交 `d01f67a`，并纳入 0.6.20 外测包。
- [The Maze 迷宫双布局](evidence/maze-20260928/README.md)：DEFAULT L1–L2、COLLAPSED L1–L4 的旧石地、旧墙和裂隙已提交 `5188942`（裂隙返工见 `4a7fe99`），并纳入 0.6.20 外测包。
- [Heart of the Gloom 双皮肤](evidence/heart-gloom-20260928/README.md)：gloomy／dreamy L1–L3 的地面、蔓延地、菌林墙与出口已提交 `20e8d1f`，并纳入 0.6.20 外测包。
- [Daikara 双布局四层地形迭代](evidence/daikara-20260928/README.md)：DEFAULT／VOLCANO L1–L4；裸岩、连片升高岩山墙与带暗红细裂缝的无害冷却熔岩，当前选中三件母版、46 张运行图。旧墙与旧熔岩因审图退选，旧墙 A8.1 豁免已撤销；完整返工记录见[美术复核](art/terrain-daikara-v1/REVIEW.md)。Caldera 中央 `down` 是原生普通熔岩，无下层跳转。已纳入 0.6.19 外测包。
- [Norgos' Lair 雪岩地形迭代](evidence/norgos-20260928/README.md)：双布局 L1–L3 六次独立冷启动、支持格 14,994/14,994、原生回退 0；七次生图调用与十二张运行图见[美术复核](art/terrain-norgos-snow-v1/REVIEW.md)。此迭代已提交 `179544e`，并纳入 0.6.19 外测包。
- [事件光环地格设置](evidence/aura-option-20260928/README.md)：事件改名的草地与石地继续显示棋盘地形；在棋盘地形启用时，事件格默认使用柔和色边 B，可在 Game Options 切换至适中色边 B1 并保存。B2 不随运行素材提供。此迭代已提交 `b5658b7`，并纳入 0.6.19 外测包。
- [0.6.17 Dreadfell 地形接入](evidence/runtime-v0617/README.md)：九层普通石格复用 Kor’Pul 贴图；密室改写格与路牌保留原生。
- [0.6.16 Rhaloren Camp 地形接入](evidence/runtime-v0616/README.md)：同层按格使用经来源校验的石质适配器与森林适配器；两种布局 L1–L3（共用静态 L3）已在隔离夹具验证，支持格零原生回退。Blockout 只覆盖森林格，石质格保持原生；特殊密室格继续原生。
- [0.6.15 G0：Old Forest 与 Slazish Fens 地形接入](evidence/runtime-v0615/README.md)：森林适配器门控从单一 Trollmire 扩展为显式白名单，新增一个按 zone 限定的 `dark_grass→grass` subtype 别名（只对 Old Forest 生效，Heart of the Gloom 同名 subtype 不受影响）；零新美术，完全复用 Trollmire 已验收的贴图族。Old Forest 两种布局（DEFAULT／CRYSTALINE）L1–L4、Slazish Fens L1–L3 全部覆盖；实机 14 次摆位地毯式统计 `native=0`，两次原生 DIG 自动修复确认，20 张截图逐张核查。
- [0.6.14 F1：洪水沼泽地形接入](evidence/runtime-v0614/README.md)：Trollmire 洪水版新增沼泽柳树（bog-tree，两款风格变体）、沼泽浅水（bog）、沼泽装饰（bog-misc，芦苇/苔藓/浮木三种）三种身份，硬树（hardtree）改用独立贴图（此前借用普通树画面）；身份识别改为按 `define_as`/`add_displays` 等原生字段判定，不再依赖 `zone.is_flooded` 整层放行/整层保留原版。生图与导出复核见[F1 复核](art/terrain-f1-flooded/REVIEW.md)，实机核验（FLOODED L1/L3/L4 + DEFAULT L1 回归，四摆位地毯式统计 `native=0`，原生 DIG 挖掘 BOGTREE 自动修复）见[实机核验](evidence/runtime-v0614/README.md)。
- [0.6.13 E1 胶质：jelly/ooze 8 款](evidence/runtime-v0613/README.md)：新增 green/black/white/yellow jelly（固定不动）与 black/yellow/red/blue ooze（会移动、`clone_on_hit` 会分裂），映射 46→54；8 次生图全部首轮通过，零返修。设计与可分性复核（含最弱的黑色一对如实记录）见[第十批审阅](art/monsters-e1-gel/REVIEW.md)，生图前的原生显示核验见 [E1 准入门控](evidence/e1-art-gate/README.md)。
- [0.6.10 V9-refine：骷髅战士接入与棕鼷重绘](evidence/runtime-v0610/README.md)：`skeleton warrior` 换动作方向（双手巨剑改贴身竖持）后首轮过门控并接入，映射 45→46；`giant brown mouse` 改为竖立端坐姿态并换掉运行贴图。换方向的理由记在[第九批 brief](art/monsters-v9-refine/BRIEF.md)，门控实测值与灰度对照见[第九批审阅](art/monsters-v9-refine/REVIEW.md)。
- [0.6.9 C0b：鼠类补全与三款霉菌](evidence/runtime-v069/README.md)：新增 8 款（三种 mouse、兔、晶鼠、棕/绿/亮霉菌），映射 37→45；`skeleton warrior` 因两次圆盘越界被剔除并保留原生图。美术与同族灰度对照见[第八批](art/monsters-v8-c0b/REVIEW.md)，生图前的原生显示核验见 [C0b 准入门控](evidence/c0b-art-gate/README.md)。
- [0.6.8 棋子直径统一 0.82](evidence/token-scale-20260927/README.md)：取消按 `size_category` 的三档缩放，所有棋子在任何地格尺寸下都是 0.82 整格；48/64/96 三档实机、带盾与不带盾均已复核。
- [0.6.7 简繁中文设置与HUD0.2.7](evidence/runtime-v067/README.md)：设置与颜色编辑器汉化；同期HUD修复中文缺字、压缩资源行并允许收起小地图。[当前安装说明](docs/external-test-v0620/INSTALL.zh-CN.md)。
- [下一阶段：常见怪物与地形重绘方案](docs/repaint-plan-20260927/PLAN.md)：当前视觉审阅、40款基础候选及“4怪物＋6地形”的首轮技术样板；按[十地城双变体方案](docs/repaint-plan-20260927/VARIANTS.md)补入替代怪群、首领、召唤和房间敌人，分20种布局成对验收。规划数量不代表已经制作。
- [执行分工与首轮派发](docs/repaint-plan-20260927/EXECUTION.md)：简单审计/导出交gpt-6-sol，复杂美术/运行语义交gpt-6-astra；记录任务边界、依赖及主代理统一实机与提交规则。
- [0.6.3 四款共享怪物实机接入](evidence/runtime-v063/README.md)：白鼠、灰鼠、绿虫团、铜头蛇；两变体8张1920×1080原图、48／64／96px检查、真实两代增殖和原生技能动作。美术由独立Sol完成，见[第七批](art/monsters-v7-c0-sol/REVIEW.md)。
- [0.6.6 压缩包图片读取修复](evidence/runtime-v066/README.md)：PNG 使用 Stored 条目；从最终 TEAA 完成非作弊正常开局，配合 Board HUD 0.2.5 隐藏建角期间的面板。[最新外测安装说明](docs/external-test-v067/INSTALL.zh-CN.md)。
- [0.6.5 整枚轻抬与固定朝向](evidence/runtime-v065/README.md)：六段1920×1080动态对照，48／64／96px、原生起伏开关、两种朝向与独立Minimalist冷启动；新增可保存的Token facing设置。[外部安装说明](docs/external-test-v065/INSTALL.zh-CN.md)与ZIP在dist中，包含主插件及可选Board HUD。
- [0.6.4 状态层重影修复](evidence/runtime-v064/README.md)：只关闭生命／护盾／等级层的 blur，保留原生主体运动；五段1920×1080 APNG、464个渲染采样确认每单位每帧最多一套状态。Opus 5.5复核接受；[新动画方案](docs/motion-design-20260927/PLAN.md)仍待后续样板，不需要逐物种走路帧。
- [0.6.3 独立移动审查](evidence/motion-review-v063/README.md)：Astra完成五段动态采样，发现击退／冲锋复制高对比状态环；这是0.6.4修复前的历史证据。
- [0.6.1 四种盗贼与潜行验证](evidence/runtime-v061/README.md)：cutpurse／rogue／thief／bandit，33款；两变体候选精确映射，HIDEOUT普通视力和原生人形ESP对照，潜行圆环防泄露及原生技能往返。素材、完整提示词和内置ImageGen来源见 [第六批](art/monsters-v6/BRIEF.md)。
- [0.6.2 楼梯与世界出口](evidence/runtime-v062/README.md)：三款独立建筑件，17张实机图、两变体10次原生换层、真实未知／记忆验证；同期Board HUD0.2.4新增日志字号。怪物库仍33款。
- [楼梯与出口历史审计](docs/p1-korpul/STAIRS-EXITS.md)：保留0.6.1时的源码分析；0.6.2完成Kor’Pul部分，森林左右通路／世界标记仍待拆分。
- [0.6.0 Kor’Pul 双布局技术样板](evidence/runtime-v060/README.md)：新增退化骷髅战士／弓手、骷髅法师、灰霉菌，六款地形设计导出196张连接图；两变体实机对照、真实开门动作、挖掘、迷雾记忆与原生ZIP校验。盗贼、两版首领及特殊房间仍保留未覆盖原生图，不代表整区完成。
- [0.5.2 第二组四款及真实繁殖](evidence/runtime-v052/README.md)：响尾蛇、蠓群、胡蜂群、白蠕虫团，25款总览、同族对照与原生两代 Multiply；修复复制怪物共享绘制缓存。
- [0.5.1 首组四款接入](evidence/runtime-v051/README.md)：恐狼、白狼、座狼、白蛇，21款实机与同族对照。
- [0.5.0 身份、独立性与正式包拆分](evidence/runtime-v050/README.md)：真实随机 rare／unique／Boss、两个插件分别冷启动、57 项原生身份覆盖审计。
- [独立开关及颜色重启保存](evidence/options-v050-plus/README.md)：真实设置页的应用、取消、重置与跨进程配置保留。
- [0.4.0 实机证据与测试边界](evidence/runtime-v040/README.md)：九张未经重绘的游戏截图，含原生怪物对照和密集状态样本。
- [0.4.1 实机证据与下一步](evidence/runtime-v041/README.md)：阵营、等级和血条改进，四张 ImageGen 返修，开启／关闭 shader 的实机验证。
- [0.4.2 圆环血条与实机截图](evidence/runtime-v042/README.md)：阵营色保持不变，亮弧长度表示血量，移除棋子内部的竖血条；含 48／64／96px 和原生护盾验证。
- [0.4.3 护盾外环／等级角徽](evidence/runtime-v043/README.md)：将护盾泡罩改为浅蓝外环，金色内圈及橙色火焰圈改为角落徽章；含同场景前后截图与原生吸收、破盾和显示回退验证。
- [0.4.4 原生阵营配色／珍珠白护盾／等级对照](evidence/runtime-v044/README.md)：恢复友方绿色、中立蓝色；护盾独立使用珍珠白。normal 与 elite 均不加标记，rare 及以上使用等级角徽。
- [0.4.5 等级角标参考原版颜色框](evidence/runtime-v045/README.md)：rare 改为粉紫，unique／Boss 及更高等级共用紫色；颜色来源改为地图战术框，形状继续区分具体等级。
- [0.4.6 颜色设置与逆时针血量环](evidence/runtime-v046/README.md)：恢复暖色角标，加入等级／阵营 RGB 预览、保存和恢复默认；血量环从正上方逆时针填充。
- [第三批四只返修说明](art/monsters-v3/BRIEF.md)、[检查结论](art/monsters-v3/REVIEW.md)。当前 37 款选定素材以 [运行时清单](data/token-manifest.json) 为准；历史审阅网页仍显示对应批次的版本。
- [第四批家族规范](art/monsters-v4/BRIEF.md)、[首组小尺寸验收](art/monsters-v4/first-four-review.md)、[第二组小尺寸验收](art/monsters-v4/second-four-review.md)：同族形状和明度的差异、原生透明母版、三张拒选稿及修复过程均留档。

- [首批五种怪物审阅页](art/monsters-v1/index.html)：母版、48／64／96px、原生与旧棋子对照；可切换预览背景和独立阵营圈。
- [第二批十二款／全部十七款总览](art/monsters-v2/index.html?compact=1&all=1)：巨魔与独特角色、陆地兽类、蛇／蜂群／水生怪，可按组查看真实小尺寸。
- [制作规范](art/monsters-v1/BRIEF.md)、[源素材与制作批次](art/monsters-v1/inventory/inventory.md)、[首批检查](art/monsters-v1/REVIEW.md)、[第二批检查](art/monsters-v2/REVIEW.md)。
- [AI 直出与 3D 路线比较](art/monsters-v1/PRODUCTION-ROUTES.md)：当前按用户决定继续 AI 直出。

共 37 种身份的母版由内置 ImageGen 生成，第三批替换其中四种；完整提示词、原图角色与输出来源保存在各批次 prompts/。masters/ 保留原始输出和弃选中间版，selected-masters.json 指定本批候选，sprites/ 或 exports/ 只做尺寸与定位归一化。图片中的中性盘面没有敌我、rank、血量或文字，这些信息由运行时独立显示。

复跑本地导出／审阅图：

```sh
python tools/build_monster_art.py
python tools/capture_monster_review.py
python tools/build_monster_art.py --batch monsters-v2
python tools/capture_monster_review.py --batch monsters-v2
python tools/build_monster_art.py --batch monsters-v3
python tools/build_monster_art.py --batch monsters-v4
python tools/build_monster_art.py --batch monsters-v6
python art/monsters-v7-c0-sol/export.py
python tools/prepare_runtime_art.py
python tools/package_monster_art.py
python tools/package_runtime.py
```

导出需要 C 编译器、libpng 和 Pillow（只读检查）；网页截图需要 Node.js、playwright-core 和本地 Chromium，可传 --playwright、--browser 和 --libraries 指定安装路径。工具等待全部图片和字体加载，并检查小尺寸样本以 1:1 像素显示。原图参考和中文字体来自本工作区原版游戏，审阅网页应在当前工作区打开。

此前美术包 dist/monster-tokens-25-v0.5.2.zip 保留25款历史批次；新增四怪的母版、完整提示词及导出器在 art/monsters-v7-c0-sol/，不冒充已更新该历史美术包。当前运行时包为 dist/tome-checker-revised-0.6.24.teaa；--runtime 只安装生产文件到已有的 demo/checkerboard-v3 离线 runtime。测试需另加 --fixture，或使用 tools/launch_fixture.py；正常角色不会被换成固定狂战士图片。按精确身份接入棋子，未知身份、外部替换和不支持的动画外观使用原生显示；不能用普通狼图冒充未知犬类。棋子的已识别护盾粒子只跳过地图绘制，等级光圈改为徽章；其他状态粒子及聊天气泡继续保留。切回原生显示时恢复原生泡罩与等级圈。

默认配色为敌方红色四刻口、友方绿色实线、中立蓝色虚线、当前操控者青色与白内环。友方／中立／敌方的默认色相含义与原版一致，具体色值为适配棋盘作了调整，也可在设置中分别修改。玩家始终保留白色内环，友方即使改成相同青色也不会获得该内环。阵营细边始终完整，生命亮弧从正上方逆时针填充（左侧 → 下方 → 右侧），损失部分显示为暗色轨道；25% 在左上、50% 为左半圆、75% 留空右上象限，颜色不随血量变化。护盾独立使用更外侧的珍珠白环和四个短刻度，保持原有顺时针方向，亮弧表示原生可量化护盾容量的剩余比例，不并入生命。不同护盾的规则仍以原生提示为准。

等级读取原生 rank，与阵营、血量和怪物等级数字分别表达。按用户选择，critter（1）、normal（2）、elite（3）不加等级标记，仍可从原生提示查看确切类型。rare（3.2）为鲑红单菱形，unique（3.5）为沙棕双菱形，Boss（4）为橙色三尖皇冠，elite boss（5）为金色五尖皇冠，god（10）为带侧饰的红色皇冠。0.4.6 按用户选择恢复 0.4.4 配色，颜色取自原生 textRank；菱形与皇冠的形状保持不变。徽章位于右上角，对话气泡位于左上角以免重叠；elite 与 elite boss 不是同一种 rank。特殊的 godslayer（11）目前没有专用徽章，保留为已知覆盖边界。

**颜色设置：** 游戏选项 → **Token colors**，顶部 **Creature tokens** 与 **Board terrain** 分别控制棋子与地形；**Token facing** 在 **Fixed**（默认固定绘制光照）与 **Follow movement**（原生移动／攻击水平翻转）间切换，即时生效并跨游戏重启保存。Refined 支持前述经过身份核验的地形；Blockout 支持森林、Norgos 雪岩、Daikara 裸岩／山墙／熔岩、Heart of the Gloom 地面／蔓延地／墙／出口、Sandworm Lair 沙地／墙／出口、Scintillating Caves 地板／墙／梯子、Unremarkable Cave 地板／墙／出口、Ardhungol 洞穴地板／墙／梯子的通用占位图，石质适配器（包括 The Maze）仍仅在 Refined 生效。可选 rare／unique／Boss／elite boss／god 等级角标，以及 **Friendly ring／Neutral ring／Hostile ring** 三种阵营圈。RGB 滑块／数字框会更新色块和实际图案预览；**Apply** 立即应用并保存，**Cancel／Esc** 放弃草稿，**Default** 将当前草稿恢复到默认颜色，**Restore default colors** 一次恢复全部等级与阵营颜色。阵营改色同时更新完整细边和已有的残血亮弧，不必等下一次受伤。设置分别保存在游戏用户配置 `tome.checker_rank_colors.cfg` 与 `tome.checker_relation_colors.cfg`，会跨角色及游戏重启保留。颜色缺失或无效时回退到对应默认值；玩家青圈白内环、珍珠白护盾和 normal／elite 无角标的规则保持独立。

程序生成的标记在原生粒子之后绘制，不改动生物画。大／小／old 战术显示均沿用此语义；原生竖／横血条偏好不改变棋子的圆环画法，未覆盖实体仍沿用原生血条。关闭 always_target 时隐藏生命及护盾比例，保留完整阵营圈和护盾存在提示；还原原生演员需关闭 Creature tokens；vanilla 只还原地形。棋子直径不分体型：`size_category` 与地格尺寸都不改变圆盘大小，任何地格下圆盘都是 0.82 整格，阵营环 0.905、护盾外环 0.995，正好落在一格之内（0.6.7 及更早按体型分三档，同屏相邻棋子会差到 7px）。获得／失去护盾时主体大小不跳变。48px 仍不能用来判断精确体型或相近的低血量比例。

棋子主体目前是静态单图，格间位移沿用原生移动插值与twitch起伏；独立的血量、护盾和等级绘制层同步原生 setMoveAnim／resetMoveAnim，但0.6.4将这一状态层的blur固定为0，避免移动残影带出多套状态。主体速度副本仍为原生。0.6.5让状态层与主体沿原生twitch一同轻抬，校正主体中心内缩；没有新增步行帧。Token facing默认Fixed，保留原生朝向意图，可选择Follow movement或关闭棋子恢复原生显示。后续受控动态证据与自然混战的边界见0.6.5验证记录。

测试覆盖真实独立 Actor ZIP 序列化／反序列化、原生 Party 控制往返、原生 shader aura 创建与移除及视觉回退。0.5.2 还覆盖真实 clone／cloneFull／cloneActor 和白蠕虫两代 Multiply，确认子体拥有独立 body／overlay 与回调；生产修复不改变生命、rank 或繁殖规则。它们不是完整战役存档跨进程恢复或第三方插件兼容承诺；真实混战与长时间游玩仍须后续验证。48px 下蠓群细肢、胡蜂细腰、响尾分节和座狼暗腹分离较弱，优先使用64px及以上观察具体物种。

生成母版属于内部视觉原型，未替代对原版引用素材来源的管理。发布打包只应包含明确选定的运行时代码和资产，不能递归打包 .git、art 母版、工具或审阅截图。

0.6.0 地形是独立绘制层，不替换规则Grid。关闭精修时恢复已观察的原生视觉；未知格不显示原生高图从迷雾边缘溢出的内容，已探索但不可见区域保留最后所见。特殊房间、装饰或外部替换不符合精确白名单时保留原生图。地形ZIP测试是独立对象容器的原生序列化，不是完整战役跨进程存档验收。详见本轮实机证据与地形契约。
