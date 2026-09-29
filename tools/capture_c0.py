#!/usr/bin/env python3
"""0.6.3 C0 comparisons in the running isolated fixture; never launches it."""
import argparse
import json
import csv
import shutil
import subprocess
import sys
from pathlib import Path
from capture_korpul import Fixture, HOME, ROOT, SESSION, digest, png_size

OUT=ROOT/'evidence/runtime-v063'
NEW={'giant white rat':'giant-white-rat','giant grey rat':'giant-grey-rat',
     'green worm mass':'green-worm-mass','copperhead snake':'copperhead-snake'}
SEEDS={'DEFAULT':537301,'HIDEOUT':537302}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--layout',choices=tuple(SEEDS),required=True)
    args=parser.parse_args();layout=args.layout
    fixture=Fixture();OUT.mkdir(parents=True,exist_ok=True);(OUT/'screenshots').mkdir(exist_ok=True)
    manifest=json.loads((ROOT/'data/token-manifest.json').read_text())
    assert manifest['version']=='0.6.3' and len(manifest['assets'])==37
    for item in manifest['assets']:
        assert digest(ROOT/'data/gfx/tokens'/(item['id']+'.png'))==item['runtime_sha256']
    installed=SESSION/'runtime/game/addons/tome-checker-fixture/data/monster-live_c0_scene.lua'
    assert digest(installed)==digest(ROOT/'tests/live_c0_scene.lua')
    result={'version':'0.6.3','hud':'0.2.4','layout':layout,'seed_input':SEEDS[layout],
            'shaders':True,'arranged':True,'frozen_ai':True,'edited':False,'complete':False,'shots':[],
            'manifest_sha256':digest(ROOT/'data/token-manifest.json'),'launch':json.loads((SESSION/'launch-plan.json').read_text())}
    def save():
        (OUT/('capture-'+layout.lower()+'.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
        (OUT/('validation-'+layout.lower()+'.txt')).write_text((''.join(fixture.transcript)+fixture.new_log()).rstrip()+'\n')
        for pattern in (f'c0-*-{layout.lower()}*.txt',f'c0-*-{layout.lower()}*.tsv',f'korpul-natural-{layout.lower()}.tsv'):
            for src in HOME.glob(pattern):shutil.copy2(src,OUT/src.name)
    def shot(phase,mode,tile):
        stem=f'c0-{layout.lower()}-{phase}-{mode}-{tile}'
        fixture.lua("game:setResolution('1920x1080 Windowed',true);"
                    f"config.settings.tome.gfx.size='{tile}x{tile}';game:setupDisplayMode(false);"
                    f"c0.mode({'true' if mode=='tokens' else 'false'});c0.dump('{phase}')")
        rules=(HOME/f'c0-rules-{layout.lower()}-{phase}.txt').read_bytes()
        tsv=HOME/f'c0-scene-{layout.lower()}-{phase}.tsv'
        rows=list(csv.DictReader(tsv.open(),delimiter='\t'))
        assert len(rows)>=(7 if phase=='baseline' else 9)
        for row in rows:
            expected=NEW.get(row['name'])
            if expected:assert row['token']==(expected if mode=='tokens' else 'native')
        source=HOME/(stem+'.png');source.unlink(missing_ok=True)
        capture=subprocess.run([sys.executable,str(ROOT/'tools/fixture_command.py'),'shot',stem],capture_output=True,text=True,timeout=25)
        fixture.transcript.append(capture.stdout+capture.stderr);fixture.check_log()
        assert capture.returncode==0 and png_size(source)==(1920,1080)
        target=OUT/'screenshots'/source.name;shutil.copy2(source,target)
        fixture.lua(f"c0.dump('{phase}')")
        assert rules==(HOME/f'c0-rules-{layout.lower()}-{phase}.txt').read_bytes()
        state=OUT/(stem+'.tsv');shutil.copy2(tsv,state)
        result['shots'].append(dict(file='screenshots/'+target.name,sha256=digest(target),resolution=[1920,1080],
             phase=phase,mode=mode,tile=tile,actor_state=state.name,rules_sha256=digest(HOME/f'c0-rules-{layout.lower()}-{phase}.txt')))
        save();return rules
    try:
        fixture.lua("assert(config.settings.cheat and config.settings.disable_all_connectivity and not profile.auth);"
                    "assert(core.shader.active(4));if not game.checker_staged then game:checkerStage() end;"
                    "assert(#require('mod.class.CheckerTokens').catalog==37);"
                    "game:checkerSetTokensEnabled(true);game:checkerSetMode('refined');"
                    "c0=dofile('/data-checker-fixture/monster-live_c0_scene.lua');"
                    f"c0.enter('{layout}',{SEEDS[layout]})")
        # Identical terrain, positions, stats and turn; only actor art differs.
        native=shot('baseline','native',64)
        refined=shot('baseline','tokens',64)
        assert native==refined,'actor art toggle changed native gameplay state'
        if layout=='DEFAULT':assert shot('baseline','tokens',48)==refined
        else:assert shot('baseline','tokens',96)==refined
        fixture.lua('c0.multiply();c0.states()')
        shot('states','tokens',64)
        fixture.lua('c0.skills()')
        fixture.check_log();result['complete']=True;save()
        print(layout,'PASS',len(result['shots']),'unedited screenshots; real Multiply and native acid/poison action handlers')
    finally:save()

if __name__=='__main__':main()
