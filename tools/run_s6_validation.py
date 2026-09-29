#!/usr/bin/env python3
"""S6 live check in the isolated fixture: Eruan L1-3 (sand, palms, deep
ocean, the L3 static map with the Charred Scar farportal) and Gorbat Pride
L1-3 (MapScript: stone, sand, mountains, deep water, bamboo roosts).

One cold start per run. `after` uses the working-tree addon; `before` installs
a TEAA built from HEAD (--before-teaa) to record the pre-S6 natural state at
the same poses. `survey` is `after` without screenshots. Every level is
entered with the fixture's ms.enter (fresh generation); per level: natural
stats and identity probe, palm probe, rule digest, screenshots (48/64 after,
64 before), lit-pixel pairs (after), a native listing, a native-FOV walk and
a forced census. Three levels get a Refined->Native->Refined toggle with the
rule digest taken in each state. Regression: Charred Scar L1, Derth, Irkkk.

The fixture is shared: before each launch the recorded game/Xvfb pids in
session/processes.json are checked via /proc/<pid>/cmdline and the tool waits
while they are alive; it never stops a process it did not start. Screenshots
stay local under evidence/terrain-s6-20260929/screenshots/.
"""
import argparse, json, subprocess, sys, zipfile
from pathlib import Path
from capture_korpul import Fixture, HOME, ROOT, SESSION, digest, png_size
from run_norgos_validation import stop_started
from run_tw2_validation import launch, read, luminance
from run_tw6_validation import pair_values
import run_tw2_validation as tw2
import run_tw6_validation as tw6

OUT = ROOT / 'evidence/terrain-s6-20260929'
SHOTS = OUT / 'screenshots'
tw2.SHOTS = SHOTS
tw6.SHOTS = SHOTS
# (label, zone, level, poses). A pose is (name, cx, cy, sx, sy); None means
# "centre on the player where ms.enter put it".
LEVELS = [
    ('eruan1', 'eruan', 1, [('start', None), ('grove', 'auto')]),
    ('eruan2', 'eruan', 2, [('start', None), ('grove', 'auto')]),
    ('eruan3', 'eruan', 3, [('shore', 15, 31, 19, 32), ('grove', 'auto')]),
    ('gorbat1', 'gorbat-pride', 1, [('start', None), ('roost', 'auto'), ('gate', 'auto')]),
    ('gorbat2', 'gorbat-pride', 2, [('roost', 'auto')]),
    ('gorbat3', 'gorbat-pride', 3, [('roost', 'auto')]),
]
TOGGLE = {('eruan1', 'grove'), ('eruan3', 'shore'), ('gorbat1', 'roost'), ('gorbat2', 'roost')}
S6_FILES = ['overload/mod/class/CheckerTerrain.lua', 'superload/mod/class/Grid.lua', 'superload/mod/class/Game.lua'] + \
    sorted(p.relative_to(ROOT).as_posix() for p in (ROOT / 'data/gfx/refined/eruan').glob('*.png'))
REGRESSION = [('charred', 'charred-scar', 1), ('derth', 'town-derth', 1), ('irkkk', 'town-irkkk', 1)]


def run(phase, only=None, shots=True, regression=True):
    f = Fixture()
    SHOTS.mkdir(parents=True, exist_ok=True)
    plan = json.loads((SESSION / 'launch-plan.json').read_text())
    assert plan['fixture'] and plan['shaders'] and plan['terrain'] == 'refined'
    if phase == 'after':
        # `after` runs HEAD plus exactly the S6 files (--after-teaa), so the
        # concurrent monster batch's unfinished token files are not loaded;
        # the package must carry the working-tree bytes of every S6 file.
        teaa = plan.get('teaa', {}).get('checker-revised')
        assert teaa, 'after needs --after-teaa (HEAD + S6 files)'
        with zipfile.ZipFile(teaa) as z:
            for rel in S6_FILES:
                assert z.read(rel) == (ROOT / rel).read_bytes(), rel

    def dump(code, name):
        f.lua(f"ms.dump('/{name}',{code})")
        return read(name)

    def size(tile, x, y):
        f.lua(f"game:setResolution('1920x1080 Windowed',true);config.settings.tome.gfx.size='{tile}x{tile}';"
              f"game:setupDisplayMode(false)")
        return dump(f'tw.view({x},{y})', 's6-view.json')

    def shot(tag):
        name = f's6-{tag}'
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
        fr['luminance'] = luminance(Path(fr['file']).name, dump('tw.samples()', 's6-samples.json'))
        if pairs:
            data = dump('tw.pairs()', 's6-pairs.json')
            fr['lit_pixels'] = pair_values(Path(fr['file']).name, data)
            fr['water_edge'] = pair_values(Path(fr['file']).name, data, 'water')
        return fr

    result = {'phase': phase, 'levels': {}}
    try:
        f.lua("assert(config.settings.cheat and config.settings.disable_all_connectivity and not profile.auth);"
              "assert(core.shader.active(4));tw=dofile('/data-checker-fixture/monster-live_s6_scene.lua');ms=tw.ms;ms.setup();"
              "tc=dofile('/data-checker-fixture/monster-live_terrain_census.lua');tc.setup();"
              "config.settings.tome.weather_effects=false")
        for label, zone, level, poses in LEVELS:
            if only and label not in only:
                continue
            row = {'zone': zone, 'level': level, 'screenshots': [], 'poses': {}}
            result['levels'][label] = row
            row['enter'] = dump(f"ms.enter('{zone}',{level})", 's6-enter.json')
            f.lua('ms.caveClearDialogs()')
            row['quiet'] = dump('tw.quiet()', 's6-quiet.json')
            st = dump('tw.stats()', 's6-stats.json')
            row['stats_natural'] = {k: v for k, v in st.items() if k != 'shop_images'}
            row['rules_before'] = dump('tw.rules()', 's6-rules.json')
            row['probe_natural'] = dump('tw.probe()', 's6-probe.json')
            row['kinds_natural'] = dump('tw.tw3()', 's6-kinds.json')
            row['natives_natural'] = dump('tw.natives()', 's6-natives.json')
            row['palms_natural'] = dump('tw.palms()', 's6-palms.json')
            row['shapes'] = dump("tw.shapes('.')", 's6-shapes.json')
            row['palm_dump'] = dump('tw.palmDump(3)', 's6-palmdump.json')
            for pose in poses:
                kind = pose[0]
                if pose[1] is None:
                    px, py = row['enter']['player_x'], row['enter']['player_y']
                    cx, cy, sx, sy = px, py, px, py
                elif pose[1] == 'auto':
                    auto = row.setdefault('auto', {})[kind] = dump(f"tw.autoPose('{kind}')", 's6-auto.json')
                    cx, cy, sx, sy = auto['x'], auto['y'], auto['x'], auto['y']
                else:
                    cx, cy, sx, sy = pose[1:]
                row['poses'][kind] = dump(f"tw.poseAt({cx},{cy},{sx},{sy},'{kind}')", 's6-pose.json')
                if not shots:
                    continue
                for tile in ((48, 64) if phase == 'after' else (64,)):
                    row['screenshots'].append(photo(tile, f'{label}-{kind}', cx, cy, pairs=phase == 'after' and tile == 64))
                if phase == 'after' and (label, kind) in TOGGLE:
                    row.setdefault('particles_paused', {})[kind] = dump('tw.pauseParticles(true)', 's6-pause.json')
                    row.setdefault('log_cleared', {})[kind] = dump('tw.clearLog()', 's6-log.json')
                    before = photo(64, f'{label}-{kind}-toggle-refined', cx, cy)
                    rb = dump('tw.rules()', 's6-rules-t0.json')
                    f.lua("ms.setMode('vanilla')")
                    native = photo(64, f'{label}-{kind}-toggle-native', cx, cy)
                    rn = dump('tw.rules()', 's6-rules-t1.json')
                    row.setdefault('native_probe', {})[kind] = dump('tw.probe()', 's6-probe-native.json')['totals']
                    f.lua("ms.setMode('refined')")
                    after = photo(64, f'{label}-{kind}-toggle-restored', cx, cy)
                    ra = dump('tw.rules()', 's6-rules-t2.json')
                    dump('tw.pauseParticles(false)', 's6-pause.json')
                    row.setdefault('toggle', {})[kind] = {
                        'refined': before, 'native': native, 'restored': after,
                        'restored_vs_refined': tw2.diff(before, after), 'native_vs_refined': tw2.diff(before, native),
                        'rules': [rb, rn, ra], 'rules_equal': rb == rn == ra}
                    row['screenshots'] += [before, native, after]
            row['rules_after'] = dump('tw.rules()', 's6-rules-after.json')
            assert row['rules_before'] == row['rules_after'], (label, row['rules_before'], row['rules_after'])
            # Natural state after a native-FOV walk over every free cell, then
            # the forced census (every stone cell observed as if seen).
            p = row['enter']
            row['walk'] = dump(f"tw.walk({p['player_x']},{p['player_y']})", 's6-walk.json')
            row['probe_walked'] = dump('tw.probe()', 's6-probe-walked.json')['totals']
            row['natives_walked'] = dump('tw.natives()', 's6-natives-walked.json')
            row['census_forced'] = dump("game.checker_mode=='refined' and tc.census() or {skipped=tostring(game.checker_mode)}",
                                        's6-census.json')
        if regression and not only:
            reg = result['regression'] = {}
            for label, zone, level in REGRESSION:
                r = reg[label] = {'zone': zone, 'level': level}
                r['enter'] = dump(f"ms.enter('{zone}',{level})", 's6-enter.json')
                f.lua('ms.caveClearDialogs()')
                r['probe_natural'] = dump('tw.probe()', 's6-probe.json')['totals']
                census = dump("game.checker_mode=='refined' and tc.census() or {skipped=tostring(game.checker_mode)}", 's6-census.json')
                r['census_forced'] = {k: census.get(k) for k in ('total', 'converted', 'native', 'converted_stone', 'converted_forest', 'groups', 'skipped')}
        return result
    finally:
        (OUT / (f'validation-{phase}' + ('-' + '-'.join(only) if only else '') + '.txt')).write_text(
            (''.join(f.transcript) + f.new_log()).rstrip() + '\n')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('phase', choices=('after', 'before', 'survey'))
    p.add_argument('--before-teaa', help='TEAA built from HEAD for the before phase')
    p.add_argument('--after-teaa', help='TEAA built from HEAD plus the S6 files for the after/survey phase')
    p.add_argument('--only', nargs='*')
    p.add_argument('--no-regression', action='store_true')
    a = p.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / 'scenes.json'
    survey = json.loads(path.read_text()) if path.exists() else {}
    if a.phase == 'before':
        assert a.before_teaa, '--before-teaa is required for the before phase'
    meta = launch(a.before_teaa if a.phase == 'before' else a.after_teaa)
    try:
        phase = 'after' if a.phase == 'survey' else a.phase
        result = run(phase, only=a.only, shots=a.phase != 'survey', regression=not a.no_regression)
        result['launch_plan'] = json.loads((SESSION / 'launch-plan.json').read_text())
        if a.only and a.phase in survey:
            # A partial rerun replaces only its own levels in the phase record.
            prev = survey[a.phase]
            prev.setdefault('reruns', []).append({'only': a.only, 'launch_plan': result['launch_plan']})
            prev['levels'].update(result['levels'])
        else:
            survey[a.phase] = result
        path.write_text(json.dumps(survey, ensure_ascii=False, indent=1) + '\n')
        print('PASS', a.phase, flush=True)
    finally:
        stop_started(meta)
        print('STOP', a.phase, flush=True)


if __name__ == '__main__':
    main()
