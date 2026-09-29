"""Burnt terrain source provenance, exports and parity gate."""
import hashlib,json,unittest
from pathlib import Path
from PIL import Image,ImageStat

ROOT=Path(__file__).resolve().parents[2]
SUITE=ROOT/'art/terrain-burnt-v1'
OUT=ROOT/'data/gfx/refined/burnt'

class BurntExports(unittest.TestCase):
    def test_manifest_and_parity(self):
        report=json.loads((SUITE/'export-manifest.json').read_text())
        self.assertEqual(report['imagegen_calls'],2)
        files=report['runtime_sha256']
        self.assertEqual(len(files),42)
        self.assertEqual(set(files),{p.name for p in OUT.glob('*.png')})
        for name,digest in files.items():
            path=OUT/name
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),digest,name)
            with Image.open(path) as image:
                self.assertEqual(image.size,(128,128),name)
        for name in (n for n in files if n.endswith('0.png')):
            mate=name[:-5]+'1.png'
            self.assertIn(mate,files)
            with Image.open(OUT/name) as first, Image.open(OUT/mate) as second:
                a=ImageStat.Stat(first.convert('L')).mean[0]
                b=ImageStat.Stat(second.convert('L')).mean[0]
            self.assertGreaterEqual((a-b)/a,.10,name)

if __name__=='__main__':unittest.main()
