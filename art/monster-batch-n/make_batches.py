"""Generate the monster-batch-n task packs and the pinned source-contract
evidence (survey-2 section 7, batch 5: skeleton magus, ghast, shadow stalker,
lesser vampire, forest wight, vampire, master vampire, ghoulking, bone giant,
grave wight, elder vampire, The Shade of Telos). Pure bookkeeping: hashes native
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

SK = 'general/npcs/skeleton.lua'
GH = 'general/npcs/ghoul.lua'
BG = 'general/npcs/bone-giant.lua'
VA = 'general/npcs/vampire.lua'
WI = 'general/npcs/wight.lua'
KM = 'zones/keepsake-meadow/npcs.lua'
TM = 'zones/telmur/npcs.lua'
MF = 'talents/spells/master-of-flesh.lua'
MB = 'talents/spells/master-of-bones.lua'
EXPLICIT = 'explicit leaf image= (no nice_tile/add_mos/shader/anim/moddable_tile/tint on the leaf or its base BASE); generic actor.image==entry.image single path'
NECRO = ('Necromancer summons of the same name ("{n}", Master of {m}) are the same creature with the same default PNG and no define_as: they are accepted as the same body '
         '(the shipped summoned-identity contract), unlike the batch K ghoul whose define_as GHOUL happens to exclude its minion')


def R(family_id, note):
    return ('family', TOK + family_id + '.png', note)


def IDN(png, note):
    return ('identity', NPC + png, note)


# ---- pack 1: skeleton, ghouls, bone giant ----
asset(1, 'skeleton-magus', 'skeleton magus', 'dreadfell, halfling-ruins, collapsed-tower and amon-sul-crypt vault loots (undead/skeleton, default-name image, non-unique, no define_as, no nice_tile); the skeleton warrior/archer/mage siblings are separate shipped names',
      [src(SK, 'name = "skeleton magus", color=colors.LIGHT_RED')], src(SK, 'define_as = "BASE_NPC_SKELETON"'), None, 'undead', 'skeleton', False, False,
      'base BASE_NPC_SKELETON (undead/skeleton, no image=); ' + DEFAULT_EL + ' gives undead_skeleton_skeleton_magus.png (64x64); talents Staff Mastery (passive), Flame, Manathrust (bolts), Arcane Power (sustained, arcane.lua:84: resist/spellpower temporary values plus an arcane_power particle, no display field) - but the leaf has no sustains_at_birth, so nothing is even activated at birth; racial skeleton talents are passive/activated with no body write (Skeleton Reassemble only reads shader particles)',
      'undead_skeleton_skeleton_magus.png',
      [STY, IDN('undead_skeleton_skeleton_magus.png', 'Native shape: a golden-ivory skeleton with both arms raised out to the sides, orange fire burning in each hand, blue ribbon sashes streaming around the ribs and legs.'),
       R('skeleton-mage', 'Shipped skeleton mage (hunched skeleton wrapped in a dark blue-black cloak with a gold-lit skull): the magus is NOT cloaked; it is an open bare-boned figure with both arms raised, a flame in each hand and streaming cobalt ribbons.')],
      "A skeleton magus seen from a steep overhead three-quarter angle: a tall thin skeleton of warm ivory and pale gold bone standing upright and clearly open, with no cloak or hood, both arms raised up and out in a wide V, a small bright orange-and-yellow flame burning in each open hand, a faint gold light in the eye sockets, long ribbon sashes of bright cobalt blue with pale-blue edges wrapping the ribcage and streaming to both sides, small tarnished-gold trinkets on the wrists. Arcane, gaunt and complete.",
      "Skeleton family: the shipped skeleton mage is a hunched figure wrapped in a dark cloak, the skeleton warrior is a steel-armoured sword bearer, the archer is a bare skeleton drawing a bow. The magus is the OPEN figure with arms raised in a wide V and a flame in each hand, trailing cobalt-blue ribbons (silhouette: upright V of raised arms, no cloak, two hand flames; hue: ivory-gold bone with cobalt and orange accents; value: light).",
      "Light warm ivory and pale-gold bone, bright cobalt-blue ribbons, orange and yellow hand flames; nothing darker than mid tone except the eye sockets and rib gaps; the hand flames must not cast orange light, glow or warm cast onto the disc, which stays neutral charcoal." + DISC,
      'READY single (skeleton magus)', ('silhouette', 'value', 'hue'))

asset(1, 'ghast', 'ghast', 'dreadfell, halfling-ruins, amon-sul-crypt vault and Master of Flesh minions (undead/ghoul, default-name image, non-unique, no define_as, no nice_tile). ' + NECRO.format(n='ghast', m='Flesh'),
      [src(GH, 'name = "ghast", color=colors.UMBER'), src(MF, 'name = "ghast", color=colors.UMBER')], src(GH, 'define_as = "BASE_NPC_GHOUL"'), None, 'undead', 'ghoul', False, False,
      'base BASE_NPC_GHOUL (undead/ghoul, no image=); ' + DEFAULT_EL + ' gives undead_ghoul_ghast.png (64x64); talents Stun, Bite Poison, Summon, Rotting Disease, Decrepitude Disease are activated (none sustained), no sustains_at_birth; racial Ghoul talents are passive/activated (Ghoulish Leap only resets the move animation while jumping, Gnaw only reads invisibility)',
      'undead_ghoul_ghast.png',
      [STY, IDN('undead_ghoul_ghast.png', 'Native shape: a hulking hunched pale grey-tan ghoul with long drooping arms that reach the ground, a wide open jaw with a lolling tongue and a knotted spine.'),
       R('ghoul', 'Shipped ghoul (crouching tan-brown ghoul with claws forward): the ghast is a larger, paler, upright-hunched grey-green brute with long dangling arms and a wide-open jaw, not a low crawler.')],
      "A ghast seen from a steep overhead three-quarter angle: a hulking pale grey-green ghoul standing hunched, rotting skin in mid-light ash grey with sickly olive-green patches, a knotted bony spine and ribs showing, very long arms hanging down and forward with big pale-yellow talons, a large heavy head with a wide open fanged jaw and small dull yellow eyes, a ragged strip of cloth at the hip. Foul, heavy and complete.",
      "Ghoul family: the shipped ghoul is a tan-brown low crawler with claws forward; the ghast is the PALE hunched brute standing on two legs with long arms hanging (silhouette: upright hunch, dangling long arms, big open jaw; hue: ash grey with olive green; value: light). The ghoulking is a darker umber ghoul with a gold crown and broad shoulders, standing with arms out.",
      "Light ash-grey and olive-green skin with pale bone and yellow talons, dull yellow eyes; nothing darker than mid tone except the mouth and the shadow under the ribs." + DISC,
      'READY single (ghast)', ('silhouette', 'value', 'hue'))

asset(1, 'ghoulking', 'ghoulking', 'dreadfell, halfling-ruins, greater-crypt/renegade-undead vaults and Master of Flesh minions (undead/ghoul, default-name image, rank 3, non-unique, no define_as, no nice_tile). ' + NECRO.format(n='ghoulking', m='Flesh'),
      [src(GH, 'name = "ghoulking", color={0,0,0}'), src(MF, 'name = "ghoulking", color={0,0,0}')], src(GH, 'define_as = "BASE_NPC_GHOUL"'), None, 'undead', 'ghoul', False, False,
      'base BASE_NPC_GHOUL (undead/ghoul, no image=); ' + DEFAULT_EL + ' gives undead_ghoul_ghoulking.png (64x64); talents Stun, Bite Poison, Summon, Rotting/Decrepitude/Weakness Disease are activated (none sustained), no sustains_at_birth; the leaf color={0,0,0} is only the ASCII colour, the sprite is a lit dark-brown ghoul with a gold crown',
      'undead_ghoul_ghoulking.png',
      [STY, IDN('undead_ghoul_ghoulking.png', 'Native shape: a lean dark-brown ghoul standing wide-legged with clawed hands out to the sides, a gold circlet on the brow and a black loincloth.'),
       R('ghoul', 'Shipped ghoul (tan low crawler): the ghoulking is a darker umber, upright, broad-shouldered ghoul wearing a bright gold crown, arms spread with claws.')],
      "A ghoulking seen from a steep overhead three-quarter angle: an upright broad-shouldered ghoul with leathery mid-tone umber-brown skin lit with warm tan highlights, standing wide-legged with both arms spread out and low, long dark claws on each hand, a heavy jaw with pointed teeth and glowing pale-yellow eyes, a bright polished gold crown of spikes on the brow, gold bands on the arms, a ragged dark-red loincloth. Regal, cruel and complete, clearly lit.",
      "Ghoul family: the shipped ghoul is a tan low crawler and the ghast a pale grey-green hunched brute with dangling arms. The ghoulking is the UMBER-brown one with a gold crown, standing upright with arms spread (silhouette: wide stance, arms spread, spiked crown on top; hue: umber brown with bright gold; value: mid with bright gold highlights).",
      "Mid umber-brown skin with lighter tan highlights, bright gold crown and arm bands, dark-red loincloth, pale-yellow eyes; the darkest tones stay mid-dark and are limited to small seams; no glow or light cast onto the disc." + DISC,
      'READY single (ghoulking)', ('silhouette', 'value', 'hue'))

asset(1, 'bone-giant', 'bone giant', 'rak-shor-pride, telmur and other bone-giant.lua loaders (undead/giant, non-unique, no define_as, nice_tile with the explicit PNG undead_giant_bone_giant.png). ' + NECRO.format(n='bone giant', m='Bones'),
      [src(BG, 'name = "bone giant", color=colors.WHITE'), src(BG, 'add_mos = {{image="npc/undead_giant_bone_giant.png"'), src(MB, 'name = "bone giant", color=colors.WHITE')], src(BG, 'define_as = "BASE_NPC_BONE_GIANT"'), None, 'undead', 'giant', False, True,
      'base BASE_NPC_BONE_GIANT (undead/giant, no image=); ' + TALL.replace('<png>', 'npc/undead_giant_bone_giant.png') + '; talents Bone Armour and Stun are activated (Bone Armour is not a sustain), no sustains_at_birth; the eternal/heavy/runed/other bone giants are other names with other PNGs; the Necromancer Lord of Skulls effect renames its minion (exact name no longer matches)',
      'undead_giant_bone_giant.png',
      [STY, IDN('undead_giant_bone_giant.png', 'Native shape: a tall lanky humanoid framework assembled from dozens of tan bones, long arms ending in clustered bone fists, a small bone head, pale lilac fringe on the edges.'),
       R('half-finished-bone-giant', 'Shipped Half-Finished Bone Giant (thin purple-aura skeleton frame with gaps): the bone giant is the complete, massive, densely packed mass of bones, no purple aura.')],
      "A bone giant seen from a steep overhead three-quarter angle: a hulking heavy humanoid mass assembled from dozens of large ivory and tan bones, ribcages and vertebra fused into a broad torso and thick shoulders, very heavy arms of stacked femurs ending in huge clustered bone fists resting low in front, thick bone-plate legs, a small skull head with dark hollow eyes sunk between the shoulders, tarnished sinew and small skulls studding the shoulders. Dense, massive and complete.",
      "Undead giants: the shipped Half-Finished Bone Giant is a thin spindly frame with a purple aura and gaps. The bone giant is the COMPLETE dense one, a wide heavy mass of stacked ivory bones with big fists (silhouette: broad blocky shoulders, huge low fists, small head; hue: warm ivory and tan; value: light).",
      "Light warm ivory and tan bone with mid-tone brown sinew and dark hollow eye sockets; nothing darker than mid tone except sockets and gaps between bones; no glow or light cast onto the disc." + DISC,
      'READY non-unique native-tall (bone giant)', ('silhouette', 'value', 'hue'))

# ---- pack 2: vampires ----
asset(2, 'lesser-vampire', 'lesser vampire', 'dreadfell, ardhungol, greater-crypt / paladin-vs-vampire vaults (undead/vampire, explicit image=npc/lesser_vampire.png, non-unique, no define_as, no nice_tile). Sustains: sustains_at_birth activates Eternal Night only (see scan)',
      [src(VA, 'name = "lesser vampire", color=colors.SLATE, image = "npc/lesser_vampire.png"')], src(VA, 'define_as = "BASE_NPC_VAMPIRE"'), None, 'undead', 'vampire', False, False,
      'base BASE_NPC_VAMPIRE (undead/vampire, no image=); leaf ' + EXPLICIT + '; sustains_at_birth starts Eternal Night (eradication.lua:179: damage/resist-pen temporary values plus shader_ring_rotating particles chosen with core.shader.active, never self.shader) - Blurred Mortality and Soul Leech are passive, Stun/Invoke Darkness activated; resolvers.inscriptions(1,"rune") may give a random rune whose use is a timed effect (Invisibility/Ethereal set self.shader for a while: the matcher falls back to native art while a shader is set, not a birth write)',
      'lesser_vampire.png',
      [STY, IDN('lesser_vampire.png', 'Native shape: a young slim man with pale blue-grey skin and dark hair, in an ochre-orange tunic, olive green trousers and brown boots, hands open at his sides.'),
       R('the-master', 'Shipped The Master (tall upright crimson-robed vampire with a staff): the lesser vampire is a plain young man in an orange tunic with no cape, no robe and no staff.')],
      "A lesser vampire seen from a steep overhead three-quarter angle: a young slim man with pale blue-grey skin and untidy dark hair, a hungry expression with small white fangs showing, dressed in a plain mid-light ochre-orange tunic with a leather belt, olive-green trousers and brown boots, both hands open and clawed slightly at his sides, standing in a slightly forward-leaning stance. No cape, no robe, no weapon. Fresh, hungry and complete.",
      "Vampire family, four grades: the lesser vampire is the plain young man in an ORANGE tunic and green trousers with no cape (silhouette: slim bare figure, open hands, no cloak; hue: ochre-orange with olive green; value: mid-light). The vampire has a flared scarlet cape and crouches, the master vampire is a tall indigo-cloaked figure, the elder vampire is a hooded burgundy robe with violet magic, and the shipped The Master is a crimson-robed figure with a staff.",
      "Mid-light ochre-orange tunic, olive-green trousers, brown boots, pale blue-grey skin, dark hair; nothing darker than mid tone except the hair and boot soles." + DISC,
      'READY single (lesser vampire)', ('silhouette', 'value', 'hue'))

asset(2, 'vampire', 'vampire', 'dreadfell, ardhungol, greater-crypt / paladin-vs-vampire vaults, antimagic quest (undead/vampire, explicit image=npc/vampire.png, non-unique, no define_as, no nice_tile). Sustains: sustains_at_birth activates Eternal Night and Blur Sight',
      [src(VA, 'name = "vampire", color=colors.SLATE, image = "npc/vampire.png"')], src(VA, 'define_as = "BASE_NPC_VAMPIRE"'), None, 'undead', 'vampire', False, False,
      'base BASE_NPC_VAMPIRE (undead/vampire, no image=); leaf ' + EXPLICIT + '; sustains_at_birth starts Eternal Night and Blur Sight (npcs.lua:3753: combat_def temporary value plus a phantasm_shield particle) - particles/temporary values only, no type/subtype/image/add_mos/shader write; Circle of Death, Stun, Rotting Disease are activated; runes as for the lesser vampire (timed shader, matcher fallback)',
      'vampire.png',
      [STY, IDN('vampire.png', 'Native shape: a crouching man in a red jacket and a big flared red cape with a high collar, pale face, one hand raised clawing, brown boots.'),
       R('the-master', 'Shipped The Master (upright robed vampire with a red-gem staff): the vampire crouches in a wide flared scarlet cape with a black lining, no staff, no long robe.')],
      "A vampire seen from a steep overhead three-quarter angle: a pale-faced dark-haired man with visible fangs crouching in a predatory lunge, wrapped in a wide flared scarlet cape with a high collar and a black lining that sweeps out behind and to one side, a mid-light red jacket underneath, one hand raised with curled claws, the other low, dark trousers and brown boots. No staff, no hood. Menacing, predatory and complete.",
      "Vampire family, four grades: the vampire is the CROUCHING one in a wide flared scarlet cape with black lining (silhouette: low diagonal lunge, big cape fan, raised claw; hue: scarlet red with black; value: mid-light). The lesser vampire is a plain orange-tunic young man without a cape, the master vampire a tall indigo-cloaked figure, the elder vampire a hooded burgundy robe with violet magic, and the shipped The Master an upright crimson robe with a staff.",
      "Mid-light scarlet cape and jacket with a black-brown lining used only in the folds, pale skin, dark hair, brown boots; nothing darker than mid tone except the cape lining seams and hair." + DISC,
      'READY single (vampire)', ('silhouette', 'value', 'hue'))

asset(2, 'master-vampire', 'master vampire', 'dreadfell, ardhungol, greater-crypt / paladin-vs-vampire vaults (undead/vampire, explicit leaf image=npc/master_vampire.png plus nice_tile naming the same PNG, non-unique, no define_as). Sustains: Eternal Night, Blur Sight, Phantasmal Shield',
      [src(VA, 'name = "master vampire", color=colors.GREEN, image = "npc/master_vampire.png"'), src(VA, 'resolvers.nice_tile{image="invis.png", add_mos = {{image="npc/master_vampire.png"')], src(VA, 'define_as = "BASE_NPC_VAMPIRE"'), None, 'undead', 'vampire', False, True,
      'base BASE_NPC_VAMPIRE (undead/vampire, no image=); leaf image=npc/master_vampire.png then ' + TALL.replace('<png>', 'npc/master_vampire.png') + '; sustains_at_birth starts Eternal Night, Blur Sight and Phantasmal Shield (phantasm.lua:67: evade callback and a phantasm_shield particle) - particles/temporary values only, no type/subtype/image/add_mos/shader write; runes as for the lesser vampire (timed shader, matcher fallback)',
      'master_vampire.png',
      [STY, IDN('master_vampire.png', 'Native shape: a tall thin man in a long dark blue cloak with a high collar, a tan waistcoat, dark trousers, pale face, dark hair, hands hanging.'),
       R('the-master', 'Shipped The Master (crimson robe, staff): the master vampire wears a long INDIGO-BLUE cloak with a cream waistcoat, no staff, arms hanging.')],
      "A master vampire seen from a steep overhead three-quarter angle: a tall gaunt pale-faced man with slicked dark hair and cold bright eyes, standing perfectly upright and calm in a long full-length mid-tone indigo-blue cloak with a high stiff collar lined pale periwinkle, a cream-tan waistcoat and cravat showing at the chest, dark trousers, both arms hanging with long pale fingers. No staff, no fangs bared. Cold, aristocratic and complete, clearly lit.",
      "Vampire family, four grades: the master vampire is the tall calm INDIGO-BLUE cloaked figure with a cream waistcoat (silhouette: tall narrow upright column, straight cloak, arms hanging; hue: indigo blue with cream; value: mid). The lesser vampire is an orange-tunic young man, the vampire a crouching scarlet-caped figure, the elder vampire a hooded burgundy robe, and the shipped The Master a crimson robe with a staff.",
      "Mid-tone indigo-blue cloak lifted with lighter periwinkle folds and lining, cream-tan waistcoat, pale skin, dark hair; nothing darker than mid-dark except the hair and trouser seams; the cloak must stay clearly lighter than the disc's darkest ring." + DISC,
      'READY non-unique native-tall (master vampire)', ('silhouette', 'value', 'hue'))

asset(2, 'elder-vampire', 'elder vampire', 'dreadfell, ardhungol, greater-crypt / paladin-vs-vampire vaults (undead/vampire, explicit image=npc/elder_vampire.png (64x64, not tall), rank 3, non-unique, no define_as, no nice_tile). Sustains: Eternal Night, Blur Sight, Phantasmal Shield',
      [src(VA, 'name = "elder vampire", color=colors.RED, image = "npc/elder_vampire.png"')], src(VA, 'define_as = "BASE_NPC_VAMPIRE"'), None, 'undead', 'vampire', False, False,
      'base BASE_NPC_VAMPIRE (undead/vampire, no image=); leaf ' + EXPLICIT + '; sustains_at_birth starts Eternal Night, Blur Sight and Phantasmal Shield (particles/temporary values only); Summon summons random undead (not this name); runes as for the lesser vampire (timed shader, matcher fallback)',
      'elder_vampire.png',
      [STY, IDN('elder_vampire.png', 'Native shape: a hooded figure in a deep red robe with a rope belt and long sleeves, pale narrow face under the cowl, one hand raised holding a swirl of violet magic.'),
       R('the-master', 'Shipped The Master (upright crimson robe with a staff and no hood): the elder vampire is HOODED, in a burgundy robe with a rope belt and a swirl of violet magic in one raised hand, no staff.')],
      "An elder vampire seen from a steep overhead three-quarter angle: a hooded figure in a long mid-tone burgundy-red robe with wide sleeves and a rope belt, the cowl pulled up over a pale narrow face with pale glowing eyes and long thin fangs, one hand raised holding a bright swirling wisp of violet magic, the other hand hidden in a sleeve, the hem of the robe brushing the base. No staff, no cape. Ancient, sinister and complete, clearly lit.",
      "Vampire family, four grades: the elder vampire is the HOODED burgundy-robed figure with violet magic in one hand (silhouette: pointed hood over a long conical robe, one raised hand with a violet wisp; hue: burgundy with violet; value: mid). The lesser vampire is an orange-tunic young man, the vampire a crouching scarlet-caped figure, the master vampire a tall indigo cloak, and the shipped The Master a bright crimson robe with a staff and no hood.",
      "Mid-tone burgundy-red robe lifted with lighter rose folds, violet magic wisp with a pale lilac core, pale skin and eyes; nothing darker than mid-dark except the cowl interior and hem seams; the magic must not cast violet light, glow or a cast onto the disc." + DISC,
      'READY single (elder vampire)', ('silhouette', 'value', 'hue'))

# ---- pack 3: wights, shadow stalker, Shade of Telos ----
asset(3, 'forest-wight', 'forest wight', 'dreadfell, ardhungol, lesser loot-vault (undead/wight, explicit image=npc/forest_wight.png, non-unique, no define_as, no nice_tile). resolvers.sustains_at_birth() is present but the wight talents (Flame, Lightning, Glacial Vapour, Mind Disruption, Flameshock) are all activated, so nothing is sustained at birth',
      [src(WI, 'name = "forest wight", color=colors.GREEN, image="npc/forest_wight.png"')], src(WI, 'define_as = "BASE_NPC_WIGHT"'), None, 'undead', 'wight', False, False,
      'base BASE_NPC_WIGHT (undead/wight, no image=); leaf ' + EXPLICIT + '; sustains_at_birth activates nothing (Flame, Lightning, Glacial Vapour, Mind Disruption are not sustained); the barrow and emperor wights are other names with tall bodies',
      'forest_wight.png',
      [STY, IDN('forest_wight.png', 'Native shape: a skeletal figure with bony legs and a skull head with red eyes, in dark rusted armour, holding a big axe raised behind one shoulder and a wooden tower shield.'),
       R('skeleton-warrior', 'Shipped skeleton warrior (steel-armoured skeleton with a downward sword): the forest wight wears moss-green corroded armour and a ragged hood, raises an axe and carries a round wooden shield.')],
      "A forest wight seen from a steep overhead three-quarter angle: a gaunt skeletal undead warrior with bare pale-bone legs and arms, a skull face with two small red glowing eyes under a ragged moss-green hood, mid-tone corroded green-bronze breastplate and shoulder pieces with hanging tatters and creeping ivy, a notched axe raised high in one hand and a round wooden shield with a rusty rim held in the other, faint pale-green wisps rising off the shoulders. Forsaken, wild and complete, clearly lit.",
      "Wight family and undead warriors: the forest wight is the GREEN one, moss-green corroded armour, a hood, a raised axe and a round shield (silhouette: raised axe and round shield either side of a hooded head; hue: moss green and bone; value: mid-light). The grave wight is a pale teal spectral shroud with reaching hands, the shipped skeleton warrior a steel sword bearer, and the Shade of Telos a robed spectral archmage with a staff.",
      "Mid-tone moss-green and green-bronze armour, pale bone limbs, small red eyes, brown wood shield, pale-green wisps; nothing darker than mid tone except the hood interior and armour seams; the wisps must not glow onto or tint the disc." + DISC,
      'READY single (forest wight)', ('silhouette', 'value', 'hue'))

asset(3, 'grave-wight', 'grave wight', 'dreadfell, ardhungol, greater-crypt / paladin-vs-vampire vaults (undead/wight, explicit image=npc/grave_wight.png, non-unique, no define_as, no nice_tile). resolvers.sustains_at_birth() present but nothing sustained (Flameshock, Lightning, Glacial Vapour, Mind Disruption are activated)',
      [src(WI, 'name = "grave wight", color=colors.SLATE, image="npc/grave_wight.png"')], src(WI, 'define_as = "BASE_NPC_WIGHT"'), None, 'undead', 'wight', False, False,
      'base BASE_NPC_WIGHT (undead/wight, no image=); leaf ' + EXPLICIT + '; sustains_at_birth activates nothing; the native sprite is already a translucent glowing teal ghost (a painted sprite, not a shader)',
      'grave_wight.png',
      [STY, IDN('grave_wight.png', 'Native shape: a translucent glowing teal-white ghostly humanoid with hollow bright eyes, arms hanging forward, a tattered shroud fading to wisps below the waist.'),
       R('the-master', 'Shipped The Master (solid crimson robe): the grave wight is a translucent pale teal-white ghost with no solid clothing.')],
      "A grave wight seen from a steep overhead three-quarter angle: a gaunt ghostly humanoid made of pale teal-white translucent mist, hollow oval eyes and mouth glowing bright, long thin arms reaching forward with clawed fingers, a tattered shroud hanging off the shoulders and trailing to wispy tatters at the base, faint cold blue veins running through the body. No weapon, no staff, no crown. Cold, hollow and complete.",
      "Wight, ghost and shadow undead built together: the grave wight is the PALE TEAL-WHITE reaching ghost in a tattered shroud (silhouette: hunched with both arms reaching forward, ragged shroud; hue: pale teal-white; value: light). The forest wight is a green armoured skeleton with an axe, the shadow stalker a slate-violet smoke figure with claws, and the Shade of Telos a large blue-violet robed spectral archmage with a crown and a staff.",
      "Light pale teal-white and cool cyan translucent body with brighter white hollows; nothing darker than mid tone except a few cold-blue veins; no glow or cold light cast onto the disc." + DISC,
      'READY single (grave wight)', ('silhouette', 'value', 'hue'))

asset(3, 'shadow-stalker', 'shadow stalker', 'keepsake-meadow shadow trap and cave entrance/last maps (undead/shadow, define_as SHADOW_STALKER, explicit image=npc/shadow-stalker.png, non-unique, faction enemies, no nice_tile; the same-family SHADOW_CLAW and SHADOW_CASTER (both named "shadow claw", other PNGs) stay native)',
      [src(KM, 'define_as = "SHADOW_STALKER"'), src(KM, 'name = "shadow stalker", image="npc/shadow-stalker.png"')], src(KM, 'define_as = "BASE_SHADOW"'), 'SHADOW_STALKER', 'undead', 'shadow', False, False,
      'base BASE_SHADOW (undead/shadow, image=npc/humanoid_human_spectator02.png overridden by the leaf); leaf define_as SHADOW_STALKER, explicit image=npc/shadow-stalker.png (64x64); no nice_tile/add_mos/shader/anim/moddable_tile; no sustains_at_birth; talents Keepsake Phase Door (teleport), Blindside (melee jump) and Fade (EFF_FADED: invulnerable and status_effect_immune temporary values only, other.lua:1916, no display field, no invisibility) are activated; onTakeHit only forces Fade/Phase Door',
      'shadow-stalker.png',
      [STY, IDN('shadow-stalker.png', 'Native shape: a lean humanoid silhouette of dark smoky grey with blurred edges, arms held out to the sides, no legs shown clearly, faint face.'),
       R('the-master', 'Shipped The Master (solid crimson robe): the shadow stalker is a lean smoky slate-violet shadow with long claws, no clothing.')],
      "A shadow stalker seen from a steep overhead three-quarter angle: a lean crouching humanoid made of layered curling smoke in mid-tone slate blue-violet, clearly lighter and paler along the upper-left facing edges with a pale lavender-grey rim, two small bright pale cyan-white eyes in a smooth faceless head, both arms stretched forward and out ending in long thin curved claws of pale grey, the lower body tapering into curling smoke tendrils. No clothing, no weapon. Stealthy, sinister and complete, clearly readable and never a black blob.",
      "Wight, ghost and shadow undead built together: the shadow stalker is the SLATE-VIOLET smoke figure with long forward claws and a tapering smoky tail (silhouette: low crouch, arms stretched forward with claws, no legs; hue: slate blue-violet with a pale lavender rim; value: mid with light edges). The grave wight is a pale teal ghost in a shroud, the Shade of Telos a large robed blue-violet archmage with a crown and staff, and the forest wight a green armoured skeleton.",
      "Mid-tone slate blue-violet smoke with lighter lavender-grey rim planes and pale cyan-white eyes; the darkest part of the body must still be lighter than the disc's darkest ring, and no part is pure black; no glow or smoke spill onto the disc." + DISC,
      'READY define_as-bound single (shadow stalker)', ('silhouette', 'value', 'hue'))

asset(3, 'shade-of-telos', 'The Shade of Telos', 'telmur (undead/ghost, define_as SHADE_OF_TELOS, unique, guardian of zone Ruins of Telmur, default-name image npc/undead_ghost_the_shade_of_telos.png, single definition; allow_infinite_dungeon)',
      [src(TM, 'define_as = "SHADE_OF_TELOS"'), src(TM, 'name = "The Shade of Telos"')], None, 'SHADE_OF_TELOS', 'undead', 'ghost', True, False,
      'no base (standalone newEntity: type undead/subtype ghost, unique=true, no image=); ' + DEFAULT_EL.replace('on the leaf or its base', 'on the entity') + ' gives undead_ghost_the_shade_of_telos.png (64x64); no sustains_at_birth; Uttercold is a sustained talent the entity knows but nothing activates it at birth (its activate only adds temporary values and circular_flames particles chosen with core.shader.active); can_pass pass_wall is movement only; resolvers.inscriptions(4,"rune") may give random runes whose use is a timed effect (matcher falls back to native while a shader is set); the Telmur zone.lua has no post-processing of the actor',
      'undead_ghost_the_shade_of_telos.png',
      [STY, IDN('undead_ghost_the_shade_of_telos.png', 'Native shape: a large glowing cyan translucent spectre with a jagged crown-like top, wide shoulders and long ragged sleeves and robe fading into trailing wisps.'),
       R('the-master', 'Shipped The Master (solid crimson robe, staff): the Shade of Telos is a translucent blue-violet spectral archmage with a pointed crown and a crystalline staff held in both hands.')],
      "The Shade of Telos seen from a steep overhead three-quarter angle: a large tall spectral archmage made of translucent ice-blue and soft violet light, a pointed jagged crown of ice on the head, a stern hollow-eyed face, wide shoulders under long flowing ragged sleeves and robes trailing to wisps at the base, both hands gripping a long crystalline ice-blue staff held upright in front of the body with a bright white-blue crystal at the top, small frost crystals drifting around the shoulders. Regal, ancient and complete, clearly lit.",
      "Wight, ghost and shadow undead built together: the Shade of Telos is the BIG blue-violet robed spectral archmage with a jagged crown and an upright crystalline staff (silhouette: wide shoulders, crown spikes, vertical staff in front of the body; hue: ice blue with soft violet; value: light). The grave wight is a smaller pale teal shroud ghost with reaching arms and no staff, the shadow stalker a low slate-violet smoke figure, and the forest wight a green armoured skeleton.",
      "Light ice-blue and soft violet translucent robes with brighter white-blue crown, staff crystal and face hollows; nothing darker than mid tone except the eye hollows and sleeve folds; no glow or cold light cast onto the disc." + DISC,
      'READY unique define_as-bound (The Shade of Telos)', ('silhouette', 'value', 'hue'))


def retry(id_, pack, **changes):
    base = next(a for a in A if a['id'] == id_)
    A.append(dict(base, pack=pack, **changes))


# ---- retry packs are appended below by later edits of retries.py ----
exec((HERE / 'retries.py').read_text()) if (HERE / 'retries.py').exists() else None

NEW_IDS = ['skeleton-magus', 'ghast', 'ghoulking', 'bone-giant', 'lesser-vampire', 'vampire', 'master-vampire',
           'elder-vampire', 'forest-wight', 'grave-wight', 'shadow-stalker', 'shade-of-telos']


def build():
    packs = {}
    identities = []
    render = 'game/addons/tome-checker-revised/evidence/monster-batch-n-20260929/source-contracts.json'
    seen = set()
    for a in A:
        if a['id'] in seen:
            continue
        seen.add(a['id'])
        native_rel = NPC + a['native']
        explicit = a['id'] in ('lesser-vampire', 'vampire', 'master-vampire', 'elder-vampire', 'forest-wight', 'grave-wight', 'shadow-stalker')
        ident = {'id': a['id'], 'native_name': a['name'], 'source': a['srcs'][0], 'define_as': a['define_as'],
                 'type': a['type'], 'subtype': a['subtype'], 'unique': a['unique'], 'native_tall': a['native_tall'],
                 'image_source': 'explicit leaf image=' if explicit else 'NPC.lua:33 default-name image',
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
          'task': "monster-batch-n: static re-verification (no game launch) of the twelve batch-5 identities of the second gap survey (skeleton magus, ghast, shadow stalker, lesser vampire, forest wight, vampire, master vampire, ghoulking, bone giant, grave wight, elder vampire, The Shade of Telos) against game/modules/tome source and native sprites. Survey verdicts were not trusted; every field below was read from source: name, type/subtype, define_as, explicit or NPC.lua:33 default image, unique, PNG on disk, and absence of moddable_tile/shader/anim/add_displays.",
          'new_ids_not_in_catalog_before_this_batch': [i['id'] for i in identities], 'identities': identities,
          'runtime_mutation_scan': {
              'method': 'every talent of each identity (resolvers.talents, inherited base talents, racial levelup talents) was resolved to its definition under game/modules/tome/data/talents and checked for mode="sustained" and for writes to self.type/subtype/image/name/display, __old_type, replace_display, add_mos, moddable_tile, shader, textures, anim, add_displays, stealth/invisibility; timed effects were grepped for the same fields; the resolvers (sustains_at_birth, racial, nice_tile, inscriptions) were read',
              'writers_found': [
                  {'file': 'game/modules/tome/data/talents/corruptions/shadowflame.lua', 'line': 96, 'talent': "Flame of Urh'Rok", 'effect': 'type/subtype -> demon/major; no identity of this batch knows it'},
                  {'file': 'game/modules/tome/data/timed_effects/magical.lua', 'line': 271, 'talent': 'GREATER_INVISIBILITY / INVISIBILITY / ETHEREAL timed effects (lines 271, 305, 345)', 'effect': 'set self.shader for the duration then clear it; reachable only through a random rune inscription (vampires, Shade of Telos) during play; the matcher already returns native art while a shader is set (shader rule), so this is not a birth write and needs no special case'},
                  {'file': 'game/modules/tome/data/timed_effects/magical.lua', 'line': 4794, 'talent': 'LORD_OF_SKULLS timed effect (Necromancer)', 'effect': 'renames a Necromancer skeleton/bone-giant minion to "Lord of Skulls (bone giant)" and swaps its display; the changed name fails the exact-name key, so the minion falls back to native; never applied at birth and never to a native bone giant'}],
              'sustains_at_birth_review': [
                  {'identity': 'lesser vampire', 'sustained': ['Eternal Night (eradication.lua:179)'], 'note': 'temporary damage/resist-pen values and two shader_ring_rotating (or ultrashield) particle emitters; no display field'},
                  {'identity': 'vampire', 'sustained': ['Eternal Night', 'Blur Sight (talents/misc/npcs.lua:3753)'], 'note': 'Blur Sight: combat_def temporary value and a phantasm_shield particle'},
                  {'identity': 'master vampire', 'sustained': ['Eternal Night', 'Blur Sight', 'Phantasmal Shield (spells/phantasm.lua:67)'], 'note': 'Phantasmal Shield: evade/light-burst callbacks and a phantasm_shield particle'},
                  {'identity': 'elder vampire', 'sustained': ['Eternal Night', 'Blur Sight', 'Phantasmal Shield'], 'note': 'same as the master vampire'},
                  {'identity': 'forest wight', 'sustained': [], 'note': 'resolvers.sustains_at_birth() present; Flame, Lightning, Glacial Vapour, Mind Disruption are not sustained'},
                  {'identity': 'grave wight', 'sustained': [], 'note': 'resolvers.sustains_at_birth() present; Flameshock, Lightning, Glacial Vapour, Mind Disruption are not sustained'},
                  {'identity': 'skeleton magus', 'sustained': [], 'note': 'Arcane Power (arcane.lua:84) is sustained but the leaf has no sustains_at_birth; if it were used it only adds resist/spellpower values and an arcane_power particle'},
                  {'identity': 'The Shade of Telos', 'sustained': [], 'note': 'Uttercold (ice.lua) is sustained but the entity has no sustains_at_birth; if used it only adds temporary values and circular_flames particles'},
                  {'identity': 'ghast / ghoulking / bone giant / shadow stalker', 'sustained': [], 'note': 'no sustained talent; Fade is an activated talent applying EFF_FADED (invulnerable, status_effect_immune)'}],
              'visibility_review': 'no identity of this batch has stealth, invisibility or a phase talent that changes display: Shadow Stalker Fade/Phase Door/Blindside and the ghost pass_wall movement never touch image, shader or add_mos; runes are the only invisibility source and follow the shader fallback above',
              'hits_in_batch': [],
              'no_hit': ['skeleton magus', 'ghast', 'ghoulking', 'bone giant', 'lesser vampire', 'vampire', 'master vampire', 'elder vampire', 'forest wight', 'grave wight', 'shadow stalker', 'The Shade of Telos']},
          'name_collisions_checked': [
              {'name': 'ghast / ghoulking / bone giant', 'other_definitions': ['talents/spells/master-of-flesh.lua and master-of-bones.lua define Necromancer minions with the same name, type, subtype and default/nice_tile PNG and no define_as (bone giant minion also has is_bone_giant)'], 'outcome': 'same creature, same art: the minion is accepted as the same body exactly as every catalog entry accepts a summoned self (tests/token_mapping.lua summoned identity); a Lord of Skulls minion is renamed by the effect and so no longer matches the exact name; eternal/heavy/runed bone giants and the half-finished bone giant stay native or their own entries; no name+define_as key extension'},
              {'name': 'ghoul (already shipped, define_as GHOUL)', 'other_definitions': ['ghast, ghoulking, risen corpse (RISEN_CORPSE, image of the ghoul) stay separate names'], 'outcome': 'unchanged; ghast/ghoulking cannot borrow the ghoul PNG and vice versa (negative tests)'},
              {'name': 'shadow stalker', 'other_definitions': ['SHADOW_CLAW (named "shadow claw", shadow-claw.png) and SHADOW_CASTER (also named "shadow claw", shadow-caster.png) share BASE_SHADOW'], 'outcome': 'both stay native: different names; the shared name "shadow claw" is not a catalog entry; define_as SHADOW_STALKER required, negative tests for wrong/missing define_as and for the claw/caster PNGs'},
              {'name': 'vampire / lesser vampire / master vampire / elder vampire', 'other_definitions': ['vampire lord, vampire rat, The Master (shipped, unique), Arch Zephyr and other vampire subtype names have their own PNGs'], 'outcome': 'exact names only; siblings cannot borrow each other\'s PNG (negative tests); vampire lord stays native'},
              {'name': 'forest wight / grave wight', 'other_definitions': ['barrow wight and emperor wight have tall nice_tile bodies, void spectre is another name'], 'outcome': 'stay native; siblings cannot borrow each other\'s PNG'},
              {'name': 'skeleton magus', 'other_definitions': ['skeleton mage (shipped, name differs by one letter), skeleton assassin, Necromancer skeleton minions named "skeleton warrior/archer/mage"'], 'outcome': 'exact name "skeleton magus" only; negative test that the skeleton mage PNG is rejected under this name'},
              {'name': 'The Shade of Telos', 'other_definitions': ['single definition; "the shade" (undead_skeleton_the_shade.png) is another creature'], 'outcome': 'define_as SHADE_OF_TELOS and unique required; unknown uniques with the same name are rejected'}],
          'kept_native': [],
          'neighbours_kept_native': [
              {'name': 'eternal / heavy / runed bone giant', 'reason': 'not in the surveyed batch; own names and PNGs'},
              {'name': 'vampire lord, vampire rat, barrow wight, emperor wight, shadow claw (SHADOW_CLAW/SHADOW_CASTER)', 'reason': 'not in the surveyed batch or shared names with other PNGs'}]}
    out = ADDON / 'evidence/monster-batch-n-20260929/source-contracts.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(ev, indent=2, ensure_ascii=False) + '\n')
    evsha = hashlib.sha256(out.read_bytes()).hexdigest()
    for a in A:
        refs = [{'path': p, 'sha256': sha(p), 'role': r, 'note': n} for r, p, n in a['refs']]
        entry = {'asset_id': a['id'], 'native_name': a['name'], 'scope': a['scope'], 'sources': a['srcs'], 'references': refs,
                 'contrast_dimensions': list(a['dims']),
                 'prompt_fields': {'subject': a['subject'], 'contrast': a['contrast'], 'composition': a['comp'] or COMP, 'palette': a['palette']},
                 'kind': 'creature', 'max_attempts': 1, 'gate': 'ready',
                 'gate_reason': f"Exact source identity re-verified directly against game/modules/tome source (name={a['name']}, define_as={a['define_as']}, type={a['type']}/subtype={a['subtype']}, unique={a['unique']}); details and hashes in evidence/monster-batch-n-20260929/source-contracts.json. {a['structure']}. Exact catalog entry only, never a whole-subtype mapping.",
                 'render_evidence': [{'path': render, 'sha256': evsha}]}
        packs.setdefault(a['pack'], []).append(entry)
    for n, assets in packs.items():
        p = ADDON / f'art/production/batches/monster-batch-n-{n}.json'
        if p.exists():
            print('exists, skipped', p.name)
            continue
        p.write_text(json.dumps({'schema': 1, 'batch_id': f'monster-batch-n-{n}', 'assets': assets}, indent=2, ensure_ascii=False) + '\n')
        print('wrote', p.name)


if __name__ == '__main__':
    build()
