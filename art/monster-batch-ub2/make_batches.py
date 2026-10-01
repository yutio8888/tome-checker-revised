"""UB-2 flat 64x64 story/city/boss identities: pinned source contracts and
TA-1/UB-1-style task packs, plus one wiring-only reuse identity (Ben Cruthdar,
the Cursed) with no new art. Static preparation only: source re-verification,
family reference sheets and ImageGen handoff manifests. No generation, no
runtime writes, no git.

The native appearance contract (clothing, armour, held items, silhouette) is the
authority: prompts below were written after viewing each native sprite at 4x-7x
nearest (see refs/), not from the earlier text plan where it disagreed.
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
ART_REL = 'game/addons/tome-checker-revised/art/monster-batch-ub2/'
EVDIR = 'evidence/monster-batch-ub2-20261001/source-contracts.json'

spec = importlib.util.spec_from_file_location('ae', HERE.parent / 'monster-batch-ae/make_batches.py')
ae = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ae)
sha = ae.sha
STYLE = ae.STYLE
COMP = ae.COMP
DARKFIX = ae.DARKFIX
CHEAT = ae.CHEAT
DISC = ae.DISC

# id, native name, source file, base file (or None), native image, define_as,
# type, subtype, family, subject, contrast, darkfix
ROWS = [
 ('sun-paladin-guren', "Sun Paladin Guren", 'zones/eruan/npcs.lua', None,
  'humanoid_human_sun_paladin_guren.png', 'SUN_PALADIN_GUREN', 'humanoid', 'human', 'sun-paladins',
  "A lean human knight in cool polished silver-grey steel FULL PLATE with a warm faint gold under-glow in the recesses and dark leather straps at the joints; a closed knight's helm with a low crest ridge and a narrow dark visor slit, pale skin showing at the jaw; a round sun-emblem shield held on the LEFT forearm, showing a gold rayed-sun device on a steel field; a long straight sword lowered across the body in the RIGHT hand, blade angled down to the lower right; both feet planted. Full-height upright armoured silhouette; broad pale upper-left plates and a thin bright rim on every steel face.",
  "Structurally outranks the shipped human-sun-paladin token: that token is a bulky GOLD paladin with an oversized round sun-disc and a forward war-hammer, while Guren is cool silver-grey plate with a long straight sword, a modest round heater shield and a low CRESTED helm. Also differs from the white-gold cape-and-mace Rodmour and from the broad dark Aluin knight by the crest and sword.",
  False),
 ('epoch', "Epoch", 'zones/paradox-plane/npcs.lua', None,
  'elemental_temporal_epoch.png', 'EPOCH', 'elemental', 'temporal', 'temporal',
  "A dense roiling VERTICAL column of raw temporal energy: a bright cobalt-blue core shot through with irregular electric-yellow lightning arcs and crackling forked tendrils that curl outward, with ragged wispy edges and small dark negative gaps inside the mass. NO limbs, NO face, NO eyes, NO segmentation: a chaotic upright blue-and-yellow storm with a faint violet fringe. Paint the blue and yellow as solid opaque material with broad bright faces.",
  "Epoch is a vertical chaotic blue-and-yellow energy storm with no limbs, eyes or segmentation, versus the shipped telugoroth/teluvorta tokens (curled segmented iridescent worms with visible eyes), the low dark blade-like temporal-stalker and the six-armed robed chronolith pair. Its chaotic column silhouette is the structural cue, not the colour alone.",
  False),
 ('corrupted-oozemancer', "Corrupted Oozemancer", 'zones/sludgenest/npcs.lua', None,
  'giant_troll_corrupted_oozemancer.png', 'CORRUPTED_OOZEMANCER', 'giant', 'troll', 'trolls',
  "A massive HUNCHED green blight-troll: very broad powerful shoulders, a thick torso, heavy muscular arms held out to the sides ending in long pale claws, short thick legs, and a low bald head thrust forward with two small glowing red eyes and a wide toothy underbite. The hide is mottled sickly mid-green with lighter mossy patches and dark ooze streaks; every large mass is painted MID-LIGHT with broad pale upper-left highlights so the body stays clearly lighter than the disc.",
  "Structurally distinct from the shipped troll tokens: the Oozemancer is a broad hunched forward-thrusting green blight-troll with a low red-eyed head and out-held clawed arms, versus the upright bulky bronze/brown mountain-troll and forest-troll tokens, the small shax and the stitched patchwork-troll. It is not a recolour of any of them.",
  False),
 ('zemekkys', "Zemekkys, Grand Keeper of Reality", 'zones/town-point-zero/npcs.lua', 'zones/town-point-zero/npcs.lua',
  'humanoid_elf_high_chronomancer_zemekkys.png', 'ZEMEKKYS', 'humanoid', 'shalore', 'elf-story',
  "A pale shalore elf man with short pale-blond hair and a calm face, BARE HEAD (no hat, no hood): a layered deep-sapphire-blue robe with a broad CHEVRON-patterned blue shoulder mantle/scarf over a lighter blue tunic, a small pale badge on the left chest, a brown leather belt, loose blue trousers and brown boots; bare forearms and EMPTY relaxed hands at his sides, no staff and no weapon. Compact upright stance, mid-light blue masses with broad pale upper-left highlight planes.",
  "Structurally distinct from the shipped elven-mage (purple hooded bearded caster), the blue armoured sword-carrying Rhaloren Inquisitor and the grey hooded Necromancer: Zemekkys is a BARE-HEADED unarmoured shalore in a layered blue robe with a chevron mantle and empty hands, no hat and no staff. The blue robe is not enough by itself; the chevron mantle, bare head and empty hands are the cues.",
  False),
 ('blood-master', "Blood Master", 'zones/ring-of-blood/npcs.lua', None,
  'humanoid_yaech_blood_master.png', 'RING_MASTER', 'humanoid', 'yaech', 'yaech',
  "A small STOUT white-furred yaech standing upright on two legs: a large rounded head with two huge bulging red-rimmed eyes and a small mouth, short ice-white fur over a stocky body, an ornate gold-and-bronze shoulder-and-chest harness, and a heavy RED-BLADED greatsword gripped in one raised hand, blade angled up across the body; a few pale ice-blue wisps beside the head. Every fur mass is painted bright white and ice-blue, clearly lighter than the disc.",
  "Structurally distinct from the shipped yaech tokens: the Blood Master is the only white-furred, weapon-wielding bipedal yaech with huge red-rimmed eyes and a red greatsword, versus the blue-grey crowned trident Murgol, the round bubble-trailing yaech-diver and the robed yaech psions. The upright sword line and the white fur are the cues, not colour alone.",
  False),
 ('limmir-the-jeweler', "Limmir the Jeweler", 'zones/valley-moon/npcs.lua', None,
  'humanoid_elf_limmir_the_jeweler.png', 'LIMMIR', 'humanoid', 'elf', 'elf-story',
  "An elven man with long dark hair and a calm face, wearing a pale sage-green and cream tunic with gold trim and cuffs, a brown belt, dark olive trousers and brown boots; he holds one hand raised to shoulder height cradling a small bright GLOWING RED GEM, the other hand resting at his hip. No armour, no staff, no weapon, no hat. Slender upright figure, cream and sage mid-light masses with a broad pale upper-left highlight.",
  "Structurally distinct from the shipped elf tokens: Limmir is a plainly dressed UNARMED elf defined by the small raised glowing RED GEM and the cream-and-sage tunic, versus the white-robed staff-carrying Fillarel, the armoured companion-archer and the corrupt elf casters. The raised gem hand is the cue.",
  False),
 ('protector-myssil', "Protector Myssil", 'zones/town-zigur/npcs.lua', 'general/npcs/ziguranth.lua',
  'humanoid_halfling_protector_myssil.png', 'PROTECTOR_MYSSIL', 'humanoid', 'halfling', 'short-proportions',
  "A SHORT STOCKY halfling woman, clearly shorter and broader in proportion than a human, encased in dark gunmetal steel plate with a CLOSED helm (narrow dark visor slit) and warm brass trim accents on the pauldrons and faulds; she grips a greatsword almost as tall as she is diagonally across her body, point down to the lower left, BOTH hands on the hilt. Heavy low compact silhouette. The armour is MID-GREY gunmetal with broad pale upper-left highlight planes and light brass trim, never a black mass.",
  "Must not read as a recoloured human. Myssil is defined by SHORT STOCKY halfling proportions plus an oversized greatsword held diagonally across the body, versus the tall human Celia and The Possessed tokens and the compact gold human-sun-paladin. The dark steel is carried by broad mid-grey highlights and brass trim, never black.",
  True),
 ("rak-shor-cultist", "Rak'Shor Cultist", 'zones/shadow-crypt/npcs.lua', 'general/npcs/orc-rak-shor.lua',
  'humanoid_orc_rak_shor_cultist.png', 'CULTIST_RAK_SHOR', 'humanoid', 'orc', 'orc-casters',
  "An old gaunt orc with mottled mid-green skin and a bald head, wearing a dark maroon-brown HOODED robe with rust-orange trim along the hood edge and hem; the hood is raised and the face is shadowed but visible, with small pale eyes and a jutting jaw; both arms spread downward and outward with long bare clawed hands. NO crown, NO armour, NO staff. Hunched caster stance; the maroon robe carries broad mid-light rust highlights so it never collapses into black.",
  "Structurally distinct from the shipped orc caster tokens: the Cultist is an unarmoured, uncrowned, staff-less hooded maroon-robed orc with a raised hood and out-held EMPTY hands, versus the blue-hooded staff orc-necromancer, the gold-crowned regal rak-shor, the blue robed orc-corruptor and the armoured ukruk. The raised hood and empty hands are the cues.",
  True),
 ('shady-cornac-man', "Shady cornac man", 'zones/town-derth/npcs.lua', 'zones/town-derth/npcs.lua',
  'humanoid_human_shady_cornac_man.png', 'ARENA_AGENT', 'humanoid', 'human', 'human-story',
  "A broad-shouldered human man with dark hair and a pale face, BARE HEAD (no hood up), wearing a dark TEAL-BLUE cloak draped over both shoulders, a pale grey-white VERTICALLY-STRIPED tunic, a brown belt, dark brown trousers and boots; one hand rests near his hip as if on a sword hilt. Heavier set than a gaunt caster. Paint the cloak mid-teal and the tunic light so the whole figure stays clearly lighter than the disc, with broad pale upper-left highlights.",
  "Structurally distinct from the shipped necromancer and assassin-lord: the Shady cornac man is a broad, BARE-HEADED, heavy-shouldered man in a teal cloak and pale striped tunic with a hand at his hip, versus the gaunt grey hooded Necromancer and the dark masked Assassin Lord. The teal cloak and open face are the cues.",
  True),
 ('tannen', "Tannen", 'zones/tannen-tower/npcs.lua', None,
  'humanoid_human_tannen.png', 'TANNEN', 'humanoid', 'human', 'human-story',
  "A stern grey-bearded human alchemist, balding with a short grey beard and heavy brows, wearing a heavy GOLDEN-TAN robe beneath a broad brown outer mantle with a wide collar; both arms are spread outward and away from the body with OPEN empty hands; no staff, no weapon, no hat. Broad robe-cone silhouette in mid-gold and tan values with broad pale upper-left highlight planes on the robe front.",
  "Structurally distinct from the shipped necromancer (a narrow grey hooded caster with book/aura) and harno: Tannen is a broad OPEN-ARMED, unarmed, bearded alchemist in a gold-and-brown robe, a wide cone shape with no hood and no staff, versus the necromancer's narrow hooded silhouette.",
  False),
]

# Wiring-only: no new art. The Cursed wears the existing ben-cruthdar-abomination
# runtime token (byte-identical native PNG). The reuse master is exported through
# the same deterministic exporter, so its 128px runtime PNG is byte-for-byte the
# abomination token; the abomination entry itself is untouched.
WIRING = dict(
    id='ben-cruthdar-the-cursed', native_name="Ben Cruthdar, the Cursed",
    source_file='zones/town-lumberjack-village/npcs.lua',
    native_image='humanoid_human_ben_cruthdar__the_cursed.png',
    define_as='BEN_CRUTHDAR', type='humanoid', subtype='human',
    reuse_batch='monster-batch-j', reuse_id='ben-cruthdar-abomination',
    reuse_master='monster-batch-j/masters/ben-cruthdar-abomination-v1.png',
)

FAMILIES = {
    'sun-paladins': ['human-sun-paladin', 'high-sun-paladin-rodmour', 'aluin-the-fallen', 'argoniel', 'elandar'],
    'temporal': ['telugoroth', 'greater-telugoroth', 'teluvorta', 'greater-teluvorta',
                 'temporal-stalker', 'temporal-defiler', 'chronolith-twin', 'chronolith-clone'],
    'trolls': ['forest-troll', 'stone-troll', 'cave-troll', 'mountain-troll', 'mountain-troll-thunderer',
               'patchwork-troll', 'shax'],
    'elf-story': ['fillarel-aldaren', 'companion-archer', 'kryl-feijan-acolyte', 'elven-mage', 'elven-corruptor',
                  'archmage-tarelion'],
    'yaech': ['murgol', 'yaech-diver', 'yaech-hunter', 'yaech-mindslayer', 'yaech-psion', 'slaver'],
    'orc-casters': ['orc-necromancer', 'rak-shor', 'ukruk', 'warmaster-gnarg', 'golbug',
                    'orc-high-pyromancer', 'orc-high-cryomancer', 'orc-summoner'],
    'human-story': ['necromancer', 'assassin-lord', 'subject-z', 'the-possessed', 'celia', 'harno', 'urkis'],
    'short-proportions': ['celia', 'the-possessed', 'halfling-guard', 'human-sun-paladin', 'burb-snow-giant-champion'],
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
        (id_, name, file, bfile, png, define, typ, sub, group, subject, contrast, darkfix) = row
        leaf, start, end = leaf_block(file, name)
        pins = [ae.src(file, 'name = "' + name + '"')]
        btext = ''
        mbase = re.search(r'base\s*=\s*"([^"]+)"', leaf)
        if mbase:
            bp = bfile or file
            pins.append(ae.src(bp, 'define_as = "' + mbase.group(1) + '"'))
            lines = (WS / (D + bp)).read_text().splitlines()
            n = pins[-1]['line'] - 1
            s = max(i for i in range(n + 1) if lines[i].startswith('newEntity{'))
            e = next((i for i in range(n + 1, len(lines)) if lines[i].startswith('newEntity{')), len(lines))
            btext = '\n'.join(lines[s:e])
        combined = leaf + btext
        assert not re.search(r'(?<![_a-z])shader\s*=|moddable_tile|add_displays|textures\s*=|anim\s*=|add_mos|nice_tile', combined), (id_, 'unsupported visual')
        native = NPC + png
        with Image.open(WS / native) as im:
            size = list(im.size)
        assert size == [64, 64], (id_, size, 'UB-2 is flat 64x64 only')
        (HERE / 'source').mkdir(exist_ok=True)
        content = ('-- Verified leaf and inherited base; source hashes in source-contracts.json\n'
                   + '\n'.join(l.rstrip() for l in leaf.splitlines())
                   + ('\n-- INHERITED BASE\n' + '\n'.join(l.rstrip() for l in btext.splitlines()) if btext else ''))
        (HERE / 'source' / f'{id_}.lua').write_text(content.rstrip() + '\n')
        explicit = re.search(r'image\s*=\s*"([^"]+)"', leaf)
        dimg = default_image(typ, sub, name)
        structure = (
            ('explicit image="' + explicit.group(1) + '"' if explicit else
             'default image name from class/NPC.lua:33 (' + dimg + ')')
            + '; flat 64x64 body. No shader, moddable_tile, anim, add_displays, textures, add_mos or '
            'nice_tile anywhere in leaf/base. auto_classes / sustains_at_birth, where present, only roll '
            'talents or enable native sustains and never write the drawn body.')
        identities.append(dict(
            id=id_, native_name=name, source=pins[0], base_source=pins[1] if mbase else None,
            sources=pins, define_as=define, type=typ, subtype=sub, unique=True,
            native_tall=False, native_image='npc/' + png, native_image_path=native,
            native_image_sha256=sha(native), native_image_size=size,
            default_image=dimg, explicit_image=(explicit.group(1) if explicit else None),
            image_source='explicit image= field' if explicit else 'class/NPC.lua:33 default name image',
            structure=structure, shader=None, moddable_tile=None, anim=None, add_displays=None,
            leaf_source_lines=[start, end],
            talents=sorted(set(re.findall(r'Talents\.(T_[A-Z0-9_]+)', combined))),
            verdict='READY exact flat unique identity'))

    # Wiring-only identity: verified BEN_CRUTHDAR leaf, but no art generation.
    wleaf, wstart, wend = leaf_block(WIRING['source_file'], WIRING['native_name'])
    assert 'define_as = "BEN_CRUTHDAR"' in wleaf
    assert 'unique = true' in wleaf
    wsrc = ae.src(WIRING['source_file'], 'name = "Ben Cruthdar, the Cursed"')
    abom = ae.src('zones/temporal-rift/npcs.lua', 'define_as = "BEN_CRUTHDAR_ABOMINATION"')
    wimg = NPC + WIRING['native_image']
    with Image.open(WS / wimg) as im:
        wsize = list(im.size)
    assert wsize == [64, 64], wsize
    reuse_manifest = json.loads((ROOT / 'data/token-manifest.json').read_text())
    reuse_entry = next(a for a in reuse_manifest['assets'] if a['id'] == WIRING['reuse_id'])
    reuse_master = WS / ('game/addons/tome-checker-revised/art/' + WIRING['reuse_master'])
    wiring_ident = dict(
        id=WIRING['id'], native_name=WIRING['native_name'], source=wsrc,
        base_source=None, sources=[wsrc, abom], define_as=WIRING['define_as'],
        type=WIRING['type'], subtype=WIRING['subtype'], unique=True,
        native_tall=False, native_image='npc/' + WIRING['native_image'],
        native_image_path=wimg, native_image_sha256=sha(wimg), native_image_size=wsize,
        image_source='class/NPC.lua:33 default name image; byte-identical native PNG to the abomination',
        structure=('wiring-only: reuses the existing ben-cruthdar-abomination runtime token '
                   '(byte-identical native PNG), exported from the same master through the same '
                   'deterministic exporter; no new ImageGen art. The abomination catalog entry, token '
                   'and manifest row are unchanged.'),
        shader=None, moddable_tile=None, anim=None, add_displays=None,
        leaf_source_lines=[wstart, wend], talents=[],
        reuse=dict(batch=WIRING['reuse_batch'], id=WIRING['reuse_id'],
                   master=WIRING['reuse_master'], master_sha256=sha(reuse_master),
                   runtime_sha256=reuse_entry['runtime_sha256']),
        verdict='WIRING-ONLY exact name+define_as entry reusing the abomination token')

    auxiliary = [
        ae.src('class/NPC.lua', '-- Grab default image name', root='game/modules/tome/'),
    ]
    findings = [
        'All ten art identities are flat 64x64 unique bodies with an exact define_as. Eight use the class/NPC.lua:33 default name image and two (Zemekkys, the wiring-only Ben Cruthdar, the abomination cross-pin) carry an explicit image= field; every resolved PNG exists on disk at 64x64.',
        'No leaf or base sets shader, moddable_tile, anim, add_displays, textures, add_mos or nice_tile. Epoch and Ben Cruthdar carry auto_classes that only roll class talents; sustains_at_birth only enables native sustains. Neither writes the drawn body.',
        'No talent, timed effect, map/vault or zone constructor renames or copies these ten identities. Gates of Morning defines an anonymous Limmir store NPC with the same name/type/subtype/image but no define_as and no unique marker, so it stays native (identity-changed), as does any same-body copy without the exact define_as.',
        'ben-cruthdar-the-cursed is wiring-only: the town-lumberjack-village BEN_CRUTHDAR leaf shares the byte-identical native PNG humanoid_human_ben_cruthdar__the_cursed.png with temporal-rift BEN_CRUTHDAR_ABOMINATION. The new catalog entry reuses the abomination runtime token; the abomination entry is unchanged.',
    ]
    ev = dict(
        schema=1,
        task='monster-batch-ub2: third uniques/bosses batch, ten flat 64x64 identities plus one wiring-only reuse; static source re-verification only, no game launch.',
        identities=identities + [wiring_ident],
        art_ids=IDS,
        wiring_only=[wiring_ident['id']],
        new_ids_not_in_catalog_before_this_batch=IDS + [wiring_ident['id']],
        auxiliary_sources=auxiliary,
        kept_native=[],
        runtime_mutation_scan=dict(
            method='Read each leaf and inherited base; scanned talents, timed_effects and zones for image/type/subtype/shader/add_mos/moddable_tile/add_displays/replace_display writes.',
            hits_in_batch=[],
            auto_classes_review=[dict(identity='Epoch', **{'class': 'Paradox Mage'},
                                      finding='auto_classes roll class talents at level-up; they never touch the displayed body.'),
                                 dict(identity="Ben Cruthdar, the Cursed", **{'class': 'Cursed'},
                                      finding='auto_classes roll class talents only.'),
                                 dict(identity='all other leaves', **{'class': 'none'}, finding='No auto_classes')],
            sustains_at_birth_review=[dict(identity='Guren / Zemekkys / Limmir / Myssil / Cultist / Ben Cruthdar',
                                           note='resolvers.sustains_at_birth only enables native sustains; none sets image, shader or add_mos.'),
                                      dict(identity='Epoch / Oozemancer / Blood Master / Shady / Tannen',
                                           note='No resolvers.sustains_at_birth body writes.')]),
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
    c = Image.new('RGBA', (4 * 210, 3 * 220), (46, 50, 46, 255))
    draw = ImageDraw.Draw(c)
    for n, i in enumerate(identities):
        im = Image.open(WS / i['native_image_path']).convert('RGBA').resize((192, 192), Image.Resampling.NEAREST)
        x, y = n % 4 * 210, n // 4 * 220
        draw.text((x + 2, y + 2), i['id'], fill='white')
        c.alpha_composite(im, (x + 8, y + 20))
    c.save(HERE / 'refs/native-identities.png')

    # ImageGen task packs, three assets per pack.
    packs = {}
    for row, i in zip(ROWS, identities):
        id_, name, file, bfile, png, define, typ, sub, group, subject, contrast, darkfix = row
        refs = [
            dict(path=STYLE, sha256=sha(STYLE), role='style', note='Approved neutral disc/camera/light only; do not copy its creature.'),
            dict(path=NPC + png, sha256=sha(NPC + png), role='identity', note='Inspected exact native body ' + str(i['native_image_size']) + '. Paint this clothing, armour, held items and silhouette.'),
            families[group],
        ]
        a = dict(
            asset_id=id_, native_name=name,
            scope='UB-2 flat unique/boss; ' + i['source']['path'] + ':' + str(i['source']['line']),
            sources=i['sources'] + auxiliary,
            references=refs,
            contrast_dimensions=['silhouette', 'value', 'hue'],
            prompt_fields=dict(
                subject=subject + CHEAT,
                contrast=contrast + ' No faction rings, health, shield, rank marks, selection, text or numbers.',
                composition=COMP + (DARKFIX if darkfix else ''),
                palette='Mid-light body masses and broad pale upper-left highlights, thin bright rim. ' + DISC + ' Keep the whole disc at reference lightness; no cast shadow or colour spill.'),
            kind='creature', max_attempts=2, gate='ready',
            gate_reason=i['structure'] + ' Static source contract only; see ' + EVDIR,
            render_evidence=[dict(path='game/addons/tome-checker-revised/' + EVDIR, sha256=hashlib.sha256(out.read_bytes()).hexdigest())])
        packs.setdefault(IDS.index(id_) // 3 + 1, []).append(a)
    for n, assets in packs.items():
        p = ROOT / f'art/production/batches/monster-batch-ub2-{n}.json'
        if not p.exists():
            p.write_text(json.dumps(dict(schema=1, batch_id=f'monster-batch-ub2-{n}', assets=assets), ensure_ascii=False, indent=2) + '\n')

    # Wiring-only task descriptor (no prompt, no pack, no call).
    (HERE / 'wiring-only.json').write_text(json.dumps(dict(
        id=wiring_ident['id'], native_name=wiring_ident['native_name'], define_as=wiring_ident['define_as'],
        sources=[wsrc, abom], native_image=wiring_ident['native_image'],
        native_image_sha256=wiring_ident['native_image_sha256'],
        reuse=wiring_ident['reuse'], note=wiring_ident['structure']), ensure_ascii=False, indent=2) + '\n')

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
    print('UB-2 preparation complete:', len(identities), 'art + 1 wiring;', len(packs), 'packs')


if __name__ == '__main__':
    build()
