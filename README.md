# Board Creatures & Terrain (tome-checker-revised)

《马基·埃亚尔的传说》（Tales of Maj'Eyal, ToME）桌面战棋风格视觉插件。将游戏内的生物与地形转换为战棋/桌游风格的棋子与棋盘地格，提供独立的战术状态指示与丰富的视觉自定义选项。

[English Summary](#english-summary)

---

## 插件介绍

本插件为 ToME 提供桌面战棋风格的视觉呈现：
- **怪物棋子**：将已核准的怪物替换为圆形桌面棋子。外环整合阵营与生命指示（友方绿色实线、中立蓝色虚线、敌方红色带四道缺口轮廓，玩家为青色圆环与白色内线；生命从正上方 12 点方向逆时针填充），外层带有独立的珍珠白护盾弧线；右上角显示清晰的等级徽记（稀有、独特、首领、精英首领、神祇；普通与精英怪物不加标记）。
- **棋盘地形**：在不改变游戏规则、视野与阻挡判定的前提下，将支持的地城、城镇与位面转换为高辨识度的棋盘地貌。
- **独立控制**：怪物棋子、棋盘地形与界面风格（HUD）完全独立，可自由搭配。

## 覆盖范围 (v0.6.31)

- **怪物棋子**：共收录 **376 款** 经过身份校验的怪物棋子（含首领、常驻怪群、召唤物与同体形复用规则）。未覆盖的生物与玩家炼金傀儡保留原版图像。
- **城镇覆盖（11 座城镇）**：德斯、伐木工人的小村庄、最后的希望、埃尔瓦拉、伊格、安格利文、钢铁议会、夏特尔、零点圣域、晨曦之门、伊尔克（包含支持的城镇道路、农田与棕榈树）。
- **地城与区域覆盖**：巨魔沼泽（含洪水版）、古老树林（含水晶版）、斯拉伊什沼泽、罗兰精灵营地（双布局）、恐惧王座、诺尔格斯巢穴（双布局）、岱卡拉（双布局）、迷宫（双布局）、黑暗之心（双皮肤）、沙虫巢穴（双布局）、里奇通道、深渊咆哮、最后的希望墓地、闪光洞穴、不起眼的洞穴、未知通道、风暴之巅、半身人废墟、瑞库纳·失落的矮人王国、从瑞库纳逃亡、纳尔湖（地表与水下/干燥石质格）、废弃地城、荒芜废墟、黑暗地宫、傀儡墓地、阿尔德胡格、魔法大爆炸之痕、混沌之沼、次元浮岛、时空裂隙（第一至第四层）、穆格尔巢穴、南方海滩、宁静的草地、剧毒火山、古老的孔克雷夫地下实验室、泰尔玛废墟、精灵废墟、沃尔军械库、布莱亚的巢穴、通往隐秘山谷的山洞、淹没的洞穴、造物者神庙、灼烧之痕、恶魔空间、夏·图尔堡垒、拉克·肖部落、卡·普尔废墟（双布局已支持格）、阴影地宫、泰恩之塔、伊塞尔森·月之谷、鲜血之环、艾露安、加伯特部落、巅峰、格鲁希纳克部落、史莱姆通道、淤泥巢穴、沃尔部落、教程（第一层）、梦境（第一层），以及时空避难所与梦境空间天赋位面。支持拉杆、拉杆门、阅读蜡烛、传送门与岩浆地面。

## 安装说明

1. 适用游戏版本：**Tales of Maj'Eyal 1.7.6**。
2. 将 `tome-checker-revised.teaa` 放入游戏安装目录下的 `game/addons/` 文件夹中。**请勿解压 `.teaa` 文件**。
3. 若使用外测压缩包（ZIP），解压后包含主插件 `tome-checker-revised.teaa`、可选界面插件 `tome-board-hud.teaa`、安装指南与 `SHA256SUMS` 校验文件。
4. 启动游戏并在插件列表中确认主插件已启用。建议使用新角色进入游戏。
5. 桌面界面插件 `tome-board-hud` 为独立的界面插件，可按需选装。
6. 详细步骤与校验说明请参阅 [外测安装说明](docs/external-test-v0630/INSTALL.zh-CN.md)。

## 游戏设置

在游戏内打开 **游戏选项 → 棋子颜色**（Game Options → Token colors）：
- **怪物棋子**（Creature tokens）：启用或禁用怪物棋子。
- **玩家棋子**（Player token）：可选中性主角棋子（按种族体型与性别匹配），不随装备或职业变化。
- **棋盘地形**（Board terrain）：在 **原版（Native）**、**简化（Blockout）** 与 **精修（Refined）** 三种模式之间循环切换。精修模式展示完整棋盘地貌。
- **棋子朝向**（Token facing）：**固定（Fixed）** 保持光照方向不变；**跟随移动（Follow movement）** 在移动或攻击时水平翻转。
- **事件光环地格**（Event aura grid）：在受支持的事件光环格显示 **柔和（Subtle）** 或 **适中（Moderate）** 边框。
- **颜色自定义**：支持通过 RGB 滑块调节等级徽记（稀有、独特、首领、精英首领、神祇）与阵营圆环（友方、中立、敌方）颜色，可一键 **恢复默认颜色**。所有配置即时生效并跨存档保存。

## 兼容性与已知限制

- **未覆盖模式**：本版本不含竞技场（Arena）与无尽地下城（Infinite Dungeon）。
- **保留原版画面**：永恒位面（Eidolon Plane）、星系（Stellar System）与梦境第二层（Dreams L2）保持原版；未覆盖的事件格、特定剧情传送门（如灼烧之痕远行传送门）保持原版。
- **存档范围**：旧存档中已生成的城镇与地层保持原版画面（需新进入对应区域）。
- **非全量替换**：未覆盖的怪物与实体（如玩家炼金傀儡）保留原版外观。

---

## English Summary

**Board Creatures & Terrain** (`tome-checker-revised`) transforms Tales of Maj'Eyal 1.7.6 into a tabletop board game aesthetic.

### Overview & Features
- **Creature Tokens**: 376 verified creature identities rendered as tabletop tokens with tactical rings (solid green friendly, dashed blue neutral, notched red hostile; player cyan ring with white inner line), radial counterclockwise health arc (filling from 12 o'clock), separate pearl-white shield arc, and distinct rank badges (Rare, Unique, Boss, Elite Boss, God; Normal and Elite remain unmarked).
- **Board Terrain**: Replaces grids across 11 towns, dozens of dungeons, and talent planes with clear tabletop tiles while fully preserving vanilla movement, line of sight, passability, and hazard rules. Supports Native, Blockout, and Refined terrain modes.
- **Independent Controls**: Creature tokens, board terrain, and the separate optional Board HUD (`tome-board-hud`) operate independently. Configure via **Game Options → Token colors**.

### Installation
1. Compatible with **Tales of Maj'Eyal 1.7.6**.
2. Place `tome-checker-revised.teaa` into the game's `game/addons/` directory. **Do not extract `.teaa` files**.
3. The external test ZIP package contains both `tome-checker-revised.teaa`, optional `tome-board-hud.teaa`, `INSTALL.zh-CN.md`, and `SHA256SUMS`.
4. Launch the game, verify the addon is enabled, and start with a new character.

### Known Limitations
- Arena and Infinite Dungeon are not covered in this release.
- Eidolon Plane, Stellar System, and Dreams level 2 remain native.
- Unsupported grids, event cells, specific story portals (e.g. Charred Scar farportal), and previously visited zones in existing saves keep native art.
- This addon is not a complete replacement of all game creatures; uncovered creatures and the player alchemist golem retain native art.

---

## 相关文档 / Links

- [更新日志 / CHANGELOG](CHANGELOG.md)
- [开发进度与验证 / PROGRESS](PROGRESS.md)
- [历史开发记录 / DEVLOG](DEVLOG.md)
- [外测安装说明 / Install Guide (zh-CN)](docs/external-test-v0630/INSTALL.zh-CN.md)
- [开源协议 / License (GPLv3)](COPYING)
