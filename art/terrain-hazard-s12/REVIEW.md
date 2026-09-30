# S12 hazard family: art review (2026-09-30)

Identity and rule contract recorded before generation in
[identity-s12.md](../../evidence/terrain-s12-20260930/identity-s12.md) (pinned by SHA in the pack). The call went
through `tools/run_imagegen.py` with its defaults (`--model gpt-6.1-sol --ephemeral`; logged `codex_model:
gpt-6.1-sol`, `codex_ephemeral: true`) and the terrain gate unchanged. Batch spec
`art/production/batches/terrain-hazard-s12-v1.json`; prompt, references, tool-origin path, ledger and receipt under
`art/production/handoffs/terrain-hazard-s12-v1/hazard-lava-floor/` (prepared with the working tree's
`tools/art_tasks.py`, not blocked by monster batch V); prompt copy in `prompts/`.

**ImageGen calls: 1 / 8 allowed** (per-asset cap 3 not approached; no repair, no waiver, no threshold change).

| Pack | Kind | Calls | Outcome | Master (sha256) |
| --- | --- | ---: | --- | --- |
| `hazard-lava-floor` | terrain-floor, opaque RGB 1254 px | 1 | recorded, attempt 1 (codex session `01a0f02f-036e-7d71-bb38-a5dae5cb1f04`, tool output `~/.codex/generated_images/…/exec-abab3a72-….png`) | `masters/hazard-lava-floor-v1.png` (`cd04a2b0…aed6b`) |

References: identity = native `terrain/lava/lava_floor9.png` (dark crust, scattered molten spots); style = the accepted
Kor'Pul floor master `art/terrain-korpul-v1/masters/floor-a-v2.png`. The stone-kerb deep water is **derived, 0 calls**:
the board deep-water surface (`art/terrain-forest-v1/masters-derived/floor-deep.png`, the surface of every
`refined/deep*` tile) plus the Kor'Pul floor master as kerb stone.

## Export

`export.py` (deterministic PIL, fixed windows, no noise) writes **128** 128 px tiles to `data/gfx/refined/hazard/` and
the gated runtime manifest `data/terrain-hazard-manifest.lua`; `export-manifest.json` pins every tile, the three source
SHAs and luminance.

- **Hazard lava** `lava-<v>-<mask>-<p>` (3 variants × 16 masks × 2 parities): a fixed 640 px window of the master per
  variant (about four crust plates across a cell); `CheckerTerrain.lua` picks the variant by `(x*17+y*7)%3`, so a pool
  never repeats one tile in a checker. On an open edge (neighbour not hazard lava) a **flush glowing seam**: a 2 px hot
  line (255,176,64) on the shared edge and a 10 px red-orange heat bleed into the crust. No raised rim, no dark frame,
  no pool.
- **Stone-kerb deep water** `deep-<mask>-<p>`: the unchanged board water surface; on an open edge a 10 px kerb of
  Kor'Pul floor stone (the forest bank depth, ×1.08) with a 2 px wet line on the water side and a 4 px shadow on the
  water under it; a corner where two kerbs meet stays dry stone.
- Both use the Kor'Pul conventions of the rooms they sit in: 1 px printed grid on all edges (×0.88), parity 1 = ×0.90.

Measured (128 px, parity 0, luminance): hazard interior **50.9–51.5** (edge tile 64.2), hot pixels 5.0–6.9 %
(blocking molten pit `burnt/lava-15` 26.2 %, harmless lava floor 0 %); Kor'Pul floor 131.8, hard wall 100–107, S8 dark
brick 90–95, harmless Daikara lava floor 54.6 (no glow), molten pit 85.6; stone deep interior 61.4 (= board deep water),
single-cell pool 79.0. Enforced by `tests/production/test_hazard_s12_exporter.py`.

## Visual review

Sheets: `review/scene-{48,64,96}.png` (+`-gray`: a Vor Armoury-like stone room with a hazard pool, a deep-water channel
and the fixture player token next to the lava), `review/compare-{48,64,96}.png` (+`-gray`: hazard interior/edge/single
beside the molten pit, harmless lava floor, lava wall, poison water, forest deep water, stone deep water, stone floor and
hard wall), and per-tile `review/{48,64,96}/`. Live frames (local): `evidence/terrain-s12-20260930/screenshots/`.

At 48/64 px the hazard reads as **hot ground you can step on**: flat dark crust plates split by thin glowing seams,
bounded by a thin hot line flush with the neighbouring floor. It is clearly not the blocking molten pit (that is mostly
bright molten with a heavy dark stone lip), not the harmless Daikara lava floor (dark cracked rock, no glow) and not a
wall (walls are light grey block with a south face). In grayscale it is the darkest material in the room with a bright
seam texture: board frames give lava 45.6–48.0 vs floor 119.0–122.2 and walls 88.8–93.5. The stone deep water reads as
a cut pool in the room floor, the same water as elsewhere on the board.

Weak points: the plates are small at 48 px (the seam network carries the reading, plate shapes do not); the hot edge
line is thin at 48 px on dark vault lighting; the hazard, like the rest of the board, has no animation, so the native
lava shader's movement is gone in Refined; the kerb uses the Kor'Pul floor stone even in the few cells where water meets
a hard wall.
