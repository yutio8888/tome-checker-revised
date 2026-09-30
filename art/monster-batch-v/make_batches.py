"""Generate the monster-batch-v task packs and the pinned source-contract
evidence (survey-2 unscheduled list after batch U: black crystal, faerlhing,
losselhing, dredge, dolleg, eternal bone giant, drem master, orc pyromancer,
orc cryomancer, bloated horror, yaech hunter, orc blood mage; see
SELECTION.md). Pure bookkeeping: hashes native sources/sprites, writes JSON and
the composite family references. Retry packs are appended by later edits of
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
CRYSTAL, SPIDER, HTEMP, HCORR, HORROR, MAJOR, BONE, ORCVOR, ORCRS, YAECH = (
    'general/npcs/crystal.lua', 'general/npcs/spider.lua', 'general/npcs/horror_temporal.lua', 'general/npcs/horror-corrupted.lua',
    'general/npcs/horror.lua', 'general/npcs/major-demon.lua', 'general/npcs/bone-giant.lua', 'general/npcs/orc-vor.lua',
    'general/npcs/orc-rak-shor.lua', 'general/npcs/yaech.lua')
REFS = HERE / 'refs'
ART_REL = 'game/addons/tome-checker-revised/art/monster-batch-v/'


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


REF_CRYSTALS = RC('crystals', ['white-crystal', 'red-crystal', 'crimson-crystal', 'spellblaze-crystal'], 2,
                  'Four shipped crystal tokens (white clear vertical prism cluster, red wide fan of thin shards, crimson single big faceted ruby, spellblaze violet spiked ball): the black crystal must not be white or clear, not a thin-shard fan, not a single gem and not a spiked ball.')
REF_SPIDERS = RC('spiders', ['giant-spider', 'spitting-spider', 'fate-spinner', 'weaver-young', 'chitinous-spider', 'nimisil', 'gaeramarth', 'ninurlhing', 'fate-weaver'], 3,
                 'Nine shipped spider tokens (dark grey giant spider, brown spitting spider, steel-blue fate spinner with a silk ring, white swirl weaver young, cream chitinous spider, silver gem-crowned nimisil, ash-and-bone rearing gaeramarth, bloated lime ninurlhing, cream-and-lavender fluffy fate weaver): the two new spiders must not repeat any of their colours or poses.')
REF_HORRORS = RC('horrors', ['dredgling', 'drem', 'dremling', 'weirdling-beast', 'horned-horror'], 3,
                 'Five shipped horror tokens (small thin pink dredgling crouched on all fours, dark-brown armoured drem with axe and shield, grey-white shaggy dremling, tan-pink many-armed weirdling beast, horned horror with a bull head and tentacles): none of the three new horrors may be any of these.')
REF_ORCS = RC('orcs', ['orc-necromancer', 'orc-archer', 'orc-assassin', 'orc-warrior', 'orc-soldier', 'orc-master-assassin', 'orc-grand-master-assassin'], 4,
              'Seven shipped orc tokens (hooded navy orc necromancer with a green glow, orc archer with a bow, hooded blue-grey assassin, orc warrior with a scimitar, spiked orc soldier, olive orc master assassin with crossed daggers, ivory-masked grand master assassin): the three new orc casters are bare-headed robed mages, none of them hooded or armed with blades or bows.')
REF_DEMONS = RC('demons', ['fire-imp', 'quasit', 'wretchling', 'onilug', 'water-imp'], 3,
                'Five shipped demon tokens (small vermilion winged fire imp, bronze bull-headed quasit with a round shield, yellow-green crouching wretchling, grey-mauve onilug, teal water imp): the dolleg is a big upright brick-red thorned brute, none of these.')
REF_GIANTS = RC('bone-giants', ['bone-giant', 'half-finished-bone-giant', 'snow-giant'], 3,
                'Three shipped giant tokens (tan bone giant, muscular and symmetric with both arms hanging; purple half-finished bone giant, a thin skeleton; snow giant): the eternal bone giant is an ivory-white ossuary golem with skulls and ONE huge arm raised overhead, not a symmetric arms-down pose and not a thin skeleton.')
REF_YEEKS = RC('yeeks', ['yaech-diver', 'yeek-wayist'], 2,
               'Two shipped yeek-kin tokens (pale blue fluffy yaech diver swimming with bubbles, white yeek wayist with a dagger): the yaech hunter is umber-brown with an ochre belly, not blue and not white.')

DEMPTY = ' no resolvers.equip that touches the body; no sustains_at_birth and no auto_classes on the leaf or base'
EQUIPONLY = ' resolvers.equip fills inventory slots only (no moddable_tile, so no display change)'
TALLD = ' NPC.lua:33 default-name image on the leaf; resolvers.nice_tile{image="invis.png", add_mos={{image="npc/%s.png", display_h=2, display_y=-1}}} (an explicit tall body, keys image/display_h/display_y only; with nicer_tiles off nice_tile is a no-op and the default-name image is the single path); no moddable_tile, shader, anim or add_displays; native sprite 64x128; non-unique with no define_as, so the catalog entry carries native_tall=true (nativeTallImage accepts the body only for unique or native_tall entries, as for bone giant and onilug)'

# ---- pack 1: crystal and spiders ----
asset(1, 'black-crystal', 'black crystal',
      "old-forest and scintillating-caves crystal pools (general/npcs/crystal.lua:119, immovable/crystal, non-unique, no define_as, rank 2, base BASE_NPC_CRYSTAL, explicit image=npc/crystal_black.png overriding the base's crystal_npc.png); the only definition of this name; no vault, event or talent builds another actor with this name (the Arena file only bases its own golden crystal on BASE_NPC_CRYSTAL)",
      [src(CRYSTAL, 'name = "black crystal"'), src(CRYSTAL, 'T_BLIGHT_BOLT', after='name = "black crystal"'), src(CRYSTAL, 'image = "npc/crystal_black.png"')],
      src(CRYSTAL, 'define_as = "BASE_NPC_CRYSTAL"'), None, 'immovable', 'crystal', False, False,
      "base BASE_NPC_CRYSTAL (immovable/crystal, image=npc/crystal_npc.png overridden by the leaf, never_move, lite 2, no shader/nice_tile/add_mos);" + EXPL + "; the leaf also sets tint=colors.BLACK (Entity.lua:129 turns it into tint_r/g/b, which tints only the native MO; the token is its own Entity); talents Blight Bolt (activated) and the base Phase Door; no sustains_at_birth and no auto_classes",
      'crystal_black.png',
      [STY, IDN('crystal_black.png', 'Native shape (64x64): a spiky cluster of black crystal shards drawn as thin dark outlines. Keep the idea of a shard cluster, but as a solid glossy gunmetal-grey formation.'), REF_CRYSTALS],
      "A black crystal seen from a steep overhead three-quarter angle: a formation of thick hexagonal SMOKY-QUARTZ crystal columns in a GUNMETAL-GREY and GRAPHITE-BLUE mid tone, ONE large main column leaning up and to the right at about thirty degrees with a faceted pointed top, TWO shorter columns beside it (one leaning left, one nearly upright), and a scatter of small crystal shards and pale grey stone rubble at their foot. Every upper-left crystal face carries a bright SILVER-WHITE polished highlight plane and thin cold VIOLET edge-light lines; the shaded faces are mid slate-grey, never black; tiny pale glints at the tips. Solid, glossy, heavy and complete; no eyes, no face.",
      "Crystals: the BLACK crystal is a cluster of three thick faceted gunmetal-grey columns with silver highlights and a violet rim (silhouette: three chunky leaning columns, one big, on a rubble foot; hue: gunmetal grey with violet edge light; value: mid with bright highlights). The shipped white crystal is a tall clear-white vertical prism bunch, red crystal a wide red fan of thin shards, crimson crystal one big faceted ruby and spellblaze crystal a violet spiked ball: this must not be white or clear, not a fan of thin shards, not one single gem and not a spiked ball; and it must not read as a near-black mass.",
      "Gunmetal grey in a mid value with slate-blue shaded facets, silver-white polished highlight planes, thin violet edge light, pale grey stone rubble; nothing darker than dark slate except hairline crack seams; the disc stays neutral charcoal at reference lightness and no crystal glow or reflection lights or darkens the disc." + DISC,
      "READY single, no define_as (black crystal)", comp=COMP + FIT + COMPACT + BRIGHT)

asset(1, 'faerlhing', 'faerlhing',
      "ardhungol spider pool (general/npcs/spider.lua:153, spiderkin/spider, non-unique, no define_as, rank 3, base BASE_NPC_SPIDER, default-name image); single definition; no vault, event or talent builds another actor with this name (Ungole's lair only draws it from the spiderkin pool)",
      [src(SPIDER, 'name = "faerlhing"'), src(SPIDER, 'T_PHANTASMAL_SHIELD', after='name = "faerlhing"'), src(SPIDER, 'resolvers.sustains_at_birth()')],
      src(SPIDER, 'define_as = "BASE_NPC_SPIDER"'), None, 'spiderkin', 'spider', False, False,
      'base BASE_NPC_SPIDER (spiderkin/spider, sustains_at_birth in the base);' + DEF + '; talents Spider Web, Lay Web, Phase Door, Manathrust, Manaflow (activated), Phantasmal Shield, Disruption Shield, Arcane Power (sustained); resolvers.sustains_at_birth() starts the three sustained ones (temporary values, shield values and particles only, no type/subtype/image/add_mos write); resolvers.inscriptions(2, infusion); no auto_classes',
      'spiderkin_spider_faerlhing.png',
      [STY, IDN('spiderkin_spider_faerlhing.png', 'Native shape (64x64): a purple spider with pink stripes and lilac legs. Keep the arcane purple identity but make it a glowing amethyst spirit spider with a rune on its back.'), REF_SPIDERS],
      "A faerlhing seen from a steep overhead three-quarter angle: an elegant arcane spirit spider with a glossy, slightly translucent AMETHYST-PURPLE and MAGENTA body in a mid-light value, a round abdomen carrying a bright glowing TEAL-WHITE RUNE RING with a small sigil in its centre, a head with four small glowing teal-white eyes, and EIGHT SLENDER LONG LEGS in lilac-purple with pale pink joints ARCHING HIGH UP and inward like the bars of a rounded cage over the body (the leg tips coming down close to the body), the two front legs cradling a small compact glowing TEAL-WHITE MANA ORB in front of the head (the orb no bigger than the head). Elegant, arcane, cage-like and complete.",
      "Spiders: the FAERLHING is the CAGE-LEGGED ARCANE one, a deep amethyst-magenta spider whose long legs arch up and in like a rounded cage around a glowing teal mana orb, with a glowing rune on its abdomen (silhouette: a dome of arched thin legs with an orb in front; hue: amethyst purple, magenta and teal-white glow; value: mid-light). The shipped fate weaver is a cream-white and lavender fluffy spider, the fate spinner is steel blue, nimisil is silver with a gem crown, weaver young is a white-blue ball and gaeramarth is ash and bone: this must not be cream, not blue, not silver, not fluffy and not reared up. The other new spider is an icy pale-cyan frost spider with a crest of ice spikes (losselhing).",
      "Amethyst purple and magenta in a mid-light value with pale pink-lilac highlight planes, lilac legs with pale pink joints, teal-white glowing rune ring and mana orb (the glow stays on the creature and must not tint or brighten the disc); nothing darker than deep violet except the eyes and thin seams." + DISC,
      "READY single, no define_as (faerlhing)", comp=COMP + FIT + COMPACT + BRIGHT)

asset(1, 'losselhing', 'losselhing',
      "ardhungol spider pool (general/npcs/spider.lua:211, spiderkin/spider, non-unique, no define_as, rank 3, base BASE_NPC_SPIDER, default-name image); single definition; no vault, event or talent builds another actor with this name",
      [src(SPIDER, 'name = "losselhing"'), src(SPIDER, 'T_ICY_SKIN', after='name = "losselhing"'), src(SPIDER, 'resolvers.sustains_at_birth()')],
      src(SPIDER, 'define_as = "BASE_NPC_SPIDER"'), None, 'spiderkin', 'spider', False, False,
      'base BASE_NPC_SPIDER (spiderkin/spider, sustains_at_birth in the base);' + DEF + '; talents Rush, Spider Web, Lay Web, Freeze, Tidal Wave, Ice Storm (activated), Icy Skin, Frost Hands (sustained); resolvers.sustains_at_birth() starts the two sustained ones (temporary values and damage callbacks only, no type/subtype/image/add_mos write); resolvers.inscriptions(2, infusion); no auto_classes',
      'spiderkin_spider_losselhing.png',
      [STY, IDN('spiderkin_spider_losselhing.png', 'Native shape (64x64): an icy pale-blue striped spider with light-blue legs. Keep the frost-blue colour idea but make it a squat frost spider with a crest of ice crystals on its back.'), REF_SPIDERS],
      "A losselhing (snow-star spider) seen from a steep overhead three-quarter angle: a squat, wide, low frost spider with a thick coat of shaggy WHITE FROST FUR over an ICY AQUAMARINE and PALE CYAN body, two big glowing pale-blue eyes and small ice-white fangs, SHORT STOUT frost-crusted legs in pale cyan with white rime spread wide, and on its back a CREST OF SIX SHARP ICE CRYSTALS fanning out like a snowflake star behind the head (the crystals pale cyan with bright white edges, the crest kept inside the disc), small icicles hanging from the leg joints. Squat, frosty, spiky-crested and complete.",
      "Spiders: the LOSSELHING is the SQUAT FROSTY one with a fan of ice crystals on its back (silhouette: a wide low body with a spiky snowflake-star crest; hue: icy aquamarine, pale cyan and white frost; value: light). The shipped chitinous spider is a cream radial spider, weaver young a white-blue ball, fate spinner a steel-blue long-legged spider with a silk ring, giant spider dark grey: this must not be a radial long-legged spider, not a smooth ball and not cream or steel blue. The other new spider is a deep amethyst cage-legged arcane spider with a glowing rune (faerlhing).",
      "Icy aquamarine and pale cyan in a light value with white frost fur and bright white highlight planes, cyan ice crystals with bright white edges, pale blue eyes; nothing darker than mid teal-blue except the eyes and thin seams; the disc stays neutral charcoal at reference lightness and must not be brightened by the pale frost or tinted blue." + DISC,
      "READY single, no define_as (losselhing)", comp=COMP + FIT + COMPACT + BRIGHT)

# ---- pack 2: horrors ----
asset(2, 'dredge', 'dredge',
      "temporal-rift, ardhungol, dreadfell and others' temporal-horror pools (general/npcs/horror_temporal.lua:73, horror/temporal, non-unique, no define_as, rank 2, base BASE_NPC_HORROR_TEMPORAL, default-name image, leaf field dredge=1); single definition; the dredge captain (horror_temporal.lua:98) only lists it in make_escort by name, so escorts are this same leaf",
      [src(HTEMP, 'name = "dredge"'), src(HTEMP, 'T_CLINCH', after='name = "dredge"'), src(HTEMP, 'name="dredge", number=3'), src(HTEMP, 'resolvers.sustains_at_birth()', after='name = "dredge"')],
      src(HTEMP, 'define_as = "BASE_NPC_HORROR_TEMPORAL"'), None, 'horror', 'temporal', False, False,
      'base BASE_NPC_HORROR_TEMPORAL (horror/temporal, no image=, no shader);' + DEF + '; leaf field dredge=1 (a flag read by the Dredge Frenzy talent only); talents Stun, Speed Sap, Clinch (activated), Crushing Hold (passive); resolvers.sustains_at_birth() on the leaf but no sustained talent known, so nothing starts; no equip, no auto_classes',
      'horror_temporal_dredge.png',
      [STY, IDN('horror_temporal_dredge.png', 'Native shape (64x64): a huge hunched brownish-pink brute with very long arms hanging to the ground. Keep the hulking knuckle-walker but a salmon-pink stitched brute with enormous fists planted on the ground.'), REF_HORRORS],
      "A dredge seen from a steep overhead three-quarter angle: a huge hunched knuckle-walking brute with wrinkled, stitched SALMON-PINK skin in a mid-light value, a massively broad rounded back and shoulders, TWO ENORMOUSLY THICK tree-trunk arms planted on the ground in front of it ending in heavy round fists, a TINY bald head with small pale eyes sunk deep between the shoulders, short stumpy legs, faint pale grey stubble and pale stitched scars across the back, and a few small pale blue clock-cog scars glowing softly on one shoulder. Wide, heavy, round and complete; the fists and knuckles stay well inside the disc.",
      "Horrors: the DREDGE is the HUGE HEAVY ROUND one, a hunched salmon-pink brute with enormous fists planted on the ground (silhouette: one wide rounded mass with two fat arm-posts and a tiny head; hue: salmon pink with pale grey stitches and pale blue cog scars; value: mid-light). The shipped dredgling is a small thin pink humanoid crouched on all fours with bulbous eyes, the weirdling beast a tan-pink many-armed octopus-like blob, drem and dremling armoured or shaggy dwarfish figures: this must not be small, thin or crouching on thin limbs, must have no tentacles and no armour. The other new horrors are a pale armoured faceless commander with a raised fist (drem master) and a cream-white floating bloated pear with red sores (bloated horror).",
      "Salmon-pink skin in a mid-light value with pale peach highlight planes and warm rose-brown shadows, pale grey stubble and stitches, pale blue cog scars, pale eyes; nothing darker than dark rose-brown except the eye pits and thin seams; the disc stays neutral charcoal at reference lightness with no warm cast." + DISC,
      "READY single, no define_as (dredge)", comp=COMP + FIT + COMPACT + BRIGHT)

asset(2, 'drem-master', 'drem master',
      "deep-bellow and maze corrupted-horror pools (general/npcs/horror-corrupted.lua:118, horror/corrupted, non-unique, no define_as, rank 2, base BASE_NPC_CORRUPTED_HORROR, default-name image); single definition; its make_escort lists drem and dremling by name, so nothing else is built as a drem master",
      [src(HCORR, 'name = "drem master"'), src(HCORR, 'T_DOMINATE', after='name = "drem master"'), src(HCORR, 'resolvers.sustains_at_birth()', after='name = "drem master"')],
      src(HCORR, 'define_as = "BASE_NPC_CORRUPTED_HORROR"'), None, 'horror', 'corrupted', False, False,
      'base BASE_NPC_CORRUPTED_HORROR (horror/corrupted, no image=, no shader);' + DEF + ';' + EQUIPONLY + ' (waraxe, shield, heavy armour); talents Dwarf Resilience, Dredge Frenzy, Dominate (all activated); resolvers.sustains_at_birth() on the leaf but no sustained talent known, so nothing starts; no auto_classes',
      'horror_corrupted_drem_master.png',
      [STY, IDN('horror_corrupted_drem_master.png', 'Native shape (64x64): a stocky dwarf-like figure in brown mail with a pale faceless head and a raised fist. Keep the pale faceless sewn-mouth head and the raised commanding fist, in lighter patched steel-blue mail.'), REF_HORRORS],
      "A drem master seen from a steep overhead three-quarter angle: a stocky dwarf-proportioned corrupted commander with a PALE GREY faceless head, a stitched-shut mouth and no eyes, wearing patched-together DENTED STEEL-BLUE-GREY mail armour with orange RUST patches and a ragged pale grey cloth sash, ONE FIST RAISED HIGH IN COMMAND beside the head and the other hand holding a chipped waraxe pointing down and forward, short thick legs planted wide. Stocky, grim, lopsided and complete; everything stays inside the disc.",
      "Horrors: the DREM MASTER is the LIGHT STEEL-BLUE ARMOURED COMMANDER with one fist raised (silhouette: a stocky figure with one arm raised above the head and an axe pointing down on the other side; hue: pale grey face, steel-blue-grey mail, orange rust patches; value: mid-light). The shipped drem is a dark brown armoured dwarfish figure with a round shield, the dremling a grey-white shaggy hunched creature, the dredgling a thin pink crouching creature: this must not be brown, must not carry a shield and must not be shaggy. The other new horrors are a huge salmon-pink knuckle-walker (dredge) and a cream-white floating bloated pear (bloated horror).",
      "Pale grey skin and cloth, dented steel-blue-grey mail in a mid-light value with pale highlight planes, orange rust patches, a chipped pale-steel axe head; nothing darker than dark steel-blue except thin seams and the stitched mouth; the disc stays neutral charcoal at reference lightness and the mail must not merge with it." + DISC,
      "READY single, no define_as (drem master)", comp=COMP + FIT + COMPACT + BRIGHT)

asset(2, 'bloated-horror', 'bloated horror',
      "lake-nur, ardhungol, ruined-dungeon and eight more zones' pools plus the horror-chamber, skeleton-mage-cabal vaults and the Arena generator (general/npcs/horror.lua:116, horror/eldritch, non-unique, no define_as, rank 2, base BASE_NPC_HORROR, default-name image, never_move, levitation); single leaf definition named exactly this; the dreams zone's 'lost wife' (zones/dreams/npcs.lua:100, define_as WIFE) only sets subtype = \"bloated horror\" and keeps another name, type humanoid/orc base and its own tall PNG",
      [src(HORROR, 'name = "bloated horror"'), src(HORROR, 'T_MIND_DISRUPTION', after='name = "bloated horror"'), src(HORROR, 'resolvers.sustains_at_birth()', after='name = "bloated horror"'), src('maps/vaults/auto/greater/horror-chamber.lua', 'name="bloated horror"')],
      src(HORROR, 'define_as = "BASE_NPC_HORROR"'), None, 'horror', 'eldritch', False, False,
      'base BASE_NPC_HORROR (horror/eldritch, no image=, no shader);' + DEF + '; talents Phase Door, Mind Disruption, Mind Sear, Telekinetic Blast (all activated); resolvers.inscriptions(1, shielding rune); resolvers.sustains_at_birth() on the leaf but no sustained talent known, so nothing starts; ingredient_on_death only; no auto_classes',
      'horror_eldritch_bloated_horror.png',
      [STY, IDN('horror_eldritch_bloated_horror.png', 'Native shape (64x64): a fat pink bulbous body with a large bald childlike head and raised arms. Keep the bulbous body and the big childlike head, but pale cream-white with red sores.'), REF_HORRORS],
      "A bloated horror seen from a steep overhead three-quarter angle: a FLOATING fat PEAR-SHAPED body of pale CREAM-WHITE and faint yellowish skin in a light value, swollen and glossy, pock-marked with a dozen bright RED-PINK SORES and a few purple veins, a disproportionately LARGE BALD CHILD-LIKE HEAD with big round pale eyes and a small open mouth at the top, two SMALL stubby arms raised in front of the chest, no legs, a soft rounded tapering underside hovering above the disc (no ground shadow). Round, bloated, pale and complete.",
      "Horrors: the BLOATED HORROR is the PALE ROUND FLOATING one, a cream-white pear with red sores and a big childlike head (silhouette: one rounded pear with a big head on top and tiny arms; hue: cream-white and yellowish with red-pink sores; value: light). The shipped dredgling is a thin pink crouching creature, the weirdling beast a tan-pink many-armed octopus-like blob, the horned horror a bull-headed tentacle monster, the dremling a grey-white shaggy figure: this must not be pink, must have no tentacles and must not crouch on limbs. The other new horrors are a huge salmon-pink knuckle-walker (dredge) and a steel-blue armoured commander with a raised fist (drem master).",
      "Cream-white and faintly yellow skin in a light value with bright highlight planes and pale grey-lilac shadows, red-pink sores, purple veins, pale eyes; nothing darker than mid grey-lilac except the pupils and thin seams; the disc stays neutral charcoal at reference lightness and must not be brightened by the pale body." + DISC,
      "READY single, no define_as (bloated horror)", comp=COMP + FIT + COMPACT + BRIGHT)

# ---- pack 3: orc casters ----
ORCB = ' resolvers.racial() adds only levelup talent tables (no display); resolvers.auto_equip_filters and resolvers.equip only fill inventory (no moddable_tile, so no display change); resolvers.inscriptions(runes)'
asset(3, 'orc-pyromancer', 'orc pyromancer',
      "vor-armoury and rak-shor-pride pools and the renegade-pyromancers and orc-hatred vaults (general/npcs/orc-vor.lua:55, humanoid/orc, non-unique, no define_as, rank 2, base BASE_NPC_ORC_VOR, default-name image); single definition; the vaults build this same leaf by name (random_filter), some as random bosses",
      [src(ORCVOR, 'name = "orc pyromancer"'), src(ORCVOR, 'T_FLAMESHOCK', after='name = "orc pyromancer"'), src(ORCVOR, 'resolvers.sustains_at_birth()', after='name = "orc pyromancer"'), src('maps/vaults/renegade-pyromancers.lua', 'name = "orc pyromancer"')],
      src(ORCVOR, 'define_as = "BASE_NPC_ORC_VOR"'), None, 'humanoid', 'orc', False, False,
      'base BASE_NPC_ORC_VOR (humanoid/orc, faction orc-pride, no image=, no shader);' + DEF + ';' + ORCB + '; talents Flame, Flameshock, Fireflash, Phase Door (activated), Spellcraft (sustained), Staff Mastery (passive); resolvers.sustains_at_birth() starts Spellcraft (temporary values only, no type/subtype/image/add_mos write); no auto_classes',
      'humanoid_orc_orc_pyromancer.png',
      [STY, IDN('humanoid_orc_orc_pyromancer.png', 'Native shape (64x64): an olive-green orc in a bright red robe with one arm raised. Keep the olive-green orc in a bright red-orange robe and give it a staff with a fire ball.'), REF_ORCS],
      "An orc pyromancer seen from a steep overhead three-quarter angle: a broad-shouldered OLIVE-GREEN orc with a bald head painted with red war stripes, small tusks and a hard scowl, wearing a BRIGHT ORANGE-RED long robe with gold trim and a gold sash (bare-headed, no hood), standing with feet apart, the RIGHT ARM holding a wooden staff diagonally up and outward with a compact bright ORANGE FIRE BALL with a yellow-white core on the staff head (the fire ball no bigger than the head and the staff tip well inside the disc), the left hand open at the hip with a few small flames. Fiery, robed, diagonal and complete.",
      "Orc casters: the PYROMANCER is the ORANGE-RED ROBED ONE with a diagonal staff ending in a fire ball (silhouette: a robed figure with one long diagonal line and a round flame; hue: orange-red robe with gold trim over olive skin; value: mid-light). The shipped orc necromancer is a hooded navy-robed orc with a green glow, the assassins are hooded or crossed-dagger fighters, the warrior and soldier are armoured melee orcs and the archer holds a bow: this must not be hooded, must not hold blades or a bow and must not be navy or grey. The other two new orc casters are a blue-robed one with arms wide throwing an ice shard fan (cryomancer) and a rose-and-bone robed hunched one holding a blood orb (blood mage).",
      "Olive-green skin, orange-red robe in a mid-light value with pale orange highlight planes, gold trim and sash, a wooden staff, orange fire ball with a yellow-white core (the fire stays on the staff and must not glow onto or warm the disc); nothing darker than dark red-brown except the eye slits and thin seams." + DISC,
      "READY single, no define_as (orc pyromancer)", comp=COMP + FIT + COMPACT + BRIGHT)

asset(3, 'orc-cryomancer', 'orc cryomancer',
      "vor-armoury and rak-shor-pride pools and the orc-hatred vault (general/npcs/orc-vor.lua:109, humanoid/orc, non-unique, no define_as, rank 2, base BASE_NPC_ORC_VOR, default-name image); single definition; the vault builds this same leaf by name (random_filter)",
      [src(ORCVOR, 'name = "orc cryomancer"'), src(ORCVOR, 'T_ICE_STORM', after='name = "orc cryomancer"'), src(ORCVOR, 'resolvers.sustains_at_birth()', after='name = "orc cryomancer"'), src('maps/vaults/auto/greater/orc-hatred.lua', 'name = "orc cryomancer"')],
      src(ORCVOR, 'define_as = "BASE_NPC_ORC_VOR"'), None, 'humanoid', 'orc', False, False,
      'base BASE_NPC_ORC_VOR (humanoid/orc, faction orc-pride, no image=, no shader);' + DEF + ';' + ORCB + '; talents Freeze, Ice Storm, Tidal Wave, Phase Door (activated), Spellcraft (sustained), Staff Mastery (passive); resolvers.sustains_at_birth() starts Spellcraft (temporary values only, no type/subtype/image/add_mos write); no auto_classes',
      'humanoid_orc_orc_cryomancer.png',
      [STY, IDN('humanoid_orc_orc_cryomancer.png', 'Native shape (64x64): an olive-green orc in a bright blue robe with rune markings. Keep the olive-green orc in an ice-blue rune-embroidered robe; no staff, hands thrown wide with ice shards.'), REF_ORCS],
      "An orc cryomancer seen from a steep overhead three-quarter angle: a broad-shouldered OLIVE-GREEN orc with a shaved head, small tusks and one long WHITE BRAID falling over the front of the shoulder (bare-headed, no hood), wearing a bright ICE-BLUE long robe embroidered with pale WHITE RUNES and a white sash, standing with feet apart, BOTH ARMS SPREAD WIDE to the sides with the palms pushed outward, and in front of and beside the hands a fan of SIX pale-cyan and white ICE SHARDS radiating outward (each shard short and the whole fan kept inside the inner three quarters of the disc), a little white frost on the sleeves. Icy, robed, wide and complete; no staff.",
      "Orc casters: the CRYOMANCER is the ICE-BLUE ROBED ONE with arms thrown wide and a fan of ice shards (silhouette: a wide low V of arms with a shard fan, no staff; hue: ice-blue robe with white runes and a white braid over olive skin; value: mid-light). The shipped orc necromancer is a hooded navy-robed orc with a green glow, the assassins are hooded or crossed-dagger fighters, the warrior and soldier are armoured melee orcs and the archer holds a bow: this must not be hooded, must not hold a staff, blade or bow and must not be navy or grey. The other two new orc casters are an orange-red robed one with a diagonal fire staff (pyromancer) and a rose-and-bone robed hunched one holding a blood orb (blood mage).",
      "Olive-green skin, ice-blue robe in a mid-light value with pale cyan highlight planes, white runes, sash and braid, pale-cyan and white ice shards (the frost stays on the creature and must not tint or brighten the disc); nothing darker than mid steel-blue except the eye slits and thin seams." + DISC,
      "READY single, no define_as (orc cryomancer)", comp=COMP + FIT + COMPACT + BRIGHT)

asset(3, 'orc-blood-mage', 'orc blood mage',
      "rak-shor-pride, ardhungol and reknor pools, the rak-shor-pride mapscript (main.lua:29) and the renegade-undead vault (general/npcs/orc-rak-shor.lua:116, humanoid/orc, non-unique, no define_as, rank 2, base BASE_NPC_ORC_RAK_SHOR, default-name image); single definition; the mapscript and vault build this same leaf by name as random bosses (random_boss path)",
      [src(ORCRS, 'name = "orc blood mage"'), src(ORCRS, 'T_BLOOD_GRASP', after='name = "orc blood mage"'), src(ORCRS, 'resolvers.sustains_at_birth()', after='name = "orc blood mage"'), src('zones/rak-shor-pride/mapscripts/main.lua', 'name="orc blood mage"')],
      src(ORCRS, 'define_as = "BASE_NPC_ORC_RAK_SHOR"'), None, 'humanoid', 'orc', False, False,
      'base BASE_NPC_ORC_RAK_SHOR (humanoid/orc, faction orc-pride, no image=, no shader);' + DEF + ';' + ORCB + '; talents Soul Rot, Blood Grasp, Curse of Vulnerability (activated), Staff Mastery (passive); resolvers.sustains_at_birth() on the leaf but no sustained talent known besides possible racial ones (temporary values only); no auto_classes',
      'humanoid_orc_orc_blood_mage.png',
      [STY, IDN('humanoid_orc_orc_blood_mage.png', 'Native shape (64x64): an olive-green orc in a dark blood-red robe with a gold collar. Keep the olive-green orc in a blood-stained robe, but rose-red and bone-white, hunched, holding a blood orb.'), REF_ORCS],
      "An orc blood mage seen from a steep overhead three-quarter angle: an OLIVE-GREEN orc hunched forward with a small BONE CIRCLET on a shaved head, small tusks and glowing pale-red eyes (bare-headed, no hood), wearing a long ROSE-RED and BONE-WHITE robe with a cream bone-plate collar and a few dark red blood stains (the robe rose-red, not black), both hands cupped together in front of the chest holding a compact floating glossy BLOOD-RED ORB with a bright pink highlight and a thin ring of red mist around it (the orb no bigger than the head), feet planted close. Hunched, robed, round and complete.",
      "Orc casters: the BLOOD MAGE is the HUNCHED ROSE-AND-BONE ROBED ONE cupping a blood orb in both hands (silhouette: a compact forward-leaning mass with one round orb at the chest; hue: rose-red robe with bone-white plates over olive skin; value: mid-light). The shipped orc necromancer is a hooded navy-robed orc with a green glow, the assassins are hooded or crossed-dagger fighters, the warrior and soldier are armoured melee orcs and the archer holds a bow: this must not be hooded, must not be black or navy, must not hold a staff, blade or bow. The other two new orc casters are an orange-red robed one with a diagonal fire staff (pyromancer) and an ice-blue robed one with arms wide throwing an ice shard fan (cryomancer).",
      "Olive-green skin, rose-red robe in a mid-light value with pale pink highlight planes, cream bone plates and circlet, glossy blood-red orb with a bright pink highlight (the red mist stays on the creature and must not tint the disc); nothing darker than dark rose-brown except the eye glow, blood stains and thin seams; no black robe anywhere." + DISC,
      "READY single, no define_as (orc blood mage)", comp=COMP + FIT + COMPACT + BRIGHT)

# ---- pack 4: dolleg, eternal bone giant, yaech hunter ----
asset(4, 'dolleg', 'dolleg',
      "valley-moon-caverns, demon-plane, ardhungol and three more zones' demon pools (general/npcs/major-demon.lua:51, demon/major, non-unique, no define_as, rank 2, base BASE_NPC_MAJOR_DEMON, explicit nice_tile tall body); single definition; the Fearscape summons of Kryl-Feijan, Lithfengel and Harkor'Zun only draw major demons from the level pool, so a dolleg from them is this same leaf",
      [src(MAJOR, 'name = "dolleg"'), src(MAJOR, 'resolvers.nice_tile', after='name = "dolleg"'), src(MAJOR, 'T_ACIDIC_SKIN', after='name = "dolleg"')],
      src(MAJOR, 'define_as = "BASE_NPC_MAJOR_DEMON"'), None, 'demon', 'major', False, True,
      'base BASE_NPC_MAJOR_DEMON (demon/major, faction fearscape, no image=, no shader, no sustains_at_birth);' + TALLD % 'demon_major_dolleg' + '; talents Acidic Skin (sustained, not started at birth) and Slime Spit; resolvers.inscriptions(1, rune); no auto_classes',
      'demon_major_dolleg.png',
      [STY, IDN('demon_major_dolleg.png', 'Native shape (64x128, tall): a tall dark red-brown thorned demon with long whip-like horns and amber thorns down its back. Keep the thorny brute and the whip-like horns, but draw it as ONE compact upright figure filling the disc, brick-red, no tall canvas.'), REF_DEMONS],
      "A dolleg seen from a steep overhead three-quarter angle: a thick-set upright thorned demon with BRICK-RED and TERRACOTTA skin in a mid value, a broad chest and heavy shoulders, two thick arms held slightly out from the body with clawed hands, a heavy brow, small glowing amber eyes, and TWO LONG CURLING WHIP-LIKE HORNS sweeping back from the head, its shoulders, upper arms, spine and knees studded with short pale AMBER-BONE THORNS (a starburst of short thorns around the silhouette, none longer than a hand's width), a few drops of bright ACID-GREEN liquid dripping from the thorn tips. Brutish, spiky, upright and complete; the whole figure kept inside the disc with the horns curled in.",
      "Demons: the DOLLEG is the BIG UPRIGHT THORNED BRICK-RED ONE (silhouette: a heavy upright figure with a starburst of short thorns and two curling horns; hue: brick-red with amber-bone thorns and acid-green drips; value: mid). The shipped fire imp is a small vermilion winged imp throwing a fire ball, quasit a bronze bull-headed shield bearer, wretchling a yellow-green crouching crawler, onilug a grey-mauve slouching figure: this must not be small, winged, yellow-green, bull-headed or hunched, and must not throw fire.",
      "Brick-red and terracotta skin in a mid value with pale salmon highlight planes and deep red-brown shadows, pale amber-bone thorns and horns with cream tips, amber eyes, bright acid-green drips (the drips stay on the creature and must not glow onto the disc); nothing darker than dark red-brown except the eye sockets and thin seams." + DISC,
      "READY tall (dolleg, native_tall)", comp=COMP + FIT + COMPACT + BRIGHT)

asset(4, 'eternal-bone-giant', 'eternal bone giant',
      "rak-shor-pride, telmur and vor-armoury pools (general/npcs/bone-giant.lua:72, undead/giant, non-unique, no define_as, rank 2, base BASE_NPC_BONE_GIANT, explicit nice_tile tall body); the necromancer's Assemble talent (talents/spells/master-of-bones.lua:393, minions_list.e_bone_giant) builds the same-named minion with type undead, subtype giant, the same nice_tile body and no define_as, so it wears the same token by the ordinary name key (see summons_and_same_body_copies)",
      [src(BONE, 'name = "eternal bone giant"'), src(BONE, 'resolvers.nice_tile', after='name = "eternal bone giant"'), src('talents/spells/master-of-bones.lua', 'name = "eternal bone giant"'), src('talents/spells/master-of-bones.lua', 'is_bone_giant = "e_bone_giant"')],
      src(BONE, 'define_as = "BASE_NPC_BONE_GIANT"'), None, 'undead', 'giant', False, True,
      'base BASE_NPC_BONE_GIANT (undead/giant, no image=, no shader, no sustains_at_birth);' + TALLD % 'undead_giant_eternal_bone_giant' + '; talents Bone Armour, Stun, Skeleton Reassemble (all activated); no auto_classes',
      'undead_giant_eternal_bone_giant.png',
      [STY, IDN('undead_giant_eternal_bone_giant.png', 'Native shape (64x128, tall): a tall pale bone golem with a lilac outline aura. Keep the ivory bone golem with a faint lilac aura, but draw it as ONE compact hunched figure filling the disc, no tall canvas.'), REF_GIANTS],
      "An eternal bone giant seen from a steep overhead three-quarter angle: a hulking IVORY-WHITE ossuary golem built from hundreds of bones, hunched forward, its shoulders and chest studded with a ring of small pale SKULLS, ONE HUGE ARM made of fused thigh bones RAISED HIGH over the shoulder like a hammer with a knuckled bone fist, the other arm hanging down with a heavy bone fist, a small skull-like head sunk between the shoulders with cold VIOLET glowing eye sockets, thick bone legs, and a faint pale LILAC unholy aura hugging its outline (a thin glow, no wisps beyond the inner three quarters of the disc). Massive, asymmetric, bony and complete.",
      "Giants: the ETERNAL BONE GIANT is the IVORY-WHITE SKULL-STUDDED ONE with ONE HUGE ARM RAISED OVERHEAD (silhouette: a hunched mass with one big raised arm like a hammer; hue: ivory white with cool lilac shadows and violet eye glow; value: light). The shipped bone giant is a tan, muscular, symmetric figure with both arms hanging and the half-finished bone giant a thin purple skeleton: this must not be tan, must not be symmetric with both arms down and must not be thin. ",
      "Ivory-white bone in a light value with bright highlight planes and cool lilac-grey shadows, pale skulls, violet eye glow, a faint lilac outline aura (the aura stays thin, on the creature, and must not brighten or tint the disc); nothing darker than mid lilac-grey except the eye sockets and thin seams." + DISC,
      "READY tall (eternal bone giant, native_tall)", comp=COMP + FIT + COMPACT + BRIGHT)

asset(4, 'yaech-hunter', 'yaech hunter',
      "murgol-lair pool (general/npcs/yaech.lua:64, humanoid/yaech, non-unique, no define_as, rank 2, base BASE_NPC_YAECH, default-name image); single definition; the south-beach zone only draws yaech from the humanoid/yaech pool, so a yaech hunter there is this same leaf",
      [src(YAECH, 'name = "yaech hunter"'), src(YAECH, 'T_MINDHOOK', after='name = "yaech hunter"'), src(YAECH, 'define_as = "BASE_NPC_YAECH"')],
      src(YAECH, 'define_as = "BASE_NPC_YAECH"'), None, 'humanoid', 'yaech', False, False,
      'base BASE_NPC_YAECH (humanoid/yaech, can_breath water, no image=, no shader);' + DEF + ';' + EQUIPONLY + ' (trident); talents Exotic Weapons Mastery (passive), Mindhook, Perfect Control (activated); no sustains_at_birth and no auto_classes on the leaf or base (only the Murgol-lair bosses have Mindslayer auto_classes)',
      'humanoid_yaech_yaech_hunter.png',
      [STY, IDN('humanoid_yaech_yaech_hunter.png', 'Native shape (64x64): a fluffy pale blue-white yeek-like swimmer with a trident. Keep the fluffy yeek body and the trident, but umber-brown fur and a diagonal thrust.'), REF_YEEKS],
      "A yaech hunter seen from a steep overhead three-quarter angle: a small fluffy yeek-like aquatic hunter with thick UMBER-BROWN and OCHRE-TAN fur in a mid-light value, a cream belly, big pale-yellow eyes with a determined scowl, a small coral-and-shell shoulder guard, a coil of pale rope net at the hip, LUNGING forward in a low crouch and THRUSTING a long pale-steel TRIDENT with both hands out along a DIAGONAL toward the upper right (the trident tip well inside the disc, no longer than the body), a few small bubbles by the shoulder. Compact, furry, diagonal and complete.",
      "Yeeks: the YAECH HUNTER is the UMBER-BROWN FURRY ONE lunging with a trident on a diagonal (silhouette: a compact furry crouch with one long diagonal trident; hue: umber brown and ochre fur with a cream belly and pale steel; value: mid-light). The shipped yaech diver is a pale blue-white fluffy swimmer and the yeek wayist a white yeek with a dagger: this must not be blue, white or holding a dagger.",
      "Umber-brown and ochre-tan fur in a mid-light value with pale tan highlight planes, a cream belly, pale-yellow eyes, pale-steel trident with a bright highlight edge, pale shell and coral accents, tiny pale bubbles; nothing darker than dark umber except the pupils and thin seams; the disc stays neutral charcoal at reference lightness with no warm cast." + DISC,
      "READY single, no define_as (yaech hunter)", comp=COMP + FIT + COMPACT + BRIGHT)


def retry(id_, pack, **changes):
    base = next(a for a in A if a['id'] == id_)
    A.append(dict(base, pack=pack, **changes))


# ---- retry packs are appended below by later edits of retries.py ----
exec((HERE / 'retries.py').read_text()) if (HERE / 'retries.py').exists() else None

EXPL_IDS = ('black-crystal',)
TALL_IDS = ('dolleg', 'eternal-bone-giant')
PNGF = {a['id']: 'NPC.lua:33 default-name image on the leaf (no image=/nice_tile)' for a in A}
PNGF.update({i: 'explicit image= on the leaf (no nice_tile/add_mos)' for i in EXPL_IDS})
PNGF.update({i: 'NPC.lua:33 default-name image on the leaf plus an explicit nice_tile tall body (image=invis.png, one add_mos entry with display_h=2, display_y=-1 naming the same PNG)' for i in TALL_IDS})


def build():
    packs = {}
    identities = []
    render = 'game/addons/tome-checker-revised/evidence/monster-batch-v-20260930/source-contracts.json'
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
        if a['native_tall']:
            ident['tall_body'] = {'image': 'invis.png', 'add_mos': [{'image': 'npc/' + a['native'], 'display_h': 2, 'display_y': -1}],
                                  'catalog_flag': 'native_tall=true', 'static_pin': 'nice_tile names the tall PNG explicitly; not unique, so no define_as binding is possible'}
        if a['base']:
            ident['base_source'] = a['base']
        if len(a['srcs']) > 1:
            ident['extra_sources'] = a['srcs'][1:]
        identities.append(ident)
    findings = [
        "All twelve names have exactly one leaf definition (eternal bone giant additionally has the Assemble minion table entry, below). Vaults (renegade-pyromancers, renegade-undead, orc-hatred, horror-chamber, skeleton-mage-cabal), the rak-shor-pride mapscript, the Arena generator and dredge/drem master make_escort only build those same leaves through random_filter/name lookups, so they are the very same actors; random bosses made from them go through the existing captureRandomOrigin path (a non-unique native-tall body such as a random-boss dolleg or eternal bone giant stays native there, as for bone giant).",
        "Eternal bone giant: talents/spells/master-of-bones.lua:393 (Assemble, minions_list.e_bone_giant, built by necroSetupSummon in talents/spells/spells.lua) creates a summon with the same name 'eternal bone giant', type undead, subtype giant and the identical nice_tile body (invis.png + add_mos {npc/undead_giant_eternal_bone_giant.png, display_h=2, display_y=-1}); it has no define_as and no unique, plus summoner, necrotic_minion, summoner_gain_exp and is_bone_giant fields. The catalog entry has no define_as, so the ordinary exact name+type+subtype key already matches it, and nativeTallImage() accepts its body: NO variants entry and NO image alias is needed (same as the shipped bone giant minion). A Lord of Skulls renames its minion ('Lord of Skulls (...)') and stays native. tests/token_mapping.lua covers both cases.",
        "No summon, clone, event or talent builds an actor with any of the other eleven names using a different native PNG (grep of every actor definition, static map, quest script, vault, encounter, event and talent under game/modules/tome for the names and PNGs), so no image_aliases entry and no variants entry are added; the summon-only image alias mechanism from batch U is not used.",
        "Neighbours that reuse a name or subtype but stay native: the dreams zone 'lost wife' (define_as WIFE) sets subtype = 'bloated horror' on a humanoid/orc base with its own tall PNG, so its type/subtype/name/image all differ from the bloated horror entry; Necromancer 'bone giant' and 'heavy bone giant' minions are other names (bone giant is catalogued, heavy bone giant is not).",
        "Result: no per-construct `variants` entry and no `image_aliases` entry is needed for this batch; the eternal bone giant Assemble minion is covered by the exact name key.",
    ]
    ev = {'schema': 1,
          'task': "monster-batch-v: static re-verification (no game launch) of the twelve identities that follow batch U in the survey-2 unscheduled list (black crystal, faerlhing, losselhing, dredge, dolleg, eternal bone giant, drem master, orc pyromancer, orc cryomancer, bloated horror, yaech hunter, orc blood mage) against game/modules/tome source and native sprites. Every field below was read from source: name, type/subtype, define_as (none: all twelve are define_as-less non-unique leaves), explicit or NPC.lua:33 default image, unique, PNG on disk, and absence of moddable_tile/shader/anim/add_displays on each leaf and its base. Findings: ten identities are 64x64 single images (black crystal names its PNG with image=, nine use the NPC.lua:33 default-name image); dolleg and eternal bone giant are non-unique native-tall bodies (nice_tile image=invis.png with one explicit add_mos display_h=2 display_y=-1 naming the tall 64x128 PNG), statically pinnable, and carry native_tall=true; none is unique. No identity has a Corruptor auto_class, so no urh_rok_form opt-in is added. The Assemble minion of the eternal bone giant is the same body under the same name and is covered by the ordinary key.",
          'new_ids_not_in_catalog_before_this_batch': [i['id'] for i in identities], 'identities': identities,
          'runtime_mutation_scan': {
              'method': "every talent of each identity (resolvers.talents, inherited base talents, racial levelup talents via resolvers.racial and the base-file talent lists) was resolved under game/modules/tome/data/talents and its mode read (sustained/activated/passive); the whole talents/, timed_effects/, birth/ and class/ trees were grepped for writes to type/subtype/image/add_mos/add_displays/moddable_tile/replace_display/shader (regex on any receiver, plus the tuple assignment form) and the results reviewed line by line, giving the same writer set as batches S, T and U; the resolvers sustains_at_birth, racial, inscriptions, equip, auto_equip_filters and nice_tile and the base-file resolvers were read; every auto_classes site under zones/, general/ and maps/ was grepped for Corruptor and Flame of Urh'Rok.",
              'writers_found': [
                  {'file': 'game/modules/tome/data/talents/corruptions/shadowflame.lua', 'line': 97, 'talent': "Flame of Urh'Rok", 'effect': 'sustain: __old_type={type,subtype}; type,subtype = demon,major; image untouched; restored on deactivate'},
                  {'file': 'game/modules/tome/data/talents/psionic/thought-forms.lua', 'line': 93, 'talent': 'thought-form summons (Solipsist tree)', 'effect': 'sets type/subtype/image/moddable_tile/add_mos on the summoned minion copied from its summoner, never on the caster'},
                  {'file': 'game/modules/tome/data/talents/chronomancy/anomalies.lua', 'line': 587, 'talent': 'anomaly summons', 'effect': 'creates a separate spawned NPC with another image; not the caster'}],
              'other_hits_reviewed': [
                  'talents/psionic/mentalism.lua:196 (party-member record for a Projection clone, sets the party subtype only)', 'talents/psionic/dream-forge.lua:135 and talents/celestial/twilight.lua (terrain objects)',
                  'talents/spells/golemancy.lua:152 and talents/uber/mag.lua:396 (golem and lich player display)', 'talents/chronomancy/timeline-threading.lua:342 (clears a shader on a clone)',
                  'timed_effects/physical.lua and other.lua (add_displays/replace_display only while the effect is active)', 'class/FortressPC.lua (the Fortress player)'],
              'timed_effects_review': "timed_effects write shader, replace_display, add_displays or image only while active (invisibility shaders, stone/ice/pin displays, Wrathroot, Shivgoroth form, dragon egg): the matcher rejects them (native art) until they end; none is applied at birth to these identities.",
              'sustains_at_birth_review': [
                  {'identity': 'faerlhing', 'sustained': ['Phantasmal Shield', 'Disruption Shield', 'Arcane Power'], 'note': 'started by the base BASE_NPC_SPIDER resolvers.sustains_at_birth(); shield/temporary values and particles only, no type/subtype/image/add_mos/shader write'},
                  {'identity': 'losselhing', 'sustained': ['Icy Skin', 'Frost Hands'], 'note': 'started by the base BASE_NPC_SPIDER resolvers.sustains_at_birth(); temporary values and damage callbacks only'},
                  {'identity': 'orc pyromancer', 'sustained': ['Spellcraft'], 'note': 'the leaf calls resolvers.sustains_at_birth(); temporary values only'},
                  {'identity': 'orc cryomancer', 'sustained': ['Spellcraft'], 'note': 'same as the pyromancer'},
                  {'identity': 'dredge, drem master, bloated horror, orc blood mage', 'sustained': [], 'note': 'the leaf calls resolvers.sustains_at_birth() (dredge also in the base) but knows no sustained talent (orc racial levelup talents such as Orc Fury/Hold the Ground are temporary-value talents that reach the orc blood mage only through levelup and write no display field)'},
                  {'identity': 'black crystal, dolleg, eternal bone giant, yaech hunter', 'sustained': [], 'note': 'no sustains_at_birth on the leaf or base (dolleg knows Acidic Skin but never starts it at birth)'}],
              'auto_classes_review': [
                  {'identity': 'all twelve', 'class': 'none', 'finding': "none of the twelve leaves or their bases has auto_classes; the zone-wide grep for Corruptor and Flame of Urh'Rok found only zones/rhaloren-camp, ruins-kor-pul, dreadfell, mark-spellblaze, sandworm-lair, general/events/cultists.lua and general/npcs/elven-caster.lua (already-mapped identities or other names).", 'outcome': "no hit: Flame of Urh'Rok is not reachable, so urh_rok_form is NOT set on any entry; the opt-in count stays 5. The dolleg is itself a demon/major, so a Urh'Rok flame form on another body never applies to it."}],
              'visibility_review': 'Every identity with inscriptions (spiders, orcs, bloated horror, dolleg) can roll an invisibility rune/infusion that applies a transient invis_edge shader through timed effects; the overlay already respects actor visibility and the transient shader rejects the token (native art) until it ends. No identity changes display at birth.',
              'hits_in_batch': [],
              'no_hit': [i['native_name'] for i in identities]},
          'summons_and_same_body_copies': {
              'method': "grep of every actor definition, static map, quest script, vault, encounter, event and talent under game/modules/tome (data and class) for the twelve names and PNGs; talents that build summons/copies (summon-*, master-of-flesh, master-of-bones, rot, thought-forms, simulacra/mirror images, Grand Arrival, cloneFull users) checked for copies of these bodies.",
              'findings': findings},
          'name_collisions_checked': [
              {'name': a['name'], 'other_definitions': ['none'], 'outcome': 'single actor definition without define_as; the catalog entry has no define_as and matches by exact name, type and subtype'} for a in {x['id']: x for x in A}.values() if a['id'] != 'eternal-bone-giant'] + [
              {'name': 'eternal bone giant', 'other_definitions': ['Necromancer Assemble minion table entry talents/spells/master-of-bones.lua:393 (same name, type, subtype and nice_tile body, no define_as)'], 'outcome': 'the zone leaf is the catalog body; the minion is the same body and wears the same token through the ordinary key'}],
          'kept_native': [],
          'neighbours_kept_native': [
              {'name': 'lost wife (dreams zone, WIFE)', 'reason': "sets subtype = 'bloated horror' on a humanoid/orc base with another name and its own tall PNG"},
              {'name': 'Lord of Skulls (bone giant) minion', 'reason': 'renamed by the talent; leaves the exact-name key'},
              {'name': 'heavy bone giant', 'reason': 'other name, not selected (6.8)'},
              {'name': 'fiery orc wyrmic / icy orc wyrmic', 'reason': 'not selected: three-way tie at 7.4 with orc blood mage; the pair is left for a later batch'}]}
    out = ADDON / 'evidence/monster-batch-v-20260930/source-contracts.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(ev, indent=2, ensure_ascii=False) + '\n')
    evsha = hashlib.sha256(out.read_bytes()).hexdigest()
    for a in A:
        refs = [{'path': p, 'sha256': sha(p), 'role': r, 'note': n} for r, p, n in a['refs']]
        entry = {'asset_id': a['id'], 'native_name': a['name'], 'scope': a['scope'], 'sources': a['srcs'], 'references': refs,
                 'contrast_dimensions': list(a['dims']),
                 'prompt_fields': {'subject': a['subject'], 'contrast': a['contrast'], 'composition': a['comp'] or COMP, 'palette': a['palette']},
                 'kind': 'creature', 'max_attempts': 1, 'gate': 'ready',
                 'gate_reason': f"Exact source identity re-verified directly against game/modules/tome source (name={a['name']}, define_as={a['define_as']}, type={a['type']}/subtype={a['subtype']}, unique={a['unique']}, native_tall={a['native_tall']}); details and hashes in evidence/monster-batch-v-20260930/source-contracts.json. {a['structure']}. Exact catalog entry only, never a whole-subtype mapping.",
                 'render_evidence': [{'path': render, 'sha256': evsha}]}
        packs.setdefault(a['pack'], []).append(entry)
    for n, assets in packs.items():
        p = ADDON / f'art/production/batches/monster-batch-v-{n}.json'
        if p.exists():
            print('exists, skipped', p.name)
            continue
        p.write_text(json.dumps({'schema': 1, 'batch_id': f'monster-batch-v-{n}', 'assets': assets}, indent=2, ensure_ascii=False) + '\n')
        print('wrote', p.name)


if __name__ == '__main__':
    build()
