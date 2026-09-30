#!/usr/bin/env python3
"""S12 live check in the isolated fixture: damaging lava floor (T19) and Vor
Armoury's deep water (T20).

Levels: Vor Armoury L2 (static map: LAVA_FLOOR* and DEEP_WATER, stone
adapter), High Peak L9 as generated and with a forced greater vault
(demon nest / dragon loot / orc hatred: lava.lua LAVA_FLOOR through the vault's
own specialList), Dreadfell L6 with a forced lava greater vault. The forced
vault is a fixture-only generator probe (tests/live_s12_scene.lua
enterForced: the level's greater-vault room list is pinned; the vault file,
its tiles and every rule are native). One cold start per run. `survey` and
`before` install a TEAA built from HEAD; `after` installs HEAD plus exactly the
S12 files (checked byte-for-byte, so the concurrent monster batch's unfinished
files are never loaded). Every level is entered after rng.seed(<fixed>).

Per level: a forced census, a full dump of every lava / water cell (fields,
callbacks with file:line, stamps, owner, S12 kind), the native on_stand call
for the player standing on one hazard cell (fields before/after: the native
callback writes self.x/self.y), 48 and 64 px frames of the densest hazard /
water window with the player standing next to it, grayscale samples, and
Refined->Native->Refined toggles with the rule digest in each state.
Regression: Charred Scar (lava walls), Noxious Caldera and Derth.

The fixture is shared: before each launch the recorded game/Xvfb pids in
session/processes.json are checked via /proc/<pid>/cmdline and the tool waits
while they are alive; it never stops a process it did not start. Screenshots
stay local under evidence/terrain-s12-20260930/screenshots/.
"""
import argparse, json, subprocess, sys, zipfile
from pathlib import Path
from PIL import Image, ImageStat
from capture_korpul import Fixture, HOME, ROOT, SESSION, digest, png_size
from run_norgos_validation import stop_started
from run_tw2_validation import launch, read, wait_free
import run_tw2_validation as tw2

OUT = ROOT / 'evidence/terrain-s12-20260930'
SHOTS = OUT / 'screenshots'
tw2.SHOTS = SHOTS
SEED = 12012
PARTIAL = {}
LAVA = '^LAVA_FLOOR'
WATER = '^DEEP_WATER'

# (label, zone, level, forced greater vaults or None, photo patterns)
LEVELS = [('vor2', 'vor-armoury', 2, None, (LAVA, WATER)),
          ('hp9', 'high-peak', 9, None, (LAVA,)),
          ('hp9v', 'high-peak', 9, ['demon-nest-1', 'demon-nest-2', 'demon-nest-3'], (LAVA,)),
          ('hp7v', 'high-peak', 7, ['dragon-loot', 'orc-hatred'], (LAVA,)),
          ('dread6v', 'dreadfell', 6, ['dragon-loot', 'orc-hatred', 'demon-nest-1'], (LAVA,))]
TOGGLE = {'vor2', 'hp9v', 'dread6v'}
REGRESS = [('scar', 'charred-scar', 1), ('caldera', 'noxious-caldera', 1), ('derth', 'town-derth', 1)]
S12_FILES = ['overload/mod/class/CheckerTerrain.lua', 'data/terrain-hazard-manifest.lua']


def s12_files():
    files = list(S12_FILES)
    files += sorted(str(p.relative_to(ROOT)) for p in (ROOT / 'data/gfx/refined/hazard').glob('*.png'))
    return files


def gray(frame, cell):
    """Mean / p10 / p90 luminance of the centre 60% of one cell."""
    s = cell['tile']
    im = Image.open(SHOTS / Path(frame).name).convert('L').crop(
        (int(cell['sx'] + s * .2), int(cell['sy'] + s * .2), int(cell['sx'] + s * .8), int(cell['sy'] + s * .8)))
    hist = im.histogram()
    total, acc, p10, p90 = sum(hist), 0, None, None
    for i, c in enumerate(hist):
        acc += c
        if p10 is None and acc >= total * .1:
            p10 = i
        if p90 is None and acc >= total * .9:
            p90 = i
    return {'mean': round(ImageStat.Stat(im).mean[0], 1), 'p10': p10, 'p90': p90}


def crop(frame, cell, pad=2):
    s = cell['tile']
    im = Image.open(SHOTS / Path(frame).name)
    box = (int(cell['sx'] - pad * s), int(cell['sy'] - pad * s), int(cell['sx'] + (pad + 1) * s), int(cell['sy'] + (pad + 1) * s))
    name = Path(frame).name.replace('.png', f"-crop-{cell['x']}-{cell['y']}.png")
    im.crop(box).save(SHOTS / name)
    return 'screenshots/' + name


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
            for rel in s12_files():
                assert z.read(rel) == (ROOT / rel).read_bytes(), rel

    def dump(code, name='s12.json'):
        f.lua(f"ms.dump('/{name}',{code})")
        return read(name)

    def size(tile):
        f.lua(f"game:setResolution('1920x1080 Windowed',true);config.settings.tome.gfx.size='{tile}x{tile}';"
              f"game:setupDisplayMode(false)")

    def shot(tag):
        name = f's12-{tag}'
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

    def view(tag, x, y, cells=()):
        dump(f'tw.view({x},{y})')
        fr = shot(f'{phase}-{tag}')
        fr['cells'] = {}
        for c in cells:
            sc = dump(f'tw.screen({c[0]},{c[1]})')
            fr['cells'][f'{c[0]},{c[1]}'] = {'screen': sc, 'gray': gray(fr['file'], sc)}
        return fr

    def census():
        c = dump("game.checker_mode=='refined' and tc.census() or {skipped=tostring(game.checker_mode)}")
        return {k: c.get(k) for k in ('total', 'converted', 'native', 'empty', 'converted_stone', 'converted_forest',
                                      'groups', 'events', 'aura', 'skipped', 'variant')}

    result = PARTIAL
    result.update({'phase': phase, 'seed': SEED, 'levels': {}})
    try:
        f.lua("assert(config.settings.cheat and config.settings.disable_all_connectivity and not profile.auth);"
              "assert(core.shader.active(4));tw=dofile('/data-checker-fixture/monster-live_s12_scene.lua');ms=tw.ms;ms.setup();"
              "tc=dofile('/data-checker-fixture/monster-live_terrain_census.lua');tc.setup();"
              "config.settings.tome.weather_effects=false")
        size(64)
        for i, (label, zone, level, vaults, patterns) in enumerate(LEVELS):
            if only and label not in only:
                continue
            row = {'zone': zone, 'level': level, 'forced_vaults': vaults, 'screenshots': []}
            result['levels'][label] = row
            f.lua(f'rng.seed({SEED + i})')
            if vaults:
                row['enter'] = dump(f"tw.enterForced('{zone}',{level},{json.dumps(vaults).replace('[', '{').replace(']', '}')})")
            else:
                row['enter'] = dump(f"ms.enter('{zone}',{level})")
            f.lua('ms.caveClearDialogs()')
            row['quiet'] = dump('tw.quiet()')
            row['rules_before'] = dump('tw.rules()')
            row['cells_natural'] = dump('tw.s12cells(false)')
            row['census_forced'] = census()
            row['cells_forced'] = dump('tw.s12cells()')
            lava = [c for c in row['cells_forced']['cells'] if str(c['id']).startswith('LAVA_FLOOR')]
            if lava:
                c = lava[0]
                row['stand'] = dump(f"tw.stand({c['x']},{c['y']})")
                row['cell_after_stand_owner'] = dump(f"tw.cell({c['x']},{c['y']})")
            row['windows'] = {}
            for pat in patterns:
                w = dump(f"tw.pickWindow('{pat}')")
                if not w.get('x'):
                    continue
                key = 'lava' if pat == LAVA else 'water'
                b = dump(f"tw.besideHazard('{pat}',{w['x']},{w['y']})")
                row['windows'][key] = {'window': w, 'beside': b}
                if not shots or not b.get('x'):
                    continue
                pose = dump(f"tw.placePlayer({b['x']},{b['y']},{w['x']},{w['y']})")
                row['windows'][key]['pose'] = pose
                dump('tw.pauseParticles(true)')
                dump('tw.clearLog()')
                probe = [(b['x'], b['y']), tuple(b['hazard'])]
                for tile in (48, 64):
                    size(tile)
                    fr = view(f'{label}-{key}-{tile}', w['x'], w['y'], probe)
                    fr['crop'] = crop(fr['file'], fr['cells'][f"{b['hazard'][0]},{b['hazard'][1]}"]['screen'])
                    fr['samples'] = dump(f"tw.graySamples({w['x']},{w['y']})")
                    for s in fr['samples'].get('cells', []):
                        s['gray'] = gray(fr['file'], s)
                    row['screenshots'].append(fr)
                size(64)
                if label in TOGGLE and phase == 'after':
                    a = view(f'{label}-{key}-toggle-refined', w['x'], w['y'])
                    ra = dump('tw.rules()')
                    f.lua("ms.setMode('vanilla')")
                    n = view(f'{label}-{key}-toggle-native', w['x'], w['y'])
                    rn = dump('tw.rules()')
                    f.lua("ms.setMode('refined')")
                    r2 = view(f'{label}-{key}-toggle-restored', w['x'], w['y'])
                    rb = dump('tw.rules()')
                    row.setdefault('toggle', {})[key] = {
                        'refined': a, 'native': n, 'restored': r2, 'rules_equal': ra == rn == rb,
                        'rules': [ra, rn, rb], 'restored_vs_refined': tw2.diff(a, r2), 'native_vs_refined': tw2.diff(a, n)}
                dump('tw.pauseParticles(false)')
            row['rules_after'] = dump('tw.rules()')
            row['cells_end'] = dump('tw.s12cells(false)')
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
                    r['screenshots'].append(view(f'{label}-start', px, py))
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
    p.add_argument('--teaa', required=True, help='before/survey: HEAD TEAA; after: HEAD plus the S12 files')
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
