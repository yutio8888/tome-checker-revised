#!/usr/bin/env python3
"""Multi-zone terrain/actor coverage survey in the running isolated fixture.

This is a driver, not a launcher. Start a fresh fixture first, e.g.:
  launch_fixture.py --shaders --tiles 64 --terrain refined --resolution 1920x1080 \
    --birth "Human:Cornac:Male:Berserker"
It jumps the frozen, invulnerable player across many zones with native
game:changeLevel, censuses terrain/actor coverage via tests/live_map_survey.lua,
and takes one unedited 1920x1080 screenshot per zone. Output goes only to
evidence/map-survey-20260928.
"""
import csv
import json
import shutil
import subprocess
import sys
from pathlib import Path

from capture_korpul import Fixture, HOME, ROOT, SESSION, digest, png_size

OUT = ROOT / 'evidence/map-survey-20260928'
SHOTS = OUT / 'screenshots'
SCENE = 'live_map_survey'

# (short_name, level, opts-or-None, label, expect) expect in {'painted','native'}
ZONES = [
    ('trollmire', 1, None, 'trollmire-L1', 'painted'),
    ('trollmire', 3, None, 'trollmire-L3', 'painted'),
    # F1 (0.6.14): FLOODED Trollmire is now painted too, same as DEFAULT;
    # dedicated F1 evidence lives in evidence/runtime-v0614 (capture_runtime_v0614.py).
    ('trollmire', 1, {'flooded': True}, 'trollmire-L1-flooded', 'painted'),
    ('ruins-kor-pul', 1, {'hideout': False}, 'korpul-L1-default', 'painted'),
    ('ruins-kor-pul', 1, {'hideout': True}, 'korpul-L1-hideout', 'painted'),
    ('norgos-lair', 1, None, 'norgos-lair-L1', 'native'),
    ('old-forest', 1, None, 'old-forest-L1', 'native'),
    ('maze', 1, None, 'maze-L1', 'native'),
    ('sandworm-lair', 1, None, 'sandworm-lair-L1', 'native'),
    ('rhaloren-camp', 1, None, 'rhaloren-camp-L1', 'native'),
    ('scintillating-caves', 1, None, 'scintillating-caves-L1', 'native'),
    ('heart-gloom', 1, None, 'heart-gloom-L1', 'native'),
    ('daikara', 1, None, 'daikara-L1', 'native'),
    ('town-derth', 1, None, 'town-derth-L1', 'native'),
    ('wilderness', 1, None, 'wilderness-L1', 'native'),
    ('dreadfell', 1, None, 'dreadfell-L1', 'native'),
    ('unremarkable-cave', 1, None, 'unremarkable-cave-L1', 'native'),
    ('ancient-elven-ruins', 1, None, 'ancient-elven-ruins-L1', 'native'),
]


def lua_opts(opts):
    if not opts:
        return 'nil'
    parts = []
    for k, v in opts.items():
        parts.append(f"{k}={'true' if v else 'false'}")
    return '{' + ','.join(parts) + '}'


def read_json(name):
    path = HOME / name
    data = json.loads(path.read_text())
    path.unlink(missing_ok=True)
    return data


def main():
    fixture = Fixture()
    SHOTS.mkdir(parents=True, exist_ok=True)
    plan = json.loads((SESSION / 'launch-plan.json').read_text())
    assert plan.get('fixture') and plan.get('shaders') and plan.get('resolution') == '1920x1080', \
        'requires the offline fixture with shaders at 1920x1080'
    installed = SESSION / f'runtime/game/addons/tome-checker-fixture/data/monster-{SCENE}.lua'
    assert digest(installed) == digest(ROOT / f'tests/{SCENE}.lua'), \
        'fixture scene differs from the repository copy; relaunch'
    for rel in ('overload/mod/class/CheckerTerrain.lua', 'overload/mod/class/CheckerTokens.lua',
                'superload/mod/class/Game.lua', 'superload/engine/Map.lua'):
        copy = SESSION / 'runtime/game/addons/tome-checker-revised' / rel
        assert digest(copy) == digest(ROOT / rel), f'installed {rel} differs from the repository copy; relaunch'

    result = {'zones': [], 'launch': plan, 'scene_sha256': digest(ROOT / f'tests/{SCENE}.lua'), 'complete': False}

    def save():
        (OUT / 'survey.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
        (OUT / 'validation-transcript.txt').write_text((''.join(fixture.transcript) + fixture.new_log()).rstrip() + '\n')

    def shot(name):
        source = HOME / (name + '.png')
        source.unlink(missing_ok=True)
        capture = subprocess.run([sys.executable, str(ROOT / 'tools/fixture_command.py'), 'shot', name],
                                  capture_output=True, text=True, timeout=25)
        fixture.transcript.append(capture.stdout + capture.stderr)
        fixture.check_log()
        assert capture.returncode == 0 and source.is_file() and png_size(source) == (1920, 1080), name
        target = SHOTS / source.name
        shutil.copy2(source, target)
        return {'file': 'screenshots/' + target.name, 'sha256': digest(target), 'resolution': [1920, 1080]}

    try:
        fixture.lua("assert(config.settings.cheat and config.settings.disable_all_connectivity and not profile.auth);"
                    "assert(core.shader.active(4));"
                    "ms=dofile('/data-checker-fixture/monster-live_map_survey.lua');ms.setup()")
        for short_name, level, opts, label, expect in ZONES:
            code = (f"local enter=ms.enter({short_name!r},{level},{lua_opts(opts)});"
                    "local terrain=ms.terrainCensus();local actors=ms.actorCensus();"
                    "ms.dump('/ms-result.json',{enter=enter,terrain=terrain,actors=actors})")
            fixture.lua(code)
            data = read_json('ms-result.json')
            shot_info = shot('map-survey-' + label)
            entry = {'label': label, 'short_name': short_name, 'level': level, 'opts': opts,
                     'expect': expect, 'enter': data['enter'], 'terrain': data['terrain'],
                     'actors': data['actors'], 'screenshot': shot_info}
            if expect == 'painted':
                fixture.lua("ms.setMode('vanilla');local v=ms.terrainCensus();"
                            "ms.setMode('refined');local r=ms.terrainCensus();"
                            "ms.dump('/ms-modecheck.json',{vanilla=v,refined=r})")
                mode_data = read_json('ms-modecheck.json')
                entry['mode_round_trip'] = mode_data
            result['zones'].append(entry)
            save()
            print('OK', label, 'terrain=', data['terrain'].get('supported'), data['terrain'].get('owned'),
                  data['terrain'].get('native'), 'actors=', len(data['actors']['actors']))
        result['complete'] = True
        save()
        print('PASS', len(result['zones']), 'zones surveyed')
    finally:
        save()


if __name__ == '__main__':
    main()
