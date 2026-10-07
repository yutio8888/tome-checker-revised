#!/usr/bin/env python3
"""把「调用内置 ImageGen → 门控 → 入库」这条链路包装成可审计的一条命令。

本工具**不自己画像素**，也不替换既有的任务包 / 返修计数体系：

* 生成由 `codex exec` 的**内置** `image_generation` 工具完成。产物落在
  `~/.codex/generated_images/<session-id>/exec-<uuid>.png`，这个目录只有内置工具
  会写——因此「产物是否溯源到该目录」被当作**防线**使用，而不是形式检查。
  提示词层面的「不要自己写代码画图」不可靠：codex 跑的是完整 agent。
* 母版透明通道、圆盘越界、底盘明度漂移、四角透明全部交给既有的只读检查器
  `tools/check_token_style.py`，128px 导出件由 `tools/export_token.c` 编出的同一个
  二进制产生（与 `tools/build_monster_art.py` 的 128px 步骤同一口径）。
* 入库、回执、返修计数一律走 `tools/art_tasks.py` 的既有接口。本工具**不另建计数**，
  并且把「单个任务包的 codex 调用总数」硬顶在任务包自己的 `max_attempts`（1 或 2）上，
  失败的调用同样计数——失败也烧掉了用户的订阅额度。

默认 **dry-run**。真正发起生成必须显式 `--execute`。

    python3 tools/run_imagegen.py generate art/production/handoffs/BATCH/ASSET \
        --saved art/BATCH/masters/ASSET-v1.png            # 预演
    python3 tools/run_imagegen.py generate ... --saved ... --execute
    python3 tools/run_imagegen.py repair   art/production/handoffs/BATCH/ASSET --execute

用法与字段说明见 `art/production/README.md` 的「生成端包装器」一节。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from string import Template

sys.path.insert(0, str(Path(__file__).resolve().parent))

import art_tasks
import check_token_style

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = art_tasks.WORKSPACE
TEMPLATES = ROOT / 'art/production/templates'
LEDGER_DIRNAME = 'imagegen-calls'

# 唯一可信的产物目录。只有 codex 的内置 image_generation 会往这里写。
DEFAULT_MODEL = 'gpt-6.1-sol'
CODEX_HOME = Path(os.environ.get('CODEX_HOME') or (Path.home() / '.codex'))
GENERATED_ROOT = CODEX_HOME / 'generated_images'
GENERATED_NAME = re.compile(r'^exec-[0-9a-fA-F-]{8,}\.png$')

EXPORT_SIZE = 128
OCCUPANCY_MIN = 0.83   # 与 tools/build_monster_art.py 的导出断言同值
OCCUPANCY_MAX = 0.91

# 送给 codex 的信封。任务包的提示词逐字嵌在 IMAGE BRIEF 里，信封只约束「怎么调工具、
# 怎么回话」，不改美术方向。信封与任务提示词分别记账（envelope_sha256 / prompt_sha256）。
ENVELOPE = Template("""You are running a headless, single-shot image generation job.

Do exactly this, in order, and nothing else:
1. Open and actually look at every attached reference image.
2. Call your built-in image generation tool EXACTLY ONCE with the image brief below.
3. Do NOT write, run, edit or save any code, script or file. Do NOT draw, composite,
   crop, upscale or post-process the picture yourself, and do not shell out to any
   image utility. The built-in image generation tool must be the sole producer of the
   returned file. If that tool is unavailable or fails, stop and report the failure in
   the JSON instead of substituting anything.
4. Do not save, move or copy the generated file anywhere. Report the tool's own output
   path exactly as the tool wrote it.
5. Reply with a single JSON object matching the supplied schema.

IMAGE BRIEF (treat the text between the markers as the verbatim art direction):
<<<BRIEF
$brief
BRIEF

$refs""")

OUTPUT_SCHEMA = {
    'type': 'object',
    'additionalProperties': False,
    'required': ['image_path', 'image_generation_tool_used', 'transparent_background', 'notes'],
    'properties': {
        'image_path': {
            'type': 'string',
            'description': "Absolute filesystem path of the PNG the built-in image "
                           "generation tool wrote, exactly as the tool reported it.",
        },
        'image_generation_tool_used': {
            'type': 'boolean',
            'description': 'True only if the built-in image generation tool produced the file.',
        },
        'transparent_background': {
            'type': 'boolean',
            'description': 'True if the returned PNG has a genuine transparent alpha channel.',
        },
        'notes': {
            'type': 'string',
            'description': 'One or two sentences: what was drawn, or why it failed.',
        },
    },
}


class WrapperError(Exception):
    """链路无法继续。区别于「跑完了但判定不合格」。"""


def digest(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def rel_to_root(path: Path) -> str:
    path = Path(path).resolve()
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


# ---------------------------------------------------------------------------
# 任务包 / 预算
# ---------------------------------------------------------------------------
def load_pack(pack: Path) -> dict:
    pack = art_tasks.confined(pack, ROOT / 'art/production')
    inputs = pack / 'inputs.json'
    if not inputs.is_file():
        raise WrapperError(f'不是任务包目录（缺 inputs.json）：{pack}')
    lock = json.loads(inputs.read_text())
    asset = lock['task']
    if asset['gate'] != 'ready':
        raise WrapperError(f"任务包 gate={asset['gate']}，hold 不是生成授权；先按规范改 ready 并换新版本目录。")
    return {'pack': pack, 'lock': lock, 'asset': asset}


def ledger_dir(pack: Path) -> Path:
    return pack / LEDGER_DIRNAME


def past_calls(pack: Path) -> list[dict]:
    folder = ledger_dir(pack)
    if not folder.is_dir():
        return []
    records = []
    for call in sorted(p for p in folder.glob('call-*') if p.is_dir()):
        path = call / 'call.json'
        try:
            records.append(json.loads(path.read_text()))
        except (OSError, ValueError) as exc:
            # 目录存在就说明这次 codex 已经发起过、额度已经烧掉；记账文件缺失或损坏
            # 要在报告里显式暴露，不能当成「没发生过」。
            records.append({'call_index': call.name, 'outcome': 'unrecorded',
                            'failure': f'记账文件缺失或损坏：{exc}'})
    return records


def budget(state: dict) -> dict:
    """单个任务包的 codex 调用预算。失败的调用同样占用。

    计数按 `imagegen-calls/call-*` **目录**数，而不是按 call.json 数：目录在发起
    codex 之前就建好，即使记账文件因崩溃没写出来，这一次额度也已经烧掉了，不能
    因为缺少记账文件就白送一次。
    """
    pack, asset = state['pack'], state['asset']
    used = len([p for p in ledger_dir(pack).glob('call-*') if p.is_dir()]) \
        if ledger_dir(pack).is_dir() else 0
    allowed = asset['max_attempts']
    return {'max_attempts': allowed, 'calls_used': used, 'calls_left': max(0, allowed - used)}


def receipts(pack: Path) -> list[int]:
    folder = pack / 'receipts'
    if not folder.is_dir():
        return []
    found = []
    for path in folder.glob('attempt-*.json'):
        match = re.fullmatch(r'attempt-(\d+)\.json', path.name)
        if match:
            found.append(int(match.group(1)))
    return sorted(found)


def resolve_attempt(state: dict, requested: int | None) -> int:
    """推断本次是第几号 attempt，并守住既有的顺序/上限规则。"""
    pack, asset = state['pack'], state['asset']
    done = receipts(pack)
    if 1 not in done:
        attempt = 1
    elif (pack / 'repair').is_dir():
        attempt = 2
    else:
        raise WrapperError('attempt-1 已入库但尚未准备返修；请用 `repair` 子命令，'
                           '不要直接发起第二次生成。')
    if requested is not None and requested != attempt:
        raise WrapperError(f'本任务包当前应为 attempt {attempt}，拒绝 attempt {requested}；'
                           '禁止跳号，也禁止另建目录洗掉返修计数。')
    if attempt > asset['max_attempts']:
        raise WrapperError(f"attempt {attempt} 超出任务包 max_attempts={asset['max_attempts']}；"
                           '第二次仍失败就停下，交回设计，不要自动发起第三次。')
    if attempt in done:
        raise WrapperError(f'attempt-{attempt} 回执已存在，拒绝覆盖。')
    return attempt


def resolve_request(state: dict, attempt: int, override: Path | None) -> Path:
    if override is not None:
        path = override.resolve()
        if not path.is_file():
            raise WrapperError(f'指定的请求文件不存在：{path}')
        return path
    folder = state['pack'] / 'repair' if attempt == 2 else state['pack']
    request = folder / 'imagegen-request.json'
    if not request.is_file():
        raise WrapperError(f'缺少 {request}；ready 任务包才有调用文件，返修需先跑 `repair`。')
    return request


def resolve_saved(state: dict, attempt: int, override: Path | None) -> Path:
    if override is not None:
        return override if override.is_absolute() else (ROOT / override)
    if attempt == 1:
        raise WrapperError('attempt 1 必须显式给出 --saved art/<batch>/masters/<id>-v1.png')
    receipt = json.loads((state['pack'] / 'receipts/attempt-1.json').read_text())
    first = ROOT / receipt['saved_output_path']
    if not first.name.endswith('-v1.png'):
        raise WrapperError(f'无法从首轮母版名推导 v2 路径：{first}；请显式 --saved')
    return first.with_name(first.name[:-len('-v1.png')] + '-v2.png')


# ---------------------------------------------------------------------------
# codex 调用
# ---------------------------------------------------------------------------
def codex_binary(explicit: str | None) -> str:
    candidate = explicit or os.environ.get('CODEX_BIN') or shutil.which('codex')
    if not candidate:
        fallback = Path.home() / '.local/bin/codex'
        candidate = str(fallback) if fallback.is_file() else None
    if not candidate or not Path(candidate).is_file():
        raise WrapperError('找不到 codex CLI；用 --codex-bin 指定，或设置 CODEX_BIN。')
    return str(candidate)


def build_envelope(request: dict) -> str:
    refs = request.get('referenced_image_paths') or []
    if refs:
        lines = '\n'.join(f'- attached image {i + 1}: {path}' for i, path in enumerate(refs))
        note = ('The attached images are references supplied with this prompt, in this order.\n'
                f'{lines}\n')
    else:
        note = 'No reference images are attached.\n'
    return ENVELOPE.substitute(brief=request['prompt'].strip(), refs=note)


def build_command(binary: str, envelope_path: Path, refs: list[Path], schema: Path,
                  result: Path, sandbox: str, cwd: Path, model: str | None,
                  ephemeral: bool = True) -> list[str]:
    command = [binary, 'exec', '--skip-git-repo-check', '--sandbox', sandbox, '--cd', str(cwd)]
    if model:
        command += ['--model', model]
    # 产物校验只看 generated_images，不读会话文件；--ephemeral 不落 sessions/ 滚动日志。
    if ephemeral:
        command.append('--ephemeral')
    for ref in refs:
        command += ['--image', str(ref)]
    command += ['--output-schema', str(schema), '--output-last-message', str(result)]
    # 提示词从 stdin 传（`-` 表示读 stdin），避免超长 argv 和 shell 转义问题。
    command.append('-')
    return command


def parse_result(path: Path) -> dict:
    """读 `-o` 写下的结构化结果。绝不去刮 stdout。"""
    if not path.is_file():
        raise WrapperError(f'codex 没有写出结构化结果：{path}')
    text = path.read_text().strip()
    if not text:
        raise WrapperError(f'codex 结构化结果为空：{path}')
    try:
        return json.loads(text)
    except ValueError:
        start, end = text.find('{'), text.rfind('}')
        if start < 0 or end <= start:
            raise WrapperError(f'codex 结果不是 JSON：{text[:400]}')
        try:
            return json.loads(text[start:end + 1])
        except ValueError as exc:
            raise WrapperError(f'codex 结果无法解析为 JSON：{exc}；原文 {text[:400]}')


def snapshot_generated() -> set[str]:
    if not GENERATED_ROOT.is_dir():
        return set()
    return {str(p) for p in GENERATED_ROOT.rglob('*.png')}


# ---------------------------------------------------------------------------
# ① 溯源校验
# ---------------------------------------------------------------------------
def verify_provenance(reported: str, before: set[str], started: float) -> dict:
    """产物必须落在 ~/.codex/generated_images/ 之下，且是本次调用期间新出现的。

    这是防线而不是形式：提示词层面禁止「自己写代码画图」不可靠，codex 跑的是完整
    agent；但它无法把文件写进内置工具的产物目录（该目录由 CLI 自己管理，且本工具
    默认用 read-only sandbox 运行 codex）。
    """
    fresh = sorted(p for p in snapshot_generated() - before)
    info = {
        'reported_path': reported,
        'generated_root': str(GENERATED_ROOT),
        'new_files_during_call': fresh,
        'ok': False,
        'reason': None,
        'session_id': None,
        'resolved_path': None,
    }
    if not reported:
        # The built-in tool sometimes writes the file but codex never echoes the
        # path back. If exactly one new exec-<uuid>.png appeared during the call,
        # that file is the artifact: same trusted directory, same call window.
        # More than one new file is ambiguous and still rejected.
        if len(fresh) == 1:
            reported = fresh[0]
            info['path_source'] = 'fresh-file fallback (codex did not report the path)'
        else:
            info['reason'] = 'codex 未返回产物路径，且本次调用期间新文件数不是 1'
            return info
    else:
        info['path_source'] = 'reported by codex'
    resolved = Path(os.path.expanduser(reported)).resolve()
    info['resolved_path'] = str(resolved)
    if not resolved.is_relative_to(GENERATED_ROOT.resolve()):
        info['reason'] = (f'疑似非 ImageGen 产出：产物 {resolved} 不在 {GENERATED_ROOT} 之下。'
                          '内置 ImageGen 只会写这个目录；路径在别处说明这张图很可能是 '
                          'agent 自己画/存的，按 art/production/README.md 一律不收。')
        return info
    if not GENERATED_NAME.fullmatch(resolved.name):
        info['reason'] = (f'疑似非 ImageGen 产出：文件名 {resolved.name} 不是内置工具的 '
                          'exec-<uuid>.png 命名。')
        return info
    if not resolved.is_file():
        info['reason'] = f'溯源目录下没有这个文件：{resolved}'
        return info
    if str(resolved) in before:
        info['reason'] = (f'疑似复用旧产物：{resolved} 在本次调用之前就已存在，'
                          '不能当作本次生成的结果记账。')
        return info
    if resolved.stat().st_mtime < started - 5:
        info['reason'] = f'产物 mtime 早于本次调用开始时间：{resolved}'
        return info
    info['ok'] = True
    info['session_id'] = resolved.parent.name
    if len(fresh) > 1:
        info['multiple_new_files'] = True
    return info


# ---------------------------------------------------------------------------
# ②③④ 母版 alpha / 128px 导出 / 风格门控
# ---------------------------------------------------------------------------
def master_alpha_finding(master: Path, kind: str = 'creature') -> dict:
    if kind == 'terrain-floor':
        from PIL import Image
        with Image.open(master) as image:
            extrema = image.convert('RGBA').getchannel('A').getextrema()
            metrics = {'mode': image.mode, 'alpha_extrema': list(extrema)}
        finding = check_token_style._finding('floor_opaque', 'blocking', extrema == (255, 255),
            f'地板母版 alpha 范围 {extrema}（须恒为 255，ACCEPTANCE A2）')
        return {'metrics': metrics, 'finding': finding, 'ok': finding['ok']}
    metrics = check_token_style.measure_master(master)
    findings = check_token_style.evaluate(None, metrics)
    finding = findings[0]
    return {'metrics': metrics, 'finding': finding, 'ok': finding['ok']}


def ensure_exporter() -> Path:
    """用与 tools/build_monster_art.py 完全相同的编译命令产出同一个导出器。"""
    binary = ROOT / 'tools/bin/export_token'
    source = ROOT / 'tools/export_token.c'
    binary.parent.mkdir(exist_ok=True)
    if not binary.is_file() or binary.stat().st_mtime < source.stat().st_mtime:
        subprocess.run(['cc', '-O2', '-Wall', '-Wextra', str(source), '-o', str(binary),
                        '-lpng', '-lm'], check=True)
    return binary


def export_and_gate(master: Path, asset_id: str, out_png: Path) -> dict:
    """走 build_monster_art.py 的 128px 导出口径，然后调 check_token_style。

    新资产一律不吃 GRANDFATHERED 豁免（allow_grandfather=False）：豁免只覆盖已决定
    本轮不返修的 37 款历史欠账。
    """
    from PIL import Image

    binary = ensure_exporter()
    out_png.parent.mkdir(parents=True, exist_ok=True)
    stats = json.loads(subprocess.check_output(
        [str(binary), str(master), str(out_png), str(EXPORT_SIZE)], text=True))
    extra = []
    with Image.open(out_png) as image:
        if image.size != (EXPORT_SIZE, EXPORT_SIZE) or image.mode != 'RGBA':
            raise WrapperError(f'导出件异常：{out_png} {image.size} {image.mode}')
        bounds = image.getchannel('A').point(lambda a: 255 if a > 8 else 0).getbbox()
        occupancy = max(bounds[2] - bounds[0], bounds[3] - bounds[1]) / EXPORT_SIZE
    ok = OCCUPANCY_MIN <= occupancy <= OCCUPANCY_MAX
    extra.append(check_token_style._finding(
        'export_occupancy', 'blocking', ok,
        f'128px 可见占格 {occupancy:.4f}（区间 {OCCUPANCY_MIN}–{OCCUPANCY_MAX}）',
        value=round(occupancy, 4)))
    result = check_token_style.check_asset(out_png, master, asset_id, allow_grandfather=False)
    result['findings'] = list(result['findings']) + extra
    blocking = [f for f in result['findings'] if f['level'] == 'blocking' and not f['ok']]
    result['blocking'] = [f['check'] for f in blocking]
    result['passed'] = not blocking or (result['waived'] and ok
        and blocking == ['base_drift'])
    result['export_stats'] = stats
    result['export_path'] = str(out_png)
    return result


def blocking_details(result: dict) -> str:
    return '；'.join(f['detail'] for f in result['findings']
                     if f['level'] == 'blocking' and not f['ok'])


# 低平的水面/地面装饰不是「立着的构筑物」：本批 F1 简报已在 BRIEF.md §1.3 里把
# bog-misc 定成贴着水面的平面贴花，明确不要求触底 25%（同 direction-mark 的平面
# 刻记豁免，ACCEPTANCE A8 例外条款只点名了 direction-mark，这里把同一类"非直立
# 构件"按同样理由白名单化，不是放宽直立树类的判据）。
GROUNDING_EXEMPT_PREFIXES = ('direction-mark', 'bog-misc')

# 实测口径（2026-09-28，F1 批次前 3 次真实 ImageGen 调用）：bog-tree-a 的两次独立
# 生成与 bog-tree-b 的第一次生成，各自互不相关，却都在同一个角（bbox 索引 2，即
# 左下角）留下 alpha=1 而不是 0。三次独立调用命中同一个角、同一个极小值，读作
# 本机 ImageGen 输出管线在透明区域边缘留下的量化残留，不是画面内容缺陷——对比
# ACCEPTANCE A1 本来就为不透明上限留了容差（`MASTER_ALPHA_MAX_FLOOR=240`，因为
# "原生输出可能为252"），这里对角点透明下限做同型量级的容差，而不是保持字面上的
# 、从未被真实输出验证过的"必须恰好为0"。阈值取 4（约1.6%），仍能挡住任何真正
# 可见的角落残留（不透明混合的角一般是两位数以上）。
CORNER_ALPHA_MAX = 4

# Narrowest possible exception mechanism (main-agent decision, 2026-09-28, see
# the `hardtree` call-2 discussion): a per-(asset_id, exact output sha256)
# waiver file, never a threshold or exemption-prefix change. It relaxes ONLY
# the A8.1 not_edge_touching check for the one file a human explicitly
# approved; every other check and every other asset/hash is untouched -- see
# tests/production/test_run_imagegen.py's waiver isolation tests.
A8_WAIVER_PATH = ROOT / 'art/production/waivers/a8-edge-margin.json'


def load_a8_waiver(asset_id: str, sha256: str) -> dict | None:
    if not A8_WAIVER_PATH.is_file():
        return None
    try:
        data = json.loads(A8_WAIVER_PATH.read_text())
    except ValueError:
        return None
    if data.get('check') != 'not_edge_touching':
        return None
    for entry in data.get('entries', []):
        if entry.get('asset_id') == asset_id and entry.get('sha256') == sha256:
            return entry
    return None


def terrain_gate(master: Path, kind: str, asset_id: str) -> dict:
    """地形母版专用门控：替代 export_and_gate 里那套按怪物棋子圆盘校准的检查。

    `tools/check_token_style.py` 的 base_drift/subject_intrusion/disc_overflow/
    export_occupancy 全部是针对「128px 圆形底盘 + 冻结的怪物环带亮度基线」设计
    的（README「可测风格约束与门控」一节）。地形道具（一棵立在水里的柳树、一截
    浮木）根本没有圆盘几何，套用这组判据只是在测量画布某个同心圆环恰好落在树冠
    还是背景上的巧合，不是真实的美术缺陷——这次 bog-tree-a 首次实测就撞上了
    （base_drift +12.02，容差 ±8），继续用这套门控走 repair 只会烧掉订阅额度去
    "修正"一个不存在的问题。

    地形母版改用 ACCEPTANCE.md 已经写清楚、且 `tools/art_tasks.py record` 在入库
    阶段本来就会执行的判据：A1（构件原生 alpha、四角透明）、A2（地板全不透明）、
    A8（构件不贴边、除白名单外必须触达画布下 25%——接地）。这里只是把同一套检查
    提前到「刚生成、还没复制进 masters/」的阶段先做一次，好在门控失败时不用先烧
    一次 `--saved` 复制。
    """
    from PIL import Image

    with Image.open(master) as image:
        w, h = image.size
        native_alpha = image.mode in ('RGBA', 'LA', 'PA') or (
            image.mode == 'P' and 'transparency' in image.info)
        rgba = image.convert('RGBA')
        alpha = rgba.getchannel('A')
        extrema = alpha.getextrema()
        corners = [alpha.getpixel(p) for p in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1))]

    findings = []

    def add(check, ok, detail, **extra):
        findings.append({'check': check, 'level': 'blocking', 'ok': ok, 'detail': detail, **extra})

    if kind == 'terrain-floor':
        add('floor_opaque', extrema == (255, 255),
            f'地板母版 alpha 范围 {extrema}（须恒为 255，ACCEPTANCE A2）')
    else:
        add('master_native_alpha',
            native_alpha and extrema[0] == 0 and extrema[1] >= check_token_style.MASTER_ALPHA_MAX_FLOOR,
            f'母版 mode={image.mode} alpha={extrema[0]}..{extrema[1]}（须原生 RGBA/LA/PA、'
            f'跨 0–{check_token_style.MASTER_ALPHA_MAX_FLOOR}+，ACCEPTANCE A1）')
        add('corner_alpha', all(c <= CORNER_ALPHA_MAX for c in corners),
            f'四角 alpha {corners}（须 ≤{CORNER_ALPHA_MAX}，ACCEPTANCE A1.5/A8.3 的实测容差版）')
        bbox = alpha.point(lambda a: 255 if a >= 128 else 0).getbbox()
        if bbox is None:
            add('nontrivial_bbox', False, '整张母版透明，没有可见主体')
        else:
            margin = 0.02 * max(w, h)
            inset_ok = (bbox[0] >= margin and bbox[1] >= margin
                       and bbox[2] <= w - margin and bbox[3] <= h - margin)
            detail = f'不透明包围盒 {bbox}，须距四边 ≥{margin:.1f}px（ACCEPTANCE A8.1）'
            waiver = None if inset_ok else load_a8_waiver(asset_id, digest(master))
            if waiver:
                detail += f'；按逐资产豁免通过（{A8_WAIVER_PATH.name}）：{waiver["reason"]}'
            add('not_edge_touching', inset_ok or bool(waiver), detail, waived=bool(waiver))
            if asset_id.startswith(GROUNDING_EXEMPT_PREFIXES):
                pass  # 平面刻记/水面贴花，按 BRIEF.md §1.3 与 A8 的 direction-mark 白名单同理豁免。
            else:
                grounded = bbox[3] >= 0.75 * h
                add('grounded_a8', grounded,
                    f'不透明包围盒下边缘 {bbox[3]}/{h}={bbox[3]/h:.3f}（须 ≥0.75，ACCEPTANCE A8.2 接地）')

    blocking = [f for f in findings if f['level'] == 'blocking' and not f['ok']]
    return {
        'kind': kind,
        'findings': findings,
        'blocking': [f['check'] for f in blocking],
        'warnings': [],
        'passed': not blocking,
        'export_stats': None,
        'export_path': None,
    }


# Standee masters have no disc geometry: they are full-body upright creatures on
# a transparent field. The disc checks (base_drift, disc_overflow, export
# occupancy, the frozen 8-sector base lightness) are meaningless here, so the
# gate checks what the standee actually has to be: native alpha, transparent
# corners, a non-trivial bbox inset from the edges, and a composition clearly
# taller than wide. The aspect floor is a blocking design requirement, not a
# silhouette-quality verdict; a human still opens every sheet.
STANDEE_MIN_ASPECT = 1.4


def standee_gate(master: Path, asset_id: str) -> dict:
    """Transparent full-body standee master: upright aspect + clean alpha."""
    from PIL import Image

    with Image.open(master) as image:
        w, h = image.size
        native_alpha = image.mode in ('RGBA', 'LA', 'PA') or (
            image.mode == 'P' and 'transparency' in image.info)
        alpha = image.convert('RGBA').getchannel('A')
        extrema = alpha.getextrema()
        corners = [alpha.getpixel(p) for p in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1))]

    findings = []

    def add(check, ok, detail, **extra):
        findings.append({'check': check, 'level': 'blocking', 'ok': ok, 'detail': detail, **extra})

    add('master_native_alpha',
        native_alpha and extrema[0] == 0 and extrema[1] >= check_token_style.MASTER_ALPHA_MAX_FLOOR,
        f'standee 母版 mode={image.mode} alpha={extrema[0]}..{extrema[1]}（须原生 RGBA/LA/PA、'
        f'跨 0–{check_token_style.MASTER_ALPHA_MAX_FLOOR}+）')
    add('corner_alpha', all(c <= CORNER_ALPHA_MAX for c in corners),
        f'四角 alpha {corners}（须 ≤{CORNER_ALPHA_MAX}，不得有假背景）')
    bbox = alpha.point(lambda a: 255 if a >= 128 else 0).getbbox()
    if bbox is None:
        add('nontrivial_bbox', False, '整张立绘母版透明，没有可见主体')
    else:
        # The image tool frames a full-body figure close to the canvas edge, so
        # the pad is deliberately small (2px): it only catches a body that is
        # actually flush with / cut by the border. Framing quality is judged by
        # the human review sheet, not by this number.
        pad = 2.0
        add('not_edge_touching',
            bbox[0] >= pad and bbox[2] <= w - pad
            and bbox[1] >= pad and bbox[3] <= h - pad,
            f'不透明包围盒 {bbox}，须距左右/上下 ≥{pad:.0f}px（不得触边或裁切身体）')
        bw, bh = bbox[2] - bbox[0], bbox[3] - bbox[1]
        aspect = bh / bw if bw else 0
        add('upright_aspect', aspect >= STANDEE_MIN_ASPECT,
            f'不透明包围盒 {bw}x{bh}，高/宽={aspect:.2f}（须 ≥{STANDEE_MIN_ASPECT} 的直立高构图；'
            '横躺/圆盘式构图直接拒收）', value=round(aspect, 3))

    blocking = [f for f in findings if f['level'] == 'blocking' and not f['ok']]
    return {
        'kind': 'standee',
        'findings': findings,
        'blocking': [f['check'] for f in blocking],
        'warnings': [],
        'passed': not blocking,
        'export_stats': None,
        'export_path': None,
    }


def gate_master(master: Path, kind: str, asset_id: str, out_png: Path) -> dict:
    """按资产 kind 分流：怪物/玩家棋子走圆盘门控，地形道具/地板走 terrain_gate。"""
    if kind in ('terrain-prop', 'terrain-floor'):
        return terrain_gate(master, kind, asset_id)
    if kind == 'standee':
        return standee_gate(master, asset_id)
    return export_and_gate(master, asset_id, out_png)


# ---------------------------------------------------------------------------
# 指标驱动的返修评审
# ---------------------------------------------------------------------------
METRIC_TAG = '[metric/128px 自动判定，未经人工看图]'


def synthesize_review(state: dict, gate_result: dict) -> dict:
    """从门控实测值填 review.json 的四个必填字段。

    诚意声明：`art/production/README.md` 要求 `observed_failure` 指向**实际看过的
    小尺寸缺陷**；而这里的结论来自数值门控，不是看图看出来的。因此：
      * 缺陷描述前缀固定带 METRIC_TAG，这段文字会进 repair/review.json、repair 提示词
        和 attempt-2 回执的 full_prompt，无法悄悄抹掉；
      * 记账文件另写 review_source="metric"。
    不要把它当成已完成的视觉评审。
    """
    asset = state['asset']
    failures = [f for f in gate_result['findings'] if f['level'] == 'blocking' and not f['ok']]
    if not failures:
        raise WrapperError('首轮已通过全部阻断判据，指标驱动返修没有依据。'
                           '若仍要改进，请人工实际查看 48/64/96px 后手写 review.json，'
                           '再直接调用 tools/art_tasks.py repair。')
    warnings = [f for f in gate_result['findings'] if f['level'] == 'warning' and not f['ok']]
    passed = [f for f in gate_result['findings'] if f['ok']]

    changes, observed = [], []
    for finding in failures:
        observed.append(finding['detail'])
        changes.append(_required_change(finding))
    for finding in warnings:
        observed.append(f"（警告，非阻断）{finding['detail']}")

    observed_text = f"{METRIC_TAG} " + '；'.join(observed) + \
        '。以上为 tools/check_token_style.py 对 128px 运行导出件的实测结论，不是视觉评审结果。'
    change_text = ' '.join(changes) + \
        ' 编辑目标图（image 1）只提供身份、造型与构图依据；上面点名的那几项正是它被判定为' \
        '缺陷的部分，不得原样继承。除点名项外不要做任何其他改动。'
    keep = [f"身份与物种：{asset['native_name']}", '姿态、朝向、镜头与构图', '主体自身的明暗与配色',
            '原生 RGBA 透明通道与四角透明', '底盘作为中性物理件的几何（直径与斜边宽度）']
    keep += [f"已通过判据 {f['check']}：{f['detail']}" for f in passed]
    return {
        'review_scale': str(EXPORT_SIZE),
        'observed_failure': observed_text,
        'required_change': change_text,
        'invariants': '；'.join(keep) + '。',
    }


def _required_change(finding: dict) -> str:
    check = finding['check']
    if check == 'base_drift':
        drift = finding['value']
        if drift > 0:
            return (f'把底盘的暗盘与铜灰斜边整体压暗约 {abs(drift):.0f} 个亮度单位'
                    f'（8 扇区偏移中位现为 {drift:+.2f}，须落回 ±'
                    f'{check_token_style.DRIFT_TOLERANCE:g} 以内），主体本身的明暗一格不动；'
                    '底盘是中性物理件，不随生物明暗被带偏。')
        return (f'把底盘的暗盘与铜灰斜边整体提亮约 {abs(drift):.0f} 个亮度单位'
                f'（8 扇区偏移中位现为 {drift:+.2f}，须落回 ±'
                f'{check_token_style.DRIFT_TOLERANCE:g} 以内），主体本身的明暗一格不动。')
    if check == 'disc_overflow':
        return (f"把越出圆盘的部分整体内收：最大不透明半径现为 {finding['value']:.3f}，"
                f"须降到 {check_token_style.MAX_DISC_RADIUS} 以内；圆盘外沿保持干净完整的圆，"
                '任何肢体、尾、翼、武器、植株或投影都不得触碰或越过盘边。')
    if check == 'corner_alpha':
        return ('四角必须完全透明：不要画任何背景、棋盘格或衬底，'
                '直接输出盘外真透明的 RGBA。')
    if check == 'master_native_alpha':
        return ('必须输出带原生 alpha 通道的 RGBA PNG，盘外真透明；'
                '不接受白底/灰底/棋盘底再抠图。')
    if check == 'export_occupancy':
        return (f"底盘直径要占满画布：128px 导出后可见占格为 {finding['value']}，"
                f'须落在 {OCCUPANCY_MIN}–{OCCUPANCY_MAX}，圆盘约占画布宽度的 82%。')
    return f"修正：{finding['detail']}。"


def preview_repair_prompt(state: dict, review: dict) -> str:
    template = Template((TEMPLATES / 'repair.txt').read_text())
    prompt = template.substitute(native_name=state['asset']['native_name'], **review)
    return prompt + '\nReferences: image 1 is the edit target; remaining images specify approved style only.\n'


# ---------------------------------------------------------------------------
# 记账
# ---------------------------------------------------------------------------
def next_call_dir(pack: Path) -> Path:
    folder = ledger_dir(pack)
    folder.mkdir(exist_ok=True)
    index = len(list(folder.glob('call-*'))) + 1
    call = folder / f'call-{index}'
    call.mkdir()
    return call


def write_ledger(pack: Path, call_dir: Path, record: dict) -> None:
    (call_dir / 'call.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
    line = {k: record.get(k) for k in ('call_index', 'timestamp_started', 'attempt', 'outcome',
                                       'codex_session_id', 'original_output_path', 'sha256',
                                       'review_source')}
    with (ledger_dir(pack) / 'ledger.jsonl').open('a') as handle:
        handle.write(json.dumps(line, ensure_ascii=False) + '\n')


# ---------------------------------------------------------------------------
# 主链路
# ---------------------------------------------------------------------------
def run_chain(state: dict, attempt: int, request_path: Path, saved: Path | None,
              args, review_source: str, record_result: bool = True) -> dict:
    pack, asset = state['pack'], state['asset']
    request = json.loads(request_path.read_text())
    refs = [Path(p) for p in request.get('referenced_image_paths', [])]
    missing = [str(p) for p in refs if not p.is_file()]
    if missing:
        raise WrapperError(f'参考图缺失：{missing}')
    ref_records = [{'path': str(p), 'sha256': digest(p)} for p in refs]
    envelope = build_envelope(request)
    binary = codex_binary(args.codex_bin)

    plan = {
        'pack': rel_to_root(pack),
        'asset_id': asset['asset_id'],
        'native_name': asset['native_name'],
        'attempt': attempt,
        'request_file': rel_to_root(request_path),
        'references': ref_records,
        'saved_target': rel_to_root(saved) if saved else None,
        'review_source': review_source,
        'budget': budget(state),
        'planned_codex_calls': 1,
    }

    if not args.execute:
        cwd = Path('<临时工作目录>')
        command = build_command(binary, Path('<信封>'), refs, Path('<schema>'),
                                Path('<result.json>'), args.codex_sandbox, cwd, args.model,
                                args.ephemeral)
        plan.update({
            'mode': 'dry-run',
            'command': command,
            'stdin': '信封提示词由 stdin 传入（命令末尾的 `-`）',
            'envelope_preview': envelope,
            'note': '这是预演，没有发起任何生成，也没有消耗额度。加 --execute 才真的调用。',
        })
        return plan

    if plan['budget']['calls_left'] <= 0:
        raise WrapperError(
            f"调用预算已用尽：本任务包 max_attempts={plan['budget']['max_attempts']}，"
            f"已记账 {plan['budget']['calls_used']} 次 codex 调用（失败的也算，它同样消耗了额度）。"
            '第二次仍失败就停下、交回设计，不要另建目录洗掉返修计数。')

    call_dir = next_call_dir(pack)
    call_index = int(call_dir.name.split('-')[1])
    schema_path = call_dir / 'output-schema.json'
    result_path = call_dir / 'result.json'
    envelope_path = call_dir / 'envelope-prompt.txt'
    schema_path.write_text(json.dumps(OUTPUT_SCHEMA, indent=2) + '\n')
    envelope_path.write_text(envelope)

    record = {
        'schema': 1,
        'tool': 'codex exec (builtin image_generation)',
        'call_index': call_index,
        'pack': rel_to_root(pack),
        'asset_id': asset['asset_id'],
        'native_name': asset['native_name'],
        'attempt': attempt,
        'review_source': review_source,
        'record_requested': record_result,
        'request_override': args.request is not None,
        'timestamp_started': now(),
        'request_file': rel_to_root(request_path),
        'task_prompt': request['prompt'],
        'task_prompt_sha256': hashlib.sha256(request['prompt'].encode()).hexdigest(),
        'envelope_prompt_sha256': hashlib.sha256(envelope.encode()).hexdigest(),
        'references': ref_records,
        'codex_sandbox': args.codex_sandbox,
        'codex_model': args.model,
        'codex_ephemeral': args.ephemeral,
        'outcome': 'started',
        'failure': None,
    }

    class _Stop(WrapperError):
        pass

    def stop(outcome, message):
        """任何中断都必须先落账：失败的调用同样烧掉了用户的订阅额度。"""
        record.update(outcome=outcome, failure=message)
        raise _Stop(message)

    ledgered = False
    try:
        with tempfile.TemporaryDirectory(prefix='run-imagegen-') as scratch:
            scratch_dir = Path(scratch)
            command = build_command(binary, envelope_path, refs, schema_path, result_path,
                                    args.codex_sandbox, scratch_dir, args.model, args.ephemeral)
            record['command'] = command
            before = snapshot_generated()
            started = time.time()
            try:
                completed = subprocess.run(command, input=envelope, text=True,
                                           capture_output=True, timeout=args.timeout,
                                           cwd=scratch_dir)
                record['exit_code'] = completed.returncode
                (call_dir / 'stdout.log').write_text(completed.stdout or '')
                (call_dir / 'stderr.log').write_text(completed.stderr or '')
            except subprocess.TimeoutExpired as exc:
                record['exit_code'] = None
                (call_dir / 'stderr.log').write_text(str(exc))
                stop('codex-timeout', f'codex exec 超时（{args.timeout}s）')
            record['duration_seconds'] = round(time.time() - started, 1)
            record['timestamp_finished'] = now()

            try:
                structured = parse_result(result_path)
            except WrapperError as exc:
                stop('no-structured-result', str(exc))
            record['structured_result'] = structured

            # ① 溯源校验
            provenance = verify_provenance(structured.get('image_path', ''), before, started)
            record['provenance'] = provenance
            if not provenance['ok']:
                stop('provenance-rejected', f"溯源校验不通过：{provenance['reason']}")
            original = Path(provenance['resolved_path'])
            record['codex_session_id'] = provenance['session_id']
            record['original_output_path'] = str(original)
            record['sha256'] = digest(original)
            if not structured.get('image_generation_tool_used', False):
                stop('tool-not-claimed', 'codex 自述未使用内置 image_generation 工具')

            # ② 母版原生 alpha
            alpha = master_alpha_finding(original, asset['kind'])
            record['master_metrics'] = alpha['metrics']
            record['master_alpha_finding'] = alpha['finding']
            if not alpha['ok']:
                record['gate_passed'] = False
                stop('master-alpha-rejected',
                     f"母版透明通道不合格：{alpha['finding']['detail']}。"
                     'art_tasks.py record 在收据阶段同样会拒收，本次不入库。'
                     '（已知失败模式：提示词未明确要求透明时，本机 ImageGen 会返回不含 alpha 的 RGB 图。）')

            # ③ 128px 导出 ④ 风格门控（地形道具/地板改走 terrain_gate，见其注释）
            staged = scratch_dir / f"{asset['asset_id']}-attempt{attempt}.png"
            shutil.copyfile(original, staged)
            is_terrain = asset['kind'] in ('terrain-prop', 'terrain-floor')
            is_flat = asset['kind'] in ('terrain-prop', 'terrain-floor', 'standee')
            try:
                gate_result = gate_master(staged, asset['kind'], asset['asset_id'],
                                          call_dir / f'export-{EXPORT_SIZE}.png')
            except (check_token_style.StyleCheckError, subprocess.CalledProcessError,
                    WrapperError, OSError) as exc:
                record['gate_passed'] = False
                stop('export-or-measure-failed', f'128px 导出或度量失败：{exc}')
            if is_flat:
                record['style_gate'] = {
                    'gate': ('terrain_gate (ACCEPTANCE A1/A2/A8; 棋子圆盘门控不适用于无底盘的地形构件)'
                             if is_terrain else
                             'standee_gate (native alpha/corners + upright aspect; 圆盘几何不适用)'),
                    'findings': gate_result['findings'],
                    'blocking': gate_result['blocking'],
                    'warnings': gate_result['warnings'],
                    'passed': gate_result['passed'],
                }
            else:
                record['style_gate'] = {
                    'baseline': list(check_token_style.BASELINE_SECTOR_MEDIANS),
                    'allow_grandfather': False,
                    'base_drift': gate_result['token']['base_drift'],
                    'max_sector_intrusion': gate_result['token']['max_sector_intrusion'],
                    'max_opaque_radius': gate_result['token']['max_opaque_radius'],
                    'sector_offsets': gate_result['token']['sector_offsets'],
                    'export_occupancy': next(f['value'] for f in gate_result['findings']
                                             if f['check'] == 'export_occupancy'),
                    'findings': gate_result['findings'],
                    'blocking': gate_result['blocking'],
                    'warnings': gate_result['warnings'],
                    'passed': gate_result['passed'],
                }
            record['gate_passed'] = gate_result['passed']
            for warning in gate_result['warnings']:
                print(f"WARN {asset['asset_id']}: {warning}", file=sys.stderr)
            if not gate_result['passed']:
                repairable = attempt < asset['max_attempts'] and 1 in receipts(pack)
                gate_label = ('地形母版门控' if is_terrain else
                              '立绘母版门控' if asset['kind'] == 'standee' else '棋子风格门控')
                stop('style-gate-rejected',
                     f'{gate_label}不通过：{blocking_details(gate_result)}。未入库。'
                     + ('可用 `repair` 子命令发起一次定向返修（会消耗最后一次调用配额）。'
                        if repairable else '返修配额已尽或首轮未入库，停下并交回设计。'))

            if not record_result:
                record['outcome'] = 'gated-only'
                record['note'] = '--no-record：链路自检，门控通过但按要求不入库、不写回执。'
                write_ledger(pack, call_dir, record)
                ledgered = True
                return {'mode': 'execute', **plan, 'call': rel_to_root(call_dir),
                        'record': record, 'receipt': None}

            # ⑤ 入库：逐字节复制后交给 art_tasks.py record
            if saved is None:
                stop('no-save-target', '通过门控但没有给出 --saved 入库路径')
            target = saved.resolve()
            created = not target.exists()
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(original, target)
            try:
                receipt = art_tasks.record(pack, original, target, attempt)
            except (ValueError, KeyError, OSError) as exc:
                if created and target.exists():
                    target.unlink()
                stop('record-rejected', f'art_tasks.py record 拒收：{exc}')
            record.update(outcome='recorded', saved_output_path=receipt['saved_output_path'],
                          receipt=f'receipts/attempt-{attempt}.json')
            write_ledger(pack, call_dir, record)
            ledgered = True
            return {'mode': 'execute', **plan, 'call': rel_to_root(call_dir),
                    'record': record, 'receipt': receipt}
    except _Stop as exc:
        write_ledger(pack, call_dir, record)
        ledgered = True
        raise WrapperError(f"{exc}（本次调用已记账：{rel_to_root(call_dir)}/call.json）") from None
    finally:
        if not ledgered:
            # 未预料到的异常：仍然要留下记账，否则这次额度就白烧且无痕。
            record.setdefault('outcome', 'aborted')
            if record['outcome'] in ('started',):
                record['outcome'] = 'aborted'
            try:
                write_ledger(pack, call_dir, record)
            except OSError:
                pass



def cmd_generate(args) -> dict:
    state = load_pack(args.pack)
    attempt = resolve_attempt(state, args.attempt)
    if args.request is not None and not args.no_record:
        # 回执里的 full_prompt 取自任务包的 prompt.txt；若实际发出的是别的提示词，
        # 回执就成了假的。因此覆盖请求文件只允许配 --no-record。
        raise WrapperError('--request 覆盖只允许配 --no-record（链路自检）；'
                           '入库必须发送任务包自己钉住的提示词，否则回执的 full_prompt 不实。')
    if args.no_record:
        print('注意：--no-record 只跑到门控为止，不入库、不写 art_tasks 回执；'
              '仅用于链路自检与诊断。额度照常消耗，记账照常写。', file=sys.stderr)
    saved = None if args.no_record else resolve_saved(state, attempt, args.saved)
    request_path = resolve_request(state, attempt, args.request)
    if attempt == 1:
        source = 'initial'
    elif (ledger_dir(state['pack']) / 'repair-review-source.json').is_file():
        source = 'metric'
    else:
        source = 'external-review'
    return run_chain(state, attempt, request_path, saved, args,
                     review_source=source, record_result=not args.no_record)


def cmd_repair(args) -> dict:
    state = load_pack(args.pack)
    pack, asset = state['pack'], state['asset']
    if asset['max_attempts'] != 2:
        raise WrapperError(f"任务包 max_attempts={asset['max_attempts']}，不允许返修。")
    if 1 not in receipts(pack):
        raise WrapperError('没有 attempt-1 回执；返修必须以已入库的首轮母版为编辑目标。'
                           '首轮若连收据都没过（例如 RGB 母版），请按报告交回设计，'
                           '不要用返修流程绕过。')
    if 2 in receipts(pack):
        raise WrapperError('attempt-2 回执已存在，返修配额已用尽。')

    receipt = json.loads((pack / 'receipts/attempt-1.json').read_text())
    master = ROOT / receipt['saved_output_path']
    if not master.is_file() or digest(master) != receipt['sha256']:
        raise WrapperError(f'首轮母版缺失或字节已变：{master}')

    # 重新实测首轮母版，不依赖上一次运行留下的内存状态。
    is_terrain = asset['kind'] in ('terrain-prop', 'terrain-floor')
    is_flat = asset['kind'] in ('terrain-prop', 'terrain-floor', 'standee')
    with tempfile.TemporaryDirectory(prefix='run-imagegen-gate-') as scratch:
        gate_result = gate_master(master, asset['kind'], asset['asset_id'],
                                  Path(scratch) / 'attempt-1-128.png')
    review = synthesize_review(state, gate_result)

    if is_flat:
        first_attempt_gate = {'blocking': gate_result['blocking'], 'warnings': gate_result['warnings']}
    else:
        first_attempt_gate = {
            'base_drift': gate_result['token']['base_drift'],
            'max_opaque_radius': gate_result['token']['max_opaque_radius'],
            'max_sector_intrusion': gate_result['token']['max_sector_intrusion'],
            'blocking': gate_result['blocking'],
            'warnings': gate_result['warnings'],
        }

    plan = {
        'pack': rel_to_root(pack),
        'asset_id': asset['asset_id'],
        'attempt': 2,
        'review_source': 'metric',
        'review_source_note': (
            f'{METRIC_TAG} 这是数值门控结论，不是人工看图评审。'
            'art/production/README.md 要求 observed_failure 指向实际看过的小尺寸缺陷；'
            '本流程把标记写进 observed_failure 正文与记账文件，不伪装成视觉评审。'),
        'first_attempt_gate': first_attempt_gate,
        'review': review,
        'edit_target': rel_to_root(master),
        'budget': budget(state),
    }

    if not args.execute:
        plan.update(mode='dry-run', repair_prompt_preview=preview_repair_prompt(state, review),
                    note='预演：没有创建 repair/ 目录，没有发起生成，没有消耗额度。')
        return plan

    review_path = ledger_dir(pack) / 'repair-review.json'
    review_path.parent.mkdir(exist_ok=True)
    review_path.write_text(json.dumps(review, ensure_ascii=False, indent=2) + '\n')
    # art_tasks.repair 强制 review.json 恰好四个键，所以 review_source 标记只能
    # 走正文（METRIC_TAG）＋这份旁注文件＋记账，不能塞进 review.json。
    (ledger_dir(pack) / 'repair-review-source.json').write_text(json.dumps({
        'review_source': 'metric',
        'measured_by': 'tools/check_token_style.py',
        'measured_at_px': EXPORT_SIZE,
        'human_visual_review': False,
        'note': plan['review_source_note'],
        'first_attempt_gate': plan['first_attempt_gate'],
        'timestamp': now(),
    }, ensure_ascii=False, indent=2) + '\n')

    if not (pack / 'repair').is_dir():
        art_tasks.repair(pack, review_path)
    plan['repair_folder'] = rel_to_root(pack / 'repair')
    saved = resolve_saved(state, 2, args.saved)
    result = run_chain(state, 2, resolve_request(state, 2, None), saved, args,
                       review_source='metric')
    plan.update(mode='execute', generation=result)
    return plan


def cmd_status(args) -> dict:
    state = load_pack(args.pack)
    return {
        'pack': rel_to_root(state['pack']),
        'asset_id': state['asset']['asset_id'],
        'native_name': state['asset']['native_name'],
        'gate': state['asset']['gate'],
        'budget': budget(state),
        'receipts': receipts(state['pack']),
        'repair_prepared': (state['pack'] / 'repair').is_dir(),
        'calls': [{k: c.get(k) for k in ('call_index', 'attempt', 'outcome', 'review_source',
                                         'codex_session_id', 'failure')}
                  for c in past_calls(state['pack'])],
        'generated_root': str(GENERATED_ROOT),
    }


def cmd_recover(args) -> dict:
    """Re-gate and record an already-generated artifact whose earlier rejection
    came from a wrapper bug (provenance path not echoed, or a gate threshold that
    was later corrected). It does NOT run codex again and does NOT add a call:
    that would waste the subscription on an image we already own. Refuses once a
    receipt exists, refuses a call that is already recorded, and re-checks the
    artifact with the current gate before recording. The recovery reason and the
    prior rejection are written into the call ledger."""
    state = load_pack(args.pack)
    pack, asset = state['pack'], state['asset']
    if receipts(pack):
        raise WrapperError('任务包已有回执；recover 只用于还没有入库回执的已发起调用。')
    if not str(args.reason).strip():
        raise WrapperError('recover 必须写明恢复原因（原拒绝为何是工具缺陷）。')
    call = ledger_dir(pack) / args.call
    if not call.is_dir():
        raise WrapperError(f'没有这次调用的记账目录：{call}')
    record = json.loads((call / 'call.json').read_text())
    if record.get('asset_id') != asset['asset_id']:
        raise WrapperError('记账调用的 asset_id 与任务包不一致。')
    previous = record.get('outcome')
    if previous == 'recorded' or previous == 'recovered-recorded':
        raise WrapperError('该调用已经入库，拒绝重复 recover。')
    provenance = record.get('provenance') or {}
    original = provenance.get('resolved_path')
    fresh = provenance.get('new_files_during_call') or []
    if not original and len(fresh) == 1:
        original = fresh[0]
    if not original:
        raise WrapperError('这次调用没有可恢复的产物路径。')
    original = Path(original).resolve()
    if (not original.is_relative_to(GENERATED_ROOT.resolve())
            or not GENERATED_NAME.fullmatch(original.name) or not original.is_file()):
        raise WrapperError(f'产物不在可信溯源目录或已不存在：{original}')
    with tempfile.TemporaryDirectory(prefix='run-imagegen-recover-') as scratch:
        gate_result = gate_master(original, asset['kind'], asset['asset_id'],
                                  Path(scratch) / f'export-{EXPORT_SIZE}.png')
    if not gate_result['passed']:
        raise WrapperError(f'恢复失败：当前门控仍不通过：{blocking_details(gate_result)}')
    target = args.saved if args.saved.is_absolute() else (ROOT / args.saved)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(original, target)
    try:
        receipt = art_tasks.record(pack, original, target, 1)
    except (ValueError, KeyError, OSError) as exc:
        raise WrapperError(f'art_tasks.py record 拒收：{exc}')
    record.update(outcome='recovered-recorded', recovery={
        'reason': args.reason,
        'previous_outcome': previous,
        'previous_failure': record.get('failure'),
        'saved_output_path': receipt['saved_output_path'],
        'timestamp': now(),
    })
    write_ledger(pack, call, record)
    return {'mode': 'recover', 'pack': rel_to_root(pack), 'call': rel_to_root(call),
            'original': str(original), 'receipt': receipt, 'gate_passed': True}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--codex-bin', help='codex CLI 路径（默认 $CODEX_BIN 或 PATH）')
    parser.add_argument('--codex-sandbox', default='read-only',
                        choices=('read-only', 'workspace-write', 'danger-full-access'),
                        help='codex 沙箱；默认 read-only，让 agent 无法自己写图再冒充产物')
    # 2026-09-30 起固定 gpt-6.1-sol（用户决定：与此前默认 gpt-6-astra 三组对比无明显差异，价格更低）。
    # 此前 399 次调用未指定模型，实际为 codex 默认 gpt-6-astra。
    parser.add_argument('--model', default=DEFAULT_MODEL, help=f'codex 模型（默认 {DEFAULT_MODEL}）')
    parser.add_argument('--no-ephemeral', dest='ephemeral', action='store_false',
                        help='保留 codex 会话文件（默认带 --ephemeral，不写 ~/.codex/sessions）')
    parser.add_argument('--timeout', type=int, default=1200, help='单次 codex 调用超时秒数')
    parser.add_argument('--execute', action='store_true',
                        help='真正发起生成并消耗订阅额度；缺省是 dry-run')
    commands = parser.add_subparsers(dest='command', required=True)

    gen = commands.add_parser('generate', help='按任务包的 imagegen-request.json 生成一次')
    gen.add_argument('pack', type=Path)
    gen.add_argument('--saved', type=Path, help='母版入库路径，art/<batch>/masters/<id>-vN.png')
    gen.add_argument('--attempt', type=int, help='显式指定 attempt，必须与推断值一致')
    gen.add_argument('--request', type=Path, help='自检用：改用指定的请求文件')
    gen.add_argument('--no-record', action='store_true',
                     help='自检用：只跑到门控，不入库、不写 art_tasks 回执')
    gen.set_defaults(func=cmd_generate)

    rep = commands.add_parser('repair', help='用门控实测值自动填 review 并发起一次定向返修')
    rep.add_argument('pack', type=Path)
    rep.add_argument('--saved', type=Path, help='默认由首轮母版名推导 -v2.png')
    # 返修复用 run_chain，后者会读这几个只属于 generate 的开关。
    rep.set_defaults(func=cmd_repair, request=None, no_record=False, attempt=None)

    sta = commands.add_parser('status', help='看任务包的回执、返修与调用预算')
    sta.add_argument('pack', type=Path)
    sta.set_defaults(func=cmd_status)

    rec = commands.add_parser('recover', help='门控/溯源缺陷后重新门控并入库已生成的产物（不重新调用 codex）')
    rec.add_argument('pack', type=Path)
    rec.add_argument('--call', required=True, help='记账目录名，如 call-1')
    rec.add_argument('--saved', type=Path, required=True)
    rec.add_argument('--reason', required=True, help='原拒绝为何是工具缺陷')
    rec.set_defaults(func=cmd_recover, request=None, no_record=False, attempt=None)

    args = parser.parse_args(argv)
    try:
        result = args.func(args)
    except (WrapperError, check_token_style.StyleCheckError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        return 1
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as exc:
        print(f'ERROR: {type(exc).__name__}: {exc}', file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
