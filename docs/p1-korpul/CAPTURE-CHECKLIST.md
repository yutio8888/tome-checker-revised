# Kor'Pul P1 双布局实机取证清单

此清单供主代理在**独立离线夹具**取证并发送实机截图。当前无本轮 TSV 或截图结论；完成截图后再填写实际结果。源码候选、脱离地图的 `finishEntity`、场景摆位和未摆位自然生成应分别标注，不能互称为自然遭遇率。身份与房间来源见 [INVENTORY.md](INVENTORY.md)。

## 输入与报告

对当前 `ruins-kor-pul` 的 DEFAULT、HIDEOUT 分别运行 `tests/live_korpul_inventory.lua`，文件名包含布局、层号与运行标识。脚本要求 cheat、offline、`checker_demo` 和 `checker_staged`，只解析当前活动区候选的脱离地图副本；会消费 RNG/UID，不应在常规存档运行。保存原始 TSV，然后运行：

```sh
python3 tools/report_korpul_inventory.py path/to/korpul-default.tsv path/to/korpul-hideout.tsv > path/to/inventory-summary.md
```

报告中的 `EXACT` 仅表示该 TSV 行有真实原生解析体、预期的 `name/type/subtype/define_as`、对应 token 与 `exact-identity` 原因；`EXPECTED_NATIVE_FALLBACK` 表示预期暂未接入的身份保留原生显示。`NO_TSV_ROW`、`REVIEW` 或未解析行须逐项说明。两版四盗贼和各自首领目前预期回退；若后续版本明确加入映射，应按新版本的实际契约重新评估，不能沿用本清单的预期。房间是否出现、Possessed 的 thief 护卫是否生成、自然生成频率，TSV 都不能证明。

## 截图组

每张截图使用真实游戏 C 渲染原图，不裁切、不拼接、不后处理。记录当前 addon/游戏版本、布局、层号、seed、角色/区域等级、坐标、回合、tile 尺寸、原生/棋盘模式和 shader 状态；同一对照在**同布局同坐标同状态同回合**完成。DEFAULT 与 HIDEOUT 分开保存，不假设相同 seed 有相同地图。

| 布局 | 必需取景 | 核查点 | 结果填写 |
| --- | --- | --- | --- |
| DEFAULT | 首四怪固定摆位，原生与棋盘各在 48/64/96px；另留一份未摆位种子 | warrior 单臂大剑、archer 弓与缺手腕、mage 杖与暗披布、grey mold 低矮演员盘；按 TSV 对照精确身份与回退。未摆位样本只记实际遇见者。 | 待实机 |
| HIDEOUT | 四盗贼固定摆位，原生与棋盘各在 48/64/96px；另留一份未摆位种子 | cutpurse/rogue/thief/bandit 分别记录原生 `image`、潜行/状态层及预期回退；共享 `all.lua` 骷髅候选不能写成必然出现。 | 待实机 |
| DEFAULT | 末层 The Shade，至少 64px 原生与棋盘同状态对照 | `unique_glow`、首领身份、层叠、rank/血量/护盾；当前预期保留原生。 | 待实机 |
| HIDEOUT | 末层 The Possessed 与实际生成的 thief 护卫，至少 64px 原生与棋盘同状态对照 | 首领 `invis.png`＋高两格 `add_mos`、护卫独立身份/阵营/rank；若护卫未出现，记未验证。 | 待实机 |
| 两版各自 | 普通走廊、转角、单格门口、可挖墙和普通地面装饰；开门前后、挖掘前后、迷雾记忆各一组 | 6 项石质母版、门状态/邻接、碰撞与视线、已见/未见区域；变化前后记录回合，不能用贴图推断规则。 | 待实机 |
| 两版各自 | 实际触发的 lesser-vault 房间（如有） | 标明六种房间中的哪一种、实际抽中怪群及等级偏移；未抽中记“未验证”。 | 待实机 |

为便于送审，最小常规组为每布局 48/64/96px 的原生与棋盘配对（12 张），另补两版首领、护卫及门/挖掘/迷雾的关键帧。棋子有圈与遮圈、Board 与原生 Minimalist、48/64/96px 识别，应至少各有能实际判断的代表图；无法一帧容纳时增加取景并在记录中指明关系。未支持地形/Actor 的回退也要留一张可核对的图。

## 截图清单与发送材料

参照 `evidence/runtime-v052/capture.json` 的 `runtime`、`edited`、`shots[]`、`file`、`resolution`、`tile`、`sha256`，本轮每条 `shots[]` 再写 `zone="ruins-kor-pul"`、`layout`、`level`、`seed`、`turn`、`x/y`、`mode`、`renderer`、`subjects`、`source_kind`（`staged`、`natural`、`fixed-boss`、`room` 或 `escort`）。相对文件路径须指向随包原图；发送前核对每张图的 SHA-256 与实际文件、截图数量及清单文件名。不要把审阅拼图代替原始截图。

发送材料包括两版原始 TSV、`inventory-summary.md`、`capture.json`、原始截图和简短结果说明。结果说明分别列：首四怪的原生解析/精确命中；两版四盗贼与首领的实际回退；触发与未触发房间；实际生成与未生成护卫；未摆位自然遭遇样本；以及地形状态和任何回退原因。发送方式由主代理负责；本清单不含收件地址或凭据。
