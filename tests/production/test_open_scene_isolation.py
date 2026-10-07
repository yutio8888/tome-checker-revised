"""The exact-zero open fallback comparison must see a stable whole scene."""
import inspect
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock, patch
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'tools'))
import run_monster_live_validation as live


class OpenSceneIsolationTests(unittest.TestCase):
    def run_capture(self, fail=False):
        events = []
        bridge = Mock()
        bridge.lua.side_effect = lambda code: events.append(('lua', code))
        entry = {}
        def capture(*args, **kwargs):
            events.append(('capture', args[2], args[3], kwargs))
            if fail:
                raise RuntimeError('capture failed')
        with patch.object(live, 'standee_isolate_shader_auras',
                          side_effect=lambda b: events.append(('auras',)) or [{'before': ['fire'], 'after': []}]), \
             patch.object(live, 'standee_remove_idle_particles',
                          side_effect=lambda b, n: events.append(('particles',)) or {'total': 2}), \
             patch.object(live, 'standee_idle_particle_count', return_value=0), \
             patch.object(live, 'standee_off_on', side_effect=capture), \
             patch.object(live, 'standee_per_actor', side_effect=lambda *a, **k: events.append(('per_actor',))):
            if fail:
                with self.assertRaisesRegex(RuntimeError, 'capture failed'):
                    live.standee_open_scene(bridge, entry, (16, 32, 48, 64))
            else:
                live.standee_open_scene(bridge, entry, (16, 32, 48, 64))
        return events, entry

    def test_all_cleanup_and_pause_precede_unchanged_whole_crop_capture(self):
        events, entry = self.run_capture()
        self.assertEqual([e[0] for e in events],
                         ['lua', 'auras', 'particles', 'capture', 'per_actor', 'lua'])
        self.assertIn('pauseAnims(true)', events[0][1])
        self.assertEqual(events[3][2], (16, 32, 48, 64))
        self.assertEqual(events[3][3], {'native': True, 'up': 2, 'down': 1, 'span': 2})
        self.assertEqual(entry['scene_isolation']['particle_removals']['total'], 2)
        self.assertEqual(entry['scene_isolation']['residual_particles'], 0)
        self.assertIn('pauseAnims(false)', events[-1][1])

    def test_realaura_and_facing_remain_unpaused(self):
        for scene in (live.standee_realaura, live.standee_facing):
            with self.subTest(scene=scene.__name__):
                source = inspect.getsource(scene)
                self.assertNotRegex(source, r'pauseAnims\s*\(\s*true\s*\)')
                self.assertIn('pauseAnims(false)', source)

    def test_capture_failure_always_restores_animation(self):
        events, _ = self.run_capture(fail=True)
        self.assertIn('pauseAnims(false)', events[-1][1])
        self.assertNotIn('per_actor', [e[0] for e in events])


class CrowdFootprintTests(unittest.TestCase):
    def test_repaint_checks_both_outer_cells(self):
        self.assertEqual(live.standee_crowd_block_size(live.STANDEE_REPAINT), (7, 4))
        self.assertEqual(live.standee_crowd_block_size(live.STANDEE_CROWD), (5, 4))
        bridge = Mock()
        bridge.lua.return_value = None
        self.assertIsNone(live.standee_place_crowd(bridge, live.STANDEE_REPAINT))
        self.assertIn('mb.freeBlock(p.x,p.y,7,4)', bridge.lua.call_args[0][0])

    def test_asymmetric_vertical_ends_are_both_preflighted(self):
        self.assertEqual(live.standee_crowd_block_size([(0, 2, 'standee', 0)]), (5, 5))
        self.assertEqual(live.standee_crowd_block_size([(0, -3, 'standee', 0)]), (5, 6))


if __name__ == '__main__':
    unittest.main()
