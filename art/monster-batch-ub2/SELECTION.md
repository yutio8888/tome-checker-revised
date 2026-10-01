# Monster batch UB-2 selection and admission (2026-10-01)

Third uniques/bosses batch: the ten flat 64x64 identities of UB-2 from
`tmp/rotation/R17-scratch/UB-SELECTION.md` §5 plus the wiring-only Ben Cruthdar,
the Cursed, per `COORDINATOR-DECISIONS.md` (which overrides the earlier plan).
Static source verification, art generation and static art review only. No game
launch, version bump, release packaging or edits to CHANGELOG/README/PROGRESS.

## Identities

| Identity | define_as | Contract | Verdict |
|---|---|---|---|
| Sun Paladin Guren | SUN_PALADIN_GUREN | flat 64x64 default image; cold gunmetal steel, closed crested helm, dark kite shield, sword low (ruling 7 + coordinator redraw) | ACCEPTED (rework) |
| Epoch | EPOCH | flat 64x64 default image; elemental/temporal | ACCEPTED |
| Corrupted Oozemancer | CORRUPTED_OOZEMANCER | flat 64x64 default image; giant/troll | ACCEPTED |
| Zemekkys | ZEMEKKYS | flat 64x64 explicit image; humanoid/shalore | ACCEPTED (rework) |
| Blood Master | RING_MASTER | flat 64x64 default image; humanoid/yaech | ACCEPTED |
| Limmir the Jeweler | LIMMIR | flat 64x64 default image; humanoid/elf | ACCEPTED |
| Protector Myssil | PROTECTOR_MYSSIL | flat 64x64 default image; humanoid/halfling | ACCEPTED |
| Rak'Shor Cultist | CULTIST_RAK_SHOR | flat 64x64 default image; humanoid/orc | ACCEPTED (rework) |
| Shady cornac man | ARENA_AGENT | flat 64x64 default image; humanoid/human | ACCEPTED |
| Tannen | TANNEN | flat 64x64 default image; humanoid/human | ACCEPTED |
| Ben Cruthdar, the Cursed | BEN_CRUTHDAR | flat 64x64 default image; humanoid/human | WIRING-ONLY, reuses the abomination token (ruling 2) |

Every art identity is unique with a bound `define_as` and no `native_tall`
flag. Full source hashes, line anchors and derived fields are in
`../evidence/monster-batch-ub2-20261001/source-contracts.json`.

## Native portrait, not the plan

The plan's fashion notes were checked against the actual 64x64 PNGs (viewed at
4x-7x nearest in `refs/native-identities.png`) and corrected:

- Zemekkys is **bare-headed** with layered blue robes, chevron mantle, belt,
  blue trousers, boots and **empty hands** (no hat, no staff).
- Corrupted Oozemancer is a **broad hunched** green blight-troll with low head,
  red eyes and out-held clawed arms (not slim).
- Rak'Shor Cultist is a hooded, **uncrowned and staff-less** orc in a maroon-red
  robe with rust trim and out-held empty hands.
- Shady cornac man is **bare-headed** under a teal cloak over a pale striped
  tunic, hand at the hip, not a hooded swordsman.
- Guren: first master read as warm bronze-gold armour, unfaithful to the native
  dark gunmetal sprite and too close to the gold paladins. Redrawn on coordinator
  order in `monster-batch-ub2-rework-2`: cold gunmetal steel dominant, closed
  crested helm, dark kite shield with a small gold sun device, long sword held
  low/diagonal, gold reduced to a rim light/halo that keeps the luminance floor
  (80.74). The v1 master is kept under `superseded/`.

## Family separation at 48px

Sheets with shipped kin at 48/64/96 colour+grayscale and a native 2x column:
`review/sun-paladins-*` (Guren vs the gold hammer human-sun-paladin, Rodmour,
Aluin, Argoniel, Elandar), `review/temporal-*` (Epoch's chaotic blue-yellow
storm vs segmented telugoroth/teluvorta and the dark stalker, magenta defiler
and white chronolith pair), `review/trolls-*` (broad green Oozemancer vs the
bronze/brown trolls and shax), `review/elf-story-*` (bare-headed blue Zemekkys
and cream-green Limmir vs Fillarel, the archer, the elf casters and Tarelion),
`review/yaech-*` (white sword-bearing Blood Master vs Murgol and the robed
yaech), `review/orc-casters-*` (red-hooded Cultist vs the blue-hooded
necromancer, crowned rak-shor, armoured ukruk and the elemental casters),
`review/human-story-*` (teal-cloaked Shady and gold-robed open-armed Tannen vs
the necromancer, assassin lord, Subject Z, the Possessed, Celia, Harno, Urkis)
and `review/short-proportions-*` (stocky greatsword Myssil vs the tall human
uniques and the halfling guard; coordinator ruling 8). `review/wiring-
ben-cruthdar-*` shows the native PNG, the abomination token and the
byte-identical wiring token. All tokens stay readable on the ten real floors in
`review/floor-readability-48*`.

## Art production

Serial `tools/run_imagegen.py` calls only, defaults `gpt-6.1-sol` +
`--ephemeral`, strictly one at a time. **15 calls, all recorded**: 13
`recorded`, 2 `style-gate-rejected`. Ten first attempts succeeded. Sun Paladin
Guren was redrawn on coordinator order (warm bronze-gold → cold gunmetal steel
with a gold rim-light/halo; v1 kept under `superseded/`). Zemekkys and
Rak'Shor Cultist passed the disc geometry but measured below the unchanged 65
masked-body floor (63.64 / 49.89); their in-pack repairs both failed the disc
door with positive base drift (+11.36 / +8.82). Fresh single-purpose rework
packs anchored on the first master then produced the selected masters
(zemekkys-rework-v1 98.67, rak-shor-cultist-rework-v1 75.43). All first masters
and the two failed repair receipts are retained. No PENDING waiver request, no
gate threshold or test floor changed, no waiver file.

## Gate results

- Isolated `git archive HEAD` copy + UB-2 changes: all non-live Lua tests and
  487 production tests pass; `audit_dead_assets.py --check` finds none; scoped
  staged whitespace check passes.
- `token_mapping`: 38,132 checks / 462 identities.
