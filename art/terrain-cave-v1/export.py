#!/usr/bin/env python3
"""Export the three selected cave masters into connected 128px board tiles."""
from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter, ImageOps, ImageDraw, ImageStat
import hashlib, json, shutil

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
NATIVE=ROOT.parents[1]/'modules/tome/data/gfx/shockbolt/terrain/cave'
SIZE=128

def master(kind):
    return Image.open(HERE/'masters'/f'cave-{kind}-v1.png').convert('RGBA')

def construction(im, size):
    body=im.crop(im.getchannel('A').getbbox())
    body=ImageOps.contain(body,(size,size),method=Image.Resampling.LANCZOS)
    out=Image.new('RGBA',(SIZE,SIZE),(0,0,0,0))
    out.alpha_composite(body,((SIZE-body.width)//2,(SIZE-body.height)//2))
    return out

def floor_tile(im):
    # The source is an earthy, stone-strewn cave. Broad softness keeps loose
    # pebbles decorative and avoids implying movement-blocking rocks.
    tile=ImageOps.fit(im,(SIZE,SIZE),method=Image.Resampling.LANCZOS)
    tile=ImageEnhance.Contrast(tile.filter(ImageFilter.GaussianBlur(.45))).enhance(.82)
    tile=ImageEnhance.Brightness(tile).enhance(1.25)
    return tile

def wall_material(im):
    body=im.crop(im.getchannel('A').getbbox())
    w,h=body.size
    # Use the broad top planes of the generated wall for the connected top;
    # the front crop appears only at a south edge facing passable floor.
    face=ImageOps.fit(body.crop((int(w*.23),int(h*.53),int(w*.77),int(h*.88))),
                      (SIZE,38),method=Image.Resampling.LANCZOS)
    return body,face

def wall_tile(material,mask,parity):
    body,face=material;w,h=body.size
    cw,ch=int(w*.57),int(h*.34)
    sx=(mask*127)%(w-cw)
    sy=int(h*.06)+(mask*23)%(int(h*.13))
    top=ImageOps.fit(body.crop((sx,sy,sx+cw,sy+ch)),(SIZE,SIZE),method=Image.Resampling.LANCZOS)
    top=ImageEnhance.Color(top).enhance(.78)
    top=ImageEnhance.Contrast(top.filter(ImageFilter.GaussianBlur(.65))).enhance(.72)
    top=ImageEnhance.Brightness(top).enhance(.57)
    tile=Image.new('RGBA',(SIZE,SIZE),(54,39,29,255));tile.alpha_composite(top)
    # N/E/S/W bit set means a neighbouring cave wall. Edge shading is baked
    # into one texture; interior 15 has no cliff face or stacked overhang.
    if not mask&1:
        rim=Image.new('RGBA',(SIZE,5),(86,65,44,255))
        tile.paste(Image.blend(tile.crop((0,0,SIZE,5)),rim,.45),(0,0))
    if not mask&8:
        strip=ImageEnhance.Brightness(tile.crop((6,0,17,SIZE))).enhance(.72)
        tile.paste(strip.resize((9,SIZE)),(0,0))
    if not mask&2:
        strip=ImageEnhance.Brightness(tile.crop((109,0,121,SIZE))).enhance(.68)
        tile.paste(strip.resize((9,SIZE)),(119,0))
    if not mask&4:
        cliff=ImageEnhance.Brightness(face).enhance(.39)
        tile.paste(cliff,(0,90))
        shadow=Image.new('RGBA',(SIZE,4),(23,17,16,255))
        tile.paste(Image.blend(tile.crop((0,87,SIZE,91)),shadow,.55),(0,87))
    return tile

def ladder_tile(im,floor):
    tile=floor.copy()
    glow=Image.new('L',(SIZE,SIZE))
    ImageDraw.Draw(glow).ellipse((21,7,107,85),fill=90)
    glow=glow.filter(ImageFilter.GaussianBlur(10))
    tile=Image.composite(Image.new('RGBA',(SIZE,SIZE),(231,176,91,255)),tile,glow)
    cutout=construction(im,110)
    tile.alpha_composite(cutout)
    return tile

def level_ladder_tile(floor,ladder,down=False):
    # The selected generated stair master remains recognisable at 48px for
    # ascent; the native descent silhouette reads as a separate recessed pit.
    tile=floor.copy()
    if down:
        native=Image.open(NATIVE/'cave_stairs_down_3_01.png').convert('RGBA')
        shade=Image.new('RGBA',(SIZE,SIZE),(0,0,0,0))
        ImageDraw.Draw(shade).ellipse((20,34,108,105),fill=(26,20,21,170))
        tile.alpha_composite(shade)
        native=ImageOps.contain(native,(112,112),method=Image.Resampling.LANCZOS)
        tile.alpha_composite(native,((SIZE-native.width)//2,(SIZE-native.height)//2))
    else:
        tile.alpha_composite(construction(ladder,110))
    return tile

def decorated_floor(floor,kind,index):
    native=Image.open(NATIVE/f'cave_{kind}_{index}_01.png').convert('RGBA')
    tile=floor.copy()
    # Keep native cutouts small and cosmetic: a 64px source occupies at most
    # half a 128px board cell before game downsampling.
    tile.alpha_composite(native,(32,32))
    return tile

def main():
    floor=floor_tile(master('floor'))
    wall=wall_material(master('wall'))
    ladder=master('ladder')
    out=HERE/'exports/runtime';runtime=ROOT/'data/gfx/refined/cave';review=HERE/'review'
    hashes={};lums={}
    for parity in (0,1):
        tiles={f'floor{parity}.png':floor,
               f'ladder-world{parity}.png':ladder_tile(ladder,floor),
               f'ladder-up{parity}.png':level_ladder_tile(floor,ladder),
               f'ladder-down{parity}.png':level_ladder_tile(floor,ladder,True)}
        for index in range(1,10):tiles[f'floor-rock-{index}-{parity}.png']=decorated_floor(floor,'rock',index)
        for index in range(1,3):tiles[f'floor-mushroom-{index}-{parity}.png']=decorated_floor(floor,'mushroom',index)
        for mask in range(16):tiles[f'wall-{mask}-{parity}.png']=wall_tile(wall,mask,parity)
        for name,tile in tiles.items():
            if parity:tile=ImageEnhance.Brightness(tile).enhance(.875)
            tile=tile.convert('RGB')
            path=out/name;path.parent.mkdir(parents=True,exist_ok=True);tile.save(path,optimize=True)
            runtime.mkdir(parents=True,exist_ok=True);shutil.copy2(path,runtime/name)
            hashes[name]=hashlib.sha256(path.read_bytes()).hexdigest()
            lums[name]=ImageStat.Stat(tile.convert('L')).mean[0]
            for size in (48,64,96):
                target=review/str(size)/name;target.parent.mkdir(parents=True,exist_ok=True)
                tile.resize((size,size),Image.Resampling.LANCZOS).save(target)
    cutouts={f'cave_{kind}_{index}_01.png':hashlib.sha256((NATIVE/f'cave_{kind}_{index}_01.png').read_bytes()).hexdigest()
             for kind,count in (('rock',9),('mushroom',2)) for index in range(1,count+1)}
    for name in ('cave_stairs_down_3_01.png',):
        cutouts[name]=hashlib.sha256((NATIVE/name).read_bytes()).hexdigest()
    (HERE/'export-manifest.json').write_text(json.dumps({'count':len(hashes),'files':hashes,'luminance':lums,'native_cutouts':cutouts},indent=2)+'\n')
    for size in (48,64,96):
        names=['floor0.png','wall-0-0.png','wall-15-0.png','ladder-world0.png','ladder-up0.png','ladder-down0.png']
        sheet=Image.new('RGB',(len(names)*size,2*size))
        for row in (0,1):
            for col,name in enumerate(names):
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
    gap=(lums['floor0.png']-lums['wall-15-0.png'])/lums['floor0.png']
    parity=min((lums[n]-lums[n[:-5]+'1.png'])/lums[n] for n in lums if n.endswith('0.png'))
    print(len(hashes),'tiles; source wall gap',round(gap,3),'min parity',round(parity,3))

if __name__=='__main__':main()
