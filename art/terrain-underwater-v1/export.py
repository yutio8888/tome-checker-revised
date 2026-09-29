#!/usr/bin/env python3
"""Deterministic 128px board export from reviewed ImageGen underwater masters."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageEnhance, ImageOps
import hashlib, json
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
OUT=ROOT/'data/gfx/refined/underwater'
OUT.mkdir(parents=True,exist_ok=True)
N=128

def read(name):
    return Image.open(HERE/'masters'/f'underwater-{name}-v1.png').convert('RGB').resize((N,N),Image.Resampling.LANCZOS)
def save(name, im, parity):
    if parity: im=ImageEnhance.Brightness(im).enhance(.82)
    im.save(OUT/f'{name}{parity}.png')

def wall_edge(im,mask):
    im=im.copy();d=ImageDraw.Draw(im)
    # Dark edge only when the neighbour is not the same blocking wall family.
    if not mask&1: d.rectangle((0,0,127,8),fill=(14,38,50));d.line((0,9,127,9),fill=(71,118,125),width=2)
    if not mask&2: d.rectangle((119,0,127,127),fill=(14,38,50));d.line((118,0,118,127),fill=(71,118,125),width=2)
    if not mask&4: d.rectangle((0,119,127,127),fill=(14,38,50));d.line((0,118,127,118),fill=(71,118,125),width=2)
    if not mask&8: d.rectangle((0,0,8,127),fill=(14,38,50));d.line((9,0,9,127),fill=(71,118,125),width=2)
    return im
floor=read('floor');wall=read('wall');door=read('door')
for p in (0,1):
    save('floor',floor,p)
    for mask in range(16): save(f'wall-{mask}-',wall_edge(wall,mask),p)
    save('door-closed',door,p)
    opened=floor.copy();d=ImageDraw.Draw(opened)
    d.rectangle((0,0,14,127),fill=(22,57,70));d.rectangle((113,0,127,127),fill=(22,57,70))
    d.line((17,0,17,127),fill=(89,139,145),width=3);d.line((110,0,110,127),fill=(89,139,145),width=3)
    save('door-open',opened,p)
    for direction in ('up','down'):
        stair=Image.open(ROOT/'data/gfx/refined/korpul'/f'stairs-{direction}.png').convert('RGBA').resize((N,N),Image.Resampling.LANCZOS)
        # Preserve the reviewed stair silhouette, colored to the underwater suite.
        gray=ImageOps.grayscale(stair)
        tint=ImageOps.colorize(gray,(14,48,62),(155,204,198)).convert('RGBA')
        tint.putalpha(stair.getchannel('A'))
        base=floor.copy().convert('RGBA');base.alpha_composite(tint)
        save(f'stairs-{direction}',base.convert('RGB'),p)
files={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(OUT.glob('*.png'))}
masters={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((HERE/'masters').glob('*.png'))}
(HERE/'export-manifest.json').write_text(json.dumps({'masters':masters,'files':files,'generator':'art/terrain-underwater-v1/export.py','imagegen_calls':3},indent=2)+'\n')
