# P1 Kor’Pul terrain contract

Status: **six-design sample integrated; DEFAULT and HIDEOUT controlled live checks passed**. Both `ruins-kor-pul` DEFAULT (`is_hideout` false/nil) and HIDEOUT (true) use the same restricted material vocabulary. This does not complete either zone's full creature/terrain coverage. All 196 runtime PNGs were checked against their manifest paths, SHA256, byte lengths and 128×128 RGBA dimensions. Parent review of `production-sheet.png` and `wall-masks.png` admitted them to isolated live validation; `data/terrain-korpul-manifest.lua` is enabled. Unsupported cells and Kor’Pul Blockout mode retain native visuals. Final cold-start captures follow the edge correction described below.

## Ownership and engine boundary

`CheckerTerrain.lua` owns classification, paths, knowledge snapshots and forest display selection. `Game:checkerApplyTerrain()` delegates to it. Existing Trollmire installation/restoration remains the previous implementation, including its existing limitations; this change does not claim to fix forest tree semantics.

The new Grid superload records basic.lua provenance after native `loadList`, including concrete nice-tile definitions. It does not override movement, opening/closing, digging, cloning, saving, `altered`, or native minimap logic. Its `getMapObjects` adapter emits a separate display Entity during a synchronous Map drawing context. It never sets a P1 `replace_display`, inserts a replacement Grid, or edits `__SAVEINSTEAD`. Native `_mo`/`_last_mo` are borrowed only during the synchronous native minimap call, then restored when the Map drawing context exits, including error exits. This matters because native Grid prototypes can be shared: leaving a per-cell display MO in a Grid could contaminate another cell's native fallback. The C map retains its emitted drawing objects; the rule Grid retains its own original cache. Any external `replace_display` wins immediately.

The Map adapter delegates every native `updateMap` and FOV method. Path/FOV caches therefore continue to derive from the real Grid. An observed change refreshes only that cell and visible cells in its 3×3 neighborhood. Native `apply`, `applyLite`, and `applyExtraLite` trigger local refresh; ESP alone is not terrain observation. Both `seens` and `infovs` must be true. There is no per-frame full-map pass. Existing settings/change-level full redraws remain. With assets unready and no existing knowledge cache, the adapter adds no FOV redraws.

`Map.seens(x,y,value)` direct writes and special reveal implementations that bypass these three FOV callbacks are not newly wrapped. They render on the next native `updateMap`/redisplay. The staged scenes exercised the normal player FOV path; other reveal implementations remain a separate compatibility case.

## Source and final-state whitelist

Native source: `/data/general/grids/basic.lua`, imported by `/data/zones/ruins-kor-pul/grids.lua`. The loader stamps exact `define_as` and a fingerprint of rule/visual fields. A different definition, modified final fingerprint, special callback, foreign replacement, shader/nonidentity tint/texture, exit, special door, or unsupported overlay falls back. A matching name or source image alone is insufficient. Existing saves without provenance safely remain native until native definitions are reloaded; no name-based migration is performed.

Native `engine.Entity:init` initializes each multiplicative tint channel to **1**. The classifier accepts nil or 1 and rejects any other channel value. The first live audit caught the initial overly strict nil-only treatment: all 2,500 HIDEOUT cells fell back. A read-only copied-cell diagnostic isolated that cause (1,813 ordinary walls, 650 floors and 8 closed doors became eligible; 29 remained native). The fix keeps source/signature/interaction guards; it does not broadly permit tinted or custom grids. The standalone test now models the native defaults.

| Material | Accepted native definitions and rules |
| --- | --- |
| stone floor A/B | `FLOOR`; unblocked, no hazard/door/exit/overlay. A/B is deterministic decorative variation, not two rule types. Nice-editor floors with additional visual decorations are conservative fallbacks. |
| ordinary wall | `WALL`, exact numbered/north/south/pillar family emitted by basic.lua; movement/sight blocked, `can_pass.pass_wall=1`, `dig=FLOOR`, air −20, no sense/ESP block. |
| hard wall | Corresponding exact `HARDWALL` family; movement/sight/sense/ESP blocked, air −20, no pass-wall capability or digging. |
| closed door | `DOOR`, `DOOR_HORIZ`, `DOOR_VERT`; exact original open target and dig target, sight blocking, native `is_door`. They deliberately need not have `does_block_move`: native `Grid:block_move` handles the action. |
| open door | `DOOR_OPEN`, `DOOR_HORIZ_OPEN`, `DOOR_OPEN_VERT`; exact close target, no sight/movement block. |

Sealed/vault/lever/glass/old-wall/special-room definitions and stair/exit grids retain native visuals. Room overlays changing a whitelisted definition also fail closed. `__SAVEINSTEAD` and nice-tile source objects retain native meaning; the provenance does not treat the original pre-tiler name as proof that every later display is supported.

## Art integration interface

Six original designs: floor A, floor B, ordinary wall, hard wall, closed door, open door. Contract paths:

```
checker-revised+refined/korpul/<material>-<mask>-<parity>.png
```

`material`: `floor-a`, `floor-b`, `wall`, `hardwall`, `door-closed-horizontal`, `door-closed-vertical`, `door-open-horizontal`, `door-open-vertical`. Door orientations are exports of the same two designs, not additional identity claims. Do not rotate baked light/shadow to produce the other orientation.

- Square RGBA master, recommended 256×256; runtime exports **128×128**, checked at 96/64/48 px. Other resolutions require explicit visual review rather than a runtime code change.
- Runtime files are complete, composited single-cell tiles: floor underneath the object, all edges/shadows inside the cell. No cross-cell overhang, state text, selection ring, or actor disc. Transparent component masters are acceptable; the exporter composites them onto the stone floor before runtime use.
- `parity` is `(x+y)%2`, 0 or 1; A/B selection is independent and deterministic. Floor uses only mask 0. No procedural substitute for the six painted masters.
- Mask uses N=1, E=2, S=4, W=8. A bit means a **last-observed supported ordinary/hard wall** adjacent to this cell. Doors are not walls for this mask. Unknown/unsupported neighbor = no bit. All 16 masks must have deliberate treatment. Wall/hardwall share connectivity, retain their own material.
- This first contract uses square tile boundaries and no diagonal corner cutouts. Four bits do not solve diagonal inner corners. The exporter must not pretend diagonal geometry exists; a later corner-aware contract requires more data and new review.
- Review isolated wall, straight runs, corners, T/cross junctions, diagonal contact, one-cell corridor, mixed ordinary/hard wall, both door axes/states. All geometry remains inside its cell.

`CheckerTerrain.assetPath(kind,orientation,mask,parity,x,y)` is the canonical resolver. `assets.files[path]=true` means an exact reviewed, packaged runtime export; absent paths fall back to the last-observed native picture. `assets.ready=true` is the explicit enable switch, not a player preference and not proof of completeness. Integration must audit actual packaged PNGs against the manifest before enabling. Complete contract: 4 floor exports + 64 wall exports + 128 door exports = **196 runtime files**, not 196 paintings. Export filenames live under `data/gfx/refined/korpul/` before addon path mounting. The mounted manifest is `/data-checker-revised/terrain-korpul-manifest.lua`. Runtime accepts it only when all 196 exact allowlist paths resolve to existing files under the addon terrain directory; a missing/invalid manifest or PNG keeps readiness false. PNG dimensions and hashes are integration checks. The renderer never invents a path outside the allowlist.

## Visibility, memory, clone and save

Knowledge resides in `map._checker_korpul`, keyed by `x+y*w`, as plain data: source identity, final-state fingerprint, kind/orientation, native visual snapshot, last selected path, and whether the tile has been painted. It holds no Grid references, Entity instances, functions, userdata or map objects. Drawing Entities are in a module-local weak-key cache keyed by the individual knowledge record. Deep/full clones or save-restored records rebuild independent drawing caches. No override of engine serialization or clone semantics is introduced.

1. While visible, capture the native visual fields and classification. Observed unsupported/foreign cells discard the prior record and draw natively.
2. While unseen, do not inspect the new Grid to replace the stored classification or native snapshot. An unseen replacement or in-place mutation cannot change this addon's remembered picture.
3. Compute adjacency from knowledge records, never hidden live terrain. Do not recompute a hidden tile's selected path when a neighbor becomes known.
4. Turning Refined off restores the stored **last-observed native visual snapshot**, even when the real hidden Grid has changed. It does not reveal the new hidden native image.
5. Re-observation replaces the record with the actual visible Grid, or falls back for unsupported geometry. Foreign `replace_display` always takes priority, including when unseen; the addon does not override another renderer's memory policy.

Completely unknown cells (`not visible` and `remembers=false`) have an additional visual rule in Refined mode when assets are ready: emit a uniform `invis.png` Entity with **`display_on_seen=false`, `display_on_remember=false`, and `display_on_unknown=false`**. Its selection does not inspect the hidden Grid identity, and it creates no knowledge record or remember flag. Foreign displays retain priority. Already remembered native cells are not erased.

This prevents a confirmed native FBO edge artifact: `src/map.c` draws remembered-capable MOs with `always_show` before applying its soft visibility mask, allowing unknown native brick art to bleed around observed board walls. The HIDEOUT border diagnostic contained exactly 42 `unknown-native` and 55 `visible-painted` cells. After the uniform unknown-cell change, the parent opened the live comparison and confirmed the brick strips disappeared while observed tiles, doors and actors stayed unchanged. Native mode delegates back to native drawing; because the blank MO never remains installed on the Grid, switching Refined → Native → Refined cannot retain the blank as a native cache. The final capture driver also cycles these modes.

Native rules, object/actor display, minimap knowledge, lighting/remember flags and discovery are not replaced. A snapshot exists only for a supported cell actually observed; art readiness does not grant knowledge of unknown cells.

## Checks and remaining live gates

`luajit tests/terrain_contract.lua`: **83 checks**, using native basic.lua definitions plus actual Map/Grid adapter methods in a mocked renderer. Covers native tint defaults and nonidentity rejection, exact nice-tile IDs, source/final-state guards, both layout flags, hidden replacement/in-place change, re-observation, native restore, foreign display, 16 masks, hidden-edge stability, pure records/cache isolation, error cleanup, shared native MO restoration, manifest completeness/path checks, uniform unknown-cell suppression and forest regression. Five additional in-memory adapter assertions checked unknown Refined → Native → Refined and native MO/pointer restoration without changing the maintained test file.

Lua syntax checks passed. Current companion checks: `runtime_modes.lua` 97, `token_mapping.lua` 1,030 for 29 exact identities, `random_identity.lua` 1,160, `clone_display.lua` 1,069. These are source/mock checks; live outcomes below were separately executed by the parent, who owns the sole fixture process.

[Live assertions](../../evidence/runtime-v060/terrain-validation.txt) and [preserved pre-edge-fix game log](../../evidence/runtime-v060/preintegration/pre-edge-fix-game.log) record **both DEFAULT and HIDEOUT** passing:

- `live_korpul_terrain.run(layout)`: real Grid open targets and sight/passability, hidden replacement and same-object change, last-observed native restore, re-observation, foreign replacement, native `DamageType.DIG` plus nice-tile update and dig counters. The test restores its terrain patch/knowledge and checks the player's position, life, energy and global turn.
- `actorDoor(layout)`: calls the actual player's `moveDir`, comparing Native and Refined. On this native revision, the first ordinary-door attempt opens it with **zero displacement and zero energy cost**. The second enters one cell and costs **1,000 energy**, matching `game.energy_to_act * combatMovementSpeed`. Both modes matched in both layouts. The synchronous test temporarily supplies sufficient energy, restores it, and does not advance the world's turn scheduler; it is not a claim that a complete NPC/world turn was simulated.
- `begin()` / `finish()`: actual native asynchronous ZIP write/read of an independent Entity container holding a real Grid and the plain terrain knowledge record. Checks restored provenance/rules, distinct record identity, fresh display cache, hidden remembered rendering and the original native visual snapshot. This is stronger than a table-copy test, but is **not** a complete Map/game save across process restarts.

The unknown-cell fix was additionally verified by a parent-run live hot comparison; final formal screenshots are cold-start captures. No normal user campaign save or online profile was used.

Remaining scope: complete Map/game persistence across process restarts, shallow Map clone callers if any, all special reveal/lighting paths, arbitrary foreign-addon combinations, all room overlays and both layouts' final-level maps, full-zone art coverage, and diagonal corner-aware geometry. Unsupported grids retain native output, and these untested scopes are not inferred from the controlled first-level sample.
