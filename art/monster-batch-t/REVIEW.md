# monster-batch-t 复核

## 2026-10-04 Slasul 平面 token 重绘（v2，用户决定）

- 用户决定：Slasul 的 `desc`（`game/modules/tome/data/zones/temple-of-creation/npcs.lua:33`，"His torso is bare apart from an exquisite pearl set directly in his chest, and in his muscular arms he holds ready a heavy mace and shield."）与现行平面 token 冲突：v1 上身是一整套金色胸甲/胸铠，把裸胸与胸中珍珠盖住。保留蛇尾纳迦姿态、冠盔、圆盾与大锤，只把躯干改回裸胸并露出珍珠。
- 重绘包 `art/production/handoffs/slasul-token-repaint-v1/`（`slasul-token-repaint-v1`，gpt-6.1-sol、`--ephemeral`；call-1 因本机 codex 认证缺失返回 401、无产物，call-2 attempt 1 过门控；manifest `art/production/batches/slasul-token-repaint-v1.json` 带 refinement 声明，supersedes 原 `monster-batch-t-3`）。
- 新母版 `art/monster-batch-t/masters/slasul-v2.png`（sha256 `497a28a3…`）；128px 门控 base_drift **-0.43**、最大不透明半径 0.8585、占格 0.8594、无警告。旧母版与旧运行 token 归档于 `art/monster-batch-t/superseded/slasul-v1.png` 与 `.../slasul-v1-runtime-128.png`。
- 外观：裸胸蜜色皮肤上有大片浅色高光面，胸口正中一颗白色珍珠，金冠盔、金臂环、圆盾与大锤照旧，海绿蛇尾盘成圆座；不再有胸甲。
- 三尺寸（48/64/96 真实尺寸、mid-brown 地板）对照图见 `art/token-layers/review-tokens/slasul.png`（native／v1／v2＋desc 原文）。
