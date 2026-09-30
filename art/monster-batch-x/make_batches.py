"""Generate the monster-batch-x task packs and the pinned source-contract
evidence (survey-2 unscheduled list after batch W: giant acid ant, giant army
ant, yaech psion, blue crystal, devourer, skeleton assassin, assassin, elven
corruptor, orc fighter, greater telugoroth, teluvorta, dread; see SELECTION.md).
Pure bookkeeping: hashes native sources/sprites, writes JSON and the composite
family references. Retry packs are appended by later edits of retries.py (never
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
ANT, YAECH, CRYS, SKEL, ECAST, THIEF, TELU, GHOST, OGR, HORR = (
    'general/npcs/ant.lua', 'general/npcs/yaech.lua', 'general/npcs/crystal.lua', 'general/npcs/skeleton.lua',
    'general/npcs/elven-caster.lua', 'general/npcs/thieve.lua', 'general/npcs/telugoroth.lua', 'general/npcs/ghost.lua',
    'general/npcs/orc-grushnak.lua', 'general/npcs/horror.lua')
REFS = HERE / 'refs'
ART_REL = 'game/addons/tome-checker-revised/art/monster-batch-x/'
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


REF_ANTS = RC('ants', ['giant-white-ant', 'giant-yellow-ant', 'giant-brown-ant', 'giant-blue-ant', 'giant-carpenter-ant', 'giant-black-ant', 'giant-green-ant', 'giant-red-ant', 'giant-fire-ant', 'giant-ice-ant', 'giant-lightning-ant'], 4,
              'Eleven shipped ant tokens (white, golden yellow, brown, cobalt blue, black carpenter ant with big mandibles, plain glossy black ant, lime green ant, deep red ant, burnt-orange fire ant with a flame plume, pale cyan ice ant with a spike crest, lavender lightning ant with arcs): the acid ant and the army ant must not be recolours of these. The acid ant is a slate-grey ant with lime-yellow acid blotches and dripping acid; the army ant is a broad armoured bronze ant with a horned head shield.')
REF_YAECH = RC('yaech', ['yaech-diver', 'yeek-wayist', 'yaech-hunter', 'yaech-mindslayer'], 2,
               'Four shipped yeek-kin tokens (pale blue-white fluffy yaech diver swimming with bubbles, white yeek wayist with a dagger, umber-brown yaech hunter thrusting a trident, seafoam-teal yaech mindslayer floating cross-legged with a lightning ball and a shield ring): the yaech psion is an oat-cream and pale lilac fluffy floating psion with a rose-red pyrokinetic flame in one outstretched hand, not blue-white, not teal, not umber and not cross-legged.')
REF_CRYSTALS = RC('crystals', ['white-crystal', 'red-crystal', 'crimson-crystal', 'black-crystal'], 2,
                  'Four shipped crystal tokens (white crystal cluster of tall spires, red crystal fan of shards, crimson crystal with two fat ruby prisms, black crystal cluster on rock): the blue crystal is a sapphire-cerulean crystal formation curling like a breaking wave, a low arch of facets rather than upright spires, with aqua highlights.')
REF_SKEL = RC('skeletons', ['skeleton-warrior', 'skeleton-magus', 'armoured-skeleton-warrior', 'skeleton-archer', 'degenerated-skeleton-warrior', 'skeleton-master-archer'], 3,
              'Six shipped skeleton tokens (armoured sword skeleton, magus with flames, armoured shield skeleton, archer, degenerated warrior, master archer): the skeleton assassin is a lean charred ash-grey skeleton with a slate-blue cowl and two pale daggers, crouched low and stealthy, not armoured, not carrying a sword, shield or bow and not flaming.')
REF_THIEVES = RC('thieves', ['rogue', 'thief', 'bandit', 'assassin-lord', 'orc-assassin', 'skeleton-master-archer'], 3,
                 'Shipped thief tokens (hooded blue rogue, brown-cloaked thief, bare-chested bandit, the red-black Assassin Lord, the olive orc assassin): the assassin is a masked human in dove-grey and slate close-fitting clothes with a wine-red sash, lunging with one long dagger, not blue, not brown, not bare-chested and not red-black.')
REF_ELVES = RC('elves', ['elven-mage', 'elven-cultist', 'elven-blood-mage', 'grand-corruptor', 'elven-guard', 'elven-warrior'], 3,
               'Six shipped shalore tokens (purple-robed elven mage with a staff, green-cloaked cultist, grey-red blood mage, hooded red-black Grand Corruptor, guard, warrior): the elven corruptor is a pale silver-haired elf in orchid-magenta and plum robes with bone-white trim, a bone-topped staff and three bone shards orbiting, not purple-blue, not green and not red-black hooded.')
REF_ORCS = RC('orcs', ['orc-warrior', 'orc-soldier', 'orc-archer', 'orc-assassin', 'fiery-orc-wyrmic', 'icy-orc-wyrmic'], 3,
              'Six shipped orc tokens (olive orc warrior with a scimitar, spiked dark orc soldier with an axe, archer, hooded assassin, crimson-scaled fiery wyrmic with a hand axe, ice-scaled icy wyrmic): the orc fighter is a heavy bulwark, an olive-brown tusked orc buried in massive gunmetal plate behind a big shield held out front with a waraxe low behind it, not scaled, not spiked, not hooded and not robed.')
REF_TEMPORAL = RC('temporal', ['telugoroth', 'dredgling', 'dredge', 'shade-of-telos'], 2,
                  'Four shipped tokens (the round rainbow-swirl telugoroth orb, the dredgling and the dredge, pink flesh horrors, and the blue ice shade of telos): the greater telugoroth is a TALL NARROW golden-orange column of time-sand and cyan streaks with a white-gold core, not a round swirl orb; the teluvorta is a violet-lilac spiky storm-ball with clock-hand shards, not a rainbow swirl and not flesh.')
REF_GHOSTS = RC('ghosts', ['shade-of-telos', 'kors-fury', 'banshee', 'forest-wight', 'grave-wight', 'shadow-stalker'], 3,
                'Six shipped spectral tokens (blue ice shade of telos, teal Kor\'s Fury with a skull, pale cyan banshee, forest wight, grave wight, shadow stalker): the dread is a ragged smoky slate-violet wraith with burning red eyes and a glowing red chest, lunging forward with clawed arms, not cyan, not teal and not robed.')
REF_HORRORS = RC('horrors', ['bloated-horror', 'weirdling-beast', 'dredge', 'grannor-vin'], 2,
                 'Four shipped horror tokens (cream bloated horror, tan-pink weirdling beast, pink flesh dredge, lavender grannor\'vin slug): the devourer is a squat round crimson-rose body that is almost all one huge ring-toothed maw with stubby arms and legs, not cream, not tentacled and not slug-shaped.')

DEMPTY = ' no resolvers.equip that touches the body; no sustains_at_birth and no auto_classes on the leaf or base'
EQUIPONLY = ' resolvers.equip fills inventory slots only (no moddable_tile, so no display change)'

# ---- pack 1: ants ----
asset(1, 'giant-acid-ant', 'giant acid ant',
      "ardhungol, dreadfell, reknor, ruined-dungeon, old-forest and four more zones' ant pools (general/npcs/ant.lua:181, insect/ant, non-unique, no define_as, rank 1, base BASE_NPC_ANT, explicit image=npc/acid_ant.png); the only definition of this name; no vault, event or talent builds another actor with this name",
      [src(ANT, 'name = "giant acid ant"'), src(ANT, 'T_ACIDIC_SPRAY', after='name = "giant acid ant"'), src(ANT, 'define_as = "BASE_NPC_ANT"')],
      src(ANT, 'define_as = "BASE_NPC_ANT"'), None, 'insect', 'ant', False, False,
      'base BASE_NPC_ANT (insect/ant, no image=, no shader, no sustains_at_birth);' + EXPL + '; melee_project acid, talents Crawl Acid and Acidic Spray (activated); no equip, no auto_classes',
      'acid_ant.png',
      [STY, IDN('acid_ant.png', 'Native shape (64x64): a black ant with yellow acid blotches, a big swollen black abdomen and yellow acid dripping from the front. Keep the acid-oozing ant, but render the carapace in mid-light slate grey (not black) with lime-yellow acid pores and bright dripping acid.'), REF_ANTS],
      "A giant acid ant seen from a steep overhead three-quarter angle: a large ant angled diagonally with its head towards the lower left, a glossy SLATE-GREY and STEEL-BLUE-GREY carapace in a mid-light value with pale silver-white highlight planes, a big swollen bulbous abdomen raised towards the upper right that is covered with POROUS LIME-YELLOW ACID BLOTCHES and bright ACID-YELLOW-GREEN pores oozing glossy drops, thick strands of glowing lime-yellow acid dripping from the open mandibles and from the abdomen tip (short drips, kept on the body and close to it), glossy pale-yellow eye dots, antennae curled in close, legs tucked in, a few faint acid bubbles on the back. Corrosive, swollen, drooling and complete.",
      "Ants: the GIANT ACID ANT is the SLATE-GREY ONE with a swollen abdomen covered in lime-yellow acid blotches and dripping acid (silhouette: a diagonal ant with a big round raised abdomen and drops at both ends; hue: slate grey and steel blue-grey with lime-yellow and acid green; value: mid-light with bright yellow accents). The shipped black ant is a plain glossy black ant, the carpenter ant a black ant with huge mandibles, the green ant lime green and the yellow ant golden: this must not be black, not plain, not lime green all over and not golden. The other new ant of this batch is a bronze armoured army ant.",
      "Slate-grey and steel-blue-grey carapace in a mid-light value with pale silver highlight planes and a bright rim light, lime-yellow and acid-green blotches and drips with a bright yellow core (the acid stays on the ant and must not glow onto, tint or lighten the disc); nothing darker than dark slate-grey except the eye dots and thin seams; NO black chitin anywhere." + DISC,
      "READY single, no define_as (giant acid ant)", comp=COMP + FIT + COMPACT + BRIGHT + DARKFIX)

asset(1, 'giant-army-ant', 'giant army ant',
      "ardhungol, dreadfell, reknor, ruined-dungeon, old-forest and three more zones' ant pools (general/npcs/ant.lua:197, insect/ant, non-unique, no define_as, rank 1, base BASE_NPC_ANT, explicit image=npc/army_ant.png); the only definition of this name; no vault, event or talent builds another actor with this name",
      [src(ANT, 'name = "giant army ant"'), src(ANT, 'T_DISARM', after='name = "giant army ant"'), src(ANT, 'define_as = "BASE_NPC_ANT"')],
      src(ANT, 'define_as = "BASE_NPC_ANT"'), None, 'insect', 'ant', False, False,
      'base BASE_NPC_ANT (insect/ant, no image=, no shader, no sustains_at_birth);' + EXPL + '; resolvers.inscriptions(1, infusion), talents Stun and Disarm (activated); no equip that changes display, no auto_classes',
      'army_ant.png',
      [STY, IDN('army_ant.png', 'Native shape (64x64): a heavy black-and-gold striped ant with an armoured horned head and thick plated exoskeleton. Keep the heavy plated war ant with a horned head, but render the plates in burnished mid-light bronze-brown with bright orange-gold bands.'), REF_ANTS],
      "A giant army ant seen from a steep overhead three-quarter angle: a broad, heavily armoured ant facing straight up the picture, its exoskeleton made of thick overlapping riveted-looking PLATES of BURNISHED BRONZE-BROWN and dull gold in a mid-light value with bright ORANGE-GOLD BANDS across the abdomen and thorax and pale gold highlight planes, a wide flared HORNED HEAD SHIELD with two short curved horns, huge open serrated mandibles, thick armoured legs planted wide in a bracing stance (leg tips inside the disc), small pale-amber eyes, a pale bone-coloured scar on one plate. Heavy, armoured, planted and complete.",
      "Ants: the GIANT ARMY ANT is the BRONZE ARMOURED ONE facing straight up with a horned head shield and gold bands (silhouette: a broad plated body with a wide horned head and wide bracing legs; hue: burnished bronze-brown with orange-gold bands; value: mid-light). The shipped ants are slender, radial and smooth, and the new acid ant is a slate-grey diagonal ant with a swollen abdomen: this must not be slender, black or smooth and must not sit diagonally.",
      "Burnished bronze-brown and dull gold plates in a mid-light value with orange-gold bands, pale gold highlight planes and a bright rim light, pale amber eyes, bone-coloured scar (nothing glows onto the disc); nothing darker than dark bronze-brown except the eye dots and thin seams; NO black chitin anywhere." + DISC,
      "READY single, no define_as (giant army ant)", comp=COMP + FIT + COMPACT + BRIGHT + DARKFIX)

# ---- pack 2: yaech psion, blue crystal, devourer ----
asset(2, 'yaech-psion', 'yaech psion',
      "murgol-lair pool (general/npcs/yaech.lua:98, humanoid/yaech, non-unique, no define_as, rank 2, base BASE_NPC_YAECH, default-name image); single definition; the south-beach zone only draws yaech from the humanoid/yaech pool, so a yaech psion there is this same leaf",
      [src(YAECH, 'name = "yaech psion"'), src(YAECH, 'T_MINDLASH', after='name = "yaech psion"'), src(YAECH, 'define_as = "BASE_NPC_YAECH"')],
      src(YAECH, 'define_as = "BASE_NPC_YAECH"'), None, 'humanoid', 'yaech', False, False,
      'base BASE_NPC_YAECH (humanoid/yaech, can_breath water, no image=, no shader);' + DEF + ';' + EQUIPONLY + ' (trident); talents Pyrokinesis and Mindlash (activated); no sustains_at_birth on the leaf or base; no auto_classes on the leaf or base (only the Murgol-lair bosses have Mindslayer auto_classes)',
      'humanoid_yaech_yaech_psion.png',
      [STY, IDN('humanoid_yaech_yaech_psion.png', 'Native shape (64x64): a pale grey-white fluffy yeek-like swimmer with a dark headband floating with one hand reaching out, a purple psychic aura and a few bubbles. Keep the fluffy floating psion with a headband and a reaching hand, but oat-cream fur, a lilac aura and a rose-red flame in the hand.'), REF_YAECH],
      "A yaech psion seen from a steep overhead three-quarter angle: a small fluffy yeek-like aquatic psion with warm OAT-CREAM and pale BUFF fur in a light value, a rose-red headband, large calm dark-violet eyes with white glints, FLOATING a little above the floor leaning forward towards the lower right, the RIGHT HAND stretched out ahead with a swirling small ball of ROSE-RED and orange PYROKINETIC FLAME, the LEFT HAND pressed to the temple, a soft translucent LILAC-VIOLET psychic aura hugging the body (thin, no wider than the body), a few tiny bubbles. Focused, psionic, fluffy and complete.",
      "Yeeks: the YAECH PSION is the OAT-CREAM FLOATING ONE leaning forward with a rose-red flame in one outstretched hand and the other hand at its temple (silhouette: a round fluffy body with one long reaching arm; hue: oat-cream fur, rose-red flame and headband, lilac aura; value: light). The shipped yaech diver is a pale blue-white swimmer, the wayist a white yeek with a dagger, the hunter an umber lunger with a trident and the mindslayer a seafoam-teal cross-legged floater with a lightning ball: this must not be blue-white, teal, umber or cross-legged and must not hold a weapon.",
      "Oat-cream and buff fur in a light value with pale highlight planes and a bright rim light, rose-red headband and flame with a bright orange-yellow core, dark-violet eyes with white glints, soft lilac aura, tiny pale bubbles (the flame and aura stay on the creature and must not brighten, warm or tint the disc); nothing darker than dark violet except the pupils and thin seams." + DISC,
      "READY single, no define_as (yaech psion)", comp=COMP + FIT + COMPACT + BRIGHT)

asset(2, 'blue-crystal', 'blue crystal',
      "scintillating-caves and old-forest crystal pools (general/npcs/crystal.lua:142, immovable/crystal, non-unique, no define_as, rank 2, base BASE_NPC_CRYSTAL, explicit image=npc/crystal_blue.png, tint=BLUE); the only definition of this name; no vault, event or talent builds another actor with this name",
      [src(CRYS, 'name = "blue crystal"'), src(CRYS, 'T_TIDAL_WAVE', after='name = "blue crystal"'), src(CRYS, 'define_as = "BASE_NPC_CRYSTAL"')],
      src(CRYS, 'define_as = "BASE_NPC_CRYSTAL"'), None, 'immovable', 'crystal', False, False,
      'base BASE_NPC_CRYSTAL (immovable/crystal, base image npc/crystal_npc.png replaced by the leaf, no shader, no sustains_at_birth);' + EXPL + ' (the leaf tint=BLUE is a colour tint only, not a display field); talent Tidal Wave (activated); never_move; no equip, no auto_classes (the multi-hued and shimmering crystals carry shaders and are other names)',
      'crystal_blue.png',
      [STY, IDN('crystal_blue.png', 'Native shape (64x64): a translucent blue crystal formation curled like an arch over a base of small facets. Keep the sapphire-blue crystal formation, but draw it as a compact wave-like arch of chunky facets on a small dark rock base with aqua highlights.'), REF_CRYSTALS],
      "A blue crystal seen from a steep overhead three-quarter angle: a compact formation of chunky faceted SAPPHIRE-BLUE and CERULEAN crystal prisms with pale AQUA-CYAN highlight planes, arranged as a CURLING WAVE CREST, a low arch of leaning prisms rising from the lower left, cresting over the centre and curling down to the right like a breaking wave, one large central hexagonal prism, smaller shard prisms along the crest, a few deep-navy facets in the shadow planes of the crystals, a small base of grey-brown rock chips, bright white glints on the edges. Cool, faceted, wave-shaped and complete.",
      "Crystals: the BLUE CRYSTAL is the SAPPHIRE CURLING-WAVE ONE (silhouette: a low arch of leaning prisms curling over like a breaking wave; hue: sapphire and cerulean blue with aqua highlights; value: mid-light with white glints). The shipped white crystal is a cluster of tall white spires, the red crystal a fan of red shards, the crimson crystal two fat ruby prisms and the black crystal a dark cluster on rock: this must not be white, red, crimson or black and must not be a cluster of tall upright spires.",
      "Sapphire-blue and cerulean crystal in a mid-light value with pale aqua-cyan highlight planes, white edge glints, a few deep-navy shadow facets, grey-brown rock chips (the crystal glow stays on the crystal and must not tint or brighten the disc); nothing darker than deep navy except thin seams." + DISC,
      "READY single, no define_as (blue crystal)", comp=COMP + FIT + COMPACT + BRIGHT)

asset(2, 'devourer', 'devourer',
      "lake-nur, ardhungol, dreadfell and three more zones' horror pools (general/npcs/horror.lua:485, horror/eldritch, non-unique, no define_as, rank 2, base BASE_NPC_HORROR, default-name image); its own make_escort builds more of the same leaf by name; the only definition of this name",
      [src(HORR, 'name = "devourer"'), src(HORR, 'T_GNASHING_TEETH', after='name = "devourer"'), src(HORR, 'define_as = "BASE_NPC_HORROR"')],
      src(HORR, 'define_as = "BASE_NPC_HORROR"'), None, 'horror', 'eldritch', False, False,
      'base BASE_NPC_HORROR (horror/eldritch, faction horrors, no image=, no shader, no sustains_at_birth);' + DEF + '; talents Bloodbath (passive), Gnashing Teeth, Frenzied Leap and Frenzied Bite (activated); no equip, no auto_classes; make_escort of two more devourers by name',
      'horror_eldritch_devourer.png',
      [STY, IDN('horror_eldritch_devourer.png', 'Native shape (64x64): a headless round reddish-brown creature with stubby arms and legs and a huge round mouth full of teeth in place of a head. Keep the squat headless body that is all mouth, in crimson-rose flesh with bright ivory teeth.'), REF_HORRORS],
      "A devourer seen from a steep overhead three-quarter angle: a squat round HEADLESS horror in glistening CRIMSON-ROSE and warm salmon-pink flesh in a mid-light value with pale pink highlight planes, its whole front one huge round MAW ringed with two rows of BRIGHT IVORY TEETH around a dark-maroon throat, two stubby thick arms raised and clawed at the sides, two stubby legs planted wide, a few strands of glistening drool, a ridge of blistered flesh across the back. Ravenous, round and complete.",
      "Horrors: the DEVOURER is the CRIMSON-ROSE ROUND ONE that is almost all mouth with a ring of ivory teeth and stubby limbs (silhouette: a round ball with a big round toothy hole and four stubs; hue: crimson-rose and salmon flesh, ivory teeth; value: mid-light with bright teeth). The shipped bloated horror is a cream pear, the weirdling beast a tan-pink many-armed beast, the dredge a hulking pink horror and the grannor'vin a lavender slug: this must not be cream, tentacled, hulking or slug-shaped.",
      "Crimson-rose and salmon flesh in a mid-light value with pale pink highlight planes and a bright rim light, bright ivory teeth, dark-maroon throat, glistening drool (nothing glows onto the disc); nothing darker than dark maroon except the throat and thin seams." + DISC,
      "READY single, no define_as (devourer)", comp=COMP + FIT + COMPACT + BRIGHT)

# ---- pack 3: skeleton assassin, assassin, elven corruptor, orc fighter ----
asset(3, 'skeleton-assassin', 'skeleton assassin',
      "dreadfell, telmur, rak-shor-pride and two more zones' skeleton pools (general/npcs/skeleton.lua:194, undead/skeleton, non-unique, no define_as, rank 3, base BASE_NPC_SKELETON, default-name image); the only definition of this name; no vault, event or talent builds another actor with this name",
      [src(SKEL, 'name = "skeleton assassin"'), src(SKEL, 'T_SHADOWSTEP', after='name = "skeleton assassin"'), src(SKEL, 'resolvers.sustains_at_birth()', after='name = "skeleton assassin"'), src(SKEL, 'define_as = "BASE_NPC_SKELETON"')],
      src(SKEL, 'define_as = "BASE_NPC_SKELETON"'), None, 'undead', 'skeleton', False, False,
      'base BASE_NPC_SKELETON (undead/skeleton, no image=, no shader, no sustains_at_birth in the base);' + DEF + ';' + EQUIPONLY + ' (two daggers, light armour); resolvers.racial() adds only levelup talent tables; resolvers.inscriptions(1, rune); the leaf calls resolvers.sustains_at_birth(), starting the sustained talents Stealth and Shadow Combat (temporary values only, no type/subtype/image/add_mos write; Tempo is passive); no auto_classes',
      'undead_skeleton_skeleton_assassin.png',
      [STY, IDN('undead_skeleton_skeleton_assassin.png', 'Native shape (64x64): a charred-black skeleton with a dark hood, orange-red eye glints, a bandolier and a dagger in the raised hand. Keep the hooded lean skeleton with glowing eyes and a dagger, but render the bones as mid-light ash-grey with bone-cream highlights and a slate-blue cowl.'), REF_SKEL],
      "A skeleton assassin seen from a steep overhead three-quarter angle: a LEAN CHARRED skeleton crouched low and stalking, the bones a mid-light ASH-GREY and smoky brown with bright BONE-CREAM highlight planes on the skull, ribs and joints, a tattered SLATE-BLUE COWL and shoulder wrap in a mid value with frayed strips, a thin bandolier, TWO PALE STEEL DAGGERS held low in reverse grip (bright steel blades with bright edges, both blades short and inside the disc), small hot ORANGE-RED eye glints in the hood shadow, knees bent, leaning forward towards the upper left. Stealthy, angular, bone-and-cloth and complete." ,
      "Skeletons: the SKELETON ASSASSIN is the LEAN CROUCHED ASH-GREY ONE with a slate-blue cowl and two reverse-grip daggers (silhouette: a low leaning angular figure with two short blades; hue: ash grey and bone cream with slate blue and orange-red eye glints; value: mid-light). The shipped skeleton warrior and armoured warrior are armoured and upright with sword and shield, the magus is flaming and the archers hold bows: this must not be armoured, upright, flaming or carrying a sword, shield or bow. The other new hooded dagger figure is a human assassin in dove-grey cloth.",
      "Ash-grey and smoky-brown bones in a mid-light value with bone-cream highlight planes and a bright pale rim light, slate-blue cloth in a mid value with lighter edge strips, bright steel blades, small orange-red eye glints (nothing glows onto the disc); nothing darker than dark slate-grey except the eye sockets and thin seams; NO black cloth or black bone anywhere." + DISC,
      "READY single, no define_as (skeleton assassin)", comp=COMP + FIT + COMPACT + BRIGHT + DARKFIX)

asset(3, 'assassin', 'assassin',
      "maze, thieves-tunnels and ardhungol pools, the bandit-fortress zone and vaults and the thief-hideout vault (general/npcs/thieve.lua:139, humanoid/human, non-unique, define_as THIEF_ASSASSIN (shared verbatim with the later 'shadowblade' leaf, which is another name and stays native), rank 2, base BASE_NPC_THIEF, default-name image); the bandit-fortress zone and vaults build this same leaf by name",
      [src(THIEF, 'define_as = "THIEF_ASSASSIN"'), src(THIEF, 'name = "assassin"'), src(THIEF, 'T_LETHALITY', after='name = "assassin"'), src(THIEF, 'define_as = "BASE_NPC_THIEF"'), src('maps/zones/bandit-fortress.lua', '"assassin"')],
      src(THIEF, 'define_as = "BASE_NPC_THIEF"'), 'THIEF_ASSASSIN', 'humanoid', 'human', False, False,
      'base BASE_NPC_THIEF (humanoid/human, no image=, no shader, no sustains_at_birth in the base);' + DEF + ';' + EQUIPONLY + ' (two daggers, light armour); resolvers.racial() adds only levelup talent tables; the leaf calls resolvers.sustains_at_birth(), starting Stealth (temporary values only, no display write); talents Stealth, Dual Weapon Mastery, Tempo, Dual Strike, Coup de Grace, Lethality, Disarm; no auto_classes (the Assassin Lord in thieves-tunnels is another name)',
      'humanoid_human_assassin.png',
      [STY, IDN('humanoid_human_assassin.png', 'Native shape (64x64): a human in dark grey-black close-fitting clothes with a hood and face mask, a scarf-like collar and a dagger in the raised hand. Keep the masked hooded knife-fighter in close clothes, but dove-grey and slate cloth with a wine-red sash and a pale steel dagger.'), REF_THIEVES],
      "An assassin seen from a steep overhead three-quarter angle: a lean masked human in close-fitting DOVE-GREY and SLATE-BLUE cloth in a mid-light value with pale highlight planes, a hood and face mask leaving only a narrow eye slit with pale eyes, a WINE-RED SASH at the waist with a short tail, dark-brown leather straps and bracers, LUNGING FORWARD towards the upper right on a bent front leg with the RIGHT ARM stretched out ahead holding ONE LONG PALE-STEEL DAGGER (bright edge, the blade inside the disc) and the left hand low behind holding a second short dagger. Swift, lean, masked and complete." ,
      "Thieves: the ASSASSIN is the DOVE-GREY MASKED LUNGER with a wine-red sash and one long dagger stretched forward (silhouette: a lean diagonal lunge with one long blade to the upper right; hue: dove grey and slate blue with wine red and pale steel; value: mid-light). The shipped rogue is a hooded blue crouching figure, the thief a brown cloak, the bandit bare-chested, the Assassin Lord red-black and the orc assassin an olive orc: this must not be blue, brown, bare-chested, red-black or an orc. The skeleton assassin of this batch is a crouched bone figure with two daggers.",
      "Dove-grey and slate-blue cloth in a mid-light value with pale highlight planes and a bright rim light, wine-red sash, brown leather, bright pale-steel blades with bright edges (nothing glows onto the disc); nothing darker than dark slate-grey except the eye slit and thin seams; NO black cloth anywhere." + DISC,
      "READY single, define_as THIEF_ASSASSIN (assassin)", comp=COMP + FIT + COMPACT + BRIGHT + DARKFIX)

asset(3, 'elven-corruptor', 'elven corruptor',
      "crypt-kryl-feijan and mark-spellblaze pools (general/npcs/elven-caster.lua:144, humanoid/shalore, non-unique, no define_as, rank 3, base BASE_NPC_ELVEN_CASTER, default-name image); the only definition of this name (the Grand Corruptor and the Rhaloren Inquisitor are other names with their own tokens)",
      [src(ECAST, 'name = "elven corruptor"'), src(ECAST, 'T_BONE_SHIELD', after='name = "elven corruptor"'), src(ECAST, 'resolvers.sustains_at_birth()', after='name = "elven corruptor"'), src(ECAST, 'define_as = "BASE_NPC_ELVEN_CASTER"')],
      src(ECAST, 'define_as = "BASE_NPC_ELVEN_CASTER"'), None, 'humanoid', 'shalore', False, False,
      'base BASE_NPC_ELVEN_CASTER (humanoid/shalore, faction rhalore, no image=, no shader, no sustains_at_birth in the base);' + DEF + ';' + EQUIPONLY + ' (staff, cloth armour, charm); resolvers.racial() adds only levelup talent tables; resolvers.inscriptions(1, rune); the leaf calls resolvers.sustains_at_birth(), starting Bone Shield (a shield particle and temporary values only, no type/subtype/image/add_mos write); talents Staff Mastery, Blood Spray, Drain, Soul Rot, Blood Grasp, Bone Spear; NO auto_classes on this leaf (only the Grand Corruptor and Rhaloren Inquisitor leaves carry Corruptor auto_classes)',
      'humanoid_shalore_elven_corruptor.png',
      [STY, IDN('humanoid_shalore_elven_corruptor.png', 'Native shape (64x64): a pale elf in dark dusky robes with a tall pointed hood and a long staff, a small orchid trim on the sleeves. Keep the robed pale elf with a tall staff, but render the robes orchid-magenta and plum in a mid-light value with bone-white trim, bone shards orbiting.'), REF_ELVES],
      "An elven corruptor seen from a steep overhead three-quarter angle: a slender pale SHALORE elf with silver-white hair, pointed ears and a gaunt calm face, wearing long ORCHID-MAGENTA and PLUM robes in a mid-light value with pale pink highlight planes and BONE-WHITE trim, ribs-like bone clasps across the chest and a bone-and-brass collar, holding a BONE-TOPPED STAFF in the right hand angled up and outward (the staff head a small bone skull-crescent, the staff short enough to stay inside the disc), the left hand open at the hip dripping a few dark-red drops, THREE small pale BONE SHARDS orbiting the body at shoulder height. Corrupt, elegant, robed and complete." ,
      "Elves: the ELVEN CORRUPTOR is the ORCHID-MAGENTA ROBED ONE with bone trim, a bone-topped staff and three orbiting bone shards (silhouette: a slim robed figure with a diagonal staff and three small shards around it; hue: orchid magenta and plum with bone white and silver hair; value: mid-light). The shipped elven mage wears blue-purple robes, the cultist green, the blood mage grey and dark red, the Grand Corruptor a red-black hood, and the guard and warrior wear armour: this must not be blue-purple, green, red-black or armoured and must not be hooded in black.",
      "Orchid-magenta and plum robes in a mid-light value with pale pink highlight planes and a bright rim light, bone-white trim and shards, silver-white hair, pale skin, dark-red drops (nothing glows onto the disc); nothing darker than dark plum except the eyes and thin seams; NO black cloth anywhere." + DISC,
      "READY single, no define_as (elven corruptor)", comp=COMP + FIT + COMPACT + BRIGHT + DARKFIX)

asset(3, 'orc-fighter', 'orc fighter',
      "vor-armoury, ardhungol, unremarkable-cave and one more zone's pools (general/npcs/orc-grushnak.lua:55, humanoid/orc, non-unique, no define_as, rank 2, base BASE_NPC_ORC_GRUSHNAK, default-name image); the only definition of this name (the orc elite fighter is another name)",
      [src(OGR, 'name = "orc fighter"'), src(OGR, 'T_OVERPOWER', after='name = "orc fighter"'), src(OGR, 'define_as = "BASE_NPC_ORC_GRUSHNAK"')],
      src(OGR, 'define_as = "BASE_NPC_ORC_GRUSHNAK"'), None, 'humanoid', 'orc', False, False,
      'base BASE_NPC_ORC_GRUSHNAK (humanoid/orc, faction orc-pride, no image=, no shader, no sustains_at_birth);' + DEF + ';' + EQUIPONLY + ' (waraxe, shield, massive armour); resolvers.racial() adds only levelup talent tables; talents Armour Training, Weapon Combat, Weapons Mastery, Rush, Shield Pummel, Overpower, Disarm (none is sustained at birth: no sustains_at_birth on the leaf or base); no auto_classes',
      'humanoid_orc_orc_fighter.png',
      [STY, IDN('humanoid_orc_orc_fighter.png', 'Native shape (64x64): an olive-green orc in heavy dark plate armour, holding a sword raised behind and a weapon across the body. Keep the heavily armoured tusked orc, but render the plate as mid-light gunmetal steel with a big shield held out front.'), REF_ORCS],
      "An orc fighter seen from a steep overhead three-quarter angle: a stocky OLIVE-BROWN tusked orc buried in MASSIVE GUNMETAL-STEEL PLATE armour in a mid-light value with bright pale steel highlight planes and dull brass rivets, a horned open steel helm with a scowling face, a big convex KITE-SHAPED STEEL SHIELD held out in front of the body in the left arm (the shield with a bold khaki-and-rust painted chevron, no text), a broad WARAXE held low behind the shield in the right hand with its bright head at the lower right, a khaki tabard over the plate, feet planted wide. Bulwark, planted and complete." ,
      "Orcs: the ORC FIGHTER is the GUNMETAL-PLATED BULWARK behind a big shield with a waraxe low behind it (silhouette: a wide blocky mass dominated by a big front shield; hue: gunmetal steel, khaki tabard, olive-brown skin; value: mid-light). The shipped orc warrior is an olive scimitar fighter without armour, the soldier a spiked dark axeman, the archer holds a bow, the assassin is hooded and the two wyrmics are red and pale blue scaled: this must not be unarmoured, spiked, hooded, robed or scaled and must not swing a weapon overhead.",
      "Olive-brown skin, gunmetal-steel plate in a mid-light value with bright pale steel highlight planes and a bright rim light, dull brass rivets, khaki and rust paint, bright steel axe head with a bright edge (nothing glows onto the disc); nothing darker than dark gunmetal except the eye slits and thin seams; NO black armour anywhere." + DISC,
      "READY single, no define_as (orc fighter)", comp=COMP + FIT + COMPACT + BRIGHT + DARKFIX)

# ---- pack 4: temporal elementals and dread ----
asset(4, 'greater-telugoroth', 'greater telugoroth',
      "temporal-rift pool (general/npcs/telugoroth.lua:116, elemental/temporal, non-unique, no define_as, rank 2, base BASE_NPC_TELUGOROTH, default-name image plus an explicit nice_tile tall body); the only definition of this name (the plain telugoroth is catalogued separately, the ultimate telugoroth is another name and stays native)",
      [src(TELU, 'name = "greater telugoroth"'), src(TELU, 'resolvers.nice_tile', after='name = "greater telugoroth"'), src(TELU, 'resolvers.sustains_at_birth()', after='name = "greater telugoroth"'), src(TELU, 'define_as = "BASE_NPC_TELUGOROTH"')],
      src(TELU, 'define_as = "BASE_NPC_TELUGOROTH"'), None, 'elemental', 'temporal', False, True,
      'base BASE_NPC_TELUGOROTH (elemental/temporal, levitation, no image=, no shader, no sustains_at_birth in the base);' + TALLD % 'elemental_temporal_greater_telugoroth' + '; the leaf calls resolvers.sustains_at_birth() but its talents Turn Back the Clock and Echoes from the Past are activated (nothing sustained is started, and any sustain would touch only temporary values); no auto_classes',
      'elemental_temporal_greater_telugoroth.png',
      [STY, IDN('elemental_temporal_greater_telugoroth.png', 'Native shape (64x128, tall): a tall shimmering column of swirling orange, gold and blue temporal energy with curling tendrils. Keep the tall swirling time column in gold, orange and cyan, drawn as ONE compact upright column filling the disc, no tall canvas.'), REF_TEMPORAL],
      "A greater telugoroth seen from a steep overhead three-quarter angle: a TALL NARROW UPRIGHT COLUMN of swirling temporal energy, GOLDEN-ORANGE and amber time-sand streams braided with CYAN and pale-blue streaks in a light-mid value, a brilliant WHITE-GOLD core glowing in the middle of the column, thick spiral ribbons curling up and around the column like a vertical vortex and a few floating pale-gold sand grains drifting close to it, the column widest near the top and pinched at the waist like an hourglass, fading into wisps at the very bottom and top (every wisp inside the disc, the column no wider than one third of the disc). Fluid, vertical, glowing and complete.",
      "Temporal elementals: the GREATER TELUGOROTH is the TALL NARROW GOLDEN COLUMN with a white-gold core and an hourglass pinch (silhouette: a vertical narrow column, wide at the top and pinched at the waist; hue: golden-orange and amber with cyan streaks and a white-gold core; value: light-mid). The shipped telugoroth is a ROUND rainbow swirl orb filling the disc, the dredge horrors are pink flesh and the shade of telos blue ice: this must not be a round swirl orb, not pink flesh and not blue ice, and must not fill the disc sideways.",
      "Golden-orange and amber energy streams with cyan and pale-blue streaks in a light-mid value with a bright white-gold core and pale highlights, pale-gold sand grains (the glow stays on the column and must not brighten, warm or tint the disc); nothing darker than deep amber-brown except a few thin swirl seams; the disc stays neutral charcoal at reference lightness." + DISC,
      "READY tall (greater telugoroth, native_tall)", comp=COMP + FIT + COMPACT + BRIGHT)

asset(4, 'teluvorta', 'teluvorta',
      "temporal-rift pool (general/npcs/telugoroth.lua:155, elemental/temporal, non-unique, no define_as, rank 2, base BASE_NPC_TELUGOROTH, default-name image); the only definition of this name (the greater and ultimate teluvortas are other names, tall bodies, and stay native)",
      [src(TELU, 'name = "teluvorta"'), src(TELU, 'doTeluvortaSwap', after='name = "teluvorta"'), src(TELU, 'resolvers.sustains_at_birth()', after='name = "teluvorta"'), src(TELU, 'define_as = "BASE_NPC_TELUGOROTH"')],
      src(TELU, 'define_as = "BASE_NPC_TELUGOROTH"'), None, 'elemental', 'temporal', False, False,
      'base BASE_NPC_TELUGOROTH (elemental/temporal, levitation, no image=, no shader, no sustains_at_birth in the base);' + DEF + '; on_act randomly swaps places with a target (teleport particles only, no display write); talents Dust to Dust and Temporal Wake (the leaf calls resolvers.sustains_at_birth() but neither is sustained); no equip, no auto_classes',
      'elemental_temporal_teluvorta.png',
      [STY, IDN('elemental_temporal_teluvorta.png', 'Native shape (64x64): a fuzzy purple-blue spiky sphere of chaotic energy with orange flecks. Keep the spiky chaotic time-storm sphere, but render it as a mid-light violet-lilac storm-ball with sharp pale clock-hand shards radiating out.'), REF_TEMPORAL],
      "A teluvorta seen from a steep overhead three-quarter angle: a round chaotic TIME-STORM ball of VIOLET, LILAC and pale ORCHID energy in a mid-light value, a bright WHITE-LILAC core, many SHARP PALE JAGGED SHARDS radiating outward like the hands of shattered clocks and broken hourglass glass (pale lilac-white with bright edges, the shard tips inside the disc), a few thin orange-gold time-spark flecks caught between the shards, a subtle broken-ring clock-face arc behind the ball. Chaotic, spiky, spherical and complete." ,
      "Temporal elementals: the TELUVORTA is the VIOLET-LILAC SPIKY STORM-BALL with clock-hand shards (silhouette: a round core bristling with sharp radiating shards like a burst; hue: violet, lilac and orchid with white-lilac shards and small orange-gold sparks; value: mid-light). The shipped telugoroth is a smooth rainbow swirl orb without spikes, the greater telugoroth of this batch a tall golden column, and the dredge and dredgling pink flesh: this must not be a smooth swirl, must not be golden and tall and must not be flesh.",
      "Violet, lilac and orchid energy in a mid-light value with a bright white-lilac core, pale lilac-white shards with bright edges, tiny orange-gold sparks (the glow stays on the creature and must not brighten, tint or purple the disc); nothing darker than deep violet except a few thin seams; the disc stays neutral charcoal at reference lightness." + DISC,
      "READY single, no define_as (teluvorta)", comp=COMP + FIT + COMPACT + BRIGHT)

asset(4, 'dread', 'dread',
      "dreadfell, rak-shor-pride, telmur and one more zone's ghost pools, the dreadmaster's summon list and the necromancer Dread minion (general/npcs/ghost.lua:64, undead/ghost, non-unique, no define_as, rank 2, base BASE_NPC_GHOST, explicit image=npc/dread.png); the Dread talent (talents/spells/dreadmaster.lua:35, minions_list.dread) and the dreadmaster leaf's summon (ghost.lua:96) build the same-named minion with type undead, subtype ghost, the same image and no define_as, so they wear the same token by the ordinary name key (see summons_and_same_body_copies)",
      [src(GHOST, 'name = "dread"'), src(GHOST, 'T_BURNING_HEX', after='name = "dread"'), src(GHOST, 'resolvers.sustains_at_birth()', after='define_as = "BASE_NPC_GHOST"'), src(GHOST, 'name="dread"', after='name = "dreadmaster"'), src('talents/spells/dreadmaster.lua', 'name = "dread"'), src('talents/spells/dreadmaster.lua', 'dread_minion = "dread"'), src(GHOST, 'define_as = "BASE_NPC_GHOST"')],
      src(GHOST, 'define_as = "BASE_NPC_GHOST"'), None, 'undead', 'ghost', False, False,
      'base BASE_NPC_GHOST (undead/ghost, pass_wall, no image=, no shader);' + EXPL + '; talents Burning Hex and Blur Sight (Blur Sight sustained); the base resolvers.sustains_at_birth() starts Blur Sight (a phantasm_shield particle and temporary values only, no type/subtype/image/add_mos write); no equip, no auto_classes',
      'dread.png',
      [STY, IDN('dread.png', 'Native shape (64x64): a black ragged wraith with glowing red eyes and a glowing red core in the chest, one arm hanging and one reaching, a ragged tail of shadow. Keep the ragged wraith with red eyes and a glowing red chest, but render the body as mid-light smoky slate-violet with pale silver rim highlights.'), REF_GHOSTS],
      "A dread seen from a steep overhead three-quarter angle: a hulking ragged SMOKY WRAITH whose body is a mid-light SLATE-VIOLET and ash-grey mass of torn smoke and shadowy rags with pale SILVER-LAVENDER highlight planes and a bright pale rim light along the whole upper-left outline, two burning RED-ORANGE eyes, a glowing RED-ORANGE burning-hex core in the chest with bright yellow-orange embers around it, both long clawed arms stretched forward towards the lower left, the lower body trailing into a ragged tail of torn smoke curling to the upper right (every wisp inside the disc). Menacing, ragged, glowing-eyed and complete." ,
      "Spectres: the DREAD is the RAGGED SLATE-VIOLET WRAITH with burning red eyes, a glowing red chest core and clawed arms reaching forward (silhouette: a hulking ragged mass with two long reaching arms and a curling tail; hue: slate violet and ash grey with red-orange fire; value: mid-light with bright red-orange accents). The shipped shade of telos is a blue ice figure, Kor's Fury a teal skull, the banshee pale cyan, the wights robed and the shadow stalker dark: this must not be blue, teal, cyan, robed or black.",
      "Slate-violet and ash-grey smoke mass in a mid-light value with pale silver-lavender highlight planes and a bright rim light, red-orange eyes and chest core with bright yellow-orange embers (the glow stays on the creature and must not tint, warm or light the disc); nothing darker than dark slate-violet except thin cloth seams; NO black body anywhere." + DISC,
      "READY single, no define_as (dread)", comp=COMP + FIT + COMPACT + BRIGHT + DARKFIX)


def retry(id_, pack, **changes):
    base = next(a for a in A if a['id'] == id_)
    A.append(dict(base, pack=pack, **changes))


# ---- retry packs are appended below by later edits of retries.py ----
exec((HERE / 'retries.py').read_text()) if (HERE / 'retries.py').exists() else None

EXPL_IDS = ('giant-acid-ant', 'giant-army-ant', 'blue-crystal', 'dread')
TALL_IDS = ('greater-telugoroth',)
PNGF = {a['id']: 'NPC.lua:33 default-name image on the leaf (no image=/nice_tile)' for a in A}
PNGF.update({i: 'explicit image= on the leaf (no nice_tile/add_mos)' for i in EXPL_IDS})
PNGF.update({i: 'NPC.lua:33 default-name image on the leaf plus an explicit nice_tile tall body (image=invis.png, one add_mos entry with display_h=2, display_y=-1 naming the same PNG)' for i in TALL_IDS})


def build():
    packs = {}
    identities = []
    render = 'game/addons/tome-checker-revised/evidence/monster-batch-x-20260930/source-contracts.json'
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
        "All twelve names have exactly one leaf definition. The zone pools, the vaults (bandit-fortress and thief-hideout for the assassin), the bandit-fortress zone map and the devourer's own make_escort only build those same leaves through name/random_filter lookups, so they are the very same actors; random bosses made from a flat entry go through the existing captureRandomOrigin path, a random boss made from the non-unique native-tall greater telugoroth stays native (only unique tall bodies qualify).",
        "Dread: talents/spells/dreadmaster.lua:35 (the necromancer Dread talent, minions_list.dread), talents/spells/dreadmaster.lua:115 (the dreadmaster minion's dread_minion) and the dreadmaster leaf's summon (general/npcs/ghost.lua:96, name=dread, type=undead, subtype=ghost) create actors named 'dread' with type undead, subtype ghost and the identical explicit image=npc/dread.png, no define_as, no shader/moddable_tile/add_mos; they wear the same token by the ordinary name key. The quest antimagic and the Arena generator name the same leaf. NO variants entry and NO image alias is needed.",
        "Assassin: the leaf carries define_as THIEF_ASSASSIN, which the later 'shadowblade' leaf in the same file repeats verbatim (thieve.lua:163); the catalog entry binds define_as THIEF_ASSASSIN together with name 'assassin', so a shadowblade (other name, same define_as) stays native. The bandit-fortress zone map and the bandit-fortress and thief-hideout vaults name the assassin, reaching this same leaf; the Assassin Lord (thieves-tunnels, its own token) and the orc assassin are other names.",
        "Greater telugoroth: non-unique native-tall body (nice_tile image=invis.png, one add_mos entry display_h=2, display_y=-1, the default-name PNG), catalog flag native_tall=true. The plain telugoroth (its own token), the ultimate telugoroth and the greater/ultimate teluvortas (other names, tall bodies) stay native; the teluvorta is a plain 64x64 default-name body (its on_act swap only moves actors and plays teleport particles).",
        "No summon, clone, event or talent builds an actor with any of the other names using a different native PNG (grep of every actor definition, static map, quest script, vault, encounter, event and talent under game/modules/tome for the names and PNGs, including data/talents/gifts wild summons and thought-forms), so no image_aliases entry and no variants entry are added.",
        "Neighbours that reuse a name or subtype but stay native: 'shadowblade' (same define_as THIEF_ASSASSIN, other name and PNG), 'assassin lord', 'orc assassin', 'orc elite fighter', 'giant black ant', 'giant carpenter ant', 'ultimate telugoroth', 'greater teluvorta', 'ultimate teluvorta', 'dreadmaster', 'multi-hued crystal' and 'shimmering crystal' (shaders), 'yaech mindslayer' (catalogued separately), 'uruivellas' and 'thaurhereg' (tied with the devourer at 3.4 for the last slot and dropped by survey-document order).",
        "Result: no per-construct `variants` entry and no `image_aliases` entry is needed for this batch; the Dread-talent minions and the dreadmaster's summons are covered by the exact name key.",
    ]
    ev = {'schema': 1,
          'task': "monster-batch-x: static re-verification (no game launch) of the twelve identities that follow batch W in the survey-2 unscheduled list (giant acid ant, giant army ant, yaech psion, blue crystal, devourer, skeleton assassin, assassin, elven corruptor, orc fighter, greater telugoroth, teluvorta, dread) against game/modules/tome source and native sprites. Every field below was read from source: name, type/subtype, define_as (only the assassin binds one, THIEF_ASSASSIN), explicit or NPC.lua:33 default image, unique, PNG on disk, and absence of moddable_tile/shader/anim/add_displays on each leaf and its base. Findings: eleven identities are 64x64 single images (the ants, blue crystal and dread name their PNG with image=; the others use the NPC.lua:33 default-name image); the greater telugoroth is a non-unique native-tall body (nice_tile image=invis.png with one explicit add_mos display_h=2, display_y=-1) with native_tall=true.",
          'new_ids_not_in_catalog_before_this_batch': [i['id'] for i in identities], 'identities': identities,
          'runtime_mutation_scan': {
              'method': "every talent of each identity (resolvers.talents, inherited base talents, racial levelup talents via resolvers.racial and the base-file talent lists) was resolved under game/modules/tome/data/talents and its mode read (sustained/activated/passive); the whole talents/, timed_effects/, birth/ and class/ trees were grepped for writes to type/subtype/image/add_mos/add_displays/moddable_tile/replace_display/shader (regex on any receiver, plus the tuple assignment form) and the results reviewed line by line, giving the same writer set as batches S to W; the resolvers sustains_at_birth, racial, inscriptions, equip, auto_equip_filters and nice_tile and the base-file resolvers were read; every auto_classes site under zones/, general/ and maps/ was listed with its leaf name.",
              'writers_found': [
                  {'file': 'game/modules/tome/data/talents/corruptions/shadowflame.lua', 'line': 97, 'talent': "Flame of Urh'Rok", 'effect': 'sustain: __old_type={type,subtype}; type,subtype = demon,major; image untouched; restored on deactivate'},
                  {'file': 'game/modules/tome/data/talents/psionic/thought-forms.lua', 'line': 93, 'talent': 'thought-form summons (Solipsist tree)', 'effect': 'sets type/subtype/image/moddable_tile/add_mos on the summoned minion copied from its summoner, never on the caster'},
                  {'file': 'game/modules/tome/data/talents/chronomancy/anomalies.lua', 'line': 587, 'talent': 'anomaly summons', 'effect': 'creates a separate spawned NPC with another image; not the caster'}],
              'other_hits_reviewed': [
                  'talents/psionic/mentalism.lua:196 (party-member record for a Projection clone, sets the party subtype only)', 'talents/psionic/dream-forge.lua:135 and talents/celestial/twilight.lua (terrain objects)',
                  'talents/spells/golemancy.lua:152 and talents/uber/mag.lua:396 (golem and lich player display)', 'talents/chronomancy/timeline-threading.lua:342 (clears a shader on a clone)',
                  'timed_effects/physical.lua and other.lua (add_displays/replace_display only while the effect is active)', 'timed_effects/magical.lua (invisibility and shadow-simulacrum shaders, dragon egg, Lord of Skulls replace_display, all only while active)', 'class/FortressPC.lua (the Fortress player)'],
              'timed_effects_review': "timed_effects write shader, replace_display, add_displays or image only while active (invisibility shaders, stone/ice/pin displays, Wrathroot, Shivgoroth form, dragon egg, Lord of Skulls): the matcher rejects them (native art) until they end; none is applied at birth to these identities.",
              'sustains_at_birth_review': [
                  {'identity': 'dread', 'sustained': ['Blur Sight'], 'note': 'started by the base BASE_NPC_GHOST resolvers.sustains_at_birth(); a phantasm_shield particle and temporary values only, no type/subtype/image/add_mos/shader write (the Dread-talent minion also calls resolvers.sustains_at_birth())'},
                  {'identity': 'skeleton assassin', 'sustained': ['Stealth', 'Shadow Combat'], 'note': 'the leaf calls resolvers.sustains_at_birth(); stealth and shadow-combat temporary values only, no display field on the caster (Tempo and the weapon talents are passive)'},
                  {'identity': 'assassin', 'sustained': ['Stealth'], 'note': 'the leaf calls resolvers.sustains_at_birth(); stealth temporary values only'},
                  {'identity': 'elven corruptor', 'sustained': ['Bone Shield'], 'note': 'the leaf calls resolvers.sustains_at_birth(); a bone-shield particle and temporary values only, no type/subtype/image/add_mos write'},
                  {'identity': 'greater telugoroth, teluvorta', 'sustained': [], 'note': 'the leaves call resolvers.sustains_at_birth() but Turn Back the Clock, Echoes from the Past, Dust to Dust and Temporal Wake are activated talents: nothing is started'},
                  {'identity': 'giant acid ant, giant army ant, yaech psion, blue crystal, devourer, orc fighter', 'sustained': [], 'note': 'no sustains_at_birth on the leaf or base (Bloodbath and the weapon talents are passive; Crawl Acid, Acidic Spray, Stun, Disarm, Pyrokinesis, Mindlash, Tidal Wave, Gnashing Teeth and the frenzy talents are activated)'}],
              'auto_classes_review': [
                  {'identity': 'all twelve', 'class': 'none', 'finding': "none of the twelve leaves or their bases has auto_classes; every auto_classes site in zones/, general/ and maps/ belongs to another leaf (listed by leaf name: Grand Corruptor, Rhaloren Inquisitor, Kryl-Feijan, Assassin Lord, Subject Z, the orc pride bosses and other named bosses). The elven corruptor pool zones (crypt-kryl-feijan, mark-spellblaze) only give Corruptor auto_classes to the Kryl-Feijan and Grand Corruptor leaves.", 'outcome': "no hit: Flame of Urh'Rok is not reachable, so urh_rok_form is NOT set on any entry; the opt-in count stays 5."}],
              'visibility_review': 'The assassin and the skeleton assassin have base stealth and Stealth at birth; identities with inscriptions (orc fighter, elven corruptor, yaech psion, skeleton assassin) can roll an invisibility rune/infusion that applies a transient invis_edge shader through timed effects; the overlay already respects actor visibility and the transient shader rejects the token (native art) until it ends. No identity changes display at birth.',
              'hits_in_batch': [],
              'no_hit': [i['native_name'] for i in identities]},
          'summons_and_same_body_copies': {
              'method': "grep of every actor definition, static map, quest script, vault, encounter, event and talent under game/modules/tome (data and class) for the twelve names and PNGs; talents that build summons/copies (summon-*, dreadmaster, master-of-flesh, master-of-bones, rot, thought-forms, simulacra/mirror images, Grand Arrival, cloneFull users) checked for copies of these bodies.",
              'findings': findings},
          'name_collisions_checked': [
              {'name': a['name'], 'other_definitions': ['none'], 'outcome': ('single actor definition bound to define_as ' + a['define_as'] if a['define_as'] else 'single actor definition without define_as; the catalog entry has no define_as and matches by exact name, type and subtype')} for a in {x['id']: x for x in A}.values() if a['id'] not in ('dread', 'assassin')] + [
              {'name': 'dread', 'other_definitions': ['Dread talent minion talents/spells/dreadmaster.lua:35 (same name, type, subtype and image, no define_as)', 'dreadmaster minion dread_minion talents/spells/dreadmaster.lua:71 and :115', 'dreadmaster leaf summon general/npcs/ghost.lua:96'], 'outcome': 'the zone leaf is the catalog body; the minions are the same body and wear the same token through the ordinary key'},
              {'name': 'assassin', 'other_definitions': ["'shadowblade' general/npcs/thieve.lua:163 repeats define_as THIEF_ASSASSIN under another name and PNG"], 'outcome': 'single actor named assassin bound to define_as THIEF_ASSASSIN; a shadowblade fails the name key and stays native'}],
          'kept_native': [],
          'neighbours_kept_native': [
              {'name': 'shadowblade', 'reason': 'shares the THIEF_ASSASSIN define_as but is another name and PNG'},
              {'name': 'uruivellas', 'reason': 'not selected: three-way tie at 3.4 (devourer, uruivellas, thaurhereg) for the last slot; survey-document order (devourer row 668, uruivellas 830) takes the devourer; tall major demon, next batch candidate'},
              {'name': 'thaurhereg', 'reason': 'not selected: same tie as uruivellas'},
              {'name': 'greater teluvorta', 'reason': 'other name, tall body, 2.5'}]}
    out = ADDON / 'evidence/monster-batch-x-20260930/source-contracts.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(ev, indent=2, ensure_ascii=False) + '\n')
    evsha = hashlib.sha256(out.read_bytes()).hexdigest()
    for a in A:
        refs = [{'path': p, 'sha256': sha(p), 'role': r, 'note': n} for r, p, n in a['refs']]
        entry = {'asset_id': a['id'], 'native_name': a['name'], 'scope': a['scope'], 'sources': a['srcs'], 'references': refs,
                 'contrast_dimensions': list(a['dims']),
                 'prompt_fields': {'subject': a['subject'], 'contrast': a['contrast'], 'composition': a['comp'] or COMP, 'palette': a['palette']},
                 'kind': 'creature', 'max_attempts': 1, 'gate': 'ready',
                 'gate_reason': f"Exact source identity re-verified directly against game/modules/tome source (name={a['name']}, define_as={a['define_as']}, type={a['type']}/subtype={a['subtype']}, unique={a['unique']}, native_tall={a['native_tall']}); details and hashes in evidence/monster-batch-x-20260930/source-contracts.json. {a['structure']}. Exact catalog entry only, never a whole-subtype mapping.",
                 'render_evidence': [{'path': render, 'sha256': evsha}]}
        if a.get('refinement'):
            entry['refinement'] = a['refinement']
        packs.setdefault(a['pack'], []).append(entry)
    for n, assets in packs.items():
        p = ADDON / f'art/production/batches/monster-batch-x-{n}.json'
        if p.exists():
            print('exists, skipped', p.name)
            continue
        p.write_text(json.dumps({'schema': 1, 'batch_id': f'monster-batch-x-{n}', 'assets': assets}, indent=2, ensure_ascii=False) + '\n')
        print('wrote', p.name)


if __name__ == '__main__':
    build()
