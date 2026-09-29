#!/usr/bin/env python3
"""Eight independent Daikara cold starts in the isolated offline fixture."""
import json
import argparse
import subprocess
import sys
import time
from pathlib import Path
from launch_fixture import SESSION
from run_norgos_validation import stop_started

ADDON=Path(__file__).resolve().parents[1]
PROCESSES=SESSION/'processes.json'

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--rework',action='store_true',help='replace DEFAULT L1, VOLCANO L1 and VOLCANO L4 evidence')
    parser.add_argument('--remaining',action='store_true',help='replace the other five 64px scene records')
    parser.add_argument('--replace-all',action='store_true',help='replace all eight scene records')
    args=parser.parse_args()
    if sum((args.rework,args.remaining,args.replace_all))>1:parser.error('choose only one replacement set')
    all_scenes=tuple((layout,level) for layout in ('default','volcano') for level in (1,2,3,4))
    primary=(('default',1),('volcano',1),('volcano',4))
    scenes=primary if args.rework else tuple(s for s in all_scenes if s not in primary) if args.remaining else all_scenes
    for layout,level in scenes:
        label=f'{layout}-L{level}'
        launch=subprocess.run([sys.executable,str(ADDON/'tools/launch_fixture.py'),
            '--shaders','--tiles','64','--terrain','refined','--resolution','1920x1080',
            '--birth','Human:Cornac:Male:Berserker'],cwd=ADDON,capture_output=True,text=True)
        if launch.returncode:raise RuntimeError(f'{label} launch failed: {launch.stdout} {launch.stderr}')
        meta=json.loads(PROCESSES.read_text())
        try:
            print('START',label,launch.stdout.strip(),flush=True)
            home=SESSION/'home/.t-engine/4.0/tome'
            for _ in range(180):
                if home.is_dir():break
                time.sleep(.5)
            else:raise RuntimeError(f'{label}: no fixture home')
            time.sleep(3)
            cmd=[sys.executable,str(ADDON/'tools/capture_daikara_20260928.py'),
                '--layout',layout,'--level',str(level)]
            if args.rework or args.remaining or args.replace_all:cmd.append('--replace')
            driver=subprocess.run(cmd,cwd=ADDON,capture_output=True,text=True,timeout=300)
            print(driver.stdout,flush=True)
            if driver.returncode:raise RuntimeError(f'{label}: {driver.stderr}')
        finally:
            stop_started(meta)
            print('STOP',label,meta['game'],meta['xvfb'],flush=True)
    survey=ADDON/'evidence/daikara-20260928/survey.json'
    data=json.loads(survey.read_text())
    assert len(data['zones'])==8 and {z['label'] for z in data['zones']}=={
        f'daikara-L{level}-{layout}' for layout in ('default','volcano') for level in (1,2,3,4)}
    data['complete']=True
    survey.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__':main()
