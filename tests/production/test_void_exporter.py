"""Void family masters, connected exports, parity, and movement value cues."""
import hashlib,json,unittest
from pathlib import Path
from PIL import Image,ImageStat
ROOT=Path(__file__).resolve().parents[2]
SUITE=ROOT/'art/terrain-void-v1'
OUT=ROOT/'data/gfx/refined/void'

class VoidExporterTest(unittest.TestCase):
 def test_option_locale_keys(self):
  hook=(ROOT/'hooks/load.lua').read_text().split("text=_t'Cycle Native",1)[1].split("'},",1)[0]
  hook='Cycle Native'+hook.replace("\\'", "'")
  for locale,names in (('zh_hans',('混沌之沼','次元浮岛','时空裂隙')),
                       ('zh_hant',('混沌之沼','次元浮島','時空裂隙'))):
   line=(ROOT/f'data/locales/{locale}.lua').read_text().splitlines()[14]
   key=line.split('t("',1)[1].split('", "',1)[0]
   self.assertEqual(key,hook)
   for name in names:self.assertIn(name,line)
 def test_selected_exports(self):
  manifest=json.loads((SUITE/'export-manifest.json').read_text())
  self.assertEqual(manifest['imagegen_calls'],3)
  expected={f'{family}-{mask}-{parity}.png' for family in ('rift','rocks') for mask in range(16) for parity in (0,1)}
  expected|={f'{family}{parity}.png' for family in ('floor','space') for parity in (0,1)}
  self.assertEqual(set(manifest['files']),expected)
  for name,sha in manifest['files'].items():
   with self.subTest(name=name):
    p=OUT/name;self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),sha)
    with Image.open(p) as im:self.assertEqual((im.size,im.getchannel('A').getextrema() if 'A' in im.getbands() else (255,255)),((128,128),(255,255)))
  for name,sha in manifest['masters'].items():
   self.assertEqual(hashlib.sha256((SUITE/'masters'/name).read_bytes()).hexdigest(),sha)
 def test_parity_and_walkability_cue(self):
  def mean(name):
   with Image.open(OUT/name) as im:return ImageStat.Stat(im.convert('L')).mean[0]
  for name in ['floor','space']+[f'{family}-{mask}-' for family in ('rift','rocks') for mask in range(16)]:
   with self.subTest(name=name):
    bright,dark=mean(name+'0.png'),mean(name+'1.png')
    self.assertGreaterEqual((bright-dark)/bright,.10)
  self.assertGreater((mean('floor0.png')-mean('rift-15-0.png'))/mean('floor0.png'),.30)
  self.assertGreater((mean('rocks-15-0.png')-mean('space0.png'))/mean('rocks-15-0.png'),.30)
if __name__=='__main__':unittest.main()
