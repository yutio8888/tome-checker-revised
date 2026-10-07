# monster-batch-o 复核

## 2026-10-04 onilug 平面 token 重绘（v3，用户决定）

- 用户决定：onilug 的 `desc`（`game/modules/tome/data/general/npcs/minor-demon.lua:93`，"A gaunt vaguely humanoid shape ... Its arms and legs seem somehow too long and it stands tall, projecting an ominous shadow even in darkness."）与现行平面 token 冲突：v2 躯干宽壮、双腿短粗，与 gaunt、过长四肢不合。保留直立恶魔姿态、骨杖/紫晶与圆盘，只把身体改成瘦长、四肢过长。
- 重绘包 `art/production/handoffs/onilug-token-repaint-v1/`（`onilug-token-repaint-v1`，gpt-6.1-sol、`--ephemeral`，attempt 1 即过门控；manifest `art/production/batches/onilug-token-repaint-v1.json` 带 refinement 声明，supersedes 原 `monster-batch-o-7`）。
- 新母版 `art/monster-batch-o/masters/onilug-v3.png`（sha256 `c74ff15f…`）；128px 门控 base_drift **-0.31**、最大不透明半径 0.8585、占格 0.8594、无警告。旧母版与旧运行 token 归档于 `art/monster-batch-o/superseded/onilug-v2.png` 与 `.../onilug-v2-runtime-128.png`。
- 外观：灰皮革皮肤、太阳穴凹陷的窄躯干与过长细肢、大手大脚长爪、发光深红眼、骨杖与紫晶、破烂腰布；不再有宽壮短腿的体型。
- 三尺寸（48/64/96 真实尺寸、mid-brown 地板）对照图见 `art/token-layers/review-tokens/onilug.png`（native／v2／v3＋desc 原文）。
