from pathlib import Path
from PIL import Image,ImageStat
import json,hashlib,shutil
root=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for family,suite in [('sand','terrain-sandworm-v1'),('crystal','terrain-crystal-v1'),('maze','terrain-maze-v1')]:
 d=root/'art'/suite;mp=d/'export-manifest.json';m=json.loads(mp.read_text())
 for p in (root/'art/terrain-contrast-v1/exports'/family).glob('*.png'):
  out=d/'exports/runtime'/p.name;shutil.copyfile(p,out)
  if isinstance(m['files'],dict):
   m['files'][p.name]=sha(p);m['luminance'][p.name]=ImageStat.Stat(Image.open(p).convert('L')).mean[0]
  else:
   for entry in m['files']:
    if Path(entry['path']).name==p.name:entry['sha256']=sha(p);entry['bytes']=p.stat().st_size
  for size in (48,64,96):
   Image.open(p).resize((size,size),Image.Resampling.LANCZOS).save(d/'review'/str(size)/p.name)
 mp.write_text(json.dumps(m,indent=2)+'\n')
