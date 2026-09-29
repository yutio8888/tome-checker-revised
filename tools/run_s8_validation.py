#!/usr/bin/env python3
"""S8 live check in the isolated fixture: the darker diggable-wall set for the
Kor'Pul stone family (V2) and the Fearscape rock (V7).

One cold start per run. `before` installs a TEAA built from HEAD
(--before-teaa); `after` installs HEAD plus exactly the S8 files
(--after-teaa; the runner checks the package bytes against the working tree,
so the concurrent monster batch's unfinished files are never loaded). Every
level is entered with the fixture's ms.enter after `rng.seed(<fixed>)`, so a
static or seeded level can be compared across the two processes.

Per level: identity counts (diggable WALL / HARDWALL / doors / stairs), rule
digest, a 'wall' pose (floor next to diggable wall) photographed at 64px
(before) or 48/64px (after) with lit-pixel pairs at 64px, plus 'door' and
'stairs' poses in the after phase. Selected levels get a Refined->Native->
Refined toggle with the rule digest in each state. Regression levels
(Conclave, Dreadfell, Derth ...) are photographed at fixed seeds in both
phases for a byte comparison.

The fixture is shared: before each launch the recorded game/Xvfb pids in
session/processes.json are checked via /proc/<pid>/cmdline and the tool waits
while they are alive; it never stops a process it did not start. Screenshots
stay local under evidence/terrain-s8-20260929/screenshots/.
"""
import argparse, json, statistics, subprocess, sys, zipfile
from pathlib import Path
from PIL import Image, ImageStat
from capture_korpul import Fixture, HOME, ROOT, SESSION, digest, png_size
from run_norgos_validation import stop_started
from run_tw2_validation import launch, read
import run_tw2_validation as tw2

OUT = ROOT / 'evidence/terrain-s8-20260929'
SHOTS = OUT / 'screenshots'
tw2.SHOTS = SHOTS
SEED = 8208
PARTIAL = {}


def L(zone, levels, opts=None, label=None):
    return [((label or zone) + str(n), zone, n, opts or {}) for n in levels]


# Every zone the stone adapter or the scorch family covers that can place a
# diggable WALL (or the Fearscape rock). Layout options follow ms.enter.
LEVELS = (L('ruins-kor-pul', (1, 2, 3), {'hideout': False}, 'korpul') + L('ruins-kor-pul', (1,), {'hideout': True}, 'korpulhide') +
          L('rhaloren-camp', (1, 2, 3), {'overground': False}, 'rhaloren') + L('dreadfell', (1, 2, 3, 5, 9)) +
          L('thieves-tunnels', (1, 2), label='thieves') + L('halfling-ruins', (1, 2, 3, 4), label='halfling') +
          L('reknor', (1, 2, 3, 4)) + L('reknor-escape', (1, 2, 3), label='rescape') +
          L('temporal-rift', (1, 2, 3, 4), label='rift') + L('ruined-dungeon', (1,), label='ruined') +
          L('blighted-ruins', (1, 2, 3), label='blighted') + L('last-hope-graveyard', (1, 2), label='graveyard') +
          L('lake-nur', (1, 2, 3), {'flooded': False}, 'nur') + L('crypt-kryl-feijan', (1, 2, 3, 4, 5), label='kryl') +
          L('conclave-vault', (1, 2, 3, 4), label='conclave') + L('telmur', (1, 2, 3, 4, 5)) +
          L('ancient-elven-ruins', (1, 2, 3), label='elven') + L('vor-armoury', (1, 2), label='vor') +
          L('orc-breeding-pit', (1,), label='orcpit') + L('charred-scar', (1,), label='charred') +
          L('shertul-fortress', (1,), label='shertul') + L('demon-plane', (1,), label='demon') +
          L('old-forest', (1, 2, 3, 4), {'crystaline': False}, 'oldforest') + L('trollmire', (1, 2, 3), {'flooded': False}) +
          L('daikara', (1, 2, 3, 4), {'volcano': False}) + L('tempest-peak', (1, 2), label='tempest') +
          L('scintillating-caves', (1, 2, 3, 4, 5), {'twisted': True}, 'scint') +
          L('shadow-crypt', (1, 2, 3), label='crypt') + L('tannen-tower', (1, 2, 3, 4), label='tannen') +
          L('ring-of-blood', (1, 2, 3), label='blood') + L('arena-unlock', (1,), label='arena') +
          L('gorbat-pride', (1, 2, 3), label='gorbat') + L('eruan', (1, 2, 3)) +
          [(t.replace('town-', '').replace('-village', '').replace('-of-morning', ''), t, 1, {}) for t in (
              'town-derth', 'town-lumberjack-village', 'town-last-hope', 'town-elvala', 'town-zigur', 'town-angolwen',
              'town-iron-council', 'town-point-zero', 'town-gates-of-morning')])
# Unaffected levels photographed at a fixed seed in both phases (byte check).
REGRESS = {'conclave1', 'conclave2', 'charred1', 'derth', 'last-hope', 'zigur', 'point-zero', 'graveyard2', 'blood3'}
TOGGLE = {'telmur1', 'lumberjack', 'reknor1', 'crypt1', 'demon1'}
S8_FILES = ['overload/mod/class/CheckerTerrain.lua', 'data/terrain-korpul-dark-manifest.lua',
            'data/terrain-scorch-dark-manifest.lua'] + \
    sorted(p.relative_to(ROOT).as_posix() for p in (ROOT / 'data/gfx/refined/korpul-dark').glob('*.png')) + \
    sorted(p.relative_to(ROOT).as_posix() for p in (ROOT / 'data/gfx/refined/scorch-dark').glob('*.png'))


def lua_opts(opts):
    return '{' + ','.join(f"{k}={'true' if v else 'false'}" for k, v in opts.items()) + '}'


def summarize(frame, data):
    """Median 40% centre crop per cell, per blocking family and per floor family."""
    im = Image.open(SHOTS / frame).convert('L')
    s = data['tile']

    def cell(sx, sy):
        return ImageStat.Stat(im.crop((int(sx + s * .3), int(sy + s * .3), int(sx + s * .7), int(sy + s * .7)))).mean[0]

    by = {}
    for p in data['pairs']:
        f, w = p['floor'], p['wall']
        by.setdefault(w[4], []).append((f[4], cell(f[2], f[3]), cell(w[2], w[3])))
    out = {}
    for wall, rows in sorted(by.items()):
        fl = statistics.median(r[1] for r in rows)
        wl = statistics.median(r[2] for r in rows)
        floors = {}
        for r in rows:
            floors[r[0]] = floors.get(r[0], 0) + 1
        out[wall] = {'pairs': len(rows), 'floor': round(fl, 1), 'wall': round(wl, 1),
                     'gap': round((fl - wl) / fl, 4) if fl else None, 'floors': floors}
    return out


def run(phase, only=None, shots=True):
    f = Fixture()
    SHOTS.mkdir(parents=True, exist_ok=True)
    plan = json.loads((SESSION / 'launch-plan.json').read_text())
    assert plan['fixture'] and plan['shaders'] and plan['terrain'] == 'refined'
    teaa = plan.get('teaa', {}).get('checker-revised')
    assert teaa, 'both phases run a packaged TEAA'
    if phase == 'after':
        with zipfile.ZipFile(teaa) as z:
            names = set(z.namelist())
            for rel in S8_FILES:
                assert z.read(rel) == (ROOT / rel).read_bytes(), rel
            assert not any(n.startswith('tests/') for n in names)

    def dump(code, name):
        f.lua(f"ms.dump('/{name}',{code})")
        return read(name)

    def size(tile, x, y):
        f.lua(f"game:setResolution('1920x1080 Windowed',true);config.settings.tome.gfx.size='{tile}x{tile}';"
              f"game:setupDisplayMode(false)")
        return dump(f'tw.view({x},{y})', 's8-view.json')

    def shot(tag):
        name = f's8-{tag}'
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
        if pairs:
            fr['lit'] = summarize(Path(fr['file']).name, dump('tw.pairs()', 's8-pairs.json'))
        return fr

    result = PARTIAL
    result.update({'phase': phase, 'seed': SEED, 'levels': {}})
    try:
        f.lua("assert(config.settings.cheat and config.settings.disable_all_connectivity and not profile.auth);"
              "assert(core.shader.active(4));tw=dofile('/data-checker-fixture/monster-live_s8_scene.lua');ms=tw.ms;ms.setup();"
              "config.settings.tome.weather_effects=false")
        for label, zone, level, opts in LEVELS:
            if only and label not in only:
                continue
            row = {'zone': zone, 'level': level, 'opts': opts, 'screenshots': [], 'poses': {}}
            result['levels'][label] = row
            f.lua(f'rng.seed({SEED})')
            row['enter'] = dump(f"ms.enter('{zone}',{level},{lua_opts(opts)})", 's8-enter.json')
            f.lua('ms.caveClearDialogs()')
            row['quiet'] = dump('tw.quiet()', 's8-quiet.json')
            row['rules_before'] = dump('tw.rules()', 's8-rules.json')
            row['kinds'] = dump('tw.kinds()', 's8-kinds.json')
            wall_ids = (row['kinds']['kinds'] or {}).get('wall', 0) if isinstance(row['kinds']['kinds'], dict) else 0
            wanted = ['scorch'] if zone == 'demon-plane' else (['wall', 'door', 'stairs'] if phase == 'after' else ['wall', 'door'])
            for kind in wanted:
                if kind != 'scorch' and not wall_ids:
                    break
                pick = dump(f"tw.pick('{kind}')", 's8-pick.json')
                if not pick.get('found'):
                    row['poses'][kind] = pick
                    continue
                cx, cy = pick['x'], pick['y']
                row['poses'][kind] = dict(pick, pose=dump(f"tw.poseAt({cx},{cy},{cx},{cy},'{kind}')", 's8-pose.json'))
                if not shots:
                    continue
                tiles = (48, 64) if phase == 'after' else (64,)
                for tile in tiles:
                    row['screenshots'].append(photo(tile, f'{label}-{kind}', cx, cy, pairs=tile == 64))
                row['kinds_after_pose'] = dump('tw.kinds()', 's8-kinds.json')
                if phase == 'after' and label in TOGGLE and kind in ('wall', 'scorch'):
                    dump('tw.pauseParticles(true)', 's8-pause.json')
                    dump('tw.clearLog()', 's8-log.json')
                    before = photo(64, f'{label}-{kind}-toggle-refined', cx, cy)
                    rb = dump('tw.rules()', 's8-rules-t0.json')
                    f.lua("ms.setMode('vanilla')")
                    native = photo(64, f'{label}-{kind}-toggle-native', cx, cy)
                    rn = dump('tw.rules()', 's8-rules-t1.json')
                    f.lua("ms.setMode('refined')")
                    after = photo(64, f'{label}-{kind}-toggle-restored', cx, cy)
                    ra = dump('tw.rules()', 's8-rules-t2.json')
                    # Same layout without the S8 set (fixture-only manifest
                    # gate), then with it again.
                    nodark = dump('tw.darkSet(false)', 's8-dark.json')
                    old = photo(64, f'{label}-{kind}-toggle-nodark', cx, cy, pairs=True)
                    redark = dump('tw.darkSet(true)', 's8-dark.json')
                    again = photo(64, f'{label}-{kind}-toggle-dark-again', cx, cy)
                    dump('tw.pauseParticles(false)', 's8-pause.json')
                    row.setdefault('toggle', {})[kind] = {
                        'refined': before, 'native': native, 'restored': after, 'nodark': old, 'dark_again': again,
                        'dark_switch': [nodark, redark],
                        'restored_vs_refined': tw2.diff(before, after), 'native_vs_refined': tw2.diff(before, native),
                        'nodark_vs_refined': tw2.diff(before, old), 'dark_again_vs_refined': tw2.diff(before, again),
                        'rules': [rb, rn, ra], 'rules_equal': rb == rn == ra}
                    row['screenshots'] += [before, native, after, old, again]
            if label in REGRESS and shots:
                px, py = row['enter']['player_x'], row['enter']['player_y']
                row['poses']['start'] = dump(f"tw.poseAt({px},{py},{px},{py},'start')", 's8-pose.json')
                dump('tw.pauseParticles(true)', 's8-pause.json')
                dump('tw.clearLog()', 's8-log.json')
                row['screenshots'].append(photo(64, f'{label}-start', px, py))
                dump('tw.pauseParticles(false)', 's8-pause.json')
            row['rules_after'] = dump('tw.rules()', 's8-rules-after.json')
            assert row['rules_before'] == row['rules_after'], (label, row['rules_before'], row['rules_after'])
        return result
    finally:
        (OUT / (f'validation-{phase}' + (('-' + '-'.join(only))[:80] if only else '') + '.txt')).write_text(
            (''.join(f.transcript) + f.new_log()).rstrip() + '\n')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('phase', choices=('after', 'before', 'survey'))
    p.add_argument('--teaa', required=True, help='before: HEAD TEAA; after/survey: HEAD plus the S8 files')
    p.add_argument('--only', nargs='*')
    a = p.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / 'scenes.json'
    survey = json.loads(path.read_text()) if path.exists() else {}
    meta = launch(a.teaa)
    try:
        phase = 'after' if a.phase == 'survey' else a.phase
        try:
            result = run(phase, only=a.only, shots=a.phase != 'survey')
        except Exception as e:
            # Keep what was measured; the failing level is recorded.
            result = PARTIAL
            result['error'] = repr(e)[:4000]
        result['launch_plan'] = json.loads((SESSION / 'launch-plan.json').read_text())
        if a.only and a.phase in survey:
            prev = survey[a.phase]
            prev.setdefault('reruns', []).append({'only': a.only, 'launch_plan': result['launch_plan']})
            prev['levels'].update(result['levels'])
        else:
            survey[a.phase] = result
        path.write_text(json.dumps(survey, ensure_ascii=False, indent=1) + '\n')
        print('ERROR' if result.get('error') else 'PASS', a.phase, flush=True)
    finally:
        stop_started(meta)
        print('STOP', a.phase, flush=True)


if __name__ == '__main__':
    main()
