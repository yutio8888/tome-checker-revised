"""R49 geometry and flame-band checks, without starting the game."""
import importlib.util
import sys
import unittest
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
spec = importlib.util.spec_from_file_location('aura_live', ROOT / 'tools/run_monster_live_validation.py')
live = importlib.util.module_from_spec(spec)
spec.loader.exec_module(live)


class AuraRegionTests(unittest.TestCase):
    def test_known_live_quads(self):
        import json
        census = json.loads((ROOT / 'evidence/token-standee-tallaura-20261004/census.json').read_text())
        actors = set()
        for step in census['scenes']['standee-aura-L1']['steps']:
            for c in step.get('aura_captures', []):
                if c['state'] != 'on':
                    continue
                actors.add(c['actor'])
                q = next(a for a in c['snap']['aura'] if a.get('mark'))
                sx, sy = c['actor_screen'][0][:2]
                t = c['tile']
                region = live.aura_score_region(sx, sy, t, q)
                self.assertEqual(region[3], sy)
                self.assertLessEqual(region[1], sy - t)
                self.assertLessEqual(region[1], sy + q['display_y'] * t)
                self.assertLessEqual(region[0], sx - t / 2)
                self.assertGreaterEqual(region[2], sx + 1.5 * t)
                self.assertLessEqual(region[0], sx + q['display_x'] * t)
                self.assertGreaterEqual(region[2], sx + (q['display_x'] + q['display_w']) * t)
        self.assertEqual(actors, {'heavy bone giant', 'snow giant', 'ogre guard'})

    def test_native_snap_quad_matches_default(self):
        # S1 item 5: the shared score region is built from the default native
        # 1x2 quad (0,-1,1,2), hard-coded because the ON readback only has the
        # standee aura. Assert the live census native snapshots agree, so a
        # future native-sprite geometry change cannot silently fall outside
        # the scored region. The engine leaves display_x/display_w at their
        # 0/1-cell defaults (absent from the snap) and records y=-1/h=2.
        import json
        census = json.loads(
            (ROOT / 'evidence/token-standee-auraregion-20261004/census.json').read_text())
        captures = 0
        for step in census['scenes']['standee-aura-L1']['steps']:
            for c in step.get('aura_captures', []):
                if c['state'] != 'native':
                    continue
                captures += 1
                quads = [a for a in c['snap']['aura'] if not a.get('mark')]
                self.assertTrue(quads, (c['actor'], c['tile']))
                for q in quads:
                    normalized = (q.get('display_x', 0), q.get('display_y', -1),
                                  q.get('display_w', 1), q.get('display_h', 2))
                    self.assertEqual(normalized, (0, -1, 1, 2),
                                     (c['actor'], c['effect'], c['tile']))
        self.assertEqual(captures, 18)
        # The default native quad and the read-back (0,-1,1,2) score the same
        # region for an ON quad, so the assumption and the snapshot agree.
        on = dict(display_x=-.0385, display_y=-1.400846, display_w=1.077, display_h=2.154)
        native = dict(display_x=0, display_y=-1, display_w=1, display_h=2)
        self.assertEqual(live.aura_score_region(100, 200, 32, on, native),
                         live.aura_score_region(100, 200, 32, on))

    def test_tall_32_known_region(self):
        q = dict(display_x=-.0385, display_y=-1.400846, display_w=1.077, display_h=2.154)
        self.assertEqual(live.aura_score_region(100, 200, 32, q), (84, 155, 148, 200))

    def test_native_higher_and_wide_quad(self):
        q = dict(display_x=-.8, display_y=-.8, display_w=2.6, display_h=2.6)
        self.assertEqual(live.aura_score_region(100, 200, 48, q), (61, 152, 187, 200))

    def test_spikes_and_scattered_pixels_do_not_set_top(self):
        mask = np.zeros((6, 10), dtype=bool)
        mask[0, 2] = True
        mask[1, [1, 3, 5]] = True
        mask[3, 2:5] = True
        self.assertEqual(live.flame_band_widths(mask), [1, 1, 0, 3, 0, 0])
        from unittest.mock import patch
        with patch.object(live, '_diff_mask', return_value=mask):
            self.assertEqual(live._diff_top_row(None, None, None), 3)
        with patch.object(live, '_diff_mask', return_value=mask[:3]):
            self.assertIsNone(live._diff_top_row(None, None, None))


class AuraSceneValidityTests(unittest.TestCase):
    def test_changes_in_union_are_valid(self):
        mask = np.zeros((8, 10), dtype=bool)
        mask[1:5, 1:5] = True
        mask[3:7, 4:9] = True
        self.assertEqual(live.outside_quad_pixels(mask, [(1, 1, 5, 5), (4, 3, 9, 7)]), 0)

    def test_changes_outside_union_are_counted(self):
        mask = np.zeros((8, 10), dtype=bool)
        mask[0, 2] = mask[4, 0] = mask[7, 8] = True
        mask[2, 2] = True
        self.assertEqual(live.outside_quad_pixels(mask, [(1, 1, 5, 5), (4, 3, 9, 7)]), 3)

    def test_fractional_quads_include_intersected_edge_texels(self):
        mask = np.zeros((5, 5), dtype=bool)
        mask[0:3, 0:3] = True
        self.assertEqual(live.outside_quad_pixels(mask, [(-.5, -.5, 2.1, 2.1)]), 0)
        mask[3, 2] = True
        self.assertEqual(live.outside_quad_pixels(mask, [(-.5, -.5, 2.1, 2.1)]), 1)

    def test_empty_and_offscreen_quads_cannot_hide_changes(self):
        mask = np.eye(4, dtype=bool)
        self.assertEqual(live.outside_quad_pixels(mask, []), 4)
        self.assertEqual(live.outside_quad_pixels(mask, [(10, 10, 12, 12)]), 4)


class ApprovedAuraRulesTests(unittest.TestCase):
    def test_stable_clean_baseline(self):
        frame = np.zeros((8, 10, 3), dtype=np.uint8)
        self.assertTrue(live.cleaned_baseline_validity([frame]*3, [0]*3)['valid'])
        self.assertFalse(live.cleaned_baseline_validity([frame]*2, [0]*2)['valid'])
        self.assertFalse(live.cleaned_baseline_validity([frame]*3, [0, 1, 0])['valid'])

    def test_idle_motion_anywhere_in_crop_is_invalid(self):
        a = np.zeros((8, 10, 3), dtype=np.uint8)
        b = a.copy(); b[7, 9] = [13, 0, 0]
        result = live.cleaned_baseline_validity([a, b, a], [0]*3)
        self.assertFalse(result['valid'])
        self.assertEqual(result['drift_pixels'], [1, 1])

    def test_existing_threshold_12_is_unchanged(self):
        a = np.zeros((8, 10, 3), dtype=np.uint8)
        b = a.copy(); b[0, 0] = [4, 4, 4]
        self.assertTrue(live.cleaned_baseline_validity([a, b, a], [0]*3)['valid'])
        b[0, 0] = [5, 4, 4]
        self.assertFalse(live.cleaned_baseline_validity([a, b, a], [0]*3)['valid'])

    def test_essence_height_is_only_judged_at_64(self):
        for tile in (32, 48, 64):
            self.assertEqual(live.aura_height_gate_required('essence_of_the_dead', tile), tile == 64)
            self.assertTrue(live.aura_height_gate_required('body_of_fire', tile))

    def test_shader_scene_isolation_uses_native_lifecycle_only(self):
        import subprocess
        setup = r"""
local shader={name='shader buff',activate=function(a) a:addShaderAura('x') end}
local ordinary={name='ordinary buff',activate=function(a) a:unrelated() end}
local a={name='actor',uid=1,shader_auras={skin={},wake={}},tmp={skin=true,ordinary=true},sustain_talents={wake=true,ordinary=true}}
function a:getEffectFromId(id) return id=='skin' and shader or ordinary end
function a:getTalentFromId(id) return id=='wake' and shader or ordinary end
function a:isTalentActive(id) return self.sustain_talents[id] end
function a:removeEffect(id) assert(id=='skin');self.tmp[id]=nil;self.shader_auras.skin=nil;self.effect_calls=(self.effect_calls or 0)+1 end
function a:forceUseTalent(id,opts) assert(id=='wake' and opts.ignore_cd and opts.ignore_energy);self.sustain_talents[id]=nil;self.shader_auras.wake=nil;self.sustain_calls=(self.sustain_calls or 0)+1 end
game={level={entities={a,{name='clean',uid=2}}}}
"""
        checks = r"""
assert(a.effect_calls==1 and a.sustain_calls==1)
assert(a.tmp.ordinary and a.sustain_talents.ordinary)
assert(next(a.shader_auras)==nil)
assert(#got==2 and #got[1].before==2 and #got[1].after==0)
assert(#got[1].removed==2 and got[1].removed[1].kind=='effect' and got[1].removed[2].kind=='sustain')
assert(#got[2].removed==0)
"""
        script = setup + '\nlocal got=(function()\n' + live.STANDEE_ISOLATE_SHADER_AURAS_LUA + '\nend)()\n' + checks
        result = subprocess.run(['luajit', '-'], input=script, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
