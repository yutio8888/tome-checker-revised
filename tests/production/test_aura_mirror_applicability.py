"""User-approved SNR applicability; the existing gain margin is unchanged."""
import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
spec = importlib.util.spec_from_file_location(
    'aura_mirror_live', ROOT / 'tools/run_monster_live_validation.py')
live = importlib.util.module_from_spec(spec)
spec.loader.exec_module(live)


class AuraMirrorApplicabilityTests(unittest.TestCase):
    def test_norgos_is_not_applicable(self):
        self.assertFalse(live.aura_mirror_applicable(582, .233, 1067, False))

    def test_prior_pass_remains_applicable(self):
        self.assertTrue(live.aura_mirror_applicable(1310, .156, 2023, False))

    def test_zero_noise_is_applicable(self):
        self.assertTrue(live.aura_mirror_applicable(582, 0, 1067, False))

    def test_lopsided_overrides_low_snr(self):
        self.assertTrue(live.aura_mirror_applicable(582, .233, 1067, True))

    def test_boundary_is_inclusive(self):
        self.assertTrue(live.aura_mirror_applicable(300, .1, 1000, False))
        self.assertFalse(live.aura_mirror_applicable(299, .1, 1000, False))

    def test_na_requires_positive_aggregate_and_every_frame(self):
        def decision(gain, frames):
            return live.aura_mirror_sign_gate(gain, frames, .8, .6, True, True, True)
        self.assertTrue(decision(.124, [.092, .100, .044]))
        for gain, frames in [(-.01, [.1, .1, .1]), (0, [.1, .1, .1]),
                             (.1, [.1, -.01, .1]), (.1, [.1, 0, .1]), (.1, [])]:
            with self.subTest(gain=gain, frames=frames):
                self.assertFalse(decision(gain, frames))

    def test_zero_asym_is_not_applicable_and_zero_gain_fails(self):
        self.assertFalse(live.aura_mirror_applicable(0, .233, 1067, False))
        self.assertFalse(live.aura_mirror_applicable(0, 0, 1067, False))
        self.assertFalse(live.aura_mirror_sign_gate(0, [.1, .1, .1], .8, .6,
                                                  True, True, True))

    def test_na_requires_better_iou_and_each_existing_sanity_check(self):
        for mirrored, own, upper, aligned in [(.6, True, True, True),
                                             (.8, False, True, True),
                                             (.8, True, False, True),
                                             (.8, True, True, False)]:
            with self.subTest(mirrored=mirrored, own=own, upper=upper, aligned=aligned):
                self.assertFalse(live.aura_mirror_sign_gate(.1, [.1, .1, .1],
                                                          mirrored, .6, own, upper, aligned))


if __name__ == '__main__':
    unittest.main()
