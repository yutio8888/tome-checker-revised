"""Export selected native-alpha masters with the repository's existing C converter."""
import hashlib
import json
import subprocess
from pathlib import Path

from PIL import Image


ART = Path(__file__).resolve().parent
ROOT = ART.parents[1]
CHOICES = json.loads((ART / 'selected-masters.json').read_text())
BINARY = ART / 'export_token-bin'
subprocess.run(['cc', '-O2', '-Wall', '-Wextra', str(ROOT / 'tools/export_token.c'),
                '-o', str(BINARY), '-lpng', '-lm'], check=True)

report = {'method': 'existing C export_token.c; native alpha; bbox placement; premultiplied-alpha area downsampling', 'assets': []}
for asset_id, source_name in CHOICES.items():
    source = ART / source_name
    with Image.open(source) as image:
        assert image.mode == 'RGBA' and image.width == image.height >= 512
        alpha = image.getchannel('A')
        assert alpha.getextrema()[0] == 0 and alpha.getextrema()[1] >= 240
        assert all(alpha.getpixel(p) == 0 for p in ((0, 0), (image.width - 1, 0), (0, image.height - 1), (image.width - 1, image.height - 1)))
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
    report['assets'].append(item)
(ART / 'export-report.json').write_text(json.dumps(report, indent=2) + '\n')
BINARY.unlink()
print(f"PASS: {len(report['assets'])} masters and {sum(len(a['exports']) for a in report['assets'])} exports")
