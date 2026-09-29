"""Selected board graveyard props keep complete opaque cells and clear parity."""
import hashlib,json,unittest
from pathlib import Path
from PIL import Image,ImageStat
ROOT=Path(__file__).resolve().parents[2]
SUITE=ROOT/'art/terrain-graveyard-v1'
OUT=ROOT/'data/gfx/refined/graveyard'

class GraveyardExporterTest(unittest.TestCase):
 def test_selected_exports(self):
  manifest=json.loads((SUITE/'export-manifest.json').read_text())
  self.assertEqual(manifest['imagegen_calls'],0)
  self.assertEqual(set(manifest['files']),{f'{stem}{p}.png' for stem in ('grave','coffin','coffin-open','mausoleum') for p in (0,1)})
  for name,sha in manifest['files'].items():
   path=OUT/name
   self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),sha)
   with Image.open(path) as im:self.assertEqual(im.size,(128,128))
  for stem in ('grave','coffin','coffin-open','mausoleum'):
   with Image.open(OUT/f'{stem}0.png') as a, Image.open(OUT/f'{stem}1.png') as b:
    bright=ImageStat.Stat(a.convert('L')).mean[0]
    dark=ImageStat.Stat(b.convert('L')).mean[0]
   self.assertGreaterEqual((bright-dark)/bright,.10)
if __name__=='__main__':unittest.main()
