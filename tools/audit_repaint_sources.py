"""Read-only source audit for the next creature/terrain art plan.

Direct Lua load statements are reuse evidence, not encounter probabilities.
Conditional branches are retained; all.lua is reported but never expanded.
The terrain set below is the finite output of the current refined selector,
not a claim that every other image is globally unused.
"""
from collections import defaultdict
from pathlib import Path
import csv
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parents[2]
OUT = ROOT / 'docs/repaint-plan-20260927'
EARLY = ('trollmire', 'ruins-kor-pul', 'norgos-lair', 'heart-gloom',
         'scintillating-caves', 'rhaloren-camp', 'old-forest', 'maze',
         'sandworm-lair', 'daikara')
LOAD = re.compile(r'^\s*load\(\s*["\']/data/general/(npcs|grids)/([^"\']+)\.lua["\']')


def visible_lines(path):
    source = path.read_text()
    source = re.sub(r'--\[(=*)\[.*?\]\1\]',
                    lambda m: '\n' * m[0].count('\n'), source, flags=re.S)
    return source.splitlines()


def relative(path):
    return path.relative_to(WORKSPACE).as_posix()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    zone_root = WORKSPACE / 'game/modules/tome/data/zones'
    statements = []
    families = defaultdict(set)
    sources = set()
    for path in sorted(zone_root.glob('*/npcs.lua')):
        sources.add(path)
        for number, line in enumerate(visible_lines(path), 1):
            match = LOAD.match(line)
            if not match or match[1] != 'npcs':
                continue
            statements.append(dict(zone=path.parent.name, family=match[2],
                                   source=relative(path), line=number,
                                   statement=line.strip()))
            families[match[2]].add(path.parent.name)
    early = []
    for zone in EARLY:
        grids = zone_root / zone / 'grids.lua'
        sources.add(grids)
        early.append(dict(zone=zone, npc_loads=[s for s in statements if s['zone'] == zone],
                          grid_loads=[dict(family=m[2], source=relative(grids), line=i,
                                           statement=line.strip())
                                      for i, line in enumerate(visible_lines(grids), 1)
                                      if (m := LOAD.match(line)) and m[1] == 'grids']))
    refined = ROOT / 'data/gfx/refined'
    selected = {f'{kind}{parity}.png'
                for kind in ('grass', 'road', 'flower', 'exit',
                             'tree-oak', 'tree-pine', 'tree-willow')
                for parity in range(2)}
    selected |= {f'{kind}{mask}-{parity}-0.png' for kind in ('deep', 'bog')
                 for mask in range(16) for parity in range(2)}
    assert all((refined / name).is_file() for name in selected)
    images = sorted(refined.glob('*.png'))
    other = [p for p in images if p.name not in selected]
    old_roads = [p for p in images if p.name.startswith(('path', 'route'))]
    for path in (ROOT / 'superload/mod/class/Game.lua', ROOT / 'overload/mod/class/CheckerTokens.lua',
                 ROOT / 'hooks/load.lua', WORKSPACE / 'game/modules/tome/class/Grid.lua'):
        sources.add(path)
    for name in ('basic', 'forest', 'water', 'sand'):
        sources.add(WORKSPACE / f'game/modules/tome/data/general/grids/{name}.lua')
    for name in families:
        path = WORKSPACE / f'game/modules/tome/data/general/npcs/{name}.lua'
        if path.is_file():
            sources.add(path)
    result = dict(
        reviewed_runtime='0.5.2', reviewed_commit='c59c21a',
        scope='Base game direct zone imports only; branches are combined; no all.lua expansion, DLC or measured encounters.',
        base_zone_definitions=len(list(zone_root.glob('*/zone.lua'))),
        npc_source_files=len(list(zone_root.glob('*/npcs.lua'))),
        early_zones=early,
        terrain=dict(refined_png_count=len(images),
                     current_selector_output_count=len(selected),
                     current_selector_outputs=sorted(selected),
                     not_selected_by_this_selector=len(other),
                     not_selected_bytes=sum(p.stat().st_size for p in other),
                     selected_bytes=sum((refined / n).stat().st_size for n in selected),
                     legacy_path_route_count=len(old_roads),
                     warning='Static selector audit, not a runtime GPU trace or permission to delete source history.'),
        source_sha256={relative(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(sources)},
    )
    (OUT / 'source-audit.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    with (OUT / 'family-loads.csv').open('w', newline='') as out:
        writer = csv.writer(out, lineterminator='\n')
        writer.writerow(('family', 'direct_zone_count', 'early_zone_count', 'direct_zones'))
        for family, zones in sorted(families.items(), key=lambda x: (-len(x[1]), x[0])):
            writer.writerow((family, len(zones), len(set(EARLY) & zones), ';'.join(sorted(zones))))
    print(f'{result["base_zone_definitions"]} base zone definitions; {len(families)} direct import families')
    print(f'{len(images)} refined PNGs; {len(selected)} current selector outputs; {len(old_roads)} legacy road variants')
    print(OUT)


if __name__ == '__main__':
    main()
