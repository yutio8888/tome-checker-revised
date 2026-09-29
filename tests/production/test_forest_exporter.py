"""Compile-and-run checks for tools/export_forest_terrain.c.

No model calls, no new or edited artwork: every master used here is a tiny
synthetic fixture built in-memory with Pillow. This only proves the exporter
mechanics (naming set, determinism, basic tile shape) on cheap fixture data;
the real reproduction-against-existing-tiles numbers are reported separately
in docs/g0-terrain-contract-20260927/EXPORTER.md, not re-derived by this test.
"""
import hashlib
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "tools" / "export_forest_terrain.c"

MAIN_MASTER_NAMES = [
    "floor-grass.png", "floor-road.png", "floor-flower.png",
    "prop-tree-oak.png", "prop-tree-pine.png", "prop-tree-willow.png", "prop-exit.png",
    "floor-deep.png", "floor-bog.png",
    "bank-deep-N.png", "bank-deep-E.png", "bank-deep-S.png", "bank-deep-W.png",
    "bank-bog-N.png", "bank-bog-E.png", "bank-bog-S.png", "bank-bog-W.png",
]
F1_MASTER_NAMES = [
    "prop-bog-tree-a.png", "prop-bog-tree-b.png",
    "prop-bog-misc-1.png", "prop-bog-misc-2.png", "prop-bog-misc-3.png",
]

EXPECTED_MAIN_NAMES = set()
for kind in ["grass", "road", "flower", "tree-oak", "tree-pine", "tree-willow", "exit"]:
    for parity in (0, 1):
        EXPECTED_MAIN_NAMES.add(f"{kind}{parity}.png")
for kind in ["deep", "bog"]:
    for mask in range(16):
        for parity in (0, 1):
            EXPECTED_MAIN_NAMES.add(f"{kind}{mask}-{parity}-0.png")

EXPECTED_F1_NAMES = set()
for style in ("a", "b"):
    for mask in range(16):
        for parity in (0, 1):
            EXPECTED_F1_NAMES.add(f"bog-tree-{style}{mask}-{parity}-0.png")
for variant in (1, 2, 3):
    for parity in (0, 1):
        EXPECTED_F1_NAMES.add(f"bog-misc{variant}-{parity}-0.png")

EXPECTED_HARDTREE_NAMES = {f"tree-hard{parity}.png" for parity in (0, 1)}
SNOW_MASTER_NAMES = ["floor-snow-ground.png", "prop-snow-tree-pine.png",
    "prop-snow-tree-elm.png", "prop-snow-exit-up.png",
    "prop-snow-exit-down.png", "prop-snow-exit-world.png"]
EXPECTED_SNOW_NAMES = {f"{kind}{parity}.png" for kind in
    ("snow-ground", "tree-pine", "tree-elm", "stairs-up", "stairs-down", "stairs-world")
    for parity in (0, 1)}


def make_fixture_masters(masters_dir: Path, names, size=16, seed_offset=0):
    """Tiny deterministic synthetic masters: solid-ish colour floors, and
    small off-centre opaque squares (with a transparent margin, satisfying
    the A1-style 'alpha touches 0' shape) standing in for props/banks."""
    masters_dir.mkdir(parents=True, exist_ok=True)
    for i, name in enumerate(names):
        n = i + seed_offset
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        px = img.load()
        is_floor = name.startswith("floor-")
        base = (40 + n * 7 % 120, 90 + n * 11 % 100, 40 + n * 5 % 80, 255)
        for y in range(size):
            for x in range(size):
                if is_floor:
                    px[x, y] = base
                else:
                    # a solid block in the middle, transparent margin around it
                    # (mirrors 'construct masters keep native alpha, corners 0')
                    if size // 4 <= x < size - size // 4 and size // 4 <= y < size - size // 4:
                        px[x, y] = base
                    else:
                        px[x, y] = (0, 0, 0, 0)
        img.save(masters_dir / name)


class ForestExporterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix="forest-exporter-test-")
        cls.binary = str(Path(cls.tmp) / "export_forest_terrain")
        compile_cmd = ["cc", "-O2", "-Wall", "-Wextra", str(SRC), "-o", cls.binary, "-lpng", "-lm"]
        result = subprocess.run(compile_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise unittest.SkipTest(
                f"cc/libpng unavailable in this environment, cannot compile exporter: {result.stderr[:2000]}"
            )
        cls.compile_stderr = result.stderr

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def setUp(self):
        self.work = Path(tempfile.mkdtemp(prefix="forest-exporter-run-", dir=self.tmp))
        self.masters = self.work / "masters"
        make_fixture_masters(self.masters, MAIN_MASTER_NAMES, size=16)
        self.f1_masters = self.work / "f1-masters"
        make_fixture_masters(self.f1_masters, F1_MASTER_NAMES, size=16, seed_offset=100)

    def run_exporter(self, out, review, f1_out=None):
        out.mkdir(parents=True, exist_ok=True)
        review.mkdir(parents=True, exist_ok=True)
        cmd = [self.binary, str(self.masters), str(out), str(review)]
        if f1_out is not None:
            f1_out.mkdir(parents=True, exist_ok=True)
            cmd += [str(self.f1_masters), str(f1_out)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        return result

    def test_compiles_clean(self):
        # No warnings from -Wall -Wextra: the exporter must stay simple enough
        # to review by inspection, same discipline as export_korpul_terrain.c.
        self.assertEqual(self.compile_stderr.strip(), "", msg=self.compile_stderr)

    def test_snow_family_exports_exact_parity_set(self):
        masters, out, review = (self.work / x for x in ("snow-masters", "snow-out", "snow-review"))
        make_fixture_masters(masters, SNOW_MASTER_NAMES, size=16)
        out.mkdir(); review.mkdir()
        result = subprocess.run([self.binary, "--snow", str(masters), str(out), str(review)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual({p.name for p in out.glob("*.png")}, EXPECTED_SNOW_NAMES)
        for name in EXPECTED_SNOW_NAMES:
            with Image.open(out / name) as image:
                self.assertEqual(image.size, (128, 128))
                self.assertEqual(image.getchannel("A").getextrema(), (255, 255))

    def test_main_naming_set_matches_current_runtime_contract(self):
        out, review = self.work / "out1", self.work / "review1"
        self.run_exporter(out, review)
        produced = {p.name for p in out.glob("*.png")}
        self.assertEqual(produced, EXPECTED_MAIN_NAMES)
        self.assertEqual(len(produced), 78, "must match the 78 in-use forest/water tiles")

    def test_f1_naming_set_matches_flooded_trollmire_identities(self):
        out, review, f1_out = self.work / "out2", self.work / "review2", self.work / "f1out2"
        self.run_exporter(out, review, f1_out=f1_out)
        # F1 output must never land in the main/data-gfx-shaped output dir.
        main_produced = {p.name for p in out.glob("*.png")}
        self.assertTrue(main_produced.isdisjoint(EXPECTED_F1_NAMES))
        f1_produced = {p.name for p in f1_out.glob("*.png")}
        self.assertEqual(f1_produced, EXPECTED_F1_NAMES)
        self.assertEqual(len(f1_produced), 70)

    def test_hardtree_is_optional_and_stays_out_when_its_master_is_absent(self):
        out, review, f1_out = self.work / "out2b", self.work / "review2b", self.work / "f1out2b"
        result = self.run_exporter(out, review, f1_out=f1_out)
        f1_produced = {p.name for p in f1_out.glob("*.png")}
        self.assertTrue(f1_produced.isdisjoint(EXPECTED_HARDTREE_NAMES))
        self.assertIn("prop-tree-hard.png not found", result.stdout)

    def test_hardtree_is_included_when_its_master_is_present(self):
        out, review, f1_out = self.work / "out2c", self.work / "review2c", self.work / "f1out2c"
        make_fixture_masters(self.f1_masters, ["prop-tree-hard.png"], size=16, seed_offset=200)
        self.run_exporter(out, review, f1_out=f1_out)
        f1_produced = {p.name for p in f1_out.glob("*.png")}
        self.assertEqual(f1_produced, EXPECTED_F1_NAMES | EXPECTED_HARDTREE_NAMES)
        for name in EXPECTED_HARDTREE_NAMES:
            with Image.open(f1_out / name) as im:
                im = im.convert("RGBA")
                self.assertEqual(im.size, (128, 128))
                self.assertEqual(im.getchannel("A").getextrema(), (255, 255))

    def test_all_tiles_are_128x128_rgba_fully_opaque(self):
        out, review = self.work / "out3", self.work / "review3"
        self.run_exporter(out, review)
        for p in out.glob("*.png"):
            with Image.open(p) as im:
                im = im.convert("RGBA")
                self.assertEqual(im.size, (128, 128), msg=str(p))
                alpha = im.getchannel("A")
                self.assertEqual(alpha.getextrema(), (255, 255), msg=str(p))

    def test_review_scales_present_for_every_tile(self):
        out, review = self.work / "out4", self.work / "review4"
        self.run_exporter(out, review)
        names = {p.name for p in out.glob("*.png")}
        for size in (48, 64, 96):
            scaled = {p.name for p in (review / str(size)).glob("*.png")}
            self.assertEqual(scaled, names, msg=f"missing/extra {size}px review tiles")
            for p in (review / str(size)).glob("*.png"):
                with Image.open(p) as im:
                    self.assertEqual(im.size, (size, size), msg=str(p))

    def test_deterministic_across_two_runs(self):
        out_a, review_a = self.work / "outA", self.work / "reviewA"
        out_b, review_b = self.work / "outB", self.work / "reviewB"
        self.run_exporter(out_a, review_a)
        self.run_exporter(out_b, review_b)
        names_a = sorted(p.name for p in out_a.glob("*.png"))
        names_b = sorted(p.name for p in out_b.glob("*.png"))
        self.assertEqual(names_a, names_b)
        for name in names_a:
            ha = hashlib.sha256((out_a / name).read_bytes()).hexdigest()
            hb = hashlib.sha256((out_b / name).read_bytes()).hexdigest()
            self.assertEqual(ha, hb, msg=f"non-deterministic output for {name}")

    def test_mask_bit_only_touches_its_own_edge(self):
        # A5 in miniature: toggling one mask bit on a tiny fixture must not
        # move pixels on the other three edges (corners excluded).
        out, review = self.work / "out5", self.work / "review5"
        self.run_exporter(out, review)
        margin = 2  # tiny analogue of the 128px M=12 corner exclusion
        with Image.open(out / "deep0-0-0.png") as a, Image.open(out / "deep1-0-0.png") as b:
            a = a.convert("RGBA"); b = b.convert("RGBA")
            pa, pb = a.load(), b.load()
            for side_pixels in [
                [(x, 126) for x in range(margin, 128 - margin)],   # S
                [(x, 127) for x in range(margin, 128 - margin)],
                [(126, y) for y in range(margin, 128 - margin)],   # E
                [(127, y) for y in range(margin, 128 - margin)],
                [(0, y) for y in range(margin, 128 - margin)],     # W
                [(1, y) for y in range(margin, 128 - margin)],
            ]:
                for x, y in side_pixels:
                    self.assertEqual(pa[x, y], pb[x, y], msg=f"deep0 vs deep1 diverged at ({x},{y})")


if __name__ == "__main__":
    unittest.main()
