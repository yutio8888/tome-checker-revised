"""Generate the monster-batch-ab task packs and the pinned source-contract
evidence (survey-2 unscheduled list after batch AA: entrenched horror, orc
summoner, greater mummy, shadowblade, orc elite fighter, orc elite berserker,
boiling horror, venom wyrm, alchemist golem, swarm hive, Forest Troll
Hedge-Wizard, ultimate shivgoroth; see SELECTION.md). Pure bookkeeping: hashes
native sources/sprites, writes JSON and the composite family references. Retry
packs are appended by later edits of retries.py (never overwritten)."""
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
ART_REL = 'game/addons/tome-checker-revised/art/monster-batch-ab/'
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
GRU = 'general/npcs/orc-grushnak.lua'
GOR = 'general/npcs/orc-gorbat.lua'
THI = 'general/npcs/thieve.lua'
VEN = 'general/npcs/venom-drake.lua'
CON = 'general/npcs/construct.lua'
SHI = 'general/npcs/shivgoroth.lua'
TRO = 'general/npcs/troll.lua'
AER = 'zones/ancient-elven-ruins/npcs.lua'
MUM = 'general/npcs/mummy.lua'

REF_ELITE_ORCS = RC('orc-fighters', ['orc-fighter', 'orc-soldier', 'orc-warrior', 'orc-berserker'], 2,
                    'Four shipped orc tokens (the orc fighter: grey plate, HORNED helm, ROUND red-striped shield and an axe; the orc soldier: dark spiked armour with an axe held low; the orc warrior: a leather-clad green orc with a curved blade; the orc berserker: pale STEEL plate, straight horned helm, crimson cloth, a short-hafted axe at the shoulder): both elite orcs are a different rank of armoured brute: the ELITE FIGHTER is a heavy bulwark in polished steel plate with ROYAL-BLUE enamel and gold trim, a closed great-helm with a tall white horsehair CREST and no horns, a huge RECTANGULAR TOWER SHIELD with a spiked boss planted in front of the body and a war-axe raised behind it; the ELITE BERSERKER is a hunched charging brute in VERMILION-ORANGE lacquered plate with gold rivets, a cream FUR mantle, a skull-crowned helm with two long RAM-CURL horns swept forward, skull-beaded chains and a huge single-crescent two-handed axe swung low behind him; neither may be grey plate, carry a round shield, wear straight horns or copy the steel berserker pose.')
REF_ORC_CASTERS = RC('orc-casters', ['orc-corruptor', 'orc-necromancer', 'orc-pyromancer', 'orc-cryomancer', 'orc-blood-mage'], 3,
                     'Five shipped orc caster tokens (the corruptor in a gold-yellow robe with a green glow, the necromancer in a navy hooded robe, the pyromancer in a red-orange robe, the cryomancer in a blue robe, the blood mage in a crimson robe with a red orb): the orc summoner is a SAVAGE BEAST-SHAMAN, a green orc in a tawny spotted hide mantle and leather kilt with NO robe, an ANTLER-and-TUSK headdress, bone bead necklaces, both hands raising a tall wooden TOTEM STAFF topped with a carved beast skull and hanging feathers while three glowing turquoise-jade SPIRIT WISPS coil out of the staff; not a robed mage, not blue, red, navy or gold.')
REF_MUMMIES = RC('mummies', ['rotting-mummy', 'ancient-elven-mummy', 'greater-mummy-lord', 'animated-mummy-wrappings'], 2,
                 'Four shipped mummy tokens (the rotting mummy: a plain tan-bandaged shambler; the ancient elven mummy: a pale bandaged elf; the greater mummy lord: a GOLD-ARMOURED mummy with a crested helm, round shield and short sword; the animated wrappings: an empty coiled bandage S): the greater mummy is a tall gaunt PRESERVED corpse wound in layered clean IVORY linen wrappings, a tall striped blue-and-gold NEMES-style royal headdress, a broad turquoise-and-gold jewelled collar, sunken glowing pale-blue eyes, a huge two-handed bronze GREATSWORD resting over the shoulder and the free hand raised with a pale frost-blue glow; not gold armour, not a shield, not a plain tan shambler and not an elf.')
REF_THIEVES = RC('thieves', ['assassin', 'rogue', 'thief', 'rogue-sapper', 'cutpurse'], 3,
                 'Five shipped thief tokens (the assassin: a grey-cloaked knifeman with a red sash and one dagger; the rogue: a dark-blue hooded runner; the thief: a brown-cloaked sneak; the rogue sapper: a goggled brown trapper; the cutpurse: a small hooded pickpocket): the shadowblade is a SHADOW-MAGE duellist caught mid-leap with TWO LONG CURVED SILVER BLADES crossed in an X in front of him, a pale half-mask, a long flowing PERIWINKLE-blue scarf and cloak streaming behind him and trailing crescent tendrils of dark violet shadow; not grey, not brown, not a single dagger, not crouched and not hooded-and-hunched.')
REF_AQUA_HORRORS = RC('aquatic-horrors', ['ravenous-horror', 'swarming-horror', 'bloated-horror', 'necrotic-mass'], 2,
                      'Four shipped horror tokens (the ravenous horror: a fanged deep-sea fish head; the swarming horror: a ring of small silver fish; the bloated horror: a pink baby-faced blob; the necrotic mass: a pink-brown lump): the three aquatic bodies of this batch are none of these: the ENTRENCHED HORROR is a stony pale-limestone PILLAR ringed with a wreath of long curling teal tentacles and glowing seams; the BOILING HORROR is a floating sphere of roiling aquamarine water crowned with white froth and steam, an orange heat-core glimpsed inside; the SWARM HIVE is a titanic pale pearl-grey flesh mound pocked with pink-mouthed orifices from which small silver fish-horrors stream; no fish head, no ring of fish and no pink baby blob.')
REF_WYRMS = RC('drakes', ['venom-drake', 'fire-wyrm', 'fire-drake', 'cold-drake'], 2,
               'Four shipped dragon tokens (the venom drake: an olive-green flat-crouching winged drake; the fire wyrm: a red serpentine wyrm coiled in a ring; the fire drake and cold drake: winged four-legged drakes): the venom wyrm is an old poisonous wyrm REARED UP on its haunches with a long swan-like S-CURVED neck, a great spiked frill and mane, a mouth dripping bright acid, a short thick tail curling up behind it and no spread wings; lime and acid-yellow green rather than olive; not crouching flat, not a coiled ring and not winged.')
REF_GOLEMS = RC('golems', ['golem', 'broken-golem'], 2,
                'Two shipped golem tokens (the golem: a stocky orange stone golem with cyan runes carrying a big hammer; the broken golem: a cracked grey rubble golem): the alchemist golem is a slimmer, polished, smooth TAN-SANDSTONE golem standing straight with both arms hanging, bright GOLD rune inlays, a single round glowing CYAN eye and a glowing cyan orb set in the chest, no hammer; not orange, not cracked grey, not stocky and not carrying a weapon.')
REF_SHIV = RC('shivgoroths', ['shivgoroth', 'greater-shivgoroth'], 2,
              'Two shipped ice-elemental tokens (the shivgoroth: a small crouching light-blue crystal beast; the greater shivgoroth: a white-blue ice giant standing among crystal spikes): the ultimate shivgoroth is a towering upright SAPPHIRE-and-cobalt faceted ice colossus with a glowing bright CYAN core in its chest, a crown of long icicle spikes and a ring of floating ice shards and swirling white snow orbiting it; deeper blue, ringed and crowned, not white and not crouching.')
REF_TROLLS = RC('trolls', ['forest-troll', 'cave-troll', 'stone-troll', 'mountain-troll'], 2,
                'Four shipped troll tokens (the forest troll: a yellow-green loin-clothed brute; the cave troll: a tan spear-carrying brute; the stone troll: a grey brute; the mountain troll): the Forest Troll Hedge-Wizard is the same yellow-green skin but a gaunt, old, hunched HEDGE-MAGE draped in a heavy plum-purple patterned ritual TABARD with a black buckled shoulder strap and dark wrist bands, thin atrophied arms, wild white eyebrows and a glaring old face, both hands held forward with roaring ORANGE flames between the fingers; not a loincloth brute, not tan, not grey and not carrying a spear.')

DEFC = ' NPC.lua:33 default-name image (npc/<type>_<subtype>_<name>.png) is the only image source: no image=, nice_tile, add_mos, moddable_tile, shader, anim or add_displays on the leaf or base; generic actor.image==entry.image single path; native sprite 64x64'
DEFD = ' define_as-bound entry: the catalog entry carries define_as and the matcher rejects any actor with another (or no) define_as'
def tall_short(png, uniq=False):
    return (' resolvers.nice_tile{tall=1} on the leaf (no image= on the leaf or base, so NPC.lua:33 default-name image ' + png + ' is used; the resolver expands to invis.png + one add_mos entry {image=e.image, display_h=2, display_y=-1}, the same live-confirmed shorthand as the ogre guard, mauler and pounder; with nicer_tiles off it is a no-op and the default-name image is the single path); no moddable_tile, shader, anim or add_displays; native sprite 64x128; '
            + ('UNIQUE, so nativeTallImage accepts the tall body through the unique path (like Kyless and Walrog) and the entry carries unique=true but no native_tall flag' if uniq else 'non-unique with no define_as, so the catalog entry carries native_tall=true'))

# ---- pack 1: entrenched horror, boiling horror, swarm hive, ultimate shivgoroth ----
asset(1, 'entrenched-horror', 'entrenched horror',
      "lake-nur pool (general/npcs/horror_aquatic.lua:62, horror/aquatic, non-unique, no define_as, rank 3, base BASE_NPC_HORROR_AQUATIC, nice_tile tall body); the only definition of this name",
      [src(HAQ, 'name = "entrenched horror"'), src(HAQ, 'resolvers.nice_tile', after='name = "entrenched horror"'), src(HAQ, 'T_EARTHQUAKE', after='name = "entrenched horror"'), src(HAQ, 'never_move = 1', after='name = "entrenched horror"'), src(HAQ, 'define_as = "BASE_NPC_HORROR_AQUATIC"')],
      src(HAQ, 'define_as = "BASE_NPC_HORROR_AQUATIC"'), None, 'horror', 'aquatic', False, True,
      'base BASE_NPC_HORROR_AQUATIC (horror/aquatic, no image=, no shader, no sustains_at_birth in the base);' + tall_explicit('horror_aquatic_entrenched_horror') + '; the leaf has no sustains_at_birth (Dig, Earthen Missiles and Earthquake are activated); the base on_die only logs an air bubble and touches terrain; never_move = 1; no equip, no auto_classes',
      'horror_aquatic_entrenched_horror.png',
      [STY, IDN('horror_aquatic_entrenched_horror.png', 'Native shape (64x128, tall): a grey stony pillar of pockmarked rock wrapped by long thin black tentacles that curl in every direction. Keep the massive stony pillar ringed by long thin probing tentacles, drawn as ONE compact figure filling the disc, no tall canvas, in pale limestone with glowing seams and mid-tone teal tentacles instead of near-black.'), REF_AQUA_HORRORS],
      "An entrenched horror seen from a steep overhead three-quarter angle: a massive squat PILLAR of pale weathered limestone-grey and blue-grey rock, encrusted with rounded barnacle-like knobs and stacked stony plates, with glowing pulsing TEAL-CYAN seams running between the plates as if it breathes; from its sides and crown rises a WREATH of eight long thin glossy tentacles in mid TEAL and blue-violet with pale sucker rows, each tentacle curling outward and hooking back toward the body, tips pointing inward; broad pale highlight planes on every upper-left plate and a thin bright rim light. Stony, ringed by tentacles and complete.",
      "Aquatic horrors: the ENTRENCHED HORROR is the STONY LIMESTONE PILLAR wreathed by curling teal tentacles with glowing seams (silhouette: a broad rounded pillar with a ring of hooked tentacles; hue: pale grey-blue stone with teal; value: light stone, mid tentacles). The shipped ravenous horror is a fanged fish head, the swarming horror a ring of small silver fish and the bloated horror a pink baby-faced blob: this must not be a fish, a school of fish or a pink blob.",
      "Pale limestone and blue-grey stone, glowing teal-cyan seams, mid teal and blue-violet tentacles with pale suckers, a thin bright rim; nothing darker than mid teal except thin gaps between plates; NO black tentacles, no black stone; the seam glow stays on the body and must not tint the disc, which stays neutral charcoal at reference lightness." + DISC,
      "READY tall (entrenched horror, native_tall)", comp=COMP + FIT + COMPACT + BRIGHT + DARKFIX + CATS)

asset(1, 'boiling-horror', 'boiling horror',
      "lake-nur pool (general/npcs/horror_aquatic.lua:133, horror/aquatic, non-unique, no define_as, rank 2, base BASE_NPC_HORROR_AQUATIC, nice_tile tall body); the only definition of this name",
      [src(HAQ, 'name = "boiling horror"'), src(HAQ, 'resolvers.nice_tile', after='name = "boiling horror"'), src(HAQ, 'T_BURNING_WAKE', after='name = "boiling horror"'), src(HAQ, 'resolvers.sustains_at_birth()', after='name = "boiling horror"'), src(HAQ, 'define_as = "BASE_NPC_HORROR_AQUATIC"')],
      src(HAQ, 'define_as = "BASE_NPC_HORROR_AQUATIC"'), None, 'horror', 'aquatic', False, True,
      'base BASE_NPC_HORROR_AQUATIC (horror/aquatic, no image=, no shader, no sustains_at_birth in the base);' + tall_explicit('horror_aquatic_boiling_horror') + '; the leaf calls resolvers.sustains_at_birth() and two of its talents are sustained: Thermal Aura (particles and temporary values only) and Burning Wake (talents/spells/wildfire.lua:78 addShaderAura, native shader-aura bookkeeping on add_mos that the matcher already ignores); no equip, no auto_classes',
      'horror_aquatic_boiling_horror.png',
      [STY, IDN('horror_aquatic_boiling_horror.png', 'Native shape (64x128, tall): a glowing cyan orb of water crowned with rising white steam and foam. Keep the frothing ball of heated water with steam, drawn as ONE compact figure filling the disc, no tall canvas, as a roiling aquamarine sphere with an orange heat core.'), REF_AQUA_HORRORS],
      "A boiling horror seen from a steep overhead three-quarter angle: a floating SPHERE of roiling bright AQUAMARINE and turquoise water hovering just above the disc as one compact figure, its surface churning with large bursting bubbles and a thick cap of bright WHITE FROTH, a glowing hot ORANGE-GOLD heat core visible through the water in the middle, three small water spouts and curling pale white STEAM plumes rising and drifting off the top (steam stays close to the body), pale specular highlights over the whole upper-left of the sphere and a thin bright cyan-white rim light; no puddle, no spill and no splash reaching the disc. Roiling, frothing, hot and complete.",
      "Aquatic horrors: the BOILING HORROR is the FLOATING SPHERE OF ROILING AQUAMARINE WATER with a white froth cap, steam plumes and an orange heat core (silhouette: a round ball with a frothy top and rising wisps; hue: aquamarine, white and orange; value: light). The shipped ravenous horror is a fanged fish head, the swarming horror a ring of silver fish and the void horror a lens-shaped indigo tear: this must not be a fish, a ring of fish or a lens.",
      "Bright aquamarine and turquoise water, white froth and steam, an orange-gold heat core, a thin bright rim; nothing darker than mid teal except thin bubble seams; the heat glow stays inside the sphere and must not warm or light the disc, which stays neutral charcoal at reference lightness and receives no water." + DISC,
      "READY tall (boiling horror, native_tall)", comp=COMP + FIT + COMPACT + BRIGHT + CATS)

asset(1, 'swarm-hive', 'swarm hive',
      "lake-nur pool (general/npcs/horror_aquatic.lua:162, horror/aquatic, non-unique, no define_as, rank 3, base BASE_NPC_HORROR_AQUATIC, nice_tile tall body); the only definition of this name; its Summon builds swarming horror leaves (batch Z token)",
      [src(HAQ, 'name = "swarm hive"'), src(HAQ, 'resolvers.nice_tile', after='name = "swarm hive"'), src(HAQ, 'T_SUMMON', after='name = "swarm hive"'), src(HAQ, 'summon = {{type="horror"', after='name = "swarm hive"'), src(HAQ, 'define_as = "BASE_NPC_HORROR_AQUATIC"')],
      src(HAQ, 'define_as = "BASE_NPC_HORROR_AQUATIC"'), None, 'horror', 'aquatic', False, True,
      'base BASE_NPC_HORROR_AQUATIC (horror/aquatic, no image=, no shader, no sustains_at_birth in the base);' + tall_explicit('horror_aquatic_swarm_hive') + '; the leaf has no sustains_at_birth; Summon (special_rarity hive_swarm_rarity) builds swarming horror leaves that wear their own token; never_move = 1; no equip, no auto_classes',
      'horror_aquatic_swarm_hive.png',
      [STY, IDN('horror_aquatic_swarm_hive.png', 'Native shape (64x128, tall): a titanic grey pockmarked mound of flesh. Keep the huge pulsating mound pocked with orifices, drawn as ONE compact figure filling the disc, no tall canvas, in pale pearl-grey flesh with pink mouths and a few small silver fish-horrors bursting out.'), REF_AQUA_HORRORS],
      "A swarm hive seen from a steep overhead three-quarter angle: a titanic rounded MOUND of pale PEARL-GREY and lavender-grey pulsating flesh standing on the disc as one compact figure, pocked all over with round orifices and lumpy blisters, seven of them wide-open PINK mouths with mid-rose lips, and from four of those mouths a few small SILVER fish-like horrors (small bright fish shapes with tiny fins, five to seven in all) burst out and spiral upward around the mound; fine pink veins under the skin, broad pale highlight planes on every upper-left lump and a thin bright rim light. Pocked, pulsing, spawning and complete.",
      "Aquatic horrors: the SWARM HIVE is the PEARL-GREY PULSATING FLESH MOUND pocked with pink mouths that spawn small silver fish (silhouette: a rounded lumpy mound with a few small fish spiralling out; hue: pearl-grey and lavender with pink mouths and silver fish; value: light). The shipped swarming horror is a ring of silver fish, the bloated horror a pink baby-faced blob and the necrotic mass a pink-brown lump with skulls: this must not be a ring of fish, a baby face or a brown lump.",
      "Pale pearl-grey and lavender-grey flesh, pink mouths and veins, small bright silver fish, a thin bright rim; nothing darker than mid rose except the mouth hollows and the seams between lumps; NO black or dark grey mass; the disc stays neutral charcoal at reference lightness." + DISC,
      "READY tall (swarm hive, native_tall)", comp=COMP + FIT + COMPACT + BRIGHT + DARKFIX + CATS)

asset(1, 'ultimate-shivgoroth', 'ultimate shivgoroth',
      "norgos-lair pool (general/npcs/shivgoroth.lua:88, elemental/ice, non-unique, no define_as, rank 3, base BASE_NPC_SHIVGOROTH, nice_tile tall body); the only definition of this name",
      [src(SHI, 'name = "ultimate shivgoroth"'), src(SHI, 'resolvers.nice_tile', after='name = "ultimate shivgoroth"'), src(SHI, 'T_ICE_STORM', after='name = "ultimate shivgoroth"'), src(SHI, 'resolvers.sustains_at_birth()', after='name = "ultimate shivgoroth"'), src(SHI, 'define_as = "BASE_NPC_SHIVGOROTH"')],
      src(SHI, 'define_as = "BASE_NPC_SHIVGOROTH"'), None, 'elemental', 'ice', False, True,
      'base BASE_NPC_SHIVGOROTH (elemental/ice, no image=, no shader, no sustains_at_birth in the base);' + tall_explicit('elemental_ice_ultimate_shivgoroth') + '; the leaf calls resolvers.sustains_at_birth() but none of its talents is sustained (Glacial Vapour, Ice Shards, Frozen Ground and Ice Storm are activated); the player-only Shivgoroth Form effect is not applied to npcs; no equip, no auto_classes',
      'elemental_ice_ultimate_shivgoroth.png',
      [STY, IDN('elemental_ice_ultimate_shivgoroth.png', 'Native shape (64x128, tall): an upright pale-blue faceted ice golem with spiked shoulders and clawed hands. Keep the towering faceted ice colossus, drawn as ONE compact figure filling the disc, no tall canvas, in deeper sapphire with a glowing cyan core, an icicle crown and a ring of orbiting ice shards and snow, clearly different from the white greater shivgoroth.'), REF_SHIV],
      "An ultimate shivgoroth seen from a steep overhead three-quarter angle: a towering upright COLOSSUS of faceted deep SAPPHIRE and cobalt ice with bright pale-cyan facet highlights, broad spiked shoulders, heavy clawed fists hanging at its sides, a glowing bright CYAN-WHITE core burning in the middle of its chest, a crown of long ICICLE spikes on its head, and around it a ring of eight floating ice SHARDS and a thin swirl of white snow orbiting at chest height; white frost rime along every upper-left edge and a thin bright icy rim light. Towering, sapphire, crowned and complete.",
      "Ice elementals: the ULTIMATE SHIVGOROTH is the TOWERING SAPPHIRE ICE COLOSSUS with a glowing cyan chest core, an icicle crown and an orbiting ring of ice shards and snow (silhouette: a broad upright figure with a spiked crown and a ring of shards around it; hue: sapphire and cobalt with cyan and white frost; value: mid-light with a bright core). The shipped shivgoroth is a small crouching light-blue crystal beast and the greater shivgoroth a white-blue ice giant among crystal spikes: this must not be crouching, must not be white and must not lack the shard ring and crown.",
      "Deep sapphire and cobalt ice with bright cyan facet highlights, white frost rime, a glowing cyan-white core, pale ice shards and snow, a thin bright rim; nothing darker than mid cobalt except thin facet seams; NO black or navy body; the glow stays on the body and must not tint the disc, which stays neutral charcoal at reference lightness." + DISC,
      "READY tall (ultimate shivgoroth, native_tall)", comp=COMP + FIT + COMPACT + BRIGHT + DARKFIX + CATS)

# ---- pack 2: orc elite fighter, orc elite berserker, orc summoner, greater mummy ----
asset(2, 'orc-elite-fighter', 'orc elite fighter',
      "vor-armoury pool and the grushnak-pride map scripts / grushnak-armory vault (general/npcs/orc-grushnak.lua:79, humanoid/orc, non-unique, define_as ORC_ELITE_FIGHTER, rank 3, base BASE_NPC_ORC_GRUSHNAK, default-name image); the only definition of this name; the random bosses of grushnak-pride are made from this exact define_as and go through captureRandomOrigin",
      [src(GRU, 'name = "orc elite fighter"'), src(GRU, 'define_as = "ORC_ELITE_FIGHTER"'), src(GRU, 'T_SHIELD_WALL', after='name = "orc elite fighter"'), src(GRU, 'resolvers.equip', after='name = "orc elite fighter"'), src(GRU, 'resolvers.racial()'), src(GRU, 'resolvers.sustains_at_birth()'), src(GRU, 'define_as = "BASE_NPC_ORC_GRUSHNAK"')],
      src(GRU, 'define_as = "BASE_NPC_ORC_GRUSHNAK"'), 'ORC_ELITE_FIGHTER', 'humanoid', 'orc', False, False,
      'base BASE_NPC_ORC_GRUSHNAK (humanoid/orc, no image=, no shader);' + DEFC + ';' + DEFD + ' (ORC_ELITE_FIGHTER); resolvers.racial() only adds orc levelup talents; the base calls resolvers.sustains_at_birth() and Shield Wall is the leaf sustain (rotating-shield particles and temporary values only); resolvers.equip a waraxe, shield and massive armour (equipment only, no moddable_tile); resolvers.inscriptions picks random runes/infusions (no display write); no auto_classes',
      'humanoid_orc_orc_elite_fighter.png',
      [STY, IDN('humanoid_orc_orc_elite_fighter.png', 'Native shape (64x64): a huge orc in grey massive plate with a round shield and an axe. Keep the massive-armoured shield-and-axe orc, but as an ELITE bulwark: polished steel plate with royal-blue enamel and gold trim, a closed great-helm with a tall white horsehair crest, a huge rectangular tower shield with a spiked boss planted in front and the axe raised behind it, drawn as ONE compact figure filling the disc, clearly different from the shipped orc fighter.'), REF_ELITE_ORCS],
      "An orc elite fighter seen from a steep overhead three-quarter angle: a huge hulking orc bulwark in MASSIVE polished pale STEEL plate with ROYAL-BLUE enamel panels and bright GOLD trim, a closed great-helm with a T-shaped visor slit and a tall white HORSEHAIR CREST swept back (no horns), rounded steel pauldrons with gold rims, a green tusked jaw visible under the visor, a huge RECTANGULAR TOWER SHIELD of blue-enamelled steel with a gold border and a spiked gold boss held in front of the body and planted on the ground, and a single-bladed steel WAR-AXE raised behind the shield edge at a diagonal with the head tucked beside the helm; broad pale highlight planes on every upper-left plate and a thin bright rim light. Armoured, crested, shielded and complete.",
      "Orcs: the ORC ELITE FIGHTER is the CRESTED BULWARK behind a huge RECTANGULAR TOWER SHIELD in steel, royal blue and gold with a war-axe raised behind (silhouette: a wide rectangle of shield in front of a helmed figure with a tall crest; hue: bright steel, royal blue, gold, white crest; value: bright). The shipped orc fighter is grey plate with horns and a ROUND red-striped shield, the orc soldier dark spiked armour, the orc warrior leather with a curved blade and the orc berserker steel plate with straight horns and a short axe: this must not have horns, a round shield or grey plate.",
      "Bright polished steel, royal-blue enamel, gold trim and rivets, a white horsehair crest, green skin, a thin bright rim light; nothing darker than mid steel-blue except the visor slit and plate seams; NO black armour; the disc stays neutral charcoal at reference lightness." + DISC,
      "READY single, define_as ORC_ELITE_FIGHTER (orc elite fighter)", comp=COMP + FIT + COMPACT + BRIGHT + DARKFIX)

asset(2, 'orc-elite-berserker', 'orc elite berserker',
      "vor-armoury pool and the grushnak-pride map scripts / grushnak-armory vault (general/npcs/orc-grushnak.lua:134, humanoid/orc, non-unique, define_as ORC_ELITE_BERSERKER, rank 3, base BASE_NPC_ORC_GRUSHNAK, default-name image); the only definition of this name; the plain orc berserker is another leaf (own token); the random bosses of grushnak-pride are made from this exact define_as and go through captureRandomOrigin",
      [src(GRU, 'name = "orc elite berserker"'), src(GRU, 'define_as = "ORC_ELITE_BERSERKER"'), src(GRU, 'T_JUGGERNAUT', after='name = "orc elite berserker"'), src(GRU, 'T_BERSERKER', after='name = "orc elite berserker"'), src(GRU, 'resolvers.equip', after='name = "orc elite berserker"'), src(GRU, 'resolvers.sustains_at_birth()'), src(GRU, 'define_as = "BASE_NPC_ORC_GRUSHNAK"')],
      src(GRU, 'define_as = "BASE_NPC_ORC_GRUSHNAK"'), 'ORC_ELITE_BERSERKER', 'humanoid', 'orc', False, False,
      'base BASE_NPC_ORC_GRUSHNAK (humanoid/orc, no image=, no shader);' + DEFC + ';' + DEFD + ' (ORC_ELITE_BERSERKER); resolvers.racial() only adds orc levelup talents; the base calls resolvers.sustains_at_birth() and Berserker and Juggernaut are the leaf sustains (particles and temporary values only); resolvers.equip a battleaxe and massive armour (equipment only, no moddable_tile); resolvers.inscriptions picks random runes/infusions (no display write); no auto_classes',
      'humanoid_orc_orc_elite_berserker.png',
      [STY, IDN('humanoid_orc_orc_elite_berserker.png', 'Native shape (64x64): a huge orc in grey massive plate holding a huge axe across the body. Keep the massive-armoured axe orc, but as a hunched CHARGING elite: vermilion-orange lacquered plate with gold rivets, a cream fur mantle, a skull-crowned helm with two long ram-curl horns, skull-beaded chains and a huge single-crescent two-handed axe swung low behind him, drawn as ONE compact figure filling the disc, clearly different from the steel orc berserker.'), REF_ELITE_ORCS],
      "An orc elite berserker seen from a steep overhead three-quarter angle: a huge hulking orc hunched forward in a CHARGE with a roaring tusked face, wearing MASSIVE plate armour of bright VERMILION-ORANGE lacquer with gold rivets and gold edging, a thick cream-white FUR mantle over the shoulders, a helm crowned with a small skull and two long RAM-CURL horns swept forward and down, a chain of small bone-white skulls slung across the chest, spiked gold-and-orange pauldrons, and a huge single-crescent-bladed two-handed steel BATTLEAXE swung low behind him to one side with the blade tucked inside the disc; no shield; broad pale highlight planes on every upper-left plate and a thin bright rim light. Charging, horned, lacquered and complete.",
      "Orcs: the ORC ELITE BERSERKER is the HUNCHED CHARGING brute in vermilion-orange lacquered plate with a fur mantle, ram-curl horns swept forward, skull chains and a crescent axe swung low behind (silhouette: a forward-leaning mass with curled horns and a trailing axe; hue: vermilion-orange, gold and cream fur; value: bright). The shipped orc berserker is an UPRIGHT pale steel plate orc with straight horns and a short axe at the shoulder, and the shipped orc fighter is grey plate with a shield: this must not be steel, upright, straight-horned, shielded or grey.",
      "Bright vermilion-orange lacquer with gold rivets, cream fur, bone-white skulls, green skin, steel axe blade, a thin bright rim light; nothing darker than mid orange except eye slits and plate seams; NO dark crimson or maroon plate, no black armour; the disc stays neutral charcoal at reference lightness." + DISC,
      "READY single, define_as ORC_ELITE_BERSERKER (orc elite berserker)", comp=COMP + FIT + COMPACT + BRIGHT + DARKFIX)

asset(2, 'orc-summoner', 'orc summoner',
      "ardhungol, unremarkable-cave and rak-shor-pride pools (general/npcs/orc-gorbat.lua:53, humanoid/orc, non-unique, no define_as, rank 2, base BASE_NPC_ORC_GORBAT, default-name image); the only definition of this name (the grand summoner is another leaf)",
      [src(GOR, 'name = "orc summoner"'), src(GOR, 'T_PSIBLADES', after='name = "orc summoner"'), src(GOR, 'T_MINOTAUR', after='name = "orc summoner"'), src(GOR, 'resolvers.equip', after='name = "orc summoner"'), src(GOR, 'resolvers.sustains_at_birth()'), src(GOR, 'define_as = "BASE_NPC_ORC_GORBAT"')],
      src(GOR, 'define_as = "BASE_NPC_ORC_GORBAT"'), None, 'humanoid', 'orc', False, False,
      'base BASE_NPC_ORC_GORBAT (humanoid/orc, no image=, no shader);' + DEFC + '; resolvers.racial() only adds orc levelup talents; the base and the leaf call resolvers.sustains_at_birth() and Psiblades is the only sustained talent (talents/gifts/mindstar-mastery.lua:29; it calls updateModdableTile, which for a non-moddable actor only rebuilds shader-aura bookkeeping); resolvers.equip two mindstars and a totem (equipment only); the Minotaur, Ritch Flamespitter and Spider summons build other leaves; no auto_classes',
      'humanoid_orc_orc_summoner.png',
      [STY, IDN('humanoid_orc_orc_summoner.png', 'Native shape (64x64): a green orc in a fur mantle and leather kilt holding a long wooden staff, wreathed in a purple glow. Keep the green beast-shaman with the long staff, drawn as ONE compact figure filling the disc, as a savage totem-summoner with an antler-and-tusk headdress and three turquoise spirit wisps coiling from the staff, clearly not a robed orc mage.'), REF_ORC_CASTERS],
      "An orc summoner seen from a steep overhead three-quarter angle: a stocky GREEN-skinned orc beast-shaman standing on the disc with a tawny spotted HIDE MANTLE over the shoulders, a brown leather kilt and no robe, an ANTLER-and-TUSK headdress, several bone-bead necklaces, painted white stripes on the face and arms, both hands raising a tall wooden TOTEM STAFF topped with a carved pale beast SKULL and hung with red and turquoise feathers, and three glowing turquoise-JADE SPIRIT WISPS in the shapes of a horned head, a spider and a flame coiling out of the staff head around him (all close to the body); broad pale highlight planes on every upper-left surface and a thin bright rim light. Savage, antlered, calling and complete.",
      "Orcs: the ORC SUMMONER is the SAVAGE BEAST-SHAMAN with an antler-and-tusk headdress, a hide mantle and a totem staff with three turquoise spirit wisps (silhouette: a figure with antlers holding a tall staff up, wisps coiling around; hue: green skin, tawny hide, turquoise-jade spirits, white bone; value: mid-light). The shipped orc corruptor, necromancer, pyromancer, cryomancer and blood mage all wear coloured robes: this must not wear a robe and must not be gold, navy, red, blue or crimson.",
      "Green skin, tawny spotted hide, brown leather, bone-white antlers and skull, turquoise-jade spirit wisps, red and turquoise feathers, a thin bright rim light; nothing darker than mid brown except eye slits and seams; NO dark robe, no black leather; the spirit glow stays close to the body and must not tint the disc, which stays neutral charcoal at reference lightness." + DISC,
      "READY single, no define_as (orc summoner)", comp=COMP + FIT + COMPACT + BRIGHT + DARKFIX)

asset(2, 'greater-mummy', 'greater mummy',
      "ancient-elven-ruins pool (zones/ancient-elven-ruins/npcs.lua:176, undead/mummy, non-unique, define_as GREATER_MUMMY, rank 3, base BASE_NPC_MUMMY, explicit image=npc/undead_mummy_greater_mummy.png); the only definition of this name (the greater mummy lord GREATER_MUMMY_LORD is another leaf with its own token)",
      [src(AER, 'name = "greater mummy"'), src(AER, 'define_as = "GREATER_MUMMY"'), src(AER, 'image = "npc/undead_mummy_greater_mummy.png"', after='name = "greater mummy"'), src(AER, 'T_FREEZE', after='name = "greater mummy"'), src(AER, 'resolvers.equip', after='name = "greater mummy"'), src(MUM, 'define_as = "BASE_NPC_MUMMY"')],
      src(MUM, 'define_as = "BASE_NPC_MUMMY"'), 'GREATER_MUMMY', 'undead', 'mummy', False, False,
      'base BASE_NPC_MUMMY (undead/mummy, no image=, no shader, no sustains_at_birth);' + EXPL + ';' + DEFD + ' (GREATER_MUMMY); the PNG undead_mummy_greater_mummy.png is used by this leaf only; resolvers.equip a greatsword, mummy armour and a helm (equipment only, no moddable_tile); the talents (Weapons Mastery, Weapon Combat, Stunning Blow, Crush, Rush, Freeze, Manathrust) are passive or activated, none sustained; no sustains_at_birth; the leaf has no auto_classes (the lord leaf above it does)',
      'undead_mummy_greater_mummy.png',
      [STY, IDN('undead_mummy_greater_mummy.png', 'Native shape (64x64): a tall golden-wrapped mummy in a crested headdress with a bloody red left hand and a long weapon. Keep the tall wrapped mummy with the striped headdress, a big blade and one raised glowing hand, drawn as ONE compact figure filling the disc, in clean ivory linen with a blue-and-gold nemes headdress and jewelled collar, clearly not the gold-armoured greater mummy lord.'), REF_MUMMIES],
      "A greater mummy seen from a steep overhead three-quarter angle: a tall gaunt PRESERVED corpse wound in layered clean IVORY and pale sand linen wrappings with loose trailing ends, a tall striped BLUE-and-GOLD NEMES-style royal headdress, a broad TURQUOISE-and-gold jewelled collar, sunken glowing pale-blue eyes in a dark leathery face, a huge two-handed BRONZE GREATSWORD resting blade-up over the right shoulder and the left hand raised open with a cold pale FROST-BLUE glow above the palm; broad pale highlight planes on every upper-left wrapping and a thin bright rim light. Wrapped, crowned, armed and complete.",
      "Mummies: the GREATER MUMMY is the TALL IVORY-WRAPPED PHARAOH with a blue-and-gold nemes headdress, a turquoise collar, a bronze greatsword over the shoulder and a frost-blue glowing palm (silhouette: a tall wrapped figure with a flared headdress and a long blade; hue: ivory linen, blue and gold, turquoise; value: light). The shipped rotting mummy is a plain tan shambler, the ancient elven mummy a pale bandaged elf, the greater mummy lord a GOLD-ARMOURED mummy with a crested helm and round shield and the animated wrappings a coiled empty bandage: this must not be gold armour, carry a shield or be plain tan bandages.",
      "Clean ivory and pale sand linen, blue-and-gold headdress, turquoise-gold collar, bronze blade, pale frost-blue glow, a thin bright rim; nothing darker than mid tan except the eye sockets and the face; NO dark or brown wrappings; the frost glow stays at the palm and must not tint the disc, which stays neutral charcoal at reference lightness." + DISC,
      "READY single, define_as GREATER_MUMMY (greater mummy)", comp=COMP + FIT + COMPACT + BRIGHT + DARKFIX)

# ---- pack 3: shadowblade, venom wyrm, alchemist golem, Forest Troll Hedge-Wizard ----
asset(3, 'shadowblade', 'shadowblade',
      "thieves-tunnels and maze pools plus the thief-hideout vault and the bandit-fortress map (general/npcs/thieve.lua:162, humanoid/human, non-unique, define_as THIEF_ASSASSIN (repeated from the assassin leaf above it), rank 2, base BASE_NPC_THIEF, default-name image); the arena zone defines a second, unrelated 'shadowblade' (zones/arena/npcs.lua:773, base BASE_NPC_ARENA1, no define_as), which the define_as binding rejects",
      [src(THI, 'name = "shadowblade"'), src(THI, 'define_as = "THIEF_ASSASSIN"', after='name = "assassin"'), src(THI, 'T_SHADOW_COMBAT', after='name = "shadowblade"'), src(THI, 'T_INVISIBILITY', after='name = "shadowblade"'), src(THI, 'resolvers.sustains_at_birth()', after='name = "shadowblade"'), src(THI, 'define_as = "BASE_NPC_THIEF"'), src('zones/arena/npcs.lua', 'newEntity{ name = "shadowblade",')],
      src(THI, 'define_as = "BASE_NPC_THIEF"'), 'THIEF_ASSASSIN', 'humanoid', 'human', False, False,
      'base BASE_NPC_THIEF (humanoid/human, no image=, no shader);' + DEFC + ';' + DEFD + ' (THIEF_ASSASSIN, the same define_as as the assassin leaf; the assassin token is bound to the name assassin and this one to the name shadowblade, and each rejects the other name); resolvers.racial(), resolvers.equip (two daggers, light armour) and resolvers.inscriptions do not write the display; the base and the leaf call resolvers.sustains_at_birth() and Stealth and Shadow Combat are sustained (particles and temporary values only); Shadow Veil, Invisibility and Shadowstep are activated and their effects (shader while active) are rejected by the matcher; color_r/g/b are colour modulation only; no auto_classes',
      'humanoid_human_shadowblade.png',
      [STY, IDN('humanoid_human_shadowblade.png', 'Native shape (64x64): a dark-hooded human with two long curved blades caught mid-strike in a dark cloak. Keep the duelling shadow-blade with two long curved swords in a dynamic dual-strike pose, drawn as ONE compact figure filling the disc, in a bright periwinkle cloak and scarf with silver blades and trailing violet shadow crescents, clearly different from the grey single-dagger assassin.'), REF_THIEVES],
      "A shadowblade seen from a steep overhead three-quarter angle: a lithe human shadow-duellist caught mid-leap on the disc with TWO LONG CURVED SILVER SCIMITARS crossed in an X in front of the body with bright white edge highlights, a pale bone-white half-mask over the lower face, dark hair, a fitted slate-blue tunic with silver buckles and dark leather bracers, a long flowing PERIWINKLE-blue SCARF and short cloak streaming behind, and three curling CRESCENT tendrils of mid-violet shadow trailing from the cloak hem and the blades (all kept close to the body, no tendril reaching the outer ring); broad pale highlight planes on every upper-left surface and a thin bright rim light. Leaping, twin-bladed, veiled and complete.",
      "Thieves: the SHADOWBLADE is the LEAPING TWIN-SCIMITAR SHADOW-DUELLIST with a half-mask, a periwinkle scarf and cloak and violet shadow crescents (silhouette: a figure with two long crossed curved blades and a streaming scarf; hue: periwinkle, silver and violet; value: mid-light). The shipped assassin is a grey-cloaked knifeman with a red sash and one dagger, the rogue a dark-blue hooded runner, the thief a brown-cloaked sneak and the rogue sapper a goggled brown trapper: this must not be grey, brown or hooded, and must not hold a single dagger.",
      "Periwinkle and slate-blue cloth, bright silver blades, bone-white mask, mid-violet shadow crescents, silver buckles, a thin bright rim; nothing darker than mid slate-blue except hair, eye slits and thin seams; NO black cloak, no black tendrils; the shadow tendrils stay close to the body and must not darken or tint the disc, which stays neutral charcoal at reference lightness." + DISC,
      "READY single, define_as THIEF_ASSASSIN (shadowblade)", comp=COMP + FIT + COMPACT + BRIGHT + DARKFIX)

asset(3, 'venom-wyrm', 'venom wyrm',
      "noxious-caldera pool plus the acidic-vault and renegade-wyrmics vaults (general/npcs/venom-drake.lua:84, dragon/venom, non-unique, no define_as, rank 3, base BASE_NPC_VENOM_DRAKE, resolvers.nice_tile{tall=1}); the only definition of this name",
      [src(VEN, 'name = "venom wyrm"'), src(VEN, 'resolvers.nice_tile{tall=1}', after='name = "venom wyrm"'), src(VEN, 'T_CORROSIVE_BREATH', after='name = "venom wyrm"'), src(VEN, 'make_escort', after='name = "venom wyrm"'), src(VEN, 'define_as = "BASE_NPC_VENOM_DRAKE"'), src('resolvers.lua', 'function resolvers.calc.nice_tile', root='game/modules/tome/')],
      src(VEN, 'define_as = "BASE_NPC_VENOM_DRAKE"'), None, 'dragon', 'venom', False, True,
      'base BASE_NPC_VENOM_DRAKE (dragon/venom, no image=, no shader, no sustains_at_birth);' + tall_short('dragon_venom_venom_wyrm.png') + '; the leaf has no sustains_at_birth (Acidic Spray, Corrosive Mist, Corrosive Breath and Dissolve are activated); make_escort builds venom drake leaves (own native art, no token); the renegade-wyrmics random boss stays native as a non-unique tall boss; no equip, no auto_classes',
      'dragon_venom_venom_wyrm.png',
      [STY, IDN('dragon_venom_venom_wyrm.png', 'Native shape (64x128, tall): an old spiny green wyrm rearing on its haunches with a long S-curved neck, a spiked mane and a tail curling up. Keep the reared S-necked spiny wyrm, drawn as ONE compact figure filling the disc, no tall canvas, in bright lime and acid-yellow green with acid dripping from the jaw, clearly different from the flat-crouching winged venom drake and the coiled fire wyrm.'), REF_WYRMS],
      "A venom wyrm seen from a steep overhead three-quarter angle: an old powerful poisonous WYRM REARED UP on its haunches on the disc with a long swan-like S-CURVED neck and a horned head turned to the lower right, a great fan of long spiked FRILL and mane spines in bright acid yellow-green, bright LIME-green and acid-yellow scales with darker mid-green scale rows, a pale sallow cream belly, clawed forelegs held up against the chest, a short thick tail curling up behind the haunches, no spread wings, and glowing acid-green DRIPS and strings of caustic saliva falling from the open jaw onto its own chest (drips stay on the body); broad pale highlight planes on every upper-left scale and a thin bright rim light. Reared, spined, dripping and complete.",
      "Dragons: the VENOM WYRM is the REARED S-NECKED SPINY WYRM with a tall frill, acid-dripping jaws and a tail curling up (silhouette: an upright S-curve with a fan of spines; hue: bright lime and acid yellow-green with a cream belly; value: mid-light). The shipped venom drake is an olive-green flat-crouching winged drake, the fire wyrm a red serpent coiled in a ring and the fire and cold drakes winged four-legged drakes: this must not be olive, crouching, winged or ring-coiled.",
      "Bright lime and acid yellow-green scales with mid-green scale rows, cream belly, acid-green drips, pale-yellow claws and horns, a thin bright rim; nothing darker than mid green except eye slits and scale seams; NO dark olive body; the acid glow stays on the body and must not stain or tint the disc, which stays neutral charcoal at reference lightness and receives no puddle." + DISC,
      "READY tall (venom wyrm, native_tall via nice_tile{tall=1})", comp=COMP + FIT + COMPACT + BRIGHT + CATS)

asset(3, 'alchemist-golem', 'alchemist golem',
      "golem-graveyard pool (general/npcs/construct.lua:93, construct/golem, non-unique, no define_as, rank 3, base BASE_NPC_CONSTRUCT, default-name image); the only NPC definition of this name; the player's own alchemist golem uses the name golem with npc/alchemist_golem.png and a paper doll (golemancy.lua), never this name",
      [src(CON, 'name = "alchemist golem"'), src(CON, 'T_GOLEM_ARCANE_PULL', after='name = "alchemist golem"'), src(CON, 'resolvers.equip', after='name = "alchemist golem"'), src(CON, 'define_as = "BASE_NPC_CONSTRUCT"')],
      src(CON, 'define_as = "BASE_NPC_CONSTRUCT"'), None, 'construct', 'golem', False, False,
      'base BASE_NPC_CONSTRUCT (construct/golem, no image=, no shader, no sustains_at_birth);' + DEFC + '; the leaf has no sustains_at_birth (Golem Knockback, Golem Crush, Golem Beam and Golem Arcane Pull are activated); resolvers.equip a greatmaul (equipment only, no moddable_tile); resolvers.inscriptions picks random runes (no display write); no auto_classes',
      'construct_golem_alchemist_golem.png',
      [STY, IDN('construct_golem_alchemist_golem.png', 'Native shape (64x64): a stone-brown golem with rune markings and a single glowing blue eye ring in its head. Keep the slim standing rune-marked golem with a glowing cyan eye, drawn as ONE compact figure filling the disc, as polished tan sandstone with gold rune inlays, a cyan chest orb and arms hanging, clearly different from the orange hammer golem and the grey rubble golem.'), REF_GOLEMS],
      "An alchemist golem seen from a steep overhead three-quarter angle: a tall slim humanoid golem of smooth polished light TAN-SANDSTONE blocks standing straight on the disc with both arms hanging and heavy rounded fists, bright GOLD rune lines and inlaid gold bands across the chest, shoulders, arms and legs, a rounded head with a single round glowing CYAN eye, a glowing cyan orb set in the middle of the chest, small brass vents on the shoulders, broad pale highlight planes on every upper-left block and a thin bright rim light; no weapon. Polished, runed, glowing and complete.",
      "Golems: the ALCHEMIST GOLEM is the SLIM POLISHED TAN-SANDSTONE GOLEM with gold rune inlays, one cyan eye and a cyan chest orb, standing with arms hanging (silhouette: a straight upright humanoid of blocks with no weapon; hue: tan sandstone, gold, cyan; value: light). The shipped golem is a stocky orange stone golem with cyan runes carrying a big hammer and the broken golem a cracked grey rubble golem: this must not be orange, cracked grey, stocky or armed.",
      "Light tan sandstone, bright gold rune inlays and bands, brass vents, glowing cyan eye and chest orb, a thin bright rim; nothing darker than mid tan except thin block seams; NO dark brown stone; the cyan glow stays on the body and must not tint the disc, which stays neutral charcoal at reference lightness." + DISC,
      "READY single, no define_as (alchemist golem)", comp=COMP + FIT + COMPACT + BRIGHT + DARKFIX)

asset(3, 'forest-troll-hedge-wizard', 'Forest Troll Hedge-Wizard',
      "reknor pool (general/npcs/troll.lua:145, giant/troll, UNIQUE, no define_as, rank 3.5, base BASE_NPC_TROLL, resolvers.nice_tile{tall=1}); the only definition of this name",
      [src(TRO, 'name = "Forest Troll Hedge-Wizard"'), src(TRO, 'unique=true', after='newEntity{ base = "BASE_NPC_TROLL", unique=true,'), src(TRO, 'resolvers.nice_tile{tall=1}', after='name = "Forest Troll Hedge-Wizard"'), src(TRO, 'T_MANATHRUST', after='name = "Forest Troll Hedge-Wizard"'), src(TRO, 'resolvers.sustains_at_birth()', after='name = "Forest Troll Hedge-Wizard"'), src(TRO, 'define_as = "BASE_NPC_TROLL"')],
      src(TRO, 'define_as = "BASE_NPC_TROLL"'), None, 'giant', 'troll', True, False,
      'base BASE_NPC_TROLL (giant/troll, no image=, no shader);' + tall_short('giant_troll_forest_troll_hedge_wizard.png', uniq=True) + '; the leaf calls resolvers.sustains_at_birth() but none of its talents is sustained (Shielding, Manathrust and Flame are activated); on_added_to_level only sets inc_damage; the base has no equip beyond drops; no auto_classes',
      'giant_troll_forest_troll_hedge_wizard.png',
      [STY, IDN('giant_troll_forest_troll_hedge_wizard.png', 'Native shape (64x128, tall): a yellow-green troll with a heavy purple patterned tabard, a black buckled shoulder strap and dark wrist bands. Keep the yellow-green troll in the purple ritual tabard with the buckled strap and wrist bands, drawn as ONE compact figure filling the disc, no tall canvas, as a gaunt old hedge-mage with orange flames between his fingers, clearly different from the loin-clothed forest troll.'), REF_TROLLS],
      "The Forest Troll Hedge-Wizard seen from a steep overhead three-quarter angle: a gaunt old hunched yellow-green TROLL with a big warty nose, glaring eyes under wild WHITE eyebrows and a jutting lower jaw, thin atrophied arms, wearing a heavy patterned PLUM-PURPLE ritual TABARD with lighter lilac scale patterns hanging front and back, a black buckled leather shoulder strap and dark leather wrist bands, bare yellow-green legs and big clawed feet, both hands held forward with bright roaring ORANGE-and-yellow FLAMES between the fingers (flames kept small and close to the body); bright pale-yellow-green highlight planes on every upper-left surface and a thin bright rim light. Gaunt, robed, flaming and complete.",
      "Trolls: the FOREST TROLL HEDGE-WIZARD is the GAUNT OLD HUNCHED HEDGE-MAGE troll in a plum-purple patterned tabard with a buckled strap and flames between his fingers (silhouette: a hunched robed figure with forward hands and two small flames; hue: yellow-green skin, plum-purple and lilac tabard, orange flames; value: mid-light). The shipped forest troll is a muscular yellow-green loin-clothed brute, the cave troll a tan spear-carrying brute and the stone troll a grey brute: this must not wear a loincloth, be muscular, carry a spear or be tan or grey.",
      "Bright yellow-green skin, plum-purple and lilac tabard, white eyebrows, dark leather straps, orange-yellow flames, a thin bright rim; nothing darker than mid plum except the strap and wrist bands; NO black or navy tabard; the flames stay in the hands and must not tint or light the disc, which stays neutral charcoal at reference lightness." + DISC,
      "READY tall (Forest Troll Hedge-Wizard, unique native-tall)", comp=COMP + FIT + COMPACT + BRIGHT + DARKFIX + CATS)


def retry(id_, pack, **changes):
    base = next(a for a in A if a['id'] == id_)
    A.append(dict(base, pack=pack, **changes))


exec((HERE / 'retries.py').read_text()) if (HERE / 'retries.py').exists() else None


TALL_IDS = tuple(a['id'] for a in A if a['native_tall'])
SHORTHAND_IDS = ('venom-wyrm', 'forest-troll-hedge-wizard')
TALL_BODY_IDS = TALL_IDS + ('forest-troll-hedge-wizard',)
EXPL_IDS = ('greater-mummy',)
PNGF = {a['id']: 'NPC.lua:33 default-name image on the leaf (no image=/nice_tile)' for a in A}
PNGF.update({i: 'explicit image= on the leaf (no nice_tile/add_mos)' for i in EXPL_IDS})
PNGF.update({i: 'NPC.lua:33 default-name image on the leaf plus an explicit nice_tile tall body (image=invis.png, one add_mos entry with display_h=2, display_y=-1 naming the same PNG)' for i in TALL_IDS})
PNGF.update({i: 'NPC.lua:33 default-name image via resolvers.nice_tile{tall=1} (live-confirmed shorthand, as for the ogre guard, mauler, rune-spinner and pounder)' for i in SHORTHAND_IDS})
EVDIR = 'evidence/monster-batch-ab-20260930/source-contracts.json'
DEFINE = {a['id']: a['define_as'] for a in A}
NAMES_LIST = "entrenched horror, orc summoner, greater mummy, shadowblade, orc elite fighter, orc elite berserker, boiling horror, venom wyrm, alchemist golem, swarm hive, Forest Troll Hedge-Wizard, ultimate shivgoroth"


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
                                  'static_pin': ('nice_tile{tall=1} expands to this body (resolvers.lua nice_tile); ' + ('unique, so the unique tall path applies' if a['unique'] else 'not unique, so no unique-only tall path applies')) if a['id'] in SHORTHAND_IDS else 'nice_tile names the tall PNG explicitly; not unique, so no unique-only tall path applies'}
        if a['base']:
            ident['base_source'] = a['base']
        if len(a['srcs']) > 1:
            ident['extra_sources'] = a['srcs'][1:]
        identities.append(ident)
    findings = [
        "All twelve names have exactly one NPC leaf definition under game/modules/tome (grep of every actor definition, zones included), with one exception: the arena zone defines a second, unrelated 'shadowblade' (zones/arena/npcs.lua:773, base BASE_NPC_ARENA1, no define_as); the catalog entry binds define_as THIEF_ASSASSIN, so that arena actor stays native. The zone pools and vaults (grushnak-pride map scripts and grushnak-armory for the two elite orcs, thief-hideout and bandit-fortress for the shadowblade, acidic-vault and renegade-wyrmics for the venom wyrm) only build those same leaves through name/define_as/random_filter lookups, so they are the very same actors; a random boss made from a flat entry goes through the existing captureRandomOrigin path (the grushnak-pride random elite orcs are made from define_as ORC_ELITE_FIGHTER / ORC_ELITE_BERSERKER), a random boss made from a non-unique native-tall entry (the renegade-wyrmics venom wyrm) stays native because only unique tall bodies qualify.",
        "Summons that copy a monster wear its token: the swarm hive's Summon builds swarming horror leaves (batch Z token), the orc summoner's Minotaur, Ritch Flamespitter and Spider builds other leaves (their own token or native), no talent, effect or event builds a copy of any of the twelve bodies under its own name; the Battle Call of the elite orcs only calls existing allies.",
        "Same-family separation: the two elite orcs are define_as-bound (ORC_ELITE_FIGHTER, ORC_ELITE_BERSERKER) and each rejects the plain orc fighter and orc berserker names and PNGs (and the reverse); the shadowblade shares define_as THIEF_ASSASSIN with the assassin but is matched by its own name and PNG, and the assassin entry rejects the shadowblade name (tests exist both ways); the greater mummy (GREATER_MUMMY) and the greater mummy lord (GREATER_MUMMY_LORD) are different leaves with different PNGs.",
        "The Forest Troll Hedge-Wizard is a unique with no define_as; unique=true in the catalog entry (like Walrog and Kyless) lets nativeTallImage accept its tall body through the unique path, so it carries no native_tall flag. No non-unique actor can borrow its name or PNG.",
        "Entrenched horror, boiling horror, swarm hive and ultimate shivgoroth name their tall PNG explicitly in nice_tile; venom wyrm and the Hedge-Wizard use the nice_tile{tall=1} shorthand (default-name PNG). Boiling horror's Burning Wake adds native shader-aura bookkeeping to add_mos, which the matcher ignores; Psiblades (orc summoner) only calls updateModdableTile, a no-op for a non-moddable actor.",
        "No summon, clone, event or talent builds an actor with any of the twelve names using a different native PNG (grep of every actor definition, static map, quest script, vault, encounter, event and talent under game/modules/tome for the names and PNGs).",
        "Neighbours that reuse a name or subtype but stay native: 'Training Dummy' (kept native since batch T), 'ruin banshee', 'Aletta Soultorn', 'Filio Flightfond' (all 0.6, below this batch), the arena 'shadowblade', 'greater mummy lord' (own token), 'orc berserker' and 'orc fighter' (own tokens), 'venom drake' (native), 'golem' (own token) and the player's alchemist golem (name golem, PNG alchemist_golem.png, paper doll).",
        "Result: no per-identity `variants` entry and no `image_aliases` entry is needed for this batch.",
    ]
    ev = {'schema': 1,
          'task': "monster-batch-ab: static re-verification (no game launch) of the twelve identities that follow batch AA in the survey-2 unscheduled list (" + NAMES_LIST + ") against game/modules/tome source and native sprites. Every field below was read from source: name, type/subtype, define_as (four bind one: shadowblade THIEF_ASSASSIN, orc elite fighter ORC_ELITE_FIGHTER, orc elite berserker ORC_ELITE_BERSERKER, greater mummy GREATER_MUMMY), explicit or NPC.lua:33 default image, unique (only the Hedge-Wizard), PNG on disk, and absence of moddable_tile/shader/anim/add_displays on each leaf and its base. Findings: six identities are tall bodies (entrenched horror, boiling horror, swarm hive, ultimate shivgoroth: nice_tile image=invis.png with one explicit add_mos display_h=2, display_y=-1, non-unique native_tall=true; venom wyrm: the nice_tile{tall=1} shorthand, native_tall=true; Forest Troll Hedge-Wizard: the same shorthand, unique so no native_tall flag); six are 64x64 single images (orc summoner, shadowblade, orc elite fighter, orc elite berserker and alchemist golem use the NPC.lua:33 default-name image; the greater mummy names its PNG with image=).",
          'new_ids_not_in_catalog_before_this_batch': [i['id'] for i in identities], 'identities': identities,
          'runtime_mutation_scan': {
              'method': "every talent of each identity (resolvers.talents, inherited base talents and the base-file talent lists) was resolved under game/modules/tome/data/talents and its mode read (sustained/activated/passive); the same talents/, timed_effects/, birth/ and class/ greps for writes to type/subtype/image/add_mos/add_displays/moddable_tile/replace_display/shader as batches S to AA were applied and give the same writer set; the resolvers sustains_at_birth, inscriptions, equip, racial and nice_tile and the base-file resolvers were read; every auto_classes site under zones/, general/ and maps/ was listed with its leaf name.",
              'writers_found': [
                  {'file': 'game/modules/tome/data/talents/corruptions/shadowflame.lua', 'line': 97, 'talent': "Flame of Urh'Rok", 'effect': 'sustain: __old_type={type,subtype}; type,subtype = demon,major; image untouched; restored on deactivate'},
                  {'file': 'game/modules/tome/data/talents/psionic/thought-forms.lua', 'line': 93, 'talent': 'thought-form summons (Solipsist tree)', 'effect': 'sets type/subtype/image/moddable_tile/add_mos on the summoned minion copied from its summoner, never on the caster'},
                  {'file': 'game/modules/tome/data/talents/chronomancy/anomalies.lua', 'line': 587, 'talent': 'anomaly summons', 'effect': 'creates a separate spawned NPC with another image; not any identity of this batch'}],
              'other_hits_reviewed': [
                  'talents/spells/golemancy.lua and talents/uber/mag.lua (player-only moddable_tile writes: the player alchemist golem, name golem; no identity of this batch)',
                  'talents/spells/wildfire.lua:78 Burning Wake addShaderAura (boiling horror): native shader-aura bookkeeping on add_mos, ignored by the matcher (emptyIgnoringAura); talents/gifts/mindstar-mastery.lua:29 Psiblades (orc summoner): updateModdableTile is a no-op for a non-moddable actor apart from shader-aura bookkeeping',
                  'timed_effects/physical.lua and other.lua (add_displays/replace_display only while the effect is active)', 'timed_effects/magical.lua (invisibility, shadow veil and similar shaders, only while active)'],
              'timed_effects_review': "timed_effects write shader, replace_display, add_displays or image only while active (invisibility shaders, stone/ice/pin displays, Wrathroot, Shivgoroth form, dragon egg, Lord of Skulls): the matcher rejects them (native art shows) and restores the token when they end.",
              'sustains_at_birth_review': [
                  {'identity': 'boiling horror', 'sustained': ['Thermal Aura', 'Burning Wake'], 'note': 'Thermal Aura is particles and temporary values; Burning Wake adds native shader-aura bookkeeping to add_mos, ignored by the matcher'},
                  {'identity': 'orc summoner', 'sustained': ['Psiblades'], 'note': 'the base BASE_NPC_ORC_GORBAT and the leaf call resolvers.sustains_at_birth(); Psiblades reloads worn mindstars and calls updateModdableTile, no display write for a non-moddable actor'},
                  {'identity': 'orc elite fighter', 'sustained': ['Shield Wall'], 'note': 'the base calls resolvers.sustains_at_birth(); rotating-shield particles and temporary values only'},
                  {'identity': 'orc elite berserker', 'sustained': ['Berserker', 'Juggernaut'], 'note': 'the base calls resolvers.sustains_at_birth(); temporary values and particles only'},
                  {'identity': 'shadowblade', 'sustained': ['Stealth', 'Shadow Combat'], 'note': 'the base and the leaf call resolvers.sustains_at_birth(); particles and temporary values only'},
                  {'identity': 'Forest Troll Hedge-Wizard, ultimate shivgoroth', 'sustained': [], 'note': 'the resolvers.sustains_at_birth() calls find no sustained talent on these leaves (their talents are activated or passive)'},
                  {'identity': 'entrenched horror, swarm hive, venom wyrm, alchemist golem, greater mummy', 'sustained': [], 'note': 'no sustains_at_birth on the leaf or base'}],
              'auto_classes_review': [
                  {'identity': 'all twelve', 'class': 'none', 'finding': "none of the twelve leaves or their bases has auto_classes (the greater mummy lord leaf in the same file has one, the greater mummy does not); every auto_classes site in zones/, general/ and maps/ belongs to another leaf, so none can reach Flame of Urh'Rok and there is no urh_rok_form opt-in."}],
              'visibility_review': 'Identities with inscriptions, stealth or invisibility (shadowblade, orc elite fighter, orc elite berserker, orc summoner, greater mummy) can roll an invisibility rune/infusion or stealth that applies a shader effect while it lasts; the matcher rejects an actor with a shader (native art shows) and the token returns when it ends; token drawing follows actor visibility as for every other token.',
              'hits_in_batch': [],
              'no_hit': [i['native_name'] for i in identities]},
          'summons_and_same_body_copies': {
              'method': "grep of every actor definition, static map, quest script, vault, encounter, event and talent under game/modules/tome (data and class) for the twelve names and PNGs; talents that build summons/copies (summon-*, dreadmaster, master-of-flesh, master-of-bones, rot, thought-forms, simulacra/mirror images, Grand Arrival, golemancy, cloneFull users, hive summons) checked for copies of these bodies.",
              'findings': findings},
          'name_collisions_checked': [
              {'name': a['name'], 'other_definitions': (['zones/arena/npcs.lua:773 (arena shadowblade, no define_as, another base)'] if a['id'] == 'shadowblade' else ['none']),
               'outcome': ('single actor definition bound to define_as ' + a['define_as'] if a['define_as'] else ('unique actor definition without define_as; unique=true in the catalog entry' if a['unique'] else 'single actor definition without define_as; the catalog entry has no define_as and matches by exact name, type and subtype'))} for a in {x['id']: x for x in A}.values()],
          'kept_native': [],
          'neighbours_kept_native': [
              {'name': 'Training Dummy', 'reason': 'listed at 12.0 by the scoring script but kept native since batch T'},
              {'name': 'ruin banshee', 'reason': 'score 0.6, below this batch (the 0.7 tier fills the last three places)'},
              {'name': 'Aletta Soultorn', 'reason': 'score 0.6, unique, below this batch'}]}
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
                 'gate_reason': f"Exact source identity re-verified directly against game/modules/tome source (name={a['name']}, define_as={a['define_as']}, type={a['type']}/subtype={a['subtype']}, unique={a['unique']}, native_tall={a['native_tall']}); details and hashes in evidence/monster-batch-ab-20260930/source-contracts.json. {a['structure']}. Exact catalog entry only, never a whole-subtype mapping.",
                 'render_evidence': [{'path': render, 'sha256': evsha}]}
        if a.get('refinement'):
            entry['refinement'] = a['refinement']
        packs.setdefault(a['pack'], []).append(entry)
    for n, assets in packs.items():
        p = ADDON / f'art/production/batches/monster-batch-ab-{n}.json'
        if p.exists():
            print('exists, skipped', p.name)
            continue
        p.write_text(json.dumps({'schema': 1, 'batch_id': f'monster-batch-ab-{n}', 'assets': assets}, indent=2, ensure_ascii=False) + '\n')
        print('wrote', p.name)


if __name__ == '__main__':
    build()
