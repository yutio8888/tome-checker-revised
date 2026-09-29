# Monster batch D — offline art review

Scope: `docs/expansion-plan-20260928/MONSTER-GAP-20260929.md` 批次 2 (E1b jellies/oozes)
and 批次 4 (E3 Rhaloren camp + ants). Task packages
`art/production/batches/monster-batch-d-1.json` and `monster-batch-d-2.json`, handoffs
`art/production/handoffs/monster-batch-d-1/` and `monster-batch-d-2/`. ImageGen
foreground single calls via `tools/run_imagegen.py --execute` (13 calls total, budget
16, max 2/asset). No fixture, no game launch.

## Native contract verification (static source only)

`evidence/monster-batch-d-20260929/source-contracts.json` records every target's
`name`/`type`/`subtype`/`unique`/`image=` exactly as read from
`game/modules/tome/data/general/npcs/{jelly,ooze,ant,elven-warrior,elven-caster}.lua`.

**Eligible** (explicit `image=` on the leaf, no equip/add_mos/shader/moddable_tile
anywhere in the chain): red jelly, blue jelly, giant white/brown/carpenter/blue/
yellow/black ant.

**Kept native**: green ooze, crimson ooze, gelatinous cube, Malevolent Dimensional
Jelly (none has an `image=`; the four already-shipped ooze colours were only
admitted after E1's isolated-fixture resolution of their runtime `actor.image`,
which this no-fixture task cannot repeat) and elven guard / mean looking elven
guard / elven mage / elven tempest (no `image=`; native paper-doll body plus
`resolvers.equip` drawing weapon/armour from the item pool at spawn — not a
deterministic single appearance, and equipment/paper-doll variants are outside the
approved production route per AGENTS.md).

## Generation results

| Identity | Calls | Result | Selected master | base_drift |
| --- | ---: | --- | --- | ---: |
| red jelly | 1 | gate pass | `masters/red-jelly-v1.png` | +0.49 |
| blue jelly | 1 | gate pass | `masters/blue-jelly-v1.png` | +1.54 |
| giant white ant | 1 | gate pass | `masters/giant-white-ant-v1.png` | +7.61 |
| giant yellow ant | 2 | gate pass (attempt 2) | `masters/giant-yellow-ant-v1.png` | +4.76 |
| giant brown ant | 2 | **base_drift only**, both attempts | `masters/giant-brown-ant-v1.png` (attempt 2, better) | +8.39 (attempt 1: +11.69) |
| giant carpenter ant | 2 | **base_drift only**, both attempts | `masters/giant-carpenter-ant-v1.png` (attempt 1, better) | +10.49 (attempt 2: +13.53) |
| giant blue ant | 2 | **base_drift only**, both attempts | `masters/giant-blue-ant-v1.png` (attempt 2, better) | +8.45 (attempt 1: +8.62) |
| giant black ant | 2 | **base_drift only**, both attempts | `masters/giant-black-ant-v1.png` (attempt 1, better) | +8.97 (attempt 2: +10.54) |

Every one of the 13 calls passed alpha, disc_overflow, corner_alpha and
export_occupancy; only base_drift ever blocked, and always alone. The four
base_drift-only masters are recorded (`receipts/attempt-1.json` in each pack) and
exported once for measurement, but are **not** wired into `check_token_style.py`'s
trusted waiver list, **not** in `overload/mod/class/CheckerTokens.lua`, and **not**
in `data/token-manifest.json`. Their exact-byte waiver requests are in
`art/production/waivers/monster-batch-d-PENDING-REQUEST.json`, explicitly marked
`PENDING — reviewer approval requested`; nothing in that file is self-approved.

## Visual review

Sheets: [jellies colour](review/jellies-color-48-64-96.png) /
[grayscale](review/jellies-grayscale-48-64-96.png);
[ants colour](review/ants-color-48-64-96.png) /
[grayscale](review/ants-grayscale-48-64-96.png), built by
`make_review_sheets.py` from the actual 48/64/96 mechanical exports (new assets
exported on the fly from their masters; the four already-shipped jellies read from
their stored `art/monsters-e1-gel/exports/`).

- **Jelly family (6, complete)**: red jelly is a 4-5 lobe clover cluster with dark
  maroon seed-like inclusions clustered at the centre — distinct at 48px from
  green jelly's smaller, evenly stippled single dome even though both are
  warm/round-ish silhouettes; the lobe/groove structure and centre inclusions read
  as a different shape, not just a different colour. Blue jelly is a smooth single
  dome with a dark spiral swirl visible even at 48px grayscale, unlike black
  jelly's flat sagging tar mound with a bright rim edge. All six members are
  readable and mutually distinct in both colour and grayscale at every size.
- **Ant family (6, new)**: white and yellow both read as bright/glossy but clearly
  separate by value (white is the family's brightest, near-neutral; yellow is a
  warmer mid-tone with more internal shading contrast). Carpenter and black share
  the native colour BLACK; they separate by silhouette (carpenter's oversized
  forward pincers vs black's plain mandibles and jagged leg texture) and finish
  (carpenter's glossy rim-lit sheen vs black's duller matte body) — this is the
  hardest pair in the batch and the one most worth a second look at real 48px
  in-context before shipping, especially since both are currently in the
  base_drift-waiver-pending group. Brown is the only bristly/matte-textured
  member, unmistakable from the five glossy siblings by silhouette alone.
- No faction, rank, health, shield or text baked into any master. No native alpha
  cheats (all masters are genuine RGBA from the tool, verified by
  `art_tasks.py record`'s mode check before the style gate even runs).

## Integration

`overload/mod/class/CheckerTokens.lua`: added `red-jelly`, `blue-jelly`,
`giant-white-ant`, `giant-yellow-ant` (exact `name`+`image`+`type`+`subtype`,
matching the native leaves). `tests/token_mapping.lua`: positive exact-identity
checks for all four, plus negative "does not borrow a sibling's image" checks for
both jelly pairs (red vs blue vs the two nearest shipped siblings) and both ant
pairs (white vs yellow), plus explicit checks that the four base_drift-pending ant
names still resolve to nothing (they are not in the catalog). `tools/build_monster_art.py`
and `tools/prepare_runtime_art.py` gained `monster-batch-d` in their batch-name
list/order (appended at the end, after `monster-batch-c`). `data/token-manifest.json`
regenerated via `tools/prepare_runtime_art.py` as the last step (74 assets now;
`version` unchanged at whatever `init.lua` already carried).

## Unfinished / handed back

- Reviewer decision needed on `art/production/waivers/monster-batch-d-PENDING-REQUEST.json`
  (4 candidates, base_drift only, see table above). Until approved these four ant
  colours stay native.
- green ooze / crimson ooze / gelatinous cube / Malevolent Dimensional Jelly need
  isolated-fixture resolution of their runtime `actor.image` (same method as
  `evidence/e1-art-gate`) before any art task can even start; out of scope here
  (no fixture).
- elven guard / mean looking elven guard / elven mage / elven tempest need a
  paper-doll/equipment design decision (how to represent randomized gear as a
  stable token, and how to avoid colliding with the player elf token) before any
  art task; out of scope here.
- No in-game/runtime validation of any kind (explicitly no fixture, no game launch
  for this task). `visual_review`/`runtime_review` remain `pending` and
  `accepted: false` in every receipt, honestly reflecting that only the 48/64/96
  mechanical-export sheets above have been reviewed, not real gameplay.

## Reviewer decision (2026-09-29)

- Accepted and shipped: red jelly, blue jelly, giant white ant, giant yellow ant (all pass the gate without waiver).
- Waiver request `art/production/waivers/monster-batch-d-PENDING-REQUEST.json`:
  - giant brown ant (+8.39) and giant blue ant (+8.45): approved in principle (overrun under 0.5, silhouettes distinct). Not yet wired in; integration (trusted `monster-batch-d.json`, check_token_style batch list, catalog/tests) is a follow-up task.
  - giant carpenter ant (+10.49) and giant black ant (+8.97): rejected. At 48px they are nearly indistinguishable from each other (both black, pincers too small to read); both stay native until a redraw separates them by shape/value.
- Kept-native list (unresolved ooze images, paper-doll elves) confirmed. The shipped E1 oozes were admitted after fixture resolution of their runtime image; the four remaining ooze/jelly identities may follow the same fixture route later.

## Waiver integration + carpenter/black redraw (2026-09-29 follow-up)

**Waiver integration.** `art/production/waivers/monster-batch-d.json` (batch-B-format trusted file, exact master + 128px export SHA-256, `base_drift`-only) now carries the reviewer-approved giant-brown-ant and giant-blue-ant entries; `tools/check_token_style.py` consults `('monster-batch-a', 'monster-batch-b', 'monster-batch-d')`. Both were added to `overload/mod/class/CheckerTokens.lua`, `tests/token_mapping.lua` and `data/token-manifest.json` (76 assets before the redraw below). `art/production/waivers/monster-batch-d-PENDING-REQUEST.json` no longer has an active request; brown/blue's entries were removed (superseded by the trusted file) and carpenter/black's rejected-draft entries are kept only as a historical record pointing at the redraw below.

**Carpenter/black redraw.** Native-source study (`game/modules/tome/data/gfx/shockbolt/npc/{carpenter_ant,black_ant}.png` inspected at 8x, `game/modules/tome/data/general/npcs/ant.lua` lines 63/120) found a genuine native cue the first draft under-used: carpenter's mandibles are visibly pale ivory-grey against its jet-black head (an internal value contrast), while black's mandibles are the same dark tone as its head (no contrast at all) — matching the native `desc` text ("huge mandibles" vs plain "a large black ant"). The redraw brief (`art/production/batches/monster-batch-d-3.json`) leaned on this value cue plus a raised/quick stance for carpenter vs. a hunched/compact stance for black, instead of the rejected draft's reliance on rim-light/gloss.

Three rounds, 6 ImageGen calls total (budget: <=6 total, <=3/asset):
1. `monster-batch-d-3` fresh generation (1 call/asset): base_drift +12.14 (carpenter) / +12.27 (black) — silhouette/value cues looked right on inspection, but both failed only `base_drift`, worse than the original draft.
2. `monster-batch-d-3` metric-driven repair (1 call/asset, `tools/run_imagegen.py repair`, auto-computed "darken ~12 units"): overshot to -18.90 (carpenter) / -20.07 (black) — confirmed the tool applies roughly 2.5x the requested correction on an edit pass.
3. `monster-batch-d-4` fresh generation with a calibrated prompt (1 call/asset, final attempt): composition text was rewritten to cite the measured +12/-19.5 pattern and ask for an explicit, deliberate 8-unit-darker bias on the disc only (not the creature) — landed at base_drift **-7.27** (carpenter) / **-5.43** (black), both within +-8 with **no waiver**. `disc_overflow`, `corner_alpha`, `export_occupancy` and master alpha all passed cleanly on every attempt; only `base_drift` ever blocked.

Selected masters: `art/monster-batch-d/masters/giant-carpenter-ant-redraw2-v1.png`, `giant-black-ant-redraw2-v1.png`. The rejected draft and the two intermediate misses are kept on disk for the record (`giant-{carpenter,black}-ant-v1.png` = original rejected draft; `giant-{carpenter,black}-ant-redraw-v1.png` = monster-batch-d-3 attempt 1, not saved to catalog).

**Visual review (48/64/96, strict).** `art/monster-batch-d/review/ants-color-48-64-96.png` / `ants-grayscale-48-64-96.png` (all six shipped ants) and `ants-carpenter-black-redraw-{color,grayscale}-48-64-96.png` (rejected draft vs. both redraw rounds, all six rows). At 48px the rejected draft's carpenter and black rows are genuinely almost indistinguishable blobs — the original rejection was correct. The shipped redraw shows a small but real and consistent bright ivory patch (carpenter's mandibles) against a uniformly dark blob (black) at every size, in both color and grayscale, so the cue is a value/shape distinction and survives desaturation, not a hue trick. At 64/96px the pale open mandibles vs. the plain closed head are unambiguous. Carpenter/black remain the tightest pair in the family and the grayscale sheet is the one to re-check if this pairing is ever revisited, but at 48px they no longer read as the same silhouette. Accepting and shipping both.

Integration: both added to `overload/mod/class/CheckerTokens.lua`, `tests/token_mapping.lua` (exact-match plus full 6-way "cannot borrow a sibling's image" negative coverage) and `data/token-manifest.json` via `tools/prepare_runtime_art.py` (78 assets, `version` unchanged). `art/monster-batch-d/catalog.json` and `selected-masters.json` now list all six ants.
