#!/usr/bin/env python3
"""Aggregate evidence/terrain-census-20260929/raw.jsonl into census.json (measurement only)."""
import json, re, collections
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'evidence/terrain-census-20260929'
AURA = {'fell-aura','antimagic-bush','spellblaze-scar','bligthed-soil','protective-aura','font-life','necrotic-air','whistling-vortex','slimey-pool'}
EVENT_ITEM = {'glowing-chest':'E4','glimmerstone':'E5','weird-pedestals':'E6','tombstones':'E7','old-battle-field':'E7','icy-ground':'E9',
              'meteor':'E10','pyroclast':'E10','damp-cave':'E11','drake-cave':'E11','naga-portal':'E11','fearscape-portal':'E11','rat-lich':'E11','sub-vault':'E12'}
STONE_ZONES = {'ruins-kor-pul','rhaloren-camp','dreadfell','halfling-ruins','reknor','blighted-ruins'}

def norm(key):
    parts = key.split('|')
    if len(parts) >= 4 and 'events/' in parts[2] and parts[0] != 'nil' and parts[1].endswith(('aura)','soil)','air)','vortex)','scar)','life)','pool)','bush)')) or ' aura)' in parts[1]:
        parts[1] = '<aura-renamed floor>'
    elif len(parts) >= 4 and 'events/' in parts[2] and re.search(r'\(.*\)$', parts[1]):
        parts[1] = '<event-renamed>'
    if parts[0].startswith('Long tunnel'):
        parts[0] = 'REL_TUNNEL?'
    return '|'.join(parts)

def item_of(zone, key, g, is_crystaline):
    ev_roles = g.get('ev') if isinstance(g.get('ev'), dict) else {}
    id_, name, cbs, adds = (key.split('|') + ['', '', '', ''])[:4]
    ev = re.findall(r'events/([\w-]+)\.lua', cbs)
    for e in ev:
        if e in AURA:
            centre = sum(n for t, n in ev_roles.items() if t.endswith('/E3-centre'))
            if centre * 2 > g.get('n', 0): return 'E3'
            return 'E1' if g.get('type') == 'floor' and not g.get('block') else 'E2'
        if e in EVENT_ITEM:
            return EVENT_ITEM[e]
    if 'glowing chest' in name: return 'E4'
    if 'glimmerstone' in name: return 'E5'
    if 'hidden vault' in name: return 'E12'
    if re.match(r'CRYSTAL_(FLOOR|WALL)\d*$', id_) and zone == 'old-forest': return 'E8'
    if id_ == 'WORMHOLE': return 'T2'
    if id_.startswith('SUMMON_CIRCLE'): return 'T17'
    if re.match(r'(DOOR_VAULT|ROCK_VAULT|BONE_VAULT_DOOR)', id_): return 'T4'
    if 'LEVER' in id_: return 'T5'
    if id_.startswith('LOCK'): return 'T6'
    if id_.startswith('CAVE_DOOR'): return 'T7'
    if id_.startswith('FLAT_'): return 'T8'
    if id_ == 'LAKE_NUR': return 'T9'
    if id_ in ('IRON_COUNCIL','QUICK_EXIT','BEACH_UP','REL_TUNNEL') or name.startswith('Long tunnel'): return 'T10'
    if 'FAR_EAST_PORTAL' in id_: return 'T13'
    if id_ in ('LORE_NOTE','IRON_THRONE_EDICT') or id_.startswith('LORE'): return 'T14'
    if 'Recall Portal' in name or 'temporal portal' in name: return 'UNLISTED:escort-recall-portal'
    if id_ == 'DEEP_WATER' and zone in STONE_ZONES: return 'UNLISTED:stone-zone-DEEP_WATER'
    if id_.startswith('POISON_DEEP_WATER'): return 'UNLISTED:poison-deep-water'
    if id_.startswith('VAULT_TELEPORTER'): return 'UNLISTED:portal-vault-teleporter'
    if id_ == 'PORTAL' and zone == 'slazish-fen': return 'UNLISTED:slazish-coral-portal'
    if id_ == 'UP' and 'collapsed tower' in name: return 'UNLISTED:rhaloren-collapsed-tower-exit'
    if id_.startswith('SANDWALL_STABLE'): return 'UNLISTED:ritch-SANDWALL_STABLE'
    if id_ == 'ALTAR_CORRUPT': return 'T16'
    if id_ in ('ALTAR','PENTAGRAM'): return 'T15'
    if id_ == 'STEW': return 'T24'
    if id_ == 'FLOOR' and name == 'floor' and int(adds or 0) > 0 and not cbs and zone in STONE_ZONES: return 'T21(inferred)'
    if zone in ('old-forest','scintillating-caves') and re.match(r'(FLOOR|HARDWALL|WALL|DOOR)', id_) and not cbs: return 'T23'
    if zone == 'trollmire' and re.match(r'(FLOOR|HARDWALL|WALL|DOOR)', id_) and not cbs: return 'T23(zone not in doc)'
    return 'UNLISTED'

def main():
    rows = [json.loads(l) for l in (OUT / 'raw.jsonl').read_text().splitlines()]
    errors = [r for r in rows if r.get('error')]
    levels = collections.OrderedDict()
    runs = []
    for r in rows:
        c = r.get('census')
        if not c: continue
        g = c['groups'] if isinstance(c['groups'], dict) else {}
        aura = c['aura'] if isinstance(c['aura'], dict) else {}
        ev = c['events'] if isinstance(c['events'], dict) else {}
        layout = ('FLOODED' if c['is_flooded'] else 'DEFAULT') if r['zone'] == 'trollmire' else \
                 ('CRYSTALINE' if c['is_crystaline'] else 'DEFAULT') if r['zone'] == 'old-forest' else \
                 ('HIDEOUT' if c['is_hideout'] else 'DEFAULT') if r['zone'] == 'ruins-kor-pul' else \
                 ('OVERGROUND' if c['is_overground'] else 'DEFAULT') if r['zone'] == 'rhaloren-camp' else \
                 ('PURIFIED' if c['is_purified'] else 'DEFAULT') if r['zone'] == 'heart-gloom' else \
                 ('TWISTED' if r['opts'].get('twisted') else 'DEFAULT') if r['zone'] == 'scintillating-caves' else 'DEFAULT'
        run = {'seed': r['seed'], 'total': c['total'], 'converted': c['converted'], 'converted_stone': c['converted_stone'],
               'converted_forest': c['converted_forest'], 'native': c['native'], 'empty': c['empty'],
               'events_findEventGrid': ev, 'aura_cells': aura, 'centres': c['centres'] if isinstance(c['centres'], list) else [],
               'groups': {}}
        e_native = collections.Counter()
        for k, v in g.items():
            nk = norm(k)
            vv0 = dict(v); vv0['ev'] = v['ev'] if isinstance(v['ev'], dict) else {}
            it = item_of(r['zone'], k, vv0, c['is_crystaline'])
            vv = dict(v); vv['ev'] = v['ev'] if isinstance(v['ev'], dict) else {}
            d = run['groups'].setdefault(nk, {'n': 0, 'item': it, 'type': v.get('type'), 'exit': v.get('exit')})
            d['n'] += v['n']
            evd = v['ev'] if isinstance(v['ev'], dict) else {}
            for t, n in evd.items():
                evn, role = t.split('/')
                if evn in AURA: e_native[role] += n
        run['aura_native_by_role'] = dict(e_native)
        run['crystal_cells'] = sum(x['n'] for k, x in run['groups'].items() if k.startswith('CRYSTAL_') and r['zone'] == 'old-forest')
        run['crystal_cells_pure_E8'] = sum(x['n'] for k, x in run['groups'].items() if x['item'] == 'E8')
        key = (r['zone'], layout, c['level'])
        levels.setdefault(key, []).append(run)
    out_levels = []
    for (zone, layout, level), rs in levels.items():
        grp = collections.defaultdict(lambda: {'n': 0, 'seeds_present': 0, 'item': None})
        for run in rs:
            for k, x in run['groups'].items():
                d = grp[k]; d['n'] += x['n']; d['seeds_present'] += 1; d['item'] = x['item']; d['exit'] = x['exit']
        au = collections.Counter(); auc = collections.Counter()
        for run in rs:
            for t, a in run['aura_cells'].items():
                au[t] += a['native']; auc[t] += a['converted']
        nat = [x['native'] for x in rs]
        by_item = collections.Counter()
        for k, d in grp.items(): by_item[d['item']] += d['n']
        out_levels.append({'zone': zone, 'layout': layout, 'level': level, 'seeds': len(rs),
            'total_cells': [x['total'] for x in rs], 'converted': [x['converted'] for x in rs], 'native': nat,
            'native_mean': round(sum(nat) / len(nat), 1), 'native_by_item_sum': dict(by_item),
            'aura_native_by_event_role_sum': dict(au), 'aura_converted_by_event_role_sum': dict(auc),
            'aura_native_by_role_sum': dict(sum((collections.Counter(x['aura_native_by_role']) for x in rs), collections.Counter())),
            'events_seen': sorted({e for x in rs for e in x['events_findEventGrid']}),
            'crystal_cells_per_seed': [x['crystal_cells'] for x in rs], 'crystal_pure_E8_per_seed': [x['crystal_cells_pure_E8'] for x in rs],
            'groups': dict(sorted(grp.items(), key=lambda kv: -kv[1]['n']))})
    meta = {'date': '2026-09-29', 'mode': 'refined', 'runs': len(rows), 'errors_in_final_data': len(errors),
            'method': 'tests/live_terrain_census.lua via tools/run_terrain_census.py; seeds = repeated ms.enter in one fixture process',
            'group_key': 'id|name|callbacks|#add_displays; aura-renamed floor names are normalised to <aura-renamed floor>',
            'converted': 'forest adapter owns replace_display, or stone adapter record.painted after forced-visible observe/render'}
    (OUT / 'census.json').write_text(json.dumps({'meta': meta, 'levels': out_levels}, ensure_ascii=False, indent=1) + '\n')
    print(len(out_levels), 'levels', len(rows), 'runs')

main()
