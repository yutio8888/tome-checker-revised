#!/usr/bin/env python3
"""S9 live check in the isolated fixture: High Peak L1-11 (L1-4 caverns on
the cave family, L5-10 Roomer and the static Sanctum L11 on the stone family
with the S8 dark brick; the two next-level stairs as exact S2 specs).

One cold start per run. `before` installs a TEAA built from HEAD; `after`
installs HEAD plus exactly the S9 files (the runner checks the package bytes
against the working tree, so the concurrent monster batch's unfinished files
are never loaded). Every level is entered with the fixture's ms.enter after
`rng.seed(<fixed>)`. Per level: identity/owner counts, native listing, rule
digest, a forced census, poses photographed at 64px (before) or 48/64px
(after) with lit-pixel pairs at 64px. Selected levels get a Refined->Native->
Refined toggle with the rule digest in each state. Regression levels
(Dreadfell L1, Derth, Telmur L1 as an S8 zone) are photographed at the fixed
seed in both phases for a byte comparison.

The fixture is shared: before each launch the recorded game/Xvfb pids in
session/processes.json are checked via /proc/<pid>/cmdline and the tool waits
while they are alive; it never stops a process it did not start. Screenshots
stay local under evidence/terrain-s9-20260929/screenshots/.
"""
import argparse, json, statistics, subprocess, sys, zipfile
from pathlib import Path
from PIL import Image, ImageStat
from capture_korpul import Fixture, HOME, ROOT, SESSION, digest, png_size
from run_norgos_validation import stop_started
from run_tw2_validation import launch, read
import run_tw2_validation as tw2

OUT = ROOT / 'evidence/terrain-s9-20260929'
SHOTS = OUT / 'screenshots'
tw2.SHOTS = SHOTS
SEED = 9209
PARTIAL = {}

# (label, zone, level, poses)
LEVELS = [(f'hp{n}', 'high-peak', n, ['cave', 'stairs'] if n <= 4 else ['wall', 'stairs']) for n in range(1, 11)] + \
    [('hp11', 'high-peak', 11, ['sanctum'])]
TOGGLE = {('hp2', 'cave'), ('hp7', 'wall'), ('hp11', 'sanctum')}
REGRESS = [('dreadfell1', 'dreadfell', 1), ('derth', 'town-derth', 1), ('telmur1', 'telmur', 1)]
S9_FILES = ['overload/mod/class/CheckerTerrain.lua', 'superload/mod/class/Grid.lua']


def summarize(frame, data):
    """Median 40% centre crop per cell, per blocking family."""
    im = Image.open(SHOTS / frame).convert('L')
    s = data['tile']

    def cell(sx, sy):
        return ImageStat.Stat(im.crop((int(sx + s * .3), int(sy + s * .3), int(sx + s * .7), int(sy + s * .7)))).mean[0]

    by = {}
    for p in data['pairs']:
        f, w = p['floor'], p['wall']
        by.setdefault(f[4] + '/' + w[4], []).append((cell(f[2], f[3]), cell(w[2], w[3])))
    out = {}
    for key, rows in sorted(by.items()):
        fl = statistics.median(r[0] for r in rows)
        wl = statistics.median(r[1] for r in rows)
        out[key] = {'pairs': len(rows), 'floor': round(fl, 1), 'wall': round(wl, 1),
                    'gap': round((fl - wl) / fl, 4) if fl else None}
    return out


def run(phase, only=None, shots=True, regression=True, with_regression=False):
    f = Fixture()
    SHOTS.mkdir(parents=True, exist_ok=True)
    plan = json.loads((SESSION / 'launch-plan.json').read_text())
    assert plan['fixture'] and plan['shaders'] and plan['terrain'] == 'refined'
    teaa = plan.get('teaa', {}).get('checker-revised')
    assert teaa, 'both phases run a packaged TEAA'
    with zipfile.ZipFile(teaa) as z:
        names = set(z.namelist())
        assert not any(n.startswith('tests/') for n in names)
        if phase == 'after':
            for rel in S9_FILES:
                assert z.read(rel) == (ROOT / rel).read_bytes(), rel

    def dump(code, name):
        f.lua(f"ms.dump('/{name}',{code})")
        return read(name)

    def size(tile, x, y):
        f.lua(f"game:setResolution('1920x1080 Windowed',true);config.settings.tome.gfx.size='{tile}x{tile}';"
              f"game:setupDisplayMode(false)")
        return dump(f'tw.view({x},{y})', 's9-view.json')

    def shot(tag):
        name = f's9-{tag}'
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
        if pairs:
            fr['lit'] = summarize(Path(fr['file']).name, dump('tw.pairs()', 's9-pairs.json'))
        return fr

    def census():
        c = dump("game.checker_mode=='refined' and tc.census() or {skipped=tostring(game.checker_mode)}", 's9-census.json')
        return {k: c.get(k) for k in ('total', 'converted', 'native', 'empty', 'converted_stone', 'converted_forest',
                                      'groups', 'events', 'aura', 'skipped', 'variant')}

    result = PARTIAL
    result.update({'phase': phase, 'seed': SEED, 'levels': {}})
    try:
        f.lua("assert(config.settings.cheat and config.settings.disable_all_connectivity and not profile.auth);"
              "assert(core.shader.active(4));tw=dofile('/data-checker-fixture/monster-live_s9_scene.lua');ms=tw.ms;ms.setup();"
              "tc=dofile('/data-checker-fixture/monster-live_terrain_census.lua');tc.setup();"
              "config.settings.tome.weather_effects=false")
        for label, zone, level, poses in LEVELS:
            if only and label not in only:
                continue
            row = {'zone': zone, 'level': level, 'screenshots': [], 'poses': {}}
            result['levels'][label] = row
            f.lua(f'rng.seed({SEED + level})')
            row['enter'] = dump(f"ms.enter('{zone}',{level})", 's9-enter.json')
            f.lua('ms.caveClearDialogs()')
            row['quiet'] = dump('tw.quiet()', 's9-quiet.json')
            row['rules_before'] = dump('tw.rules()', 's9-rules.json')
            f.lua(f"tw.keepRows={'true' if label == 'hp11' else 'false'}")
            row['rules_norm'] = dump('tw.rulesNorm()', 's9-rules-norm.json')
            f.lua('tw.keepRows=false')
            row['hp_natural'] = dump('tw.hp()', 's9-hp.json')
            for kind in poses:
                pick = dump(f"tw.pick('{kind}')", 's9-pick.json')
                if not pick.get('found'):
                    row['poses'][kind] = pick
                    continue
                cx, cy = pick['x'], pick['y']
                row['poses'][kind] = dict(pick, pose=dump(f"tw.poseAt({cx},{cy},{cx},{cy},'{kind}')", 's9-pose.json'))
                if not shots:
                    continue
                tiles = (48, 64) if phase == 'after' else (64,)
                for tile in tiles:
                    row['screenshots'].append(photo(tile, f'{label}-{kind}', cx, cy, pairs=tile == 64))
                if phase == 'after' and (label, kind) in TOGGLE:
                    dump('tw.pauseParticles(true)', 's9-pause.json')
                    dump('tw.clearLog()', 's9-log.json')
                    before = photo(64, f'{label}-{kind}-toggle-refined', cx, cy)
                    rb = dump('tw.rules()', 's9-rules-t0.json')
                    f.lua("ms.setMode('vanilla')")
                    native = photo(64, f'{label}-{kind}-toggle-native', cx, cy)
                    rn = dump('tw.rules()', 's9-rules-t1.json')
                    hn = dump('tw.hp()', 's9-hp-native.json')
                    f.lua("ms.setMode('refined')")
                    after = photo(64, f'{label}-{kind}-toggle-restored', cx, cy)
                    ra = dump('tw.rules()', 's9-rules-t2.json')
                    dump('tw.pauseParticles(false)', 's9-pause.json')
                    row.setdefault('toggle', {})[kind] = {
                        'refined': before, 'native': native, 'restored': after, 'native_owner': hn['owner'],
                        'restored_vs_refined': tw2.diff(before, after), 'native_vs_refined': tw2.diff(before, native),
                        'rules': [rb, rn, ra], 'rules_equal': rb == rn == ra}
                    row['screenshots'] += [before, native, after]
            row['hp_after_poses'] = dump('tw.hp()', 's9-hp.json')
            row['natives'] = dump('tw.natives()', 's9-natives.json')
            row['census_forced'] = census()
            row['rules_after'] = dump('tw.rules()', 's9-rules-after.json')
            assert row['rules_before'] == row['rules_after'], (label, row['rules_before'], row['rules_after'])
        if regression and (not only or with_regression):
            reg = result['regression'] = {}
            for label, zone, level in REGRESS:
                r = reg[label] = {'zone': zone, 'level': level, 'screenshots': []}
                f.lua(f'rng.seed({SEED})')
                r['enter'] = dump(f"ms.enter('{zone}',{level})", 's9-enter.json')
                f.lua('ms.caveClearDialogs()')
                r['quiet'] = dump('tw.quiet()', 's9-quiet.json')
                px, py = r['enter']['player_x'], r['enter']['player_y']
                r['pose'] = dump(f"tw.poseAt({px},{py},{px},{py},'start')", 's9-pose.json')
                if shots:
                    dump('tw.pauseParticles(true)', 's9-pause.json')
                    dump('tw.clearLog()', 's9-log.json')
                    r['screenshots'].append(photo(64, f'{label}-start', px, py))
                    dump('tw.pauseParticles(false)', 's9-pause.json')
                r['rules'] = dump('tw.rules()', 's9-rules.json')
                f.lua(f"tw.keepRows={'true' if label == 'derth' else 'false'}")
                r['rules_norm'] = dump('tw.rulesNorm()', 's9-rules-norm.json')
                f.lua('tw.keepRows=false')
                r['census_forced'] = census()
        return result
    finally:
        (OUT / (f'validation-{phase}' + (('-' + '-'.join(only))[:80] if only else '') + '.txt')).write_text(
            (''.join(f.transcript) + f.new_log()).rstrip() + '\n')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('phase', choices=('after', 'before', 'survey', 'survey-before'))
    p.add_argument('--teaa', required=True, help='before: HEAD TEAA; after/survey: HEAD plus the S9 files')
    p.add_argument('--only', nargs='*')
    p.add_argument('--no-regression', action='store_true')
    p.add_argument('--with-regression', action='store_true', help='also run the regression levels with --only')
    a = p.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / 'scenes.json'
    survey = json.loads(path.read_text()) if path.exists() else {}
    meta = launch(a.teaa)
    try:
        phase = {'survey': 'after', 'survey-before': 'before'}.get(a.phase, a.phase)
        try:
            result = run(phase, only=a.only, shots=not a.phase.startswith('survey'), regression=not a.no_regression,
                         with_regression=a.with_regression)
        except Exception as e:
            # Keep what was measured; the failing level is recorded.
            result = PARTIAL
            result['error'] = repr(e)[:4000]
        result['launch_plan'] = json.loads((SESSION / 'launch-plan.json').read_text())
        key = a.phase
        if a.only and key in survey and 'levels' in survey[key]:
            prev = survey[key]
            prev.setdefault('reruns', []).append({'only': a.only, 'launch_plan': result['launch_plan'],
                                                  'error': result.get('error')})
            prev['levels'].update(result['levels'])
            if 'regression' in result:
                prev['regression_rerun'] = result['regression']
        else:
            survey[key] = result
        path.write_text(json.dumps(survey, ensure_ascii=False, indent=1) + '\n')
        print('ERROR ' + result['error'] if result.get('error') else 'PASS', a.phase, flush=True)
    finally:
        stop_started(meta)
        print('STOP', a.phase, flush=True)


if __name__ == '__main__':
    main()
