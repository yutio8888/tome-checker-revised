#!/usr/bin/env python3
"""Derive muted graveyard props from existing board grass and stone materials."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps
import hashlib, json
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
OUT=ROOT/'data/gfx/refined/graveyard'
OUT.mkdir(parents=True,exist_ok=True)
S=128

def source(path): return Image.open(ROOT/path).convert('RGB')
grass=source('data/gfx/refined/grass0.png')
stone=source('data/gfx/refined/korpul/wall-15-0.png')
road=source('data/gfx/refined/korpul/floor-a-0-0.png')

def polygon_mask(points):
    im=Image.new('L',(S,S));ImageDraw.Draw(im).polygon(points,fill=255)
    return im

def fill_shape(base,points,material):
    mask=polygon_mask(points)
    base.paste(material,(0,0),mask)
    return base

def make(kind):
    base=(grass if kind=='grave' else road).copy()
    d=ImageDraw.Draw(base)
    if kind=='grave':
        # A small upright headstone and low plinth: unmistakably blocking,
        # with the grass from the same board family covering the whole cell.
        d.ellipse((23,94,106,114),fill=(43,48,38))
        fill_shape(base,[(35,91),(99,91),(108,101),(27,101)],stone)
        d.line((35,91,99,91),fill=(159,159,147),width=3)
        fill_shape(base,[(42,33),(51,23),(80,23),(91,34),(91,86),(42,86)],stone)
        d=ImageDraw.Draw(base)
        d.line([(42,84),(42,33),(51,23),(80,23),(91,34)],fill=(162,163,154),width=4)
        d.line((52,47,80,47),fill=(56,58,57),width=4)
        d.line((58,61,74,61),fill=(58,60,59),width=3)
        d.line((66,53,66,74),fill=(58,60,59),width=3)
    elif kind.startswith('coffin'):
        d.ellipse((19,84,111,113),fill=(36,42,38))
        hull=[(38,20),(87,20),(102,38),(102,91),(88,104),(38,104),(24,91),(24,38)]
        fill_shape(base,hull,stone)
        d=ImageDraw.Draw(base)
        d.line(hull+[hull[0]],fill=(44,47,49),width=5)
        if kind=='coffin':
            d.polygon([(43,29),(83,29),(92,41),(92,89),(83,95),(43,95),(34,89),(34,41)],fill=(95,82,73))
            d.line([(42,34),(84,34),(90,42)],fill=(174,151,126),width=3)
            d.line((63,43,63,80),fill=(175,150,110),width=4)
            d.line((49,59,77,59),fill=(175,150,110),width=4)
        else:
            d.polygon([(43,29),(83,29),(92,41),(92,88),(82,96),(43,96),(34,88),(34,41)],fill=(23,25,32))
            d.line([(43,29),(83,29),(92,41),(92,88)],fill=(115,106,104),width=4)
            d.polygon([(42,85),(83,85),(91,92),(81,97),(43,97),(35,91)],fill=(64,64,69))
    else:
        # Dark open passage in a low stone arch; visible floor makes it clear
        # this marker is an entrance, not another blocking tombstone.
        d.ellipse((21,90,107,113),fill=(48,47,44))
        fill_shape(base,[(25,101),(25,40),(37,25),(88,25),(102,41),(102,101)],stone)
        d=ImageDraw.Draw(base)
        d.rounded_rectangle((40,38,87,105),radius=19,fill=(22,24,29))
        d.line([(41,96),(41,53),(46,42),(59,35),(74,35),(86,46),(86,95)],fill=(179,166,141),width=4)
        d.polygon([(49,95),(78,95),(88,105),(39,105)],fill=(116,108,94))
        d.line((43,105,86,105),fill=(199,186,155),width=3)
    return base

files={}
for kind in ('grave','coffin','coffin-open','mausoleum'):
    master=make(kind)
    for p in (0,1):
        tile=master if p==0 else ImageEnhance.Brightness(master).enhance(.86)
        path=OUT/f'{kind}{p}.png';tile.save(path)
        files[path.name]=hashlib.sha256(path.read_bytes()).hexdigest()
(HERE/'export-manifest.json').write_text(json.dumps({'sources':{
    str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in
    (ROOT/'data/gfx/refined/grass0.png',ROOT/'data/gfx/refined/korpul/wall-15-0.png',ROOT/'data/gfx/refined/korpul/floor-a-0-0.png')},
    'files':files,'imagegen_calls':0},indent=2)+'\n')
