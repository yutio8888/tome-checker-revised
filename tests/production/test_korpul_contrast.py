"""Kor'Pul / Kor'Pul-dark floor-vs-wall readability (2026-10-01 hue finish).
Additional floor only; every existing value gate stays as it was."""
import importlib.util
from pathlib import Path
import unittest
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
GFX = ROOT / 'data/gfx/refined'
HERE = ROOT / 'art/terrain-contrast-v1'
FROZEN = HERE / 'frozen-inputs'
spec = importlib.util.spec_from_file_location('contrast_export', HERE / 'export.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)


def lab(path):
    return m.lab(Image.open(path))


def gray(path):
    return np.asarray(Image.open(path).convert('L')).astype(float)


class KorpulContrastTests(unittest.TestCase):
    def test_floor_wall_delta_e(self):
        for p in (0, 1):
            floor = lab(GFX / f'korpul/floor-a-0-{p}.png')
            for wall in ('korpul/wall-15', 'korpul-dark/wall-15', 'korpul/hardwall-15', 'maze/old-wall-15'):
                with self.subTest(wall=wall, parity=p):
                    self.assertGreaterEqual(float(np.linalg.norm(floor - lab(GFX / f'{wall}-{p}.png'))), 25)
            # Warm walkable stone against cool brick, and the dark brick keeps a value step.
            self.assertGreaterEqual(floor[2] - lab(GFX / f'korpul/wall-15-{p}.png')[2], 20, p)
            self.assertGreaterEqual(floor[0] - lab(GFX / f'korpul-dark/wall-15-{p}.png')[0], 12, p)

    def test_luma_preserved(self):
        # The finish moves hue only, so every luminance gate sees the baseline values.
        for fam in ('korpul', 'korpul-dark'):
            for src in sorted((FROZEN / fam).glob('*.png')):
                with self.subTest(name=f'{fam}/{src.name}'):
                    d = np.abs(gray(GFX / fam / src.name) - gray(src))
                    self.assertLessEqual(d.mean(), .6)
                    self.assertLessEqual(np.percentile(d, 99), 2)

    def test_dark_brick_and_unfinished_tiles_unchanged(self):
        for path in (FROZEN / 'korpul-dark').glob('wall-*.png'):
            self.assertEqual(path.read_bytes(), (GFX / 'korpul-dark' / path.name).read_bytes(), path.name)

    def test_door_floor_matches_floor_tile(self):
        # Door cells show exactly the finished floor where the baseline showed floor.
        for fam in ('korpul', 'korpul-dark'):
            for door in sorted((FROZEN / fam).glob('door-*.png')):
                p = door.stem[-1]
                base = np.asarray(Image.open(FROZEN / 'korpul' / f'floor-a-0-{p}.png').convert('RGBA'))
                was_floor = (np.asarray(Image.open(door).convert('RGBA')) == base).all(-1)
                now = np.asarray(Image.open(GFX / fam / door.name).convert('RGBA'))
                floor = np.asarray(Image.open(GFX / 'korpul' / f'floor-a-0-{p}.png').convert('RGBA'))
                with self.subTest(name=f'{fam}/{door.name}'):
                    self.assertGreater(was_floor.mean(), .6)
                    self.assertTrue((now[was_floor] == floor[was_floor]).all())


if __name__ == '__main__':
    unittest.main()
