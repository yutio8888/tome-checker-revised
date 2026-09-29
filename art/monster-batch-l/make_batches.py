"""Generate the monster-batch-l task packs and the pinned source-contract
evidence (survey-2 section 7, batch 3: orcs, shalore elves, nagas, yaech
diver, plus Kyless). Pure bookkeeping: hashes native sources/sprites, writes JSON.
Retry packs are appended by later edits of this file (never overwritten)."""
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
SINGLE = 'no image=/nice_tile/add_mos/shader/anim/moddable_tile on the leaf or its base; no tint; generic actor.image==entry.image single path'
TALL = 'resolvers.nice_tile{image="invis.png", add_mos={{image="<png>", display_h=2, display_y=-1}}} names the PNG explicitly (no =BASE=TILE= indirection and no {tall=1} shorthand), so the resolved tall body is statically pinnable (the batch F xhaiak/shiaak/Kyless obstacle does not apply); native sprite is 64x128; catalog nativeTallImage matches the one-body add_mos'
SQ = 'zones/'

AC = 'general/npcs/aquatic_critter.lua'
AD = 'general/npcs/aquatic_demon.lua'
SP = 'general/npcs/spider.lua'
MO = 'zones/unhallowed-morass/npcs.lua'

# ---- shared source anchors ----
OR = 'general/npcs/orc.lua'
EW = 'general/npcs/elven-warrior.lua'
EC = 'general/npcs/elven-caster.lua'
NG = 'general/npcs/naga.lua'
YA = 'general/npcs/yaech.lua'
ML = 'zones/murgol-lair/npcs.lua'
SF = 'zones/slazish-fen/npcs.lua'
KM = 'zones/keepsake-meadow/npcs.lua'
DEFAULT_HUM = 'no image=/nice_tile/add_mos/shader/anim/moddable_tile/tint on the leaf or its base; generic actor.image==entry.image single path; NPC.lua:33 default-name image'


def R(family_id, note):
    return ('family', TOK + family_id + '.png', note)


def IDN(png, note):
    return ('identity', NPC + png, note)


# ---- pack 1: orcs and the naga myrmidon ----
asset(1, 'orc-warrior', 'orc warrior', 'reknor, reknor-escape, grushnak/gorbat pride, eruan, dreams, high-peak and other general orc spawns (humanoid/orc, define_as HILL_ORC_WARRIOR, default-name image, non-unique). The Charred Scar attacker of the same name (define_as ORC_ATTACK, other base) must stay native',
      [src(OR, 'name = "orc warrior", color=colors.LIGHT_UMBER')], src(OR, 'define_as = "BASE_NPC_ORC"'), 'HILL_ORC_WARRIOR', 'humanoid', 'orc', False, False,
      'base BASE_NPC_ORC (humanoid/orc, no image=); leaf define_as HILL_ORC_WARRIOR; ' + DEFAULT_HUM + ' gives humanoid_orc_orc_warrior.png; reknor-escape only lowers level_range; charred-scar defines a second "orc warrior" (define_as ORC_ATTACK, base BASE_NPC_ORC_ATTACKER) that the define_as check rejects, so no name+define_as key extension is needed',
      'humanoid_orc_orc_warrior.png',
      [STY, IDN('humanoid_orc_orc_warrior.png', 'Native shape: a hunched, wide-stanced olive-green orc in grey-green plate over a torn dark skirt, holding a long curved scimitar out to the left, bare head with a heavy jaw.'),
       R('krogar', 'Shipped Krogar (brown leather-clad brute with a mace): the orc warrior is a lighter olive-green regular soldier with a curved blade, not a brown leather brute.')],
      "A hardy hunched orc warrior seen from a steep overhead three-quarter angle: olive-green skin, a heavy jawed bare head with small tusks, a rounded olive-green breastplate with worn brass rivets over a rust-brown leather tunic and a ragged khaki skirt, thick arms, a long curved scimitar with a bright steel blade held out low to the left side in a wide diagonal slash, the other fist clenched, a wide braced stance. Weathered, sturdy and complete.",
      "Orc tokens: Brotoq (near-black plate, raised sword), Golbug (gold horned), Krogar (brown leather brute), Massok (dark horned helm). The three ordinary orcs are built together: the warrior is the one with the long curved scimitar swung out to the left over olive and rust-brown plate (silhouette: wide stance plus a diagonal curved blade; hue: olive green with rust-brown leather; value: mid). The soldier carries a heavy axe in grey spiked steel; the archer holds a tall bow in khaki leather.",
      "Mid olive-green skin and breastplate lifted with lighter moss planes, rust-brown leather, tan khaki skirt, bright steel blade; nothing darker than mid tone except small seams." + DISC,
      'READY single (orc warrior)', ('silhouette', 'value', 'hue'))

asset(1, 'orc-soldier', 'orc soldier', 'reknor, reknor-escape, grushnak/gorbat pride, dreams, eruan, high-peak and orc group spawns (humanoid/orc, define_as ORC, default-name image, non-unique)',
      [src(OR, 'name = "orc soldier", color=colors.DARK_RED')], src(OR, 'define_as = "BASE_NPC_ORC"'), 'ORC', 'humanoid', 'orc', False, False,
      'base BASE_NPC_ORC (humanoid/orc, no image=); leaf define_as ORC; ' + DEFAULT_HUM + ' gives humanoid_orc_orc_soldier.png; group spawns reference the name only',
      'humanoid_orc_orc_soldier.png',
      [STY, IDN('humanoid_orc_orc_soldier.png', 'Native shape: a heavily armoured orc in dark grey-green spiked plate with jagged shoulder blades and a tattered fringe of cloth strips, a big battleaxe hanging low on the left and a tusked helmeted face.'),
       R('massok', 'Shipped Massok (near-black horned orc): the orc soldier is a plain regular soldier in lighter grey steel spiked plate with an axe, no horned crown.')],
      "A heavily armoured orc soldier seen from a steep overhead three-quarter angle: a stocky figure in cool grey steel plate with sharp jagged spiked shoulder plates and spiked knees over a fringe of tattered olive-brown cloth strips, an olive-green tusked face under a plain open steel cap, and a big two-bladed battleaxe held low on the left with a broad bright steel axe head that sticks out clearly to the side, stout planted legs. Brutal, armoured and complete.",
      "Orc tokens: Brotoq (near-black plate), Golbug (gold), Krogar (brown leather), Massok (dark horned helm), plus the ordinary orc warrior (olive-and-rust with a curved scimitar) and archer (khaki with a tall bow) built beside it. The soldier is the one in cool light-grey spiked steel plate with a broad-headed axe (silhouette: spiked jagged shoulders, wide axe head at the side; hue: cool grey steel with olive skin; value: mid-light steel).",
      "Mid-light cool grey steel plate with pale highlights and bright edges, olive-green skin, olive-brown cloth fringe, bright steel axe head; nothing darker than mid tone except seams." + DISC,
      'READY single (orc soldier)', ('silhouette', 'value', 'hue'))

asset(1, 'orc-archer', 'orc archer', 'reknor, reknor-escape, grushnak/gorbat pride, dreams, eruan, high-peak, grushnak-armory and orc-hatred vault (humanoid/orc, define_as HILL_ORC_ARCHER, default-name image, non-unique)',
      [src(OR, 'name = "orc archer", color=colors.UMBER')], src(OR, 'define_as = "BASE_NPC_ORC"'), 'HILL_ORC_ARCHER', 'humanoid', 'orc', False, False,
      'base BASE_NPC_ORC (humanoid/orc, no image=); leaf define_as HILL_ORC_ARCHER; ' + DEFAULT_HUM + ' gives humanoid_orc_orc_archer.png; the grushnak-armory random_boss archer changes the name, so it cannot match',
      'humanoid_orc_orc_archer.png',
      [STY, IDN('humanoid_orc_orc_archer.png', 'Native shape: a hunched olive-green orc in grey-green armour drawing a big longbow held across the body, an arrow nocked, tusked face under a heavy brow.'),
       R('brotoq', 'Shipped Brotoq (near-black plate orc with a raised curved blade): the archer is a lean khaki-leather bowman with a tall bow, not a heavy sword fighter.')],
      "A lean orc archer seen from a steep overhead three-quarter angle: olive-green skin, tusked face under a heavy brow and a khaki-tan leather hood pushed back, khaki and sand-brown leather jerkin with a few dull steel plates, a quiver of feathered arrows at the shoulder, a large tall longbow of pale wood with a taut string held upright across the body in the front and a long arrow nocked and aimed, crouched wide stance. Alert and complete.",
      "Orc tokens: Brotoq, Golbug, Krogar, Massok plus the ordinary orc warrior (olive-and-rust with a curved scimitar) and orc soldier (grey spiked steel with an axe) built beside it. The archer is the lean one in light khaki leather with a tall upright bow arc and nocked arrow (silhouette: tall bow arc plus arrow line; hue: khaki tan and pale wood; value: mid-light).",
      "Mid-light khaki tan and sand-brown leather with pale wood bow, olive-green skin, dull steel plates, pale feathers; nothing darker than mid tone except the string and seams." + DISC,
      'READY single (orc archer)', ('silhouette', 'value', 'hue'))

asset(1, 'naga-myrmidon', 'naga myrmidon', 'temple-of-creation, ardhungol, naga portal events and arena (humanoid/naga, explicit image=npc/naga_myrmidon.png, no define_as, non-unique, single-cell 64x64)',
      [src(NG, 'name = "naga myrmidon", color=colors.DARK_UMBER, image="npc/naga_myrmidon.png"')], src(NG, 'define_as = "BASE_NPC_NAGA"'), None, 'humanoid', 'naga', False, False,
      'base BASE_NPC_NAGA (humanoid/naga, no image=); leaf sets the explicit image npc/naga_myrmidon.png (64x64; sibling files naga_myrmidon_2/_no_armor are Birther race preview art, not NPC images); no nice_tile/add_mos/shader/anim/moddable_tile/tint; the tall naga nereid and the shipped tidewarden/tidecaller/Nashva/Zoisla are other names',
      'naga_myrmidon.png',
      [STY, IDN('naga_myrmidon.png', 'Native shape: a muscular fair-haired man in slate-grey scale armour rising from a coiled cobalt-blue serpent tail with pale belly bands, gripping a long trident across his body.'),
       R('naga-tidewarden', 'Shipped naga tidewarden (brown-skinned, round shield, brown-grey tail): the myrmidon is fair-skinned in steel armour with a cobalt blue tail and a two-handed trident, no shield.')],
      "A naga warrior seen from a steep overhead three-quarter angle: the upper body of a muscular fair-skinned blond man in slate-grey scale armour with steel pauldrons and dark bracers, both hands gripping a long trident with a bright steel head held diagonally across the chest, rising from a thick coiled serpent tail in bright cobalt blue with a wide pale cream-white banded belly, the coil forming a clear open spiral at the base. Fierce, armoured and complete.",
      "Naga tokens: naga tidewarden (brown man, round shield, brown-grey tail), naga tidecaller (hooded dark caster), Lady Nashva (teal woman, water), Lady Zoisla (orange-red tail woman). The myrmidon is the steel-armoured fair man with a diagonal two-handed trident and a bright cobalt-blue tail with cream belly bands (silhouette: diagonal trident plus open tail spiral, no shield; hue: cobalt blue and steel grey; value: mid-light).",
      "Bright cobalt-blue tail with cream belly bands, mid slate-grey scale armour with lighter steel highlights, fair skin and blond hair, bright steel trident; nothing darker than mid tone except armour seams." + DISC,
      'READY single (naga myrmidon)', ('silhouette', 'value', 'hue'))

# ---- pack 2: elven guards and the naga nereid ----
asset(2, 'elven-guard', 'elven guard', 'rhaloren-camp, crypt-kryl-feijan and other shalore spawns (humanoid/shalore, default-name image, non-unique, no define_as)',
      [src(EW, 'name = "elven guard", color=colors.LIGHT_UMBER')], src(EW, 'define_as = "BASE_NPC_ELVEN_WARRIOR"'), None, 'humanoid', 'shalore', False, False,
      'base BASE_NPC_ELVEN_WARRIOR (humanoid/shalore, no image=); ' + DEFAULT_HUM + ' gives humanoid_shalore_elven_guard.png; crypt-kryl-feijan loads elven-warrior.lua with rarity only; the sibling "mean looking elven guard" is a separate name/image',
      'humanoid_shalore_elven_guard.png',
      [STY, IDN('humanoid_shalore_elven_guard.png', 'Native shape: an upright pale elf with pointed ears and blond hair in a forest-green tunic and trousers with a gold-embossed pauldron and belt, a big gold-rimmed kite shield on the left arm and a longsword held down at the right.'),
       R('rhaloren-inquisitor', 'Shipped Rhaloren Inquisitor (steel-plate knight with a trident): the guard wears green cloth and gold trim, not full steel plate.')],
      "A proud elven guard seen from a steep overhead three-quarter angle: an upright pale-skinned elf with pointed ears and swept blond hair, a bright forest-green tunic and trousers with brown leather belt and boots, a polished gold pauldron on the left shoulder, a large tall gold-rimmed kite shield with a gold emblem raised on the left arm, and a longsword with a bright blade held vertically upright in the right hand beside the head, a straight formal stance. Polished, disciplined and complete.",
      "Shalore tokens: Rhaloren Inquisitor (steel plate), Grand Corruptor, Kryl-Feijan acolyte (red robes), plus the elven casters and the mean looking elven guard built beside it. The elven guard is the polished one: bright forest green with gold pauldron, shield emblem and trim, upright sword raised beside the head, kite shield held high (silhouette: tall and symmetrical, sword vertical; hue: bright green and gold; value: mid-light). The mean looking guard is hunched, drab olive-brown, without gold, with the sword pointing low.",
      "Bright forest-green cloth lifted with light leaf-green planes, gold pauldron and shield rim, brown leather belt and boots, pale skin, blond hair, bright steel blade; nothing darker than mid tone except seams." + DISC,
      'READY single (elven guard)', ('silhouette', 'value', 'hue'))

asset(2, 'mean-looking-elven-guard', 'mean looking elven guard', 'rhaloren-camp, crypt-kryl-feijan and other shalore spawns (humanoid/shalore, default-name image, non-unique, no define_as)',
      [src(EW, 'name = "mean looking elven guard", color=colors.UMBER')], src(EW, 'define_as = "BASE_NPC_ELVEN_WARRIOR"'), None, 'humanoid', 'shalore', False, False,
      'base BASE_NPC_ELVEN_WARRIOR (humanoid/shalore, no image=); ' + DEFAULT_HUM + ' gives humanoid_shalore_mean_looking_elven_guard.png',
      'humanoid_shalore_mean_looking_elven_guard.png',
      [STY, IDN('humanoid_shalore_mean_looking_elven_guard.png', 'Native shape: a scarred elf with a sullen face in a drab green-brown tunic without a pauldron, a battered tall shield on the left and a sword held low at the right.'),
       R('rhaloren-inquisitor', 'Shipped Rhaloren Inquisitor (steel-plate knight): the mean guard wears drab worn cloth and leather, no plate and no gold.')],
      "A sullen scarred elven guard seen from a steep overhead three-quarter angle: a hunched, forward-leaning elf with pointed ears, tangled dirty-blond hair and a scowling face with a visible scar, a drab worn olive-brown and moss tunic with tattered edges and a dark leather harness with no gold, a battered plain wooden kite shield with a dented iron rim held low on the left arm, a longsword with a nicked blade held low pointing out and forward to the right, wide aggressive crouched stance. Grim, ragged and complete.",
      "Shalore tokens: Rhaloren Inquisitor (steel plate), Grand Corruptor, acolyte plus the polished elven guard built beside it. The mean looking guard is the hunched drab one: olive-brown and leather with a dented plain shield and the sword pointing low and forward, no gold anywhere (silhouette: crouched and asymmetric, sword pointing out low; hue: muted olive-brown and leather; value: mid). The polished guard stands upright with a raised sword and gold trim.",
      "Mid muted olive-brown and moss cloth lifted with lighter khaki planes, tan leather harness, weathered wood shield with iron rim, pale skin with a pink scar, dirty-blond hair, steel blade; nothing darker than mid tone except seams." + DISC,
      'READY single (mean looking elven guard)', ('silhouette', 'value', 'hue'))

asset(2, 'naga-nereid', 'naga nereid', 'murgol-lair and slazish-fen (humanoid/naga, non-unique, nice_tile{tall=1} shorthand with no define_as; the two zone definitions are identical in name, base and art; the tall body is the default-name humanoid_naga_naga_nereid.png)',
      [src(ML, 'name = "naga nereid", color=colors.YELLOW, resolvers.nice_tile{tall=1}'), src(SF, 'name = "naga nereid", color=colors.YELLOW, resolvers.nice_tile{tall=1}')], src(NG, 'define_as = "BASE_NPC_NAGA"'), None, 'humanoid', 'naga', False, True,
      'base BASE_NPC_NAGA (humanoid/naga, no image=); the leaf uses resolvers.nice_tile{tall=1}: with nicer tiles it resolves (resolvers.lua:1375-1385) to image=invis.png plus one add_mos {image=<default-name PNG>, display_h=2, display_y=-1}; native sprite 64x128; the identical shorthand on xhaiak/shiaak/naga tidewarden/tidecaller was live-confirmed in batches F/G to resolve to the disk filename, and Kyless (same shorthand) was live-confirmed in batch J; non-unique, so the entry is native_tall=true; single-cell path also accepted (nicer tiles off)',
      'humanoid_naga_naga_nereid.png',
      [STY, IDN('humanoid_naga_naga_nereid.png', 'Native shape (64x128 tall): a slim golden-haired woman with green eyes rising from a pale-gold coiled serpent tail with dark scaly green back, holding a staff that crackles with lilac magic sparks.'),
       R('lady-zoisla', 'Shipped Lady Zoisla (dark-haired, orange-red tail, trident): the nereid is golden-blonde with a pale gold and cream tail and a lilac-sparked staff, no trident.')],
      "A graceful naga nereid seen from a steep overhead three-quarter angle, drawn compact: a slim pale-skinned woman with long flowing golden-blonde hair and green eyes, in a light teal-green bodice, rising from a thick coiled serpent tail in pale gold with a wide cream-yellow banded belly and a dark olive-green scaly back ridge, the coil forming a low round spiral at the base, one hand raised holding a short wooden staff topped with a burst of bright lilac-violet magic sparks. Elegant, magical and complete.",
      "Naga tokens: naga tidewarden (brown man with shield), tidecaller (hooded dark), Lady Nashva (teal), Lady Zoisla (orange-red tail, dark hair, trident) and the myrmidon (cobalt tail, steel armour) built beside it. The nereid is the golden-blonde woman with a pale-gold cream tail and a raised staff bursting lilac sparks (silhouette: slim upper body, raised sparkling staff, round tail spiral; hue: pale gold with lilac accent; value: light).",
      "Light pale-gold and cream tail lifted with warm butter-yellow planes, olive-green back ridge, golden-blonde hair, light teal bodice, pale skin, bright lilac-violet spark accent; nothing darker than mid tone except the scale ridge." + DISC,
      'READY non-unique native-tall (naga nereid)', ('silhouette', 'value', 'hue'))

# ---- pack 3: elven casters, yaech diver, Kyless ----
asset(3, 'elven-mage', 'elven mage', 'mark-spellblaze, rhaloren-camp, crypt-kryl-feijan and other shalore spawns (humanoid/shalore, default-name image, non-unique). It is also placed by name in game/modules/tome/class/Game.lua:2128',
      [src(EC, 'name = "elven mage", color=colors.TEAL')], src(EC, 'define_as = "BASE_NPC_ELVEN_CASTER"'), None, 'humanoid', 'shalore', False, False,
      'base BASE_NPC_ELVEN_CASTER (humanoid/shalore, no image=); ' + DEFAULT_HUM + ' gives humanoid_shalore_elven_mage.png; talents Staff Mastery/Earthen Missiles/Shock are not sustains; no sustains_at_birth',
      'humanoid_shalore_elven_mage.png',
      [STY, IDN('humanoid_shalore_elven_mage.png', 'Native shape: a pale elf with long flowing pale hair in a dark navy robe with a gold-trimmed high collar and belt, arms hanging loosely at the sides.'),
       R('kryl-feijan-acolyte', 'Shipped Kryl-Feijan acolyte (crimson robes with a red orb): the elven mage is an indigo-violet robe with gold trim and a staff, no red.')],
      "A calm elven mage seen from a steep overhead three-quarter angle: an upright pale elf with long flowing silver-blond hair and a tall upturned gold-trimmed collar, a long robe in rich mid indigo-violet with lighter lavender highlights on the folds, gold trim at the collar cuffs and belt, one hand holding a tall slender wooden staff upright at the side topped with a small pale glowing crystal, the other hand open low. Tall, narrow, dignified and complete.",
      "Shalore tokens: Kryl-Feijan acolyte (crimson robe, red orb), Grand Corruptor (blue and red with horns), Rhaloren Inquisitor plus the elven tempest and blood mage built beside it. The elven mage is the indigo-violet robe with gold trim and a tall upright staff (silhouette: tall narrow figure with vertical staff, arms low; hue: indigo-violet with gold; value: mid). The tempest is bright sky-blue with a raised arm and lightning; the blood mage is slate grey with red stains and open dripping hands.",
      "Mid indigo-violet robe lifted with lighter lavender folds, gold trim, pale skin, silver-blond hair, light wooden staff with a pale crystal; nothing darker than mid tone except robe seams." + DISC,
      'READY single (elven mage)', ('silhouette', 'value', 'hue'))

asset(3, 'elven-tempest', 'elven tempest', 'mark-spellblaze, rhaloren-camp and other shalore spawns (humanoid/shalore, default-name image, non-unique; sustains_at_birth activates only its own Thunderstorm sustain, which changes no body field)',
      [src(EC, 'name = "elven tempest", color=colors.LIGHT_BLUE')], src(EC, 'define_as = "BASE_NPC_ELVEN_CASTER"'), None, 'humanoid', 'shalore', False, False,
      'base BASE_NPC_ELVEN_CASTER (humanoid/shalore, no image=); ' + DEFAULT_HUM + ' gives humanoid_shalore_elven_tempest.png; talents Lightning/Thunderstorm: Thunderstorm is a sustain started by sustains_at_birth but it only adds a lightning aura effect (no type/subtype/image write; the only talent in the tree that writes self.type is Flame of Urh\'Rok)',
      'humanoid_shalore_elven_tempest.png',
      [STY, IDN('humanoid_shalore_elven_tempest.png', 'Native shape: a pale elf in a bright sky-blue hooded robe crackling with electricity, one arm raised holding a spark, with pale blond hair.'),
       R('grand-corruptor', 'Shipped Grand Corruptor (blue-and-crimson robes, horned crown): the tempest is a lighter sky-blue robe with white lightning, no horns and no red.')],
      "A crackling elven tempest seen from a steep overhead three-quarter angle: a pale elf with blond hair under a bright sky-blue hood, a wide-sleeved robe in bright sky blue and pale cyan with white highlights, the right arm raised high and wide with jagged white-yellow lightning bolts arcing from the fingertips and a few sparks around the shoulders, the left hand open at the side, a wide dynamic stance. Electric, bright and complete.",
      "Shalore tokens: Grand Corruptor (deep blue and red, horned), Kryl-Feijan acolyte (crimson), Rhaloren Inquisitor plus the elven mage (indigo with a staff) and blood mage (slate with red) built beside it. The tempest is the bright sky-blue one with a wide raised arm throwing white lightning (silhouette: asymmetric with one high arm and jagged bolts; hue: bright sky blue and white; value: light).",
      "Light sky-blue and pale cyan robe with white highlights, bright white-yellow lightning, pale skin, blond hair; nothing darker than mid tone except a few robe seams." + DISC,
      'READY single (elven tempest)', ('silhouette', 'value', 'hue'))

asset(3, 'elven-blood-mage', 'elven blood mage', 'crypt-kryl-feijan, mark-spellblaze and other shalore spawns (humanoid/shalore, default-name image, non-unique; sustains_at_birth activates Blood Fury only, which changes no body field)',
      [src(EC, 'name = "elven blood mage", color=colors.ORCHID')], src(EC, 'define_as = "BASE_NPC_ELVEN_CASTER"'), None, 'humanoid', 'shalore', False, False,
      'base BASE_NPC_ELVEN_CASTER (humanoid/shalore, no image=); ' + DEFAULT_HUM + ' gives humanoid_shalore_elven_blood_mage.png; talents Drain/Blood Spray/Blood Grasp/Blood Boil/Blood Fury: none writes type/subtype/image (only Flame of Urh\'Rok does, and the blood mage does not know it)',
      'humanoid_shalore_elven_blood_mage.png',
      [STY, IDN('humanoid_shalore_elven_blood_mage.png', 'Native shape: a pale elf in a dark navy-blue hooded robe splattered with red blood stains, arms hanging at the sides, blond hair.'),
       R('kryl-feijan-acolyte', 'Shipped Kryl-Feijan acolyte (crimson robes, red orb held up): the blood mage is a slate-blue-grey robe with red stains and open dripping hands, no red robe and no orb.')],
      "A grim elven blood mage seen from a steep overhead three-quarter angle: a pale elf with blond hair under a slate blue-grey hood, a long robe in mid slate blue-grey with lighter steel-blue folds and bold bright crimson blood splatters and a wet crimson hem, both hands held open in front at hip height dripping bright red blood in a few droplets that stay near the hands, a hunched menacing lean forward. Sinister and complete.",
      "Shalore tokens: Kryl-Feijan acolyte (crimson robe, red orb held up), Grand Corruptor (blue with red, horned), Rhaloren Inquisitor plus the elven mage (indigo, staff) and tempest (sky-blue, lightning) built beside it. The blood mage is the slate blue-grey robe with bright red splatters, hunched forward with open dripping hands (silhouette: hunched with two low forward hands; hue: slate steel-blue with crimson accents; value: mid). Never a red robe, never a raised orb.",
      "Mid slate blue-grey robe lifted with lighter steel-blue folds, bright crimson blood accents, pale skin, blond hair; nothing darker than mid tone except robe seams." + DISC,
      'READY single (elven blood mage)', ('silhouette', 'value', 'hue'))

asset(3, 'yaech-diver', 'yaech diver', 'murgol-lair and other yaech spawns (humanoid/yaech, default-name image, non-unique; murgol-lair loads yaech.lua with a damage-reduction callback only)',
      [src(YA, 'name = "yaech diver", color=colors.BLUE')], src(YA, 'define_as = "BASE_NPC_YAECH"'), None, 'humanoid', 'yaech', False, False,
      'base BASE_NPC_YAECH (humanoid/yaech, no image=); ' + DEFAULT_HUM + ' gives humanoid_yaech_yaech_diver.png; murgol-lair callback only sets inc_damage.all; the sibling yaech hunter and the shipped Murgol are other names',
      'humanoid_yaech_yaech_diver.png',
      [STY, IDN('humanoid_yaech_yaech_diver.png', 'Native shape: a small pale blue-white furry creature with big dark eyes swimming on all fours with tiny bubbles trailing behind.'),
       R('murgol', 'Shipped Murgol (spiky grey-blue armoured yaech lord with a trident): the diver is a small soft furry pale swimmer on all fours, no armour and no spikes.')],
      "A small furry yaech diver seen from a steep overhead three-quarter angle: a round soft pale blue-white fluffy body swimming forward on all fours, a big round head with large dark glossy eyes with white glints and a small mournful face, tiny hands and feet with pale pink pads stretched out, a short stubby tail, a trail of a few small clear bubbles rising around the back. Soft, small and complete.",
      "Yaech tokens: Murgol the Yaech Lord (spiky armoured grey-blue with a trident). The diver is the small fluffy pale swimmer on all fours with big dark eyes and bubbles (silhouette: round fluffy body with four stretched limbs and bubbles; hue: pale ice-blue and white; value: light). It must not look armoured or spiky.",
      "Light pale ice-blue and white fluffy fur with soft blue-grey shading, pale pink pads, big dark eyes with white glints, clear pale bubbles; nothing darker than mid tone except the eyes." + DISC,
      'READY single (yaech diver)', ('silhouette', 'value', 'hue'))

asset(2, 'kyless', 'Kyless', 'keepsake-meadow (humanoid/human, define_as KYLESS, unique, nice_tile{tall=1} shorthand with no image= anywhere; live-confirmed in the batch J census to be image=invis.png with a single add_mos {image=npc/humanoid_human_kyless.png, display_h=2, display_y=-1}; native sprite 64x128)',
      [src(KM, 'define_as="KYLESS"')], None, 'KYLESS', 'humanoid', 'human', True, False,
      'no base; unique with define_as KYLESS, type humanoid/subtype human, no image=; resolvers.nice_tile{tall=1} (resolvers.lua:1375-1385) expands with nicer tiles to invis.png + add_mos {image=<default-name PNG>, display_h=2, display_y=-1}. The earlier static doubt (image nil at resolve time) was disproved by the batch J live census (evidence/monster-batch-j-live-20260929/census.json, keepsake-meadow-L6: image invis.png, add_mos[1].image npc/humanoid_human_kyless.png, display_h 2, display_y -1, no aura entry, moddable_tile false), the same shorthand that batches F/G confirmed for xhaiak/shiaak. Talents (Willful Strike, Deflection, Blast, Unseen Force, Feed, Devour Life, Feed Power, Feed Strengths, Creeping Darkness, Dark Vision, Dark Tendrils) and sustains_at_birth never write type/subtype/image; never_act and seen_by do not touch display. Unique catalog entries accept the tall path and the single-cell path',
      'humanoid_human_kyless.png',
      [STY, IDN('humanoid_human_kyless.png', 'Native shape (64x128 tall): a dark-haired man in an olive-green tunic and brown boots and leather wrist-wraps, holding a curled spiral object at his belly, wreathed in curling black smoke tendrils.'),
       R('the-possessed', 'Shipped The Possessed (human unique, tall): Kyless is an ordinary olive-tunic man wreathed in smoky violet-grey tendrils, not a possessed robed figure.')],
      "A haunted human man seen from a steep overhead three-quarter angle, drawn compact: a lean dark-haired man with a weary corrupted face and glinting pale eyes, in a mid olive-green tunic with a tan leather belt and brown boots and wrist-wraps, holding a curled spiral horn against his belly with both hands, wreathed by several thick curling tendrils of smoky violet-grey shadow that coil up around his shoulders and arms and stay close to his body. Uneasy, sinister and complete.",
      "Human unique tokens: Subject Z, The Possessed, Harno, Assassin Lord, Ben Cruthdar. Kyless is the olive-tunic man with a spiral horn in a corona of smoky violet-grey tendrils (silhouette: narrow figure with curling tendrils around shoulders; hue: olive green with violet-grey smoke; value: mid, the smoke lighter than charcoal).",
      "Mid olive-green tunic lifted with lighter moss planes, tan leather, brown boots, warm skin, smoky mid violet-grey tendrils with lighter edges that stay clearly lighter than the disc; nothing darker than mid tone except the hair and seams." + DISC,
      'READY unique native-tall (Kyless)', ('silhouette', 'value', 'hue'))


def retry(id_, pack, **changes):
    base = next(a for a in A if a['id'] == id_)
    A.append(dict(base, pack=pack, **changes))


# ---- retry packs are appended below by later edits ----
exec((HERE / 'retries.py').read_text()) if (HERE / 'retries.py').exists() else None


def build():
    packs = {}
    identities = []
    render = 'game/addons/tome-checker-revised/evidence/monster-batch-l-20260929/source-contracts.json'
    seen = set()
    for a in A:
        if a['id'] in seen:
            continue
        seen.add(a['id'])
        native_rel = NPC + a['native']
        ident = {'id': a['id'], 'native_name': a['name'], 'source': a['srcs'][0], 'define_as': a['define_as'],
                 'type': a['type'], 'subtype': a['subtype'], 'unique': a['unique'], 'native_tall': a['native_tall'],
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
          'task': 'monster-batch-l: static re-verification (no game launch) of the twelve batch-3 identities of the second gap survey (orc warrior, elven guard, naga myrmidon, mean looking elven guard, orc soldier, naga nereid, elven mage, elven tempest, yaech diver, orc archer, elven cultist, elven blood mage) plus Kyless (kept native in batch J on a static guess, disproved by its live census) against game/modules/tome source and native sprites. Survey verdicts were not trusted; every field below was read from source.',
          'new_ids_not_in_catalog_before_this_batch': [i['id'] for i in identities], 'identities': identities,
          'runtime_mutation_scan': {
              'method': 'grep of game/modules/tome/data/talents and timed_effects for writes to self.type/subtype/image, __old_type, replace_display, add_mos, moddable_tile; every talent of each identity (resolvers.talents and inherited base talents) was checked against the hits',
              'writers_found': [
                  {'file': 'game/modules/tome/data/talents/corruptions/shadowflame.lua', 'line': 96, 'talent': "Flame of Urh'Rok", 'effect': 'sustain: __old_type={type,subtype}; type,subtype = demon,major; image untouched'},
                  {'file': 'game/modules/tome/data/talents/chronomancy/anomalies.lua', 'line': 587, 'talent': 'chronomancy anomaly (random human/halfling/shalore/dwarf civilians)', 'effect': 'writes m.name/m.subtype/m.image on a freshly made summon, not on any identity of this batch'},
                  {'file': 'game/modules/tome/data/talents/psionic/thought-forms.lua', 'line': 92, 'talent': 'Thought-Forms', 'effect': 'player summons only'}],
              'hits_in_batch': [{'identity': 'elven cultist', 'talent': "T_FLAME_OF_URH_ROK (base=3) plus resolvers.sustains_at_birth()", 'consequence': 'the sustain can flip the cultist to demon/major at birth (sustains_at_birth, resolvers.lua:842-857), exactly the Grand Corruptor case fixed in a3a0225 via the opt-in urh_rok_form flag. No live check of the cultist exists, so it stays native in this batch instead of inventing or extending a rule. Adding urh_rok_form=true to a catalog entry later would cover it with the existing tests.'}],
              'no_hit': ['orc warrior', 'orc soldier', 'orc archer', 'elven guard', 'mean looking elven guard', 'naga myrmidon', 'naga nereid', 'elven mage', 'elven tempest', 'yaech diver', 'elven blood mage', 'Kyless']},
          'name_collisions_checked': [
              {'name': 'orc warrior', 'other_definitions': ['zones/charred-scar/npcs.lua ORC_ATTACK (humanoid/orc, define_as ORC_ATTACK, base BASE_NPC_ORC_ATTACKER, default-name image humanoid_orc_orc_warrior.png)'],
               'outcome': 'catalog entry requires define_as HILL_ORC_WARRIOR: the Charred Scar attacker is rejected by exactIdentity (define_as mismatch, negative test added) and stays native; no name+define_as key extension'},
              {'name': 'orc soldier / orc archer', 'other_definitions': ['class/generator/actor/Arena.lua and general/npcs/orc.lua group spawns refer to the names only (entity filters, not definitions)', 'maps/vaults/grushnak-armory.lua random_boss archer renames the actor'],
               'outcome': 'single definitions; define_as ORC / HILL_ORC_ARCHER bound in the catalog'},
              {'name': 'naga nereid', 'other_definitions': ['zones/murgol-lair/npcs.lua and zones/slazish-fen/npcs.lua both define it, identical in base, tall=1 shorthand and art (only life_rating/auto_equip_filters differ)'],
               'outcome': 'one identity, one catalog entry (native_tall=true)'},
              {'name': 'naga myrmidon', 'other_definitions': ['class/generator/actor/Arena.lua entity filter by name; birth Birther lists npc/naga_myrmidon_2.png and _no_armor.png as race previews only'], 'outcome': 'single NPC definition with explicit image npc/naga_myrmidon.png'},
              {'name': 'elven guard / mean looking elven guard / elven mage / elven tempest / elven blood mage / yaech diver / Kyless', 'other_definitions': ['class/Game.lua:2128 places an elven mage by name from the normal npc list'], 'outcome': 'single definitions in the native tree; no addon redefinition found'}],
          'kept_native': [{'name': 'elven cultist', 'type': 'humanoid', 'subtype': 'shalore', 'source': src(EC, 'name = "elven cultist", color=colors.DARK_SEA_GREEN'),
                           'native_image': 'npc/humanoid_shalore_elven_cultist.png',
                           'reason': "knows T_FLAME_OF_URH_ROK and carries resolvers.sustains_at_birth(): the sustain (shadowflame.lua:96-97) may turn it into demon/major at birth, so its runtime type is unverified and the exactIdentity type check could reject it; no live check exists and the task forbids inventing a rule. The existing urh_rok_form flag would cover it if a later live check confirms the form."}]}
    out = ADDON / 'evidence/monster-batch-l-20260929/source-contracts.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(ev, indent=2, ensure_ascii=False) + '\n')
    evsha = hashlib.sha256(out.read_bytes()).hexdigest()
    for a in A:
        refs = [{'path': p, 'sha256': sha(p), 'role': r, 'note': n} for r, p, n in a['refs']]
        entry = {'asset_id': a['id'], 'native_name': a['name'], 'scope': a['scope'], 'sources': a['srcs'], 'references': refs,
                 'contrast_dimensions': list(a['dims']),
                 'prompt_fields': {'subject': a['subject'], 'contrast': a['contrast'], 'composition': a['comp'] or COMP, 'palette': a['palette']},
                 'kind': 'creature', 'max_attempts': 1, 'gate': 'ready',
                 'gate_reason': f"Exact source identity re-verified directly against game/modules/tome source (name={a['name']}, define_as={a['define_as']}, type={a['type']}/subtype={a['subtype']}, unique={a['unique']}); details and hashes in evidence/monster-batch-l-20260929/source-contracts.json. {a['structure']}. Exact catalog entry only, never a whole-subtype mapping.",
                 'render_evidence': [{'path': render, 'sha256': evsha}]}
        packs.setdefault(a['pack'], []).append(entry)
    for n, assets in packs.items():
        p = ADDON / f'art/production/batches/monster-batch-l-{n}.json'
        if p.exists():
            print('exists, skipped', p.name)
            continue
        p.write_text(json.dumps({'schema': 1, 'batch_id': f'monster-batch-l-{n}', 'assets': assets}, indent=2, ensure_ascii=False) + '\n')
        print('wrote', p.name)


if __name__ == '__main__':
    build()
