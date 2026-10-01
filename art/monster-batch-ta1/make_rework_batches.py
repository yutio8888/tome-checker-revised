"""Coordinator-requested human-guard rework; keeps all original TA-1 packs/gates.

The selected human-guard v2 read too close to the shipped elven-guard and was
unfaithful to its native sprite. This prepares a separately reviewed rework pack
with the unchanged style/disc gates and body floor.
"""
import copy
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WS = ROOT.parents[2]
REL = 'game/addons/tome-checker-revised/'
REWORK = HERE / 'rework'


def pin(path):
    return dict(path=REL + path, sha256=hashlib.sha256((ROOT / path).read_bytes()).hexdigest())


def build():
    REWORK.mkdir(exist_ok=True)
    request = dict(
        authority='Coordinator review of commit dcb5c982 (2026-10-01, this task)',
        accepted_previous=['apprentice-mage', 'pyromancer', 'cryomancer', 'geomancer', 'tempest',
                           'derth-guard', 'last-hope-guard', 'halfling-guard', 'dwarven-guard',
                           'elvala-guard', 'slaver', 'enthralled-slave'],
        rework={'human-guard':
                'Rejected v2 read almost identical to the shipped elven-guard token (green tunic/tabard, '
                'green shield, upright sword) and was unfaithful to native npc/humanoid_human_human_guard.png. '
                'Redraw faithful to the native sprite: brown studded leather jerkin with shoulder pads as the '
                'dominant torso mass, bare head with short hair, green trousers, a grey steel heater shield held '
                'out to the side, and the sword held diagonally across the body. No green tabard and no green '
                'shield; stay clearly distinct from elven-guard and caravan-guard at 48 px.'},
        no_game_launch=True, body_floor=65.0, disc_and_style_gates='unchanged')
    r = REWORK / 'coordinator-rework-human-guard.json'
    if not r.exists():
        r.write_text(json.dumps(request, ensure_ascii=False, indent=2) + '\n')

    original = next(a for a in json.loads((ROOT / 'art/production/batches/monster-batch-ta1-2.json').read_text())['assets']
                    if a['asset_id'] == 'human-guard')
    a = copy.deepcopy(original)
    a['scope'] += ('; coordinator-requested TA-1 rework on dcb5c982: faithful native jerkin/steel shield, '
                   'no green tabard; original TA-1 calls and masters preserved')
    a['prompt_fields']['subject'] = (
        'A human TOWN GUARD drawn exactly from the native sprite: a rich BROWN LEATHER PADDED JERKIN with a '
        'vertical row of small metal studs down the chest and warm tan piping, over broad brown leather SHOULDER '
        'PADS; below the belt, plain GREEN TROUSERS. BARE HEAD with short brown hair, a clean-shaven face, bare '
        'lower legs and simple brown shoes. In the right hand a straight arming SWORD is held low with the blade '
        'angled diagonally across the body; the left arm holds a large GREY STEEL HEATER SHIELD out to the side, '
        'its face plain weathered steel with a dark central boss. NO green tabard, NO green tunic, NO green '
        'shield, NO helmet and NO cloak. Render mid-light warm browns and greens with broad pale upper-left '
        'highlight planes on the jerkin, shoulder pads and steel shield, and a thin bright rim, so the figure is '
        'clearly lighter than the charcoal disc; aim the central body luminance comfortably above 65, around '
        '80-95, while the neutral disc stays unchanged. Every surface is SOLID OPAQUE material.')
    a['prompt_fields']['contrast'] = (
        'Structural identity versus the shipped siblings: brown studded leather jerkin with shoulder pads, bare '
        'head, green trousers and a large out-held GREY STEEL heater shield. The rejected v2 brown-green tunic '
        'and green shield must not be copied. Versus elven-guard (green-and-gold outfit with a green-rimmed '
        'round shield and a helmeted blonde head) and caravan-guard (full chainmail body with a round shield and '
        'spear), the torso cloth is dominantly BROWN and the shield is plain grey steel; no green cloth on the '
        'torso or shield. Read the difference by silhouette and large value masses at 48 px, never by hue alone. '
        'No faction rings, health, shield, rank marks, selection, text or numbers.')
    a['gate_reason'] += (' Coordinator-authorized faithful-native redesign after the dcb5c982 review; not a waiver '
                         'and no gate/threshold changed.')
    a['refinement'] = dict(
        supersedes='human-guard',
        previous_batch='monster-batch-ta1-2',
        design_change_reason=request['rework']['human-guard'] +
        ' This is a separately reviewed change of torso material, head treatment and shield colour/pose, not a '
        'colour-only correction or a retry note.',
        evidence=[pin('art/production/handoffs/monster-batch-ta1-2/human-guard/receipts/attempt-2.json'),
                  pin('art/production/handoffs/monster-batch-ta1-2/human-guard/imagegen-calls/call-2/call.json'),
                  pin('art/monster-batch-ta1/rework/coordinator-rework-human-guard.json')])
    a['render_evidence'] = a['render_evidence'] + [pin('art/monster-batch-ta1/rework/coordinator-rework-human-guard.json')]
    a['max_attempts'] = 2

    p = ROOT / 'art/production/batches/monster-batch-ta1-rework-1.json'
    if not p.exists():
        p.write_text(json.dumps(dict(schema=1, batch_id='monster-batch-ta1-rework-1', assets=[a]),
                                ensure_ascii=False, indent=2) + '\n')
    print('wrote', p.relative_to(ROOT))


if __name__ == '__main__':
    build()
