"""Generate the monster-batch-ac task packs and the pinned source-contract
evidence (survey-2 unscheduled list after batch AB, the FINAL batch: every
remaining candidate except Training Dummy: Aletta Soultorn, ruin banshee, Filio
Flightfond, orc high pyromancer, orc high cryomancer, Glacial Legion, Arch
Zephyr, Rotting Titan, Heavy Sentinel, Void Spectre, oozing horror, abyssal
horror, ungolmor, umbral horror, vampire lord, degenerated ogric mass, ogric
abomination; see SELECTION.md). Pure bookkeeping: hashes native sources/sprites,
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
ART_REL = 'game/addons/tome-checker-revised/art/monster-batch-ac/'
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


# family references built from shipped runtime tokens
REF_GHOSTS = RC('ghosts', ['banshee', 'dread', 'dreadmaster', 'kors-fury', 'grave-wight', 'shade-of-telos'], 3,
                'Six shipped ghost tokens (the banshee: a flowing pale-CYAN woman-ghost; the dread: a hooded purple-blue shroud with a red core; the dreadmaster: a big blue hooded shroud; Kor\'s Fury: a teal-cyan robed spirit; the grave wight: a pale cyan drifting ghost; the Shade of Telos: a blue crystalline figure): Aletta Soultorn is a slender ORCHID-VIOLET and lilac ghost-woman with a silver diadem and streaming white hair, shrieking with arms flung wide; the ruin banshee is a hunched clawed screaming spectre of acid-green and ember-orange Fearscape vapour; the Glacial Legion is a huge teardrop of frosted white ice-fog with a deep crimson frozen-blood orb at its heart; none is cyan or teal, none is a hooded shroud and none is a crystalline blue figure.')
REF_HIGH_ORCS = RC('orc-robed-casters', ['orc-pyromancer', 'orc-cryomancer', 'orc-corruptor', 'orc-necromancer', 'orc-blood-mage', 'orc-summoner'], 3,
                   'Six shipped orc caster tokens (the pyromancer: a plain red-orange robe with one small flame in hand; the cryomancer: a plain blue robe; the corruptor, necromancer, blood mage and the beast-shaman summoner in their own colours): the two HIGH casters are a higher rank, not recolours: the HIGH PYROMANCER stands tall and wide-armed in layered scarlet-and-gold ceremonial robes with a tall horned flame-crest mitre, gold-rimmed flame-pattern pauldrons, BOTH hands blazing and a whole ring of fire orbiting its waist; the HIGH CRYOMANCER is a staff-planted figure in white-and-ice-blue robes with a white fur collar, a tall crystalline ice crown, jagged ice pauldrons, one hand gripping a tall staff topped with a huge snowflake crystal, the other hand holding a frost wand, and a spiral of ice shards; neither may be a plain robe with one small effect.')
REF_SKELETONS = RC('skeletons', ['skeleton-mage', 'skeleton-magus', 'skeleton-master-archer', 'skeleton-assassin', 'degenerated-skeleton-archer'], 3,
                   'Five shipped skeleton tokens (the skeleton mage: a dark-cloaked caster; the magus: a blue-robed caster with two flames; the master archer: a gold-armoured archer; the skeleton assassin; the degenerated archer): Filio Flightfond is a SHORT, hunched, furtive IVORY-bone skeleton with soft padded brown boots, a plum-violet neckerchief and belt, a leather SLING whirling in one hand and a short steel dagger in the other, in a sneaking crouch; not robed, not armoured and not an archer with a bow.')
REF_VAMPIRES = RC('vampires', ['lesser-vampire', 'vampire', 'master-vampire', 'elder-vampire', 'the-master'], 3,
                  'Five shipped vampire tokens (the lesser vampire: an orange-shirted man; the vampire: a red-caped lunging man; the master vampire: a blue-caped man; the elder vampire: a plum hooded robe with a purple orb; the Master: a crimson-robed red-hooded figure): the vampire lord is a noble in an OCHRE-GOLD long tunic with a gold sash, high collar and a heavy bronze-brown cloak lined with crimson, a rapier raised in one hand; ARCH ZEPHYR is a gale-grey and storm-blue robed ARCHER drawing a lightning-wrapped longbow with billowing wind-swept robes and forked lightning; neither is a red, blue or plum cloak and Arch Zephyr is never a standing caster.')
REF_GHOULS = RC('ghouls-giants', ['ghoul', 'ghast', 'ghoulking', 'borfast', 'necrotic-mass', 'ogre-pounder'], 3,
                'Six shipped bodies (the ghoul, ghast and ghoulking: lean brown hunched ghouls; Borfast: a shield-and-mace dwarf ghoul; the necrotic mass: a pink-brown lump with skulls; the ogre pounder: a blue ogre): the Rotting Titan is a colossal slow HULK assembled from dusky mauve rotting flesh and huge slabs and boulders of pale limestone-beige stone, boulder-fists at the end of every limb, sickly green-yellow rot patches and small glowing green eyes; not a lean ghoul, not a pink lump and not an ogre.')
REF_BONE_GIANTS = RC('bone-giants', ['bone-giant', 'heavy-bone-giant', 'runed-bone-giant', 'eternal-bone-giant', 'half-finished-bone-giant'], 3,
                     'Five shipped bone giant tokens (the bone giant and heavy bone giant: plain tan bone hulks; the runed bone giant: red rune glyphs; the eternal bone giant: pale lavender bones; the half-finished bone giant: a thin unfinished lilac skeleton): the Heavy Sentinel is a bone giant FORGED INTO A FURNACE: ash-grey and ivory bones fused by molten-ORANGE seams into armour plates, a wide-open ribcage furnace roaring with a tall column of white-yellow fire, a horned fused-bone skull with blazing eye sockets and fists dripping embers; not plain tan bones and not a runed giant.')
REF_WIGHTS = RC('wights-spectres', ['forest-wight', 'grave-wight', 'barrow-wight', 'shade-of-telos', 'dread'], 3,
                'Five shipped wight and spirit tokens (the forest wight: a green armoured shield-bearer; the grave wight: a pale cyan drifting ghost; the barrow wight: an armoured blue-glowing figure; the Shade of Telos: a blue crystalline figure; the dread: a hooded purple shroud): the Void Spectre is a gaunt hooded humanoid wraith made of swirling ROSE-RED and magenta arcane energy with a white-hot face slit and long trailing ragged sleeves, ringed by an orbiting vortex of pale violet and white arcane runes and sparks; solid and opaque, not cyan, not armoured and not a purple shroud.')
REF_SLIMES = RC('slimes-blobs', ['green-ooze', 'green-jelly', 'poison-ooze', 'bloated-horror', 'luminous-horror', 'necrotic-mass'], 3,
                'Six shipped blob tokens (the green ooze, green jelly and poison ooze: small shiny slime blobs; the bloated horror: a pink baby-faced blob; the luminous horror: a yellow glowing humanoid; the necrotic mass: a pink-brown lump): the oozing horror is a MASSIVE amorphous lime-green slime mound, much bigger and heavier than the small ooze tokens, with SEVEN OR EIGHT large drifting orange-amber EYES scattered through the translucent slime, thick dripping slime tendrils and pools of ooze around its base; not a small shiny blob, not pink and not humanoid.')
REF_DARK_HORRORS = RC('dark-horrors', ['entrenched-horror', 'ravenous-horror', 'horned-horror', 'weirdling-beast', 'blade-horror', 'void-horror'], 3,
                      'Six shipped horror tokens (the entrenched horror: a limestone pillar in a teal tentacle wreath; the ravenous horror: a fanged fish head; the horned horror: a purple horned beast; the weirdling beast: a purple-pink tentacled beast; the blade horror; the void horror: an indigo lens): the ABYSSAL HORROR is a heaving MASS OF WRITHING TENTACLES in deep indigo-violet and slate-teal with a cluster of glowing CRIMSON eyes buried at its centre and pale lilac sucker rows catching the light; the UMBRAL HORROR is a lithe jagged shadow-stalker crouched low, made of smoky pearl-grey and dusk-lavender shadow with hooked claws, backswept thorn-spikes and two pale-yellow eyes; neither has a pillar, a fish head or a horned beast body.')
REF_SPIDERS = RC('spiders', ['giant-spider', 'chitinous-spider', 'ungole', 'weaver-patriarch', 'orb-weaver'], 3,
                 'Five shipped spider tokens (the giant spider: a slender dark-grey spider; the chitinous spider: a pale bone-white spider; Ungole: a black spider with a red mark; the weaver patriarch: a blue-and-white spider; the orb weaver): the ungolmor is the LARGEST, squat and heavy, a dome-bodied spider whose thick hide hangs in overlapping armoured FOLDS like a rhinoceros, in mid slate-blue-grey with pale silver ridges and short thick legs, a cluster of glowing amber eyes and broad mandibles; not slender, not bone-white, not black.')
REF_OGRES = RC('ogres', ['ogre-guard', 'ogre-mauler', 'ogre-pounder', 'ogre-warmaster', 'ogre-rune-spinner', 'drem-master'], 3,
               'Six shipped ogre and giant tokens (the ogre guard: a tan hammer ogre; the mauler: a red ogre; the pounder: a blue ogre; the warmaster: a plate-armoured ogre; the rune-spinner: an orange caster; the drem master): the OGRIC ABOMINATION is a mottled grey-mauve ogre with one arm replaced by a huge pale STONE golem arm and fist with glowing violet-cyan runes, bolted stone plates on shoulder and chest, a leather loincloth and a great maul; the DEGENERATED OGRIC MASS is not an ogre-shaped fighter at all but a slumped heap of bulging ochre-tan flesh with tumours, several malformed fused limbs and a half-buried tusked ogre face; neither is tan, red, blue or plate-armoured.')

CHEAT = ' Every surface of the figure is painted as SOLID OPAQUE material (no see-through, faded or translucent parts, no alpha gradients inside the figure).'

# ---- pack 1: Aletta Soultorn, ruin banshee, Glacial Legion, Filio Flightfond ----
asset(1, 'aletta-soultorn', 'Aletta Soultorn',
      "dreadfell boss (zones/dreadfell/npcs.lua:282, undead/ghost, UNIQUE, define_as ALETTA, rank 3.5, no base, default-name image); the only definition of this name",
      [src(DRE, 'name = "Aletta Soultorn"'), src(DRE, 'define_as = "ALETTA"'), src(DRE, 'T_TYRANT', after='name = "Aletta Soultorn"'), src(DRE, 'resolvers.sustains_at_birth()', after='name = "Aletta Soultorn"'), src(DRE, 'resolvers.equip{', after='name = "Aletta Soultorn"')],
      None, 'ALETTA', 'undead', 'ghost', True, False,
      'no base entity (a plain define_as leaf: no image=, no shader);' + DEFC + ';' + DEFD + ' (ALETTA);' + DEFU + '; resolvers.equip a cloth robe, diadem, amulet and rings (equipment only, no moddable_tile); the leaf calls resolvers.sustains_at_birth() and Gloom is the only sustained talent (temporary values and particles); no auto_classes; pass_wall movement is not a display change',
      'undead_ghost_aletta_soultorn.png',
      [STY, IDN('undead_ghost_aletta_soultorn.png', 'Native shape (64x64): a pale cyan-white ghost of a slender woman with long wild hair and tattered robes, mouth open in a shriek, arms flung wide. Keep the slender shrieking ghost-woman with flowing hair and wide arms, drawn as ONE compact figure filling the disc, but in orchid-violet and lilac robes with a silver-and-amethyst diadem, clearly not the cyan banshee.'), REF_GHOSTS],
      "Aletta Soultorn seen from a steep overhead three-quarter angle: a slender, elegant GHOST-WOMAN floating just above the disc, an enchantingly beautiful higher-elf face twisted in a shriek of despair with wide glowing white-violet eyes and an open mouth, long wild silver-white HAIR streaming out to both sides, a delicate silver DIADEM set with a big amethyst on her brow, both arms flung wide with long thin clawed fingers, and a long tattered ORCHID-VIOLET and pale-lilac ROBE with ragged trailing hems that curl into ribbons of pearly lilac mist below her; broad pale highlight planes on every upper-left fold and a thin bright rim light. Shrieking, crowned, violet and complete." + CHEAT,
      "Ghosts: ALETTA SOULTORN is the SLENDER SHRIEKING VIOLET GHOST-WOMAN with a silver-and-amethyst diadem, streaming white hair and arms flung wide (silhouette: a tall slim figure with two wide arms and streaming hair; hue: orchid-violet, lilac, pearl white and silver; value: light). The shipped banshee is a flowing pale cyan woman-ghost, Kor's Fury a teal spirit, the grave wight a cyan ghost, the dread and dreadmaster hooded blue-purple shrouds: this must not be cyan or teal, must not be hooded and must wear a diadem.",
      "Orchid-violet and pale-lilac robe, pearl-white face and hair, silver diadem with an amethyst, white-violet glowing eyes, pearly lilac mist, a thin bright rim; nothing darker than mid orchid except the mouth and eye hollows; NO black robe, no dark shroud; the glow stays on the figure and must not tint the disc, which stays neutral charcoal at reference lightness." + DISC,
      "READY unique flat, define_as ALETTA (Aletta Soultorn)", comp=COMP + FIT + COMPACT + BRIGHT + DARKFIX)

asset(1, 'ruin-banshee', 'ruin banshee',
      "rak-shor-pride pool and the greater-crypt vault (general/npcs/ghost.lua:129, undead/ghost, non-unique, no define_as, rank 3, base BASE_NPC_GHOST, default-name image); the only definition of this name; the vault picks it with random_filter name=ruin banshee (the same leaf)",
      [src(GHO, 'name = "ruin banshee"'), src(GHO, 'T_CORRUPTED_NEGATION', after='name = "ruin banshee"'), src(GHO, 'T_PHASE_DOOR', after='name = "ruin banshee"'), src(GHO, 'resolvers.sustains_at_birth()'), src(GHO, 'define_as = "BASE_NPC_GHOST"')],
      src(GHO, 'define_as = "BASE_NPC_GHOST"'), None, 'undead', 'ghost', False, False,
      'base BASE_NPC_GHOST (undead/ghost, no image=, no shader);' + DEFC + '; the base calls resolvers.sustains_at_birth() but none of the leaf talents is sustained (Phase Door, Silence, Mind Disruption, Corrupted Negation, Corrosive Worm, Poison Storm and the curses are activated or passive); no equip, no auto_classes',
      'undead_ghost_ruin_banshee.png',
      [STY, IDN('undead_ghost_ruin_banshee.png', 'Native shape (64x64): a hunched, ragged spectre of glowing cyan lines with a gaping screaming face, long clawed arms and a trailing tattered lower body. Keep the hunched, clawed, ragged, screaming spectre, drawn as ONE compact figure filling the disc, but wreathed in acid-green and ember-orange Fearscape vapour instead of cyan, clearly not the graceful cyan banshee.'), REF_GHOSTS],
      "A ruin banshee seen from a steep overhead three-quarter angle: a hunched, ragged, vengeful SPECTRE hovering over the disc, its body made of tattered sickly ACID-LIME-GREEN ghost-cloth with glowing EMBER-ORANGE cracks running through it like a burning ruin, a gaunt pale-bone-grey skull-like face thrown back with a huge gaping shrieking mouth and two white-hot eyes, long ropy arms ending in curved claws held out in front, wisps of bright blight-green vapour and a few orange sparks curling up from its shoulders and back, its lower body dissolving into ragged tattered strips (all close to the body); broad pale highlight planes on every upper-left surface and a thin bright rim light. Hunched, screaming, burning and complete." + CHEAT,
      "Ghosts: the RUIN BANSHEE is the HUNCHED CLAWED SCREAMING SPECTRE of acid-green ghost-cloth with ember-orange cracks and Fearscape vapour (silhouette: a hunched mass with a big screaming head and two long clawed arms reaching forward; hue: acid lime-green and ember orange with a bone-grey face; value: mid-light). The shipped banshee is a flowing upright pale cyan woman-ghost, the dread a purple hooded shroud and Kor's Fury a teal spirit: this must not be cyan, teal, upright, graceful or hooded.",
      "Acid lime-green cloth, ember-orange cracks and sparks, bone-grey face, white-hot eyes, bright blight-green vapour, a thin bright rim; nothing darker than mid green except the mouth interior and eye rims; NO black or dark green cloth; the glow stays on the figure and must not tint the disc, which stays neutral charcoal at reference lightness." + DISC,
      "READY single, no define_as (ruin banshee)", comp=COMP + FIT + COMPACT + BRIGHT + DARKFIX)

asset(1, 'glacial-legion', 'Glacial Legion',
      "rak-shor-pride boss (zones/rak-shor-pride/npcs.lua:195, undead/ghost, UNIQUE, define_as GLACIAL_LEGION, rank 3.5, base BASE_NPC_GHOST, resolvers.nice_tile tall body); the only definition of this name",
      [src(RSP, 'name = "Glacial Legion"'), src(RSP, 'define_as = "GLACIAL_LEGION"'), src(RSP, 'resolvers.nice_tile', after='name = "Glacial Legion"'), src(RSP, 'T_UTTERCOLD', after='name = "Glacial Legion"'), src(RSP, 'on_move = function(self)', after='name = "Glacial Legion"'), src(GHO, 'define_as = "BASE_NPC_GHOST"')],
      src(GHO, 'define_as = "BASE_NPC_GHOST"'), 'GLACIAL_LEGION', 'undead', 'ghost', True, False,
      'base BASE_NPC_GHOST (undead/ghost, no image=, no shader);' + tall_unique('undead_ghost_glacial_legion') + ';' + DEFD + ' (GLACIAL_LEGION); the leaf has no sustains_at_birth of its own (the base calls it) and Uttercold, Spellcraft and Frost Hands are sustained temporary values and particles; on_move only adds a lasting ice map effect; resolvers.equip only the Glacial Cloak; no auto_classes',
      'undead_ghost_glacial_legion.png',
      [STY, IDN('undead_ghost_glacial_legion.png', 'Native shape (64x128, tall): a huge pale ice-blue ghost form like a tall teardrop of frosted mist with a glowing red orb of frozen blood at its chest. Keep the tall teardrop of frosted ice-fog around a red frozen-blood orb, drawn as ONE compact figure filling the disc, no tall canvas, in frosted white and pale ice-blue with a deep crimson orb and frost crystals, clearly not the shipped cyan ghosts.'), REF_GHOSTS],
      "The Glacial Legion seen from a steep overhead three-quarter angle: a huge rounded TEARDROP of swirling FROSTED WHITE and pale ice-blue fog and ice hovering over the disc as one compact mass, dozens of faint ghostly faces and reaching hands (the fused legion of souls) pressed into its surface, sharp white frost crystals and short icicles sprouting from its shoulders and crown, and at its heart a large glossy deep CRIMSON ORB of FROZEN BLOOD, ringed by ice crystals and glowing softly, the bottom of the teardrop trailing into two small curling pools of white frost; broad pale highlight planes on every upper-left surface and a thin bright rim light. Massed, frozen, red-hearted and complete." + CHEAT,
      "Ghosts: the GLACIAL LEGION is the HUGE TEARDROP OF FROSTED WHITE ICE-FOG packed with ghostly faces around a DEEP CRIMSON FROZEN-BLOOD ORB (silhouette: a big round-topped teardrop with sprouting ice crystals and one strong red centre; hue: frosted white and ice-blue with crimson; value: very light with a saturated red core). The shipped banshee is a slim cyan woman-ghost, the grave wight a cyan drifting ghost, the Shade of Telos a blue crystalline figure and the dread a purple shroud: this must not be a slim humanoid, must not be a crystalline figure and must have the red orb.",
      "Frosted white and pale ice-blue mist and ice, sharp white frost crystals, a deep glossy crimson orb with a pale rim, faint pale ghost faces, a thin bright rim; nothing darker than mid ice-blue except the crimson orb and the faces' hollows; NO black or navy mass; the glow stays on the figure and must not tint the disc, which stays neutral charcoal at reference lightness." + DISC,
      "READY tall unique, define_as GLACIAL_LEGION (Glacial Legion)", comp=COMP + FIT + COMPACT + BRIGHT + DARKFIX + CATS)

asset(1, 'filio-flightfond', 'Filio Flightfond',
      "dreadfell boss (zones/dreadfell/npcs.lua:358, undead/skeleton, UNIQUE, define_as FILIO, rank 3.5, no base, default-name image); the only definition of this name",
      [src(DRE, 'name = "Filio Flightfond"'), src(DRE, 'define_as = "FILIO"'), src(DRE, 'resolvers.auto_equip_filters{', after='name = "Filio Flightfond"'), src(DRE, 'resolvers.equip{', after='name = "Filio Flightfond"'), src(DRE, 'body = { INVEN = 10, MAINHAND=1, OFFHAND=1, QUIVER=1  }', after='name = "Filio Flightfond"')],
      None, 'FILIO', 'undead', 'skeleton', True, False,
      'no base entity (a plain define_as leaf: no image=, no shader);' + DEFC + ';' + DEFD + ' (FILIO);' + DEFU + '; resolvers.equip a sling, a dagger and shot (equipment only, no moddable_tile); the leaf defines no talents and has no sustains_at_birth; no auto_classes',
      'undead_skeleton_filio_flightfond.png',
      [STY, IDN('undead_skeleton_filio_flightfond.png', 'Native shape (64x64): a small furtive cream-bone skeleton in big soft brown boots holding a short dagger and a sling. Keep the short furtive padded-footed skeleton with sling and dagger, drawn as ONE compact figure filling the disc, in bright ivory bone with a plum-violet neckerchief and belt, clearly not a robed caster or an archer.'), REF_SKELETONS],
      "Filio Flightfond seen from a steep overhead three-quarter angle: a SHORT furtive IVORY-BONE skeleton caught in a sneaking crouch on the disc, a big cunning skull with hollow sockets tilted to one side, soft padded tan-brown leather boots and ankle wraps, a PLUM-VIOLET neckerchief knotted at the throat and a matching sash belt with two bright brass buckles, a leather SLING with a small stone swinging in the left hand and a short bright steel DAGGER in the right hand held low, a small pouch of shot at the hip; broad pale highlight planes on every upper-left bone and a thin bright rim light. Furtive, padded, armed with sling and dagger and complete.",
      "Skeletons: FILIO FLIGHTFOND is the SHORT SNEAKING IVORY SKELETON with soft padded boots, a plum-violet neckerchief and sash, a whirling sling and a short dagger (silhouette: a small crouched figure with a big skull, one arm swinging a sling and one arm low with a dagger; hue: ivory bone, tan-brown boots, plum-violet cloth; value: light). The shipped skeleton mage is a dark-cloaked caster, the magus a blue-robed caster with flames, the master archer a gold-armoured archer with a bow and the skeleton assassin a dark blade-wielder: this must not wear a robe or armour, must not hold a bow and must not be dark.",
      "Bright ivory and cream bone, tan-brown padded boots, plum-violet cloth, brass buckles, steel dagger, a thin bright rim; nothing darker than mid brown except the eye sockets and joint seams; NO black cloak, no dark bones; the disc stays neutral charcoal at reference lightness." + DISC,
      "READY unique flat, define_as FILIO (Filio Flightfond)", comp=COMP + FIT + COMPACT + BRIGHT + DARKFIX)

# ---- pack 2: orc high pyromancer, orc high cryomancer, vampire lord, ungolmor ----
asset(2, 'orc-high-pyromancer', 'orc high pyromancer',
      "vor-armoury pool and the renegade-pyromancers vault (general/npcs/orc-vor.lua:77, humanoid/orc, non-unique, no define_as, rank 3, base BASE_NPC_ORC_VOR, default-name image); the only definition of this name; the vault builds it with random_filter name=orc high pyromancer and a random_boss 'the Invoker' (the existing flat captureRandomOrigin path)",
      [src(VOR, 'name = "orc high pyromancer"'), src(VOR, 'T_BURNING_WAKE', after='name = "orc high pyromancer"'), src(VOR, 'T_INFERNO', after='name = "orc high pyromancer"'), src(VOR, 'resolvers.equip', after='name = "orc high pyromancer"'), src(VOR, 'resolvers.sustains_at_birth()', after='name = "orc high pyromancer"'), src(VOR, 'define_as = "BASE_NPC_ORC_VOR"')],
      src(VOR, 'define_as = "BASE_NPC_ORC_VOR"'), None, 'humanoid', 'orc', False, False,
      'base BASE_NPC_ORC_VOR (humanoid/orc, no image=, no shader);' + DEFC + '; resolvers.racial() only adds orc levelup talents; the leaf calls resolvers.sustains_at_birth() and Burning Wake (talents/spells/wildfire.lua:78 addShaderAura, native shader-aura bookkeeping the matcher ignores), Spellcraft and Essence of Speed are sustained (particles and temporary values); resolvers.equip a staff, cloth armour and a wand (equipment only, no moddable_tile); resolvers.inscriptions picks runes (no display write); no auto_classes',
      'humanoid_orc_orc_high_pyromancer.png',
      [STY, IDN('humanoid_orc_orc_high_pyromancer.png', 'Native shape (64x64): a green orc in scarlet robes with a red horned pauldron collar, fire in both hands. Keep the robed green fire-orc with flames in both hands, drawn as ONE compact figure filling the disc, as a higher rank: layered scarlet-and-gold ceremonial robes, a tall horned flame-crest mitre, gold flame-pattern pauldrons, both hands blazing and a ring of fire orbiting the waist, clearly more than the shipped plain-robed pyromancer.'), REF_HIGH_ORCS],
      "An orc high pyromancer seen from a steep overhead three-quarter angle: a tall broad GREEN-skinned tusked orc standing with BOTH ARMS SPREAD WIDE and a roaring ball of bright orange-yellow FIRE blazing in each open hand, wearing layered ceremonial SCARLET robes with wide GOLD trim bands, a tall pointed horned FLAME-CREST MITRE in scarlet and gold on his head, GOLD-rimmed crimson pauldrons embossed with flame patterns, a cream sash, and a whole RING OF FIRE (a loop of bright orange-yellow flames) orbiting around his waist at knee height, tucked inside the disc; broad pale highlight planes on every upper-left fold and a thin bright rim light. Robed, crested, blazing and complete.",
      "Orc casters: the ORC HIGH PYROMANCER is the TALL WIDE-ARMED CEREMONIAL FIRE-LORD with a horned flame-crest mitre, gold-trimmed scarlet robes, gold pauldrons, a blazing fireball in EACH hand and a ring of fire orbiting his waist (silhouette: a tall figure with a pointed crest, two wide arms with fire and a flame ring; hue: scarlet, gold, cream and fire orange with green skin; value: bright). The shipped orc pyromancer is a plain red-orange robe with one small flame, the cryomancer a plain blue robe: this must not be a plain robe, must not have a single small flame and must wear the crest mitre and pauldrons.",
      "Bright scarlet and gold robes, cream sash, green skin, orange-yellow flames, a thin bright rim; nothing darker than mid scarlet except eye slits and fold seams; NO dark maroon robe, no black; the fire glow stays on the figure and its ring and must not tint or light the disc, which stays neutral charcoal at reference lightness." + DISC,
      "READY single, no define_as (orc high pyromancer)", comp=COMP + FIT + COMPACT + BRIGHT + DARKFIX)

asset(2, 'orc-high-cryomancer', 'orc high cryomancer',
      "vor-armoury pool (general/npcs/orc-vor.lua:131, humanoid/orc, non-unique, no define_as, rank 3, base BASE_NPC_ORC_VOR, default-name image); the only definition of this name",
      [src(VOR, 'name = "orc high cryomancer"'), src(VOR, 'T_FROZEN_GROUND', after='name = "orc high cryomancer"'), src(VOR, 'T_ICE_SHARDS', after='name = "orc high cryomancer"'), src(VOR, 'resolvers.equip', after='name = "orc high cryomancer"'), src(VOR, 'resolvers.sustains_at_birth()', after='name = "orc high cryomancer"'), src(VOR, 'define_as = "BASE_NPC_ORC_VOR"')],
      src(VOR, 'define_as = "BASE_NPC_ORC_VOR"'), None, 'humanoid', 'orc', False, False,
      'base BASE_NPC_ORC_VOR (humanoid/orc, no image=, no shader);' + DEFC + '; resolvers.racial() only adds orc levelup talents; the leaf calls resolvers.sustains_at_birth() and Spellcraft and Essence of Speed are the sustained talents (particles and temporary values); resolvers.equip a staff, cloth armour and a wand (equipment only, no moddable_tile); resolvers.inscriptions picks runes (no display write); no auto_classes',
      'humanoid_orc_orc_high_cryomancer.png',
      [STY, IDN('humanoid_orc_orc_high_cryomancer.png', 'Native shape (64x64): a green orc in blue robes with a blue horned pauldron collar, a curved ice blade in one hand. Keep the robed green frost-orc, drawn as ONE compact figure filling the disc, as a higher rank: white-and-ice-blue robes with a white fur collar, a tall crystalline ice crown, jagged ice pauldrons, a staff topped with a huge snowflake crystal in one hand and a frost wand in the other, with a spiral of ice shards, clearly more than the shipped plain blue-robed cryomancer and not a copy of the high pyromancer pose.'), REF_HIGH_ORCS],
      "An orc high cryomancer seen from a steep overhead three-quarter angle: a tall GREEN-skinned tusked orc standing upright in a wide stance with a tall STAFF planted at his right side, the staff topped by a huge glittering six-armed SNOWFLAKE ICE CRYSTAL in pale cyan, his left hand held out with a short bright FROST WAND spitting a small burst of ice, wearing layered ceremonial robes of WHITE and ICE-BLUE with a thick WHITE FUR COLLAR and silver trim, a tall jagged CRYSTALLINE ICE CROWN on his head, jagged pale-blue ICE-SHARD pauldrons, and a slow SPIRAL of eight pale-blue ice shards and snowflakes swirling up around him (all inside the disc); broad pale highlight planes on every upper-left fold and a thin bright rim light. Robed, crowned with ice, staff-planted and complete.",
      "Orc casters: the ORC HIGH CRYOMANCER is the TALL STAFF-PLANTED FROST-LORD in white and ice-blue robes with a white fur collar, a tall crystal ice crown, jagged ice pauldrons, a huge snowflake crystal atop his staff, a frost wand in the other hand and a spiral of ice shards (silhouette: a tall upright figure with a jagged crown and a tall staff on one side with a big crystal; hue: white, ice-blue, silver and cyan with green skin; value: bright). The shipped orc cryomancer is a plain blue robe, and the high pyromancer of this batch is a wide-armed fire-lord with a flame ring: this must not be a plain robe, must not have spread arms with fire and must not be scarlet.",
      "Bright white and ice-blue robes, white fur, silver trim, pale cyan crystals, green skin, a thin bright rim; nothing darker than mid ice-blue except eye slits and fold seams; NO navy or dark blue robe, no black; the frost glow stays on the figure and must not tint the disc, which stays neutral charcoal at reference lightness." + DISC,
      "READY single, no define_as (orc high cryomancer)", comp=COMP + FIT + COMPACT + BRIGHT + DARKFIX)

asset(2, 'vampire-lord', 'vampire lord',
      "dreadfell pool and the greater-vault crypt and paladin-vs-vampire vaults (general/npcs/vampire.lua:135, undead/vampire, non-unique, no define_as, rank 3, base BASE_NPC_VAMPIRE, explicit image=npc/vampire_lord.png); the only definition of this name; the vaults pick it with random_filter name=vampire lord (the same leaf); npc/vampire_lord_02.png is only a facings flip entry",
      [src(VAM, 'name = "vampire lord"'), src(VAM, 'image = "npc/vampire_lord.png"', after='name = "vampire lord"'), src(VAM, 'T_HIEMAL_SHIELD', after='name = "vampire lord"'), src(VAM, 'T_SUMMON', after='name = "vampire lord"'), src(VAM, 'make_escort', after='name = "vampire lord"'), src(VAM, 'define_as = "BASE_NPC_VAMPIRE"')],
      src(VAM, 'define_as = "BASE_NPC_VAMPIRE"'), None, 'undead', 'vampire', False, False,
      'base BASE_NPC_VAMPIRE (undead/vampire, no image=, no shader);' + EXPL + '; the base calls resolvers.sustains_at_birth() and Blur Sight, Phantasmal Shield and Hiemal Shield are the sustained talents (particles and temporary values); no equip, no auto_classes; Summon builds random undead leaves that wear their own tokens',
      'vampire_lord.png',
      [STY, IDN('vampire_lord.png', 'Native shape (64x64): a dark-haired pale man in a long ochre-gold tunic with a gold sash and a heavy brown cloak lined with red, a slim sword raised in one hand. Keep the noble in the ochre-gold tunic and lined cloak raising a slim sword, drawn as ONE compact figure filling the disc, with red eyes and a pale face, clearly not the red-caped vampire or the blue-caped master.'), REF_VAMPIRES],
      "A vampire lord seen from a steep overhead three-quarter angle: a tall elegant pale-faced NOBLE with slicked dark hair, glowing red eyes and small fangs, in a long OCHRE-GOLD tunic with a broad gold sash and high stiff collar, a heavy BRONZE-BROWN CLOAK lined with bright CRIMSON swept out behind his shoulders, black-and-gold trimmed sleeves, tan boots, a slim bright steel RAPIER raised in the right hand at a diagonal and the left hand held open with a small pale chill of frost; broad pale highlight planes on every upper-left fold and a thin bright rim light. Noble, gold-robed, armed and complete.",
      "Vampires: the VAMPIRE LORD is the OCHRE-GOLD ROBED NOBLE with a bronze-brown crimson-lined cloak and a raised rapier (silhouette: a tall figure with a swept cloak and one diagonal blade; hue: ochre gold, bronze and crimson lining with a pale face; value: mid-light). The shipped lesser vampire is an orange-shirted man, the vampire a red-caped lunging man, the master vampire a blue-caped man and the elder vampire a plum hooded robe: this must not have a red, blue or plum cloak and must not be hooded.",
      "Ochre-gold tunic, bronze-brown cloak with crimson lining, pale face, red eyes, steel blade, tan boots, a thin bright rim; nothing darker than mid bronze except hair and eye slits; NO black cloak; the disc stays neutral charcoal at reference lightness." + DISC,
      "READY single, no define_as, explicit image= (vampire lord)", comp=COMP + FIT + COMPACT + BRIGHT + DARKFIX)

asset(2, 'ungolmor', 'ungolmor',
      "ardhungol pool (general/npcs/spider.lua:182, spiderkin/spider, non-unique, no define_as, rank 3, base BASE_NPC_SPIDER, default-name image); the only definition of this name (Ungole is a different unique with its own token)",
      [src(SPI, 'name = "ungolmor"'), src(SPI, 'T_BITE_POISON', after='name = "ungolmor"'), src(SPI, 'T_DARKNESS', after='name = "ungolmor"'), src(SPI, 'resolvers.sustains_at_birth()'), src(SPI, 'define_as = "BASE_NPC_SPIDER"')],
      src(SPI, 'define_as = "BASE_NPC_SPIDER"'), None, 'spiderkin', 'spider', False, False,
      'base BASE_NPC_SPIDER (spiderkin/spider, no image=, no shader);' + DEFC + '; the base calls resolvers.sustains_at_birth() but none of the leaf talents is sustained (Spider Web, Lay Web, Regeneration, Bite Poison, Darkness, Rush and Stun are activated or passive); color={0,0,0} is a colour value only; no equip, no auto_classes',
      'spiderkin_spider_ungolmor.png',
      [STY, IDN('spiderkin_spider_ungolmor.png', 'Native shape (64x64): a huge squat grey-black spider with heavy thick folded hide and pale steel-grey legs. Keep the heavy dome-bodied spider with thick overlapping folds, drawn as ONE compact figure filling the disc, in mid slate-blue-grey with pale silver ridges and amber eyes instead of near-black.'), REF_SPIDERS],
      "An ungolmor seen from a steep overhead three-quarter angle: the LARGEST and heaviest of the spiderkin, a squat DOME-BODIED spider whose thick hide hangs in overlapping armoured FOLDS and ridges like a rhinoceros, painted in mid SLATE-BLUE-GREY with broad pale SILVER-GREY ridge highlights along every fold, eight short thick legs with pale steel-grey joints and small hooked claws splayed evenly around the body, a cluster of six glowing bright AMBER eyes and two broad pale mandibles with a drop of green venom; broad pale highlight planes on every upper-left fold and a thin bright rim light. Armoured, folded, heavy and complete.",
      "Spiders: the UNGOLMOR is the SQUAT HEAVY DOME-BODIED SPIDER with rhinoceros-like armoured folds, short thick legs and amber eyes (silhouette: a wide low dome with eight short legs splayed all round; hue: slate blue-grey with silver ridges and amber; value: mid). The shipped giant spider is a slender dark-grey spider, the chitinous spider a pale bone-white one, Ungole a black spider with a red mark and the weaver patriarch a blue-and-white one: this must not be slender, bone-white, black or blue-and-white.",
      "Mid slate-blue-grey hide, pale silver-grey ridge highlights, steel-grey joints, amber eyes, a drop of green venom, a thin bright rim; nothing darker than mid slate except the seams between folds; NO black body; the disc stays neutral charcoal at reference lightness." + DISC,
      "READY single, no define_as (ungolmor)", comp=COMP + FIT + COMPACT + BRIGHT + DARKFIX)

# ---- pack 3: Arch Zephyr, Rotting Titan, Heavy Sentinel, Void Spectre ----
asset(3, 'arch-zephyr', 'Arch Zephyr',
      "rak-shor-pride boss (zones/rak-shor-pride/npcs.lua:304, undead/vampire, UNIQUE, define_as ARCH_ZEPHYR, rank 3.5, base BASE_NPC_VAMPIRE, resolvers.nice_tile tall body); the only definition of this name",
      [src(RSP, 'name = "Arch Zephyr"'), src(RSP, 'define_as="ARCH_ZEPHYR"'), src(RSP, 'resolvers.nice_tile', after='name = "Arch Zephyr"'), src(RSP, 'T_THUNDERSTORM', after='name = "Arch Zephyr"'), src(RSP, 'resolvers.equip', after='name = "Arch Zephyr"'), src(VAM, 'define_as = "BASE_NPC_VAMPIRE"')],
      src(VAM, 'define_as = "BASE_NPC_VAMPIRE"'), 'ARCH_ZEPHYR', 'undead', 'vampire', True, False,
      'base BASE_NPC_VAMPIRE (undead/vampire, no image=, no shader);' + tall_unique('undead_vampire_arch_zephyr') + ';' + DEFD + ' (ARCH_ZEPHYR); the base calls resolvers.sustains_at_birth() and Blur Sight, Phantasmal Shield, Feather Wind, Thunderstorm, Tempest and Hurricane are sustained (particles and temporary values only); resolvers.equip a longbow and arrows (equipment only, no moddable_tile); no auto_classes',
      'undead_vampire_arch_zephyr.png',
      [STY, IDN('undead_vampire_arch_zephyr.png', 'Native shape (64x128, tall): a pale old vampire in a dark purple hooded robe with a bow, lightning crawling over his body and the bow. Keep the robed vampire archer with the electric bow and lightning arcs, drawn as ONE compact figure filling the disc, no tall canvas, in gale-grey and storm-blue wind-swept robes with a lightning-wrapped drawn longbow, clearly not the plum-hooded elder vampire.'), REF_VAMPIRES],
      "Arch Zephyr seen from a steep overhead three-quarter angle: an ancient pale-faced VAMPIRE ARCHER in a wide braced stance drawing a big LONGBOW with an arrow of white-yellow LIGHTNING nocked, the bow and his outstretched arm wrapped in crackling electric-blue arcs, long tarnished-silver hair and red eyes, wearing billowing WIND-SWEPT robes in light GALE-GREY and STORM-BLUE with a pale silver-white lining, the hem and sleeves streaming sideways in a gale, forked bright yellow-white LIGHTNING bolts arcing over the robes (all close to the body); broad pale highlight planes on every upper-left fold and a thin bright rim light. Wind-swept, drawing, crackling and complete.",
      "Vampires: ARCH ZEPHYR is the WIND-SWEPT VAMPIRE ARCHER drawing a lightning-wrapped longbow in gale-grey and storm-blue robes with forked lightning (silhouette: a braced side-on figure with a big bow arc and streaming robes; hue: gale grey, storm blue, silver and lightning yellow-white with a pale face; value: light). The shipped elder vampire is a plum hooded robe with a purple orb, the master vampire a blue-caped man, the vampire a red-caped man and the Master a crimson-robed figure: this must not be plum, purple, hooded, red or a standing caster, and must be drawing a bow.",
      "Light gale-grey and storm-blue robes, silver-white lining, pale face, silver hair, red eyes, brown longbow, white-yellow and electric-blue lightning, a thin bright rim; nothing darker than mid storm-blue except eye slits and fold seams; NO dark purple or black robe; the lightning glow stays on the figure and must not tint the disc, which stays neutral charcoal at reference lightness." + DISC,
      "READY tall unique, define_as ARCH_ZEPHYR (Arch Zephyr)", comp=COMP + FIT + COMPACT + BRIGHT + DARKFIX + CATS)

asset(3, 'rotting-titan', 'Rotting Titan',
      "rak-shor-pride boss (zones/rak-shor-pride/npcs.lua:119, undead/ghoul, UNIQUE, define_as ROTTING_TITAN, rank 3.5, base BASE_NPC_GHOUL, resolvers.nice_tile tall body); the only definition of this name",
      [src(RSP, 'name = "Rotting Titan"'), src(RSP, 'define_as = "ROTTING_TITAN"'), src(RSP, 'resolvers.nice_tile', after='name = "Rotting Titan"'), src(RSP, 'T_CRYSTALLINE_FOCUS', after='name = "Rotting Titan"'), src(RSP, 'resolvers.sustains_at_birth()', after='name = "Rotting Titan"'), src(GHL, 'define_as = "BASE_NPC_GHOUL"')],
      src(GHL, 'define_as = "BASE_NPC_GHOUL"'), 'ROTTING_TITAN', 'undead', 'ghoul', True, False,
      'base BASE_NPC_GHOUL (undead/ghoul, no image=, no shader, no sustains_at_birth);' + tall_unique('undead_ghoul_rotting_titan') + ';' + DEFD + ' (ROTTING_TITAN); the leaf calls resolvers.sustains_at_birth() and Crystalline Focus and Onslaught are sustained (Crystalline Focus adds native shader-aura bookkeeping the matcher ignores); on_move only shakes the ground and on_added_to_level only sets can_pass; resolvers.equip only the Rotting Maul; no auto_classes',
      'undead_ghoul_rotting_titan.png',
      [STY, IDN('undead_ghoul_rotting_titan.png', 'Native shape (64x128, tall): a colossal pale grey-mauve hulk of flesh and stone with raised boulder fists and small dark eyes. Keep the colossal hulk of flesh fused with stone slabs, boulder-fists on every limb and a small sunken head, drawn as ONE compact figure filling the disc, no tall canvas, in dusky mauve flesh, pale limestone-beige stone and sickly green rot patches.'), REF_GHOULS],
      "The Rotting Titan seen from a steep overhead three-quarter angle: a COLOSSAL slow hulk standing on the disc as one compact mass, its body assembled from bulging dusky MAUVE-ROSE rotting flesh fused with huge slabs and boulders of pale LIMESTONE-BEIGE stone, a small sunken head with two glowing green eyes set into the chest-heavy body, a massive BOULDER FIST at the end of EACH of its four limbs (two thick arms raised in front, two stumpy legs), patches of sickly GREEN-YELLOW rot, moss-like fungus and a few exposed pale ribs, cracks in the stone glowing faintly green; broad pale highlight planes on every upper-left stone slab and a thin bright rim light. Rotting, stony, massive and complete.",
      "Ghouls and giants: the ROTTING TITAN is the COLOSSAL HULK OF MAUVE ROTTING FLESH FUSED WITH PALE LIMESTONE SLABS with boulder fists on every limb and sickly green rot (silhouette: a huge broad mass with a tiny head and four heavy boulder-ended limbs; hue: dusky mauve-rose, limestone beige and sickly green-yellow; value: mid-light). The shipped ghoul, ghast and ghoulking are lean brown hunched ghouls, the necrotic mass a pink-brown lump with skulls and the ogres upright tan, red or blue giants: this must not be lean, must not be a pink lump with skulls and must not be an ogre.",
      "Dusky mauve-rose flesh, pale limestone-beige stone slabs, sickly green-yellow rot and faint green glow, pale ribs, a thin bright rim; nothing darker than mid mauve except cracks between slabs and eye sockets; NO black or dark brown mass; the glow stays on the figure and must not tint the disc, which stays neutral charcoal at reference lightness." + DISC,
      "READY tall unique, define_as ROTTING_TITAN (Rotting Titan)", comp=COMP + FIT + COMPACT + BRIGHT + DARKFIX + CATS)

asset(3, 'heavy-sentinel', 'Heavy Sentinel',
      "rak-shor-pride boss (zones/rak-shor-pride/npcs.lua:258, undead/giant, UNIQUE, define_as HEAVY_SENTINEL, rank 3.5, base BASE_NPC_BONE_GIANT, resolvers.nice_tile tall body); the only definition of this name",
      [src(RSP, 'name = "Heavy Sentinel"'), src(RSP, 'define_as = "HEAVY_SENTINEL"'), src(RSP, 'resolvers.nice_tile', after='name = "Heavy Sentinel"'), src(RSP, 'T_BURNING_WAKE', after='name = "Heavy Sentinel"'), src(RSP, 'resolvers.sustains_at_birth()', after='name = "Heavy Sentinel"'), src(BGI, 'define_as = "BASE_NPC_BONE_GIANT"')],
      src(BGI, 'define_as = "BASE_NPC_BONE_GIANT"'), 'HEAVY_SENTINEL', 'undead', 'giant', True, False,
      'base BASE_NPC_BONE_GIANT (undead/giant, no image=, no shader);' + tall_unique('undead_giant_heavy_sentinel') + ';' + DEFD + ' (HEAVY_SENTINEL); the base and the leaf call resolvers.sustains_at_birth() and Arcane Power, Burning Wake (talents/spells/wildfire.lua:78 addShaderAura, native shader-aura bookkeeping the matcher ignores), Wildfire, Arcane Combat, Spellcraft and Fiery Hands are sustained (particles and temporary values); resolvers.equip only the Molten Skin armour; no auto_classes',
      'undead_giant_heavy_sentinel.png',
      [STY, IDN('undead_giant_heavy_sentinel.png', 'Native shape (64x128, tall): a towering cream-white bone giant with a fiery orange glow burning in its chest cavity and a skull head. Keep the towering bone giant with a flaming chest furnace, drawn as ONE compact figure filling the disc, no tall canvas, as ash-grey and ivory bones fused with molten-orange seams, a roaring column of fire in the open ribcage and a horned blazing-eyed skull, clearly not a plain tan bone giant.'), REF_BONE_GIANTS],
      "The Heavy Sentinel seen from a steep overhead three-quarter angle: a towering BONE GIANT forged into a furnace, standing on the disc as one compact mass, its ivory and ash-grey bones FUSED by glowing molten-ORANGE seams into heavy armour plates on the shoulders, arms and legs, a wide-open ribcage in the chest roaring with a tall COLUMN OF WHITE-YELLOW FIRE, a large horned FUSED-BONE SKULL with blazing orange eye sockets, two huge bone fists dripping small embers, small flames licking from the shoulders (flames kept close to the body); broad pale highlight planes on every upper-left bone plate and a thin bright rim light. Forged, blazing, massive and complete.",
      "Bone giants: the HEAVY SENTINEL is the FURNACE BONE GIANT with molten-orange seams fusing ash-grey and ivory armour plates, a roaring flame column in the open ribcage and a horned blazing skull (silhouette: a broad heavy mass with a tall central flame and a horned head; hue: ivory, ash-grey, molten orange and white-yellow fire; value: light with a bright core). The shipped bone giant and heavy bone giant are plain tan bone hulks, the runed bone giant has red glyphs, the eternal bone giant pale lavender bones and the half-finished bone giant a thin lilac skeleton: this must not be plain tan bone, must not have glyphs or lavender and must have the chest furnace fire.",
      "Ivory and ash-grey bone plates, molten-orange seams, white-yellow fire and embers, a thin bright rim; nothing darker than mid ash-grey except gaps between plates and eye rims; NO black bones, no charred black armour; the fire glow stays on the figure and must not tint or light the disc, which stays neutral charcoal at reference lightness." + DISC,
      "READY tall unique, define_as HEAVY_SENTINEL (Heavy Sentinel)", comp=COMP + FIT + COMPACT + BRIGHT + DARKFIX + CATS)

asset(3, 'void-spectre', 'Void Spectre',
      "rak-shor-pride boss (zones/rak-shor-pride/npcs.lua:355, undead/wight, UNIQUE, NO define_as, rank 3.5, base BASE_NPC_WIGHT, resolvers.nice_tile tall body); the only definition of this name",
      [src(RSP, 'name = "Void Spectre"'), src(RSP, 'unique=true', after='name = "Void Spectre"'), src(RSP, 'resolvers.nice_tile', after='name = "Void Spectre"'), src(RSP, 'T_PURE_AETHER', after='name = "Void Spectre"'), src(RSP, 'resolvers.sustains_at_birth()', after='name = "Void Spectre"'), src(WIG, 'define_as = "BASE_NPC_WIGHT"')],
      src(WIG, 'define_as = "BASE_NPC_WIGHT"'), None, 'undead', 'wight', True, False,
      'base BASE_NPC_WIGHT (undead/wight, no image=, no shader);' + tall_unique('undead_wight_void_spectre').replace('UNIQUE with a define_as binding', 'UNIQUE without a define_as (like the Hedge-Wizard)').replace('the entry carries unique=true and define_as but no native_tall flag', 'the entry carries unique=true, no define_as and no native_tall flag') + '; the base and the leaf call resolvers.sustains_at_birth() and Arcane Power, Spellcraft, Shielding, Arcane Shield and Pure Aether are sustained (particles and temporary values only; Aether Avatar style effects are timed effects the matcher rejects while active); resolvers.equip only the Aether Ring; no auto_classes',
      'undead_wight_void_spectre.png',
      [STY, IDN('undead_wight_void_spectre.png', 'Native shape (64x128, tall): a tall thin translucent red humanoid of swirling energy streaks with ragged arms. Keep the gaunt humanoid wraith of swirling arcane energy with long ragged arms, drawn as ONE compact figure filling the disc, no tall canvas, in solid rose-red and magenta with a white-hot face slit and an orbiting ring of pale violet arcane runes, clearly not a cyan ghost or an armoured wight.'), REF_WIGHTS],
      "The Void Spectre seen from a steep overhead three-quarter angle: a gaunt hooded HUMANOID WRAITH standing on the disc as one compact figure, its body a SOLID mass of swirling bright ROSE-RED and hot MAGENTA arcane energy streaks with pale-pink highlight planes, a narrow WHITE-HOT slit for a face under the hood, long ragged trailing sleeves ending in thin clawed hands held out at its sides, and a slow VORTEX RING of pale-violet and white ARCANE RUNE GLYPHS and small sparks orbiting it at chest height, tucked inside the disc; broad pale highlight planes on every upper-left surface and a thin bright rim light. Swirling, hooded, arcane and complete." + CHEAT,
      "Wights and spectres: the VOID SPECTRE is the GAUNT HOODED WRAITH OF ROSE-RED AND MAGENTA ARCANE ENERGY with a white-hot face slit, ragged sleeves and an orbiting ring of pale-violet runes (silhouette: a slim hooded figure with two ragged arms and a ring around it; hue: rose-red, magenta, white-hot and pale violet; value: mid-light). The shipped forest wight is a green armoured shield-bearer, the grave wight a pale cyan ghost, the barrow wight an armoured blue-glowing figure, the Shade of Telos a blue crystalline figure and the dread a purple shroud: this must not be cyan, green, blue, armoured, crystalline or a purple shroud.",
      "Bright rose-red and magenta energy streaks, pale-pink highlights, white-hot face slit, pale-violet and white runes and sparks, a thin bright rim; nothing darker than mid rose except the hood hollow; NO black or dark maroon mass; the glow stays on the figure and must not tint the disc, which stays neutral charcoal at reference lightness." + DISC,
      "READY tall unique, no define_as (Void Spectre)", comp=COMP + FIT + COMPACT + BRIGHT + DARKFIX + CATS)

# ---- pack 4: oozing horror, abyssal horror, umbral horror, degenerated ogric mass ----
asset(4, 'oozing-horror', 'oozing horror',
      "lake-nur pool (general/npcs/horror.lua:554, horror/eldritch (subtype override on BASE_NPC_HORROR), non-unique, no define_as, rank 3, default-name image); the only NPC definition of this name; the Corpathus artifact summons a separate 'Vilespawn' minion that reuses the PNG under another name (world-artifacts.lua:3443), which stays native",
      [src(HOR, 'name = "oozing horror"'), src(HOR, 'T_OOZE_SPIT', after='name = "oozing horror"'), src(HOR, 'on_move = function(self)', after='name = "oozing horror"'), src(HOR, 'define_as = "BASE_NPC_HORROR"')],
      src(HOR, 'define_as = "BASE_NPC_HORROR"'), None, 'horror', 'eldritch', False, False,
      'base BASE_NPC_HORROR (horror, no image=, no shader) with the leaf overriding subtype to eldritch;' + DEFC + '; the leaf has no sustains_at_birth (Resolve, Mana Clash, Ooze Spit, Ooze Roots, Slime Wave and Tentacle Grab are activated or passive); on_move only adds a slime map effect; no equip, no auto_classes',
      'horror_eldritch_oozing_horror.png',
      [STY, IDN('horror_eldritch_oozing_horror.png', 'Native shape (64x64): a big lumpy mound of translucent lime-green slime with orange-amber eyes scattered through it. Keep the massive mound of green slime with many drifting orange eyes, drawn as ONE compact figure filling the disc, much heavier and bigger-looking than the small shipped ooze tokens.'), REF_SLIMES],
      "An oozing horror seen from a steep overhead three-quarter angle: a MASSIVE amorphous MOUND of translucent glossy LIME-GREEN slime filling the disc as one compact heap, seven or eight large round glowing ORANGE-AMBER EYES with dark pupils drifting at different depths through the slime, thick ropes of slime drooping over the mound and a few heavy drips and small pools of ooze hugging its base, big shiny white specular highlights on every upper-left bulge and a thin bright yellow-green rim light. Heaping, glossy, many-eyed and complete.",
      "Slimes: the OOZING HORROR is the MASSIVE MOUND OF LIME-GREEN SLIME with seven or eight large orange-amber eyes (silhouette: a big lumpy heap with many round eyes; hue: lime green with orange-amber eyes; value: mid-light and glossy). The shipped green ooze, green jelly and poison ooze are small shiny single blobs, the bloated horror a pink baby-faced blob, the luminous horror a yellow humanoid and the necrotic mass a pink-brown lump: this must not be small, single-eyed, pink or humanoid, and must show many eyes.",
      "Bright lime and yellow-green translucent slime, orange-amber eyes with small dark pupils, white specular highlights, a thin bright rim; nothing darker than mid green except the pupils and thin creases; NO dark green or black slime; the slime stays on the mound and must not spill across the disc, which stays neutral charcoal at reference lightness." + DISC,
      "READY single, no define_as (oozing horror)", comp=COMP + FIT + COMPACT + BRIGHT + DARKFIX)

asset(4, 'abyssal-horror', 'abyssal horror',
      "lake-nur pool (general/npcs/horror_aquatic.lua:192, horror/aquatic, non-unique, no define_as, rank 3, base BASE_NPC_HORROR_AQUATIC, nice_tile tall body); the only definition of this name",
      [src(HAQ, 'name = "abyssal horror"'), src(HAQ, 'resolvers.nice_tile', after='name = "abyssal horror"'), src(HAQ, 'T_ABYSSAL_SHROUD', after='name = "abyssal horror"'), src(HAQ, 'resolvers.sustains_at_birth()', after='name = "abyssal horror"'), src(HAQ, 'define_as = "BASE_NPC_HORROR_AQUATIC"')],
      src(HAQ, 'define_as = "BASE_NPC_HORROR_AQUATIC"'), None, 'horror', 'aquatic', False, True,
      'base BASE_NPC_HORROR_AQUATIC (horror/aquatic, no image=, no shader, no sustains_at_birth in the base);' + tall_explicit('horror_aquatic_abyssal_horror') + '; the leaf calls resolvers.sustains_at_birth() but none of its talents is sustained (Dark Torrent, Creeping Darkness, Dark Tendrils, Abyssal Shroud, Tentacle Grab are activated, Dark Vision passive); the base on_die only logs an air bubble and touches terrain; no equip, no auto_classes',
      'horror_aquatic_abyssal_horror.png',
      [STY, IDN('horror_aquatic_abyssal_horror.png', 'Native shape (64x128, tall): a pitch-black heaving mass of long tentacles with a pair of deep red eyes hidden inside. Keep the heaving tentacle mass with glowing red eyes buried in it, drawn as ONE compact figure filling the disc, no tall canvas, in deep indigo-violet and slate-teal with pale lilac sucker rows and a cluster of glowing crimson eyes instead of black.'), REF_DARK_HORRORS],
      "An abyssal horror seen from a steep overhead three-quarter angle: a heaving MASS OF WRITHING TENTACLES piled up into one compact dome on the disc, the thick glossy tentacles in deep INDIGO-VIOLET and SLATE-TEAL with broad pale-lilac highlight planes on every upper-left coil, rows of pale LILAC SUCKERS along their undersides, hooked tips curling back inward, and buried in the tangle at the centre a cluster of four to six glowing bright CRIMSON-RED EYES with hot orange-white pupils staring out from the gaps; a thin bright lilac rim light. Heaving, tangled, red-eyed and complete.",
      "Aquatic horrors: the ABYSSAL HORROR is the HEAVING DOME OF WRITHING INDIGO-VIOLET TENTACLES with glowing crimson eyes buried in the centre (silhouette: a round tangled tentacle pile with hooked tips and a few eyes in the middle; hue: indigo-violet and slate-teal with lilac suckers and crimson eyes; value: mid). The shipped entrenched horror is a limestone pillar in a teal tentacle wreath, the ravenous horror a fanged fish head, the weirdling beast a purple-pink tentacled beast and the horned horror a purple horned beast: this must not have a stone pillar, a fish head, a horned beast body or teal-only tentacles, and must be a pure tentacle mass with red eyes.",
      "Deep indigo-violet and slate-teal glossy tentacles, pale lilac suckers and highlights, glowing crimson eyes with orange-white pupils, a thin bright lilac rim; nothing darker than mid indigo except thin gaps between coils; NO black tentacles, no black mass; the eye glow stays on the figure and must not tint the disc, which stays neutral charcoal at reference lightness." + DISC,
      "READY tall (abyssal horror, native_tall)", comp=COMP + FIT + COMPACT + BRIGHT + DARKFIX + CATS)

asset(4, 'umbral-horror', 'umbral horror',
      "lake-nur pool (general/npcs/horror.lua:613, horror/eldritch (subtype override on BASE_NPC_HORROR), non-unique, no define_as, rank 3, resolvers.nice_tile tall body); the only definition of this name",
      [src(HOR, 'name = "umbral horror"'), src(HOR, 'resolvers.nice_tile', after='name = "umbral horror"'), src(HOR, 'T_STEALTH', after='name = "umbral horror"'), src(HOR, 'T_SHADOW_WARRIORS', after='name = "umbral horror"'), src(HOR, 'resolvers.sustains_at_birth()', after='name = "umbral horror"'), src(HOR, 'define_as = "BASE_NPC_HORROR"')],
      src(HOR, 'define_as = "BASE_NPC_HORROR"'), None, 'horror', 'eldritch', False, True,
      'base BASE_NPC_HORROR (horror, no image=, no shader) with the leaf overriding subtype to eldritch;' + tall_explicit('horror_eldritch_umbral_horror') + '; the leaf calls resolvers.sustains_at_birth() and Call Shadows and Stealth are sustained (particles and temporary values only); Shadow Warriors and Focus Shadows build subtype shadow allies, not copies of this body; no equip, no auto_classes',
      'horror_eldritch_umbral_horror.png',
      [STY, IDN('horror_eldritch_umbral_horror.png', 'Native shape (64x128, tall): a black jagged crouching shadow-stalker with long thin claws and swept-back spikes. Keep the lithe jagged crouched shadow-stalker with hooked claws and thorn spikes, drawn as ONE compact figure filling the disc, no tall canvas, in smoky pearl-grey and dusk-lavender shadow with a bright lilac rim and two pale-yellow eyes instead of black.'), REF_DARK_HORRORS],
      "An umbral horror seen from a steep overhead three-quarter angle: a lithe JAGGED SHADOW-STALKER crouched low on the disc in a wary stalking pose as one compact figure, its body made of smoky PEARL-GREY and DUSK-LAVENDER shadow-stuff with large broad lighter grey-lilac planes on every upper-left surface, long thin HOOKED CLAWS on both hands held forward, a crest of backswept thorn-like SPIKES down its head and spine, a ragged tapering tail, two bright PALE-YELLOW slit EYES, and a few curling wisps of pale violet shadow rising off it (all close to the body); a thin bright lilac-white rim light along the whole outline. Crouched, jagged, smoky and complete." + CHEAT,
      "Eldritch horrors: the UMBRAL HORROR is the LITHE CROUCHED JAGGED SHADOW-STALKER of smoky pearl-grey and dusk-lavender with hooked claws, thorn spikes and two pale-yellow eyes (silhouette: a low spiky crouch with forward claws and a crest; hue: pearl-grey, dusk-lavender and pale yellow; value: mid-light). The shipped horned horror is a purple horned beast, the weirdling beast a purple-pink tentacled beast, the dread a purple hooded shroud and the void horror an indigo lens: this must not be a tentacle mass, must not be horned or hooded, and must not be black.",
      "Smoky pearl-grey and dusk-lavender shadow-stuff, pale grey-lilac highlight planes, pale-yellow eyes, pale violet wisps, a thin bright lilac-white rim; nothing darker than mid dusk-lavender except the eye slits and thin gaps between spikes; NO black body, no black wisps; the disc stays neutral charcoal at reference lightness." + DISC,
      "READY tall (umbral horror, native_tall)", comp=COMP + FIT + COMPACT + BRIGHT + DARKFIX + CATS)

asset(4, 'degenerated-ogric-mass', 'degenerated ogric mass',
      "conclave-vault zone pool (zones/conclave-vault/npcs.lua:61, giant/ogre, non-unique, no define_as, rank 2, base BASE_NPC_OGRE via ogre.lua loaded with switchRarity, resolvers.nice_tile{tall=1}); the only definition of this name",
      [src(CVN, 'name = "degenerated ogric mass"'), src(CVN, 'resolvers.nice_tile{tall=1}', after='name = "degenerated ogric mass"'), src(CVN, 'T_CATALEPSY', after='name = "degenerated ogric mass"'), src(CVN, 'load("/data/general/npcs/ogre.lua", switchRarity("special_rarity"))'), src(OGR, 'resolvers.sustains_at_birth()'), src(OGR, 'define_as = "BASE_NPC_OGRE"'), src('resolvers.lua', 'function resolvers.calc.nice_tile', root='game/modules/tome/')],
      src(OGR, 'define_as = "BASE_NPC_OGRE"'), None, 'giant', 'ogre', False, True,
      'base BASE_NPC_OGRE (giant/ogre, no image=, no shader); the base calls resolvers.sustains_at_birth() but none of the leaf talents is sustained (Epidemic, Rotting Disease, Weapon Combat and Catalepsy are activated or passive);' + tall_short('giant_ogre_degenerated_ogric_mass.png') + '; resolvers.equip a greatmaul (equipment only, no moddable_tile); no auto_classes',
      'giant_ogre_degenerated_ogric_mass.png',
      [STY, IDN('giant_ogre_degenerated_ogric_mass.png', 'Native shape (64x128, tall): a slumped tree-stump-like heap of warty brown-red deformed flesh with stubby limbs and a twisted lump on top. Keep the slumped heap of deformed flesh with malformed limbs, drawn as ONE compact figure filling the disc, no tall canvas, in ochre-tan flesh with blue-grey bruises, tumours and a half-buried tusked ogre face.'), REF_OGRES],
      "A degenerated ogric mass seen from a steep overhead three-quarter angle: a slumped HEAP of bulging OCHRE-TAN and salmon flesh that was once an ogre, piled on the disc as one compact lump, rolls of sagging skin, big round TUMOURS with pale yellow pustules, patches of blue-grey BRUISING, three or four MALFORMED stubby fused limbs with lumpy hands sprouting at odd angles, ropy brown tendons, and a half-buried TUSKED OGRE FACE with one sunken eye and a drooling crooked jaw pushed out of the top of the heap; broad pale highlight planes on every upper-left bulge and a thin bright rim light. Slumped, lumpy, malformed and complete.",
      "Ogres: the DEGENERATED OGRIC MASS is the SLUMPED HEAP OF OCHRE-TAN DEFORMED FLESH with tumours, malformed fused limbs and a half-buried tusked ogre face (silhouette: a low lumpy heap with a face poking out of the top; hue: ochre-tan and salmon with blue-grey bruises; value: mid-light). The shipped ogre guard, mauler, pounder and warmaster are upright tan, red, blue and armoured ogre fighters, the necrotic mass a pink-brown lump with skulls and the bloated horror a pink baby-faced blob: this must not be an upright ogre fighter, must not be pink with skulls and must not have a baby face.",
      "Ochre-tan and salmon flesh, blue-grey bruises, pale yellow pustules, brown tendons, ivory tusks, a thin bright rim; nothing darker than mid tan-brown except the eye socket and skin creases; NO black or dark brown mass; the disc stays neutral charcoal at reference lightness." + DISC,
      "READY tall (degenerated ogric mass, native_tall via nice_tile{tall=1})", comp=COMP + FIT + COMPACT + BRIGHT + DARKFIX + CATS)

# ---- pack 5: ogric abomination ----
asset(5, 'ogric-abomination', 'ogric abomination',
      "conclave-vault zone pool (zones/conclave-vault/npcs.lua:79, giant/ogre, non-unique, no define_as, rank 3, base BASE_NPC_OGRE via ogre.lua loaded with switchRarity, resolvers.nice_tile{tall=1}); the only definition of this name",
      [src(CVN, 'name = "ogric abomination"'), src(CVN, 'resolvers.nice_tile{tall=1}', after='name = "ogric abomination"'), src(CVN, 'T_GOLEM_REFLECTIVE_SKIN', after='name = "ogric abomination"'), src(CVN, 'load("/data/general/npcs/ogre.lua", switchRarity("special_rarity"))'), src(OGR, 'resolvers.sustains_at_birth()'), src(OGR, 'define_as = "BASE_NPC_OGRE"'), src('resolvers.lua', 'function resolvers.calc.nice_tile', root='game/modules/tome/')],
      src(OGR, 'define_as = "BASE_NPC_OGRE"'), None, 'giant', 'ogre', False, True,
      'base BASE_NPC_OGRE (giant/ogre, no image=, no shader); the base calls resolvers.sustains_at_birth() and Golem Reflective Skin is the leaf sustain (talents/spells/golem.lua:325 addShaderAura, native shader-aura bookkeeping on add_mos that the matcher ignores);' + tall_short('giant_ogre_ogric_abomination.png') + '; resolvers.equip a greatmaul (equipment only, no moddable_tile); no auto_classes',
      'giant_ogre_ogric_abomination.png',
      [STY, IDN('giant_ogre_ogric_abomination.png', 'Native shape (64x128, tall): a hulking grey-mauve ogre with purple crystals grafted on its body, one arm a lumpy golem arm, swinging a big club overhead. Keep the hulking ogre with grafted stone golem parts and a raised maul, drawn as ONE compact figure filling the disc, no tall canvas, in mottled grey-mauve skin with a huge pale stone golem arm and glowing violet-cyan runes.'), REF_OGRES],
      "An ogric abomination seen from a steep overhead three-quarter angle: a hulking OGRE with mottled GREY-MAUVE skin and a heavy brutish tusked face, one arm ordinary and gripping a big brown wooden GREATMAUL raised diagonally over the shoulder, the OTHER ARM replaced by a huge pale limestone STONE GOLEM ARM ending in a boulder fist with glowing VIOLET-CYAN RUNES, more STONE PLATES bolted onto the shoulder and chest with brass rivets, small violet crystals sprouting at the seams where the stone joins the flesh, a tattered brown leather loincloth and heavy bare feet; broad pale highlight planes on every upper-left surface and a thin bright rim light. Grafted, hulking, armed and complete.",
      "Ogres: the OGRIC ABOMINATION is the HULKING GREY-MAUVE OGRE with one huge pale STONE GOLEM ARM with glowing violet-cyan runes, bolted stone plates and a raised greatmaul (silhouette: a broad brute with one oversized stone arm and a diagonal maul; hue: grey-mauve skin, pale limestone stone and violet-cyan glow; value: mid-light). The shipped ogre guard is a tan hammer ogre, the mauler a red ogre, the pounder a blue ogre, the warmaster a plate-armoured ogre and the rune-spinner an orange caster: this must not be tan, red, blue, orange or plate-armoured and must have the stone arm.",
      "Mottled grey-mauve skin, pale limestone stone arm and plates, violet-cyan runes and crystals, brass rivets, brown maul and loincloth, a thin bright rim; nothing darker than mid grey-mauve except eye slits and seams; NO black or dark brown mass; the rune glow stays on the figure and must not tint the disc, which stays neutral charcoal at reference lightness." + DISC,
      "READY tall (ogric abomination, native_tall via nice_tile{tall=1})", comp=COMP + FIT + COMPACT + BRIGHT + DARKFIX + CATS)


# Packs 1-2 measured a pattern (orc high pyromancer 0.941, orc high cryomancer 1.034, vampire lord 1.008: weapons, arms and effects crossing the disc rim).
# Packs 3-5 had not been run yet, so their prompts carry this calibration from the first call.
TIGHT = " CALIBRATION FROM EARLIER TOKENS OF THIS BATCH (three first generations failed the disc-geometry gate because arms, weapons and effects crossed the disc rim): draw the whole creature clearly SMALLER than feels natural, everything (limbs, weapons, wisps, flames, tentacles, cloth ends, shards and effects) inside a circle of about 0.58 of the disc radius, centred, with a wide bare ring of plate on every side; hold every weapon, arm and effect tight against the body; no cast shadow onto the plate."
for _a in A:
    if _a['pack'] in (3, 4, 5):
        _a['comp'] = (_a['comp'] or COMP) + TIGHT


def retry(id_, pack, **changes):
    base = next(a for a in A if a['id'] == id_)
    A.append(dict(base, pack=pack, **changes))


exec((HERE / 'retries.py').read_text()) if (HERE / 'retries.py').exists() else None


TALL_IDS = tuple(a['id'] for a in A if a['native_tall'])
UNIQUE_TALL_IDS = ('glacial-legion', 'arch-zephyr', 'rotting-titan', 'heavy-sentinel', 'void-spectre')
SHORTHAND_IDS = ('degenerated-ogric-mass', 'ogric-abomination')
TALL_BODY_IDS = TALL_IDS + UNIQUE_TALL_IDS
EXPL_IDS = ('vampire-lord',)
PNGF = {a['id']: 'NPC.lua:33 default-name image on the leaf (no image=/nice_tile)' for a in A}
PNGF.update({i: 'explicit image= on the leaf (no nice_tile/add_mos)' for i in EXPL_IDS})
PNGF.update({i: 'NPC.lua:33 default-name image on the leaf plus an explicit nice_tile tall body (image=invis.png, one add_mos entry with display_h=2, display_y=-1 naming the same PNG)' for i in TALL_IDS + UNIQUE_TALL_IDS if i not in SHORTHAND_IDS})
PNGF.update({i: 'NPC.lua:33 default-name image via resolvers.nice_tile{tall=1} (live-confirmed shorthand, as for the ogre guard, mauler, rune-spinner and pounder)' for i in SHORTHAND_IDS})
EVDIR = 'evidence/monster-batch-ac-20260930/source-contracts.json'
DEFINE = {a['id']: a['define_as'] for a in A}
NAMES_LIST = "Aletta Soultorn, ruin banshee, Filio Flightfond, orc high pyromancer, orc high cryomancer, Glacial Legion, Arch Zephyr, Rotting Titan, Heavy Sentinel, Void Spectre, oozing horror, abyssal horror, ungolmor, umbral horror, vampire lord, degenerated ogric mass, ogric abomination"


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
        if a['id'] in TALL_BODY_IDS:
            ident['tall_body'] = {'image': 'invis.png', 'add_mos': [{'image': native_image, 'display_h': 2, 'display_y': -1}],
                                  'catalog_flag': ('unique=true (unique tall path, no native_tall flag)' if a['unique'] else 'native_tall=true'),
                                  'static_pin': ('nice_tile{tall=1} expands to this body (resolvers.lua nice_tile); not unique, so no unique-only tall path applies') if a['id'] in SHORTHAND_IDS else ('nice_tile names the tall PNG explicitly; unique, so the unique tall path applies' if a['unique'] else 'nice_tile names the tall PNG explicitly; not unique, so no unique-only tall path applies')}
        if a['base']:
            ident['base_source'] = a['base']
        if len(a['srcs']) > 1:
            ident['extra_sources'] = a['srcs'][1:]
        identities.append(ident)
    findings = [
        "All seventeen names have exactly one NPC leaf definition under game/modules/tome (grep of every actor definition, zones included). The zone pools and vaults (greater-crypt for the ruin banshee, crypt and paladin-vs-vampire for the vampire lord, renegade-pyromancers for the orc high pyromancer) only build those same leaves through name/random_filter lookups; the renegade-pyromancers vault makes a random boss 'the Invoker' from the flat orc high pyromancer entry, which goes through the existing captureRandomOrigin path (tests exist).",
        "Summons that copy a monster wear its token: the vampire lord's Summon builds random undead leaves that wear their own tokens; no talent, effect or event builds a copy of any of the seventeen bodies under its own name. Shadow Warriors and Focus Shadows (umbral horror) build subtype shadow allies, not copies.",
        "Kept native by design: the Corpathus artifact's 'Vilespawn' minion (world-artifacts.lua:3443) reuses the oozing horror PNG under its own name and fields; it is a differently named artifact minion with its own hard-coded stat block, not a summon of an oozing horror, and mapping it would need a name-alias mechanism the catalog does not have. Left native and reported.",
        "Uniques (Aletta Soultorn ALETTA, Filio Flightfond FILIO, Glacial Legion GLACIAL_LEGION, Arch Zephyr ARCH_ZEPHYR, Rotting Titan ROTTING_TITAN, Heavy Sentinel HEAVY_SENTINEL, Void Spectre without a define_as) each get a token of their own; the five tall uniques carry unique=true and no native_tall flag (nativeTallImage accepts their body through the unique path, like the Hedge-Wizard); Void Spectre, like the Hedge-Wizard, has no define_as and is matched by exact name, type, subtype and unique flag. No non-unique actor can borrow their names or PNGs.",
        "Same-family separation: the orc high pyromancer and cryomancer are ordinary leaves with their own names and PNGs (the plain pyromancer and cryomancer tokens are unchanged and reject the high names, and the reverse); the vampire lord and Arch Zephyr are distinct leaves from the vampire, master vampire and elder vampire; the ogric abomination and degenerated ogric mass are separate leaves from every shipped ogre.",
        "Degenerated ogric mass and ogric abomination, abyssal horror and umbral horror are non-unique tall bodies (nice_tile{tall=1} shorthand for the two ogres, explicit nice_tile for the two horrors) and carry native_tall=true; a random boss made from such an entry stays native (existing behaviour, tests exist). Golem Reflective Skin, Burning Wake and Crystalline Focus add native shader-aura bookkeeping the matcher ignores.",
        "Result: no per-identity `variants` entry and no `image_aliases` entry is needed for this batch.",
    ]
    ev = {'schema': 1,
          'task': "monster-batch-ac: static re-verification (no game launch) of the seventeen identities that remain in the survey-2 unscheduled list after batch AB, the FINAL batch, everything except Training Dummy (" + NAMES_LIST + ") against game/modules/tome source and native sprites. Every field below was read from source: name, type/subtype, define_as (six bind one), explicit or NPC.lua:33 default image, unique (seven), PNG on disk, and absence of moddable_tile/shader/anim/add_displays on each leaf and its base. Findings: nine identities are tall bodies (five unique: Glacial Legion, Arch Zephyr, Rotting Titan, Heavy Sentinel, Void Spectre; four non-unique native_tall: abyssal horror, umbral horror, degenerated ogric mass, ogric abomination), eight are 64x64 single images (Aletta Soultorn, ruin banshee, Filio Flightfond, orc high pyromancer, orc high cryomancer, oozing horror, ungolmor use the NPC.lua:33 default-name image; the vampire lord names its PNG with image=).",
          'new_ids_not_in_catalog_before_this_batch': [i['id'] for i in identities], 'identities': identities,
          'runtime_mutation_scan': {
              'method': "every talent of each identity (resolvers.talents, inherited base talents and the base-file talent lists) was resolved under game/modules/tome/data/talents and its mode read (sustained/activated/passive); the same talents/ and timed_effects/ greps for writes to type/subtype/image/add_mos/add_displays/moddable_tile/replace_display/shader/updateModdableTile as batches S to AB were applied and give the same writer set; the resolvers sustains_at_birth, inscriptions, equip, racial and nice_tile and the base-file resolvers were read; every auto_classes site under zones/, general/ and maps/ was listed with its leaf name.",
              'writers_found': [
                  {'file': 'game/modules/tome/data/talents/corruptions/shadowflame.lua', 'line': 97, 'talent': "Flame of Urh'Rok", 'effect': 'sustain: __old_type={type,subtype}; type,subtype = demon,major; image untouched; restored on deactivate'},
                  {'file': 'game/modules/tome/data/talents/psionic/thought-forms.lua', 'line': 93, 'talent': 'thought-form summons (Solipsist tree)', 'effect': 'sets type/subtype/image/moddable_tile/add_mos on the summoned minion copied from its summoner, never on the caster'},
                  {'file': 'game/modules/tome/data/talents/chronomancy/anomalies.lua', 'line': 587, 'talent': 'anomaly summons', 'effect': 'creates a separate spawned NPC with another image; not any identity of this batch'}],
              'other_hits_reviewed': [
                  'talents/spells/golemancy.lua and talents/uber/mag.lua (player-only moddable_tile writes: the player alchemist golem and lich transformation; no identity of this batch)',
                  'talents/spells/wildfire.lua:78 Burning Wake (orc high pyromancer, Heavy Sentinel), talents/spells/golem.lua:325 Golem Reflective Skin (ogric abomination) and talents/spells/earth.lua:112 / chronomancy/matter.lua:134 stone-skin style auras (Crystalline Focus, Rotting Titan): native shader-aura bookkeeping on add_mos, ignored by the matcher (emptyIgnoringAura / nativeTallImage)',
                  'talents/spells/phantasm.lua:187 and talents/misc/inscriptions.lua:862 (illusions copy the caster add_mos onto a separate summoned image actor with its own name; not a copy of these bodies under their own names)',
                  'timed_effects/physical.lua and other.lua (add_displays/replace_display only while the effect is active)', 'timed_effects/magical.lua (invisibility, shadow veil and similar shaders, only while active)'],
              'timed_effects_review': "timed_effects write shader, replace_display, add_displays or image only while active (invisibility shaders, stone/ice/pin displays, Wrathroot, Shivgoroth form, dragon egg, Lord of Skulls): the matcher rejects them (native art shows) and restores the token when they end.",
              'sustains_at_birth_review': [
                  {'identity': 'Aletta Soultorn', 'sustained': ['Gloom'], 'note': 'temporary values and particles only'},
                  {'identity': 'orc high pyromancer', 'sustained': ['Burning Wake', 'Spellcraft', 'Essence of Speed'], 'note': 'Burning Wake adds native shader-aura bookkeeping to add_mos, ignored by the matcher; the others are particles and temporary values'},
                  {'identity': 'orc high cryomancer', 'sustained': ['Spellcraft', 'Essence of Speed'], 'note': 'particles and temporary values only'},
                  {'identity': 'Glacial Legion', 'sustained': ['Uttercold', 'Spellcraft', 'Frost Hands'], 'note': 'the base calls resolvers.sustains_at_birth(); particles and temporary values only'},
                  {'identity': 'Arch Zephyr', 'sustained': ['Blur Sight', 'Phantasmal Shield', 'Feather Wind', 'Thunderstorm', 'Tempest', 'Hurricane'], 'note': 'particles and temporary values only'},
                  {'identity': 'Rotting Titan', 'sustained': ['Crystalline Focus', 'Onslaught'], 'note': 'Crystalline Focus adds native shader-aura bookkeeping, ignored by the matcher'},
                  {'identity': 'Heavy Sentinel', 'sustained': ['Arcane Power', 'Burning Wake', 'Wildfire', 'Arcane Combat', 'Spellcraft', 'Fiery Hands'], 'note': 'Burning Wake adds native shader-aura bookkeeping, ignored by the matcher; the others are particles and temporary values'},
                  {'identity': 'Void Spectre', 'sustained': ['Arcane Power', 'Spellcraft', 'Shielding', 'Arcane Shield', 'Pure Aether'], 'note': 'particles and temporary values only'},
                  {'identity': 'umbral horror', 'sustained': ['Call Shadows', 'Stealth'], 'note': 'particles and temporary values only'},
                  {'identity': 'vampire lord', 'sustained': ['Blur Sight', 'Phantasmal Shield', 'Hiemal Shield'], 'note': 'the base calls resolvers.sustains_at_birth(); particles and temporary values only'},
                  {'identity': 'ogric abomination', 'sustained': ['Golem Reflective Skin'], 'note': 'the base calls resolvers.sustains_at_birth(); addShaderAura bookkeeping, ignored by the matcher'},
                  {'identity': 'ruin banshee, Filio Flightfond, ungolmor, oozing horror, abyssal horror, degenerated ogric mass', 'sustained': [], 'note': 'no sustained talent on the leaf (Filio has no talents block)'}],
              'auto_classes_review': [
                  {'identity': 'all seventeen', 'class': 'none', 'finding': "none of the seventeen leaves or their bases has auto_classes; every auto_classes site in zones/, general/ and maps/ belongs to another leaf, so none can reach Flame of Urh'Rok and there is no urh_rok_form opt-in."}],
              'visibility_review': 'Identities with stealth or invisibility (Aletta Soultorn, ruin banshee, umbral horror, orc high casters through runes) can apply a shader effect while it lasts; the matcher rejects an actor with a shader (native art shows) and the token returns when it ends; token drawing follows actor visibility as for every other token.',
              'hits_in_batch': [],
              'no_hit': [i['native_name'] for i in identities]},
          'summons_and_same_body_copies': {
              'method': "grep of every actor definition, static map, quest script, vault, encounter, event, artifact and talent under game/modules/tome (data and class) for the seventeen names and PNGs; talents that build summons/copies (summon-*, dreadmaster, master-of-flesh, master-of-bones, rot, thought-forms, simulacra/mirror images, Grand Arrival, golemancy, cloneFull users, shadows) checked for copies of these bodies.",
              'findings': findings},
          'name_collisions_checked': [
              {'name': a['name'], 'other_definitions': ['none'],
               'outcome': ('single actor definition bound to define_as ' + a['define_as'] + ('; unique=true in the catalog entry' if a['unique'] else '') if a['define_as'] else ('unique actor definition without define_as; unique=true in the catalog entry' if a['unique'] else 'single actor definition without define_as; the catalog entry has no define_as and matches by exact name, type and subtype'))} for a in {x['id']: x for x in A}.values()],
          'kept_native': [
              {'name': 'Vilespawn (Corpathus artifact minion)', 'reason': "world-artifacts.lua:3443 builds a separately named minion on the oozing horror PNG with its own hard-coded fields; not a summon of an oozing horror; mapping it needs a name alias the catalog does not have"}],
          'neighbours_kept_native': [
              {'name': 'Training Dummy', 'reason': 'listed at 12.0 by the scoring script but kept native since batch T'},
              {'name': 'Vilespawn', 'reason': 'see kept_native'}]}
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
                 'gate_reason': f"Exact source identity re-verified directly against game/modules/tome source (name={a['name']}, define_as={a['define_as']}, type={a['type']}/subtype={a['subtype']}, unique={a['unique']}, native_tall={a['native_tall']}); details and hashes in evidence/monster-batch-ac-20260930/source-contracts.json. {a['structure']}. Exact catalog entry only, never a whole-subtype mapping.",
                 'render_evidence': [{'path': render, 'sha256': evsha}]}
        if a.get('refinement'):
            entry['refinement'] = a['refinement']
        packs.setdefault(a['pack'], []).append(entry)
    for n, assets in packs.items():
        p = ADDON / f'art/production/batches/monster-batch-ac-{n}.json'
        if p.exists():
            print('exists, skipped', p.name)
            continue
        p.write_text(json.dumps({'schema': 1, 'batch_id': f'monster-batch-ac-{n}', 'assets': assets}, indent=2, ensure_ascii=False) + '\n')
        print('wrote', p.name)


if __name__ == '__main__':
    build()
