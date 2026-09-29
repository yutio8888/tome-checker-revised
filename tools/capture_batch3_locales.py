#!/usr/bin/env python3
"""Capture the changed Board terrain option in three independent locales."""
import json
import shutil
import subprocess
import sys
import time

from capture_korpul import Fixture, HOME, ROOT, SESSION, digest, png_size
from run_norgos_validation import stop_started

OUT = ROOT / 'evidence/batch3-20260928'
SHOTS = OUT / 'screenshots'

for locale in ('en_US', 'zh_hans', 'zh_hant'):
    launch = subprocess.run([sys.executable, str(ROOT / 'tools/launch_fixture.py'), '--shaders', '--tiles', '64', '--terrain', 'refined', '--resolution', '1920x1080', '--locale', locale], cwd=ROOT, capture_output=True, text=True)
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
        fixture = Fixture()
        fixture.lua("assert(config.settings.cheat and config.settings.disable_all_connectivity and not profile.auth);assert(core.shader.active(4));checker_options=require('mod.dialogs.GameOptions').new();game:registerDialog(checker_options);for _,t in ipairs(checker_options.c_tabs.tabs) do if t.title=='Token colors' or t.title=='棋子颜色' or t.title=='棋子顏色' then checker_options.c_tabs:select(t.kind) end end")
        fixture.lua("local row;for i,item in ipairs(checker_options.list) do if item.checker_terrain_mode then row=i end end;assert(row,'Board terrain row missing');checker_options.c_list.sel=row;checker_options:select(checker_options.list[row]);core.display.forceRedraw()")
        name = f'options-{locale}'
        source = HOME / (name + '.png')
        source.unlink(missing_ok=True)
        result = subprocess.run([sys.executable, str(ROOT / 'tools/fixture_command.py'), 'shot', name], capture_output=True, text=True, timeout=35)
        assert result.returncode == 0 and source.is_file() and png_size(source) == (1920, 1080), result.stdout + result.stderr
        SHOTS.mkdir(parents=True, exist_ok=True)
        target = SHOTS / source.name
        shutil.copy2(source, target)
        (OUT / f'validation-options-{locale}.txt').write_text((''.join(fixture.transcript) + fixture.new_log()).rstrip() + '\n')
        print(locale, target, digest(target), flush=True)
    finally:
        stop_started(meta)
