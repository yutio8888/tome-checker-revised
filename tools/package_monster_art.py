"""Bundle selected AI art candidates, sizes and provenance; this is not a teaa."""
from pathlib import Path
import hashlib
import json
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]
version='.'.join(re.search(r'addon_version\s*=\s*\{([^}]+)\}',(ROOT/'init.lua').read_text())[1].replace(' ','').split(','))
manifest = {'kind': 'source-art-not-an-installer', 'version':version, 'generator': 'built-in image_gen', 'assets': []}
files = {}
selected = {}
for batch in ('monsters-v1', 'monsters-v2', 'monsters-v3', 'monsters-v4'):
    art = ROOT / 'art' / batch
    if batch == 'monsters-v4' and not (art/'export-report.json').exists():
        continue
    report = json.loads((art / 'export-report.json').read_text())
    choices = json.loads((art / 'selected-masters.json').read_text())
    for required in ('BRIEF.md', 'REVIEW.md', 'selected-masters.json', 'export-report.json'):
        assert (art / required).is_file(), f'Missing review or provenance: {art / required}'
    assert len(report['assets']) == len(choices)
    for item in report['assets']:
        assert choices[item['id']] == item['master'], item['id']
        p = art / item['master']
        assert hashlib.sha256(p.read_bytes()).hexdigest() == item['sha256'], p
        selected[item['id']]={'batch':batch, **item}
    for pattern in ('prompts/*.json', 'BRIEF.md', 'REVIEW.md', 'selected-masters.json', 'catalog.json', 'export-report.json'):
        for p in art.glob(pattern):
            files[f'{batch}/{p.relative_to(art).as_posix()}'] = p
manifest['assets']=list(selected.values())
for item in manifest['assets']:
    batch=item['batch'];art=ROOT/'art'/batch
    files[f'{batch}/{item["master"]}']=art/item['master']
    for export in item['exports']:
        p=art/export['path']
        assert hashlib.sha256(p.read_bytes()).hexdigest()==export['sha256'],p
        files[f'{batch}/{export["path"]}']=p
runtime=json.loads((ROOT/'data/token-manifest.json').read_text())
assert {x['id'] for x in manifest['assets']} == {x['id'] for x in runtime['assets']}, 'Only package integrated identities'
count=len(manifest['assets'])
output = ROOT / ('dist/monster-tokens-'+str(count)+'-v'+version+'.zip')
output.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as z:
    for name, p in sorted(files.items()):
        z.write(p, name)
    z.writestr('manifest.json', json.dumps(manifest, ensure_ascii=False, indent=2)+'\n')
    z.writestr('README.txt', f'{count} 个怪物棋子素材候选。不是可安装的 ToME addon。\n'
        'manifest.json 是当前选择；各批次的selected-masters只记录该批当时的选择。\n'
        'masters/ 仅含当前选定 ImageGen 原图，sprites/ 为 48/64/96/128/256px 工程导出。\n'
        '图中无阵营色圈，动态阵营/rank/状态须由游戏显示层提供。\n'
        '完整提示词记录在 prompts/，编辑来源中未选中的中间版仍保留在开发仓库。\n'
        '原游戏参考图不包含于此包；其路径与来源保留在记录中。\n')
with zipfile.ZipFile(output) as z:
    assert z.testzip() is None
    assert len([n for n in z.namelist() if '/masters/' in n]) == count
    assert len([n for n in z.namelist() if '/sprites/' in n]) == count*5
sha = hashlib.sha256(output.read_bytes()).hexdigest()
(output.parent / 'monster-art-SHA256SUMS').write_text(sha+'  '+output.name+'\n')
print(f'{output}\n{sha}\n{count} selected masters + {count*5} size exports + prompts and review documents')
