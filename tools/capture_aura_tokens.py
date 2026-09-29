#!/usr/bin/env python3
"""Native shader-aura + token capture inside the running isolated fixture.

This is a driver, not a launcher. Start a fresh fixture first with
`launch_fixture.py --shaders --tiles 64 --terrain refined --resolution 1920x1080`
(tokens on, no --hero-token so the player uses the production player:human_male
mapping). It runs tests/live_aura_tokens.lua to stage the scene, spawn a giant
crystal rat, apply four native addShaderAura samples (stone_skin/crystalineaura
required, plus body_of_fire/reflective_skin/essence_of_the_dead) to the staged
wolf/forest troll/brown bear/large brown snake plus the player token, proves
the real (non-debug) T_STONE_SKIN talent path on the crystal rat, then removes
every aura. It captures: one "before" shot with no auras, 48/64/96 "active"
shots, and one shot with tokens switched off (native art + native aura).
Output goes only to evidence/aura-tokens-20260928. Screenshots are unedited
engine captures of a staged scene with frozen AI (checkerStage/never_act).
"""
import json
import shutil
import subprocess
import sys

from capture_korpul import Fixture, HOME, ROOT, SESSION, digest, png_size

OUT = ROOT / 'evidence/aura-tokens-20260928'
SCENE = 'live_aura_tokens'
MONSTERS = ('wolf', 'forest troll', 'brown bear', 'large brown snake')
AURAS = {
    'wolf': 'stone_skin',
    'forest troll': 'body_of_fire',
    'brown bear': 'reflective_skin',
    'large brown snake': 'essence_of_the_dead',
    'player': 'stone_skin',
}


def main():
    fixture = Fixture()
    (OUT / 'screenshots').mkdir(parents=True, exist_ok=True)
    plan = json.loads((SESSION / 'launch-plan.json').read_text())
    assert plan.get('fixture') and plan.get('tokens') and plan.get('shaders') and plan.get('resolution') == '1920x1080', \
        'requires the offline fixture with tokens, shaders and 1920x1080'
    installed = SESSION / f'runtime/game/addons/tome-checker-fixture/data/monster-{SCENE}.lua'
    assert digest(installed) == digest(ROOT / f'tests/{SCENE}.lua'), 'fixture scene differs from the repository copy; relaunch'
    for rel in ('overload/mod/class/CheckerTokens.lua', 'overload/mod/class/CheckerPlayerTokens.lua',
                'superload/mod/class/Game.lua', 'superload/mod/class/Actor.lua'):
        copy = SESSION / 'runtime/game/addons/tome-checker-revised' / rel
        assert digest(copy) == digest(ROOT / rel), f'installed {rel} differs from the repository copy; relaunch'
    result = {'zone': 'trollmire', 'shaders': True, 'staged': True, 'frozen_ai': True,
              'edited': False, 'complete': False, 'shots': [],
              'scene_sha256': digest(ROOT / f'tests/{SCENE}.lua'), 'launch': plan, 'samples': []}

    def save():
        (OUT / 'capture.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
        (OUT / 'validation-transcript.txt').write_text((''.join(fixture.transcript) + fixture.new_log()).rstrip() + '\n')
        src = HOME / 'aura-tokens-validation.txt'
        if src.exists():
            shutil.copy2(src, OUT / src.name)

    def shot(name, tile, focus, kind):
        fixture.lua(f"config.settings.tome.gfx.size='{tile}x{tile}';game:setupDisplayMode(false);{focus}")
        source = HOME / (name + '.png')
        source.unlink(missing_ok=True)
        capture = subprocess.run([sys.executable, str(ROOT / 'tools/fixture_command.py'), 'shot', name],
                                 capture_output=True, text=True, timeout=25)
        fixture.transcript.append(capture.stdout + capture.stderr)
        fixture.check_log()
        assert capture.returncode == 0 and source.is_file() and png_size(source) == (1920, 1080), name
        target = OUT / 'screenshots' / source.name
        shutil.copy2(source, target)
        result['shots'].append(dict(file='screenshots/' + target.name, sha256=digest(target),
                                    resolution=[1920, 1080], tile=tile, kind=kind))
        save()

    try:
        fixture.lua("assert(config.settings.cheat and not profile.auth);assert(core.shader.active(4));"
                    "if not game.checker_staged then game:checkerStage() end;"
                    f"aura=dofile('/data-checker-fixture/monster-{SCENE}.lua');aura.run()")
        shot('aura-tokens-64-before', 64, "aura.focus('player')", 'before-no-aura')
        for name in MONSTERS:
            fixture.lua(f"aura.apply('{name}','{AURAS[name]}')")
        fixture.lua("aura.apply('player','stone_skin')")
        fixture.lua("aura.realStoneSkin('giant crystal rat')")
        fixture.lua("aura.report()")
        for tile in (48, 64, 96):
            shot(f'aura-tokens-{tile}-active', tile, "aura.focus('player')", 'active')
        fixture.lua("game:checkerSetTokensEnabled(false)")
        shot('aura-tokens-native-wolf', 64, '', 'tokens-off-native-aura')
        fixture.lua("game:checkerSetTokensEnabled(true);aura.report()")
        fixture.lua("game:checkerSetMode('vanilla');aura.report();game:checkerSetMode('refined');aura.report()")
        for name in MONSTERS:
            fixture.lua(f"aura.remove('{name}','{AURAS[name]}')")
        fixture.lua("aura.remove('player','stone_skin');aura.deactivateStoneSkin('giant crystal rat');aura.report()")
        result['complete'] = True
        save()
        print('PASS', len(result['shots']), 'unedited 1920x1080 screenshots: before/active(48,64,96)/native-tokens-off')
    finally:
        save()


if __name__ == '__main__':
    main()
