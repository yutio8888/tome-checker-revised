"""Abashed static tree reuses approved art and connected rock tiles."""
import hashlib,json,unittest
from pathlib import Path
from PIL import Image,ImageStat
ROOT=Path(__file__).resolve().parents[2]
SUITE=ROOT/'art/terrain-floating-tree-t5'
OUT=ROOT/'data/gfx/refined/void'
class FloatingTreeExporterTest(unittest.TestCase):
 def test_provenance_masks_and_parity(self):
  manifest=json.loads((SUITE/'export-manifest.json').read_text())
  self.assertEqual(manifest['new_imagegen_calls'],0)
  self.assertEqual(hashlib.sha256((ROOT/manifest['source_master']).read_bytes()).hexdigest(),manifest['source_sha256'])
  self.assertEqual(set(manifest['files']),{f'rocks-tree-{mask}-{p}.png' for mask in range(16) for p in (0,1)})
  for mask in range(16):
   means=[]
   for p in (0,1):
    name=f'rocks-tree-{mask}-{p}.png';file=OUT/name
    self.assertEqual(hashlib.sha256(file.read_bytes()).hexdigest(),manifest['files'][name])
    with Image.open(file) as im:
     self.assertEqual((im.size,im.mode),((128,128),'RGB'))
     means.append(ImageStat.Stat(im.convert('L')).mean[0])
   self.assertGreaterEqual((means[0]-means[1])/means[0],.10)
if __name__=='__main__':unittest.main()
