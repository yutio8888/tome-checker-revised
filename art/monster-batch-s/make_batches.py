"""Generate the monster-batch-s task packs and the pinned source-contract
evidence (survey-2 follow-up list, next twelve by score under the batch R rule:
human sun-paladin, High Sun-Paladin Rodmour, Aluin the Fallen, Argoniel, Elandar,
Mindworm, Berethh, Companion Warrior, Companion Archer, Greater Mummy Lord, Kor's
Fury, Borfast the Broken; see SELECTION.md). Pure bookkeeping: hashes native
sources/sprites, writes JSON. Retry packs are appended by later edits of
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
COMPACT = " Draw the creature COMPACT and chunky: limbs, weapons, staffs, capes and effects are pulled in so the whole silhouette forms one rounded mass inside the inner three quarters of the disc; no tip, blade, staff head, cape end or bandage tail reaches the outer sixth ring band or crosses the disc rim."
BRIGHT = " Value discipline (measured lesson from earlier tokens): the creature's large masses are MID-LIGHT to LIGHT in value, clearly LIGHTER than the charcoal disc, with broad pale highlight planes on every upper-left surface, so the silhouette reads as a bright shape on the dark disc at very small size. Nothing near-black except tiny eye slits and thin seams; no black cloth, black leather, black armour or black fur anywhere."
DEF = ' NPC.lua:33 default-name image (npc/<type>_<subtype>_<name>.png) is the only image source: no image=, nice_tile, add_mos, moddable_tile, shader, anim or add_displays on the leaf or base; generic actor.image==entry.image single path; native sprite 64x64'
EXPL = ' explicit image= on the leaf (no nice_tile, add_mos, moddable_tile, shader, anim or add_displays on the leaf or base); generic actor.image==entry.image single path; native sprite 64x64'
TALL = ' NPC.lua:33 default-name image on the leaf; resolvers.nice_tile{image="invis.png", add_mos={{image="npc/<type>_<subtype>_<name>.png", display_h=2, display_y=-1}}} (an explicit tall body, keys image/display_h/display_y only; with nicer_tiles off nice_tile is a no-op and the default-name image is the single path); no moddable_tile, shader, anim or add_displays; native sprite 64x128; non-unique so the catalog entry carries native_tall=true'
NO_BIRTH = 'no sustains_at_birth and no sustained talent'
CS, TM, KM = 'zones/charred-scar/npcs.lua', 'zones/trollmire/npcs.lua', 'zones/keepsake-meadow/npcs.lua'
NC, AE, KP, DF = 'zones/noxious-caldera/npcs.lua', 'zones/ancient-elven-ruins/npcs.lua', 'zones/ruins-kor-pul/npcs.lua', 'zones/dreadfell/npcs.lua'
HP = 'zones/high-peak/npcs.lua'

REF_ELFW = R('elven-warrior', 'Shipped elven warrior (slender silver-plate elf with a winged plumed helm, a tall kite shield and a diagonal war axe): no sun-paladin token may be a silver plate knight with a kite shield and an axe.')
REF_EMAGE = R('elven-mage', 'Shipped elven mage (purple-robed elf standing upright with a vertical staff): no sorcerer token may be a purple robed figure with a vertical staff.')
REF_EBLOOD = R('elven-blood-mage', 'Shipped elven blood mage (grey-robed elf with blood-red streaks, hands lowered): Elandar must not be a grey robed elf with lowered hands.')
REF_NECRO = R('necromancer', 'Shipped necromancer (grey hooded human with a staff): Mindworm must not be a grey hooded standing caster.')
REF_GUARD = R('elven-guard', 'Shipped elven guard (green-tunic elf standing upright with a sword and small shield): no Keepsake elf may be a standing green-tunic swordsman.')
REF_SKELW = R('armoured-skeleton-warrior', 'Shipped armoured skeleton warrior (bony undead in plate with sword and shield): the Greater Mummy Lord must not be a bone-and-plate skeleton.')
REF_SHADE = R('shade-of-telos', 'Shipped Shade of Telos (upright translucent ice-blue humanoid figure): Kor\'s Fury must not be an upright blue humanoid ghost.')
REF_GHOUL = R('ghoul', 'Shipped ghoul (bare hunched grey-brown ghoul crawling on all fours): Borfast must not be a bare crawling ghoul.')

# ---- pack 1: sunwall knights ----
asset(1, 'human-sun-paladin', 'human sun-paladin',
      "charred-scar (zones/charred-scar/npcs.lua:50, humanoid/human, non-unique, define_as SUN_PALADIN_DEFENDER, rank 3, base BASE_NPC_SUNWALL_DEFENDER, faction sunwall); placed by the static map maps/zones/charred-scar.lua:24; a same-name 'human sun-paladin' without define_as exists in the Gates of Morning town (general/npcs/sunwall-town.lua:81) and stays native by the define_as binding",
      [src(CS, 'name = "human sun-paladin"'), src(CS, 'self:useTalent(self.T_WEAPON_OF_LIGHT)', after='define_as = "SUN_PALADIN_DEFENDER"')], src(CS, 'define_as = "BASE_NPC_SUNWALL_DEFENDER"'), 'SUN_PALADIN_DEFENDER', 'humanoid', 'human', False, False,
      'base BASE_NPC_SUNWALL_DEFENDER (humanoid/human, no image=);' + DEF + '; resolvers.equip mace, shield and massive armour (equipment only, no moddable_tile); talents Armour Training, Chant of Fortress, Searing Light, Martyrdom, Weapon of Light, Firebeam, Weapon Combat, Healing Light; no sustains_at_birth and no auto_classes on the leaf or base; on_added uses Weapon of Light and Chant of Fortress once (sustains: temporary values, callbacks and particles only, no display write)',
      'humanoid_human_human_sun_paladin.png',
      [STY, IDN('humanoid_human_human_sun_paladin.png', 'Native shape (64x64): a broad human in grey plate armour with a sword raised and a round shield.'), REF_ELFW],
      "A human sun-paladin seen from a steep overhead three-quarter angle: a broad-shouldered human knight in polished WARM GOLD-YELLOW plate armour with a plain white cloth tabard bearing a small gold sunburst, a BARE short-haired blond head with a strong jaw and no helm, a big ROUND SUNBURST SHIELD (a circular gold disc with short radiating spikes around the rim) held out FORWARD on the left arm, a heavy round-headed flanged mace raised behind the right shoulder, a short white cape trailing behind, feet planted wide in a braced advancing stance. Radiant, sturdy, golden and complete.",
      "Human knights: the sun-paladin is the WARM GOLD knight with a big ROUND SUNBURST SHIELD forward and a mace behind the head, bare blond head (silhouette: round shield mass in front plus a mace head behind the shoulder, no helm and no plume; hue: warm gold and white; value: light). The shipped elven warrior is a slender SILVER elf with a winged helm, plume, KITE shield and axe: this must not be silver, not slender and not a kite shield with an axe. High Sun-Paladin Rodmour is ivory with a violet cloak and a vertical planted sword; Aluin is a hunched tarnished bronze knight with a dragging axe.",
      "Warm gold-yellow plate with pale butter-yellow highlight planes and amber shadows, white cloth tabard and cape, blond hair, steel mace head with pale highlights; nothing darker than dark amber-brown except the eyes and seams; the disc stays neutral charcoal with no golden cast." + DISC,
      "READY single with define_as (human sun-paladin, SUN_PALADIN_DEFENDER)", comp=COMP + FIT + COMPACT + BRIGHT)

asset(1, 'high-sun-paladin-rodmour', 'High Sun-Paladin Rodmour',
      'charred-scar (zones/charred-scar/npcs.lua:80, unique, define_as SUN_PALADIN_DEFENDER_RODMOUR, humanoid/human, rank 3, base BASE_NPC_SUNWALL_DEFENDER); placed by maps/zones/charred-scar.lua:25; single definition',
      [src(CS, 'define_as = "SUN_PALADIN_DEFENDER_RODMOUR"'), src(CS, 'name = "High Sun-Paladin Rodmour"'), src(CS, 'self:doEmote(("Go %s! We will hold the line!")', after='define_as = "SUN_PALADIN_DEFENDER_RODMOUR"')], src(CS, 'define_as = "BASE_NPC_SUNWALL_DEFENDER"'), 'SUN_PALADIN_DEFENDER_RODMOUR', 'humanoid', 'human', True, False,
      'base BASE_NPC_SUNWALL_DEFENDER (humanoid/human, no image=); unique with define_as SUN_PALADIN_DEFENDER_RODMOUR;' + DEF + '; resolvers.equip mace, shield and massive armour (equipment only, no moddable_tile); talents Armour Training, Chant of Fortress, Searing Light, Martyrdom, Weapon of Light, Firebeam, Weapon Combat, Healing Light; no sustains_at_birth and no auto_classes; on_added uses Weapon of Light and Chant of Fortress once (temporary values and particles)',
      'humanoid_human_high_sun_paladin_rodmour.png',
      [STY, IDN('humanoid_human_high_sun_paladin_rodmour.png', 'Native shape (64x64): a blond human in silver plate standing upright with a long sword held low.'), REF_ELFW],
      "High Sun-Paladin Rodmour seen from a steep overhead three-quarter angle: an older bearded human commander standing UPRIGHT and rigid in heavy IVORY-WHITE plate armour with gold trim and a large gold sunburst on the breastplate, a thin gold circlet on a bare head with a short grey-blond beard, a wide ROYAL VIOLET cloak with a gold edge spread behind him in a broad triangle, BOTH HANDS resting on the pommel of a long straight broadsword planted POINT-DOWN between his feet (the sword short enough that its pommel sits at chest height and everything stays inside the disc), pale steel blade. Vertical, regal, ivory and violet and complete.",
      "Human knights: RODMOUR is the IVORY-WHITE commander with a VIOLET cloak fanned behind and a broadsword planted point-down held in both hands (silhouette: tall vertical sword line inside a triangular cloak fan, gold circlet, no shield; hue: ivory and violet with gold; value: light with a mid violet fan). The sun-paladin is warm GOLD with a round sunburst shield and a mace; the shipped elven warrior is slender silver with a plume, kite shield and axe; Aluin is a hunched tarnished bronze knight.",
      "Ivory-white plate with pale cream highlight planes and warm grey shadows, gold trim and sunburst, royal violet cloak in a mid-light value with lilac highlight planes and a gold edge, grey-blond hair and beard, pale steel blade; nothing darker than dark violet-grey except the eyes; the disc stays neutral charcoal with no violet or gold cast." + DISC,
      "READY unique with define_as (High Sun-Paladin Rodmour, SUN_PALADIN_DEFENDER_RODMOUR)", comp=COMP + FIT + COMPACT + BRIGHT)

asset(1, 'aluin-the-fallen', 'Aluin the Fallen',
      'trollmire (zones/trollmire/npcs.lua:223, unique, define_as ALUIN, humanoid/human, rank 4, no base, default-name image); backup guardian created by activateBackupGuardian("ALUIN") after Prox/Shax die (only once the player has gone east); single definition; auto_classes Sun Paladin and Cursed from level 36',
      [src(TM, 'define_as = "ALUIN"'), src(TM, 'name = "Aluin the Fallen"'), src(TM, 'resolvers.sustains_at_birth()', after='define_as = "ALUIN"'), src(TM, 'auto_classes={{class="Sun Paladin"', after='define_as = "ALUIN"')], None, 'ALUIN', 'humanoid', 'human', True, False,
      'no base (humanoid/human on the leaf, no image=);' + DEF + '; resolvers.equip waraxe, SANGUINE_SHIELD and massive armour (equipment only, no moddable_tile); talents Armour Training, Weapon Combat, Weapons Mastery, Rush, Blindside, Gloom, Weakness, Dismay, Sanctuary, Chant of Light, Searing Light, Martyrdom, Barrier, Weapon of Light, Crusade, Firebeam, Arcane Might, Irresistible Sun; resolvers.sustains_at_birth() starts the sustained ones (temporary values, callbacks and particles only, no type/subtype/image/add_mos write) plus auto_classes Sun Paladin/Cursed (see runtime_mutation_scan)',
      'humanoid_human_aluin_the_fallen.png',
      [STY, IDN('humanoid_human_aluin_the_fallen.png', 'Native shape (64x64): a dark-haired human in dull grey plate armour standing with a sword.'), REF_ELFW],
      "Aluin the Fallen seen from a steep overhead three-quarter angle: a big human knight HUNCHED and slumped forward with his head bowed and a tangled dark-brown beard, in weathered TARNISHED BRONZE-GREY steel plate armour crusted with dull rust-red bloodstains and one cracked, dented pauldron, a ragged deep-crimson cloak torn at the hem hanging from one shoulder, a heavy double-headed waraxe held LOW in one hand with its blade dragging diagonally down beside his leg, a small round blood-red shield strapped to the other forearm, heavy boots dragging. Broken, grim, tarnished and complete.",
      "Human knights: ALUIN is the HUNCHED, ASYMMETRIC, tarnished bronze-grey knight with a DRAGGING axe, rust-red stains and a torn crimson cloak (silhouette: slumped rounded shoulders with a diagonal axe blade low on one side and a small round red shield; hue: tarnished bronze-grey with crimson and rust; value: mid). The sun-paladin is upright warm gold with a big sunburst shield and a raised mace; Rodmour is ivory with a violet cloak and a vertical planted sword; the shipped elven warrior is slender silver with a kite shield and a raised axe.",
      "Tarnished mid bronze-grey plate with lighter warm-grey highlight planes and dull rust-red stains, a torn deep crimson cloak with brighter red-brown highlight planes, a small blood-red round shield, dark-brown beard, tan skin, pale steel axe blade; nothing darker than dark warm grey except the eyes and seams; keep the armour mid tan-grey rather than black; the disc stays neutral charcoal with no red cast." + DISC,
      "READY unique with define_as (Aluin the Fallen, ALUIN)", comp=COMP + FIT + COMPACT + BRIGHT)

# ---- pack 2: sorcerers ----
asset(2, 'argoniel', 'Argoniel',
      "charred-scar (zones/charred-scar/npcs.lua:218, humanoid/human, define_as ARGONIEL, rank 5, invulnerable static sorcerer, placed by maps/zones/charred-scar.lua:29; explicit nice_tile tall body 64x128) and the identical High Peak final boss (zones/high-peak/npcs.lua:146, same name, define_as, type, image and tall body, outside the 47 surveyed zones); NOT unique in either definition, so the entry carries native_tall=true and binds ARGONIEL",
      [src(CS, 'define_as = "ARGONIEL"'), src(CS, 'name = "Argoniel"', after='define_as = "ARGONIEL"'), src(CS, 'image="npc/humanoid_human_argoniel.png"', after='define_as = "ARGONIEL"'), src(CS, 'resolvers.sustains_at_birth()', after='define_as = "ARGONIEL"'), src(HP, 'define_as = "ARGONIEL"')], None, 'ARGONIEL', 'humanoid', 'human', False, True,
      'no base (humanoid/human on the leaf);' + TALL + '; sorcerers faction, invulnerable; resolvers.equip staff and cloth armour (equipment only); talents Flame, Freeze, Lightning, Manathrust, Inferno, Flameshock, Stone Skin, Strike, Heal, Regeneration, Illuminate, Spellcraft, Arcane Power, Metaflow, Phase Door, Essence of Speed; resolvers.sustains_at_birth() starts the sustained ones (Stone Skin, Illuminate, Spellcraft, Arcane Power and similar: temporary values and particles only); no auto_classes',
      'humanoid_human_argoniel.png',
      [STY, IDN('humanoid_human_argoniel.png', 'Native shape (64x128 tall body): a woman in a violet hood and long robe holding a glowing sword and a tall staff.'), REF_EMAGE],
      "Argoniel seen from a steep overhead three-quarter angle: a female human sorcerer LEANING FORWARD mid-cast, a plum-violet hood up over her head with her pale face and determined mouth visible and a long dark braid swinging, cream-and-plum long robes with gold trim and a gold sash, BOTH HANDS thrust forward together holding one bright glowing AMBER-WHITE FIRE SPHERE at chest height, a short staff with an amber crystal head slung DIAGONALLY across her back (the staff head no higher than her hood), the robe hem flaring round pointed boots. Poised, forward-leaning and complete.",
      "Robed casters: ARGONIEL is a FORWARD-LEANING compact figure with a big bright FIRE SPHERE between both hands and a short staff DIAGONAL across the back, plum and cream (silhouette: leaning mass with a bright sphere out front, no vertical staff line; hue: plum-violet, cream and amber; value: mid-light with a bright sphere). The shipped elven mage is an UPRIGHT purple robed elf with a VERTICAL staff: this must not be an upright purple robe with a vertical staff. Elandar is an upright red-caped figure with two crossed staves; Mindworm is a cross-legged floating psion.",
      "Plum-violet hood and robe in a mid-light value with lilac highlight planes, cream underdress and gold trim, pale skin, dark braid, bright amber-white fire sphere and amber crystal; nothing darker than dark plum except the eyes; the fire sphere must not glow onto or tint the disc." + DISC,
      "READY single native-tall (Argoniel, non-unique, native_tall=true, define_as ARGONIEL)", comp=COMP + FIT + COMPACT + BRIGHT)

asset(2, 'elandar', 'Elandar',
      "charred-scar (zones/charred-scar/npcs.lua:160, humanoid/shalore, define_as ELANDAR, rank 5, invulnerable static sorcerer, placed by maps/zones/charred-scar.lua:28; explicit nice_tile tall body 64x128) and the identical High Peak final boss (zones/high-peak/npcs.lua:56, same name, define_as, type, image and tall body, outside the 47 surveyed zones); NOT unique in either definition, so the entry carries native_tall=true and binds ELANDAR",
      [src(CS, 'define_as = "ELANDAR"'), src(CS, 'name = "Elandar"', after='define_as = "ELANDAR"'), src(CS, 'image="npc/humanoid_shalore_elandar.png"', after='define_as = "ELANDAR"'), src(CS, 'resolvers.sustains_at_birth()', after='define_as = "ELANDAR"'), src(HP, 'define_as = "ELANDAR"')], None, 'ELANDAR', 'humanoid', 'shalore', False, True,
      'no base (humanoid/shalore on the leaf);' + TALL + '; sorcerers faction, invulnerable; resolvers.equip staff and cloth armour (equipment only); talents Flame, Freeze, Lightning, Manathrust, Inferno, Flameshock, Stone Skin, Strike, Heal, Regeneration, Illuminate, Spellcraft, Arcane Power, Metaflow, Phase Door, Essence of Speed; resolvers.sustains_at_birth() starts the sustained ones (temporary values and particles only); no auto_classes',
      'humanoid_shalore_elandar.png',
      [STY, IDN('humanoid_shalore_elandar.png', 'Native shape (64x128 tall body): a gaunt elf in a red cloak and dark tunic holding two glowing staves.'), REF_EBLOOD],
      "Elandar seen from a steep overhead three-quarter angle: a gaunt elegant male shalore sorcerer standing upright, a tall pointed high collar and a spiked silver circlet on long white hair, a deep BRIGHT CRIMSON cloak flaring out behind him in a wide TRIANGULAR FAN, a teal-and-cream tunic with silver clasps beneath, pale skin and a stern narrow face, TWO SHORT STAVES held CROSSED IN AN X in front of his chest, one topped with a glowing pale blue crystal and the other with a glowing green crystal, both staff heads no higher than his shoulders. Severe, upright, crimson and complete.",
      "Robed casters: ELANDAR is an UPRIGHT figure with a wide CRIMSON CLOAK FAN behind and TWO STAVES CROSSED IN AN X on the chest (silhouette: triangular cape fan plus an X of two short lines with glowing tips; hue: bright crimson, teal and cream with blue and green crystals; value: mid with a bright cape). Argoniel is a forward-leaning plum and cream caster holding a fire sphere; the shipped elven mage is a purple robed elf with one vertical staff; the shipped elven blood mage is a grey robed elf with lowered hands.",
      "Bright saturated crimson cloak in a mid value with pinkish-red highlight planes, teal-and-cream tunic, silver clasps and circlet, white hair, pale skin, pale blue and green crystals; nothing darker than dark red-brown except the eyes; the crystals must not glow onto or tint the disc; keep the cloak a bright crimson rather than maroon or black." + DISC,
      "READY single native-tall (Elandar, non-unique, native_tall=true, define_as ELANDAR)", comp=COMP + FIT + COMPACT + BRIGHT)

asset(2, 'mindworm', 'Mindworm',
      'noxious-caldera (zones/noxious-caldera/npcs.lua:37, unique, define_as MINDWORM, humanoid/thalore, rank 3.5, no base, default-name image); placed by zones/noxious-caldera/zone.lua:110 makeEntityByName; single definition; auto_classes Solipsist from level 25',
      [src(NC, 'define_as = "MINDWORM"'), src(NC, 'name = "Mindworm"'), src(NC, 'auto_classes={', after='define_as = "MINDWORM"')], None, 'MINDWORM', 'humanoid', 'thalore', True, False,
      'no base (humanoid/thalore on the leaf, no image=);' + DEF + '; resolvers.equip mindstars (PSIONIC_FURY), amulet, rings and light armour (equipment only, no moddable_tile); talents Sleep, Mind Sear, Solipsism, Feedback Loop, Backlash, Forge Shield, Forge Armor, Biofeedback, Resonance Field, Amplification, Conversion, Psychic Lobotomy, Synaptic Static; no sustains_at_birth; auto_classes Solipsist (see runtime_mutation_scan)',
      'humanoid_thalore_mindworm.png',
      [STY, IDN('humanoid_thalore_mindworm.png', 'Native shape (64x64): a thin thalore in dark teal robes with a spiked collar standing with arms at his sides.'), REF_NECRO],
      "Mindworm seen from a steep overhead three-quarter angle: a thin pale thalore psion LEVITATING CROSS-LEGGED a hand above the ground, hands open and resting on his knees, vacant pale eyes staring past the viewer and long pale-blond hair hanging over his shoulders, a SAGE-GREEN and cream hooded robe with a spiked collar of pale leaf-like blades, TWO glowing pale teal crystal mindstars floating close beside his head, one on each side, at about shoulder height. Vacant, still, floating and complete.",
      "Robed casters: MINDWORM is a ROUND CROSS-LEGGED FLOATING figure with two orbiting crystals, sage green and cream (silhouette: one low round mass with a small head and two bright dots beside it; hue: sage green, cream and pale teal; value: mid-light). Argoniel leans forward with a fire sphere; Elandar is an upright red-caped figure with crossed staves; the shipped necromancer is a grey hooded standing caster with a staff.",
      "Sage-green robe in a mid-light value with pale celadon highlight planes, cream underrobe and collar blades, pale skin, pale-blond hair, pale teal crystals; nothing darker than dark sage-green except the eyes; the crystals must not glow onto or tint the disc; keep the robe sage green rather than dark teal." + DISC,
      "READY unique with define_as (Mindworm, MINDWORM)", comp=COMP + FIT + COMPACT + BRIGHT)

# ---- pack 3: keepsake-meadow ----
asset(3, 'berethh', 'Berethh',
      'keepsake-meadow (zones/keepsake-meadow/npcs.lua:388, unique, define_as BERETHH, humanoid/thalore, rank 4, no base, default-name image); spawned by quests/keepsake.lua:238 makeEntityByName after the caravan quest; single definition',
      [src(KM, 'define_as="BERETHH"'), src(KM, 'name = "Berethh", unique = true'), src(KM, 'resolvers.sustains_at_birth()', after='define_as="BERETHH"')], None, 'BERETHH', 'humanoid', 'thalore', True, False,
      'no base (humanoid/thalore on the leaf, display "p", no image=);' + DEF + '; resolvers.equip longbow, arrows, light armour, gloves and boots (equipment only, no moddable_tile); talents Weapon Combat, Bow Mastery, Shoot, Pinning Shot, Crippling Shot, Dual Arrows, Disengage; resolvers.sustains_at_birth() has no sustained talent to start (all are activated or passive) and resolvers.inscriptions adds a regeneration infusion; no auto_classes',
      'humanoid_thalore_berethh.png',
      [STY, IDN('humanoid_thalore_berethh.png', 'Native shape (64x64): a lean bearded thalore in a dark green-brown tunic and leather holding a bow, wreathed in dark wisps.'), REF_GUARD],
      "Berethh seen from a steep overhead three-quarter angle: a lean thalore archer standing SIDEWAYS at FULL DRAW, a long OLIVE-GREY hooded travel cloak with lighter sage highlight planes thrown back over worn tan leather, a long pale braid, a calm expressionless narrow face, a SHORT recurve bow held out forward-left with the arrow nocked and the string drawn to the cheek (the bow no longer than his own body width, its tips well inside the disc), a leather quiver of pale-fletched arrows on his back, a small silver leaf pin at the cloak throat. Composed, aiming and complete.",
      "Keepsake elves: BERETHH is the standing full-draw archer in an OLIVE-GREY hooded cloak with a short bow held out to one side (silhouette: sideways figure with a bow line and a drawn arm, cloak mass behind; hue: olive-grey, sage and tan; value: mid-light). The Companion Warrior is a low lunging russet swordsman with no bow; the Companion Archer is a kneeling gold-and-green archer aiming upward; the shipped elven guard is an upright green-tunic swordsman with a shield.",
      "Olive-grey cloak in a mid-light value with pale sage highlight planes, tan worn leather with lighter buff highlights, pale-blond braid, pale skin, pale wood bow, cream-fletched arrows, silver pin; nothing darker than dark olive-grey except the eyes; the disc stays neutral charcoal with no green cast." + DISC,
      "READY unique with define_as (Berethh, BERETHH)", comp=COMP + FIT + COMPACT + BRIGHT)

asset(3, 'companion-warrior', 'Companion Warrior',
      'keepsake-meadow (zones/keepsake-meadow/npcs.lua:273, humanoid/thalore, non-unique, define_as BERETHH_WARRIOR, rank 2, base BASE_BERETHH_COMPANION with faction enemies, explicit image=npc/humanoid_elenulach_thief.png); spawned by quests/keepsake.lua:296 after Berethh dies; single definition',
      [src(KM, 'define_as = "BERETHH_WARRIOR"'), src(KM, 'name = "Companion Warrior"'), src(KM, 'image="npc/humanoid_elenulach_thief.png"'), src(KM, 'resolvers.racial()', after='define_as = "BERETHH_WARRIOR"')], src(KM, 'define_as = "BASE_BERETHH_COMPANION"'), 'BERETHH_WARRIOR', 'humanoid', 'thalore', False, False,
      'base BASE_BERETHH_COMPANION (humanoid/thalore, its own image="player/thalore_male.png" is overridden by the leaf);' + EXPL + '; resolvers.equip longsword and light armour (equipment only, no moddable_tile); talents Weapons Mastery, Assault; resolvers.racial() adds thalore racial levelup talents only; ' + NO_BIRTH,
      'humanoid_elenulach_thief.png',
      [STY, IDN('humanoid_elenulach_thief.png', 'Native shape (64x64): a brown-haired commoner in a tan tunic, brown belt and boots, arms down.'), REF_GUARD],
      "A Berethh companion warrior seen from a steep overhead three-quarter angle: a lean pointed-eared elf swordsman in a LOW FORWARD LUNGE, knees bent and weight on the front leg, a steel longsword thrust forward at a low angle in the right hand (the sword short enough that its tip stays well inside the disc), the left hand thrown back for balance, RUSSET-BROWN light leather armour with brass buckles, a bright TEAL scarf whipping back from the neck, tan bracers and boots, short chestnut hair. Aggressive, low, russet and teal and complete.",
      "Keepsake elves: the COMPANION WARRIOR is a LOW LUNGING russet swordsman with a forward sword and a teal scarf, no bow, no cloak (silhouette: low wide diagonal lunge with one sword line; hue: russet brown, teal and steel; value: mid-light). Berethh is a standing olive-grey hooded archer at full draw; the Companion Archer is a kneeling gold-and-green archer; the shipped elven guard is an upright green-tunic swordsman with a shield.",
      "Russet-brown leather in a mid-light value with lighter tan-orange highlight planes, brass buckles, bright teal scarf with pale aqua highlights, steel sword blade, chestnut hair, tan skin; nothing darker than dark russet except the eyes and seams; the disc stays neutral charcoal with no brown cast." + DISC,
      "READY single with define_as (Companion Warrior, BERETHH_WARRIOR)", comp=COMP + FIT + COMPACT + BRIGHT)

asset(3, 'companion-archer', 'Companion Archer',
      'keepsake-meadow (zones/keepsake-meadow/npcs.lua:296, humanoid/thalore, non-unique, define_as BERETHH_ARCHER, rank 2, base BASE_BERETHH_COMPANION with faction enemies, explicit image=npc/humanoid_elf_elven_archer.png); spawned by quests/keepsake.lua:302 after Berethh dies; single definition',
      [src(KM, 'define_as = "BERETHH_ARCHER"'), src(KM, 'name = "Companion Archer"'), src(KM, 'image="npc/humanoid_elf_elven_archer.png"'), src(KM, 'resolvers.racial()', after='define_as = "BERETHH_ARCHER"')], src(KM, 'define_as = "BASE_BERETHH_COMPANION"'), 'BERETHH_ARCHER', 'humanoid', 'thalore', False, False,
      'base BASE_BERETHH_COMPANION (humanoid/thalore, its own image="player/thalore_male.png" is overridden by the leaf);' + EXPL + '; resolvers.equip longbow, arrows and light armour (equipment only, no moddable_tile); talents Bow Mastery, Shoot; resolvers.racial() adds thalore racial levelup talents only; ' + NO_BIRTH,
      'humanoid_elf_elven_archer.png',
      [STY, IDN('humanoid_elf_elven_archer.png', 'Native shape (64x64): an elf in golden plate with a winged helm and a tall bow.'), REF_GUARD],
      "A Berethh companion archer seen from a steep overhead three-quarter angle: a slender pointed-eared elf archer KNEELING on one knee, aiming a SHORT bow upward and to the left at about forty-five degrees with the arrow nocked and drawn (the bow no longer than her body width, both tips well inside the disc), GREEN-AND-GOLD light leather armour over a cream shirt with gold-brown trim, a pale green hood pushed back, a leather quiver full of pale-fletched arrows on the back, bright golden-blond hair tied back, brown boots. Focused, kneeling, green and gold and complete.",
      "Keepsake elves: the COMPANION ARCHER is a KNEELING archer aiming UPWARD, green-and-gold with a pushed-back hood (silhouette: low folded knee mass with a diagonal bow line rising up-left; hue: bright green, gold and cream; value: light). Berethh is a standing olive-grey hooded archer at full draw aimed level; the Companion Warrior is a low russet swordsman; the shipped elven guard is an upright green-tunic swordsman with a shield.",
      "Bright leaf-green leather in a mid-light value with pale lime highlight planes, gold-brown trim, cream shirt, pale green hood, golden-blond hair, pale wood bow, cream-fletched arrows; nothing darker than dark green except the eyes and seams; the disc stays neutral charcoal with no green cast." + DISC,
      "READY single with define_as (Companion Archer, BERETHH_ARCHER)", comp=COMP + FIT + COMPACT + BRIGHT)

# ---- pack 4: undead uniques ----
asset(4, 'greater-mummy-lord', 'Greater Mummy Lord',
      'ancient-elven-ruins (zones/ancient-elven-ruins/npcs.lua:35, unique, define_as GREATER_MUMMY_LORD, undead/mummy, rank 4, no base, default-name image; guardian of zone.lua:49, no rarity); single definition; resolvers.racial("shalore"); auto_classes Bulwark and Archmage from level 30',
      [src(AE, 'define_as = "GREATER_MUMMY_LORD"'), src(AE, 'name = "Greater Mummy Lord"'), src(AE, 'resolvers.racial("shalore")'), src(AE, 'auto_classes={', after='define_as = "GREATER_MUMMY_LORD"')], None, 'GREATER_MUMMY_LORD', 'undead', 'mummy', True, False,
      'no base (undead/mummy on the leaf, no image=);' + DEF + '; resolvers.equip longsword (LONGSWORD_WINTERTIDE), shield, mummy armour and head armour (equipment only, no moddable_tile); talents Armour Training, Shield Pummel, Assault, Overpower, Blinding Speed, Weapons Mastery, Weapon Combat, Freeze, Ice Storm, Invisibility, Rotting Disease, Tricks of the Trade; resolvers.racial("shalore") adds racial levelup talents only; no sustains_at_birth; auto_classes Bulwark/Archmage (see runtime_mutation_scan); a cast Invisibility applies the temporary EFF_INVISIBILITY shader invis_edge (native art while active, not at birth)',
      'undead_mummy_greater_mummy_lord.png',
      [STY, IDN('undead_mummy_greater_mummy_lord.png', 'Native shape (64x64): a mummy wrapped in cream bandages with arms flung wide, surrounded by a purple aura.'), REF_SKELW],
      "The Greater Mummy Lord seen from a steep overhead three-quarter angle: a massive hulking undead lord wrapped head to foot in thick PALE CREAM and sand-coloured linen bandages, ragged bandage tails streaming out to the LEFT behind him as if blown by a strong wind, a BRONZE-GOLD crested crown-helm with a sculpted mask face and two glowing pale blue-white eyes, broad bronze pauldrons over the wrapped shoulders, a ROUND bronze-rimmed shield on the left arm and a wide pale-steel longsword held low across the front of the body in the right hand, feet planted wide. Ancient, regal, bandaged and complete.",
      "Undead uniques: the GREATER MUMMY LORD is the BROAD BANDAGED LORD with a crowned bronze mask, a round shield and a low sword, bandage tails streaming to one side (silhouette: wide shouldered blocky mass with a round shield and a horizontal sword line and a streaming tail; hue: cream linen with bronze and pale blue eyes; value: light). Kor's Fury is a pale spiral-tailed spectre with a skull face; Borfast is a squat armoured grey-green dwarf ghoul with a cage chest; the shipped armoured skeleton warrior is bone in plate.",
      "Cream and sand linen bandages with near-white highlight planes and warm tan shadows, bronze-gold crown-helm, pauldrons and shield rim with lighter gold highlights, pale steel blade, pale blue-white eyes; nothing darker than dark tan-brown except the eye sockets; the disc stays neutral charcoal with no cream cast." + DISC,
      "READY unique with define_as (Greater Mummy Lord, GREATER_MUMMY_LORD)", comp=COMP + FIT + COMPACT + BRIGHT)

asset(4, 'kors-fury', "Kor's Fury",
      "ruins-kor-pul (zones/ruins-kor-pul/npcs.lua:138, unique, define_as KOR_FURY, undead/ghost, rank 4, no base, default-name image; backup guardian created by activateBackupGuardian('KOR_FURY') after The Possessed/The Shade die); single definition; auto_classes Archmage and Corruptor from level 39",
      [src(KP, 'define_as = "KOR_FURY"'), src(KP, 'name = "Kor\'s Fury"'), src(KP, 'auto_classes={{class="Archmage"', after='define_as = "KOR_FURY"')], None, 'KOR_FURY', 'undead', 'ghost', True, False,
      'no base (undead/ghost on the leaf, no image=);' + DEF + '; resolvers.equip staff, light armour and the VOX amulet (equipment only, no moddable_tile); talents Manathrust, Freeze, Tidal Wave, Ice Storm, Burning Hex, Empathic Hex, Curse of Death, Curse of Impotence, Virulent Disease (activated, none sustained); no sustains_at_birth; auto_classes Archmage/Corruptor (see runtime_mutation_scan)',
      'undead_ghost_kor_s_fury.png',
      [STY, IDN('undead_ghost_kor_s_fury.png', "Native shape (64x64): a translucent cyan spectre with flowing shroud and arms held forward."), REF_SHADE],
      "Kor's Fury seen from a steep overhead three-quarter angle: a vengeful insane spectre in a PALE SEA-FOAM GREEN-CYAN semi-translucent form, a BONE-WHITE SKULL FACE with hollow dark eye sockets and a wide screaming open mouth under a ragged hood, two long thin CLAWED ARMS hooked forward with the fingers curled, a few pale ribs glimpsed through the shroud, the lower body a long ragged shroud COILED INTO A TIGHT SPIRAL beneath it like a drill (the whole spiral inside the inner three quarters of the disc). Furious, coiled, spectral and complete.",
      "Undead uniques: KOR'S FURY is a SKULL-FACED SPECTRE with hooked claw arms over a TIGHT SPIRAL TAIL (silhouette: round spiral mass with a small skull head and two forward claws; hue: pale sea-foam cyan-green with bone white; value: light). The shipped Shade of Telos is an UPRIGHT ICE-BLUE humanoid ghost with a smooth face and no spiral tail; the Greater Mummy Lord is a broad cream bandaged lord; Borfast is an armoured dwarf ghoul.",
      "Pale sea-foam green-cyan translucent shroud with near-white highlight planes and mid teal-grey shadows, bone-white skull face and ribs, dark hollow sockets; nothing darker than mid teal-grey except the sockets and mouth; the ghost must not glow onto or tint the disc; keep the body light rather than dark." + DISC,
      "READY unique with define_as (Kor's Fury, KOR_FURY)", comp=COMP + FIT + COMPACT + BRIGHT)

asset(4, 'borfast', 'Borfast the Broken',
      'dreadfell (zones/dreadfell/npcs.lua:210, unique, define_as BORFAST, undead/ghoul, rank 3.5, rarity 50 pool unique, no base, default-name image); single definition',
      [src(DF, 'define_as = "BORFAST"'), src(DF, 'name = "Borfast the Broken"')], None, 'BORFAST', 'undead', 'ghoul', True, False,
      'no base (undead/ghoul on the leaf, faction dreadfell, no image=);' + DEF + '; resolvers.equip mace, shield, BORFAST_CAGE massive armour, head, hands and feet (equipment only, no moddable_tile); talents Shield Pummel, Assault, Rush, Spell Shield, Perfect Strike, Shield Wall, Shield Expertise, Thick Skin, Armour Training, Weapons Mastery, Weapon Combat, Unflinching Resolve, Daunting Presence, Ghoul, Ghoulish Leap, Retch plus Keepsake Phase Door, Willful Strike, Reproach and Mind Sear; ' + NO_BIRTH + ' (Shield Wall is a sustained shield stance started only by the AI: temporary values); no auto_classes',
      'undead_ghoul_borfast_the_broken.png',
      [STY, IDN('undead_ghoul_borfast_the_broken.png', 'Native shape (64x64): a stocky bearded dwarf ghoul in silver plate with a round shield and a raised sword.'), REF_GHOUL],
      "Borfast the Broken seen from a steep overhead three-quarter angle: a SQUAT broad dwarf ghoul standing hunched, sagging PALE GREY-GREEN flesh hanging loosely from the bones, half of the face seared away with a drooping eyeball, a ragged tuft of white-grey beard on the chin, a bare balding head, a scavenged MID-GREY iron plate with a rusted iron CAGE of bars around the chest, a LARGE ROUND IRON-BOSSED SHIELD held forward on the left arm and a spiked flanged mace raised over the right shoulder, heavy boots. Sorrowful, hulking, armoured and complete.",
      "Undead uniques: BORFAST is a SQUAT ARMOURED DWARF with a big ROUND SHIELD forward, a cage chest and a raised mace, grey-green flesh (silhouette: short wide block with a round shield disc in front and a mace head above; hue: pale grey-green flesh with mid steel-grey and rust; value: mid-light). The shipped ghoul and ghoulking are bare crawling ghouls; the Greater Mummy Lord is a tall cream bandaged lord; Kor's Fury is a pale spiral spectre. The sun-paladin also has a round shield: Borfast is grey-green, short and cage-chested, with a ghoul face.",
      "Pale grey-green flesh with lighter sickly highlight planes, mid steel-grey plate and shield with pale highlight planes and rust-brown seams, iron cage bars, white-grey beard tuft, steel mace head; nothing darker than dark slate-grey except the eye socket and seams; keep the plate mid grey rather than black; the disc stays neutral charcoal with no green cast." + DISC,
      "READY unique with define_as (Borfast the Broken, BORFAST)", comp=COMP + FIT + COMPACT + BRIGHT)


def retry(id_, pack, **changes):
    base = next(a for a in A if a['id'] == id_)
    A.append(dict(base, pack=pack, **changes))


# ---- retry packs are appended below by later edits of retries.py ----
exec((HERE / 'retries.py').read_text()) if (HERE / 'retries.py').exists() else None

PNGF = {i: 'NPC.lua:33 default-name image on the leaf (no image=/nice_tile)' for i in (
    'human-sun-paladin', 'high-sun-paladin-rodmour', 'aluin-the-fallen', 'mindworm', 'berethh', 'greater-mummy-lord', 'kors-fury', 'borfast')}
PNGF.update({i: 'explicit image= on the leaf (no nice_tile/add_mos)' for i in ('companion-warrior', 'companion-archer')})
PNGF.update({i: 'NPC.lua:33 default-name image on the leaf plus an explicit resolvers.nice_tile tall body naming the same PNG (invis.png + one add_mos entry, display_h=2, display_y=-1; no-op when nicer_tiles is off)' for i in ('argoniel', 'elandar')})


def build():
    packs = {}
    identities = []
    render = 'game/addons/tome-checker-revised/evidence/monster-batch-s-20260929/source-contracts.json'
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
          'task': "monster-batch-s: static re-verification (no game launch) of the twelve identities picked by the batch R score rule from the survey-2 follow-up list (human sun-paladin, High Sun-Paladin Rodmour, Aluin the Fallen, Argoniel, Elandar, Mindworm, Berethh, Companion Warrior, Companion Archer, Greater Mummy Lord, Kor's Fury, Borfast the Broken) against game/modules/tome source and native sprites. Survey verdicts were not trusted; every field below was read from source: name, type/subtype, define_as, explicit or NPC.lua:33 default image, unique, PNG on disk, and absence of moddable_tile/shader/anim/add_displays. Findings: ten identities are 64x64 single images (Companion Warrior and Archer through an explicit image=, the rest through the default-name image); Argoniel and Elandar are NON-unique native-tall bodies (explicit nice_tile, PNGs 64x128, native_tall=true) that also appear as the identical High Peak final bosses; every define_as is bound by its entry; human sun-paladin shares its name, type and PNG with a define_as-less Gates of Morning town definition that the define_as binding keeps native; no name collision inside the catalog.",
          'new_ids_not_in_catalog_before_this_batch': [i['id'] for i in identities], 'identities': identities,
          'runtime_mutation_scan': {
              'method': "every talent of each identity (resolvers.talents, inherited base talents, racial levelup talents and the auto_classes class talent trees: Sun Paladin, Cursed, Archmage, Corruptor, Bulwark, Solipsist) was resolved under game/modules/tome/data/talents and the trees cursed, celestial, corruption, spell, psionic, technique, cunning and chronomancy were grepped for writes to type/subtype/image/add_mos/add_displays/moddable_tile/replace_display/shader (regex on any receiver, plus the tuple assignment form); timed_effects were grepped for the same fields; the resolvers sustains_at_birth, racial, inscriptions, equip, nice_tile and the base-file talent lists were read; the uber talent Lichform (becomeLich, moddable_tile=skeleton) is no_npc_use and cannot be learnt by an actor.",
              'writers_found': [
                  {'file': 'game/modules/tome/data/talents/corruptions/shadowflame.lua', 'line': 96, 'talent': "Flame of Urh'Rok", 'effect': 'sustain: __old_type={type,subtype}; type,subtype = demon,major; image untouched; restored on deactivate'},
                  {'file': 'game/modules/tome/data/talents/psionic/thought-forms.lua', 'line': 92, 'talent': 'thought-form summons (Solipsist tree)', 'effect': 'sets type/subtype/image/moddable_tile/add_mos on the summoned thought-form minion copied from its summoner, never on the caster'},
                  {'file': 'game/modules/tome/data/talents/chronomancy/anomalies.lua', 'line': 587, 'talent': 'anomaly summons', 'effect': 'creates a separate spawned NPC with another image; not the caster'}],
              'sustains_at_birth_review': [
                  {'identity': 'Aluin the Fallen', 'sustained': ['Gloom', 'Weakness', 'Dismay', 'Sanctuary', 'Chant of Light', 'Martyrdom', 'Barrier', 'Weapon of Light', 'Irresistible Sun'], 'note': 'temporary values, callbacks and particles only; none writes type/subtype/image/add_mos'},
                  {'identity': 'Argoniel', 'sustained': ['Stone Skin', 'Illuminate', 'Spellcraft', 'Arcane Power'], 'note': 'temporary values, light radius and particles only'},
                  {'identity': 'Elandar', 'sustained': ['Stone Skin', 'Illuminate', 'Spellcraft', 'Arcane Power'], 'note': 'same as Argoniel'},
                  {'identity': 'Berethh', 'sustained': [], 'note': 'resolvers.sustains_at_birth() present but the talents are activated or passive (Weapon Combat, Bow Mastery, Shoot, Pinning Shot, Crippling Shot, Dual Arrows, Disengage)'},
                  {'identity': 'human sun-paladin, High Sun-Paladin Rodmour', 'sustained': ['Weapon of Light', 'Chant of Fortress (on_added, once)'], 'note': 'no sustains_at_birth; on_added starts two sustains that add temporary values and particles only'},
                  {'identity': 'Mindworm, Companion Warrior, Companion Archer, Greater Mummy Lord, Kor\'s Fury, Borfast the Broken', 'sustained': [], 'note': 'no sustains_at_birth; Borfast knows Shield Wall (sustained shield stance, temporary values) and the mummy lord and Kor\'s Fury cast spells only in combat'}],
              'auto_classes_review': [
                  {'identity': "Kor's Fury", 'class': 'Archmage and Corruptor from level 39 (birth/classes/mage.lua, corrupted.lua)', 'finding': "The Corruptor trees include corruption/shadowflame (shadowflame.lua:85, sustained Flame of Urh'Rok sets demon/major over {undead,ghost} with __old_type). Reachable only by a class level-up after level 39 (Kor's Fury is level_range 38+), not by sustains_at_birth (the leaf has none), and the AI may activate it in combat. The Archmage trees add phantasm Invisibility (temporary EFF_INVISIBILITY shader invis_edge, native art while active) and spells with particles only.", 'outcome': "reported hit; NOT a birth mutation. If the sustain ever runs, Kor's Fury becomes demon/major, the matcher returns body-changed and shows native art; on deactivation type/subtype restore and the token returns; urh_rok_form is NOT set (not observed, not needed; static finding, same handling as Rak'shor in batch R, decision left to the user)"},
                  {'identity': 'Aluin the Fallen', 'class': 'Sun Paladin and Cursed from level 36 (birth/classes/celestial.lua, afflicted.lua)', 'finding': 'Trees celestial/* and technique/* plus cursed/gloom, slaughter, endless-hunt, strife, cursed-form, unyielding, rampage, predator and fears: the greps found no talent writing type/subtype/image/add_mos/moddable_tile; sustained Cursed talents change only temporary values and particles.', 'outcome': 'no hit'},
                  {'identity': 'Greater Mummy Lord', 'class': 'Bulwark and Archmage from level 30, add_trees spell/ice (birth/classes/warrior.lua, mage.lua)', 'finding': 'Shield/technique trees and spell trees (arcane, aether, fire, wildfire, earth, stone, water, ice, air, storm, phantasm, temporal, meta, divination, conveyance, aegis): no type/subtype/image writes; phantasm Invisibility applies the temporary shader invis_edge (also a native talent of the leaf).', 'outcome': 'no permanent hit; transient invisibility shader falls back to native art while active, exactly like every other invisible actor'},
                  {'identity': 'Mindworm', 'class': 'Solipsist from level 25 (birth/classes/psionic.lua)', 'finding': 'Trees distortion, dream-smith, psychic-assault, slumber, solipsism, thought-forms, dreaming, feedback, mentalism, discharge, dream-forge, nightmare: only thought-forms writes appearance fields and only on the summoned minion copied from the caster.', 'outcome': 'no hit on the caster'}],
              'visibility_review': 'Berethh (Disengage), the mummy lord and Kor\'s Fury (Invisibility) can turn temporarily invisible or shaded through timed effects; the overlay already respects actor visibility, and the transient shader rejects the token (native art) until it ends. No identity changes display at birth.',
              'hits_in_batch': ["Kor's Fury: Flame of Urh'Rok reachable through auto_classes Corruptor after level 39 (not at birth; body-changed fallback to native art if it ever runs)",
                                'Greater Mummy Lord and Kor\'s Fury: cast Invisibility applies the transient shader invis_edge (native art while it lasts)'],
              'no_hit': [i['native_name'] for i in identities if i['id'] not in ('kors-fury', 'greater-mummy-lord')]},
          'name_collisions_checked': [
              {'name': 'human sun-paladin', 'other_definitions': ['general/npcs/sunwall-town.lua:81 (Gates of Morning town): same name, type humanoid/human and default-name PNG, but no define_as (base BASE_NPC_SUNWALL_TOWN); charred-scar SUN_PALADIN_DEFENDER carries the define_as'], 'outcome': 'the entry binds define_as SUN_PALADIN_DEFENDER, so the town definition (no define_as) is identity-changed and keeps native art; negative test pinned; whether the town version should also wear the token is an open question, no name+define_as key extension'},
              {'name': 'High Sun-Paladin Rodmour', 'other_definitions': ['none (High Sun Paladin Aeryn is another name)'], 'outcome': 'single actor definition; bound to define_as SUN_PALADIN_DEFENDER_RODMOUR'},
              {'name': 'Aluin the Fallen', 'other_definitions': ['none'], 'outcome': 'single actor definition; bound to define_as ALUIN'},
              {'name': 'Argoniel', 'other_definitions': ['zones/high-peak/npcs.lua:146: same name, define_as ARGONIEL, type, default-name PNG and the same explicit tall body (level 75+, ROYAL_BLUE colour only)'], 'outcome': 'the two definitions are the same appearance contract, so the exact entry (native_tall=true, define_as ARGONIEL) also covers the High Peak final boss; a runtime change of any field rejects the token; reported to the user'},
              {'name': 'Elandar', 'other_definitions': ['zones/high-peak/npcs.lua:56: same name, define_as ELANDAR, type, default-name PNG and the same explicit tall body'], 'outcome': 'same as Argoniel'},
              {'name': 'Mindworm', 'other_definitions': ['none (the achievement and lore text use the word, not an actor)'], 'outcome': 'single actor definition; bound to define_as MINDWORM'},
              {'name': 'Berethh', 'other_definitions': ['none'], 'outcome': 'single actor definition; bound to define_as BERETHH'},
              {'name': 'Companion Warrior / Companion Archer', 'other_definitions': ['none; their explicit PNGs humanoid_elenulach_thief.png and humanoid_elf_elven_archer.png are used by no other actor definition'], 'outcome': 'single definitions; bound to define_as BERETHH_WARRIOR and BERETHH_ARCHER'},
              {'name': 'Greater Mummy Lord', 'other_definitions': ['none (the other mummies are ancient elven mummy, animated mummy wrappings, rotting mummy and greater mummy, each with its own name)'], 'outcome': 'single actor definition; bound to define_as GREATER_MUMMY_LORD'},
              {'name': "Kor's Fury", 'other_definitions': ['The Shade (SHADE) is another name and stays native'], 'outcome': 'single actor definition; bound to define_as KOR_FURY'},
              {'name': 'Borfast the Broken', 'other_definitions': ['none; ghoul and ghoulking are other names'], 'outcome': 'single actor definition; bound to define_as BORFAST'}],
          'kept_native': [],
          'neighbours_kept_native': [
              {'name': 'Gates of Morning "human sun-paladin" (no define_as), Aeryn, other sunwall defenders', 'reason': 'town or different definitions; the town same-name actor is kept native by the define_as binding'},
              {'name': 'caravan merchant/guard/porter, war dog, Nimisil, Lost Merchant, the Shertul fortress set, Slasul, Draebor, Yeek Wayist', 'reason': 'the other tied 12.0 candidates; not in this batch'}]}
    out = ADDON / 'evidence/monster-batch-s-20260929/source-contracts.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(ev, indent=2, ensure_ascii=False) + '\n')
    evsha = hashlib.sha256(out.read_bytes()).hexdigest()
    for a in A:
        refs = [{'path': p, 'sha256': sha(p), 'role': r, 'note': n} for r, p, n in a['refs']]
        entry = {'asset_id': a['id'], 'native_name': a['name'], 'scope': a['scope'], 'sources': a['srcs'], 'references': refs,
                 'contrast_dimensions': list(a['dims']),
                 'prompt_fields': {'subject': a['subject'], 'contrast': a['contrast'], 'composition': a['comp'] or COMP, 'palette': a['palette']},
                 'kind': 'creature', 'max_attempts': 1, 'gate': 'ready',
                 'gate_reason': f"Exact source identity re-verified directly against game/modules/tome source (name={a['name']}, define_as={a['define_as']}, type={a['type']}/subtype={a['subtype']}, unique={a['unique']}, native_tall={a['native_tall']}); details and hashes in evidence/monster-batch-s-20260929/source-contracts.json. {a['structure']}. Exact catalog entry only, never a whole-subtype mapping.",
                 'render_evidence': [{'path': render, 'sha256': evsha}]}
        packs.setdefault(a['pack'], []).append(entry)
    for n, assets in packs.items():
        p = ADDON / f'art/production/batches/monster-batch-s-{n}.json'
        if p.exists():
            print('exists, skipped', p.name)
            continue
        p.write_text(json.dumps({'schema': 1, 'batch_id': f'monster-batch-s-{n}', 'assets': assets}, indent=2, ensure_ascii=False) + '\n')
        print('wrote', p.name)


if __name__ == '__main__':
    build()
