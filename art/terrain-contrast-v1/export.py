#!/usr/bin/env python3
"""Readability finish on frozen accepted wall exports; no runtime changes.
Original exporters and their downstream families remain frozen byte-for-byte.
Run this after original family exporters to reproduce the selected finish.
"""
from pathlib import Path
from PIL import Image, ImageEnhance, ImageOps, ImageDraw, ImageStat
import hashlib,json
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
GAINS={'sand':.78,'maze':.55,'crystal':.65}
PENDING_GAINS={'korpul':.37,'korpul-dark':.37}

def lab(im):
 a=np.asarray(im.convert('RGBA'),dtype=float)/255
 rgb=a[:,:,:3]*a[:,:,3:4]
 rgb=np.where(rgb<=.04045,rgb/12.92,((rgb+.055)/1.055)**2.4)
 xyz=rgb@np.array([[.4124564,.3575761,.1804375],[.2126729,.7151522,.0721750],[.0193339,.1191920,.9503041]]).T
 xyz/=np.array([.95047,1,1.08883])
 f=np.where(xyz>216/24389,np.cbrt(xyz),xyz*(24389/27)/116+16/116)
 return np.stack([116*f[:,:,1]-16,500*(f[:,:,0]-f[:,:,1]),200*(f[:,:,1]-f[:,:,2])],-1).mean((0,1))

def floor(family,p):
 return ROOT/'data/gfx/refined'/('korpul' if family in ('maze','korpul-dark') else family)/(f'floor-a-0-{p}.png' if family in ('maze','korpul','korpul-dark') else f'floor{p}.png')

def finish(im,family,mask,p):
 if family=='korpul-dark':
  base=Image.open(HERE/'frozen-inputs/korpul'/f'wall-{mask}-{p}.png').convert('RGBA')
  return ImageEnhance.Brightness(finish(base,'korpul',mask,p)).enhance(.60)
 out=ImageEnhance.Brightness(im).enhance(GAINS[family])
 if family=='sand':
  # Preserve actual generated rock planes rather than synthesizing floor grain.
  src=Image.open(ROOT/'art/terrain-sandworm-v1/masters/sand-wall-v1.png').convert('RGBA')
  body=src.crop(src.getchannel('A').getbbox());w,h=body.size
  top=body.crop((int(w*.22),int(h*.14),int(w*.78),int(h*.44)))
  top=ImageOps.fit(top,(128,128),method=Image.Resampling.LANCZOS)
  top=ImageOps.colorize(ImageOps.grayscale(top),(30,12,1),(154,101,48)).convert('RGBA')
  top=ImageEnhance.Brightness(top).enhance(48/ImageStat.Stat(top.convert('L')).mean[0])
  if p:top=ImageEnhance.Brightness(top).enhance(.88)
  # Keep the accepted south vertical face, now below a textured raised cap.
  out=top
  if not mask&4:
   face=im.crop((0,90,128,128))
   out.paste(ImageEnhance.Brightness(face).enhance(.45),(0,90))
 if family=='crystal':
  r,g,b,a=im.split()
  out=Image.merge('RGBA',(r.point(lambda v:int(v*.52)),g.point(lambda v:int(v*.60)),b.point(lambda v:int(v*.91)),a))
 # Exposed edges only; connected wall tops carry no false floor gutters.
 d=ImageDraw.Draw(out)
 scale=.9 if p else 1
 lip=tuple(int(v*scale) for v in ((104,92,71) if family=='sand' else (85,91,99) if family=='crystal' else (89,86,78)))
 dark=tuple(int(v*scale) for v in (13,14,17))
 if not mask&1:d.rectangle((0,0,127,2),fill=lip);d.line((0,3,127,3),fill=dark,width=1)
 if not mask&8:d.rectangle((0,0,2,127),fill=lip)
 if not mask&2:d.rectangle((124,0,127,127),fill=dark)
 if not mask&4:
  y=88 if family in ('sand','crystal') else 117
  d.line((0,y,127,y),fill=lip,width=3)
  d.line((0,y+3,127,y+3),fill=dark,width=2)
  d.rectangle((0,125,127,127),fill=dark)
 return out

def main():
 report={'imagegen_calls':0,'files':{},'metrics':{}}
 for family in GAINS:
  for src in sorted((HERE/'frozen-inputs'/family).glob('*.png')):
   mask,p=map(int,src.stem.split('-')[-2:]);old=Image.open(src).convert('RGBA')
   if src.name.startswith('door-'):
    new=old.copy()
    boxes=((0,84,20,124),(108,84,128,124)) if 'horizontal' in src.name else ((4,0,44,20),(4,108,44,128))
    toned=ImageEnhance.Brightness(old).enhance(GAINS[family])
    for box in boxes:new.paste(toned.crop(box),box[:2])
   else:new=finish(old,family,mask,p)
   dst=ROOT/'data/gfx/refined'/family/src.name
   new.save(dst,optimize=True)
   selected=HERE/'exports'/family/src.name;selected.parent.mkdir(parents=True,exist_ok=True);selected.write_bytes(dst.read_bytes())
   report['files'][str(dst.relative_to(ROOT))]={'before':hashlib.sha256(src.read_bytes()).hexdigest(),'after':hashlib.sha256(dst.read_bytes()).hexdigest()}
   if mask==15 and not src.name.startswith('door-'):
    f=lab(Image.open(floor(family,p)));b=lab(old);a=lab(new)
    report['metrics'][f'{family}-{p}']={'before_delta_e':float(np.linalg.norm(f-b)),'after_delta_e':float(np.linalg.norm(f-a)),'floor_L':float(f[0]),'before_wall_L':float(b[0]),'after_wall_L':float(a[0])}
  for size in (48,64,96):
   sheet=Image.new('RGB',(10*size,8*size))
   for y in range(8):
    for x in range(10):
     p=(x+y)%2
     if 2<=x<=7 and 2<=y<=5:
      mask=sum(bit for dx,dy,bit in ((0,-1,1),(1,0,2),(0,1,4),(-1,0,8)) if 2<=x+dx<=7 and 2<=y+dy<=5)
      path=ROOT/'data/gfx/refined'/family/f'{"old-wall" if family=="maze" else "wall"}-{mask}-{p}.png'
     else:path=floor(family,p)
     sheet.paste(Image.open(path).convert('RGB').resize((size,size),Image.Resampling.LANCZOS),(x*size,y*size))
   dest=HERE/'review'/f'{family}-{size}.png';dest.parent.mkdir(exist_ok=True);sheet.save(dest)
 (HERE/'export-manifest.json').write_text(json.dumps(report,indent=2)+'\n')
 import runpy
 runpy.run_path(str(HERE/'sync_selected.py'))
 print(json.dumps(report['metrics'],indent=2))
if __name__=='__main__':main()
