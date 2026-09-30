"""Generate the monster-batch-y task packs and the pinned source-contract
evidence (survey-2 unscheduled list after batch X: uruivellas, thaurhereg,
orc corruptor, temporal stalker, broken golem, golem, blade horror, animated
mummy wrappings, grizzly bear, weaver patriarch, luminous horror, necrotic mass;
see SELECTION.md). Pure bookkeeping: hashes native sources/sprites, writes JSON
and the composite family references. Retry packs are appended by later edits of
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
REFS = HERE / 'refs'
ART_REL = 'game/addons/tome-checker-revised/art/monster-batch-y/'
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


MAJD, ORCR, TEMP, CONS, HORR, HORU, MUMZ, BEAR, SPID = (
    'general/npcs/major-demon.lua', 'general/npcs/orc-rak-shor.lua', 'general/npcs/horror_temporal.lua',
    'general/npcs/construct.lua', 'general/npcs/horror.lua', 'general/npcs/horror-undead.lua',
    'zones/ancient-elven-ruins/npcs.lua', 'general/npcs/bear.lua', 'general/npcs/spider.lua')
MUMB = 'general/npcs/mummy.lua'

REF_DEMONS = RC('demons', ['dolleg', 'kryl-feijan', 'minotaur', 'fire-imp'], 2,
                'Four shipped tokens (the orange-red spiky thorn demon dolleg, the grey smoke-cloud Kryl-Feijan, the tan-and-cream bull-headed minotaur with a labrys, the small orange fire imp): uruivellas is a hulking ash-grey and pale-clay bull-headed demon with ivory horns all over and a tight flame aura, not tan and cream, not orange-red thorny and not small; thaurhereg is a lanky PALE ROSE-PINK demon covered in flowing bright crimson blood rivulets with a crown of horns, not solid orange-red and not grey smoke.')
REF_ORCS = RC('orcs', ['orc-warrior', 'orc-soldier', 'orc-blood-mage', 'orc-necromancer', 'orc-pyromancer', 'orc-cryomancer'], 3,
              'Six shipped orc tokens (olive orc warrior with a scimitar, spiked grey orc soldier, red-robed blood mage with a ruby orb, dark blue-robed necromancer, pyromancer, cryomancer): the orc corruptor is an olive-green orc in tattered PUTRID moss-green and ochre-yellow robes with bone-white shoulder spikes and a short staff with a sickly green-yellow blight glow, not red-robed, not dark blue, not armoured and not fire or ice themed.')
REF_GOLEMS = RC('golems', ['atamathon', 'bone-giant', 'stone-troll', 'minotaur'], 2,
                'Four shipped big-bodied tokens (the grey-white segmented metal giant golem Atamathon, the tan bone giant, the stone troll, the minotaur): the broken golem is a lumpy PALE LIMESTONE-GREY stone figure with a big crack, a missing chunk and a rust-orange exposed seam, slumped, with no glow; the golem is an intact honey-tan clay figure with glowing cyan eyes and cyan rune lines, holding a huge maul, standing square. Neither is white-grey segmented metal and neither is bone.')
REF_HORRORS = RC('horrors', ['bloated-horror', 'weirdling-beast', 'fleshy-experiment', 'sanguine-experiment', 'boney-experiment', 'shadow-stalker', 'dread', 'horned-horror'], 4,
                 'Eight shipped horror and spectre tokens (cream bloated horror, tan-pink weirdling beast, pink fleshy experiment brute, red sanguine blob, tan boney experiment, dark shadow stalker, slate-violet dread wraith with red eyes, horned horror): the necrotic mass is a low lumpy heap of BRUISE-MAUVE and grey-pink rotting flesh with green-yellow pustules and pale bone knobs, not a brute, not red and not cream; the blade horror is a pale grey-blue hooded floating figure with violet eyes inside a whirl of bright steel blades and white wind, not a slate-violet smoke wraith and not red-eyed; the temporal stalker is a slender polished chrome horror with a scythe-crescent head, long claw fingers and cyan glints; the luminous horror is a lanky figure of pure golden-yellow light.')
REF_BEARS = RC('bears', ['brown-bear', 'black-bear', 'cave-bear', 'war-bear'], 2,
               'Four shipped bear tokens (brown bear on all fours, black bear, grey cave bear, rust-orange war bear rearing with a spiked collar): the grizzly bear is a big honey-blond and tawny-gold grizzled bear rearing up on its hind legs with frosted silver-tipped fur, a huge shoulder hump and paws raised, no collar or armour, not brown, not black, not grey and not orange.')
REF_SPIDERS = RC('spiders', ['weaver-hatchling', 'weaver-young', 'weaver-queen', 'fate-weaver', 'giant-spider', 'chitinous-spider'], 3,
                 'Six shipped spider tokens (small blue-white striped weaver hatchling, blue swirl weaver young, cream-and-gold weaver queen, fate weaver, grey giant spider, chitinous spider): the weaver patriarch is a large deep cobalt-sapphire spider with a bright white chevron on the thorax and faint golden time-echo outlines trailing its legs, not cream, not grey and not a small swirl ball.')
REF_MUMMIES = RC('mummies', ['rotting-mummy', 'ancient-elven-mummy', 'greater-mummy-lord', 'ghoul'], 2,
                 'Four shipped undead tokens (tan rotting mummy, ancient elven mummy, armoured greater mummy lord, ghoul): the animated mummy wrappings is NOT a body at all, only an empty S-shaped coil of pale ivory linen bandages floating with violet arcane sparks in its hollow, no face, no limbs.')

DEMPTY = ' no resolvers.equip that touches the body; no sustains_at_birth and no auto_classes on the leaf or base'
EQUIPONLY = ' resolvers.equip fills inventory slots only (no moddable_tile, so no display change)'
TALLB = ' no moddable_tile, shader, anim or add_displays; native sprite 64x128; non-unique'
GRIZD = (' explicit image=npc/grizzly_bear.png on the leaf AND resolvers.nice_tile{image="invis.png", add_mos={{image="npc/grizzly_bear.png", display_h=2, display_y=-1}}} '
         '(keys image/display_h/display_y only): with nicer_tiles on the actor is image=invis.png plus that one add_mos body (native-tall path), with nicer_tiles off it keeps image=npc/grizzly_bear.png (single path); '
         'no moddable_tile, shader, anim or add_displays; native sprite 64x128; non-unique with no define_as, so the catalog entry carries native_tall=true')
CATS = ' Draw the whole creature as ONE compact upright figure filling the disc; never a tall canvas.'

# ---- pack 1: tall major demons ----
asset(1, 'uruivellas', 'uruivellas',
      "valley-moon-caverns and demon-plane pools (general/npcs/major-demon.lua:95, demon/major, non-unique, no define_as, rank 3, base BASE_NPC_MAJOR_DEMON, nice_tile tall body; also the lava_island vault 'U' tile by name); the only definition of this name",
      [src(MAJD, 'name = "uruivellas"'), src(MAJD, 'resolvers.nice_tile', after='name = "uruivellas"'), src(MAJD, 'T_FIRE_STORM', after='name = "uruivellas"'), src(MAJD, 'define_as = "BASE_NPC_MAJOR_DEMON"')],
      src(MAJD, 'define_as = "BASE_NPC_MAJOR_DEMON"'), None, 'demon', 'major', False, True,
      'base BASE_NPC_MAJOR_DEMON (demon/major, no image=, no shader, no sustains_at_birth in the base);' + TALLD % 'demon_major_uruivellas' + '; resolvers.equip battleaxe (inventory only, no moddable_tile); talents Disarm, Rush, Battle Call, weapon talents and Fire Storm (all activated); no sustains_at_birth on the leaf, no auto_classes',
      'demon_major_uruivellas.png',
      [STY, IDN('demon_major_uruivellas.png', 'Native shape (64x128, tall): a hulking dark-brown bull-headed demon with horns all over its body inside a fierce orange fire aura. Keep the hulking bull-headed horned demon wrapped in a tight flame aura, but render the body in mid-light ash-grey and pale clay with glowing lava seams and bright ivory horns, drawn as ONE compact figure filling the disc, no tall canvas.'), REF_DEMONS],
      "An uruivellas seen from a steep overhead three-quarter angle: a HULKING bull-headed demon standing square and facing the lower left, a broad muscular body in pale ASH-GREY and light CLAY-TAN skin in a mid-light value with cream highlight planes and thin glowing molten-orange seams between the muscles, a massive bull skull-like head with two huge curved BRIGHT IVORY horns and rows of short ivory horn spikes along the shoulders, spine and forearms, blazing white-yellow eyes, a thick tight mantle of BRIGHT ORANGE and YELLOW FLAMES wrapping the whole body outline like a burning aura (the flames hug the body and every flame tip stays inside the disc), heavy clenched fists at its sides. Hot, horned, powerful and complete.",
      "Major demons: URUIVELLAS is the HULKING ASH-GREY BULL DEMON in a tight flame aura with ivory horns everywhere (silhouette: a broad square horned brute with flames hugging the body; hue: ash grey and pale clay with orange-yellow flames and ivory; value: mid-light with bright flame accents). The shipped minotaur is a tan-and-cream bull warrior with a labrys and no flames, dolleg an orange-red thorny demon, Kryl-Feijan a grey smoke cloud and the fire imp a small orange imp: this must not be tan and cream, not thorny orange-red, not smoke and not small.",
      "Pale ash-grey and clay-tan skin in a mid-light value with cream highlight planes, thin molten-orange seams, bright ivory horns, orange and yellow flames with a white-yellow core (the fire stays on the demon and must not glow onto, tint or warm the disc); nothing darker than mid ash-brown except thin seams; NO dark brown or black body anywhere." + DISC,
      "READY tall (uruivellas, native_tall)", comp=COMP + FIT + COMPACT + BRIGHT + DARKFIX + CATS)

asset(1, 'thaurhereg', 'thaurhereg',
      "valley-moon-caverns and demon-plane pools (general/npcs/major-demon.lua:128, demon/major, non-unique, no define_as, rank 3, base BASE_NPC_MAJOR_DEMON, nice_tile tall body); the only definition of this name",
      [src(MAJD, 'name = "thaurhereg"'), src(MAJD, 'resolvers.nice_tile', after='name = "thaurhereg"'), src(MAJD, 'T_BONE_SHIELD', after='name = "thaurhereg"'), src(MAJD, 'resolvers.sustains_at_birth()', after='name = "thaurhereg"'), src(MAJD, 'define_as = "BASE_NPC_MAJOR_DEMON"')],
      src(MAJD, 'define_as = "BASE_NPC_MAJOR_DEMON"'), None, 'demon', 'major', False, True,
      'base BASE_NPC_MAJOR_DEMON (demon/major, no image=, no shader, no sustains_at_birth in the base);' + TALLD % 'demon_major_thaurhereg' + '; resolvers.equip staff (inventory only); the leaf calls resolvers.sustains_at_birth() and its Bone Shield talent is a sustain (a bone-shield particle and temporary values only, no type/subtype/image/add_mos write); no auto_classes',
      'demon_major_thaurhereg.png',
      [STY, IDN('demon_major_thaurhereg.png', 'Native shape (64x128, tall): a lanky blood-red demon with a crown of horns, long clawed limbs and swirling blood patterns flowing over its skin. Keep the lanky horn-crowned demon with long clawed arms and flowing blood patterns, but render the skin pale rose-pink with bright crimson blood rivulets, drawn as ONE compact figure filling the disc, no tall canvas.'), REF_DEMONS],
      "A thaurhereg seen from a steep overhead three-quarter angle: a LANKY hunched demon with long thin limbs, a bulbous middle and long clawed hands hanging forward, a crown of five long curved sharp HORNS radiating from the head in pale bone-ivory with crimson tips, a gaunt grinning face with pale glowing eyes, the skin PALE ROSE-PINK and blush in a light value with cream highlight planes, covered all over with swirling ever-changing patterns of BRIGHT CRIMSON BLOOD rivulets flowing across the body and limbs like living veins (a few bright crimson drops falling close to the body), the whole figure leaning towards the lower right. Gaunt, horned, blood-veined and complete.",
      "Major demons: THAURHEREG is the LANKY PALE ROSE-PINK DEMON with a crown of horns and flowing bright crimson blood patterns over the skin (silhouette: a lanky hunched figure with a horn crown and long hanging claws; hue: pale rose-pink and blush with crimson blood lines and ivory horns; value: light with saturated red accents). The shipped dolleg is a solid orange-red thorny brute, the fire imp a small orange imp, Kryl-Feijan a grey smoke cloud and the minotaur tan and cream: this must not be a solid orange-red mass, not thorny, not grey and not tan.",
      "Pale rose-pink and blush skin in a light value with cream highlight planes, bright crimson blood rivulets and drops, ivory horns with crimson tips, pale glowing eyes (nothing glows onto or reddens the disc); nothing darker than deep crimson except thin seams; the disc stays neutral charcoal at reference lightness." + DISC,
      "READY tall (thaurhereg, native_tall)", comp=COMP + FIT + COMPACT + BRIGHT + CATS)

# ---- pack 2: orc corruptor and the two golems ----
asset(2, 'orc-corruptor', 'orc corruptor',
      "rak-shor-pride pool (general/npcs/orc-rak-shor.lua:139, humanoid/orc, non-unique, no define_as, rank 3, base BASE_NPC_ORC_RAK_SHOR, default-name image); the antimagic quest lists it by name; the only definition of this name (the named uniques Brotoq the Reaver, Golbug the Destroyer and Krogar are other names)",
      [src(ORCR, 'name = "orc corruptor"'), src(ORCR, 'T_BONE_SHIELD', after='name = "orc corruptor"'), src(ORCR, 'resolvers.sustains_at_birth()', after='name = "orc corruptor"'), src(ORCR, 'define_as = "BASE_NPC_ORC_RAK_SHOR"')],
      src(ORCR, 'define_as = "BASE_NPC_ORC_RAK_SHOR"'), None, 'humanoid', 'orc', False, False,
      'base BASE_NPC_ORC_RAK_SHOR (humanoid/orc, no image=, no shader, no moddable_tile, no sustains_at_birth in the base);' + DEF + '; resolvers.equip staff, cloth armour and charm (inventory only); the leaf calls resolvers.sustains_at_birth() and its Bone Shield is a sustain (particle and temporary values only); no auto_classes',
      'humanoid_orc_orc_corruptor.png',
      [STY, IDN('humanoid_orc_orc_corruptor.png', 'Native shape (64x64): a green-skinned orc with black spiked shoulder pauldrons in long dark putrid robes. Keep the green orc in long tattered robes with spiked shoulders, but render the robes in mid-light moss-green and ochre with bone-white spikes.'), REF_ORCS],
      "An orc corruptor seen from a steep overhead three-quarter angle: a hunched OLIVE-GREEN tusked orc standing with a slight stoop, wrapped in long tattered PUTRID robes of light MOSS-GREEN and OCHRE-YELLOW in a mid-light value with pale highlight planes and bright bile-yellow stains, big pauldrons on the shoulders bristling with short BONE-WHITE SPIKES, a hood pushed back, a SHORT gnarled staff held close in one hand topped with a small sickly GREEN-YELLOW blight glow, the free hand raised with curling green wisps (short, close to the body), a little rim of pale bone charms on the belt. Rotting, robed, spiked and complete.",
      "Orcs: the ORC CORRUPTOR is the ROBED OLIVE ORC in putrid moss-green and ochre with bone spikes on the shoulders and a blight-glowing staff (silhouette: a hunched robed figure with spiked shoulders and a short staff; hue: olive green skin, moss green and ochre robes, bone white spikes, sickly yellow-green glow; value: mid-light). The shipped orc warrior is a bare olive fighter with a scimitar, the soldier a grey spiked armoured orc, the blood mage red-robed, the necromancer dark blue-robed: this must not be armoured, red, dark blue or bare.",
      "Olive skin and light moss-green and ochre robes in a mid-light value with pale highlight planes and a bright rim light, bone-white spikes, a small sickly green-yellow staff glow (kept on the staff and must not tint or light the disc); nothing darker than deep olive except thin robe seams; NO black robes or black leather anywhere." + DISC,
      "READY single, no define_as (orc corruptor)", comp=COMP + FIT + COMPACT + BRIGHT + DARKFIX)

asset(2, 'broken-golem', 'broken golem',
      "golem-graveyard pool and the collapsed-tower vault (general/npcs/construct.lua:58, construct/golem, non-unique, no define_as, rank 1, base BASE_NPC_CONSTRUCT, default-name image); the only definition of this name",
      [src(CONS, 'name = "broken golem"'), src(CONS, 'T_GOLEM_KNOCKBACK', after='name = "broken golem"'), src(CONS, 'define_as = "BASE_NPC_CONSTRUCT"')],
      src(CONS, 'define_as = "BASE_NPC_CONSTRUCT"'), None, 'construct', 'golem', False, False,
      'base BASE_NPC_CONSTRUCT (construct/golem, no image=, no shader, no sustains_at_birth);' + DEF + '; resolvers.equip greatmaul (inventory only), one rune inscription, talents Weapon Combat, Weapons Mastery and Golem Knockback (activated); no sustains_at_birth, no auto_classes',
      'construct_golem_broken_golem.png',
      [STY, IDN('construct_golem_broken_golem.png', 'Native shape (64x64): a dark grey-brown lumpy stone golem, one arm a stump, cracked and crumbling, standing hunched. Keep the crumbling hunched golem with the damaged arm, but render the stone in mid-light pale limestone-grey with bright cracks and a rust-orange exposed seam.'), REF_GOLEMS],
      "A broken golem seen from a steep overhead three-quarter angle: a slumped hulking golem of blocky PALE LIMESTONE-GREY and cool light grey stone in a mid-light value with cream highlight planes on every upper-left face, deep zig-zag CRACKS, a big missing chunk in the chest and the LEFT FOREARM BROKEN OFF into a jagged stump with a few pale rubble pieces on the disc close to its feet, a RUST-ORANGE exposed iron seam and rivets in the chest crack, tufts of pale green moss on the shoulders, a blank dark eye socket with no glow, the right arm hanging heavy. Damaged, slumped, crumbling and complete.",
      "Golems: the BROKEN GOLEM is the SLUMPED PALE LIMESTONE-GREY STONE FIGURE with a cracked chest, a broken-off forearm and a rust-orange seam, no glow (silhouette: a hunched blocky figure missing one forearm with rubble at its feet; hue: pale limestone grey with rust orange and moss green; value: mid-light). Atamathon is a white-grey segmented metal giant and the bone giants are tan: this must not be metal, not tan and not skeletal; and it must differ from the intact glowing-eyed honey-tan golem of this batch.",
      "Pale limestone-grey stone in a mid-light value with cream highlight planes and a bright rim light, rust-orange seam, pale green moss, no glow anywhere; nothing darker than mid grey except the crack seams and the blank eye socket; NO dark brown or black stone." + DISC,
      "READY single, no define_as (broken golem)", comp=COMP + FIT + COMPACT + BRIGHT + DARKFIX)

asset(2, 'golem', 'golem',
      "golem-graveyard pool (general/npcs/construct.lua:75, construct/golem, non-unique, no define_as, rank 1, base BASE_NPC_CONSTRUCT, default-name image); the only NPC leaf with this name. The player's alchemist golem (talents/spells/golemancy.lua:30) is also named golem with the same type and subtype but uses image=npc/alchemist_golem.png plus a moddable_tile paper doll, so the matcher rejects it (image and moddable-tile checks) and it stays native",
      [src(CONS, 'name = "golem"'), src(CONS, 'T_GOLEM_BEAM', after='name = "golem"'), src(CONS, 'define_as = "BASE_NPC_CONSTRUCT"'), src('talents/spells/golemancy.lua', 'name = "golem"'), src('talents/spells/golemancy.lua', 'image = "npc/alchemist_golem.png"'), src('talents/spells/golemancy.lua', 'moddable_tile = "runic_golem"')],
      src(CONS, 'define_as = "BASE_NPC_CONSTRUCT"'), None, 'construct', 'golem', False, False,
      'base BASE_NPC_CONSTRUCT (construct/golem, no image=, no shader, no sustains_at_birth);' + DEF + '; resolvers.equip greatmaul (inventory only), two rune inscriptions, talents Weapon Combat, Weapons Mastery, Golem Knockback and Golem Beam (activated); no sustains_at_birth, no auto_classes; the alchemist golem of the player has the same name, type and subtype but image npc/alchemist_golem.png and a moddable_tile, both of which the matcher refuses',
      'construct_golem_golem.png',
      [STY, IDN('construct_golem_golem.png', 'Native shape (64x64): a sturdy tan clay-and-stone golem standing square with glowing cyan eyes. Keep the sturdy square golem with glowing cyan eyes, but render the body in bright honey-tan clay with cyan rune lines and a huge maul.'), REF_GOLEMS],
      "A golem seen from a steep overhead three-quarter angle: a sturdy intact blocky golem standing square, its body sculpted from bright HONEY-TAN and warm terracotta clay in a light-mid value with cream highlight planes, glowing CYAN EYES and thin glowing cyan RUNE LINES along the chest and arms, thick rounded limbs with pale stone knuckles, a HUGE grey-steel MAUL held low across the body in both hands (the maul head inside the disc), simple stitched clay seams. Solid, intact, rune-lit and complete.",
      "Golems: the GOLEM is the INTACT HONEY-TAN CLAY FIGURE with glowing cyan eyes and rune lines and a big maul (silhouette: a square blocky figure holding a huge maul across the body; hue: honey tan and terracotta with cyan; value: light-mid). The broken golem of this batch is pale grey, cracked and armless below the elbow, Atamathon is a white-grey metal giant and the bone giants are skeletal: this must not be grey, not cracked, not metal and not bone.",
      "Honey-tan and terracotta clay in a light-mid value with cream highlight planes and a bright rim light, glowing cyan eyes and rune lines, grey-steel maul (the cyan glow stays on the golem and must not tint or light the disc); nothing darker than deep terracotta except the seams; the disc stays neutral charcoal at reference lightness." + DISC,
      "READY single, no define_as (golem)", comp=COMP + FIT + COMPACT + BRIGHT)

# ---- pack 3: horrors ----
asset(3, 'temporal-stalker', 'temporal stalker',
      "temporal-rift and ardhungol pools (general/npcs/horror_temporal.lua:129, horror/temporal, non-unique, no define_as, rank 2, base BASE_NPC_HORROR_TEMPORAL, nice_tile tall body); the only definition of this name",
      [src(TEMP, 'name = "temporal stalker"'), src(TEMP, 'npc/horror_temporal_temporal_stalker.png'), src(TEMP, 'T_STEALTH', after='name = "temporal stalker"'), src(TEMP, 'resolvers.sustains_at_birth()', after='name = "temporal stalker"'), src(TEMP, 'define_as = "BASE_NPC_HORROR_TEMPORAL"')],
      src(TEMP, 'define_as = "BASE_NPC_HORROR_TEMPORAL"'), None, 'horror', 'temporal', False, True,
      'base BASE_NPC_HORROR_TEMPORAL (horror/temporal, no image=, no shader, no sustains_at_birth in the base);' + TALLD % 'horror_temporal_temporal_stalker' + '; the leaf calls resolvers.sustains_at_birth() and its Stealth is a sustain (stealth temporary values only; Fateweaver and Spin Fate are temporal values only); two inscriptions; no equip, no auto_classes',
      'horror_temporal_temporal_stalker.png',
      [STY, IDN('horror_temporal_temporal_stalker.png', 'Native shape (64x128, tall): a slender polished-steel monstrosity with a scythe-like crescent head, long blade claws in place of fingers and razor teeth. Keep the slender chrome horror with the crescent head and claw fingers, bright polished steel with cyan glints, drawn as ONE compact figure filling the disc, no tall canvas.'), REF_HORRORS],
      "A temporal stalker seen from a steep overhead three-quarter angle: a SLENDER gaunt hunched horror of bright POLISHED CHROME and steel-silver metal in a light value with white specular highlights, a head shaped like a big curved SCYTHE-CRESCENT blade, a narrow torso, long thin legs, and very long thin arms ending in bundles of long curved BLADE-CLAW fingers hanging forward and outward (the claw tips inside the disc), a rim of small bright CYAN time-glints and a few pale cyan clock-hand shards floating close to the body, a thin gap of dark grey seams between the plates. Metallic, slender, claw-fingered and complete.",
      "Horrors: the TEMPORAL STALKER is the SLENDER POLISHED CHROME HORROR with a scythe-crescent head and long blade-claw fingers (silhouette: a thin hunched figure with a big crescent head and long hanging claws; hue: chrome silver with cyan glints; value: light). The shadow stalker is a dark smoke cat-shape, Atamathon a white-grey bulky metal giant, the dredge pink flesh: this must not be dark, not bulky, not fleshy and not smoke.",
      "Polished chrome and steel-silver in a light value with white specular highlights and a bright rim light, cyan glints and pale cyan shards (the glints stay on the creature and must not tint or light the disc); nothing darker than mid steel-grey except thin plate seams; NO black metal.",
      "READY tall (temporal stalker, native_tall)", comp=COMP + FIT + COMPACT + BRIGHT + CATS)

asset(3, 'blade-horror', 'blade horror',
      "lake-nur, ardhungol, dreadfell and more pools plus the living-weapons vault 'b' tile (general/npcs/horror.lua:514, horror/eldritch, non-unique, define_as BLADEHORROR, rank 2, base BASE_NPC_HORROR, nice_tile tall body); the only definition of this name (the unique Ak'Gishil is another name with resolvers.nice_tile{tall=1} and stays native)",
      [src(HORR, 'name = "blade horror"'), src(HORR, 'resolvers.nice_tile', after='name = "blade horror"'), src(HORR, 'define_as="BLADEHORROR"', after='name = "blade horror"'), src(HORR, 'define_as = "BASE_NPC_HORROR"')],
      src(HORR, 'define_as = "BASE_NPC_HORROR"'), 'BLADEHORROR', 'horror', 'eldritch', False, True,
      'base BASE_NPC_HORROR (horror/eldritch, no image=, no shader, no sustains_at_birth in the base);' + TALLD % 'horror_eldritch_blade_horror' + '; the leaf binds define_as BLADEHORROR (so the catalog entry binds it too, native_tall=true); levitate; the leaf calls resolvers.sustains_at_birth() and Kinetic Aura and Kinetic Shield are sustains (temporary values only, no type/subtype/image/add_mos/shader write); Knife Storm, Implode, Razor Knife, Psionic Pull and Kinetic Leech are activated; no equip, no auto_classes',
      'horror_eldritch_blade_horror.png',
      [STY, IDN('horror_eldritch_blade_horror.png', 'Native shape (64x128, tall): a black hooded floating figure with glowing violet eyes inside a whirl of countless telekinetic blades and pale wind. Keep the hooded floating figure inside a whirling ring of blades, but render the figure in pale slate-blue and white with a bright steel blade ring, drawn as ONE compact figure filling the disc, no tall canvas.'), REF_HORRORS],
      "A blade horror seen from a steep overhead three-quarter angle: a thin FLOATING hooded figure in the centre of the disc, its ragged cloak of PALE GREY-BLUE and near-white mist in a light-mid value with bright silver highlight planes, a hooded face with two glowing VIOLET-WHITE eyes, thin hands raised, surrounded by a tight SPIRAL RING of six to eight BRIGHT POLISHED STEEL SWORDS AND DAGGERS orbiting the body in mid-air (all blades short, angled tangent to the ring, every blade tip inside the disc) and curling swirls of white wind between them. Floating, blade-ringed, pale and complete.",
      "Horrors: the BLADE HORROR is the PALE GREY-BLUE HOODED FLOATER inside a spiral ring of bright steel blades and white wind with violet-white eyes (silhouette: a small central figure inside a round blade wheel; hue: pale grey-blue and white with steel and violet-white eyes; value: light-mid). The dread is a slate-violet smoke wraith with RED eyes and a red chest core, the shadow stalker dark smoke: this must not be a violet smoke wraith, not red-eyed and not black.",
      "Pale grey-blue and near-white mist in a light-mid value with silver highlight planes and a bright rim light, bright polished steel blades with white edge highlights, violet-white eyes (nothing glows onto or tints the disc); nothing darker than mid slate-grey except the eye sockets and thin seams; NO black cloak or black body anywhere." + DISC,
      "READY tall (blade horror, native_tall, define_as BLADEHORROR)", comp=COMP + FIT + COMPACT + BRIGHT + DARKFIX + CATS)

asset(3, 'luminous-horror', 'luminous horror',
      "lake-nur, ardhungol, dreadfell and more pools, escorted by other horrors (general/npcs/horror.lua:408, horror/eldritch, non-unique, no define_as, rank 1, base BASE_NPC_HORROR, default-name image); the only definition of this name",
      [src(HORR, 'name = "luminous horror"'), src(HORR, 'T_CHANT_OF_FORTITUDE', after='name = "luminous horror"'), src(HORR, 'resolvers.sustains_at_birth()', after='name = "luminous horror"'), src(HORR, 'define_as = "BASE_NPC_HORROR"')],
      src(HORR, 'define_as = "BASE_NPC_HORROR"'), None, 'horror', 'eldritch', False, False,
      'base BASE_NPC_HORROR (horror/eldritch, no image=, no shader, no sustains_at_birth in the base);' + DEF + '; lite=3; the leaf calls resolvers.sustains_at_birth() and Chant of Fortitude and Providence are sustains (temporary values and particles only, no type/subtype/image/add_mos/shader write); no equip, no auto_classes',
      'horror_eldritch_luminous_horror.png',
      [STY, IDN('horror_eldritch_luminous_horror.png', 'Native shape (64x64): a lanky humanoid outline made of glowing yellow light, hollow inside. Keep the lanky glowing yellow humanoid of light, but render it as a solid bright golden-yellow figure with a white-hot core.'), REF_HORRORS],
      "A luminous horror seen from a steep overhead three-quarter angle: a LANKY humanoid figure with long thin limbs and a small head, its body made of solid BRIGHT GOLDEN-YELLOW LIGHT in a light value with a WHITE-HOT glowing core in the chest, pale lemon highlight planes and a brilliant white-gold rim along the outline, thin darker AMBER contour lines where the limbs cross the body so the figure reads as a solid shape, long arms hanging forward with spread glowing fingers, a few tiny lemon light motes drifting close to the body (all inside the disc). Radiant, lanky, luminous and complete.",
      "Horrors: the LUMINOUS HORROR is the LANKY GOLDEN-YELLOW LIGHT FIGURE with a white-hot core (silhouette: a tall thin humanoid with long arms and a small head; hue: golden yellow, lemon and white-gold with amber contours; value: very light). Every shipped horror is flesh, smoke or tentacles in pink, cream, red or violet: this must not be flesh, not smoke, not tentacled and not pink.",
      "Golden-yellow, lemon and white-gold light in a light value with amber contour lines (the light stays on the figure and must not glow onto, brighten or yellow the disc); nothing darker than deep amber except thin contour lines; the disc stays neutral charcoal at reference lightness." + DISC,
      "READY single, no define_as (luminous horror)", comp=COMP + FIT + COMPACT + BRIGHT)

asset(3, 'necrotic-mass', 'necrotic mass',
      "rak-shor-pride pool (general/npcs/horror-undead.lua:46, undead/horror, non-unique, no define_as, rank 1, base BASE_NPC_HORROR_UNDEAD, nice_tile tall body, never_move); the only definition of this name",
      [src(HORU, 'name = "necrotic mass"'), src(HORU, 'resolvers.nice_tile', after='name = "necrotic mass"'), src(HORU, 'never_move', after='name = "necrotic mass"'), src(HORU, 'define_as = "BASE_NPC_HORROR_UNDEAD"')],
      src(HORU, 'define_as = "BASE_NPC_HORROR_UNDEAD"'), None, 'undead', 'horror', False, True,
      'base BASE_NPC_HORROR_UNDEAD (undead/horror, no image=, no shader, no sustains_at_birth in the base);' + TALLD % 'undead_horror_necrotic_mass' + '; never_move, no talents, no sustains_at_birth on the leaf, no equip, no auto_classes',
      'undead_horror_necrotic_mass.png',
      [STY, IDN('undead_horror_necrotic_mass.png', 'Native shape (64x128 canvas, a low lump at the bottom): a shapeless mound of rotting pink-grey flesh with dark pits and pale flecks. Keep the shapeless quivering heap of rotting flesh, but render it in bruise-mauve and grey-pink with green-yellow pustules and pale bone knobs, a low wide heap filling the disc, no tall canvas.'), REF_HORRORS],
      "A necrotic mass seen from a steep overhead three-quarter angle: a low wide quivering HEAP of putrefying flesh filling the middle of the disc, the surface a lumpy mix of BRUISE-MAUVE, dusty PINK-GREY and pale mottled flesh in a light-mid value with cream wet highlights on every upper-left bulge, clusters of sickly GREEN-YELLOW PUSTULES and blisters, a few pale BONE KNOBS and rib tips pushing out of the mass, dark maroon pits and splits in the flesh, a few thick strings of green-yellow ooze dripping down its sides (short, close to the body), no face, no limbs, no eyes. Putrid, shapeless, lumpy and complete.",
      "Horrors: the NECROTIC MASS is the LOW LUMPY HEAP OF BRUISE-MAUVE AND GREY-PINK ROTTING FLESH with green-yellow pustules and pale bone knobs, no limbs and no face (silhouette: a wide lumpy mound; hue: mauve, grey-pink, green-yellow and bone; value: light-mid). The shipped fleshy experiment is a pink muscled brute, the sanguine experiment a red blob, the bloated horror cream and the boney experiment a tan bone pile: this must not be a brute, not solid red, not cream and not just bones.",
      "Bruise-mauve, dusty pink-grey and pale flesh in a light-mid value with cream wet highlights, green-yellow pustules, pale bone knobs and dark maroon pits (nothing glows onto or darkens the disc); nothing darker than deep maroon except thin splits; NO black anywhere." + DISC,
      "READY tall (necrotic mass, native_tall)", comp=COMP + FIT + COMPACT + BRIGHT + CATS)

# ---- pack 4: mummy wrappings, grizzly bear, weaver patriarch ----
asset(4, 'animated-mummy-wrappings', 'animated mummy wrappings',
      "ancient-elven-ruins zone pool (zones/ancient-elven-ruins/npcs.lua:130, undead/mummy, non-unique, no define_as, rank 1, base BASE_NPC_MUMMY, explicit image=object/mummy_wrappings.png with display '['); the only definition of this name",
      [src(MUMZ, 'name = "animated mummy wrappings"'), src(MUMZ, 'image="object/mummy_wrappings.png"', after='name = "animated mummy wrappings"'), src(MUMZ, 'never_move', after='name = "animated mummy wrappings"'), src(MUMB, 'define_as = "BASE_NPC_MUMMY"')],
      src(MUMB, 'define_as = "BASE_NPC_MUMMY"'), None, 'undead', 'mummy', False, False,
      'base BASE_NPC_MUMMY (undead/mummy, no image=, no shader, no sustains_at_birth);' + EXPL + '; the PNG lives under gfx/shockbolt/object/ (image=object/mummy_wrappings.png), never_move, caster talents Manathrust, Freeze, Lightning and Strike (activated); resolvers.equip armour of subtype mummy (inventory only); no sustains_at_birth, no auto_classes',
      'object/mummy_wrappings.png',
      [STY, ('identity', D + 'gfx/shockbolt/object/mummy_wrappings.png', 'Native shape (64x64; the leaf itself names object/mummy_wrappings.png, so the token image is the object PNG, not the default-name npc PNG): an empty S-shaped coil of pale linen mummy wrappings with frayed ends, floating. Keep the empty S-shaped coil of bandages with no body, in bright ivory linen with violet arcane sparks in the hollow.'), REF_MUMMIES],
      "An animated mummy wrappings seen from a steep overhead three-quarter angle: an EMPTY floating S-SHAPED COIL of thick aged linen bandages, no body inside, the cloth bright IVORY and CREAM with warm tan grime stains and pale highlight planes in a light value, the two ends flaring and fraying into loose short ribbons, a few loose bandage turns wound round the middle, the hollow inside the coil showing a faint glowing VIOLET-LILAC arcane light with a few small violet and cyan spark motes hovering in it (kept inside the coil), no face, no eyes, no limbs. Floating, coiled, hollow and complete.",
      "Mummies: the ANIMATED MUMMY WRAPPINGS is an EMPTY S-SHAPED COIL OF IVORY LINEN with violet arcane sparks in its hollow, no body (silhouette: a wide S-curve ribbon with frayed ends; hue: ivory and cream with violet and cyan sparks; value: light). The shipped rotting mummy, ancient elven mummy and greater mummy lord are tan humanoid bodies in wrappings: this must not have a body, a head or limbs.",
      "Ivory and cream linen in a light value with warm tan grime and pale highlight planes, faint violet arcane light and violet and cyan spark motes (the light stays inside the coil and must not tint or light the disc); nothing darker than mid tan stains except thin fold seams; NO black anywhere." + DISC,
      "READY single, no define_as (animated mummy wrappings)", comp=COMP + FIT + COMPACT + BRIGHT)

asset(4, 'grizzly-bear', 'grizzly bear',
      "old-forest and noxious-caldera pools and the honey_glade vault (general/npcs/bear.lua:94, animal/bear, non-unique, no define_as, rank 1, base BASE_NPC_BEAR, explicit image=npc/grizzly_bear.png plus nice_tile tall body); the only definition of this name (the uniques Norgos are other names)",
      [src(BEAR, 'name = "grizzly bear"'), src(BEAR, 'image = "npc/grizzly_bear.png"', after='name = "grizzly bear"'), src(BEAR, 'resolvers.nice_tile', after='name = "grizzly bear"'), src(BEAR, 'define_as = "BASE_NPC_BEAR"')],
      src(BEAR, 'define_as = "BASE_NPC_BEAR"'), None, 'animal', 'bear', False, True,
      'base BASE_NPC_BEAR (animal/bear, no image=, no shader, no sustains_at_birth);' + GRIZD + '; Stamina Pool, Stun, Knockback and Disarm (activated); no equip, no sustains_at_birth, no auto_classes; heart-gloom renames non-unique bears with a gloomy/deformed/sick prefix, which the existing heartGloomBase path already maps for animal/bear entries',
      'grizzly_bear.png',
      [STY, IDN('grizzly_bear.png', 'Native shape (64x128, tall): a big dark-brown bear rearing on its hind legs with both forepaws raised and its mouth open. Keep the huge bear rearing up on its hind legs with raised paws, but render the fur in mid-light honey-blond and tawny gold with frosted silver tips, drawn as ONE compact figure filling the disc, no tall canvas.'), REF_BEARS],
      "A grizzly bear seen from a steep overhead three-quarter angle: a huge bear REARING UP on its hind legs facing the lower left, both forepaws raised with long pale claws, the mouth wide open with pale teeth and a pink tongue, thick shaggy fur in HONEY-BLOND and TAWNY GOLD in a mid-light value with FROSTED SILVER-CREAM TIPS on the guard hairs (the grizzled look), a big muscular SHOULDER HUMP, warm umber-brown only on the lower legs and paws (no darker than mid umber), small dark eyes, a bright pale rim light along the whole fur outline, no collar, no armour. Huge, grizzled, rearing and complete.",
      "Bears: the GRIZZLY BEAR is the HONEY-BLOND AND TAWNY-GOLD GRIZZLED BEAR REARING UP with frosted silver fur tips and a shoulder hump (silhouette: an upright bear with raised paws and a hump; hue: honey blond, tawny gold and silver cream with umber paws; value: mid-light). The shipped brown bear is a brown bear on all fours, the black bear black, the cave bear grey and the war bear rust-orange with a spiked collar: this must not be plain brown, black, grey or rust-orange and must not wear a collar.",
      "Honey-blond and tawny-gold fur in a mid-light value with silver-cream frosted tips and pale highlight planes and a bright rim light, umber only on the lower legs, pale claws and teeth (nothing glows onto the disc); nothing darker than mid umber except the eyes and nostrils; NO dark brown or black fur." + DISC,
      "READY tall (grizzly bear, native_tall)", comp=COMP + FIT + COMPACT + BRIGHT + DARKFIX + CATS)

asset(4, 'weaver-patriarch', 'weaver patriarch',
      "ardhungol pool and the weaver matriarch's escort (general/npcs/spider.lua:266, spiderkin/spider, non-unique, no define_as, rank 2, base BASE_NPC_SPIDER, default-name image); the only definition of this name (the uniques Ungole and Ninandra are other names)",
      [src(SPID, 'name = "weaver patriarch"'), src(SPID, 'T_SPIN_FATE', after='name = "weaver patriarch"'), src(SPID, 'resolvers.sustains_at_birth()', after='define_as = "BASE_NPC_SPIDER"'), src(SPID, 'define_as = "BASE_NPC_SPIDER"')],
      src(SPID, 'define_as = "BASE_NPC_SPIDER"'), None, 'spiderkin', 'spider', False, False,
      'base BASE_NPC_SPIDER (spiderkin/spider, no image=, no shader);' + DEF + '; the base resolvers.sustains_at_birth() starts Spin Fate (a sustain: temporary values only, no type/subtype/image/add_mos/shader write); two base infusion inscriptions (an invisibility infusion would apply a shader-based effect only while active, and the matcher rejects it then); Spider Web, Lay Web, Swap, Rethread and Static History are activated; no equip, no auto_classes',
      'spiderkin_spider_weaver_patriarch.png',
      [STY, IDN('spiderkin_spider_weaver_patriarch.png', 'Native shape (64x64): a big icy-blue armoured spider with white markings on the thorax and glowing white orbs at its leg joints. Keep the large blue spider with white thorax markings and glowing leg-joint orbs, but render it in bright cobalt-sapphire with a bright white chevron and faint golden time-echo outlines.'), REF_SPIDERS],
      "A weaver patriarch seen from a steep overhead three-quarter angle: a LARGE armoured spider facing the lower left, a glossy deep COBALT-SAPPHIRE and bright AZURE-BLUE carapace in a mid-light value with pale ice-blue highlight planes, a bold bright WHITE CHEVRON MARKING on the thorax and white spots on the abdomen, eight strong jointed legs with small glowing white-cyan orbs at the joints (all leg tips inside the disc), curved fangs and several pale-cyan eyes, and faint GOLDEN TIME-ECHO OUTLINES trailing a little behind each leg tip like a shimmer, a bright pale rim light along the carapace. Armoured, shimmering, white-marked and complete.",
      "Spiders: the WEAVER PATRIARCH is the LARGE COBALT-SAPPHIRE SPIDER with a bold white chevron on the thorax, glowing joint orbs and golden time-echo shimmer (silhouette: a large eight-legged spider with a thick thorax; hue: cobalt sapphire and azure with white and gold-shimmer accents; value: mid-light). The shipped weaver hatchling and young are small blue-white swirl ball spiders, the weaver queen cream and gold, the giant spider grey: this must not be a small swirl ball, not cream and gold and not grey.",
      "Deep cobalt-sapphire and azure carapace in a mid-light value with pale ice-blue highlight planes and a bright rim light, bright white chevron and spots, white-cyan joint orbs and faint golden echo lines (the glow stays on the spider and must not tint or light the disc); nothing darker than deep cobalt except thin seams; NO black chitin." + DISC,
      "READY single, no define_as (weaver patriarch)", comp=COMP + FIT + COMPACT + BRIGHT)


def retry(id_, pack, **changes):
    base = next(a for a in A if a['id'] == id_)
    A.append(dict(base, pack=pack, **changes))


exec((HERE / 'retries.py').read_text()) if (HERE / 'retries.py').exists() else None

EXPL_IDS = ('animated-mummy-wrappings', 'grizzly-bear')
TALL_IDS = tuple(a['id'] for a in A if a['native_tall'])
PNGF = {a['id']: 'NPC.lua:33 default-name image on the leaf (no image=/nice_tile)' for a in A}
PNGF.update({'animated-mummy-wrappings': 'explicit image=object/mummy_wrappings.png on the leaf (no nice_tile/add_mos)'})
PNGF.update({i: 'NPC.lua:33 default-name image on the leaf plus an explicit nice_tile tall body (image=invis.png, one add_mos entry with display_h=2, display_y=-1 naming the same PNG)' for i in TALL_IDS})
PNGF['grizzly-bear'] = 'explicit image=npc/grizzly_bear.png on the leaf plus an explicit nice_tile tall body (image=invis.png, one add_mos entry with display_h=2, display_y=-1 naming the same PNG; with nicer_tiles off the leaf keeps the single image)'
EVDIR = 'evidence/monster-batch-y-20260930/source-contracts.json'


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
        native_rel = (D + 'gfx/shockbolt/' + a['native']) if a['native'].startswith('object/') else NPC + a['native']
        native_image = a['native'] if a['native'].startswith('object/') else 'npc/' + a['native']
        ident = {'id': a['id'], 'native_name': a['name'], 'source': a['srcs'][0], 'define_as': a['define_as'],
                 'type': a['type'], 'subtype': a['subtype'], 'unique': a['unique'], 'native_tall': a['native_tall'],
                 'image_source': PNGF[a['id']],
                 'structure': a['structure'], 'native_image': native_image, 'native_image_path': native_rel,
                 'native_image_sha256': sha(native_rel), 'native_image_size': None, 'verdict': a['verdict']}
        with Image.open(WS / native_rel) as im:
            ident['native_image_size'] = list(im.size)
        if a['native_tall']:
            ident['tall_body'] = {'image': 'invis.png', 'add_mos': [{'image': native_image, 'display_h': 2, 'display_y': -1}],
                                  'catalog_flag': 'native_tall=true', 'static_pin': 'nice_tile names the tall PNG explicitly; not unique, so no unique-only tall path applies'}
        if a['base']:
            ident['base_source'] = a['base']
        if len(a['srcs']) > 1:
            ident['extra_sources'] = a['srcs'][1:]
        identities.append(ident)
    findings = [
        "All twelve names have exactly one NPC leaf definition. The zone pools, the vaults (lava_island for uruivellas, collapsed-tower for the broken golem, living-weapons for the blade horror, honey_glade for the grizzly bear), the antimagic quest (orc corruptor), the weaver matriarch's escort and the horror escorts only build those same leaves through name/random_filter lookups, so they are the very same actors; a random boss made from a flat entry goes through the existing captureRandomOrigin path, a random boss made from a non-unique native-tall entry stays native (only unique tall bodies qualify).",
        "Golem: the player's alchemist golem (talents/spells/golemancy.lua:30) is also named golem with type construct and subtype golem, but its image is npc/alchemist_golem.png and it carries a moddable_tile paper doll, so appearance() rejects it twice over (image mismatch, moddable-tile); it stays native. The atamathon, alchemist golem and every other construct keep their own names.",
        "Blade horror: the leaf binds define_as BLADEHORROR and the catalog entry binds it too; the temporal Ak'Gishil (a unique blade-horror variant, resolvers.nice_tile{tall=1}) has another name and stays native; the Animated Sword constructs are other names.",
        "Grizzly bear: heart-gloom renames non-unique bears with a gloomy/deformed/sick prefix; the existing heartGloomBase path (animal/bear is a covered family) resolves such a renamed body to the grizzly entry and the ordinary appearance contract (single or native-tall) still applies; no change to that code.",
        "No summon, clone, event or talent builds an actor with any of the twelve names using a different native PNG (grep of every actor definition, static map, quest script, vault, encounter, event and talent under game/modules/tome for the names and PNGs), except the player's alchemist golem described above (which fails the matcher).",
        "Neighbours that reuse a name or subtype but stay native: 'alchemist golem', 'Atamathon the Giant Golem' (own token), 'Ak'Gishil', 'greater/ultimate teluvorta', 'weaver matriarch', 'Ungole', 'Ninandra the Great Weaver', 'Norgos the Guardian/Frozen' (own tokens), 'polar bear', the other rak-shor orcs, 'necrotic abomination', 'black mamba' (tied at 2.7 with the last three, lost on survey-document order).",
        "Result: no per-construct `variants` entry and no `image_aliases` entry is needed for this batch.",
    ]
    ev = {'schema': 1,
          'task': "monster-batch-y: static re-verification (no game launch) of the twelve identities that follow batch X in the survey-2 unscheduled list (uruivellas, thaurhereg, orc corruptor, temporal stalker, broken golem, golem, blade horror, animated mummy wrappings, grizzly bear, weaver patriarch, luminous horror, necrotic mass) against game/modules/tome source and native sprites. Every field below was read from source: name, type/subtype, define_as (only the blade horror binds one, BLADEHORROR), explicit or NPC.lua:33 default image, unique, PNG on disk, and absence of moddable_tile/shader/anim/add_displays on each leaf and its base. Findings: six identities are non-unique native-tall bodies (uruivellas, thaurhereg, temporal stalker, blade horror, grizzly bear, necrotic mass: nice_tile image=invis.png with one explicit add_mos display_h=2, display_y=-1) with native_tall=true; six are 64x64 single images (the orc corruptor, both golems, the luminous horror and the weaver patriarch use the NPC.lua:33 default-name image; the animated mummy wrappings names object/mummy_wrappings.png with image=).",
          'new_ids_not_in_catalog_before_this_batch': [i['id'] for i in identities], 'identities': identities,
          'runtime_mutation_scan': {
              'method': "every talent of each identity (resolvers.talents, inherited base talents and the base-file talent lists) was resolved under game/modules/tome/data/talents and its mode read (sustained/activated/passive); the same talents/, timed_effects/, birth/ and class/ greps for writes to type/subtype/image/add_mos/add_displays/moddable_tile/replace_display/shader as batches S to X were applied and give the same writer set; the resolvers sustains_at_birth, inscriptions, equip and nice_tile and the base-file resolvers were read; every auto_classes site under zones/, general/ and maps/ was listed with its leaf name.",
              'writers_found': [
                  {'file': 'game/modules/tome/data/talents/corruptions/shadowflame.lua', 'line': 97, 'talent': "Flame of Urh'Rok", 'effect': 'sustain: __old_type={type,subtype}; type,subtype = demon,major; image untouched; restored on deactivate'},
                  {'file': 'game/modules/tome/data/talents/psionic/thought-forms.lua', 'line': 93, 'talent': 'thought-form summons (Solipsist tree)', 'effect': 'sets type/subtype/image/moddable_tile/add_mos on the summoned minion copied from its summoner, never on the caster'},
                  {'file': 'game/modules/tome/data/talents/chronomancy/anomalies.lua', 'line': 587, 'talent': 'anomaly summons', 'effect': 'creates a separate spawned NPC with another image; not the caster'}],
              'other_hits_reviewed': [
                  'talents/spells/golemancy.lua:30 (the alchemist golem constructor: same name/type/subtype as the golem leaf but image npc/alchemist_golem.png and moddable_tile; rejected by the matcher)',
                  'timed_effects/physical.lua and other.lua (add_displays/replace_display only while the effect is active)', 'timed_effects/magical.lua (invisibility and shadow-simulacrum shaders and similar, only while active)'],
              'timed_effects_review': "timed_effects write shader, replace_display, add_displays or image only while active (invisibility shaders, stone/ice/pin displays, Wrathroot, Shivgoroth form, dragon egg, Lord of Skulls): the matcher rejects them (native art shows) and restores the token when they end.",
              'sustains_at_birth_review': [
                  {'identity': 'thaurhereg, orc corruptor', 'sustained': ['Bone Shield'], 'note': 'the leaf calls resolvers.sustains_at_birth(); a bone-shield particle and temporary values only, no type/subtype/image/add_mos write'},
                  {'identity': 'temporal stalker', 'sustained': ['Stealth'], 'note': 'stealth temporary values only'},
                  {'identity': 'blade horror', 'sustained': ['Kinetic Aura', 'Kinetic Shield'], 'note': 'temporary values and particles only, no display field written (projection.lua:140, absorption.lua:137 read)'},
                  {'identity': 'luminous horror', 'sustained': ['Chant of Fortitude', 'Providence'], 'note': 'temporary values only (chants.lua:25, light.lua:121 read)'},
                  {'identity': 'weaver patriarch', 'sustained': ['Spin Fate'], 'note': 'the base BASE_NPC_SPIDER resolvers.sustains_at_birth() starts Spin Fate; temporary values only'},
                  {'identity': 'uruivellas, broken golem, golem, animated mummy wrappings, grizzly bear, necrotic mass', 'sustained': [], 'note': 'no sustains_at_birth on the leaf or base'}],
              'auto_classes_review': [
                  {'identity': 'all twelve', 'class': 'none', 'finding': "none of the twelve leaves or their bases has auto_classes; every auto_classes site in zones/, general/ and maps/ belongs to another leaf, so none can reach Flame of Urh'Rok (uruivellas and thaurhereg are demon/major but never learn it) and there is no urh_rok_form opt-in."}],
              'visibility_review': 'Identities with inscriptions (orc corruptor, weaver patriarch, broken golem, golem, temporal stalker) can roll an invisibility rune/infusion that applies a shader effect while it lasts; the matcher rejects an actor with a shader (native art shows) and the token returns when it ends. The temporal stalker has Stealth; token drawing follows actor visibility as for every other token.',
              'hits_in_batch': [],
              'no_hit': [i['native_name'] for i in identities]},
          'summons_and_same_body_copies': {
              'method': "grep of every actor definition, static map, quest script, vault, encounter, event and talent under game/modules/tome (data and class) for the twelve names and PNGs; talents that build summons/copies (summon-*, dreadmaster, master-of-flesh, master-of-bones, rot, thought-forms, simulacra/mirror images, Grand Arrival, golemancy, cloneFull users) checked for copies of these bodies.",
              'findings': findings},
          'name_collisions_checked': [
              {'name': a['name'], 'other_definitions': ['none'], 'outcome': ('single actor definition bound to define_as ' + a['define_as'] if a['define_as'] else 'single actor definition without define_as; the catalog entry has no define_as and matches by exact name, type and subtype')} for a in {x['id']: x for x in A}.values() if a['id'] != 'golem'] + [
              {'name': 'golem', 'other_definitions': ["the player's alchemist golem talents/spells/golemancy.lua:30 (same name, type, subtype; image npc/alchemist_golem.png and moddable_tile)"], 'outcome': 'the NPC leaf is the catalog body; the alchemist golem fails the image and moddable-tile checks and stays native'}],
          'kept_native': [],
          'neighbours_kept_native': [
              {'name': 'black mamba', 'reason': 'tied at 2.7 with weaver patriarch, luminous horror and necrotic mass for the last three slots; survey-document row order (weaver patriarch 626, luminous horror 669, necrotic mass 872, black mamba 997) takes the first three; next batch candidate'},
              {'name': 'alchemist golem', 'reason': 'other name (0.8)'},
              {'name': "Ak'Gishil", 'reason': 'unique, other name'}]}
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
                 'gate_reason': f"Exact source identity re-verified directly against game/modules/tome source (name={a['name']}, define_as={a['define_as']}, type={a['type']}/subtype={a['subtype']}, unique={a['unique']}, native_tall={a['native_tall']}); details and hashes in evidence/monster-batch-y-20260930/source-contracts.json. {a['structure']}. Exact catalog entry only, never a whole-subtype mapping.",
                 'render_evidence': [{'path': render, 'sha256': evsha}]}
        if a.get('refinement'):
            entry['refinement'] = a['refinement']
        packs.setdefault(a['pack'], []).append(entry)
    for n, assets in packs.items():
        p = ADDON / f'art/production/batches/monster-batch-y-{n}.json'
        if p.exists():
            print('exists, skipped', p.name)
            continue
        p.write_text(json.dumps({'schema': 1, 'batch_id': f'monster-batch-y-{n}', 'assets': assets}, indent=2, ensure_ascii=False) + '\n')
        print('wrote', p.name)


if __name__ == '__main__':
    build()
