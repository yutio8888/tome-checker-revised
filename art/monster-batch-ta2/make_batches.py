"""Batch TA-2 town/wilds residents: pinned source contracts and TA-1/UB-2-style
task packs, plus one wiring-only reuse identity (elven archer) with no new art.

Static preparation only: source re-verification, family reference sheets and
ImageGen handoff manifests. No generation, no runtime writes, no git.

The native appearance contract (clothing, held items, silhouette) is the
authority: prompts below were written after viewing each native sprite at 8x
nearest (see refs/native-identities.png), not from the earlier text plan where
it disagreed.

OTA: the plan named `elven archer` as an art asset; coordinator ruling 2 makes
it a wiring-only reuse of the shipped companion-archer token because both native
actors draw the byte-identical PNG npc/humanoid_elf_elven_archer.png.
"""
import hashlib
import importlib.util
import json
import re
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WS = ROOT.parents[2]
D = 'game/modules/tome/data/'
NPC = D + 'gfx/shockbolt/npc/'
ART_REL = 'game/addons/tome-checker-revised/art/monster-batch-ta2/'
EVDIR = 'evidence/monster-batch-ta2-20261001/source-contracts.json'

spec = importlib.util.spec_from_file_location('ae', HERE.parent / 'monster-batch-ae/make_batches.py')
ae = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ae)
sha = ae.sha
STYLE = ae.STYLE
COMP = ae.COMP
DARKFIX = ae.DARKFIX
CHEAT = ae.CHEAT
DISC = ae.DISC

# id, native name, source file, native image, type, subtype, native_tall,
# family, subject, contrast, source line anchor
ROWS = [
 ('human-citizen', "human citizen", 'zones/town-last-hope/npcs.lua',
  'humanoid_human_human_citizen.png', 'humanoid', 'human', False, 'citizens',
  "An older grey-blond human townsman: a plain orange-red BUTTONED sleeveless doublet over a white long-sleeved shirt with a pale shirt-tail below the belt, green trousers and brown shoes. His RIGHT arm (image left) is raised with the open palm turned up in greeting, the other hand rests at his hip; relaxed town-square stance. Warm orange, cream and green cloth, pale skin; broad pale upper-left planes on the shoulder and doublet.",
  "No tool and a raised greeting arm with a buttoned red doublet, versus human-farmer's white tunic and upright pitchfork, halfling-citizen's short body and shawl, and the shipped caravan-merchant (blue robe, wide-brim hat, coin pouch) and cutpurse. Silhouette and clothing, never colour alone."),
 ('halfling-citizen', "halfling citizen", 'zones/town-last-hope/npcs.lua',
  'humanoid_halfling_halfling_citizen.png', 'humanoid', 'halfling', False, 'citizens',
  "A short round HALFLING townsman with dark shoulder-length hair and a slight belly: a grey cloth SHOULDER SHAWL/mantle over a brown leather vest, blue knee-shorts and bare furry feet, both arms hanging relaxed at his sides and empty. Wide low settled stance, oversized head. Grey shawl, brown vest and blue shorts, warm tan skin; broad pale upper-left cloth planes.",
  "Static arms-down pose with no tool, a grey shoulder shawl and blue shorts, versus halfling-gardener's two small hand tools and forward lean, halfling-slinger's overhead swing and the shipped caravan-porter's round pack. Body proportion and shawl, not colour."),
 ('human-farmer', "human farmer", 'zones/town-derth/npcs.lua',
  'humanoid_human_human_farmer.png', 'humanoid', 'human', False, 'citizens',
  "A dark-haired weather-worn human farmer in a plain white short tunic and brown shorts, barefoot; he holds a tall straight wooden three-tine PITCHFORK upright with one hand (image left), the tines up above shoulder height, and stands in a simple farmhand pose. Cream cloth, brown shorts, tan skin; broad pale upper-left tunic planes.",
  "A vertical pitchfork longer than the body plus a plain tunic, versus lumberjack's single lowered felling axe and sleeveless apron, halfling-gardener's short body and small tool pair, and the shipped caravan-porter. Tool and height, not colour."),
 ('halfling-gardener', "halfling gardener", 'zones/town-derth/npcs.lua',
  'humanoid_halfling_halfling_gardener.png', 'humanoid', 'halfling', False, 'citizens',
  "A short round HALFLING gardener with dark hair: a brown leather vest over a cream long-sleeved shirt, olive-green shorts, bare furry feet and a brown belt pouch; he holds small steel PRUNING SHEARS raised in one hand and a small hand RAKE/hoe in the other, leaning slightly forward in a busy tending pose. Brown and cream cloth, green shorts, small bright steel glint; broad pale upper-left planes on the shirt.",
  "Short halfling proportions with TWO small hand tools and a forward tending lean, versus human-farmer's tall upright pitchfork, halfling-citizen's empty arms-down shawl and the shipped caravan-porter. Tool pair and posture, not colour."),
 ('lumberjack', "lumberjack", 'zones/town-lumberjack-village/npcs.lua',
  'humanoid_human_lumberjack.png', 'humanoid', 'human', False, 'citizens',
  "A lean weathered human lumberjack with long dark-brown hair, BARE SHOULDERS and sleeveless arms: a cream/off-white sleeveless linen tunic-apron cinched with a dark belt, green trousers and brown boots; one hand hangs a FELLING AXE with a wooden handle LOW at his side, the steel blade near hip height. Pale linen, olive-green trousers, dark axe head; broad pale upper-left linen planes.",
  "Sleeveless pale apron with bare arms and a single lowered felling axe, versus human-farmer's tunic and vertical pitchfork and the shipped bandit's twin axes in an aggressive crouch and cutpurse. Pose and single axe, not colour."),
 ('halfling-slinger', "halfling slinger", 'zones/town-derth/npcs.lua',
  'humanoid_halfling_halfling_slinger.png', 'humanoid', 'halfling', False, 'citizens',
  "A short round HALFLING caught MID-SWING: both arms are RAISED and a red-brown leather SLING whips in a wide arc overhead with a pale grey stone shot at its end; the other fist is up. Green tunic, blue knee-shorts, a tan leather chest bandolier, brown wrist wraps and bare furry feet, wide-footed action stance. Greens and blue with a tan strap and a bright stone; broad pale upper-left arm planes.",
  "The only dynamic overhead two-arm sling arc in the family, versus the static halfling-citizen, the tending halfling-gardener and the shipped rogue/thief. Outer contour and action pose, not colour."),
 ('dwarven-earthwarden', "dwarven earthwarden", 'zones/town-iron-council/npcs.lua',
  'humanoid_dwarf_dwarven_earthwarden.png', 'humanoid', 'dwarf', False, 'dwarves',
  "A broad BARE-HEADED dwarf with a huge pale-brown beard and brown hair: grey steel PAULDRONS on both shoulders over an earthy olive-brown tunic with a heavy wide belt, brown boots. A LARGE round grey shield with a spiral-ring boss is held forward on the left arm; the right hand hangs open and EMPTY (no weapon). Wide planted stance. Olive-brown cloth, grey steel pauldrons and shield; broad pale upper-left planes.",
  "No helm, no axe and a large round shield-forward silhouette, versus the shipped dwarven-guard (grey helm plus two-handed battleaxe), norgan (hammer, bare chest, no shield) and protector-myssil (full plate plus greatsword). Shield and head treatment, not colour."),
 ('yeek-mindslayer', "yeek mindslayer", 'zones/town-irkkk/npcs.lua',
  'humanoid_yeek_yeek_mindslayer.png', 'humanoid', 'yeek', True, 'yeeks',
  "A TALL pale bone-white furred YEEK with empty dark hollow eye sockets and small pale-blue pupils, wearing an olive-green sash and a loose olive kilt: both arms are crossed in front holding TWO long pale-blue GLOWING BLADES that cross in a wide X above and below the chest. Tall poised psionic stance. Bone-white fur, olive cloth, cool blue blade light; broad pale upper-left fur planes.",
  "Tall crossed-blade X silhouette, versus yeek-psionic's short folded arms and chest gem, the shipped yeek-wayist (white, sash, single sword) and the cyan furless yaech-mindslayer. Height and blade cross, not colour."),
 ('yeek-psionic', "yeek psionic", 'zones/town-irkkk/npcs.lua',
  'humanoid_yeek_yeek_psionic.png', 'humanoid', 'yeek', False, 'yeeks',
  "A SHORT wide pale bone-white furred YEEK with empty dark hollow eye sockets: a brown-tan hooded shoulder mantle, arms folded across the chest cradling a small bright GLOWING RED GEM pendant, a dark-brown kilt and pale legs, squat sturdy stance. Bone-white fur, tan mantle, dark kilt and one crimson gem; broad pale upper-left fur planes.",
  "Short squat body with folded arms and a single crimson chest gem, versus yeek-mindslayer's tall crossed blades and the shipped yaech-psion (violet, floating bubbles). Height and the red gem, not colour."),
 ('thalore-hunter', "thalore hunter", 'zones/town-shatur/npcs.lua',
  'humanoid_thalore_thalore_hunter.png', 'humanoid', 'thalore', False, 'thalore',
  "A green-clad THALORE elf with a pointed LEAF-GREEN HOOD and pointed ears: a leaf-green tunic and leather bracers, both arms DRAWN drawing a wooden longbow with a nocked arrow, a quiver of white-fletched arrows over the shoulder, green leggings and brown boots, alert wide archer stance. Forest greens, leather browns and a pale wood bow; broad pale upper-left cloth planes.",
  "Pointed green hood plus a drawn bow and quiver, versus the gold-armoured vertical-bow elven archer/companion-archer and the shipped berethh (cloaked ranger, no pointed hood). Hood and drawn-bow pose, not colour."),
 ('thalore-wilder', "thalore wilder", 'zones/town-shatur/npcs.lua',
  'humanoid_thalore_thalore_wilder.png', 'humanoid', 'thalore', True, 'thalore',
  "A TALL humanoid whose whole body is OLIVE-GREEN BARK and MOSS with darker bark grooves, a smooth mask-like face and two small amber eye-glows; NO clothing, NO gear, arms slightly out with open palms, legs apart. Wild nature-spirit. Olive and moss greens with lighter moss highlight faces; broad pale upper-left planes so the body reads on the dark disc.",
  "Plant bark-and-moss body with no clothing and no bow, versus thalore-hunter's green cloth, hood and drawn bow, the shipped mindworm (pale crouching starfield) and berethh. Anatomy and gear, not colour."),
 ('elven-sun-mage', "elven sun-mage", 'general/npcs/sunwall-town.lua',
  'humanoid_elf_elven_sun_mage.png', 'humanoid', 'elf', False, 'elves',
  "A TALL elven SUN-MAGE: a long golden-yellow robe under a broad brown-tan shoulder mantle/collar and a wide soft golden-brimmed hat over pale hair, a belt at the waist; both arms are lifted apart and out with open empty hands, a faint painted warm glow at the palms (no weapon, no staff). Narrow upright caster silhouette. Saturated golden-yellow cloth with tan mantle and pale highlights; broad pale upper-left robe planes.",
  "Full golden robe, wide brimmed hat/mantle and raised open arms, versus shalore-rune-master's bare tattooed chest and twin hand orbs, the shipped fillarel-aldaren (closed gold robe and staff) and elven-mage (purple, staff). Robe and arms, not colour."),
 ('shalore-rune-master', "shalore rune master", 'zones/town-elvala/npcs.lua',
  'humanoid_shalore_shalore_rune_master.png', 'humanoid', 'shalore', False, 'elves',
  "A BARE-CHESTED tattooed SHALORE elf with pointed ears and dark hair: dark line tattoos across the chest and arms, a blue patterned KILT/loincloth with a wide blue sash, brown boots; both arms are spread low and out with a small glowing YELLOW-ORANGE ORB floating above each open palm. Compact ritual stance. Dark tan tattooed skin, blue cloth, warm orb light; broad pale upper-left skin planes.",
  "Bare tattooed torso with a kilt and a glowing orb in each hand, versus elven-sun-mage's full golden robe and the shipped robed/corrupt elf casters. Bare shoulders and twin orbs, not colour."),
]

# Wiring-only: no new art. The elven archer and the Companion Archer draw the
# byte-identical native PNG; the resident reuses the shipped companion-archer
# runtime token. The companion-archer entry and token are untouched.
WIRING = dict(
    id='elven-archer', native_name="elven archer",
    source_file='general/npcs/sunwall-town.lua',
    native_image='humanoid_elf_elven_archer.png',
    type='humanoid', subtype='elf',
    reuse_batch='monster-batch-s', reuse_id='companion-archer',
    reuse_master='monster-batch-s/masters/companion-archer-v1.png',
)

FAMILIES = {
    'citizens': ['caravan-merchant', 'caravan-porter', 'lost-merchant', 'cutpurse', 'thief', 'bandit'],
    'yeeks': ['yeek-wayist', 'yaech-hunter', 'yaech-mindslayer', 'yaech-psion', 'yaech-diver', 'slaver'],
    'dwarves': ['dwarven-guard', 'norgan', 'protector-myssil', 'human-sun-paladin'],
    'thalore': ['berethh', 'companion-warrior', 'companion-archer', 'mindworm'],
    'elves': ['companion-archer', 'fillarel-aldaren', 'elven-warrior', 'elven-elite-warrior',
              'elven-mage', 'elven-corruptor', 'elven-cultist', 'elven-blood-mage'],
}
IDS = [r[0] for r in ROWS]


def leaf_block(path, name):
    lines = (WS / (D + path)).read_text().splitlines()
    n = next(i for i, l in enumerate(lines) if 'name = "' + name + '"' in l)
    start = max(i for i in range(n + 1) if lines[i].startswith('newEntity{'))
    end = next((i for i in range(n + 1, len(lines)) if lines[i].startswith('newEntity{')), len(lines))
    return '\n'.join(lines[start:end]), start + 1, end


def default_image(typ, sub, name):
    def clean(s):
        return re.sub('[^a-z0-9]', '_', s.lower())
    return 'npc/' + typ + '_' + clean(sub) + '_' + clean(name) + '.png'


def build():
    identities = []
    for row in ROWS:
        (id_, name, file, png, typ, sub, tall, group, subject, contrast) = row
        leaf, start, end = leaf_block(file, name)
        pins = [ae.src(file, 'name = "' + name + '"')]
        # lumberjack carries the runtime-inert `defined_as` typo, so its exact
        # leaf anchor is pinned explicitly (coordinator ruling 3).
        if id_ == 'lumberjack':
            pins.append(ae.src(file, 'defined_as = "LUMBERJACK"'))
        combined = leaf
        mbase = re.search(r'base\s*=\s*"([^"]+)"', leaf)
        btext = ''
        if mbase:
            bp = file
            bpins = ae.src(bp, 'define_as = "' + mbase.group(1) + '"')
            pins.append(bpins)
            lines = (WS / (D + bp)).read_text().splitlines()
            n = bpins['line'] - 1
            s = max(i for i in range(n + 1) if lines[i].startswith('newEntity{'))
            e = next((i for i in range(n + 1, len(lines)) if lines[i].startswith('newEntity{')), len(lines))
            btext = '\n'.join(lines[s:e])
            combined = leaf + '\n' + btext
        if id_ != 'lumberjack':
            assert 'defined_as' not in combined, (id_, 'typo define_as')
        assert not re.search(r'moddable_tile|add_displays|(?:^|\s)shader\s*=|(?:^|\s)anim\s*=', combined), (id_, 'unsupported visual')
        native = NPC + png
        with Image.open(WS / native) as im:
            size = list(im.size)
        assert size == ([64, 128] if tall else [64, 64]), (id_, size)
        (HERE / 'source').mkdir(exist_ok=True)
        (HERE / 'source' / f'{id_}.lua').write_text(
            '-- Verified leaf and inherited base; source hashes in source-contracts.json\n'
            + '\n'.join(l.rstrip() for l in leaf.splitlines())
            + ('\n-- INHERITED BASE\n' + '\n'.join(l.rstrip() for l in btext.splitlines()) if btext else '') + '\n')
        dimg = default_image(typ, sub, name)
        nice = re.search(r'resolvers\.nice_tile\{[^\n]*\}', leaf)
        explicit = re.search(r'image\s*=\s*"([^"]+)"', leaf)
        structure = (
            ('explicit nice_tile tall body: image="invis.png", add_mos image="npc/' + png
             + '" display_h=2/display_y=-1; native_tall=true admits it (nativeTallImage requires '
             'entry.unique or entry.native_tall).')
            if tall else
            (('explicit image="' + explicit.group(1) + '"' if explicit else
              'default image name from class/NPC.lua:33 (' + dimg + ')') + '; flat 64x64 body.'))
        structure += (' No shader, moddable_tile, anim, add_displays or textures anywhere in leaf/base; '
                      'no auto_classes body writes.')
        identities.append(dict(
            id=id_, native_name=name, source=pins[0], base_source=pins[-1] if mbase else None,
            sources=pins, define_as=None, type=typ, subtype=sub, unique=False,
            native_tall=tall, native_image='npc/' + png, native_image_path=native,
            native_image_sha256=sha(native), native_image_size=size,
            default_image=dimg, explicit_image=(explicit.group(1) if explicit else None),
            image_source=('nice_tile explicit single-body tall image' if tall else
                          ('explicit image= field' if explicit else 'class/NPC.lua:33 default name image')),
            structure=structure, shader=None, moddable_tile=None, anim=None, add_displays=None,
            nice_tile=('explicit single-body tall' if tall else None),
            add_mos=[dict(image='npc/' + png, display_h=2, display_y=-1)] if tall else None,
            leaf_source_lines=[start, end],
            talents=sorted(set(re.findall(r'Talents\.(T_[A-Z0-9_]+)', combined))),
            verdict='READY exact resident identity'))
        if tall:
            identities[-1]['tall_body'] = dict(
                image='invis.png', add_mos=[dict(image='npc/' + png, display_h=2, display_y=-1)],
                catalog_flag='native_tall=true')

    # Wiring-only identity: verified elven archer leaf, no art generation.
    wleaf, wstart, wend = leaf_block(WIRING['source_file'], WIRING['native_name'])
    assert 'subtype = "elf"' in wleaf
    assert 'define_as' not in wleaf
    wsrc = ae.src(WIRING['source_file'], 'name = "elven archer"')
    comp = ae.src('zones/keepsake-meadow/npcs.lua', 'define_as = "BERETHH_ARCHER"')
    wimg = NPC + WIRING['native_image']
    with Image.open(WS / wimg) as im:
        wsize = list(im.size)
    assert wsize == [64, 64], wsize
    reuse_manifest = json.loads((ROOT / 'data/token-manifest.json').read_text())
    reuse_entry = next(a for a in reuse_manifest['assets'] if a['id'] == WIRING['reuse_id'])
    reuse_master = WS / ('game/addons/tome-checker-revised/art/' + WIRING['reuse_master'])
    wiring_ident = dict(
        id=WIRING['id'], native_name=WIRING['native_name'], source=wsrc, base_source=None,
        sources=[wsrc, comp], define_as=None, type=WIRING['type'], subtype=WIRING['subtype'],
        unique=False, native_tall=False, native_image='npc/' + WIRING['native_image'],
        native_image_path=wimg, native_image_sha256=sha(wimg), native_image_size=wsize,
        image_source='class/NPC.lua:33 default name image; byte-identical native PNG to companion-archer',
        structure=('wiring-only: the resident elven archer and the shipped Companion Archer draw the '
                   'byte-identical native PNG npc/humanoid_elf_elven_archer.png, so the resident reuses '
                   'the companion-archer runtime token; no new ImageGen art. The companion-archer entry, '
                   'token and manifest row are unchanged.'),
        shader=None, moddable_tile=None, anim=None, add_displays=None,
        leaf_source_lines=[wstart, wend], talents=[],
        reuse=dict(batch=WIRING['reuse_batch'], id=WIRING['reuse_id'],
                   master=WIRING['reuse_master'], master_sha256=sha(reuse_master),
                   runtime_sha256=reuse_entry['runtime_sha256']),
        verdict='WIRING-ONLY exact name+type/subtype entry reusing the companion-archer token')

    auxiliary = [
        ae.src('class/NPC.lua', '-- Grab default image name', root='game/modules/tome/'),
        ae.src('resolvers.lua', 'function resolvers.calc.nice_tile', root='game/modules/tome/'),
        ae.src('zones/arena-unlock/npcs.lua', 'define_as = "SLINGER"'),
        ae.src('talents/chronomancy/anomalies.lua', 'm.name = _t"human farmer"'),
        ae.src('talents/chronomancy/anomalies.lua', 'm.name = _t"halfling gardener"'),
        ae.src('talents/chronomancy/anomalies.lua', 'm.name = _t"shalore scribe"'),
        ae.src('talents/misc/races.lua', 'name = _t"yeek mindslayer"'),
        ae.src('zones/town-lumberjack-village/npcs.lua', 'defined_as = "LUMBERJACK"'),
    ]
    findings = [
        'All thirteen art identities and the wiring-only elven archer are non-unique with no runtime '
        'define_as. Each name has exactly one actor leaf across data/ (grepped), so exact '
        'name+type+subtype+image identity is sufficient and no alias/variant rule is needed.',
        'yeek mindslayer and thalore wilder are explicit nice_tile 64x128 bodies (image="invis.png", '
        'add_mos image/display_h=2/display_y=-1); both carry native_tall=true because nativeTallImage '
        'requires entry.unique or entry.native_tall. The other eleven art identities are flat 64x64.',
        'lumberjack opens with `defined_as = "LUMBERJACK"` (town-lumberjack-village/npcs.lua:70), a typo '
        'for define_as, so no runtime define_as is bound; the entry matches on name+type/subtype only '
        '(coordinator ruling 3) and a pinning test records the typo.',
        'halfling slinger: only the Derth resident (town-derth/npcs.lua:70-71, no define_as) is mapped. '
        'The Arena copy (arena-unlock/npcs.lua:70-71) binds define_as="SLINGER" and is spawned by '
        'arena-unlock/zone.lua:41; because the entry has define_as nil it fails the exact-identity bind '
        'and stays native (coordinator ruling 1).',
        'human farmer and halfling gardener are also spawned by the Chronomancy anomaly '
        '(anomalies.lua:584-597) with the same name, type, subtype and PNG; they match the ordinary '
        'exact-identity path and wear the same token. The different-name "shalore scribe" '
        '(anomalies.lua:598-604) reuses the rune-master PNG but keeps native art (coordinator rulings 4/6), '
        'as do the different-name gem crafter (YEEK_STORE_GEM) and the YEEK_STORE_* illusion NPCs.',
        'The Wayist summon (talents/misc/races.lua:989-991) constructs a "yeek mindslayer" with the same '
        'type/subtype and the same nice_tile tall body; it satisfies nativeTallImage and wears the same '
        'token (coordinator ruling 5).',
        'elven archer (general/npcs/sunwall-town.lua:64-65, humanoid/elf, no define_as) and Companion '
        'Archer (keepsake-meadow/npcs.lua:296-297, define_as="BERETHH_ARCHER", subtype thalore) draw the '
        'byte-identical PNG npc/humanoid_elf_elven_archer.png. The resident is a wiring-only catalog entry '
        'that reuses the shipped companion-archer token; the companion-archer entry and token are '
        'unchanged (coordinator ruling 2).',
        'No leaf or base sets shader, moddable_tile, anim, add_displays or textures. The earthwarden may '
        'sustain T_BODY_OF_STONE (talents/spells/earth.lua:112) and the sun-mage births with '
        'T_CHANT_OF_LIGHT (talents/celestial/chants.lua:247); both write only _isshaderaura add_mos '
        'bookkeeping (earthwarden) or particles (both), never actor.shader, so appearance() stays valid '
        '(coordinator ruling 9).',
    ]
    ev = dict(
        schema=1,
        task='monster-batch-ta2: second town-resident batch, thirteen new drawings plus one wiring-only '
             'reuse (elven archer); static source re-verification only, no game launch.',
        identities=identities + [wiring_ident],
        art_ids=IDS,
        wiring_only=[wiring_ident['id']],
        new_ids_not_in_catalog_before_this_batch=IDS + [wiring_ident['id']],
        auxiliary_sources=auxiliary,
        kept_native=[
            'halfling slinger (arena SLINGER, define_as)',
            'shalore scribe (anomaly, different name)',
            'gem crafter (YEEK_STORE_GEM, different name)',
            'YEEK_STORE_* illusion NPCs (different names)',
        ],
        summons_and_same_body_copies=dict(
            method='Source scan of NPC leaves, bases, make_escort, talents, timed_effects, maps/vaults and zones for name/PNG hits.',
            findings=findings),
        runtime_mutation_scan=dict(
            method='Read each leaf and inherited base; scanned talents, timed_effects, zones and maps for image/type/subtype/shader/add_mos/moddable_tile/add_displays/replace_display writes.',
            hits_in_batch=[],
            auto_classes_review=[dict(identity='all leaves', **{'class': 'none'},
                                      finding='No auto_classes in this batch')],
            sustains_at_birth_review=[
                dict(identity='dwarven earthwarden / elven sun-mage',
                     note='T_BODY_OF_STONE uses addShaderAura (an _isshaderaura add_mos entry, no '
                          'actor.shader); T_CHANT_OF_LIGHT adds a golden_shield particle only. appearance() '
                          'ignores aura bookkeeping and does not test particles.'),
                dict(identity='all other leaves', sustained=[],
                     note='No resolvers.sustains_at_birth')]),
    )
    out = ROOT / EVDIR
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(ev, ensure_ascii=False, indent=2) + '\n')

    # Family reference sheets from shipped tokens.
    families = {}
    for group, gids in FAMILIES.items():
        c = Image.new('RGBA', (3 * 128, ((len(gids) + 2) // 3) * 128))
        for n, i in enumerate(gids):
            c.alpha_composite(Image.open(ROOT / 'data/gfx/tokens' / f'{i}.png').convert('RGBA'), (n % 3 * 128, n // 3 * 128))
        p = HERE / 'refs' / f'{group}.png'
        p.parent.mkdir(exist_ok=True)
        c.save(p)
        families[group] = dict(path=ART_REL + 'refs/' + p.name, sha256=sha(ART_REL + 'refs/' + p.name), role='family',
                               note='Shipped siblings row order: ' + ', '.join(gids) + '. Match tabletop language and stay structurally distinct; do not copy their anatomy.')

    # Native identity contact sheet (viewing aid) at 3x nearest.
    c = Image.new('RGBA', (4 * 220, 5 * 420), (46, 50, 46, 255))
    draw = ImageDraw.Draw(c)
    for n, i in enumerate(identities):
        im = Image.open(WS / i['native_image_path']).convert('RGBA')
        im = im.resize((im.width * 3, im.height * 3), Image.Resampling.NEAREST)
        x, y = n % 4 * 220, n // 4 * 420
        draw.text((x + 2, y + 2), i['id'], fill='white')
        c.alpha_composite(im, (x + 20, y + 18))
    c.save(HERE / 'refs/native-identities.png')

    # ImageGen task packs, three art assets per pack.
    packs = {}
    for row, i in zip(ROWS, identities):
        id_, name, file, png, typ, sub, tall, group, subject, contrast = row
        refs = [
            dict(path=STYLE, sha256=sha(STYLE), role='style', note='Approved neutral disc/camera/light only; do not copy its creature.'),
            dict(path=NPC + png, sha256=sha(NPC + png), role='identity', note='Inspected exact native body ' + str(i['native_image_size']) + '. Paint this clothing, held items and silhouette.'),
            families[group],
        ]
        a = dict(
            asset_id=id_, native_name=name,
            scope='TA-2 town/wilds resident; ' + i['source']['path'] + ':' + str(i['source']['line']),
            sources=i['sources'] + auxiliary,
            references=refs,
            contrast_dimensions=['silhouette', 'value', 'hue'],
            prompt_fields=dict(
                subject=subject + CHEAT,
                contrast=contrast + ' No faction rings, health, shield, rank marks, selection, text or numbers.',
                composition=COMP + (DARKFIX if id_ in ('thalore-wilder',) else ''),
                palette='Mid-light body masses and broad pale upper-left highlights, thin bright rim. ' + DISC + ' Keep the whole disc at reference lightness; no cast shadow or colour spill.'),
            kind='creature', max_attempts=2, gate='ready',
            gate_reason=i['structure'] + ' Static source contract only; see ' + EVDIR,
            render_evidence=[dict(path='game/addons/tome-checker-revised/' + EVDIR, sha256=hashlib.sha256(out.read_bytes()).hexdigest())])
        packs.setdefault(IDS.index(id_) // 3 + 1, []).append(a)
    for n, assets in packs.items():
        p = ROOT / f'art/production/batches/monster-batch-ta2-{n}.json'
        if not p.exists():
            p.write_text(json.dumps(dict(schema=1, batch_id=f'monster-batch-ta2-{n}', assets=assets), ensure_ascii=False, indent=2) + '\n')

    # Wiring-only task descriptor (no prompt, no pack, no call).
    (HERE / 'wiring-only.json').write_text(json.dumps(dict(
        id=wiring_ident['id'], native_name=wiring_ident['native_name'], type=wiring_ident['type'],
        subtype=wiring_ident['subtype'], sources=wiring_ident['sources'],
        native_image=wiring_ident['native_image'],
        native_image_sha256=wiring_ident['native_image_sha256'],
        reuse=wiring_ident['reuse'], note=wiring_ident['structure']), ensure_ascii=False, indent=2) + '\n')

    # Official Chinese names: record the exact mod-tome.lua line for each identity.
    names_path = '/workspace/tome4-chinese-translation/mod-tome.lua'
    source = Path(names_path)
    names = {'path': names_path, 'names': []}
    if source.is_file():
        lines = source.read_text(encoding='utf-8').splitlines()
        pattern = re.compile(r'^\s*t\(\s*"' + r'((?:[^"\\]|\\.)*)"\s*,\s*"((?:[^"\\]|\\.)*)"')
        for i in identities + [wiring_ident]:
            hits = []
            for n, line in enumerate(lines, 1):
                m = pattern.match(line)
                if m and m.group(1) == i['native_name']:
                    hits.append(dict(source_line=n, official_line=line))
            names['names'].append(dict(id=i['id'], native_name=i['native_name'], hits=hits))
    (HERE / 'official-names.json').write_text(json.dumps(names, ensure_ascii=False, indent=2) + '\n')

    if not (HERE / 'selected-masters.json').exists():
        choices = {i: f'masters/{i}-v1.png' for i in IDS}
        choices[wiring_ident['id']] = '../' + WIRING['reuse_master']
        (HERE / 'selected-masters.json').write_text(json.dumps(choices, indent=2) + '\n')
    if not (HERE / 'final-admission.json').exists():
        (HERE / 'final-admission.json').write_text(json.dumps(
            dict(accepted_ids=IDS + [wiring_ident['id']], art_ids=IDS, wiring_only=[wiring_ident['id']],
                 native={}, art_review='pending static 48/64/96 review', body_minimum=65.0,
                 descriptive_floor_baseline=45.0, calls=0, waivers=[]), indent=2) + '\n')
    admitted = json.loads((HERE / 'final-admission.json').read_text())['accepted_ids']
    (HERE / 'catalog.json').write_text(json.dumps([dict(id=i) for i in admitted], indent=2) + '\n')
    (HERE / 'catalog.js').write_text('window.monsterCatalog = ' + (HERE / 'catalog.json').read_text().strip() + ';\n')
    print('TA-2 preparation complete:', len(identities), 'art + 1 wiring;', len(packs), 'packs')


if __name__ == '__main__':
    build()
