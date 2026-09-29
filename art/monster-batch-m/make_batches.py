"""Generate the monster-batch-m task packs and the pinned source-contract
evidence (survey-2 section 7, batch 4: losgoroth, gwelgoroth, manaworm, faeros,
umber hulk, greater gwelgoroth, xorn, ultimate gwelgoroth, telugoroth, Fyrk,
xaren, greater faeros) plus the elven cultist that batch L kept native until its
Flame of Urh'Rok demon form was live-confirmed. Pure bookkeeping: hashes native
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


def src(path, anchor):
    lines = (WS / (D + path)).read_text().splitlines()
    cands = [i + 1 for i, l in enumerate(lines) if anchor in l]
    assert cands, (path, anchor)
    return {'path': D + path, 'sha256': sha(D + path), 'line': cands[0], 'anchor': anchor}


COMP = ("One compact complete creature on a single circular tabletop disc, steep overhead three-quarter camera; visible clear neutral base ring on every side. Keep all anatomy and equipment well inside the inner four-fifths of disc radius. Base brightness must visually match reference neutral disc, with no illumination spill or ground effects. Disc plate discipline: measured results show generations of this style reference tend to render the disc DARKER than the reference, never lighter. So do not darken the disc at all: render the neutral disc -- including the whole outer-sixth ring band and the area under the creature -- at the style reference's own brightness, if anything a hair lighter, and never darker. No warm cast, glow, bounce-light, gradient or vignette anywhere on the disc. Do not darken the creature to compensate either. Add no warm cast, glow, bounce-light, gradient or vignette to the disc anywhere, including directly under or behind dark-bodied creatures.")
DISC = " Dry neutral charcoal disc with restrained copper-grey bevel, kept a visibly lighter value than the creature's darkest parts so the two never merge."
A = []


def asset(pack, id_, name, scope, srcs, base, define_as, typ, sub, unique, native_tall, structure, native, refs, subject,
          contrast, palette, verdict, dims=('silhouette', 'value'), comp=None):
    A.append(dict(comp=comp, pack=pack, id=id_, name=name, scope=scope, srcs=srcs, base=base, define_as=define_as, type=typ,
                  subtype=sub, unique=unique, native_tall=native_tall, structure=structure, native=native, refs=refs,
                  subject=subject, contrast=contrast, palette=palette, verdict=verdict, dims=dims))


STY = ('style', STYLE, 'Approved disc, lighting and camera; do not copy its creature.')
DEFAULT_EL = 'no image=/nice_tile/add_mos/shader/anim/moddable_tile/tint on the leaf or its base; generic actor.image==entry.image single path; NPC.lua:33 default-name image'
TALL = ('resolvers.nice_tile{image="invis.png", add_mos={{image="<png>", display_h=2, display_y=-1}}} names the PNG explicitly (no {tall=1} shorthand and no =BASE=TILE= indirection), '
        'so the resolved tall body is statically pinnable (same form as the batch F shivgoroth/greater shivgoroth, batch K Walrog/tunneler and batch J Weaver Queen entries); native sprite 64x128')

LG = 'general/npcs/losgoroth.lua'
GW = 'general/npcs/gwelgoroth.lua'
FA = 'general/npcs/faeros.lua'
XO = 'general/npcs/xorn.lua'
TE = 'general/npcs/telugoroth.lua'
EC = 'general/npcs/elven-caster.lua'
CS = 'zones/charred-scar/npcs.lua'


def R(family_id, note):
    return ('family', TOK + family_id + '.png', note)


def IDN(png, note):
    return ('identity', NPC + png, note)


# ---- pack 1: void and temporal elementals ----
asset(1, 'losgoroth', 'losgoroth', 'abashed-expanse (load with rarity(1)), meteor event (loadList of losgoroth.lua) and the general elemental spawn tables (elemental/void, default-name image, non-unique, no define_as). town-point-zero "monstrous losgoroth" (define_as MONSTROUS_LOSGOROTH, explicit image= npc/elemental_void_losgoroth.png) is another name and stays native',
      [src(LG, 'name = "losgoroth", color=colors.GREY')], src(LG, 'define_as = "BASE_NPC_LOSGOROTH"'), None, 'elemental', 'void', False, False,
      'base BASE_NPC_LOSGOROTH (elemental/void, no image=); ' + DEFAULT_EL + ' gives elemental_void_losgoroth.png; talent Void Blast is not a sustain; no sustains_at_birth; the CORRUPT_LOSGOROTH_FORM timed effect (special-artifacts.lua:100) writes replace_display on whoever drinks it and is never applied at birth',
      'elemental_void_losgoroth.png',
      [STY, IDN('elemental_void_losgoroth.png', 'Native shape: a violet-magenta squat translucent mass with four long curved tentacles arching out and down around a bright core.'),
       R('shivgoroth', 'Shipped shivgoroth (crystalline ice elemental, hunched): the losgoroth is a soft translucent violet void creature with arched tentacles, no crystals.')],
      "A void elemental seen from a steep overhead three-quarter angle: a squat translucent mass of mid-light orchid-violet and lilac energy with a bright pale-lilac glowing core at the centre, and four thick curling tentacles that arch outward and then downward around the body like the legs of a spider crab, each tapering to a soft point, with fine bright white-violet motes drifting inside the body. Ethereal, alien and complete.",
      "Void and temporal elementals built together: the losgoroth is the violet one with four arched tentacles radiating from a bright core (silhouette: radial curved legs around a round centre; hue: orchid violet; value: mid-light). The manaworm is a single coiled lemon-yellow serpent with pincers, and the telugoroth is a round swirl of gold, teal and violet ribbons; the shipped shivgoroth is a blue-white crystalline giant.",
      "Mid-light orchid-violet and lilac translucent body with lighter pale-lilac tentacle edges and a bright white-violet core; nothing darker than mid tone; no glow, light cast or spill onto the disc." + DISC,
      'READY single (losgoroth)', ('silhouette', 'value', 'hue'))

asset(1, 'manaworm', 'manaworm', 'abashed-expanse and other losgoroth.lua loaders (elemental/void, default-name image, non-unique, no define_as; a mana-draining latch worm)',
      [src(LG, 'name = "manaworm", color=colors.BLUE')], src(LG, 'define_as = "BASE_NPC_LOSGOROTH"'), None, 'elemental', 'void', False, False,
      'base BASE_NPC_LOSGOROTH (elemental/void, no image=); ' + DEFAULT_EL + ' gives elemental_void_manaworm.png; no talents, no sustains_at_birth; combat damtype MANAWORM does not touch body fields',
      'elemental_void_manaworm.png',
      [STY, IDN('elemental_void_manaworm.png', 'Native shape: a glowing lemon-yellow serpentine worm coiled on itself, head raised with two curved pincer mandibles and a curling tail.'),
       R('naga-nereid', 'Shipped naga nereid (pale gold-tailed woman): the manaworm is a bare glowing yellow worm with pincers, no human torso.')],
      "A manaworm seen from a steep overhead three-quarter angle: a thick glowing lemon-yellow serpentine worm with faint segment bands, coiled in a clear open spiral on itself, the head raised at the centre with two curved pale-gold pincer mandibles and a few short trailing feelers, brighter cream-yellow highlights along the upper-left of the coils, a slender curling tail tip. Alien, hungry and complete.",
      "Void and temporal elementals built together: the manaworm is the single coiled lemon-yellow serpent with pincers (silhouette: open spiral of one thick coil with a raised forked head; hue: lemon yellow; value: light). The losgoroth is a violet mass with four arched tentacles and the telugoroth is a round multicolour swirl.",
      "Bright lemon-yellow body with cream-yellow highlights and pale-gold pincers, faint ochre segment bands; nothing darker than mid tone except the band seams; no glow or light cast onto the disc." + DISC,
      'READY single (manaworm)', ('silhouette', 'value', 'hue'))

asset(1, 'telugoroth', 'telugoroth', 'temporal-rift and paradox-plane (elemental/temporal, default-name image, non-unique, no define_as, no nice_tile; the greater/ultimate telugoroth have tall nice_tile bodies and stay native)',
      [src(TE, 'name = "telugoroth", color=colors.KHAKI')], src(TE, 'define_as = "BASE_NPC_TELUGOROTH"'), None, 'elemental', 'temporal', False, False,
      'base BASE_NPC_TELUGOROTH (elemental/temporal, no image=); ' + DEFAULT_EL + ' gives elemental_temporal_telugoroth.png (64x64); the leaf carries only Turn Back the Clock (not a sustain) and no sustains_at_birth; greater/ultimate telugoroth are separate names with tall bodies',
      'elemental_temporal_telugoroth.png',
      [STY, IDN('elemental_temporal_telugoroth.png', 'Native shape: a round blurred swirl of overlapping translucent ribbons in gold, teal and violet around a paler centre.'),
       R('shivgoroth', 'Shipped shivgoroth (solid blue crystal giant): the telugoroth has no solid body, only overlapping translucent ribbons.')],
      "A temporal elemental seen from a steep overhead three-quarter angle: a roughly round shimmering mass made of many overlapping translucent ribbons of khaki-gold, teal and soft violet swirling in a slow spiral around a bright cream-white core, thin curved time-arcs echoing through the ribbons like several ghost copies of the same shape, soft feathered outer edges, no limbs and no face. Shimmering, unstable and complete.",
      "Void and temporal elementals built together: the telugoroth is the round multicolour ribbon swirl with a pale core (silhouette: compact round spiral, no limbs; hue: gold, teal and violet together; value: mid-light). The losgoroth is a violet tentacled mass and the manaworm a coiled yellow serpent.",
      "Mid-light khaki-gold, teal and soft violet ribbons over a bright cream-white core; nothing darker than mid tone; no glow or light cast onto the disc." + DISC,
      'READY single (telugoroth)', ('silhouette', 'value', 'hue'))

# ---- pack 2: gwelgoroth trio ----
GW_REF = R('greater-shivgoroth', 'Shipped greater shivgoroth (bright frost-white crystalline giant): the gwelgoroth trio are wind vortices, not crystal bodies.')
asset(2, 'gwelgoroth', 'gwelgoroth', 'tempest-peak, mark-spellblaze, infinite-dungeon, tannen-tower, ruined-dungeon, town-zigur and the town spawns (elemental/air, default-name image, non-unique, no define_as, no nice_tile)',
      [src(GW, 'name = "gwelgoroth", color=colors.AQUAMARINE')], src(GW, 'define_as = "BASE_NPC_GWELGOROTH"'), None, 'elemental', 'air', False, False,
      'base BASE_NPC_GWELGOROTH (elemental/air, no image=); ' + DEFAULT_EL + ' gives elemental_air_gwelgoroth.png (64x64); Lightning is not a sustain; no sustains_at_birth; the town loaders only move rarity into derth_rarity/POINT_ZERO_rarity',
      'elemental_air_gwelgoroth.png',
      [STY, IDN('elemental_air_gwelgoroth.png', 'Native shape: a single slim tilted funnel of pale grey-blue wind bands, wider at the top, with a few specks of brown dust at its foot.'),
       GW_REF],
      "An air elemental seen from a steep overhead three-quarter angle: one slender storm vortex, a narrow funnel of pale grey-blue wind bands wider at the top and tapering to a point at the foot, leaning gently toward the lower right, a few thin bright yellow-white lightning sparks running through the bands and a small scatter of tan dust specks near the foot. Light, fast and complete.",
      "Gwelgoroth family built together (all wind vortices): the plain gwelgoroth is ONE slim pale funnel with no debris (silhouette: narrow leaning cone; hue: pale grey-blue with tiny yellow sparks; value: light). The greater gwelgoroth is a fat heavy cone with three separate rings and orbiting rocks in slate steel-blue; the ultimate gwelgoroth is a huge wide column with a storm-cloud crown and forked lightning in royal blue. The shipped shivgoroths are crystal giants, not vortices.",
      "Pale grey-blue and off-white wind bands with lighter cream highlights, thin yellow-white lightning sparks, tan dust specks; nothing darker than mid tone; no glow or light cast onto the disc." + DISC,
      'READY single (gwelgoroth)', ('silhouette', 'value', 'hue'))

asset(2, 'greater-gwelgoroth', 'greater gwelgoroth', 'mark-spellblaze, tempest-peak, infinite-dungeon and town spawns; also named in quests/antimagic.lua (elemental/air, non-unique, no define_as, explicit tall nice_tile PNG elemental_air_greater_gwelgoroth.png)',
      [src(GW, 'name = "greater gwelgoroth", color=colors.STEEL_BLUE'), src(GW, 'image="npc/elemental_air_greater_gwelgoroth.png"')], src(GW, 'define_as = "BASE_NPC_GWELGOROTH"'), None, 'elemental', 'air', False, True,
      'base BASE_NPC_GWELGOROTH (elemental/air); the leaf has ' + TALL.replace('<png>', 'npc/elemental_air_greater_gwelgoroth.png') + '; non-unique so the entry is native_tall=true; sustains_at_birth activates no sustain that writes body fields (Lightning and Shock are bolts; Hurricane, the one sustain of the ultimate variant, writes nothing)',
      'elemental_air_greater_gwelgoroth.png',
      [STY, IDN('elemental_air_greater_gwelgoroth.png', 'Native shape: a fat slate-blue inverted-cone tornado of layered wind bands with brown rock and wood fragments spinning through the middle.'),
       GW_REF],
      "A greater air elemental seen from a steep overhead three-quarter angle, drawn compact: a fat heavy inverted-cone tornado of slate steel-blue wind bands with three clearly separate rotating rings, a wide rounded top and a narrower foot, chunks of brown rock and splintered wood orbiting in the middle band, thick bright cyan-white lightning bolts crackling across the front of the cone. Heavy, violent and complete.",
      "Gwelgoroth family built together (all wind vortices): the greater gwelgoroth is the fat slate-steel-blue cone with three rings and orbiting brown debris plus thick cyan-white lightning (silhouette: broad heavy cone with ring steps and chunks around it; hue: slate steel blue with brown rock; value: mid). The plain gwelgoroth is one slim pale funnel; the ultimate gwelgoroth is a much wider royal-blue column with a storm-cloud crown.",
      "Mid slate steel-blue wind bands with lighter pale-blue ring highlights, brown rock and wood chunks, bright cyan-white lightning; nothing darker than mid tone except the debris; no glow or light cast onto the disc." + DISC,
      'READY non-unique native-tall (greater gwelgoroth)', ('silhouette', 'value', 'hue'))

asset(2, 'ultimate-gwelgoroth', 'ultimate gwelgoroth', 'mark-spellblaze, tempest-peak, infinite-dungeon and town spawns (elemental/air, rank 3, non-unique, no define_as, explicit tall nice_tile PNG elemental_air_ultimate_gwelgoroth.png)',
      [src(GW, 'name = "ultimate gwelgoroth", color=colors.ROYAL_BLUE'), src(GW, 'image="npc/elemental_air_ultimate_gwelgoroth.png"')], src(GW, 'define_as = "BASE_NPC_GWELGOROTH"'), None, 'elemental', 'air', False, True,
      'base BASE_NPC_GWELGOROTH (elemental/air); the leaf has ' + TALL.replace('<png>', 'npc/elemental_air_ultimate_gwelgoroth.png') + '; non-unique so the entry is native_tall=true; its sustains_at_birth activates Hurricane (storm.lua:104), whose activate returns {} and deactivate returns true (storm.lua:126-131: a proc-only sustain that writes no field at all)',
      'elemental_air_ultimate_gwelgoroth.png',
      [STY, IDN('elemental_air_ultimate_gwelgoroth.png', 'Native shape: a towering wide pale-blue storm column with dark rock fragments spinning through it and a broad rounded crown.'),
       GW_REF],
      "An ultimate air elemental seen from a steep overhead three-quarter angle, drawn compact but filling more of the disc than its siblings: a towering wide near-cylindrical storm column of deep royal-blue and white wind bands that flares at the top into a thick storm-cloud crown, lit from within by yellow-white lightning, three bright forked lightning bolts bursting outward and downward across the body, dark rock fragments orbiting, a pale glowing storm eye near the top. Imposing and complete.",
      "Gwelgoroth family built together (all wind vortices): the ultimate gwelgoroth is the tallest widest one, a royal-blue and white column with a cloud crown and three forked yellow-white lightning bolts (silhouette: wide column with a flared crown and radiating bolts; hue: royal blue with white and yellow; value: mid with bright highlights). The plain gwelgoroth is one slim pale funnel; the greater gwelgoroth is a slate-blue cone with rings and orbiting debris.",
      "Mid royal-blue and white wind bands with lighter sky-blue highlights, bright yellow-white lightning forks, dark rock fragments kept small; nothing darker than mid tone except the fragments; no glow or light cast onto the disc." + DISC,
      'READY non-unique native-tall (ultimate gwelgoroth)', ('silhouette', 'value', 'hue'))

# ---- pack 3: faeros trio ----
asset(3, 'faeros', 'faeros', 'charred-scar, mark-spellblaze, daikara, noxious-caldera, infinite-dungeon, tannen-tower, ruined-dungeon, town-zigur; also named in quests/antimagic.lua (elemental/fire, default-name image, non-unique, no define_as)',
      [src(FA, 'name = "faeros", color=colors.ORANGE')], src(FA, 'define_as = "BASE_NPC_FAEROS"'), None, 'elemental', 'fire', False, False,
      'base BASE_NPC_FAEROS (elemental/fire, no image=; lite=1 is a light radius, not a display field); ' + DEFAULT_EL + ' gives elemental_fire_faeros.png (64x64); Flame is not a sustain; no sustains_at_birth; the sibling ultimate faeros has a tall nice_tile body and stays native',
      'elemental_fire_faeros.png',
      [STY, IDN('elemental_fire_faeros.png', 'Native shape: a lean humanoid figure of bright orange flame with a yellow-white chest, arms flung wide, flame licking from elbows and legs.'),
       R('shivgoroth', 'Shipped shivgoroth (hunched blue ice crystals): the faeros is a lean upright orange flame figure, not a crystal.')],
      "A fire elemental seen from a steep overhead three-quarter angle: a lean humanoid figure made entirely of licking bright orange flame with a yellow-white glowing core in the chest, thin limbs, both arms flung wide and slightly upward, a smooth teardrop head of flame with two small dark ember eyes, flame licks trailing from the elbows and knees. Fierce, quick and complete.",
      "Fire elementals built together: the plain faeros is the LEAN one, a slim bright-orange flame figure with arms flung wide (silhouette: thin X-shaped stance; hue: bright orange; value: mid-light). The greater faeros is a broad burly deep-orange figure with a tall flame crest and clawed hands, and Fyrk is a huge crimson-scarlet guardian with a glowing pale face and a three-pronged crown.",
      "Bright orange and amber flame with a yellow-white core; nothing darker than mid tone except the two ember eyes; the flame must not cast orange light, glow or warm cast onto the disc, which stays neutral charcoal." + DISC,
      'READY single (faeros)', ('silhouette', 'value', 'hue'))

asset(3, 'greater-faeros', 'greater faeros', 'charred-scar, noxious-caldera, mark-spellblaze, renegade-pyromancers vault (random_filter by name), infinite-dungeon and other faeros.lua loaders (elemental/fire, default-name image, non-unique, no define_as, no nice_tile)',
      [src(FA, 'name = "greater faeros", color=colors.ORANGE')], src(FA, 'define_as = "BASE_NPC_FAEROS"'), None, 'elemental', 'fire', False, False,
      'base BASE_NPC_FAEROS (elemental/fire, no image=); ' + DEFAULT_EL + ' gives elemental_fire_greater_faeros.png (64x64, NOT tall: the tall body belongs to ultimate faeros); Fiery Hands is a sustain started by sustains_at_birth but it only attaches two shader particle emitters (enhancement.lua:69, no type/subtype/image/add_mos/shader write)',
      'elemental_fire_greater_faeros.png',
      [STY, IDN('elemental_fire_greater_faeros.png', 'Native shape: a broad burly humanoid of layered orange and yellow flame with a tall flame crest, a glowing face and long hanging claws.'),
       R('greater-shivgoroth', 'Shipped greater shivgoroth (frost-white crystal giant): the greater faeros is a burly deep-orange flame figure, no crystals.')],
      "A greater fire elemental seen from a steep overhead three-quarter angle: a broad burly humanoid built of layered flame in deep orange with a bright yellow-white inner core, a wide chest and heavy arms hanging forward with long clawed hands of flame, a tall crest of flames rising from the head, an incandescent white-yellow face with two dark ember eyes, curling flame plumes from the shoulders. Powerful, blazing and complete.",
      "Fire elementals built together: the greater faeros is the BROAD one, a burly deep-orange flame figure with a tall flame crest and heavy hanging claws (silhouette: wide shoulders and hanging arms, crest on top; hue: deep orange with a white-yellow core; value: mid-light). The plain faeros is a lean slim figure with arms flung wide, and Fyrk is a crimson-scarlet guardian with a glowing pale face and a three-pronged crown.",
      "Deep orange and amber flame with a bright yellow-white core and face; nothing darker than mid tone except the two ember eyes; the flame must not cast orange light, glow or warm cast onto the disc, which stays neutral charcoal." + DISC,
      'READY single (greater faeros)', ('silhouette', 'value', 'hue'))

asset(3, 'fyrk', 'Fyrk, Faeros High Guard', 'charred-scar (elemental/fire, define_as FYRK, unique, explicit tall nice_tile PNG elemental_fire_fyrk__faeros_high_guard.png, single definition; allow_infinite_dungeon)',
      [src(CS, 'define_as = "FYRK"'), src(CS, 'image="npc/elemental_fire_fyrk__faeros_high_guard.png"')], src(FA, 'define_as = "BASE_NPC_FAEROS"'), 'FYRK', 'elemental', 'fire', True, False,
      'base BASE_NPC_FAEROS (elemental/fire); leaf define_as FYRK, unique=true; ' + TALL.replace('<png>', 'npc/elemental_fire_fyrk__faeros_high_guard.png') + '; sustains_at_birth activates Fiery Hands, Wildfire and Burning Wake: the first two attach particles, Burning Wake calls addShaderAura("burning_wake", ...) (wildfire.lua:67-95) which only appends an add_mos entry flagged _isshaderaura that nativeTallImage/emptyIgnoringAura already ignore (the batch I Harkor\'Zun Stone Skin case); no talent writes type/subtype/image',
      'elemental_fire_fyrk__faeros_high_guard.png',
      [STY, IDN('elemental_fire_fyrk__faeros_high_guard.png', 'Native shape: a tall broad fire giant of orange and gold flame with a glowing yellow face, heavy shoulders, flames rising above the head and swirling around the body.'),
       R('greater-shivgoroth', 'Shipped greater shivgoroth (frost-white crystal giant): Fyrk is a crimson-scarlet flame guardian, no crystals.')],
      "Fyrk, a faeros high guard, seen from a steep overhead three-quarter angle: a huge hulking figure of crimson-scarlet and molten-orange flame with a bright white-yellow core, broad heavy shoulders of layered flame, a glowing pale-yellow scowling face with dark heavy brows looking down in disdain, a tall three-pronged crown of white-yellow flames on the head, clawed hands held low in front, curling ribbons of fire around the body. Imperious, blazing and complete.",
      "Fire elementals built together: Fyrk is the crimson-scarlet guardian with a pale glowing face and a three-pronged flame crown (silhouette: heavy shoulders and a three-spike crown; hue: crimson and scarlet with white-yellow highlights; value: mid). The plain faeros is a lean bright-orange figure with arms flung wide and the greater faeros a burly deep-orange figure with a tall crest and hanging claws.",
      "Crimson-scarlet and molten-orange flame lifted with bright yellow-white highlights on the face, crown and core; nothing darker than mid tone except the brow shadows; the flame must not cast red or orange light, glow or warm cast onto the disc, which stays neutral charcoal." + DISC,
      'READY unique native-tall (Fyrk)', ('silhouette', 'value', 'hue'))

# ---- pack 4: xorn family ----
asset(4, 'umber-hulk', 'umber hulk', 'tempest-peak, daikara, quests/antimagic.lua and xorn.lua loaders (elemental/xorn, default-name image, non-unique, no define_as)',
      [src(XO, 'name = "umber hulk", color=colors.LIGHT_UMBER')], src(XO, 'define_as = "BASE_NPC_XORN"'), None, 'elemental', 'xorn', False, False,
      'base BASE_NPC_XORN (elemental/xorn, no image=); ' + DEFAULT_EL + ' gives elemental_xorn_umber_hulk.png (64x64); Mind Disruption is not a sustain; no sustains_at_birth; move_project DIG does not touch display fields; can_pass pass_wall is movement only',
      'elemental_xorn_umber_hulk.png',
      [STY, IDN('elemental_xorn_umber_hulk.png', 'Native shape: a hulking dark-brown insectoid brute with a broad flat head, two huge curved mandibles and two pale glaring eyes, thick clawed forelimbs.'),
       R('harkor-zun', "Shipped Harkor'Zun (brown two-armed rock golem with orange cracks): the umber hulk is a chitinous insectoid with mandibles and glowing eyes, not a rock golem.")],
      "An umber hulk seen from a steep overhead three-quarter angle: a hulking hunched insectoid brute with a broad flat-topped head, two huge curved pale-bone mandibles curling forward, two glowing pale-yellow eyes, a warm mid-umber chitin armoured back with lighter tan-ochre overlapping plates, thick clawed forelimbs held forward and down and stocky bent legs. Brutal, armoured and complete, clearly lit with pale rim light on the upper-left.",
      "Xorn family built together (all earth elementals): the umber hulk is the insectoid one, mid-umber chitin with two pale curved mandibles and two glowing eyes, two big forelimbs (silhouette: wide flat head with forward mandible curves, hunched, two arms; hue: warm umber with pale bone; value: mid). The xorn is a squat ochre stone barrel with four arms and one dark eye hole; the xaren is a tall angular silver-grey ore body with a skull face and four blocky fists. Harkor'Zun is a brown two-armed golem with orange cracks.",
      "Warm mid-umber chitin lifted with tan-ochre plates and pale bone-white mandibles, glowing pale-yellow eyes; nothing darker than mid tone except small plate seams." + DISC,
      'READY single (umber hulk)', ('silhouette', 'value', 'hue'))

asset(4, 'xorn', 'xorn', 'tempest-peak, daikara and the xorn-trap vault (maps/vaults/auto/lesser/xorn-trap.lua loads xorn.lua and filters by subtype) (elemental/xorn, default-name image, non-unique, no define_as)',
      [src(XO, 'name = "xorn", color=colors.UMBER')], src(XO, 'define_as = "BASE_NPC_XORN"'), None, 'elemental', 'xorn', False, False,
      'base BASE_NPC_XORN (elemental/xorn, no image=); ' + DEFAULT_EL + ' gives elemental_xorn_xorn.png (64x64); Constrict is not a sustain; no sustains_at_birth; the Fragmented Essence of Harkor\'Zun shares the base but is another unique name with its own tall body and stays a separate shipped entry',
      'elemental_xorn_xorn.png',
      [STY, IDN('elemental_xorn_xorn.png', 'Native shape: a squat brown stone body with a hooded round top holding one dark eye hole, four thick arms (two up, two out) and short legs.'),
       R('harkor-zun', "Shipped Harkor'Zun (brown two-armed rock golem with orange cracks): the xorn has FOUR arms, a hooded barrel body and a single eye hole, no orange cracks.")],
      "A xorn seen from a steep overhead three-quarter angle: a squat barrel-shaped body of warm ochre-tan stone and earth with a hood-like rounded top holding a single round dark eye hole, four thick rounded stone arms with blunt fists (two raised high, two spread out to the sides), three short stubby feet, pale mineral patches and a few moss-green streaks. Heavy, symmetric and complete, lit from the upper-left with pale rim light.",
      "Xorn family built together (all earth elementals): the xorn is the squat ochre-tan barrel with FOUR spread arms and one round eye hole (silhouette: round body with four radiating arms; hue: warm ochre-tan; value: mid-light). The umber hulk is a hunched insectoid with mandibles; the xaren is a tall angular cool silver-grey ore body with a skull face. Harkor'Zun is a brown two-armed golem with orange cracks.",
      "Warm ochre-tan stone with lighter sandy highlights and pale mineral patches, a few moss-green streaks; nothing darker than mid tone except the eye hole and seams." + DISC,
      'READY single (xorn)', ('silhouette', 'value', 'hue'))

asset(4, 'xaren', 'xaren', 'tempest-peak, daikara and xorn.lua loaders (elemental/xorn, default-name image, non-unique, no define_as; a tougher relative of the xorn)',
      [src(XO, 'name = "xaren", color=colors.SLATE')], src(XO, 'define_as = "BASE_NPC_XORN"'), None, 'elemental', 'xorn', False, False,
      'base BASE_NPC_XORN (elemental/xorn, no image=); ' + DEFAULT_EL + ' gives elemental_xorn_xaren.png (64x64); Constrict and Rush are not sustains; no sustains_at_birth',
      'elemental_xorn_xaren.png',
      [STY, IDN('elemental_xorn_xaren.png', 'Native shape: a tall angular body of grey metallic ore with bright glittering flecks, a skull-like head, four heavy arms and blocky fists.'),
       R('harkor-zun', "Shipped Harkor'Zun (brown two-armed rock golem with orange cracks): the xaren is cool silver-grey ore with a skull face and four arms.")],
      "A xaren seen from a steep overhead three-quarter angle: a tall angular blocky body of cool silver-grey metal ore studded with bright glittering flecks of copper, brass and turquoise, a squared skull-like head with two dark eye sockets and a jagged jaw, broad shoulders with ore-nugget knobs, four heavy arms ending in big blocky fists (two raised high, two hanging forward), an upright stiff stance. Hard, metallic and complete.",
      "Xorn family built together (all earth elementals): the xaren is the tall angular cool silver-grey ore body with a skull face and four blocky fists (silhouette: upright angular blocks, skull head, two arms raised; hue: cool silver-grey with copper and turquoise flecks; value: mid-light). The xorn is a squat warm ochre barrel with one eye hole and the umber hulk a hunched mandibled insectoid. Harkor'Zun is a brown two-armed golem with orange cracks.",
      "Mid-light cool silver-grey ore with brighter metallic highlights and copper, brass and turquoise flecks; nothing darker than mid tone except the eye sockets and seams." + DISC,
      'READY single (xaren)', ('silhouette', 'value', 'hue'))

# ---- pack 5: elven cultist ----
asset(5, 'elven-cultist', 'elven cultist', "reknor (live-checked in batch L) and other shalore spawns (humanoid/shalore, default-name image, non-unique, no define_as). It knows Flame of Urh'Rok and starts with sustains_at_birth, so at birth it is demon/major with __old_type={humanoid,shalore}: the exact form the Grand Corruptor entry handles through urh_rok_form=true",
      [src(EC, 'name = "elven cultist", color=colors.DARK_SEA_GREEN')], src(EC, 'define_as = "BASE_NPC_ELVEN_CASTER"'), None, 'humanoid', 'shalore', False, False,
      "base BASE_NPC_ELVEN_CASTER (humanoid/shalore, no image=); " + DEFAULT_EL + " gives humanoid_shalore_elven_cultist.png (64x64); sustains_at_birth activates T_FLAME_OF_URH_ROK (shadowflame.lua:96-97: __old_type={type,subtype}; type,subtype=demon,major; image untouched). The batch L live census (evidence/monster-batch-l-live-20260929/census.json, README) recorded type=demon, subtype=major, __old_type={humanoid,shalore}, image=npc/humanoid_shalore_elven_cultist.png, define_as=nil, T_FLAME_OF_URH_ROK active at birth. Batch L kept it native; batch M maps it as type humanoid/shalore with urh_rok_form=true. Other sustains at birth: none (Dark Ritual/Dark Portal/Soul Rot/Virulent Disease/Drain are not sustains)",
      'humanoid_shalore_elven_cultist.png',
      [STY, IDN('humanoid_shalore_elven_cultist.png', 'Native shape: a slim pale elf in a long flared sickly green robe, arms raised out to the sides gripping two curved daggers, hair pale, a small hood.'),
       R('elven-tempest', 'Shipped elven tempest (sky-blue robed caster with lightning): the cultist wears sickly sea-green robes and holds two curved daggers, no lightning.')],
      "A sinister elven cultist seen from a steep overhead three-quarter angle: a slim pale-skinned elf with pointed ears and pale silver-blond hair under a soft hood pushed back, a long flared robe in sickly mid-light sea-green with lighter lime-green folds and a darker jade trim and belt, both arms raised out to the sides each gripping a curved ritual dagger with a bright steel blade, a cold fanatical grin. Wicked, ritual and complete, clearly lit.",
      "Shalore tokens: elven mage (indigo robe, upright staff), elven tempest (sky-blue robe, lightning), elven blood mage (slate robe, red stains), Kryl-Feijan acolyte (red robe), Grand Corruptor (cobalt blue and red, horned), elven guard (green tunic with gold, shield and sword). The cultist is the one in a flared sickly sea-green ROBE with both arms raised holding two curved daggers (silhouette: flared robe with arms out to the sides; hue: sea-green and lime; value: mid-light). The elven guard is a forest-green armoured figure with a gold shield.",
      "Mid-light sickly sea-green robe lifted with lighter lime-green fold highlights, darker jade trim only as narrow seams, pale skin and silver-blond hair, bright steel blades; nothing darker than mid tone except small seams." + DISC,
      'READY single (elven cultist, Flame of Urh\'Rok form)', ('silhouette', 'value', 'hue'))


def retry(id_, pack, **changes):
    base = next(a for a in A if a['id'] == id_)
    A.append(dict(base, pack=pack, **changes))


# ---- retry packs are appended below by later edits of retries.py ----
exec((HERE / 'retries.py').read_text()) if (HERE / 'retries.py').exists() else None


def build():
    packs = {}
    identities = []
    render = 'game/addons/tome-checker-revised/evidence/monster-batch-m-20260929/source-contracts.json'
    seen = set()
    for a in A:
        if a['id'] in seen:
            continue
        seen.add(a['id'])
        native_rel = NPC + a['native']
        ident = {'id': a['id'], 'native_name': a['name'], 'source': a['srcs'][0], 'define_as': a['define_as'],
                 'type': a['type'], 'subtype': a['subtype'], 'unique': a['unique'], 'native_tall': a['native_tall'],
                 'urh_rok_form': a['id'] == 'elven-cultist',
                 'structure': a['structure'], 'native_image': 'npc/' + a['native'], 'native_image_path': native_rel,
                 'native_image_sha256': sha(native_rel), 'native_image_size': None, 'verdict': a['verdict']}
        from PIL import Image
        with Image.open(WS / native_rel) as im:
            ident['native_image_size'] = list(im.size)
        if a['base']:
            ident['base_source'] = a['base']
        if len(a['srcs']) > 1:
            ident['extra_sources'] = a['srcs'][1:]
        identities.append(ident)
    ev = {'schema': 1,
          'task': "monster-batch-m: static re-verification (no game launch) of the twelve batch-4 identities of the second gap survey (losgoroth, gwelgoroth, manaworm, faeros, umber hulk, greater gwelgoroth, xorn, ultimate gwelgoroth, telugoroth, Fyrk Faeros High Guard, xaren, greater faeros) plus the elven cultist that batch L left native pending a live check (now recorded in evidence/monster-batch-l-live-20260929) against game/modules/tome source and native sprites. Survey verdicts were not trusted; every field below was read from source: name, type/subtype, define_as, explicit or NPC.lua:33 default image, unique, PNG on disk, and absence of moddable_tile/shader/anim/add_displays.",
          'new_ids_not_in_catalog_before_this_batch': [i['id'] for i in identities], 'identities': identities,
          'runtime_mutation_scan': {
              'method': 'grep of game/modules/tome/data/talents and timed_effects for writes to self.type/subtype/image, __old_type, replace_display, add_mos, moddable_tile, shader; every talent of each identity (resolvers.talents and inherited base talents) was resolved to its definition and checked for mode="sustained" and for those writes',
              'writers_found': [
                  {'file': 'game/modules/tome/data/talents/corruptions/shadowflame.lua', 'line': 96, 'talent': "Flame of Urh'Rok", 'effect': 'sustain: __old_type={type,subtype}; type,subtype = demon,major; image untouched; restored on deactivate'},
                  {'file': 'game/modules/tome/data/timed_effects/magical.lua', 'line': 2958, 'talent': 'CORRUPT_LOSGOROTH_FORM (effect from a special artifact, special-artifacts.lua:100)', 'effect': 'replace_display on the drinker; never applied at birth and not by any identity of this batch (a display replacement is rejected by the matcher as external-display anyway)'},
                  {'file': 'game/modules/tome/data/timed_effects/magical.lua', 'line': 1132, 'talent': 'PHOENIX_EGG timed effect', 'effect': 'writes self.image while a reviving phoenix is an egg; timed status, never at birth, not a batch identity'},
                  {'file': 'game/modules/tome/data/talents/chronomancy/anomalies.lua', 'line': 587, 'talent': 'chronomancy anomaly', 'effect': 'writes name/subtype/image on a freshly made civilian summon only'}],
              'sustains_at_birth_review': [
                  {'identity': 'greater gwelgoroth', 'sustained': [], 'note': 'Lightning and Shock are bolts; resolvers.sustains_at_birth() has nothing to activate'},
                  {'identity': 'ultimate gwelgoroth', 'sustained': ['Hurricane (storm.lua:104)'], 'note': 'activate returns {} and deactivate returns true (storm.lua:126-131): writes nothing'},
                  {'identity': 'greater faeros', 'sustained': ['Fiery Hands (enhancement.lua:69)'], 'note': 'two shader_shield particle emitters only'},
                  {'identity': 'Fyrk', 'sustained': ['Fiery Hands', 'Wildfire (wildfire.lua:138: particles)', 'Burning Wake (wildfire.lua:67: addShaderAura, an add_mos entry flagged _isshaderaura)'], 'note': 'the aura entry is ignored by nativeTallImage exactly like the Harkor\'Zun Stone Skin aura (batch I, commit 32f4ec5)'},
                  {'identity': 'elven cultist', 'sustained': ["Flame of Urh'Rok (shadowflame.lua:85)"], 'note': 'type/subtype become demon/major with __old_type saved; handled only by the opt-in urh_rok_form flag'}],
              'hits_in_batch': [{'identity': 'elven cultist', 'talent': "T_FLAME_OF_URH_ROK (base=3) plus resolvers.sustains_at_birth()", 'consequence': "born demon/major over {humanoid,shalore} (live-confirmed in batch L). Mapped as type humanoid/subtype shalore with urh_rok_form=true; the flag accepts exactly demon/major with __old_type == {humanoid, shalore}, sustain_talents.T_FLAME_OF_URH_ROK and an unchanged image, and restores to the plain humanoid/shalore form when the sustain ends. Batch L kept it native; batch M maps it."}],
              'no_hit': ['losgoroth', 'manaworm', 'telugoroth', 'gwelgoroth', 'greater gwelgoroth', 'ultimate gwelgoroth', 'faeros', 'greater faeros', 'Fyrk, Faeros High Guard', 'umber hulk', 'xorn', 'xaren']},
          'name_collisions_checked': [
              {'name': 'losgoroth', 'other_definitions': ['zones/town-point-zero/npcs.lua MONSTROUS_LOSGOROTH is named "monstrous losgoroth" with an explicit image=npc/elemental_void_losgoroth.png (same PNG, other name)', 'abashed-expanse Spacial Disturbance (unique, invis.png, particle body)'], 'outcome': 'different names: the catalog key is the exact name "losgoroth", so both stay native; negative tests added'},
              {'name': 'greater gwelgoroth / ultimate gwelgoroth / gwelgoroth', 'other_definitions': ['zones/town-*/npcs.lua only move rarity into derth_rarity/POINT_ZERO_rarity; single definitions in gwelgoroth.lua'], 'outcome': 'one identity each; tall bodies pinned to their explicit PNGs, siblings cannot borrow each other\'s file'},
              {'name': 'faeros / greater faeros / ultimate faeros / Fyrk', 'other_definitions': ['ultimate faeros (faeros.lua:86) has a tall nice_tile body of its own', 'Fyrk (charred-scar) is a unique tall body'], 'outcome': 'ultimate faeros is not in this batch and stays native (negative test); Fyrk requires define_as FYRK and unique'},
              {'name': 'umber hulk / xorn / xaren', 'other_definitions': ['The Fragmented Essence of Harkor\'Zun (unique, tall) and Harkor\'Zun (demon/major) are separate shipped entries'], 'outcome': 'single definitions; different names and bodies'},
              {'name': 'telugoroth', 'other_definitions': ['greater telugoroth and ultimate telugoroth have tall nice_tile bodies'], 'outcome': 'they stay native; negative tests added'},
              {'name': 'elven cultist', 'other_definitions': ['single definition in elven-caster.lua'], 'outcome': 'one entry with urh_rok_form=true; the opt-in still applies to no other entry except the Grand Corruptor'}],
          'kept_native': [],
          'neighbours_kept_native': [
              {'name': 'monstrous losgoroth', 'reason': 'different name (town-point-zero), define_as MONSTROUS_LOSGOROTH'},
              {'name': 'ultimate faeros', 'reason': 'not in the surveyed batch; tall body of its own'},
              {'name': 'greater telugoroth / ultimate telugoroth', 'reason': 'not in the surveyed batch; tall bodies of their own'}]}
    out = ADDON / 'evidence/monster-batch-m-20260929/source-contracts.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(ev, indent=2, ensure_ascii=False) + '\n')
    evsha = hashlib.sha256(out.read_bytes()).hexdigest()
    for a in A:
        refs = [{'path': p, 'sha256': sha(p), 'role': r, 'note': n} for r, p, n in a['refs']]
        entry = {'asset_id': a['id'], 'native_name': a['name'], 'scope': a['scope'], 'sources': a['srcs'], 'references': refs,
                 'contrast_dimensions': list(a['dims']),
                 'prompt_fields': {'subject': a['subject'], 'contrast': a['contrast'], 'composition': a['comp'] or COMP, 'palette': a['palette']},
                 'kind': 'creature', 'max_attempts': 1, 'gate': 'ready',
                 'gate_reason': f"Exact source identity re-verified directly against game/modules/tome source (name={a['name']}, define_as={a['define_as']}, type={a['type']}/subtype={a['subtype']}, unique={a['unique']}); details and hashes in evidence/monster-batch-m-20260929/source-contracts.json. {a['structure']}. Exact catalog entry only, never a whole-subtype mapping.",
                 'render_evidence': [{'path': render, 'sha256': evsha}]}
        packs.setdefault(a['pack'], []).append(entry)
    for n, assets in packs.items():
        p = ADDON / f'art/production/batches/monster-batch-m-{n}.json'
        if p.exists():
            print('exists, skipped', p.name)
            continue
        p.write_text(json.dumps({'schema': 1, 'batch_id': f'monster-batch-m-{n}', 'assets': assets}, indent=2, ensure_ascii=False) + '\n')
        print('wrote', p.name)


if __name__ == '__main__':
    build()
