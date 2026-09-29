"""T5 underwater masters, exact exports, and parity/value cues."""
import hashlib,json,unittest
from pathlib import Path
from PIL import Image,ImageStat
ROOT=Path(__file__).resolve().parents[2]
SUITE=ROOT/'art/terrain-underwater-v1'
OUT=ROOT/'data/gfx/refined/underwater'
class UnderwaterExporterTest(unittest.TestCase):
 def test_selected_exports_and_parity(self):
  manifest=json.loads((SUITE/'export-manifest.json').read_text())
  self.assertEqual(manifest['imagegen_calls'],3)
  stems=['floor','door-closed','door-open','stairs-up','stairs-down']+[f'wall-{m}-' for m in range(16)]
  expected={f'{s}{p}.png' for s in stems for p in (0,1)}
  self.assertEqual(set(manifest['files']),expected)
  means={}
  for name,sha in manifest['files'].items():
   p=OUT/name;self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),sha)
   with Image.open(p) as im:
    self.assertEqual(im.size,(128,128))
    self.assertEqual(im.mode,'RGB')
    means[name]=ImageStat.Stat(im.convert('L')).mean[0]
  for stem in stems:
   self.assertGreaterEqual((means[stem+'0.png']-means[stem+'1.png'])/means[stem+'0.png'],.10)
  self.assertGreater((means['floor0.png']-means['wall-15-0.png'])/means['floor0.png'],.30)
  for name,sha in manifest['masters'].items():
   self.assertEqual(hashlib.sha256((SUITE/'masters'/name).read_bytes()).hexdigest(),sha)
 def test_option_locale_keys(self):
  hook=(ROOT/'hooks/load.lua').read_text().split("text=_t'Cycle Native",1)[1].split("'},",1)[0]
  hook='Cycle Native'+hook.replace("\\'", "'")
  for locale in ('zh_hans','zh_hant'):
   line=(ROOT/f'data/locales/{locale}.lua').read_text().splitlines()[14]
   self.assertEqual(line.split('t("',1)[1].split('\", \"',1)[0],hook)
if __name__=='__main__':unittest.main()
