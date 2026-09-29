#!/usr/bin/env python3
"""Supplemental Daikara exit poses in one isolated fixture process."""
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path
from capture_korpul import Fixture, HOME, ROOT, SESSION, digest, png_size
from run_norgos_validation import stop_started

OUT=ROOT/'evidence/daikara-20260928'
SHOTS=OUT/'screenshots'

def main():
    launch=subprocess.run([sys.executable,str(ROOT/'tools/launch_fixture.py'),
        '--shaders','--tiles','64','--terrain','refined','--resolution','1920x1080',
        '--birth','Human:Cornac:Male:Berserker'],cwd=ROOT,capture_output=True,text=True)
    if launch.returncode:raise RuntimeError(launch.stderr)
    meta=json.loads((SESSION/'processes.json').read_text())
    result={'launch':json.loads((SESSION/'launch-plan.json').read_text()),'poses':[]}
    fixture=Fixture()
    try:
        time.sleep(4)
        fixture.lua("assert(core.shader.active(4));ms=dofile('/data-checker-fixture/monster-live_map_survey.lua');ms.setup()")
        for level,volcano,name,selector in ((1,False,'world','world'),(2,False,'up','up'),
                                           (2,False,'down','down'),(4,True,'caldera-center','center')):
            if not (result['poses'] and result['poses'][-1]['level']==level and
                    result['poses'][-1]['volcano']==volcano):
                fixture.lua(f"ms.enter('daikara',{level},{{volcano={'true' if volcano else 'false'}}});"
                            "ms.dump('/exit-details.json',ms.daikaraDetails())")
                details=json.loads((HOME/'exit-details.json').read_text())
                (HOME/'exit-details.json').unlink()
            if selector=='center':
                target=details['default_down']
                assert target and target['kind']=='lava-floor' and not target['change_level']
            else:
                kind={'world':'stairs-world','up':'stairs-up','down':'stairs-down'}[selector]
                target=next(e for e in details['exits'] if e['kind']==kind)
            x,y=target['x'],target['y']
            fixture.lua(f"ms.focus({x},{y});local m=game.level.map;"
                        f"for px=math.max(0,{x}-17),math.min(m.w-1,{x}+17) do "
                        f"for py=math.max(0,{y}-12),math.min(m.h-1,{y}+12) do "
                        "m.seens(px,py,true);m.infovs(px,py,true);m.remembers(px,py,true) "
                        "end end;m:redisplay();m.changed=true;core.display.forceRedraw()")
            filename=f'daikara-{name}-64'
            source=HOME/(filename+'.png');source.unlink(missing_ok=True)
            shot=subprocess.run([sys.executable,str(ROOT/'tools/fixture_command.py'),'shot',filename],
                                capture_output=True,text=True,timeout=25)
            fixture.transcript.append(shot.stdout+shot.stderr);fixture.check_log()
            assert shot.returncode==0 and source.is_file() and png_size(source)==(1920,1080)
            dest=SHOTS/source.name;shutil.copy2(source,dest)
            result['poses'].append({'level':level,'volcano':volcano,'name':name,'grid':target,
                                    'screenshot':'screenshots/'+dest.name,'sha256':digest(dest)})
            print('OK',name,target,flush=True)
        (OUT/'exit-poses.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
        (OUT/'validation-exits.txt').write_text((''.join(fixture.transcript)+fixture.new_log()).rstrip()+'\n')
    finally:
        stop_started(meta)
        print('STOP',meta['game'],meta['xvfb'],flush=True)

if __name__=='__main__':main()
