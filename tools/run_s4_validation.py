#!/usr/bin/env python3
"""S4 live check in the isolated fixture: T1 underwater air bubbles (Lake of Nur
L2 both layouts, FLOODED L3, Murgol L2) and T16 callback altars (Spellblaze L2,
Caldera L2).

One cold start per phase. `after` uses the working-tree addon; `before`
installs a TEAA built from HEAD (--before-teaa) and records the pre-S4 state of
the same levels. Per level: the bubble/altar report, the rule digest, the forced
census; in `after` also 48/64px shots of one bubble (or the altar), a native
consumption of that bubble (map:checkEntity on_stand, as Actor:act does) with
64px before/after shots and the charge sequence, and on TOGGLE levels a
Refined->Native->Refined round trip with the rule digest in each state.
Regression probe: Derth and Kryl-Feijan L5 (S2).

The fixture is shared: before each launch the recorded game/Xvfb pids in
session/processes.json are checked via /proc/<pid>/cmdline and the tool waits
(60 s polls) while they are alive; it only stops the processes it started.
Screenshots stay local under evidence/terrain-s4-20260929/screenshots/.
"""
import argparse, json, subprocess, sys
from capture_korpul import Fixture, HOME, ROOT, SESSION, digest, png_size
from run_norgos_validation import stop_started
from run_tw2_validation import launch, read
import run_tw2_validation as tw2

OUT = ROOT / 'evidence/terrain-s4-20260929'
SHOTS = OUT / 'screenshots'
tw2.SHOTS = SHOTS
# (label, zone, level, opts)
LEVELS = [
    ('nur2', 'lake-nur', 2, '{flooded=false}'),
    ('nur2f', 'lake-nur', 2, '{flooded=true}'),
    ('nur3f', 'lake-nur', 3, '{flooded=true}'),
    ('murgol2', 'murgol-lair', 2, None),
    ('spellblaze2', 'mark-spellblaze', 2, None),
    ('caldera2', 'noxious-caldera', 2, None),
]
TOGGLE = {'nur2', 'murgol2', 'caldera2'}
REGRESSION = [('derth', 'town-derth', 1, None), ('kryl5', 'crypt-kryl-feijan', 5, None)]


def run(phase, only=None):
    f = Fixture()
    SHOTS.mkdir(parents=True, exist_ok=True)
    plan = json.loads((SESSION / 'launch-plan.json').read_text())
    assert plan['fixture'] and plan['shaders'] and plan['terrain'] == 'refined'
    if phase == 'after':
        for rel in ('overload/mod/class/CheckerTerrain.lua', 'superload/mod/class/Grid.lua', 'superload/engine/Zone.lua'):
            assert digest(SESSION / 'runtime/game/addons/tome-checker-revised' / rel) == digest(ROOT / rel), rel

    def dump(code, name):
        f.lua(f"ms.dump('/{name}',{code})")
        return read(name)

    def size(tile, x, y):
        f.lua(f"game:setResolution('1920x1080 Windowed',true);config.settings.tome.gfx.size='{tile}x{tile}';"
              f"game:setupDisplayMode(false)")
        return dump(f'tw.view({x},{y})', 's4-view.json')

    def shot(tag):
        name = f's4-{tag}'
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
              "assert(core.shader.active(4));tw=dofile('/data-checker-fixture/monster-live_s4_scene.lua');ms=tw.ms;ms.setup();"
              "tc=dofile('/data-checker-fixture/monster-live_terrain_census.lua');tc.setup();"
              "config.settings.tome.weather_effects=false")
        for label, zone, level, opts in LEVELS:
            if only and label not in only:
                continue
            row = {'zone': zone, 'level': level, 'opts': opts, 'screenshots': []}
            result['levels'][label] = row
            row['enter'] = dump(f"ms.enter('{zone}',{level},{opts or 'nil'})", 's4-enter.json')
            f.lua('ms.caveClearDialogs()')
            row['quiet'] = dump('tw.quiet()', 's4-quiet.json')
            row['rules_before'] = dump('tw.rules()', 's4-rules.json')
            row['cells_natural'] = dump('tw.s4cells()', 's4-cells.json')
            # Photograph target: a bubble with a free floor neighbour, else the altar.
            pick = dump('tw.pickBubble()', 's4-pick.json')
            if pick:
                x, y, sx, sy, tag = pick['x'], pick['y'], pick['sx'], pick['sy'], 'bubble'
            elif row['cells_natural']['altars']:
                a = row['cells_natural']['altars'][0]
                x, y, sx, sy, tag = a['x'], a['y'], a['x'], a['y'] + 2, 'altar'
            else:
                x = None
            row['target'] = pick or (x is not None and {'x': x, 'y': y, 'kind': tag}) or False
            if x is not None:
                row['pose'] = dump(f"tw.poseAt({x},{y},{sx},{sy},'{tag}')", 's4-pose.json')
                row['cell_posed'] = dump(f'tw.report({x},{y})', 's4-cell.json')
                if phase == 'after':
                    for tile in (48, 64):
                        row['screenshots'].append(photo(tile, f'{label}-{tag}', x, y))
                else:
                    row['screenshots'].append(photo(64, f'{label}-{tag}', x, y))
                if phase == 'after' and label in TOGGLE:
                    row['particles_paused'] = dump('tw.pauseParticles(true)', 's4-pause.json')
                    before = photo(64, f'{label}-{tag}-toggle-refined', x, y)
                    rb = dump('tw.rules()', 's4-rules-t0.json')
                    f.lua("ms.setMode('vanilla')")
                    native = photo(64, f'{label}-{tag}-toggle-native', x, y)
                    rn = dump('tw.rules()', 's4-rules-t1.json')
                    cn = dump(f'tw.report({x},{y})', 's4-cell-native.json')
                    f.lua("ms.setMode('refined')")
                    after = photo(64, f'{label}-{tag}-toggle-restored', x, y)
                    ra = dump('tw.rules()', 's4-rules-t2.json')
                    dump('tw.pauseParticles(false)', 's4-pause.json')
                    row['toggle'] = {'target': tag, 'refined': before, 'native': native, 'restored': after, 'cell_native': cn,
                                     'restored_vs_refined': tw2.diff(before, after), 'native_vs_refined': tw2.diff(before, native),
                                     'rules': [rb, rn, ra], 'rules_equal': rb == rn == ra}
                    row['screenshots'] += [before, native, after]
                row['rules_after_pose'] = dump('tw.rules()', 's4-rules-after.json')
                assert row['rules_before'] == row['rules_after_pose'], (label, row['rules_before'], row['rules_after_pose'])
                if tag == 'bubble':
                    pre = photo(64, f'{label}-consume-before', x, y)
                    row['consume'] = dump(f'tw.consume({x},{y})', 's4-consume.json')
                    post = photo(64, f'{label}-consume-after', x, y)
                    row['consume']['frames'] = [pre, post, tw2.diff(pre, post)]
                    row['screenshots'] += [pre, post]
            row['census_forced'] = dump("game.checker_mode=='refined' and tc.census() or {skipped=tostring(game.checker_mode)}",
                                        's4-census.json')
            row['cells_forced'] = dump('tw.s4cells()', 's4-cells-forced.json')
        if not only:
            reg = result['regression'] = {}
            for label, zone, level, opts in REGRESSION:
                r = reg[label] = {'zone': zone, 'level': level}
                r['enter'] = dump(f"ms.enter('{zone}',{level},{opts or 'nil'})", 's4-enter.json')
                f.lua('ms.caveClearDialogs()')
                r['probe_natural'] = dump('tw.probe()', 's4-probe.json')['totals']
                census = dump("game.checker_mode=='refined' and tc.census() or {skipped=tostring(game.checker_mode)}", 's4-census.json')
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
    a = p.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / 'scenes.json'
    data = json.loads(path.read_text()) if path.exists() else {}
    if a.phase == 'before':
        assert a.before_teaa, '--before-teaa is required for the before phase'
    meta = launch(a.before_teaa if a.phase == 'before' else None)
    try:
        result = run(a.phase, only=a.only)
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
