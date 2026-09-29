#!/usr/bin/env python3
"""Audit real Kor'Pul exits in the running offline fixture (never launches it).

Both variants use native generated levels and real CHANGE_LEVEL key dispatch.
The hero is positioned beside/on exits and AI is frozen for reproducibility.
Screenshots are unedited engine PNGs; input seeds are not cross-build promises.
"""
import argparse
import json
import shutil
import subprocess
import sys

from capture_korpul import Fixture, ROOT, SESSION, HOME, digest, png_size

OUT = ROOT / 'evidence/runtime-v062'
SEEDS = {'DEFAULT': 537211, 'HIDEOUT': 537212}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--layout', choices=tuple(SEEDS), required=True)
    args = parser.parse_args()
    layout = args.layout
    OUT.mkdir(parents=True, exist_ok=True)
    shots = OUT / 'screenshots'
    shots.mkdir(exist_ok=True)
    fixture = Fixture()
    metadata = OUT / ('capture-' + layout.lower() + '.json')
    result = {'version': '0.6.2', 'hud': '0.2.4', 'layout': layout,
              'seed_input': SEEDS[layout], 'edited': False, 'shaders': True,
              'natural_stairs': True, 'hero_positioned': True, 'ai_frozen': True,
              'complete': False, 'shots': [], 'transitions': []}
    comparison_rules = {}

    def save():
        metadata.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
        (OUT / ('validation-' + layout.lower() + '.txt')).write_text(''.join(fixture.transcript) + fixture.new_log())
        if (HOME / 'korpul-stairs-results.txt').exists():
            shutil.copy2(HOME / 'korpul-stairs-results.txt', OUT / 'live-results.txt')
        for p in HOME.glob('korpul-stairs-*.tsv'):
            shutil.copy2(p, OUT / p.name)

    def lua(code):
        fixture.lua(code)

    def shot(level, identity, mode='refined', tile=64, font=16):
        lua("game:setResolution('1920x1080 Windowed',true);"
            f"config.settings.tome.gfx.size='{tile}x{tile}';game:setupDisplayMode(false);"
            f"config.settings.tome.board_log_font_size={font};game.uiset:resizeIconsHotkeysToolbar();"
            f"st.stage('{identity}');st.mode('{mode}');sc.dismissFixturePrompts();"
            f"assert(game.level.level=={level});st.audit();"
            "local f=assert(fs.open('/stairs-shot-rules.txt','w'));"
            "f:write(table.concat({game.zone.short_name,game.level.level,game.turn,game.player.x,game.player.y,game.player.life,game.player.energy.value},'\t'));f:close()")
        rule = (HOME / 'stairs-shot-rules.txt').read_text()
        comparison_key = (level, identity)
        if comparison_key in comparison_rules and comparison_rules[comparison_key] != rule:
            raise RuntimeError('camera/hero or rules changed across art modes/zoom/font: ' + identity)
        comparison_rules[comparison_key] = rule
        stem = f"stairs-{layout.lower()}-l{level}-{identity.lower()}-{mode}-{tile}"
        if font != 16:
            stem += f'-font{font}'
        source = HOME / (stem + '.png')
        source.unlink(missing_ok=True)
        command = subprocess.run([sys.executable, str(ROOT / 'tools/fixture_command.py'), 'shot', stem],
                                 capture_output=True, text=True, timeout=25)
        fixture.transcript.append(command.stdout + command.stderr)
        fixture.check_log()
        if command.returncode or not source.exists() or png_size(source) != (1920,1080):
            raise RuntimeError('invalid engine screenshot: ' + stem)
        target = shots / source.name
        shutil.copy2(source, target)
        lua("assert(table.concat({game.zone.short_name,game.level.level,game.turn,game.player.x,game.player.y,game.player.life,game.player.energy.value},'\\t')=="
            + json.dumps(rule) + ", 'hero rules changed during screenshot')")
        result['shots'].append({'file': 'screenshots/' + target.name, 'sha256': digest(target),
                                'resolution': [1920,1080], 'level': level, 'identity': identity,
                                'mode': mode, 'tile': tile, 'log_font': font, 'rules': rule})
        save()

    def travel(identity, expected_level, expected_zone='ruins-kor-pul'):
        lua(f"st.mode('refined');sc.dismissFixturePrompts();st.travel('{identity}')")
        # Separate bridge turn permits the engine to complete a queued change.
        lua('st.arrive();sc.dismissFixturePrompts()')
        result['transitions'].append({'identity': identity, 'zone': expected_zone, 'level': expected_level,
                                      'route': 'native CHANGE_LEVEL; st.arrive verified actual destination'})
        save()

    def remembered_shot():
        lua("st.mode('refined');st.stage('DOWN');st.stageRemembered('DOWN')")
        try:
            stem = f'stairs-{layout.lower()}-l2-down-remembered-64'
            source = HOME / (stem + '.png')
            source.unlink(missing_ok=True)
            command = subprocess.run([sys.executable, str(ROOT / 'tools/fixture_command.py'), 'shot', stem],
                                     capture_output=True, text=True, timeout=25)
            fixture.transcript.append(command.stdout + command.stderr)
            fixture.check_log()
            if command.returncode or not source.exists() or png_size(source)!=(1920,1080):
                raise RuntimeError('invalid remembered screenshot')
            lua('st.checkRemembered()')
            target = shots / source.name
            shutil.copy2(source, target)
            result['shots'].append({'file': 'screenshots/' + target.name, 'sha256': digest(target),
                                    'resolution': [1920,1080], 'level': 2, 'identity': 'DOWN',
                                    'mode': 'refined', 'tile': 64, 'log_font': 16, 'state': 'remembered',
                                    'observer': 'temporary sight=1 and moved to nearby native floor; real playerFOV; restored afterward'})
        finally:
            lua('st.restoreRemembered()')
            save()

    try:
        lua("assert(config.settings.cheat and config.settings.disable_all_connectivity and not profile.auth);"
            "assert(core.shader.active(4));if not game.checker_staged then game:checkerStage() end;"
            "assert(require('mod.class.CheckerTerrain').stairsReady());"
            "sc=dofile('/data-checker-fixture/monster-live_korpul_scene.lua');"
            "st=dofile('/data-checker-fixture/monster-live_korpul_stairs.lua');"
            f"sc.enter('{layout}',{SEEDS[layout]});sc.dismissFixturePrompts();st.audit();st.contracts()")
        shot(1, 'UP_WILDERNESS', 'vanilla')
        shot(1, 'UP_WILDERNESS')
        travel('DOWN', 2)
        lua('st.audit();st.contracts()')
        shot(2, 'UP')
        shot(2, 'DOWN', 'vanilla')
        shot(2, 'DOWN')
        remembered_shot()
        if layout == 'HIDEOUT':
            shot(2, 'DOWN', tile=48)
            shot(2, 'DOWN', tile=96)
            shot(2, 'DOWN', font=20)
        travel('DOWN', 3)
        lua('st.audit()')
        shot(3, 'UP')
        travel('UP', 2)
        travel('UP', 1)
        travel('UP_WILDERNESS', 1, 'wilderness')
        lua('config.settings.tome.board_log_font_size=16;game.uiset:resizeIconsHotkeysToolbar()')
        result['complete'] = True
        print(layout, 'PASS:', len(result['shots']), 'screenshots and', len(result['transitions']), 'native transitions')
    finally:
        save()


if __name__ == '__main__':
    main()
