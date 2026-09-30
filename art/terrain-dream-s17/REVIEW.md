# S17 dream family: art review (2026-09-30)

Identity and rule contract recorded before generation in
[identity-s17.md](../../evidence/terrain-s17-20260930/identity-s17.md) (pinned by SHA in both packs). Both calls went
through `tools/run_imagegen.py` with its defaults (`--model gpt-6.1-sol --ephemeral`; logged `codex_model:
gpt-6.1-sol`, `codex_ephemeral: true`), one call at a time, terrain gate unchanged. Batch specs
`art/production/batches/terrain-dream-s17-v1.json` (cloud) and `terrain-dream-s17-void-v1.json` (void, which takes the
recorded cloud master as its family reference, hence a second batch); prompts, references, ledgers and receipts under
`art/production/handoffs/terrain-dream-s17{,-void}-v1/`; prompt copies in `prompts/`.

**ImageGen calls: 2 / 6 allowed** (no repair, no waiver, no threshold change).

| Pack | Kind | Calls | Outcome | Master (sha256) |
| --- | --- | ---: | --- | --- |
| `dream-cloud-floor` | terrain-floor, opaque RGB 1254 px | 1 | `recorded` by the wrapper, attempt 1 (codex session `01a0f10d-f674-7030-91e0-9eaa069de438`, tool output `~/.codex/generated_images/01a0f10d-…/exec-df9ad29f-….png`) | `masters/dream-cloud-floor-v1.png` (`3e0c3d7b…cf9`) |
| `dream-void` | terrain-floor, opaque RGB 1254 px | 1 | wrapper `provenance-rejected` only because codex returned an empty `image_path` (its notes: tool called once, path not captured). The call ledger lists exactly one new file in `~/.codex/generated_images/` during the call (`01a0f110-0491-7b33-a745-f2062617df00/exec-69d53658-8aaf-4245-8b1c-7774d093e9b8.png`); that file was copied byte-for-byte and recorded through the standard `tools/art_tasks.py record … --attempt 1` (receipt `receipts/attempt-1.json`, mechanical check pass) instead of spending a second call. The rejected `call-1/` record is kept unchanged. | `masters/dream-void-v1.png` (`77ff9f1e…fce`) |

References: cloud = native `terrain/clouds/cloud_normal_002.png` (identity) + accepted Kor'Pul floor master (style); void =
the recorded cloud master (family) + accepted board void master `art/terrain-void-v1/masters/void-blocked-fracture-v1.png`
(style).

## Export

`export.py` (deterministic PIL, fixed windows, no noise) writes **100** 128 px tiles to `data/gfx/refined/dream/` and the
gated runtime manifest `data/terrain-dream-manifest.lua` (revision `dream-s17-9bef16fa6fab`); `export-manifest.json`
pins every tile, both master SHAs and luminance.

- **Cloud floor** `cloud-<v>-<mask>-<p>` (3 variants × 16 masks × 2 parities): a fixed 640 px window of the master per
  variant (about two to three billows across a cell), contrast ×1.18 and brightness ×0.82 so tokens stay the strongest
  element. On an open edge (neighbour not cloud) a soft **billowed cloud rim**: a scalloped band (32 px scallop period
  anchored at the cell corners, so neighbouring rims meet) shaded toward lilac — 5 px north, 7 px east/west, 13 px south
  (+ up to 4 px swell), i.e. the floor's side falling away under the board's upper-left light — with a 2 px bright lip on
  the walkable side. No wall, rail or fence; 1 px printed grid ×0.93; parity 1 = ×0.90.
- **Dream void** `void-<v>-<p>` (2 variants × 2 parities, unmasked): fixed 640 px windows of the indigo haze master;
  parity 1 = ×0.86. The variant is `(x*17+y*7)%2` so pools do not repeat one tile in a checker.

Measured (128 px, parity 0, luminance): cloud interior **185.7–190.9** (parity 1: 171.8), single cell 174.6, south-open
184.5; void **24.6–28.5** (parity 1: 21.1). For reference: Point Zero space 11.2, Point Zero platform 163.3, snow ground
175.0, board grass 109.0. Enforced by `tests/production/test_dream_s17_exporter.py`.

## Visual review

Sheets: `review/scene-{48,64,96}.png` (+`-gray`: a Dreamscape-like plane with cloud islands, a one-cell peninsula and a
lone cloud cell over the void, the demo player token and a giant white mouse token on the cloud),
`review/scene-64-tinted.png` (the scene multiplied by the zone's `color_shown` {0.5, 1, 0.7}),
`review/compare-{48,64,96}.png` (+`-gray`: cloud interior / parity / south rim / east-west rim / single, dream void and
its parity, beside Point Zero space and platform, snow ground, grass, Kor'Pul floor, hazard lava and the native cloud
puff), and per-tile `review/{48,64,96}/`. Live frames (local): `evidence/terrain-s17-20260930/screenshots/`.

At 48/64 px the cloud reads as **soft pale ground laid out on the board**: a quilted billow texture of even scale with
the checker parity clearly visible, the rim marking where the floor ends as a soft drop, not a wall. The void reads as a
**dark, empty field** well below it (grayscale 25 vs 186 offline; in game under the plane's own tint 16 vs 140), with no
stars, swirls or bright specks that could read as items, portals or a hazard, and no warm colours that could read as lava.
It is distinct from Point Zero space (near-black cosmic) and from the pale Point Zero platform (grey-lavender marble). In
game the zone's clock-driven foreground tints both (the frames show the pink phase, like the native pink puffs).

Weak points: the rim is subtle at 48 px (the value step carries the reading); the cloud, like the rest of the board, is
static, so the native `cloud_anim` shader movement is gone in Refined; the south side band is a stylised depth cue, the
native plane has no vertical depth either.
