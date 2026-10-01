"""Batch TA-1 town residents: pinned source contracts and AF/UA-style task packs.

Static preparation only: source re-verification, family reference sheets and
ImageGen handoff manifests. No generation, no runtime writes, no git operation.
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
ART_REL = 'game/addons/tome-checker-revised/art/monster-batch-ta1/'
EVDIR = 'evidence/monster-batch-ta1-20261001/source-contracts.json'

spec = importlib.util.spec_from_file_location('ae', HERE.parent / 'monster-batch-ae/make_batches.py')
ae = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ae)
sha = ae.sha
STYLE = ae.STYLE  # art/monsters-v2/masters/prox-v2.png
COMP = ae.COMP
DARKFIX = ae.DARKFIX

# id, native name, source file (under data/), base file (or None==same), image,
# type, subtype, tall, family, subject, contrast
ROWS = [
 ('apprentice-mage', "apprentice mage", 'zones/town-angolwen/npcs.lua', None,
  'humanoid_human_apprentice_mage.png', 'humanoid', 'human', False, 'angolwen-mages',
  "A young human APPRENTICE of the Angolwen school: a plain tan-brown cowled robe with a short shoulder cape, the hood down over short brown hair, NO pointed hat and NO staff, both empty hands hanging relaxed and open at his sides. Warm beige and light brown cloth, pale skin, calm upright junior-student stance. Broad pale upper-left planes on the cowl, shoulders and robe folds.",
  "The junior unarmed member: bare/cowled head (no pointed hat) and no staff, versus the four full wizards' tall hats and staves; versus the shipped necromancer hooded skull-caster and elven mage robed staff wizard. Silhouette and equipment, never colour alone."),
 ('pyromancer', "pyromancer", 'zones/town-angolwen/npcs.lua', None,
  'humanoid_human_pyromancer.png', 'humanoid', 'human', True, 'angolwen-mages',
  "A tall grey-bearded wizard in a CRIMSON hooded robe with restrained gold trim and a tall red pointed hat leaning slightly forward. Both hands grip a LONG STAFF held diagonally low across the chest; the lowered off-hand cups a small bright ember. Crimson and vermilion cloth, gold edging, pale ash-grey beard and face, broad pale upper-left highlight planes.",
  "Differentiated by staff angle + focus prop + stance: staff couched LOW and diagonal across the chest, ember cupped low, forward lean. Versus cryomancer's vertical staff and ice shards, geomancer's short conical hat and rune-cube, tempest's overhead staff and lightning, and shipped orc/elven casters. Pose and props, never colour alone."),
 ('cryomancer', "cryomancer", 'zones/town-angolwen/npcs.lua', None,
  'humanoid_human_cryomancer.png', 'humanoid', 'human', True, 'angolwen-mages',
  "A tall grey-bearded wizard in a dark sapphire-blue robe and a tall STRAIGHT blue pointed hat, standing fully UPRIGHT with the LONG STAFF held nearly VERTICAL in the outer hand; a cluster of pale angular ICE SHARDS and a snowflake crystal floats above the near open hand. Blue cloth, frost-white highlights, pale grey beard, broad light upper-left planes.",
  "Differentiated by upright stance + near-vertical staff + pale angular ice-shard prop. Versus pyromancer's diagonal low staff and ember, geomancer's short hat and rune-cube, tempest's raised lightning staff, and shipped orc-cryomancer (bare green orc, no hat). Structure, not colour."),
 ('geomancer', "geomancer", 'zones/town-angolwen/npcs.lua', None,
  'humanoid_human_geomancer.png', 'humanoid', 'human', True, 'angolwen-mages',
  "A tall grey-bearded wizard in an ochre-mustard hooded robe and a SHORT CONICAL brown hat, planted in a WIDE stable stance with the LONG STAFF angled outward and low, and a small hard-edged glowing GOLDEN RUNE-CUBE floating above the open near hand. Earthy brown and ochre cloth with darker seams, warm gold glyph, broad pale upper-left planes.",
  "Differentiated by short conical hat + wide planted stance + hard-edged floating rune-CUBE (not a soft ember, white angular ice or forked lightning). Versus pyromancer/cryomancer/tempest and shipped casters by silhouette and prop geometry, not colour."),
 ('tempest', "tempest", 'zones/town-angolwen/npcs.lua', None,
  'humanoid_human_tempest.png', 'humanoid', 'human', True, 'angolwen-mages',
  "A tall grey-bearded wizard in a near-black charcoal robe and a tall slightly BENT dark pointed hat, both arms RAISED so the LONG STAFF is lifted HIGH overhead and a forked cyan-white LIGHTNING bolt crackles from its tip. Render the whole figure in MID-LIGHT charcoal and slate values, never black, with broad pale grey upper-left robe folds and a bright cool rim light on the hat, shoulders and staff so the silhouette reads light on the dark disc.",
  "Differentiated by raised overhead staff + forked lightning and the darkest, most vertical caster body. Versus pyromancer's low diagonal staff, cryomancer's upright ice staff, geomancer's wide short-hat stance, and shipped elven-tempest (pale, no hat) and urkis. Pose and hat, not colour."),
 ('human-guard', "human guard", 'general/npcs/sunwall-town.lua', None,
  'humanoid_human_human_guard.png', 'humanoid', 'human', False, 'guards',
  "A blonde human town GUARD in a green tunic under a brown leather jerkin, bare lower legs and simple shoes, a drawn arming SWORD in the right hand and a tall heraldic KITE SHIELD on the left arm; light upright watch stance. Greens and leather browns with bright steel highlights, broad pale upper-left planes.",
  "Human proportions and plain gear: green cloth + kite shield + lowered sword, versus caravan-guard's full mail and round shield + spear, human-sun-paladin's gold full plate and mace, and the elven/derth/other guards' distinct head and weapon shapes. Structure, not colour."),
 ('derth-guard', "derth guard", 'zones/town-derth/npcs.lua', None,
  'humanoid_human_derth_guard.png', 'humanoid', 'human', False, 'guards',
  "A broad BARE-ARMED human guard in a brown leather hood and tunic, a ROUND TARGE on the left arm and a raised spiked MACE in the right hand, aggressive wide open stance. Warm brown leather, dark steel mace head, ruddy skin, broad pale upper-left planes on the bald head, shoulders and targe.",
  "Round targe + raised spiked mace + bare arms, versus human-guard's kite shield and lowered sword, last-hope-guard's full sallet plate, and bandit's twin axes with no shield. Weapon and shield shape, not colour."),
 ('last-hope-guard', "last hope guard", 'zones/town-last-hope/npcs.lua', None,
  'humanoid_human_last_hope_guard.png', 'humanoid', 'human', False, 'guards',
  "A fully armoured human guard in grey steel PLATE with a CLOSED SALLET HELM and a white surcoat, holding a longsword LOW across the body and a kite shield bearing a dark horse/charge emblem. Cool steel greys and white cloth with a single warm accent on the shield, bright pale upper-left plate faces.",
  "The heaviest fully enclosed head silhouette (closed sallet + plate + white surcoat) with a low longsword and emblem kite shield, versus human-guard's bare head/green cloth, derth-guard's hood and mace, and human-sun-paladin's gold plate. Structure, not colour."),
 ('halfling-guard', "halfling guard", 'zones/town-last-hope/npcs.lua', None,
  'humanoid_halfling_halfling_guard.png', 'humanoid', 'halfling', False, 'guards',
  "A short round HALFLING guard: oversized head under a small steel CAP, brown leather tunic, bare furry feet, a crude wooden CUDGEL/CLUB held down in one hand and the other hand empty; stumpy low-centre-of-gravity stance. Browns and warm tan cloth with a steel-cap highlight, broad pale upper-left planes.",
  "Halfling body proportions (short limbs, oversized head, wide low stance) and a crude wooden club with NO shield, versus the human guards' swords/maces and kite/round shields and the dwarf's axe. Proportion and weapon, not colour."),
 ('dwarven-guard', "dwarven guard", 'zones/town-iron-council/npcs.lua', None,
  'humanoid_dwarf_dwarven_guard.png', 'humanoid', 'dwarf', False, 'guards',
  "A stocky DWARF guard in a grey steel helm and grey mail with a huge pale beard, gripping a TWO-HANDED BATTLEAXE carried diagonally across the body with both hands; heavy planted broad stance. Grey mail, brown leather straps, pale ivory beard, bright pale upper-left planes on the helm and axe head.",
  "Dwarf proportions (short, broad, huge beard) plus helm and two-handed axe with NO shield, versus dwarven-earthwarden's bare head and large round shield, norgan's bare head and hammer, and every human guard. Proportion and weapon, not colour."),
 ('elvala-guard', "elvala guard", 'zones/town-elvala/npcs.lua', None,
  'humanoid_shalore_elvala_guard.png', 'humanoid', 'shalore', False, 'guards',
  "A slender TALL elven guard in warm gold-bronze SCALE armour with a tall crested helm, a longsword in the right hand and a shield bearing a green leaf emblem on the left. Gold-bronze scale, green accent, pale skin, broad pale upper-left planes on the helm, pauldrons and shield.",
  "Tall slender elf with gold-bronze scale and a TALL CRESTED helm plus leaf-emblem shield, versus elven-guard's green-and-gold kit, mean-looking-elven-guard's unarmoured ranger body, and every human guard. Silhouette and helm, not colour."),
 ('slaver', "slaver", 'zones/ring-of-blood/npcs.lua', None,
  'humanoid_yaech_slaver.png', 'humanoid', 'yaech', False, 'ring-of-blood',
  "A small hunched blue-grey amphibian YAECH slaver with huge red eyes and a finned head crest, one arm raised mid-gesture and the other holding a wavy serrated DAGGER; predatory crouch. Cold blue-grey scales, bright red eyes, dark steel blade, broad pale upper-left planes on the crest and shoulders.",
  "Serrated dagger plus raised commanding arm and finned crest, versus shipped yaech-hunter/diver (trident/swim), yaech-mindslayer/psion (psionic glow, no weapon) and bandit. Weapon and posture, not colour."),
 ('enthralled-slave', "enthralled slave", 'zones/ring-of-blood/npcs.lua', None,
  'humanoid_human_enthralled_slave.png', 'humanoid', 'human', False, 'ring-of-blood',
  "A pale hollow-eyed human SLAVE in a plain worn off-white tunic, arms slack at the sides and the head slightly BOWED; subdued powerless stance. Washed cream and grey cloth, sallow skin, no gear. Broad pale upper-left cloth planes and a bright rim so the pale body reads on the disc.",
  "No tool, no armour, no belt and a bowed-head arms-down silhouette, versus human-citizen's raised greeting arm and doublet, human-farmer's pitchfork, and the yaech slaver. The bowed-head T silhouette is the cue, not colour."),
]

FAMILIES = {
    'angolwen-mages': ['elven-mage', 'elven-tempest', 'orc-pyromancer', 'orc-cryomancer', 'necromancer', 'urkis'],
    'guards': ['caravan-guard', 'elven-guard', 'mean-looking-elven-guard', 'human-sun-paladin', 'elven-warrior', 'norgan'],
    'ring-of-blood': ['yaech-hunter', 'yaech-mindslayer', 'yaech-psion', 'yaech-diver', 'bandit'],
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
    for id_, name, file, bfile, png, typ, sub, tall, group, subject, contrast in ROWS:
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
        assert not re.search(r'auto_classes', combined), (id_, 'auto_classes')
        native = NPC + png
        with Image.open(WS / native) as im:
            size = list(im.size)
        assert size == ([64, 128] if tall else [64, 64]), (id_, size)
        (HERE / 'source').mkdir(exist_ok=True)
        (HERE / 'source' / f'{id_}.lua').write_text(
            '-- Verified leaf and inherited base; source hashes in source-contracts.json\n'
            + '\n'.join(l.rstrip() for l in leaf.splitlines())
            + '\n-- INHERITED BASE\n' + '\n'.join(l.rstrip() for l in btext.splitlines()).rstrip() + '\n')
        default = 'npc/' + typ + '_' + sub + '_' + re.sub('[^a-z0-9]', '_', name.lower()) + '.png'
        nice = re.search(r'resolvers\.nice_tile\{[^\n]*\}', leaf)
        structure = (
            'Exactly one nice_tile body at display_h=2/display_y=-1 (native_tall=true admits it); '
            'no shader, moddable_tile, anim or add_displays on leaf/base; no auto_classes. '
            'nicer_tiles off uses the same single native image.'
            if tall else
            'Flat single 64x64 default-name native image; no nice_tile or add_mos; '
            'no shader, moddable_tile, anim or add_displays on leaf/base; no auto_classes.')
        identities.append(dict(
            id=id_, native_name=name, source=pins[0], base_source=pins[1] if base else None,
            sources=pins, define_as=None, type=typ, subtype=sub, unique=False,
            native_tall=tall, native_image='npc/' + png, native_image_path=native,
            native_image_sha256=sha(native), native_image_size=size,
            default_image=default, default_image_exists=(WS / (D + 'gfx/shockbolt/' + default)).exists(),
            image_source='NPC.lua:33 default-name image' if not tall else 'nice_tile explicit single-body tall image',
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

    auxiliary = [
        ae.src('class/NPC.lua', '-- Grab default image name', root='game/modules/tome/'),
        ae.src('resolvers.lua', 'function resolvers.calc.nice_tile', root='game/modules/tome/'),
        ae.src('zones/ring-of-blood/npcs.lua', 'make_escort = {'),
        ae.src('zones/ring-of-blood/npcs.lua', 'name="enthralled slave", number=2'),
    ]

    findings = [
        'All thirteen leaves are non-unique with no define_as. Each name has exactly one actor leaf across data/ (grepped), so exact name+type+subtype+image identity is sufficient and no alias/variant rule is needed.',
        'Four Angolwen mages (pyromancer, cryomancer, geomancer, tempest) are explicit nice_tile 64x128 bodies (image="invis.png", add_mos image/display_h=2/display_y=-1); apprentice mage is a flat 64x64 default-name body. All four talls carry native_tall=true because nativeTallImage requires entry.unique or entry.native_tall.',
        'The six guards are flat 64x64 default-name bodies with distinct type/subtype: human guard and derth guard/last hope guard are humanoid/human, halfling guard is humanoid/halfling, dwarven guard humanoid/dwarf, elvala guard humanoid/shalore. None has define_as.',
        'slaver is humanoid/yaech with an explicit default-name body; enthralled slave is humanoid/human. make_escort spawns two "enthralled slave" actors with type=humanoid, subtype=human, name="enthralled slave" and the same default image, i.e. same-body copies that wear the enthralled-slave token through the ordinary exact-identity path (coordinator decision 7). No separate escort entry is added.',
        'No leaf or base sets shader, moddable_tile, anim, add_displays or auto_classes. The mages equip staff/cloth and the guards equip mundane weapons/armour, but none is a moddable_tile paper-doll, so equipment never changes the drawn body.',
        'No talent, timed effect, map/vault or zone constructor renames or copies these thirteen identities except the slaver make_escort above; no name_aliases, image_aliases, body_aliases or sameBodyVariant entries are added for this batch.',
    ]
    ev = dict(
        schema=1,
        task='monster-batch-ta1: first town-resident batch; static source re-verification only, no game launch; thirteen exact identities.',
        identities=identities,
        new_ids_not_in_catalog_before_this_batch=IDS,
        auxiliary_sources=auxiliary,
        summons_and_same_body_copies=dict(
            method='Source scan of NPC leaves, bases, make_escort, talents, timed_effects, maps/vaults and zones for name/PNG hits.',
            findings=findings),
        kept_native=[],
        runtime_mutation_scan=dict(
            method='Read each leaf and inherited base; scanned talents, timed_effects, zones and maps for image/type/subtype/shader/add_mos/moddable_tile/add_displays/replace_display writes.',
            hits_in_batch=[],
            auto_classes_review=[dict(identity='all thirteen leaves', **{'class': 'none'}, finding='No auto_classes; no urh_rok_form opt-in')],
            sustains_at_birth_review=[dict(identity='all thirteen town leaves', sustained=[], note='No resolvers.sustains_at_birth; only racial()/inscriptions()/equip()/talents() resolvers')]),
    )
    out = ROOT.parents[2] / 'game/addons/tome-checker-revised' / EVDIR
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(ev, ensure_ascii=False, indent=2) + '\n')

    # Family reference sheets from shipped tokens.
    families = {}
    for group, gids in FAMILIES.items():
        c = Image.new('RGBA', (384, ((len(gids) + 2) // 3) * 128))
        for n, i in enumerate(gids):
            c.alpha_composite(Image.open(ROOT / 'data/gfx/tokens' / f'{i}.png').convert('RGBA'), (n % 3 * 128, n // 3 * 128))
        p = HERE / 'refs' / f'{group}.png'
        p.parent.mkdir(exist_ok=True)
        c.save(p)
        families[group] = dict(path=ART_REL + 'refs/' + p.name, sha256=sha(ART_REL + 'refs/' + p.name), role='family',
                               note='Shipped siblings row order: ' + ', '.join(gids) + '. Match tabletop language and stay structurally distinct; do not copy their anatomy.')

    # Native identity contact sheet (viewing aid).
    c = Image.new('RGBA', (5 * 220, 3 * 320), (46, 50, 46, 255))
    draw = ImageDraw.Draw(c)
    for n, i in enumerate(identities):
        im = Image.open(WS / i['native_image_path']).convert('RGBA')
        im = im.resize((128, 256 if i['native_tall'] else 128), Image.Resampling.NEAREST)
        x, y = n % 5 * 220, n // 5 * 320
        draw.text((x + 2, y + 2), i['id'], fill='white')
        c.alpha_composite(im, (x + 40, y + 24))
    c.save(HERE / 'refs/native-identities.png')

    # ImageGen task packs, three assets per pack.
    packs = {}
    for row, i in zip(ROWS, identities):
        id_, name, file, bfile, png, typ, sub, tall, group, subject, contrast = row
        refs = [
            dict(path=STYLE, sha256=sha(STYLE), role='style', note='Approved neutral disc/camera/light only; do not copy its creature.'),
            dict(path=NPC + png, sha256=sha(NPC + png), role='identity', note='Inspected exact native body ' + str(i['native_image_size']) + '.'),
            families[group],
        ]
        a = dict(
            asset_id=id_, native_name=name,
            scope='TA-1 town resident; ' + i['source']['path'] + ':' + str(i['source']['line']),
            sources=i['sources'] + auxiliary,
            references=refs,
            contrast_dimensions=['silhouette', 'value', 'hue'],
            prompt_fields=dict(
                subject=subject + ae.CHEAT,
                contrast=contrast + ' No faction rings, health, shield, rank marks, selection, text or numbers.',
                composition=COMP + DARKFIX,
                palette='Mid-light body masses and broad pale upper-left highlights, thin bright rim. ' + ae.DISC + ' Keep the whole disc at reference lightness; no cast shadow or colour spill.'),
            kind='creature', max_attempts=2, gate='ready',
            gate_reason=i['structure'] + ' Static source contract only; see ' + EVDIR,
            render_evidence=[dict(path='game/addons/tome-checker-revised/' + EVDIR, sha256=hashlib.sha256(out.read_bytes()).hexdigest())])
        packs.setdefault(IDS.index(id_) // 3 + 1, []).append(a)
    for n, assets in packs.items():
        p = ROOT / f'art/production/batches/monster-batch-ta1-{n}.json'
        if not p.exists():
            p.write_text(json.dumps(dict(schema=1, batch_id=f'monster-batch-ta1-{n}', assets=assets), ensure_ascii=False, indent=2) + '\n')

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

    # Final admission defaults to every READY identity (art review may update it).
    if not (HERE / 'final-admission.json').exists():
        (HERE / 'final-admission.json').write_text(json.dumps(
            dict(accepted_ids=IDS, native={}, art_review='pending static 48/64/96 review',
                 body_minimum=65.0, descriptive_floor_baseline=45.0, calls=0,
                 selected_masters=len(IDS), waivers=[]), indent=2) + '\n')
    admitted = json.loads((HERE / 'final-admission.json').read_text())['accepted_ids']
    (HERE / 'catalog.json').write_text(json.dumps([dict(id=i) for i in admitted], indent=2) + '\n')
    (HERE / 'catalog.js').write_text('window.monsterCatalog = ' + (HERE / 'catalog.json').read_text().strip() + ';\n')
    print('TA-1 preparation complete:', len(identities), 'identities,', len(packs), 'packs')


if __name__ == '__main__':
    build()
