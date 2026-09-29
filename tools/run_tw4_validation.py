#!/usr/bin/env python3
"""TW4 live check in the isolated fixture: Shatur and Point Zero.

One cold start per run. `after` uses the working-tree addon; `before` installs
the HEAD release TEAA (--teaa, see --before-teaa) to record the pre-TW4
natural state at the same fixed poses (same flow as tools/run_tw3_validation.py).
Both phases end with a regression probe of the seven 0.6.28 towns so their
counts can be compared before/after. The fixture is shared: before each launch
the recorded game/Xvfb pids in session/processes.json are checked via
/proc/<pid>/cmdline and the tool waits while they are alive; it never stops a
process it did not start. Screenshots stay local under
evidence/terrain-tw4-20260929/screenshots/.
"""
import argparse, json, subprocess, sys
from pathlib import Path
from capture_korpul import Fixture, HOME, ROOT, SESSION, digest, png_size
from run_norgos_validation import stop_started
from run_tw2_validation import launch, read, luminance
import run_tw2_validation as tw2

OUT = ROOT / 'evidence/terrain-tw4-20260929'
SHOTS = OUT / 'screenshots'
tw2.SHOTS = SHOTS  # luminance()/diff() read frames from this run's folder
TOWNS = [('shatur', 'town-shatur'), ('pointzero', 'town-point-zero')]
# Fixed poses on the verified static maps (data/maps/towns/*.lua): window
# centre, stand cell. 'remembered' stands far away so no window cell is in FOV.
POSES = {
    'shatur': [('remembered', (22, 8, 30, 47)),   # snow shops (4,3,2) from the southern exit road
               ('centre', (25, 31, 25, 31)),      # statue, shops 5/7, green forest glade
               ('boundary', (24, 20, 24, 23)),    # lake, cobblestone bridge, snow/green edge
               ('snow', (22, 8, 23, 9))],         # snow glade with three shops on ROCKY_GROUND
    'pointzero': [('remembered', (20, 8, 38, 46)),  # north shop blocks from the Zemekkys ring
                  ('centre', (20, 8, 20, 11)),      # shops 1-4,7,8, floating rocks, space
                  ('beam', (23, 27, 24, 29)),       # beam endpoints (23,25)/(23,28), RIFT exit
                  ('south', (25, 42, 25, 44)),      # shops 5/6, grass, trees, water, mountain, cold forest
                  ('rift', (40, 44, 36, 44))],      # SPACETIME_RIFT ring round the VOID floor
}
TOGGLE = {'centre', 'boundary', 'beam', 'south'}
REGRESSION = [('derth', 'town-derth'), ('lumberjack', 'town-lumberjack-village'), ('lasthope', 'town-last-hope'),
              ('elvala', 'town-elvala'), ('zigur', 'town-zigur'), ('angolwen', 'town-angolwen'),
              ('council', 'town-iron-council')]


def run(phase, only=None, regression=True):
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
        return dump(f'tw.view({x},{y})', 'tw-view.json')

    def shot(tag):
        name = f'tw4-{tag}'
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
        fr['luminance'] = luminance(Path(fr['file']).name, dump('tw.samples()', 'tw-samples.json'))
        return fr

    result = {'phase': phase, 'towns': {}}
    try:
        f.lua("assert(config.settings.cheat and config.settings.disable_all_connectivity and not profile.auth);"
              "assert(core.shader.active(4));tw=dofile('/data-checker-fixture/monster-live_tw4_scene.lua');ms=tw.ms;ms.setup();"
              "tc=dofile('/data-checker-fixture/monster-live_terrain_census.lua');"
              # Fixture-only: no rain/cloud particles so toggle frames compare terrain.
              "config.settings.tome.weather_effects=false")
        for label, zone in TOWNS:
            if only and label != only:
                continue
            row = {'zone': zone, 'screenshots': [], 'poses': {}}
            result['towns'][label] = row
            if phase == 'after':
                f.lua('tw.setInstall(false)')
            row['enter'] = dump(f"ms.enter('{zone}',1)", 'tw-enter.json')
            row['enter_player'] = [row['enter']['player_x'], row['enter']['player_y']]
            f.lua('ms.caveClearDialogs()')
            row['stats_natural'] = dump('tw.stats()', 'tw-stats.json')
            if phase == 'after':
                row['stats_install_off'] = row['stats_natural']
                row['probe_install_off'] = dump('tw.probe()', 'tw-probe-off.json')['totals']
                f.lua('tw.setInstall(true)')
                dump('tw.apply()', 'tw-apply.json')
                row['stats_natural'] = dump('tw.stats()', 'tw-stats.json')
            row['rules_before'] = dump('tw.rules()', 'tw-rules.json')
            row['probe_natural'] = dump('tw.probe()', 'tw-probe.json')
            row['kinds_natural'] = dump('tw.tw3()', 'tw-kinds.json')
            row['endpoints'] = dump('tw.endpoints()', 'tw-endpoints.json')
            row['quiet'] = dump('tw.quiet()', 'tw-quiet.json')
            for kind, (cx, cy, sx, sy) in POSES[label]:
                pose = row['poses'][kind] = dump(f"tw.poseAt({cx},{cy},{sx},{sy},'{kind}')", 'tw-pose.json')
                for tile in (48, 64):
                    row['screenshots'].append(photo(tile, f'{label}-{kind}', cx, cy))
                if phase == 'after' and kind == 'remembered':
                    f.lua("tw.setInstall(false);game.level.map._checker_korpul=nil;tw.apply()")
                    off = photo(64, f'{label}-{kind}-install-off', cx, cy)
                    row['stats_remembered_install_off'] = dump('tw.stats()', 'tw-stats-off.json')
                    f.lua("tw.setInstall(true);tw.apply()")
                    on = photo(64, f'{label}-{kind}-install-on', cx, cy)
                    first = next(s for s in row['screenshots'] if s['tag'] == f'after-{label}-{kind}-64')
                    row['install_toggle'] = {'off': off, 'on': on, 'on_vs_first': tw2.diff(first, on),
                                             'off_vs_first': tw2.diff(first, off)}
                    row['screenshots'] += [off, on]
                if phase == 'after' and kind in TOGGLE:
                    # Animated beam particles are not terrain: paused for the comparison.
                    row.setdefault('particles_paused', {})[kind] = dump('tw.pauseParticles(true)', 'tw-pause.json')
                    before = photo(64, f'{label}-{kind}-toggle-refined', cx, cy)
                    rb = dump('tw.rules()', 'tw-rules-t0.json')
                    f.lua("ms.setMode('vanilla')")
                    native = photo(64, f'{label}-{kind}-toggle-native', cx, cy)
                    rn = dump('tw.rules()', 'tw-rules-t1.json')
                    row.setdefault('native_probe', {})[kind] = dump('tw.probe()', 'tw-probe-native.json')['totals']
                    f.lua("ms.setMode('refined')")
                    after = photo(64, f'{label}-{kind}-toggle-restored', cx, cy)
                    ra = dump('tw.rules()', 'tw-rules-t2.json')
                    dump('tw.pauseParticles(false)', 'tw-pause.json')
                    row.setdefault('toggle', {})[kind] = {
                        'refined': before, 'native': native, 'restored': after,
                        'restored_vs_refined': tw2.diff(before, after), 'native_vs_refined': tw2.diff(before, native),
                        'rules': [rb, rn, ra], 'rules_equal': rb == rn == ra}
                    row['screenshots'] += [before, native, after]
            row['rules_after'] = dump('tw.rules()', 'tw-rules-after.json')
            assert row['rules_before'] == row['rules_after'], (row['rules_before'], row['rules_after'])
            row['stats_end'] = dump('tw.stats()', 'tw-stats-end.json')
            row['probe_end'] = dump('tw.probe()', 'tw-probe-end.json')
            row['kinds_end'] = dump('tw.tw3()', 'tw-kinds-end.json')
            # An ungated town (before) runs in vanilla mode: every cell is native.
            row['census_forced'] = dump("game.checker_mode=='refined' and tc.census() or {skipped=tostring(game.checker_mode)}",
                                        'tw-census.json')
        if regression and not only:
            # The seven 0.6.28 towns: natural probe, then the forced census.
            reg = result['regression'] = {}
            for label, zone in REGRESSION:
                r = reg[label] = {'zone': zone}
                r['enter'] = dump(f"ms.enter('{zone}',1)", 'tw-enter.json')
                f.lua('ms.caveClearDialogs()')
                r['probe_natural'] = dump('tw.probe()', 'tw-probe.json')['totals']
                r['stats_natural'] = {k: v for k, v in dump('tw.stats()', 'tw-stats.json').items() if k not in ('shop_images',)}
                census = dump('tc.census()', 'tw-census.json')
                r['census_forced'] = {k: census[k] for k in ('total', 'converted', 'native', 'converted_stone', 'converted_forest', 'groups')}
        return result
    finally:
        (OUT / (f'validation-{phase}' + (f'-{only}' if only else '') + '.txt')).write_text((''.join(f.transcript) + f.new_log()).rstrip() + '\n')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('phase', choices=('after', 'before'))
    p.add_argument('--before-teaa', help='HEAD release tome-checker-revised-<v>.teaa for the before phase')
    p.add_argument('--town', choices=[t[0] for t in TOWNS], help='Re-run one town and merge it into scenes.json')
    a = p.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / 'scenes.json'
    survey = json.loads(path.read_text()) if path.exists() else {}
    if a.phase == 'before':
        assert a.before_teaa, '--before-teaa is required for the before phase'
    meta = launch(a.before_teaa if a.phase == 'before' else None)
    try:
        result = run(a.phase, a.town)
        result['launch_plan'] = json.loads((SESSION / 'launch-plan.json').read_text())
        if a.town and a.phase in survey:
            survey[a.phase]['towns'].update(result['towns'])
            survey[a.phase].setdefault('reruns', []).append({'town': a.town, 'launch_plan': result['launch_plan']})
        else:
            survey[a.phase] = result
        path.write_text(json.dumps(survey, ensure_ascii=False, indent=1) + '\n')
        print('PASS', a.phase, flush=True)
    finally:
        stop_started(meta)
        print('STOP', a.phase, flush=True)


if __name__ == '__main__':
    main()
