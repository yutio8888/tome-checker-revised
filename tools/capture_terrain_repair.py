#!/usr/bin/env python3
"""Trollmire refined-terrain repair capture inside the running isolated fixture.

This is a driver, not a launcher. Start a fresh fixture with
`launch_fixture.py --shaders --tiles 64 --terrain refined --resolution 1920x1080`
first. It runs tests/live_terrain_repair.lua (native DIG, generic updateAround
and mid-game full passes), then captures one unrepaired control and the
repaired dig at 48/64/96. Output goes only to evidence/terrain-repair-20260928.
Screenshots are unedited engine captures of a staged scene with frozen AI.
"""
import json
import shutil
import subprocess
import sys

from capture_korpul import Fixture, HOME, ROOT, SESSION, digest, png_size

OUT = ROOT / 'evidence/terrain-repair-20260928'
SCENE = 'live_terrain_repair'


def main():
    fixture = Fixture()
    (OUT / 'screenshots').mkdir(parents=True, exist_ok=True)
    plan = json.loads((SESSION / 'launch-plan.json').read_text())
    assert plan.get('fixture') and plan.get('shaders') and plan.get('resolution') == '1920x1080', \
        'requires the offline fixture with shaders at 1920x1080'
    installed = SESSION / f'runtime/game/addons/tome-checker-fixture/data/monster-{SCENE}.lua'
    assert digest(installed) == digest(ROOT / f'tests/{SCENE}.lua'), 'fixture scene differs from the repository copy; relaunch'
    for rel in ('overload/mod/class/CheckerTerrain.lua', 'superload/mod/class/NicerTiles.lua',
                'superload/mod/class/Game.lua'):
        copy = SESSION / 'runtime/game/addons/tome-checker-revised' / rel
        assert digest(copy) == digest(ROOT / rel), f'installed {rel} differs from the repository copy; relaunch'
    result = {'zone': 'trollmire', 'terrain': 'refined', 'shaders': True, 'staged': True,
              'frozen_ai': True, 'edited': False, 'complete': False, 'shots': [],
              'scene_sha256': digest(ROOT / f'tests/{SCENE}.lua'), 'launch': plan}

    def save():
        (OUT / 'capture.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
        (OUT / 'validation-transcript.txt').write_text((''.join(fixture.transcript) + fixture.new_log()).rstrip() + '\n')
        src = HOME / 'terrain-repair-validation.txt'
        if src.exists():
            shutil.copy2(src, OUT / src.name)

    def state():
        fixture.lua("local f=assert(fs.open('/terrain-repair-state.txt','w'));f:write(tr.state());f:close()")
        return (HOME / 'terrain-repair-state.txt').read_text()

    def shot(name, tile, focus, kind):
        fixture.lua("game:setResolution('1920x1080 Windowed',true);"
                    f"config.settings.tome.gfx.size='{tile}x{tile}';game:setupDisplayMode(false);{focus}")
        before = state()
        source = HOME / (name + '.png')
        source.unlink(missing_ok=True)
        capture = subprocess.run([sys.executable, str(ROOT / 'tools/fixture_command.py'), 'shot', name],
                                 capture_output=True, text=True, timeout=25)
        fixture.transcript.append(capture.stdout + capture.stderr)
        fixture.check_log()
        assert capture.returncode == 0 and source.is_file() and png_size(source) == (1920, 1080), name
        assert state() == before, 'capture changed turn, position, life or energy'
        target = OUT / 'screenshots' / source.name
        shutil.copy2(source, target)
        result['shots'].append(dict(file='screenshots/' + target.name, sha256=digest(target),
                                    resolution=[1920, 1080], tile=tile, kind=kind, state=before))
        save()

    try:
        fixture.lua("assert(config.settings.cheat and config.settings.disable_all_connectivity and not profile.auth);"
                    "assert(core.shader.active(4));if not game.checker_staged then game:checkerStage() end;"
                    "game:checkerSetMode('refined');"
                    f"tr=dofile('/data-checker-fixture/monster-{SCENE}.lua');tr.run()")
        shot('terrain-repair-control-unrepaired-64', 64, 'tr.controlShot()', 'control-unrepaired')
        shot('terrain-repair-control-repaired-64', 64, 'tr.controlRepair()', 'control-repaired')
        for tile in (48, 64, 96):
            shot(f'terrain-repair-dig-{tile}', tile, 'tr.focusDig()', 'integrated-dig')
        fixture.lua("config.settings.tome.gfx.size='64x64';game:setupDisplayMode(false);tr.focusDig()")
        fixture.check_log()
        result['complete'] = True
        save()
        print('PASS', len(result['shots']), 'unedited 1920x1080 screenshots: control + repaired dig at 48/64/96')
    finally:
        save()


if __name__ == '__main__':
    main()
