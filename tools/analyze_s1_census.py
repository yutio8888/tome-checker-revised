#!/usr/bin/env python3
"""S1 before/after native-cell table (measurement only).

before = the latest same-tool census of each layout:
  evidence/terrain-s3-20260929/raw.jsonl for the layouts S3 re-measured
  (Trollmire FLOODED, Old Forest CRYSTALINE, Scintillating TWISTED), else
  evidence/terrain-census-20260929/raw.jsonl (HEAD bccc3e6).
after  = evidence/terrain-s1-20260929/raw.jsonl (this change, same tool).
Also sums the census's own aura attribution (cells an aura event wrote,
by event/role) as native vs converted. Writes evidence/terrain-s1-20260929/census.json."""
import collections, json, statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CENSUS = ROOT / 'evidence/terrain-census-20260929/raw.jsonl'
S3 = ROOT / 'evidence/terrain-s3-20260929/raw.jsonl'
OUT = ROOT / 'evidence/terrain-s1-20260929'
S3_LAYOUTS = {('trollmire', 'FLOODED'), ('old-forest', 'CRYSTALINE'), ('scintillating-caves', 'TWISTED')}


def layout(c):
    z = c['zone']
    if z == 'trollmire':
        return 'FLOODED' if c['is_flooded'] else 'DEFAULT'
    if z == 'old-forest':
        return 'CRYSTALINE' if c['is_crystaline'] else 'DEFAULT'
    if z == 'heart-gloom':
        return 'PURIFIED' if c['is_purified'] else 'DEFAULT'
    if z == 'ruins-kor-pul':
        return 'HIDEOUT' if c['is_hideout'] else 'DEFAULT'
    if z == 'rhaloren-camp':
        return 'OVERGROUND' if c['is_overground'] else 'DEFAULT'
    return 'DEFAULT'


def load(path):
    rows = collections.defaultdict(list)
    for line in path.read_text().splitlines():
        r = json.loads(line)
        c = r.get('census')
        if not c:
            continue
        lay = layout(c)
        # Scintillating layout is known from the job options.
        if c['zone'] == 'scintillating-caves':
            lay = 'TWISTED' if r['opts'].get('twisted') else 'DEFAULT'
        rows[(c['zone'], lay, c['level'])].append(c)
    return rows


RING = {'fell-aura', 'antimagic-bush', 'spellblaze-scar', 'bligthed-soil', 'protective-aura', 'font-life',
        'necrotic-air', 'whistling-vortex', 'slimey-pool'}


def aura(cs):
    # Only the ring events (other events such as sub-vault or glimmerstone
    # also write terrain and are attributed by the census, but are not S1).
    native, converted = collections.Counter(), collections.Counter()
    for c in cs:
        for k, v in (c.get('aura') or {}).items():
            if k.split('/')[0] not in RING:
                continue
            native[k] += v['native']
            converted[k] += v['converted']
    return native, converted


def main():
    census, s3, after = load(CENSUS), load(S3), load(OUT / 'raw.jsonl')
    levels = []
    zones = collections.defaultdict(lambda: {'before': [], 'after': [], 'aura_before': 0, 'aura_after': 0,
                                             'aura_total_before': 0, 'aura_total_after': 0, 'seeds_b': 0, 'seeds_a': 0})
    for key in sorted(after):
        src = s3 if key[:2] in S3_LAYOUTS else census
        b, a = src.get(key, []), after[key]
        bn, bc = aura(b)
        an, ac = aura(a)
        groups = collections.Counter()
        layers = {}
        for c in a:
            for k, g in (c['groups'] or {}).items():
                groups[k] += g['n']
                if g.get('layers'):
                    layers.setdefault(k, g['layers'])
        entry = {'zone': key[0], 'layout': key[1], 'level': key[2], 'total_cells': a[0]['total'],
                 'before_source': 'terrain-s3-20260929' if src is s3 else 'terrain-census-20260929',
                 'before_seeds': len(b), 'after_seeds': len(a),
                 'before_native': [c['native'] for c in b], 'after_native': [c['native'] for c in a],
                 'before_native_mean': round(statistics.mean(c['native'] for c in b), 1) if b else None,
                 'after_native_mean': round(statistics.mean(c['native'] for c in a), 1),
                 'before_aura_native_per_seed': round(sum(bn.values()) / len(b), 1) if b else None,
                 'after_aura_native_per_seed': round(sum(an.values()) / len(a), 1),
                 'after_aura_converted_per_seed': round(sum(ac.values()) / len(a), 1),
                 'after_aura_native_by_event_role': dict(an), 'after_aura_converted_by_event_role': dict(ac),
                 'events_after': dict(sum((collections.Counter(c.get('events') or {}) for c in a), collections.Counter())),
                 'after_remaining_groups_sum': dict(groups.most_common()), 'after_remaining_layers': layers}
        levels.append(entry)
        z = zones[key[:2]]
        if b:
            z['before'].append(entry['before_native_mean'])
        z['after'].append(entry['after_native_mean'])
        z['aura_before'] += sum(bn.values()); z['aura_total_before'] += sum(bn.values()) + sum(bc.values())
        z['aura_after'] += sum(an.values()); z['aura_total_after'] += sum(an.values()) + sum(ac.values())
        z['seeds_b'] += len(b); z['seeds_a'] += len(a)
        z['cells'] = a[0]['total']
    summary = []
    for (zone, lay), z in sorted(zones.items()):
        summary.append({'zone': zone, 'layout': lay,
                        'before_native_per_level': round(statistics.mean(z['before']), 1) if z['before'] else None,
                        'after_native_per_level': round(statistics.mean(z['after']), 1),
                        'aura_cells_native_before': f"{z['aura_before']}/{z['aura_total_before']} ({z['seeds_b']} level-seeds)",
                        'aura_cells_native_after': f"{z['aura_after']}/{z['aura_total_after']} ({z['seeds_a']} level-seeds)"})
    out = {'meta': {'date': '2026-09-29', 'mode': 'refined', 'tool': 'tools/run_terrain_census.py --item s1 --seeds 2 --out evidence/terrain-s1-20260929',
                    'before_source': 'terrain-s3-20260929 raw for Trollmire FLOODED / Old Forest CRYSTALINE / Scintillating TWISTED; '
                                     'terrain-census-20260929 raw otherwise (same tool)',
                    'note': 'seeds are random regenerations; before/after are different maps, compare means. '
                            'aura_* counts use the census attribution of cells an aura event wrote (E1/E2/E3 roles).'},
           'summary': summary, 'levels': levels}
    (OUT / 'census.json').write_text(json.dumps(out, ensure_ascii=False, indent=1) + '\n')
    for s in summary:
        print(s)


if __name__ == '__main__':
    main()
