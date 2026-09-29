# ToME 棋子外测包安装说明（棋子 0.6.28 / Board HUD 0.2.7）

适用：**Tales of Maj'Eyal 1.7.6** 的正常游戏。这个外层 ZIP 内有主插件 `tome-checker-revised.teaa`、可选的独立界面插件 `tome-board-hud.teaa`、本说明和 `SHA256SUMS`。本地验证使用的是 1.7.6；其他游戏版本及系统尚未验证。

1. 关闭游戏，解压**外层 ZIP**。如需核对下载文件，解压目录中的 `SHA256SUMS` 列出了两个 `.teaa` 和本说明的 SHA-256。
2. 找到游戏安装目录下的 `game/addons/`。把 `tome-checker-revised.teaa` 放进去；如想使用 Board 界面，再把 `tome-board-hud.teaa` 放进去。**不要解压 `.teaa` 文件**。若目录中已有这两个插件的旧版 `.teaa` 或同名解压目录，先移走旧版，避免游戏同时读到重复版本。
3. 启动游戏，在主菜单的插件列表确认主插件已启用。建议用**新测试角色**进入普通游戏，并在创建角色时确认启用了主插件；已有角色的插件关联和存档兼容性未作为本次外测结论。

主插件默认开启已覆盖生物的棋子，地形默认 **原版（Native）**。在游戏内打开 **游戏选项 → 棋子颜色**，可切换 **怪物棋子**，用 **棋盘地形** 循环选择 **原版 / 简化 / 精修**。想看目前覆盖的地形，请选 **精修**。英文路径是 Game Options → Token colors → Board terrain → Refined。棋子与地形选项彼此独立。主插件覆盖的是已经核准的 **191 种怪物身份**；未覆盖或不支持的外观继续使用原版画面。当前地形覆盖集中在 Trollmire（**洪水版与非洪水版均已覆盖**，见下）、**Old Forest（两种布局均已覆盖）**、**Slazish Fens**、**Rhaloren Camp 两种布局**、**Dreadfell 全九层**、**诺尔格斯巢穴双布局三层**、**岱卡拉双布局四层**、**迷宫双布局**、**黑暗之心双皮肤三层**、**沙虫巢穴双布局**、**闪光洞穴双布局**、**隐蔽的洞穴单层**、**未知通道、风暴之巅、半身人废墟、瑞库纳、瑞库纳逃亡**、**纳尔湖 L1 地表、废弃地城、荒芜废墟、黑暗地窖、傀儡墓地、阿尔德胡格**、**里奇通道、无尽深渊、最后的希望墓地、魔法大爆炸之痕**、**混沌之沼、次元浮岛、时空裂隙第一至第四层、纳尔湖 L2–L3 水下格**、**宁静的草原全六层、孔克雷夫实验室全四层、剧毒火山两层、穆格尔巢穴双布局三层、南方海滩**、**泰尔玛废墟五层、精灵废墟三层、沃尔军械库两层、布莱亚弗巢穴、隐秘山谷两层、淹没的洞穴两层、造物者神庙三层、灼烧之痕、恶魔空间、夏·图尔堡垒**、**拉克·肖部落三层**、**城镇：德斯、伐木工人的小村庄、最后的希望、埃尔瓦拉、伊格、安格利文、钢铁议会（仅城内已支持的地格；农田、传送门等保持原版）**，以及两种 Kor'Pul 布局中的部分格子、门和出口；其他地形按原版显示。这不是全游戏美术替换。

## 0.6.28 新增地形与棋子

**怪物棋子**：目录 131→**191** 款（怪物 Batch J–N，共 60 款）：
- **Batch J**（首领／唯一怪）：shardskin、The Withering Thing、The Dreaming One、Weaver Queen、Murgol、Lady Nashva、The Possessed、Subject Z、Grand Corruptor（含精灵教徒形态与恶魔形态）、Assassin Lord、Ben Cruthdar 的畸变体。
- **Batch K**：squid、ink squid、water imp、walrog、weaver hatchling、orb spinner、三种蜘蛛（giant／spitting／chitinous）、ghoul、drem、gigantic sandworm tunneler。
- **Batch L**：orc warrior／soldier／archer、naga myrmidon／nereid、五种沙洛尔精灵（elven guard、mean-looking elven guard、elven mage、elven tempest、elven blood mage）、yaech diver、Kyless。
- **Batch M**：losgoroth、gwelgoroth（三档）、manaworm、faeros／greater faeros、Fyrk（带光环）、umber hulk、xorn、xaren、telugoroth、elven cultist。
- **Batch N**：skeleton magus、ghast、ghoulking、bone giant、四档 vampire（lesser、普通、master、elder）、forest wight、grave wight、shadow stalker、The Shade of Telos。

**地形**：
- **Old Forest 晶洞布局**：CRYSTALINE 事件的晶簇、森林区域内的石质密室；纳尔湖出口（LAKE_NUR）。
- **事件光环环**：事件在地图上留下的光环格（gloom、sand、crystal、cave、burnt、bone 等，如 Rak'shor、Blighted、Dreadfell 中）现在与周围同族棋盘地形连成一片；仅限原生事件定义的光环，熔岩中心、WORMHOLE、SUMMON_CIRCLE 保持原版。
- **城镇**：德斯（Derth）、伐木工人的小村庄（Lumberjack Town）、最后的希望（Last Hope）、埃尔瓦拉（Elvala）、伊格（Zigur）、安格利文（Angolwen）、钢铁议会（Iron Council）。进入城镇时先安装记忆格，因此已探索格也会显示棋盘地形。

**已知限制**：48px 下 dark orc 系偏暗、forest wight 偏暗；伐木工人的小村庄、伊格、安格利文的商店墙为亮砖；城镇中的棋盘道路偏棕；农田与安格利文传送门保持原版；旧存档中的城镇保持原版（需新进入）；原版天气效果未改动，夹具中偶见的天气方块疑为软件 GL 的显示瑕疵。

## 0.6.27 新增棋子

本轮无新增地形。新增 24 款怪物棋子（棋子目录 107→**131** 款，怪物 Batch H 与 Batch I），并修复一个棋子开关问题：

- **怪物 Batch H**：三种沙虫（sandworm、sandworm destroyer、sandworm burrower）、三种水晶（white crystal、red crystal、crimson crystal）、poison ivy、honey tree、Necromancer，以及三种试验体（fleshy experiment、boney experiment、sanguine experiment）。
- **怪物 Batch I**：四个原生软泥／果冻（green ooze、crimson ooze、gelatinous cube、Malevolent Dimensional Jelly）、风暴之巅三首领（Fragmented Essence of Harkor'Zun、Harkor'Zun、Burb the snow giant champion）、Norgan、slimy crawler、Spellblaze Simulacrum、Kryl-Feijan 侍僧、Z'quikzshl。elven corruptor 保持原版画面。
- **修复**：Harkor'Zun 身上带有 Stone Skin 光环；在游戏选项里把怪物棋子关掉再打开后，它曾回退成原版高大身体加光环。现在光环不再影响判定，开关往返后棋子恢复，光环仍包在棋子外。
- 已知限制：crimson ooze 与 red ooze 在 48px 下同为红色团块，靠偏粉色相与浪头形区分；Harkor'Zun 碎片、Burb 深底深主体，48px 下主要靠红环与菱形标记定位；Spellblaze Simulacrum 细长，48px 偏小。
- 上一版（0.6.26）新增的棋子仍然保留。

## 0.6.26 新增棋子

本轮无新增地形。新增 12 款怪物棋子（棋子目录 95→**107** 款，怪物 Batch G）：

- xhaiak arachnomancer、shiaak venomblade（蛛人一对）、dremling（浅灰石像重绘版）、Massok the Dragonslayer（经评审批准的底盘偏移豁免接入）、The Master、Pale Drake、Spellblaze Crystal、Rhaloren Inquisitor、Krogar、Fillarel Aldaren、Harno, Herald of Last Hope、Lithfengel。
- 已知限制：Harno 与 xhaiak arachnomancer 为深色主体，48px 下偏弱但仍可读；Pale Drake 与 The Master 在 48px 下主要靠色相以及原生光环／冠色区分，而非轮廓。
- 上一版（0.6.25）新增的棋子仍然保留：六色巨蚁、六色果冻、12 个地城终层首领、naga tidewarden／tidecaller、treant、shivgoroth 一对与重绘 Kryl-Feijan。

## 0.6.25 新增棋子

本轮无新增地形。新增 25 款怪物棋子（棋子目录 70→**95** 款）：

- **怪物 Batch D**：red jelly、blue jelly（补齐六色果冻族）；六色巨蚁全部上线——giant white／yellow ant 直接过审，giant brown／blue ant 经评审批准的底盘偏移豁免接入，giant carpenter／black ant 因原稿 48px 几乎无法区分被拒收后重新设计上线（象牙灰巨颚 vs 零反差暗色颚，仍是全库可分性最弱的一对，已如实记录为已知限制）。
- **怪物 Batch E**：12 个地城终层首领全部接入——Lady Zoisla the Tidebringer、Urkis the High Tempest、Golbug the Destroyer、Brotoq the Reaver、Ungolë、Half-Finished Bone Giant、Kryl-Feijan（后于 Batch F 重绘）、Atamathon the Giant Golem、Ritch Great Hive Mother、The Mouth、The Abomination、Celia；其中 7 款（Urkis、Golbug、Ungolë、Half-Finished Bone Giant、Kryl-Feijan、Atamathon、Ritch Great Hive Mother）经评审批准的底盘偏移豁免接入。Ungolë、Kryl-Feijan 是较暗的题材，已在真实地板 48px 下逐张确认未消失、保持可读。
- **怪物 Batch F**：naga tidewarden、naga tidecaller（自然生成）、treant 直接过审；shivgoroth、greater shivgoroth 一对经评审批准的底盘偏移豁免接入。Kryl-Feijan 重绘（原图 48px 深色地板下几乎读作纯黑团块，新图亮度提升 44%，明显改善，撤销原豁免）。xhaiak arachnomancer／shiaak venomblade 当时仅做运行时探针（已在 0.6.26 接入）。
- dremling 旧稿（暗底暗色）当时被评审拒绝；xhaiak arachnomancer／shiaak venomblade 当时未接入。以上三者已在 0.6.26 Batch G 重绘并接入，见上。

## 0.6.24 新增地形与棋子

**地形批次 4**：宁静的草原 L1–L6、孔克雷夫实验室 L1–L4（Kor'Pul 变体，区域墙、装饰地板与光环墙）、剧毒火山 L1–L2（丛林地、满格暗丛林树、毒水、岩墙与出口）、穆格尔巢穴 DEFAULT／INVASION 各 L1–L3（水下套件复用＋世界出口）、南方海滩 L1（沙地、深海、草地、树、石路、阳伞／篮子）。随后视觉返工：火山毒水改为平静暗绿浑水，丛林树与海滩树换新满格贴图，海滩沙地降饱和／对比。

**地形批次 5**：泰尔玛废墟 L1–L5、精灵废墟 L1–L3、沃尔军械库 L1–L2、布莱亚弗巢穴 L1、隐秘山谷洞穴 L1–L2、淹没的洞穴 L1–L2、造物者神庙 L1–L3、灼烧之痕 L1、恶魔空间 L1、夏·图尔堡垒 L1（仅 `SOLID_FLOOR`／`SOLID_WALL*` 与外围石墙；控制球、传送门、壁画、封门与改写楼梯保持原版）。无尽深渊格子不变。（源码同批还接入了兽人育种棚 L1 石质格及后续 L2–L3 `gloom/pit` 返工，但该地城在当前游戏中已不可进入，不计入本包覆盖范围。）

**拉克·肖部落**：L1–L3（骨质地面／墙／门、梯子与世界出口接入新 `rakshor` 组）；杠杆、杠杆门、封印宝库门、事件光环格与隐藏宝库入口保持原版。

新增 1 款怪物棋子（共 70 款）：skeleton master archer（黑漆金边重甲）。重绘 skeleton archer（正面直立持金弓）与 Horned Horror（浅色身体、品红触手冠、闪电拳套），提升与 degenerated skeleton archer、Minotaur of the Labyrinth 的可分性。

## 0.6.23 新增地形与棋子

混沌之沼 L1–L3、次元浮岛 L1–L3、时空裂隙 L1 接入虚空地面、平台与裂隙边缘；时空裂隙 L2–L4 复用已有石质、岩山与纳尔湖地表贴图。次元浮岛的焦树随浮岩显示；虫洞、移动平台的原生效果与剧情格保持原版。纳尔湖 DEFAULT／FLOODED 的 L2 与 FLOODED L3 普通水下格接入水下地板、墙、门与楼梯，DEFAULT L3 普通石质格复用既有贴图；空气泡、Sher'Tul 入口等特殊格保持原版。最后的希望墓地 L1 新增石路、沼泽树、墓碑与墓堂入口，L2 新增棺材（封闭／开启）贴图；墓碑与棺材的原生交互不变。混沌之沼与时空裂隙里的原生天气云在两种地形模式下都会显示成暗色方块，这是原版天气效果，本插件未改动。

新增 15 款怪物棋子（共 69 款）：Shax the Slimy、electric eel、ancient dragon turtle、Wrathroot、Snaproot、Horned Horror、Minotaur of the Labyrinth、Sandworm Queen、Corrupted Sand Wyrm、Rantha the Worm、Varsha the Writhing、Norgos the Frozen、Norgos the Guardian、skeleton archer、armoured skeleton warrior。黑暗之心的改名鼠／狼变体沿用对应基础棋子。skeleton master archer 及其他未核准的亡灵仍显示原版。

## 0.6.22 新增地形

里奇通道 L1–L3 接入沙地、稳定沙墙和楼梯；无尽深渊 L1–L3 接入地下地板、蔓延地、菌林墙和楼梯；最后的希望墓地 L1 草地与 L2 普通石质格接入，坟墓、棺材、陵寝及专有出口保持原版。魔法大爆炸之痕 L1–L2 接入焦土地面、可挖焦树、阻挡移动的熔岩潭和普通出口；祭坛及改写格保持原版。简化模式支持里奇通道、无尽深渊和魔法大爆炸之痕的上述非特殊格；墓地石质格保持原版。

## 0.6.21 新增地形

隐蔽的洞穴单层支持洞穴地板、可挖墙与世界出口。未知通道、风暴之巅、半身人废墟、瑞库纳与瑞库纳逃亡复用已核准的石质和岩山贴图。纳尔湖 DEFAULT／FLOODED 的 L1 地表、废弃地城 L1、荒芜废墟 L1–L3、黑暗地窖 L1–L5、傀儡墓地 L1、阿尔德胡格 L1–L3 也已接入。纳尔湖 L2–L3 的水下或干燥石质格未覆盖；法阵、封锁、传送门、石魔像雕像、虫洞、未确认出口及改写格继续原版。简化模式除原有范围外，支持隐蔽的洞穴和阿尔德胡格的洞穴格、墙与出口／梯子，以及风暴之巅的岩地与山墙；其他复用石质格继续原版。

## 0.6.20 新增地形

迷宫 DEFAULT L1–L2／COLLAPSED L1–L4 支持旧石地板、墙和裂隙。黑暗之心 gloomy／dreamy 各 L1–L3 支持地面、蔓延地、菌林墙与出口。沙虫巢穴 DEFAULT L1–L4／BIGWORM L1–L2 支持沙地、沙墙与出口。闪光洞穴 DEFAULT L1–L3／TWISTED L1–L5 支持晶地、晶墙与梯子。仅通过原生身份、来源及外观核对的格子会替换；密室、特殊改写格和其他未支持的地格保持原版。简化模式支持黑暗之心、沙虫巢穴、闪光洞穴的上述格子，迷宫石质格保持原版。

## 随机事件光环地格

原生随机事件在草地或石地周围改写地格名称并附加站立效果。精修地形现在继续绘制这些基础地格；原生粒子光环、地格提示名称、小地图颜色及站立效果仍保留。事件中心若变成特殊物件或熔岩，继续按原版显示。事件格现在默认使用柔和彩色边框，可在同一页的“事件光环地格”切换为适中强度；设置立即生效并保存。

## 诺尔格斯巢穴与岱卡拉地形（0.6.19）

诺尔格斯巢穴 DEFAULT／INVADED 两种布局的 L1–L3 使用雪岩地面、雪树和出口构件。岱卡拉 DEFAULT／VOLCANO 两种布局的 L1–L4 使用裸岩地面、连片山墙、雪树、出口和无害熔岩。精修模式显示选定棋盘图，简化模式显示占位棋盘图；未知或特殊格保持原版。岱卡拉火山末层中央熔岩格没有原生下楼交互，不画楼梯。

## Dreadfell 地形

Dreadfell 1–9 层的普通石地板、墙、硬墙、开闭门及上楼、下楼、世界出口复用 Kor'Pul 已验收的贴图。简化模式保留这些石格的原版画面；精修模式仅替换通过来源和最终状态核对的格。路牌、密室改写格及其他未支持身份保持原版。原生通行、视线、挖掘、门和楼梯规则不变。

## Rhaloren Camp 地形

Rhaloren Camp 的 DEFAULT／OVERGROUND 两种布局及各自 L1–L3 已接入。OVERGROUND 的露天草地和树木与建筑石地、墙、门可以在同一层同时显示棋盘贴图；两种布局的 L3 共用静态地图。未知或被密室改写的格子仍显示原版。简化模式只画森林格，石质格保留原版；精修模式同时覆盖合格的森林和石质格。原生通行、视线、挖掘、门与上下楼规则不变。

## Old Forest 与 Slazish Fens 地形（0.6.15）

Old Forest（等级 7–16）有两种布局：普通版（较暗的草地/树林）和水晶版
CRYSTALINE（较亮的草地/树林，部分楼层混有原版晶洞密室）；两种布局的 1–4 层
都已覆盖，草地和树木复用的是 Trollmire 已验收的贴图族（普通树、硬树各自独立
一张图）。第 4 层通往努尔湖（Lake of Nur）的特殊出口格保持原版。密室内容
（如蜂窝营地、强盗要塞等）保持原版，不受地形选项影响。

Slazish Fens（等级 1–7，仅东部“晨门”开局可见）三层全部覆盖，复用 Trollmire
洪水版的沼泽浅水、沼泽柳树和沼泽装饰贴图。唯一保留原版的是该区域末层的珊瑚
传送门（推动剧情用的谜题物件），这是设计决定，不是遗漏。

## 洪水沼泽版 Trollmire 地形（0.6.14 新增）

Trollmire 有两种布局：非洪水版（树林＋深水池塘）与**洪水版**（同一片林地被水淹没，
树变成站在水里的柳树，深水换成沼泽浅水）。此前精修地形只覆盖非洪水版，进入洪水版
会整层保留原版画面；现在两种布局**都**有精修美术：

- **沼泽柳树（bog-tree）**：洪水版里站在水中的树，画的是两款柳树构件之一（同一格
  重进不换图，两款按格子位置固定分配，纯为增加同片水域的视觉变化），底部随四周
  同类水体自动接岸/连通，和深水池塘的接岸逻辑一致。
- **沼泽浅水（bog）**：颜色比深水池塘浅、偏灰绿，不是深水的冷暗蓝绿，也不是原版
  毒水的黄绿色，一眼可辨。
- **沼泽装饰（bog-misc）**：贴着水面的芦苇丛/苔藓团/浮木三种矮装饰，不影响通行，
  不会被误认成矮墙、围栏或桥。
- **硬树（hardtree）**：洪水版和非洪水版共有的一种更密实厚重的树（原版规则上不能
  被普通挖掘打通、会挡感知），现在有自己的贴图，和普通橡树/松树/柳树能一眼区分；
  之前它借用普通树的画面，这次起两者不再共用同一张图。
- 藏宝图隐藏层（原版一路打通后触发的静态地图，两种布局共用同一张图，本身不含
  水域）与两种 Trollmire 的普通楼层用的是同一套身份识别逻辑，一并核实过。

洪水版某一格被原生"挖掘"（例如天赋、道具效果）打通后，画面会跟着原生规则自动从
柳树换成沼泽浅水，不需要重新进出楼层或切换选项。这条路径复用的是非洪水版树木被
挖掘后自动换成草地画面的同一套机制。

## 8 款胶质怪物棋子（果冻／软泥，0.6.13 新增）

green/black/white/yellow jelly（果冻，固定不动的圆丘状生物）与
black/yellow/red/blue ooze（软泥，会移动、受伤到一定程度有概率分裂出克隆体的
生物）共 8 款棋子，覆盖 46→54 款。果冻与软泥在剪影上刻意区分（果冻是对称、
居中、不带朝向的丘状体；软泥是低伏、带方向性伪足的流体），同色一对
（黑色果冻／黑色软泥）是该轮可分性最弱的一对，已如实记录，仍满足最低两维
差异要求。软泥的分裂是原生 `clone_on_hit` 机制，克隆体会各自获得独立的棋子
与阵营圆环，分裂状态本身不画进棋子图案。

## 施法光环下继续显示棋子

只要生物或玩家身上出现原生"光环"效果（如石肤 Stone Skin、化身火焰、反射护甲等天赋/效果自带的 shader 光环），棋子会围绕光环继续显示，不再让位退回原版画面；光环结束后棋子照常显示，圆环（阵营/生命/护盾）不受影响。这是纯视觉层面的修正，不改变光环本身的效果或数值。少数生物身上的光环（例如原版 Stone Skin 的水晶尖刺效果）本身在原版画面上也偏细微，肉眼不一定明显，属于该光环特效自身的表现，与本插件无关。

## 玩家角色棋子（默认开启）

主角（无论种族、职业）在按 **人类/精灵/矮人/半身人（男）/巨魔/羊足人/食尸鬼/骷髅/符文魔像** 这 13 个原生身体族出生时，会显示中性无装备造型的玩家棋子；半身人女性两次生图未能入库，暂时继续显示原版纸娃娃。开关在 **游戏选项 → 棋子颜色 → 玩家棋子（Player token）**，默认**开启**，独立于怪物棋子开关，可单独关闭以查看原版纸娃娃（含当前装备外观）。角色变身（如原生"化身古树"）等外部特效期间会自动让位给原生美术，特效结束后自动恢复棋子；换装不影响棋子外观，但关闭棋子开关后能看到最新装备的原版纸娃娃。

在 **棋子颜色 → 棋子朝向（Token facing）** 可选 **固定（Fixed）**（默认，棋子画面及绘制的光照方向固定）或 **跟随移动（Follow movement）**（沿用原生移动和攻击时的水平翻转）。此选项只影响已覆盖的生物/玩家棋子；其他外观保持原生朝向。切换后立即生效并保存。平滑移动和原生起伏仍由游戏本身的选项控制。反馈移动表现时，请写明所选模式及当时的操作。

0.6.8 起棋子直径在 48/64/96 三档地格下统一为同一比例，不再因体型分类出现三种不同大小。0.6.9–0.6.10 把怪物棋子从 37 款扩充到 46 款。0.6.11 修复了 Trollmire 精修地形在原生地图重铺（挖掘、天赋、传送门等）后偶尔永久退回原版贴图的问题，并清理了大量不再被引用的旧美术文件（不影响任何已生效的贴图）。

0.6.5 起让棋子、生命环、护盾和等级角标随原生起伏一起移动；没有新增走路帧。冲锋等动作仍保留原生主体残影，但不再复制多套状态环。单棋子疾滑、近战前探和传送新提示属于后续计划，本包尚未包含。

0.6.7 为设置页和颜色编辑器增加简繁中文。

0.6.6 修正了图片在压缩插件中的读取兼容性，解决精修地形在正式安装后可能变黑的问题。请用本次完整包替换旧版本。

`tome-board-hud.teaa` 是可选的独立插件，本包为 **0.2.7**（与上一轮外测包相同，未改动）。修复了中文模式下姓名、资源、属性、生物列表和日志中文字消失的问题，改用游戏的语言字体；Gold、六属性、导航及设置等自定义标题支持简繁中文。资源名称、数值和资源条合并为一行，长名称／数值换行保留，不缩小字体。创建、初始加点及开场说明期间不显示角色栏、快捷栏和日志／聊天，进入游戏后自动恢复。启用后，在 **游戏选项 → 用户界面 → HUD 风格** 中选择 **棋盘（Board）**，然后重启游戏使界面切换生效；不选择 Board 也可单独测试主插件。

**游戏选项 → 棋盘界面（Board HUD）** 集中提供快捷栏行数、图标大小、最小地图高度、右栏宽度、聊天可见性、战斗日志字号、日志／聊天分区、地图形状和小地图；不再在 Game Menu 中逐项列出。Board 下修改立即生效并保存，其他 HUD 下修改只保存 Board 偏好。旧配置继续有效，右栏宽度可选 Automatic 恢复自适应。测试时请按正常游戏操作，无需调试命令、作弊模式或专用存档。

小地图默认展开。点击地区名旁的 − 可以收起，为角色信息增加 **200px** 高度；+ 恢复展开，设置会保存。此操作不改变主地图大小。

棋盘地图是另一个选项：**游戏选项 → 棋子颜色 → 棋盘地形 → 精修**。在支持的地图中会立即刷新当前层，不必重新开局或上下楼。Trollmire（洪水版与非洪水版）、Old Forest（两种布局）、Slazish Fens、Rhaloren Camp（两种布局）、Dreadfell（九层）、诺尔格斯巢穴（双布局三层）、岱卡拉（双布局四层）、迷宫（双布局）、黑暗之心（双皮肤三层）、沙虫巢穴（双布局）、闪光洞穴（双布局）及上文 0.6.21／0.6.22／0.6.23 新增区域的受支持格现在都会刷新；其他未覆盖区域和特殊格子（如藏宝图关卡里的炖锅、未核准的地窖特殊格、Slazish Fens 末层的珊瑚传送门）保持原版。只切换 HUD Style 不会自动开启棋盘地形。

反馈时请附游戏版本、是否启用 Board、Token colors 各项设置（含玩家棋子开关）、角色种族/职业和区域（**若在 Trollmire 请注明是否为洪水版，若在 Old Forest 请注明是普通版还是水晶版**）、出现问题前的操作，以及能够说明问题的截图或日志。若出现移动视觉问题，注明普通移动、击退、冲刺还是传送，以及是否只在移动过程中出现。若出现光环相关问题，请注明触发的天赋/效果名称。
