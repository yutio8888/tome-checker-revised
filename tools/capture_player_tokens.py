#!/usr/bin/env python3
"""Player token live validation in the running isolated fixture.

This is a driver, not a launcher. Launch the fixture first with
`launch_fixture.py --shaders --resolution 1920x1080 --terrain refined --tiles 64
--birth RACE:SUBRACE:SEX:CLASS` (directory install, no --hero-token, no --without-fixture).
It waits for the birthed hero, runs tests/live_player_tokens.lua, asserts the
production identity contract, takes unedited 1920x1080 screenshots, and (case
'a' only) also exercises the toggle, an external-display override and an
equipment change. Output goes only to evidence/player-tokens-20260928.
"""
import argparse
import json
import re
import sys
import time

from capture_korpul import Fixture, HOME, LOG, ROOT, SESSION, digest, png_size

OUT = ROOT / 'evidence/player-tokens-20260928'
SCENE = 'live_player_tokens'

CASES = {
    'a': dict(family='human_male', subrace='Cornac', sex='Male', extended=True),
    'b': dict(family='elf_female', subrace='Shalore', sex='Female', extended=False),
    'c': dict(family=None, subrace='Halfling', sex='Female', extended=False),
    'd': dict(family='skeleton', subrace='Skeleton', sex='Male', extended=False),
}


def wait_for_birth(fixture, case, timeout=120):
    deadline = time.monotonic() + timeout
    pattern = re.compile(r"\[CheckerFixture\] BIRTH\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)")
    error_pattern = re.compile(r"\[CheckerFixture\] ERROR invalid checker_birth: (.+)")
    last_err = None
    while time.monotonic() < deadline:
        # Birth may already be logged before this process starts (fixture.new_log
        # only sees bytes written after Fixture() was constructed); read the whole
        # session log instead of the offset-based tail.
        text = LOG.read_text(encoding='utf-8', errors='replace') if LOG.exists() else ''
        err = error_pattern.search(text)
        if err:
            raise RuntimeError('invalid checker_birth: ' + err.group(1))
        match = None
        for match in pattern.finditer(text):
            pass
        if match and match.group(1) == case['subrace'] and match.group(2) == case['sex']:
            return match.groups()
        time.sleep(1)
    raise RuntimeError('birth did not complete in time; last log tail: ' + fixture.new_log()[-2000:])


def installed_ok():
    plan = json.loads((SESSION / 'launch-plan.json').read_text())
    assert plan.get('fixture') and plan.get('shaders') and plan.get('resolution') == '1920x1080' \
        and plan.get('terrain') == 'refined' and plan.get('tokens') and not plan.get('hero_token'), \
        'requires the offline fixture: shaders, refined terrain, 1920x1080, tokens on, no --hero-token'
    installed = SESSION / f'runtime/game/addons/tome-checker-fixture/data/monster-{SCENE}.lua'
    assert digest(installed) == digest(ROOT / f'tests/{SCENE}.lua'), 'fixture scene differs from the repository copy; relaunch'
    for rel in ('overload/mod/class/CheckerPlayerTokens.lua', 'superload/mod/class/Game.lua',
                'overload/mod/class/CheckerOptions.lua', 'superload/mod/class/Actor.lua'):
        copy = SESSION / 'runtime/game/addons/tome-checker-revised' / rel
        assert digest(copy) == digest(ROOT / rel), f'installed {rel} differs from the repository copy; relaunch'
    return plan


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('case', choices=sorted(CASES))
    args = parser.parse_args()
    case = CASES[args.case]
    fixture = Fixture()
    (OUT / 'screenshots').mkdir(parents=True, exist_ok=True)
    plan = installed_ok()
    result = {'case': args.case, 'family': case['family'], 'birth': plan.get('birth'),
              'launch': plan, 'shots': [], 'reports': [], 'complete': False,
              'scene_sha256': digest(ROOT / f'tests/{SCENE}.lua')}

    def save():
        (OUT / f'capture-{args.case}.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
        (OUT / f'validation-transcript-{args.case}.txt').write_text((''.join(fixture.transcript) + fixture.new_log()).rstrip() + '\n')

    def shot(name, tile):
        source = HOME / (name + '.png')
        source.unlink(missing_ok=True)
        import subprocess
        capture = subprocess.run([sys.executable, str(ROOT / 'tools/fixture_command.py'), 'shot', name],
                                 capture_output=True, text=True, timeout=25)
        fixture.transcript.append(capture.stdout + capture.stderr)
        fixture.check_log()
        assert capture.returncode == 0 and source.is_file() and png_size(source) == (1920, 1080), name
        import shutil
        target = OUT / 'screenshots' / source.name
        shutil.copy2(source, target)
        result['shots'].append(dict(file='screenshots/' + target.name, sha256=digest(target),
                                    resolution=[1920, 1080], tile=tile))
        save()

    def report(label):
        fixture.lua(f"pt=pt or dofile('/data-checker-fixture/monster-{SCENE}.lua');pt.report('{label}')")
        text = (HOME / 'player-tokens-validation.txt').read_text()
        line = text.strip().splitlines()[-1]
        result['reports'].append(line)
        save()
        return line

    try:
        birth = wait_for_birth(fixture, case)
        fixture.lua(f"pt=dofile('/data-checker-fixture/monster-{SCENE}.lua');pt.refresh()")
        line = report('birth')
        if case['family']:
            fixture.lua(f"pt.assertIdentity('{case['family']}')")
        else:
            fixture.lua("pt.assertIdentity(nil)")
        shot(f'player-tokens-{args.case}-64', 64)

        if case['extended']:
            fixture.lua("pt.setZoom(48)")
            shot(f'player-tokens-{args.case}-48', 48)
            fixture.lua("pt.setZoom(96)")
            shot(f'player-tokens-{args.case}-96', 96)
            fixture.lua("pt.setZoom(64)")
            report('back-to-64')

            fixture.lua("pt.setPlayerTokens(false)")
            report('tokens-off')
            fixture.lua("pt.assertIdentity(nil)")
            shot(f'player-tokens-{args.case}-native', 64)

            fixture.lua("pt.setPlayerTokens(true)")
            report('tokens-on-again')
            fixture.lua(f"pt.assertIdentity('{case['family']}')")

            fixture.lua("pt.applyShapeshift()")
            report('shapeshift-active')
            fixture.lua("pt.assertIdentity(nil)")
            shot(f'player-tokens-{args.case}-shapeshift', 64)

            fixture.lua("pt.removeShapeshift()")
            report('shapeshift-removed')
            fixture.lua(f"pt.assertIdentity('{case['family']}')")

            removed = fixture.lua("local r=pt.changeEquipment();"
                                  "local f=assert(fs.open('/equipment-removed.txt','w'));f:write(r.name);f:close()")
            report('equipment-changed-token-still-on')
            fixture.lua(f"pt.assertIdentity('{case['family']}')")

            fixture.lua("pt.setPlayerTokens(false)")
            after = report('equipment-changed-native')
            shot(f'player-tokens-{args.case}-equipment-native', 64)
            fixture.lua("pt.setPlayerTokens(true)")
            report('final-tokens-on')

        result['complete'] = True
        save()
        print('PASS case', args.case, 'family', case['family'], 'shots', len(result['shots']))
    finally:
        save()


if __name__ == '__main__':
    main()
