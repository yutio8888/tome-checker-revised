# player-tokens-v1 生成与验收记录

批次：`art/production/handoffs/player-tokens-v1-{human-elf,dwarf-halfling,ogre-yeek,ghoul-skeleton-golem}`，
共 14 个原生体型家族资产，`max_attempts=2`，预算上限 28 次调用。本轮实际消耗
**16 次**，13 个资产入库，1 个资产（halfling_female）预算耗尽仍未产出，保留原生贴图。

角色/工具背景见 `art/player-tokens-v1/BRIEF.md`、`docs/handoff-20260927/HANDOFF.md` §六。
所有数值均来自 `tools/check_token_style.py` 对 128px 导出件的机器判定（母版偏移中位、
最大不透明半径、128px 可见占格），未经人工目测调整；`passed` 为该次调用的门控总判定。

## 逐资产记录

| 资产 | 调用次数 | 结果 | base_drift | max_radius (≤0.867) | occupancy (0.83–0.91) |
| --- | --- | --- | --- | --- | --- |
| human_male | 1/2 | 通过 | +2.12 | 0.8576 | 0.8594 |
| human_female | 1/2 | 通过 | +0.41 | 0.8576 | 0.8594 |
| elf_male | 2/2 | 通过（见下） | -1.83 (call-1) | 0.8576 | 0.8594 |
| elf_female | 1/2 | 通过 | -2.49 | 0.8576 | 0.8594 |
| dwarf_male | 1/2 | 通过 | -1.31 | 0.8585 | 0.8594 |
| dwarf_female | 1/2 | 通过 | -1.32 | 0.8576 | 0.8594 |
| halfling_male | 1/2 | 通过 | -0.60 | 0.8576 | 0.8594 |
| halfling_female | 2/2 | **失败** | — | — | — |
| ogre_male | 1/2 | 通过 | -4.53 | 0.8576 | 0.8594 |
| ogre_female | 1/2 | 通过 | -1.24 | 0.8576 | 0.8594 |
| yeek | 1/2 | 通过 | +0.15 | 0.8596 | 0.8594 |
| ghoul | 1/2 | 通过 | -0.75 | 0.8559 | 0.8594 |
| skeleton | 1/2 | 通过 | -2.37 | 0.8585 | 0.8594 |
| runic_golem | 1/2 | 通过 | -4.24 | 0.8576 | 0.8594 |

容差：`base_drift` ±8、`max_radius` ≤0.867、`export_occupancy` 0.83–0.91；14 个资产的每一次
成功调用在这三项及母版 alpha／四角透明检查上全部通过，无一次因风格门控被拒。

### elf_male：预算记账事故（操作失误，非画面问题）

第一次调用（call-1）本身通过了溯源、母版 alpha 和风格门控（`base_drift -1.83`），但操作方
（本 agent）误用 shell `&` 把该调用放到后台后过早判定其"已终止"，实际上该进程仍在容器内
继续运行并最终正常完成、正常入库（`outcome: recorded`）。在此期间操作方又发起了第二次
`generate`（call-2），两次调用发生竞争：call-2 在尝试写入 `receipts/attempt-1.json` 时，
call-1 已经写入过，被 `art_tasks.py record` 的"序号必须连续、不可覆盖"检查拒收
（`record-rejected`）。**该资产的最终产物来自 call-1，图像本身没有问题**，但因为这次操作
失误，elf_male 的 2 次预算在第一个资产上就用完了（`calls_used=2, calls_left=0`），后续如果
它需要返修将没有额度。这是本轮唯一的记账浪费，原因是后台调用方式使用不当，不是生成链路
或风格门控的缺陷；后续同类调用一律改为直接前台调用、让 harness 自动转后台并等待完成通知，
不再手工 `&`。

### halfling_female：两次调用均溯源失败（已知失败模式的另一种表现）

两次调用都在 codex 阶段就失败：`溯源校验不通过：codex 未返回产物路径`——即内置
ImageGen 这两次都没有产出任何图像文件（不是产出了错误画面，也不是 RGB/棋盘格伪透明），
所以连母版 alpha 检查都没有机会跑。预算已耗尽（2/2），本轮不再有调用额度，
该家族保留原生贴图，`data/player-token-manifest.lua` 中不列出 `halfling_female`。
这不是画面质量问题，是生成调用本身的失败；未使用任何变通手段（未开新目录、未加
`--force`、未开新批次）。

## 可分离性目测记录（128px 导出件，Read 工具单次查看）

- **human vs elf**：human 肩宽更厚、圆耳；elf 更瘦长、耳尖在发际线外可见但因头发遮挡，在
  48px 缩略图上不如躯干比例差异明显——躯干比例是主要可分离特征，耳形是次要特征，符合预期。
- **dwarf vs halfling（仅 male 有对照，female 缺失）**：dwarf_male 明显更矮壮、有胡须；
  halfling_male 头身比例更大、无胡须、体积更小，两者在 48px 灰度下不会混淆。dwarf_female
  与 halfling_female 的对照因后者失败而无法验证。
- **male vs female**（human/elf/dwarf/ogre 四对）：肩腰比例、发型轮廓均有区分，不只是配色
  差异，符合要求。
- **ghoul / skeleton / runic_golem**：三者在 96px 单独看时分色到位（ghoul 斑驳绿棕、
  skeleton 苍白骨白、runic_golem 中灰石纹带刻线），但在 `compare-gray.png` 的 **48px 行**
  三者的灰度明度彼此接近、轮廓都偏"人形深色块"，仅从缩略图快速一瞥不如其他家族好分——
  这是一个主观目测提示，风格门控的机器指标（value/occupancy/radius）三者均独立通过，
  没有量化的可分离性判据可引用；建议后续如需更强区分可考虑单独复测，但本轮未发现任何一
  项机器可判定的失败，未发起额外返修。
- 未见任何持械、错误种族、超出圆盘边缘或双人构图的问题；13 个入库资产的 128px 导出件目视
  均为单个平静站姿、无武器、着装简朴的人形/兽形。

## 产物与运行时接入

- 母版：`art/player-tokens-v1/masters/<family>-v1.png`（13 个，1254x1254 RGBA）。
- 运行时贴图：`data/gfx/tokens/player-<family>.png`（13 个，128x128），用与怪物棋子相同的
  `tools/bin/export_token`（`tools/export_token.c` 编译产物）从对应母版直接导出，导出参数
  （`export_window`/`visible_bbox`）与门控阶段记录的临时导出件完全一致，字节确定性可复现。
- 清单：`data/player-token-manifest.lua`，`revision='players-v1'`，列出 13 个通过家族；
  `halfling_female` 未列入，保留原生贴图（`CheckerPlayerTokens.lua` 的清单门控本身即已覆盖
  "未列出=原生"这一路径，无需额外代码改动）。
- 测试：`lua5.1 tests/player_tokens.lua`（129 项通过）、`lua5.1 tests/token_mapping.lua`
  （1612 项通过）均绿。
- 死资产审计：`python3 tools/audit_dead_assets.py --check` 最初把全部 13 个新贴图判为死
  资产，因为审计脚本原先只从两个测试文件里的字面量识别到 `player-human_male.png` 和
  `player-halfling_male.png` 两个路径，没有从 `CheckerPlayerTokens.lua` 的真实清单门控逻辑
  推导可达集合。按任务要求，对审计脚本做了最小修改：新增 `player_token_paths()`，用真实的
  `fs.exists`/`loadfile`（映射到本仓库实际 `data/` 目录，而不是测试用的内存桩）执行
  `CheckerPlayerTokens.lua` 本体，读取真实的 `data/player-token-manifest.lua`，对
  `M.available` 里的每个家族调用 `M.image()`，与怪物棋子已有的 `token_paths()` 手法一致。
  修改后 `--check` 输出 `reachable token:player 13`，`dead assets: none`，退出码 0。

## 调用预算汇总

| 阶段 | 调用次数 |
| --- | --- |
| human-elf（4 资产） | 5（elf_male 记账事故多耗 1 次） |
| dwarf-halfling（4 资产） | 5（含 halfling_female 失败的 2 次） |
| ogre-yeek（3 资产） | 3 |
| ghoul-skeleton-golem（3 资产） | 3 |
| **合计** | **16 / 28** |

13/14 资产入库，1/14（halfling_female）失败保留原生贴图。未使用任何超出
`max_attempts` 的变通手段。
