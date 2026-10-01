#!/usr/bin/env python3
"""棋子贴图风格一致性门控（只读检查器）。

本工具只读取 PNG 并计算数值，不写入、不修改、不重绘任何美术资产。
它把"底盘几何与底盘明度"这一条已被验证的漂移，固化成可复现的判据，
避免后续新生成的贴图重复已经发生过的风格漂移。

用法：

    python3 tools/check_token_style.py check data/gfx/tokens/fox.png \\
        --master art/monsters-v2/masters/fox-v1.png
    python3 tools/check_token_style.py report
    python3 tools/check_token_style.py report --json
    python3 tools/check_token_style.py baseline
    python3 tools/check_token_style.py baseline --recompute data/gfx/tokens

退出码：0 全部通过（可含警告）；1 存在阻断项；2 用法/读取错误。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNTIME_TOKENS = ROOT / 'data/gfx/tokens'

# --------------------------------------------------------------------------
# 度量常量
# --------------------------------------------------------------------------
# 运行贴图边长。C 导出器（tools/export_token.c）把可见包围盒缩放到画布的
# target_occupancy=0.86，因此底盘外缘半径在各款之间本来就应当一致。
TOKEN_SIZE = 128
# 底盘外缘环带。归一化半径 d = hypot(x+0.5-64, y+0.5-64)/64。
# 0.72–0.84 这一段落在圆盘斜边的外侧、主体轮廓的外侧，是"纯底盘"区域。
RING_INNER = 0.72
RING_OUTER = 0.84
# 只统计不透明像素，避免把抗锯齿边缘的半透明像素算进明度。
ALPHA_FLOOR = 128
# 8 个角度扇区。扇区 0 从左侧（-x 方向）起、顺时针推进：
# ang = (atan2(dy, dx) + pi) / (2*pi)，sector = min(7, int(ang * 8))。
SECTORS = 8

# 判据阈值
MAX_DISC_RADIUS = 0.867      # 阻断：最大不透明半径
DRIFT_TOLERANCE = 8.0        # 阻断：底盘偏移中位的绝对值上限
INTRUSION_TOLERANCE = 20.0   # 警告：单扇区相对本款中位的上偏
MASTER_ALPHA_MAX_FLOOR = 240 # 母版 alpha 上限的容差（原生输出可能为 252）
NEAR_THRESHOLD_MARGIN = 1.0  # 报告模式中标记"逼近阈值"的余量

# --------------------------------------------------------------------------
# 冻结基线（禁止运行时重算）
# --------------------------------------------------------------------------
# 这 8 个数是**写死的常量**，不是每次运行从当前贴图集合算出来的。
#
# 为什么必须冻结：若基线随贴图集合重算，每加入一张有漂移的新图，都会把
# 基线朝这张图的方向拉一点；跑够多批之后门控就会被它本该拦截的资产驯化，
# 判据自我失效。这是典型的反馈回路失效，必须用常量切断。
#
# 重算基线的唯一合法时机：对**现有**美术开返修批次并整体重导之后，由人
# 决定重算，用 `baseline --recompute` 打印新值、人工核对、再修改本常量并
# 同步更新下面的溯源块。日常新增资产一律不重算。
BASELINE_SECTOR_MEDIANS = (
    72.09,  # S0 左
    71.16,  # S1 左上
    64.66,  # S2 上
    62.97,  # S3 右上
    65.21,  # S4 右
    67.05,  # S5 右下
    74.33,  # S6 下
    76.42,  # S7 左下
)

BASELINE_PROVENANCE = {
    'frozen_on': '2026-09-27',
    'method': (
        '对 37 款运行贴图各自求 8 扇区不透明像素亮度中位数，再对每个扇区'
        '跨 37 款取中位数。亮度 L = 0.299R + 0.587G + 0.114B。'
    ),
    'sample_size': 37,
    'source_dir': 'data/gfx/tokens',
    'token_manifest_sha256': 'ece656b24e30e045dfc36d80c5bd369c1a5e0ca4fc38e02023e0ad8d56f10315',
    'token_manifest_path': 'data/token-manifest.json',
    'addon_version_at_freeze': '0.6.3',
    'rebaseline_policy': (
        '仅在对现有美术开返修批次并整体重新导出之后才允许重算；'
        '重算须由人核对 `baseline --recompute` 的输出后手工改常量，'
        '并在此处更新日期、样本数与 manifest 哈希。新增资产不触发重算。'
    ),
    'exclusions': '以下划线开头的 UI 遮罩（_relation-* / _shield-* / _badge-* / _health-band / _player-inner）不是生物美术，不参与基线。',
}

# --------------------------------------------------------------------------
# 既有资产豁免名单（grandfather）
# --------------------------------------------------------------------------
# 冻结基线当天，这 37 款已在运行包里；其中 11 款按 [-8,+8] 口径不合规。
# 用户已决定**本轮不返修**，因此门控只对新资产生效，对下列 id 放行。
#
# 名单显式列出且带当时实测值与运行 PNG 的 SHA-256，可审计：
#   (底盘偏移中位, 最大扇区上偏, 最大不透明半径, runtime png sha256)
# 放行按 id 生效（重新编译导出器后字节可能不同，不能以哈希为放行条件），
# 但字节或数值变化会在报告中被指出，不会被静默吞掉。
# 一旦某款返修达标，应把它从本名单删除，而不是留着继续豁免。
GRANDFATHERED = {
    'bandit': (-2.68, 3.76, 0.8559, 'c070e17287889e479e5cd6771283ffaf97eb2dc25e5c0f6660f5b39dd3043405'),
    'bee-swarm': (0.08, 8.36, 0.8610, '617bf68d9d71189ecc7cbc8256dcb890109d8edae6594ed2d5dccec5454bf7fc'),
    'bill': (-2.55, 19.96, 0.8585, '41543243196311517082c546e74b5502b8edbd8a7aab9646547ff3aa19cf91da'),
    'black-bear': (10.28, 11.54, 0.8655, '6c91bbefa57970e8bdca63df08c68d0ef6f98de13a5b1e1bdfa39d1e4f8a915a'),
    'brown-bear': (-0.61, 4.58, 0.8652, 'e9320eb860cfbb1f1d7c3bbbf98c9cfa8a35514dd3e9752aca064af18cf7cf74'),
    'brown-rat': (13.62, 20.57, 0.8585, '3be5bbbfeeb11466d57d3d8571b9815c3cab6d6a63db1c57051e54277b6e4c33'),
    'brown-snake': (-7.57, 15.02, 0.8636, 'f94df9fa12fff8941a3a1b382314810676980eef72af4c321753ca3119ffb258'),
    'cave-troll': (-7.61, 9.51, 0.8610, '77d9b1435e549729989353fd90e2a8fa3ed56fd2a48822299363ab229408bfe5'),
    'copperhead-snake': (6.39, 5.45, 0.8599, 'f42420a47768244a5ea49a50cb5a2d69ab1440ed4bf4852ae01d6b95d77bf68c'),
    'cutpurse': (-1.69, 4.93, 0.8576, 'bea7aa68b0e74e2a852344666fdabbbb3b73860ffb1fe309412ecf7ec71a0793'),
    'degenerated-skeleton-archer': (-8.48, 3.74, 0.8562, '1b2ae07794f4852f3962d7e514b3abf3c433417cbe3c56d4f6d2931af03ca85a'),
    'degenerated-skeleton-warrior': (-2.87, 4.90, 0.8599, 'a01bf214f261358bd6c57fcb09f287593cc156ed657d05c1302ee1e64c798f88'),
    'dire-wolf': (8.07, 6.74, 0.8576, 'd1bba94a9cba2a01e47013e398c5ab80537dce0c48a0795aeafcf48632c7910e'),
    'dragon-turtle': (-3.79, 6.12, 0.8585, '6215d177556f6aef9aca99ea2d8a591be5194e35d211a6ed2a02f0d98757b9c2'),
    'forest-troll': (-12.45, 34.93, 0.8579, '474ccc6cc0eafa81aa27acf696a2efca7307bcc55fa7dd55adcb3cbae9e82fb4'),
    'fox': (6.46, 16.06, 0.8604, 'bb1b2c92d3d75edaa3bd89e497f2f2020bdf9a1388700c40ff61df242327ec1d'),
    'giant-eel': (-5.34, 6.89, 0.8604, '3d7161da0e9308a93202d3bb803a41c7020cac20eb492a2fccea1886cad9d903'),
    'giant-grey-rat': (5.33, 2.62, 0.8604, 'd9b9e1c8899396f02a90d4d6708de1b8712da480181afa601cb14b52d99648d6'),
    'giant-white-rat': (8.32, 4.38, 0.8576, '9d4bac0e58c07d8da690687d6c748cfc15ddd55581e7f8bce7b93923eb50f1f7'),
    'great-wolf': (6.36, 4.38, 0.8604, '3c00d849c122fa611abb248336766611b9b35976c153813571160dc402174741'),
    'green-worm-mass': (3.25, 4.90, 0.8599, '60f7932c1c54a323c174b6f497c6607ae26baeaf63e2ebe826ae571c08d4f6d1'),
    'grey-mold': (-9.17, 7.96, 0.8576, '5c33de41016595d8c3f0203e5b2088eaf79bf9e75e0f7199905d480b9dd79fc0'),
    'hornet-swarm': (7.64, 8.36, 0.8576, '19f642deae5ba15a2f41f4c89cdb722ff0c87256395b10fc6732768bf6041e42'),
    'king-cobra': (1.10, 4.56, 0.8596, '278f4f1ff76afc2ffd51ca0882e1159adc1a2497e54f2bbfdcbffe3325454609'),
    'midge-swarm': (16.90, 7.69, 0.8576, '2376ff1dd46628c9433f817a909fda54a5c5df54c27aed1072253f0b656b842a'),
    'prox': (-12.91, 5.30, 0.8585, '1efb487e858d0f7f585eea20388e84c05ba854576941e84bcd424e69b6af118d'),
    'rattlesnake': (-4.94, 5.19, 0.8585, '23c6c8ea5cc45262b2fdc9d6fdf22f506f078f85529d2d802d70433a0a78ab79'),
    'rogue': (0.90, 4.44, 0.8576, 'd157c696914c6a28c42e1dcfcde64ee75815b61c76c9021ed90c51eb130d3856'),
    'skeleton-mage': (-5.53, 5.95, 0.8576, '49f2d7cc8f25596469983b3e95fcc4e4eafe39ca3cdccc2c4e722f2ed54edb05'),
    'stone-troll': (-12.76, 12.31, 0.9047, '06d2c60ee3cc58657cacd30e092351faea6b821ab17c2b2a0d0a42d448ac5e03'),
    'thief': (-3.11, 4.92, 0.8576, '85d491efdc3cbabd3788b18a6ca4afeb38b0cf869ae9d58778e9ab928e0399e5'),
    'venus-flytrap': (2.52, 21.04, 0.8576, 'cbed86869610e30e1f1f5fdb39f58ad94bb9a8a9eb608eb61cf6b5397fd81b6f'),
    'warg': (9.32, 9.57, 0.8585, '3891d495c890686880c3f7d119a21dae0af87819dd62356d167375d9a26c1230'),
    'white-snake': (0.80, 6.13, 0.8576, '9b48deebe113292a5ea9c8bfb6f07eaf018073d3ea2cd62e18ed70b6108c5e5e'),
    'white-wolf': (7.93, 17.57, 0.8585, '98366ca2384f30bc4f6c36350eae71f131b78e0cf1295a9eb099f575ea01fb5e'),
    'white-worm-mass': (-2.26, 15.49, 0.8585, '55671a39ff9388694837a3a72073a516196d8401dfa0bb807a374b34a442efc8'),
    'wolf': (-0.16, 3.42, 0.8576, '782857cb4784c71367100b69ee3c734423e74f431d032bcdd1a3ed7e893b1da4'),
}
# 豁免只覆盖这两项几何/明度历史欠账。母版原生 alpha 与四角透明属于
# 机械正确性，既有 37 款本来就全部通过，任何情况下都不放行。
WAIVABLE_CHECKS = frozenset({'disc_overflow', 'base_drift'})
GRANDFATHER_NOTE = (
    '2026-09-27 冻结：用户决定本轮不对既有 37 款开返修批次，'
    '门控只对新加入的资产生效。'
)


class StyleCheckError(Exception):
    """无法完成度量（文件缺失、尺寸不符等），与"度量后判定不合格"区分开。"""


def _load_rgba(path: Path):
    from PIL import Image  # 只读检查，不 save/resize/recolor。
    with Image.open(path) as image:
        fmt, mode = image.format, image.mode
        transparency = 'transparency' in image.info
        rgba = image.convert('RGBA')
        rgba.load()
    return rgba, fmt, mode, transparency


def measure_token(path: Path) -> dict:
    """计算一张 128px 运行贴图的几何与底盘明度指标。只读。"""
    image, _fmt, _mode, _tr = _load_rgba(path)
    if image.size != (TOKEN_SIZE, TOKEN_SIZE):
        raise StyleCheckError(f'运行贴图必须是 {TOKEN_SIZE}x{TOKEN_SIZE}：{path} 实为 {image.size}')
    pixels = image.load()
    half = TOKEN_SIZE / 2
    buckets: list[list[float]] = [[] for _ in range(SECTORS)]
    max_radius = 0.0
    for y in range(TOKEN_SIZE):
        for x in range(TOKEN_SIZE):
            red, green, blue, alpha = pixels[x, y]
            if alpha < ALPHA_FLOOR:
                continue
            dx = x + 0.5 - half
            dy = y + 0.5 - half
            distance = math.hypot(dx, dy) / half
            if distance > max_radius:
                max_radius = distance
            if RING_INNER <= distance <= RING_OUTER:
                angle = (math.atan2(dy, dx) + math.pi) / (2 * math.pi)
                sector = min(SECTORS - 1, int(angle * SECTORS))
                buckets[sector].append(0.299 * red + 0.587 * green + 0.114 * blue)
    empty = [i for i, bucket in enumerate(buckets) if not bucket]
    if empty:
        raise StyleCheckError(f'外环扇区 {empty} 没有不透明像素，底盘不完整或已被裁切：{path}')
    sector_medians = [statistics.median(bucket) for bucket in buckets]
    offsets = [value - BASELINE_SECTOR_MEDIANS[i] for i, value in enumerate(sector_medians)]
    # 第 5 步取**中位**而非均值：对 1–2 个被主体侵入或接触阴影污染的扇区免疫。
    drift = statistics.median(offsets)
    intrusion = max(offset - drift for offset in offsets)
    corner_alpha = [pixels[p][3] for p in ((0, 0), (TOKEN_SIZE - 1, 0),
                                           (0, TOKEN_SIZE - 1), (TOKEN_SIZE - 1, TOKEN_SIZE - 1))]
    return {
        'path': str(path),
        'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
        'sector_medians': [round(v, 2) for v in sector_medians],
        'sector_offsets': [round(v, 2) for v in offsets],
        'base_drift': round(drift, 2),
        'max_sector_intrusion': round(intrusion, 2),
        'max_opaque_radius': round(max_radius, 4),
        'corner_alpha': corner_alpha,
        'ring_samples': [len(b) for b in buckets],
    }


def measure_master(path: Path) -> dict:
    """检查母版的原生透明通道。只读。

    这不是形式检查：本机 ImageGen 在提示词没有明确要求透明时会返回不含
    alpha 的 RGB 图，而 art/production/README.md 明确禁止"抠白底冒充原生
    alpha"。RGB 图经 convert('RGBA') 后 alpha 恒为 255，必须在转换前拦住。
    """
    image, fmt, mode, transparency = _load_rgba(path)
    alpha = image.getchannel('A')
    low, high = alpha.getextrema()
    native = mode in ('RGBA', 'LA', 'PA') or (mode == 'P' and transparency)
    return {
        'path': str(path),
        'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
        'format': fmt,
        'mode': mode,
        'native_alpha_channel': native,
        'alpha_min': low,
        'alpha_max': high,
        'size': list(image.size),
    }


def _finding(check, level, ok, detail, **extra):
    return dict(check=check, level=level, ok=ok, detail=detail, **extra)


def evaluate(token_metrics: dict | None, master_metrics: dict | None = None) -> list[dict]:
    """把实测值翻译成判定项。level 为 blocking 或 warning。"""
    findings = []
    if master_metrics is not None:
        native = master_metrics['native_alpha_channel']
        low, high = master_metrics['alpha_min'], master_metrics['alpha_max']
        ok = native and low == 0 and high >= MASTER_ALPHA_MAX_FLOOR
        findings.append(_finding(
            'master_native_alpha', 'blocking', ok,
            f"母版 mode={master_metrics['mode']} alpha={low}..{high}"
            + ('' if ok else '；需要 RGBA 原生 alpha 且取值跨 0..255'
                             f'（上限容差 {MASTER_ALPHA_MAX_FLOOR}，禁止抠白底冒充）'),
            mode=master_metrics['mode'], alpha_min=low, alpha_max=high))
    if token_metrics is None:
        return findings
    radius = token_metrics['max_opaque_radius']
    findings.append(_finding(
        'disc_overflow', 'blocking', radius <= MAX_DISC_RADIUS,
        f'最大不透明半径 {radius:.3f}（上限 {MAX_DISC_RADIUS}）',
        value=radius, limit=MAX_DISC_RADIUS))
    drift = token_metrics['base_drift']
    findings.append(_finding(
        'base_drift', 'blocking', abs(drift) <= DRIFT_TOLERANCE,
        f'底盘偏移中位 {drift:+.2f}（容差 ±{DRIFT_TOLERANCE:g}）',
        value=drift, limit=DRIFT_TOLERANCE))
    intrusion = token_metrics['max_sector_intrusion']
    findings.append(_finding(
        'subject_intrusion', 'warning', intrusion <= INTRUSION_TOLERANCE,
        f'单扇区相对本款中位最大上偏 {intrusion:+.2f}（容差 +{INTRUSION_TOLERANCE:g}）',
        value=intrusion, limit=INTRUSION_TOLERANCE))
    corners = token_metrics['corner_alpha']
    findings.append(_finding(
        'corner_alpha', 'blocking', not any(corners),
        f'四角 alpha {corners}', value=corners))
    return findings


def check_asset(token_path: Path | None, master_path: Path | None = None,
                asset_id: str | None = None, allow_grandfather: bool = True) -> dict:
    """对单个资产做完整判定，返回可序列化结果。不写任何文件。"""
    token_metrics = measure_token(token_path) if token_path is not None else None
    master_metrics = measure_master(master_path) if master_path is not None else None
    if asset_id is None:
        source = token_path if token_path is not None else master_path
        asset_id = source.stem if source is not None else '<unnamed>'
    findings = evaluate(token_metrics, master_metrics)
    blocking = [f for f in findings if f['level'] == 'blocking' and not f['ok']]
    warnings = [f for f in findings if f['level'] == 'warning' and not f['ok']]
    record = GRANDFATHERED.get(asset_id) if allow_grandfather else None
    waived = bool(blocking) and record is not None and all(
        f['check'] in WAIVABLE_CHECKS for f in blocking)
    notes = []
    # New-art exceptions are bound to both source and exported bytes. They do
    # not inherit the id-only historical policy above, and never excuse alpha,
    # disc geometry or an unrelated finding.
    waiver_dir = Path(__file__).resolve().parents[1] / 'art/production/waivers'
    for batch in ('monster-batch-a', 'monster-batch-b', 'monster-batch-d', 'monster-batch-e', 'monster-batch-f', 'monster-batch-g', 'monster-batch-h', 'monster-batch-i', 'monster-batch-j', 'monster-batch-k', 'monster-batch-l', 'monster-batch-m', 'monster-batch-n', 'monster-batch-o', 'monster-batch-p', 'monster-batch-q', 'monster-batch-r', 'monster-batch-s', 'monster-batch-t', 'monster-batch-u', 'monster-batch-v', 'monster-batch-w', 'monster-batch-x', 'monster-batch-y', 'monster-batch-z', 'monster-batch-aa', 'monster-batch-ab', 'monster-batch-ac', 'monster-batch-ad', 'monster-batch-ae', 'monster-batch-af'):
        waiver_path = waiver_dir / (batch + '.json')
        if not (blocking and token_metrics is not None and waiver_path.is_file()):
            continue
        for exception in json.loads(waiver_path.read_text())['assets']:
            if (exception['id'] == asset_id
                and exception['runtime_sha256'] == token_metrics['sha256']
                and (master_metrics is None or exception['master_sha256'] == master_metrics['sha256'])
                and exception['base_drift'] == token_metrics['base_drift']
                and [f['check'] for f in blocking] == exception['waived_checks']):
                waived = True
                notes.append('Exact-byte ' + batch + ' exception: ' + exception['reason'])
                break
    if record is not None:
        if token_metrics is not None:
            if token_metrics['sha256'] != record[3]:
                notes.append('豁免名单记录的字节已变化：名单按 id 放行，但请人工确认这次改动是有意的返修。')
            for label, index, current in (('底盘偏移', 0, token_metrics['base_drift']),
                                          ('扇区上偏', 1, token_metrics['max_sector_intrusion']),
                                          ('最大半径', 2, token_metrics['max_opaque_radius'])):
                if abs(current - record[index]) > 0.05:
                    notes.append(f'{label}由 {record[index]} 变为 {current}。')
        if not blocking:
            notes.append('本款现已满足全部阻断判据，可从 GRANDFATHERED 名单中移除。')
    return {
        'asset_id': asset_id,
        'token': token_metrics,
        'master': master_metrics,
        'findings': findings,
        'blocking': [f['check'] for f in blocking],
        'warnings': [f['check'] for f in warnings],
        'grandfathered': record is not None,
        'waived': waived,
        'notes': notes,
        'passed': not blocking or waived,
    }


def gate(token_path: Path | None, master_path: Path | None = None,
         asset_id: str | None = None, allow_grandfather: bool = True) -> dict:
    """阻断门控入口：不合格且不在豁免名单时抛 StyleCheckError。

    供 tools/build_monster_art.py 在 128px 导出之后调用。
    """
    result = check_asset(token_path, master_path, asset_id, allow_grandfather)
    if not result['passed']:
        detail = '；'.join(f['detail'] for f in result['findings']
                           if f['level'] == 'blocking' and not f['ok'])
        raise StyleCheckError(f"{result['asset_id']} 未通过棋子风格门控：{detail}")
    return result


# --------------------------------------------------------------------------
# 命令行
# --------------------------------------------------------------------------
def runtime_token_paths(directory: Path):
    """运行目录下的生物贴图；以下划线开头的是程序生成的 UI 遮罩，排除。"""
    return sorted(p for p in directory.glob('*.png') if not p.name.startswith('_'))


def _status(result):
    if result['blocking']:
        return 'WAIVED' if result['waived'] else 'FAIL'
    return 'WARN' if result['warnings'] else 'PASS'


def cmd_check(args):
    try:
        result = check_asset(args.token, args.master, args.id, not args.no_grandfather)
    except StyleCheckError as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"{result['asset_id']}  {_status(result)}")
        for finding in result['findings']:
            mark = 'ok  ' if finding['ok'] else ('阻断' if finding['level'] == 'blocking' else '警告')
            print(f"  [{mark}] {finding['check']}: {finding['detail']}")
        for note in result['notes']:
            print(f'  注: {note}')
        if result['waived']:
            print('  豁免: ' + (GRANDFATHER_NOTE if result['grandfathered'] else 'exact-byte batch exception'))
    return 0 if result['passed'] else 1


def cmd_report(args):
    paths = runtime_token_paths(args.tokens)
    if not paths:
        print(f'ERROR: {args.tokens} 下没有生物贴图', file=sys.stderr)
        return 2
    rows, failures = [], 0
    for path in paths:
        try:
            result = check_asset(path, None, path.stem, not args.no_grandfather)
        except StyleCheckError as exc:
            print(f'ERROR: {exc}', file=sys.stderr)
            return 2
        rows.append(result)
        if not result['passed']:
            failures += 1
    rows.sort(key=lambda r: r['token']['base_drift'])
    if args.json:
        print(json.dumps({
            'baseline': list(BASELINE_SECTOR_MEDIANS),
            'baseline_provenance': BASELINE_PROVENANCE,
            'thresholds': {'max_opaque_radius': MAX_DISC_RADIUS,
                           'base_drift': DRIFT_TOLERANCE,
                           'subject_intrusion': INTRUSION_TOLERANCE},
            'grandfather_note': GRANDFATHER_NOTE,
            'count': len(rows), 'blocking_assets': failures,
            'assets': rows}, ensure_ascii=False, indent=2))
        return 0 if failures == 0 else 1
    print(f'棋子风格报告：{len(rows)} 款  目录 {args.tokens}')
    print(f'冻结基线 S0..S7 = ' + ' '.join(f'{v:.2f}' for v in BASELINE_SECTOR_MEDIANS))
    print(f'判据：|底盘偏移| <= {DRIFT_TOLERANCE:g}（阻断）；最大半径 <= {MAX_DISC_RADIUS}（阻断）；'
          f'扇区上偏 <= {INTRUSION_TOLERANCE:g}（警告）')
    print()
    print(f"{'id':30s} {'底盘偏移':>9s} {'扇区上偏':>9s} {'最大半径':>8s}  判定")
    drift_bad = over_bad = intrude_bad = 0
    for result in rows:
        token = result['token']
        flags = []
        if 'base_drift' in result['blocking']:
            flags.append('偏移越界'); drift_bad += 1
        if 'disc_overflow' in result['blocking']:
            flags.append('圆盘越界'); over_bad += 1
        if 'corner_alpha' in result['blocking']:
            flags.append('四角不透明')
        if 'subject_intrusion' in result['warnings']:
            flags.append('主体侵入'); intrude_bad += 1
        # 逼近阈值的项单独标出，避免 19.96 这类只差一点的情况被读成"干净"。
        if 'subject_intrusion' not in result['warnings'] and \
                token['max_sector_intrusion'] > INTRUSION_TOLERANCE - NEAR_THRESHOLD_MARGIN:
            flags.append('侵入逼近阈值')
        if abs(token['base_drift']) > DRIFT_TOLERANCE - NEAR_THRESHOLD_MARGIN and \
                'base_drift' not in result['blocking']:
            flags.append('偏移逼近阈值')
        if result['waived']:
            flags.append('已豁免')
        print(f"{result['asset_id']:30s} {token['base_drift']:+9.2f} "
              f"{token['max_sector_intrusion']:+9.2f} {token['max_opaque_radius']:8.3f}  "
              f"{_status(result):6s} {'，'.join(flags)}")
        # 只在有旗标时打印逐条注记，避免把"已达标"刷满整张表。
        if flags:
            for note in result['notes']:
                print(f'{"":30s} 注: {note}')
    print()
    print(f'底盘偏移不合规 {drift_bad} 款；圆盘越界 {over_bad} 款；主体侵入警告 {intrude_bad} 款；'
          f'未豁免的阻断资产 {failures} 款')
    if not args.no_grandfather:
        print(f'豁免名单共 {len(GRANDFATHERED)} 款 —— {GRANDFATHER_NOTE}')
        clean = [r['asset_id'] for r in rows
                 if r['grandfathered'] and not r['blocking'] and not r['warnings']]
        if clean:
            print(f'其中 {len(clean)} 款现已满足全部阻断判据、无警告，可从名单移除：'
                  + ' '.join(sorted(clean)))
        print('用 --no-grandfather 查看不带豁免的原始判定，供将来决定是否开返修批次。')
    return 0 if failures == 0 else 1


def cmd_baseline(args):
    print('冻结基线（扇区 0 = 左，顺时针）：')
    for index, value in enumerate(BASELINE_SECTOR_MEDIANS):
        print(f'  S{index} = {value:.2f}')
    print()
    for key, value in BASELINE_PROVENANCE.items():
        print(f'{key}: {value}')
    print()
    print(f'可豁免的判据：{" ".join(sorted(WAIVABLE_CHECKS))}'
          '（master_native_alpha 与 corner_alpha 任何情况下都不放行）')
    print(f'豁免名单（{len(GRANDFATHERED)} 款）：' + ' '.join(sorted(GRANDFATHERED)))
    if args.recompute is None:
        return 0
    paths = runtime_token_paths(args.recompute)
    if not paths:
        print(f'ERROR: {args.recompute} 下没有生物贴图', file=sys.stderr)
        return 2
    print()
    print(f'从 {args.recompute} 重算（{len(paths)} 款，仅打印，不写回常量）：')
    try:
        columns = [measure_token(p)['sector_medians'] for p in paths]
    except StyleCheckError as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        return 2
    drifted = False
    for sector in range(SECTORS):
        value = statistics.median(row[sector] for row in columns)
        delta = value - BASELINE_SECTOR_MEDIANS[sector]
        if abs(delta) > 0.005:
            drifted = True
        print(f'  S{sector} = {value:6.2f}  （冻结值 {BASELINE_SECTOR_MEDIANS[sector]:6.2f}，差 {delta:+.2f}）')
    print('重算值与冻结值一致。' if not drifted else
          '重算值与冻结值不同。只有在对现有美术开过返修批次并整体重导之后，'
          '才由人决定是否手工更新常量与溯源块；新增资产绝不因此重算。')
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest='command', required=True)

    check = commands.add_parser('check', help='检查单个资产')
    check.add_argument('token', type=Path, nargs='?', default=None, help='128px 运行贴图')
    check.add_argument('--master', type=Path, default=None, help='可选，对应母版 PNG')
    check.add_argument('--id', default=None, help='资产 id，默认取贴图文件名')
    check.add_argument('--json', action='store_true')
    check.add_argument('--no-grandfather', action='store_true', help='忽略既有资产豁免名单')
    check.set_defaults(func=cmd_check)

    report = commands.add_parser('report', help='对整个运行目录出报告')
    report.add_argument('--tokens', type=Path, default=RUNTIME_TOKENS)
    report.add_argument('--json', action='store_true')
    report.add_argument('--no-grandfather', action='store_true')
    report.set_defaults(func=cmd_report)

    baseline = commands.add_parser('baseline', help='打印冻结基线与溯源')
    baseline.add_argument('--recompute', type=Path, default=None,
                          help='从给定目录重算并与冻结值对比；只打印，不写回')
    baseline.set_defaults(func=cmd_baseline)

    args = parser.parse_args(argv)
    if args.command == 'check' and args.token is None and args.master is None:
        parser.error('check 至少需要一个贴图或 --master')
    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
