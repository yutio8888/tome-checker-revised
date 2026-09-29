#!/usr/bin/env python3
"""Derive a scorched board family from pinned existing painted terrain and native lava."""
from pathlib import Path
from PIL import Image, ImageChops, ImageEnhance, ImageFilter, ImageOps, ImageDraw
import hashlib, json

ROOT=Path(__file__).resolve().parents[2]
MASTERS=Path(__file__).resolve().parent/'masters'
OUT=ROOT/'data/gfx/refined/burnt'
OUT.mkdir(parents=True,exist_ok=True)
def board(name): return Image.open(MASTERS/f'{name.split("/")[-1]}.png').convert('RGB')
def native(name):
    key='native-grass-burnt1.png' if name=='grass_burnt1.png' else 'native-molten-lava.png'
    return Image.open(MASTERS/key).convert('RGB')
def tint(im,black,white): return ImageOps.colorize(ImageOps.grayscale(im),black,white).convert('RGB')
def parity(im,p):
    if p: im=ImageEnhance.Brightness(im).enhance(.88)
    return im.convert('RGBA')
def save(name,im,p): parity(im,p).save(OUT/f'{name}{p}.png')

for p in (0,1):
    ground=tint(board('daikara/rock-ground0'),(51,33,27),(185,116,75))
    ash=native('grass_burnt1.png').resize((128,128),Image.Resampling.BICUBIC)
    ground=Image.blend(ground,tint(ash,(47,29,24),(152,97,66)),.22)
    save('floor',ground,p)

    # Generated native-alpha branch silhouette, complete at the 48px review
    # size; keep the gameplay-neutral warm ground behind it.
    with Image.open(MASTERS/'burnt-tree-v1.png') as master:
        tree=master.convert('RGBA').resize((122,122),Image.Resampling.LANCZOS)
    treebase=ground.convert('RGBA')
    treebase.alpha_composite(tree,(3,3))
    save('tree',treebase,p)

    with Image.open(MASTERS/'molten-pool-v1.png') as master:
        lava=master.convert('RGB').resize((128,128),Image.Resampling.LANCZOS)
    # The raised cooled-rock lip is an overlay only where molten cells meet
    # walkable burnt ground; joined sides expose no rim.
    rim_rock=tint(board('daikara/rock-ground0'),(17,15,15),(74,64,59))
    for neighbors in range(16):
        pool=lava.copy()
        shore=Image.new('L',(128,128),0)
        rd=ImageDraw.Draw(shore)
        # N/E/S/W bits: edge only where the neighbouring cell is not lava.
        if not neighbors&1: rd.rectangle((0,0,127,15),fill=255)
        if not neighbors&2: rd.rectangle((112,0,127,127),fill=255)
        if not neighbors&4: rd.rectangle((0,112,127,127),fill=255)
        if not neighbors&8: rd.rectangle((0,0,15,127),fill=255)
        pool=Image.composite(rim_rock,pool,shore)
        d=ImageDraw.Draw(pool)
        if not neighbors&1:
            d.line((0,4,127,4),fill=(111,91,71),width=2)
            d.line((0,15,127,15),fill=(25,18,17),width=3)
        if not neighbors&2:
            d.line((124,0,124,127),fill=(98,78,63),width=2)
            d.line((112,0,112,127),fill=(25,18,17),width=3)
        if not neighbors&4:
            d.line((0,123,127,123),fill=(82,66,57),width=2)
            d.line((0,112,127,112),fill=(25,18,17),width=3)
        if not neighbors&8:
            d.line((4,0,4,127),fill=(112,91,70),width=2)
            d.line((15,0,15,127),fill=(25,18,17),width=3)
        save(f'lava-{neighbors}-',pool,p)

    # Exit glyphs are extracted from the established board symbol; the
    # backing is newly scorched floor. Down rotates the directional glyph.
    source=board('exit0')
    glyph=Image.new('L',(128,128))
    glyph.putdata([255 if r>164 and g>150 and b>95 and r>g else 0
                   for r,g,b in source.get_flattened_data()])
    glyph=glyph.filter(ImageFilter.GaussianBlur(.4))
    for kind in ('up','down','world'):
        base=ground.copy()
        mark=Image.new('RGB',(128,128),(237,204,144))
        current=glyph.rotate(180) if kind=='down' else glyph
        base.paste(mark,(0,0),current)
        if kind=='world':
            d=ImageDraw.Draw(base)
            d.ellipse((37,37,91,91),outline=(232,192,126),width=2)
        save('exit-'+kind,base,p)

sources=sorted(MASTERS.glob('*.png'))
report={'imagegen_calls':2,'source_sha256':{str(s.relative_to(ROOT)):hashlib.sha256(s.read_bytes()).hexdigest() for s in sources},
 'runtime_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(OUT.glob('*.png'))}}
(Path(__file__).parent/'export-manifest.json').write_text(json.dumps(report,indent=2)+'\n')
