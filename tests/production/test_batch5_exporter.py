"""Batch 5 (Charred Scar / Fearscape lava walls, Sher'Tul Fortress) exports."""
import hashlib,json,unittest
from pathlib import Path
from PIL import Image,ImageStat
ROOT=Path(__file__).resolve().parents[2]
SUITE=ROOT/'art/terrain-batch5-v1'
GFX=ROOT/'data/gfx/refined'
def lum(rel):
 with Image.open(GFX/rel) as im:return ImageStat.Stat(im.convert('L')).mean[0]
class Batch5ExporterTest(unittest.TestCase):
 def setUp(self):
  self.manifest=json.loads((SUITE/'export-manifest.json').read_text())
 def test_no_imagegen_and_pinned_sources(self):
  self.assertEqual(self.manifest['imagegen_calls'],0)
  base=ROOT.parents[2]
  for rel,sha in self.manifest['sources'].items():
   self.assertEqual(hashlib.sha256((base/rel).read_bytes()).hexdigest(),sha,rel)
 def test_exact_exports(self):
  stems=(['shertul/floor','gloom/pit/floor','gloom/pit/ladder-up','gloom/pit/ladder-down','gloom/pit/ladder-world']+[f'gloom/pit/wall-{m}-' for m in range(16)]+[f'shertul/wall-{m}-' for m in range(16)]+[f'scorch/wall-{m}-' for m in range(16)])
  expected={f'{s}{p}.png' for s in stems for p in (0,1)}
  self.assertEqual(set(self.manifest['files']),expected)
  for name,sha in self.manifest['files'].items():
   p=GFX/name;self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),sha,name)
   with Image.open(p) as im:
    self.assertEqual(im.size,(128,128));self.assertEqual(im.mode,'RGB')
  # Every board pair keeps the >=10% luminance parity step.
  for stem in stems:
   a,b=lum(stem+'0.png'),lum(stem+'1.png')
   self.assertGreaterEqual((a-b)/a,.10,stem)
  self.assertGreaterEqual(self.manifest['parity_min'],.10)
 def test_reused_parity_pairs(self):
  # Reused suites drawn by the batch 5 zones keep the same >=10% parity step.
  stems=(['daikara/lava-floor','cave/floor','cave/ladder-up','cave/ladder-down','cave/ladder-world',
          'sand/floor','sand/ladder-world','underwater/floor','underwater/door-closed','underwater/door-open',
          'underwater/stairs-up','underwater/stairs-down','underwater/stairs-world','gloom/plain/floor',
          'gloom/plain/ladder-up','gloom/plain/ladder-down']+[f'burnt/lava-{m}-' for m in range(16)]+
         [f'cave/wall-{m}-' for m in range(16)]+[f'sand/wall-{m}-' for m in range(16)]+
         [f'underwater/wall-{m}-' for m in range(16)]+[f'gloom/plain/wall-{m}-' for m in range(16)])
  for stem in stems:
   a,b=lum(stem+'0.png'),lum(stem+'1.png')
   self.assertGreaterEqual((a-b)/a,.10,stem)
 def test_floor_wall_separation(self):
  # Ash-basalt lava walls are clearly lighter than the dark lava floor
  # (Daikara mountain/lava-floor relation) and clearly different from lava.
  floor=lum('daikara/lava-floor0.png')
  for m in range(16):self.assertGreater((lum(f'scorch/wall-{m}-0.png')-floor)/floor,.30,m)
  # Sher'Tul: pale walkable panels, dark graphite blocking walls.
  sfloor=lum('shertul/floor0.png')
  for m in range(16):self.assertGreater((sfloor-lum(f'shertul/wall-{m}-0.png'))/sfloor,.45,m)
  # Orc Breeding Pit readability rework: a calm pale floor and solid dark
  # walls far below it, for both parities (the dark floor parity must still
  # sit well above the light wall parity).
  for p in (0,1):
   pfloor=lum(f'gloom/pit/floor{p}.png')
   for m in range(16):
    for q in (0,1):self.assertGreater((pfloor-lum(f'gloom/pit/wall-{m}-{q}.png'))/pfloor,.55,(p,m,q))
 def test_pit_calm_surfaces(self):
  # Calm materials: a smooth floor and a near-uniform wall interior (the
  # only detail sits on the faces toward open floor).
  def sd(rel,box=None):
   with Image.open(GFX/rel) as im:
    g=im.convert('L')
    return ImageStat.Stat(g.crop(box) if box else g).stddev[0]
  for p in (0,1):
   self.assertLess(sd(f'gloom/pit/floor{p}.png'),4.0,p)
   self.assertLess(sd(f'gloom/pit/wall-15-{p}.png'),3.0,p)
   for m in range(16):self.assertLess(sd(f'gloom/pit/wall-{m}-{p}.png',(8,8,120,88)),4.0,(m,p))
  self.assertGreater(sd('gloom/plain/floor0.png'),2*sd('gloom/pit/floor0.png'))
if __name__=='__main__':unittest.main()
