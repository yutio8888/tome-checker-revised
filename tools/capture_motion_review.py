#!/usr/bin/env python3
"""Lossless X11 frame capture of ONLY the disposable :162 fixture; no launch."""
import argparse, hashlib, json, os, shutil, subprocess, sys, time
from pathlib import Path
from PIL import ImageGrab
ROOT=Path(__file__).resolve().parents[1]
SESSION=ROOT.parents[2]/'demo/checkerboard-v3/session'
HOME=SESSION/'home/.t-engine/4.0/tome'
OUT=ROOT/'evidence/motion-review-v063'
p=argparse.ArgumentParser();p.add_argument('clip',choices=['walk','special','twitch-off','rush','path-camera']);p.add_argument('--output',type=Path,default=OUT);args=p.parse_args()
OUT=args.output.resolve();assert OUT.is_relative_to(ROOT/'evidence'),'Keep evidence inside the addon repository'
OUT.mkdir(exist_ok=True,parents=True)
plan=json.loads((SESSION/'launch-plan.json').read_text());assert plan['fixture']
# A resize during cold launch can move the window despite SDL's position hint.
# Place only this disposable process at the capture origin; never crop a bad grab.
from launch_fixture import DEPS
process=json.loads((SESSION/'processes.json').read_text());assert process['display']==':162'
assert str(SESSION/'runtime/t-engine').encode() in Path('/proc',str(process['game']),'cmdline').read_bytes()
env=dict(os.environ,DISPLAY=':162',LD_LIBRARY_PATH=str(DEPS/'lib/x86_64-linux-gnu'))
def x11(*values):
 return subprocess.check_output([str(DEPS/'bin/xdotool'),*values],env=env,text=True).strip()
window=x11('search','--pid',str(process['game'])).splitlines()[0]
x11('windowmove',window,'0','0')
geometry=dict(line.split('=',1) for line in x11('getwindowgeometry','--shell',window).splitlines())
assert geometry['X']=='0' and geometry['Y']=='0'
assert geometry['WIDTH']+'x'+geometry['HEIGHT']==plan['resolution']
assert (HOME/'motion-setup.txt').exists()
for suffix in ['.tsv','-done.txt','-ERROR.txt']:(HOME/('motion-'+args.clip+suffix)).unlink(missing_ok=True)
proc=subprocess.Popen([sys.executable,str(ROOT/'tools/fixture_debug.py'),"motion.start('"+args.clip+"')"],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
frames=[];stamp=[];t0=time.monotonic();deadline=t0
while time.monotonic()-t0<3.5:
 now=time.monotonic()
 if now<deadline:time.sleep(deadline-now)
 start=time.monotonic();im=ImageGrab.grab(xdisplay=':162');frames.append(im);stamp.append({'frame':len(frames)-1,'start_ms':round((start-t0)*1000,3),'end_ms':round((time.monotonic()-t0)*1000,3)})
 deadline+=.04
 if deadline<time.monotonic():deadline=time.monotonic()
stdout=proc.communicate(timeout=10)[0];(OUT/(args.clip+'-command.txt')).write_text(stdout)
assert proc.returncode==0,stdout
assert not (HOME/('motion-'+args.clip+'-ERROR.txt')).exists(),(HOME/('motion-'+args.clip+'-ERROR.txt')).read_text() if (HOME/('motion-'+args.clip+'-ERROR.txt')).exists() else ''
assert (HOME/('motion-'+args.clip+'-done.txt')).exists(),'rendered sequence not finished'
durations=[max(1,round(stamp[i+1]['start_ms']-stamp[i]['start_ms'])) for i in range(len(stamp)-1)]+[40]
path=OUT/(args.clip+'.png')
frames[0].save(path,save_all=True,append_images=frames[1:],duration=durations,loop=0,disposal=0,blend=0,compress_level=6)
metadata={'display':':162','format':'lossless APNG','resolution':list(frames[0].size),'clip':args.clip,'frames':len(frames),'timestamps':stamp,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'edited':False,'note':'Full X11 frames; no crop, resize, recolor, interpolation or playback-speed change. Duplicate frames may be coalesced losslessly by Pillow. Lua timestamps use independent origin.'}
metadata['window_geometry']=geometry
(OUT/(args.clip+'.json')).write_text(json.dumps(metadata,indent=2)+'\n')
for name in ['setup.txt',args.clip+'.tsv',args.clip+'-done.txt']:shutil.copy2(HOME/('motion-'+name),OUT/('motion-'+name))
print(args.clip,len(frames),'frames',path.stat().st_size,'bytes')
