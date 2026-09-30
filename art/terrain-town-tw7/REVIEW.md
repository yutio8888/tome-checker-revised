# TW7 town roads and crop fields: art review (2026-09-30)

Identity and rule contract recorded before generation in [identity-tw7.md](../../evidence/terrain-tw7-20260930/identity-tw7.md) (pinned by SHA in both packs). Both calls went through `tools/run_imagegen.py` (default `--model gpt-6.1-sol --ephemeral`, logged as `codex_model: gpt-6.1-sol` in each `call.json`) with the terrain gate unchanged. Batch spec `art/production/batches/town-tw7-v1.json`; prompts, references, tool-origin paths, ledgers and receipts under `art/production/handoffs/town-tw7-v1/`; prompt copies in `prompts/`.

**ImageGen calls: 2 / 10 allowed** (one per master, both recorded on attempt 1; no repair, no waiver, no threshold change). Gates of Morning palms use the existing S6 palm (`art/terrain-palm-s6`), no new art.

| Pack | Kind | Master (sha256) | Exports |
| --- | --- | --- | --- |
| `town-road-slab` | terrain-floor, opaque 1254 px | `masters/town-road-slab-v1.png` (`69690702…0edf1`) | `road{0,1}` |
| `town-crop-field` | terrain-floor, opaque 1254 px | `masters/town-crop-field-v1.png` (`9ef964b1…f0a7`) | `fields{0,1}` |

References: identity = native `road_oldstone/road_horizontal_a_01.png` / `cultivation02.png`; style = the accepted TW6 hut-floor master.

## Export

`export.py` (deterministic PIL crops) writes 4 128 px RGB tiles to `exports/runtime/` and byte-identically to `data/gfx/refined/town/`; `export-manifest.json` pins files, masters, constants and metrics. Structure = the existing board road/grass (2 parities, no neighbour masks: both are plain walkable floors). Parity 1 = ×0.875.

- `road<p>`: centred 500 px window (about two pale limestone slabs across a cell), contrast .78, brightness .86.
- `fields<p>`: a window exactly two furrow periods high (period 208.5 px measured on the master), so vertically stacked cells continue the row rhythm; two low green seedling rows on light tilled soil per cell.

Measured (128 px, parity 0): road **152.9** vs grass 109.0 (+28.7%), Kor'Pul plaza floor 131.8 (+13.8%), hardwall interior 106.9 (+30.1%), gold mountain 63.9 (+58.2%), old dirt road 113.2; fields **113.1** vs grass (+3.7%), tree +10.9%; parity gaps ≥ 12.8%. Enforced by `tests/production/test_town_tw7_exporter.py`.

## Visual review

`review/contact-{48,64,96}.png`, `review/town-scene-{48,64}.png` and their `-gray` versions (a Kor'Pul house with a road in front, plaza floor, grass, a crop plot beside the road, trees, beach with the S6 palm). At 48/64 px the road reads as pale, warm dressed-stone paving — clearly passable ground, lighter than grass and every wall, warmer and slab-jointed against the grey plaza floor. The field reads as flat farmland: soft brown/green stripes, the same value as grass, nothing standing up, so it does not suggest an obstacle or a path bonus. In grayscale the hierarchy holds: road lightest, grass/fields middle, walls/trees/palms darkest.

Weak points: every road cell repeats the same slab arrangement (board-tile rhythm, visible along long straight roads); road vs plaza floor differs mostly by pattern and warmth (value gap ~8–14%); field rows are horizontal regardless of plot orientation.
