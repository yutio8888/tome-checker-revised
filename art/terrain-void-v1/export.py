#!/usr/bin/env python3
"""Export reviewed void and floating-platform masters as connected board cells."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps
import hashlib, json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
MASTERS=HERE/'masters'
OUT=ROOT/'data/gfx/refined/void'
OUT.mkdir(parents=True,exist_ok=True)
SIZE=128

def read(name):
    return Image.open(MASTERS/(name+'-v1.png')).convert('RGB').resize((SIZE,SIZE),Image.Resampling.LANCZOS)
def paint(name,im,parity):
    if parity: im=ImageEnhance.Brightness(im).enhance(.84)
    im.save(OUT/(name+str(parity)+'.png'))
def edge(source,mask,kind):
    im=source.copy();draw=ImageDraw.Draw(im)
    # N/E/S/W: quiet, broad shadow faces only where a wall meets walkable
    # floor. Joined faces have no outline, so contiguous walls read as mass.
    if kind=='rift':
        face=(35,29,59)
    else:
        face=(65,64,83)
    if not mask&1:
        draw.rectangle((0,0,127,9),fill=face)
    if not mask&2:
        draw.rectangle((118,0,127,127),fill=face)
    if not mask&4:
        draw.rectangle((0,118,127,127),fill=face)
    if not mask&8:
        draw.rectangle((0,0,9,127),fill=face)
    return im

floor=read('void-walkable-platform')
# Retain a little of the painted grain, suppressing the busy microtexture.
# The generated master remains the sole material source.
rift=Image.blend(read('void-blocked-fracture').filter(ImageFilter.GaussianBlur(10)),
                 read('void-blocked-fracture'),.08)
rocks=read('space-floating-platform')
space=ImageOps.colorize(ImageOps.grayscale(rift),(8,10,26),(38,39,76)).convert('RGB')
space=ImageEnhance.Brightness(space).enhance(.82)
for p in (0,1):
    paint('floor',floor,p)
    paint('space',space,p)
    for mask in range(16):
        paint(f'rift-{mask}-',edge(rift,mask,'rift'),p)
        paint(f'rocks-{mask}-',edge(rocks,mask,'rocks'),p)

files={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(OUT.glob('*.png'))
       if not p.name.startswith('rocks-tree-')}
masters={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(MASTERS.glob('*.png'))}
(HERE/'export-manifest.json').write_text(json.dumps({'masters':masters,'files':files,'imagegen_calls':3},indent=2)+'\n')
