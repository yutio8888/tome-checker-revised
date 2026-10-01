# Monster batch AE selection (2026-10-01)

Second off-list dungeon-pool batch; survey `tmp/offlist-survey/final.tsv`, class a.
Static identity audit and art selection complete; all twelve pool identities accepted. Live checks remain separate.
No game launch, version bump, release package, README, CHANGELOG or PROGRESS change.

| Pool identity | Official Chinese name | Source leaf | Body contract |
|---|---|---|---|
| champion of Urh'Rok | 乌鲁洛克的冠军 | major-demon.lua:204 | demon/major; single-body tall, native_tall; npc/demon_major_champion_of_urh_rok.png |
| forge-giant | 锻造巨人 | major-demon.lua:249 | demon/major; single-body tall, native_tall; npc/demon_major_forge_giant.png |
| hummerhorn | 大黄蜂 | swarm.lua:95 | insect/swarms; flat single image; npc/hummerhorn.png |
| weaver matriarch | 雌性编织者 | spider.lua:293 | spiderkin/spider; single-body tall, native_tall; npc/spiderkin_spider_weaver_matriarch.png |
| patchwork troll | 拼凑巨魔 | troll.lua:115 | giant/troll; single-body tall, native_tall; npc/giant_troll_patchwork_troll.png |
| maulotaur | 玛诺陶 | minotaur.lua:75 | giant/minotaur; single-body tall, native_tall; npc/giant_minotaur_maulotaur.png |
| worm that walks | 蠕虫合体 | horror.lua:47 | horror/eldritch; flat single image; npc/horror_eldritch_worm_that_walks.png |
| headless horror | 无头恐魔 | horror.lua:196 | horror/eldritch; flat single image; npc/horror_eldritch_headless_horror.png |
| storm wyrm | 风暴巨龙 | storm-drake.lua:85 | dragon/storm; single-body tall, native_tall; npc/dragon_storm_storm_wyrm.png |
| spire dragon | 螺旋巨龙 | wild-drake.lua:47 | dragon/wild; single-body tall, native_tall; npc/dragon_wild_spire_dragon.png |
| blinkwyrm | 相位巨龙 | wild-drake.lua:76 | dragon/wild; single-body tall, native_tall; npc/dragon_wild_blinkwyrm.png |
| emperor wight | 帝王尸妖 | wight.lua:107 | undead/wight; single-body tall, native_tall; npc/emperor_wight.png |

All pool leaves have `define_as=nil`, `unique=false`, no leaf/base shader,
moddable_tile, animation or add_displays. Nine have supported native tall bodies
(64×128); three flat (64×64): hummerhorn, worm that walks, headless horror.
Patchwork troll's `nice_tile{tall=1}` is the shorthand for the same one-body tall
contract; other tall leaves specify `invis.png` and one add_mos body with
`display_h=2,display_y=-1`. This is a tall display mechanism, not an invisible
body. Nicer_tiles-off uses the same explicit/default native PNG for all twelve.

Headless horror has a same-name Arena leaf `HEADLESSHORROR`, with the same PNG.
There is no occupied catalog name/id; the existing define_as equality guard
separates the pool leaf from the Arena body. Arena stays native. Unknown unique
actors or another define_as also stay native. No alias for this Arena name or art variant is added.

Hummerhorn Multiply clones its identity and body, and therefore wears the same
token. Weaver matriarch escorts are weaver young, storm wyrm escorts are storm
drakes, emperor wight escorts are individual wight leaves; each uses its own
mapping. Worm Rot/on_takehit spawn the separately mapped carrion worm mass.
Headless horror's three eyes are separate actors and stay native this batch.
Vaults build the same pool leaves by name. The renegade-wyrmics Storm Terror and
the destruction-orb Crusher (storm wyrm / forge-giant) are renamed tall random
bosses and stay native under AD's existing captureRandomOrigin policy.

See pinned `source-contracts.json` and `talent-contracts.json` in
`evidence/monster-batch-ae-20261001/`. `talent-review.md` corrects preliminary
birth-sustain wording: Fast Metabolism is passive, emperor wight sustains
Thunderstorm, blinkwyrm also sustains Spellcraft. Burning Wake has supported
_isshaderaura bookkeeping, not actor.shader. No appearance exception is added. The final `clone-contracts.md` supplement
corrects the preliminary no-alias conclusion: AE-only exact temporal-clone
constructor aliases are required by the same-body-summon policy.

## Art direction and reference review

Every call uses the approved Prox-v2 disc/camera/lighting reference, its own
inspected native sprite and a focused contact sheet of shipped siblings.
The native reference contact sheet and all five family sheets were opened
before generation. Official Chinese names above are from the sole requested
translation source `mod-tome.lua`; no user-facing setting text is changed.

- Champion: enclosed silver armoured greatsword knight. Forge-giant: exposed
  burning smith, paired square hammers, apron; distinct from thorned, bull,
  shadow and smoke demons by anatomy and equipment.
- Storm wyrm: thick horseshoe coil, raised neck, forked crest and folded wing
  triangles; spire dragon: low heavy wingless blade-armoured coil; blinkwyrm:
  slender smooth high S curve and small fins. Compare against shipped storm
  drake, fire/venom/ice wyrms and Rantha; shape and structure, not colour alone.
- Hummerhorn: one large thin-waisted wasp, not a swarm. Weaver matriarch:
  broad low eight-legged spider, bulbous abdomen and yellow-white thorax.
- Patchwork troll: asymmetrical stitched troll parts and broken weapon pieces.
  Maulotaur: bull with a square greatmaul, not the minotaur's axe.
- Worm that walks: ragged hood, maggot-bundle arms, paired waraxes. Headless
  horror: no head, bare distended belly, bent gangly arms. Emperor wight:
  gold funerary armour and raised curved sword; no crown or rank graphic.
  Emperor's brief was corrected to its native equipment before any call.

All dark subjects receive AD's unchanged compact-fit, mid-light body and disc
calibration clauses. No lowered gate, batch-local test floor or new waiver.
Multi-hued drakes/wyrms, shadow claws, crystals, liches and other eldritch horrors
are outside AE and untouched.

## Initial selection and ImageGen outcomes (historical)

**13 serial calls**, all run_imagegen.py defaults (gpt-6.1-sol, ephemeral).
Twelve admitted masters: eleven v1, hummerhorn v2. Hummerhorn pack 1 returned no
image path (provenance-rejected, no admitted master); pack 5 repeated the same
brief and passed. No art-gate rejection, luminance redraw, waiver or PENDING
request. Call records, exact prompts, references and receipts remain under
art/production/handoffs/monster-batch-ae-*; no superseded image existed to move.

## Initial 48/64/96 and floor review (storm conclusion superseded)

Opened all three family sheets in both colour and grayscale, plus both 2x
48px floor sheets. Shipped siblings are in every family sheet. All twelve retain
complete silhouettes and identity features at 48px across the ten real refined
floors. Yellow frames are representative survey-zone floors, not verified live
spawn locations. The central masked-body means below meet the unchanged 65
minimum; the descriptive real-floor baseline stays 45 (as AD).

Champion's plate/sword versus forge-giant's exposed body/two hammers remain
separate in grayscale. Maulotaur has a square hammer and bull face, patchwork
has uneven stitched arms. Storm wyrm's long raised neck/open horseshoe and wing
triangles differ from ice wyrm's short broad head/compact crystal spiral; spire
is a low densely armoured wingless coil; blinkwyrm is smooth and slender with
two S bends and no big wings. Hummerhorn is one wasp, matriarch a broad patterned
spider; headless horror has no head, unlike the ragged hooded worm bundles;
emperor's gold sword-warrior silhouette differs from existing wights.

The relatively weakest small features are worm-that-walks' individual maggots
and patchwork stitch seams at 48px; their broad body/equipment structure remains
readable. Fine anatomy is naturally clearer at 64/96px. No gate was relaxed.

| Identity | Masked body luminance |
|---|---|

| champion-of-urh-rok | 82.21 |
| forge-giant | 79.43 |
| hummerhorn | 84.08 |
| weaver-matriarch | 108.07 |
| patchwork-troll | 94.85 |
| maulotaur | 80.07 |
| worm-that-walks | 91.42 |
| headless-horror | 100.45 |
| storm-wyrm (selected v2) | 100.71 |
| spire-dragon | 110.45 |
| blinkwyrm | 114.44 |
| emperor-wight | 84.73 |

Catalog: 389 → 401. Nine tall entries, three flat. Existing released version stays 0.6.31.

## Isolated gates

20 Lua scripts, 32,003 token-mapping checks, 425 production tests, dead-assets audit
and explicit-path staged diff check passed. No game launch. See AE evidence logs.

## Coordinator-requested storm refinement

The coordinator accepted eleven designs and rejected storm-wyrm-v1: its pale
ice-blue coil reads too close to ice-wyrm and Rantha at 48/64px. The original
numeric pass and initial visual conclusions above are historical, not the final
storm decision. The original master and review log remain under `superseded/`;
the original `review/storm-anchor-48-64-96.png` remains historical evidence.

Pack 6 is an explicit pinned refinement brief. One additional serial ImageGen
call (gpt-6.1-sol, ephemeral) produced selected `masters/storm-wyrm-v2.png`;
14 total AE calls, two for storm wyrm. It passed without repair or waiver.
Violet/indigo scales, yellow-white crackle and a broad gold belly restore the
storm palette. Forked thunderbolt horns and broad scalloped fan wings change
its silhouette as well as colour. The upright coiled great wyrm differs from
the crouching shipped storm-drake and the needle-crystal cold wyrms at all
three sizes, including grayscale. The gold belly remains readable on all ten
48px floor composites. Selected masked-body luminance is **100.71**, against
the unchanged **65** body gate; descriptive floor baseline remains **45**.

Open the regenerated dragon colour/grayscale 48/64/96 sheets and
`review/floor-readability-48-x2-b.png`. Separate refinement gate evidence is
in `evidence/monster-batch-ae-storm-refinement-20261001/`. No runtime mapping
code changes: HEAD's whole-catalog temporalClone from 10c81933 is preserved.
The production provenance test only follows the retained old master into
`superseded/`; every threshold and attempt budget remains unchanged.

Refinement isolated gates: all 20 non-live Lua scripts, 33,042 token-mapping
checks, 425 production tests and dead-assets audit passed. Scoped staged diff
check passed. No game launch; separate live review remains pending.
