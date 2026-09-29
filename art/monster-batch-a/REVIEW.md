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
