#!/usr/bin/env python3
"""S3 before/after native-cell table (measurement only).

before = evidence/terrain-census-20260929/census.json (same census tool, HEAD bccc3e6)
after  = evidence/terrain-s3-20260929/raw.jsonl (this change, same tool)
Writes evidence/terrain-s3-20260929/census.json."""
import collections, json, statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BEFORE = ROOT / 'evidence/terrain-census-20260929/census.json'
OUT = ROOT / 'evidence/terrain-s3-20260929'


def layout(c):
    z = c['zone']
    if z == 'trollmire':
        return 'FLOODED' if c['is_flooded'] else 'DEFAULT'
    if z == 'old-forest':
        return 'CRYSTALINE' if c['is_crystaline'] else 'DEFAULT'
    if z == 'scintillating-caves':
        return 'TWISTED' if c['max_level'] == 5 else 'DEFAULT'
    return 'DEFAULT'


def main():
    before = {}
    for lv in json.loads(BEFORE.read_text())['levels']:
        before[(lv['zone'], lv['layout'], lv['level'])] = lv
    rows = collections.defaultdict(list)
    for line in (OUT / 'raw.jsonl').read_text().splitlines():
        r = json.loads(line)
        if 'census' not in r:
            continue
        c = r['census']
        rows[(c['zone'], layout(c), c['level'])].append(c)
    levels, zones = [], collections.defaultdict(lambda: {'before': [], 'after': [], 'cells': 0})
    for key in sorted(rows):
        cs = rows[key]
        groups = collections.Counter()
        layers = {}
        for c in cs:
            for k, g in (c['groups'] or {}).items():
                groups[k] += g['n']
                if g.get('layers'):
                    layers.setdefault(k, g['layers'])
        b = before.get(key)
        after = [c['native'] for c in cs]
        entry = {'zone': key[0], 'layout': key[1], 'level': key[2], 'seeds': len(cs), 'total_cells': cs[0]['total'],
                 'before_native_mean': b['native_mean'] if b else None,
                 'before_native': b['native'] if b else None,
                 'after_native': after, 'after_native_mean': round(statistics.mean(after), 1),
                 'after_converted_stone': [c['converted_stone'] for c in cs],
                 'after_remaining_groups_sum': dict(groups.most_common()),
                 'after_remaining_layers': layers}
        levels.append(entry)
        z = zones[key[:2]]
        if b:
            z['before'].append(b['native_mean'])
        z['after'].append(entry['after_native_mean'])
        z['cells'] = cs[0]['total']
    summary = []
    for (zone, lay), z in sorted(zones.items()):
        summary.append({'zone': zone, 'layout': lay,
                        'before_native_per_level': round(statistics.mean(z['before']), 1) if z['before'] else None,
                        'after_native_per_level': round(statistics.mean(z['after']), 1),
                        'cells_per_level': z['cells']})
    out = {'meta': {'date': '2026-09-29', 'mode': 'refined', 'tool': 'tools/run_terrain_census.py --item s3 --seeds 2',
                    'before_source': 'evidence/terrain-census-20260929/census.json (HEAD bccc3e6, same tool)',
                    'note': 'seeds are random regenerations; before/after are different maps, compare means'},
           'summary': summary, 'levels': levels}
    (OUT / 'census.json').write_text(json.dumps(out, ensure_ascii=False, indent=1) + '\n')
    for s in summary:
        print(s)


if __name__ == '__main__':
    main()
