#!/usr/bin/env python3
"""TW1 live check in the isolated fixture: Derth and the Lumberjack village.

One cold start per run. `after` uses the working-tree addon; `before` installs
a HEAD-built TEAA (--teaa, see --before-teaa) to record the pre-TW1 natural
state at the same poses. The fixture is shared: before each launch the
recorded game/Xvfb pids in session/processes.json are checked via
/proc/<pid>/cmdline and the tool waits while they are alive; it never stops a
process it did not start. Screenshots stay local under
evidence/terrain-tw1-20260929/screenshots/ (listed in scenes.json).
"""
import argparse, json, shutil, statistics, subprocess, sys, time
from pathlib import Path
from PIL import Image, ImageChops, ImageStat
from capture_korpul import Fixture, HOME, ROOT, SESSION, digest, png_size
from run_norgos_validation import stop_started

OUT = ROOT / 'evidence/terrain-tw1-20260929'
SHOTS = OUT / 'screenshots'
TOWNS = [('derth', 'town-derth'), ('lumberjack', 'town-lumberjack-village')]


def alive(pid, marker):
    try:
        return marker in (Path('/proc') / str(pid) / 'cmdline').read_bytes()
    except OSError:
        return False


def wait_free():
    while True:
        p = SESSION / 'processes.json'
        meta = json.loads(p.read_text()) if p.exists() else {}
        busy = [k for k, m in (('game', b'/t-engine'), ('xvfb', b'Xvfb')) if meta.get(k) and alive(meta[k], m)]
        if not busy:
            return
        print('fixture busy', {k: meta[k] for k in busy}, 'waiting 60 s', flush=True)
        time.sleep(60)


def launch(teaa=None):
    wait_free()
    cmd = [sys.executable, str(ROOT / 'tools/launch_fixture.py'), '--shaders', '--tiles', '64', '--terrain', 'refined',
           '--resolution', '1920x1080', '--birth', 'Human:Cornac:Male:Berserker']
    if teaa:
        cmd += ['--teaa', 'checker-revised=' + str(teaa)]
    call = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    if call.returncode:
        raise RuntimeError(call.stdout + call.stderr)
    time.sleep(2)
    return json.loads((SESSION / 'processes.json').read_text())


def read(name):
    p = HOME / name
    value = json.loads(p.read_text())
    p.unlink()
    return value


def luminance(frame, samples):
    im = Image.open(SHOTS / frame).convert('L')
    s = samples['tile']
    fam = {}
    for c in samples['cells']:
        x, y = c['sx'], c['sy']
        v = ImageStat.Stat(im.crop((int(x + s * .3), int(y + s * .3), int(x + s * .7), int(y + s * .7)))).mean[0]
        fam.setdefault(c['family'], []).append(v)
    return {k: {'n': len(v), 'median': round(statistics.median(v), 1)} for k, v in sorted(fam.items())}


def diff(a, b):
    d = ImageChops.difference(Image.open(SHOTS / Path(a['file']).name).convert('RGB'),
                              Image.open(SHOTS / Path(b['file']).name).convert('RGB')).convert('L')
    hist = d.histogram()
    total = sum(hist)
    return {'identical': hist[0] == total, 'differing_pixels': total - hist[0],
            'mean_abs': round(sum(i * c for i, c in enumerate(hist)) / total, 4), 'max': max(i for i, c in enumerate(hist) if c)}


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
        name = f'tw1-{tag}'
        src = HOME / (name + '.png')
        src.unlink(missing_ok=True)
        call = subprocess.run([sys.executable, str(ROOT / 'tools/fixture_command.py'), 'shot', name],
                              capture_output=True, text=True, timeout=35)
        f.transcript.append(call.stdout + call.stderr)
        f.check_log()
        assert call.returncode == 0 and src.is_file() and png_size(src) == (1920, 1080), (call.stdout, call.stderr)
        dst = SHOTS / src.name
        shutil.copy2(src, dst)
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
              "assert(core.shader.active(4));tw=dofile('/data-checker-fixture/monster-live_tw1_scene.lua');ms=tw.ms;ms.setup();"
              "tc=dofile('/data-checker-fixture/monster-live_terrain_census.lua');"
              # Fixture-only: no rain/cloud particles so toggle frames compare terrain.
              "config.settings.tome.weather_effects=false")
        for label, zone in TOWNS:
            if only and label != only:
                continue
            row = {'zone': zone, 'screenshots': [], 'poses': {}}
            result['towns'][label] = row
            if phase == 'after':
                # Pre-install FOV behaviour of the gated code (install disabled).
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
            for kind in ('centre', 'remembered'):
                if kind == 'remembered' and label == 'lumberjack':
                    # Not all_remembered: memory only through (staged) exploration.
                    stand = row['poses']['centre'].get('stand') or row['enter_player']
                    row['explore'] = dump(f"tw.explore({stand[0]},{stand[1]})", 'tw-explore.json')
                    row['stats_explored'] = dump('tw.stats()', 'tw-stats-explored.json')
                given = poses_in.get(label, {}).get(kind)
                if given:
                    stand = given.get('stand')
                    f.lua(f"tw.place({given['x']},{given['y']},{stand[0]},{stand[1]})" if stand else
                          f"tw.place({given['x']},{given['y']})")
                    pose = dict(given)
                else:
                    pose = dump(f"tw.pose('{kind}')", 'tw-pose.json')
                row['poses'][kind] = pose
                if not pose.get('found'):
                    continue
                x, y = pose['x'], pose['y']
                for tile in (48, 64):
                    row['screenshots'].append(photo(tile, f'{label}-{kind}', x, y))
                if phase == 'after' and kind == 'remembered':
                    # Same window with the install disabled and records cleared:
                    # the pre-install FOV-only state, then the install again.
                    f.lua("tw.setInstall(false);game.level.map._checker_korpul=nil;tw.apply()")
                    off = photo(64, f'{label}-{kind}-install-off', x, y)
                    row['stats_remembered_install_off'] = dump('tw.stats()', 'tw-stats-off.json')
                    f.lua("tw.setInstall(true);tw.apply()")
                    on = photo(64, f'{label}-{kind}-install-on', x, y)
                    first = next(s for s in row['screenshots'] if s['tag'] == f'after-{label}-{kind}-64')
                    row['install_toggle'] = {'off': off, 'on': on, 'on_vs_first': diff(first, on), 'off_vs_first': diff(first, off)}
                    row['screenshots'] += [off, on]
                if phase == 'after' and kind == 'centre':
                    # Refined -> Native -> Refined at 64px on the same view.
                    before = photo(64, f'{label}-{kind}-toggle-refined', x, y)
                    rb = dump('tw.rules()', 'tw-rules-t0.json')
                    f.lua("ms.setMode('vanilla')")
                    native = photo(64, f'{label}-{kind}-toggle-native', x, y)
                    rn = dump('tw.rules()', 'tw-rules-t1.json')
                    row['native_stats'] = dump('tw.stats()', 'tw-stats-native.json')
                    f.lua("ms.setMode('refined')")
                    after = photo(64, f'{label}-{kind}-toggle-restored', x, y)
                    ra = dump('tw.rules()', 'tw-rules-t2.json')
                    row['toggle'] = {'refined': before, 'native': native, 'restored': after,
                                     'restored_vs_refined': diff(before, after), 'native_vs_refined': diff(before, native),
                                     'rules': [rb, rn, ra], 'rules_equal': rb == rn == ra}
                    row['screenshots'] += [before, native, after]
            row['rules_after'] = dump('tw.rules()', 'tw-rules-after.json')
            assert row['rules_before'] == row['rules_after'], (row['rules_before'], row['rules_after'])
            row['stats_end'] = dump('tw.stats()', 'tw-stats-end.json')
            if phase == 'after':
                # Established forced-visible census (every cell observed as if seen).
                row['census_forced'] = dump('tc.census()', 'tw-census.json')
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
            if 'explore' in row:
                poses[label]['explore'] = True
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
