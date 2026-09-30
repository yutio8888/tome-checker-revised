#!/usr/bin/env python3
"""S13 live check in the isolated fixture: Ardhungol's unstable wormhole (T2)
and exact DEEP_WATER in further stone zones (the S12 stone-kerb water).

`survey` (HEAD TEAA, no photographs): census of every level below — every
WORMHOLE / water cell with fields, callbacks (file:line), stamps, owner, kind
and the grid's own particle emitters, plus the forced census. `before`
(HEAD TEAA) and `after` (HEAD plus exactly the S13 files, checked
byte-for-byte in the TEAA, so the concurrent monster batch's unfinished files
are never loaded) photograph the wormhole and water windows at 48/64 px.
After: the wormhole particle on/off at the same window (the particle is drawn
over the board floor), Refined -> Native -> Refined with the wormhole
emitters taken off (pixel identity) and with them on (particles kept in all
three states), rule digests in each state. Forced vault levels pin the
level's vault list only (fixture-only generator probe; vault file, tiles and
rules native). Every level is entered after rng.seed(<fixed>).

The fixture is shared: before each launch the recorded game/Xvfb pids in
session/processes.json are checked via /proc/<pid>/cmdline and the tool waits
while they are alive; it never stops a process it did not start. Screenshots
stay local under evidence/terrain-s13-20260930/screenshots/.
"""
import argparse, json, subprocess, sys, zipfile
from pathlib import Path
from PIL import Image, ImageChops, ImageStat
from capture_korpul import Fixture, HOME, ROOT, SESSION, digest, png_size
from run_norgos_validation import stop_started
from run_tw2_validation import launch, read
import run_tw2_validation as tw2

OUT = ROOT / 'evidence/terrain-s13-20260930'
SHOTS = OUT / 'screenshots'
tw2.SHOTS = SHOTS
SEED = 13013
PARTIAL = {}
WORM = '^WORMHOLE$'
WATER = '^DEEP_WATER$'
WV = ['water-vault', 'trapped-hexagon']

# (label, zone, level, forced (list key, list, rooms) or None, ms.enter opts, photo patterns)
GV = 'greater_vaults_list'
FORCE_G = (GV, WV, [['greater_vault', 100], 'random_room'])
LEVELS = [('ard1', 'ardhungol', 1, None, None, (WORM,)),
          ('ard2', 'ardhungol', 2, None, None, (WORM,)),
          ('ard3', 'ardhungol', 3, None, None, ()),
          ('dread6v', 'dreadfell', 6, FORCE_G, None, (WATER,)),
          ('hp7v', 'high-peak', 7, FORCE_G, None, (WATER,)),
          ('vor2', 'vor-armoury', 2, None, None, ())]
# Census only (no photographs): other stone levels that can place DEEP_WATER.
CENSUS = [('dread1', 'dreadfell', 1, None, None),
          ('dread8', 'dreadfell', 8, None, None),
          ('dread3v', 'dreadfell', 3, FORCE_G, None),
          ('hp5', 'high-peak', 5, None, None),
          ('hp9v', 'high-peak', 9, FORCE_G, None),
          ('halfling2', 'halfling-ruins', 2, None, None),
          ('rhaloren-og', 'rhaloren-camp', 1, ('lesser_vaults_list', ['collapsed-tower'], ['lesser_vault']), {'overground': True}),
          ('tannen2', 'tannen-tower', 2, None, None),
          ('gorbat1', 'gorbat-pride', 1, None, None),
          ('vorpride1', 'vor-pride', 1, None, None),
          ('grushnak1', 'grushnak-pride', 1, None, None),
          ('conclave1', 'conclave-vault', 1, None, None),
          ('rift3', 'temporal-rift', 3, None, None),
          ('abashed1', 'abashed-expanse', 1, None, None)]
TOGGLE = {'ard1', 'dread6v', 'hp7v'}
REGRESS = [('derth', 'town-derth', 1), ('korpul', 'ruins-kor-pul', 1)]
S13_FILES = ['overload/mod/class/CheckerTerrain.lua', 'superload/mod/class/Grid.lua']


def gray(frame, cell):
    s = cell['tile']
    im = Image.open(SHOTS / Path(frame).name).convert('L').crop(
        (int(cell['sx'] + s * .2), int(cell['sy'] + s * .2), int(cell['sx'] + s * .8), int(cell['sy'] + s * .8)))
    return round(ImageStat.Stat(im).mean[0], 1)


def cell_diff(a, b, cell):
    s = cell['tile']
    box = (int(cell['sx']), int(cell['sy']), int(cell['sx'] + s), int(cell['sy'] + s))
    d = ImageChops.difference(Image.open(SHOTS / Path(a['file']).name).convert('RGB').crop(box),
                              Image.open(SHOTS / Path(b['file']).name).convert('RGB').crop(box)).convert('L')
    h = d.histogram()
    return {'differing_pixels': sum(h) - h[0], 'of': sum(h)}


def masked_diff(a, b, rects):
    """Frame difference outside the given cell rectangles (the wormholes)."""
    ims = []
    for fr in (a, b):
        im = Image.open(SHOTS / Path(fr['file']).name).convert('RGB')
        for r in rects:
            s = r['tile']
            im.paste((0, 0, 0), (int(r['sx']), int(r['sy']), int(r['sx'] + s), int(r['sy'] + s)))
        ims.append(im)
    h = ImageChops.difference(*ims).convert('L').histogram()
    return {'identical': h[0] == sum(h), 'differing_pixels': sum(h) - h[0], 'masked_cells': len(rects)}


def crop(frame, cell, pad=2):
    s = cell['tile']
    im = Image.open(SHOTS / Path(frame).name)
    box = (int(cell['sx'] - pad * s), int(cell['sy'] - pad * s), int(cell['sx'] + (pad + 1) * s), int(cell['sy'] + (pad + 1) * s))
    name = Path(frame).name.replace('.png', f"-crop-{cell['x']}-{cell['y']}.png")
    im.crop(box).save(SHOTS / name)
    return 'screenshots/' + name


def run(phase, only=None, shots=True, regression=True, census_only=False, tag=None):
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
            for rel in S13_FILES:
                assert z.read(rel) == (ROOT / rel).read_bytes(), rel

    def dump(code, name='s13.json'):
        f.lua(f"ms.dump('/{name}',{code})")
        return read(name)

    def size(tile):
        f.lua(f"game:setResolution('1920x1080 Windowed',true);config.settings.tome.gfx.size='{tile}x{tile}';"
              f"game:setupDisplayMode(false)")

    def shot(tag):
        name = f's13-{tag}'
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

    def enter(zone, level, forced, opts):
        if forced:
            key, lst, rooms = forced
            lua = lambda v: json.dumps(v).replace('[', '{').replace(']', '}')
            o = 'nil' if not opts else '{' + ','.join(f'{k}={str(v).lower()}' for k, v in opts.items()) + '}'
            return dump(f"tw.enterList('{zone}',{level},'{key}',{lua(lst)},{lua(rooms)},{o})")
        o = '' if not opts else ',{' + ','.join(f'{k}={str(v).lower()}' for k, v in opts.items()) + '}'
        return dump(f"ms.enter('{zone}',{level}{o})")

    result = PARTIAL
    result.update({'phase': phase, 'seed': SEED, 'levels': {}, 'census_levels': {}})
    try:
        f.lua("assert(config.settings.cheat and config.settings.disable_all_connectivity and not profile.auth);"
              "assert(core.shader.active(4));tw=dofile('/data-checker-fixture/monster-live_s13_scene.lua');ms=tw.ms;ms.setup();"
              "tc=dofile('/data-checker-fixture/monster-live_terrain_census.lua');tc.setup();"
              "config.settings.tome.weather_effects=false")
        size(64)
        for i, (label, zone, level, forced, opts, patterns) in enumerate(LEVELS):
            if census_only or (only and label not in only):
                continue
            row = {'zone': zone, 'level': level, 'forced': forced, 'screenshots': []}
            result['levels'][label] = row
            f.lua(f'rng.seed({SEED + i})')
            row['enter'] = enter(zone, level, forced, opts)
            f.lua('ms.caveClearDialogs()')
            row['quiet'] = dump('tw.quiet()')
            row['rules_before'] = dump('tw.rules()')
            row['cells_natural'] = dump('tw.s13cells(false)')
            row['census_forced'] = census()
            row['cells_forced'] = dump('tw.s13cells()')
            row['windows'] = {}
            for pat in patterns:
                if not shots:
                    continue
                w = dump(f"tw.pickWindow('{pat}')")
                if not w.get('x'):
                    continue
                key = 'worm' if pat == WORM else 'water'
                b = dump(f"tw.besideHazard('{pat}',{w['x']},{w['y']})")
                row['windows'][key] = {'window': w, 'beside': b}
                if not b.get('x'):
                    continue
                row['windows'][key]['pose'] = dump(f"tw.placePlayer({b['x']},{b['y']},{w['x']},{w['y']})")
                # A lore note picked up on arrival opens a popup over the map.
                f.lua('ms.caveClearDialogs()')
                dump('tw.pauseParticles(true)')
                dump('tw.clearLog()')
                probe = [(b['x'], b['y']), tuple(b['hazard'])]
                hx, hy = b['hazard']
                for tile in (48, 64):
                    size(tile)
                    fr = view(f'{label}-{key}-{tile}', w['x'], w['y'], probe)
                    fr['crop'] = crop(fr['file'], fr['cells'][f'{hx},{hy}']['screen'])
                    fr['samples'] = dump(f"tw.graySamples({w['x']},{w['y']})")
                    for s in fr['samples'].get('cells', []):
                        s['gray'] = gray(fr['file'], s)
                    row['screenshots'].append(fr)
                    if key == 'worm':
                        # Same window with the wormholes' own emitters taken off:
                        # the difference on the wormhole cell is the particle.
                        row.setdefault('particle', {})[tile] = {'off': dump('tw.wormholes(false)')}
                        off = view(f'{label}-{key}-{tile}-particle-off', w['x'], w['y'], probe)
                        row['particle'][tile]['on_again'] = dump('tw.wormholes(true)')
                        sc = fr['cells'][f'{hx},{hy}']['screen']
                        row['particle'][tile].update({'frame_off': off, 'cell_diff': cell_diff(fr, off, sc),
                                                      'frame_diff': tw2.diff(fr, off)})
                        row['particle'][tile]['crop_off'] = crop(off['file'], sc)
                size(64)
                if label in TOGGLE and phase == 'after':
                    tg = row.setdefault('toggle', {})
                    for hide in ((True, False) if key == 'worm' else (False,)):
                        ttag = f'{key}-toggle' + ('-still' if hide else '')
                        if hide:
                            dump('tw.wormholes(false)')
                        a = view(f'{label}-{ttag}-refined', w['x'], w['y'], probe)
                        ra = dump('tw.rules()')
                        ca = dump('tw.s13cells(false)')
                        f.lua("ms.setMode('vanilla')")
                        n = view(f'{label}-{ttag}-native', w['x'], w['y'], probe)
                        rn = dump('tw.rules()')
                        cn = dump('tw.s13cells(false)')
                        f.lua("ms.setMode('refined')")
                        r2 = view(f'{label}-{ttag}-restored', w['x'], w['y'], probe)
                        rb = dump('tw.rules()')
                        cb = dump('tw.s13cells(false)')
                        if hide:
                            dump('tw.wormholes(true)')
                        extra = {}
                        if key == 'worm':
                            rects = dump('tw.wormRects()')
                            extra = {'restored_vs_refined_outside_wormholes': masked_diff(a, r2, rects),
                                     'native_vs_refined_outside_wormholes': masked_diff(a, n, rects)}
                        tg[ttag] = {**extra, 'refined': a, 'native': n, 'restored': r2, 'rules_equal': ra == rn == rb,
                                   'rules': [ra, rn, rb], 'restored_vs_refined': tw2.diff(a, r2),
                                   'native_vs_refined': tw2.diff(a, n), 'cells': [ca['ids'], cn['ids'], cb['ids']]}
                dump('tw.pauseParticles(false)')
            row['rules_after'] = dump('tw.rules()')
            row['cells_end'] = dump('tw.s13cells(false)')
        for i, (label, zone, level, forced, opts) in enumerate(CENSUS):
            if only and label not in only:
                continue
            row = {'zone': zone, 'level': level, 'forced': forced, 'opts': opts}
            result['census_levels'][label] = row
            f.lua(f'rng.seed({SEED + 100 + i})')
            try:
                row['enter'] = enter(zone, level, forced, opts)
                f.lua('ms.caveClearDialogs()')
                row['cells_natural'] = dump('tw.s13cells(false)')
                row['census_forced'] = census()
                row['cells_forced'] = dump('tw.s13cells(false)')
            except Exception as e:  # a census level that cannot be entered is recorded, not fatal
                row['error'] = repr(e)[:2000]
        if regression and not only and not census_only:
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
        (OUT / (f'validation-{tag or phase}' + (('-' + '-'.join(only))[:80] if only else '') + '.txt')).write_text(
            (''.join(f.transcript) + f.new_log()).rstrip() + '\n')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('phase', choices=('after', 'before', 'survey'))
    p.add_argument('--teaa', required=True, help='before/survey: HEAD TEAA; after: HEAD plus the S13 files')
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
            result = run(phase, only=a.only, shots=a.phase != 'survey', regression=not a.no_regression, tag=a.phase)
        except Exception as e:
            result = PARTIAL
            result['error'] = repr(e)[:4000]
        result['launch_plan'] = json.loads((SESSION / 'launch-plan.json').read_text())
        key = a.phase
        if a.only and key in scenes and 'levels' in scenes[key]:
            prev = scenes[key]
            prev.setdefault('reruns', []).append({'only': a.only, 'launch_plan': result['launch_plan'], 'error': result.get('error')})
            prev['levels'].update(result['levels'])
            prev.setdefault('census_levels', {}).update(result['census_levels'])
        else:
            scenes[key] = result
        path.write_text(json.dumps(scenes, ensure_ascii=False, indent=1) + '\n')
        print('ERROR ' + result['error'] if result.get('error') else 'PASS', a.phase, flush=True)
    finally:
        stop_started(meta)
        print('STOP', a.phase, flush=True)


if __name__ == '__main__':
    main()
