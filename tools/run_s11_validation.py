#!/usr/bin/env python3
"""S11 live check in the isolated fixture: levers, lever doors and Vor's candles.

Levels: Tannen's Tower L1 (basic.lua levers + lever doors, stone adapter),
Gorbat Pride L1-3 (GENERIC_LEVER_SAND + ROCK_LEVER_DOOR), Vor Pride L1-3
(gothic levers/lever door, CANDLE1-3), Rak'shor Pride L1 (bone levers/lever
doors), Derth's arena (lever-door gates) and the Ruined Dungeon (sealed lever
door). One cold start per run. `before` installs a TEAA built from HEAD;
`after` installs HEAD plus exactly the S11 files (checked byte-for-byte, so the
concurrent monster batch's unfinished files are never loaded). Every level is
entered with ms.enter after rng.seed(<fixed>).

after, per lever level: every lever is pulled for real (the player bumps it)
with 64px frames of the lever and its linked doors before/after each pull,
recentred without a forced repaint pass; the first lever is pulled back at the
end. Vor's first pull runs with the S11 lever/door repaint probes stubbed out
(fixture only) to record the native behaviour, then the probe is restored.
Refined->Native->Refined toggles with the rule digest in each state; the Vor
candle particle check; a forced census per level; regression Derth and
Grushnak L1.

The fixture is shared: before each launch the recorded game/Xvfb pids in
session/processes.json are checked via /proc/<pid>/cmdline and the tool waits
while they are alive; it never stops a process it did not start. Screenshots
stay local under evidence/terrain-s11-20260930/screenshots/.
"""
import argparse, json, subprocess, sys, zipfile
from pathlib import Path
from PIL import Image, ImageChops, ImageStat
from capture_korpul import Fixture, HOME, ROOT, SESSION, digest, png_size
from run_norgos_validation import stop_started
from run_tw2_validation import launch, read
import run_tw2_validation as tw2

OUT = ROOT / 'evidence/terrain-s11-20260930'
SHOTS = OUT / 'screenshots'
tw2.SHOTS = SHOTS
SEED = 11011
PARTIAL = {}

# (label, zone, level, pulls)
LEVELS = [('tannen1', 'tannen-tower', 1, True),
          ('gorbat1', 'gorbat-pride', 1, True),
          ('gorbat2', 'gorbat-pride', 2, False),
          ('gorbat3', 'gorbat-pride', 3, False),
          ('vor1', 'vor-pride', 1, True),
          ('vor2', 'vor-pride', 2, False),
          ('vor3', 'vor-pride', 3, False),
          ('rakshor1', 'rak-shor-pride', 1, True),
          ('arena', 'arena-unlock', 1, False),
          ('ruined', 'ruined-dungeon', 1, False)]
TOGGLE = {'tannen1', 'gorbat1', 'vor1', 'rakshor1'}
REGRESS = [('derth', 'town-derth', 1), ('grushnak1', 'grushnak-pride', 1)]
S11_FILES = ['overload/mod/class/CheckerTerrain.lua', 'superload/engine/Map.lua']


def crop(frame, cell, pad=1):
    """Cell (plus pad cells) crop of a frame, saved next to it."""
    s = cell['tile']
    im = Image.open(SHOTS / frame)
    box = (int(cell['sx'] - pad * s), int(cell['sy'] - pad * s), int(cell['sx'] + (pad + 1) * s), int(cell['sy'] + (pad + 1) * s))
    name = frame.replace('.png', f"-crop-{cell['x']}-{cell['y']}.png")
    im.crop(box).save(SHOTS / name)
    return 'screenshots/' + name


def cell_diff(a, b, cell):
    s = cell['tile']
    box = (int(cell['sx']), int(cell['sy']), int(cell['sx'] + s), int(cell['sy'] + s))
    da = Image.open(SHOTS / Path(a).name).convert('RGB').crop(box)
    db = Image.open(SHOTS / Path(b).name).convert('RGB').crop(box)
    d = ImageChops.difference(da, db).convert('L')
    hist = d.histogram()
    return {'differing_pixels': sum(hist) - hist[0], 'max': max(i for i, c in enumerate(hist) if c)}


def cell_light(frame, cell):
    """Mean and 99th-percentile luminance of one cell (candle glow check)."""
    s = cell['tile']
    im = Image.open(SHOTS / Path(frame).name).convert('L').crop(
        (int(cell['sx']), int(cell['sy']), int(cell['sx'] + s), int(cell['sy'] + s)))
    hist = im.histogram()
    total, acc, p99 = sum(hist), 0, 0
    for i, c in enumerate(hist):
        acc += c
        if acc >= total * .99:
            p99 = i
            break
    return {'mean': round(ImageStat.Stat(im).mean[0], 1), 'p99': p99}


def run(phase, only=None, shots=True, regression=True):
    f = Fixture()
    SHOTS.mkdir(parents=True, exist_ok=True)
    plan = json.loads((SESSION / 'launch-plan.json').read_text())
    assert plan['fixture'] and plan['shaders'] and plan['terrain'] == 'refined'
    teaa = plan.get('teaa', {}).get('checker-revised')
    assert teaa, 'every phase runs a packaged TEAA'
    with zipfile.ZipFile(teaa) as z:
        names = set(z.namelist())
        assert not any(n.startswith('tests/') for n in names)
        if phase == 'after':
            for rel in S11_FILES:
                assert z.read(rel) == (ROOT / rel).read_bytes(), rel

    def dump(code, name='s11.json'):
        f.lua(f"ms.dump('/{name}',{code})")
        return read(name)

    def size(tile):
        f.lua(f"game:setResolution('1920x1080 Windowed',true);config.settings.tome.gfx.size='{tile}x{tile}';"
              f"game:setupDisplayMode(false)")

    def shot(tag):
        name = f's11-{tag}'
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

    def view(tag, x, y, refresh=False, cells=()):
        # refresh=False: recentre only (a stale display stays stale).
        dump(f'tw.view({x},{y})' if refresh else f'tw.look({x},{y})')
        fr = shot(f'{phase}-{tag}')
        fr['cells'] = {}
        for c in cells:
            sc = dump(f'tw.screen({c[0]},{c[1]})')
            fr['cells'][f'{c[0]},{c[1]}'] = {'screen': sc, 'crop': crop(Path(fr['file']).name, sc)}
        return fr

    def census():
        c = dump("game.checker_mode=='refined' and tc.census() or {skipped=tostring(game.checker_mode)}")
        return {k: c.get(k) for k in ('total', 'converted', 'native', 'empty', 'converted_stone', 'converted_forest',
                                      'groups', 'events', 'aura', 'skipped', 'variant')}

    def toggle(row, tag, x, y, cells):
        dump('tw.pauseParticles(true)')
        dump('tw.candles(false)')
        dump('tw.clearLog()')
        a = view(f'{tag}-toggle-refined', x, y, True, cells)
        ra = dump('tw.rules()')
        f.lua("ms.setMode('vanilla')")
        n = view(f'{tag}-toggle-native', x, y, True, cells)
        rn = dump('tw.rules()')
        f.lua("ms.setMode('refined')")
        b = view(f'{tag}-toggle-restored', x, y, True, cells)
        rb = dump('tw.rules()')
        dump('tw.candles(true)')
        dump('tw.pauseParticles(false)')
        row['toggle'] = {'refined': a, 'native': n, 'restored': b, 'rules_equal': ra == rn == rb, 'rules': [ra, rn, rb],
                         'restored_vs_refined': tw2.diff(a, b), 'native_vs_refined': tw2.diff(a, n)}

    result = PARTIAL
    result.update({'phase': phase, 'seed': SEED, 'levels': {}})
    try:
        f.lua("assert(config.settings.cheat and config.settings.disable_all_connectivity and not profile.auth);"
              "assert(core.shader.active(4));tw=dofile('/data-checker-fixture/monster-live_s11_scene.lua');ms=tw.ms;ms.setup();"
              "tc=dofile('/data-checker-fixture/monster-live_terrain_census.lua');tc.setup();"
              "config.settings.tome.weather_effects=false")
        size(64)
        for i, (label, zone, level, pulls) in enumerate(LEVELS):
            if only and label not in only:
                continue
            row = {'zone': zone, 'level': level, 'screenshots': []}
            result['levels'][label] = row
            f.lua(f'rng.seed({SEED + i})')
            row['enter'] = dump(f"ms.enter('{zone}',{level})")
            f.lua('ms.caveClearDialogs()')
            row['quiet'] = dump('tw.quiet()')
            row['rules_before'] = dump('tw.rules()')
            row['cells_natural'] = dump('tw.s11cells()')
            row['levers'] = dump('tw.levers()')
            if not shots:
                row['layer_sets'] = dump('tw.layerSets()')
            row['census_forced'] = census()
            row['cells_forced'] = dump('tw.s11cells()')
            if shots:
                levers = row['levers']
                doors = sorted({tuple(l) for lv in levers for l in lv['links']})
                cells = row['cells_forced']['cells']
                if not levers:
                    # Sealed doors without a lever (arena gates, Ruined Dungeon).
                    targets = [c for c in cells if c['id'] and 'LEVER' in c['id']] or cells
                    if targets:
                        t = targets[0]
                        dump(f"tw.poseAt({t['x']},{t['y']},{t['x']},{t['y']},'door')")
                        row['screenshots'].append(view(f'{label}-door', t['x'], t['y'], True, [(c['x'], c['y']) for c in targets]))
                        if phase == 'after':
                            row['cells_photo'] = dump('tw.s11cells()')
                else:
                    lx, ly = levers[0]['x'], levers[0]['y']
                    lcells = [(lv['x'], lv['y']) for lv in levers]
                    if doors:
                        # Walk up to the doors first: later door frames show them remembered, out of FOV.
                        dx, dy = doors[0]
                        row['door_pose'] = dump(f"tw.poseAt({dx},{dy},{dx+2},{dy+1},'doors')")
                        row['screenshots'].append(view(f'{label}-doors0', dx, dy, True, doors))
                    dump(f"tw.poseAt({lx},{ly},{lx},{ly+1},'lever')")
                    row['screenshots'].append(view(f'{label}-lever0', lx, ly, True, lcells[:1]))
                    if phase == 'after' and pulls:
                        seq = row['pulls'] = []
                        if label in TOGGLE:
                            toggle(row, label, lx, ly, lcells[:1] + list(doors[:1]))
                        for k, lv in enumerate(levers + levers[:1]):
                            x, y = lv['x'], lv['y']
                            stub = label in ('vor1', 'rakshor1') and k == 0 and 'lever' or \
                                label == 'rakshor1' and k == len(levers) - 1 and 'door' or None
                            dump('tw.clearLog()')
                            if stub:
                                dump('tw.probe(false)')
                            p = dump(f'tw.pull({x},{y})')
                            step = {'k': k, 'lever': [x, y], 'stub': stub, 'pull': p}
                            step['lever_after'] = view(f'{label}-pull{k}-lever', x, y, False, [(x, y)])
                            if doors:
                                step['doors_after'] = view(f'{label}-pull{k}-doors', doors[0][0], doors[0][1], False, doors)
                            if stub:
                                dump('tw.probe(true)')
                                if stub == 'lever':
                                    # The probe is back: the next native updateMap of the cell repaints it.
                                    f.lua(f'game.level.map:updateMap({x},{y})')
                                    step['lever_restored'] = view(f'{label}-pull{k}-lever-probe', x, y, False, [(x, y)])
                                else:
                                    f.lua(f'game:checkerRepairTerrain({doors[0][0]-1},{doors[0][1]-1},{doors[0][0]+1},{doors[0][1]+1});'
                                          f'game.level.map:updateMap({x},{y})')
                                    step['doors_restored'] = view(f'{label}-pull{k}-doors-repair', doors[0][0], doors[0][1], False, doors)
                            step['cells'] = dump('tw.s11cells()')
                            seq.append(step)
                            row['screenshots'] += [step[k2] for k2 in ('lever_after', 'doors_after', 'lever_restored', 'doors_restored') if k2 in step]
                        row['cells_after_pulls'] = dump('tw.s11cells()')
                    if phase == 'after' and label == 'vor1':
                        cand = [c for c in cells if c['id'] and c['id'].startswith('CANDLE')]
                        if cand:
                            c = cand[0]
                            dump(f"tw.poseAt({c['x']},{c['y']},{c['x']},{c['y']+2},'candle')")
                            out = row['candle'] = {'cell': dump(f"tw.cell({c['x']},{c['y']})")}
                            for mode in ('refined', 'vanilla', 'refined'):
                                f.lua(f"ms.setMode('{mode}')")
                                fr = view(f"{label}-candle-{mode}-{len(out)}", c['x'], c['y'], True, [(c['x'], c['y']), (c['x'] + 1, c['y'])])
                                sc = fr['cells'][f"{c['x']},{c['y']}"]['screen']
                                nb = fr['cells'][f"{c['x'] + 1},{c['y']}"]['screen']
                                fr['candle_light'] = cell_light(fr['file'], sc)
                                fr['neighbour_light'] = cell_light(fr['file'], nb)
                                fr['cell'] = dump(f"tw.cell({c['x']},{c['y']})")
                                out[f'{mode}-{len(out)}'] = fr
                                row['screenshots'].append(fr)
            row['rules_after'] = dump('tw.rules()')
            row['cells_end'] = dump('tw.s11cells()')
        if regression and not only:
            reg = result['regression'] = {}
            for label, zone, level in REGRESS:
                r = reg[label] = {'zone': zone, 'level': level, 'screenshots': []}
                f.lua(f'rng.seed({SEED})')
                r['enter'] = dump(f"ms.enter('{zone}',{level})")
                f.lua('ms.caveClearDialogs()')
                r['quiet'] = dump('tw.quiet()')
                px, py = r['enter']['player_x'], r['enter']['player_y']
                r['pose'] = dump(f"tw.poseAt({px},{py},{px},{py},'start')")
                if shots:
                    dump('tw.pauseParticles(true)')
                    dump('tw.clearLog()')
                    r['screenshots'].append(view(f'{label}-start', px, py, True))
                    dump('tw.pauseParticles(false)')
                r['rules'] = dump('tw.rules()')
                r['census_forced'] = census()
        return result
    finally:
        (OUT / (f'validation-{phase}' + (('-' + '-'.join(only))[:80] if only else '') + '.txt')).write_text(
            (''.join(f.transcript) + f.new_log()).rstrip() + '\n')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('phase', choices=('after', 'before', 'survey'))
    p.add_argument('--teaa', required=True, help='before/survey: HEAD TEAA; after: HEAD plus the S11 files')
    p.add_argument('--only', nargs='*')
    p.add_argument('--no-regression', action='store_true')
    a = p.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / 'scenes.json'
    scenes = json.loads(path.read_text()) if path.exists() else {}
    meta = launch(a.teaa)
    try:
        phase = {'survey': 'before'}.get(a.phase, a.phase)
        try:
            result = run(phase, only=a.only, shots=a.phase != 'survey', regression=not a.no_regression)
        except Exception as e:
            result = PARTIAL
            result['error'] = repr(e)[:4000]
        result['launch_plan'] = json.loads((SESSION / 'launch-plan.json').read_text())
        key = a.phase
        if a.only and key in scenes and 'levels' in scenes[key]:
            prev = scenes[key]
            prev.setdefault('reruns', []).append({'only': a.only, 'launch_plan': result['launch_plan'], 'error': result.get('error')})
            prev['levels'].update(result['levels'])
        else:
            scenes[key] = result
        path.write_text(json.dumps(scenes, ensure_ascii=False, indent=1) + '\n')
        print('ERROR ' + result['error'] if result.get('error') else 'PASS', a.phase, flush=True)
    finally:
        stop_started(meta)
        print('STOP', a.phase, flush=True)


if __name__ == '__main__':
    main()
