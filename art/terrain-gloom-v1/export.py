#!/usr/bin/env python3
"""Deterministic 128px board exports from ImageGen masters and native ladder shapes."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageEnhance,ImageFilter,ImageOps,ImageStat
import hashlib,json,shutil,math
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
NATIVE=ROOT.parents[1]/'modules/tome/data/gfx/shockbolt/terrain'
SIZE=128

def load(name):
    path=HERE/'masters'/f'{name}-v1.png'
    im=Image.open(path).convert('RGBA')
    return ImageOps.fit(im,(SIZE,SIZE),method=Image.Resampling.LANCZOS,centering=(.5,.5))

def parity(im,p):
    if not p:return im
    return ImageEnhance.Brightness(im).enhance(.895)

def plain(im, dark, light, strength=.55):
    """Derive the dwarf cavern's neutral stone palette from reviewed masters."""
    grey=ImageOps.grayscale(im)
    toned=ImageOps.colorize(grey,dark,light).convert('RGBA')
    toned.putalpha(im.getchannel('A'))
    return Image.blend(im,toned,strength)

# Wall rework (2026-09-30, user report "黑暗之心的墙有点模糊"): the first
# version filled every wall cell with the whole side-view vegetation prop,
# stretched 18px edge strips toward wall neighbours and Gaussian-blurred
# 3/4-neighbour cells (78% blend for the fully enclosed mask 15, the most
# common wall cell), so the wall mass read as a soft smear.  Walls are now
# built like the accepted gothic/crystal families: a crisp overhead canopy
# (ImageGen wall-top master, heart-gloom-3) fills the cell, exposed sides get
# a shaded rim, and an exposed south side shows the stem face cut from the
# accepted side-view vegetation master.  No blur and no strip stretching.
WALL_WINDOW=400          # master px per 128px cell: 3-5 legible caps per cell
WALL_TARGET={'gloomy':40.0,'dreamy':76.0,'plain':40.0}   # mean L of the canopy
FLOOR_GAIN={'gloomy':1.42,'dreamy':1.06,'plain':1.32}    # floor+creep lift for floor/wall separation
FACE_H=34                # south stem face height (px of the 128px cell)
FACE_SRC=(.50,.76)       # trunk rows of the side-view master (bbox height fractions)
FACE_BRIGHT=.80
WALL_BASE={'plain':(34,31,26),'gloomy':(30,22,31),'dreamy':(44,42,66)}
RIM_LIGHT={'plain':(170,160,132),'gloomy':(172,150,126),'dreamy':(196,206,226)}

def canopy_tone(canopy,skin):
    im=canopy.convert('RGB')
    if skin=='plain':
        im=plain(im.convert('RGBA'),'#292824','#a89b7e',.78).convert('RGB')
    im=ImageEnhance.Brightness(im).enhance(WALL_TARGET[skin]/ImageStat.Stat(im.convert('L')).mean[0])
    return im

def stem_face(veg,skin):
    """South-facing trunk band of the side-view master, made opaque."""
    body=veg.crop(veg.getchannel('A').getbbox())
    w,h=body.size
    # Keep the trunks' aspect ratio: the band width follows its height.
    y0,y1=int(h*FACE_SRC[0]),int(h*FACE_SRC[1])
    bw=min(w,round((y1-y0)*SIZE/FACE_H));x0=(w-bw)//2
    band=body.crop((x0,y0,x0+bw,y1)).resize((SIZE,FACE_H),Image.Resampling.LANCZOS)
    face=Image.new('RGBA',band.size,WALL_BASE[skin]+(255,))
    face.alpha_composite(band)
    return ImageEnhance.Brightness(face.convert('RGB')).enhance(FACE_BRIGHT)

def edge_ramp(length,depth,strength):
    """Linear falloff band, darkest at the outer edge (no blur, no noise)."""
    ramp=Image.new('L',(length,depth))
    ramp.putdata([int(255*strength*(1-y/depth)) for y in range(depth) for x in range(length)])
    return ramp

def calm_windows(canopy,count=10,step=34):
    """Master windows with the most even broad value, calmest first.

    Enclosed cells tile in a two-parity diagonal pattern; windows without a
    single dominant cap keep that repetition from reading as stripes.
    Windows are chosen greedily so no two overlap by more than half."""
    w,h=canopy.size
    small=canopy.convert('L').resize((w//step,h//step),Image.Resampling.BOX)
    n=WALL_WINDOW//step
    scored=[]
    for y in range(0,small.height-n+1):
        for x in range(0,small.width-n+1):
            v=ImageStat.Stat(small.crop((x,y,x+n,y+n)).resize((4,4),Image.Resampling.BOX)).stddev[0]
            scored.append((round(v,4),x*step,y*step))
    scored.sort()
    picked=[]
    for v,x,y in scored:
        if all(abs(x-a)>=WALL_WINDOW//2 or abs(y-b)>=WALL_WINDOW//2 for a,b in picked):
            picked.append((x,y))
        if len(picked)==count:break
    return picked

def vegetation_wall(canopy,face,mask,skin,p,calm):
    """Crisp canopy top; rims and a stem face only on exposed sides."""
    w,h=canopy.size
    # A fixed window per mask/parity, always inside the master (no wrap
    # seam). Cells joined on three or four sides make up the wall mass and
    # use the calmest windows; exposed cells keep more varied windows.
    if mask.bit_count()>=3:
        sx,sy=calm[({15:0,7:2,11:4,13:6,14:8}[mask]+p)%len(calm)]
    else:
        sx=(mask*211+p*503)%(w-WALL_WINDOW)
        sy=(mask*137+p*311)%(h-WALL_WINDOW)
    top=canopy.crop((sx,sy,sx+WALL_WINDOW,sy+WALL_WINDOW)).resize((SIZE,SIZE),Image.Resampling.LANCZOS)
    # Level every window to the skin's wall value so parity stays a pure
    # post-composite 0.895 step whichever window a cell uses.
    top=ImageEnhance.Brightness(top).enhance(WALL_TARGET[skin]/ImageStat.Stat(top.convert('L')).mean[0])
    tile=top.filter(ImageFilter.UnsharpMask(radius=1.2,percent=60,threshold=2)).convert('RGBA')
    dark=Image.new('RGBA',(SIZE,SIZE),(8,6,10,255))
    light=Image.new('RGBA',(SIZE,SIZE),RIM_LIGHT[skin]+(255,))
    # Open north and west edges catch the upper-left light: a thin lit lip
    # over a narrow shadow, so the thicket's outline reads against the floor.
    if not mask&1:
        m=Image.new('L',(SIZE,SIZE));m.paste(edge_ramp(SIZE,4,.42),(0,0));tile=Image.composite(light,tile,m)
    if not mask&8:
        m=Image.new('L',(SIZE,SIZE));m.paste(edge_ramp(SIZE,4,.30).rotate(90,expand=True).transpose(Image.Transpose.FLIP_LEFT_RIGHT),(0,0));tile=Image.composite(light,tile,m)
    # Open east edge: shaded side.
    if not mask&2:
        m=Image.new('L',(SIZE,SIZE));m.paste(edge_ramp(SIZE,10,.62).rotate(90,expand=True),(SIZE-10,0));tile=Image.composite(dark,tile,m)
    # Open south edge: the stem face under an overhanging cap line with a
    # contact shadow; the only vertical face, as in the other board walls.
    if not mask&4:
        tile.paste(face.convert('RGBA'),(0,SIZE-FACE_H))
        m=Image.new('L',(SIZE,SIZE));m.paste(edge_ramp(SIZE,7,.70).transpose(Image.Transpose.FLIP_TOP_BOTTOM),(0,SIZE-FACE_H-7))
        tile=Image.composite(dark,tile,m)
        m=Image.new('L',(SIZE,SIZE));m.paste(edge_ramp(SIZE,8,.55).transpose(Image.Transpose.FLIP_TOP_BOTTOM),(0,SIZE-8))
        tile=Image.composite(dark,tile,m)
    return tile

def leveled_wall(canopy,face,mask,skin,p,calm):
    """Both parities of a mask share one mean before the 0.895 parity step,
    so the checker step does not depend on which canopy window a cell uses."""
    tile=vegetation_wall(canopy,face,mask,skin,p,calm)
    if not p:return tile
    ref=ImageStat.Stat(vegetation_wall(canopy,face,mask,skin,0,calm).convert('L')).mean[0]
    return ImageEnhance.Brightness(tile).enhance(ref/ImageStat.Stat(tile.convert('L')).mean[0])

def creep_mask(bits):
    vals=[]
    for y in range(SIZE):
        for x in range(SIZE):
            # A connected neighbour removes just that side's exposed fringe.
            edges=(y, SIZE-1-x, SIZE-1-y, x)
            distance=min((d for i,d in enumerate(edges) if bits&(1<<i)==0),default=SIZE)
            jitter=2.5*math.sin(x*.19+y*.07)+1.5*math.sin(y*.31-x*.13)
            val=max(0,min(255,int((distance-10+jitter)*36)))
            vals.append(val)
    mask=Image.new('L',(SIZE,SIZE));mask.putdata(vals)
    return mask.filter(ImageFilter.GaussianBlur(1.2))

def main():
    out=HERE/'exports/runtime';out.mkdir(parents=True,exist_ok=True)
    runtime=ROOT/'data/gfx/refined/gloom'
    review=HERE/'review'
    files={}
    for skin in ('gloomy','dreamy','plain'):
        source='gloomy' if skin=='plain' else skin
        floor=load(f'{source}-floor')
        creep=load(f'{source}-creep')
        if skin=='plain':
            floor=plain(floor,'#302c2a','#c8bca4',.78)
            creep=plain(creep,'#302a24','#b19e7e',.85)
        if skin=='gloomy':
            # Keep the generated cap texture; separate the passable creep
            # from near-identical brown floor at 48px with a muted plum wash.
            wash=Image.new('RGBA',(SIZE,SIZE),(119,87,124,255))
            creep=Image.blend(creep,wash,.35)
        # Floor/wall separation (2026-09-30 playtest: walkable floor and the
        # blocking thicket read too alike in gloomy and plain). Floor and creep
        # get the same gain, so their relation and the parity ratio hold.
        floor=ImageEnhance.Brightness(floor).enhance(FLOOR_GAIN[skin])
        creep=ImageEnhance.Brightness(creep).enhance(FLOOR_GAIN[skin])
        wall=Image.open(HERE/'masters'/f'{source}-vegetation-v1.png').convert('RGBA')
        if skin=='plain': wall=plain(wall,'#292824','#a89b7e',.78)
        canopy=canopy_tone(Image.open(HERE/'masters'/f'{source}-canopy-v1.png'),skin)
        face=stem_face(wall,skin)
        calm=calm_windows(canopy)
        for p in (0,1):
            ground=floor.copy()
            outputs={f'floor{p}.png':parity(ground,p)}
            for mask in range(16):
                outputs[f'wall-{mask}-{p}.png']=parity(leveled_wall(canopy,face,mask,skin,p,calm),p)
            for mask in range(16):
                tile=Image.composite(creep,ground,creep_mask(mask))
                outputs[f'creep-{mask}-{p}.png']=parity(tile,p)
            for kind,native in [('ladder-up','ladder_up.png'),('ladder-down','ladder_down.png'),('ladder-world','ladder_up_wild.png')]:
                ladder=Image.open(NATIVE/native).convert('RGBA')
                tint=(173,160,131,255) if skin=='plain' else (150,136,111,255) if skin=='gloomy' else (182,205,220,255)
                alpha=ladder.getchannel('A')
                ladder=Image.blend(ladder,Image.new('RGBA',ladder.size,tint),.22)
                ladder.putalpha(alpha)
                ladder.thumbnail((108,108),Image.Resampling.LANCZOS)
                tile=ground.copy()
                if kind=='ladder-world':
                    # The native up/world ladder bitmaps have identical pixels.
                    # A soft daylight pool identifies the wilderness exit.
                    halo=Image.new('L',(SIZE,SIZE));draw=ImageDraw.Draw(halo)
                    draw.ellipse((13,12,115,116),fill=190)
                    halo=halo.filter(ImageFilter.GaussianBlur(8))
                    light=(211,194,151,255) if skin=='plain' else (190,166,104,255) if skin=='gloomy' else (223,238,233,255)
                    tile=Image.composite(Image.new('RGBA',(SIZE,SIZE),light),tile,halo)
                tile.alpha_composite(ladder,((SIZE-ladder.width)//2,(SIZE-ladder.height)//2))
                outputs[f'{kind}{p}.png']=parity(tile,p)
            for name,tile in outputs.items():
                path=out/skin/name;path.parent.mkdir(parents=True,exist_ok=True)
                tile.save(path,optimize=True)
                dest=runtime/skin/name;dest.parent.mkdir(parents=True,exist_ok=True)
                shutil.copy2(path,dest)
                files[f'{skin}/{name}']=hashlib.sha256(path.read_bytes()).hexdigest()
                for size in (48,64,96):
                    target=review/str(size)/skin/name;target.parent.mkdir(parents=True,exist_ok=True)
                    tile.resize((size,size),Image.Resampling.LANCZOS).save(target)
    (HERE/'export-manifest.json').write_text(json.dumps({'count':len(files),'files':files},indent=2)+'\n')
    columns=['floor0.png','creep-0-0.png','creep-15-0.png','wall-0-0.png','wall-15-0.png',
             'ladder-up0.png','ladder-down0.png','ladder-world0.png']
    for size in (48,64,96):
        sheet=Image.new('RGB',(len(columns)*size,3*size),(36,34,39))
        for row,skin in enumerate(('gloomy','dreamy','plain')):
            for col,name in enumerate(columns):
                tile=Image.open(review/str(size)/skin/name).convert('RGB')
                sheet.paste(tile,(col*size,row*size))
        sheet.save(review/f'contact-{size}.png')
    print(len(files),'runtime tiles')
if __name__=='__main__': main()
