"""Generate the monster-batch-o task packs and the pinned source-contract
evidence (survey-2 section 7, batch 6: white ooze, gigantic corrosive tunneler,
gigantic gravity worm, slimy ooze, poison ooze, carrion worm mass, brittle clear
ooze, cute little bunny, dredgling, onilug, wretchling, brecklorn). Pure
bookkeeping: hashes native sources/sprites, writes JSON. Retry packs are
appended by later edits of retries.py (never overwritten)."""
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
FIT = " The ENTIRE creature, every limb, tail, wing, drip, staff and effect included, fits inside a circle of about three quarters of the disc radius around the disc centre, leaving a wide bare charcoal ring of base plate on every side, yet the creature is large and bold inside that circle."
DISC = " Dry neutral charcoal disc with restrained copper-grey bevel, kept a visibly lighter value than the creature's darkest parts so the two never merge."
A = []


def asset(pack, id_, name, scope, srcs, base, define_as, typ, sub, unique, native_tall, structure, native, refs, subject,
          contrast, palette, verdict, dims=('silhouette', 'value'), comp=None):
    A.append(dict(comp=comp, pack=pack, id=id_, name=name, scope=scope, srcs=srcs, base=base, define_as=define_as, type=typ,
                  subtype=sub, unique=unique, native_tall=native_tall, structure=structure, native=native, refs=refs,
                  subject=subject, contrast=contrast, palette=palette, verdict=verdict, dims=dims))


STY = ('style', STYLE, 'Approved disc, lighting and camera; do not copy its creature.')
DEFAULT_EL = 'no image=/nice_tile/add_mos/shader/anim/moddable_tile/tint on the leaf or its base; generic actor.image==entry.image single path; NPC.lua:33 default-name image'
TALL = ('resolvers.nice_tile{image="invis.png", add_mos={{image="<png>", display_h=2, display_y=-1}}} names the PNG explicitly (no {tall=1} shorthand and no =BASE=TILE= indirection), '
        'so the resolved tall body is statically pinnable (same form as the batch K gigantic sandworm tunneler and batch M gwelgoroth entries); native sprite 64x128')
OO = 'general/npcs/ooze.lua'
SW = 'general/npcs/sandworm.lua'
VE = 'general/npcs/vermin.lua'
OF = 'zones/old-forest/npcs.lua'
RO = 'general/npcs/rodent.lua'
HT = 'general/npcs/horror_temporal.lua'
HC = 'general/npcs/horror-corrupted.lua'
MD = 'general/npcs/minor-demon.lua'


def R(family_id, note):
    return ('family', TOK + family_id + '.png', note)


def IDN(png, note):
    return ('identity', NPC + png, note)


OOZE_SCOPE = 'ooze.lua loader (vermin/oozes, default-name image, non-unique, no define_as, no nice_tile); '
OOZE_BASE = 'base BASE_NPC_OOZE (vermin/oozes, no image=); ' + DEFAULT_EL

# ---- pack 1: white ooze ----
asset(1, 'white-ooze', 'white ooze', OOZE_SCOPE + 'sandworm-lair, conclave-vault, Arena (entity filter by name only); clone_on_hit is absent, the leaf is a plain blob',
      [src(OO, 'name = "white ooze", color=colors.WHITE')], src(OO, 'define_as = "BASE_NPC_OOZE"'), None, 'vermin', 'oozes', False, False,
      OOZE_BASE + ' gives vermin_oozes_white_ooze.png (64x64); no talents, no sustains_at_birth',
      'vermin_oozes_white_ooze.png',
      [STY, IDN('vermin_oozes_white_ooze.png', 'Native shape: a low flat puddle of milky white slime with a lumpy top, two small detached drops beside it.'),
       R('white-jelly', 'Shipped white jelly (a tall domed bright-white cloud-shaped mound): the white ooze is a LOW WIDE flat puddle with a rippled edge, not a domed mound.')],
      "A white ooze seen from a steep overhead three-quarter angle: a low wide flat puddle of glossy milky-white slime, with a rippled scalloped edge, a few small bubbles on its glossy surface, faint pearl-blue shadows in the folds and bright white highlights along the upper-left of each lump, three small round drops detached beside the puddle. No eyes, no face. Wet, simple and complete.",
      "Ooze family, shipped black/yellow/red/blue/green/crimson oozes and the white jelly: the white ooze is the LOW FLAT scalloped puddle with three detached drops (silhouette: wide flat scalloped puddle, three separate drops; hue: milky white with pearl-blue shade; value: very light). The white jelly is a tall domed mound; do not draw a dome.",
      "Milky white slime with pearl-blue and pale-lavender shade planes, bright white highlights; nothing darker than a light mid-grey-blue; the disc stays neutral charcoal and receives no glow or white cast." + DISC,
      'READY single (white ooze)', ('silhouette', 'value'))

# ---- pack 2: slimy ooze, poison ooze, brittle clear ooze ----
asset(2, 'slimy-ooze', 'slimy ooze', OOZE_SCOPE + 'conclave-vault, ardhungol (rank 2, clone_on_hit, Slime Spit); no define_as',
      [src(OO, 'name = "slimy ooze", color=colors.GREEN')], src(OO, 'define_as = "BASE_NPC_OOZE"'), None, 'vermin', 'oozes', False, False,
      OOZE_BASE + ' gives vermin_oozes_slimy_ooze.png (64x64); talents: Slime Spit (activated gift, gifts/slime.lua); no sustains_at_birth; clone_on_hit clones keep the same name/image',
      'vermin_oozes_slimy_ooze.png',
      [STY, IDN('vermin_oozes_slimy_ooze.png', 'Native shape: two stringy diagonal streaks of yellow-green slime with ragged fuzzy edges.'),
       R('green-ooze', 'Shipped green ooze (flat bright-green puddle with three round drops): the slimy ooze is NOT a puddle; it is stringy diagonal ropes of lime-yellow slime.')],
      "A slimy ooze seen from a steep overhead three-quarter angle: a knot of thick glistening ropes and strands of lime-yellow-green slime, two long diagonal ropes twisting around each other with drooping stringy tendrils and long sticky threads hanging off, small bright yellow highlights and translucent pale-lime sheen, a few flying slime flecks. No eyes, no face. Stringy, sticky and complete.",
      "Ooze family: the shipped green ooze is a flat rounded puddle with round drops, the shipped yellow ooze a flame-shaped splash. The slimy ooze is the STRINGY ROPE-KNOT of lime-yellow slime with drooping threads (silhouette: crossed diagonal ropes with long strings; hue: lime-yellow green; value: light).",
      "Bright lime and yellow-green slime with translucent pale-lime sheen and bright yellow highlights, darker olive only in small gaps; the slime must not cast green light or a green cast onto the disc." + DISC,
      'READY single (slimy ooze)', ('silhouette', 'value', 'hue'))

asset(2, 'poison-ooze', 'poison ooze', OOZE_SCOPE + 'conclave-vault, ardhungol (rank 2, clone_on_hit, Poisonous Spores); no define_as',
      [src(OO, 'name = "poison ooze", color=colors.LIGHT_GREEN')], src(OO, 'define_as = "BASE_NPC_OOZE"'), None, 'vermin', 'oozes', False, False,
      OOZE_BASE + ' gives vermin_oozes_poison_ooze.png (64x64); talents: Poisonous Spores (activated gift, gifts/slime.lua); no sustains_at_birth',
      'vermin_oozes_poison_ooze.png',
      [STY, IDN('vermin_oozes_poison_ooze.png', 'Native shape: a glossy violet blob with a lumpy top and two detached drops.'),
       R('crimson-ooze', 'Shipped crimson ooze (upright raspberry wave with drips): the poison ooze is a low rounded mound with mushroom-like spore caps growing out of it, not an upright wave.')],
      "A poison ooze seen from a steep overhead three-quarter angle: a low rounded glossy mound of bright violet-magenta slime, several small pale-yellow spore puffs and little lilac mushroom-like caps growing out of its top with tiny spore dots drifting off, wet violet highlights on the upper-left, a bubble or two, a couple of small drops at its base. No eyes, no face. Toxic, glossy and complete.",
      "Ooze family: the shipped crimson ooze is an upright dripping wave, the blue ooze a jagged splash, the green ooze a flat puddle. The poison ooze is the ROUND MOUND of bright violet slime studded with little spore caps and drifting yellow spores (silhouette: round mound with several small caps; hue: violet-magenta with pale yellow; value: mid-light).",
      "Bright violet-magenta slime with lighter lilac highlight planes and pale-yellow spore puffs; the darkest tone is a mid purple in small creases; no glow or purple cast on the disc." + DISC,
      'READY single (poison ooze)', ('silhouette', 'value', 'hue'))

asset(2, 'brittle-clear-ooze', 'brittle clear ooze', OOZE_SCOPE + 'conclave-vault (rank 2, rarity 10, clone_on_hit); no define_as',
      [src(OO, 'name = "brittle clear ooze", color=colors.WHITE')], src(OO, 'define_as = "BASE_NPC_OOZE"'), None, 'vermin', 'oozes', False, False,
      OOZE_BASE + ' gives vermin_oozes_brittle_clear_ooze.png (64x64); no talents, no sustains_at_birth',
      'vermin_oozes_brittle_clear_ooze.png',
      [STY, IDN('vermin_oozes_brittle_clear_ooze.png', 'Native shape: a translucent grey-blue blob, flat topped, with faint highlights and two drops.'),
       R('white-jelly', 'Shipped white jelly (opaque white cloud mound): the brittle clear ooze is TRANSLUCENT glass-like ice-blue with sharp cracks, not opaque white.')],
      "A brittle clear ooze seen from a steep overhead three-quarter angle: a low faceted lump of translucent glass-like pale ice-blue and pale-cyan jelly with sharp angular cracks running through it, several shattered shard-like fragments broken off around its edge, bright white glints on the upper-left facets and a clear pale-teal see-through look. No eyes, no face. Brittle, crystalline and complete.",
      "Ooze family and white things: the white ooze is a soft opaque milky puddle with round drops and the white jelly an opaque dome. The brittle clear ooze is the ANGULAR CRACKED glass lump with sharp shards (silhouette: faceted with pointed shards, no round drops; hue: pale ice-cyan and teal; value: light).",
      "Pale ice-cyan and teal translucent glass with bright white glints and slightly darker teal crack lines; nothing darker than mid tone; the disc stays neutral charcoal with no cyan cast." + DISC,
      'READY single (brittle clear ooze)', ('silhouette', 'value', 'hue'))

# ---- pack 3: gigantic worms ----
TALL_REF = ('family', TOK + 'gigantic-sandworm-tunneler.png', 'Shipped gigantic sandworm tunneler (olive-sand worm with a four-petal mouth on a sand heap): do NOT reuse its olive colour, sand heap or petal flower.')
asset(3, 'gigantic-corrosive-tunneler', 'gigantic corrosive tunneler', 'briagh-lair, sandworm-lair (sandworm.lua, vermin/sandworm, non-unique, no define_as, nice_tile with the explicit PNG vermin_sandworm_gigantic_corrosive_tunneler.png); batch K kept it native and shipped only the sibling gigantic sandworm tunneler',
      [src(SW, 'name = "gigantic corrosive tunneler", color=colors.GREEN'), src(SW, 'add_mos = {{image="npc/vermin_sandworm_gigantic_corrosive_tunneler.png"')], src(SW, 'define_as = "BASE_NPC_SANDWORM"'), None, 'vermin', 'sandworm', False, True,
      'base BASE_NPC_SANDWORM (vermin/sandworm, no image=); ' + TALL.replace('<png>', 'npc/vermin_sandworm_gigantic_corrosive_tunneler.png') + '; talents Acid Blood (passive), Rush and Grab (activated); no sustains_at_birth; on_die adds a map effect only',
      'vermin_sandworm_gigantic_corrosive_tunneler.png',
      [STY, IDN('vermin_sandworm_gigantic_corrosive_tunneler.png', 'Native shape (64x128 tall): a dark green-grey scaled worm body rising and curving up, with a coral four-petal mouth on top and yellow acid dripping down.'),
       TALL_REF],
      "A gigantic corrosive tunneler seen from a steep overhead three-quarter angle: a thick segmented worm of vivid acid lime-green scales with pale yellow-green belly bands, coiled into a low S-shape and lifting its front third up, the head an open round toothy maw ringed with pale jagged fangs and glistening yellow-green acid, thick glowing yellow acid drooling down onto a small bubbling puddle of yellow-green acid at its base with a couple of scorched pebbles. No flower petals, no sand heap. Corrosive, heavy and complete.",
      "Sandworm family, shipped: sandworm (slim orange S-curve), destroyer (closed armoured brown ring), burrower (olive arches over a sand heap), gigantic sandworm tunneler (olive worm with petal mouth on sand), queen. The corrosive tunneler is the LIME-GREEN S-coil with a round fanged maw dripping into an acid puddle (silhouette: S-coil with raised round-mouthed head and a puddle; hue: vivid acid lime-green with yellow; value: mid-light).",
      "Vivid acid lime-green scales with pale yellow-green belly bands and bright yellow acid; nothing darker than mid green except small scale seams; the acid must not cast green light or a green cast onto the disc, which stays neutral charcoal." + DISC,
      'READY non-unique native-tall (gigantic corrosive tunneler; K kept native, O maps)', ('silhouette', 'value', 'hue'), comp=COMP + FIT)

asset(3, 'gigantic-gravity-worm', 'gigantic gravity worm', 'briagh-lair, sandworm-lair (sandworm.lua, vermin/sandworm, non-unique, no define_as, nice_tile with the explicit PNG vermin_sandworm_gigantic_gravity_worm.png); batch K kept it native',
      [src(SW, 'name = "gigantic gravity worm", color=colors.UMBER'), src(SW, 'add_mos = {{image="npc/vermin_sandworm_gigantic_gravity_worm.png"')], src(SW, 'define_as = "BASE_NPC_SANDWORM"'), None, 'vermin', 'sandworm', False, True,
      'base BASE_NPC_SANDWORM (vermin/sandworm, no image=); ' + TALL.replace('<png>', 'npc/vermin_sandworm_gigantic_gravity_worm.png') + '; talents Gravity Well, Gravity Spike (activated), Gravity Locus (sustained, chronomancy/gravity.lua, but the leaf has no sustains_at_birth; when used it adds a temporary value and a particle, no display write), Rush, Grab',
      'vermin_sandworm_gigantic_gravity_worm.png',
      [STY, IDN('vermin_sandworm_gigantic_gravity_worm.png', 'Native shape (64x128 tall): a slate-grey scaled worm rising up with a coral four-petal mouth and blue lightning crackling around it.'),
       TALL_REF],
      "A gigantic gravity worm seen from a steep overhead three-quarter angle: a thick segmented worm of cool slate blue-grey scales with pale silver belly bands, coiled into a tight round spiral like a wound rope with its head raised in the middle, the head a small blunt mouth with a ring of coral-pink petal lobes, a ring of pale grey pebbles and small stones floating in orbit around its raised head, a few thin pale-blue arcs of energy between the pebbles. No sand heap, no acid. Weighty, bending space and complete.",
      "Sandworm family, shipped: sandworm (slim orange S-curve), destroyer (closed armoured brown ring), burrower (olive arches over sand), gigantic sandworm tunneler (olive petal-mouthed worm on sand). The gravity worm is the SLATE BLUE-GREY TIGHT SPIRAL with orbiting pebbles round a raised head (silhouette: round wound coil with a ring of floating stones; hue: cool slate blue-grey with pale silver; value: mid-light). The corrosive tunneler is a green S-coil; do not draw green.",
      "Cool slate blue-grey scales with pale silver bands, coral-pink petals, pale grey pebbles, pale-blue arcs; nothing darker than mid tone except scale seams; the arcs must not glow onto or tint the disc." + DISC,
      'READY non-unique native-tall (gigantic gravity worm; K kept native, O maps)', ('silhouette', 'value', 'hue'), comp=COMP + FIT)

# ---- pack 4: carrion worm mass, bunny, dredgling ----
asset(4, 'carrion-worm-mass', 'carrion worm mass', 'mark-spellblaze, ancient-elven-ruins, worms vault (vermin/worms, default-name image, non-unique, define_as CARRION_WORM_MASS); the Corruptions Worm Rot / Infestation summon (talents/corruptions/rot.lua:62) has the same name, type, subtype and explicit PNG but NO define_as and a summoner: it is rejected by the define_as binding and stays native (open decision reported, see evidence)',
      [src(VE, 'define_as = "CARRION_WORM_MASS"'), src('talents/corruptions/rot.lua', 'name = "carrion worm mass", faction = self.faction')], src(VE, 'define_as = "BASE_NPC_WORM"'), 'CARRION_WORM_MASS', 'vermin', 'worms', False, False,
      'base BASE_NPC_WORM (vermin/worms, no image=); leaf ' + DEFAULT_EL + ' gives vermin_worms_carrion_worm_mass.png (64x64); can_multiply clones keep define_as; talents Crawl Acid, Rotting Disease, Multiply (activated, no sustain); on_die adds a blight map effect only',
      'vermin_worms_carrion_worm_mass.png',
      [STY, IDN('vermin_worms_carrion_worm_mass.png', 'Native shape: two thick pale grey-white ringed worms curling up, each with a small dark bitten mouth.'),
       R('white-worm-mass', 'Shipped white worm mass (a cream cluster of many small worms) and green worm mass (many thin olive worms): the carrion worm mass is FEW FAT dirty worms, not a cluster of many.')],
      "A carrion worm mass seen from a steep overhead three-quarter angle: three fat segmented worms of sallow tan-brown and dirty pink-grey flesh, ringed with darker sand-brown bands, entwined in a sprawling heap with two heads raised and open showing small sharp pale teeth, glistening wet sores and pale-green rot patches on the bodies, a small wisp of pale green gas rising at one side. Rotting, fat and complete.",
      "Worm family, shipped: white worm mass (cream cluster of many small worms) and green worm mass (many thin olive worms), plus the sandworms. The carrion worm mass is FEW FAT worms in a heap with two raised toothy heads (silhouette: three thick bodies, two raised heads; hue: sallow tan-brown and dirty pink with pale-green rot; value: mid-light).",
      "Sallow tan-brown and dirty pink-grey worm flesh with lighter sand bands, pale sickly green rot patches and pale teeth; nothing darker than mid tone except small seams and mouths; the gas must not cast green light onto the disc." + DISC,
      'READY define_as-bound (carrion worm mass)', ('silhouette', 'value', 'hue'), comp=COMP + FIT)

asset(4, 'cute-little-bunny', 'cute little bunny', 'old-forest (vermin/rodent, default-name image, non-unique, no define_as, no nice_tile; rarity 200; allow_infinite_dungeon); the Old Forest rabbit is a single definition',
      [src(OF, 'name = "cute little bunny", color=colors.SALMON')], src(RO, 'define_as = "BASE_NPC_RODENT"'), None, 'vermin', 'rodent', False, False,
      'base BASE_NPC_RODENT (vermin/rodent, no image=); leaf ' + DEFAULT_EL + ' gives vermin_rodent_cute_little_bunny.png (64x64); no talents, no sustains_at_birth; can_multiply clones keep the identity',
      'vermin_rodent_cute_little_bunny.png',
      [STY, IDN('vermin_rodent_cute_little_bunny.png', 'Native shape: a plump grey-white rabbit sitting sideways with blue eyes, long upright ears and a green sprig in its mouth.'),
       R('giant-white-mouse', 'Shipped giant white mouse (pale mouse with a long pink tail and small round ears) and giant white rat: the bunny is a chunky rabbit with LONG UPRIGHT EARS and a fluffy cotton tail, no long tail.')],
      "A cute little bunny seen from a steep overhead three-quarter angle: a plump round white-and-pale-grey rabbit sitting upright and facing the viewer at a slight angle, two very long upright ears with pink insides, big round bright blue eyes, a pink nose, soft fluffy fur with light-grey shading, a fluffy round cotton tail, small pink front paws held up, and just two tiny pointed white teeth showing over the lower lip. Adorable, soft and complete.",
      "Rodent family, shipped: giant white and grey mice and rats with long tails and small round ears. The bunny is the round fluffy rabbit with two LONG UPRIGHT EARS and a cotton tail (silhouette: round body with two tall ears; hue: white with pink and blue eyes; value: very light).",
      "Warm white and pale grey fur with light cool-grey shade, pink ears, nose and paws, bright blue eyes; nothing darker than a light mid-grey; the disc stays neutral charcoal." + DISC,
      'READY single (cute little bunny)', ('silhouette', 'value'), comp=COMP + FIT)

asset(4, 'dredgling', 'dredgling', 'temporal-rift, maze (horror/temporal, default-name image, non-unique, no define_as, no nice_tile; dredge=1); Batch F/K shipped dremling and drem (different name and PNG)',
      [src(HT, 'name = "dredgling", color=colors.TAN')], src(HT, 'define_as = "BASE_NPC_HORROR_TEMPORAL"'), None, 'horror', 'temporal', False, False,
      'base BASE_NPC_HORROR_TEMPORAL (horror/temporal, no image=); leaf ' + DEFAULT_EL + ' gives horror_temporal_dredgling.png (64x64); talents Dust to Dust (activated chronomancy); resolvers.sustains_at_birth() present but the only sustained candidates are none (Dust to Dust is not sustained), so nothing is activated at birth; no type/subtype/image write',
      'horror_temporal_dredgling.png',
      [STY, IDN('horror_temporal_dredgling.png', 'Native shape: a hunched pink-skinned hairless humanoid crouching on all fours with huge bulbous white eyes and a wide open mouth.'),
       R('drem', 'Shipped drem (armoured brown dwarf-like warrior with axe and shield) and dremling (pale stone-grey giant): the dredgling is a small bare pink skinned crawler, unarmoured, no weapon.')],
      "A dredgling seen from a steep overhead three-quarter angle: a small hunched hairless humanoid of pale salmon-pink flesh crouching low on bent limbs with long-fingered hands planted forward, an oversized head with two huge bulbous glossy white-and-cream eyes with tiny dark pupils and a wide gaping mouth with a pink tongue, ribs faintly showing, a thin wrinkled skin with paler belly. No clothes, no weapon, no armour. Creepy, small and complete.",
      "Dredge family, shipped: drem is an armoured brown warrior with axe and shield, dremling a tall stone-grey giant. The dredgling is the BARE SALMON-PINK CROUCHING crawler with huge round eyes (silhouette: low four-limbed crouch, oversized head, two big round eyes; hue: salmon-pink; value: light-mid).",
      "Pale salmon-pink and coral skin with lighter peach highlight planes, cream-white eyes, pink mouth; nothing darker than mid pink except the pupils and mouth interior." + DISC,
      'READY single (dredgling)', ('silhouette', 'value', 'hue'), comp=COMP + FIT)

# ---- pack 5: demons and brecklorn ----
asset(5, 'wretchling', 'wretchling', 'valley-moon-caverns, demon-plane, acidic-vault (demon/minor, default-name image, non-unique, no define_as, no nice_tile; make_escort of same-name wretchlings; Arena entity filter by name)',
      [src(MD, 'name = "wretchling", color=colors.GREEN')], src(MD, 'define_as = "BASE_NPC_DEMON"'), None, 'demon', 'minor', False, False,
      'base BASE_NPC_DEMON (demon/minor, no image=); leaf ' + DEFAULT_EL + ' gives demon_minor_wretchling.png (64x64); talents Rush, Acid Blood (passive), Corrosive Vapour (activated); no sustains_at_birth; escorts are the same entity by name',
      'demon_minor_wretchling.png',
      [STY, IDN('demon_minor_wretchling.png', 'Native shape: a small spiky olive-green imp with bat ears, yellow acid pustules spotting its body, arms spread and claws forward.'),
       R('water-imp', 'Shipped water imp (blue-teal smooth imp with two horns and bat ears, hands raised casting): the wretchling is olive-lime with yellow acid blisters and a spiky back, low pouncing pose, no horns.')],
      "A wretchling seen from a steep overhead three-quarter angle: a small squat lean imp of bright olive-lime green skin, low in a pouncing crouch with both clawed arms stretched forward and down, large pointed bat ears, a ridge of short spikes down the back, a grinning wide mouth with tiny fangs and two round yellow eyes, the whole body spotted with bright yellow-orange acid pustules and glistening drips of yellow-green acid from the fingers. No horns, no wings, no weapon. Acidic, feral and complete.",
      "Minor demons, shipped: the water imp is a smooth blue-teal imp with two horns standing and casting. The wretchling is the OLIVE-LIME spiky crouching pouncer covered in yellow acid blisters (silhouette: low forward pounce, big ears, spiky back, arms forward; hue: olive-lime with yellow-orange; value: mid-light). The onilug is tall and thin grey; the wretchling is small and squat.",
      "Bright olive-lime green skin with lighter yellow-green highlight planes, bright yellow-orange acid pustules, pale yellow eyes; nothing darker than mid olive except the mouth interior; the acid must not glow onto or tint the disc." + DISC,
      'READY single (wretchling)', ('silhouette', 'value', 'hue'), comp=COMP + FIT)

asset(5, 'onilug', 'onilug', 'valley-moon-caverns, demon-plane (demon/minor, non-unique, no define_as, resolvers.nice_tile{tall=1} shorthand on the leaf, no image=); the {tall=1} shorthand was live-confirmed for xhaiak/shiaak (batch G, evidence/monster-live-f-20260929) and the naga nereid (batch L live, evidence/monster-batch-l-live-20260929): it resolves to invis.png + add_mos{display_h=2, display_y=-1} of the disk-formula PNG',
      [src(MD, 'name = "onilug", color=colors.GREY'), src(MD, 'resolvers.nice_tile{tall=1}')], src(MD, 'define_as = "BASE_NPC_DEMON"'), None, 'demon', 'minor', False, True,
      'base BASE_NPC_DEMON (demon/minor, no image=); NPC.lua:33 gives the disk-formula PNG demon_minor_onilug.png (64x128 tall) and resolvers.nice_tile{tall=1} expands (resolvers.lua:1375) to invis.png + add_mos{image=that PNG, display_h=2, display_y=-1}, the same shape the live probes recorded for the other {tall=1} identities; talents Curses, Soul Rot, Vimsense, Leech, Drain, Channel Staff (none sustained) and equipment resolvers (staff, rings, amulet); no sustains_at_birth; non-unique so native_tall=true',
      'demon_minor_onilug.png',
      [STY, IDN('demon_minor_onilug.png', 'Native shape (64x128 tall): a gaunt, very tall thin grey leathery humanoid with over-long arms and legs, a small head with glowing red eyes and dark spiky hair or horns.'),
       R('water-imp', 'Shipped water imp (small blue-teal imp): the onilug is the tall thin grey-mauve one, standing upright and holding a staff, nothing like a small imp.')],
      "An onilug seen from a steep overhead three-quarter angle: a gaunt tall thin humanoid demon of mid-light warm grey-mauve leathery skin, standing upright with too-long arms and legs and a narrow chest, a small bald head with bright glowing red eyes, a thin cruel grin, holding a crooked pale-bone staff topped with a small violet crystal in one long-fingered hand, a tattered mid-grey loincloth, faint darker mauve ribs. No wings, no horns. Sinister, tall and complete.",
      "Minor demons: the shipped water imp is a small blue-teal imp, and the wretchling an olive-lime squat pouncer. The onilug is the TALL THIN GREY-MAUVE upright staff-bearer with red eyes (silhouette: narrow tall upright figure with a vertical staff; hue: warm grey-mauve with red eyes and a violet crystal; value: mid-light).",
      "Mid-light warm grey-mauve skin with lighter lilac-grey highlight planes, pale-bone staff, violet crystal, bright red eyes; nothing darker than mid grey except the eye sockets and a few rib lines; the crystal and eyes must not glow onto or tint the disc." + DISC,
      'READY non-unique native-tall shorthand (onilug)', ('silhouette', 'value', 'hue'), comp=COMP + FIT)

asset(5, 'brecklorn', 'brecklorn', 'deep-bellow, maze (horror/corrupted, default-name image, non-unique, no define_as, no nice_tile; resolvers.sustains_at_birth present)',
      [src(HC, 'name = "brecklorn", color=colors.PINK')], src(HC, 'define_as = "BASE_NPC_CORRUPTED_HORROR"'), None, 'horror', 'corrupted', False, False,
      'base BASE_NPC_CORRUPTED_HORROR (horror/corrupted, no image=); leaf ' + DEFAULT_EL + ' gives horror_corrupted_brecklorn.png (64x64); sustains_at_birth activates Gloom (talents/cursed/gloom.lua, sustained aura: temporary values and particles, no type/subtype/image/add_mos/shader write; Dwarf Resilience and Leech-type passives, Dredge Frenzy/Dominate/Spit Blight/Shriek are activated); the identity is not shared with drem/dremling (different names and PNGs)',
      'horror_corrupted_brecklorn.png',
      [STY, IDN('horror_corrupted_brecklorn.png', 'Native shape: a giant hairless bat with leathery rust-brown spread wings, sores on the body, and a screaming bearded dwarf-like face.'),
       R('drem', 'Shipped drem (armoured dwarf-like warrior): the brecklorn is a winged bat-body with a tormented pink face, not a warrior; it has no armour.')],
      "A brecklorn seen from a steep overhead three-quarter angle: a giant hairless bat with a pinkish-tan wrinkled body covered in pustulant yellow sores, two leathery wings of warm rust-orange membrane with lighter tan veins held half-spread and folded compactly in a wide V close around the body, clawed wing hands, and a dwarf-like human face twisted in a constant scream with wide open mouth, a short ragged tan beard and bulging pale eyes, small clawed feet. Grotesque, screaming and complete.",
      "Corrupted horrors, shipped: drem (armoured brown dwarf-like warrior) and dremling (pale stone-grey giant). The brecklorn is the WINGED PINK-FACED BAT with a screaming dwarf face (silhouette: bat wings spread in a wide V around a small body; hue: rust-orange membrane with pink flesh and yellow sores; value: mid-light).",
      "Warm rust-orange wing membranes with lighter tan veins, pinkish-tan flesh, pale-yellow sores, tan beard, pale eyes; nothing darker than mid rust except the mouth interior and fold seams." + DISC,
      'READY single (brecklorn)', ('silhouette', 'value', 'hue'), comp=COMP + FIT)


def retry(id_, pack, **changes):
    base = next(a for a in A if a['id'] == id_)
    A.append(dict(base, pack=pack, **changes))


# ---- retry packs are appended below by later edits of retries.py ----
exec((HERE / 'retries.py').read_text()) if (HERE / 'retries.py').exists() else None

EXPLICIT_IDS = ()
PNGF = {'gigantic-corrosive-tunneler': 'explicit nice_tile add_mos PNG', 'gigantic-gravity-worm': 'explicit nice_tile add_mos PNG',
        'onilug': 'NPC.lua:33 default-name image via resolvers.nice_tile{tall=1} (live-confirmed shorthand)'}


def build():
    packs = {}
    identities = []
    render = 'game/addons/tome-checker-revised/evidence/monster-batch-o-20260929/source-contracts.json'
    seen = set()
    from PIL import Image
    for a in A:
        if a['id'] in seen:
            continue
        seen.add(a['id'])
        native_rel = NPC + a['native']
        ident = {'id': a['id'], 'native_name': a['name'], 'source': a['srcs'][0], 'define_as': a['define_as'],
                 'type': a['type'], 'subtype': a['subtype'], 'unique': a['unique'], 'native_tall': a['native_tall'],
                 'image_source': PNGF.get(a['id'], 'NPC.lua:33 default-name image'),
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
          'task': "monster-batch-o: static re-verification (no game launch) of the twelve batch-6 identities of the second gap survey (white ooze, gigantic corrosive tunneler, gigantic gravity worm, slimy ooze, poison ooze, carrion worm mass, brittle clear ooze, cute little bunny, dredgling, onilug, wretchling, brecklorn) against game/modules/tome source and native sprites. Survey verdicts were not trusted; every field below was read from source: name, type/subtype, define_as, explicit or NPC.lua:33 default image, unique, PNG on disk, and absence of moddable_tile/shader/anim/add_displays.",
          'new_ids_not_in_catalog_before_this_batch': [i['id'] for i in identities], 'identities': identities,
          'runtime_mutation_scan': {
              'method': 'every talent of each identity (resolvers.talents, inherited base talents) was resolved to its definition under game/modules/tome/data/talents and checked for mode="sustained" and for writes to self.type/subtype/image/name/display, __old_type, replace_display, add_mos, moddable_tile, shader, textures, anim, add_displays; the resolvers sustains_at_birth, nice_tile and the base-file talent lists were read. Only dredgling and brecklorn carry sustains_at_birth; the only sustained talents on any identity are Gloom (brecklorn, started at birth) and Gravity Locus (gravity worm, no sustains_at_birth).',
              'writers_found': [],
              'sustains_at_birth_review': [
                  {'identity': 'brecklorn', 'sustained': ['Gloom (talents/cursed/gloom.lua)'], 'note': 'aura of temporary values and particles; no display field, no type/subtype/image/add_mos/shader write'},
                  {'identity': 'dredgling', 'sustained': [], 'note': 'resolvers.sustains_at_birth() present; Dust to Dust is an activated chronomancy talent'},
                  {'identity': 'gigantic gravity worm', 'sustained': [], 'note': 'Gravity Locus (chronomancy/gravity.lua) is sustained but the leaf has no sustains_at_birth; if used it only adds temporary values and a particle'},
                  {'identity': 'oozes, worms, bunny, wretchling, onilug, corrosive tunneler', 'sustained': [], 'note': 'no sustains_at_birth and no sustained talent'}],
              'visibility_review': 'no identity of this batch has stealth, invisibility or a phase talent that changes display; random runes are not resolved on any of them (no resolvers.inscriptions)',
              'hits_in_batch': [],
              'no_hit': ['white ooze', 'gigantic corrosive tunneler', 'gigantic gravity worm', 'slimy ooze', 'poison ooze', 'carrion worm mass', 'brittle clear ooze', 'cute little bunny', 'dredgling', 'onilug', 'wretchling', 'brecklorn']},
          'name_collisions_checked': [
              {'name': 'carrion worm mass', 'other_definitions': ['talents/corruptions/rot.lua:62 (Worm Rot / Infestation summon, also spawned by the Corrupter horror on_takehit and by the Worm Rot timed effect): same name, type vermin/worms, explicit image npc/vermin_worms_carrion_worm_mass.png, no define_as, summoner set, summon_time 5', 'maps/vaults/auto/lesser/worms.lua:39 and general/npcs/vermin.lua CARRION_WORM_MASS are the native entity'], 'outcome': 'catalog entry is bound to define_as CARRION_WORM_MASS, so the summon (no define_as) is rejected and keeps its native art; this is the existing exact-identity behaviour, NOT a decision on summons/minions: reported to the user as an open question (whether a same-name summoned worm should also wear the token); no name+define_as key extension'},
              {'name': 'white ooze / white jelly / white worm mass', 'other_definitions': ['white jelly and white worm mass are shipped under their own names and PNGs'], 'outcome': 'exact names only; siblings cannot borrow each other\'s PNG (negative tests); Arena.lua only filters by name'},
              {'name': 'wretchling', 'other_definitions': ['make_escort spawns the same entity by name; acidic-vault random_filter by name; Arena filter by name; the ingredient "wretchling eyeball" is an object'], 'outcome': 'same entity, same art; no other actor definition'},
              {'name': 'gigantic corrosive tunneler / gigantic gravity worm', 'other_definitions': ['gigantic sandworm tunneler (shipped batch K, its own PNG), huge sandworm burrower (native)'], 'outcome': 'K kept these two native, O maps them; each cannot wear the other\'s or the K tunneler\'s tall body (negative tests); batch K negatives on the K tunneler with the corrosive PNG remain'},
              {'name': 'dredgling / brecklorn', 'other_definitions': ['drem, dremling (shipped), dredge-related horrors with other names'], 'outcome': 'exact names; siblings cannot borrow each other\'s PNG'},
              {'name': 'slimy ooze / poison ooze / brittle clear ooze / cute little bunny / onilug', 'other_definitions': ['single definitions; the Arena and vault filters only refer by name'], 'outcome': 'exact catalog entries'}],
          'kept_native': [],
          'neighbours_kept_native': [
              {'name': 'huge sandworm burrower, morphic ooze (commented out), bloated ooze', 'reason': 'not in the surveyed batch'},
              {'name': 'Corruptions carrion worm mass summon', 'reason': 'same name/PNG but no define_as; rejected by the define_as binding, pending the user decision on summons'}]}
    out = ADDON / 'evidence/monster-batch-o-20260929/source-contracts.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(ev, indent=2, ensure_ascii=False) + '\n')
    evsha = hashlib.sha256(out.read_bytes()).hexdigest()
    for a in A:
        refs = [{'path': p, 'sha256': sha(p), 'role': r, 'note': n} for r, p, n in a['refs']]
        entry = {'asset_id': a['id'], 'native_name': a['name'], 'scope': a['scope'], 'sources': a['srcs'], 'references': refs,
                 'contrast_dimensions': list(a['dims']),
                 'prompt_fields': {'subject': a['subject'], 'contrast': a['contrast'], 'composition': a['comp'] or COMP, 'palette': a['palette']},
                 'kind': 'creature', 'max_attempts': 1, 'gate': 'ready',
                 'gate_reason': f"Exact source identity re-verified directly against game/modules/tome source (name={a['name']}, define_as={a['define_as']}, type={a['type']}/subtype={a['subtype']}, unique={a['unique']}); details and hashes in evidence/monster-batch-o-20260929/source-contracts.json. {a['structure']}. Exact catalog entry only, never a whole-subtype mapping.",
                 'render_evidence': [{'path': render, 'sha256': evsha}]}
        packs.setdefault(a['pack'], []).append(entry)
    for n, assets in packs.items():
        p = ADDON / f'art/production/batches/monster-batch-o-{n}.json'
        if p.exists():
            print('exists, skipped', p.name)
            continue
        p.write_text(json.dumps({'schema': 1, 'batch_id': f'monster-batch-o-{n}', 'assets': assets}, indent=2, ensure_ascii=False) + '\n')
        print('wrote', p.name)


if __name__ == '__main__':
    build()
