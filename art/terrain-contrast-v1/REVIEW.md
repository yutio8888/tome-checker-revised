# Terrain floor / blocking-wall readability pass — 2026-10-01

Reuses existing generated art; **zero ImageGen calls**. No gameplay, runtime Lua, file-name, neighbour-mask or parity changes. Native alpha is retained; floors, exits, locks, doors and stairs are unchanged in the accepted runtime iteration. All other refined assets, including gloom and downstream derived families, are checked byte-identical against the baseline commit in `evidence/terrain-contrast-20261001/package-and-byte-audit.json`.

Sand's old exporter removed broad rock-plane detail and substituted floor-derived grain. Its nearly featureless brown cap could read as shaded ground. The new cap samples the existing `sand-wall-v1.png` master's actual rock planes, recolours to dark warm compacted stone (48 mean grey before parity), and preserves the south vertical face at a lower value. Exposed north/west lips, east shadow, south overhang/contact shadow provide height cues. Sand stays warm under the unchanged colour gate. The diagonal source planes repeat visibly across a large wall field; they remain crisp and distinct from passable dunes.

Maze's old lichen bricks had insufficient value separation. Its frozen accepted exports receive a 0.55 value gain, retaining brick detail and masks, plus exposed-edge cues. Crystal's facets already conveyed height but its darkened floor reduced the value step. The finish scales R/G/B by 0.52/0.60/0.91, preserving the existing blue-vs-floor colour gate and crystal detail, with exposed-edge cues.

`export.py` replays the finish from byte-pinned `frozen-inputs`, synchronises the original suites' selected exports, manifests and 48/64/96 review downscales via `sync_selected.py`. Original masters/exporters remain the baseline production stage; run this final pass **after** their exporters. Unchanged runtime-derived families need no new inputs because this accepted iteration leaves every source they consume unchanged.

Mean per-pixel CIELAB, D65 sRGB, alpha composited on black, parity 0 / 1:

| Family | Before ΔE | After ΔE | After floor L* / wall L* (p0) |
| --- | --- | --- | --- |
| sand | 27.1 / 24.4 | 37.0 / 33.5 | 47.6 / 19.9 |
| maze | 11.9 / 10.9 | 32.2 / 29.5 | 55.1 / 23.4 |
| crystal | 23.7 / 21.1 | 36.7 / 32.1 | 43.9 / 14.3 |

Measurements differ from the supplied preliminary sheet; these use the precise HEAD baseline bytes and the explicit conversion in `export.py`, with matching floor and wall parities. New additional gate: ΔE >=25 and floor L* minus wall L* >=24, both parities. No existing threshold was changed.

## RESOLVED (2026-10-01, hue finish below) — former PENDING waiver request, Kor’Pul / Kor’Pul-dark

The waiver below is no longer requested: the `korpul.py` hue finish reaches the target without touching any gate. The original analysis is kept as the record of why the darker-brick candidates were withheld.

Root cause: original diggable Kor’Pul bricks are lighter than floor with a small value gap; dark bricks improve that gap but remain below the requested ΔE. Review-only candidates are kept in `pending-exports`; **none are installed**. Proposed ordinary brick gain 0.37 with exposed-edge cues gives ΔE 10.4→32.0 (parity 1: 9.6→29.3). A dark candidate preserving the existing 0.60 geometry/value ratio also improves separation, but violates existing cross-family hierarchy gates:

- `test_gothic_s10b_exporter.test_distinct_from_korpul`: Gothic wall 50.1 must be below 0.65 × proposed Kor’Pul wall 56.1 =36.5.
- `test_hazard_s12_exporter.test_hazard_value_hierarchy`: lava variants 50.9–51.5 must be below 0.65 × proposed dark brick 33.2 =21.6.

The unchanged S8 geometry ratio gate prevents independently lifting the dark family to repair that hierarchy. The candidates are withheld; thresholds/tests are untouched. A later decision must explicitly waive the conflicting cross-family comparisons or authorise a broader value-hierarchy redesign. Current production Kor’Pul / Kor’Pul-dark ΔE remains 10.4 / 19.3 (p0).

## Visual review

Personally inspected all four before/after comparison sheets, containing lit 48/64/96 and remembered 64 crops. Sand rock tops now remain visibly distinct from dunes in dim terrain. Maze bricks remain legible with a clear floor step and thin raised edges. Crystal facets retain colour and fine detail while the wall mass separates from the purple-tinted floor. Kor’Pul screenshots are unchanged-art controls. These are staged fixture scenes, with different generated layouts between launches; no pixel-aligned before/after claim. Doors/locks/stairs were not systematically placed beside every new edge in-game; their bytes are unchanged, but exhaustive interaction-adjacency validation remains open. Full save loading and continuous combat were not tested.

## Kor’Pul / Kor’Pul-dark resolution — luma-preserving hue split (2026-10-01)

Why values cannot move: with every existing gate unchanged, the floor luma is boxed in to roughly 124–138 (p0) / 116–120 (p1) by Conclave (>30% above its walls), the S8 dark brick (floor ≥ dark/0.82, dark < grass), the TW7 road (≥10% above the floor) and the Gothic floors (≥ Kor’Pul floor). The dark brick must stay ≥79 for lava/Gothic and at 0.55–0.66 of the Kor’Pul brick, so the brick stays ≥120. There is no luma pair that gives ΔE ≥25 on value alone. The remaining dimension is hue.

`korpul.py` (zero ImageGen, no runtime Lua) scales R/G/B and then restores each pixel’s original luma (PIL `L`), so every existing luminance gate reads the baseline values:

- `floor-a`/`floor-b` (4 files): warm sandstone, gains 1.08/0.99/0.82.
- Kor’Pul diggable brick `wall-*` (32) and the jamb pixels of its doors: cool grey, gains 0.93/1.00/1.14.
- Kor’Pul-dark brick (32): byte-identical. It is already near-neutral.
- Doors (128 + 128): pixels equal to the baseline floor get the floor finish, which makes them identical to the new floor tile. Kor’Pul jamb pixels (where the baseline Kor’Pul and dark doors differ) get the brick finish. Leaf and fittings are unchanged. Dark doors still differ from Kor’Pul doors only inside the S8 jamb rectangles.
- Hardwall and stairs are unchanged.

Mean CIELAB ΔE against `korpul/floor-a-0-p` (parity 0 / 1):

| Wall | Before | After |
| --- | --- | --- |
| korpul/wall-15 | 10.4 / 9.6 | 28.9 / 26.5 |
| korpul-dark/wall-15 | 19.3 / 17.7 | 28.2 / 26.0 |
| korpul/hardwall-15 | 16.9 / 15.5 | 27.6 / 25.4 |
| maze/old-wall-15 (Maze floor = korpul floor-a) | 32.2 / 29.5 | 36.4 / 33.4 |

Floor L*/a*/b* p0 is 55.2/3.6/24.4 (was 55.1/0.8/12.6). The value step is unchanged by design. The dark brick sits 15.2 / 14.0 L* below the floor. The diggable Kor’Pul brick remains 9.6 / 8.7 L* lighter than the floor because the gates force it to. Its separation comes from warm floor against cool brick (Δb* 27). The bricks are not resampled, so 48/64/96 crispness is unchanged.

Shared-file families: the slime creep edges (30 tiles) and the graveyard coffin/mausoleum road (6 tiles) composite the live floor beside live floor cells. They are re-exported so no old-floor seam remains. The headstone material reads a frozen brick, which keeps graves byte-identical. Batch 4 (Conclave), batch 5 (Sher’Tul grain), the cave doors (S2) and the S8 assembler self-check now read the frozen baseline in `frozen-inputs/korpul`. Their outputs re-export byte-identical, and only their source paths in the manifests changed. The Kor’Pul runtime manifest, the review downscales and the S8 export record hashes are synchronised. Order: `export_korpul_terrain.c` → S8 `export.py` → `korpul.py`.

New gate `tests/production/test_korpul_contrast.py` requires:

- ΔE ≥25 for brick, dark brick, hardwall and Maze wall in both parities.
- Floor b* at least 20 above the brick’s.
- Floor L* at least 12 above the dark brick’s.
- Luma preserved.
- Dark brick byte-identical.
- Door floor pixels equal to the floor tile.

No existing threshold changed. The `pending-exports` candidates are superseded and unused.

Visual review: I inspected the before/after sheets `review/korpul-{before,after}-{48,64,96}.png` and the live crops in `evidence/korpul-contrast-20261001/crops/`. In Kor’Pul (both layouts) and Rhaloren, the warm floor now reads clearly against the grey brick, both lit and remembered. Door cells show no floor seam. In the Maze, corridors still read clearly against the dark walls. In graveyard L2, the coffins sit seamlessly on the road. Derth’s pose framed lake and trees, so no stone-town cell was in view there; Rhaloren camp covers that requirement. The light Kor’Pul brick has no live diggable-wall zone outside S8 (every such zone uses the dark brick). It is checked on the review sheets only.
