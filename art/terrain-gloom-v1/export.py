#!/usr/bin/env python3
"""Deterministic 128px board exports from ImageGen masters and native ladder shapes."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageEnhance,ImageFilter,ImageOps
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

def vegetation_wall(source,mask,skin):
    """A continuous blocking mass, textured entirely by the selected master."""
    box=source.getchannel('A').getbbox()
    art=ImageOps.fit(source.crop(box),(SIZE,SIZE),method=Image.Resampling.LANCZOS)
    base=(55,48,39,255) if skin=='plain' else (48,37,50,255) if skin=='gloomy' else (68,72,91,255)
    tile=Image.new('RGBA',(SIZE,SIZE),base)
    # The blurred enlarged master fills transparent gaps between individual
    # mushrooms; the crisp pass preserves the generated caps and stems.
    tile.alpha_composite(art.filter(ImageFilter.GaussianBlur(11)))
    tile.alpha_composite(art)
    # Shared edges carry the same wall material across adjacent cells.
    if mask&1: tile.paste(tile.crop((18,18,110,38)).resize((SIZE,18)),(0,0))
    if mask&2: tile.paste(tile.crop((90,18,110,110)).resize((18,SIZE)),(110,0))
    if mask&4: tile.paste(tile.crop((18,90,110,110)).resize((SIZE,18)),(0,110))
    if mask&8: tile.paste(tile.crop((18,18,38,110)).resize((18,SIZE)),(0,0))
    # Interior cells form a continuous low-detail body; exposed cells keep
    # the mushroom contours that explain what the obstacle is.
    joins=mask.bit_count()
    if joins>=3:
        tile=Image.blend(tile,tile.filter(ImageFilter.GaussianBlur(9)),.78 if joins==4 else .46)
    return tile

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
        wall=Image.open(HERE/'masters'/f'{source}-vegetation-v1.png').convert('RGBA')
        if skin=='plain': wall=plain(wall,'#292824','#a89b7e',.78)
        for p in (0,1):
            ground=floor.copy()
            outputs={f'floor{p}.png':parity(ground,p)}
            for mask in range(16):
                outputs[f'wall-{mask}-{p}.png']=parity(vegetation_wall(wall,mask,skin),p)
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
