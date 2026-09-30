#!/usr/bin/env python3
"""S16 live check in the isolated fixture: the Fearscape spell plane
(demon-plane-spell) and Temporal Reprieve (temporal-reprieve-talent), entered
and left through the real talents (forceUseTalent on the fixture hero) from
Kor'Pul L1, so the direct game.level swap and its display hook are exercised.

`before` (HEAD TEAA) records each plane's id/kind census and 64 px frames
(native) plus the Kor'Pul source frame. `after` (HEAD plus exactly the S16
runtime files, checked byte-for-byte in the installed TEAA) records the
census, 48/64 px frames, Refined -> Native -> Refined inside each plane with
map particles paused and actor particles dropped (pixel identity) and rule
digests in each state, and the return to Kor'Pul: after the Fearscape the
source frame must equal the one taken before the cast; after switching to
Native inside the Reprieve, the returned source must equal Kor'Pul's own
Native frame, and switching back to Refined must equal the first frame.
Every level is entered after rng.seed(<fixed>).

Before launching, the recorded game/Xvfb pids in session/processes.json are
checked via /proc/<pid>/cmdline (run_tw2_validation.wait_free); only the
processes this tool started are stopped. Screenshots stay local under
evidence/terrain-s16-20260930/screenshots/.
"""
import argparse, json, subprocess, sys, time, zipfile
from pathlib import Path
from PIL import Image, ImageChops
from capture_korpul import Fixture, HOME, ROOT, SESSION, digest, png_size
from run_norgos_validation import stop_started
from run_tw2_validation import launch, read
import run_tw2_validation as tw2

OUT = ROOT / 'evidence/terrain-s16-20260930'
SHOTS = OUT / 'screenshots'
tw2.SHOTS = SHOTS
SEED = 16016
S16_FILES = ['overload/mod/class/CheckerTerrain.lua', 'superload/mod/class/Grid.lua', 'superload/mod/class/Game.lua']
PLANES = [('fear', 'demon-plane-spell', 'tw.castFearscape()', 'tw.leaveFearscape()', (6, 6)),
          ('reprieve', 'temporal-reprieve-talent', 'tw.castReprieve()', 'tw.leaveReprieve()', (5, 6))]


def region_diff(a, b, vp):
    box = (vp['x'], vp['y'], vp['x'] + vp['w'], vp['y'] + vp['h'])
    d = ImageChops.difference(Image.open(SHOTS / Path(a['file']).name).convert('RGB').crop(box),
                              Image.open(SHOTS / Path(b['file']).name).convert('RGB').crop(box)).convert('L')
    hist = d.histogram()
    return {'box': box, 'identical': hist[0] == sum(hist), 'differing_pixels': sum(hist) - hist[0]}


def run(phase):
    f = Fixture()
    SHOTS.mkdir(parents=True, exist_ok=True)
    plan = json.loads((SESSION / 'launch-plan.json').read_text())
    assert plan['fixture'] and plan['shaders'] and plan['terrain'] == 'refined'
    teaa = plan.get('teaa', {}).get('checker-revised')
    assert teaa, 'every phase runs a packaged TEAA'
    with zipfile.ZipFile(teaa) as z:
        names = set(z.namelist())
        assert not any(n.startswith('tests/') for n in names)
        for rel in S16_FILES:
            same = z.read(rel) == (ROOT / rel).read_bytes()
            assert same == (phase == 'after'), (rel, phase, same)

    def dump(code, name='s16.json'):
        f.lua(f"ms.dump('/{name}',{code})")
        return read(name)

    def size(tile):
        f.lua(f"game:setResolution('1920x1080 Windowed',true);config.settings.tome.gfx.size='{tile}x{tile}';"
              f"game:setupDisplayMode(false)")

    def shot(tag):
        name = f's16-{tag}'
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

    def view(tag, x, y):
        v = dump(f'tw.view({x},{y})')
        fr = shot(f'{phase}-{tag}')
        fr['view'] = v
        return fr

    def census():
        c = dump("(function() local o=game.checker_mode;game.checker_mode='refined';local ok,c=pcall(tc.census);"
                 "game.checker_mode=o;if not ok then return {error=tostring(c)} end;c.mode=o;return c end)()")
        return {k: c.get(k) for k in ('total', 'converted', 'native', 'empty', 'converted_stone', 'converted_forest',
                                      'mode', 'variant', 'error')}

    def wait_zone(zone):
        for _ in range(40):
            w = dump('tw.where()')
            if w['zone'] == zone:
                return w
            time.sleep(.25)
        raise RuntimeError(f'zone did not become {zone}: {w}')

    def settle():
        # Let the arrival/return teleport particles be created, then pause.
        time.sleep(1.0)
        f.lua('ms.caveClearDialogs()')
        dump('tw.pauseParticles(true)')
        dump('tw.clearLog()')

    result = {'phase': phase, 'seed': SEED, 'teaa': teaa, 'planes': {}}
    try:
        f.lua("assert(config.settings.cheat and config.settings.disable_all_connectivity and not profile.auth);"
              "assert(core.shader.active(4));tw=dofile('/data-checker-fixture/monster-live_s16_scene.lua');ms=tw.ms;ms.setup();"
              "tc=dofile('/data-checker-fixture/monster-live_terrain_census.lua');tc.setup();"
              "config.settings.tome.weather_effects=false")
        size(64)
        f.lua(f'rng.seed({SEED})')
        src = result['source'] = {'zone': 'ruins-kor-pul', 'level': 1}
        src['enter'] = dump("ms.enter('ruins-kor-pul',1)")
        f.lua('ms.caveClearDialogs()')
        src['quiet'] = dump('tw.quiet()')
        src['learn'] = dump('tw.learn()')
        src['target'] = dump('tw.prepareFearscape()')
        w = src['where'] = dump('tw.where()')
        px, py = w['x'], w['y']
        src['viewport'] = vp = dump('tw.viewport()')
        src['rules'] = dump('tw.rules()')
        settle()
        src['refined'] = view('src-refined', px, py)
        if phase == 'after':
            f.lua("ms.setMode('vanilla')")
            src['native'] = view('src-native', px, py)
            f.lua("ms.setMode('refined')")
            src['refined2'] = view('src-refined2', px, py)
            src['refined_repeat'] = tw2.diff(src['refined'], src['refined2'])
        dump('tw.pauseParticles(false)')
        for i, (label, zone, cast, leave, (cx, cy)) in enumerate(PLANES):
            row = result['planes'][label] = {'zone': zone, 'screenshots': []}
            f.lua(f'rng.seed({SEED + 1 + i})')
            row['cast'] = dump(cast)
            row['where'] = wait_zone(zone)
            f.lua('ms.caveClearDialogs()')
            row['cells'] = dump('tw.cells()')
            row['census_forced'] = census()
            row['rules_before'] = dump('tw.rules()')
            time.sleep(1.0)
            dump('tw.clearLog()')
            row['look'] = view(f'{label}-look', cx, cy)  # native background/starfield kept
            row['quiet'] = dump('tw.quiet()')
            row['dropped'] = dump('tw.dropActorParticles()')
            settle()
            for tile in ((48, 64) if phase == 'after' else (64,)):
                size(tile)
                row['screenshots'].append(view(f'{label}-{tile}', cx, cy))
            size(64)
            if phase == 'after':
                a = view(f'{label}-toggle-refined', cx, cy)
                ra = dump('tw.rules()')
                f.lua("ms.setMode('vanilla')")
                n = view(f'{label}-toggle-native', cx, cy)
                rn = dump('tw.rules()')
                cn = dump('tw.cells()')
                f.lua("ms.setMode('refined')")
                r2 = view(f'{label}-toggle-restored', cx, cy)
                rb = dump('tw.rules()')
                row['toggle'] = {'refined': a, 'native': n, 'restored': r2, 'rules_equal': ra == rn == rb,
                                 'rules': [ra, rn, rb], 'restored_vs_refined': tw2.diff(a, r2),
                                 'native_vs_refined': tw2.diff(a, n), 'cells_native': cn}
                if label == 'reprieve':
                    f.lua("ms.setMode('vanilla')")
                    row['left_in'] = 'vanilla'
            row['rules_after'] = dump('tw.rules()')
            row['leave'] = dump(leave)
            row['back'] = wait_zone('ruins-kor-pul')
            dump('tw.resetCooldowns()')
            settle()
            row['source_rules'] = dump('tw.rules()')
            if phase == 'after':
                if label == 'fear':
                    b = view('src-after-fear', px, py)
                    row['return'] = {'frame': b, 'vs_source_refined': tw2.diff(src['refined'], b),
                                     'map_vs_source_refined': region_diff(src['refined'], b, vp)}
                else:
                    c = view('src-after-reprieve-native', px, py)
                    f.lua("ms.setMode('refined')")
                    d = view('src-after-reprieve-refined', px, py)
                    row['return'] = {'native_frame': c, 'refined_frame': d,
                                     'native_vs_source_native': tw2.diff(src['native'], c),
                                     'map_native_vs_source_native': region_diff(src['native'], c, vp),
                                     'refined_vs_source_refined': tw2.diff(src['refined'], d),
                                     'map_refined_vs_source_refined': region_diff(src['refined'], d, vp)}
            else:
                row['return'] = {'frame': view(f'src-after-{label}', px, py)}
            dump('tw.pauseParticles(false)')
        result['source_rules_final'] = dump('tw.rules()')
        return result
    except Exception as e:
        result['error'] = repr(e)[:4000]
        return result
    finally:
        (OUT / f'validation-{phase}.txt').write_text((''.join(f.transcript) + f.new_log()).rstrip() + '\n')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('phase', choices=('after', 'before'))
    p.add_argument('--teaa', required=True, help='before: HEAD TEAA; after: HEAD plus the S16 files')
    a = p.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / 'scenes.json'
    scenes = json.loads(path.read_text()) if path.exists() else {}
    meta = launch(a.teaa)
    try:
        result = run(a.phase)
        result['launch_plan'] = json.loads((SESSION / 'launch-plan.json').read_text())
        scenes[a.phase] = result
        path.write_text(json.dumps(scenes, ensure_ascii=False, indent=1) + '\n')
        print('ERROR ' + result['error'] if result.get('error') else 'PASS', a.phase, flush=True)
    finally:
        stop_started(meta)
        print('STOP', a.phase, flush=True)


if __name__ == '__main__':
    main()
