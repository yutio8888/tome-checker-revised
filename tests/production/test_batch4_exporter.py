"""Batch 4 (Caldera, Southern Beach, Tranquil Meadow, Murgol, Conclave) exports."""
import hashlib,json,re,unittest
from pathlib import Path
from PIL import Image,ImageStat
ROOT=Path(__file__).resolve().parents[2]
SUITE=ROOT/'art/terrain-batch4-v1'
GFX=ROOT/'data/gfx/refined'
def lum(rel):
 with Image.open(GFX/rel) as im:return ImageStat.Stat(im.convert('L')).mean[0]
class Batch4ExporterTest(unittest.TestCase):
 def setUp(self):
  self.manifest=json.loads((SUITE/'export-manifest.json').read_text())
 def test_no_imagegen_and_pinned_sources(self):
  self.assertEqual(self.manifest['imagegen_calls'],0)
  base=ROOT.parents[2]
  for rel,sha in self.manifest['sources'].items():
   self.assertEqual(hashlib.sha256((base/rel).read_bytes()).hexdigest(),sha,rel)
 def test_exact_exports(self):
  stems=(['caldera/floor','caldera/tree-a','caldera/tree-b','caldera/tree-c','caldera/exit-up','caldera/exit-down','caldera/exit-world']+
   [f'caldera/poison-{m}-' for m in range(16)]+[f'caldera/wall-{m}-' for m in range(16)]+
   ['beach/sand','beach/tree-oak','beach/tree-pine','beach/tree-willow','beach/umbrella','beach/basket','keepsake/stew','underwater/stairs-world']+[f'conclave/wall-{m}-' for m in range(16)])
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
 def test_floor_wall_separation(self):
  floor=lum('caldera/floor0.png')
  for m in range(16):self.assertGreater((floor-lum(f'caldera/wall-{m}-0.png'))/floor,.30,m)
  for key in 'abc':self.assertGreater((floor-lum(f'caldera/tree-{key}0.png'))/floor,.30,key)
  # Poison water stays darker than the grass without becoming wall-dark.
  self.assertGreater((floor-lum('caldera/poison-15-0.png'))/floor,.15)
  # South Beach blocking trees fill their cell and stay clearly darker than
  # the open grass around them.
  grass=lum('grass0.png')
  for kind in ('oak','pine','willow'):self.assertGreater((grass-lum(f'beach/tree-{kind}0.png'))/grass,.25,kind)
  kfloor=lum('korpul/floor-a-0-0.png')
  for m in range(16):self.assertGreater((kfloor-lum(f'conclave/wall-{m}-0.png'))/kfloor,.30,m)
 def test_conclave_runtime_manifest(self):
  text=(ROOT/'data/terrain-conclave-manifest.lua').read_text()
  files=set(re.findall(r"\['checker-revised\+refined/(conclave/wall-\d+-[01]\.png)'\]=true",text))
  self.assertEqual(files,{f'conclave/wall-{m}-{p}.png' for m in range(16) for p in (0,1)})
  self.assertIn('ready=true',text)
if __name__=='__main__':unittest.main()
