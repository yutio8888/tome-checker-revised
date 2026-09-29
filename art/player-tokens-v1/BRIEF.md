# Player tokens v1: 14 native body families (prep only, no calls made)

Native identity: **body family**, not race/subrace/class. Family = `descriptor.subrace x
descriptor.sex -> moddable_tile`, per `overload/mod/class/CheckerPlayerTokens.lua`
(`M.families`/`M.moddable`/`M.keys`) and `docs/player-token-plan-20260928/PLAN.md`. 14 families:
`human_male`, `human_female`, `elf_male`, `elf_female`, `dwarf_male`, `dwarf_female`,
`halfling_male`, `halfling_female`, `ogre_male`, `ogre_female`, `yeek`, `ghoul`, `skeleton`,
`runic_golem`. Class, equipment and cosmetics are ignored by design: the art never follows
them, and one image serves every class and every gear set of that family. Lich, DLC subraces
and tutorial subraces are out of scope (see `CheckerPlayerTokens.lua` comments).

Task packages are split into four manifests under `art/production/batches/` and prepared into
matching directories under `art/production/handoffs/`:

| Package (`batch_id`) | Assets | Grouping rationale |
| --- | --- | --- |
| `player-tokens-v1-human-elf` | human_male, human_female, elf_male, elf_female | Sexed pair x 2 families; human is the baseline, elf is the first differentiated family (ears/build) |
| `player-tokens-v1-dwarf-halfling` | dwarf_male, dwarf_female, halfling_male, halfling_female | Sexed pair x 2 families; the hardest same-scale separation (proportion/beard) |
| `player-tokens-v1-ogre-yeek` | ogre_male, ogre_female, yeek | Ogre sexed pair plus the one small unisex family that doesn't pair with a family of its own |
| `player-tokens-v1-ghoul-skeleton-golem` | ghoul, skeleton, runic_golem | The three remaining unisex families, grouped because they must mutually separate by value/hue against the same dark disc |

All 14 assets are `kind: "player"`, `gate: "ready"`, `max_attempts: 2`. Ceiling: 14 x 2 = **28**
calls, matching the approved budget. Masters, once actually generated, land at
`art/player-tokens-v1/masters/<asset-id>-v1.png`.

## Shared visual spec

Same tabletop token language as the monster set (`art/production/templates/player.txt`,
new sibling of `templates/creature.txt`): steep overhead three-quarter camera, upper-left
soft light, matte painted miniature finish, thin charcoal-brown disc with a restrained
bronze-grey bevel at ~82% of canvas width, outer sixth of the disc radius kept bare, native
RGBA alpha with fully transparent corners (explicitly required in every prompt — the known
failure mode is a flat RGB image with a painted checkerboard backdrop standing in for
transparency).

Player-specific additions on top of the creature contract:

- **Neutral standing pose only**: weight even on both feet, arms relaxed, hands empty.
- **Plain traveller's clothes only**: simple tunic/dress, trousers/skirt, belt, boots or
  bare feet, at most a short plain cloak. No weapon, shield, tool, armour plate, jewellery,
  glow or class emblem — the figure must not read as any specific class.
- **Family separation, four required pairs** (baked into the template as fixed prose, not
  left to per-asset text alone):
  - human vs elf: elf keeps visibly pointed ear tips clear of the hairline and a leaner,
    longer-limbed build; human keeps rounded ears and a heavier average frame.
  - dwarf vs halfling: dwarf stays stocky, wide-shouldered and (male) bearded, and is
    noticeably shorter/broader than human/elf; halfling is smaller again, with a
    proportionally larger, rounder, child-like head and no beard. Neither may be a
    same-body-different-size recolor of the other.
  - male vs female of the same family: differ in silhouette/proportion (shoulder-to-hip
    taper, frame width, hairstyle silhouette), never only by palette or an accessory swap.
  - ghoul / skeleton / runic golem: each holds its own value+hue band against the disc so
    none collapses into one dark humanoid blob — ghoul is mottled rotting green-brown flesh,
    skeleton is pale bone-white/grey openwork bone, runic golem is mid-grey carved stone with
    dark incised rune lines.

## References per asset

Every asset uses exactly two references:

1. **style** — `art/monsters-v6/masters/bandit-v1.png` (the same well-established anchor
   nearly every monster batch reuses, confirmed as the currently accepted `bandit` master via
   `data/token-manifest.json`'s `master_sha256`). It is a bipedal humanoid on the correct disc,
   so it anchors camera/disc/finish *and* general proportion register; the prompt explicitly
   tells the model not to copy its crouching pose, bald head or daggers.
2. **identity** — the family's own native unequipped paper-doll base body,
   `game/modules/tome/data/gfx/shockbolt/player/<family>/base_01.png` (skin-tone option 1 of
   several; any option is equally native). Verified present, correctly sized (128x128, except
   128x256 for the two taller ogre files) and distinct per family by direct hash comparison —
   see the table below.

No second/family-contrast reference image was added on top of these two: the required
separations (human/elf, dwarf/halfling, sexes, ghoul/skeleton/golem) are well-documented,
lore-stable body differences already visible in each family's own doll image, so they are
carried as fixed template prose plus per-asset `contrast` text instead of an extra pinned
image citing a sibling asset that doesn't exist yet.

## Reference image per family (native doll, `base_01.png`)

| Family | Doll path | SHA-256 (16) | Size |
| --- | --- | --- | --- |
| human_male | `game/modules/tome/data/gfx/shockbolt/player/human_male/base_01.png` | `fee7e9005cfcd08d` | 128x128 |
| human_female | `.../human_female/base_01.png` | `17b861e6a8837812` | 128x128 |
| elf_male | `.../elf_male/base_01.png` | `3e1e472e3d74a215` | 128x128 |
| elf_female | `.../elf_female/base_01.png` | `1e523a43b96516c3` | 128x128 |
| dwarf_male | `.../dwarf_male/base_01.png` | `8dfa4af19147f66e` | 128x128 |
| dwarf_female | `.../dwarf_female/base_01.png` | `9e8614199cca66e0` | 128x128 |
| halfling_male | `.../halfling_male/base_01.png` | `1aa1ba5302c445f5` | 128x128 |
| halfling_female | `.../halfling_female/base_01.png` | `1cdaa823506a4b4d` | 128x128 |
| ogre_male | `.../ogre_male/base_01.png` | `ec76b88528ea4619` | 128x256 |
| ogre_female | `.../ogre_female/base_01.png` | `6b2df71180258170` | 128x256 |
| yeek | `.../yeek/base_01.png` | `8585dfafe06fa75b` | 128x128 |
| ghoul | `.../ghoul/base_01.png` | `2cb59444fe90353e` | 128x128 |
| skeleton | `.../skeleton/base_01.png` | `eb72fb03da6537c1` | 128x128 |
| runic_golem | `.../runic_golem/base_01.png` | `07e83128d99d3276` | 128x128 |

Visual spot check (main agent viewed 9 of the 14, one per distinct silhouette family) confirms
these are genuinely unequipped/nude native bodies, not ASCII overlays, tutorial art, Lich
variants or shadow/artifice cosmetics: elf shows clear pointed ears, dwarf/halfling show the
expected stocky-vs-small-headed proportion split, skeleton/ghoul/runic golem are already
correctly bone-white/mottled-green/carved-stone in the native art. Yeek's native doll is
already fur-covered with large dark eyes rather than bare skin — treated as its native
identity, not a costume to strip.

## Provenance (`sources`, distinct from `references`)

Each asset's `sources` pins two kinds of evidence, both checked mechanically by
`tools/art_tasks.py`'s new `player_contract()`:

1. The birth descriptor line(s) in `game/modules/tome/data/birth/races/*.lua` that set
   `moddable_tile = "<template>"` for every subrace expanding to this family (e.g. `human_male`
   pins both `Higher` at `human.lua:149` and `Cornac` at `human.lua:181`, since both share the
   family). Ghoul/skeleton/runic golem pin their one subrace each; the skeleton pin is
   `undead.lua:223` specifically, **not** the Lich cosmetic block later in the same file, which
   reuses the same `moddable_tile` string but is reached only by post-birth conversion and is
   out of scope.
2. The same native doll `base_01.png` named above, pinned a second time here (by hash only, no
   text anchor) as the audit-trail proof that the identity reference image really is this
   family's own native art.

## Verification against the runtime contract

`overload/mod/class/CheckerPlayerTokens.lua`'s `M.families` array was read and matches the
`PLAYER_FAMILIES` dict added to `tools/art_tasks.py` exactly (14 entries, same names, same
`#sex#` templates). `M.keys` was cross-checked against the birth race files to confirm which
subraces are genuinely sex-restricted natively (Ghoul, Skeleton, Runic Golem: `sex.__ALL__ =
"disallow", sex.Male = "allow"` in `undead.lua`/`construct.lua` — single-sex families, not an
art-production shortcut).

## Ambiguous / missing references

None found. Every one of the 14 families has a present, correctly named, distinctly-hashed
`base_01.png`, and every birth descriptor line exists at the cited path/line with the expected
`moddable_tile` text. No placeholder or fixture art (`data/gfx/hero.png`, the fixture
`checker_hero` demo token) was used anywhere in this batch.
