"""AE appended retry packs. Total budget is checked across all packs.
No style, contrast or luminance threshold may be overridden.
"""
from copy import deepcopy

def add_retries(packs):
    # Pack 5: hummerhorn call 1 in pack 1 returned no image path;
    # provenance-rejected, no master admitted. Same brief, second call.
    base = next(a for a in packs[1] if a['asset_id']=='hummerhorn')
    packs[5] = [deepcopy(base)]
