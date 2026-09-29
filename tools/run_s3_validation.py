#!/usr/bin/env python3
"""S3 live check in the isolated fixture: Old Forest crystal patch boundary,
forest-zone stone rooms, Old Forest LAKE_NUR exit. One cold start per scene;
every process started here is stopped. Screenshots stay local under
evidence/terrain-s3-20260929/screenshots/ (listed in scenes.json)."""
import argparse, json, shutil, statistics, subprocess, sys, time
from pathlib import Path
from PIL import Image, ImageChops, ImageStat
from capture_korpul import Fixture, HOME, ROOT, SESSION, digest, png_size
from run_norgos_validation import stop_started

OUT = ROOT / 'evidence/terrain-s3-20260929'
SHOTS = OUT / 'screenshots'
# (label, zone, level, opts, poses)
SCENES = [
    ('oldforest-crystaline-L2', 'old-forest', 2, '{crystaline=true}', ['crystal', 'stone']),
    ('oldforest-crystaline-L4', 'old-forest', 4, '{crystaline=true}', ['crystal', 'exit']),
    ('oldforest-default-L4', 'old-forest', 4, '{crystaline=false}', ['stone', 'exit']),
    ('trollmire-default-L1', 'trollmire', 1, '{flooded=false}', ['stone']),
    ('trollmire-flooded-L2', 'trollmire', 2, '{flooded=true}', ['stone']),
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


def capture(label, zone, level, opts, poses):
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
              f"game:setupDisplayMode(false);s3.stage({x},{y})")

    def shot(tile, tag):
        name = f's3-{label}-{tag}-{tile}'
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

    row = {'label': label, 'zone': zone, 'level': level, 'opts': opts, 'poses': {}, 'screenshots': []}
    try:
        f.lua("assert(config.settings.cheat and config.settings.disable_all_connectivity and not profile.auth);"
              "assert(core.shader.active(4));s3=dofile('/data-checker-fixture/monster-live_s3_scene.lua');ms=s3.ms;ms.setup();"
              # Fixture-only: no rain/cloud particles so toggle frames compare terrain.
              "config.settings.tome.weather_effects=false")
        row['enter'] = dump(f"ms.enter('{zone}',{level},{opts})", 's3-enter.json')
        f.lua('ms.caveClearDialogs()')
        row['counts'] = dump('s3.counts()', 's3-counts.json')
        # Random maps: regenerate (fixture-only) until the photographed feature exists.
        row['regenerated'] = 0
        need = 'stone_records' if 'stone' in poses else 'crystal_owned'
        while row['counts'][need] == 0 and row['regenerated'] < 8:
            row['regenerated'] += 1
            row['enter'] = dump(f"ms.enter('{zone}',{level},{opts})", 's3-enter.json')
            f.lua('ms.caveClearDialogs()')
            row['counts'] = dump('s3.counts()', 's3-counts.json')
            time.sleep(4)
        row['rules_before'] = dump('s3.rules()', 's3-rules.json')
        for kind in poses:
            pose = dump(f"s3.pose('{kind}')", 's3-pose.json')
            row['poses'][kind] = {'pose': pose}
            if not pose.get('found'):
                continue
            x, y = pose['x'], pose['y']
            for tile in (48, 64):
                size(tile, x, y)
                frame = shot(tile, kind)
                samples = dump('s3.samples()', 's3-samples.json')
                frame['luminance'] = luminance(Path(frame['file']).name, samples)
                row['screenshots'].append(frame)
            if kind == poses[0]:
                # Refined -> Native -> Refined at 64px on the same view.
                size(64, x, y)
                before = shot(64, kind + '-toggle-refined')
                f.lua("ms.setMode('vanilla')");size(64, x, y)
                native = shot(64, kind + '-toggle-native')
                row['native_counts'] = dump('s3.counts()', 's3-counts-native.json')
                f.lua("ms.setMode('refined')");size(64, x, y)
                after = shot(64, kind + '-toggle-restored')
                row['restored_counts'] = dump('s3.counts()', 's3-counts-restored.json')
                a = Image.open(SHOTS / Path(before['file']).name).convert('RGB')
                b = Image.open(SHOTS / Path(after['file']).name).convert('RGB')
                n = Image.open(SHOTS / Path(native['file']).name).convert('RGB')
                def changed(x, y):
                    d = ImageChops.difference(x, y).convert('L')
                    hist = d.histogram()
                    total = sum(hist)
                    return {'mean_abs': round(sum(i * c for i, c in enumerate(hist)) / total, 3),
                            'share_gt24': round(sum(hist[25:]) / total, 5)}
                row['toggle'] = {'refined': before, 'native': native, 'restored': after,
                                 'restored_vs_refined': changed(a, b), 'native_vs_refined': changed(a, n)}
                row['screenshots'] += [before, native, after]
        row['rules_after'] = dump('s3.rules()', 's3-rules-after.json')
        assert row['rules_before'] == row['rules_after'], (row['rules_before'], row['rules_after'])
        row['counts_after'] = dump('s3.counts()', 's3-counts-after.json')
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
    for label, zone, level, opts, poses in SCENES:
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
            row = capture(label, zone, level, opts, poses)
            survey['scenes'].append(row)
            path.write_text(json.dumps(survey, ensure_ascii=False, indent=1) + '\n')
            print('PASS', label, row['counts'], row.get('toggle', {}).get('restored_equals_refined'), flush=True)
        finally:
            stop_started(meta)
            print('STOP', label, flush=True)


if __name__ == '__main__':
    main()
