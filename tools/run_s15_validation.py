#!/usr/bin/env python3
"""S15 live check in the isolated fixture: tutorial L1 (forest) and dreams L1
(jungle maze), plus a native census of the other mode / tutorial / class-plane
zones.

`before` (HEAD TEAA) records the forced census and 64 px windows; `after`
(HEAD plus exactly the S15 runtime files, checked byte-for-byte in the
installed TEAA) records the census, 48/64 px windows, Refined -> Native ->
Refined with map particles paused (pixel identity) and rule digests in each
state, a Derth regression frame, and a census-only pass over the zones S15
leaves native. Every level is entered after rng.seed(<fixed>).

Before launching, the recorded game/Xvfb pids in session/processes.json are
checked via /proc/<pid>/cmdline (run_tw2_validation.wait_free); only the
processes this tool started are stopped. Screenshots stay local under
evidence/terrain-s15-20260930/screenshots/.
"""
import argparse, json, subprocess, sys, zipfile
from pathlib import Path
from PIL import Image, ImageStat
from capture_korpul import Fixture, HOME, ROOT, SESSION, digest, png_size
from run_norgos_validation import stop_started
from run_tw2_validation import launch, read
import run_tw2_validation as tw2

OUT = ROOT / 'evidence/terrain-s15-20260930'
SHOTS = OUT / 'screenshots'
tw2.SHOTS = SHOTS
SEED = 15015
S15_FILES = ['overload/mod/class/CheckerTerrain.lua', 'superload/mod/class/Grid.lua']
# (label, zone, level, [(window tag, picker lua expression or 'player')])
LEVELS = [('tut1', 'tutorial', 1, [('start', 'player'), ('lake', "tw.pick('^GRASS','^DEEP_WATER',30,34,49,46)")]),
          ('dream1', 'dreams', 1, [('start', 'player'), ('hole', "tw.pick('^DREAM_MOUSE_HOLE',nil)"),
                                   ('exit', "tw.pick('^DREAM_END$',nil)")])]
# Census only: dreams L2 (native by design) and the zones S15 leaves native.
CENSUS = [('dream2', 'dreams', 2), ('tutstats1', 'tutorial-combat-stats', 1), ('arena1', 'arena', 1),
          ('infinite1', 'infinite-dungeon', 1), ('demonspell', 'demon-plane-spell', 1),
          ('dreamscape', 'dreamscape-talent', 1), ('reprieve', 'temporal-reprieve-talent', 1),
          ('eidolon', 'eidolon-plane', 1), ('stellar', 'stellar-system-shandral', 1)]


def gray(frame, cell):
    s = cell['tile']
    im = Image.open(SHOTS / Path(frame).name).convert('L').crop(
        (int(cell['sx'] + s * .2), int(cell['sy'] + s * .2), int(cell['sx'] + s * .8), int(cell['sy'] + s * .8)))
    return round(ImageStat.Stat(im).mean[0], 1)


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
        for rel in S15_FILES:
            same = z.read(rel) == (ROOT / rel).read_bytes()
            assert same == (phase == 'after'), (rel, phase, same)

    def dump(code, name='s15.json'):
        f.lua(f"ms.dump('/{name}',{code})")
        return read(name)

    def size(tile):
        f.lua(f"game:setResolution('1920x1080 Windowed',true);config.settings.tome.gfx.size='{tile}x{tile}';"
              f"game:setupDisplayMode(false)")

    def shot(tag):
        name = f's15-{tag}'
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
        dump(f'tw.view({x},{y})')
        return shot(f'{phase}-{tag}')

    def census():
        # Unsupported zones run with checker_mode 'vanilla' (nothing converted);
        # the census is forced there so every cell is counted as native.
        c = dump("(function() local o=game.checker_mode;game.checker_mode='refined';local ok,c=pcall(tc.census);"
                 "game.checker_mode=o;assert(ok,c);c.mode=o;return c end)()")
        return {k: c.get(k) for k in ('total', 'converted', 'native', 'empty', 'converted_stone', 'converted_forest',
                                      'groups', 'mode', 'variant')}

    result = {'phase': phase, 'seed': SEED, 'teaa': teaa, 'levels': {}, 'census_levels': {}}
    try:
        f.lua("assert(config.settings.cheat and config.settings.disable_all_connectivity and not profile.auth);"
              "assert(core.shader.active(4));tw=dofile('/data-checker-fixture/monster-live_s15_scene.lua');ms=tw.ms;ms.setup();"
              "tc=dofile('/data-checker-fixture/monster-live_terrain_census.lua');tc.setup();"
              "config.settings.tome.weather_effects=false")
        size(64)
        for i, (label, zone, level, windows) in enumerate(LEVELS):
            row = result['levels'][label] = {'zone': zone, 'level': level, 'screenshots': []}
            f.lua(f'rng.seed({SEED + i})')
            row['enter'] = dump(f"ms.enter('{zone}',{level})" if zone != 'dreams' else f"tw.enterQuiet('{zone}',{level})")
            f.lua('ms.caveClearDialogs()')
            row['player'] = dump('tw.player()')
            row['quiet'] = dump('tw.quiet()')
            row['rules_before'] = dump('tw.rules()')
            row['census_forced'] = census()
            row['cells'] = dump('tw.s15cells()')
            row['windows'] = {}
            start = row['player']
            for wtag, pick in windows:
                w = start if pick == 'player' else dump(pick)
                if not w.get('x'):
                    row['windows'][wtag] = {'missing': pick}
                    continue
                wx, wy = w['x'], w['y']
                win = row['windows'][wtag] = {'window': {'x': wx, 'y': wy}}
                if pick != 'player':
                    # Stand two cells south (or at the start) looking at the cell.
                    win['pose'] = dump(f"tw.placePlayer({wx},{wy + 2},{wx},{wy})")
                    f.lua('ms.caveClearDialogs()')
                dump('tw.pauseParticles(true)')
                dump('tw.clearLog()')
                for tile in ((48, 64) if phase == 'after' else (64,)):
                    size(tile)
                    fr = view(f'{label}-{wtag}-{tile}', wx, wy)
                    fr['samples'] = dump(f'tw.graySamples({wx},{wy})')
                    for s in fr['samples'].get('cells', []):
                        s['gray'] = gray(fr['file'], s)
                    row['screenshots'].append(fr)
                size(64)
                if phase == 'after':
                    a = view(f'{label}-{wtag}-toggle-refined', wx, wy)
                    ra = dump('tw.rules()')
                    ca = dump('tw.s15cells()')
                    f.lua("ms.setMode('vanilla')")
                    n = view(f'{label}-{wtag}-toggle-native', wx, wy)
                    rn = dump('tw.rules()')
                    cn = dump('tw.s15cells()')
                    f.lua("ms.setMode('refined')")
                    r2 = view(f'{label}-{wtag}-toggle-restored', wx, wy)
                    rb = dump('tw.rules()')
                    win['toggle'] = {'refined': a, 'native': n, 'restored': r2, 'rules_equal': ra == rn == rb,
                                     'rules': [ra, rn, rb], 'restored_vs_refined': tw2.diff(a, r2),
                                     'native_vs_refined': tw2.diff(a, n), 'board_native': cn}
                dump('tw.pauseParticles(false)')
            row['rules_after'] = dump('tw.rules()')
        reg = result['regression'] = {'zone': 'town-derth', 'level': 1}
        f.lua(f'rng.seed({SEED})')
        reg['enter'] = dump("ms.enter('town-derth',1)")
        f.lua('ms.caveClearDialogs()')
        reg['quiet'] = dump('tw.quiet()')
        px, py = reg['enter']['player_x'], reg['enter']['player_y']
        reg['pose'] = dump(f"tw.poseAt({px},{py},{px},{py},'start')")
        dump('tw.pauseParticles(true)')
        dump('tw.clearLog()')
        reg['frame'] = view('derth-start', px, py)
        dump('tw.pauseParticles(false)')
        reg['census_forced'] = census()
        for i, (label, zone, level) in enumerate(CENSUS):
            if phase != 'after' and label != 'dream2':
                continue
            row = result['census_levels'][label] = {'zone': zone, 'level': level}
            f.lua(f'rng.seed({SEED + 100 + i})')
            try:
                row['enter'] = dump(f"tw.enterQuiet('{zone}',{level})")
                f.lua('ms.caveClearDialogs()')
                row['census_forced'] = census()
                row['cells'] = dump('tw.s15cells()')
            except Exception as e:  # recorded, not fatal
                row['error'] = repr(e)[:2000]
        return result
    except Exception as e:
        result['error'] = repr(e)[:4000]
        return result
    finally:
        (OUT / f'validation-{phase}.txt').write_text((''.join(f.transcript) + f.new_log()).rstrip() + '\n')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('phase', choices=('after', 'before'))
    p.add_argument('--teaa', required=True, help='before: HEAD TEAA; after: HEAD plus the S15 files')
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
