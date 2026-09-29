#!/usr/bin/env python3
"""0.6.13 E1 gel (jelly/ooze) in-game capture inside the already running isolated fixture.

This is a driver, not a launcher. It refuses an incomplete catalog or art set and
writes only evidence/runtime-v0613. Screenshots are engine captures of arranged
native actors with frozen AI in the fixture's native Trollmire birth zone; they
are not natural-encounter evidence. A final phase deals real native physical
damage through the same projector as tests/live_shields.lua to exercise the
native clone_on_hit split on one ooze.
"""
import argparse
import csv
import json
import shutil
import subprocess
import sys
from pathlib import Path

from capture_korpul import Fixture, HOME, ROOT, SESSION, digest, png_size

OUT = ROOT / 'evidence/runtime-v0613'
NEW = {'green jelly': 'green-jelly', 'black jelly': 'black-jelly', 'white jelly': 'white-jelly',
       'yellow jelly': 'yellow-jelly', 'black ooze': 'black-ooze', 'yellow ooze': 'yellow-ooze',
       'red ooze': 'red-ooze', 'blue ooze': 'blue-ooze'}
ANCHORS = {'green mold': 'green-mold', 'green worm mass': 'green-worm-mass'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--split', default='black ooze', help='identity used for the clone_on_hit split check')
    args = parser.parse_args()
    fixture = Fixture()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'screenshots').mkdir(exist_ok=True)
    manifest = json.loads((ROOT / 'data/token-manifest.json').read_text())
    assert manifest['version'] == '0.6.13' and len(manifest['assets']) == 54, \
        'requires the reviewed 0.6.13 54-token catalog'
    ids = {item['id'] for item in manifest['assets']}
    assert set(NEW.values()) | set(ANCHORS.values()) <= ids
    for item in manifest['assets']:
        assert digest(ROOT / 'data/gfx/tokens' / (item['id'] + '.png')) == item['runtime_sha256']
    installed = SESSION / 'runtime/game/addons/tome-checker-fixture/data/monster-live_e1_scene.lua'
    assert digest(installed) == digest(ROOT / 'tests/live_e1_scene.lua'), \
        'fixture scene differs from the repository copy'
    result = {'version': '0.6.13', 'zone': 'trollmire', 'shaders': True,
              'arranged': True, 'frozen_ai': True, 'edited': False, 'complete': False, 'shots': [],
              'manifest_sha256': digest(ROOT / 'data/token-manifest.json'),
              'launch': json.loads((SESSION / 'launch-plan.json').read_text())}

    def save():
        (OUT / 'capture-trollmire.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
        (OUT / 'validation-trollmire.txt').write_text(
            (''.join(fixture.transcript) + fixture.new_log()).rstrip() + '\n')
        for pattern in ('e1-*.txt', 'e1-*.tsv'):
            for src in HOME.glob(pattern):
                shutil.copy2(src, OUT / src.name)

    def shot(phase, mode, tile, expected_rows, check_rules=None):
        stem = f'e1-{phase}-{mode}-{tile}'
        fixture.lua("game:setResolution('1920x1080 Windowed',true);"
                    f"config.settings.tome.gfx.size='{tile}x{tile}';game:setupDisplayMode(false);"
                    f"e1.mode({'true' if mode == 'tokens' else 'false'});e1.dump('{phase}')")
        rules = (HOME / f'e1-rules-{phase}.txt').read_bytes()
        if check_rules is not None:
            assert rules == check_rules, 'actor art toggle changed native gameplay state'
        tsv = HOME / f'e1-scene-{phase}.tsv'
        rows = list(csv.DictReader(tsv.open(), delimiter='\t'))
        assert len(rows) == expected_rows, rows
        for row in rows:
            expected = NEW.get(row['name']) or ANCHORS.get(row['name'])
            assert expected, row['name']
            assert row['token'] == (expected if mode == 'tokens' else 'native'), row
        source = HOME / (stem + '.png')
        source.unlink(missing_ok=True)
        capture = subprocess.run([sys.executable, str(ROOT / 'tools/fixture_command.py'), 'shot', stem],
                                 capture_output=True, text=True, timeout=25)
        fixture.transcript.append(capture.stdout + capture.stderr)
        fixture.check_log()
        assert capture.returncode == 0 and png_size(source) == (1920, 1080)
        target = OUT / 'screenshots' / source.name
        shutil.copy2(source, target)
        fixture.lua(f"e1.dump('{phase}')")
        assert rules == (HOME / f'e1-rules-{phase}.txt').read_bytes(), 'capture changed native state'
        state = OUT / (stem + '.tsv')
        shutil.copy2(tsv, state)
        result['shots'].append(dict(file='screenshots/' + target.name, sha256=digest(target),
                                    resolution=[1920, 1080], phase=phase, mode=mode, tile=tile,
                                    actor_state=state.name, rules_sha256=digest(HOME / f'e1-rules-{phase}.txt')))
        save()
        return rules

    try:
        fixture.lua("assert(config.settings.cheat and config.settings.disable_all_connectivity and not profile.auth);"
                    "assert(core.shader.active(4));if not game.checker_staged then game:checkerStage() end;"
                    "assert(#require('mod.class.CheckerTokens').catalog==54);"
                    "game:checkerSetTokensEnabled(true);game:checkerSetMode('refined');"
                    "e1=dofile('/data-checker-fixture/monster-live_e1_scene.lua');"
                    "e1.enter()")
        native = shot('baseline', 'native', 64, 10)
        for tile in (48, 64, 96):
            shot('baseline', 'tokens', tile, 10, check_rules=native)
        fixture.check_log()
        # Real native clone_on_hit split: physical damage via the native projector
        # (same call as tests/live_shields.lua), chance forced to 100 on the test
        # actor only so it fires deterministically; the split code itself
        # (Actor.lua:onTakeHit) is untouched.
        fixture.lua(f"e1.split({args.split!r})")
        shot('split', 'tokens', 64, 11)
        fixture.check_log()
        result['complete'] = True
        save()
        print('PASS', len(result['shots']), 'unedited screenshots (native baseline + 48/64/96 tokens + split)')
    finally:
        save()


if __name__ == '__main__':
    main()
