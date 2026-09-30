#!/usr/bin/env python3
"""TW7 live check in the isolated fixture: town stone roads, Zigur/Angolwen
crop fields and the Gates of Morning palms.

One cold start per phase, both from packaged TEAAs: `before` = HEAD, `after` =
HEAD plus only the TW7 runtime files (the working tree may hold another
agent's unrelated in-progress files). Six towns are photographed at 48/64 px
at fixed poses (roads beside shops, fields, palms, the Shatur bridge); per
town the TW7 identity census, the full identity probe and the rule digest are
recorded. `after` adds Refined->Native->Refined toggles (four towns) with the
rule digest at each step, and grayscale value pairs (road/field/palm against
their neighbours). Both phases end with a regression pass: the remaining
towns, Dreadfell L1 (a dungeon) and Eruan L1 (S6 palms).

The fixture is shared: before each launch the recorded game/Xvfb pids in
session/processes.json are checked via /proc/<pid>/cmdline and the tool waits
while they are alive; it never stops a process it did not start. Screenshots
stay local under evidence/terrain-tw7-20260930/screenshots/.
"""
import argparse, json, statistics, subprocess, sys, zipfile
from pathlib import Path
from PIL import Image, ImageStat
from capture_korpul import Fixture, HOME, ROOT, SESSION, digest, png_size
from run_norgos_validation import stop_started
from run_tw2_validation import launch, read, luminance
import run_tw2_validation as tw2

OUT = ROOT / 'evidence/terrain-tw7-20260930'
SHOTS = OUT / 'screenshots'
tw2.SHOTS = SHOTS
TW7_FILES = ['overload/mod/class/CheckerTerrain.lua'] + [f'data/gfx/refined/town/{k}{p}.png' for k in ('road', 'fields') for p in (0, 1)]
# (label, zone, [(pose, (cx, cy, sx, sy) or centroid pattern)]) on the static maps.
TOWNS = [
    ('derth', 'town-derth', [('shops', (26, 28, 24, 26)), ('crossroads', (21, 21, 20, 20))]),
    ('lasthope', 'town-last-hope', [('shops', (20, 13, 18, 14)), ('plaza', (32, 15, 33, 15))]),
    ('zigur', 'town-zigur', [('fields', (43, 40, 40, 40)), ('road', (18, 14, 16, 14))]),
    ('angolwen', 'town-angolwen', [('fields', '^FIELDS%d$'), ('shops', '^HARDWALL')]),
    ('gates', 'town-gates-of-morning', [('palms', (37, 39, 38, 37)), ('shops', (36, 15, 37, 13))]),
    ('shatur', 'town-shatur', [('bridge', (25, 21, 25, 24))]),
]
TOGGLE = {('derth', 'shops'), ('zigur', 'fields'), ('angolwen', 'fields'), ('gates', 'palms')}
REGRESSION = [('lumberjack', 'town-lumberjack-village', 1), ('elvala', 'town-elvala', 1), ('council', 'town-iron-council', 1),
              ('pointzero', 'town-point-zero', 1), ('irkkk', 'town-irkkk', 1), ('dreadfell', 'dreadfell', 1), ('eruan', 'eruan', 1)]


def gray_pairs(frame, data):
    """Grayscale median of the 40% centre crop per cell, grouped by family pair."""
    im = Image.open(SHOTS / frame).convert('L')
    s = data['tile']

    def cell(sx, sy):
        return ImageStat.Stat(im.crop((int(sx + s * .3), int(sy + s * .3), int(sx + s * .7), int(sy + s * .7)))).mean[0]

    groups = {}
    for p in data['pairs']:
        f, w = p['floor'], p['wall']
        groups.setdefault(f'{f[4]}|{w[4]}', []).append((cell(f[2], f[3]), cell(w[2], w[3])))
    out = {}
    for k, v in sorted(groups.items()):
        a = statistics.median(x for x, _ in v)
        b = statistics.median(y for _, y in v)
        out[k] = {'n': len(v), 'subject': round(a, 1), 'neighbour': round(b, 1), 'relative': round((a - b) / a, 4) if a else None}
    return out


def run(phase, teaa):
    f = Fixture()
    SHOTS.mkdir(parents=True, exist_ok=True)
    plan = json.loads((SESSION / 'launch-plan.json').read_text())
    assert plan['fixture'] and plan['shaders'] and plan['terrain'] == 'refined'
    if phase == 'after':
        with zipfile.ZipFile(teaa) as z:
            for rel in TW7_FILES:
                assert z.read(rel) == (ROOT / rel).read_bytes(), rel

    def dump(code, name):
        f.lua(f"ms.dump('/{name}',{code})")
        return read(name)

    def size(tile, x, y):
        f.lua(f"game:setResolution('1920x1080 Windowed',true);config.settings.tome.gfx.size='{tile}x{tile}';"
              f"game:setupDisplayMode(false)")
        return dump(f'tw.view({x},{y})', 'tw-view.json')

    def shot(tag):
        name = f'tw7-{tag}'
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
            fr['gray_pairs'] = gray_pairs(Path(fr['file']).name, dump('tw.pairs()', 'tw-pairs.json'))
        return fr

    result = {'phase': phase, 'teaa': str(teaa), 'teaa_sha256': digest(Path(teaa)), 'towns': {}}
    try:
        f.lua("assert(config.settings.cheat and config.settings.disable_all_connectivity and not profile.auth);"
              "assert(core.shader.active(4));tw=dofile('/data-checker-fixture/monster-live_tw7_scene.lua');ms=tw.ms;ms.setup();"
              "tc=dofile('/data-checker-fixture/monster-live_terrain_census.lua');"
              "config.settings.tome.weather_effects=false")
        for label, zone, poses in TOWNS:
            row = {'zone': zone, 'screenshots': [], 'poses': {}}
            result['towns'][label] = row
            row['enter'] = dump(f"ms.enter('{zone}',1)", 'tw-enter.json')
            f.lua('ms.caveClearDialogs()')
            row['quiet'] = dump('tw.quiet()', 'tw-quiet.json')
            row['rules_before'] = dump('tw.rules()', 'tw-rules.json')
            row['probe_natural'] = dump('tw.probe()', 'tw-probe.json')
            row['tw7_natural'] = dump('tw.tw7()', 'tw-tw7.json')
            for kind, where in poses:
                if isinstance(where, str):
                    c = dump(f"tw.centroid('{where}')", 'tw-centroid.json')
                    assert c['n'] > 0, (label, where)
                    where = (c['x'], c['y'], c['x'], c['y'] + 1)
                cx, cy, sx, sy = where
                row['poses'][kind] = dump(f"tw.poseAt({cx},{cy},{sx},{sy},'{kind}')", 'tw-pose.json')
                for tile in (48, 64):
                    row['screenshots'].append(photo(tile, f'{label}-{kind}', cx, cy, pairs=tile == 64))
                if phase == 'after' and (label, kind) in TOGGLE:
                    row.setdefault('particles_paused', {})[kind] = dump('tw.pauseParticles(true)', 'tw-pause.json')
                    before = photo(64, f'{label}-{kind}-toggle-refined', cx, cy)
                    rb = dump('tw.rules()', 'tw-rules-t0.json')
                    f.lua("ms.setMode('vanilla')")
                    native = photo(64, f'{label}-{kind}-toggle-native', cx, cy)
                    rn = dump('tw.rules()', 'tw-rules-t1.json')
                    row.setdefault('native_tw7', {})[kind] = dump('tw.tw7()', 'tw-tw7-native.json')
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
            assert row['rules_before'] == row['rules_after'], (label, row['rules_before'], row['rules_after'])
            row['probe_end'] = dump('tw.probe()', 'tw-probe-end.json')['totals']
            row['tw7_end'] = dump('tw.tw7()', 'tw-tw7-end.json')
            census = dump("game.checker_mode=='refined' and tc.census() or {skipped=tostring(game.checker_mode)}", 'tw-census.json')
            row['census_forced'] = {k: census.get(k) for k in ('total', 'converted', 'native', 'converted_stone', 'converted_forest', 'skipped')}
        reg = result['regression'] = {}
        for label, zone, level in REGRESSION:
            r = reg[label] = {'zone': zone}
            r['enter'] = dump(f"ms.enter('{zone}',{level})", 'tw-enter.json')
            f.lua('ms.caveClearDialogs()')
            r['probe_natural'] = dump('tw.probe()', 'tw-probe.json')['totals']
            r['tw7'] = dump('tw.tw7()', 'tw-tw7.json')
            r['images'] = dump('tw.imageHist()', 'tw-hist.json')
            census = dump("game.checker_mode=='refined' and tc.census() or {skipped=tostring(game.checker_mode)}", 'tw-census.json')
            r['census_forced'] = {k: census.get(k) for k in ('total', 'converted', 'native', 'converted_stone', 'converted_forest', 'skipped')}
            if label in ('dreadfell', 'eruan'):
                f.lua(f"tw.poseAt(game.player.x,game.player.y,game.player.x,game.player.y,'{label}')")
                r['screenshot'] = photo(64, f'reg-{label}', 'game.player.x', 'game.player.y')
        return result
    finally:
        (OUT / f'validation-{phase}.txt').write_text((''.join(f.transcript) + f.new_log()).rstrip() + '\n')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('phase', choices=('after', 'before'))
    p.add_argument('--teaa', required=True, help='TEAA to install (HEAD for before, HEAD+TW7 files for after)')
    a = p.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / 'scenes.json'
    survey = json.loads(path.read_text()) if path.exists() else {}
    meta = launch(a.teaa)
    try:
        result = run(a.phase, a.teaa)
        result['launch_plan'] = json.loads((SESSION / 'launch-plan.json').read_text())
        survey[a.phase] = result
        path.write_text(json.dumps(survey, ensure_ascii=False, indent=1) + '\n')
        print('PASS', a.phase, flush=True)
    finally:
        stop_started(meta)
        print('STOP', a.phase, flush=True)


if __name__ == '__main__':
    main()
