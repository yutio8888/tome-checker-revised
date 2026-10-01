"""AG last off-list pool batch (special cases): exact source contracts and task packs.

Seven identities that were native because of an actor shader or a shared name:
three multi-hued drakes (quad_hue only when nicer_tiles is off), two shadow claws
(same name, distinct define_as, PNG and stats) and two quad_hue crystals.
AD/AE composition strings and every gate are reused unchanged. No generation,
runtime write or game launch happens here.
"""
import hashlib, importlib.util, json, re
from pathlib import Path
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ADDON = HERE.parents[1]
WS = ADDON.parents[2]
D = 'game/modules/tome/data/'
NPC = D + 'gfx/shockbolt/npc/'
ART_REL = 'game/addons/tome-checker-revised/art/monster-batch-ag/'
EVDIR = 'evidence/monster-batch-ag-20261001/source-contracts.json'
spec = importlib.util.spec_from_file_location('ae', HERE.parent / 'monster-batch-ae/make_batches.py')
ae = importlib.util.module_from_spec(spec); spec.loader.exec_module(ae)
sha, src = ae.sha, ae.src

MH = 'general/npcs/multihued-drake.lua'
CR = 'general/npcs/crystal.lua'
KM = 'zones/keepsake-meadow/npcs.lua'
# id, name, file, leaf anchor, define_as, type, subtype, png, tall, group, shader contract, subject, contrast
ROWS = [
('multi-hued-drake-hatchling', 'multi-hued drake hatchling', MH, 'name = "multi-hued drake hatchling"', None, 'dragon', 'multihued',
 'dragon_multihued_multi_hued_drake_hatchling.png', False, 'multihued', 'nicer-off',
 'A small young multi-hued drake hatchling sitting up on its haunches, chubby round body, short stubby wings half raised, big round head topped by a wide SPREAD FAN-SHAPED FRILL of many thin upright spines like a crest fan, tail curled forward around its feet. Its scales are an opalescent HARLEQUIN MOSAIC of distinct patches: coral red, leaf green, sky blue, violet and gold, each patch mid-light with pale pearly highlights, iridescent sheen on the frill. Pale cream belly plates, small bright eyes. One baby dragon, no breath effect.',
 'Hatchling: small seated chubby baby with a WIDE SPINED HEAD FAN and mosaic patchwork scales of many colours; shipped fire/cold/storm/venom hatchlings are single-colour, crest-less or serpentine; the multi-hued drake adult is a heavy roaring quadruped with swept fin-wings and the greater wyrm a towering winged coil.'),
('multi-hued-drake', 'multi-hued drake', MH, 'name = "multi-hued drake"', None, 'dragon', 'multihued',
 'dragon_multihued_multi_hued_drake.png', False, 'multihued', 'nicer-off',
 'A mature heavy multi-hued drake crouched low on four thick legs, broad barrel body, head thrust forward with jaws WIDE OPEN in a roar showing a pale throat, a crown of several swept-back horns and spines, two large swept-back FIN-LIKE WINGS folded tight along the back with membranes divided into separate colour panels. Pearl-white base hide covered in a HARLEQUIN MOSAIC of coral red, emerald green, cobalt blue and violet scale patches, all mid-light with broad pearly highlights. No breath effect.',
 'Adult drake: heavy low four-legged roaring body with swept panelled fin-wings and pearl hide with multicolour patches; differs from the seated fan-crested hatchling and the upright coiled greater wyrm by posture and build, and from shipped fire/storm/cold/venom/sand drakes by the many-coloured panelled wings, open roar and patchwork, not only hue.'),
('greater-multi-hued-wyrm', 'greater multi-hued wyrm', MH, 'name = "greater multi-hued wyrm"', 'GREATER_MULTI_HUED_WYRM', 'dragon', 'multihued',
 'dragon_multihued_greater_multi_hued_wyrm.png', True, 'multihued', 'nicer-off',
 'An old powerful greater multi-hued wyrm REARING UPRIGHT: long serpentine neck raised in an S-curve over a coiled heavy body, horned head with a beak-like snout turned sideways, and two HUGE upright bat WINGS raised high behind it and folded close together like a tall fan, wing ribs radiating with separate membrane panels in coral red, green, blue, violet and gold. Deep sapphire-blue hide (mid-light, never black) mottled with a mosaic of iridescent colour patches, broad pearly highlights on neck and coils. Compact vertical silhouette, tail tucked in the coil. No breath effect.',
 'Greater wyrm: towering upright neck plus a tall fan of raised panelled wings above a heavy coil; shipped fire/venom/ice/storm wyrms are wingless or small-winged horizontal coils of one colour; the multi-hued drake crouches on four legs, the hatchling sits small with a head fan.'),
('shadow-claw', 'shadow claw', KM, 'define_as = "SHADOW_CLAW"', 'SHADOW_CLAW', 'undead', 'shadow',
 'shadow-claw.png', False, 'shadows', None,
 'A shadow, almost humanoid in shape, swimming through the air: a smoky lean torso and small featureless head leaning forward, no legs, the lower body trailing into a short curled wisp of smoke kept on the figure. TWO ENORMOUS long curved scythe-like CLAWS extend forward and outward from its arms, glossy MAGENTA-ROSE claws curving back inward so their tips stay well inside the disc. Smoke body rendered as solid sculpted ash-lavender and slate-grey volumes, mid-light, with a pale silver rim; bright pink-magenta claws.',
 'Shadow claw: legless forward-lunging smoke torso with two huge curved magenta scythe claws; shadow caster is an upright hooded psionic figure with concentric rings around its head; shipped shadow stalker is a crouched smoke humanoid with short claws.'),
('shadow-caster', 'shadow claw', KM, 'define_as = "SHADOW_CASTER"', 'SHADOW_CASTER', 'undead', 'shadow',
 'shadow-caster.png', False, 'shadows', None,
 'A shadow whose form is a force of will: an UPRIGHT narrow HOODED figure of solid sculpted smoke, tall pointed hood with a dim violet face hollow, cloak-like body tapering to a smoky point, arms folded inward with two small open hands. Around its hooded head hover TWO thin CONCENTRIC MAGENTA PSIONIC RINGS, flat circles hovering close around the hood like still ripples, well inside the disc. Smoke rendered mid-light ash-lavender and slate grey with pale silver rim highlights; rings bright rose-magenta.',
 'Shadow caster: upright still hooded cone with concentric magenta rings around the head, no claws; shadow claw is a legless forward-lunging torso with two huge scythe claws; shipped shadow stalker is a crouched smoke humanoid.'),
('multi-hued-crystal', 'multi-hued crystal', CR, 'name = "multi-hued crystal"', None, 'immovable', 'crystal',
 'crystal_violet.png', False, 'crystals', 'always',
 'A formation of multi-hued crystal shaped as an ARCH: several long thin crystal shards bent into a low hooped arch like a crystal bridge or spider legs, standing on splayed pointed shard feet, with shorter shards bristling from the top of the arch. Clear pale violet crystal whose facets are split by PRISMATIC RAINBOW bands, red, orange, green, cyan, blue and violet refraction stripes running along each shard, bright white glints. Open hollow silhouette, not a solid cluster. No light beams on the disc.',
 'Multi-hued crystal: open arched bridge of bent thin shards with rainbow refraction bands; shimmering crystal is a squat rounded dome with three small orbs; shipped white/red/blue/crimson/black crystals are solid upright prism clusters of a single colour.'),
('shimmering-crystal', 'shimmering crystal', CR, 'name = "shimmering crystal"', None, 'immovable', 'crystal',
 'crystal_npc.png', False, 'crystals', 'always',
 'A formation of shimmering crystal: a SQUAT ROUNDED DOME-SHAPED geode cluster of short blunt pale mint-green and pearl-white crystal points, iridescent opal sheen with faint pink and blue reflections, and THREE small round glowing ORBS of soft yellow-white light floating close around its middle at different heights, each orb touching or nearly touching the crystal, all inside the disc. Broad pale facets. No rays, no glow spilled on the disc.',
 'Shimmering crystal: low rounded dome of short blunt points with three small attached light orbs; multi-hued crystal is an open rainbow-banded arch of thin shards; shipped white crystal is a tall upright prism cluster, and red/blue/crimson/black crystals are single-colour clusters.'),
]
IDS = [r[0] for r in ROWS]
# The two "shadow claw" identities share a name, so they live in different packs.
PACK = {'multi-hued-drake-hatchling': 1, 'multi-hued-drake': 1, 'greater-multi-hued-wyrm': 1,
        'shadow-claw': 2, 'multi-hued-crystal': 2, 'shadow-caster': 3, 'shimmering-crystal': 3}
FAMILIES = {
    'multihued': ['fire-drake-hatchling', 'cold-drake-hatchling', 'storm-drake-hatchling', 'fire-drake', 'storm-drake', 'venom-drake', 'fire-wyrm', 'ice-wyrm', 'storm-wyrm'],
    'shadows': ['shadow-stalker', 'dread', 'umbral-horror'],
    'crystals': ['white-crystal', 'red-crystal', 'blue-crystal', 'crimson-crystal', 'black-crystal', 'giant-crystal-rat'],
}
SHADER = {
    'nicer-off': dict(field='shader', value='quad_hue', shader_args=None, inherited_from='BASE_NPC_MULTIHUED_DRAKE',
                      nicer_tiles_on='resolvers.nice_tile{shader = false} on the base merges shader=false: actor.shader is false, no shader drawn natively; token needs no shader rule.',
                      nicer_tiles_off='resolver inactive: actor.shader="quad_hue" (no shader_args) on the single default/explicit PNG.'),
    'always': dict(field='shader', value='quad_hue', shader_args=None, inherited_from='leaf',
                   nicer_tiles_on='no nice_tile resolver: shader="quad_hue" in every tile mode.',
                   nicer_tiles_off='same.'),
}


def leaf_block(path, anchor):
    lines = (WS / (D + path)).read_text().splitlines()
    n = next(i for i, l in enumerate(lines) if anchor in l)
    start = max(i for i in range(n + 1) if lines[i].startswith('newEntity{'))
    end = next((i for i in range(n + 1, len(lines)) if lines[i].startswith('newEntity{')), len(lines))
    return '\n'.join(lines[start:end]), start + 1, end


def build():
    identities = []
    for id_, name, file, anchor, define_as, typ, sub, png, tall, group, shader, subject, contrast in ROWS:
        block, start, end = leaf_block(file, anchor)
        base = re.search(r'base\s*=\s*"([^"]+)"', block)[1]
        source = src(file, anchor)
        basepin = src(file, 'define_as = "' + base + '"')
        extras = [src(file, 'name = "' + name + '"', after=anchor)] if anchor.startswith('define_as') else []
        if tall:
            extras.append(src(file, 'resolvers.nice_tile', after=anchor))
        if shader:
            extras.append(src(file, 'shader = "quad_hue"', after='define_as = "' + base + '"' if shader == 'nicer-off' else anchor))
        native = NPC + png
        with Image.open(WS / native) as im:
            size = list(im.size)
        assert size == ([64, 128] if tall else [64, 64]), (id_, size)
        explicit = re.search(r'(?<!_)\bimage\s*=\s*"npc/', block.split('resolvers.nice_tile')[0]) is not None
        default = 'npc/' + typ + '_' + re.sub('[^a-z0-9]', '_', sub.lower()) + '_' + re.sub('[^a-z0-9]', '_', name.lower()) + '.png'
        if id_ == 'shimmering-crystal':
            image_source = 'inherits BASE_NPC_CRYSTAL image npc/crystal_npc.png (same PNG as the shipped white crystal; name-keyed identity)'
        elif explicit:
            image_source = 'explicit image= on the leaf'
        else:
            image_source = 'NPC.lua:33 default-name image'
        structure = image_source + '; '
        structure += ('nicer_tiles on: invis.png + one body {image=PNG,display_h=2,display_y=-1} (native_tall); nicer_tiles off: the same PNG as a single image. ' if tall else 'flat single image 64x64. ')
        if shader == 'nicer-off':
            structure += 'Actor shader quad_hue (no shader_args) only with nicer_tiles off; base nice_tile sets shader=false otherwise. Exact native_shader="quad_hue" allow-list entry.'
        elif shader == 'always':
            structure += 'Actor shader quad_hue (no shader_args) in every tile mode. Exact native_shader="quad_hue" allow-list entry.'
        if define_as and id_ != 'greater-multi-hued-wyrm':
            structure += ' Name "shadow claw" is shared by SHADOW_CLAW and SHADOW_CASTER: composite name+define_as identity (shared_name=true).'
        identities.append(dict(
            id=id_, native_name=name, source=source, base_source=basepin, extra_sources=extras, define_as=define_as,
            type=typ, subtype=sub, unique=False, native_tall=tall, native_image='npc/' + png, native_image_path=native,
            native_image_sha256=sha(native), native_image_size=size, default_image=default,
            default_image_exists=(WS / (D + 'gfx/shockbolt/' + default)).exists(), image_source=image_source,
            structure=structure, shader=SHADER.get(shader), moddable_tile=None, anim=None, add_displays=None,
            nice_tile='explicit single-body tall' if tall else ('shader=false (base)' if shader == 'nicer-off' else None),
            add_mos=[dict(image='npc/' + png, display_h=2, display_y=-1)] if tall else None,
            leaf_source_lines=[start, end], talents=re.findall(r'Talents\.(T_[A-Z0-9_]+)', block),
            direct_display_hits=[l.strip() for l in block.splitlines() if re.search(r'shader|addParticles|addShaderAura|image|summon|make_escort|tint', l)],
            verdict='READY'))
    auxiliary = [
        src('resolvers.lua', 'function resolvers.calc.nice_tile', root='game/modules/tome/'),
        src('class/NPC.lua', '-- Grab default image name', root='game/modules/tome/'),
        src('class/Game.lua', 'elseif gfx.tiles == "shockbolt" then', root='game/modules/tome/'),
        src('gfx/shaders/quad_hue.lua', 'frag = "quad_hue"'),
        src('engine/Entity.lua', 'if self.replace_display then tgt = self.replace_display end', root='game/engines/default/'),
        src('engine/Entity.lua', 'if tiles.use_images and core.shader.active() and self.shader then', root='game/engines/default/'),
        src('engine/Entity.lua', 'table.mergeAppendArray(temp, t, true)', root='game/engines/default/'),
        src('zones/keepsake-meadow/traps.lua', 'name = "SHADOW_CASTER"'),
        src('quests/keepsake.lua', '"actor", "SHADOW_CLAW"'),
        src('maps/zones/keepsake-cave-last.lua', '"SHADOW_CASTER"'),
        src('maps/vaults/dragon_lair.lua', 'name="greater multi-hued wyrm"'),
        src('zones/vor-armoury/npcs.lua', 'define_as="OVERPOWERED_WYRM"'),
        src('general/events/drake-cave.lua', '"multihued"'),
        src('zones/arena/npcs.lua', 'shader = "quad_hue"'),
    ]
    shader_policy = dict(
        decision='(b) narrow exact allow-list: catalog field native_shader="quad_hue" on these five non-unique entries only; actor.shader must equal exactly "quad_hue" with shader_args nil. Every other shader (shadow_simulacrum on shadowy assassin and dreaming horror, any args variant, any other entry) keeps native art.',
        why_token_is_honest='quad_hue (data/gfx/shaders/quad_hue.frag) multiplies the whole sprite by one global colour that cycles red->green->blue->cyan every 2 s. It encodes no game state; it is the constant "shines with all the colours of the rainbow" look of these leaves. The tokens paint that identity as physical iridescent patchwork scales / prismatic refraction bands.',
        why_native_shader_not_drawn='engine Entity:getMapObjects builds map objects from tgt=self.replace_display when set. The installed token is a fresh Entity{image=token} with no shader field, so the actor quad_hue is neither drawn under nor over the token; the actor own _mo is not built. Removing the token rebuilds the native mo with its shader.',
        rejected_c='Applying quad_hue to the token would multiply the neutral disc plate by saturated cycling colours, breaking the neutral-base rule and readability; rejected.',
        drakes_nicer_on='Default shockbolt tiles set nicer_tiles=true: BASE_NPC_MULTIHUED_DRAKE nice_tile{shader=false} merges shader=false (arrays appended by importBase), so the three drakes carry no shader natively and match like any single/native-tall body.',
        tint='Crystal tint (VIOLET/GREEN) is colour modulation of the native mo only; shipped crystal tokens already ignore tint.',
        unchanged=['shadowy assassin shadow_simulacrum', 'dreaming horror shadow_simulacrum', 'Arena golden crystal and other quad_hue actors without an entry', 'Ureslak the Prismatic (unique) and overpowered greater multi-hued wyrm (other name)'])
    same_name = dict(
        decision='Two distinct creatures: SHADOW_CLAW (shadow-claw.png, life 80-100, rating 8, melee crit claws, Dominate/Blindside) and SHADOW_CASTER (shadow-caster.png, life 50-60, hate/psi, Willful Strike/Reproach/Mind Sear) both named "shadow claw". Composite identity name+define_as: entries opt in with shared_name=true and a distinct non-nil define_as; the CheckerTokens index still asserts that any other duplicate name fails.',
        spawns='keepsake-meadow pool (cave/vault rarity), traps.lua summon shadow trap and keepsake-cave maps by define_as, quests/keepsake.lua guards by makeEntityByName SHADOW_CLAW: define_as is always kept on the actor.',
        other_lookups='heartGloomBase only resolves define_as-less families (no change); temporal clones keep define_as and resolve shared names by define_as; random-boss origins go through exactIdentity; audit_completion planning map lists the shared name once with both ids.')
    ev = dict(schema=1, task='monster-batch-ag: last off-list dungeon-pool batch, special cases; static source verification only; no game launch',
              identities=identities, auxiliary_sources=auxiliary, shader_policy=shader_policy, same_name_policy=same_name,
              summons_and_same_body_copies=[
                  'Hatchling escorts 3 hatchlings, drake escorts a hatchling, greater wyrm escorts two drakes: same leaves, same tokens.',
                  'dragon_lair vault and 32-chambers/tannen-tower filters take the pool leaves by exact name; drake-cave event loads multihued-drake.lua.',
                  'Shimmering crystal summons wisps (elemental/light), separate native bodies.',
                  'Generic temporal clones keep define_as; shared-name clones resolve by define_as.',
                  'createRandomBoss tall-body greater wyrm stays native under the existing captureRandomOrigin policy (native-tall origin only for uniques).'],
              runtime_mutation_scan='Breath, claw, wing buffet, silence/disarm (drakes), Elemental Bolt/Summon/Phase Door (crystals), keepsake Phase Door/Blindside/Dominate and Willful Strike/Reproach/Mind Sear (shadows) are activated attacks or particles; no actor image, type, shader, add_mos or replace_display write. Any runtime appearance change still falls through existing guards.',
              excluded=['overpowered greater multi-hued wyrm (Vor Armoury, other name)', 'Ureslak the Prismatic (unique)', 'Arena golden crystal', 'shadowy assassin and dreaming horror shaders'])
    out = ADDON / EVDIR
    out.write_text(json.dumps(ev, ensure_ascii=False, indent=2) + '\n')
    families = {}
    for group, ids in FAMILIES.items():
        c = Image.new('RGBA', (384, ((len(ids) + 2) // 3) * 128))
        for n, i in enumerate(ids):
            c.alpha_composite(Image.open(ADDON / 'data/gfx/tokens' / f'{i}.png').convert('RGBA'), (n % 3 * 128, n // 3 * 128))
        p = HERE / 'refs' / f'{group}.png'
        c.save(p)
        families[group] = dict(path=ART_REL + 'refs/' + p.name, sha256=sha(ART_REL + 'refs/' + p.name), role='family',
                               note='Shipped siblings row order: ' + ', '.join(ids) + '. Compare shape; do not copy anatomy.')
    packs = {}
    for row, i in zip(ROWS, identities):
        id_, name, file, anchor, define_as, typ, sub, png, tall, group, shader, subject, contrast = row
        dark = group == 'shadows'
        refs = [dict(path=ae.STYLE, sha256=sha(ae.STYLE), role='style', note='Approved tabletop disc, camera, lighting only; do not copy creature.'),
                dict(path=NPC + png, sha256=sha(NPC + png), role='identity', note='Inspected native identity and anatomy, ' + str(i['native_image_size'])),
                families[group]]
        a = dict(asset_id=id_, native_name=name, scope='class a off-list pool; ' + i['source']['path'] + ':' + str(i['source']['line']),
                 sources=[i['source'], i['base_source']] + i['extra_sources'] + auxiliary[:2], references=refs,
                 contrast_dimensions=['silhouette', 'value', 'hue'],
                 prompt_fields=dict(subject=subject + ae.CHEAT, contrast=contrast, composition=ae.COMP + (ae.DARKFIX if dark else ''),
                                    palette='Mid-light body masses and broad pale upper-left highlights, thin bright rim. ' + ae.DISC + ' Keep whole disc at reference lightness; no cast shadow or colour spill.'),
                 kind='creature', max_attempts=2, gate='ready', gate_reason=i['structure'] + ' Static evidence only; live separate.',
                 render_evidence=[dict(path='game/addons/tome-checker-revised/' + EVDIR, sha256=hashlib.sha256(out.read_bytes()).hexdigest())])
        packs.setdefault(PACK[id_], []).append(a)
    for n, assets in packs.items():
        names = [a['native_name'] for a in assets]
        assert len(names) == len(set(names)), 'shared-name identities must be in different packs'
        p = ADDON / f'art/production/batches/monster-batch-ag-{n}.json'
        if not p.exists():
            p.write_text(json.dumps(dict(schema=1, batch_id=f'monster-batch-ag-{n}', assets=assets), ensure_ascii=False, indent=2) + '\n')
    admitted = json.loads((HERE / 'final-admission.json').read_text())['accepted_ids'] if (HERE / 'final-admission.json').exists() else IDS
    (HERE / 'catalog.json').write_text(json.dumps([dict(id=i) for i in admitted], indent=2) + '\n')
    (HERE / 'catalog.js').write_text('window.monsterCatalog = ' + (HERE / 'catalog.json').read_text().strip() + ';\n')
    canvas = Image.new('RGBA', (7 * 190, 340), (48, 48, 48, 255)); draw = ImageDraw.Draw(canvas)
    for n, i in enumerate(identities):
        im = Image.open(WS / i['native_image_path']).convert('RGBA')
        im = im.resize((128, 256 if i['native_tall'] else 128), Image.Resampling.NEAREST)
        draw.text((n * 190 + 3, 3), i['id'], fill='white'); canvas.alpha_composite(im, (n * 190 + 20, 30))
    canvas.save(HERE / 'refs' / 'native-identities.png')


if __name__ == '__main__':
    build()
