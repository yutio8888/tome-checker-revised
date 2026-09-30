#!/usr/bin/env python3
"""S17 live check in the isolated fixture: the Solipsist Dreamscape plane
(dreamscape-talent), entered through a real Dreamscape cast (forceUseTalent on
the fixture hero at a sleeping adjacent monster) from Kor'Pul L1 and left
through the native EFF_DREAMSCAPE deactivation, so the direct game.level swap
and the S16 display hook (now listing this plane) are exercised both ways.

`before` (HEAD TEAA) records the plane's id/kind census and native frames plus
the Kor'Pul source frame. `after` (HEAD plus exactly the S17 runtime files,
checked byte-for-byte in the installed TEAA) records the census, 48/64/96 px
frames, grey samples, Refined -> Native -> Refined inside the plane with map
particles paused, weather and the time-varying foreground tint frozen and
actor particles dropped (pixel identity), rule digests in each state, and the
return to Kor'Pul (map viewport vs the frame taken before the cast). Every
level is entered after rng.seed(<fixed>).

Before launching, the recorded game/Xvfb pids in session/processes.json are
checked via /proc/<pid>/cmdline (run_tw2_validation.wait_free); only the
processes this tool started are stopped. Screenshots stay local under
evidence/terrain-s17-20260930/screenshots/.
"""
import argparse, json, subprocess, sys, time, zipfile
from pathlib import Path
from PIL import Image, ImageChops
from capture_korpul import Fixture, HOME, ROOT, SESSION, digest, png_size
from run_norgos_validation import stop_started
from run_tw2_validation import launch, read
import run_tw2_validation as tw2

OUT = ROOT / 'evidence/terrain-s17-20260930'
SHOTS = OUT / 'screenshots'
tw2.SHOTS = SHOTS
SEED = 17017
S17_FILES = ['overload/mod/class/CheckerTerrain.lua', 'superload/mod/class/Grid.lua', 'data/terrain-dream-manifest.lua'] + \
    sorted('data/gfx/refined/dream/' + p.name for p in (ROOT / 'data/gfx/refined/dream').glob('*.png'))
CENTER = (9, 9)


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
        for rel in S17_FILES:
            same = rel in names and z.read(rel) == (ROOT / rel).read_bytes()
            assert same == (phase == 'after'), (rel, phase, same)
            if rel.endswith('.png') and rel in names:
                assert z.getinfo(rel).compress_type == zipfile.ZIP_STORED, rel

    def dump(code, name='s17.json'):
        f.lua(f"ms.dump('/{name}',{code})")
        return read(name)

    def size(tile):
        f.lua(f"game:setResolution('1920x1080 Windowed',true);config.settings.tome.gfx.size='{tile}x{tile}';"
              f"game:setupDisplayMode(false)")

    def shot(tag):
        name = f's17-{tag}'
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
        time.sleep(1.0)
        f.lua('ms.caveClearDialogs()')
        dump('tw.pauseParticles(true)')
        dump('tw.clearLog()')

    result = {'phase': phase, 'seed': SEED, 'teaa': teaa}
    try:
        f.lua("assert(config.settings.cheat and config.settings.disable_all_connectivity and not profile.auth);"
              "assert(core.shader.active(4));tw=dofile('/data-checker-fixture/monster-live_s17_scene.lua');ms=tw.ms;ms.setup();"
              "tc=dofile('/data-checker-fixture/monster-live_terrain_census.lua');tc.setup();"
              "config.settings.tome.weather_effects=false")
        size(64)
        f.lua(f'rng.seed({SEED})')
        src = result['source'] = {'zone': 'ruins-kor-pul', 'level': 1}
        src['enter'] = dump("ms.enter('ruins-kor-pul',1)")
        f.lua('ms.caveClearDialogs()')
        src['quiet'] = dump('tw.quiet()')
        src['learn'] = dump('tw.learnDream()')
        src['target'] = dump('tw.prepareDream()')
        w = src['where'] = dump('tw.where()')
        px, py = w['x'], w['y']
        src['viewport'] = vp = dump('tw.viewport()')
        src['rules'] = dump('tw.rules()')
        settle()
        src['refined'] = view('src-refined', px, py)
        dump('tw.pauseParticles(false)')
        row = result['plane'] = {'zone': 'dreamscape-talent', 'screenshots': []}
        f.lua(f'rng.seed({SEED + 1})')
        row['cast'] = dump('tw.castDream()')
        row['where'] = wait_zone('dreamscape-talent')
        f.lua('ms.caveClearDialogs()')
        row['cells'] = dump('tw.cells()')
        row['census_forced'] = census()
        row['rules_before'] = dump('tw.rules()')
        time.sleep(1.0)
        dump('tw.clearLog()')
        cx, cy = CENTER
        row['look'] = view('dream-look', cx, cy)  # native foreground tint and weather kept
        row['quiet'] = dump('tw.quietDream()')
        row['dropped'] = dump('tw.dropActorParticles()')
        settle()
        for tile in ((48, 64, 96) if phase == 'after' else (64,)):
            size(tile)
            fr = view(f'dream-{tile}', cx, cy)
            samples = dump(f'tw.samples({cx},{cy})')
            fr['gray'] = tw2.luminance(Path(fr['file']).name, samples)
            row['screenshots'].append(fr)
        size(64)
        if phase == 'after':
            a = view('dream-toggle-refined', cx, cy)
            ra = dump('tw.rules()')
            f.lua("ms.setMode('vanilla')")
            n = view('dream-toggle-native', cx, cy)
            rn = dump('tw.rules()')
            cn = dump('tw.cells()')
            f.lua("ms.setMode('refined')")
            r2 = view('dream-toggle-restored', cx, cy)
            rb = dump('tw.rules()')
            row['toggle'] = {'refined': a, 'native': n, 'restored': r2, 'rules_equal': ra == rn == rb,
                             'rules': [ra, rn, rb], 'restored_vs_refined': tw2.diff(a, r2),
                             'native_vs_refined': tw2.diff(a, n), 'cells_native': cn,
                             'rules_equal_entry': ra == row['rules_before']}
        row['rules_after'] = dump('tw.rules()')
        row['leave'] = dump('tw.leaveDream()')
        row['back'] = wait_zone('ruins-kor-pul')
        dump('tw.resetDreamCooldown()')
        settle()
        row['source_rules'] = dump('tw.rules()')
        row['source_rules_equal'] = row['source_rules'] == src['rules']
        b = view('src-after-dream', px, py)
        row['return'] = {'frame': b, 'vs_source_refined': tw2.diff(src['refined'], b),
                         'map_vs_source_refined': region_diff(src['refined'], b, vp)}
        if phase == 'after':
            f.lua("ms.setMode('vanilla')")
            row['return']['source_native'] = view('src-after-dream-native', px, py)
            f.lua("ms.setMode('refined')")
            c = view('src-after-dream-refined2', px, py)
            row['return']['map_refined2_vs_source_refined'] = region_diff(src['refined'], c, vp)
        dump('tw.pauseParticles(false)')
        return result
    except Exception as e:
        result['error'] = repr(e)[:4000]
        return result
    finally:
        (OUT / f'validation-{phase}.txt').write_text((''.join(f.transcript) + f.new_log()).rstrip() + '\n')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('phase', choices=('after', 'before'))
    p.add_argument('--teaa', required=True, help='before: HEAD TEAA; after: HEAD plus the S17 files')
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
