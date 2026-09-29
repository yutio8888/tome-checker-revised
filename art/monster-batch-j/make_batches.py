"""Generate the monster-batch-j task packs and the pinned source-contract
evidence. Pure bookkeeping: hashes native sources/sprites, writes JSON."""
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


def src(path, anchor, hint=None):
    lines = (WS / (D + path)).read_text().splitlines()
    cands = [i + 1 for i, l in enumerate(lines) if anchor in l]
    assert cands, (path, anchor)
    return {'path': D + path, 'sha256': sha(D + path), 'line': cands[0], 'anchor': anchor}


COMP = ("One compact complete creature on a single circular tabletop disc, steep overhead three-quarter camera; visible clear neutral base ring on every side. Keep all anatomy and equipment well inside the inner four-fifths of disc radius. Base brightness must visually match reference neutral disc, with no illumination spill or ground effects. Disc plate discipline: measured results show generations of this style reference tend to render the disc DARKER than the reference, never lighter. So do not darken the disc at all: render the neutral disc -- including the whole outer-sixth ring band and the area under the creature -- at the style reference's own brightness, if anything a hair lighter, and never darker. No warm cast, glow, bounce-light, gradient or vignette anywhere on the disc. Do not darken the creature to compensate either. Add no warm cast, glow, bounce-light, gradient or vignette to the disc anywhere, including directly under or behind dark-bodied creatures.")
DISC = " Dry neutral charcoal disc with restrained copper-grey bevel, kept a visibly lighter value than the creature's darkest parts so the two never merge."


A = []  # (pack, spec)


def asset(pack, id_, name, scope, srcs, base, define_as, typ, sub, unique, structure, native, refs, subject, contrast, palette, verdict, dims=('silhouette', 'value'), comp=None):
    A.append(dict(comp=comp, pack=pack, id=id_, name=name, scope=scope, srcs=srcs, base=base, define_as=define_as, type=typ,
                  subtype=sub, unique=unique, structure=structure, native=native, refs=refs, subject=subject,
                  contrast=contrast, palette=palette, verdict=verdict, dims=dims))


STY = ('style', STYLE, 'Approved disc, lighting and camera; do not copy its creature.')
Z = 'zones/'
SINGLE = 'no nice_tile/add_mos/shader/anim/moddable_tile on the leaf or its base; Actor tint (native colour modulation) does not change identity or display structure; generic actor.image==entry.image single path (the exact-identity path also accepts the invis.png+add_mos body every unique gets when nicer_tiles rewrites it)'
TALL = 'resolvers.nice_tile{image="invis.png", add_mos={{image=<png>, display_h=2, display_y=-1}}} names the PNG explicitly (no =BASE=TILE= indirection, so the resolve-order issue that keeps {tall=1} shorthand native does not apply); nativeTallImage matches the exact one-body add_mos, unique entry, native-tall path'

# ---- pack 1 ----
asset(1, 'shardskin', 'Shardskin', 'old-forest guaranteed guardian in the CRYSTALINE layout (giant/crystal, explicit image=)',
      [src(Z + 'old-forest/npcs.lua', 'define_as = "SHARDSKIN"'), src(Z + 'old-forest/npcs.lua', 'image = "npc/immovable_crystal_golden_crystal.png"')],
      None, 'SHARDSKIN', 'giant', 'crystal', True,
      'explicit image= npc/immovable_crystal_golden_crystal.png, standalone entity, no base, no nice_tile/add_mos/shader/anim/moddable_tile/tint; 64x64 single-cell native sprite',
      'immovable_crystal_golden_crystal.png',
      [STY,
       ('identity', NPC + 'immovable_crystal_golden_crystal.png', 'Native shape: one angular mass of golden-yellow faceted crystal shards with a bright glow. The lore says the remains of a huge tree can be seen through the surface.'),
       ('family', TOK + 'white-crystal.png', 'Shipped white crystal (tall pale bouquet of shards): show the crystal finish only; Shardskin is a broad golden mass with a trapped tree, not a slim white bouquet.')],
      "A broad, heavy mass of golden-amber faceted crystal shards heaped like a jagged low pyramid: many angular translucent honey-gold facets with pale-yellow highlight planes, and inside the glassy core the petrified remains of a huge gnarled tree are visible -- a thick warm-brown trunk stump with a few twisted root and branch stubs showing through the crystal, with a small malevolent violet glow deep in the core. Two or three larger shards jut up at the back and sides. No face, no limbs.",
      "Crystal tokens: white crystal (tall pale bouquet), red crystal (long blade fan), crimson crystal (two chunky prisms), Spellblaze Crystal (round purple spiky cluster), Spellblaze Simulacrum (person-shaped violet crystal). Shardskin is the only golden-amber crystal, a broad low pyramid mass with a visible brown tree trunk trapped inside (silhouette: wide jagged heap with a trunk in the core; hue: honey gold with brown wood and a violet core glow; value: light gold facets).",
      "Honey-gold and warm amber crystal facets at mid-light value with pale butter-yellow highlight planes, a warm-brown wood trunk inside, a small violet glow in the core; nothing darker than mid tone." + DISC,
      'READY unique single (SHARDSKIN)', ('silhouette', 'value', 'hue'))

asset(1, 'the-withering-thing', 'The Withering Thing', 'heart-gloom guaranteed guardian in the non-purified layout (animal/canine unique, default-name image, purple tint)',
      [src(Z + 'heart-gloom/npcs.lua', 'define_as = "WITHERING_THING"'), src(Z + 'heart-gloom/npcs.lua', 'name = "The Withering Thing", tint=colors.PURPLE')],
      src('general/npcs/canine.lua', 'define_as = "BASE_NPC_CANINE"'), 'WITHERING_THING', 'animal', 'canine', True,
      'base BASE_NPC_CANINE (animal/canine, no image=); no image=/nice_tile/add_mos/shader/anim/moddable_tile on leaf or base; NPC.lua:33 default-image formula gives animal_canine_the_withering_thing.png; ' + SINGLE.split(';')[1].strip(),
      'animal_canine_the_withering_thing.png',
      [STY,
       ('identity', NPC + 'animal_canine_the_withering_thing.png', 'Native shape: a gaunt, mangy, deformed wolf-like beast with a patchy grey-mauve hide and wormy growths, purple-tinted.'),
       ('family', TOK + 'warg.png', 'Shipped warg (dark broad wolf): the Withering Thing must NOT be a healthy wolf; it is emaciated and covered in worms.')],
      "A gaunt, deformed, hunched wolf-like beast seen from a steep overhead angle: patchy mangy grey-mauve hide stretched over a visible ribcage and spine, mismatched over-long forelegs, an oversized lopsided head with a gaping jaw and glowing violet eyes, and a mass of pale pink-cream worms writhing out of its back, flanks and mouth. A dull amber amulet hangs at its chest. Pale bone-coloured patches show through the rotten fur.",
      "Canine tokens: wolf (grey healthy wolf), great wolf (dark heavy), dire wolf (brown), white wolf (pure white), warg (black broad), fox (orange). The Withering Thing is the only diseased, emaciated canine: visible ribs, writhing pale worms and a lopsided head (silhouette: spiky ribs and worm tendrils, hunched), purple-mauve hide with cream worms (hue), mid value.",
      "Mid-light grey-mauve and dusty violet mangy hide with pale bone patches, cream-pink worms as the brightest planes, glowing violet eyes, dull amber amulet; nothing darker than mid tone." + DISC,
      'READY unique single (WITHERING_THING)', ('silhouette', 'value', 'hue'))

asset(1, 'the-dreaming-one', 'The Dreaming One', 'heart-gloom guaranteed guardian in the purified layout (horror/eldritch unique, explicit image=, purple tint, never_move)',
      [src(Z + 'heart-gloom/npcs.lua', 'define_as = "DREAMING_ONE"'), src(Z + 'heart-gloom/npcs.lua', 'image = "npc/seed_of_dreams.png"')],
      None, 'DREAMING_ONE', 'horror', 'eldritch', True,
      'explicit image= npc/seed_of_dreams.png (a file without a type_subtype prefix), standalone entity, no base, no nice_tile/add_mos/shader/anim/moddable_tile; tint only',
      'seed_of_dreams.png',
      [STY,
       ('identity', NPC + 'seed_of_dreams.png', 'Native shape: a large glossy pale-cyan glass sphere with a pearly lilac-pink swirl core, resting with a soft shadow.'),
       ('family', TOK + 'spellblaze-crystal.png', 'Shipped Spellblaze Crystal (round purple spiky cluster): the Dreaming One is a smooth sphere, no spikes.')],
      "A single large smooth glossy glass-like sphere resting on the disc, about two thirds of the disc width: pale luminous cyan-aqua glass with a bright white specular highlight at the upper left, and inside it a soft pearly swirl of lilac, pink and white forming a slowly turning eye-like vortex with a dark violet pupil at its centre. A few tiny pale dream-motes drift inside the glass. No face, no limbs, no spikes, no tendrils.",
      "Orb-like or eldritch tokens: Spellblaze Crystal (spiky purple cluster), the abomination (pink flesh spire), the mouth (red maw mass), horned horror. The Dreaming One is the only perfectly smooth sphere: bright pale cyan-aqua glass with a lilac-pink vortex eye (silhouette: clean circle; hue: cyan glass with lilac core; value: light).",
      "Light luminous aqua-cyan glass at mid-light value with a pearly lilac-pink and white swirl, a dark violet pupil, bright white specular gloss; the sphere must never be dark." + DISC,
      'READY unique single (DREAMING_ONE)', ('silhouette', 'value', 'hue'))

asset(1, 'weaver-queen', 'Weaver Queen', 'unhallowed-morass guaranteed guardian (spiderkin/spider unique, nice_tile native-tall)',
      [src(Z + 'unhallowed-morass/npcs.lua', 'define_as = "WEAVER_QUEEN"'), src(Z + 'unhallowed-morass/npcs.lua', 'image="npc/spiderkin_spider_weaver_queen.png"')],
      src('general/npcs/spider.lua', 'define_as = "BASE_NPC_SPIDER"'), 'WEAVER_QUEEN', 'spiderkin', 'spider', True,
      TALL + '; base BASE_NPC_SPIDER has no image=/shader; native sprite is 64x128',
      'spiderkin_spider_weaver_queen.png',
      [STY,
       ('identity', NPC + 'spiderkin_spider_weaver_queen.png', 'Native shape (64x128 tall): a huge pale frosted-blue furry spider with a cluster of glowing eyes, long jointed blue-grey legs, and flecks of light drifting around it.'),
       ('family', TOK + 'ungole.png', 'Shipped Ungole (black spider with red markings): the Weaver Queen must be a pale, furry, blue-white spider, clearly lighter than Ungole.')],
      "A very large pale spider seen from a steep overhead three-quarter angle: a thick fuzzy frost-white abdomen with soft blue-grey fur tufts and small glowing cyan clock-like dots along its back, a rounded furry head with a cluster of large glowing cyan-white eyes, and eight long jointed legs in pale blue-grey with light joints spread symmetrically across the disc. Female queen, imposing and regal, no web scenery.",
      "Spider tokens: Ungole (black spider, red markings), the spinner-type spiders are not yet covered. The Weaver Queen is the pale one: fuzzy frost-white body with cyan eyes and blue-grey legs (value: light body against a charcoal disc; hue: icy white-blue; silhouette: round furry abdomen with a wide eight-leg spread). Never black, never a red-marked spider.",
      "Frost-white and pale blue-grey fur at mid-light to light value, cool cyan glowing eyes and small cyan dots, blue-grey jointed legs with pale joints; nothing darker than mid tone." + DISC,
      'READY unique native-tall (WEAVER_QUEEN)', ('silhouette', 'value', 'hue'))

# ---- pack 2 ----
asset(2, 'murgol', 'Murgol, the Yaech Lord', 'murgol-lair guaranteed guardian in the non-INVASION layout (humanoid/yaech unique, default-name image)',
      [src(Z + 'murgol-lair/npcs.lua', 'define_as = "MURGOL"'), src(Z + 'murgol-lair/npcs.lua', 'name = "Murgol, the Yaech Lord"')],
      src('general/npcs/yaech.lua', 'define_as = "BASE_NPC_YAECH"'), 'MURGOL', 'humanoid', 'yaech', True,
      'base BASE_NPC_YAECH (humanoid/yaech, no image=); no image=/nice_tile/add_mos/shader/anim/moddable_tile; NPC.lua:33 gives humanoid_yaech_murgol__the_yaech_lord.png; ' + SINGLE.split(';')[1].strip(),
      'humanoid_yaech_murgol__the_yaech_lord.png',
      [STY,
       ('identity', NPC + 'humanoid_yaech_murgol__the_yaech_lord.png', 'Native shape: a small floating fish-headed yaech with a spiny fin crest, red eyes, dark armour and a golden trident, wrapped in a blue psionic glow.'),
       ('family', TOK + 'lady-zoisla.png', 'Shipped Lady Zoisla (naga with trident): Murgol is a small finned yaech in armour, no serpent tail, no woman.')],
      "A small squat fish-like yaech warlord: a big round head with a jagged fin crest of spines, wide staring red eyes, a frog-like wide mouth and gill frills, pale blue-grey scaly skin, wearing lifted slate-blue eel-skin armour plates with pale rims, gripping a tall golden trident in one hand and the other hand raised with a pale blue psionic ring of light around it. Hunched aggressive stance on stubby webbed feet. Compact and complete.",
      "Aquatic humanoids: Lady Zoisla and the naga tidewarden/tidecaller (serpent tails, tall), the merman-like yaech are not otherwise covered. Murgol is small and round-headed with a fin crest and red eyes, standing on legs (silhouette: big head with spines, trident held upright), pale blue-grey skin and slate-blue armour (hue/value), not a naga.",
      "Pale blue-grey scaly skin, slate-blue armour plates lifted with pale rims, bright red eyes, gold trident, soft pale-blue psionic ring; nothing darker than mid tone." + DISC,
      'READY unique single (MURGOL)', ('silhouette', 'value', 'hue'))

asset(2, 'lady-nashva', 'Lady Nashva the Streambender', 'murgol-lair guaranteed guardian in the INVASION layout (humanoid/naga unique, nice_tile native-tall)',
      [src(Z + 'murgol-lair/npcs.lua', 'define_as = "NASHVA"'), src(Z + 'murgol-lair/npcs.lua', 'image="npc/humanoid_naga_lady_nashva_the_streambender.png"')],
      src('general/npcs/naga.lua', 'define_as = "BASE_NPC_NAGA"'), 'NASHVA', 'humanoid', 'naga', True,
      TALL + '; base BASE_NPC_NAGA has no image=/shader; native sprite is 64x128; entity only exists when the zone is invaded',
      'humanoid_naga_lady_nashva_the_streambender.png',
      [STY,
       ('identity', NPC + 'humanoid_naga_lady_nashva_the_streambender.png', 'Native shape (64x128 tall): a pale-skinned naga woman with long dark hair and a circlet, a jewelled blue bodice, a dark tail coiled tight, a tall glowing teal trident in one hand and a glowing blue water orb in the other, water swirling around her.'),
       ('family', TOK + 'lady-zoisla.png', 'Shipped Lady Zoisla (naga with orange-red tail and a gold trident): Nashva must differ by teal-blue water palette, dark-teal tail, water orb and a circlet.')],
      "A regal naga woman rearing up from a tightly coiled slate-teal serpent tail with pale blue scale highlights: pale skin, long dark hair, a small silver circlet, a jewelled pale-blue bodice, one hand raised holding a glowing blue water orb, the other holding a tall teal glowing trident upright, and a ring of pale blue water swirling around her coils on the disc. Calm, confident stare. Compact upright composition seen from a steep overhead three-quarter angle.",
      "Naga tokens: Lady Zoisla (orange-red tail, gold trident, brown hair), naga tidewarden (male, tan tail, shield), naga tidecaller (hooded dark caster). Nashva is the water-blue one: slate-teal tail with pale highlights, teal trident, glowing water orb and circlet (hue: cool teal-blue against Zoisla's warm orange; silhouette: tight coil with orb and trident held up).",
      "Slate-teal serpent tail lifted with pale aqua highlights, pale skin, dark hair, silver circlet, luminous blue water orb and pale water ring, glowing teal trident; nothing darker than mid tone." + DISC,
      'READY unique native-tall (NASHVA)', ('silhouette', 'value', 'hue'))

asset(2, 'the-possessed', 'The Possessed', 'ruins-kor-pul guaranteed guardian in the HIDEOUT layout (humanoid/human unique, nice_tile native-tall)',
      [src(Z + 'ruins-kor-pul/npcs.lua', 'define_as = "THE_POSSESSED"'), src(Z + 'ruins-kor-pul/npcs.lua', 'image="npc/humanoid_human_the_possessed.png"')],
      src('general/npcs/thieve.lua', 'define_as = "BASE_NPC_THIEF"'), 'THE_POSSESSED', 'humanoid', 'human', True,
      TALL + '; base BASE_NPC_THIEF has no image=/shader; native sprite is 64x128. Ordinary thieves/rogues/cutpurses keep their own catalog entries',
      'humanoid_human_the_possessed.png',
      [STY,
       ('identity', NPC + 'humanoid_human_the_possessed.png', 'Native shape (64x128 tall): a cloaked dagger fighter whose face is a glowing green mask, in a dark green cloak with gold trim, with an orange flame-like halo crown behind the head.'),
       ('family', TOK + 'harno.png', 'Shipped Harno (hooded blue-grey cloak, two knives): The Possessed has a bare glowing green face, a green cloak and a fiery crown, not a blue-grey hood.')],
      "A tall gaunt human bandit possessed by a spirit: a glowing pale-green skull-like face with hollow bright eyes, an orange-gold flame-shaped spectral crown rising behind the head, a long moss-green cloak with gold trim thrown wide over dark brown leathers, a dagger in each hand, one held high and one low, in a menacing dual-dagger stance. Compact upright composition seen from a steep overhead three-quarter angle.",
      "Human rogue tokens: thief (brown hooded), rogue (dark blue), cutpurse (white shirt), bandit (bare-chested), Harno (blue-grey hooded cloak), Celia and Necromancer. The Possessed is the green one: glowing green skull face, moss-green cloak with gold trim and an orange flame crown (silhouette: wide cloak with a flame crown; hue: green plus orange flame; value: mid green cloak, bright face and flame).",
      "Mid moss-green cloak lifted with lighter olive fold planes and gold trim, glowing pale-green face, orange-gold flame crown as the brightest plane, steel daggers; nothing darker than mid tone." + DISC,
      'READY unique native-tall (THE_POSSESSED)', ('silhouette', 'value', 'hue'))

asset(2, 'subject-z', 'Subject Z', 'halfling-ruins guaranteed guardian on the last-level static map (humanoid/human unique, default-name image, never_act until seen)',
      [src(Z + 'halfling-ruins/npcs.lua', 'define_as="SUBJECT_Z"'), src(Z + 'halfling-ruins/npcs.lua', 'name = "Subject Z"')],
      None, 'SUBJECT_Z', 'humanoid', 'human', True,
      'standalone entity (no base), no image=/nice_tile/add_mos/shader/anim/moddable_tile/tint; NPC.lua:33 gives humanoid_human_subject_z.png; ' + SINGLE.split(';')[1].strip(),
      'humanoid_human_subject_z.png',
      [STY,
       ('identity', NPC + 'humanoid_human_subject_z.png', 'Native shape: an ordinary-looking young man with shoulder-length dark hair in a plain white tunic and green trousers, standing upright with both arms flared wide, a long dagger in each hand.'),
       ('family', TOK + 'cutpurse.png', 'Shipped cutpurse (white vest, brown trousers, crouched with daggers low): Subject Z stands stiffly upright with arms spread wide and has green trousers and long dark hair.')],
      "A gaunt pale human man standing rigidly upright and facing the viewer with both arms flared wide out to the sides: shoulder-length straight dark hair, a blank calm face, a plain cream-white linen tunic with a rope belt, moss-green trousers and worn brown boots, a long slim dagger held point-up in each hand. Symmetrical Vitruvian stance, uncanny and still.",
      "Human dagger fighters: cutpurse (crouched, brown trousers), rogue (blue hooded), thief (brown cloak), bandit (bare-chested), Harno, and the Assassin Lord (bulky mantle, crouched lunge). Subject Z is the only stiff symmetrical upright figure with arms flared wide, cream tunic and moss-green trousers (silhouette: T-shaped standing figure with two raised daggers; hue: cream plus green).",
      "Cream-white tunic as the brightest plane, moss-green trousers, brown boots and belt, dark hair, pale skin, steel daggers; nothing darker than mid tone except the hair." + DISC,
      'READY unique single (SUBJECT_Z)', ('silhouette', 'value', 'hue'))

# ---- pack 3 ----
asset(3, 'grand-corruptor', 'Grand Corruptor', 'mark-spellblaze guaranteed guardian on the last-level static map (humanoid/shalore unique, default-name image); town-zigur defines a second, same-named Grand Corruptor (unique="Grand Corruptor Zigur", same define_as, same default image)',
      [src(Z + 'mark-spellblaze/npcs.lua', 'define_as = "GRAND_CORRUPTOR"'), src(Z + 'mark-spellblaze/npcs.lua', 'name = "Grand Corruptor", color=colors.VIOLET, unique = true')],
      src('general/npcs/elven-caster.lua', 'define_as = "BASE_NPC_ELVEN_CASTER"'), 'GRAND_CORRUPTOR', 'humanoid', 'shalore', True,
      'base BASE_NPC_ELVEN_CASTER (humanoid/shalore, no image=); no image=/nice_tile/add_mos/shader/anim/moddable_tile; NPC.lua:33 gives humanoid_shalore_grand_corruptor.png; ' + SINGLE.split(';')[1].strip() + '. town-zigur/npcs.lua:28 defines the same name, define_as and image (unique="Grand Corruptor Zigur", rank 3.5): it is the same character design, so the exact entry also serves it (documented, tested)',
      'humanoid_shalore_grand_corruptor.png',
      [STY,
       ('identity', NPC + 'humanoid_shalore_grand_corruptor.png', 'Native shape: a pale elf in a horned indigo-black cowl and dark blue robe with a crimson-pink sigil sash, holding a tall dark staff.'),
       ('family', TOK + 'rhaloren-inquisitor.png', 'Shipped Rhaloren Inquisitor (armoured elf knight with a sword): the Grand Corruptor is a robed staff caster in a horned cowl, no armour, no sword.')],
      "A gaunt pale elven blood-mage: a tall horned cowl with two curved horn tips over a pale narrow face with long pointed ears, a long sapphire-indigo robe with wide sleeves and lighter steel-blue fold planes, a bright crimson-magenta sigil sash and bright crimson trim, pale hands holding a tall dark staff topped with a glowing blood-red orb. Upright imposing stance seen from a steep overhead three-quarter angle.",
      "Robed casters: necromancer (bald human, slate-violet robe), Kryl-Feijan acolyte (bare silver hair, mauve robe), Harno (hooded blue-grey), Fillarel (gold robe), Celia (pale gown), Urkis (blue lightning). Rhaloren Inquisitor is an armoured knight. The Grand Corruptor is the only one in a horned indigo cowl with a crimson sash and a red-orb staff (silhouette: two horn tips and a tall staff; hue: sapphire-indigo plus crimson).",
      "Sapphire-indigo robe lifted with light steel-blue fold planes, bright crimson-magenta sash and trim, pale face and hands as the value break, dark-brown staff with a glowing red orb; the robe must never be near-black." + DISC,
      'READY unique single (GRAND_CORRUPTOR)', ('silhouette', 'value', 'hue'))

asset(3, 'assassin-lord', 'Assassin Lord', 'thieves-tunnels quest boss on the level-2 static map (humanoid/human unique, default-name image, cant_be_moved)',
      [src(Z + 'thieves-tunnels/npcs.lua', 'define_as = "ASSASSIN_LORD"'), src(Z + 'thieves-tunnels/npcs.lua', 'name = "Assassin Lord", unique = true')],
      None, 'ASSASSIN_LORD', 'humanoid', 'human', True,
      'standalone entity (no base), no image=/nice_tile/add_mos/shader/anim/moddable_tile/tint; NPC.lua:33 gives humanoid_human_assassin_lord.png; ' + SINGLE.split(';')[1].strip(),
      'humanoid_human_assassin_lord.png',
      [STY,
       ('identity', NPC + 'humanoid_human_assassin_lord.png', 'Native shape: a stocky dark-haired man in a moss-green fur-collared mantle over a patterned tan tabard, yellow sleeves and red trousers, a dagger in each raised hand.'),
       ('family', TOK + 'bandit.png', 'Shipped bandit (bare-chested, two knives low): the Assassin Lord is fully dressed in a green mantle, red trousers and gold sleeves.')],
      "A stocky broad-shouldered human assassin in a lunging crouch: dark tousled hair and a hard face, a moss-olive fur-collared mantle over a patterned tan tabard, golden-yellow sleeves, crimson trousers and brown boots, a long dagger in each hand with faint green poison on the blades, one blade raised and one pointing forward. Menacing, compact, complete.",
      "Human dagger fighters: cutpurse (white vest), rogue (dark blue), thief (brown hooded), bandit (bare-chested), Harno (blue-grey hood), Subject Z (stiff upright, cream tunic). The Assassin Lord is the bulky one in an olive fur-collared mantle with crimson trousers and gold sleeves in a lunge (silhouette: wide mantle shoulders, forward lunge; hue: olive, gold and crimson).",
      "Moss-olive mantle with a pale fur collar, tan patterned tabard, golden-yellow sleeves, crimson trousers, brown boots, steel blades with a hint of green poison; nothing darker than mid tone except the hair." + DISC,
      'READY unique single (ASSASSIN_LORD)', ('silhouette', 'value', 'hue'))

asset(3, 'ben-cruthdar-abomination', 'Ben Cruthdar, the Abomination', 'temporal-rift guaranteed guardian, first entry to level 2 (humanoid/temporal unique, explicit image= reusing the sprite of Ben Cruthdar, the Cursed of town-lumberjack-village)',
      [src(Z + 'temporal-rift/npcs.lua', 'define_as = "BEN_CRUTHDAR_ABOMINATION"'), src(Z + 'temporal-rift/npcs.lua', 'image = "npc/humanoid_human_ben_cruthdar__the_cursed.png"')],
      None, 'BEN_CRUTHDAR_ABOMINATION', 'humanoid', 'temporal', True,
      'explicit image= npc/humanoid_human_ben_cruthdar__the_cursed.png, standalone entity, no nice_tile/add_mos/shader/anim/moddable_tile/tint; the same PNG belongs natively to "Ben Cruthdar, the Cursed" (town-lumberjack-village, other name/type), which stays native because the catalog is keyed by exact name and type',
      'humanoid_human_ben_cruthdar__the_cursed.png',
      [STY,
       ('identity', NPC + 'humanoid_human_ben_cruthdar__the_cursed.png', 'Native portrait (shared with Ben Cruthdar, the Cursed): a hulking pale bald madman in brown leather rags with a huge two-headed battleaxe.'),
       ('family', TOK + 'krogar.png', 'Shipped Krogar (armoured green orc with a club): Ben is a pale human abomination in rags, twisted by temporal energy, with a battleaxe.')],
      "A hulking hunched pale human madman twisted by time: bald head, gaunt crazed face with wide pale eyes, bare grey-white skin crossed by thin glowing cyan temporal cracks, ragged brown leather straps and tattered rags, one enormous shoulder and arm, gripping a huge double-bladed steel battleaxe across his body, with a faint translucent cyan afterimage of the axe and arm slightly offset as if phasing out of time. Compact and complete.",
      "Human/orc brutes: bandit (bare-chested, knives), krogar and Massok (green orcs), Norgan (dwarf), Shax and Bill (trolls), the abomination (pink flesh spire). Ben is the only pale bald hunched human with a huge battleaxe and cyan temporal cracks (silhouette: hunched with a big axe across the body; hue: grey-white skin, brown rags, cyan cracks).",
      "Pale grey-white skin as the value break, mid brown leather and rags lifted with lighter tan planes, steel axe blades, thin cyan temporal cracks and a faint cyan afterimage; nothing darker than mid tone." + DISC,
      'READY unique single (BEN_CRUTHDAR_ABOMINATION)', ('silhouette', 'value', 'hue'))



# ---- geometry retries (v1 was rejected at the gate for weapons/limbs beyond the disc; the earlier pack keeps its own ledger) ----
def retry(id_, pack, **changes):
    base = next(a for a in A if a['id'] == id_)
    A.append(dict(base, pack=pack, **changes))


FIT = " Calibration from the previous generation of this exact token: it drew the weapon and limbs (and effect rings) reaching past the edge of the disc onto the transparent canvas, so the token could not be exported. This time draw the creature markedly smaller and tighter: the ENTIRE figure, including the tip of every weapon, every raised hand and every swirl, fits inside a circle of about two thirds of the disc radius around the disc centre, leaving a wide bare charcoal ring of base plate on every side. Shorten weapons and hold them close to the body, nothing extends toward the disc rim."
retry('murgol', 4,
      comp=COMP + FIT,
      subject="A small squat fish-like yaech warlord: a big round head with a jagged fin crest of spines, wide staring red eyes, a frog-like wide mouth and gill frills, pale blue-grey scaly skin, wearing lifted slate-blue eel-skin armour plates with pale rims, holding a SHORT golden trident close against his body pointing upward (the trident is no taller than his head), the other hand raised beside his chest with a small pale blue psionic ring of light. Hunched aggressive stance on stubby webbed feet. Compact and complete, small on the disc.")
retry('lady-nashva', 4,
      comp=COMP + FIT,
      subject="A regal naga woman rearing up from a tightly coiled slate-teal serpent tail with pale blue scale highlights: pale skin, long dark hair, a small silver circlet, a jewelled pale-blue bodice, one hand held near her chest holding a small glowing blue water orb, the other holding a SHORT glowing teal trident close against her side pointing upward (the trident's top is no higher than the top of her head), and a thin flat ring of pale blue water lying on the disc immediately around her coils. Calm, confident stare. Compact upright composition, small on the disc.")
retry('subject-z', 4,
      comp=COMP + FIT,
      subject="A gaunt pale human man standing upright and facing the viewer with his arms held out only slightly from his sides, elbows bent, forearms angled upward: shoulder-length straight dark hair, a blank calm face, a plain cream-white linen tunic with a rope belt, moss-green trousers and worn brown boots, a SHORT dagger held point-up in each hand at shoulder height close to the body. Stiff, symmetrical, uncanny and still; the whole figure narrow and compact, small on the disc.")


# ---- value retries (v1 passed the numeric gate but the masked-body luminance / 48px floor readability failed) ----
retry('grand-corruptor', 5,
      subject="A gaunt pale elven blood-mage: a tall horned cowl with two curved horn tips in a bright royal sapphire-blue over a pale narrow face with long pointed ears, a long robe in clearly mid-light cobalt and steel-blue with broad pale periwinkle fold planes and light silver-blue edge highlights, a bright crimson-magenta sigil sash and bright crimson trim, pale hands holding a tall warm-brown staff topped with a glowing blood-red orb. Upright imposing stance seen from a steep overhead three-quarter angle.",
      palette="Robe and cowl in bright cobalt and steel-blue at mid-light value, lifted with broad pale periwinkle fold planes and silver-blue rim light; bright crimson-magenta sash and trim; pale face and hands; warm-brown staff with a glowing red orb; nothing darker than mid tone, never navy, indigo-black or near-black." + DISC,
      contrast="Robed casters: necromancer (bald human, slate-violet robe), Kryl-Feijan acolyte (bare silver hair, mauve robe), Harno (hooded blue-grey), Fillarel (gold robe), Celia (pale gown), Urkis (blue lightning). Rhaloren Inquisitor is an armoured knight. A first draft of this token was a near-black navy robe that merged with dark floors at 48px. This redraw is a bright cobalt and steel-blue robe with pale fold planes (value/hue) in a horned cowl with a crimson sash and a red-orb staff (silhouette), far lighter than the first draft.")
retry('the-possessed', 5,
      subject="A tall gaunt human bandit possessed by a spirit: a glowing pale-green skull-like face with hollow bright eyes, an orange-gold flame-shaped spectral crown rising behind the head, a long light sage-green cloak with bright gold trim thrown wide over warm tan-brown leathers, a dagger in each hand, one held high and one low, in a menacing dual-dagger stance. Compact upright composition seen from a steep overhead three-quarter angle.",
      palette="Cloak in light sage and moss green at mid-light value with broad pale-olive fold planes and bright gold trim, warm tan leathers, glowing pale-green face and orange-gold flame crown as the brightest planes, steel daggers; nothing darker than mid tone, never a dark forest-green or black cloak." + DISC,
      contrast="Human rogue tokens: thief (brown hooded), rogue (dark blue), cutpurse (white shirt), bandit (bare-chested), Harno (blue-grey hooded cloak), Celia and Necromancer. A first draft of this token had a dark forest-green cloak that read as a dim mass at 48px. This redraw is a clearly lighter sage-green cloak with gold trim, a glowing green skull face and an orange flame crown (silhouette: wide cloak with a flame crown; hue: sage green plus orange; value: mid-light cloak).")


# ---- size retry: v2 passed the gate but the figure was tiny on the disc (48px, cream tunic close to the cutpurse) ----
FIT2 = " Calibration from two previous generations of this exact token: the first drew the daggers and outstretched arms past the disc edge; the second kept everything inside but drew the whole figure too small, only about a third of the disc wide. This time make the figure large: standing figure about as tall as three quarters of the disc diameter, arms bent so the hands stay close to the shoulders, daggers held upright above the hands and shorter than the head, all clearly inside the inner four-fifths of the disc radius with a bare ring of base plate on every side."
retry('subject-z', 6,
      comp=COMP + FIT2,
      subject="A gaunt pale human man standing rigidly upright and facing the viewer, drawn large: shoulder-length straight dark hair, a blank calm face, a broad-sleeved cream-white linen tunic with a rope belt, moss-green trousers and worn brown boots, both elbows bent outward and both hands raised at shoulder height each holding a short dagger point-up. Symmetrical, stiff, uncanny and still.")


KYLESS = {
    'native_name': 'Kyless', 'define_as': 'KYLESS', 'type': 'humanoid', 'subtype': 'human', 'unique': True,
    'source': src('zones/keepsake-meadow/npcs.lua', 'define_as="KYLESS"'),
    'nice_tile_source': src('zones/keepsake-meadow/npcs.lua', 'resolvers.nice_tile{tall=1},'),
    'native_image_path': NPC + 'humanoid_human_kyless.png',
    'native_image_sha256': sha(NPC + 'humanoid_human_kyless.png'),
    'decision': 'KEEP NATIVE (no token made, no catalog entry)',
    'reason': 'Kyless uses the resolvers.nice_tile{tall=1} shorthand with no image= anywhere in his entity (no base). resolvers.calc.nice_tile (modules/tome/resolvers.lua:1375-1385) expands it to add_mos={{image=e.image,display_h=2,display_y=-1}} using e.image at resolve time; NPC.lua:33 fills the default image only later in NPC:init, after Zone:finishEntity has already resolved the template (engine/Zone.lua:633; the same trace that kept xhaiak arachnomancer and shiaak venomblade native in batch F). The add_mos image is therefore most likely nil, so the tall body the catalog matcher requires (add_mos image == entry.image) cannot be pinned statically and a token could sit dead or hide a blank native body. Quest state also matters: Kyless spawns with never_act=true, seen_by activates him and calls the keepsake quest hooks (on_kyless_encounter/on_kyless_death), and the quest, not the entity, owns the surrounding presentation. Nothing here could be confirmed without launching the game, which this task forbids.',
}

def build():
    packs = {}
    identities = []
    render = 'game/addons/tome-checker-revised/evidence/monster-batch-j-20260929/source-contracts.json'
    seen = set()
    for a in A:
        if a['id'] in seen:
            continue
        seen.add(a['id'])
        native_rel = NPC + a['native']
        ident = {'id': a['id'], 'native_name': a['name'], 'source': a['srcs'][0], 'define_as': a['define_as'],
                 'type': a['type'], 'subtype': a['subtype'], 'unique': a['unique'], 'structure': a['structure'],
                 'native_image': 'npc/' + a['native'], 'native_image_path': native_rel,
                 'native_image_sha256': sha(native_rel), 'verdict': a['verdict']}
        if a['base']:
            ident['base_source'] = a['base']
        if len(a['srcs']) > 1:
            ident['extra_sources'] = a['srcs'][1:]
        identities.append(ident)
    ev = {'schema': 1,
          'task': 'monster-batch-j: static re-verification (no game launch) of the twelve guaranteed bosses/uniques of the second gap survey (batch 1) against game/modules/tome source and native sprites; Kyless stays native (see kept_native).',
          'new_ids_not_in_catalog_before_this_batch': [i['id'] for i in identities], 'identities': identities,
          'kept_native': [KYLESS]}
    out = ADDON / 'evidence/monster-batch-j-20260929/source-contracts.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(ev, indent=2, ensure_ascii=False) + '\n')
    evsha = hashlib.sha256(out.read_bytes()).hexdigest()
    for a in A:
        refs = [{'path': p, 'sha256': sha(p), 'role': r, 'note': n} for r, p, n in a['refs']]
        entry = {'asset_id': a['id'], 'native_name': a['name'], 'scope': a['scope'], 'sources': a['srcs'], 'references': refs,
                 'contrast_dimensions': list(a['dims']),
                 'prompt_fields': {'subject': a['subject'], 'contrast': a['contrast'], 'composition': a['comp'] or COMP, 'palette': a['palette']},
                 'kind': 'creature', 'max_attempts': 1, 'gate': 'ready',
                 'gate_reason': f"Exact source identity re-verified directly against game/modules/tome source (name={a['name']}, define_as={a['define_as']}, type={a['type']}/subtype={a['subtype']}, unique={a['unique']}); details and hashes in evidence/monster-batch-j-20260929/source-contracts.json. {a['structure']}. Exact catalog entry only, never a whole-subtype mapping.",
                 'render_evidence': [{'path': render, 'sha256': evsha}]}
        packs.setdefault(a['pack'], []).append(entry)
    for n, assets in packs.items():
        p = ADDON / f'art/production/batches/monster-batch-j-{n}.json'
        if p.exists():
            print('exists, skipped', p.name)
            continue
        p.write_text(json.dumps({'schema': 1, 'batch_id': f'monster-batch-j-{n}', 'assets': assets}, indent=2, ensure_ascii=False) + '\n')
        print('wrote', p.name)


if __name__ == '__main__':
    build()
