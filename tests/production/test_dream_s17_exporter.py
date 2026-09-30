"""S17 dream family: the two recorded masters (the cloud call recorded by the
wrapper; the void call's single tool output recorded through art_tasks.py
record after the wrapper's provenance step rejected an unreported path), the
complete tiles and runtime manifest, the value hierarchy (pale walkable cloud
far above the dark void), the cloud rim only on open edges, and parity."""
import hashlib
import json
import re
import unittest
from pathlib import Path
from PIL import Image, ImageStat

ROOT = Path(__file__).resolve().parents[2]
SUITE = ROOT / 'art/terrain-dream-s17'
RUNTIME = ROOT / 'data/gfx/refined/dream'
HANDOFFS = ROOT / 'art/production/handoffs'
CLOUD_PACK = HANDOFFS / 'terrain-dream-s17-v1/dream-cloud-floor'
VOID_PACK = HANDOFFS / 'terrain-dream-s17-void-v1/dream-void'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def lum(path, box=None):
    im = Image.open(path).convert('L')
    return ImageStat.Stat(im.crop(box) if box else im).mean[0]


class DreamS17ExporterTests(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads((SUITE / 'export-manifest.json').read_text())

    def test_masters_are_the_recorded_generations(self):
        for pack, name in ((CLOUD_PACK, 'dream-cloud-floor-v1.png'), (VOID_PACK, 'dream-void-v1.png')):
            receipt = json.loads((pack / 'receipts/attempt-1.json').read_text())
            master = ROOT / receipt['saved_output_path']
            self.assertEqual(master, SUITE / 'masters' / name)
            self.assertEqual(digest(master), receipt['sha256'])
            self.assertEqual(self.manifest['source_sha256'][f'art/terrain-dream-s17/masters/{name}'], receipt['sha256'])
            calls = sorted((pack / 'imagegen-calls').glob('call-*'))
            self.assertEqual(len(calls), 1)
            call = json.loads((calls[0] / 'call.json').read_text())
            self.assertEqual(call['codex_model'], 'gpt-6.1-sol')
            self.assertTrue(call['codex_ephemeral'])
        self.assertEqual(json.loads((CLOUD_PACK / 'imagegen-calls/call-1/call.json').read_text())['outcome'], 'recorded')
        void_call = json.loads((VOID_PACK / 'imagegen-calls/call-1/call.json').read_text())
        self.assertEqual(void_call['outcome'], 'provenance-rejected')
        # The recorded void master is the one file the tool wrote during that call.
        new = void_call['provenance']['new_files_during_call']
        self.assertEqual(len(new), 1)
        receipt = json.loads((VOID_PACK / 'receipts/attempt-1.json').read_text())
        self.assertIn(Path(new[0]).name, json.dumps(receipt))
        self.assertEqual(self.manifest['imagegen_calls'], 2)

    def test_complete_tiles_bytes_and_runtime_manifest(self):
        expected = sorted([f'cloud-{v}-{m}-{p}.png' for v in 'abc' for m in range(16) for p in (0, 1)] +
                          [f'void-{v}-{p}.png' for v in 'ab' for p in (0, 1)])
        self.assertEqual(sorted(p.name for p in RUNTIME.glob('*.png')), expected)
        self.assertEqual(sorted(self.manifest['runtime_sha256']), expected)
        for name, sha in self.manifest['runtime_sha256'].items():
            self.assertEqual(digest(RUNTIME / name), sha, name)
            with Image.open(RUNTIME / name) as im:
                self.assertEqual((im.size, im.mode), ((128, 128), 'RGB'), name)
        lua = (ROOT / 'data/terrain-dream-manifest.lua').read_text()
        self.assertIn('ready=true', lua)
        entries = re.findall(r"\['checker-revised\+refined/dream/([\w-]+\.png)'\]=true", lua)
        self.assertEqual(sorted(entries), expected)
        self.assertIn(self.manifest['revision'], lua)

    def test_value_hierarchy_and_parity(self):
        for v in 'abc':
            interior = lum(RUNTIME / f'cloud-{v}-15-0.png')
            self.assertGreater(interior, 165)
            self.assertLess(interior, 215)
            self.assertLess(lum(RUNTIME / f'cloud-{v}-15-1.png'), interior)
        for v in 'ab':
            void = lum(RUNTIME / f'void-{v}-0.png')
            self.assertLess(void, 40)
            self.assertLess(lum(RUNTIME / f'void-{v}-1.png'), void)
        # Walkable cloud and impassable void stay far apart in grayscale.
        self.assertGreater(lum(RUNTIME / 'cloud-a-0-0.png') - lum(RUNTIME / 'void-a-0.png'), 120)

    def test_rim_only_on_open_edges(self):
        south = (8, 116, 120, 126)
        north = (8, 1, 120, 5)
        closed = lum(RUNTIME / 'cloud-a-15-0.png', south)
        # Mask 11 = N+E+W cloud, south open: a darker side band on the south edge only.
        self.assertLess(lum(RUNTIME / 'cloud-a-11-0.png', south), closed - 20)
        self.assertAlmostEqual(lum(RUNTIME / 'cloud-a-11-0.png', north), lum(RUNTIME / 'cloud-a-15-0.png', north), delta=1)
        # The interior of an edge tile is the interior tile.
        box = (24, 24, 104, 104)
        self.assertAlmostEqual(lum(RUNTIME / 'cloud-b-0-0.png', box), lum(RUNTIME / 'cloud-b-15-0.png', box), delta=1)


if __name__ == '__main__':
    unittest.main()
