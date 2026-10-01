# Monster batch TA-1 selection and admission (2026-10-01)

First town-resident batch; exactly the thirteen TA-1 identities from
`tmp/rotation/R16-scratch/TA-SELECTION.md` and coordinator decisions 7/8.
Static source verification, art generation and static art review only. No game
launch, version bump, release packaging or edits to CHANGELOG/README/PROGRESS.

## Identities

| Identity | define_as | Contract | Verdict |
|---|---|---|---|
| apprentice mage | none | flat 64x64 `npc/humanoid_human_apprentice_mage.png` | ACCEPTED |
| pyromancer | none | nice_tile single 64x128 body; `native_tall=true` | ACCEPTED (v2) |
| cryomancer | none | nice_tile single 64x128 body; `native_tall=true` | ACCEPTED |
| geomancer | none | nice_tile single 64x128 body; `native_tall=true` | ACCEPTED |
| tempest | none | nice_tile single 64x128 body; `native_tall=true` | ACCEPTED |
| human guard | none | flat 64x64 default image (sunwall-town leaf) | ACCEPTED (v3 rework) |
| derth guard | none | flat 64x64 default image | ACCEPTED (v2) |
| last hope guard | none | flat 64x64 default image | ACCEPTED |
| halfling guard | none | flat 64x64 default image; subtype halfling | ACCEPTED |
| dwarven guard | none | flat 64x64 default image; subtype dwarf | ACCEPTED |
| elvala guard | none | flat 64x64 default image; subtype shalore | ACCEPTED |
| slaver | none | flat 64x64 default image; subtype yaech | ACCEPTED |
| enthralled slave | none | flat 64x64 default image; subtype human | ACCEPTED |
| (slaver escort) | none | make_escort same name/type/subtype/image | same token, no new entry |

All thirteen are non-unique with no `define_as`. Each native name has exactly
one actor leaf in `data/` (grepped): the Angolwen mages in
`zones/town-angolwen/npcs.lua`, the human guard in `general/npcs/sunwall-town.lua`
(loaded by `town-gates-of-morning`), derth/last-hope/halfling guards in their
town files, dwarven guard in `town-iron-council`, elvala guard in `town-elvala`,
and the two Ring of Blood residents in `zones/ring-of-blood/npcs.lua`. No leaf
or base sets `shader`, `moddable_tile`, `anim`, `add_displays` or `auto_classes`.
Full source hashes, line anchors and derived fields are in
`evidence/monster-batch-ta1-20261001/source-contracts.json`.

Tall/body handling: the four elemental mages use the native
`resolvers.nice_tile{image="invis.png", add_mos={{image=..., display_h=2,
display_y=-1}}}` body and therefore carry `native_tall=true`
(`nativeTallImage` requires `entry.unique or entry.native_tall`). The apprentice
mage and all six guards plus the two Ring of Blood residents are flat
default-name bodies.

Slaver escort (coordinator decision 7): `make_escort` builds two
`{type="humanoid", subtype="human", name="enthralled slave"}` actors with the
same default image, i.e. the same body as the resident leaf. They wear the
`enthralled-slave` token through the ordinary exact-identity path; no separate
escort entry, alias or variant is added.

## Same-body / rename scan

No talent, timed effect, map/vault or zone constructor renames or copies these
thirteen identities other than the slaver escort above. No name/image/body
alias or same-body variant is added for TA-1. Different-name sprite reuses
(e.g. the unmapped "Novice mage", which uses the apprentice-mage PNG) stay
native because the token matches on name+type+subtype+image.

## Art production

Serial `tools/run_imagegen.py` calls only, default `gpt-6.1-sol` + `--ephemeral`,
strictly one at a time. **17 calls, all recorded**: 13 first attempts, three
luminance refinements and one coordinator-requested human-guard rework.

- pyromancer v1 masked-body luminance 61.57 (< unchanged 65 floor); v2 brightens
  the crimson robe/hat with broad rose-gold upper-left planes → 87.94.
- derth-guard v1 62.13; v2 lifts the hood/leather to warm light brown → 83.89.
- human-guard v1 64.91; v2 85.27. Coordinator review of dcb5c982 rejected the
  selected v2 as too close to the shipped elven-guard and unfaithful to native
  `npc/humanoid_human_human_guard.png`. Separately reviewed rework pack
  `monster-batch-ta1-rework-1` (refinement brief, one call) draws the native
  brown studded leather jerkin with shoulder pads, bare head, green trousers,
  out-held grey steel heater shield and diagonal sword, with no green tabard or
  green shield; v3 masked-body luminance 67.43. v1/v2 masters are retained.

The two luminance refinements use human-written reviews (four required fields)
through `tools/art_tasks.py repair`; the human-guard rework uses a separately
reviewed `refinement` brief in a fresh pack. All superseded masters are
retained. No PENDING waiver request, no gate threshold or test floor changed, no
waiver file.

## Static review

Family sheets with shipped siblings at 48/64/96 (colour + grayscale):
`review/angolwen-mages-*`, `review/guards-*`, `review/ring-of-blood-*`.
Real-floor 48px sheets and their 1x/2x variants: `review/floor-readability-48*`.
The four mages separate structurally (no-hat/no-staff apprentice; diagonal low
staff + ember; near-vertical staff + ice shards; short conical hat + rune cube
+ wide stance; raised staff + lightning). The six guards separate structurally
by head treatment, weapon and shield shape (kite sword, round targe + mace,
closed sallet plate, halfling cap + club, dwarf helm + two-hand axe, elven
crest + leaf shield), not colour alone. Static review only; live checks remain
a separate task.

## Gate results

- Isolated `git archive HEAD` copy + TA-1 changes: all non-live Lua tests and
  468 production tests pass; `audit_dead_assets.py --check` finds none; scoped
  staged whitespace check passes.
- `token_mapping`: 36,550 checks / 442 identities.
