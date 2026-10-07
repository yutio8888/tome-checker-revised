"""Batch TA-2 rework pack for the identity whose first master passed the disc
geometry but measured below the unchanged 65 masked-body floor. Fresh pack handed
to the same wrapper; the first master is the identity/edit anchor so the design is
preserved and only the body value changes. Static preparation only.
"""
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
EVDIR = 'evidence/monster-batch-ta2-20261001/source-contracts.json'
A = 'game/addons/tome-checker-revised/'

spec = importlib.util.spec_from_file_location('ae', HERE.parent / 'monster-batch-ae/make_batches.py')
ae = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ae)
sha = ae.sha

DISC_NEUTRAL = ("The disc is a NEUTRAL physical prop and must NOT be darkened with the creature: render "
                "the charcoal-brown plate and its bronze-grey bevel at EXACTLY the style reference's own "
                "lightness, evenly all round, including the outer sixth ring band and the plate directly "
                "under and beside the creature. Add no contact shadow, glow, bounce light or colour spill "
                "onto the plate; only the creature's own surfaces get the lighter values.")

ROWS = [
 dict(id='thalore-hunter', group='thalore', floor=64.27,
      subject=("A green-clad THALORE elf with a pointed LEAF-GREEN HOOD and pointed ears, in the SAME pose "
               "and gear as the identity reference master: a leaf-green tunic and leather bracers, both arms "
               "DRAWING a wooden longbow with a nocked arrow, a quiver of white-fletched arrows over the "
               "shoulder, green leggings and brown boots, alert wide archer stance. Keep the exact pose, "
               "camera, composition and gear of the identity reference. Raise the whole body to clearly "
               "LIGHTER value: a bright spring-green / yellow-green tunic and hood with broad pale "
               "yellow-green highlight planes on every upper-left surface, light tan leather and a pale "
               "wood bow, a light face, and a thin bright pale rim along the outline, so the figure reads as "
               "a light green shape on the dark disc at 48px."),
      contrast=("Identity is unchanged from the first master: a pointed green hood, a drawn bow and a quiver, "
                "versus the gold-armoured vertical-bow elven archer/companion-archer and the cloaked berethh. "
                "Only the body value is corrected upward; the disc must stay at the style reference's own "
                "lightness."),
      palette=("Bright mid-light spring-green and yellow-green body masses with broad upper-left highlights "
               "and a thin bright rim. Light tan leather and a pale wood bow. " + ae.DISC + " " + DISC_NEUTRAL)),
]
BATCH = 'monster-batch-ta2-rework-1'


def build():
    ev = json.loads((ROOT / EVDIR).read_text())
    by_id = {i['id']: i for i in ev['identities']}
    assets = []
    for row in ROWS:
        ident = by_id[row['id']]
        master = A + f'art/monster-batch-ta2/masters/{row["id"]}-v1.png'
        family = dict(path=A + f'art/monster-batch-ta2/refs/{row["group"]}.png',
                      sha256=sha(A + f'art/monster-batch-ta2/refs/{row["group"]}.png'), role='family',
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
            scope='TA-2 rework pack (body value below the unchanged 65 floor); ' + ident['source']['path'] + ':' + str(ident['source']['line']),
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
