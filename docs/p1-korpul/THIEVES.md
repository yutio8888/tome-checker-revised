# Kor’Pul HIDEOUT 四盗贼：身份、潜行与实机验收

**交付更新：** 0.6.1已完成四款接入、两变体原生候选审计和HIDEOUT实机对照，详见 [本轮证据](../../evidence/runtime-v061/README.md)。以下保留来源与测试方法。

本批目标是 `cutpurse`、`rogue`、`thief`、`bandit` 四个**精确身份**。依据是 0.6.0 的 [HIDEOUT 原生解析 TSV](../../evidence/runtime-v060/korpul-inventory-final-hideout.tsv) 和游戏原生 `/data/general/npcs/thieve.lua:62-110`，不是按名称猜测贴图。0.6.0 里四者均为 `fallback/no-art`；0.6.1 的接入和实机结果须另取证，不能把这份基线当作新版本结论。

| 身份 | HIDEOUT 来源 | 原生解析 `name / type / subtype / define_as / image` | 原生 Stealth | 场景注意 |
| --- | --- | --- | --- | --- |
| cutpurse | direct | `cutpurse / humanoid / human / 空 / npc/humanoid_human_cutpurse.png` | 无 `T_STEALTH` | 可见的四款基准；不要把它伪称潜行者。 |
| rogue | direct | `rogue / humanoid / human / 空 / npc/humanoid_human_rogue.png` | base 1，每 6 级增长，max 7 | 装配后记录天赋与实际 sustain，不能仅凭原型认定已潜行。 |
| thief | direct | `thief / humanoid / human / 空 / npc/humanoid_human_thief.png` | base 2，每 6 级增长，max 8 | 与条件房间、The Possessed 护卫的同名实体分开标记来源。 |
| bandit | direct | `bandit / humanoid / human / THIEF_BANDIT / npc/humanoid_human_bandit.png` | base 3，每 6 级增长，max 9 | `define_as` 只有此款；不要把 bandit lord 或 assassin 纳入映射。 |

四者都继承 `BASE_NPC_THIEF`：`resolvers.sustains_at_birth()`、双匕首与轻甲装配、开门能力和原生 AI。原生 Stealth 激活会改变 `stealth`、`lite`、`infravision` 与 `stealthed_prevents_targetting`，还会刷新可见性缓存。它是战术状态；token 只提供演员外观，不能借取消 sustain、改技能、强制显示或关闭可见性门控来制造整齐截图。玩家识破概率和 FOV 会影响画面：actor 在 TSV 中存在但截图中不可见，可以是**正确结果**。

NPC 原生 Stealth 不设置演员 `shader`；玩家的 `updateMainShader` 是另一条路径。故不能要求原生盗贼自带“潜行 shader”，也不能把空 shader 误判为潜行丢失。当前纯 Lua `tests/thief_visibility.lua` 已通过 20 项可见性门控检查；真实游戏里的潜行、识破及战术叠层仍以本轮实机记录为准。

## 独立夹具场景

`tests/live_thief_scene.lua` 仅供已启动的离线 checker fixture 加载。`enter(seed)` 生成真实 HIDEOUT 地图并保留未摆位样本；`stage()` 用当前活动区原型 `finishEntity` 构造四人、移除该次自然怪群、在原生可行走地板人工摆位并冻结 AI。它先将夹具英雄移到远处，让 `Zone:addEntity` 的原生 `on_added` 装配有机会自然启动 sustain，再把英雄移回取景中心；不调用技能来强迫潜行。它不改盗贼技能、sustain、装备、阵营、生命或地形规则。摆位图用于外观与状态对照，不是自然遭遇率证据。默认状态调用 `dump('baseline')` 输出 `/thief-scene-baseline.tsv` 和 `/thief-rules-baseline.txt`。

单独的 `setObservation('detected')` 只给夹具英雄临时增加原生 `esp.humanoid=1`，使用原生 `hero:canSee(actor)` 与 FOV 再观察潜行者；`dump('detected')` 输出 `/thief-scene-detected.tsv` 与 `/thief-rules-detected.txt`。这是**临时人形 ESP 识破**，不代表普通一级英雄自然识破；盗贼自身的潜行仍活动。首轮实测曾尝试 `see_stealth+1000`，概率仍仅约 94–96%，bandit 当次未被识破，所以该值不适合作为四款同时可见的确定性对照。`setObservation('baseline')` 撤回临时 ESP 并清理识破缓存。不能把 baseline 与 detected 写成同状态的原版／棋盘配对；每个状态内应各拍原版与棋盘，再比较。同一状态内的 actor 坐标、生命、天赋、`stealth` 与回合必须保持一致，`thief-rules-*.txt` 的逐字节哈希应相同。规则文件首行记录英雄坐标、生命、`see_stealth` 与 `esp.humanoid`；每位演员记录 `active_stealth`、`stealth`、`hero_can_see`、`see_chance`、`map_seens`、`map_infovs` 和 token。`canSee` 是原生缓存判定，切勿调用 `canSeeNoCache` 重抽结果。

截图前仅清理已知的测试入场对话与飘字；保留潜行特效、状态、地面效果、血环、角标和游戏日志。图片须是引擎直接输出的 1920×1080 PNG，保留原文件与 SHA-256，不裁切、拼接、修色或补画消失的角色。最小组是 baseline 64px 原版与棋盘、detected 64px 原版与棋盘，以及 detected 96/48px 棋盘，共六张。若 baseline 中三名潜行者已被自然识破，仍记录实际结果，不声称“潜行不可见”已验证。若侦测增强仍不能识破，记录 `hero_can_see=false` 和现场原因，不把空格认作贴图故障。

最终 `capture-thieves.json` 的每张图应有 `phase`（`baseline`/`detected`）、`visibility_expected`（由该次 TSV 中 `hero_can_see` 与 `map_seens` 给出）、`actor_state_tsv`、`source_kind=arranged`、模式、tile、布局、层号、输入 seed、回合、1920×1080 分辨率、原图 SHA-256 和 `edited=false`。detected 阶段须断言四名的原生 `canSee=true` 且概率 100%，并与 baseline 比对盗贼潜行属性及 sustain 不变。另保留未摆位 `natural` TSV；这和四名摆位演员的存在不能混写。最终报告逐人列出身份命中、原生图、token、实际 sustain/识破和回退原因；任何图片上缺席的潜行者须对照原生 `hero_can_see` 解释。0.6.0 的两版 TSV 表明同四名在 DEFAULT 仅是 `shared-import` 候选，在 HIDEOUT 才是 `direct`，不能据此推出 DEFAULT 自然生成概率。
