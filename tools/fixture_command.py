from pathlib import Path
import sys,time
root=Path(__file__).resolve().parents[4]/'demo/checkerboard-v3'
home=root/'session/home/.t-engine/4.0/tome'
command=' '.join(sys.argv[1:])
assert command in ('stage','toggle','audit','mode vanilla','mode blockout','mode refined','tokens on','tokens off','zoom 48','zoom 64','zoom 96','aura subtle','aura moderate') or command.startswith('shot '), 'stage | tokens on/off | mode vanilla/blockout/refined | aura subtle/moderate | zoom 48/64/96 | shot NAME'
p=home/'checker-command.txt'
assert not p.exists(), 'Previous command still pending'
p.write_text(command)
for _ in range(100):
    if not p.exists():break
    time.sleep(.1)
else:raise SystemExit('Game did not consume command; check session/game.log')
if command.startswith('shot '):
    name=command.split()[1];src=home/(name+'.png')
    for _ in range(100):
        if src.exists() and src.stat().st_size:break
        time.sleep(.1)
    print(src)
else:print('Done:',command)
