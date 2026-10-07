# monster-batch-ac 复核

## 2026-10-04 abyssal horror 平面 token 重绘（v2，用户决定）

- 用户决定：abyssal horror 的 `desc`（`game/modules/tome/data/general/npcs/horror_aquatic.lua:194`，"This pitch black form is shrouded in darkness. All you can make out are a pair of deep red eyes, hidden behind a mass of tentacles."）与现行平面 token 冲突：v1 是明亮蓝紫色、多眼触手团（其参考注甚至写着 "instead of black"）。保留触手团姿态家族，只把体色改为漆黑、眼睛改为唯一一对深红眼。
- 重绘包 `art/production/handoffs/abyssal-horror-token-repaint-v1/`（`abyssal-horror-token-repaint-v1`，gpt-6.1-sol、`--ephemeral`；call-1 溯源拒绝无产物，call-2 attempt 1 过门控；manifest `art/production/batches/abyssal-horror-token-repaint-v1.json` 带 refinement 声明，supersedes 原 `monster-batch-ac-4`）。
- 新母版 `art/monster-batch-ac/masters/abyssal-horror-v2.png`（sha256 `26cbc4cf…`）；128px 门控 base_drift **-2.63**、最大不透明半径 0.8576、占格 0.8594、无警告。旧母版与旧运行 token 归档于 `art/monster-batch-ac/superseded/abyssal-horror-v1.png` 与 `.../abyssal-horror-v1-runtime-128.png`。
- 外观：漆黑近黑墨紫/炭色触手团，湿深紫高光与冷灰蓝边缘光；唯一一对深红细缝眼藏在触手之间，无其它眼睛、无粉/橙光点。dark-subject 可读性靠内部浅灰吸盘与边缘光，48/64/96px 均可辨。
- 三尺寸（48/64/96 真实尺寸、mid-brown 地板）对照图见 `art/token-layers/review-tokens/abyssal-horror.png`（native／v1／v2＋desc 原文）。
- 本目录 `review/` 下 2026-09-30 的家族图与 `luminance.json` 是 v1 的历史记录，未重跑；v2 为刻意的黑色主体，其可读性以 `abyssal-horror.png` 对照图与门控为准。
