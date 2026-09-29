# Kor’Pul stone stairs and world exit — v1

2026-09-27. Three original architectural sprites generated with the built-in `image_gen__imagegen` tool, one independent call per asset. No CLI fallback, procedural replacement drawing, manual retouching, background extraction or recoloring was used. Each source and each 48/64 export was visually inspected; the full review sheet was then inspected at its native size.

| Asset | Exact intended native identity | Distinguishing shape |
| --- | --- | --- |
| stairs-up | UP | Raised pale staircase, full run of broad treads and elevated landing |
| stairs-down | DOWN | Low enclosed rectangular stone rim, opaque dark well and descending treads |
| stairs-world | UP_WILDERNESS | Rounded stone arch, bright surface vista, short approach steps, folded map emblem on crown |

The original RGBA PNGs are preserved in `masters/`; exact prompts are in `prompts/`; generated source locations and tool output hints are in `provenance.json`. Prior Kor’Pul floor and production-sheet references were visually inspected before generating; their paths and hashes are recorded in `references/inspected.json`.

## Export and runtime contract

`node art/terrain-korpul-exits-v1/export.cjs` compiles and uses the existing `tools/export_token.c`: visible bounds fit to 86% of the cell, then premultiplied-alpha area downsampling. It produces 48/64/96/128/256px PNGs, copies the three 256px files to `data/gfx/refined/korpul/stairs-{up,down,world}.png`, and writes the isolated three-file `data/terrain-korpul-stairs-manifest.lua`. `export-report.json` records every source and export hash, crop window and bound. `runtime-manifest.json` records the exact runtime paths and hashes.

Foreground only: runtime must put the existing parity-aware Kor’Pul floor below each sprite. The dark well and daylight window have generated center alpha 252/255: they are visually near-opaque, with approximately 1.2% base-floor contribution. This original alpha was preserved rather than clamped. No part occupies an adjacent tile. Existing 196 terrain PNGs and their manifest are untouched by this exporter. This art package does not alter native level-change rules, gameplay callbacks, observation or memory.

## Visual review

`review/production-sheet.png` is a browser screenshot of `review/index.html`, with actual-size 48/64/96/128px samples over an existing floor, CSS grayscale comparison and native-alpha checkerboard. It is an art review, not an engine screenshot or a player blind test. `review/capture-report.json` verifies sample dimensions and image loads.

- At 48px the pale rising tread run, black recessed rectangle and round bright arch remain distinct, including in grayscale.
- At 64/96/128px the stone blocks and stair depth become clearer, and the stone palette remains consistent with the existing greige floor.
- The map badge reads as a small folded plaque at 48px. Its winding route detail becomes legible only at larger sizes; the primary WORLD identifier is the rounded arch and daylight center.
- The masters show tiny colored fringe pixels when enlarged against a black alpha viewer. The existing premultiplied filter prevents hidden RGB contamination: after export, no visible yellow/red fringe was found in the 48/64 direct inspection or the floor/checkerboard review sheet. No source color pixels were manually removed.
- `review/alpha-validation.json` records decoded alpha counts for all three masters and fifteen exports. All have transparent exterior pixels, near-opaque subject pixels (at least 248/255), center alpha 252/255, and no visible outer-edge alpha above 8/255. Masters contain faint outer-edge noise; the 256px DOWN export retains three nearly transparent edge pixels. 48/64/96/128px exports have fully transparent outer edges. No alpha was erased or clamped.

To recapture the sheet with the already cached browser dependencies:

```sh
LD_LIBRARY_PATH=~/.cache/sgstory-chrome-deps/usr/lib/x86_64-linux-gnu node tools/capture_monster_review.cjs < art/terrain-korpul-exits-v1/review/capture-config.json
LD_LIBRARY_PATH=~/.cache/sgstory-chrome-deps/usr/lib/x86_64-linux-gnu node art/terrain-korpul-exits-v1/review/validate-alpha.cjs
```

Main agent owns runtime acceptance, release packaging, documentation integration and the iteration commit. This art task did not launch the game or commit files.
