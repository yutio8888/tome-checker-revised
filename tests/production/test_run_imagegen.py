"""`tools/run_imagegen.py` 的链路测试。不调用真实模型，不新增/修改任何美术。

真实模型被一个**假 codex 可执行文件**替换：它按真 CLI 的参数约定解析 `-i/--image`、
`--output-schema`、`-o/--output-last-message`，把一张**既有的真实 PNG**放进临时
`$CODEX_HOME/generated_images/<session>/exec-<uuid>.png`，再写出结构化结果。
被替换的只有「模型产出哪张图」这一件事；溯源校验、alpha 校验、128px 导出、风格门控、
记账与 `art_tasks.py record` 全部是真代码在真文件上跑。
"""
import contextlib
import hashlib
import io
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKSPACE = ROOT.parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
import art_tasks                      # noqa: E402
import run_imagegen as wrapper        # noqa: E402

# 门控口径下干净的既有母版；用作「本次生成」的替身。
CLEAN_MASTER = ROOT / 'art/monsters-v2/masters/bee-swarm-v1.png'
# 底盘偏移 +13.62，按 [-8,+8] 口径不合格，且不吃豁免（新资产 id）。
DRIFTED_MASTER = ROOT / 'art/monsters-v2/masters/brown-rat-v2.png'

FAKE_CODEX = r'''#!/usr/bin/env python3
import json, os, shutil, sys, uuid
from pathlib import Path

argv = sys.argv[1:]
out = None
images = []
i = 0
while i < len(argv):
    if argv[i] in ('-o', '--output-last-message'):
        out = argv[i + 1]; i += 2
    elif argv[i] in ('-i', '--image'):
        images.append(argv[i + 1]); i += 2
    else:
        i += 1
sys.stdin.read()
mode = os.environ['FAKE_MODE']
src = Path(os.environ['FAKE_SRC'])
root = Path(os.environ['CODEX_HOME']) / 'generated_images'
session = os.environ.get('FAKE_SESSION', '01a00000-0000-7000-8000-000000000001')
if mode == 'outside':
    target = Path(os.environ['FAKE_OUTSIDE'])
else:
    target = root / session / f'exec-{uuid.uuid4()}.png'
target.parent.mkdir(parents=True, exist_ok=True)
shutil.copyfile(src, target)
Path(os.environ['FAKE_IMAGES_SEEN']).write_text(json.dumps(images))
payload = {
    'image_path': str(target),
    'image_generation_tool_used': mode != 'notool',
    'transparent_background': True,
    'notes': 'fake codex for tooling tests',
}
Path(out).write_text(json.dumps(payload))
print(json.dumps(payload))
'''


class Args:
    """argparse.Namespace 的最小替身。"""

    def __init__(self, **kw):
        self.codex_bin = None
        self.codex_sandbox = 'read-only'
        self.model = None
        self.ephemeral = True
        self.timeout = 60
        self.execute = True
        self.pack = None
        self.saved = None
        self.attempt = None
        self.request = None
        self.no_record = False
        self.__dict__.update(kw)


class ChainTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='run-imagegen-test-')
        self.tmpdir = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)

        self.codex_home = self.tmpdir / 'codex-home'
        (self.codex_home / 'generated_images').mkdir(parents=True)
        patch = mock.patch.multiple(
            wrapper, CODEX_HOME=self.codex_home,
            GENERATED_ROOT=self.codex_home / 'generated_images')
        patch.start()
        self.addCleanup(patch.stop)

        self.fake = self.tmpdir / 'fake-codex'
        self.fake.write_text(FAKE_CODEX)
        self.fake.chmod(self.fake.stat().st_mode | stat.S_IEXEC)
        self.images_seen = self.tmpdir / 'images-seen.json'

        # 任务包与母版目录都建在仓库内的临时目录里，测试结束即删。
        self.handoffs = Path(tempfile.mkdtemp(dir=ROOT / 'art/production', prefix='test-wrapper-'))
        self.addCleanup(shutil.rmtree, self.handoffs, True)
        self.masters = Path(tempfile.mkdtemp(dir=ROOT / 'art', prefix='test-wrapper-'))
        self.addCleanup(shutil.rmtree, self.masters, True)

        catalog = mock.patch.object(art_tasks, 'current_catalog', return_value={})
        catalog.start()
        self.addCleanup(catalog.stop)
        self.pack = self.make_pack()

    # ---------------------------------------------------------------- helpers
    def pin(self, rel, **extra):
        path = WORKSPACE / rel
        return dict(path=rel, sha256=hashlib.sha256(path.read_bytes()).hexdigest(), **extra)

    def make_pack(self, max_attempts=2):
        style = 'game/addons/tome-checker-revised/art/monsters-v2/masters/brown-rat-v2.png'
        ident = 'game/addons/tome-checker-revised/art/monsters-v1/masters/wolf-v1.png'
        me = 'game/addons/tome-checker-revised/tools/run_imagegen.py'
        manifest = dict(schema=1, batch_id='test-wrapper', assets=[dict(
            asset_id='wrapper-fixture', native_name='wrapper test fixture',
            kind='creature', gate='ready',
            gate_reason='Synthetic gate for tool unit test only; not production approval.',
            scope='tooling test fixture; no native identity claimed.',
            max_attempts=max_attempts,
            sources=[self.pin(me, line=1, anchor='#!/usr/bin/env python3')],
            references=[self.pin(style, role='style', note='style only'),
                        self.pin(ident, role='identity', note='identity only')],
            render_evidence=[self.pin(me)],
            contrast_dimensions=['silhouette', 'value'],
            prompt_fields=dict(subject='fixture', contrast='fixture',
                               composition='fixture', palette='fixture'))])
        path = self.handoffs / 'manifest.json'
        path.write_text(json.dumps(manifest))
        art_tasks.prepare(path, self.handoffs / 'out')
        return self.handoffs / 'out/wrapper-fixture'

    def args(self, src=CLEAN_MASTER, mode='normal', **kw):
        os.environ.update(CODEX_HOME=str(self.codex_home), FAKE_MODE=mode,
                          FAKE_SRC=str(src), FAKE_IMAGES_SEEN=str(self.images_seen))
        return Args(codex_bin=str(self.fake), pack=self.pack, **kw)

    def saved_path(self, version=1):
        return self.masters / f'masters/wrapper-fixture-v{version}.png'

    # ------------------------------------------------------------------ tests
    def test_dry_run_makes_no_call_and_shows_command(self):
        plan = wrapper.cmd_generate(self.args(execute=False, saved=self.saved_path()))
        self.assertEqual(plan['mode'], 'dry-run')
        self.assertIn('--output-schema', plan['command'])
        self.assertIn('--skip-git-repo-check', plan['command'])
        self.assertEqual(plan['command'].count('--image'), 2)
        self.assertEqual(plan['planned_codex_calls'], 1)
        self.assertFalse((self.pack / wrapper.LEDGER_DIRNAME).exists())
        self.assertEqual(wrapper.budget(wrapper.load_pack(self.pack))['calls_used'], 0)

    def test_success_passes_references_and_records_through_art_tasks(self):
        result = wrapper.cmd_generate(self.args(saved=self.saved_path()))
        # 参考图确实通过 -i 传给了 CLI。
        self.assertEqual(len(json.loads(self.images_seen.read_text())), 2)
        self.assertEqual(result['record']['outcome'], 'recorded')
        self.assertTrue(result['record']['provenance']['ok'])
        self.assertTrue(result['record']['gate_passed'])
        # 回执由 art_tasks.py 写，本工具不另建一套。
        receipt = json.loads((self.pack / 'receipts/attempt-1.json').read_text())
        self.assertEqual(receipt['attempt'], 1)
        self.assertEqual(receipt['accepted'], False)
        # 逐字节复制。
        self.assertEqual(hashlib.sha256(self.saved_path().read_bytes()).hexdigest(),
                         receipt['sha256'])
        # 记账里有会话 id、产物原始路径、门控实测值。
        record = json.loads((ROOT / result['call'] / 'call.json').read_text())
        self.assertTrue(record['codex_session_id'])
        self.assertIn('generated_images', record['original_output_path'])
        self.assertIn('base_drift', record['style_gate'])
        self.assertEqual(len(record['references']), 2)
        self.assertTrue(record['task_prompt'].startswith('Use case: stylized-concept.'))

    def test_provenance_rejects_output_outside_generated_images(self):
        outside = self.tmpdir / 'hand-painted.png'
        os.environ['FAKE_OUTSIDE'] = str(outside)
        with self.assertRaises(wrapper.WrapperError) as caught:
            wrapper.cmd_generate(self.args(mode='outside', saved=self.saved_path()))
        self.assertIn('疑似非 ImageGen 产出', str(caught.exception))
        self.assertFalse((self.pack / 'receipts').exists())
        # 失败的调用同样记账，同样占用预算。
        record = json.loads((self.pack / wrapper.LEDGER_DIRNAME / 'call-1/call.json').read_text())
        self.assertEqual(record['outcome'], 'provenance-rejected')
        self.assertEqual(wrapper.budget(wrapper.load_pack(self.pack))['calls_used'], 1)

    def test_master_alpha_rejects_a_real_rgb_imagegen_output(self):
        """真实的已知失败模式：ImageGen 在未要求透明时返回不含 alpha 的 RGB 图。"""
        from PIL import Image
        rgb = self.tmpdir / 'rgb-master.png'
        with Image.open(CLEAN_MASTER) as image:
            flat = Image.new('RGB', image.size, (255, 255, 255))
            flat.paste(image.convert('RGB'), mask=image.getchannel('A'))
            flat.save(rgb)
        with Image.open(rgb) as check:
            self.assertEqual(check.mode, 'RGB')
        with self.assertRaises(wrapper.WrapperError) as caught:
            wrapper.cmd_generate(self.args(src=rgb, saved=self.saved_path()))
        self.assertIn('母版透明通道不合格', str(caught.exception))
        self.assertFalse((self.pack / 'receipts').exists())
        self.assertFalse(self.saved_path().exists())
        record = json.loads((self.pack / wrapper.LEDGER_DIRNAME / 'call-1/call.json').read_text())
        self.assertEqual(record['outcome'], 'master-alpha-rejected')
        self.assertEqual(record['master_metrics']['mode'], 'RGB')
        self.assertFalse(record['master_metrics']['native_alpha_channel'])

    def test_style_gate_blocks_and_does_not_record(self):
        with self.assertRaises(wrapper.WrapperError) as caught:
            wrapper.cmd_generate(self.args(src=DRIFTED_MASTER, saved=self.saved_path()))
        self.assertIn('风格门控不通过', str(caught.exception))
        self.assertIn('底盘偏移', str(caught.exception))
        self.assertFalse((self.pack / 'receipts').exists())
        self.assertFalse(self.saved_path().exists())
        record = json.loads((self.pack / wrapper.LEDGER_DIRNAME / 'call-1/call.json').read_text())
        self.assertEqual(record['outcome'], 'style-gate-rejected')
        self.assertIn('base_drift', record['style_gate']['blocking'])
        # 新资产不吃 GRANDFATHERED 豁免。
        self.assertFalse(record['style_gate']['allow_grandfather'])

    def test_no_record_stops_before_ingest_but_still_bills(self):
        result = wrapper.cmd_generate(self.args(no_record=True, request=None))
        self.assertEqual(result['record']['outcome'], 'gated-only')
        self.assertFalse((self.pack / 'receipts').exists())
        self.assertEqual(wrapper.budget(wrapper.load_pack(self.pack))['calls_used'], 1)

    def test_request_override_requires_no_record(self):
        other = self.tmpdir / 'other-request.json'
        other.write_text(json.dumps({'prompt': 'x', 'referenced_image_paths': []}))
        with self.assertRaisesRegex(wrapper.WrapperError, 'full_prompt 不实'):
            wrapper.cmd_generate(self.args(request=other, saved=self.saved_path()))

    def test_budget_is_capped_at_max_attempts_counting_failures(self):
        outside = self.tmpdir / 'hand-painted.png'
        os.environ['FAKE_OUTSIDE'] = str(outside)
        for _ in range(2):
            with self.assertRaises(wrapper.WrapperError):
                wrapper.cmd_generate(self.args(mode='outside', saved=self.saved_path()))
        self.assertEqual(wrapper.budget(wrapper.load_pack(self.pack))['calls_left'], 0)
        with self.assertRaisesRegex(wrapper.WrapperError, '调用预算已用尽'):
            wrapper.cmd_generate(self.args(mode='outside', saved=self.saved_path()))
        self.assertEqual(len(list((self.pack / wrapper.LEDGER_DIRNAME).glob('call-*'))), 2)

    def test_single_attempt_pack_gets_no_repair(self):
        shutil.rmtree(self.handoffs / 'out')
        self.pack = self.make_pack(max_attempts=1)
        wrapper.cmd_generate(self.args(saved=self.saved_path()))
        with self.assertRaisesRegex(wrapper.WrapperError, '不允许返修'):
            wrapper.cmd_repair(self.args(execute=False))

    def test_direct_second_generate_without_repair_is_refused(self):
        wrapper.cmd_generate(self.args(saved=self.saved_path()))
        with self.assertRaisesRegex(wrapper.WrapperError, '尚未准备返修'):
            wrapper.cmd_generate(self.args(saved=self.saved_path(2)))

    def test_repair_is_metric_tagged_and_uses_art_tasks(self):
        # 首轮用一张门控不合格但母版 alpha 合格的图入库：art_tasks.record 在收据
        # 阶段只管母版 alpha，底盘漂移要等 128px 导出才测得到，这正是返修的由来。
        self.args()  # 只为设置假 codex 的环境变量
        saved = self.saved_path()
        saved.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(DRIFTED_MASTER, saved)
        original = self.tmpdir / 'original.png'
        shutil.copyfile(DRIFTED_MASTER, original)
        art_tasks.record(self.pack, original, saved, 1)

        preview = wrapper.cmd_repair(self.args(execute=False))
        self.assertEqual(preview['review_source'], 'metric')
        self.assertIn(wrapper.METRIC_TAG, preview['review']['observed_failure'])
        self.assertIn('压暗', preview['review']['required_change'])
        self.assertIn('不得原样继承', preview['review']['required_change'])
        self.assertIn('身份与物种', preview['review']['invariants'])
        self.assertEqual(preview['review']['review_scale'], '128')
        # 预演不创建 repair/，不消耗预算。
        self.assertFalse((self.pack / 'repair').exists())
        self.assertEqual(preview['budget']['calls_used'], 0)

        result = wrapper.cmd_repair(self.args(src=CLEAN_MASTER, saved=self.saved_path(2)))
        # repair/ 由 art_tasks.py 生成，计数与提示词都归它管。
        self.assertTrue((self.pack / 'repair/review.json').is_file())
        self.assertTrue((self.pack / 'repair/imagegen-request.json').is_file())
        request = json.loads((self.pack / 'repair/imagegen-request.json').read_text())
        # 失败的那张图确实作为 image 1（编辑目标）发了回去。
        self.assertEqual(Path(request['referenced_image_paths'][0]).resolve(), saved.resolve())
        self.assertIn(wrapper.METRIC_TAG, request['prompt'])
        review = json.loads((self.pack / 'repair/review.json').read_text())
        self.assertEqual(set(review), {'review_scale', 'observed_failure',
                                       'required_change', 'invariants'})
        marker = json.loads((self.pack / wrapper.LEDGER_DIRNAME
                             / 'repair-review-source.json').read_text())
        self.assertEqual(marker['review_source'], 'metric')
        self.assertFalse(marker['human_visual_review'])
        self.assertEqual(result['generation']['record']['review_source'], 'metric')
        self.assertEqual(result['generation']['record']['attempt'], 2)
        self.assertTrue((self.pack / 'receipts/attempt-2.json').is_file())
        # 第三次由 art_tasks 的既有规则挡住。
        with self.assertRaisesRegex(wrapper.WrapperError, '配额已用尽|回执已存在'):
            wrapper.cmd_repair(self.args(saved=self.saved_path(3)))

    def test_real_cli_parser_drives_generate_and_repair(self):
        """走真 argparse：返修复用 run_chain，缺一个 generate 专属默认值就会炸在这里。"""
        self.args()
        saved = self.saved_path()
        saved.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(DRIFTED_MASTER, saved)
        original = self.tmpdir / 'cli-original.png'
        shutil.copyfile(DRIFTED_MASTER, original)
        art_tasks.record(self.pack, original, saved, 1)

        common = ['--codex-bin', str(self.fake)]

        def cli(*argv):
            with contextlib.redirect_stdout(io.StringIO()), \
                 contextlib.redirect_stderr(io.StringIO()):
                return wrapper.main(common + list(argv))

        self.assertEqual(cli('status', str(self.pack)), 0)
        self.assertEqual(cli('repair', str(self.pack)), 0)
        self.assertFalse((self.pack / 'repair').exists())          # 预演不落盘
        self.args(src=CLEAN_MASTER)
        self.assertEqual(cli('--execute', 'repair', str(self.pack),
                             '--saved', str(self.saved_path(2))), 0)
        self.assertTrue((self.pack / 'receipts/attempt-2.json').is_file())
        # 第三次被既有规则挡住，退出码非 0。
        self.assertEqual(cli('--execute', 'repair', str(self.pack)), 1)

    def test_repair_refuses_when_first_attempt_passed_every_blocking_check(self):
        wrapper.cmd_generate(self.args(saved=self.saved_path()))
        with self.assertRaisesRegex(wrapper.WrapperError, '指标驱动返修没有依据'):
            wrapper.cmd_repair(self.args(execute=False))


class TerrainGateTests(unittest.TestCase):
    """`terrain_gate` replaces the monster-disc gate for terrain-prop/floor
    kinds (see its docstring: the disc/base-drift checks measure a circular
    baseline that has no meaning for a tree cutout, and the very first real
    F1 call, bog-tree-a attempt 1, was falsely rejected by it). These tests
    use tiny synthetic fixtures, not real generated art.
    """

    def setUp(self):
        from PIL import Image
        self.tmp = tempfile.TemporaryDirectory(prefix='terrain-gate-test-')
        self.dir = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)
        self.Image = Image
        self.size = 512
        self.margin = 0.02 * self.size

        def make(path, top_inset, bottom_edge_frac=0.92, left_inset=60, right_inset=60,
                 corner_alpha=0):
            img = Image.new('RGBA', (self.size, self.size), (0, 0, 0, 0))
            px = img.load()
            top, bottom = int(top_inset), int(self.size * bottom_edge_frac)
            left, right = left_inset, self.size - right_inset
            for y in range(top, bottom):
                for x in range(left, right):
                    px[x, y] = (90, 70, 40, 255)
            if corner_alpha:
                px[0, 0] = (0, 0, 0, corner_alpha)
            img.save(path)
            return path
        self.make = make

        self.clean = make(self.dir / 'clean.png', top_inset=self.margin + 20)
        self.edge = make(self.dir / 'edge.png', top_inset=max(0, self.margin - 1))

    def test_clean_prop_master_passes_all_checks(self):
        result = wrapper.terrain_gate(self.clean, 'terrain-prop', 'some-asset')
        self.assertTrue(result['passed'], result['findings'])
        self.assertEqual(result['blocking'], [])

    def test_edge_touching_master_fails_a8_1_without_a_waiver(self):
        result = wrapper.terrain_gate(self.edge, 'terrain-prop', 'some-asset')
        self.assertFalse(result['passed'])
        self.assertIn('not_edge_touching', result['blocking'])

    def test_floor_master_checks_full_opacity_not_disc_geometry(self):
        opaque = self.dir / 'floor-opaque.png'
        self.Image.new('RGBA', (256, 256), (50, 80, 60, 255)).save(opaque)
        self.assertTrue(wrapper.terrain_gate(opaque, 'terrain-floor', 'some-floor')['passed'])
        rgb = self.dir / 'floor-rgb.png'
        self.Image.new('RGB', (512, 512), (50, 80, 60)).save(rgb)
        self.assertTrue(wrapper.master_alpha_finding(rgb, 'terrain-floor')['ok'])
        self.assertTrue(wrapper.terrain_gate(rgb, 'terrain-floor', 'some-floor')['passed'])
        self.assertFalse(wrapper.master_alpha_finding(rgb, 'terrain-prop')['ok'])
        holey = self.dir / 'floor-holey.png'
        img = self.Image.new('RGBA', (256, 256), (50, 80, 60, 255))
        img.putpixel((5, 5), (50, 80, 60, 0))
        img.save(holey)
        result = wrapper.terrain_gate(holey, 'terrain-floor', 'some-floor')
        self.assertFalse(result['passed'])
        self.assertIn('floor_opaque', result['blocking'])

    def test_bog_misc_prefix_is_exempt_from_grounding_but_not_from_edge_inset(self):
        # A low, flat, water-surface decoration: bbox bottom well above 75%
        # of the canvas must still pass for a bog-misc-* asset id (BRIEF.md
        # Section 1.3), while direction-mark stays the only other exemption.
        low = self.make(self.dir / 'low.png', top_inset=self.margin + 40,
                        bottom_edge_frac=0.4)
        exempt = wrapper.terrain_gate(low, 'terrain-prop', 'bog-misc-1')
        self.assertTrue(exempt['passed'], exempt['findings'])
        self.assertNotIn('grounded_a8', [f['check'] for f in exempt['findings']])
        not_exempt = wrapper.terrain_gate(low, 'terrain-prop', 'some-other-tree')
        self.assertFalse(not_exempt['passed'])
        self.assertIn('grounded_a8', not_exempt['blocking'])


class A8WaiverIsolationTests(unittest.TestCase):
    """The A8.1 waiver file must be the narrowest possible exception: it may
    only ever accept the exact (asset_id, output sha256) pair a human
    approved, never a threshold change and never a whole asset_id prefix.
    """

    def setUp(self):
        from PIL import Image
        self.tmp = tempfile.TemporaryDirectory(prefix='a8-waiver-test-')
        self.dir = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)
        size = 512
        margin = 0.02 * size
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        px = img.load()
        for y in range(int(margin - 1), int(size * 0.92)):
            for x in range(60, size - 60):
                px[x, y] = (90, 70, 40, 255)
        self.edge = self.dir / 'edge.png'
        img.save(self.edge)
        self.edge_sha = wrapper.digest(self.edge)

        self.waiver_path = self.dir / 'waiver.json'
        self.waiver_path.write_text(json.dumps({
            'schema': 1, 'check': 'not_edge_touching',
            'entries': [{'asset_id': 'hardtree-test', 'sha256': self.edge_sha,
                        'reason': 'unit test fixture'}],
        }))

    def test_exact_asset_and_hash_is_waived(self):
        with mock.patch.object(wrapper, 'A8_WAIVER_PATH', self.waiver_path):
            result = wrapper.terrain_gate(self.edge, 'terrain-prop', 'hardtree-test')
        self.assertTrue(result['passed'], result['findings'])
        finding = next(f for f in result['findings'] if f['check'] == 'not_edge_touching')
        self.assertTrue(finding['waived'])

    def test_wrong_asset_id_same_hash_is_not_waived(self):
        with mock.patch.object(wrapper, 'A8_WAIVER_PATH', self.waiver_path):
            result = wrapper.terrain_gate(self.edge, 'terrain-prop', 'someone-else')
        self.assertFalse(result['passed'])

    def test_same_asset_id_different_hash_is_not_waived(self):
        from PIL import Image
        mutated = self.dir / 'edge-mutated.png'
        img = Image.open(self.edge).convert('RGBA')
        img.putpixel((0, 0), (1, 1, 1, 1))
        img.save(mutated)
        with mock.patch.object(wrapper, 'A8_WAIVER_PATH', self.waiver_path):
            result = wrapper.terrain_gate(mutated, 'terrain-prop', 'hardtree-test')
        self.assertFalse(result['passed'])

    def test_missing_waiver_file_waives_nothing(self):
        with mock.patch.object(wrapper, 'A8_WAIVER_PATH', self.dir / 'does-not-exist.json'):
            result = wrapper.terrain_gate(self.edge, 'terrain-prop', 'hardtree-test')
        self.assertFalse(result['passed'])

    def test_shipped_waiver_file_covers_only_pinned_entries(self):
        # Exercises the real, committed waiver file so a future careless edit
        # that widens it (drops the sha256 pin, adds a prefix match, etc.) is
        # caught here, not just in a synthetic fixture.
        data = json.loads(wrapper.A8_WAIVER_PATH.read_text())
        self.assertEqual(data['check'], 'not_edge_touching')
        self.assertEqual({e['asset_id'] for e in data['entries']},
                         {'hardtree', 'snow-tree-elm', 'gloomy-vegetation', 'dreamy-vegetation', 'sand-wall', 'crystal-wall', 'cave-wall', 'cave-ladder', 'spellblaze-burnt-tree'})
        for entry in data['entries']:
            self.assertIsNone(wrapper.load_a8_waiver(entry['asset_id'], '0' * 64))
            self.assertIsNone(wrapper.load_a8_waiver('some-other-asset', entry['sha256']))
            self.assertEqual(wrapper.load_a8_waiver(entry['asset_id'], entry['sha256']), entry)


class ModelPinTests(unittest.TestCase):
    """2026-09-30 起默认固定 gpt-6.1-sol 并带 --ephemeral（用户决定）。"""

    def test_cli_defaults_pin_model_and_ephemeral(self):
        parser_args = {}
        real_parse = wrapper.argparse.ArgumentParser.parse_args

        def capture(parser, argv=None, namespace=None):
            ns = real_parse(parser, argv, namespace)
            parser_args.update(vars(ns))
            raise SystemExit(0)

        with mock.patch.object(wrapper.argparse.ArgumentParser, 'parse_args', capture):
            with self.assertRaises(SystemExit):
                wrapper.main(['generate', 'x'])
        self.assertEqual(parser_args['model'], 'gpt-6.1-sol')
        self.assertIs(parser_args['ephemeral'], True)

    def test_no_ephemeral_opt_out(self):
        parser_args = {}
        real_parse = wrapper.argparse.ArgumentParser.parse_args

        def capture(parser, argv=None, namespace=None):
            ns = real_parse(parser, argv, namespace)
            parser_args.update(vars(ns))
            raise SystemExit(0)

        with mock.patch.object(wrapper.argparse.ArgumentParser, 'parse_args', capture):
            with self.assertRaises(SystemExit):
                wrapper.main(['--no-ephemeral', '--model', 'gpt-6-astra', 'generate', 'x'])
        self.assertEqual(parser_args['model'], 'gpt-6-astra')
        self.assertIs(parser_args['ephemeral'], False)

    def test_build_command_flags(self):
        cmd = wrapper.build_command('codex', Path('e'), [], Path('s'), Path('r'),
                                    'read-only', Path('.'), 'gpt-6.1-sol')
        self.assertEqual(cmd[cmd.index('--model') + 1], 'gpt-6.1-sol')
        self.assertIn('--ephemeral', cmd)
        cmd = wrapper.build_command('codex', Path('e'), [], Path('s'), Path('r'),
                                    'read-only', Path('.'), None, ephemeral=False)
        self.assertNotIn('--ephemeral', cmd)
        self.assertNotIn('--model', cmd)


class ProvenanceUnitTests(unittest.TestCase):
    def test_paths_outside_the_generated_root_are_rejected(self):
        info = wrapper.verify_provenance('/tmp/whatever.png', set(), 0)
        self.assertFalse(info['ok'])
        self.assertIn('疑似非 ImageGen 产出', info['reason'])

    def test_wrong_filename_inside_the_root_is_rejected(self):
        bogus = wrapper.GENERATED_ROOT / 'sess/hand-made.png'
        info = wrapper.verify_provenance(str(bogus), set(), 0)
        self.assertFalse(info['ok'])
        self.assertIn('exec-<uuid>.png', info['reason'])

    def test_empty_path_is_rejected(self):
        self.assertFalse(wrapper.verify_provenance('', set(), 0)['ok'])


if __name__ == '__main__':
    unittest.main()
