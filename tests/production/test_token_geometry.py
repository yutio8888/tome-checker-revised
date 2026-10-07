"""Geometry contract: the flat token is a .92-cell disc in a .035-cell faction
ring (outer edge .955 cell), and the procedural masks stay in step with it.

Static only. The in-game check is a separate task. These tests replace the old
shield-style geometry floor so a future change cannot pin the removed health or
shield lanes back in.
"""
import math
import re
import subprocess
import unittest
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
STYLE = ROOT / 'overload/mod/class/CheckerTokenStyle.lua'
PREPARE = ROOT / 'tools/prepare_runtime_art.py'
TOKENS = ROOT / 'data/gfx/tokens'

TOKEN_DIAMETER = .92
RING_LANE = .035
ART_OCCUPANCY = .86
OUTER = TOKEN_DIAMETER + RING_LANE

DELETED_MASKS = (
    '_health-band.png', '_shield-track.png', '_shield-band.png', '_shield-ticks.png',
    '_relation-edge-enemy.png', '_relation-edge-neutral.png',
    '_relation-edge-friend.png', '_relation-edge-player.png',
)


def lua(expr: str) -> str:
    out = subprocess.run(['luajit', '-e', expr], cwd=ROOT, capture_output=True, text=True, check=True)
    return out.stdout.strip()


def style_constant(name: str) -> float:
    return float(lua(f"local S=dofile('{STYLE.relative_to(ROOT)}') io.write(tostring(S.{name}))"))


def mask_radii(name: str) -> tuple[float, float]:
    image = Image.open(TOKENS / name).convert('RGBA')
    size = image.size[0]
    pixels = image.load()
    radii = []
    for y in range(size):
        for x in range(size):
            if pixels[x, y][3] > 127:
                radii.append(math.hypot(x + .5 - size / 2, y + .5 - size / 2) / size)
    return min(radii), max(radii)


class DiscGeometryTests(unittest.TestCase):
    def test_style_constants(self):
        self.assertEqual(style_constant('token_diameter'), TOKEN_DIAMETER)
        self.assertEqual(style_constant('ring_lane'), RING_LANE)
        self.assertEqual(style_constant('art_occupancy'), ART_OCCUPANCY)

    def test_geometry_is_disc_plus_ring_at_every_cell(self):
        script = (
            "local S=dofile('overload/mod/class/CheckerTokenStyle.lua') "
            "for _,tile in ipairs{48,64,96} do for sc=1,5 do "
            "local g=S.geometry(0,0,tile,S.scale(sc,tile)) "
            "io.write(string.format('%.9f\\n',g.d/tile)) end end")
        values = [float(v) for v in lua(script).splitlines()]
        self.assertEqual(len(values), 15)
        for value in values:
            self.assertAlmostEqual(value, OUTER, places=9)

    def test_exporter_occupancy_unchanged(self):
        text = (ROOT / 'tools/export_token.c').read_text()
        match = re.search(r'target_occupancy.*?([0-9.]+)\}', text)
        self.assertIsNotNone(match)
        self.assertAlmostEqual(float(match.group(1)), ART_OCCUPANCY, places=6)


class MaskContractTests(unittest.TestCase):
    def test_prepare_runtime_art_radius_matches_contract(self):
        text = PREPARE.read_text()
        digits = re.search(r"mask\('_relation-'\+relation,\[\(\.([0-9]+),\.5\)\]", text).group(1)
        inner = float('.' + digits)
        self.assertAlmostEqual(inner, (TOKEN_DIAMETER - RING_LANE) / 2 / OUTER, places=4)
        self.assertNotIn("mask('_health-band'", text)
        self.assertNotIn("mask('_shield", text)
        self.assertNotIn("mask('_relation-edge", text)
        self.assertIn("mask('_player-inner'", text)

    def test_ring_masks_are_on_the_outer_canvas(self):
        expected_inner = (TOKEN_DIAMETER - RING_LANE) / 2 / OUTER
        for kind in ('enemy', 'neutral', 'friend', 'player'):
            low, high = mask_radii(f'_relation-{kind}.png')
            self.assertAlmostEqual(low, expected_inner, places=2, msg=kind)
            self.assertAlmostEqual(high, .5, places=2, msg=kind)
        low, high = mask_radii('_relation-back.png')
        self.assertLess(low, expected_inner)
        self.assertAlmostEqual(high, .5, places=2)
        low, high = mask_radii('_player-inner.png')
        self.assertGreater(low, .43)
        self.assertLess(high, expected_inner)

    def test_removed_masks_are_not_shipped(self):
        for name in DELETED_MASKS:
            self.assertFalse((TOKENS / name).exists(), name)


if __name__ == '__main__':
    unittest.main()
