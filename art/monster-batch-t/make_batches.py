"""Generate the monster-batch-t task packs and the pinned source-contract
evidence (remaining 12.0-tier story identities, twelve of the thirteen named in
art/monster-batch-s/SELECTION.md: caravan merchant/guard/porter, Lost Merchant,
Nimisil, Slasul, Draebor, war dog, Yeek Wayist, Weirdling Beast, Fortress
Shadow, Pumpkin; Training Dummy kept native; see SELECTION.md). Pure
bookkeeping: hashes native sources/sprites, writes JSON and the composite
family references. Retry packs are appended by later edits of retries.py
(never overwritten)."""
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
TALLU = ' NPC.lua:33 default-name image on the leaf; resolvers.nice_tile{image="invis.png", add_mos={{image="npc/humanoid_naga_slasul.png", display_h=2, display_y=-1}}} (an explicit tall body, keys image/display_h/display_y only; with nicer_tiles off nice_tile is a no-op and the default-name image is the single path); no moddable_tile, shader, anim or add_displays; native sprite 64x128; unique with define_as, so the catalog entry needs no native_tall flag (nativeTallImage accepts the body of any unique entry, as for Walrog)'
KM = 'zones/keepsake-meadow/npcs.lua'
TT, MZ, TC, DP, HR, SF = ('zones/thieves-tunnels/npcs.lua', 'zones/maze/npcs.lua', 'zones/temple-of-creation/npcs.lua',
                          'zones/demon-plane/npcs.lua', 'zones/halfling-ruins/npcs.lua', 'zones/shertul-fortress/npcs.lua')
REFS = HERE / 'refs'


def composite(name, ids, cols):
    """Side-by-side of shipped runtime tokens used as a 'do not become this' family reference."""
    from PIL import Image
    out = REFS / f'{name}.png'
    if out.exists():
        return 'game/addons/tome-checker-revised/art/monster-batch-t/refs/' + out.name
    REFS.mkdir(exist_ok=True)
    rows = (len(ids) + cols - 1) // cols
    canvas = Image.new('RGBA', (cols * 128, rows * 128), (0, 0, 0, 0))
    for i, id_ in enumerate(ids):
        canvas.alpha_composite(Image.open(ADDON / 'data/gfx/tokens' / f'{id_}.png').convert('RGBA'), ((i % cols) * 128, (i // cols) * 128))
    canvas.save(out)
    return 'game/addons/tome-checker-revised/art/monster-batch-t/refs/' + out.name


def RC(name, ids, cols, note):
    return ('family', composite(name, ids, cols), note)


REF_HUMANS = RC('humans', ['cutpurse', 'rogue', 'thief', 'bandit'], 2,
                'Four shipped human tokens (cutpurse, rogue, thief, bandit: lean or muscular figures with paired daggers, hoods or a bald brawler pose): no caravan token or the Lost Merchant may be a dagger-wielding thief, hooded rogue or bald dagger brawler.')
REF_SUNP = R('human-sun-paladin', 'Shipped human sun-paladin (gold plate, round sunburst shield, mace): the caravan guard must not be a gold plate knight with a round shield.')
REF_NAGAS = RC('nagas', ['naga-myrmidon', 'naga-tidewarden', 'naga-nereid', 'lady-zoisla', 'lady-nashva', 'naga-tidecaller'], 3,
               'Six shipped naga tokens (blue-tailed myrmidon with a trident, brown tidewarden with a shield, yellow-tailed nereid, red lady zoisla, teal lady nashva, grey tidecaller): Slasul must not be another naga in one of those tail colours or poses.')
REF_IMPS = RC('imps', ['quasit', 'water-imp', 'wretchling', 'onilug'], 2,
              'Four shipped minor-demon tokens (bronze bull-headed quasit with a round shield, teal water imp, yellow-green wretchling, grey onilug): Draebor must not be any of these.')
REF_SPIDERS = RC('spiders', ['giant-spider', 'ungole', 'fate-spinner', 'weaver-young'], 2,
                 'Four shipped spider tokens (grey giant spider, black ungole, steel-blue fate spinner, white-swirl weaver young): Nimisil must not be a plain long-legged dark or blue spider.')
REF_HORRORS = RC('horrors', ['the-mouth', 'horned-horror', 'shade-of-telos', 'the-dreaming-one'], 2,
                 'Four shipped horror/ghost tokens (red tentacle mass the-mouth, horned-horror with a pink tentacle crown, upright ice-blue shade of telos, blue swirl the-dreaming-one): the Weirdling Beast and the Fortress Shadow must not look like any of these or like each other.')
REF_DOGS = RC('canines', ['dire-wolf', 'corrupted-war-dog', 'wolf', 'warg'], 2,
              'Four shipped canine tokens (brown dire wolf pacing sideways, grey corrupted war dog pouncing sideways with purple-green cracks, grey wolf, dark warg): the war dog must not be a sideways wolf or dog in brown, grey or black fur.')

# ---- pack 1: caravan ----
asset(1, 'caravan-merchant', 'caravan merchant',
      "keepsake-meadow (zones/keepsake-meadow/npcs.lua:62, humanoid/human, non-unique, define_as CARAVAN_MERCHANT, rank 2, base BASE_CARAVANEER, faction merchant-caravan, explicit image=npc/humanoid_human_spectator02.png); placed by the static dream-level map maps/zones/keepsake-dream.lua:32 (tile M); single definition",
      [src(KM, 'define_as = "CARAVAN_MERCHANT"'), src(KM, 'name = "caravan merchant"'), src(KM, 'image="npc/humanoid_human_spectator02.png"', after='define_as = "CARAVAN_MERCHANT"'),
       src('maps/zones/keepsake-dream.lua', 'defineTile("M", "GRASS", nil, "CARAVAN_MERCHANT")')],
      src(KM, 'define_as = "BASE_CARAVANEER"'), 'CARAVAN_MERCHANT', 'humanoid', 'human', False, False,
      'base BASE_CARAVANEER (humanoid/human, its own image=spectator02 repeated by the leaf, faction merchant-caravan, ai dumb_talented_simple);' + EXPL + '; resolvers.racial() only adds levelup talents (Higher Heal, Born into Magic, Highborn\'s Bloom), resolvers.equip longsword (equipment only, no moddable_tile); talents Armour Training, Weapon Combat, Weapons Mastery; no sustains_at_birth and no auto_classes on the leaf or base',
      'humanoid_human_spectator02.png',
      [STY, IDN('humanoid_human_spectator02.png', 'Native shape (64x64): a blond man in a plain blue tunic standing with arms at his sides.'), REF_HUMANS],
      "A caravan merchant seen from a steep overhead three-quarter angle: a plump, prosperous middle-aged human trader with a round belly, a bright SKY-BLUE knee-length tunic with a wide OCHRE-YELLOW sash, a cream linen shirt, a WIDE-BRIMMED PALE-KHAKI TRAVELLING HAT with one small white feather, rosy cheeks and a curled light-brown moustache, one arm raised HIGH holding a big bulging tan leather COIN PURSE tied at the neck, a rolled cream scroll tucked under the other arm, a short sheathed sword at the hip, brown boots. Jovial, round, prosperous and complete.",
      "Caravan people: the MERCHANT is a ROUND-BELLIED figure under a WIDE-BRIMMED HAT with one arm raised holding a big round coin purse (silhouette: wide flat hat brim above a round body plus a raised round bag; hue: sky blue, ochre and cream; value: mid-light). The shipped cutpurse, rogue, thief and bandit are lean or muscular figures with paired daggers, hoods or a bald head: no daggers, no hood, no crouched stalking pose here. The other caravan people are a mail-clad shield bearer (guard), a hunched man under stacked crates (porter) and a bald cowering man with a lantern (Lost Merchant).",
      "Sky-blue tunic in a mid-light value with pale blue highlight planes, cream shirt and scroll, ochre sash, pale khaki hat with a white feather, tan purse, light-brown moustache, pink skin; nothing darker than dark brown except the eyes; the disc stays neutral charcoal with no blue cast." + DISC,
      "READY single with define_as (caravan merchant, CARAVAN_MERCHANT)", comp=COMP + FIT + COMPACT + BRIGHT)

asset(1, 'caravan-guard', 'caravan guard',
      "keepsake-meadow (zones/keepsake-meadow/npcs.lua:75, humanoid/human, non-unique, define_as CARAVAN_GUARD, rank 2, base BASE_CARAVANEER, faction merchant-caravan, explicit image=npc/humanoid_human_spectator.png); placed by maps/zones/keepsake-dream.lua:33 (tile G); single definition",
      [src(KM, 'define_as = "CARAVAN_GUARD"'), src(KM, 'name = "caravan guard"'), src(KM, 'image="npc/humanoid_human_spectator.png"', after='define_as = "CARAVAN_GUARD"'),
       src('maps/zones/keepsake-dream.lua', 'defineTile("G", "GRASS", nil, "CARAVAN_GUARD")')],
      src(KM, 'define_as = "BASE_CARAVANEER"'), 'CARAVAN_GUARD', 'humanoid', 'human', False, False,
      'base BASE_CARAVANEER (humanoid/human, faction merchant-caravan);' + EXPL + '; resolvers.racial() only adds levelup talents, resolvers.equip longsword, shield and heavy armour (equipment only, no moddable_tile); talents Armour Training, Weapon Combat, Weapons Mastery, Shield Pummel; no sustains_at_birth and no auto_classes',
      'humanoid_human_spectator.png',
      [STY, IDN('humanoid_human_spectator.png', 'Native shape (64x64): a dark-haired commoner in an olive cloak and brown tunic standing with his hands lowered.'), REF_SUNP],
      "A caravan guard seen from a steep overhead three-quarter angle: a broad-shouldered human mercenary standing BRACED with knees bent, an open-faced rounded IRON KETTLE HELM with a plain brow band, a light grey RING-MAIL hauberk under a KHAKI-YELLOW surcoat with a small brown WAGON-WHEEL emblem, a LARGE RECTANGULAR STEEL-GREY SHIELD with a pale riveted rim and a central iron boss held straight IN FRONT of the body covering the torso, a plain bright steel longsword thrust forward along the shield's right edge, brown leather boots and gauntlets, a square stubbled jaw. Steady, boxy and complete.",
      "Caravan people: the GUARD is a helmeted mail-clad figure behind a big RECTANGULAR grey shield held in front, with a sword edge beside it (silhouette: a boxy shield block in front topped by a rounded helm; hue: steel grey, khaki and brown; value: mid-light). The shipped human sun-paladin is a GOLD plate knight with a ROUND sunburst shield and a mace: this must not be gold, not plate, not a round shield. The merchant is a plump blue figure with a wide hat and a coin purse; the porter is a hunched man carrying crates on his back with warm pale wood; the Lost Merchant is a bald cowering man.",
      "Light grey ring-mail with pale highlight planes, khaki-yellow surcoat, steel-grey shield face with pale rim and boss, bright polished steel sword and helm, tan skin, brown boots and gauntlets; nothing darker than dark grey-brown except the eyes; the disc stays neutral charcoal with no yellow cast." + DISC,
      "READY single with define_as (caravan guard, CARAVAN_GUARD)", comp=COMP + FIT + COMPACT + BRIGHT)

asset(1, 'caravan-porter', 'caravan porter',
      "keepsake-meadow (zones/keepsake-meadow/npcs.lua:91, humanoid/human, non-unique, define_as CARAVAN_PORTER, rank 2, base BASE_CARAVANEER, faction merchant-caravan, explicit image=npc/humanoid_human_spectator03.png); placed by maps/zones/keepsake-dream.lua:34 (tile P); single definition",
      [src(KM, 'define_as = "CARAVAN_PORTER"'), src(KM, 'name = "caravan porter"'), src(KM, 'image="npc/humanoid_human_spectator03.png"', after='define_as = "CARAVAN_PORTER"'),
       src('maps/zones/keepsake-dream.lua', 'defineTile("P", "GRASS", nil, "CARAVAN_PORTER")')],
      src(KM, 'define_as = "BASE_CARAVANEER"'), 'CARAVAN_PORTER', 'humanoid', 'human', False, False,
      'base BASE_CARAVANEER (humanoid/human, faction merchant-caravan);' + EXPL + '; resolvers.racial() only adds levelup talents, resolvers.equip waraxe (equipment only, no moddable_tile); talents Armour Training, Weapon Combat, Weapons Mastery; no sustains_at_birth and no auto_classes',
      'humanoid_human_spectator03.png',
      [STY, IDN('humanoid_human_spectator03.png', 'Native shape (64x64): a dark-haired man in a cream vest, brown shorts and a dark cloak standing with his arms at his sides.'), REF_HUMANS],
      "A caravan porter seen from a steep overhead three-quarter angle: a stocky, burly human labourer HUNCHED forward under the weight of a tall stack of TWO WARM PALE-WOOD CRATES with dark iron corner plates strapped together with a coil of rope and carried on his back and shoulders (the stack rises behind and above his head like a blocky pack, its top edge pulled well inside the disc), a cream linen shirt with rolled sleeves and a brown leather harness strap across the chest, light tan trousers, a flat brown cap, a small waraxe hanging from his belt, thick bare forearms, heavy boots, a stubbled chin, head thrust forward. Laden, hunched, boxy and complete.",
      "Caravan people: the PORTER is a HUNCHED figure whose main mass is a blocky STACK OF CRATES ON HIS BACK with his head thrust out in front (silhouette: one big square pack behind a small forward head; hue: warm pale wood, cream and tan; value: light). The guard holds a grey shield block IN FRONT; the merchant is a round blue figure with a wide hat; the Lost Merchant is a bald man with a lumpy canvas rucksack and a lantern. The shipped cutpurse, rogue, thief and bandit carry paired daggers or wear hoods: the porter has no dagger and no hood.",
      "Warm pale wood crates in a light value with cream highlight planes on the upper-left faces and dark iron corner plates, rope in tan, cream shirt, light tan trousers, brown cap and harness, tanned skin, steel waraxe head; nothing darker than dark brown except the eyes and the iron corner plates; the disc stays neutral charcoal with no warm cast." + DISC,
      "READY single with define_as (caravan porter, CARAVAN_PORTER)", comp=COMP + FIT + COMPACT + BRIGHT)

# ---- pack 2: lost merchant, war dog, yeek wayist ----
asset(2, 'lost-merchant', 'Lost Merchant',
      "thieves-tunnels (zones/thieves-tunnels/npcs.lua:113, humanoid/human, non-unique, define_as MERCHANT, no base, no rank field, faction victim, default-name image); placed by the static quest map maps/quests/lost-merchant.lua:29 (tile @); single definition",
      [src(TT, 'define_as = "MERCHANT"'), src(TT, 'name = "Lost Merchant"'), src('maps/quests/lost-merchant.lua', "defineTile('@', \"FLOOR\", nil, \"MERCHANT\")")], None,
      'MERCHANT', 'humanoid', 'human', False, False,
      'no base (humanoid/human on the leaf, faction victim, ai simple, cant_be_moved, can_talk lost-merchant);' + DEF + '; no resolvers, no talents, no equipment, no sustains_at_birth and no auto_classes',
      'humanoid_human_lost_merchant.png',
      [STY, IDN('humanoid_human_lost_merchant.png', 'Native shape (64x64): a stout bald bearded man in a cream tunic and belt standing with his hands at his sides.'), REF_HUMANS],
      "The Lost Merchant seen from a steep overhead three-quarter angle: a stout middle-aged human trader CROUCHING low and COWERING, shoulders hunched and head pulled in, a shiny bald head with a bushy GREY beard and wide frightened eyes, a dusty long TAN-OLIVE travelling coat torn at the hem over a cream shirt with a red neckerchief, a huge lumpy pale CANVAS RUCKSACK bulging on his back with a rolled bedroll on top, one hand raised palm-out in fright and the other clutching a small brass LANTERN with a tiny warm flame close to his chest, worn brown boots. Frightened, round, unarmed and complete.",
      "Human traders: the LOST MERCHANT is a low ROUND CROUCHED figure with a big lumpy RUCKSACK on his back and a small lantern, no weapon (silhouette: one squat round mass with a bulging pack and a raised hand; hue: dusty tan-olive, cream and grey beard; value: mid-light). The shipped bandit is a bald bearded muscular fighter with two daggers and the cutpurse, rogue and thief are lean dagger figures: this man holds no weapon and cowers. The caravan merchant is a plump upright blue figure with a wide hat; the porter carries crates; the guard holds a shield.",
      "Dusty tan-olive coat in a mid-light value with pale straw highlight planes, cream shirt and rucksack canvas, grey beard, pink bald head, red neckerchief, brass lantern with a tiny warm flame; nothing darker than dark brown except the eyes and boots; the flame and lantern must not glow onto or tint the disc." + DISC,
      "READY single with define_as (Lost Merchant, MERCHANT)", comp=COMP + FIT + COMPACT + BRIGHT)

asset(2, 'war-dog', 'war dog',
      "keepsake-meadow (zones/keepsake-meadow/npcs.lua:104, animal/canine, non-unique, define_as WAR_DOG, base BASE_NPC_CANINE, explicit image=npc/canine_dw.png); spawned twice by quests/keepsake.lua:290 (on_spawn_companions, next to the Berethh companions); the SAME PNG is also the dire wolf (general/npcs/canine.lua:75) and the corrupted war dog (keepsake-meadow/npcs.lua:118, CORRUPTED_WAR_DOG), told apart by exact name",
      [src(KM, 'define_as = "WAR_DOG"'), src(KM, 'name = "war dog"'), src(KM, 'image="npc/canine_dw.png"', after='define_as = "WAR_DOG"'),
       src('quests/keepsake.lua', 'makeEntityByName(game.level, "actor", "WAR_DOG")')],
      src('general/npcs/canine.lua', 'define_as = "BASE_NPC_CANINE"'), 'WAR_DOG', 'animal', 'canine', False, False,
      'base BASE_NPC_CANINE (animal/canine, no image=);' + EXPL + '; talents Rush, Grappling Stance (sustained, only if the AI starts it: temporary values), Clinch; no sustains_at_birth, no auto_classes and no resolvers.equip; shares canine_dw.png with dire wolf and corrupted war dog, each entry matching only its exact name',
      'canine_dw.png',
      [STY, IDN('canine_dw.png', 'Native shape (64x64, shared by dire wolf, war dog and corrupted war dog): a dark brown heavy canine standing side-on with a snarling face. Do NOT copy its dark fur or its side-on stance.'), REF_DOGS],
      "A war dog seen from a steep overhead three-quarter angle: a huge heavy-set MASTIFF-type fighting dog with a short SANDY-FAWN coat and a cream chest and paws, standing BRACED and FACING THE VIEWER HEAD-ON with its head lowered and its shoulders wide, a broad short blunt muzzle with a dark brown mask, small folded ears, bared front teeth, a studded brown leather HARNESS with bright steel rivets and a small polished steel breastplate on the chest, a RED CLOTH CAPARISON draped over its back, a spiked steel collar, front legs planted wide apart, tail low. Braced, wide, armoured and complete.",
      "Canines sharing one native PNG: the WAR DOG is a WARM SANDY-FAWN and CREAM mastiff seen HEAD-ON, wide-shouldered, with a red cloth on its back and a steel breastplate (silhouette: a wide front-facing triangle with a broad flat face and a chest plate; hue: sandy fawn, cream, red and steel; value: light). The shipped dire wolf is a brown long-muzzled wolf pacing SIDEWAYS, the corrupted war dog is a grey dog pouncing SIDEWAYS with purple-green cracks: this must not be side-on, not brown, not grey, not cracked, and must carry the harness and red cloth.",
      "Sandy-fawn short coat in a light value with pale cream highlight planes, cream chest and paws, brown mask, brown leather harness with bright steel rivets and breastplate, red cloth in a mid-light value, pale steel spikes; nothing darker than dark brown except the eyes, nose and mask; the disc stays neutral charcoal with no red or tan cast." + DISC,
      "READY single with define_as (war dog, WAR_DOG)", comp=COMP + FIT + COMPACT + BRIGHT)

asset(2, 'yeek-wayist', 'Yeek Wayist',
      "halfling-ruins (zones/halfling-ruins/npcs.lua:117, humanoid/yeek, unique, define_as YEEK_WAYIST, rank 3, no base, default-name image, faction the-way, never_act); placed by the static last-level map maps/zones/halfling-ruins-last.lua:51 (tile Y); single definition",
      [src(HR, 'define_as="YEEK_WAYIST"'), src(HR, 'name = "Yeek Wayist"'), src(HR, 'resolvers.sustains_at_birth()', after='define_as="YEEK_WAYIST"'),
       src('maps/zones/halfling-ruins-last.lua', 'defineTile(\'Y\', "FLOOR", nil, "YEEK_WAYIST")')], None,
      'YEEK_WAYIST', 'humanoid', 'yeek', True, False,
      'no base (humanoid/yeek on the leaf, no image=);' + DEF + '; resolvers.equip greatsword (equipment only, no moddable_tile); talents Kinetic Shield (sustained), Mindhook, Pyrokinesis, Mindlash, Charged Aura (sustained), Telekinetic Smash; resolvers.sustains_at_birth() starts the sustained ones (temporary values and particles only, no type/subtype/image/add_mos write); no auto_classes',
      'humanoid_yeek_yeek_wayist.png',
      [STY, IDN('humanoid_yeek_yeek_wayist.png', 'Native shape (64x64): a small white-furred yeek with a big head and a sword floating beside it.')],
      "The Yeek Wayist seen from a steep overhead three-quarter angle: a small pot-shaped WHITE-FURRED yeek elder standing calmly upright, long thin arms held out with open palms as if guiding, a big rounded head with a large forehead, huge pale ICE-BLUE eyes and a tiny mouth, a teal-blue cloth BANDOLIER across the chest and small teal wrist wraps, bare pale feet, and a broad steel GREATSWORD FLOATING in the air beside his shoulder on the left, tilted diagonally point-down and NOT held, no longer than his own body height, with a small ring of pale motes around the hilt. Serene, small, pale and complete.",
      "Yeek: the WAYIST is a small WHITE furry pot-shaped figure with a large round head and a teal bandolier, with a FLOATING diagonal greatsword hovering unheld beside him (silhouette: small rounded body with a round head plus a diagonal blade floating apart from the hands; hue: white fur, teal and steel; value: light). No yeek token exists yet; the shipped naga, human and imp tokens are much larger and more armoured, so this must read as a small pale gentle creature with a floating sword, not a warrior holding a sword.",
      "White fur in a light value with pale blue-grey shadow planes and broad bright highlight planes, pale skin on face and feet, ice-blue eyes, teal bandolier and wraps in a mid value, bright polished steel blade with a pale edge; nothing darker than mid blue-grey except the eyes; the disc stays neutral charcoal and must not be brightened by the white fur." + DISC,
      "READY unique with define_as (Yeek Wayist, YEEK_WAYIST)", comp=COMP + FIT + COMPACT + BRIGHT)

# ---- pack 3: nimisil, slasul, draebor ----
asset(3, 'nimisil', 'Nimisil',
      "maze (zones/maze/npcs.lua:152, spiderkin/spider, unique, define_as NIMISIL, rank 4, base BASE_NPC_SPIDER, default-name image); a backup guardian created by game.state:activateBackupGuardian(\"NIMISIL\", 2, 40) when the maze's Minotaur or Horned Horror dies (only on a return visit); single definition; auto_classes Anorithil from level 44",
      [src(MZ, 'define_as = "NIMISIL"'), src(MZ, 'name = "Nimisil"'), src(MZ, 'auto_classes={{class="Anorithil"'), src(MZ, 'game.state:activateBackupGuardian("NIMISIL"'),
       src('general/npcs/spider.lua', 'resolvers.sustains_at_birth()', after='define_as = "BASE_NPC_SPIDER"')],
      src('general/npcs/spider.lua', 'define_as = "BASE_NPC_SPIDER"'), 'NIMISIL', 'spiderkin', 'spider', True, False,
      'base BASE_NPC_SPIDER (spiderkin/spider, no image=);' + DEF + '; talents Spider Web, Lay Web, Phase Door, Hymn of Moonlight (sustained), Moonlight Ray, Shadow Blast, Searing Light; the base has resolvers.sustains_at_birth() which starts Hymn of Moonlight (temporary values, callbacks and particles only, no type/subtype/image/add_mos write); auto_classes Anorithil from level 44 (see runtime_mutation_scan)',
      'spiderkin_spider_nimisil.png',
      [STY, IDN('spiderkin_spider_nimisil.png', 'Native shape (64x64): a dark spider whose body and back are covered with glowing multicoloured crystalline growths.'), REF_SPIDERS],
      "Nimisil seen from a steep overhead three-quarter angle: a large spider with a stout PALE SILVER-GREY body and short thick pale-banded legs held in a tight RADIAL RING (all eight legs bent compactly around the body), the bulbous abdomen and back crowned with a dense CLUSTER of luminous crystalline fungus-like growths and knobs in glowing AQUA-CYAN, pale PINK, LEMON-YELLOW and soft VIOLET like a jewelled crown of moonlit lumps, a small pale head with several glowing pale-blue eyes and short white fangs, a faint moon-white sheen. Eerie, jewelled and complete.",
      "Spiders: NIMISIL is a PALE SILVER spider with a JEWELLED CROWN OF GLOWING KNOBS clustered on its back and short stout legs in a tight ring (silhouette: a round crowned bump-covered mass with short stubby legs; hue: silver grey with aqua, pink, yellow and violet lumps; value: light). The shipped giant spider is a long-legged grey and white spider, ungole is black, fate spinner is a steel-blue spider with long serrated legs and a silk ring, weaver young is a white curled ball: this must not have long spread legs and must not be a plain single-colour spider.",
      "Pale silver-grey body in a light value with bright highlight planes and blue-grey shadows, glowing aqua-cyan, pink, lemon and violet crystal knobs (bright, saturated but light), pale banded legs, pale blue eyes; nothing darker than mid blue-grey except the eyes; the glow must stay on the creature and must not spill onto or tint the disc." + DISC,
      "READY unique with define_as (Nimisil, NIMISIL)", comp=COMP + FIT + COMPACT + BRIGHT)

asset(3, 'slasul', 'Slasul',
      "temple-of-creation (zones/temple-of-creation/npcs.lua:26, humanoid/naga, unique, define_as SLASUL, rank 4, no base, explicit nice_tile tall body 64x128); placed by the static last-level map maps/zones/temple-of-creation-last.lua:26; single definition",
      [src(TC, 'define_as = "SLASUL"'), src(TC, 'name = "Slasul"'), src(TC, 'resolvers.nice_tile{image="invis.png", add_mos = {{image="npc/humanoid_naga_slasul.png"'),
       src(TC, 'resolvers.sustains_at_birth()', after='define_as = "SLASUL"'), src('maps/zones/temple-of-creation-last.lua', 'defineTile(\'@\', "WATER_FLOOR", nil, "SLASUL")')], None,
      'SLASUL', 'humanoid', 'naga', True, False,
      'no base (humanoid/naga on the leaf, faction temple-of-creation);' + TALLU + '; resolvers.equip mace, shield, heavy armour and the Eldritch Pearl (equipment only); talents Weapon Combat, Weapons Mastery, Shield Expertise, Shield Pummel, Riposte, Blinding Speed, Perfect Strike, Spit Poison, Heal, Uttercold (sustained), Ice Shards, Freeze, Tidal Wave, Ice Storm, Water Bolt, No Fatigue, Massive Blow, Draconic Will, Draconic Body, Arcane Might, Corrupted Shell; resolvers.sustains_at_birth() starts the sustained ones (temporary values and particles only, no type/subtype/image/add_mos write); no auto_classes',
      'humanoid_naga_slasul.png',
      [STY, IDN('humanoid_naga_slasul.png', 'Native shape (64x128 tall body): a bare-chested naga in a bronze crested helm holding a round shield and a mace over a blue serpent tail.'), REF_NAGAS],
      "Slasul seen from a steep overhead three-quarter angle: a towering regal male naga, a muscular bare torso with an exquisite large WHITE PEARL set in the centre of his chest, a bronze-gold CRESTED HELM with a tall fin-shaped crest and cheek plates, gold collar and armbands, a ROUND bronze-rimmed shield with a pearl boss held forward on the left arm and a heavy flanged MACE raised on the right, a stern face with tanned skin, and below the waist a thick SEA-GREEN serpent tail with a pale cream belly coiled in a broad round SPIRAL BASE beneath him, gold-edged scales. Regal, coiled, golden and complete.",
      "Nagas: SLASUL is a GOLD-CRESTED armoured king with a big pearl on his chest, a round shield forward and a mace raised, on a SEA-GREEN spiral tail base (silhouette: fin-crested helm above a round shield and a raised mace over a round coiled base; hue: sea green and bronze-gold with a white pearl; value: mid-light). The shipped myrmidon has a blue tail and a trident, the tidewarden is brown with a shield, the nereid is yellow-tailed, zoisla red-tailed, nashva teal-tailed, the tidecaller grey robed: none of those have a fin-crested helm, gold armour, a pearl or a green tail.",
      "Sea-green tail in a mid-light value with pale jade highlight planes and cream belly, gold-edged scales, bronze-gold helm, collar and shield rim with bright pale-yellow highlight planes, tan skin, white pearl, pale steel mace head; nothing darker than dark green except the eyes and seams; the disc stays neutral charcoal with no green or gold cast." + DISC,
      "READY unique tall with define_as (Slasul, SLASUL; native-tall body pinned, no native_tall flag)", comp=COMP + FIT + COMPACT + BRIGHT)

asset(3, 'draebor', 'Draebor, the Imp',
      "demon-plane (zones/demon-plane/npcs.lua:26, demon/minor, unique, define_as DRAEBOR, rank 4, no base, default-name image, faction fearscape); the zone's guaranteed guardian (zones/demon-plane/zone.lua:58); single definition",
      [src(DP, 'define_as = "DRAEBOR"'), src(DP, 'name = "Draebor, the Imp"'), src(DP, 'resolvers.sustains_at_birth()', after='define_as = "DRAEBOR"'),
       src(DP, 'summon = {', after='define_as = "DRAEBOR"'), src('zones/demon-plane/zone.lua', 'guardian = "DRAEBOR"')], None,
      'DRAEBOR', 'demon', 'minor', True, False,
      'no base (demon/minor on the leaf, no image=);' + DEF + '; resolvers.equip Boots of Phasing (equipment only); talents Summon, Flame, Blood Grasp, Wildfire (sustained), Phase Door, Curse of Vulnerability, Bone Shield (sustained); resolvers.sustains_at_birth() starts the sustained ones (temporary values and particles only, no type/subtype/image/add_mos write); summon={type=demon} draws generic demons from the level, never a copy of Draebor; no auto_classes',
      'demon_minor_draebor__the_imp.png',
      [STY, IDN('demon_minor_draebor__the_imp.png', 'Native shape (64x64): a squat shaggy grey-white imp with red eyes, a wide toothy grin and claws.'), REF_IMPS],
      "Draebor, the Imp seen from a steep overhead three-quarter angle: a squat pot-bellied mocking imp crouched forward in a smug pose, covered in matted PALE GREY-WHITE shaggy fur, a big wide face with a huge toothy grin of sharp yellow fangs, two small curved horns, large pointed ears, glowing ORANGE eyes, long clawed hands, one hand raised with a small ball of ORANGE FIRE flickering above the palm and the other on its hip, a thin tufted tail curling up behind, oversized clawed feet. Smug, shaggy, squat and complete.",
      "Minor demons: DRAEBOR is a SHAGGY PALE GREY-WHITE pot-bellied imp with a huge grin and a small fireball in one raised hand (silhouette: a squat round fluffy mass with big ears and one raised hand; hue: pale grey-white fur with orange fire and yellow teeth; value: light). The shipped quasit is a bronze bull-headed demon holding a round shield, the water imp is a slim teal imp, the wretchling a yellow-green crouching demon, the onilug a grey lanky horror: this must not have a shield, a bull head, a smooth skin or a teal or yellow-green colour.",
      "Pale grey-white matted fur in a light value with broad bright highlight planes and blue-grey shadow planes, yellow teeth, orange eyes and orange fire, dark grey claws and horns in a mid value; nothing darker than mid grey except the eyes; the fire must stay small and must not glow onto or tint the disc." + DISC,
      "READY unique with define_as (Draebor, the Imp, DRAEBOR)", comp=COMP + FIT + COMPACT + BRIGHT)

# ---- pack 4: shertul fortress ----
asset(4, 'weirdling-beast', 'Weirdling Beast',
      "shertul-fortress (zones/shertul-fortress/npcs.lua:24, horror/eldritch, unique, define_as WEIRDLING_BEAST, rank 3.5, base BASE_NPC_HORROR, default-name image); placed by the static tmx maps/zones/shertul-fortress.tmx (spawn#actor object id WEIRDLING_BEAST); single definition; auto_classes Anorithil, Doomed, Corruptor and Archmage from level 22",
      [src(SF, 'define_as="WEIRDLING_BEAST"'), src(SF, 'name = "Weirdling Beast"'), src(SF, 'auto_classes={', after='define_as="WEIRDLING_BEAST"'),
       src(SF, 'resolvers.sustains_at_birth()', after='define_as="WEIRDLING_BEAST"'), src('maps/zones/shertul-fortress.tmx', '<property name="id" value="WEIRDLING_BEAST"/>')],
      src('general/npcs/horror.lua', 'define_as = "BASE_NPC_HORROR"'), 'WEIRDLING_BEAST', 'horror', 'eldritch', True, False,
      'base BASE_NPC_HORROR (horror/eldritch, no image=);' + DEF + '; resolvers.equip staff and light armour (equipment only, no moddable_tile); talents Staff Mastery, Acid Blood, Bone Grab, Bone Shield (sustained), Mind Sear, Telekinetic Blast, Gloom (sustained), Soul Rot, Corrupted Negation, Time Prison, Starfall, Manathrust, Freeze plus inscriptions; resolvers.sustains_at_birth() starts the sustained ones (temporary values and particles only, no type/subtype/image/add_mos write); auto_classes Anorithil, Doomed, Corruptor, Archmage from level 22: the Corruptor tree corruption/shadowflame contains Flame of Urh\'Rok (see runtime_mutation_scan; the entry opts into urh_rok_form)',
      'horror_eldritch_weirdling_beast.png',
      [STY, IDN('horror_eldritch_weirdling_beast.png', 'Native shape (64x64): a headless brown octopus-like body with four thick tentacle limbs and eye-like warts.'), REF_HORRORS],
      "The Weirdling Beast seen from a steep overhead three-quarter angle: a HEADLESS, roughly humanoid mass of pale FLESH-PINK and tan skin, a wide squat torso with a smooth rounded shoulder-mass and NO head at all, covered in dozens of round wart-like blisters some of which burst with yellow-green pus, FOUR thick TENTACLES serving as limbs (two as arms curled up and out, two as splayed legs) arranged in an X around the torso, the tentacle undersides lined with round cream suckers, a few larger glowing pale-yellow warts. Putrid, lumpy, headless and complete.",
      "Horrors of the fortress: the WEIRDLING BEAST is a SOLID, HEADLESS, WARTY flesh-pink torso with FOUR TENTACLE LIMBS in an X (silhouette: a round lumpy body with four curled arms and legs radiating like an octopus seen from above, no head; hue: flesh pink, tan and sickly yellow-green; value: mid-light). The shipped the-mouth is a red tentacle mass, horned-horror has a pink tentacle crown on a bull, shade-of-telos is an upright ice-blue ghost, the-dreaming-one a blue swirl; the Fortress Shadow of this same set is a translucent aqua bell with hanging tendrils: this must be solid, warm-coloured and headless.",
      "Pale flesh-pink and tan skin in a mid-light value with bright pale highlight planes on the upper-left of the torso and tentacles, sickly yellow-green wart tips, cream suckers, a little warm brown in the creases; nothing darker than dark tan-brown except seams; keep the flesh pink-tan rather than brown or maroon; the disc stays neutral charcoal with no pink cast." + DISC,
      "READY unique with define_as (Weirdling Beast, WEIRDLING_BEAST); urh_rok_form opt-in", comp=COMP + FIT + COMPACT + BRIGHT)

asset(4, 'fortress-shadow', 'Fortress Shadow',
      "shertul-fortress (zones/shertul-fortress/npcs.lua:128, horror/Sher'Tul, non-unique, define_as BUTLER, rank 3, base BASE_NPC_HORROR, faction neutral, invulnerable, never_move, default-name image whose subtype part is the lowercased, non-alphanumeric-to-underscore form of \"Sher'Tul\"); created by quests/shertul-fortress.lua:88 spawn_butler via makeEntityByName(\"BUTLER\"); single definition",
      [src(SF, 'define_as="BUTLER"'), src(SF, 'subtype = "Sher\'Tul"'), src(SF, 'name = "Fortress Shadow"'), src('quests/shertul-fortress.lua', 'makeEntityByName(game.level, "actor", "BUTLER")')],
      src('general/npcs/horror.lua', 'define_as = "BASE_NPC_HORROR"'), 'BUTLER', 'horror', "Sher'Tul", False, False,
      'base BASE_NPC_HORROR (horror/eldritch, overridden to subtype "Sher\'Tul" by the leaf, no image=);' + DEF + '; the subtype string is "Sher\'Tul" exactly (capital S and T, apostrophe): NPC.lua:33 lowercases it and turns the apostrophe into an underscore, giving horror_sher_tul_fortress_shadow.png; no talents, no equipment, no sustains_at_birth and no auto_classes',
      'horror_sher_tul_fortress_shadow.png',
      [STY, IDN('horror_sher_tul_fortress_shadow.png', 'Native shape (64x64): a translucent turquoise outline of a headless tentacled shadow.'), REF_HORRORS],
      "The Fortress Shadow seen from a steep overhead three-quarter angle: a hovering SEMI-TRANSLUCENT but mostly opaque PALE AQUAMARINE-WHITE smoky glass-like creature shaped like a JELLYFISH: a domed hood-like bell on top with darker teal edges and a faint glowing white ring of Sher'Tul rune marks across the dome, and EIGHT long wavy tendrils trailing outward around it in a radial ring, no face, no eyes, a soft pale inner glow at the centre of the dome, a few tiny drifting motes. Ghostly, floating, luminous and complete.",
      "Horrors of the fortress: the FORTRESS SHADOW is a floating PALE AQUA DOME with EIGHT TENDRILS radiating in a ring and a rune circle on the dome (silhouette: a round bell with a wavy radial fringe, jellyfish-like; hue: pale aquamarine and white with teal edges; value: light). The shipped shade-of-telos is an upright humanoid ice-blue ghost, the-dreaming-one a round blue swirl, the-mouth a red tentacle mass, horned-horror a pink bull; the Weirdling Beast of this same set is a solid warty flesh-pink headless body: this must be pale aqua, translucent-looking, with no humanoid outline.",
      "Pale aquamarine-white in a light value with bright white highlight planes on the upper-left of the dome, darker teal edges and tendril tips in a mid value, a soft pale inner glow; nothing darker than mid teal; keep it luminous and pale rather than dark teal; the glow must stay inside the creature and must not spill onto or tint the disc." + DISC,
      "READY single with define_as (Fortress Shadow, BUTLER; subtype \"Sher'Tul\")", comp=COMP + FIT + COMPACT + BRIGHT)

asset(4, 'pumpkin', 'Pumpkin, the little kitty',
      "shertul-fortress (zones/shertul-fortress/npcs.lua:176, animal/feline, unique, define_as KITTY, base BASE_NPC_CAT, explicit image=npc/sage_kitty.png, invulnerable, never_anger, the leaf sets an empty defineDisplayCallback); created by zones/shertul-fortress/zone.lua:94 makeEntityByName(\"KITTY\"); single definition (the Lost Kitty encounter of general/encounters/maj-eyal.lua:106 is another name and stays native)",
      [src(SF, 'define_as = "KITTY"'), src(SF, 'name = "Pumpkin, the little kitty"'), src(SF, 'image="npc/sage_kitty.png"', after='define_as = "KITTY"'),
       src(SF, 'defineDisplayCallback = function() end', after='define_as = "KITTY"'), src('zones/shertul-fortress/zone.lua', 'makeEntityByName(game.level, "actor", "KITTY", true)')],
      src('general/npcs/feline.lua', 'define_as = "BASE_NPC_CAT"'), 'KITTY', 'animal', 'feline', True, False,
      'base BASE_NPC_CAT (animal/feline, resolvers.sustains_at_birth() with no sustained talents on the leaf);' + EXPL + '; the leaf overrides defineDisplayCallback with an empty function (native life/rank frames are not drawn for it; the token overlay is a separate layer, not live-tested here); no talents, no equipment and no auto_classes',
      'sage_kitty.png',
      [STY, IDN('sage_kitty.png', 'Native shape (64x64): a small orange tabby cat walking in profile with its tail raised.')],
      "Pumpkin, the little kitty seen from a steep overhead three-quarter angle: a plump small ORANGE TABBY cat SITTING upright and compact with its tail wrapped round its front paws, its round head turned UP toward the viewer with big bright GREEN eyes, a pink nose and white whiskers, a clear white STAR-SHAPED BLAZE on the chest, white front paws, darker orange tiger stripes on the back and cheeks, ears pricked. Drawn LARGE within the inner three quarters of the disc so the little cat still reads at small size. Cute, round, orange and complete.",
      "Small animals: PUMPKIN is a round SITTING ORANGE cat with a white star on the chest, drawn large (silhouette: a round upright mass with two pointed ears and a curled tail around the paws; hue: warm orange with white and green eyes; value: mid-light). It is not a canine: no long muzzle, no wolf ears, no side-on standing pose, so it cannot be confused with the shipped dogs or wolves; the war dog is a big sandy front-facing dog.",
      "Warm orange fur in a mid-light value with pale peach highlight planes on the upper-left and deeper orange stripes, white chest star and paws, bright green eyes, pink nose; nothing darker than dark orange-brown except the pupils; the disc stays neutral charcoal with no orange cast." + DISC,
      "READY unique with define_as (Pumpkin, the little kitty, KITTY)", comp=COMP + FIT + COMPACT + BRIGHT)


def retry(id_, pack, **changes):
    base = next(a for a in A if a['id'] == id_)
    A.append(dict(base, pack=pack, **changes))


# ---- retry packs are appended below by later edits of retries.py ----
exec((HERE / 'retries.py').read_text()) if (HERE / 'retries.py').exists() else None

PNGF = {i: 'NPC.lua:33 default-name image on the leaf (no image=/nice_tile)' for i in (
    'lost-merchant', 'nimisil', 'draebor', 'yeek-wayist', 'weirdling-beast', 'fortress-shadow')}
PNGF.update({i: 'explicit image= on the leaf (no nice_tile/add_mos)' for i in ('caravan-merchant', 'caravan-guard', 'caravan-porter', 'war-dog', 'pumpkin')})
PNGF['slasul'] = 'NPC.lua:33 default-name image on the leaf plus an explicit resolvers.nice_tile tall body naming the same PNG (invis.png + one add_mos entry, display_h=2, display_y=-1; no-op when nicer_tiles is off)'


def build():
    packs = {}
    identities = []
    render = 'game/addons/tome-checker-revised/evidence/monster-batch-t-20260930/source-contracts.json'
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
          'task': "monster-batch-t: static re-verification (no game launch) of the twelve identities of the remaining 12.0-tier story list (caravan merchant, caravan guard, caravan porter, Lost Merchant, Nimisil, Slasul, Draebor the Imp, war dog, Yeek Wayist, Weirdling Beast, Fortress Shadow, Pumpkin the little kitty) against game/modules/tome source and native sprites; the thirteenth candidate, Training Dummy, is kept native (see kept_native). Every field below was read from source: name, type/subtype, define_as, explicit or NPC.lua:33 default image, unique, PNG on disk, and absence of moddable_tile/shader/anim/add_displays. Findings: eleven identities are 64x64 single images (five through an explicit image=, six through the default-name image); Slasul is a UNIQUE native-tall body (explicit nice_tile, PNG 64x128, define_as SLASUL, no native_tall flag as for Walrog); no identity is a non-unique tall body. Fortress Shadow's subtype is exactly \"Sher'Tul\" (capital letters, apostrophe) and its default image is horror_sher_tul_fortress_shadow.png. The war dog, dire wolf and corrupted war dog share canine_dw.png and are told apart by exact name and define_as. Weirdling Beast can reach Flame of Urh'Rok through its Corruptor auto_class and opts into urh_rok_form.",
          'new_ids_not_in_catalog_before_this_batch': [i['id'] for i in identities], 'identities': identities,
          'runtime_mutation_scan': {
              'method': "every talent of each identity (resolvers.talents, inherited base talents, racial levelup talents and the auto_classes class talent trees: Anorithil, Doomed, Corruptor, Archmage) was resolved under game/modules/tome/data/talents; the whole talents/ and timed_effects/ trees were grepped for writes to type/subtype/image/add_mos/add_displays/moddable_tile/replace_display/shader (regex on any receiver, plus the tuple assignment form) and the results reviewed line by line; the resolvers sustains_at_birth, racial, inscriptions, equip, nice_tile and the base-file talent lists were read.",
              'writers_found': [
                  {'file': 'game/modules/tome/data/talents/corruptions/shadowflame.lua', 'line': 97, 'talent': "Flame of Urh'Rok", 'effect': 'sustain: __old_type={type,subtype}; type,subtype = demon,major; image untouched; restored on deactivate'},
                  {'file': 'game/modules/tome/data/talents/psionic/thought-forms.lua', 'line': 92, 'talent': 'thought-form summons (Solipsist tree)', 'effect': 'sets type/subtype/image/moddable_tile/add_mos on the summoned minion copied from its summoner, never on the caster'},
                  {'file': 'game/modules/tome/data/talents/chronomancy/anomalies.lua', 'line': 587, 'talent': 'anomaly summons', 'effect': 'creates a separate spawned NPC with another image; not the caster'}],
              'timed_effects_review': "timed_effects write shader, replace_display, add_displays or image only while active (invisibility shaders, stone/ice/pin displays, Wrathroot, Shivgoroth form, dragon egg): the matcher rejects them (native art) until they end; none is applied at birth to these identities.",
              'sustains_at_birth_review': [
                  {'identity': 'Weirdling Beast', 'sustained': ['Bone Shield', 'Gloom'], 'note': 'temporary values, callbacks and particles only; none writes type/subtype/image/add_mos'},
                  {'identity': 'Slasul', 'sustained': ['Uttercold'], 'note': 'temporary values and particles only'},
                  {'identity': 'Draebor, the Imp', 'sustained': ['Wildfire', 'Bone Shield'], 'note': 'temporary values and particles only'},
                  {'identity': 'Nimisil', 'sustained': ['Hymn of Moonlight (started by the base BASE_NPC_SPIDER resolvers.sustains_at_birth)'], 'note': 'temporary values and particles only'},
                  {'identity': 'Yeek Wayist', 'sustained': ['Kinetic Shield', 'Charged Aura'], 'note': 'temporary values and particles only'},
                  {'identity': 'Pumpkin, the little kitty', 'sustained': [], 'note': 'BASE_NPC_CAT has resolvers.sustains_at_birth() but the leaf has no talents'},
                  {'identity': 'war dog', 'sustained': [], 'note': 'no sustains_at_birth; Grappling Stance is a sustained stance the AI may start in combat (temporary values)'},
                  {'identity': 'caravan merchant, caravan guard, caravan porter, Lost Merchant, Fortress Shadow', 'sustained': [], 'note': 'no sustains_at_birth and no sustained talent'}],
              'auto_classes_review': [
                  {'identity': 'Weirdling Beast', 'class': 'Anorithil, Doomed, Corruptor and Archmage from level 22 (birth/classes/celestial.lua, afflicted.lua, corrupted.lua, mage.lua)', 'finding': "The Corruptor class carries corruption/shadowflame (corrupted.lua:141), whose sustained Flame of Urh'Rok sets demon/major over {horror,eldritch} with __old_type and restores it on deactivation (shadowflame.lua:97-107). Reachable by a class level-up after level 22 and by the AI in combat, not at birth. The other three classes' trees (celestial, cursed, spell) contain no type/subtype/image/add_mos write; Archmage Invisibility applies the transient shader invis_edge (native art while active).", 'outcome': "reported hit; NOT a birth mutation. The entry opts into urh_rok_form (user-approved policy, the same mechanism as Grand Corruptor, elven cultist, Rak'shor and Kor's Fury): the token stays through the exact sustain state over horror/eldritch, and any other body change still falls back to native art."},
                  {'identity': 'Nimisil', 'class': 'Anorithil from level 44 (birth/classes/celestial.lua)', 'finding': 'Anorithil trees (sun/moon/twilight, celestial, cunning/survival): the Twilight jumpgate writes a terrain grid, not an actor; no talent writes type/subtype/image/add_mos/moddable_tile on the caster.', 'outcome': 'no hit'}],
              'visibility_review': 'Nimisil (random inscriptions, e.g. an invisibility rune) and Weirdling Beast (Archmage phantasm Invisibility) can be temporarily shaded through timed effects; the overlay already respects actor visibility and the transient shader rejects the token (native art) until it ends. No identity changes display at birth.',
              'hits_in_batch': ["Weirdling Beast: Flame of Urh'Rok reachable through auto_classes Corruptor (level 22+); urh_rok_form=true set",
                                "Weirdling Beast: Archmage Invisibility applies the transient shader invis_edge (native art while it lasts)"],
              'no_hit': [i['native_name'] for i in identities if i['id'] != 'weirdling-beast']},
          'summons_and_same_body_copies': {
              'method': "grep of every actor definition, static map, quest script and talent under game/modules/tome/data for the twelve names, defines and PNGs; talents that build summons/copies (summon-*, master-of-flesh, rot, thought-forms, simulacra/mirror images, Grand Arrival, clone/cloneFull users) checked for copies of these bodies.",
              'findings': [
                  "None of the twelve names has a second actor definition, a define_as-less same-name leaf, a summon or a clone construct: caravan merchant/guard/porter, Lost Merchant, Nimisil, Slasul, Draebor, Yeek Wayist, Weirdling Beast, Fortress Shadow and Pumpkin each have exactly one definition; war dog has one definition (WAR_DOG, spawned twice by the keepsake quest script through makeEntityByName, so the very same define_as).",
                  "Draebor's summon={type=demon} draws generic demons from the level pool (never Draebor, a unique).",
                  "The war dog PNG canine_dw.png is shared with the dire wolf (general/npcs/canine.lua:75) and the corrupted war dog (keepsake-meadow/npcs.lua:118): different names, so no copy relation; each keeps its own exact entry and none can borrow another's token (negatives pinned in tests/token_mapping.lua).",
                  "The shadow claw family (BASE_SHADOW, keepsake-meadow/npcs.lua:132) reuses humanoid_human_spectator02.png but is undead/shadow with other names: not a caravan copy, stays native.",
                  "Result: no per-construct `variants` entry is needed for this batch."]},
          'name_collisions_checked': [
              {'name': 'caravan merchant / caravan guard / caravan porter', 'other_definitions': ['none; BASE_CARAVANEER is a base without a name; the arena spectators (maps/zones/ring-of-blood.lua spots) and BASE_SHADOW reuse the same spectator PNGs under other types or names'], 'outcome': 'single definitions; bound to define_as CARAVAN_MERCHANT, CARAVAN_GUARD, CARAVAN_PORTER; each entry carries its own explicit PNG so the three cannot borrow one another'},
              {'name': 'Lost Merchant', 'other_definitions': ['none'], 'outcome': 'single actor definition; bound to define_as MERCHANT'},
              {'name': 'Nimisil', 'other_definitions': ['none'], 'outcome': 'single actor definition; bound to define_as NIMISIL'},
              {'name': 'Slasul', 'other_definitions': ['none (achievement text and Slasul\'s note object use the word)'], 'outcome': 'single actor definition; unique tall body pinned by define_as SLASUL'},
              {'name': 'Draebor, the Imp', 'other_definitions': ['none'], 'outcome': 'single actor definition; bound to define_as DRAEBOR'},
              {'name': 'war dog', 'other_definitions': ['none with this name; canine_dw.png is also the dire wolf and the corrupted war dog'], 'outcome': 'single actor definition bound to define_as WAR_DOG; a dire wolf or corrupted war dog body cannot wear it (name and define_as), and it cannot wear theirs'},
              {'name': 'Yeek Wayist', 'other_definitions': ['none (the wayist quest text uses the word)'], 'outcome': 'single actor definition; bound to define_as YEEK_WAYIST; the old tests/token_mapping.lua look-alike negative for it is replaced by the batch T positive plus negatives'},
              {'name': 'Weirdling Beast', 'other_definitions': ['none'], 'outcome': 'single actor definition; bound to define_as WEIRDLING_BEAST'},
              {'name': 'Fortress Shadow', 'other_definitions': ['none'], 'outcome': 'single actor definition; bound to define_as BUTLER; subtype must be exactly "Sher\'Tul"'},
              {'name': 'Pumpkin, the little kitty', 'other_definitions': ['general/encounters/maj-eyal.lua:106 "Lost Kitty" uses the same PNG under another name'], 'outcome': 'single actor definition; bound to define_as KITTY; the Lost Kitty encounter stays native'}],
          'kept_native': [
              {'name': 'Training Dummy', 'define_as': 'TRAINING_DUMMY', 'source': src(SF, 'define_as="TRAINING_DUMMY"'),
               'reason': "the thirteenth 12.0 candidate, left out by family coherence: type training/subtype dummy with explicit npc/lure.png, an inanimate 300000-life practice target with no faction or story and no body family with the other Sher'Tul entries; lure.png is the generic lure image, so a creature-style token would mislead; kept native and open for a later batch."}],
          'neighbours_kept_native': [
              {'name': 'shadow claw, shadow stalker, keepsake shadows', 'reason': 'other names and types (undead/shadow); shadow claw is a section 5.1 same-name conflict'},
              {'name': 'corrupted war dog, dire wolf', 'reason': 'already mapped under their own exact names (batches R and the base set)'},
              {'name': 'Lost Kitty encounter', 'reason': 'another name on the same PNG as Pumpkin'}]}
    out = ADDON / 'evidence/monster-batch-t-20260930/source-contracts.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(ev, indent=2, ensure_ascii=False) + '\n')
    evsha = hashlib.sha256(out.read_bytes()).hexdigest()
    for a in A:
        refs = [{'path': p, 'sha256': sha(p), 'role': r, 'note': n} for r, p, n in a['refs']]
        entry = {'asset_id': a['id'], 'native_name': a['name'], 'scope': a['scope'], 'sources': a['srcs'], 'references': refs,
                 'contrast_dimensions': list(a['dims']),
                 'prompt_fields': {'subject': a['subject'], 'contrast': a['contrast'], 'composition': a['comp'] or COMP, 'palette': a['palette']},
                 'kind': 'creature', 'max_attempts': 1, 'gate': 'ready',
                 'gate_reason': f"Exact source identity re-verified directly against game/modules/tome source (name={a['name']}, define_as={a['define_as']}, type={a['type']}/subtype={a['subtype']}, unique={a['unique']}, native_tall={a['native_tall']}); details and hashes in evidence/monster-batch-t-20260930/source-contracts.json. {a['structure']}. Exact catalog entry only, never a whole-subtype mapping.",
                 'render_evidence': [{'path': render, 'sha256': evsha}]}
        packs.setdefault(a['pack'], []).append(entry)
    for n, assets in packs.items():
        p = ADDON / f'art/production/batches/monster-batch-t-{n}.json'
        if p.exists():
            print('exists, skipped', p.name)
            continue
        p.write_text(json.dumps({'schema': 1, 'batch_id': f'monster-batch-t-{n}', 'assets': assets}, indent=2, ensure_ascii=False) + '\n')
        print('wrote', p.name)


if __name__ == '__main__':
    build()
