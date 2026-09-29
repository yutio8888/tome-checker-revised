# 正式玩家棋子映射：实施方案（草案，待用户决策）

2026-09-28。只读调研产出（子代理起草，主代理抽查引用），**未改任何运行代码、未生图**。第 5 节的待决项确定前不进入实现。

## 0. 现状

- 普通玩家必走原生：玩家名由用户自取，`by_name` 查不到返回 `no-art`（`overload/mod/class/CheckerTokens.lua:95-96`）；即使查到，`moddable_tile` 也会被拒（`:115`）。
- `allow_player_identity`（`superload/mod/class/Game.lua:20-24`）只处理“被控制 NPC 带 `unique=="player"` 哨兵”的情况，与主角无关。
- 夹具演示棋子只在 `checker_hero` 显式开启且 `e==game.checker_hero` 时生效，夹具建角写死 Cornac/Male/Berserker。`data/gfx/hero.png` 带职业装备、无正式母版与溯源，只能继续作夹具用（`AGENTS.md`）。

## 1. 身份键：`descriptor.subrace × descriptor.sex`，与职业无关

- 字段：`actor.descriptor.subrace`、`actor.descriptor.sex`（`"Female"/"Male"`，出生同时拷贝 `female`/`male` 布尔，用于交叉核对）。
- 防护：`actor.moddable_tile` 须等于该亚种描述符的展开值（如 `human_#sex#`）；`has_custom_tile` 须为 nil（捐助者自定义贴图会清掉 `moddable_tile`）。
- 不按职业：原生职业差异全来自装备图层，换装不在当前范围。
- 本体亚种（`data/birth/descriptors.lua:370-378` 载入的种族文件）：分性别 7 个（Higher、Cornac、Shalore、Thalore、Dwarf、Halfling、Ogre），不分性别 4 个（Yeek、Ghoul、Skeleton、Runic Golem）；Lich 由转化得到（改写 `subrace` 与 `moddable_tile`）；教程亚种排除。按键计 18（含 Lich 19），按身体族（`moddable_tile`）只有 **14** 种。
- DLC（`game/dlcs/*.teaac`）：Doomelf、Drem、Krog、Orc（分性别），Whitehoof、Kruk Yeti（不分）；新身体族只有 orc 男女、whitehoof、yeti。
- 实现：映射表“键 → 图片 id”，允许多键共用一图；未列入的键一律原生。

## 2. 运行时合同

- 新增独立玩家表（`CheckerPlayerTokens.lua` 或 `CheckerTokens` 内独立 `M.player`），**不复用** `exactIdentity`/`appearance`（它们拒绝纸娃娃常态的 `moddable_tile`/`add_mos`）。`checkerRefreshActor` 开头加主角分支，id 用 `player:<key>` 命名空间。
- 同时满足才用：怪物棋子开关与新“玩家棋子”开关都开；`e == game.party:findMember{main=true}`（`class/Party.lua:164`，排除傀儡、召唤、thought-forms 复制体）；键在表内且性别、`moddable_tile`、`has_custom_tile` 校验通过；`replace_display` 为 nil 或为我方所装；无 `shader`/`anim`/`add_displays`/非空 `shader_auras`；非 ASCII（`Map.tiles.no_moddable_tiles` 为假）。
- 必须回退：TREE_OF_LIFE、TEMPORAL_FORM、各 LOSGOROTH/SHIVGOROTH/DEEPROCK 形态、LORD_OF_SKULLS 等设置 `replace_display` 的效果（现有归属判断会让出，效果结束后需实测自动装回）；其他插件的 `replace_display`；Lich 转化；自定义贴图；未映射 DLC 亚种。
- **必须修的缺陷**：棋子在场时 `updateModdableTilePrepare` 以我方 Entity 为 selfbase（`class/Actor.lua:4251`），换装后 `add_mos` 不更新；卸下玩家棋子时须显式 `e:updateModdableTile()`。
- 夹具 `--hero-token` 继续优先；`tests/runtime_modes.lua` 中“普通玩家不得用演示棋子”的断言改写为“开关关闭或键未映射时保持原生”＋“演示 hero 仅夹具”。
- 开关：`hooks/load.lua` 的 Token colors 标签页新增 “Player token”，`CheckerOptions` 新持久化键；文案走 `_t` 并同步简繁 locale。

## 3. 首批与预算

- 生产链路：`tools/art_tasks.py` 增 `kind:"player"` 与 `templates/player.txt`（中性站姿、朴素旅行服、无职业武器装备，盘面构图与风格门控同 creature）；`prepare_runtime_art.py`、`token-manifest.json`、`audit_dead_assets.py` 纳入玩家图。
- 最小首批：1 包 4 张（human 男女、elf 男女，覆盖 Cornac/Higher/Shalore/Thalore，Doomelf 可共用），上限 8 次调用，按历史约 5–6 次。
- 本体全量 14 张：4 包，上限 28 次，预计约 17 次；DLC 新身体族再 4 张，上限 8 次。不分性别则本体降到 9 张。

## 4. 验证计划

1. 单元：未映射键、自定义贴图、`moddable_tile` 被改、性别不一致、被控非主角、外部 `replace_display`、开关往返、卸下后纸娃娃重建。
2. 夹具：`launch_fixture.py` 增 `--birth Race:Subrace:Sex:Class`，经 `__module_extra_info` 传给夹具 Birther（需先确认锁定种族能否绕过离线解锁）。
3. 冷启动：每个已覆盖键至少一次，至少两个职业证明与职业无关；1920×1080、shader 开、48/64/96；核对同径、青色玩家环、护盾环。
4. 状态切换：施加／移除 TREE_OF_LIFE、TEMPORAL_FORM；Alchemist 傀儡控制切换；棋子在场换装后关开关核对纸娃娃；`becomeLich`；未映射 DLC 亚种保持原生。
5. 语言与持久化：新进程确认保存；简／繁／英文案。
6. 打包：`package_runtime.py`，PNG ZIP_STORED，TEAA 冷启动冒烟，升版本。

## 5. 待用户决定

1. 出图粒度：按身体族（14）还是按亚种（18）？例如 Higher 与 Cornac 是否共用、Doomelf 是否单独红肤。
2. 是否分性别出图。
3. 是否接受“中性无装备、不随职业/换装变化”的造型。
4. 玩家棋子开关默认开还是关。
5. Lich 与 DLC 是否纳入。
6. 首批授权的生图调用额度（建议首批 4 张、上限 8 次）。

## 6. 风险

- 纸娃娃 `add_mos` 残留（§2，必须修）。
- `shader_auras` 回退会让持续技能期间棋子与原生频繁切换；“保留棋子、光环叠加”需另立合同。
- DLC 可能改写描述符，需实机确认；完整读档从未测过，玩家 `_checker_token` 的序列化需单独验证。
- 无原生“中性单图”可对照，人类／精灵、矮人／Drem 的区分需按 48px 同族判据评审。
