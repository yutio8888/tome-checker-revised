#!/usr/bin/env python3
"""S14 live check in the isolated fixture: portal / farportal bridge and the
High Peak invocation portals / Sanctum portal.

`survey` (HEAD TEAA, no photographs): per level, every portal-like cell with
fields, callbacks (file:line), stamps, owner, S14 kind/reason and the map
particle emitters on it, plus the forced census. Quest-made portals are
staged with their quest's own addEntity sequence (fixture only). `before`
(HEAD TEAA) and `after` (HEAD plus exactly the S14 files, checked
byte-for-byte in the installed TEAA, so the concurrent monster batch's
unfinished files are never loaded) photograph the portal windows at 48/64 px.
After: map particles on/off at the same window (the native vortex/lightning
over the board floor), Refined -> Native -> Refined with the map particles
paused (pixel identity) and running, rule digests in each state, and on High
Peak L11 the native invocation-portal shutdown (display stays, rules digest
changes only by the callback's own name/colour write). Every level is entered
after rng.seed(<fixed>).

The fixture is shared: before each launch the recorded game/Xvfb pids in
session/processes.json are checked via /proc/<pid>/cmdline and the tool waits
while they are alive; it never stops a process it did not start. Screenshots
stay local under evidence/terrain-s14-20260930/screenshots/.
"""
import argparse, json, subprocess, sys, zipfile
from pathlib import Path
from PIL import Image, ImageChops, ImageStat
from capture_korpul import Fixture, HOME, ROOT, SESSION, digest, png_size
from run_norgos_validation import stop_started
from run_tw2_validation import launch, read
import run_tw2_validation as tw2

OUT = ROOT / 'evidence/terrain-s14-20260930'
SHOTS = OUT / 'screenshots'
tw2.SHOTS = SHOTS
SEED = 14014
PARTIAL = {}

# (label, zone, level, stage or None, [(window tag, centre id)])
LEVELS = [('hp11', 'high-peak', 11, None, [('sanctum', 'CVOID_PORTAL'), ('east', 'CFAR_EAST_PORTAL'), ('orb', 'ORB_DRAGON')]),
          ('hp10', 'high-peak', 10, None, [('boss', 'PORTAL_BOSS')]),
          ('reknor4', 'reknor', 4, None, [('farportal', 'CFAR_EAST_PORTAL')]),
          ('lasthope', 'town-last-hope', 1, 'last-hope', [('farportal', 'CFAR_EAST_PORTAL')]),
          ('gates', 'town-gates-of-morning', 1, 'gates', [('farportal', 'CWEST_PORTAL')]),
          # Tannen's portal replaces the up stairs inside four locked lever
          # doors (tannen-tower-4 map): its four native levers open them and
          # the photograph looks down the corridor from three cells west.
          ('tannen1', 'tannen-tower', 1, 'tannen', [('portal', 'PORTAL_BACK', (-3, 0))]),
          ('fortress', 'shertul-fortress', 1, None, [('farportal', 'CFARPORTAL')]),
          ('demon', 'demon-plane', 1, 'demon', [('portal', 'PORTAL_BACK')])]
# Census only (no photographs): portals that stay native, for the record.
CENSUS = [('eruan3', 'eruan', 3, None),
          ('charred', 'charred-scar', 1, 'charred'),
          ('slazish', 'slazish-fen', 1, None),
          ('ruined', 'ruined-dungeon', 1, None),
          ('hp1', 'high-peak', 1, None),
          ('hp5', 'high-peak', 5, None)]
TOGGLE = {'hp11', 'hp10', 'reknor4', 'lasthope', 'gates', 'tannen1', 'fortress', 'demon'}
REGRESS = [('derth', 'town-derth', 1), ('korpul', 'ruins-kor-pul', 1)]
S14_FILES = ['overload/mod/class/CheckerTerrain.lua', 'superload/mod/class/Grid.lua', 'superload/engine/Zone.lua']


def gray(frame, cell):
    s = cell['tile']
    im = Image.open(SHOTS / Path(frame).name).convert('L').crop(
        (int(cell['sx'] + s * .2), int(cell['sy'] + s * .2), int(cell['sx'] + s * .8), int(cell['sy'] + s * .8)))
    return round(ImageStat.Stat(im).mean[0], 1)


def box_diff(a, b, cell, pad=0):
    s = cell['tile']
    box = (int(cell['sx'] - pad * s), int(cell['sy'] - pad * s), int(cell['sx'] + (pad + 1) * s), int(cell['sy'] + (pad + 1) * s))
    d = ImageChops.difference(Image.open(SHOTS / Path(a['file']).name).convert('RGB').crop(box),
                              Image.open(SHOTS / Path(b['file']).name).convert('RGB').crop(box)).convert('L')
    h = d.histogram()
    return {'differing_pixels': sum(h) - h[0], 'of': sum(h)}


def masked_diff(a, b, rects, pad=0):
    """Frame difference outside the given cell rectangles (grown by pad cells)."""
    ims = []
    for fr in (a, b):
        im = Image.open(SHOTS / Path(fr['file']).name).convert('RGB')
        for r in rects:
            s = r['tile']
            im.paste((0, 0, 0), (int(r['sx'] - pad * s), int(r['sy'] - pad * s), int(r['sx'] + (pad + 1) * s), int(r['sy'] + (pad + 1) * s)))
        ims.append(im)
    h = ImageChops.difference(*ims).convert('L').histogram()
    return {'identical': h[0] == sum(h), 'differing_pixels': sum(h) - h[0], 'masked_cells': len(rects), 'pad': pad}


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
            for rel in S14_FILES:
                assert z.read(rel) == (ROOT / rel).read_bytes(), rel

    def dump(code, name='s14.json'):
        f.lua(f"ms.dump('/{name}',{code})")
        return read(name)

    def size(tile):
        f.lua(f"game:setResolution('1920x1080 Windowed',true);config.settings.tome.gfx.size='{tile}x{tile}';"
              f"game:setupDisplayMode(false)")

    def shot(tag):
        name = f's14-{tag}'
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
    result.update({'phase': phase, 'seed': SEED, 'levels': {}, 'census_levels': {}})
    try:
        f.lua("assert(config.settings.cheat and config.settings.disable_all_connectivity and not profile.auth);"
              "assert(core.shader.active(4));tw=dofile('/data-checker-fixture/monster-live_s14_scene.lua');ms=tw.ms;ms.setup();"
              "tc=dofile('/data-checker-fixture/monster-live_terrain_census.lua');tc.setup();"
              "config.settings.tome.weather_effects=false")
        size(64)
        for i, (label, zone, level, stage, windows) in enumerate(LEVELS):
            if census_only or (only and label not in only):
                continue
            row = {'zone': zone, 'level': level, 'stage': stage, 'screenshots': []}
            result['levels'][label] = row
            f.lua(f'rng.seed({SEED + i})')
            row['enter'] = dump(f"ms.enter('{zone}',{level})")
            f.lua('ms.caveClearDialogs()')
            if stage:
                row['staged'] = dump(f"tw.stage('{stage}')")
            if label == 'tannen1':
                # All four native levers (lever_action=4 opens the doors); the
                # actors around them are cleared first (poseAt), one guards a lever.
                row['lever'] = dump("(function() local o={} tw.poseAt(12,12,12,15,'levers') for _,l in ipairs(tw.levers()) do "
                                    "local ok,r=pcall(tw.pull,l.x,l.y);o[#o+1]={x=l.x,y=l.y,moved=ok and r.moved or tostring(r)} end "
                                    "o.door=tw.cell(12,13).id return o end)()")
                f.lua('ms.caveClearDialogs()')
            row['quiet'] = dump('tw.quiet()')
            row['rules_before'] = dump('tw.rules()')
            row['cells_natural'] = dump('tw.s14cells(false)')
            row['census_forced'] = census()
            row['cells_forced'] = dump('tw.s14cells()')
            row['windows'] = {}
            for wtag, wid, *off in windows:
                dx, dy = off[0] if off else (0, 2)
                if not shots:
                    continue
                w = dump(f"tw.find('{wid}')")
                if not w.get('x'):
                    row['windows'][wtag] = {'missing': wid}
                    continue
                wx, wy = w['x'], w['y']
                row['windows'][wtag] = {'window': w, 'pose': dump(f"tw.placePlayer({wx + dx},{wy + dy},{wx},{wy})")}
                f.lua('ms.caveClearDialogs()')
                dump('tw.clearLog()')
                probe = [(wx, wy)]
                for tile in (48, 64):
                    size(tile)
                    fr = view(f'{label}-{wtag}-{tile}', wx, wy, probe)
                    fr['crop'] = crop(fr['file'], fr['cells'][f'{wx},{wy}']['screen'])
                    fr['samples'] = dump(f"tw.graySamples({wx},{wy})")
                    for s in fr['samples'].get('cells', []):
                        s['gray'] = gray(fr['file'], s)
                    row['screenshots'].append(fr)
                    # Same window with the level's map particle emitters paused:
                    # the difference is the native vortex / lightning.
                    pt = row.setdefault('particle', {}).setdefault(wtag, {})
                    pt[tile] = {'off': dump('tw.pauseParticles(true)')}
                    off = view(f'{label}-{wtag}-{tile}-particles-off', wx, wy, probe)
                    pt[tile]['on_again'] = dump('tw.pauseParticles(false)')
                    sc = fr['cells'][f'{wx},{wy}']['screen']
                    pt[tile].update({'frame_off': off, 'cell_diff': box_diff(fr, off, sc),
                                     'block3_diff': box_diff(fr, off, sc, 1), 'frame_diff': tw2.diff(fr, off)})
                    pt[tile]['crop_off'] = crop(off['file'], sc)
                size(64)
                if label in TOGGLE and phase == 'after':
                    tg = row.setdefault('toggle', {}).setdefault(wtag, {})
                    for still in (True, False):
                        ttag = 'toggle' + ('-still' if still else '')
                        if still:
                            dump('tw.pauseParticles(true)')
                        a = view(f'{label}-{wtag}-{ttag}-refined', wx, wy, probe)
                        ra = dump('tw.rules()')
                        ca = dump('tw.s14cells(false)')
                        f.lua("ms.setMode('vanilla')")
                        n = view(f'{label}-{wtag}-{ttag}-native', wx, wy, probe)
                        rn = dump('tw.rules()')
                        cn = dump('tw.s14cells(false)')
                        f.lua("ms.setMode('refined')")
                        r2 = view(f'{label}-{wtag}-{ttag}-restored', wx, wy, probe)
                        rb = dump('tw.rules()')
                        cb = dump('tw.s14cells(false)')
                        if still:
                            dump('tw.pauseParticles(false)')
                        rects = dump('tw.portalRects()')
                        tg[ttag] = {'refined': a, 'native': n, 'restored': r2, 'rules_equal': ra == rn == rb,
                                    'rules': [ra, rn, rb], 'restored_vs_refined': tw2.diff(a, r2),
                                    'native_vs_refined': tw2.diff(a, n),
                                    'restored_vs_refined_outside_portals': masked_diff(a, r2, rects, 1),
                                    'cells': [ca['ids'], cn['ids'], cb['ids']]}
            if label == 'hp11' and phase == 'after' and shots:
                # The native shutdown of one invocation portal, then the same window.
                o = dump("tw.find('ORB_DRAGON')")
                row['orb_close'] = {'rules_before': dump('tw.rules()'), 'close': dump(f"tw.closeOrb({o['x']},{o['y']})")}
                f.lua('ms.caveClearDialogs()')
                dump('tw.clearLog()')
                dump('tw.pauseParticles(true)')
                fr = view('hp11-orb-closed-64', o['x'], o['y'], [(o['x'], o['y'])])
                fr['crop'] = crop(fr['file'], fr['cells'][f"{o['x']},{o['y']}"]['screen'])
                row['orb_close']['frame'] = fr
                row['orb_close']['rules_after'] = dump('tw.rules()')
                row['orb_close']['cells'] = dump('tw.s14cells(false)')
                a = fr
                f.lua("ms.setMode('vanilla')")
                n = view('hp11-orb-closed-native-64', o['x'], o['y'], [(o['x'], o['y'])])
                f.lua("ms.setMode('refined')")
                r2 = view('hp11-orb-closed-restored-64', o['x'], o['y'], [(o['x'], o['y'])])
                row['orb_close'].update({'native': n, 'restored': r2, 'restored_vs_refined': tw2.diff(a, r2)})
                dump('tw.pauseParticles(false)')
            row['rules_after'] = dump('tw.rules()')
            row['cells_end'] = dump('tw.s14cells(false)')
        for i, (label, zone, level, stage) in enumerate(CENSUS):
            if only and label not in only:
                continue
            row = {'zone': zone, 'level': level, 'stage': stage}
            result['census_levels'][label] = row
            f.lua(f'rng.seed({SEED + 100 + i})')
            try:
                row['enter'] = dump(f"ms.enter('{zone}',{level})")
                f.lua('ms.caveClearDialogs()')
                if stage:
                    row['staged'] = dump(f"tw.stage('{stage}')")
                row['cells_natural'] = dump('tw.s14cells(false)')
                row['census_forced'] = census()
                row['cells_forced'] = dump('tw.s14cells()')
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
    p.add_argument('--teaa', required=True, help='before/survey: HEAD TEAA; after: HEAD plus the S14 files')
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
            for k in ('regression', 'error'):
                if k in result:
                    prev[k] = result[k]
        else:
            scenes[key] = result
        path.write_text(json.dumps(scenes, ensure_ascii=False, indent=1) + '\n')
        print('ERROR ' + result['error'] if result.get('error') else 'PASS', a.phase, flush=True)
    finally:
        stop_started(meta)
        print('STOP', a.phase, flush=True)


if __name__ == '__main__':
    main()
