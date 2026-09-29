#!/usr/bin/env python3
"""0.6.9 C0b in-game capture inside the already running isolated fixture.

This is a driver, not a launcher. It refuses an incomplete catalog or art set and
writes only evidence/runtime-v069. Screenshots are engine captures of arranged
native actors with frozen AI; they are not natural-encounter evidence.
"""
import argparse
import csv
import json
import shutil
import subprocess
import sys
from pathlib import Path

from capture_korpul import Fixture, HOME, ROOT, SESSION, digest, png_size

OUT = ROOT / 'evidence/runtime-v069'
NEW = {'giant white mouse': 'giant-white-mouse', 'giant brown mouse': 'giant-brown-mouse',
       'giant grey mouse': 'giant-grey-mouse', 'giant rabbit': 'giant-rabbit',
       'giant crystal rat': 'giant-crystal-rat', 'brown mold': 'brown-mold',
       'green mold': 'green-mold', 'shining mold': 'shining-mold'}
ANCHORS = {'giant white rat': 'giant-white-rat', 'giant brown rat': 'brown-rat',
           'giant grey rat': 'giant-grey-rat', 'grey mold': 'grey-mold'}
SEEDS = {'DEFAULT': 537501, 'HIDEOUT': 537502}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--layout', choices=tuple(SEEDS), default='DEFAULT')
    args = parser.parse_args()
    layout = args.layout
    fixture = Fixture()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'screenshots').mkdir(exist_ok=True)
    manifest = json.loads((ROOT / 'data/token-manifest.json').read_text())
    assert manifest['version'] == '0.6.9' and len(manifest['assets']) == 45, 'requires the reviewed 0.6.9 45-token catalog'
    ids = {item['id'] for item in manifest['assets']}
    assert set(NEW.values()) | set(ANCHORS.values()) <= ids
    for item in manifest['assets']:
        assert digest(ROOT / 'data/gfx/tokens' / (item['id'] + '.png')) == item['runtime_sha256']
    installed = SESSION / 'runtime/game/addons/tome-checker-fixture/data/monster-live_c0b_scene.lua'
    assert digest(installed) == digest(ROOT / 'tests/live_c0b_scene.lua'), 'fixture scene differs from the repository copy'
    result = {'version': '0.6.9', 'layout': layout, 'seed_input': SEEDS[layout], 'shaders': True,
              'arranged': True, 'frozen_ai': True, 'edited': False, 'complete': False, 'shots': [],
              'manifest_sha256': digest(ROOT / 'data/token-manifest.json'),
              'launch': json.loads((SESSION / 'launch-plan.json').read_text())}

    def save():
        (OUT / ('capture-' + layout.lower() + '.json')).write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
        (OUT / ('validation-' + layout.lower() + '.txt')).write_text((''.join(fixture.transcript) + fixture.new_log()).rstrip() + '\n')
        for pattern in (f'c0b-*-{layout.lower()}*.txt', f'c0b-*-{layout.lower()}*.tsv'):
            for src in HOME.glob(pattern):
                shutil.copy2(src, OUT / src.name)

    def shot(phase, mode, tile):
        stem = f'c0b-{layout.lower()}-{phase}-{mode}-{tile}'
        fixture.lua("game:setResolution('1920x1080 Windowed',true);"
                    f"config.settings.tome.gfx.size='{tile}x{tile}';game:setupDisplayMode(false);"
                    f"c0b.mode({'true' if mode == 'tokens' else 'false'});c0b.dump('{phase}')")
        rules = (HOME / f'c0b-rules-{layout.lower()}-{phase}.txt').read_bytes()
        tsv = HOME / f'c0b-scene-{layout.lower()}-{phase}.tsv'
        rows = list(csv.DictReader(tsv.open(), delimiter='\t'))
        assert len(rows) == 12, rows
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
        fixture.lua(f"c0b.dump('{phase}')")
        assert rules == (HOME / f'c0b-rules-{layout.lower()}-{phase}.txt').read_bytes(), 'capture changed native state'
        state = OUT / (stem + '.tsv')
        shutil.copy2(tsv, state)
        result['shots'].append(dict(file='screenshots/' + target.name, sha256=digest(target),
                                    resolution=[1920, 1080], phase=phase, mode=mode, tile=tile,
                                    actor_state=state.name, rules_sha256=digest(HOME / f'c0b-rules-{layout.lower()}-{phase}.txt')))
        save()
        return rules

    try:
        fixture.lua("assert(config.settings.cheat and config.settings.disable_all_connectivity and not profile.auth);"
                    "assert(core.shader.active(4));if not game.checker_staged then game:checkerStage() end;"
                    "assert(#require('mod.class.CheckerTokens').catalog==45);"
                    "game:checkerSetTokensEnabled(true);game:checkerSetMode('refined');"
                    "c0b=dofile('/data-checker-fixture/monster-live_c0b_scene.lua');"
                    f"c0b.enter('{layout}',{SEEDS[layout]})")
        native = shot('baseline', 'native', 64)
        for tile in (48, 64, 96):
            assert shot('baseline', 'tokens', tile) == native, 'actor art toggle changed native gameplay state'
        fixture.check_log()
        result['complete'] = True
        save()
        print(layout, 'PASS', len(result['shots']), 'unedited screenshots at 48/64/96 plus a native baseline')
    finally:
        save()


if __name__ == '__main__':
    main()
