"""R53 measurement validity: preserve R52 brightness, never alter aura gates."""
import json
import hashlib
import math
import sys
import unittest
from pathlib import Path
import numpy as np
from PIL import Image
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
import run_monster_live_validation as live

class StandeeLightingTests(unittest.TestCase):
    def test_registered_reference_matches_saved_r52_pixels(self):
        ref = live.AURA_CONTRACT['LIGHTING_REFERENCE']
        path = ROOT / ref['source']
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), ref['source_sha256'])
        measured = float(np.asarray(Image.open(path).convert('RGB').crop(ref['source_crop_box'])).mean())
        self.assertEqual(measured, ref['mean_rgb_brightness'])
        self.assertTrue(live.lighting_validity([measured]*3)['valid'])

    def test_lighting_precondition_is_inclusive_and_requires_all_three(self):
        r = live.AURA_CONTRACT['LIGHTING_REFERENCE']['mean_rgb_brightness']
        self.assertTrue(live.lighting_validity([r*.9,r,r*1.1])['valid'])
        for values in ([r*.899,r,r], [r,r,r*1.101], [r]*2, [r,r,float('nan')],
                       [math.nextafter(r*.9, -math.inf),r,r],
                       [r,r,math.nextafter(r*1.1, math.inf)]):
            self.assertFalse(live.lighting_validity(values)['valid'])
        self.assertFalse(live.lighting_validity([r]*3, bare=False)['valid'])

    def test_original_r53_dim_floor_is_invalid_not_a_gate_failure(self):
        path = ROOT / 'evidence/token-standee-briagh-20261006/history/r53-uncontrolled-lighting/crops/standee-aura-bill-essence_of_the_dead-on-32-base-frame-1-crop.png'
        measured = float(np.asarray(Image.open(path).convert('RGB').crop((32,0,64,32))).mean())
        validity = live.lighting_validity([measured]*3)
        self.assertEqual(validity['status'], 'INVALID (lighting)')
        self.assertFalse(validity['valid'])
        self.assertEqual(live.AURA_HEIGHT_FRAMES, 15)
        self.assertEqual(live.AURA_CONTRACT['AURA_FLAME_ABOVE_TOP_FLOOR_CELLS'], .3)

    def test_fixture_restores_lighting_after_native_fov_and_retires_storm(self):
        import subprocess
        setup = r"""
package.preload['mod.class.CheckerFixture']=function() return {enabled=function() return true end} end
profile={};config={settings={tome={}}}
local cells={};local p={lite=0,x=25,y=26,EFF_ZONE_AURA_THUNDERSTORM=1,storm=true}
function p:hasEffect(id) return self.storm end
function p:removeEffect(id,force) assert(id==1 and force);self.storm=false end
function p:playerFOV() cells['25,25']=.2 end
local a={x=25,y=25};mb={byName=function() return a end}
local m={w=50,h=50,color_shown={.3,.3,.3,1},color_obscure={.18,.18,.18,.6},particles={{id=1},{id=2}},removed={}}
function m:setShown(...) self.color_shown={...} end
function m:setObscure(...) self.color_obscure={...} end
m.lites=function() end;m.remembers=function() end
function m:applyLite(x,y,v) cells[x..','..y]=v end
function m:redisplay() end
function m:removeParticleEmitter(ps) assert(type(ps)=='table');self.removed[#self.removed+1]=ps end
core={display={forceRedraw=function() end}}
local original_background=function() end
local storm_background=function() end
local level={map=m,level=1,entities={p,a},effects={'EFF_ZONE_AURA_THUNDERSTORM'},data={background=storm_background,thunderstorm_event_background=original_background}}
game={player=p,level=level,zone={thunderstorm_event_levels={[1]=true}}}
local control=function()
"""
        code = setup + live.STANDEE_LIGHTING_LUA.replace('NAME', "'actor'") + r"""
end
assert(control());p:playerFOV()
assert(cells['25,25']==1 and p.lite==3)
assert(m.color_shown[1]==1 and m.color_obscure[1]==.6)
assert(config.settings.tome.daynight==false and config.settings.tome.smooth_fov==false)
assert(not game.zone.thunderstorm_event_levels[1] and not p.storm)
assert(level.data.background==original_background and #level.effects==0)
assert(#m.removed==2 and #m._checker_removed_light_events==1)
local original=p._checker_original_measure_fov
assert(control());assert(p._checker_original_measure_fov==original)
p:playerFOV();assert(cells['25,25']==1 and #m._checker_removed_light_events==1)
"""
        result = subprocess.run(['luajit', '-'], input=code, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_aura_invalid_lighting_label_for_baseline_and_effect_frames(self):
        from copy import deepcopy
        good = {'baseline_validity': {'valid': True, 'lighting': {'valid': True},
                                      'lighting_frames': {'valid': True}}}
        self.assertEqual(live.aura_case_validity(good, good), 'VALID')
        for state in ('on', 'native'):
            for key in ('lighting', 'lighting_frames'):
                bad = deepcopy(good);bad['baseline_validity']['valid'] = False
                bad['baseline_validity'][key]['valid'] = False
                on, native = (bad, good) if state == 'on' else (good, bad)
                self.assertEqual(live.aura_case_validity(on, native), 'INVALID (lighting)')
        bad = deepcopy(good);bad['baseline_validity']['valid'] = False
        self.assertEqual(live.aura_case_validity(bad, good), 'INVALID')

    def test_effect_endpoints_use_same_reference_and_both_must_pass(self):
        r = live.AURA_CONTRACT['LIGHTING_REFERENCE']['mean_rgb_brightness']
        self.assertTrue(live.lighting_validity([r*.9,r*1.1], samples=2)['valid'])
        for values in ([r*.899,r], [r,r*1.101], [r], [r,r,float('nan')]):
            self.assertEqual(live.lighting_validity(values, samples=2)['status'], 'INVALID (lighting)')

    def test_dim_reference_is_pinned_and_does_not_replace_gate_reference(self):
        ref=live.AURA_CONTRACT['DIM_LIGHTING_REFERENCE'];path=ROOT/ref['source']
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), ref['source_sha256'])
        value=float(np.asarray(Image.open(path).convert('RGB').crop(ref['source_crop_box'])).mean())
        self.assertEqual(value,ref['mean_rgb_brightness']);self.assertAlmostEqual(value,21.126,places=3)
        self.assertTrue(live.lighting_validity([value]*3,reference=ref)['valid'])
        self.assertFalse(live.lighting_validity([value]*3)['valid'])
        self.assertTrue(ref['informative_only'])

    def test_informative_scene_cannot_change_any_existing_gate(self):
        import copy
        census=json.loads((ROOT/'evidence/token-standee-briagh-20261006/census.json').read_text())
        from unittest.mock import patch
        with patch.object(live,'OUT',ROOT/'evidence/token-standee-briagh-20261006'):
            first=live.verify_standee(census)
            extra=copy.deepcopy(census)
            extra['scenes']['standee-aura-dim-L1']={'lua_errors':1,'steps':[{'error':'diagnostic failure'}]}
            self.assertEqual(live.verify_standee(extra),first)
