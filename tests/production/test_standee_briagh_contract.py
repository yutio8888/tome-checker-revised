"""R53 coverage: accepted identity, unchanged fallback floor and facing decision."""
import importlib.util
import sys
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
spec = importlib.util.spec_from_file_location('briagh_live', ROOT / 'tools/run_monster_live_validation.py')
live = importlib.util.module_from_spec(spec)
spec.loader.exec_module(live)


class BriaghContractTests(unittest.TestCase):
    def test_identity_aura_crowd_and_flat_coverage(self):
        self.assertEqual(live.R39_STANDS[59], ('Briagh, Great Sand Wyrm', '/data/zones/briagh-lair/npcs.lua', 'BRIAGH', 'briagh'))
        self.assertIn(('Briagh, Great Sand Wyrm', 59), live.R39_AURA_ACTORS)
        self.assertEqual({live.STANDEE_GROUPS[g][i][3] for _, _, g, i in live.STANDEE_BRIAGH_CROWD}, set(live.R39_BATCH3_IDS[:7]) | {'briagh'})
        self.assertIn('briagh', {live.STANDEE_GROUPS[g][i][3] for _, _, g, i in live.STANDEE_FLAT})

    def test_no_new_eligible_facing_subject(self):
        row = live.static_aura_asymmetry('briagh')
        self.assertAlmostEqual(row['static_asymmetry'], 3330 / 12951, places=12)
        with self.assertRaises(ValueError):
            live.select_facing_subject([row])
        self.assertEqual(live.facing_run_status(row['static_asymmetry'], {'raw': True}), 'INFORMATIVE')
        self.assertEqual(live.facing_run_status(row['static_asymmetry'], {'raw': False}), 'INFORMATIVE')

    def test_authoritative_forge_capture_follows_main(self):
        names = [row[0] for row in live.SCENES_STANDEE]
        self.assertLess(names.index('standee-aura-L1'), names.index('standee-aura-forge-L1'),
                        'Shared Forge crop names must end with the authoritative dedicated capture')
