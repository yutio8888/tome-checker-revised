# Eruan palm and sand exits — terrain art review (S6, 2026-09-29)

Identity and rule contract were recorded before generation in [identity-palm.md](../../evidence/terrain-s6-20260929/identity-palm.md) (pinned by SHA in the pack). The call went through `tools/run_imagegen.py --execute generate` with the terrain gate unchanged; prompt, references, tool-origin path, call ledger and receipt are under `art/production/handoffs/palm-s6-v1/palm-tree/` (batch spec `art/production/batches/palm-s6-v1.json`).

**ImageGen calls: 1 / 6 allowed** (attempt 1 recorded; no repair, no waiver, no threshold change).

| Pack | Kind | Outcome | Master (sha256) |
| --- | --- | --- | --- |
| `palm-tree` | terrain-prop | Native alpha 0..255, corners 0, A8.1 box `(174,102,1094,1186)` (≥25.1 px from every edge), grounded 1186/1254 = 0.946 | `masters/palm-tree-v1.png` (`371f61e1…337f`) |

References: identity = native `terrain/palmtree_alpha5.png`; style = the F1 `hardtree-v1` board tree master (its recoloured crops are the South Beach and Caldera board trees); family = the Norgos snow-pine prop (margins). The master is a date palm with a leaning diamond-bark trunk, a dense dark-green frond crown with a few dry fronds and a date cluster, on a small sand mound — the same painted tabletop finish and upper-left light as the board trees.

## Export

`export.py` (deterministic PIL) writes **10** 128 px RGB tiles to `exports/runtime/` and byte-identically to `data/gfx/refined/eruan/`; `export-manifest.json` pins the master, the two reused sources (`refined/beach/sand0.png`, `refined/exit0.png`), every output and the constants.

- `palm-{a,b}{0,1}`: the palm (solid silhouette, alpha > 60) scaled to 136 px wide over the beach sand darkened ×0.62 with a broad contact shadow; the mound rests on the bottom edge, only frond tips pass the cell edges. `b` is the mirrored palm; the renderer picks `a`/`b` by `(x*17+y*7)%4<2`, independent of parity.
- `exit-{up,down,world}{0,1}`: the board beach sand with the forest exit's pale arrow (down = rotated; world = ring) and a thin dark keyline so it holds on sand.
- Parity 1 = ×0.86 (the beach family's step).

Measured (`export-manifest.json` → `metrics`): beach sand 109.2 / 93.4; palm tile 72.3 / 61.7 (whole) and 70.3 / 60.0 (40% centre crop) → palm cells **33.8% / 33.9%** darker than the open sand of the same parity; exits 108.7–109.7 (sand value, glyph on top); parity gaps 14.4–14.7%. Enforced by `tests/production/test_palm_s6_exporter.py` (master = receipt, native alpha/corners, 10 files byte-identical in both places, sources pinned, parity ≥ 10%, palm ≥ 25% darker than beach sand at both parities incl. the centre crop, mirrored crown, three distinct exit glyphs).

## Visual review

`review/contact-{48,64,96}.png` (all 10 tiles) and `review/shore-{48,64,96}.png` (a 12×6 Erúan shore: palm groves on sand, palms beside board deep water, the three exits) at 48/64/96 px. The palm reads as a palm at 48 px (radiating fronds, bare curved trunk), each palm cell is a clearly darker, blocking square against the open sand, and palm clumps form a readable wall line without merging into a single blob thanks to the pale mound and the parity step. Dark-green crown vs teal board water and tan sand: three distinct hues and values. Live frames: [S6 evidence](../../evidence/terrain-s6-20260929/README.md).

Weak points: the pale sand mound is the brightest part of the cell and can read as a small island at 96 px; plain/mirrored is the only variation (native used 1–3 random palms per cell, the board uses one palm per cell); in very dense groves the grid of identical crowns is regular.

Gates of Morning (`maps/towns/gates-of-morning.lua:29`, 9 cells) places the same `sand.lua` `PALMTREE` over the same board beach sand; the tile would fit exactly there but is **not applied** (open user decision on town palms).
