#!/usr/bin/env python3
"""Batch 5 terrain: source probe and per-level cold-start validation.

Isolated offline fixture only (tools/launch_fixture.py). Every validation scene
is its own cold start; the probe visits all scenes in one process because it
only reads final native grids. Every process this tool starts is stopped.
"""
import argparse,json,shutil,statistics,subprocess,sys,time
from pathlib import Path
from PIL import Image,ImageStat
from capture_korpul import Fixture,HOME,ROOT,SESSION,digest,png_size
from run_norgos_validation import stop_started
OUT=ROOT/'evidence/batch5-20260929';SHOTS=OUT/'screenshots'
# (zone, level, enter options, label suffix)
PROBE_SCENES=[
 ('telmur',1,{},'roomer'),('telmur',2,{},'roomer'),('telmur',3,{},'roomer'),('telmur',4,{},'roomer'),('telmur',5,{},'roomer'),
 ('ancient-elven-ruins',1,{},'tileset'),('ancient-elven-ruins',2,{},'tileset'),('ancient-elven-ruins',3,{},'crypt'),
 ('vor-armoury',1,{},'tileset'),('vor-armoury',2,{},'static'),
 ('briagh-lair',1,{},'cavern'),
 ('valley-moon-caverns',1,{},'cavern'),('valley-moon-caverns',2,{},'cavern'),
 ('flooded-cave',1,{},'cavern'),('flooded-cave',2,{},'static'),
 ('temple-of-creation',1,{},'static'),('temple-of-creation',2,{},'cavern'),('temple-of-creation',3,{},'static'),
 ('orc-breeding-pit',1,{},'static'),('orc-breeding-pit',2,{},'cavern'),('orc-breeding-pit',3,{},'cavern'),
 ('shertul-fortress',1,{},'static'),
 ('charred-scar',1,{},'static'),('demon-plane',1,{},'forest'),
 ('rak-shor-pride',1,{},'mapscript'),('rak-shor-pride',2,{},'roomer'),('rak-shor-pride',3,{},'roomer'),
]
SCENES=[s for s in PROBE_SCENES]
def label(zone,level,suffix):return f'{zone}-{suffix}-L{level}'
def lua_opts(opts):
 return '{'+','.join(f"{k}={'true' if v else 'false'}" for k,v in opts.items())+'}'
def read(name):
 p=HOME/name;value=json.loads(p.read_text());p.unlink();return value
def launch():
 running=[]
 for proc in Path('/proc').iterdir():
  try:argv0=(proc/'cmdline').read_bytes().split(b'\0')[0].decode(errors='replace')
  except OSError:continue
  if argv0.endswith('session/runtime/t-engine') or argv0.endswith('Xvfb-local'):running.append(proc.name)
 if running:raise RuntimeError('another fixture process is running: '+' '.join(running))
 call=subprocess.run([sys.executable,str(ROOT/'tools/launch_fixture.py'),'--shaders','--tiles','64','--terrain','refined',
  '--resolution','1920x1080','--birth','Human:Cornac:Male:Berserker'],cwd=ROOT,capture_output=True,text=True)
 if call.returncode:raise RuntimeError(call.stdout+call.stderr)
 time.sleep(2)
 return json.loads((SESSION/'processes.json').read_text())

def probe(args):
 OUT.mkdir(parents=True,exist_ok=True);meta=launch();f=Fixture();result={'scenes':[]}
 name='probe.json' if not args.zone else f'probe-{args.zone}.json'
 try:
  f.lua("ms=dofile('/data-checker-fixture/monster-live_map_survey.lua');ms.setup()")
  for zone,level,opts,suffix in PROBE_SCENES:
   if args.zone and args.zone!=zone:continue
   try:
    f.lua(f"ms.dump('/b5-enter.json',ms.enter('{zone}',{level},{lua_opts(opts)}))");enter=read('b5-enter.json')
    f.lua("ms.caveClearDialogs();ms.dump('/b5-probe.json',ms.batch4Probe())");rows=read('b5-probe.json')
    result['scenes'].append({'label':label(zone,level,suffix),'enter':enter,'probe':rows})
    print('PROBE',label(zone,level,suffix),len(rows['rows']),flush=True)
   except Exception as e:
    result['scenes'].append({'label':label(zone,level,suffix),'error':str(e)[-1500:]})
    print('PROBE-ERROR',label(zone,level,suffix),str(e)[-300:],flush=True)
   (OUT/name).write_text(json.dumps(result,ensure_ascii=False,indent=1)+'\n')
 finally:
  (OUT/'probe-transcript.txt').write_text((''.join(f.transcript)+f.new_log()).rstrip()+'\n')
  stop_started(meta);print('STOP probe',flush=True)

VALIDATE_SCENES=[s for s in PROBE_SCENES if s[0]!='rak-shor-pride']

def validate(args):
 import run_batch4_validation as b4
 b4.OUT=OUT;b4.SHOTS=SHOTS
 OUT.mkdir(parents=True,exist_ok=True);path=OUT/'survey.json'
 survey=json.loads(path.read_text()) if path.exists() else {'scenes':[]}
 for zone,level,opts,suffix in VALIDATE_SCENES:
  name=label(zone,level,suffix)
  if args.zone and args.zone!=zone or args.level and args.level!=level or args.suffix and args.suffix!=suffix:continue
  if args.redo:survey['scenes']=[s for s in survey['scenes'] if s['label']!=name]
  elif any(s['label']==name for s in survey['scenes']):continue
  meta=launch()
  try:
   row=b4.capture(zone,level,opts,suffix);survey['scenes'].append(row)
   path.write_text(json.dumps(survey,ensure_ascii=False,indent=1)+'\n')
   print('PASS',name,row['census']['supported'],row['census']['owned'],row['census']['native'],
    row.get('lit_pixels',{}).get('relative_gap'),flush=True)
  except Exception as e:
   print('FAIL',name,str(e)[-600:],flush=True)
  finally:stop_started(meta);print('STOP',name,flush=True)

def main():
 p=argparse.ArgumentParser();p.add_argument('command',choices=('probe','validate'))
 p.add_argument('--zone');p.add_argument('--level',type=int);p.add_argument('--suffix');p.add_argument('--redo',action='store_true')
 a=p.parse_args()
 (probe if a.command=='probe' else validate)(a)
if __name__=='__main__':main()
