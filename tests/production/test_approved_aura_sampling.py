"""Coordinator-approved R51/R52 sampling and placement contracts, no live launch."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
import run_monster_live_validation as live


class HeightSamplingTests(unittest.TestCase):
    def gate(self, below):
        # art row10, native height.5 => unchanged k=max(.3,.6*.5)=.3.
        on = [8]*below + [6]*(15-below)  # heights .2 and .4 cells
        return live.aura_height_gate(on, [5]*15, 10, 10, 10)

    def test_two_of_fifteen_below_k_pass(self):
        result = self.gate(2)
        self.assertTrue(result['pass'])
        self.assertEqual(result['k'], .3)

    def test_eight_of_fifteen_below_k_fail(self):
        self.assertFalse(self.gate(8)['pass'])

    def test_nine_missing_bands_and_six_tall_frames_fail(self):
        result = live.aura_height_gate([None]*9 + [6]*6, [5]*15, 10, 10, 10)
        self.assertFalse(result['pass'])
        self.assertEqual(result['on_cells'], 0.0)
        self.assertEqual(result['k'], .3)

    def test_two_missing_bands_and_thirteen_tall_frames_pass(self):
        result = live.aura_height_gate([None]*2 + [6]*13, [5]*15, 10, 10, 10)
        self.assertTrue(result['pass'])
        self.assertEqual(result['on_cells'], .4)

    def test_missing_native_bands_are_zero_height_too(self):
        result = live.aura_height_gate([6]*15, [None]*9 + [0]*6, 10, 10, 10)
        self.assertTrue(result['pass'])
        self.assertEqual(result['native_cells'], 0.0)
        self.assertEqual(result['k'], .3)

    def test_wrong_count_is_error_for_either_state(self):
        for count in (0, 3, 14, 16):
            for on, native in (([6]*count, [5]*15), ([6]*15, [5]*count)):
                with self.assertRaises(ValueError):
                    live.aura_height_gate(on, native, 10, 10, 10)

    def test_band_and_still_keep_three_frames_ratio_keeps_all_fifteen(self):
        # Exercise the real capture pipeline with frames4–15 changing every pixel.
        # Band/stillness remain unchanged; ratio must include later frames.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); black = root/'black.png'; white = root/'white.png'
            Image.new('RGB', (300, 300), 'black').save(black)
            Image.new('RGB', (300, 300), 'white').save(white)
            bridge = Mock()
            def lua(body):
                if 'vp={m.display_x' in body:
                    return {'vp': [0, 0, 300, 300]}
                if 'return mb.row(a)' in body:
                    return {'screen': [100, 100]}
                return True
            bridge.lua.side_effect = lua
            def shot(name, **kwargs):
                if '-base-' in name:
                    return black
                return black if int(name.rsplit('-', 1)[1]) <= 3 else white
            bridge.shot.side_effect = shot
            aura = {'mark': True, 'display_x': 0, 'display_y': -1, 'display_w': 1, 'display_h': 2}
            native = dict(aura, mark=False)
            with patch.multiple(live, OUT=root, CROPS=root/'crops'), \
                 patch.object(live.time, 'sleep'), \
                 patch.object(live, 'standee_clear_auras'), \
                 patch.object(live, 'standee_apply_aura', return_value={}), \
                 patch.object(live, 'standee_isolate_shader_auras', return_value=[]), \
                 patch.object(live, 'standee_remove_idle_particles', return_value={}), \
                 patch.object(live, 'standee_idle_particle_count', return_value=0), \
                 patch.object(live, 'standee_lighting_state', return_value={}), \
                 patch.object(live, 'standee_floor_measure', return_value={'valid': True}), \
                 patch.object(live, 'standee_aura_state', return_value={'aura': [aura, native]}), \
                 patch.object(live, 'standee_reach', return_value={'anchor_cells': 2.753, 'on_reach': 1.75, 'native_top_px': 0}), \
                 patch.object(live.Path, 'unlink'):
                records = live.standee_realaura(bridge, {}, 'test actor', tiles=(32,))
            self.assertEqual(len(records), 4)  # two effects × ON/NATIVE
            for rec in records:
                self.assertEqual(rec['whole_frames'], [0, 0, 0])
                self.assertEqual(len(rec['whole_ratio_frames']), 15)
                self.assertEqual(rec['whole_ratio_frames'][:3], [0, 0, 0])
                self.assertTrue(all(c > 0 for c in rec['whole_ratio_frames'][3:]))
                self.assertEqual(rec['ratio_frame_indices'], list(range(1, 16)))
                self.assertEqual(rec['flame_band_widths'], [0, 0, 0])
                self.assertEqual(rec['creature_move'], [0, 0])
                self.assertEqual(rec['self_diff'], [0, 0])
                self.assertEqual(len(rec['actor_screen']), 3)
                self.assertEqual(len(rec['flame_top_rows']), 15)
                self.assertEqual(len(rec['baseline_crops']), 3)
                self.assertTrue(rec['baseline_validity']['valid'])
                self.assertEqual(rec['endpoint_lighting']['frame_indices'], [1,15])
                self.assertTrue(rec['baseline_validity']['lighting_frames']['valid'])


class PlacementTests(unittest.TestCase):
    quad = (20, 20, 80, 160)

    def mask(self, box):
        mask = np.zeros((200, 100), dtype=bool)
        l, t, r, b = box; mask[t:b, l:r] = True
        return mask

    def test_two_pixels_down_fails(self):
        self.assertTrue(live.aura_mask_placement(self.mask((30, 30, 70, 160)), self.quad)['pass'])
        self.assertFalse(live.aura_mask_placement(self.mask((30, 32, 70, 162)), self.quad)['pass'])

    def test_old_disc_rows_48_to_144_fail(self):
        self.assertFalse(live.aura_mask_placement(self.mask((30, 48, 70, 144)), self.quad)['pass'])

    def test_two_pixels_above_quad_top_fails(self):
        self.assertFalse(live.aura_mask_placement(self.mask((30, 18, 70, 160)), self.quad)['pass'])

    def test_recorded_five_actors_both_directions_pass(self):
        folder = ROOT/'tests/production/fixtures/standee-facing-placement'
        rows = json.loads((folder/'cases.json').read_text())
        self.assertEqual({r['id'] for r in rows}, {'ogre-guard', 'heavy-bone-giant', 'corrupted-daelach', 'norgos-guardian', 'rantha'})
        self.assertEqual(len(rows), 10)
        for row in rows:
            mask = np.asarray(Image.open(folder/row['mask'])) > 0
            with self.subTest(actor=row['id'], direction=row['direction']):
                self.assertTrue(live.aura_mask_placement(mask, row['quad'])['pass'])


class RatioSamplingTests(unittest.TestCase):
    def test_median_of_all_fifteen_and_unchanged_normalisation(self):
        result = live.aura_ratio_gate([1]*3+[70]*12, [100]*15, 1)
        self.assertEqual(result['normalised'], .7)
        self.assertTrue(result['pass'])
        self.assertEqual(live.aura_ratio_gate([140]*15, [100]*15, 2)['normalised'], .7)
        self.assertFalse(live.aura_ratio_gate([59]*15, [100]*15, 1)['pass'])
        self.assertFalse(live.aura_ratio_gate([151]*15, [100]*15, 1)['pass'])

    def test_any_other_count_errors_for_either_state(self):
        for count in range(32):
            if count == 15:
                continue
            for on, native in (([70]*count, [100]*15), ([70]*15, [100]*count)):
                with self.subTest(count=count), self.assertRaises(ValueError):
                    live.aura_ratio_gate(on, native, 1)

    def test_missing_or_invalid_frame_is_never_dropped(self):
        for bad in (None, float('nan'), float('inf'), -1, '70'):
            for on, native in (([bad]+[70]*14, [100]*15), ([70]*15, [bad]+[100]*14)):
                with self.subTest(bad=bad), self.assertRaises(ValueError):
                    live.aura_ratio_gate(on, native, 1)


class MirrorOcclusionTests(unittest.TestCase):
    def exclusion(self):
        return live.mirror_exclusion((40, 40), [{'kind': 'rank-badge', 'box': [27, 5, 33, 15]}], (0, 0, 40, 40), 20)

    def test_symmetric_aura_fixed_occluder_has_no_negative_gain(self):
        aura = np.zeros((40, 40), dtype=bool); aura[5:30, 7:33] = True
        occluded = aura.copy(); occluded[5:15, 27:33] = False
        self.assertLess(live.aura_mirror_gain(occluded, occluded, 20), 0)
        excluded, report = self.exclusion()
        self.assertEqual(live.aura_mirror_gain(occluded & ~excluded, occluded & ~excluded, 20), 0)
        self.assertEqual(report['excluded_pixels'], 120)
        self.assertTrue(report['includes_mirror_images'])
        np.testing.assert_array_equal(excluded, live.mirror_mask_axis(excluded, 20))

    def test_unmirrored_lopsided_aura_with_occluder_still_fails(self):
        aura = np.zeros((40, 40), dtype=bool); aura[5:35, 3:18] = True
        excluded, _ = self.exclusion(); observed = aura & ~excluded
        gain = live.aura_mirror_gain(observed, observed, 20)
        self.assertLess(gain, 0)
        self.assertFalse(live.aura_mirror_sign_gate(gain, [gain]*3, .1, 1, True, True, True))

    def test_geometry_is_screen_relative_clipped_and_reported(self):
        mask, report = live.mirror_exclusion((20, 20), [{'kind': 'life-bar', 'box': [117.5, 202, 125, 206]}], (100, 200, 120, 220), 10)
        self.assertEqual(report['excluded_pixels'], 24)
        self.assertTrue(mask[2:6, :3].all())
        self.assertTrue(mask[2:6, 17:].all())


class MirrorCensusIntegrationTests(unittest.TestCase):
    def score(self, lopsided, unequal_margins=False):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            body = np.zeros((40, 40, 3), dtype=np.uint8); body[:, 5:12] = 255
            Image.fromarray(body).save(root/'left.png')
            Image.fromarray(body[:, ::-1]).save(root/'right.png')
            Image.new('RGB', (40, 40)).save(root/'off.png')
            aura = np.zeros((40, 40, 3), dtype=np.uint8)
            aura[5:35, 3:18 if lopsided else 33] = 255
            if not lopsided:
                aura[:, :7] = 0
            aura[5:15, 27:33] = 0  # screen-fixed badge, identical in both directions
            Image.fromarray(aura).save(root/'on.png')
            boxes = [{'kind': 'rank-badge', 'box': [27, 5, 33, 15]},
                     {'kind': 'life-bar', 'box': [17, 35, 20, 38]}]
            facing = []
            for mode in ('fixed', 'native'):
                for direction in ('left', 'right'):
                    facing.append({'mode': mode, 'direction': direction,
                                   'crop': 'right.png' if mode == 'native' and direction == 'right' else 'left.png',
                                   'region': [0, 0, 40, 40], 'creature': [0, 0, 40, 40],
                                   'own': [0, 20, 40, 40], 'upper': [0, 0, 40, 20],
                                   'state': {'body_flip': mode == 'native' and direction == 'left',
                                             'creature_bbox_centre': {'x': 20, 'y': 20},
                                             'mirror_occluder_boxes': boxes}})
            if unequal_margins:
                facing[-1]['own'] = [1, 20, 40, 40]
            fa = [{'direction': d, 'region': [0, 0, 40, 40], 'off': 'off.png', 'ons': ['on.png']*3,
                   'state': {'mirror_occluder_boxes': boxes, 'aura_quad': [0, 0, 40, 35]}}
                  for d in ('left', 'right')]
            checks, metrics = {}, {}
            with patch.object(live, 'OUT', root):
                live._verify_facing_scene({'steps': [{'facing': facing, 'facing_aura': fa,
                                          'facing_aura_state': {d: {'base_invis': True} for d in ('left', 'right')}}]},
                                          'test', checks, metrics)
            return checks, metrics

    def test_actual_native_mirror_path_asserts_centred_region(self):
        with self.assertRaisesRegex(AssertionError, 'unequal margins'):
            self.score(False, unequal_margins=True)

    def test_excluded_area_reaches_real_census_metrics(self):
        _, metrics = self.score(False)
        self.assertEqual(metrics['test-aura-asym-gain'], 0)
        self.assertEqual(metrics['test-aura-mirror-exclusion']['excluded_pixels'], 138)
        self.assertEqual(metrics['test-native-own-exclusion']['excluded_pixels'], 18)
        self.assertEqual(metrics['test-native-upper-exclusion']['excluded_pixels'], 120)
        self.assertTrue(metrics['test-aura-mirror-exclusion']['includes_mirror_images'])
        json.dumps(metrics)  # directly serialisable as the live census metrics

    def test_real_mirror_gate_rejects_unmirrored_lopsided_occluded_aura(self):
        checks, metrics = self.score(True)
        self.assertLess(metrics['test-aura-asym-gain'], 0)
        self.assertFalse(checks['test-aura-mirror'])


class StaticFacingSelectionTests(unittest.TestCase):
    def test_candidates_below_point_three_are_rejected(self):
        with self.assertRaises(ValueError):
            live.select_facing_subject([{'id': 'a', 'static_asymmetry': .299999}])
        self.assertEqual(live.select_facing_subject([{'id': 'a', 'static_asymmetry': .30}])['id'], 'a')

    def test_highest_new_actor_selected_from_shipped_alpha_eight(self):
        ids = list(live.R39_BATCH4_IDS) + ['norgos-guardian']
        rows = [live.static_aura_asymmetry(tid) for tid in ids]
        chosen = live.select_facing_subject([row for row in rows if row['id'] in live.R39_BATCH4_IDS])
        self.assertEqual(chosen['id'], 'onilug')
        expected = {'prox': .169427, 'bill': .128135, 'shax': .270993,
                    'onilug': .792349, 'chronolith-twin': .232444,
                    'chronolith-clone': .089608, 'norgos-guardian': .147844}
        for row in rows:
            mask = np.asarray(Image.open(ROOT/'data/gfx/tokens-layer/aura'/f"{row['id']}.png"))[:, :, 3] > 8
            # Independent continuous aura bbox centre; raster edge rounding
            # can shift the alpha bbox centre by half a pixel.
            bbox = json.loads((ROOT/'art/token-layers/geometry.json').read_text())[row['id']]['aura']
            axis = (bbox['left'] + bbox['right']) / 2
            self.assertAlmostEqual(row['axis'], axis, delta=1e-9)
            mirrored = np.zeros_like(mask)
            for x in range(mask.shape[1]):
                target = int(2 * axis - 1 - x)
                if 0 <= target < mask.shape[1]:
                    mirrored[:, target] = mask[:, x]
            independent = (mask ^ mirrored).sum() / mask.sum()
            self.assertEqual(row['alpha_threshold'], 8)
            self.assertAlmostEqual(row['static_asymmetry'], independent, delta=1e-12)
            self.assertAlmostEqual(row['static_asymmetry'], expected[row['id']], delta=1e-6)

    def test_low_asymmetry_pass_and_fail_are_both_informative(self):
        for outcome in (True, False):
            self.assertEqual(live.facing_run_status(.148, {'mirror': outcome}), 'INFORMATIVE')
        self.assertEqual(live.facing_run_status(.30, {'mirror': True}), 'PASS')
        self.assertEqual(live.facing_run_status(.30, {'mirror': False}), 'FAIL')

    def test_native_mirror_rejects_unequal_crop_margins(self):
        frame = {'region': [0, 0, 144, 192]}
        for region in ([48, 96, 96, 144], [48, 0, 96, 96]):
            live.assert_centred_mirror_region(frame, region)
            with self.assertRaisesRegex(AssertionError, 'unequal margins'):
                live.assert_centred_mirror_region(frame, [47, region[1], 96, region[3]])
