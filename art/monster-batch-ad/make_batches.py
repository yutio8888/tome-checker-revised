"""Generate the monster-batch-ad task packs and the pinned source-contract
evidence (survey 'final.tsv' class-a rows: the first off-list dungeon-pool batch:
duathedlen, daelach, orc grand summoner, orc master wyrmic, orc mage-hunter,
ritch larva, ritch hunter, ritch hive mother, snow cat, panther, tiger, sabertooth
tiger, ice wyrm; see SELECTION.md). Pure bookkeeping: hashes native sources/sprites,
writes JSON and the composite family references. Retry packs are appended by
later edits of retries.py (never overwritten)."""
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
REFS = HERE / 'refs'
ART_REL = 'game/addons/tome-checker-revised/art/monster-batch-ad/'
DARKFIX = " DARK-SUBJECT DISCIPLINE (the native art of this creature is almost black; earlier near-black tokens were rejected at 48px): render it in MID-LIGHT slate and ash values, never black, at least as light as the copper-grey bevel of the disc and clearly lighter than the charcoal plate, with a thin bright pale RIM LIGHT along the whole upper-left outline and bright accent patches (named in the brief) so that the silhouette reads as a light shape on the dark disc at 48 pixels."


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


MOD = ' no moddable_tile, shader, anim or add_displays on the leaf or base; native sprite 64x64; non-unique'
CATS = ' Draw the whole creature as ONE compact upright figure filling the disc; never a tall canvas.'
def tall_explicit(png):
    return ' resolvers.nice_tile{image="invis.png", add_mos={{image="npc/%s.png", display_h=2, display_y=-1}}} names the tall PNG explicitly (keys image/display_h/display_y only; with nicer_tiles off nice_tile is a no-op and the single image is used); no moddable_tile, shader, anim or add_displays; native sprite 64x128; non-unique with no define_as, so the catalog entry carries native_tall=true' % png


HAQ = 'general/npcs/horror_aquatic.lua'


def tall_short(png):
    return (' resolvers.nice_tile{tall=1} on the leaf (no image= on the leaf or base, so NPC.lua:33 default-name image ' + png + ' is used; the resolver expands to invis.png + one add_mos entry {image=e.image, display_h=2, display_y=-1}, the same live-confirmed shorthand as the ogre guard, mauler and pounder; with nicer_tiles off it is a no-op and the default-name image is the single path); no moddable_tile, shader, anim or add_displays; native sprite 64x128; non-unique with no define_as, so the catalog entry carries native_tall=true')


GHO = 'general/npcs/ghost.lua'
VOR = 'general/npcs/orc-vor.lua'
DRE = 'zones/dreadfell/npcs.lua'
RSP = 'zones/rak-shor-pride/npcs.lua'
CVN = 'zones/conclave-vault/npcs.lua'
HOR = 'general/npcs/horror.lua'
SPI = 'general/npcs/spider.lua'
VAM = 'general/npcs/vampire.lua'
GHL = 'general/npcs/ghoul.lua'
BGI = 'general/npcs/bone-giant.lua'
WIG = 'general/npcs/wight.lua'
OGR = 'general/npcs/ogre.lua'

DEFC = ' NPC.lua:33 default-name image (npc/<type>_<subtype>_<name>.png) is the only image source: no image=, nice_tile, add_mos, moddable_tile, shader, anim or add_displays on the leaf or base; generic actor.image==entry.image single path; native sprite 64x64'
DEFD = ' define_as-bound entry: the catalog entry carries define_as and the matcher rejects any actor with another (or no) define_as'
DEFU = ' UNIQUE: the catalog entry carries unique=true, so an unknown unique of the same shape is only accepted when it is this exact define_as-bound leaf'


def tall_unique(png):
    return (' resolvers.nice_tile{image="invis.png", add_mos={{image="npc/%s.png", display_h=2, display_y=-1}}} names the tall PNG explicitly (keys image/display_h/display_y only; with nicer_tiles off nice_tile is a no-op and the default-name image is the single path); no moddable_tile, shader, anim or add_displays; native sprite 64x128; UNIQUE with a define_as binding, so nativeTallImage accepts the tall body through the unique path (like the Hedge-Wizard, Kyless and Walrog) and the entry carries unique=true and define_as but no native_tall flag' % png)



CHEAT = ' Every surface of the figure is painted as SOLID OPAQUE material (no see-through, faded or translucent parts, no alpha gradients inside the figure).'
GOR = 'general/npcs/orc-gorbat.lua'
MDM = 'general/npcs/major-demon.lua'
FEL = 'general/npcs/feline.lua'
RIT = 'general/npcs/ritch.lua'
CDR = 'general/npcs/cold-drake.lua'
DUA = 'dúathedlen'

DUATH_FALLBACK = ' NOTE: the default-name image of this leaf would be npc/demon_major_d__athedlen.png (NPC.lua:33 replaces each byte of the UTF-8 u-acute with an underscore and no such PNG exists), so with nicer_tiles OFF the actor.image never equals the catalog image and the token is simply not applied (native behaviour stays); with nicer_tiles ON (the default) the explicit nice_tile body matches through the native-tall path'

# ---- family references built from shipped runtime tokens ----
REF_ORC_PRIDE = RC('orc-pride', ['orc-summoner', 'fiery-orc-wyrmic', 'icy-orc-wyrmic', 'orc-berserker', 'orc-elite-fighter', 'orc-necromancer'], 3,
                   'Six shipped orc tokens (the orc summoner: a green beast-shaman with antlers and a teal-cyan swirl; the fiery orc wyrmic: a red-orange armoured axe orc; the icy orc wyrmic: a white-and-ice-blue armoured axe orc; the orc berserker: a spiked silver-brown axe orc; the orc elite fighter: a gold-and-blue plate fighter with a tower shield; the orc necromancer: a dark-robed caster): the ORC GRAND SUMMONER is a bare-chested BEASTMASTER in earth-tone hides and a fur-and-bone mantle, a bone-white python and a green viper coiled around his body and a totem staff topped with a tusked skull, no glow; the ORC MASTER WYRMIC is a bronze-and-sand-gold DRAKE-SCALE armoured orc in a dragon-head helm with four differently coloured drake-scale pauldrons (crimson, ice-blue, sand-gold, storm-violet) and a huge single-bladed battleaxe; the ORC MAGE-HUNTER is a fully ENCLOSED bulky pale blue-steel and silver armoured orc with a great helm whose visor slit glows turquoise, a big round shield with concentric rings and a waraxe; none of them is a teal-aura antlered shaman, a red or white axe orc, a spiked berserker, a gold-blue shield fighter or a dark robed caster.')
REF_RITCH = RC('ritches', ['ritch-flamespitter', 'ritch-impaler', 'chitinous-ritch', 'ritch-hive-mother'], 2,
               'Four shipped ritch tokens (the flamespitter: an orange scorpion-like ritch with a flaming tail; the impaler: a tan ritch with a long spike; the chitinous ritch: a golden turtle-shelled ritch; the Ritch Great Hive Mother: a big brick-red clawed ritch): the RITCH LARVA is a plump pale BUTTER-YELLOW segmented GRUB curled into a C shape with tiny black legs and small head spikes, no claws; the RITCH HUNTER is a sleek SLATE-INDIGO wasp-like ritch with orange zig-zag stripes, a hooked horn crest and blade-like forelegs, upright and lean; the RITCH HIVE MOTHER is a large crimson-rust matriarch with big pincers, one huge amber compound eye and a swollen banded amber-and-black egg-laden ABDOMEN dragging behind; none of them is an orange scorpion, a tan spiked impaler, a golden turtle or the plain brick-red clawed Great Hive Mother.')
REF_CATS = RC('felines', ['pumpkin', 'white-wolf', 'dire-wolf', 'wolf', 'polar-bear', 'great-wolf'], 3,
              'Six shipped animal tokens (Pumpkin: a fat orange tabby sitting front-on; the white wolf: a low white wolf; the dire wolf: a brown prowling wolf; the wolf, the polar bear and the great wolf): the four big cats are a set of distinct POSES as well as colours: the SNOW CAT sits in a tight round crouch with a thick ringed tail wrapped around its body, snow-white coat with grey rosettes; the PANTHER is a long low sleek stalking body stretched diagonally with an S-curved tail, indigo-blue coat; the TIGER is a mid-stride roaring orange-and-black striped cat with one forepaw raised and the tail curled up; the SABERTOOTH TIGER is a bulky heavy-shouldered ash-grey smilodon seen nearly head-on with two long ivory fangs and a short bobbed tail; none of them is a tabby sitting front-on, a wolf or a bear.')
REF_WYRMS = RC('wyrms', ['cold-drake', 'fire-wyrm', 'venom-wyrm', 'rantha', 'storm-drake', 'fire-drake'], 3,
               'Six shipped dragon tokens (the cold drake: a teal-blue crouching drake; the fire wyrm: a red serpentine coiled wyrm; the venom wyrm: a green coiled wyrm; Rantha the Worm: a grey-blue winged worm; the storm drake and the fire drake): the ICE WYRM is a serpentine wyrm coiled into a compact spiral under a raised horned head, silver-white and deep cobalt scales, a crest of translucent-pale ice-crystal spines down the neck and back, the two bat-like wings folded tight against the body; it is not a crouching teal drake, not a red or green coiled wyrm and not a grey-blue worm.')
REF_DEMONS = RC('major-demons', ['dolleg', 'uruivellas', 'thaurhereg', 'kryl-feijan', 'lithfengel', 'harkor-zun'], 3,
                'Six shipped major demon tokens (Dolleg: a red thorned demon; Uruivellas: a flame-wreathed horned bull; Thaurhereg: a thin red spiked demon; Kryl-Feijan; Lithfengel: a grey smoke ghost with red eyes; Harkor\'Zun): the DUATHEDLEN is a lean horned demon made of pale ASH-LAVENDER and slate-violet shadow with glowing red eyes and red cracks, drifting ragged shadow tendrils and a red-lit open palm; the DAELACH is an armoured horned demon half-emerging from a rolling cloud of dark PLUM smoke veined with magenta and orange shadow-flame, a longsword in one hand and a waraxe in the other; neither is a red thorned demon, a flaming bull or a plain grey smoke ghost.')

DISCCAL = " CALIBRATION FROM EARLIER TOKENS (first generations failed the disc-geometry and base-lightness gates because arms, weapons, tails and effects crossed the rim or the body shaded the plate): draw the whole creature clearly SMALLER than feels natural, everything inside a circle of about 0.55 of the disc radius, centred, with a wide bare ring of plate on every side; hold every weapon, limb, tail, wing and effect tight against the body; render the WHOLE disc, its outer ring band and the plate under and around the creature, at exactly the style reference lightness or a hair lighter, evenly all round, with no cast shadow, contact shadow or darkening beside the creature."
ALLC = COMP + FIT + COMPACT + BRIGHT + DISCCAL
DARKC = COMP + FIT + COMPACT + BRIGHT + DARKFIX + DISCCAL


def tall_d(png, extra=''):
    return tall_explicit(png) + extra


# ---- pack 1: dUathedlen, daelach, ice wyrm, snow cat (tall native bodies) ----
asset(1, 'duathedlen', DUA,
      "dungeon pool (general/npcs/major-demon.lua:73, demon/major, non-unique, no define_as, rank 2, base BASE_NPC_MAJOR_DEMON, explicit tall nice_tile body); the only definition of this name",
      [src(MDM, 'name = "%s"' % DUA), src(MDM, 'resolvers.nice_tile', after='name = "%s"' % DUA), src(MDM, 'T_BLOOD_GRASP', after='name = "%s"' % DUA), src(MDM, 'define_as = "BASE_NPC_MAJOR_DEMON"')],
      src(MDM, 'define_as = "BASE_NPC_MAJOR_DEMON"'), None, 'demon', 'major', False, True,
      'base BASE_NPC_MAJOR_DEMON (demon/major, no image=, no shader, resolvers.inscriptions(1, "rune") only picks runes);' + tall_d('demon_major_duathedlen', DUATH_FALLBACK) + '; the leaf calls neither sustains_at_birth nor equip; Darkness and Blood Grasp are activated talents; no auto_classes',
      'demon_major_duathedlen.png',
      [STY, IDN('demon_major_duathedlen.png', 'Native shape (64x128, tall): an almost black lean horned demon wreathed in a cloud of darkness, with two red eyes and red hands. Keep the lean horned shadow-demon with red eyes and red-lit hand, drawn as ONE compact figure filling the disc, no tall canvas, rendered in pale ash-lavender and slate-violet so it reads as a light shape on the dark disc, clearly not the red thorned demons.'), REF_DEMONS],
      "A duathedlen (darkness exiled) seen from a steep overhead three-quarter angle: a lean, tall-limbed HORNED DEMON standing in a slight hunch on the disc, its body made of pale ASH-LAVENDER and slate-violet shadow-flesh with a few glowing RED cracks across the chest and ribs, a narrow horned skull-like head with two swept-back curved horns and two glowing red eyes, long thin arms, one claw hand held forward with a small glowing RED orb of blood-light in the open palm, ragged drifting tendrils of pale grey-lilac shadow curling off the shoulders and hips (kept close to the body and pale, never dark smoke); broad pale highlight planes on every upper-left surface and a thin bright rim light. Horned, red-eyed, lavender and complete." + CHEAT,
      "Major demons: the DUATHEDLEN is the LEAN HORNED SHADOW-DEMON of pale ash-lavender and slate-violet with red eyes, red cracks and a red-lit palm (silhouette: a thin upright figure with two curved horns, long arms and trailing shadow wisps; hue: ash-lavender, violet-grey and red accents; value: mid-light). The shipped Dolleg is a red thorned brute, Uruivellas a flame-wreathed bull, Thaurhereg a thin red spiked demon and Lithfengel a grey smoke ghost: this must not be red, must not be thorned, must not be a bull and must not be a formless smoke cloud.",
      "Ash-lavender and slate-violet body, pale grey-lilac shadow wisps, glowing red eyes and red cracks, a thin bright rim; nothing darker than mid slate-violet except the eye sockets and cracks; NO black body, no black smoke; the red glow stays on the figure and must not tint the disc, which stays neutral charcoal at reference lightness." + DISC,
      "READY tall non-unique (duathedlen, native_tall via explicit nice_tile)", comp=DARKC + CATS)

asset(1, 'daelach', 'daelach',
      "dungeon pool (general/npcs/major-demon.lua:162, demon/major, non-unique, no define_as, rank 3, base BASE_NPC_MAJOR_DEMON, explicit tall nice_tile body); the only definition of this name (the unique Corrupted Daelach of valley-moon is a different name, define_as and PNG and is not part of this batch)",
      [src(MDM, 'name = "daelach"'), src(MDM, 'resolvers.nice_tile', after='name = "daelach"'), src(MDM, 'T_TWILIGHT_SURGE', after='name = "daelach"'), src(MDM, 'resolvers.equip', after='name = "daelach"'), src(MDM, 'define_as = "BASE_NPC_MAJOR_DEMON"')],
      src(MDM, 'define_as = "BASE_NPC_MAJOR_DEMON"'), None, 'demon', 'major', False, True,
      'base BASE_NPC_MAJOR_DEMON (demon/major, no image=, no shader);' + tall_d('demon_major_daelach') + '; resolvers.equip a longsword and a waraxe (equipment only, no moddable_tile); the leaf has no sustains_at_birth of its own and its talents are activated or passive; no auto_classes',
      'demon_major_daelach.png',
      [STY, IDN('demon_major_daelach.png', 'Native shape (64x128, tall): a tall billowing cloud of black smoke and dark fire with no visible body. Keep the billowing shadow-flame cloud, but draw it as ONE compact mass filling the disc with an armoured horned demon half-emerging from it carrying a longsword and a waraxe (the demon holds the two weapons it really wields), rendered in plum-violet and lavender smoke with bright magenta and orange shadow-flame, clearly not the grey smoke ghost or the red demons.'), REF_DEMONS],
      "A daelach (shadow flame) seen from a steep overhead three-quarter angle: a rolling compact CLOUD of PLUM-VIOLET and lavender smoke hovering over the disc, veined with bright MAGENTA and ember-ORANGE shadow-flame flickering along its edges, and emerging from the front of the cloud a broad-shouldered ARMOURED HORNED DEMON torso in dark-violet plate with pale lavender highlights, two thick curved horns, two burning orange eyes, a bright steel LONGSWORD in one hand and a bright steel WARAXE in the other, both held in close; broad pale highlight planes on every upper-left surface and a thin bright rim light. Smoking, horned, armed and complete." + CHEAT,
      "Major demons: the DAELACH is the ROLLING PLUM SMOKE-AND-FLAME CLOUD with a horned armoured demon and two weapons half-emerging (silhouette: a rounded cloud mass with a horned head and a blade on each side; hue: plum-violet, lavender, magenta and orange flame; value: mid-light). The shipped Lithfengel is a thin grey smoke ghost with red eyes, Dolleg and Thaurhereg red brutes and Uruivellas a flaming bull: this must not be grey, must not be a bare ghost and must show the armoured demon with sword and axe.",
      "Plum-violet and lavender smoke, pale lavender plate highlights, magenta and ember-orange flame edges, steel weapons, orange eyes, a thin bright rim; nothing darker than mid plum except the eye sockets and seams; NO black smoke mass, no black armour; the flame glow stays on the figure and must not tint the disc, which stays neutral charcoal at reference lightness." + DISC,
      "READY tall non-unique (daelach, native_tall via explicit nice_tile)", comp=DARKC + CATS)

asset(1, 'ice-wyrm', 'ice wyrm',
      "dungeon pool (general/npcs/cold-drake.lua:89, dragon/cold, non-unique, no define_as, rank 3, base BASE_NPC_COLD_DRAKE, explicit tall nice_tile body); the only definition of this name; the vaults frost-dragon-lair, sleeping-dragons and renegade-wyrmics pick it by name/random_filter (the same leaf)",
      [src(CDR, 'name = "ice wyrm"'), src(CDR, 'resolvers.nice_tile', after='name = "ice wyrm"'), src(CDR, 'T_ICE_BREATH', after='name = "ice wyrm"'), src(CDR, 'define_as = "BASE_NPC_COLD_DRAKE"')],
      src(CDR, 'define_as = "BASE_NPC_COLD_DRAKE"'), None, 'dragon', 'cold', False, True,
      'base BASE_NPC_COLD_DRAKE (dragon/cold, no image=, no shader);' + tall_d('dragon_cold_ice_wyrm') + '; no equip, no sustains_at_birth; Ice Claw and Ice Breath are activated and Icy Skin is a sustained defensive buff (temporary values and particles); no auto_classes',
      'dragon_cold_ice_wyrm.png',
      [STY, IDN('dragon_cold_ice_wyrm.png', 'Native shape (64x128, tall): a large deep-blue serpentine wyrm with big spread bat wings, a horned head and a coiled body. Keep the big blue wyrm with horned head and wings, drawn as ONE compact coiled figure filling the disc, no tall canvas, wings folded tight, in silver-white and cobalt with pale ice-crystal spines, clearly not the teal cold drake.'), REF_WYRMS],
      "An ice wyrm seen from a steep overhead three-quarter angle: a serpentine ICE WYRM coiled into a compact SPIRAL on the disc with its long horned head raised at the front, SILVER-WHITE belly plates and deep COBALT-BLUE scales on the back, a ridge of translucent PALE ICE-CRYSTAL SPINES running down the neck and back, two large curved horns swept back, pale blue glowing eyes, both bat-like wings FOLDED TIGHT against its flanks with pale blue membranes and white frost-rimed wing fingers, clawed forelegs gripping the coil, a thin wisp of white frost breath at the open jaws kept close; broad pale highlight planes on every upper-left surface and a thin bright rim light. Coiled, crystalled, horned and complete." + CHEAT,
      "Dragons: the ICE WYRM is the COILED SERPENTINE silver-white and cobalt wyrm with ice-crystal spines, swept horns and tightly folded wings (silhouette: a spiral coil topped by a raised horned head with a crest of spikes; hue: silver-white, cobalt blue and pale ice-blue; value: light with mid-blue scales). The shipped cold drake is a crouching teal-blue drake with open wings, the fire wyrm a red coil, the venom wyrm a green coil and Rantha a grey-blue winged worm: this must not be teal, must not crouch on four legs with open wings and must carry a crystalline spine crest.",
      "Silver-white plates, cobalt-blue scales, pale translucent ice-blue crystals, pale blue eyes and wing membranes, a thin bright rim; nothing darker than mid cobalt except the eye sockets and scale seams; NO navy-black body; the frost stays on the figure and must not tint the disc, which stays neutral charcoal at reference lightness." + DISC,
      "READY tall non-unique (ice wyrm, native_tall via explicit nice_tile)", comp=ALLC + CATS)

asset(1, 'snow-cat', 'snow cat',
      "dungeon pool (general/npcs/feline.lua:40, animal/feline, non-unique, no define_as, rank 2, base BASE_NPC_CAT, explicit tall nice_tile body); the only definition of this name; the vaults forest-ruined-building3 and snake-pit pick it by name",
      [src(FEL, 'name = "snow cat"'), src(FEL, 'resolvers.nice_tile', after='name = "snow cat"'), src(FEL, 'T_LETHALITY', after='name = "snow cat"'), src(FEL, 'define_as = "BASE_NPC_CAT"'), src(FEL, 'resolvers.sustains_at_birth()')],
      src(FEL, 'define_as = "BASE_NPC_CAT"'), None, 'animal', 'feline', False, True,
      'base BASE_NPC_CAT (animal/feline, no image=, no shader; calls resolvers.sustains_at_birth());' + tall_d('animal_feline_snow_cat') + '. The native source line sets nice_tile image="invis.png" only as the tall-body mechanism (the same as dolleg, uruivellas and thaurhereg): with nicer_tiles on the body is the add_mos entry; with nicer_tiles off the default-name image animal_feline_snow_cat.png is used directly, and both paths are covered; Stealth is the only sustained talent (hides the actor, no image or shader write for a non-moddable cat; the matcher already rejects an actor carrying a shader); no auto_classes',
      'animal_feline_snow_cat.png',
      [STY, IDN('animal_feline_snow_cat.png', 'Native shape (64x128, tall canvas): a snow-white and grey rosette-coated large cat crouched low with a bushy ringed tail and amber eyes. Keep the snow leopard: pale grey-white coat with darker grey rosette spots and a thick ringed tail, drawn as ONE compact round crouching figure filling the disc, no tall canvas, clearly not a white wolf or a tabby.'), REF_CATS],
      "A snow cat seen from a steep overhead three-quarter angle: a large SNOW LEOPARD sitting in a tight ROUND CROUCH on the disc, dense thick pale grey-white fur with clear DARK-GREY ROSETTE spots on the back and flanks, a broad round head turned toward the viewer with white cheek ruffs, pale AMBER eyes and a pink nose, small rounded ears, big fluffy forepaws tucked under the chest, and a thick bushy TAIL with dark grey rings wrapped around the front of the body; broad pale highlight planes on every upper-left surface and a thin bright rim light. Round, rosetted, ringed-tail and complete." + CHEAT,
      "Felines: the SNOW CAT is the ROUND CROUCHING snow leopard with grey rosettes, cheek ruffs and a thick ringed tail wrapped around its body (silhouette: a compact rounded mound with a round head and a wrapped tail; hue: pale grey-white with dark grey rosettes and amber eyes; value: very light). The other three big cats are a long low stalking panther, a mid-stride roaring tiger and a bulky fanged sabertooth, and the shipped Pumpkin is a fat orange tabby sitting front-on and the white wolf a low white wolf: this must not be orange, must not be a wolf and must not be long and stalking.",
      "Pale grey-white fur, dark grey rosettes and tail rings, pink nose, amber eyes, a thin bright rim; nothing darker than mid grey except the rosettes and eye slits; the disc stays neutral charcoal at reference lightness, not lightened under the white fur." + DISC,
      "READY tall non-unique (snow cat, native_tall via explicit nice_tile invis.png body)", comp=ALLC + CATS)

# ---- pack 2: panther, tiger, sabertooth tiger ----
asset(2, 'panther', 'panther',
      "dungeon pool (general/npcs/feline.lua:57, animal/feline, non-unique, no define_as, rank 2, base BASE_NPC_CAT, default-name image); the only definition of this name",
      [src(FEL, 'name = "panther"'), src(FEL, 'T_STEALTH', after='name = "panther"'), src(FEL, 'define_as = "BASE_NPC_CAT"'), src(FEL, 'resolvers.sustains_at_birth()')],
      src(FEL, 'define_as = "BASE_NPC_CAT"'), None, 'animal', 'feline', False, False,
      'base BASE_NPC_CAT (animal/feline, no image=, no shader; calls resolvers.sustains_at_birth());' + DEFC + '; Stealth is the only sustained talent (hides the actor; no image or shader write for a non-moddable cat); no equip, no auto_classes',
      'animal_feline_panther.png',
      [STY, IDN('animal_feline_panther.png', 'Native shape (64x64): a sleek deep indigo-black panther in a low stalking prowl with a long curling tail and yellow eyes. Keep the long low sleek stalking panther with an S-curved tail, drawn as ONE compact figure filling the disc, but rendered in mid-light indigo-blue and slate with pale lavender highlights (never black) and bright yellow eyes.'), REF_CATS],
      "A panther seen from a steep overhead three-quarter angle: a sleek muscular PANTHER in a low STALKING PROWL, its long body stretched diagonally across the disc with the head lowered forward and one front paw lifted mid-step, a long tail in a gentle S-curve behind, coat of glossy mid-light INDIGO-BLUE and slate-violet with broad pale LAVENDER highlight planes along the spine, shoulder and haunch, a pale lavender rim light along the whole upper-left outline, bright YELLOW-GREEN eyes and a pale pink nose, lighter slate-blue paw pads. Sleek, stalking, indigo and complete." + CHEAT,
      "Felines: the PANTHER is the LONG LOW STALKING indigo cat with an S-curved tail stretched diagonally (silhouette: a long low diagonal body with a lowered head, one lifted paw and an S tail; hue: indigo-blue and slate-violet with lavender highlights and yellow-green eyes; value: mid-light). The snow cat is a white rounded crouch, the tiger an orange roaring striped cat and the sabertooth a bulky fanged grey cat, and the shipped wolves are not cats: this must not be orange, white or grey-striped and must be long and low rather than round.",
      "Mid-light indigo-blue and slate-violet coat, pale lavender highlights and rim, yellow-green eyes, pale pink nose; nothing darker than mid slate-blue except the eye slits and claw seams; NO black fur, no black cat; the disc stays neutral charcoal at reference lightness and clearly darker than the coat highlights." + DISC,
      "READY single, no define_as (panther)", comp=DARKC + CATS)

asset(2, 'tiger', 'tiger',
      "dungeon pool (general/npcs/feline.lua:73, animal/feline, non-unique, no define_as, rank 2, base BASE_NPC_CAT, default-name image); the only definition of this name",
      [src(FEL, 'name = "tiger"'), src(FEL, 'T_SHADOW_DANCE', after='name = "tiger"'), src(FEL, 'define_as = "BASE_NPC_CAT"'), src(FEL, 'resolvers.sustains_at_birth()')],
      src(FEL, 'define_as = "BASE_NPC_CAT"'), None, 'animal', 'feline', False, False,
      'base BASE_NPC_CAT (animal/feline, no image=, no shader; calls resolvers.sustains_at_birth());' + DEFC + '; Stealth is the only sustained talent at birth (hides the actor; no image or shader write for a non-moddable cat), Shadow Dance is activated; no equip, no auto_classes',
      'animal_feline_tiger.png',
      [STY, IDN('animal_feline_tiger.png', 'Native shape (64x64): a golden-orange tiger with black stripes, low to the ground, white muzzle, mouth open. Keep the orange black-striped tiger with a white muzzle and open jaws, drawn as ONE compact figure filling the disc, in a mid-stride roaring pose with one forepaw raised and the tail curled up, clearly not the long low indigo panther.'), REF_CATS],
      "A tiger seen from a steep overhead three-quarter angle: a powerful TIGER caught in a mid-stride ROAR on the disc, head turned toward the viewer with the mouth wide open showing ivory fangs and a pink tongue, one front paw RAISED, bright GOLDEN-ORANGE coat with bold black tapered stripes, a white muzzle, white chest and belly, white cheek ruffs and white-ringed amber eyes, and a thick striped tail curled UP over the haunch; broad pale highlight planes on every upper-left surface and a thin bright rim light. Striped, roaring, raised-paw and complete." + CHEAT,
      "Felines: the TIGER is the MID-STRIDE ROARING golden-orange black-striped cat with one raised paw and an upcurled tail (silhouette: a chunky forward-facing body with an open mouth, a raised paw and a curled tail; hue: golden-orange, black stripes and white; value: bright). The snow cat is a white rounded crouch, the panther a long low indigo stalker and the sabertooth a bulky grey fanged cat, and the shipped Pumpkin is a plain orange tabby sitting front-on: this must not be solid-coloured, must not be sitting and must roar with bold black stripes.",
      "Golden-orange coat, bold black stripes, white muzzle, chest and cheek ruffs, ivory fangs, pink tongue, a thin bright rim; nothing darker than the stripes themselves; the disc stays neutral charcoal at reference lightness." + DISC,
      "READY single, no define_as (tiger)", comp=ALLC + CATS)

asset(2, 'sabertooth-tiger', 'sabertooth tiger',
      "dungeon pool (general/npcs/feline.lua:90, animal/feline, non-unique, no define_as, rank 2, base BASE_NPC_CAT, default-name image); the only definition of this name",
      [src(FEL, 'name = "sabertooth tiger"'), src(FEL, 'T_CRIPPLE', after='name = "sabertooth tiger"'), src(FEL, 'define_as = "BASE_NPC_CAT"'), src(FEL, 'resolvers.sustains_at_birth()')],
      src(FEL, 'define_as = "BASE_NPC_CAT"'), None, 'animal', 'feline', False, False,
      'base BASE_NPC_CAT (animal/feline, no image=, no shader; calls resolvers.sustains_at_birth());' + DEFC + '; Stealth is the only sustained talent at birth (hides the actor; no image or shader write for a non-moddable cat), Cripple is activated; no equip, no auto_classes',
      'animal_feline_sabertooth_tiger.png',
      [STY, IDN('animal_feline_sabertooth_tiger.png', 'Native shape (64x64): a heavy grey-striped big cat with enormous ivory fangs and a short tail. Keep the bulky heavy-shouldered smilodon with two very long ivory fangs and a short bobbed tail, drawn as ONE compact figure filling the disc, seen nearly head-on, clearly not a tiger or a panther.'), REF_CATS],
      "A sabertooth tiger seen from a steep overhead three-quarter angle: a BULKY heavy-shouldered SMILODON crouched and seen nearly HEAD-ON on the disc, a huge broad head with a wrinkled snarling muzzle and TWO VERY LONG IVORY SABRE FANGS hanging far below the jaw, small round ears, pale yellow eyes, a thick muscular neck and massive shoulders, ash-grey and warm tan coat with soft dark-grey vertical stripes, thick short forelegs with big paws planted wide and a short BOBBED stump of a tail; broad pale highlight planes on every upper-left surface and a thin bright rim light. Bulky, fanged, head-on and complete." + CHEAT,
      "Felines: the SABERTOOTH TIGER is the BULKY HEAD-ON ash-grey smilodon with two very long ivory sabre fangs, massive shoulders and a bobbed tail (silhouette: a wide blocky forward-facing mass with two long fangs; hue: ash-grey, warm tan and ivory; value: mid-light). The snow cat is a white rounded crouch with a ringed tail, the panther a long low indigo stalker and the tiger an orange roaring striped cat with a long curled tail: this must not be orange, must not be slender and must show the two huge fangs and a short tail.",
      "Ash-grey and warm tan coat with soft dark-grey stripes, ivory fangs, pale yellow eyes, a thin bright rim; nothing darker than mid grey except the stripes and eye slits; the disc stays neutral charcoal at reference lightness." + DISC,
      "READY single, no define_as (sabertooth tiger)", comp=ALLC + CATS)

# ---- pack 3: three Gorbat-pride orcs ----
ORC_BASE = lambda: src(GOR, 'define_as = "BASE_NPC_ORC_GORBAT"')
ORC_STRUCT = 'base BASE_NPC_ORC_GORBAT (humanoid/orc, faction orc-pride, no image=, no shader);' + DEFC + '; resolvers.racial() only adds orc levelup talents (the racial doll belongs to random bosses, see the evidence); the base calls resolvers.sustains_at_birth() (%s); resolvers.equip %s (equipment only, no moddable_tile); resolvers.inscriptions picks infusions (no display write); no auto_classes'
asset(3, 'orc-grand-summoner', 'orc grand summoner',
      "gorbat-pride and dungeon pool (general/npcs/orc-gorbat.lua:81, humanoid/orc, non-unique, no define_as, rank 3, base BASE_NPC_ORC_GORBAT, default-name image); the only definition of this name; the renegade-wyrmics vault makes a random boss 'Beastmaster #rng#' from it (the existing flat captureRandomOrigin path)",
      [src(GOR, 'name = "orc grand summoner"'), src(GOR, 'T_STONE_GOLEM', after='name = "orc grand summoner"'), src(GOR, 'resolvers.equip', after='name = "orc grand summoner"'), src(GOR, 'resolvers.sustains_at_birth()'), ORC_BASE()],
      ORC_BASE(), None, 'humanoid', 'orc', False, False,
      ORC_STRUCT % ('Psiblades is the only sustained talent and calls updateModdableTile, a no-op display write for a non-moddable actor', 'mindstars, cloth armour and a totem'),
      'humanoid_orc_orc_grand_summoner.png',
      [STY, IDN('humanoid_orc_orc_grand_summoner.png', 'Native shape (64x64): a green orc beastmaster in earth-tone hides with a bone-white serpent draped over one shoulder and a green serpent coiled around a staff. Keep the bare-chested green beastmaster with the two serpents and the serpent staff, drawn as ONE compact figure filling the disc, in earth-tone fur and bone, clearly not the glowing teal antlered orc summoner.'), REF_ORC_PRIDE],
      "An orc grand summoner seen from a steep overhead three-quarter angle: a broad tusked GREEN-skinned orc BEASTMASTER standing on the disc, bare-chested under a heavy mantle of tawny fur and white BONE plates, tribal ochre and umber hide kilt, a big BONE-WHITE PYTHON draped over his shoulders, a bright GREEN VIPER coiled around a short wooden TOTEM STAFF held in one hand topped with a tusked skull, strings of bone beads and claws at the neck, a tall crest of feathers and small antlers on the head; broad pale highlight planes on every upper-left surface and a thin bright rim light. Beastmaster, serpent-wrapped, earthy and complete." + CHEAT,
      "Gorbat-pride orcs: the ORC GRAND SUMMONER is the BARE-CHESTED BEASTMASTER with a fur-and-bone mantle, a white python, a green viper around a skull totem staff and a feather crest (silhouette: a broad figure with a staff topped by a skull and snakes over the shoulders; hue: tawny fur, bone white, ochre and viper green on a green-skinned orc; value: mid-light). The shipped orc summoner is a teal-aura antlered shaman, the fiery and icy wyrmics red and white armoured axe orcs, the berserker a spiked silver-brown axe orc: this must not glow teal, must not be armoured and must carry the snakes and the skull staff.",
      "Tawny fur, bone white plates and python, green viper, ochre-umber hide, green orc skin, feather crest, a thin bright rim; nothing darker than mid umber except the eye slits and seams; NO black hide, no dark cloak; the disc stays neutral charcoal at reference lightness." + DISC,
      "READY single, no define_as (orc grand summoner)", comp=ALLC + CATS)

asset(3, 'orc-master-wyrmic', 'orc master wyrmic',
      "gorbat-pride and dungeon pool (general/npcs/orc-gorbat.lua:114, humanoid/orc, non-unique, no define_as, rank 3, base BASE_NPC_ORC_GORBAT, default-name image); the only definition of this name (the fiery and icy orc wyrmics are other names with their own define_as); the renegade-wyrmics vault makes a random boss 'the Herald' from it (the existing flat captureRandomOrigin path)",
      [src(GOR, 'name = "orc master wyrmic"'), src(GOR, 'T_ICE_BREATH', after='name = "orc master wyrmic"'), src(GOR, 'resolvers.equip', after='name = "orc master wyrmic"'), src(GOR, 'resolvers.sustains_at_birth()'), ORC_BASE()],
      ORC_BASE(), None, 'humanoid', 'orc', False, False,
      ORC_STRUCT % ('Icy Skin is the only sustained talent and is a temporary-value and particle buff; Lightning Speed and the breaths are activated', 'a battleaxe, light armour and a totem'),
      'humanoid_orc_orc_master_wyrmic.png',
      [STY, IDN('humanoid_orc_orc_master_wyrmic.png', 'Native shape (64x64): a horned olive-drab armoured orc holding a big red-bladed axe crosswise, scales and trophies on the armour. Keep the horned armoured orc with a big axe held crosswise, drawn as ONE compact figure filling the disc, but in bronze and sand-gold drake-scale plate with four different coloured drake-scale pauldrons, clearly not the red fiery or white icy wyrmic.'), REF_ORC_PRIDE],
      "An orc master wyrmic seen from a steep overhead three-quarter angle: a broad tusked GREEN-skinned orc soldier standing on the disc in layered BRONZE and SAND-GOLD DRAKE-SCALE plate armour, a DRAGON-HEAD HELM with two swept-back horns and a short spine crest, FOUR shoulder pauldrons of differently coloured drake scales (crimson, ice-blue, sand-gold and storm-violet), a bright steel single-bladed BATTLEAXE with a big curved blade held diagonally across the chest in both hands, a small dragon-fang totem hanging at the belt; broad pale highlight planes on every upper-left plate and a thin bright rim light. Horned, scaled, four-coloured and complete." + CHEAT,
      "Gorbat-pride orcs: the ORC MASTER WYRMIC is the BRONZE-AND-SAND-GOLD DRAKE-SCALE armoured orc with a dragon-head helm, FOUR differently coloured drake-scale pauldrons and a big curved battleaxe across the chest (silhouette: a broad horned figure with a wide axe diagonal and four big shoulder plates; hue: bronze, sand-gold and green skin with crimson, ice-blue and violet accents; value: mid-light to bright). The shipped fiery orc wyrmic is a red-orange armoured axe orc, the icy orc wyrmic a white-and-ice-blue one, the berserker a spiked silver-brown one and the elite fighter a gold-and-blue shield fighter: this must not be uniformly red or white, must not hold a shield and must show the four coloured pauldrons and the dragon helm.",
      "Bronze and sand-gold scale plate, four accent pauldrons in crimson, ice-blue, sand-gold and violet, green skin, steel axe blade, a thin bright rim; nothing darker than mid bronze except the eye slits and plate seams; NO black armour; the disc stays neutral charcoal at reference lightness." + DISC,
      "READY single, no define_as (orc master wyrmic)", comp=ALLC + CATS)

asset(3, 'orc-mage-hunter', 'orc mage-hunter',
      "gorbat-pride and dungeon pool (general/npcs/orc-gorbat.lua:148, humanoid/orc, non-unique, no define_as, rank 3, base BASE_NPC_ORC_GORBAT, default-name image npc/humanoid_orc_orc_mage_hunter.png via the hyphen-to-underscore rule); the only definition of this name",
      [src(GOR, 'name = "orc mage-hunter"'), src(GOR, 'T_MANA_CLASH', after='name = "orc mage-hunter"'), src(GOR, 'resolvers.equip', after='name = "orc mage-hunter"'), src(GOR, 'resolvers.sustains_at_birth()'), ORC_BASE()],
      ORC_BASE(), None, 'humanoid', 'orc', False, False,
      ORC_STRUCT % ('Resolve is passive; Antimagic Shield is the only sustained talent and is a particle-and-shield buff (shader_shield particles only, no actor shader); the leaf also sets power_source antimagic', 'a waraxe, a shield and massive armour'),
      'humanoid_orc_orc_mage_hunter.png',
      [STY, IDN('humanoid_orc_orc_mage_hunter.png', 'Native shape (64x64): a huge fully enclosed blue-steel armoured orc with a slit visor and thick plates and spikes. Keep the bulky fully enclosed armoured orc, drawn as ONE compact figure filling the disc, in pale blue-steel and silver plate with a turquoise-glowing visor slit, a round ringed shield and a waraxe, clearly not the spiked brown berserker or the gold-and-blue elite fighter.'), REF_ORC_PRIDE],
      "An orc mage-hunter seen from a steep overhead three-quarter angle: a huge hulking orc FULLY ENCLOSED in bulky pale BLUE-STEEL and bright SILVER massive plate armour, a rounded GREAT HELM with a single narrow visor slit glowing pale TURQUOISE, broad overlapping layered pauldrons and thick greaves etched with thin pale lavender antimagic sigils, a big ROUND SHIELD in the left hand painted with concentric rings like a target and a short steel WARAXE in the right hand held in close, short silver chains hanging from the belt; broad pale highlight planes on every upper-left plate and a thin bright rim light. Enclosed, blue-steel, ringed-shield and complete." + CHEAT,
      "Gorbat-pride orcs: the ORC MAGE-HUNTER is the FULLY ENCLOSED hulking pale blue-steel and silver armoured orc with a turquoise visor slit, a concentric-ring round shield and a waraxe (silhouette: a blocky faceless armoured mass with a big round shield; hue: pale blue-steel, silver and turquoise with no visible skin; value: bright). The shipped berserker is a spiked silver-brown axe orc with a visible face, the elite fighter a gold-and-blue tower-shield fighter with a plume, the fiery and icy wyrmics red and white axe orcs: this must not show an orc face, must not be brown, gold or red and must carry the ringed round shield.",
      "Pale blue-steel and bright silver plate, turquoise visor glow, thin lavender sigils, steel waraxe, a thin bright rim; nothing darker than mid steel-blue except the visor slit and plate seams; NO black armour; the glow stays on the visor and must not tint the disc, which stays neutral charcoal at reference lightness." + DISC,
      "READY single, no define_as (orc mage-hunter)", comp=ALLC + CATS)

# ---- pack 4: three ritches ----
RITB = lambda: src(RIT, 'define_as = "BASE_NPC_RITCH"')
RIT_STRUCT = 'base BASE_NPC_RITCH (insect/ritch, no image=, no shader);' + DEFC + '; no equip, no sustains_at_birth, no auto_classes; %s'
asset(4, 'ritch-larva', 'ritch larva',
      "ritch-tunnels, eruan and ruined-dungeon pools plus the Arena (general/npcs/ritch.lua:50, insect/ritch, non-unique, no define_as, rank 1, base BASE_NPC_RITCH, default-name image); the only definition of this name",
      [src(RIT, 'name = "ritch larva"'), src(RIT, 'T_ROTTING_DISEASE', after='name = "ritch larva"'), RITB()],
      RITB(), None, 'insect', 'ritch', False, False,
      RIT_STRUCT % 'Rotting Disease and Shriek are activated talents',
      'insect_ritch_ritch_larva.png',
      [STY, IDN('insect_ritch_ritch_larva.png', 'Native shape (64x64): a plump butter-yellow segmented grub curled into a C shape with tiny black legs and small spikes on its head. Keep the fat yellow C-curled grub, drawn as ONE compact figure filling the disc, with no claws or armour, clearly not an orange armoured ritch.'), REF_RITCH],
      "A ritch larva seen from a steep overhead three-quarter angle: a fat, glossy, plump BUTTER-YELLOW segmented GRUB curled into a tight C SHAPE on the disc, six or seven distinct rounded body segments with pale cream undersides and thin orange-amber segment lines, a rounded head with small dark beady eyes, two tiny curved head spikes and small mandibles, rows of tiny black stub legs along the underside; broad pale highlight planes on every upper-left segment and a thin bright rim light. Soft, segmented, yellow, curled and complete." + CHEAT,
      "Ritches: the RITCH LARVA is the FAT BUTTER-YELLOW SEGMENTED GRUB curled into a C (silhouette: a soft round C-shaped tube of segments with no limbs to speak of; hue: butter-yellow, cream and amber lines; value: bright). The shipped flamespitter is an orange scorpion-like ritch, the impaler a tan spiked ritch, the chitinous ritch a golden turtle-shelled ritch and the Great Hive Mother a brick-red clawed ritch: this must not have claws, pincers, a stinger or armour and must be a soft curled grub.",
      "Butter-yellow and cream segments, amber lines, tiny black legs and eyes, a thin bright rim; nothing darker than mid amber except the eyes and leg stubs; the disc stays neutral charcoal at reference lightness." + DISC,
      "READY single, no define_as (ritch larva)", comp=ALLC + CATS)

asset(4, 'ritch-hunter', 'ritch hunter',
      "ritch-tunnels, eruan and ruined-dungeon pools plus the Arena (general/npcs/ritch.lua:66, insect/ritch, non-unique, no define_as, rank 2, base BASE_NPC_RITCH, default-name image); the only definition of this name",
      [src(RIT, 'name = "ritch hunter"'), src(RIT, 'T_FLAME', after='name = "ritch hunter"'), RITB()],
      RITB(), None, 'insect', 'ritch', False, False,
      RIT_STRUCT % 'Rotting Disease, Rush, Flame and Shriek are activated talents',
      'insect_ritch_ritch_hunter.png',
      [STY, IDN('insect_ritch_ritch_hunter.png', 'Native shape (64x64): a lean slate-blue wasp-like ritch with orange zig-zag stripes, a hooked horn crest and thin translucent wings. Keep the lean upright slate-indigo ritch with orange stripes and blade-like forelegs, drawn as ONE compact figure filling the disc, clearly not the orange flamespitter or the tan impaler.'), REF_RITCH],
      "A ritch hunter seen from a steep overhead three-quarter angle: a lean, upright WASP-LIKE RITCH standing tall on four thin jointed legs on the disc, slate-INDIGO chitin with bold ORANGE ZIG-ZAG STRIPES across the thorax and abdomen, a narrow head with a curved hooked HORN CREST and large amber compound eyes, two long BLADE-LIKE forelegs raised in front like scythes, two narrow pale blue-grey glassy wings held back along the body, a tapering striped abdomen; broad pale highlight planes on every upper-left plate and a thin bright rim light. Lean, blue, striped, scythe-armed and complete." + CHEAT,
      "Ritches: the RITCH HUNTER is the LEAN UPRIGHT SLATE-INDIGO WASP-LIKE ritch with orange zig-zag stripes, a hooked horn crest, scythe forelegs and held-back wings (silhouette: a thin tall figure with two raised blades and a tapering tail; hue: slate-indigo chitin with orange stripes and amber eyes; value: mid-light). The shipped flamespitter is an orange scorpion-like ritch with a flaming tail, the impaler a tan ritch with a long spike, the chitinous ritch a golden turtle-shelled ritch and the larva a soft yellow grub: this must not be orange, tan or golden overall, must not be a low scorpion and must be lean and upright with blade forelegs.",
      "Slate-indigo chitin, orange zig-zag stripes, amber eyes, pale blue-grey wings, a thin bright rim; nothing darker than mid slate-blue except the eye rims and leg joints; NO black chitin; the disc stays neutral charcoal at reference lightness." + DISC,
      "READY single, no define_as (ritch hunter)", comp=ALLC + CATS)

asset(4, 'ritch-hive-mother-pool', 'ritch hive mother',
      "ritch-tunnels, eruan and ruined-dungeon pools plus the Arena (general/npcs/ritch.lua:83, insect/ritch, non-unique, no define_as, rank 3, base BASE_NPC_RITCH, default-name image insect_ritch_ritch_hive_mother.png); the only definition of this NAME. The unique Ritch Great Hive Mother (zones/ritch-tunnels/npcs.lua:100, define_as HIVE_MOTHER) draws the same native PNG through an explicit image= and is already catalogued as id ritch-hive-mother, so this entry takes the new id ritch-hive-mother-pool (the names differ: 'ritch hive mother' vs 'Ritch Great Hive Mother', and the matcher binds the unique to its define_as)",
      [src(RIT, 'name = "ritch hive mother"'), src(RIT, 'T_SUMMON', after='name = "ritch hive mother"'), src(RIT, 'make_escort', after='name = "ritch hive mother"'), RITB(), src('zones/ritch-tunnels/npcs.lua', 'name = "Ritch Great Hive Mother"')],
      RITB(), None, 'insect', 'ritch', False, False,
      RIT_STRUCT % "Summon, Flame, Shriek and Rotting Disease are activated talents; summon and make_escort build random insect/ritch leaves that each wear their own token",
      'insect_ritch_ritch_hive_mother.png',
      [STY, IDN('insect_ritch_ritch_hive_mother.png', 'Native shape (64x64): a large red ritch with big pincers, one huge round amber eye, and a striped amber-and-black abdomen. Keep the big crimson-rust matriarch with big pincers, one huge amber eye and the swollen banded abdomen, drawn as ONE compact figure filling the disc, clearly larger and heavier than the lean hunter and the soft larva, and showing the swollen egg-laden abdomen the plain brick-red Great Hive Mother does not.'), REF_RITCH],
      "A ritch hive mother seen from a steep overhead three-quarter angle: a large heavy MATRIARCH RITCH squatting on the disc, glossy CRIMSON-RUST chitin, two big curved serrated PINCERS held forward, one huge round AMBER COMPOUND EYE in the middle of the face, four thick jointed legs planted wide, and trailing behind her a hugely SWOLLEN rounded ABDOMEN banded in amber and dark brown, with a few pale egg-sac bulges showing through its sides; broad pale highlight planes on every upper-left plate and a thin bright rim light. Heavy, pincered, one-eyed, egg-laden and complete." + CHEAT,
      "Ritches: the RITCH HIVE MOTHER is the LARGE HEAVY CRIMSON-RUST MATRIARCH with two big pincers, a single huge amber eye and a hugely SWOLLEN AMBER-AND-BROWN BANDED ABDOMEN (silhouette: a wide squat body with two big pincers in front and a big round bulb behind; hue: crimson-rust, amber and dark brown bands, cream eggs; value: mid-light). The shipped Great Hive Mother is a plain brick-red clawed ritch with no swollen abdomen, the flamespitter an orange scorpion-like ritch, the impaler a tan spiked ritch and the larva a soft yellow grub: this must be heavy rather than lean, must show the big banded abdomen and must not be orange, tan or yellow overall.",
      "Crimson-rust chitin, amber and dark brown abdomen bands, amber eye, cream egg bulges, a thin bright rim; nothing darker than mid brown except the eye rims and leg joints; NO black chitin; the disc stays neutral charcoal at reference lightness." + DISC,
      "READY single, no define_as (ritch hive mother, id ritch-hive-mother-pool)", comp=ALLC + CATS)


def retry(id_, pack, **changes):
    base = next(a for a in A if a['id'] == id_)
    A.append(dict(base, pack=pack, **changes))


exec((HERE / 'retries.py').read_text()) if (HERE / 'retries.py').exists() else None


TALL_IDS = tuple(a['id'] for a in A if a['native_tall'])
PNGF = {a['id']: 'NPC.lua:33 default-name image on the leaf (no image=/nice_tile)' for a in A}
PNGF.update({i: 'NPC.lua:33 default-name image on the leaf plus an explicit nice_tile tall body (image=invis.png, one add_mos entry with display_h=2, display_y=-1 naming the same PNG)' for i in TALL_IDS})
PNGF['duathedlen'] = PNGF['duathedlen'] + '; the default-name image of this leaf is the nonexistent npc/demon_major_d__athedlen.png (non-ASCII name), so only the nicer_tiles-on body is mapped'
EVDIR = 'evidence/monster-batch-ad-20260930/source-contracts.json'
DEFINE = {a['id']: a['define_as'] for a in A}
NAMES_LIST = "dúathedlen, daelach, orc grand summoner, orc master wyrmic, orc mage-hunter, ritch larva, ritch hunter, ritch hive mother, snow cat, panther, tiger, sabertooth tiger, ice wyrm"


def build():
    packs = {}
    identities = []
    render = 'game/addons/tome-checker-revised/' + EVDIR
    seen = set()
    from PIL import Image
    for a in A:
        if a['id'] in seen:
            continue
        seen.add(a['id'])
        native_rel = NPC + a['native']
        native_image = 'npc/' + a['native']
        ident = {'id': a['id'], 'native_name': a['name'], 'source': a['srcs'][0], 'define_as': a['define_as'],
                 'type': a['type'], 'subtype': a['subtype'], 'unique': a['unique'], 'native_tall': a['native_tall'],
                 'image_source': PNGF[a['id']],
                 'structure': a['structure'], 'native_image': native_image, 'native_image_path': native_rel,
                 'native_image_sha256': sha(native_rel), 'native_image_size': None, 'verdict': a['verdict']}
        with Image.open(WS / native_rel) as im:
            ident['native_image_size'] = list(im.size)
        if a['id'] in TALL_IDS:
            ident['tall_body'] = {'image': 'invis.png', 'add_mos': [{'image': native_image, 'display_h': 2, 'display_y': -1}],
                                  'catalog_flag': 'native_tall=true',
                                  'static_pin': 'nice_tile names the tall PNG explicitly; not unique, so no unique-only tall path applies'}
        if a['base']:
            ident['base_source'] = a['base']
        if len(a['srcs']) > 1:
            ident['extra_sources'] = a['srcs'][1:]
        identities.append(ident)
    findings = [
        "All thirteen names have exactly one NPC leaf definition under game/modules/tome (grep of every actor definition, zones, vaults and the Arena included). The zone pools and vaults (frost-dragon-lair, sleeping-dragons, renegade-wyrmics for the ice wyrm, the orc master wyrmic and the orc grand summoner; forest-ruined-building3 and snake-pit for the snow cat) only build those same leaves through name/random_filter lookups; renegade-wyrmics makes random bosses ('the Herald', 'Beastmaster #rng#', '#rng# the Frozen Terror') from the flat orc entries (existing captureRandomOrigin path, tests exist) and from the tall ice wyrm (tall entries stay native for random bosses, tests exist). The Arena spawns ritch larva and ritch hunter by name (same leaves).",
        "Summons that copy a monster wear its token: no talent, effect, vault or event builds a copy of any of the thirteen bodies under its own or another name. The ritch hive mother's Summon talent and make_escort build random insect/ritch leaves (each wearing its own token); the ice wyrm's make_escort builds cold drakes (already mapped); the orc grand summoner's Minotaur, Stone Golem, Ritch Flamespitter and Spider talents are the Wild Gift summons of other bodies (minotaur, stone golem, ritch flamespitter and giant spider aliases already exist); the orc master wyrmic's breaths and Tornado build no creature; Wild Gift and Wyrmic player talents copy none of the felines, demons or ritches.",
        "Same PNG, other identity: the native Ritch Great Hive Mother (zones/ritch-tunnels/npcs.lua:100, UNIQUE, define_as HIVE_MOTHER, explicit image=) draws insect_ritch_ritch_hive_mother.png, the PNG of the non-unique ritch hive mother. The catalog id ritch-hive-mother is taken by the unique, so the pool monster is catalogued as ritch-hive-mother-pool with its own drawing (the two names differ, so name lookup never crosses, and the unique is bound to its define_as). No name alias is needed.",
        "Left native: Corrupted Daelach (valley-moon, unique, define_as CORRUPTED_DAELACH, its own PNG demon_major_corrupted_daelach.png) is a different name and body from daelach and is not part of this batch; the Arena's 'ice wyrmic' is a different name from 'ice wyrm'. The dúathedlen's default-name image (used only with nicer_tiles off) is the nonexistent npc/demon_major_d__athedlen.png because NPC.lua:33 replaces every byte of the non-ASCII letter with an underscore; with nicer_tiles off the actor.image therefore never equals the catalog image and the token is not applied, and the tests pin that.",
        "Appearance contract: the dúathedlen, daelach, ice wyrm and snow cat are non-unique tall bodies (resolvers.nice_tile{image='invis.png', add_mos={{image='npc/<png>', display_h=2, display_y=-1}}}) and carry native_tall=true; the snow cat's invis.png is the tall-body mechanism of the nice_tile line, not an invisible actor (its PNG is a 64x128 cat, identical in kind to dolleg and thaurhereg), so it is mapped. The other nine are flat 64x64 default-name bodies.",
        "Same-family separation: the three Gorbat orcs are separate leaves from the orc summoner, the fiery and icy orc wyrmics, the orc berserker and the elite fighter (their tokens are unchanged and reject these names, and the reverse); the four cats, the three ritches, the two demons and the ice wyrm versus the cold drake, fire wyrm and venom wyrm are separate leaves with their own PNGs.",
        "Result: no per-identity `variants` entry, no `image_aliases` entry and no `name_aliases` entry is needed for this batch.",
    ]
    ev = {'schema': 1,
          'task': "monster-batch-ad: static re-verification (no game launch) of the thirteen identities of the first off-list dungeon-pool batch (" + NAMES_LIST + ") against game/modules/tome source and native sprites. Every field below was read from source: name, type/subtype, define_as (none bind one), explicit or NPC.lua:33 default image, unique (none), PNG on disk, and absence of moddable_tile/shader/anim/add_displays on each leaf and its base. Findings: four identities are non-unique tall bodies with an explicit nice_tile (dúathedlen, daelach, ice wyrm, snow cat; native_tall=true), nine are 64x64 single images (the three orc-pride orcs, the three ritches, panther, tiger, sabertooth tiger).",
          'new_ids_not_in_catalog_before_this_batch': [i['id'] for i in identities], 'identities': identities,
          'runtime_mutation_scan': {
              'method': "every talent of each identity (resolvers.talents, inherited base talents and the base-file talent lists) was resolved under game/modules/tome/data/talents and its mode read (sustained/activated/passive), and each talent block was grepped for writes to type/subtype/image/add_mos/add_displays/moddable_tile/replace_display/shader/updateModdableTile/addShaderAura/textures; the same talents/ and timed_effects/ greps as batches S to AC were applied and give the same writer set; the resolvers sustains_at_birth, inscriptions, equip, racial and nice_tile and the base-file resolvers were read; every auto_classes site under zones/, general/ and maps/ was listed with its leaf name.",
              'writers_found': [
                  {'file': 'game/modules/tome/data/talents/corruptions/shadowflame.lua', 'line': 97, 'talent': "Flame of Urh'Rok", 'effect': 'sustain: __old_type={type,subtype}; type,subtype = demon,major; image untouched; restored on deactivate'},
                  {'file': 'game/modules/tome/data/talents/psionic/thought-forms.lua', 'line': 93, 'talent': 'thought-form summons (Solipsist tree)', 'effect': 'sets type/subtype/image/moddable_tile/add_mos on the summoned minion copied from its summoner, never on the caster'},
                  {'file': 'game/modules/tome/data/talents/chronomancy/anomalies.lua', 'line': 587, 'talent': 'anomaly summons', 'effect': 'creates a separate spawned NPC with another image; not any identity of this batch'}],
              'other_hits_reviewed': [
                  'talents/gifts/mindstar-mastery.lua Psiblades (orc grand summoner; also the shipped orc summoner): updateModdableTile is a no-op for a non-moddable actor apart from shader-aura bookkeeping',
                  'talents/gifts/antimagic.lua Antimagic Shield (orc mage-hunter): shader_shield talent particles only, no actor shader or display write',
                  'talents/gifts/cold-drake.lua, fire-drake.lua and sand-drake.lua breaths (ice wyrm, orc master wyrmic): shader_wings particles only',
                  'talents/cunning/stealth.lua Stealth (snow cat, panther, tiger, sabertooth tiger): only reads the worn armour subtype; stealth hides the actor through visibility, not through an image write',
                  'talents/spells/golemancy.lua and talents/uber/mag.lua (player-only moddable_tile writes: the player alchemist golem and lich transformation; no identity of this batch)',
                  'timed_effects/physical.lua and other.lua (add_displays/replace_display only while the effect is active)', 'timed_effects/magical.lua (invisibility, shadow veil and similar shaders, only while active)'],
              'timed_effects_review': "timed_effects write shader, replace_display, add_displays or image only while active (invisibility shaders, stone/ice/pin displays, Wrathroot, Shivgoroth form, dragon egg, Lord of Skulls): the matcher rejects them (native art shows) and restores the token when they end.",
              'sustains_at_birth_review': [
                  {'identity': 'snow cat, panther, tiger, sabertooth tiger', 'sustained': ['Stealth'], 'note': 'the base BASE_NPC_CAT calls resolvers.sustains_at_birth(); Stealth is temporary values and visibility only'},
                  {'identity': 'orc grand summoner', 'sustained': ['Psiblades'], 'note': 'the base calls resolvers.sustains_at_birth(); Psiblades calls updateModdableTile, a no-op for a non-moddable actor'},
                  {'identity': 'orc master wyrmic', 'sustained': ['Icy Skin'], 'note': 'the base calls resolvers.sustains_at_birth(); temporary values and particles only'},
                  {'identity': 'orc mage-hunter', 'sustained': ['Antimagic Shield'], 'note': 'the base calls resolvers.sustains_at_birth(); shield particles only'},
                  {'identity': 'dúathedlen, daelach, ice wyrm, ritch larva, ritch hunter, ritch hive mother', 'sustained': [], 'note': 'no sustains_at_birth on the leaf or its base (Icy Skin of the ice wyrm is sustained only when the actor activates it)'}],
              'auto_classes_review': [
                  {'identity': 'all thirteen', 'class': 'none', 'finding': "none of the thirteen leaves or their bases has auto_classes; every auto_classes site in zones/, general/ and maps/ belongs to another leaf, so none can reach Flame of Urh'Rok and there is no urh_rok_form opt-in."}],
              'visibility_review': 'Identities with stealth or invisibility (the four felines through Stealth, the orc mage-hunter through runes) can apply a shader effect while it lasts; the matcher rejects an actor with a shader (native art shows) and the token returns when it ends; token drawing follows actor visibility as for every other token.',
              'hits_in_batch': [],
              'no_hit': [i['native_name'] for i in identities]},
          'summons_and_same_body_copies': {
              'method': "grep of every actor definition, static map, quest script, vault, encounter, event, artifact and talent under game/modules/tome (data and class) for the thirteen names and PNGs; talents that build summons/copies (summon-*, dreadmaster, master-of-flesh, master-of-bones, rot, thought-forms, simulacra/mirror images, Grand Arrival, golemancy, cloneFull users, shadows) checked for copies of these bodies.",
              'findings': findings},
          'name_collisions_checked': [
              {'name': a['name'], 'other_definitions': ['none'],
               'outcome': ('single actor definition without define_as; the catalog entry has no define_as and matches by exact name, type and subtype' + ('; same PNG as the unique Ritch Great Hive Mother (HIVE_MOTHER), different name, own id ritch-hive-mother-pool' if a['id'] == 'ritch-hive-mother-pool' else ''))} for a in {x['id']: x for x in A}.values()],
          'kept_native': [
              {'name': 'Corrupted Daelach (valley-moon unique)', 'reason': 'different name, define_as and PNG from daelach; not part of this batch'},
              {'name': 'dúathedlen with nicer_tiles off', 'reason': 'the default-name image is the nonexistent npc/demon_major_d__athedlen.png, never equal to the catalog image'}],
          'neighbours_kept_native': [
              {'name': 'multi-hued drakes and shadow claw', 'reason': 'separate batch'}]}
    out = ADDON / EVDIR
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(ev, indent=2, ensure_ascii=False) + '\n')
    evsha = hashlib.sha256(out.read_bytes()).hexdigest()
    for a in A:
        refs = [{'path': p, 'sha256': sha(p), 'role': r, 'note': n} for r, p, n in a['refs']]
        entry = {'asset_id': a['id'], 'native_name': a['name'], 'scope': a['scope'], 'sources': a['srcs'], 'references': refs,
                 'contrast_dimensions': list(a['dims']),
                 'prompt_fields': {'subject': a['subject'], 'contrast': a['contrast'], 'composition': a['comp'] or COMP, 'palette': a['palette']},
                 'kind': 'creature', 'max_attempts': 1, 'gate': 'ready',
                 'gate_reason': f"Exact source identity re-verified directly against game/modules/tome source (name={a['name']}, define_as={a['define_as']}, type={a['type']}/subtype={a['subtype']}, unique={a['unique']}, native_tall={a['native_tall']}); details and hashes in evidence/monster-batch-ad-20260930/source-contracts.json. {a['structure']}. Exact catalog entry only, never a whole-subtype mapping.",
                 'render_evidence': [{'path': render, 'sha256': evsha}]}
        if a.get('refinement'):
            entry['refinement'] = a['refinement']
        packs.setdefault(a['pack'], []).append(entry)
    for n, assets in packs.items():
        p = ADDON / f'art/production/batches/monster-batch-ad-{n}.json'
        if p.exists():
            print('exists, skipped', p.name)
            continue
        p.write_text(json.dumps({'schema': 1, 'batch_id': f'monster-batch-ad-{n}', 'assets': assets}, indent=2, ensure_ascii=False) + '\n')
        print('wrote', p.name)


if __name__ == '__main__':
    build()
