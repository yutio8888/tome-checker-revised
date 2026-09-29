#!/usr/bin/env python3
"""Fixture-only probe: force a native Abashed platform move and census repaint."""
import json,subprocess,sys,time
from pathlib import Path
from run_norgos_validation import stop_started
from launch_fixture import SESSION
ROOT=Path(__file__).resolve().parents[1]
HOME=SESSION/'home/.t-engine/4.0/tome'
OUT=ROOT/'evidence/void-20260928'
cmd=[sys.executable,str(ROOT/'tools/launch_fixture.py'),'--shaders','--tiles','64','--terrain','refined','--resolution','1920x1080','--birth','Human:Cornac:Male:Berserker']
r=subprocess.run(cmd,capture_output=True,text=True)
if r.returncode:raise RuntimeError(r.stdout+r.stderr)
meta=json.loads((SESSION/'processes.json').read_text())
try:
 for _ in range(100):
  if HOME.is_dir():break
  time.sleep(.2)
 else:raise RuntimeError('fixture home not ready')
 time.sleep(2)
 code="""assert(core.shader.active(4));ms=dofile('/data-checker-fixture/monster-live_map_survey.lua');ms.setup();ms.enter('abashed-expanse',1);local before=ms.terrainCensus();local old_turn=game.turn;local data=game.level.data;local moved=0;local attempts=0;local ok=true;local err=nil;for trial=1,30 do local pos={};for i,p in ipairs(game.level.pods) do pos[i]={p.x1,p.y1} end;data.next_move=1;data.teleport_zones=true;game.turn=10;ok,err=pcall(function() game:onTurn() end);attempts=trial;if not ok then break end;for i,p in ipairs(game.level.pods) do if p.x1~=pos[i][1] or p.y1~=pos[i][2] then moved=moved+1 end end;if moved>0 then break end end;local after=ms.terrainCensus();ms.dump('/void-platform-motion.json',{ok=ok,error=err or false,before=before,after=after,moved=moved,attempts=attempts,pods=#game.level.pods});game.turn=old_turn"""
 r=subprocess.run([sys.executable,str(ROOT/'tools/fixture_debug.py'),code],capture_output=True,text=True,timeout=90)
 (OUT/'platform-motion-validation.txt').write_text(r.stdout+r.stderr)
 if r.returncode:raise RuntimeError(r.stdout+r.stderr)
 result=json.loads((HOME/'void-platform-motion.json').read_text())
 (OUT/'platform-motion.json').write_text(json.dumps(result,indent=2)+'\n')
 assert result['ok'] and result['moved']>0 and result['after']['native']==0,result
 print(result)
finally:stop_started(meta)
