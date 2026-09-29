#!/usr/bin/env python3
"""Norgos snow-rock live driver; launch a fresh isolated fixture per invocation."""
import argparse
import json
import shutil
import subprocess
import sys

from capture_korpul import Fixture, HOME, ROOT, SESSION, digest, png_size

OUT = ROOT / 'evidence/norgos-20260928'
SHOTS = OUT / 'screenshots'
SCENE = 'live_map_survey'

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
    parser = argparse.ArgumentParser()
    parser.add_argument('--layout', choices=('default', 'invaded'), required=True)
    parser.add_argument('--level', type=int, choices=(1, 2, 3), required=True)
    args = parser.parse_args()
    label = f'norgos-L{args.level}-{args.layout}'
    ZONES = [('norgos-lair', args.level, {'invaded': args.layout == 'invaded'},
              label, args.level == 1 and args.layout == 'default', args.level == 1)]
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

    survey_path = OUT / 'survey.json'
    result = json.loads(survey_path.read_text()) if survey_path.exists() else {'zones': []}
    assert not any(z['label'] == label for z in result['zones']), f'already captured: {label}'
    result.update(scene_sha256=digest(ROOT / f'tests/{SCENE}.lua'), complete=False)
    result.setdefault('launches', {})[label] = plan

    def save():
        (OUT / 'survey.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
        with (OUT / f'validation-{label}.txt').open('w') as stream:
            stream.write((''.join(fixture.transcript) + fixture.new_log()).rstrip() + '\n')

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
        for short_name, level, opts, label, dig, full_res in ZONES:
            code = (f"local enter=ms.enter({short_name!r},{level},{lua_opts(opts)});"
                    "local terrain=ms.terrainCensus();local actors=ms.actorCensus();"
                    "local details=ms.norgosDetails();"
                    "ms.dump('/ms-result.json',{enter=enter,terrain=terrain,actors=actors,details=details})")
            fixture.lua(code)
            data = read_json('ms-result.json')
            shots = []
            tiles = (48, 64, 96) if full_res else (64,)
            for tile in tiles:
                fixture.lua("game:setResolution('1920x1080 Windowed',true);"
                            f"config.settings.tome.gfx.size='{tile}x{tile}';game:setupDisplayMode(false);"
                            "ms.focus(game.player.x,game.player.y)")
                info = shot(f'norgos-{label}-{tile}')
                info['tile'] = tile
                shots.append(info)
            fixture.lua("config.settings.tome.gfx.size='64x64';game:setupDisplayMode(false);"
                        "ms.focus(game.player.x,game.player.y)")
            entry = {'label': label, 'short_name': short_name, 'level': level, 'opts': opts,
                     'enter': data['enter'], 'terrain': data['terrain'],
                     'actor_count': len(data['actors']['actors']), 'screenshots': shots,
                     'details': data['details']}
            assert entry['enter']['is_invaded'] == opts['invaded']
            ids = entry['details']['ids']
            assert ids.get('ROCKY_GROUND', {}).get('count', 0) > 0, ids
            assert sum(v['count'] for k, v in ids.items() if k.startswith('ROCKY_SNOWY_TREE')) > 0, ids
            assert ids.get('ROCKY_UP_WILDERNESS' if level == 1 else 'ROCKY_UP6', {}).get('count', 0) > 0, ids
            if level < 3:
                assert ids.get('ROCKY_DOWN4', {}).get('count', 0) > 0, ids
            # Mode round trip: vanilla releases every painted/tracked cell,
            # refined reinstalls it. For the Kor'Pul-variant regression entry
            # this exercises the per-cell adapter's own owned/native fields;
            # for forest zones it exercises applyForest's replace_display.
            fixture.lua("ms.setMode('vanilla');local v=ms.terrainCensus();"
                        "ms.setMode('refined');local r=ms.terrainCensus();"
                        "ms.dump('/ms-modecheck.json',{vanilla=v,refined=r})")
            entry['mode_round_trip'] = read_json('ms-modecheck.json')
            assert entry['terrain']['native'] == 0, f'{label}: expected full painted coverage, got {entry["terrain"]}'
            assert entry['mode_round_trip']['vanilla']['owned'] == 0, f'{label}: vanilla must release every cell'
            assert entry['mode_round_trip']['refined']['native'] == 0, f'{label}: refined must reinstall everything'
            if dig:
                fixture.lua("local d=ms.digTree();ms.dump('/ms-dig.json',d)")
                dig_result = read_json('ms-dig.json')
                entry['dig'] = dig_result
                if dig_result.get('found'):
                    assert dig_result.get('after_owned') is True, dig_result
                    fixture.lua(f"ms.focus({dig_result['x']},{dig_result['y']})")
                    entry['dig']['screenshot'] = shot(f'norgos-{label}-dig-repair-64')
                fixture.lua("local t=ms.terrainCensus();ms.dump('/ms-postdig.json',t)")
                entry['post_dig_terrain'] = read_json('ms-postdig.json')
                assert entry['post_dig_terrain']['native'] == 0, entry['post_dig_terrain']
            if args.layout == 'default' and level == 1:
                fixture.lua("local v=ms.norgosMemoryPose();ms.dump('/ms-memory.json',v)")
                memory = read_json('ms-memory.json')
                entry['memory_pose'] = memory
                assert memory['found'] and memory['details']['visibility']['remembered'] > 0, memory
                entry['screenshots'].append(shot(f'norgos-{label}-memory-64'))
            result['zones'].append(entry)
            save()
            print('OK', label, 'terrain=', entry['terrain'], 'actors=', entry['actor_count'],
                  'dig=', entry.get('dig', {}).get('found') if dig else 'n/a')
        result['complete'] = len(result['zones']) == 6
        save()
        print('PASS', len(result['zones']), 'zones surveyed')
    finally:
        save()


if __name__ == '__main__':
    main()
