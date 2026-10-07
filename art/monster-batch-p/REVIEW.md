# monster-batch-p 复核

## 2026-10-05 ogre-mauler 平面 token 重绘（v2，用户决定）

- 用户决定：ogre mauler 的 NPC 装备是双手巨槌 —— `game/modules/tome/data/general/npcs/ogre.lua:95` `resolvers.equip{{type="weapon", subtype="greatmaul", ...}}`（同定义 `desc` 在 `ogre.lua:88`，"Crush! Destroy! Maim!"）——但现行平面 token（v1）画的是抬起的金色护手／拳头，完全没有武器；同一身份已验收的立绘 `art/token-layers/ogre-mauler/standee/master-v1.png` 握着一把大型双手巨槌。保留蜷伏姿态族、砖红皮肤、暗红乱发、棕色腰布、圆盘与镜头，只把护手替换成和立绘一致的双手巨槌。
- 重绘包 `art/production/handoffs/ogre-mauler-token-repaint-v1/`（`ogre-mauler-token-repaint-v1`，gpt-6.1-sol、`--ephemeral`，attempt 1 即过门控；manifest `art/production/batches/ogre-mauler-token-repaint-v1.json` 带 refinement 声明，supersedes 原 `monster-batch-p-3`）。
- 新母版 `art/monster-batch-p/masters/ogre-mauler-v2.png`（sha256 `e71d829a…`）；128px 门控 base_drift **-6.12**、最大不透明半径 0.8576、占格 0.8594、无警告、无豁免。旧母版与旧运行 token 归档于 `art/monster-batch-p/superseded/ogre-mauler-v1.png` 与 `.../ogre-mauler-v1-runtime-128.png`。
- 外观：砖红皮肤、暗红乱发、裸胸伤痕、棕色腰布与獠牙照旧；双手握住一根深棕木柄，槌头是带铆钉与铁箍的方形石／铁块，低垂在膝盖旁，明显是双手重槌而非单手锤，保持与 ogre-guard 的区别。128px 主体中位亮度 63.61→**63.9**（floor 45，远高于下限）。
- 三尺寸（48/64/96、mid-brown 地板）对照图见 `art/token-layers/review-tokens/ogre-mauler.png`（native／v1／v2／standee＋desc 与 equip 行原文）。
