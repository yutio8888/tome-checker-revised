#!/usr/bin/env python3
"""Batch 4 board terrain, derived deterministically from pinned existing art.

No ImageGen. Sources are the reviewed forest/Daikara/Kor'Pul/underwater/F1
tree board masters plus native ToME sprites that the covered grids already
draw (troll stew, picnic umbrella and basket). Every runtime file is written
by this script; the manifest pins source and output hashes.
"""
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageOps, ImageStat
import hashlib, json
import numpy as np

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
NATIVE=ROOT.parents[1]/'modules/tome/data/gfx/shockbolt/terrain'
FOREST=ROOT/'art/terrain-forest-v1/masters-derived'
GFX=ROOT/'data/gfx/refined'
S=128
PARITY=.86
SOURCES=[]

def src(path):
    SOURCES.append(path);return path
def rgb(path): return Image.open(src(path)).convert('RGB')
def rgba(path): return Image.open(src(path)).convert('RGBA')
def tint(im,black,white,mid=None,midpoint=127):
    g=ImageOps.grayscale(im)
    if mid is None: return ImageOps.colorize(g,black,white).convert('RGB')
    return ImageOps.colorize(g,black,white,mid=mid,midpoint=midpoint).convert('RGB')
def tint_alpha(im,black,white):
    out=tint(im.convert('RGB'),black,white).convert('RGBA');out.putalpha(im.getchannel('A'));return out
def parity(im,p):
    im=im.convert('RGB')
    return ImageEnhance.Brightness(im).enhance(PARITY) if p else im

FILES={}
def save(folder,name,im):
    out=GFX/folder/name;out.parent.mkdir(parents=True,exist_ok=True)
    im.convert('RGB').save(out,optimize=True)
    FILES[f'{folder}/{name}']=hashlib.sha256(out.read_bytes()).hexdigest()

def sprite(name,box,bottom=4):
    """Native cutout scaled into box, bottom-centred, alpha preserved."""
    im=rgba(NATIVE/name);im=im.crop(im.getchannel('A').getbbox())
    scale=min(box[0]/im.width,box[1]/im.height)
    im=im.resize((round(im.width*scale),round(im.height*scale)),Image.Resampling.LANCZOS)
    return im,((S-im.width)//2,S-im.height-bottom)

def contact_shadow(base,box,alpha):
    sh=Image.new('RGBA',(S,S));ImageDraw.Draw(sh).ellipse(box,fill=(6,14,4,alpha))
    base.alpha_composite(sh.filter(ImageFilter.GaussianBlur(5)))

# ---------------------------------------------------------------- caldera --
grass=rgb(FOREST/'floor-grass.png')
jungle=rgb(NATIVE/'jungle/jungle_grass_floor_01.png').resize((S,S),Image.Resampling.BICUBIC)
floor=Image.blend(tint(grass,(34,68,22),(150,206,84)),tint(jungle,(34,68,22),(150,206,84)),.35)

deep=rgb(FOREST/'floor-deep.png')
banks=[rgba(FOREST/f'bank-deep-{d}.png') for d in 'NESW']
def poison(mask):
    # Murky green pool like the native poisoned water. Rework 2026-09-29: the
    # first version kept the fine ripple noise of the deep-water master, which
    # read as a busy brown carpet under the caldera's warm light. The surface
    # is now a heavily blurred, low-contrast copy of that master: a few broad
    # pale-scum blotches on dark green water, so parity stays visible and the
    # pool reads as one calm liquid body. A dark mud lip only where the water
    # meets a non-water cell. No symbols: colour and liquid texture only.
    # Wrapped (seamless) Gaussian blur in floating point, then normalised: an
    # 8-bit blur of this strength would posterise when stretched.
    # Broad blotches (sigma 9) carry the surface; a quarter-weight sigma 3
    # layer keeps a faint ripple so it still reads as liquid, not felt.
    src=np.asarray(ImageOps.grayscale(deep),dtype=np.float64)
    def blur(sigma):
        r=int(3*sigma);k=np.exp(-.5*(np.arange(-r,r+1)/sigma)**2);k/=k.sum();g=src
        for axis in (0,1): g=sum(w*np.roll(g,i-r,axis=axis) for i,w in enumerate(k))
        return (g-np.percentile(g,1))/(np.percentile(g,99)-np.percentile(g,1))
    g=.75*blur(9.)+.25*blur(3.)
    g=Image.fromarray(np.clip(127.5+(g-.5)*255*.5,0,255).round().astype(np.uint8),'L')
    im=ImageOps.colorize(g,(14,30,14),(118,168,72),mid=(40,72,34),midpoint=128).convert('RGBA')
    boxes=[(0,0,S,10),(S-10,0,S,S),(0,S-10,S,S),(0,0,10,S)]
    for bit,(bank,box) in enumerate(zip(banks,boxes)):
        if not mask&(1<<bit):
            lip=tint_alpha(bank,(30,44,16),(92,124,46)).resize((box[2]-box[0],box[3]-box[1]),Image.Resampling.LANCZOS)
            im.alpha_composite(lip,(box[0],box[1]))
    return im

daikara=rgba(ROOT/'art/terrain-daikara-v1/masters/mountain-wall-solid-v3.png')
body=daikara.crop(daikara.getchannel('A').getbbox());bw,bh=body.size
face=ImageOps.fit(body.crop((int(bw*.18),int(bh*.56),int(bw*.82),int(bh*.9))),(S,40),method=Image.Resampling.LANCZOS)
def rock_wall(mask):
    # One calm rock mass filling the blocking cell: a high-passed crop of the
    # reviewed Daikara rock (no per-cell light gradient). Edge shading and a
    # dark cliff face appear only toward non-wall neighbours; interior masks
    # carry no stacked faces.
    cw,ch=int(bw*.46),int(bh*.30)
    sx=int(bw*.14)+(mask*53)%int(bw*.3);sy=int(bh*.06)+(mask*29)%int(bh*.1)
    g=ImageOps.grayscale(body.crop((sx,sy,sx+cw,sy+ch)).convert('RGB')).resize((S,S),Image.Resampling.LANCZOS)
    hp=ImageChops.subtract(g,g.filter(ImageFilter.GaussianBlur(14)),1,128).filter(ImageFilter.GaussianBlur(.6))
    tile=ImageOps.colorize(ImageEnhance.Contrast(hp).enhance(1.6),(14,13,13),(112,104,96),mid=(54,50,47)).convert('RGB')
    if not mask&1:
        tile.paste(Image.blend(tile.crop((0,0,S,5)),Image.new('RGB',(S,5),(128,120,110)),.45),(0,0))
    if not mask&8:
        tile.paste(ImageEnhance.Brightness(tile.crop((0,0,8,S))).enhance(.74),(0,0))
    if not mask&2:
        tile.paste(ImageEnhance.Brightness(tile.crop((S-8,0,S,S))).enhance(.70),(S-8,0))
    if not mask&4:
        tile.paste(tint(face.convert('RGB'),(10,9,9),(70,64,60)),(0,88))
        tile.paste(Image.blend(tile.crop((0,85,S,88)),Image.new('RGB',(S,3),(12,10,10)),.6),(0,85))
    return tile

# Blocking jungle trees. Rework 2026-09-29: the first version (three small
# native 64px canopies, darkened) read as a dark square with a faint shrub.
# Each tree is now one reviewed high-resolution board tree master filling the
# cell (canopy edge to edge, trunk and roots on the ground), recoloured to a
# lusher jungle green, over deeply shaded ground so the whole cell reads as a
# blocking obstacle. 'a'/'b' are the broad hardwood (mirrored), 'c' the
# drooping willow form with its water base cut away.
F1=ROOT/'art/terrain-f1-flooded/masters'
hard_master=rgba(F1/'hardtree-v1.png')
willow_master=rgba(F1/'bog-tree-b-v1.png')
def jungle_green(im,sat,gain):
    a=im.getchannel('A');r,g,b=ImageEnhance.Color(im.convert('RGB')).enhance(sat).split()
    out=Image.merge('RGB',(r.point(lambda v:min(255,int(v*gain[0]))),g.point(lambda v:min(255,int(v*gain[1]))),
                           b.point(lambda v:min(255,int(v*gain[2]))))).convert('RGBA')
    out.putalpha(a);return out
def jungle_tree(kind):
    base=ImageEnhance.Brightness(floor).enhance(.42).convert('RGBA')
    sh=Image.new('RGBA',(S,S));ImageDraw.Draw(sh).ellipse((0,40,128,132),fill=(4,10,2,200))
    base.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8)))
    src=willow_master.crop((0,0,willow_master.width,int(willow_master.height*.84))) if kind=='c' else hard_master
    src=src.crop(src.getchannel('A').point(lambda v:255 if v>60 else 0).getbbox())
    if kind=='b': src=ImageOps.mirror(src)
    w=136 if kind=='c' else 138
    h=round(src.height*w/src.width)
    sat,gain=((1.1,(.62,.78,.5)) if kind=='c' else (1.25,(.95,1.12,.78)))
    base.alpha_composite(jungle_green(src.resize((w,h),Image.Resampling.LANCZOS),sat,gain),((S-w)//2,S-h+2))
    return base

board_exit=Image.open(src(GFX/'exit0.png')).convert('RGB')
glyph=Image.new('L',(S,S))
glyph.putdata([255 if r>164 and g>150 and b>95 and r>g else 0 for r,g,b in board_exit.get_flattened_data()])
glyph=glyph.filter(ImageFilter.GaussianBlur(.4))
def exit_tile(kind):
    base=floor.copy()
    base.paste(Image.new('RGB',(S,S),(237,214,150)),(0,0),glyph.rotate(180) if kind=='down' else glyph)
    if kind=='world': ImageDraw.Draw(base).ellipse((37,37,91,91),outline=(236,206,140),width=2)
    return base

for p in (0,1):
    save('caldera',f'floor{p}.png',parity(floor,p))
    for key in 'abc': save('caldera',f'tree-{key}{p}.png',parity(jungle_tree(key),p))
    for kind in ('up','down','world'): save('caldera',f'exit-{kind}{p}.png',parity(exit_tile(kind),p))
    for mask in range(16):
        save('caldera',f'poison-{mask}-{p}.png',parity(poison(mask),p))
        save('caldera',f'wall-{mask}-{p}.png',parity(rock_wall(mask),p))

# ------------------------------------------------------------ South Beach --
# Rework 2026-09-29. The shared dune sand read as harsh orange stripes next to
# the calm grass: the beach gets its own copy with less saturation and
# contrast (same mean light, same parity step). Blocking TREE# cells showed
# the forest suite's small tree icon floating on open grass; the beach trees
# now zoom the same reviewed oak/pine/willow tiles so the tree fills the cell
# and shade the ground outside the tree (mask = difference from the grass
# tile the icon was composited on), so every tree cell reads as an obstacle.
sand_src=rgb(GFX/'sand/floor0.png')
beach_sand=ImageEnhance.Contrast(ImageEnhance.Color(sand_src).enhance(.82)).enhance(.74)
beach_grass=rgb(GFX/'grass0.png')
def beach_tree(kind):
    t=rgb(GFX/f'tree-{kind}0.png')
    m=ImageChops.difference(t,beach_grass).convert('L').point(lambda v:255 if v>16 else 0)
    m=m.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.MinFilter(5))
    x0,y0,x1,y1=m.getbbox()
    side=min(S,max(x1-x0,y1-y0)+4);cx=(x0+x1)//2
    left=max(0,min(S-side,cx-side//2));top=max(0,min(S-side,y1+3-side))
    box=(left,top,left+side,top+side)
    tree=t.crop(box).resize((S,S),Image.Resampling.LANCZOS)
    mask=m.crop(box).resize((S,S),Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(2.5))
    return Image.composite(tree,ImageEnhance.Brightness(tree).enhance(.56),mask)
for p in (0,1):
    save('beach',f'sand{p}.png',parity(beach_sand,p))
    for kind in ('oak','pine','willow'): save('beach',f'tree-{kind}{p}.png',parity(beach_tree(kind),p))

# ---------------------------------------------------- beach and meadow props --
def prop_on(folder,base_name,sprite_name,box,shadow,name):
    for p in (0,1):
        base=Image.open(src(GFX/folder/f'{base_name}{p}.png')).convert('RGBA')
        contact_shadow(base,shadow,110)
        im,pos=sprite(sprite_name,box)
        # The floor already carries its suite parity; darken the prop too so
        # the whole cell keeps the >=10% board parity step.
        if p: im=Image.merge('RGBA',(*ImageEnhance.Brightness(im.convert('RGB')).enhance(PARITY).split(),im.getchannel('A')))
        base.alpha_composite(im,pos)
        save(name[0],f'{name[1]}{p}.png',base)
# Blocking parasol: large, fills the cell like other board blockers.
prop_on('beach','sand','picnic_umbrella.png',(118,118),(18,96,110,124),('beach','umbrella'))
# Passable basket: small and low, reads as an item on open sand, never a wall.
prop_on('beach','sand','picnic_basket.png',(52,40),(38,98,90,120),('beach','basket'))
# Blocking stew pot on its tripod over embers.
for p in (0,1):
    base=Image.open(src(GFX/f'grass{p}.png')).convert('RGBA')
    contact_shadow(base,(16,92,112,124),130)
    im,pos=sprite('troll_stew.png',(118,118))
    if p: im=Image.merge('RGBA',(*ImageEnhance.Brightness(im.convert('RGB')).enhance(PARITY).split(),im.getchannel('A')))
    base.alpha_composite(im,pos)
    save('keepsake',f'stew{p}.png',base)

# -------------------------------------------------- Murgol underwater exit --
uw=Image.open(src(ROOT/'art/terrain-underwater-v1/masters/underwater-floor-v1.png')).convert('RGB').resize((S,S),Image.Resampling.LANCZOS)
stair=rgba(GFX/'korpul/stairs-world.png').resize((S,S),Image.Resampling.LANCZOS)
mark=ImageOps.colorize(ImageOps.grayscale(stair),(14,48,62),(155,204,198)).convert('RGBA')
mark.putalpha(stair.getchannel('A'))
world=uw.convert('RGBA');world.alpha_composite(mark)
for p in (0,1):
    # Same parity factor as the reviewed underwater suite.
    save('underwater',f'stairs-world{p}.png',ImageEnhance.Brightness(world.convert('RGB')).enhance(.82) if p else world)

# ------------------------------------------------- Conclave Vault walls --
# The reviewed Kor'Pul brick walls are brighter than its floors. The vault
# keeps the same brick masks, recoloured to a cool, darker grey so walls read
# as solid mass against the pale lab floor; the board parity step is reapplied
# from the parity-0 source.
CONCLAVE=[]
for mask in range(16):
    # Frozen pre-2026-10-01 Kor'Pul brick (the live brick got a cool hue finish).
    brick=rgb(ROOT/'art/terrain-contrast-v1/frozen-inputs/korpul'/f'wall-{mask}-0.png')
    r,g,b=brick.split()
    cool=Image.merge('RGB',(r.point(lambda v:int(v*.52)),g.point(lambda v:int(v*.55)),b.point(lambda v:int(v*.62))))
    for p in (0,1):
        save('conclave',f'wall-{mask}-{p}.png',parity(cool,p));CONCLAVE.append(f'conclave/wall-{mask}-{p}.png')
(ROOT/'data/terrain-conclave-manifest.lua').write_text(
    '-- Generated by art/terrain-batch4-v1/export.py.\n'
    '-- Conclave Vault wall recolour of the reviewed Kor\'Pul brick masks.\n'
    'return {\n ready=true,\n revision=\'conclave-v1-'+hashlib.sha256(''.join(FILES[k] for k in CONCLAVE).encode()).hexdigest()[:12]+'\',\n files={\n'
    +''.join(f"  ['checker-revised+refined/{k}']=true,\n" for k in CONCLAVE)+' },\n}\n')

def lum(rel): return ImageStat.Stat(Image.open(GFX/rel).convert('L')).mean[0]
parities={k[:-5]:(lum(k)-lum(k[:-5]+'1.png'))/lum(k) for k in FILES if k.endswith('0.png')}
manifest={'generator':'art/terrain-batch4-v1/export.py','imagegen_calls':0,
 'sources':{str(Path(s).resolve().relative_to(ROOT.parents[2])):hashlib.sha256(Path(s).read_bytes()).hexdigest()
            for s in sorted(set(map(str,SOURCES)))},
 'files':FILES,'parity_min':round(min(parities.values()),4),
 'floor_wall_gap':round((lum('caldera/floor0.png')-lum('caldera/wall-15-0.png'))/lum('caldera/floor0.png'),4),
 'conclave_floor_wall_gap':round((lum('korpul/floor-a-0-0.png')-lum('conclave/wall-15-0.png'))/lum('korpul/floor-a-0-0.png'),4)}
(HERE/'export-manifest.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
print(len(FILES),'files; parity min',manifest['parity_min'],'floor/wall gap',manifest['floor_wall_gap'])
