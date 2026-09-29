# Irkkk bamboo-hut terrain art review (TW6, 2026-09-29)

Identity and rule contract were recorded before generation in [identity-bamboo-hut.md](../../evidence/terrain-tw6-20260929/identity-bamboo-hut.md) (pinned by SHA in every pack). All calls went through `tools/run_imagegen.py` with the terrain gate unchanged; full prompts, references, tool-origin paths, call ledgers and receipts are under `art/production/handoffs/bamboo-hut-tw6-v1/` (batch spec `art/production/batches/bamboo-hut-tw6-v1.json`).

**ImageGen calls: 4 / 14 allowed** (one per master, all recorded on attempt 1; no repair, no waiver, no threshold change).

| Pack | Kind | Outcome | Master (sha256) | Selected as |
| --- | --- | --- | --- | --- |
| `bamboo-hut-wall-top` | terrain-floor | Opaque 1254 px thatch-over-bamboo wall top; floor gate passed | `masters/bamboo-hut-wall-top-v1.png` (`a67b9ff0…141a`) | `selected/floor-bamboo-wall-top.png` |
| `bamboo-hut-wall` | terrain-prop | Native alpha, corners 0, A8.1 box `(122,301,1151,947)`, grounded 0.755 | `masters/bamboo-hut-wall-v1.png` (`b1b12099…6b0f`) | `selected/prop-bamboo-hut-wall.png` |
| `bamboo-hut-floor` | terrain-floor | Opaque 1254 px woven split-bamboo/reed mat; floor gate passed | `masters/bamboo-hut-floor-v1.png` (`e3bf199c…fc75`) | `selected/floor-bamboo-hut-floor.png` |
| `bamboo-hut-door` | terrain-prop | Native alpha, corners 0, A8.1 box `(284,145,965,1125)`, grounded 0.897 (a standing leaf, so A8.2 applies unchanged) | `masters/bamboo-hut-door-v1.png` (`58bc3131…2876`) | `selected/prop-bamboo-hut-door.png` |

The style references were the accepted TW5 golden crest (wall-top value/finish), the Norgos snow-pine prop (margins; it kept TW5's v4 block inside A8.1) and the Daikara bare-rock floor; identity references were the native `terrain/bamboo/*` tiles.

## Why four masters

The wall top and the wall face are separate for the same reason as TW5: a cropped palisade top would repeat as stripes. The thatch material is the cell-filling, non-directional blocking mass; the palisade's own culm face appears only on south edges open to passable ground. The floor must be a calm, lighter surface that shopkeepers stand on; the native dirt floor is darker than the native walls, so it was not reusable under the board value rule. The door leaf is a distinct woven palm-frond object so a door never reads as wall.

## Export

`export.py` (deterministic PIL, fixed crops, no noise) writes **42** 128 px RGB tiles to `exports/runtime/` and byte-identically to `data/gfx/refined/bamboo/`; `export-manifest.json` pins every tile, the four master SHAs and the constants.

- **Walls** `wall-<mask>-<parity>` (16 N/E/S/W masks × 2): a fixed 380 px window of the thatch master per mask (brightness .80, contrast .78); bamboo ridge poles (single culms cropped from the palisade face) run from the cell's ridge point to every connected side, so the hut outline is drawn as a lashed pole frame; open N/W edges get a thin dry-thatch rim, an open E edge a shaded side, an open S edge the palisade's culm face (44 px) with a contact shadow. A hut door counts as a connected wall neighbour.
- **Floor** `floor<parity>`: a centred 520 px window of the mat master, calmer (contrast .72) and darker (.80).
- **Doors** `door-{closed,open}-{horizontal,vertical}<parity>`: board hut floor with two short thatch posts in the wall line; closed = the woven leaf spans the doorway (46 px band), open = the leaf swung against the west/north post, seen edge-on as its bamboo stile, so the floor reads through (the Kor'Pul door language).
- Parity 1 = ×0.875 everywhere.

Measured on the exports (`export-manifest.json` → `metrics`): wall interior `wall-15-0` **52.0**, brightest wall 57.1, darkest wall 51.5; board floors it touches: jungle grass (Caldera) 96.5/82.5, hut floor 123.4/107.5 → interior gaps **46.2%** (grass) / **57.9%** (hut floor); brightest wall vs darkest parity-0 floor **40.9%**; doors 108.6–111.1 (between wall and floor, closed leaf covers more of the cell than the open one); minimum parity gap **12.8%** (all 21 pairs ≥ 10%). Enforced by `tests/production/test_bamboo_hut_exporter.py` (masters = recorded receipts, 42 files byte-identical in both places, parity ≥ 10%, walls ≥ 30% below both floors at either parity, warm hut floor lighter than jungle grass, south culm face present only on open south edges, distinct from gold-mountain/cave walls and jungle trees, doors lighter than walls, closed leaf larger than open).

## Visual review

`review/contact-{48,64,96}.png` (32 walls + floor + 8 doors) and `review/hut-field-64.png` (a hut with horizontal/vertical doors on jungle grass by the lake, the market's cooking pits over board hut floor). At 48/64/96 px the huts read as dark, clearly blocking bamboo-and-thatch walls framed by honey-coloured ridge poles, with a vertical-culm palisade face wherever a wall looks south onto open ground; the woven floor is light, warm and calm, so the yeek shopkeepers stay readable on it. Walls are warm brown, not the green of the Caldera trees nor the grey of stone. The native brightness order (pale bamboo walls on near-black dirt) is deliberately inverted (no bright-wall problem).

Weak points: the thatch top is busy and at 48 px reads more like rough bark/earth than thatch — the ridge poles carry most of the bamboo identity; the ridge poles are thin at 48 px; the door leaf is small at 48 px (a closed door reads as a short bamboo gate). Live frames and lit-pixel measurements: [TW6 evidence](../../evidence/terrain-tw6-20260929/README.md).
