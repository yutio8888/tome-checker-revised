"""Generate the monster-batch-w task packs and the pinned source-contract
evidence (survey-2 unscheduled list after batch V: fiery orc wyrmic, icy orc
wyrmic, yaech mindslayer, heavy bone giant, cave bear, war bear, grannor'vin,
rotting mummy, banshee, giant fire ant, giant ice ant, giant lightning ant; see
SELECTION.md). Pure bookkeeping: hashes native sources/sprites, writes JSON and
the composite family references. Retry packs are appended by later edits of
retries.py (never overwritten)."""
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


COMP = ("One compact complete creature on a single circular tabletop disc, steep overhead three-quarter camera; visible clear neutral base ring on every side. Keep all anatomy and equipment well inside the inner four-fifths of disc radius. Base brightness must visually match reference neutral disc, with no illumination spill or ground effects. Disc plate discipline: measured results show generations of this style reference tend to render the disc DARKER than the reference, never lighter. So do not darken the disc at all: render the neutral disc -- including the whole outer-sixth ring band and the area under the creature -- at reference lightness, a hair lighter, never darker (the style reference's own brightness). No warm cast, glow, bounce-light, gradient or vignette anywhere on the disc. Do not darken the creature to compensate either. Add no warm cast, glow, bounce-light, gradient or vignette to the disc anywhere, including directly under or behind dark-bodied creatures.")
FIT = " The ENTIRE creature, every limb, tail, wing, drip, staff and effect included, fits inside a circle of about three quarters of the disc radius around the disc centre, leaving a wide bare charcoal ring of base plate on every side, yet the creature is large and bold inside that circle."
DISC = " Dry neutral charcoal disc with restrained copper-grey bevel, kept a visibly lighter value than the creature's darkest parts so the two never merge."
A = []


def asset(pack, id_, name, scope, srcs, base, define_as, typ, sub, unique, native_tall, structure, native, refs, subject,
          contrast, palette, verdict, dims=('silhouette', 'value', 'hue'), comp=None):
    A.append(dict(comp=comp, pack=pack, id=id_, name=name, scope=scope, srcs=srcs, base=base, define_as=define_as, type=typ,
                  subtype=sub, unique=unique, native_tall=native_tall, structure=structure, native=native, refs=refs,
                  subject=subject, contrast=contrast, palette=palette, verdict=verdict, dims=dims))


STY = ('style', STYLE, 'Approved disc, lighting and camera; do not copy its creature.')


def IDN(png, note):
    return ('identity', NPC + png, note)


# ---- shared strings ----
COMPACT = " Draw the creature COMPACT and chunky: limbs, weapons, tools, cloth and effects are pulled in so the whole silhouette forms one rounded mass inside the inner three quarters of the disc; no tip, blade, hat brim, tentacle end, antenna or tail reaches the outer sixth ring band or crosses the disc rim."
BRIGHT = " Value discipline (measured lesson from earlier tokens, including a rejected dark war dog and drem master): the creature's large masses are MID-LIGHT to LIGHT in value, clearly LIGHTER than the charcoal disc, with broad pale highlight planes on every upper-left surface and a thin bright LIGHT RIM along the outline, so the silhouette reads as a bright shape on the dark disc at very small size. Nothing near-black except tiny eye slits and thin seams; no black cloth, black leather, black armour, black chitin or black fur anywhere."
DEF = ' NPC.lua:33 default-name image (npc/<type>_<subtype>_<name>.png) is the only image source: no image=, nice_tile, add_mos, moddable_tile, shader, anim or add_displays on the leaf or base; generic actor.image==entry.image single path; native sprite 64x64'
EXPL = ' explicit image= on the leaf (no nice_tile, add_mos, moddable_tile, shader, anim or add_displays on the leaf or base); generic actor.image==entry.image single path; native sprite 64x64'
TALLD = ' NPC.lua:33 default-name image on the leaf; resolvers.nice_tile{image="invis.png", add_mos={{image="npc/%s.png", display_h=2, display_y=-1}}} (an explicit tall body, keys image/display_h/display_y only; with nicer_tiles off nice_tile is a no-op and the default-name image is the single path); no moddable_tile, shader, anim or add_displays; native sprite 64x128; non-unique with no define_as, so the catalog entry carries native_tall=true (nativeTallImage accepts the body only for unique or native_tall entries, as for bone giant and eternal bone giant)'
ORC, YAECH, BONE, BEAR, HCORR, MUMMY, GHOST, ANT = (
    'general/npcs/orc.lua', 'general/npcs/yaech.lua', 'general/npcs/bone-giant.lua', 'general/npcs/bear.lua',
    'general/npcs/horror-corrupted.lua', 'zones/ancient-elven-ruins/npcs.lua', 'general/npcs/ghost.lua', 'general/npcs/ant.lua')
REFS = HERE / 'refs'
ART_REL = 'game/addons/tome-checker-revised/art/monster-batch-w/'


def composite(name, ids, cols):
    """Side-by-side of shipped runtime tokens used as a 'do not become this' family reference."""
    from PIL import Image
    out = REFS / f'{name}.png'
    if out.exists():
        return ART_REL + 'refs/' + out.name
    REFS.mkdir(exist_ok=True)
    rows = (len(ids) + cols - 1) // cols
    canvas = Image.new('RGBA', (cols * 128, rows * 128), (0, 0, 0, 0))
    for i, id_ in enumerate(ids):
        canvas.alpha_composite(Image.open(ADDON / 'data/gfx/tokens' / f'{id_}.png').convert('RGBA'), ((i % cols) * 128, (i // cols) * 128))
    canvas.save(out)
    return ART_REL + 'refs/' + out.name


def RC(name, ids, cols, note):
    return ('family', composite(name, ids, cols), note)


REF_ORCS = RC('orcs', ['orc-warrior', 'orc-soldier', 'orc-archer', 'orc-assassin', 'orc-necromancer', 'orc-master-assassin', 'orc-pyromancer', 'orc-cryomancer', 'orc-blood-mage'], 3,
              'Nine shipped orc tokens (olive orc warrior with a scimitar, spiked dark orc soldier with an axe, orc archer, hooded assassin, hooded necromancer, master assassin, and the robed pyromancer, cryomancer and blood mage): the two wyrmics are armoured dragon-scale axe fighters, bare olive-green faces under horned helms, not robed casters, not hooded and not carrying a scimitar or a bow.')
REF_YEEKS = RC('yeeks', ['yaech-diver', 'yeek-wayist', 'yaech-hunter'], 3,
               'Three shipped yeek-kin tokens (pale blue fluffy yaech diver swimming with bubbles, white yeek wayist with a dagger, umber-brown yaech hunter thrusting a trident): the yaech mindslayer is seafoam-teal, floating cross-legged with a lightning ball and a kinetic shield ring, not blue-white, not umber and not thrusting a weapon.')
REF_GIANTS = RC('bone-giants', ['bone-giant', 'half-finished-bone-giant', 'eternal-bone-giant', 'snow-giant'], 2,
                'Four shipped giant tokens (tan bone giant, muscular and symmetric with both arms hanging; purple half-finished bone giant, a thin skeleton; ivory eternal bone giant with skulls and one huge arm raised overhead; snow giant): the heavy bone giant is a squat, broad, honey-amber ossuary golem hugging a bundle of long thigh bones with both arms, not arms-down symmetric, not thin, not skull-studded and not raising one arm.')
REF_BEARS = RC('bears', ['brown-bear', 'black-bear', 'white-wolf', 'great-wolf'], 2,
               'Four shipped animal tokens (brown bear walking towards the lower left, black bear facing front-right, white wolf, great wolf): the cave bear is a pale stone-grey bear walking in profile, the war bear a russet-red bear reared up on its hind legs with tusks; neither may repeat the brown or black bear poses and colours.')
REF_SLUGS = RC('slugs', ['grannor-vor', 'slimy-crawler', 'bloated-horror', 'weirdling-beast'], 2,
               'Four shipped horror tokens (blue-grey curled acid slug grannor-vor with green slime, slimy crawler, cream bloated horror, tan-pink weirdling beast): the grannor-vin is a smoky lavender-and-mauve slug rearing up in an S-curve with a pale human face, not blue-grey, not curled flat, not green-slimed.')
REF_UNDEAD = RC('undead', ['ancient-elven-mummy', 'ghoul', 'ghast', 'greater-mummy-lord'], 2,
                'Four shipped undead tokens (upright tan ancient elven mummy with pointed ears, green ghoul, pale ghast, greater mummy lord): the rotting mummy is a hunched shambling bandaged corpse with green-grey rot lunging with one arm out, not upright and not elven.')
REF_GHOSTS = RC('ghosts', ['shade-of-telos', 'forest-wight', 'grave-wight', 'shadow-stalker'], 2,
                'Four shipped spectral tokens (blue ice shade of telos, forest wight, grave wight, shadow stalker): the banshee is a translucent pale cyan-white wailing woman with long streaming hair and a mist-dissolving gown, not a blue ice figure and not a robed wight.')
REF_ANTS = RC('ants', ['giant-white-ant', 'giant-yellow-ant', 'giant-brown-ant', 'giant-blue-ant', 'giant-carpenter-ant', 'giant-black-ant', 'giant-green-ant', 'giant-red-ant'], 4,
              'Eight shipped ant tokens (plain white, golden yellow, brown, cobalt blue, black carpenter ant with big mandibles, black ant, lime scorpion-like green ant, deep red ant with red legs): the three elemental ants must not be plain recolours of these; each needs its own elemental silhouette feature (flame plume, ice-crystal spike crest, lightning arcs).')

DEMPTY = ' no resolvers.equip that touches the body; no sustains_at_birth and no auto_classes on the leaf or base'
EQUIPONLY = ' resolvers.equip fills inventory slots only (no moddable_tile, so no display change)'

# ---- pack 1: orc wyrmics, yaech mindslayer, heavy bone giant ----
asset(1, 'fiery-orc-wyrmic', 'fiery orc wyrmic',
      "reknor (reknor-last static map tile 'f' = define_as ORC_FIRE_WYRMIC), rak-shor-pride and vor-armoury pools and the orc-hatred and orc-armoury vaults (general/npcs/orc.lua:114, humanoid/orc, non-unique, define_as ORC_FIRE_WYRMIC, rank 3, base BASE_NPC_ORC, default-name image); single definition; the vaults build this same leaf by name (random_filter), so their actors carry the same define_as",
      [src(ORC, 'name = "fiery orc wyrmic"'), src(ORC, 'define_as = "ORC_FIRE_WYRMIC"'), src(ORC, 'T_FIRE_BREATH', after='name = "fiery orc wyrmic"'), src('maps/zones/reknor-last.lua', 'ORC_FIRE_WYRMIC'), src('maps/vaults/auto/greater/orc-hatred.lua', 'name = "fiery orc wyrmic"')],
      src(ORC, 'define_as = "BASE_NPC_ORC"'), 'ORC_FIRE_WYRMIC', 'humanoid', 'orc', False, False,
      'base BASE_NPC_ORC (humanoid/orc, faction orc-pride, no image=, no shader, no sustains_at_birth);' + DEF + ';' + EQUIPONLY + ' (battleaxe, totem charm); resolvers.racial() adds only levelup talent tables; resolvers.inscriptions(1, infusion); talents Weapons Mastery (passive), Bellowing Roar, Wing Buffet, Fire Breath (activated); make_escort of orc soldiers only; no auto_classes',
      'humanoid_orc_fiery_orc_wyrmic.png',
      [STY, IDN('humanoid_orc_fiery_orc_wyrmic.png', 'Native shape (64x64): an olive-green orc in orange-gold dragon-scale armour with a curved blade. Keep the dragon-scale armour and the olive orc; make the armour bright crimson-orange with wing-fin pauldrons and a diagonal battleaxe.'), REF_ORCS],
      "A fiery orc wyrmic seen from a steep overhead three-quarter angle: a broad, powerful OLIVE-GREEN orc with small tusks and a snarling roar, wearing BRIGHT CRIMSON-ORANGE DRAGON-SCALE armour (overlapping scale plates with pale gold edges and bright orange-yellow highlight planes), a pair of red drake-wing-fin pauldrons flaring from the shoulders, a horned pale-bone-and-gold helm, a wide belt with a small red totem charm; the RIGHT ARM raises a broad battleaxe DIAGONALLY UP AND OUTWARD over the shoulder toward the upper right (bright steel axe head with an orange fire glint, the haft short and the axe head well inside the disc), the LEFT HAND open in front of the hip with a small tongue of flame, feet planted wide. Fiery, scaled, diagonal-axe and complete.",
      "Orc wyrmics: the FIERY orc wyrmic is the CRIMSON-ORANGE SCALED ONE with a diagonal raised axe and a flame in the open hand (silhouette: an upright wide-stanced figure with one long diagonal line to the upper right; hue: crimson-orange scale armour with gold edges over olive skin; value: mid-light). The shipped orc warrior is an olive fighter with a scimitar, the soldier a dark spiked axeman, the archer holds a bow and the casters are robed: this must not be robed, hooded, dark-plated or holding a scimitar or bow. Its twin, the icy orc wyrmic, is pale blue-white scaled, crouched low with a horizontal axe.",
      "Olive-green skin, crimson-orange scale armour in a mid-light value with pale orange-yellow highlight planes and gold edging, pale bone-and-gold helm, bright steel axe head with a bright rim, a small orange flame (the flame stays on the hand and must not glow onto or warm the disc); nothing darker than dark red-brown except the eye slits and thin seams." + DISC,
      "READY single, define_as ORC_FIRE_WYRMIC (fiery orc wyrmic)", comp=COMP + FIT + COMPACT + BRIGHT)

asset(1, 'icy-orc-wyrmic', 'icy orc wyrmic',
      "reknor (reknor-last static map tile 'i' = define_as ORC_ICE_WYRMIC), rak-shor-pride and vor-armoury pools and the orc-hatred and orc-armoury vaults (general/npcs/orc.lua:144, humanoid/orc, non-unique, define_as ORC_ICE_WYRMIC, rank 3, base BASE_NPC_ORC, default-name image); single definition; the vaults build this same leaf by name (random_filter), so their actors carry the same define_as",
      [src(ORC, 'name = "icy orc wyrmic"'), src(ORC, 'ORC_ICE_WYRMIC', after='name = "icy orc wyrmic"'), src(ORC, 'T_ICE_BREATH', after='name = "icy orc wyrmic"'), src('maps/zones/reknor-last.lua', 'ORC_ICE_WYRMIC'), src('maps/vaults/auto/greater/orc-hatred.lua', 'name = "icy orc wyrmic"')],
      src(ORC, 'define_as = "BASE_NPC_ORC"'), 'ORC_ICE_WYRMIC', 'humanoid', 'orc', False, False,
      'base BASE_NPC_ORC (humanoid/orc, faction orc-pride, no image=, no shader, no sustains_at_birth);' + DEF + ';' + EQUIPONLY + ' (battleaxe, totem charm); resolvers.racial() adds only levelup talent tables; resolvers.inscriptions(1, infusion); talents Weapons Mastery (passive), Ice Claw, Ice Breath (activated), Icy Skin (sustained, never started at birth: the leaf has no sustains_at_birth); make_escort of orc soldiers only; no auto_classes',
      'humanoid_orc_icy_orc_wyrmic.png',
      [STY, IDN('humanoid_orc_icy_orc_wyrmic.png', 'Native shape (64x64): an olive-green orc in teal-blue dragon-scale armour with a curved blade. Keep the dragon-scale armour and the olive orc; make the armour pale ice-blue and white with ice-crystal pauldrons and a low horizontal battleaxe.'), REF_ORCS],
      "An icy orc wyrmic seen from a steep overhead three-quarter angle: a broad OLIVE-GREEN orc (a slightly grey-green cast) with small tusks and a hard glare, wearing PALE ICE-BLUE and WHITE DRAGON-SCALE armour with bright frost-white edges and pale cyan highlight planes, a pair of jagged ICE-CRYSTAL pauldrons (three short pale-cyan ice spikes on each shoulder, the spikes short), a pale horned white-bone helm with a small frost crest, a small pale-blue totem charm on the belt; crouched in a wide LOW STANCE leaning to the left with BOTH HANDS holding a battleaxe HORIZONTALLY across the hips (the axe head at the left, bright pale steel rimed with white frost, the whole axe well inside the disc), a small puff of pale frost breath at the mouth. Frosty, scaled, low-and-horizontal and complete.",
      "Orc wyrmics: the ICY orc wyrmic is the PALE BLUE-WHITE SCALED ONE crouched low with a horizontal two-handed axe and ice-crystal pauldrons (silhouette: a wide low crouch with one horizontal line and small spiky shoulders; hue: ice-blue and white scale armour over grey-green olive skin; value: light). The shipped orc warrior is an olive fighter with a scimitar, the soldier a dark spiked axeman, the archer holds a bow and the casters are robed: this must not be robed, hooded, dark-plated or holding a scimitar or bow, and must not be the orange-red upright twin with a raised diagonal axe (the fiery orc wyrmic).",
      "Grey-green olive skin, pale ice-blue and white scale armour in a light value with bright white edging and pale cyan highlight planes, pale bone helm, pale steel axe head with white frost and a bright rim, cyan ice crystals (the frost stays on the creature and must not brighten, whiten or tint the disc); nothing darker than mid blue-grey except the eye slits and thin seams; the disc stays neutral charcoal at reference lightness." + DISC,
      "READY single, define_as ORC_ICE_WYRMIC (icy orc wyrmic)", comp=COMP + FIT + COMPACT + BRIGHT)

asset(1, 'yaech-mindslayer', 'yaech mindslayer',
      "murgol-lair pool (general/npcs/yaech.lua:79, humanoid/yaech, non-unique, no define_as, rank 2, base BASE_NPC_YAECH, default-name image); single definition; the south-beach zone only draws yaech from the humanoid/yaech pool, so a yaech mindslayer there is this same leaf",
      [src(YAECH, 'name = "yaech mindslayer"'), src(YAECH, 'T_KINETIC_SHIELD', after='name = "yaech mindslayer"'), src(YAECH, 'define_as = "BASE_NPC_YAECH"')],
      src(YAECH, 'define_as = "BASE_NPC_YAECH"'), None, 'humanoid', 'yaech', False, False,
      'base BASE_NPC_YAECH (humanoid/yaech, can_breath water, no image=, no shader);' + DEF + ';' + EQUIPONLY + ' (trident); talents Kinetic Aura, Charged Aura, Kinetic Shield, Exotic Weapons Mastery; none is started at birth (no sustains_at_birth on the leaf or base) and their effects are temporary values; no auto_classes on the leaf or base (only the Murgol-lair bosses have Mindslayer auto_classes)',
      'humanoid_yaech_yaech_mindslayer.png',
      [STY, IDN('humanoid_yaech_yaech_mindslayer.png', 'Native shape (64x64): a pale blue-white fluffy yeek-like swimmer holding a curved blade, with bubbles. Keep the small fluffy yaech psion with bubbles, but seafoam-teal fur, floating cross-legged, no blade.'), REF_YEEKS],
      "A yaech mindslayer seen from a steep overhead three-quarter angle: a small fluffy yeek-like aquatic psion with SEAFOAM-TEAL and PALE-MINT fur in a mid-light value, a cream face and belly, two large glowing PALE-YELLOW eyes with a calm stare, a small pale coral circlet, FLOATING a little above the floor in a cross-legged pose with both hands raised in front of the chest, a small crackling ball of bright YELLOW-WHITE LIGHTNING between the palms, a thin translucent pale-cyan circular KINETIC SHIELD RING hugging the front of the body (the ring no wider than the body), a small pale-steel trident floating tilted behind one shoulder (short, well inside the disc), a few tiny bubbles. Calm, psionic, round and complete.",
      "Yeeks: the YAECH MINDSLAYER is the SEAFOAM-TEAL FLOATING PSION with a lightning ball and a shield ring (silhouette: a compact round seated figure inside a circular ring with a small spark between the hands; hue: seafoam teal and mint fur, cream belly, yellow-white lightning, pale cyan ring; value: mid-light). The shipped yaech diver is a pale blue-white swimmer, the yeek wayist a white yeek with a dagger and the yaech hunter an umber-brown lunger with a trident: this must not be blue-white, white or umber and must not lunge or thrust a weapon.",
      "Seafoam-teal and pale mint fur in a mid-light value with pale highlight planes, a cream face and belly, pale-yellow eyes, yellow-white lightning ball with a bright core, a pale-cyan translucent ring, pale-steel trident with a bright highlight edge, tiny pale bubbles (the lightning and ring stay on the creature and must not brighten, warm or tint the disc); nothing darker than dark teal-grey except the pupils and thin seams." + DISC,
      "READY single, no define_as (yaech mindslayer)", comp=COMP + FIT + COMPACT + BRIGHT)

asset(1, 'heavy-bone-giant', 'heavy bone giant',
      "rak-shor-pride, telmur and vor-armoury pools (general/npcs/bone-giant.lua:85, undead/giant, non-unique, no define_as, rank 2, base BASE_NPC_BONE_GIANT, explicit nice_tile tall body); the necromancer's Assemble talent (talents/spells/master-of-bones.lua:429, minions_list.h_bone_giant) builds the same-named minion with type undead, subtype giant, the same nice_tile body and no define_as, so it wears the same token by the ordinary name key (see summons_and_same_body_copies)",
      [src(BONE, 'name = "heavy bone giant"'), src(BONE, 'resolvers.nice_tile', after='name = "heavy bone giant"'), src('talents/spells/master-of-bones.lua', 'name = "heavy bone giant"'), src('talents/spells/master-of-bones.lua', 'is_bone_giant = "h_bone_giant"')],
      src(BONE, 'define_as = "BASE_NPC_BONE_GIANT"'), None, 'undead', 'giant', False, True,
      'base BASE_NPC_BONE_GIANT (undead/giant, no image=, no shader, no sustains_at_birth);' + TALLD % 'undead_giant_heavy_bone_giant' + '; talents Bone Armour, Throw Bones, Stun (all activated); no auto_classes',
      'undead_giant_heavy_bone_giant.png',
      [STY, IDN('undead_giant_heavy_bone_giant.png', 'Native shape (64x128, tall): a tall pale-tan bone golem built from twiggy bones with a lilac outline aura. Keep the bone-built golem, but draw it as ONE compact squat broad figure filling the disc, honey-amber, no tall canvas.'), REF_GIANTS],
      "A heavy bone giant seen from a steep overhead three-quarter angle: a massively broad, squat, hunched ossuary golem built from hundreds of AMBER-TAN and HONEY-BROWN bones with pale cream highlight planes, a huge barrel chest of stacked ribcages, huge armoured shoulders of layered pelvis and shoulder-blade plates, a small skull head with two dull amber glowing eyes sunk between the shoulders, BOTH ARMS wrapped around a big BUNDLE OF SIX LONG THIGH-BONES clutched against the chest like a load of javelins to throw (the bone ends short and inside the disc), short thick leg-pillars, a very faint warm-ochre unholy haze close to the outline. Wide, heavy, round and complete.",
      "Giants: the HEAVY BONE GIANT is the SQUAT HONEY-AMBER ONE hugging a bundle of long bones (silhouette: a very wide low round mass with a bone bundle across the chest and no raised arm; hue: honey-amber and amber-tan bone with cream highlights; value: mid-light). The shipped bone giant is a tan, muscular, symmetric figure with both arms hanging, the half-finished bone giant a thin purple skeleton and the eternal bone giant an ivory skull-studded figure with one huge arm raised overhead: this must not have arms hanging, must not be thin, must not be ivory-white or skull-studded and must not raise an arm.",
      "Honey-amber and amber-tan bone in a mid-light value with pale cream highlight planes and warm brown shadows, dull amber eye glow, a very faint warm-ochre haze (the haze stays thin, on the creature, and must not brighten or tint the disc); nothing darker than mid warm brown except the eye sockets and thin seams." + DISC,
      "READY tall (heavy bone giant, native_tall)", comp=COMP + FIT + COMPACT + BRIGHT)

# ---- pack 2: bears and slug ----
asset(2, 'cave-bear', 'cave bear',
      "old-forest, noxious-caldera, scintillating-caves, norgos-lair, daikara and more zones' bear pools (general/npcs/bear.lua:72, animal/bear, non-unique, no define_as, rank 2, base BASE_NPC_BEAR, explicit image=npc/cave_bear.png); the only definition of this name; no vault, event or talent builds another actor with this name",
      [src(BEAR, 'name = "cave bear"'), src(BEAR, 'T_KNOCKBACK', after='name = "cave bear"'), src(BEAR, 'define_as = "BASE_NPC_BEAR"')],
      src(BEAR, 'define_as = "BASE_NPC_BEAR"'), None, 'animal', 'bear', False, False,
      'base BASE_NPC_BEAR (animal/bear, no image=, no shader, no sustains_at_birth);' + EXPL + '; talents Stamina Pool, Stun, Knockback (activated); no equip, no auto_classes',
      'cave_bear.png',
      [STY, IDN('cave_bear.png', 'Native shape (64x64): a big shaggy grey-brown bear walking on all fours with its head lowered to the left. Keep the bear on all fours but make the fur pale stone-grey and draw it in profile walking to the right with a domed shoulder hump.'), REF_BEARS],
      "A cave bear seen from a steep overhead three-quarter angle: a big shaggy STONE-GREY and ASH-BROWN bear in a mid-light value, pale grey-white frosted guard hairs over a domed shoulder hump, a lighter BUFF muzzle and pale claws, small dark eyes, walking heavily on all four legs in PROFILE towards the right with its head held low and slightly swinging, pale cave dust on the paws. A heavy, round, hump-backed animal, complete.",
      "Bears: the CAVE BEAR is the PALE STONE-GREY ONE walking in profile to the right with a domed shoulder hump and a low head (silhouette: a long low body in side view with a hump; hue: stone grey and ash brown with a buff muzzle; value: mid-light). The shipped brown bear is a brown bear walking towards the lower left and the black bear a black front-facing bear: this must not be brown or black and must not face the lower left or the front. The other new bear is a russet-red bear reared up on its hind legs with tusks (war bear).",
      "Stone-grey and ash-brown fur in a mid-light value with pale grey-white frosted highlight planes on the hump and shoulders, buff muzzle, pale claws; nothing darker than dark grey-brown except the eyes, nose and thin seams; the disc stays neutral charcoal at reference lightness and no grey fur may merge with it." + DISC,
      "READY single, no define_as (cave bear)", comp=COMP + FIT + COMPACT + BRIGHT)

asset(2, 'war-bear', 'war bear',
      "old-forest, noxious-caldera, scintillating-caves, norgos-lair, daikara and more zones' bear pools and the grushnak-armoury vault (general/npcs/bear.lua:83, animal/bear, non-unique, no define_as, rank 2, base BASE_NPC_BEAR, explicit image=npc/war_bear.png); the only definition of this name; the vault builds this same leaf by name (random_filter) as a random boss 'Warbear', which the existing random-origin path covers for single-image entries",
      [src(BEAR, 'name = "war bear"'), src(BEAR, 'T_DISARM', after='name = "war bear"'), src('maps/vaults/grushnak-armory.lua', 'name = "war bear"'), src(BEAR, 'define_as = "BASE_NPC_BEAR"')],
      src(BEAR, 'define_as = "BASE_NPC_BEAR"'), None, 'animal', 'bear', False, False,
      'base BASE_NPC_BEAR (animal/bear, no image=, no shader, no sustains_at_birth);' + EXPL + '; talents Stamina Pool, Stun, Knockback, Disarm (activated); no equip, no auto_classes',
      'war_bear.png',
      [STY, IDN('war_bear.png', 'Native shape (64x64): a dark brown bear facing the front with an open mouth and tusks. Keep the tusks and the snarling mouth, but make the fur russet-red and draw the bear reared up on its hind legs with both forepaws raised.'), REF_BEARS],
      "A war bear seen from a steep overhead three-quarter angle: a big bear REARED UP on its hind legs in a roaring stance with both forepaws raised and clawed, RUSSET-RED-BROWN fur in a mid-light value with bright copper highlight planes and a cream chest patch, two long curved IVORY TUSKS curling up from the lower jaw, an open pink mouth with pale teeth, a broad rough IRON-BANDED LEATHER collar with brass rivets and a short frayed chain at the neck. Fierce, upright, round and complete; the raised paws kept inside the disc.",
      "Bears: the WAR BEAR is the RUSSET-RED ONE reared up on its hind legs with tusks and an iron collar (silhouette: an upright figure with two raised paws and curved tusks; hue: russet red-brown with copper highlights, cream chest, ivory tusks, iron and brass; value: mid-light). The shipped brown bear is a brown bear on all fours towards the lower left and the black bear a black front-facing bear on all fours: this must not be on all fours, brown or black. The other new bear is a pale stone-grey bear walking in profile (cave bear).",
      "Russet red-brown fur in a mid-light value with copper highlight planes, a cream chest patch, ivory tusks with bright highlights, pale claws, an open pink mouth, a dull iron collar with brass rivets; nothing darker than dark red-brown except the eyes and thin seams." + DISC,
      "READY single, no define_as (war bear)", comp=COMP + FIT + COMPACT + BRIGHT)

asset(2, 'grannor-vin', "grannor'vin",
      "deep-bellow and maze pools (general/npcs/horror-corrupted.lua:216, horror/corrupted, non-unique, no define_as, rank 2, base BASE_NPC_CORRUPTED_HORROR, default-name image); the only definition of this name; no vault, event or talent builds another actor with this name",
      [src(HCORR, "name = \"grannor'vin\""), src(HCORR, 'T_CALL_SHADOWS', after="name = \"grannor'vin\""), src(HCORR, 'resolvers.sustains_at_birth()', after="name = \"grannor'vin\""), src(HCORR, 'define_as = "BASE_NPC_CORRUPTED_HORROR"')],
      src(HCORR, 'define_as = "BASE_NPC_CORRUPTED_HORROR"'), None, 'horror', 'corrupted', False, False,
      'base BASE_NPC_CORRUPTED_HORROR (horror/corrupted, faction horrors, no image=, no shader, no sustains_at_birth in the base);' + DEF + '; talents Call Shadows (sustained), Creeping Darkness, Dark Torrent (activated); resolvers.sustains_at_birth() on the leaf starts Call Shadows (a rotating shield particle and shadow summons, no type/subtype/image/add_mos write; the shadows are separate actors); no equip, no auto_classes',
      'horror_corrupted_grannor_vin.png',
      [STY, IDN('horror_corrupted_grannor_vin.png', 'Native shape (64x64): a big reddish-brown slug with an S-curved raised tail and a screaming human face on its front. Keep the sluglike body with the human face, but make it smoky lavender and mauve with pale highlights, the front half reared up.'), REF_SLUGS],
      "A grannor'vin seen from a steep overhead three-quarter angle: a large sluglike horror with a smooth glossy SMOKY LAVENDER-GREY and PALE MAUVE body in a mid-light value with silver-white highlight planes along the back, the FRONT HALF REARED UP in an S-curve, at the front of the raised head a pale cream-white HUMAN FACE (grief-stricken, hollow eyes, open mouth), a ribbed underside in pale pink-grey, the tail curling in a compact round spiral at the base, and a few thin wisps of DEEP-VIOLET shadow smoke curling off the back (thin, kept behind and beside the body, never covering it). Heavy, glossy, reared and complete.",
      "Horrors: the GRANNOR'VIN is the SMOKY LAVENDER-MAUVE SLUG with its front half reared in an S-curve and a pale human face (silhouette: a tall S-shaped rear on a round spiral base; hue: lavender-grey and pale mauve with silver highlights and thin violet smoke; value: mid-light). The shipped grannor'vor is a blue-grey acid slug curled flat with green slime, the slimy crawler a crawler, the bloated horror a cream floating pear and the weirdling beast a tan-pink many-armed beast: this must not be blue-grey, green-slimed, curled flat or black.",
      "Smoky lavender-grey and pale mauve in a mid-light value with silver-white highlight planes and a bright light rim, cream-white face with hollow dark-violet eyes, pale pink-grey underside, thin deep-violet smoke wisps (the smoke stays thin and must not darken the disc or cover the body); nothing darker than dark violet except the eye hollows, the mouth and thin seams; the disc stays neutral charcoal at reference lightness." + DISC,
      "READY single, no define_as (grannor'vin)", comp=COMP + FIT + COMPACT + BRIGHT)

# ---- pack 3: mummy and banshee ----
asset(3, 'rotting-mummy', 'rotting mummy',
      "ancient-elven-ruins pool (zones/ancient-elven-ruins/npcs.lua:155, undead/mummy, non-unique, no define_as, rank 2, base BASE_NPC_MUMMY, default-name image); the only definition of this name; no vault, event or talent builds another actor with this name",
      [src(MUMMY, 'name = "rotting mummy"'), src(MUMMY, 'T_BITE_POISON', after='name = "rotting mummy"'), src('general/npcs/mummy.lua', 'define_as = "BASE_NPC_MUMMY"')],
      src('general/npcs/mummy.lua', 'define_as = "BASE_NPC_MUMMY"'), None, 'undead', 'mummy', False, False,
      'base BASE_NPC_MUMMY (undead/mummy, no image=, no shader, no sustains_at_birth);' + DEF + '; resolvers.racial("shalore") only adds levelup talent tables, resolvers.equip mummy armour (equipment only, no moddable_tile), resolvers.inscriptions(1, rune); talents Weakness Disease, Gnaw, Retch, Bite Poison (none sustained); no auto_classes (the only auto_classes in that file belong to another leaf)',
      'undead_mummy_rotting_mummy.png',
      [STY, IDN('undead_mummy_rotting_mummy.png', 'Native shape (64x64): a hunched bandage-wrapped corpse in grey and tan stripes with arms hanging. Keep the striped bandages and the hunched shambling corpse, but paler bandages with green-grey rot and one arm reaching.'), REF_UNDEAD],
      "A rotting mummy seen from a steep overhead three-quarter angle: a hunched, shambling corpse wrapped in filthy TAN and BONE-CREAM linen bandages stained with brown and GREEN-GREY rot patches, frayed bandage tails trailing from the arms and legs, ONE ARM STRETCHED FORWARD towards the lower left with grasping fingers of grey-green rotting flesh showing through the wrappings, the other arm hanging, the head half-wrapped with one sunken glowing PALE YELLOW-GREEN eye and a gaping jaw with grey teeth. Lurching, ragged, round and complete.",
      "Undead: the ROTTING MUMMY is the HUNCHED LURCHING ONE in stained tan bandages with green-grey rot and one arm reaching out (silhouette: a hunched mass with one long arm stretched forward and trailing rags; hue: tan and bone-cream bandages with brown stains and green-grey rot; value: mid-light). The shipped ancient elven mummy is an upright pale tan elf with pointed ears, the ghoul is green, the ghast pale and the greater mummy lord ornate: this must not be upright, must not have pointed ears and must not be clean tan.",
      "Tan and bone-cream bandages in a mid-light value with pale highlight planes and warm brown stains, green-grey rot patches, grey-green flesh, a pale yellow-green eye glow (the glow stays on the creature and must not tint the disc); nothing darker than dark brown-grey except the eye socket and thin seams." + DISC,
      "READY single, no define_as (rotting mummy)", comp=COMP + FIT + COMPACT + BRIGHT)

asset(3, 'banshee', 'banshee',
      "dreadfell, rak-shor-pride, telmur and demon-plane ghost pools (general/npcs/ghost.lua:108, undead/ghost, non-unique, no define_as, rank 2, base BASE_NPC_GHOST, explicit image=npc/banshee.png); the only definition of this name (ruin banshee is another name and PNG, not selected); no vault, event or talent builds another actor with this name",
      [src(GHOST, 'name = "banshee"'), src(GHOST, 'T_SHRIEK', after='name = "banshee"'), src(GHOST, 'resolvers.sustains_at_birth()', after='define_as = "BASE_NPC_GHOST"'), src(GHOST, 'define_as = "BASE_NPC_GHOST"')],
      src(GHOST, 'define_as = "BASE_NPC_GHOST"'), None, 'undead', 'ghost', False, False,
      'base BASE_NPC_GHOST (undead/ghost, pass_wall, no image=, no shader);' + EXPL + '; talents Shriek, Phase Door, Silence, Mind Disruption (activated) and Blur Sight (sustained); the base resolvers.sustains_at_birth() starts Blur Sight (a phantasm_shield particle and temporary values only, no type/subtype/image/add_mos write); no equip, no auto_classes',
      'banshee.png',
      [STY, IDN('banshee.png', 'Native shape (64x64): a translucent cyan ghostly woman with long flowing hair. Keep the cyan wailing woman with streaming hair and mist-dissolving gown, drawn as a solid glowing spectre.'), REF_GHOSTS],
      "A banshee seen from a steep overhead three-quarter angle: a translucent ghostly woman's form in PALE CYAN and ICE-WHITE glowing in a light value, LONG WILD HAIR streaming up and sideways like wind-blown mist, a tattered flowing gown dissolving into curling wisps of mist below the waist, the face gaunt with hollow deep-blue eyes and the mouth wide open in a wail, BOTH ARMS raised with clawed hands beside the head, floating just above the floor. Ethereal but solid enough to read as a bold bright silhouette; every wisp tip inside the disc.",
      "Spectres: the BANSHEE is the PALE CYAN-WHITE WAILING WOMAN with streaming hair and raised clawed hands (silhouette: a woman's torso with a big wind-blown hair mass and mist tails, both arms raised; hue: pale cyan and ice-white with deep-blue eye hollows; value: light). The shipped shade of telos is a blue ice humanoid, the forest and grave wights are robed undead and the shadow stalker is dark: this must not be blue ice, robed or dark.",
      "Pale cyan and ice-white spectral body in a light value with bright white highlights and a bright light rim, deep-blue hollow eyes and mouth, pale mist wisps (the glow stays on the creature and must not brighten or tint the disc); nothing darker than mid blue-grey except the eye hollows and mouth." + DISC,
      "READY single, no define_as (banshee)", comp=COMP + FIT + COMPACT + BRIGHT)

# ---- pack 4: elemental ants ----
asset(4, 'giant-fire-ant', 'giant fire ant',
      "ardhungol, dreadfell, reknor, ruined-dungeon, old-forest and four more zones' ant pools (general/npcs/ant.lua:131, insect/ant, non-unique, no define_as, rank 1, base BASE_NPC_ANT, explicit image=npc/fire_ant.png); the only definition of this name; no vault, event or talent builds another actor with this name",
      [src(ANT, 'name = "giant fire ant"'), src(ANT, 'T_FLAME_FURY', after='name = "giant fire ant"'), src(ANT, 'define_as = "BASE_NPC_ANT"')],
      src(ANT, 'define_as = "BASE_NPC_ANT"'), None, 'insect', 'ant', False, False,
      'base BASE_NPC_ANT (insect/ant, no image=, no shader, no sustains_at_birth);' + EXPL + '; melee_project fire, talents Ritch Flamespitter Bolt and Flame Fury (activated); no equip, no auto_classes',
      'fire_ant.png',
      [STY, IDN('fire_ant.png', 'Native shape (64x64): a dark red ant with a burning abdomen, flames on the back. Keep the burning ant, but make the carapace glowing burnt-orange and draw a tall flame plume from the abdomen.'), REF_ANTS],
      "A giant fire ant seen from a steep overhead three-quarter angle: a large ant angled diagonally with its head towards the upper left, a glossy BURNT-ORANGE and VERMILION carapace glowing from within like hot metal in a light-mid value, seams glowing bright YELLOW-ORANGE, a plume of bright ORANGE-YELLOW FLAMES with a white-yellow core rising from the swollen abdomen (a compact flame plume no taller than the body), small licking flames along the legs, mandibles open with a small fireball forming, antennae with ember tips curled in close, legs tucked in. Blazing, compact, plume-topped and complete.",
      "Ants: the GIANT FIRE ANT is the BURNT-ORANGE GLOWING ONE with a flame plume on the abdomen and a fireball at the mandibles (silhouette: a compact diagonal ant with a tall flame plume over the rear; hue: burnt-orange and vermilion with yellow-orange glowing seams and orange-yellow flames; value: light-mid). The shipped red ant is a dark red ant with long red legs and antennae spread flat, the yellow ant golden, the brown ant brown and the black ants black: this must not be dark red or black and must not be a flat spread ant without a flame plume. The other new ants are a crystalline pale-cyan ice ant with a spike crest and a lavender lightning ant with arcs.",
      "Burnt-orange and vermilion carapace in a light-mid value with bright yellow-orange glowing seams and pale orange highlight planes, orange-yellow flames with a white-yellow core (the flames stay on the ant and must not glow onto or warm the disc); nothing darker than dark red-brown except the eye dots and thin seams." + DISC,
      "READY single, no define_as (giant fire ant)", comp=COMP + FIT + COMPACT + BRIGHT)

asset(4, 'giant-ice-ant', 'giant ice ant',
      "ardhungol, dreadfell, reknor, ruined-dungeon, old-forest and four more zones' ant pools (general/npcs/ant.lua:147, insect/ant, non-unique, no define_as, rank 1, base BASE_NPC_ANT, explicit image=npc/ice_ant.png); the only definition of this name; no vault, event or talent builds another actor with this name",
      [src(ANT, 'name = "giant ice ant"'), src(ANT, 'T_ICY_SKIN', after='name = "giant ice ant"'), src(ANT, 'define_as = "BASE_NPC_ANT"')],
      src(ANT, 'define_as = "BASE_NPC_ANT"'), None, 'insect', 'ant', False, False,
      'base BASE_NPC_ANT (insect/ant, no image=, no shader, no sustains_at_birth);' + EXPL + '; melee_project ice, ingredient_on_death FROST_ANT_STINGER, talents Water Bolt (activated) and Icy Skin (sustained, never started at birth: no sustains_at_birth on the leaf or base); no equip, no auto_classes',
      'ice_ant.png',
      [STY, IDN('ice_ant.png', 'Native shape (64x64): a translucent pale white-blue ant. Keep the icy frosted ant, but make the carapace crystalline pale cyan with a crest of jagged ice spikes on its back.'), REF_ANTS],
      "A giant ice ant seen from a steep overhead three-quarter angle: a large ant angled diagonally with its head towards the lower right, a translucent crystalline PALE-CYAN and ICE-BLUE carapace with white frost in a light value, a CREST OF FIVE SHORT JAGGED ICE-CRYSTAL SPIKES along its back and abdomen (each spike pale cyan with bright white edges, all short and inside the disc), frost-rimed mandibles, thick white rime on the leg joints, a few tiny snow crystals drifting close to the body, antennae curled in close, legs tucked in. Frosty, crystalline, spiky-backed and complete.",
      "Ants: the GIANT ICE ANT is the CRYSTALLINE PALE-CYAN ONE with a crest of ice spikes along its back (silhouette: a compact diagonal ant with a jagged spiky spine; hue: pale cyan and ice-blue with white frost; value: light). The shipped white ant is a plain smooth white slender ant, the blue ant a glossy cobalt-blue one and the yellow and red ants golden and deep red: this must not be a smooth plain white ant, not cobalt blue and not spineless. The other new ants are a burnt-orange fire ant with a flame plume and a lavender lightning ant with arcs.",
      "Pale cyan and ice-blue crystalline carapace in a light value with bright white frost and highlight planes, cyan spikes with bright white edges, white rime (the frost stays on the ant and must not whiten, brighten or tint the disc); nothing darker than mid blue-grey except the eye dots and thin seams; the disc stays neutral charcoal at reference lightness." + DISC,
      "READY single, no define_as (giant ice ant)", comp=COMP + FIT + COMPACT + BRIGHT)

asset(4, 'giant-lightning-ant', 'giant lightning ant',
      "ardhungol, dreadfell, reknor, ruined-dungeon, old-forest and four more zones' ant pools (general/npcs/ant.lua:164, insect/ant, non-unique, no define_as, rank 1, base BASE_NPC_ANT, explicit image=npc/lightning_ant.png); the only definition of this name; no vault, event or talent builds another actor with this name",
      [src(ANT, 'name = "giant lightning ant"'), src(ANT, 'T_CALL_LIGHTNING', after='name = "giant lightning ant"'), src(ANT, 'define_as = "BASE_NPC_ANT"')],
      src(ANT, 'define_as = "BASE_NPC_ANT"'), None, 'insect', 'ant', False, False,
      'base BASE_NPC_ANT (insect/ant, no image=, no shader, no sustains_at_birth);' + EXPL + '; melee_project lightning, talents Lightning Speed and Call Lightning (activated); no equip, no auto_classes',
      'lightning_ant.png',
      [STY, IDN('lightning_ant.png', 'Native shape (64x64): a blue ant with white lightning sparks arcing over its body. Keep the crackling ant, but a pale lavender carapace with a glowing abdomen and a small crackling arc halo.'), REF_ANTS],
      "A giant lightning ant seen from a steep overhead three-quarter angle: a large ant angled diagonally with its head towards the upper right, a glossy PALE-LAVENDER and STEEL-VIOLET carapace with bright white highlight planes in a light-mid value, the swollen abdomen glowing with a bright WHITE-YELLOW core, JAGGED BRIGHT YELLOW-WHITE LIGHTNING ARCS jumping between the two antennae and around the abdomen in a small crackling halo (thin bolts, all kept close to the body and inside the disc), legs tensed and tucked in. Electric, compact, arc-haloed and complete.",
      "Ants: the GIANT LIGHTNING ANT is the PALE-LAVENDER ONE crowned with jagged yellow-white lightning arcs and a glowing abdomen (silhouette: a compact diagonal ant with a zigzag arc halo; hue: pale lavender and steel violet with yellow-white lightning; value: light-mid). The shipped blue ant is a glossy cobalt-blue ant, the yellow ant golden and the white ant plain white: this must not be cobalt blue, golden or plain white and must not lack the arcs. The other new ants are a burnt-orange fire ant with a flame plume and a crystalline pale-cyan ice ant with a spike crest.",
      "Pale lavender and steel-violet carapace in a light-mid value with bright white highlight planes, a white-yellow abdomen core, thin bright yellow-white lightning arcs (the arcs stay on the ant and must not brighten, tint or light the disc); nothing darker than dark violet-grey except the eye dots and thin seams." + DISC,
      "READY single, no define_as (giant lightning ant)", comp=COMP + FIT + COMPACT + BRIGHT)


def retry(id_, pack, **changes):
    base = next(a for a in A if a['id'] == id_)
    A.append(dict(base, pack=pack, **changes))


# ---- retry packs are appended below by later edits of retries.py ----
exec((HERE / 'retries.py').read_text()) if (HERE / 'retries.py').exists() else None

EXPL_IDS = ('cave-bear', 'war-bear', 'banshee', 'giant-fire-ant', 'giant-ice-ant', 'giant-lightning-ant')
TALL_IDS = ('heavy-bone-giant',)
PNGF = {a['id']: 'NPC.lua:33 default-name image on the leaf (no image=/nice_tile)' for a in A}
PNGF.update({i: 'explicit image= on the leaf (no nice_tile/add_mos)' for i in EXPL_IDS})
PNGF.update({i: 'NPC.lua:33 default-name image on the leaf plus an explicit nice_tile tall body (image=invis.png, one add_mos entry with display_h=2, display_y=-1 naming the same PNG)' for i in TALL_IDS})


def build():
    packs = {}
    identities = []
    render = 'game/addons/tome-checker-revised/evidence/monster-batch-w-20260930/source-contracts.json'
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
        if a['native_tall']:
            ident['tall_body'] = {'image': 'invis.png', 'add_mos': [{'image': 'npc/' + a['native'], 'display_h': 2, 'display_y': -1}],
                                  'catalog_flag': 'native_tall=true', 'static_pin': 'nice_tile names the tall PNG explicitly; not unique, so no define_as binding is possible'}
        if a['base']:
            ident['base_source'] = a['base']
        if len(a['srcs']) > 1:
            ident['extra_sources'] = a['srcs'][1:]
        identities.append(ident)
    findings = [
        "All twelve names have exactly one leaf definition. The vaults (orc-hatred, orc-armoury, grushnak-armory), the reknor-last static map (define_as tiles), the orc wyrmics' make_escort and the zone pools only build those same leaves through random_filter/name/define_as lookups, so they are the very same actors; random bosses made from a flat entry go through the existing captureRandomOrigin path (a Warbear random boss from the war bear keeps the token as a 'single' origin), a random boss made from the non-unique native-tall heavy bone giant stays native (only unique tall bodies qualify).",
        "Heavy bone giant: talents/spells/master-of-bones.lua:429 (Assemble, minions_list.h_bone_giant, built by necroSetupSummon in talents/spells/spells.lua) creates a summon with the same name 'heavy bone giant', type undead, subtype giant and the identical nice_tile body (invis.png + add_mos {npc/undead_giant_heavy_bone_giant.png, display_h=2, display_y=-1}); it has no define_as and no unique, plus summoner, necrotic_minion, summoner_gain_exp and is_bone_giant fields. The catalog entry has no define_as, so the ordinary exact name+type+subtype key already matches it, and nativeTallImage() accepts its body: NO variants entry and NO image alias is needed (same as the shipped eternal bone giant and bone giant minions). A Lord of Skulls renames its minion ('Lord of Skulls (bone giant)', timed_effects/magical.lua:4812) and replaces its display, and stays native. tests/token_mapping.lua covers both cases.",
        "Fiery and icy orc wyrmic: their leaves carry define_as ORC_FIRE_WYRMIC and ORC_ICE_WYRMIC, which the catalog entries bind exactly (like bandit and the naga tidewarden); reknor-last builds them by define_as and the vaults by name, both reaching the same leaf. No summon or clone builds an actor with either name.",
        "No summon, clone, event or talent builds an actor with any of the other ten names using a different native PNG (grep of every actor definition, static map, quest script, vault, encounter, event and talent under game/modules/tome for the names and PNGs, including data/talents/gifts wild summons and thought-forms), so no image_aliases entry and no variants entry are added; the summon-only image alias mechanism from batch U is not used.",
        "Neighbours that reuse a name or subtype but stay native: 'ruin banshee' (another name and PNG, vault greater-crypt), 'brown bear'/'black bear'/'grizzly bear' (other names; brown and black are catalogued, grizzly is a tall body not catalogued), 'grannor'vor' (catalogued separately), 'giant acid ant' (tied at 4.8, not selected) and 'giant army ant' (4.4), 'animated mummy wrappings' and 'greater mummy' (other names), 'yeek mindslayer' (a yeek, another name and PNG).",
        "Result: no per-construct `variants` entry and no `image_aliases` entry is needed for this batch; the heavy bone giant Assemble minion is covered by the exact name key.",
    ]
    ev = {'schema': 1,
          'task': "monster-batch-w: static re-verification (no game launch) of the twelve identities that follow batch V in the survey-2 unscheduled list (fiery orc wyrmic, icy orc wyrmic, yaech mindslayer, heavy bone giant, cave bear, war bear, grannor'vin, rotting mummy, banshee, giant fire ant, giant ice ant, giant lightning ant) against game/modules/tome source and native sprites. Every field below was read from source: name, type/subtype, define_as (the two orc wyrmics bind ORC_FIRE_WYRMIC and ORC_ICE_WYRMIC; the other ten have none), explicit or NPC.lua:33 default image, unique, PNG on disk, and absence of moddable_tile/shader/anim/add_displays on each leaf and its base. Findings: eleven identities are 64x64 single images (bears, banshee and the three ants name their PNG with image=; the wyrmics, mindslayer, grannor'vin and rotting mummy use the NPC.lua:33 default-name image); the heavy bone giant is a non-unique native-tall body (nice_tile image=invis.png with one explicit add_mos display_h=2, display_y=-1) with native_tall=true.",
          'new_ids_not_in_catalog_before_this_batch': [i['id'] for i in identities], 'identities': identities,
          'runtime_mutation_scan': {
              'method': "every talent of each identity (resolvers.talents, inherited base talents, racial levelup talents via resolvers.racial and the base-file talent lists) was resolved under game/modules/tome/data/talents and its mode read (sustained/activated/passive); the whole talents/, timed_effects/, birth/ and class/ trees were grepped for writes to type/subtype/image/add_mos/add_displays/moddable_tile/replace_display/shader (regex on any receiver, plus the tuple assignment form) and the results reviewed line by line, giving the same writer set as batches S, T, U and V; the resolvers sustains_at_birth, racial, inscriptions, equip, auto_equip_filters and nice_tile and the base-file resolvers were read; every auto_classes site under zones/, general/ and maps/ was grepped for Corruptor and Flame of Urh'Rok.",
              'writers_found': [
                  {'file': 'game/modules/tome/data/talents/corruptions/shadowflame.lua', 'line': 97, 'talent': "Flame of Urh'Rok", 'effect': 'sustain: __old_type={type,subtype}; type,subtype = demon,major; image untouched; restored on deactivate'},
                  {'file': 'game/modules/tome/data/talents/psionic/thought-forms.lua', 'line': 93, 'talent': 'thought-form summons (Solipsist tree)', 'effect': 'sets type/subtype/image/moddable_tile/add_mos on the summoned minion copied from its summoner, never on the caster'},
                  {'file': 'game/modules/tome/data/talents/chronomancy/anomalies.lua', 'line': 587, 'talent': 'anomaly summons', 'effect': 'creates a separate spawned NPC with another image; not the caster'}],
              'other_hits_reviewed': [
                  'talents/psionic/mentalism.lua:196 (party-member record for a Projection clone, sets the party subtype only)', 'talents/psionic/dream-forge.lua:135 and talents/celestial/twilight.lua (terrain objects)',
                  'talents/spells/golemancy.lua:152 and talents/uber/mag.lua:396 (golem and lich player display)', 'talents/chronomancy/timeline-threading.lua:342 (clears a shader on a clone)',
                  'timed_effects/physical.lua and other.lua (add_displays/replace_display only while the effect is active)', 'timed_effects/magical.lua:4812 ff. (Lord of Skulls replace_display on a renamed bone-giant minion)', 'class/FortressPC.lua (the Fortress player)'],
              'timed_effects_review': "timed_effects write shader, replace_display, add_displays or image only while active (invisibility shaders, stone/ice/pin displays, Wrathroot, Shivgoroth form, dragon egg, Lord of Skulls): the matcher rejects them (native art) until they end; none is applied at birth to these identities.",
              'sustains_at_birth_review': [
                  {'identity': 'banshee', 'sustained': ['Blur Sight'], 'note': 'started by the base BASE_NPC_GHOST resolvers.sustains_at_birth(); a phantasm_shield particle and temporary values only, no type/subtype/image/add_mos/shader write'},
                  {'identity': "grannor'vin", 'sustained': ['Call Shadows'], 'note': 'the leaf calls resolvers.sustains_at_birth(); a rotating shield particle and shadow summons (separate actors), no display field on the caster'},
                  {'identity': 'fiery orc wyrmic, icy orc wyrmic, yaech mindslayer, heavy bone giant, cave bear, war bear, rotting mummy, giant fire ant, giant ice ant, giant lightning ant', 'sustained': [], 'note': 'no sustains_at_birth on the leaf or base (Icy Skin, Kinetic Aura, Charged Aura and Kinetic Shield are known but never started at birth)'}],
              'auto_classes_review': [
                  {'identity': 'all twelve', 'class': 'none', 'finding': "none of the twelve leaves or their bases has auto_classes; the only auto_classes in the ancient-elven-ruins npc file belong to the boss leaf before the mummies, and the zone-wide grep for Corruptor and Flame of Urh'Rok found only zones/rhaloren-camp, ruins-kor-pul, dreadfell, mark-spellblaze, sandworm-lair, general/events/cultists.lua and general/npcs/elven-caster.lua (already-mapped identities or other names).", 'outcome': "no hit: Flame of Urh'Rok is not reachable, so urh_rok_form is NOT set on any entry; the opt-in count stays 5."}],
              'visibility_review': 'Every identity with inscriptions (orcs, mummy, yaech) can roll an invisibility rune/infusion that applies a transient invis_edge shader through timed effects; the banshee has base stealth; the overlay already respects actor visibility and the transient shader rejects the token (native art) until it ends. No identity changes display at birth.',
              'hits_in_batch': [],
              'no_hit': [i['native_name'] for i in identities]},
          'summons_and_same_body_copies': {
              'method': "grep of every actor definition, static map, quest script, vault, encounter, event and talent under game/modules/tome (data and class) for the twelve names and PNGs; talents that build summons/copies (summon-*, master-of-flesh, master-of-bones, rot, thought-forms, simulacra/mirror images, Grand Arrival, cloneFull users) checked for copies of these bodies.",
              'findings': findings},
          'name_collisions_checked': [
              {'name': a['name'], 'other_definitions': ['none'], 'outcome': ('single actor definition bound to define_as ' + a['define_as'] if a['define_as'] else 'single actor definition without define_as; the catalog entry has no define_as and matches by exact name, type and subtype')} for a in {x['id']: x for x in A}.values() if a['id'] != 'heavy-bone-giant'] + [
              {'name': 'heavy bone giant', 'other_definitions': ['Necromancer Assemble minion table entry talents/spells/master-of-bones.lua:429 (same name, type, subtype and nice_tile body, no define_as)'], 'outcome': 'the zone leaf is the catalog body; the minion is the same body and wears the same token through the ordinary key'}],
          'kept_native': [],
          'neighbours_kept_native': [
              {'name': 'ruin banshee', 'reason': 'other name and PNG, not selected'},
              {'name': 'Lord of Skulls (bone giant) minion', 'reason': 'renamed by the talent; leaves the exact-name key'},
              {'name': 'giant acid ant', 'reason': 'not selected: four-way tie at 4.8 for the last three slots; ant.lua source order (fire, ice, lightning, acid) drops the acid ant, a black-and-yellow ant that would also be a dark subject'},
              {'name': 'giant army ant', 'reason': 'not selected (4.4)'}]}
    out = ADDON / 'evidence/monster-batch-w-20260930/source-contracts.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(ev, indent=2, ensure_ascii=False) + '\n')
    evsha = hashlib.sha256(out.read_bytes()).hexdigest()
    for a in A:
        refs = [{'path': p, 'sha256': sha(p), 'role': r, 'note': n} for r, p, n in a['refs']]
        entry = {'asset_id': a['id'], 'native_name': a['name'], 'scope': a['scope'], 'sources': a['srcs'], 'references': refs,
                 'contrast_dimensions': list(a['dims']),
                 'prompt_fields': {'subject': a['subject'], 'contrast': a['contrast'], 'composition': a['comp'] or COMP, 'palette': a['palette']},
                 'kind': 'creature', 'max_attempts': 1, 'gate': 'ready',
                 'gate_reason': f"Exact source identity re-verified directly against game/modules/tome source (name={a['name']}, define_as={a['define_as']}, type={a['type']}/subtype={a['subtype']}, unique={a['unique']}, native_tall={a['native_tall']}); details and hashes in evidence/monster-batch-w-20260930/source-contracts.json. {a['structure']}. Exact catalog entry only, never a whole-subtype mapping.",
                 'render_evidence': [{'path': render, 'sha256': evsha}]}
        packs.setdefault(a['pack'], []).append(entry)
    for n, assets in packs.items():
        p = ADDON / f'art/production/batches/monster-batch-w-{n}.json'
        if p.exists():
            print('exists, skipped', p.name)
            continue
        p.write_text(json.dumps({'schema': 1, 'batch_id': f'monster-batch-w-{n}', 'assets': assets}, indent=2, ensure_ascii=False) + '\n')
        print('wrote', p.name)


if __name__ == '__main__':
    build()
