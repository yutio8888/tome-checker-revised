"""Generate the monster-batch-k task packs and the pinned source-contract
evidence (survey-2 section 7, batch 2: aquatic, spiderkin, ghoul, drem,
sandworm tunneler). Pure bookkeeping: hashes native sources/sprites, writes JSON.
Retry packs are appended by later edits of this file (never overwritten)."""
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


def src(path, anchor):
    lines = (WS / (D + path)).read_text().splitlines()
    cands = [i + 1 for i, l in enumerate(lines) if anchor in l]
    assert cands, (path, anchor)
    return {'path': D + path, 'sha256': sha(D + path), 'line': cands[0], 'anchor': anchor}


COMP = ("One compact complete creature on a single circular tabletop disc, steep overhead three-quarter camera; visible clear neutral base ring on every side. Keep all anatomy and equipment well inside the inner four-fifths of disc radius. Base brightness must visually match reference neutral disc, with no illumination spill or ground effects. Disc plate discipline: measured results show generations of this style reference tend to render the disc DARKER than the reference, never lighter. So do not darken the disc at all: render the neutral disc -- including the whole outer-sixth ring band and the area under the creature -- at the style reference's own brightness, if anything a hair lighter, and never darker. No warm cast, glow, bounce-light, gradient or vignette anywhere on the disc. Do not darken the creature to compensate either. Add no warm cast, glow, bounce-light, gradient or vignette to the disc anywhere, including directly under or behind dark-bodied creatures.")
DISC = " Dry neutral charcoal disc with restrained copper-grey bevel, kept a visibly lighter value than the creature's darkest parts so the two never merge."
A = []


def asset(pack, id_, name, scope, srcs, base, define_as, typ, sub, unique, native_tall, structure, native, refs, subject,
          contrast, palette, verdict, dims=('silhouette', 'value'), comp=None):
    A.append(dict(comp=comp, pack=pack, id=id_, name=name, scope=scope, srcs=srcs, base=base, define_as=define_as, type=typ,
                  subtype=sub, unique=unique, native_tall=native_tall, structure=structure, native=native, refs=refs,
                  subject=subject, contrast=contrast, palette=palette, verdict=verdict, dims=dims))


STY = ('style', STYLE, 'Approved disc, lighting and camera; do not copy its creature.')
SINGLE = 'no image=/nice_tile/add_mos/shader/anim/moddable_tile on the leaf or its base; no tint; generic actor.image==entry.image single path'
TALL = 'resolvers.nice_tile{image="invis.png", add_mos={{image="<png>", display_h=2, display_y=-1}}} names the PNG explicitly (no =BASE=TILE= indirection and no {tall=1} shorthand), so the resolved tall body is statically pinnable (the batch F xhaiak/shiaak/Kyless obstacle does not apply); native sprite is 64x128; catalog nativeTallImage matches the one-body add_mos'
SQ = 'zones/'

AC = 'general/npcs/aquatic_critter.lua'
AD = 'general/npcs/aquatic_demon.lua'
SP = 'general/npcs/spider.lua'
MO = 'zones/unhallowed-morass/npcs.lua'

# ---- pack 1: aquatic ----
asset(1, 'squid', 'squid', 'flooded-cave, murgol-lair, temple-of-creation, lake-nur, tannen-tower (aquatic/critter, default-name image, non-unique); trollmire removes squids from its own pool only by zeroing rarity',
      [src(AC, 'name = "squid"')], src(AC, 'define_as = "BASE_NPC_AQUATIC_CRITTER"'), None, 'aquatic', 'critter', False, False,
      'base BASE_NPC_AQUATIC_CRITTER (aquatic/critter, no image=); ' + SINGLE + '; NPC.lua:33 gives aquatic_critter_squid.png; zone loaders (trollmire, lake-nur, tannen-tower) only change rarity fields',
      'aquatic_critter_squid.png',
      [STY, ('identity', NPC + 'aquatic_critter_squid.png', 'Native shape: a fat taupe-brown squid with a rounded mantle, one large golden eye with a dark pupil and eight thick curling arms.'),
       ('family', TOK + 'giant-eel.png', 'Shipped giant eel (slate-blue S-curve): show the aquatic finish only; the squid is a rounded mantle with eight curled arms, not a snake-like body.')],
      "A plump common squid seen from a steep overhead three-quarter angle: a broad rounded warm-taupe mantle with soft mottled cocoa spots and a pale cream underside, a single large round golden-yellow eye with a dark pupil, a short blunt siphon, and eight thick short tapered arms curling outward in a loose radial spread with pale suckers on the undersides. Compact, chunky and complete.",
      "Aquatic critters: giant eel (slate-blue S-curve), electric eel, dragon turtle (green shell). The squid is the only round-mantled cephalopod: broad rounded mantle with eight short thick curled arms and a golden eye (silhouette: rounded blob with radial curled arms; hue: warm taupe-brown; value: mid-light). The ink squid (built beside it) is slimmer, cooler lavender-grey with fins and long trailing tentacles.",
      "Warm mid taupe and cocoa-brown mantle with lighter cream underside and pale suckers, bright golden eye; nothing darker than mid tone." + DISC,
      'READY single (squid)', ('silhouette', 'value', 'hue'))

asset(1, 'ink-squid', 'ink squid', 'flooded-cave, temple-of-creation, murgol-lair, lake-nur, tannen-tower (aquatic/critter, default-name image, non-unique)',
      [src(AC, 'name = "ink squid"')], src(AC, 'define_as = "BASE_NPC_AQUATIC_CRITTER"'), None, 'aquatic', 'critter', False, False,
      'base BASE_NPC_AQUATIC_CRITTER (aquatic/critter, no image=); ' + SINGLE + '; NPC.lua:33 gives aquatic_critter_ink_squid.png; name also matches trollmire\'s e.name:find("squid") rarity filter, which changes rarity only',
      'aquatic_critter_ink_squid.png',
      [STY, ('identity', NPC + 'aquatic_critter_ink_squid.png', 'Native shape: a slim lavender-grey squid with a pointed mantle and fins, a golden eye and long trailing tentacles.'),
       ('family', TOK + 'giant-eel.png', 'Shipped giant eel (slate-blue S-curve): show the aquatic finish only; the ink squid is a slim pointed cephalopod, not an eel.')],
      "A slender ink squid seen from a steep overhead three-quarter angle: a long pointed torpedo-shaped lavender-grey mantle with a pair of triangular pale fins at its tip and fine darker violet speckles along the back, a golden eye, and eight long tapering arms trailing backward and out in a streamlined fan, two of them much longer feeding tentacles with paddle tips, dark violet ink-stained ends. Streamlined, elegant, compact and complete.",
      "Aquatic critters: giant eel (slate-blue S-curve), dragon turtle, and the common squid (fat rounded taupe-brown mantle with short curled arms). The ink squid is the slim one: pointed torpedo mantle with fins and long trailing tentacles (silhouette: pointed teardrop with a long streamlined fan of arms), cool lavender-grey with violet speckles (hue), lighter than the squid (value). It must never look like the fat taupe squid.",
      "Cool mid-light lavender-grey mantle with pale silver-lilac fins, violet speckles and violet-stained tentacle ends, bright golden eye; nothing darker than mid tone." + DISC,
      'READY single (ink squid)', ('silhouette', 'value', 'hue'))

asset(1, 'water-imp', 'water imp', 'flooded-cave, lake-nur, temple-of-creation, tannen-tower (aquatic/demon, default-name image, non-unique; a forest vault also spawns it by name)',
      [src(AD, 'name = "water imp"')], src(AD, 'define_as = "BASE_NPC_AQUATIC_DEMON"'), None, 'aquatic', 'demon', False, False,
      'base BASE_NPC_AQUATIC_DEMON (aquatic/demon, no image=); ' + SINGLE + '; NPC.lua:33 gives aquatic_demon_water_imp.png; zone loaders only change rarity fields',
      'aquatic_demon_water_imp.png',
      [STY, ('identity', NPC + 'aquatic_demon_water_imp.png', 'Native shape: a small teal-blue horned imp with big pointed ears, bare pot belly, a thin tail and both clawed hands raised in a casting pose.'),
       ('family', TOK + 'murgol.png', 'Shipped Murgol (finned yaech in armour with a trident): the water imp is a tiny unarmoured horned imp, no fins, no trident.')],
      "A small mischievous water imp seen from a steep overhead three-quarter angle: a stocky teal-blue skinned body with a paler aqua pot belly, two short curved horns, large pointed bat-like ears, big round pale eyes and a wide toothy grin, thin arms raised out and up with clawed hands spread as if lobbing a spell, short stubby legs planted apart and a thin tail curling behind. Small, cheeky and complete.",
      "Aquatic demons and humanoids: Murgol (armoured finned yaech), Lady Zoisla (naga). The water imp is a small unarmoured horned biped with bat ears, arms raised and a pot belly (silhouette: small T-shaped figure with horns and ears; hue: teal-blue with paler belly; value: mid).",
      "Mid teal-blue skin lifted with pale aqua belly and highlight planes, ivory horns and claws, pale eyes; nothing darker than mid tone." + DISC,
      'READY single (water imp)', ('silhouette', 'value', 'hue'))

asset(1, 'walrog', 'Walrog', 'temple-of-creation, flooded-cave (aquatic/demon unique lord of water, no define_as, explicit nice_tile tall body)',
      [src(AD, 'name = "Walrog"'), src(AD, 'image="npc/aquatic_demon_walrog.png"')], src(AD, 'define_as = "BASE_NPC_AQUATIC_DEMON"'), None, 'aquatic', 'demon', True, False,
      TALL.replace('<png>', 'npc/aquatic_demon_walrog.png') + '; unique=true with no define_as (name+type+subtype+image bind it; the catalog accepts the native-tall body of any unique entry); single-cell art path also accepted (nicer tiles off)',
      'aquatic_demon_walrog.png',
      [STY, ('identity', NPC + 'aquatic_demon_walrog.png', 'Native shape (64x128 tall): a translucent bright-blue humanoid made of churning water with two long curling horns, hanging arms, no legs, water spray falling off his edges.'),
       ('family', TOK + 'shivgoroth.png', 'Shipped shivgoroth (lean pale-blue ice elemental): Walrog is a broad horned water-lord made of curling water, not ice shards.')],
      "A towering horned water demon rising from the disc, drawn upright and compact: a broad-shouldered humanoid torso and thick arms hanging at his sides sculpted entirely from churning translucent bright-cerulean water with white foam crests and swirling current lines, a hooded featureless head with two long swept-back curling horns of clear aqua water, two pale glowing eyes, the lower body dissolving into a spiralling whirlpool tail that coils on the disc, a few droplets orbiting. Glassy, watery and imposing, all inside the disc.",
      "Elemental or watery tokens: shivgoroth and greater shivgoroth (pale ice elementals), Murgol and the nagas (scaled), the water imp (small teal imp). Walrog is the only large horned figure made of flowing water with a whirlpool tail (silhouette: broad torso, two swept horns, spiral lower body; hue: saturated cerulean with white foam; value: mid-light with white crests and deeper blue core lines so its edge stays readable).",
      "Saturated mid cerulean and azure water with pale aqua highlight bands, bright white foam crests, deeper blue swirl lines, pale glowing eyes; nothing darker than mid tone." + DISC,
      'READY unique native-tall (Walrog)', ('silhouette', 'value', 'hue'))

# ---- pack 2: spiderkin of the morass and the ardhungol brood ----
asset(2, 'weaver-hatchling', 'weaver hatchling', 'unhallowed-morass (spiderkin/spider, explicit image=npc/spiderkin_spider_weaver_young.png, non-unique; also spawned as an escort/summon by the same entity name)',
      [src(MO, 'name = "weaver hatchling"'), src(MO, 'image="npc/spiderkin_spider_weaver_young.png"')], src(MO, 'define_as = "BASE_NPC_SPIDER"'), None, 'spiderkin', 'spider', False, False,
      'zone-local BASE_NPC_SPIDER (spiderkin/spider, no image=); explicit image= npc/spiderkin_spider_weaver_young.png (the PNG name differs from the default-name formula, so the pin is the explicit image); no nice_tile/add_mos/shader/anim/moddable_tile/tint; single path',
      'spiderkin_spider_weaver_young.png',
      [STY, ('identity', NPC + 'spiderkin_spider_weaver_young.png', 'Native shape: a small round nearly translucent pale-blue spider hatchling with a bulbous banded body and bright glowing white orbs around its feet.'),
       ('family', TOK + 'weaver-queen.png', 'Shipped Weaver Queen (large frost-white furry spider): the hatchling is small, smooth and glassy with glowing orbs, not a furry queen.')],
      "A small round spider hatchling seen from a steep overhead three-quarter angle: a plump smooth glassy pale-aqua abdomen with faint darker-blue curved stripes and a soft inner glow, a small rounded head with a cluster of big dark eyes with white highlights, eight short delicate pale blue-grey legs tucked in a tight radial spread, and a bright white-blue glowing orb of light at the tip of about four of the legs. Tiny, delicate, translucent, complete.",
      "Spider tokens: Ungole (large black, red marks), Weaver Queen (large frost-white furry with blue legs). The weaver hatchling is the small smooth translucent one with a plump round striped abdomen and glowing white orbs at its feet (silhouette: small round body with orb-tipped short legs; hue: pale aqua and blue stripes; value: light). Built beside the orb spinner (long ribbed body, long legs) so the two blue spiders differ by shape, not only size.",
      "Light translucent aqua and pale cyan-white glassy body with mid-blue curved stripes, bright white glowing orbs, pale blue-grey legs, dark eyes with white glints; nothing darker than mid tone except the eyes." + DISC,
      'READY single (weaver hatchling)', ('silhouette', 'value', 'hue'))

asset(2, 'orb-spinner', 'orb spinner', 'unhallowed-morass (spiderkin/spider, default-name image, non-unique; its escort is an orb weaver, not covered)',
      [src(MO, 'name = "orb spinner"')], src(MO, 'define_as = "BASE_NPC_SPIDER"'), None, 'spiderkin', 'spider', False, False,
      'zone-local BASE_NPC_SPIDER (spiderkin/spider, no image=); ' + SINGLE + '; NPC.lua:33 gives spiderkin_spider_orb_spinner.png',
      'spiderkin_spider_orb_spinner.png',
      [STY, ('identity', NPC + 'spiderkin_spider_orb_spinner.png', 'Native shape: a long-bodied pale steel-blue and bone-white ribbed spider with a segmented striped abdomen and long thin legs.'),
       ('family', TOK + 'weaver-queen.png', 'Shipped Weaver Queen (round furry frost-white spider): the orb spinner has a long ribbed segmented body with hard bone-white bands, no fur.')],
      "A long-bodied spider seen from a steep overhead three-quarter angle: an elongated tapering abdomen made of many ribbed segments alternating steel-blue and bone-white like a striped shell, a narrow head with a row of small dark eyes and two curved fangs with a drip of pale fluid, and eight long thin angular legs with pale joints held in a wide asymmetric spread. Sleek, ribbed, elegant, complete.",
      "Spider tokens: Ungole (round black), Weaver Queen (round furry frost-white), weaver hatchling (small round glassy with glowing orbs). The orb spinner is the elongated ribbed one: long tapering abdomen banded steel-blue and bone-white with long thin legs (silhouette: long ribbed teardrop with wide leg spread; hue: steel-blue with bone bands; value: mid with bright bone stripes).",
      "Mid steel-blue and slate-blue abdomen shell with bright bone-white rib bands, pale blue-grey legs with pale joints, dark eyes; nothing darker than mid tone except the eyes." + DISC,
      'READY single (orb spinner)', ('silhouette', 'value', 'hue'))

asset(2, 'giant-spider', 'giant spider', 'ardhungol, daikara, forest vaults and other general spawns (spiderkin/spider, default-name image, no define_as). Same-name actors that must stay native: tutorial-combat-stats TUT_SPIDER_1 (same type, define_as differs) and the player-summoned giant spider (animal/spider)',
      [src(SP, 'name = "giant spider"')], src(SP, 'define_as = "BASE_NPC_SPIDER"'), None, 'spiderkin', 'spider', False, False,
      'base BASE_NPC_SPIDER (spiderkin/spider, no image=); ' + SINGLE + '; NPC.lua:33 gives spiderkin_spider_giant_spider.png. Name collisions handled by the exact-identity contract itself: the tutorial spider carries define_as TUT_SPIDER_1 (entry requires none) and the wild-gift summon is type animal (entry requires spiderkin), so neither can wear this token; no name+define_as key extension needed',
      'spiderkin_spider_giant_spider.png',
      [STY, ('identity', NPC + 'spiderkin_spider_giant_spider.png', 'Native shape: a big dark slate-grey spider with a glossy shell, pale silvery veined markings on the oval abdomen, glossy black eyes and long banded legs.'),
       ('family', TOK + 'ungole.png', 'Shipped Ungole (round pitch-black spider with red eyes and red marks): the giant spider is a lighter slate-grey with pale silver dorsal markings and no red.')],
      "A large ordinary giant spider seen from a steep overhead three-quarter angle: an oval slate-grey glossy abdomen with a bold pale-silver chevron and vein pattern across its back, a rounded cephalothorax with four big glossy black eyes with white glints and small pale pedipalps, and eight long slender angular legs in mid grey with pale silver bands at each joint, spread wide in an open radial pose. Elegant, lanky, complete.",
      "Spider tokens: Ungole (round pitch-black body, red eyes and marks, short-legged), Weaver Queen (frost-white furry), the pale ribbed orb spinner, the brown spitting spider and the ivory chitinous spider (built alongside). The giant spider is the slate-grey lanky one with pale silver chevron markings on an oval abdomen and long banded legs (silhouette: oval body with long wide-spread thin legs; hue: neutral slate-grey with silver, no red; value: mid-grey clearly lighter than Ungole).",
      "Mid slate-grey glossy shell lifted with light steel-grey planes, bold pale silver dorsal chevron, pale silver leg bands, black glossy eyes with white glints; the body must read as mid grey, never black." + DISC,
      'READY single (giant spider)', ('silhouette', 'value', 'hue'))

asset(2, 'spitting-spider', 'spitting spider', 'ardhungol, daikara, forest vaults (spiderkin/spider, default-name image, non-unique)',
      [src(SP, 'name = "spitting spider"')], src(SP, 'define_as = "BASE_NPC_SPIDER"'), None, 'spiderkin', 'spider', False, False,
      'base BASE_NPC_SPIDER (spiderkin/spider, no image=); ' + SINGLE + '; NPC.lua:33 gives spiderkin_spider_spitting_spider.png',
      'spiderkin_spider_spitting_spider.png',
      [STY, ('identity', NPC + 'spiderkin_spider_spitting_spider.png', 'Native shape: a hairy chestnut-brown spider with a round high abdomen, big glossy black eyes and long fangs with a stream of yellow-green venom spitting from its mouth.'),
       ('family', TOK + 'ungole.png', 'Shipped Ungole (black spider with red): the spitting spider is warm chestnut-brown with a green venom spray, no red marks.')],
      "A hairy chestnut-brown spider rearing slightly forward, seen from a steep overhead three-quarter angle: a tall round bristly abdomen in warm brown with lighter tan hairs, a broad head with big glossy black eyes with white glints and two long curved dark fangs, a thin stream of bright acid-green venom spraying forward from the fangs in a short arc that stays on the disc, and eight sturdy bent legs in brown with tan joints, front legs raised. Aggressive and complete.",
      "Spider tokens: Ungole (black, red), giant spider (slate-grey, silver chevrons), Weaver Queen (frost-white), chitinous spider (ivory plates). The spitting spider is the warm brown hairy one that is spraying an acid-green venom stream (silhouette: reared front with a visible venom arc; hue: chestnut brown plus acid green; value: mid).",
      "Warm mid chestnut-brown with lighter tan hair tufts and tan leg joints, bright acid-green venom stream as the accent, black glossy eyes with white glints; nothing darker than mid tone except the eyes." + DISC,
      'READY single (spitting spider)', ('silhouette', 'value', 'hue'))

# ---- pack 3 ----
asset(3, 'chitinous-spider', 'chitinous spider', 'ardhungol, dreadfell, daikara (spiderkin/spider, default-name image, non-unique)',
      [src(SP, 'name = "chitinous spider"')], src(SP, 'define_as = "BASE_NPC_SPIDER"'), None, 'spiderkin', 'spider', False, False,
      'base BASE_NPC_SPIDER (spiderkin/spider, no image=); ' + SINGLE + '; NPC.lua:33 gives spiderkin_spider_chitinous_spider.png',
      'spiderkin_spider_chitinous_spider.png',
      [STY, ('identity', NPC + 'spiderkin_spider_chitinous_spider.png', 'Native shape: a pale ivory-white spider with a broad ridged shell, small dark eyes and many thin legs.'),
       ('family', TOK + 'weaver-queen.png', 'Shipped Weaver Queen (fuzzy frost-white spider): the chitinous spider is smooth hard armour with dark plate seams, no fur.')],
      "A heavily armoured spider seen from a steep overhead three-quarter angle: a broad smooth glossy ivory-bone carapace made of overlapping ridged plates with dark warm-grey seams and a faint pale jade sheen, a blocky armoured head with four small dark eyes and stout mandibles, and eight thick short spiked legs in the same plated ivory with dark joints, planted in a compact wide stance. Solid, tank-like, complete.",
      "Spider tokens: Ungole (black), giant spider (slate-grey, long legs), spitting spider (brown, hairy, venom), Weaver Queen (fuzzy frost-white with blue legs), orb spinner (steel-blue ribbed). The chitinous spider is the armoured ivory tank: smooth hard plates with dark seams and short thick spiked legs (silhouette: broad blocky shell, short spiked legs, no fur; hue: ivory-bone with a faint jade tint; value: light).",
      "Light ivory-bone and pale warm-grey armour plates with faint jade sheen, darker warm-grey seams and leg joints, small dark eyes; nothing darker than mid tone except seams and eyes." + DISC,
      'READY single (chitinous spider)', ('silhouette', 'value', 'hue'))

asset(3, 'ghoul', 'ghoul', 'dreadfell, telmur, halfling-ruins, blighted-ruins, last-hope-graveyard, tannen-tower, rak-shor-pride, high-peak (undead/ghoul with define_as GHOUL, default-name image, non-unique). Same-name actors that must stay native: the Master of Flesh player minion (no define_as), Walking Corpse (other name, same PNG), risen corpse (other name)',
      [src('general/npcs/ghoul.lua', 'name = "ghoul", color=colors.TAN, define_as = "GHOUL"')], src('general/npcs/ghoul.lua', 'define_as = "BASE_NPC_GHOUL"'), 'GHOUL', 'undead', 'ghoul', False, False,
      'base BASE_NPC_GHOUL (undead/ghoul, no image=); ' + SINGLE + '; define_as="GHOUL" is on the leaf; NPC.lua:33 gives undead_ghoul_ghoul.png. The player-summoned ghoul (talents/spells/master-of-flesh.lua minions_list.ghoul) has the same name, type and default image but no define_as, so the exact-identity contract rejects it and it stays native; "risen corpse" and the Walking Corpse effect minion share the PNG under other names and stay native',
      'undead_ghoul_ghoul.png',
      [STY, ('identity', NPC + 'undead_ghoul_ghoul.png', 'Native shape: a hunched, gaunt brown-skinned humanoid with a sunken skull-like face, long dangling arms and torn flesh.'),
       ('family', TOK + 'skeleton-warrior.png', 'Shipped skeleton warrior (bone white, armed): the ghoul is rotting flesh, no armour, no weapon, hunched on all bare limbs.')],
      "A hunched gaunt ghoul seen from a steep overhead three-quarter angle: emaciated leathery tan-brown skin stretched over visible ribs and spine with grey patches of rot and torn hanging flesh strips, a sunken skull-like head with hollow dark eye sockets and a gaping fanged mouth, very long thin arms ending in long dark claws dragging low on both sides, bent legs, no clothes, no weapon. Feral, decayed and complete.",
      "Undead tokens: skeleton warrior/archer/mage (bone-white with gear), the necromancer, the player ghoul race. The common ghoul is the bare-skinned hunched rotting brute with long claws (silhouette: hunched with long low-hanging arms; hue: sickly tan-brown with grey rot patches; value: mid-light). Never bone-white, never armoured.",
      "Sickly mid-light tan and leather-brown skin lifted with pale dusty-grey rot patches and bone-pale ribs, dark hollow eyes, dark claws; nothing darker than mid tone except the eye sockets." + DISC,
      'READY single (ghoul)', ('silhouette', 'value', 'hue'))

asset(3, 'drem', 'drem', 'deep-bellow, maze, arena, dredge escorts (horror/corrupted, explicit image=npc/horror_corrupted_dremling.png -- the filename swap with dremling -- non-unique, single-cell)',
      [src('general/npcs/horror-corrupted.lua', 'name = "drem"'), src('general/npcs/horror-corrupted.lua', 'image = "npc/horror_corrupted_dremling.png"')],
      src('general/npcs/horror-corrupted.lua', 'define_as = "BASE_NPC_CORRUPTED_HORROR"'), None, 'horror', 'corrupted', False, False,
      'base BASE_NPC_CORRUPTED_HORROR (horror/corrupted, no image=); leaf sets explicit image= npc/horror_corrupted_dremling.png (a 64x64 single-cell sprite whose file is named after dremling; dremling in turn resolves to the 64x128 npc/horror_corrupted_drem.png); no nice_tile/add_mos/shader/anim/moddable_tile/tint; single path. Catalog: dremling (native_tall, image horror_corrupted_drem.png) already ships; the two entries differ by name and by image and neither can wear the other (tested)',
      'horror_corrupted_dremling.png',
      [STY, ('identity', NPC + 'horror_corrupted_dremling.png', 'Native shape: a small stocky dwarf-like figure in patched brown-grey rags and rusty scrap armour with a pale featureless face, a battered rusty waraxe in one hand and a dented round shield on the other arm.'),
       ('family', TOK + 'dremling.png', 'Shipped dremling (tall pale stone-grey spiked giant with a hammer): the drem is a small hunched axe-and-shield dwarf-like warrior in rags, not a giant statue.')],
      "A small stocky dwarf-like dredge warrior seen from a steep overhead three-quarter angle: a hunched squat body with a large round pale-grey featureless smooth face under a patched brown leather hood-cap, wearing layered patched warm grey-brown rags and rusty scrap plates with tarnished ochre rivets, a battered rusty waraxe with a notched blade held up in the right hand and a dented round wooden shield with an iron rim on the left arm, short bowed legs in worn boots. Battered, ill-kept and complete.",
      "Corrupted horror tokens: dremling (tall pale stone-grey spiked giant with a hammer, native-tall), horned horror, the mouth. The drem is the small hunched axe-and-shield warrior in patched brown-grey rags with a pale blank face and rusty gear (silhouette: compact with a raised axe and a round shield; hue: warm rust-brown and grey; value: mid). Never a tall giant, never spiked stone.",
      "Mid warm grey-brown patched rags and hood lifted with lighter tan planes, rusty ochre and orange-brown metal, pale-grey smooth face as a value break, iron-grey shield rim; nothing darker than mid tone." + DISC,
      'READY single (drem)', ('silhouette', 'value', 'hue'))

asset(3, 'gigantic-sandworm-tunneler', 'gigantic sandworm tunneler', 'briagh-lair, sandworm-lair, eruan (vermin/sandworm, non-unique, explicit nice_tile tall body); the scripted sandworm burrower/huge burrower and the gigantic corrosive tunneler / gravity worm are other names and stay native or already-mapped as before',
      [src('general/npcs/sandworm.lua', 'name = "gigantic sandworm tunneler"'), src('general/npcs/sandworm.lua', 'image="npc/vermin_sandworm_gigantic_sandworm_tunneler.png"')],
      src('general/npcs/sandworm.lua', 'define_as = "BASE_NPC_SANDWORM"'), None, 'vermin', 'sandworm', False, True,
      TALL.replace('<png>', 'npc/vermin_sandworm_gigantic_sandworm_tunneler.png') + '; non-unique, so the catalog entry must carry native_tall=true; base BASE_NPC_SANDWORM has no image=/shader; single-cell art path also accepted (nicer tiles off)',
      'vermin_sandworm_gigantic_sandworm_tunneler.png',
      [STY, ('identity', NPC + 'vermin_sandworm_gigantic_sandworm_tunneler.png', 'Native shape (64x128 tall): a thick tan-brown segmented worm rearing straight up from a crater of earth, its top split open into a four-petal flower-like maw lined in red-brown flesh, with crackling blue lightning arcing around it.'),
       ('family', TOK + 'sandworm-destroyer.png', 'Shipped sandworm destroyer (closed rust-orange ring with a toothy round mouth): the tunneler is a thicker earth-brown worm reared up with a four-petal split maw, not a coiled ring.')],
      "A gigantic thick tunneling sandworm rearing up from the disc, drawn compact: a very thick segmented earth-brown and dusty umber body with fine ring ridges and paler tan underbelly bands coiling once around its own base in a low heap of broken stone and packed earth chunks, the front third reared up toward the viewer with its head split open into a wide four-petalled flower-like maw, each petal lined inside with glossy red-brown flesh and a few blunt pale teeth, a dark throat at the centre. No lightning, no glow.",
      "Sandworm tokens: sandworm (slim orange S-curve), sandworm destroyer (closed rust-orange ring with a round toothy mouth), sandworm burrower (green arches on a sand heap), sandworm queen. The tunneler is the only thick earth-brown worm reared up with a four-petal split maw over a rubble heap (silhouette: thick coil plus reared petal head; hue: umber earth brown, not orange, not green; value: mid).",
      "Mid earth-brown and dusty umber body lifted with paler tan segment bands and lighter ridge highlights, glossy red-brown maw interior, pale blunt teeth, light grey-tan stone chunks; nothing darker than mid tone except the throat." + DISC,
      'READY non-unique native-tall (gigantic sandworm tunneler)', ('silhouette', 'value', 'hue'))


def retry(id_, pack, **changes):
    base = next(a for a in A if a['id'] == id_)
    A.append(dict(base, pack=pack, **changes))


# ---- retry packs are appended below by later edits ----
exec((HERE / 'retries.py').read_text()) if (HERE / 'retries.py').exists() else None


def build():
    packs = {}
    identities = []
    render = 'game/addons/tome-checker-revised/evidence/monster-batch-k-20260929/source-contracts.json'
    seen = set()
    for a in A:
        if a['id'] in seen:
            continue
        seen.add(a['id'])
        native_rel = NPC + a['native']
        ident = {'id': a['id'], 'native_name': a['name'], 'source': a['srcs'][0], 'define_as': a['define_as'],
                 'type': a['type'], 'subtype': a['subtype'], 'unique': a['unique'], 'native_tall': a['native_tall'],
                 'structure': a['structure'], 'native_image': 'npc/' + a['native'], 'native_image_path': native_rel,
                 'native_image_sha256': sha(native_rel), 'native_image_size': None, 'verdict': a['verdict']}
        from PIL import Image
        with Image.open(WS / native_rel) as im:
            ident['native_image_size'] = list(im.size)
        if a['base']:
            ident['base_source'] = a['base']
        if len(a['srcs']) > 1:
            ident['extra_sources'] = a['srcs'][1:]
        identities.append(ident)
    ev = {'schema': 1,
          'task': 'monster-batch-k: static re-verification (no game launch) of the twelve batch-2 identities of the second gap survey (squid, ink squid, water imp, Walrog, weaver hatchling, orb spinner, ghoul, drem, giant spider, spitting spider, chitinous spider, gigantic sandworm tunneler) against game/modules/tome source and native sprites. Survey verdicts were not trusted; every field below was read from source.',
          'new_ids_not_in_catalog_before_this_batch': [i['id'] for i in identities], 'identities': identities,
          'name_collisions_checked': [
              {'name': 'giant spider', 'other_definitions': ['zones/tutorial-combat-stats/npcs.lua TUT_SPIDER_1 (spiderkin/spider, define_as TUT_SPIDER_1)', 'talents/gifts/summon-utility.lua wild-gift summon (type animal, subtype spider, explicit same PNG)'],
               'outcome': 'catalog entry has define_as nil and type spiderkin: both others are rejected by exactIdentity (define_as / type mismatch); they stay native; no key extension'},
              {'name': 'ghoul', 'other_definitions': ['talents/spells/master-of-flesh.lua minions_list.ghoul (undead/ghoul, no define_as, default PNG)', 'birth/races/undead.lua and talents/undeads/ghoul.lua use the capitalised name "Ghoul" (player race / player minion)'],
               'outcome': 'catalog entry requires define_as GHOUL: the player minion has none and stays native'},
              {'name': 'drem', 'other_definitions': ['general/npcs/horror-corrupted.lua dremling (different name; its resolved body is npc/horror_corrupted_drem.png)'],
               'outcome': 'distinct names; images are swapped between the two entries and neither can wear the other'},
              {'name': 'weaver hatchling', 'other_definitions': [], 'outcome': 'unique name, single definition (also used as escort/summon by name)'},
              {'name': 'squid / ink squid / water imp / Walrog / orb spinner / spitting spider / chitinous spider / gigantic sandworm tunneler', 'other_definitions': [], 'outcome': 'unique names in the native tree, no addon redefinition found'}],
          'kept_native': []}
    out = ADDON / 'evidence/monster-batch-k-20260929/source-contracts.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(ev, indent=2, ensure_ascii=False) + '\n')
    evsha = hashlib.sha256(out.read_bytes()).hexdigest()
    for a in A:
        refs = [{'path': p, 'sha256': sha(p), 'role': r, 'note': n} for r, p, n in a['refs']]
        entry = {'asset_id': a['id'], 'native_name': a['name'], 'scope': a['scope'], 'sources': a['srcs'], 'references': refs,
                 'contrast_dimensions': list(a['dims']),
                 'prompt_fields': {'subject': a['subject'], 'contrast': a['contrast'], 'composition': a['comp'] or COMP, 'palette': a['palette']},
                 'kind': 'creature', 'max_attempts': 1, 'gate': 'ready',
                 'gate_reason': f"Exact source identity re-verified directly against game/modules/tome source (name={a['name']}, define_as={a['define_as']}, type={a['type']}/subtype={a['subtype']}, unique={a['unique']}); details and hashes in evidence/monster-batch-k-20260929/source-contracts.json. {a['structure']}. Exact catalog entry only, never a whole-subtype mapping.",
                 'render_evidence': [{'path': render, 'sha256': evsha}]}
        packs.setdefault(a['pack'], []).append(entry)
    for n, assets in packs.items():
        p = ADDON / f'art/production/batches/monster-batch-k-{n}.json'
        if p.exists():
            print('exists, skipped', p.name)
            continue
        p.write_text(json.dumps({'schema': 1, 'batch_id': f'monster-batch-k-{n}', 'assets': assets}, indent=2, ensure_ascii=False) + '\n')
        print('wrote', p.name)


if __name__ == '__main__':
    build()
