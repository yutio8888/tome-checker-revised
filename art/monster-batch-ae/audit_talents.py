"""Reproduce AE's static leaf/inherited talent mode and appearance-writer audit."""
import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ADDON = HERE.parents[1]
MODULE = ADDON.parents[2] / 'game/modules/tome'
EVIDENCE = ADDON / 'evidence/monster-batch-ae-20261001'

def run():
    identities = json.loads((EVIDENCE / 'source-contracts.json').read_text())['identities']
    definitions = {}
    for p in (MODULE / 'data/talents').rglob('*.lua'):
        chunks = re.split(r'(?m)^(?:newTalent|uberTalent)\{',p.read_text())
        for chunk in chunks[1:]:
            name = re.search(r'\bname\s*=\s*"([^"]+)"',chunk)
            short = re.search(r'\bshort_name\s*=\s*"([^"]+)"',chunk)
            if not name: continue
            key = 'T_'+(short[1] if short else re.sub('[^A-Z0-9]','_',name[1].upper()))
            mode = re.search(r'\bmode\s*=\s*"([^"]+)"',chunk)
            definitions[key] = dict(path=str(p.relative_to(MODULE)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),name=name[1],mode=mode[1] if mode else 'activated (default)',display_hits=[l.strip() for l in chunk.splitlines() if re.search(r'(?:self|who|target)\.(?:image|shader|moddable_tile|add_mos|add_displays|type|subtype)\s*=(?!=)|addShaderAura|updateModdableTile|replace_display',l)])
    out = {}
    for i in identities:
        base = ADDON.parents[2] / i['base_source']['path']
        line = i['base_source']['line']
        lines = base.read_text().splitlines()
        end = next((n for n in range(line,len(lines)) if lines[n].startswith('newEntity{')),len(lines))
        inherited = re.findall(r'Talents\.(T_[A-Z0-9_]+)','\n'.join(lines[line-1:end]))
        talents = list(dict.fromkeys(i['talents']+inherited+(['T_MULTIPLY'] if i['id']=='hummerhorn' else [])))
        assert all(t in definitions for t in talents), (i['id'],talents)
        out[i['id']] = {t:definitions[t] for t in talents}
    (EVIDENCE / 'talent-contracts.json').write_text(json.dumps(out,indent=2)+'\n')
    print('Resolved',sum(len(ts) for ts in out.values()),'leaf/inherited talents across',len(out),'identities')

if __name__=='__main__': run()
