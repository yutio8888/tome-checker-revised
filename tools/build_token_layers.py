#!/usr/bin/env python3
"""Build the 1.25x layered small-tile trial assets.

This tool produces the shared empty disc (data/gfx/tokens-layer/_disc.png) and
one creature cut-out per trial token (data/gfx/tokens-layer/<id>.png), plus the
source copies, aligned masks and provenance records under art/token-layers/.

It is DETERMINISTIC but NOT self-contained: it needs the private R30 virtualenv
that carries rembg + the BiRefNet model, e.g.

    <workspace>/tmp/rotation/R30-scratch/venv/bin/python \
        tools/build_token_layers.py

The BiRefNet foreground pass is cached under art/token-layers/, so re-running the
tool reproduces the runtime files from the committed sources. This tool must
never run from packaging or the test suite; the shipped PNGs are the product.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image
# scipy is only needed by the disc/alpha cleaning passes, not by build_aura.
# Import it lazily so the pure pass can be imported (and unit-tested) without
# the private R30 venv; a call site that needs it raises the normal ImportError.
try:
    from scipy import ndimage
    from scipy.ndimage import map_coordinates
except ImportError:  # pragma: no cover - only in a scipy-less test interpreter
    ndimage = None
    map_coordinates = None

ROOT = Path(__file__).resolve().parents[1]
TOKENS_LUA = ROOT / 'overload/mod/class/CheckerTokens.lua'
MANIFEST = ROOT / 'data/token-manifest.json'
RUNTIME_DIR = ROOT / 'data/gfx/tokens-layer'
AURA_DIR = RUNTIME_DIR / 'aura'
ART = ROOT / 'art/token-layers'
SIZE = 128
# R38: standee layers ship on a 256px canvas so a 1.85-cell standee at a 128px
# tile is not upscaled. Ordinary R32 layers stay on the 128px canvas because
# they are only drawn at <=48px cells. The shared disc stays 128px.
STANDEE_SIZE = 256
# R42: the shader aura samples the creature's alpha-distance field (SDM). The
# awesomeaura shader draws the flame pattern over the aura quad, so the quad
# DIAGONAL sets the flame size: R41 padded the aura 128px on EVERY side, which
# made the aura quad 3.27x3.27 cells (diagonal 4.63 cells) and the flames about
# 2x a native 1x2 tall sprite (diagonal 2.24 cells). Pad mainly at the TOP
# instead: the aura quad is the BODY height plus AURA_HEADROOM_CELLS above
# body_top, floored at AURA_MIN_QUAD_CELLS, giving a diagonal of ~2.33-2.55
# cells for the four shipped standees (a native 1x2 tall sprite is 2.24).
# The aura texture is a POT square holding the layer scaled to that quad, so
# the creature still lines up exactly with the creature quad.
AURA_HEADROOM_CELLS = 0.4
# R50 approved design: one shared live floor plus animation-tip budget.
_AURA_CONTRACT = json.loads((ROOT / 'tools/standee_aura_contract.json').read_text())
AURA_FLAME_ABOVE_TOP_FLOOR_CELLS = _AURA_CONTRACT['AURA_FLAME_ABOVE_TOP_FLOOR_CELLS']
AURA_TIP_BUDGET_CELLS = _AURA_CONTRACT['AURA_TIP_BUDGET_CELLS']
AURA_GATE_HEADROOM_CELLS = AURA_FLAME_ABOVE_TOP_FLOOR_CELLS + AURA_TIP_BUDGET_CELLS
# The SDM shader normalises its distance field by the aura texture diagonal, so
# the quad diagonal -- not the quad side -- sets the flame size. A native 1x2
# tall sprite (the shockbolt `nice_tile tall=1` body) has diagonal
# sqrt(1^2 + 2^2) = sqrt(5) = 2.236 cells; a square quad with that same
# diagonal has side sqrt(5)/sqrt(2) = sqrt(2.5) = 1.581 cells. A small body
# (ogre-guard's 1.078125-cell body after the body-top rule) would otherwise
# give a body + headroom quad of only 1.478 cells (diagonal 2.09), drawing the
# SDM flames below native size, so the quad is floored at the native-diagonal
# square. The creature still maps onto the creature quad because the layer is
# scaled into the aura canvas and the extra space is transparent headroom.
AURA_MIN_QUAD_CELLS = 1.5811388300841898  # sqrt(2.5): square with diagonal sqrt(5)
AURA_CANVAS = 256
# R46 tall aura: a body + headroom quad whose diagonal would exceed
# AURA_TALL_DIAG_CELLS is not a square near native size. Use a 1:2 POT texture
# instead (128x256, isotropic, sdm_double=false): h = max(H, AURA_TALL_MIN_CELLS)
# and w = h/2, so the quad diagonal is h*sqrt(5)/2, within [sqrt(5), 2.25*sqrt(5)/2] for
# the shipped maximum art height 1.75 plus 0.50 headroom: h <= 2.25. The engine maps the whole texture (Entity.lua:416-436) and the SDM
# distances/angles are in texture pixels (src/core_lua.c:1531-1586), so the
# texture aspect MUST equal the quad aspect and both must stay POT.
AURA_TALL_DIAG_CELLS = 2.6
AURA_TALL_MIN_CELLS = 2.0
AURA_TALL_W, AURA_TALL_H = 128, 256
# Manual body-top review (R42/R43/R45). body_top is the y (layer px) of the top
# of the BODY: head, horns, helmets, hats, hair, raised arms, wings and fins
# count as body; raised weapons, staves, floating orbs, debris, particles,
# flames, lightning and glow do not, and neither do sparse or semi-transparent
# fringes (bristles, specks, mist, darkness shroud) - the R45 user rule, so the
# top row comes from the solid body mass (alpha > 128). Any id absent here
# defaults to its alpha top. The tool fails loudly if a key is not a shipped
# standee or if the value is outside the art. The four R43 standees:
#   ogre-guard  38  the hammer and a floating 1px speck are above the head
#   ninandra/ravenous-horror/snow-giant: alpha top is body (raised spider legs,
#                                        head fins, bald head), default.
# kra-tor is flat in R43 (its axe blade sits above a ~1-cell body), so its
# layer/aura are archived and it must not appear here.
BODY_TOP = {
    # R52: first solid horn pixel; the higher crystal staff is not body.
    'onilug': 27,
    'ogre-guard': 38,
    # R50 batch 2: exported layer coordinates, excluding the raised flame.
    'ogre-rune-spinner': 32,  # hair/head top; raised fire orb is not body
    'uruivellas': 34,  # horn tips; head flames are not body (master y ~0.074)
    # R47 batch 1: the topmost body pixel when a weapon/flame sits above the
    # head (layer px, measured on the 256px layer).
    'archlich': 26,  # staff above the head; crown top y=26
    'snow-giant-chieftain': 38,  # maul above the head; horn top y=38
    'snow-giant-boulder-thrower': 43,  # boulder above the raised fists; fist top y=43
    'celia': 35,  # staff above the head; head/hair top y=35
    'forge-giant': 40,  # head flame is not body; horn tip y=40
    'healer-astelrid': 44,  # scalpel-club above the head; head/hair top y=44
}
# Normalised disc geometry shared by every shipped 128px token (measured across
# the catalogue: cx 63.4-63.6, cy 63.4-64.6, R 54.3-54.9). Keeping it explicit
# makes the disc reproducible; the runtime never uses these numbers.
DISC_CX, DISC_CY, DISC_R = 63.9, 64.1, 54.2
MODEL = 'birefnet-general'
# 40 varied extra sources for the shared-disc median, alongside the trial set.
EXTRA_SAMPLE_IDS = [
    'brown-rat', 'giant-grey-rat', 'brown-bear', 'black-bear', 'ghoul', 'red-jelly',
    'black-jelly', 'white-crystal', 'sandworm', 'cave-troll', 'fire-drake', 'minotaur',
    'treant', 'stone-troll', 'lich', 'vampire-lord', 'ruin-banshee', 'glacial-legion',
    'void-spectre', 'dredge', 'dredge-captain', 'giant-white-ant', 'giant-blue-ant',
    'naga-tidewarden', 'naga-tidecaller', 'shivgoroth', 'greater-shivgoroth',
    'spitting-spider', 'forest-troll', 'orc-berserker', 'orc-fighter', 'bandit', 'thief',
    'assassin', 'rogue', 'orc-necromancer', 'mountain-troll', 'patchwork-troll',
    'ogre-guard', 'polar-bear',
]
# The shared disc is a frozen artifact: its per-pixel median was taken over the
# original 20 R32 ordinary ids plus EXTRA_SAMPLE_IDS. Pin that set here so adding
# or removing a shipped layer (e.g. the R39 standee archive) cannot silently
# shift the disc bytes every layered token draws on.
DISC_SAMPLE_LAYER_IDS = [
    'wolf', 'warg', 'great-wolf', 'orc-warrior', 'orc-archer', 'orc-assassin',
    'skeleton-warrior', 'skeleton-mage', 'skeleton-archer', 'giant-spider', 'ungole',
    'weaver-queen', 'phoenix', 'storm-wyrm', 'human-guard', 'derth-guard', 'elven-mage',
    'necromancer', 'pyromancer', 'yeek-mindslayer',
]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def layer_ids() -> list[str]:
    """Read the authoritative layer-file id set from the runtime module.

    This is M.layer_file_ids (the union of the R32 ordinary ids and the R33
    standee ids), not the M.layer_ids trial gate: the layers must keep building
    while the ordinary trial switch is off.
    """
    out = subprocess.run(
        ['lua5.1', '-e', (
            "local T=assert(loadfile('overload/mod/class/CheckerTokens.lua'))() "
            "local ids={} for id in pairs(T.layer_file_ids) do ids[#ids+1]=id end "
            "table.sort(ids) io.write(table.concat(ids,'\\n'))")],
        cwd=ROOT, capture_output=True, text=True, check=True)
    return [line for line in out.stdout.splitlines() if line]


def ordinary_layer_ids() -> list[str]:
    """The R32 ordinary id set (M.layer_ids), used to keep the shared disc's
    sample set pinned so adding standee layers cannot shift its bytes."""
    out = subprocess.run(
        ['lua5.1', '-e', (
            "local T=assert(loadfile('overload/mod/class/CheckerTokens.lua'))() "
            "local ids={} for id in pairs(T.layer_ids) do ids[#ids+1]=id end "
            "table.sort(ids) io.write(table.concat(ids,'\\n'))")],
        cwd=ROOT, capture_output=True, text=True, check=True)
    return [line for line in out.stdout.splitlines() if line]


def alpha_box(rgba: np.ndarray, threshold: int = 8) -> dict:
    """Creature alpha bbox on the layer canvas, PIL getbbox convention
    (right/bottom exclusive). Threshold matches the exporter's occupancy gate.
    """
    ys, xs = np.where(rgba[..., 3] > threshold)
    assert len(xs) and len(ys), 'empty layer alpha'
    return {'left': int(xs.min()), 'top': int(ys.min()),
            'right': int(xs.max()) + 1, 'bottom': int(ys.max()) + 1}


def write_geometry(boxes: dict) -> None:
    lines = ['-- Generated by tools/build_token_layers.py. Do not edit by hand.',
             '-- Creature alpha bbox on the layer canvas, PIL getbbox convention',
             '-- (right/bottom exclusive), plus that file\'s square canvas size in',
             '-- px. The standee feet anchor and scale read this table; a missing',
             '-- entry keeps an id flattened. Ordinary R32 layers are 128px; standee',
             '-- layers are 256px. A standee carries body_top: the y of the top of',
             '-- the BODY in the layer (raised weapons/orbs/particles are excluded).',
             '-- It also carries an "aura" box: the same creature on the POT aura',
             '-- texture (body + ~0.4 cell headroom, so the SDM flames are native-',
             '-- sized and the creature still lines up exactly). The aura texture is a',
             '-- 256x256 square, or 128x256 for a tall body whose square diagonal would',
             '-- exceed 2.6 cells; canvas_w/canvas_h give the texture size (canvas stays',
             '-- the height for older readers). Aura bounds may be fractional:',
             '-- they preserve the continuous layer transform, not raster occupancy.',
             'return {']
    for tid in sorted(boxes):
        b = boxes[tid]
        line = '\t[%s]={left=%d,top=%d,right=%d,bottom=%d,canvas=%d' % (
            json.dumps(tid), b['left'], b['top'], b['right'], b['bottom'], b['canvas'])
        if 'body_top' in b:
            line += ',body_top=%d' % b['body_top']
        if 'aura' in b:
            a = b['aura']
            # Aura geometry is the continuous mapping of the layer bounds,
            # not the integer alpha occupancy of its resampled PNG (R50).
            # repr preserves float precision; legacy integer entries stay intact.
            line += ',aura={' + ','.join('%s=%r' % (key, a.get(key, a['canvas']))
                for key in ('left', 'top', 'right', 'bottom', 'canvas',
                            'canvas_w', 'canvas_h', 'body_top')) + '}'
        lines.append(line + '},')
    lines.append('}')
    (ROOT / 'data' / 'token-layer-geometry.lua').write_text('\n'.join(lines) + '\n')
    (ART / 'geometry.json').write_text(json.dumps(boxes, indent=2, sort_keys=True) + '\n')


def manifest() -> dict:
    data = json.loads(MANIFEST.read_text())
    return {entry['id']: entry for entry in data['assets']}


def master_path(entry: dict) -> Path | None:
    for candidate in sorted((ROOT / 'art' / entry['batch'] / 'masters').glob(entry['id'] + '-v*.png')):
        if digest(candidate) == entry['master_sha256']:
            return candidate
    return None


# R36 upright standee masters. A layer id with art/token-layers/<id>/standee/
# master-v*.png uses that full-body upright master for the standee layer instead
# of the flat token cut-out; every other id keeps the flat-master default. The
# master's own native alpha is used (run_imagegen already gated it); BiRefNet is
# only a fallback when the stored alpha is unusable, and the disc-radius
# clean_alpha pass is skipped because it would delete parts far from the centre.
def standee_master(tid: str) -> Path | None:
    folder = ART / tid / 'standee'
    candidates = sorted(folder.glob('master-v*.png')) if folder.is_dir() else []
    return candidates[-1] if candidates else None


def load_rgba(path: Path) -> np.ndarray:
    return np.asarray(Image.open(path).convert('RGBA')).astype(np.float64)


def run_rembg(master: Path, out: Path, force: bool, session=None) -> None:
    if out.exists() and not force:
        return
    from rembg import new_session, remove
    out.parent.mkdir(parents=True, exist_ok=True)
    if session is None:
        session = new_session(MODEL)
    image = Image.open(master).convert('RGBA')
    remove(image, session=session, alpha_matting=False).save(out)


def export_window(master: np.ndarray, size: int = SIZE) -> tuple[float, float, float]:
    """Port of tools/export_token.c: centre the alpha>8 bounds at .86 occupancy."""
    alpha = master[..., 3]
    ys, xs = np.where(alpha > 8)
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    extent = max(x1 - x0 + 1, y1 - y0 + 1) / 0.86
    left = (x0 + x1 + 1) / 2.0 - extent / 2
    top = (y0 + y1 + 1) / 2.0 - extent / 2
    return left, top, extent / size


def resample_premul(rgba: np.ndarray, left: float, top: float, step: float, size: int = SIZE, pad: int = 512) -> np.ndarray:
    """Premultiplied area downsample onto the `size`-px token canvas (export_token.c)."""
    h, w, _ = rgba.shape
    canvas = np.zeros((h + 2 * pad, w + 2 * pad, 4), np.float64)
    canvas[pad:pad + h, pad:pad + w] = rgba
    l, t = left + pad, top + pad
    x0, y0 = int(np.floor(l)), int(np.floor(t))
    side = int(np.ceil(step * size)) + 2
    crop = canvas[y0:y0 + side, x0:x0 + side].copy()
    crop[..., :3] *= crop[..., 3:4] / 255.0
    im = Image.fromarray(np.clip(crop, 0, 255).astype(np.uint8), 'RGBA').resize((size, size), Image.BOX)
    out = np.asarray(im).astype(np.float64)
    out[..., :3] = np.where(out[..., 3:4] > 0, out[..., :3] * 255.0 / np.maximum(out[..., 3:4], 1e-6), 0)
    return np.clip(out, 0, 255)


def resample_alpha(alpha: np.ndarray, left: float, top: float, step: float) -> np.ndarray:
    ys = (top + (np.arange(SIZE) + 0.5) * step).astype(np.float32)
    xs = (left + (np.arange(SIZE) + 0.5) * step).astype(np.float32)
    X, Y = np.meshgrid(xs, ys)
    return map_coordinates(alpha.astype(np.float32), [Y, X], order=1, mode='constant', cval=0.0)


def median_map(data: np.ndarray, bare: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    cov = bare.sum(0)
    out = np.full(data.shape[1:], np.nan, np.float32)
    for y in range(SIZE):
        for x in range(SIZE):
            sel = bare[:, y, x]
            if sel.sum() > 0:
                out[y, x] = np.median(data[sel, y, x], axis=0)
    return out, cov


def build_disc(sample_ids: list[str], entries: dict, force: bool, session=None) -> np.ndarray:
    """Per-pixel median over creature-mask-0 samples, shadow-field removed."""
    yy, xx = np.mgrid[:SIZE, :SIZE]
    radius = np.hypot(xx - DISC_CX, yy - DISC_CY) / DISC_R
    ri = np.clip(np.round(radius * DISC_R).astype(int), 0, int(DISC_R))
    (ART / 'disc/masks').mkdir(parents=True, exist_ok=True)
    rgbs, alphas, masks = [], [], []
    for tid in sample_ids:
        entry = entries[tid]
        master = master_path(entry)
        assert master, 'no pinned master for ' + tid
        src = ART / 'disc/source' / (tid + '.png')
        run_rembg(master, src, force, session)
        left, top, step = export_window(load_rgba(master))
        masked = load_rgba(src)
        masks.append(resample_alpha(masked[..., 3], left, top, step))
        token = load_rgba(ROOT / 'data/gfx/tokens' / (tid + '.png'))
        rgbs.append(token[..., :3])
        alphas.append(token[..., 3])
        Image.fromarray(np.clip(masks[-1], 0, 255).astype(np.uint8)).save(
            ART / 'disc/masks' / (tid + '.png'))
    rgb = np.stack(rgbs)
    alpha = np.stack(alphas)
    mask = np.stack(masks)
    bare = mask < 16
    med, cov = median_map(rgb, bare)

    # The disc base is the shadow-free annulus 0.60R..0.88R held flat inward:
    # every trial creature stands over the centre, so every centre sample is
    # contact shadow, not disc.
    prof = np.full((int(DISC_R) + 1, 3), np.nan, np.float32)
    for rad in range(int(DISC_R) + 1):
        ring = (ri == rad) & (cov >= 6)
        if ring.sum() >= 4:
            prof[rad] = np.median(med[ring], axis=0)
    band = [rad for rad in range(int(0.60 * DISC_R), int(0.88 * DISC_R) + 1) if np.isfinite(prof[rad, 0])]
    model = np.tile(np.median(prof[band], axis=0), (int(DISC_R) + 1, 1))
    for rad in band:
        model[rad] = prof[rad]
    # Real high-frequency grain everywhere, low-frequency shadow nowhere.
    from scipy.ndimage import gaussian_filter
    blur = gaussian_filter(np.nan_to_num(med, nan=0.0), sigma=(5, 5, 0))
    detail = np.nan_to_num(med - blur, nan=0.0)
    w = np.clip((radius - 0.35) / (0.70 - 0.35), 0, 1)
    w = w * w * (3 - 2 * w)
    out = model[ri] + detail * w[..., None]
    rim = (radius > 0.90) & (radius < 1.06) & (cov >= 6)
    for c in range(3):
        out[..., c] = np.where(rim, med[..., c], out[..., c])
    # One uniform soft contact shadow for every trial creature instead of 20
    # inconsistent per-token shadows.
    out *= (1.0 - 0.10 * np.exp(-(radius / 0.52) ** 2))[..., None]

    amed, acov = median_map(alpha[..., None], bare)
    real_a = amed[..., 0]
    aedge = np.clip((1.00 - radius) / 0.04, 0, 1) * 255
    edge = (acov >= 5) & ~np.isnan(real_a) & (radius > 0.90) & (radius < 1.04)
    aval = np.where(edge, real_a, aedge)
    result = np.zeros((SIZE, SIZE, 4), np.uint8)
    result[..., :3] = np.clip(out, 0, 255).astype(np.uint8)
    result[..., 3] = np.clip(aval, 0, 255).astype(np.uint8)
    return result


def clean_alpha(alpha: np.ndarray, cx: float, cy: float, radius: float) -> np.ndarray:
    """Drop disc chips/noise, keep creature detail, close interior holes."""
    hard = alpha >= 40
    lab, n = ndimage.label(hard)
    yy, xx = np.mgrid[:alpha.shape[0], :alpha.shape[1]]
    rr = np.hypot(xx - cx, yy - cy) / radius
    keep = np.zeros(n + 1, bool)
    for i in range(1, n + 1):
        comp = lab == i
        size = int(comp.sum())
        if size < 40:
            continue
        if rr[comp].mean() > 0.86 and size < 1500:
            continue
        keep[i] = True
    cleaned = np.where(keep[lab], alpha, 0.0)
    holes = ndimage.binary_fill_holes(cleaned >= 40) & (cleaned < 40)
    return np.where(holes, alpha, cleaned)


def build_creature(tid: str, entry: dict, force: bool, session=None) -> np.ndarray:
    master = master_path(entry)
    assert master, 'no pinned master for ' + tid
    src = ART / tid / 'source.png'
    run_rembg(master, src, force, session)
    master_rgba = load_rgba(master)
    left, top, step = export_window(master_rgba)
    cre = resample_premul(load_rgba(src), left, top, step)
    # Disc geometry in canvas coords, from the master's own visible disc. The
    # 128 canvas is normalised, so the disc centre lands near (63.9, 64.1).
    cx, cy, r = DISC_CX, DISC_CY, DISC_R
    cre[..., 3] = clean_alpha(cre[..., 3], cx, cy, r)
    Image.fromarray(np.clip(cre, 0, 255).astype(np.uint8), 'RGBA').save(ART / tid / ('mask-%d.png' % SIZE))
    return cre


def usable_alpha(rgba: np.ndarray) -> bool:
    alpha = rgba[..., 3]
    return alpha.max() >= 240 and alpha.min() == 0


def build_standee(tid: str, master: Path, force: bool, session=None) -> np.ndarray:
    """Upright standee layer from a full-body master (R36).

    Prefer the master's own native alpha: run_imagegen already rejected a fake
    background, and a BiRefNet pass would only add a second guess. Fall back to
    rembg if the stored alpha is not usable. No disc-radius clean_alpha: a
    standee legitimately has limbs and held items far from the canvas centre.
    """
    master_rgba = load_rgba(master)
    if usable_alpha(master_rgba):
        source = master
    else:
        source = ART / tid / 'standee' / 'source.png'
        run_rembg(master, source, force, session)
    # Keep the committed per-id source path the provenance/test resolver expects.
    (ART / tid / 'source.png').write_bytes(source.read_bytes())
    left, top, step = export_window(load_rgba(source), STANDEE_SIZE)
    cre = resample_premul(load_rgba(source), left, top, step, STANDEE_SIZE)
    Image.fromarray(np.clip(cre, 0, 255).astype(np.uint8), 'RGBA').save(ART / tid / ('mask-%d.png' % STANDEE_SIZE))
    return cre


def standee_caps() -> dict[str, float]:
    """Committed standee height caps (generated native-tall table + overrides).

    The aura quad is body height + headroom, so the aura texture depends on the
    cap. Read the same committed data the runtime uses rather than duplicating
    the rule: tools/build_standee_heights.py generates the table and
    CheckerTokenStyle.M.standee_height_override wins for reviewed ids.
    """
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        'build_standee_heights', ROOT / 'tools' / 'build_standee_heights.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    caps = dict(mod.compute()[0])
    caps.update(mod.parse_overrides((ROOT / 'overload/mod/class/CheckerTokenStyle.lua').read_text()))
    return caps


def build_aura(cre: np.ndarray, tid: str, body_top: int, cap: float) -> tuple[np.ndarray, dict]:
    """R42/R46 POT aura copy: body + headroom, not a pad on every side.

    The awesomeaura shader draws its flames over the whole aura quad, so the
    quad diagonal sets the flame size. Build the quad as the BODY height plus
    AURA_HEADROOM_CELLS above body_top (native 1x2 tall sprite diagonal 2.24
    cells), then fit the layer into a POT texture so the creature still maps
    onto the creature quad exactly. Any raised weapon sits inside the headroom.

    R50: H = max(body + 0.4, art + gate_headroom), with gate_headroom=0.5. When H*sqrt(2) <= 2.6 the texture is
    the 256x256 square S = max(H, sqrt(2.5)). When it is larger the texture is
    128x256 with h = max(H, 2.0) and w = h/2 (isotropic), so a tall body keeps
    the native-diagonal flame size instead of a huge square. The recorded box
    carries canvas_w/canvas_h so the runtime can map the non-square texture.
    """
    layer = np.clip(cre, 0, 255).astype(np.uint8)
    box = alpha_box(cre)
    bh_body = box['bottom'] - body_top
    bw = box['right'] - box['left']
    assert bh_body > 0, 'body_top is below the layer bottom: ' + tid
    assert 0 <= body_top < box['bottom'], 'body_top outside the art: ' + tid
    # Runtime scale (cells per layer px), the same rule as standeeQuad.
    s_c = min(cap / bh_body, 1.0 / bw)
    art_cells = (box['bottom'] - box['top']) * s_c
    body_cells = bh_body * s_c
    h_need = max(body_cells + AURA_HEADROOM_CELLS,
                 art_cells + AURA_GATE_HEADROOM_CELLS)
    if h_need * math.sqrt(2) <= AURA_TALL_DIAG_CELLS:
        # SQUARE (R42): unchanged. S = max(H, sqrt(2.5)), 256x256.
        quad_h = max(h_need, AURA_MIN_QUAD_CELLS)
        canvas_w = canvas_h = AURA_CANVAS
    else:
        # TALL (R46): h = max(H, 2.0), w = h/2, 128x256, isotropic.
        quad_h = max(h_need, AURA_TALL_MIN_CELLS)
        canvas_w, canvas_h = AURA_TALL_W, AURA_TALL_H
    # texture px per layer px: the whole quad height maps to canvas_h.
    r = canvas_h / (quad_h / s_c)
    # R50: use one continuous isotropic transform for both the pixels and
    # geometry. Rounding resize dimensions/offsets, then measuring alpha_box,
    # changes the body-height/width ratio and breaks width-bound scale equality.
    ox = canvas_w / 2 - ((box['left'] + box['right']) / 2) * r
    oy = canvas_h - box['bottom'] * r
    # Pillow's affine coordinates map output pixel centres into source centres.
    # RGBa resamples premultiplied colour/alpha, avoiding dark transparent rims.
    out = Image.fromarray(layer, 'RGBA').convert('RGBa').transform(
        (canvas_w, canvas_h), Image.Transform.AFFINE,
        (1 / r, 0, -ox / r, 0, 1 / r, -oy / r),
        resample=Image.Resampling.BICUBIC).convert('RGBA')
    data = np.asarray(out).astype(np.float64)
    abox = {key: (ox + box[key] * r) if key in ('left', 'right')
            else (oy + box[key] * r)
            for key in ('left', 'top', 'right', 'bottom')}
    # The width cap mathematically keeps these bounds inside the canvas.
    # Clamp cancellation noise at exact edges (e.g. -7e-15 at left=0).
    abox['left'] = max(0.0, abox['left'])
    abox['right'] = min(float(canvas_w), abox['right'])
    abox['bottom'] = min(float(canvas_h), abox['bottom'])
    abox['canvas'] = canvas_h  # backward compatible: the texture height
    abox['canvas_w'] = canvas_w
    abox['canvas_h'] = canvas_h
    abox['body_top'] = oy + body_top * r
    return data, abox


def versions() -> dict:
    from importlib.metadata import version
    return {name: version(name) for name in ('rembg', 'onnxruntime', 'numpy', 'pillow', 'scipy')}


def write_provenance(layers: list[str], samples: list[str]) -> None:
    vers = versions()
    lines = [
        '# Layered small-tile trials - provenance',
        '',
        'Generated by `tools/build_token_layers.py` (never run during packaging or tests).',
        f'Background-removal model: rembg `{MODEL}` (BiRefNet).',
        '',
        '## Toolchain',
        '',
    ]
    for name, ver in vers.items():
        lines.append(f'- {name} {ver}')
    lines += [
        '',
        '## Commands',
        '',
        '```sh',
        'R30=<workspace>/tmp/rotation/R30-scratch/venv/bin/python',
        '$R30 tools/build_token_layers.py',
        '```',
        '',
        'The BiRefNet pass is cached under `art/token-layers/*/source.png` and',
        '`art/token-layers/disc/source/`, so re-running the tool reproduces the',
        'runtime PNGs byte-for-byte from the committed sources.',
        '',
        f'## Creature layers ({len(layers)})',
        '',
        'The id set is `CheckerTokens.layer_file_ids` (R32 ordinary plus R33',
        'boss standee). The per-creature alpha bbox is in `geometry.json` and',
        '`data/token-layer-geometry.lua`.',
        '',
    ]
    for tid in layers:
        standee = standee_master(tid)
        if standee:
            lines.append(f'- `{tid}`: `{standee.relative_to(ROOT)}` (upright standee master, R36), '
                         f'`{tid}/mask-{STANDEE_SIZE}.png` (aligned alpha), '
                         f'`{tid}/aura.png` and `data/gfx/tokens-layer/aura/{tid}.png` '
                         f'(R42 POT {AURA_CANVAS}px aura copy, body + {AURA_HEADROOM_CELLS} cell headroom), '
                         f'`data/gfx/tokens-layer/{tid}.png` (runtime, {STANDEE_SIZE}px canvas). '
                         'The flat token cut-out is not used for this standee layer; the flat '
                         '128px token is unchanged.')
        else:
            lines.append(f'- `{tid}`: `{tid}/source.png` (master cut-out), `{tid}/mask-{SIZE}.png` '
                         f'(aligned/cleaned alpha), `data/gfx/tokens-layer/{tid}.png` (runtime, {SIZE}px canvas).')
    lines += [
        '',
        '## Shared disc samples',
        '',
        f'{len(samples)} varied tokens. Their aligned masks live in `disc/masks/`;',
        'the per-pixel median over mask-0 samples is in `disc/_disc.png` and',
        '`data/gfx/tokens-layer/_disc.png`.',
        '',
    ]
    (ART / 'PROVENANCE.md').write_text('\n'.join(lines))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--force', action='store_true', help='re-run BiRefNet even if cached')
    args = parser.parse_args()
    layers = layer_ids()
    assert layers, 'CheckerTokens.layer_file_ids is empty; nothing to build'
    standee_layer_ids = {tid for tid in layers if standee_master(tid)}
    unknown_body_top = sorted(set(BODY_TOP) - standee_layer_ids)
    if unknown_body_top:
        raise SystemExit('BODY_TOP names ids that do not ship a standee: ' + ', '.join(unknown_body_top))
    caps = standee_caps()
    entries = manifest()
    for tid in layers:
        assert tid in entries, 'layer id missing from manifest: ' + tid
    samples = DISC_SAMPLE_LAYER_IDS + EXTRA_SAMPLE_IDS
    for tid in samples:
        assert tid in entries, 'disc sample missing from manifest: ' + tid
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)

    from rembg import new_session
    session = new_session(MODEL)
    disc = build_disc(samples, entries, args.force, session)
    Image.fromarray(disc, 'RGBA').save(RUNTIME_DIR / '_disc.png')
    (ART / 'disc').mkdir(parents=True, exist_ok=True)
    Image.fromarray(disc, 'RGBA').save(ART / 'disc/_disc.png')

    boxes = {}
    AURA_DIR.mkdir(parents=True, exist_ok=True)
    for tid in layers:
        (ART / tid).mkdir(parents=True, exist_ok=True)
        standee = standee_master(tid)
        if standee:
            cre = build_standee(tid, standee, args.force, session)
            canvas = STANDEE_SIZE
        else:
            cre = build_creature(tid, entries[tid], args.force, session)
            canvas = SIZE
        Image.fromarray(np.clip(cre, 0, 255).astype(np.uint8), 'RGBA').save(RUNTIME_DIR / (tid + '.png'))
        (ART / tid / 'creature.png').write_bytes((RUNTIME_DIR / (tid + '.png')).read_bytes())
        box = alpha_box(cre)
        box['canvas'] = canvas
        if standee:
            if tid not in caps:
                raise SystemExit('standee has no committed height cap: ' + tid)
            body_top = BODY_TOP.get(tid, box['top'])
            if not (box['top'] <= body_top < box['bottom']):
                raise SystemExit(f'body_top {body_top} outside the art for {tid}')
            box['body_top'] = int(body_top)
            aura, abox = build_aura(cre, tid, int(body_top), caps[tid])
            Image.fromarray(np.clip(aura, 0, 255).astype(np.uint8), 'RGBA').save(ART / tid / 'aura.png')
            Image.fromarray(np.clip(aura, 0, 255).astype(np.uint8), 'RGBA').save(AURA_DIR / (tid + '.png'))
            box['aura'] = abox
        boxes[tid] = box
    write_geometry(boxes)
    write_provenance(layers, samples)
    print('built', len(layers), 'creature layers + shared disc')
    print('disc', digest(RUNTIME_DIR / '_disc.png'))


if __name__ == '__main__':
    main()
