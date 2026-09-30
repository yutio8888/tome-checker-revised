"""S12 hazard family: the recorded lava master, complete tiles and runtime
manifest, the hazard value hierarchy (hazard lava far below the board stone
floor and walls, distinct from the blocking molten pit and the harmless lava
floor), the flush seam only on open edges, the stone kerb only on open edges
of the unchanged board deep-water surface, and parity."""
import hashlib
import json
import re
import unittest
from pathlib import Path
from PIL import Image, ImageStat

ROOT = Path(__file__).resolve().parents[2]
SUITE = ROOT / 'art/terrain-hazard-s12'
RUNTIME = ROOT / 'data/gfx/refined/hazard'
REFINED = ROOT / 'data/gfx/refined'
PACK = ROOT / 'art/production/handoffs/terrain-hazard-s12-v1/hazard-lava-floor'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def lum(path, box=None):
    im = Image.open(path).convert('L')
    return ImageStat.Stat(im.crop(box) if box else im).mean[0]


def hot(path):
    im = Image.open(path).convert('RGB')
    r, g, b = (list(c.getdata()) for c in im.split())
    return sum(1 for i in range(len(r)) if r[i] > 200 and r[i] - b[i] > 120) / len(r)


def px(path, xy):
    return Image.open(path).convert('RGB').getpixel(xy)


class HazardS12ExporterTests(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads((SUITE / 'export-manifest.json').read_text())

    def test_master_is_the_recorded_generation(self):
        receipt = json.loads((PACK / 'receipts/attempt-1.json').read_text())
        master = ROOT / receipt['saved_output_path']
        self.assertEqual(master, SUITE / 'masters/hazard-lava-floor-v1.png')
        self.assertEqual(digest(master), receipt['sha256'])
        self.assertEqual(self.manifest['source_sha256']['art/terrain-hazard-s12/masters/hazard-lava-floor-v1.png'], receipt['sha256'])
        call = json.loads((PACK / 'imagegen-calls/call-1/call.json').read_text())
        self.assertEqual(call['codex_model'], 'gpt-6.1-sol')
        self.assertTrue(call['codex_ephemeral'])
        self.assertEqual(call['outcome'], 'recorded')
        self.assertEqual(len(list((PACK / 'imagegen-calls').glob('call-*'))), 1)
        self.assertEqual(self.manifest['imagegen_calls'], 1)
        # The water is derived from the pinned board deep surface and Kor'Pul floor master.
        for rel in ('art/terrain-forest-v1/masters-derived/floor-deep.png', 'art/terrain-korpul-v1/masters/floor-a-v2.png'):
            self.assertEqual(self.manifest['source_sha256'][rel], digest(ROOT / rel))

    def test_complete_tiles_bytes_and_runtime_manifest(self):
        expected = sorted([f'lava-{v}-{m}-{p}.png' for v in 'abc' for m in range(16) for p in (0, 1)] +
                          [f'deep-{m}-{p}.png' for m in range(16) for p in (0, 1)])
        self.assertEqual(sorted(self.manifest['runtime_sha256']), expected)
        self.assertEqual(sorted(p.name for p in RUNTIME.iterdir()), expected)
        for name, sha in self.manifest['runtime_sha256'].items():
            self.assertEqual(digest(RUNTIME / name), sha, name)
            im = Image.open(RUNTIME / name)
            self.assertEqual(im.size, (128, 128))
            self.assertEqual(im.getchannel('A').getextrema(), (255, 255), name)
        lua = (ROOT / 'data/terrain-hazard-manifest.lua').read_text()
        self.assertIn('ready=true', lua)
        self.assertIn(f"revision='{self.manifest['revision']}'", lua)
        listed = re.findall(r"\['checker-revised\+refined/hazard/([\w-]+\.png)'\]=true", lua)
        self.assertEqual(sorted(listed), expected)

    def test_hazard_value_hierarchy(self):
        floor = lum(REFINED / 'korpul/floor-a-0-0.png')
        hard = min(lum(REFINED / f'korpul/hardwall-{m}-0.png') for m in (0, 15))
        dark = min(lum(REFINED / f'korpul-dark/wall-{m}-0.png') for m in (0, 15))
        for v in 'abc':
            lava = lum(RUNTIME / f'lava-{v}-15-0.png')
            with self.subTest(variant=v):
                self.assertLess(lava, floor * .5)      # far below the walkable stone floor
                self.assertLess(lava, hard * .6)       # and below the hard wall
                self.assertLess(lava, dark * .65)      # and the S8 dark brick
                # Glowing seams: hot pixels (r > 200, r - b > 120) that no floor or
                # wall has, but far fewer than the blocking molten pit (26%).
                self.assertGreater(hot(RUNTIME / f'lava-{v}-15-0.png'), .03)
                self.assertLess(hot(RUNTIME / f'lava-{v}-15-0.png'), hot(REFINED / 'burnt/lava-15-0.png') / 2.5)
                self.assertLess(lava, lum(REFINED / 'burnt/lava-15-0.png') - 20)
        for name in ('korpul/floor-a-0-0', 'korpul/hardwall-15-0', 'korpul-dark/wall-15-0', 'daikara/lava-floor0', 'deep15-0-0'):
            self.assertEqual(hot(REFINED / f'{name}.png'), 0, name)

    def test_seam_only_on_open_edges(self):
        for v in 'abc':
            closed = RUNTIME / f'lava-{v}-15-0.png'
            opened = RUNTIME / f'lava-{v}-0-0.png'
            for box in ((2, 1, 126, 3), (125, 2, 127, 126), (2, 125, 126, 127), (1, 2, 3, 126)):
                self.assertGreater(lum(opened, box), lum(closed, box) + 60, (v, box))
            # Interior untouched by the seam.
            self.assertAlmostEqual(lum(opened, (20, 20, 108, 108)), lum(closed, (20, 20, 108, 108)), delta=.5)
        # Mask bit N=1 E=2 S=4 W=8: only the open sides glow.
        m5 = RUNTIME / 'lava-a-5-0.png'   # N and S joined: E and W open
        self.assertGreater(lum(m5, (125, 20, 127, 108)), lum(m5, (20, 1, 108, 3)) + 60)

    def test_stone_kerb_on_unchanged_deep_surface(self):
        surface = Image.open(ROOT / 'art/terrain-forest-v1/masters-derived/floor-deep.png').convert('RGB')
        inner = Image.open(RUNTIME / 'deep-15-0.png').convert('RGB')
        self.assertEqual(inner.crop((1, 1, 127, 127)).tobytes(), surface.crop((1, 1, 127, 127)).tobytes())
        closed, opened = RUNTIME / 'deep-15-0.png', RUNTIME / 'deep-0-0.png'
        for box in ((12, 0, 116, 8), (120, 12, 128, 116), (12, 120, 116, 128), (0, 12, 8, 116)):
            self.assertGreater(lum(opened, box), lum(closed, box) + 50, box)   # pale stone, not water
        r, g, b = px(opened, (64, 4))
        self.assertTrue(r >= b and g >= b, (r, g, b))                          # warm stone, not teal water
        self.assertLess(lum(opened, (15, 15, 113, 113)), lum(REFINED / 'korpul/floor-a-0-0.png') * .6)

    def test_parity(self):
        for name in ('lava-b-15', 'lava-c-0', 'deep-15', 'deep-6'):
            a, b = lum(RUNTIME / f'{name}-0.png'), lum(RUNTIME / f'{name}-1.png')
            self.assertAlmostEqual(b / a, .90, delta=.012, msg=name)


if __name__ == '__main__':
    unittest.main()
