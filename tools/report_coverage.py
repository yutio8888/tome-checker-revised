"""Turn a native detached-actor audit into a bounded, reason-coded coverage table."""
from pathlib import Path
import argparse
import collections
import csv

parser=argparse.ArgumentParser()
parser.add_argument('input',type=Path)
parser.add_argument('output',type=Path)
args=parser.parse_args()
rows=list(csv.DictReader(args.input.open(),delimiter='\t'))
assert rows and len({r['name'] for r in rows})==len(rows)
counts=collections.Counter(r['status'] for r in rows)
reasons=collections.Counter(r['reason'] for r in rows if r['status']!='covered')
lines=['# 原生身份覆盖审计','',
       '这张表在离线 fixture 中通过原生 finishEntity 解析未入场的怪物，再调用生产映射器 explain。覆盖范围为九个森林／水域直接家族定义及 Trollmire 固定独特怪。**不是全游戏覆盖率，也不是自然刷怪概率**；通用 all.lua 候选、随机稀有变体和第三方插件另行验证。',
       '',f"本次 {len(rows)} 项："+'；'.join(f'{k}={v}' for k,v in sorted(counts.items()))+'。','',
       '回退原因：'+('；'.join(f'{k}={v}' for k,v in sorted(reasons.items())) or '无')+'。','',
       '| 原生身份 | 等级范围 | 棋子 | 状态／原因 | 来源 |',
       '| --- | --- | --- | --- | --- |']
for r in rows:
    def clean(v): return v.replace('|','\\|').replace('\n',' ')
    values=[r['name'],r['min_level']+'–'+(r['max_level'] or '不限'),r['token'] or '—',
            r['status']+' / '+r['reason'],r['source']]
    lines.append('| '+' | '.join(clean(v) for v in values)+' |')
args.output.parent.mkdir(parents=True,exist_ok=True)
args.output.write_text('\n'.join(lines)+'\n')
print(dict(total=len(rows),status=dict(counts),reasons=dict(reasons)))
