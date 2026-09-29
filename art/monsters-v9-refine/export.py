"""Export the V9-refine native-alpha masters with the repository's existing C converter.

Python only reads image metadata and runs the same `tools/export_token.c` binary
used by `tools/build_monster_art.py`; no pixel is painted here. Every 128px export
is re-measured by `tools/check_token_style.py` with the grandfather waiver OFF:
`skeleton-warrior` is a new identity and `giant-brown-mouse` is a replacement for
an identity that was never grandfathered, so both must meet the acceptance table
on their own. The C0b batch's own masters and exports are not touched.
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image

ART = Path(__file__).resolve().parent
ROOT = ART.parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import check_token_style  # noqa: E402

CHOICES = json.loads((ART / 'selected-masters.json').read_text())
BINARY = ART / 'export_token-bin'
subprocess.run(['cc', '-O2', '-Wall', '-Wextra', str(ROOT / 'tools/export_token.c'),
                '-o', str(BINARY), '-lpng', '-lm'], check=True)

report = {'method': 'existing C export_token.c; native alpha; bbox placement; premultiplied-alpha '
                    'area downsampling; 128px style gate with allow_grandfather=False',
          'assets': []}
failures = []
for asset_id, source_name in CHOICES.items():
    source = ART / source_name
    with Image.open(source) as image:
        assert image.mode == 'RGBA' and image.width == image.height >= 512, (source, image.mode)
        alpha = image.getchannel('A')
        assert alpha.getextrema()[0] == 0 and alpha.getextrema()[1] >= check_token_style.MASTER_ALPHA_MAX_FLOOR
        assert all(alpha.getpixel(p) == 0 for p in ((0, 0), (image.width - 1, 0),
                                                    (0, image.height - 1), (image.width - 1, image.height - 1)))
    item = {'id': asset_id, 'master': source_name,
            'sha256': hashlib.sha256(source.read_bytes()).hexdigest(), 'exports': []}
    for size in (48, 64, 96, 128, 256):
        target = ART / 'exports' / str(size) / f'{asset_id}.png'
        target.parent.mkdir(parents=True, exist_ok=True)
        stats = json.loads(subprocess.check_output([str(BINARY), str(source), str(target), str(size)], text=True))
        with Image.open(target) as image:
            assert image.mode == 'RGBA' and image.size == (size, size)
            alpha = image.getchannel('A')
            assert all(alpha.getpixel(p) == 0 for p in ((0, 0), (size - 1, 0), (0, size - 1), (size - 1, size - 1)))
            bounds = alpha.point(lambda a: 255 if a > 8 else 0).getbbox()
            occupancy = max(bounds[2] - bounds[0], bounds[3] - bounds[1]) / size
            assert .83 <= occupancy <= .91, (target, occupancy)
        item['exports'].append({'path': target.relative_to(ART).as_posix(), **stats,
                                'sha256': hashlib.sha256(target.read_bytes()).hexdigest()})
        if size == 128:
            gated = check_token_style.check_asset(target, source, asset_id, allow_grandfather=False)
            item['style_gate'] = {
                'baseline': list(check_token_style.BASELINE_SECTOR_MEDIANS),
                'allow_grandfather': False,
                'base_drift': gated['token']['base_drift'],
                'max_sector_intrusion': gated['token']['max_sector_intrusion'],
                'max_opaque_radius': gated['token']['max_opaque_radius'],
                'export_occupancy': occupancy,
                'blocking': gated['blocking'], 'warnings': gated['warnings'],
                'grandfathered': gated['grandfathered'], 'waived': gated['waived'],
                'passed': gated['passed'],
            }
            for warning in gated['warnings']:
                print(f'WARN {asset_id}: {warning}')
            if not gated['passed']:
                detail = '；'.join(f['detail'] for f in gated['findings']
                                   if f['level'] == 'blocking' and not f['ok'])
                failures.append(f'{asset_id}: {detail}')
                print(f'FAIL {asset_id}: {detail}')
    report['assets'].append(item)
(ART / 'export-report.json').write_text(json.dumps(report, indent=2) + '\n')
BINARY.unlink()
if failures:
    raise SystemExit('FAIL: 风格门控未通过：\n' + '\n'.join(failures))
print(f"PASS: {len(report['assets'])} masters, {sum(len(a['exports']) for a in report['assets'])} exports, "
      f"style gate on without grandfather waiver")
