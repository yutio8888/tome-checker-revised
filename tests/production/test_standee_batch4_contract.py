"""Final optional standees: exact native identity and live scene coverage."""
import importlib.util
import sys
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
spec = importlib.util.spec_from_file_location('batch4_live', ROOT / 'tools/run_monster_live_validation.py')
live = importlib.util.module_from_spec(spec)
spec.loader.exec_module(live)


class Batch4ContractTests(unittest.TestCase):
    def test_exact_native_identity_routes(self):
        expected = {
            'prox': ('Prox the Mighty', '/data/zones/trollmire/npcs.lua', 'TROLL_PROX'),
            'bill': ('Bill the Stone Troll', '/data/zones/trollmire/npcs.lua', 'TROLL_BILL'),
            'shax': ('Shax the Slimy', '/data/zones/trollmire/npcs.lua', 'TROLL_SHAX'),
            'onilug': ('onilug', '/data/general/npcs/minor-demon.lua', None),
            'chronolith-twin': ('Chronolith Twin', '/data/zones/temporal-rift/npcs.lua', 'CHRONOLITH_TWIN'),
            'chronolith-clone': ('Chronolith Clone', '/data/zones/temporal-rift/npcs.lua', 'CHRONOLITH_CLONE'),
        }
        self.assertEqual(set(live.R39_BATCH4_IDS), set(expected))
        self.assertEqual({tid: (name, src, define) for name, src, define, tid in live.R39_STANDS
                          if tid in expected}, expected)

    def test_trio_crowd_and_all_six_flat_fallback(self):
        crowd = {live.STANDEE_GROUPS[g][i][3] for _, _, g, i in live.STANDEE_BATCH4_CROWD}
        self.assertEqual(crowd, {'prox', 'bill', 'shax'})
        positions = {(x, y) for x, y, _, _ in live.STANDEE_BATCH4_CROWD}
        self.assertEqual(positions, {(-1, -1), (0, -1), (1, -1)})
        flat = {live.STANDEE_GROUPS[g][i][3] for _, _, g, i in live.STANDEE_FLAT}
        self.assertTrue(set(live.R39_BATCH4_IDS) <= flat)

    def test_bill_aura_retained_and_facing_subject_pre_registered(self):
        name, index = next(row for row in live.R39_AURA_ACTORS if row[0] == 'Bill the Stone Troll')
        self.assertEqual(live.R39_STANDS[index][0], name)
        self.assertEqual(live.R39_STANDS[index][3], 'bill')
        scenes = {s[0]: s[-1][-1] for s in live.SCENES_STANDEE}
        self.assertEqual(scenes['standee-facing-bill-L1'], ('standee_grid', 'facing-bill'))
        self.assertEqual(live.select_facing_subject([live.static_aura_asymmetry(tid) for tid in live.R39_BATCH4_IDS])['id'], 'onilug')
        self.assertEqual(scenes['standee-facing-batch4-L1'], ('standee_grid', 'facing-batch4'))
        self.assertEqual(scenes['standee-batch4-L1'], ('standee_grid', 'batch4'))

    def test_live_body_readback_excludes_staff(self):
        import inspect
        for function in (live.standee_state, live.standee_actor_metrics):
            source = inspect.getsource(function)
            self.assertIn('box.body_top or box.top', source)
            self.assertIn('drawn=bh*math.min(cap/bh', source)
