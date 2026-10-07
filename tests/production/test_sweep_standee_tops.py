"""R46 sweep contract: the low-saturation light cut really triggers the flag.

The sweep is triage, not a product rule, but the R44 miss was a colour cut that
did not catch burb's (155,194,212) lightning (colour spread S = 57). This test
feeds a synthetic sprite whose top rows are exactly that colour and asserts the
light fraction and the flag, independent of the real sprites.
"""
import importlib.util
import tempfile
import unittest
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]


def _load_sweep():
    spec = importlib.util.spec_from_file_location(
        'sweep_standee_tops', ROOT / 'tools' / 'sweep_standee_tops.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class SweepColourTests(unittest.TestCase):
    def _synthetic(self, top_rgb, rows=8, top_w=16, body_rgb=(90, 60, 40, 255)):
        td = tempfile.TemporaryDirectory()
        sprite = Path(td.name) / 'synthetic.png'
        im = Image.new('RGBA', (64, 128), (0, 0, 0, 0))
        # The top rows: a narrow light fringe (below the 18px body-row width)
        # directly above the body mass, so only the colour cut can flag it.
        for y in range(rows):
            for x in range(24, 24 + top_w):
                im.putpixel((x, y), tuple(top_rgb) + (255,))
        for y in range(rows, 100):
            for x in range(12, 52):
                im.putpixel((x, y), body_rgb)
        im.save(sprite)
        return td, sprite

    def _analyse(self, sprite):
        mod = _load_sweep()
        old = mod.SPRITES
        try:
            mod.SPRITES = Path(sprite).parent
            return mod.analyse('synthetic', Path(sprite).name)
        finally:
            mod.SPRITES = old

    def test_low_saturation_light_flags(self):
        # burb's lightning: V = 212 > 205, colour spread S = 212 - 155 = 57 < 64.
        td, sprite = self._synthetic((155, 194, 212))
        try:
            row = self._analyse(sprite)
        finally:
            td.cleanup()
        self.assertEqual(row['light'], 1.0)
        self.assertEqual(row['warm'], 0.0)
        self.assertEqual(row['detach_gap'], 0)
        self.assertGreaterEqual(row['max_alpha'], 200)
        self.assertTrue(row['flag'], 'S < 64 light must set the flag')

    def test_saturated_light_does_not_use_the_colour_cut(self):
        # A cool saturated light (V = 255, S = 255 - 170 = 85 > 64) is not the
        # low-saturation lightning the cut targets and is not warm; with a solid
        # top and no gap nothing flags.
        td, sprite = self._synthetic((170, 220, 255), body_rgb=(120, 90, 60, 255))
        try:
            row = self._analyse(sprite)
        finally:
            td.cleanup()
        self.assertEqual(row['warm'], 0.0)
        self.assertEqual(row['detach_gap'], 0)
        self.assertGreaterEqual(row['max_alpha'], 200)
        self.assertFalse(row['flag'], 'a warm-but-not-light top must not flag')

    def test_docstring_points_at_the_r46_evidence(self):
        text = (ROOT / 'tools' / 'sweep_standee_tops.py').read_text()
        self.assertIn('evidence/token-standee-shape-20261004/', text)
        self.assertIn('solid top', text.lower())


if __name__ == '__main__':
    unittest.main()
