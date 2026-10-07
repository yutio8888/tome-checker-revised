"""R48 conditional aura-moment gate: pure synthetic decision checks."""
import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
spec = importlib.util.spec_from_file_location(
    'aura_live', ROOT / 'tools/run_monster_live_validation.py')
live = importlib.util.module_from_spec(spec)
spec.loader.exec_module(live)


class AuraMomentGateTests(unittest.TestCase):
    def test_lopsided_and_not_flipped_fails(self):
        # Both directions are clearly lopsided (means +20 / +10 px) but the
        # signs do not differ, so the must-flip gate fails.
        gate = live.aura_moment_gate(200.0, 100.0, 10, 10)
        self.assertTrue(gate['lopsided'])
        self.assertEqual(gate['label'], 'flip')
        self.assertFalse(gate['passed'])

    def test_lopsided_and_flipped_passes(self):
        # Same lopsidedness, opposite signs: the gate is exercised and passes.
        gate = live.aura_moment_gate(200.0, -100.0, 10, 10)
        self.assertTrue(gate['lopsided'])
        self.assertEqual(gate['label'], 'flip')
        self.assertTrue(gate['passed'])

    def test_below_two_px_is_not_applicable(self):
        # One direction's per-pixel mean is below 2 px, so the silhouette is
        # not lopsided enough to judge: the gate records N/A and passes.
        gate = live.aura_moment_gate(15.0, 10.0, 10, 10)
        self.assertFalse(gate['lopsided'])
        self.assertEqual(gate['label'], 'N/A')
        self.assertTrue(gate['passed'])

    def test_threshold_is_inclusive_at_two_px(self):
        gate = live.aura_moment_gate(20.0, -20.0, 10, 10)
        self.assertTrue(gate['lopsided'])
        self.assertEqual(gate['label'], 'flip')

    def test_zero_count_is_not_applicable(self):
        gate = live.aura_moment_gate(0.0, 0.0, 0, 0)
        self.assertFalse(gate['lopsided'])
        self.assertEqual(gate['label'], 'N/A')
        self.assertTrue(gate['passed'])


if __name__ == '__main__':
    unittest.main()
