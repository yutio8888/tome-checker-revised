"""Generate the monster-batch-q task packs and the pinned source-contract
evidence (survey-2 section 7, batch 8: fire/cold/storm/venom drake hatchlings,
sand-drake, Rantha the Abomination, Briagh Great Sand Wyrm, Ukllmswwik the Wise,
fire drake, storm drake, cold drake, venom drake). Pure bookkeeping: hashes
native sources/sprites, writes JSON. Retry packs are appended by later edits of
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
DRAKE = " This is a dragon on a small tabletop disc, drawn COMPACT and chunky: wings, tail, neck and head are pulled in so the whole silhouette forms one rounded mass inside the inner three quarters of the disc; no wing tip, tail tip, claw, horn, drip or flame reaches the outer sixth ring band or crosses the disc rim. Do not spread the wings wider than about two thirds of the disc diameter."
DISC = " Dry neutral charcoal disc with restrained copper-grey bevel, kept a visibly lighter value than the creature's darkest parts so the two never merge."
A = []


def asset(pack, id_, name, scope, srcs, base, define_as, typ, sub, unique, native_tall, structure, native, refs, subject,
          contrast, palette, verdict, dims=('silhouette', 'value', 'hue'), comp=None):
    A.append(dict(comp=comp, pack=pack, id=id_, name=name, scope=scope, srcs=srcs, base=base, define_as=define_as, type=typ,
                  subtype=sub, unique=unique, native_tall=native_tall, structure=structure, native=native, refs=refs,
                  subject=subject, contrast=contrast, palette=palette, verdict=verdict, dims=dims))


STY = ('style', STYLE, 'Approved disc, lighting and camera; do not copy its creature.')
TALL_EXPLICIT = ('resolvers.nice_tile{image="invis.png", add_mos={{image="<png>", display_h=2, display_y=-1}}} names the PNG explicitly (no {tall=1} shorthand and no =BASE=TILE= indirection), '
                 'so the resolved tall body is statically pinnable (same form as the batch K gigantic sandworm tunneler and the batch P snow giants); native sprite 64x128; unique with define_as, so an ordinary unique native-tall entry like Walrog and Healer Astelrid')
RES = src('resolvers.lua', 'function resolvers.calc.nice_tile', root='game/modules/tome/')
FD, CD, SD, VD, SW = 'general/npcs/fire-drake.lua', 'general/npcs/cold-drake.lua', 'general/npcs/storm-drake.lua', 'general/npcs/venom-drake.lua', 'general/npcs/sandworm.lua'
BR, FC, TR_ = 'zones/briagh-lair/npcs.lua', 'zones/flooded-cave/npcs.lua', 'zones/temporal-rift/npcs.lua'


def R(family_id, note):
    return ('family', TOK + family_id + '.png', note)


def IDN(png, note):
    return ('identity', NPC + png, note)


REF_RANTHA = R('rantha', 'Shipped Rantha the Worm (pale silver-blue winged dragon coiled round): the ice element and every cold drake must not read as this pale coiled winged dragon.')
REF_VARSHA = R('varsha', 'Shipped Varsha the Writhing (deep crimson winged dragon, wings folded, coiled): no fire drake may be a deep crimson coiled dragon.')
REF_CSW = R('corrupted-sand-wyrm', 'Shipped Corrupted Sand Wyrm (brown horned serpentine dragon in an S coil): the sand-drake and Briagh must not be a brown S-coiled horned serpent.')

DRAKE_TALK = 'resolvers.drops money only; no sustains_at_birth on the base'
FIRE_BASE = 'base BASE_NPC_FIRE_DRAKE (dragon/fire, no image=)'
COLD_BASE = 'base BASE_NPC_COLD_DRAKE (dragon/cold, no image=)'
STORM_BASE = 'base BASE_NPC_STORM_DRAKE (dragon/storm, no image=)'
VENOM_BASE = 'base BASE_NPC_VENOM_DRAKE (dragon/venom, no image=)'
DEF = ' NPC.lua:33 default-name image (npc/dragon_<subtype>_<name>.png) is the only image source: no image=, nice_tile, add_mos, moddable_tile, shader, anim or add_displays on the leaf or base; generic actor.image==entry.image single path; native sprite 64x64'


def drake_scope(extra):
    return extra


# ---- pack 1: four hatchlings ----
asset(1, 'fire-drake-hatchling', 'fire drake hatchling',
      'fire-drake.lua (dragon/fire, non-unique, define_as FIRE_DRAKE_HATCHLING, rarity 1, rank 1, make_escort of three hatchlings); daikara, charred-scar, vault renegade-wyrmics via the adult escort; the Wyrmic Grand Arrival wild gift (talents/gifts/summon-distance.lua:786) builds an NPC of the same name/type/subtype and explicit PNG WITHOUT define_as: with the define_as bound below it stays native (open decision, reported)',
      [src(FD, 'name = "fire drake hatchling", color=colors.RED'), src(FD, 'define_as = "FIRE_DRAKE_HATCHLING"'), src('talents/gifts/summon-distance.lua', 'name = "fire drake hatchling", faction = self.faction')], src(FD, 'define_as = "BASE_NPC_FIRE_DRAKE"'), 'FIRE_DRAKE_HATCHLING', 'dragon', 'fire', False, False,
      FIRE_BASE + '; leaf carries define_as FIRE_DRAKE_HATCHLING, so the entry binds it exactly;' + DEF + '; no resolvers.talents on the leaf (base has none); on_melee_hit fire only; no sustains_at_birth',
      'dragon_fire_fire_drake_hatchling.png',
      [STY, IDN('dragon_fire_fire_drake_hatchling.png', 'Native shape (64x64): a small red hatchling with a big head, wings folded up behind, sitting upright.'), REF_VARSHA],
      "A fire drake hatchling seen from a steep overhead three-quarter angle: a small chubby baby drake SITTING UPRIGHT on its haunches and facing the camera, a big rounded head with two short stubby horns and large bright amber eyes, a short snout with a wisp of smoke from one nostril, tiny stubby wings folded flat against its back like a short cape, a short thick tail curled around its front feet, bright orange scales with a cream-yellow belly and glowing ember-orange cheeks, dark red horn tips and claws. Small, round, cute-but-dangerous and complete.",
      "Fire family: the fire hatchling is a SITTING UPRIGHT round baby with a big head and folded stub wings (silhouette: compact round upright blob, big head on top; hue: bright orange with cream belly; value: mid-light). The adult fire drake is a long low stalking body with big spread swept-back wings and open flame-breathing jaws in vermilion with black membranes; the shipped Varsha the Writhing is a deep crimson coiled adult with folded wings.",
      "Bright orange scales with lighter yellow-orange highlight planes, cream-yellow belly plates, amber eyes, dark red horn tips and claws; nothing darker than dark red-brown except the pupils; the smoke and ember cheeks must not glow onto or tint the disc." + DISC,
      'READY single with define_as (fire drake hatchling, FIRE_DRAKE_HATCHLING)', comp=COMP + FIT + DRAKE)

asset(1, 'cold-drake-hatchling', 'cold drake hatchling',
      'cold-drake.lua (dragon/cold, non-unique, no define_as, rarity 1, rank 1, make_escort of three hatchlings); daikara, ardhungol, frost-dragon-lair vault (entity filter by name)',
      [src(CD, 'name = "cold drake hatchling", color=colors.WHITE')], src(CD, 'define_as = "BASE_NPC_COLD_DRAKE"'), None, 'dragon', 'cold', False, False,
      COLD_BASE + ';' + DEF + '; no resolvers.talents on the leaf; on_melee_hit cold only; sound tables only; no sustains_at_birth',
      'dragon_cold_cold_drake_hatchling.png',
      [STY, IDN('dragon_cold_cold_drake_hatchling.png', 'Native shape (64x64): a small dark-blue hatchling with a big head and wings folded up, sitting.'), REF_RANTHA],
      "A cold drake hatchling seen from a steep overhead three-quarter angle: a small baby drake CROUCHED LOW ON ALL FOURS in a wary pouncing stance with its chest down and rump slightly raised, head lowered and turned toward the viewer with wide pale eyes and a small open mouth showing tiny fangs, two tiny half-lifted translucent frosted wings held out a little from its back, a row of small pointed icicle spikes along the spine and a short tail with an ice tip, glacier cyan-blue scales with a white frosted belly and pale ice-blue claws. Small, chilly, springy and complete.",
      "Cold family: the cold hatchling is a LOW POUNCING crouch on all fours with tiny half-lifted frosted wings and an icicle spine (silhouette: low wide flat body with head down; hue: saturated glacier cyan with white frost; value: mid-light). The adult cold drake is a heavy hunched mass with high folded wings like a cloak. The hatchlings of the other elements are: fire sitting upright orange, storm rearing violet, venom S-coiled green. The shipped Rantha the Worm is a big pale silver-blue coiled winged dragon.",
      "Saturated glacier cyan-blue scales with lighter white-cyan highlight planes, white frosted belly, pale ice-blue claws and icicle spikes, pale eyes; nothing darker than dark teal blue except the mouth; the frost must not glow onto or tint the disc." + DISC,
      'READY single (cold drake hatchling)', comp=COMP + FIT + DRAKE)

asset(1, 'storm-drake-hatchling', 'storm drake hatchling',
      'storm-drake.lua (dragon/storm, non-unique, no define_as, rarity 1, rank 1, make_escort of three hatchlings); tempest-peak, ardhungol',
      [src(SD, 'name = "storm drake hatchling", color=colors.BLUE')], src(SD, 'define_as = "BASE_NPC_STORM_DRAKE"'), None, 'dragon', 'storm', False, False,
      STORM_BASE + ';' + DEF + '; no resolvers.talents on the leaf; on_melee_hit lightning only; no sustains_at_birth',
      'dragon_storm_storm_drake_hatchling.png',
      [STY, IDN('dragon_storm_storm_drake_hatchling.png', 'Native shape (64x64): a small pale blue-white hatchling with folded wings, sitting.'), REF_RANTHA],
      "A storm drake hatchling seen from a steep overhead three-quarter angle: a small baby drake REARING UP on its hind legs with both forepaws raised and both small wings flared open to the sides (each wing about as long as its body), head tilted up with a wide open squeaking mouth and bright yellow eyes, deep indigo-violet scales with a jagged bright yellow lightning-bolt stripe down the chest and belly and yellow tips on the wing fingers, a short tail with a forked yellow tip, two or three tiny yellow sparks close to the body. Small, jittery, electric and complete.",
      "Storm family: the storm hatchling is REARED UP with small flared wings, indigo-violet with a yellow lightning stripe (silhouette: upright body with two flared side wings, a T shape; hue: deep indigo-violet with yellow; value: mid with bright yellow accents). The adult storm drake is a lean diagonal streak with long narrow swept wings. Fire hatchling is orange sitting, cold hatchling is cyan crouched low, venom hatchling is green S-coiled.",
      "Deep indigo-violet scales with lighter periwinkle highlight planes, bright yellow lightning stripe and wing tips, yellow eyes; nothing darker than dark indigo except the mouth; the sparks must not glow onto or tint the disc." + DISC,
      'READY single (storm drake hatchling)', comp=COMP + FIT + DRAKE)

asset(1, 'venom-drake-hatchling', 'venom drake hatchling',
      'venom-drake.lua (dragon/venom, non-unique, no define_as, rarity 1, rank 1, make_escort of three hatchlings); noxious-caldera, ardhungol',
      [src(VD, 'name = "venom drake hatchling", color=colors.GREEN')], src(VD, 'define_as = "BASE_NPC_VENOM_DRAKE"'), None, 'dragon', 'venom', False, False,
      VENOM_BASE + ';' + DEF + '; no resolvers.talents on the leaf; on_melee_hit acid only; no sustains_at_birth',
      'dragon_venom_venom_drake_hatchling.png',
      [STY, IDN('dragon_venom_venom_drake_hatchling.png', 'Native shape (64x64): a slim green wingless serpent-like hatchling with a raised head and dripping mouth.'), REF_CSW],
      "A venom drake hatchling seen from a steep overhead three-quarter angle: a small slim baby drake coiled in a tight S-CURVE like a serpent, the head raised on a curved neck at the top with a wide open mouth dripping bright green acid, two small wing buds folded flat on its back, poison-green scales with a yellow-orange belly and a row of little dark green spines, glowing yellow eyes, a thin tail curling round to the front. Slender, sinuous, corrosive and complete.",
      "Venom family: the venom hatchling is a SLIM S-COILED serpent-like baby with a raised dripping head (silhouette: S curve with head up; hue: poison green with yellow-orange belly; value: mid). The adult venom drake is a broad hunched four-legged body with folded wings and a low spitting head. The sand-drake is a pale tan flat crawler, not green.",
      "Poison green scales with lighter lime highlight planes, yellow-orange belly, yellow eyes, bright green acid drips inside the disc; nothing darker than dark green except the mouth; the acid must not glow onto or tint the disc." + DISC,
      'READY single (venom drake hatchling)', comp=COMP + FIT + DRAKE)

# ---- pack 2: sand-drake and Ukllmswwik ----
SD_SC = 'sandworm.lua (dragon/sand, non-unique, no define_as, base BASE_NPC_SANDWORM which is vermin/sandworm but the leaf overrides type and subtype; rank 3); briagh-lair, sandworm-lair'
asset(2, 'sand-drake', 'sand-drake', SD_SC,
      [src(SW, 'name = "sand-drake", display'), src(SW, 'type = "dragon", subtype = "sand"', after='name = "sand-drake"')], src(SW, 'define_as = "BASE_NPC_SANDWORM"'), None, 'dragon', 'sand', False, False,
      'base BASE_NPC_SANDWORM (vermin/sandworm, no image=), the leaf overrides type/subtype to dragon/sand;' + DEF + '; talents Sand Breath, Knockback (activated); resolvers ingredient_on_death only; no sustains_at_birth; the wild-gift TREE sand-drake is a talent category, not an actor',
      'dragon_sand_sand_drake.png',
      [STY, IDN('dragon_sand_sand_drake.png', 'Native shape (64x64): a wingless tan dragon-shaped lizard crawling low, long tail curled up behind.'), REF_CSW],
      "A sand-drake seen from a steep overhead three-quarter angle: a wingless dragon-shaped desert lizard prowling low on four heavy splayed clawed legs, a broad flat crocodile-like head held low with small blunt horns and a wide mouth, a row of low dark brown spines along the back, a thick tail curved round beside the body ending in a blunt tip, pale dusty sand-tan and cream scales with a lighter cream belly and darker brown scale edges, no wings at all, a little sand dust on the claws. Heavy, flat, dry and complete.",
      "Sand family: the sand-drake is a PALE TAN WINGLESS FLAT LIZARD prowling on four legs with a low broad head (silhouette: long flat oval with four splayed legs, no wings; hue: pale dusty sand-tan and cream; value: light). The shipped Corrupted Sand Wyrm is a DARK BROWN horned S-coiled serpent; the shipped sandworms are smooth orange worms. Briagh is a golden serpent rearing upright with a violet frill.",
      "Pale dusty sand-tan and cream scales with lighter highlight planes, darker brown scale edges and spines, cream belly, dark eyes; nothing darker than dark brown except the eyes and mouth; the sand dust must not tint the disc." + DISC,
      'READY single (sand-drake; wingless dragon/sand)', comp=COMP + FIT + DRAKE)

asset(2, 'ukllmswwik', 'Ukllmswwik the Wise',
      'flooded-cave (zones/flooded-cave/npcs.lua:25, unique, define_as UKLLMSWWIK, dragon/water, rank 4, faction water-lair, default-name image, no nice_tile); flooded-cave-last map defineTile; single definition; can_talk ukllmswwik',
      [src(FC, 'define_as = "UKLLMSWWIK"'), src(FC, 'name = "Ukllmswwik the Wise"'), src(FC, 'resolvers.sustains_at_birth()')], None, 'UKLLMSWWIK', 'dragon', 'water', True, False,
      'no base (dragon/water leaf); unique with define_as UKLLMSWWIK;' + DEF + '; resolvers.equip Trident of Tides (equipment, the leaf has no moddable_tile); talents Weapon Combat, Knockback, Ice Storm, Freeze, Ice Claw, Icy Skin, Ice Breath, Lightning Breath, Poison Breath, Draconic Will; resolvers.sustains_at_birth() starts Icy Skin only (temporary max_life/armour/on_melee_hit; Draconic Will is an activated effect with a temporary negative_status_effect_immune): no type/subtype/image/add_mos write',
      'dragon_water_ukllmswwik_the_wise.png',
      [STY, IDN('dragon_water_ukllmswwik_the_wise.png', 'Native shape (64x64): a blue-grey shark-headed dragon with folded wings and a trident.'), REF_RANTHA],
      "Ukllmswwik the Wise seen from a steep overhead three-quarter angle: a squat powerful sea-dragon with the head of a shark, a wide toothy mouth with rows of white teeth and small pale eyes, a tall notched dorsal fin along the back, wide finned wings folded like flippers against the flanks, gills on the neck, deep sea-teal and slate blue-grey scales with a cream-white belly and dark blue mottling, four clawed webbed limbs and a heavy finned tail curled round beside him, one clawed hand gripping a golden trident held diagonally across the body with the three tines pointing up-left. Ancient, aquatic and complete.",
      "Dragons of the tokens: Ukllmswwik is the only SHARK-HEADED SEA-TEAL dragon carrying a GOLDEN TRIDENT with a tall dorsal fin (silhouette: fin ridge, shark head, diagonal trident; hue: sea-teal with cream belly and gold; value: mid). The cold drakes are cyan with icicles and no weapon; the shipped Rantha the Worm is a pale silver-blue coiled winged dragon.",
      "Deep sea-teal and slate blue-grey scales with lighter aqua highlight planes, cream-white belly, golden trident, white teeth; nothing darker than dark teal-blue except the eyes and mouth interior; the disc stays neutral charcoal with no teal cast." + DISC,
      'READY unique with define_as (Ukllmswwik the Wise, UKLLMSWWIK)', comp=COMP + FIT + DRAKE)

# ---- pack 3: four adults ----
asset(3, 'fire-drake', 'fire drake',
      'fire-drake.lua (dragon/fire, non-unique, no define_as, rarity 3, rank 2, escorts of hatchlings); charred-scar, daikara, vault renegade-wyrmics (entity filter by name); the Wyrmic Fire Drake summon (talents/gifts/summon-distance.lua:850) builds an NPC of the same name/type/subtype and explicit PNG npc/dragon_fire_fire_drake.png without define_as, summoner set: it matches this entry (existing exact-identity behaviour, open decision reported); fire wyrm and Varsha are other names',
      [src(FD, 'name = "fire drake", color=colors.RED'), src('talents/gifts/summon-distance.lua', 'name = "fire drake", faction = self.faction')], src(FD, 'define_as = "BASE_NPC_FIRE_DRAKE"'), None, 'dragon', 'fire', False, False,
      FIRE_BASE + ';' + DEF + '; talents Wing Buffet, Fire Breath (activated; particle shader only); no sustains_at_birth',
      'dragon_fire_fire_drake.png',
      [STY, IDN('dragon_fire_fire_drake.png', 'Native shape (64x64): a red winged four-legged drake crouching, head low, wings raised behind.'), REF_VARSHA],
      "A fire drake seen from a steep overhead three-quarter angle: a mature drake stalking forward in a low crouch, a long horned head thrust forward with the jaws wide open and a compact cone of orange-yellow flame just inside the disc, BOTH LARGE BAT-LIKE WINGS SPREAD OPEN and swept back to form a wide delta shape with black membranes veined and edged in glowing ember orange, thick bright orange-vermilion scales with a darker charcoal dorsal ridge, cream chest plates, hind legs bent, a long tail sweeping to one side. Aggressive, spread-winged and complete.",
      "Fire family: the ADULT fire drake is a long low STALKING body with WINGS SPREAD wide in a delta and open flaming jaws, bright orange-vermilion with black membranes (silhouette: wide flat delta with head forward; hue: orange with black and ember; value: mid). The fire hatchling is a small SITTING UPRIGHT round baby with folded stub wings. The shipped Varsha the Writhing is a DEEP CRIMSON coiled dragon with FOLDED wings and no flame.",
      "Bright orange-vermilion scales with lighter yellow-orange highlight planes, black wing membranes with ember-orange veins, cream chest plates, yellow-orange flame; nothing darker than the black membranes and charcoal ridge; the flame must not glow onto or tint the disc." + DISC,
      'READY single (fire drake; Wyrmic summon of same name/PNG matches too - open decision)', comp=COMP + FIT + DRAKE)

asset(3, 'cold-drake', 'cold drake',
      'cold-drake.lua (dragon/cold, non-unique, define_as NPC_COLD_DRAKE, rarity 3, rank 2, escorts of hatchlings); daikara, ardhungol, vaults frost-dragon-lair and renegade-wyrmics (entity filters by name); ice wyrm is another name',
      [src(CD, 'name = "cold drake", color=colors.SLATE'), src(CD, 'define_as = "NPC_COLD_DRAKE"')], src(CD, 'define_as = "BASE_NPC_COLD_DRAKE"'), 'NPC_COLD_DRAKE', 'dragon', 'cold', False, False,
      COLD_BASE + '; leaf carries define_as NPC_COLD_DRAKE, so the entry binds it exactly;' + DEF + '; talents Ice Claw (activated), Ice Breath (activated; particle shader only); no sustains_at_birth (Icy Skin is only on the ice wyrm and Ukllmswwik)',
      'dragon_cold_cold_drake.png',
      [STY, IDN('dragon_cold_cold_drake.png', 'Native shape (64x64): a pale ice-blue four-legged drake with wings raised behind and an open mouth.'), REF_RANTHA],
      "A cold drake seen from a steep overhead three-quarter angle: a heavy broad HUNCHED drake squatting low like a rounded boulder with both wings FOLDED HIGH over its back like a shrugged cloak (the wing tips meeting above the spine), a big head lowered to one side with jaws parted and a glint of teeth, thick deep glacier cyan-teal scales with white belly and chest plates, jagged translucent ice crystals jutting from the shoulders and along the spine, pale blue frosted claws, a short heavy tail tucked round the body. Heavy, hunched, icy and complete.",
      "Cold family: the ADULT cold drake is a HEAVY HUNCHED round mass with wings FOLDED HIGH like a cloak and ice crystals on the shoulders (silhouette: rounded boulder with a crest of crystals; hue: deep saturated glacier cyan-teal with white; value: mid). The cold hatchling is a low pouncing crouch with tiny half-lifted wings; the fire drake spreads its wings in a delta; the shipped Rantha the Worm is a pale silver-blue COILED dragon with spread wings: keep the cold drake a stockier, more saturated teal boulder shape, not silver.",
      "Deep saturated glacier cyan-teal scales with lighter aqua highlight planes, white belly plates, translucent pale ice-blue crystals, dark teal shadows; nothing darker than dark teal except the mouth; the ice must not glow onto or tint the disc." + DISC,
      'READY single with define_as (cold drake, NPC_COLD_DRAKE)', comp=COMP + FIT + DRAKE)

asset(3, 'storm-drake', 'storm drake',
      'storm-drake.lua (dragon/storm, non-unique, no define_as, rarity 3, rank 2, escorts of hatchlings); tempest-peak, ardhungol, vault renegade-wyrmics (entity filter by name); storm wyrm is another name',
      [src(SD, 'name = "storm drake", color=colors.BLUE')], src(SD, 'define_as = "BASE_NPC_STORM_DRAKE"'), None, 'dragon', 'storm', False, False,
      STORM_BASE + ';' + DEF + '; talents Lightning Speed (an ACTIVATED talent applying the temporary LIGHTNING_SPEED effect: temporary movement_speed/resists values and a particle, no display write), Lightning Breath (activated; particle shader only); no sustains_at_birth',
      'dragon_storm_storm_drake.png',
      [STY, IDN('dragon_storm_storm_drake.png', 'Native shape (64x64): a pale grey-white four-legged drake with long spread wings and an open mouth.'), REF_RANTHA],
      "A storm drake seen from a steep overhead three-quarter angle: a lean slender mature drake stretched along a DIAGONAL from lower-left to upper-right, head thrown back and up with the jaws open and a forked yellow lightning bolt between the teeth, TWO LONG NARROW POINTED SWALLOW-TAIL WINGS swept back along the body like a jet, a long thin tail, deep royal-violet and indigo scales with a paler lavender belly, bright yellow lightning veins running across the wings and down the flanks, yellow eyes, slim clawed legs tucked in. Streamlined, electric and complete.",
      "Storm family: the ADULT storm drake is a LEAN DIAGONAL STREAK with two long narrow swept wings and a head thrown back, royal violet with yellow lightning veins (silhouette: diagonal narrow dart; hue: violet-indigo with yellow; value: mid-dark with bright yellow). The storm hatchling is a small reared T-shape; the fire drake is a wide delta with flame; the cold drake is a heavy round teal boulder; the venom drake is a broad green hunched body.",
      "Royal violet and indigo scales with lighter lavender highlight planes and belly, bright yellow lightning veins and eyes; nothing darker than dark indigo except the mouth; keep the body mid-value, not near-black; the lightning must not glow onto or tint the disc." + DISC,
      'READY single (storm drake)', comp=COMP + FIT + DRAKE)

asset(3, 'venom-drake', 'venom drake',
      'venom-drake.lua (dragon/venom, non-unique, no define_as, rarity 3, rank 2, escorts of hatchlings); noxious-caldera, ardhungol, vault renegade-wyrmics (entity filter by name); venom wyrm is another name',
      [src(VD, 'name = "venom drake", color=colors.GREEN')], src(VD, 'define_as = "BASE_NPC_VENOM_DRAKE"'), None, 'dragon', 'venom', False, False,
      VENOM_BASE + ';' + DEF + '; talents Acidic Spray, Corrosive Mist, Corrosive Breath, Dissolve (all activated; particle shader only); no sustains_at_birth',
      'dragon_venom_venom_drake.png',
      [STY, IDN('dragon_venom_venom_drake.png', 'Native shape (64x64): an olive yellow-green four-legged drake with folded wings, mouth dripping.'), REF_CSW],
      "A venom drake seen from a steep overhead three-quarter angle: a broad HUNCHED four-legged mature drake with its bat wings FOLDED TIGHT along its back with sharp elbow spikes, a long sinuous neck bent down so the wedge-shaped head hangs LOW with a gaping mouth spitting a glob of bright green acid, dark poison-green scales with sickly yellow-green highlights and a yellow-orange belly, bony spines down the spine, pitted corroded-looking patches on the shoulders, thick clawed legs, a heavy tail curled to one side. Toxic, hunched and complete.",
      "Venom family: the ADULT venom drake is a BROAD HUNCHED FOUR-LEGGED body with tight folded wings and a LOW spitting head on a bent neck, dark poison green (silhouette: broad body with a dangling head and elbow spikes; hue: poison green with yellow-orange; value: mid). The venom hatchling is a slim S-coiled baby with a raised head. The sand-drake is a pale tan wingless flat lizard, not green and with no wings.",
      "Dark poison-green scales with lighter yellow-green highlight planes, yellow-orange belly, bright green acid glob; nothing darker than dark green except the mouth; keep the body mid-value; the acid must not glow onto or tint the disc." + DISC,
      'READY single (venom drake)', comp=COMP + FIT + DRAKE)

# ---- pack 4: Rantha and Briagh ----
asset(4, 'rantha-abomination', 'Rantha the Abomination',
      'temporal-rift (zones/temporal-rift/npcs.lua:73, unique, define_as ABOMINATION_RANTHA, dragon/temporal, rank 3.5, guardian generated from zone.lua:147, resolvers.nice_tile with the explicit PNG in add_mos); single definition; Rantha the Worm is a different unique (RANTHA_THE_WORM, own name and PNG, shipped)',
      [src(TR_, 'define_as = "ABOMINATION_RANTHA"'), src(TR_, 'add_mos = {{image="npc/dragon_temporal_rantha_the_abomination.png"')], None, 'ABOMINATION_RANTHA', 'dragon', 'temporal', True, False,
      'no base (dragon/temporal leaf); ' + TALL_EXPLICIT.replace('<png>', 'npc/dragon_temporal_rantha_the_abomination.png') + '; talents Knockback, Ice Storm, Freeze, Ice Claw, Icy Skin, Ice Breath, Haste, Celerity, Time Dilation; resolvers.sustains_at_birth() starts only Icy Skin (temporary max_life/armour/on_melee_hit values; Haste is activated, Celerity and Time Dilation are passives): no type/subtype/image/add_mos write',
      'dragon_temporal_rantha_the_abomination.png',
      [STY, IDN('dragon_temporal_rantha_the_abomination.png', 'Native shape (64x128 tall): a huge black dragon with raised dark bat wings, grey scaled belly, claws, and a curled tail.'), REF_RANTHA],
      "Rantha the Abomination seen from a steep overhead three-quarter angle: a hulking corrupted dragon reared up and half-crouched with both tattered wings raised and folded in around its shoulders like a torn cloak, a horned skull-like head with the jaws open and glowing cyan-white eyes, dark slate-violet scaled hide broken by glowing cyan-white temporal fissures and cracks across the chest, back and wing membranes as if the body were splitting along time-rift seams, pale bone-white spurs and claws, torn wing edges dissolving into a few small floating cyan fragments kept close to the body, a heavy tail curled at the base. Corrupted, cracked and complete.",
      "Dragons of the tokens: Rantha the ABOMINATION is the SLATE-VIOLET DRAGON CRACKED BY GLOWING CYAN TIME-FISSURES with torn wings raised round the shoulders (silhouette: hunched bulk with two raised tattered wing peaks; hue: dark slate violet with cyan-white cracks and bone spurs; value: mid-dark with bright cracks). The shipped Rantha the Worm is a smooth PALE SILVER-BLUE coiled dragon with no cracks; the cold drakes are saturated cyan teal.",
      "Slate-violet scaled hide with lighter lavender-grey highlight planes, glowing cyan-white fissures, pale bone spurs and claws; nothing darker than dark slate violet except the mouth and wing tears; keep the body mid-dark rather than black; the cracks must not glow onto or tint the disc." + DISC,
      'READY unique native-tall explicit PNG (Rantha the Abomination, ABOMINATION_RANTHA)', comp=COMP + FIT + DRAKE)

asset(4, 'briagh', 'Briagh, Great Sand Wyrm',
      'briagh-lair (zones/briagh-lair/npcs.lua:25, unique, define_as BRIAGH, dragon/sand, rank 4, guardian of zone.lua:48, resolvers.nice_tile with the explicit PNG in add_mos, summons eight sandworms); single definition',
      [src(BR, 'define_as = "BRIAGH"'), src(BR, 'add_mos = {{image="npc/dragon_sand_briagh__great_sand_wyrm.png"'), src(BR, 'resolvers.sustains_at_birth()')], None, 'BRIAGH', 'dragon', 'sand', True, False,
      'no base (dragon/sand leaf); ' + TALL_EXPLICIT.replace('<png>', 'npc/dragon_sand_briagh__great_sand_wyrm.png') + '; talents Summon, Sand Breath, Stun, Knockback (activated) plus auto_classes Summoner from level 35 (see runtime_mutation_scan); resolvers.sustains_at_birth() present but none of its own talents is sustained; resolvers.inscriptions(3,...)',
      'dragon_sand_briagh__great_sand_wyrm.png',
      [STY, IDN('dragon_sand_briagh__great_sand_wyrm.png', 'Native shape (64x128 tall): a golden armoured serpent rearing upright in an S curve with a dragon head and sand streaming down.'), REF_CSW],
      "Briagh, Great Sand Wyrm seen from a steep overhead three-quarter angle: a wingless armoured sand wyrm reared up from a tight spiral of thick coils like a hooded cobra, the front of the body rising in the centre with a broad dragon head bent forward and open jaws, a wide fan-shaped VIOLET-PURPLE frill and crest around the head and neck, glowing violet eyes, bright golden-yellow overlapping armour plates over the whole body with paler cream underplates on the belly, dark amber plate edges, a few grains of sand trickling off the coils kept inside the disc. Towering, golden, regal and complete.",
      "Sand family: BRIAGH is the GOLDEN SERPENT REARED UP FROM A SPIRAL COIL with a big VIOLET FRILL around the head (silhouette: central rising column with a wide fan frill on top, spiral base; hue: golden yellow with violet frill; value: mid-light). The shipped Corrupted Sand Wyrm is a DARK BROWN horned S-coil with no frill; the sandworm destroyer is a smooth ORANGE ring with a toothed round maw; the sand-drake is a pale tan flat wingless lizard.",
      "Bright golden-yellow armour plates with lighter yellow highlight planes, cream belly plates, dark amber plate edges, violet-purple frill and eyes; nothing darker than dark amber except the mouth; the disc stays neutral charcoal with no gold cast." + DISC,
      'READY unique native-tall explicit PNG (Briagh, BRIAGH)', comp=COMP + FIT + DRAKE)


def retry(id_, pack, **changes):
    base = next(a for a in A if a['id'] == id_)
    A.append(dict(base, pack=pack, **changes))


# ---- retry packs are appended below by later edits of retries.py ----
exec((HERE / 'retries.py').read_text()) if (HERE / 'retries.py').exists() else None

PNGF = {i: 'NPC.lua:33 default-name image on the leaf (no image=/nice_tile)' for i in (
    'fire-drake-hatchling', 'cold-drake-hatchling', 'storm-drake-hatchling', 'venom-drake-hatchling', 'sand-drake', 'ukllmswwik',
    'fire-drake', 'cold-drake', 'storm-drake', 'venom-drake')}
PNGF.update({i: 'explicit nice_tile add_mos PNG' for i in ('rantha-abomination', 'briagh')})


def build():
    packs = {}
    identities = []
    render = 'game/addons/tome-checker-revised/evidence/monster-batch-q-20260929/source-contracts.json'
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
          'task': "monster-batch-q: static re-verification (no game launch) of the twelve batch-8 identities of the second gap survey (fire drake hatchling, cold drake hatchling, storm drake hatchling, sand-drake, venom drake hatchling, Rantha the Abomination, Briagh Great Sand Wyrm, Ukllmswwik the Wise, fire drake, storm drake, cold drake, venom drake) against game/modules/tome source and native sprites. Survey verdicts were not trusted; every field below was read from source: name, type/subtype, define_as, explicit or NPC.lua:33 default image, unique, PNG on disk, and absence of moddable_tile/shader/anim/add_displays. Findings: FIRE_DRAKE_HATCHLING and NPC_COLD_DRAKE are non-unique leaves that carry a define_as, so the entries bind it exactly; Ukllmswwik the Wise is a 64x64 single image (no nice_tile) although a unique; Rantha the Abomination and Briagh are unique with an explicit nice_tile PNG (64x128).",
          'new_ids_not_in_catalog_before_this_batch': [i['id'] for i in identities], 'identities': identities,
          'runtime_mutation_scan': {
              'method': 'every talent of each identity (resolvers.talents, inherited base talents, the Briagh auto_classes Summoner class talent trees) was resolved to its definition under game/modules/tome/data/talents and checked for mode="sustained" and for writes to self.type/subtype/image/name/display, __old_type, replace_display, add_mos, add_displays, moddable_tile, shader, textures, anim, updateModdableTile, addShaderAura; the resolvers sustains_at_birth, nice_tile, inscriptions, equip and the base-file talent lists were read. Drake talents (Wing Buffet, Fire Breath, Ice Claw, Ice Breath, Lightning Speed, Lightning Breath, Acidic Spray, Corrosive Mist, Corrosive Breath, Dissolve, Sand Breath, Knockback, Stun, Summon, Ice Storm, Freeze, Draconic Will, Haste, Celerity, Time Dilation, Bellowing Roar, Devouring Flame, Weapon Combat): text hits are only particle "shader" strings (core.shader.active(4) + shader_wings/shader_shield_temp particles), no actor display write. Lightning Speed applies the LIGHTNING_SPEED effect (temporary movement_speed/resists values and a bolt_lightning particle).',
              'writers_found': [],
              'sustains_at_birth_review': [
                  {'identity': 'Ukllmswwik the Wise', 'sustained': ['Icy Skin (talents/gifts/cold-drake.lua)'], 'note': 'temporary max_life, combat_armor and on_melee_hit values only; Draconic Will is an activated talent (temporary negative_status_effect_immune)'},
                  {'identity': 'Rantha the Abomination', 'sustained': ['Icy Skin (talents/gifts/cold-drake.lua)'], 'note': 'same temporary values; Haste is activated, Celerity and Time Dilation are passive'},
                  {'identity': 'Briagh, Great Sand Wyrm', 'sustained': [], 'note': 'resolvers.sustains_at_birth() present, none of Summon, Sand Breath, Stun, Knockback is sustained'},
                  {'identity': 'drakes, hatchlings, sand-drake', 'sustained': [], 'note': 'no sustains_at_birth and no sustained talent'}],
              'auto_classes_review': [
                  {'identity': 'Briagh, Great Sand Wyrm', 'class': 'Summoner from level 35 (birth/classes/wilder.lua): the class talent trees include wild-gift/summon-advanced (Master Summoner, sustained) and wild-gift/mindstar-mastery (Psiblades, sustained). Master Summoner calls Actor:addShaderAura, which stores shader_auras and runs updateModdableTile; for an invis.png+add_mos body that builds a replace_display shader-aura body. Psiblades calls updateModdableTile but only matters for moddable bodies. Native shader auras are an ALREADY SUPPORTED appearance of the addon: CheckerTokens.appearance ignores an add_mos that only carries aura entries (emptyIgnoringAura), the integration rebuilds the aura mos onto the token entity, and tests/token_mapping.lua pins that an active shader_aura keeps every token; any other external replace_display falls back to native art. Whether Briagh actually learns and activates Master Summoner (auto_sustain) was NOT observed live (static finding).', 'outcome': 'reported hit, already supported (aura tokens); Briagh keeps its token with the aura wrapped around it'}],
              'visibility_review': 'no identity of this batch has stealth, invisibility or a phase talent that changes display; random inscriptions are resolvers (no display write)',
              'hits_in_batch': ['Briagh: Master Summoner addShaderAura/updateModdableTile is reachable through auto_classes Summoner (shader aura is an already supported appearance; see auto_classes_review)'],
              'no_hit': [i['native_name'] for i in identities if i['id'] != 'briagh']},
          'name_collisions_checked': [
              {'name': 'fire drake hatchling', 'other_definitions': ['talents/gifts/summon-distance.lua:786 (Wyrmic Grand Arrival escort): same name, dragon/fire and the explicit PNG npc/dragon_fire_fire_drake_hatchling.png but NO define_as and a summoner'], 'outcome': 'the zone leaf carries define_as FIRE_DRAKE_HATCHLING, which the entry binds exactly, so the summon (no define_as) stays native. NOT a decision on summons: reported to the user as an open question; no name+define_as key extension'},
              {'name': 'fire drake', 'other_definitions': ['talents/gifts/summon-distance.lua:850 (Wyrmic Fire Drake summon): same name, dragon/fire, explicit PNG npc/dragon_fire_fire_drake.png, no define_as, summoner set'], 'outcome': 'the leaf has no define_as, so the summon has the same name/type/subtype/PNG and matches the zone fire drake token like the batch N minions and the batch P minotaur. Existing behaviour, reported as an open question; not decided here'},
              {'name': 'cold drake / storm drake / venom drake', 'other_definitions': ['vault random_filters (frost-dragon-lair, renegade-wyrmics) filter by name only'], 'outcome': 'single definitions; exact names; siblings cannot borrow each other or wyrm PNGs (negative tests)'},
              {'name': 'sand-drake', 'other_definitions': ['wild-gift/sand-drake is a talent category, not an actor; no other actor of that name'], 'outcome': 'single definition; the batch H test that kept it native is updated'},
              {'name': 'Rantha the Abomination / Rantha the Worm', 'other_definitions': ['RANTHA_THE_WORM (shipped rantha, dragon/ice, own PNG)'], 'outcome': 'different name, subtype, define_as and PNG; the two cannot borrow each other'},
              {'name': 'Briagh / Ukllmswwik', 'other_definitions': ['single definitions; achievements and quests only reference the define_as'], 'outcome': 'bound to define_as and unique'}],
          'kept_native': [],
          'neighbours_kept_native': [
              {'name': 'fire wyrm, ice wyrm, storm wyrm, venom wyrm, corrupted sand wyrm variants of other names', 'reason': 'not in the surveyed batch (fire/ice/storm/venom wyrm are later or NEEDS; Corrupted Sand Wyrm and Varsha are shipped)'},
              {'name': 'multi-hued drake family, wild-drake, Wyrmic summons of other names', 'reason': 'not in the surveyed batch'}]}
    out = ADDON / 'evidence/monster-batch-q-20260929/source-contracts.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(ev, indent=2, ensure_ascii=False) + '\n')
    evsha = hashlib.sha256(out.read_bytes()).hexdigest()
    for a in A:
        refs = [{'path': p, 'sha256': sha(p), 'role': r, 'note': n} for r, p, n in a['refs']]
        entry = {'asset_id': a['id'], 'native_name': a['name'], 'scope': a['scope'], 'sources': a['srcs'], 'references': refs,
                 'contrast_dimensions': list(a['dims']),
                 'prompt_fields': {'subject': a['subject'], 'contrast': a['contrast'], 'composition': a['comp'] or COMP, 'palette': a['palette']},
                 'kind': 'creature', 'max_attempts': 1, 'gate': 'ready',
                 'gate_reason': f"Exact source identity re-verified directly against game/modules/tome source (name={a['name']}, define_as={a['define_as']}, type={a['type']}/subtype={a['subtype']}, unique={a['unique']}); details and hashes in evidence/monster-batch-q-20260929/source-contracts.json. {a['structure']}. Exact catalog entry only, never a whole-subtype mapping.",
                 'render_evidence': [{'path': render, 'sha256': evsha}]}
        packs.setdefault(a['pack'], []).append(entry)
    for n, assets in packs.items():
        p = ADDON / f'art/production/batches/monster-batch-q-{n}.json'
        if p.exists():
            print('exists, skipped', p.name)
            continue
        p.write_text(json.dumps({'schema': 1, 'batch_id': f'monster-batch-q-{n}', 'assets': assets}, indent=2, ensure_ascii=False) + '\n')
        print('wrote', p.name)


if __name__ == '__main__':
    build()
