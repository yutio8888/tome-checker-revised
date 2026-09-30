"""Generate the monster-batch-z task packs and the pinned source-contract
evidence (survey-2 unscheduled list after batch Y: black mamba, bandit lord,
rogue sapper, orb weaver, elven elite warrior, fire wyrm, runed bone giant,
ultimate telugoroth, greater teluvorta, void horror, swarming horror, ravenous
horror; see SELECTION.md). Pure bookkeeping: hashes native sources/sprites,
writes JSON and the composite family references. Retry packs are appended by
later edits of retries.py (never overwritten)."""
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
ART_REL = 'game/addons/tome-checker-revised/art/monster-batch-z/'
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





REF_SNAKES = RC('snakes', ['brown-snake', 'king-cobra', 'white-snake', 'rattlesnake', 'copperhead-snake'], 3,
                'Five shipped snake tokens (tan-brown patterned coil, olive-green hooded king cobra, cream-white snake, tan diamond-back rattlesnake, coppery-salmon copperhead): the black mamba is a long sleek cool STEEL-BLUE and slate-grey glossy snake with no pattern, no hood and no rattle, a few smooth loops with the front third raised in an S-curve and a pale silvery belly, a yellow eye and a pink-red tongue; not brown, not green, not white, not patterned.')
REF_THIEVES = RC('thieves', ['bandit', 'thief', 'rogue', 'assassin', 'cutpurse'], 3,
                 'Five shipped human thief tokens (bald brawny bandit with two knives and an orange belt, dark-cloaked thief, blue-hooded rogue with a dagger, blue-grey hooded assassin with a white scarf and twin knives, cutpurse in a tan vest): the bandit lord is a BEARDED, long-haired, bare-chested brawny man with arms crossed, crimson baggy trousers, a gold sash and gold armbands, a sheathed curved sabre at the hip, no drawn knives, not bald and not hooded; the rogue sapper is a crouched goggled trapper in DUN KHAKI and olive-brown cloth with a bandolier of brass spring-traps, a satchel of trap parts and a small spiked steel trap held in one hand, not blue-grey and not white-scarfed.')
REF_SPIDERS = RC('spiders', ['weaver-hatchling', 'weaver-young', 'weaver-queen', 'weaver-patriarch', 'giant-spider', 'spitting-spider'], 3,
                 'Six shipped spider tokens (small blue-white striped weaver hatchling, blue swirl weaver young, cream-and-gold weaver queen, the deep cobalt weaver patriarch with a white chevron and gold echoes, grey giant spider, brown spitting spider): the orb weaver is a PALE FROST-BLUE and white spider with a big round abdomen patterned in CONCENTRIC silver rings like an orb web, a small head with glinting eyes and eight long thin banded legs splayed wide, with fine white silk strands; not deep cobalt, not chevron-marked, not grey and not a small swirl ball.')
REF_ELVES = RC('elves', ['elven-warrior', 'elven-guard', 'elven-corruptor', 'elven-mage'], 2,
               'Four shipped elf tokens (the elven warrior in light white-and-gold plate with a polearm axe and a round shield, the green-clad elven guard with a sword and shield, the pink-robed corruptor, the blue-robed mage): the elven elite warrior is a visibly BULKIER full-heavy-plate elf in deep burnished BRONZE-GOLD with teal-blue enamel trim, a winged crested helm with a white plume, huge upswept pauldron spikes, a huge kite tower shield with a teal sunburst and a big double-bladed waraxe, with a short teal cape; not slim white-and-gold, not green and not robed.')
REF_TELUGOROTH = RC('telugoroth', ['telugoroth', 'greater-telugoroth', 'teluvorta', 'temporal-stalker'], 2,
                    'Four shipped temporal tokens (the telugoroth: a flat round rainbow swirl; the greater telugoroth: a slim gold-orange twisting flame column; the teluvorta: a spiky violet crystal-urchin ball; the chrome temporal stalker): the ultimate telugoroth is a colossal TIME STORM shaped like an EIGHT-POINTED STARBURST, a blazing white-gold core with eight-to-twelve sharp radiating golden sand-blade spokes and ribbons of amber, sapphire and violet sand between them; the greater teluvorta is a smooth billowing dark-violet STORM-CLOUD crowned by a ring of six long curved ivory-lilac horns with a comet-tail wake of cream dust and hourglass shards. Neither may be a flat rainbow swirl, a slim flame column or a spiky crystal ball.')
REF_GIANTS = RC('giants', ['bone-giant', 'heavy-bone-giant', 'eternal-bone-giant', 'atamathon'], 2,
                'Four shipped giant tokens (plain tan bone giant, golden plated heavy bone giant, pale eternal bone giant with a lilac halo, white-grey metal Atamathon): the runed bone giant is a hunched giant of AGED CREAM-TAN bones whose every big bone plate is carved with bright glowing CRIMSON RUNE glyphs, with glowing crimson eye pits, one arm raised casting with a ring of six floating red glyphs around it and a faint rose aura; not plain tan, not golden, not lilac-haloed and not metal.')
REF_VOIDS = RC('voids', ['dredgling', 'dredge', 'temporal-stalker', 'dread', 'shadow-stalker', 'ink-squid'], 3,
               'Six shipped horror tokens (pink dredgling, dredge, chrome temporal stalker, slate-violet dread wraith, dark shadow stalker, violet ink squid): the void horror is a vertical LENS-SHAPED TEAR in spacetime, an eye-like pointed oval with a thick luminous silver-white border, a mid-indigo starfield inside with a bright four-point star-flare and a violet nebula swirl, and ringed by floating silver glass-like space shards; not a creature body, not smoke and not a wraith.')
REF_AQUA = RC('aquatic', ['ink-squid', 'squid', 'giant-eel', 'electric-eel', 'naga-tide-huntress'], 3,
              'Five shipped water-creature tokens (violet ink squid, squid, giant eel, electric eel, naga tide huntress): the swarming horror is a loose SCHOOL of eight small silvery-teal fish-like horrors with big pale glowing eyes and needle-toothed mouths swirling in a ring, many small bodies; the ravenous horror is ONE fat fanged slate-blue predator with a huge gaping needle-toothed mouth dripping lime-yellow acid, a cluster of round pale eyes and a huge fan of bone-white spined fins; not a squid, not an eel, not violet.')
REF_DRAGONS = RC('dragons', ['fire-drake', 'fire-drake-hatchling', 'cold-drake', 'sand-drake', 'venom-drake', 'storm-drake'], 3,
                 'Six shipped drake tokens (the orange fire drake crouched with wings fully spread and a fire cone, its small hatchling, and the cold, sand, venom and storm drakes): the fire wyrm is an ancient, bulkier, deep SCARLET-CRIMSON serpentine dragon coiled in an S with its long neck reared and jaws open showing a glowing gold throat, a crown of long swept-back horns, a spiny back ridge, pale cream belly plates and ragged half-folded wings with bone-ivory spines, and no flame cone; not orange, not a crouching four-legged winged silhouette with a fire cone.')

MOD = ' no moddable_tile, shader, anim or add_displays on the leaf or base; native sprite 64x64; non-unique'
TALLB = ' no moddable_tile, shader, anim or add_displays; native sprite 64x128; non-unique'
CATS = ' Draw the whole creature as ONE compact upright figure filling the disc; never a tall canvas.'
SWARMS = ' Draw the whole swarm as ONE compact loose ring of bodies filling the inner three quarters of the disc; never a tall canvas.'
THIEFD = ' resolvers.racial() only adds human levelup talents (Higher Heal, Born into Magic, Highborn\'s Bloom: passives, no display write) and the base calls resolvers.sustains_at_birth() (Stealth and Total Thuggery are sustains: temporary values only); resolvers.equip daggers and light armour (equipment only, no moddable_tile)'

SNAK = 'general/npcs/snake.lua'
THEF = 'general/npcs/thieve.lua'
MORS = 'zones/unhallowed-morass/npcs.lua'
SPID = 'general/npcs/spider.lua'
ELFW = 'general/npcs/elven-warrior.lua'
TELU = 'general/npcs/telugoroth.lua'
HAQU = 'general/npcs/horror_aquatic.lua'
HTMP = 'general/npcs/horror_temporal.lua'
BONE = 'general/npcs/bone-giant.lua'
FDRK = 'general/npcs/fire-drake.lua'

# ---- pack 1: black mamba, bandit lord, rogue sapper, orb weaver ----
asset(1, 'black-mamba', 'black mamba',
      "noxious-caldera, unremarkable-cave and lake-nur pools (general/npcs/snake.lua:102, animal/snake, non-unique, no define_as, rank 2, base BASE_NPC_SNAKE, explicit image=npc/darkgrey-snake.png); the only definition of this name",
      [src(SNAK, 'name = "black mamba"'), src(SNAK, 'image="npc/darkgrey-snake.png"', after='name = "black mamba"'), src(SNAK, 'T_BITE_POISON', after='name = "black mamba"'), src(SNAK, 'define_as = "BASE_NPC_SNAKE"')],
      src(SNAK, 'define_as = "BASE_NPC_SNAKE"'), None, 'animal', 'snake', False, False,
      'base BASE_NPC_SNAKE (animal/snake, no image=, no shader, no sustains_at_birth);' + EXPL + '; the same PNG is used by no other leaf (darkgrey-snake.png); the only talent is Bite Poison (activated); ingredient_on_death only names a drop; no equip, no sustains_at_birth, no auto_classes',
      'darkgrey-snake.png',
      [STY, IDN('darkgrey-snake.png', 'Native shape (64x64): a glossy near-black indigo snake in a few loops with its head raised in an S-curve, a yellow eye and a flicking red-pink tongue. Keep the sleek raised-head snake with the yellow eye and red tongue, but render the scales in mid-light steel-blue and slate with bright silver-blue highlight bands, a pale silvery belly and a thin bright rim light.'), REF_SNAKES],
      "A black mamba seen from a steep overhead three-quarter angle: a long SLEEK snake lying in a few smooth loops on the disc with the front third of its body rearing up in a graceful S-curve, the head raised and turned to the lower left with the jaw slightly open showing a pale pink mouth and two small white fangs and a flicking RED-PINK forked tongue, one bright YELLOW eye, the skin smooth glossy STEEL-BLUE and cool SLATE-GREY in a mid-light value with fine small scales and bright pale silver-blue highlight bands along the upper-left curve of every loop, a pale SILVERY-LAVENDER belly visible along the throat and under the jaw, a thin bright pale rim light along the whole outline. Sleek, glossy, coiled and complete.",
      "Snakes: the BLACK MAMBA is the SLEEK STEEL-BLUE AND SLATE SNAKE, plain and patternless, in smooth loops with the front raised in an S-curve, a yellow eye and a red tongue (silhouette: a few smooth loops with a raised S neck, no hood; hue: cool steel-blue and slate with silver highlights, pink-red tongue, yellow eye; value: mid-light). The shipped large brown snake is a tan-brown coil, the king cobra an olive-green hooded snake, the white snake cream, the rattlesnake a tan patterned diamond-back with a rattle, the copperhead coppery salmon: this must not be brown, green, white, patterned, hooded or rattle-tailed.",
      "Steel-blue and cool slate scales in a mid-light value with bright silver-blue highlight bands, a pale silvery-lavender belly, yellow eye, pink-red tongue and a bright pale rim light; nothing darker than mid slate-blue except the eye pupil; NO black or near-black body anywhere." + DISC,
      "READY single, no define_as (black mamba)", comp=COMP + FIT + COMPACT + BRIGHT + DARKFIX)

asset(1, 'bandit-lord', 'bandit lord',
      "maze pool, thieves-tunnels (rare) and the bandit-fortress zone and vault (general/npcs/thieve.lua:112, humanoid/human, non-unique, no define_as, rank 2, base BASE_NPC_THIEF, default-name image); the only definition of this name",
      [src(THEF, 'name = "bandit lord"'), src(THEF, 'T_TOTAL_THUGGERY', after='name = "bandit lord"'), src(THEF, 'T_SUMMON', after='name = "bandit lord"'), src(THEF, 'resolvers.racial()'), src(THEF, 'resolvers.sustains_at_birth()'), src(THEF, 'define_as = "BASE_NPC_THIEF"')],
      src(THEF, 'define_as = "BASE_NPC_THIEF"'), None, 'humanoid', 'human', False, False,
      'base BASE_NPC_THIEF (humanoid/human, no image=, no shader);' + DEF + ';' + THIEFD + '; the leaf itself has no sustains_at_birth of its own and no auto_classes; Summon calls the bandit, thief and rogue leaves (each wears its own token)',
      'humanoid_human_bandit_lord.png',
      [STY, IDN('humanoid_human_bandit_lord.png', 'Native shape (64x64): a bare-chested, bearded, dark-haired brawny man standing with his arms crossed over his chest, baggy crimson trousers, barefoot. Keep the bare-chested bearded brawny man with crossed arms and crimson trousers, adding a gold sash, gold armbands and a sheathed sabre so that he reads as the gang leader.'), REF_THIEVES],
      "A bandit lord seen from a steep overhead three-quarter angle: a BROAD brawny bare-chested man standing square and facing the lower left with his ARMS CROSSED over his chest, a full dark-brown BEARD and long dark wind-tossed hair, warm tan skin with light highlight planes on the shoulders, baggy CRIMSON-RED trousers gathered at the ankle, a wide GOLD-YELLOW SASH at the waist with a sheathed curved SABRE hanging at the hip, thick GOLD ARMBANDS on both biceps and a heavy gold chain on the chest, bare feet planted apart, a confident smirk. Brawny, bearded, gold-sashed and complete.",
      "Human thieves: the BANDIT LORD is the BEARDED LONG-HAIRED BARE-CHESTED BRAWNY MAN with arms crossed, crimson trousers and gold sash and armbands (silhouette: a broad standing man with folded arms and a hip sabre, no weapon drawn; hue: warm tan skin, dark brown hair and beard, crimson trousers, gold accents; value: mid-light). The shipped bandit is a bald brawler with two knives and an orange belt, the thief and rogue are hooded and cloaked, the assassin blue-grey hooded, the cutpurse a tan-vested skinny man: this must not be bald, not holding knives, not hooded and not cloaked.",
      "Warm tan skin with light highlight planes, dark brown hair and beard, bright crimson trousers, gold sash, armbands and chain (kept on the man), a steel sabre hilt; nothing darker than deep brown except the eyes and thin seams; the disc stays neutral charcoal at reference lightness." + DISC,
      "READY single, no define_as (bandit lord)", comp=COMP + FIT + COMPACT + BRIGHT)

asset(1, 'rogue-sapper', 'rogue sapper',
      "maze pool, thieves-tunnels (rare), the bandit-fortress zone and the bandit-fortress and thief-hideout vaults (general/npcs/thieve.lua:190, humanoid/human, non-unique, define_as THIEF_SAPPER, rank 2, base BASE_NPC_THIEF, explicit image=npc/humanoid_human_assassin.png); the only definition of this name",
      [src(THEF, 'name = "rogue sapper"'), src(THEF, 'image = "npc/humanoid_human_assassin.png"', after='name = "rogue sapper"'), src(THEF, 'define_as = "THIEF_SAPPER"'), src(THEF, 'T_TRAP_MASTERY', after='name = "rogue sapper"'), src(THEF, 'resolvers.racial()'), src(THEF, 'define_as = "BASE_NPC_THIEF"')],
      src(THEF, 'define_as = "BASE_NPC_THIEF"'), 'THIEF_SAPPER', 'humanoid', 'human', False, False,
      'base BASE_NPC_THIEF (humanoid/human, no image=, no shader);' + EXPL + ';' + THIEFD + '; the leaf binds define_as THIEF_SAPPER and calls resolvers.sustains_at_birth() (Stealth is the only sustain: temporary values only); Trap Mastery, Trap Priming, Dual Strike and Disarm are activated, the rest passive; the explicit image is the assassin\'s PNG (humanoid_human_assassin.png), which the assassin catalog entry also names, but the two are told apart by name and define_as (THIEF_ASSASSIN vs THIEF_SAPPER)',
      'humanoid_human_assassin.png',
      [STY, IDN('humanoid_human_assassin.png', 'Native shape (64x64; the leaf reuses the assassin PNG): a crouching black-clad hooded and masked figure with a curved dagger held low. Keep a crouched hooded, masked, low-slung rogue, but this token must NOT be the shipped assassin: render a goggled trapper in dun khaki and olive-brown cloth with a bandolier of brass spring-traps, a trap satchel and a small spiked steel trap in one hand.'), REF_THIEVES],
      "A rogue sapper seen from a steep overhead three-quarter angle: a CROUCHED sneaking rogue facing the lower left, a pulled-up hood and face wrap in light DUN KHAKI and OLIVE-BROWN cloth in a mid-light value with pale highlight planes on the upper-left folds, round BRASS-RIMMED GOGGLES with amber lenses pushed on the forehead, a diagonal BANDOLIER across the chest studded with small polished BRASS SPRING-TRAPS and coiled steel wire, a bulging leather SATCHEL of trap parts on the hip with a few protruding spikes, one gloved hand holding a small toothed STEEL BEAR-TRAP up close to the body and the other hand a short curved dagger held low, tan leather boots; no props on the ground. Crouched, goggled, trap-laden and complete.",
      "Human thieves: the ROGUE SAPPER is the CROUCHED GOGGLED TRAPPER in DUN KHAKI AND OLIVE-BROWN cloth with a bandolier of brass spring-traps, a satchel and a steel bear-trap in hand (silhouette: a hunched hooded figure with a bulky satchel and a trap held up; hue: khaki, olive-brown, brass and steel with amber goggles; value: mid-light). The shipped assassin is a blue-grey hooded figure with a white scarf and twin knives, the rogue blue-hooded, the thief dark-cloaked, the bandit a bald brawler: this must not be blue-grey, not white-scarfed, not black and must show the traps.",
      "Dun khaki and olive-brown cloth in a mid-light value with pale highlight planes and a bright rim light, polished brass and steel trap parts, amber goggle lenses; nothing darker than deep olive-brown except thin seams and the eye shadow; NO black cloth or black leather anywhere; the disc stays neutral charcoal at reference lightness." + DISC,
      "READY single, define_as THIEF_SAPPER (rogue sapper)", comp=COMP + FIT + COMPACT + BRIGHT + DARKFIX)

asset(1, 'orb-weaver', 'orb weaver',
      "unhallowed-morass pool and the orb spinner's escort (zones/unhallowed-morass/npcs.lua:73, spiderkin/spider, non-unique, no define_as, rank 1, base BASE_NPC_SPIDER, default-name image); the only definition of this name",
      [src(MORS, 'name = "orb weaver"'), src(MORS, 'T_LAY_WEB', after='name = "orb weaver"'), src(SPID, 'resolvers.sustains_at_birth()', after='define_as = "BASE_NPC_SPIDER"'), src(SPID, 'define_as = "BASE_NPC_SPIDER"')],
      src(SPID, 'define_as = "BASE_NPC_SPIDER"'), None, 'spiderkin', 'spider', False, False,
      'base BASE_NPC_SPIDER (spiderkin/spider, no image=, no shader);' + DEF + '; the base resolvers.sustains_at_birth() has no sustained talent to start here (Lay Web and Spider Web are activated, Spin Fate is not learned by this leaf); two base infusion inscriptions (an invisibility infusion would apply a shader-based effect only while active, and the matcher rejects it then); no equip, no auto_classes; the orb spinner and Weaver Queen escorts build this same leaf',
      'spiderkin_spider_orb_weaver.png',
      [STY, IDN('spiderkin_spider_orb_weaver.png', 'Native shape (64x64): a big frost-blue and white spider with translucent pale legs and a bulky rounded body, seen from the front. Keep the big pale frosty spider, and give it a round orb-web abdomen patterned in concentric silver rings, pale frost-blue and white, long thin banded legs.'), REF_SPIDERS],
      "An orb weaver seen from a steep overhead three-quarter angle: a large spider facing the lower left with a big round BULBOUS ABDOMEN in pale FROST-BLUE and white in a light value, marked with bold CONCENTRIC CIRCULAR RINGS of silver and pale sky-blue like a spun orb web with a bright white centre spot, a smaller pale-blue head-thorax with several glinting pale eyes and small fangs, eight long thin LEGS banded in pale ice-blue and steel-blue and splayed wide (every leg tip inside the disc), a few fine white SILK STRANDS trailing from the spinnerets and curling close to the body, a bright pale rim light along the outline. Pale, ringed, long-legged and complete.",
      "Spiders: the ORB WEAVER is the PALE FROST-BLUE SPIDER with a big round abdomen of concentric silver rings and long thin banded legs (silhouette: a round ringed abdomen behind a small head with eight long thin legs splayed wide; hue: pale frost-blue, white and silver; value: light). The shipped weaver patriarch is a deep cobalt-sapphire spider with a white chevron and golden echoes, the weaver hatchling and young are small blue-white swirl balls, the weaver queen cream and gold, the giant spider grey and the spitting spider brown: this must not be deep blue, not chevron-marked, not a small swirl ball, not cream and not grey.",
      "Pale frost-blue, white and silver in a light value with steel-blue leg bands and a bright rim light, faint white silk; nothing darker than mid steel-blue except the eye pits and thin seams; NO black chitin; the disc stays neutral charcoal at reference lightness." + DISC,
      "READY single, no define_as (orb weaver)", comp=COMP + FIT + COMPACT + BRIGHT)

# ---- pack 2: elven elite warrior, fire wyrm, runed bone giant ----
asset(2, 'elven-elite-warrior', 'elven elite warrior',
      "crypt-kryl-feijan pool (general/npcs/elven-warrior.lua:97, humanoid/shalore, non-unique, no define_as, rank 3, base BASE_NPC_ELVEN_WARRIOR, default-name image); the only definition of this name (the plain elven warrior is another leaf with its own token)",
      [src(ELFW, 'name = "elven elite warrior"'), src(ELFW, 'T_ASSAULT', after='name = "elven elite warrior"'), src(ELFW, 'resolvers.racial()'), src(ELFW, 'define_as = "BASE_NPC_ELVEN_WARRIOR"')],
      src(ELFW, 'define_as = "BASE_NPC_ELVEN_WARRIOR"'), None, 'humanoid', 'shalore', False, False,
      'base BASE_NPC_ELVEN_WARRIOR (humanoid/shalore, no image=, no shader, no moddable_tile);' + DEF + '; resolvers.equip waraxe, shield, heavy armour (equipment only, no moddable_tile); Shield Pummel and Assault are activated; resolvers.racial() adds shalore racial levelup talents only (Secrets of the Eternals is sustained but only learnt by level-up: neither the base nor the leaf has sustains_at_birth); no auto_classes',
      'humanoid_shalore_elven_elite_warrior.png',
      [STY, IDN('humanoid_shalore_elven_elite_warrior.png', 'Native shape (64x64): an elf in heavy golden-bronze plate armour with a horned winged helm, a tall oval shield and a long-hafted polearm axe. Keep the elf in heavy bronze-gold plate with a winged crested helm, a big shield and a long-hafted axe, but make him visibly bulkier and more ornate than the shipped elven warrior.'), REF_ELVES],
      "An elven elite warrior seen from a steep overhead three-quarter angle: a tall proud elf in full HEAVY PLATE of deep burnished BRONZE-GOLD with bright polished highlight planes and TEAL-BLUE enamel trim along every edge, a WINGED CRESTED HELM with two long swept-back wing-crests and a white horsehair plume, broad flared PAULDRONS with short upswept spikes, a large KITE TOWER SHIELD in bronze with a teal sunburst held forward on the left arm, a big DOUBLE-BLADED WARAXE with a long haft held raised in the right hand (the blades inside the disc), a short TEAL CAPE flaring behind, fair elven face with a stern look. Gleaming, heavy, crested and complete.",
      "Elves: the ELVEN ELITE WARRIOR is the BULKY FULL-PLATE ELF in deep burnished bronze-gold with teal trim, a winged crested helm with a white plume, upswept pauldron spikes, a tower shield with a teal sunburst, a double-bladed waraxe and a teal cape (silhouette: a broad heavy armoured figure with winged helm crests, spiked shoulders and a big shield in front; hue: deep bronze-gold, teal and white plume; value: mid-light). The shipped elven warrior is a slimmer white-and-gold plated fighter with a polearm axe and a round shield, the elven guard is green-clad, the corruptor and mage robed: this must not be slim, not white-gold, not green and not robed.",
      "Deep burnished bronze-gold plate in a mid-light value with bright polished highlight planes and a bright rim light, teal-blue enamel trim, white plume, teal cape, pale elven skin; nothing darker than deep bronze except thin plate seams and the visor slit; the disc stays neutral charcoal at reference lightness." + DISC,
      "READY single, no define_as (elven elite warrior)", comp=COMP + FIT + COMPACT + BRIGHT)

asset(2, 'fire-wyrm', 'fire wyrm',
      "charred-scar pool, the demon-nest and dragon-loot and sleeping-dragons vaults and the renegade-wyrmics vault (general/npcs/fire-drake.lua:84, dragon/fire, non-unique, no define_as, rank 3, base BASE_NPC_FIRE_DRAKE, nice_tile tall body); the only definition of this name (Varsha the Writhing is another name)",
      [src(FDRK, 'name = "fire wyrm"'), src(FDRK, 'resolvers.nice_tile', after='name = "fire wyrm"'), src(FDRK, 'T_DEVOURING_FLAME', after='name = "fire wyrm"'), src(FDRK, 'define_as = "BASE_NPC_FIRE_DRAKE"')],
      src(FDRK, 'define_as = "BASE_NPC_FIRE_DRAKE"'), None, 'dragon', 'fire', False, True,
      'base BASE_NPC_FIRE_DRAKE (dragon/fire, no image=, no shader, no sustains_at_birth);' + TALLD % 'dragon_fire_fire_wyrm' + '; Bellowing Roar, Wing Buffet, Fire Breath and Devouring Flame are activated; make_escort names fire drakes (their own token); no sustains_at_birth, no equip, no auto_classes; ingredient_on_death only names a drop',
      'dragon_fire_fire_wyrm.png',
      [STY, IDN('dragon_fire_fire_wyrm.png', 'Native shape (64x128, tall): a large crimson dragon with wings spread up and back with spiky ridges, a coiled body and a red eye. Keep the big crimson horned dragon with a coiled body and jagged wings, drawn as ONE compact figure filling the disc, no tall canvas, as an ancient serpentine wyrm clearly different from the shipped fire drake.'), REF_DRAGONS],
      "A fire wyrm seen from a steep overhead three-quarter angle: an ancient bulky SERPENTINE dragon whose heavy body is coiled in an S on the disc, its long thick neck REARED and the head turned to the lower left with the jaws open showing a glowing GOLD-ORANGE throat and a pointed tongue of small flame, scales deep SCARLET and CRIMSON in a mid-light value with bright orange-red highlight planes on every upper-left plate, pale CREAM armoured belly plates, a CROWN of long swept-back curved horns in pale bone-ivory, a ridge of jagged spines down the back, huge leathery WINGS half-folded against the back with ragged torn membranes in bright red-orange and bone-ivory finger spines (all wing tips inside the disc), thin glowing ember cracks between the scales, a golden slit eye. Ancient, coiled, horned and complete.",
      "Dragons: the FIRE WYRM is the ANCIENT SERPENTINE DEEP SCARLET DRAGON coiled in an S with a reared neck, open jaws, a horn crown and half-folded ragged wings (silhouette: a coiled body with a tall reared neck and head, folded wings behind; hue: deep scarlet and crimson with cream belly, ivory horns and gold throat; value: mid-light). The shipped fire drake is an orange crouching four-legged drake with wings fully spread and a fire cone, and the other drakes are cold blue, sand, venom green and storm violet: this must not be orange, not a crouched winged silhouette and must not spit a big fire cone.",
      "Deep scarlet and crimson scales in a mid-light value with bright orange-red highlight planes and a bright rim light, cream belly plates, ivory horns and spines, a gold-orange throat glow (the glow stays in the throat and must not tint or light the disc); nothing darker than deep crimson except thin scale seams; NO black or dark maroon body; the disc stays neutral charcoal at reference lightness." + DISC,
      "READY tall (fire wyrm, native_tall)", comp=COMP + FIT + COMPACT + BRIGHT + DARKFIX + CATS)

asset(2, 'runed-bone-giant', 'runed bone giant',
      "rak-shor-pride pool (general/npcs/bone-giant.lua:97, undead/giant, non-unique, no define_as, rank 3, base BASE_NPC_BONE_GIANT, nice_tile tall body); the only definition of this name (Half-Finished Bone Giant is another name)",
      [src(BONE, 'name = "runed bone giant"'), src(BONE, 'resolvers.nice_tile', after='name = "runed bone giant"'), src(BONE, 'T_ARCANE_POWER', after='name = "runed bone giant"'), src(BONE, 'resolvers.sustains_at_birth()', after='name = "runed bone giant"'), src(BONE, 'define_as = "BASE_NPC_BONE_GIANT"')],
      src(BONE, 'define_as = "BASE_NPC_BONE_GIANT"'), None, 'undead', 'giant', False, True,
      'base BASE_NPC_BONE_GIANT (undead/giant, no image=, no shader, no sustains_at_birth in the base);' + TALLD % 'undead_giant_runed_bone_giant' + '; the leaf calls resolvers.sustains_at_birth() and Arcane Power is its only sustain (temporary values only); Bone Armour, Stun, Skeleton Reassemble, Manathrust, Manaflow, Strike and Earthen Missiles are activated; no equip, no auto_classes; ingredient_on_death only names a drop',
      'undead_giant_runed_bone_giant.png',
      [STY, IDN('undead_giant_runed_bone_giant.png', 'Native shape (64x128, tall): a towering giant assembled from tan bones etched with red runes inside a faint pink-lilac aura, arms hanging. Keep the hulking bone-assembled giant with red runes on its bones, drawn as ONE compact hunched figure filling the disc, no tall canvas, with bright glowing crimson runes and crimson eye pits.'), REF_GIANTS],
      "A runed bone giant seen from a steep overhead three-quarter angle: a HULKING hunched giant assembled from hundreds of AGED CREAM-TAN and ivory bones (skulls, ribs, thigh bones, vertebrae), big skull head with small horns and two glowing CRIMSON eye pits, broad shoulders, one huge arm RAISED in a casting gesture and the other fist hanging low, every large bone plate on the chest, shoulders and forearms carved with bright glowing CRIMSON-RED RUNE GLYPHS, a ring of six pale red RUNE GLYPHS floating in an arc close around the figure (inside the disc), a faint ROSE-PINK aura hugging the outline, bright cream highlight planes on every upper-left bone. Towering, rune-carved, crimson-lit and complete.",
      "Giants: the RUNED BONE GIANT is the HUNCHED BONE GIANT with glowing CRIMSON RUNES carved on every bone plate, crimson eye pits, one arm raised casting and a ring of floating red glyphs (silhouette: a hulking figure with a raised arm and orbiting glyphs; hue: aged cream-tan bone with bright crimson runes and a rose aura; value: mid-light). The shipped bone giant is plain tan, the heavy bone giant golden and plated, the eternal bone giant pale with a lilac halo and Atamathon white-grey metal: this must not be plain, not golden-plated, not lilac and must show the glowing red runes and the orbiting glyphs.",
      "Aged cream-tan and ivory bone in a mid-light value with bright cream highlight planes and a bright rim light, glowing crimson runes, glyphs and eye pits and a faint rose aura (the glow stays on the giant and the floating glyphs and must not tint or light the disc); nothing darker than mid tan-brown except thin bone seams and the eye pits; the disc stays neutral charcoal at reference lightness." + DISC,
      "READY tall (runed bone giant, native_tall)", comp=COMP + FIT + COMPACT + BRIGHT + CATS)

# ---- pack 3: temporal elementals and the void horror ----
asset(3, 'ultimate-telugoroth', 'ultimate telugoroth',
      "temporal-rift pool (general/npcs/telugoroth.lua:132, elemental/temporal, non-unique, no define_as, rank 3, base BASE_NPC_TELUGOROTH, nice_tile tall body); the only definition of this name (telugoroth and greater telugoroth are other leaves with their own tokens)",
      [src(TELU, 'name = "ultimate telugoroth"'), src(TELU, 'resolvers.nice_tile', after='name = "ultimate telugoroth"'), src(TELU, 'T_RETHREAD', after='name = "ultimate telugoroth"'), src(TELU, 'resolvers.sustains_at_birth()', after='name = "ultimate telugoroth"'), src(TELU, 'define_as = "BASE_NPC_TELUGOROTH"')],
      src(TELU, 'define_as = "BASE_NPC_TELUGOROTH"'), None, 'elemental', 'temporal', False, True,
      'base BASE_NPC_TELUGOROTH (elemental/temporal, no image=, no shader, no sustains_at_birth in the base);' + TALLD % 'elemental_temporal_ultimate_telugoroth' + '; the leaf calls resolvers.sustains_at_birth() but none of its talents (Turn Back the Clock, Echoes from the Past, Rethread, Stop) is sustained, so nothing starts; no equip, no auto_classes',
      'elemental_temporal_ultimate_telugoroth.png',
      [STY, IDN('elemental_temporal_ultimate_telugoroth.png', 'Native shape (64x128, tall): a big tall oval cloud of shifting yellow, orange and blue mist and sparks with a ragged outline. Keep the colossal shifting time-mist of yellow, orange and blue with sparks, drawn as ONE compact figure filling the disc, no tall canvas, as an eight-pointed starburst of radiating sand-blade spokes around a white-gold core.'), REF_TELUGOROTH],
      "An ultimate telugoroth seen from a steep overhead three-quarter angle: a colossal TIME STORM in the middle of the disc, a blazing WHITE-GOLD CORE sphere at its centre, EIGHT to TWELVE sharp radiating golden SAND-BLADE SPOKES (like clock hands and sunburst rays) shooting outward from the core so that the whole silhouette is an EIGHT-POINTED STARBURST (every spoke tip inside the disc), between the spokes thick swirling ribbons of AMBER, GOLD, SAPPHIRE-BLUE and VIOLET sand and mist curling outward, thin bright sapphire LIGHTNING arcs threading between the spokes, tiny gold clock-gear fragments and glittering sand grains scattered inside the starburst. Radiant, spoked, swirling and complete.",
      "Temporal elementals: the ULTIMATE TELUGOROTH is the EIGHT-POINTED STARBURST TIME STORM with a white-gold core, radiating golden sand-blade spokes and ribbons of amber, sapphire and violet (silhouette: a star with sharp radiating spokes around a bright core; hue: white-gold, amber, sapphire and violet; value: very light). The shipped telugoroth is a flat round rainbow swirl, the greater telugoroth a slim gold-orange twisting flame column, the teluvorta a spiky violet crystal ball: this must not be a flat round swirl, not a slim column and not a crystal urchin.",
      "White-gold, amber and gold in a light value with sapphire and violet ribbons and bright sapphire lightning (the glow stays on the storm and must not tint, brighten or yellow the disc); nothing darker than mid violet except thin seams between ribbons; the disc stays neutral charcoal at reference lightness." + DISC,
      "READY tall (ultimate telugoroth, native_tall)", comp=COMP + FIT + COMPACT + BRIGHT + CATS)

asset(3, 'greater-teluvorta', 'greater teluvorta',
      "temporal-rift pool (general/npcs/telugoroth.lua:180, elemental/temporal, non-unique, no define_as, rank 2, base BASE_NPC_TELUGOROTH, nice_tile tall body); the only definition of this name (teluvorta and ultimate teluvorta are other leaves)",
      [src(TELU, 'name = "greater teluvorta"'), src(TELU, 'resolvers.nice_tile', after='name = "greater teluvorta"'), src(TELU, 'T_REALITY_SMEARING', after='name = "greater teluvorta"'), src(TELU, 'resolvers.sustains_at_birth()', after='name = "greater teluvorta"'), src(TELU, 'define_as = "BASE_NPC_TELUGOROTH"')],
      src(TELU, 'define_as = "BASE_NPC_TELUGOROTH"'), None, 'elemental', 'temporal', False, True,
      'base BASE_NPC_TELUGOROTH (elemental/temporal, no image=, no shader, no sustains_at_birth in the base);' + TALLD % 'elemental_temporal_greater_teluvorta' + '; the leaf calls resolvers.sustains_at_birth() and Reality Smearing is its only sustain (temporary values only, no display write); Dust to Dust and Temporal Wake are activated; the teluvorta swap function only exchanges map positions; no equip, no auto_classes',
      'elemental_temporal_greater_teluvorta.png',
      [STY, IDN('elemental_temporal_greater_teluvorta.png', 'Native shape (64x128, tall): a tall dark violet-blue mist storm with pink and lilac swirls, faint small horns at the top and a soft ragged outline. Keep the dark violet time-mist with lilac swirls and horns, drawn as ONE compact figure filling the disc, no tall canvas, as a smooth billowing storm-cloud crowned with six long curved horns and trailing a dust wake, clearly not the spiky crystal teluvorta.'), REF_TELUGOROTH],
      "A greater teluvorta seen from a steep overhead three-quarter angle: a dense round billowing STORM-CLOUD of VIOLET and INDIGO mist in a mid-light value with soft LILAC and rose-pink swirls and bright pale highlight billows on every upper-left bulge, CROWNED by a ring of SIX long curved IVORY-LILAC HORNS sweeping up and inward like a crown (horn tips inside the disc), two glowing pale-CYAN eyes glaring from the mist, and a comet-like trailing WAKE of drifting cream DUST grains and cracked HOURGLASS glass shards streaming off to one side close to the body, a bright lilac rim light along the cloud outline. Billowing, horned, dust-trailing and complete.",
      "Temporal elementals: the GREATER TELUVORTA is the SMOOTH BILLOWING VIOLET STORM-CLOUD crowned with six long curved ivory horns, cyan eyes and a trailing dust-and-hourglass wake (silhouette: a round soft cloud with a horn crown and a trailing tail of dust; hue: violet, indigo, lilac with ivory horns and cyan eyes; value: mid-light). The shipped teluvorta is a SPIKY violet CRYSTAL-URCHIN ball with no horn crown and no wake, the telugoroth a rainbow swirl, the greater telugoroth a gold column: this must not be spiky or faceted, must not be a rainbow swirl or gold, and must show the horn crown and the dust wake.",
      "Violet and indigo mist in a mid-light value with lilac and rose-pink swirls and bright pale highlight billows, ivory-lilac horns, pale cyan eyes and cream dust (the glow stays on the cloud and must not tint or light the disc); nothing darker than deep violet except thin seams and the eye pits; NO black; the disc stays neutral charcoal at reference lightness." + DISC,
      "READY tall (greater teluvorta, native_tall)", comp=COMP + FIT + COMPACT + BRIGHT + DARKFIX + CATS)

asset(3, 'void-horror', 'void horror',
      "temporal-rift pool (general/npcs/horror_temporal.lua:160, horror/temporal, non-unique, no define_as, rank 2, base BASE_NPC_HORROR_TEMPORAL, default-name image); the only definition of this name",
      [src(HTMP, 'name = "void horror"'), src(HTMP, 'T_ENERGY_DECOMPOSITION', after='name = "void horror"'), src(HTMP, 'resolvers.sustains_at_birth()', after='name = "void horror"'), src(HTMP, 'define_as = "BASE_NPC_HORROR_TEMPORAL"')],
      src(HTMP, 'define_as = "BASE_NPC_HORROR_TEMPORAL"'), None, 'horror', 'temporal', False, False,
      'base BASE_NPC_HORROR_TEMPORAL (horror/temporal, no image=, no shader, no sustains_at_birth in the base);' + DEF + '; the leaf calls resolvers.sustains_at_birth() and Energy Decomposition is its only sustain (temporary values only, no display write); Energy Absorption, Entropy, Echoes from the Void and Void Shards are activated; on_die forces a random anomaly talent (a separate spawned actor, never a rewrite of this one); no equip, no auto_classes',
      'horror_temporal_void_horror.png',
      [STY, IDN('horror_temporal_void_horror.png', 'Native shape (64x64): a dark vertical oval hole in spacetime with a bright cross-shaped twinkle and tiny star points inside, a black smoky halo. Keep the vertical oval rift in spacetime with the bright starry twinkle inside, but render a luminous silver-white border, a mid-indigo starfield interior and pale silver shards around it so that it reads as a bright shape on the dark disc.'), REF_VOIDS],
      "A void horror seen from a steep overhead three-quarter angle: a tall vertical LENS-SHAPED TEAR in spacetime, a pointed oval like a great eye standing on the disc, its border a thick LUMINOUS SILVER-WHITE ring with an inner icy-CYAN glow, the inside a mid-INDIGO and violet STARFIELD (never darker than mid indigo) full of tiny bright white and cyan stars around a brilliant white FOUR-POINT STAR-FLARE at the centre and a swirling lilac NEBULA ribbon, jagged pale-silver CRACKS radiating a short way out of the rim like shattered glass, and a ring of small floating pale-SILVER SPACE SHARDS close around the rift (all inside the disc), a bright white rim light along the outer border. Luminous, cracked, starry and complete.",
      "Temporal horrors: the VOID HORROR is the VERTICAL LENS-SHAPED SPACETIME TEAR with a luminous silver-white border, a mid-indigo starfield with a bright four-point flare and a nebula ribbon, cracks and floating silver shards (silhouette: a pointed vertical oval eye-rift with radiating cracks; hue: silver-white, cyan, indigo and violet; value: light border with a mid-value interior). The shipped dredgling is a pink humanoid, the dredge a hulking pale brute, the temporal stalker chrome, the dread a violet smoke wraith, the shadow stalker dark smoke: this must not be a creature body, must not be smoke and must not be black inside.",
      "Silver-white border and cyan glow in a light value, mid-indigo and violet starfield with bright white and cyan stars, a lilac nebula ribbon, pale silver cracks and shards (the light stays on the rift and must not tint or light the disc); nothing darker than mid indigo anywhere, NO black void; the disc stays neutral charcoal at reference lightness." + DISC,
      "READY single, no define_as (void horror)", comp=COMP + FIT + COMPACT + BRIGHT + DARKFIX)

# ---- pack 4: the aquatic horrors ----
asset(4, 'swarming-horror', 'swarming horror',
      "lake-nur pool, its own six-strong escort and the swarm hive's summons (general/npcs/horror_aquatic.lua:91, horror/aquatic, non-unique, no define_as, rank 1, base BASE_NPC_HORROR_AQUATIC, nice_tile tall body); the only definition of this name",
      [src(HAQU, 'name = "swarming horror"'), src(HAQU, 'resolvers.nice_tile', after='name = "swarming horror"'), src(HAQU, 'T_BLINDSIDE', after='name = "swarming horror"'), src(HAQU, 'define_as = "BASE_NPC_HORROR_AQUATIC"')],
      src(HAQU, 'define_as = "BASE_NPC_HORROR_AQUATIC"'), None, 'horror', 'aquatic', False, True,
      'base BASE_NPC_HORROR_AQUATIC (horror/aquatic, no image=, no shader, no sustains_at_birth in the base);' + TALLD % 'horror_aquatic_swarming_horror' + '; Blindside is its only talent (activated); the base on_die only adds bubble grids to the terrain; no sustains_at_birth, no equip, no auto_classes',
      'horror_aquatic_swarming_horror.png',
      [STY, IDN('horror_aquatic_swarming_horror.png', 'Native shape (64x128 canvas): a loose swarm of about seven tiny grey fish-like creatures with pale glowing bellies and eyes drifting together in the lower part of the canvas. Keep the small school of grey fish-like horrors with glowing pale bellies, but render them in mid-light silvery-teal with big pale eyes, drawn as one compact loose ring filling the disc, no tall canvas.'), REF_AQUA],
      "A swarming horror seen from a steep overhead three-quarter angle: a SCHOOL of EIGHT small fish-like horrors circling together in a loose SPIRAL RING around the centre of the disc, each about one sixth of the disc across with a stubby body in mid-light SILVERY-TEAL and pale steel-blue with bright silver highlight planes, a big round pale glowing yellow-white EYE, a wide mouth of tiny white needle teeth, ragged small fins and a luminous pale-mint BELLY, a few tiny pale bubbles between them (all inside the disc), each body clearly separate with a small gap of bare plate between neighbours. Many small, silvery, needle-toothed and complete.",
      "Aquatic horrors: the SWARMING HORROR is a SCHOOL OF EIGHT SMALL SILVERY-TEAL FISH-LIKE HORRORS with big pale eyes and needle teeth circling in a ring (silhouette: many small separate bodies in a loose spiral ring; hue: silvery teal, steel-blue, mint bellies and pale yellow-white eyes; value: mid-light). Every shipped water token is ONE body (violet ink squid, squid, giant eel, electric eel, naga): this must be many small bodies and must not be one squid, eel or naga; and it differs from the single spined slate-blue ravenous horror of this batch.",
      "Silvery-teal and pale steel-blue bodies in a mid-light value with bright silver highlight planes and a bright rim light, pale mint bellies, pale yellow-white eyes, white teeth; nothing darker than deep teal except the mouth interiors and thin seams; NO black bodies; the disc stays neutral charcoal at reference lightness." + DISC,
      "READY tall (swarming horror, native_tall)", comp=COMP + FIT + COMPACT + BRIGHT + DARKFIX + SWARMS)

asset(4, 'ravenous-horror', 'ravenous horror',
      "lake-nur pool (general/npcs/horror_aquatic.lua:114, horror/aquatic, non-unique, no define_as, rank 2, base BASE_NPC_HORROR_AQUATIC, nice_tile tall body); the only definition of this name",
      [src(HAQU, 'name = "ravenous horror"'), src(HAQU, 'resolvers.nice_tile', after='name = "ravenous horror"'), src(HAQU, 'T_BLOOD_GRASP', after='name = "ravenous horror"'), src(HAQU, 'define_as = "BASE_NPC_HORROR_AQUATIC"')],
      src(HAQU, 'define_as = "BASE_NPC_HORROR_AQUATIC"'), None, 'horror', 'aquatic', False, True,
      'base BASE_NPC_HORROR_AQUATIC (horror/aquatic, no image=, no shader, no sustains_at_birth in the base);' + TALLD % 'horror_aquatic_ravenous_horror' + '; Blood Lock, Blood Grasp and Drain are activated; the base on_die only adds bubble grids to the terrain; no sustains_at_birth, no equip, no auto_classes',
      'horror_aquatic_ravenous_horror.png',
      [STY, IDN('horror_aquatic_ravenous_horror.png', 'Native shape (64x128, tall): a big dark grey-black spined horror with a cluster of round pale eyes, a wide toothy jaw and yellow liquid drooling from its teeth, spiked fins jutting outward. Keep the big spined fanged predator with round pale eyes and yellow drool, but render the body in mid-light slate-blue with bone-white spines and lime-yellow acid, drawn as ONE compact figure filling the disc, no tall canvas.'), REF_AQUA],
      "A ravenous horror seen from a steep overhead three-quarter angle: ONE fat fanged deep-water predator lunging towards the lower left, a blunt wide head with a huge GAPING MOUTH bristling with rows of long white NEEDLE TEETH, thick glowing LIME-YELLOW ACID drooling from the teeth in a few short strings, a cluster of six round pale glowing EYES above the mouth, a heavy body of SLATE-BLUE and steel-blue in a mid-light value with silver highlight planes and pale scale plates, a huge FAN of sharp BONE-WHITE SPINED FINS jutting outward from the back and sides (every spine tip inside the disc), a short thick tail curled to one side. Fanged, spined, acid-drooling and complete.",
      "Aquatic horrors: the RAVENOUS HORROR is ONE FAT SLATE-BLUE FANGED PREDATOR with a gaping needle-toothed mouth dripping lime-yellow acid, six pale eyes and a huge fan of bone-white spined fins (silhouette: one big body with a wide open jaw and radiating spines; hue: slate-blue, bone-white and lime-yellow; value: mid-light). The shipped violet ink squid, squid, giant eel, electric eel and naga are smooth tentacled or serpentine bodies, and the swarming horror of this batch is a school of small silvery-teal fish: this must not be tentacled, not serpentine, not violet and not a school.",
      "Slate-blue and steel-blue body in a mid-light value with silver highlight planes and a bright rim light, bone-white teeth and spines, pale glowing eyes, lime-yellow acid (the acid stays on the creature and must not tint or light the disc); nothing darker than mid slate except the mouth interior and thin seams; NO black body; the disc stays neutral charcoal at reference lightness." + DISC,
      "READY tall (ravenous horror, native_tall)", comp=COMP + FIT + COMPACT + BRIGHT + DARKFIX + CATS)


def retry(id_, pack, **changes):
    base = next(a for a in A if a['id'] == id_)
    A.append(dict(base, pack=pack, **changes))


exec((HERE / 'retries.py').read_text()) if (HERE / 'retries.py').exists() else None


TALL_IDS = tuple(a['id'] for a in A if a['native_tall'])
EXPL_IDS = ('black-mamba', 'rogue-sapper')
PNGF = {a['id']: 'NPC.lua:33 default-name image on the leaf (no image=/nice_tile)' for a in A}
PNGF.update({i: 'explicit image= on the leaf (no nice_tile/add_mos)' for i in EXPL_IDS})
PNGF.update({i: 'NPC.lua:33 default-name image on the leaf plus an explicit nice_tile tall body (image=invis.png, one add_mos entry with display_h=2, display_y=-1 naming the same PNG)' for i in TALL_IDS})
EVDIR = 'evidence/monster-batch-z-20260930/source-contracts.json'
DEFINE = {a['id']: a['define_as'] for a in A}


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
        if a['native_tall']:
            ident['tall_body'] = {'image': 'invis.png', 'add_mos': [{'image': native_image, 'display_h': 2, 'display_y': -1}],
                                  'catalog_flag': 'native_tall=true', 'static_pin': 'nice_tile names the tall PNG explicitly; not unique, so no unique-only tall path applies'}
        if a['base']:
            ident['base_source'] = a['base']
        if len(a['srcs']) > 1:
            ident['extra_sources'] = a['srcs'][1:]
        identities.append(ident)
    findings = [
        "All twelve names have exactly one NPC leaf definition. The zone pools, the vaults (bandit-fortress for the bandit lord and rogue sapper, thief-hideout for the rogue sapper, demon-nest / dragon-loot / sleeping-dragons / renegade-wyrmics for the fire wyrm), the orb spinner and hive escorts (orb weaver, swarming horror) only build those same leaves through name/random_filter lookups, so they are the very same actors; a random boss made from a flat entry goes through the existing captureRandomOrigin path, a random boss made from a non-unique native-tall entry (the renegade-wyrmics fire wyrm 'Flame Terror') stays native because only unique tall bodies qualify.",
        "Summons that copy a monster wear its token: the bandit lord's Summon calls the bandit, thief and rogue leaves (each already has its own token); the swarm hive summons and the swarming horror's own escort call the swarming horror leaf; the orb spinner escort calls the orb weaver leaf; the fire wyrm's escort calls fire drakes (their own token).",
        "Rogue sapper: its explicit image is the assassin's PNG (humanoid_human_assassin.png), which the assassin catalog entry (define_as THIEF_ASSASSIN) also names. by_name resolves each actor by its own name and define_as, so a sapper wears the sapper token and an assassin the assassin token; the new sapper token is a khaki goggled trapper, not a recolour of the assassin.",
        "Black mamba: the explicit image darkgrey-snake.png is used by this leaf only; the anaconda, king cobra and other snakes have their own PNGs and tokens.",
        "No summon, clone, event or talent builds an actor with any of the twelve names using a different native PNG (grep of every actor definition, static map, quest script, vault, encounter, event and talent under game/modules/tome for the names and PNGs).",
        "Neighbours that reuse a name or subtype but stay native: 'elven warrior' (own token), 'assassin' (own token), 'ultimate teluvorta' (tall, own name), 'telugoroth', 'greater telugoroth' and 'teluvorta' (own tokens), 'entrenched horror', 'boiling horror', 'swarm hive', 'abyssal horror' (other aquatic leaves), 'Half-Finished Bone Giant', 'Varsha the Writhing', 'anaconda', 'orb spinner', 'dredge captain'.",
        "Result: no per-identity `variants` entry and no `image_aliases` entry is needed for this batch.",
    ]
    ev = {'schema': 1,
          'task': "monster-batch-z: static re-verification (no game launch) of the twelve identities that follow batch Y in the survey-2 unscheduled list (black mamba, bandit lord, orb weaver, elven elite warrior, ultimate telugoroth, greater teluvorta, runed bone giant, void horror, swarming horror, ravenous horror, rogue sapper, fire wyrm) against game/modules/tome source and native sprites. Every field below was read from source: name, type/subtype, define_as (only the rogue sapper binds one, THIEF_SAPPER), explicit or NPC.lua:33 default image, unique, PNG on disk, and absence of moddable_tile/shader/anim/add_displays on each leaf and its base. Findings: six identities are non-unique native-tall bodies (ultimate telugoroth, greater teluvorta, runed bone giant, swarming horror, ravenous horror, fire wyrm: nice_tile image=invis.png with one explicit add_mos display_h=2, display_y=-1) with native_tall=true; six are 64x64 single images (the bandit lord, orb weaver, elven elite warrior and void horror use the NPC.lua:33 default-name image; the black mamba and the rogue sapper name their PNG with image=).",
          'new_ids_not_in_catalog_before_this_batch': [i['id'] for i in identities], 'identities': identities,
          'runtime_mutation_scan': {
              'method': "every talent of each identity (resolvers.talents, inherited base talents and the base-file talent lists) was resolved under game/modules/tome/data/talents and its mode read (sustained/activated/passive); the same talents/, timed_effects/, birth/ and class/ greps for writes to type/subtype/image/add_mos/add_displays/moddable_tile/replace_display/shader as batches S to Y were applied and give the same writer set; the resolvers sustains_at_birth, inscriptions, equip, racial and nice_tile and the base-file resolvers were read; every auto_classes site under zones/, general/ and maps/ was listed with its leaf name.",
              'writers_found': [
                  {'file': 'game/modules/tome/data/talents/corruptions/shadowflame.lua', 'line': 97, 'talent': "Flame of Urh'Rok", 'effect': 'sustain: __old_type={type,subtype}; type,subtype = demon,major; image untouched; restored on deactivate'},
                  {'file': 'game/modules/tome/data/talents/psionic/thought-forms.lua', 'line': 93, 'talent': 'thought-form summons (Solipsist tree)', 'effect': 'sets type/subtype/image/moddable_tile/add_mos on the summoned minion copied from its summoner, never on the caster'},
                  {'file': 'game/modules/tome/data/talents/chronomancy/anomalies.lua', 'line': 587, 'talent': 'anomaly summons', 'effect': 'creates a separate spawned NPC with another image; not the caster (the void horror only forces a random anomaly talent on death)'}],
              'other_hits_reviewed': [
                  'talents/spells/golemancy.lua and talents/uber/mag.lua (player-only moddable_tile writes: alchemist golem and the player skeleton; no identity of this batch)',
                  'timed_effects/physical.lua and other.lua (add_displays/replace_display only while the effect is active)', 'timed_effects/magical.lua (invisibility, shadow-simulacrum and similar shaders, dragon egg image, only while active)'],
              'timed_effects_review': "timed_effects write shader, replace_display, add_displays or image only while active (invisibility shaders, stone/ice/pin displays, Wrathroot, Shivgoroth form, dragon egg, Lord of Skulls): the matcher rejects them (native art shows) and restores the token when they end.",
              'sustains_at_birth_review': [
                  {'identity': 'bandit lord', 'sustained': ['Stealth', 'Total Thuggery'], 'note': 'the base BASE_NPC_THIEF calls resolvers.sustains_at_birth(); stealth and thuggery temporary values only, no display write'},
                  {'identity': 'rogue sapper', 'sustained': ['Stealth'], 'note': 'the base BASE_NPC_THIEF and the leaf call resolvers.sustains_at_birth(); stealth temporary values only'},
                  {'identity': 'greater teluvorta', 'sustained': ['Reality Smearing'], 'note': 'temporary values only'},
                  {'identity': 'runed bone giant', 'sustained': ['Arcane Power'], 'note': 'temporary values only'},
                  {'identity': 'void horror', 'sustained': ['Energy Decomposition'], 'note': 'temporary values only'},
                  {'identity': 'orb weaver', 'sustained': [], 'note': 'the base BASE_NPC_SPIDER resolvers.sustains_at_birth() finds no sustained talent on this leaf (Spin Fate is not learned; Lay Web and Spider Web are activated)'},
                  {'identity': 'ultimate telugoroth', 'sustained': [], 'note': 'the leaf calls resolvers.sustains_at_birth() but none of its talents is sustained'},
                  {'identity': 'black mamba, elven elite warrior, swarming horror, ravenous horror, fire wyrm', 'sustained': [], 'note': 'no sustains_at_birth on the leaf or base'}],
              'auto_classes_review': [
                  {'identity': 'all twelve', 'class': 'none', 'finding': "none of the twelve leaves or their bases has auto_classes; every auto_classes site in zones/, general/ and maps/ belongs to another leaf, so none can reach Flame of Urh'Rok and there is no urh_rok_form opt-in."}],
              'visibility_review': 'Identities with inscriptions or Stealth (bandit lord, rogue sapper, orb weaver, elven elite warrior) can roll an invisibility rune/infusion or stealth that applies a shader effect while it lasts; the matcher rejects an actor with a shader (native art shows) and the token returns when it ends; token drawing follows actor visibility as for every other token.',
              'hits_in_batch': [],
              'no_hit': [i['native_name'] for i in identities]},
          'summons_and_same_body_copies': {
              'method': "grep of every actor definition, static map, quest script, vault, encounter, event and talent under game/modules/tome (data and class) for the twelve names and PNGs; talents that build summons/copies (summon-*, dreadmaster, master-of-flesh, master-of-bones, rot, thought-forms, simulacra/mirror images, Grand Arrival, golemancy, cloneFull users, hive summons, bandit lord Summon) checked for copies of these bodies.",
              'findings': findings},
          'name_collisions_checked': [
              {'name': a['name'], 'other_definitions': ['none'], 'outcome': ('single actor definition bound to define_as ' + a['define_as'] if a['define_as'] else 'single actor definition without define_as; the catalog entry has no define_as and matches by exact name, type and subtype')} for a in {x['id']: x for x in A}.values()],
          'kept_native': [],
          'neighbours_kept_native': [
              {'name': 'Training Dummy', 'reason': 'listed at 12.0 by the scoring script but kept native since batch T'},
              {'name': 'dredge captain', 'reason': 'score 1.8, below this batch'},
              {'name': 'ultimate teluvorta', 'reason': 'score 1.7, next tier candidate'}]}
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
                 'gate_reason': f"Exact source identity re-verified directly against game/modules/tome source (name={a['name']}, define_as={a['define_as']}, type={a['type']}/subtype={a['subtype']}, unique={a['unique']}, native_tall={a['native_tall']}); details and hashes in evidence/monster-batch-z-20260930/source-contracts.json. {a['structure']}. Exact catalog entry only, never a whole-subtype mapping.",
                 'render_evidence': [{'path': render, 'sha256': evsha}]}
        if a.get('refinement'):
            entry['refinement'] = a['refinement']
        packs.setdefault(a['pack'], []).append(entry)
    for n, assets in packs.items():
        p = ADDON / f'art/production/batches/monster-batch-z-{n}.json'
        if p.exists():
            print('exists, skipped', p.name)
            continue
        p.write_text(json.dumps({'schema': 1, 'batch_id': f'monster-batch-z-{n}', 'assets': assets}, indent=2, ensure_ascii=False) + '\n')
        print('wrote', p.name)


if __name__ == '__main__':
    build()
