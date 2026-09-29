"""S8 (V2/V7) darker wall sets: complete tiles and manifests, byte identity with
the export record, unchanged mask/edge geometry (door changes only inside the
jamb rectangles), and the floor-light / wall-dark relation in grayscale."""
import hashlib
import json
import re
import unittest
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw, ImageOps, ImageStat

ROOT = Path(__file__).resolve().parents[2]
GFX = ROOT / 'data/gfx/refined'
SUITE = ROOT / 'art/terrain-korpul-dark-s8'
KINDS = ('wall', 'door-closed-horizontal', 'door-closed-vertical', 'door-open-horizontal', 'door-open-vertical')
JAMBS = {'horizontal': ((0, 84, 20, 124), (108, 84, 128, 124)), 'vertical': ((4, 0, 44, 20), (4, 108, 44, 128))}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def lum(path):
    return ImageStat.Stat(Image.open(path).convert('L').resize((64, 64), Image.Resampling.LANCZOS)).mean[0]


class DarkWallExporterTests(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads((SUITE / 'export-manifest.json').read_text())

    def test_complete_sets_and_bytes(self):
        korpul = {f'{k}-{m}-{p}.png' for k in KINDS for m in range(16) for p in (0, 1)}
        scorch = {f'wall-{m}-{p}.png' for m in range(16) for p in (0, 1)}
        self.assertEqual({p.name for p in (GFX / 'korpul-dark').glob('*.png')}, korpul)
        self.assertEqual({p.name for p in (GFX / 'scorch-dark').glob('*.png')}, scorch)
        self.assertEqual(set(self.manifest['files']), {'korpul-dark/' + n for n in korpul} | {'scorch-dark/' + n for n in scorch})
        self.assertEqual(self.manifest['imagegen_calls'], 0)
        for rel, sha in self.manifest['files'].items():
            with self.subTest(rel=rel):
                self.assertEqual(digest(GFX / rel), sha)
                self.assertEqual(Image.open(GFX / rel).size, (128, 128))
        for rel, sha in self.manifest['sources'].items():
            with self.subTest(source=rel):
                self.assertEqual(digest(ROOT / rel), sha)

    def test_runtime_manifests(self):
        for name, folder, n in (('terrain-korpul-dark-manifest.lua', 'korpul-dark', 160),
                                ('terrain-scorch-dark-manifest.lua', 'scorch-dark', 32)):
            text = (ROOT / 'data' / name).read_text()
            files = set(re.findall(r"\['checker-revised\+refined/(" + folder + r"/[\w-]+\.png)'\]=true", text))
            self.assertEqual(len(files), n)
            self.assertEqual(files, {k for k in self.manifest['files'] if k.startswith(folder + '/')})

    def test_same_geometry(self):
        # Walls: the same brick layout, only darker (per-channel scale).
        for m in range(16):
            for p in (0, 1):
                a = Image.open(GFX / f'korpul/wall-{m}-{p}.png').convert('RGB')
                b = Image.open(GFX / f'korpul-dark/wall-{m}-{p}.png').convert('RGB')
                ga, gb = (ImageOps.grayscale(i) for i in (a, b))
                ratio = ImageStat.Stat(gb).mean[0] / ImageStat.Stat(ga).mean[0]
                self.assertTrue(.55 < ratio < .66, (m, p, ratio))
                # Edge structure: dark/light pattern correlates pixel for pixel.
                ea = ga.point(lambda v: 255 if v > 90 else 0)
                eb = gb.point(lambda v: 255 if v > round(90 * ratio) else 0)
                self.assertLess(ImageStat.Stat(ImageChops.difference(ea, eb)).mean[0], 255 * .03, (m, p))
        # Doors: leaf and floor pixels identical, change only in jamb rectangles.
        for kind in KINDS[1:]:
            orient = kind.rsplit('-', 1)[1]
            allowed = Image.new('L', (128, 128), 0)
            for box in JAMBS[orient]:
                ImageDraw.Draw(allowed).rectangle((box[0], box[1], box[2] - 1, box[3] - 1), fill=255)
            for m in range(16):
                for p in (0, 1):
                    d = ImageChops.difference(Image.open(GFX / f'korpul/{kind}-{m}-{p}.png').convert('RGBA'),
                                              Image.open(GFX / f'korpul-dark/{kind}-{m}-{p}.png').convert('RGBA')).convert('L')
                    outside = ImageChops.multiply(d.point(lambda v: 255 if v else 0), ImageOps.invert(allowed))
                    self.assertIsNone(outside.getbbox(), (kind, m, p))
        # Scorch: same masks and faces, darker.
        for m in range(16):
            a = ImageOps.grayscale(Image.open(GFX / f'scorch/wall-{m}-0.png'))
            b = ImageOps.grayscale(Image.open(GFX / f'scorch-dark/wall-{m}-0.png'))
            self.assertLess(ImageStat.Stat(b).mean[0], ImageStat.Stat(a).mean[0] * .52)

    def test_floor_light_wall_dark(self):
        floor = min(lum(GFX / f'korpul/floor-{k}-0-{p}.png') for k in 'ab' for p in (0, 1))
        grass = min(lum(GFX / f'grass{p}.png') for p in (0, 1))
        walls = [lum(GFX / f'korpul-dark/wall-{m}-{p}.png') for m in range(16) for p in (0, 1)]
        self.assertGreater((floor - max(walls)) / floor, .18)
        self.assertLess(max(walls), grass)
        lava = min(lum(GFX / f'daikara/lava-floor{p}.png') for p in (0, 1))
        rock = [lum(GFX / f'scorch-dark/wall-{m}-0.png') for m in range(16)]
        self.assertLess(sorted(rock)[len(rock) // 2], lava)


if __name__ == '__main__':
    unittest.main()
