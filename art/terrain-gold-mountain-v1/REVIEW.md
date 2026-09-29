# Sunwall golden-mountain terrain art review (TW5, 2026-09-29)

Identity and rule contract were recorded before generation in [identity-gold-mountain.md](../../evidence/terrain-tw5-20260929/identity-gold-mountain.md) (pinned by SHA in every pack). All calls went through `tools/run_imagegen.py` with the terrain gate unchanged; full prompts, references, tool-origin paths, call ledgers and receipts are under `art/production/handoffs/gold-mountain-tw5-*`.

**ImageGen calls: 5 / 12 allowed.**

| Pack | Call | Outcome |
| --- | --- | --- |
| `gold-mountain-tw5-v1` | 1 | Desired broad golden sandstone block; failed A8.1 (opaque box `(33,139,1235,1146)` on 1254 px, right inset 19 px < 25.1). Not recorded; bytes kept as `masters/gold-mountain-wall-v1-rejected.png`. |
| `gold-mountain-tw5-v2` | 1 | Same design with a 10% inset request; failed A8.1 by 1.1 px on the right (`(36,137,1230,1138)`). Kept as `-v2-rejected.png`. |
| `gold-mountain-tw5-v3` | 1 | "Middle 70% of the width" request; failed A8.1 again (`(32,138,1230,1131)`). Kept as `-v3-rejected.png`. The three footprints matched the Daikara style reference (x 31–1227), which the model copied. |
| `gold-mountain-tw5-v4` | 1 | Style reference swapped for the accepted Norgos snow-pine prop (light/finish/margins only). Passed native alpha, corners, grounding and A8.1 (`(73,215,1207,1129)`), no waiver. **Selected** as `selected/prop-gold-mountain.png`. |
| `gold-mountain-tw5-crest-v1` | 1 | Opaque overhead crest material. Passed the floor gate (opaque, 1254 px). **Selected** as `selected/floor-gold-crest.png`. |

No waiver was requested or used; no threshold changed. (The working-tree token catalog was mid-edit by monster batch O, so `art_tasks.py`/`run_imagegen.py` were run through a wrapper, `tmp/tw5/head_catalog_run.py` outside the repo, that feeds `current_catalog()` the committed HEAD catalog/manifest with the identical parser; nothing else differs.)

## Why two masters

The first export cropped the v4 block's own stepped plateau as the cell-filling interior. In the 64 px connected field and in the live fixture its horizontal ledges repeated as streaks that read as wooden boards, not a mountain. The crest master (crumpled, non-directional golden crags like the native `golden_mountain5_*` texture) replaced only the interior; the block master still supplies the dark strata cliff face on south edges open to passable ground.

## Export

`export.py` (deterministic PIL, fixed crops, no noise) writes **32** 128 px RGB tiles `wall-<mask>-<parity>.png` (16 N/E/S/W masks × 2 parities) to `exports/runtime/` and byte-identically to `data/gfx/refined/gold-mountain/`; `export-manifest.json` pins every tile, both master SHAs and the constants. Each mask uses a fixed 420 px window of the crest master, a power-curve tone (γ 1.5) and a slight hue pull toward ochre; an open N edge gets a thin sunlit gold rim, an open W/E edge a light/shaded side, an open S edge the master's cliff face (darker) with a contact shadow. Parity 1 = ×0.875.

Measured on the exports (`export-manifest.json` → `metrics`): interior `wall-15-0` luminance **63.9**; board floors it touches: stone floor 131.8, grass 109.0, sand 109.2, road 113.2 → gaps **51.5% / 41.3% / 41.4% / 43.5%**; brightest wall tile 69.8 (still ≥30% below the darkest floor); minimum parity gap **13.1%** (all 16 pairs ≥10%). Enforced by `tests/production/test_gold_mountain_exporter.py` (masters = recorded receipts, 32 files byte-identical in both places, parity ≥10%, wall ≤70% of darkest floor, exposed S face darker than interior, warm hue r>g>1.2b, distinct from the Daikara/cave/crystal walls).

## Visual review

`review/contact-{48,64,96}.png` (all 32 tiles) and `review/wall-field-64.png` (ring round a stone/grass/sand clearing). At 48/64/96 px the mass reads as dark golden crag rock, clearly blocking and clearly warmer than the grey Daikara/Kor'Pul families; the south cliff face marks the ring's inner edge. The crest texture is busy at 48 px, but it stays a uniform dark mass rather than individual obstacles, and it never looks like floor. The native bright-yellow value is deliberately not reproduced (V2 bright-wall problem). Live frames: [TW5 evidence](../../evidence/terrain-tw5-20260929/README.md).
