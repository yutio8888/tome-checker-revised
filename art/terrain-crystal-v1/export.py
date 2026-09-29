#!/usr/bin/env python3
"""Export selected Scintillating Caves masters to 128px connected board terrain."""
from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter, ImageOps, ImageDraw, ImageStat
import hashlib, json, shutil
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
NATIVE=ROOT.parents[1]/'modules/tome/data/gfx/shockbolt/terrain'
SIZE=128

def load(name):
    return Image.open(HERE/'masters'/f'crystal-{name}-v1.png').convert('RGBA')

def opaque(im):
    stone=ImageOps.fit(im,(SIZE,SIZE),method=Image.Resampling.LANCZOS)
    # The native map tint and FOV darken both families substantially. Give the
    # passable stone a high, near-neutral value before that shared lighting.
    stone=ImageEnhance.Color(stone).enhance(.52)
    stone=ImageEnhance.Contrast(stone.filter(ImageFilter.GaussianBlur(.55))).enhance(.84)
    return ImageEnhance.Brightness(stone).enhance(1.84)

def construction(im, size=118):
    bbox=im.getchannel('A').getbbox()
    art=ImageOps.contain(im.crop(bbox),(size,size),method=Image.Resampling.LANCZOS)
    out=Image.new('RGBA',(SIZE,SIZE),(0,0,0,0))
    out.alpha_composite(art,((SIZE-art.width)//2,(SIZE-art.height)//2))
    return out

def wall_material(wall):
    """Separate the ImageGen crystal top and vertical face from one master."""
    body=wall.crop(wall.getchannel('A').getbbox())
    w,h=body.size
    front=ImageOps.fit(body.crop((int(w*.15),int(h*.48),int(w*.85),int(h*.92))),
                       (SIZE,38),method=Image.Resampling.LANCZOS)
    front=ImageOps.colorize(ImageOps.grayscale(front),(13,17,29),(39,49,70)).convert('RGBA')
    return body,front

def wall_tile(material,mask,parity):
    # N/E/S/W mask bits mean wall neighbours. An interior cell (15) has only
    # the calm top. Vertical faces occur exclusively on exposed sides; the
    # south edge gets the substantial cliff face seen from overhead.
    body,front=material
    # Select different broad crystalline planes from the generated wall master
    # for each outline/parity. The source facets and glints fill the top; only
    # the south-exposed mask gets a vertical face below them.
    w,h=body.size;cw,ch=int(w*.58),int(h*.38)
    sx=(mask*137+parity*241)%(w-cw)
    sy=int(h*.03)+(mask*29+parity*47)%(int(h*.12))
    facets=ImageOps.fit(body.crop((sx,sy,sx+cw,sy+ch)),(SIZE,SIZE),method=Image.Resampling.LANCZOS)
    opaque_top=Image.new('RGBA',(SIZE,SIZE),(34,42,62,255))
    opaque_top.alpha_composite(facets)
    tile=ImageEnhance.Brightness(ImageEnhance.Color(opaque_top).enhance(1.16)).enhance(.56)
    tile=ImageEnhance.Brightness(tile).enhance(52/ImageStat.Stat(tile.convert('L')).mean[0])
    # Bake one small native crystal cutout into exposed wall tops. The runtime
    # still draws one board texture and suppresses makeCrystals add_displays.
    # Interior walls stay nearly calm; the two parities avoid one fixed stamp.
    exposed=[(mask&bit)==0 for bit in (1,2,4,8)]
    if any(exposed) or parity==0:
        index=(mask*3+parity*5)%6+1
        cluster=Image.open(NATIVE/f'crystal_alpha{index}.png').convert('RGBA')
        cluster=cluster.crop(cluster.getchannel('A').getbbox())
        cluster=ImageOps.contain(cluster,(47 if any(exposed) else 34,44 if any(exposed) else 34),method=Image.Resampling.LANCZOS)
        cluster=ImageEnhance.Brightness(cluster).enhance(1.28)
        alpha=cluster.getchannel('A').point(lambda value:value*9//10)
        cluster.putalpha(alpha)
        if not mask&4:x,y=58,43
        elif not mask&1:x,y=53,9
        elif not mask&2:x,y=81,31
        elif not mask&8:x,y=12,31
        else:x,y=76,24
        x+=parity*5+(mask%3-1)*3
        tile.alpha_composite(cluster,(x,y))
    top=tile.copy()
    if not mask&1:
        rim=Image.new('RGBA',(SIZE,5),(59,68,89,255))
        tile.paste(Image.blend(tile.crop((0,0,SIZE,5)),rim,.28),(0,0))
    if not mask&8:
        side=ImageEnhance.Brightness(top.crop((8,0,18,SIZE))).enhance(.74)
        tile.paste(side.resize((9,SIZE)),(0,0))
    if not mask&2:
        side=ImageEnhance.Brightness(top.crop((110,0,120,SIZE))).enhance(.68)
        tile.paste(side.resize((9,SIZE)),(119,0))
    if not mask&4:
        tile.paste(front,(0,90))
        shadow=Image.new('RGBA',(SIZE,3),(13,18,29,255))
        tile.paste(Image.blend(tile.crop((0,88,SIZE,91)),shadow,.40),(0,88))
    return tile

def ladder_tile(ladder,kind,floor):
    tile=floor.copy()
    # Native destinations remain in Grid fields; daylight and depth make
    # three board constructions distinguishable without fake arrows.
    wash={'ladder-up':(117,178,205,95),'ladder-down':(18,22,44,105),'ladder-world':(165,194,226,155)}[kind]
    mask=Image.new('L',(SIZE,SIZE));ImageDraw.Draw(mask).ellipse((8,7,120,121),fill=wash[3]);mask=mask.filter(ImageFilter.GaussianBlur(9))
    tile=Image.composite(Image.new('RGBA',(SIZE,SIZE),wash[:3]+(255,)),tile,mask)
    ladder=construction(ladder,110)
    if kind=='ladder-down':ladder=ImageEnhance.Brightness(ladder).enhance(.76)
    elif kind=='ladder-world':ladder=ImageEnhance.Brightness(ladder).enhance(1.12)
    tile.alpha_composite(ladder)
    return tile

def main():
    floor=opaque(load('floor'));wall=wall_material(load('wall'));ladder=load('ladder')
    runtime=ROOT/'data/gfx/refined/crystal';out=HERE/'exports/runtime';review=HERE/'review'
    files={};lums={}
    for parity in (0,1):
        outputs={f'floor{parity}.png':floor}
        for mask in range(16):outputs[f'wall-{mask}-{parity}.png']=wall_tile(wall,mask,parity)
        for kind in ('ladder-up','ladder-down','ladder-world'):
            outputs[f'{kind}{parity}.png']=ladder_tile(ladder,kind,floor)
        for name,tile in outputs.items():
            if parity:tile=ImageEnhance.Brightness(tile).enhance(.875)
            tile=tile.convert('RGB')
            path=out/name;path.parent.mkdir(parents=True,exist_ok=True);tile.save(path,optimize=True)
            runtime.mkdir(parents=True,exist_ok=True);shutil.copy2(path,runtime/name)
            files[name]=hashlib.sha256(path.read_bytes()).hexdigest()
            lums[name]=ImageStat.Stat(tile.convert('L')).mean[0]
            for size in (48,64,96):
                target=review/str(size)/name;target.parent.mkdir(parents=True,exist_ok=True)
                tile.resize((size,size),Image.Resampling.LANCZOS).save(target)
    native_cutouts={f'crystal_alpha{i}.png':hashlib.sha256((NATIVE/f'crystal_alpha{i}.png').read_bytes()).hexdigest()
                    for i in range(1,7)}
    (HERE/'export-manifest.json').write_text(json.dumps({'count':len(files),'files':files,'luminance':lums,
                                                         'native_cutouts':native_cutouts},indent=2)+'\n')
    for size in (48,64,96):
        columns=['floor0.png','wall-0-0.png','wall-15-0.png','ladder-up0.png','ladder-down0.png','ladder-world0.png']
        sheet=Image.new('RGB',(len(columns)*size,2*size),(25,29,45))
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
