"""Offline contact sheets comparing token disc diameters and UI lane widths.

Purely a decision aid: it renders nothing the game loads and changes no asset.
The cell geometry reproduces CheckerTokenStyle.geometry / checkerTacticalFrame
and the procedural ring radii of prepare_runtime_art.py, so a panel shows what
the engine would draw for a given (art disc, faction lane, shield lane) triple.

  python3 tools/render_token_scale_compare.py --out evidence/<dir>

Pillow only; no numpy. Every ring is supersampled and box-filtered down.
"""
from pathlib import Path
import argparse
import math

from PIL import Image, ImageChops, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
NATIVE = ROOT.parents[2] / 'demo/checkerboard-v3/session/runtime/game/modules/tome/data/gfx/shockbolt/npc'

SS = 6            # supersampling factor
CELL = 64         # map cell size under test
ART_OCCUPANCY = .86

COLORS = {
    'enemy': (225, 55, 40), 'friend': (72, 210, 105), 'neutral': (65, 125, 245),
    'player': (30, 195, 245), 'shield': (236, 234, 225), 'shield_ticks': (255, 253, 245),
    'back': (15, 20, 20), 'shield_track': (25, 28, 27),
}
FLOOR = (46, 44, 40)
FLOOR_ALT = (38, 36, 33)

# Radii as a share of the texture square, copied from prepare_runtime_art.py.
STOCK = {
    'relation_back': (.402, .498),
    'relation_edge': (.474, .495),
    'health_band': (.410, .463),
    'shield_track': (.459, .499),
    'shield_band': (.465, .493),
    'shield_ticks': (.473, .495),
}

NATIVE_IMAGE = {
    'brown-rat': 'vermin_rodent_giant_brown_rat.png',
    'bee-swarm': 'bee_swarm.png',
    'brown-snake': 'umber-snake.png',
    'degenerated-skeleton-warrior': 'degenerated_skeleton_warrior.png',
    'wolf': 'canine_w.png',
    'forest-troll': 'troll_f.png',
    'brown-bear': 'brown_bear.png',
}


def retune_shield(rings, faction_outer_abs, shield_d):
    """Push the shield masks outwards until they clear a narrowed faction rim.

    Thinning both lanes without this makes the shield track overlap the faction
    ring, which the shield_style geometry assertion already forbids.
    """
    out = dict(rings)
    lo, hi = rings['shield_track']
    new_lo = (faction_outer_abs + .006) / shield_d
    if new_lo <= lo:
        return out
    factor = (hi - new_lo) / (hi - lo)
    for key in ('shield_track', 'shield_band', 'shield_ticks'):
        a, b = rings[key]
        out[key] = (hi - (hi - a) * factor, hi - (hi - b) * factor)
    return out


def disc(n, cx, cy, r, fill=255, into=None):
    img = into if into is not None else Image.new('L', (n, n), 0)
    ImageDraw.Draw(img).ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill)
    return img


def annulus(n, cx, cy, r_in, r_out):
    mask = disc(n, cx, cy, r_out)
    disc(n, cx, cy, r_in, fill=0, into=mask)
    return mask


def arc_mask(n, cx, cy, r, fraction, counterclockwise):
    """Sector of `fraction` of a turn starting at twelve o'clock.

    Pillow measures degrees clockwise from three o'clock with y pointing down,
    so the counterclockwise health arc runs towards decreasing angles.
    """
    mask = Image.new('L', (n, n), 0)
    if fraction <= 0:
        return mask
    if fraction >= 1:
        return Image.new('L', (n, n), 255)
    sweep = fraction * 360
    start, end = (-90 - sweep, -90) if counterclockwise else (-90, -90 + sweep)
    ImageDraw.Draw(mask).pieslice([cx - r, cy - r, cx + r, cy + r], start, end, fill=255)
    return mask


def axis_wedges(n, cx, cy, r, half_width_rad, keep):
    """Reproduce the notch/tick patterns of prepare_runtime_art.mask()."""
    wedge = Image.new('L', (n, n), 0)
    draw = ImageDraw.Draw(wedge)
    half = math.degrees(half_width_rad)
    for axis in (0, 90, 180, 270):
        draw.pieslice([cx - r, cy - r, cx + r, cy + r], axis - half, axis + half, fill=255)
    return wedge if keep else ImageChops.invert(wedge)


def paint(base, mask, color):
    base.paste(Image.new('RGBA', base.size, color + (255,)), (0, 0), mask)


def render_cell(image, *, art, faction_lane, shield_lane, rings, relation='enemy',
                life=1.0, shield=None, alt=False, cell=CELL):
    """One map cell: floor, token artwork, faction/health ring, optional shield."""
    n = cell * SS
    base = Image.new('RGBA', (n, n), (FLOOR_ALT if alt else FLOOR) + (255,))
    if image is not None:
        side = int(round(cell * art / ART_OCCUPANCY * SS))
        off = (n - side) // 2
        base.alpha_composite(image.resize((side, side), Image.LANCZOS), (off, off))

    cx = cy = n / 2 - .5
    gd = cell * (art + faction_lane) * SS
    outer_r = rings['relation_back'][1] * gd

    paint(base, annulus(n, cx, cy, rings['relation_back'][0] * gd, outer_r), COLORS['back'])
    color = COLORS[relation]
    band = annulus(n, cx, cy, rings['health_band'][0] * gd, rings['health_band'][1] * gd)
    paint(base, ImageChops.multiply(band, arc_mask(n, cx, cy, outer_r, life, True)), color)
    edge = annulus(n, cx, cy, rings['relation_edge'][0] * gd, rings['relation_edge'][1] * gd)
    if relation == 'enemy':
        edge = ImageChops.multiply(edge, axis_wedges(n, cx, cy, outer_r, .075, keep=False))
    elif relation == 'neutral':
        edge = ImageChops.multiply(edge, axis_wedges(n, cx, cy, outer_r, math.pi / 12, keep=True))
    paint(base, edge, color)

    if shield is not None:
        sd = gd + cell * shield_lane * SS
        s_out = rings['shield_track'][1] * sd
        paint(base, annulus(n, cx, cy, rings['shield_track'][0] * sd, s_out), COLORS['shield_track'])
        s_band = annulus(n, cx, cy, rings['shield_band'][0] * sd, rings['shield_band'][1] * sd)
        paint(base, ImageChops.multiply(s_band, arc_mask(n, cx, cy, s_out, shield, False)), COLORS['shield'])
        ticks = annulus(n, cx, cy, rings['shield_ticks'][0] * sd, rings['shield_ticks'][1] * sd)
        paint(base, ImageChops.multiply(ticks, axis_wedges(n, cx, cy, s_out, .035, keep=True)),
              COLORS['shield_ticks'])

    return base.resize((cell, cell), Image.LANCZOS)


def font(size):
    for name in ('/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc',
                 '/usr/share/fonts/noto-cjk/NotoSerifCJK-Regular.ttc',
                 '/usr/share/fonts/TTF/DejaVuSans.ttf'):
        if Path(name).exists():
            try:
                return ImageFont.truetype(name, size)
            except OSError:
                continue
    return ImageFont.load_default()


def old_scale(size_category, tile=CELL):
    """The 0.6.7 tiering, kept here only to draw the "before" column."""
    s = .86 if size_category <= 1 else .94 if size_category <= 3 else 1
    if tile < 64:
        s = 1
    return s * .95


def variant_table():
    thin = dict(art=.88, faction_lane=.055, shield_lane=.06)
    thin_gd = thin['art'] + thin['faction_lane']
    retuned = retune_shield(STOCK, STOCK['relation_back'][1] * thin_gd, thin_gd + thin['shield_lane'])
    return [
        ('current', '现状 0.6.7\n三档 0.702/0.767/0.816',
         lambda sc: dict(art=ART_OCCUPANCY * old_scale(sc), faction_lane=.085, shield_lane=.09, rings=STOCK)),
        ('unified', '方案(a) 本轮交付\n统一 0.82',
         lambda sc: dict(art=.82, faction_lane=.085, shield_lane=.09, rings=STOCK)),
        ('thin', '方案(b) 0.88 削薄\n沿用现有环遮罩',
         lambda sc: dict(rings=STOCK, **thin)),
        ('thin_retuned', "方案(b') 0.88 削薄\n＋外推护盾遮罩",
         lambda sc: dict(rings=retuned, **thin)),
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', default='evidence/token-scale-20260927')
    args = parser.parse_args()
    out = ROOT / args.out
    out.mkdir(parents=True, exist_ok=True)

    subjects = [
        ('brown-rat', 1, '巨型棕鼠 size 1'),
        ('bee-swarm', 1, '蜂群 size 1'),
        ('brown-snake', 2, '大棕蛇 size 2'),
        ('wolf', 2, '狼 size 2'),
        ('degenerated-skeleton-warrior', 3, '退化骷髅战士 size 3'),
        ('forest-troll', 4, '森林巨魔 size 4'),
        ('brown-bear', 4, '棕熊 size 4'),
    ]
    art = {s: Image.open(ROOT / 'data/gfx/tokens' / f'{s}.png').convert('RGBA') for s, _, _ in subjects}
    variants = variant_table()
    f_head, f_small = font(15), font(13)
    pad, head, label_w = 10, 80, 215

    # --- Sheet 1: disc diameter per size_category, with the native reference.
    zoom = 3
    cw = CELL * zoom + pad
    sheet = Image.new('RGBA', (label_w + (len(variants) + 1) * cw + pad,
                               head + len(subjects) * cw + 36), (24, 24, 26, 255))
    draw = ImageDraw.Draw(sheet)
    draw.text((pad, 10), '棋子直径对照（64px 地格，放大 3 倍，敌对红环＋满血弧）', font=f_head, fill=(235, 235, 235))
    draw.text((label_w, 36), '原版 shockbolt\n（对照，无棋子环）', font=f_small, fill=(200, 200, 200))
    for i, (_, label, _) in enumerate(variants):
        draw.text((label_w + (i + 1) * cw, 36), label, font=f_small, fill=(200, 200, 200))
    for r, (sid, sc, label) in enumerate(subjects):
        y = head + r * cw
        draw.text((pad, y + CELL * zoom // 2 - 8), label, font=f_small, fill=(215, 215, 215))
        native_file = NATIVE / NATIVE_IMAGE[sid]
        if native_file.exists():
            cellimg = Image.new('RGBA', (CELL, CELL), FLOOR + (255,))
            cellimg.alpha_composite(Image.open(native_file).convert('RGBA').resize((CELL, CELL), Image.LANCZOS))
            sheet.alpha_composite(cellimg.resize((CELL * zoom, CELL * zoom), Image.NEAREST), (label_w, y))
        for i, (_, _, geom) in enumerate(variants):
            cellimg = render_cell(art[sid], relation='enemy', life=1.0, alt=(r + i) % 2 == 0, **geom(sc))
            sheet.alpha_composite(cellimg.resize((CELL * zoom, CELL * zoom), Image.NEAREST),
                                  (label_w + (i + 1) * cw, y))
    draw.text((pad, sheet.height - 28),
              '同一列内圆盘直径是否一致即为“齐不齐”；原版列只作大小参照，不含阵营／生命环。',
              font=f_small, fill=(170, 170, 170))
    sheet.convert('RGB').save(out / 'diameter-compare-64.png')

    # --- Sheet 2: lane readability with and without a shield.
    rows = [
        ('满血 · 无护盾', dict(life=1.0, shield=None)),
        ('35% 生命 · 无护盾', dict(life=.35, shield=None)),
        ('满血 · 满护盾', dict(life=1.0, shield=1.0)),
        ('35% 生命 · 45% 护盾', dict(life=.35, shield=.45)),
    ]
    zoom2 = 6
    cw2 = CELL * zoom2 + pad
    sheet2 = Image.new('RGBA', (label_w + len(variants) * cw2 + pad,
                                head + len(rows) * cw2 + 56), (24, 24, 26, 255))
    d2 = ImageDraw.Draw(sheet2)
    d2.text((pad, 10), '留道可读性对照（狼 size 2，64px 地格，放大 6 倍）', font=f_head, fill=(235, 235, 235))
    for i, (_, label, _) in enumerate(variants):
        d2.text((label_w + i * cw2, 36), label, font=f_small, fill=(200, 200, 200))
    for r, (label, state) in enumerate(rows):
        y = head + r * cw2
        d2.text((pad, y + CELL * zoom2 // 2 - 8), label, font=f_small, fill=(215, 215, 215))
        for i, (_, _, geom) in enumerate(variants):
            cellimg = render_cell(art['wolf'], relation='enemy', alt=(r + i) % 2 == 0, **state, **geom(2))
            sheet2.alpha_composite(cellimg.resize((CELL * zoom2, CELL * zoom2), Image.NEAREST),
                                   (label_w + i * cw2, y))
    d2.text((pad, sheet2.height - 46),
            '生命弧与阵营环共用同一条留道。(b) 沿用现有遮罩时护盾环内缘压到阵营环上；\n'
            "(b') 把护盾遮罩外推才能保持分隔，代价是护盾环本身变窄。",
            font=f_small, fill=(170, 170, 170))
    sheet2.convert('RGB').save(out / 'lane-readability-64.png')

    # --- Sheet 3: one board row of mixed size categories, 1:1 strip plus zoom.
    row_ids = ['brown-rat', 'brown-snake', 'degenerated-skeleton-warrior', 'forest-troll', 'brown-bear']
    row_sc = [1, 2, 3, 4, 4]
    zoom3 = 4
    strip_h = CELL * zoom3 + pad
    sheet3 = Image.new('RGBA', (label_w + len(row_ids) * CELL * zoom3 + 2 * pad,
                                head + len(variants) * strip_h + 30), (24, 24, 26, 255))
    d3 = ImageDraw.Draw(sheet3)
    d3.text((pad, 10), '同一排棋子并列（64px 地格，放大 4 倍；交替底色代表相邻地格）',
            font=f_head, fill=(235, 235, 235))
    d3.text((pad, 36), '顺序：巨型棕鼠(1) 大棕蛇(2) 退化骷髅战士(3) 森林巨魔(4) 棕熊(4)',
            font=f_small, fill=(180, 180, 180))
    for i, (_, label, geom) in enumerate(variants):
        y = head + i * strip_h
        d3.text((pad, y + CELL * zoom3 // 2 - 14), label, font=f_small, fill=(215, 215, 215))
        strip = Image.new('RGBA', (len(row_ids) * CELL, CELL))
        for j, sid in enumerate(row_ids):
            strip.alpha_composite(render_cell(art[sid], relation='enemy', life=1.0, alt=j % 2 == 0,
                                              **geom(row_sc[j])), (j * CELL, 0))
        sheet3.alpha_composite(strip.resize((len(row_ids) * CELL * zoom3, CELL * zoom3), Image.NEAREST),
                               (label_w, y))
    sheet3.convert('RGB').save(out / 'board-row-compare-64.png')

    for name in ('diameter-compare-64.png', 'lane-readability-64.png', 'board-row-compare-64.png'):
        print('wrote', (out / name).relative_to(ROOT))


if __name__ == '__main__':
    main()
