#!/usr/bin/env python3
"""TW5 live check in the isolated fixture: Gates of Morning.

One cold start per run. `after` uses the working-tree addon; `before` installs
a TEAA built from HEAD (--before-teaa) to record the pre-TW5 natural state at
the same fixed poses (same flow as tools/run_tw4_validation.py). Both phases
end with a regression probe of the nine committed towns (0.6.28's seven plus
TW4's Shatur and Point Zero) so their counts can be compared before/after.
`after` also measures lit-pixel pairs (visible board floor next to a visible
board golden-mountain cell) on the natural 64px frames and places the FENS
entrance the way the zone's post_process does for a sunwall player.

The fixture is shared: before each launch the recorded game/Xvfb pids in
session/processes.json are checked via /proc/<pid>/cmdline and the tool waits
while they are alive; it never stops a process it did not start. Screenshots
stay local under evidence/terrain-tw5-20260929/screenshots/.
"""
import argparse, json, statistics, subprocess, sys
from pathlib import Path
from PIL import Image, ImageStat
from capture_korpul import Fixture, HOME, ROOT, SESSION, digest, png_size
from run_norgos_validation import stop_started
from run_tw2_validation import launch, read, luminance
import run_tw2_validation as tw2

OUT = ROOT / 'evidence/terrain-tw5-20260929'
SHOTS = OUT / 'screenshots'
tw2.SHOTS = SHOTS  # luminance()/diff() read frames from this run's folder
TOWNS = [('gates', 'town-gates-of-morning')]
# Fixed poses on the verified static map (data/maps/towns/gates-of-morning.lua,
# 50x50): window centre, stand cell. 'remembered' stands on the southern beach
# so no cell of the north-west window is in FOV.
POSES = {
    'gates': [('remembered', (12, 9, 38, 42)),   # NW shops 6/0/9, building blocks, north mountain ring
              ('centre', (35, 16, 33, 20)),      # plaza shops 3/4/5, Zemekkys' hall, roads, Melnela
              ('mountain', (43, 9, 40, 12)),     # NE mountain ring over the shop 8/A block
              ('beach', (36, 40, 32, 38)),       # sand, palms, ocean inlet, SE mountain ring
              ('west', (12, 38, 18, 36)),        # lake, trees, grass, Limmir, SW mountain ring
              ('gate', (5, 26, 6, 26))],         # world exit, western road, gap in the ring
}
TOGGLE = {'centre', 'mountain', 'beach', 'west'}
PAIRS = {'centre', 'mountain', 'beach', 'west', 'gate'}
REGRESSION = [('derth', 'town-derth'), ('lumberjack', 'town-lumberjack-village'), ('lasthope', 'town-last-hope'),
              ('elvala', 'town-elvala'), ('zigur', 'town-zigur'), ('angolwen', 'town-angolwen'),
              ('council', 'town-iron-council'), ('shatur', 'town-shatur'), ('pointzero', 'town-point-zero')]


def pair_values(frame, data):
    """Median 40% centre crop per cell, for every floor/mountain pair."""
    im = Image.open(SHOTS / frame).convert('L')
    s = data['tile']

    def cell(sx, sy):
        return ImageStat.Stat(im.crop((int(sx + s * .3), int(sy + s * .3), int(sx + s * .7), int(sy + s * .7)))).mean[0]

    rows = []
    for p in data['pairs']:
        f, w = p['floor'], p['wall']
        rows.append({'floor': f[:2], 'floor_family': f[4], 'wall': w[:2],
                     'floor_value': round(cell(f[2], f[3]), 2), 'wall_value': round(cell(w[2], w[3]), 2)})
    if not rows:
        return {'pairs': 0}
    fl = statistics.median(r['floor_value'] for r in rows)
    wl = statistics.median(r['wall_value'] for r in rows)
    by = {}
    for r in rows:
        by.setdefault(r['floor_family'], []).append(r)
    return {'pairs': len(rows), 'floor_median': round(fl, 2), 'wall_median': round(wl, 2),
            'absolute_gap': round(fl - wl, 2), 'relative_gap': round((fl - wl) / fl, 4),
            'by_floor': {k: {'n': len(v), 'floor_median': round(statistics.median(r['floor_value'] for r in v), 2),
                             'wall_median': round(statistics.median(r['wall_value'] for r in v), 2)} for k, v in by.items()},
            'rows': rows}


def run(phase, only=None, regression=True):
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
        name = f'tw5-{tag}'
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
        fr['luminance'] = luminance(Path(fr['file']).name, dump('tw.samples()', 'tw-samples.json'))
        if pairs:
            fr['lit_pixels'] = pair_values(Path(fr['file']).name, dump('tw.pairs()', 'tw-pairs.json'))
        return fr

    result = {'phase': phase, 'towns': {}}
    try:
        f.lua("assert(config.settings.cheat and config.settings.disable_all_connectivity and not profile.auth);"
              "assert(core.shader.active(4));tw=dofile('/data-checker-fixture/monster-live_tw5_scene.lua');ms=tw.ms;ms.setup();"
              "tc=dofile('/data-checker-fixture/monster-live_terrain_census.lua');"
              # Fixture-only: no rain/cloud particles so toggle frames compare terrain.
              "config.settings.tome.weather_effects=false")
        for label, zone in TOWNS:
            if only and label != only:
                continue
            row = {'zone': zone, 'screenshots': [], 'poses': {}}
            result['towns'][label] = row
            if phase == 'after':
                f.lua('tw.setInstall(false)')
            row['enter'] = dump(f"ms.enter('{zone}',1)", 'tw-enter.json')
            row['enter_player'] = [row['enter']['player_x'], row['enter']['player_y']]
            f.lua('ms.caveClearDialogs()')
            row['stats_natural'] = dump('tw.stats()', 'tw-stats.json')
            if phase == 'after':
                row['stats_install_off'] = row['stats_natural']
                row['probe_install_off'] = dump('tw.probe()', 'tw-probe-off.json')['totals']
                f.lua('tw.setInstall(true)')
                dump('tw.apply()', 'tw-apply.json')
                row['stats_natural'] = dump('tw.stats()', 'tw-stats.json')
            row['rules_before'] = dump('tw.rules()', 'tw-rules.json')
            row['probe_natural'] = dump('tw.probe()', 'tw-probe.json')
            row['kinds_natural'] = dump('tw.tw3()', 'tw-kinds.json')
            row['quiet'] = dump('tw.quiet()', 'tw-quiet.json')
            for kind, (cx, cy, sx, sy) in POSES[label]:
                pose = row['poses'][kind] = dump(f"tw.poseAt({cx},{cy},{sx},{sy},'{kind}')", 'tw-pose.json')
                for tile in (48, 64):
                    row['screenshots'].append(photo(tile, f'{label}-{kind}', cx, cy, pairs=tile == 64 and kind in PAIRS))
                if phase == 'after' and kind == 'remembered':
                    f.lua("tw.setInstall(false);game.level.map._checker_korpul=nil;tw.apply()")
                    off = photo(64, f'{label}-{kind}-install-off', cx, cy)
                    row['stats_remembered_install_off'] = dump('tw.stats()', 'tw-stats-off.json')
                    f.lua("tw.setInstall(true);tw.apply()")
                    on = photo(64, f'{label}-{kind}-install-on', cx, cy)
                    first = next(s for s in row['screenshots'] if s['tag'] == f'after-{label}-{kind}-64')
                    row['install_toggle'] = {'off': off, 'on': on, 'on_vs_first': tw2.diff(first, on),
                                             'off_vs_first': tw2.diff(first, off)}
                    row['screenshots'] += [off, on]
                if phase == 'after' and kind in TOGGLE:
                    row.setdefault('particles_paused', {})[kind] = dump('tw.pauseParticles(true)', 'tw-pause.json')
                    before = photo(64, f'{label}-{kind}-toggle-refined', cx, cy)
                    rb = dump('tw.rules()', 'tw-rules-t0.json')
                    f.lua("ms.setMode('vanilla')")
                    native = photo(64, f'{label}-{kind}-toggle-native', cx, cy)
                    rn = dump('tw.rules()', 'tw-rules-t1.json')
                    row.setdefault('native_probe', {})[kind] = dump('tw.probe()', 'tw-probe-native.json')['totals']
                    f.lua("ms.setMode('refined')")
                    after = photo(64, f'{label}-{kind}-toggle-restored', cx, cy)
                    ra = dump('tw.rules()', 'tw-rules-t2.json')
                    dump('tw.pauseParticles(false)', 'tw-pause.json')
                    row.setdefault('toggle', {})[kind] = {
                        'refined': before, 'native': native, 'restored': after,
                        'restored_vs_refined': tw2.diff(before, after), 'native_vs_refined': tw2.diff(before, native),
                        'rules': [rb, rn, ra], 'rules_equal': rb == rn == ra}
                    row['screenshots'] += [before, native, after]
            row['rules_after'] = dump('tw.rules()', 'tw-rules-after.json')
            assert row['rules_before'] == row['rules_after'], (row['rules_before'], row['rules_after'])
            row['stats_end'] = dump('tw.stats()', 'tw-stats-end.json')
            row['probe_end'] = dump('tw.probe()', 'tw-probe-end.json')
            row['kinds_end'] = dump('tw.tw3()', 'tw-kinds-end.json')
            # An ungated town (before) runs in vanilla mode: every cell is native.
            row['census_forced'] = dump("game.checker_mode=='refined' and tc.census() or {skipped=tostring(game.checker_mode)}",
                                        'tw-census.json')
            # Fixture-only: the sunwall-only FENS entrance, placed exactly as
            # the zone's post_process does it; it must stay native.
            row['fens'] = dump('tw.addFens()', 'tw-fens.json')
            fx, fy = row['fens']['x'], row['fens']['y']
            f.lua(f"tw.poseAt({fx},{fy},{fx},{fy + 2},'fens')")
            row['screenshots'].append(photo(64, f'{label}-fens', fx, fy))
        if regression and not only:
            reg = result['regression'] = {}
            for label, zone in REGRESSION:
                r = reg[label] = {'zone': zone}
                r['enter'] = dump(f"ms.enter('{zone}',1)", 'tw-enter.json')
                f.lua('ms.caveClearDialogs()')
                r['probe_natural'] = dump('tw.probe()', 'tw-probe.json')['totals']
                r['stats_natural'] = {k: v for k, v in dump('tw.stats()', 'tw-stats.json').items() if k not in ('shop_images',)}
                census = dump("game.checker_mode=='refined' and tc.census() or {skipped=tostring(game.checker_mode)}", 'tw-census.json')
                r['census_forced'] = {k: census.get(k) for k in ('total', 'converted', 'native', 'converted_stone', 'converted_forest', 'groups', 'skipped')}
        return result
    finally:
        (OUT / (f'validation-{phase}' + (f'-{only}' if only else '') + '.txt')).write_text((''.join(f.transcript) + f.new_log()).rstrip() + '\n')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('phase', choices=('after', 'before'))
    p.add_argument('--before-teaa', help='TEAA built from HEAD for the before phase')
    p.add_argument('--no-regression', action='store_true')
    a = p.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / 'scenes.json'
    survey = json.loads(path.read_text()) if path.exists() else {}
    if a.phase == 'before':
        assert a.before_teaa, '--before-teaa is required for the before phase'
    meta = launch(a.before_teaa if a.phase == 'before' else None)
    try:
        result = run(a.phase, regression=not a.no_regression)
        result['launch_plan'] = json.loads((SESSION / 'launch-plan.json').read_text())
        survey[a.phase] = result
        path.write_text(json.dumps(survey, ensure_ascii=False, indent=1) + '\n')
        print('PASS', a.phase, flush=True)
    finally:
        stop_started(meta)
        print('STOP', a.phase, flush=True)


if __name__ == '__main__':
    main()
