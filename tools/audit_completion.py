#!/usr/bin/env python3
"""Reconcile reviewed candidate lists against current tokens; no Lua execution.

Names are planning keys only, never runtime selectors. Static declarations do not
resolve inheritance, callbacks, room eligibility, translations or encounter rates.
Historical plans remain immutable. Output includes source hashes for invalidation.
"""
import argparse
import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from audit_repaint_variants import declarations
from audit_repaint_sources import visible_lines, LOAD

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parents[2]
OLD = ROOT / 'docs/repaint-plan-20260927'
OUT = ROOT / 'docs/completion-plan-20260927'
ROOM_EXTRAS = {
    'skeleton archer': 'amon-sul-crypt;skeleton-mage-cabal',
    'armoured skeleton warrior': 'amon-sul-crypt',
    'skeleton magus': 'amon-sul-crypt', 'skeleton master archer': 'amon-sul-crypt',
    'ghoul': 'amon-sul-crypt;forest-ruined-building1', 'ghast': 'amon-sul-crypt',
    'bloated horror': 'skeleton-mage-cabal', 'snow cat': 'snake-pit',
    'giant spider': 'snake-pit', 'broken golem': 'collapsed-tower',
    'honey tree': 'honey_glade;forest-ruined-building2', 'grizzly bear': 'honey_glade',
    'water imp': 'forest-ruined-building2', 'treant': 'plantlife',
    'forest wight': 'loot-vault', 'carrion worm mass': 'worms',
    'worm that walks': 'worms', 'snow giant chieftain': 'snow-giant-camp',
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path):
    with path.open(encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))


def current_catalog():
    path = ROOT / 'overload/mod/class/CheckerTokens.lua'
    rows = re.findall(r'\{id="([^"]+)", name="([^"]+)"([^\n]*)', path.read_text())
    manifest = json.loads((ROOT / 'data/token-manifest.json').read_text())
    names, definitions, shared = {}, {}, {}
    for asset_id, name, fields in rows:
        composite = 'shared_name=true' in fields
        definition = re.search(r'define_as="([^"]+)"', fields)
        definition = definition[1] if definition else None
        if composite and not definition:
            raise ValueError('shared planning name requires define_as')
        if name in names and (not composite or not shared[name] or definition in definitions[name]):
            raise ValueError('duplicate planning name; identity key must be reviewed')
        names.setdefault(name, []).append(asset_id)
        definitions.setdefault(name, set()).add(definition)
        shared[name] = composite
    if len(rows) != len({r[0] for r in rows}):
        raise ValueError('duplicate planning id')
    if {r[0] for r in rows} != {a['id'] for a in manifest['assets']}:
        raise ValueError('catalog parser / runtime manifest mismatch')
    # Planning names remain names; enumerate every explicit composite id in
    # the CSV cell without treating the name as a runtime selector.
    return {name: ';'.join(ids) for name, ids in names.items()}


def global_indexes(native_root, matrix):
    """Navigation for all base zones/grids, deliberately not an encounter census."""
    tracked, zones, grids = set(), [], []
    paired = {r['zone'] for r in matrix}
    for path in sorted((native_root/'zones').glob('*/zone.lua')):
        tracked.add(path)
        imports, local_names = {}, []
        for kind in ('npcs', 'grids'):
            source = path.parent/(kind+'.lua')
            imports[kind] = []
            if source.exists():
                tracked.add(source)
                imports[kind] = [m[2] for line in visible_lines(source) if (m := LOAD.match(line))]
                if kind == 'npcs':
                    local_names = [a['native_name'] for a in declarations(source)]
        zones.append(dict(zone=path.parent.name, source=str(path.relative_to(WORKSPACE)),
            phase='paired-early-plan' if path.parent.name in paired else 'later-base-audit',
            direct_npc_imports=';'.join(imports['npcs']), direct_grid_imports=';'.join(imports['grids']),
            literal_local_actor_names=';'.join(local_names),
            status='static-navigation-only; branches/inheritance/runtime-unresolved'))
    groups = {
        'G0-review-material-variants': ['forest', 'autumn_forest', 'elven_forest'],
        'G1-review-cross-zone-contracts': ['basic', 'underground'],
        'G2-planned': ['cave', 'crystal', 'underground_gloomy', 'underground_dreamy'],
        'G3-planned': ['snowy_forest', 'mountain', 'ice', 'icecave'],
        'G3-volcanic-review-hazards': ['lava', 'burntland'],
        'G4-planned': ['sand', 'sanddunes'],
    }
    lookup = {family:group for group,families in groups.items() for family in families}
    for path in sorted((native_root/'general/grids').glob('*.lua')):
        tracked.add(path)
        grids.append(dict(family=path.stem, source=str(path.relative_to(WORKSPACE)),
            proposed_reuse_group=lookup.get(path.stem, 'later-base-new-material-audit'),
            status='not-a-runtime-whitelist; audit each Grid and zone callback'))
    return zones, grids, tracked


def build():
    tracked = {Path(__file__).resolve(), ROOT/'tools/audit_repaint_variants.py', ROOT/'tools/audit_repaint_sources.py'}
    def rows(name):
        path = OLD / name
        tracked.add(path)
        return read_csv(path)
    base, variants = rows('monster-backlog.csv'), rows('variant-monster-backlog.csv')
    rooms = {r['room']: r for r in rows('variant-room-backlog.csv')}
    matrix = rows('zone-variants.csv')
    tracked.add(OLD / 'terrain-backlog.csv')
    catalog = current_catalog()
    tracked.update([ROOT/'overload/mod/class/CheckerTokens.lua', ROOT/'data/token-manifest.json'])
    native_root = WORKSPACE / 'game/modules/tome/data'
    index = {}
    family_report = []
    for path in sorted((native_root / 'general/npcs').glob('*.lua')):
        tracked.add(path)
        actors = declarations(path)
        for actor in actors:
            index.setdefault(actor['native_name'], []).append(actor)
        covered = [a['native_name'] for a in actors if a['native_name'] in catalog]
        family_report.append(dict(source=str(path.relative_to(WORKSPACE)),
            literal_declarations=len(actors), catalog_names=len(covered),
            missing_literal_names=';'.join(a['native_name'] for a in actors if a['native_name'] not in catalog),
            status='static-navigation-only-not-encounter-coverage'))
    candidates = {}
    for origin, items in [('baseline', base), ('variant', variants)]:
        for item in items:
            name = item['native_name']
            previous = candidates.get(name, {})
            # Variant list supplies generation/renderer warnings missing in baseline.
            row = {**previous, **item}
            row['origin'] = previous.get('origin', '') + (';' if previous else '') + origin
            row.setdefault('priority', 'baseline-plan')
            candidates[name] = row
    historical = set(candidates)
    for actor in declarations(native_root / 'general/npcs/rodent.lua'):
        if actor['native_name'] not in candidates:
            candidates[actor['native_name']] = dict(**actor, origin='rodent-family-completion',
                priority='shared-family-gap', paired_phase='P1/P2/P4/P7', zone_layouts='',
                design='鼠/大鼠/兔至少两项剪影、明度或色相区别；不得仅换色')
    for name, room_names in ROOM_EXTRAS.items():
        hits = index.get(name, [])
        if len(hits) != 1:
            raise ValueError(f'curated room identity is ambiguous or missing: {name}')
        layouts = sorted({z for room in room_names.split(';') for z in rooms[room]['zone_layouts'].split(';')})
        candidates.setdefault(name, dict(**hits[0], origin='room-gap', priority='conditional-room',
            zone_layouts=';'.join(layouts), paired_phase='room-owner-phase', rooms=room_names,
            design='先解析房间条件和最终显示；不是仅按声明最低等级决定出图'))
    for name, asset_id in catalog.items():
        if name not in candidates:
            candidates[name] = dict(native_name=name, origin='existing-outside-old-plan',
                priority='already-covered', source='', source_line='', design='reuse existing token')
    # Pin zone, room and grid contracts too, not only creature definitions.
    for row in matrix:
        folder = native_root / 'zones' / row['zone']
        tracked.update(p for p in folder.glob('*.lua') if p.name in ('zone.lua', 'npcs.lua', 'grids.lua'))
    for row in rooms.values():
        tracked.add(WORKSPACE / row['source'])
    grid_paths = sorted((native_root / 'general/grids').glob('*.lua'))
    zone_index, grid_index, global_sources = global_indexes(native_root, matrix)
    tracked.update(global_sources)
    result = []
    for name, row in sorted(candidates.items()):
        src = row.get('source', '')
        if src:
            path = WORKSPACE / src
            tracked.add(path)
            # Verify historical source references still contain this exact declaration.
            hits = [a for a in declarations(path) if a['native_name'] == name]
            if name == 'shadow' and row['priority'] == 'summoned-actor':
                matches = list(re.finditer(r'(?m)^\s*name\s*=\s*"shadow"', path.read_text()))
                if len(matches) != 1:
                    raise ValueError('dynamic shadow source changed; re-audit required')
                row['source_line'] = path.read_text()[:matches[0].start()].count('\n') + 1
            elif len(hits) == 1:
                row.update(hits[0])
            else:
                raise ValueError(f'needs source re-audit: {name} in {src}')
        gate = 'native-resolve-before-generation'
        if row.get('native_tall') == 'yes' or row.get('shader'):
            gate = 'render-contract-first'
        if row['priority'] in ('excluded-local-import', 'conditional-event', 'conditional-generation', 'conditional-room', 'summoned-actor'):
            gate = 'generation-or-behavior-contract-first'
        if name in catalog:
            gate = 'reuse-current-art-check-each-context'
        result.append(dict(native_name=name, token_id=catalog.get(name, ''),
            art_status='mapped' if name in catalog else 'missing-candidate', origin=row['origin'],
            priority=row['priority'], gate=gate, source=src, source_line=row.get('source_line', ''),
            source_sha256=digest(WORKSPACE/src) if src else '', define_as=row.get('define_as', ''),
            declared_min_level=row.get('declared_min_level', ''), native_tall=row.get('native_tall', ''),
            shader=row.get('shader', ''), zone_layouts=row.get('zone_layouts', ''),
            paired_phase=row.get('paired_phase', ''), rooms=row.get('rooms', ''),
            design=row.get('design', ''), generation_note=row.get('generation_note', '')))
    missing = [r for r in result if r['art_status'] == 'missing-candidate']
    summary = dict(schema=1, scope='curated early-zone candidates + room gaps + existing tokens; NOT exhaustive',
        installed_token_count=sum(len(ids.split(';')) for ids in catalog.values()),
        mapped_planning_name_count=len(catalog), historical_union=len(historical),
        historical_mapped=len(historical & catalog.keys()),
        historical_missing=len(historical - catalog.keys()), registry_rows=len(result),
        missing_candidates=len(missing), missing_by_priority=dict(sorted(Counter(r['priority'] for r in missing).items())),
        paired_layouts=len(matrix), explicit_room_templates=len(rooms),
        base_npc_family_files=len(family_report), base_grid_family_files=len(grid_paths), base_zones=len(zone_index),
        unresolved_not_counted=[
            'snake-pit references ritch flamespitter; zone and summon definitions exist but room resolution is unverified',
            'collapsed-tower creates elemental crystal dynamically; needs source identity/display contract',
            'all.lua, escorts, nested areas, random unique actors, inherited/translated/dynamic names need runtime expansion'],
        limitations='Literal name matches are planning evidence, not safe runtime identity or encounter probability.',
        inputs={str(p.relative_to(WORKSPACE)): digest(p) for p in sorted(tracked)})
    return result, family_report, summary, zone_index, grid_index


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=OUT)
    args = parser.parse_args()
    result, families, summary, zones, grids = build()
    args.output.mkdir(parents=True, exist_ok=True)
    for name, records in [('creatures.csv', result), ('base-family-index.csv', families), ('base-zone-index.csv', zones), ('base-grid-index.csv', grids)]:
        with (args.output/name).open('w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=list(records[0]), lineterminator='\n')
            writer.writeheader()
            writer.writerows(records)
    (args.output/'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k != 'inputs'}, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
