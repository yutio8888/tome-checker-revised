#!/usr/bin/env python3
"""Independent cold-start census and screenshots for second terrain reuse batch."""
import argparse
import json
import shutil
import statistics
import subprocess
import sys
import time
from pathlib import Path

from PIL import Image, ImageStat
from capture_korpul import Fixture, HOME, ROOT, SESSION, digest, png_size
from run_norgos_validation import stop_started

OUT = ROOT / 'evidence/reuse-batch2-20260928'
SHOTS = OUT / 'screenshots'
SCENES = [(zone, level, layout) for zone, maximum, layouts in (
    ('lake-nur', 3, ('DEFAULT', 'FLOODED')),
    ('ruined-dungeon', 1, ('DEFAULT',)),
    ('blighted-ruins', 3, ('DEFAULT',)),
    ('crypt-kryl-feijan', 5, ('DEFAULT',)),
    ('golem-graveyard', 1, ('DEFAULT',)),
    ('ardhungol', 3, ('DEFAULT',)),
) for layout in layouts for level in range(1, maximum + 1)]


def read(name):
    path = HOME / name
    result = json.loads(path.read_text())
    path.unlink()
    return result


def capture(zone, level, layout):
    label = f'{zone}-{layout}-L{level}'
    fixture = Fixture()
    SHOTS.mkdir(parents=True, exist_ok=True)
    plan = json.loads((SESSION / 'launch-plan.json').read_text())
    assert plan['fixture'] and plan['shaders'] and plan['resolution'] == '1920x1080'
    assert digest(SESSION / 'runtime/game/addons/tome-checker-revised/overload/mod/class/CheckerTerrain.lua') == digest(ROOT / 'overload/mod/class/CheckerTerrain.lua')
    assert digest(SESSION / 'runtime/game/addons/tome-checker-fixture/data/monster-live_map_survey.lua') == digest(ROOT / 'tests/live_map_survey.lua')
    fixture.lua("assert(config.settings.cheat and config.settings.disable_all_connectivity and not profile.auth);assert(core.shader.active(4));ms=dofile('/data-checker-fixture/monster-live_map_survey.lua');ms.setup()")

    def dump(code, name):
        fixture.lua(f"ms.dump('/{name}',{code})")
        return read(name)

    def shot(tile, tag):
        name = f'{label}-{tag}-{tile}'
        source = HOME / (name + '.png')
        source.unlink(missing_ok=True)
        result = subprocess.run([sys.executable, str(ROOT / 'tools/fixture_command.py'), 'shot', name], capture_output=True, text=True, timeout=35)
        fixture.transcript.append(result.stdout + result.stderr)
        fixture.check_log()
        assert result.returncode == 0 and source.is_file() and png_size(source) == (1920, 1080), result.stdout + result.stderr
        target = SHOTS / source.name
        shutil.copy2(source, target)
        return {'file': 'screenshots/' + target.name, 'sha256': digest(target), 'tile': tile}

    entry = {'zone': zone, 'level': level, 'layout': layout, 'label': label, 'launch': plan, 'screenshots': []}
    entry['enter'] = dump(f"ms.enter('{zone}',{level},{{flooded={str(layout=='FLOODED').lower()}}})" if zone=='lake-nur' else f"ms.enter('{zone}',{level})", 'reuse-enter.json')
    assert entry['enter']['zone'] == zone and entry['enter']['level'] == level
    entry['census'] = dump('ms.terrainCensus()', 'reuse-census.json')
    entry['details'] = dump('ms.reuseDetails()', 'reuse-details.json')
    assert entry['census']['native'] == 0, entry['census']
    pose = dump('ms.reusePose(false)', 'reuse-pose.json')
    assert pose['found'], pose
    entry['open_pose'] = pose
    entry['lit_pairs'] = dump('ms.reuseLitPairs()', 'reuse-lit.json')
    if level == 1:
        natural = shot(64, 'natural')
        entry['screenshots'].append(natural)
        image = Image.open(SHOTS / Path(natural['file']).name).convert('L')
        values = []
        for pair in entry['lit_pairs']['pairs']:
            def mean(cell):
                x, y, size = cell['sx'], cell['sy'], entry['lit_pairs']['tile']
                return ImageStat.Stat(image.crop((int(x+size*.3), int(y+size*.3), int(x+size*.7), int(y+size*.7)))).mean[0]
            values.append({'floor': mean(pair['floor']), 'wall': mean(pair['wall'])})
        if values:
            floor = statistics.median(v['floor'] for v in values)
            wall = statistics.median(v['wall'] for v in values)
            entry['lit_pixel_check'] = {'pairs': len(values), 'floor_median': floor, 'wall_median': wall,
                                        'relative_gap': (floor-wall)/floor if floor else 0,
                                        'screenshot': natural['file'], 'natural_fov': True}
    for tile in ((48, 64, 96) if level == 1 else (64,)):
        fixture.lua(f"game:setResolution('1920x1080 Windowed',true);config.settings.tome.gfx.size='{tile}x{tile}';game:setupDisplayMode(false);ms.focus(game.player.x,game.player.y);ms.reuseStageView()")
        entry['screenshots'].append(shot(tile, 'open'))
    exit_pose = dump('ms.reusePose(true)', 'reuse-exit-pose.json')
    entry['exit_pose'] = exit_pose
    if exit_pose['found'] and exit_pose['exit']:
        fixture.lua("game:setResolution('1920x1080 Windowed',true);config.settings.tome.gfx.size='64x64';game:setupDisplayMode(false);ms.focus(game.player.x,game.player.y);ms.reuseStageView()")
        entry['screenshots'].append(shot(64, 'exit'))
    if level == 1:
        entry['modes'] = dump("(function() ms.setMode('vanilla');local v=ms.terrainCensus();ms.setMode('blockout');local b=ms.terrainCensus();ms.setMode('refined');local r=ms.terrainCensus();return {vanilla=v,blockout=b,refined=r} end)()", 'reuse-modes.json')
        assert entry['modes']['vanilla']['owned'] == 0 and entry['modes']['refined']['native'] == 0
        if zone == 'tempest-peak':
            assert entry['modes']['blockout']['native'] == 0
    (OUT / f'validation-{label}.txt').write_text((''.join(fixture.transcript) + fixture.new_log()).rstrip() + '\n')
    return entry


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--zone')
    parser.add_argument('--level', type=int)
    parser.add_argument('--layout')
    args = parser.parse_args()
    OUT.mkdir(exist_ok=True)
    survey = OUT / 'survey.json'
    result = json.loads(survey.read_text()) if survey.exists() else {'scenes': []}
    for zone, level, layout in SCENES:
        if args.zone and args.zone != zone or args.level and args.level != level or args.layout and args.layout != layout:
            continue
        label = f'{zone}-{layout}-L{level}'
        if any(x['label'] == label for x in result['scenes']):
            continue
        launch = subprocess.run([sys.executable, str(ROOT / 'tools/launch_fixture.py'), '--shaders', '--tiles', '64', '--terrain', 'refined', '--resolution', '1920x1080', '--birth', 'Human:Cornac:Male:Berserker'], cwd=ROOT, capture_output=True, text=True)
        if launch.returncode:
            raise RuntimeError(launch.stdout + launch.stderr)
        meta = json.loads((SESSION / 'processes.json').read_text())
        try:
            for _ in range(180):
                if HOME.is_dir():
                    break
                time.sleep(.5)
            else:
                raise RuntimeError('fixture home missing')
            time.sleep(2)
            print('START', label, flush=True)
            entry = capture(zone, level, layout)
            result['scenes'].append(entry)
            survey.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
            print('OK', label, entry['census'], flush=True)
        finally:
            stop_started(meta)
            print('STOP', label, flush=True)


if __name__ == '__main__':
    main()
