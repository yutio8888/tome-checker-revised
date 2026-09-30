"""Generate the monster-batch-aa task packs and the pinned source-contract
evidence (survey-2 unscheduled list after batch Z: ultimate faeros, orc
berserker, dredge captain, polar bear, anaconda, ultimate teluvorta, necrotic
abomination, bone horror, sanguine horror, barrow wight, ogre warmaster,
dreadmaster; see SELECTION.md). Pure bookkeeping: hashes native sources/sprites,
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
ART_REL = 'game/addons/tome-checker-revised/art/monster-batch-aa/'
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
FAER = 'general/npcs/faeros.lua'
ORCG = 'general/npcs/orc-grushnak.lua'
HTMP = 'general/npcs/horror_temporal.lua'
BEAR = 'general/npcs/bear.lua'
SNAK = 'general/npcs/snake.lua'
TELU = 'general/npcs/telugoroth.lua'
HUND = 'general/npcs/horror-undead.lua'
WIGH = 'general/npcs/wight.lua'
OGRE = 'general/npcs/ogre.lua'
GHOS = 'general/npcs/ghost.lua'
RESOLV = 'resolvers.lua'

REF_FAEROS = RC('faeros', ['faeros', 'greater-faeros'], 2,
                'Two shipped faeros tokens (the faeros: a thin orange-red flame figure with legs and arms flung wide in an X; the greater faeros: a bulkier orange flame giant with legs): the ultimate faeros is a LEGLESS fire spirit, a blazing WHITE-HOT and pale-gold core torso with a fierce bright face, a crown of seven tall flame plumes, two long thick flame arms hanging in front and a heavy tapering flame TAIL that spirals once around the base and curls up like a comma, with only the outer fringe orange; not an orange figure with legs and not an X-shaped pose.')
REF_TELUV = RC('teluvorta', ['teluvorta', 'greater-teluvorta', 'ultimate-telugoroth', 'void-horror'], 2,
               'Four shipped temporal tokens (the teluvorta: a spiky violet crystal-urchin ball; the greater teluvorta: a dark-violet storm cloud crowned with six ivory horns; the ultimate telugoroth: a gold eight-point starburst; the void horror: a lens-shaped indigo spacetime tear with a silver border): the ultimate teluvorta is a tall collapsing HOURGLASS-SHAPED VORTEX of luminous COBALT-BLUE and bright CYAN nebula sand, two spinning funnels meeting at a blazing white-cyan pinch point, orbited by three broken silver-gold rings and falling glass shards; not violet, not spiky, not horned, not a starburst and not a lens-shaped tear.')
REF_DREDGE = RC('dredges', ['dredge', 'dredgling'], 2,
                'Two shipped dredge tokens (the dredge: a bulky bald pink brute with heavy arms; the dredgling: a small crouching pink creature): the dredge captain is a THIN, gaunt, spindly horror standing hunched with an oversized head, stringy arms reaching almost to the floor and a long curved bright steel dagger in its raised hand, its body split down the middle into a wrinkled aged grey-lavender half and a smooth young pink half; not bulky, not all pink and not crouching on all fours.')
REF_GHOSTS = RC('ghosts', ['dread', 'banshee', 'grave-wight'], 3,
                'Three shipped ghostly tokens (the dread: a small slate-violet spiky hairy ball with one red eye; the banshee: a cyan-white wailing woman spirit; the grave wight: a translucent cyan ghost): the dreadmaster is a TOWERING hooded WRAITH, a bell-shaped ragged cloak of pale slate-blue and periwinkle shroud with a tall pointed hood, a glowing RED screaming face inside the hood, long thin pale clawed arms and curling pale-blue mist; not a spiky ball, not a cyan woman and not a plain ghost.')
REF_ORCS = RC('orcs', ['orc-fighter', 'orc-soldier', 'orc-warrior', 'orc-assassin'], 2,
              'Four shipped orc tokens (the orc fighter: grey plate with a shield and a mace; the orc soldier: dark spiked armour with an axe held low; the orc warrior: a leather-clad green orc with a curved blade; the orc assassin: a dark-cloaked knifeman): the orc berserker is a huge green orc in MASSIVE polished pale-steel plate with big rounded spiked pauldrons and a HORNED helm, rust-red and bone-white war-paint, a tattered crimson war-cloth and a huge two-handed double-bladed BATTLEAXE raised HIGH OVERHEAD in both hands, roaring, with no shield; not a shield-bearer, not an axe held low and not leather.')
REF_OGRES = RC('ogres', ['ogre-guard', 'ogre-mauler', 'ogre-pounder', 'elven-elite-warrior'], 2,
               'Four shipped tokens (three brawny bare-chested ogres in blue, red and blue-skinned brute builds with mauls, and the bronze-plated elven elite warrior): the ogre warmaster is a tall imposing ARMOURED female ogre in gleaming SILVER-WHITE full plate with gold-trimmed edges, a tall crested visored helm with a crimson plume, gold collar, greaves and gauntlets and two long straight swords held close, one point-up beside the head and one low; not a bare-chested brute, not blue or red skinned and not bronze.')
REF_WIGHTS = RC('wights', ['forest-wight', 'grave-wight', 'armoured-skeleton-warrior', 'dread'], 2,
                'Four shipped undead tokens (the forest wight: a green hooded goblin-like wight with a round shield; the grave wight: a translucent cyan ghost; the armoured skeleton warrior; the dread): the barrow wight is a GAUNT tall undead in ancient grave-armour, an ash-pale skull-like face with sunken glowing ICE-BLUE eyes and a tarnished bronze circlet, a verdigris-green and bronze breastplate and pauldrons, a tattered pale-grey burial shroud, bony ash-white arms reaching forward with cold blue witch-light and pale blue mist round the legs; not green-hooded, not a see-through ghost and not a skeleton.')
REF_BEARS = RC('bears', ['brown-bear', 'black-bear', 'cave-bear', 'war-bear', 'grizzly-bear'], 3,
               'Five shipped bear tokens (brown, black, the grey-white hulking cave bear, the orange war bear and the tan grizzly, the last two reared up): the polar bear is a huge broad-shouldered PURE WHITE bear in a low STALKING pose with its long neck stretched forward and head lowered, a long narrow snout, small round ears, a black nose, shaggy white fur with soft ICE-BLUE shadows and faint frost crystals along the back; not brown, not black, not grey, not reared and not a humped hulking cave bear.')
REF_SNAKES = RC('snakes', ['brown-snake', 'king-cobra', 'black-mamba', 'rattlesnake'], 2,
                'Four shipped snake tokens (the tan-brown patterned flat coil, the olive-green hooded king cobra, the steel-blue black mamba and the tan diamond-back rattlesnake): the anaconda is a gigantic very THICK snake wound into a tight VERTICAL constricting spiral of three heavy stacked coils like a rope pile, the front rising in a short S to a broad flat wedge-shaped head, bright YELLOW-GREEN and olive scales with two rows of big dark green-brown OVAL RING blotches and a cream-yellow belly; not tan-brown, not hooded, not blue and not a flat coil.')
REF_UNDEAD_H = RC('undead-horrors', ['necrotic-mass', 'fleshy-experiment', 'boney-experiment', 'sanguine-experiment'], 2,
                  'Four shipped undead-horror tokens (the necrotic mass: a round pink-brown lump with small skulls; the fleshy experiment: a pink mass with tentacles; the boney experiment: a flat heap of bones; the sanguine experiment: a low glossy red blob dome): the necrotic abomination is a lopsided hunched drag-forward hulk of sickly OLIVE-GREEN rotting flesh torn open to bone-white ribs with a crest of jutting bone spikes and a gaping fanged chest split; the bone horror is a huge ivory RIBCAGE arch standing on six long spidery legs of fused finger bones with skeletal hands reaching up and a warm amber heartbeat glow inside; the sanguine horror is an upright rearing wave-column of crimson blood with a glowing coral-pink heart inside and dripping tendril arms; none may be a lump, a flat heap or a low dome.')

DEFB = ' NPC.lua:33 default-name image on the leaf (no image=)'


def tall_explicit(png):
    return ' resolvers.nice_tile{image="invis.png", add_mos={{image="npc/%s.png", display_h=2, display_y=-1}}} names the tall PNG explicitly (keys image/display_h/display_y only; with nicer_tiles off nice_tile is a no-op and the single image is used); no moddable_tile, shader, anim or add_displays; native sprite 64x128; non-unique with no define_as, so the catalog entry carries native_tall=true' % png


# ---- pack 1: ultimate faeros, ultimate teluvorta, dredge captain, dreadmaster ----
asset(1, 'ultimate-faeros', 'ultimate faeros',
      "charred-scar pool (general/npcs/faeros.lua:86, elemental/fire, non-unique, no define_as, rank 3, base BASE_NPC_FAEROS, nice_tile tall body); the renegade-pyromancers vault builds the same leaf by name (its random-boss variant stays native as a non-unique tall boss); the only definition of this name",
      [src(FAER, 'name = "ultimate faeros"'), src(FAER, 'resolvers.nice_tile', after='name = "ultimate faeros"'), src(FAER, 'T_FIERY_HANDS', after='name = "ultimate faeros"'), src(FAER, 'resolvers.sustains_at_birth()', after='name = "ultimate faeros"'), src(FAER, 'define_as = "BASE_NPC_FAEROS"')],
      src(FAER, 'define_as = "BASE_NPC_FAEROS"'), None, 'elemental', 'fire', False, True,
      'base BASE_NPC_FAEROS (elemental/fire, no image=, no shader, no sustains_at_birth in the base);' + tall_explicit('elemental_fire_ultimate_faeros') + '; the leaf calls resolvers.sustains_at_birth() and Fiery Hands is its only sustain (hand particles and temporary values only); on_melee_hit fire damage only; no equip, no auto_classes',
      'elemental_fire_ultimate_faeros.png',
      [STY, IDN('elemental_fire_ultimate_faeros.png', 'Native shape (64x128, tall): a tall orange flame spirit with a glowing yellow face, arms hanging and a tapering flame tail instead of legs. Keep the legless tall flame spirit with the glowing face and the tapering flame tail, drawn as ONE compact figure filling the disc, no tall canvas, as a white-hot colossus clearly different from the shipped faeros and greater faeros.'), REF_FAEROS],
      "An ultimate faeros seen from a steep overhead three-quarter angle: a colossal LEGLESS FIRE SPIRIT rising from the disc as one compact upright column: a blazing WHITE-HOT and pale-gold core torso with a fierce face with two bright white-gold eyes and a snarling mouth, a tall crown of seven curling flame plumes, two long thick arms of living flame hanging in front of the body ending in crackling molten-gold hands, and instead of legs a heavy tapering TAIL of flame that spirals once around the base and curls up in front like a comma; the outer flame fringe and plume tips are bright ORANGE and vivid red-orange, the flames have crisp readable tongue shapes with lighter inner edges, a ring of small pale-gold embers around the base, a thin bright pale-yellow rim light. Luminous, legless, crowned and complete.",
      "Fire elementals: the ULTIMATE FAEROS is the LEGLESS WHITE-HOT flame colossus with a spiral tail and a seven-plume crown (silhouette: a single upright column with a comma-curled tail and no legs; hue: white-gold core with an orange fringe; value: very bright with red-orange tips). The shipped faeros is a thin orange-red flame figure with legs and arms flung wide in an X, and the greater faeros a bulkier orange flame giant with legs: this must not have legs, must not be an X pose and must not be plain orange.",
      "White-hot and pale-gold core, bright orange and red-orange flame fringe, pale-gold embers, a thin bright pale-yellow rim; no smoke, no black char, no lava, no dark red body; the fire glow stays on the body and must not tint, light or warm the disc, which stays neutral charcoal at reference lightness." + DISC,
      "READY tall (ultimate faeros, native_tall)", comp=COMP + FIT + COMPACT + BRIGHT + CATS)

asset(1, 'ultimate-teluvorta', 'ultimate teluvorta',
      "temporal-rift pool (general/npcs/telugoroth.lua:207, elemental/temporal, non-unique, no define_as, rank 3, base BASE_NPC_TELUGOROTH, nice_tile tall body); the only definition of this name",
      [src(TELU, 'name = "ultimate teluvorta"'), src(TELU, 'resolvers.nice_tile', after='name = "ultimate teluvorta"'), src(TELU, 'T_REALITY_SMEARING', after='name = "ultimate teluvorta"'), src(TELU, 'doTeluvortaSwap()', after='name = "ultimate teluvorta"'), src(TELU, 'resolvers.sustains_at_birth()', after='name = "ultimate teluvorta"'), src(TELU, 'define_as = "BASE_NPC_TELUGOROTH"')],
      src(TELU, 'define_as = "BASE_NPC_TELUGOROTH"'), None, 'elemental', 'temporal', False, True,
      'base BASE_NPC_TELUGOROTH (elemental/temporal, no image=, no shader);' + tall_explicit('elemental_temporal_ultimate_teluvorta') + '; the leaf calls resolvers.sustains_at_birth() and Reality Smearing is its only sustain (shield particle and temporary values only); on_act may call doTeluvortaSwap (a position swap, no display write); no equip, no auto_classes',
      'elemental_temporal_ultimate_teluvorta.png',
      [STY, IDN('elemental_temporal_ultimate_teluvorta.png', 'Native shape (64x128, tall): a tall irregular cloud of blue and violet nebula with pale star flecks and glowing cracks. Keep the tall churning cosmic blue nebula with star flecks and cracks, drawn as ONE compact figure filling the disc, no tall canvas, as a collapsing hourglass-shaped vortex clearly different from the shipped teluvorta tiers.'), REF_TELUV],
      "An ultimate teluvorta seen from a steep overhead three-quarter angle: a colossal collapsing HOURGLASS-SHAPED VORTEX of time and space standing upright on the disc as one compact figure: two spinning funnels of luminous COBALT-BLUE and bright CYAN nebula sand, one above and one below, meeting at a blazing white-cyan pinch point in the middle, silver star-flecks scattered through the cloud and glowing pale-blue cracks running across it, three broken bright silver-gold RINGS (thin arcs with small tick marks, no numerals or letters) orbiting the vortex at different tilts, a few falling glass-like SILVER shards, a thin bright pale-cyan rim light. Collapsing, blue, ringed and complete.",
      "Temporal elementals: the ULTIMATE TELUVORTA is the COBALT-AND-CYAN HOURGLASS VORTEX with a white-cyan pinch point and orbiting broken rings (silhouette: an upright double funnel pinched in the middle with arcs around it; hue: cobalt blue, cyan and silver; value: mid-light with a bright centre). The shipped teluvorta is a spiky violet crystal ball, the greater teluvorta a dark-violet storm cloud with six ivory horns, the ultimate telugoroth a gold starburst, and the void horror a lens-shaped indigo tear: this must not be violet, spiky, horned, star-shaped or a lens.",
      "Mid-light cobalt blue and bright cyan nebula with silver star-flecks, a white-cyan pinch point, silver-gold rings and a bright rim; nothing darker than mid cobalt except thin cracks; NO black or near-black cloud, no violet body; the glow stays in the vortex and must not tint or light the disc, which stays neutral charcoal at reference lightness." + DISC,
      "READY tall (ultimate teluvorta, native_tall)", comp=COMP + FIT + COMPACT + BRIGHT + DARKFIX + CATS)

asset(1, 'dredge-captain', 'dredge captain',
      "temporal-rift pool (general/npcs/horror_temporal.lua:98, horror/temporal, non-unique, no define_as, rank 3, base BASE_NPC_HORROR_TEMPORAL, default-name image); the only definition of this name",
      [src(HTMP, 'name = "dredge captain"'), src(HTMP, 'make_escort', after='name = "dredge captain"'), src(HTMP, 'T_DREDGE_FRENZY', after='name = "dredge captain"'), src(HTMP, 'resolvers.inscriptions(1, {"shielding rune"})', after='name = "dredge captain"'), src(HTMP, 'define_as = "BASE_NPC_HORROR_TEMPORAL"')],
      src(HTMP, 'define_as = "BASE_NPC_HORROR_TEMPORAL"'), None, 'horror', 'temporal', False, False,
      'base BASE_NPC_HORROR_TEMPORAL (horror/temporal, no image=, no shader);' + DEF + '; make_escort builds three dredge leaves (each wears its own token); resolvers.inscriptions picks a shielding rune and an infusion (random inscription, no display write, an invisibility infusion applies a shader only while active and the matcher then rejects it); Dredge Frenzy and Speed Sap are activated npc talents; the leaf calls resolvers.sustains_at_birth() but none of its talents is sustained; no equip, no auto_classes',
      'horror_temporal_dredge_captain.png',
      [STY, IDN('horror_temporal_dredge_captain.png', 'Native shape (64x64): a thin pink-skinned creature with long spindly arms holding a knife, half of the body wrinkled and old. Keep the gaunt spindly creature with the knife and the split old/young body, drawn as ONE compact hunched figure filling the disc, clearly thinner and more upright than the shipped dredge and dredgling.'), REF_DREDGE],
      "A dredge captain seen from a steep overhead three-quarter angle: a THIN, gaunt, spindly horror standing hunched forward on the disc with an oversized bald head, long stringy arms reaching almost to the floor and clawed hands, its raised right hand clutching a long curved bright STEEL DAGGER; the body is split cleanly down the middle: the left half wrinkled, aged, sallow GREY-LAVENDER skin with sagging folds and a milky pale eye, the right half smooth young pale PINK skin with a bright eye; a ragged pale cloth sash across the chest, bony knees and long pale toes; light rim along the whole outline. Gaunt, two-faced, armed and complete.",
      "Temporal horrors: the DREDGE CAPTAIN is the THIN two-toned dagger-wielding hunched horror (silhouette: a tall spindly hunched figure with a raised arm and a long blade; hue: half grey-lavender wrinkled, half pale pink; value: light). The shipped dredge is a bulky bald pink brute and the dredgling a small crouching pink creature, both unarmed: this must not be bulky, not all pink and not crouching on all fours.",
      "Light grey-lavender and pale pink skin, bright steel blade, pale cream sash, a thin bright rim light; nothing darker than mid grey-lavender except eye slits and skin folds; the disc stays neutral charcoal at reference lightness." + DISC,
      "READY single, no define_as (dredge captain)", comp=COMP + FIT + COMPACT + BRIGHT)

asset(1, 'dreadmaster', 'dreadmaster',
      "rak-shor-pride, telmur and demon-plane pools plus the greater-crypt and orc-necromancer vaults (general/npcs/ghost.lua:81, undead/ghost, non-unique, no define_as, rank 3, base BASE_NPC_GHOST, explicit image=npc/dreadmaster.png); the Necromancer's Dread talent summons a minion with the same name, type, subtype and image (talents/spells/dreadmaster.lua), which wears the same token",
      [src(GHOS, 'name = "dreadmaster"'), src(GHOS, 'image="npc/dreadmaster.png"', after='name = "dreadmaster"'), src(GHOS, 'summon = {{type="undead", subtype="ghost", name="dread"', after='name = "dreadmaster"'), src(GHOS, 'define_as = "BASE_NPC_GHOST"'), src('talents/spells/dreadmaster.lua', 'image="npc/dreadmaster.png"', after='dreadmaster = {')],
      src(GHOS, 'define_as = "BASE_NPC_GHOST"'), None, 'undead', 'ghost', False, False,
      'base BASE_NPC_GHOST (undead/ghost, no image=, no shader);' + EXPL + '; the base and the leaf call resolvers.sustains_at_birth() and Blur Sight is the only sustained talent (particle and temporary values only); Summon calls the dread leaf (own token); the Necromancer Dread talent builds a minion with identical name/type/subtype/image (wears the same token); no equip, no auto_classes',
      'dreadmaster.png',
      [STY, IDN('dreadmaster.png', 'Native shape (64x64): a near-black hooded blob wraith with a glowing red screaming face and a blue glow around its edges. Keep the hooded shroud with the glowing red screaming face, but render the cloak in mid-light slate-blue and periwinkle with a bright icy rim light and bright red face features, drawn as ONE compact figure filling the disc, clearly a larger cloaked wraith than the shipped dread.'), REF_GHOSTS],
      "A dreadmaster seen from a steep overhead three-quarter angle: a towering hooded WRAITH standing on the disc, a big bell-shaped ragged cloak of pale SLATE-BLUE and PERIWINKLE shroud with broad bright highlight planes on every upper-left fold, a tall pointed hood whose interior is a mid-indigo hollow, inside it a glowing RED screaming face: two bright red eyes and a long open mouth glowing crimson-orange, two long thin pale-grey clawed arms emerging from the wide sleeves and reaching forward, the ragged torn hem sweeping around the base in pointed tatters with pale blue spectral mist curling off the edges, a thin bright ICY BLUE-WHITE rim light along the whole outline. Hooded, screaming, ragged and complete.",
      "Ghosts: the DREADMASTER is the TOWERING HOODED WRAITH in a pale slate-blue bell-shaped shroud with a glowing red screaming face (silhouette: a bell-shaped cloak with a tall pointed hood and clawed arms out of the sleeves; hue: pale slate-blue and periwinkle with a red face; value: mid-light). The shipped dread is a small slate-violet spiky hairy ball with one red eye, the banshee a cyan woman spirit and the grave wight a translucent cyan ghost: this must not be a spiky ball, a woman or a plain see-through ghost.",
      "Pale slate-blue and periwinkle shroud with bright icy highlights, mid-indigo hood hollow, bright red and crimson-orange face, pale-grey claws, a bright icy rim; nothing darker than mid indigo except thin seams; NO black cloak; the red glow stays in the face and must not tint the disc, which stays neutral charcoal at reference lightness." + DISC,
      "READY single, no define_as (dreadmaster)", comp=COMP + FIT + COMPACT + BRIGHT + DARKFIX)

# ---- pack 2: orc berserker, ogre warmaster, barrow wight, polar bear ----
asset(2, 'orc-berserker', 'orc berserker',
      "vor-armoury and rak-shor-pride pools (general/npcs/orc-grushnak.lua:111, humanoid/orc, non-unique, no define_as, rank 2, base BASE_NPC_ORC_GRUSHNAK, default-name image); the elite berserker is a different leaf (define_as ORC_ELITE_BERSERKER) and stays native; the only definition of this name",
      [src(ORCG, 'name = "orc berserker"'), src(ORCG, 'T_BERSERKER', after='name = "orc berserker"'), src(ORCG, 'resolvers.equip', after='name = "orc berserker"'), src(ORCG, 'resolvers.racial()'), src(ORCG, 'resolvers.sustains_at_birth()'), src(ORCG, 'define_as = "BASE_NPC_ORC_GRUSHNAK"')],
      src(ORCG, 'define_as = "BASE_NPC_ORC_GRUSHNAK"'), None, 'humanoid', 'orc', False, False,
      'base BASE_NPC_ORC_GRUSHNAK (humanoid/orc, no image=, no shader);' + DEF + '; resolvers.racial() only adds orc levelup talents (passives, no display write); the base calls resolvers.sustains_at_birth() and Berserker is the leaf sustain (temporary values only); resolvers.equip a battleaxe and massive armour (equipment only, no moddable_tile); resolvers.inscriptions picks random runes/infusions (no display write); no auto_classes',
      'humanoid_orc_orc_berserker.png',
      [STY, IDN('humanoid_orc_orc_berserker.png', 'Native shape (64x64): a huge orc in near-black massive spiked armour with a horned helm and a big axe. Keep the massive-armoured orc with a horned helm and the huge axe, but render the plate in bright polished steel with broad pale highlights, the axe raised high overhead in both hands, drawn as ONE compact figure filling the disc.'), REF_ORCS],
      "An orc berserker seen from a steep overhead three-quarter angle: a huge hulking GREEN-skinned orc in MASSIVE plate armour of polished pale STEEL with brass rivets, big rounded spiked pauldrons and a spiked gorget, a HORNED steel helm, a snarling roaring tusked face striped with rust-red and bone-white war-paint, a tattered CRIMSON war-cloth hanging at the hip, heavy steel gauntlets gripping a huge two-handed double-bladed BATTLEAXE raised HIGH OVERHEAD in both hands with bright steel blades; no shield and no second weapon; broad pale highlight planes on every upper-left plate and a thin bright rim light. Roaring, horned, steel-plated and complete.",
      "Orcs: the ORC BERSERKER is the ROARING GREEN ORC IN MASSIVE POLISHED STEEL PLATE with a horned helm and a huge double-bladed axe raised overhead in both hands (silhouette: a wide armoured figure with both arms up and a vertical axe above the head, horns; hue: steel with green skin, crimson cloth and rust-red paint; value: bright steel). The shipped orc fighter is grey plate with a shield and mace, the orc soldier dark spiked armour with an axe held low, the orc warrior leather with a curved blade and the orc assassin a dark-cloaked knifeman: this must not carry a shield, hold the axe low or wear leather or dark cloth.",
      "Bright polished steel plate with brass rivets, green skin, rust-red and bone-white paint, crimson cloth, a thin bright rim light; nothing darker than mid steel-grey except eye slits and armour seams; NO black armour; the disc stays neutral charcoal at reference lightness." + DISC,
      "READY single, no define_as (orc berserker)", comp=COMP + FIT + COMPACT + BRIGHT + DARKFIX)

asset(2, 'ogre-warmaster', 'ogre warmaster',
      "crypt-kryl-feijan pool (general/npcs/ogre.lua:62, giant/ogre, non-unique, no define_as, rank 3, base BASE_NPC_OGRE, resolvers.nice_tile{tall=1}); the only definition of this name",
      [src(OGRE, 'name = "ogre warmaster"'), src(OGRE, 'resolvers.nice_tile{tall=1}', after='name = "ogre warmaster"'), src(OGRE, 'T_SHATTERING_BLOW', after='name = "ogre warmaster"'), src(OGRE, 'resolvers.racial()'), src(OGRE, 'resolvers.sustains_at_birth()'), src(OGRE, 'define_as = "BASE_NPC_OGRE"'), src('resolvers.lua', 'function resolvers.calc.nice_tile', root='game/modules/tome/')],
      src(OGRE, 'define_as = "BASE_NPC_OGRE"'), None, 'giant', 'ogre', False, True,
      'base BASE_NPC_OGRE (giant/ogre, no image=); NPC.lua:33 default-name image via resolvers.nice_tile{tall=1} (the same live-confirmed shorthand as the ogre guard, mauler, rune-spinner and pounder: invis.png + add_mos{image=e.image, display_h=2, display_y=-1}); native sprite 64x128; resolvers.racial() only adds ogre levelup talents (passives/one activated buff, no display write); the base calls resolvers.sustains_at_birth() and no sustained talent is learned (none of the leaf talents is sustained); resolvers.equip a mace and a shield (equipment only, no moddable_tile); resolvers.inscriptions picks random runes/infusions (no display write); no auto_classes; female = 1 only affects name gender',
      'giant_ogre_ogre_warmaster.png',
      [STY, IDN('giant_ogre_ogre_warmaster.png', 'Native shape (64x128, tall): a tall figure in silver-white plate armour with a crested helm, gold greaves and collar and two long blades held upright. Keep the tall silver-plated crested warrior with gold trim and long blades, drawn as ONE compact figure filling the disc, no tall canvas, clearly an armoured warmaster and not a bare-chested ogre brute.'), REF_OGRES],
      "An ogre warmaster seen from a steep overhead three-quarter angle: a tall imposing ARMOURED female ogre standing upright and broad-shouldered on the disc in gleaming SILVER-WHITE full plate with gold-trimmed edges and bright pale highlight planes, a tall crested visored helm with a swept CRIMSON plume, a GOLD collar, gold greaves and gold gauntlets, a grey-tan ogre jaw and tusk-tips visible under the visor, a woven crimson sash across the waist, and two long straight steel swords held close to the body, one point-up beside the head and one low pointing down at the side (both blades tucked well inside the disc), a thin bright rim light. Armoured, crested, gold-trimmed and complete.",
      "Ogres: the OGRE WARMASTER is the TALL SILVER-PLATED CRESTED ARMOURED WARRIOR with a crimson plume, gold trim and two long swords (silhouette: an upright plated figure with a tall crest and swords beside the body; hue: silver-white plate with gold and crimson; value: bright). The shipped ogre guard, mauler and pounder are brawny bare-chested brutes with mauls in blue and red skin, and the elven elite warrior is bronze plate: this must not be bare-chested, not blue or red skinned and not bronze.",
      "Bright silver-white plate with gold trim, crimson plume and sash, grey-tan skin, steel blades and a thin bright rim; nothing darker than mid silver-grey except visor slit and plate seams; the disc stays neutral charcoal at reference lightness." + DISC,
      "READY tall (ogre warmaster, native_tall via nice_tile{tall=1})", comp=COMP + FIT + COMPACT + BRIGHT + CATS)

asset(2, 'barrow-wight', 'barrow wight',
      "dreadfell and ardhungol pools (general/npcs/wight.lua:92, undead/wight, non-unique, no define_as, rank 2, base BASE_NPC_WIGHT, explicit image=npc/barrow_wight.png and a nice_tile tall body); the only definition of this name",
      [src(WIGH, 'name = "barrow wight"'), src(WIGH, 'image="npc/barrow_wight.png"', after='name = "barrow wight"'), src(WIGH, 'resolvers.nice_tile', after='name = "barrow wight"'), src(WIGH, 'T_CHAIN_LIGHTNING', after='name = "barrow wight"'), src(WIGH, 'resolvers.sustains_at_birth()'), src(WIGH, 'define_as = "BASE_NPC_WIGHT"')],
      src(WIGH, 'define_as = "BASE_NPC_WIGHT"'), None, 'undead', 'wight', False, True,
      'base BASE_NPC_WIGHT (undead/wight, no image=, no shader);' + ' explicit image=npc/barrow_wight.png plus' + tall_explicit('barrow_wight') + ' (the master vampire has the same image= plus nice_tile form); the base calls resolvers.sustains_at_birth() and no sustained talent is learned (Flameshock, Chain Lightning, Glacial Vapour and Mind Disruption are activated); resolvers.drops only names loot; no equip, no auto_classes',
      'barrow_wight.png',
      [STY, IDN('barrow_wight.png', 'Native shape (64x128, tall): a gaunt armoured undead with a pale skull-like face, dark armour and shreds of cloth, wreathed in cold blue mist. Keep the gaunt armoured undead with the pale face and cold blue mist, but render the armour in bright verdigris and bronze and the shroud pale grey, drawn as ONE compact figure filling the disc, no tall canvas.'), REF_WIGHTS],
      "A barrow wight seen from a steep overhead three-quarter angle: a GAUNT tall undead standing hunched forward on the disc in ancient grave-armour: an ash-pale skull-like face with sunken glowing ICE-BLUE eyes and a tarnished bronze CIRCLET, a breastplate and rounded pauldrons of bright VERDIGRIS-green and tarnished bronze with broad pale highlight planes, a tattered pale-grey burial SHROUD hanging behind as a cloak and in front as a ragged loincloth, bony ash-white arms with long fingers reaching forward with a small cold blue witch-light between the hands, a pale cold-blue MIST swirling around the lower legs and feet, a thin bright pale-blue rim light. Gaunt, crowned, armoured and complete.",
      "Wights: the BARROW WIGHT is the GAUNT ARMOURED GRAVE-WIGHT with a bronze circlet, verdigris-and-bronze armour, a pale shroud and ice-blue eyes (silhouette: a hunched upright armoured figure with forward-reaching arms and a cloak; hue: verdigris green, bronze, ash white and ice blue; value: mid-light). The shipped forest wight is a green hooded goblin-like wight with a round shield, the grave wight a translucent cyan ghost and the skeleton warriors bare bone: this must not be hooded, shield-bearing, see-through or a skeleton.",
      "Ash-pale skin, bright verdigris and tarnished bronze armour, pale grey shroud, ice-blue eyes and mist, a thin bright pale-blue rim; nothing darker than mid verdigris except eye sockets and seams; NO black armour or cloak; the mist and witch-light stay on the figure and must not tint or light the disc, which stays neutral charcoal at reference lightness." + DISC,
      "READY tall (barrow wight, native_tall)", comp=COMP + FIT + COMPACT + BRIGHT + DARKFIX + CATS)

asset(2, 'polar-bear', 'polar bear',
      "noxious-caldera and old-forest pools (general/npcs/bear.lua:106, animal/bear, non-unique, no define_as, rank 2, base BASE_NPC_BEAR, explicit image=npc/polar_bear.png); the only definition of this name",
      [src(BEAR, 'name = "polar bear"'), src(BEAR, 'image = "npc/polar_bear.png"', after='name = "polar bear"'), src(BEAR, 'T_KNOCKBACK', after='name = "polar bear"'), src(BEAR, 'define_as = "BASE_NPC_BEAR"')],
      src(BEAR, 'define_as = "BASE_NPC_BEAR"'), None, 'animal', 'bear', False, False,
      'base BASE_NPC_BEAR (animal/bear, no image=, no shader, no sustains_at_birth);' + EXPL + '; the PNG polar_bear.png is used by this leaf only; Stamina Pool is passive and Stun, Knockback and Disarm are activated npc talents; no equip, no sustains_at_birth, no auto_classes',
      'polar_bear.png',
      [STY, IDN('polar_bear.png', 'Native shape (64x64): a cream-white bear walking sideways with a broad head. Keep the pure white bear, but draw it as a low stalking predator, drawn as ONE compact figure filling the disc, clearly a sleeker white ice bear and not a grey hulking cave bear.'), REF_BEARS],
      "A polar bear seen from a steep overhead three-quarter angle: a huge broad-shouldered bear in a low STALKING pose on the disc, its long neck stretched forward and the head lowered and turned to the lower right, a long narrow snout, small round ears, a black nose and dark eyes, thick shaggy PURE WHITE and cream fur with soft pale ICE-BLUE shadows and bright white highlight planes on every upper-left surface, big splayed furry paws with dark claws, faint frost crystals glittering along the back, a thin bright rim light. Sleek, white, stalking and complete.",
      "Bears: the POLAR BEAR is the LOW STALKING PURE-WHITE BEAR with a long stretched neck, a narrow snout and ice-blue shadows (silhouette: a long low body with a stretched neck and lowered head; hue: white and cream with ice blue; value: very light). The shipped bears are brown, black, the grey-white hulking humped cave bear and the two reared war and grizzly bears: this must not be brown, black, grey, humped or reared.",
      "Pure white and cream fur with soft ice-blue shadows, black nose and claws, glittering frost, a thin bright rim; the fur is the brightest thing but the disc stays neutral charcoal at reference lightness under it, never lightened." + DISC,
      "READY single, no define_as (polar bear)", comp=COMP + FIT + COMPACT + BRIGHT)

# ---- pack 3: anaconda, necrotic abomination, bone horror, sanguine horror ----
asset(3, 'anaconda', 'anaconda',
      "noxious-caldera and unremarkable-cave pools (general/npcs/snake.lua:115, animal/snake, non-unique, no define_as, rank 3, base BASE_NPC_SNAKE, explicit image=npc/yellow-green-snake.png); the only definition of this name",
      [src(SNAK, 'name = "anaconda"'), src(SNAK, 'image="npc/yellow-green-snake.png"', after='name = "anaconda"'), src(SNAK, 'T_CONSTRICT', after='name = "anaconda"'), src(SNAK, 'define_as = "BASE_NPC_SNAKE"')],
      src(SNAK, 'define_as = "BASE_NPC_SNAKE"'), None, 'animal', 'snake', False, False,
      'base BASE_NPC_SNAKE (animal/snake, no image=, no shader, no sustains_at_birth);' + EXPL + '; the PNG yellow-green-snake.png is used by this leaf only; Constrict is an activated npc talent; no equip, no sustains_at_birth, no auto_classes',
      'yellow-green-snake.png',
      [STY, IDN('yellow-green-snake.png', 'Native shape (64x64): a gigantic golden-yellow snake with dark scale patterns wound into a tall coil. Keep the huge thick yellow-green snake in a heavy coil, drawn as ONE compact stacked spiral filling the disc with a raised broad head, clearly different from the shipped flat brown coil and hooded cobra.'), REF_SNAKES],
      "An anaconda seen from a steep overhead three-quarter angle: a gigantic very THICK snake whose body is wound into a tight VERTICAL constricting spiral of three heavy stacked coils like a coiled rope pile on the disc, the front of the body rising from the top coil in a short S-curve to a broad flat WEDGE-SHAPED head turned to the lower left with small dark eyes set on top, the jaw slightly open with a flicking pink forked tongue, bright YELLOW-GREEN and olive scales with TWO ROWS of big dark green-brown OVAL RING blotches along the back, a cream-yellow throat and belly showing between coils, bright pale highlight bands along the upper-left of every coil, a thin bright rim light. Thick, stacked, blotched and complete.",
      "Snakes: the ANACONDA is the GIGANTIC THICK YELLOW-GREEN SNAKE in a tight stacked vertical spiral with ring blotches and a broad flat head (silhouette: a thick rope-pile spiral with a raised wedge head, no hood; hue: bright yellow-green and olive with dark oval rings, cream belly; value: mid-light). The shipped large brown snake is a flat tan-brown coil, the king cobra an olive-green hooded snake, the black mamba a slender steel-blue snake and the rattlesnake a tan diamond-back: this must not be tan, hooded, blue, slender or a flat coil.",
      "Bright yellow-green and olive scales with dark green-brown oval ring blotches, cream-yellow belly, pink tongue, a thin bright rim; nothing darker than dark olive except eye pupils and blotch centres; the disc stays neutral charcoal at reference lightness." + DISC,
      "READY single, no define_as (anaconda)", comp=COMP + FIT + COMPACT + BRIGHT)

asset(3, 'necrotic-abomination', 'necrotic abomination',
      "rak-shor-pride pool (general/npcs/horror-undead.lua:61, undead/horror, non-unique, no define_as, rank 3, base BASE_NPC_HORROR_UNDEAD, nice_tile tall body); the renegade-undead vault and the rak-shor-pride map script build the same leaf by name; the only definition of this name",
      [src(HUND, 'name = "necrotic abomination"'), src(HUND, 'resolvers.nice_tile', after='name = "necrotic abomination"'), src(HUND, 'base_list="mod.class.NPC:/data/general/npcs/ghoul.lua"', after='name = "necrotic abomination"'), src(HUND, 'T_SOUL_ROT', after='name = "necrotic abomination"'), src(HUND, 'resolvers.sustains_at_birth()', after='name = "necrotic abomination"'), src(HUND, 'define_as = "BASE_NPC_HORROR_UNDEAD"')],
      src(HUND, 'define_as = "BASE_NPC_HORROR_UNDEAD"'), None, 'undead', 'horror', False, True,
      'base BASE_NPC_HORROR_UNDEAD (undead/horror, no image=, no shader, no sustains_at_birth in the base);' + tall_explicit('undead_horror_necrotic_abomination') + '; the leaf calls resolvers.sustains_at_birth() but none of its talents is sustained; its Summon (ghoul and skeleton lists) and on_die summon build other exact leaves; no equip, no auto_classes',
      'undead_horror_necrotic_abomination.png',
      [STY, IDN('undead_horror_necrotic_abomination.png', 'Native shape (64x128, tall): a dark hunched heap of putrid flesh with chipped bone and a skull, dragging itself forward. Keep the hunched torn-flesh-and-bone hulk, but render the flesh in sickly pale olive-green with bone-white ribs and spikes, drawn as ONE compact figure filling the disc, no tall canvas, clearly different from the shipped necrotic mass and experiments.'), REF_UNDEAD_H],
      "A necrotic abomination seen from a steep overhead three-quarter angle: a monstrous lopsided hunched hulk of putrid flesh dragging itself forward across the disc, sickly pale OLIVE-GREEN and grey-green rotting flesh with broad pale highlight planes, torn open at the side to show bone-white RIBS, a CREST of jutting broken bone spikes along the back, a gaping crooked jaw-like split across the chest showing yellow bone fangs, one massive drooping arm of stitched flesh trailing a bone claw and one short arm of bare bone, a few pale skulls embedded in the mass, glistening red viscera seams and a few blood drips spurting from tears (drips stay on the body), a thin bright rim light. Hunched, torn, spiked and complete.",
      "Undead horrors: the NECROTIC ABOMINATION is the LOPSIDED DRAG-FORWARD OLIVE-GREEN HULK torn open to ribs with a bone-spike crest and a fanged chest split (silhouette: an asymmetric hunched hulk with a spiked back crest and one huge drooping arm; hue: sickly olive-green with bone white and red seams; value: mid-light). The shipped necrotic mass is a round pink-brown lump with small skulls, the fleshy experiment a pink tentacled mass, the boney experiment a flat heap of bones and the sanguine experiment a low red blob: this must not be a round lump, pink, a flat heap or a red dome.",
      "Sickly pale olive-green flesh, bone-white ribs, spikes and skulls, small red viscera seams, yellow fangs, a thin bright rim; nothing darker than mid olive except mouth hollows and seams; NO black or dark green mass; the disc stays neutral charcoal at reference lightness." + DISC,
      "READY tall (necrotic abomination, native_tall)", comp=COMP + FIT + COMPACT + BRIGHT + DARKFIX + CATS)

asset(3, 'bone-horror', 'bone horror',
      "rak-shor-pride pool (general/npcs/horror-undead.lua:105, undead/horror, non-unique, no define_as, rank 3, base BASE_NPC_HORROR_UNDEAD, nice_tile tall body); the renegade-undead vault builds the same leaf by name (its random-boss variant stays native as a non-unique tall boss); the only definition of this name",
      [src(HUND, 'name = "bone horror"'), src(HUND, 'resolvers.nice_tile', after='name = "bone horror"'), src(HUND, 'T_BONE_SHIELD', after='name = "bone horror"'), src(HUND, 'base_list="mod.class.NPC:/data/general/npcs/skeleton.lua"', after='name = "bone horror"'), src(HUND, 'resolvers.sustains_at_birth()', after='name = "bone horror"'), src(HUND, 'define_as = "BASE_NPC_HORROR_UNDEAD"')],
      src(HUND, 'define_as = "BASE_NPC_HORROR_UNDEAD"'), None, 'undead', 'horror', False, True,
      'base BASE_NPC_HORROR_UNDEAD (undead/horror, no image=, no shader, no sustains_at_birth in the base);' + tall_explicit('undead_horror_bone_horror') + '; the leaf calls resolvers.sustains_at_birth() and Bone Shield is its only sustain (ring particle and temporary values only); its Summon and on_die summon build skeleton leaves (own tokens); no equip, no auto_classes',
      'undead_horror_bone_horror.png',
      [STY, IDN('undead_horror_bone_horror.png', 'Native shape (64x128, tall): a pale ribcage held up on long spidery limbs of fused skeletal hands, with more hands reaching upward. Keep the ribcage arch on spindly finger-bone legs with skeletal hands reaching up, drawn as ONE compact figure filling the disc, no tall canvas, clearly a spidery arch and not a heap.'), REF_UNDEAD_H],
      "A bone horror seen from a steep overhead three-quarter angle: a massive pale ivory RIBCAGE standing on the disc as a huge arch, held up on six long spindly leg-like assemblies of fused FINGER BONES and skeletal forearms that bend out and down like a spider's legs, skeletal HANDS with long fingers reaching up and out from the top of the ribcage and a few smaller hands clutching at the air, a dim warm AMBER-yellow glow of a beating heart inside the ribs, bright bone-white and warm ivory with soft grey-beige shadows and bright highlight planes on every upper-left bone, a thin bright rim light; no skull face and no ground pile. Arched, spidery, many-handed and complete.",
      "Undead horrors: the BONE HORROR is the IVORY RIBCAGE ARCH on six spidery finger-bone legs with skeletal hands reaching up and an amber heartbeat glow (silhouette: a tall arch on splayed thin legs with hands above; hue: bright ivory bone with a warm amber core; value: very light). The shipped boney experiment is a flat heap of bones with skulls, the necrotic mass a pink lump and the skeleton tokens are upright humanoids: this must not be a heap, pink or a humanoid skeleton.",
      "Bright bone-white and warm ivory with soft grey-beige shadows, an amber heart glow contained inside the ribs, a thin bright rim; nothing darker than mid grey-beige except thin gaps between bones; the amber glow stays inside the ribs and must not tint the disc, which stays neutral charcoal at reference lightness." + DISC,
      "READY tall (bone horror, native_tall)", comp=COMP + FIT + COMPACT + BRIGHT + CATS)

asset(3, 'sanguine-horror', 'sanguine horror',
      "rak-shor-pride pool (general/npcs/horror-undead.lua:150, undead/horror, non-unique, no define_as, rank 3, base BASE_NPC_HORROR_UNDEAD, nice_tile tall body); the renegade-undead vault and the rak-shor-pride map script build the same leaf by name (its random-boss variant stays native as a non-unique tall boss); the only definition of this name",
      [src(HUND, 'name = "sanguine horror"'), src(HUND, 'resolvers.nice_tile', after='name = "sanguine horror"'), src(HUND, 'T_BLOOD_FURY', after='name = "sanguine horror"'), src(HUND, 'summon = {', after='name = "sanguine horror"'), src(HUND, 'resolvers.sustains_at_birth()', after='name = "sanguine horror"'), src(HUND, 'define_as = "BASE_NPC_HORROR_UNDEAD"')],
      src(HUND, 'define_as = "BASE_NPC_HORROR_UNDEAD"'), None, 'undead', 'horror', False, True,
      'base BASE_NPC_HORROR_UNDEAD (undead/horror, no image=, no shader, no sustains_at_birth in the base);' + tall_explicit('undead_horror_sanguine_horror') + '; the leaf calls resolvers.sustains_at_birth() and Blood Fury is its only sustain (shield particles and temporary values only); its Summon builds undead/blood leaves (own tokens or native); Bloodspring is a talent that only creates terrain; no equip, no auto_classes',
      'undead_horror_sanguine_horror.png',
      [STY, IDN('undead_horror_sanguine_horror.png', 'Native shape (64x128, tall): a glossy deep-red pulsing mass of blood. Keep the glossy crimson blood body, but draw it as an upright rearing wave-column with a glowing heart inside and dripping tendrils, as ONE compact figure filling the disc, no tall canvas, clearly not the low red dome of the shipped sanguine experiment.'), REF_UNDEAD_H],
      "A sanguine horror seen from a steep overhead three-quarter angle: a towering rippling COLUMN of thick glossy deep CRIMSON blood reared upright on the disc like a wave about to break, a visible translucent beating HEART glowing bright coral-pink in the middle of the column, two thick blood TENDRILS arcing out and down from the sides like arms with dripping tips, concentric ripples travelling up the surface, glossy bright coral-red highlight planes on every upper-left surface and a pale pink rim light along the outline, a few blood droplets falling (all on the body side of the disc), no puddle spreading across the disc. Upright, pulsing, tendril-armed and complete.",
      "Undead horrors: the SANGUINE HORROR is the UPRIGHT REARING CRIMSON WAVE-COLUMN with a glowing coral heart inside and two dripping tendril arms (silhouette: a tall narrowing column with a curling crest and arcing tendrils; hue: crimson with coral and pale-pink highlights; value: mid-light with a bright heart). The shipped sanguine experiment is a low glossy red dome blob, the fleshy experiment a pink tentacled mass and the necrotic mass a pink lump: this must not be a low dome, a lump or pink flesh.",
      "Glossy deep crimson blood with bright coral highlights, a coral-pink glowing heart contained inside the body, a pale pink rim; nothing darker than deep crimson except thin ripple seams; NO dark maroon body; the disc stays neutral charcoal at reference lightness and receives no red spill or puddle." + DISC,
      "READY tall (sanguine horror, native_tall)", comp=COMP + FIT + COMPACT + BRIGHT + CATS)


def retry(id_, pack, **changes):
    base = next(a for a in A if a['id'] == id_)
    A.append(dict(base, pack=pack, **changes))


exec((HERE / 'retries.py').read_text()) if (HERE / 'retries.py').exists() else None


TALL_IDS = tuple(a['id'] for a in A if a['native_tall'])
EXPL_IDS = ('polar-bear', 'anaconda', 'dreadmaster')
PNGF = {a['id']: 'NPC.lua:33 default-name image on the leaf (no image=/nice_tile)' for a in A}
PNGF.update({i: 'explicit image= on the leaf (no nice_tile/add_mos)' for i in EXPL_IDS})
PNGF.update({i: 'NPC.lua:33 default-name image on the leaf plus an explicit nice_tile tall body (image=invis.png, one add_mos entry with display_h=2, display_y=-1 naming the same PNG)' for i in TALL_IDS})
PNGF['barrow-wight'] = 'explicit image=npc/barrow_wight.png on the leaf plus an explicit nice_tile tall body (image=invis.png, one add_mos entry with display_h=2, display_y=-1 naming the same PNG), the same form as the master vampire'
PNGF['ogre-warmaster'] = 'NPC.lua:33 default-name image via resolvers.nice_tile{tall=1} (live-confirmed shorthand, as for the ogre guard, mauler, rune-spinner and pounder)'
EVDIR = 'evidence/monster-batch-aa-20260930/source-contracts.json'
DEFINE = {a['id']: a['define_as'] for a in A}
NAMES_LIST = "ultimate faeros, orc berserker, dredge captain, polar bear, anaconda, ultimate teluvorta, necrotic abomination, bone horror, sanguine horror, barrow wight, ogre warmaster, dreadmaster"


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
        if a['native_tall']:
            ident['tall_body'] = {'image': 'invis.png', 'add_mos': [{'image': native_image, 'display_h': 2, 'display_y': -1}],
                                  'catalog_flag': 'native_tall=true', 'static_pin': ('nice_tile{tall=1} expands to this body (resolvers.lua nice_tile); not unique, so no unique-only tall path applies' if a['id'] == 'ogre-warmaster' else 'nice_tile names the tall PNG explicitly; not unique, so no unique-only tall path applies')}
        if a['base']:
            ident['base_source'] = a['base']
        if len(a['srcs']) > 1:
            ident['extra_sources'] = a['srcs'][1:]
        identities.append(ident)
    findings = [
        "All twelve names have exactly one NPC leaf definition (grep of every actor definition under game/modules/tome, zones included). The zone pools and vaults (renegade-pyromancers for the ultimate faeros, renegade-undead and the rak-shor-pride map script for the necrotic abomination, bone horror and sanguine horror, greater-crypt and orc-necromancer for the dreadmaster) only build those same leaves through name/random_filter lookups, so they are the very same actors; a random boss made from a flat entry goes through the existing captureRandomOrigin path, a random boss made from a non-unique native-tall entry (the renegade-pyromancers ultimate faeros and the renegade-undead bone horror and sanguine horror) stays native because only unique tall bodies qualify.",
        "Summons that copy a monster wear its token: the Necromancer's Dread talent (talents/spells/dreadmaster.lua) builds a minion with the identical name, type, subtype and image=npc/dreadmaster.png, which wears the dreadmaster token; the dreadmaster's own Summon and the dredge captain's escort build dread and dredge leaves (own tokens); the necrotic abomination, bone horror and sanguine horror summons build ghoul, skeleton and undead/blood leaves (own tokens or native).",
        "Orc berserker: the elite berserker is a different leaf (define_as ORC_ELITE_BERSERKER, name 'orc elite berserker') and stays native; the exact name 'orc berserker' is used by this leaf only.",
        "Polar bear and anaconda: the explicit images polar_bear.png and yellow-green-snake.png are used by these leaves only; the grizzly bear, other bears and other snakes have their own PNGs and tokens (or stay native).",
        "Ultimate faeros, ultimate teluvorta, necrotic abomination, bone horror, sanguine horror, barrow wight and ogre warmaster are non-unique native-tall bodies (nice_tile, explicit add_mos or the tall=1 shorthand) with native_tall=true; no unique borrows any of these PNGs.",
        "No summon, clone, event or talent builds an actor with any of the twelve names using a different native PNG (grep of every actor definition, static map, quest script, vault, encounter, event and talent under game/modules/tome for the names and PNGs).",
        "Neighbours that reuse a name or subtype but stay native: 'orc elite berserker', 'entrenched horror' (tied at 1.5 with the dreadmaster and dropped by row order), 'boiling horror', 'swarm hive', 'greater mummy', 'orc summoner', 'shadowblade', 'venom wyrm', 'emperor wight', 'Fyrk, Faeros High Guard' (unique, own token).",
        "Result: no per-identity `variants` entry and no `image_aliases` entry is needed for this batch.",
    ]
    ev = {'schema': 1,
          'task': "monster-batch-aa: static re-verification (no game launch) of the twelve identities that follow batch Z in the survey-2 unscheduled list (" + NAMES_LIST + ") against game/modules/tome source and native sprites. Every field below was read from source: name, type/subtype, define_as (none of the twelve binds one), explicit or NPC.lua:33 default image, unique, PNG on disk, and absence of moddable_tile/shader/anim/add_displays on each leaf and its base. Findings: seven identities are non-unique native-tall bodies (ultimate faeros, ultimate teluvorta, necrotic abomination, bone horror, sanguine horror, barrow wight: nice_tile image=invis.png with one explicit add_mos display_h=2, display_y=-1; ogre warmaster: the nice_tile{tall=1} shorthand) with native_tall=true; five are 64x64 single images (the orc berserker and dredge captain use the NPC.lua:33 default-name image; the polar bear, anaconda and dreadmaster name their PNG with image=).",
          'new_ids_not_in_catalog_before_this_batch': [i['id'] for i in identities], 'identities': identities,
          'runtime_mutation_scan': {
              'method': "every talent of each identity (resolvers.talents, inherited base talents and the base-file talent lists) was resolved under game/modules/tome/data/talents and its mode read (sustained/activated/passive); the same talents/, timed_effects/, birth/ and class/ greps for writes to type/subtype/image/add_mos/add_displays/moddable_tile/replace_display/shader as batches S to Z were applied and give the same writer set; the resolvers sustains_at_birth, inscriptions, equip, racial and nice_tile and the base-file resolvers were read; every auto_classes site under zones/, general/ and maps/ was listed with its leaf name.",
              'writers_found': [
                  {'file': 'game/modules/tome/data/talents/corruptions/shadowflame.lua', 'line': 97, 'talent': "Flame of Urh'Rok", 'effect': 'sustain: __old_type={type,subtype}; type,subtype = demon,major; image untouched; restored on deactivate'},
                  {'file': 'game/modules/tome/data/talents/psionic/thought-forms.lua', 'line': 93, 'talent': 'thought-form summons (Solipsist tree)', 'effect': 'sets type/subtype/image/moddable_tile/add_mos on the summoned minion copied from its summoner, never on the caster'},
                  {'file': 'game/modules/tome/data/talents/chronomancy/anomalies.lua', 'line': 587, 'talent': 'anomaly summons', 'effect': 'creates a separate spawned NPC with another image; not the caster (the ultimate teluvorta only induces an anomaly, which spawns separate actors)'}],
              'other_hits_reviewed': [
                  'talents/spells/golemancy.lua and talents/uber/mag.lua (player-only moddable_tile writes: alchemist golem and the player skeleton; no identity of this batch; uber/mag.lua:197 only reads who.name == "dreadmaster")',
                  'timed_effects/physical.lua and other.lua (add_displays/replace_display only while the effect is active)', 'timed_effects/magical.lua (invisibility, shadow-simulacrum and similar shaders, dragon egg image, only while active)'],
              'timed_effects_review': "timed_effects write shader, replace_display, add_displays or image only while active (invisibility shaders, stone/ice/pin displays, Wrathroot, Shivgoroth form, dragon egg, Lord of Skulls): the matcher rejects them (native art shows) and restores the token when they end.",
              'sustains_at_birth_review': [
                  {'identity': 'ultimate faeros', 'sustained': ['Fiery Hands'], 'note': 'hand particles and temporary values only, no actor display write'},
                  {'identity': 'orc berserker', 'sustained': ['Berserker'], 'note': 'the base BASE_NPC_ORC_GRUSHNAK calls resolvers.sustains_at_birth(); temporary values only'},
                  {'identity': 'ultimate teluvorta', 'sustained': ['Reality Smearing'], 'note': 'shield particle and temporary values only'},
                  {'identity': 'bone horror', 'sustained': ['Bone Shield'], 'note': 'rotating ring particle and temporary values only'},
                  {'identity': 'sanguine horror', 'sustained': ['Blood Fury'], 'note': 'shield particles and temporary values only'},
                  {'identity': 'dreadmaster', 'sustained': ['Blur Sight'], 'note': 'the base BASE_NPC_GHOST and the leaf call resolvers.sustains_at_birth(); particle and temporary values only'},
                  {'identity': 'ogre warmaster, barrow wight, dredge captain, necrotic abomination', 'sustained': [], 'note': 'the resolvers.sustains_at_birth() calls find no sustained talent on these leaves (their talents are activated or passive)'},
                  {'identity': 'polar bear, anaconda', 'sustained': [], 'note': 'no sustains_at_birth on the leaf or base'}],
              'auto_classes_review': [
                  {'identity': 'all twelve', 'class': 'none', 'finding': "none of the twelve leaves or their bases has auto_classes; every auto_classes site in zones/, general/ and maps/ belongs to another leaf, so none can reach Flame of Urh'Rok and there is no urh_rok_form opt-in."}],
              'visibility_review': 'Identities with inscriptions or stealth (dredge captain, orc berserker, ogre warmaster, dreadmaster) can roll an invisibility rune/infusion or stealth that applies a shader effect while it lasts; the matcher rejects an actor with a shader (native art shows) and the token returns when it ends; token drawing follows actor visibility as for every other token.',
              'hits_in_batch': [],
              'no_hit': [i['native_name'] for i in identities]},
          'summons_and_same_body_copies': {
              'method': "grep of every actor definition, static map, quest script, vault, encounter, event and talent under game/modules/tome (data and class) for the twelve names and PNGs; talents that build summons/copies (summon-*, dreadmaster, master-of-flesh, master-of-bones, rot, thought-forms, simulacra/mirror images, Grand Arrival, golemancy, cloneFull users, hive summons) checked for copies of these bodies.",
              'findings': findings},
          'name_collisions_checked': [
              {'name': a['name'], 'other_definitions': ['none'], 'outcome': ('single actor definition bound to define_as ' + a['define_as'] if a['define_as'] else 'single actor definition without define_as; the catalog entry has no define_as and matches by exact name, type and subtype')} for a in {x['id']: x for x in A}.values()],
          'kept_native': [],
          'neighbours_kept_native': [
              {'name': 'Training Dummy', 'reason': 'listed at 12.0 by the scoring script but kept native since batch T'},
              {'name': 'entrenched horror', 'reason': 'score 1.5, tied with the dreadmaster; the tie is broken by row order (681 before 727), so it is the first candidate of the next batch'},
              {'name': 'orc summoner', 'reason': 'score 1.4, below this batch'}]}
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
                 'gate_reason': f"Exact source identity re-verified directly against game/modules/tome source (name={a['name']}, define_as={a['define_as']}, type={a['type']}/subtype={a['subtype']}, unique={a['unique']}, native_tall={a['native_tall']}); details and hashes in evidence/monster-batch-aa-20260930/source-contracts.json. {a['structure']}. Exact catalog entry only, never a whole-subtype mapping.",
                 'render_evidence': [{'path': render, 'sha256': evsha}]}
        if a.get('refinement'):
            entry['refinement'] = a['refinement']
        packs.setdefault(a['pack'], []).append(entry)
    for n, assets in packs.items():
        p = ADDON / f'art/production/batches/monster-batch-aa-{n}.json'
        if p.exists():
            print('exists, skipped', p.name)
            continue
        p.write_text(json.dumps({'schema': 1, 'batch_id': f'monster-batch-aa-{n}', 'assets': assets}, indent=2, ensure_ascii=False) + '\n')
        print('wrote', p.name)


if __name__ == '__main__':
    build()
