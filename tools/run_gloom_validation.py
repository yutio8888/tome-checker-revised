#!/usr/bin/env python3
"""Six independent shader-enabled cold starts in the isolated offline fixture."""
import argparse,json,subprocess,sys,time
from pathlib import Path
from launch_fixture import SESSION
from run_norgos_validation import stop_started
ROOT=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('--skin',choices=('gloomy','dreamy'))
ap.add_argument('--level',type=int,choices=(1,2,3));ap.add_argument('--replace',action='store_true');args=ap.parse_args()
for skin in ((args.skin,) if args.skin else ('gloomy','dreamy')):
    for level in ((args.level,) if args.level else (1,2,3)):
        label=f'{skin}-L{level}'
        launch=subprocess.run([sys.executable,str(ROOT/'tools/launch_fixture.py'),'--shaders','--tiles','64',
            '--terrain','refined','--resolution','1920x1080','--birth','Human:Cornac:Male:Berserker'],
            cwd=ROOT,capture_output=True,text=True)
        if launch.returncode:raise RuntimeError(f'{label} launch failed: {launch.stdout} {launch.stderr}')
        meta=json.loads((SESSION/'processes.json').read_text())
        try:
            print('START',label,flush=True)
            home=SESSION/'home/.t-engine/4.0/tome'
            for _ in range(180):
                if home.is_dir():break
                time.sleep(.5)
            else:raise RuntimeError(f'{label} no fixture home')
            time.sleep(3)
            result=subprocess.run([sys.executable,str(ROOT/'tools/capture_gloom_20260928.py'),
                '--skin',skin,'--level',str(level),*(['--replace'] if args.replace else [])],cwd=ROOT,capture_output=True,text=True,timeout=300)
            print(result.stdout,flush=True)
            if result.returncode:raise RuntimeError(f'{label}: {result.stderr}')
        finally:
            stop_started(meta)
            print('STOP',label,meta['game'],meta['xvfb'],flush=True)
