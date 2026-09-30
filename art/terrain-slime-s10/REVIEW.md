# S10a slime family: art review (2026-09-30)

Identity and rule contract recorded before generation in [identity-s10a.md](../../evidence/terrain-s10a-20260930/identity-s10a.md) (pinned by SHA in both packs). Both calls went through `tools/run_imagegen.py` (default `--model gpt-6.1-sol --ephemeral`, logged as `codex_model: gpt-6.1-sol`, `outcome: recorded` in each `call.json`) with the terrain gate unchanged. Batch spec `art/production/batches/slime-s10-v1.json`; prompts, references, tool-origin paths, ledgers and receipts under `art/production/handoffs/slime-s10-v1/` (prepared from a HEAD copy of the tools because the working tree's token catalogue was mid-edit by monster batch T; the prepared pack is byte-identical to what `prepare` writes); prompt copies in `prompts/`.

**ImageGen calls: 2 / 12 allowed** (one per master, both recorded on attempt 1; no repair, no waiver, no threshold change).

| Pack | Kind | Master (sha256) | Exports |
| --- | --- | --- | --- |
| `slime-floor` | terrain-floor, opaque 1254 px | `masters/slime-floor-v1.png` (`0d7b1ef8…eacec`) | `floor{0,1}`, `stairs-{up,down}{0,1}`, `creep-<mask>-{0,1}` |
| `slime-wall` | terrain-floor (opaque wall-top material), 1254 px | `masters/slime-wall-v1.png` (`f59fbb74…cd7a8`) | `wall-<mask>-{0,1}` |

References: identity = native `slime/slime_floor_01.png` / `slime/slime_wall_V2_8_01.png`; style = the accepted cave floor master (`terrain-cave-v1`) / the TW5 golden-mountain crest material.

## Export

`export.py` (deterministic PIL) writes 70 128 px RGB tiles to `exports/runtime/` and byte-identically to `data/gfx/refined/slime/`; `export-manifest.json` pins files, masters, the reused board tiles and constants. Construction follows the accepted cave / golden-mountain families: floor = one softened centred window, pulled from khaki toward sage (channel balance .88/1/.92); wall = one master window per N/E/S/W mask, open north edge gets a thin wet-green rim, open east/west a shaded side, open south the only cliff (the same ooze compressed and darkened, with a contact shadow); creep = the slime floor laid over the board stone floor (`korpul/floor-a`) with the gloom creep-edge rule (an exposed side fades back to stone); stairs = the board's shared Kor'Pul stair pieces on the slime floor. Parity 1 = ×0.875. Reused unchanged: Kor'Pul floor/brick (+S8 dark) for Grushnak's barracks and SLIMED corner, `gloom/plain` walls for the mushroom thicket, Caldera jungle for Sludgenest L1.

Measured (128 px, parity 0, luminance): slime floor **127.1** (cave floor 135.0, Kor'Pul floor 131.8, Caldera grass 96.5); slime wall **43.4–49.3** (cave wall 51.4, Caldera tree 47.2); creep 117.7 (full) / 122.8 (open); stairs 121.9 / 98.2. Floor − wall ≥ 61%; parity gaps ≥ 12.5%. Floor and wall lean green (G > R, G > B + 8); creep is greener than the stone it lies on. Enforced by `tests/production/test_slime_s10_exporter.py`.

## Visual review

`review/contact-{48,64,96}.png` (+`-gray`), `review/scene-{tunnel,grushnak,sludge}-{48,64}.png` (+`-gray`), and the live frames in `evidence/terrain-s10a-20260930/screenshots/` (local). At 48/64 px the slime family reads as its own set inside the board language: pale sage slime-glazed ground that pieces clearly stand on, and heavy dark glossy-green ooze blocks with a lit rim and a darker south face — the same construction as the cave and mountain walls, so it belongs to the tabletop set while its hue and wet lumps separate it from grey brick, brown cave rock and the brown mushroom thicket. Grushnak's creep reads as a green film spreading over the stone barracks floor, not as a pool or hazard; the pit entrance and stairs use the shared board stair pieces. In grayscale the hierarchy holds: floors/creep light (≈118–127), brick mid (≈90), thicket and slime wall dark (≈45–65).

Weak points: every slime floor cell repeats the same window (visible board rhythm on the 250-cell tunnel); isolated one-cell slime walls in Sludgenest's lake read a little like dark hedges; creep and stone floor differ by hue more than value; Sludgenest L2/L3 are tinted by the zone's own native colour pulse (pink/red phases), which shifts the sage floor warm while keeping the floor/wall gap (≥ 60% in the tinted frames).
