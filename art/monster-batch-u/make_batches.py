"""Generate the monster-batch-u task packs and the pinned source-contract
evidence (survey-2 unscheduled list after the 12.0 tier: naga tide huntress,
ancient elven mummy, ritch flamespitter/impaler, chitinous ritch, gaeramarth,
ninurlhing, orc master assassin, orc grand master assassin, fire imp, naga
psyren, fate weaver; see SELECTION.md). Pure bookkeeping: hashes native
sources/sprites, writes JSON and the composite family references. Retry packs
are appended by later edits of retries.py (never overwritten)."""
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
def R(family_id, note):
    return ('family', TOK + family_id + '.png', note)


def IDN(png, note):
    return ('identity', NPC + png, note)





# ---- shared strings ----
COMPACT = " Draw the creature COMPACT and chunky: limbs, weapons, tools, cloth and effects are pulled in so the whole silhouette forms one rounded mass inside the inner three quarters of the disc; no tip, blade, hat brim, tentacle end or tail reaches the outer sixth ring band or crosses the disc rim."
BRIGHT = " Value discipline (measured lesson from earlier tokens): the creature's large masses are MID-LIGHT to LIGHT in value, clearly LIGHTER than the charcoal disc, with broad pale highlight planes on every upper-left surface, so the silhouette reads as a bright shape on the dark disc at very small size. Nothing near-black except tiny eye slits and thin seams; no black cloth, black leather, black armour or black fur anywhere."
DEF = ' NPC.lua:33 default-name image (npc/<type>_<subtype>_<name>.png) is the only image source: no image=, nice_tile, add_mos, moddable_tile, shader, anim or add_displays on the leaf or base; generic actor.image==entry.image single path; native sprite 64x64'
EXPL = ' explicit image= on the leaf (no nice_tile, add_mos, moddable_tile, shader, anim or add_displays on the leaf or base); generic actor.image==entry.image single path; native sprite 64x64'
ZONE_RT, ZONE_MISC = 'zones/ritch-tunnels/npcs.lua', 'zones/unhallowed-morass/npcs.lua'
NAGA, DEMON, ORC, SPIDER, MUMMY = ('general/npcs/naga.lua', 'general/npcs/minor-demon.lua', 'general/npcs/orc.lua', 'general/npcs/spider.lua', 'general/npcs/mummy.lua')
ZONE_AER = 'zones/ancient-elven-ruins/npcs.lua'
REFS = HERE / 'refs'


def composite(name, ids, cols):
    """Side-by-side of shipped runtime tokens used as a 'do not become this' family reference."""
    from PIL import Image
    out = REFS / f'{name}.png'
    if out.exists():
        return 'game/addons/tome-checker-revised/art/monster-batch-u/refs/' + out.name
    REFS.mkdir(exist_ok=True)
    rows = (len(ids) + cols - 1) // cols
    canvas = Image.new('RGBA', (cols * 128, rows * 128), (0, 0, 0, 0))
    for i, id_ in enumerate(ids):
        canvas.alpha_composite(Image.open(ADDON / 'data/gfx/tokens' / f'{id_}.png').convert('RGBA'), ((i % cols) * 128, (i // cols) * 128))
    canvas.save(out)
    return 'game/addons/tome-checker-revised/art/monster-batch-u/refs/' + out.name


def RC(name, ids, cols, note):
    return ('family', composite(name, ids, cols), note)


REF_RITCH = RC('ritches', ['ritch-hive-mother', 'chitinous-spider'], 2,
               'Shipped ritch-hive-mother (orange-red crab-like radial body seen from above) and chitinous-spider (cream radial-legged spider): none of the new ritches may be a radial crab or a cream spider shape; each new ritch has its own distinct silhouette.')
REF_NAGAS = RC('nagas', ['naga-myrmidon', 'naga-tidewarden', 'naga-nereid', 'lady-zoisla', 'lady-nashva', 'naga-tidecaller', 'slasul'], 4,
               'Seven shipped naga tokens (blue-tailed myrmidon with a trident, brown tidewarden with a shield, yellow-tailed nereid with a crystal staff, red lady zoisla, teal lady nashva, grey tidecaller, green slasul): none of them carries a bow, and none has a white-silver tail or a violet spiral tail.')
REF_MUMMY = R('greater-mummy-lord', 'Shipped greater mummy lord (bulky gold-armoured bandaged warrior with a round shield and a sword): the ancient elven mummy must not be a bulky armoured shield bearer.')
REF_ORCS = RC('orcs', ['orc-assassin', 'orc-necromancer', 'orc-warrior', 'orc-soldier'], 2,
              'Four shipped orc tokens (hooded blue-grey orc assassin crouching with two curved daggers, hooded orc necromancer, orc warrior with a scimitar, spiked orc soldier): the two master assassins must not be a hooded crouching dagger orc.')
REF_IMPS = RC('imps', ['quasit', 'water-imp', 'wretchling', 'draebor'], 2,
              'Four shipped minor-demon tokens (bronze bull-headed quasit with a round shield, teal water imp, yellow-green crouching wretchling, white shaggy draebor crouching with a flame in one hand): the fire imp must not be any of these.')
REF_SPIDERS = RC('spiders', ['giant-spider', 'spitting-spider', 'fate-spinner', 'weaver-young', 'chitinous-spider', 'nimisil'], 3,
                 'Six shipped spider tokens (dark grey giant spider, brown spitting spider with green spit, steel-blue fate spinner with a silk ring, white swirl weaver young, cream chitinous spider, silver gem-crowned nimisil): the three new spiders must not be a plain grey, brown, blue, white-cream or silver spider and must not repeat their poses.')

DEMPTY = ' no resolvers.equip that touches the body; no sustains_at_birth and no auto_classes on the leaf or base'
SIGNAL = "the leaf and its base carry no image=/nice_tile/add_mos/moddable_tile/shader/anim/add_displays"

# ---- pack 1: ritches ----
asset(1, 'ritch-flamespitter', 'ritch flamespitter',
      "ritch-tunnels (zones/ritch-tunnels/npcs.lua:53, insect/ritch, non-unique, no define_as, rank 2, base BASE_NPC_RITCH_REL, default-name image); the only definition of this name in the zone/general npc lists. The Wild Gift 'Ritch Flamespitter' summon (talents/gifts/summon-distance.lua:446) builds another actor of the same name and type but with image=npc/summoner_ritch.png, a different native PNG (see summons_and_same_body_copies); the snake-pit vault (maps/vaults/snake-pit.lua:50) names it in a random mob list and builds this same leaf",
      [src(ZONE_RT, 'name = "ritch flamespitter"'), src(ZONE_RT, 'T_RITCH_FLAMESPITTER_BOLT', after='name = "ritch flamespitter"'),
       src('talents/gifts/summon-distance.lua', 'image = "npc/summoner_ritch.png"'), src('maps/vaults/snake-pit.lua', '"ritch flamespitter"')],
      src(ZONE_RT, 'define_as = "BASE_NPC_RITCH_REL"'), None, 'insect', 'ritch', False, False,
      'base BASE_NPC_RITCH_REL (insect/ritch, no image=, no shader);' + DEF + '; talents Ritch Flamespitter Bolt (activated); ' + DEMPTY,
      'insect_ritch_ritch_flamespitter.png',
      [STY, IDN('insect_ritch_ritch_flamespitter.png', 'Native shape (64x64): a scarlet-orange banded ritch (insect) on six legs spitting a stream of fire from its mandibles. Do not copy the long flame stream: keep the flame a small compact ball.'), REF_RITCH],
      "A ritch flamespitter seen from a steep overhead three-quarter angle: a giant insect with a glossy SCARLET-ORANGE carapace, an S-curved body REARED UP on its four hind legs so it stands tall and vertical, a swollen abdomen with bright CREAM-YELLOW zigzag bands, two big round AMBER compound eyes, short curled antennae, the two serrated foreclaws folded against its chest, and a small compact BALL OF ORANGE FIRE just leaving its open mandibles at the top of the pose (the fire ball no wider than its head, fully contained). Upright, tall, glossy and complete.",
      "Ritches: the FLAMESPITTER is the TALL VERTICAL one, an S-curved body reared up with a small fire ball at the top (silhouette: a tall narrow S-curve with a round flame at its head; hue: scarlet-orange with cream bands and orange fire; value: mid-light). The shipped ritch-hive-mother is a wide orange radial crab-shaped body seen from above and the chitinous-spider is a cream radial spider: this must not be a wide radial crab shape and must not lie flat. The other two new ritches are a low copper one thrusting a long lance-like claw diagonally (impaler) and a round golden armoured dome (chitinous).",
      "Scarlet-orange carapace in a mid-light value with pale orange highlight planes, cream-yellow abdomen bands, amber eyes, warm orange fire ball with a pale yellow core; nothing darker than dark red-brown except thin leg joints; the fire must stay on the creature and must not glow onto or tint the disc." + DISC,
      "READY single, no define_as (ritch flamespitter)", comp=COMP + FIT + COMPACT + BRIGHT)

asset(1, 'ritch-impaler', 'ritch impaler',
      "ritch-tunnels (zones/ritch-tunnels/npcs.lua:69, insect/ritch, non-unique, no define_as, rank 2, base BASE_NPC_RITCH_REL, default-name image); single definition; no talent, summon or vault builds another actor with this name",
      [src(ZONE_RT, 'name = "ritch impaler"'), src(ZONE_RT, 'T_RUSHING_CLAWS', after='name = "ritch impaler"')],
      src(ZONE_RT, 'define_as = "BASE_NPC_RITCH_REL"'), None, 'insect', 'ritch', False, False,
      'base BASE_NPC_RITCH_REL (insect/ritch);' + DEF + '; talents Rushing Claws (activated); ' + DEMPTY,
      'insect_ritch_ritch_impaler.png',
      [STY, IDN('insect_ritch_ritch_impaler.png', 'Native shape (64x64): a red banded ritch (insect) with one huge blade-like claw held up and out. Keep the one huge claw, but copper-brown and thrust forward.'), REF_RITCH],
      "A ritch impaler seen from a steep overhead three-quarter angle: a giant insect with a COPPER-BROWN glossy carapace and a low, streamlined body LUNGING forward along a diagonal, ONE enormous lance-like foreclaw of pale BONE-WHITE chitin with a needle tip thrust straight out along the diagonal (about the length of its own body but kept well inside the disc), the other foreclaw small and folded, a banded tapering abdomen with cream-tan stripes raised slightly behind, two amber eyes, short antennae, six thin dark-copper legs braced low. Low, forward-thrusting, sharp and complete.",
      "Ritches: the IMPALER is the LOW LONG DIAGONAL one, a copper body with one huge bone-white lance claw thrust forward (silhouette: a long diagonal line with a spear point; hue: copper-brown with bone-white lance and cream stripes; value: mid-light). The flamespitter is a tall scarlet S-curve with a fire ball and the chitinous ritch is a round golden dome; the shipped ritch-hive-mother is a wide orange radial crab: this must not be tall, not scarlet, not radial and not round.",
      "Copper-brown carapace in a mid-light value with pale copper highlight planes, bone-white lance claw with a bright highlight edge, cream-tan abdomen stripes, amber eyes; nothing darker than dark brown except thin leg joints; the disc stays neutral charcoal with no warm cast." + DISC,
      "READY single, no define_as (ritch impaler)", comp=COMP + FIT + COMPACT + BRIGHT)

asset(1, 'chitinous-ritch', 'chitinous ritch',
      "ritch-tunnels (zones/ritch-tunnels/npcs.lua:84, insect/ritch, non-unique, no define_as, rank 2, base BASE_NPC_RITCH_REL, default-name image); single definition; no talent, summon or vault builds another actor with this name",
      [src(ZONE_RT, 'name = "chitinous ritch"'), src(ZONE_RT, 'combat_armor = 6', after='name = "chitinous ritch"')],
      src(ZONE_RT, 'define_as = "BASE_NPC_RITCH_REL"'), None, 'insect', 'ritch', False, False,
      'base BASE_NPC_RITCH_REL (insect/ritch);' + DEF + '; no talents; ' + DEMPTY,
      'insect_ritch_chitinous_ritch.png',
      [STY, IDN('insect_ritch_chitinous_ritch.png', 'Native shape (64x64): a pale golden armoured ritch with thorny plates and horn-like claws.'), REF_RITCH],
      "A chitinous ritch seen from a steep overhead three-quarter angle: a heavy squat armoured giant insect with a broad rounded DOME-SHAPED carapace of overlapping GOLDEN-YELLOW chitin plates with darker amber edges and a row of short ridge spikes along the back, all six legs FOLDED tightly under the shell so it looks like a big armoured beetle, a small head tucked forward with two amber eyes, and two short curved pale-ivory HORN-CLAWS in front. Round, plated, heavy and complete.",
      "Ritches: the CHITINOUS one is a ROUND GOLDEN ARMOURED DOME with folded legs and two short horn claws (silhouette: one round plated shell like a beetle or armadillo; hue: golden yellow with amber edges and ivory horns; value: light). The flamespitter is a tall scarlet S-curve and the impaler is a low copper lance-thruster; the shipped ritch-hive-mother is an orange radial crab and the chitinous-spider is a cream radial-legged spider: this must not show spread radial legs and must not be cream-white.",
      "Golden-yellow plates in a light value with pale butter highlight planes on the upper-left and darker amber plate edges, ivory horn-claws, amber eyes; nothing darker than dark amber-brown except thin seams; the disc stays neutral charcoal with no yellow cast." + DISC,
      "READY single, no define_as (chitinous ritch)", comp=COMP + FIT + COMPACT + BRIGHT)

# ---- pack 2: nagas and the elven mummy ----
asset(2, 'naga-tide-huntress', 'naga tide huntress',
      "general npc list (general/npcs/naga.lua:73, humanoid/naga, non-unique, no define_as, rank 3, base BASE_NPC_NAGA, explicit image=npc/naga_tide_huntress.png); loaded by temple-of-creation (zones/temple-of-creation/npcs.lua:22), high-peak, the naga-portal event and the water-vault/flooded-prison vaults; the Arena generator names it (class/generator/actor/Arena.lua:167); one definition everywhere",
      [src(NAGA, 'name = "naga tide huntress"'), src(NAGA, 'image="npc/naga_tide_huntress.png"', after='name = "naga tide huntress"'),
       src('zones/temple-of-creation/npcs.lua', 'load("/data/general/npcs/naga.lua", rarity(0))'), src('class/generator/actor/Arena.lua', 'name = "naga tide huntress"', root=D.replace('data/', ''))],
      src(NAGA, 'define_as = "BASE_NPC_NAGA"'), None, 'humanoid', 'naga', False, False,
      'base BASE_NPC_NAGA (humanoid/naga, no image=; the murgol-lair and slazish-fen zone files redefine BASE_NPC_NAGA for their own leaves and are not loaded with general/npcs/naga.lua);' + EXPL + '; resolvers.racial() (naga has no racials entry: nothing added), resolvers.equip longbow and arrows (equipment only, no moddable_tile), resolvers.inscriptions(1, infusion/rune); talents Spit Poison, Water Jet, Water Bolt, Shoot, Weapon Combat, Bow Mastery (none sustained); no sustains_at_birth and no auto_classes',
      'naga_tide_huntress.png',
      [STY, IDN('naga_tide_huntress.png', 'Native shape (64x64): a blonde female naga drawing a longbow over a blue serpent tail. Keep the bow-drawing archer, but with a white-silver tail and a short compact bow.'), REF_NAGAS],
      "A naga tide huntress seen from a steep overhead three-quarter angle: a slender young female naga whose torso rises from a tight flat coil of a long serpent tail covered in PALE ICE-BLUE and WHITE-SILVER scales with a bright pearly belly, a long SILVER-WHITE braid over one shoulder, a teal-green leather cuirass, the arms DRAWING a short recurve bow diagonally (the bow no taller than her torso, drawn to the cheek) with a nocked arrow tipped by a small clear ICE CRYSTAL pointing to the upper right, a narrow cold determined face with pale ice-blue eyes, a quiver of pale feathered arrows on her back. Poised, cold, bow-drawn and complete.",
      "Nagas: the TIDE HUNTRESS is a female ARCHER, the only one drawing a BOW (silhouette: a coiled tail base, an upright torso and a diagonal bow with a nocked arrow; hue: white-silver and ice-blue tail, teal cuirass, silver braid; value: light). The shipped nagas hold tridents, staffs or shields and have blue, brown, yellow, red, teal, grey or green tails: this must not hold a trident or staff, and the tail must be pale white-silver, not a saturated blue or yellow. The psyren is a violet-tailed spiral figure with an orb and flowing hair, no bow.",
      "White-silver and pale ice-blue scales in a light value with bright pearly highlight planes and soft blue-grey shadows, silver braid, teal-green cuirass in a mid value, pale wood bow with a bright tip, clear ice-crystal arrowhead; nothing darker than mid teal except the eyes and thin seams; the ice glint must not tint the disc." + DISC,
      "READY single, no define_as (naga tide huntress)", comp=COMP + FIT + COMPACT + BRIGHT)

asset(2, 'naga-psyren', 'naga psyren',
      "general npc list (general/npcs/naga.lua:102, humanoid/naga, non-unique, no define_as, rank 3, base BASE_NPC_NAGA, explicit image=npc/naga_psyren.png); loaded by temple-of-creation, high-peak, the naga-portal event and vaults; the Arena generator names it (class/generator/actor/Arena.lua:179); one definition everywhere",
      [src(NAGA, 'name = "naga psyren"'), src(NAGA, 'image="npc/naga_psyren.png"', after='name = "naga psyren"'),
       src('zones/temple-of-creation/npcs.lua', 'load("/data/general/npcs/naga.lua", rarity(0))'), src('class/generator/actor/Arena.lua', 'name = "naga psyren"', root=D.replace('data/', ''))],
      src(NAGA, 'define_as = "BASE_NPC_NAGA"'), None, 'humanoid', 'naga', False, False,
      'base BASE_NPC_NAGA (humanoid/naga);' + EXPL + '; resolvers.racial() (nothing added), resolvers.equip trident (equipment only), resolvers.inscriptions(1, infusion/rune); talents Mind Disruption, Mind Sear, Silence, Telekinetic Blast (none sustained); no sustains_at_birth and no auto_classes',
      'naga_psyren.png',
      [STY, IDN('naga_psyren.png', 'Native shape (64x64): a blonde female naga with a glowing purple orb in her hand over a blue serpent tail. Keep the orb-casting siren, but with a violet spiral tail and flowing rose hair.'), REF_NAGAS],
      "A naga psyren seen from a steep overhead three-quarter angle: an ethereal female naga whose serene torso rises from a tail coiled in a tight RISING SPIRAL of pearlescent MAGENTA-VIOLET and pale pink scales with a cream belly, long flowing ROSE-PINK hair spreading out to both sides like soft wings, a pearl-and-gold shell bodice, closed eyes and a faint smile, both hands raised and cupped in front of the chest around a glowing PURPLE-WHITE psychic ORB the size of her head (its glow contained, a few tiny pale motes only). Serene, spiralled, ethereal and complete.",
      "Nagas: the PSYREN is a SPIRAL-TAILED siren with flowing hair wings and a glowing orb in both raised hands (silhouette: a rising spiral column with a wide hair spread and a round orb at chest height; hue: magenta-violet tail, rose hair, pearl and gold, purple-white orb; value: mid-light). The shipped nereid has a yellow tail and blonde hair with a crystal staff, myrmidon a blue tail with a trident, nashva a teal water figure: this must not hold a weapon or staff, and its tail must be violet-magenta. The tide huntress is a white-silver archer with a bow.",
      "Magenta-violet and pale pink scales in a mid-light value with pearly highlight planes, rose-pink hair in a mid-light value, cream belly, pearl-and-gold bodice, purple-white orb with a bright core; nothing darker than mid violet except the eyes and thin seams; the orb glow must stay on the creature and must not tint the disc." + DISC,
      "READY single, no define_as (naga psyren)", comp=COMP + FIT + COMPACT + BRIGHT)

asset(2, 'ancient-elven-mummy', 'ancient elven mummy',
      "ancient-elven-ruins (zones/ancient-elven-ruins/npcs.lua:107, undead/mummy, non-unique, no define_as, rank 2, base BASE_NPC_MUMMY from general/npcs/mummy.lua, default-name image); the only definition of this name; the general mummy list (loaded by infinite-dungeon and ruined-dungeon) does not contain it",
      [src(ZONE_AER, 'name = "ancient elven mummy"'), src(ZONE_AER, 'T_CRUSH', after='name = "ancient elven mummy"'),
       src(ZONE_AER, 'load("/data/general/npcs/mummy.lua", rarity(0))')],
      src(MUMMY, 'define_as = "BASE_NPC_MUMMY"'), None, 'undead', 'mummy', False, False,
      'base BASE_NPC_MUMMY (undead/mummy, no image=);' + DEF + '; resolvers.racial("shalore") only adds levelup talents, resolvers.equip greatsword and mummy armour (equipment only, no moddable_tile), resolvers.inscriptions(2, rune); talents Stunning Blow, Crush, Manathrust (none sustained); no sustains_at_birth and no auto_classes',
      'undead_mummy_ancient_elven_mummy.png',
      [STY, IDN('undead_mummy_ancient_elven_mummy.png', 'Native shape (64x64): a slender bandaged mummy in pale wrappings standing with arms hanging slightly forward.'), REF_MUMMY],
      "An ancient elven mummy seen from a steep overhead three-quarter angle: a gaunt, tall-and-slender elven corpse wrapped from head to foot in aged CREAM and pale TAN linen bandages, two long POINTED ELF EARS poking out through the wrappings on the sides of the head, a thin tarnished GOLD circlet across the brow holding a small JADE-GREEN leaf gem, glowing pale JADE-GREEN eye sockets, both arms stretched STIFFLY FORWARD at chest height with ragged bandage strips trailing from the wrists and hem, a short narrow stance in a slow shuffling stride, small gold arm rings. Gaunt, elegant, ancient and complete, no weapon, no shield, no armour plates.",
      "Undead mummies: the ANCIENT ELVEN MUMMY is a GAUNT SLENDER figure with POINTED EARS, a gold-and-jade circlet and both arms stretched forward with trailing bandage ends, no weapon or shield (silhouette: a narrow vertical figure with two ear points and forward arms; hue: cream and tan wrappings with gold and jade green accents; value: light). The shipped greater mummy lord is a bulky gold-armoured bandaged warrior with a round shield and a sword: this must not be bulky, armoured, crowned with horns or holding a shield.",
      "Cream and pale tan bandages in a light value with bright highlight planes on the upper-left folds and soft warm-grey shadows, tarnished gold circlet and rings, jade-green gem and eye glow (small), nothing darker than mid warm grey except the eye sockets and thin seams; the eye glow must not tint the disc." + DISC,
      "READY single, no define_as (ancient elven mummy)", comp=COMP + FIT + COMPACT + BRIGHT)

# ---- pack 3: orc assassins and the fire imp ----
asset(3, 'orc-master-assassin', 'orc master assassin',
      "general npc list (general/npcs/orc.lua:204, humanoid/orc, non-unique, no define_as, rank 3, base BASE_NPC_ORC, default-name image); loaded by reknor, vor-armoury, rak-shor-pride and others; the orc-armoury vault names it in a random_filter (maps/vaults/auto/greater/orc-armoury.lua:43) and builds this same leaf; one definition",
      [src(ORC, 'name = "orc master assassin"'), src(ORC, 'resolvers.sustains_at_birth()', after='name = "orc master assassin"'),
       src('maps/vaults/auto/greater/orc-armoury.lua', "name='orc master assassin'")],
      src(ORC, 'define_as = "BASE_NPC_ORC"'), None, 'humanoid', 'orc', False, False,
      'base BASE_NPC_ORC (humanoid/orc, faction orc-pride, no image=);' + DEF + '; color_r/g/b tint fields only; resolvers.racial() (orc racials: Orc Fury, Hold the Ground, Skirmisher, Pride of the Orcs, levelup talents only), resolvers.equip two daggers and light armour (equipment only, no moddable_tile), resolvers.inscriptions(1, infusion); talents Knife Mastery, Stealth (sustained), Lethality, Apply Poison (sustained), Vile Poisons, Venomous Strike; resolvers.sustains_at_birth() starts Stealth and Apply Poison (temporary values only, no type/subtype/image/add_mos write); no auto_classes',
      'humanoid_orc_orc_master_assassin.png',
      [STY, IDN('humanoid_orc_orc_master_assassin.png', 'Native shape (64x64): an olive-green orc in wrapped bands crouching with two daggers, dark and swarthy. Do NOT copy its dark tones: keep the same green skin but with light sky-blue and cream wrappings.'), REF_ORCS],
      "An orc master assassin seen from a steep overhead three-quarter angle: a lean muscular OLIVE-GREEN orc standing FACING THE VIEWER in a wide low stance, BARE-HEADED with shaved sides and a tall RED-BROWN TOPKNOT (no hood, no helmet), small tusks, narrow yellow eyes, a cream leather vest with layered SKY-BLUE cloth wraps on the forearms and shins, a pale leather sash, and TWO long steel daggers held CROSSED IN AN X in front of the chest with their blades pointing up and out (the crossed blades stay within the shoulder width). Compact, poised, lethal and complete.",
      "Orc assassins: the MASTER ASSASSIN is a BARE-HEADED TOPKNOT orc facing the viewer with two daggers CROSSED in an X in front of the chest (silhouette: a compact upright body with an X of blades; hue: olive-green skin with sky-blue and cream wraps and a red-brown topknot; value: mid-light). The shipped orc-assassin is a HOODED blue-grey orc CROUCHING sideways with curved daggers held low: this must not be hooded, not blue-grey clothes and not a side crouch. The grand master is a taller ivory-masked figure with arms spread wide and the blades pointing outward and down.",
      "Olive-green skin in a mid-light value with pale green highlight planes, cream vest and sky-blue wraps in a light value, pale leather sash, red-brown topknot, bright polished steel daggers; nothing darker than dark olive-brown except the eyes and thin seams; the disc stays neutral charcoal with no blue or green cast." + DISC,
      "READY single, no define_as (orc master assassin)", comp=COMP + FIT + COMPACT + BRIGHT)

asset(3, 'orc-grand-master-assassin', 'orc grand master assassin',
      "general npc list (general/npcs/orc.lua:240, humanoid/orc, non-unique, no define_as, rank 3, base BASE_NPC_ORC, default-name image); loaded by reknor, vor-armoury, rak-shor-pride and others; the orc-armoury and orc-hatred vaults name it in random_filters (orc-armoury.lua:44, orc-hatred.lua:74) and build this same leaf; one definition",
      [src(ORC, 'name = "orc grand master assassin"'), src(ORC, 'resolvers.sustains_at_birth()', after='name = "orc grand master assassin"'),
       src('maps/vaults/auto/greater/orc-hatred.lua', 'name = "orc grand master assassin"')],
      src(ORC, 'define_as = "BASE_NPC_ORC"'), None, 'humanoid', 'orc', False, False,
      'base BASE_NPC_ORC (humanoid/orc, faction orc-pride);' + DEF + '; color_r/g/b tint fields only; resolvers.racial() (orc levelup talents only), resolvers.equip two daggers and light armour (equipment only), resolvers.inscriptions(3, infusion); talents Knife Mastery, Stealth (sustained), Lethality, Deadly Strikes, Shadow Dance, Apply Poison (sustained), Vile Poisons, Venomous Strike; resolvers.sustains_at_birth() starts Stealth and Apply Poison (temporary values only, no type/subtype/image/add_mos write); no auto_classes',
      'humanoid_orc_orc_grand_master_assassin.png',
      [STY, IDN('humanoid_orc_orc_grand_master_assassin.png', 'Native shape (64x64): a dark olive orc with tattered loincloth and many blades. Do NOT copy its dark tones: use an ivory mask and pale teal-green cloth.'), REF_ORCS],
      "An orc grand master assassin seen from a steep overhead three-quarter angle: a tall, upright, lean orc standing FACING THE VIEWER with both arms SPREAD WIDE and two long curved steel blades pointing OUTWARD AND DOWN so the pose forms a wide A shape, wearing an IVORY-WHITE BONE MASK with two short curved horns and narrow eye slits, pale steel spiked SHOULDER PAULDRONS, a light TEAL-GREEN cloth cowl and a long pale teal tabard with a tattered hem hanging between the legs, layered bone-white forearm guards, olive-green skin visible on the arms. Tall, masked, wide and complete.",
      "Orc assassins: the GRAND MASTER is a TALL IVORY-MASKED figure with ARMS SPREAD WIDE and two blades pointing outward and down (silhouette: an upright body with a wide A of arms and blades, small horns on the head; hue: ivory mask and guards, pale teal cloth, steel spikes; value: light). The master assassin is a bare-headed topknot orc with two crossed daggers in front of the chest, and the shipped orc-assassin is a hooded blue-grey orc crouching sideways: this must not be crouching, not hooded, not crossed daggers and not blue-grey.",
      "Ivory-white mask and guards in a light value with bright highlight planes, pale teal-green cloth in a mid-light value, pale steel spikes and blades with bright edges, olive-green arms in a mid value; nothing darker than dark teal-grey except the eye slits and thin seams; the disc stays neutral charcoal with no green cast." + DISC,
      "READY single, no define_as (orc grand master assassin)", comp=COMP + FIT + COMPACT + BRIGHT)

asset(3, 'fire-imp', 'fire imp',
      "general npc list (general/npcs/minor-demon.lua:47, demon/minor, non-unique, no define_as, rank 2, base BASE_NPC_DEMON, default-name image); loaded by valley-moon-caverns, demon-plane, crypt-kryl-feijan, ardhungol (via all.lua) and the fearscape-portal event; the antimagic quest (quests/antimagic.lua:90) and the dragon-loot and lava-island vaults name it and build this same leaf; one definition",
      [src(DEMON, 'name = "fire imp"'), src(DEMON, 'T_RITCH_FLAMESPITTER_BOLT', after='name = "fire imp"'),
       src('quests/antimagic.lua', '{name="fire imp"}'), src('maps/vaults/lava_island.lua', 'name="fire imp"')],
      src(DEMON, 'define_as = "BASE_NPC_DEMON"'), None, 'demon', 'minor', False, False,
      'base BASE_NPC_DEMON (demon/minor, faction fearscape, no image=);' + DEF + '; talents Ritch Flamespitter Bolt, Phase Door (neither sustained); ' + DEMPTY,
      'demon_minor_fire_imp.png',
      [STY, IDN('demon_minor_fire_imp.png', 'Native shape (64x64): a thin rust-brown imp with glowing hands, holding fire. Keep the small fire-throwing imp, but scarlet, winged and with both arms raised.'), REF_IMPS],
      "A fire imp seen from a steep overhead three-quarter angle: a small wiry SCARLET-RED imp with a big head, two curved CHARCOAL-DARK-GREY horns with pale tips, glowing yellow eyes and a toothy grin, small folded leathery batwings in a lighter red-orange on its back, BOTH ARMS RAISED HIGH over its head hurling a compact round BALL OF ORANGE FIRE held between the hands, thin legs in a light hop, and a long thin curled tail whose tip ends in a small flame. Lively, wiry, fire-throwing and complete.",
      "Minor demons: the FIRE IMP is a small SCARLET winged imp with BOTH ARMS RAISED throwing a fire ball overhead (silhouette: a Y-shaped body with raised arms, a round fire ball above and a curled tail with a flame tip; hue: scarlet red, orange fire, charcoal horns, yellow eyes; value: mid-light). The shipped quasit is a bronze bull-headed shield bearer, the water imp is teal, the wretchling is a yellow-green crouching crawler and draebor is a white shaggy crouching imp with one flame hand: this must not be crouching, not white, not teal and not holding a shield.",
      "Scarlet-red skin in a mid-light value with pale red-orange highlight planes, orange-red batwings, orange fire ball with a pale yellow core, charcoal-grey horns with pale tips, yellow eyes; nothing darker than mid charcoal-grey except thin seams; the fire must stay on the creature and must not glow onto or tint the disc." + DISC,
      "READY single, no define_as (fire imp)", comp=COMP + FIT + COMPACT + BRIGHT)

# ---- pack 4: spiders ----
asset(4, 'gaeramarth', 'gaeramarth',
      "general npc list (general/npcs/spider.lua:101, spiderkin/spider, non-unique, no define_as, rank 2, base BASE_NPC_SPIDER, default-name image); loaded by ardhungol (zones/ardhungol/npcs.lua:20), all.lua and several vaults; one definition",
      [src(SPIDER, 'name = "gaeramarth"'), src(SPIDER, 'T_STEALTH', after='name = "gaeramarth"'),
       src('zones/ardhungol/npcs.lua', 'load("/data/general/npcs/spider.lua", rarity(0))')],
      src(SPIDER, 'define_as = "BASE_NPC_SPIDER"'), None, 'spiderkin', 'spider', False, False,
      'base BASE_NPC_SPIDER (spiderkin/spider, no image=; the base has resolvers.sustains_at_birth());' + DEF + '; talents Rush, Spider Web, Lay Web, Stealth (sustained), Stun; resolvers.sustains_at_birth() starts Stealth (temporary values only, no type/subtype/image/add_mos write); resolvers.inscriptions(2, infusion); no auto_classes',
      'spiderkin_spider_gaeramarth.png',
      [STY, IDN('spiderkin_spider_gaeramarth.png', 'Native shape (64x64): a grey and black striped spider with a rounded abdomen and long legs. Keep the pale-ash coloured spider but rear the front legs up.'), REF_SPIDERS],
      "A gaeramarth seen from a steep overhead three-quarter angle: a large spider in pale ASH-GREY and BONE-WHITE with a rounded abdomen carrying an IVORY SKULL-LIKE marking outlined in charcoal grey, a broad cream head with a cluster of small glossy dark eyes and two curved ivory fangs, its TWO LONG FRONT LEGS REARED HIGH in the air in a threatening rush pose while the six other legs stay tucked close and bent around the body (the raised legs pulled well inside the disc), fine pale hairs. Threatening, pale, reared and complete.",
      "Spiders: the GAERAMARTH is a PALE ASH and BONE-WHITE spider with an ivory skull marking and its TWO FRONT LEGS REARED UP (silhouette: a compact body with a raised pair of front legs forming a V above the head; hue: ash-grey, bone-white and ivory; value: light). The shipped giant spider is a dark grey flat spider, the spitting spider is brown, the fate spinner is steel-blue with a silk ring, the weaver young a white swirl ball, the chitinous spider cream with radial legs, nimisil a silver gem-crowned spider: this must not be flat with all legs radial and must not be dark grey.",
      "Pale ash-grey and bone-white in a light value with bright highlight planes and soft blue-grey shadows, ivory skull marking with charcoal-grey outline, cream fangs; nothing darker than mid charcoal-grey except the eyes; the disc stays neutral charcoal and must not be brightened by the pale body." + DISC,
      "READY single, no define_as (gaeramarth)", comp=COMP + FIT + COMPACT + BRIGHT)

asset(4, 'ninurlhing', 'ninurlhing',
      "general npc list (general/npcs/spider.lua:127, spiderkin/spider, non-unique, no define_as, rank 2, base BASE_NPC_SPIDER, default-name image); loaded by ardhungol, all.lua and several vaults; the tutorial zone reuses its PNG for a differently named actor (zones/tutorial-combat-stats/npcs.lua:444, 'hairy spider', TUT_SPIDER_3) which stays native by name; one definition of the name ninurlhing",
      [src(SPIDER, 'name = "ninurlhing"'), src(SPIDER, 'T_ACIDIC_SKIN', after='name = "ninurlhing"'),
       src('zones/tutorial-combat-stats/npcs.lua', 'image="npc/spiderkin_spider_ninurlhing.png"')],
      src(SPIDER, 'define_as = "BASE_NPC_SPIDER"'), None, 'spiderkin', 'spider', False, False,
      'base BASE_NPC_SPIDER (spiderkin/spider, sustains_at_birth in the base);' + DEF + '; talents Rush, Spider Web, Lay Web, Acidic Skin (sustained), Corrosive Vapour, Crawl Acid, Stun; resolvers.sustains_at_birth() starts Acidic Skin (temporary values and a damage callback only, no type/subtype/image/add_mos write); resolvers.inscriptions(2, infusion); no auto_classes',
      'spiderkin_spider_ninurlhing.png',
      [STY, IDN('spiderkin_spider_ninurlhing.png', 'Native shape (64x64): a sickly cream-green spider with a round pink-striped abdomen. Keep the sickly acidic look and add drips and a little vapour.'), REF_SPIDERS],
      "A ninurlhing seen from a steep overhead three-quarter angle: a squat spider with a hugely swollen, glossy, half-translucent SICKLY LIME-GREEN and BUTTER-YELLOW abdomen with pink-orange stripes and small CORRODED HOLES weeping bright green acid drops that drip down its sides, a pale yellow-green head with two glowing green eyes and short fangs, EIGHT SHORT STOUT LEGS in pale olive-cream splayed wide to the sides like a crab, and a small puff of pale green VAPOUR rising from the back of the abdomen (compact, no bigger than the head). Bloated, acidic, dripping and complete.",
      "Spiders: the NINURLHING is a SQUAT BLOATED spider with a huge glossy lime-green and yellow abdomen, dripping acid and short legs splayed wide (silhouette: one big round bloated abdomen on a wide low crab-like splay, with small drips and a vapour puff; hue: lime green, butter yellow and pink-orange stripes; value: light). The shipped spitting spider is a brown long-legged spider spitting green liquid, the giant spider is dark grey, the chitinous spider is a cream armoured spider: this must not be brown, not long-legged and not a spitter.",
      "Lime-green and butter-yellow abdomen in a light value with bright highlight planes and a translucent glow, pink-orange stripes, bright acid-green drops, pale olive-cream legs; nothing darker than mid olive-green except the eyes and thin seams; the acid glow must stay on the creature and must not tint the disc." + DISC,
      "READY single, no define_as (ninurlhing)", comp=COMP + FIT + COMPACT + BRIGHT)

asset(4, 'fate-weaver', 'fate weaver',
      "unhallowed-morass (zones/unhallowed-morass/npcs.lua:102, spiderkin/spider, non-unique, no define_as, rank 2, base BASE_NPC_SPIDER as redefined in the zone file (no sustains_at_birth), default-name image); the only definition of this name; general/npcs/spider.lua only has a comment 'Fate Weavers; temporal spiders' (spider.lua:239)",
      [src(ZONE_MISC, 'name = "fate weaver"'), src(ZONE_MISC, 'T_FATEWEAVER', after='name = "fate weaver"'),
       src(SPIDER, 'Fate Weavers; temporal spiders')],
      src(ZONE_MISC, 'define_as = "BASE_NPC_SPIDER"'), None, 'spiderkin', 'spider', False, False,
      'base BASE_NPC_SPIDER as redefined in the zone file (spiderkin/spider, no image=, no sustains_at_birth);' + DEF + '; talents Spin Fate (passive), Webs of Fate, Fateweaver (passive), Rethread (activated, no sustained talent); ' + DEMPTY,
      'spiderkin_spider_fate_weaver.png',
      [STY, IDN('spiderkin_spider_fate_weaver.png', 'Native shape (64x64): a large white-lavender hairy spider. Keep the white-lavender fuzzy spider and add a golden clock marking and thread.'), REF_SPIDERS],
      "A fate weaver seen from a steep overhead three-quarter angle: a large fluffy spider with a thick coat of CREAM-WHITE and pale LAVENDER-VIOLET fur, a round abdomen carrying a bright GOLDEN CLOCK-FACE marking with a small hourglass in its centre, a lavender head with several small glowing pale-violet eyes, its two front legs held forward in front of the head weaving a compact CAT'S-CRADLE loop of glowing GOLDEN THREAD between them (the loop no wider than the head), the other six fluffy legs folded neatly around the body in a tight ring. Calm, fluffy, golden-threaded and complete.",
      "Spiders: the FATE WEAVER is a FLUFFY CREAM-WHITE and LAVENDER spider with a GOLDEN CLOCK-FACE on its abdomen and a small golden thread cat's-cradle held between its front legs (silhouette: a round fluffy body with a small forward loop; hue: cream-white, lavender and gold; value: light). The shipped fate spinner is a steel-blue spider with long serrated legs and a large silk ring at the side, weaver young is a white-blue swirl ball: this must not be steel blue, not serrated long-legged and must carry the gold clock face.",
      "Cream-white and lavender fur in a light value with bright highlight planes and soft violet-grey shadows, bright gold clock-face and thread, pale violet eyes; nothing darker than mid violet-grey except the eyes; the disc stays neutral charcoal and must not be brightened by the pale fur, the gold thread must not glow onto the disc." + DISC,
      "READY single, no define_as (fate weaver)", comp=COMP + FIT + COMPACT + BRIGHT)


def retry(id_, pack, **changes):
    base = next(a for a in A if a['id'] == id_)
    A.append(dict(base, pack=pack, **changes))


# ---- retry packs are appended below by later edits of retries.py ----
exec((HERE / 'retries.py').read_text()) if (HERE / 'retries.py').exists() else None

EXPL_IDS = ('naga-tide-huntress', 'naga-psyren')
PNGF = {a['id']: 'NPC.lua:33 default-name image on the leaf (no image=/nice_tile)' for a in A}
PNGF.update({i: 'explicit image= on the leaf (no nice_tile/add_mos)' for i in EXPL_IDS})


def build():
    packs = {}
    identities = []
    render = 'game/addons/tome-checker-revised/evidence/monster-batch-u-20260930/source-contracts.json'
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
    summoner_size = None
    with Image.open(WS / (NPC + 'summoner_ritch.png')) as im:
        summoner_size = list(im.size)
    findings = [

                  "All twelve names have exactly one leaf definition. Vaults (snake-pit, orc-armoury, orc-hatred, lava-island, dragon-loot), the antimagic quest, the Arena generator, the naga-portal and fearscape-portal events only build those same leaves through random_filter/name lookups, so they are the very same actors; random bosses made from them go through the existing captureRandomOrigin path.",
                  "Ritch Flamespitter (Wild Gift summon, talents/gifts/summon-distance.lua:446, renamed to '<name> (wild summon)' with the wild_summon attribute) builds an NPC with type insect, subtype ritch and the name 'ritch flamespitter' but image = npc/summoner_ritch.png (%dx%d, a different native drawing without the flame stream), and its own fields (summoner, ai summoned, wild_gift_summon, summoner_gain_exp). appearance() compares actor.image with the entry image, so it resolves to body-changed and the summon keeps its native art. A per-construct variant cannot express this (variants only relax the define_as check, never the image), so NO variants entry and no wild_summon_ids entry is added; this is reported as an open question rather than widened here.",
                  "The tutorial zone's 'hairy spider' (TUT_SPIDER_3) borrows spiderkin_spider_ninurlhing.png but has another name and define_as, so it stays native.",
                  "No other summon, clone or same-body construct exists for the other eleven names; Draebor-style summon={type=demon} pools draw generic demons from the level pool, which can include the fire imp as the very same leaf.",
                  "Result: no per-construct `variants` entry is needed for this batch."
    ]
    findings = [f % tuple(summoner_size) if '%dx%d' in f else f for f in findings]
    ev = {'schema': 1,
          'task': "monster-batch-u: static re-verification (no game launch) of the twelve identities that follow the finished 12.0 story tier in the survey-2 unscheduled list (naga tide huntress, ancient elven mummy, ritch flamespitter, chitinous ritch, gaeramarth, ninurlhing, orc master assassin, fire imp, ritch impaler, orc grand master assassin, naga psyren, fate weaver) against game/modules/tome source and native sprites. Every field below was read from source: name, type/subtype, define_as (none: all twelve are define_as-less non-unique leaves), explicit or NPC.lua:33 default image, unique, PNG on disk (all 64x64), and absence of moddable_tile/shader/anim/add_displays/nice_tile/add_mos on each leaf and its base. Findings: ten identities use the NPC.lua:33 default-name image, the two nagas name their PNG explicitly with image=; no identity is a tall body (no native_tall flag anywhere); none is unique. The Ritch Flamespitter Wild Gift summon has the same name and type but another native PNG (summoner_ritch.png), so it is a different native body and stays native (open question in summons_and_same_body_copies). No identity can reach Flame of Urh'Rok (no Corruptor auto_class), so no urh_rok_form opt-in is added.",
          'new_ids_not_in_catalog_before_this_batch': [i['id'] for i in identities], 'identities': identities,
          'runtime_mutation_scan': {
              'method': "every talent of each identity (resolvers.talents, inherited base talents, racial levelup talents and the base-file talent lists) was resolved under game/modules/tome/data/talents and its mode read (sustained/activated/passive); the whole talents/, timed_effects/, birth/ and class/ trees were grepped for writes to type/subtype/image/add_mos/add_displays/moddable_tile/replace_display/shader (regex on any receiver, plus the tuple assignment form) and the results reviewed line by line, giving the same writer set as batches S and T; the resolvers sustains_at_birth, racial, inscriptions, equip and nice_tile and the base-file resolvers were read; every auto_classes site under zones/ and general/ was grepped for Corruptor and Flame of Urh'Rok.",
              'writers_found': [
                  {'file': 'game/modules/tome/data/talents/corruptions/shadowflame.lua', 'line': 97, 'talent': "Flame of Urh'Rok", 'effect': 'sustain: __old_type={type,subtype}; type,subtype = demon,major; image untouched; restored on deactivate'},
                  {'file': 'game/modules/tome/data/talents/psionic/thought-forms.lua', 'line': 92, 'talent': 'thought-form summons (Solipsist tree)', 'effect': 'sets type/subtype/image/moddable_tile/add_mos on the summoned minion copied from its summoner, never on the caster'},
                  {'file': 'game/modules/tome/data/talents/chronomancy/anomalies.lua', 'line': 587, 'talent': 'anomaly summons', 'effect': 'creates a separate spawned NPC with another image; not the caster'}],
              'timed_effects_review': "timed_effects write shader, replace_display, add_displays or image only while active (invisibility shaders, stone/ice/pin displays, Wrathroot, Shivgoroth form, dragon egg): the matcher rejects them (native art) until they end; none is applied at birth to these identities.",
              'sustains_at_birth_review': [
                  {'identity': 'orc master assassin', 'sustained': ['Stealth', 'Apply Poison'], 'note': 'the leaf calls resolvers.sustains_at_birth(); temporary values and callbacks only, no type/subtype/image/add_mos/shader write'},
                  {'identity': 'orc grand master assassin', 'sustained': ['Stealth', 'Apply Poison'], 'note': 'same as the master assassin (Shadow Dance and Deadly Strikes are activated talents)'},
                  {'identity': 'gaeramarth', 'sustained': ['Stealth (started by the base BASE_NPC_SPIDER resolvers.sustains_at_birth)'], 'note': 'temporary values only'},
                  {'identity': 'ninurlhing', 'sustained': ['Acidic Skin (started by the base BASE_NPC_SPIDER resolvers.sustains_at_birth)'], 'note': 'temporary values and a damage callback only'},
                  {'identity': 'fate weaver', 'sustained': [], 'note': "the zone-file BASE_NPC_SPIDER has no sustains_at_birth and the leaf has no sustained talent"},
                  {'identity': 'naga tide huntress, naga psyren, ancient elven mummy, fire imp, ritch flamespitter, ritch impaler, chitinous ritch', 'sustained': [], 'note': 'no sustains_at_birth on the leaf or base and no sustained talent'}],
              'auto_classes_review': [
                  {'identity': 'all twelve', 'class': 'none', 'finding': "none of the twelve leaves or their bases has auto_classes (only the Ritch Great Hive Mother in the same zone file does, Summoner class); the zone-wide grep for Corruptor and Flame of Urh'Rok found only zones/rhaloren-camp, ruins-kor-pul, dreadfell, mark-spellblaze, general/events/cultists.lua and general/npcs/elven-caster.lua (already-mapped identities or other names), and general/npcs/minor-demon.lua:113 only sets an auto_equip filter on another leaf, not on the fire imp.", 'outcome': "no hit: Flame of Urh'Rok is not reachable, so urh_rok_form is NOT set on any entry; the opt-in count stays 5"}],
              'visibility_review': 'Every identity with inscriptions (nagas, mummy, orcs, spiders) can roll an invisibility rune/infusion that applies a transient invis_edge shader through timed effects; the overlay already respects actor visibility and the transient shader rejects the token (native art) until it ends. No identity changes display at birth.',
              'hits_in_batch': [],
              'no_hit': [i['native_name'] for i in identities]},
          'summons_and_same_body_copies': {
              'method': "grep of every actor definition, static map, quest script, vault, encounter, event and talent under game/modules/tome (data and class) for the twelve names and PNGs; talents that build summons/copies (summon-*, master-of-flesh, rot, thought-forms, simulacra/mirror images, Grand Arrival, cloneFull users) checked for copies of these bodies.",
              'findings': findings},
          'name_collisions_checked': [
              {'name': a['name'], 'other_definitions': ['none'], 'outcome': 'single actor definition without define_as; the catalog entry has no define_as and matches by exact name, type and subtype'} for a in {x['id']: x for x in A}.values() if a['id'] != 'ritch-flamespitter'] + [
              {'name': 'ritch flamespitter', 'other_definitions': ["Wild Gift summon of the same name with image summoner_ritch.png (talents/gifts/summon-distance.lua:446)"], 'outcome': 'the zone leaf is the catalog body; the summon has a different native image and stays native'}],
          'kept_native': [],
          'neighbours_kept_native': [
              {'name': "ritch flamespitter Wild Gift summon", 'reason': 'same name and type, different native PNG (summoner_ritch.png): body-changed'},
              {'name': 'hairy spider (tutorial)', 'reason': 'other name and define_as on the ninurlhing PNG'},
              {'name': 'black crystal', 'reason': 'not selected: tied at 8.5 with fate weaver, no family companion; left for a later batch'}]}
    out = ADDON / 'evidence/monster-batch-u-20260930/source-contracts.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(ev, indent=2, ensure_ascii=False) + '\n')
    evsha = hashlib.sha256(out.read_bytes()).hexdigest()
    for a in A:
        refs = [{'path': p, 'sha256': sha(p), 'role': r, 'note': n} for r, p, n in a['refs']]
        entry = {'asset_id': a['id'], 'native_name': a['name'], 'scope': a['scope'], 'sources': a['srcs'], 'references': refs,
                 'contrast_dimensions': list(a['dims']),
                 'prompt_fields': {'subject': a['subject'], 'contrast': a['contrast'], 'composition': a['comp'] or COMP, 'palette': a['palette']},
                 'kind': 'creature', 'max_attempts': 1, 'gate': 'ready',
                 'gate_reason': f"Exact source identity re-verified directly against game/modules/tome source (name={a['name']}, define_as={a['define_as']}, type={a['type']}/subtype={a['subtype']}, unique={a['unique']}, native_tall={a['native_tall']}); details and hashes in evidence/monster-batch-u-20260930/source-contracts.json. {a['structure']}. Exact catalog entry only, never a whole-subtype mapping.",
                 'render_evidence': [{'path': render, 'sha256': evsha}]}
        packs.setdefault(a['pack'], []).append(entry)
    for n, assets in packs.items():
        p = ADDON / f'art/production/batches/monster-batch-u-{n}.json'
        if p.exists():
            print('exists, skipped', p.name)
            continue
        p.write_text(json.dumps({'schema': 1, 'batch_id': f'monster-batch-u-{n}', 'assets': assets}, indent=2, ensure_ascii=False) + '\n')
        print('wrote', p.name)


if __name__ == '__main__':
    build()
