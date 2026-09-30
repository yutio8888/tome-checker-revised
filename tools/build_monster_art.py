"""Compile the mechanical exporter and validate selected ImageGen PNG assets.

Python reads image metadata only; all painted pixels originate in ImageGen.
The C export step performs a documented placement/size conversion, not repainting.
"""
from pathlib import Path
from PIL import Image
import argparse
import hashlib
import json
import subprocess

import check_token_style

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--batch', choices=tuple(f'monsters-v{i}' for i in range(1, 7)) + ('monster-batch-b', 'monster-batch-c', 'monster-batch-d', 'monster-batch-e', 'monster-batch-f', 'monster-batch-g', 'monster-batch-h', 'monster-batch-i', 'monster-batch-j', 'monster-batch-k', 'monster-batch-l', 'monster-batch-m', 'monster-batch-n', 'monster-batch-o', 'monster-batch-p', 'monster-batch-q', 'monster-batch-r', 'monster-batch-s', 'monster-batch-t', 'monster-batch-u', 'monster-batch-v', 'monster-batch-w', 'monster-batch-x', 'monster-batch-y', 'monster-batch-z', 'monster-batch-aa', 'monster-batch-ab', 'monster-batch-ac'), default='monsters-v1')
# 风格判据始终测量，无法跳过。--style-gate-advisory 只把"阻断"降级为
# 大声警告，用于诊断尚未定稿的草图；降级事实会写进 export-report.json，
# 无法静默绕过，也不代表该批可以进 data/gfx/tokens。
parser.add_argument('--style-gate-advisory', action='store_true',
                    help='diagnostic only: downgrade the blocking style gate to a recorded warning')
parser.add_argument('--strict-style', action='store_true',
                    help='ignore the grandfather waiver list; report legacy assets as failures')
args = parser.parse_args()
ART = ROOT / 'art' / args.batch
catalog_path = ART / 'catalog.json'
catalog = json.loads(catalog_path.read_text()) if catalog_path.exists() else None
IDS = tuple(a['id'] for a in catalog) if catalog else ('forest-troll', 'wolf', 'brown-bear', 'brown-snake', 'venus-flytrap')
assert len(set(IDS)) == len(IDS), 'Duplicate catalog identity'
choices_path = ART / 'selected-masters.json'
choices = json.loads(choices_path.read_text()) if choices_path.exists() else {i: f'masters/{i}-v1.png' for i in IDS}
assert set(choices) == set(IDS), 'Explicitly select every catalog master'
binary = ROOT / 'tools/bin/export_token'
binary.parent.mkdir(exist_ok=True)
subprocess.run(['cc', '-O2', '-Wall', '-Wextra', str(ROOT / 'tools/export_token.c'), '-o', str(binary), '-lpng', '-lm'], check=True)
report = {'method': 'ImageGen masters; native alpha; mechanical bbox placement and alpha-weighted area downsampling', 'assets': []}
for asset_id in IDS:
    source = ART / choices[asset_id]
    with Image.open(source) as im:
        assert im.mode == 'RGBA', (source, im.mode)
        amin, amax = im.getchannel('A').getextrema()
        assert amin == 0 and amax >= 240, (source, 'native alpha required')
    result = {'id': asset_id, 'master': choices[asset_id], 'sha256': hashlib.sha256(source.read_bytes()).hexdigest(), 'exports': []}
    for size in (48, 64, 96, 128, 256):
        target = ART / 'sprites' / str(size) / f'{asset_id}.png'
        target.parent.mkdir(parents=True, exist_ok=True)
        stats = json.loads(subprocess.check_output([str(binary), str(source), str(target), str(size)], text=True))
        with Image.open(target) as im:
            assert im.size == (size, size) and im.mode == 'RGBA'
            assert all(im.getpixel(p)[3] == 0 for p in ((0,0),(size-1,0),(0,size-1),(size-1,size-1))), (target, 'corner alpha')
            bounds = im.getchannel('A').point(lambda a: 255 if a > 8 else 0).getbbox()
            occupancy = max(bounds[2]-bounds[0], bounds[3]-bounds[1])/size
            assert .83 <= occupancy <= .91, (target, occupancy)
        result['exports'].append({'path': target.relative_to(ART).as_posix(), **stats, 'sha256': hashlib.sha256(target.read_bytes()).hexdigest()})
        if size == 128:
            # 阻断门控接在这里：128px 导出件就是将来被逐字节拷进
            # data/gfx/tokens 的运行贴图，这里是"最终像素第一次存在"的时刻，
            # 且已有四角 alpha 与 occupancy 断言，风格判据与它们同层。
            # 既有 37 款在 check_token_style.GRANDFATHERED 名单内，按 id 放行。
            gated = check_token_style.check_asset(
                target, source, asset_id, allow_grandfather=not args.strict_style)
            result['style_gate'] = {
                'baseline': list(check_token_style.BASELINE_SECTOR_MEDIANS),
                'base_drift': gated['token']['base_drift'],
                'max_sector_intrusion': gated['token']['max_sector_intrusion'],
                'max_opaque_radius': gated['token']['max_opaque_radius'],
                'blocking': gated['blocking'],
                'warnings': gated['warnings'],
                'grandfathered': gated['grandfathered'],
                'waived': gated['waived'],
                'passed': gated['passed'],
                'advisory_downgrade': bool(args.style_gate_advisory) and not gated['passed'],
            }
            for warning in gated['warnings']:
                print(f'WARN {asset_id}: {warning}')
            if gated['waived']:
                print(f'WAIVED {asset_id}: {"; ".join(gated["notes"])}')
            if not gated['passed']:
                detail = '；'.join(f['detail'] for f in gated['findings']
                                   if f['level'] == 'blocking' and not f['ok'])
                message = f'{asset_id} 未通过棋子风格门控：{detail}'
                if not args.style_gate_advisory:
                    raise SystemExit(f'FAIL: {message}\n'
                                     '这是阻断项；按 art/production/README.md 的验收表返修或重新生成。')
                print(f'ADVISORY-FAIL {asset_id}: {message}（已记入 export-report.json，'
                      '这批不得进入 data/gfx/tokens）')
    report['assets'].append(result)
(ART / 'export-report.json').write_text(json.dumps(report, indent=2)+'\n')
(ART / 'selection.js').write_text('// Derived sprites preserve selected ImageGen artwork; see export-report.json.\nwindow.monsterSelection = '+json.dumps({i:f'sprites/256/{i}.png' for i in IDS}, indent=2)+';\n')
if catalog:
    (ART / 'catalog.js').write_text('window.monsterCatalog = '+json.dumps(catalog, ensure_ascii=False, indent=2)+';\n')
gate_state = 'advisory' if args.style_gate_advisory else ('strict' if args.strict_style else 'on')
print(f'PASS: {len(IDS)} native-alpha masters; {len(IDS)*5} size exports, alpha corners, visible size and SHA-256 recorded; style gate {gate_state}')
