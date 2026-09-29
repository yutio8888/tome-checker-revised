"""Generate the monster-batch-p task packs and the pinned source-contract
evidence (survey-2 section 7, batch 7: snow giant, minotaur, snow giant
thunderer, Healer Astelrid, mountain troll, snow giant boulder thrower,
mountain troll thunderer, snow giant chieftain, ogre guard, ogre mauler, ogre
rune-spinner, ogre pounder). Pure bookkeeping: hashes native sources/sprites,
writes JSON. Retry packs are appended by later edits of retries.py (never
overwritten)."""
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


def src(path, anchor, after=None, root=D):
    lines = (WS / (root + path)).read_text().splitlines()
    start = 0
    if after:
        start = next(i for i, l in enumerate(lines) if after in l)
    cands = [i + 1 for i, l in enumerate(lines) if i >= start and anchor in l]
    assert cands, (path, anchor)
    return {'path': root + path, 'sha256': sha(root + path), 'line': cands[0], 'anchor': anchor}


COMP = ("One compact complete creature on a single circular tabletop disc, steep overhead three-quarter camera; visible clear neutral base ring on every side. Keep all anatomy and equipment well inside the inner four-fifths of disc radius. Base brightness must visually match reference neutral disc, with no illumination spill or ground effects. Disc plate discipline: measured results show generations of this style reference tend to render the disc DARKER than the reference, never lighter. So do not darken the disc at all: render the neutral disc -- including the whole outer-sixth ring band and the area under the creature -- at the style reference's own brightness, if anything a hair lighter, and never darker. No warm cast, glow, bounce-light, gradient or vignette anywhere on the disc. Do not darken the creature to compensate either. Add no warm cast, glow, bounce-light, gradient or vignette to the disc anywhere, including directly under or behind dark-bodied creatures.")
FIT = " The ENTIRE creature, every limb, tail, wing, drip, staff and effect included, fits inside a circle of about three quarters of the disc radius around the disc centre, leaving a wide bare charcoal ring of base plate on every side, yet the creature is large and bold inside that circle."
GIANT = " This is a huge giant, but on the tabletop disc it is drawn COMPACT: hunched forward with rolled shoulders, bent knees and elbows kept in close, the weapon held short and close to the body, so the whole figure is a broad chunky mass that fills the inner three quarters of the disc yet never reaches the outer sixth ring band. Do not draw a tall standing figure that would run off the disc; the feet and the head both stay well inside the disc."
DISC = " Dry neutral charcoal disc with restrained copper-grey bevel, kept a visibly lighter value than the creature's darkest parts so the two never merge."
A = []


def asset(pack, id_, name, scope, srcs, base, define_as, typ, sub, unique, native_tall, structure, native, refs, subject,
          contrast, palette, verdict, dims=('silhouette', 'value', 'hue'), comp=None):
    A.append(dict(comp=comp, pack=pack, id=id_, name=name, scope=scope, srcs=srcs, base=base, define_as=define_as, type=typ,
                  subtype=sub, unique=unique, native_tall=native_tall, structure=structure, native=native, refs=refs,
                  subject=subject, contrast=contrast, palette=palette, verdict=verdict, dims=dims))


STY = ('style', STYLE, 'Approved disc, lighting and camera; do not copy its creature.')
TALL_EXPLICIT = ('resolvers.nice_tile{image="invis.png", add_mos={{image="<png>", display_h=2, display_y=-1}}} names the PNG explicitly (no {tall=1} shorthand and no =BASE=TILE= indirection), '
                 'so the resolved tall body is statically pinnable (same form as the batch K gigantic sandworm tunneler and batch M gwelgoroth entries); native sprite 64x128')
TALL_SHORT = ('resolvers.nice_tile{tall=1} shorthand (resolvers.lua nice_tile: invis.png + add_mos{image=e.image (the NPC.lua:33 default-name PNG), display_h=2, display_y=-1}), '
              'the same expansion live-confirmed for xhaiak/shiaak/naga nereid/Kyless (evidence/monster-live-f-20260929, monster-batch-l-live-20260929, monster-batch-j-live-20260929); native sprite 64x128')
SG = 'general/npcs/snow-giant.lua'
MI = 'general/npcs/minotaur.lua'
TR = 'general/npcs/troll.lua'
OG = 'general/npcs/ogre.lua'
CV = 'zones/conclave-vault/npcs.lua'
RES = src('resolvers.lua', 'function resolvers.calc.nice_tile', root='game/modules/tome/')


def R(family_id, note):
    return ('family', TOK + family_id + '.png', note)


def IDN(png, note):
    return ('identity', NPC + png, note)


SNOW_BASE = 'base BASE_NPC_SNOW_GIANT (giant/ice, no image=)'
SNOW_TALK = 'resolvers.inscriptions(1,"infusion") (random infusion, no display write); ingredient_on_death only'
SNOW_REF = R('burb-snow-giant-champion', 'Shipped Burb the snow giant champion (silver plate armour, horned helm, blue lightning): none of the four ordinary snow giants wears plate armour or that silver-white palette.')


def snow_scope(extra):
    return ('snow-giant.lua (giant/ice, non-unique, no define_as, resolvers.nice_tile with the explicit PNG in add_mos); daikara, tempest-peak, lesser vault snow-giant-camp (entity filters by name only); ' + extra)


# ---- pack 1: the four snow giants ----
asset(1, 'snow-giant', 'snow giant', snow_scope('the plain member of the family, rarity 1'),
      [src(SG, 'name = "snow giant", color=colors.WHITE'), src(SG, 'add_mos = {{image="npc/giant_ice_snow_giant.png"')], src(SG, 'define_as = "BASE_NPC_SNOW_GIANT"'), None, 'giant', 'ice', False, True,
      SNOW_BASE + '; ' + TALL_EXPLICIT.replace('<png>', 'npc/giant_ice_snow_giant.png') + '; talent Mind Disruption (activated npc talent, misc/npcs.lua); ' + SNOW_TALK + '; no sustains_at_birth',
      'giant_ice_snow_giant.png',
      [STY, IDN('giant_ice_snow_giant.png', 'Native shape (64x128 tall): a bald, heavy-browed pale blue-grey giant in a dark hide tunic, arms hanging, no weapon shown, standing upright.'), SNOW_REF],
      "A snow giant seen from a steep overhead three-quarter angle: a huge hunched bald humanoid giant with pale slate blue-grey skin, thick bare shoulders and arms with dark leather wristbands, a heavy-browed flat grim face with a wide jaw and deep-set eyes, a dark charcoal hide tunic with a rope belt, heavy dark boots wrapped in frost-white fur, patches of white frost on the shoulders and knuckles, a short thick grey stone-headed maul held low in the right hand against the hip and the left hand hanging open. No horned helm, no beard, no armour, no lightning. Cold, heavy and complete.",
      "Four snow giants share this body: this is the PLAIN one (silhouette: bald round head, broad shoulders, both arms LOW with a short maul at the hip; hue: cool pale slate blue-grey; value: mid-light with a dark tunic). The thunderer raises crackling fists and has a white beard, the boulder thrower holds a huge boulder overhead, the chieftain wears horns and a fur mantle; the shipped Burb is silver-armoured.",
      "Pale slate blue-grey skin with lighter icy highlight planes, dark charcoal tunic, grey stone maul head, white frost patches; nothing darker than dark grey except tunic seams and boots; the disc stays neutral charcoal with no blue cast." + DISC,
      'READY non-unique native-tall (snow giant)', comp=COMP + FIT + GIANT)

asset(1, 'snow-giant-thunderer', 'snow giant thunderer', snow_scope('rarity 3, autolevel warriormage; Lightning and Chain Lightning (activated spells, spells/air.lua)'),
      [src(SG, 'name = "snow giant thunderer", color=colors.LIGHT_BLUE'), src(SG, 'add_mos = {{image="npc/giant_ice_snow_giant_thunderer.png"')], src(SG, 'define_as = "BASE_NPC_SNOW_GIANT"'), None, 'giant', 'ice', False, True,
      SNOW_BASE + '; ' + TALL_EXPLICIT.replace('<png>', 'npc/giant_ice_snow_giant_thunderer.png') + '; talents Lightning, Chain Lightning (activated, no sustain); ' + SNOW_TALK + '; no sustains_at_birth',
      'giant_ice_snow_giant_thunderer.png',
      [STY, IDN('giant_ice_snow_giant_thunderer.png', 'Native shape (64x128 tall): a white-bearded pale blue giant with crackling blue lightning arcing around his body and hands.'), SNOW_REF],
      "A snow giant thunderer seen from a steep overhead three-quarter angle: a huge hunched giant with icy pale-blue skin and a long braided white beard, bare heavy shoulders, a dark blue-grey hide tunic and boots, both big clenched fists raised in front of the chest with jagged bright yellow-white and electric-blue lightning bolts arcing between the two fists and around the shoulders, a few small spiky sparks, no weapon. Crackling, bearded and complete.",
      "Four snow giants share this body: the THUNDERER is the bearded one with BOTH FISTS RAISED and zig-zag lightning between them (silhouette: raised elbows, bolt zig-zags, white beard; hue: icy pale blue with vivid yellow-white and electric blue bolts; value: mid-light with bright bolts). The plain snow giant is bald with arms low and a maul; the boulder thrower carries a boulder; the chieftain is horned with a fur mantle.",
      "Icy pale-blue skin with lighter highlight planes, white beard, dark blue-grey tunic, bright yellow-white lightning with electric-blue edges; nothing darker than dark blue-grey except tunic seams; the lightning must not glow onto or tint the disc." + DISC,
      'READY non-unique native-tall (snow giant thunderer)', comp=COMP + FIT + GIANT)

asset(1, 'snow-giant-boulder-thrower', 'snow giant boulder thrower', snow_scope('rarity 3; Throw Boulder (activated npc talent, misc/npcs.lua)'),
      [src(SG, 'name = "snow giant boulder thrower", color=colors.UMBER'), src(SG, 'add_mos = {{image="npc/giant_ice_snow_giant_boulder_thrower.png"')], src(SG, 'define_as = "BASE_NPC_SNOW_GIANT"'), None, 'giant', 'ice', False, True,
      SNOW_BASE + '; ' + TALL_EXPLICIT.replace('<png>', 'npc/giant_ice_snow_giant_boulder_thrower.png') + '; talent Throw Boulder (activated, no sustain); ' + SNOW_TALK + '; no sustains_at_birth',
      'giant_ice_snow_giant_boulder_thrower.png',
      [STY, IDN('giant_ice_snow_giant_boulder_thrower.png', 'Native shape (64x128 tall): a bald grey giant hoisting a huge grey boulder above his head with both arms, mouth open in effort.'), SNOW_REF],
      "A snow giant boulder thrower seen from a steep overhead three-quarter angle: a huge hunched bald giant with weathered warm grey-brown skin, thick bare arms with dark leather wristbands, a brown hide tunic with a rope belt and heavy boots, both arms raised in front of him and lifting a huge rounded rough grey boulder with a few frost patches up to chest height, shoulders hunched with effort, his face grimacing with an open mouth, small pebbles falling from the boulder. No beard, no horned helm, no armour. Straining, heavy and complete.",
      "Four snow giants share this body: the BOULDER THROWER is the one lifting a big round grey boulder in both arms (silhouette: a round rock mass in front of the chest with both arms up around it; hue: warm grey-brown skin and brown tunic with a cool grey boulder; value: mid). The plain snow giant holds a maul low, the thunderer has raised crackling fists and a white beard, the chieftain is horned.",
      "Weathered warm grey-brown skin with lighter tan highlight planes, brown hide tunic, cool light-grey boulder with white frost; nothing darker than dark brown except tunic seams and boots; the disc stays neutral charcoal." + DISC,
      'READY non-unique native-tall (snow giant boulder thrower)', comp=COMP + FIT + GIANT)

asset(1, 'snow-giant-chieftain', 'snow giant chieftain', snow_scope('rarity 7, rank 3, make_escort of three other giant/ice bodies (other names), Knockback and Stun (activated npc talents)'),
      [src(SG, 'name = "snow giant chieftain", color=colors.AQUAMARINE'), src(SG, 'add_mos = {{image="npc/giant_ice_snow_giant_chieftain.png"')], src(SG, 'define_as = "BASE_NPC_SNOW_GIANT"'), None, 'giant', 'ice', False, True,
      SNOW_BASE + '; ' + TALL_EXPLICIT.replace('<png>', 'npc/giant_ice_snow_giant_chieftain.png') + '; talents Knockback, Stun (activated, no sustain); ' + SNOW_TALK + '; no sustains_at_birth; escorts are other giant/ice leaves with their own names',
      'giant_ice_snow_giant_chieftain.png',
      [STY, IDN('giant_ice_snow_giant_chieftain.png', 'Native shape (64x128 tall): a white-bearded giant in a horned iron helm and a white-grey fur mantle, a stone maul in one hand.'), SNOW_REF],
      "A snow giant chieftain seen from a steep overhead three-quarter angle: a huge hunched giant with cold ice-teal skin marked by pale blue war-paint stripes, a horned dark-iron helm with two long curved bone-white horns, a long braided white beard, a big shaggy white-and-grey fur mantle over both shoulders, an iron-studded dark leather harness, wristbands and heavy fur boots, a giant stone-headed war maul carved with runes held diagonally across the body in both hands. No plate armour, no silver, no lightning. Commanding, shaggy and complete.",
      "Four snow giants share this body: the CHIEFTAIN is the horned, fur-mantled one holding a big rune maul across the body (silhouette: two wide horns, bulky fur shoulders, diagonal maul; hue: ice-teal skin, dark iron helm, white-grey fur; value: mid with a pale fur mantle). The plain snow giant is bald with a low maul, the thunderer is bearded with crackling fists, the boulder thrower holds a boulder. The shipped Burb wears silver plate and lightning: do NOT draw plate armour or silver.",
      "Ice-teal skin with lighter aqua highlight planes, dark iron helm, bone-white horns, white-and-grey fur, dark brown leather, grey stone maul head; nothing darker than dark brown except seams; the disc stays neutral charcoal with no teal cast." + DISC,
      'READY non-unique native-tall (snow giant chieftain)', comp=COMP + FIT + GIANT)

# ---- pack 2: minotaur and the two mountain trolls ----
MI_REF = R('minotaur-maze', 'Shipped Minotaur of the Labyrinth (dark brown fur, brown skin, axe hanging low on the left): the ordinary minotaur must not be a dark brown recolour; it is a paler tawny bull-man with black horns and the axe carried across the body.')
asset(2, 'minotaur', 'minotaur', 'minotaur.lua (giant/minotaur, non-unique, no define_as, resolvers.nice_tile with the explicit PNG in add_mos); maze, ardhungol, Arena (entity filter by name); the Summon Minotaur wild gift (talents/gifts/summon-melee.lua:365) builds an NPC of the same name/type/PNG without define_as and with a summoner: it matches the same entry (existing exact-identity behaviour, open decision reported); maulotaur and Minotaur of the Labyrinth are other names',
      [src(MI, 'name = "minotaur", color=colors.UMBER'), src(MI, 'add_mos = {{image="npc/giant_minotaur_minotaur.png"'), src('talents/gifts/summon-melee.lua', 'name = "minotaur", color=colors.UMBER')], src(MI, 'define_as = "BASE_NPC_MINOTAUR"'), None, 'giant', 'minotaur', False, True,
      'base BASE_NPC_MINOTAUR (giant/minotaur, no image=); ' + TALL_EXPLICIT.replace('<png>', 'npc/giant_minotaur_minotaur.png') + '; talents Warshout, Stunning Blow, Sunder Armour, Sunder Arms, Weapon Combat, Weapons Mastery (activated/passive); resolvers.inscriptions rune+infusion; no sustains_at_birth',
      'giant_minotaur_minotaur.png',
      [STY, IDN('giant_minotaur_minotaur.png', 'Native shape (64x128 tall): a brown bull-headed man with wide horns, bare chest, brown loincloth, a battleaxe in one hand.'), MI_REF],
      "A minotaur seen from a steep overhead three-quarter angle: a hulking hunched bull-headed man with a tawny cream-and-tan hide dappled with darker brown patches, a shaggy black mane running from the head down the shoulders, a bull head with a flat pink-grey muzzle, an iron nose ring, glaring pale eyes and two wide swept-back glossy black horns, a bare broad muscled chest crossed by a studded brown leather harness, a ragged leather loincloth, a double-bladed steel battle-axe held diagonally across the body in both hands with the blades low on the left. Snorting, brutish and complete.",
      "Giants of the maze: the shipped Minotaur of the Labyrinth is dark brown with an axe hanging on the left, and the shipped Horned Horror is a pale body with a magenta tentacle crown and lightning gauntlets. The ordinary MINOTAUR is the TAWNY CREAM bull-man with a BLACK mane and two wide black horns and a diagonal double-bladed axe (silhouette: wide horn span, black mane, diagonal axe; hue: pale tawny tan with black and steel; value: mid-light with black horns). No tentacles, no lightning, not dark brown.",
      "Tawny cream and tan hide with darker brown dapples, black mane and horns, pink-grey muzzle, brown leather harness, steel axe blades; nothing darker than the black horns and mane; the disc stays neutral charcoal." + DISC,
      'READY non-unique native-tall (minotaur; summon of same name/type/PNG matches too - open decision)', comp=COMP + FIT + GIANT)

TR_REF = R('cave-troll', 'Shipped cave troll (pale tan crouching troll with a spear), stone troll (dark grey hunched, skull belt) and forest troll (green, tusked): the mountain troll is a rust-brown warty boxer with no weapon.')
asset(2, 'mountain-troll', 'mountain troll', 'troll.lua (giant/troll, non-unique, no define_as, explicit image="npc/troll_m.png", 64x64, no nice_tile); reknor, ardhungol (entity filter by name); the boot module has an unrelated same-name leaf outside the tome module',
      [src(TR, 'name = "mountain troll", color=colors.UMBER, image="npc/troll_m.png"')], src(TR, 'define_as = "BASE_NPC_TROLL"'), None, 'giant', 'troll', False, False,
      'base BASE_NPC_TROLL (giant/troll, no image=); leaf sets image="npc/troll_m.png" explicitly, no nice_tile/add_mos/shader/anim/moddable_tile, generic actor.image==entry.image single path; talents Stun, Knockback, Rush, Disarm (activated); no sustains_at_birth; troll is not a racial-resolver body',
      'troll_m.png',
      [STY, IDN('troll_m.png', 'Native shape (64x64): a hunched dark brown troll with a bumpy stony warty hide, huge shoulders and arms hanging, small head.'), TR_REF],
      "A mountain troll seen from a steep overhead three-quarter angle: a huge athletic hunched troll with rust-brown skin covered in round stony warts and knobbly lumps like river cobbles with patches of pale green-grey lichen, thick shoulders, both big knuckled fists raised in front in a boxer's guard, a small head with small dark eyes, a heavy underbite with two blunt tusks, a ragged hide loincloth with a rope belt, no weapon. Rugged, bumpy and complete.",
      "Trolls, shipped: forest troll (green, tusks), stone troll (dark grey, skull belt), cave troll (tan with spear), Prox, Bill, Shax. The MOUNTAIN TROLL is the RUST-BROWN COBBLE-WARTED troll with two fists raised in a boxer's guard (silhouette: raised fists guard, lumpy bumpy outline; hue: warm rust-brown with pale lichen; value: mid). The mountain troll thunderer is a steel-teal warty troll casting lightning with arms flung out.",
      "Warm rust-brown skin with lighter tan wart highlights and a few pale lichen patches, brown leather loincloth, blunt bone-tan tusks; nothing darker than dark brown except mouth and seams; the disc stays neutral charcoal." + DISC,
      'READY single (mountain troll)', comp=COMP + FIT + GIANT)

asset(2, 'mountain-troll-thunderer', 'mountain troll thunderer', 'troll.lua (giant/troll, non-unique, no define_as, explicit image="npc/troll_mt.png", 64x64, no nice_tile); reknor, lightning vault (entity filter by name); rank 3, tactical ai, one random rune',
      [src(TR, 'name = "mountain troll thunderer", color=colors.AQUAMARINE, image="npc/troll_mt.png"')], src(TR, 'define_as = "BASE_NPC_TROLL"'), None, 'giant', 'troll', False, False,
      'base BASE_NPC_TROLL (giant/troll, no image=); leaf sets image="npc/troll_mt.png" explicitly, no nice_tile/add_mos/shader/anim/moddable_tile, generic actor.image==entry.image single path; talents Stun, Knockback, Lightning (activated), Thunderstorm (sustained, spells/air.lua, but the leaf has no sustains_at_birth; when used it only adds temporary values and a particle, no display write); resolvers.inscriptions(1,"rune")',
      'troll_mt.png',
      [STY, IDN('troll_mt.png', 'Native shape (64x64): a blue-teal troll with a bumpy stony hide, otherwise the mountain troll body.'), TR_REF],
      "A mountain troll thunderer seen from a steep overhead three-quarter angle: a huge hunched troll with steel-blue teal skin covered in round stony warts and knobbly lumps, both arms flung wide and up with open clawed hands, bright yellow-white and electric-blue lightning arcing from one hand to the other across the chest and shoulders, a small head with glowing pale eyes and a heavy underbite with blunt tusks, a dark grey hide loincloth, a rune-scratched stone amulet on the chest. Charged, bumpy and complete.",
      "Trolls, shipped: forest (green), stone (dark grey), cave (tan). The mountain troll thunderer is the STEEL-TEAL BLUE cobble-warted troll with ARMS FLUNG WIDE and lightning arcing between the hands (silhouette: wide open arms with zig-zag bolts, bumpy outline; hue: steel-blue teal with yellow-white and electric-blue bolts; value: mid). The mountain troll is rust-brown with fists in guard.",
      "Steel-blue teal skin with lighter aqua wart highlights, dark grey loincloth, pale bone tusks, bright yellow-white lightning with electric-blue edges; nothing darker than dark blue-grey except mouth and seams; the lightning must not glow onto or tint the disc." + DISC,
      'READY single (mountain troll thunderer)', comp=COMP + FIT + GIANT)

# ---- pack 3: four ogres ----
OGRE_BASE = 'base BASE_NPC_OGRE (giant/ogre, no image=); resolvers.racial() only adds levelup talents Ogre Wrath, Grisly Constitution, Scar-Scripted Flesh, Writ Large (races.lua, passives/one activated buff, no display write); resolvers.sustains_at_birth() present: the sustained talents are listed per leaf; '
OGRE_REF = R('cave-troll', 'Shipped cave troll (pale tan crouching troll with a spear) and stone troll: ogres here are human-shaped muscular brutes, not warty trolls, and each of the four ogres has its own clear colour and pose.')


def ogre_scope(extra):
    return 'ogre.lua (giant/ogre, non-unique, no define_as, resolvers.nice_tile{tall=1}); crypt-kryl-feijan (ogre[fn] loader) and Arena; ' + extra


asset(3, 'ogre-guard', 'ogre guard', ogre_scope('rarity 2, rank 2, greatmaul; the Elvala town ogre guards are other names'),
      [src(OG, 'name = "ogre guard", color=colors.LIGHT_GREY'), src(OG, 'resolvers.nice_tile{tall=1}', after='name = "ogre guard"'), RES], src(OG, 'define_as = "BASE_NPC_OGRE"'), None, 'giant', 'ogre', False, True,
      OGRE_BASE + 'leaf talents Sunder Armour, Weapon Combat, Weapons Mastery (activated/passive); no sustained talent besides none, so nothing is activated at birth; ' + TALL_SHORT,
      'giant_ogre_ogre_guard.png',
      [STY, IDN('giant_ogre_ogre_guard.png', 'Native shape (64x128 tall): a broad tan-skinned bare-chested ogre with dark tied hair, steel shoulder guards, blue trousers, gold-trimmed gauntlets and a big two-handed maul held up.'), OGRE_REF],
      "An ogre guard seen from a steep overhead three-quarter angle: a huge hunched muscular human-shaped ogre with warm tan skin, a heavy jaw with a small lower tusk, dark hair tied back, a bare broad chest with a steel shoulder plate on one shoulder, bright blue cloth trousers with a rope belt, heavy brown boots, gold-trimmed steel gauntlets, and a big two-handed steel-headed maul held diagonally across the body in both hands. Sturdy, disciplined and complete.",
      "Four ogres share this body: the GUARD is the TAN-skinned soldier in BLUE trousers and a steel shoulder plate carrying a big maul diagonally (silhouette: diagonal maul, one plated shoulder; hue: warm tan skin with bright blue trousers and steel; value: mid-light). The mauler is red-skinned and maul-less, the rune-spinner is orange with glowing runes and fire, the pounder is a blue-skinned unarmed grappler with arms spread.",
      "Warm tan skin with lighter peach highlight planes, bright blue trousers, brown boots and belt, steel and gold-trimmed gauntlets; nothing darker than dark brown except the boots and seams; the disc stays neutral charcoal." + DISC,
      'READY non-unique native-tall shorthand (ogre guard)', comp=COMP + FIT + GIANT)

asset(3, 'ogre-mauler', 'ogre mauler', ogre_scope('rarity 2, rank 2, greatmaul; Warshout Berserker'),
      [src(OG, 'name = "ogre mauler", color=colors.LIGHT_UMBER'), src(OG, 'resolvers.nice_tile{tall=1}', after='name = "ogre mauler"'), RES], src(OG, 'define_as = "BASE_NPC_OGRE"'), None, 'giant', 'ogre', False, True,
      OGRE_BASE + 'leaf talents Warshout Berserker, Weapon Combat, Weapons Mastery (activated/passive); no sustained talent, so nothing is activated at birth; ' + TALL_SHORT,
      'giant_ogre_ogre_mauler.png',
      [STY, IDN('giant_ogre_ogre_mauler.png', 'Native shape (64x128 tall): a crouching red-brown muscular ogre with clenched fists, a gold-gauntleted hand raised, wild hair.'), OGRE_REF],
      "An ogre mauler seen from a steep overhead three-quarter angle: a huge hunched furious muscular human-shaped ogre with brick-red skin and lighter orange highlights, a snarling open mouth with two lower tusks, wild dark red hair, bare chest and back covered in old scars, a ragged brown loincloth, one massive clenched fist thrust forward wearing a gold-plated gauntlet and the other arm hanging low with the fist clenched, no weapon. Enraged, brutal and complete.",
      "Four ogres share this body: the MAULER is the BRICK-RED enraged brute with one GOLD-GAUNTLET FIST thrust forward and no weapon (silhouette: crouched wide with one big fist forward; hue: brick red with gold; value: mid). The guard is tan with blue trousers and a maul, the rune-spinner is orange with runes and fire, the pounder is a blue grappler with arms spread wide.",
      "Brick-red skin with lighter orange highlight planes, dark red hair, gold gauntlet, brown loincloth; nothing darker than dark red-brown except the mouth and seams; the disc stays neutral charcoal with no red cast." + DISC,
      'READY non-unique native-tall shorthand (ogre mauler)', comp=COMP + FIT + GIANT)

asset(3, 'ogre-rune-spinner', 'ogre rune-spinner', ogre_scope('rarity 2, rank 3, female, staff; the Elvala town leaf of the SAME name (zones/town-elvala/npcs.lua:106, base BASE_NPC_ELVALA_OGRE_TOWN, also {tall=1}, no define_as) resolves to the same name/type/subtype/PNG/tall body and matches this entry (open decision reported)'),
      [src(OG, 'name = "ogre rune-spinner", color=colors.LIGHT_RED'), src(OG, 'resolvers.nice_tile{tall=1}', after='name = "ogre rune-spinner"'), src('zones/town-elvala/npcs.lua', 'name = "ogre rune-spinner", color=colors.LIGHT_UMBER'), RES], src(OG, 'define_as = "BASE_NPC_OGRE"'), None, 'giant', 'ogre', False, True,
      OGRE_BASE + 'leaf talents Staff Mastery (passive), Lightning, Flame, Earthen Missiles, Barrier (all activated; Barrier is celestial/light.lua, a shield, not a sustain); no sustained talent, so nothing is activated at birth; ' + TALL_SHORT,
      'giant_ogre_ogre_rune_spinner.png',
      [STY, IDN('giant_ogre_ogre_rune_spinner.png', 'Native shape (64x128 tall): a tall female ogre with orange-red skin covered in glowing runes, raising both hands with a swirl of orange flame above her head.'), OGRE_REF],
      "An ogre rune-spinner seen from a steep overhead three-quarter angle: a huge hunched female ogre with warm orange-red skin covered in glowing gold arcane runes and spiral marks, long swept-back dark hair, a strong jaw with small tusks, a short bright cloth wrap and sash, one hand gripping a short thick runed wooden staff and the other hand raised with a small compact swirl of bright orange fire and a curl of yellow-white lightning above the palm. Arcane, glowing and complete.",
      "Four ogres share this body: the RUNE-SPINNER is the ORANGE female covered in GLOWING GOLD RUNES with a small fire swirl above one raised hand (silhouette: one arm up with a flame curl, a short staff; hue: orange with gold runes and yellow-white fire; value: mid-light). The mauler is brick-red with a gold fist, the guard tan with blue trousers, the pounder blue.",
      "Warm orange-red skin with gold runes and lighter highlight planes, dark hair, bright orange fire and yellow-white spark, pale cloth wrap; nothing darker than dark brown except hair and seams; the fire and runes must not glow onto or tint the disc." + DISC,
      'READY non-unique native-tall shorthand (ogre rune-spinner; Elvala leaf of the same name also matches - open decision)', comp=COMP + FIT + GIANT)

asset(3, 'ogre-pounder', 'ogre pounder', ogre_scope('rarity 3, rank 3, unarmed (Double Strike, Uppercut, Clinch, Maim)'),
      [src(OG, 'name = "ogre pounder", color=colors.DARK_UMBER'), src(OG, 'resolvers.nice_tile{tall=1}', after='name = "ogre pounder"'), RES], src(OG, 'define_as = "BASE_NPC_OGRE"'), None, 'giant', 'ogre', False, True,
      OGRE_BASE + 'leaf talents Double Strike, Uppercut, Empty Hand (passive), Clinch, Maim, Unarmed Mastery (passive), Weapon Combat (passive); no sustained talent, so nothing is activated at birth; ' + TALL_SHORT,
      'giant_ogre_ogre_pounder.png',
      [STY, IDN('giant_ogre_ogre_pounder.png', 'Native shape (64x128 tall): a crouched blue-skinned muscular ogre with both arms spread wide, black shorts, grimacing.'), OGRE_REF],
      "An ogre pounder seen from a steep overhead three-quarter angle: a huge crouched muscular human-shaped ogre with smooth bright cornflower-blue skin and lighter periwinkle highlights, a grimacing wide mouth with two lower tusks, a shaved head, both massive arms spread WIDE open with big hands ready to crush in a hug, fingerless dark leather grappling gauntlets, black shorts with a rope belt, wide-planted bent legs, no weapon. Grappling, powerful and complete.",
      "Four ogres share this body: the POUNDER is the BLUE-skinned bald grappler crouched with BOTH ARMS SPREAD WIDE (silhouette: wide open arms, low crouch; hue: bright cornflower blue with black shorts; value: mid). The guard is tan with a maul, the mauler brick-red with one gold fist, the rune-spinner orange with fire. The shipped mountain troll thunderer is a warty teal troll with lightning; the pounder is smooth-skinned with no lightning.",
      "Bright cornflower-blue skin with lighter periwinkle highlight planes, black shorts, dark brown leather gauntlets, pale bone tusks; nothing darker than black shorts and seams; the disc stays neutral charcoal with no blue cast." + DISC,
      'READY non-unique native-tall shorthand (ogre pounder)', comp=COMP + FIT + GIANT)

# ---- pack 4: Healer Astelrid ----
asset(4, 'healer-astelrid', 'Healer Astelrid', 'conclave-vault (boss room, zones/conclave-vault/npcs.lua:140; base BASE_NPC_OGRE, unique, define_as HEALER_ASTELRID, resolvers.nice_tile{tall=1}); single definition, female, rank 4',
      [src(CV, 'define_as = "HEALER_ASTELRID"'), src(CV, 'resolvers.nice_tile{tall=1}', after='define_as = "HEALER_ASTELRID"'), RES], src(OG, 'define_as = "BASE_NPC_OGRE"'), 'HEALER_ASTELRID', 'giant', 'ogre', True, False,
      OGRE_BASE + 'talents Heal, Arcane Shield (sustained, spells/aegis.lua), Aegis, Earthquake, Rush, Stunning Blow, Living Lightning (sustained, spells/energy-alchemy.lua); the two sustains start at birth and only add a damage shield, temporary values and particles (no type/subtype/image/add_mos/shader write); unique with define_as, so an ordinary unique native-tall entry like Kyless; ' + TALL_SHORT,
      'giant_ogre_healer_astelrid.png',
      [STY, IDN('giant_ogre_healer_astelrid.png', 'Native shape (64x128 tall): a huge female ogre in tattered dark violet healer robes with long dark hair, an officer badge, and a spiked club-staff wrapped with plaster and scalpels.'), OGRE_REF],
      "Healer Astelrid seen from a steep overhead three-quarter angle: an enormous hunched female ogre with pale grey-pink stitched skin and long dark hair partly tied up, a strong jaw with small tusks, wearing a wide tattered dark violet healer's robe with a lighter lavender collar and sleeves and a bright brass officer's badge on the chest, a white apron smeared with faint stains, her two big hands gripping a thick spiked club that is a healer's staff wrapped in white plaster bandages with a fan of steel scalpels bristling from its head, held diagonally across the body. Clinical, imposing and complete.",
      "Ogres share this body: ASTELRID is the only one in a WIDE VIOLET ROBE with a white apron and a plaster-and-scalpel club (silhouette: broad robe skirt, diagonal bristling club; hue: dark violet and lavender with white bandages and brass; value: mid). The ordinary ogres are bare-chested in tan/red/orange/blue and carry no robe.",
      "Pale grey-pink skin, dark violet robe with lavender trim, white bandages and apron, brass badge, steel scalpels; nothing darker than dark violet and dark hair; the disc stays neutral charcoal with no violet cast." + DISC,
      'READY unique native-tall shorthand (Healer Astelrid, HEALER_ASTELRID)', comp=COMP + FIT + GIANT)


def retry(id_, pack, **changes):
    base = next(a for a in A if a['id'] == id_)
    A.append(dict(base, pack=pack, **changes))


# ---- retry packs are appended below by later edits of retries.py ----
exec((HERE / 'retries.py').read_text()) if (HERE / 'retries.py').exists() else None

EXPLICIT_IDS = ()
PNGF = {i: 'explicit nice_tile add_mos PNG' for i in ('snow-giant', 'snow-giant-thunderer', 'snow-giant-boulder-thrower', 'snow-giant-chieftain', 'minotaur')}
PNGF.update({'mountain-troll': 'explicit image="npc/troll_m.png" on the leaf', 'mountain-troll-thunderer': 'explicit image="npc/troll_mt.png" on the leaf'})
PNGF.update({i: 'NPC.lua:33 default-name image via resolvers.nice_tile{tall=1} (live-confirmed shorthand)' for i in ('ogre-guard', 'ogre-mauler', 'ogre-rune-spinner', 'ogre-pounder', 'healer-astelrid')})


def build():
    packs = {}
    identities = []
    render = 'game/addons/tome-checker-revised/evidence/monster-batch-p-20260929/source-contracts.json'
    seen = set()
    from PIL import Image
    for a in A:
        if a['id'] in seen:
            continue
        seen.add(a['id'])
        native_rel = NPC + a['native']
        ident = {'id': a['id'], 'native_name': a['name'], 'source': a['srcs'][0], 'define_as': a['define_as'],
                 'type': a['type'], 'subtype': a['subtype'], 'unique': a['unique'], 'native_tall': a['native_tall'],
                 'image_source': PNGF[a['id']],
                 'structure': a['structure'], 'native_image': 'npc/' + a['native'], 'native_image_path': native_rel,
                 'native_image_sha256': sha(native_rel), 'native_image_size': None, 'verdict': a['verdict']}
        with Image.open(WS / native_rel) as im:
            ident['native_image_size'] = list(im.size)
        if a['base']:
            ident['base_source'] = a['base']
        if len(a['srcs']) > 1:
            ident['extra_sources'] = a['srcs'][1:]
        identities.append(ident)
    ev = {'schema': 1,
          'task': "monster-batch-p: static re-verification (no game launch) of the twelve batch-7 identities of the second gap survey (snow giant, minotaur, snow giant thunderer, Healer Astelrid, mountain troll, snow giant boulder thrower, mountain troll thunderer, snow giant chieftain, ogre guard, ogre mauler, ogre rune-spinner, ogre pounder) against game/modules/tome source and native sprites. Survey verdicts were not trusted; every field below was read from source: name, type/subtype, define_as, explicit or NPC.lua:33 default image, unique, PNG on disk, and absence of moddable_tile/shader/anim/add_displays. The survey listed the two mountain trolls as 'default-name single image'; they carry an explicit image= (troll_m.png, troll_mt.png), 64x64, and are plain single entries.",
          'new_ids_not_in_catalog_before_this_batch': [i['id'] for i in identities], 'identities': identities,
          'runtime_mutation_scan': {
              'method': 'every talent of each identity (resolvers.talents, inherited base talents, resolvers.racial levelup talents) was resolved to its definition under game/modules/tome/data/talents and checked for mode="sustained" and for writes to self.type/subtype/image/name/display, __old_type, replace_display, add_mos, add_displays, moddable_tile, shader, textures, anim; the resolvers sustains_at_birth, racial, nice_tile, inscriptions and the base-file talent lists were read. Only the ogre body carries sustains_at_birth (BASE_NPC_OGRE); the only sustained talents on any identity are Arcane Shield and Living Lightning (Healer Astelrid, started at birth) and Thunderstorm (mountain troll thunderer, no sustains_at_birth). Text hits: Warshout/Warshout Berserker read self.subtype only to pick a log message.',
              'writers_found': [],
              'sustains_at_birth_review': [
                  {'identity': 'Healer Astelrid', 'sustained': ['Arcane Shield (talents/spells/aegis.lua)', 'Living Lightning (talents/spells/energy-alchemy.lua)'], 'note': 'damage shield, temporary values and particles only; no type/subtype/image/add_mos/shader write'},
                  {'identity': 'ogre guard, ogre mauler, ogre rune-spinner, ogre pounder', 'sustained': [], 'note': 'resolvers.sustains_at_birth() present on BASE_NPC_OGRE but none of their talents (nor the racial talents Ogre Wrath, Grisly Constitution, Scar-Scripted Flesh, Writ Large) is sustained'},
                  {'identity': 'mountain troll thunderer', 'sustained': [], 'note': 'Thunderstorm (spells/air.lua) is sustained but the leaf has no sustains_at_birth; if the tactical AI uses it it adds temporary values and a particle, no display write'},
                  {'identity': 'snow giants, minotaur, mountain troll', 'sustained': [], 'note': 'no sustains_at_birth and no sustained talent'}],
              'visibility_review': 'no identity of this batch has stealth, invisibility or a phase talent that changes display; random runes/infusions are inscription resolvers (no display write)',
              'hits_in_batch': [],
              'no_hit': [i['native_name'] for i in identities]},
          'name_collisions_checked': [
              {'name': 'minotaur', 'other_definitions': ['talents/gifts/summon-melee.lua:365 (Summon Minotaur wild gift): same name "minotaur", type giant/minotaur, same explicit tall PNG npc/giant_minotaur_minotaur.png, no define_as, summoner set, autolevel none; renamed "minotaur (wild summon)" on a wild-summon proc', 'maulotaur (own name/PNG), Minotaur of the Labyrinth (MINOTAUR_MAZE, shipped, own PNG)'], 'outcome': 'the summon has the same name, body and art, so the existing exact-identity check maps it like the zone minotaur (as the Necromancer minions of batch N); the "(wild summon)" rename stays native. NOT a decision on summons/minions: reported to the user as an open question; no name+define_as key extension'},
              {'name': 'ogre rune-spinner', 'other_definitions': ['zones/town-elvala/npcs.lua:106 (Elvala town guard leaf, base BASE_NPC_ELVALA_OGRE_TOWN): same name, giant/ogre, {tall=1} so the same default-name PNG and tall body, no define_as, non-unique, level 1 town NPC with other stats'], 'outcome': 'indistinguishable from the general leaf by every exact check (name, type, subtype, define_as, image body); it therefore wears the same token as the zone ogre. Not a summon, but the same category of same-name-different-definition case: reported as an open question, nothing keyed on the base name'},
              {'name': 'mountain troll / mountain troll thunderer', 'other_definitions': ['game/engines/default/modules/boot/data/general/npcs/troll.lua (boot module demo leaves, not loaded by the tome module)'], 'outcome': 'not reachable in the tome module; siblings cannot borrow each other\'s or another troll\'s PNG (negative tests)'},
              {'name': 'snow giant family', 'other_definitions': ['Burb the snow giant champion (BURB_SNOW_GIANT, shipped batch A, unique, own PNG); chieftain and Burb make_escort of three giant/ice bodies with their own names; vault tiles (snow-giant-camp, lightning-vault, perilous-cliffs) and the antimagic quest only filter by name'], 'outcome': 'exact names; the four ordinary giants cannot wear each other\'s or Burb\'s tall body (negative tests)'},
              {'name': 'Healer Astelrid', 'other_definitions': ['single definition (conclave-vault boss room); the lore book only prints the name'], 'outcome': 'bound to define_as HEALER_ASTELRID and unique'},
              {'name': 'ogre guard / ogre mauler / ogre pounder', 'other_definitions': ['single definitions in ogre.lua; Arena.lua filters by name only'], 'outcome': 'exact catalog entries; siblings cannot borrow each other\'s tall body'}],
          'kept_native': [],
          'neighbours_kept_native': [
              {'name': 'ogre warmaster, degenerated ogric mass, ogric abomination, ogre sentry', 'reason': 'not in the surveyed batch (later batch / NEEDS)'},
              {'name': 'maulotaur', 'reason': 'not in the surveyed batch'},
              {'name': 'minotaur (wild summon)', 'reason': 'renamed by the wild-summon proc; exact name differs'}]}
    out = ADDON / 'evidence/monster-batch-p-20260929/source-contracts.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(ev, indent=2, ensure_ascii=False) + '\n')
    evsha = hashlib.sha256(out.read_bytes()).hexdigest()
    for a in A:
        refs = [{'path': p, 'sha256': sha(p), 'role': r, 'note': n} for r, p, n in a['refs']]
        entry = {'asset_id': a['id'], 'native_name': a['name'], 'scope': a['scope'], 'sources': a['srcs'], 'references': refs,
                 'contrast_dimensions': list(a['dims']),
                 'prompt_fields': {'subject': a['subject'], 'contrast': a['contrast'], 'composition': a['comp'] or COMP, 'palette': a['palette']},
                 'kind': 'creature', 'max_attempts': 1, 'gate': 'ready',
                 'gate_reason': f"Exact source identity re-verified directly against game/modules/tome source (name={a['name']}, define_as={a['define_as']}, type={a['type']}/subtype={a['subtype']}, unique={a['unique']}); details and hashes in evidence/monster-batch-p-20260929/source-contracts.json. {a['structure']}. Exact catalog entry only, never a whole-subtype mapping.",
                 'render_evidence': [{'path': render, 'sha256': evsha}]}
        packs.setdefault(a['pack'], []).append(entry)
    for n, assets in packs.items():
        p = ADDON / f'art/production/batches/monster-batch-p-{n}.json'
        if p.exists():
            print('exists, skipped', p.name)
            continue
        p.write_text(json.dumps({'schema': 1, 'batch_id': f'monster-batch-p-{n}', 'assets': assets}, indent=2, ensure_ascii=False) + '\n')
        print('wrote', p.name)


if __name__ == '__main__':
    build()
