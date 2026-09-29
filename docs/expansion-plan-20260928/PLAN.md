# 扩充计划（2026-09-28，基于 0.6.12 多地图巡检）

数据来源：[evidence/map-survey-20260928](../../evidence/map-survey-20260928/README.md)。18 个区域／层、557 个生物：320 个已映射（43 款），237 个未映射，共 95 个独立身份，原因全部是 `no-art`，没有显示故障。本计划取代 `docs/completion-plan-20260927/` 的 33 款数量口径；该文档中的区域清单仍可参考。

## 原则

- 每批沿用现有链路：先做**生成前准入**（隔离夹具中实例化，核对 `add_mos`／`add_displays`／`shader`／`anim`／`textures`／`replace_display`／`moddable_tile`／`unique`，参照 `evidence/c0b-art-gate`），再建任务包、预演，由主代理审完提示词后才真实生图。每款 `max_attempts=2`，任务包最多 4 款。
- 按**同族成批**：同一批内完成两维可分性评审（剪影＋明暗，48px 灰度）。
- 风格门控、冻结基线、`target_occupancy` 一律不改；不做整个亚类的替换，只按精确身份映射。
- 执行分工：准入、任务包、生图驱动、打包交 sonnet，生图本身走 codex；主代理负责审提示词、看图验收、提交。

## 怪物批次（按出现范围与数量排序）

| 批次 | 身份 | 出现区域 | 备注 |
| --- | --- | --- | --- |
| **E1 胶质** | green／black／white／yellow jelly；black／yellow／red／blue ooze | Maze、Norgos、Sandworm、洪水 Trollmire 等 7 区 | 数量最多、跨区最广。jelly 固定不动、ooze 会移动，形态必须明显不同；同类之间不能只靠颜色区分（表面质感、形状、核心）。另有 green ooze、red jelly、blue jelly、crimson ooze、gelatinous cube 延入 E1b |
| **E2 早期亡灵** | skeleton magus、skeleton archer、armoured skeleton warrior、skeleton master archer、ghoul、ghast | Dreadfell、Unremarkable Cave、Ancient Elven Ruins、Daikara | 已有 skeleton warrior、skeleton mage、degenerated skeleton warrior 作为同族锚点；ghoul 要与玩家 ghoul 棋子区分 |
| **E3 Rhaloren 营地与蚁类** | elven guard、mean looking elven guard、elven mage、elven tempest；giant white／carpenter／black／yellow ant | Rhaloren Camp、Old Forest、Kor'Pul HIDEOUT | 精灵 NPC 要与玩家 elf 棋子区分（装备与姿态） |
| **E4 沙虫与 Heart of the Gloom** | sandworm、sandworm burrower、sandworm destroyer；sick／gloomy／deformed 系鼠兔、gloomy wolf | Sandworm Lair、Heart of the Gloom | 病变系是已映射鼠类的变体，要确认是否只是改名，按改名身份的溯源路径处理，不要重复出图 |
| E5 植物与晶体 | poison ivy、honey tree、white／red／crimson crystal、elemental crystal | Trollmire、Old Forest、Scintillating Caves | 固定物体，先核实显示合同 |
| E6 城镇 NPC | human farmer、halfling gardener | Derth | 优先级低 |
| 暂缓 | dremling／drem 系（`invis.png` 组合身份）、各类首领／唯一、shivgoroth（元素形态） | Maze、Norgos | 需要单独的外观合同 |

## 变体同步原则（2026-09-28 用户要求）

已支持的地城，其布局变体必须一并支持，不能只覆盖默认布局。现状：Kor'Pul DEFAULT／HIDEOUT 均已支持；Trollmire FLOODED 整区原生（原因见下）；Trollmire 第 4 层的静态宝藏图（`zones/trollmire-treasure`）尚未核对。

**F1 洪水 Trollmire**（排在 G0 导出器之后，优先于其他地形套件）：
- 地形：新增三个身份，分别是 `BOGTREE`（水中柳树，`subtype="water"`、`shader="water"`、可挖成 BOGWATER）、`BOGWATER`（已有 64 张 `refined/bog*` 瓦片，从未实机启用，需复审）、`BOGWATER_MISC`（7 种水面装饰，纯显示）。按身份显式加入分类，不得放宽 `subtype=='water'`；水体掩码写死为“同种水”。精修和 blockout 两种模式都要支持。
- 怪物：该布局主要共用 vermin／troll／snake／plant／swarm／bear 族（多数已映射），另有 `aquatic_critter`（如 electric eel）与守关首领 Shax the Slimy，并入怪物批次。
- 门控：删除 `CheckerTerrain.lua:54` 的 `not is_flooded`，改为按身份判定。

## 地形线（G0）

1. **森林／水体导出器**（硬阻塞，见 HANDOFF §八.2）：按 `docs/g0-terrain-contract-20260927/ACCEPTANCE.md` 的 A4–A6 先写导出器，再出新母版。
2. 道路压实泥纹理；森林东西向通路与世界出口拆分。
3. 方案 B：森林迁到逐格适配器，并扩充 `markSource` 白名单。
4. 下一个地形套件候选：Norgos Lair／Old Forest（森林系，复用导出器）。

## 近期顺序

1. E1 胶质（8 款，上限 16 次调用）← **本轮开始**
2. E2 早期亡灵
3. 并行准备 G0 导出器（纯工具，不生图）
4. E3 → E4 → E5，每批结束后打一个小版本，并用 TEAA 做冒烟测试
