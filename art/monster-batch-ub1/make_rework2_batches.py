"""UB-1 rework-2/3: single-identity refinement packs for Fallen Sun Paladin
Aeryn and Chronolith Clone, both already mapped by monster-batch-ub1. Static
preparation only: pinned source contracts, refinement briefs, no generation.
"""
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WS = ROOT.parents[2]
D = 'game/modules/tome/data/'
EVDIR = 'evidence/monster-batch-ub1-20261001/source-contracts.json'
A = 'game/addons/tome-checker-revised/'

spec = importlib.util.spec_from_file_location('ae', HERE.parent / 'monster-batch-ae/make_batches.py')
ae = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ae)
sha = ae.sha


def pin(rel):
    return dict(path=rel, sha256=hashlib.sha256((WS / rel).read_bytes()).hexdigest())


DISC_NEUTRAL = ("The disc is a NEUTRAL physical prop: render the charcoal-brown plate and its bronze-grey "
                "bevel at EXACTLY the style reference's own lightness, evenly all round, including the outer "
                "sixth ring band and the plate directly under and beside the creature. Add no contact shadow, "
                "glow, bounce light or colour spill onto the plate.")

ROWS = [
 dict(id='fallen-sun-paladin-aeryn', batch='monster-batch-ub1-rework-2', family='sun-paladins',
      supersedes='fallen-sun-paladin-aeryn',
      reason=("The first two reworks made Fallen Aeryn a bright silver mirror of the High Aeryn token. "
              "The native sprite is visibly corrupted, so the design direction changes from 'bright silver "
              "plate' to 'dark blood-stained plate carried by a crimson aura and rim light', with a point-down "
              "two-handed greatsword so Fallen and High separate by both structure and value at 48px."),
      evidence=[pin(A + 'art/monster-batch-ub1/superseded/fallen-sun-paladin-aeryn-rework-v2.png'),
                pin(A + 'art/production/handoffs/monster-batch-ub1-rework-1/fallen-sun-paladin-aeryn/receipts/attempt-2.json')],
      ref_pair=A + 'art/monster-batch-ub1/refs/native-sun-paladin-pair.png',
      subject=("A tall grim fallen paladin woman: BLACKENED BLOOD-STAINED plate armour in dark oxblood and "
               "charcoal, thick smeared blood down the chest and greaves, torn dark-crimson cloth. The whole "
               "figure is wrapped in a BROAD GLOWING BLOOD-RED AURA with a strong crimson rim light along "
               "every upper-left edge and a bright red halo behind the shoulders, so the body reads as a "
               "luminous red figure and NEVER as a black mass. Pale blonde hair and a pale gaunt hollow-eyed "
               "face catch the light. She holds a heavy two-handed greatsword POINT-DOWN in front of her, "
               "both hands on the hilt, the bloody blade bright silver-red with a broad pale reflection face, "
               "its tip near the ground. Hunched forward in a spent, heavy stance, weight over the sword, a "
               "long tattered dark-crimson cloak trailing to one side."),
      contrast=("Fallen vs High Aeryn: a POINT-DOWN two-handed greatsword in a grim hunched stance, dark "
                "blood-soaked plate and a strong crimson aura, versus the High Aeryn's bright polished silver "
                "plate, upright one-handed sword and free open hand. Structure and value must separate them at "
                "48px. The dark armour is carried by broad crimson glow and pale red rim highlights, never a "
                "black silhouette. Distinct from the broad dark Aluin knight by being a slender woman."),
      palette=("Dark blood-crimson and charcoal armour masses, but with broad luminous blood-red glow, strong "
               "crimson rim light, pale blonde hair and face, and a bright silver-red blade reflection. " +
               ae.DISC + " " + DISC_NEUTRAL),
      ),
 dict(id='chronolith-clone', batch='monster-batch-ub1-rework-3', family='temporal-horrors',
      supersedes='chronolith-clone',
      reason=("The first attempt collapsed the native six-'limbed' temporal horror into a cocoon/egg bundle "
              "that does not exist in the sprite. The design direction changes to paint the exact twin "
              "creature (cream bony torso plate, blue-violet body, curling blue arms) and separate it from the "
              "Twin by a mirrored arm arrangement plus a faint offset temporal afterimage, not by colour."),
      evidence=[pin(A + 'art/monster-batch-ub1/superseded/chronolith-clone-v1.png'),
                pin(A + 'art/production/handoffs/monster-batch-ub1-2/chronolith-clone/receipts/attempt-1.json')],
      ref_pair=A + 'art/monster-batch-ub1/refs/native-chronolith-pair.png',
      subject=("A temporal horror, the SAME creature as the Chronolith Twin: a narrow upright body whose "
               "torso is a CREAM-BONE armour plate of stacked vertical rib ridges and segmented panels, "
               "blue-violet limbs, and a blue-violet elongated head with large glossy black insectile eyes. "
               "It has FOUR long thin curling blue-violet arms: the LEFT upper arm is raised high and curled "
               "inward across the head, the RIGHT upper arm is lowered and coiled across the belly, and the "
               "two lower arms curl outward and down; two short blue legs below the hem. This MIRRORED, closed "
               "arm arrangement contrasts the Twin's symmetric raised-arm fan. Behind and up-left of the body "
               "floats a FAINT DUPLICATED TEMPORAL AFTERIMAGE: an OPAQUE pale blue-grey echo of the same "
               "silhouette offset by about a fifth of the body height, drawn as a flat low-contrast ghost "
               "outline with a thin pale edge and no interior face or eye detail, clearly a temporal echo and "
               "not a second solid creature."),
      contrast=("Same creature as the Twin but structurally distinguished: a mirrored/opposite arm layout "
                "(one arm curled across the head, one across the belly) plus a faint offset temporal afterimage "
                "behind it, versus the Twin's upright symmetric raised-arm fan. The arm layout and the echo "
                "outline must separate the pair at 48px; this is not a colour change. Both still differ from "
                "the temporal stalker's low dark blade mass."),
      palette=("Cream-bone torso plate with pale upper highlights, mid-light blue-violet limbs and head, black "
               "insectile eye points, and a pale desaturated blue-grey opaque afterimage echo. " + ae.DISC +
               " " + DISC_NEUTRAL),
      ),
]


def build():
    ev = json.loads((ROOT / EVDIR).read_text())
    by_id = {i['id']: i for i in ev['identities']}
    for row in ROWS:
        ident = by_id[row['id']]
        family = dict(path=f'game/addons/tome-checker-revised/art/monster-batch-ub1/refs/{row["family"]}.png',
                      sha256=sha(f'game/addons/tome-checker-revised/art/monster-batch-ub1/refs/{row["family"]}.png'),
                      role='family',
                      note='Shipped siblings; stay structurally distinct, do not copy their anatomy.')
        refs = [
            dict(path=ae.STYLE, sha256=sha(ae.STYLE), role='style',
                 note='Approved neutral disc/camera/light only; do not copy its creature.'),
            dict(path=ident['native_image_path'], sha256=ident['native_image_sha256'], role='identity',
                 note='Exact native body 64x128; match its portrait.'),
            dict(path=row['ref_pair'], sha256=sha(row['ref_pair']), role='family',
                 note='Native pair 2x nearest: the same character/creature in its two states.'),
        ]
        render = [dict(path='game/addons/tome-checker-revised/' + EVDIR,
                       sha256=hashlib.sha256((ROOT / EVDIR).read_bytes()).hexdigest())]
        if row['id'] == 'archmage-tarelion':
            render.append(pin(A + 'art/monster-batch-ub1/refs/tarelion-probe.md'))
        asset = dict(
            asset_id=row['id'], native_name=ident['native_name'],
            scope='UB-1 rework; ' + ident['source']['path'] + ':' + str(ident['source']['line']),
            sources=ident['sources'] + ev['auxiliary_sources'],
            references=refs, contrast_dimensions=['silhouette', 'value', 'hue'],
            prompt_fields=dict(subject=row['subject'] + ae.CHEAT, contrast=row['contrast'],
                               composition=ae.COMP + ae.DARKFIX, palette=row['palette']),
            kind='creature', max_attempts=2, gate='ready',
            gate_reason=ident['structure'] + ' Coordinator-requested rework; see ' + EVDIR,
            render_evidence=render,
            refinement=dict(supersedes=row['supersedes'], previous_batch='monster-batch-ub1',
                            design_change_reason=row['reason'], evidence=row['evidence']),
        )
        out = ROOT / f'art/production/batches/{row["batch"]}.json'
        if not out.exists():
            out.write_text(json.dumps(dict(schema=1, batch_id=row['batch'], assets=[asset]), ensure_ascii=False, indent=2) + '\n')
        print('rework manifest:', out)


if __name__ == '__main__':
    build()
