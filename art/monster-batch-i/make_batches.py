"""Generate the monster-batch-i task packs and the pinned source-contract
evidence. Pure bookkeeping: hashes native sources/sprites, writes JSON."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ADDON = HERE.parents[1]
WS = ADDON.parents[2]
D = 'game/modules/tome/data/'
NPC = D + 'gfx/shockbolt/npc/'
TOK = 'game/addons/tome-checker-revised/data/gfx/tokens/'
STYLE = 'game/addons/tome-checker-revised/art/monsters-v2/masters/prox-v2.png'


def sha(rel):
    return hashlib.sha256((WS / rel).read_bytes()).hexdigest()


def src(path, anchor, hint=None):
    lines = (WS / (D + path)).read_text().splitlines()
    cands = [i + 1 for i, l in enumerate(lines) if anchor in l]
    assert cands, (path, anchor)
    return {'path': D + path, 'sha256': sha(D + path), 'line': cands[0], 'anchor': anchor}


COMP = ("One compact complete creature on a single circular tabletop disc, steep overhead three-quarter camera; visible clear neutral base ring on every side. Keep all anatomy and equipment well inside the inner four-fifths of disc radius. Base brightness must visually match reference neutral disc, with no illumination spill or ground effects. Disc plate discipline: measured results show generations of this style reference tend to render the disc DARKER than the reference, never lighter. So do not darken the disc at all: render the neutral disc -- including the whole outer-sixth ring band and the area under the creature -- at the style reference's own brightness, if anything a hair lighter, and never darker. No warm cast, glow, bounce-light, gradient or vignette anywhere on the disc. Do not darken the creature to compensate either. Add no warm cast, glow, bounce-light, gradient or vignette to the disc anywhere, including directly under or behind dark-bodied creatures.")
DISC = " Dry neutral charcoal disc with restrained copper-grey bevel, kept a visibly lighter value than the creature's darkest parts so the two never merge."

OOZE = ('general/npcs/ooze.lua', 'define_as = "BASE_NPC_OOZE"')
OOZE_BASE_ANCHOR = 'type = "vermin", subtype = "oozes",'

A = []  # (pack, spec)


def asset(pack, id_, name, scope, srcs, base, define_as, typ, sub, unique, structure, native, refs, subject, contrast, palette, verdict, dims=('silhouette', 'value'), comp=None):
    A.append(dict(comp=comp, pack=pack, id=id_, name=name, scope=scope, srcs=srcs, base=base, define_as=define_as, type=typ,
                  subtype=sub, unique=unique, structure=structure, native=native, refs=refs, subject=subject,
                  contrast=contrast, palette=palette, verdict=verdict, dims=dims))


FORMULA = 'formula: no image=/nice_tile/add_mos/shader/anim/moddable_tile/tint in the entity or its base; NPC.lua:33 default-image formula gives the file (same path the shipped black/yellow/red/blue ooze resolved to in the E1 fixture run); generic actor.image==entry.image single path'

asset(1, 'green-ooze', 'green ooze', 'general vermin/oozes (ooze.lua; also placed by vault forest-ruined-building3)',
      [src('general/npcs/ooze.lua', 'name = "green ooze"')], src('general/npcs/ooze.lua', 'type = "vermin", subtype = "oozes",'),
      None, 'vermin', 'oozes', False, FORMULA, 'vermin_oozes_green_ooze.png',
      [('style', STYLE, 'Approved disc, lighting and camera; do not copy its creature.'),
       ('identity', NPC + 'vermin_oozes_green_ooze.png', 'Native shape: low flat glossy bright-green puddle with a raised back and three small detached droplets.'),
       ('family', TOK + 'red-ooze.png', 'Shipped ooze (red, flat branching blob): show the family finish only; green ooze must NOT reuse this blob outline.')],
      "A low, wet, bright lime-green ooze puddle seen from above: one broad flat body with a raised rounded glossy crest along its back, one short blunt forward pseudopod, and exactly three small separate round droplets trailing behind it in a gentle curved row, each droplet carrying a white specular glint. No eyes, no mouth, no face, no spikes.",
      "Shipped siblings: black ooze (dark flat blob), yellow ooze (spiky flame-like), red ooze (bright red branching blob), blue ooze (pale branching amoeba) and green jelly (olive stippled dome). Green ooze must read as none of them: a flat spreading puddle with a raised crest and a curved row of three detached round droplets (silhouette), in a light saturated lime green with strong white gloss, clearly lighter and brighter than green jelly's olive dome (value/hue). No dome, no spikes, no branching arms, no spiral.",
      "Bright lime-green body, light and saturated, with pale yellow-green gloss planes and white specular glints, slightly deeper leaf-green shadows only at the underside." + DISC,
      'READY single (rarity 1, level 1-25)', ('silhouette', 'value', 'hue'))

asset(1, 'crimson-ooze', 'crimson ooze', 'general vermin/oozes (ooze.lua; rank 2, level 25+, 50% clone_on_hit)',
      [src('general/npcs/ooze.lua', 'name = "crimson ooze"')], src('general/npcs/ooze.lua', 'type = "vermin", subtype = "oozes",'),
      None, 'vermin', 'oozes', False, FORMULA, 'vermin_oozes_crimson_ooze.png',
      [('style', STYLE, 'Approved disc, lighting and camera; do not copy its creature.'),
       ('identity', NPC + 'vermin_oozes_crimson_ooze.png', 'Native shape: larger deep-red glossy blob with lobes and two detached pieces.'),
       ('family', TOK + 'red-ooze.png', 'Shipped red ooze (bright orange-red flat branching blob): crimson ooze must be heavier, taller, deeper wine-red and shaped differently.')],
      "A large, heavy, deep wine-crimson ooze rearing up into one thick glossy wave-shaped mound with a curling overhanging lip along its front, three fat drips hanging from that lip, and one smaller round bud of the same ooze splitting off beside it, joined to the main mass by a thin strand. Bright rose-pink specular streaks along the wave crest. No eyes, no mouth, no face.",
      "Red-hued siblings: red ooze (bright orange-red flat branching blob), red jelly (round red clover dome with dark seeds), crimson crystal (two chunky prisms), sanguine experiment (smooth scarlet clot). Crimson ooze is taller and heavier than red ooze, deeper and cooler wine-crimson, and shaped as a rearing wave with an overhanging lip, hanging drips and a split-off bud (silhouette); not a flat blob, not a seeded dome, not faceted. Its body must stay a clearly visible mid-value crimson with broad lighter rose planes, never near-black maroon.",
      "Deep wine-crimson body with broad lighter rose-red planes on the wave face and bright pink-white specular streaks; cool crimson rather than orange." + DISC,
      'READY single (rarity 1, level 25+)', ('silhouette', 'value', 'hue'))

asset(1, 'gelatinous-cube', 'gelatinous cube', 'general vermin/oozes (ooze.lua; rarity 3, level 12+, ACID)',
      [src('general/npcs/ooze.lua', 'name = "gelatinous cube"')], src('general/npcs/ooze.lua', 'type = "vermin", subtype = "oozes",'),
      None, 'vermin', 'oozes', False, FORMULA, 'vermin_oozes_gelatinous_cube.png',
      [('style', STYLE, 'Approved disc, lighting and camera; do not copy its creature.'),
       ('identity', NPC + 'vermin_oozes_gelatinous_cube.png', 'Native shape: a translucent yellow-green cube with engulfed items (skull, blade, coins) visible inside.'),
       ('family', TOK + 'yellow-ooze.png', 'Shipped yellow ooze (spiky amorphous blob): the cube must be a rigid geometric solid, not this blob.')],
      "A single translucent lime-yellow gelatinous cube with softly rounded edges, seen from a three-quarter overhead angle so its bright top face and two side faces are all visible; a few engulfed objects hang dimly inside the jelly: a pale skull, a short sword blade and three gold coins. The whole cube sits centred on the disc, well inside the inner four-fifths.",
      "The only rigid, box-shaped body among the ooze and jelly tokens: yellow ooze (spiky flame-like blob), yellow jelly (gold bumpy dome) and all other siblings are amorphous mounds. Hard straight cube edges with a bright translucent top face against darker side faces (silhouette and value); pale yellow-green rather than their golden yellow (hue). No drips, no pseudopods, no face.",
      "Pale translucent lime-yellow jelly, bright top face, mid yellow-green side faces, white glassy edge highlights, dim pale bone skull, grey-blue blade and dull gold coins inside." + DISC,
      'READY single (rarity 3, level 12+)', ('silhouette', 'value', 'hue'))

asset(1, 'malevolent-dimensional-jelly', 'Malevolent Dimensional Jelly', 'general immovable/jelly unique (jelly.lua; rarity 50, level 25+, DARKNESS)',
      [src('general/npcs/jelly.lua', 'name = "Malevolent Dimensional Jelly"')], src('general/npcs/jelly.lua', 'type = "immovable", subtype = "jelly",'),
      None, 'immovable', 'jelly', True,
      'formula: unique=true, no define_as, no image=/nice_tile/add_mos/shader/anim/moddable_tile/tint in the entity or BASE_NPC_JELLY (the six other jellies each set an explicit image= on their own leaf; this one does not); NPC.lua:33 formula gives npc/immovable_jelly_malevolent_dimensional_jelly.png; generic actor.image==entry.image single path for a unique entry',
      'immovable_jelly_malevolent_dimensional_jelly.png',
      [('style', STYLE, 'Approved disc, lighting and camera; do not copy its creature.'),
       ('identity', NPC + 'immovable_jelly_malevolent_dimensional_jelly.png', 'Native shape: dark glossy puddle with a starry window and curling tendrils at the rim.'),
       ('family', TOK + 'black-jelly.png', 'Shipped black jelly (black tar mound): this unique must be a lighter violet puddle with a starry opening, not a black mound and not blue jelly\'s spiral.')],
      "A flat glossy violet-indigo jelly puddle with a wide round opening in its centre like a window into a star-filled night sky: inside the opening a handful of tiny pale stars and a soft pale cyan-lilac haze. Three thin curling tendrils lift from the puddle's rim with their tips curled over. Slick and eerie, no eyes, no mouth.",
      "Jelly siblings: black jelly (black tar mound), blue jelly (bright blue dome with a dark spiral), green/white/yellow/red jellies (domes) and the ooze tokens. This unique is a flat puddle with a central starry window and curled tendrils (silhouette); medium violet rim with a pale luminous centre (value) separates it from the dark black jelly and the saturated blue dome. No spiral body, no near-black surface, no dome.",
      "Medium violet-indigo body with lighter lilac rim highlights and pale gloss, pale cyan-white star points and a pale lilac glow in the window; the puddle must never be near-black." + DISC,
      'READY single unique (rarity 50, level 25+)', ('silhouette', 'value', 'hue'))

XORN_BASE = src('general/npcs/xorn.lua', 'type = "elemental", subtype = "xorn",')
NT = 'nice_tile resolver sets image="invis.png" + add_mos[1]={image=<sprite>, display_h=2, display_y=-1} when nicer_tiles is on; the catalog unique entry matches that native-tall body (and the plain image when it is off); NPC.lua:33 formula is never reached'
asset(2, 'harkor-zun-fragment', "The Fragmented Essence of Harkor'Zun", 'tempest-peak unique elemental/xorn (xorn.lua; rarity 50; five clones share the entry)',
      [src('general/npcs/xorn.lua', 'name = "The Fragmented Essence of Harkor\'Zun"')], XORN_BASE, None, 'elemental', 'xorn', True, NT,
      'elemental_xorn_fragmented_harkor_zun.png',
      [('style', STYLE, 'Approved disc, lighting and camera; do not copy its creature.'),
       ('identity', NPC + 'elemental_xorn_fragmented_harkor_zun.png', 'Native shape: a jagged fractured heap of brown earth-rock spikes, no limbs.'),
       ('family', TOK + 'boney-experiment.png', 'Shipped boney experiment (ivory spiky bone pile): the fragment must be opaque earth-rock with glowing cracks, not bone.')],
      "A compact upright cluster of jagged tan-ochre earth and rock shards, fractured apart: one central cracked spire with four broken splinters hovering just off its surface, a rough boulder-like lump at the base, and hairline glowing violet-lilac cracks running through the stone. Solid opaque rock with light-catching flat facets. No limbs, no head, no face.",
      "Siblings and lookalikes: Harkor'Zun himself (a huge horned four-armed humanoid, drawn separately), boney experiment (ivory bone spikes), crystal tokens (translucent white, red, crimson and violet crystals) and the sandworm-burrower sand heap. The fragment is a headless heap of splinters with a tall central spire (silhouette), opaque light tan-ochre rock with violet cracks (hue), clearly lighter than the darkest parts of the base.",
      "Light tan-ochre and sandstone rock facets with slightly darker terracotta cracks and thin glowing violet-lilac fracture lines; never dark brown-black." + DISC,
      'READY unique native-tall (rarity 50; no define_as)', ('silhouette', 'value', 'hue'))

asset(2, 'harkor-zun', "Harkor'Zun", 'tempest-peak unique demon/major (xorn.lua, FULL_HARKOR_ZUN, no rarity; only spawned when five fragments die)',
      [src('general/npcs/xorn.lua', 'define_as = "FULL_HARKOR_ZUN"'), src('general/npcs/xorn.lua', 'name = "Harkor\'Zun", color=colors.VIOLET, unique=true,')],
      XORN_BASE, 'FULL_HARKOR_ZUN', 'demon', 'major', True, NT, 'elemental_xorn_harkor_zun.png',
      [('style', STYLE, 'Approved disc, lighting and camera; do not copy its creature.'),
       ('identity', NPC + 'elemental_xorn_harkor_zun.png', 'Native shape: a huge hunched earth-brown horned humanoid with extra lower arms, arms raised.'),
       ('family', TOK + 'lithfengel.png', 'Shipped Lithfengel (demon/major, hulking brown horned beast): Harkor\'Zun must be a stone humanoid, greyer and with raised arms, not this brown beast.')],
      "A hulking hunched earth-demon built of grey-tan stone and clay: very broad shoulders, a small horned head with two glowing amber eyes, two big upper arms raised and spread wide ending in heavy blocky fists, two shorter lower arms braced forward like a crab, thick pillar legs, carved rocky ridges along the back, glowing amber-orange cracks across the chest. Compact stance, fists and elbows well inside the disc.",
      "Lookalikes: Lithfengel (brown hulking horned beast on all fours), the fragment of Harkor'Zun (headless splinter heap, drawn separately), Prox/Bill trolls and the crystal tokens. Harkor'Zun is an upright stone humanoid with a horned head and arms raised in a wide V (silhouette), grey-tan stone with amber glowing cracks (hue/value), lighter than Lithfengel's brown.",
      "Warm grey-tan stone and pale clay planes with darker terracotta joints and glowing amber-orange cracks and eyes; body never darker than mid-tone." + DISC,
      'READY unique native-tall (FULL_HARKOR_ZUN; type/subtype overridden to demon/major)', ('silhouette', 'value', 'hue'))

asset(2, 'burb-snow-giant-champion', 'Burb the snow giant champion', 'tempest-peak unique giant/ice (snow-giant.lua, BURB_SNOW_GIANT, rarity 10)',
      [src('general/npcs/snow-giant.lua', 'define_as = "BURB_SNOW_GIANT"'), src('general/npcs/snow-giant.lua', 'name = "Burb the snow giant champion"')],
      src('general/npcs/snow-giant.lua', 'type = "giant", subtype = "ice",'), 'BURB_SNOW_GIANT', 'giant', 'ice', True, NT,
      'giant_ice_burb_the_snow_giant_champion.png',
      [('style', STYLE, 'Approved disc, lighting and camera; do not copy its creature.'),
       ('identity', NPC + 'giant_ice_burb_the_snow_giant_champion.png', 'Native shape: armoured horned-helm snow giant with a fur mantle and pale blue frost sparks; the sprite armour is dark.'),
       ('family', TOK + 'bill.png', 'Shipped Bill (giant/troll, grey hulk with a log): Burb is a pale cold armoured giant with fur and no club.')],
      "A towering maddened snow giant champion: pale frost-grey and ice-blue plate armour, a thick white fur mantle across the shoulders, a horned iron helm above a wild white beard and wide angry eyes, one huge clenched fist raised and the other arm hanging, a few pale blue frost sparks crackling close to the body. Hunched forward and compact, everything inside the inner four-fifths of the disc.",
      "The only giant/ice in the catalog. Giants nearby: Prox, Bill and Shax (brown, grey and green trolls with clubs) and the shivgoroth (crystalline blue ice elemental). Burb is pale white-blue armoured with fur and horns and no weapon (silhouette: horned helm, fur mantle, raised fist), with light frost values instead of the trolls' earth tones (hue/value). His armour must read light frost-blue-grey, not the sprite's near-black plate.",
      "Light frost-grey and ice-blue plate with white fur, mid-grey iron helm and horns, pale cyan frost sparks; nothing darker than mid grey." + DISC,
      'READY unique native-tall (BURB_SNOW_GIANT)', ('silhouette', 'value', 'hue'))

asset(2, 'norgan', 'Norgan', 'reknor-escape unique humanoid/dwarf (NORGAN, dwarf-start squadmate, control=order party member)',
      [src('zones/reknor-escape/npcs.lua', 'define_as = "NORGAN"'), src('zones/reknor-escape/npcs.lua', 'name = "Norgan"')],
      None, 'NORGAN', 'humanoid', 'dwarf', True,
      'formula: standalone entry (no base), unique=true, no image=/nice_tile/add_mos/shader/anim/moddable_tile/tint; equipment is resolvers.equip only (no paper-doll for an NPC without moddable_tile); NPC.lua:33 formula gives npc/humanoid_dwarf_norgan.png; generic single path',
      'humanoid_dwarf_norgan.png',
      [('style', STYLE, 'Approved disc, lighting and camera; do not copy its creature.'),
       ('identity', NPC + 'humanoid_dwarf_norgan.png', 'Native shape: broad dwarf berserker with a big brown beard, olive tabard and an iron maul on the shoulder.'),
       ('family', TOK + 'krogar.png', 'Shipped Krogar (orc in heavy armour with a staff): Norgan is a squat bearded dwarf with a maul, not a tall armoured orc.')],
      "A short, very broad dwarf berserker with a bare head, a huge braided chestnut-brown beard, thick bare forearms, an olive-green tabard over iron mail, a big iron greatmaul resting on one shoulder with its head kept close to his ear, the other hand clenched into a fist forward, a small brass lantern hanging at his belt. Squat and wide, wider than tall.",
      "The only dwarf in the catalog; the other humanoid tokens are tall: human thieves/bandits, Celia, Urkis, Harno, Necromancer, elf Fillarel and orc Krogar. Norgan is squat with a huge beard and shoulder maul (silhouette: wider than tall), warm chestnut and olive on a mid-light value.",
      "Chestnut-brown beard and hair, warm skin tones, olive-green tabard, mid grey iron mail and maul head, brass lantern; all values mid or lighter." + DISC,
      'READY unique single (NORGAN)', ('silhouette', 'value', 'hue'))

CH = src('zones/deep-bellow/npcs.lua', 'define_as = "SLIMY_CRAWLER"')
asset(3, 'slimy-crawler', 'slimy crawler', "deep-bellow non-unique horror/corrupted, define_as SLIMY_CRAWLER (The Mouth's summon; facings.lua only sets flipx=false)",
      [CH, src('zones/deep-bellow/npcs.lua', 'name = "slimy crawler"')],
      src('general/npcs/horror-corrupted.lua', 'type = "horror", subtype = "corrupted",'), 'SLIMY_CRAWLER', 'horror', 'corrupted', False,
      'formula: no image=/nice_tile/add_mos/shader/anim/moddable_tile/tint in the entity or BASE_NPC_CORRUPTED_HORROR; NPC.lua:33 formula gives npc/horror_corrupted_slimy_crawler.png; generic single path',
      'horror_corrupted_slimy_crawler.png',
      [('style', STYLE, 'Approved disc, lighting and camera; do not copy its creature.'),
       ('identity', NPC + 'horror_corrupted_slimy_crawler.png', 'Native shape: pale ivory plated many-legged crawler with pincers.'),
       ('family', TOK + 'sandworm.png', 'Shipped sandworm (slim pale open S-curve, no legs): the crawler has many legs, plates and pincers and must not read as a worm.')],
      "A low plated centipede-like crawler seen from above: a pale ivory-olive body of about eight overlapping segment plates coated in glistening green slime, many short legs along both sides, two curved pincers at its head, the body bent into a compact C shape, green slime dripping in a few fat drops. Small and wiry, not a worm.",
      "Lookalikes: the three sandworm tokens and sandworm queen (legless smooth worms), the six ant tokens, green-worm-mass and the other horror/corrupted tokens (The Mouth, The Abomination, Horned Horror, dremling). The slimy crawler is the only plated multi-legged body with pincers, C-curved (silhouette), pale ivory with green slime (hue), lighter than the base's dark parts.",
      "Pale ivory-olive plates, bright green glossy slime, warm grey leg tips and small dark pincer tips; body never darker than mid-tone." + DISC,
      'READY single (deep-bellow)', ('silhouette', 'value', 'hue'))

asset(3, 'spellblaze-simulacrum', 'Spellblaze Simulacrum', 'scintillating-caves unique immovable/crystal (SPELLBLAZE_SIMULACRUM, backup guardian; image= and nice_tile name the same PNG)',
      [src('zones/scintillating-caves/npcs.lua', 'define_as = "SPELLBLAZE_SIMULACRUM"'), src('zones/scintillating-caves/npcs.lua', 'name = "Spellblaze Simulacrum"')],
      src('general/npcs/crystal.lua', 'type = "immovable", subtype = "crystal", image ='), 'SPELLBLAZE_SIMULACRUM', 'immovable', 'crystal', True,
      'explicit image= plus nice_tile naming the same PNG (no =BASE=TILE=): image is npc/spellblaze_simulacrum.png without nicer_tiles and invis.png+add_mos with it; the catalog unique entry matches both. No tint/shader on the leaf (BASE_NPC_CRYSTAL has none either)',
      'spellblaze_simulacrum.png',
      [('style', STYLE, 'Approved disc, lighting and camera; do not copy its creature.'),
       ('identity', NPC + 'spellblaze_simulacrum.png', 'Native shape: a large upright humanoid figure made of faceted purple crystal.'),
       ('family', TOK + 'spellblaze-crystal.png', 'Shipped Spellblaze Crystal (round purple spiky cluster): the Simulacrum must be an upright person-shaped figure instead.')],
      "An upright person-shaped figure of faceted violet crystal: angular head, broad shoulders, two long arms hanging slightly away from the body ending in blunt crystal fists, faceted legs, a brighter pink-lilac glowing core in the chest, shards jutting at the elbows and shoulders. Stiff statue-like stance seen from a three-quarter overhead angle.",
      "Crystal tokens: Spellblaze Crystal (round purple spiky cluster, no figure), white crystal (tall pale bouquet), red crystal (long blade fan), crimson crystal (two chunky prisms). The Simulacrum is the only person-shaped crystal (head, arms, legs silhouette), medium-light violet with pale facet planes (value), not a cluster.",
      "Medium-light violet and amethyst facets with pale lilac highlight planes, brighter pink-lilac chest core, darker plum only in thin facet creases." + DISC,
      'READY unique native-tall/single (SPELLBLAZE_SIMULACRUM)', ('silhouette', 'value'))

asset(3, 'kryl-feijan-acolyte', 'Acolyte of the Sect of Kryl-Feijan', 'crypt-kryl-feijan non-unique humanoid/elf, define_as ACOLYTE (explicit image= reusing the elven corruptor portrait)',
      [src('zones/crypt-kryl-feijan/npcs.lua', 'define_as = "ACOLYTE"'), src('zones/crypt-kryl-feijan/npcs.lua', 'image = "npc/humanoid_shalore_elven_corruptor.png"')],
      None, 'ACOLYTE', 'humanoid', 'elf', False,
      'explicit image= (npc/humanoid_shalore_elven_corruptor.png, shared natively with the elven corruptor); standalone entry, no nice_tile/add_mos/shader/anim/moddable_tile; the catalog entry is bound to the exact name and define_as ACOLYTE so the corruptor keeps native art',
      'humanoid_shalore_elven_corruptor.png',
      [('style', STYLE, 'Approved disc, lighting and camera; do not copy its creature.'),
       ('identity', NPC + 'humanoid_shalore_elven_corruptor.png', 'Native portrait (shared with the elven corruptor): an elf in dark robes. The acolyte must read as a mad cultist, not this pointed-hat staff caster.'),
       ('family', TOK + 'necromancer.png', 'Shipped Necromancer (bald human in slate-violet robe with staff): the acolyte is an elf with long hair, pointed ears and a dagger, no staff.')],
      "A bare-headed elven cultist with long pale silver hair swept back, long pointed ears, wide staring mad eyes and a thin pale face, in a floor-length plum-charcoal robe with wide crimson-lined bell sleeves and a blood-red sigil sash: one hand raised holding a small glowing crimson blood orb, the other hand low holding a curved ritual dagger with a red tip. No hat, no hood, no staff. Compact upright pose.",
      "Nearby humanoids: Necromancer (bald human, slate-violet robe, staff), Harno (hooded blue-grey cloak, two knives), Celia (pale gown and staff), Urkis and Fillarel (elf mage in gold). The elven corruptor keeps native art and wears a pointed hat with a tall staff. The acolyte has bare silver hair, long ears, bell sleeves with a red orb and a dagger (silhouette: swept-back hair, ears, wide sleeves), plum-crimson robe on a mid value (hue/value).",
      "Plum-charcoal robe lifted with broad mid-violet fold planes, crimson lining and sash, pale skin and silver hair as the value break, glowing crimson orb, dull grey dagger; the robe is never near-black." + DISC,
      'READY single (ACOLYTE)', ('silhouette', 'value', 'hue'))

asset(3, 'zquikzshl', "Z'quikzshl the skeletal mold", "general unique undead/molds (molds.lua; rarity 50; type overridden from immovable; explicit image=)",
      [src('general/npcs/molds.lua', 'name = "Z\'quikzshl the skeletal mold"'), src('general/npcs/molds.lua', 'type = "undead", subtype = "molds",')],
      src('general/npcs/molds.lua', 'type = "immovable", subtype = "molds",'), None, 'undead', 'molds', True,
      'explicit image= npc/immovable_molds_skeletal_mold.png on the leaf; no nice_tile/add_mos/shader/anim/moddable_tile; type overridden to undead so the four immovable/molds tokens can never match it',
      'immovable_molds_skeletal_mold.png',
      [('style', STYLE, 'Approved disc, lighting and camera; do not copy its creature.'),
       ('identity', NPC + 'immovable_molds_skeletal_mold.png', 'Native shape: a low pile of pale bones lying on a dark green mould mat.'),
       ('family', TOK + 'boney-experiment.png', 'Shipped boney experiment (bare ivory spiky bone pile): the mould must read as a green-violet mat over the bones, not a bare bone heap.')],
      "A low rounded mound of pale bones thickly overgrown by a sickly green-and-violet mould mat: a skull at the front, a curved rib cage arching over the middle like a cage, two thigh bones crossing, and pale fuzzy mould patches with a few violet spore caps and tiny spore puffs spreading over the bones. The whole heap is about as wide as it is tall, sitting fully inside the disc.",
      "Molds: green mold (cluster of olive bulbs), brown mold (round frilled disc), shining mold (tan coral stalks), grey mold (grey frilled fan); boney experiment (bare ivory spiky bone pile with skulls). Z'quikzshl is a rounded green-teal mould mat over a skull and rib cage, with violet caps (silhouette: skull plus rib arch under a mould blanket; hue: green-violet mat around ivory bones).",
      "Mid green-teal and violet-tinged mould mat with lighter sage fuzz, ivory-white skull and ribs as the value break, small violet spore caps; nothing darker than mid tone." + DISC,
      'READY unique single (rarity 50)', ('silhouette', 'value', 'hue'))


# ---- retries (fresh calibrated packs; the earlier pack keeps its own ledger) ----
RETRY_BURB = COMP + " Calibration from the previous generation of this exact token: it rendered the neutral disc about ten luminance units DARKER than the style reference (the pale armoured giant made the disc plate look dim). This time deliberately paint the whole disc plate, bevel and the area under the giant clearly lighter than feels natural, about ten units brighter than your first instinct, so it lands at or slightly above the reference disc."
_burb = next(a for a in A if a['id'] == 'burb-snow-giant-champion')
A.append(dict(_burb, pack=4, comp=RETRY_BURB))


# ---- value retries (v1 passed the numeric gate but was rejected by eye/luminance) ----
def retry(id_, pack, **changes):
    base = next(a for a in A if a['id'] == id_)
    A.append(dict(base, pack=pack, **changes))


retry('crimson-ooze', 5,
      palette="Luminous raspberry-rose crimson: the wave face in bright strawberry-rose with pink-white highlights and broad lighter pink planes, deep wine only in thin creases and under the lip; overall clearly mid-light in value (at least as light as a bright red ooze), cool and pink-leaning rather than orange." + DISC,
      contrast="Red-hued siblings: red ooze (bright orange-red flat branching blob), red jelly (round red clover dome with dark seeds), crimson crystal (two chunky prisms), sanguine experiment (smooth dark scarlet clot). A first draft of this token was rejected as a near-black wine blob that merged with red jelly and the sanguine experiment at 48px. This redraw keeps the rearing wave with overhanging lip, hanging drips and split-off bud (silhouette) but in a light translucent raspberry-rose (value/hue) with a broad pale rim on the wave crest; it must never be dark maroon.")
retry('kryl-feijan-acolyte', 5,
      subject="A bare-headed elven cultist with long pale silver hair swept back, long pointed ears, wide staring mad eyes and a thin pale face, in a floor-length dusty plum-mauve robe with wide bell sleeves lined in bright crimson and a bright blood-red sigil sash: one hand raised holding a small glowing crimson blood orb, the other hand low holding a curved ritual dagger with a red tip. No hat, no hood, no staff. Compact upright pose.",
      palette="Dusty plum-mauve robe as light as a mid-tone slate-violet (lifted with broad pale mauve fold planes), bright crimson lining and sash, pale skin and silver hair as the value break, glowing crimson orb, pale steel dagger; nothing darker than mid tone, never a black or near-black robe." + DISC,
      contrast="Nearby humanoids: Necromancer (bald human, slate-violet robe, staff), Harno (hooded blue-grey cloak, two knives), Celia (pale gown and staff), Urkis and Fillarel (elf mage in gold). The elven corruptor keeps native art and wears a pointed hat with a tall staff. A first draft of this token was rejected for a near-black robe at 48px. The acolyte has bare silver hair, long ears, bell sleeves with a red orb and a dagger (silhouette), in a clearly light mauve-plum robe with bright crimson accents (hue/value).")
retry('zquikzshl', 5,
      subject="A low rounded dome-shaped mound of pale bones almost completely blanketed by a thick, bright, sickly moss-green mould mat with violet patches: only a skull at the front and the curved tops of a few ribs poke through the mould, plus one thigh bone end; a cluster of tall violet spore caps and fuzzy pale-green mould tufts stand on top. The whole mound reads as a fuzzy green mould dome first and a bone pile second, sitting fully inside the disc.",
      palette="Bright moss-green and lime-tinged mould mat, mid-light in value, with violet-lilac patches and violet spore caps, pale sage fuzz on top, ivory skull and rib tips as small accents; nothing darker than mid tone." + DISC,
      contrast="Molds: green mold (cluster of olive bulbs), brown mold (round frilled disc), shining mold (tan coral stalks), grey mold (grey frilled fan); boney experiment (bare tan-ivory bone pile). A first draft of this token was a grey-green low-contrast bone heap that read as the boney experiment at 48px. This redraw is a bright moss-green fuzzy dome with violet caps and only a skull and rib tips showing (silhouette: dome plus tall caps; hue: bright green-violet, unlike the tan bone pile).")
retry('malevolent-dimensional-jelly', 5,
      subject="A flat glossy amethyst-violet jelly puddle with a wide round opening in its centre like a window into a bright star-filled night sky: inside the opening many tiny white stars and a luminous pale cyan-lilac nebula haze. Three thin curling tendrils lift from the puddle's rim with their tips curled over, and pale lavender highlights run along the whole rim. Slick and eerie, no eyes, no mouth.",
      palette="Light amethyst and lilac-violet jelly body at mid-light value with pale lavender rim highlights and bright white gloss, bright white star points and a luminous pale cyan-lilac window; the puddle must never be dark indigo or near-black." + DISC,
      contrast="Jelly siblings: black jelly (black tar mound), blue jelly (bright blue dome with a dark spiral), green/white/yellow/red jellies (domes) and the ooze tokens. A first draft of this token had a dark indigo rim that read dim against the base at 48px. This redraw is a flat puddle with a central starry window and curled tendrils (silhouette) in a clearly lighter amethyst-lilac with pale rim highlights (value/hue), far lighter than the black jelly and unlike the saturated blue dome. No spiral body, no dome.")


retry('zquikzshl', 6,
      subject="A large curved ivory rib cage arching up like an open dome cage from a low flat pad of bright moss-green and violet mould: a big ivory skull sits at the front of the cage with dark eye sockets, two thigh bones lie crossed beside it, and clumps of pale-green fuzzy mould plus a few violet spore caps cling to the rib tips and the pad. The bones stay clearly visible and large (light ivory against the green pad); the pad is a flat mat around the bones rather than a dome covering them.",
      palette="Light ivory-cream bones as the dominant value plane, bright moss-green and lilac-violet mould pad around and under them, violet spore caps and pale sage fuzz; nothing darker than mid tone." + DISC,
      contrast="Molds: green mold (cluster of round olive bulbs), brown mold (round frilled disc), shining mold (tan coral stalks), grey mold (grey frilled fan); boney experiment (flat tan bare bone pile of thin spikes). Two earlier drafts failed: a grey-green low-contrast bone heap and a bright green dome that read as another green mold. This redraw makes the arched ivory rib cage with a big skull the silhouette (unlike any blob-shaped mold) standing on a visible green-violet mould pad (unlike the bare tan spiky bone pile).")


def build():
    packs = {}
    identities = []
    render = 'game/addons/tome-checker-revised/evidence/monster-batch-i-20260929/source-contracts.json'
    seen = set()
    for a in A:
        if a['id'] in seen:
            continue
        seen.add(a['id'])
        native_rel = NPC + a['native']
        ident = {'id': a['id'], 'native_name': a['name'], 'source': a['srcs'][0], 'define_as': a['define_as'],
                 'type': a['type'], 'subtype': a['subtype'], 'unique': a['unique'], 'structure': a['structure'],
                 'native_image': 'npc/' + a['native'], 'native_image_path': native_rel,
                 'native_image_sha256': sha(native_rel), 'verdict': a['verdict']}
        if a['base']:
            ident['base_source'] = a['base']
        if len(a['srcs']) > 1:
            ident['extra_sources'] = a['srcs'][1:]
        identities.append(ident)
    ev = {'schema': 1,
          'task': 'monster-batch-i: static re-verification (no game launch) of the four kept-native oozes/jellies, the Tempest Peak bosses, Norgan, slimy crawler, Spellblaze Simulacrum, the Kryl-Feijan acolyte and Z\'quikzshl against game/modules/tome source and native sprites.',
          'new_ids_not_in_catalog_before_this_batch': [i['id'] for i in identities], 'identities': identities}
    out = ADDON / 'evidence/monster-batch-i-20260929/source-contracts.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(ev, indent=2, ensure_ascii=False) + '\n')
    evsha = hashlib.sha256(out.read_bytes()).hexdigest()
    for a in A:
        refs = [{'path': p, 'sha256': sha(p), 'role': r, 'note': n} for r, p, n in a['refs']]
        entry = {'asset_id': a['id'], 'native_name': a['name'], 'scope': a['scope'], 'sources': a['srcs'], 'references': refs,
                 'contrast_dimensions': list(a['dims']),
                 'prompt_fields': {'subject': a['subject'], 'contrast': a['contrast'], 'composition': a['comp'] or COMP, 'palette': a['palette']},
                 'kind': 'creature', 'max_attempts': 1, 'gate': 'ready',
                 'gate_reason': f"Exact source identity re-verified directly against game/modules/tome source (name={a['name']}, define_as={a['define_as']}, type={a['type']}/subtype={a['subtype']}, unique={a['unique']}); details and hashes in evidence/monster-batch-i-20260929/source-contracts.json. {a['structure']}. Exact catalog entry only, never a whole-subtype mapping.",
                 'render_evidence': [{'path': render, 'sha256': evsha}]}
        packs.setdefault(a['pack'], []).append(entry)
    for n, assets in packs.items():
        p = ADDON / f'art/production/batches/monster-batch-i-{n}.json'
        if p.exists():
            print('exists, skipped', p.name)
            continue
        p.write_text(json.dumps({'schema': 1, 'batch_id': f'monster-batch-i-{n}', 'assets': assets}, indent=2, ensure_ascii=False) + '\n')
        print('wrote', p.name)


if __name__ == '__main__':
    build()
