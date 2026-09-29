#!/usr/bin/env python3
"""Summarise evidence/terrain-s2-20260929/scenes.json into census.json.

Per level: the forced census (every stone cell observed as if seen) native
count and native groups, before (HEAD TEAA) and after (working tree); the S2
identities found with how many cells are board; water-edged floors (T21);
exit targets seen after (change_level / change_zone of every S2 exit cell, the
same in the natural, posed and forced passes); toggles; regression probes.
Before and after are separate generations of the same level.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'evidence/terrain-s2-20260929'


def groups(census):
    g = census.get('groups') or {}
    return {k: v['n'] for k, v in sorted(g.items(), key=lambda kv: -kv[1]['n'])} if isinstance(g, dict) else {}


def level(row):
    c = row['census_forced']
    s = row['s2_forced']
    exits = {}
    for key in ('s2_natural', 's2_posed', 's2_forced'):
        for cell in row[key]['cells']:
            if cell['change_level'] or cell['change_zone']:
                exits.setdefault(f"{cell['id']}@{cell['x']},{cell['y']}", set()).add((cell['change_level'], cell['change_zone'], cell['auto'], cell['check']))
    return {'native': c.get('native'), 'converted': c.get('converted'), 'total': c.get('total'),
            'native_groups': groups(c), 's2_by_id': s['by_id'] or {}, 'edged_floor': s['edged'],
            'hunt': {'tries': row['enter'].get('tries'), 'found': row['enter'].get('found')},
            'exit_targets': {k: [list(v) for v in sorted(vals, key=str)] for k, vals in exits.items()},
            'exit_targets_stable': all(len(v) == 1 for v in exits.values()),
            'rules_equal': row['rules_before'] == row['rules_after']}


def main():
    data = json.loads((OUT / 'scenes.json').read_text())
    after, before = data.get('after', {}), data.get('before', {})
    # Targeted re-runs (after a contract fix, or extra hunts) replace the
    # full run's row for their levels.
    for key, run in data.items():
        for phase, base in (('after-', after), ('before-', before)):
            if key.startswith(phase):
                base.setdefault('levels', {}).update(run['levels'])
                base.setdefault('reruns', []).append(key)
    out = {'meta': {'date': '2026-09-29', 'mode': 'refined', 'method': __doc__.strip().splitlines()[0],
                    'before': 'HEAD 2f79a4d9 TEAA', 'after': 'working tree',
                    'reruns': after.get('reruns', []) + before.get('reruns', [])}, 'levels': {}, 'toggles': {}, 'regression': {}}
    for label, row in after.get('levels', {}).items():
        entry = {'zone': row['zone'], 'level': row['level'], 'opts': row['opts'], 'after': level(row)}
        if label in before.get('levels', {}):
            entry['before'] = level(before['levels'][label])
        out['levels'][label] = entry
        t = row.get('toggle')
        if t:
            out['toggles'][label] = {'target': t['target'], 'restored_vs_refined': t['restored_vs_refined'],
                                     'native_vs_refined': t['native_vs_refined'], 'rules_equal': t['rules_equal'],
                                     'rule_digests': t['rules']}
    for phase, d in (('after', after), ('before', before)):
        for label, r in d.get('regression', {}).items():
            c = r['census_forced']
            out['regression'].setdefault(label, {})[phase] = {'natural': r['probe_natural'], 'forced_native': c.get('native'),
                                                             'forced_total': c.get('total'), 'groups': groups(c)}
    (OUT / 'census.json').write_text(json.dumps(out, ensure_ascii=False, indent=1) + '\n')
    for label, e in out['levels'].items():
        b = e.get('before', {})
        print(f"{label:12} native {b.get('native')}->{e['after']['native']}  s2 {e['after']['s2_by_id']}  edged {e['after']['edged_floor']['n']}/{e['after']['edged_floor']['board']}")


if __name__ == '__main__':
    main()
