"""UB-2 rework packs for the two identities whose first attempt passed the disc
geometry but fell below the unchanged 65 masked-body floor. Fresh packs handed
to the same wrapper; the first master is the identity/edit anchor so the design
is preserved and only the body value changes. Static preparation only.
"""
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WS = ROOT.parents[2]
D = 'game/modules/tome/data/'
EVDIR = 'evidence/monster-batch-ub2-20261001/source-contracts.json'
A = 'game/addons/tome-checker-revised/'

spec = importlib.util.spec_from_file_location('ae', HERE.parent / 'monster-batch-ae/make_batches.py')
ae = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ae)
sha = ae.sha

DISC_NEUTRAL = ("The disc is a NEUTRAL physical prop and must NOT be brightened with the creature: render "
                "the charcoal-brown plate and its bronze-grey bevel at EXACTLY the style reference's own "
                "lightness, evenly all round, including the outer sixth ring band and the plate directly "
                "under and beside the creature. Add no contact shadow, glow, bounce light or colour spill "
                "onto the plate; only the creature's own surfaces get the lighter values.")

ROWS = [
 dict(id='zemekkys', group='elf-story', floor=63.64,
      subject=("A pale shalore elf man with short pale-blond hair and a calm bare head, in the SAME layered "
               "blue robe and chevron-patterned blue shoulder mantle as the identity reference master, with a "
               "small pale chest badge, brown belt, blue trousers and brown boots, EMPTY relaxed hands, no "
               "hat and no staff. Keep the exact pose, camera, composition and robe design of the identity "
               "reference. Raise the whole body to clearly LIGHTER value: a bright sky-blue robe and mantle "
               "with broad pale blue-white highlight planes on every upper-left surface, a light face and "
               "hair, and a broad pale rim along the outline, so the figure reads as a light blue shape on "
               "the dark disc at 48px."),
      contrast=("Identity is unchanged from the first master: bare-headed unarmoured shalore in a layered "
                "blue robe with a chevron mantle and empty hands, no hat and no staff. Only the body value "
                "is corrected upward; the disc must stay at the style reference's own lightness."),
      palette=("Bright mid-light sky-blue and pale blue-white body masses with broad upper-left highlights "
               "and a thin bright rim. " + ae.DISC + " " + DISC_NEUTRAL)),
 dict(id='rak-shor-cultist', group='orc-casters', floor=49.89,
      subject=("An old gaunt orc with a bald head, in the SAME dark hooded robe as the identity reference "
               "master, hood raised with a visible shadowed face and small pale eyes, rust-orange trim along "
               "the hood and hem, both arms spread down and outward with long bare clawed hands, no crown and "
               "no staff. Keep the exact pose, camera, composition and robe design of the identity reference. "
               "Raise the whole body to clearly LIGHTER value: a warm brick-red / ochre robe with broad pale "
               "ochre highlight planes on the hood, shoulders and hem, and light moss-green skin with pale "
               "green highlights on the face and arms, plus a thin bright rim, so the figure reads as a light "
               "warm-red-and-green shape on the dark disc at 48px."),
      contrast=("Identity is unchanged from the first master: a hooded, uncrowned, staff-less orc in a "
                "maroon-red robe with out-held empty hands. Only the body value is corrected upward; the "
                "hood, robe cut and empty hands must stay exactly as in the identity reference, and the disc "
                "must stay at the style reference's own lightness."),
      palette=("Warm mid-light brick-red and ochre robe masses, light moss-green skin, broad upper-left "
               "highlights and a thin bright rim. " + ae.DISC + " " + DISC_NEUTRAL)),
]

BATCH = 'monster-batch-ub2-rework-1'


def build():
    ev = json.loads((ROOT / EVDIR).read_text())
    by_id = {i['id']: i for i in ev['identities']}
    assets = []
    for row in ROWS:
        ident = by_id[row['id']]
        master = A + f'art/monster-batch-ub2/masters/{row["id"]}-v1.png'
        family = dict(path=A + f'art/monster-batch-ub2/refs/{row["group"]}.png',
                      sha256=sha(A + f'art/monster-batch-ub2/refs/{row["group"]}.png'), role='family',
                      note='Shipped siblings; stay structurally distinct, do not copy their anatomy.')
        refs = [
            dict(path=ae.STYLE, sha256=sha(ae.STYLE), role='style',
                 note='Approved neutral disc/camera/light only; do not copy its creature.'),
            dict(path=master, sha256=sha(master), role='identity',
                 note='First-attempt master of this same identity: keep its design, pose, camera and composition; correct only the body value.'),
            family,
        ]
        assets.append(dict(
            asset_id=row['id'], native_name=ident['native_name'],
            scope='UB-2 rework pack (body value below the unchanged 65 floor); ' + ident['source']['path'] + ':' + str(ident['source']['line']),
            sources=ident['sources'] + ev['auxiliary_sources'],
            references=refs, contrast_dimensions=['silhouette', 'value', 'hue'],
            prompt_fields=dict(subject=row['subject'] + ae.CHEAT, contrast=row['contrast'],
                               composition=ae.COMP, palette=row['palette']),
            kind='creature', max_attempts=2, gate='ready',
            gate_reason=ident['structure'] + ' Rework after the first master measured ' + str(row['floor']) + ' (< 65); see ' + EVDIR,
            render_evidence=[dict(path=A + EVDIR, sha256=hashlib.sha256((ROOT / EVDIR).read_bytes()).hexdigest())],
        ))
    out = ROOT / f'art/production/batches/{BATCH}.json'
    if not out.exists():
        out.write_text(json.dumps(dict(schema=1, batch_id=BATCH, assets=assets), ensure_ascii=False, indent=2) + '\n')
    print('rework manifest:', out, len(assets), 'assets')


if __name__ == '__main__':
    build()
