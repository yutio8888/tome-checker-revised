"""Generate the monster-batch-r task packs and the pinned source-contract
evidence (survey-2 follow-up list, next twelve by score: orc necromancer,
Rak'shor, Warmaster Gnarg, orc assassin, weaver young, fate spinner, giant green
ant, giant red ant, quasit, elven warrior, corrupted war dog, grannor'vor; see
SELECTION.md). Pure bookkeeping: hashes native sources/sprites, writes JSON.
Retry packs are appended by later edits of retries.py (never overwritten)."""
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


COMP = ("One compact complete creature on a single circular tabletop disc, steep overhead three-quarter camera; visible clear neutral base ring on every side. Keep all anatomy and equipment well inside the inner four-fifths of disc radius. Base brightness must visually match reference neutral disc, with no illumination spill or ground effects. Disc plate discipline: measured results show generations of this style reference tend to render the disc DARKER than the reference, never lighter. So do not darken the disc at all: render the neutral disc -- including the whole outer-sixth ring band and the area under the creature -- at the style reference's own brightness, if anything a hair lighter, and never darker. No warm cast, glow, bounce-light, gradient or vignette anywhere on the disc. Do not darken the creature to compensate either. Add no warm cast, glow, bounce-light, gradient or vignette to the disc anywhere, including directly under or behind dark-bodied creatures.")
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
COMPACT = " Draw the creature COMPACT and chunky: limbs, tails, weapons, staffs and effects are pulled in so the whole silhouette forms one rounded mass inside the inner three quarters of the disc; no tip, blade, staff head, leg or drip reaches the outer sixth ring band or crosses the disc rim."
DEF = ' NPC.lua:33 default-name image (npc/<type>_<subtype>_<name>.png) is the only image source: no image=, nice_tile, add_mos, moddable_tile, shader, anim or add_displays on the leaf or base; generic actor.image==entry.image single path; native sprite 64x64'
EXPL = ' explicit image= on the leaf (no nice_tile, add_mos, moddable_tile, shader, anim or add_displays on the leaf or base); generic actor.image==entry.image single path; native sprite 64x64'
NO_BIRTH = 'no sustains_at_birth and no sustained talent'
RK = 'zones/rak-shor-pride/npcs.lua'
VA = 'zones/vor-armoury/npcs.lua'
OR_, ORK, ORG = 'general/npcs/orc.lua', 'general/npcs/orc-rak-shor.lua', 'general/npcs/orc-grushnak.lua'
MD, SP, AN, EW, HC, CN = 'general/npcs/minor-demon.lua', 'general/npcs/spider.lua', 'general/npcs/ant.lua', 'general/npcs/elven-warrior.lua', 'general/npcs/horror-corrupted.lua', 'general/npcs/canine.lua'
UM, KM = 'zones/unhallowed-morass/npcs.lua', 'zones/keepsake-meadow/npcs.lua'

REF_HATCH = R('weaver-hatchling', 'Shipped weaver hatchling (small pale blue-white spider seen flat from above, legs radiating evenly, glowing leg tips): the weaver young shares its native PNG but must not read as this radially spread pale spider.')
REF_WQUEEN = R('weaver-queen', 'Shipped Weaver Queen (large pure-white spider, legs radiating evenly): no fate weaver token may be a big white radial spider.')
REF_ANT = R('giant-yellow-ant', 'Shipped giant yellow ant (a straight three-segment ant seen from above, legs splayed, antennae forward; the white, brown, blue and black ants use the same pose): the green and red ants must not be this straight recoloured ant.')
REF_CARP = R('giant-carpenter-ant', 'Shipped giant carpenter ant (black ant with huge open mandibles): the red ant must not be a straight ant with big mandibles.')
REF_DW = R('dire-wolf', 'Shipped dire wolf (brown wolf prowling side-on, head level with the shoulders): the corrupted war dog must not be a brown side-on prowling wolf.')
REF_KROGAR = R('krogar', 'Shipped Krogar (brown-armoured orc corruptor standing upright with a staff): the orc necromancer and Rak\'shor must not be a brown armoured staff orc.')
REF_MASSOK = R('massok', 'Shipped Massok the Dragonslayer (black plate orc with horned helm, upright, axe): Warmaster Gnarg must not be an upright black-plate horned orc with an axe.')
REF_WARRIOR = R('orc-warrior', 'Shipped orc warrior (leather-clad green orc with a curved blade): the orc assassin must not be a bare-armed green orc with a curved sword.')
REF_GUARD = R('elven-guard', 'Shipped elven guard (green-tunic elf standing with sword and small shield): the elven warrior must not be a green-tunic sword elf.')
REF_ONILUG = R('onilug', 'Shipped onilug (tall grey gaunt demon with a staff) and wretchling/water imp (small imps): the quasit must not be a gaunt grey demon or a small bright imp.')
REF_CRAWLER = R('slimy-crawler', 'Shipped slimy crawler (green segmented caterpillar-like horror): the grannor\'vor must not be a green segmented crawler.')


# ---- pack 1: four orcs ----
asset(1, 'orc-necromancer', 'orc necromancer',
      "orc-rak-shor.lua (humanoid/orc, non-unique, no define_as, rarity 1, rank 2, base BASE_NPC_ORC_RAK_SHOR, autolevel caster); rak-shor-pride (pool, E13.4), ardhungol, reknor; vault entity filters by name (renegade-undead, greater/orc-necromancer, rak-shor-pride mapscript random_filter)",
      [src(ORK, 'name = "orc necromancer"'), src(ORK, 'resolvers.sustains_at_birth()', after='name = "orc necromancer"')], src(ORK, 'define_as = "BASE_NPC_ORC_RAK_SHOR"'), None, 'humanoid', 'orc', False, False,
      'base BASE_NPC_ORC_RAK_SHOR (humanoid/orc, no image=);' + DEF + '; talents Hiemal Shield, Desolate Waste, Bleak Guard, Blurred Mortality, Soul Leech, Staff Mastery plus one rngtalentsets theme; resolvers.racial() adds only orc racial levelup talents; resolvers.sustains_at_birth() starts Hiemal Shield, Necrotic Aura, Putrescent Liquefaction, Suffer for Me, Erupting Shadows or River of Souls: temporary values, callbacks and particles only, no type/subtype/image/add_mos write',
      'humanoid_orc_orc_necromancer.png',
      [STY, IDN('humanoid_orc_orc_necromancer.png', 'Native shape (64x64): a green-skinned orc in long dark indigo robes with gold trim, hunched and clawed, standing.'), REF_KROGAR],
      "An orc necromancer seen from a steep overhead three-quarter angle: a hunched green-skinned orc leaning forward in long dark indigo-blue robes with pale gold trim and a deep hood thrown back, a heavy brutish brow with small glowing yellow eyes and a jutting lower jaw with two tusks, NO STAFF, one clawed hand stretched forward open with a small floating sphere of sickly green-white soul flame hovering just above the palm, the other hand clenched near the chest, a bone-white skull charm on a cord at the belt, the robe hem flaring round bare clawed feet. Menacing, hunched, spell-casting and complete.",
      "Orc family: the orc NECROMANCER is a HUNCHED CASTER with NO WEAPON and one open hand offering a green soul flame, dark indigo robes (silhouette: bent forward, one arm extended, compact robed mass; hue: dark indigo with pale green flame; value: mid-dark with bright flame). Rak'shor is an UPRIGHT figure with a tall bone-crook staff and spiked shoulders; the orc assassin is a low crouching dark-leather figure with two daggers; Gnarg is a huge horizontal-sword brute. The shipped Krogar is a brown-armoured orc with a staff.",
      "Dark indigo-blue robes with lighter periwinkle highlight planes and pale gold trim, olive-green skin with lighter olive highlights, pale green-white soul flame, bone-white skull charm; nothing darker than dark indigo except the eyes and mouth; keep the robe mid-dark rather than black; the flame must not glow onto or tint the disc." + DISC,
      'READY single (orc necromancer)', comp=COMP + FIT + COMPACT)

asset(1, 'rak-shor', "Rak'shor, Grand Necromancer of the Pride",
      "rak-shor-pride (zones/rak-shor-pride/npcs.lua:32, unique, define_as RAK_SHOR, humanoid/orc, rank 5, guardian of zone.lua:60, default-name image, no nice_tile); single definition (the shadow-crypt CULTIST_RAK_SHOR is another name); auto_classes Necromancer and Corruptor from level 35",
      [src(RK, 'define_as = "RAK_SHOR"'), src(RK, 'name = "Rak\'shor, Grand Necromancer of the Pride"'), src(RK, 'auto_classes={', after='define_as = "RAK_SHOR"'), src(RK, 'resolvers.sustains_at_birth()', after='define_as = "RAK_SHOR"')], src(ORK, 'define_as = "BASE_NPC_ORC_RAK_SHOR"'), 'RAK_SHOR', 'humanoid', 'orc', True, False,
      'base BASE_NPC_ORC_RAK_SHOR (humanoid/orc, no image=); unique with define_as RAK_SHOR;' + DEF + '; resolvers.equip staff, BLACK_ROBE and charm (equipment only, no moddable_tile); talents Summon, Necrotic Aura, Call of the Crypt, Call of the Mausoleum, Lord of Skulls, Discarded Refuse, Corpse Explosion, Assemble, Putrescent Liquefaction, Soul Rot, Blood Grasp, Curse of Vulnerability, Bone Shield, Blood Spray, Staff Mastery, Blighted Summoning, Endless Woes; resolvers.sustains_at_birth() starts Necrotic Aura, Discarded Refuse, Putrescent Liquefaction and Bone Shield (temporary values and particles) plus auto_classes Necromancer/Corruptor (see runtime_mutation_scan)',
      'humanoid_orc_rak_shor__grand_necromancer_of_the_pride.png',
      [STY, IDN('humanoid_orc_rak_shor__grand_necromancer_of_the_pride.png', "Native shape (64x64): an old green orc in purple-blue robes standing upright with a tall bone-crook staff."), REF_KROGAR],
      "Rak'shor, Grand Necromancer of the Pride seen from a steep overhead three-quarter angle: an old towering green-skinned orc standing UPRIGHT and imperious in a heavy black-and-deep-violet robe with a tall stiff spiked collar and bone-white spiked shoulder pauldrons, a bald scarred head with a white braided beard and glowing violet eyes, one hand gripping a TALL BONE STAFF planted upright at his side topped by a curled skull-and-crescent crook, the other hand raised with clawed fingers spread, a chain of small skulls across the chest, the robe falling to the ground in heavy folds. Ancient, commanding, ornate and complete.",
      "Orc family: RAK'SHOR is the UPRIGHT TALL FIGURE with a vertical bone-crook staff, spiked collar and shoulder pauldrons in black and violet (silhouette: vertical staff line beside a wide spiked shoulder mass; hue: black-violet with bone white; value: mid-dark with bright bone accents). The orc necromancer is a hunched staffless caster in indigo with a green flame; the orc assassin is a low crouch; Gnarg is a huge horizontal-sword brute. The shipped Krogar is a brown-armoured orc with a staff.",
      "Deep violet and blue-black robes with lighter violet-grey highlight planes, bone-white spikes, staff and skulls, olive-green skin with lighter olive highlights, glowing violet eyes; nothing darker than dark violet-black except the eye sockets; keep the robe mid-dark rather than black; the disc stays neutral charcoal with no violet cast." + DISC,
      "READY unique with define_as (Rak'shor, RAK_SHOR)", comp=COMP + FIT + COMPACT)

asset(1, 'warmaster-gnarg', 'Warmaster Gnarg',
      'vor-armoury (zones/vor-armoury/npcs.lua:29, unique, define_as GNARG, humanoid/orc, rank 4, base BASE_NPC_ORC_GRUSHNAK, last-level static map guardian, default-name image, no nice_tile); single definition; auto_classes Berserker from level 35',
      [src(VA, 'define_as = "GNARG"'), src(VA, 'name = "Warmaster Gnarg"'), src(VA, 'auto_classes={{class="Berserker"'), src(VA, 'resolvers.sustains_at_birth()', after='define_as = "GNARG"')], src(ORG, 'define_as = "BASE_NPC_ORC_GRUSHNAK"'), 'GNARG', 'humanoid', 'orc', True, False,
      'base BASE_NPC_ORC_GRUSHNAK (humanoid/orc, no image=); unique with define_as GNARG;' + DEF + '; resolvers.equip MURDERBLADE greatsword and massive armour (equipment only, no moddable_tile); talents Giant Leap, Windblade, Rush, Warshout, Stunning Blow, Sunder Armour, Slow Motion, Shattering Shout, Second Wind; resolvers.sustains_at_birth() (leaf and base) starts Slow Motion only (temporary speed values) plus auto_classes Berserker (see runtime_mutation_scan)',
      'humanoid_orc_warmaster_gnarg.png',
      [STY, IDN('humanoid_orc_warmaster_gnarg.png', 'Native shape (64x64): a huge green orc in dark spiked armour hefting a giant greatsword across his body.'), REF_MASSOK],
      "Warmaster Gnarg seen from a steep overhead three-quarter angle: a hulking green-skinned orc warlord in massive dark violet-steel plate armour with tall curved spiked shoulder pauldrons, a heavy tusked scowling face with a crested iron helm, a short tattered crimson cloak, both hands gripping a HUGE WIDE-BLADED SERRATED GREATSWORD held HORIZONTALLY across the front of his body at chest height (the blade a broad pale steel bar with a notched edge, the whole sword no longer than the width of his shoulders and kept inside the disc), legs planted wide in a braced stance. Brutal, massive, armoured and complete.",
      "Orc family: GNARG is a WIDE BRACED BRUTE with a HORIZONTAL greatsword bar across his chest and spiked pauldrons in violet-steel with a crimson cloak (silhouette: broad horizontal bar over a wide shouldered mass; hue: violet-steel plate with crimson and pale steel blade; value: mid with a bright blade). The shipped Massok is an UPRIGHT black-plate horned orc with an axe; the orc soldier is grey plate with a shield; the orc necromancer and Rak'shor are robed casters; the orc assassin is a low crouch.",
      "Violet-tinted steel plate with lighter lavender-grey highlight planes and dark violet recesses, pale steel sword blade, crimson cloak, olive-green skin, gold-brown eyes; nothing darker than dark violet-grey except the eye slits; keep the armour mid-value rather than black; the disc stays neutral charcoal with no violet cast." + DISC,
      'READY unique with define_as (Warmaster Gnarg, GNARG)', comp=COMP + FIT + COMPACT)

asset(1, 'orc-assassin', 'orc assassin',
      'orc.lua (humanoid/orc, non-unique, no define_as, rarity 3, rank 2, base BASE_NPC_ORC, autolevel rogue, color_b randomised 175-195); reknor (pool, E9.2), rak-shor-pride, vor-armoury',
      [src(OR_, 'name = "orc assassin"'), src(OR_, 'resolvers.sustains_at_birth()', after='name = "orc assassin"')], src(OR_, 'define_as = "BASE_NPC_ORC"'), None, 'humanoid', 'orc', False, False,
      'base BASE_NPC_ORC (humanoid/orc, no image=);' + DEF + '; resolvers.equip two daggers and light armour (equipment only); talents Knife Mastery, Stealth, Lethality, Apply Poison, Venomous Strike; resolvers.sustains_at_birth() starts Stealth and Apply Poison: Stealth changes visibility, not display (an actor-visibility matter the overlay already respects, as for the batch J Assassin Lord), no type/subtype/image/add_mos write; color_b is a colour modulation of the same image',
      'humanoid_orc_orc_assassin.png',
      [STY, IDN('humanoid_orc_orc_assassin.png', 'Native shape (64x64): a lean olive-green orc in a loincloth mid-stride with a blade raised.'), REF_WARRIOR],
      "An orc assassin seen from a steep overhead three-quarter angle: a lean sinewy olive-green orc CROUCHED VERY LOW in a stalking crouch, knees deeply bent and one hand almost touching the ground, a dark navy-blue leather hood pulled over the head with a cloth mask across the lower face leaving only narrow glowing yellow eyes and one tusk tip, dark navy leather jerkin with a bandolier of small vials, a short dagger held in each hand in reverse grip pointing back along the forearms, a small green-glinting poison drip on one blade. Stealthy, coiled, blue-black and complete.",
      "Orc family: the orc ASSASSIN is a LOW COILED CROUCH in DARK NAVY hooded leather with two reverse-grip daggers (silhouette: low wide crouch with two short blades pointing back; hue: navy blue-black leather with olive skin and steel; value: mid-dark with pale blade and eye accents). The orc warrior is an upright leather orc with a curved blade; Gnarg is a huge horizontal-sword brute; the necromancer and Rak'shor are robed casters.",
      "Dark navy-blue leather with lighter slate-blue highlight planes, olive-green skin with lighter olive highlights, pale steel daggers, small green poison drip, glowing yellow eyes; nothing darker than dark navy except the eye slits; keep the leather mid-dark rather than black; the disc stays neutral charcoal with no blue cast." + DISC,
      'READY single (orc assassin)', comp=COMP + FIT + COMPACT)

# ---- pack 2: spiders and ants ----
asset(2, 'weaver-young', 'weaver young',
      'spider.lua (spiderkin/spider, non-unique, no define_as, rarity 2, rank 1, size 1, base BASE_NPC_SPIDER); ardhungol (pool, E17.6), daikara, dreadfell, other pools; summoned by weaver escorts (spider.lua:312, :359: name="weaver young"); shares its native PNG with the unhallowed-morass "weaver hatchling" (explicit image=spiderkin_spider_weaver_young.png), a different name that keeps its own catalog entry',
      [src(SP, 'name = "weaver young"'), src(UM, 'name = "weaver hatchling"')], src(SP, 'define_as = "BASE_NPC_SPIDER"'), None, 'spiderkin', 'spider', False, False,
      'base BASE_NPC_SPIDER (spiderkin/spider, no image=);' + DEF + '; talents Spider Web, Lay Web, Spin Fate, Swap (none sustained); ' + NO_BIRTH,
      'spiderkin_spider_weaver_young.png',
      [STY, IDN('spiderkin_spider_weaver_young.png', 'Native shape (64x64): a translucent pale blue fuzzy spider with glowing white orbs at the leg tips.'), REF_HATCH],
      "A weaver young seen from a steep overhead three-quarter angle: a small translucent pale lilac-blue young weaver spider with its legs FOLDED IN and CURLED TIGHT UNDER a big round swollen abdomen like a sitting ball, the abdomen marked with a bold glowing white spiral swirl, a tiny head with four bright pale-blue eyes peeking out at the front, eight short bent legs with bright glowing white tips tucked close, a few thin silver threads of light drawn from the spinnerets and coiled once beside the body. Round, curled, spiral-marked and complete.",
      "Spider family: the weaver YOUNG is a ROUND CURLED BALL with a bold white SPIRAL on the abdomen and legs tucked under (silhouette: one compact round mass, legs almost hidden; hue: pale lilac-blue with white glow; value: light). The shipped weaver hatchling is a small pale blue-white spider with legs radiating evenly; the fate spinner is a large spider with long legs spread wide; the shipped Weaver Queen is a big pure-white radial spider.",
      "Pale lilac-blue translucent body with lighter white-blue highlight planes, glowing white spiral and leg tips, pale blue eyes, thin silver threads; nothing darker than mid slate-blue except the eyes; the glow must not tint the disc." + DISC,
      'READY single (weaver young; same native PNG as weaver hatchling, distinct name)', comp=COMP + FIT + COMPACT)

asset(2, 'fate-spinner', 'fate spinner',
      'unhallowed-morass (zones/unhallowed-morass/npcs.lua:88, spiderkin/spider, non-unique, no define_as, rarity 2, rank 2, size 4, base BASE_NPC_SPIDER; zone-private pool E12.8); single definition',
      [src(UM, 'name = "fate spinner"')], src(SP, 'define_as = "BASE_NPC_SPIDER"'), None, 'spiderkin', 'spider', False, False,
      'base BASE_NPC_SPIDER (spiderkin/spider, no image=);' + DEF + '; talents Dimensional Step, Warp Mine Toward (activated, no display write); ' + NO_BIRTH,
      'spiderkin_spider_fate_spinner.png',
      [STY, IDN('spiderkin_spider_fate_spinner.png', 'Native shape (64x64): a large pale blue-white spider with long jointed legs spread wide.'), REF_WQUEEN],
      "A fate spinner seen from a steep overhead three-quarter angle: a horse-sized steel-blue spider seen crouched LOW and WIDE, a broad flat cephalothorax with six bright cyan-white eyes in two rows, eight long jointed legs SPREAD WIDE in a zigzag star with pale silver joint highlights but each leg bent back sharply so the whole leg span stays inside the disc, a slender pointed abdomen raised behind and a GLOWING SILVER-VIOLET THREAD LOOP forming a small clock-like ring spun between the two front legs, a few short glowing threads trailing back. Wide, threaded, temporal and complete.",
      "Spider family: the fate SPINNER is a LOW WIDE ZIGZAG-LEGGED STAR with a glowing THREAD RING between the front legs, steel-blue (silhouette: flat star with a small ring in front; hue: steel blue with silver-violet thread; value: mid). The weaver young is a tiny round curled ball with a white spiral; the shipped weaver hatchling is a small pale radial spider; the shipped Weaver Queen is a big pure-white radial spider; the giant spider is black.",
      "Steel-blue and slate-blue body with lighter pale-blue highlight planes and silver leg joints, cyan-white eyes, glowing silver-violet thread ring; nothing darker than dark slate-blue except the leg undersides; keep the body mid-value; the thread glow must not tint the disc." + DISC,
      'READY single (fate spinner)', comp=COMP + FIT + COMPACT)

asset(2, 'giant-green-ant', 'giant green ant',
      'ant.lua (insect/ant, non-unique, no define_as, rarity 1, rank 1, base BASE_NPC_ANT, explicit image=npc/green_ant.png); old-forest, maze, ritch-tunnels and 10 more zones (E13.3 total)',
      [src(AN, 'name = "giant green ant"')], src(AN, 'define_as = "BASE_NPC_ANT"'), None, 'insect', 'ant', False, False,
      'base BASE_NPC_ANT (insect/ant, no image=);' + EXPL + '; talent Bite Poison (activated, no display write); ' + NO_BIRTH,
      'green_ant.png',
      [STY, IDN('green_ant.png', 'Native shape (64x64): a straight olive-green ant seen from the side with a big round abdomen.'), REF_ANT],
      "A giant green ant seen from a steep overhead three-quarter angle: a large glossy moss-green ant with its ABDOMEN CURLED FORWARD AND UP over its back like a scorpion tail, the abdomen tip hanging a big bright lime-green venom drop, the whole body forming a C-shaped crescent, a rounded head with two short curved antennae and small mandibles, six bent legs gripping the ground close to the body, pale yellow-green underbelly and glossy dark-green segment edges. Hunched, curled, venomous and complete.",
      "Ant family: the GREEN ant is a C-SHAPED CRESCENT with the ABDOMEN CURLED OVER THE BACK and a dripping venom drop (silhouette: crescent with a hanging tip; hue: moss green with lime venom; value: mid). The red ant is an upright rearing T with raised front legs. The shipped white, yellow, brown, blue and black ants are one straight recoloured ant, and the carpenter ant is a black ant with huge open mandibles: the green ant must not be a straight ant.",
      "Moss-green chitin with lighter lime highlight planes, pale yellow-green underbelly, bright lime venom drop; nothing darker than dark green except the eyes; the venom must not glow onto or tint the disc." + DISC,
      'READY single (giant green ant)', comp=COMP + FIT + COMPACT)

asset(2, 'giant-red-ant', 'giant red ant',
      'ant.lua (insect/ant, non-unique, no define_as, rarity 1, rank 1, base BASE_NPC_ANT, explicit image=npc/red_ant.png); old-forest, maze, ritch-tunnels and 10 more zones (E13.3 total)',
      [src(AN, 'name = "giant red ant"')], src(AN, 'define_as = "BASE_NPC_ANT"'), None, 'insect', 'ant', False, False,
      'base BASE_NPC_ANT (insect/ant, no image=);' + EXPL + '; talent Flame Fury (activated, no display write); ' + NO_BIRTH,
      'red_ant.png',
      [STY, IDN('red_ant.png', 'Native shape (64x64): a straight deep-red ant seen from the side with a big round abdomen.'), REF_ANT, REF_CARP][:3],
      "A giant red ant seen from a steep overhead three-quarter angle: a large glossy crimson-red ant REARED UP on its four hind legs in a fierce upright stance, the two front legs raised high in the air with claws spread and the head thrown back showing wide open serrated mandibles, a big round abdomen behind glowing dull orange along its seams like a heated ember, two bent antennae, orange-red segment edges and a paler orange underbelly. Upright, fierce, fiery and complete.",
      "Ant family: the RED ant is an UPRIGHT REARING T with two raised front legs and wide open mandibles (silhouette: vertical body with raised arms; hue: crimson with orange ember seams; value: mid). The green ant is a curled C-shaped crescent with a venom drop. The shipped white, yellow, brown, blue and black ants are one straight recoloured ant, and the carpenter ant is a black ant with huge open mandibles: the red ant must not be a straight ant.",
      "Crimson-red chitin with lighter orange-red highlight planes, orange glowing seams, pale orange underbelly; nothing darker than dark crimson except the eyes; the ember glow must not tint the disc." + DISC,
      'READY single (giant red ant)', comp=COMP + FIT + COMPACT)

# ---- pack 3: quasit, elven warrior, corrupted war dog, grannor'vor ----
asset(3, 'quasit', 'quasit',
      'minor-demon.lua (demon/minor, non-unique, no define_as, rarity 1, rank 2, size 1, base BASE_NPC_DEMON; only onilug uses nice_tile{tall=1} in this file); valley-moon-caverns (E13.9), demon-plane, crypt-kryl-feijan and 7 more zones; lava_island vault filters by name',
      [src(MD, 'name = "quasit"')], src(MD, 'define_as = "BASE_NPC_DEMON"'), None, 'demon', 'minor', False, False,
      'base BASE_NPC_DEMON (demon/minor, no image=);' + DEF + '; resolvers.equip longsword, shield, heavy armour (equipment only, no moddable_tile); talents Armour Training, Shield Pummel, Riposte, Overpower, Rush (none sustained); ' + NO_BIRTH,
      'demon_minor_quasit.png',
      [STY, IDN('demon_minor_quasit.png', 'Native shape (64x64): a squat brown armoured demon hunched forward, rocky skin.'), REF_ONILUG],
      "A quasit seen from a steep overhead three-quarter angle: a SQUAT stocky heavily armoured minor demon crouched behind a big round bronze-studded shield held out in front of its body, a short broad sword held low behind the shield, its skin dark warm brown and pebbly like rock with thick riveted dark-bronze plate on the shoulders and a spiked back, a big flat head with two short curved horns, a wide grinning mouth with pale fangs and small glowing orange eyes, a stubby tail. Stubborn, heavy, armoured and complete.",
      "Demon family: the QUASIT is a SQUAT ARMOURED BRUISER behind a big round SHIELD, warm brown with bronze plate (silhouette: wide low block with a round shield disc in front and two short horns; hue: warm brown and bronze with pale fangs; value: mid). The onilug is a tall gaunt grey demon with a staff; the wretchling is a small bright yellow imp; the water imp is a small teal imp.",
      "Warm mid-brown pebbly skin with lighter tan highlight planes, dark bronze plates and shield with lighter gold-bronze highlights, pale bone fangs and horn tips, orange eyes; nothing darker than dark brown except the eyes and mouth; keep the body mid-value; the disc stays neutral charcoal with no brown cast." + DISC,
      'READY single (quasit)', comp=COMP + FIT + COMPACT)

asset(3, 'elven-warrior', 'elven warrior',
      'elven-warrior.lua (humanoid/shalore, non-unique, no define_as, rarity 1, rank 2, base BASE_NPC_ELVEN_WARRIOR); crypt-kryl-feijan (pool, E12.7); vault entity filters by name',
      [src(EW, 'name = "elven warrior"')], src(EW, 'define_as = "BASE_NPC_ELVEN_WARRIOR"'), None, 'humanoid', 'shalore', False, False,
      'base BASE_NPC_ELVEN_WARRIOR (humanoid/shalore, no image=);' + DEF + '; resolvers.equip waraxe, shield, heavy armour (equipment only, no moddable_tile); talents Armour Training, Weapon Combat, Weapons Mastery, Shield Pummel; resolvers.racial() adds shalore racial levelup talents (Secrets of the Eternals is sustained but only learnt by level-up, not at birth: the leaf has no sustains_at_birth); ' + NO_BIRTH,
      'humanoid_shalore_elven_warrior.png',
      [STY, IDN('humanoid_shalore_elven_warrior.png', 'Native shape (64x64): a slim elf in full grey plate armour with a tall shield and a long weapon.'), REF_GUARD],
      "An elven warrior seen from a steep overhead three-quarter angle: a slender tall elf sheathed in full polished silver-grey plate armour with gold-cream trim, a closed winged helm with a long pale-blond horsehair plume swept back, a tall kite shield held forward on the left arm with a gold sun crest, a long-hafted single-bladed war axe raised diagonally over the right shoulder, a short cream tabard hanging over the plate, feet planted in a firm guarding stance, pointed ears just visible below the helm. Disciplined, gleaming, heavily armoured and complete.",
      "Shalore family: the elven WARRIOR is a FULLY PLATED SILVER-GREY KNIGHT with a tall crested shield and a diagonal WAR AXE over the shoulder (silhouette: narrow plated figure with a shield edge and a diagonal axe line; hue: silver-grey plate with gold-cream and blond plume; value: light-mid). The shipped elven guard is a green-tunic elf with a sword and small shield; the mean looking elven guard is leather with a sword; the elven mage, tempest and blood mage are robed casters.",
      "Polished silver-grey plate with lighter white-silver highlight planes and cool slate shadows, gold-cream trim and shield crest, pale blond plume, cream tabard, steel axe blade; nothing darker than dark slate-grey except the eye slit; keep the armour light-mid value; the disc stays neutral charcoal with no silver cast." + DISC,
      'READY single (elven warrior)', comp=COMP + FIT + COMPACT)

asset(3, 'corrupted-war-dog', 'corrupted war dog',
      'keepsake-meadow (zones/keepsake-meadow/npcs.lua:118, animal/canine, non-unique, define_as CORRUPTED_WAR_DOG, rank 1, base BASE_NPC_CANINE, explicit image=npc/canine_dw.png, rarity 5 with cave_rarity 5; zone-private pool E12.5); shares the PNG with the dire wolf and with the same zone\'s "war dog" (other names, other catalog state)',
      [src(KM, 'define_as = "CORRUPTED_WAR_DOG"'), src(KM, 'name = "corrupted war dog"'), src(CN, 'name = "dire wolf"')], src(CN, 'define_as = "BASE_NPC_CANINE"'), 'CORRUPTED_WAR_DOG', 'animal', 'canine', False, False,
      'base BASE_NPC_CANINE (animal/canine, no image=); leaf carries define_as CORRUPTED_WAR_DOG, so the entry binds it exactly;' + EXPL + '; talents Rush, Grappling Stance, Clinch (Grappling Stance is sustained but the leaf has no sustains_at_birth, and it writes only temporary values); ' + NO_BIRTH,
      'canine_dw.png',
      [STY, IDN('canine_dw.png', 'Native shape (64x64): a large dark brown dog facing forward, thick-set, ears up, baring teeth.'), REF_DW],
      "A corrupted war dog seen from a steep overhead three-quarter angle: a heavy thick-set black-furred mastiff-type war dog CROUCHED BACK ON ITS HAUNCHES in a coiled pouncing stance, chest low and front paws planted forward, head lowered and turned up toward the viewer with the jaws wide open and slavering, a studded iron collar with a short broken chain, patches of fur torn away to show glowing sickly violet-green veins and cracks running along the ribs, shoulders and muzzle, small glowing green eyes, cropped notched ears, a stiff short tail. Twisted, coiled, corrupted and complete.",
      "Canine family: the corrupted WAR DOG is a COILED POUNCING CROUCH facing the viewer with an open slavering mouth, a spiked collar and glowing violet-green corruption veins on black fur (silhouette: compact haunch-heavy crouch with head forward; hue: black-charcoal fur with violet-green veins; value: mid-dark with bright veins). The shipped dire wolf is a brown wolf prowling SIDE-ON; the shipped warg is a dark grey side-on wolf.",
      "Charcoal-black fur with lighter grey-brown highlight planes on the back and shoulders, glowing violet-green corruption veins, iron studded collar with lighter steel highlights, pale bone teeth, green eyes; nothing darker than very dark charcoal except the mouth interior; keep the fur clearly lighter than the disc rim and mid-value overall, never near-black; the veins must not glow onto or tint the disc." + DISC,
      'READY single with define_as (corrupted war dog, CORRUPTED_WAR_DOG)', comp=COMP + FIT + COMPACT)

asset(3, 'grannor-vor', "grannor'vor",
      "horror-corrupted.lua (horror/corrupted, non-unique, no define_as, rarity 2, rank 2, base BASE_NPC_CORRUPTED_HORROR, clone_on_hit); deep-bellow (E6.8), maze (E5.2); clones made by clone_on_hit are same-name copies of the same actor and keep the same token",
      [src(HC, 'name = "grannor\'vor"'), src(HC, 'resolvers.sustains_at_birth()', after='name = "grannor\'vor"')], src(HC, 'define_as = "BASE_NPC_CORRUPTED_HORROR"'), None, 'horror', 'corrupted', False, False,
      "base BASE_NPC_CORRUPTED_HORROR (horror/corrupted, no image=);" + DEF + "; talents Crawl Acid, Acid Blood (Acid Blood is a passive); resolvers.sustains_at_birth() present but no sustained talent is known; clone_on_hit clones the whole actor (same name/type/image)",
      'horror_corrupted_grannor_vor.png',
      [STY, IDN('horror_corrupted_grannor_vor.png', 'Native shape (64x64): a big blue-grey slug curled in a ring with a melting humanoid face and a curled tail.'), REF_CRAWLER],
      "A grannor'vor seen from a steep overhead three-quarter angle: a big swollen blue-grey slug curled in a fat CRESCENT with its head at one end and its tail curling back beside it, wet glistening teal-grey skin with pale bluish underside folds, at the head a strangely HUMANOID FACE half melted into the body with sunken pale eyes and an open slack mouth, a ridged back with a darker blue-teal mottled pattern, and thick bright acid-green slime dripping from the mouth and pooling in a few small glistening beads right beside the body. Slimy, swollen, melted and complete.",
      "Corrupted horror family: the GRANNOR'VOR is a FAT SMOOTH CRESCENT SLUG with a melted HUMANOID FACE and dripping acid-green slime, blue-grey teal (silhouette: thick crescent with a face at one end; hue: blue-grey teal with acid green drips; value: mid-light). The shipped slimy crawler is a green segmented caterpillar-like horror with many small legs; the drem and dremling are armoured horrors; the brecklorn is an orange bat.",
      "Blue-grey teal skin with lighter pale blue-white highlight planes and darker blue-teal mottling, pale sunken eyes, bright acid-green slime; nothing darker than dark blue-teal except the mouth; keep the body mid-light; the slime must not glow onto or tint the disc." + DISC,
      'READY single (grannor\'vor)', comp=COMP + FIT + COMPACT)


def retry(id_, pack, **changes):
    base = next(a for a in A if a['id'] == id_)
    A.append(dict(base, pack=pack, **changes))


# ---- retry packs are appended below by later edits of retries.py ----
exec((HERE / 'retries.py').read_text()) if (HERE / 'retries.py').exists() else None

PNGF = {i: 'NPC.lua:33 default-name image on the leaf (no image=/nice_tile)' for i in (
    'orc-necromancer', 'rak-shor', 'warmaster-gnarg', 'orc-assassin', 'weaver-young', 'fate-spinner', 'quasit', 'elven-warrior', 'grannor-vor')}
PNGF.update({i: 'explicit image= on the leaf (no nice_tile/add_mos)' for i in ('giant-green-ant', 'giant-red-ant', 'corrupted-war-dog')})


def build():
    packs = {}
    identities = []
    render = 'game/addons/tome-checker-revised/evidence/monster-batch-r-20260929/source-contracts.json'
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
          'task': "monster-batch-r: static re-verification (no game launch) of the twelve identities picked by score from the survey-2 follow-up list (orc necromancer, Rak'shor Grand Necromancer of the Pride, Warmaster Gnarg, orc assassin, weaver young, fate spinner, giant green ant, giant red ant, quasit, elven warrior, corrupted war dog, grannor'vor) against game/modules/tome source and native sprites. Survey verdicts were not trusted; every field below was read from source: name, type/subtype, define_as, explicit or NPC.lua:33 default image, unique, PNG on disk, and absence of moddable_tile/shader/anim/add_displays. Findings: none is native-tall (all native sprites are 64x64, none has nice_tile); Gnarg, Rak'shor and the corrupted war dog carry a define_as that their entries bind exactly; the green/red ants and the war dog use an explicit image=; weaver young shares its native PNG with the shipped weaver hatchling and the war dog shares canine_dw.png with the dire wolf (different names, separate entries); no name collision inside the catalog.",
          'new_ids_not_in_catalog_before_this_batch': [i['id'] for i in identities], 'identities': identities,
          'runtime_mutation_scan': {
              'method': "every talent of each identity (resolvers.talents, inherited base talents, rngtalentsets themes, racial levelup talents, and the auto_classes class talent trees of Rak'shor and Gnarg) was resolved to its definition under game/modules/tome/data/talents and checked for mode=\"sustained\" and for writes to self.type/subtype/image/name/display/shader, __old_type, replace_display, add_mos, add_displays, moddable_tile, textures, anim, addShaderAura, updateModdableTile; timed_effects were grepped for the same fields; the resolvers sustains_at_birth, racial, inscriptions, equip and the base-file talent lists were read. Uber talents (Giant Leap, Windblade, Blighted Summoning, Endless Woes) checked by hand. Text hits in the identities' own talents are only particle \"shader\" strings (Hiemal Shield, Bone Shield, Pride of the Orcs) and Assemble, which defines the add_mos of a bone-giant MINION it summons, not the caster.",
              'writers_found': [
                  {'file': 'game/modules/tome/data/talents/corruptions/shadowflame.lua', 'line': 96, 'talent': "Flame of Urh'Rok", 'effect': 'sustain: __old_type={type,subtype}; type,subtype = demon,major; image untouched; restored on deactivate'},
                  {'file': 'game/modules/tome/data/timed_effects/magical.lua', 'line': 4809, 'talent': 'LORD_OF_SKULLS timed effect', 'effect': 'renames a Necromancer minion (skeleton/bone giant) and swaps its display; not the caster, never applied at birth'}],
              'sustains_at_birth_review': [
                  {'identity': 'orc necromancer', 'sustained': ['Hiemal Shield (glacial-waste.lua)', 'Necrotic Aura', 'Putrescent Liquefaction', 'Suffer for Me', 'Erupting Shadows', 'River of Souls (one rngtalentsets theme)'], 'note': 'temporary values, callbacks and shader/circular particles only; none writes type/subtype/image/add_mos'},
                  {'identity': "Rak'shor, Grand Necromancer of the Pride", 'sustained': ['Necrotic Aura', 'Discarded Refuse', 'Putrescent Liquefaction', 'Bone Shield (bone.lua: shader_shield particle)'], 'note': 'same class of temporary values and particles'},
                  {'identity': 'Warmaster Gnarg', 'sustained': ['Slow Motion (temporary global_speed values)'], 'note': 'no display write'},
                  {'identity': 'orc assassin', 'sustained': ['Stealth', 'Apply Poison'], 'note': 'Stealth is a visibility state (the overlay already respects actor visibility, as for the batch J Assassin Lord); neither writes a display field'},
                  {'identity': "grannor'vor", 'sustained': [], 'note': 'resolvers.sustains_at_birth() present; Crawl Acid is an action and Acid Blood a passive'},
                  {'identity': 'weaver young, fate spinner, ants, quasit, elven warrior, corrupted war dog', 'sustained': [], 'note': 'no sustains_at_birth; the war dog knows Grappling Stance (sustained, temporary values) and the elven warrior racial Secrets of the Eternals only by level-up'}],
              'auto_classes_review': [
                  {'identity': "Rak'shor, Grand Necromancer of the Pride", 'class': 'Necromancer and Corruptor from level 35 (birth/classes/mage.lua, corrupted.lua)', 'finding': "The Corruptor class trees include corruption/shadowflame (learnable-locked, {false, 0.3}); Actor:levelupClass may spend a category point on it (50% pick of an unknown tree) and then learn Flame of Urh'Rok (shadowflame.lua:85, sustained, sets demon/major over {humanoid,orc} with __old_type). The class only levels beyond level 35 (start_level 35; Rak'shor is level_range 35+, so this is reachable mainly after the infinite dungeon raises levels), sustains_at_birth runs once at on_added so a talent learnt later is not auto-activated at birth, and the AI may activate it in combat. The Necromancer trees add sustained talents with particles only; Assemble creates minions. Not observed live (static finding).", 'outcome': "reported hit; NOT a birth mutation. If the sustain ever runs, Rak'shor becomes demon/major, the matcher returns body-changed and he shows native art (urh_rok_form is NOT set on his entry: not observed and not needed); on deactivation type/subtype restore and the token returns"},
                  {'identity': 'Warmaster Gnarg', 'class': 'Berserker from level 35 (birth/classes/warrior.lua)', 'finding': 'Trees strength-of-the-berserker, superiority, warcries, bloodthirst, conditioning and the combat trees: sustained talents Berserker Rage, Precise Strikes, Daunting Presence, Onslaught, Shattering Impact write no display field; the timed effect RAMPAGE (mental.lua:1945) only calls addShaderAura, an already supported aura appearance.', 'outcome': 'no hit beyond the supported aura'}],
              'visibility_review': 'orc assassin: Stealth is a visibility state, not a display write; no identity has invisibility or a phase talent that changes display; random inscriptions are resolvers (no display write)',
              'hits_in_batch': ["Rak'shor: Flame of Urh'Rok reachable through auto_classes Corruptor after level 35 (not at birth; body-changed fallback to native art if it ever runs)",
                                'Warmaster Gnarg: Rampage aura via Berserker auto_class (aura is an already supported appearance)'],
              'no_hit': [i['native_name'] for i in identities if i['id'] not in ('rak-shor', 'warmaster-gnarg')]},
          'name_collisions_checked': [
              {'name': 'orc necromancer', 'other_definitions': ['vault/mapscript random_filters (renegade-undead, greater/orc-necromancer, rak-shor-pride mapscript) filter by name only'], 'outcome': "single actor definition; exact name; Rak'shor Cultist and other robed orcs have other names"},
              {'name': "Rak'shor, Grand Necromancer of the Pride", 'other_definitions': ["shadow-crypt CULTIST_RAK_SHOR is named \"Rak'Shor Cultist\""], 'outcome': 'different name and define_as; single definition; bound to define_as RAK_SHOR'},
              {'name': 'Warmaster Gnarg', 'other_definitions': ["object 'Warmaster Gnarg's Murderblade' is an item"], 'outcome': 'single actor definition; bound to define_as GNARG'},
              {'name': 'orc assassin', 'other_definitions': ['orc master assassin / orc grand master assassin are other names'], 'outcome': 'single definition; exact name'},
              {'name': 'weaver young', 'other_definitions': ['unhallowed-morass "weaver hatchling" uses the same native PNG (explicit image=)'], 'outcome': 'different name: two entries, two tokens, each keyed by its own name; neither borrows the other (negative test); weaver escorts summon "weaver young" by exact name'},
              {'name': 'fate spinner', 'other_definitions': ['fate weaver, weaver patriarch, weaver matriarch are other names'], 'outcome': 'single definition'},
              {'name': 'giant green ant / giant red ant', 'other_definitions': ['giant fire/ice/lightning/acid/army/white/brown/blue/yellow/black/carpenter ant are other names with their own PNGs'], 'outcome': 'exact names; siblings cannot borrow each other or the new ants (negative tests)'},
              {'name': 'quasit', 'other_definitions': ['lava_island vault random_filter by name'], 'outcome': 'single definition'},
              {'name': 'elven warrior', 'other_definitions': ['elven elite warrior, elven guard, mean looking elven guard are other names'], 'outcome': 'single definition'},
              {'name': 'corrupted war dog', 'other_definitions': ['keepsake-meadow "war dog" uses the same native PNG canine_dw.png; the dire wolf catalog entry also has image canine_dw.png'], 'outcome': 'different names; the dog entry is bound to define_as CORRUPTED_WAR_DOG; war dog and dire wolf keep their own state (negative test)'},
              {'name': "grannor'vor", 'other_definitions': ["grannor'vin is another name with another PNG; clone_on_hit clones are the same actor (same name/type/image)"], 'outcome': 'single definition; exact name'}],
          'kept_native': [],
          'neighbours_kept_native': [
              {'name': "war dog (keepsake-meadow), grannor'vin, orc master assassin, orc grand master assassin, fate weaver, weaver patriarch, other ants", 'reason': 'not in the surveyed batch or a later batch'},
              {'name': "Rak'Shor Cultist (shadow-crypt)", 'reason': 'different name; not surveyed'}]}
    out = ADDON / 'evidence/monster-batch-r-20260929/source-contracts.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(ev, indent=2, ensure_ascii=False) + '\n')
    evsha = hashlib.sha256(out.read_bytes()).hexdigest()
    for a in A:
        refs = [{'path': p, 'sha256': sha(p), 'role': r, 'note': n} for r, p, n in a['refs']]
        entry = {'asset_id': a['id'], 'native_name': a['name'], 'scope': a['scope'], 'sources': a['srcs'], 'references': refs,
                 'contrast_dimensions': list(a['dims']),
                 'prompt_fields': {'subject': a['subject'], 'contrast': a['contrast'], 'composition': a['comp'] or COMP, 'palette': a['palette']},
                 'kind': 'creature', 'max_attempts': 1, 'gate': 'ready',
                 'gate_reason': f"Exact source identity re-verified directly against game/modules/tome source (name={a['name']}, define_as={a['define_as']}, type={a['type']}/subtype={a['subtype']}, unique={a['unique']}); details and hashes in evidence/monster-batch-r-20260929/source-contracts.json. {a['structure']}. Exact catalog entry only, never a whole-subtype mapping.",
                 'render_evidence': [{'path': render, 'sha256': evsha}]}
        packs.setdefault(a['pack'], []).append(entry)
    for n, assets in packs.items():
        p = ADDON / f'art/production/batches/monster-batch-r-{n}.json'
        if p.exists():
            print('exists, skipped', p.name)
            continue
        p.write_text(json.dumps({'schema': 1, 'batch_id': f'monster-batch-r-{n}', 'assets': assets}, indent=2, ensure_ascii=False) + '\n')
        print('wrote', p.name)


if __name__ == '__main__':
    build()
