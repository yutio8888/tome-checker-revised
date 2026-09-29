#!/usr/bin/env python3
"""Rak'Shor Pride board terrain (bone.lua), derived deterministically.

No ImageGen. One new family, `rakshor`:
- floor: the reviewed Sandworm Lair sand master, smoothed and re-toned to a
  calm pale desert sand (BONEFLOOR is native "sand" on sandfloor.png);
- walls (BONEWALL*, HARDBONEWALL*): one calm dark bone-and-earth mass per
  cell. The interior carries only a faint, blurred bone grain from the native
  bone wall bitmaps; open north sides get a thin ivory cap, open east/west
  sides a soft shade, and open south sides a dark face band that carries the
  zone's identity (the native bone wall face, softened and re-toned);
- doors: the native bone gate/arch bitmaps, calmed and re-toned onto the new
  floor (one cell-filling tile per state, like the underwater doors);
- stairs/exits: the native bone stair frames and world-map disc seated on the
  new floor.
Levers, lever doors and sealed vault doors are not exported: they stay native.
Every runtime file is written here; the manifest pins source/output hashes.
"""
from pathlib import Path
from PIL import Image, ImageChops, ImageEnhance, ImageFilter, ImageOps, ImageStat
import hashlib, json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
NATIVE=ROOT.parents[1]/'modules/tome/data/gfx/shockbolt/terrain'
GFX=ROOT/'data/gfx/refined'
S=128
PARITY=.86
SOURCES=[];FILES={}

def src(path): SOURCES.append(path);return path
def rgb(path): return Image.open(src(path)).convert('RGB')
def rgba(path): return Image.open(src(path)).convert('RGBA')
def parity(im,p):
    im=im.convert('RGB')
    return ImageEnhance.Brightness(im).enhance(PARITY) if p else im
def save(name,im):
    out=GFX/'rakshor'/name;out.parent.mkdir(parents=True,exist_ok=True)
    im.convert('RGB').save(out,optimize=True)
    FILES[f'rakshor/{name}']=hashlib.sha256(out.read_bytes()).hexdigest()
def shade(tile,box,factor):
    tile.paste(ImageEnhance.Brightness(tile.crop(box)).enhance(factor),box[:2])
def norm(g,k,centre=128):
    mean=ImageStat.Stat(g).mean[0]
    return g.point(lambda v:max(0,min(255,int(round(centre+(v-mean)*k)))))

# ------------------------------------------------------------------ floor --
sand=ImageOps.fit(rgb(ROOT/'art/terrain-sandworm-v1/masters/sand-floor-v1.png'),(S,S),method=Image.Resampling.LANCZOS)
def floor():
    g=norm(ImageOps.grayscale(sand).filter(ImageFilter.GaussianBlur(1.6)),.8)
    return ImageOps.colorize(g,(142,122,88),(214,196,154),mid=(182,162,122)).convert('RGB')
FLOOR=floor()

# ------------------------------------------------------------------ walls --
grain=[ImageOps.grayscale(rgb(NATIVE/f'bone/bonewall_5_{k}.png')).resize((S,S),Image.Resampling.LANCZOS) for k in (1,3,5)]
face_src=ImageOps.grayscale(rgb(NATIVE/'bone/bone_V3_8_01.png')).resize((S,S),Image.Resampling.LANCZOS).crop((0,52,S,S))
def wall(mask):
    g=grain[mask%3].rotate(90*(mask//4%4))
    hp=ImageChops.subtract(g,g.filter(ImageFilter.GaussianBlur(10)),1,128).filter(ImageFilter.GaussianBlur(1.6))
    hp=norm(hp,.55)
    tile=ImageOps.colorize(hp,(20,16,12),(96,84,64),mid=(46,39,30)).convert('RGB')
    if not mask&1:
        tile.paste(Image.new('RGB',(S,3),(170,156,122)),(0,0))
        tile.paste(Image.new('RGB',(S,2),(18,14,10)),(0,3))
    if not mask&8: shade(tile,(0,0,6,S),.76)
    if not mask&2: shade(tile,(S-6,0,S,S),.70)
    if not mask&4:
        band=norm(face_src.resize((S,34),Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(1.4)),1.1)
        tile.paste(ImageOps.colorize(band,(10,8,6),(150,134,100),mid=(46,38,28)).convert('RGB'),(0,94))
        tile.paste(Image.blend(tile.crop((0,92,S,94)),Image.new('RGB',(S,2),(8,6,4)),.7),(0,92))
    return tile

# ------------------------------------------------------ doors and exits --
def calm_sprite(path,size,contrast=.8,sat=.75,bright=1.0):
    im=rgba(path);a=im.getchannel('A')
    im=im.resize((size,size),Image.Resampling.LANCZOS);a=a.resize((size,size),Image.Resampling.LANCZOS)
    c=im.convert('RGB').filter(ImageFilter.GaussianBlur(.6))
    c=ImageEnhance.Brightness(ImageEnhance.Color(ImageEnhance.Contrast(c).enhance(contrast)).enhance(sat)).enhance(bright)
    c=c.convert('RGBA');c.putalpha(a);return c
def seat(sprite,size):
    tile=FLOOR.convert('RGBA');tile.alpha_composite(sprite,((S-size)//2,(S-size)//2));return tile
def door(path):
    # Full-cell gate: the native bitmap is a gate set in a bone wall section.
    return seat(calm_sprite(NATIVE/path,S,contrast=.75,sat=.7),S)
KINDS={
 'door-closed':lambda:door('bone/bone_door1.png'),
 'door-open':lambda:door('bone/bone_door1_open.png'),
 'stairs-up':lambda:seat(calm_sprite(NATIVE/'bone/bone_stairs_up_1_01.png',116),116),
 'stairs-down':lambda:seat(calm_sprite(NATIVE/'bone/bone_stairs_down_1_01.png',116),116),
 'stairs-exit':lambda:seat(calm_sprite(NATIVE/'bone/bone_stairs_exit_1_01.png',116),116),
 'exit-world':lambda:seat(calm_sprite(NATIVE/'worldmap.png',104,contrast=.9,sat=.85),104),
}

for p in (0,1):
    save(f'floor{p}.png',parity(FLOOR,p))
    for mask in range(16): save(f'wall-{mask}-{p}.png',parity(wall(mask),p))
    for k,fn in KINDS.items(): save(f'{k}{p}.png',parity(fn(),p))

def lum(rel): return ImageStat.Stat(Image.open(GFX/rel).convert('L')).mean[0]
parities={k[:-5]:(lum(k)-lum(k[:-5]+'1.png'))/lum(k) for k in FILES if k.endswith('0.png')}
manifest={'generator':'art/terrain-rakshor-v1/export.py','imagegen_calls':0,
 'sources':{str(Path(s).resolve().relative_to(ROOT.parents[2])):hashlib.sha256(Path(s).read_bytes()).hexdigest()
            for s in sorted(set(map(str,SOURCES)))},
 'files':FILES,'parity_min':round(min(parities.values()),4),
 'floor_wall_gap':round((lum('rakshor/floor0.png')-lum('rakshor/wall-15-0.png'))/lum('rakshor/floor0.png'),4)}
(HERE/'export-manifest.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
print(len(FILES),'files; parity min',manifest['parity_min'],'floor/wall',manifest['floor_wall_gap'])
