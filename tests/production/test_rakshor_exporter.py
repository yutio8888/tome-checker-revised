"""Rak'Shor Pride bone family exports (art/terrain-rakshor-v1)."""
import hashlib,json,unittest
from pathlib import Path
from PIL import Image,ImageStat
ROOT=Path(__file__).resolve().parents[2]
SUITE=ROOT/'art/terrain-rakshor-v1'
GFX=ROOT/'data/gfx/refined'
KINDS=['floor','door-closed','door-open','stairs-up','stairs-down','stairs-exit','exit-world']
def stat(rel,box=None):
 with Image.open(GFX/rel) as im:
  g=im.convert('L')
  return ImageStat.Stat(g.crop(box) if box else g)
def lum(rel):return stat(rel).mean[0]
class RakshorExporterTest(unittest.TestCase):
 def setUp(self):
  self.manifest=json.loads((SUITE/'export-manifest.json').read_text())
  self.stems=[f'rakshor/{k}' for k in KINDS]+[f'rakshor/wall-{m}-' for m in range(16)]
 def test_no_imagegen_and_pinned_sources(self):
  self.assertEqual(self.manifest['imagegen_calls'],0)
  base=ROOT.parents[2]
  for rel,sha in self.manifest['sources'].items():
   self.assertEqual(hashlib.sha256((base/rel).read_bytes()).hexdigest(),sha,rel)
 def test_exact_exports_and_parity(self):
  expected={f'{s}{p}.png' for s in self.stems for p in (0,1)}
  self.assertEqual(set(self.manifest['files']),expected)
  on_disk={f'rakshor/{p.name}' for p in (GFX/'rakshor').iterdir()}
  self.assertEqual(on_disk,expected)
  for name,sha in self.manifest['files'].items():
   p=GFX/name;self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),sha,name)
   with Image.open(p) as im:
    self.assertEqual(im.size,(128,128));self.assertEqual(im.mode,'RGB')
  for stem in self.stems:
   a,b=lum(stem+'0.png'),lum(stem+'1.png')
   self.assertGreaterEqual((a-b)/a,.10,stem)
  self.assertGreaterEqual(self.manifest['parity_min'],.10)
 def test_floor_wall_separation_and_calm(self):
  # Pale calm sand floor, dark bone walls well below it for every parity pair.
  for p in (0,1):
   floor=lum(f'rakshor/floor{p}.png')
   self.assertLess(stat(f'rakshor/floor{p}.png').stddev[0],6.0,p)
   for m in range(16):
    for q in (0,1):self.assertGreater((floor-lum(f'rakshor/wall-{m}-{q}.png'))/floor,.55,(p,m,q))
    # Calm interior: the only strong detail sits on faces toward open floor.
    self.assertLess(stat(f'rakshor/wall-{m}-{p}.png',(8,8,120,88)).stddev[0],4.0,(m,p))
 def test_blocking_door_fills_cell(self):
  # The closed gate is an opaque, cell-filling blocker, darker than the floor.
  for p in (0,1):
   self.assertLess(lum(f'rakshor/door-closed{p}.png'),lum(f'rakshor/floor{p}.png')*.75,p)
if __name__=='__main__':unittest.main()
