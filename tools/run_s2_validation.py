#!/usr/bin/env python3
"""S2 live check in the isolated fixture: exits, callback-free doors and static
props inside already-covered zones (T8 FLAT exits, T9 LAKE_NUR re-check, T10
Iron Council / teleport circles / South Beach exit / Rel tunnel, T4 sealed
doors and loose vault rocks, T6 locks, T7 cave doors, T15 symbols, T14 lore
posts, T21 water-edged floors, T24 Trollmire stew).

One cold start per phase. `after` uses the working-tree addon; `before`
installs a TEAA built from HEAD (--before-teaa) and records the pre-S2 state
of the same levels. Every level is entered with the fixture's ms.enter (fresh
generation); levels whose S2 content is random vault content are re-entered
until it appears (bounded). Per level: the S2 cell report (owner, board file,
overlay, redrawn native prop, and the rule fields that must not change), the
rule digest before/after, one pose per S2 id with 64px (and 48px for the first)
screenshots in `after`, and the forced census. Four levels get a
Refined->Native->Refined toggle with the rule digest in each state. Both phases
end with a regression probe (Derth, Valley of the Moon, Dreadfell L1).

The fixture is shared: before each launch the recorded game/Xvfb pids in
session/processes.json are checked via /proc/<pid>/cmdline and the tool waits
(60 s polls) while they are alive; it only stops the processes it started.
Screenshots stay local under evidence/terrain-s2-20260929/screenshots/.
"""
import argparse, json, subprocess, sys
from pathlib import Path
from capture_korpul import Fixture, HOME, ROOT, SESSION, digest, png_size
from run_norgos_validation import stop_started
from run_tw2_validation import launch, read, luminance
import run_tw2_validation as tw2

OUT = ROOT / 'evidence/terrain-s2-20260929'
SHOTS = OUT / 'screenshots'
tw2.SHOTS = SHOTS
DOORS = ['DOOR_VAULT', 'DOOR_VAULT_HORIZ', 'DOOR_VAULT_VERT']
BONE = ['BONE_VAULT_DOOR', 'BONE_VAULT_DOOR_HORIZ', 'BONE_VAULT_DOOR_VERT']
# (label, zone, level, opts (lua table literal or None), hunt ids or None, tries)
LEVELS = [
    ('halfling1', 'halfling-ruins', 1, None, ['FLAT_DOWN4'], 1),
    ('halfling2', 'halfling-ruins', 2, None, DOORS, 6),
    ('halfling4', 'halfling-ruins', 4, None, ['<rel tunnel>'], 1),
    ('conclave1', 'conclave-vault', 1, None, None, 1),
    ('rkescape3', 'reknor-escape', 3, None, None, 1),
    ('bellow1', 'deep-bellow', 1, None, None, 1),
    ('maze2', 'maze', 2, '{collapsed=false}', None, 1),
    ('elven3', 'ancient-elven-ruins', 3, None, None, 1),
    ('beach1', 'south-beach', 1, None, None, 1),
    ('dreadfell3', 'dreadfell', 3, None, ['LORE_NOTE'], 2),
    ('dreadfell2', 'dreadfell', 2, None, DOORS + ['<edged floor>'], 6),
    ('rakshor1', 'rak-shor-pride', 1, None, BONE, 8),
    ('rakshor2', 'rak-shor-pride', 2, None, BONE, 15),
    ('rakshor3', 'rak-shor-pride', 3, None, BONE, 15),
    ('kryl5', 'crypt-kryl-feijan', 5, None, None, 1),
    ('keepsake3', 'keepsake-meadow', 3, None, None, 1),
    ('keepsake6', 'keepsake-meadow', 6, None, None, 1),
    ('graveyard2', 'last-hope-graveyard', 2, None, None, 1),
    ('reknor1', 'reknor', 1, None, ['IRON_THRONE_EDICT'], 2),
    ('ruined1', 'ruined-dungeon', 1, None, None, 1),
    ('trollmire3', 'trollmire', 3, '{flooded=false}', ['STEW'], 3),
    ('trollmire3f', 'trollmire', 3, '{flooded=true}', ['STEW'], 3),
    ('trollmire4', 'trollmire', 4, '{flooded=false}', ['ROCK_VAULT'], 1),
    ('oldforest4d', 'old-forest', 4, '{crystaline=false}', ['LAKE_NUR'], 1),
    ('oldforest4c', 'old-forest', 4, '{crystaline=true}', ['LAKE_NUR'], 1),
    ('oldforest2', 'old-forest', 2, '{crystaline=false}', ['ROCK_VAULT'] + DOORS, 6),
    ('vor2', 'vor-armoury', 2, None, DOORS + ['<edged floor>'], 3),
    ('scint1t', 'scintillating-caves', 1, '{twisted=true}', DOORS + ['<edged floor>'], 4),
]
TOGGLE = {'kryl5', 'keepsake3', 'halfling1', 'trollmire4'}
REGRESSION = [('derth', 'town-derth', 1, None), ('valley', 'valley-moon', 1, None), ('dreadfell1', 'dreadfell', 1, None)]


def run(phase, only=None, shots=True, regression=True):
    f = Fixture()
    SHOTS.mkdir(parents=True, exist_ok=True)
    plan = json.loads((SESSION / 'launch-plan.json').read_text())
    assert plan['fixture'] and plan['shaders'] and plan['terrain'] == 'refined'
    if phase == 'after':
        for rel in ('overload/mod/class/CheckerTerrain.lua', 'superload/mod/class/Grid.lua'):
            assert digest(SESSION / 'runtime/game/addons/tome-checker-revised' / rel) == digest(ROOT / rel), rel

    def dump(code, name):
        f.lua(f"ms.dump('/{name}',{code})")
        return read(name)

    def size(tile, x, y):
        f.lua(f"game:setResolution('1920x1080 Windowed',true);config.settings.tome.gfx.size='{tile}x{tile}';"
              f"game:setupDisplayMode(false)")
        return dump(f'tw.view({x},{y})', 's2-view.json')

    def shot(tag):
        name = f's2-{tag}'
        src = HOME / (name + '.png')
        src.unlink(missing_ok=True)
        call = subprocess.run([sys.executable, str(ROOT / 'tools/fixture_command.py'), 'shot', name],
                              capture_output=True, text=True, timeout=35)
        f.transcript.append(call.stdout + call.stderr)
        f.check_log()
        assert call.returncode == 0 and src.is_file() and png_size(src) == (1920, 1080), (call.stdout, call.stderr)
        dst = SHOTS / src.name
        dst.write_bytes(src.read_bytes())
        return {'file': 'screenshots/' + dst.name, 'sha256': digest(dst), 'tag': tag}

    def photo(tile, tag, x, y):
        view = size(tile, x, y)
        fr = shot(f'{phase}-{tag}-{tile}')
        fr['tile'] = tile
        fr['view'] = view
        return fr

    result = {'phase': phase, 'levels': {}}
    try:
        f.lua("assert(config.settings.cheat and config.settings.disable_all_connectivity and not profile.auth);"
              "assert(core.shader.active(4));tw=dofile('/data-checker-fixture/monster-live_s2_scene.lua');ms=tw.ms;ms.setup();"
              "tc=dofile('/data-checker-fixture/monster-live_terrain_census.lua');tc.setup();"
              "config.settings.tome.weather_effects=false")
        for label, zone, level, opts, hunt, tries in LEVELS:
            if only and label not in only:
                continue
            row = {'zone': zone, 'level': level, 'opts': opts, 'screenshots': [], 'poses': {}}
            result['levels'][label] = row
            o = opts or 'nil'
            if hunt:
                ids = '{' + ','.join(f"'{i}'" for i in hunt) + '}'
                row['enter'] = dump(f"tw.hunt('{zone}',{level},{ids},{o},{tries})", 's2-enter.json')
            else:
                row['enter'] = dump(f"ms.enter('{zone}',{level},{o})", 's2-enter.json')
                f.lua('ms.caveClearDialogs()')
            row['quiet'] = dump('tw.quiet()', 's2-quiet.json')
            row['rules_before'] = dump('tw.rules()', 's2-rules.json')
            row['s2_natural'] = dump('tw.s2cells()', 's2-cells.json')
            # One pose per S2 id (first cell of each), plus the first edged floor.
            targets, seen = [], set()
            for c in row['s2_natural']['cells']:
                if c['id'] not in seen:
                    seen.add(c['id'])
                    targets.append((c['id'], c['x'], c['y']))
            edged = row['s2_natural']['edged']
            if edged['n'] and edged['sample']:
                targets.append(('<edged floor>', edged['sample'][0], edged['sample'][1]))
            row['targets'] = targets
            first = True
            for ident, x, y in targets:
                tag = ident.strip('<>').replace(' ', '-').lower()
                row['poses'][ident] = dump(f"tw.poseAt({x},{y},{x},{y+1},'{tag}')", 's2-pose.json')
                if shots:
                    for tile in ((48, 64) if (phase == 'after' and first) else (64,)):
                        row['screenshots'].append(photo(tile, f'{label}-{tag}', x, y))
                row.setdefault('cell_after_pose', {})[ident] = dump(f'tw.s2cell({x},{y})', 's2-cell.json')
                first = False
            if phase == 'after' and label in TOGGLE and targets:
                ident, x, y = targets[0]
                tag = ident.strip('<>').replace(' ', '-').lower()
                row['particles_paused'] = dump('tw.pauseParticles(true)', 's2-pause.json')
                before = photo(64, f'{label}-{tag}-toggle-refined', x, y)
                rb = dump('tw.rules()', 's2-rules-t0.json')
                f.lua("ms.setMode('vanilla')")
                native = photo(64, f'{label}-{tag}-toggle-native', x, y)
                rn = dump('tw.rules()', 's2-rules-t1.json')
                cn = dump(f'tw.s2cell({x},{y})', 's2-cell-native.json')
                f.lua("ms.setMode('refined')")
                after = photo(64, f'{label}-{tag}-toggle-restored', x, y)
                ra = dump('tw.rules()', 's2-rules-t2.json')
                dump('tw.pauseParticles(false)', 's2-pause.json')
                row['toggle'] = {'target': ident, 'refined': before, 'native': native, 'restored': after, 'cell_native': cn,
                                 'restored_vs_refined': tw2.diff(before, after), 'native_vs_refined': tw2.diff(before, native),
                                 'rules': [rb, rn, ra], 'rules_equal': rb == rn == ra}
                row['screenshots'] += [before, native, after]
            row['s2_posed'] = dump('tw.s2cells()', 's2-cells-posed.json')
            row['rules_after'] = dump('tw.rules()', 's2-rules-after.json')
            assert row['rules_before'] == row['rules_after'], (label, row['rules_before'], row['rules_after'])
            row['census_forced'] = dump("game.checker_mode=='refined' and tc.census() or {skipped=tostring(game.checker_mode)}",
                                        's2-census.json')
            row['s2_forced'] = dump('tw.s2cells()', 's2-cells-forced.json')
        if regression and not only:
            reg = result['regression'] = {}
            for label, zone, level, opts in REGRESSION:
                r = reg[label] = {'zone': zone, 'level': level}
                r['enter'] = dump(f"ms.enter('{zone}',{level},{opts or 'nil'})", 's2-enter.json')
                f.lua('ms.caveClearDialogs()')
                r['probe_natural'] = dump('tw.probe()', 's2-probe.json')['totals']
                census = dump("game.checker_mode=='refined' and tc.census() or {skipped=tostring(game.checker_mode)}", 's2-census.json')
                r['census_forced'] = {k: census.get(k) for k in ('total', 'converted', 'native', 'converted_stone', 'converted_forest', 'groups', 'skipped')}
        return result
    finally:
        (OUT / (f'validation-{phase}' + ('-' + '-'.join(only) if only else '') + '.txt')).write_text(
            (''.join(f.transcript) + f.new_log()).rstrip() + '\n')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('phase', choices=('after', 'before'))
    p.add_argument('--before-teaa', help='TEAA built from HEAD for the before phase')
    p.add_argument('--only', nargs='*')
    p.add_argument('--no-shots', action='store_true')
    p.add_argument('--no-regression', action='store_true')
    a = p.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / 'scenes.json'
    data = json.loads(path.read_text()) if path.exists() else {}
    if a.phase == 'before':
        assert a.before_teaa, '--before-teaa is required for the before phase'
    meta = launch(a.before_teaa if a.phase == 'before' else None)
    try:
        result = run(a.phase, only=a.only, shots=not a.no_shots, regression=not a.no_regression)
        result['launch_plan'] = json.loads((SESSION / 'launch-plan.json').read_text())
        key = a.phase + ('-' + '-'.join(a.only) if a.only else '')
        data[key] = result
        path.write_text(json.dumps(data, ensure_ascii=False, indent=1) + '\n')
        print('PASS', key, flush=True)
    finally:
        stop_started(meta)
        print('STOP', a.phase, flush=True)


if __name__ == '__main__':
    main()
