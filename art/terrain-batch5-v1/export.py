#!/usr/bin/env python3
"""Batch 5 board terrain, derived deterministically from pinned existing art.

No ImageGen. Two new families:
- scorch: LAVA_WALL of the Charred Scar and the Fearscape (demon plane),
  the reviewed Daikara rock master re-rendered as calm ash basalt with the
  same cell-filling construction as the batch 4 caldera walls;
- shertul: Sher'Tul Fortress SOLID_FLOOR and SOLID_WALL, the reviewed
  Kor'Pul stone grain recoloured to the fortress's ivory/graphite palette,
  with the native fortress panel seams and banded wall face.
Every runtime file is written here; the manifest pins source/output hashes.
"""
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageOps, ImageStat
import hashlib, json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
NATIVE=ROOT.parents[1]/'modules/tome/data/gfx/shockbolt/terrain'
GFX=ROOT/'data/gfx/refined'
S=128
PARITY=.86
SOURCES=[]
FILES={}

def src(path):
    SOURCES.append(path);return path
def rgb(path): return Image.open(src(path)).convert('RGB')
def rgba(path): return Image.open(src(path)).convert('RGBA')
def parity(im,p):
    im=im.convert('RGB')
    return ImageEnhance.Brightness(im).enhance(PARITY) if p else im
def save(folder,name,im):
    out=GFX/folder/name;out.parent.mkdir(parents=True,exist_ok=True)
    im.convert('RGB').save(out,optimize=True)
    FILES[f'{folder}/{name}']=hashlib.sha256(out.read_bytes()).hexdigest()
def shade(tile,box,factor):
    tile.paste(ImageEnhance.Brightness(tile.crop(box)).enhance(factor),box[:2])

# ------------------------------------------------------------- scorch walls --
# Same calm construction as the caldera rock wall: one high-passed crop of the
# reviewed Daikara rock filling the whole blocking cell, edge light/shade and a
# dark cliff face only toward non-wall neighbours. The palette is a warm ash
# grey, clearly lighter than the dark cracked lava floor of these zones (the
# Daikara mountain/lava-floor relation), with no glow, ember or hazard mark:
# LAVA_WALL is inert rock that blocks movement and sight.
daikara=rgba(ROOT/'art/terrain-daikara-v1/masters/mountain-wall-solid-v3.png')
body=daikara.crop(daikara.getchannel('A').getbbox());bw,bh=body.size
face=ImageOps.fit(body.crop((int(bw*.18),int(bh*.56),int(bw*.82),int(bh*.9))),(S,40),method=Image.Resampling.LANCZOS)
def scorch_wall(mask):
    cw,ch=int(bw*.46),int(bh*.30)
    sx=int(bw*.14)+(mask*53)%int(bw*.3);sy=int(bh*.06)+(mask*29)%int(bh*.1)
    g=ImageOps.grayscale(body.crop((sx,sy,sx+cw,sy+ch)).convert('RGB')).resize((S,S),Image.Resampling.LANCZOS)
    hp=ImageChops.subtract(g,g.filter(ImageFilter.GaussianBlur(14)),1,128).filter(ImageFilter.GaussianBlur(.8))
    tile=ImageOps.colorize(ImageEnhance.Contrast(hp).enhance(1.35),(40,37,35),(170,160,150),mid=(104,97,91)).convert('RGB')
    if not mask&1:
        tile.paste(Image.blend(tile.crop((0,0,S,5)),Image.new('RGB',(S,5),(190,180,168)),.45),(0,0))
    if not mask&8: shade(tile,(0,0,8,S),.78)
    if not mask&2: shade(tile,(S-8,0,S,S),.72)
    if not mask&4:
        tile.paste(ImageOps.colorize(ImageOps.grayscale(face.convert('RGB')),(16,14,13),(84,76,70)).convert('RGB'),(0,88))
        tile.paste(Image.blend(tile.crop((0,85,S,88)),Image.new('RGB',(S,3),(20,16,15)),.6),(0,85))
    return tile

# ----------------------------------------------------------- Sher'Tul fortress --
# Board language keeps walkable floors light and blocking walls dark. The
# fortress floor is a smooth ivory-grey panel floor (the native wall-cap
# ivory) with the native floor's large-panel seam layout; the walls are one
# calm graphite block per cell (the native floor graphite) with a thin ivory
# cap toward open north sides and the native banded face on open south sides.
# Frozen pre-2026-10-01 Kor'Pul floors (the live floor got a warm hue finish).
grain_a=ImageOps.grayscale(rgb(ROOT/'art/terrain-contrast-v1/frozen-inputs/korpul/floor-a-0-0.png'))
grain_b=ImageOps.grayscale(rgb(ROOT/'art/terrain-contrast-v1/frozen-inputs/korpul/floor-b-0-0.png'))
def calm(g,amount):
    # Keep only a soft stone grain: blur the reviewed texture, then pull its
    # contrast toward the mean so the panel reads smooth and machined.
    g=g.filter(ImageFilter.GaussianBlur(1.2))
    mean=ImageStat.Stat(g).mean[0]
    return g.point(lambda v:int(round(mean+(v-mean)*amount)))
def seams(name,dark):
    # Native seam lines: the native floor is a flat graphite (57) whose panel
    # grooves are the few darker pixels (<=54). Those groove pixels, scaled to
    # the board cell, become a soft multiply layer.
    n=ImageOps.grayscale(rgb(NATIVE/'solidwall'/name))
    m=n.point(lambda v:255 if v<=54 else 0).resize((S,S),Image.Resampling.NEAREST).filter(ImageFilter.GaussianBlur(.8))
    return m.point(lambda v:int(255-v*(1-dark)))
floor_seam=seams('solid_floor1.png',.84)
def shertul_floor():
    g=calm(grain_a,.45)
    base=ImageOps.colorize(g,(112,112,110),(214,210,198),mid=(166,164,156)).convert('RGB')
    return ImageChops.multiply(base,Image.merge('RGB',[floor_seam]*3))
band=ImageOps.grayscale(rgb(NATIVE/'solidwall/solid_wall1.png')).resize((S,S),Image.Resampling.BICUBIC).crop((0,72,S,S))
band=band.resize((S,40),Image.Resampling.BICUBIC)
def shertul_wall(mask):
    g=calm(grain_b.rotate(90*(mask%4)),.55)
    tile=ImageOps.colorize(g,(30,33,38),(96,100,108),mid=(58,62,70)).convert('RGB')
    if not mask&1:
        tile.paste(Image.new('RGB',(S,4),(188,184,172)),(0,0))
        tile.paste(Image.new('RGB',(S,2),(24,26,30)),(0,4))
    if not mask&8: shade(tile,(0,0,6,S),.80)
    if not mask&2: shade(tile,(S-6,0,S,S),.74)
    if not mask&4:
        tile.paste(ImageOps.colorize(band,(12,13,16),(70,72,78)).convert('RGB'),(0,88))
        tile.paste(Image.new('RGB',(S,2),(14,15,18)),(0,86))
    return tile

# ------------------------------------------------------- Orc Breeding Pit --
# The pits (L2-L3, underground.lua) reuse the Deep Bellow plain suite's
# fungal stone, but in the pits' dim light a grainy mid-dark floor next to
# textured dark walls blurred into one busy pattern. Rework (readability):
# - floor: the same plain fungal-stone floor, strongly smoothed and lifted to
#   a calm pale moss-grey, so walkable ground reads as one light field;
# - walls: one near-uniform dark peat mass per cell (a heavily blurred wash of
#   the plain fungal wall), a thin muted cap line toward open north sides,
#   soft side shade, and on open south sides a dark face band carrying the
#   only fungal detail (softened mushroom stalks from the plain wall frieze);
# - ladders: the native ladder bitmaps re-seated on the new floor exactly as
#   the gloom suite builds them.
# Deep Bellow uses the live gloom/plain suite.
# The plain floor/wall tiles read here are frozen copies of the 2026-09-28
# gloom plain tiles the accepted pit was built from; the 2026-09-30 gloom wall
# rework (crisp walls, lifted floor) replaced the live plain tiles, and the
# pit keeps its reviewed look.
pit_floor_src=ImageOps.grayscale(rgb(HERE/'frozen-inputs/gloom-plain-floor0.png'))
pit_wall_src=ImageOps.grayscale(rgb(HERE/'frozen-inputs/gloom-plain-wall-15-0.png'))
pit_frieze=ImageOps.grayscale(rgb(HERE/'frozen-inputs/gloom-plain-wall-0-0.png'))
def pit_floor():
    fine=pit_floor_src.filter(ImageFilter.GaussianBlur(1.4))
    broad=pit_floor_src.rotate(90).filter(ImageFilter.GaussianBlur(10))
    def norm(g,k):
        mean=ImageStat.Stat(g).mean[0]
        return g.point(lambda v:max(0,min(255,int(round(128+(v-mean)*k)))))
    g=ImageChops.add(norm(fine,1.3),norm(broad,2.5),1,-128)
    return ImageOps.colorize(g,(70,68,54),(160,154,128),mid=(116,112,92)).convert('RGB')
def pit_wall(mask):
    g=pit_wall_src.rotate(90*(mask%4)).filter(ImageFilter.GaussianBlur(9))
    mean=ImageStat.Stat(g).mean[0]
    g=g.point(lambda v:max(0,min(255,int(round(128+(v-mean)*1.2)))))
    tile=ImageOps.colorize(g,(20,19,15),(50,46,36),mid=(33,31,25)).convert('RGB')
    if not mask&1:
        tile.paste(Image.new('RGB',(S,3),(104,100,76)),(0,0))
        tile.paste(Image.new('RGB',(S,2),(16,15,12)),(0,3))
    if not mask&8: shade(tile,(0,0,6,S),.78)
    if not mask&2: shade(tile,(S-6,0,S,S),.72)
    if not mask&4:
        # Face toward the floor: a soft lit-to-shadow gradient with faint
        # vertical fungal-stalk striation (low-contrast, blurred frieze).
        grad=Image.linear_gradient('L').resize((S,34)).point(lambda v:255-v)
        stalks=ImageOps.autocontrast(pit_frieze.crop((0,40,S,S)).resize((S,34),Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(2.2)),cutoff=2)
        band=Image.blend(grad,stalks,.28)
        tile.paste(ImageOps.colorize(band,(12,11,9),(78,74,56)).convert('RGB'),(0,94))
        tile.paste(Image.blend(tile.crop((0,92,S,94)),Image.new('RGB',(S,2),(10,9,7)),.7),(0,92))
    return tile
LADDERS=[('ladder-up','ladder_up.png'),('ladder-down','ladder_down.png'),('ladder-world','ladder_up_wild.png')]
def pit_ladder(kind,native):
    ladder=rgba(NATIVE/native);alpha=ladder.getchannel('A')
    ladder=Image.blend(ladder,Image.new('RGBA',ladder.size,(173,160,131,255)),.22);ladder.putalpha(alpha)
    ladder.thumbnail((108,108),Image.Resampling.LANCZOS)
    tile=pit_floor().convert('RGBA')
    if kind=='ladder-world':
        halo=Image.new('L',(S,S));ImageDraw.Draw(halo).ellipse((13,12,115,116),fill=190)
        tile=Image.composite(Image.new('RGBA',(S,S),(211,194,151,255)),tile,halo.filter(ImageFilter.GaussianBlur(8)))
    tile.alpha_composite(ladder,((S-ladder.width)//2,(S-ladder.height)//2))
    return tile

for p in (0,1):
    for mask in range(16): save('gloom/pit',f'wall-{mask}-{p}.png',parity(pit_wall(mask),p))
    save('gloom/pit',f'floor{p}.png',parity(pit_floor(),p))
    for kind,native in LADDERS: save('gloom/pit',f'{kind}{p}.png',parity(pit_ladder(kind,native),p))
    save('shertul',f'floor{p}.png',parity(shertul_floor(),p))
    for mask in range(16):
        save('scorch',f'wall-{mask}-{p}.png',parity(scorch_wall(mask),p))
        save('shertul',f'wall-{mask}-{p}.png',parity(shertul_wall(mask),p))

def lum(rel): return ImageStat.Stat(Image.open(GFX/rel).convert('L')).mean[0]
parities={k[:-5]:(lum(k)-lum(k[:-5]+'1.png'))/lum(k) for k in FILES if k.endswith('0.png')}
manifest={'generator':'art/terrain-batch5-v1/export.py','imagegen_calls':0,
 'sources':{str(Path(s).resolve().relative_to(ROOT.parents[2])):hashlib.sha256(Path(s).read_bytes()).hexdigest()
            for s in sorted(set(map(str,SOURCES)))},
 'files':FILES,'parity_min':round(min(parities.values()),4),
 'scorch_wall_floor_gap':round((lum('scorch/wall-15-0.png')-lum('daikara/lava-floor0.png'))/lum('daikara/lava-floor0.png'),4),
 'pit_floor_wall_gap':round((lum('gloom/pit/floor0.png')-lum('gloom/pit/wall-15-0.png'))/lum('gloom/pit/floor0.png'),4),
 'shertul_floor_wall_gap':round((lum('shertul/floor0.png')-lum('shertul/wall-15-0.png'))/lum('shertul/floor0.png'),4)}
(HERE/'export-manifest.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
print(len(FILES),'files; parity min',manifest['parity_min'],'scorch',manifest['scorch_wall_floor_gap'],'shertul',manifest['shertul_floor_wall_gap'])
