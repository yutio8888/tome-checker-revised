#!/usr/bin/env python3
"""F1 flooded Trollmire terrain: 0.6.14 live validation driver.

This is a driver, not a launcher. Start a fresh fixture first, e.g.:
  launch_fixture.py --shaders --tiles 64 --terrain refined --resolution 1920x1080 \
    --birth "Human:Cornac:Male:Berserker"
It forces Trollmire FLOODED L1 and L3, the shared static L4 treasure map
under the FLOODED zone object, and re-enters DEFAULT L1 as a regression --
all through tests/live_map_survey.lua (native game:changeLevel plus the same
alternateZoneTier1 override-then-restore technique already used for Kor'Pul
HIDEOUT/DEFAULT). For FLOODED L1 it also runs a native DIG on a BOGTREE cell
(tests/live_map_survey.lua's M.digBogtree(), which uses the same DamageType
DIG projector entry point as tests/live_terrain_repair.lua) to confirm the
integrated NicerTiles->checkerRepairTerrain hook repaints it from bog-tree to
bog art automatically. Output goes only to evidence/runtime-v0614.
"""
import json
import shutil
import subprocess
import sys

from capture_korpul import Fixture, HOME, ROOT, SESSION, digest, png_size

OUT = ROOT / 'evidence/runtime-v0614'
SHOTS = OUT / 'screenshots'
SCENE = 'live_map_survey'

# (short_name, level, opts-or-None, label, dig)
ZONES = [
    ('trollmire', 1, {'flooded': True}, 'trollmire-L1-flooded', True),
    ('trollmire', 3, {'flooded': True}, 'trollmire-L3-flooded', False),
    ('trollmire', 4, {'flooded': True}, 'trollmire-L4-flooded-treasure', False),
    ('trollmire', 1, {'flooded': False}, 'trollmire-L1-default-regression', False),
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
        for short_name, level, opts, label, dig in ZONES:
            code = (f"local enter=ms.enter({short_name!r},{level},{lua_opts(opts)});"
                    "local terrain=ms.terrainCensus();local actors=ms.actorCensus();"
                    "ms.dump('/ms-result.json',{enter=enter,terrain=terrain,actors=actors})")
            fixture.lua(code)
            data = read_json('ms-result.json')
            shots = []
            for tile in (48, 64, 96):
                fixture.lua("game:setResolution('1920x1080 Windowed',true);"
                            f"config.settings.tome.gfx.size='{tile}x{tile}';game:setupDisplayMode(false);"
                            "ms.focus(game.player.x,game.player.y)")
                info = shot(f'runtime-v0614-{label}-{tile}')
                info['tile'] = tile
                shots.append(info)
            fixture.lua("config.settings.tome.gfx.size='64x64';game:setupDisplayMode(false);"
                        "ms.focus(game.player.x,game.player.y)")
            entry = {'label': label, 'short_name': short_name, 'level': level, 'opts': opts,
                     'enter': data['enter'], 'terrain': data['terrain'],
                     'actor_count': len(data['actors']['actors']), 'screenshots': shots}
            # Mode round trip: vanilla releases every painted cell, refined
            # reinstalls it, same assertion shape as capture_map_survey.py's
            # 'painted' zones -- every Trollmire layout is now fully painted.
            fixture.lua("ms.setMode('vanilla');local v=ms.terrainCensus();"
                        "ms.setMode('refined');local r=ms.terrainCensus();"
                        "ms.dump('/ms-modecheck.json',{vanilla=v,refined=r})")
            entry['mode_round_trip'] = read_json('ms-modecheck.json')
            assert entry['terrain']['native'] == 0, f'{label}: expected full painted coverage, got {entry["terrain"]}'
            assert entry['mode_round_trip']['vanilla']['owned'] == 0, f'{label}: vanilla must release every cell'
            assert entry['mode_round_trip']['refined']['native'] == 0, f'{label}: refined must reinstall everything'
            if dig:
                fixture.lua("local d=ms.digBogtree();ms.dump('/ms-dig.json',d)")
                dig_result = read_json('ms-dig.json')
                entry['dig'] = dig_result
                if dig_result.get('found'):
                    assert dig_result['after_name'] == 'bog water', dig_result
                    assert dig_result.get('after_owned') is True, dig_result
                    assert dig_result.get('after_image') and 'bog-tree' not in dig_result['after_image'], dig_result
                    fixture.lua(f"ms.focus({dig_result['x']},{dig_result['y']})")
                    entry['dig']['screenshot'] = shot(f'runtime-v0614-{label}-dig-repair-64')
                fixture.lua("local t=ms.terrainCensus();ms.dump('/ms-postdig.json',t)")
                entry['post_dig_terrain'] = read_json('ms-postdig.json')
                assert entry['post_dig_terrain']['native'] == 0, entry['post_dig_terrain']
            result['zones'].append(entry)
            save()
            print('OK', label, 'terrain=', entry['terrain'], 'actors=', entry['actor_count'],
                  'dig=', entry.get('dig', {}).get('found') if dig else 'n/a')
        result['complete'] = True
        save()
        print('PASS', len(result['zones']), 'zones surveyed')
    finally:
        save()


if __name__ == '__main__':
    main()
