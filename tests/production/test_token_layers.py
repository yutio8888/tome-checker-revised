"""Layered small-tile trials: runtime-asset contract.

Static validation only; the in-game check is a separate task. These tests pin
the shipped layer set to the runtime module's own lists, so a new layer cannot
ship without a catalog id and a missing layer cannot silently fall back. The
R32 ordinary trial and the R33 boss standee trial have independent switches;
their layer files share one build set (M.layer_file_ids).
"""
import hashlib
import json
import subprocess
import unittest
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
TOKENS_LUA = ROOT / 'overload/mod/class/CheckerTokens.lua'
LAYER_DIR = ROOT / 'data/gfx/tokens-layer'
AURA_DIR = LAYER_DIR / 'aura'
TOKEN_DIR = ROOT / 'data/gfx/tokens'
ART = ROOT / 'art/token-layers'
GEOMETRY_LUA = ROOT / 'data/token-layer-geometry.lua'
GEOMETRY_JSON = ART / 'geometry.json'
EXPECTED_ORDINARY = {
    'wolf', 'warg', 'great-wolf', 'orc-warrior', 'orc-archer', 'orc-assassin',
    'skeleton-warrior', 'skeleton-mage', 'skeleton-archer', 'giant-spider', 'ungole',
    'weaver-queen', 'storm-wyrm', 'human-guard', 'derth-guard', 'elven-mage',
    'necromancer', 'pyromancer', 'yeek-mindslayer',
}
# R39: standee eligibility is native-tall only, so the native 1-cell boss art
# (rungof, grushnak, vor, phoenix, shardskin, subject-z) and the native-tall
# ids whose derived body-only cap is 1.0 (gorbat, bone-giant and R43 kra-tor)
# are archived and no longer ship a layer.
# Independently pinned approved R53 roster: swapping one id must fail even
# when the total remains 59. All file/canvas/aura checks use this same set.
EXPECTED_STANDEE = {
    'ak-gishil', 'arch-zephyr', 'archlich', 'atamathon',
    'burb-snow-giant-champion', 'celia', 'champion-of-urh-rok',
    'corrupted-daelach', 'dolleg', 'dremling', 'duathedlen',
    'eternal-bone-giant', 'fire-wyrm', 'forge-giant', 'fyrk',
    'greater-multi-hued-wyrm', 'half-finished-bone-giant', 'harkor-zun',
    'healer-astelrid', 'heavy-bone-giant', 'heavy-sentinel', 'horned-horror',
    'ice-wyrm', 'minotaur-maze', 'ninandra', 'norgos-frozen', 'norgos-guardian',
    'ogre-guard', 'ogre-mauler', 'ogre-rune-spinner', 'ogre-warmaster',
    'ogric-abomination', 'rantha', 'ravenous-horror', 'rotting-titan',
    'runed-bone-giant', 'snaproot', 'snow-giant',
    'snow-giant-boulder-thrower', 'snow-giant-chieftain',
    'snow-giant-thunderer', 'storm-wyrm', 'temporal-defiler', 'thaurhereg',
    'treant', 'ultimate-faeros', 'ultimate-shivgoroth', 'uruivellas',
    'varsha', 'venom-wyrm', 'wrathroot', 'xhaiak-arachnomancer',
    'prox', 'bill', 'shax', 'onilug', 'chronolith-twin', 'chronolith-clone',
    'briagh',
}
# Explicit floor (R46): the original four shipped standee ids must remain a
# subset of the runtime set.
ORIGINAL_STANDEE_FLOOR = {'ninandra', 'ogre-guard', 'snow-giant', 'ravenous-horror'}
EXPECTED_FILES = EXPECTED_ORDINARY | EXPECTED_STANDEE
ARCHIVED_IDS = {
    'rungof', 'grushnak', 'vor', 'phoenix', 'shardskin', 'subject-z', 'gorbat', 'bone-giant',
    'kra-tor',
}
# R38: standee layers ship on a 256px canvas so they are not upscaled at a
# 128px tile; ordinary R32 layers stay on the 128px canvas because they only
# draw at <=48px cells. The flattened token PNGs are always 128px.
ORDINARY_CANVAS = 128
STANDEE_CANVAS = 256
EXPECTED_CANVAS = {tid: (STANDEE_CANVAS if tid in EXPECTED_STANDEE else ORDINARY_CANVAS)
                   for tid in EXPECTED_FILES}


def lua(expr: str, interp='luajit') -> str:
    out = subprocess.run([interp, '-e', expr], cwd=ROOT, capture_output=True, text=True, check=True)
    return out.stdout.strip()


def lua_set(field: str) -> list[str]:
    text = lua(
        "local T=assert(loadfile('overload/mod/class/CheckerTokens.lua'))() "
        f"local ids={{}} for id in pairs(T.{field}) do ids[#ids+1]=id end table.sort(ids) "
        "io.write(table.concat(ids,'\\n'))")
    return [line for line in text.splitlines() if line]


def lua_bool(expr: str) -> bool:
    return lua("local T=assert(loadfile('overload/mod/class/CheckerTokens.lua'))() "
               f"io.write(tostring({expr}))") == 'true'


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class TrialListTests(unittest.TestCase):
    def test_flags_default(self):
        self.assertFalse(lua_bool('T.layer_trial'), 'R32 ordinary trial is off by default')
        self.assertTrue(lua_bool('T.standee_trial'), 'R33 standee trial is on by default')
        self.assertEqual(lua("local T=assert(loadfile('overload/mod/class/CheckerTokens.lua'))() "
                             "io.write(tostring(T.layer_max_cell))"), '48')

    def test_exact_id_sets(self):
        self.assertEqual(set(lua_set('layer_ids')), EXPECTED_ORDINARY)
        self.assertEqual(len(lua_set('layer_ids')), 19)
        self.assertEqual(set(lua_set('standee_ids')), EXPECTED_STANDEE)
        self.assertEqual(len(EXPECTED_STANDEE), 59)
        self.assertTrue(ORIGINAL_STANDEE_FLOOR <= EXPECTED_STANDEE, 'the original four ids still ship')
        missing = lua("local g=assert(loadfile('data/token-layer-geometry.lua'))() "
                      "local T=assert(loadfile('overload/mod/class/CheckerTokens.lua'))() "
                      "local o={} for id in pairs(T.standee_ids) do if type(g[id])~='table' then o[#o+1]=id end end "
                      "table.sort(o) io.write(table.concat(o,','))")
        self.assertEqual(missing, '', 'every standee id has a geometry entry')
        self.assertEqual(set(lua_set('layer_file_ids')), EXPECTED_FILES)
        self.assertEqual(len(lua_set('layer_file_ids')), 77)

    def test_layer_paths_and_disc_path(self):
        for tid in sorted(EXPECTED_FILES):
            expected = 'checker-revised+tokens-layer/' + tid + '.png'
            got = lua("local T=assert(loadfile('overload/mod/class/CheckerTokens.lua'))() "
                      f"local v=T.layerImage({tid!r}) io.write(v or '')")
            self.assertEqual(got, expected)
        disc = lua("local T=assert(loadfile('overload/mod/class/CheckerTokens.lua'))() "
                   "io.write(T.layerDisc() or '')")
        self.assertEqual(disc, 'checker-revised+tokens-layer/_disc.png')

    def test_switches_gate_the_two_paths_independently(self):
        # Ordinary R32 path follows M.layer_trial only.
        self.assertFalse(lua_bool("T.layeredId('wolf')"))
        self.assertFalse(lua_bool("T.layeredId('phoenix')"))
        self.assertTrue(lua_bool("(function() T.layer_trial=true return T.layeredId('wolf') end)()"))
        self.assertFalse(lua_bool("(function() T.layer_trial=true return T.layeredId('animated-blood') end)()"))
        # Standee eligibility follows M.standee_trial, not M.layer_trial.
        geom = "T.layer_geometry=assert(loadfile('data/token-layer-geometry.lua'))() "
        self.assertTrue(lua_bool("(function() " + geom + "return T.standeeEligible({rank=1},T.by_id['snow-giant']) end)()"))
        self.assertTrue(lua_bool("(function() T.layer_trial=false " + geom +
                                 "return T.standeeEligible({rank=1},T.by_id['snow-giant']) end)()"),
                        'standee must not depend on layer_trial')
        self.assertFalse(lua_bool("(function() " + geom +
                                  "T.standee_trial=false return T.standeeEligible({rank=1},T.by_id['snow-giant']) end)()"))
        # Both switches off: no disc path for the flattened token.
        self.assertEqual(lua("local T=assert(loadfile('overload/mod/class/CheckerTokens.lua'))() "
                             "T.layer_trial=false T.standee_trial=false "
                             "io.write(tostring(T.layerDisc())..'|'..T.image('snow-giant'))"),
                         'nil|checker-revised+tokens/snow-giant.png')

    def test_static_native_tall_rule(self):
        # Eligibility is decided from the catalogue entry alone: rank and live
        # size_category never change the answer.
        geom = "T.layer_geometry=assert(loadfile('data/token-layer-geometry.lua'))() "
        for id in ('snow-giant', 'ravenous-horror', 'ogre-guard', 'ninandra'):
            self.assertTrue(lua_bool("T.standeeRule(T.by_id[%r])" % id), id)
        # R46: for EVERY shipped standee id both gates must be true (natively
        # tall with a >1.0 cap AND a shipped layer), and the original four ids
        # must remain a subset. This is the explicit floor the review asked for.
        self.assertTrue(ORIGINAL_STANDEE_FLOOR <= EXPECTED_STANDEE,
                        'missing original standee ids: %r' % (ORIGINAL_STANDEE_FLOOR - EXPECTED_STANDEE))
        for id in sorted(EXPECTED_STANDEE):
            self.assertTrue(lua_bool("T.standeeRule(T.by_id[%r])" % id), 'standeeRule ' + id)
            self.assertTrue(lua_bool(
                "(function() " + geom + "return T.standeeEligible({rank=1},T.by_id[%r]) end)()" % id),
                'standeeEligible ' + id)
        for id in ('phoenix', 'rungof', 'vor', 'wolf', 'lich', 'gorbat', 'bone-giant', 'kra-tor'):
            self.assertFalse(lua_bool("T.standeeRule(T.by_id[%r])" % id), id)
        self.assertFalse(lua_bool('T.standeeRule(nil)'))
        # A size_category/rank buff cannot grant a flat id a standee.
        self.assertFalse(lua_bool("(function() " + geom +
                                  "return T.standeeEligible({rank=10,size_category=6},T.by_id['lich']) end)()"))
        # Archived ids never resolve to a layer file.
        for id in ('rungof', 'grushnak', 'vor', 'phoenix', 'shardskin', 'subject-z', 'gorbat', 'bone-giant',
                   'kra-tor'):
            self.assertFalse(lua_bool("T.standee_ids[%r]" % id), id)
            self.assertFalse(lua_bool("T.layer_ids[%r]" % id), id)
            self.assertEqual(lua("local T=assert(loadfile('overload/mod/class/CheckerTokens.lua'))() "
                                 "io.write(tostring(T.layerImage(%r)))" % id), 'nil')

    def test_standee_tile_gate_is_24px(self):
        self.assertEqual(lua("local T=assert(loadfile('overload/mod/class/CheckerTokens.lua'))() "
                             "io.write(tostring(T.standee_min_cell))"), '24')
        for cell in (24, 32, 48, 64, 96, 128):
            self.assertTrue(lua_bool(f"T.standeeTileAllowed({cell})"), cell)
        for cell in (16, 10, 23):
            self.assertFalse(lua_bool(f"T.standeeTileAllowed({cell})"), cell)
        self.assertFalse(lua_bool('T.standeeTileAllowed(nil)'))

    def test_standee_geometry_manifest_matches_layers(self):
        self.assertTrue(GEOMETRY_LUA.is_file())
        geom = lua("local g=assert(loadfile('data/token-layer-geometry.lua'))() "
                   "io.write(tostring(g['snow-giant'].left)..'|'..tostring(g['snow-giant'].bottom)..'|'..tostring(g['snow-giant'].canvas))")
        left, bottom, canvas = (int(v) for v in geom.split('|'))
        self.assertEqual(canvas, STANDEE_CANVAS, 'standee geometry records its 256px canvas')
        self.assertTrue(0 <= left < bottom <= canvas)
        # Every standee layer id needs a box, or the runtime keeps it flat.
        missing = lua("local T=assert(loadfile('overload/mod/class/CheckerTokens.lua'))() "
                      "local g=assert(loadfile('data/token-layer-geometry.lua'))() local o={} "
                      "for id in pairs(T.standee_ids) do if type(g[id])~='table' then o[#o+1]=id end end "
                      "table.sort(o) io.write(table.concat(o,','))")
        self.assertEqual(missing, '')
        on_disk = json.loads(GEOMETRY_JSON.read_text())
        for tid in sorted(EXPECTED_FILES):
            box = on_disk[tid]
            canvas = EXPECTED_CANVAS[tid]
            self.assertEqual(box['canvas'], canvas, tid)
            self.assertLess(box['left'], box['right'])
            self.assertLess(box['top'], box['bottom'])
            self.assertGreaterEqual(box['left'], 0)
            self.assertLessEqual(box['right'], canvas)
            self.assertGreaterEqual(box['top'], 0)
            self.assertLessEqual(box['bottom'], canvas)
            # R42: standees carry body_top and a POT aura box (body + headroom).
            if tid in EXPECTED_STANDEE:
                aura = box['aura']
                # R46: canvas stays the texture HEIGHT for older readers;
                # canvas_w/canvas_h give the real POT texture size (256x256
                # square, or 128x256 for a tall body).
                self.assertEqual(aura['canvas'], aura['canvas_h'], tid)
                self.assertIn(aura['canvas_w'], (128, 256), tid)
                self.assertEqual(aura['canvas_h'], 256, tid)
                self.assertIn('body_top', box, tid)
                self.assertIn('body_top', aura, tid)
                for key in ('left', 'top', 'right', 'bottom'):
                    self.assertTrue(0 <= aura[key] <= aura['canvas_h'], (tid, key))
                self.assertTrue(0 <= aura['left'] and aura['right'] <= aura['canvas_w'], tid)
                self.assertTrue(aura['left'] < aura['right'] and aura['top'] < aura['bottom'], tid)
                self.assertLessEqual(box['top'], box['body_top'])
                self.assertLessEqual(box['body_top'], box['bottom'])
                self.assertLessEqual(aura['top'], aura['body_top'])
                self.assertLessEqual(aura['body_top'], aura['bottom'])
            else:
                self.assertNotIn('aura', box, tid)
                self.assertNotIn('body_top', box, tid)

    def test_tall_aura_shape_is_covered_by_real_ids(self):
        # R47: the 128x256 TALL aura branch must be exercised by real shipped
        # ids, not only the synthetic unit case. At least one standee has
        # canvas_w==128, and every TALL texture is 128x256 POT with w<h.
        on_disk = json.loads(GEOMETRY_JSON.read_text())
        tall = [tid for tid in sorted(EXPECTED_STANDEE)
                if on_disk[tid]['aura']['canvas_w'] == 128]
        self.assertTrue(tall, 'at least one real TALL aura id ships')
        for tid in tall:
            aura = on_disk[tid]['aura']
            self.assertEqual(aura['canvas_h'], 256, tid)
            self.assertLess(aura['canvas_w'], aura['canvas_h'], tid)


class LayerAssetTests(unittest.TestCase):
    def test_every_layer_id_has_a_catalog_token_and_the_expected_layer_canvas(self):
        for tid in sorted(EXPECTED_FILES):
            token = TOKEN_DIR / (tid + '.png')
            layer = LAYER_DIR / (tid + '.png')
            self.assertTrue(token.is_file(), f'missing flattened token {tid}')
            self.assertTrue(layer.is_file(), f'missing layer {tid}')
            with Image.open(token) as a, Image.open(layer) as b:
                self.assertEqual(a.size, (128, 128), tid)
                self.assertEqual(b.size, (EXPECTED_CANVAS[tid],) * 2, tid)
                self.assertEqual(b.mode, 'RGBA', tid)
                self.assertNotEqual(sha(token), sha(layer), f'{tid} layer is just the flattened token')

    def test_standee_layers_are_256_and_ordinary_layers_are_128(self):
        for tid in sorted(EXPECTED_STANDEE):
            self.assertEqual(Image.open(LAYER_DIR / (tid + '.png')).size, (STANDEE_CANVAS,) * 2, tid)
        for tid in sorted(EXPECTED_ORDINARY - EXPECTED_STANDEE):
            self.assertEqual(Image.open(LAYER_DIR / (tid + '.png')).size, (ORDINARY_CANVAS,) * 2, tid)

    def test_no_unlisted_layer_files(self):
        on_disk = {p.name for p in LAYER_DIR.glob('*.png')}
        expected = {tid + '.png' for tid in EXPECTED_FILES} | {'_disc.png'}
        self.assertEqual(on_disk, expected)

    def test_aura_textures_are_pot_scaled_standee_copies(self):
        # R42: every standee ships a 256px POT aura texture: the 256px layer
        # scaled so the aura quad is body + ~0.4 cell headroom, with the
        # creature lined up. The transparent border gives the SDM flames room
        # without R41's 2x-large flames. No ordinary layer or archived id ships
        # one.
        on_disk = {p.name for p in AURA_DIR.glob('*.png')}
        self.assertEqual(on_disk, {tid + '.png' for tid in EXPECTED_STANDEE})
        for tid in sorted(EXPECTED_STANDEE):
            layer = Image.open(LAYER_DIR / (tid + '.png')).convert('RGBA')
            aura = Image.open(AURA_DIR / (tid + '.png')).convert('RGBA')
            box = json.loads(GEOMETRY_JSON.read_text())[tid]
            abox = box['aura']
            cw, ch = abox['canvas_w'], abox['canvas_h']
            self.assertEqual(aura.size, (cw, ch), tid)
            self.assertEqual(aura.mode, 'RGBA', tid)
            self.assertIn(cw, (128, 256), tid)
            self.assertEqual(ch, 256, tid)
            # The border above the art and below the feet is transparent.
            for px in ((0, 0), (cw - 1, 0), (0, ch - 1), (cw - 1, ch - 1)):
                self.assertEqual(aura.getpixel(px)[3], 0, (tid, px))
            self.assertGreater(abox['top'], 0, tid)
            self.assertLessEqual(abox['bottom'], ch, tid)
            # The layer was scaled uniformly: the body-height ratio in the aura
            # matches the art-height ratio to within a resampled pixel.
            r_art = (abox['bottom'] - abox['top']) / (box['bottom'] - box['top'])
            body_in_aura = abox['body_top'] - abox['top']
            body_expected = r_art * (box['body_top'] - box['top'])
            self.assertLess(abs(body_in_aura - body_expected), 1.5, tid)
            # The aura body still carries the creature's alpha (not an empty box).
            region = aura.crop((abox['left'], abox['body_top'], abox['right'], abox['bottom']))
            self.assertGreater(region.getchannel('A').getextrema()[1], 8, tid)

    def test_shipped_aura_matches_independent_premultiplied_raster(self):
        # Independent oracle: read the recorded transform, never call/import
        # the builder. PIL EXTENT maps a source window onto the aura canvas;
        # the builder uses AFFINE. RGBa keeps colour premultiplied during sampling.
        geometry = json.loads(GEOMETRY_JSON.read_text())
        self.assertEqual(len(EXPECTED_STANDEE), 59)
        for tid in sorted(EXPECTED_STANDEE):
            with self.subTest(id=tid):
                box = geometry[tid]
                aura = box['aura']
                r = ((aura['right'] - aura['left'])
                     / (box['right'] - box['left']))
                ox = aura['left'] - box['left'] * r
                oy = aura['top'] - box['top'] * r
                size = (aura['canvas_w'], aura['canvas_h'])
                extent = (-ox / r, -oy / r,
                          (size[0] - ox) / r, (size[1] - oy) / r)
                with Image.open(LAYER_DIR / (tid + '.png')) as source:
                    source_alpha = source.getchannel('A').copy()
                    independent = source.convert('RGBa').transform(
                        size, Image.Transform.EXTENT, extent,
                        resample=Image.Resampling.BICUBIC).convert('RGBA')
                oracle = independent.getchannel('A').point(
                    lambda a: 255 if a > 8 else 0).getbbox()
                with Image.open(AURA_DIR / (tid + '.png')) as shipped:
                    raster = shipped.getchannel('A').point(
                        lambda a: 255 if a > 8 else 0).getbbox()
                self.assertIsNotNone(oracle)
                self.assertIsNotNone(raster)
                for i, edge in enumerate(('left', 'top', 'right', 'bottom')):
                    self.assertLessEqual(abs(oracle[i] - raster[i]), 1.5,
                                         (tid, edge, 'oracle versus shipped'))
                    # Geometry uses source alpha >8. Resampling can erase a
                    # threshold-straddling wisp: horned-horror left max=9,
                    # output columns 63/64/65 max=8/7/5, bbox starts at 66
                    # versus geometry 63.584. Only such weak edges may inset.
                    inset = ((oracle[i] - aura[edge]) if i < 2
                             else (aura[edge] - oracle[i]))
                    self.assertGreaterEqual(inset, -1.5,
                                            (tid, edge, 'raster outside geometry'))
                    if inset > 1.5:
                        strip = {
                            'left': (box['left'], 0, box['left'] + 1, box['canvas']),
                            'right': (box['right'] - 1, 0, box['right'], box['canvas']),
                            'top': (0, box['top'], box['canvas'], box['top'] + 1),
                            'bottom': (0, box['bottom'] - 1, box['canvas'], box['bottom']),
                        }[edge]
                        edge_max = source_alpha.crop(strip).getextrema()[1]
                        self.assertLessEqual(edge_max, 2 * 8,
                            (tid, edge, 'strong source edge inset',
                             'source-edge max alpha', edge_max, 'inset px', inset))

    def test_every_standee_has_gate_headroom_and_bounded_diagonal(self):
        import math
        shared = json.loads((ROOT / 'tools/standee_aura_contract.json').read_text())
        headroom = (shared['AURA_FLAME_ABOVE_TOP_FLOOR_CELLS']
                    + shared['AURA_TIP_BUDGET_CELLS'])
        self.assertEqual(shared['AURA_FLAME_ABOVE_TOP_FLOOR_CELLS'], 0.3)
        self.assertEqual(headroom, 0.5)
        code = "local T=assert(loadfile('overload/mod/class/CheckerTokens.lua'))() local S=assert(loadfile('overload/mod/class/CheckerTokenStyle.lua'))() for id in pairs(T.standee_ids) do print(id,S.standeeHeight(id)) end"
        caps = dict((line.split()[0], float(line.split()[1])) for line in subprocess.check_output(
            ['luajit', '-e', code], cwd=ROOT, text=True).splitlines())
        geom = json.loads(GEOMETRY_JSON.read_text())
        for tid in EXPECTED_STANDEE:
            with self.subTest(id=tid):
                b = geom[tid]; a = b['aura']
                factor = min(caps[tid] / (a['bottom'] - a['body_top']),
                             1 / (a['right'] - a['left']))
                # Positive distance from quad top to art top, in map cells.
                self.assertGreaterEqual(a['top'] * factor, headroom - 1e-9)
                w, h = a['canvas_w'] * factor, a['canvas_h'] * factor
                diag = math.hypot(w, h)
                self.assertGreaterEqual(diag, 2.2)
                self.assertLessEqual(diag, 2.6 + 1e-9)
                if a['canvas_w'] == 128:
                    # Maximum shipped art 1.75 + shared headroom 0.5;
                    # aspect 1:2 gives diagonal h*sqrt(5)/2.
                    self.assertLessEqual(h, 2.25 + 1e-9)
                    self.assertLessEqual(diag, 2.25 * math.sqrt(5) / 2 + 1e-9)

    def test_disc_exists_and_is_a_normalised_token_canvas(self):
        disc = LAYER_DIR / '_disc.png'
        self.assertTrue(disc.is_file())
        with Image.open(disc) as im:
            self.assertEqual(im.size, (128, 128))
            self.assertEqual(im.mode, 'RGBA')
        alpha = Image.open(disc).getchannel('A')
        self.assertEqual(alpha.getpixel((64, 64)), 255)
        self.assertEqual(alpha.getpixel((1, 1)), 0)
        self.assertEqual(alpha.getpixel((126, 126)), 0)

    def test_source_provenance_is_recorded(self):
        self.assertTrue((ART / 'PROVENANCE.md').is_file())
        text = (ART / 'PROVENANCE.md').read_text()
        self.assertIn('birefnet-general', text)
        self.assertIn('tools/build_token_layers.py', text)
        for tid in sorted(EXPECTED_FILES):
            mask = ART / tid / f'mask-{EXPECTED_CANVAS[tid]}.png'
            self.assertTrue(mask.is_file(), tid)
            self.assertTrue((ART / tid / 'creature.png').is_file(), tid)
            self.assertEqual(sha(ART / tid / 'creature.png'), sha(LAYER_DIR / (tid + '.png')), tid)
        self.assertEqual(sha(ART / 'disc/_disc.png'), sha(LAYER_DIR / '_disc.png'))


class ToolContractTests(unittest.TestCase):
    def test_build_aura_tall_synthetic_box(self):
        # R48 item 4: call the PRODUCTION build_aura on a synthetic box whose
        # H > 2.6/sqrt(2) forces the TALL branch, and pin the 128x256 canvas
        # and the horizontal centring at texture x=64.
        import importlib.util
        import numpy as np
        spec = importlib.util.spec_from_file_location(
            'build_token_layers', ROOT / 'tools' / 'build_token_layers.py')
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        cre = np.zeros((256, 256, 4), np.uint8)
        cre[20:240, 78:178, :3] = 200
        cre[20:240, 78:178, 3] = 255
        data, abox = mod.build_aura(cre, 'synthetic-tall', 40, 1.75)
        self.assertEqual((abox['canvas_w'], abox['canvas_h']), (128, 256))
        self.assertEqual(data.shape, (256, 128, 4))
        self.assertLessEqual(abs((abox['left'] + abox['right']) / 2 - 64), 1,
                        'synthetic TALL aura is centred at texture x=64')
        self.assertLessEqual(abox['right'], 128)

    def test_width_bound_aura_preserves_exact_layer_transform(self):
        # Regression for the R50 five width-bound ids. Geometry must preserve
        # the layer transform, even when no integer raster bbox can have the
        # same aspect ratio. Keep the existing Lua 1e-9 gate unchanged.
        import importlib.util
        import numpy as np
        spec = importlib.util.spec_from_file_location(
            'build_token_layers', ROOT / 'tools' / 'build_token_layers.py')
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        for width, cap in ((133, 1.703125), (150, 1.609375),
                           (168, 1.53125), (177, 1.328125), (151, 1.625)):
            with self.subTest(width=width):
                cre = np.zeros((256, 256, 4), np.uint8)
                left = (256 - width) // 2
                cre[18:238, left:left + width, :] = 255
                data, aura = mod.build_aura(cre, 'width-bound', 18, cap)
                r = (aura['bottom'] - aura['body_top']) / 220
                factor = min(cap / (aura['bottom'] - aura['body_top']),
                             1 / (aura['right'] - aura['left']))
                self.assertLess(abs(factor * 48 - (48 / width) / r), 1e-9)
                self.assertLess(abs((aura['right'] - aura['left']) / r - width), 1e-9)
                self.assertLess(abs((aura['left'] + aura['right']) / 2
                                    - aura['canvas_w'] / 2), 1e-9)
                self.assertGreater(data[..., 3].max(), 128)

    def test_tool_reads_the_file_set_not_the_flag(self):
        text = (ROOT / 'tools/build_token_layers.py').read_text()
        self.assertIn('R30-scratch/venv', text)
        self.assertIn('never run from packaging', text.lower())
        # The build must not assert the ordinary switch is on.
        self.assertNotIn('layer_trial is off; nothing to build', text)
        self.assertIn('layer_file_ids', text)
        self.assertIn('token-layer-geometry.lua', text)
        # R38: the standee canvas is a per-file geometry field, not a global.
        self.assertIn('STANDEE_SIZE = 256', text)
        self.assertIn("box['canvas'] = canvas", text)
        # R46: the aura texture is 256x256 square or 128x256 tall; the branch
        # and the per-axis canvas fields are pinned here.
        self.assertIn('AURA_TALL_W, AURA_TALL_H = 128, 256', text)
        self.assertIn('canvas_w, canvas_h = AURA_TALL_W, AURA_TALL_H', text)
        self.assertIn('canvas_w = canvas_h = AURA_CANVAS', text)
        self.assertIn('abox[%s]' % repr('canvas_w'), text)
        self.assertIn('abox[%s]' % repr('canvas_h'), text)
        self.assertFalse((ROOT / 'data' / 'build_token_layers.py').exists())


if __name__ == '__main__':
    unittest.main()
