#!/usr/bin/env python3
"""TW3 live check in the isolated fixture: Zigur, Angolwen, Iron Council.

One cold start per run. `after` uses the working-tree addon; `before` installs
a HEAD-built TEAA (--teaa, see --before-teaa) to record the pre-TW3 natural
state at the same poses (same flow as tools/run_tw2_validation.py). `after`
ends with a regression probe of the TW1/TW2 towns (Derth, Lumberjack, Last
Hope, Elvala). The fixture is shared: before each launch the recorded
game/Xvfb pids in session/processes.json are checked via /proc/<pid>/cmdline
and the tool waits while they are alive; it never stops a process it did not
start. Screenshots stay local under evidence/terrain-tw3-20260929/screenshots/.
"""
import argparse, json, subprocess, sys
from pathlib import Path
from capture_korpul import Fixture, HOME, ROOT, SESSION, digest, png_size
from run_norgos_validation import stop_started
from run_tw2_validation import launch, read, luminance
import run_tw2_validation as tw2

OUT = ROOT / 'evidence/terrain-tw3-20260929'
SHOTS = OUT / 'screenshots'
tw2.SHOTS = SHOTS  # luminance()/diff() read frames from this run's folder
TOWNS = [('zigur', 'town-zigur'), ('angolwen', 'town-angolwen'), ('council', 'town-iron-council')]
# Poses: Lua expressions returning a pose table. 'centre' is each town's heart
# (Zigur's shop quarter, Angolwen's fountain plaza, the council hall's crystal
# cluster and statues); 'remembered' is a stone window with no cell in FOV.
POSES = {
    'zigur': [('centre', "tw.pose('centre')"), ('arena', "tw.poseOn('^ROCK$',0,0,false,'arena')"),
              ('post', "tw.poseOn('^POST$',0,-2,false,'post')"), ('remembered', "tw.pose('remembered')")],
    'angolwen': [('centre', "tw.poseOn('^FOUNTAIN',0,0,false,'centre')"), ('shops', "tw.poseOn('^HARDWALL',0,1,false,'shops')"),
                 ('remembered', "tw.pose('remembered')")],
    'council': [('centre', "tw.poseOn('^CRYSTAL_WALL',0,0,false,'centre')"), ('exits', "tw.poseOn('^DEEP_BELLOW$',0,4,false,'exits')"),
                ('escape', "tw.poseOn('^ESCAPE_REKNOR$',0,4,false,'escape')"),
                ('remembered', "tw.pose('remembered')")],
}
TOGGLE = {'centre', 'arena', 'exits'}
REGRESSION = [('derth', 'town-derth'), ('lumberjack', 'town-lumberjack-village'), ('lasthope', 'town-last-hope'), ('elvala', 'town-elvala')]


def diff(a, b):
    return tw2.diff(a, b)


def run(phase, poses_in, only=None):
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
        name = f'tw3-{tag}'
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
              "assert(core.shader.active(4));tw=dofile('/data-checker-fixture/monster-live_tw3_scene.lua');ms=tw.ms;ms.setup();"
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
                f.lua('tw.setInstall(true)')
                dump('tw.apply()', 'tw-apply.json')
                row['stats_natural'] = dump('tw.stats()', 'tw-stats.json')
            row['rules_before'] = dump('tw.rules()', 'tw-rules.json')
            row['probe_natural'] = dump('tw.probe()', 'tw-probe.json')
            row['tw3_natural'] = dump('tw.tw3()', 'tw-tw3.json')
            if label == 'angolwen':
                # Not all_remembered: native memory accrues only by walking.
                # Fixture staging walks every free cell with native FOV, then
                # returns to the arrival cell (seens are never forced).
                p = row['enter_player']
                row['explore'] = dump(f"tw.explore({p[0]},{p[1]})", 'tw-explore.json')
                row['stats_explored'] = dump('tw.stats()', 'tw-stats-x.json')
                row['probe_explored'] = dump('tw.probe()', 'tw-probe-x.json')
            for kind, expr in POSES[label]:
                given = poses_in.get(label, {}).get(kind)
                if given:
                    stand = given.get('stand')
                    f.lua(f"tw.place({given['x']},{given['y']},{stand[0]},{stand[1]})" if stand else
                          f"tw.place({given['x']},{given['y']})")
                    pose = dict(given)
                else:
                    pose = dump(expr, 'tw-pose.json')
                row['poses'][kind] = pose
                if not pose.get('found'):
                    continue
                x, y = pose['x'], pose['y']
                for tile in (48, 64):
                    row['screenshots'].append(photo(tile, f'{label}-{kind}', x, y))
                if phase == 'after' and kind == 'remembered':
                    f.lua("tw.setInstall(false);game.level.map._checker_korpul=nil;tw.apply()")
                    off = photo(64, f'{label}-{kind}-install-off', x, y)
                    row['stats_remembered_install_off'] = dump('tw.stats()', 'tw-stats-off.json')
                    f.lua("tw.setInstall(true);tw.apply()")
                    on = photo(64, f'{label}-{kind}-install-on', x, y)
                    first = next(s for s in row['screenshots'] if s['tag'] == f'after-{label}-{kind}-64')
                    row['install_toggle'] = {'off': off, 'on': on, 'on_vs_first': diff(first, on), 'off_vs_first': diff(first, off)}
                    row['screenshots'] += [off, on]
                if phase == 'after' and kind in TOGGLE:
                    before = photo(64, f'{label}-{kind}-toggle-refined', x, y)
                    rb = dump('tw.rules()', 'tw-rules-t0.json')
                    f.lua("ms.setMode('vanilla')")
                    native = photo(64, f'{label}-{kind}-toggle-native', x, y)
                    rn = dump('tw.rules()', 'tw-rules-t1.json')
                    row.setdefault('native_stats', {})[kind] = dump('tw.stats()', 'tw-stats-native.json')
                    f.lua("ms.setMode('refined')")
                    after = photo(64, f'{label}-{kind}-toggle-restored', x, y)
                    ra = dump('tw.rules()', 'tw-rules-t2.json')
                    row.setdefault('toggle', {})[kind] = {
                        'refined': before, 'native': native, 'restored': after,
                        'restored_vs_refined': diff(before, after), 'native_vs_refined': diff(before, native),
                        'rules': [rb, rn, ra], 'rules_equal': rb == rn == ra}
                    row['screenshots'] += [before, native, after]
            row['rules_after'] = dump('tw.rules()', 'tw-rules-after.json')
            assert row['rules_before'] == row['rules_after'], (row['rules_before'], row['rules_after'])
            row['stats_end'] = dump('tw.stats()', 'tw-stats-end.json')
            row['probe_end'] = dump('tw.probe()', 'tw-probe-end.json')
            row['tw3_end'] = dump('tw.tw3()', 'tw-tw3-end.json')
            if phase == 'after':
                row['census_forced'] = dump('tc.census()', 'tw-census.json')
        if phase == 'after' and not only:
            # Regression: TW1/TW2 towns keep 0 native cells (natural state,
            # then the established forced-visible census).
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
    p.add_argument('--before-teaa', help='HEAD-built tome-checker-revised-<v>.teaa for the before phase')
    p.add_argument('--town', choices=[t[0] for t in TOWNS], help='Re-run one town and merge it into scenes.json')
    a = p.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / 'scenes.json'
    survey = json.loads(path.read_text()) if path.exists() else {}
    poses = {}
    if a.phase == 'before':
        assert a.before_teaa, '--before-teaa is required for the before phase'
        for label, row in survey['after']['towns'].items():
            poses[label] = {k: v for k, v in row['poses'].items() if v.get('found')}
    meta = launch(a.before_teaa if a.phase == 'before' else None)
    try:
        result = run(a.phase, poses, a.town)
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
