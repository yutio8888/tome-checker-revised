# Monster batch E — offline art review

Scope: `docs/expansion-plan-20260928/CONTRACTS-B5-B7-20260929.md` §2 (batch 6, the
12 recommended zone-finale bosses) — Lady Zoisla the Tidebringer, Urkis the High
Tempest, Golbug the Destroyer, Brotoq the Reaver, Ungolë, Half-Finished Bone Giant,
Kryl-Feijan, Atamathon the Giant Golem, Ritch Great Hive Mother, The Mouth, The
Abomination, Celia. Task packages `art/production/batches/monster-batch-e-{1,2,3}.json`
plus a third-attempt fresh-generation package `monster-batch-e-1b.json` for
lady-zoisla. Handoffs under `art/production/handoffs/monster-batch-e-{1,2,3,1b}/`.
ImageGen foreground single calls via `tools/run_imagegen.py --execute` (17 calls
total, budget 24, max 3/asset). No fixture, no game launch.

## Native contract verification (static source only)

`evidence/monster-batch-e-20260929/source-contracts.json` re-verifies every
target's `name`/`define_as`/`type`/`subtype`/`unique`/display contract directly
against `game/modules/tome/data/zones/{slazish-fen,tempest-peak,reknor,
reknor-escape,ardhungol,blighted-ruins,crypt-kryl-feijan,golem-graveyard,
ritch-tunnels,deep-bellow,last-hope-graveyard}/npcs.lua` and the relevant
`BASE_NPC_{NAGA,SPIDER,BONE_GIANT,MAJOR_DEMON,CONSTRUCT}` parents, plus a visual
inspection of every native `gfx/shockbolt/npc/*.png` target. All 12 match
CONTRACTS-B5-B7-20260929.md §2 exactly; no discrepancy found this round.

11 of 12 are the standard `invis.png` + single `add_mos{display_h=2, display_y=-1}`
native-tall shape. Ritch Great Hive Mother is a plain single top-level `image=`
with no `nice_tile`/`add_mos` anywhere on the leaf. **Atamathon** carries a
documented exception: `golem-graveyard/npcs.lua:27` sets a top-level
`image="npc/atamathon.png"` (64×64) that is a *different* file from the tall
inner body `construct_golem_athamathon_the_giant_golem.png` (64×128); this batch
maps only the verified native-tall contract (`entry.image` = the tall inner
file). With nicer_tiles ON (the checker precondition) this renders correctly as
`native-tall`; with nicer_tiles OFF, `actor.image` stays `npc/atamathon.png` (≠
`entry.image`), `appearance()` correctly declines, and Atamathon shows its
native single icon — a known, intentional partial-fallback path, not invented
or patched around here, matching the survey's own note.

## Base-plate calibration (reusing the batch D-4 fix)

The batch D-4 carpenter/black-ant redraw found this style/camera/disc reference
(steep overhead 3/4, upper-left light, thin charcoal disc) renders measurably
too *bright* by default and calibrated an explicit "render the disc ~8 units
darker than it looks" instruction into the composition field. This batch reused
that instruction verbatim for the first four assets (lady-zoisla, urkis, golbug,
brotoq), then, after three of those four still overshot into `base_drift`
failure (-9.23, -12.21, -15.18) and one landed cleanly (-4.42), recalibrated the
remaining 8 assets to "~4 units darker" (based on a controlled retest on
lady-zoisla: 8-unit ask → -9.23 failed; 4-unit ask → -5.11 passed).

The 4-unit version did **not** reliably fix the remaining assets either
(observed range -9.47 to -12.83 on 4-unit-calibrated fresh generations) —
confirming this metric is dominated by per-composition variance (how much dark
vs. light area the specific creature occupies near the disc's outer ring), not
just the instruction text. The instruction measurably reduces risk (it is why
The Mouth and Celia passed on the first try, and why brotoq's first attempt was
already within 0.5 of tolerance) but cannot guarantee every subject clears ±8.
This is recorded honestly rather than claimed as a full fix.

## Repair-pass overshoot (new finding this batch)

Two metric-driven *brighten* repairs (lady-zoisla attempt 2, asking for ~+9;
ungolë attempt 2, asking for ~+9.47) both overshot dramatically: +52.61 and
+44.24 respectively (roughly 5x the requested correction), far worse than batch
D's previously-documented ~2.5x overshoot on *darkening* edits. After the second
data point, further edit-based brighten-repairs were deliberately not attempted
on the other five base_drift-only candidates (urkis, golbug, half-finished-
bone-giant, kryl-feijan, atamathon, ritch-hive-mother) to avoid wasting each
pack's last call on a near-certain worse result; those stand on their single
fresh-generation attempt and are presented as base_drift-only waiver
candidates instead. Lady-zoisla's actual fix came from a **third, fresh (non-
edit) generation** in a new package (`monster-batch-e-1b`) with a tightened,
more compact composition (weapons held inward instead of raised to the canvas
edge, tail coiled tighter) plus the toned-down 4-unit disc instruction — this,
not a repair edit, is what cleared both `disc_overflow` and `base_drift`
together.

## Generation results

| Identity | Calls | Result | Selected master | base_drift | disc_overflow |
| --- | ---: | --- | --- | ---: | ---: |
| lady-zoisla | 3 | gate pass (attempt 3, fresh gen in e-1b) | `masters/lady-zoisla-v2.png` | -5.11 | 0.8599 |
| brotoq | 2 | gate pass (attempt 2, repair) | `masters/brotoq-v2.png` | -7.93 | 0.8599 |
| the-mouth | 1 | gate pass (attempt 1) | `masters/the-mouth-v1.png` | -6.13* | 0.86* |
| the-abomination | 2 | gate pass (attempt 2, repair) | `masters/the-abomination-v2.png` | -4.45 | 0.8576 |
| celia | 1 | gate pass (attempt 1) | `masters/celia-v1.png` | -7.89* | 0.86* |
| urkis | 1 | **base_drift only**, PENDING waiver | `masters/urkis-v1.png` | -12.21 | 0.8585 (pass) |
| golbug | 1 | **base_drift only**, PENDING waiver | `masters/golbug-v1.png` | -15.18 | 0.8596 (pass) |
| ungolë | 2 | **base_drift only** (attempt 1), PENDING waiver; attempt 2 repair rejected (+44.24, not saved) | `masters/ungole-v1.png` | -9.47 | 0.8585 (pass) |
| half-finished-bone-giant | 1 | **base_drift only**, PENDING waiver | `masters/half-finished-bone-giant-v1.png` | -12.83 | 0.8585 (pass) |
| kryl-feijan | 1 | **base_drift only**, PENDING waiver | `masters/kryl-feijan-v1.png` | -10.97 | 0.8576 (pass) |
| atamathon | 1 | **base_drift only**, PENDING waiver | `masters/atamathon-v1.png` | -10.60 | 0.8585 (pass) |
| ritch-hive-mother | 1 | **base_drift only**, PENDING waiver | `masters/ritch-hive-mother-v1.png` | -10.34 | 0.8576 (pass) |

\* the-mouth/celia figures are from `art/monster-batch-e/export-report.json`
(the 128px export used for the official style gate at `build_monster_art.py`
time); all other figures are from the `run_imagegen.py` call-time gate.

17 calls total (budget 24, max 3/asset — lady-zoisla used all 3, brotoq and
the-abomination used 2, the rest used 1). Every call passed master alpha,
corner alpha and export occupancy; only `disc_overflow` (lady-zoisla attempt 1,
brotoq attempt 1, the-abomination attempt 1 — all fixed by attempt 2) and
`base_drift` ever blocked, and never both at once past attempt 1 except
lady-zoisla's first draft.

The 7 base_drift-only masters are recorded (`receipts/attempt-1.json` in each
pack) and exported once for measurement, but are **not** wired into
`check_token_style.py`'s trusted waiver list, **not** in
`overload/mod/class/CheckerTokens.lua`, and **not** in
`data/token-manifest.json`. Their exact-byte waiver requests are in
`art/production/waivers/monster-batch-e-PENDING-REQUEST.json`, explicitly
marked `PENDING — reviewer approval requested`; nothing in that file is
self-approved or wired in.

## Visual review

Sheets in `art/monster-batch-e/review/` (9 groups × color + grayscale = 18
files), built by `make_review_sheets.py` from the actual 48/64/96 mechanical
exports (shipped assets from their stored `sprites/`; the 7 pending candidates
exported on the fly from their attempt-1 masters purely for this review, which
does not admit them to the catalog).

- **orcs** (golbug PENDING vs. brotoq SHIPPED): clearly separable at every size
  by value (golbug brighter, brass-warmed) and silhouette (upswept horned
  pauldrons + low diagonal sword vs. angular helm + high raised sword).
- **humans** (urkis PENDING vs. celia SHIPPED): trivially separable — urkis's
  bright cyan-white lightning fringe reads as a starburst silhouette even at
  48px against celia's quiet unlit tan-robed figure.
- **horror-corrupted** (existing shipped horned-horror for context, the-mouth
  and the-abomination both SHIPPED): all three read as completely different
  silhouettes at every size in both color and grayscale — upright horned
  minotaur vs. low wide red toothed mass vs. tall pale two-headed spire. This
  is the strongest family separation in the batch.
- **naga** (lady-zoisla SHIPPED, no in-family collision): coiled tail base
  reads clearly at 48px.
- Five solo new-family candidates (ungolë/spiderkin, half-finished-bone-
  giant/undead-giant, kryl-feijan/demon-major, atamathon/construct-golem,
  ritch-hive-mother/insect-ritch, all PENDING) have no catalog sibling to
  collide with; each reads as a distinct, legible silhouette at 48px on its
  own sheet.
- No faction, rank, health, shield or text baked into any master. No native
  alpha cheats (every master is genuine RGBA straight from the tool, verified
  by `art_tasks.py record`'s mode check before the style gate even runs).

## Integration

`overload/mod/class/CheckerTokens.lua`: added `lady-zoisla`, `brotoq`,
`the-mouth`, `the-abomination`, `celia` (exact `name`+`image`+`type`+`subtype`+
`define_as`+`unique=true`, matching the native leaves; catalog 78→83).
`tests/token_mapping.lua` needed no bespoke additions: the file's existing
generic per-catalog-entry loop already builds a positive "resolved nice_tile"
/exact-identity check and a full set of "altered tall body" negative checks
(changed image/display_h/display_y/display_w/display_x/display_scale/shader,
second add_mos element, non-array add_mos, unknown define_as) for every entry
with `unique=true`, purely from being present in `M.catalog` — the same
pattern batch A's 8 guardians and batch B's shax/horned-horror/norgos-guardian
used. 3,407 checks pass (up from 78 catalog entries' worth in the prior run).

`tools/build_monster_art.py` gained `monster-batch-e` in its `--batch` choices;
`art/monster-batch-e/catalog.json` and `selected-masters.json` list the 5
shipped ids and their chosen master files (v2 for lady-zoisla/brotoq/
the-abomination after their repair/redraw rounds, v1 for the-mouth/celia).
`tools/prepare_runtime_art.py` gained `monster-batch-e` at the end of its batch
tuple. `data/token-manifest.json` regenerated via `tools/prepare_runtime_art.py`
as the one and only final step (83 assets now; `version` unchanged at 0.6.24).

## Gates (all pass)

- `for t in tests/*.lua; do ... lua5.1 $t; done` — all 13 scripts pass (token
  mapping 3,407 checks; totals for the others unchanged from before this batch).
- `python3 -m unittest discover -s tests/production -q` — 87 tests, OK.
- `python3 tools/audit_dead_assets.py --check` — `dead assets: none`.
- `git diff --check -- . ':!evidence' ':!art/production/handoffs'` — clean.

## Unfinished / handed back

- Reviewer decision needed on
  `art/production/waivers/monster-batch-e-PENDING-REQUEST.json` (7 candidates,
  base_drift only, magnitudes -9.47 to -15.18 against a ±8 tolerance — see
  table above; not self-approved, not wired in). Until approved these 7
  identities stay native. golbug (-15.18) is the largest overrun in the batch
  and worth a specific look; the other 6 are in the -9.47 to -12.83 range.
- No in-game/runtime validation of any kind (explicitly no fixture, no game
  launch for this task). `visual_review`/`runtime_review` remain `pending` and
  `accepted: false` in every receipt, honestly reflecting that only the
  48/64/96 mechanical-export sheets above have been reviewed, not real
  gameplay. Another agent is running the game fixture and live validation for
  batch D concurrently; batch E's live validation is a separate follow-up not
  attempted here.
- Not committed, not packaged, per this task's explicit instructions.

## Reviewer decision (2026-09-29)

- Shipped without waiver: Lady Zoisla, Brotoq, The Mouth, The Abomination, Celia.
- Base-drift waiver request (all seven fail only base_drift, darker base): **approved** for Urkis (-12.21), Golbug (-15.18), Ungolë (-9.47), Half-Finished Bone Giant (-12.83), Kryl-Feijan (-10.97), Atamathon (-10.60), Ritch Great Hive Mother (-10.34), bound to the exact master and 128px SHA256 in the request file. All read as their specific boss at 48/96px on a mid-green test ground. Ungolë (black spider) and Kryl-Feijan (dark shade) are dark subjects on a dark base and must be checked in-game at 48px; revoke their waivers if they vanish against real floor tiles. Wiring (trusted `monster-batch-e.json`, check_token_style batch list, catalog, tests) is a follow-up.
