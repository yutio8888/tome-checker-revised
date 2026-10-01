"""UB-1 native-tall unique/boss batch: pinned source contracts and AF/UA-style
task packs. Static preparation only: source re-verification, family reference
sheets and ImageGen handoff manifests. No generation, no runtime writes, no git.
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
ART_REL = 'game/addons/tome-checker-revised/art/monster-batch-ub1/'
EVDIR = 'evidence/monster-batch-ub1-20261001/source-contracts.json'

spec = importlib.util.spec_from_file_location('ae', HERE.parent / 'monster-batch-ae/make_batches.py')
ae = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ae)
sha = ae.sha
STYLE = ae.STYLE
COMP = ae.COMP
DARKFIX = ae.DARKFIX
CHEAT = ae.CHEAT
DISC = ae.DISC

# id, native name, source file (under data/), base file (or None), image, define_as,
# define_as_alias, type, subtype, family, subject, contrast
ROWS = [
 ('high-sun-paladin-aeryn', "High Sun Paladin Aeryn", 'zones/high-peak/npcs.lua', None,
  'humanoid_human_high_sun_paladin_aeryn.png', 'HIGH_SUN_PALADIN_AERYN', None,
  'humanoid', 'human', 'sun-paladins',
  "A tall heroic woman in bright polished silver full plate with warm gold edging and a long crimson cloak sweeping down one side; long pale blonde hair uncovered and calm face. She holds a long straight knight's sword PERFECTLY UPRIGHT in her right hand, the blade vertical beside her head, her left hand open and empty at her hip; no shield, no hammer. Full-height upright stance with both feet planted, broad pale upper-left plates and a thin bright rim; the crimson cloak is the only warm accent.",
  "Aeryn is a full-height slender upright figure with an upright sword and an EMPTY off-hand (no shield and no hammer), versus the shipped gold human sun-paladin token with its huge round sun-disc shield and forward war-hammer, and versus the white-gold cape-and-mace Rodmour. Distinguish by tall height, the vertical sword line and the absent shield, never by hue alone; the Fallen variant is near-black and blood-red with a centred two-handed greatsword."),
 ('fallen-sun-paladin-aeryn', "Fallen Sun Paladin Aeryn", 'zones/high-peak/npcs.lua', None,
  'humanoid_human_fallen_sun_paladin_aeryn.png', 'FALLEN_SUN_PALADIN_AERYN', None,
  'humanoid', 'human', 'sun-paladins',
  "A tall tragic woman in blackened full plate with dull oxblood-red trim and thin glowing crimson seams, a long tattered dark-red cloak trailing asymmetrically to one side; loose pale blonde hair and a gaunt hollow-eyed face. She grips a great TWO-HANDED blood-dark greatsword PERFECTLY UPRIGHT in the centre of her chest with BOTH hands on the hilt, the blade vertical down the body centre-line, no shield. Slightly hunched forward with a heavy planted stance and torn asymmetrical cloak.",
  "The Fallen Aeryn is defined by a centred TWO-HANDED vertical greatsword (both hands on the hilt), a forward hunch and a tattered one-sided cloak, versus the High Aeryn's calm upright one-handed off-side sword with a free open hand. Same character, different pose structure and crimson-black palette; structure must separate them at 48px, not colour alone. Distinct from the broad dark Aluin knight by being a slender woman."),
 ('caldizar', "Caldizar", 'zones/shertul-fortress-caldizar/npcs.lua', 'general/npcs/shertul.lua',
  'horror_sher_tul_caldizar.png', 'CALDIZAR', 'CALDIZAR_AOADS',
  'horror', "sher'tul", 'shertul',
  "A massive ancient seated Sher'Tul: a low broad mound wrapped in a pale ivory-grey ceremonial mantle, a single squat rounded head bump rising low between the shoulders bearing a smooth mauve-violet crown-disc and a thin violet halo ring; a nest of long tapered magenta-purple tentacles splaying outward and downward around the base; a vertical fountain of fine golden motes rising above the head. No face, eyes or arms.",
  "Caldizar is a low seated pale-ivory mound with a distinct mauve head-disc, a mantle, downward magenta tentacles and a golden mote fountain, versus the shipped Fortress Shadow token's flat radial cyan-teal dome with a bright central core and no head. Structure (head bump, robe, mote column) and palette (ivory/magenta/gold vs cyan/teal), never a recolour. This one art covers BOTH native define sites (CALDIZAR and CALDIZAR_AOADS), whose sprites are byte-identical."),
 ('chronolith-twin', "Chronolith Twin", 'zones/temporal-rift/npcs.lua', 'general/npcs/horror_temporal.lua',
  'horror_temporal_cronolith_twin.png', 'CHRONOLITH_TWIN', None,
  'horror', 'temporal', 'temporal-horrors',
  "A temporal horror: a narrow upright body in a pale ivory floor-length stitched robe, a blue-violet elongated head with large glossy black insectile eyes, and SIX long thin blue arms -- three per side -- spread WIDE in an open symmetric radial fan, the upper pair raised high above the shoulders, the middle pair straight out to the sides, the lower pair angled down and out; long thin blue legs beneath the robe hem. All six arms clearly separated and visible.",
  "The Twin is upright with all six blue arms spread in a wide open symmetric fan and the head held high, versus the shipped temporal stalker's low dark blade-and-cloak mass. It must be the structural opposite of the Clone (open fan vs closed folded bundle) so the pair never merges at 48px."),
 ('chronolith-clone', "Chronolith Clone", 'zones/temporal-rift/npcs.lua', 'general/npcs/horror_temporal.lua',
  'horror_temporal_cronolith_clone.png', 'CHRONOLITH_CLONE', None,
  'horror', 'temporal', 'temporal-horrors',
  "The same temporal horror HUNCHED and closed: a compact forward-curled body in the same pale ivory stitched robe, the blue-violet head lowered and pulled down between raised shoulders, and all six thin blue arms FOLDED CLOSE across the chest and belly in three overlapping horizontal bands, elbows pressed to the ribs so no arm reaches outside the body outline; short blue legs tucked under the hem. A bundled, self-embracing silhouette.",
  "The Clone is a hunched closed bundle with all six arms wrapped across its own chest, versus the Twin's upright wide radial arm fan; the two must differ by pose and outline at 48px, not by colour. Both still read as six-armed robed temporal horrors and stay distinct from the low dark temporal stalker."),
 ('temporal-defiler', "Temporal Defiler", 'zones/town-point-zero/npcs.lua', None,
  'horror_temporal_temporal_defiler.png', 'TEMPORAL_DEFILER', None,
  'horror', 'temporal', 'temporal-horrors',
  "A slender upright insectile horror in glossy violet-magenta chitin with mid-light lavender highlights, a very narrow ribbed hourglass waist between a small narrow thorax and long thin legs, and a small sharp bony head with tiny dark eyes. TWO very long curved bone-cream scythe-blades replace the forelimbs and are raised HIGH at chest height as a symmetric pair; a pair of short lower claw-limbs is tucked in against the waist.",
  "The Defiler is a tall narrow hourglass with two long raised bone scythe-claws and a tiny head, versus the shipped temporal stalker's low broad dark blade mass and the six-armed robed chronolith pair. Its twin raised scythes and pinched waist are the structural cue, not the magenta colour."),
 ('corrupted-daelach', "Corrupted Daelach", 'zones/valley-moon/npcs.lua', None,
  'demon_major_corrupted_daelach.png', 'CORRUPTED_DAELACH', None,
  'demon', 'major', 'demons',
  "A huge demon of shadow and fire: two enormous broad black leathery bat wings spread WIDE to either side and raised above the shoulders, a molten amber-orange body with a glowing chest core, a low horned demon head set forward between raised shoulders with a small pale-eyed face and burning mouth, arms ending in black smoking claws, and a short black tail. Fire stays on the body; no ground flames, no smoke curtain.",
  "The Corrupted Daelach has OPEN wings spread wide and a molten amber-orange fire body, versus the shipped daelach token's magenta hunched demon with FOLDED wings and a pink aura. Wing geometry (wide open vs folded) and the fire palette are the structural cue; also distinct from the brown spiky Lithfengel and the grey smoke Kryl-Feijan."),
 ('supreme-archmage-linaniil', "Linaniil, Supreme Archmage of Angolwen", 'zones/town-angolwen/npcs.lua', None,
  'humanoid_human_linaniil_supreme_archmage.png', 'SUPREME_ARCHMAGE_LINANIIL', None,
  'humanoid', 'human', 'archmages',
  "A tall regal sorceress with very long straight copper-red hair, pale skin and an intense forward stare; she wears a long flowing ivory-white silk robe with a slashed front panel over a pale inner under-robe and a long dark waist sash, bare arms. She holds a tall ornate silver-knobbed staff vertically in her right hand with its finial above her head, the left hand hanging open at her side. Slender full-height upright stance.",
  "Linaniil is a full-height unhooded woman in a pale ivory robe with long copper-red hair and a tall ornate staff, versus the shipped grey hooded skeletal Necromancer and the purple hooded bearded Elven Mage. Bare head, hair colour, robe and staff distinguish her; not a colour swap of either."),
 ('archmage-tarelion', "Archmage Tarelion", 'zones/town-angolwen/npcs.lua', None,
  'humanoid_shalore_archmage_tarelion.png', 'TARELION', None,
  'humanoid', 'shalore', 'archmages',
  "A tall calm shalore archmage: a slender elf with pale ivory skin, long silver-white hair, pointed ears, and a deep sapphire-blue layered robe with a tall stiff standing collar, broad shoulders, pale blue-white inner panels and wide draped sleeves. Both arms are held relaxed at his sides with open empty hands; no staff, no weapon. Full-height upright serene stance.",
  "Tarelion is a full-height unarmoured elf in a deep blue layered robe with a tall collar and no staff, versus the purple hooded bearded Elven Mage, the blue armoured sword-carrying Rhaloren Inquisitor and the grey hooded Necromancer. Collar, empty hands and blue robe are the cue. Distinct from Linaniil (ivory robe, staff, red hair, female)."),
]

FAMILIES = {
    'sun-paladins': ['human-sun-paladin', 'high-sun-paladin-rodmour', 'aluin-the-fallen', 'argoniel', 'elandar'],
    'shertul': ['fortress-shadow'],
    'temporal-horrors': ['temporal-stalker', 'dredgling', 'dredge', 'void-horror', 'telugoroth', 'teluvorta'],
    'archmages': ['elven-mage', 'rhaloren-inquisitor', 'necromancer', 'fillarel-aldaren', 'grand-corruptor', 'elven-blood-mage'],
    'demons': ['daelach', 'lithfengel', 'kryl-feijan', 'uruivellas', 'champion-of-urh-rok', 'forge-giant'],
}
IDS = [r[0] for r in ROWS]


def leaf_block(path, name):
    lines = (WS / (D + path)).read_text().splitlines()
    n = next(i for i, l in enumerate(lines) if 'name = "' + name + '"' in l)
    start = max(i for i in range(n + 1) if lines[i].startswith('newEntity{'))
    end = next((i for i in range(n + 1, len(lines)) if lines[i].startswith('newEntity{')), len(lines))
    return '\n'.join(lines[start:end]), start + 1, end


def build():
    identities = []
    for id_, name, file, bfile, png, define, alias, typ, sub, group, subject, contrast in ROWS:
        leaf, start, end = leaf_block(file, name)
        base = re.search(r'base\s*=\s*"([^"]+)"', leaf)
        pins = [ae.src(file, 'name = "' + name + '"')]
        btext = ''
        if base:
            bp = bfile or file
            pins.append(ae.src(bp, 'define_as = "' + base[1] + '"'))
            lines = (WS / (D + bp)).read_text().splitlines()
            n = pins[-1]['line'] - 1
            s = max(i for i in range(n + 1) if lines[i].startswith('newEntity{'))
            e = next((i for i in range(n + 1, len(lines)) if lines[i].startswith('newEntity{')), len(lines))
            btext = '\n'.join(lines[s:e])
        combined = leaf + btext
        assert not re.search(r'moddable_tile|add_displays|shader\s*=', combined), (id_, 'unsupported visual')
        native = NPC + png
        with Image.open(WS / native) as im:
            size = list(im.size)
        assert size == [64, 128], (id_, size, 'UB-1 is native-tall only')
        (HERE / 'source').mkdir(exist_ok=True)
        content = ('-- Verified leaf and inherited base; source hashes in source-contracts.json\n'
                   + '\n'.join(l.rstrip() for l in leaf.splitlines())
                   + '\n-- INHERITED BASE\n' + '\n'.join(l.rstrip() for l in btext.splitlines()))
        (HERE / 'source' / f'{id_}.lua').write_text(content.rstrip() + '\n')
        nice = re.search(r'resolvers\.nice_tile\{[^\n]*\}', leaf)
        structure = (
            'Exactly one native-tall body: image="invis.png" with one add_mos entry '
            '{image=' + 'npc/' + png + ', display_h=2, display_y=-1}; unique=true admits it without a '
            'native_tall flag (Walrog/Kyless/Walrog precedent). No shader, moddable_tile, anim or '
            'add_displays anywhere in leaf/base. auto_classes, where present, only roll talents, never '
            'the drawn body.')
        identities.append(dict(
            id=id_, native_name=name, source=pins[0], base_source=pins[1] if base else None,
            sources=pins, define_as=define, define_as_alias=alias, type=typ, subtype=sub, unique=True,
            native_tall=True, native_image='npc/' + png, native_image_path=native,
            native_image_sha256=sha(native), native_image_size=size,
            default_image='npc/' + typ + '_' + sub + '_' + re.sub('[^a-z0-9]', '_', name.lower()) + '.png',
            default_image_exists=(WS / (D + 'gfx/shockbolt/' + 'npc/' + typ + '_' + sub + '_' + re.sub('[^a-z0-9]', '_', name.lower()) + '.png')).exists(),
            image_source='nice_tile explicit single-body tall image' if 'add_mos' in leaf else 'nice_tile{tall=true} shorthand (R20 probe: resolves to one add_mos body)',
            structure=structure, shader=None, moddable_tile=None, anim=None, add_displays=None,
            nice_tile=(nice.group(0) if nice else None),
            add_mos=[dict(image='npc/' + png, display_h=2, display_y=-1)],
            leaf_source_lines=[start, end],
            talents=sorted(set(re.findall(r'Talents\.(T_[A-Z0-9_]+)', combined))),
            verdict='READY exact unique tall identity'))

    # Secondary define sites / same-name constructs that the same token must serve.
    high_gom = ae.src('zones/town-gates-of-morning/npcs.lua', 'name = "High Sun Paladin Aeryn"')
    ao = ae.src('zones/high-peak/npcs.lua', 'name = "Caldizar"')
    auxiliary = [
        ae.src('class/NPC.lua', '-- Grab default image name', root='game/modules/tome/'),
        ae.src('resolvers.lua', 'function resolvers.calc.nice_tile', root='game/modules/tome/'),
    ]
    probe = {'path': 'game/addons/tome-checker-revised/art/monster-batch-ub1/refs/tarelion-probe.md',
             'sha256': sha('game/addons/tome-checker-revised/art/monster-batch-ub1/refs/tarelion-probe.md')}
    for ident in identities:
        if ident['id'] == 'high-sun-paladin-aeryn':
            ident['sources'].append(high_gom)
            ident['secondary_define_site'] = 'zones/town-gates-of-morning/npcs.lua binds the same name/define_as/PNG; one token serves both.'
        if ident['id'] == 'caldizar':
            ident['sources'].append(ao)
            ident['secondary_define_site'] = 'zones/high-peak/npcs.lua binds CALDIZAR_AOADS to the byte-identical sprite; the single shared token serves both via shared_name + a second bound define_as.'

    findings = [
        'All nine leaves are unique native-tall bodies (64x128). Eight use an explicit nice_tile{image="invis.png", add_mos={{...display_h=2, display_y=-1}}}; Tarelion uses the {tall=true} shorthand, live-probed in the isolated fixture (R20) to resolve to image=invis.png plus one add_mos body npc/humanoid_shalore_archmage_tarelion.png, display_h=2, display_y=-1, no actor shader.',
        'High Sun Paladin Aeryn is defined twice (zones/high-peak/npcs.lua:316 rank 5, zones/town-gates-of-morning/npcs.lua:25 rank 4). Both share name, define_as HIGH_SUN_PALADIN_AERYN and the same PNG, so one token serves both; unique differs only as the truthy marker string vs true and is not part of the identity key.',
        'Caldizar is defined twice (shertul-fortress-caldizar CALDIZAR, high-peak CALDIZAR_AOADS) with byte-identical art and the same base BASE_NPC_SHERTUL. Coordinator ruling 1 grants ONE shared token: a single catalog entry bound to CALDIZAR with a second bound define_as CALDIZAR_AOADS (shared_name + composite name+define_as machinery, AG precedent).',
        'No leaf or base sets shader, moddable_tile, anim, add_displays or textures. Aeryn leaves carry auto_classes (Sun Paladin talent selection) which never writes the drawn body, and High Aeryn additionally has never_anger/move_others; these are gameplay fields only.',
        'No talent, timed effect, map/vault or zone constructor renames or copies these nine identities. Chronolith Twin/Clone build a linked brother reference (twin_take_hit) but are separate leaves with separate PNGs and their own bodies.',
        'Neither Chronolith nor the other leaves has same-body summons, so no name_aliases, image_aliases, body_aliases or sameBodyVariant entries are added for UB-1. Random-boss / temporal-clone paths keep their existing behaviour.',
    ]
    ev = dict(
        schema=1,
        task='monster-batch-ub1: second uniques/bosses batch, nine native-tall bodies; static source re-verification only, no game launch.',
        identities=identities,
        new_ids_not_in_catalog_before_this_batch=IDS,
        auxiliary_sources=auxiliary,
        shared_token=dict(
            method='R14/R17 source comparison and coordinator ruling 1.',
            findings=['CALDIZAR and CALDIZAR_AOADS use the identical file npc/horror_sher_tul_caldizar.png; one token is bound to both define_as values.'],
        ),
        summons_and_same_body_copies=dict(
            method='Source scan of NPC leaves, bases, talents, timed_effects, maps/vaults and zones for name/PNG hits.',
            findings=findings),
        kept_native=[],
        runtime_mutation_scan=dict(
            method='Read each leaf and inherited base; scanned talents, timed_effects and zones for image/type/subtype/shader/add_mos/moddable_tile/add_displays/replace_display writes.',
            hits_in_batch=[],
            auto_classes_review=[dict(identity='High/Fallen Sun Paladin Aeryn', **{'class': 'Sun Paladin'},
                                      finding='auto_classes roll class talents at level-up; they never touch the displayed body.'),
                                 dict(identity='all other leaves', **{'class': 'none'}, finding='No auto_classes')],
            sustains_at_birth_review=[dict(identity='High/Fallen Sun Paladin Aeryn',
                                           sustained=['Chant of Fortress', 'Barrier', 'Weapon of Light', 'Healing Light',
                                                      'Crusade', 'Shield of Light', 'Second Life', 'Bathe in Light',
                                                      'Providence', 'Thick Skin'],
                                           note='resolvers.sustains_at_birth only enables native sustains; none sets image, shader or add_mos.'),
                                      dict(identity='Caldizar / Chronolith / Defiler / Daelach / Linaniil / Tarelion',
                                           sustained=[], note='No resolvers.sustains_at_birth body writes.')]),
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

    # Native identity contact sheet (viewing aid).
    c = Image.new('RGBA', (3 * 220, 4 * 320), (46, 50, 46, 255))
    draw = ImageDraw.Draw(c)
    for n, i in enumerate(identities):
        im = Image.open(WS / i['native_image_path']).convert('RGBA')
        im = im.resize((128, 256), Image.Resampling.NEAREST)
        x, y = n % 3 * 220, n // 3 * 320
        draw.text((x + 2, y + 2), i['id'], fill='white')
        c.alpha_composite(im, (x + 40, y + 24))
    c.save(HERE / 'refs/native-identities.png')

    # ImageGen task packs, three assets per pack.
    packs = {}
    for row, i in zip(ROWS, identities):
        id_, name, file, bfile, png, define, alias, typ, sub, group, subject, contrast = row
        refs = [
            dict(path=STYLE, sha256=sha(STYLE), role='style', note='Approved neutral disc/camera/light only; do not copy its creature.'),
            dict(path=NPC + png, sha256=sha(NPC + png), role='identity', note='Inspected exact native body ' + str(i['native_image_size']) + '.'),
            families[group],
        ]
        a = dict(
            asset_id=id_, native_name=name,
            scope='UB-1 native-tall unique/boss; ' + i['source']['path'] + ':' + str(i['source']['line']),
            sources=i['sources'] + auxiliary,
            references=refs,
            contrast_dimensions=['silhouette', 'value', 'hue'],
            prompt_fields=dict(
                subject=subject + CHEAT,
                contrast=contrast + ' No faction rings, health, shield, rank marks, selection, text or numbers.',
                composition=COMP + DARKFIX,
                palette='Mid-light body masses and broad pale upper-left highlights, thin bright rim. ' + DISC + ' Keep the whole disc at reference lightness; no cast shadow or colour spill.'),
            kind='creature', max_attempts=2, gate='ready',
            gate_reason=i['structure'] + ' Static source contract only; see ' + EVDIR,
            render_evidence=[dict(path='game/addons/tome-checker-revised/' + EVDIR, sha256=hashlib.sha256(out.read_bytes()).hexdigest())]
            + ([probe] if id_ == 'archmage-tarelion' else []))
        packs.setdefault(IDS.index(id_) // 3 + 1, []).append(a)
    for n, assets in packs.items():
        p = ROOT / f'art/production/batches/monster-batch-ub1-{n}.json'
        if not p.exists():
            p.write_text(json.dumps(dict(schema=1, batch_id=f'monster-batch-ub1-{n}', assets=assets), ensure_ascii=False, indent=2) + '\n')

    # Official Chinese names: record the exact mod-tome.lua line for each identity.
    names_path = '/workspace/tome4-chinese-translation/mod-tome.lua'
    source = Path(names_path)
    names = {'path': names_path, 'names': []}
    if source.is_file():
        lines = source.read_text(encoding='utf-8').splitlines()
        pattern = re.compile(r'^\s*t\(\s*"' + r'((?:[^"\\]|\\.)*)"\s*,\s*"((?:[^"\\]|\\.)*)"')
        for i in identities:
            hits = []
            for n, line in enumerate(lines, 1):
                m = pattern.match(line)
                if m and m.group(1) == i['native_name']:
                    hits.append(dict(source_line=n, official_line=line))
            names['names'].append(dict(id=i['id'], native_name=i['native_name'], hits=hits))
    (HERE / 'official-names.json').write_text(json.dumps(names, ensure_ascii=False, indent=2) + '\n')

    if not (HERE / 'final-admission.json').exists():
        (HERE / 'final-admission.json').write_text(json.dumps(
            dict(accepted_ids=IDS, native={}, art_review='pending static 48/64/96 review',
                 body_minimum=65.0, descriptive_floor_baseline=45.0, calls=0,
                 selected_masters=len(IDS), waivers=[]), indent=2) + '\n')
    admitted = json.loads((HERE / 'final-admission.json').read_text())['accepted_ids']
    (HERE / 'catalog.json').write_text(json.dumps([dict(id=i) for i in admitted], indent=2) + '\n')
    (HERE / 'catalog.js').write_text('window.monsterCatalog = ' + (HERE / 'catalog.json').read_text().strip() + ';\n')
    print('UB-1 preparation complete:', len(identities), 'identities,', len(packs), 'packs')


if __name__ == '__main__':
    build()
