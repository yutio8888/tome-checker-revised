# S10b gothic family: art review (2026-09-30)

Identity and rule contract recorded before generation in [identity-s10b.md](../../evidence/terrain-s10b-20260930/identity-s10b.md) (pinned by SHA in every pack). All calls went through `tools/run_imagegen.py` (default `--model gpt-6.1-sol --ephemeral`, logged as `codex_model: gpt-6.1-sol`, `codex_ephemeral: true` in each `call.json`) with the terrain gate unchanged. Batch spec `art/production/batches/gothic-s10b-v1.json`; prompts, references, tool-origin paths, ledgers and receipts under `art/production/handoffs/gothic-s10b-v1/` (prepared with the working tree's unmodified `tools/art_tasks.py`; its inputs were not touched by monster batch U); prompt copies in `prompts/`.

**ImageGen calls: 5 / 12 allowed** (per-asset cap respected: at most 2, the tool's own pack limit; no repair, no waiver, no threshold change).

| Pack | Kind | Calls | Outcome | Master (sha256) |
| --- | --- | ---: | --- | --- |
| `gothic-floor` | terrain-floor, opaque 1254 px | 1 | recorded, attempt 1 | `masters/gothic-floor-v1.png` (`a7af50d4…7771`) |
| `gothic-wall-top` | terrain-floor (opaque wall-top material), 1254 px | 1 | recorded, attempt 1 | `masters/gothic-wall-top-v1.png` (`77b64f71…90c5`) |
| `gothic-door` | terrain-prop, native alpha | 1 | recorded, attempt 1 | `masters/gothic-door-v1.png` (`fc58ecfd…1b`) |
| `gothic-wall-face` | terrain-prop, native alpha | 2 | **not recorded**: call 1 `provenance-rejected` (the CLI reported the tool ran but returned no file), call 2 `style-gate-rejected` (A8.1: opaque box `(15,335,1238,951)` within 25.1 px of the edge). Pack budget spent; handed back to design, no third call, no new pack | — |

References: identity = native `gothic_walls/marble_floor.png`, `granite_wall1_1.png`, `granite_wall2.png`, `granite_door1.png`; style = the accepted Kor'Pul floor master, the TW5 golden-mountain crest, the TW6 bamboo wall/door props.

## Export

`export.py` (deterministic PIL, fixed crops, no noise) writes **52** 128 px RGB tiles to `exports/runtime/` and byte-identically to `data/gfx/refined/gothic/`; `export-manifest.json` pins every tile, the three master SHAs, the reused Kor'Pul stair pieces and the constants.

- **Floor** `floor-{a,b,c}<p>`: the master is a 4×4 grid of pale limestone flags (joints measured at 313/626/940 px); each variant is one whole interior flag cropped joint-centre to joint-centre, so two neighbouring cells form one full joint on the board grid line. The three flags are levelled to the same value (146) and softened; `CheckerTerrain.lua` picks the variant by `(x*17+y*7)%3`.
- **Walls** `wall-<mask>-<p>` (16 N/E/S/W masks × 2): a fixed 470 px window of the slate coping master per mask; open N/W edges get a thin cool rim, open E a shaded side, open S the only face: two courses of the same slate compressed into a 40 px band, darkened, under a lit coping lip, with a contact shadow (the slime-family construction; the face prop was not available). Gothic doors and Vor's native lever doors count as connected wall.
- **Doors** `door-{closed,open}-{horizontal,vertical}<p>`: gothic floor with two slate jamb posts in the wall line; closed = the iron-strapped oak leaf spans the doorway (46 px band), open = the leaf swung against the west/north post, seen edge-on (the Kor'Pul/bamboo door language).
- **Exits** `exit-{up,down,world}<p>`: the shared Kor'Pul stair pieces (the stone adapter draws basic.lua flat exits with the same pieces) on floor-a.
- Parity 1 = ×0.875 everywhere. Reused unchanged: Spellblaze `burnt/floor`, `burnt/tree`, `burnt/exit-down` for the burnt yard and FLAT_DOWN4; Kor'Pul stone (S8 dark wall) for the renegade vault.

Measured (128 px, parity 0, luminance): floor **145.5** (all three variants; Kor'Pul floor 131.8, cave 135); wall interior **48.7**, walls 38.0–54.3 (Kor'Pul brick 158.2, S8 dark brick 94.8); floor − brightest wall **62.7%**; doors 118 closed / 125 open; burnt ground 72.7, burnt tree 66.5; minimum parity gap 12.8%. Enforced by `tests/production/test_gothic_s10b_exporter.py` (recorded masters and model, 52 files byte-identical in both places, parity ≥ 10%, walls ≥ 55% below floor and ≥ 20% below burnt ground, face band only on open south edges, doors between wall and floor, cool slate distinct from both Kor'Pul brick sets).

## Visual review

`review/contact-{48,64,96}.png` (+`-gray`) and `review/scene-{hall,yard}-{48,64}.png` (+`-gray`), plus the live frames in `evidence/terrain-s10b-20260930/screenshots/` (local). At 48/64 px the gothic family reads as its own set inside the board language: pale cool-grey flagstone halls that pieces clearly stand on, heavy near-black slate walls with iron clamps and a dark south face, and warm oak doors with black strap hinges in the wall line. It is neither a Kor'Pul recolour (Kor'Pul is pale warm sandstone brick; S8 dark brick is warm grey-brown at 95) nor the slime/cave families (hue and cut masonry). In grayscale the hierarchy holds: floor ≈146, doors ≈118–125, burnt yard ≈67–73, walls ≈39–54.

Weak points: the one-flag-per-cell floor makes the joint grid coincide with the board grid (tidy, but every hall is a regular chequer of flags); the south face is compressed coping, not a true wall elevation with niches/spikes (the face prop failed twice); the Spellblaze burnt yard reused as-is keeps its low ground/tree contrast (≈9%) and is only ≈33% above the gothic wall in grayscale.
