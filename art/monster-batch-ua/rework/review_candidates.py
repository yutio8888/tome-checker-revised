"""Read generated candidate bytes; mechanically export and show unchanged gates."""
import argparse, hashlib, json, math, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
import check_token_style
parser = argparse.ArgumentParser()
parser.add_argument('master', type=Path)
parser.add_argument('identity')
a = parser.parse_args()
folder = HERE / 'candidates' / a.master.stem
folder.mkdir(parents=True, exist_ok=True)
canvas = Image.new('RGBA', (280, 126), (46, 50, 46, 255))
ImageDraw.Draw(canvas).text((4, 3), a.master.stem, fill='white')
x = 4
for size in (48, 64, 96, 128):
    target = folder / f'{size}.png'
    subprocess.run([str(ROOT / 'tools/bin/export_token'), str(a.master), str(target), str(size)], check=True, capture_output=True)
    with Image.open(target) as image:
        if size < 128:
            canvas.alpha_composite(image, (x, 22 + (96 - size) // 2)); x += size + 10
        else:
            vals = [.299*r+.587*g+.114*b for y in range(128) for x in range(128)
                    for r,g,b,alpha in [image.getpixel((x,y))]
                    if alpha >= 180 and math.hypot(x+.5-64,y+.5-64)/64 <= .55]
            luminance = round(sum(vals)/len(vals),2)
canvas.convert('RGB').save(folder / '48-64-96.png')
result = check_token_style.check_asset(folder/'128.png', a.master, a.identity, allow_grandfather=False)
summary = {'master':str(a.master),'sha256':hashlib.sha256(a.master.read_bytes()).hexdigest(),
           'body_luminance':luminance,'unchanged_body_minimum':65.0,'body_passed':luminance>=65.0,'style_gate':result}
(folder/'gates.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps({k:v for k,v in summary.items() if k!='style_gate'},indent=2))
print('style', result['passed'], 'blocking', result['blocking'], 'warnings', result['warnings'])
