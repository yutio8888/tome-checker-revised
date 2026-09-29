#!/usr/bin/env python3
"""Rak'Shor Pride (bone.lua) board terrain: per-level cold-start validation.

Isolated offline fixture only (tools/launch_fixture.py). Same capture as
batch 5 (tools/run_batch4_validation.capture): census, lit pixels, 48/64/96
open, natural FOV, feature, exit, remembered, Native/Blockout/Refined round
trip with rule snapshots, dig repair. One cold start per level; every process
this tool starts is stopped.
"""
import argparse,json
from pathlib import Path
import run_batch5_validation as b5
from run_batch5_validation import ROOT,label,launch,stop_started
OUT=ROOT/'evidence/rakshor-20260929';SHOTS=OUT/'screenshots'
SCENES=[s for s in b5.PROBE_SCENES if s[0]=='rak-shor-pride']
def validate(args):
 import run_batch4_validation as b4
 b4.OUT=OUT;b4.SHOTS=SHOTS
 OUT.mkdir(parents=True,exist_ok=True);path=OUT/'survey.json'
 survey=json.loads(path.read_text()) if path.exists() else {'scenes':[]}
 for zone,level,opts,suffix in SCENES:
  name=label(zone,level,suffix)
  if args.level and args.level!=level:continue
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
 p=argparse.ArgumentParser();p.add_argument('--level',type=int);p.add_argument('--redo',action='store_true')
 validate(p.parse_args())
if __name__=='__main__':main()
