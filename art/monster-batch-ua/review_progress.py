"""Small-size previews of completed calls; deterministic exporter, no painting."""
import json,math,subprocess
from pathlib import Path
from PIL import Image,ImageDraw
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
for p in HERE.glob('masters/*-v1.png'):
 id_=p.stem[:-3];c=Image.new('RGBA',(270,120),(46,50,46,255));d=ImageDraw.Draw(c);d.text((4,2),id_,fill='white');x=4
 for size in (48,64,96):
  target=HERE/f'sprites/{size}/{id_}.png';target.parent.mkdir(parents=True,exist_ok=True)
  subprocess.run([str(ROOT/'tools/bin/export_token'),str(p),str(target),str(size)],check=True,capture_output=True)
  c.alpha_composite(Image.open(target),(x,20+(96-size)//2));x+=size+10
 c.convert('RGB').save(HERE/f'review/{id_}-v1-48-64-96.png')
