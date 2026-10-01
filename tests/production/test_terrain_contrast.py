"""Additional readability floor; existing gates remain unchanged."""
import importlib.util
from pathlib import Path
import unittest
from PIL import Image
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('contrast_export',ROOT/'art/terrain-contrast-v1/export.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class ContrastTests(unittest.TestCase):
 def test_floor_wall_separation(self):
  for family in m.GAINS:
   for p in (0,1):
    with self.subTest(family=family,parity=p):
     f=m.lab(Image.open(m.floor(family,p)))
     w=m.lab(Image.open(ROOT/'data/gfx/refined'/family/f'{"old-wall" if family=="maze" else "wall"}-15-{p}.png'))
     self.assertGreaterEqual(float(np.linalg.norm(f-w)),25)
     self.assertGreaterEqual(float(f[0]-w[0]),24)
 def test_selected_exports(self):
  for p in (ROOT/'art/terrain-contrast-v1/exports').glob('*/*.png'):
   self.assertEqual(p.read_bytes(),(ROOT/'data/gfx/refined'/p.parent.name/p.name).read_bytes())
