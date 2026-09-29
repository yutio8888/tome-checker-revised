"""Production-tool safety checks; no model calls, no new or edited artwork."""
import copy
import hashlib
import json
import shutil
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tools'))
import art_tasks as art
import audit_completion as audit

SAMPLE = ROOT/'art/production/batches/shared-rodents-pilot-v1.json'
PLAYER_SAMPLE = ROOT/'art/production/batches/player-tokens-v1-human-elf.json'


class HandoffTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=ROOT/'art/production', prefix='test-')
        self.dir = Path(self.tmp.name)
        self.manifest = json.loads(SAMPLE.read_text())
        # Test the production tool against a fixed pre-integration registry.
        # These historic sample identities are now covered in the live catalog.
        patch = mock.patch.object(art, 'current_catalog', return_value={'giant brown rat':'brown-rat'})
        patch.start()
        self.addCleanup(patch.stop)

    def tearDown(self):
        self.tmp.cleanup()

    def write_manifest(self):
        path = self.dir/'manifest.json'
        path.write_text(json.dumps(self.manifest))
        return path

    def ready(self):
        self.manifest['assets'] = self.manifest['assets'][:1]
        asset = self.manifest['assets'][0]
        asset['gate'] = 'ready'
        asset['gate_reason'] = 'Synthetic gate for tool unit test only; not production approval.'
        asset['render_evidence'] = [dict(path=asset['sources'][0]['path'], sha256=asset['sources'][0]['sha256'])]
        out = self.dir/'ready'
        art.prepare(self.write_manifest(), out)
        return out/asset['asset_id']

    def test_hold_has_no_callable_request_and_cannot_record(self):
        out = self.dir/'hold'
        report = art.prepare(self.write_manifest(), out)
        self.assertEqual((report['hold'], report['ready'], report['image_calls']), (2,0,0))
        self.assertEqual(list(out.rglob('imagegen-request.json')), [])
        with self.assertRaisesRegex(ValueError, 'hold task'):
            art.record(out/self.manifest['assets'][0]['asset_id'], SAMPLE, SAMPLE, 1)

    def test_ready_requires_evidence(self):
        self.manifest['assets'][0]['gate'] = 'ready'
        with self.assertRaisesRegex(ValueError, 'resolved actor/grid evidence'):
            art.validate(self.manifest)

    def test_pin_changes_and_anchor_drift_fail(self):
        original = copy.deepcopy(self.manifest)
        self.manifest['assets'][0]['references'][0]['sha256'] = '0'*64
        with self.assertRaisesRegex(ValueError, 'changed input'):
            art.validate(self.manifest)
        original['assets'][0]['sources'][0]['line'] = 1
        with self.assertRaisesRegex(ValueError, 'anchor changed'):
            art.validate(original)

    def test_duplicates_existing_tokens_and_single_axis_fail(self):
        original = copy.deepcopy(self.manifest)
        self.manifest['assets'].append(copy.deepcopy(self.manifest['assets'][0]))
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            art.validate(self.manifest)
        original['assets'][0]['native_name'] = 'giant brown rat'
        with self.assertRaisesRegex(ValueError, 'already mapped'):
            art.validate(original)
        original['assets'][0]['native_name'] = 'giant white rat'
        original['assets'][0]['contrast_dimensions'] = ['hue']
        with self.assertRaisesRegex(ValueError, 'two design dimensions'):
            art.validate(original)

    def test_refinement_brief_is_the_only_declared_way_past_the_duplicate_check(self):
        """Repainting a mapped token needs a declared, pinned refinement brief.

        The duplicate check itself is unchanged: without the declaration an
        already mapped identity is still rejected, and the declaration is not a
        third attempt -- it must pin how the previous batch actually ended.
        """
        asset = self.manifest['assets'][0]
        asset['native_name'] = 'giant brown rat'
        with self.assertRaisesRegex(ValueError, 'already mapped'):
            art.validate(self.manifest)
        evidence = dict(asset['sources'][0])
        reason = ('Design direction changed after the recorded failure: the previous brief kept '
                  'the four-footed profile, and this one replaces it with an upright pose.')
        asset['refinement'] = dict(supersedes='brown-rat', previous_batch='unit-test-batch',
                                   design_change_reason=reason,
                                   evidence=[dict(path=evidence['path'], sha256=evidence['sha256'])])
        art.validate(self.manifest)
        broken = copy.deepcopy(self.manifest)
        broken['assets'][0]['refinement']['supersedes'] = 'some-other-token'
        with self.assertRaisesRegex(ValueError, 'must supersede'):
            art.validate(broken)
        broken = copy.deepcopy(self.manifest)
        broken['assets'][0]['refinement']['design_change_reason'] = 'try again'
        with self.assertRaisesRegex(ValueError, 'design-direction change'):
            art.validate(broken)
        broken = copy.deepcopy(self.manifest)
        broken['assets'][0]['refinement']['evidence'][0]['sha256'] = '0'*64
        with self.assertRaisesRegex(ValueError, 'changed input'):
            art.validate(broken)
        broken = copy.deepcopy(self.manifest)
        broken['assets'][0]['refinement'].pop('evidence')
        with self.assertRaisesRegex(ValueError, 'refinement needs exactly'):
            art.validate(broken)
        broken = copy.deepcopy(self.manifest)
        broken['assets'][0]['native_name'] = 'giant white rat'
        with self.assertRaisesRegex(ValueError, 'not mapped'):
            art.validate(broken)

    def test_cannot_overwrite_or_escape_output_tree(self):
        manifest = self.write_manifest()
        out = self.dir/'once'
        art.prepare(manifest, out)
        before = (out/'batch.json').read_bytes()
        with self.assertRaisesRegex(ValueError, 'output exists'):
            art.prepare(manifest, out)
        self.assertEqual(before, (out/'batch.json').read_bytes())
        with self.assertRaisesRegex(ValueError, 'escapes permitted tree'):
            art.prepare(manifest, Path('/tmp/not-an-art-handoff'))

    def test_terrain_contract_is_required_and_template_is_complete(self):
        self.manifest['assets'] = self.manifest['assets'][:1]
        asset = self.manifest['assets'][0]
        asset.update(kind='terrain-floor', native_name='GRASS', asset_id='grass-contract-test')
        workspace = ROOT.parents[2]
        path = workspace/'game/modules/tome/data/general/grids/forest.lua'
        anchor = 'define_as = "GRASS"'
        line = next(i for i,s in enumerate(path.read_text().splitlines(),1) if anchor in s)
        asset['sources'] = [dict(path=str(path.relative_to(workspace)), sha256=art.digest(path), line=line, anchor=anchor)]
        reference = ROOT/'art/terrain-korpul-v1/masters/floor-a-v2.png'
        asset['references'] = [dict(path=str(reference.relative_to(workspace)), sha256=art.digest(reference), role='style', note='Material reference for schema test only.')]
        asset['prompt_fields'] = dict(subject='Grass printed ground.', contrast='Low-contrast ground.',
            palette='Muted green.', composition='Full bleed square.', mechanics='Use native GRASS rules.')
        with self.assertRaisesRegex(ValueError, 'separate movement'):
            art.validate(self.manifest)
        asset['grid_contract'] = dict(movement='native passability', sight='native sight',
            danger='native hazard', interaction='native callback', export='full square material')
        result = art.prepare(self.write_manifest(), self.dir/'terrain')
        self.assertEqual(result['hold'], 1)
        with self.assertRaisesRegex(ValueError, 'must be opaque'):
            art.inspect_png(art.pinned(json.loads(SAMPLE.read_text())['assets'][0]['references'][0]), 'terrain-floor')

    def test_record_and_repair_preserve_actual_prompts_and_budget(self):
        pack = self.ready()
        # Copy an existing approved master solely as test data. No generation.
        source = art.pinned(self.manifest['assets'][0]['references'][0])
        saved = self.dir/'mock-master-v1.png'
        shutil.copyfile(source, saved)
        receipt = art.record(pack, source, saved, 1)
        self.assertFalse(receipt['accepted'])
        self.assertEqual(receipt['sha256'], art.digest(source))
        self.assertEqual(receipt['runtime_review'], 'pending')
        with self.assertRaisesRegex(ValueError, 'sequential'):
            art.record(pack, source, saved, 1)
        review = self.dir/'repair-review.json'
        review.write_text(json.dumps(dict(review_scale=64, observed_failure='Synthetic test failure.',
            required_change='Synthetic test correction.', invariants='Camera and base.')))
        art.repair(pack, review)
        request = json.loads((pack/'repair/imagegen-request.json').read_text())
        self.assertEqual(request['referenced_image_paths'][0], str(saved))
        self.assertIn('Synthetic test correction.', request['prompt'])
        saved2 = self.dir/'mock-master-v2.png'
        shutil.copyfile(source, saved2)
        second = art.record(pack, source, saved2, 2)
        self.assertNotEqual(receipt['prompt_sha256'], second['prompt_sha256'])
        self.assertIn('Synthetic test correction.', second['full_prompt'])
        with self.assertRaisesRegex(ValueError, 'budget exhausted'):
            art.repair(pack, review)
        with self.assertRaisesRegex(ValueError, 'budget exceeded'):
            art.record(pack, source, saved2, 3)

    def test_record_rejects_modified_copy(self):
        pack = self.ready()
        source = art.pinned(self.manifest['assets'][0]['references'][0])
        saved = self.dir/'not-the-original.png'
        saved.write_bytes(b'not a PNG')
        with self.assertRaisesRegex(ValueError, 'identical bytes'):
            art.record(pack, source, saved, 1)

    def test_modified_prompt_cannot_get_receipt(self):
        pack = self.ready()
        (pack/'prompt.txt').write_text('untracked replacement')
        with self.assertRaisesRegex(ValueError, 'prompt changed'):
            art.record(pack, SAMPLE, SAMPLE, 1)


class PlayerKindTests(unittest.TestCase):
    """`kind: "player"` is checked against the player family registry, never the
    monster catalog: a player body family is not a native creature name, and a
    monster token must not satisfy (or block) a player family by accident.
    """

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=ROOT/'art/production', prefix='test-player-')
        self.dir = Path(self.tmp.name)
        self.manifest = json.loads(PLAYER_SAMPLE.read_text())
        patch = mock.patch.object(art, 'current_player_registry', return_value={})
        patch.start()
        self.addCleanup(patch.stop)

    def tearDown(self):
        self.tmp.cleanup()

    def write_manifest(self):
        path = self.dir/'manifest.json'
        path.write_text(json.dumps(self.manifest))
        return path

    def test_real_batch_validates_and_prepares_all_ready(self):
        out = self.dir/'out'
        report = art.prepare(self.write_manifest(), out)
        self.assertEqual(report, {'assets': 4, 'ready': 4, 'hold': 0, 'output': str(out), 'image_calls': 0})
        for asset in self.manifest['assets']:
            self.assertTrue((out/asset['asset_id']/'imagegen-request.json').is_file())

    def test_asset_id_must_match_family(self):
        self.manifest['assets'][0]['asset_id'] = 'player-wrong-id'
        with self.assertRaisesRegex(ValueError, 'player asset_id must be'):
            art.validate(self.manifest)

    def test_family_must_be_a_known_player_body_family(self):
        asset = self.manifest['assets'][0]
        asset['native_name'] = 'human_neuter'
        asset['asset_id'] = art.player_token_id('human_neuter')
        with self.assertRaisesRegex(ValueError, 'unknown player body family'):
            art.validate(self.manifest)

    def test_sources_must_pin_both_descriptor_and_doll(self):
        asset = self.manifest['assets'][0]
        only_doll = [s for s in asset['sources'] if 'line' not in s and 'anchor' not in s]
        only_descriptor = [s for s in asset['sources'] if 'line' in s or 'anchor' in s]
        self.assertTrue(only_doll and only_descriptor)
        no_doll = copy.deepcopy(self.manifest)
        no_doll['assets'][0]['sources'] = only_descriptor
        with self.assertRaisesRegex(ValueError, 'native paper-doll base image'):
            art.validate(no_doll)
        no_descriptor = copy.deepcopy(self.manifest)
        no_descriptor['assets'][0]['sources'] = only_doll
        with self.assertRaisesRegex(ValueError, 'birth descriptor line'):
            art.validate(no_descriptor)

    def test_image_source_outside_own_doll_folder_is_rejected(self):
        asset = self.manifest['assets'][0]
        wrong_family_doll = ROOT.parents[2]/'game/modules/tome/data/gfx/shockbolt/player/elf_male/base_01.png'
        asset['sources'] = [s for s in asset['sources'] if 'line' in s or 'anchor' in s]
        asset['sources'].append({'path': str(wrong_family_doll.relative_to(ROOT.parents[2])),
                                  'sha256': art.digest(wrong_family_doll)})
        with self.assertRaisesRegex(ValueError, 'base doll PNG under'):
            art.validate(self.manifest)

    def test_player_family_checked_against_player_registry_not_monster_catalog(self):
        # A monster happens to already be mapped to the same string as a player
        # family. It must not block (or silently satisfy) the player asset.
        with mock.patch.object(art, 'current_catalog', return_value={'human_male': 'some-monster-id'}):
            art.validate(self.manifest)  # must NOT raise "already mapped"
        # Once the *player* registry (not the monster catalog) already ships this
        # family, a bare re-run is rejected exactly like the monster duplicate check.
        with mock.patch.object(art, 'current_player_registry',
                               return_value={'human_male': 'player-human-male'}):
            with self.assertRaisesRegex(ValueError, 'already mapped'):
                art.validate(self.manifest)

    def test_player_kind_still_requires_two_contrast_dimensions(self):
        self.manifest['assets'][0]['contrast_dimensions'] = ['hue']
        with self.assertRaisesRegex(ValueError, 'two design dimensions'):
            art.validate(self.manifest)


class CoverageTests(unittest.TestCase):
    def test_reconciliation_counts_each_identity_once(self):
        rows, families, summary, zones, grids = audit.build()
        self.assertEqual(len(rows), len({r['native_name'] for r in rows}))
        self.assertEqual(sum(r['art_status']=='mapped' for r in rows), len(audit.current_catalog()))
        self.assertEqual(summary['missing_candidates'] + summary['installed_token_count'], len(rows))
        self.assertEqual(sum(summary['missing_by_priority'].values()), summary['missing_candidates'])
        by_name = {r['native_name']:r for r in rows}
        self.assertEqual(by_name['giant white rat']['origin'], 'rodent-family-completion')
        self.assertEqual(by_name['squid']['priority'], 'excluded-local-import')
        self.assertEqual(by_name['shadow']['priority'], 'summoned-actor')
        self.assertEqual(by_name['The Shade']['gate'], 'render-contract-first')
        self.assertEqual(by_name['bandit']['art_status'], 'mapped')
        self.assertGreater(len(families), 60)
        self.assertEqual(len(zones), summary['base_zones'])
        self.assertEqual(len(grids), summary['base_grid_family_files'])


if __name__ == '__main__':
    unittest.main()
