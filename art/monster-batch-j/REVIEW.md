# monster-batch-j 复核

## 2026-10-04 Lady Nashva 平面 token 重绘（v3，用户决定）

- 用户决定：Lady Nashva 的 `desc`（`game/modules/tome/data/zones/murgol-lair/npcs.lua:165`）写明 "Her dark tail is coiled tight, making her look short"，但现行 v2 平面 token 的蛇尾是中蓝绿色（审计 lower-tail median 68.4）。保留纳迦姿态、三叉戟、青色水纹与紧蜷尾，只把尾巴改成深蓝绿，并保持比 Lady Zoisla 的深色尾更偏蓝。
- 重绘包 `art/production/handoffs/lady-nashva-token-repaint-v1/`（`lady-nashva-token-repaint-v1`，gpt-6.1-sol、`--ephemeral`，attempt 1 即过门控；manifest `art/production/batches/lady-nashva-token-repaint-v1.json` 带 refinement 声明，supersedes 原 `monster-batch-j-4`）。
- 新母版 `art/monster-batch-j/masters/lady-nashva-v3.png`（sha256 `818099dd…`）；128px 门控 base_drift **-1.20**、最大不透明半径 0.8576、占格 0.8594、无警告。旧母版与旧运行 token 归档于 `art/monster-batch-j/superseded/lady-nashva-v2.png` 与 `.../lady-nashva-v2-runtime-128.png`。
- 外观：蛇尾为深蓝绿（尾区纯尾像素中位亮度 68.0→**46.6**，接近 native Nashva 48.9 与 Zoisla v3 的 43.1），带冷蓝高光与略浅蓝绿腹面；青色水纹收窄为细亮描边，不再像 v2 那样在尾下方形成亮池；上身蜜色皮肤、深紫黑发、银蓝额饰、蓝宝石胸衣、青色三叉戟照旧。
- 测量说明：审计用的是 128px「lower-centre box（x∈[0.28,0.72]·W、y∈[0.54,0.97]·H，opaque px）中位亮度」。该 box 约 60% 落在中性圆盘上，所以对 Nashva 这种尾盘较小的纳迦无法达到 Zoisla 的 47.5（Zoisla 的 box 里近八成是深色尾/体）；同口径下 v2→v3 从 68.3 降到 63.9，而纯尾像素从 61.8 降到 46.6。蓝度：v3 尾区 B−G=+2，Zoisla v3 为 −1，明显更蓝。
- 三尺寸（48/64/96、mid-brown 地板）对照图见 `art/token-layers/review-tokens/lady-nashva.png`（native／v2／v3＋desc 原文）。
