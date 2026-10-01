"""UB-1 rework packs: a fresh, separately reviewed pack for an identity whose
first attempt failed a batch floor. Static preparation only: no generation.
"""
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WS = ROOT.parents[2]
D = 'game/modules/tome/data/'
NPC = D + 'gfx/shockbolt/npc/'
EVDIR = 'evidence/monster-batch-ub1-20261001/source-contracts.json'

spec = importlib.util.spec_from_file_location('ae', HERE.parent / 'monster-batch-ae/make_batches.py')
ae = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ae)
sha = ae.sha

# Subject/contrast/palette overrides for a design change after a failed attempt.
# Fallen Aeryn attempt 1 was faithful to the dark native sprite but its masked-body
# luminance was 49.08 (< the unchanged 65 floor).
DISC_NEUTRAL = ("The disc is a NEUTRAL physical prop and must NOT be brightened to match a bright body: "
                "render the charcoal-brown plate and its bronze-grey bevel at EXACTLY the style reference's "
                "own lightness, evenly all round, including the outer sixth ring band and the plate directly "
                "under and beside the creature. Add no contact shadow, no glow, no bounce light and no colour "
                "spill onto the plate. Only the creature's own surfaces get the brighter values.")

OVERRIDES = {
    'fallen-sun-paladin-aeryn': dict(
        subject=("A tall tragic woman in MID-LIGHT warm grey steel full plate with clearly lighter oxblood-red "
                 "trim and thin glowing crimson seams, a long tattered light-crimson cloak trailing "
                 "asymmetrically to one side; loose pale blonde hair and a pale gaunt face, all painted in "
                 "mid-light values that stay clearly LIGHTER than the charcoal disc. She grips a great "
                 "TWO-HANDED blood-dark greatsword PERFECTLY UPRIGHT in the centre of her chest with BOTH "
                 "hands on the hilt, the blade vertical down the body centre-line with a broad pale upper-left "
                 "highlight face, no shield. Slightly hunched forward with a heavy planted stance and a torn "
                 "asymmetrical cloak. Every armour plane on the upper-left is a broad pale highlight; the red "
                 "cape and trim are bright mid-crimson, never near-black."),
        contrast=("The Fallen Aeryn is defined by a centred TWO-HANDED vertical greatsword (both hands on the "
                  "hilt), a forward hunch and a tattered one-sided cloak, versus the High Aeryn's calm upright "
                  "one-handed off-side sword with a free open hand. Same character, different pose structure; "
                  "the sweep from near-black to mid-light grey-and-crimson is a value change that must keep the "
                  "silhouette clearly LIGHTER than the disc at 48px. Distinct from the broad dark Aluin knight "
                  "by being a slender woman."),
        palette=("Mid-light body masses with broad pale upper-left highlights and a thin bright rim. The plate is "
                 "warm mid-grey steel, the cloak and trim clearly light crimson, the blade pale silver with a "
                 "light reflection face. " + ae.DISC + " " + DISC_NEUTRAL +
                 " Keep the whole disc at reference lightness; no cast shadow or colour spill."),
    ),
}

BATCH = 'monster-batch-ub1-rework-1'


def build():
    ev = json.loads((ROOT / EVDIR).read_text())
    by_id = {i['id']: i for i in ev['identities']}
    assets = []
    for id_, ov in OVERRIDES.items():
        ident = by_id[id_]
        group = {
            'high-sun-paladin-aeryn': 'sun-paladins', 'fallen-sun-paladin-aeryn': 'sun-paladins',
            'caldizar': 'shertul', 'chronolith-twin': 'temporal-horrors', 'chronolith-clone': 'temporal-horrors',
            'temporal-defiler': 'temporal-horrors', 'corrupted-daelach': 'demons',
            'supreme-archmage-linaniil': 'archmages', 'archmage-tarelion': 'archmages',
        }[id_]
        family = dict(path=f'game/addons/tome-checker-revised/art/monster-batch-ub1/refs/{group}.png',
                      sha256=sha(f'game/addons/tome-checker-revised/art/monster-batch-ub1/refs/{group}.png'),
                      role='family',
                      note='Shipped siblings; stay structurally distinct, do not copy their anatomy.')
        refs = [
            dict(path=ae.STYLE, sha256=sha(ae.STYLE), role='style',
                 note='Approved neutral disc/camera/light only; do not copy its creature.'),
            dict(path=ident['native_image_path'], sha256=ident['native_image_sha256'],
                 role='identity', note='Exact native body 64x128; match its portrait.'),
            family,
        ]
        render_evidence = [dict(path='game/addons/tome-checker-revised/' + EVDIR,
                                sha256=hashlib.sha256((ROOT / EVDIR).read_bytes()).hexdigest())]
        if id_ == 'archmage-tarelion':
            render_evidence.append(dict(
                path='game/addons/tome-checker-revised/art/monster-batch-ub1/refs/tarelion-probe.md',
                sha256=sha('game/addons/tome-checker-revised/art/monster-batch-ub1/refs/tarelion-probe.md')))
        assets.append(dict(
            asset_id=id_, native_name=ident['native_name'],
            scope='UB-1 rework pack; ' + ident['source']['path'] + ':' + str(ident['source']['line']),
            sources=ident['sources'] + ev['auxiliary_sources'],
            references=refs, contrast_dimensions=['silhouette', 'value', 'hue'],
            prompt_fields=dict(subject=ov['subject'] + ae.CHEAT, contrast=ov['contrast'],
                               composition=ae.COMP + ae.DARKFIX, palette=ov['palette']),
            kind='creature', max_attempts=2, gate='ready',
            gate_reason=ident['structure'] + ' Rework after a failed batch floor; see ' + EVDIR,
            render_evidence=render_evidence,
        ))
    out = ROOT / f'art/production/batches/{BATCH}.json'
    if not out.exists():
        out.write_text(json.dumps(dict(schema=1, batch_id=BATCH, assets=assets), ensure_ascii=False, indent=2) + '\n')
    print('rework manifest:', out, len(assets), 'assets')


if __name__ == '__main__':
    build()
