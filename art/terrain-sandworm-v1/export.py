#!/usr/bin/env python3
"""Export selected Sandworm masters to 128px connected board terrain."""
from pathlib import Path
from PIL import Image, ImageChops, ImageEnhance, ImageFilter, ImageOps, ImageDraw, ImageStat
import hashlib, json, shutil
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
SIZE=128

def load(name):
    return Image.open(HERE/'masters'/f'sand-{name}-v1.png').convert('RGBA')

def opaque(im):
    return ImageOps.fit(im,(SIZE,SIZE),method=Image.Resampling.LANCZOS)

def construction(im, size=118):
    bbox=im.getchannel('A').getbbox()
    art=ImageOps.contain(im.crop(bbox),(size,size),method=Image.Resampling.LANCZOS)
    out=Image.new('RGBA',(SIZE,SIZE),(0,0,0,0))
    out.alpha_composite(art,((SIZE-art.width)//2,(SIZE-art.height)//2))
    return out

def wall_material(wall,floor):
    """Separate the master's compacted top from its vertical cliff face."""
    body=wall.crop(wall.getchannel('A').getbbox())
    w,h=body.size
    top=ImageOps.fit(body.crop((int(w*.12),int(h*.04),int(w*.88),int(h*.40))),
                     (SIZE,SIZE),method=Image.Resampling.LANCZOS)
    # Retain the master's small-scale grain while removing the broad slab
    # boundaries that would repeat as ledge rows across a wall mass.
    master_top=Image.new('RGBA',top.size,(145,145,145,255))
    master_top.alpha_composite(top)
    source=ImageOps.grayscale(master_top)
    broad=source.filter(ImageFilter.GaussianBlur(2))
    grain=ImageChops.add(source,ImageOps.invert(broad))
    grain=ImageEnhance.Contrast(grain).enhance(3.5)
    # Draw fine grain from lit stone surfaces, not from shadowed cracks.
    lit_stone=broad.point(lambda value:max(0,min(255,(value-140)*8)))
    grain=Image.composite(grain,Image.new('L',grain.size,128),lit_stone)
    compacted=ImageOps.colorize(ImageOps.grayscale(floor.filter(ImageFilter.GaussianBlur(1.4))),
                                (56,38,24),(151,116,69)).convert('RGBA')
    sandstone_grain=ImageOps.colorize(grain,(58,42,29),(148,107,65)).convert('RGBA')
    top=Image.blend(compacted,sandstone_grain,.40)
    front=ImageOps.fit(body.crop((int(w*.15),int(h*.48),int(w*.85),int(h*.92))),
                       (SIZE,38),method=Image.Resampling.LANCZOS)
    front=ImageOps.colorize(ImageOps.grayscale(front),(32,31,31),(91,78,62)).convert('RGBA')
    return top,front

def wall_tile(material,mask):
    # N/E/S/W mask bits mean wall neighbours. An interior cell (15) has only
    # the calm top. Vertical faces occur exclusively on exposed sides; the
    # south edge gets the substantial cliff face seen from overhead.
    top,front=material
    tile=top.copy()
    if not mask&1:
        rim=Image.new('RGBA',(SIZE,5),(112,106,83,255))
        tile.paste(Image.blend(tile.crop((0,0,SIZE,5)),rim,.28),(0,0))
    if not mask&8:
        side=ImageEnhance.Brightness(top.crop((8,0,18,SIZE))).enhance(.74)
        tile.paste(side.resize((9,SIZE)),(0,0))
    if not mask&2:
        side=ImageEnhance.Brightness(top.crop((110,0,120,SIZE))).enhance(.68)
        tile.paste(side.resize((9,SIZE)),(119,0))
    if not mask&4:
        tile.paste(front,(0,90))
        shadow=Image.new('RGBA',(SIZE,3),(40,38,34,255))
        tile.paste(Image.blend(tile.crop((0,88,SIZE,91)),shadow,.40),(0,88))
    return tile

def ladder_tile(ladder,kind,floor):
    tile=floor.copy()
    # Native destinations remain in Grid fields; daylight and depth make
    # three board constructions distinguishable without fake arrows.
    wash={'ladder-up':(214,185,117,95),'ladder-down':(59,39,26,105),'ladder-world':(238,216,151,155)}[kind]
    mask=Image.new('L',(SIZE,SIZE));ImageDraw.Draw(mask).ellipse((8,7,120,121),fill=wash[3]);mask=mask.filter(ImageFilter.GaussianBlur(9))
    tile=Image.composite(Image.new('RGBA',(SIZE,SIZE),wash[:3]+(255,)),tile,mask)
    ladder=construction(ladder,110)
    if kind=='ladder-down':ladder=ImageEnhance.Brightness(ladder).enhance(.76)
    elif kind=='ladder-world':ladder=ImageEnhance.Brightness(ladder).enhance(1.12)
    tile.alpha_composite(ladder)
    return tile

def main():
    floor=opaque(load('floor'));wall=wall_material(load('wall'),floor);ladder=load('ladder')
    runtime=ROOT/'data/gfx/refined/sand';out=HERE/'exports/runtime';review=HERE/'review'
    files={};lums={}
    for parity in (0,1):
        outputs={f'floor{parity}.png':floor}
        for mask in range(16):outputs[f'wall-{mask}-{parity}.png']=wall_tile(wall,mask)
        for kind in ('ladder-up','ladder-down','ladder-world'):
            outputs[f'{kind}{parity}.png']=ladder_tile(ladder,kind,floor)
        for name,tile in outputs.items():
            if parity:tile=ImageEnhance.Brightness(tile).enhance(.88)
            tile=tile.convert('RGB')
            path=out/name;path.parent.mkdir(parents=True,exist_ok=True);tile.save(path,optimize=True)
            runtime.mkdir(parents=True,exist_ok=True);shutil.copy2(path,runtime/name)
            files[name]=hashlib.sha256(path.read_bytes()).hexdigest()
            lums[name]=ImageStat.Stat(tile.convert('L')).mean[0]
            for size in (48,64,96):
                target=review/str(size)/name;target.parent.mkdir(parents=True,exist_ok=True)
                tile.resize((size,size),Image.Resampling.LANCZOS).save(target)
    (HERE/'export-manifest.json').write_text(json.dumps({'count':len(files),'files':files,'luminance':lums},indent=2)+'\n')
    for size in (48,64,96):
        columns=['floor0.png','wall-0-0.png','wall-15-0.png','ladder-up0.png','ladder-down0.png','ladder-world0.png']
        sheet=Image.new('RGB',(len(columns)*size,2*size),(43,35,29))
        for row in (0,1):
            for col,name in enumerate(columns):
                sheet.paste(Image.open(review/str(size)/name.replace('0.png',f'{row}.png')),(col*size,row*size))
        sheet.save(review/f'contact-{size}.png')
    field=Image.new('RGB',(10*64,8*64))
    for y in range(8):
        for x in range(10):
            if 2<=x<=7 and 2<=y<=5:
                mask=sum(bit for dx,dy,bit in ((0,-1,1),(1,0,2),(0,1,4),(-1,0,8))
                         if 2<=x+dx<=7 and 2<=y+dy<=5)
                name=f'wall-{mask}-{(x+y)%2}.png'
            else:name=f'floor{(x+y)%2}.png'
            field.paste(Image.open(out/name).resize((64,64),Image.Resampling.LANCZOS),(x*64,y*64))
    field.save(review/'wall-field-64.png')
    print(len(files),'tiles; min parity',min((lums[n]-lums[n[:-5]+'1.png'])/lums[n] for n in lums if n.endswith('0.png')))
if __name__=='__main__':main()
