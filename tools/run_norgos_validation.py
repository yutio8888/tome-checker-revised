#!/usr/bin/env python3
"""Six independent cold starts in the isolated offline fixture, then stop our PIDs."""
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

from launch_fixture import SESSION

ADDON = Path(__file__).resolve().parents[1]
PROCESSES = SESSION / 'processes.json'


def stop_started(meta):
    for kind, marker in (('game', '/t-engine'), ('xvfb', 'Xvfb')):
        pid = meta[kind]
        cmdline = Path('/proc') / str(pid) / 'cmdline'
        if cmdline.exists() and marker.encode() in cmdline.read_bytes():
            os.kill(pid, signal.SIGTERM)
    for _ in range(50):
        if all(not (Path('/proc') / str(meta[k]) / 'cmdline').exists() for k in ('game', 'xvfb')):
            break
        time.sleep(.1)
    for kind, marker in (('game', '/t-engine'), ('xvfb', 'Xvfb')):
        pid = meta[kind]
        cmdline = Path('/proc') / str(pid) / 'cmdline'
        if cmdline.exists() and marker.encode() in cmdline.read_bytes():
            os.kill(pid, signal.SIGKILL)
    socket = Path('/tmp/.X11-unix') / ('X' + meta['display'][1:])
    for _ in range(30):
        if not socket.exists():
            break
        time.sleep(.1)
    if socket.exists():
        # The exact Xvfb we started is gone; this is its stale socket only.
        cmdline = Path('/proc') / str(meta['xvfb']) / 'cmdline'
        if not cmdline.exists() or b'Xvfb' not in cmdline.read_bytes():
            socket.unlink()


def main():
    for layout in ('default', 'invaded'):
        for level in (1, 2, 3):
            label = f'{layout}-L{level}'
            launch = subprocess.run([sys.executable, str(ADDON / 'tools/launch_fixture.py'),
                '--shaders', '--tiles', '64', '--terrain', 'refined', '--resolution', '1920x1080',
                '--birth', 'Human:Cornac:Male:Berserker'], cwd=ADDON, capture_output=True, text=True)
            if launch.returncode:
                raise RuntimeError(f'{label} launch failed: {launch.stdout} {launch.stderr}')
            meta = json.loads(PROCESSES.read_text())
            try:
                print('START', label, launch.stdout.strip(), flush=True)
                home = SESSION / 'home/.t-engine/4.0/tome'
                for _ in range(180):
                    if home.is_dir():
                        break
                    time.sleep(.5)
                else:
                    raise RuntimeError(f'{label}: game did not create fixture home')
                time.sleep(3)
                driver = subprocess.run([sys.executable, str(ADDON / 'tools/capture_norgos_20260928.py'),
                    '--layout', layout, '--level', str(level)], cwd=ADDON,
                    capture_output=True, text=True, timeout=300)
                print(driver.stdout, flush=True)
                if driver.returncode:
                    raise RuntimeError(f'{label} capture failed: {driver.stderr}')
            finally:
                stop_started(meta)
                print('STOP', label, meta['game'], meta['xvfb'], flush=True)


if __name__ == '__main__':
    main()
