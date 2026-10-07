# Monster batch A — offline art review

All 13 identities were checked against native source before generation. The original sources, prompt packs, reference hashes, 21 ImageGen call ledgers and byte-identical 21 masters are under `art/production/handoffs/monster-batch-a-*` and `art/monster-batch-a/masters`. No game fixture was launched in this task.

Selected review sheets: [color](review/selected-color-48-64-96.png), [grayscale](review/selected-grayscale-48-64-96.png). The [first pass sheet](first-pass-sheet.png) includes rejected attempts; it is not the selected catalog.

| Identity | Calls | Selected master | 128px gate |
| --- | ---: | --- | --- |
| Shax the Slimy | 2 | native fallback | call 1: style-gate-rejected; call 2: style-gate-rejected |
| Wrathroot | 2 | `masters/wrathroot-v2.png` | exact-byte base drift waiver |
| Snaproot | 2 | `masters/snaproot-v2.png` | passed |
| Horned Horror | 2 | native fallback | call 1: style-gate-rejected; call 2: style-gate-rejected |
| Minotaur of the Labyrinth | 1 | `masters/minotaur-maze-v1.png` | passed |
| Sandworm Queen | 1 | `masters/sandworm-queen-v1.png` | passed |
| Corrupted Sand Wyrm | 1 | `masters/corrupted-sand-wyrm-v1.png` | passed |
| Rantha the Worm | 2 | `masters/rantha-v1.png` | exact-byte base drift waiver |
| Varsha the Writhing | 2 | `masters/varsha-v1.png` | exact-byte base drift waiver |
| Norgos, the Frozen | 2 | `masters/norgos-frozen-v1.png` | exact-byte base drift waiver |
| Norgos, the Guardian | 2 | native fallback | call 1: style-gate-rejected; call 2: style-gate-rejected |
| electric eel | 1 | `masters/electric-eel-v1.png` | passed |
| ancient dragon turtle | 1 | `masters/ancient-dragon-turtle-v1.png` | passed |

The four waivers in `art/production/waivers/monster-batch-a.json` bind the master and selected 128px PNG SHA256 values and cover only `base_drift`. Global thresholds stay unchanged. Measured drifts: Wrathroot −9.77, Rantha −8.31, Varsha −10.58, Frozen Norgos +8.63 (limit ±8). All other blocking checks pass. Shax, Horned Horror, and Guardian Norgos exhausted their two calls; they remain native.

The wrapper rejected first attempts before creating an `art_tasks.py` receipt. Their byte-identical masters were recorded solely to unlock the existing second-attempt repair path; the call ledgers retain the failed style results. None of those receipts was treated as a selected export. The treant repairs used visual reviews of the 48/64/96px first-pass sheet; the other repairs used the wrapper's explicitly marked metric reviews.

At 48/64/96px the selected silhouettes remain legible: drooping pale willow versus forked charred treant; segmented round Sandworm Queen versus narrow clawed sand wyrm; tall narrow ice dragon versus lower wide fire dragon; sharply bent electric eel versus the existing broad giant eel; ancient ridged turtle versus the existing smoother dragon turtle. Snaproot and Varsha are the darkest selected bodies and need special attention in the live shader check.

No live actor, shader, saved-setting, full-save, or TEAA claim is made here.

## 2026-10-04 Snaproot 平面 token 重绘（v4，用户决定）

- 用户决定：Snaproot 的 `desc`（`game/modules/tome/data/zones/old-forest/npcs.lua:164`，"This ancient Treant's bark is scorched almost black. It sees humanity as a scourge, to be purged."）与现行平面 token 冲突：v2 树皮是温暖中棕（审计实测中心主体 top-30% 亮度 102.5，原生精灵近黑 39.5）。保留枝/根姿态、树人面孔与圆盘，只把树皮改成灼烧近黑炭色。
- 重绘包 `art/production/handoffs/snaproot-token-repaint-v1/`（`snaproot-token-repaint-v1`，gpt-6.1-sol、`--ephemeral`）：attempt 1 产出 `masters/snaproot-v3.png`，门控通过但树皮仍偏灰白；attempt 2 定向返修产出 `masters/snaproot-v4.png`，门控通过 base_drift **-5.82**、最大不透明半径 0.8585、占格 0.8594、无警告。v3 作为未选中间稿保留在 `masters/`。
- manifest `art/production/batches/snaproot-token-repaint-v1.json` 带 refinement 声明，supersedes 原 `monster-batch-a-1`。旧母版与旧运行 token 归档于 `art/monster-batch-a/superseded/snaproot-v2.png` 与 `.../snaproot-v2-runtime-128.png`。
- 外观：树皮为灼烧近黑炭色（lit-bark top-30% 从 102.5 降到 **64.8**，中位 28.9），带细窄的灰白炭化边缘与裂缝以及微弱余烬；枝/根姿态与树人面孔保持。
- attempt 2 的 codex 回复漏报 image_generation 工具路径，按既有 recover 口径（调用窗口内唯一新 `exec-*.png`、在可信溯源目录内、重新过门控入库）记为 `recovered-recorded`，未再加发第三次调用。
- 三尺寸（48/64/96、mid-brown 地板）对照图见 `art/token-layers/review-tokens/snaproot.png`（native／v2／v4＋desc 原文）。
