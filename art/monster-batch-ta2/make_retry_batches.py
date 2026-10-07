"""Batch TA-2 retry packs for calls that failed at the wrapper (style-gate or
provenance) before any receipt existed. A failed check is an infrastructure
retry, never a reason to stop or leave the identity native; the same task is
re-issued in a fresh versioned pack with no threshold or floor changed.
Static preparation only.
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

DISC_NEUTRAL = ("The disc is a NEUTRAL physical prop and must NOT be brightened or darkened with the "
                "creature's value: render the charcoal-brown plate and its bronze-grey bevel at EXACTLY the "
                "style reference's own lightness, evenly all round, including the outer sixth ring band and "
                "the plate directly under and beside the creature, and do NOT lighten the plate under the "
                "creature's pale shirt or skin. Add no contact shadow, glow, bounce light or colour spill "
                "onto the plate.")

# (asset_id, source pack number, extra composition)
RETRIES = [
    ('halfling-slinger', '2', ''),
    ('halfling-gardener', '2', DISC_NEUTRAL),
]
BATCH = 'monster-batch-ta2-retry-1'


def build():
    out = ROOT / f'art/production/batches/{BATCH}.json'
    if out.exists():
        print('retry manifest exists:', out)
        return
    source = {}
    for n in ('1', '2', '3', '4', '5'):
        for a in json.loads((ROOT / f'art/production/batches/monster-batch-ta2-{n}.json').read_text())['assets']:
            source[a['asset_id']] = a
    assets = []
    for id_, src_pack, extra in RETRIES:
        a = json.loads(json.dumps(source[id_]))
        a['scope'] += ' (retry pack ' + BATCH + '; first call failed the wrapper gate/infrastructure, no master)'
        if extra:
            a['prompt_fields']['composition'] = a['prompt_fields']['composition'] + ' ' + extra
        assets.append(a)
    out.write_text(json.dumps(dict(schema=1, batch_id=BATCH, assets=assets), ensure_ascii=False, indent=2) + '\n')
    print('retry manifest:', out, len(assets), 'assets')


if __name__ == '__main__':
    build()
