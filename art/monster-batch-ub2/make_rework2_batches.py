"""UB-2 rework-2: the coordinator-ordered Sun Paladin Guren redraw. The first
master read as warm bronze-gold armour, unfaithful to the dark gunmetal native
sprite and too close to the gold human-sun-paladin / Rodmour family. This pack
is a separately reviewed refinement brief (the identity is now mapped), anchored
on the exact native sprite, and changes the design direction to cold steel-grey
plate with only a gold rim-light/halo. Static preparation only.
"""
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WS = ROOT.parents[2]
EVDIR = 'evidence/monster-batch-ub2-20261001/source-contracts.json'
A = 'game/addons/tome-checker-revised/'

spec = importlib.util.spec_from_file_location('ae', HERE.parent / 'monster-batch-ae/make_batches.py')
ae = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ae)
sha = ae.sha

DISC_NEUTRAL = ("The disc is a NEUTRAL physical prop and must NOT be tinted or brightened with the creature: "
                "render the charcoal-brown plate and its bronze-grey bevel at EXACTLY the style reference's own "
                "lightness, evenly all round, including the outer sixth ring band and the plate directly under "
                "and beside the creature. Add no contact shadow, glow, bounce light or colour spill onto the "
                "plate; only the creature's own surfaces and its gold halo get the lighter values.")

SUBJECT = (
 "A lean human knight in cold DARK GUNMETAL STEEL full plate, painted in mid-light grey with broad pale "
 "steel-blue upper-left highlight planes, darker recessed seams and dark leather straps, so the armour stays "
 "clearly lighter than the disc but is unmistakably COLD STEEL, never bronze and never gold. A closed knight's "
 "helm with a low crest/plume ridge along the top and a narrow dark visor slit, a small pale chin guard. A DARK "
 "STEEL KITE SHIELD on the LEFT forearm bearing a small gold rayed-sun emblem. A long straight sword held LOW "
 "and diagonally across the body in the RIGHT hand, point toward the lower right, the blade pale polished steel. "
 "The whole figure is edged with a thin warm GOLD RIM LIGHT along its upper-left outline and sits inside a soft "
 "GOLDEN HALO GLOW behind the shoulders and around the silhouette (the native golden emanation). The gold exists "
 "ONLY as rim light and halo; NO gold or bronze armour, no gold tabard, no gold plates."
)

CONTRAST = (
 "Structurally and in value distinct from the shipped gold human-sun-paladin (bulky WARM GOLD plate, huge round "
 "sun-disc, forward war-hammer) and the white-gold cape-and-mace Rodmour: Guren is COLD gunmetal steel, a closed "
 "crested helm and a dark kite shield with a small sun device, with the long sword held LOW and diagonal. At 48px "
 "he must read as the grey-steel knight carried by a gold halo, not as another gold paladin. No faction rings, "
 "health, shield, rank marks, selection, text or numbers."
)

PALETTE = (
 "Cold mid-light gunmetal grey and pale steel-blue body masses with broad upper-left highlights and a thin warm "
 "gold RIM LIGHT / halo. Dark steel shield with a small gold sun device. " + ae.DISC + " " + DISC_NEUTRAL
)

BATCH = 'monster-batch-ub2-rework-2'


def pin(rel):
    return dict(path=rel, sha256=hashlib.sha256((WS / rel).read_bytes()).hexdigest())


def build():
    ev = json.loads((ROOT / EVDIR).read_text())
    ident = next(i for i in ev['identities'] if i['id'] == 'sun-paladin-guren')
    family = dict(path=A + 'art/monster-batch-ub2/refs/sun-paladins.png',
                  sha256=sha(A + 'art/monster-batch-ub2/refs/sun-paladins.png'), role='family',
                  note='Shipped siblings human-sun-paladin, high-sun-paladin-rodmour, aluin-the-fallen, argoniel, elandar; stay structurally distinct, do not copy their anatomy.')
    refs = [
        dict(path=ae.STYLE, sha256=sha(ae.STYLE), role='style',
             note='Approved neutral disc/camera/light only; do not copy its creature.'),
        dict(path=ident['native_image_path'], sha256=ident['native_image_sha256'], role='identity',
             note='Exact native body 64x64: DARK gunmetal steel plate, closed crested helm, dark kite shield with a gold sun emblem, long sword low and diagonal, golden halo. Paint this portrait.'),
        family,
    ]
    asset = dict(
        asset_id='sun-paladin-guren', native_name=ident['native_name'],
        scope='UB-2 rework-2 (coordinator-ordered redraw: cold steel-grey, not bronze-gold); ' + ident['source']['path'] + ':' + str(ident['source']['line']),
        sources=ident['sources'] + ev['auxiliary_sources'],
        references=refs, contrast_dimensions=['silhouette', 'value', 'hue'],
        prompt_fields=dict(subject=SUBJECT + ae.CHEAT, contrast=CONTRAST,
                           composition=ae.COMP + ae.DARKFIX, palette=PALETTE),
        kind='creature', max_attempts=2, gate='ready',
        gate_reason=ident['structure'] + ' Coordinator rework: first master read as warm bronze-gold; see ' + EVDIR,
        render_evidence=[dict(path=A + EVDIR, sha256=hashlib.sha256((ROOT / EVDIR).read_bytes()).hexdigest())],
        refinement=dict(
            supersedes='sun-paladin-guren', previous_batch='monster-batch-ub2',
            design_change_reason=(
                "The first Guren master rendered the plate as warm bronze-gold with a gold tabard, which is "
                "unfaithful to the native dark gunmetal sprite and merges into the shipped gold human-sun-paladin "
                "and white-gold Rodmour at 48px. The design direction changes from warm bronze-gold armour to COLD "
                "gunmetal steel dominant, with a closed crested helm and a dark kite shield carrying only a small "
                "gold sun device; gold is reduced to a rim light and halo that keeps the luminance floor. This is a "
                "colour-and-value direction change, not a cosmetic retry."),
            evidence=[pin(A + 'art/monster-batch-ub2/superseded/sun-paladin-guren-v1.png'),
                      pin(A + 'art/production/handoffs/monster-batch-ub2-1/sun-paladin-guren/receipts/attempt-1.json')],
        ),
    )
    out = ROOT / f'art/production/batches/{BATCH}.json'
    if not out.exists():
        out.write_text(json.dumps(dict(schema=1, batch_id=BATCH, assets=[asset]), ensure_ascii=False, indent=2) + '\n')
    print('rework manifest:', out)


if __name__ == '__main__':
    build()
