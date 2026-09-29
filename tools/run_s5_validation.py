#!/usr/bin/env python3
"""S5 live check in the isolated fixture: six reachable zones on existing
families (Dreadfell ambush, Shadow Crypt L1-3, Tannen's Tower L1-4, Valley of
the Moon, Ring of Blood L1-3, Derth's southeast arena).

One cold start per run. `after` uses the working-tree addon; `before` installs
a TEAA built from HEAD (--before-teaa) to record the pre-S5 natural state at
the same poses. Every level is entered with the fixture's ms.enter (fresh
generation); per level: natural stats and identity probe, rule digest,
screenshots (48/64 after, 64 before), lit-pixel pairs (after), a native
listing, a native-FOV walk and a forced census (after). Three levels get a
Refined->Native->Refined toggle with the rule digest taken in each state.
`after` also replays two native quest terrain placements (Dreadfell ambush
exit through the quest's killed_ukruk; Shadow Crypt stairs as the shade's
on_die sets them). Both phases end with a regression probe of Dreadfell L1,
Derth and Old Forest L1.

The fixture is shared: before each launch the recorded game/Xvfb pids in
session/processes.json are checked via /proc/<pid>/cmdline and the tool waits
while they are alive; it never stops a process it did not start. Screenshots
stay local under evidence/terrain-s5-20260929/screenshots/.
"""
import argparse, json, subprocess, sys
from pathlib import Path
from capture_korpul import Fixture, HOME, ROOT, SESSION, digest, png_size
from run_norgos_validation import stop_started
from run_tw2_validation import launch, read, luminance
from run_tw6_validation import pair_values
import run_tw2_validation as tw2
import run_tw6_validation as tw6

OUT = ROOT / 'evidence/terrain-s5-20260929'
SHOTS = OUT / 'screenshots'
tw2.SHOTS = SHOTS
tw6.SHOTS = SHOTS
# (label, zone, level, poses). A pose is (name, cx, cy, sx, sy); None means
# "centre on the player where ms.enter put it".
LEVELS = [
    ('ambush', 'dreadfell-ambush', 1, [('glade', 8, 5, 8, 5)]),
    ('crypt1', 'shadow-crypt', 1, [('start', None)]),
    ('crypt2', 'shadow-crypt', 2, [('start', None)]),
    ('crypt3', 'shadow-crypt', 3, [('hall', 7, 7, 7, 9)]),
    ('tannen1', 'tannen-tower', 1, [('cells', 12, 12, 5, 14), ('grove', 16, 15, 15, 14)]),
    ('tannen2', 'tannen-tower', 2, [('pools', 12, 12, 12, 8)]),
    ('tannen3', 'tannen-tower', 3, [('ring', 12, 10, 19, 5)]),
    ('tannen4', 'tannen-tower', 4, [('roof', 12, 12, 12, 12)]),
    ('valley', 'valley-moon', 1, [('lake', 26, 23, 30, 25), ('portal', 40, 8, 40, 9), ('shore', 10, 12, 9, 12)]),
    ('blood1', 'ring-of-blood', 1, [('start', None)]),
    ('blood2', 'ring-of-blood', 2, [('start', None)]),
    ('blood3', 'ring-of-blood', 3, [('arena', 24, 23, 34, 23)]),
    ('arena', 'arena-unlock', 1, [('pit', 8, 7, 8, 12)]),
]
TOGGLE = {('valley', 'lake'), ('blood3', 'arena'), ('tannen1', 'cells'), ('crypt3', 'hall'), ('arena', 'pit')}
# Dreadfell last: after the fixture granted staff-absorption for the ambush
# replay, leaving Dreadfell natively redirects to the ambush zone.
REGRESSION = [('derth', 'town-derth', 1), ('oldforest', 'old-forest', 1), ('dreadfell', 'dreadfell', 1)]


def run(phase, only=None, shots=True, regression=True):
    f = Fixture()
    SHOTS.mkdir(parents=True, exist_ok=True)
    plan = json.loads((SESSION / 'launch-plan.json').read_text())
    assert plan['fixture'] and plan['shaders'] and plan['terrain'] == 'refined'
    if phase == 'after':
        for rel in ('overload/mod/class/CheckerTerrain.lua', 'superload/mod/class/Grid.lua', 'superload/mod/class/Game.lua'):
            assert digest(SESSION / 'runtime/game/addons/tome-checker-revised' / rel) == digest(ROOT / rel), rel

    def dump(code, name):
        f.lua(f"ms.dump('/{name}',{code})")
        return read(name)

    def size(tile, x, y):
        f.lua(f"game:setResolution('1920x1080 Windowed',true);config.settings.tome.gfx.size='{tile}x{tile}';"
              f"game:setupDisplayMode(false)")
        return dump(f'tw.view({x},{y})', 's5-view.json')

    def shot(tag):
        name = f's5-{tag}'
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

    def photo(tile, tag, x, y, pairs=False):
        view = size(tile, x, y)
        fr = shot(f'{phase}-{tag}-{tile}')
        fr['tile'] = tile
        fr['view'] = view
        fr['luminance'] = luminance(Path(fr['file']).name, dump('tw.samples()', 's5-samples.json'))
        if pairs:
            data = dump('tw.pairs()', 's5-pairs.json')
            fr['lit_pixels'] = pair_values(Path(fr['file']).name, data)
            fr['water_edge'] = pair_values(Path(fr['file']).name, data, 'water')
        return fr

    result = {'phase': phase, 'levels': {}}
    try:
        f.lua("assert(config.settings.cheat and config.settings.disable_all_connectivity and not profile.auth);"
              "assert(core.shader.active(4));tw=dofile('/data-checker-fixture/monster-live_s5_scene.lua');ms=tw.ms;ms.setup();"
              "tc=dofile('/data-checker-fixture/monster-live_terrain_census.lua');tc.setup();"
              "config.settings.tome.weather_effects=false")
        for label, zone, level, poses in LEVELS:
            if only and label not in only:
                continue
            row = {'zone': zone, 'level': level, 'screenshots': [], 'poses': {}}
            result['levels'][label] = row
            row['enter'] = dump(f"ms.enter('{zone}',{level})", 's5-enter.json')
            f.lua('ms.caveClearDialogs()')
            row['quiet'] = dump('tw.quiet()', 's5-quiet.json')
            st = dump('tw.stats()', 's5-stats.json')
            row['stats_natural'] = {k: v for k, v in st.items() if k != 'shop_images'}
            row['rules_before'] = dump('tw.rules()', 's5-rules.json')
            row['probe_natural'] = dump('tw.probe()', 's5-probe.json')
            row['kinds_natural'] = dump('tw.tw3()', 's5-kinds.json')
            row['natives_natural'] = dump('tw.natives()', 's5-natives.json')
            for pose in poses:
                kind = pose[0]
                if pose[1] is None:
                    px, py = row['enter']['player_x'], row['enter']['player_y']
                    cx, cy, sx, sy = px, py, px, py
                else:
                    cx, cy, sx, sy = pose[1:]
                row['poses'][kind] = dump(f"tw.poseAt({cx},{cy},{sx},{sy},'{kind}')", 's5-pose.json')
                if not shots:
                    continue
                for tile in ((48, 64) if phase == 'after' else (64,)):
                    row['screenshots'].append(photo(tile, f'{label}-{kind}', cx, cy, pairs=phase == 'after' and tile == 64))
                if phase == 'after' and (label, kind) in TOGGLE:
                    row.setdefault('particles_paused', {})[kind] = dump('tw.pauseParticles(true)', 's5-pause.json')
                    before = photo(64, f'{label}-{kind}-toggle-refined', cx, cy)
                    rb = dump('tw.rules()', 's5-rules-t0.json')
                    f.lua("ms.setMode('vanilla')")
                    native = photo(64, f'{label}-{kind}-toggle-native', cx, cy)
                    rn = dump('tw.rules()', 's5-rules-t1.json')
                    row.setdefault('native_probe', {})[kind] = dump('tw.probe()', 's5-probe-native.json')['totals']
                    f.lua("ms.setMode('refined')")
                    after = photo(64, f'{label}-{kind}-toggle-restored', cx, cy)
                    ra = dump('tw.rules()', 's5-rules-t2.json')
                    dump('tw.pauseParticles(false)', 's5-pause.json')
                    row.setdefault('toggle', {})[kind] = {
                        'refined': before, 'native': native, 'restored': after,
                        'restored_vs_refined': tw2.diff(before, after), 'native_vs_refined': tw2.diff(before, native),
                        'rules': [rb, rn, ra], 'rules_equal': rb == rn == ra}
                    row['screenshots'] += [before, native, after]
            row['rules_after'] = dump('tw.rules()', 's5-rules-after.json')
            assert row['rules_before'] == row['rules_after'], (label, row['rules_before'], row['rules_after'])
            if phase == 'after' and label == 'ambush':
                row['quest_exit'] = dump('tw.ambushExit()', 's5-ambush-exit.json')
                if shots:
                    ex = row['quest_exit']
                    f.lua(f"tw.poseAt({ex['x']},{ex['y']},{ex['x']},{ex['y']},'exit')")
                    row['screenshots'].append(photo(64, f'{label}-quest-exit', ex['x'], ex['y']))
            if phase == 'after' and label == 'crypt3':
                row['quest_exit'] = dump('tw.cryptExit()', 's5-crypt-exit.json')
                if shots:
                    row['screenshots'].append(photo(64, f'{label}-quest-exit', 7, 7))
            # Natural state after a native-FOV walk over every free cell, then
            # the forced census (every stone cell observed as if seen).
            p = row['enter']
            row['walk'] = dump(f"tw.walk({p['player_x']},{p['player_y']})", 's5-walk.json')
            row['probe_walked'] = dump('tw.probe()', 's5-probe-walked.json')['totals']
            row['natives_walked'] = dump('tw.natives()', 's5-natives-walked.json')
            row['census_forced'] = dump("game.checker_mode=='refined' and tc.census() or {skipped=tostring(game.checker_mode)}",
                                        's5-census.json')
        if regression and not only:
            reg = result['regression'] = {}
            for label, zone, level in REGRESSION:
                r = reg[label] = {'zone': zone, 'level': level}
                r['enter'] = dump(f"ms.enter('{zone}',{level})", 's5-enter.json')
                f.lua('ms.caveClearDialogs()')
                r['probe_natural'] = dump('tw.probe()', 's5-probe.json')['totals']
                census = dump("game.checker_mode=='refined' and tc.census() or {skipped=tostring(game.checker_mode)}", 's5-census.json')
                r['census_forced'] = {k: census.get(k) for k in ('total', 'converted', 'native', 'converted_stone', 'converted_forest', 'groups', 'skipped')}
        return result
    finally:
        (OUT / (f'validation-{phase}' + ('-' + '-'.join(only) if only else '') + '.txt')).write_text(
            (''.join(f.transcript) + f.new_log()).rstrip() + '\n')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('phase', choices=('after', 'before', 'survey'))
    p.add_argument('--before-teaa', help='TEAA built from HEAD for the before phase')
    p.add_argument('--only', nargs='*')
    p.add_argument('--no-regression', action='store_true')
    a = p.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / 'scenes.json'
    survey = json.loads(path.read_text()) if path.exists() else {}
    if a.phase == 'before':
        assert a.before_teaa, '--before-teaa is required for the before phase'
    meta = launch(a.before_teaa if a.phase == 'before' else None)
    try:
        phase = 'after' if a.phase == 'survey' else a.phase
        result = run(phase, only=a.only, shots=a.phase != 'survey', regression=not a.no_regression)
        result['launch_plan'] = json.loads((SESSION / 'launch-plan.json').read_text())
        survey[a.phase] = result
        path.write_text(json.dumps(survey, ensure_ascii=False, indent=1) + '\n')
        print('PASS', a.phase, flush=True)
    finally:
        stop_started(meta)
        print('STOP', a.phase, flush=True)


if __name__ == '__main__':
    main()
