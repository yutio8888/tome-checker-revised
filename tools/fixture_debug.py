"""Execute Lua only in the isolated, offline checkerboard debug session."""
from pathlib import Path
import subprocess
import sys
import time

root = Path(__file__).resolve().parents[4]
session = root / 'demo/checkerboard-v3/session'
data = session / 'runtime/game/addons/tome-checker-fixture/data'
assert (data / 'audit.lua').is_file(), 'Install the separate offline checker-fixture first'
assert len(sys.argv) == 2, 'Pass one Lua source string'
home = session / 'home/.t-engine/4.0/tome'
command = home / 'board-test-command.txt'
result = home / 'board-test-result.txt'
assert not command.exists(), 'Previous debug command remains pending'
result.unlink(missing_ok=True)
# The audit reader must never observe a partially written Lua command.
pending = command.with_name('.board-test-command.pending')
pending.write_text(sys.argv[1])
pending.replace(command)
subprocess.run([sys.executable, str(Path(__file__).with_name('fixture_command.py')), 'audit'], check=True)
deadline = time.monotonic() + 45
while time.monotonic() < deadline:
    if result.exists() and result.stat().st_size:
        message = result.read_text()
        print(message)
        raise SystemExit(0 if message.startswith('PASS\n') else 1)
    time.sleep(0.1)
raise SystemExit('Debug command did not finish; inspect session/game.log')
