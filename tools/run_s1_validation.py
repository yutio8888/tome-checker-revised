#!/usr/bin/env python3
"""S1 live check in the isolated fixture: native aura circles crossing walls in
a stone zone and in the bone, cave and gloom families. One cold start per
scene; every process started here is stopped. Screenshots stay local under
evidence/terrain-s1-20260929/screenshots/ (listed in scenes.json)."""
import argparse, json, shutil, statistics, subprocess, sys, time
from pathlib import Path
from PIL import Image, ImageChops, ImageStat
from capture_korpul import Fixture, HOME, ROOT, SESSION, digest, png_size
from run_norgos_validation import stop_started

OUT = ROOT / 'evidence/terrain-s1-20260929'
SHOTS = OUT / 'screenshots'
# (label, zone, level, opts)
SCENES = [
    ('blighted-L1', 'blighted-ruins', 1, 'nil'),
    ('rakshor-L1', 'rak-shor-pride', 1, 'nil'),
    ('ardhungol-L1', 'ardhungol', 1, 'nil'),
    ('heartgloom-L1', 'heart-gloom', 1, '{purified=false}'),
]


def read(name):
    p = HOME / name
    value = json.loads(p.read_text())
    p.unlink()
    return value


def luminance(frame, samples):
    im = Image.open(SHOTS / frame).convert('L')
    s = samples['tile']
    fam = {}
    for c in samples['cells']:
        x, y = c['sx'], c['sy']
        v = ImageStat.Stat(im.crop((int(x + s * .3), int(y + s * .3), int(x + s * .7), int(y + s * .7)))).mean[0]
        fam.setdefault(c['family'], []).append(v)
    return {k: {'n': len(v), 'median': round(statistics.median(v), 1)} for k, v in sorted(fam.items())}


def capture(label, zone, level, opts):
    f = Fixture()
    SHOTS.mkdir(parents=True, exist_ok=True)
    plan = json.loads((SESSION / 'launch-plan.json').read_text())
    assert plan['fixture'] and plan['shaders'] and plan['terrain'] == 'refined'
    for rel in ('overload/mod/class/CheckerTerrain.lua', 'superload/mod/class/Grid.lua'):
        assert digest(SESSION / 'runtime/game/addons/tome-checker-revised' / rel) == digest(ROOT / rel), rel

    def dump(code, name):
        f.lua(f"ms.dump('/{name}',{code})")
        return read(name)

    def size(tile, x, y):
        f.lua(f"game:setResolution('1920x1080 Windowed',true);config.settings.tome.gfx.size='{tile}x{tile}';"
              f"game:setupDisplayMode(false);s1.stage({x},{y})")

    def shot(tile, tag):
        name = f's1-{label}-{tag}-{tile}'
        src = HOME / (name + '.png')
        src.unlink(missing_ok=True)
        call = subprocess.run([sys.executable, str(ROOT / 'tools/fixture_command.py'), 'shot', name],
                              capture_output=True, text=True, timeout=35)
        f.transcript.append(call.stdout + call.stderr)
        f.check_log()
        assert call.returncode == 0 and src.is_file() and png_size(src) == (1920, 1080), (call.stdout, call.stderr)
        dst = SHOTS / src.name
        shutil.copy2(src, dst)
        return {'file': 'screenshots/' + dst.name, 'sha256': digest(dst), 'tile': tile, 'tag': tag}

    row = {'label': label, 'zone': zone, 'level': level, 'opts': opts, 'screenshots': []}
    try:
        f.lua("assert(config.settings.cheat and config.settings.disable_all_connectivity and not profile.auth);"
              "assert(core.shader.active(4));s1=dofile('/data-checker-fixture/monster-live_s1_scene.lua');ms=s1.ms;ms.setup();"
              # Fixture-only: no rain/cloud particles so toggle frames compare terrain.
              "config.settings.tome.weather_effects=false")
        row['enter'] = dump(f"ms.enter('{zone}',{level},{opts})", 's1-enter.json')
        f.lua('ms.caveClearDialogs()')
        row['counts'] = dump('s1.counts()', 's1-counts.json')
        # Random maps/events: regenerate (fixture-only) until an aura crosses walls.
        row['regenerated'] = 0
        while row['counts']['ring_blocking'] == 0 and row['regenerated'] < 8:
            row['regenerated'] += 1
            time.sleep(4)
            row['enter'] = dump(f"ms.enter('{zone}',{level},{opts})", 's1-enter.json')
            f.lua('ms.caveClearDialogs()')
            row['counts'] = dump('s1.counts()', 's1-counts.json')
        row['rules_before'] = dump('s1.rules()', 's1-rules.json')
        pose = dump('s1.pose()', 's1-pose.json')
        row['pose'] = pose
        assert pose.get('found'), pose
        x, y = pose['x'], pose['y']
        for tile in (48, 64):
            size(tile, x, y)
            frame = shot(tile, 'aura')
            samples = dump('s1.samples()', 's1-samples.json')
            frame['luminance'] = luminance(Path(frame['file']).name, samples)
            row['screenshots'].append(frame)
        # Refined -> Native -> Refined at 64px on the same view.
        size(64, x, y)
        before = shot(64, 'toggle-refined')
        row['rules_refined'] = dump('s1.rules()', 's1-rules-r.json')
        f.lua("ms.setMode('vanilla')");size(64, x, y)
        native = shot(64, 'toggle-native')
        row['native_counts'] = dump('s1.counts()', 's1-counts-native.json')
        row['rules_native'] = dump('s1.rules()', 's1-rules-n.json')
        f.lua("ms.setMode('refined')");size(64, x, y)
        after = shot(64, 'toggle-restored')
        row['restored_counts'] = dump('s1.counts()', 's1-counts-restored.json')
        a = Image.open(SHOTS / Path(before['file']).name).convert('RGB')
        b = Image.open(SHOTS / Path(after['file']).name).convert('RGB')
        n = Image.open(SHOTS / Path(native['file']).name).convert('RGB')
        def changed(x, y):
            d = ImageChops.difference(x, y).convert('L')
            hist = d.histogram()
            total = sum(hist)
            return {'mean_abs': round(sum(i * c for i, c in enumerate(hist)) / total, 3),
                    'share_gt24': round(sum(hist[25:]) / total, 5),
                    'identical': ImageChops.difference(x, y).getbbox() is None}
        row['toggle'] = {'refined': before, 'native': native, 'restored': after,
                         'restored_vs_refined': changed(a, b), 'native_vs_refined': changed(a, n)}
        row['screenshots'] += [before, native, after]
        row['rules_after'] = dump('s1.rules()', 's1-rules-after.json')
        for k in ('rules_refined', 'rules_native', 'rules_after'):
            assert row['rules_before'] == row[k], (k, row['rules_before'], row[k])
        row['counts_after'] = dump('s1.counts()', 's1-counts-after.json')
        return row
    finally:
        (OUT / f'validation-{label}.txt').write_text((''.join(f.transcript) + f.new_log()).rstrip() + '\n')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--label')
    a = p.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / 'scenes.json'
    survey = json.loads(path.read_text()) if path.exists() else {'scenes': []}
    for label, zone, level, opts in SCENES:
        if a.label and a.label != label:
            continue
        if any(s['label'] == label for s in survey['scenes']):
            continue
        call = subprocess.run([sys.executable, str(ROOT / 'tools/launch_fixture.py'), '--shaders', '--tiles', '64',
                               '--terrain', 'refined', '--resolution', '1920x1080', '--birth', 'Human:Cornac:Male:Berserker'],
                              cwd=ROOT, capture_output=True, text=True)
        if call.returncode:
            raise RuntimeError(call.stdout + call.stderr)
        meta = json.loads((SESSION / 'processes.json').read_text())
        try:
            time.sleep(2)
            row = capture(label, zone, level, opts)
            survey['scenes'].append(row)
            path.write_text(json.dumps(survey, ensure_ascii=False, indent=1) + '\n')
            print('PASS', label, row['counts_after'], row['toggle']['restored_vs_refined'], flush=True)
        finally:
            stop_started(meta)
            print('STOP', label, flush=True)


if __name__ == '__main__':
    main()
