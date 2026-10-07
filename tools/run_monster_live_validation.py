#!/usr/bin/env python3
"""Monster batch A/B live check (2026-09-29): one isolated offline cold start per scene.

Only tools/launch_fixture.py, tools/fixture_debug.py-style bridge files and
tools/fixture_command.py are used. Every scene launches its own game and Xvfb
and stops exactly those PIDs afterwards. Natural actors are inspected in
place (the hero may be moved beside them for a picture); `placed` actors come
from the zone's own npc_list and are always labelled placed in the census.
"""
import argparse
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True
from launch_fixture import SESSION
from run_norgos_validation import stop_started

ADDON = Path(__file__).resolve().parents[1]
HOME = SESSION / 'home/.t-engine/4.0/tome'
LOG = SESSION / 'game.log'
OUT = ADDON / 'evidence/monster-live-20260929'
SHOTS = OUT / 'screenshots'
CROPS = OUT / 'crops'
OUT_C = ADDON / 'evidence/monster-live-c-20260929'
OUT_D = ADDON / 'evidence/monster-live-d-20260929'
OUT_E = ADDON / 'evidence/monster-live-e-20260929'
OUT_F = ADDON / 'evidence/monster-live-f-20260929'
OUT_G = ADDON / 'evidence/monster-live-g-20260929'
OUT_H = ADDON / 'evidence/monster-live-h-20260929'
OUT_I = ADDON / 'evidence/monster-live-i-20260929'
OUT_J = ADDON / 'evidence/monster-batch-j-live-20260929'
OUT_K = ADDON / 'evidence/monster-batch-k-live-20260929'
OUT_L = ADDON / 'evidence/monster-batch-l-live-20260929'
OUT_M = ADDON / 'evidence/monster-batch-m-live-20260929'
OUT_N = ADDON / 'evidence/monster-batch-n-live-20260929'
OUT_O = ADDON / 'evidence/monster-batch-o-live-20260929'
OUT_P = ADDON / 'evidence/monster-batch-p-live-20260929'
OUT_Q = ADDON / 'evidence/monster-batch-q-live-20260929'
OUT_R = ADDON / 'evidence/monster-batch-r-live-20260929'
OUT_S = ADDON / 'evidence/monster-batch-s-live-20260929'
OUT_T = ADDON / 'evidence/monster-batch-t-live-20260930'
OUT_BU = ADDON / 'evidence/monster-batch-u-live-20260930'
OUT_BV = ADDON / 'evidence/monster-batch-v-live-20260930'
OUT_BW = ADDON / 'evidence/monster-batch-w-live-20260930'
OUT_BX = ADDON / 'evidence/monster-batch-x-live-20260930'
OUT_BY = ADDON / 'evidence/monster-batch-y-live-20260930'
OUT_BZ = ADDON / 'evidence/monster-batch-z-live-20260930'
OUT_BA = ADDON / 'evidence/monster-batch-aa-live-20260930'
OUT_BB = ADDON / 'evidence/monster-batch-ab-live-20260930'
OUT_BC = ADDON / 'evidence/monster-batch-ac-live-20260930'
OUT_BD = ADDON / 'evidence/monster-batch-ad-live-20261001'
OUT_BE = ADDON / 'evidence/monster-batch-ae-live-20261001'
OUT_BF = ADDON / 'evidence/monster-batch-af-live-20261001'
OUT_BUB = ADDON / 'evidence/monster-batch-ub1-live-20261001'
OUT_U = ADDON / 'evidence/token-summons-20260929'

A = ['Wrathroot', 'Snaproot', 'Minotaur of the Labyrinth', 'Sandworm Queen', 'Corrupted Sand Wyrm',
     'Rantha the Worm', 'Varsha the Writhing', 'Norgos, the Frozen', 'electric eel', 'ancient dragon turtle']
B = ['Shax the Slimy', 'Horned Horror', 'Norgos, the Guardian', 'skeleton archer', 'armoured skeleton warrior']
# Batch C (2026-09-29) maps the master archer; it is now checked like any token.
C = ['skeleton master archer']
# Batch D (2026-09-29, commits 2caaade/13e04b2): red/blue jelly complete the
# 6-colour jelly family; all six giant ant colours now ship (brown/blue via
# reviewer-approved waivers, carpenter/black via a redraw). The four
# remaining ooze/jelly identities stay native (no image= source, unresolved
# runtime actor.image) and are checked with the existing `native` step kind.
D = ['red jelly', 'blue jelly', 'giant white ant', 'giant brown ant', 'giant carpenter ant',
     'giant blue ant', 'giant yellow ant', 'giant black ant']
# Batch E (2026-09-29, commits a3e6fc7/<this commit>): all 12 recommended
# zone-finale bosses (CONTRACTS-B5-B7-20260929.md §2). 5 shipped without a
# waiver (a3e6fc7); the other 7 ship under the reviewer-approved base_drift
# waiver in art/production/waivers/monster-batch-e.json. Ungole and
# Kryl-Feijan are dark subjects on the dark base disc and are the specific
# 48px-on-real-floor readability judgment call this live check makes;
# Atamathon's documented nicer_tiles-off native fallback is also confirmed
# here, not just asserted from static source reading.
E = ['Lady Zoisla the Tidebringer', 'Urkis, the High Tempest', 'Golbug the Destroyer', 'Brotoq the Reaver',
     'Ungolë', 'Half-Finished Bone Giant', 'Kryl-Feijan', 'Atamathon the Giant Golem',
     'Ritch Great Hive Mother', 'The Mouth', 'The Abomination', 'Celia']
# Batch F (2026-09-29): the 3 wired native_tall identities (naga tidewarden,
# naga tidecaller shipped clean; shivgoroth, greater shivgoroth shipped under
# the reviewer-approved base_drift waiver in
# art/production/waivers/monster-batch-f.json). Kryl-Feijan is already in E
# above (redrawn art this batch, same identity/wiring). treant is also new
# this batch (removed from the token_mapping.lua excluded list). xhaiak
# arachnomancer / shiaak venomblade are NOT mapped (unresolved add_mos per
# evidence/monster-batch-f-20260929/source-contracts.json); they are probed
# with the `native` step kind only, to record what actually renders, per
# this task's explicit "do not map them" instruction.
F = ['naga tidewarden', 'naga tidecaller', 'treant', 'shivgoroth', 'greater shivgoroth']
# Batch G (2026-09-29): 12 tokens (11 clean + Massok under the approved waiver
# in art/production/waivers/monster-batch-g.json). Harno and xhaiak are the
# dark-subject judgments; Pale Drake vs The Master is judged side by side.
G = ['xhaiak arachnomancer', 'shiaak venomblade', 'dremling', 'Massok the Dragonslayer', 'The Master',
     'Pale Drake', 'Spellblaze Crystal', 'Rhaloren Inquisitor', 'Krogar', 'Fillarel Aldaren',
     'Harno, Herald of Last Hope', 'Lithfengel']
# Batch H (2026-09-29): 12 exact single-image tokens (119 total). Crimson
# crystal (scintillating-caves/old-forest crystaline/arena) and sanguine
# experiment (blighted-ruins only) never share a zone; they are compared from
# two separate scenes. shimmering crystal and orc necromancer are negatives.
H = ['sandworm', 'sandworm destroyer', 'sandworm burrower', 'white crystal', 'red crystal', 'crimson crystal',
     'poison ivy', 'honey tree', 'Necromancer', 'fleshy experiment', 'boney experiment', 'sanguine experiment']
NATIVE_H = ['shimmering crystal', 'orc necromancer']
# Batch I (2026-09-29): 12 exact single/native-tall tokens (131 total). Oozes are
# lined up with the shipped red/black/yellow/blue oozes; Norgan is also checked
# after joining the party (control="order"); elven corruptor stays native.
I = ['green ooze', 'crimson ooze', 'gelatinous cube', 'Malevolent Dimensional Jelly',
     "The Fragmented Essence of Harkor'Zun", "Harkor'Zun", 'Burb the snow giant champion', 'Norgan',
     'slimy crawler', 'Spellblaze Simulacrum', 'Acolyte of the Sect of Kryl-Feijan', "Z'quikzshl the skeletal mold"]
NATIVE_I = ['elven corruptor']
OOZES_SHIPPED = ['red ooze', 'black ooze', 'yellow ooze', 'blue ooze']
NATIVE = []
NATIVE_D = ['green ooze', 'crimson ooze', 'gelatinous cube', 'Malevolent Dimensional Jelly']
NATIVE_F = ['xhaiak arachnomancer', 'shiaak venomblade']
# Batch J (2026-09-29, commit 3f33d19): 11 guaranteed bosses/uniques. Kyless,
# Ben Cruthdar the Cursed and an uncovered Heart of the Gloom prefixed base
# stay native (negatives).
J = ['Shardskin', 'The Withering Thing', 'The Dreaming One', 'Weaver Queen', 'Murgol, the Yaech Lord',
     'Lady Nashva the Streambender', 'The Possessed', 'Subject Z', 'Grand Corruptor', 'Assassin Lord',
     'Ben Cruthdar, the Abomination']
NATIVE_J = ['Kyless', 'Ben Cruthdar, the Cursed']
# Batch K (2026-09-29, commit c93f5c5 + Grand Corruptor fix a3a0225): 12 aquatic/
# spider/ghoul/drem/tunneler identities. Negatives stay native.
K = ['squid', 'ink squid', 'water imp', 'Walrog', 'weaver hatchling', 'orb spinner', 'giant spider',
     'spitting spider', 'chitinous spider', 'ghoul', 'drem', 'gigantic sandworm tunneler', 'dremling']
NATIVE_K = ['gigantic corrosive tunneler', 'gigantic gravity worm']
# Batch L (2026-09-29, commit f40e507): orcs, Shaloren elves, nagas, yaech diver, Kyless.
# Negatives: Charred Scar ORC_ATTACK 'orc warrior' (different define_as) and elven cultist.
L = ['orc warrior', 'orc soldier', 'orc archer', 'elven guard', 'mean looking elven guard', 'elven mage',
     'elven tempest', 'elven blood mage', 'naga myrmidon', 'naga nereid', 'yaech diver', 'Kyless']
NATIVE_L = ['elven cultist']
PLACE_SRC_L = {'naga nereid@murgol-lair': '/data/zones/murgol-lair/npcs.lua', 'naga nereid@slazish-fen': '/data/zones/slazish-fen/npcs.lua',
               'naga myrmidon': '/data/general/npcs/naga.lua', 'yaech diver': '/data/general/npcs/yaech.lua',
               'elven guard': '/data/general/npcs/elven-warrior.lua', 'elven mage': '/data/general/npcs/elven-caster.lua',
               'elven tempest': '/data/general/npcs/elven-caster.lua', 'elven blood mage': '/data/general/npcs/elven-caster.lua',
               'mean looking elven guard': '/data/general/npcs/elven-warrior.lua',
               'orc warrior': '/data/general/npcs/orc.lua', 'orc soldier': '/data/general/npcs/orc.lua',
               'orc archer': '/data/general/npcs/orc.lua', 'Kyless': '/data/zones/keepsake-meadow/npcs.lua'}
# Batch M (2026-09-29, HEAD 5cfe96c): elementals (losgoroth, gwelgoroth, faeros, xorn families),
# Fyrk, and the elven cultist in Urh'Rok form. Negatives: monstrous losgoroth (other name/define_as),
# ultimate faeros, greater/ultimate telugoroth, Spacial Disturbance.
M = ['losgoroth', 'manaworm', 'telugoroth', 'gwelgoroth', 'greater gwelgoroth', 'ultimate gwelgoroth', 'faeros',
     'greater faeros', 'Fyrk, Faeros High Guard', 'umber hulk', 'xorn', 'xaren', 'elven cultist']
NATIVE_M = ['monstrous losgoroth', 'ultimate faeros', 'greater telugoroth', 'ultimate telugoroth', 'Spacial Disturbance']
PLACE_SRC_M = {'losgoroth': '/data/general/npcs/losgoroth.lua', 'manaworm': '/data/general/npcs/losgoroth.lua',
               'telugoroth': '/data/general/npcs/telugoroth.lua', 'gwelgoroth': '/data/general/npcs/gwelgoroth.lua',
               'greater gwelgoroth': '/data/general/npcs/gwelgoroth.lua',
               'ultimate gwelgoroth': '/data/general/npcs/gwelgoroth.lua',
               'faeros': '/data/general/npcs/faeros.lua', 'greater faeros': '/data/general/npcs/faeros.lua',
               'Fyrk, Faeros High Guard': '/data/zones/charred-scar/npcs.lua',
               'umber hulk': '/data/general/npcs/xorn.lua', 'xorn': '/data/general/npcs/xorn.lua',
               'xaren': '/data/general/npcs/xorn.lua', 'elven cultist': '/data/general/npcs/elven-caster.lua'}
PLACE_SRC_L.update(PLACE_SRC_M)
EXPECT = {'losgoroth': 'losgoroth', 'manaworm': 'manaworm', 'telugoroth': 'telugoroth', 'gwelgoroth': 'gwelgoroth',
          'greater gwelgoroth': 'greater-gwelgoroth', 'ultimate gwelgoroth': 'ultimate-gwelgoroth', 'faeros': 'faeros',
          'greater faeros': 'greater-faeros', 'Fyrk, Faeros High Guard': 'fyrk', 'umber hulk': 'umber-hulk', 'xorn': 'xorn',
          'xaren': 'xaren', 'monstrous losgoroth': 'monstrous-losgoroth-native', 'ultimate faeros': 'ultimate-faeros-native',
          'greater telugoroth': 'greater-telugoroth-native', 'ultimate telugoroth': 'ultimate-telugoroth-native',
          'Spacial Disturbance': 'spacial-disturbance-native',
          'orc warrior': 'orc-warrior', 'orc soldier': 'orc-soldier', 'orc archer': 'orc-archer',
          'elven guard': 'elven-guard', 'mean looking elven guard': 'mean-looking-elven-guard',
          'elven mage': 'elven-mage', 'elven tempest': 'elven-tempest', 'elven blood mage': 'elven-blood-mage',
          'naga myrmidon': 'naga-myrmidon', 'naga nereid': 'naga-nereid', 'yaech diver': 'yaech-diver',
          'elven cultist': 'elven-cultist',
          'squid': 'squid', 'ink squid': 'ink-squid', 'water imp': 'water-imp', 'Walrog': 'walrog',
          'weaver hatchling': 'weaver-hatchling', 'orb spinner': 'orb-spinner', 'giant spider': 'giant-spider',
          'spitting spider': 'spitting-spider', 'chitinous spider': 'chitinous-spider', 'ghoul': 'ghoul',
          'drem': 'drem', 'dremling': 'dremling', 'gigantic sandworm tunneler': 'gigantic-sandworm-tunneler',
          'gigantic corrosive tunneler': 'corrosive-tunneler-native', 'gigantic gravity worm': 'gravity-worm-native',
          'Kyless': 'kyless', 'Ben Cruthdar, the Cursed': 'ben-cruthdar-cursed-native', 'Shardskin': 'shardskin', 'The Withering Thing': 'the-withering-thing', 'The Dreaming One': 'the-dreaming-one',
          'Weaver Queen': 'weaver-queen', 'Murgol, the Yaech Lord': 'murgol', 'Lady Nashva the Streambender': 'lady-nashva',
          'The Possessed': 'the-possessed', 'Subject Z': 'subject-z', 'Grand Corruptor': 'grand-corruptor',
          'Assassin Lord': 'assassin-lord', 'Ben Cruthdar, the Abomination': 'ben-cruthdar-abomination',
          'Wrathroot': 'wrathroot', 'Snaproot': 'snaproot', 'Minotaur of the Labyrinth': 'minotaur-maze',
          'Sandworm Queen': 'sandworm-queen', 'Corrupted Sand Wyrm': 'corrupted-sand-wyrm',
          'Rantha the Worm': 'rantha', 'Varsha the Writhing': 'varsha', 'Norgos, the Frozen': 'norgos-frozen',
          'electric eel': 'electric-eel', 'ancient dragon turtle': 'ancient-dragon-turtle',
          'Shax the Slimy': 'shax', 'Horned Horror': 'horned-horror', 'Norgos, the Guardian': 'norgos-guardian',
          'skeleton archer': 'skeleton-archer', 'armoured skeleton warrior': 'armoured-skeleton-warrior',
          'skeleton master archer': 'skeleton-master-archer',
          'red jelly': 'red-jelly', 'blue jelly': 'blue-jelly',
          'giant white ant': 'giant-white-ant', 'giant brown ant': 'giant-brown-ant',
          'giant carpenter ant': 'giant-carpenter-ant', 'giant blue ant': 'giant-blue-ant',
          'giant yellow ant': 'giant-yellow-ant', 'giant black ant': 'giant-black-ant',
          'Lady Zoisla the Tidebringer': 'lady-zoisla', 'Urkis, the High Tempest': 'urkis',
          'Golbug the Destroyer': 'golbug', 'Brotoq the Reaver': 'brotoq', 'Ungolë': 'ungole',
          'Half-Finished Bone Giant': 'half-finished-bone-giant', 'Kryl-Feijan': 'kryl-feijan',
          'Atamathon the Giant Golem': 'atamathon', 'Ritch Great Hive Mother': 'ritch-hive-mother',
          'The Mouth': 'the-mouth', 'The Abomination': 'the-abomination', 'Celia': 'celia',
          'naga tidewarden': 'naga-tidewarden', 'naga tidecaller': 'naga-tidecaller', 'treant': 'treant',
          'shivgoroth': 'shivgoroth', 'greater shivgoroth': 'greater-shivgoroth',
          'xhaiak arachnomancer': 'xhaiak-arachnomancer', 'shiaak venomblade': 'shiaak-venomblade',
          'dremling': 'dremling', 'Massok the Dragonslayer': 'massok', 'The Master': 'the-master',
          'Pale Drake': 'pale-drake', 'Spellblaze Crystal': 'spellblaze-crystal',
          'Rhaloren Inquisitor': 'rhaloren-inquisitor', 'Krogar': 'krogar', 'Fillarel Aldaren': 'fillarel-aldaren',
          'Harno, Herald of Last Hope': 'harno', 'Lithfengel': 'lithfengel',
          'sandworm': 'sandworm', 'sandworm destroyer': 'sandworm-destroyer', 'sandworm burrower': 'sandworm-burrower',
          'white crystal': 'white-crystal', 'red crystal': 'red-crystal', 'crimson crystal': 'crimson-crystal',
          'poison ivy': 'poison-ivy', 'honey tree': 'honey-tree', 'Necromancer': 'necromancer',
          'fleshy experiment': 'fleshy-experiment', 'boney experiment': 'boney-experiment',
          'sanguine experiment': 'sanguine-experiment',
          'green ooze': 'green-ooze', 'crimson ooze': 'crimson-ooze', 'gelatinous cube': 'gelatinous-cube',
          'Malevolent Dimensional Jelly': 'malevolent-dimensional-jelly',
          "The Fragmented Essence of Harkor'Zun": 'harkor-zun-fragment', "Harkor'Zun": 'harkor-zun',
          'Burb the snow giant champion': 'burb-snow-giant-champion', 'Norgan': 'norgan',
          'slimy crawler': 'slimy-crawler', 'Spellblaze Simulacrum': 'spellblaze-simulacrum',
          'Acolyte of the Sect of Kryl-Feijan': 'kryl-feijan-acolyte',
          "Z'quikzshl the skeletal mold": 'zquikzshl',
          'red ooze': 'red-ooze', 'black ooze': 'black-ooze', 'yellow ooze': 'yellow-ooze', 'blue ooze': 'blue-ooze'}
LINEUP = ['skeleton archer', 'skeleton master archer', 'armoured skeleton warrior', 'skeleton warrior',
          'degenerated skeleton archer', 'skeleton mage']
# Batch D lineups: all six shipped colours of each family, in CheckerTokens.lua order.
ANTS = ['giant white ant', 'giant brown ant', 'giant carpenter ant', 'giant blue ant',
        'giant yellow ant', 'giant black ant']
JELLIES = ['green jelly', 'black jelly', 'white jelly', 'yellow jelly', 'red jelly', 'blue jelly']

# (label, zone, level, opts, steps). Step kinds:
#   natural NAME [tiles]          approach a naturally generated actor and capture
#   place NAME [tiles]            place the exact zone prototype beside the hero and capture
#   toggle NAME                   Native <-> Refined creature display round trip
#   hide NAME                     temporary native invisibility on NAME, capture, restore
#   unseen                        focus a mapped actor outside current FOV and capture
#   wound NAME                    half life so the health arc is partial, capture
#   friendly NAME / neutral NAME  temporary faction for ring colour check, capture
#   lineup                        clear, place the skeleton family row, capture 48/64/96
#   natural_or_place NAME [tiles] natural if generated on this level, else place (labelled placed)
#   native NAME                   place the exact zone prototype and record that it keeps native art
SCENES = [
    ('trollmire-flooded-L3', 'trollmire', 3, {'flooded': True}, [
        ('natural', 'Shax the Slimy', (64, 48, 96)), ('natural', 'electric eel', (64,)),
        ('toggle', 'Shax the Slimy'), ('wound', 'Shax the Slimy'), ('hide', 'Shax the Slimy'), ('unseen',)]),
    ('trollmire-flooded-L1', 'trollmire', 1, {'flooded': True}, [
        ('natural', 'electric eel', (64,)), ('place', 'dragon turtle', ()),
        ('place', 'ancient dragon turtle', (64, 48, 96))]),
    ('old-forest-default-L4', 'old-forest', 4, {'crystaline': False}, [
        ('natural', 'Wrathroot', (64, 48, 96)), ('place', 'Snaproot', (64, 48, 96))]),
    ('maze-collapsed-L4', 'maze', 4, {'collapsed': True}, [
        ('natural', 'Horned Horror', (64, 48, 96)), ('toggle', 'Horned Horror')]),
    ('maze-default-L2', 'maze', 2, {'collapsed': False}, [('natural', 'Minotaur of the Labyrinth', (64,))]),
    ('sandworm-default-L4', 'sandworm-lair', 4, {'bigworm': False}, [
        ('natural', 'Sandworm Queen', (64,)), ('place', 'Corrupted Sand Wyrm', (64,))]),
    ('sandworm-bigworm-L2', 'sandworm-lair', 2, {'bigworm': True}, [('natural', 'Sandworm Queen', (64,))]),
    ('daikara-default-L4', 'daikara', 4, {'volcano': False}, [('natural', 'Rantha the Worm', (64,))]),
    ('daikara-volcano-L4', 'daikara', 4, {'volcano': True}, [('natural', 'Varsha the Writhing', (64,))]),
    ('norgos-invaded-L3', 'norgos-lair', 3, {'invaded': True}, [('natural', 'Norgos, the Frozen', (64, 48, 96))]),
    ('norgos-default-L3', 'norgos-lair', 3, {'invaded': False}, [
        ('natural', 'Norgos, the Guardian', (64, 48, 96)), ('toggle', 'Norgos, the Guardian')]),
    ('dreadfell-L1', 'dreadfell', 1, {}, [
        ('natural', 'armoured skeleton warrior', (64,)), ('natural', 'skeleton archer', (64,)),
        ('natural', 'skeleton master archer', (64,)),
        ('lineup',), ('toggle', 'skeleton archer'), ('friendly', 'skeleton archer'),
        ('neutral', 'armoured skeleton warrior')]),
    ('halfling-ruins-L1', 'halfling-ruins', 1, {}, [
        ('natural', 'skeleton master archer', (64,)), ('natural', 'skeleton archer', (64,)),
        ('natural', 'armoured skeleton warrior', (64,))]),
    ('unremarkable-cave-L1', 'unremarkable-cave', 1, {}, [
        ('natural', 'skeleton master archer', (64,)), ('natural', 'skeleton archer', (64,)),
        ('natural', 'armoured skeleton warrior', (64,))]),
]

# Batch C (533341a) live check: redrawn skeleton archer / Horned Horror and the
# newly mapped skeleton master archer; skeleton magus must still be native.
SCENES_C = [
    ('dreadfell-L1', 'dreadfell', 1, {}, [
        ('natural_or_place', 'skeleton master archer', (64, 48, 96)), ('natural', 'skeleton archer', (64,)),
        ('lineup',), ('native', 'skeleton magus'), ('toggle', 'skeleton master archer')]),
    ('unremarkable-cave-L1', 'unremarkable-cave', 1, {}, [
        ('natural', 'skeleton master archer', (64, 48, 96)), ('natural', 'skeleton archer', (64,))]),
    # Extra cold start only for a naturally generated master archer (random pool).
    ('dreadfell-L1-master', 'dreadfell', 1, {}, [('natural', 'skeleton master archer', (64, 48, 96))]),
    ('maze-collapsed-L4', 'maze', 4, {'collapsed': True}, [
        ('natural', 'Horned Horror', (64, 48, 96)), ('toggle', 'Horned Horror')]),
    ('maze-default-L2', 'maze', 2, {'collapsed': False}, [
        ('natural', 'Minotaur of the Labyrinth', (64, 48, 96))]),
]

# Batch D (2caaade/13e04b2) live check: red/blue jelly and the six giant ant
# colours (brown/blue via waiver, carpenter/black redrawn). Old Forest DEFAULT
# has an explicit {type="insect", subtype="ant"} forest_clearing filter, so
# it is the best natural chance for the ants; Trollmire's lesser_vaults_list
# includes forest-ruined-building3, the only vault with a chance-based jelly
# spawn table, for the jellies. Both zones' npcs.lua load general/npcs/all.lua,
# so every identity here (including the four kept-native ooze/jelly ones) is
# also reachable through the zone's own npc_list for `place`/`native`.
SCENES_D = [
    ('old-forest-default-L4-ants', 'old-forest', 4, {'crystaline': False}, [
        ('natural_or_place', 'giant white ant', (64,)),
        ('natural_or_place', 'giant brown ant', (64,)),
        # Carpenter vs black is the hardest pair in the batch (REVIEW.md); shoot
        # both individually at all three sizes, not just in the lineup.
        ('natural_or_place', 'giant carpenter ant', (48, 64, 96)),
        ('natural_or_place', 'giant black ant', (48, 64, 96)),
        ('natural_or_place', 'giant blue ant', (64,)),
        ('natural_or_place', 'giant yellow ant', (64,)),
        ('lineup', 'ant', ANTS),
        ('toggle', 'giant carpenter ant'),
    ]),
    ('trollmire-flooded-L1-jellies', 'trollmire', 1, {'flooded': True}, [
        ('natural_or_place', 'red jelly', (64, 48, 96)),
        ('natural_or_place', 'blue jelly', (64,)),
        ('native', 'green ooze'), ('native', 'crimson ooze'),
        ('native', 'gelatinous cube'), ('native', 'Malevolent Dimensional Jelly'),
        ('lineup', 'jelly', JELLIES),
    ]),
]

# Batch E (2026-09-29): the 12 zone-finale bosses, one cold start per zone
# (deep-bellow hosts two on the same level, so 11 scenes cover all 12). Level
# numbers come from the zone.lua source, not the survey doc, which does not
# give levels: tempest-peak/ardhungol/blighted-ruins/ritch-tunnels use the
# native generator.actor "guardian"/"guardian_level" mechanic (unconditional
# on level generation -- see engine/generator/actor/Random.lua ~line 50-55);
# reknor/reknor-escape/deep-bellow(The Mouth)/last-hope-graveyard place the
# boss with an explicit defineTile(...) actor on their static final-level map
# (maps/zones/{reknor-last,reknor-escape-last,deep-bellow-last,
# last-hope-mausoleum}.lua); all four are natural on a cold entry to that
# level, same as the guardian mechanic. Lady Zoisla (slazish-fen L3, portal-
# destroy quest event), Kryl-Feijan (crypt-kryl-feijan L5, turn-counter altar
# event replacing NPC MELINDA), Atamathon (golem-graveyard L1, requires
# breaking ATAMATHON_BROKEN wall terrain) and The Abomination (deep-bellow
# L3, GameState:activateBackupGuardian -- only spawns in an "advanced"
# playthrough after The Mouth's death) are genuine scripted triggers, not
# reachable from a cold birth without simulating a multi-step quest; each
# uses `place` from the zone's own npc_list and is labelled placed, per this
# task's fallback instruction. `natural_or_place` is still used for the other
# 8 so the census (not this comment) is the source of truth for which ones
# were actually found generated.
SCENES_E = [
    ('slazish-fen-L3', 'slazish-fen', 3, {}, [
        ('place', 'Lady Zoisla the Tidebringer', (64, 48, 96)),
        ('toggle', 'Lady Zoisla the Tidebringer'),
    ]),
    ('tempest-peak-L2', 'tempest-peak', 2, {}, [
        ('natural_or_place', 'Urkis, the High Tempest', (64, 48, 96)),
    ]),
    ('reknor-L4', 'reknor', 4, {}, [
        ('natural_or_place', 'Golbug the Destroyer', (64, 48, 96)),
    ]),
    ('reknor-escape-L3', 'reknor-escape', 3, {}, [
        ('natural_or_place', 'Brotoq the Reaver', (64, 48, 96)),
    ]),
    ('ardhungol-L3', 'ardhungol', 3, {}, [
        # Dark spiderkin subject on the dark base disc -- the specific
        # readability judgment this batch's waiver conditioned on.
        ('natural_or_place', 'Ungolë', (48, 64, 96)),
    ]),
    ('blighted-ruins-L1', 'blighted-ruins', 1, {}, [
        ('natural_or_place', 'Half-Finished Bone Giant', (64, 48, 96)),
    ]),
    ('crypt-kryl-feijan-L5', 'crypt-kryl-feijan', 5, {}, [
        # Dark demon-major subject on the dark base disc -- the other
        # specific readability judgment this batch's waiver conditioned on.
        ('place', 'Kryl-Feijan', (48, 64, 96)),
    ]),
    ('golem-graveyard-L1', 'golem-graveyard', 1, {}, [
        ('place', 'Atamathon the Giant Golem', (64, 48, 96)),
        ('atamathon_fallback', 'Atamathon the Giant Golem'),
    ]),
    ('ritch-tunnels-L3', 'ritch-tunnels', 3, {}, [
        ('natural_or_place', 'Ritch Great Hive Mother', (64, 48, 96)),
    ]),
    ('deep-bellow-L3', 'deep-bellow', 3, {}, [
        ('natural_or_place', 'The Mouth', (64, 48, 96)),
        ('place', 'The Abomination', (64, 48, 96)),
    ]),
    ('last-hope-graveyard-L2', 'last-hope-graveyard', 2, {}, [
        ('natural_or_place', 'Celia', (64, 48, 96)),
    ]),
]

# Batch F (2026-09-29): naga tidewarden/tidecaller (slazish-fen, common
# rarity=1, level_range from 1/2 -- very likely natural at L3), treant
# (old-forest DEFAULT loads general/npcs/plant.lua; the same zone/level batch
# E already used for Wrathroot/Snaproot), shivgoroth/greater shivgoroth
# (norgos-lair only loads general/npcs/shivgoroth.lua when currentZone.
# is_invaded -- same invaded variant already used for Norgos, the Frozen),
# and the redrawn Kryl-Feijan (crypt-kryl-feijan, same turn-counter altar
# event as monster-batch-e, placed and labelled, art-only change this
# batch). xhaiak arachnomancer / shiaak venomblade (ardhungol, rarity 2/4,
# level_range from 38/35) are probed with `native` -- placed from the zone's
# own npc_list exactly like every other placed identity, but never wired
# into the catalog; the census row (image/add_mos/rendered_token) is the
# record this task asks for, not a mapping. One toggle (naga tidecaller,
# flagged as the dark-figure readability concern) covers the whole batch.
SCENES_F = [
    ('slazish-fen-L3', 'slazish-fen', 3, {}, [
        ('natural_or_place', 'naga tidewarden', (48, 64, 96)),
        ('natural_or_place', 'naga tidecaller', (48, 64, 96)),
        ('toggle', 'naga tidecaller'),
    ]),
    ('old-forest-default-L4', 'old-forest', 4, {'crystaline': False}, [
        ('natural_or_place', 'treant', (48, 64, 96)),
    ]),
    ('norgos-invaded-L3', 'norgos-lair', 3, {'invaded': True}, [
        ('natural_or_place', 'shivgoroth', (48, 64, 96)),
        ('natural_or_place', 'greater shivgoroth', (48, 64, 96)),
    ]),
    ('crypt-kryl-feijan-L5', 'crypt-kryl-feijan', 5, {}, [
        ('place', 'Kryl-Feijan', (48, 64, 96)),
    ]),
    ('ardhungol-L3', 'ardhungol', 3, {}, [
        # Task 2 runtime probe only: records actor.image, add_mos
        # (image/display_h/display_y) and rendered_token/display_image as
        # actually resolved at runtime. Not mapped this task; no crops
        # required (task 3's live-check list does not include these two).
        ('native', 'xhaiak arachnomancer'),
        ('native', 'shiaak venomblade'),
    ]),
]

# Batch G (2026-09-29): one cold start per zone. Most bosses are scripted
# (guardian/backup-guardian/final-map) or level-gated far above the zone's
# depth, so natural_or_place labels the census truthfully. Dreadfell also
# places The Master and Pale Drake side by side (lineup, custom offsets).
SCENES_G = [
    ('ardhungol-L3', 'ardhungol', 3, {}, [
        ('natural_or_place', 'xhaiak arachnomancer', (48, 64, 96)),
        ('natural_or_place', 'shiaak venomblade', (48, 64, 96)),
    ]),
    ('maze-collapsed-L4', 'maze', 4, {'collapsed': True}, [
        ('natural_or_place', 'dremling', (48, 64, 96)),
    ]),
    ('daikara-default-L4', 'daikara', 4, {'volcano': False}, [
        ('natural_or_place', 'Massok the Dragonslayer', (48, 64, 96)),
    ]),
    ('dreadfell-L9', 'dreadfell', 9, {}, [
        ('natural_or_place', 'The Master', (48, 64, 96)),
        ('natural_or_place', 'Pale Drake', (48, 64, 96)),
        ('lineup', 'master-vs-drake', ['Pale Drake', 'The Master'], [(-1, 1), (1, 1)]),
    ]),
    ('scintillating-caves-L5', 'scintillating-caves', 5, {}, [
        ('natural_or_place', 'Spellblaze Crystal', (48, 64, 96)),
    ]),
    ('rhaloren-camp-L3', 'rhaloren-camp', 3, {}, [
        ('natural_or_place', 'Rhaloren Inquisitor', (48, 64, 96)),
    ]),
    ('unremarkable-cave-L1', 'unremarkable-cave', 1, {}, [
        ('natural_or_place', 'Krogar', (48, 64, 96)),
        ('natural_or_place', 'Fillarel Aldaren', (48, 64, 96)),
    ]),
    ('reknor-L4', 'reknor', 4, {}, [
        ('natural_or_place', 'Harno, Herald of Last Hope', (48, 64, 96)),
        ('natural_or_place', 'Lithfengel', (48, 64, 96)),
        ('toggle', 'Harno, Herald of Last Hope'),
    ]),
]


# Batch H (2026-09-29): one cold start per zone. Natural where the native
# generator produced it, otherwise placed from the zone npc_list (labelled).
# Lineups clear the hero's surroundings, so natural captures come first.
SCENES_H = [
    ('sandworm-lair-L4', 'sandworm-lair', 4, {'bigworm': False}, [
        ('natural_or_place', 'sandworm', (48, 64, 96)),
        ('natural_or_place', 'sandworm destroyer', (48, 64, 96)),
        ('natural_or_place', 'sandworm burrower', (48, 64, 96)),
        ('lineup', 'sandworms', ['sandworm', 'sandworm destroyer', 'sandworm burrower', 'Sandworm Queen'],
         [(-3, 1), (-1, 1), (1, 1), (3, 1)]),
    ]),
    ('scintillating-caves-L5', 'scintillating-caves', 5, {}, [
        ('natural_or_place', 'white crystal', (48, 64, 96)),
        ('natural_or_place', 'red crystal', (48, 64, 96)),
        ('natural_or_place', 'crimson crystal', (48, 64, 96)),
        ('lineup', 'crystals', ['white crystal', 'red crystal', 'crimson crystal', 'Spellblaze Crystal'],
         [(-3, 1), (-1, 1), (1, 1), (3, 1)]),
        ('native', 'shimmering crystal'),
    ]),
    ('trollmire-default-L3', 'trollmire', 3, {'flooded': False}, [
        ('natural_or_place', 'poison ivy', (48, 64, 96)),
    ]),
    ('old-forest-default-L4', 'old-forest', 4, {'crystaline': False}, [
        ('natural_or_place', 'honey tree', (48, 64, 96)),
    ]),
    ('blighted-ruins-L2', 'blighted-ruins', 2, {}, [
        ('natural_or_place', 'Necromancer', (48, 64, 96)),
        ('natural_or_place', 'fleshy experiment', (48, 64, 96)),
        ('natural_or_place', 'boney experiment', (48, 64, 96)),
        ('natural_or_place', 'sanguine experiment', (48, 64, 96)),
        ('toggle', 'Necromancer'),
        ('lineup', 'ruins', ['Necromancer', 'fleshy experiment', 'boney experiment', 'sanguine experiment'],
         [(-3, 1), (-1, 1), (1, 1), (3, 1)]),
        ('native', 'orc necromancer', '/data/general/npcs/orc-rak-shor.lua'),
    ]),
]

SCENES_I = [
    ('sandworm-lair-L4', 'sandworm-lair', 4, {'bigworm': False}, [
        ('natural_or_place', 'green ooze', (48, 64, 96)),
        ('natural_or_place', 'crimson ooze', (48, 64, 96)),
        ('natural_or_place', 'gelatinous cube', (48, 64, 96)),
        ('natural_or_place', 'Malevolent Dimensional Jelly', (48, 64, 96)),
        ('lineup', 'oozes', OOZES_SHIPPED + ['green ooze', 'crimson ooze', 'gelatinous cube', 'Malevolent Dimensional Jelly'],
         [(-3, 1), (-1, 1), (1, 1), (3, 1), (-3, 3), (-1, 3), (1, 3), (3, 3)]),
    ]),
    ('tempest-peak-L1', 'tempest-peak', 1, {}, [
        ('natural_or_place', "The Fragmented Essence of Harkor'Zun", (48, 64, 96)),
        ('natural_or_place', "Harkor'Zun", (48, 64, 96)),
        ('settle', "Harkor'Zun"),
        ('toggle', "Harkor'Zun", '-cluttered'),
        ('toggle_again', "Harkor'Zun"),
        ('clean_place', 'Burb the snow giant champion', (48, 64, 96)),
        ('toggle', 'Burb the snow giant champion'),
    ]),
    ('reknor-escape-L1', 'reknor-escape', 1, {}, [
        ('norgan',),
        ('natural_or_place', "Z'quikzshl the skeletal mold", (48, 64, 96)),
    ]),
    ('deep-bellow-L3', 'deep-bellow', 3, {}, [
        ('natural_or_place', 'slimy crawler', (48, 64, 96)),
    ]),
    ('scintillating-caves-L5', 'scintillating-caves', 5, {}, [
        ('natural_or_place', 'Spellblaze Simulacrum', (48, 64, 96)),
    ]),
    ('crypt-kryl-feijan-L5', 'crypt-kryl-feijan', 5, {}, [
        ('natural_or_place', 'Acolyte of the Sect of Kryl-Feijan', (48, 64, 96)),
        ('native', 'elven corruptor'),
    ]),
]

SCENES_J = [
    ('old-forest-crystaline-L4', 'old-forest', 4, {'crystaline': True}, [
        ('natural_or_place', 'Shardskin', (48, 64, 96))]),
    ('heart-gloom-default-L3', 'heart-gloom', 3, {'purified': False}, [
        ('natural_or_place', 'The Withering Thing', (48, 64, 96)),
        ('gloom', 'brown bear', (48, 64)), ('gloom', 'poison ivy', (48, 64)),
        ('gloom', 'cave bear', (48,)), ('gloom', 'war bear', (48,))]),
    ('heart-gloom-purified-L3', 'heart-gloom', 3, {'purified': True}, [
        ('natural_or_place', 'The Dreaming One', (48, 64, 96)),
        ('gloom', 'black bear', (48,)), ('gloom', 'honey tree', (48,)), ('gloom', 'cave bear', (48,))]),
    ('unhallowed-morass-L3', 'unhallowed-morass', 3, {}, [
        ('natural_or_place', 'Weaver Queen', (48, 64, 96)),
        ('toggle', 'Weaver Queen'), ('toggle_again', 'Weaver Queen')]),
    ('murgol-lair-default-L3', 'murgol-lair', 3, {'invasion': False}, [
        ('natural_or_place', 'Murgol, the Yaech Lord', (48, 64, 96))]),
    ('murgol-lair-invasion-L3', 'murgol-lair', 3, {'invasion': True}, [
        ('natural_or_place', 'Lady Nashva the Streambender', (48, 64, 96)),
        ('toggle', 'Lady Nashva the Streambender'), ('toggle_again', 'Lady Nashva the Streambender')]),
    ('ruins-kor-pul-hideout-L3', 'ruins-kor-pul', 3, {'hideout': True}, [
        ('natural_or_place', 'The Possessed', (48, 64, 96)),
        ('toggle', 'The Possessed'), ('toggle_again', 'The Possessed')]),
    ('halfling-ruins-L4', 'halfling-ruins', 4, {}, [
        ('natural_or_place', 'Subject Z', (48, 64, 96))]),
    ('mark-spellblaze-L2', 'mark-spellblaze', 2, {}, [
        ('natural_or_place', 'Grand Corruptor', (48, 64, 96))]),
    ('town-zigur-L1', 'town-zigur', 1, {}, [
        ('natural_or_place', 'Grand Corruptor', (48, 64, 96))]),
    ('thieves-tunnels-L2', 'thieves-tunnels', 2, {}, [
        ('natural_or_place', 'Assassin Lord', (48, 64, 96))]),
    ('temporal-rift-L4', 'temporal-rift', 4, {}, [
        ('natural_or_place', 'Ben Cruthdar, the Abomination', (48, 64, 96))]),
    ('town-lumberjack-village-L1', 'town-lumberjack-village', 1, {}, [
        ('natural_or_place', 'Ben Cruthdar, the Cursed', (48,))]),
    # Kyless is a static-map actor on level 6 (keepsake-cave-last); a `native`
    # placement from the zone list errors inside keepsake-meadow/npcs.lua:376,
    # so he is inspected naturally there.
    ('keepsake-meadow-L6', 'keepsake-meadow', 6, {}, [
        ('natural_or_place', 'Kyless', (48, 64, 96))]),
    ('halfling-ruins-lineup-L1', 'halfling-ruins', 1, {}, [
        ('lineup', 'bosses-j',
         [('Subject Z', None), ('Murgol, the Yaech Lord', '/data/zones/murgol-lair/npcs.lua'),
          ('Lady Nashva the Streambender', '/data/zones/murgol-lair/npcs.lua'),
          ('The Possessed', '/data/zones/ruins-kor-pul/npcs.lua')],
         [(-3, 1), (-1, 1), (1, 1), (3, 1)])]),
]

SCENES_K = [
    ('flooded-cave-L1', 'flooded-cave', 1, {}, [
        ('natural_or_place', 'squid', (48, 64, 96)),
        ('natural_or_place', 'ink squid', (48, 64, 96)),
        ('natural_or_place', 'water imp', (48, 64, 96))]),
    ('flooded-cave-L2', 'flooded-cave', 2, {}, [
        ('natural_or_place', 'Walrog', (48, 64, 96)),
        ('toggle', 'Walrog'), ('toggle_again', 'Walrog')]),
    ('ardhungol-L3', 'ardhungol', 3, {}, [
        ('natural_or_place', 'giant spider', (48, 64, 96)),
        ('natural_or_place', 'spitting spider', (48, 64, 96)),
        ('natural_or_place', 'chitinous spider', (48, 64, 96))]),
    ('unhallowed-morass-L3', 'unhallowed-morass', 3, {}, [
        ('natural_or_place', 'weaver hatchling', (48, 64, 96)),
        ('natural_or_place', 'orb spinner', (48, 64, 96))]),
    ('halfling-ruins-L1', 'halfling-ruins', 1, {}, [
        ('natural_or_place', 'ghoul', (48, 64, 96))]),
    ('deep-bellow-L3', 'deep-bellow', 3, {}, [
        ('natural_or_place', 'drem', (48, 64, 96)),
        ('natural_or_place', 'dremling', (48, 64, 96))]),
    ('sandworm-lair-L4', 'sandworm-lair', 4, {'bigworm': False}, [
        ('natural_or_place', 'gigantic sandworm tunneler', (48, 64, 96)),
        ('toggle', 'gigantic sandworm tunneler'), ('toggle_again', 'gigantic sandworm tunneler'),
        ('native', 'gigantic corrosive tunneler'), ('native', 'gigantic gravity worm')]),
    ('tutorial-combat-stats-L1', 'tutorial-combat-stats', 1, {}, [
        ('native', 'giant spider', None, 'TUT_SPIDER_1')]),
    ('mark-spellblaze-L2', 'mark-spellblaze', 2, {}, [
        ('natural_or_place', 'Grand Corruptor', (48, 64, 96)),
        ('gc', 'Grand Corruptor')]),
    ('town-zigur-L1', 'town-zigur', 1, {}, [
        ('natural_or_place', 'Grand Corruptor', (48, 64, 96)),
        ('gc', 'Grand Corruptor')]),
    ('halfling-ruins-lineup-L1', 'halfling-ruins', 1, {}, [
        ('lineup', 'batch-k',
         [('giant spider', '/data/general/npcs/spider.lua'), ('orb spinner', '/data/zones/unhallowed-morass/npcs.lua'),
          ('ghoul', '/data/general/npcs/ghoul.lua'), ('drem', '/data/general/npcs/horror-corrupted.lua'),
          ('squid', '/data/general/npcs/aquatic_critter.lua'), ('Walrog', '/data/general/npcs/aquatic_demon.lua')],
         [(-3, 1), (-2, 1), (-1, 1), (1, 1), (2, 1), (3, 1)])]),
]

SCENES_L = [
    ('reknor-L1', 'reknor', 1, {}, [
        ('natural_or_place', 'orc warrior', (48, 64, 96)),
        ('natural_or_place', 'orc soldier', (48, 64, 96)),
        ('natural_or_place', 'orc archer', (48, 64, 96))]),
    ('reknor-L2', 'reknor', 2, {}, [
        ('natural_or_place', 'orc warrior', (48, 64, 96)),
        ('natural_or_place', 'orc soldier', (48, 64, 96)),
        ('natural_or_place', 'orc archer', (48, 64, 96))]),
    ('rhaloren-camp-L1', 'rhaloren-camp', 1, {}, [
        ('natural_or_place', 'elven guard', (48, 64, 96)),
        ('natural_or_place', 'elven mage', (48, 64, 96)),
        ('natural_or_place', 'elven tempest', (48, 64, 96)),
        ('natural_or_place', 'mean looking elven guard', (48, 64, 96))]),
    ('mark-spellblaze-L1', 'mark-spellblaze', 1, {}, [
        ('natural_or_place', 'elven blood mage', (48, 64, 96)),
        ('natural_or_place', 'elven guard', (48, 64, 96)),
        ('natural_or_place', 'elven mage', (48, 64, 96))]),
    ('crypt-kryl-feijan-L1', 'crypt-kryl-feijan', 1, {}, [
        ('natural_or_place', 'elven blood mage', (48, 64, 96)),
        ('natural_or_place', 'mean looking elven guard', (48, 64, 96)),
        ('natural_or_place', 'elven tempest', (48, 64, 96))]),
    ('murgol-lair-L1', 'murgol-lair', 1, {}, [
        ('natural_or_place', 'naga myrmidon', (48, 64, 96)),
        ('natural_or_place', 'naga nereid', (48, 64, 96)),
        ('toggle', 'naga nereid'), ('toggle_again', 'naga nereid'),
        ('natural_or_place', 'yaech diver', (48, 64, 96))]),
    ('slazish-fen-L1', 'slazish-fen', 1, {}, [
        ('natural_or_place', 'naga myrmidon', (48, 64, 96)),
        ('natural_or_place', 'naga nereid', (48, 64, 96)),
        ('natural_or_place', 'yaech diver', (48, 64, 96))]),
    ('temple-of-creation-L1', 'temple-of-creation', 1, {}, [
        ('natural_or_place', 'naga myrmidon', (48, 64, 96)),
        ('natural_or_place', 'naga nereid', (48, 64, 96)),
        ('natural_or_place', 'yaech diver', (48, 64, 96))]),
    ('keepsake-meadow-L6', 'keepsake-meadow', 6, {}, [
        ('natural_or_place', 'Kyless', (48, 64, 96)),
        ('toggle', 'Kyless'), ('toggle_again', 'Kyless')]),
    ('charred-scar-L1', 'charred-scar', 1, {}, [
        ('native', 'orc warrior', None, 'ORC_ATTACK')]),
    ('reknor-cultist-L1', 'reknor', 1, {}, [
        ('native', 'elven cultist', '/data/general/npcs/elven-caster.lua'),
        ('inspect', 'elven cultist')]),
    ('keepsake-lineup-L6', 'keepsake-meadow', 6, {}, [
        ('lineup', 'batch-l',
         [('orc warrior', '/data/general/npcs/orc.lua'), ('orc soldier', '/data/general/npcs/orc.lua'),
          ('orc archer', '/data/general/npcs/orc.lua'),
          ('mean looking elven guard', '/data/general/npcs/elven-warrior.lua'),
          ('Kyless', None),
          ('elven mage', '/data/general/npcs/elven-caster.lua'),
          ('elven blood mage', '/data/general/npcs/elven-caster.lua')],
         [(-3, 1), (-2, 1), (-1, 1), (1, 1), (2, 1), (3, 1), (0, 2)])]),
]

# Batch N (2026-09-29, HEAD cc7c275): vampires, wights, ghast/ghoulking, bone giant, skeleton magus,
# shadow stalker, The Shade of Telos. Negatives: barrow/emperor wight, eternal/heavy
# bone giant, skeleton mage. (The vampire lord was a native negative here; batch AC maps it, so it is now a positive.)
N = ['skeleton magus', 'ghast', 'ghoulking', 'bone giant', 'lesser vampire', 'vampire', 'master vampire', 'elder vampire',
     'forest wight', 'grave wight', 'shadow stalker', 'The Shade of Telos', 'vampire lord']
NATIVE_N = ['barrow wight', 'emperor wight', 'eternal bone giant', 'heavy bone giant', 'skeleton mage']
PLACE_SRC_N = {'skeleton magus': '/data/general/npcs/skeleton.lua', 'skeleton mage': '/data/general/npcs/skeleton.lua',
               'ghast': '/data/general/npcs/ghoul.lua', 'ghoulking': '/data/general/npcs/ghoul.lua', 'ghoul': '/data/general/npcs/ghoul.lua',
               'bone giant': '/data/general/npcs/bone-giant.lua', 'eternal bone giant': '/data/general/npcs/bone-giant.lua',
               'heavy bone giant': '/data/general/npcs/bone-giant.lua', 'lesser vampire': '/data/general/npcs/vampire.lua', 'vampire': '/data/general/npcs/vampire.lua',
               'master vampire': '/data/general/npcs/vampire.lua', 'elder vampire': '/data/general/npcs/vampire.lua', 'vampire lord': '/data/general/npcs/vampire.lua',
               'forest wight': '/data/general/npcs/wight.lua', 'grave wight': '/data/general/npcs/wight.lua', 'barrow wight': '/data/general/npcs/wight.lua',
               'emperor wight': '/data/general/npcs/wight.lua', 'shadow stalker': '/data/zones/keepsake-meadow/npcs.lua',
               'The Shade of Telos': '/data/zones/telmur/npcs.lua'}
PLACE_SRC_L.update(PLACE_SRC_N)
EXPECT.update({'skeleton magus': 'skeleton-magus', 'ghast': 'ghast', 'ghoulking': 'ghoulking', 'bone giant': 'bone-giant',
               'lesser vampire': 'lesser-vampire', 'vampire': 'vampire', 'master vampire': 'master-vampire',
               'elder vampire': 'elder-vampire', 'forest wight': 'forest-wight', 'grave wight': 'grave-wight',
               'shadow stalker': 'shadow-stalker', 'The Shade of Telos': 'shade-of-telos',
               'vampire lord': 'vampire-lord', 'barrow wight': 'barrow-wight-native',
               'emperor wight': 'emperor-wight-native', 'eternal bone giant': 'eternal-bone-giant-native',
               'heavy bone giant': 'heavy-bone-giant-native', 'skeleton mage': 'skeleton-mage-native'})

# Batch O (2026-09-29, HEAD f2d4a4a): oozes, gigantic worms, carrion worm mass, bunny, dredgling,
# onilug, wretchling, brecklorn. Negatives: huge sandworm burrower (real), morphic ooze and bloated
# ooze (no live prototype: commented out / nonexistent -> synthetic NPC with the native name+image).
O = ['white ooze', 'slimy ooze', 'poison ooze', 'brittle clear ooze', 'gigantic corrosive tunneler', 'gigantic gravity worm',
     'carrion worm mass', 'cute little bunny', 'dredgling', 'onilug', 'wretchling', 'brecklorn', 'white jelly']
NATIVE_O = ['huge sandworm burrower', 'morphic ooze', 'bloated ooze']
PLACE_SRC_O = {'white ooze': '/data/general/npcs/ooze.lua', 'slimy ooze': '/data/general/npcs/ooze.lua',
               'poison ooze': '/data/general/npcs/ooze.lua', 'brittle clear ooze': '/data/general/npcs/ooze.lua',
               'gigantic corrosive tunneler': '/data/general/npcs/sandworm.lua', 'gigantic gravity worm': '/data/general/npcs/sandworm.lua',
               'gigantic sandworm tunneler': '/data/general/npcs/sandworm.lua', 'huge sandworm burrower': '/data/zones/sandworm-lair/npcs.lua',
               'carrion worm mass': '/data/general/npcs/vermin.lua', 'cute little bunny': '/data/zones/old-forest/npcs.lua',
               'dredgling': '/data/general/npcs/horror_temporal.lua', 'onilug': '/data/general/npcs/minor-demon.lua',
               'wretchling': '/data/general/npcs/minor-demon.lua', 'brecklorn': '/data/general/npcs/horror-corrupted.lua',
               'white jelly': '/data/general/npcs/jelly.lua'}
PLACE_SRC_L.update(PLACE_SRC_O)
EXPECT.update({'white ooze': 'white-ooze', 'slimy ooze': 'slimy-ooze', 'poison ooze': 'poison-ooze', 'brittle clear ooze': 'brittle-clear-ooze',
               'gigantic corrosive tunneler': 'gigantic-corrosive-tunneler', 'gigantic gravity worm': 'gigantic-gravity-worm',
               'carrion worm mass': 'carrion-worm-mass', 'cute little bunny': 'cute-little-bunny', 'dredgling': 'dredgling',
               'onilug': 'onilug', 'wretchling': 'wretchling', 'brecklorn': 'brecklorn', 'white jelly': 'white-jelly',
               'huge sandworm burrower': 'huge-sandworm-burrower-native', 'morphic ooze': 'morphic-ooze-native',
               'bloated ooze': 'bloated-ooze-native'})

# Batch P (2026-09-29, HEAD ee705b8): snow giants, minotaur, mountain trolls, ogres, Healer Astelrid.
# Negatives: ogre warmaster, ogre sentry (conclave-vault), maulotaur, patchwork troll. Existing
# Minotaur of the Labyrinth and Burb must keep their own ids. Wild-summon minotaur (summon-melee.lua:365)
# and the Elvala ogre rune-spinner are reported only.
P = ['snow giant', 'snow giant thunderer', 'snow giant boulder thrower', 'snow giant chieftain', 'minotaur', 'mountain troll',
     'mountain troll thunderer', 'ogre guard', 'ogre mauler', 'ogre rune-spinner', 'ogre pounder', 'Healer Astelrid',
     'Minotaur of the Labyrinth', 'Burb the snow giant champion']
NATIVE_P = ['ogre warmaster', 'ogre sentry', 'maulotaur', 'patchwork troll']
PLACE_SRC_P = {n: '/data/general/npcs/snow-giant.lua' for n in ('snow giant', 'snow giant thunderer', 'snow giant boulder thrower',
                                                                'snow giant chieftain', 'Burb the snow giant champion')}
PLACE_SRC_P.update({n: '/data/general/npcs/ogre.lua' for n in ('ogre guard', 'ogre mauler', 'ogre rune-spinner', 'ogre pounder', 'ogre warmaster')})
PLACE_SRC_P.update({'minotaur': '/data/general/npcs/minotaur.lua', 'maulotaur': '/data/general/npcs/minotaur.lua',
                    'Minotaur of the Labyrinth': '/data/zones/maze/npcs.lua',
                    'mountain troll': '/data/general/npcs/troll.lua', 'mountain troll thunderer': '/data/general/npcs/troll.lua',
                    'patchwork troll': '/data/general/npcs/troll.lua',
                    'Healer Astelrid': '/data/zones/conclave-vault/npcs.lua', 'ogre sentry': '/data/zones/conclave-vault/npcs.lua'})
PLACE_SRC_L.update(PLACE_SRC_P)
EXPECT.update({'snow giant': 'snow-giant', 'snow giant thunderer': 'snow-giant-thunderer',
               'snow giant boulder thrower': 'snow-giant-boulder-thrower', 'snow giant chieftain': 'snow-giant-chieftain',
               'minotaur': 'minotaur', 'mountain troll': 'mountain-troll', 'mountain troll thunderer': 'mountain-troll-thunderer',
               'ogre guard': 'ogre-guard', 'ogre mauler': 'ogre-mauler', 'ogre rune-spinner': 'ogre-rune-spinner',
               'ogre pounder': 'ogre-pounder', 'Healer Astelrid': 'healer-astelrid',
               'Minotaur of the Labyrinth': 'minotaur-maze', 'Burb the snow giant champion': 'burb-snow-giant-champion',
               'ogre warmaster': 'ogre-warmaster-native', 'ogre sentry': 'ogre-sentry-native', 'maulotaur': 'maulotaur-native',
               'patchwork troll': 'patchwork-troll-native'})

# Batch Q (2026-09-29, HEAD be5d0470): drakes, hatchlings, sand-drake, Rantha the Abomination, Briagh, Ukllmswwik.
# Negatives: multi-hued drake/hatchling, fire wyrm, greater multi-hued wyrm. Existing Varsha, Rantha the Worm and
# Corrupted Sand Wyrm keep their own ids. Wyrmic Fire Drake (summon-distance.lua:850) and Grand Arrival hatchling
# (:786) are reported only.
Q = ['fire drake hatchling', 'cold drake hatchling', 'storm drake hatchling', 'sand-drake', 'venom drake hatchling',
     'Rantha the Abomination', 'Briagh, Great Sand Wyrm', 'Ukllmswwik the Wise', 'fire drake', 'storm drake', 'cold drake',
     'venom drake', 'Rantha the Worm', 'Varsha the Writhing', 'Corrupted Sand Wyrm']
NATIVE_Q = ['multi-hued drake', 'multi-hued drake hatchling', 'fire wyrm', 'greater multi-hued wyrm']
PLACE_SRC_Q = {'fire drake hatchling': '/data/general/npcs/fire-drake.lua', 'fire drake': '/data/general/npcs/fire-drake.lua',
               'fire wyrm': '/data/general/npcs/fire-drake.lua',
               'cold drake hatchling': '/data/general/npcs/cold-drake.lua', 'cold drake': '/data/general/npcs/cold-drake.lua',
               'storm drake hatchling': '/data/general/npcs/storm-drake.lua', 'storm drake': '/data/general/npcs/storm-drake.lua',
               'venom drake hatchling': '/data/general/npcs/venom-drake.lua', 'venom drake': '/data/general/npcs/venom-drake.lua',
               'sand-drake': '/data/general/npcs/sandworm.lua', 'Corrupted Sand Wyrm': '/data/general/npcs/sandworm.lua',
               'Rantha the Abomination': '/data/zones/temporal-rift/npcs.lua', 'Briagh, Great Sand Wyrm': '/data/zones/briagh-lair/npcs.lua',
               'Ukllmswwik the Wise': '/data/zones/flooded-cave/npcs.lua', 'Rantha the Worm': '/data/zones/daikara/npcs.lua',
               'Varsha the Writhing': '/data/zones/daikara/npcs.lua',
               'multi-hued drake': '/data/general/npcs/multihued-drake.lua', 'multi-hued drake hatchling': '/data/general/npcs/multihued-drake.lua',
               'greater multi-hued wyrm': '/data/general/npcs/multihued-drake.lua'}
PLACE_SRC_L.update(PLACE_SRC_Q)
EXPECT.update({'fire drake hatchling': 'fire-drake-hatchling', 'cold drake hatchling': 'cold-drake-hatchling',
               'storm drake hatchling': 'storm-drake-hatchling', 'sand-drake': 'sand-drake', 'venom drake hatchling': 'venom-drake-hatchling',
               'Rantha the Abomination': 'rantha-abomination', 'Briagh, Great Sand Wyrm': 'briagh', 'Ukllmswwik the Wise': 'ukllmswwik',
               'fire drake': 'fire-drake', 'storm drake': 'storm-drake', 'cold drake': 'cold-drake', 'venom drake': 'venom-drake',
               'multi-hued drake': 'multi-hued-drake-native', 'multi-hued drake hatchling': 'multi-hued-drake-hatchling-native',
               'fire wyrm': 'fire-wyrm-native', 'greater multi-hued wyrm': 'greater-multi-hued-wyrm-native'})

# Batch R (2026-09-29, HEAD 886c0688): quasit, weaver young, orc necromancer/assassin, giant green/red ant, fate spinner,
# elven warrior, corrupted war dog, Warmaster Gnarg, Rak'shor, grannor'vor. Same-PNG comparisons: weaver hatchling
# (weaver young PNG), dire wolf and keepsake-meadow's plain war dog (canine_dw.png).
R = ['quasit', 'weaver young', 'orc necromancer', 'orc assassin', 'giant green ant', 'giant red ant', 'fate spinner',
     'elven warrior', 'corrupted war dog', 'Warmaster Gnarg', "Rak'shor, Grand Necromancer of the Pride", "grannor'vor",
     'weaver hatchling', 'dire wolf', 'war dog']
NATIVE_R = []
PLACE_SRC_R = {'quasit': '/data/general/npcs/minor-demon.lua', 'weaver young': '/data/general/npcs/spider.lua',
               'orc necromancer': '/data/general/npcs/orc-rak-shor.lua', 'orc assassin': '/data/general/npcs/orc.lua',
               'giant green ant': '/data/general/npcs/ant.lua', 'giant red ant': '/data/general/npcs/ant.lua',
               'fate spinner': '/data/zones/unhallowed-morass/npcs.lua', 'elven warrior': '/data/general/npcs/elven-warrior.lua',
               'corrupted war dog': '/data/zones/keepsake-meadow/npcs.lua', 'Warmaster Gnarg': '/data/zones/vor-armoury/npcs.lua',
               "Rak'shor, Grand Necromancer of the Pride": '/data/zones/rak-shor-pride/npcs.lua',
               "grannor'vor": '/data/general/npcs/horror-corrupted.lua', 'weaver hatchling': '/data/zones/unhallowed-morass/npcs.lua',
               'dire wolf': '/data/general/npcs/canine.lua', 'war dog': '/data/zones/keepsake-meadow/npcs.lua'}
PLACE_SRC_L.update(PLACE_SRC_R)
EXPECT.update({'quasit': 'quasit', 'weaver young': 'weaver-young', 'orc necromancer': 'orc-necromancer', 'orc assassin': 'orc-assassin',
               'giant green ant': 'giant-green-ant', 'giant red ant': 'giant-red-ant', 'fate spinner': 'fate-spinner',
               'elven warrior': 'elven-warrior', 'corrupted war dog': 'corrupted-war-dog', 'Warmaster Gnarg': 'warmaster-gnarg',
               "Rak'shor, Grand Necromancer of the Pride": 'rak-shor', "grannor'vor": 'grannor-vor',
               'weaver hatchling': 'weaver-hatchling', 'dire wolf': 'dire-wolf', 'war dog': 'war-dog-native'})

# Batch S (2026-09-29, HEAD ea7dd21a): Sunwall paladins, Charred Scar mages, Mindworm, Keepsake companions, undead uniques.
# Argoniel/Elandar are non-unique native_tall (two-cell); High Peak has same-define_as versions. Gates of Morning's
# define_as-less "human sun-paladin" (general/npcs/sunwall-town.lua) is the negative.
S = ['human sun-paladin', 'High Sun-Paladin Rodmour', 'Aluin the Fallen', 'Argoniel', 'Elandar', 'Mindworm', 'Berethh',
     'Companion Warrior', 'Companion Archer', 'Greater Mummy Lord', "Kor's Fury", 'Borfast the Broken']
NATIVE_S = []
PLACE_SRC_S = {'human sun-paladin': '/data/zones/charred-scar/npcs.lua', 'High Sun-Paladin Rodmour': '/data/zones/charred-scar/npcs.lua',
               'Aluin the Fallen': '/data/zones/trollmire/npcs.lua', 'Argoniel': '/data/zones/charred-scar/npcs.lua',
               'Elandar': '/data/zones/charred-scar/npcs.lua', 'Mindworm': '/data/zones/noxious-caldera/npcs.lua',
               'Berethh': '/data/zones/keepsake-meadow/npcs.lua', 'Companion Warrior': '/data/zones/keepsake-meadow/npcs.lua',
               'Companion Archer': '/data/zones/keepsake-meadow/npcs.lua', 'Greater Mummy Lord': '/data/zones/ancient-elven-ruins/npcs.lua',
               "Kor's Fury": '/data/zones/ruins-kor-pul/npcs.lua', 'Borfast the Broken': '/data/zones/dreadfell/npcs.lua'}
PLACE_SRC_L.update(PLACE_SRC_S)
EXPECT.update({'human sun-paladin': 'human-sun-paladin', 'High Sun-Paladin Rodmour': 'high-sun-paladin-rodmour',
               'Aluin the Fallen': 'aluin-the-fallen', 'Argoniel': 'argoniel', 'Elandar': 'elandar', 'Mindworm': 'mindworm',
               'Berethh': 'berethh', 'Companion Warrior': 'companion-warrior', 'Companion Archer': 'companion-archer',
               'Greater Mummy Lord': 'greater-mummy-lord', "Kor's Fury": 'kors-fury', 'Borfast the Broken': 'borfast'})

# Batch T (2026-09-30, HEAD 8ad5f105): caravan trio, Lost Merchant, war dog, Yeek Wayist, Nimisil, Slasul (unique tall,
# bound by define_as), Draebor, Yiilkgur's Weirdling Beast / Fortress Shadow / Pumpkin. Same-PNG checks: war dog vs dire wolf
# and corrupted war dog (canine_dw.png); caravan spectator PNGs vs ring-of-blood's spectator and the shadow claws.
T = ['caravan merchant', 'caravan guard', 'caravan porter', 'Lost Merchant', 'war dog', 'Yeek Wayist', 'Nimisil', 'Slasul',
     'Draebor, the Imp', 'Weirdling Beast', 'Fortress Shadow', 'Pumpkin, the little kitty']
NATIVE_T = ['spectator', 'shadow claw']
PLACE_SRC_T = {'caravan merchant': '/data/zones/keepsake-meadow/npcs.lua', 'caravan guard': '/data/zones/keepsake-meadow/npcs.lua',
               'caravan porter': '/data/zones/keepsake-meadow/npcs.lua', 'Lost Merchant': '/data/zones/thieves-tunnels/npcs.lua',
               'war dog': '/data/zones/keepsake-meadow/npcs.lua', 'Yeek Wayist': '/data/zones/halfling-ruins/npcs.lua',
               'Nimisil': '/data/zones/maze/npcs.lua', 'Slasul': '/data/zones/temple-of-creation/npcs.lua',
               'Draebor, the Imp': '/data/zones/demon-plane/npcs.lua', 'Weirdling Beast': '/data/zones/shertul-fortress/npcs.lua',
               'Fortress Shadow': '/data/zones/shertul-fortress/npcs.lua', 'Pumpkin, the little kitty': '/data/zones/shertul-fortress/npcs.lua'}
PLACE_SRC_L.update(PLACE_SRC_T)
EXPECT.update({'caravan merchant': 'caravan-merchant', 'caravan guard': 'caravan-guard', 'caravan porter': 'caravan-porter',
               'Lost Merchant': 'lost-merchant', 'war dog': 'war-dog', 'Yeek Wayist': 'yeek-wayist', 'Nimisil': 'nimisil',
               'Slasul': 'slasul', 'Draebor, the Imp': 'draebor', 'Weirdling Beast': 'weirdling-beast',
               'Fortress Shadow': 'fortress-shadow', 'Pumpkin, the little kitty': 'pumpkin'})

# Batch U (2026-09-30, HEAD 90dc1001): ritch trio, naga tide huntress / psyren, ancient elven mummy, orc master / grand master
# assassin, fire imp, gaeramarth, ninurlhing, fate weaver. Negatives: tutorial "hairy spider" (TUT_SPIDER_3, borrows the
# ninurlhing PNG) stays native; Ritch Great Hive Mother keeps its own id. Wild Gift Ritch Flamespitter wears ritch-flamespitter.
BU = ['ritch flamespitter', 'ritch impaler', 'chitinous ritch', 'naga tide huntress', 'naga psyren', 'ancient elven mummy',
      'orc master assassin', 'orc grand master assassin', 'fire imp', 'gaeramarth', 'ninurlhing', 'fate weaver',
      'ritch flamespitter (wild summon)', '火焰里奇 (野性召唤)']
NATIVE_BU = ['hairy spider']
PLACE_SRC_BU = {'naga tide huntress': '/data/general/npcs/naga.lua', 'naga psyren': '/data/general/npcs/naga.lua',
                'orc master assassin': '/data/general/npcs/orc.lua', 'orc grand master assassin': '/data/general/npcs/orc.lua',
                'fire imp': '/data/general/npcs/minor-demon.lua', 'gaeramarth': '/data/general/npcs/spider.lua',
                'ninurlhing': '/data/general/npcs/spider.lua', 'ritch flamespitter': '/data/zones/ritch-tunnels/npcs.lua',
                'ritch impaler': '/data/zones/ritch-tunnels/npcs.lua', 'chitinous ritch': '/data/zones/ritch-tunnels/npcs.lua',
                'ancient elven mummy': '/data/zones/ancient-elven-ruins/npcs.lua', 'fate weaver': '/data/zones/unhallowed-morass/npcs.lua',
                'Ritch Great Hive Mother': '/data/zones/ritch-tunnels/npcs.lua'}
PLACE_SRC_L.update(PLACE_SRC_BU)
EXPECT.update({'ritch flamespitter': 'ritch-flamespitter', 'ritch impaler': 'ritch-impaler', 'chitinous ritch': 'chitinous-ritch',
               'naga tide huntress': 'naga-tide-huntress', 'naga psyren': 'naga-psyren', 'ancient elven mummy': 'ancient-elven-mummy',
               'orc master assassin': 'orc-master-assassin', 'orc grand master assassin': 'orc-grand-master-assassin',
               'fire imp': 'fire-imp', 'gaeramarth': 'gaeramarth', 'ninurlhing': 'ninurlhing', 'fate weaver': 'fate-weaver',
               'ritch flamespitter (wild summon)': 'ritch-flamespitter', '火焰里奇 (野性召唤)': 'ritch-flamespitter',
               'Ritch Great Hive Mother': 'ritch-hive-mother'})

# Batch V (2026-09-30, HEAD c5b2888f): black crystal, faerlhing, losselhing, dredge, dolleg and eternal bone giant (native_tall),
# drem master, orc pyromancer / cryomancer / blood mage, bloated horror, yaech hunter. The Necromancer Assemble minion
# (e_bone_giant) wears the eternal-bone-giant token. None of these identities know Stealth natively: the stealth step teaches it.
BV = ['black crystal', 'faerlhing', 'losselhing', 'dredge', 'dolleg', 'eternal bone giant', 'drem master', 'orc pyromancer',
      'orc cryomancer', 'bloated horror', 'yaech hunter', 'orc blood mage']
NATIVE_BV = []
PLACE_SRC_BV = {'black crystal': '/data/general/npcs/crystal.lua', 'faerlhing': '/data/general/npcs/spider.lua',
                'losselhing': '/data/general/npcs/spider.lua', 'dredge': '/data/general/npcs/horror_temporal.lua',
                'dolleg': '/data/general/npcs/major-demon.lua', 'eternal bone giant': '/data/general/npcs/bone-giant.lua',
                'drem master': '/data/general/npcs/horror-corrupted.lua', 'orc pyromancer': '/data/general/npcs/orc-vor.lua',
                'orc cryomancer': '/data/general/npcs/orc-vor.lua', 'bloated horror': '/data/general/npcs/horror.lua',
                'yaech hunter': '/data/general/npcs/yaech.lua', 'orc blood mage': '/data/general/npcs/orc-rak-shor.lua'}
PLACE_SRC_L.update(PLACE_SRC_BV)
EXPECT.update({n: n.replace(' ', '-') for n in BV})

# Batch W (2026-09-30, HEAD 427cb74e): fiery/icy orc wyrmic (define_as ORC_FIRE_WYRMIC / ORC_ICE_WYRMIC), yaech mindslayer,
# heavy bone giant (native_tall), cave bear, war bear, grannor'vin, rotting mummy, banshee, giant fire/ice/lightning ant.
# The Necromancer Assemble minion at talent level 6 is h_bone_giant ("heavy bone giant"); a Lord of Skulls rename stays native.
BW = ['fiery orc wyrmic', 'icy orc wyrmic', 'yaech mindslayer', 'heavy bone giant', 'cave bear', 'war bear', "grannor'vin",
      'rotting mummy', 'banshee', 'giant fire ant', 'giant ice ant', 'giant lightning ant']
NATIVE_BW = []
PLACE_SRC_BW = {'fiery orc wyrmic': '/data/general/npcs/orc.lua', 'icy orc wyrmic': '/data/general/npcs/orc.lua',
                'yaech mindslayer': '/data/general/npcs/yaech.lua', 'heavy bone giant': '/data/general/npcs/bone-giant.lua',
                'cave bear': '/data/general/npcs/bear.lua', 'war bear': '/data/general/npcs/bear.lua',
                "grannor'vin": '/data/general/npcs/horror-corrupted.lua', 'rotting mummy': '/data/zones/ancient-elven-ruins/npcs.lua',
                'banshee': '/data/general/npcs/ghost.lua', 'giant fire ant': '/data/general/npcs/ant.lua',
                'giant ice ant': '/data/general/npcs/ant.lua', 'giant lightning ant': '/data/general/npcs/ant.lua'}
PLACE_SRC_L.update(PLACE_SRC_BW)
EXPECT.update({n: n.replace(' ', '-').replace("'", '-') for n in BW})

# Batch X (2026-09-30, HEAD 262a70a6): giant acid/army ant, yaech psion, skeleton assassin, blue crystal, elven corruptor,
# assassin (define_as THIEF_ASSASSIN; shadowblade shares it and stays native), greater telugoroth (native_tall), teluvorta,
# dread (also the Dread-talent minion), orc fighter, devourer.
BX = ['giant acid ant', 'giant army ant', 'yaech psion', 'skeleton assassin', 'blue crystal', 'elven corruptor', 'assassin',
      'greater telugoroth', 'teluvorta', 'dread', 'orc fighter', 'devourer']
NATIVE_BX = ['shadowblade']
PLACE_SRC_BX = {'giant acid ant': '/data/general/npcs/ant.lua', 'giant army ant': '/data/general/npcs/ant.lua',
                'yaech psion': '/data/general/npcs/yaech.lua', 'skeleton assassin': '/data/general/npcs/skeleton.lua',
                'blue crystal': '/data/general/npcs/crystal.lua', 'elven corruptor': '/data/general/npcs/elven-caster.lua',
                'assassin': '/data/general/npcs/thieve.lua', 'greater telugoroth': '/data/general/npcs/telugoroth.lua',
                'teluvorta': '/data/general/npcs/telugoroth.lua', 'dread': '/data/general/npcs/ghost.lua',
                'orc fighter': '/data/general/npcs/orc-grushnak.lua', 'devourer': '/data/general/npcs/horror.lua',
                'shadowblade': '/data/general/npcs/thieve.lua'}
PLACE_SRC_L.update(PLACE_SRC_BX)
EXPECT.update({n: n.replace(' ', '-') for n in BX})

# Batch Y (2026-09-30, HEAD 9c8d9bfb): uruivellas, thaurhereg, orc corruptor, temporal stalker, broken golem, golem, blade horror
# (define_as BLADEHORROR), animated mummy wrappings, grizzly bear, weaver patriarch, luminous horror, necrotic mass.
# Six are native_tall (uruivellas, thaurhereg, temporal stalker, blade horror, grizzly bear, necrotic mass). The alchemist's player
# golem (same name/type/subtype as `golem`, own image + moddable_tile) must stay native.
BY = ['uruivellas', 'thaurhereg', 'orc corruptor', 'temporal stalker', 'broken golem', 'golem', 'blade horror',
      'animated mummy wrappings', 'grizzly bear', 'weaver patriarch', 'luminous horror', 'necrotic mass']
NATIVE_BY = []
PLACE_SRC_BY = {'uruivellas': '/data/general/npcs/major-demon.lua', 'thaurhereg': '/data/general/npcs/major-demon.lua',
                'orc corruptor': '/data/general/npcs/orc-rak-shor.lua', 'temporal stalker': '/data/general/npcs/horror_temporal.lua',
                'broken golem': '/data/general/npcs/construct.lua', 'golem': '/data/general/npcs/construct.lua',
                'blade horror': '/data/general/npcs/horror.lua', 'animated mummy wrappings': '/data/zones/ancient-elven-ruins/npcs.lua',
                'grizzly bear': '/data/general/npcs/bear.lua', 'weaver patriarch': '/data/general/npcs/spider.lua',
                'luminous horror': '/data/general/npcs/horror.lua', 'necrotic mass': '/data/general/npcs/horror-undead.lua'}
PLACE_SRC_L.update(PLACE_SRC_BY)
EXPECT.update({n: n.replace(' ', '-') for n in BY})
EXPECT['alchemist golem'] = 'alchemist-golem'

# Batch Z (2026-09-30, HEAD effe8d9e): black mamba, bandit lord, orb weaver, elven elite warrior, ultimate telugoroth, greater teluvorta,
# runed bone giant, void horror, swarming horror, ravenous horror, rogue sapper (define_as THIEF_SAPPER, shares the assassin's native PNG),
# fire wyrm. Six are native_tall (ultimate telugoroth, greater teluvorta, runed bone giant, swarming horror, ravenous horror, fire wyrm).
# Negatives: assassin vs rogue sapper each keep their own token; a random-boss fire wyrm (real random_boss filter) stays native.
# Summons: the bandit lord's Summon talent (bandit/thief/rogue) and the fire wyrm's make_escort fire drakes.
BZ = ['black mamba', 'bandit lord', 'orb weaver', 'elven elite warrior', 'ultimate telugoroth', 'greater teluvorta', 'runed bone giant',
      'void horror', 'swarming horror', 'ravenous horror', 'rogue sapper', 'fire wyrm']
NATIVE_BZ = []
PLACE_SRC_BZ = {'black mamba': '/data/general/npcs/snake.lua', 'bandit lord': '/data/general/npcs/thieve.lua',
                'orb weaver': '/data/zones/unhallowed-morass/npcs.lua', 'elven elite warrior': '/data/general/npcs/elven-warrior.lua',
                'ultimate telugoroth': '/data/general/npcs/telugoroth.lua', 'greater teluvorta': '/data/general/npcs/telugoroth.lua',
                'runed bone giant': '/data/general/npcs/bone-giant.lua', 'void horror': '/data/general/npcs/horror_temporal.lua',
                'swarming horror': '/data/general/npcs/horror_aquatic.lua', 'ravenous horror': '/data/general/npcs/horror_aquatic.lua',
                'rogue sapper': '/data/general/npcs/thieve.lua', 'fire wyrm': '/data/general/npcs/fire-drake.lua'}
PLACE_SRC_L.update(PLACE_SRC_BZ)
EXPECT.update({n: n.replace(' ', '-') for n in BZ})

# Batch AA (2026-09-30, HEAD ba364c2f): ultimate faeros, orc berserker, dredge captain, polar bear, anaconda, ultimate teluvorta,
# necrotic abomination, bone horror, sanguine horror, barrow wight, ogre warmaster, dreadmaster. Seven are native_tall (ultimate faeros,
# ultimate teluvorta, necrotic abomination, bone horror, sanguine horror, barrow wight, ogre warmaster).
# Negative: orc elite berserker (ORC_ELITE_BERSERKER, another leaf) stays native. Summon: the Necromancer's Dread talent with
# Dreadmaster known makes a dreadmaster minion. Every evidence picture clears dialogs, lights/marks seen the area, drops birth Stealth and
# centres on its subjects (CLEAN).
CLEAN = False
BA = ['ultimate faeros', 'orc berserker', 'dredge captain', 'polar bear', 'anaconda', 'ultimate teluvorta', 'necrotic abomination',
      'bone horror', 'sanguine horror', 'barrow wight', 'ogre warmaster', 'dreadmaster']
TALL_BA = ['ultimate faeros', 'ultimate teluvorta', 'necrotic abomination', 'bone horror', 'sanguine horror', 'barrow wight', 'ogre warmaster']
NATIVE_BA = ['orc elite berserker']
PLACE_SRC_BA = {'ultimate faeros': '/data/general/npcs/faeros.lua', 'orc berserker': '/data/general/npcs/orc-grushnak.lua',
                'dredge captain': '/data/general/npcs/horror_temporal.lua', 'polar bear': '/data/general/npcs/bear.lua',
                'anaconda': '/data/general/npcs/snake.lua', 'ultimate teluvorta': '/data/general/npcs/telugoroth.lua',
                'necrotic abomination': '/data/general/npcs/horror-undead.lua', 'bone horror': '/data/general/npcs/horror-undead.lua',
                'sanguine horror': '/data/general/npcs/horror-undead.lua', 'barrow wight': '/data/general/npcs/wight.lua',
                'ogre warmaster': '/data/general/npcs/ogre.lua', 'dreadmaster': '/data/general/npcs/ghost.lua'}
PLACE_SRC_L.update(PLACE_SRC_BA)
EXPECT.update({n: n.replace(' ', '-') for n in BA})

CLEAN_VIEW = ("ms.caveClearDialogs();local m=game.level.map;local p=game.player;local grp={};"
              "for _,a in pairs(game.level.entities) do if a~=p and a.x and %s then grp[#grp+1]=a end end;"
              "local x0,y0,x1,y1=p.x,p.y,p.x,p.y;for _,a in ipairs(grp) do x0,y0,x1,y1=math.min(x0,a.x),math.min(y0,a.y),math.max(x1,a.x),math.max(y1,a.y) end;"
              "for x=x0-3,x1+3 do for y=y0-3,y1+3 do if x>=0 and y>=0 and x<m.w and y<m.h then pcall(function() m.lites(x,y,true);m.remembers(x,y,true);m.seens(x,y,true) end) end end end;"
              "for _,a in ipairs(grp) do if a.stealth then a._checker_live_was_stealth=a.stealth;a.stealth=nil;a.inc_stealth=nil end end;"
              "for _,a in ipairs(grp) do if a:isTalentActive('T_STEALTH') then pcall(function() a:forceUseTalent('T_STEALTH',{ignore_energy=true,ignore_cd=true,no_talent_fail=true,silent=true}) end) end end;"
              "pcall(function() p:resetCanSeeCache() end);for _,a in ipairs(grp) do pcall(function() a:resetCanSeeCacheOf() end) end;"
              "game.level.data.weather_particle=nil;game.level.data.weather_shader=nil;game.level.foreground_particle=nil;"  # zone weather clouds are drawn over tokens
              "m.smooth_scroll=0;m:centerViewAround(%s);m:redisplay();m.changed=true;game.paused=true;ms.caveClearDialogs();core.display.forceRedraw();"
              "local rows={};for _,a in ipairs(grp) do local r=mb.row(a);r.can_see=p:canSee(a) and true or false;r.seen=m.seens(a.x,a.y) and true or false;rows[#rows+1]=r end;"
              "local lx0=math.max(m.display_x,m.display_x+(0-m.mx)*m.tile_w);local ly0=math.max(m.display_y,m.display_y+(0-m.my)*m.tile_h);"
              "local lx1=math.min(m.display_x+m.viewport.width,m.display_x+(m.w-m.mx)*m.tile_w);local ly1=math.min(m.display_y+m.viewport.height,m.display_y+(m.h-m.my)*m.tile_h);"
              "return {box={x0,y0,x1,y1},rows=rows,hero=mb.row(p),vp={m.display_x,m.display_y,m.viewport.width,m.viewport.height},lvp={lx0,ly0,lx1-lx0,ly1-ly0}}")  # lvp: viewport cut to the level (no black beyond the map edge)


VP = None  # map viewport [x, y, w, h] in screen pixels: evidence crops never reach into the HUD panels


def clamp_box(box):
    if not (CLEAN and VP):
        return box
    return (max(box[0], VP[0]), max(box[1], VP[1]), min(box[2], VP[0] + VP[2]), min(box[3], VP[1] + VP[3]))


def _set_vp(view):
    global VP
    VP = tuple(view.get('lvp') or view['vp'])
    return view


def clean_view_actor(bridge, name):
    """Clear dialogs, light/mark-seen the area, drop Stealth and centre on the named actor (fixture only)."""
    q = json.dumps(name, ensure_ascii=False)
    return _set_vp(bridge.lua("local S=mb.byName(%s);" % q + CLEAN_VIEW % ("a==S", "S.x,S.y")))


def group_crop(view, ps, name, margin=1):
    """Crop the screenshot to the group's bounding box (one tile of margin, tall bodies included), limited to the map viewport."""
    from PIL import Image
    sc = [r['screen'] for r in view['rows']]
    tt = sc[0][2]
    im = Image.open(ps).convert('RGB')
    box = clamp_box((max(0, min(c[0] for c in sc) - margin * tt), max(0, min(c[1] for c in sc) - margin * tt),
                     min(im.width, max(c[0] for c in sc) + (1 + margin) * tt), min(im.height, max(c[1] for c in sc) + (1 + margin) * tt)))
    cp = CROPS / f'{name}-crop.png'
    CROPS.mkdir(parents=True, exist_ok=True)
    im.crop(box).save(cp)
    return cp, box


def clean_view_placed(bridge):
    """Same for the whole placed lineup, centred on the hero."""
    return _set_vp(bridge.lua(CLEAN_VIEW % ("a._checker_live_placed", "p.x,p.y")))


def ta2_reposition(bridge):
    """Move the hero to the open cell with the most free neighbours nearby, so
    native summon helpers (findFreeGrid radius 5) have room to place actors."""
    return bridge.lua(
        "local Map=require 'engine.Map';local m=game.level.map;local p=game.player;"
        "local function free(x,y) return x>=1 and y>=1 and x<m.w-1 and y<m.h-1 and not m(x,y,Map.ACTOR) "
        "and not m:checkEntity(x,y,Map.TERRAIN,'block_move',p) and not m:checkEntity(x,y,Map.TERRAIN,'change_level') end;"
        "local best,bs;for x=math.max(1,p.x-14),math.min(m.w-2,p.x+14) do for y=math.max(1,p.y-12),math.min(m.h-2,p.y+12) do "
        "if free(x,y) then local n=0;for dx=-3,3 do for dy=-3,3 do if free(x+dx,y+dy) then n=n+1 end end end "
        "if not bs or n>bs then best,bs={x,y},n end end end end;"
        "if best then p:move(best[1],best[2],true) end;mb.refresh();mb.focus(p.x,p.y);return {x=p.x,y=p.y,free=bs}")


def ta2_group_shots(bridge, label, prefix, entry, margin=2):
    """Capture a placed group at 48/64/96 (dialogs cleared, area lit/seen, Stealth dropped)."""
    entry['shots'] = []
    entry['view_rows'] = {}
    for t in (48, 64, 96):
        bridge.lua(f"mb.setTile({t});mb.focus(game.player.x,game.player.y);return mb.row(game.player)")
        view = clean_view_placed(bridge)
        entry['view_rows'][str(t)] = [[r['name'], r['identify'], r['rendered_token'], r['can_see'], r['screen']]
                                      for r in view['rows']]
        if not view['rows']:
            entry.setdefault('empty_view', []).append(t)
            continue
        ps = bridge.shot(f'{prefix}-{label}-{t}')
        cp, box = group_crop(view, ps, f'{prefix}-{label}-{t}', margin)
        entry['shots'].append({'tile': t, 'file': rel(ps), 'sha256': digest(ps), 'crop': rel(cp)})
    bridge.lua('mb.setTile(64)')


# Batch AB (2026-09-30, HEAD ac1506e3): entrenched horror, orc summoner, greater mummy, shadowblade, orc elite fighter, orc elite berserker,
# boiling horror, venom wyrm, alchemist golem, swarm hive, Forest Troll Hedge-Wizard, ultimate shivgoroth. Six are tall bodies (entrenched horror,
# boiling horror, venom wyrm, swarm hive, ultimate shivgoroth, and the unique Hedge-Wizard). Negatives: the shadowblade shares define_as
# THIEF_ASSASSIN with the assassin and each keeps its own token in one scene; the player's own alchemist golem (real T_REFIT_GOLEM) stays native;
# the arena's define_as-less shadowblade stays native. Summons: swarm hive -> swarming horror token; orc summoner's Minotaur / Ritch Flamespitter /
# Spider wild gifts (the giant spider has no token by design and stays native).
BB = ['entrenched horror', 'orc summoner', 'greater mummy', 'shadowblade', 'orc elite fighter', 'orc elite berserker', 'boiling horror',
      'venom wyrm', 'alchemist golem', 'swarm hive', 'Forest Troll Hedge-Wizard', 'ultimate shivgoroth']
TALL_BB = ['entrenched horror', 'boiling horror', 'venom wyrm', 'swarm hive', 'ultimate shivgoroth', 'Forest Troll Hedge-Wizard']
PLACE_SRC_BB = {'entrenched horror': '/data/general/npcs/horror_aquatic.lua', 'orc summoner': '/data/general/npcs/orc-gorbat.lua',
                'greater mummy': '/data/zones/ancient-elven-ruins/npcs.lua', 'shadowblade': '/data/general/npcs/thieve.lua',
                'orc elite fighter': '/data/general/npcs/orc-grushnak.lua', 'orc elite berserker': '/data/general/npcs/orc-grushnak.lua',
                'boiling horror': '/data/general/npcs/horror_aquatic.lua', 'venom wyrm': '/data/general/npcs/venom-drake.lua',
                'alchemist golem': '/data/general/npcs/construct.lua', 'swarm hive': '/data/general/npcs/horror_aquatic.lua',
                'Forest Troll Hedge-Wizard': '/data/general/npcs/troll.lua', 'ultimate shivgoroth': '/data/general/npcs/shivgoroth.lua'}
PLACE_SRC_L.update(PLACE_SRC_BB)
EXPECT.update({n: n.replace(' ', '-').lower() for n in BB})
SUMMON_EXPECT_BB = {'minotaur': 'minotaur', 'ritch flamespitter': 'ritch-flamespitter', 'giant spider': None}

HIVE_LUA = (
    "local hive=mb.byName(%s);assert(hive,'no hive');hive._checker_live_group=true;hive.never_act=true;local before={};for _,a in pairs(game.level.entities) do before[a]=true end;"
    "local FT={ignore_energy=true,ignore_cd=true,no_equilibrium_fail=true,no_talent_fail=true,silent=true};"
    "local casts,out=0,{};while casts<6 and #out<3 do casts=casts+1;local ok,err=pcall(hive.forceUseTalent,hive,'T_SUMMON',FT);assert(ok,tostring(err));"
    "for _,a in pairs(game.level.entities) do if not before[a] and a.x then before[a]=true;a._checker_live_placed=true;a._checker_live_minion=true;a.never_act=true;"
    "pcall(function() game:checkerRefreshActor(a,'display') end);out[#out+1]=a end end end;"
    "mb.refresh();local rows={};for _,a in ipairs(out) do local r=mb.row(a);r.summoner_is_hive=(a.summoner==hive);r.define_as_field=a.define_as or false;rows[#rows+1]=r end;"
    "mb.focus(hive.x,hive.y);return {casts=casts,rows=rows,hive=mb.row(hive)}")
GROUP_CENTER = "math.floor((x0+x1)/2),math.floor((y0+y1)/2)"

SCENES_M = [
    ('abashed-expanse-L1', 'abashed-expanse', 1, {}, [
        ('natural_or_place', 'losgoroth', (48, 64, 96)),
        ('natural_or_place', 'manaworm', (48, 64, 96)),
        ('native', 'Spacial Disturbance')]),
    ('temporal-rift-L1', 'temporal-rift', 1, {}, [
        ('natural_or_place', 'telugoroth', (48, 64, 96)),
        ('native', 'greater telugoroth', '/data/general/npcs/telugoroth.lua'),
        ('native', 'ultimate telugoroth', '/data/general/npcs/telugoroth.lua')]),
    ('tempest-peak-L1', 'tempest-peak', 1, {}, [
        ('natural_or_place', 'gwelgoroth', (48, 64, 96)),
        ('natural_or_place', 'greater gwelgoroth', (48, 64, 96)),
        ('toggle', 'greater gwelgoroth'), ('toggle_again', 'greater gwelgoroth'),
        ('natural_or_place', 'ultimate gwelgoroth', (48, 64, 96)),
        ('toggle', 'ultimate gwelgoroth'), ('toggle_again', 'ultimate gwelgoroth'),
        ('natural_or_place', 'xorn', (48, 64, 96)),
        ('natural_or_place', 'xaren', (48, 64, 96)),
        ('natural_or_place', 'umber hulk', (48, 64, 96))]),
    ('mark-spellblaze-L1', 'mark-spellblaze', 1, {}, [
        ('natural_or_place', 'faeros', (48, 64, 96)),
        ('natural_or_place', 'gwelgoroth', (48, 64, 96)),
        ('natural_or_place', 'greater gwelgoroth', (48, 64, 96))]),
    ('charred-scar-L1', 'charred-scar', 1, {}, [
        ('natural_or_place', 'faeros', (48, 64, 96)),
        ('natural_or_place', 'greater faeros', (48, 64, 96)),
        ('natural_or_place', 'Fyrk, Faeros High Guard', (48, 64, 96)),
        ('aura', 'Fyrk, Faeros High Guard'),
        ('toggle', 'Fyrk, Faeros High Guard'), ('toggle_again', 'Fyrk, Faeros High Guard'),
        ('aura', 'Fyrk, Faeros High Guard', '-after-toggles'),
        ('native', 'ultimate faeros', '/data/general/npcs/faeros.lua')]),
    ('daikara-L1', 'daikara', 1, {}, [
        ('natural_or_place', 'xorn', (48, 64, 96)),
        ('natural_or_place', 'xaren', (48, 64, 96)),
        ('natural_or_place', 'umber hulk', (48, 64, 96)),
        ('natural_or_place', 'faeros', (48, 64, 96))]),
    ('noxious-caldera-L1', 'noxious-caldera', 1, {}, [
        ('natural_or_place', 'faeros', (48, 64, 96)),
        ('natural_or_place', 'greater faeros', (48, 64, 96))]),
    ('rhaloren-camp-L1', 'rhaloren-camp', 1, {}, [
        ('natural_or_place', 'elven cultist', (48, 64, 96)),
        ('inspect', 'elven cultist'),
        ('gc', 'elven cultist')]),
    ('crypt-kryl-feijan-L1', 'crypt-kryl-feijan', 1, {}, [
        ('natural_or_place', 'elven cultist', (48, 64, 96)),
        ('inspect', 'elven cultist'),
        ('gc', 'elven cultist')]),
    ('town-point-zero-L1', 'town-point-zero', 1, {}, [
        ('native', 'monstrous losgoroth')]),
    ('mark-lineup-L1', 'mark-spellblaze', 1, {}, [
        ('lineup', 'batch-m',
         [('greater gwelgoroth', '/data/general/npcs/gwelgoroth.lua'), ('ultimate gwelgoroth', '/data/general/npcs/gwelgoroth.lua'),
          ('Fyrk, Faeros High Guard', '/data/zones/charred-scar/npcs.lua'),
          ('gwelgoroth', '/data/general/npcs/gwelgoroth.lua'), ('faeros', '/data/general/npcs/faeros.lua'),
          ('greater faeros', '/data/general/npcs/faeros.lua'), ('xorn', '/data/general/npcs/xorn.lua'),
          ('xaren', '/data/general/npcs/xorn.lua'), ('umber hulk', '/data/general/npcs/xorn.lua')],
         # tall tokens (two-cell bodies) on the upper row, single-cell ones below
         [(-2, 1), (0, 1), (2, 1), (-3, 3), (-2, 3), (-1, 3), (1, 3), (2, 3), (3, 3)])]),
]

SCENES_N = [
    ('dreadfell-L1', 'dreadfell', 1, {}, [
        ('natural_or_place', 'skeleton magus', (48, 64, 96)),
        ('natural_or_place', 'ghast', (48, 64, 96)),
        ('natural_or_place', 'ghoulking', (48, 64, 96)),
        ('natural_or_place', 'forest wight', (48, 64, 96)),
        ('sustain', 'forest wight'), ('fade', 'forest wight'),
        ('natural_or_place', 'grave wight', (48, 64, 96)),
        ('sustain', 'grave wight'), ('fade', 'grave wight'),
        ('natural_or_place', 'lesser vampire', (48, 64, 96)),
        ('sustain', 'lesser vampire'),
        ('natural_or_place', 'vampire', (48, 64, 96)),
        ('sustain', 'vampire'),
        ('natural_or_place', 'master vampire', (48, 64, 96)),
        ('sustain', 'master vampire'),
        ('toggle', 'master vampire'), ('toggle_again', 'master vampire'),
        ('sustain', 'master vampire', '-after-toggles'),
        ('natural_or_place', 'elder vampire', (48, 64, 96)),
        ('sustain', 'elder vampire'),
        ('natural_or_place', 'vampire lord', (48, 64, 96)),
        ('native', 'barrow wight', '/data/general/npcs/wight.lua'),
        ('native', 'emperor wight', '/data/general/npcs/wight.lua')]),
    ('dreadfell-L2', 'dreadfell', 2, {}, [
        ('natural_or_place', 'bone giant', (48, 64, 96)),
        ('toggle', 'bone giant'), ('toggle_again', 'bone giant'),
        ('natural_or_place', 'ghoulking', (48, 64, 96)),
        ('natural_or_place', 'vampire', (48, 64, 96)),
        ('native', 'eternal bone giant', '/data/general/npcs/bone-giant.lua'),
        ('native', 'heavy bone giant', '/data/general/npcs/bone-giant.lua'),
        ('natural_or_place', 'skeleton mage', (64,))]),  # already mapped by an earlier batch (skeleton-mage); recorded, not a native negative
    ('halfling-ruins-L1', 'halfling-ruins', 1, {}, [
        ('natural_or_place', 'skeleton magus', (48, 64, 96)),
        ('natural_or_place', 'ghast', (48, 64, 96)),
        ('minion', 'ghast', 'T_CALL_OF_THE_MAUSOLEUM', 'ghast'),
        ('minion', 'ghoulking', 'T_CALL_OF_THE_MAUSOLEUM', 'ghoulking'),
        ('minion', 'bone giant', 'T_ASSEMBLE', 'bone_giant'),
        ('ghoulcheck',)]),
    ('ardhungol-L1', 'ardhungol', 1, {}, [
        ('natural_or_place', 'ghast', (48, 64, 96)),
        ('natural_or_place', 'skeleton magus', (48, 64, 96)),
        ('natural_or_place', 'forest wight', (48, 64, 96))]),
    ('rak-shor-pride-L1', 'rak-shor-pride', 1, {}, [
        ('natural_or_place', 'ghast', (48, 64, 96)),
        ('natural_or_place', 'skeleton magus', (48, 64, 96)),
        ('natural_or_place', 'bone giant', (48, 64, 96)),
        ('natural_or_place', 'vampire', (48, 64, 96))]),
    ('telmur-L5', 'telmur', 5, {}, [
        ('natural_or_place', 'The Shade of Telos', (48, 64, 96)),
        ('sustain', 'The Shade of Telos'),
        ('natural_or_place', 'skeleton magus', (48, 64, 96))]),
    ('keepsake-meadow-L1', 'keepsake-meadow', 1, {}, [
        ('natural_or_place', 'shadow stalker', (48, 64, 96))]),
    ('mark-lineup-L1', 'mark-spellblaze', 1, {}, [
        ('lineup', 'batch-n',
         [('master vampire', '/data/general/npcs/vampire.lua'),
          ('forest wight', '/data/general/npcs/wight.lua'), ('shadow stalker', '/data/zones/keepsake-meadow/npcs.lua'),
          ('grave wight', '/data/general/npcs/wight.lua'), ('The Shade of Telos', '/data/zones/telmur/npcs.lua'),
          ('vampire', '/data/general/npcs/vampire.lua'), ('elder vampire', '/data/general/npcs/vampire.lua'),
          ('lesser vampire', '/data/general/npcs/vampire.lua')],
         [(0, 1), (-3, 3), (-2, 3), (-1, 3), (1, 3), (2, 3), (3, 3), (-3, 1)])]),
]

SCENES_O = [
    ('sandworm-lair-L4', 'sandworm-lair', 4, {'bigworm': False}, [
        ('natural_or_place', 'gigantic corrosive tunneler', (48, 64, 96)),
        ('natural_or_place', 'gigantic gravity worm', (48, 64, 96)),
        ('natural_or_place', 'gigantic sandworm tunneler', (64,)),
        ('natural_or_place', 'white ooze', (48, 64, 96)),
        ('natural_or_place', 'slimy ooze', (48, 64, 96)),
        ('natural_or_place', 'poison ooze', (48, 64, 96)),
        ('toggle', 'gigantic corrosive tunneler'), ('toggle_again', 'gigantic corrosive tunneler'),
        ('toggle', 'gigantic gravity worm'), ('toggle_again', 'gigantic gravity worm'),
        ('sustain', 'gigantic gravity worm'),
        ('usetalent', 'gigantic gravity worm', 'T_GRAVITY_LOCUS'),
        ('sustain', 'gigantic gravity worm', '-after-locus'),
        ('native', 'huge sandworm burrower', None),
        ('synth', 'morphic ooze', 'npc/vermin_oozes_morphic_ooze.png'),
        ('synth', 'bloated ooze', 'npc/vermin_oozes_bloated_ooze.png')]),
    ('conclave-vault-L1', 'conclave-vault', 1, {}, [
        ('natural_or_place', 'brittle clear ooze', (48, 64, 96)),
        ('natural_or_place', 'white ooze', (48, 64, 96)),
        ('natural_or_place', 'slimy ooze', (48, 64, 96)),
        ('natural_or_place', 'poison ooze', (48, 64, 96))]),
    ('briagh-lair-L1', 'briagh-lair', 1, {}, [
        ('natural_or_place', 'gigantic corrosive tunneler', (48, 64, 96)),
        ('natural_or_place', 'gigantic gravity worm', (48, 64, 96)),
        ('sustain', 'gigantic gravity worm')]),
    ('old-forest-L1', 'old-forest', 1, {}, [
        ('natural_or_place', 'cute little bunny', (48, 64, 96)),
        ('natural_or_place', 'carrion worm mass', (48, 64, 96)),
        ('wormsummon',)]),
    ('temporal-rift-L1', 'temporal-rift', 1, {}, [
        ('natural_or_place', 'dredgling', (48, 64, 96)),
        ('sustain', 'dredgling')]),
    ('deep-bellow-L1', 'deep-bellow', 1, {}, [
        ('natural_or_place', 'brecklorn', (48, 64, 96)),
        ('sustain', 'brecklorn'),
        ('toggle', 'brecklorn'), ('toggle_again', 'brecklorn'),
        ('sustain', 'brecklorn', '-after-toggles')]),
    ('valley-moon-caverns-L1', 'valley-moon-caverns', 1, {}, [
        ('natural_or_place', 'onilug', (48, 64, 96)),
        ('toggle', 'onilug'), ('toggle_again', 'onilug'),
        ('natural_or_place', 'wretchling', (48, 64, 96))]),
    ('mark-lineup-L1', 'mark-spellblaze', 1, {}, [
        ('lineup', 'batch-o',
         [('onilug', '/data/general/npcs/minor-demon.lua'), ('gigantic gravity worm', '/data/general/npcs/sandworm.lua'),
          ('brecklorn', '/data/general/npcs/horror-corrupted.lua'), ('wretchling', '/data/general/npcs/minor-demon.lua'),
          ('carrion worm mass', '/data/general/npcs/vermin.lua'), ('white ooze', '/data/general/npcs/ooze.lua'),
          ('white jelly', '/data/general/npcs/jelly.lua')],
         [(-3, 3), (3, 3), (-3, 1), (-1, 1), (1, 1), (3, 1), (0, 3)])]),
]

SCENES_P = [
    ('daikara-L2', 'daikara', 2, {}, [
        ('natural_or_place', 'snow giant', (48, 64, 96)),
        ('natural_or_place', 'snow giant thunderer', (48, 64, 96)),
        ('natural_or_place', 'snow giant boulder thrower', (48, 64, 96)),
        ('natural_or_place', 'snow giant chieftain', (48, 64, 96)),
        ('natural_or_place', 'Burb the snow giant champion', (64,)),
        ('toggle', 'snow giant'), ('toggle_again', 'snow giant'),
        ('toggle', 'snow giant thunderer'), ('toggle_again', 'snow giant thunderer'),
        ('toggle', 'snow giant boulder thrower'), ('toggle_again', 'snow giant boulder thrower'),
        ('toggle', 'snow giant chieftain'), ('toggle_again', 'snow giant chieftain'),
        ('lineup', 'batch-p-snow',
         [('snow giant', None), ('snow giant thunderer', None), ('snow giant boulder thrower', None),
          ('snow giant chieftain', None), ('Burb the snow giant champion', None)],
         [(-3, 2), (-1, 2), (1, 2), (3, 2), (0, 4)])]),
    ('maze-L1', 'maze', 1, {}, [
        ('natural_or_place', 'minotaur', (48, 64, 96)),
        ('natural_or_place', 'Minotaur of the Labyrinth', (64,)),
        ('toggle', 'minotaur'), ('toggle_again', 'minotaur'),
        ('wildsummon', False), ('wildsummon', True)]),
    ('trollmire-L1', 'trollmire', 1, {}, [
        ('natural_or_place', 'mountain troll', (48, 64, 96)),
        ('natural_or_place', 'mountain troll thunderer', (48, 64, 96)),
        ('native', 'patchwork troll', '/data/general/npcs/troll.lua'),
        ('native', 'maulotaur', '/data/general/npcs/minotaur.lua')]),
    ('conclave-vault-L1', 'conclave-vault', 1, {}, [
        ('natural_or_place', 'Healer Astelrid', (48, 64, 96)),
        ('sustain', 'Healer Astelrid'),
        ('natural_or_place', 'ogre guard', (48, 64, 96)),
        ('natural_or_place', 'ogre mauler', (48, 64, 96)),
        ('natural_or_place', 'ogre rune-spinner', (48, 64, 96)),
        ('natural_or_place', 'ogre pounder', (48, 64, 96)),
        ('toggle', 'Healer Astelrid'), ('toggle_again', 'Healer Astelrid'),
        ('sustain', 'Healer Astelrid', '-after-toggles'),
        ('toggle', 'ogre guard'), ('toggle_again', 'ogre guard'),
        ('toggle', 'ogre mauler'), ('toggle_again', 'ogre mauler'),
        ('toggle', 'ogre rune-spinner'), ('toggle_again', 'ogre rune-spinner'),
        ('toggle', 'ogre pounder'), ('toggle_again', 'ogre pounder'),
        ('native', 'ogre warmaster', '/data/general/npcs/ogre.lua'),
        ('native', 'ogre sentry', None)]),
    ('town-elvala-L1', 'town-elvala', 1, {}, [
        ('natural_or_place', 'ogre rune-spinner', (64,))]),
    ('mark-lineup-L1', 'mark-spellblaze', 1, {}, [
        ('lineup', 'batch-p',
         [('Healer Astelrid', '/data/zones/conclave-vault/npcs.lua'), ('mountain troll', '/data/general/npcs/troll.lua'),
          ('ogre mauler', '/data/general/npcs/ogre.lua'), ('snow giant', '/data/general/npcs/snow-giant.lua'),
          ('ogre pounder', '/data/general/npcs/ogre.lua'), ('mountain troll thunderer', '/data/general/npcs/troll.lua')],
         [(-3, 3), (-1, 3), (1, 3), (3, 3), (-2, 1), (2, 1)])]),
]

SCENES_Q = [
    ('daikara-cold-L4', 'daikara', 4, {'volcano': False}, [
        ('natural_or_place', 'cold drake', (48, 64, 96)),
        ('natural_or_place', 'cold drake hatchling', (48, 64, 96)),
        ('natural_or_place', 'Rantha the Worm', (64,)),
        ('toggle', 'cold drake'), ('toggle_again', 'cold drake')]),
    ('daikara-volcano-L4', 'daikara', 4, {'volcano': True}, [
        ('natural_or_place', 'fire drake', (48, 64, 96)),
        ('natural_or_place', 'fire drake hatchling', (48, 64, 96)),
        ('natural_or_place', 'Varsha the Writhing', (64,)),
        ('toggle', 'fire drake hatchling'), ('toggle_again', 'fire drake hatchling'),
        ('drakesummon', 'wyrmic'), ('drakesummon', 'grand')]),
    ('charred-scar-L1', 'charred-scar', 1, {}, [
        ('natural_or_place', 'fire drake', (64,)),
        ('native', 'fire wyrm', '/data/general/npcs/fire-drake.lua'),
        ('native', 'multi-hued drake', '/data/general/npcs/multihued-drake.lua'),
        ('native', 'multi-hued drake hatchling', '/data/general/npcs/multihued-drake.lua'),
        ('native', 'greater multi-hued wyrm', '/data/general/npcs/multihued-drake.lua')]),
    ('tempest-peak-L1', 'tempest-peak', 1, {}, [
        ('natural_or_place', 'storm drake', (48, 64, 96)),
        ('natural_or_place', 'storm drake hatchling', (48, 64, 96)),
        ('toggle', 'storm drake hatchling'), ('toggle_again', 'storm drake hatchling')]),
    ('noxious-caldera-L1', 'noxious-caldera', 1, {}, [
        ('natural_or_place', 'venom drake', (48, 64, 96)),
        ('natural_or_place', 'venom drake hatchling', (48, 64, 96)),
        ('toggle', 'venom drake'), ('toggle_again', 'venom drake')]),
    ('sandworm-lair-L1', 'sandworm-lair', 1, {}, [
        ('natural_or_place', 'sand-drake', (48, 64, 96)),
        ('natural_or_place', 'Corrupted Sand Wyrm', (64,)),
        ('toggle', 'sand-drake'), ('toggle_again', 'sand-drake')]),
    ('flooded-cave-L1', 'flooded-cave', 1, {}, [
        ('natural_or_place', 'Ukllmswwik the Wise', (48, 64, 96)),
        ('sustain', 'Ukllmswwik the Wise'),
        ('toggle', 'Ukllmswwik the Wise'), ('toggle_again', 'Ukllmswwik the Wise'),
        ('sustain', 'Ukllmswwik the Wise', '-after-toggles')]),
    ('temporal-rift-L1', 'temporal-rift', 1, {}, [
        ('natural_or_place', 'Rantha the Abomination', (48, 64, 96)),
        ('sustain', 'Rantha the Abomination'),
        ('toggle', 'Rantha the Abomination'), ('toggle_again', 'Rantha the Abomination'),
        ('sustain', 'Rantha the Abomination', '-after-toggles')]),
    ('briagh-lair-L1', 'briagh-lair', 1, {}, [
        ('natural_or_place', 'Briagh, Great Sand Wyrm', (48, 64, 96)),
        ('sustain', 'Briagh, Great Sand Wyrm'),
        ('usetalent', 'Briagh, Great Sand Wyrm', 'T_MASTER_SUMMONER'),
        ('sustain', 'Briagh, Great Sand Wyrm', '-after-master-summoner'),
        ('toggle', 'Briagh, Great Sand Wyrm'), ('toggle_again', 'Briagh, Great Sand Wyrm'),
        ('sustain', 'Briagh, Great Sand Wyrm', '-after-toggles')]),
    ('mark-lineup-L1', 'mark-spellblaze', 1, {}, [
        ('lineup', 'batch-q',
         [('Rantha the Abomination', '/data/zones/temporal-rift/npcs.lua'), ('venom drake', '/data/general/npcs/venom-drake.lua'),
          ('fire drake', '/data/general/npcs/fire-drake.lua'), ('storm drake hatchling', '/data/general/npcs/storm-drake.lua'),
          ('Ukllmswwik the Wise', '/data/zones/flooded-cave/npcs.lua'), ('cold drake', '/data/general/npcs/cold-drake.lua')],
         [(-3, 3), (-1, 3), (1, 3), (3, 3), (-2, 1), (2, 1)])]),
]

SCENES_R = [
    ('rak-shor-pride-L1', 'rak-shor-pride', 1, {}, [
        ('natural_or_place', 'orc necromancer', (48, 64, 96)),
        ('natural_or_place', "Rak'shor, Grand Necromancer of the Pride", (48, 64, 96)),
        ('sustain', 'orc necromancer'), ('sustain', "Rak'shor, Grand Necromancer of the Pride"),
        ('toggle', 'orc necromancer'), ('toggle_again', 'orc necromancer'),
        ('toggle', "Rak'shor, Grand Necromancer of the Pride"), ('toggle_again', "Rak'shor, Grand Necromancer of the Pride"),
        ('sustain', "Rak'shor, Grand Necromancer of the Pride", '-after-toggles'),
        ('urhrok', "Rak'shor, Grand Necromancer of the Pride")]),
    ('vor-armoury-L1', 'vor-armoury', 1, {}, [
        ('natural_or_place', 'Warmaster Gnarg', (48, 64, 96)),
        ('sustain', 'Warmaster Gnarg'),
        ('toggle', 'Warmaster Gnarg'), ('toggle_again', 'Warmaster Gnarg'),
        ('sustain', 'Warmaster Gnarg', '-after-toggles'),
        ('rampage', 'Warmaster Gnarg')]),
    ('reknor-L1', 'reknor', 1, {}, [
        ('natural_or_place', 'orc assassin', (48, 64, 96)),
        ('sustain', 'orc assassin'),
        ('toggle', 'orc assassin'), ('toggle_again', 'orc assassin'),
        ('stealth', 'orc assassin')]),
    ('ardhungol-L1', 'ardhungol', 1, {}, [
        ('natural_or_place', 'weaver young', (48, 64, 96)),
        ('toggle', 'weaver young'), ('toggle_again', 'weaver young')]),
    ('unhallowed-morass-L1', 'unhallowed-morass', 1, {}, [
        ('natural_or_place', 'fate spinner', (48, 64, 96)),
        ('toggle', 'fate spinner'), ('toggle_again', 'fate spinner'),
        ('natural_or_place', 'weaver hatchling', (64,)),
        ('natural_or_place', 'weaver young', (64,))]),
    ('valley-moon-caverns-L1', 'valley-moon-caverns', 1, {}, [
        ('natural_or_place', 'quasit', (48, 64, 96)),
        ('toggle', 'quasit'), ('toggle_again', 'quasit')]),
    ('old-forest-L1', 'old-forest', 1, {}, [
        ('natural_or_place', 'giant green ant', (48, 64, 96)),
        ('natural_or_place', 'giant red ant', (48, 64, 96)),
        ('toggle', 'giant green ant'), ('toggle_again', 'giant green ant'),
        ('toggle', 'giant red ant'), ('toggle_again', 'giant red ant')]),
    ('crypt-kryl-feijan-L1', 'crypt-kryl-feijan', 1, {}, [
        ('natural_or_place', 'elven warrior', (48, 64, 96)),
        ('toggle', 'elven warrior'), ('toggle_again', 'elven warrior')]),
    ('keepsake-meadow-L1', 'keepsake-meadow', 1, {}, [
        ('natural_or_place', 'corrupted war dog', (48, 64, 96)),
        ('natural_or_place', 'dire wolf', (64,)),
        ('natural_or_place', 'war dog', (64,)),
        ('toggle', 'corrupted war dog'), ('toggle_again', 'corrupted war dog')]),
    ('deep-bellow-L1', 'deep-bellow', 1, {}, [
        ('natural_or_place', "grannor'vor", (48, 64, 96)),
        ('toggle', "grannor'vor"), ('toggle_again', "grannor'vor")]),
    ('mark-lineup-L1', 'mark-spellblaze', 1, {}, [
        ('lineup', 'batch-r',
         [('orc assassin', '/data/general/npcs/orc.lua'), ('corrupted war dog', '/data/zones/keepsake-meadow/npcs.lua'),
          ("Rak'shor, Grand Necromancer of the Pride", '/data/zones/rak-shor-pride/npcs.lua'),
          ('orc necromancer', '/data/general/npcs/orc-rak-shor.lua'), ('giant red ant', '/data/general/npcs/ant.lua'),
          ('quasit', '/data/general/npcs/minor-demon.lua')],
         [(-3, 3), (-1, 3), (1, 3), (3, 3), (-2, 1), (2, 1)])]),
]

SCENES_S = [
    ('charred-scar-L1', 'charred-scar', 1, {}, [
        ('natural_or_place', 'human sun-paladin', (48, 64, 96)),
        ('natural_or_place', 'High Sun-Paladin Rodmour', (48, 64, 96)),
        ('natural_or_place', 'Argoniel', (48, 64, 96)),
        ('natural_or_place', 'Elandar', (48, 64, 96)),
        ('toggle', 'human sun-paladin'), ('toggle_again', 'human sun-paladin'),
        ('toggle', 'High Sun-Paladin Rodmour'), ('toggle_again', 'High Sun-Paladin Rodmour'),
        ('sustain', 'High Sun-Paladin Rodmour'), ('sustain', 'Argoniel'), ('sustain', 'Elandar'),
        ('toggle', 'Argoniel'), ('toggle_again', 'Argoniel'),
        ('toggle', 'Elandar'), ('toggle_again', 'Elandar')]),
    ('town-gates-of-morning-L1', 'town-gates-of-morning', 1, {}, [
        ('native', 'human sun-paladin', '/data/general/npcs/sunwall-town.lua')]),
    ('high-peak-L1', 'high-peak', 1, {}, [
        ('place', 'Argoniel', (64,)), ('place', 'Elandar', (64,))]),
    ('trollmire-L1', 'trollmire', 1, {}, [
        ('natural_or_place', 'Aluin the Fallen', (48, 64, 96)),
        ('sustain', 'Aluin the Fallen'),
        ('toggle', 'Aluin the Fallen'), ('toggle_again', 'Aluin the Fallen')]),
    ('noxious-caldera-L2', 'noxious-caldera', 2, {}, [
        ('natural_or_place', 'Mindworm', (48, 64, 96)),
        ('sustain', 'Mindworm'),
        ('toggle', 'Mindworm'), ('toggle_again', 'Mindworm'),
        ('thoughtform', 'Mindworm')]),
    ('keepsake-meadow-L1', 'keepsake-meadow', 1, {}, [
        ('natural_or_place', 'Berethh', (48, 64, 96)),
        ('natural_or_place', 'Companion Warrior', (48, 64, 96)),
        ('natural_or_place', 'Companion Archer', (48, 64, 96)),
        ('sustain', 'Berethh'), ('sustain', 'Companion Warrior'), ('sustain', 'Companion Archer'),
        ('toggle', 'Berethh'), ('toggle_again', 'Berethh'),
        ('toggle', 'Companion Warrior'), ('toggle_again', 'Companion Warrior'),
        ('toggle', 'Companion Archer'), ('toggle_again', 'Companion Archer')]),
    ('ancient-elven-ruins-L3', 'ancient-elven-ruins', 3, {}, [
        ('natural_or_place', 'Greater Mummy Lord', (48, 64, 96)),
        ('sustain', 'Greater Mummy Lord'),
        ('toggle', 'Greater Mummy Lord'), ('toggle_again', 'Greater Mummy Lord'),
        ('forcesus', 'Greater Mummy Lord', 'T_INVISIBILITY')]),
    ('ruins-kor-pul-L1', 'ruins-kor-pul', 1, {}, [
        ('natural_or_place', "Kor's Fury", (48, 64, 96)),
        ('sustain', "Kor's Fury"),
        ('toggle', "Kor's Fury"), ('toggle_again', "Kor's Fury"),
        ('urhrok', "Kor's Fury")]),
    ('dreadfell-L1', 'dreadfell', 1, {}, [
        ('natural_or_place', 'Borfast the Broken', (48, 64, 96)),
        ('sustain', 'Borfast the Broken'),
        ('toggle', 'Borfast the Broken'), ('toggle_again', 'Borfast the Broken')]),
    ('mark-lineup-L1', 'mark-spellblaze', 1, {}, [
        ('lineup', 'batch-s',
         [('Elandar', '/data/zones/charred-scar/npcs.lua'), ('Berethh', '/data/zones/keepsake-meadow/npcs.lua'),
          ('Borfast the Broken', '/data/zones/dreadfell/npcs.lua'), ('Aluin the Fallen', '/data/zones/trollmire/npcs.lua'),
          ('Companion Archer', '/data/zones/keepsake-meadow/npcs.lua'), ('Greater Mummy Lord', '/data/zones/ancient-elven-ruins/npcs.lua')],
         [(0, 1), (-3, 3), (-1, 3), (1, 3), (3, 3), (0, 5)])]),
]

# Summons batch (2026-09-29): summons and same-body variants wear the token of the monster they copy.
# Each summon is built by the talent's own code path (necroSetupSummon via Call of the Mausoleum,
# Worm Rot's spawn_carrion_worm, the wild-gift actions with getTarget stubbed to a free grid) and
# recorded with identify/explain/rendered_token. `summon` step: (kind, name, wild, (dx, dy), expected token id or None).
U = ['ghoul', 'carrion worm mass', 'fire drake hatchling', 'fire drake', 'minotaur', 'minotaur (wild summon)',
     'black jelly', 'black jelly (wild summon)', 'fire drake (wild summon)', 'giant spider', 'giant spider (wild summon)',
     "Rak'shor, Grand Necromancer of the Pride", "Kor's Fury"]
EXPECT.update({'minotaur (wild summon)': 'minotaur', 'black jelly (wild summon)': 'black-jelly',
               'fire drake (wild summon)': 'fire-drake', 'giant spider (wild summon)': 'giant-spider-wild-native'})
PLACE_SRC_L['human sun-paladin@town-gates-of-morning'] = '/data/general/npcs/sunwall-town.lua'
SUMMON_PRE = ("local Map=require 'engine.Map';local p=game.player;"
              "local before={};for _,a in pairs(game.level.entities) do before[a]=true end;"
              "local function newest(pred) local o;for _,a in pairs(game.level.entities) do if not before[a] and a.x and pred(a) then o=a end end return o end;"
              "local function flags(m) return {necrotic_minion=m.necrotic_minion or false,ghoul_minion=m.ghoul_minion or false,"
              "basic_ghoul_minion=m.basic_ghoul_minion or false,carrion_worm=m.carrion_worm or false,wild_gift_summon=m.wild_gift_summon or false,"
              "wild_gift_summon_ignore_cap=m.wild_gift_summon_ignore_cap or false,ai=m.ai or false,summoner_gain_exp=m.summoner_gain_exp or false,"
              "summon_time=m.summon_time or false,summoner=m.summoner==p} end;"
              "local function fin(m,tag) assert(m,'summon not created: '..tag);m._checker_live_placed=true;m._checker_live_minion=true;m.never_act=true;"
              "local okr,er=pcall(function() game:checkerRefreshActor(m,'display') end);"
              "mb.refresh();mb.focus(m.x,m.y);local r=mb.row(m);r.refresh_ok=okr;r.refresh_err=okr and false or tostring(er);r.tag=tag;r.summon_name=m.name;r.flags=flags(m);return r end;"
              "local function learn(tid) if not p:knowTalent(tid) then p:learnTalent(tid,true,1) end end;"
              "local function spot(dx,dy) local m=game.level.map;local bx,by,bs;for x=p.x-6,p.x+6 do for y=p.y-4,p.y+4 do "
              "if x>=0 and y>=0 and x<m.w and y<m.h and not m(x,y,Map.ACTOR) and not m:checkEntity(x,y,Map.TERRAIN,'block_move',p) and m.seens(x,y) and (x~=p.x or y~=p.y) then "
              "local d=(x-p.x-dx)^2+(y-p.y-dy)^2;if not bs or d<bs then bx,by,bs=x,y,d end end end end;return bx,by end;"
              "local FT={ignore_energy=true,ignore_cd=true,no_equilibrium_fail=true,no_talent_fail=true,silent=true};")
OSUMMON_LUA = (SUMMON_PRE +
    "local S=mb.byName(%s);assert(S,'no summoner');S._checker_live_group=true;S.never_act=true;local out={};"
    "local offs={{-2,1},{2,1},{0,3}};"
    "for i,tid in ipairs({'T_MINOTAUR','T_RITCH_FLAMESPITTER','T_SPIDER'}) do "
    "if not S:knowTalent(tid) then S:learnTalent(tid,true,3) end;local t=S:getTalentFromId(tid);"
    "local fx,fy=spot(offs[i][1],offs[i][2]);assert(fx,'no free grid');S.getTarget=function() return fx,fy,nil end;S.ai_target=S.ai_target or {};"
    "local ok,err=pcall(t.action,S,t);S.getTarget=nil;"
    "local m=newest(function(a) return a.summoner==S and not a._checker_live_minion end);"
    "if not m then out[#out+1]={talent=tid,ok=ok,err=tostring(err),made=false} else local r=fin(m,tid);r.talent=tid;r.action_ok=ok;r.made=true;"
    "r.summoner_is_orc=(m.summoner==S);r.define_as_field=m.define_as or false;out[#out+1]=r end end;"
    "return {summons=out,summoner=mb.row(S)}")

NATIVE_NO_DEFINE_AS = (
    "local Map=require 'engine.Map';local src,name=%s,%s;"
    "local had=rawget(_G,'currentZone');if not had then rawset(_G,'currentZone',setmetatable({is_invaded=true},{__index=game.zone})) end;"
    "local okl,list=pcall(function() return game.zone.npc_class:loadList(src,true) end);if not had then rawset(_G,'currentZone',nil) end;assert(okl,list);"
    "local proto,n;n=0;for _,q in pairs(list) do if type(q)=='table' and q.name==name then n=n+1;if not q.define_as then proto=q end end end;"
    "assert(proto,'no define_as-less '..name);local a=game.zone:finishEntity(game.level,'actor',proto);assert(a.name==name and not a.define_as);"
    "local p=game.player;local m=game.level.map;local nx,ny,bs;for x=p.x-6,p.x+6 do for y=p.y-4,p.y+4 do "
    "if x>=0 and y>=0 and x<m.w and y<m.h and not m(x,y,Map.ACTOR) and not m:checkEntity(x,y,Map.TERRAIN,'block_move',p) and not m:checkEntity(x,y,Map.TERRAIN,'change_level') and m.seens(x,y) then "
    "local d=(x-(p.x+2))^2+(y-(p.y-1))^2;if not bs or d<bs then nx,ny,bs=x,y,d end end end end;assert(nx,'no free cell');"
    "a._checker_live_placed=true;a.never_act=true;game.zone:addEntity(game.level,a,'actor',nx,ny);mb.refresh();local r=mb.row(a);r.same_name_protos=n;return r")
GIFT_TALENTS = {'minotaur': 'T_MINOTAUR', 'jelly': 'T_JELLY', 'firedrake': 'T_FIRE_DRAKE', 'spider': 'T_SPIDER'}


def summon_lua(kind, name, wild, dx, dy):
    if kind == 'ghoul':
        body = ("learn('T_CALL_OF_THE_MAUSOLEUM');local t=p:getTalentFromId('T_CALL_OF_THE_MAUSOLEUM');"
                f"local x,y=spot({dx},{dy});assert(x,'no free grid');"
                "p:callTalent('T_CALL_OF_THE_MAUSOLEUM','summonGhoul',{{x=x,y=y}},t.minions_list.ghoul);"
                "return fin(newest(function(a) return a.ghoul_minion=='ghoul' end),'ghoul')")
    elif kind == 'assemble':
        body = ("learn('T_CALL_OF_THE_CRYPT');local tc=p:getTalentFromId('T_CALL_OF_THE_CRYPT');local nsk=0;local nss=getfenv(tc.action).necroSetupSummon or necroSetupSummon;"
                "for _,o in ipairs({{-3,1},{-3,3},{-1,3}}) do local x,y=spot(o[1],o[2]);assert(x,'no free grid');"
                "local s=nss(p,tc.minions_list.skel_warrior,x,y,0,nil,true);s.never_act=true;nsk=nsk+1 end;"
                f"if not p:knowTalent('T_ASSEMBLE') then p:learnTalent('T_ASSEMBLE',true,{6 if name == 'heavy bone giant' else 3}) end;"
                "local tl=p:getTalentLevel('T_ASSEMBLE');local ok,err=pcall(p.forceUseTalent,p,'T_ASSEMBLE',FT);assert(ok,tostring(err));"
                "local m=newest(function(a) return a.is_bone_giant end);local r=fin(m,'assemble');"
                "r.talent_level=tl;r.skeletons_made=nsk;r.is_bone_giant=m.is_bone_giant;r.necrotic_minion=m.necrotic_minion;r.type=m.type;r.subtype=m.subtype;"
                "r.define_as_field=m.define_as or false;r.name_repr=string.format('%q',tostring(m.name));r.name_type=type(m.name);"
                "local Tk=require 'mod.class.CheckerTokens';local ent;for _,e in ipairs(Tk.catalog) do if e.name==m.name then ent=e.id end end;r.catalog_name_match=ent or false;"
                "r.level=m.level;r.uid=m.uid;return r")
    elif kind == 'alchemist_golem':
        # The real Refit Golem path (golemancy.lua invoke_golem: makeAlchemistGolem, renamed "golem (servant of <hero>)"), then the
        # same body renamed to the bare "golem" so only the image/moddable_tile guard can keep it native.
        body = ("local t=p:getTalentFromId('T_REFIT_GOLEM');p.alchemy_golem=nil;t.invoke_golem(p,t);local m=p.alchemy_golem;assert(m and m.x,'no golem');"
                "local r=fin(m,'alchemist-golem');r.is_alchemist_golem=m.is_alchemist_golem or false;r.moddable_tile=m.moddable_tile or false;"
                "r.image=m.image;r.name_real=m.name;r.type=m.type;r.subtype=m.subtype;r.summoner=(m.summoner==p);"
                "m.name='golem';pcall(function() game:checkerRefreshActor(m,'display') end);mb.refresh();mb.focus(m.x,m.y);"
                "local q=mb.row(m);r.plain=q;r.plain_name=m.name;return r")
    elif kind == 'dread':
        body = ("learn('T_DREAD');local ok,err=pcall(p.forceUseTalent,p,'T_DREAD',FT);assert(ok,tostring(err));"
                "local m=newest(function(a) return a.dread_minion end);local r=fin(m,'dread');"
                "r.dread_minion=m.dread_minion;r.necrotic_minion=m.necrotic_minion or false;r.type=m.type;r.subtype=m.subtype;"
                "r.summoner=(m.summoner==p);r.talent_level=p:getTalentLevel('T_DREAD');r.define_as_field=m.define_as or false;return r")
    elif kind == 'worm':
        body = ("p:callTalent('T_WORM_ROT','spawn_carrion_worm',p);"
                "return fin(newest(function(a) return a.carrion_worm end),'worm')")
    else:
        tid = GIFT_TALENTS[kind]
        pre = ""
        if kind == 'firedrake':
            pre = ("learn('T_MASTER_SUMMONER');learn('T_GRAND_ARRIVAL');"
                   "if not p:isTalentActive('T_MASTER_SUMMONER') then p:forceUseTalent('T_MASTER_SUMMONER',FT) end;"
                   "assert(p:isTalentActive('T_MASTER_SUMMONER'),'master summoner inactive');")
        body = (f"learn('{tid}');local t=p:getTalentFromId('{tid}');{pre}"
                f"local fx,fy=spot({dx},{dy});assert(fx,'no free grid');"
                f"p.getTarget=function() return fx,fy,nil end;p.wild_summon={100 if wild else 'nil'};"
                "local ok,err=pcall(t.action,p,t);p.wild_summon=nil;p.getTarget=nil;assert(ok,tostring(err));"
                f"local nm={json.dumps(name, ensure_ascii=False)};local m=newest(function(a) return a.name==nm end);local fb=false;if not m then fb=true;m=newest(function(a) return a.wild_gift_summon and a.name~='fire drake hatchling' end) end;local r=fin(m,'{kind}');r.name_fallback=fb;"
                "if nm=='fire drake' or nm=='fire drake (wild summon)' then r.escorts={};for _,a in pairs(game.level.entities) do "
                "if not before[a] and a.x and a.name=='fire drake hatchling' then a._checker_live_placed=true;a._checker_live_minion=true;a.never_act=true;"
                "mb.refresh();r.escorts[#r.escorts+1]=mb.row(a);r.escorts[#r.escorts].flags=flags(a) end end end;return r")
    return SUMMON_PRE + body


# Run only with MLV_LOCALE=zh_hans: the wild rename is then the translated tformat string.
SCENES_ZH = [
    ('summons-zh-hans-L1', 'trollmire', 1, {}, [
        ('summon', 'minotaur', '米诺陶 (野性召唤)', True, (-2, 1), 'minotaur'), ('toggle', '米诺陶 (野性召唤)')]),
]

SCENES_U = [
    ('summons-trollmire-L1', 'trollmire', 1, {}, [
        ('summon', 'ghoul', 'ghoul', False, (2, 1), 'ghoul'), ('toggle', 'ghoul'),
        ('summon', 'worm', 'carrion worm mass', False, (-2, 1), 'carrion-worm-mass'), ('toggle', 'carrion worm mass'),
        ('summon', 'minotaur', 'minotaur', False, (-3, 1), 'minotaur'), ('toggle', 'minotaur'),
        ('summon', 'minotaur', 'minotaur (wild summon)', True, (-3, -1), 'minotaur'), ('toggle', 'minotaur (wild summon)'),
        ('summon', 'jelly', 'black jelly (wild summon)', True, (1, 2), 'black-jelly'), ('toggle', 'black jelly (wild summon)'),
        ('summon', 'jelly', 'black jelly', False, (2, 2), 'black-jelly'),
        ('summon', 'spider', 'giant spider', False, (-1, 2), None),
        ('summon', 'spider', 'giant spider (wild summon)', True, (0, 3), None)]),
    ('summons-fire-drake-wild-L1', 'trollmire', 1, {}, [
        ('summon', 'firedrake', 'fire drake', False, (3, -1), 'fire-drake'), ('toggle', 'fire drake'),
        ('toggle', 'fire drake hatchling'),
        ('summon', 'firedrake', 'fire drake (wild summon)', True, (-3, -1), 'fire-drake'), ('toggle', 'fire drake (wild summon)')]),
    ('vault-paladin-L1', 'trollmire', 1, {}, [('vaultpaladin',)]),
    ('town-gates-of-morning-L1', 'town-gates-of-morning', 1, {}, [
        ('natural_or_place', 'human sun-paladin', (48, 64, 96)), ('paladinfields', 'human sun-paladin'),
        ('toggle', 'human sun-paladin')]),
    ('rak-shor-pride-L1', 'rak-shor-pride', 1, {}, [
        ('natural_or_place', "Rak'shor, Grand Necromancer of the Pride", (48, 64, 96)),
        ('urhrok', "Rak'shor, Grand Necromancer of the Pride"),
        ('toggle', "Rak'shor, Grand Necromancer of the Pride")]),
    ('ruins-kor-pul-L1', 'ruins-kor-pul', 1, {}, [
        ('natural_or_place', "Kor's Fury", (48, 64, 96)),
        ('urhrok', "Kor's Fury"), ('toggle', "Kor's Fury")]),
]

def _tt(n):
    return [('natural_or_place', n, (48, 64, 96)), ('toggle', n), ('toggle_again', n)]


SCENES_T = [
    ('keepsake-meadow-L1', 'keepsake-meadow', 1, {}, [
        ('natural_or_place', 'caravan merchant', (48, 64, 96)), ('natural_or_place', 'caravan guard', (48, 64, 96)),
        ('natural_or_place', 'caravan porter', (48, 64, 96)), ('natural_or_place', 'war dog', (48, 64, 96)),
        ('natural_or_place', 'corrupted war dog', (48, 64, 96)), ('natural_or_place', 'dire wolf', (48, 64, 96)),
        ('toggle', 'war dog'), ('toggle_again', 'war dog'), ('toggle', 'caravan merchant'), ('toggle_again', 'caravan merchant'),
        ('toggle', 'caravan guard'), ('toggle_again', 'caravan guard'), ('toggle', 'caravan porter'), ('toggle_again', 'caravan porter'),
        ('toggle', 'corrupted war dog'), ('toggle', 'dire wolf'),
        ('native', 'spectator', '/data/zones/ring-of-blood/npcs.lua'),
        ('native', 'shadow claw', '/data/zones/keepsake-meadow/npcs.lua')]),
    ('thieves-tunnels-L2', 'thieves-tunnels', 2, {}, _tt('Lost Merchant')),
    ('halfling-ruins-L4', 'halfling-ruins', 4, {}, _tt('Yeek Wayist')),
    ('maze-L1', 'maze', 1, {}, _tt('Nimisil')),
    ('temple-of-creation-L3', 'temple-of-creation', 3, {}, _tt('Slasul')),
    ('demon-plane-L1', 'demon-plane', 1, {}, _tt('Draebor, the Imp')),
    ('shertul-fortress-L1', 'shertul-fortress', 1, {}, [
        ('natural_or_place', 'Weirdling Beast', (48, 64, 96)), ('natural_or_place', 'Fortress Shadow', (48, 64, 96)),
        ('natural_or_place', 'Pumpkin, the little kitty', (48, 64, 96)),
        ('toggle', 'Weirdling Beast'), ('toggle_again', 'Weirdling Beast'),
        ('toggle', 'Fortress Shadow'), ('toggle_again', 'Fortress Shadow'),
        ('toggle', 'Pumpkin, the little kitty'), ('toggle_again', 'Pumpkin, the little kitty'),
        ('urhrok', 'Weirdling Beast'),
        ('forcesus', 'Weirdling Beast', 'T_INVISIBILITY')]),
    # Run only with MLV_LOCALE=zh_hans (--only shertul-fortress-zh-L1): native entity names stay English, only display strings translate.
    ('shertul-fortress-zh-L1', 'shertul-fortress', 1, {}, [
        ('natural_or_place', 'Weirdling Beast', (48, 64)), ('toggle', 'Weirdling Beast'), ('toggle_again', 'Weirdling Beast'),
        ('natural_or_place', 'Fortress Shadow', (64,)), ('natural_or_place', 'Pumpkin, the little kitty', (64,)),
        ('natural_or_place', 'Slasul', (64,))]),
    ('mark-lineup-L1', 'mark-spellblaze', 1, {}, [
        ('lineup', 'batch-t',
         [('Slasul', '/data/zones/temple-of-creation/npcs.lua'), ('caravan porter', '/data/zones/keepsake-meadow/npcs.lua'),
          ('Lost Merchant', '/data/zones/thieves-tunnels/npcs.lua'), ('war dog', '/data/zones/keepsake-meadow/npcs.lua'),
          ('Fortress Shadow', '/data/zones/shertul-fortress/npcs.lua'), ('Yeek Wayist', '/data/zones/halfling-ruins/npcs.lua')],
         [(0, 1), (-3, 3), (-1, 3), (1, 3), (3, 3), (0, 5)])]),
]

GIFT_TALENTS['ritch'] = 'T_RITCH_FLAMESPITTER'


def _bu(n):
    return [('natural_or_place', n, (48, 64, 96)), ('toggle', n), ('toggle_again', n)]


SCENES_BU = [
    ('ritch-tunnels-L3', 'ritch-tunnels', 3, {}, [
        ('natural_or_place', 'ritch flamespitter', (48, 64, 96)), ('natural_or_place', 'ritch impaler', (48, 64, 96)),
        ('natural_or_place', 'chitinous ritch', (48, 64, 96)), ('natural_or_place', 'Ritch Great Hive Mother', (48, 64, 96)),
        ('toggle', 'ritch flamespitter'), ('toggle_again', 'ritch flamespitter'),
        ('toggle', 'ritch impaler'), ('toggle_again', 'ritch impaler'),
        ('toggle', 'chitinous ritch'), ('toggle_again', 'chitinous ritch'),
        ('toggle', 'Ritch Great Hive Mother')]),
    ('temple-of-creation-L2', 'temple-of-creation', 2, {}, [
        ('natural_or_place', 'naga tide huntress', (48, 64, 96)), ('natural_or_place', 'naga psyren', (48, 64, 96)),
        ('toggle', 'naga tide huntress'), ('toggle_again', 'naga tide huntress'),
        ('toggle', 'naga psyren'), ('toggle_again', 'naga psyren')]),
    ('ancient-elven-ruins-L3', 'ancient-elven-ruins', 3, {}, _bu('ancient elven mummy')),
    ('reknor-L2', 'reknor', 2, {}, [
        ('natural_or_place', 'orc master assassin', (48, 64, 96)), ('natural_or_place', 'orc grand master assassin', (48, 64, 96)),
        ('toggle', 'orc master assassin'), ('toggle_again', 'orc master assassin'),
        ('toggle', 'orc grand master assassin'), ('toggle_again', 'orc grand master assassin'),
        ('sustain', 'orc master assassin', '-birth'), ('sustain', 'orc grand master assassin', '-birth'),
        ('stealth', 'orc master assassin'), ('stealth', 'orc grand master assassin')]),
    ('demon-plane-L1', 'demon-plane', 1, {}, _bu('fire imp')),
    ('ardhungol-L3', 'ardhungol', 3, {}, [
        ('natural_or_place', 'gaeramarth', (48, 64, 96)), ('natural_or_place', 'ninurlhing', (48, 64, 96)),
        ('toggle', 'gaeramarth'), ('toggle_again', 'gaeramarth'), ('toggle', 'ninurlhing'), ('toggle_again', 'ninurlhing'),
        ('sustain', 'gaeramarth', '-birth'), ('sustain', 'ninurlhing', '-birth'), ('stealth', 'gaeramarth'),
        ('native', 'hairy spider', '/data/zones/tutorial-combat-stats/npcs.lua', 'TUT_SPIDER_3')]),
    ('unhallowed-morass-L3', 'unhallowed-morass', 3, {}, _bu('fate weaver')),
    ('summons-ritch-L1', 'trollmire', 1, {}, [
        ('summon', 'ritch', 'ritch flamespitter', False, (2, 1), 'ritch-flamespitter'), ('toggle', 'ritch flamespitter'),
        ('summon', 'ritch', 'ritch flamespitter (wild summon)', True, (-2, 1), 'ritch-flamespitter'),
        ('toggle', 'ritch flamespitter (wild summon)')]),
    # Run only with MLV_LOCALE=zh_hans (--only summons-ritch-zh-L1).
    ('summons-ritch-zh-L1', 'trollmire', 1, {}, [
        ('summon', 'ritch', '火焰里奇 (野性召唤)', True, (-2, 1), 'ritch-flamespitter'), ('toggle', '火焰里奇 (野性召唤)')]),
    ('mark-lineup-L1', 'mark-spellblaze', 1, {}, [
        ('midstart',),
        # 1) as born: Stealth is a birth sustain, so the three stealthed ones are invisible to the hero (honest behaviour)
        ('lineup', 'batch-u-stealthed',
         [('orc master assassin', '/data/general/npcs/orc.lua'), ('orc grand master assassin', '/data/general/npcs/orc.lua'),
          ('ritch impaler', '/data/zones/ritch-tunnels/npcs.lua'), ('fire imp', '/data/general/npcs/minor-demon.lua'),
          ('gaeramarth', '/data/general/npcs/spider.lua'), ('naga psyren', '/data/general/npcs/naga.lua')],
         [(-4, -2), (0, -3), (4, -2), (-4, 2), (0, 3), (4, 2)]),
        # 2) Stealth dropped so all six are readable
        ('lineup', 'batch-u',
         [('orc master assassin', '/data/general/npcs/orc.lua'), ('orc grand master assassin', '/data/general/npcs/orc.lua'),
          ('ritch impaler', '/data/zones/ritch-tunnels/npcs.lua'), ('fire imp', '/data/general/npcs/minor-demon.lua'),
          ('gaeramarth', '/data/general/npcs/spider.lua'), ('naga psyren', '/data/general/npcs/naga.lua')],
         [(-4, -2), (0, -3), (4, -2), (-4, 2), (0, 3), (4, 2)], 'reveal')]),
]

LINEUP_BV = [(n, PLACE_SRC_BV[n]) for n in BV]
LINEUP_BV_POS = [(-8, -4), (-3, -4), (3, -4), (8, -4), (-8, 0), (-3, 0), (3, 0), (8, 0), (-8, 4), (-3, 4), (3, 4), (8, 4)]

SCENES_BV = [
    ('scintillating-caves-L2', 'scintillating-caves', 2, {}, _bu('black crystal')),
    ('ardhungol-L3', 'ardhungol', 3, {}, [
        ('natural_or_place', 'faerlhing', (48, 64, 96)), ('natural_or_place', 'losselhing', (48, 64, 96)),
        ('toggle', 'faerlhing'), ('toggle_again', 'faerlhing'), ('toggle', 'losselhing'), ('toggle_again', 'losselhing')]),
    ('temporal-rift-L1', 'temporal-rift', 1, {}, _bu('dredge')),
    ('demon-plane-L1', 'demon-plane', 1, {}, _bu('dolleg')),
    ('vor-armoury-L1', 'vor-armoury', 1, {}, [
        ('natural_or_place', 'eternal bone giant', (48, 64, 96)), ('natural_or_place', 'orc pyromancer', (48, 64, 96)),
        ('natural_or_place', 'orc cryomancer', (48, 64, 96)),
        ('toggle', 'eternal bone giant'), ('toggle_again', 'eternal bone giant'),
        ('toggle', 'orc pyromancer'), ('toggle_again', 'orc pyromancer'),
        ('toggle', 'orc cryomancer'), ('toggle_again', 'orc cryomancer'),
        ('stealth', 'orc pyromancer', 'teach')]),
    ('deep-bellow-L2', 'deep-bellow', 2, {}, _bu('drem master')),
    ('lake-nur-L2', 'lake-nur', 2, {}, _bu('bloated horror')),
    ('south-beach-L1', 'south-beach', 1, {}, [
        ('natural_or_place', 'yaech hunter', (48, 64, 96)), ('toggle', 'yaech hunter'), ('toggle_again', 'yaech hunter'),
        ('stealth', 'yaech hunter', 'teach')]),
    ('rak-shor-pride-L1', 'rak-shor-pride', 1, {}, _bu('orc blood mage')),
    ('assemble-L1', 'trollmire', 1, {}, [
        ('summon', 'assemble', 'eternal bone giant', False, (3, 0), 'eternal-bone-giant'), ('toggle', 'eternal bone giant'),
        ('toggle_again', 'eternal bone giant')]),
    # Run only with MLV_LOCALE=zh_hans (--only assemble-zh-L1 mark-lineup-zh-L1).
    ('assemble-zh-L1', 'trollmire', 1, {}, [
        ('summon', 'assemble', 'eternal bone giant', False, (3, 0), 'eternal-bone-giant'), ('toggle', 'eternal bone giant')]),
    ('mark-lineup-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('lineup', 'batch-v', LINEUP_BV, LINEUP_BV_POS)]),
    ('mark-lineup-zh-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('lineup', 'batch-v-zh', LINEUP_BV, LINEUP_BV_POS)]),
]

LINEUP_BW = [(n, PLACE_SRC_BW[n]) for n in BW]

SCENES_BW = [
    ('gorbat-pride-L2', 'gorbat-pride', 2, {}, [
        ('natural_or_place', 'fiery orc wyrmic', (48, 64, 96)), ('natural_or_place', 'icy orc wyrmic', (48, 64, 96)),
        ('toggle', 'fiery orc wyrmic'), ('toggle_again', 'fiery orc wyrmic'),
        ('toggle', 'icy orc wyrmic'), ('toggle_again', 'icy orc wyrmic')]),
    ('murgol-lair-L2', 'murgol-lair', 2, {}, [
        ('natural_or_place', 'yaech mindslayer', (48, 64, 96)), ('toggle', 'yaech mindslayer'), ('toggle_again', 'yaech mindslayer'),
        ('stealth', 'yaech mindslayer', 'teach')]),
    ('vor-armoury-L2', 'vor-armoury', 2, {}, [
        ('natural_or_place', 'heavy bone giant', (48, 64, 96)),
        ('toggle', 'heavy bone giant'), ('toggle_again', 'heavy bone giant')]),
    ('trollmire-L2-bears', 'trollmire', 2, {}, [
        ('natural_or_place', 'cave bear', (48, 64, 96)), ('natural_or_place', 'war bear', (48, 64, 96)),
        ('toggle', 'cave bear'), ('toggle_again', 'cave bear'), ('toggle', 'war bear'), ('toggle_again', 'war bear')]),
    ('deep-bellow-L2', 'deep-bellow', 2, {}, _bu("grannor'vin")),
    ('ancient-elven-ruins-L1', 'ancient-elven-ruins', 1, {}, _bu('rotting mummy')),
    ('telmur-L2', 'telmur', 2, {}, [
        ('natural_or_place', 'banshee', (48, 64, 96)), ('toggle', 'banshee'), ('toggle_again', 'banshee'),
        ('stealth', 'banshee', 'teach')]),
    ('old-forest-L4-ants', 'old-forest', 4, {'crystaline': False}, [
        ('natural_or_place', 'giant fire ant', (48, 64, 96)), ('natural_or_place', 'giant ice ant', (48, 64, 96)),
        ('natural_or_place', 'giant lightning ant', (48, 64, 96)),
        ('toggle', 'giant fire ant'), ('toggle_again', 'giant fire ant'), ('toggle', 'giant ice ant'), ('toggle_again', 'giant ice ant'),
        ('toggle', 'giant lightning ant'), ('toggle_again', 'giant lightning ant'), ('stealth', 'giant ice ant', 'teach')]),
    ('assemble-L1', 'trollmire', 1, {}, [
        ('summon', 'assemble', 'heavy bone giant', False, (3, 0), 'heavy-bone-giant'), ('toggle', 'heavy bone giant'),
        ('toggle_again', 'heavy bone giant'), ('lordskulls', 'Lord of Skulls (bone giant)')]),
    # Run only with MLV_LOCALE=zh_hans (--only assemble-zh-L1 mark-lineup-zh-L1).
    ('assemble-zh-L1', 'trollmire', 1, {}, [
        ('summon', 'assemble', 'heavy bone giant', False, (3, 0), 'heavy-bone-giant'), ('toggle', 'heavy bone giant')]),
    ('mark-lineup-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('lineup', 'batch-w', LINEUP_BW, LINEUP_BV_POS)]),
    ('mark-lineup-zh-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('lineup', 'batch-w-zh', LINEUP_BW, LINEUP_BV_POS)]),
]

LINEUP_BX = [(n, PLACE_SRC_BX[n]) for n in BX]

SCENES_BX = [
    ('old-forest-L4-ants', 'old-forest', 4, {'crystaline': False}, [
        ('natural_or_place', 'giant acid ant', (48, 64, 96)), ('natural_or_place', 'giant army ant', (48, 64, 96)),
        ('toggle', 'giant acid ant'), ('toggle_again', 'giant acid ant'), ('toggle', 'giant army ant'), ('toggle_again', 'giant army ant')]),
    ('murgol-lair-L2', 'murgol-lair', 2, {}, _bu('yaech psion')),
    ('dreadfell-L2', 'dreadfell', 2, {}, [
        ('natural_or_place', 'skeleton assassin', (48, 64, 96)), ('reveal', 'skeleton assassin', (48, 64, 96)), ('toggle', 'skeleton assassin'), ('toggle_again', 'skeleton assassin'),
        ('natural_or_place', 'dread', (48, 64, 96)), ('toggle', 'dread'), ('toggle_again', 'dread')]),
    ('abashed-expanse-L1', 'abashed-expanse', 1, {}, _bu('blue crystal')),
    ('crypt-kryl-feijan-L1', 'crypt-kryl-feijan', 1, {}, _bu('elven corruptor')),
    ('thieves-tunnels-L1', 'thieves-tunnels', 1, {}, [
        ('natural_or_place', 'assassin', (48, 64, 96)), ('reveal', 'assassin', (48, 64, 96)), ('toggle', 'assassin'), ('toggle_again', 'assassin'),
        ('stealth', 'assassin'), ('native', 'shadowblade', '/data/general/npcs/thieve.lua', None, 'shot')]),
    ('temporal-rift-L1', 'temporal-rift', 1, {}, [
        ('natural_or_place', 'greater telugoroth', (48, 64, 96)), ('natural_or_place', 'teluvorta', (48, 64, 96)),
        ('toggle', 'greater telugoroth'), ('toggle_again', 'greater telugoroth'), ('toggle', 'teluvorta'), ('toggle_again', 'teluvorta')]),
    ('grushnak-pride-L1', 'grushnak-pride', 1, {}, _bu('orc fighter')),
    ('lake-nur-L1', 'lake-nur', 1, {}, _bu('devourer')),
    ('dread-summon-L1', 'trollmire', 1, {}, [
        ('summon', 'dread', 'dread', False, (3, 0), 'dread'), ('toggle', 'dread'), ('toggle_again', 'dread')]),
    # Run only with MLV_LOCALE=zh_hans (--only dread-summon-zh-L1 mark-lineup-zh-L1).
    ('dread-summon-zh-L1', 'trollmire', 1, {}, [
        ('summon', 'dread', 'dread', False, (3, 0), 'dread'), ('toggle', 'dread')]),
    ('mark-lineup-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('lineup', 'batch-x', LINEUP_BX, LINEUP_BV_POS, 'reveal')]),
    ('mark-lineup-zh-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('lineup', 'batch-x-zh', LINEUP_BX, LINEUP_BV_POS, 'reveal')]),
]

LINEUP_BY = [(n, PLACE_SRC_BY[n]) for n in BY]

SCENES_BY = [
    ('rak-shor-pride-L1', 'rak-shor-pride', 1, {}, [
        ('natural_or_place', 'orc corruptor', (48, 64, 96)), ('natural_or_place', 'uruivellas', (48, 64, 96)),
        ('natural_or_place', 'thaurhereg', (48, 64, 96)),
        ('toggle', 'orc corruptor'), ('toggle_again', 'orc corruptor'), ('toggle', 'uruivellas'), ('toggle_again', 'uruivellas'),
        ('toggle', 'thaurhereg'), ('toggle_again', 'thaurhereg')]),
    ('temporal-rift-L1', 'temporal-rift', 1, {}, _bu('temporal stalker')),
    ('golem-graveyard-L1', 'golem-graveyard', 1, {}, [
        ('natural_or_place', 'broken golem', (48, 64, 96)), ('natural_or_place', 'golem', (48, 64, 96)),
        ('toggle', 'broken golem'), ('toggle_again', 'broken golem'), ('toggle', 'golem'), ('toggle_again', 'golem')]),
    ('abashed-expanse-L1', 'abashed-expanse', 1, {}, [
        ('natural_or_place', 'blade horror', (48, 64, 96)), ('natural_or_place', 'luminous horror', (48, 64, 96)),
        ('toggle', 'blade horror'), ('toggle_again', 'blade horror'), ('toggle', 'luminous horror'), ('toggle_again', 'luminous horror')]),
    ('ancient-elven-ruins-L1', 'ancient-elven-ruins', 1, {}, _bu('animated mummy wrappings')),
    ('trollmire-L2-bear', 'trollmire', 2, {}, _bu('grizzly bear')),
    ('deep-bellow-L1', 'deep-bellow', 1, {}, _bu('weaver patriarch')),
    ('dreadfell-L2', 'dreadfell', 2, {}, _bu('necrotic mass')),
    ('alchemist-golem-L1', 'trollmire', 1, {}, [('summon', 'alchemist_golem', 'alchemist golem', False, (3, 0), None)]),
    # Run only with MLV_LOCALE=zh_hans (--only mark-lineup-zh-L1).
    ('mark-lineup-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('lineup', 'batch-y', LINEUP_BY, LINEUP_BV_POS, 'reveal')]),
    ('mark-lineup-zh-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('lineup', 'batch-y-zh', LINEUP_BY, LINEUP_BV_POS, 'reveal')]),
]


LINEUP_BZ = [(n, PLACE_SRC_BZ[n]) for n in BZ]
_BZ_SUMMON = ('bandit_summon', 'bandit lord')


def _bz_thieves(zh=False):
    if zh:
        return [('natural_or_place', 'bandit lord', ()), ('reveal', 'bandit lord', (64,)), _BZ_SUMMON]
    return [
        ('natural_or_place', 'bandit lord', ()), ('reveal', 'bandit lord', (48, 64, 96)),
        ('natural_or_place', 'rogue sapper', ()), ('reveal', 'rogue sapper', (48, 64, 96)),
        ('natural_or_place', 'assassin', ()), ('reveal', 'assassin', (48, 64, 96)),
        ('toggle', 'bandit lord'), ('toggle_again', 'bandit lord'), ('toggle', 'rogue sapper'), ('toggle_again', 'rogue sapper'),
        ('toggle', 'assassin'), ('toggle_again', 'assassin'), _BZ_SUMMON]


SCENES_BZ = [
    ('old-forest-L1', 'old-forest', 1, {}, _bu('black mamba')),
    ('thieves-tunnels-L1', 'thieves-tunnels', 1, {}, _bz_thieves()),
    ('unhallowed-morass-L3', 'unhallowed-morass', 3, {}, _bu('orb weaver')),
    ('rhaloren-camp-L1', 'rhaloren-camp', 1, {}, _bu('elven elite warrior')),
    ('temporal-rift-L1', 'temporal-rift', 1, {}, [
        ('natural_or_place', 'ultimate telugoroth', (48, 64, 96)), ('natural_or_place', 'greater teluvorta', (48, 64, 96)),
        ('natural_or_place', 'void horror', (48, 64, 96)),
        ('toggle', 'ultimate telugoroth'), ('toggle_again', 'ultimate telugoroth'), ('toggle', 'greater teluvorta'), ('toggle_again', 'greater teluvorta'),
        ('toggle', 'void horror'), ('toggle_again', 'void horror')]),
    ('dreadfell-L2', 'dreadfell', 2, {}, _bu('runed bone giant')),
    ('lake-nur-L1', 'lake-nur', 1, {}, [
        ('natural_or_place', 'swarming horror', (48, 64, 96)), ('natural_or_place', 'ravenous horror', (48, 64, 96)),
        ('toggle', 'swarming horror'), ('toggle_again', 'swarming horror'), ('toggle', 'ravenous horror'), ('toggle_again', 'ravenous horror')]),
    ('daikara-L1', 'daikara', 1, {}, [
        ('natural_or_place', 'fire wyrm', (48, 64, 96)), ('toggle', 'fire wyrm'), ('toggle_again', 'fire wyrm'),
        ('midstart',), ('randboss', 'fire wyrm'), ('escort', 'fire wyrm')]),
    # Run only with MLV_LOCALE=zh_hans (--only bandit-summon-zh-L1 mark-lineup-zh-L1).
    ('bandit-summon-zh-L1', 'thieves-tunnels', 1, {}, _bz_thieves(True)),
    ('mark-lineup-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('lineup', 'batch-z', LINEUP_BZ, LINEUP_BV_POS, 'reveal')]),
    ('mark-lineup-zh-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('lineup', 'batch-z-zh', LINEUP_BZ, LINEUP_BV_POS, 'reveal')]),
]

LINEUP_BA = [(n, PLACE_SRC_BA[n]) for n in BA]
# 4x3, 11 x 8 grids incl. the tall bodies' extra row: the whole array fits the 96px map viewport (the batch-Z +-8 spread does not).
LINEUP_BA_POS = [(-5, -3), (-2, -3), (2, -3), (5, -3), (-5, 0), (-2, 0), (2, 0), (5, 0), (-5, 3), (-2, 3), (2, 3), (5, 3)]
SCENES_BA = [
    ('charred-scar-L1', 'charred-scar', 1, {}, _bu('ultimate faeros')),
    ('grushnak-pride-L1', 'grushnak-pride', 1, {}, _bu('orc berserker') + [
        ('native', 'orc elite berserker', '/data/general/npcs/orc-grushnak.lua', 'ORC_ELITE_BERSERKER', 'shot')]),
    ('temporal-rift-L1', 'temporal-rift', 1, {}, _bu('dredge captain')),
    # Temporal Rift draws translucent black squares over tokens in software GL (its own distortion/void layers, present with tokens off too),
    # which hid the placed ultimate teluvorta at 64px, so the teluvorta single draw uses a level without that layer.
    ('mark-teluvorta-L1', 'mark-spellblaze', 1, {}, _bu('ultimate teluvorta')),
    ('old-forest-L1', 'old-forest', 1, {}, _bu('polar bear') + _bu('anaconda')),
    ('blighted-ruins-L1', 'blighted-ruins', 1, {}, _bu('necrotic abomination') + _bu('bone horror') + _bu('sanguine horror')),
    ('dreadfell-L2', 'dreadfell', 2, {}, _bu('barrow wight') + _bu('dreadmaster')),
    ('crypt-kryl-feijan-L1', 'crypt-kryl-feijan', 1, {}, _bu('ogre warmaster')),
    ('dreadmaster-minion-L1', 'trollmire', 1, {}, [('dm_summon',)]),
    # Run only with MLV_LOCALE=zh_hans (--only dreadmaster-minion-zh-L1 mark-lineup-zh-L1).
    ('dreadmaster-minion-zh-L1', 'trollmire', 1, {}, [('dm_summon',)]),
    ('mark-lineup-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('lineup', 'batch-aa', LINEUP_BA, LINEUP_BA_POS, 'reveal')]),
    ('mark-lineup-zh-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('lineup', 'batch-aa-zh', LINEUP_BA, LINEUP_BA_POS, 'reveal')]),
]

# --- Temporal Rift L1 repro (2026-09-30): does something draw a translucent dark square over a token / native sprite? ---
CLEAN_VIEW_KEEP = CLEAN_VIEW.replace("game.level.data.weather_particle=nil;game.level.data.weather_shader=nil;game.level.foreground_particle=nil;", "")
assert CLEAN_VIEW_KEEP != CLEAN_VIEW  # keep the level's own weather and foreground layers: they are what is being examined
RIFT_SITE = (
    "local m=game.level.map;local Map=require 'engine.Map';local p=game.player;"
    "local function wall(x,y) local g=m(x,y,Map.TERRAIN);return g and g.define_as=='SPACETIME_RIFT' end;"
    "local function floor(x,y) local g=m(x,y,Map.TERRAIN);return g and g.define_as=='VOID' and not m(x,y,Map.ACTOR) end;"
    "local function walls(x,y) local n=0;for dx=-1,1 do for dy=-1,1 do if wall(x+dx,y+dy) then n=n+1 end end end return n end;"
    "local best,bs;for x=10,m.w-11 do for y=6,m.h-7 do if floor(x,y) and floor(x-1,y-1) and floor(x+1,y) then "
    "local sc=walls(x-1,y-1)+walls(x+1,y);if sc>=8 and (not bs or sc>bs) then best,bs={x,y},sc end end end end;"
    "assert(best,'no site');return {hx=best[1],hy=best[2],walls=bs}")
PLACE_AT = ("local Map=require 'engine.Map';local src,name,X,Y=%s,%s,%d,%d;"
            "local had=rawget(_G,'currentZone');if not had then rawset(_G,'currentZone',setmetatable({is_invaded=true},{__index=game.zone})) end;"
            "local okl,list=pcall(function() return game.zone.npc_class:loadList(src,true) end);if not had then rawset(_G,'currentZone',nil) end;assert(okl,list);"
            "local proto;for _,q in pairs(list) do if type(q)=='table' and q.name==name then proto=q break end end;assert(proto,'no proto '..name);"
            "local a=game.zone:finishEntity(game.level,'actor',proto);a._checker_live_placed=true;a.never_act=true;a.seen_by=nil;"
            "assert(not game.level.map(X,Y,Map.ACTOR),'occupied');game.zone:addEntity(game.level,a,'actor',X,Y);return mb.row(a)")
RIFT_LAYERS = ("local L=game.level;if not L._rr_fg then L._rr_fg,L._rr_wp=L.foreground_particle,L.data.weather_particle end;"
               "L.foreground_particle=(%s) and L._rr_fg or nil;L.data.weather_particle=(%s) and L._rr_wp or nil;core.display.forceRedraw();return true")
RIFT_ATTEMPTS = 8

LINEUP_BB = [(n, PLACE_SRC_BB[n]) for n in BB]
_AB_ENTER = ('natural_or_place', 'orc summoner', ())


def _bb_thieves():
    # assassin first: the placed shadowblade then lands next to the hero, who stands beside the (natural or placed) assassin.
    return [('natural_or_place', 'assassin', (48, 64, 96)), ('natural_or_place', 'shadowblade', (48, 64, 96)),
            ('toggle', 'shadowblade'), ('toggle_again', 'shadowblade'), ('toggle', 'assassin'), ('toggle_again', 'assassin'),
            ('group_view', 'shadowblade-assassin', "(a==mb.byName('shadowblade') or a==mb.byName('assassin'))", ('shadowblade', 'assassin'))]


SCENES_BB = [
    ('lake-nur-L1', 'lake-nur', 1, {}, _bu('entrenched horror') + _bu('boiling horror') + _bu('swarm hive') + [('hive_summon', 'swarm hive')]),
    ('gorbat-pride-L1', 'gorbat-pride', 1, {}, _bu('orc summoner')),
    ('orc-summoner-summons-L1', 'gorbat-pride', 1, {}, [_AB_ENTER, ('osummon', 'orc summoner')]),
    # Run only with MLV_LOCALE=zh_hans (--only orc-summoner-summons-zh-L1 mark-lineup-zh-L1).
    ('orc-summoner-summons-zh-L1', 'gorbat-pride', 1, {}, [_AB_ENTER, ('osummon', 'orc summoner')]),
    ('ancient-elven-ruins-L1', 'ancient-elven-ruins', 1, {}, _bu('greater mummy')),
    ('thieves-tunnels-L1', 'thieves-tunnels', 1, {}, _bb_thieves()),
    ('grushnak-pride-L1', 'grushnak-pride', 1, {}, _bu('orc elite fighter') + _bu('orc elite berserker')),
    ('noxious-caldera-L1', 'noxious-caldera', 1, {}, _bu('venom wyrm')),
    ('norgos-lair-L1', 'norgos-lair', 1, {}, _bu('ultimate shivgoroth')),
    ('trollmire-L1', 'trollmire', 1, {}, _bu('Forest Troll Hedge-Wizard') + [
        ('summon', 'alchemist_golem', 'alchemist golem', False, (3, 0), None)]),
    ('arena-shadowblade-L1', 'trollmire', 1, {}, [('native', 'shadowblade', '/data/zones/arena/npcs.lua', '-none-', 'shot')]),
    ('golem-graveyard-L1', 'golem-graveyard', 1, {}, _bu('alchemist golem')),
    ('rift-repro-L1', 'temporal-rift', 1, {}, [('rift_repro',)]),
    ('mark-lineup-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('lineup', 'batch-ab', LINEUP_BB, LINEUP_BA_POS, 'reveal')]),
    ('mark-lineup-zh-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('lineup', 'batch-ab-zh', LINEUP_BB, LINEUP_BA_POS, 'reveal')]),
]

# Batch AC (2026-09-30, HEAD 3fea4206, the final batch): 17 ids. Nine tall bodies: five uniques (Glacial Legion, Arch Zephyr, Rotting Titan, Heavy Sentinel,
# Void Spectre) and four native_tall (abyssal horror, umbral horror, degenerated ogric mass, ogric abomination). Negatives: the Corpathus Vilespawn (real
# CORPUS artifact summon; reuses the oozing horror PNG under its own identity) and Training Dummy stay native. Summon: the vampire lord's own T_SUMMON
# (random undead of the zone; each mapped one wears its token). Two mid-map arrays (9 tall + 8 flat) per language.
BC = ['Aletta Soultorn', 'ruin banshee', 'Filio Flightfond', 'orc high pyromancer', 'orc high cryomancer', 'Glacial Legion', 'Arch Zephyr', 'Rotting Titan',
      'Heavy Sentinel', 'Void Spectre', 'oozing horror', 'abyssal horror', 'ungolmor', 'umbral horror', 'vampire lord', 'degenerated ogric mass', 'ogric abomination']
TALL_BC = ['Glacial Legion', 'Arch Zephyr', 'Rotting Titan', 'Heavy Sentinel', 'Void Spectre', 'abyssal horror', 'umbral horror', 'degenerated ogric mass', 'ogric abomination']
FLAT_BC = [n for n in BC if n not in TALL_BC]
NATIVE_BC = ['Vilespawn', 'Training Dummy']
PLACE_SRC_BC = {'Aletta Soultorn': '/data/zones/dreadfell/npcs.lua', 'Filio Flightfond': '/data/zones/dreadfell/npcs.lua',
                'ruin banshee': '/data/general/npcs/ghost.lua', 'orc high pyromancer': '/data/general/npcs/orc-vor.lua',
                'orc high cryomancer': '/data/general/npcs/orc-vor.lua', 'Glacial Legion': '/data/zones/rak-shor-pride/npcs.lua',
                'Arch Zephyr': '/data/zones/rak-shor-pride/npcs.lua', 'Rotting Titan': '/data/zones/rak-shor-pride/npcs.lua',
                'Heavy Sentinel': '/data/zones/rak-shor-pride/npcs.lua', 'Void Spectre': '/data/zones/rak-shor-pride/npcs.lua',
                'oozing horror': '/data/general/npcs/horror.lua', 'umbral horror': '/data/general/npcs/horror.lua',
                'abyssal horror': '/data/general/npcs/horror_aquatic.lua', 'ungolmor': '/data/general/npcs/spider.lua',
                'vampire lord': '/data/general/npcs/vampire.lua', 'degenerated ogric mass': '/data/zones/conclave-vault/npcs.lua',
                'ogric abomination': '/data/zones/conclave-vault/npcs.lua', 'Training Dummy': '/data/zones/shertul-fortress/npcs.lua'}
PLACE_SRC_L.update(PLACE_SRC_BC)
EXPECT.update({n: n.replace(' ', '-').lower() for n in BC})

VILESPAWN_LUA = (SUMMON_PRE +
    "local o=game.zone:makeEntityByName(game.level,'object','CORPUS');assert(o,'no CORPUS artifact');o:resolve();"
    "local ok,err=pcall(o.summon,o,p);assert(ok,tostring(err));"
    "local m=newest(function(a) return a.name=='Vilespawn' end);local r=fin(m,'vilespawn');r.action_ok=ok;r.define_as_field=m.define_as or false;"
    "r.image_field=m.image or false;return r")
TSUMMON_LUA = (
    "local lord=mb.byName(%s);assert(lord,'no lord');lord._checker_live_group=true;lord.never_act=true;local before={};for _,a in pairs(game.level.entities) do before[a]=true end;"
    "local FT={ignore_energy=true,ignore_cd=true,no_equilibrium_fail=true,no_talent_fail=true,silent=true};"
    "local casts,out=0,{};while casts<12 and #out<5 do casts=casts+1;local ok,err=pcall(lord.forceUseTalent,lord,'T_SUMMON',FT);assert(ok,tostring(err));"
    "for _,a in pairs(game.level.entities) do if not before[a] and a.x then before[a]=true;a._checker_live_placed=true;a._checker_live_minion=true;a.never_act=true;"
    "pcall(function() game:checkerRefreshActor(a,'display') end);out[#out+1]=a end end end;"
    "mb.refresh();local rows={};for _,a in ipairs(out) do local r=mb.row(a);r.summoner_is_lord=(a.summoner==lord);r.define_as_field=a.define_as or false;rows[#rows+1]=r end;"
    "mb.focus(lord.x,lord.y);return {casts=casts,rows=rows,lord=mb.row(lord)}")

LINEUP_BC_A = [(n, PLACE_SRC_BC[n]) for n in TALL_BC]
LINEUP_BC_B = [(n, PLACE_SRC_BC[n]) for n in FLAT_BC]
LINEUP_BC_POS_A = LINEUP_BA_POS[:8] + [(0, 3)]
LINEUP_BC_POS_B = LINEUP_BA_POS[:8]
_AC_ENTER = ('natural_or_place', 'vampire lord', ())

SCENES_BC = [
    ('dreadfell-L9', 'dreadfell', 9, {}, _bu('Aletta Soultorn') + _bu('Filio Flightfond') + _bu('vampire lord')),
    ('rak-shor-pride-L3', 'rak-shor-pride', 3, {}, _bu('ruin banshee') + _bu('Glacial Legion') + _bu('Arch Zephyr') + _bu('Rotting Titan') + _bu('Heavy Sentinel') + _bu('Void Spectre')),
    ('vor-armoury-L2', 'vor-armoury', 2, {}, _bu('orc high pyromancer') + _bu('orc high cryomancer') + [
        ('native', 'Training Dummy', PLACE_SRC_BC['Training Dummy'], None, 'shot')]),
    ('lake-nur-L1', 'lake-nur', 1, {}, _bu('oozing horror') + _bu('abyssal horror') + _bu('umbral horror') + [('vilespawn',)]),
    ('ardhungol-L3', 'ardhungol', 3, {}, _bu('ungolmor')),
    ('conclave-vault-L1', 'conclave-vault', 1, {}, _bu('degenerated ogric mass') + _bu('ogric abomination')),
    ('vampire-lord-summons-L9', 'dreadfell', 9, {}, [_AC_ENTER, ('tsummon', 'vampire lord')]),
    # Run only with MLV_LOCALE=zh_hans (--only vampire-lord-summons-zh-L9 mark-lineup-a-zh-L1 mark-lineup-b-zh-L1).
    ('vampire-lord-summons-zh-L9', 'dreadfell', 9, {}, [_AC_ENTER, ('tsummon', 'vampire lord')]),
    ('mark-lineup-a-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('lineup', 'batch-ac-tall', LINEUP_BC_A, LINEUP_BC_POS_A, 'reveal')]),
    ('mark-lineup-b-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('lineup', 'batch-ac-flat', LINEUP_BC_B, LINEUP_BC_POS_B, 'reveal')]),
    ('mark-lineup-a-zh-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('lineup', 'batch-ac-tall-zh', LINEUP_BC_A, LINEUP_BC_POS_A, 'reveal')]),
    ('mark-lineup-b-zh-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('lineup', 'batch-ac-flat-zh', LINEUP_BC_B, LINEUP_BC_POS_B, 'reveal')]),
]

# Batch AD (2026-10-01, commit 935e50d2): 13 off-list dungeon-pool ids. Four tall native_tall bodies (duathedlen, daelach, snow cat, ice wyrm), nine flat.
# The pool ritch hive mother (id ritch-hive-mother-pool) and the unique Ritch Great Hive Mother draw the same native PNG and each keeps its own token.
# Checks: nicer_tiles OFF (duathedlen stays native, snow cat and ice wyrm still map), felines with Stealth active, a random-boss ice wyrm stays native.
BD = ['dúathedlen', 'daelach', 'ice wyrm', 'snow cat', 'orc grand summoner', 'orc master wyrmic', 'orc mage-hunter', 'ritch larva', 'ritch hunter',
      'ritch hive mother', 'panther', 'tiger', 'sabertooth tiger']
TALL_BD = ['dúathedlen', 'daelach', 'ice wyrm', 'snow cat']
FLAT_BD = [n for n in BD if n not in TALL_BD]
EXPECT_BD = {'dúathedlen': 'duathedlen', 'ritch hive mother': 'ritch-hive-mother-pool'}
PLACE_SRC_BD = {'dúathedlen': '/data/general/npcs/major-demon.lua', 'daelach': '/data/general/npcs/major-demon.lua',
                'ice wyrm': '/data/general/npcs/cold-drake.lua', 'snow cat': '/data/general/npcs/feline.lua',
                'orc grand summoner': '/data/general/npcs/orc-gorbat.lua', 'orc master wyrmic': '/data/general/npcs/orc-gorbat.lua',
                'orc mage-hunter': '/data/general/npcs/orc-gorbat.lua', 'ritch larva': '/data/general/npcs/ritch.lua',
                'ritch hunter': '/data/general/npcs/ritch.lua', 'ritch hive mother': '/data/general/npcs/ritch.lua',
                'panther': '/data/general/npcs/feline.lua', 'tiger': '/data/general/npcs/feline.lua', 'sabertooth tiger': '/data/general/npcs/feline.lua'}
PLACE_SRC_L.update(PLACE_SRC_BD)
EXPECT.update({n: EXPECT_BD.get(n) or n.replace(' ', '-').lower() for n in BD})
LINEUP_BD_A = [(n, PLACE_SRC_BD[n]) for n in TALL_BD]
LINEUP_BD_B = [(n, PLACE_SRC_BD[n]) for n in FLAT_BD]
LINEUP_BD_POS_A = LINEUP_BA_POS[:4]
LINEUP_BD_POS_B = LINEUP_BA_POS[:8] + [(0, 3)]
NICER_OFF_BD = [(n, PLACE_SRC_BD[n]) for n in ('dúathedlen', 'snow cat', 'ice wyrm')]

SCENES_BD = [
    ('gorbat-pride-L1', 'gorbat-pride', 1, {}, _bu('orc grand summoner') + _bu('orc master wyrmic') + _bu('orc mage-hunter')),
    ('ritch-tunnels-L3', 'ritch-tunnels', 3, {}, _bu('ritch larva') + _bu('ritch hunter') + _bu('ritch hive mother') + _bu('Ritch Great Hive Mother')),
    ('demon-plane-L1', 'demon-plane', 1, {}, _bu('dúathedlen') + _bu('daelach')),
    ('shertul-fortress-L1', 'shertul-fortress', 1, {}, _bu('panther') + _bu('tiger') + _bu('sabertooth tiger') + _bu('snow cat') + [
        ('stealth', 'panther'), ('stealth', 'tiger'), ('stealth', 'sabertooth tiger'), ('stealth', 'snow cat')]),
    ('daikara-L1', 'daikara', 1, {}, _bu('ice wyrm') + [('midstart',), ('randboss', 'ice wyrm')]),
    ('stealth-seen-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('stealth_seen', [(n, PLACE_SRC_BD[n]) for n in ('panther', 'tiger', 'sabertooth tiger', 'snow cat')])]),
    ('nicer-off-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('nicer_off', NICER_OFF_BD)]),
    ('mark-lineup-a-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('lineup', 'batch-ad-tall', LINEUP_BD_A, LINEUP_BD_POS_A, 'reveal')]),
    ('mark-lineup-b-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('lineup', 'batch-ad-flat', LINEUP_BD_B, LINEUP_BD_POS_B, 'reveal')]),
    # Run only with MLV_LOCALE=zh_hans (--only mark-lineup-a-zh-L1 mark-lineup-b-zh-L1 [other scenes]).
    ('mark-lineup-a-zh-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('lineup', 'batch-ad-tall-zh', LINEUP_BD_A, LINEUP_BD_POS_A, 'reveal')]),
    ('mark-lineup-b-zh-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('lineup', 'batch-ad-flat-zh', LINEUP_BD_B, LINEUP_BD_POS_B, 'reveal')]),
]

# Batch AE (2026-10-01, commits aa62033a + 2da92616): 12 off-list dungeon-pool ids, nine native_tall (champion of Urh'Rok, forge-giant, weaver matriarch,
# patchwork troll, maulotaur, storm wyrm, spire dragon, blinkwyrm, emperor wight), three flat (hummerhorn, worm that walks, headless horror).
# Checks: per-id 48/64/96 + toggle x2, en_US/zh_hans lineups, nicer_tiles OFF for all nine tall bodies (recorded), hummerhorn Multiply clone wears the token,
# Arena HEADLESSHORROR (same name, define_as) stays native, renamed random-boss tall bodies (Crusher / Storm Terror) stay native, Burning Wake on the
# forge-giant (native birth sustain) and force-learned on the champion keeps the token, and temporal clones (native makeParadoxClone) across the catalog.
BE = ["champion of Urh'Rok", 'forge-giant', 'hummerhorn', 'weaver matriarch', 'patchwork troll', 'maulotaur', 'worm that walks', 'headless horror',
      'storm wyrm', 'spire dragon', 'blinkwyrm', 'emperor wight']
TALL_BE = ["champion of Urh'Rok", 'forge-giant', 'weaver matriarch', 'patchwork troll', 'maulotaur', 'storm wyrm', 'spire dragon', 'blinkwyrm', 'emperor wight']
FLAT_BE = [n for n in BE if n not in TALL_BE]
EXPECT_BE = {"champion of Urh'Rok": 'champion-of-urh-rok'}
PLACE_SRC_BE = {"champion of Urh'Rok": '/data/general/npcs/major-demon.lua', 'forge-giant': '/data/general/npcs/major-demon.lua',
                'hummerhorn': '/data/general/npcs/swarm.lua', 'weaver matriarch': '/data/general/npcs/spider.lua',
                'patchwork troll': '/data/general/npcs/troll.lua', 'maulotaur': '/data/general/npcs/minotaur.lua',
                'worm that walks': '/data/general/npcs/horror.lua', 'headless horror': '/data/general/npcs/horror.lua',
                'storm wyrm': '/data/general/npcs/storm-drake.lua', 'spire dragon': '/data/general/npcs/wild-drake.lua',
                'blinkwyrm': '/data/general/npcs/wild-drake.lua', 'emperor wight': '/data/general/npcs/wight.lua',
                'Wrathroot': '/data/zones/old-forest/npcs.lua'}
PLACE_SRC_L.update(PLACE_SRC_BE)
EXPECT.update({n: EXPECT_BE.get(n) or n.replace(' ', '-').lower() for n in BE})
LINEUP_BE_A = [(n, PLACE_SRC_BE[n]) for n in TALL_BE]
LINEUP_BE_B = [(n, PLACE_SRC_BE[n]) for n in FLAT_BE]
LINEUP_BE_POS_A = LINEUP_BA_POS[:8] + [(0, 3)]
LINEUP_BE_POS_B = LINEUP_BA_POS[:3]
NICER_OFF_BE = [(n, PLACE_SRC_BE[n]) for n in TALL_BE]
# Temporal clone cases: (key, name, source, mode). 'target' places the actor then clones it; 'player' clones the hero.
PARADOX_BE = [('ae-tall-maulotaur', 'maulotaur', PLACE_SRC_BE['maulotaur'], 'target'),
              ('ae-flat-hummerhorn', 'hummerhorn', PLACE_SRC_BE['hummerhorn'], 'target'),
              ('older-orc-berserker', 'orc berserker', '/data/general/npcs/orc-grushnak.lua', 'target'),
              ('older-giant-spider', 'giant spider', '/data/general/npcs/spider.lua', 'target'),
              ('unique-wrathroot', 'Wrathroot', PLACE_SRC_BE['Wrathroot'], 'target'),
              ('player', None, None, 'player')]
EXPECT.update({'orc berserker': 'orc-berserker', 'giant spider': 'giant-spider', 'Wrathroot': 'wrathroot'})
PARADOX_DUR = 8
_AE_SRC = {'forge-giant': 'forge-giant'}

SCENES_BE = [
    ('demon-plane-L1', 'demon-plane', 1, {}, _bu("champion of Urh'Rok") + _bu('forge-giant') + [
        ('aura', 'forge-giant'), ('usetalent', "champion of Urh'Rok", 'T_BURNING_WAKE', 'learn'), ('sustain', "champion of Urh'Rok"),
        ('midstart',), ('randboss', 'forge-giant', '#rng# the Crusher')]),
    ('old-forest-L1', 'old-forest', 1, {}, _bu('hummerhorn') + [('multiply', 'hummerhorn')]),
    ('daikara-L1', 'daikara', 1, {}, _bu('spire dragon') + _bu('blinkwyrm')),
    ('gorbat-pride-L1', 'gorbat-pride', 1, {}, _bu('storm wyrm')),
    ('randboss-storm-L9', 'dreadfell', 9, {}, [('midstart',), ('randboss', 'storm wyrm', '#rng# the Storm Terror')]),
    ('ardhungol-L3', 'ardhungol', 3, {}, _bu('weaver matriarch')),
    ('trollmire-L1', 'trollmire', 1, {}, _bu('patchwork troll') + _bu('maulotaur')),
    ('lake-nur-L1', 'lake-nur', 1, {}, _bu('worm that walks') + _bu('headless horror') + [
        ('native', 'headless horror', '/data/zones/arena/npcs.lua', 'HEADLESSHORROR', 'shot')]),
    ('dreadfell-L9', 'dreadfell', 9, {}, _bu('emperor wight')),
    ('nicer-off-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('nicer_off', NICER_OFF_BE, LINEUP_BA_POS[:9])]),
    ('mark-lineup-a-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('lineup', 'batch-ae-tall', LINEUP_BE_A, LINEUP_BE_POS_A, 'reveal')]),
    ('mark-lineup-b-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('lineup', 'batch-ae-flat', LINEUP_BE_B, LINEUP_BE_POS_B, 'reveal')]),
    ('temporal-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('paradox', PARADOX_BE)]),
    # Run only with MLV_LOCALE=zh_hans (--only mark-lineup-a-zh-L1 mark-lineup-b-zh-L1 temporal-zh-L1).
    ('mark-lineup-a-zh-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('lineup', 'batch-ae-tall-zh', LINEUP_BE_A, LINEUP_BE_POS_A, 'reveal')]),
    ('mark-lineup-b-zh-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('lineup', 'batch-ae-flat-zh', LINEUP_BE_B, LINEUP_BE_POS_B, 'reveal')]),
    ('temporal-zh-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('paradox', PARADOX_BE)]),
]

# Batch AF: archived a05a8e2f + 0b2b855f, nine tokens; dreaming horror stays native.
BF = ['nightmare horror', 'radiant horror', 'maelstrom', 'parasitic horror',
      'lich', 'ancient lich', 'archlich', 'blood lich', 'animated blood']
TALL_BF = ['maelstrom', 'parasitic horror', 'lich', 'ancient lich', 'archlich', 'animated blood']
PLACE_SRC_BF = {n: '/data/general/npcs/horror.lua' for n in BF[:4]}
PLACE_SRC_BF.update({n: '/data/general/npcs/lich.lua' for n in BF[4:8]})
PLACE_SRC_BF['animated blood'] = '/data/general/npcs/horror-undead.lua'
PLACE_SRC_L.update(PLACE_SRC_BF)
EXPECT.update({n: n.replace(' ', '-') for n in BF + ['luminous horror']})
LINEUP_BF = [(n, PLACE_SRC_BF[n]) for n in BF]
def _af_steps(n):
    return [('natural_or_place', n, (48, 64, 96)), ('toggle', n, '-' + EXPECT[n]), ('toggle_again', n, '-' + EXPECT[n])]

SCENES_BF = [
    ('horrors-L1', 'mark-spellblaze', 1, {}, [('midstart',)] + sum((_af_steps(n) for n in BF[:4]), []) + [('af_effect', 'maelstrom')]),
    ('liches-L1', 'mark-spellblaze', 1, {}, [('midstart',)] + sum((_af_steps(n) for n in BF[4:8]), []) +
     [('lineup', 'af-lich-tiers', LINEUP_BF[4:8], [(-3, 1), (-1, 1), (1, 1), (3, 1)], 'reveal')]),
    ('blood-L1', 'mark-spellblaze', 1, {}, [('midstart',)] + _af_steps('animated blood') + [('blood_edge',)]),
    ('nicer-off-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('nicer_off', [(n, PLACE_SRC_BF[n]) for n in TALL_BF], LINEUP_BA_POS[:6])]),
    ('lineup-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('lineup', 'batch-af', LINEUP_BF, LINEUP_BE_POS_A, 'reveal')]),
    ('siblings-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('lineup', 'af-radiant-luminous',
     [('radiant horror', PLACE_SRC_BF['radiant horror']), ('luminous horror', '/data/general/npcs/horror.lua')], [(-1, 1), (1, 1)], 'reveal')]),
    ('dreaming-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('native', 'dreaming horror', '/data/general/npcs/horror.lua', None, 'shot'), ('af_effect', 'dreaming horror')]),
    ('maelstrom-effects-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('place', 'maelstrom', ()), ('af_effect', 'maelstrom')]),
    ('temporal-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('paradox', [('af-tall-archlich', 'archlich', PLACE_SRC_BF['archlich'], 'target')])]),
    ('blood-guard-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('blood_edge', 'measure-only')]),
    # Run the following two scenes with MLV_LOCALE=zh_hans.
    ('lineup-zh-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('lineup', 'batch-af-zh', LINEUP_BF, LINEUP_BE_POS_A, 'reveal')]),
    ('blood-zh-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('blood_edge',)]),
]

# Batch AG: composite shadow identities and native quad_hue isolation.
OUT_BG = ADDON / 'evidence/monster-batch-ag-live-20261001'
BG = ['multi-hued drake hatchling', 'multi-hued drake', 'greater multi-hued wyrm',
      'shadow claw', 'multi-hued crystal', 'shimmering crystal']
AG_CASES = [(n, '/data/general/npcs/multihued-drake.lua', 'GREATER_MULTI_HUED_WYRM' if i == 2 else None, n.replace(' ', '-')) for i,n in enumerate(BG[:3])] + [
    ('shadow claw', '/data/zones/keepsake-meadow/npcs.lua', 'SHADOW_CLAW', 'shadow-claw'),
    ('shadow claw', '/data/zones/keepsake-meadow/npcs.lua', 'SHADOW_CASTER', 'shadow-caster'),
    ('multi-hued crystal', '/data/general/npcs/crystal.lua', None, 'multi-hued-crystal'),
    ('shimmering crystal', '/data/general/npcs/crystal.lua', None, 'shimmering-crystal')]
AG_POS = [(-3,1),(-1,1),(1,1),(3,1),(-2,3),(0,3),(2,3)]
SCENES_BG = [
    ('lineup-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('ag_cycle', True)]),
    ('nicer-off-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('ag_cycle', False)]),
    ('negative-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('ag_negative',)]),
    ('temporal-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('paradox', [
        ('ag-drake', 'multi-hued drake', '/data/general/npcs/multihued-drake.lua', 'target'),
        ('ag-caster', 'shadow claw', '/data/zones/keepsake-meadow/npcs.lua', 'target:SHADOW_CASTER')])]),
    ('blood-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('blood_edge',)]),
    ('lineup-zh-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('ag_cycle', True)]),
    ('blood-zh-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('blood_edge',)]),
]

# Batch UB-1 (2026-10-01, commits c2c90eb2 + rework f4a77bae/aeecc5ea): nine
# native-tall unique/boss bodies, one shared Caldizar token bound to CALDIZAR
# and CALDIZAR_AOADS through the new define_as_alias field. Live checks: 48/64/96
# identity + two off/on cycles per locale, single-body metadata, both Aeryn
# define sites, both Caldizar define_as values, the twin/clone pair, the native
# twin_take_hit link, Tarelion's {tall=true} shorthand and native negatives.
OUT_BUB = ADDON / 'evidence/monster-batch-ub1-live-20261001'
UB1 = ['High Sun Paladin Aeryn', 'Fallen Sun Paladin Aeryn', 'Caldizar', 'Chronolith Twin',
       'Chronolith Clone', 'Temporal Defiler', 'Corrupted Daelach',
       'Linaniil, Supreme Archmage of Angolwen', 'Archmage Tarelion']
UB1_CASES = [
    ('High Sun Paladin Aeryn', '/data/zones/high-peak/npcs.lua', 'HIGH_SUN_PALADIN_AERYN', 'high-sun-paladin-aeryn'),
    ('Fallen Sun Paladin Aeryn', '/data/zones/high-peak/npcs.lua', 'FALLEN_SUN_PALADIN_AERYN', 'fallen-sun-paladin-aeryn'),
    ('Caldizar', '/data/zones/shertul-fortress-caldizar/npcs.lua', 'CALDIZAR', 'caldizar'),
    ('Chronolith Twin', '/data/zones/temporal-rift/npcs.lua', 'CHRONOLITH_TWIN', 'chronolith-twin'),
    ('Chronolith Clone', '/data/zones/temporal-rift/npcs.lua', 'CHRONOLITH_CLONE', 'chronolith-clone'),
    ('Temporal Defiler', '/data/zones/town-point-zero/npcs.lua', 'TEMPORAL_DEFILER', 'temporal-defiler'),
    ('Corrupted Daelach', '/data/zones/valley-moon/npcs.lua', 'CORRUPTED_DAELACH', 'corrupted-daelach'),
    ('Linaniil, Supreme Archmage of Angolwen', '/data/zones/town-angolwen/npcs.lua', 'SUPREME_ARCHMAGE_LINANIIL', 'supreme-archmage-linaniil'),
    ('Archmage Tarelion', '/data/zones/town-angolwen/npcs.lua', 'TARELION', 'archmage-tarelion'),
]
# The same High Aeryn body is bound at a second native define site; the shared
# Caldizar token is bound to the CALDIZAR_AOADS define_as of high-peak/npcs.lua.
UB1_GATES = ('High Sun Paladin Aeryn', '/data/zones/town-gates-of-morning/npcs.lua', 'HIGH_SUN_PALADIN_AERYN', 'high-sun-paladin-aeryn')
UB1_AOADS = ('Caldizar', '/data/zones/high-peak/npcs.lua', 'CALDIZAR_AOADS', 'caldizar')
UB1_POS = [(-3, 1), (-1, 1), (1, 1), (3, 1), (-3, 3), (-1, 3), (1, 3), (3, 3), (-1, 5)]
UB1_EXPECT = {'High Sun Paladin Aeryn': 'high-sun-paladin-aeryn',
              'Fallen Sun Paladin Aeryn': 'fallen-sun-paladin-aeryn',
              'Caldizar': 'caldizar', 'Chronolith Twin': 'chronolith-twin',
              'Chronolith Clone': 'chronolith-clone', 'Temporal Defiler': 'temporal-defiler',
              'Corrupted Daelach': 'corrupted-daelach',
              'Linaniil, Supreme Archmage of Angolwen': 'supreme-archmage-linaniil',
              'Archmage Tarelion': 'archmage-tarelion'}
EXPECT.update(UB1_EXPECT)
UB1_IMAGE = {'high-sun-paladin-aeryn': 'npc/humanoid_human_high_sun_paladin_aeryn.png',
             'fallen-sun-paladin-aeryn': 'npc/humanoid_human_fallen_sun_paladin_aeryn.png',
             'caldizar': 'npc/horror_sher_tul_caldizar.png',
             'chronolith-twin': 'npc/horror_temporal_cronolith_twin.png',
             'chronolith-clone': 'npc/horror_temporal_cronolith_clone.png',
             'temporal-defiler': 'npc/horror_temporal_temporal_defiler.png',
             'corrupted-daelach': 'npc/demon_major_corrupted_daelach.png',
             'supreme-archmage-linaniil': 'npc/humanoid_human_linaniil_supreme_archmage.png',
             'archmage-tarelion': 'npc/humanoid_shalore_archmage_tarelion.png'}

SCENES_UB1 = [
    ('lineup-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('ub1_group', 'lineup'), ('ub1_meta', UB1), ('ub1_each',)]),
    ('lineup-zh-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('ub1_group', 'lineup'), ('ub1_meta', UB1)]),
    ('sites-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('ub1_sites',)]),
    ('siblings-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('ub1_siblings',)]),
    ('twin-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('ub1_twin',)]),
    ('nicer-off-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('ub1_nicer',)]),
    ('negative-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('ub1_negative',)]),
]

# Batch UB-2 (2026-10-01, commits 98782cb2 + a1a5cee9 + Guren rework e55b5611):
# ten flat 64x64 unique/boss bodies plus the wiring-only Ben Cruthdar, the
# Cursed that reuses the ben-cruthdar-abomination token PNG. Live checks:
# en_US/zh_hans lineups of all eleven at 48/64/96 with two off/on cycles,
# natural spawns in their real zones where feasible, the Cursed and the
# temporal-rift Abomination side by side (same PNG bytes, distinct identities),
# Guren beside the shipped human sun-paladin, Epoch's native Multiply clone,
# and native appearance negatives (anonymous Limmir, wrong/no define_as).
OUT_BUB2 = ADDON / 'evidence/monster-batch-ub2-live-20261001'
UB2 = ['Sun Paladin Guren', 'Epoch', 'Corrupted Oozemancer', 'Zemekkys, Grand Keeper of Reality',
       'Blood Master', 'Limmir the Jeweler', 'Protector Myssil', "Rak'Shor Cultist",
       'Shady cornac man', 'Tannen', 'Ben Cruthdar, the Cursed']
UB2_CASES = [
    ('Sun Paladin Guren', '/data/zones/eruan/npcs.lua', 'SUN_PALADIN_GUREN', 'sun-paladin-guren'),
    ('Epoch', '/data/zones/paradox-plane/npcs.lua', 'EPOCH', 'epoch'),
    ('Corrupted Oozemancer', '/data/zones/sludgenest/npcs.lua', 'CORRUPTED_OOZEMANCER', 'corrupted-oozemancer'),
    ('Zemekkys, Grand Keeper of Reality', '/data/zones/town-point-zero/npcs.lua', 'ZEMEKKYS', 'zemekkys'),
    ('Blood Master', '/data/zones/ring-of-blood/npcs.lua', 'RING_MASTER', 'blood-master'),
    ('Limmir the Jeweler', '/data/zones/valley-moon/npcs.lua', 'LIMMIR', 'limmir-the-jeweler'),
    ('Protector Myssil', '/data/zones/town-zigur/npcs.lua', 'PROTECTOR_MYSSIL', 'protector-myssil'),
    ("Rak'Shor Cultist", '/data/zones/shadow-crypt/npcs.lua', 'CULTIST_RAK_SHOR', 'rak-shor-cultist'),
    ('Shady cornac man', '/data/zones/town-derth/npcs.lua', 'ARENA_AGENT', 'shady-cornac-man'),
    ('Tannen', '/data/zones/tannen-tower/npcs.lua', 'TANNEN', 'tannen'),
    ('Ben Cruthdar, the Cursed', '/data/zones/town-lumberjack-village/npcs.lua', 'BEN_CRUTHDAR', 'ben-cruthdar-the-cursed'),
]
UB2_ABOM = ('Ben Cruthdar, the Abomination', '/data/zones/temporal-rift/npcs.lua', 'BEN_CRUTHDAR_ABOMINATION', 'ben-cruthdar-abomination')
UB2_PALADIN = ('human sun-paladin', '/data/general/npcs/sunwall-town.lua', None, 'human-sun-paladin')
# Real zone and level per identity: the survey enters the native zone first so a
# natural spawn can be used; the zone npc list only supplies the prototype when
# the unique is not generated there (recorded as `resolved`).
UB2_ZONES = {
    'Sun Paladin Guren': ('eruan', 1), 'Epoch': ('paradox-plane', 1),
    'Corrupted Oozemancer': ('sludgenest', 1), 'Zemekkys, Grand Keeper of Reality': ('town-point-zero', 1),
    'Blood Master': ('ring-of-blood', 1), 'Limmir the Jeweler': ('valley-moon', 1),
    'Protector Myssil': ('town-zigur', 1), "Rak'Shor Cultist": ('shadow-crypt', 1),
    'Shady cornac man': ('town-derth', 1), 'Tannen': ('tannen-tower', 1),
    'Ben Cruthdar, the Cursed': ('town-lumberjack-village', 1),
}
EXPECT.update({n: tid for (n, _s, _d, tid) in UB2_CASES})
EXPECT.update({UB2_ABOM[0]: UB2_ABOM[3], UB2_PALADIN[0]: UB2_PALADIN[3]})
PLACE_SRC_L.update({n: s for (n, s, _d, _t) in UB2_CASES})
PLACE_SRC_L.update({UB2_ABOM[0]: UB2_ABOM[1], UB2_PALADIN[0]: UB2_PALADIN[1]})
# Eleven flat tokens around a mid-map hero (two rows of six/five).
UB2_POS = [(-4, -2), (-2, -2), (0, -2), (2, -2), (4, -2), (-4, 1), (-2, 1), (0, 1), (2, 1), (4, 1), (0, 4)]
UB2_IDS = {tid for (_n, _s, _d, tid) in UB2_CASES}
SCENES_UB2 = [
    ('natural-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('ub2_natural',)]),
    ('lineup-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('ub2_group', 'lineup'), ('ub2_each',)]),
    ('lineup-zh-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('ub2_group', 'lineup')]),
    ('ben-cruthdar-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('ub2_ben',)]),
    ('guren-paladin-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('ub2_guren',)]),
    ('epoch-multiply-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('ub2_epoch',)]),
    ('negative-L1', 'town-gates-of-morning', 1, {}, [('ub2_negative',)]),
]

# Batch UA: fixed archived package only; native prototypes in paused fixture scenes.
OUT_UA = ADDON / 'evidence/monster-batch-ua-live-20261001'
UA_CASES = [
    ("Kra'Tor the Gluttonous", '/data/general/npcs/orc.lua', None, 'kra-tor'),
    ("Khulmanar, General of Urh'Rok", '/data/general/npcs/major-demon.lua', None, 'khulmanar'),
    ('Rungof the Warg Titan', '/data/general/npcs/canine.lua', None, 'rungof'),
    ('Grgglck the Devouring Darkness', '/data/general/npcs/horror.lua', None, 'grgglck'),
    ('Queen Ant', '/data/general/npcs/ant.lua', None, 'queen-ant'),
    ("Ak'Gishil", '/data/general/npcs/horror.lua', None, 'ak-gishil'),
    ('Ninandra, the Great Weaver', '/data/general/npcs/spider.lua', None, 'ninandra'),
    ('Phoenix', '/data/general/npcs/bird.lua', 'NPC_PHOENIX', 'phoenix'),
    ('Ukruk the Fierce', '/data/zones/dreadfell-ambush/npcs.lua', 'UKRUK', 'ukruk'),
    ('Gorbat, Supreme Wyrmic of the Pride', '/data/zones/gorbat-pride/npcs.lua', 'GORBAT', 'gorbat'),
    ('Grushnak, Battlemaster of the Pride', '/data/zones/grushnak-pride/npcs.lua', 'GRUSHNAK', 'grushnak'),
    ('Vor, Grand Geomancer of the Pride', '/data/zones/vor-pride/npcs.lua', 'VOR', 'vor'),
]
UA_POS = [(x,y) for y in (1,3,5) for x in (-3,-1,1,3)]
UA_KIN = [('orc warrior','/data/general/npcs/orc.lua',None,'orc-warrior'),
          ('Weaver Queen','/data/zones/unhallowed-morass/npcs.lua',None,'weaver-queen'),
          ('nightmare horror','/data/general/npcs/horror.lua',None,'nightmare-horror'),
          ('abyssal horror','/data/general/npcs/horror_aquatic.lua',None,'abyssal-horror'),
          ('great wolf','/data/general/npcs/canine.lua',None,'great-wolf'),
          ('warg','/data/general/npcs/canine.lua',None,'warg')]
SCENES_UA = [
    ('lineup-L1','mark-spellblaze',1,{},[('midstart',),('ua_group','lineup')]),
    ('badge-L1','mark-spellblaze',1,{},[('midstart',),('ua_group','badge')]),
    ('kin-L1','mark-spellblaze',1,{},[('midstart',),('ua_group','kin-orc'),('ua_group','kin-weaver'),('ua_group','kin-horror'),('ua_group','kin-warg')]),
    ('prefix-L1','mark-spellblaze',1,{},[('midstart',),('ua_group','prefix')]),
    ('negative-L1','mark-spellblaze',1,{},[('midstart',),('ua_negative',)]),
    ('lineup-zh-L1','mark-spellblaze',1,{},[('midstart',),('ua_group','lineup')]),
    ('prefix-zh-L1','mark-spellblaze',1,{},[('midstart',),('ua_group','prefix')]),
]

# Batch TA-1 (2026-10-01, commits dcb5c982 + 4dad5b9e): the first town-resident
# batch, thirteen identities, four native-tall Angolwen mages. Live checks:
# 48/64/96 identity + toggle x2 per id, en_US/zh_hans lineups of all thirteen,
# the six guards on one 48px board beside elven/caravan guard, the four native
# tall bodies (one token, nicer_tiles off round trip), the slaver's native
# make_escort enthralled slaves, and appearance negatives (wrong type/subtype,
# added shader, different-name PNG reuse).
OUT_BTA = ADDON / 'evidence/monster-batch-ta1-live-20261001'
TA1 = ['apprentice mage', 'pyromancer', 'cryomancer', 'geomancer', 'tempest',
       'human guard', 'derth guard', 'last hope guard', 'halfling guard', 'dwarven guard', 'elvala guard',
       'slaver', 'enthralled slave']
TA1_MAGES = ['apprentice mage', 'pyromancer', 'cryomancer', 'geomancer', 'tempest']
TA1_TALL = ['pyromancer', 'cryomancer', 'geomancer', 'tempest']
TA1_GUARDS = ['human guard', 'derth guard', 'last hope guard', 'halfling guard', 'dwarven guard', 'elvala guard']
PLACE_SRC_TA1 = {
    'apprentice mage': '/data/zones/town-angolwen/npcs.lua', 'pyromancer': '/data/zones/town-angolwen/npcs.lua',
    'cryomancer': '/data/zones/town-angolwen/npcs.lua', 'geomancer': '/data/zones/town-angolwen/npcs.lua',
    'tempest': '/data/zones/town-angolwen/npcs.lua',
    'human guard': '/data/general/npcs/sunwall-town.lua', 'derth guard': '/data/zones/town-derth/npcs.lua',
    'last hope guard': '/data/zones/town-last-hope/npcs.lua', 'halfling guard': '/data/zones/town-last-hope/npcs.lua',
    'dwarven guard': '/data/zones/town-iron-council/npcs.lua', 'elvala guard': '/data/zones/town-elvala/npcs.lua',
    'slaver': '/data/zones/ring-of-blood/npcs.lua', 'enthralled slave': '/data/zones/ring-of-blood/npcs.lua',
}
PLACE_SRC_L.update(PLACE_SRC_TA1)
EXPECT.update({n: n.replace(' ', '-') for n in TA1})
TA1_LINEUP = [(n, PLACE_SRC_TA1[n]) for n in TA1]
TA1_POS = [(-4, -3), (-2, -3), (0, -3), (2, -3), (4, -3), (-4, 0), (-2, 0), (0, 0), (2, 0), (4, 0), (-4, 3), (-2, 3), (0, 3)]
TA1_MAGE_POS = [(-4, 0), (-2, 0), (0, 0), (2, 0), (4, 0)]
TA1_GUARD_POS = [(-5, 0), (-3, 0), (-1, 0), (1, 0), (3, 0), (5, 0)]
TA1_SIBLINGS = [('human guard', PLACE_SRC_TA1['human guard']),
                ('elven guard', '/data/general/npcs/elven-warrior.lua'),
                ('caravan guard', '/data/zones/keepsake-meadow/npcs.lua')]
TA1_NEG_CASES = [
    ('wrong-type', 'apprentice mage', PLACE_SRC_TA1['apprentice mage'], "a.type='vermin'"),
    ('wrong-subtype', 'human guard', PLACE_SRC_TA1['human guard'], "a.subtype='orc'"),
    ('added-shader', 'derth guard', PLACE_SRC_TA1['derth guard'], "a.shader='shadow_simulacrum'"),
]
# data/general/encounters/maj-eyal.lua creates a WorldNPC named "Novice mage"
# with the apprentice-mage PNG (type humanoid/human); a faithful synthetic copy
# of that body must stay native (different name, reused PNG).
TA1_NOVICE_LUA = (
    "local Map=require 'engine.Map';local p=game.player;"
    "local q=require('mod.class.NPC').new({name='Novice mage',type='humanoid',subtype='human',image='npc/humanoid_human_apprentice_mage.png',display='@',faction='angolwen',max_life=80,life=80});"
    "q:resolve();q:resolve(nil,true);local x,y=util.findFreeGrid(p.x+2,p.y+1,6,true,{[Map.ACTOR]=true});assert(x,'no free grid');"
    "q._checker_live_placed=true;q.never_act=true;game.zone:addEntity(game.level,q,'actor',x,y);_G.TA1N=q;mb.refresh();mb.focus(x,y);"
    "local r=mb.row(q);r.synthetic=true;return r")


def _ta(n, tiles=(48, 64, 96)):
    sfx = '-' + n.replace(' ', '-')
    return [('natural_or_place', n, tiles), ('toggle', n, sfx), ('toggle_again', n, sfx)]


SCENES_TA1 = [
    ('angolwen-L1', 'town-angolwen', 1, {}, sum((_ta(n) for n in TA1_MAGES), []) + [
        ('ta1_meta', TA1_TALL),
        ('lineup', 'ta1-mages', [(n, PLACE_SRC_TA1[n]) for n in TA1_MAGES], TA1_MAGE_POS)]),
    ('gates-of-morning-L1', 'town-gates-of-morning', 1, {}, _ta('human guard')),
    ('derth-L1', 'town-derth', 1, {}, _ta('derth guard')),
    ('last-hope-L1', 'town-last-hope', 1, {}, _ta('last hope guard') + _ta('halfling guard')),
    ('iron-council-L1', 'town-iron-council', 1, {}, _ta('dwarven guard')),
    ('elvala-L1', 'town-elvala', 1, {}, _ta('elvala guard')),
    ('ring-of-blood-L1', 'ring-of-blood', 1, {}, _ta('slaver') + _ta('enthralled slave') + [('ta1_escort', 'slaver')]),
    ('mark-lineup-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('lineup', 'ta1-all', TA1_LINEUP, TA1_POS)]),
    ('mark-guards-L1', 'mark-spellblaze', 1, {}, [
        ('midstart',),
        ('lineup', 'ta1-guards', [(n, PLACE_SRC_TA1[n]) for n in TA1_GUARDS], TA1_GUARD_POS),
        ('lineup', 'ta1-guard-siblings', TA1_SIBLINGS, [(-2, 0), (0, 0), (2, 0)])]),
    ('mark-nicer-off-L1', 'mark-spellblaze', 1, {}, [
        ('midstart',), ('nicer_off', [(n, PLACE_SRC_TA1[n]) for n in TA1_TALL], [(-4, 0), (-1, 0), (1, 0), (4, 0)])]),
    ('mark-negative-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('ta1_negative',)]),
    # Run only with MLV_LOCALE=zh_hans (--only mark-lineup-zh-L1).
    ('mark-lineup-zh-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('lineup', 'ta1-all-zh', TA1_LINEUP, TA1_POS)]),
]

# Batch TA-2 (2026-10-01, commit 4280b90f): the second town/wilds-resident
# batch, thirteen new non-unique bodies (two native-tall) plus the wiring-only
# elven archer that reuses the byte-identical companion-archer token PNG. Live
# checks: 48/64/96 identity + toggle x2 per id across their real towns, en_US
# and zh_hans fourteen lineups, the two native-tall bodies drawn once, the
# nicer_tiles off/on round trip, the Derth slinger positive beside the native
# Arena SLINGER, the lumberjack's native `defined_as` typo (no runtime
# define_as), the anomaly farmer/gardener summons that map while `shalore
# scribe` stays native, the Wayist yeek-mindslayer summon (tall), the elven
# archer beside the companion archer, the earthwarden/sun-mage aura sustains
# and the different-name / wrong-body negatives.
OUT_BTA2 = ADDON / 'evidence/monster-batch-ta2-live-20261001'
TA2 = ['human citizen', 'halfling citizen', 'human farmer', 'halfling gardener', 'lumberjack',
       'halfling slinger', 'dwarven earthwarden', 'yeek mindslayer', 'yeek psionic',
       'thalore hunter', 'thalore wilder', 'elven sun-mage', 'shalore rune master', 'elven archer']
TA2_TALL = ['yeek mindslayer', 'thalore wilder']
PLACE_SRC_TA2 = {
    'human citizen': '/data/zones/town-last-hope/npcs.lua',
    'halfling citizen': '/data/zones/town-last-hope/npcs.lua',
    'human farmer': '/data/zones/town-derth/npcs.lua',
    'halfling gardener': '/data/zones/town-derth/npcs.lua',
    'halfling slinger': '/data/zones/town-derth/npcs.lua',
    'lumberjack': '/data/zones/town-lumberjack-village/npcs.lua',
    'dwarven earthwarden': '/data/zones/town-iron-council/npcs.lua',
    'yeek mindslayer': '/data/zones/town-irkkk/npcs.lua',
    'yeek psionic': '/data/zones/town-irkkk/npcs.lua',
    'thalore hunter': '/data/zones/town-shatur/npcs.lua',
    'thalore wilder': '/data/zones/town-shatur/npcs.lua',
    'elven sun-mage': '/data/general/npcs/sunwall-town.lua',
    'shalore rune master': '/data/zones/town-elvala/npcs.lua',
    'elven archer': '/data/general/npcs/sunwall-town.lua',
}
PLACE_SRC_L.update(PLACE_SRC_TA2)
EXPECT.update({n: n.replace(' ', '-') for n in TA2})
TA2_LINEUP = [(n, PLACE_SRC_TA2[n]) for n in TA2]
# Four rows (5/5/4); the two native-tall bodies still fit at 96px.
TA2_POS = [(-4, -3), (-2, -3), (0, -3), (2, -3), (4, -3),
           (-4, 0), (-2, 0), (0, 0), (2, 0), (4, 0),
           (-4, 3), (-2, 3), (0, 3), (2, 3)]
# Different-name PNG reuses and same-name wrong bodies stay native.
TA2_NEG_CASES = [
    ('different-name-gem-crafter', 'gem crafter', '/data/zones/town-irkkk/npcs.lua', 'YEEK_STORE_GEM', None),
    ('different-name-2hands', 'two hander weapons crafter', '/data/zones/town-irkkk/npcs.lua', 'YEEK_STORE_2HANDS', None),
    ('wrong-subtype', 'yeek psionic', '/data/zones/town-irkkk/npcs.lua', None, "a.subtype='human'"),
    ('wrong-type', 'thalore hunter', '/data/zones/town-shatur/npcs.lua', None, "a.type='animal'"),
]
# data/general/encounters/maj-eyal.lua creates a WorldNPC "Novice mage" with
# the apprentice-mage PNG; a faithful synthetic copy of that body must stay
# native (different name, reused PNG).
TA2_NOVICE_LUA = (
    "local Map=require 'engine.Map';local p=game.player;"
    "local q=require('mod.class.NPC').new({name='Novice mage',type='humanoid',subtype='human',image='npc/humanoid_human_apprentice_mage.png',display='@',faction='angolwen',max_life=80,life=80});"
    "q:resolve();q:resolve(nil,true);local x,y=util.findFreeGrid(p.x+2,p.y+1,6,true,{[Map.ACTOR]=true});assert(x,'no free grid');"
    "q._checker_live_placed=true;q.never_act=true;game.zone:addEntity(game.level,q,'actor',x,y);_G.TA2N=q;mb.refresh();mb.focus(x,y);"
    "local r=mb.row(q);r.synthetic=true;return r")

# Real Wayist (talents/misc/races.lua:961) talent action called with a fixed
# target: the created same-name/native-tall yeek mindslayer must wear the token.
TA2_WAYIST_LUA = (
    "local Map=require 'engine.Map';local p=game.player;"
    "local t=p:getTalentFromId('T_WAYIST') or require('engine.interface.ActorTalents').talents_def['T_WAYIST'];"
    "if not t then return {ok=false,err='no talent',rows={}} end;"
    "if not p:knowTalent('T_WAYIST') then p:learnTalent('T_WAYIST',true,1) end;"
    "local before={};for _,a in pairs(game.level.entities) do before[a]=true end;"
    "local og,oc=p.getTarget,p.canProject;"
    "p.getTarget=function(self,tg) return p.x,p.y end;"
    "p.canProject=function(self,tg,x,y) return true,x,y,x,y end;"
    "local ok,err=pcall(t.action,p,t);"
    "p.getTarget,p.canProject=og,oc;"
    "local allnew={};for _,a in pairs(game.level.entities) do if not before[a] and a.x then allnew[#allnew+1]=a.name end end;"
    "local ffg={util.findFreeGrid(p.x,p.y,5,true,{[Map.ACTOR]=true})};"
    "local out={};for _,a in pairs(game.level.entities) do if not before[a] and a.x and a.name=='yeek mindslayer' then "
    "a._checker_live_placed=true;a._checker_live_minion=true;a.never_act=true;pcall(function() game:checkerRefreshActor(a,'display') end);out[#out+1]=a end end;"
    "mb.refresh();local rows={};for _,a in ipairs(out) do local r=mb.row(a);r.summoner_is_player=(a.summoner==p);"
    "r.summon_time=a.summon_time or false;r.tall_body=(a.image=='invis.png');rows[#rows+1]=r end;"
    "return {ok=ok,err=tostring(err),rows=rows,allnew=allnew}")

# Real Anomaly Summon Townsfolk (talents/chronomancy/anomalies.lua:519)
# doAction called repeatedly until the farmer, gardener and scribe variants have
# all appeared. Farmer/gardener match the catalog exact-identity path; the
# different-name shalore scribe (rune-master PNG) and dwarven lumberjack stay native.
TA2_ANOMALY_LUA = (
    "local Map=require 'engine.Map';local p=game.player;"
    "local t=p:getTalentFromId('T_ANOMALY_SUMMON_TOWNSFOLK') or require('engine.interface.ActorTalents').talents_def['T_ANOMALY_SUMMON_TOWNSFOLK'];"
    "if not t then return {ok=false,err='no talent',rows={}} end;"
    "if not p:knowTalent('T_ANOMALY_SUMMON_TOWNSFOLK') then p:learnTalent('T_ANOMALY_SUMMON_TOWNSFOLK',true,1) end;"
    "local before={};for _,a in pairs(game.level.entities) do before[a]=true end;"
    "local og,oc=p.getTarget,p.canProject;"
    "p.getTarget=function(self,tg) return p.x,p.y end;"
    "p.canProject=function(self,tg,x,y) return true,x,y,x,y end;"
    "local fn=t.doAction or t.action;local made={};local seen={};local calls=0;local removed=0;"
    "for i=1,40 do calls=i;"
    "  local ok,err=pcall(fn,p,t,true);"
    "  if not ok then p.getTarget,p.canProject=og,oc;return {ok=false,err=tostring(err),rows={}} end;"
    "  local new={};for _,a in pairs(game.level.entities) do if not before[a] and a.x then before[a]=true;new[#new+1]=a end end;"
    "  for _,a in ipairs(new) do"
    "    if seen[a.name] then removed=removed+1;pcall(function() game.level.map:remove(a.x,a.y,Map.ACTOR);game.level:removeEntity(a,true) end)"
    "    else seen[a.name]=true;a._checker_live_placed=true;a._checker_live_group=true;a.never_act=true;pcall(function() game:checkerRefreshActor(a,'display') end);made[#made+1]=a end"
    "  end;"
    "  if seen['human farmer'] and seen['halfling gardener'] and seen['shalore scribe'] then break end;"
    "end;"
    "p.getTarget,p.canProject=og,oc;mb.refresh();"
    "local rows={};for _,a in ipairs(made) do local r=mb.row(a);r.anomaly_name=a.name;r.summoned_field=(a.summoner~=nil);rows[#rows+1]=r end;"
    "return {ok=true,rows=rows,count=#made,kept=#rows,calls=calls,removed=removed}")


def _ta2(n, tiles=(48, 64, 96)):
    sfx = '-' + n.replace(' ', '-')
    return [('natural_or_place', n, tiles), ('toggle', n, sfx), ('toggle_again', n, sfx)]


SCENES_TA2 = [
    ('derth-L1', 'town-derth', 1, {}, _ta2('human farmer') + _ta2('halfling gardener') +
     _ta2('halfling slinger') + [('ta2_slinger',)]),
    ('last-hope-L1', 'town-last-hope', 1, {}, _ta2('human citizen') + _ta2('halfling citizen')),
    ('lumberjack-L1', 'town-lumberjack-village', 1, {}, _ta2('lumberjack') + [('ta2_lumberjack',)]),
    ('iron-council-L1', 'town-iron-council', 1, {}, _ta2('dwarven earthwarden') +
     [('ta2_aura', 'dwarven earthwarden', 'T_BODY_OF_STONE')]),
    ('irkkk-L1', 'town-irkkk', 1, {}, _ta2('yeek mindslayer') + _ta2('yeek psionic') +
     [('ta2_wayist',)]),
    ('shatur-L1', 'town-shatur', 1, {}, _ta2('thalore hunter') + _ta2('thalore wilder')),
    ('gates-of-morning-L1', 'town-gates-of-morning', 1, {}, _ta2('elven sun-mage') +
     _ta2('elven archer') + [('ta2_aura', 'elven sun-mage', 'T_CHANT_OF_LIGHT'), ('ta2_archers',)]),
    ('elvala-L1', 'town-elvala', 1, {}, _ta2('shalore rune master') + [('ta2_anomaly',)]),
    ('mark-lineup-L1', 'mark-spellblaze', 1, {}, [('midstart',),
     ('lineup', 'ta2-all', TA2_LINEUP, TA2_POS), ('ta2_meta', TA2_TALL)]),
    ('mark-nicer-off-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('nicer_off', TA2_LINEUP, TA2_POS)]),
    ('mark-negative-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('ta2_negative',)]),
    # Run only with MLV_LOCALE=zh_hans (--only mark-lineup-zh-L1).
    ('mark-lineup-zh-L1', 'mark-spellblaze', 1, {}, [('midstart',),
     ('lineup', 'ta2-all-zh', TA2_LINEUP, TA2_POS)]),
]

# 1.25x layered small-tile trial (R32, 2026-10-01). A bright-floor and a
# dark-floor scene each place the 20 trial bodies, capture the same frame with
# the single trial flag off and on at 48/64/96, and diff the frames: 48 must
# change (creature enlarged over the shared disc) while 64/96 must be
# pixel-identical (the flattened token). At 48px one body is wounded to 50%
# life, one carries a shield and one is promoted to boss so the health arc,
# shield arc and rank badge are visible with the creature drawn above them.
OUT_LAYER = ADDON / 'evidence/token-layers-trial-20261001'
# R39/R43 native-tall standee redesign. Eligibility is static: only
# natively-tall ids with a body-only height > 1.0 cell and shipped art. R43
# kept ravenous-horror, snow-giant, ogre-guard and ninandra; R47 batch 1 adds
# 17 more accepted standees (M.standee_ids = 21). kra-tor (axe above a
# ~1-cell body) and the native 1-cell bosses are flat; standees render only at
# tiles >= 24px.
OUT_STANDEE = ADDON / 'evidence/token-standee-briagh-20261006'

# R45 normalised aura gate. The SDM aura flame size scales with the aura quad,
# but how many of its pixels land in the cell ABOVE the actor also scales with
# how far the creature's top reaches INTO that upper cell. `ratio /
# reach_ratio` removes that geometric part so ONE gate works for a native-sized
# snow-giant and a small ogre-guard body. reach_ratio is: how far the ON art
# top reaches into the upper cell divided by how far the native alpha top does.
# The ON feet are at cell centre + standee_feet*disc radius (0.753 cell below
# the cell top), so ON into-upper = on_reach - feet_depth. The native sprite is
# drawn display_h=2/display_y=-1, so its base is the cell bottom and native
# into-upper = native_reach - 1.0.
_STANDEE_STATIC = None


def _standee_static():
    global _STANDEE_STATIC
    if _STANDEE_STATIC is not None:
        return _STANDEE_STATIC
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        'bsh_live', ADDON / 'tools/build_standee_heights.py')
    bsh = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bsh)
    caps = dict(bsh.compute()[0])
    caps.update(bsh.parse_overrides(
        (ADDON / 'overload/mod/class/CheckerTokenStyle.lua').read_text()))
    catalogue = dict(bsh.parse_catalogue((ADDON / 'overload/mod/class/CheckerTokens.lua').read_text()))
    geom = {}
    pat = re.compile(r'\["([^"]+)"\]=\{left=(\d+),top=(\d+),right=(\d+),bottom=(\d+),canvas=(\d+)(?:,body_top=(\d+))?')
    for m in pat.finditer((ADDON / 'data/token-layer-geometry.lua').read_text()):
        g = {'left': int(m.group(2)), 'top': int(m.group(3)), 'right': int(m.group(4)),
             'bottom': int(m.group(5)), 'canvas': int(m.group(6))}
        if m.group(7):
            g['body_top'] = int(m.group(7))
        geom[m.group(1)] = g
    _STANDEE_STATIC = {'caps': caps, 'catalogue': catalogue, 'geom': geom, 'sprites': bsh.SPRITES}
    sty = (ADDON / 'overload/mod/class/CheckerTokenStyle.lua').read_text()
    feet = float(re.search(r'M\.standee_feet=([0-9.]+)', sty).group(1))
    diam = float(re.search(r'M\.token_diameter=([0-9.]+)', sty).group(1))
    # Crop top is two cells above the actor; the art top is 0.5 cell (cell
    # centre) + feet*token_diameter/2 above it, minus the art reach above feet.
    _STANDEE_STATIC['anchor_cells'] = 2.5 + feet * diam / 2.0
    # Feet sit at cell centre + standee_feet * disc radius below the cell top.
    _STANDEE_STATIC['feet_depth'] = 0.5 + feet * diam / 2.0
    return _STANDEE_STATIC


def native_alpha_top(alpha, threshold=8, min_pixels=3):
    """First native sprite row with at least `min_pixels` pixels above
    `threshold`.

    R46: an isolated alpha>8 pixel (a stray speck, a 1px antenna tip) must not
    set the native alpha top, exactly like the solid-top body measure. Falls
    back to the raw minimum when no row reaches the count.
    """
    import numpy as np
    for y in range(alpha.shape[0]):
        if int((alpha[y] > threshold).sum()) >= min_pixels:
            return y
    ys = np.where(alpha > threshold)[0]
    return int(ys.min()) if len(ys) else 0


def standee_reach(pid):
    """Static art reach in cells for one standee id, or None.

    R45/R46: reach_ratio is how far the ON art top reaches INTO the upper cell
    divided by how far the native alpha top reaches into it. The ON feet are
    at cell centre + standee_feet * disc radius (feet_depth), so the ON reach
    into the upper cell is on_reach - feet_depth. The native sprite is drawn
    display_h=2/display_y=-1, so the whole 64x128 canvas maps onto 2 cells and
    the cell top is sprite row 64: the alpha top row `ntop` reaches
    native_into = (64 - ntop)/64 cells into the upper cell. R45 assumed the
    alpha bottom was row 127 and used (bottom - top + 1)/64 - 1.0, which is
    only the same for a sprite that fills the canvas. `ntop` skips isolated
    pixels (>= 3 in the row) so a 1px speck cannot set the native top.

    Also returns the native sprite alpha top row (for the absolute
    flame-above-top check).
    """
    st = _standee_static()
    g = st['geom'].get(pid)
    cap = st['caps'].get(pid)
    image = st['catalogue'].get(pid)
    if not (g and cap and image):
        return None
    import numpy as np
    from PIL import Image
    a = np.asarray(Image.open(st['sprites'] / image).convert('RGBA'))[..., 3]
    ys = np.where(a > 8)[0]
    ntop, nbottom = native_alpha_top(a), int(ys.max())
    native_reach = (nbottom - ntop + 1) / 64.0
    body_h = g['bottom'] - g.get('body_top', g['top'])
    bw = g['right'] - g['left']
    scale = min(cap / body_h, 1.0 / bw)
    on_reach = (g['bottom'] - g['top']) * scale
    feet_depth = st['feet_depth']
    on_into = on_reach - feet_depth
    native_into = (64 - ntop) / 64.0
    return {'on_reach': on_reach, 'native_reach': native_reach,
            'on_into': on_into, 'native_into': native_into,
            'feet_depth': feet_depth,
            'ratio': (on_into / native_into) if native_into else 0.0,
            'native_top_px': ntop, 'native_bottom_px': nbottom,
            'anchor_cells': st['anchor_cells']}


AURA_FLAME_BAND_MIN_PX = 3


def aura_score_region(sx, sy, tile, on_quad, native_quad=None):
    """Fixed half-open screen region shared by ON and NATIVE.

    Above own-cell top; up to the higher quad top (native sprite defaults
    to x=0,y=-1,w=1,h=2). Include own column +/- half a cell and both
    quad widths, rounding outwards so lateral spill is never truncated.
    """
    native_quad = native_quad or dict(display_x=0, display_y=-1, display_w=1, display_h=2)
    quads = (on_quad, native_quad)
    left = min(-0.5, *(q['display_x'] for q in quads))
    right = max(1.5, *(q['display_x'] + q['display_w'] for q in quads))
    top = min(q['display_y'] for q in quads)
    return (math.floor(sx + left * tile), math.floor(sy + top * tile),
            math.ceil(sx + right * tile), sy)


def flame_band_widths(mask):
    """Longest contiguous changed-pixel run per row, not scattered specks."""
    widths = []
    for row in mask:
        best = run = 0
        for pixel in row:
            run = run + 1 if pixel else 0
            best = max(best, run)
        widths.append(best)
    return widths


def _diff_top_row(a, b, box, threshold=12):
    """First row with a contiguous >=3px flame band, or None; no spike fallback."""
    widths = flame_band_widths(_diff_mask(a, b, box, threshold))
    return next((y for y, width in enumerate(widths)
                 if width >= AURA_FLAME_BAND_MIN_PX), None)


def _median_defined(values):
    """Median of the defined (non-None) values, or None when there are none."""
    kept = [v for v in values if v is not None]
    return _median(kept) if kept else None
R39_STANDS = [
    ('ogre guard', '/data/general/npcs/ogre.lua', None, 'ogre-guard'),
    ('snow giant', '/data/general/npcs/snow-giant.lua', None, 'snow-giant'),
    ('Ninandra, the Great Weaver', '/data/general/npcs/spider.lua', None, 'ninandra'),
    ("Kra'Tor the Gluttonous", '/data/general/npcs/orc.lua', None, 'kra-tor'),
    ('ravenous horror', '/data/general/npcs/horror_aquatic.lua', None, 'ravenous-horror'),
    # R47 batch 1: the 17 accepted standee ids, with the verified in-game name,
    # source and define_as (unique bosses only) from the batch provenance.
    ('heavy bone giant', '/data/general/npcs/bone-giant.lua', None, 'heavy-bone-giant'),
    ('runed bone giant', '/data/general/npcs/bone-giant.lua', None, 'runed-bone-giant'),
    ('eternal bone giant', '/data/general/npcs/bone-giant.lua', None, 'eternal-bone-giant'),
    ('Atamathon the Giant Golem', '/data/zones/golem-graveyard/npcs.lua', 'ATAMATHON', 'atamathon'),
    ('Heavy Sentinel', '/data/zones/rak-shor-pride/npcs.lua', 'HEAVY_SENTINEL', 'heavy-sentinel'),
    ('Burb the snow giant champion', '/data/general/npcs/snow-giant.lua', 'BURB_SNOW_GIANT', 'burb-snow-giant-champion'),
    ('archlich', '/data/general/npcs/lich.lua', None, 'archlich'),
    ('snow giant chieftain', '/data/general/npcs/snow-giant.lua', None, 'snow-giant-chieftain'),
    ('snow giant boulder thrower', '/data/general/npcs/snow-giant.lua', None, 'snow-giant-boulder-thrower'),
    ('snow giant thunderer', '/data/general/npcs/snow-giant.lua', None, 'snow-giant-thunderer'),
    ('Minotaur of the Labyrinth', '/data/zones/maze/npcs.lua', 'MINOTAUR_MAZE', 'minotaur-maze'),
    ("champion of Urh'Rok", '/data/general/npcs/major-demon.lua', None, 'champion-of-urh-rok'),
    ('ogre warmaster', '/data/general/npcs/ogre.lua', None, 'ogre-warmaster'),
    ('Celia', '/data/zones/last-hope-graveyard/npcs.lua', 'CELIA', 'celia'),
    ('dremling', '/data/general/npcs/horror-corrupted.lua', None, 'dremling'),
    ('forge-giant', '/data/general/npcs/major-demon.lua', None, 'forge-giant'),
    ('Healer Astelrid', '/data/zones/conclave-vault/npcs.lua', 'HEALER_ASTELRID', 'healer-astelrid'),
    # R50 batch 2: exact native names, sources and unique definitions.
    ('treant', '/data/general/npcs/plant.lua', None, 'treant'),
    ('Wrathroot', '/data/zones/old-forest/npcs.lua', 'WRATHROOT', 'wrathroot'),
    ('ogre mauler', '/data/general/npcs/ogre.lua', None, 'ogre-mauler'),
    ('ogre rune-spinner', '/data/general/npcs/ogre.lua', None, 'ogre-rune-spinner'),
    ('ultimate shivgoroth', '/data/general/npcs/shivgoroth.lua', None, 'ultimate-shivgoroth'),
    ('ogric abomination', '/data/zones/conclave-vault/npcs.lua', None, 'ogric-abomination'),
    ('Half-Finished Bone Giant', '/data/zones/blighted-ruins/npcs.lua', 'HALF_BONE_GIANT', 'half-finished-bone-giant'),
    ('Norgos, the Guardian', '/data/zones/norgos-lair/npcs.lua', 'NORGOS', 'norgos-guardian'),
    ('Norgos, the Frozen', '/data/zones/norgos-lair/npcs.lua', 'FROZEN_NORGOS', 'norgos-frozen'),
    ('Horned Horror', '/data/zones/maze/npcs.lua', 'HORNED_HORROR', 'horned-horror'),
    ("Harkor'Zun", '/data/general/npcs/xorn.lua', 'FULL_HARKOR_ZUN', 'harkor-zun'),
    ('dolleg', '/data/general/npcs/major-demon.lua', None, 'dolleg'),
    ('dúathedlen', '/data/general/npcs/major-demon.lua', None, 'duathedlen'),
    ('thaurhereg', '/data/general/npcs/major-demon.lua', None, 'thaurhereg'),
    ('uruivellas', '/data/general/npcs/major-demon.lua', None, 'uruivellas'),
    ('xhaiak arachnomancer', '/data/zones/ardhungol/npcs.lua', None, 'xhaiak-arachnomancer'),
    ('Rotting Titan', '/data/zones/rak-shor-pride/npcs.lua', 'ROTTING_TITAN', 'rotting-titan'),
    ('Corrupted Daelach', '/data/zones/valley-moon/npcs.lua', 'CORRUPTED_DAELACH', 'corrupted-daelach'),
    # R51 batch 3: native definitions verified in G4 and batch provenance.
    ('Rantha the Worm', '/data/zones/daikara/npcs.lua', 'RANTHA_THE_WORM', 'rantha'),
    ('Varsha the Writhing', '/data/zones/daikara/npcs.lua', 'VARSHA_THE_WRITHING', 'varsha'),
    ('fire wyrm', '/data/general/npcs/fire-drake.lua', None, 'fire-wyrm'),
    ('ice wyrm', '/data/general/npcs/cold-drake.lua', None, 'ice-wyrm'),
    ('storm wyrm', '/data/general/npcs/storm-drake.lua', None, 'storm-wyrm'),
    ('venom wyrm', '/data/general/npcs/venom-drake.lua', None, 'venom-wyrm'),
    ('greater multi-hued wyrm', '/data/general/npcs/multihued-drake.lua', 'GREATER_MULTI_HUED_WYRM', 'greater-multi-hued-wyrm'),
    ('ultimate faeros', '/data/general/npcs/faeros.lua', None, 'ultimate-faeros'),
    ('Fyrk, Faeros High Guard', '/data/zones/charred-scar/npcs.lua', 'FYRK', 'fyrk'),
    ('Snaproot', '/data/zones/old-forest/npcs.lua', 'SNAPROOT', 'snaproot'),
    ('Temporal Defiler', '/data/zones/town-point-zero/npcs.lua', 'TEMPORAL_DEFILER', 'temporal-defiler'),
    ('Arch Zephyr', '/data/zones/rak-shor-pride/npcs.lua', 'ARCH_ZEPHYR', 'arch-zephyr'),
    ("Ak'Gishil", '/data/general/npcs/horror.lua', None, 'ak-gishil'),
    # R52 final optional batch: exact native identities.
    ('Prox the Mighty', '/data/zones/trollmire/npcs.lua', 'TROLL_PROX', 'prox'),
    ('Bill the Stone Troll', '/data/zones/trollmire/npcs.lua', 'TROLL_BILL', 'bill'),
    ('Shax the Slimy', '/data/zones/trollmire/npcs.lua', 'TROLL_SHAX', 'shax'),
    ('onilug', '/data/general/npcs/minor-demon.lua', None, 'onilug'),
    ('Chronolith Twin', '/data/zones/temporal-rift/npcs.lua', 'CHRONOLITH_TWIN', 'chronolith-twin'),
    ('Chronolith Clone', '/data/zones/temporal-rift/npcs.lua', 'CHRONOLITH_CLONE', 'chronolith-clone'),
    ('Briagh, Great Sand Wyrm', '/data/zones/briagh-lair/npcs.lua', 'BRIAGH', 'briagh'),
]
# The R47 batch-1 additions and the R43 original four, by token id.
R39_BATCH1_IDS = ("heavy-bone-giant", "runed-bone-giant", "eternal-bone-giant",
                  "atamathon", "heavy-sentinel", "burb-snow-giant-champion",
                  "archlich", "snow-giant-chieftain", "snow-giant-boulder-thrower",
                  "snow-giant-thunderer", "minotaur-maze", "champion-of-urh-rok",
                  "ogre-warmaster", "celia", "dremling", "forge-giant",
                  "healer-astelrid")
R39_BATCH2_IDS = ('treant', 'wrathroot', 'ogre-mauler', 'ogre-rune-spinner', 'ultimate-shivgoroth', 'ogric-abomination', 'half-finished-bone-giant', 'norgos-guardian', 'norgos-frozen', 'horned-horror', 'harkor-zun', 'dolleg', 'duathedlen', 'thaurhereg', 'uruivellas', 'xhaiak-arachnomancer', 'rotting-titan', 'corrupted-daelach')
R39_BATCH3_IDS = ('rantha', 'varsha', 'fire-wyrm', 'ice-wyrm', 'storm-wyrm', 'venom-wyrm', 'greater-multi-hued-wyrm', 'ultimate-faeros', 'fyrk', 'snaproot', 'temporal-defiler', 'arch-zephyr', 'ak-gishil')
R39_BATCH4_IDS = ('prox', 'bill', 'shax', 'onilug', 'chronolith-twin', 'chronolith-clone')
R53_BRIAGH_IDS = ('briagh',)
R39_ORIGINAL_IDS = ("ravenous-horror", "snow-giant", "ogre-guard", "ninandra")
# One TALL new id for the animated aura and native-facing mirror checks.
R39_AURA_ACTOR = ('Rantha the Worm', 40)  # (in-game name, R39_STANDS index)
# R50: new TALL and SQUARE actors, retaining the three R49 regressions.
R39_AURA_ACTORS = (
    ('Briagh, Great Sand Wyrm', 59),
    ('Bill the Stone Troll', 54),
    ('Rantha the Worm', 40),
    ('Arch Zephyr', 51),
    ('Corrupted Daelach', 39),
    ('Norgos, the Guardian', 29),
    ('heavy bone giant', 5),
    ('snow giant', 1),
    ('ogre guard', 0),
    ('Celia', 18),
    ('forge-giant', 20),
    ('Healer Astelrid', 21),
    ('uruivellas', 36),
    ('ogre rune-spinner', 25),
)
# Native 1-cell bosses: no standee, flat token + rank badge.
R39_FLAT_BOSSES = [
    ('Phoenix', '/data/general/npcs/bird.lua', 'NPC_PHOENIX', 'phoenix'),
    ('Vor, Grand Geomancer of the Pride', '/data/zones/vor-pride/npcs.lua', 'VOR', 'vor'),
    ('Grushnak, Battlemaster of the Pride', '/data/zones/grushnak-pride/npcs.lua', 'GRUSHNAK', 'grushnak'),
    ('Rungof the Warg Titan', '/data/general/npcs/canine.lua', None, 'rungof'),
    ('Shardskin', '/data/zones/old-forest/npcs.lua', None, 'shardskin'),
    ('Subject Z', '/data/zones/halfling-ruins/npcs.lua', None, 'subject-z'),
]
R39_ORDINARY = [
    ('wolf', '/data/general/npcs/canine.lua', None, 'wolf'),
    ('human guard', '/data/general/npcs/sunwall-town.lua', None, 'human-guard'),
    ('giant spider', '/data/general/npcs/spider.lua', None, 'giant-spider'),
]
STANDEE_GROUPS = {'standee': R39_STANDS, 'flatboss': R39_FLAT_BOSSES, 'ordinary': R39_ORDINARY}
# (dx, dy, group, index) relative to the hero. kra-tor sits directly below
# snow-giant at x=0 (occlusion vs NATIVE), ninandra is forced friendly and
# kra-tor neutral by the scene special, and the native 1-cell bosses are flat.
STANDEE_CROWD = [
    (-2, -2, 'standee', 0), (-1, -2, 'standee', 4), (0, -2, 'standee', 1), (1, -2, 'flatboss', 0), (2, -2, 'ordinary', 0),
    (-2, -1, 'standee', 2), (-1, -1, 'flatboss', 1), (0, -1, 'standee', 3), (1, -1, 'flatboss', 2), (2, -1, 'ordinary', 1),
    (-2, 0, 'flatboss', 3), (-1, 0, 'flatboss', 4), (1, 0, 'flatboss', 5),
]
# Repaint check: ogre-guard + ninandra beside snow-giant and a black spider.
STANDEE_REPAINT = [
    (-3, 0, 'standee', 0), (-1, 0, 'standee', 1), (1, 0, 'standee', 2), (3, 0, 'ordinary', 2),
]
# Flat-token sanity row at 16px: standees must be off below 24px. R47 adds a
# batch-1 id (heavy bone giant, index 5) to prove the new art is flat too.
STANDEE_FLAT = [
    (-2, 0, 'standee', 0), (-1, 0, 'standee', 1), (0, -1, 'standee', 5), (3, 0, 'standee', 40),
    (1, 0, 'standee', 2), (2, 0, 'standee', 3),
    (-1, -1, 'standee', 53), (1, -1, 'standee', 54), (2, -1, 'standee', 55),
    (-2, 1, 'standee', 56), (-1, 1, 'standee', 57), (1, 1, 'standee', 58),
    (2, 1, 'standee', 59),
]
# R47: several batch-1 standees adjacent for one crowd capture at 48px.
STANDEE_BATCH1_CROWD = [
    (-2, -1, 'standee', 5), (-1, -1, 'standee', 6), (0, -1, 'standee', 7),
    (1, -1, 'standee', 12), (2, -1, 'standee', 15), (-1, 0, 'standee', 11),
    (1, 0, 'standee', 16),
]
# Adjacent new trees/ice/rock/demons, including the width-bound cases.
STANDEE_BATCH2_CROWD = [
    (-2, -1, 'standee', 22), (-1, -1, 'standee', 23), (0, -1, 'standee', 26),
    (1, -1, 'standee', 32), (2, -1, 'standee', 33), (-1, 0, 'standee', 38),
    (1, 0, 'standee', 39),
]
# R51 adjacent dragons: every neighbour cell remains separately locatable.
STANDEE_BATCH3_CROWD = [
    (-2,-1,'standee',40),(-1,-1,'standee',41),(0,-1,'standee',42),
    (1,-1,'standee',43),(2,-1,'standee',44),(-1,0,'standee',45),(1,0,'standee',46),
]
# R52 adjacent Trollmire trio, in a single row.
STANDEE_BATCH4_CROWD = [(-1,-1,'standee',53),(0,-1,'standee',54),(1,-1,'standee',55)]
STANDEE_BRIAGH_CROWD = STANDEE_BATCH3_CROWD + [(2, 0, 'standee', 59)]
SCENES_STANDEE = [
    ('standee-briagh-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('standee_grid', 'briagh')]),
    ('standee-batch4-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('standee_grid', 'batch4')]),
    ('standee-facing-bill-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('standee_grid', 'facing-bill')]),
    ('standee-facing-batch4-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('standee_grid', 'facing-batch4')]),
    ('standee-rank-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('standee_grid', 'rank')]),
    ('standee-crowd-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('standee_grid', 'crowd')]),
    ('standee-open-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('standee_grid', 'open')]),
    ('standee-repaint-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('standee_grid', 'repaint')]),
    ('standee-forge-innate-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('standee_grid', 'forge-innate')]),
    ('standee-aura-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('standee_grid', 'aura')]),
    # Main includes Forge and reuses its crop paths; final dedicated capture owns them.
    ('standee-aura-forge-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('standee_grid', 'aura-forge')]),
    ('standee-sequential-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('standee_grid', 'sequential')]),
    ('standee-facing-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('standee_grid', 'facing')]),
    ('standee-facing-new-tall-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('standee_grid', 'facing-new-tall')]),
    # R48 item B: the R46 ogre-guard facing scene, restored beside the TALL id.
    ('standee-facing-ogre-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('standee_grid', 'facing-ogre')]),
    ('standee-facing-heavy-bone-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('standee_grid', 'facing-heavy-bone')]),
    ('standee-facing-daelach-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('standee_grid', 'facing-daelach')]),
    ('standee-top-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('standee_grid', 'top')]),
    ('standee-wide-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('standee_grid', 'wide')]),
    ('standee-flat-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('standee_grid', 'flat')]),
    ('standee-batch3-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('standee_grid', 'batch3')]),
    ('standee-batch2-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('standee_grid', 'batch2')]),
    ('standee-batch1-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('standee_grid', 'batch1')]),
    ('standee-crowd-zh-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('standee_grid', 'crowd-zh')]),
]
EXPECT.update({name: tid for name, _, _, tid in R39_STANDS + R39_FLAT_BOSSES if tid})
LAYER_CASES = [
    ('wolf', '/data/general/npcs/canine.lua', None, 'wolf'),
    ('warg', '/data/general/npcs/canine.lua', None, 'warg'),
    ('great wolf', '/data/general/npcs/canine.lua', None, 'great-wolf'),
    ('orc warrior', '/data/general/npcs/orc.lua', None, 'orc-warrior'),
    ('orc archer', '/data/general/npcs/orc.lua', None, 'orc-archer'),
    ('orc assassin', '/data/general/npcs/orc.lua', None, 'orc-assassin'),
    ('skeleton warrior', '/data/general/npcs/skeleton.lua', None, 'skeleton-warrior'),
    ('skeleton mage', '/data/general/npcs/skeleton.lua', None, 'skeleton-mage'),
    ('skeleton archer', '/data/general/npcs/skeleton.lua', None, 'skeleton-archer'),
    ('giant spider', '/data/general/npcs/spider.lua', None, 'giant-spider'),
    ('Ungolë', '/data/zones/ardhungol/npcs.lua', None, 'ungole'),
    ('Weaver Queen', '/data/zones/unhallowed-morass/npcs.lua', None, 'weaver-queen'),
    ('Phoenix', '/data/general/npcs/bird.lua', 'NPC_PHOENIX', 'phoenix'),
    ('storm wyrm', '/data/general/npcs/storm-drake.lua', None, 'storm-wyrm'),
    ('human guard', '/data/general/npcs/sunwall-town.lua', None, 'human-guard'),
    ('derth guard', '/data/zones/town-derth/npcs.lua', None, 'derth-guard'),
    ('elven mage', '/data/general/npcs/elven-caster.lua', None, 'elven-mage'),
    ('Necromancer', '/data/zones/blighted-ruins/npcs.lua', None, 'necromancer'),
    ('pyromancer', '/data/zones/town-angolwen/npcs.lua', None, 'pyromancer'),
    ('yeek mindslayer', '/data/zones/town-irkkk/npcs.lua', None, 'yeek-mindslayer'),
]
LAYER_POS = [(x, y) for y in (-2, 0, 2, 4) for x in (-4, -2, 0, 2, 4)]
EXPECT.update({name: tid for name, _, _, tid in LAYER_CASES})
SCENES_LAYER = [
    # Bright floor: one map cell of the bright stone/adapter floor.
    ('layer-bright-L1', 'dreadfell', 2, {}, [('midstart',), ('layer_grid', 'bright')]),
    # Dark floor: the darker brown checker floor.
    ('layer-dark-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('layer_grid', 'dark')]),
    # Run only with MLV_LOCALE=zh_hans (--only layer-bright-zh-L1).
    ('layer-bright-zh-L1', 'mark-spellblaze', 1, {}, [('midstart',), ('layer_grid', 'bright-zh')]),
]

REACH_FALLBACK = True  # batch N: natural actor in a closed vault -> place from the native list, flagged natural_unreachable
SUSTAIN_SNAP = ("local a=mb.byName(%s);pcall(function() a:updateModdableTile() end);mb.refresh();mb.focus(a.x,a.y);"
                "local n=0;for _ in pairs(a.shader_auras or {}) do n=n+1 end;"
                "local t=a.replace_display or a;local au=0;for _,m in ipairs(t.add_mos or {}) do if m._isshaderaura then au=au+1 end end;"
                "local function L(t) local o={};for _,m in ipairs(t or {}) do o[#o+1]=(m._isshaderaura and 'AURA:' or '')..tostring(m.image)..'/'..tostring(m.shader or '') end return o end;"
                "local s={};for tid,v in pairs(a.sustain_talents or {}) do if v then s[#s+1]=tid end end table.sort(s);"
                "local e={};for eid,_ in pairs(a.tmp or {}) do e[#e+1]=tostring(eid) end table.sort(e);"
                "return {row=mb.row(a),sustains=s,effects=e,actor_shader=a.shader or false,shader_auras=n,aura_entries_in_display=au,image=a.image,"
                "own_add_mos=L(a.add_mos),replace_display_image=a.replace_display and a.replace_display.image or false,"
                "replace_display_add_mos=L(a.replace_display and a.replace_display.add_mos),particles=(function() local c=0;for _ in pairs(a.__particles or {}) do c=c+1 end return c end)()}")

def resolve_gloom(bridge, base):
    """Pick a naturally generated actor whose name is <Heart of the Gloom prefix> + base, else the
    zone npc_list prototype with that name. Returns the exact runtime name (prefix is random per load)."""
    code = ("local pf={'gloomy ','deformed ','sick ','dreaming ','slumbering ','dozing '};local base=%s;"
            "local function m(n) if type(n)~='string' then return false end for _,p in ipairs(pf) do if n==p..base then return true end end end;"
            "local nat,lst;for _,a in pairs(game.level.entities) do if a.x and a~=game.player and not a._checker_live_placed and m(a.name) then nat=a.name end end;"
            "for _,p in pairs(game.zone.npc_list) do if type(p)=='table' and m(p.name) then lst=p.name end end;"
            "return {natural=nat or false,listed=lst or false}") % json.dumps(base)
    return bridge.lua(code)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def lua_value(v):
    if v is None:
        return 'nil'
    if isinstance(v, bool):
        return 'true' if v else 'false'
    return json.dumps(v, ensure_ascii=False)


def lua_opts(opts):
    return '{' + ','.join(f'{k}={lua_value(v)}' for k, v in opts.items()) + '}' if opts else 'nil'


class Bridge:
    def __init__(self):
        self.transcript = []

    def raw(self, code, timeout=240):
        """tools/fixture_debug.py; if its 45 s wait expires during a slow level
        generation, keep waiting for the same pending result file."""
        result = HOME / 'board-test-result.txt'
        run = subprocess.run([sys.executable, str(ADDON / 'tools/fixture_debug.py'), code],
                             capture_output=True, text=True, timeout=120)
        text = run.stdout
        if run.returncode and 'did not finish' in (run.stdout + run.stderr):
            deadline = time.monotonic() + timeout
            while time.monotonic() < deadline:
                if result.exists() and result.stat().st_size:
                    text = result.read_text()
                    break
                time.sleep(.2)
            else:
                raise RuntimeError('fixture Lua timed out; inspect session/game.log')
        self.transcript.append(text[-2000:])
        if 'PASS\n' not in text:
            raise RuntimeError('fixture Lua failed: ' + text[-3000:] + run.stderr[-1000:])

    def lua(self, body, timeout=240):
        out = HOME / 'mlv.json'
        out.unlink(missing_ok=True)
        self.raw("ms=ms or dofile('/data-checker-fixture/monster-live_map_survey.lua');"
                 "mb=mb or dofile('/data-checker-fixture/monster-live_monster_batch.lua');"
                 "local r=(function() " + body + " end)();ms.dump('/mlv.json',r or {ok=true})", timeout)
        data = json.loads(out.read_text())
        out.unlink(missing_ok=True)
        return data

    def shot(self, name, settle_s=0.5, clear_dialogs=True):
        if CLEAN and clear_dialogs:
            self.lua("ms.caveClearDialogs();return true")
        src = HOME / (name + '.png')
        # The isolated screenshot command is occasionally slow under the aura
        # scene's rapid cadence; retry once instead of losing the whole scene.
        for attempt in range(2):
            src.unlink(missing_ok=True)
            time.sleep(settle_s)
            run = subprocess.run([sys.executable, str(ADDON / 'tools/fixture_command.py'), 'shot', name],
                                 capture_output=True, text=True, timeout=40)
            assert run.returncode == 0, run.stdout + run.stderr
            for _ in range(300):
                if src.exists() and src.stat().st_size:
                    break
                time.sleep(.1)
            if src.exists() and src.stat().st_size:
                break
        if not (src.exists() and src.stat().st_size):
            raise RuntimeError('screenshot never appeared: ' + name)
        SHOTS.mkdir(parents=True, exist_ok=True)
        dst = SHOTS / src.name
        shutil.copy2(src, dst)
        src.unlink(missing_ok=True)
        return dst


def crop(path, screen, name, span=2):
    from PIL import Image
    x, y, t = screen
    CROPS.mkdir(parents=True, exist_ok=True)
    im = Image.open(path).convert('RGB')
    box = clamp_box((max(0, x - span * t), max(0, y - span * t), x + (span + 1) * t, y + (span + 1) * t))
    dst = CROPS / (name + '.png')
    im.crop(box).save(dst)
    return dst


def rel(path):
    return str(Path(path).relative_to(OUT))


def capture(bridge, label, actor, tiles, record):
    for t in tiles:
        row = bridge.lua(f"mb.setTile({t});local a=assert(mb.byName({json.dumps(actor, ensure_ascii=False)}));"
                         "mb.focus(a.x,a.y);return mb.row(a)")
        if CLEAN:
            view = clean_view_actor(bridge, actor)
            row = bridge.lua(f"local a=mb.byName({json.dumps(actor, ensure_ascii=False)});local r=mb.row(a);r.can_see=game.player:canSee(a) and true or false;return r")
        assert row['screen'][2] == t, row['screen']
        name = f'{label}-{t}'
        path = bridge.shot(name)
        c = crop(path, row['screen'], name + '-crop')
        record.setdefault('shots', []).append({'tile': t, 'actor': actor, 'file': rel(path), 'sha256': digest(path),
                                               'crop': rel(c), 'row': row})
    if tiles:
        bridge.lua('mb.setTile(64)')


def standee_groups():
    return STANDEE_GROUPS


def standee_crowd_block_size(layout):
    """Include every offset in the native freeBlock half-open centred bounds."""
    width = max([5] + [max(-2*dx, 2*dx+1) for dx, _, _, _ in layout])
    height = max([4] + [max(-2*dy, 2*dy+1) for _, dy, _, _ in layout])
    return width, height


def standee_place_crowd(bridge, layout):
    """Find a block covering the whole layout, then place on exact free cells.

    Repaint offsets extend to +/-3; the original 5x4 search omitted those ends.
    placeAt keeps its native free/visible assertion, so adjacency is real.
    """
    width, height = standee_crowd_block_size(layout)
    blk = bridge.lua(f"local p=game.player;return mb.freeBlock(p.x,p.y,{width},{height})")
    if not blk:
        return None
    bx, by = blk
    bridge.lua(f"game.player:move({bx},{by},true);mb.refresh()")
    placed = []
    for dx, dy, group, index in layout:
        name, source, das, tid = STANDEE_GROUPS[group][index]
        row = bridge.lua(f"return mb.placeAt({json.dumps(name, ensure_ascii=False)},"
                         f"{json.dumps(source) if source else 'nil'},{bx + dx},{by + dy},"
                         f"{json.dumps(das) if das else 'nil'})")
        placed.append({'name': name, 'group': group, 'id': tid, 'row': row})
    return {'block': [bx, by], 'placed': placed}


def standee_place_one(bridge, group, index, dx=0, dy=-1):
    name, source, das, tid = STANDEE_GROUPS[group][index]
    # Snap to the nearest free visible cell (robust across room shapes); the
    # returned row carries the real coordinates used for the crop region.
    row = bridge.lua(f"return mb.place({json.dumps(name, ensure_ascii=False)},"
                     f"{json.dumps(source) if source else 'nil'},{dx},{dy},"
                     f"{json.dumps(das) if das else 'nil'})")
    return {'name': name, 'id': tid, 'row': row}


def standee_state(bridge):
    return bridge.lua(
        "local S=require 'mod.class.CheckerTokenStyle';local o={};for _,a in pairs(game.level.entities) do if a.x and a._checker_live_placed and a._checker_token then "
        "local s=a._checker_token;local cap=S.standeeHeight(s.id);local drawn=false;"
        "local box=s.layer_box;if cap and box and box.right-box.left>0 and box.bottom-box.top>0 then "
        "local bh=box.bottom-(box.body_top or box.top);"
        "drawn=bh*math.min(cap/bh,S.standee_width/(box.right-box.left)) end;"
        "o[#o+1]={name=a.name,id=s.id,size_category=a.size_category,layered=s.layered and true or false,"
        "standee=s.standee and true or false,height_cap=cap or false,drawn_cells=drawn or false,"
        "has_box=s.layer_box~=nil,canvas=box and box.canvas or false,scale=s.scale,layer_id=s.layer_id or false} end end;return o")


def standee_actor_metrics(bridge, name):
    """Per-id size_category plus the cap and drawn height in cells that the ship
    path computes at draw time (mirrors Actor:checkerLayerCreature)."""
    q = json.dumps(name, ensure_ascii=False)
    return bridge.lua(
        "local S=require 'mod.class.CheckerTokenStyle';local a=mb.byName(%s);if not a then return {} end;"
        "local s=a._checker_token;local cap=S.standeeHeight(s and s.id or nil);local drawn=false;"
        "local box=s and s.layer_box;if cap and box and box.right-box.left>0 and box.bottom-box.top>0 then "
        "local bh=box.bottom-(box.body_top or box.top);"
        "drawn=bh*math.min(cap/bh,S.standee_width/(box.right-box.left)) end;"
        "return {size_category=a.size_category,render_id=(s and s.id) or false,height_cap=cap or false,"
        "drawn_cells=drawn or false,standee=(s and s.standee) and true or false,has_box=box~=nil}" % q)


def standee_region(bridge, tile, up=2, down=1, span=1):
    rows = bridge.lua(
        "local o={};for _,a in pairs(game.level.entities) do if a.x and a._checker_live_placed then "
        "local m=game.level.map;o[#o+1]={math.floor(m.display_x+(a.x-m.mx)*m.tile_w),math.floor(m.display_y+(a.y-m.my)*m.tile_h)} end end;return o")
    xs = [r[0] for r in rows] or [0]
    ys = [r[1] for r in rows] or [0]
    return clamp_box((min(xs) - span * tile, min(ys) - up * tile, max(xs) + (span + 1) * tile, max(ys) + (down + 1) * tile))


def standee_remove_idle_particles(bridge, name):
    """Remove level idle particles without pausing or touching shader auras."""
    q = json.dumps(name, ensure_ascii=False)
    return bridge.lua(
        "local counts={};local total=0;local own=0;"
        "for uid,a in pairs(game.level.entities) do if a.__particles then local rem={};"
        "for e in pairs(a.__particles) do rem[#rem+1]=e end;local n=0;"
        "for _,e in ipairs(rem) do pcall(function() a:removeParticles(e) end);"
        "if not a.__particles or not a.__particles[e] then n=n+1 end end;"
        "if n>0 then counts[#counts+1]={uid=uid,name=a.name or false,removed=n};"
        f"total=total+n;if a.name=={q} then own=own+n end end end end;"
        "return {total=total,actor_removed=own,entities=counts}")


def outside_quad_pixels(mask, quads):
    """Changed pixels outside the union of raster-covered screen quads.

    Bounds are continuous screen pixels. Floor/ceil includes exactly the
    pixels intersected by a quad; no padding or noise tolerance is added.
    """
    import numpy as np
    inside = np.zeros(mask.shape, dtype=bool)
    height, width = mask.shape
    for left, top, right, bottom in quads:
        x0, y0 = max(0, math.floor(left)), max(0, math.floor(top))
        x1, y1 = min(width, math.ceil(right)), min(height, math.ceil(bottom))
        if x1 > x0 and y1 > y0:
            inside[y0:y1, x0:x1] = True
    return int((mask & ~inside).sum())


def cleaned_baseline_validity(frames, residual_particles):
    """Three unpaused RGB crops must be clean and stable at threshold 12."""
    import numpy as np
    drift = [int((np.abs(np.asarray(a).astype(int) - np.asarray(b).astype(int))
                  .sum(axis=2) > 12).sum()) for a, b in zip(frames, frames[1:])]
    valid = len(frames) == 3 and len(residual_particles) == 3 \
        and not any(residual_particles) and not any(drift)
    return {'valid': valid, 'drift_pixels': drift,
            'residual_particles': residual_particles, 'diff_threshold': 12}


def aura_case_validity(on, native):
    """Lighting invalidity has the same explicit label as facing."""
    for record in (on, native):
        baseline = record.get('baseline_validity', {})
        for key in ('lighting', 'lighting_frames'):
            if key in baseline and not baseline[key].get('valid'):
                return 'INVALID (lighting)'
    return 'VALID' if all(r.get('baseline_validity', {}).get('valid') for r in (on, native)) else 'INVALID'


def lighting_validity(brightness, bare=True, reference=None, samples=3):
    """Pre-registered R52 floor; lighting never changes a detector threshold."""
    ref = reference or AURA_CONTRACT['LIGHTING_REFERENCE']
    reference = ref['mean_rgb_brightness']
    valid = bare and len(brightness) == samples and all(
        math.isfinite(v) and reference * (1 - ref['tolerance_fraction']) <= v
        <= reference * (1 + ref['tolerance_fraction'])
        for v in brightness)
    return {'valid': valid, 'status': 'VALID' if valid else 'INVALID (lighting)',
            'brightness': brightness, 'reference': reference,
            'tolerance_fraction': ref['tolerance_fraction'], 'bare_floor': bare}


# Disposable fixture only: native FOV calls can otherwise overwrite manually
# lit cells between setup and screenshot. Re-apply one registered state after
# every native FOV refresh, including refreshes caused by aura removal/facing.
STANDEE_LIGHTING_LUA = r"""
local p=game.player;local mm=game.level.map
assert(require('mod.class.CheckerFixture').enabled() and not profile.auth)
local a=assert(mb.byName(NAME));mm._checker_measure_light={x=a.x,y=a.y}
config.settings.tome.daynight=false;config.settings.tome.smooth_fov=false;p.lite=3
-- Native outdoor thunderstorm darkens setShown to .3 and adds a realtime
-- lightning background. Retire this environment event uniformly in fixture
-- measurements, preserving its original state in the census.
mm._checker_removed_light_events=mm._checker_removed_light_events or {}
if game.zone.thunderstorm_event_levels and game.zone.thunderstorm_event_levels[game.level.level] then
 local event={name='thunderstorm',shown_before=mm.color_shown,obscure_before=mm.color_obscure,removed_effects={},removed_map_particles=0}
 game.level.data.background=game.level.data.thunderstorm_event_background
 game.level.data.thunderstorm_event_background=nil
 game.zone.thunderstorm_event_levels[game.level.level]=nil
 local effects={};for _,id in ipairs(game.level.effects or {}) do
  if id=='EFF_ZONE_AURA_THUNDERSTORM' then event.removed_effects[#event.removed_effects+1]=id else effects[#effects+1]=id end
 end;game.level.effects=effects
 for _,e in pairs(game.level.entities) do
  if e.EFF_ZONE_AURA_THUNDERSTORM and e:hasEffect(e.EFF_ZONE_AURA_THUNDERSTORM) then
   e:removeEffect(e.EFF_ZONE_AURA_THUNDERSTORM,true)
  end
 end
 local particles={};for _,ps in ipairs(mm.particles or {}) do particles[#particles+1]=ps end
 for _,ps in ipairs(particles) do mm:removeParticleEmitter(ps);event.removed_map_particles=event.removed_map_particles+1 end
 mm._checker_removed_light_events[#mm._checker_removed_light_events+1]=event
end
local function relight()
 local m=game.level.map;local c=m._checker_measure_light;if not c then return end
 local tint=m._checker_measure_tint or 1;m:setShown(tint,tint,tint,1);m:setObscure(.6,.6,.6,.5)
 for dx=-5,5 do for dy=-5,5 do local x,y=c.x+dx,c.y+dy
  if x>=0 and y>=0 and x<m.w and y<m.h then
   m.lites(x,y,true);m.remembers(x,y,true);m:applyLite(x,y,1)
  end
 end end
end
if not p._checker_original_measure_fov then
 p._checker_original_measure_fov=p.playerFOV
 p.playerFOV=function(self,...)
  self._checker_original_measure_fov(self,...);relight()
 end
end
relight();mm:redisplay();core.display.forceRedraw()
return true
"""


def standee_lighting_state(bridge, name, set_state=False, profile="LIGHTING_REFERENCE"):
    q = json.dumps(name, ensure_ascii=False)
    if set_state:
        tint = AURA_CONTRACT[profile]['shown'][0]
        bridge.lua(f'game.level.map._checker_measure_tint={tint};' + STANDEE_LIGHTING_LUA.replace('NAME', q))
    return bridge.lua(
        f"local a=assert(mb.byName({q}));local p=game.player;local m=game.level.map;"
        "local cells={};for dx=-5,5 do for dy=-5,5 do local x,y=a.x+dx,a.y+dy;"
        "local g=m(x,y,m.TERRAIN);cells[#cells+1]={x=x,y=y,lit=m.lites(x,y) or false,"
        "remembered=m.remembers(x,y) or false,seen=m.seens(x,y) or false,"
        "terrain=g and g.name or false,image=g and g.image or false,"
        "block_sight=g and g.block_sight or false} end end;"
        "local lights={};for _,e in pairs(game.level.entities) do if e.x and "
        "((e.lite or 0)>0 or (e.radiance_aura or 0)>0) then lights[#lights+1]={"
        "name=e.name,x=e.x,y=e.y,lite=e.lite or 0,radiance=e.radiance_aura or 0} end end;"
        "local fx=a.x-2;local fy=a.y-2;if (fx+fy)%2~=0 then fx=fx-1 end;"
        "local g=m(fx,fy,m.TERRAIN);local sx=m.display_x+(fx-m.mx)*m.tile_w;"
        "local sy=m.display_y+(fy-m.my)*m.tile_h;"
        "local effects={};for id in pairs(p.tmp or {}) do effects[#effects+1]=tostring(id) end;"
        "return {player_lite=p.lite,sight=p.sight,infravision=p.infravision or false,"
        "blind=p.blind or false,player_effects=effects,shown=m.color_shown,obscure=m.color_obscure,"
        "daynight=config.settings.tome.daynight,smooth_fov=config.settings.tome.smooth_fov,"
        "level_daynight=game.level.data.day_night or false,turn=game.turn,"
        "time={game.calendar:getTimeOfDay(game.turn)},lighting_entities=lights,cells=cells,"
        "native_environment={thunderstorm=game.zone.thunderstorm_event_levels and "
        "game.zone.thunderstorm_event_levels[game.level.level] or false,level_effects=game.level.effects or {},"
        "background=game.level.data.background and true or false,weather_shader=game.level.data.weather_shader and true or false},"
        "removed_light_events=m._checker_removed_light_events or {},"
        "map_origin={m.mx,m.my},floor_world={fx,fy},floor_box={sx,sy,sx+m.tile_w,sy+m.tile_h},"
        "bare_floor=g and g.name=='burnt ground' and not m(fx,fy,m.ACTOR) "
        "and not m(fx,fy,m.OBJECT) and not m(fx,fy,m.TRAP) and true or false}")


def standee_floor_measure(paths, states, prefix, profile="LIGHTING_REFERENCE", samples=3):
    from PIL import Image
    import numpy as np
    values, crops = [], []
    for k, (path, state) in enumerate(zip(paths, states), 1):
        patch = Image.open(path).convert('RGB').crop(state['floor_box'])
        dest = CROPS / f'{prefix}-floor-{k}.png'
        dest.parent.mkdir(parents=True, exist_ok=True);patch.save(dest)
        values.append(float(np.asarray(patch).mean()));crops.append(rel(dest))
    result = lighting_validity(values, all(st['bare_floor'] for st in states),
                               AURA_CONTRACT[profile], samples=samples)
    result.update(crops=crops, states=states)
    return result


def standee_clear_around_logged(bridge, radius):
    return bridge.lua(
        f"local p=game.player;local removed={{}};for _,e in pairs(game.level.entities) do "
        f"if e~=p and e.x and math.abs(e.x-p.x)<={radius} and math.abs(e.y-p.y)<={radius} then "
        "removed[#removed+1]={name=e.name,x=e.x,y=e.y,lite=e.lite or 0,radiance=e.radiance_aura or 0} end end;"
        f"local n=mb.clearAround({radius});return {{n=n,entities=removed}}")


def aura_height_gate_required(effect, tile):
    """2026-10-05 approved option 2: essence height is judged only at 64px.

    Independent design review (2026-10-04): at alpha .6 the near-black tip
    and .24-.34-cell core reach are not resolvable at 32/48px. Band, ratio,
    stillness, median and k remain unchanged; body_of_fire uses every size.
    """
    return effect != 'essence_of_the_dead' or tile == 64


# Native aura-producing definitions contain this API in their activation
# bytecode. Inspect active definitions uniformly; never delete shader tables or
# deactivate unrelated buffs. Native deactivation owns all lifecycle cleanup.
STANDEE_ISOLATE_SHADER_AURAS_LUA = r"""
local function keys(a)
 local out={};for k in pairs(a.shader_auras or {}) do out[#out+1]=k end
 table.sort(out);return out
end
local function attaches(d)
 if not d or type(d.activate)~='function' then return false end
 local ok,code=pcall(string.dump,d.activate)
 return ok and code:find('addShaderAura',1,true)~=nil
end
local rows={}
for _,a in pairs(game.level.entities) do
 local row={actor=a.name,uid=a.uid,before=keys(a),removed={},lite_before=a.lite or 0,radiance_before=a.radiance_aura or 0}
 if #row.before>0 then
  local effects={};for id in pairs(a.tmp or {}) do effects[#effects+1]=id end
  local sustains={};for id in pairs(a.sustain_talents or {}) do sustains[#sustains+1]=id end
  for _,id in ipairs(effects) do
   local def=a:getEffectFromId(id)
   if attaches(def) then
    local before=keys(a);local ok,err=pcall(function() a:removeEffect(id) end)
    row.removed[#row.removed+1]={kind='effect',id=id,name=def.name,before=before,after=keys(a),ok=ok,error=not ok and tostring(err) or false}
   end
  end
  for _,id in ipairs(sustains) do
   local def=a:getTalentFromId(id)
   if a:isTalentActive(id) and attaches(def) then
    local before=keys(a);local ok,err=pcall(function()
     a:forceUseTalent(id,{ignore_energy=true,ignore_cd=true,no_equilibrium_fail=true,no_talent_fail=true,silent=true})
    end)
    row.removed[#row.removed+1]={kind='sustain',id=id,name=def.name,before=before,after=keys(a),ok=ok,error=not ok and tostring(err) or false}
   end
  end
 end
 row.after=keys(a);row.lite_after=a.lite or 0;row.radiance_after=a.radiance_aura or 0;rows[#rows+1]=row
end
return rows
"""


def standee_isolate_shader_auras(bridge):
    """Detach pre-existing aura effects/sustains via their native removal API."""
    return bridge.lua(STANDEE_ISOLATE_SHADER_AURAS_LUA)


def standee_idle_particle_count(bridge):
    return bridge.lua("local n=0;for _,a in pairs(game.level.entities) do "
                      "for _ in pairs(a.__particles or {}) do n=n+1 end end;return n")


def aura_screen_quad(sx, sy, tile, quad):
    return [sx + quad.get('display_x', 0) * tile,
            sy + quad.get('display_y', -1) * tile,
            sx + (quad.get('display_x', 0) + quad.get('display_w', 1)) * tile,
            sy + (quad.get('display_y', -1) + quad.get('display_h', 2)) * tile]


def standee_freeze(bridge):
    """Freeze idle animation and strip idle particles/shader auras so the only
    variable between the flag-off and flag-on frame is the token draw path.
    The phoenix flame A/B keeps its aura because that scene does not freeze."""
    bridge.lua(
        "core.display.pauseAnims(true);"
        "for _,a in pairs(game.level.entities) do if a.__particles then local rem={};"
        "for e in pairs(a.__particles) do rem[#rem+1]=e end;"
        "for _,e in ipairs(rem) do pcall(function() a:removeParticles(e) end) end end end;"
        "local function strip(t) if not t then return end for i=#(t.add_mos or {}),1,-1 do "
        "local m=t.add_mos[i];if type(m)=='table' and m._isshaderaura then table.remove(t.add_mos,i) end end end;"
        "for _,a in pairs(game.level.entities) do a.shader=nil;a.shader_args=nil;a.shader_auras=nil;strip(a);strip(a.replace_display) end;"
        "mb.refresh();return true")


def standee_open_scene(bridge, entry, tiles):
    """Isolate every actor and freeze native scene animation for exact A/B.

    Native API removal owns particle/effect lifecycle. The animation pause also
    holds terrain shader tick fixed, so a corner overhang cannot confound the
    whole-crop exactly-zero 16px fallback gate. No pixels are excluded.
    """
    # Coordinator-approved open/flat isolation, following standee_freeze:
    # CheckerTokens/CheckerTokenStyle have no time-based drawing; rings/arcs
    # are static. Realaura and facing captures must remain unpaused.
    bridge.lua('core.display.pauseAnims(true);return true')
    try:
        entry['scene_isolation'] = {
            'shader_aura_removals': standee_isolate_shader_auras(bridge),
            'particle_removals': standee_remove_idle_particles(bridge, 'ogre guard'),
            'residual_particles': standee_idle_particle_count(bridge),
            'animations_paused': True,
        }
        standee_off_on(bridge, entry, 'open', tiles, 'standee-open',
                       native=True, up=2, down=1, span=2)
        standee_per_actor(bridge, entry, 'standee-open',
                          ['ogre guard', 'Ninandra, the Great Weaver'], tile=32)
    finally:
        bridge.lua('core.display.pauseAnims(false);return true')


def standee_off_on(bridge, entry, label, tiles, prefix, focus='mb.focus(game.player.x,game.player.y)',
                   up=2, down=1, span=1, native=False, freeze=False):
    """Capture flag-off/flag-on at each tile, plus a tokens-off native frame at
    every tile when `native` is set. Crops are regions only; full screenshots
    are removed."""
    from PIL import Image, ImageChops
    shots = []
    if freeze:
        standee_freeze(bridge)
    for t in tiles:
        bridge.lua("local T=require 'mod.class.CheckerTokens';T.layer_trial=false;T.standee_trial=false;"
                   f"mb.setTile({t});game:checkerRefreshVisuals();{focus};return true")
        p_off = bridge.shot(f'{prefix}-off-{label}-{t}')
        bridge.lua("local T=require 'mod.class.CheckerTokens';T.layer_trial=false;T.standee_trial=true;"
                   f"mb.setTile({t});game:checkerRefreshVisuals();{focus};return true")
        p_on = bridge.shot(f'{prefix}-on-{label}-{t}')
        state = standee_state(bridge)
        box = standee_region(bridge, t, up, down, span)
        CROPS.mkdir(parents=True, exist_ok=True)
        c_off = CROPS / f'{prefix}-off-{label}-{t}-crop.png'
        c_on = CROPS / f'{prefix}-on-{label}-{t}-crop.png'
        a = Image.open(p_off).convert('RGB').crop(box)
        b = Image.open(p_on).convert('RGB').crop(box)
        a.save(c_off); b.save(c_on)
        diff = ImageChops.difference(a, b)
        changed = diff.getbbox() is not None
        changed_px = sum(1 for px in diff.getdata() if px != (0, 0, 0))
        item = {'tile': t, 'region': list(box), 'off': rel(c_off), 'on': rel(c_on),
                'changed': changed, 'changed_pixels': changed_px, 'state': state}
        if native:
            bridge.lua("local T=require 'mod.class.CheckerTokens';T.standee_trial=false;T.layer_trial=false;"
                       f"mb.tokens(false);mb.setTile({t});{focus};return true")
            p_nat = bridge.shot(f'{prefix}-native-{label}-{t}')
            c_nat = CROPS / f'{prefix}-native-{label}-{t}-crop.png'
            Image.open(p_nat).convert('RGB').crop(box).save(c_nat)
            item['native'] = rel(c_nat)
            bridge.lua("local T=require 'mod.class.CheckerTokens';T.standee_trial=true;T.layer_trial=false;"
                       "mb.tokens(true);mb.refresh();return true")
            Path(p_nat).unlink(missing_ok=True)
        shots.append(item)
        Path(p_off).unlink(missing_ok=True)
        Path(p_on).unlink(missing_ok=True)
    if freeze:
        bridge.lua('core.display.pauseAnims(false);return true')
    bridge.lua('mb.setTile(64)')
    entry.setdefault('captures', []).extend(shots)
    return shots


def standee_per_actor(bridge, entry, label, names, tile=48, up=2, down=1, span=1):
    """Crops centred on one actor's own cell, the SAME window for OFF, ON and
    tokens-off NATIVE: 3 cells wide (span=1) x 4 cells tall (up=2, down=1).

    R33's version spanned the whole packed crowd (span=2) and had no native
    frame, so every per-actor ON crop covered the same scene. This re-focuses on
    the single actor before each shot and re-uses one box for all three."""
    from PIL import Image
    bridge.lua('core.display.pauseAnims(true);return true')
    focus = ('local a=mb.byName(%s);if not a then return {found=false} end;'
             'mb.focus(a.x,a.y);local m=game.level.map;'
             'local r=mb.row(a);r.found=true;'
             'r.screen2={math.floor(m.display_x+(a.x-m.mx)*m.tile_w),'
             'math.floor(m.display_y+(a.y-m.my)*m.tile_h)};return r')
    for name in names:
        q = json.dumps(name, ensure_ascii=False)
        off = bridge.lua(f"local T=require 'mod.class.CheckerTokens';T.layer_trial=false;T.standee_trial=false;"
                         f"mb.setTile({tile});game:checkerRefreshVisuals();" + (focus % q))
        if not off.get('found'):
            entry.setdefault('per_actor', []).append({'name': name, 'found': False})
            continue
        p_off = bridge.shot(f'{label}-{EXPECT.get(name) or name}-off')
        bridge.lua("local T=require 'mod.class.CheckerTokens';T.standee_trial=true;"
                   f"mb.setTile({tile});game:checkerRefreshVisuals();" + (focus % q))
        p_on = bridge.shot(f'{label}-{EXPECT.get(name) or name}-on')
        # Size/cap/drawn height are read while the standee is installed (ON).
        metrics = standee_actor_metrics(bridge, name)
        # tokens-off NATIVE frame, same focused window as OFF/ON.
        bridge.lua("local T=require 'mod.class.CheckerTokens';T.standee_trial=false;T.layer_trial=false;"
                   f"mb.tokens(false);mb.setTile({tile});game:checkerRefreshVisuals();" + (focus % q))
        p_nat = bridge.shot(f'{label}-{EXPECT.get(name) or name}-native')
        bridge.lua("local T=require 'mod.class.CheckerTokens';T.standee_trial=true;T.layer_trial=false;"
                   "mb.tokens(true);mb.refresh();return true")
        sx, sy, tt = off['screen2'][0], off['screen2'][1], tile
        box = clamp_box((sx - span * tt, sy - up * tt, sx + (span + 1) * tt, sy + (down + 1) * tt))
        CROPS.mkdir(parents=True, exist_ok=True)
        tag = EXPECT.get(name) or name
        c_off = CROPS / f'{label}-{tag}-off-crop.png'
        c_on = CROPS / f'{label}-{tag}-on-crop.png'
        c_nat = CROPS / f'{label}-{tag}-native-crop.png'
        Image.open(p_off).convert('RGB').crop(box).save(c_off)
        Image.open(p_on).convert('RGB').crop(box).save(c_on)
        Image.open(p_nat).convert('RGB').crop(box).save(c_nat)
        entry.setdefault('per_actor', []).append({'name': name, 'id': EXPECT.get(name), 'found': True,
                                                  'label': label, 'tile': tile,
                                                  'region': list(box), 'off': rel(c_off), 'on': rel(c_on),
                                                  'native': rel(c_nat),
                                                  'size_category': metrics.get('size_category'),
                                                  'height_cap': metrics.get('height_cap'),
                                                  'drawn_cells': metrics.get('drawn_cells'),
                                                  'has_box': metrics.get('has_box')})
        for p in (p_off, p_on, p_nat):
            Path(p).unlink(missing_ok=True)
    # Restore the standee flag for any later step.
    bridge.lua("local T=require 'mod.class.CheckerTokens';T.layer_trial=false;T.standee_trial=true;"
               "game:checkerRefreshVisuals();core.display.pauseAnims(false);return true")


def diff_pixels(a, b, box, threshold=12):
    """Count pixels that differ between two frames inside one box.

    The R41 method: the aura count is the DIFFERENCE between the same frame
    with and without the aura, so the faction ring, the creature's colours,
    clothes and the floor cannot pollute it. ``threshold`` rejects sub-pixel
    antialias noise. Contrast with R40's single bright-warm mask, which
    over-counted red creatures/flames and under-counted a dark aura.
    """
    from PIL import Image
    import numpy as np
    ia = np.asarray(Image.open(a).convert('RGB').crop(box)).astype(int)
    ib = np.asarray(Image.open(b).convert('RGB').crop(box)).astype(int)
    return int((np.abs(ia - ib).sum(axis=2) > threshold).sum())


def _diff_mask(a, b, box, threshold=12):
    """Boolean changed-pixel mask between two frames inside one box.

    R43 uses it to subtract the aura's own pixels before measuring creature
    stillness and to locate the aura pixel centroid and the creature bbox
    centre for the native-facing mirror.
    """
    from PIL import Image
    import numpy as np
    ia = np.asarray(Image.open(a).convert('RGB').crop(box)).astype(int)
    ib = np.asarray(Image.open(b).convert('RGB').crop(box)).astype(int)
    return np.abs(ia - ib).sum(axis=2) > threshold


def _centroid(mask):
    """(x, y) centroid of a boolean mask in crop coordinates, or None."""
    import numpy as np
    ys, xs = np.where(mask)
    if not len(xs):
        return None
    return float(xs.mean()), float(ys.mean())


def _median(values):
    ordered = sorted(values)
    return ordered[len(ordered) // 2]


def standee_aura_state(bridge, name):
    q = json.dumps(name, ensure_ascii=False)
    return bridge.lua(
        ("local a=mb.byName(%s);local s=a._checker_token;local t=a.replace_display or a;"
         "local au={};for _,m in ipairs(t.add_mos or {}) do if m._isshaderaura then "
         "au[#au+1]={image=m.image,display_x=m.display_x,display_y=m.display_y,display_w=m.display_w,"
         "display_h=m.display_h,sdm=m.sdm_double,mark=m._checker_standee_aura and true or false,"
         "base=m._checker_standee_base and true or false} end end;"
         "return {standee=(s and s.standee) and true or false,aura=au}") % q)


# The two REAL native shader auras used by the standee aura scene. R41 passed
# the TALENT id ('T_BODY_OF_FIRE') into a function that tested the label
# 'body_of_fire', so the else branch ran and every "body_of_fire" capture really
# applied EFF_ESSENCE_OF_THE_DEAD. The label is the caller's request; `applied`
# is read back from the actor so a mislabel can never pass.
AURA_EFFECTS = ('body_of_fire', 'essence_of_the_dead')

# R49 user decision: apply the 0.3-cell floor to EVERY native reference,
# k = max(0.3, 0.6 * native flame height), with solid flame rows only.
AURA_CONTRACT = json.loads((ADDON / 'tools/standee_aura_contract.json').read_text())
AURA_FLAME_ABOVE_TOP_FLOOR_CELLS = AURA_CONTRACT['AURA_FLAME_ABOVE_TOP_FLOOR_CELLS']
AURA_HEIGHT_FRAMES = AURA_CONTRACT['AURA_HEIGHT_FRAMES']


def aura_height_gate(on_rows, native_rows, on_art_top, native_art_top, tile):
    """Uniform pre-registered height sample; k and solid-top detector unchanged."""
    if len(on_rows) != AURA_HEIGHT_FRAMES or len(native_rows) != AURA_HEIGHT_FRAMES:
        raise ValueError(f'aura height requires exactly {AURA_HEIGHT_FRAMES} frames per state')
    # A missing solid band contributes zero height, never a dropped sample:
    # both medians must retain all 15 pre-registered frames.
    on_height = _median([0.0 if row is None else (on_art_top - row) / tile
                         for row in on_rows])
    native_height = _median([0.0 if row is None else (native_art_top - row) / tile
                             for row in native_rows])
    k = max(AURA_FLAME_ABOVE_TOP_FLOOR_CELLS, 0.6 * native_height)
    return {'pass': on_height >= k, 'on_cells': on_height,
            'native_cells': native_height, 'k': k}


def aura_non_height_frames(files):
    """Band and creature-still retain frames 1–3; ratio and height use all 15."""
    if len(files) != AURA_HEIGHT_FRAMES:
        raise ValueError(f'aura capture requires {AURA_HEIGHT_FRAMES} frames')
    return files[:3]



def aura_ratio_gate(on_counts, native_counts, reach_ratio):
    """R52 approved: strict, uniform 15-frame whole-region medians."""
    import math
    for counts in (on_counts, native_counts):
        if len(counts) != AURA_HEIGHT_FRAMES or any(
                c is None or not isinstance(c, (int, float)) or not math.isfinite(c) or c < 0
                for c in counts):
            raise ValueError('aura ratio requires exactly 15 valid counts per state')
    on, native = _median(on_counts), _median(native_counts)
    raw = on / native if native else 0.0
    normalised = raw / reach_ratio if reach_ratio else 0.0
    return {'on_median': on, 'native_median': native, 'ratio': raw,
            'normalised': normalised,
            'pass': bool(reach_ratio) and on > 0 and native > 0 and 0.6 <= normalised <= 1.5}


def mirror_mask_axis(mask, axis):
    """Mirror pixel centres about the same continuous body axis as runtime."""
    import numpy as np
    out = np.zeros_like(mask)
    if axis is not None:
        for x in range(mask.shape[1]):
            dx = int(round(2 * axis - 1 - x))
            if 0 <= dx < mask.shape[1]:
                out[:, dx] |= mask[:, x]
    return out


def aura_mirror_gain(left, right, axis):
    """Unchanged asymmetric-region gain, after caller excludes tactical boxes."""
    flipped = mirror_mask_axis(left, axis)
    asym = left ^ flipped
    count = int(asym.sum())
    return ((int((right & flipped & asym).sum()) - int((right & left & asym).sum()))
            / count) if count else 0.0


def mirror_exclusion(shape, boxes, region, axis):
    """Exclude actual tactical boxes AND their mirrors, uniformly for all actors."""
    import numpy as np
    mask = np.zeros(shape, dtype=bool)
    for box in boxes:
        l, top, r, bottom = box['box']
        l, r = max(0, math.floor(l-region[0])), min(shape[1], math.ceil(r-region[0]))
        top, bottom = max(0, math.floor(top-region[1])), min(shape[0], math.ceil(bottom-region[1]))
        if r > l and bottom > top:
            mask[top:bottom, l:r] = True
    mask |= mirror_mask_axis(mask, axis)
    return mask, {'boxes': boxes, 'region': list(region), 'axis': axis,
                  'excluded_pixels': int(mask.sum()), 'includes_mirror_images': True}


def static_aura_asymmetry(tid):
    """Pre-registered alpha>8; body bbox centre mapped by exact aura affine."""
    import numpy as np
    from PIL import Image
    geometry = json.loads((ADDON/'art/token-layers/geometry.json').read_text())[tid]
    aura = geometry['aura']
    layer = geometry
    scale = (aura['right'] - aura['left']) / (layer['right'] - layer['left'])
    offset = aura['left'] - layer['left'] * scale
    axis = offset + (layer['left'] + layer['right']) / 2 * scale
    path = ADDON/'data/gfx/tokens-layer/aura'/f'{tid}.png'
    mask = np.asarray(Image.open(path))[:, :, 3] > 8
    occupied = int(mask.sum())
    asymmetric = int((mask ^ mirror_mask_axis(mask, axis)).sum())
    return {'id': tid, 'alpha_threshold': 8, 'axis': axis,
            'occupied_pixels': occupied, 'asymmetric_pixels': asymmetric,
            'static_asymmetry': asymmetric / occupied if occupied else 0.0}


def select_facing_subject(rows):
    """Pre-register highest new-actor asymmetry; below .30 is ineligible."""
    eligible = [row for row in rows if row['static_asymmetry'] >= 0.30]
    if not eligible:
        raise ValueError('no new facing candidate reaches static asymmetry 0.30')
    return max(eligible, key=lambda row: (row['static_asymmetry'], row['id']))


def facing_run_status(static_asymmetry, checks):
    """Below .30 is informative regardless of outcome; preserve raw checks."""
    if static_asymmetry < 0.30:
        return 'INFORMATIVE'
    return 'PASS' if all(checks.values()) else 'FAIL'


def assert_centred_mirror_region(frame, region):
    """Region-only flip requires equal horizontal crop margins."""
    left = region[0] - frame['region'][0]
    right = frame['region'][2] - region[2]
    if left != right:
        raise AssertionError(f'native mirror region has unequal margins: {left} != {right}')


def aura_mask_placement(mask, quad):
    """Half-open mask bbox contained by quad +/-1px, bottom anchored +/-1px."""
    import numpy as np
    ys, xs = np.where(mask)
    if not len(xs) or quad is None:
        return {'pass': False, 'bbox': None, 'quad': quad, 'bottom_error_px': None}
    bbox = [int(xs.min()), int(ys.min()), int(xs.max())+1, int(ys.max())+1]
    left, top, right, bottom = quad
    contained = bbox[0] >= left-1 and bbox[1] >= top-1 \
        and bbox[2] <= right+1 and bbox[3] <= bottom+1
    bottom_error = bbox[3] - bottom
    return {'pass': bool(contained and abs(bottom_error) <= 1), 'bbox': bbox,
            'quad': list(quad), 'contained': bool(contained),
            'bottom_error_px': float(bottom_error)}


def standee_apply_aura(bridge, name, effect, on):
    """Apply one REAL shader aura and read back which effect is active.

    effect is the label: 'body_of_fire' -> T_BODY_OF_FIRE (a talent),
    'essence_of_the_dead' -> EFF_ESSENCE_OF_THE_DEAD (an effect). Both use the
    native awesomeaura shader. The returned ``applied`` field is derived from
    the actor's live talent/effect state, not from the label, so the aura scene
    can assert the intended aura really is the one on the actor.
    """
    if effect not in AURA_EFFECTS:
        raise ValueError('unknown aura effect: %r' % (effect,))
    q = json.dumps(name, ensure_ascii=False)
    want = 1 if on else 0
    # Shared readback: which of the two auras is actually active right now.
    readback = (
        "local EFF=a.EFF_ESSENCE_OF_THE_DEAD or 'EFF_ESSENCE_OF_THE_DEAD';"
        "local bof=a:isTalentActive('T_BODY_OF_FIRE') and true or false;"
        "local eod=a:hasEffect(EFF) and true or false;"
        "local applied=bof and 'body_of_fire' or (eod and 'essence_of_the_dead' or false);"
        "local t=a.replace_display or a;local au=0;for _,m in ipairs(t.add_mos or {}) do if m._isshaderaura then au=au+1 end end;"
        "local n=0;for _ in pairs(a.shader_auras or {}) do n=n+1 end;")
    if effect == 'body_of_fire':
        body = (
            f"local a=mb.byName({q});"
            "if not a:knowTalent('T_BODY_OF_FIRE') then a:learnTalent('T_BODY_OF_FIRE',true,1) end;"
            "local active=a:isTalentActive('T_BODY_OF_FIRE');"
            f"if {want}==1 and not active then a:forceUseTalent('T_BODY_OF_FIRE',{{ignore_energy=true,ignore_cd=true,no_equilibrium_fail=true,no_talent_fail=true,silent=true}}) "
            f"elseif {want}==0 and active then a:forceUseTalent('T_BODY_OF_FIRE',{{ignore_energy=true,ignore_cd=true,no_equilibrium_fail=true,no_talent_fail=true,silent=true}}) end;"
            "pcall(function() a:updateModdableTile() end);mb.focus(a.x,a.y);"
            + readback +
            "return {active=bof,body_of_fire=bof,essence_of_the_dead=eod,applied=applied,shader_auras=n,aura_entries=au}")
    else:
        body = (
            f"local a=mb.byName({q});local EFF=a.EFF_ESSENCE_OF_THE_DEAD or 'EFF_ESSENCE_OF_THE_DEAD';"
            f"if {want}==1 then a:setEffect(EFF,50,{{}}) elseif a:hasEffect(EFF) then a:removeEffect(EFF) end;"
            "pcall(function() a:updateModdableTile() end);mb.focus(a.x,a.y);"
            + readback +
            "return {active=eod,body_of_fire=bof,essence_of_the_dead=eod,applied=applied,shader_auras=n,aura_entries=au}")
    return bridge.lua(body)


def standee_clear_auras(bridge, name):
    standee_apply_aura(bridge, name, 'body_of_fire', False)
    standee_apply_aura(bridge, name, 'essence_of_the_dead', False)


def standee_rank_check(bridge, entry):
    """Exercise aura-chain rank callbacks on a boss and a normal tall actor."""
    from PIL import Image
    import numpy as np
    records = []
    for name, index in (('Norgos, the Guardian', 29), ('heavy bone giant', 5)):
        entry.setdefault('placed', []).append(standee_place_one(bridge, 'standee', index))
        q = json.dumps(name)
        for tile in (32, 48, 64):
            for state in ('on', 'native'):
                enabled = 'true' if state == 'on' else 'false'
                bridge.lua("local T=require 'mod.class.CheckerTokens';T.layer_trial=false;"
                           f"T.standee_trial={enabled};mb.tokens({enabled});mb.setTile({tile});"
                           f"game:checkerRefreshVisuals();local a=mb.byName({q});mb.focus(a.x,a.y);"
                           "core.display.pauseAnims(false);return true")
                standee_clear_auras(bridge, name)
                removed = standee_remove_idle_particles(bridge, name)
                applied = standee_apply_aura(bridge, name, 'essence_of_the_dead', True)
                row = bridge.lua(f"local a=mb.byName({q});return mb.row(a)")
                sx, sy = row['screen'][:2]
                _set_vp(bridge.lua("local m=game.level.map;return {vp={m.display_x,m.display_y,m.viewport.width,m.viewport.height}}"))
                box = clamp_box((sx-tile, sy-2*tile, sx+2*tile, sy+2*tile))
                path = bridge.shot(f'rank-{index}-{state}-{tile}')
                crop_path = CROPS / f'rank-{EXPECT[name]}-{state}-{tile}-crop.png'
                CROPS.mkdir(parents=True, exist_ok=True)
                Image.open(path).convert('RGB').crop(box).save(crop_path)
                # Native boss front decoration occupies the strip just below
                # the own cell. Brown terrain and the adjacent player's skin
                # are excluded by its saturated orange colour.
                roi = (sx, sy+tile, sx+tile, sy+math.ceil(1.2*tile))
                a = np.asarray(Image.open(path).convert('RGB').crop(roi)).astype(int)
                orange = (a[:,:,0] >= 160) & (a[:,:,0] >= 1.6*a[:,:,1]) & (a[:,:,1] >= 1.3*a[:,:,2])
                records.append({'actor': name, 'id': EXPECT[name], 'rank': row['rank'],
                                'tile': tile, 'state': state, 'crop': rel(crop_path),
                                'region': list(box), 'ornament_region': list(roi),
                                'ornament_pixels': int(orange.sum()), 'applied': applied,
                                'particles_removed': removed, 'snap': standee_aura_state(bridge,name)})
                Path(path).unlink(missing_ok=True)
                standee_clear_auras(bridge, name)
        bridge.lua('mb.clearAround(12);return true')
    entry['rank_captures'] = records
    return records


def standee_forge_innate_diagnostic(bridge, entry):
    """DIAGNOSTIC ONLY: retain native Burning Wake, three ON/NATIVE frames."""
    from PIL import Image
    entry['placed'] = standee_place_one(bridge, 'standee', 20)
    captures = []
    for state in ('on', 'native'):
        enabled = 'true' if state == 'on' else 'false'
        bridge.lua("local T=require 'mod.class.CheckerTokens';T.layer_trial=false;"
                   f"T.standee_trial={enabled};mb.tokens({enabled});mb.setTile(48);"
                   "game:checkerRefreshVisuals();local a=mb.byName('forge-giant');"
                   "mb.focus(a.x,a.y);core.display.pauseAnims(false);return true")
        removed = standee_remove_idle_particles(bridge, 'forge-giant')
        active = bridge.lua("local a=mb.byName('forge-giant');return "
                            "{active=a:isTalentActive('T_BURNING_WAKE') and true or false, "
                            "burning_wake=(a.shader_auras or {}).burning_wake or false}")
        row = bridge.lua("return mb.row(mb.byName('forge-giant'))")
        sx, sy = row['screen'][:2]
        _set_vp(bridge.lua("local m=game.level.map;return {vp={m.display_x,m.display_y,m.viewport.width,m.viewport.height}}"))
        box = clamp_box((sx-48, sy-96, sx+96, sy+96))
        paths = []
        for frame in range(3):
            shot = bridge.shot(f'forge-innate-{state}-{frame+1}')
            path = CROPS / f'forge-innate-{state}-48-frame-{frame+1}-crop.png'
            Image.open(shot).convert('RGB').crop(box).save(path)
            paths.append(rel(path));Path(shot).unlink(missing_ok=True);time.sleep(.3)
        captures.append({'actor': 'forge-giant', 'state': state, 'tile': 48,
                         'diagnostic_only': True, 'active': active, 'region': list(box),
                         'row': row, 'snap': standee_aura_state(bridge, 'forge-giant'),
                         'particles_removed': removed, 'frame_crops': paths})
    entry['innate_diagnostic'] = captures
    return captures


def standee_realaura(bridge, entry, name, tiles=(32, 48, 64), frames=AURA_HEIGHT_FRAMES, up=2, down=1, span=1, lighting_profile="LIGHTING_REFERENCE"):
    """Measure each REAL shader aura SEPARATELY on one standee.

    One warm aura (T_BODY_OF_FIRE) and one cool/dark aura
    (EFF_ESSENCE_OF_THE_DEAD); both are native ``awesomeaura`` shader auras.
    Animations stay RUNNING: for each tile/state the actor is captured without
    the aura (the baseline), the effect is applied, and 15 height frames ~0.3s
    apart are captured. The aura count is the pixel DIFFERENCE against the
    baseline in the WHOLE region above the actor own-cell top, so floor/creature/faction colours
    cannot pollute it. The per-frame counts show the aura moving and the
    recorded actor screen shows the creature stays put. Replaces R40's single
    warm mask and total-pixel count.
    """
    from PIL import Image
    if frames != AURA_HEIGHT_FRAMES:
        raise ValueError(f'aura height requires {AURA_HEIGHT_FRAMES} frames')
    q = json.dumps(name, ensure_ascii=False)
    bridge.lua('core.display.pauseAnims(false);return true')
    shots = []
    for effect in ('body_of_fire', 'essence_of_the_dead'):
        for t in tiles:
            bridge.lua("local T=require 'mod.class.CheckerTokens';T.layer_trial=false;T.standee_trial=true;mb.tokens(true);"
                       f"mb.setTile({t});game:checkerRefreshVisuals();local a=mb.byName({q});mb.focus(a.x,a.y);return true")
            _set_vp(bridge.lua("local m=game.level.map;return {vp={m.display_x,m.display_y,m.viewport.width,m.viewport.height}}"))
            row = bridge.lua(f"local a=mb.byName({q});return mb.row(a)")
            sx, sy = row['screen'][0], row['screen'][1]
            box = clamp_box((sx - span * t, sy - up * t, sx + (span + 1) * t, sy + (down + 1) * t))
            upper = clamp_box((sx, sy - t, sx + t, sy))
            own = clamp_box((sx, sy, sx + t, sy + t))
            case_images = {}
            case_records = {}
            for state in ('on', 'native'):
                if state == 'on':
                    setup = "local T=require 'mod.class.CheckerTokens';T.layer_trial=false;T.standee_trial=true;mb.tokens(true);"
                else:
                    setup = "local T=require 'mod.class.CheckerTokens';T.layer_trial=false;T.standee_trial=false;mb.tokens(false);"
                bridge.lua(setup + f"mb.setTile({t});game:checkerRefreshVisuals();"
                           f"local a=mb.byName({q});mb.focus(a.x,a.y);return true")
                standee_clear_auras(bridge, name)
                bridge.lua(f"local a=mb.byName({q});mb.focus(a.x,a.y);return true")
                off_applied = standee_apply_aura(bridge, name, effect, False)
                shader_removed = standee_isolate_shader_auras(bridge)
                entry.setdefault('shader_aura_removals', []).append(
                    {'actor': name, 'effect': effect, 'tile': t, 'state': state, 'entities': shader_removed})
                removed = standee_remove_idle_particles(bridge, name)
                removed.update(actor=name, effect=effect, tile=t, state=state)
                entry.setdefault('particle_removals', []).append(removed)
                bases, residual, lighting_states = [], [], []
                standee_lighting_state(bridge, name, set_state=True, profile=lighting_profile)
                for k in range(3):
                    lighting_states.append(standee_lighting_state(bridge, name))
                    bases.append(bridge.shot(f'standee-aura-{effect}-{state}-{t}-base-{k + 1}'))
                    residual.append(standee_idle_particle_count(bridge))
                    time.sleep(0.3)
                import numpy as np
                baseline = cleaned_baseline_validity(
                    [np.asarray(Image.open(path).convert('RGB').crop(box)) for path in bases], residual)
                lighting = standee_floor_measure(bases, lighting_states,
                    f"standee-aura-{EXPECT.get(name, name.replace(' ', '-'))}-{effect}-{state}-{t}",
                    profile=lighting_profile)
                baseline['lighting'] = {k: value for k, value in lighting.items() if k != 'states'}
                baseline['valid'] = baseline['valid'] and lighting['valid']
                base = bases[0]
                applied = standee_apply_aura(bridge, name, effect, True)
                snap = standee_aura_state(bridge, name)
                if state == 'on':
                    quad = next(a for a in snap['aura'] if a.get('mark'))
                    score = clamp_box(aura_score_region(sx, sy, t, quad))
                # The three baselines already clear dialogs. Repeating that Lua
                # round trip per timed sample prevents the 0.3s cadence.
                height_files, capture_times, endpoint_states = [], [], []
                for k in range(frames):
                    if k in (0, frames - 1):
                        endpoint_states.append(standee_lighting_state(bridge, name))
                    started = time.monotonic()
                    height_files.append(bridge.shot(f'standee-aura-{effect}-{state}-{t}-{k + 1}', settle_s=0, clear_dialogs=False))
                    capture_times.append(started)
                    time.sleep(max(0, 0.3 - (time.monotonic() - started)))
                endpoint_lighting = standee_floor_measure(
                    [height_files[0], height_files[-1]], endpoint_states,
                    f"standee-aura-{EXPECT.get(name, name.replace(' ', '-'))}-{effect}-{state}-{t}-endpoints",
                    profile=lighting_profile, samples=2)
                endpoint_lighting['frame_indices'] = [1, frames]
                baseline['lighting_frames'] = {k: value for k, value in endpoint_lighting.items() if k != 'states'}
                baseline['valid'] = baseline['valid'] and endpoint_lighting['valid']
                files = aura_non_height_frames(height_files)
                upper_counts = [diff_pixels(base, p, upper) for p in files]
                whole_counts = [diff_pixels(base, p, score) for p in files]
                ratio_counts = [diff_pixels(base, p, score) for p in height_files]
                total_counts = [diff_pixels(base, p, box) for p in files]
                own_counts = [diff_pixels(base, p, own) for p in files]
                self_diffs = [diff_pixels(files[i], files[i + 1], upper) for i in range(len(files) - 1)]
                # R43 creature-still: the overlay creature is static, so what is
                # left of the consecutive-frame difference after subtracting the
                # aura's own pixels is movement/noise. The aura mask is the union
                # of the per-frame |ON - OFF| pixels over the whole body region
                # (the own cell plus the upper body cells); creature_move counts
                # only moving pixels outside it. The pass threshold is justified
                # by the recorded counts, not by a fraction of the area.
                body = clamp_box((sx, sy - up * t, sx + t, sy + t))
                aura_pixels = _diff_mask(base, files[0], body)
                for p in files[1:]:
                    aura_pixels = aura_pixels | _diff_mask(base, p, body)
                creature_move = []
                for i in range(len(files) - 1):
                    move = _diff_mask(files[i], files[i + 1], body)
                    creature_move.append(int((move & ~aura_pixels).sum()))
                creature_frames = [diff_pixels(files[i], files[i + 1], own) for i in range(len(files) - 1)]
                # R52 approved: height and ratio use all15; band/still use frames1–3.
                flame_top_rows = [_diff_top_row(base, p, box) for p in height_files]
                reach = standee_reach(EXPECT.get(name, name.replace(' ', '-')))
                art_top = (t * (reach['anchor_cells'] - reach['on_reach']) if state == 'on'
                           else t * (1 + reach['native_top_px'] / 64.0))
                band_widths = [max(flame_band_widths(_diff_mask(base, p, box))
                                   [:max(0, math.ceil(art_top))], default=0)
                               for p in files]
                screens = []
                for _ in range(3):
                    r = bridge.lua(f"local a=mb.byName({q});return mb.row(a)")
                    screens.append(r['screen'])
                CROPS.mkdir(parents=True, exist_ok=True)
                slug = EXPECT.get(name, name.replace(' ', '-'))
                c = CROPS / f'standee-aura-{slug}-{effect}-{state}-{t}-crop.png'
                Image.open(files[0]).convert('RGB').crop(box).save(c)
                frame_crops = []
                for frame, path in enumerate(height_files, 1):
                    frame_crop = CROPS / f'standee-aura-{slug}-{effect}-{state}-{t}-frame-{frame}-crop.png'
                    Image.open(path).convert('RGB').crop(box).save(frame_crop)
                    frame_crops.append(rel(frame_crop))
                baseline_crops = []
                for frame, path in enumerate(bases, 1):
                    bc = CROPS / f'standee-aura-{slug}-{effect}-{state}-{t}-base-frame-{frame}-crop.png'
                    Image.open(path).convert('RGB').crop(box).save(bc)
                    baseline_crops.append(rel(bc))
                Image.open(base).convert('RGB').crop(box).save(
                    CROPS / f'standee-aura-{slug}-{effect}-{state}-{t}-base-crop.png')
                shots.append({'tile': t, 'effect': effect, 'state': state, 'actor': name,
                              'region': list(box), 'upper': list(upper), 'body': list(body), 'crop': rel(c),
                              'frame_crops': frame_crops, 'particles_removed': removed,
                              'height_frames': AURA_HEIGHT_FRAMES, 'non_height_frame_indices': [1, 2, 3],
                              'capture_times': capture_times,
                              'intervals_s': [b-a for a,b in zip(capture_times,capture_times[1:])],
                              'baseline_crops': baseline_crops, 'baseline_validity': baseline,
                              'lighting': lighting, 'endpoint_lighting': endpoint_lighting,
                              'lighting_profile': lighting_profile,
                              'shader_aura_removals': shader_removed,
                              'upper_frames': upper_counts, 'whole_region': list(score),
                              'whole_frames': whole_counts, 'whole_ratio_frames': ratio_counts,
                              'ratio_frame_indices': list(range(1, 16)), 'total_frames': total_counts,
                              'own_frames': own_counts, 'self_diff': self_diffs,
                              'creature_frames': creature_frames, 'creature_move': creature_move,
                              'flame_top_rows': flame_top_rows, 'flame_band_widths': band_widths,
                              'flame_band_min_px': AURA_FLAME_BAND_MIN_PX,
                              'aura_pixels': int(aura_pixels.sum()),
                              'body_area': (body[2] - body[0]) * (body[3] - body[1]),
                              'creature_area': (own[2] - own[0]) * (own[3] - own[1]),
                              'actor_screen': screens, 'applied': applied,
                              'off_applied': off_applied,
                              'snap': snap})
                case_images[state] = (bases, height_files)
                case_records[state] = shots[-1]
            on_quad = next(a for a in case_records['on']['snap']['aura'] if a.get('mark'))
            native_quad = next(a for a in case_records['native']['snap']['aura']
                               if not a.get('base') and not a.get('mark'))
            screen_quads = [aura_screen_quad(sx, sy, t, q) for q in (on_quad, native_quad)]
            # Diagnostic only: actor crop is clipped to the map viewport,
            # excluding the combat log. Legitimate effect output may spill.
            local_quads = [[l-box[0], top-box[1], r-box[0], b-box[1]]
                           for l, top, r, b in screen_quads]
            for state, (bases, files) in case_images.items():
                outside = [outside_quad_pixels(_diff_mask(bases[0], path, box), local_quads)
                           for path in files]
                case_records[state]['screen_quads'] = screen_quads
                case_records[state]['outside_quad_pixels'] = outside
                case_records[state]['outside_quad_region'] = list(box)
                case_records[state]['validity'] = 'VALID' if case_records[state]['baseline_validity']['valid'] else 'INVALID'
                for path in bases + files:
                    Path(path).unlink(missing_ok=True)
            standee_clear_auras(bridge, name)
    bridge.lua("local T=require 'mod.class.CheckerTokens';T.standee_trial=true;T.layer_trial=false;"
               "mb.tokens(true);mb.refresh();return true")
    bridge.lua('mb.setTile(64)')
    entry.setdefault('aura_captures', []).extend(shots)
    return shots


def standee_sequential(bridge, entry, name, tile=48, pause=0.6, frames=3):
    """Two real auras added one after another with no refresh/toggle between.

    Native updateModdableTilePrepare only inserts aura add_mos when the display
    add_mos is nil; a token keeps its add_mos after the first aura, so a second
    aura (and removing one of two) used to be dropped. Apply two lasting timed
    auras A and B, let a turn pass between them, then remove A: every stage must
    be visible.
    """
    from PIL import Image
    q = json.dumps(name, ensure_ascii=False)
    bridge.lua("local T=require 'mod.class.CheckerTokens';T.layer_trial=false;T.standee_trial=true;mb.tokens(true);"
               f"mb.setTile({tile});game:checkerRefreshVisuals();local a=mb.byName({q});mb.focus(a.x,a.y);return true")
    standee_clear_auras(bridge, name)
    row = bridge.lua(f"local a=mb.byName({q});return mb.row(a)")
    sx, sy = row['screen'][0], row['screen'][1]
    box = clamp_box((sx - tile, sy - 2 * tile, sx + 2 * tile, sy + 2 * tile))
    shots = []

    def stage(tag):
        state = bridge.lua(
            "local a=mb.byName(%s);local t=a.replace_display or a;"
            "local au={};for _,m in ipairs(t.add_mos or {}) do if m._isshaderaura then au[#au+1]=m.image end end;"
            "local kinds={};for k in pairs(a.shader_auras or {}) do kinds[#kinds+1]=tostring(k) end;table.sort(kinds);"
            "return {aura=au,kinds=kinds,entries=#au}" % q)
        files = []
        for k in range(frames):
            files.append(bridge.shot(f'standee-seq-{tag}-{k + 1}'))
            time.sleep(0.3)
        counts = [diff_pixels(files[i], files[i + 1], box) for i in range(len(files) - 1)]
        CROPS.mkdir(parents=True, exist_ok=True)
        c = CROPS / f'standee-seq-{tag}-crop.png'
        Image.open(files[0]).convert('RGB').crop(box).save(c)
        frame_crops = []
        for frame, path in enumerate(files, 1):
            frame_crop = CROPS / f'standee-seq-{tag}-frame-{frame}-crop.png'
            Image.open(path).convert('RGB').crop(box).save(frame_crop)
            frame_crops.append(rel(frame_crop))
        for p in files:
            Path(p).unlink(missing_ok=True)
        shots.append({'stage': tag, 'region': list(box), 'crop': rel(c), 'state': state,
                      'frame_crops': frame_crops,
                      'frame_diff': counts})

    def apply_effect(effect, on):
        want = 1 if on else 0
        return bridge.lua(
            f"local a=mb.byName({q});local E=a[{json.dumps(effect)}] or {json.dumps(effect)};"
            f"if {want}==1 then a:setEffect(E,60,{{}}) elseif a:hasEffect(E) then a:removeEffect(E) end;"
            "pcall(function() a:updateModdableTile() end);mb.focus(a.x,a.y);"
            "local t=a.replace_display or a;local au=0;for _,m in ipairs(t.add_mos or {}) do if m._isshaderaura then au=au+1 end end;"
            "local n=0;for _ in pairs(a.shader_auras or {}) do n=n+1 end;"
            "return {active=a:hasEffect(E) and true or false,shader_auras=n,aura_entries=au}")

    apply_effect('EFF_ICE_ARMOUR', False)
    apply_effect('EFF_ESSENCE_OF_THE_DEAD', False)
    a1 = apply_effect('EFF_ICE_ARMOUR', True)
    stage('a')
    # "Wait a turn": let the engine tick without any checker refresh/toggle.
    bridge.lua("if game.player then game.player:useEnergy() end;return true")
    time.sleep(pause)
    a2 = apply_effect('EFF_ESSENCE_OF_THE_DEAD', True)
    stage('ab')
    rem = apply_effect('EFF_ICE_ARMOUR', False)
    stage('b')
    entry['sequential'] = {'first': a1, 'second': a2, 'after_remove_a': rem, 'shots': shots}
    apply_effect('EFF_ICE_ARMOUR', False)
    apply_effect('EFF_ESSENCE_OF_THE_DEAD', False)
    bridge.lua('mb.setTile(64)')
    return entry['sequential']


def standee_facing(bridge, entry, name, tile=48):
    """Native facing draws ONE creature and mirrors the creature.

    Animations stay RUNNING: R41 paused them, which made the "mirror" check a
    frozen-frame tautology. The aura is left OFF for the pixel pass because the
    creature layer is static: in fixed facing both directions must be identical,
    and in native facing the left crop horizontally flipped must match the right
    crop. The base-redraw/aura state is read in a separate pass with the aura
    applied, so no aura animation pollutes the mirror comparison.
    """
    from PIL import Image
    q = json.dumps(name, ensure_ascii=False)
    # R48: two facing scenes (heavy bone giant + ogre guard) share this CROPS
    # directory, so the kept crops carry the actor slug; otherwise the second
    # scene overwrites the first and the verifier reads one actor twice.
    slug = EXPECT.get(name, name.replace(' ', '-'))
    bridge.lua("local T=require 'mod.class.CheckerTokens';T.layer_trial=false;T.standee_trial=true;mb.tokens(true);"
               f"mb.setTile({tile});game:checkerRefreshVisuals();local a=mb.byName({q});mb.focus(a.x,a.y);"
               "core.display.pauseAnims(false);return true")
    standee_clear_auras(bridge, name)
    entry['facing_shader_aura_removals'] = standee_isolate_shader_auras(bridge)
    entry['facing_idle_particles_removed'] = standee_remove_idle_particles(bridge, name)
    standee_lighting_state(bridge, name, set_state=True)
    row = bridge.lua(f"local a=mb.byName({q});return mb.row(a)")
    sx, sy = row['screen'][0], row['screen'][1]
    box = clamp_box((sx - tile, sy - 2 * tile, sx + 2 * tile, sy + 2 * tile))
    # The standee itself: one cell wide, the two cells above plus the own cell.
    # This excludes the player token in the cell below, so the comparison is the
    # creature's mirror and not another actor's pixels.
    creature = clamp_box((sx, sy - 2 * tile, sx + tile, sy + tile))
    own = clamp_box((sx, sy, sx + tile, sy + tile))
    upper = clamp_box((sx, sy - 2 * tile, sx + tile, sy))
    state_q = (
        "local a=mb.byName(%s);local s=a._checker_token;local t=a.replace_display or a;"
        "local aura={};local base_invis=false;"
        "for _,m in ipairs(t.add_mos or {}) do if m._isshaderaura then "
        "if m._checker_standee_base then base_invis=(m.image=='invis.png') end;"
        "aura[#aura+1]={image=m.image,mark=m._checker_standee_aura and true or false,"
        "base=m._checker_standee_base and true or false} end end;"
        "local S=require 'mod.class.CheckerTokenStyle';local mm=game.level.map;local cc=false;"
        "local box=s and s.layer_box;local cap=s and S.standeeHeight(s.id);"
        "if box and cap then local cell=mm.tile_w;local dd=cell*S.token_diameter;"
        "local ql,qt,qs=S.standeeQuad(cell,box,box.canvas or 256,cell/2,cell/2,dd,cap);"
        "local sc=qs/(box.canvas or 256);"
        "cc={x=mm.display_x+(a.x-mm.mx)*cell+ql+((box.left+box.right)/2)*sc,"
        "y=mm.display_y+(a.y-mm.my)*cell+qt+((box.top+box.bottom)/2)*sc} end;"
        "local aq=false;local ab=s and s.layer_aura;if ab and cap then "
        "local dx,dy,w,h=S.standeeAuraQuad(ab,ab.canvas_w or ab.canvas or 256,ab.canvas_h or ab.canvas or 256,cap);"
        "if dx then local cell=mm.tile_w;local sx=mm.display_x+(a.x-mm.mx)*cell;local sy=mm.display_y+(a.y-mm.my)*cell;"
        "aq={sx+dx*cell,sy+dy*cell,sx+(dx+w)*cell,sy+(dy+h)*cell} end end;"
        "local cell=mm.tile_w;local sx=mm.display_x+(a.x-mm.mx)*cell;local sy=mm.display_y+(a.y-mm.my)*cell;"
        "local oc={};local function rect(kind,x,y,w,h) oc[#oc+1]={kind=kind,box={x,y,x+w,y+h}} end;"
        "local g=S.geometry(sx,sy,cell,(s and s.scale) or 1);if S.rankBadge(a.rank) then "
        "local w,h=S.badgeSize(g.cell);rect('rank-badge',sx+g.cell-w,sy+1,w,h) end;"
        "local mode=S.nativeBarMode(mm);local b=S.native_life_bar;"
        "if mode=='small-side' then local v=mm.actor_player;local friend=v and v:reactionToward(a);"
        "local x=friend and friend<0 and b.small_side.enemy_sx or b.small_side.sx;local q=b.small_side;"
        "rect('life-bar',sx+cell*x,sy+cell*q.sy,cell*(q.dx-q.sx),cell*(q.dy-q.sy)) "
        "elseif mode=='small-bottom' then local q=b.small_bottom;"
        "rect('life-bar',sx+cell*q.sx,sy+cell*q.sy,cell*(q.dx-q.sx),cell*(q.dy-q.sy)) "
        "elseif mode=='big-side' then rect('life-bar',sx+b.big.inset,sy+b.big.inset,cell*b.big.side_dw,cell-2*b.big.inset) "
        "elseif mode=='big-bottom' then rect('life-bar',sx+b.big.inset,sy+cell-cell*b.big.bottom_dh,cell-2*b.big.inset,cell*b.big.bottom_dh) end;"
        "return {body_flip=(s and s.body_flip) and true or false,standee=(s and s.standee) and true or false,"
        "overlay_active=(s and s.overlay_active) and true or false,_flipx=a._flipx and true or false,"
        "creature_bbox_centre=cc,aura_quad=aq,mirror_occluder_boxes=oc,"
        "base_invis=base_invis,aura=aura}") % q

    def set_direction(mode, flip):
        bridge.lua(f"config.settings.tome.checker_token_facing={json.dumps(mode)};"
                   f"local a=mb.byName({q});if a.MOflipX then a:MOflipX({'true' if flip else 'false'}) end;"
                   "game:checkerRefreshVisuals();mb.focus(a.x,a.y);return true")

    shots = []
    for mode in ('fixed', 'native'):
        for direction, flip in (('left', True), ('right', False)):
            set_direction(mode, flip)
            state = bridge.lua(state_q)
            files, light_states = [], []
            standee_lighting_state(bridge, name, set_state=True)
            for k in range(3):
                light_states.append(standee_lighting_state(bridge, name))
                files.append(bridge.shot(f'standee-facing-{mode}-{direction}-{k + 1}'))
                time.sleep(0.25)
            CROPS.mkdir(parents=True, exist_ok=True)
            c = CROPS / f'standee-facing-{slug}-{mode}-{direction}-crop.png'
            Image.open(files[1]).convert('RGB').crop(box).save(c)
            light = standee_floor_measure(files, light_states, f'standee-facing-{slug}-{mode}-{direction}')
            for p in files:
                Path(p).unlink(missing_ok=True)
            shots.append({'mode': mode, 'direction': direction, 'region': list(box),
                          'creature': list(creature), 'own': list(own), 'upper': list(upper),
                          'crop': rel(c), 'state': state, 'lighting': light})
    # R46 aura mirror pass: animations RUN, so the same-direction inter-frame
    # IoU measures the real scene noise (creature + flame motion) instead of a
    # paused-fixture 0.0. The aura-difference mask is scored only on the
    # asymmetric region about the creature's own body axis, and the gain must
    # beat the same-direction inter-frame noise baseline. R45 paused the
    # animations, which hid the noise.
    from PIL import Image
    # R45: THREE aura frames per direction. The same-direction inter-frame IoU
    # is the noise baseline, and the mirror gain is scored only on the
    # asymmetric region of the aura about the creature's own body axis.
    facing_aura = []
    for direction, flip in (('left', True), ('right', False)):
        set_direction('native', flip)
        standee_clear_auras(bridge, name)
        standee_lighting_state(bridge, name, set_state=True)
        off_states, off_paths = [], []
        for k in range(3):
            off_states.append(standee_lighting_state(bridge, name))
            off_paths.append(bridge.shot(f'standee-facing-aura-{slug}-{direction}-off-{k}'))
            time.sleep(.3)
        light = standee_floor_measure(off_paths, off_states, f'standee-facing-{slug}-aura-{direction}')
        p_off = off_paths[0]
        c_off = CROPS / f'standee-facing-aura-{slug}-{direction}-off-crop.png'
        Image.open(p_off).convert('RGB').crop(box).save(c_off)
        for path in off_paths:
            Path(path).unlink(missing_ok=True)
        standee_apply_aura(bridge, name, 'body_of_fire', True)
        ons = []
        for k in range(3):
            p_on = bridge.shot(f'standee-facing-aura-{slug}-{direction}-on-{k + 1}')
            c_on = CROPS / f'standee-facing-aura-{slug}-{direction}-on-{k + 1}-crop.png'
            Image.open(p_on).convert('RGB').crop(box).save(c_on)
            Path(p_on).unlink(missing_ok=True)
            ons.append(rel(c_on))
            time.sleep(0.3)
        facing_aura.append({'direction': direction, 'region': list(box), 'own': list(own),
                            'upper': list(upper), 'off': rel(c_off), 'ons': ons,
                            'state': bridge.lua(state_q), 'lighting': light})
    standee_clear_auras(bridge, name)
    entry['facing_aura'] = facing_aura
    # Aura state pass: the native base-redraw copy must be invis and the sdm
    # aura must carry the standee mark. No pixel comparison here.
    standee_apply_aura(bridge, name, 'body_of_fire', True)
    aura_state = {}
    for mode in ('fixed', 'native'):
        for direction, flip in (('left', True), ('right', False)):
            set_direction(mode, flip)
            aura_state['%s-%s' % (mode, direction)] = bridge.lua(state_q)
    standee_clear_auras(bridge, name)
    bridge.lua("config.settings.tome.checker_token_facing='fixed';game:checkerRefreshVisuals();mb.setTile(64);return true")
    entry['facing'] = shots
    entry['facing_aura_state'] = aura_state
    return shots


def standee_wall_cell(bridge):
    return bridge.lua(
        "local p=game.player;local Map=require 'engine.Map';local m=game.level.map;local best,bd;"
        "for x=p.x-9,p.x+9 do for y=p.y-7,p.y+7 do if mb.freeAt(x,y) and not mb.freeAt(x,y-1) then "
        "local wall=m:checkEntity(x,y-1,Map.TERRAIN,'block_move',p) and true or false;"
        "local sight=m:checkEntity(x,y-1,Map.TERRAIN,'block_sight',p) and true or false;"
        "local t=m(x,y-1,Map.TERRAIN);local door=t and (t.door or t.change_level or t.define_as=='DOOR') and true or false;"
        "local d=(x-p.x)^2+(y-p.y)^2;if (wall and sight) or door then if not bd or d<bd then best,bd={x=x,y=y,terrain=t and (t.name or t.define_as or tostring(t.image)) or false,image=t and t.image or false,door=door,wall=wall,sight=sight},d end end end end end;return best")


def standee_scroll_top(bridge, name):
    # R40: force the actor's own row to be the first visible map row via the
    # fixture helper (move to the top free row, then bounded setScroll).
    return bridge.lua(f"return mb.forceTop({json.dumps(name, ensure_ascii=False)})")


def run_scene(scene, bridge):
    label, zone, level, opts, steps = scene
    record = {'label': label, 'zone': zone, 'level': level, 'opts': opts, 'steps': []}
    bridge.lua("assert(config.settings.cheat and config.settings.disable_all_connectivity and not profile.auth);"
               "assert(core.shader.active(4));ms.setup()")
    names = '{' + ','.join(f'[{json.dumps(n, ensure_ascii=False)}]=true' for n in A + B + C + D + E + F + G + H + NATIVE + NATIVE_D + NATIVE_F + NATIVE_H + I + NATIVE_I + OOZES_SHIPPED + J + NATIVE_J + K + NATIVE_K + ['Grand Corruptor'] + L + NATIVE_L + M + NATIVE_M + N + NATIVE_N + O + NATIVE_O + P + NATIVE_P + Q + NATIVE_Q + R + NATIVE_R + S + NATIVE_S + T + NATIVE_T + BU + NATIVE_BU + BV + NATIVE_BV + BW + NATIVE_BW + BX + NATIVE_BX + BY + NATIVE_BY + BZ + NATIVE_BZ + BA + NATIVE_BA + BB + BC + NATIVE_BC + BD + BE + BF + ['dread', 'swarming horror', 'minotaur', 'ritch flamespitter', 'giant spider'] + ['assassin', 'bandit', 'thief', 'rogue', 'fire drake'] + U + ['ghoul', 'gigantic sandworm tunneler'] + UB2 + [UB2_ABOM[0], UB2_PALADIN[0]] + TA2) + '}'
    record['enter'] = bridge.lua(f"return ms.enter({json.dumps(zone, ensure_ascii=False)},{level},{lua_opts(opts)})")
    record['census_targets'] = bridge.lua(f"return mb.find({names})")
    census = bridge.lua('return ms.actorCensus()')
    record['census_all'] = census
    for step in steps:
        kind = step[0]
        if kind == 'gloom':
            found = resolve_gloom(bridge, step[1])
            record.setdefault('gloom_resolution', {})[step[1]] = found
            nm = found['natural'] or found['listed']
            if not nm:
                record['steps'].append({'step': ['gloom', step[1]], 'found': False})
                continue
            step = ('natural_or_place', nm, step[2])
            kind = step[0]
        if kind in ('toggle', 'aura', 'sustain', 'fade', 'wound', 'hide', 'stealth', 'urhrok', 'forcesus', 'thoughtform', 'friendly', 'neutral', 'ta2_aura'):
            # State checks need the subject inside the hero's current FOV.
            q = json.dumps(step[1], ensure_ascii=False)
            try:
                bridge.lua(f"local a=mb.byName({q});if a and not game.level.map.seens(a.x,a.y) then mb.approach({q}) end")
            except Exception as exc:
                print('PRECHECK approach failed', step, str(exc)[:200], flush=True)
        entry = {'step': list(step[:2]) if len(step) > 1 else [kind]}
        try:
            if kind == 'natural_or_place':
                q = json.dumps(step[1], ensure_ascii=False)
                has = bridge.lua(f"local a=mb.byName({q});return {{found=a and not a._checker_live_placed and true or false}}")
                if has['found'] and step[0] == 'natural_or_place' and REACH_FALLBACK:
                    reach = bridge.lua(f"local ok,err=pcall(mb.approach,{q});return {{ok=ok,err=tostring(err)}}")
                    if not reach['ok']:
                        entry['natural_unreachable'] = reach['err'][:120]
                        has['found'] = False
                kind = 'natural' if has['found'] else 'place'
                entry['resolved'] = kind
            if kind == 'native':
                src = json.dumps(step[2]) if len(step) > 2 and step[2] else 'nil'
                entry['source'] = step[2] if len(step) > 2 and step[2] else 'zone npc_list'
                das = json.dumps(step[3]) if len(step) > 3 and step[3] else 'nil'
                if len(step) > 3 and step[3] == '-none-':
                    # The leaf WITHOUT a define_as (mb.place filters only positively; the arena list also loads the define_as-bearing leaf of the same name).
                    entry['row'] = bridge.lua(NATIVE_NO_DEFINE_AS % (json.dumps(step[2]), json.dumps(step[1], ensure_ascii=False)))
                else:
                    entry['row'] = bridge.lua(f"return mb.place({json.dumps(step[1], ensure_ascii=False)},{src},2,-1,{das})")
                entry['native_ok'] = not entry['row']['rendered_token'] and not entry['row']['display_image']
                assert entry['native_ok'], entry['row']
                if len(step) > 4 and step[4] == 'shot':
                    # Negative evidence picture: drop any birth Stealth so the native body is drawn, then capture 64.
                    q = json.dumps(step[1], ensure_ascii=False)
                    entry['native_view'] = bridge.lua(
                        f"local a=mb.byName({q});local was=a:isTalentActive('T_STEALTH') and true or false;"
                        "if was then pcall(function() a:forceUseTalent('T_STEALTH',{ignore_energy=true,ignore_cd=true,no_talent_fail=true,silent=true}) end) end;"
                        "pcall(function() game.player:resetCanSeeCache();a:resetCanSeeCacheOf() end);mb.refresh();mb.focus(a.x,a.y);"
                        "local r=mb.row(a);r.was_stealthed=was;r.player_can_see=game.player:canSee(a) and true or false;return r")
                    if CLEAN:
                        clean_view_actor(bridge, step[1])
                        entry['native_view'] = bridge.lua(f"local a=mb.byName({q});local r=mb.row(a);r.player_can_see=game.player:canSee(a) and true or false;return r")
                    pn = bridge.shot(f'native-{step[1].replace(" ", "-")}-{label}')
                    entry['shots'] = [{'file': rel(pn), 'sha256': digest(pn), 'crop': rel(crop(pn, entry['native_view']['screen'], f'native-{step[1].replace(" ", "-")}-{label}-crop', 3))}]
                    assert not entry['native_view']['rendered_token'], entry['native_view']
            elif kind in ('natural', 'place'):
                actor, tiles = step[1], step[2]
                if kind == 'natural':
                    found = bridge.lua(f"local a=mb.byName({json.dumps(actor, ensure_ascii=False)});if not a or a._checker_live_placed then return {{found=false}} end;"
                                       f"return {{found=true,row=mb.approach({json.dumps(actor, ensure_ascii=False)})}}")
                    entry['found'] = found['found']
                    if not found['found']:
                        record['steps'].append(entry)
                        continue
                    entry['row'] = found['row']
                else:
                    try:
                        entry['row'] = bridge.lua(f"return mb.place({json.dumps(actor, ensure_ascii=False)},nil,1,1)")
                    except Exception as exc:
                        if actor not in PLACE_SRC_L and f'{actor}@{zone}' not in PLACE_SRC_L:
                            raise
                        srcp = PLACE_SRC_L.get(f'{actor}@{zone}') or PLACE_SRC_L[actor]
                        entry['zone_list_miss'] = str(exc)[:120]
                        entry['source'] = srcp
                        entry['row'] = bridge.lua(f"return mb.place({json.dumps(actor, ensure_ascii=False)},{json.dumps(srcp)},1,1)")
                    entry['found'] = True
                tag = 'placed' if kind == 'place' else 'natural'
                capture(bridge, f"{EXPECT.get(actor) or actor.replace(' ', '-')}-{tag}-{label}", actor, tiles, entry)
            elif kind == 'toggle':
                actor = step[1]
                sfx = step[2] if len(step) > 2 else ''
                q = json.dumps(actor, ensure_ascii=False)
                entry['off'] = bridge.lua(f"mb.tokens(false);local a=mb.byName({q});mb.focus(a.x,a.y);"
                                          "local rows={};for _,r in ipairs(mb.find()) do if r.rendered_token then rows[#rows+1]=r end end;"
                                          "return {enabled=game:checkerTokensEnabled(),row=mb.row(a),still_mapped=#rows}")
                p1 = bridge.shot(f'toggle-native{sfx}-{label}')
                entry['on'] = bridge.lua(f"mb.tokens(true);local a=mb.byName({q});mb.focus(a.x,a.y);"
                                         "return {enabled=game:checkerTokensEnabled(),row=mb.row(a)}")
                p2 = bridge.shot(f'toggle-refined{sfx}-{label}')
                entry['on_all'] = bridge.lua("local o={};for _,r in ipairs(mb.find()) do o[#o+1]={r.name,r.identify,r.rendered_token} end;return o")
                row = entry['on']['row']
                entry['shots'] = [{'file': rel(p1), 'sha256': digest(p1), 'crop': rel(crop(p1, row['screen'], f'toggle-native{sfx}-{label}-crop', 3))},
                                  {'file': rel(p2), 'sha256': digest(p2), 'crop': rel(crop(p2, row['screen'], f'toggle-refined{sfx}-{label}-crop', 3))}]
            elif kind == 'inspect':
                q = json.dumps(step[1], ensure_ascii=False)
                entry['fields'] = bridge.lua(
                    f"local a=mb.byName({q});return {{row=mb.row(a),type=a.type,subtype=a.subtype,"
                    "old_type=a.__old_type or false,image=a.image,define_as=a.define_as or false,"
                    "sustained=a:isTalentActive('T_FLAME_OF_URH_ROK') and true or false,"
                    "has_talent=a:knowTalent('T_FLAME_OF_URH_ROK') and true or false}")
            elif kind == 'aura':
                # Fyrk (sustains_at_birth): record Burning Wake state and the Actor.lua
                # shader-aura add_mos entry; activate the sustain if birth left it off.
                q = json.dumps(step[1], ensure_ascii=False)
                sfx = step[2] if len(step) > 2 else ''
                snap = ("local a=mb.byName(%s);pcall(function() a:updateModdableTile() end);mb.refresh();mb.focus(a.x,a.y);"
                        "local n=0;for _ in pairs(a.shader_auras or {}) do n=n+1 end;"
                        "local t=a.replace_display or a;local au=0;for _,m in ipairs(t.add_mos or {}) do if m._isshaderaura then au=au+1 end end;"
                        "local function L(t) local o={};for _,m in ipairs(t or {}) do o[#o+1]=(m._isshaderaura and 'AURA:' or '')..tostring(m.image)..'/'..tostring(m.shader or '') end return o end;"
                        "return {row=mb.row(a),shader_auras=n,aura_entries=au,image=a.image,own_add_mos=L(a.add_mos),"
                        "replace_display_image=a.replace_display and a.replace_display.image or false,replace_display_add_mos=L(a.replace_display and a.replace_display.add_mos),"
                        "burning_wake=a:isTalentActive('T_BURNING_WAKE') and true or false}") % q
                entry['before'] = bridge.lua(snap)
                pa = bridge.shot(f'aura-before{sfx}-{label}')
                if not entry['before']['burning_wake']:
                    entry['activate'] = bridge.lua(
                        f"local a=mb.byName({q});local ok,err=pcall(function() a:forceUseTalent('T_BURNING_WAKE',"
                        "{ignore_energy=true,ignore_cd=true,no_equilibrium_fail=true,silent=true}) end);return {ok=ok,err=tostring(err)}")
                    entry['after'] = bridge.lua(snap)
                    pb = bridge.shot(f'aura-after{sfx}-{label}')
                    entry['shots'] = [{'file': rel(pb), 'sha256': digest(pb),
                                       'crop': rel(crop(pb, entry['after']['row']['screen'], f'aura-after{sfx}-{label}-crop', 3))}]
                else:
                    entry['shots'] = [{'file': rel(pa), 'sha256': digest(pa),
                                       'crop': rel(crop(pa, entry['before']['row']['screen'], f'aura-before{sfx}-{label}-crop', 3))}]
            elif kind == 'sustain':
                q = json.dumps(step[1], ensure_ascii=False)
                sfx = step[2] if len(step) > 2 else ''
                entry['snap'] = bridge.lua(SUSTAIN_SNAP % q)
                p = bridge.shot(f'sustain{sfx}-{label}-{EXPECT.get(step[1], "x")}')
                entry['shots'] = [{'file': rel(p), 'sha256': digest(p),
                                   'crop': rel(crop(p, entry['snap']['row']['screen'], f'sustain{sfx}-{label}-{EXPECT.get(step[1], "x")}-crop', 3))}]
            elif kind == 'fade':
                q = json.dumps(step[1], ensure_ascii=False)
                entry['before'] = bridge.lua(SUSTAIN_SNAP % q)
                entry['use'] = bridge.lua(
                    f"local a=mb.byName({q});local ids={{}};for tid in pairs(a.talents or {{}}) do if tostring(tid):find('FADE') then ids[#ids+1]=tid end end;"
                    "local res={ids=ids};if #ids>0 then local ok,err=pcall(function() a:forceUseTalent(ids[1],{ignore_energy=true,ignore_cd=true,silent=true}) end);res.ok=ok;res.err=tostring(err)"
                    "else local ok,err=pcall(function() a:setEffect(a.EFF_FADED,3,{}) end);res.direct_effect=true;res.ok=ok;res.err=tostring(err) end;"
                    "res.faded=a:hasEffect(a.EFF_FADED) and true or false;return res")
                entry['after'] = bridge.lua(SUSTAIN_SNAP % q)
                p = bridge.shot(f'fade-{label}-{EXPECT.get(step[1], "x")}')
                entry['shots'] = [{'file': rel(p), 'sha256': digest(p),
                                   'crop': rel(crop(p, entry['after']['row']['screen'], f'fade-{label}-{EXPECT.get(step[1], "x")}-crop', 3))}]
                bridge.lua(f"local a=mb.byName({q});pcall(function() a:removeEffect(a.EFF_FADED,true,true) end);mb.refresh()")
            elif kind == 'minion':
                # Necromancer-style summon: build the talent's minion definition (no define_as,
                # native name/image), add it next to the hero and record its token resolution.
                name, tid, key = step[1], step[2], step[3]
                q = json.dumps(name, ensure_ascii=False)
                entry['row'] = bridge.lua(
                    "local Map=require 'engine.Map';local p=game.player;local t=p:getTalentFromId(%s) or (game.zone and require('engine.interface.ActorTalents').talents_def[%s]);"
                    "local def=t.minions_list[%s];local m=require('mod.class.NPC').new(table.clone(def,true));m:resolve();m:resolve(nil,true);"
                    "m.faction=p.faction;m.summoner=p;m.summoner_gain_exp=true;"
                    "local x,y=util.findFreeGrid(p.x+2,p.y+1,6,true,{[Map.ACTOR]=true});assert(x,'no free grid');"
                    "m._checker_live_placed=true;m._checker_live_minion=true;m.never_act=true;game.zone:addEntity(game.level,m,'actor',x,y);"
                    "mb.refresh();mb.focus(x,y);local r=mb.row(m);r.minion_define_as=m.define_as or false;r.minion_image=m.image or false;"
                    "r.summoner=m.summoner==p;return r" % (json.dumps(tid), json.dumps(tid), json.dumps(key)))
                entry['found'] = True
                pm = bridge.shot(f'minion-{EXPECT.get(name, "x")}-{label}')
                entry['shots'] = [{'file': rel(pm), 'sha256': digest(pm),
                                   'crop': rel(crop(pm, entry['row']['screen'], f'minion-{EXPECT.get(name, "x")}-{label}-crop', 3))}]
            elif kind == 'ghoulcheck':
                # Batch K contract: ghoul with define_as GHOUL maps; a same-named ghoul
                # without define_as (minion-like) stays native.
                entry['mapped'] = bridge.lua("return mb.place('ghoul','/data/general/npcs/ghoul.lua',-2,1,'GHOUL')")
                entry['no_define_as'] = bridge.lua(
                    "local a=mb.place('ghoul','/data/general/npcs/ghoul.lua',-3,2,'GHOUL');local m;for _,e in pairs(game.level.entities) do if e.x and e.name=='ghoul' and e~=game.player and e._checker_live_placed then m=e end end;"
                    "local Map=require 'engine.Map';local old=game.level.map;"
                    "local q=require('mod.class.NPC').new({name='ghoul',type='undead',subtype='ghoul',image=m.image,display='z',faction=game.player.faction,rank=2,max_life=50,life=50});q:resolve();q:resolve(nil,true);"
                    "local x,y=util.findFreeGrid(game.player.x+1,game.player.y+2,6,true,{[Map.ACTOR]=true});q._checker_live_placed=true;q.never_act=true;"
                    "game.zone:addEntity(game.level,q,'actor',x,y);mb.refresh();mb.focus(x,y);local r=mb.row(q);r.define_as_field=q.define_as or false;return r")
                assert entry['mapped']['identify'] == 'ghoul' and entry['mapped']['rendered_token'] == 'ghoul', entry['mapped']
                entry['ghoul_exact_ok'] = (not entry['no_define_as']['rendered_token'] and not entry['no_define_as']['identify'])
                pg = bridge.shot(f'ghoulcheck-{label}')
                entry['shots'] = [{'file': rel(pg), 'sha256': digest(pg), 'crop': rel(crop(pg, entry['no_define_as']['screen'], f'ghoulcheck-{label}-crop', 3))}]
            elif kind == 'usetalent':
                q = json.dumps(step[1], ensure_ascii=False)
                entry['use'] = bridge.lua(
                    f"local a=mb.byName({q});local tid={json.dumps(step[2])};local res={{known=a:knowTalent(tid) and true or false}};"
                    + ("if not res.known then a:learnTalent(tid,true,1);res.learned=true end;" if len(step) > 3 and step[3] == 'learn' else '') +
                    "local ok,err=pcall(function() a:forceUseTalent(tid,{ignore_energy=true,ignore_cd=true,no_equilibrium_fail=true,silent=true}) end);"
                    "res.ok=ok;res.err=tostring(err);res.active=a:isTalentActive(tid) and true or false;return res")
            elif kind == 'synth':
                # No live prototype (morphic ooze is commented out, bloated ooze never existed):
                # synthetic NPC with the native name/type/image; must stay native.
                name, img = step[1], step[2]
                entry['row'] = bridge.lua(
                    "local Map=require 'engine.Map';local p=game.player;"
                    f"local q=require('mod.class.NPC').new({{name={json.dumps(name)},type='vermin',subtype='oozes',image={json.dumps(img)},display='j',faction='enemies',rank=2,max_life=50,life=50}});"
                    "q:resolve();q:resolve(nil,true);local x,y=util.findFreeGrid(p.x+2,p.y+1,6,true,{[Map.ACTOR]=true});assert(x,'no free grid');"
                    "q._checker_live_placed=true;q.never_act=true;game.zone:addEntity(game.level,q,'actor',x,y);mb.refresh();mb.focus(x,y);local r=mb.row(q);r.synthetic=true;return r")
                entry['native_ok'] = not entry['row']['rendered_token'] and not entry['row']['identify']
                entry['found'] = True
                ps = bridge.shot(f'synth-{EXPECT.get(name, "x")}-{label}')
                entry['shots'] = [{'file': rel(ps), 'sha256': digest(ps), 'crop': rel(crop(ps, entry['row']['screen'], f'synth-{EXPECT.get(name, "x")}-{label}-crop', 3))}]
            elif kind == 'wildsummon':
                # Wild-gift minotaur (talents/gifts/summon-melee.lua:365): same name/type/tall PNG as the
                # zone minotaur, no define_as, summoner set; step[1] applies the "(wild summon)" rename.
                ren = 'true' if step[1] else 'false'
                Z = ("local Map=require 'engine.Map';local p=game.player;"
                     "local m=require('mod.class.NPC').new{type='giant',subtype='minotaur',display='H',name='minotaur',color=colors.UMBER,"
                     "resolvers.nice_tile{image='invis.png',add_mos={{image='npc/giant_minotaur_minotaur.png',display_h=2,display_y=-1}}},"
                     "body={INVEN=10,MAINHAND=1,OFFHAND=1,BODY=1},max_stamina=100,life_rating=13,max_life=60,infravision=10,autolevel='none',"
                     "stats={str=0,dex=0,con=0,cun=0,wil=0,mag=0},desc='cross',level_range={p.level,p.level},exp_worth=0,combat_armor=13,combat_def=8,"
                     "faction=p.faction,summoner=p,summoner_gain_exp=true,wild_gift_summon=true,summon_time=10};"
                     f"if {ren} then m.name=('%s (wild summon)'):format(m.name) end;"
                     "m:resolve();m:resolve(nil,true);m.summoner=p;m.is_nature_summon=true;"
                     "local x,y=util.findFreeGrid(p.x+2,p.y+1,6,true,{[Map.ACTOR]=true});assert(x,'no free grid');"
                     "m._checker_live_placed=true;m._checker_live_minion=true;m.never_act=true;game.zone:addEntity(game.level,m,'actor',x,y);"
                     "mb.refresh();mb.focus(x,y);local r=mb.row(m);r.summoner=m.summoner==p;r.define_as_field=m.define_as or false;r.summon_name=m.name;return r")
                entry['summon'] = bridge.lua(Z)
                tag = 'renamed' if step[1] else 'plain'
                ps = bridge.shot(f'wildsummon-{tag}-{label}')
                entry['shots'] = [{'file': rel(ps), 'sha256': digest(ps), 'crop': rel(crop(ps, entry['summon']['screen'], f'wildsummon-{tag}-{label}-crop', 3))}]
            elif kind == 'summon':
                sk, sname, wild, (dx, dy), expected = step[1], step[2], step[3], step[4], step[5]
                entry['summon'] = bridge.lua(summon_lua(sk, sname, wild, dx, dy))
                row = entry['summon']
                entry['expected'] = expected or False
                entry['ok'] = (row['identify'] == (expected or False) and row['rendered_token'] == (expected or False))
                if sk == 'alchemist_golem':
                    entry['ok'] = entry['ok'] and row['plain']['identify'] == False and row['plain']['rendered_token'] == False
                tag = sname.replace(' ', '-').replace('(', '').replace(')', '') if sname.isascii() else f'{sk}-localized'
                ps = bridge.shot(f'summon-{tag}-{label}')
                entry['shots'] = [{'file': rel(ps), 'sha256': digest(ps), 'crop': rel(crop(ps, row['screen'], f'summon-{tag}-{label}-crop', 3))}]
            elif kind == 'bandit_summon':
                # The lord's own Summon talent (npcs.lua T_SUMMON, self.summon = bandit x2, thief, rogue x2), used until every
                # summon name has appeared (at most 30 casts; a cast can make nothing when the zone filter misses); each new body is frozen and its row recorded.
                q = json.dumps(step[1], ensure_ascii=False)
                entry['summons'] = bridge.lua(
                    f"local lord=mb.byName({q});assert(lord,'no lord');local before={{}};for _,a in pairs(game.level.entities) do before[a]=true end;"
                    "local FT={ignore_energy=true,ignore_cd=true,no_equilibrium_fail=true,no_talent_fail=true,silent=true};"
                    "local seen,casts,out={},0,{};while casts<30 and not (seen.bandit and seen.thief and seen.rogue) do casts=casts+1;"
                    "local ok,err=pcall(lord.forceUseTalent,lord,'T_SUMMON',FT);assert(ok,tostring(err));"
                    "for _,a in pairs(game.level.entities) do if not before[a] and a.x then before[a]=true;a._checker_live_placed=true;a._checker_live_minion=true;a.never_act=true;"
                    "pcall(function() game:checkerRefreshActor(a,'display') end);seen[a.name]=true;out[#out+1]=a end end end;"
                    "mb.refresh();local rows={};for _,a in ipairs(out) do local r=mb.row(a);r.summoner_is_lord=(a.summoner==lord);r.define_as_field=a.define_as or false;rows[#rows+1]=r end;"
                    "mb.focus(lord.x,lord.y);return {casts=casts,rows=rows,lord=mb.row(lord)}")
                rows = entry['summons']['rows']
                entry['ok'] = {r['name'] for r in rows} >= {'bandit', 'thief', 'rogue'} and all(r['identify'] == r['name'] and r['rendered_token'] == r['name'] for r in rows if r['name'] in ('bandit', 'thief', 'rogue'))
                entry['names'] = sorted({r['name'] for r in rows})
                # Evidence view: drop the "Summoner unlocked" popup, then centre the view on the box that holds the lord and every summon
                # (they scatter up to ~10 grids), force that box lit, remembered and seen (no FOV recompute afterwards) so all tokens draw,
                # and crop exactly that box plus one grid of margin.
                bridge.lua("ms.caveClearDialogs();return true")
                entry['view'] = bridge.lua(
                    f"local lord=mb.byName({q});local m=game.level.map;local p=game.player;local Map=require 'engine.Map';"
                    "local group={lord};for _,a in pairs(game.level.entities) do if a.x and a._checker_live_minion and (a.name=='bandit' or a.name=='thief' or a.name=='rogue') then group[#group+1]=a end end;"
                    "local x0,y0,x1,y1=lord.x,lord.y,lord.x,lord.y;for _,a in ipairs(group) do x0,y0,x1,y1=math.min(x0,a.x),math.min(y0,a.y),math.max(x1,a.x),math.max(y1,a.y) end;"
                    "m.smooth_scroll=0;m:centerViewAround(math.floor((x0+x1)/2),math.floor((y0+y1)/2));m:redisplay();"
                    "for x=x0-2,x1+2 do for y=y0-2,y1+2 do if x>=0 and y>=0 and x<m.w and y<m.h then pcall(function() m.lites(x,y,true);m.remembers(x,y,true);m.seens(x,y,true) end) end end end;"
                    "for _,a in ipairs(group) do if a:isTalentActive('T_STEALTH') then pcall(function() a:forceUseTalent('T_STEALTH',{ignore_energy=true,ignore_cd=true,no_talent_fail=true,silent=true}) end) end end;"
                    "pcall(function() p:resetCanSeeCache() end);for _,a in ipairs(group) do pcall(function() a:resetCanSeeCacheOf() end) end;"
                    "m.changed=true;game.paused=true;ms.caveClearDialogs();core.display.forceRedraw();"
                    "local rows={};for _,a in ipairs(group) do local r=mb.row(a);r.can_see=p:canSee(a) and true or false;r.seen=m.seens(a.x,a.y) and true or false;rows[#rows+1]=r end;"
                    "return {box={x0,y0,x1,y1},rows=rows}")
                ps = bridge.shot(f'bandit-summons-{label}')
                from PIL import Image
                sc = [r['screen'] for r in entry['view']['rows']]
                tt = sc[0][2]
                im = Image.open(ps).convert('RGB')
                box = (max(0, min(c[0] for c in sc) - tt), max(0, min(c[1] for c in sc) - tt), min(im.width, max(c[0] for c in sc) + 2 * tt), min(im.height, max(c[1] for c in sc) + 2 * tt))
                cp = CROPS / f'bandit-summons-{label}-crop.png'
                CROPS.mkdir(parents=True, exist_ok=True)
                im.crop(box).save(cp)
                entry['view']['crop_box'] = box
                entry['shots'] = [{'file': rel(ps), 'sha256': digest(ps), 'crop': rel(cp)}]
            elif kind == 'dm_summon':
                # The Necromancer's real Dread talent (spells/dreadmaster.lua action) with T_DREADMASTER known makes the dreadmaster minion.
                entry['summon'] = bridge.lua(SUMMON_PRE +
                    "learn('T_DREAD');learn('T_DREADMASTER');local ok,err=pcall(p.forceUseTalent,p,'T_DREAD',FT);assert(ok,tostring(err));"
                    "local m=newest(function(a) return a.dread_minion end);local r=fin(m,'dreadmaster');"
                    "r.dread_minion=m.dread_minion;r.necrotic_minion=m.necrotic_minion or false;r.type=m.type;r.subtype=m.subtype;r.image=m.image;"
                    "r.summoner=(m.summoner==p);r.knows_dreadmaster=p:knowTalent('T_DREADMASTER') and true or false;r.define_as_field=m.define_as or false;return r")
                # Evidence view: popup ("new class unlocked") cleared, hero and minion lit and marked seen, both centred.
                bridge.lua("ms.caveClearDialogs();return true")
                entry['view'] = bridge.lua(
                    "local M;for _,a in pairs(game.level.entities) do if a._checker_live_minion and a.name=='dreadmaster' then M=a end end;assert(M,'no minion');"
                    "local m=game.level.map;local p=game.player;local x0,y0,x1,y1=math.min(p.x,M.x),math.min(p.y,M.y),math.max(p.x,M.x),math.max(p.y,M.y);"
                    "for x=x0-4,x1+4 do for y=y0-4,y1+4 do if x>=0 and y>=0 and x<m.w and y<m.h then pcall(function() m.lites(x,y,true);m.remembers(x,y,true);m.seens(x,y,true) end) end end end;"
                    "if M.stealth then M._checker_live_was_stealth=M.stealth;M.stealth=nil;M.inc_stealth=nil end;"
                    "if M:isTalentActive('T_STEALTH') then pcall(function() M:forceUseTalent('T_STEALTH',{ignore_energy=true,ignore_cd=true,no_talent_fail=true,silent=true}) end) end;"
                    "pcall(function() p:resetCanSeeCache();M:resetCanSeeCacheOf() end);"
                    "m.smooth_scroll=0;m:centerViewAround(math.floor((x0+x1)/2),math.floor((y0+y1)/2));m:redisplay();m.changed=true;game.paused=true;ms.caveClearDialogs();core.display.forceRedraw();"
                    "local r=mb.row(M);r.can_see=p:canSee(M) and true or false;local h=mb.row(p);return {minion=r,hero=h,box={x0,y0,x1,y1},vp={m.display_x,m.display_y,m.viewport.width,m.viewport.height}}")
                _set_vp(entry['view'])
                row = entry['summon']
                entry['ok'] = (row['identify'] == 'dreadmaster' and row['rendered_token'] == 'dreadmaster' and row['knows_dreadmaster']
                               and row['summoner'] and entry['view']['minion']['can_see'] and entry['view']['minion']['rendered_token'] == 'dreadmaster')
                ps = bridge.shot(f'dreadmaster-minion-{label}')
                from PIL import Image
                sc = [entry['view']['minion']['screen'], entry['view']['hero']['screen']]
                tt = sc[0][2]
                im = Image.open(ps).convert('RGB')
                box = clamp_box((max(0, min(c[0] for c in sc) - tt), max(0, min(c[1] for c in sc) - tt), min(im.width, max(c[0] for c in sc) + 2 * tt), min(im.height, max(c[1] for c in sc) + 2 * tt)))
                cp = CROPS / f'dreadmaster-minion-{label}-crop.png'
                CROPS.mkdir(parents=True, exist_ok=True)
                im.crop(box).save(cp)
                entry['view']['crop_box'] = box
                entry['shots'] = [{'file': rel(ps), 'sha256': digest(ps), 'crop': rel(cp)}]
            elif kind == 'group_view':
                # Several named subjects in one evidence picture (64px): dialogs cleared, area lit, stealth dropped, centred.
                view = _set_vp(bridge.lua(CLEAN_VIEW % (step[2], GROUP_CENTER)))
                ps = bridge.shot(f'{step[1]}-group-{label}')
                cp, box = group_crop(view, ps, f'{step[1]}-group-{label}')
                view['crop_box'] = box
                entry['view'] = view
                entry['ok'] = {r['name'] for r in view['rows']} >= set(step[3]) and all(
                    r['can_see'] and r['identify'] == r['rendered_token'] == EXPECT[r['name']] and r['explain'] == 'exact-identity'
                    for r in view['rows'] if r['name'] in step[3])
                entry['define_as'] = {r['name']: r['define_as'] for r in view['rows'] if r['name'] in step[3]}
                entry['shots'] = [{'file': rel(ps), 'sha256': digest(ps), 'crop': rel(cp)}]
            elif kind == 'osummon':
                entry['summon'] = bridge.lua(OSUMMON_LUA % json.dumps(step[1], ensure_ascii=False))
                view = _set_vp(bridge.lua(CLEAN_VIEW % ("(a._checker_live_group or a._checker_live_minion)", GROUP_CENTER)))
                ps = bridge.shot(f'orc-summoner-summons-{label}')
                cp, box = group_crop(view, ps, f'orc-summoner-summons-{label}')
                view['crop_box'] = box
                entry['view'] = view
                entry['shots'] = [{'file': rel(ps), 'sha256': digest(ps), 'crop': rel(cp)}]
                got = {r['name']: r for r in view['rows']}
                res = {}
                for nm, tok in SUMMON_EXPECT_BB.items():
                    r = got.get(nm)
                    res[nm] = bool(r) and r['identify'] == (tok or False) and r['rendered_token'] == (tok or False) and r['can_see']
                entry['expected'] = SUMMON_EXPECT_BB
                entry['per_summon_ok'] = res
                entry['ok'] = all(res.values()) and all(x.get('made') and x.get('summoner_is_orc') for x in entry['summon']['summons'])
            elif kind == 'hive_summon':
                entry['summons'] = bridge.lua(HIVE_LUA % json.dumps(step[1], ensure_ascii=False))
                view = _set_vp(bridge.lua(CLEAN_VIEW % ("(a._checker_live_group or a._checker_live_minion)", GROUP_CENTER)))
                ps = bridge.shot(f'swarm-hive-summons-{label}')
                cp, box = group_crop(view, ps, f'swarm-hive-summons-{label}')
                view['crop_box'] = box
                entry['view'] = view
                entry['shots'] = [{'file': rel(ps), 'sha256': digest(ps), 'crop': rel(cp)}]
                rows = [r for r in view['rows'] if r['name'] == 'swarming horror']
                entry['ok'] = len(rows) >= 3 and all(r['identify'] == r['rendered_token'] == 'swarming-horror' and r['can_see'] for r in rows) and all(
                    r['summoner_is_hive'] and r['identify'] == 'swarming-horror' for r in entry['summons']['rows'])
            elif kind == 'vilespawn':
                # Negative: the Corpathus artifact's real summon (reuses the oozing horror PNG under its own name) stays native.
                entry['summon'] = bridge.lua(VILESPAWN_LUA)
                view = _set_vp(bridge.lua(CLEAN_VIEW % ("(a._checker_live_placed or a._checker_live_minion)", GROUP_CENTER)))  # the earlier tokens stand beside it for comparison
                ps = bridge.shot(f'vilespawn-native-{label}')
                cp, box = group_crop(view, ps, f'vilespawn-native-{label}', 2)
                view['crop_box'] = box
                entry['view'] = view
                entry['shots'] = [{'file': rel(ps), 'sha256': digest(ps), 'crop': rel(cp)}]
                sm = entry['summon']
                entry['ok'] = sm['identify'] is False and sm['rendered_token'] is False and not sm.get('display_image') and sm['name'] == 'Vilespawn' \
                    and [r['rendered_token'] for r in view['rows'] if r['name'] == 'Vilespawn'] == [False] and all(
                        r['can_see'] and (r['name'] == 'Vilespawn' or r['identify'] == r['rendered_token'] == EXPECT[r['name']]) for r in view['rows'])
            elif kind == 'tsummon':
                entry['summons'] = bridge.lua(TSUMMON_LUA % json.dumps(step[1], ensure_ascii=False))
                view = _set_vp(bridge.lua(CLEAN_VIEW % ("(a._checker_live_group or a._checker_live_minion)", GROUP_CENTER)))
                ps = bridge.shot(f'vampire-lord-summons-{label}')
                cp, box = group_crop(view, ps, f'vampire-lord-summons-{label}', 2)
                view['crop_box'] = box
                entry['view'] = view
                entry['shots'] = [{'file': rel(ps), 'sha256': digest(ps), 'crop': rel(cp)}]
                srows = entry['summons']['rows']
                vrows = [r for r in view['rows'] if r['name'] != step[1]]
                entry['summon_names'] = [[r['name'], r['identify'], r['rendered_token']] for r in srows]
                entry['mapped_count'] = sum(1 for r in srows if r['identify'])
                entry['ok'] = len(srows) >= 3 and len(vrows) == len(srows) and entry['mapped_count'] >= 1 and all(
                    r['summoner_is_lord'] and r['identify'] == r['rendered_token'] for r in srows) and all(
                    r['can_see'] and r['identify'] == r['rendered_token'] for r in vrows)
            elif kind == 'rift_repro':
                import numpy as np
                from PIL import Image
                CROPS.mkdir(parents=True, exist_ok=True)
                SUBJ = [('ultimate teluvorta', '/data/general/npcs/telugoroth.lua', (-1, -1), True), ('dredge', '/data/general/npcs/horror_temporal.lua', (1, 0), False)]
                site = bridge.lua(RIFT_SITE)
                bridge.lua("mb.clearAround(7);return true")
                hx, hy = site['hx'], site['hy']
                bridge.lua(f"local p=game.player;p:move({hx},{hy},true);mb.refresh();return true")
                placed = [bridge.lua(PLACE_AT % (json.dumps(src), json.dumps(nm), hx + dx, hy + dy)) for nm, src, (dx, dy), _ in SUBJ]
                entry['site'] = site
                entry['placed'] = [{'name': r['name'], 'cell': [r['x'], r['y']], 'identify': r['identify']} for r in placed]
                entry['frames'] = []
                res = {}

                def setup():
                    return _set_vp(bridge.lua(CLEAN_VIEW_KEEP % ("a._checker_live_placed", "p.x,p.y")))

                def layers(fg, wp):
                    bridge.lua(RIFT_LAYERS % ('true' if fg else 'false', 'true' if wp else 'false'))

                def grab(name):
                    return np.array(Image.open(bridge.shot(name)).convert('RGB')).astype(int)

                def regions(view, t):
                    out = {}
                    for r in view['rows']:
                        x, y, tt = r['screen']
                        out[r['name']] = (x, y - tt, tt, 2 * tt) if r['name'] == 'ultimate teluvorta' else (x, y, tt, tt)
                    return out

                def metric(fr, base, box):
                    x, y, w, h = box
                    a, b = fr[y:y + h, x:x + w], base[y:y + h, x:x + w]
                    ratio = float(a.sum() / max(1, b.sum()))
                    changed = float((np.abs(a - b).max(axis=2) > 24).mean())
                    return {'lum_ratio': round(ratio, 3), 'changed': round(changed, 3)}

                for t in (48, 64):
                    bridge.lua(f"mb.setTile({t});return true")
                    for state in ('on', 'off'):
                        bridge.lua(f"mb.tokens({'true' if state == 'on' else 'false'});return true")
                        view = setup()
                        boxes = regions(view, t)
                        layers(False, False)  # baseline: both level layers withheld
                        base = grab(f'rift-tmp-base-{t}-{state}')
                        base_path = SHOTS / f'rift-tmp-base-{t}-{state}.png'
                        layers(True, True)
                        best = None
                        att = []
                        for i in range(RIFT_ATTEMPTS):
                            bridge.lua("core.display.forceRedraw();return true")
                            nm = f'rift-tmp-{t}-{state}-{i}'
                            fr = grab(nm)
                            met = {k: metric(fr, base, bx) for k, bx in boxes.items()}
                            att.append(met)
                            key = met['ultimate teluvorta']['changed'] + met['dredge']['changed']
                            if best is None or key > best[0]:
                                if best is not None:
                                    (SHOTS / f'rift-tmp-{t}-{state}-{best[1]}.png').unlink(missing_ok=True)
                                best = (key, i)
                            else:
                                (SHOTS / f'{nm}.png').unlink(missing_ok=True)
                        rows_now = view['rows']
                        sc = [r['screen'] for r in rows_now]
                        im0 = Image.open(base_path).convert('RGB')
                        box = clamp_box((max(0, min(c[0] for c in sc) - t), max(0, min(c[1] for c in sc) - 2 * t),
                                         min(im0.width, max(c[0] for c in sc) + 2 * t), min(im0.height, max(c[1] for c in sc) + 2 * t)))
                        final = {}
                        for tag, src_png in (('covered-worst-of-%d' % RIFT_ATTEMPTS, SHOTS / f'rift-tmp-{t}-{state}-{best[1]}.png'), ('layers-withheld', base_path)):
                            dst = SHOTS / f'rift-repro-{state}-{t}-{tag}.png'
                            shutil.move(str(src_png), str(dst))
                            cp = CROPS / f'rift-repro-{state}-{t}-{tag}-crop.png'
                            Image.open(dst).convert('RGB').crop(box).save(cp)
                            final[tag] = {'file': rel(dst), 'sha256': digest(dst), 'crop': rel(cp)}
                        entry['frames'].append({'tile': t, 'state': state, 'rows': [[r['name'], r['identify'], r['rendered_token'], r['can_see'], r['screen']] for r in rows_now],
                                                'crop_box': box, 'attempts': att, 'worst_attempt': best[1], 'files': final,
                                                'worst_changed': {k: max(a[k]['changed'] for a in att) for k in boxes},
                                                'worst_lum_ratio': {k: min(a[k]['lum_ratio'] for a in att) for k in boxes}})
                # Layer attribution at 64px with tokens ON: each level layer alone, N frames each, versus the both-withheld baseline.
                bridge.lua("mb.setTile(64);mb.tokens(true);return true")
                view = setup()
                boxes = regions(view, 64)
                layers(False, False)
                base = grab('rift-tmp-attr-base')
                attr = {}
                for label_, fg, wp in (('foreground_only', True, False), ('weather_only', False, True), ('both', True, True)):
                    layers(fg, wp)
                    fr_ = []
                    for i in range(6):
                        bridge.lua("core.display.forceRedraw();return true")
                        fr = grab('rift-tmp-attr')
                        fr_.append({k: metric(fr, base, bx) for k, bx in boxes.items()})
                    attr[label_] = {'worst_changed': {k: max(a[k]['changed'] for a in fr_) for k in boxes},
                                    'worst_lum_ratio': {k: min(a[k]['lum_ratio'] for a in fr_) for k in boxes}, 'frames': fr_}
                for f in SHOTS.glob('rift-tmp-*'):
                    f.unlink()
                layers(True, True)
                entry['layer_attribution'] = attr
                entry['layer_objects'] = bridge.lua(
                    "local L=game.level;local fp=L._rr_fg;local wp=L._rr_wp;return {foreground_particle_def=fp and tostring(fp.def) or false,"
                    "foreground_particle_shader=fp and fp.shader and fp.shader.type or false,zone_foreground_fn=type(L.data.foreground),"
                    "weather_particles=wp and #wp or 0,weather_def=wp and wp[1] and tostring(wp[1].def) or false,"
                    "weather_effects=config.settings.tome.weather_effects and true or false,tile=game.level.map.tile_w}")
                entry['ok'] = all(f['rows'] and all(r[3] for r in f['rows']) for f in entry['frames']) and len(entry['frames']) == 4
            elif kind == 'stealth_seen':
                # Felines with T_STEALTH active AND detectable (temporary negative stealth power): the token must draw while the sustain is on.
                roster = step[1]
                entry['cleared'] = bridge.lua("return {n=mb.clearAround(6)}")
                for (n, sp), (dx, dy) in zip(roster, [(-3, 1), (-1, 1), (1, 1), (3, 1)]):
                    bridge.lua(f"return mb.place({json.dumps(n, ensure_ascii=False)},{json.dumps(sp)},{dx},{dy})")
                bridge.lua("for _,a in pairs(game.level.entities) do if a._checker_live_placed and a~=game.player then "
                           "if not a:isTalentActive('T_STEALTH') then pcall(function() a:forceUseTalent('T_STEALTH',{ignore_energy=true,ignore_cd=true,no_talent_fail=true,silent=true}) end) end;"
                           "a._sl_boost=a:addTemporaryValue('stealth',-1000) end end;return true")
                keep = CLEAN_VIEW
                for frag in ("for _,a in ipairs(grp) do if a.stealth then a._checker_live_was_stealth=a.stealth;a.stealth=nil;a.inc_stealth=nil end end;",
                             "for _,a in ipairs(grp) do if a:isTalentActive('T_STEALTH') then pcall(function() a:forceUseTalent('T_STEALTH',{ignore_energy=true,ignore_cd=true,no_talent_fail=true,silent=true}) end) end end;"):
                    assert frag in keep
                    keep = keep.replace(frag, '')
                view = _set_vp(bridge.lua(keep % ("a._checker_live_placed", "p.x,p.y")))
                entry['rows'] = bridge.lua("local o={};for _,r in ipairs(mb.find()) do if r.placed then local a=mb.byName(r.name);o[#o+1]={r.name,r.identify,r.rendered_token,r.can_see,a:isTalentActive('T_STEALTH') and true or false} end end;return o")
                ps = bridge.shot(f'stealth-seen-{label}')
                cp, box = group_crop(view, ps, f'stealth-seen-{label}', 1)
                entry['shots'] = [{'file': rel(ps), 'sha256': digest(ps), 'crop': rel(cp)}]
                entry['ok'] = len(entry['rows']) == len(roster) and all(r[3] and r[4] and r[1] == r[2] == EXPECT[r[0]] for r in entry['rows'])
            elif kind == 'nicer_off':
                # Fresh placements made while engine.Map.tiles.nicer_tiles is off (resolvers.nice_tile resolves at entity creation).
                roster = step[1]
                entry['cleared'] = bridge.lua("return {n=mb.clearAround(6)}")
                entry['nicer_before'] = bridge.lua("return {v=require('engine.Map').tiles.nicer_tiles}")['v']
                bridge.lua("require('engine.Map').tiles.nicer_tiles=false;return true")
                try:
                    entry['rows'] = [bridge.lua(f"local r=mb.place({json.dumps(n, ensure_ascii=False)},{json.dumps(sp)},{dx},{dy});r._fallback=true;return r")
                                     for (n, sp), (dx, dy) in zip(roster, step[2] if len(step) > 2 else [(-4, 1), (0, 1), (4, 1)])]
                    view = _set_vp(bridge.lua(CLEAN_VIEW % ("a._checker_live_placed", "p.x,p.y")))
                    entry['nicer_during'] = bridge.lua("return {v=require('engine.Map').tiles.nicer_tiles}")['v']
                    entry['view_rows'] = [[r['name'], r['identify'], r['rendered_token'], r['can_see'], r.get('image'), r['screen']] for r in view['rows']]
                    ps = bridge.shot(f'nicer-off-{label}')
                    cp, box = group_crop(view, ps, f'nicer-off-{label}', 1)
                    entry['shots'] = [{'file': rel(ps), 'sha256': digest(ps), 'crop': rel(cp)}]
                finally:
                    bridge.lua("require('engine.Map').tiles.nicer_tiles=true;"
                               "local rm={};for _,a in pairs(game.level.entities) do if a.x and a._checker_live_placed and a._fallback_marker==nil and a~=game.player then rm[#rm+1]=a end end;"
                               "for _,a in ipairs(rm) do pcall(function() game.level.map:remove(a.x,a.y,require('engine.Map').ACTOR);game.level:removeEntity(a,true) end) end;"
                               "mb.refresh();return {removed=#rm}")
                entry['nicer_restored'] = bridge.lua("return {v=require('engine.Map').tiles.nicer_tiles}")['v']
            elif kind == 'ua_group':
                mode=step[1]
                bridge.lua('mb.clearAround(8);_G.UAC={};return true')
                cases=UA_CASES if mode in ('lineup','badge') else ([next(c for c in UA_CASES if c[3]==i) for i in ('grushnak','gorbat','ninandra','grgglck','rungof')]+UA_KIN if mode=='kin' else [next(c for c in UA_CASES if c[3]=='rungof')]*6)
                positions=UA_POS
                if mode.startswith('kin-'):
                    ids={'kin-orc':['grushnak','orc-warrior','gorbat'],'kin-weaver':['ninandra','weaver-queen'],
                         'kin-horror':['grgglck','nightmare-horror','abyssal-horror'],'kin-warg':['rungof','great-wolf','warg']}[mode]
                    cases=[next(c for c in UA_CASES+UA_KIN if c[3]==tid) for tid in ids]
                    positions=[(-2,1),(0,1),(2,1)] if len(cases)==3 else [(-1,1),(1,1)]
                for index,((n,src,das,tid),(dx,dy)) in enumerate(zip(cases,positions)):
                    bridge.lua(f"mb.place({lua_value(n)},{lua_value(src)},{dx},{dy},{lua_value(das)});local best;for _,a in pairs(game.level.entities) do if a._checker_live_placed and a.x and not a._ua_id then best=a end end;assert(best);best._ua_id={lua_value(tid)};UAC[#UAC+1]=best;return true")
                    if mode=='prefix':
                        # Execute the actual native Heart Gloom modifier in its native locale,
                        # controlling only which of the three prefix choices is selected.
                        bridge.lua("local a=UAC[#UAC];local text=fs.readAll('/data/zones/heart-gloom/npcs.lua');local first=assert(text:find('if not currentZone.is_purified then',1,true));local last=assert(text:find('load(\"/data/general/npcs/rodent.lua\"',first,true));local code=text:sub(first,last-1)..';return alter(1)';"
                            +f"local env=setmetatable({{currentZone={{is_purified={'true' if index>=3 else 'false'}}},Talents=require('engine.interface.ActorTalents'),rng={{table=function(t) return t[1]:sub(1,2)=='T_' and t[1] or t[{index%3+1}] end}}}},{{__index=_G}});local f=assert(loadstring(code));setfenv(f,env);f()(a);mb.refresh();return mb.row(a)")
                if mode=='badge':
                    entry['before']=bridge.lua("local out={};for _,a in ipairs(UAC) do out[#out+1]=mb.row(a);a.rank=2 end;mb.refresh();return out")
                snap="local out={};local Style=require 'mod.class.CheckerTokenStyle';for _,a in ipairs(UAC) do local r=mb.row(a);r.ua_id=a._ua_id;r.badge=Style.rankBadge(a.rank) or false;r.shader=a.shader or false;local d=a.replace_display;r.replacement_display_h=d and d.display_h or false;r.replacement_add_mos=d and d.add_mos or false;out[#out+1]=r end;return out"
                entry['states']=[]
                for enabled,roundno in (((True,0),(False,1),(True,1),(False,2),(True,2)) if mode=='lineup' else ((True,0),)):
                    bridge.lua('mb.tokens('+('true' if enabled else 'false')+');return true')
                    state={'enabled':enabled,'round':roundno,'frames':[]}
                    for tile in (48,64,96):
                        bridge.lua(f'mb.setTile({tile});return true')
                        view=_set_vp(bridge.lua(CLEAN_VIEW % ('a._ua_id',GROUP_CENTER)))
                        rows=bridge.lua(snap)
                        name=f'ua-{mode}-{label}-r{roundno}-{"token" if enabled else "native"}-{tile}'
                        ps=bridge.shot(name);cp,box=group_crop(view,ps,name,1)
                        state['frames'].append({'tile':tile,'rows':rows,'view':view,'file':rel(ps),'crop':rel(cp),'crop_box':box,'sha256':digest(cp)})
                    entry['states'].append(state)
                bridge.lua('mb.setTile(64);return true')
            elif kind == 'ua_negative':
                entry['cases']=[]
                cases=[(next(c for c in UA_CASES if c[3]==tid),das) for tid in ('grushnak','phoenix') for das in (None,'OTHER_BOSS')]
                cases.append((('The Shade','/data/zones/ruins-kor-pul/npcs.lua','SHADE','the-shade-native'),'SHADE'))
                for (n,src,das,tid),newdas in cases:
                    bridge.lua(f'mb.clearAround(8);mb.place({lua_value(n)},{lua_value(src)},1,1,{lua_value(das)});_G.UAN=mb.byName({lua_value(n)});UAN.define_as={lua_value(newdas)};mb.refresh();return true')
                    view=_set_vp(bridge.lua(CLEAN_VIEW % ('a==UAN',GROUP_CENTER)))
                    r=bridge.lua('local r=mb.row(UAN);r.shader=UAN.shader or false;return r')
                    name=f'ua-negative-{tid}-{newdas}-{label}'
                    ps=bridge.shot(name);cp,box=group_crop(view,ps,name,1)
                    entry['cases'].append({'id':tid,'define_as':newdas,'row':r,'view':view,'crop':rel(cp)})
                c=next(c for c in UA_CASES if c[3]=='phoenix');n,src,das,tid=c
                bridge.lua(f'mb.clearAround(8);mb.place({lua_value(n)},{lua_value(src)},1,1,{lua_value(das)});_G.UAN=mb.byName({lua_value(n)});return true')
                entry['phoenix']=[]
                for form,code in [('bird',''),('egg','UAN:setEffect(UAN.EFF_PHOENIX_EGG,10,{});'),('reborn','UAN:removeEffect(UAN.EFF_PHOENIX_EGG,true,true);')]:
                    bridge.lua(code+'mb.refresh();return true')
                    for tile in (48,64,96):
                        bridge.lua(f'mb.setTile({tile});return true')
                        view=_set_vp(bridge.lua(CLEAN_VIEW % ('a==UAN',GROUP_CENTER)))
                        r=bridge.lua('return mb.row(UAN)')
                        name=f'ua-phoenix-{form}-{label}-{tile}'
                        ps=bridge.shot(name);cp,box=group_crop(view,ps,name,1)
                        entry['phoenix'].append({'form':form,'tile':tile,'row':r,'view':view,'crop':rel(cp)})
            elif kind == 'ag_cycle':
                nicer = step[1]
                bridge.lua("mb.clearAround(8);require('engine.Map').tiles.nicer_tiles=" + ('true' if nicer else 'false') + ";_G.AGC={};return true")
                for (n,src,das,tid),(dx,dy) in zip(AG_CASES,AG_POS):
                    bridge.lua(f"mb.place({lua_value(n)},{lua_value(src)},{dx},{dy},{lua_value(das)});local best;for _,a in pairs(game.level.entities) do if a._checker_live_placed and a.x and not a._ag_id then best=a end end;assert(best);best._ag_id={lua_value(tid)};best._checker_live_group=true;AGC[#AGC+1]=best;return true")
                snap = "local out={};for _,a in ipairs(AGC) do local r=mb.row(a);r.ag_id=a._ag_id;r.shader=a.shader or false;r.shader_args=a.shader_args or false;r.replacement_shader=a.replace_display and a.replace_display.shader or false;r.replacement_display_h=a.replace_display and a.replace_display.display_h or false;out[#out+1]=r end;return out"
                entry['nicer_tiles'] = bridge.lua("return {value=require('engine.Map').tiles.nicer_tiles}")['value']
                entry['states'] = []
                for enabled,roundno in ((True,0),(False,1),(True,1),(False,2),(True,2)):
                    bridge.lua('mb.tokens(' + ('true' if enabled else 'false') + ');return true')
                    state = {'enabled':enabled,'round':roundno,'rows':bridge.lua(snap),'frames':[]}
                    # First off/on cycle includes 3 timed frames at every requested size.
                    for tile in ((48,64,96) if roundno < 2 else (64,)):
                        bridge.lua(f'mb.setTile({tile});return true')
                        view = _set_vp(bridge.lua(CLEAN_VIEW % ('a._checker_live_group',GROUP_CENTER)))
                        state.setdefault('views',[]).append(view)
                        rows=bridge.lua(snap)
                        for frame in range(3 if roundno < 2 else 1):
                            name=f'ag-{label}-r{roundno}-{"token" if enabled else "native"}-{tile}-f{frame}'
                            ps=bridge.shot(name)
                            cp,box=group_crop(view,ps,name,1)
                            subjects=[]
                            from PIL import Image
                            im=Image.open(ps).convert('RGB')
                            for r in rows:
                                x,y,t=r['screen']; body=im.crop((x,y,x+t,y+t))
                                subjects.append({'id':r['ag_id'],'tile_sha256':hashlib.sha256(body.tobytes()).hexdigest()})
                            state['frames'].append({'tile':tile,'frame':frame,'time_monotonic':time.monotonic(),'file':rel(ps),'crop':rel(cp),'crop_box':box,'subjects':subjects,'rows':rows})
                    entry['states'].append(state)
                bridge.lua('mb.setTile(64);return true')
            elif kind == 'ag_negative':
                entry['cases']=[]
                for das in (None,'OTHER_SHADOW'):
                    bridge.lua("mb.clearAround(8);mb.place('shadow claw','/data/zones/keepsake-meadow/npcs.lua',1,1,'SHADOW_CASTER');return true")
                    r=bridge.lua("local a=mb.byName('shadow claw');a.define_as="+lua_value(das)+";game:checkerRefreshActor(a,'display');mb.refresh();return mb.row(a)")
                    view=_set_vp(bridge.lua(CLEAN_VIEW % ('a._checker_live_placed',GROUP_CENTER)))
                    ps=bridge.shot('ag-negative-'+str(das)+'-'+label);cp,box=group_crop(view,ps,'ag-negative-'+str(das)+'-'+label,1)
                    entry['cases'].append({'define_as':das,'row':r,'view':view,'crop':rel(cp)})
                bridge.lua("mb.clearAround(8);mb.place('dreaming horror','/data/general/npcs/horror.lua',1,1);return true")
                r=bridge.lua("local a=mb.byName('dreaming horror');local r=mb.row(a);r.shader=a.shader or false;return r")
                capture(bridge,'ag-dreaming-'+label,'dreaming horror',(48,64,96),entry)
                entry['dreaming']=r
                bridge.lua("mb.clearAround(8);mb.place('lich','/data/general/npcs/lich.lua',1,1);local p=game.player;local Map=require 'engine.Map';local x,y=util.findFreeGrid(p.x,p.y,3,true,{[Map.ACTOR]=true});local f=getfenv(p:getTalentFromId('T_AMBUSH_TRAP').action).summon_assassin;assert(type(f)=='function');local a=f(p,mb.byName('lich'),10,x,y);a.never_act=true;a._checker_live_placed=true;_G.AGASS=a;return true")
                view=_set_vp(bridge.lua(CLEAN_VIEW % ('a==AGASS',GROUP_CENTER)))
                entry['assassin']=bridge.lua("local r=mb.row(AGASS);r.shader=AGASS.shader or false;return r")
                ps=bridge.shot('ag-assassin-'+label);cp,box=group_crop(view,ps,'ag-assassin-'+label,1)
                entry['assassin_view']=view;entry['assassin_crop']=rel(cp)
                entry['shader_negatives']=[]
                for key,shader,args in (('quad-hue-args','quad_hue','{}'),('other-shader','shadow_simulacrum','nil')):
                    bridge.lua("mb.clearAround(8);mb.place('multi-hued crystal','/data/general/npcs/crystal.lua',1,1);local a=mb.byName('multi-hued crystal');a.shader="+lua_value(shader)+";a.shader_args="+args+";mb.refresh();return true")
                    view=_set_vp(bridge.lua(CLEAN_VIEW % ('a._checker_live_placed',GROUP_CENTER)))
                    r=bridge.lua("local a=mb.byName('multi-hued crystal');local r=mb.row(a);r.shader=a.shader;r.shader_args=a.shader_args or false;return r")
                    ps=bridge.shot('ag-'+key+'-'+label);cp,box=group_crop(view,ps,'ag-'+key+'-'+label,1)
                    entry['shader_negatives'].append({'case':key,'row':r,'view':view,'crop':rel(cp)})
                bridge.lua("mb.clearAround(8);mb.place('shadow claw','/data/zones/keepsake-meadow/npcs.lua',-1,1,'SHADOW_CLAW');mb.place('shadow claw','/data/zones/keepsake-meadow/npcs.lua',1,1,'SHADOW_CASTER');return true")
                entry['shadow_pair']=[]
                for tile in (48,64,96):
                    bridge.lua(f'mb.setTile({tile});return true')
                    view=_set_vp(bridge.lua(CLEAN_VIEW % ('a._checker_live_placed',GROUP_CENTER)))
                    ps=bridge.shot(f'ag-shadow-pair-{label}-{tile}');cp,box=group_crop(view,ps,f'ag-shadow-pair-{label}-{tile}',1)
                    entry['shadow_pair'].append({'tile':tile,'view':view,'crop':rel(cp)})
                bridge.lua('mb.setTile(64);return true')
            elif kind == 'af_effect':
                # Read native actor effects; do not strip actor auras or particles.
                q = json.dumps(step[1])
                clean_view_actor(bridge, step[1])
                entry['snap'] = bridge.lua(f"local a=mb.byName({q});local n=0;for _ in pairs(a.shader_auras or {{}}) do n=n+1 end;"
                    "local t=a.replace_display or a;local au=0;local body={};for _,m in ipairs(t.add_mos or {}) do if m._isshaderaura then au=au+1 else body[#body+1]={image=m.image or false,display_h=m.display_h or false} end end;"
                    "local particles=0;for _ in pairs(a.__particles or {}) do particles=particles+1 end;"
                    "return {row=mb.row(a),actor_shader=a.shader or false,shader_auras=n,aura_entries=au,body_entries=body,"
                    "snowparticle=a.snowparticle and true or false,snow_registered=a.__particles and a.__particles[a.snowparticle] and true or false,particles=particles}")
                capture(bridge, 'af-effects-' + step[1].replace(' ', '-') + '-' + label, step[1], (48, 64, 96), entry)
            elif kind == 'blood_edge':
                # Execute the artifact's own special_on_hit proc on a genuinely bleeding target.
                # Retry its unmodified 15% roll; do not substitute a constructed summon or alter RNG.
                bridge.lua("return {n=mb.clearAround(6)}")
                bridge.lua("return mb.place('lich','/data/general/npcs/lich.lua',1,1)")
                entry['summon'] = bridge.lua(
                    "local p=game.player;local target=mb.byName('lich');target.cut_immune=0;target:setEffect(target.EFF_CUT,10,{power=1,src=p});assert(target:hasEffect(target.EFF_CUT),'no cut');"
                    "local list=game.zone.object_class:loadList('/data/general/objects/world-artifacts-far-east.lua',true,table.clone(game.zone.object_list));list.__real_type='object';local o=game.zone:makeEntityByName(game.level,list,'BLOODEDGE');assert(o,'no Blood-Edge');o:resolve();"
                    "local before={};for _,a in pairs(game.level.entities) do before[a]=true end;local m;local tries=0;"
                    "while not m and tries<100 do tries=tries+1;o.combat.special_on_hit.fct(o.combat,p,target);"
                    "for _,a in pairs(game.level.entities) do if not before[a] and a.summoner==p and a.subtype=='blood' then m=a end end end;assert(m,'proc made no summon');"
                    "m._checker_live_placed=true;m._checker_live_minion=true;m.never_act=true;mb.refresh();"
                    "local r=mb.row(m);r.localized_name=m.name;r.display_name=m:getName();r.summoner=m.summoner==p;r.summon_time=m.summon_time;r.party_member=game.party:hasMember(m) and true or false;"
                    "r.guards={ai=m.ai or false,ai_real=m.ai_real or false,ai_party=m.ai_state and m.ai_state.ai_party or false,autolevel=m.autolevel or false,"
                    "summoner_gain_exp=m.summoner_gain_exp or false,negative_status_effect_immune=m.negative_status_effect_immune or false,max_vim=m.max_vim,"
                    "exp_worth=m.exp_worth,silent_levelup=m.silent_levelup or false,life_rating=m.life_rating,body_keys={}};for k in pairs(m.add_mos[1]) do r.guards.body_keys[#r.guards.body_keys+1]=k end;"
                    "r.tries=tries;r.artifact=o.define_as or false;r.target_cut=target:hasEffect(target.EFF_CUT) and true or false;return r")
                if len(step) > 1 and step[1] == 'measure-only':
                    entry['measurement_only'] = True
                    record['steps'].append(entry)
                    continue
                entry['shots'] = []
                for tile in (48, 64, 96):
                    bridge.lua(f'mb.setTile({tile})')
                    view = _set_vp(bridge.lua(CLEAN_VIEW % ('a._checker_live_minion', GROUP_CENTER)))
                    entry.setdefault('views', []).append(view)
                    ps = bridge.shot(f'blood-edge-{label}-{tile}')
                    cp, box = group_crop(view, ps, f'blood-edge-{label}-{tile}', 1)
                    entry['shots'].append({'tile': tile, 'file': rel(ps), 'sha256': digest(ps), 'crop': rel(cp), 'crop_box': box})
                r = entry['summon']
                entry['ok'] = r['identify'] == r['rendered_token'] == 'animated-blood' and r['summoner'] and r['party_member'] and all(
                    len(v['rows']) == 1 and v['rows'][0]['can_see'] and v['rows'][0]['rendered_token'] == 'animated-blood' for v in entry['views'])
                bridge.lua('mb.setTile(64)')
            elif kind == 'multiply':
                # Hummerhorn Multiply (talents/misc/npcs.lua:56, can_multiply clone): the native clone must wear the same token.
                q = json.dumps(step[1], ensure_ascii=False)
                entry['before'] = bridge.lua(f"local a=mb.byName({q});return {{can_multiply=a.can_multiply or false,knows=a:knowTalent('T_MULTIPLY') and true or false}}")
                entry['cast'] = bridge.lua(
                    f"local a=mb.byName({q});a._checker_live_group=true;if not a:knowTalent('T_MULTIPLY') then a:learnTalent('T_MULTIPLY',true,1) end;"
                    "_G.MLV_BEFORE={};for _,e in pairs(game.level.entities) do _G.MLV_BEFORE[e]=true end;"
                    "local ok,err=pcall(a.forceUseTalent,a,'T_MULTIPLY',{ignore_energy=true,ignore_cd=true,no_talent_fail=true,silent=true});"
                    "local out={};for _,e in pairs(game.level.entities) do if not _G.MLV_BEFORE[e] and e.x then e._checker_live_placed=true;e._checker_live_minion=true;e.never_act=true;"
                    "pcall(function() game:checkerRefreshActor(e,'display') end);out[#out+1]=e end end;"
                    "mb.refresh();local rows={};for _,e in ipairs(out) do local r=mb.row(e);r.can_multiply=e.can_multiply or false;r.exp_worth=e.exp_worth;r.define_as_field=e.define_as or false;rows[#rows+1]=r end;"
                    "return {ok=ok,err=tostring(err),rows=rows,parent=mb.row(a)}")
                view = _set_vp(bridge.lua(CLEAN_VIEW % ("(a._checker_live_group or a._checker_live_minion)", GROUP_CENTER)))
                ps = bridge.shot(f'multiply-{label}')
                cp, box = group_crop(view, ps, f'multiply-{label}', 2)
                view['crop_box'] = box
                entry['view'] = view
                entry['shots'] = [{'file': rel(ps), 'sha256': digest(ps), 'crop': rel(cp)}]
                eid = EXPECT[step[1]]
                crow = entry['cast']['rows']
                entry['ok'] = bool(entry['cast']['ok']) and len(crow) >= 1 and all(r['identify'] == r['rendered_token'] == eid and r['explain'] == 'exact-identity' for r in crow) and len(view['rows']) == len(crow) + 1 and all(
                    r['can_see'] and r['identify'] == r['rendered_token'] == eid for r in view['rows'])
            elif kind == 'paradox':
                # Native makeParadoxClone (talents/chronomancy/chronomancer.lua:240) the way the Anomaly Clone talent uses it (a nearby creature,
                # clone added on a free grid); mode 'player' clones the hero as Timeline Threading does. Each case: shot with the clone, then the clone
                # expires through the native NPC:actBase summon_time countdown and a second shot shows the survivor alone.
                from PIL import Image
                entry['cases'] = []
                for key, nm, srcp, mode in step[1]:
                    c = {'key': key, 'name': nm, 'mode': mode}
                    try:
                        bridge.lua("return {n=mb.clearAround(6)}")
                        if mode.startswith('target'):
                            c['target_placed'] = bridge.lua(f"return mb.place({json.dumps(nm, ensure_ascii=False)},{json.dumps(srcp) if srcp else 'nil'},1,1,{json.dumps(mode.split(':',1)[1]) if ':' in mode else 'nil'})")
                            tget = f"mb.byName({json.dumps(nm, ensure_ascii=False)})"
                        else:
                            c['player_before'] = bridge.lua("return mb.row(game.player)")
                            tget = "game.player"
                        c['made'] = bridge.lua(
                            f"local p=game.player;local Map=require 'engine.Map';local a={tget};assert(a,'no target');a._checker_live_group=true;"
                            "local x,y=util.findFreeGrid(a.x,a.y,3,true,{[Map.ACTOR]=true});assert(x,'no grid');"
                            f"local mpc=getfenv(game.player:getTalentFromId('T_ANOMALY_TEMPORAL_CLONE').doAction).makeParadoxClone;assert(type(mpc)=='function','no makeParadoxClone');local m=mpc(p,a,{PARADOX_DUR});assert(m,'no clone');m.ai_state={{talent_in=2,ally_compassion=10}};"
                            "game.zone:addEntity(game.level,m,'actor',x,y);m._checker_live_placed=true;m._checker_live_minion=true;m._checker_live_clone=true;m.never_act=true;"
                            "pcall(function() game:checkerRefreshActor(m,'display') end);mb.refresh();"
                            "local r=mb.row(m);r.display_name=m:getName();r.summon_time=m.summon_time;r.summoner_is_target=(m.summoner==a);r.unique_field=m.unique or false;"
                            "r.exp_worth=m.exp_worth;r.ai=m.ai;r.ai_real=m.ai_real;r.max_level=m.max_level;r.level=m.level;"
                            "local t=mb.row(a);t.display_name=a:getName();return {clone=r,target=t}")
                        view = _set_vp(bridge.lua(CLEAN_VIEW % ("(a._checker_live_group or a._checker_live_minion)", GROUP_CENTER)))
                        c['view_rows'] = [[r['name'], r['identify'], r['rendered_token'], r['can_see'], r['screen']] for r in view['rows']]
                        c['hero'] = view['hero']
                        ps = bridge.shot(f'paradox-{key}-{label}')
                        sc = [r['screen'] for r in view['rows']] + [view['hero']['screen']]
                        tt = sc[0][2]
                        im = Image.open(ps).convert('RGB')
                        box = clamp_box((max(0, min(q[0] for q in sc) - tt), max(0, min(q[1] for q in sc) - tt),
                                         min(im.width, max(q[0] for q in sc) + 2 * tt), min(im.height, max(q[1] for q in sc) + 2 * tt)))
                        cp = CROPS / f'paradox-{key}-{label}-crop.png'
                        CROPS.mkdir(parents=True, exist_ok=True)
                        im.crop(box).save(cp)
                        c['shots'] = [{'file': rel(ps), 'sha256': digest(ps), 'crop': rel(cp), 'crop_box': box}]
                        c['expiry'] = bridge.lua(
                            "local m;for _,e in pairs(game.level.entities) do if e._checker_live_clone and e.x and e.summon_time then m=e end end;assert(m,'no clone');"
                            "local Map=require 'engine.Map';local n,st0=0,m.summon_time;local x,y=m.x,m.y;"
                            "while not m.dead and n<40 do n=n+1;mod.class.NPC.actBase(m) end;"
                            "mb.refresh();return {countdown_steps=n,summon_time_start=st0,dead=m.dead and true or false,dead_by_unsummon=m.dead_by_unsummon and true or false,"
                            "on_map_after=(x and game.level.map(x,y,Map.ACTOR)==m) and true or false}")
                        view2 = _set_vp(bridge.lua(CLEAN_VIEW % ("(a._checker_live_group or a._checker_live_minion)", GROUP_CENTER)))
                        c['after_rows'] = [[r['name'], r['identify'], r['rendered_token'], r['can_see']] for r in view2['rows']]
                        ps2 = bridge.shot(f'paradox-{key}-expired-{label}')
                        sc2 = [r['screen'] for r in view2['rows']] + [view2['hero']['screen']]
                        im2 = Image.open(ps2).convert('RGB')
                        box2 = clamp_box((max(0, min(q[0] for q in sc2) - tt), max(0, min(q[1] for q in sc2) - tt),
                                          min(im2.width, max(q[0] for q in sc2) + 2 * tt), min(im2.height, max(q[1] for q in sc2) + 2 * tt)))
                        cp2 = CROPS / f'paradox-{key}-expired-{label}-crop.png'
                        im2.crop(box2).save(cp2)
                        c['shots'].append({'file': rel(ps2), 'sha256': digest(ps2), 'crop': rel(cp2), 'crop_box': box2})
                        if mode == 'player':
                            c['player_after'] = bridge.lua("return mb.row(game.player)")
                    except Exception as exc:
                        c['error'] = str(exc)[:1200]
                        print('STEP ERROR paradox', key, str(exc)[:400], flush=True)
                    entry['cases'].append(c)
            elif kind == 'randboss':
                # Real GameState random_boss filter path (as the renegade-wyrmics vault): a non-unique native-tall wyrm stays native.
                nm = json.dumps(step[1], ensure_ascii=False)
                scheme = step[2] if len(step) > 2 else '#rng# the Flame Terror'
                entry['cleared'] = bridge.lua("return {n=mb.clearAround(6)}")  # the small start room is otherwise full
                entry['row'] = bridge.lua(
                    "local Map=require 'engine.Map';local p=game.player;"
                    f"local m=game.zone:makeEntity(game.level,'actor',{{name={nm},random_boss={{name_scheme={json.dumps(scheme)},nb_classes=1,rank=4,loot_quality='store',loot_quantity=1,ai_move='move_complex'}}}},nil,true);"
                    "assert(m and m.randboss,'no random boss');local mm=game.level.map;local x,y,bs;for cx=p.x-8,p.x+8 do for cy=p.y-6,p.y+6 do if cx>=1 and cy>=1 and cx<mm.w-1 and cy<mm.h-1 and (cx~=p.x or cy~=p.y) and not mm(cx,cy,Map.ACTOR) and not mm:checkEntity(cx,cy,Map.TERRAIN,'block_move',p) and mm.seens(cx,cy) then local d=(cx-p.x-3)^2+(cy-p.y-1)^2;if not bs or d<bs then x,y,bs=cx,cy,d end end end end;assert(x,'no free grid');"
                    "m._checker_live_placed=true;m.never_act=true;game.zone:addEntity(game.level,m,'actor',x,y);"
                    "pcall(function() p:resetCanSeeCache() end);mb.refresh();mb.focus(x,y);local r=mb.row(m);"
                    "r.randboss=m.randboss or false;r.unique=m.unique or false;r.define_as_field=m.define_as or false;r.rank=m.rank;return r")
                row = entry['row']
                rtag = step[1].replace(' ', '-')
                if CLEAN:
                    view = _set_vp(bridge.lua("local S;for _,a in pairs(game.level.entities) do if a.randboss and a._checker_live_placed then S=a end end;assert(S,'no random boss');" + CLEAN_VIEW % ("a==S", "S.x,S.y")))
                    row = bridge.lua("local S;for _,a in pairs(game.level.entities) do if a.randboss and a._checker_live_placed then S=a end end;local r=mb.row(S);r.randboss=S.randboss or false;"
                                     "r.unique=S.unique or false;r.rank=S.rank;r.can_see=game.player:canSee(S) and true or false;return r")
                    entry['row'] = row
                entry['native_ok'] = not row['rendered_token'] and not row['identify'] and not row['display_image']
                ps = bridge.shot(f'randboss-{rtag}-{label}')
                entry['shots'] = [{'file': rel(ps), 'sha256': digest(ps), 'crop': rel(crop(ps, row['screen'], f'randboss-{rtag}-{label}-crop', 3))}]
            elif kind == 'escort':
                # A fresh fire wyrm's own make_escort (added on tick end): the escort fire drakes wear the fire drake token.
                nm = json.dumps(step[1], ensure_ascii=False)
                entry['cleared'] = bridge.lua("return {n=mb.clearAround(6)}")
                bridge.lua("_G.MLV_BEFORE={};for _,a in pairs(game.level.entities) do _G.MLV_BEFORE[a]=true end;return true")
                entry['wyrm'] = bridge.lua(f"return mb.place({nm},{json.dumps(PLACE_SRC_BZ[step[1]])},-2,1)")
                esc = []
                for _ in range(12):
                    time.sleep(1)
                    esc = bridge.lua("local out={};for _,a in pairs(game.level.entities) do if not _G.MLV_BEFORE[a] and a.x and a.name=='fire drake' then "
                                     "a._checker_live_placed=true;a._checker_live_minion=true;a.never_act=true;pcall(function() game:checkerRefreshActor(a,'display') end);out[#out+1]=a end end;"
                                     "mb.refresh();local rows={};for _,a in ipairs(out) do local r=mb.row(a);r.define_as_field=a.define_as or false;rows[#rows+1]=r end;return rows")
                    if esc:
                        break
                entry['escorts'] = esc
                entry['ok'] = bool(esc) and all(r['identify'] == 'fire-drake' and r['rendered_token'] == 'fire-drake' for r in esc)
                wx, wy, wt = entry['wyrm']['screen']
                bridge.lua(f"mb.focus({entry['wyrm']['x']},{entry['wyrm']['y']})")
                ps = bridge.shot(f'escort-fire-drakes-{label}')
                entry['shots'] = [{'file': rel(ps), 'sha256': digest(ps), 'crop': rel(crop(ps, (wx, wy, wt), f'escort-fire-drakes-{label}-crop', 4))}]
            elif kind == 'lordskulls':
                # Negative: Lord of Skulls renames the minion ("Lord of Skulls (bone giant)"); it must fall back to native.
                entry['lord'] = bridge.lua(
                    "local m;for _,a in pairs(game.level.entities) do if a.is_bone_giant and a.x then m=a end end;assert(m,'no bone giant');"
                    "local before=m.name;m:setEffect(m.EFF_LORD_OF_SKULLS,1,{life=10,talents=1});mb.refresh();mb.focus(m.x,m.y);"
                    "local r=mb.row(m);r.name_before=before;r.name_after=m.name;r.lord_of_skulls=m.lord_of_skulls or false;r.is_bone_giant=m.is_bone_giant;return r")
                pl = bridge.shot(f'lord-of-skulls-{label}')
                row = entry['lord']
                entry['ok'] = (row['identify'] == False and row['rendered_token'] == False and bool(row.get('lord_of_skulls')))
                entry['shots'] = [{'file': rel(pl), 'sha256': digest(pl), 'crop': rel(crop(pl, row['screen'], f'lord-of-skulls-{label}-crop', 3))}]
            elif kind == 'vaultpaladin':
                entry['row'] = bridge.lua(
                    "local cap;local env=setmetatable({defineTile=function(c,f,o,a) if c=='S' then cap=a end end},"
                    "{__index=function(t,k) local v=rawget(_G,k);if v~=nil then return v end return function() end end});"
                    "local f=assert(loadfile('/data/maps/vaults/auto/greater/paladin-vs-vampire.lua'));setfenv(f,env);f();assert(cap,'no S tile');"
                    "local a=game.zone:finishEntity(game.level,'actor',cap);assert(a.name=='human sun-paladin');"
                    "local Map=require 'engine.Map';local p=game.player;local m=game.level.map;local bx,by,bs;"
                    "for x=p.x-6,p.x+6 do for y=p.y-4,p.y+4 do if x>=0 and y>=0 and x<m.w and y<m.h and not m(x,y,Map.ACTOR) and "
                    "not m:checkEntity(x,y,Map.TERRAIN,'block_move',p) and m.seens(x,y) and (x~=p.x or y~=p.y) then local d=(x-p.x-2)^2+(y-p.y)^2;"
                    "if not bs or d<bs then bx,by,bs=x,y,d end end end end;assert(bx);"
                    "a._checker_live_placed=true;a.never_act=true;game.zone:addEntity(game.level,a,'actor',bx,by);mb.refresh();mb.focus(bx,by);"
                    "local r=mb.row(a);r.fields={rank=a.rank,rarity=a.rarity or false,exp_worth=a.exp_worth,ai=a.ai,autolevel=a.autolevel,"
                    "size_category=a.size_category,hard_faction=a.hard_faction or false,positive_regen=a.positive_regen or false,"
                    "level_range={a.level_range[1],a.level_range[2] or false},life_rating=a.life_rating or false,define_as=a.define_as or false};return r")
                pv = bridge.shot(f'vault-paladin-{label}')
                entry['shots'] = [{'file': rel(pv), 'sha256': digest(pv), 'crop': rel(crop(pv, entry['row']['screen'], f'vault-paladin-{label}-crop', 3))}]
            elif kind == 'paladinfields':
                q = json.dumps(step[1], ensure_ascii=False)
                entry['fields'] = bridge.lua(
                    f"local a=mb.byName({q});local lr=a.level_range;return {{row=mb.row(a),define_as=a.define_as or false,rank=a.rank,rarity=a.rarity or false,"
                    "exp_worth=a.exp_worth,ai=a.ai,autolevel=a.autolevel,life_rating=a.life_rating,size_category=a.size_category,"
                    "level_range={lr and lr[1] or false,lr and lr[2] or false},faction=a.faction,desc=a.desc,unique=a.unique or false,"
                    "summoner=a.summoner and true or false}")
            elif kind == 'rampage':
                # Warmaster Gnarg's Berserker auto_class (level 35+) may learn Rampage. It is an effect, not a sustain:
                # teach the talent, run its action and record the effect, aura entries and token.
                q = json.dumps(step[1], ensure_ascii=False)
                RP = ("local a=mb.byName(%s);pcall(function() a:updateModdableTile() end);mb.refresh();mb.focus(a.x,a.y);"
                      "local n=0;for _ in pairs(a.shader_auras or {}) do n=n+1 end;"
                      "local t=a.replace_display or a;local au=0;for _,m in ipairs(t.add_mos or {}) do if m._isshaderaura then au=au+1 end end;"
                      "local fx={};for e in pairs(a.tmp or {}) do fx[#fx+1]=tostring(e) end;table.sort(fx);"
                      "return {row=mb.row(a),effects=fx,rampage=a:hasEffect(a.EFF_RAMPAGE) and true or false,shader_auras=n,aura_entries=au,"
                      "actor_shader=a.shader or false,type=a.type,subtype=a.subtype}") % q
                entry['before'] = bridge.lua(RP)
                entry['use'] = bridge.lua(f"local a=mb.byName({q});local res={{known=a:knowTalent('T_RAMPAGE') and true or false}};"
                                          "if not res.known then a:learnTalent('T_RAMPAGE',true,1);res.learned=true end;"
                                          "local t=a:getTalentFromId('T_RAMPAGE');local ok,err=pcall(t.action,a,t);res.ok=ok;res.err=tostring(err);return res")
                entry['during'] = bridge.lua(RP)
                p1 = bridge.shot(f'rampage-during-{label}')
                entry['shots'] = [{'file': rel(p1), 'sha256': digest(p1), 'crop': rel(crop(p1, entry['during']['row']['screen'], f'rampage-during-{label}-crop', 3))}]
                bridge.lua(f"local a=mb.byName({q});pcall(function() a:removeEffect(a.EFF_RAMPAGE,true,true) end);mb.refresh()")
                entry['ended'] = bridge.lua(RP)
            elif kind == 'stealth':
                # Orc assassin: native Stealth. Record the token while stealthed (hero in normal detection
                # range), while hidden (stealth boosted so the hero cannot see it) and after it is revealed.
                q = json.dumps(step[1], ensure_ascii=False)
                SS = ("local a=mb.byName(%s);pcall(function() game.player:resetCanSeeCache();a:resetCanSeeCacheOf() end);mb.refresh();pcall(function() game.player:resetCanSeeCache();a:resetCanSeeCacheOf() end);mb.focus(a.x,a.y);local r=mb.row(a);"
                      "r.stealth_attr=a:attr('stealth') or 0;r.stealth_active=a:isTalentActive('T_STEALTH') and true or false;"
                      "r.player_can_see=game.player:canSee(a) and true or false;"
                      "r.token_state=a._checker_token and a._checker_token.id or false;"
                      "local cnt=0;for _,e in pairs(game.level.entities) do if e~=game.player and e.x and e._checker_token and not game.player:canSee(e) then cnt=cnt+1 end end;"
                      "r.hidden_actors_with_token_state=cnt;return r") % q
                if len(step) > 2 and step[2] == 'teach':
                    entry['taught'] = bridge.lua(f"local a=mb.byName({q});local had=a:knowTalent('T_STEALTH') and true or false;if not had then a:learnTalent('T_STEALTH',true,3) end;return {{had_natively=had,now=a:knowTalent('T_STEALTH') and true or false}}")
                entry['before'] = bridge.lua(SS)
                entry['use'] = bridge.lua(f"local a=mb.byName({q});local was=a:isTalentActive('T_STEALTH') and true or false;local ok,err=true,'nil';if not was then ok,err=pcall(function() a:forceUseTalent('T_STEALTH',{{ignore_energy=true,ignore_cd=true,no_talent_fail=true,silent=true}}) end) end;return {{ok=ok,err=tostring(err),known=a:knowTalent('T_STEALTH') and true or false,active_at_birth=was}}")
                entry['stealthed'] = bridge.lua(SS)
                p1 = bridge.shot(f'stealth-active-{label}-{EXPECT.get(step[1], "x")}')
                bridge.lua(f"local a=mb.byName({q});a._checker_live_stealth_boost=a:addTemporaryValue('stealth',1000);mb.refresh()")
                entry['hidden'] = bridge.lua(SS)
                p2 = bridge.shot(f'stealth-hidden-{label}-{EXPECT.get(step[1], "x")}')
                bridge.lua(f"local a=mb.byName({q});if a._checker_live_stealth_boost then a:removeTemporaryValue('stealth',a._checker_live_stealth_boost);a._checker_live_stealth_boost=nil end;pcall(function() a:forceUseTalent('T_STEALTH',{{ignore_energy=true,ignore_cd=true,no_talent_fail=true,silent=true}}) end);mb.refresh()")
                entry['revealed'] = bridge.lua(SS)
                p3 = bridge.shot(f'stealth-revealed-{label}-{EXPECT.get(step[1], "x")}')
                sc = entry['stealthed']['screen']
                entry['shots'] = [{'file': rel(p), 'sha256': digest(p), 'crop': rel(crop(p, sc, f'stealth-{n}-{label}-{EXPECT.get(step[1], "x")}-crop', 3))}
                                  for n, p in (('active', p1), ('hidden', p2), ('revealed', p3))]
            elif kind == 'urhrok':
                # Rak'shor: force Flame of Urh'Rok (teach it if the fixture-level actor lacks it), record the
                # display, then end it and record that the token returns.
                q = json.dumps(step[1], ensure_ascii=False)
                UR = ("local a=mb.byName(%s);pcall(function() a:updateModdableTile() end);mb.refresh();mb.focus(a.x,a.y);local r=mb.row(a);"
                      "return {row=r,type=a.type,subtype=a.subtype,old_type=a.__old_type or false,image=a.image,"
                      "sustained=a:isTalentActive('T_FLAME_OF_URH_ROK') and true or false,known=a:knowTalent('T_FLAME_OF_URH_ROK') and true or false,"
                      "urh_rok_form=a.urh_rok_form or false,particles=(function() local o={};for ps in pairs(a.__particles or {}) do o[#o+1]=tostring(ps.def) end table.sort(o);return o end)()}") % q
                entry['before'] = bridge.lua(UR)
                entry['learn'] = bridge.lua(f"local a=mb.byName({q});if not a:knowTalent('T_FLAME_OF_URH_ROK') then a:learnTalent('T_FLAME_OF_URH_ROK',true,1) end;return {{known=a:knowTalent('T_FLAME_OF_URH_ROK') and true or false}}")
                FT = "{ignore_energy=true,ignore_cd=true,no_equilibrium_fail=true,no_talent_fail=true,silent=true}"
                entry['activate'] = bridge.lua(f"local a=mb.byName({q});local ok,err=pcall(function() a:forceUseTalent('T_FLAME_OF_URH_ROK',{FT}) end);return {{ok=ok,err=tostring(err)}}")
                entry['during'] = bridge.lua(UR)
                p1 = bridge.shot(f'urhrok-during-{label}')
                entry['deactivate'] = bridge.lua(f"local a=mb.byName({q});local ok,err=pcall(function() a:forceUseTalent('T_FLAME_OF_URH_ROK',{FT}) end);return {{ok=ok,err=tostring(err)}}")
                entry['after'] = bridge.lua(UR)
                p2 = bridge.shot(f'urhrok-after-{label}')
                entry['shots'] = [{'file': rel(p1), 'sha256': digest(p1), 'crop': rel(crop(p1, entry['during']['row']['screen'], f'urhrok-during-{label}-crop', 3))},
                                  {'file': rel(p2), 'sha256': digest(p2), 'crop': rel(crop(p2, entry['after']['row']['screen'], f'urhrok-after-{label}-crop', 3))}]
            elif kind == 'forcesus':
                # Force a sustain (learned if needed), record the display while active and after it ends.
                q = json.dumps(step[1], ensure_ascii=False)
                tid = step[2]
                FS = ("local a=mb.byName(%s);pcall(function() a:updateModdableTile() end);mb.refresh();mb.focus(a.x,a.y);local r=mb.row(a);"
                      "local n=0;for _ in pairs(a.shader_auras or {}) do n=n+1 end;"
                      "local t=a.replace_display or a;local L={};for _,m in ipairs(t.add_mos or {}) do L[#L+1]=(m._isshaderaura and 'AURA:' or '')..tostring(m.image)..'/'..tostring(m.shader or '') end;"
                      "return {row=r,sustained=a:isTalentActive('%s') and true or false,known=a:knowTalent('%s') and true or false,"
                      "actor_shader=a.shader or false,shader_auras=n,add_mos=L,type=a.type,subtype=a.subtype}") % (q, tid, tid)
                FT = "{ignore_energy=true,ignore_cd=true,no_equilibrium_fail=true,no_talent_fail=true,silent=true}"
                entry['before'] = bridge.lua(FS)
                entry['learn'] = bridge.lua(f"local a=mb.byName({q});if not a:knowTalent('{tid}') then a:learnTalent('{tid}',true,1) end;return {{known=a:knowTalent('{tid}') and true or false}}")
                entry['activate'] = bridge.lua(f"local a=mb.byName({q});local ok,err=pcall(function() a:forceUseTalent('{tid}',{FT}) end);return {{ok=ok,err=tostring(err)}}")
                entry['during'] = bridge.lua(FS)
                p1 = bridge.shot(f'forcesus-during-{label}')
                # Invisibility is a timed effect (not a sustain): end it explicitly; a real sustain is toggled off.
                entry['deactivate'] = bridge.lua(f"local a=mb.byName({q});local fx={{}};for e in pairs(a.tmp or {{}}) do fx[#fx+1]=tostring(e) end;table.sort(fx);"
                                                 "local ok,err=pcall(function() if a:isTalentActive('%s') then a:forceUseTalent('%s',%s) end;"
                                                 "for _,eid in ipairs{'EFF_INVISIBILITY','EFF_GREATER_INVISIBILITY'} do if a[eid] and a:hasEffect(a[eid]) then a:removeEffect(a[eid],true,true) end end end);"
                                                 "local fx2={};for e in pairs(a.tmp or {}) do fx2[#fx2+1]=tostring(e) end;table.sort(fx2);"
                                                 "return {ok=ok,err=tostring(err),effects_before=fx,effects_after=fx2}" % (tid, tid, FT))
                entry['after'] = bridge.lua(FS)
                p2 = bridge.shot(f'forcesus-after-{label}')
                entry['shots'] = [{'file': rel(p1), 'sha256': digest(p1), 'crop': rel(crop(p1, entry['during']['row']['screen'], f'forcesus-during-{label}-crop', 3))},
                                  {'file': rel(p2), 'sha256': digest(p2), 'crop': rel(crop(p2, entry['after']['row']['screen'], f'forcesus-after-{label}-crop', 3))}]
            elif kind == 'thoughtform':
                # Mindworm: learn/activate Thought-Form: Warrior, record the summon and the caster's token.
                q = json.dumps(step[1], ensure_ascii=False)
                TF = ("local a=mb.byName(%s);pcall(function() a:updateModdableTile() end);mb.refresh();mb.focus(a.x,a.y);"
                      "local sm={};for _,e in pairs(game.level.entities) do if e.summoner==a and e.x then sm[#sm+1]={name=e.name,type=e.type,subtype=e.subtype,image=e.image,x=e.x,y=e.y,row=mb.row(e)} end end;"
                      "return {caster=mb.row(a),summons=sm,active=a:isTalentActive('T_TF_WARRIOR') and true or false}") % q
                FT = "{ignore_energy=true,ignore_cd=true,no_talent_fail=true,silent=true}"
                entry['before'] = bridge.lua(TF)
                entry['learn'] = bridge.lua(f"local a=mb.byName({q});for _,t in ipairs{{'T_THOUGHT_FORMS','T_TF_WARRIOR'}} do if not a:knowTalent(t) then a:learnTalent(t,true,1) end end;a.psi=a.max_psi or 100;return {{known=a:knowTalent('T_TF_WARRIOR') and true or false}}")
                entry['activate'] = bridge.lua(f"local a=mb.byName({q});local ok,err=pcall(function() a:forceUseTalent('T_TF_WARRIOR',{FT}) end);return {{ok=ok,err=tostring(err)}}")
                entry['during'] = bridge.lua(TF)
                p1 = bridge.shot(f'thoughtform-during-{label}')
                entry['shots'] = [{'file': rel(p1), 'sha256': digest(p1), 'crop': rel(crop(p1, entry['during']['caster']['screen'], f'thoughtform-during-{label}-crop', 3))}]
                bridge.lua(f"local a=mb.byName({q});pcall(function() a:forceUseTalent('T_TF_WARRIOR',{FT}) end);mb.refresh()")
                entry['after'] = bridge.lua(TF)
            elif kind == 'drakesummon':
                # Summons that reuse the zone drake's name/type/PNG: Wyrmic Fire Drake (summon-distance.lua:850,
                # image set) or Grand Arrival hatchling (:786, image set). No define_as, summoner set.
                hatch = step[1] == 'grand'
                nm, img = ('fire drake hatchling', 'npc/dragon_fire_fire_drake_hatchling.png') if hatch else ('fire drake', 'npc/dragon_fire_fire_drake.png')
                Z = ("local Map=require 'engine.Map';local p=game.player;"
                     f"local m=require('mod.class.NPC').new{{type='dragon',subtype='fire',display='{'d' if hatch else 'D'}',color=colors.RED,image='{img}',name='{nm}',"
                     "faction=p.faction,desc='A mighty fire drake.',autolevel='none',stats={str=0,dex=0,con=0,cun=0,wil=0,mag=0},"
                     "level_range={p.level,p.level},exp_worth=0,max_life=100,life_rating=12,infravision=10,combat_armor=0,combat_def=0,"
                     "summoner=p,summoner_gain_exp=true,wild_gift_summon=true,summon_time=10};"
                     "m:resolve();m:resolve(nil,true);m.summoner=p;"
                     "local x,y=util.findFreeGrid(p.x+2,p.y+1,6,true,{[Map.ACTOR]=true});assert(x,'no free grid');"
                     "m._checker_live_placed=true;m._checker_live_minion=true;m.never_act=true;game.zone:addEntity(game.level,m,'actor',x,y);"
                     "mb.refresh();mb.focus(x,y);local r=mb.row(m);r.summoner=m.summoner==p;r.define_as_field=m.define_as or false;r.summon_name=m.name;return r")
                entry['summon'] = bridge.lua(Z)
                ps = bridge.shot(f'drakesummon-{step[1]}-{label}')
                entry['shots'] = [{'file': rel(ps), 'sha256': digest(ps), 'crop': rel(crop(ps, entry['summon']['screen'], f'drakesummon-{step[1]}-{label}-crop', 3))}]
            elif kind == 'wormsummon':
                # Worm Rot / Infestation summon (talents/corruptions/rot.lua:62): same name/type/image
                # as CARRION_WORM_MASS but no define_as and a summoner. Zone define_as one for contrast.
                Z = ("local Map=require 'engine.Map';local p=game.player;"
                     "local m=require('mod.class.NPC').new{type='vermin',subtype='worms',display='w',color=colors.SANDY_BROWN,"
                     "image='npc/vermin_worms_carrion_worm_mass.png',name='carrion worm mass',faction=p.faction,autolevel='none',"
                     "level_range={1,p.level},exp_worth=0,max_life=7,summoner=p,summoner_gain_exp=true,carrion_worm=true,summon_time=5};"
                     "m:resolve();m:resolve(nil,true);m.summoner=p;"
                     "local x,y=util.findFreeGrid(p.x+2,p.y+1,6,true,{[Map.ACTOR]=true});assert(x,'no free grid');"
                     "m._checker_live_placed=true;m._checker_live_minion=true;m.never_act=true;game.zone:addEntity(game.level,m,'actor',x,y);"
                     "mb.refresh();mb.focus(x,y);local r=mb.row(m);r.summoner=m.summoner==p;r.define_as_field=m.define_as or false;return r")
                entry['summon'] = bridge.lua(Z)
                entry['summon_native_ok'] = not entry['summon']['rendered_token'] and not entry['summon']['identify']
                entry['zone_mapped'] = bridge.lua("return mb.place('carrion worm mass','/data/general/npcs/vermin.lua',-2,1,'CARRION_WORM_MASS')")
                ps = bridge.shot(f'wormsummon-{label}')
                entry['shots'] = [{'file': rel(ps), 'sha256': digest(ps), 'crop': rel(crop(ps, entry['summon']['screen'], f'wormsummon-{label}-crop', 3))}]
            elif kind == 'gc':
                # Grand Corruptor: Flame of Urh'Rok is sustained from birth (type demon/major,
                # __old_type set). Record, deactivate the sustain, re-record.
                q = json.dumps(step[1], ensure_ascii=False)
                snap = ("local a=mb.byName(%s);mb.focus(a.x,a.y);local r=mb.row(a);"
                        "return {row=r,type=a.type,subtype=a.subtype,old_type=a.__old_type or false,"
                        "sustained=a:isTalentActive('T_FLAME_OF_URH_ROK') and true or false}") % q
                entry['before'] = bridge.lua(snap)
                entry['deactivate'] = bridge.lua(
                    f"local a=mb.byName({q});local ok,err=pcall(function() a:forceUseTalent('T_FLAME_OF_URH_ROK',"
                    "{ignore_energy=true,ignore_cd=true,no_equilibrium_fail=true,silent=true}) end);"
                    "return {ok=ok,err=tostring(err)}")
                entry['after'] = bridge.lua(snap)
                pgc = bridge.shot(f'gc-after-deactivate-{label}')
                entry['shots'] = [{'file': rel(pgc), 'sha256': digest(pgc),
                                   'crop': rel(crop(pgc, entry['after']['row']['screen'], f'gc-after-deactivate-{label}-crop', 3))}]
            elif kind == 'toggle_again':
                # Second Native->Refined cycle (regression check for the
                # native-tall shader-aura fix 32f4ec5): off, on, off, on.
                actor = step[1]
                sfx = step[2] if len(step) > 2 else ''
                q = json.dumps(actor, ensure_ascii=False)
                entry['off'] = bridge.lua(f"mb.tokens(false);local a=mb.byName({q});mb.focus(a.x,a.y);"
                                          "local rows={};for _,r in ipairs(mb.find()) do if r.rendered_token then rows[#rows+1]=r end end;"
                                          "return {enabled=game:checkerTokensEnabled(),row=mb.row(a),still_mapped=#rows}")
                p1 = bridge.shot(f'toggle2-native{sfx}-{label}')
                entry['on'] = bridge.lua(f"mb.tokens(true);local a=mb.byName({q});mb.focus(a.x,a.y);"
                                         "return {enabled=game:checkerTokensEnabled(),row=mb.row(a)}")
                time.sleep(3)
                entry['on_later'] = bridge.lua(f"local a=mb.byName({q});mb.focus(a.x,a.y);return mb.row(a)")
                p2 = bridge.shot(f'toggle2-refined{sfx}-{label}')
                row = entry['on_later']
                entry['shots'] = [{'file': rel(p1), 'sha256': digest(p1), 'crop': rel(crop(p1, row['screen'], f'toggle2-native{sfx}-{label}-crop', 3))},
                                  {'file': rel(p2), 'sha256': digest(p2), 'crop': rel(crop(p2, row['screen'], f'toggle2-refined{sfx}-{label}-crop', 3))}]
            elif kind == 'settle':
                # Diagnostic: does the token survive after the actor has had
                # time (real seconds, several frames) to settle? Records the
                # identity/add_mos at t=0 and after 4 s, plus a shot.
                q = json.dumps(step[1], ensure_ascii=False)
                entry['t0'] = bridge.lua(f"local a=mb.byName({q});mb.focus(a.x,a.y);return mb.row(a)")
                time.sleep(4)
                entry['t4'] = bridge.lua(f"local a=mb.byName({q});mb.focus(a.x,a.y);return mb.row(a)")
                p = bridge.shot(f'settle-{label}-{EXPECT.get(step[1], "x")}')
                entry['shots'] = [{'file': rel(p), 'sha256': digest(p), 'crop': rel(crop(p, entry['t4']['screen'], f'settle-{label}-{EXPECT.get(step[1], "x")}-crop', 3))}]
            elif kind == 'clean_place':
                # Clear the surroundings, place the actor, then drop any escort
                # that came with it so the crop shows only the token under test.
                actor, tiles = step[1], step[2]
                q = json.dumps(actor, ensure_ascii=False)
                entry['cleared'] = bridge.lua("return {n=mb.clearAround(6)}")
                entry['row'] = bridge.lua(f"local pr;for _,p in pairs(game.zone.npc_list) do if type(p)=='table' and p.name=={q} then pr=p end end;"
                                          "local esc=pr.make_escort;pr.make_escort=nil;local r=mb.place("+q+",nil,1,1);pr.make_escort=esc;local keep=mb.byName("+q+");"
                                          "local rm={};for _,a in pairs(game.level.entities) do if a~=game.player and a~=keep and a.x then rm[#rm+1]=a end end;"
                                          "for _,a in ipairs(rm) do game.level.map:remove(a.x,a.y,require('engine.Map').ACTOR);game.level:removeEntity(a,true) end;"
                                          "mb.refresh();r.escorts_removed=#rm;return r")
                entry['found'] = True
                capture(bridge, f"{EXPECT.get(actor) or actor.replace(' ', '-')}-placed-clean-{label}", actor, tiles, entry)
            elif kind == 'norgan':
                # Norgan joins the party in the real quest via
                # game.party:addMember{control="order",type="squadmate"}.
                # Check the token as a placed NPC, then again after joining;
                # the player's own token row must not change.
                q = json.dumps('Norgan')
                entry['player_before'] = bridge.lua("return mb.row(game.player)")
                entry['row'] = bridge.lua(f"return mb.place({q},nil,1,1)")
                capture(bridge, 'norgan-placed-npc-' + label, 'Norgan', (48, 64, 96), entry)
                entry['party'] = bridge.lua(
                    f"local a=mb.byName({q});game.party:addMember(a,{{control='order',type='squadmate',title='Norgan',"
                    "orders={leash=true,anchor=true}});mb.refresh();mb.focus(a.x,a.y);"
                    "return {row=mb.row(a),member=game.party:hasMember(a) and true or false,"
                    "control=game.party.members[a] and game.party.members[a].control or false,"
                    "player_is_player=(game.player~=a),player=mb.row(game.player)}")
                entry['party_shots'] = []
                for t in (48, 64, 96):
                    r = bridge.lua(f"mb.setTile({t});local a=mb.byName({q});mb.focus(a.x,a.y);return mb.row(a)")
                    nm = f'norgan-party-member-{label}-{t}'
                    p = bridge.shot(nm)
                    c = crop(p, r['screen'], nm + '-crop')
                    entry['party_shots'].append({'tile': t, 'file': rel(p), 'sha256': digest(p), 'crop': rel(c), 'row': r})
                entry['player_after'] = bridge.lua("mb.setTile(64);return mb.row(game.player)")
                entry['player_unchanged'] = (entry['player_before']['rendered_token'] == entry['player_after']['rendered_token']
                                             and entry['player_before']['display_image'] == entry['player_after']['display_image']
                                             and entry['player_before']['identify'] == entry['player_after']['identify'])
            elif kind == 'wound':
                row = bridge.lua(f"local r=mb.wound({json.dumps(step[1], ensure_ascii=False)},.45);local a=mb.byName({json.dumps(step[1], ensure_ascii=False)});mb.focus(a.x,a.y);return mb.row(a)")
                p = bridge.shot(f'wound-{label}')
                entry['row'] = row
                entry['shots'] = [{'file': rel(p), 'sha256': digest(p), 'crop': rel(crop(p, row['screen'], f'wound-{label}-crop'))}]
            elif kind in ('friendly', 'neutral'):
                q = json.dumps(step[1], ensure_ascii=False)
                faction = 'game.player.faction' if kind == 'friendly' else "'neutral'"
                row = bridge.lua(f"local a=mb.byName({q});a._checker_live_faction=a.faction;a.faction={faction};"
                                 "mb.refresh();mb.focus(a.x,a.y);return mb.row(a)")
                p = bridge.shot(f'{kind}-{label}')
                entry['row'] = row
                entry['shots'] = [{'file': rel(p), 'sha256': digest(p), 'crop': rel(crop(p, row['screen'], f'{kind}-{label}-crop'))}]
                bridge.lua(f"local a=mb.byName({q});a.faction=a._checker_live_faction;a._checker_live_faction=nil;mb.refresh()")
            elif kind == 'reveal':
                # Natively stealthy body (skeleton assassin) placed unseen: drop Stealth, then capture 48/64/96 (rows record can_see).
                q = json.dumps(step[1], ensure_ascii=False)
                entry['revealed'] = bridge.lua(
                    f"local a=mb.byName({q});local was=a:isTalentActive('T_STEALTH') and true or false;"
                    "if was then pcall(function() a:forceUseTalent('T_STEALTH',{ignore_energy=true,ignore_cd=true,no_talent_fail=true,silent=true}) end) end;"
                    "pcall(function() game.player:resetCanSeeCache();a:resetCanSeeCacheOf() end);mb.refresh();"
                    "return {was_stealthed=was,now_stealthed=a:isTalentActive('T_STEALTH') and true or false,can_see=game.player:canSee(a) and true or false}")
                capture(bridge, f"{EXPECT.get(step[1]) or step[1].replace(' ', '-')}-revealed-{label}", step[1], step[2], entry)
            elif kind == 'hide':
                q = json.dumps(step[1], ensure_ascii=False)
                row = bridge.lua(f"mb.invisible({q});local a=mb.byName({q});mb.focus(a.x,a.y);return mb.row(a)")
                p = bridge.shot(f'hidden-invisible-{label}')
                entry['row'] = row
                entry['shots'] = [{'file': rel(p), 'sha256': digest(p), 'crop': rel(crop(p, row['screen'], f'hidden-invisible-{label}-crop'))}]
                entry['restored'] = bridge.lua(f"return mb.invisible({q},true)")
            elif kind == 'atamathon_fallback':
                # Confirm the documented nicer_tiles-off native-icon fallback
                # (evidence/monster-batch-e-20260929/source-contracts.json,
                # Atamathon's fallback_caveat): resolvers.nice_tile resolves
                # engine.Map.tiles.nicer_tiles at entity-creation time, so a
                # *fresh* placement made while it is off is required -- the
                # already-placed refined instance above keeps its own
                # already-resolved image. Flip off, place a second instance,
                # capture and assert the checker declines it and its actor.image
                # is the native single icon, then restore nicer_tiles and clean
                # up the extra instance so it cannot confuse a later step.
                actor = step[1]
                q = json.dumps(actor, ensure_ascii=False)
                before = bridge.lua("return {nicer_tiles=require('engine.Map').tiles.nicer_tiles}")
                entry['nicer_tiles_before'] = before['nicer_tiles']
                bridge.lua("require('engine.Map').tiles.nicer_tiles=false")
                fb = bridge.lua(f"local r=mb.place({q},nil,-2,1);r._fallback=true;return r")
                p = bridge.shot(f'atamathon-fallback-native-{label}')
                entry['fallback_row'] = fb
                entry['fallback_ok'] = (fb['image'] == 'npc/atamathon.png' and not fb['identify']
                                        and fb['add_mos'] in (False, []))
                entry['shots'] = [{'file': rel(p), 'sha256': digest(p),
                                   'crop': rel(crop(p, fb['screen'], f'atamathon-fallback-native-{label}-crop'))}]
                bridge.lua("require('engine.Map').tiles.nicer_tiles=true;"
                          "local removed=0;for _,a in pairs(game.level.entities) do "
                          f"if a.x and a.name=={q} and a._checker_live_placed and a.image=='npc/atamathon.png' then "
                          "game.level.map:remove(a.x,a.y,require('engine.Map').ACTOR);game.level:removeEntity(a,true);removed=removed+1 end end;"
                          "mb.refresh();return {removed=removed}")
            elif kind == 'unseen':
                row = bridge.lua("local best;for _,a in pairs(game.level.entities) do if a.x and a~=game.player and a._checker_token "
                                 "and not game.level.map.seens(a.x,a.y) and (not best or a.name<best.name) then best=a end end;"
                                 "if not best then return {found=false} end;mb.focus(best.x,best.y);return {found=true,row=mb.row(best)}")
                entry.update(row)
                if row['found']:
                    p = bridge.shot(f'unseen-out-of-fov-{label}')
                    entry['shots'] = [{'file': rel(p), 'sha256': digest(p), 'crop': rel(crop(p, row['row']['screen'], f'unseen-out-of-fov-{label}-crop', 3))}]
            elif kind == 'midstart':
                # Lineup only: move the hero to the free, visible cell nearest the map centre with the most free
                # neighbours (away from the edge), light the surroundings, then let the lineup spread around it.
                entry['start'] = bridge.lua(
                    "local Map=require 'engine.Map';local m=game.level.map;local p=game.player;local best,bs;"
                    "local function free(x,y) return x>=1 and y>=1 and x<m.w-1 and y<m.h-1 and not m(x,y,Map.ACTOR) and not m:checkEntity(x,y,Map.TERRAIN,'block_move',p) and not m:checkEntity(x,y,Map.TERRAIN,'change_level') end;"
                    "for x=8,m.w-9 do for y=6,m.h-7 do if free(x,y) then local n=0;for dx=-6,6 do for dy=-4,4 do if free(x+dx,y+dy) then n=n+1 end end end;"
                    "local sc=n*100-((x-m.w/2)^2+(y-m.h/2)^2)*0.01;if not bs or sc>bs then best,bs=(x..','..y),sc;p._checker_mid={x,y,n} end end end end;"
                    "local x,y=p._checker_mid[1],p._checker_mid[2];p:move(x,y,true);"
                    "for dx=-9,9 do for dy=-6,6 do local a,b=x+dx,y+dy;if a>=0 and b>=0 and a<m.w and b<m.h then pcall(function() m.lites(a,b,true);m.remembers(a,b,true) end) end end end;"
                    "mb.refresh();mb.focus(x,y);return {x=x,y=y,free_cells_in_view=p._checker_mid[3],map_w=m.w,map_h=m.h}")
            elif kind == 'lineup':
                # ('lineup',) keeps the original skeleton-family default (batch
                # A/B/C); ('lineup', prefix, names) picks the file prefix and
                # the exact roster (batch D's six-ant / six-jelly rows).
                prefix = step[1] if len(step) > 1 else 'skeleton'
                roster = step[2] if len(step) > 2 else LINEUP
                entry['cleared'] = bridge.lua("return {n=mb.clearAround(6)}")
                rows = []
                offsets = step[3] if len(step) > 3 else [(-3, 1), (-2, 1), (-1, 1), (1, 1), (2, 1), (3, 1)]
                for name, (dx, dy) in zip(roster, offsets):
                    src = 'nil'
                    if isinstance(name, (tuple, list)):
                        name, srcpath = name
                        src = json.dumps(srcpath) if srcpath else 'nil'
                    rows.append(bridge.lua(f"return mb.place({json.dumps(name, ensure_ascii=False)},{src},{dx},{dy})"))
                if len(step) > 4 and step[4] == 'reveal':
                    # Birth sustains (Stealth) hide the placed assassins/spider from the hero; drop Stealth so the row is readable.
                    entry['revealed'] = bridge.lua(
                        "local out={};for _,a in pairs(game.level.entities) do if a~=game.player and a._checker_live_placed and a:isTalentActive('T_STEALTH') then "
                        "pcall(function() a:forceUseTalent('T_STEALTH',{ignore_energy=true,ignore_cd=true,no_talent_fail=true,silent=true}) end);"
                        "out[#out+1]={a.name,a:isTalentActive('T_STEALTH') and true or false} end end;"
                        "pcall(function() game.player:resetCanSeeCache() end);mb.refresh();mb.focus(game.player.x,game.player.y);return out")
                    entry['rows_after'] = bridge.lua("local o={};for _,r in ipairs(mb.find()) do if r.placed then o[#o+1]={r.name,r.identify,r.rendered_token,r.can_see,r.x,r.y} end end;return o")
                entry['rows'] = rows
                entry['shots'] = []
                for t in (48, 64, 96):
                    r = bridge.lua(f"mb.setTile({t});mb.focus(game.player.x,game.player.y);return mb.row(game.player)")
                    if CLEAN:
                        view = clean_view_placed(bridge)
                        p = bridge.shot(f'{prefix}-lineup-placed-{label}-{t}')
                        from PIL import Image
                        sc = [q['screen'] for q in view['rows']]
                        im = Image.open(p).convert('RGB')
                        box = clamp_box((max(0, min(c[0] for c in sc) - t // 2), max(0, min(c[1] for c in sc) - t), min(im.width, max(c[0] for c in sc) + t + t // 2),
                                         min(im.height, max(c[1] for c in sc) + t + t // 2)))
                        c = CROPS / f'{prefix}-lineup-placed-{label}-{t}-crop.png'
                        CROPS.mkdir(parents=True, exist_ok=True)
                        im.crop(box).save(c)
                        entry['shots'].append({'tile': t, 'file': rel(p), 'sha256': digest(p), 'crop': rel(c), 'crop_box': box, 'vp': view['vp'],
                                               'all_inside_viewport': all(q['screen'][0] >= view['vp'][0] and q['screen'][1] >= view['vp'][1] and q['screen'][0] + t <= view['vp'][0] + view['vp'][2] and q['screen'][1] + t <= view['vp'][1] + view['vp'][3] for q in view['rows']),
                                               'seen_rows': [[q['name'], q['identify'], q['rendered_token'], q['can_see'], q['screen']] for q in view['rows']]})
                        continue
                    p = bridge.shot(f'{prefix}-lineup-placed-{label}-{t}')
                    x, y, tt = r['screen']
                    c = crop(p, (x, y, tt), f'{prefix}-lineup-placed-{label}-{t}-crop', 4)
                    entry['shots'].append({'tile': t, 'file': rel(p), 'sha256': digest(p), 'crop': rel(c)})
                bridge.lua('mb.setTile(64)')
            elif kind == 'layer_grid':
                # 1.25x layered small-tile trial: place every trial body, then
                # capture the identical frame with the single trial flag off
                # and on at all three sizes. 64/96 must be pixel-identical; 48
                # must differ. Only region crops are kept (no full screenshots).
                from PIL import Image, ImageChops
                prefix = step[1] if len(step) > 1 else 'layer'
                entry['cleared'] = bridge.lua("return {n=mb.clearAround(12)}")
                rows = []
                for (name, src, das, tid), (dx, dy) in zip(LAYER_CASES, LAYER_POS):
                    s = json.dumps(src) if src else 'nil'
                    d = json.dumps(das) if das else 'nil'
                    rows.append(bridge.lua(
                        f"return mb.place({json.dumps(name, ensure_ascii=False)},{s},{dx},{dy},{d})"))
                entry['rows'] = rows
                entry['revealed'] = bridge.lua(
                    "local out={};for _,a in pairs(game.level.entities) do if a~=game.player and a._checker_live_placed and a:isTalentActive('T_STEALTH') then "
                    "pcall(function() a:forceUseTalent('T_STEALTH',{ignore_energy=true,ignore_cd=true,no_talent_fail=true,silent=true}) end);out[#out+1]=a.name end end;"
                    "pcall(function() game.player:resetCanSeeCache() end);mb.refresh();return out")
                entry['special'] = bridge.lua(
                    "local w=mb.byName('orc warrior');if w then w.life=math.max(1,math.floor(w.max_life*0.5)) end;"
                    "local s=mb.byName('skeleton warrior');if s then s.damage_shield=40;s.damage_shield_absorb=10;s.damage_shield_absorb_max=40 end;"
                    "local b=mb.byName('Ungolë');if b then b.rank=4 end;"
                    "mb.refresh();return {wounded=w and w.name or false,shield=s and s.name or false,boss=b and b.name or false}")
                # Drop idle particles so the only difference between the off and
                # on captures is the token draw path.
                entry['particles_removed'] = bridge.lua(
                    "local n=0;for _,a in pairs(game.level.entities) do if a.__particles then local rem={};"
                    "for e in pairs(a.__particles) do rem[#rem+1]=e end;"
                    "for _,e in ipairs(rem) do local ok=pcall(function() a:removeParticles(e) end);if ok then n=n+1 end end end end;"
                    "local function strip(t) if not t then return end for i=#(t.add_mos or {}),1,-1 do local m=t.add_mos[i];if type(m)=='table' and m._isshaderaura then table.remove(t.add_mos,i) end end end;"
                    "for _,a in pairs(game.level.entities) do a.shader=nil;a.shader_args=nil;a.shader_auras=nil;strip(a);strip(a.replace_display) end;"
                    "mb.refresh();return n")
                entry['shots'] = []
                # Freeze idle animation so a flag toggle is the only variable
                # between the off/on frames (particles otherwise drift).
                bridge.lua("core.display.pauseAnims(true);return true")
                for t in (48, 64, 96):
                    bridge.lua("local T=require 'mod.class.CheckerTokens';T.layer_trial=false;"
                               f"mb.setTile({t});game:checkerRefreshVisuals();mb.focus(game.player.x,game.player.y);return true")
                    p_off = bridge.shot(f'{prefix}-off-{label}-{t}')
                    bridge.lua("local T=require 'mod.class.CheckerTokens';T.layer_trial=true;"
                               f"mb.setTile({t});game:checkerRefreshVisuals();mb.focus(game.player.x,game.player.y);return true")
                    p_on = bridge.shot(f'{prefix}-on-{label}-{t}')
                    view = bridge.lua("local o={};for _,r in ipairs(mb.find()) do if r.placed then o[#o+1]=r.screen end end;"
                                      "return {rows=o,vp={math.floor(game.level.map.display_x),math.floor(game.level.map.display_y),game.level.map.viewport.w,game.level.map.viewport.h}}")
                    xs = [r[0] for r in view['rows']] or [0]
                    ys = [r[1] for r in view['rows']] or [0]
                    box = clamp_box((min(xs) - t, min(ys) - t, max(xs) + 2 * t, max(ys) + 2 * t))
                    CROPS.mkdir(parents=True, exist_ok=True)
                    a = Image.open(p_off).convert('RGB').crop(box)
                    b = Image.open(p_on).convert('RGB').crop(box)
                    c_off = CROPS / f'{prefix}-off-{label}-{t}-crop.png'
                    c_on = CROPS / f'{prefix}-on-{label}-{t}-crop.png'
                    a.save(c_off); b.save(c_on)
                    diff = ImageChops.difference(a, b)
                    differing = diff.getbbox() is not None
                    changed = sum(1 for px in diff.getdata() if px != (0, 0, 0))
                    entry['shots'].append({'tile': t, 'off': rel(c_off), 'on': rel(c_on),
                                           'region': list(box), 'changed_pixels': changed, 'changed': differing})
                    # Keep only the crops in the evidence tree.
                    Path(p_off).unlink(missing_ok=True)
                    Path(p_on).unlink(missing_ok=True)
                entry['unchanged_64_96'] = all(not s['changed'] for s in entry['shots'] if s['tile'] in (64, 96))
                entry['changed_48'] = next(s['changed'] for s in entry['shots'] if s['tile'] == 48)
                entry['tall'] = [r['name'] for r in entry['rows'] if r['name'] in ('pyromancer', 'yeek mindslayer')]
                bridge.lua("core.display.pauseAnims(false);return true")
            elif kind == 'standee_grid':
                # R50: retain NPC invisibility/stealth and use native player
                # perception for placed actors (Corrupted Daelach invisible=40).
                entry['perception'] = bridge.lua(
                    "game.player.see_invisible=1000;game.player.see_stealth=1000;"
                    "game.player:resetCanSeeCache();mb.refresh();"
                    "return {see_invisible=game.player.see_invisible,see_stealth=game.player.see_stealth}")
                # R39 native-tall standee redesign. Region crops only; no full
                # frames are kept. Tile sizes 16/32/48/64 plus the native
                # tokens-off frame.
                mode = step[1]
                entry['mode'] = mode
                # The four shipped standees; kra-tor is placed in the crowd as a
                # FLAT token (body-only cap 1.0) and is asserted flat, not a
                # standee. R47 batch-1 ids get their own dedicated scene so the
                # R43 regression set stays unchanged.
                stand_names = [n for n, _, _, tid in R39_STANDS if tid in R39_ORIGINAL_IDS]
                sizes = (16, 32, 48, 64)
                if mode in ('crowd', 'crowd-zh'):
                    entry['crowd'] = standee_place_crowd(bridge, STANDEE_CROWD)
                    if not entry['crowd']:
                        entry['failed'] = 'no 5x4 free block'
                    else:
                        entry['special'] = bridge.lua(
                            "game.always_target=true;"
                            "local function setf(n,f) local a=mb.byName(n);if a then a.faction=f end end;"
                            "setf('Ninandra, the Great Weaver',game.player.faction);"
                            "setf(\"Kra'Tor the Gluttonous\",'neutral');"
                            "local g=mb.byName('snow giant');if g then g.life=math.max(1,math.floor(g.max_life*0.5));g.rank=4;"
                            "g.damage_shield=40;g.damage_shield_absorb=10;g.damage_shield_absorb_max=40 end;"
                            "mb.refresh();local rows={};for _,n in ipairs({'Ninandra, the Great Weaver',\"Kra'Tor the Gluttonous\",'snow giant','Phoenix','ogre guard'}) do "
                            "local a=mb.byName(n);if a then local st=a._checker_token;rows[#rows+1]={name=n,token=st and st.id or false,standee=st and st.standee or false,"
                            "faction=a.faction or false,reaction=game.player:reactionToward(a),rank=a.rank or false} end end;return {rows=rows}")
                        capture_sizes = (32,) if mode == 'crowd-zh' else sizes
                        standee_off_on(bridge, entry, mode, capture_sizes, 'standee-' + mode,
                                       native=True, up=2, down=1, span=1, freeze=True)
                        if mode == 'crowd':
                            for tile in (32, 64):
                                standee_per_actor(bridge, entry, 'standee-crowd-%d' % tile, stand_names, tile=tile)
                elif mode in ('batch1', 'batch2', 'batch3', 'batch4', 'briagh'):
                    # R47 batch 1: spawn each of the 17 new ids and capture a
                    # per-actor OFF/ON/NATIVE 3x4 crop at 32/48/64, then a
                    # crowd of several new standees adjacent at 48px.
                    batch_ids = {'batch1': R39_BATCH1_IDS, 'batch2': R39_BATCH2_IDS, 'batch3': R39_BATCH3_IDS, 'batch4': R39_BATCH4_IDS, 'briagh': R53_BRIAGH_IDS}[mode]
                    batch_crowd = {'batch1': STANDEE_BATCH1_CROWD, 'batch2': STANDEE_BATCH2_CROWD, 'batch3': STANDEE_BATCH3_CROWD, 'batch4': STANDEE_BATCH4_CROWD, 'briagh': STANDEE_BRIAGH_CROWD}[mode]
                    placed = []
                    for n, src, das, tid in R39_STANDS:
                        if tid not in batch_ids:
                            continue
                        bridge.lua('mb.clearAround(10);return true')
                        row = bridge.lua(
                            'return mb.place(%s,%s,0,-1,%s)' % (
                                json.dumps(n, ensure_ascii=False),
                                json.dumps(src) if src else 'nil',
                                json.dumps(das) if das else 'nil'))
                        placed.append({'name': n, 'id': tid, 'row': row})
                        for t in (32, 48, 64):
                            standee_per_actor(bridge, entry, 'standee-%s-%s-%d' % (mode, tid, t),
                                              [n], tile=t)
                    entry['placed'] = placed
                    bridge.lua('mb.clearAround(12);return true')
                    entry['crowd'] = standee_place_crowd(bridge, batch_crowd)
                    if not entry['crowd']:
                        entry['failed'] = 'no 5x4 free block'
                    else:
                        standee_off_on(bridge, entry, mode, (48,), 'standee-' + mode + '-crowd',
                                       native=True, up=2, down=1, span=2, freeze=True)
                    entry['done'] = True
                elif mode == 'open':
                    entry['placed'] = standee_place_one(bridge, 'standee', 0)
                    standee_open_scene(bridge, entry, sizes)
                elif mode == 'repaint':
                    entry['layout'] = standee_place_crowd(bridge, STANDEE_REPAINT)
                    if not entry['layout']:
                        entry['failed'] = 'no free block'
                    else:
                        entry['special'] = bridge.lua(
                            "game.always_target=true;mb.focus(game.player.x,game.player.y);"
                            "local rows={};for _,n in ipairs({'ogre guard','snow giant','Ninandra, the Great Weaver','giant spider'}) do "
                            "local a=mb.byName(n);if a then local st=a._checker_token;rows[#rows+1]={name=n,token=st and st.id or false,standee=st and st.standee or false,"
                            "image=a.replace_display and a.replace_display.image or a.image} end end;return {rows=rows}")
                        standee_off_on(bridge, entry, 'repaint', (32,), 'standee-repaint',
                                       native=True, up=2, down=1, span=2, freeze=True)
                elif mode == 'rank':
                    standee_rank_check(bridge, entry)
                elif mode == 'forge-innate':
                    standee_forge_innate_diagnostic(bridge, entry)
                elif mode in ('aura', 'aura-forge', 'aura-dim'):
                    # R48 item C: measure the animated aura on a TALL id and two
                    # SQUARE ids. heavy bone giant (cap 1.75) exercises the
                    # 128x256 TALL texture path with body_top == alpha top;
                    # snow giant (SQUARE) and ogre-guard (SQUARE, body_top 38 !=
                    # alpha top 18) cover the 256x256 branch and the body-only
                    # quad. Each actor is placed alone (clearAround between) so
                    # a neighbour cannot pollute the measured cell.
                    entry['placed'] = []
                    # Two REAL native shader auras measured SEPARATELY and
                    # animated: warm T_BODY_OF_FIRE and dark
                    # EFF_ESSENCE_OF_THE_DEAD. Also attach a native particle so
                    # the addParticles positioning is recorded.
                    actors = ([('Bill the Stone Troll', 54), ('snow giant', 1)] if mode == 'aura-dim' else
                              [('forge-giant', 20)] if mode == 'aura-forge' else R39_AURA_ACTORS)
                    entry['informative_only'] = mode == 'aura-dim'
                    for aname, aidx in actors:
                        entry['placed'].append(standee_place_one(bridge, 'standee', aidx))
                        standee_realaura(bridge, entry, aname, tiles=(32, 48, 64), frames=AURA_HEIGHT_FRAMES, up=2, down=1, span=1,
                                         lighting_profile="DIM_LIGHTING_REFERENCE" if mode == "aura-dim" else "LIGHTING_REFERENCE")
                        entry.setdefault('clear_around_removals', []).append(standee_clear_around_logged(bridge, 12))
                    # The loop's final clearAround removed the last actor; put
                    # the first one back for the particle / aura_after snapshot
                    # (otherwise mb.byName(name) is nil and the step errors).
                    entry['placed'].append(standee_place_one(bridge, 'standee', actors[0][1]))
                    name = actors[0][0]
                    q = json.dumps(name, ensure_ascii=False)
                    entry['aura_particles'] = bridge.lua(
                        ("local a=mb.byName(%s);local P=require 'engine.Particles';"
                         "local okp,err=pcall(function() a:addParticles(P.new('flame',1,{})) end);"
                         "pcall(function() a:updateModdableTile() end);mb.focus(a.x,a.y);"
                         "local pc=0;for _ in pairs(a.__particles or {}) do pc=pc+1 end;"
                         "return {particle_ok=okp and true or false,particle_err=tostring(err),particles=pc}") % q)
                    entry['aura_after'] = bridge.lua(
                        f"local a=mb.byName({q});local t=a.replace_display or a;local au=0;for _,m in ipairs(t.add_mos or {{}}) do if m._isshaderaura then au=au+1 end end;"
                        "local n=0;for _ in pairs(a.shader_auras or {}) do n=n+1 end;"
                        "return {standee=(a._checker_token and a._checker_token.standee) and true or false,shader_auras=n,aura_entries=au}")
                elif mode == 'sequential':
                    # Two real auras added one after another with no
                    # refresh/toggle in between, then one removed.
                    name = 'snow giant'
                    entry['placed'] = standee_place_one(bridge, 'standee', 1)
                    standee_sequential(bridge, entry, name, tile=48)
                elif mode in ('facing', 'facing-ogre', 'facing-new-tall', 'facing-heavy-bone', 'facing-daelach', 'facing-bill', 'facing-batch4'):
                    # Native facing: one creature, creature and aura mirrored.
                    # R47 used the TALL new id (heavy bone giant); R48 restores
                    # the R46 ogre-guard scene beside it. Both score the mirror
                    # gain on the real aura asymmetric region with animations
                    # running, so the conditional moment gate has two actors.
                    if mode == 'facing-batch4':
                        rows = [static_aura_asymmetry(tid) for tid in R39_BATCH4_IDS]
                        chosen = select_facing_subject(rows)
                        entry['facing_subject_selection'] = {'candidates': rows, 'selected': chosen, 'minimum': 0.30}
                        idx = next(i for i, row in enumerate(R39_STANDS) if row[3] == chosen['id'])
                        name = R39_STANDS[idx][0]
                    elif mode == 'facing-bill':
                        name, idx = 'Bill the Stone Troll', 54
                    elif mode == 'facing-new-tall':
                        name, idx = 'Norgos, the Guardian', 29
                    elif mode == 'facing-ogre':
                        name, idx = 'ogre guard', 0
                    elif mode == 'facing-heavy-bone':
                        name, idx = 'heavy bone giant', 5
                    elif mode == 'facing-daelach':
                        name, idx = 'Corrupted Daelach', 39
                    else:
                        name, idx = R39_AURA_ACTOR[0], R39_AURA_ACTOR[1]
                    entry['placed'] = standee_place_one(bridge, 'standee', idx)
                    standee_facing(bridge, entry, name, tile=48)
                elif mode == 'top':
                    entry['placed'] = standee_place_one(bridge, 'standee', 1)
                    # R41: the top-edge geometry must be measured at the SAME
                    # 48px tile as the top-48 sheet. R40 measured it at the
                    # 64px launch tile while the sheet was 48px.
                    bridge.lua("local T=require 'mod.class.CheckerTokens';T.layer_trial=false;T.standee_trial=true;"
                               "mb.setTile(48);game:checkerRefreshVisuals();return true")
                    # R40: move the actor to the top free visible row and use a
                    # bounded setScroll, so its own row really is the first
                    # visible map row (R39's m.my=a.y was undone by bounding).
                    entry['top'] = standee_scroll_top(bridge, 'snow giant')
                    entry['top_geometry'] = bridge.lua(
                        "local S=require 'mod.class.CheckerTokenStyle';local a=mb.byName('snow giant');"
                        "local m=game.level.map;local s=a._checker_token;local cap=S.standeeHeight(s and s.id or nil);"
                        "local box=s and s.layer_box;local quad=nil;"
                        "if cap and box then local cell=m.tile_w;local dd=cell*S.token_diameter;"
                        "local left,top,size=S.standeeQuad(cell,box,box.canvas or 128,cell/2,cell/2,dd,cap);"
                        "quad={left=left,top=top,size=size,screen_left=m.display_x+left,screen_top=m.display_y+top,frame_bottom=m.display_y+top+size} end;"
                        "return {viewport_top=m.display_y,viewport_bottom=m.display_y+m.viewport.mheight*m.tile_h,quad=quad,same_row=(m.my==a.y) and true or false,my=m.my,ay=a.y,tile=m.tile_w,map={w=m.w,h=m.h}}")
                    focus = "mb.forceTop('snow giant')"
                    standee_off_on(bridge, entry, 'top', (48,), 'standee-top', focus=focus,
                                   native=True, up=2, down=1, span=2)
                elif mode == 'wide':
                    # A wide native-tall id with no shipped standee layer (Corrupted Sand Wyrm,
                    # derived cap 1.703125) must stay a flat token: only
                    # M.standee_ids get a standee, so the width path can never
                    # turn an unknown native-tall actor into a standee.
                    name = 'Corrupted Sand Wyrm'
                    q = json.dumps(name, ensure_ascii=False)
                    entry['placed'] = bridge.lua(
                        f"return mb.place({q},'/data/zones/sandworm-lair/npcs.lua',2,0,'CORRUPTED_SAND_WYRM')")
                    entry['wide_state'] = bridge.lua(
                        f"local a=mb.byName({q});local s=a._checker_token;"
                        "return {identify=(require 'mod.class.CheckerTokens'.explain(a,nil,false)) or false,"
                        "rendered_token=(s and s.id) or false,standee=(s and s.standee) and true or false,"
                        "layered=(s and s.layered) and true or false,has_box=(s and s.layer_box~=nil) and true or false,"
                        "height=require('mod.class.CheckerTokenStyle').standeeHeight(s and s.id or nil) or false}")
                    standee_off_on(bridge, entry, 'wide', (48,), 'standee-wide',
                                   native=True, up=2, down=1, span=2)
                elif mode == 'flat':
                    from PIL import Image
                    entry['layout'] = standee_place_crowd(bridge, STANDEE_FLAT)
                    if not entry['layout']:
                        entry['failed'] = 'no free block'
                    else:
                        bridge.lua("game.always_target=true;local m=game.level.map;m.view_faction='players';"
                                   "config.settings.tome.small_frame_side=nil;mb.refresh();return true")
                        for tile in (16,):
                            bridge.lua("local T=require 'mod.class.CheckerTokens';T.layer_trial=false;T.standee_trial=true;"
                                       f"mb.setTile({tile});game:checkerRefreshVisuals();game.always_target=true;"
                                       "game.level.map.view_faction='players';config.settings.tome.small_frame_side=nil;"
                                       "mb.focus(game.player.x,game.player.y);return true")
                            state = standee_state(bridge)
                            p_flat = bridge.shot('standee-flat-%d' % tile)
                            flat_box = standee_region(bridge, tile, up=2, down=1, span=3)
                            CROPS.mkdir(parents=True, exist_ok=True)
                            c_flat = CROPS / ('standee-flat-%d-crop.png' % tile)
                            Image.open(p_flat).convert('RGB').crop(flat_box).save(c_flat)
                            entry.setdefault('captures', []).append({'tile': tile, 'region': list(flat_box),
                                                                     'crop': rel(c_flat), 'native': False,
                                                                     'state': state})
                            Path(p_flat).unlink(missing_ok=True)
                entry['done'] = True
            elif kind in ('ta1_meta', 'ta2_meta'):
                # Tall-body metadata: the installed token replacement must be a
                # single body (no non-aura add_mos), the actor shader nil and the
                # identity exact. Machine record only; the draw-once judgement is
                # a human crop review (a machine count cannot prove it).
                names = '{' + ','.join(json.dumps(n, ensure_ascii=False) for n in step[1]) + '}'
                entry['rows'] = bridge.lua(
                    "local out={};local function L(t) local o={};for _,m in ipairs(t or {}) do o[#o+1]={image=m.image or false,display_h=m.display_h or false,display_y=m.display_y or false,display_w=m.display_w or false,aura=m._isshaderaura and true or false} end return o end;"
                    "for _,n in ipairs(" + names + ") do local a=mb.byName(n);if a then local r=mb.row(a);"
                    "r.replacement_display_h=a.replace_display and a.replace_display.display_h or false;"
                    "r.replacement_display_y=a.replace_display and a.replace_display.display_y or false;"
                    "r.replacement_display_image=a.replace_display and a.replace_display.image or false;"
                    "r.replacement_add_mos=L(a.replace_display and a.replace_display.add_mos);"
                    "r.own_image=a.image;r.own_add_mos=L(a.add_mos);r.shader=a.shader or false;r.shader_args=a.shader_args or false;out[#out+1]=r end end;return out")
            elif kind == 'ta1_negative':
                # Appearance negatives: the body changes, so exact identity must
                # fail and native art remain. (1) wrong type, (2) wrong subtype,
                # (3) added shader, (4) different name reusing an admitted PNG.
                entry['cases'] = []
                for key, name, src, mut in TA1_NEG_CASES:
                    bridge.lua("mb.clearAround(8);return true")
                    row = bridge.lua(
                        f"local r=mb.place({json.dumps(name, ensure_ascii=False)},{json.dumps(src)},1,1);"
                        f"local a=mb.byName({json.dumps(name, ensure_ascii=False)});{mut};"
                        "pcall(function() game:checkerRefreshActor(a,'display') end);mb.refresh();"
                        "local x=mb.row(a);x.shader=a.shader or false;x.shader_args=a.shader_args or false;return x")
                    view = _set_vp(bridge.lua(CLEAN_VIEW % ('a._checker_live_placed', GROUP_CENTER)))
                    ps = bridge.shot(f'ta1-negative-{key}-{label}')
                    cp, box = group_crop(view, ps, f'ta1-negative-{key}-{label}', 1)
                    entry['cases'].append({'key': key, 'name': name, 'row': row, 'view': view, 'crop': rel(cp)})
                bridge.lua("mb.clearAround(8);return true")
                row = bridge.lua(TA1_NOVICE_LUA)
                view = _set_vp(bridge.lua(CLEAN_VIEW % ('a==_G.TA1N', GROUP_CENTER)))
                ps = bridge.shot(f'ta1-negative-different-name-{label}')
                cp, box = group_crop(view, ps, f'ta1-negative-different-name-{label}', 1)
                entry['different_name'] = {'row': row, 'view': view, 'crop': rel(cp)}
            elif kind == 'ta1_escort':
                # The slaver's own native make_escort (ring-of-blood/npcs.lua:192)
                # spawns two "enthralled slave" same-body copies on tick end; both
                # must wear the enthralled-slave token through the exact path.
                bridge.lua("return {n=mb.clearAround(8)}")
                bridge.lua("_G.MLV_BEFORE={};for _,a in pairs(game.level.entities) do _G.MLV_BEFORE[a]=true end;return true")
                entry['slaver'] = bridge.lua(f"return mb.place({json.dumps(step[1], ensure_ascii=False)},{json.dumps(PLACE_SRC_TA1['slaver'])},-2,1)")
                esc = []
                for _ in range(12):
                    time.sleep(1)
                    esc = bridge.lua(
                        "local out={};for _,a in pairs(game.level.entities) do if not _G.MLV_BEFORE[a] and a.x and a.name=='enthralled slave' then "
                        "a._checker_live_placed=true;a._checker_live_minion=true;a.never_act=true;pcall(function() game:checkerRefreshActor(a,'display') end);out[#out+1]=a end end;"
                        "mb.refresh();local rows={};for _,a in ipairs(out) do local r=mb.row(a);r.define_as_field=a.define_as or false;r.master=(a.master==mb.byName('slaver')) and true or false;rows[#rows+1]=r end;return rows")
                    if len(esc) >= 2:
                        break
                entry['escorts'] = esc
                entry['ok'] = bool(esc) and all(r['identify'] == 'enthralled-slave' and r['rendered_token'] == 'enthralled-slave' for r in esc)
                view = _set_vp(bridge.lua(CLEAN_VIEW % ("(a._checker_live_placed or a._checker_live_minion)", GROUP_CENTER)))
                ps = bridge.shot(f'ta1-slaver-escort-{label}')
                cp, box = group_crop(view, ps, f'ta1-slaver-escort-{label}', 2)
                view['crop_box'] = box
                entry['view'] = view
                entry['shots'] = [{'file': rel(ps), 'sha256': digest(ps), 'crop': rel(cp)}]
            elif kind == 'ta2_slinger':
                # Derth's resident (no define_as) wears the token; the Arena copy
                # (define_as="SLINGER") fails the exact bind and stays native.
                bridge.lua("return {n=mb.clearAround(8)}")
                entry['derth'] = bridge.lua("return mb.place('halfling slinger','/data/zones/town-derth/npcs.lua',-2,1)")
                entry['arena'] = bridge.lua("return mb.place('halfling slinger','/data/zones/arena-unlock/npcs.lua',2,1,'SLINGER')")
                ta2_group_shots(bridge, label, 'ta2-slinger', entry)
            elif kind == 'ta2_lumberjack':
                # town-lumberjack-village/npcs.lua:70 writes `defined_as` (a typo),
                # so the runtime actor has no define_as and matches on name+body.
                entry['row'] = bridge.lua("local a=mb.byName('lumberjack');assert(a,'no lumberjack');return mb.row(a)")
            elif kind == 'ta2_wayist':
                entry['cleared'] = bridge.lua("return {n=mb.clearAround(8)}")
                entry['reposition'] = ta2_reposition(bridge)
                entry['use'] = bridge.lua(TA2_WAYIST_LUA)
                ta2_group_shots(bridge, label, 'ta2-wayist', entry)
            elif kind == 'ta2_anomaly':
                entry['cleared'] = bridge.lua("return {n=mb.clearAround(8)}")
                entry['reposition'] = ta2_reposition(bridge)
                entry['use'] = bridge.lua(TA2_ANOMALY_LUA)
                ta2_group_shots(bridge, label, 'ta2-anomaly', entry, margin=3)
            elif kind == 'ta2_archers':
                # Same native PNG; each keeps its own identity (name/subtype differ).
                bridge.lua("return {n=mb.clearAround(8)}")
                entry['archer'] = bridge.lua("return mb.place('elven archer','/data/general/npcs/sunwall-town.lua',-2,1)")
                entry['companion'] = bridge.lua("return mb.place('Companion Archer','/data/zones/keepsake-meadow/npcs.lua',2,1,'BERETHH_ARCHER')")
                ta2_group_shots(bridge, label, 'ta2-archers', entry)
            elif kind == 'ta2_aura':
                # Sustained aura on a token actor: the token must stay, the actor
                # shader must stay nil and the native aura (shader aura and/or
                # particle) must remain around the token.
                name, tid = step[1], step[2]
                q = json.dumps(name, ensure_ascii=False)
                FS = ("local a=mb.byName(%s);pcall(function() a:updateModdableTile() end);mb.refresh();mb.focus(a.x,a.y);local r=mb.row(a);"
                      "local n=0;for _ in pairs(a.shader_auras or {}) do n=n+1 end;"
                      "local t=a.replace_display or a;local L={};for _,m in ipairs(t.add_mos or {}) do L[#L+1]=(m._isshaderaura and 'AURA:' or '')..tostring(m.image)..'/'..tostring(m.shader or '') end;"
                      "local pc=0;for _ in pairs(a.__particles or {}) do pc=pc+1 end;"
                      "return {row=r,sustained=a:isTalentActive('%s') and true or false,known=a:knowTalent('%s') and true or false,"
                      "actor_shader=a.shader or false,shader_auras=n,add_mos=L,particles=pc,image=a.image,type=a.type,subtype=a.subtype}") % (q, tid, tid)
                FT = "{ignore_energy=true,ignore_cd=true,no_equilibrium_fail=true,no_talent_fail=true,silent=true}"
                entry['before'] = bridge.lua(FS)
                entry['learn'] = bridge.lua(
                    f"local a=mb.byName({q});if not a:knowTalent('{tid}') then a:learnTalent('{tid}',true,1) end;"
                    f"return {{known=a:knowTalent('{tid}') and true or false}}")
                if not entry['before'].get('sustained'):
                    entry['activate'] = bridge.lua(
                        f"local a=mb.byName({q});local was=a:isTalentActive('{tid}') and true or false;"
                        f"if not was then pcall(function() a:forceUseTalent('{tid}',{FT}) end) end;"
                        f"return {{was_active=was,now=a:isTalentActive('{tid}') and true or false}}")
                else:
                    entry['activate'] = {'was_active': True, 'now': True, 'skipped': 'already sustained at birth'}
                entry['during'] = bridge.lua(FS)
                p1 = bridge.shot(f'ta2-aura-during-{tid}-{label}')
                entry['shots'] = [{'file': rel(p1), 'sha256': digest(p1),
                                   'crop': rel(crop(p1, entry['during']['row']['screen'], f'ta2-aura-during-{tid}-{label}-crop', 3))}]
                if not entry['before'].get('sustained'):
                    entry['deactivate'] = bridge.lua(
                        f"local a=mb.byName({q});local ok,err=pcall(function() if a:isTalentActive('{tid}') then a:forceUseTalent('{tid}',{FT}) end end);"
                        f"return {{ok=ok,err=tostring(err),now=a:isTalentActive('{tid}') and true or false}}")
                    entry['after'] = bridge.lua(FS)
            elif kind == 'ta2_negative':
                # Different-name PNG reuses (gem crafter / YEEK_STORE_*), a same-name
                # wrong type/subtype and a synthetic Novice mage stay native.
                entry['cases'] = []
                for key, name, src, das, mut in TA2_NEG_CASES:
                    bridge.lua("mb.clearAround(8);return true")
                    dasv = json.dumps(das) if das else 'nil'
                    row = bridge.lua(
                        f"local r=mb.place({json.dumps(name, ensure_ascii=False)},{json.dumps(src)},1,1,{dasv});"
                        f"local a=mb.byName({json.dumps(name, ensure_ascii=False)});" + (mut + ";" if mut else "") +
                        "pcall(function() game:checkerRefreshActor(a,'display') end);mb.refresh();"
                        "local x=mb.row(a);x.shader=a.shader or false;return x")
                    view = _set_vp(bridge.lua(CLEAN_VIEW % ('a._checker_live_placed', GROUP_CENTER)))
                    ps = bridge.shot(f'ta2-negative-{key}-{label}')
                    cp, box = group_crop(view, ps, f'ta2-negative-{key}-{label}', 1)
                    entry['cases'].append({'key': key, 'name': name, 'define_as': das, 'row': row, 'view': view, 'crop': rel(cp)})
                bridge.lua("mb.clearAround(8);return true")
                row = bridge.lua(TA2_NOVICE_LUA)
                view = _set_vp(bridge.lua(CLEAN_VIEW % ('a==_G.TA2N', GROUP_CENTER)))
                ps = bridge.shot(f'ta2-negative-novice-mage-{label}')
                cp, box = group_crop(view, ps, f'ta2-negative-novice-mage-{label}', 1)
                entry['novice'] = {'row': row, 'view': view, 'crop': rel(cp)}
            elif kind == 'ub1_group':
                # Nine native-tall uniques placed together; two off/on cycles.
                mode = step[1]
                bridge.lua('mb.clearAround(8);_G.UBC={};return true')
                for index, ((n, src, das, tid), (dx, dy)) in enumerate(zip(UB1_CASES, UB1_POS)):
                    bridge.lua(f"mb.place({lua_value(n)},{lua_value(src)},{dx},{dy},{lua_value(das)});local best;for _,a in pairs(game.level.entities) do if a._checker_live_placed and a.x and not a._ub1_id then best=a end end;assert(best);best._ub1_id={lua_value(tid)};best.invisible=nil;best.stealth=nil;best.inc_stealth=nil;UBC[#UBC+1]=best;return true")
                snap = ("local out={};local Style=require 'mod.class.CheckerTokenStyle';"
                        "for _,a in ipairs(UBC) do local r=mb.row(a);r.ub1_id=a._ub1_id;r.badge=Style.rankBadge(a.rank) or false;"
                        "r.shader=a.shader or false;r.shader_args=a.shader_args or false;"
                        "local d=a.replace_display;r.replacement_display_h=d and d.display_h or false;"
                        "r.replacement_display_y=d and d.display_y or false;r.replacement_image=d and d.image or false;"
                        "local n=0;for _,m in ipairs(d and d.add_mos or {}) do if not m._isshaderaura then n=n+1 end end;r.replacement_add_mos_count=n;out[#out+1]=r end;return out")
                entry['states'] = []
                for enabled, roundno in ((True, 0), (False, 1), (True, 1), (False, 2), (True, 2)):
                    bridge.lua('mb.tokens(' + ('true' if enabled else 'false') + ');return true')
                    state = {'enabled': enabled, 'round': roundno, 'frames': []}
                    for tile in ((48, 64, 96) if roundno < 2 else (64,)):
                        bridge.lua(f'mb.setTile({tile});return true')
                        view = _set_vp(bridge.lua(CLEAN_VIEW % ('a._ub1_id', GROUP_CENTER)))
                        rows = bridge.lua(snap)
                        name = f'ub1-{mode}-{label}-r{roundno}-{"token" if enabled else "native"}-{tile}'
                        ps = bridge.shot(name); cp, box = group_crop(view, ps, name, 1)
                        state['frames'].append({'tile': tile, 'rows': rows, 'view': view, 'file': rel(ps), 'crop': rel(cp), 'crop_box': box, 'sha256': digest(cp)})
                    entry['states'].append(state)
                bridge.lua('mb.setTile(64);return true')
            elif kind == 'ub1_meta':
                # Single-body metadata: replacement display is one body (no
                # non-aura add_mos) and the actor keeps its own native tall body.
                names = '{' + ','.join(json.dumps(n, ensure_ascii=False) for n in step[1]) + '}'
                entry['rows'] = bridge.lua(
                    "local out={};local function L(t) local o={};for _,m in ipairs(t or {}) do o[#o+1]={image=m.image or false,display_h=m.display_h or false,display_y=m.display_y or false,display_w=m.display_w or false,aura=m._isshaderaura and true or false} end return o end;"
                    "for _,n in ipairs(" + names + ") do local a=mb.byName(n);if a then local r=mb.row(a);"
                    "r.replacement_display_h=a.replace_display and a.replace_display.display_h or false;"
                    "r.replacement_display_y=a.replace_display and a.replace_display.display_y or false;"
                    "r.replacement_display_image=a.replace_display and a.replace_display.image or false;"
                    "r.replacement_add_mos=L(a.replace_display and a.replace_display.add_mos);"
                    "r.own_image=a.image;r.own_add_mos=L(a.add_mos);r.shader=a.shader or false;r.shader_args=a.shader_args or false;out[#out+1]=r end end;return out")
            elif kind == 'ub1_each':
                # One identity at a time so each tall body can be inspected alone.
                entry['items'] = []
                for (n, src, das, tid) in UB1_CASES:
                    bridge.lua("return {n=mb.clearAround(8)}")
                    bridge.lua(f"mb.place({lua_value(n)},{lua_value(src)},0,1,{lua_value(das)});local a;for _,x in pairs(game.level.entities) do if x._checker_live_placed and x~=game.player then a=x end end;if a then a.invisible=nil;a.stealth=nil;a.inc_stealth=nil end;return true")
                    frames = []
                    for tile in (48, 64, 96):
                        bridge.lua(f'mb.setTile({tile});return true')
                        view = _set_vp(bridge.lua(CLEAN_VIEW % ('a._checker_live_placed', GROUP_CENTER)))
                        r = bridge.lua("local a;for _,x in pairs(game.level.entities) do if x._checker_live_placed and x~=game.player then a=x end end;return mb.row(a)")
                        name = f'ub1-each-{tid}-{label}-{tile}'
                        ps = bridge.shot(name); cp, box = group_crop(view, ps, name, 2)
                        frames.append({'tile': tile, 'row': r, 'view': view, 'file': rel(ps), 'crop': rel(cp), 'crop_box': box, 'sha256': digest(cp)})
                    entry['items'].append({'id': tid, 'name': n, 'frames': frames})
                bridge.lua('mb.setTile(64);return true')
            elif kind in ('ub1_sites', 'ub1_siblings'):
                # Both Aeryn define sites / both Caldizar define_as values, and
                # the High-vs-Fallen / Twin-vs-Clone pairs side by side.
                entry['groups'] = []
                if kind == 'ub1_sites':
                    pairs = [('aeryn-sites', [UB1_CASES[0], UB1_GATES]),
                             ('caldizar-alias', [UB1_CASES[2], UB1_AOADS])]
                else:
                    pairs = [('aeryn', [UB1_CASES[0], UB1_CASES[1]]),
                             ('chronolith', [UB1_CASES[3], UB1_CASES[4]])]
                for key, cases in pairs:
                    bridge.lua('mb.clearAround(8);_G.UBS={};return true')
                    for index, ((n, src, das, tid), (dx, dy)) in enumerate(zip(cases, [(-2, 1), (2, 1)])):
                        bridge.lua(f"mb.place({lua_value(n)},{lua_value(src)},{dx},{dy},{lua_value(das)});local best;for _,a in pairs(game.level.entities) do if a._checker_live_placed and a.x and a._ub1_ref==nil then best=a end end;assert(best);best._ub1_ref={index};best.invisible=nil;best.stealth=nil;best.inc_stealth=nil;UBS[#UBS+1]=best;return true")
                    frames = []
                    for tile in (48, 64, 96):
                        bridge.lua(f'mb.setTile({tile});return true')
                        view = _set_vp(bridge.lua(CLEAN_VIEW % ('a._ub1_ref ~= nil', GROUP_CENTER)))
                        rows = bridge.lua("local out={};for _,a in ipairs(UBS) do local r=mb.row(a);r.ub1_ref=a._ub1_ref;out[#out+1]=r end;return out")
                        name = f'ub1-{key}-{label}-{tile}'
                        ps = bridge.shot(name); cp, box = group_crop(view, ps, name, 1)
                        frames.append({'tile': tile, 'rows': rows, 'view': view, 'file': rel(ps), 'crop': rel(cp), 'crop_box': box, 'sha256': digest(cp)})
                    entry['groups'].append({'key': key, 'cases': [[n, src, das, tid] for (n, src, das, tid) in cases], 'frames': frames})
                bridge.lua('mb.setTile(64);return true')
            elif kind == 'ub1_twin':
                # Native zone.lua links the pair through `.brother`; the real
                # twin_take_hit onTakeHit halves the damage and passes it on.
                bridge.lua('mb.clearAround(8);_G.UBT={};return true')
                for index, ((n, src, das, tid), (dx, dy)) in enumerate(zip([UB1_CASES[3], UB1_CASES[4]], [(-2, 1), (2, 1)])):
                    bridge.lua(f"mb.place({lua_value(n)},{lua_value(src)},{dx},{dy},{lua_value(das)});local best;for _,a in pairs(game.level.entities) do if a._checker_live_placed and a.x and a._ub1_ref==nil then best=a end end;assert(best);best._ub1_ref={index};best.invisible=nil;best.stealth=nil;best.inc_stealth=nil;UBT[#UBT+1]=best;return true")
                entry['link'] = bridge.lua("local t,c=UBT[1],UBT[2];t.brother=c;c.brother=t;return {linked=(t.brother==c and c.brother==t),twin_on_take_hit=t.onTakeHit~=nil,clone_on_take_hit=c.onTakeHit~=nil}")
                entry['hit'] = bridge.lua("local t,c=UBT[1],UBT[2];local tl,cl=t.life,c.life;local dealt=t:takeHit(40,game.player);mb.refresh();local rt=mb.row(t);local rc=mb.row(c);return {twin_before=tl,clone_before=cl,twin_after=t.life,clone_after=c.life,dealt=dealt,twin=rt,clone=rc,brother_after=(t.brother==c and c.brother==t)}")
                entry['frames'] = []
                for tile in (48, 64, 96):
                    bridge.lua(f'mb.setTile({tile});return true')
                    view = _set_vp(bridge.lua(CLEAN_VIEW % ('a._ub1_ref ~= nil', GROUP_CENTER)))
                    ps = bridge.shot(f'ub1-twin-{label}-{tile}'); cp, box = group_crop(view, ps, f'ub1-twin-{label}-{tile}', 1)
                    entry['frames'].append({'tile': tile, 'view': view, 'file': rel(ps), 'crop': rel(cp), 'crop_box': box, 'sha256': digest(cp)})
                bridge.lua('mb.setTile(64);return true')
            elif kind == 'ub1_negative':
                # Same-name actor with no or another define_as stays native; the
                # CALDIZAR_AOADS define_as with a changed name or body stays native.
                entry['cases'] = []
                cases = [
                    ('aeryn-no-define', 'High Sun Paladin Aeryn', '/data/zones/high-peak/npcs.lua', 'HIGH_SUN_PALADIN_AERYN', 'a.define_as=nil'),
                    ('aeryn-other-define', 'High Sun Paladin Aeryn', '/data/zones/high-peak/npcs.lua', 'HIGH_SUN_PALADIN_AERYN', "a.define_as='OTHER_AERYN'"),
                    ('caldizar-no-define', 'Caldizar', '/data/zones/shertul-fortress-caldizar/npcs.lua', 'CALDIZAR', 'a.define_as=nil'),
                    ('caldizar-alias-rename', 'Caldizar', '/data/zones/high-peak/npcs.lua', 'CALDIZAR_AOADS', "a.name='Caldizar the Impostor'"),
                    ('caldizar-alias-image', 'Caldizar', '/data/zones/high-peak/npcs.lua', 'CALDIZAR_AOADS', "a.add_mos[1].image='npc/horror_temporal_temporal_defiler.png'"),
                    ('tarelion-shorthand-altered', 'Archmage Tarelion', '/data/zones/town-angolwen/npcs.lua', 'TARELION', 'a.add_mos[1].display_h=1'),
                ]
                for key, n, src, das, mut in cases:
                    bridge.lua('mb.clearAround(8);return true')
                    row = bridge.lua(
                        f"local r=mb.place({lua_value(n)},{lua_value(src)},1,1,{lua_value(das)});"
                        f"local a=mb.byName({lua_value(n)});assert(a,'no actor');{mut};"
                        "pcall(function() game:checkerRefreshActor(a,'display') end);mb.refresh();return mb.row(a)")
                    view = _set_vp(bridge.lua(CLEAN_VIEW % ('a._checker_live_placed', GROUP_CENTER)))
                    ps = bridge.shot(f'ub1-negative-{key}-{label}')
                    cp, box = group_crop(view, ps, f'ub1-negative-{key}-{label}', 1)
                    entry['cases'].append({'key': key, 'name': n, 'define_as': das, 'mut': mut, 'row': row, 'view': view, 'crop': rel(cp)})
            elif kind == 'ub1_nicer':
                # nicer_tiles off -> fresh native bodies (some default-name files
                # do not exist, so those stay native), then back on -> all map.
                entry['nicer_before'] = bridge.lua("return {v=require('engine.Map').tiles.nicer_tiles}")['v']

                def ub1_nicer_place():
                    bridge.lua('mb.clearAround(8);_G.UBN={};return true')
                    for (n, src, das, tid), (dx, dy) in zip(UB1_CASES, UB1_POS):
                        bridge.lua(f"mb.place({lua_value(n)},{lua_value(src)},{dx},{dy},{lua_value(das)});local best;for _,a in pairs(game.level.entities) do if a._checker_live_placed and a.x and not a._ub1_id then best=a end end;assert(best);best._ub1_id={lua_value(tid)};best.invisible=nil;best.stealth=nil;best.inc_stealth=nil;UBN[#UBN+1]=best;return true")

                def ub1_nicer_snap(tag):
                    frames = []
                    for tile in (48, 64, 96):
                        bridge.lua(f'mb.setTile({tile});return true')
                        view = _set_vp(bridge.lua(CLEAN_VIEW % ('a._ub1_id ~= nil', GROUP_CENTER)))
                        rows = bridge.lua("local o={};for _,a in ipairs(UBN) do local r=mb.row(a);r.ub1_id=a._ub1_id;o[#o+1]=r end;return o")
                        name = f'ub1-nicer-{tag}-{label}-{tile}'
                        ps = bridge.shot(name); cp, box = group_crop(view, ps, name, 1)
                        frames.append({'tile': tile, 'rows': rows, 'view': view, 'file': rel(ps), 'crop': rel(cp), 'crop_box': box, 'sha256': digest(cp)})
                    return frames

                bridge.lua("require('engine.Map').tiles.nicer_tiles=false;return true")
                entry['nicer_during'] = bridge.lua("return {v=require('engine.Map').tiles.nicer_tiles}")['v']
                ub1_nicer_place()
                entry['off'] = ub1_nicer_snap('off')
                bridge.lua("require('engine.Map').tiles.nicer_tiles=true;return true")
                entry['nicer_restored'] = bridge.lua("return {v=require('engine.Map').tiles.nicer_tiles}")['v']
                ub1_nicer_place()
                entry['on'] = ub1_nicer_snap('on')
                bridge.lua('mb.setTile(64);return true')
            elif kind == 'ub2_natural':
                # Enter each identity's real zone and prefer the natural spawn;
                # fall back to the zone npc list and record which happened.
                entry['items'] = []
                for (n, src, das, tid) in UB2_CASES:
                    zone, level = UB2_ZONES[n]
                    it = {'id': tid, 'name': n, 'zone': zone, 'level': level, 'source': src}
                    try:
                        it['enter'] = bridge.lua(f"return ms.enter({lua_value(zone)},{level},nil)")
                    except Exception as exc:
                        it['error'] = 'enter: ' + str(exc)[:300]
                        entry['items'].append(it)
                        continue
                    try:
                        has = bridge.lua(f"local a=mb.byName({lua_value(n)});return {{found=a and not a._checker_live_placed or false}}")
                        it['found_natural'] = bool(has['found'])
                        if has['found']:
                            reach = bridge.lua(f"local ok,err=pcall(mb.approach,{lua_value(n)});return {{ok=ok,err=tostring(err)}}")
                            if reach['ok']:
                                it['resolved'] = 'natural'
                            else:
                                it['natural_unreachable'] = reach['err'][:160]
                                has['found'] = False
                        if not has['found']:
                            it['resolved'] = 'placed'
                            it['row'] = bridge.lua(f"return mb.place({lua_value(n)},{lua_value(src)},1,1,{lua_value(das)})")
                    except Exception as exc:
                        it['error'] = 'place: ' + str(exc)[:300]
                        entry['items'].append(it)
                        continue
                    frames = []
                    for t in (48, 64, 96):
                        bridge.lua(f'mb.setTile({t});return true')
                        view = _set_vp(bridge.lua(CLEAN_VIEW % ('a==mb.byName(' + lua_value(n) + ')', GROUP_CENTER)))
                        # A native NPC emote (e.g. Derth's arena agent) is not a UI
                        # dialog; clear it so the subject tile is unobstructed.
                        bridge.lua("for _,a in pairs(game.level.entities) do if a.__emote then pcall(function() require('mod.class.Actor').setEmote(a,nil) end) end end;local m=game.level.map;m:redisplay();m.changed=true;core.display.forceRedraw();return true")
                        r = bridge.lua(f"local a=mb.byName({lua_value(n)});local x=mb.row(a);"
                                       "x.can_see=game.player:canSee(a) and true or false;"
                                       "x.seen=game.level.map.seens(a.x,a.y) and true or false;"
                                       "x.badge=require('mod.class.CheckerTokenStyle').rankBadge(a.rank) or false;return x")
                        name = f'ub2-natural-{tid}-{t}'
                        ps = bridge.shot(name); cp = crop(ps, r['screen'], name + '-crop', 3)
                        frames.append({'tile': t, 'row': r, 'view': view, 'file': rel(ps), 'sha256': digest(ps), 'crop': rel(cp)})
                    bridge.lua('mb.setTile(64);return true')
                    it['frames'] = frames
                    entry['items'].append(it)
            elif kind == 'ub2_group':
                mode = step[1]
                bridge.lua('mb.clearAround(8);_G.U2C={};return true')
                for (n, src, das, tid), (dx, dy) in zip(UB2_CASES, UB2_POS):
                    bridge.lua(f"mb.place({lua_value(n)},{lua_value(src)},{dx},{dy},{lua_value(das)});local best;for _,a in pairs(game.level.entities) do if a._checker_live_placed and a.x and not a._ub2_id then best=a end end;assert(best);best._ub2_id={lua_value(tid)};best.invisible=nil;best.stealth=nil;best.inc_stealth=nil;U2C[#U2C+1]=best;return true")
                snap = ("local out={};local Style=require 'mod.class.CheckerTokenStyle';"
                        "for _,a in ipairs(U2C) do local r=mb.row(a);r.ub2_id=a._ub2_id;r.badge=Style.rankBadge(a.rank) or false;"
                        "r.shader=a.shader or false;r.shader_args=a.shader_args or false;"
                        "r.replacement_image=a.replace_display and a.replace_display.image or false;out[#out+1]=r end;return out")
                entry['states'] = []
                for enabled, roundno in ((True, 0), (False, 1), (True, 1), (False, 2), (True, 2)):
                    bridge.lua('mb.tokens(' + ('true' if enabled else 'false') + ');return true')
                    state = {'enabled': enabled, 'round': roundno, 'frames': []}
                    for tile in ((48, 64, 96) if roundno < 2 else (64,)):
                        bridge.lua(f'mb.setTile({tile});return true')
                        view = _set_vp(bridge.lua(CLEAN_VIEW % ('a._ub2_id', GROUP_CENTER)))
                        rows = bridge.lua(snap)
                        name = f'ub2-{mode}-{label}-r{roundno}-{"token" if enabled else "native"}-{tile}'
                        ps = bridge.shot(name); cp, box = group_crop(view, ps, name, 1)
                        state['frames'].append({'tile': tile, 'rows': rows, 'view': view, 'file': rel(ps), 'crop': rel(cp), 'crop_box': box, 'sha256': digest(cp)})
                    entry['states'].append(state)
                bridge.lua('mb.setTile(64);return true')
            elif kind == 'ub2_each':
                entry['items'] = []
                for (n, src, das, tid) in UB2_CASES:
                    bridge.lua("return {n=mb.clearAround(8)}")
                    bridge.lua(f"mb.place({lua_value(n)},{lua_value(src)},0,1,{lua_value(das)});local a;for _,x in pairs(game.level.entities) do if x._checker_live_placed and x~=game.player then a=x end end;if a then a.invisible=nil;a.stealth=nil;a.inc_stealth=nil end;return true")
                    frames = []
                    for tile in (48, 64, 96):
                        bridge.lua(f'mb.setTile({tile});return true')
                        view = _set_vp(bridge.lua(CLEAN_VIEW % ('a._checker_live_placed', GROUP_CENTER)))
                        r = bridge.lua("local a;for _,x in pairs(game.level.entities) do if x._checker_live_placed and x~=game.player then a=x end end;return mb.row(a)")
                        name = f'ub2-each-{tid}-{label}-{tile}'
                        ps = bridge.shot(name); cp, box = group_crop(view, ps, name, 2)
                        frames.append({'tile': tile, 'row': r, 'view': view, 'file': rel(ps), 'crop': rel(cp), 'crop_box': box, 'sha256': digest(cp)})
                    entry['items'].append({'id': tid, 'name': n, 'frames': frames})
                bridge.lua('mb.setTile(64);return true')
            elif kind == 'ub2_ben':
                bridge.lua('mb.clearAround(8);_G.U2B={};return true')
                for (n, src, das, tid), (dx, dy) in zip([UB2_CASES[-1], UB2_ABOM], [(-2, 1), (2, 1)]):
                    bridge.lua(f"mb.place({lua_value(n)},{lua_value(src)},{dx},{dy},{lua_value(das)});local best;for _,a in pairs(game.level.entities) do if a._checker_live_placed and a.x and not a._ub2_ref then best=a end end;assert(best);best._ub2_ref={lua_value(tid)};best.invisible=nil;best.stealth=nil;best.inc_stealth=nil;U2B[#U2B+1]=best;return true")
                entry['frames'] = []
                for tile in (48, 64, 96):
                    bridge.lua(f'mb.setTile({tile});return true')
                    view = _set_vp(bridge.lua(CLEAN_VIEW % ('a._ub2_ref ~= nil', GROUP_CENTER)))
                    rows = bridge.lua("local o={};for _,a in ipairs(U2B) do local r=mb.row(a);r.ub2_ref=a._ub2_ref;o[#o+1]=r end;return o")
                    name = f'ub2-ben-{label}-{tile}'
                    ps = bridge.shot(name); cp, box = group_crop(view, ps, name, 2)
                    entry['frames'].append({'tile': tile, 'rows': rows, 'view': view, 'file': rel(ps), 'crop': rel(cp), 'crop_box': box, 'sha256': digest(cp)})
                bridge.lua('mb.setTile(64);return true')
            elif kind == 'ub2_guren':
                bridge.lua('mb.clearAround(8);_G.U2G={};return true')
                for (n, src, das, tid), (dx, dy) in zip([UB2_CASES[0], UB2_PALADIN], [(-2, 1), (2, 1)]):
                    bridge.lua(f"mb.place({lua_value(n)},{lua_value(src)},{dx},{dy},{lua_value(das)});local best;for _,a in pairs(game.level.entities) do if a._checker_live_placed and a.x and not a._ub2_ref then best=a end end;assert(best);best._ub2_ref={lua_value(tid)};best.invisible=nil;best.stealth=nil;best.inc_stealth=nil;U2G[#U2G+1]=best;return true")
                entry['frames'] = []
                for tile in (48, 64, 96):
                    bridge.lua(f'mb.setTile({tile});return true')
                    view = _set_vp(bridge.lua(CLEAN_VIEW % ('a._ub2_ref ~= nil', GROUP_CENTER)))
                    rows = bridge.lua("local o={};for _,a in ipairs(U2G) do local r=mb.row(a);r.ub2_ref=a._ub2_ref;o[#o+1]=r end;return o")
                    name = f'ub2-guren-paladin-{label}-{tile}'
                    ps = bridge.shot(name); cp, box = group_crop(view, ps, name, 2)
                    entry['frames'].append({'tile': tile, 'rows': rows, 'view': view, 'file': rel(ps), 'crop': rel(cp), 'crop_box': box, 'sha256': digest(cp)})
                bridge.lua('mb.setTile(64);return true')
            elif kind == 'ub2_epoch':
                n, src, das, tid = UB2_CASES[1]
                bridge.lua('mb.clearAround(8);return true')
                bridge.lua(f"return mb.place({lua_value(n)},{lua_value(src)},0,1,{lua_value(das)})")
                entry['before'] = bridge.lua("local a=assert(mb.byName('Epoch'));return {row=mb.row(a),can_multiply=a.can_multiply,has_talent=a:knowTalent('T_MULTIPLY') and true or false}")
                entry['use'] = bridge.lua(
                    "local a=assert(mb.byName('Epoch'));assert(a.can_multiply,'no can_multiply');"
                    "local before={};for _,x in pairs(game.level.entities) do before[x]=true end;"
                    "local old=a.getTarget;a.getTarget=function() return a.x+1,a.y,nil end;"
                    "local ok,err=pcall(a.forceUseTalent,a,'T_MULTIPLY',{ignore_energy=true,ignore_cd=true,no_talent_fail=true,silent=true});"
                    "a.getTarget=old;local clone;for _,x in pairs(game.level.entities) do if not before[x] and x.x and x~=a then clone=x end end;"
                    "a._ub2_epoch='original';if clone then clone._ub2_epoch='clone';clone.invisible=nil;clone.stealth=nil;clone.never_act=true end;"
                    "mb.refresh();return {ok=ok,err=tostring(err),original=mb.row(a),clone=clone and mb.row(clone) or false,"
                    "original_define_as=a.define_as or false,clone_define_as=clone and (clone.define_as or false) or false,"
                    "original_multiply=a.can_multiply,clone_name=clone and clone.name or false}")
                entry['frames'] = []
                for tile in (48, 64, 96):
                    bridge.lua(f'mb.setTile({tile});return true')
                    view = _set_vp(bridge.lua(CLEAN_VIEW % ('a._ub2_epoch ~= nil', GROUP_CENTER)))
                    rows = bridge.lua("local o={};for _,a in pairs(game.level.entities) do if a._ub2_epoch then local r=mb.row(a);r.ub2_epoch=a._ub2_epoch;o[#o+1]=r end end;return o")
                    name = f'ub2-epoch-{label}-{tile}'
                    ps = bridge.shot(name); cp, box = group_crop(view, ps, name, 2)
                    entry['frames'].append({'tile': tile, 'rows': rows, 'view': view, 'file': rel(ps), 'crop': rel(cp), 'crop_box': box, 'sha256': digest(cp)})
                bridge.lua('mb.setTile(64);return true')
            elif kind == 'ub2_negative':
                entry['cases'] = []
                bridge.lua('mb.clearAround(8);return true')
                anon = bridge.lua(
                    "local Map=require 'engine.Map';local p=game.player;"
                    "local q=require('mod.class.NPC').new({name='Limmir the Jeweler',type='humanoid',subtype='elf',"
                    "image='npc/humanoid_elf_limmir_the_jeweler.png',display='@',faction='players',rank=3,unique=true,max_life=200,life=200});"
                    "q:resolve();q:resolve(nil,true);local x,y=util.findFreeGrid(p.x+1,p.y+1,6,true,{[Map.ACTOR]=true});assert(x,'no free grid');"
                    "q._checker_live_placed=true;q.never_act=true;game.zone:addEntity(game.level,q,'actor',x,y);q._ub2_neg='anonymous-limmir';"
                    "mb.refresh();local r=mb.row(q);r.define_as_field=q.define_as or false;r.synthetic=true;return r")
                view = _set_vp(bridge.lua(CLEAN_VIEW % ("a._ub2_neg=='anonymous-limmir'", GROUP_CENTER)))
                ps = bridge.shot(f'ub2-negative-anonymous-limmir-{label}')
                cp, box = group_crop(view, ps, f'ub2-negative-anonymous-limmir-{label}', 1)
                entry['cases'].append({'key': 'anonymous-limmir', 'row': anon, 'view': view, 'crop': rel(cp)})
                cases = [
                    ('epoch-no-define', 'Epoch', UB2_CASES[1][1], 'EPOCH', 'a.define_as=nil'),
                    ('corrupted-oozemancer-wrong-define', 'Corrupted Oozemancer', UB2_CASES[2][1], 'CORRUPTED_OOZEMANCER', "a.define_as='OTHER_OOZEMANCER'"),
                    ('tannen-no-define', 'Tannen', UB2_CASES[9][1], 'TANNEN', 'a.define_as=nil'),
                    ('zemekkys-other-define', 'Zemekkys, Grand Keeper of Reality', UB2_CASES[3][1], 'ZEMEKKYS', "a.define_as='OTHER_ZEMEKKYS'"),
                ]
                for key, n, src, das, mut in cases:
                    bridge.lua('mb.clearAround(8);return true')
                    row = bridge.lua(
                        f"local r=mb.place({lua_value(n)},{lua_value(src)},1,1,{lua_value(das)});"
                        f"local a=mb.byName({lua_value(n)});assert(a,'no actor');{mut};"
                        "pcall(function() game:checkerRefreshActor(a,'display') end);mb.refresh();return mb.row(a)")
                    view = _set_vp(bridge.lua(CLEAN_VIEW % ('a._checker_live_placed', GROUP_CENTER)))
                    ps = bridge.shot(f'ub2-negative-{key}-{label}')
                    cp, box = group_crop(view, ps, f'ub2-negative-{key}-{label}', 1)
                    entry['cases'].append({'key': key, 'name': n, 'row': row, 'view': view, 'crop': rel(cp)})
                bridge.lua('mb.setTile(64);return true')
        except Exception as exc:  # recorded, the scene continues
            entry['error'] = str(exc)[:1500]
            print('STEP ERROR', label, step, str(exc)[:400], flush=True)
        record['steps'].append(entry)
    return record


def wait_ready(bridge, log_start):
    """Birth finished and its first save completed, then a trivial bridge call."""
    for _ in range(600):
        text = LOG.read_bytes()[log_start:].decode('utf-8', 'replace') if LOG.exists() else ''
        at = text.find('[CheckerFixture] BIRTH')
        if at >= 0 and ('Saving done.' in text[at:] or '保存完毕' in text[at:]):
            break
        time.sleep(.5)
    else:
        raise RuntimeError('fixture did not finish birth')
    time.sleep(3)
    bridge.raw("assert(game and game.player and game.level)")


def wait_fixture_free():
    """Never launch while another agent's fixture process is alive (shared session)."""
    for _ in range(360):
        try:
            meta = json.loads((SESSION / 'processes.json').read_text())
        except Exception:
            return
        alive = [k for k in ('game', 'xvfb') if meta.get(k) and (Path('/proc') / str(meta[k]) / 'cmdline').exists()]
        if not alive:
            return
        print('WAIT fixture busy', meta.get('game'), meta.get('xvfb'), flush=True)
        time.sleep(60)
    raise RuntimeError('fixture stayed busy')


def verify_aa(result):
    """Batch AA pass criteria: every expected id present in every check (never a subset)."""
    sc = result['scenes']
    fails, per = [], {}
    tall = set(TALL_BA)

    def steps(label, kind, name):
        return [st for st in sc.get(label, {}).get('steps', []) if st['step'][:2] == [kind, name]]

    where = {'ultimate faeros': 'charred-scar-L1', 'orc berserker': 'grushnak-pride-L1', 'dredge captain': 'temporal-rift-L1',
             'ultimate teluvorta': 'mark-teluvorta-L1', 'polar bear': 'old-forest-L1', 'anaconda': 'old-forest-L1',
             'necrotic abomination': 'blighted-ruins-L1', 'bone horror': 'blighted-ruins-L1', 'sanguine horror': 'blighted-ruins-L1',
             'barrow wight': 'dreadfell-L2', 'dreadmaster': 'dreadfell-L2', 'ogre warmaster': 'crypt-kryl-feijan-L1'}
    for n in BA:
        tid = EXPECT[n]
        lab = where[n]
        rec = {'scene': lab}
        got = steps(lab, 'natural_or_place', n)
        shots = got[0].get('shots', []) if got else []
        rec['source'] = got[0].get('resolved') if got else None
        rec['tiles'] = [x['tile'] for x in shots]
        ok = rec['tiles'] == [48, 64, 96] and all(
            x['row']['identify'] == tid and x['row']['rendered_token'] == tid and x['row']['explain'] == 'exact-identity' and x['row']['can_see']
            and (not x['row']['display_image'] or x['row']['display_image'].endswith('/' + tid + '.png')) and x['row']['display_image'] for x in shots)
        t1, t2 = steps(lab, 'toggle', n), steps(lab, 'toggle_again', n)
        tg = bool(t1 and t2) and t1[0]['off']['enabled'] is False and t1[0]['off']['still_mapped'] == 0 and not t1[0]['off']['row']['rendered_token'] \
            and t1[0]['on']['row']['rendered_token'] == tid and t2[0]['off']['still_mapped'] == 0 and t2[0]['on_later']['rendered_token'] == tid
        rec.update(draw_ok=bool(ok), toggle_ok=bool(tg), tall=n in tall)
        if not (ok and tg):
            fails.append(n)
        per[tid] = rec
    neg = steps('grushnak-pride-L1', 'native', 'orc elite berserker')
    negok = bool(neg) and neg[0].get('native_ok') is True and neg[0]['row']['identify'] is False and not neg[0]['row']['display_image'] \
        and not neg[0].get('native_view', {}).get('rendered_token') and bool(neg[0].get('native_view', {}).get('player_can_see'))
    if not negok:
        fails.append('negative orc elite berserker')
    summ = {}
    for lab in ('dreadmaster-minion-L1', 'dreadmaster-minion-zh-L1'):
        st = sc.get(lab, {}).get('steps', [])
        summ[lab] = bool(st) and st[0].get('ok') is True and 'error' not in st[0]
        if not summ[lab]:
            fails.append(lab)
    lin = {}
    for lab in ('mark-lineup-L1', 'mark-lineup-zh-L1'):
        st = [x for x in sc.get(lab, {}).get('steps', []) if x['step'][0] == 'lineup']
        rows = st[0].get('rows_after', []) if st else []
        by = {r[0]: r for r in rows}
        # rows_after is taken before the evidence view drops the innate stealth attribute, so only the identity is required there;
        # every picture row (seen_rows, after the clean view) must additionally be visible to the hero.
        ok = all(n in by and by[n][1] == EXPECT[n] and by[n][2] == EXPECT[n] for n in BA) and len(rows) == 12
        ok = ok and [x['tile'] for x in st[0]['shots']] == [48, 64, 96] and all(
            x['all_inside_viewport'] and {r[0] for r in x['seen_rows']} == set(BA) and all(r[3] and r[1] == r[2] == EXPECT[r[0]] for r in x['seen_rows']) for x in st[0]['shots'])
        lin[lab] = ok
        if not ok:
            fails.append(lab)
    lua_errors = {lab: rec.get('lua_errors') for lab, rec in sc.items()}
    step_errors = [(lab, x['step']) for lab, rec in sc.items() for x in rec.get('steps', []) if 'error' in x]
    if any(lua_errors.values()) or step_errors:
        fails.append('lua/step errors')
    missing = [sc_[0] for sc_ in SCENES_BA if sc_[0] not in sc]
    if missing:
        fails.append('missing scenes: ' + ','.join(missing))
    return {'per_id': per, 'negative_orc_elite_berserker_native': negok, 'dreadmaster_minion': summ, 'lineups': lin,
            'lua_errors': lua_errors, 'step_errors': step_errors, 'failures': fails, 'pass': not fails}


def verify_ab(result):
    """Batch AB pass criteria: every expected id present in every check (never a subset)."""
    sc = result['scenes']
    fails, per = [], {}
    tall = set(TALL_BB)

    def steps(label, kind, name):
        return [st for st in sc.get(label, {}).get('steps', []) if st['step'][:2] == [kind, name]]

    where = {'entrenched horror': 'lake-nur-L1', 'boiling horror': 'lake-nur-L1', 'swarm hive': 'lake-nur-L1', 'orc summoner': 'gorbat-pride-L1',
             'greater mummy': 'ancient-elven-ruins-L1', 'shadowblade': 'thieves-tunnels-L1', 'orc elite fighter': 'grushnak-pride-L1',
             'orc elite berserker': 'grushnak-pride-L1', 'venom wyrm': 'noxious-caldera-L1', 'ultimate shivgoroth': 'norgos-lair-L1',
             'Forest Troll Hedge-Wizard': 'trollmire-L1', 'alchemist golem': 'golem-graveyard-L1'}
    for n in BB:
        tid = EXPECT[n]
        lab = where[n]
        rec = {'scene': lab}
        got = steps(lab, 'natural_or_place', n)
        shots = got[0].get('shots', []) if got else []
        rec['source'] = got[0].get('resolved') if got else None
        rec['tiles'] = [x['tile'] for x in shots]
        ok = rec['tiles'] == [48, 64, 96] and all(
            x['row']['identify'] == tid and x['row']['rendered_token'] == tid and x['row']['explain'] == 'exact-identity' and x['row']['can_see']
            and x['row']['display_image'] and x['row']['display_image'].endswith('/' + tid + '.png') for x in shots)
        t1, t2 = steps(lab, 'toggle', n), steps(lab, 'toggle_again', n)
        tg = bool(t1 and t2) and t1[0]['off']['enabled'] is False and t1[0]['off']['still_mapped'] == 0 and not t1[0]['off']['row']['rendered_token'] \
            and t1[0]['on']['row']['rendered_token'] == tid and t2[0]['off']['still_mapped'] == 0 and t2[0]['on_later']['rendered_token'] == tid
        rec.update(draw_ok=bool(ok), toggle_ok=bool(tg), tall=n in tall)
        if not (ok and tg):
            fails.append(n)
        per[tid] = rec
    # Negatives
    neg = {}
    gv = [x for x in sc.get('thieves-tunnels-L1', {}).get('steps', []) if x['step'][0] == 'group_view']
    neg['shadowblade_vs_assassin'] = bool(gv) and gv[0].get('ok') is True and gv[0]['define_as'] == {'shadowblade': 'THIEF_ASSASSIN', 'assassin': 'THIEF_ASSASSIN'} \
        and {r['name']: r['identify'] for r in gv[0]['view']['rows']} == {'shadowblade': 'shadowblade', 'assassin': 'assassin'}
    pg = [x for x in sc.get('trollmire-L1', {}).get('steps', []) if x['step'][:2] == ['summon', 'alchemist_golem']]
    neg['player_alchemist_golem_native'] = bool(pg) and pg[0].get('ok') is True and pg[0]['summon']['identify'] is False and pg[0]['summon']['rendered_token'] is False \
        and bool(pg[0]['summon'].get('is_alchemist_golem')) and pg[0]['summon']['plain']['identify'] is False and pg[0]['summon']['plain']['rendered_token'] is False
    ar = [x for x in sc.get('arena-shadowblade-L1', {}).get('steps', []) if x['step'][:2] == ['native', 'shadowblade']]
    neg['arena_shadowblade_native'] = bool(ar) and ar[0].get('native_ok') is True and ar[0]['row']['define_as'] is False and ar[0]['row']['identify'] is False \
        and not ar[0]['row']['display_image'] and not ar[0].get('native_view', {}).get('rendered_token') and bool(ar[0].get('native_view', {}).get('player_can_see'))
    for k, v in neg.items():
        if not v:
            fails.append('negative ' + k)
    summ = {}
    hv = [x for x in sc.get('lake-nur-L1', {}).get('steps', []) if x['step'][0] == 'hive_summon']
    summ['swarm_hive_swarming_horrors'] = bool(hv) and hv[0].get('ok') is True and 'error' not in hv[0]
    for lab in ('orc-summoner-summons-L1', 'orc-summoner-summons-zh-L1'):
        ov = [x for x in sc.get(lab, {}).get('steps', []) if x['step'][0] == 'osummon']
        summ[lab] = bool(ov) and ov[0].get('ok') is True and 'error' not in ov[0]
    for k, v in summ.items():
        if not v:
            fails.append('summon ' + k)
    lin = {}
    for lab in ('mark-lineup-L1', 'mark-lineup-zh-L1'):
        st = [x for x in sc.get(lab, {}).get('steps', []) if x['step'][0] == 'lineup']
        rows = st[0].get('rows_after', []) if st else []
        by = {r[0]: r for r in rows}
        ok = all(n in by and by[n][1] == EXPECT[n] and by[n][2] == EXPECT[n] for n in BB) and len(rows) == 12
        ok = ok and [x['tile'] for x in st[0]['shots']] == [48, 64, 96] and all(
            x['all_inside_viewport'] and {r[0] for r in x['seen_rows']} == set(BB) and all(r[3] and r[1] == r[2] == EXPECT[r[0]] for r in x['seen_rows']) for x in st[0]['shots'])
        lin[lab] = ok
        if not ok:
            fails.append(lab)
    # Temporal Rift repro: pass = the measurement ran (both subjects present, visible, ids exact, 4 tile/state frames, attribution recorded).
    rr = [x for x in sc.get('rift-repro-L1', {}).get('steps', []) if x['step'][0] == 'rift_repro']
    rift = {'ran': bool(rr) and rr[0].get('ok') is True and 'error' not in rr[0]}
    if rift['ran']:
        e = rr[0]
        rift['ids_exact'] = all(any(r[0] == nm and r[1] == r[2] == tid for r in f['rows']) if f['state'] == 'on' else any(r[0] == nm and r[1] == tid and r[2] is False for r in f['rows'])
                                for f in e['frames'] for nm, tid in (('ultimate teluvorta', 'ultimate-teluvorta'), ('dredge', 'dredge')))
        rift['worst_changed'] = {f"{f['state']}-{f['tile']}": f['worst_changed'] for f in e['frames']}
        rift['covered_native_off'] = any(max(f['worst_changed'].values()) >= 0.25 for f in e['frames'] if f['state'] == 'off')
        rift['covered_token_on'] = any(max(f['worst_changed'].values()) >= 0.25 for f in e['frames'] if f['state'] == 'on')
        a = e['layer_attribution']
        rift['foreground_only_covers'] = max(a['foreground_only']['worst_changed'].values()) >= 0.15
        rift['weather_only_covers'] = max(a['weather_only']['worst_changed'].values()) >= 0.15
        rift['ran'] = rift['ids_exact']
    if not rift['ran']:
        fails.append('rift repro')
    lua_errors = {lab: rec.get('lua_errors') for lab, rec in sc.items()}
    step_errors = [(lab, x['step']) for lab, rec in sc.items() for x in rec.get('steps', []) if 'error' in x]
    if any(lua_errors.values()) or step_errors:
        fails.append('lua/step errors')
    missing = [sc_[0] for sc_ in SCENES_BB if sc_[0] not in sc]
    if missing:
        fails.append('missing scenes: ' + ','.join(missing))
    return {'per_id': per, 'negatives': neg, 'summons': summ, 'lineups': lin, 'rift_repro': rift,
            'lua_errors': lua_errors, 'step_errors': step_errors, 'failures': fails, 'pass': not fails}


def verify_ac(result):
    """Batch AC pass criteria: every expected id present in every check (never a subset)."""
    sc = result['scenes']
    fails, per = [], {}
    tall = set(TALL_BC)

    def steps(label, kind, name):
        return [st for st in sc.get(label, {}).get('steps', []) if st['step'][:2] == [kind, name]]

    where = {'Aletta Soultorn': 'dreadfell-L9', 'Filio Flightfond': 'dreadfell-L9', 'vampire lord': 'dreadfell-L9',
             'ruin banshee': 'rak-shor-pride-L3', 'Glacial Legion': 'rak-shor-pride-L3', 'Arch Zephyr': 'rak-shor-pride-L3',
             'Rotting Titan': 'rak-shor-pride-L3', 'Heavy Sentinel': 'rak-shor-pride-L3', 'Void Spectre': 'rak-shor-pride-L3',
             'orc high pyromancer': 'vor-armoury-L2', 'orc high cryomancer': 'vor-armoury-L2', 'oozing horror': 'lake-nur-L1',
             'abyssal horror': 'lake-nur-L1', 'umbral horror': 'lake-nur-L1', 'ungolmor': 'ardhungol-L3',
             'degenerated ogric mass': 'conclave-vault-L1', 'ogric abomination': 'conclave-vault-L1'}
    for n in BC:
        tid = EXPECT[n]
        lab = where[n]
        rec = {'scene': lab}
        got = steps(lab, 'natural_or_place', n)
        shots = got[0].get('shots', []) if got else []
        rec['source'] = got[0].get('resolved') if got else None
        rec['tiles'] = [x['tile'] for x in shots]
        ok = rec['tiles'] == [48, 64, 96] and all(
            x['row']['identify'] == tid and x['row']['rendered_token'] == tid and x['row']['explain'] == 'exact-identity' and x['row']['can_see']
            and x['row']['display_image'] and x['row']['display_image'].endswith('/' + tid + '.png') for x in shots)
        t1, t2 = steps(lab, 'toggle', n), steps(lab, 'toggle_again', n)
        tg = bool(t1 and t2) and t1[0]['off']['enabled'] is False and t1[0]['off']['still_mapped'] == 0 and not t1[0]['off']['row']['rendered_token'] \
            and t1[0]['on']['row']['rendered_token'] == tid and t2[0]['off']['still_mapped'] == 0 and t2[0]['on_later']['rendered_token'] == tid
        rec.update(draw_ok=bool(ok), toggle_ok=bool(tg), tall=n in tall)
        if not (ok and tg):
            fails.append(n)
        per[tid] = rec
    neg = {}
    vs = [x for x in sc.get('lake-nur-L1', {}).get('steps', []) if x['step'][0] == 'vilespawn']
    neg['vilespawn_native'] = bool(vs) and vs[0].get('ok') is True and 'error' not in vs[0]
    td = [x for x in sc.get('vor-armoury-L2', {}).get('steps', []) if x['step'][:2] == ['native', 'Training Dummy']]
    neg['training_dummy_native'] = bool(td) and td[0].get('native_ok') is True and td[0]['row']['identify'] is False and not td[0]['row']['display_image'] \
        and not td[0].get('native_view', {}).get('rendered_token') and bool(td[0].get('native_view', {}).get('player_can_see'))
    for k, v in neg.items():
        if not v:
            fails.append('negative ' + k)
    summ = {}
    for lab in ('vampire-lord-summons-L9', 'vampire-lord-summons-zh-L9'):
        ov = [x for x in sc.get(lab, {}).get('steps', []) if x['step'][0] == 'tsummon']
        summ[lab] = bool(ov) and ov[0].get('ok') is True and 'error' not in ov[0]
    for k, v in summ.items():
        if not v:
            fails.append('summon ' + k)
    lin = {}
    for lab, roster in (('mark-lineup-a-L1', TALL_BC), ('mark-lineup-b-L1', FLAT_BC), ('mark-lineup-a-zh-L1', TALL_BC), ('mark-lineup-b-zh-L1', FLAT_BC)):
        st = [x for x in sc.get(lab, {}).get('steps', []) if x['step'][0] == 'lineup']
        rows = st[0].get('rows_after', []) if st else []
        by = {r[0]: r for r in rows}
        ok = all(n in by and by[n][1] == EXPECT[n] and by[n][2] == EXPECT[n] for n in roster) and len(rows) == len(roster)
        ok = ok and [x['tile'] for x in st[0]['shots']] == [48, 64, 96] and all(
            x['all_inside_viewport'] and {r[0] for r in x['seen_rows']} == set(roster) and all(r[3] and r[1] == r[2] == EXPECT[r[0]] for r in x['seen_rows']) for x in st[0]['shots'])
        lin[lab] = ok
        if not ok:
            fails.append(lab)
    lua_errors = {lab: rec.get('lua_errors') for lab, rec in sc.items()}
    step_errors = [(lab, x['step']) for lab, rec in sc.items() for x in rec.get('steps', []) if 'error' in x]
    if any(lua_errors.values()) or step_errors:
        fails.append('lua/step errors')
    missing = [sc_[0] for sc_ in SCENES_BC if sc_[0] not in sc]
    if missing:
        fails.append('missing scenes: ' + ','.join(missing))
    return {'per_id': per, 'negatives': neg, 'summons': summ, 'lineups': lin,
            'lua_errors': lua_errors, 'step_errors': step_errors, 'failures': fails, 'pass': not fails}


def verify_ad(result):
    """Batch AD pass criteria: every expected id present in every check (never a subset)."""
    sc = result['scenes']
    fails, per = [], {}
    tall = set(TALL_BD)

    def steps(label, kind, name):
        return [st for st in sc.get(label, {}).get('steps', []) if st['step'][:2] == [kind, name]]

    where = {'orc grand summoner': 'gorbat-pride-L1', 'orc master wyrmic': 'gorbat-pride-L1', 'orc mage-hunter': 'gorbat-pride-L1',
             'ritch larva': 'ritch-tunnels-L3', 'ritch hunter': 'ritch-tunnels-L3', 'ritch hive mother': 'ritch-tunnels-L3',
             'Ritch Great Hive Mother': 'ritch-tunnels-L3', 'dúathedlen': 'demon-plane-L1', 'daelach': 'demon-plane-L1',
             'panther': 'shertul-fortress-L1', 'tiger': 'shertul-fortress-L1', 'sabertooth tiger': 'shertul-fortress-L1',
             'snow cat': 'shertul-fortress-L1', 'ice wyrm': 'daikara-L1'}
    for n in BD + ['Ritch Great Hive Mother']:
        tid = EXPECT[n]
        lab = where[n]
        rec = {'scene': lab}
        got = steps(lab, 'natural_or_place', n)
        shots = got[0].get('shots', []) if got else []
        rec['source'] = got[0].get('resolved') if got else None
        rec['tiles'] = [x['tile'] for x in shots]
        ok = rec['tiles'] == [48, 64, 96] and all(
            x['row']['identify'] == tid and x['row']['rendered_token'] == tid and x['row']['explain'] == 'exact-identity' and x['row']['can_see']
            and x['row']['display_image'] and x['row']['display_image'].endswith('/' + tid + '.png') for x in shots)
        t1, t2 = steps(lab, 'toggle', n), steps(lab, 'toggle_again', n)
        tg = bool(t1 and t2) and t1[0]['off']['enabled'] is False and t1[0]['off']['still_mapped'] == 0 and not t1[0]['off']['row']['rendered_token'] \
            and t1[0]['on']['row']['rendered_token'] == tid and t2[0]['off']['still_mapped'] == 0 and t2[0]['on_later']['rendered_token'] == tid
        rec.update(draw_ok=bool(ok), toggle_ok=bool(tg), tall=n in tall)
        if n in ('panther', 'tiger', 'sabertooth tiger', 'snow cat'):
            st = steps(lab, 'stealth', n)
            s0 = st[0] if st else {}
            rec['stealth'] = {'active': bool(s0.get('stealthed', {}).get('stealth_active')), 'identify_while_stealthed': s0.get('stealthed', {}).get('identify'),
                              'rendered_while_stealthed': s0.get('stealthed', {}).get('rendered_token'), 'player_can_see_stealthed': s0.get('stealthed', {}).get('player_can_see'),
                              'hidden_can_see': s0.get('hidden', {}).get('player_can_see'), 'hidden_rendered': s0.get('hidden', {}).get('rendered_token'),
                              'revealed_rendered': s0.get('revealed', {}).get('rendered_token')}
            sok = rec['stealth']['active'] and rec['stealth']['identify_while_stealthed'] == tid and (not rec['stealth']['player_can_see_stealthed'] or rec['stealth']['rendered_while_stealthed'] == tid) \
                and rec['stealth']['revealed_rendered'] == tid
            rec['stealth_ok'] = bool(sok)
            if not sok:
                fails.append('stealth ' + n)
        if not (ok and tg):
            fails.append(n)
        per[tid] = rec
    neg = {}
    p, u = EXPECT['ritch hive mother'], EXPECT['Ritch Great Hive Mother']
    neg['pool_vs_unique_distinct'] = p != u and per[p]['draw_ok'] and per[u]['draw_ok']
    nof = [x for x in sc.get('nicer-off-L1', {}).get('steps', []) if x['step'][0] == 'nicer_off']
    nrows = {r[0]: r for r in (nof[0].get('view_rows', []) if nof else [])}
    neg['nicer_off'] = {'duathedlen_native': bool(nrows.get('dúathedlen')) and nrows['dúathedlen'][1] is False and nrows['dúathedlen'][2] is False,
                        'snow_cat_maps': bool(nrows.get('snow cat')) and nrows['snow cat'][1] == 'snow-cat' and nrows['snow cat'][2] == 'snow-cat',
                        'ice_wyrm_maps': bool(nrows.get('ice wyrm')) and nrows['ice wyrm'][1] == 'ice-wyrm' and nrows['ice wyrm'][2] == 'ice-wyrm',
                        'nicer_off_during': bool(nof) and nof[0].get('nicer_during') is False and nof[0].get('nicer_restored') is True and 'error' not in nof[0],
                        'all_visible': bool(nrows) and all(r[3] for r in nrows.values())}
    neg['nicer_off_ok'] = all(neg['nicer_off'].values())
    rb = [x for x in sc.get('daikara-L1', {}).get('steps', []) if x['step'][:2] == ['randboss', 'ice wyrm']]
    neg['randboss_ice_wyrm_native'] = bool(rb) and rb[0].get('native_ok') is True and bool(rb[0]['row'].get('randboss')) and 'error' not in rb[0] and bool(rb[0]['row'].get('can_see', True))
    ss = [x for x in sc.get('stealth-seen-L1', {}).get('steps', []) if x['step'][0] == 'stealth_seen']
    neg['stealth_active_and_seen_tokens_drawn'] = bool(ss) and ss[0].get('ok') is True and 'error' not in ss[0]
    for k in ('pool_vs_unique_distinct', 'nicer_off_ok', 'randboss_ice_wyrm_native', 'stealth_active_and_seen_tokens_drawn'):
        if not neg[k]:
            fails.append('negative ' + k)
    lin = {}
    for lab, roster in (('mark-lineup-a-L1', TALL_BD), ('mark-lineup-b-L1', FLAT_BD), ('mark-lineup-a-zh-L1', TALL_BD), ('mark-lineup-b-zh-L1', FLAT_BD)):
        st = [x for x in sc.get(lab, {}).get('steps', []) if x['step'][0] == 'lineup']
        rows = st[0].get('rows_after', []) if st else []
        by = {r[0]: r for r in rows}
        ok = all(n in by and by[n][1] == EXPECT[n] and by[n][2] == EXPECT[n] for n in roster) and len(rows) == len(roster)
        ok = ok and [x['tile'] for x in st[0]['shots']] == [48, 64, 96] and all(
            x['all_inside_viewport'] and {r[0] for r in x['seen_rows']} == set(roster) and all(r[3] and r[1] == r[2] == EXPECT[r[0]] for r in x['seen_rows']) for x in st[0]['shots'])
        lin[lab] = ok
        if not ok:
            fails.append(lab)
    lua_errors = {lab: rec.get('lua_errors') for lab, rec in sc.items()}
    step_errors = [(lab, x['step']) for lab, rec in sc.items() for x in rec.get('steps', []) if 'error' in x]
    if any(lua_errors.values()) or step_errors:
        fails.append('lua/step errors')
    missing = [sc_[0] for sc_ in SCENES_BD if sc_[0] not in sc]
    if missing:
        fails.append('missing scenes: ' + ','.join(missing))
    return {'per_id': per, 'negatives': neg, 'lineups': lin, 'lua_errors': lua_errors, 'step_errors': step_errors, 'failures': fails, 'pass': not fails}


def verify_ae(result):
    """Batch AE pass criteria: every expected id present in every check; contract-bound negatives; temporal clones."""
    sc = result['scenes']
    fails, per = [], {}
    tall = set(TALL_BE)

    def steps(label, kind, name):
        return [st for st in sc.get(label, {}).get('steps', []) if st['step'][:2] == [kind, name]]

    where = {"champion of Urh'Rok": 'demon-plane-L1', 'forge-giant': 'demon-plane-L1', 'hummerhorn': 'old-forest-L1', 'spire dragon': 'daikara-L1',
             'blinkwyrm': 'daikara-L1', 'storm wyrm': 'gorbat-pride-L1', 'weaver matriarch': 'ardhungol-L3', 'patchwork troll': 'trollmire-L1',
             'maulotaur': 'trollmire-L1', 'worm that walks': 'lake-nur-L1', 'headless horror': 'lake-nur-L1', 'emperor wight': 'dreadfell-L9'}
    for n in BE:
        tid = EXPECT[n]
        lab = where[n]
        rec = {'scene': lab}
        got = steps(lab, 'natural_or_place', n)
        shots = got[0].get('shots', []) if got else []
        rec['source'] = got[0].get('resolved') if got else None
        rec['tiles'] = [x['tile'] for x in shots]
        ok = rec['tiles'] == [48, 64, 96] and all(
            x['row']['identify'] == tid and x['row']['rendered_token'] == tid and x['row']['explain'] == 'exact-identity' and x['row']['can_see']
            and x['row']['display_image'] and x['row']['display_image'].endswith('/' + tid + '.png') for x in shots)
        t1, t2 = steps(lab, 'toggle', n), steps(lab, 'toggle_again', n)
        tg = bool(t1 and t2) and t1[0]['off']['enabled'] is False and t1[0]['off']['still_mapped'] == 0 and not t1[0]['off']['row']['rendered_token'] \
            and t1[0]['on']['row']['rendered_token'] == tid and t2[0]['off']['still_mapped'] == 0 and t2[0]['on_later']['rendered_token'] == tid
        rec.update(draw_ok=bool(ok), toggle_ok=bool(tg), tall=n in tall)
        if not (ok and tg):
            fails.append(n)
        per[tid] = rec
    neg = {}
    # Burning Wake: forge-giant native sustain; champion force-learned. Token must survive with the aura entries present.
    au = [x for x in sc.get('demon-plane-L1', {}).get('steps', []) if x['step'][:2] == ['aura', 'forge-giant']]
    aa = (au[0].get('after') or au[0].get('before')) if au else None
    neg['forge_giant_burning_wake'] = {'wake_active': bool(aa and (aa.get('burning_wake') or au[0].get('activate', {}).get('ok'))),
                                       'identify': aa['row']['identify'] if aa else None, 'rendered': aa['row']['rendered_token'] if aa else None,
                                       'shader_auras': aa.get('shader_auras') if aa else None, 'aura_entries': aa.get('aura_entries') if aa else None,
                                       'can_see': aa['row']['can_see'] if aa else None}
    neg['forge_giant_burning_wake_ok'] = bool(aa) and neg['forge_giant_burning_wake']['identify'] == neg['forge_giant_burning_wake']['rendered'] == 'forge-giant' and neg['forge_giant_burning_wake']['wake_active']
    ul = [x for x in sc.get('demon-plane-L1', {}).get('steps', []) if x['step'][:2] == ['usetalent', "champion of Urh'Rok"]]
    ss = [x for x in sc.get('demon-plane-L1', {}).get('steps', []) if x['step'][:2] == ['sustain', "champion of Urh'Rok"]]
    cs = ss[0]['snap'] if ss else None
    neg['champion_burning_wake'] = {'use': ul[0].get('use') if ul else None, 'identify': cs['row']['identify'] if cs else None,
                                    'rendered': cs['row']['rendered_token'] if cs else None, 'sustains': cs.get('sustains') if cs else None,
                                    'shader_auras': cs.get('shader_auras') if cs else None, 'aura_entries': cs.get('aura_entries_in_display') if cs else None}
    neg['champion_burning_wake_ok'] = bool(cs) and cs['row']['identify'] == cs['row']['rendered_token'] == 'champion-of-urh-rok' and 'T_BURNING_WAKE' in (cs.get('sustains') or [])
    mu = [x for x in sc.get('old-forest-L1', {}).get('steps', []) if x['step'][:2] == ['multiply', 'hummerhorn']]
    neg['hummerhorn_multiply_ok'] = bool(mu) and mu[0].get('ok') is True and 'error' not in mu[0]
    neg['hummerhorn_multiply'] = {'rows': [[r['name'], r['identify'], r['rendered_token']] for r in mu[0]['cast']['rows']]} if mu and 'cast' in mu[0] else None
    ar = [x for x in sc.get('lake-nur-L1', {}).get('steps', []) if x['step'][:2] == ['native', 'headless horror']]
    neg['arena_headlesshorror_native'] = bool(ar) and ar[0].get('native_ok') is True and ar[0]['row'].get('define_as') == 'HEADLESSHORROR' and 'error' not in ar[0]
    for lab, nm in (('demon-plane-L1', 'forge-giant'), ('randboss-storm-L9', 'storm wyrm')):
        rb = [x for x in sc.get(lab, {}).get('steps', []) if x['step'][:2] == ['randboss', nm]]
        neg['randboss_' + nm.replace(' ', '_') + '_native'] = bool(rb) and rb[0].get('native_ok') is True and bool(rb[0]['row'].get('randboss')) and 'error' not in rb[0] and bool(rb[0]['row'].get('can_see', True))
    nof = [x for x in sc.get('nicer-off-L1', {}).get('steps', []) if x['step'][0] == 'nicer_off']
    nrows = {r[0]: r for r in (nof[0].get('view_rows', []) if nof else [])}
    neg['nicer_off_rows'] = {n: {'identify': nrows[n][1], 'rendered': nrows[n][2], 'can_see': nrows[n][3], 'image': nrows[n][4]} if n in nrows else None for n in TALL_BE}
    neg['nicer_off_consistent'] = bool(nof) and all(n in nrows and nrows[n][1] == nrows[n][2] and nrows[n][3] for n in TALL_BE) and nof[0].get('nicer_during') is False \
        and nof[0].get('nicer_restored') is True and 'error' not in nof[0]
    for k in ('forge_giant_burning_wake_ok', 'champion_burning_wake_ok', 'hummerhorn_multiply_ok', 'arena_headlesshorror_native', 'randboss_forge-giant_native',
              'randboss_storm_wyrm_native', 'nicer_off_consistent'):
        if not neg.get(k):
            fails.append('negative ' + k)
    lin = {}
    for lab, roster in (('mark-lineup-a-L1', TALL_BE), ('mark-lineup-b-L1', FLAT_BE), ('mark-lineup-a-zh-L1', TALL_BE), ('mark-lineup-b-zh-L1', FLAT_BE)):
        st = [x for x in sc.get(lab, {}).get('steps', []) if x['step'][0] == 'lineup']
        rows = st[0].get('rows_after', []) if st else []
        by = {r[0]: r for r in rows}
        ok = all(n in by and by[n][1] == EXPECT[n] and by[n][2] == EXPECT[n] for n in roster) and len(rows) == len(roster)
        ok = ok and [x['tile'] for x in st[0]['shots']] == [48, 64, 96] and all(
            x['all_inside_viewport'] and {r[0] for r in x['seen_rows']} >= set(roster) and all(r[3] for r in x['seen_rows']) and all(
                r[1] == r[2] == EXPECT[r[0]] for r in x['seen_rows'] if r[0] in roster) for x in st[0]['shots'])
        lin[lab] = ok
        if not ok:
            fails.append(lab)
    temporal = {}
    for lab in ('temporal-L1', 'temporal-zh-L1'):
        st = [x for x in sc.get(lab, {}).get('steps', []) if x['step'][0] == 'paradox']
        cases = {c['key']: c for c in (st[0].get('cases', []) if st else [])}
        res = {}
        for key, nm, _, mode in PARADOX_BE:
            c = cases.get(key)
            r = {'ok': False}
            if c and 'error' not in c and 'made' in c:
                cl, tg = c['made']['clone'], c['made']['target']
                if key in ('ae-tall-maulotaur', 'ae-flat-hummerhorn', 'older-orc-berserker', 'older-giant-spider'):
                    tid = EXPECT[nm]
                    want_clone = tid if nm != 'giant spider' else tid
                    r.update(clone_identify=cl['identify'], clone_rendered=cl['rendered_token'], clone_explain=cl['explain'], target_identify=tg['identify'],
                             display_name=cl['display_name'], clone_can_see=cl['can_see'])
                    r['ok'] = cl['identify'] == cl['rendered_token'] == tid and tg['identify'] == tg['rendered_token'] == tid and cl['can_see'] and tg['can_see']
                elif key == 'unique-wrathroot':
                    r.update(clone_identify=cl['identify'], clone_rendered=cl['rendered_token'], clone_explain=cl['explain'], target_identify=tg['identify'],
                             display_name=cl['display_name'], clone_can_see=cl['can_see'])
                    r['ok'] = cl['identify'] is False and cl['rendered_token'] is False and tg['identify'] == tg['rendered_token'] == 'wrathroot' and cl['can_see']
                else:
                    pb, pa = c.get('player_before', {}), c.get('player_after', {})
                    r.update(clone_identify=cl['identify'], clone_rendered=cl['rendered_token'], clone_explain=cl['explain'], display_name=cl['display_name'],
                             player_before=[pb.get('identify'), pb.get('rendered_token'), pb.get('display_image')], player_after=[pa.get('identify'), pa.get('rendered_token'), pa.get('display_image')])
                    r['ok'] = cl['identify'] is False and cl['rendered_token'] is False and pb.get('rendered_token') == pa.get('rendered_token') and pb.get('display_image') == pa.get('display_image')
                ex = c.get('expiry', {})
                r['expiry'] = ex
                r['expired_ok'] = bool(ex.get('dead')) and bool(ex.get('dead_by_unsummon')) and not ex.get('on_map_after')
                if mode == 'target':
                    after = {a[0]: a for a in c.get('after_rows', [])}
                    r['survivor_still_ok'] = bool(after.get(nm)) and after[nm][1] == after[nm][2] and after[nm][1] == (EXPECT[nm] if nm else False) and after[nm][3]
                    r['ok'] = r['ok'] and r['survivor_still_ok']
                r['ok'] = r['ok'] and r['expired_ok']
            else:
                r['error'] = c.get('error') if c else 'case missing'
            res[key] = r
            if not r['ok']:
                fails.append(f'temporal {lab} {key}')
        temporal[lab] = res
    lua_errors = {lab: rec.get('lua_errors') for lab, rec in sc.items()}
    step_errors = [(lab, x['step']) for lab, rec in sc.items() for x in rec.get('steps', []) if 'error' in x]
    if any(lua_errors.values()) or step_errors:
        fails.append('lua/step errors')
    required = [sc_[0] for sc_ in SCENES_BE]
    missing = [l for l in required if l not in sc]
    if missing:
        fails.append('missing scenes: ' + ','.join(missing))
    return {'per_id': per, 'negatives': neg, 'lineups': lin, 'temporal': temporal, 'lua_errors': lua_errors, 'step_errors': step_errors, 'failures': fails, 'pass': not fails}


def verify_af(result):
    """AF checks require complete sets; nicer-off explicitly records native fallbacks."""
    sc, failures, per = result['scenes'], [], {}
    def get(label, kind, name=None):
        return [x for x in sc.get(label, {}).get('steps', []) if x['step'][0] == kind and (name is None or x['step'][1] == name)]
    def exact(r, tid):
        return r.get('identify') == r.get('rendered_token') == tid and r.get('can_see') and r.get('seen')
    for n in BF:
        lab = 'horrors-L1' if n in BF[:4] else 'liches-L1' if n in BF[4:8] else 'blood-L1'
        tid = EXPECT[n]
        st = get(lab, 'natural_or_place', n)
        shots = st[0].get('shots', []) if st else []
        draw = [x['tile'] for x in shots] == [48, 64, 96] and all(exact(x['row'], tid) and x['row']['explain'] == 'exact-identity' and
            str(x['row'].get('display_image')).endswith('/' + tid + '.png') for x in shots)
        t1, t2 = get(lab, 'toggle', n), get(lab, 'toggle_again', n)
        toggle = bool(t1 and t2) and all(t[0].get('off', {}).get('enabled') is False and t[0]['off'].get('still_mapped') == 0 and
            t[0]['off']['row'].get('rendered_token') is False and t[0].get('on', {}).get('row', {}).get('rendered_token') == tid for t in (t1,t2)) and t2[0].get('on_later', {}).get('rendered_token') == tid
        per[tid] = {'scene': lab, 'source': st[0].get('resolved') if st else None, 'tiles': [x['tile'] for x in shots],
                    'native_tall': n in TALL_BF, 'draw_ok': bool(draw), 'toggle_ok': bool(toggle)}
        if not draw or not toggle: failures.append(n)
    lineups = {}
    for lab, roster, locale in [('lineup-L1', BF, 'en_US'), ('lineup-zh-L1', BF, 'zh_hans'),
            ('siblings-L1', ['radiant horror','luminous horror'], 'en_US'), ('liches-L1', BF[4:8], 'en_US')]:
        st = get(lab, 'lineup');shots = st[0].get('shots', []) if st else []
        ok = [x['tile'] for x in shots] == [48,64,96] and all(x['all_inside_viewport'] and
            {r[0] for r in x['seen_rows']} >= set(roster) and all(r[3] and r[1] == r[2] == EXPECT[r[0]] for r in x['seen_rows'] if r[0] in roster) for x in shots)
        ok = ok and sc.get(lab, {}).get('launch', {}).get('locale') == locale
        lineups[lab] = bool(ok)
        if not ok: failures.append('lineup ' + lab)
    nof = get('nicer-off-L1', 'nicer_off');rows = {r[0]: r for r in nof[0].get('view_rows', [])} if nof else {}
    nicer = {n: {'identify': rows[n][1], 'rendered_token': rows[n][2], 'can_see': rows[n][3], 'image': rows[n][4]} if n in rows else None for n in TALL_BF}
    # Default-name images match the two horrors and three liches. Animated blood's
    # undead/blood default-name PNG is absent (documented source-contract fallback).
    nicer_ok = bool(nof) and nof[0].get('nicer_during') is False and nof[0].get('nicer_restored') is True and all(
        n in rows and rows[n][3] and rows[n][1] == rows[n][2] == (False if n == 'animated blood' else EXPECT[n]) for n in TALL_BF)
    if not nicer_ok: failures.append('nicer-off contract')
    specials = {}
    for lab in ('blood-L1', 'blood-zh-L1'):
        b = get(lab, 'blood_edge');r = b[0].get('summon', {}) if b else {}
        ok = bool(b) and b[0].get('ok') is True and r.get('artifact') == 'BLOODEDGE' and r.get('target_cut') and r.get('summon_time') == 9
        if lab == 'blood-zh-L1': ok = ok and r.get('localized_name') != 'animated blood' and sc[lab]['launch']['locale'] == 'zh_hans'
        specials[lab] = bool(ok)
        if not ok: failures.append('Blood-Edge ' + lab)
    au = get('maelstrom-effects-L1', 'af_effect', 'maelstrom');a = au[0].get('snap', {}) if au else {}
    specials['maelstrom_aura_particles'] = bool(a) and exact(a['row'], 'maelstrom') and a.get('shader_auras', 0) >= 1 and a.get('aura_entries', 0) >= 1 and a.get('snowparticle') and a.get('snow_registered') and a.get('particles', 0) >= 1 and not a.get('body_entries')
    dh = get('dreaming-L1', 'af_effect', 'dreaming horror');d = dh[0].get('snap', {}) if dh else {}
    specials['dreaming_native_shader'] = bool(d) and d['row']['identify'] is False and d['row']['rendered_token'] is False and d['actor_shader'] == 'shadow_simulacrum' and d['row']['can_see']
    cl = get('temporal-L1','paradox');cases = cl[0].get('cases', []) if cl else []
    c = cases[0] if cases else {};made=c.get('made', {})
    specials['temporal_clone'] = bool(made) and exact(made['clone'],'archlich') and exact(made['target'],'archlich') and c.get('expiry', {}).get('dead_by_unsummon') and not c.get('expiry', {}).get('on_map_after')
    for k in ('maelstrom_aura_particles','dreaming_native_shader','temporal_clone'):
        if not specials[k]: failures.append(k)
    errors = [(lab,x['step'],x['error']) for lab,rec in sc.items() for x in rec.get('steps',[]) if 'error' in x]
    lua_errors = {lab:rec.get('lua_errors') for lab,rec in sc.items()}
    missing = [s[0] for s in SCENES_BF if s[0] not in sc]
    if errors or any(lua_errors.values()): failures.append('Lua/step errors')
    if missing: failures.append('missing scenes: ' + ','.join(missing))
    return {'per_id':per,'lineups':lineups,'nicer_off':nicer,'nicer_off_contract_ok':bool(nicer_ok),'specials':specials,
            'step_errors':errors,'lua_errors':lua_errors,'failures':failures,'pass':not failures,
            'visual_single_body_review':'pending: machine identity is not a draw-count proof'}


def verify_ag(result):
    """Complete AG identity, shader, toggle, locale, native and summon checks."""
    scenes=result.get('scenes', {})
    checks={}
    def exact(row, tid):
        return row.get('identify') == row.get('rendered_token') == tid and row.get('can_see') and row.get('seen')
    ids={c[3] for c in AG_CASES}
    cycles={}
    for label,nicer in (('lineup-L1',True),('nicer-off-L1',False),('lineup-zh-L1',True)):
        st=next((st for st in scenes.get(label,{}).get('steps',[]) if st['step'][0]=='ag_cycle'),{})
        states=st.get('states',[])
        good=len(states)==5 and not st.get('error') and st.get('nicer_tiles') is nicer and scenes.get(label,{}).get('launch',{}).get('locale') == ('zh_hans' if '-zh-' in label else 'en_US')
        detail={}
        for state in states:
            rows=state['rows']
            good=good and {r['ag_id'] for r in rows}==ids and len(rows)==7
            if state['enabled']:
                good=good and all(exact(r,r['ag_id']) for r in rows)
            else:
                good=good and all(not r['rendered_token'] and not r['display_image'] for r in rows)
            for view in state['views']:
                good=good and len(view['rows'])==7 and all(r['can_see'] and r['seen'] for r in view['rows'])
            if state['round'] < 2:
                for tile in (48,64,96):
                    frames=[f for f in state['frames'] if f['tile']==tile]
                    good=good and len(frames)==3
                    if len(frames)!=3: continue
                    for tid in sorted(ids):
                        hashes=[next(a['tile_sha256'] for a in f['subjects'] if a['id']==tid) for f in frames]
                        row=next(r for r in rows if r['ag_id']==tid)
                        shader_expected='quad_hue' if tid in ('multi-hued-crystal','shimmering-crystal') or (not nicer and 'hued' in tid) else False
                        key=f"r{state['round']}-{'token' if state['enabled'] else 'native'}-{tile}-{tid}"
                        d={'shader':row['shader'],'shader_args':row['shader_args'],'unique_tile_frames':len(set(hashes)),
                           'intervals_s':[round(frames[i+1]['time_monotonic']-frames[i]['time_monotonic'],3) for i in (0,1)]}
                        detail[key]=d
                        good=good and row['shader']==shader_expected and row['shader_args'] is False
                        if state['enabled']:
                            good=good and len(set(hashes))==1 and not row['replacement_shader']
                        elif shader_expected:
                            good=good and len(set(hashes))>1
        checks[label]=bool(good);cycles[label]=detail
    st=next((st for st in scenes.get('negative-L1',{}).get('steps',[]) if st['step'][0]=='ag_negative'),{})
    checks['composite_negatives']=len(st.get('cases',[]))==2 and all(not c['row']['identify'] and not c['row']['rendered_token'] and all(r['can_see'] for r in c['view']['rows']) for c in st.get('cases',[]))
    pair=st.get('shadow_pair',[])
    checks['shadow_pair']=len(pair)==3 and all(len(p['view']['rows'])==2 and {r['define_as'] for r in p['view']['rows']}=={'SHADOW_CLAW','SHADOW_CASTER'} and all(exact(r,'shadow-caster' if r['define_as']=='SHADOW_CASTER' else 'shadow-claw') for r in p['view']['rows']) for p in pair)
    ns=st.get('shader_negatives',[])
    checks['strict_shader_contract']=len(ns)==2 and all(not n['row']['identify'] and not n['row']['rendered_token'] and n['row']['can_see'] for n in ns)
    for name in ('dreaming','assassin'):
        r=st.get(name,{})
        checks[name+'_native']=bool(r) and not r['identify'] and not r['rendered_token'] and r['shader']=='shadow_simulacrum'
    st=next((st for st in scenes.get('temporal-L1',{}).get('steps',[]) if st['step'][0]=='paradox'),{})
    cases=st.get('cases',[])
    checks['temporal']=len(cases)==2 and {c['key'] for c in cases}=={'ag-drake','ag-caster'} and all(not c.get('error') and exact(c['made']['target'],'shadow-caster' if c['key']=='ag-caster' else 'multi-hued-drake') and exact(c['made']['clone'],'shadow-caster' if c['key']=='ag-caster' else 'multi-hued-drake') and len(c['view_rows'])==2 and all(r[3] for r in c['view_rows']) and c['expiry']['dead_by_unsummon'] and not c['expiry']['on_map_after'] for c in cases)
    for label in ('blood-L1','blood-zh-L1'):
        st=next((st for st in scenes.get(label,{}).get('steps',[]) if st['step'][0]=='blood_edge'),{})
        checks[label]=st.get('ok',False)
    checks['no_lua_or_step_errors']=len(scenes)==7 and all(not sc.get('lua_errors') and all(not st.get('error') for st in sc['steps']) for sc in scenes.values())
    return {'ok':all(checks.values()),'checks':checks,'cycles':cycles}


def verify_ua(result):
    """Require both real locales, all sizes/cycles and native appearance negatives."""
    scenes=result.get('scenes',{})
    def step(label,kind,mode=None):
        return next((e for e in scenes.get(label,{}).get('steps',[]) if e['step'][0]==kind and (mode is None or e['step'][1]==mode)),{})
    def exact(r):
        return r['identify']==r['rendered_token']==r['ua_id'] and str(r['display_image']).endswith('/'+r['ua_id']+'.png')
    checks={}
    for label,locale in [('lineup-L1','en_US'),('lineup-zh-L1','zh_hans')]:
        states=step(label,'ua_group','lineup').get('states',[])
        checks[label]=[(st['enabled'],st['round']) for st in states]==[(True,0),(False,1),(True,1),(False,2),(True,2)] and scenes.get(label,{}).get('launch',{}).get('locale')==locale
        for st in states:
            frames=st.get('frames',[])
            checks[label]=checks[label] and {f['tile'] for f in frames}=={48,64,96}
            for f in frames:
                rows=f['rows']
                checks[label]=checks[label] and len(rows)==12 and {r['ua_id'] for r in rows}=={c[3] for c in UA_CASES}
                checks[label]=checks[label] and all(r['can_see'] and r['seen'] for r in rows)
                checks[label]=checks[label] and all(exact(r) if st['enabled'] else not r['rendered_token'] and not r['display_image'] for r in rows)
        checks[label+'-rank']=bool(states) and all(r['badge']==('elite_boss' if r['rank']==5 else 'boss' if r['rank']==4 else 'unique') for st in states for f in st['frames'] for r in f['rows'])
        checks[label+'-single-body']=bool(states) and all(0 < r['replacement_display_h'] <= 1 and all(m.get('_isshaderaura') for m in (r['replacement_add_mos'] or [])) for st in states if st['enabled'] for f in st['frames'] for r in f['rows'])
    badge=step('badge-L1','ua_group','badge');states=badge.get('states',[])
    checks['badge-independent']=len(badge.get('before',[]))==12 and len(states)==1 and all(exact(r) and not r['badge'] for f in states[0]['frames'] for r in f['rows']) and all(r['identify']==r['rendered_token'] for r in badge.get('before',[]))
    for mode in ('kin-orc','kin-weaver','kin-horror','kin-warg'):
        states=step('kin-L1','ua_group',mode).get('states',[])
        checks[mode]=len(states)==1 and {f['tile'] for f in states[0]['frames']}=={48,64,96} and all(exact(r) and r['can_see'] and r['seen'] for f in states[0]['frames'] for r in f['rows'])
    for label,locale in [('prefix-L1','en_US'),('prefix-zh-L1','zh_hans')]:
        states=step(label,'ua_group','prefix').get('states',[])
        checks[label]=len(states)==1 and scenes.get(label,{}).get('launch',{}).get('locale')==locale and {f['tile'] for f in states[0]['frames']}=={48,64,96}
        checks[label]=checks[label] and all(len(f['rows'])==6 and len({r['name'] for r in f['rows']})==6 and all(exact(r) and r['can_see'] and r['seen'] for r in f['rows']) for f in states[0]['frames'])
    neg=step('negative-L1','ua_negative');cases=neg.get('cases',[])
    checks['same-name-negative']=len(cases)==5 and all(not c['row']['identify'] and not c['row']['rendered_token'] and not c['row']['display_image'] and c['view']['rows'][0]['can_see'] for c in cases)
    checks['shade']=any(c['id']=='the-shade-native' and c['row']['shader']=='unique_glow' and not c['row']['rendered_token'] for c in cases)
    forms=neg.get('phoenix',[])
    checks['phoenix']=len(forms)==9 and all((not f['row']['identify'] and not f['row']['rendered_token'] and f['row']['image']=='object/egg_dragons_egg_06_64.png') if f['form']=='egg' else f['row']['identify']==f['row']['rendered_token']=='phoenix' for f in forms) and all(f['view']['rows'][0]['can_see'] and f['view']['rows'][0]['seen'] for f in forms)
    required={s[0] for s in SCENES_UA}
    checks['no-errors']=required.issubset(scenes) and all(scenes[k]['lua_errors']==0 and all(not e.get('error') for e in scenes[k]['steps']) for k in required)
    return {'checks':checks,'all_ok':all(checks.values())}


def verify_ta1(result):
    """Batch TA-1: thirteen town residents, tall bodies, escort, negatives, both locales."""
    sc, failures, per = result.get('scenes', {}), [], {}

    def step(label, kind, prefix=None):
        return [x for x in sc.get(label, {}).get('steps', [])
                if x['step'][0] == kind and (prefix is None or x['step'][1:2] == [prefix])]

    def exact(r, tid):
        return (r.get('identify') == r.get('rendered_token') == tid and r.get('can_see')
                and r.get('explain') == 'exact-identity' and str(r.get('display_image')).endswith('/' + tid + '.png'))

    where = {'apprentice mage': 'angolwen-L1', 'pyromancer': 'angolwen-L1', 'cryomancer': 'angolwen-L1',
             'geomancer': 'angolwen-L1', 'tempest': 'angolwen-L1', 'human guard': 'gates-of-morning-L1',
             'derth guard': 'derth-L1', 'last hope guard': 'last-hope-L1', 'halfling guard': 'last-hope-L1',
             'dwarven guard': 'iron-council-L1', 'elvala guard': 'elvala-L1',
             'slaver': 'ring-of-blood-L1', 'enthralled slave': 'ring-of-blood-L1'}
    for n in TA1:
        tid, lab = EXPECT[n], where[n]
        st = step(lab, 'natural_or_place', n)
        shots = st[0].get('shots', []) if st else []
        draw = [x['tile'] for x in shots] == [48, 64, 96] and all(exact(x['row'], tid) for x in shots)
        t1, t2 = step(lab, 'toggle', n), step(lab, 'toggle_again', n)
        tg = bool(t1 and t2) and all(
            t[0].get('off', {}).get('enabled') is False and t[0]['off'].get('still_mapped') == 0
            and t[0]['off']['row'].get('rendered_token') is False
            and t[0].get('on', {}).get('row', {}).get('rendered_token') == tid for t in (t1, t2)) \
            and t2[0].get('on_later', {}).get('rendered_token') == tid
        per[tid] = {'scene': lab, 'source': st[0].get('resolved') if st else None, 'tiles': [x['tile'] for x in shots],
                    'native_tall': n in TA1_TALL, 'draw_ok': bool(draw), 'toggle_ok': bool(tg)}
        if not draw or not tg:
            failures.append(n)
    # Tall-body token metadata (one body; visual draw-once review is separate).
    tm = step('angolwen-L1', 'ta1_meta')
    tall_meta = {}
    if tm:
        for r in tm[0].get('rows', []):
            if r['name'] in TA1_TALL:
                tall_meta[r['name']] = {'identify': r['identify'], 'rendered': r['rendered_token'],
                                        'replacement_display_h': r.get('replacement_display_h'),
                                        'replacement_display_y': r.get('replacement_display_y'),
                                        'replacement_add_mos': r.get('replacement_add_mos'),
                                        'own_image': r.get('own_image'), 'own_add_mos': r.get('own_add_mos'),
                                        'shader': r.get('shader')}
    tall_ok = len(tall_meta) == len(TA1_TALL) and all(
        v['identify'] == v['rendered'] == EXPECT[n] and not v['shader'] for n, v in tall_meta.items())
    if not tall_ok:
        failures.append('tall metadata')
    # Combined thirteen lineups (en_US and zh_hans) plus the six-guard board.
    lineups = {}
    for lab, prefix, roster, locale in (('mark-lineup-L1', 'ta1-all', TA1, 'en_US'),
                                        ('mark-lineup-zh-L1', 'ta1-all-zh', TA1, 'zh_hans'),
                                        ('mark-guards-L1', 'ta1-guards', TA1_GUARDS, 'en_US')):
        st = step(lab, 'lineup', prefix)
        shots = st[0].get('shots', []) if st else []
        ok = [x['tile'] for x in shots] == [48, 64, 96] and all(
            x.get('all_inside_viewport') and {r[0] for r in x.get('seen_rows', [])} >= set(roster)
            and all(r[3] and r[1] == r[2] == EXPECT[r[0]] for r in x.get('seen_rows', []) if r[0] in roster)
            for x in shots)
        ok = ok and sc.get(lab, {}).get('launch', {}).get('locale') == locale
        lineups[lab] = bool(ok)
        if not ok:
            failures.append('lineup ' + lab)
    sib = step('mark-guards-L1', 'lineup', 'ta1-guard-siblings')
    sib_rows = sib[0].get('shots', [{}])[0].get('seen_rows', []) if sib else []
    sib_ok = bool(sib) and {r[0] for r in sib_rows} >= {'human guard', 'elven guard', 'caravan guard'} and all(
        r[3] and r[1] == r[2] for r in sib_rows)
    lineups['mark-guard-siblings'] = bool(sib_ok)
    if not sib_ok:
        failures.append('guard siblings')
    # native_tall bodies with nicer_tiles off (fresh placements) must still map.
    nof = step('mark-nicer-off-L1', 'nicer_off')
    nrows = {r[0]: r for r in (nof[0].get('view_rows', []) if nof else [])}
    nicer = {n: {'identify': nrows[n][1], 'rendered': nrows[n][2], 'can_see': nrows[n][3], 'image': nrows[n][4]}
             if n in nrows else None for n in TA1_TALL}
    nicer_ok = bool(nof) and nof[0].get('nicer_during') is False and nof[0].get('nicer_restored') is True and all(
        n in nrows and nrows[n][3] and nrows[n][1] == nrows[n][2] == EXPECT[n] for n in TA1_TALL)
    if not nicer_ok:
        failures.append('nicer-off')
    # Slaver's native make_escort copies wear the enthralled-slave token.
    es = step('ring-of-blood-L1', 'ta1_escort')
    escort_ok = bool(es) and es[0].get('ok') is True and len(es[0].get('escorts', [])) >= 2
    if not escort_ok:
        failures.append('escort')
    # Appearance negatives.
    neg = step('mark-negative-L1', 'ta1_negative')
    neg_ok = bool(neg) and len(neg[0].get('cases', [])) == 3 and all(
        not c['row']['identify'] and not c['row']['rendered_token'] and not c['row']['display_image']
        and c['view']['rows'][0]['can_see'] for c in neg[0].get('cases', []))
    if neg and neg[0].get('cases'):
        sh = next((c for c in neg[0]['cases'] if c['key'] == 'added-shader'), None)
        neg_ok = neg_ok and bool(sh) and sh['row'].get('explain') == 'shader'
    dn = neg[0].get('different_name') if neg else None
    neg_ok = neg_ok and bool(dn) and not dn['row']['identify'] and not dn['row']['rendered_token']
    if not neg_ok:
        failures.append('negatives')
    errors = [(lab, x.get('step'), x.get('error')) for lab, rec in sc.items() for x in rec.get('steps', []) if 'error' in x]
    lua_errors = {lab: rec.get('lua_errors') for lab, rec in sc.items()}
    missing = [s[0] for s in SCENES_TA1 if s[0] not in sc]
    if errors or any(lua_errors.values()):
        failures.append('Lua/step errors')
    if missing:
        failures.append('missing scenes: ' + ','.join(missing))
    return {'per_id': per, 'tall_meta': tall_meta, 'tall_ok': bool(tall_ok), 'lineups': lineups,
            'nicer_off': nicer, 'nicer_ok': bool(nicer_ok),
            'escort': {'ok': bool(escort_ok),
                       'rows': [[r['name'], r['identify'], r['rendered_token']] for r in (es[0]['escorts'] if es else [])]},
            'negatives': (neg[0] if neg else None), 'step_errors': errors, 'lua_errors': lua_errors,
            'failures': failures, 'pass': not failures,
            'visual_single_body_review': 'pending: machine identity is not a draw-count proof'}


def verify_ta2(result):
    """Batch TA-2: fourteen town/wilds residents, both locales, tall bodies,
    the Derth/Arena slinger split, the lumberjack `defined_as` typo, the anomaly
    and Wayist same-name summons, the two archers, the aura sustains and the
    different-name / wrong-body negatives."""
    sc, failures, per = result.get('scenes', {}), [], {}

    def step(label, kind, prefix=None):
        return [x for x in sc.get(label, {}).get('steps', [])
                if x['step'][0] == kind and (prefix is None or x['step'][1:2] == [prefix])]

    def exact(r, tid):
        return (r.get('identify') == r.get('rendered_token') == tid and r.get('can_see')
                and r.get('explain') == 'exact-identity' and str(r.get('display_image')).endswith('/' + tid + '.png'))

    where = {'human citizen': 'last-hope-L1', 'halfling citizen': 'last-hope-L1',
             'human farmer': 'derth-L1', 'halfling gardener': 'derth-L1', 'halfling slinger': 'derth-L1',
             'lumberjack': 'lumberjack-L1', 'dwarven earthwarden': 'iron-council-L1',
             'yeek mindslayer': 'irkkk-L1', 'yeek psionic': 'irkkk-L1',
             'thalore hunter': 'shatur-L1', 'thalore wilder': 'shatur-L1',
             'elven sun-mage': 'gates-of-morning-L1', 'elven archer': 'gates-of-morning-L1',
             'shalore rune master': 'elvala-L1'}
    # 1. Per-id 48/64/96 exact identity + two off/on cycles in their real towns.
    for n in TA2:
        tid, lab = EXPECT[n], where[n]
        st = step(lab, 'natural_or_place', n)
        shots = st[0].get('shots', []) if st else []
        draw = [x['tile'] for x in shots] == [48, 64, 96] and all(exact(x['row'], tid) for x in shots)
        t1, t2 = step(lab, 'toggle', n), step(lab, 'toggle_again', n)
        tg = bool(t1 and t2) and all(
            t[0].get('off', {}).get('enabled') is False and t[0]['off'].get('still_mapped') == 0
            and t[0]['off']['row'].get('rendered_token') is False
            and t[0].get('on', {}).get('row', {}).get('rendered_token') == tid for t in (t1, t2)) \
            and t2[0].get('on_later', {}).get('rendered_token') == tid
        per[tid] = {'scene': lab, 'source': st[0].get('resolved') if st else None, 'tiles': [x['tile'] for x in shots],
                    'native_tall': n in TA2_TALL, 'draw_ok': bool(draw), 'toggle_ok': bool(tg)}
        if not draw or not tg:
            failures.append(n)
    # 2. Tall-body token metadata (one body; the draw-once judgement is a human crop review).
    tm = step('mark-lineup-L1', 'ta2_meta')
    tall_meta = {}
    if tm:
        for r in tm[0].get('rows', []):
            if r['name'] in TA2_TALL:
                tall_meta[r['name']] = {'identify': r['identify'], 'rendered': r['rendered_token'],
                                        'replacement_display_h': r.get('replacement_display_h'),
                                        'replacement_display_y': r.get('replacement_display_y'),
                                        'replacement_add_mos': r.get('replacement_add_mos'),
                                        'own_image': r.get('own_image'), 'own_add_mos': r.get('own_add_mos'),
                                        'shader': r.get('shader')}
    tall_ok = len(tall_meta) == len(TA2_TALL) and all(
        v['identify'] == v['rendered'] == EXPECT[n] and not v['shader']
        and v['own_image'] == 'invis.png'
        and len([m for m in (v['own_add_mos'] or []) if not m.get('aura')]) == 1
        and next(m for m in v['own_add_mos'] if not m.get('aura'))['display_h'] == 2
        and next(m for m in v['own_add_mos'] if not m.get('aura'))['display_y'] == -1
        and not [m for m in (v['replacement_add_mos'] or []) if not m.get('aura')] for n, v in tall_meta.items())
    if not tall_ok:
        failures.append('tall metadata')
    # 3. Fourteen lineups (en_US and zh_hans), 48/64/96.
    lineups = {}
    for lab, prefix, locale in (('mark-lineup-L1', 'ta2-all', 'en_US'),
                                ('mark-lineup-zh-L1', 'ta2-all-zh', 'zh_hans')):
        st = step(lab, 'lineup', prefix)
        shots = st[0].get('shots', []) if st else []
        ok = [x['tile'] for x in shots] == [48, 64, 96] and all(
            x.get('all_inside_viewport') and {r[0] for r in x.get('seen_rows', [])} >= set(TA2)
            and all(r[3] and r[1] == r[2] == EXPECT[r[0]] for r in x.get('seen_rows', []) if r[0] in TA2)
            for x in shots)
        ok = ok and sc.get(lab, {}).get('launch', {}).get('locale') == locale
        lineups[lab] = bool(ok)
        if not ok:
            failures.append('lineup ' + lab)
    # 4. nicer_tiles off/on round trip: every identity still maps with nicer tiles off.
    nof = step('mark-nicer-off-L1', 'nicer_off')
    nrows = {r[0]: r for r in (nof[0].get('view_rows', []) if nof else [])}
    nicer = {n: {'identify': nrows[n][1], 'rendered': nrows[n][2], 'can_see': nrows[n][3], 'image': nrows[n][4]}
             if n in nrows else None for n in TA2}
    nicer_ok = bool(nof) and nof[0].get('nicer_during') is False and nof[0].get('nicer_restored') is True and all(
        n in nrows and nrows[n][3] and nrows[n][1] == nrows[n][2] == EXPECT[n] for n in TA2)
    if not nicer_ok:
        failures.append('nicer-off')
    # 5. Derth slinger positive; Arena SLINGER stays native.
    sl = (step('derth-L1', 'ta2_slinger') or [{}])[0]
    derth, arena = sl.get('derth', {}), sl.get('arena', {})
    slinger_ok = exact(derth, 'halfling-slinger') and arena.get('define_as') == 'SLINGER' \
        and not arena.get('identify') and not arena.get('rendered_token') and not arena.get('display_image')
    if not slinger_ok:
        failures.append('slinger')
    # 6. Lumberjack: no runtime define_as (the source writes `defined_as`).
    lj = (step('lumberjack-L1', 'ta2_lumberjack') or [{}])[0].get('row', {})
    lumberjack_ok = exact(lj, 'lumberjack') and not lj.get('define_as')
    if not lumberjack_ok:
        failures.append('lumberjack')
    # 7. Wayist yeek mindslayer summon wears the tall token.
    wy = (step('irkkk-L1', 'ta2_wayist') or [{}])[0].get('use', {})
    wrows = wy.get('rows', [])
    wayist_ok = bool(wy.get('ok')) and bool(wrows) and all(
        r.get('summoner_is_player') and r.get('tall_body') and exact(r, 'yeek-mindslayer') for r in wrows)
    if not wayist_ok:
        failures.append('wayist')
    # 8. Anomaly townsfolk: farmer/gardener wear the token; scribe and dwarven lumberjack stay native.
    an = (step('elvala-L1', 'ta2_anomaly') or [{}])[0].get('use', {})
    arows = {r.get('anomaly_name'): r for r in an.get('rows', [])}
    anomaly_ok = bool(an.get('ok')) and 'human farmer' in arows and exact(arows['human farmer'], 'human-farmer') \
        and 'halfling gardener' in arows and exact(arows['halfling gardener'], 'halfling-gardener') \
        and 'shalore scribe' in arows and not arows['shalore scribe'].get('identify') \
        and not arows['shalore scribe'].get('rendered_token')
    if 'dwarven lumberjack' in arows:
        anomaly_ok = anomaly_ok and not arows['dwarven lumberjack'].get('identify')
    if not anomaly_ok:
        failures.append('anomaly')
    # 9. Elven archer and companion archer side by side; identical token PNG bytes.
    ar = (step('gates-of-morning-L1', 'ta2_archers') or [{}])[0]
    archer_ok = exact(ar.get('archer', {}), 'elven-archer') and exact(ar.get('companion', {}), 'companion-archer')
    try:
        import zipfile
        with zipfile.ZipFile(result['runtime_teaa']['path']) as z:
            ea = z.read('data/gfx/tokens/elven-archer.png')
            ca = z.read('data/gfx/tokens/companion-archer.png')
        archer_same_png = ea == ca
    except Exception as exc:  # recorded, not hidden
        archer_same_png = False
        result.setdefault('diagnostics', {})['archer_png_error'] = str(exc)[:200]
    if not archer_ok or not archer_same_png:
        failures.append('archers')
    # 10. Aura sustains: token stays, no actor shader, native aura present.
    auras = {}
    for lab, nm, tid, key in (('iron-council-L1', 'dwarven earthwarden', 'T_BODY_OF_STONE', 'body-of-stone'),
                              ('gates-of-morning-L1', 'elven sun-mage', 'T_CHANT_OF_LIGHT', 'chant-of-light')):
        a = (step(lab, 'ta2_aura', nm) or [{}])[0]
        during, before = a.get('during', {}), a.get('before', {})
        row = during.get('row', {})
        aura_present = bool(during.get('shader_auras')) or any('AURA:' in m for m in (during.get('add_mos') or [])) \
            or bool(during.get('particles'))
        good = during.get('sustained') is True and exact(row, EXPECT[nm]) \
            and during.get('actor_shader') is False and aura_present
        auras[key] = {'sustained_before': before.get('sustained'), 'during': {k: during.get(k) for k in
                      ('sustained', 'actor_shader', 'shader_auras', 'add_mos', 'particles')}, 'ok': bool(good)}
        if not good:
            failures.append('aura ' + key)
    # 11. Negatives: different-name PNG reuses, wrong body and synthetic Novice mage.
    neg = (step('mark-negative-L1', 'ta2_negative') or [{}])[0]
    cases = neg.get('cases', [])
    neg_ok = len(cases) == len(TA2_NEG_CASES) and all(
        not c['row']['identify'] and not c['row']['rendered_token'] and not c['row']['display_image']
        and c['view']['rows'] and c['view']['rows'][0]['can_see'] for c in cases)
    nv = neg.get('novice')
    neg_ok = neg_ok and bool(nv) and not nv['row']['identify'] and not nv['row']['rendered_token']
    if not neg_ok:
        failures.append('negatives')
    # 12. Clean runs and complete scenes.
    errors = [(lab, x.get('step'), x.get('error')) for lab, rec in sc.items() for x in rec.get('steps', []) if 'error' in x]
    lua_errors = {lab: rec.get('lua_errors') for lab, rec in sc.items()}
    missing = [s[0] for s in SCENES_TA2 if s[0] not in sc]
    if errors or any(lua_errors.values()):
        failures.append('Lua/step errors')
    if missing:
        failures.append('missing scenes: ' + ','.join(missing))
    return {'per_id': per, 'tall_meta': tall_meta, 'tall_ok': bool(tall_ok), 'lineups': lineups,
            'nicer_off': nicer, 'nicer_ok': bool(nicer_ok),
            'slinger': {'derth': {k: derth.get(k) for k in ('identify', 'rendered_token', 'define_as')},
                        'arena': {k: arena.get(k) for k in ('identify', 'rendered_token', 'define_as', 'display_image')},
                        'ok': bool(slinger_ok)},
            'lumberjack': {'identify': lj.get('identify'), 'rendered_token': lj.get('rendered_token'),
                           'define_as': lj.get('define_as'), 'ok': bool(lumberjack_ok)},
            'wayist': {'ok': bool(wayist_ok), 'count': len(wrows),
                       'rows': [[r.get('identify'), r.get('rendered_token'), r.get('tall_body'),
                                 r.get('summoner_is_player')] for r in wrows]},
            'anomaly': {'ok': bool(anomaly_ok), 'calls': an.get('calls'), 'count': an.get('count'),
                        'rows': [[r.get('anomaly_name'), r.get('identify'), r.get('rendered_token')]
                                 for r in an.get('rows', [])]},
            'archers': {'ok': bool(archer_ok), 'same_png': bool(archer_same_png),
                        'archer': ar.get('archer', {}).get('identify'),
                        'companion': ar.get('companion', {}).get('identify')},
            'auras': auras,
            'negatives': {'cases': [[c['key'], c['name'], c['row'].get('identify'), c['row'].get('rendered_token')] for c in cases],
                          'novice': {'identify': (nv or {}).get('row', {}).get('identify'),
                                     'rendered_token': (nv or {}).get('row', {}).get('rendered_token')}},
            'step_errors': errors, 'lua_errors': lua_errors, 'failures': failures, 'pass': not failures,
            'visual_single_body_review': 'pending: machine identity is not a draw-count proof'}


def verify_ub1(result):
    """Batch UB-1: nine native-tall uniques/bosses, both define sites and aliases,
    the native twin link, Tarelion's shorthand, two toggle cycles and negatives."""
    sc = result.get('scenes', {})
    def step(label, kind, prefix=None):
        return [x for x in sc.get(label, {}).get('steps', [])
                if x['step'][0] == kind and (prefix is None or x['step'][1:2] == [prefix])]
    def exact(r, tid):
        return (r.get('identify') == r.get('rendered_token') == tid and r.get('can_see')
                and r.get('seen') and r.get('explain') == 'exact-identity'
                and str(r.get('display_image')).endswith('/' + tid + '.png'))
    checks, detail = {}, {}
    expected_badge = {3.5: 'unique', 4: 'boss', 5: 'elite_boss', 10: 'god'}
    badges = {}
    # 1. en_US + zh_hans lineups, two off/on cycles at 48/64/96.
    for lab, locale in (('lineup-L1', 'en_US'), ('lineup-zh-L1', 'zh_hans')):
        states = step(lab, 'ub1_group', 'lineup')
        states = states[0].get('states', []) if states else []
        ids = set(UB1_EXPECT.values())
        ok = [(s['enabled'], s['round']) for s in states] == [(True, 0), (False, 1), (True, 1), (False, 2), (True, 2)]
        ok = ok and sc.get(lab, {}).get('launch', {}).get('locale') == locale
        sizes_ok = True
        for s in states:
            frames = s.get('frames', [])
            sizes_ok = sizes_ok and ({f['tile'] for f in frames} == {48, 64, 96} if s['round'] < 2 else {f['tile'] for f in frames} == {64})
            for f in frames:
                rows = f['rows']
                ok = ok and len(rows) == 9 and {r['ub1_id'] for r in rows} == ids
                ok = ok and all(r['can_see'] and r['seen'] for r in rows)
                if s['enabled']:
                    ok = ok and all(exact(r, r['ub1_id']) for r in rows)
                else:
                    ok = ok and all(not r['rendered_token'] and not r['display_image'] for r in rows)
                for r in rows:
                    badges[r['ub1_id']] = {'rank': r.get('rank'), 'badge': r.get('badge')}
        checks[lab] = bool(ok and sizes_ok)
        checks[lab + '-single-body'] = bool(states) and all(
            isinstance(r['replacement_display_h'], (int, float)) and 0 < r['replacement_display_h'] <= 1
            and r['replacement_add_mos_count'] == 0
            for s in states if s['enabled'] for f in s['frames'] for r in f['rows'])
        checks[lab + '-badge'] = bool(states) and all(
            r['badge'] == expected_badge.get(r['rank'], False)
            for s in states for f in s['frames'] for r in f['rows'])
    detail['rank_badges'] = badges
    # 2. Tarelion's {tall=true} shorthand resolved to the verified tall body.
    tm = (step('lineup-L1', 'ub1_meta') or [{}])[0].get('rows', [])
    trow = next((r for r in tm if r['name'] == 'Archmage Tarelion'), {})
    checks['tarelion'] = bool(trow) and trow.get('own_image') == 'invis.png' and any(
        m['image'] == 'npc/humanoid_shalore_archmage_tarelion.png' and m['display_h'] == 2 and m['display_y'] == -1
        for m in (trow.get('own_add_mos') or []))
    # 3. Both native Aeryn define sites and both Caldizar define_as values.
    groups = (step('sites-L1', 'ub1_sites') or [{}])[0].get('groups', [])
    sites_ok = {g['key']: True for g in groups}
    for g in groups:
        for f in g['frames']:
            by_ref = {r['ub1_ref']: r for r in f['rows']}
            for i, (n, src, das, tid) in enumerate(g['cases']):
                r = by_ref.get(i)
                sites_ok[g['key']] = sites_ok.get(g['key'], True) and r is not None and exact(r, tid) \
                    and r.get('define_as') == das
    checks['aeryn-two-sites'] = bool(sites_ok.get('aeryn-sites'))
    checks['caldizar-alias'] = bool(sites_ok.get('caldizar-alias'))
    # 4. High vs Fallen Aeryn and Twin vs Clone side by side (48px included).
    groups = (step('siblings-L1', 'ub1_siblings') or [{}])[0].get('groups', [])
    sib = {g['key']: True for g in groups}
    for g in groups:
        for f in g['frames']:
            by_ref = {r['ub1_ref']: r for r in f['rows']}
            for i, (n, src, das, tid) in enumerate(g['cases']):
                r = by_ref.get(i)
                sib[g['key']] = sib.get(g['key'], True) and r is not None and exact(r, tid)
            sib[g['key']] = sib.get(g['key'], True) and {r['name'] for r in f['rows']} == {c[0] for c in g['cases']}
    checks['aeryn-siblings-48'] = bool(sib.get('aeryn')) and 48 in {f['tile'] for f in next((g for g in groups if g['key'] == 'aeryn'), {}).get('frames', [])}
    checks['chronolith-siblings-48'] = bool(sib.get('chronolith')) and 48 in {f['tile'] for f in next((g for g in groups if g['key'] == 'chronolith'), {}).get('frames', [])}
    # 5. The native twin_take_hit link propagates damage and both keep tokens.
    tw = (step('twin-L1', 'ub1_twin') or [{}])[0]
    link, hit = tw.get('link', {}), tw.get('hit', {})
    checks['twin-link'] = bool(link.get('linked') and link.get('twin_on_take_hit') and link.get('clone_on_take_hit'))
    checks['twin-damage'] = bool(
        hit.get('twin_before', 0) > hit.get('twin_after', 0) and hit.get('clone_before', 0) > hit.get('clone_after', 0)
        and hit.get('brother_after')
        and exact(hit.get('twin', {}), 'chronolith-twin') and exact(hit.get('clone', {}), 'chronolith-clone'))
    # 6. nicer_tiles off/on round trip: fresh placements while off keep the
    #    native fallback where the default-name body differs from the catalog
    #    image, and all nine map again after the flag is restored.
    nn = (step('nicer-off-L1', 'ub1_nicer') or [{}])[0]
    nic = {}
    for f in nn.get('off', []):
        for r in f['rows']:
            img = r.get('image')
            mapped = bool(r['identify'] == r['rendered_token'] == r['ub1_id'])
            nic.setdefault(r['ub1_id'], {'native_image': img, 'catalog_image': UB1_IMAGE.get(r['ub1_id']), 'maps_off': mapped})
    off_ok = all(v['maps_off'] == (v['native_image'] == v['catalog_image']) for v in nic.values())
    on_ok = all(exact(r, r['ub1_id']) for f in nn.get('on', []) for r in f['rows'])
    checks['nicer-off'] = bool(nn) and nn.get('nicer_before') is True and nn.get('nicer_during') is False \
        and nn.get('nicer_restored') is True and off_ok and on_ok \
        and all(len(f['rows']) == 9 for f in nn.get('off', []) + nn.get('on', [])) \
        and {f['tile'] for f in nn.get('off', []) + nn.get('on', [])} == {48, 64, 96}
    detail['nicer_off'] = nic
    # 7. Native appearance negatives.
    neg = (step('negative-L1', 'ub1_negative') or [{}])[0]
    cases = neg.get('cases', [])
    checks['negatives'] = len(cases) == 6 and all(
        not c['row']['identify'] and not c['row']['rendered_token'] and not c['row']['display_image']
        and c['view']['rows'] and c['view']['rows'][0]['can_see'] for c in cases)
    # 8. Per-identity individual placement metadata (lineup-L1).
    each = (step('lineup-L1', 'ub1_each') or [{}])[0].get('items', [])
    checks['each-identity'] = len(each) == 9 and all(
        len(it['frames']) == 3 and all(exact(fr['row'], it['id']) for fr in it['frames']) for it in each)
    errors = [(lab, x.get('step'), x.get('error')) for lab, rec in sc.items() for x in rec.get('steps', []) if 'error' in x]
    lua_errors = {lab: rec.get('lua_errors') for lab, rec in sc.items()}
    missing = [s[0] for s in SCENES_UB1 if s[0] not in sc]
    checks['no-errors'] = not missing and not errors and not any(lua_errors.values())
    return {'checks': checks, 'rank_badges': badges, 'nicer_off': detail.get('nicer_off'),
            'twin': {'link': link, 'hit': {k: v for k, v in hit.items() if k not in ('twin', 'clone')}},
            'step_errors': errors, 'lua_errors': lua_errors, 'missing_scenes': missing,
            'pass': all(checks.values())}


def verify_ub2(result):
    """Batch UB-2: eleven flat unique/boss tokens, natural spawns in their real
    zones, the wiring-only Cursed/Abomination pair, Guren beside the shipped
    human sun-paladin, Epoch's native Multiply clone and appearance negatives."""
    sc = result.get('scenes', {})

    def step(label, kind, prefix=None):
        return [x for x in sc.get(label, {}).get('steps', [])
                if x['step'][0] == kind and (prefix is None or x['step'][1:2] == [prefix])]

    def exact(r, tid):
        return (r.get('identify') == r.get('rendered_token') == tid and r.get('can_see')
                and r.get('seen') and r.get('explain') == 'exact-identity'
                and str(r.get('display_image')).endswith('/' + tid + '.png'))

    checks, detail, badges = {}, {}, {}
    expected_badge = {3.5: 'unique', 4: 'boss', 5: 'elite_boss', 10: 'god'}
    ids = set(UB2_IDS)
    # 1. en_US + zh_hans lineups, two off/on cycles at 48/64/96, badges.
    for lab, locale in (('lineup-L1', 'en_US'), ('lineup-zh-L1', 'zh_hans')):
        states = step(lab, 'ub2_group', 'lineup')
        states = states[0].get('states', []) if states else []
        ok = [(s['enabled'], s['round']) for s in states] == [(True, 0), (False, 1), (True, 1), (False, 2), (True, 2)]
        ok = ok and sc.get(lab, {}).get('launch', {}).get('locale') == locale
        for s in states:
            frames = s.get('frames', [])
            ok = ok and ({f['tile'] for f in frames} == {48, 64, 96} if s['round'] < 2 else {f['tile'] for f in frames} == {64})
            for f in frames:
                rows = f['rows']
                ok = ok and len(rows) == 11 and {r['ub2_id'] for r in rows} == ids
                ok = ok and all(r['can_see'] and r['seen'] for r in rows)
                if s['enabled']:
                    ok = ok and all(exact(r, r['ub2_id']) for r in rows)
                else:
                    ok = ok and all(not r['rendered_token'] and not r['display_image'] for r in rows)
                for r in rows:
                    badges[r['ub2_id']] = {'rank': r.get('rank'), 'badge': r.get('badge')}
        checks[lab] = bool(ok)
        checks[lab + '-badge'] = bool(states) and all(
            r['badge'] == expected_badge.get(r['rank'], False)
            for s in states for f in s['frames'] for r in f['rows'])
        checks[lab + '-single-token'] = bool(states) and all(
            r['replacement_image'] and str(r['replacement_image']).endswith('/' + r['ub2_id'] + '.png')
            for s in states if s['enabled'] for f in s['frames'] for r in f['rows'])
    detail['rank_badges'] = badges
    # 2. Natural spawns in the real zones (or the recorded fallback).
    items = (step('natural-L1', 'ub2_natural') or [{}])[0].get('items', [])
    nat = {}
    nat_ok = len(items) == 11
    for it in items:
        frames = it.get('frames', [])
        good = it.get('resolved') in ('natural', 'placed') and [f['tile'] for f in frames] == [48, 64, 96] \
            and all(exact(f['row'], it['id']) for f in frames) and not it.get('error')
        nat[it['id']] = {'zone': it.get('zone'), 'resolved': it.get('resolved'),
                         'natural_unreachable': it.get('natural_unreachable'), 'error': it.get('error'), 'ok': bool(good)}
        nat_ok = nat_ok and good
    checks['natural-spawns'] = bool(nat_ok)
    detail['natural'] = nat
    # 3. Ben Cruthdar, the Cursed and the Abomination side by side.
    ben = (step('ben-cruthdar-L1', 'ub2_ben') or [{}])[0]
    ben_frames = ben.get('frames', [])
    ben_ids = {'ben-cruthdar-the-cursed', 'ben-cruthdar-abomination'}
    checks['ben-pair'] = len(ben_frames) == 3 and [f['tile'] for f in ben_frames] == [48, 64, 96] and all(
        {r['ub2_ref'] for r in f['rows']} == ben_ids and all(exact(r, r['ub2_ref']) for r in f['rows'])
        for f in ben_frames)
    try:
        import zipfile
        with zipfile.ZipFile(result['runtime_teaa']['path']) as z:
            a = z.read('data/gfx/tokens/ben-cruthdar-abomination.png')
            b = z.read('data/gfx/tokens/ben-cruthdar-the-cursed.png')
        checks['ben-same-png'] = a == b
        detail['ben_png_sha256'] = {'ben-cruthdar-abomination': hashlib.sha256(a).hexdigest(),
                                    'ben-cruthdar-the-cursed': hashlib.sha256(b).hexdigest()}
    except Exception as exc:  # recorded, not hidden
        checks['ben-same-png'] = False
        detail['ben_png_error'] = str(exc)[:200]
    # 4. Guren beside the shipped human sun-paladin at 48px.
    gp = (step('guren-paladin-L1', 'ub2_guren') or [{}])[0]
    gp_frames = gp.get('frames', [])
    gp_ids = {'sun-paladin-guren', 'human-sun-paladin'}
    checks['guren-vs-paladin'] = len(gp_frames) == 3 and [f['tile'] for f in gp_frames] == [48, 64, 96] and all(
        {r['ub2_ref'] for r in f['rows']} == gp_ids and all(exact(r, r['ub2_ref']) for r in f['rows'])
        for f in gp_frames)
    # 5. Epoch's native Multiply clone keeps the original token.
    ep = (step('epoch-multiply-L1', 'ub2_epoch') or [{}])[0]
    use = ep.get('use', {})
    orig_rows = [next((r for r in f.get('rows', []) if r.get('ub2_epoch') == 'original'), {}) for f in ep.get('frames', [])]
    checks['epoch-multiply'] = bool(use.get('ok')) and exact(use.get('original', {}), 'epoch') \
        and bool(use.get('clone')) and ep.get('before', {}).get('row', {}).get('identify') == 'epoch' \
        and len(orig_rows) == 3 and all(exact(r, 'epoch') for r in orig_rows)
    detail['epoch_multiply'] = {'ok': use.get('ok'), 'err': use.get('err'),
                                'original_define_as': use.get('original_define_as'),
                                'clone_define_as': use.get('clone_define_as'),
                                'clone_identify': (use.get('clone') or {}).get('identify'),
                                'original_can_multiply_after': use.get('original_multiply')}
    # 6. Native appearance negatives (anonymous Limmir + wrong/no define_as).
    neg = (step('negative-L1', 'ub2_negative') or [{}])[0]
    cases = neg.get('cases', [])
    by_key = {c['key']: c for c in cases}

    def native_case(c):
        return (not c['row']['identify'] and not c['row']['rendered_token'] and not c['row']['display_image']
                and c['view']['rows'] and c['view']['rows'][0]['can_see'])

    boss_cases = [c for k, c in by_key.items() if k != 'anonymous-limmir']
    checks['anonymous-limmir'] = 'anonymous-limmir' in by_key and native_case(by_key['anonymous-limmir'])
    checks['boss-define-as-negatives'] = len(boss_cases) >= 2 and all(native_case(c) for c in boss_cases)
    checks['negatives'] = checks['anonymous-limmir'] and checks['boss-define-as-negatives']
    errors = [(lab, x.get('step'), x.get('error')) for lab, rec in sc.items() for x in rec.get('steps', []) if 'error' in x]
    lua_errors = {lab: rec.get('lua_errors') for lab, rec in sc.items()}
    missing = [s[0] for s in SCENES_UB2 if s[0] not in sc]
    checks['no-errors'] = not missing and not errors and not any(lua_errors.values())
    return {'checks': checks, 'rank_badges': badges, 'natural': detail.get('natural'),
            'ben_png_sha256': detail.get('ben_png_sha256'), 'ben_png_error': detail.get('ben_png_error'),
            'epoch_multiply': detail.get('epoch_multiply'),
            'step_errors': errors, 'lua_errors': lua_errors, 'missing_scenes': missing,
            'pass': all(checks.values())}


def aura_moment_gate(moment_left, moment_right, count_left, count_right, threshold=2.0):
    """Conditional aura-moment gate: pure decision, no image data.

    R48 made the whole-mask first-moment sign check conditional. The per-pixel
    mean horizontal offset is |moment|/count for each direction. When BOTH
    directions are clearly lopsided (mean >= `threshold` px) the left/right
    moment signs MUST differ; otherwise the silhouette is not lopsided enough
    to judge and the gate records 'N/A' and passes. N is that direction's
    aura-mask pixel count.
    """
    mean_left = moment_left / count_left if count_left else 0.0
    mean_right = moment_right / count_right if count_right else 0.0
    lopsided = abs(mean_left) >= threshold and abs(mean_right) >= threshold
    flipped = bool(moment_left) and bool(moment_right) and ((moment_left > 0) != (moment_right > 0))
    return {
        'label': 'flip' if lopsided else 'N/A',
        'passed': flipped if lopsided else True,
        'mean_left': mean_left,
        'mean_right': mean_right,
        'lopsided': lopsided,
    }


def aura_mirror_applicable(n_asym, noise, n_L, lopsided):
    """Apply the gain-margin gate only at SNR >= 3 or lopsided moments.

    Independent review, user-approved 2026-10-05: a perfect mirror under
    noise reaches about 0.5 * (1 - 1/SNR). Norgos's SNR 2.34 gives 0.286
    against the required 0.283, so the margin cannot decide. Three lies
    between 2.34 and the lowest prior pass, 4.15. Gain thresholds stay intact;
    low-SNR scenes must instead pass every sign and alignment check below.
    """
    if lopsided:
        return True
    if n_asym <= 0 or n_L <= 0:
        return False
    return noise == 0 or n_asym / (noise * n_L) >= 3.0


def aura_mirror_sign_gate(gain, frame_gains, mirrored_iou, plain_iou,
                          native_own, native_upper, aligned):
    """Mandatory sign-only checks when the gain margin is not applicable."""
    return gain > 0 and bool(frame_gains) and all(g > 0 for g in frame_gains) \
        and mirrored_iou > plain_iou and native_own and native_upper and aligned


def _verify_facing_scene(scene, prefix, checks, metrics):
    # Native facing: one creature, the creature mirrored when native. The
    # comparison uses ANIMATED frames (anims are not paused) and the standee
    # region only, so another actor below cannot pollute it. The native left
    # crop horizontally flipped must match the right crop within a tolerance;
    # the unflipped crops must differ more, or the pose would be symmetric and
    # the mirror check meaningless.
    facing = []
    for st in scene.get('steps', []):
        facing = st.get('facing', []) or facing
    facing_aura = {}
    for st in scene.get('steps', []):
        facing_aura = st.get('facing_aura_state', {}) or facing_aura
    fmap = {(r['mode'], r['direction']): r for r in facing}
    checks[f'{prefix}-captures'] = set(fmap) == {('fixed', 'left'), ('fixed', 'right'), ('native', 'left'), ('native', 'right')}
    if checks[f'{prefix}-captures']:
        from PIL import Image, ImageFilter
        import numpy as np

        def _crop_pixels(r, region=None, flip=False):
            # clamp_box returns (x0, y0, x1, y1): the last two entries are the
            # far corner, NOT a width/height pair. R41/R42-fix5 sliced with them
            # as w/h and read a much larger box than intended.
            im = Image.open(OUT / r['crop']).convert('RGB')
            if flip:
                im = im.transpose(Image.FLIP_LEFT_RIGHT)
            a = np.asarray(im).astype(float)
            if region is not None:
                x0, y0 = r['region'][0], r['region'][1]
                rx, ry, rx1, ry1 = region
                a = a[ry - y0:ry1 - y0, rx - x0:rx1 - x0]
            return a

        def _blur(a):
            # A small Gaussian absorbs the sub-pixel offset of the UV mirror
            # (the standee quad centre is not always on an integer pixel), so
            # the comparison tests the mirrored pose, not antialias phase.
            im = Image.fromarray(np.clip(a, 0, 255).astype('uint8'))
            return np.asarray(im.filter(ImageFilter.GaussianBlur(1.5))).astype(float)

        def _frame_pixels(r, flip=False):
            return _crop_pixels(r, r['creature'], flip)

        fl = fmap[('fixed', 'left')]
        fr = fmap[('fixed', 'right')]
        fixed_diff = int((np.abs(_frame_pixels(fl) - _frame_pixels(fr)).sum(axis=2) > 12).sum())
        checks[f'{prefix}-fixed-identical'] = fixed_diff == 0
        metrics[f'{prefix}-fixed-identical-px'] = fixed_diff
        native_left, native_right = fmap[('native', 'left')], fmap[('native', 'right')]

        def _mirror(region, tag):
            # R43: the R42 assertion compared the whole two-cell region, so a
            # mirror of only the feet/disc (own cell) passed even when the upper
            # body was not mirrored. Run it SEPARATELY on the own cell and on
            # the upper body cells; both must mirror. The mask is only the
            # pixels facing actually changed, so static floor/HUD cannot make
            # the flipped frame mismatch.
            for frame in (native_left, native_right):
                assert_centred_mirror_region(frame, frame[tag])
                if frame[tag] != region:
                    raise AssertionError('native left/right mirror regions differ')
            nl = _crop_pixels(native_left, region)
            nr = _crop_pixels(native_right, region)
            boxes = [b for row in (native_left, native_right)
                     for b in row['state']['mirror_occluder_boxes']]
            excluded, report = mirror_exclusion(nl.shape[:2], boxes, region, nl.shape[1]/2)
            metrics[f'{prefix}-native-{tag}-exclusion'] = report
            nl[excluded] = 0
            nr[excluded] = 0
            mask = (np.abs(nl - nr).sum(axis=2) > 12) & ~excluded
            n = int(mask.sum())
            metrics[f'{prefix}-native-%s-changed-px' % tag] = n
            if not n:
                checks[f'{prefix}-native-mirror-%s' % tag] = False
                return
            nlb, nrb = _blur(nl), _blur(nr)
            nlf = _blur(nl[:, ::-1])
            plain_mad = float(np.abs(nlb - nrb).sum(axis=2)[mask].mean())
            mirror_mad = float(np.abs(nlf - nrb).sum(axis=2)[mask].mean())
            metrics[f'{prefix}-native-%s-plain-mad' % tag] = round(plain_mad, 1)
            metrics[f'{prefix}-native-%s-mirror-mad' % tag] = round(mirror_mad, 1)
            ratio = mirror_mad / plain_mad if plain_mad else 0.0
            # How far the observed ratio is from the 0.7 pass threshold: a
            # negative margin would fail. Reported so the claim is honest.
            metrics[f'{prefix}-native-%s-mirror-ratio' % tag] = round(ratio, 3)
            metrics[f'{prefix}-native-%s-mirror-margin' % tag] = round(0.7 - ratio, 3)
            checks[f'{prefix}-native-mirror-%s' % tag] = mirror_mad <= 0.7 * plain_mad

        _mirror(native_left['own'], 'own')
        _mirror(native_left['upper'], 'upper')
        checks[f'{prefix}-native-asymmetric'] = metrics.get(f'{prefix}-native-upper-changed-px', 0) > 0

        # R43/R44 aura under native facing with animations RUNNING (no overlay
        # pause): the only difference between an aura-ON and an aura-OFF frame
        # is the shader aura. R44 compares the aura difference MASKS by
        # IoU: a centroid check cannot tell a mirrored aura from an unmirrored
        # one when the aura hugs the midline. The left mask flipped horizontally
        # must overlap the right mask much better than the unflipped left mask.
        def _mask_full(pa, pb, threshold=12):
            ia = np.asarray(Image.open(OUT / pa).convert('RGB')).astype(int)
            ib = np.asarray(Image.open(OUT / pb).convert('RGB')).astype(int)
            return np.abs(ia - ib).sum(axis=2) > threshold

        def _iou(a, b):
            if a.shape != b.shape:
                return 0.0
            union = int((a | b).sum())
            return (int((a & b).sum()) / union) if union else 0.0

        fa = {}
        for st in scene.get('steps', []):
            for row in st.get('facing_aura', []) or []:
                fa[row['direction']] = row
        if set(fa) == {'left', 'right'}:
            left, right = fa['left'], fa['right']
            on_left = [_mask_full(left['off'], p) for p in left['ons']]
            on_right = [_mask_full(right['off'], p) for p in right['ons']]
            L, R = np.zeros_like(on_left[0]), np.zeros_like(on_right[0])
            for m in on_left:
                L |= m
            for m in on_right:
                R |= m
            # R45/R46: flip about the creature's own body axis (the creature
            # bbox centre x in crop coordinates), NOT the crop midline. R46:
            # pixel x spans [x, x+1], so a mirror about the continuous axis a
            # maps pixel index x to 2a - 1 - x (R45 used 2a - x, a half-pixel
            # shift).
            cc = native_left['state'].get('creature_bbox_centre')
            axis = None if not cc else (cc['x'] - left['region'][0])

            raw_L, raw_R = L.copy(), R.copy()
            boxes = [b for row in (left, right) for b in row['state']['mirror_occluder_boxes']]
            excluded, exclusion_report = mirror_exclusion(L.shape, boxes, left['region'], axis)
            metrics[f'{prefix}-aura-mirror-exclusion'] = exclusion_report
            on_left = [mask & ~excluded for mask in on_left]
            on_right = [mask & ~excluded for mask in on_right]
            L &= ~excluded
            R &= ~excluded
            _flip_axis = mirror_mask_axis

            flip_L = _flip_axis(L, axis)
            asym = L ^ flip_L
            n_asym = int(asym.sum())
            gain = aura_mirror_gain(L, R, axis)
            # R48: the three ON frames per direction give three independent
            # mirror gains (the aggregate above is over their union).
            frame_gains = []
            frame_gains_raw = []
            for i in range(len(on_left)):
                Li, Ri = on_left[i], on_right[i]
                frame_gain = aura_mirror_gain(Li, Ri, axis)
                frame_gains_raw.append(frame_gain)
                frame_gains.append(round(frame_gain, 3))
            metrics[f'{prefix}-aura-frame-gains'] = frame_gains
            # The noise baseline is the SAME-DIRECTION inter-frame IoU: the
            # fraction of a mask that changes between two frames of the SAME
            # direction. A mirrored aura must beat that noise.
            noise_iou = _median(
                [_iou(on_left[i], on_left[j]) for i in range(len(on_left)) for j in range(i + 1, len(on_left))]
                + [_iou(on_right[i], on_right[j]) for i in range(len(on_right)) for j in range(i + 1, len(on_right))])
            noise = 1.0 - noise_iou
            xs = np.arange(L.shape[1])[None, :]
            mom_L = float((L * (xs - (axis or 0))).sum())
            mom_R = float((R * (xs - (axis or 0))).sum())
            moment_flip = bool(mom_L) and bool(mom_R) and ((mom_L > 0) != (mom_R > 0))
            metrics[f'{prefix}-aura-asym-px'] = n_asym
            metrics[f'{prefix}-aura-asym-gain'] = round(gain, 3)
            metrics[f'{prefix}-aura-noise-iou'] = round(noise_iou, 3)
            metrics[f'{prefix}-aura-noise'] = round(noise, 3)
            metrics[f'{prefix}-aura-moment-left'] = round(mom_L, 1)
            metrics[f'{prefix}-aura-moment-right'] = round(mom_R, 1)
            metrics[f'{prefix}-aura-moment-flip'] = moment_flip
            # R48: conditional moment gate. When BOTH directions are clearly
            # lopsided (per-pixel mean offset |moment|/N >= 2 px) the sign MUST
            # flip; otherwise the silhouette is not lopsided enough to judge and
            # the check records N/A (True). N is that direction's aura-mask
            # pixel count. This restores the R46 moment rule without letting an
            # almost-symmetric aura (heavy bone giant, means < 1.3 px) fail.
            n_L, n_R = int(L.sum()), int(R.sum())
            # Reviewer diagnostics only: asym is L XOR mirror(L), so report
            # its fraction of the same LEFT three-frame-union aura mask.
            # Also retain both direction counts and their union explicitly.
            metrics[f'{prefix}-aura-mask-left-px'] = n_L
            metrics[f'{prefix}-aura-mask-right-px'] = n_R
            metrics[f'{prefix}-aura-mask-union-px'] = int((L | R).sum())
            metrics[f'{prefix}-aura-asym-fraction-left'] = n_asym / n_L if n_L else None
            metrics[f'{prefix}-aura-asym-occupied-left-px'] = int((asym & L).sum())
            metrics[f'{prefix}-aura-asym-occupied-left-fraction'] = int((asym & L).sum()) / n_L if n_L else None
            metrics[f'{prefix}-aura-asym-fraction-union'] = n_asym / int((L | R).sum()) if (L | R).any() else None
            gate = aura_moment_gate(mom_L, mom_R, n_L, n_R)
            metrics[f'{prefix}-aura-moment-mean-left'] = round(gate['mean_left'], 3)
            metrics[f'{prefix}-aura-moment-mean-right'] = round(gate['mean_right'], 3)
            metrics[f'{prefix}-aura-moment-lopsided'] = gate['lopsided']
            metrics[f'{prefix}-aura-moment-gate'] = gate['label']
            checks[f'{prefix}-aura-moment'] = gate['passed']
            applicable = aura_mirror_applicable(n_asym, noise, n_L, gate['lopsided'])
            snr = n_asym / (noise * n_L) if noise and n_L else (
                'infinite' if n_asym > 0 and n_L > 0 else 0.0)
            metrics[f'{prefix}-aura-mirror-snr'] = round(snr, 6) if isinstance(snr, float) else snr
            metrics[f'{prefix}-aura-mirror-applicable'] = applicable
            metrics[f'{prefix}-aura-mirror-gate'] = 'applicable' if applicable else 'N/A'
            mirrored_iou, plain_iou = _iou(R, flip_L), _iou(R, L)
            metrics[f'{prefix}-aura-mirror-iou'] = mirrored_iou
            metrics[f'{prefix}-aura-plain-iou'] = plain_iou
            # Margin justified from the data: R44's crop-midline IoU gain was
            # only +0.055 (threshold +0.05), while the asym-restricted gain on
            # ogre-guard is 0.334 against a 0.0 noise baseline. Require a 0.10
            # absolute floor AND > noise + 0.05.
            # Never below the R44-style margin.
            margin_passed = n_asym > 0 and gain >= 0.10 and gain > noise + 0.05
            metrics[f'{prefix}-aura-mirror-margin-passed'] = margin_passed
            checks[f'{prefix}-aura-left-pixels'] = int(on_left[0].sum()) > 0
            checks[f'{prefix}-aura-right-pixels'] = int(on_right[0].sum()) > 0
            # Positional sanity only: the aura pixel centroid relative to the
            # creature bbox centre. With animations running (R46) a single ON
            # frame is noisy, so use the 3-frame union (the same L/R mask the
            # mirror gain uses); the tolerances are unchanged. Horizontal stays
            # tight; direction-to-direction vertical tolerance stays <=2px.
            # R51 approved: absolute vertical centroid offset is diagnostic;
            # placement instead uses the Style quad +/-1px and anchored bottom.
            creature_bbox_centre = None if not cc else (
                cc['x'] - left['region'][0], cc['y'] - left['region'][1])
            offsets = {}
            for direction, mask in (('left', raw_L), ('right', raw_R)):
                aura_centroid = _centroid(mask)
                offsets[direction] = None if (aura_centroid is None or creature_bbox_centre is None) else (
                    aura_centroid[0] - creature_bbox_centre[0], aura_centroid[1] - creature_bbox_centre[1])
            if creature_bbox_centre is not None and offsets['left'] and offsets['right']:
                dlx, dly = offsets['left']
                drx, dry = offsets['right']
                placement = {}
                for direction, mask, row in (('left', raw_L, left), ('right', raw_R, right)):
                    q = row.get('state', {}).get('aura_quad')
                    local_quad = None if not q else [q[0]-row['region'][0], q[1]-row['region'][1],
                                                    q[2]-row['region'][0], q[3]-row['region'][1]]
                    placement[direction] = aura_mask_placement(mask, local_quad)
                metrics[f'{prefix}-aura-placement'] = placement
                metrics[f'{prefix}-aura-offsets-raw'] = {'left': [dlx, dly], 'right': [drx, dry]}
                checks[f'{prefix}-aura-aligned'] = max(abs(dlx), abs(drx)) <= 6 \
                    and abs(dly - dry) <= 2 and all(p['pass'] for p in placement.values())
                metrics[f'{prefix}-aura-offset-left'] = [round(dlx, 1), round(dly, 1)]
                metrics[f'{prefix}-aura-offset-right'] = [round(drx, 1), round(dry, 1)]
                metrics[f'{prefix}-aura-offset-x-max'] = round(max(abs(dlx), abs(drx)), 1)
                metrics[f'{prefix}-aura-offset-y-diff'] = round(abs(dly - dry), 1)
            else:
                checks[f'{prefix}-aura-aligned'] = False
            signs = {
                'aggregate-positive': gain > 0,
                'every-frame-positive': bool(frame_gains_raw) and all(g > 0 for g in frame_gains_raw),
                'mirrored-iou-greater': mirrored_iou > plain_iou,
                'native-mirror-own': checks[f'{prefix}-native-mirror-own'],
                'native-mirror-upper': checks[f'{prefix}-native-mirror-upper'],
                'aura-aligned': checks[f'{prefix}-aura-aligned'],
            }
            metrics[f'{prefix}-aura-mirror-sign-checks'] = signs
            checks[f'{prefix}-aura-mirror'] = margin_passed if applicable else aura_mirror_sign_gate(
                gain, frame_gains_raw, mirrored_iou, plain_iou,
                signs['native-mirror-own'], signs['native-mirror-upper'], signs['aura-aligned'])
        else:
            checks[f'{prefix}-aura-left-pixels'] = False
            checks[f'{prefix}-aura-right-pixels'] = False
            checks[f'{prefix}-aura-mirror'] = False
            checks[f'{prefix}-aura-moment'] = False
            checks[f'{prefix}-aura-aligned'] = False
        checks[f'{prefix}-base-redraw-invis'] = bool(facing_aura) and all(
            v.get('base_invis') for v in facing_aura.values())
        checks[f'{prefix}-body-flip-native'] = bool(native_left['state'].get('body_flip')) \
            and not native_right['state'].get('body_flip')
        checks[f'{prefix}-body-flip-fixed'] = not fl['state'].get('body_flip') \
            and not fmap[('fixed', 'right')]['state'].get('body_flip')

def verify_standee(result):
    """Machine check for the R39/R43 native-tall standee batch. The
    draw-once/occlusion, aura and top-edge judgements are human crop reviews;
    this proves the 24px tile floor, that the four native-tall standees resolve
    to a 256px standee at 32/48/64 and stay flat at 16, that kra-tor (body-only
    cap 1.0) and the native 1-cell bosses stay flat, that the repaints ship, and
    that friend/neutral standees render."""
    def capture_set(rec):
        out = []
        for st in rec.get('steps', []):
            out.extend(st.get('captures', []))
        return out

    def actor_set(rec):
        out = []
        for st in rec.get('steps', []):
            out.extend(st.get('per_actor', []))
        return out

    checks = {}
    metrics = {}
    aura_ratios = {}
    sizes = (16, 32, 48, 64)
    stand_ids = set(R39_ORIGINAL_IDS)
    batch1_ids = set(R39_BATCH1_IDS)
    flat_ids = {'phoenix', 'vor', 'grushnak', 'rungof', 'shardskin', 'subject-z', 'kra-tor'}
    scenes = {k:v for k,v in result.get('scenes', {}).items() if k != 'standee-aura-dim-L1'}
    crowd = scenes.get('standee-crowd-L1', {})
    caps = {c['tile']: c for c in capture_set(crowd)}
    checks['crowd-native-frames'] = all('native' in caps.get(t, {}) for t in sizes)
    checks['crowd-changed-32-48-64'] = all(caps.get(t, {}).get('changed') for t in (32, 48, 64))
    checks['crowd-16-flat'] = caps.get(16, {}).get('changed_pixels') == 0
    for t in (32, 48, 64):
        state = caps.get(t, {}).get('state', [])
        checks['crowd-%d-all-standee' % t] = bool(state) and all(
            s['standee'] and s['layered'] and s['has_box'] and s['canvas'] == 256
            for s in state if s.get('id') in stand_ids) and all(
            not s['standee'] for s in state if s.get('id') in flat_ids)
    state16 = caps.get(16, {}).get('state', [])
    checks['crowd-16-all-flat'] = bool(state16) and all(not s['standee'] for s in state16)
    special = []
    for st in crowd.get('steps', []):
        special.extend(st.get('special', {}).get('rows', []))
    byname = {r['name']: r for r in special}
    checks['crowd-friendly-standee'] = bool(byname.get('Ninandra, the Great Weaver')) and \
        byname['Ninandra, the Great Weaver']['standee'] and byname['Ninandra, the Great Weaver']['reaction'] > 0
    checks['crowd-neutral-flat'] = bool(byname.get("Kra'Tor the Gluttonous")) and \
        not byname["Kra'Tor the Gluttonous"]['standee'] and byname["Kra'Tor the Gluttonous"]['reaction'] == 0
    checks['crowd-flat-boss-token'] = bool(byname.get('Phoenix')) and not byname['Phoenix']['standee']
    # Per-actor 3x4 centred OFF/ON/NATIVE crops at 32 and 64 for the four ids.
    per = actor_set(crowd)
    for t in (32, 64):
        rows = [p for p in per if p.get('found') and p.get('tile') == t]
        checks['per-actor-%d-all-ids' % t] = {p['id'] for p in rows} == stand_ids
        checks['per-actor-%d-crops' % t] = bool(rows) and all(
            (OUT / p['on']).is_file() and (OUT / p['off']).is_file() and (OUT / p['native']).is_file()
            and (p['region'][2] - p['region'][0]) == 3 * t
            and (p['region'][3] - p['region'][1]) == 4 * t
            for p in rows)
        checks['per-actor-%d-size' % t] = bool(rows) and all(
            p.get('height_cap') and p.get('drawn_cells')
            and 0 < p['drawn_cells'] <= p['height_cap'] + 1e-9 for p in rows)
    # Single-standee open scene at 16/32/48/64 with a native frame.
    open_rec = scenes.get('standee-open-L1', {})
    ocaps = {c['tile']: c for c in capture_set(open_rec)}
    checks['open-native-frames'] = all('native' in ocaps.get(t, {}) for t in sizes)
    checks['open-changed-32-48-64'] = all(ocaps.get(t, {}).get('changed') for t in (32, 48, 64))
    checks['open-16-flat'] = ocaps.get(16, {}).get('changed_pixels') == 0
    # Repaint scene: ogre-guard + ninandra beside snow-giant and a black spider.
    rp = scenes.get('standee-repaint-L1', {})
    rcs = capture_set(rp)
    checks['repaint-runs'] = bool(rcs) and not rp.get('failed')
    checks['repaint-32-changed'] = any(c['tile'] == 32 and c['changed'] for c in rcs)
    checks['repaint-32-native-frame'] = any(c['tile'] == 32 and 'native' in c for c in rcs)
    checks['repaint-ids'] = set()
    for st in rp.get('steps', []):
        checks['repaint-ids'] = {r['token'] for r in st.get('special', {}).get('rows', [])}
    checks['repaint-ids'] = checks['repaint-ids'] >= {'ogre-guard', 'ninandra', 'snow-giant', 'giant-spider'}
    # Aura scene: one warm and one dark REAL shader aura measured SEPARATELY by
    # pixel DIFFERENCE above the own-cell top, with animations running.
    ranks = [c for st in scenes.get('standee-rank-L1', {}).get('steps', [])
             for c in st.get('rank_captures', [])]
    checks['rank-all-captures'] = len(ranks) == 12
    for rank in (4, 2):
        for tile in (32, 48, 64):
            by = {c['state']: c for c in ranks if c['rank'] == rank and c['tile'] == tile}
            checks['rank-%d-%d-on-hides-native' % (rank, tile)] = bool(by.get('on')) and by['on']['ornament_pixels'] == 0
            checks['rank-%d-%d-native-ornament' % (rank, tile)] = bool(by.get('native')) and (
                by['native']['ornament_pixels'] > 0 if rank == 4 else by['native']['ornament_pixels'] == 0)

    aura = scenes.get('standee-aura-L1', {})
    acaps = []
    for source in (aura, scenes.get('standee-aura-forge-L1', {})):
        for st in source.get('steps', []):
            acaps.extend(st.get('aura_captures', []))
    # The cold forge-only isolation rerun supersedes its historical six cases;
    # retain the other 54, whose baseline shader counts were already zero.
    acaps = list({(c['actor'], c['effect'], c['tile'], c['state']): c
                  for c in acaps}.values())
    checks['aura-effects-separate'] = {c['effect'] for c in acaps} == {'body_of_fire', 'essence_of_the_dead'}
    checks['aura-tall-new-actor'] = {c.get('actor') for c in acaps} == {a[0] for a in R39_AURA_ACTORS}
    # The label is not enough: every ON capture must have really applied its own
    # aura. `applied` is read back from the actor's live talent/effect state.
    checks['aura-applied-effects'] = bool(acaps) and all(
        c['state'] != 'on' or (c.get('applied') or {}).get('applied') == c['effect']
        for c in acaps)
    checks['aura-off-applied-none'] = bool(acaps) and all(
        not (c.get('off_applied') or {}).get('applied') for c in acaps)
    # R43 creature-still: the overlay creature is static, so after subtracting
    # the aura's own pixels from the consecutive-frame difference only aura
    # fringe pixels (amplitude below the 12 threshold) remain. The cap is a small
    # absolute pixel count justified by the recorded R43 live values (observed
    # max 9 px at 48px, on a ~6900 px body region), not by a fraction of the area.
    CREATURE_STILL_MAX = 16
    creature_still = {}
    aura_pixels = {}
    aura_normalised = {}
    aura_upper_diagnostic = {}
    aura_reach = {}
    aura_flame = {}
    aura_validity = {}
    # R49 user decision: whole-region difference ON/NATIVE / reach_ratio.
    # Upper-cell ratios remain diagnostic; threshold 12 and gate [0.6,1.5]
    # are unchanged. The common region includes headroom and lateral spill.
    for actor in [a[0] for a in R39_AURA_ACTORS]:
        slug = EXPECT.get(actor, actor.replace(' ', '-'))
        reach = standee_reach(slug)
        if reach:
            aura_reach[slug] = {'on_reach': round(reach['on_reach'], 4),
                                'native_reach': round(reach['native_reach'], 4),
                                'on_into': round(reach['on_into'], 4),
                                'native_into': round(reach['native_into'], 4),
                                'feet_depth': round(reach['feet_depth'], 4),
                                'reach_ratio': round(reach['ratio'], 4),
                                'native_top_px': reach['native_top_px'],
                                'native_bottom_px': reach['native_bottom_px']}
        for effect in ('body_of_fire', 'essence_of_the_dead'):
            for t in (32, 48, 64):
                by = {c['state']: c for c in acaps
                      if c.get('actor') == actor and c.get('effect') == effect and c.get('tile') == t}
                on, native = by.get('on'), by.get('native')
                key = '%s-%s-%d' % (slug, effect, t)
                checks['aura-%s-captures' % key] = bool(on and native) \
                    and all(len(r.get('whole_ratio_frames', [])) == 15 for r in (on, native))
                checks['aura-%s-fixed-region' % key] = bool(on and native) and on['whole_region'] == native['whole_region']
                if on and native:
                    valid = all(c.get('baseline_validity', {}).get('valid') for c in (on, native))
                    aura_validity[key] = {'status': aura_case_validity(on, native),
                                          'on': on.get('baseline_validity', {}),
                                          'native': native.get('baseline_validity', {}),
                                          'outside_diagnostic': {'on': on.get('outside_quad_pixels', []),
                                                                 'native': native.get('outside_quad_pixels', [])}}
                    if not valid:
                        # Invalid measurements have no aura pass/fail verdict.
                        # Keep raw counts in census for inspection; do not run
                        # the unchanged detectors on contaminated samples.
                        continue
                    ratio_result = aura_ratio_gate(on['whole_ratio_frames'], native['whole_ratio_frames'], reach['ratio'])
                    on_med = ratio_result['on_median']
                    nat_med = ratio_result['native_median']
                    upper_ratio = _median(on['upper_frames']) / _median(native['upper_frames'])
                    aura_upper_diagnostic[key] = round(upper_ratio / reach['ratio'], 3)
                    ratio = (on_med / nat_med) if nat_med else 0.0
                    aura_ratios[key] = round(ratio, 3)
                    norm = (ratio / reach['ratio']) if (reach and reach['ratio']) else 0.0
                    aura_normalised[key] = round(norm, 3)
                    # 0.6-1.5x the geometry-normalised native: below 0.6 rejects
                    # a disc-shaped own-cell aura, above 1.5 rejects the R41
                    # 128px-every-side pad (which drew ~2x native flames).
                    checks['aura-%s-whole-on-vs-native' % key] = \
                        bool(reach) and on_med > 0 and nat_med > 0 and 0.6 <= norm <= 1.5
                    # Absolute flame-above-top: the highest row of the ON aura
                    # difference mask with >=3 contiguous pixels must sit k cells above the standee
                    # art top, k = max(0.3, 0.6x native flame height above
                    # the native top measured on the same NATIVE crop).
                    # R51 approved: height only uses the pre-registered 15-frame median.
                    if reach:
                        on_art_top = t * (reach['anchor_cells'] - reach['on_reach'])
                        nat_art_top = t * (1 + reach['native_top_px'] / 64.0)
                        height = aura_height_gate(on.get('flame_top_rows') or [],
                                                  native.get('flame_top_rows') or [],
                                                  on_art_top, nat_art_top, t)
                    else:
                        height = {'pass': False, 'on_cells': None, 'native_cells': None, 'k': None}
                    if height['on_cells'] is not None and height['native_cells'] is not None:
                        on_flame, nat_flame, k = height['on_cells'], height['native_cells'], height['k']
                        widths = on.get('flame_band_widths') or []
                        band_frames = sum(w >= AURA_FLAME_BAND_MIN_PX for w in widths)
                        aura_flame[key] = {'on_cells': round(on_flame, 3),
                                           'native_cells': round(nat_flame, 3),
                                           'k': round(k, 3), 'height_frames': AURA_HEIGHT_FRAMES,
                                           'band_min_px': AURA_FLAME_BAND_MIN_PX,
                                           'band_widths': widths, 'band_frames': band_frames,
                                           'height_gate_required': aura_height_gate_required(effect, t)}
                        if aura_height_gate_required(effect, t):
                            checks['aura-%s-flame-above-top' % key] = height['pass']
                        checks['aura-%s-solid-flame-band' % key] = len(widths) == 3 and band_frames >= 2
                    else:
                        if aura_height_gate_required(effect, t):
                            checks['aura-%s-flame-above-top' % key] = False
                        checks['aura-%s-solid-flame-band' % key] = False
                    checks['aura-%s-applied' % key] = \
                        (on.get('applied') or {}).get('applied') == effect \
                        and bool((on.get('applied') or {}).get('active')) \
                        and not (on.get('off_applied') or {}).get('applied')
                    checks['aura-%s-aura-moves' % key] = max(on['self_diff'] or [0]) > 0
                    creature_still[key] = list(on.get('creature_move') or [])
                    aura_pixels[key] = on.get('aura_pixels')
                    checks['aura-%s-creature-still' % key] = \
                        len({tuple(s) for s in on['actor_screen']}) == 1 \
                        and bool(on.get('creature_move')) \
                        and on.get('body_area', 0) > 0 \
                        and max(on['creature_move']) <= CREATURE_STILL_MAX
                    checks['aura-%s-follows-standee' % key] = bool(on.get('snap', {}).get('aura')) and any(
                        a.get('mark') and str(a.get('image', '')).find('tokens-layer/aura/') >= 0 for a in on['snap']['aura'])
                    checks['aura-%s-base-invis' % key] = any(a.get('base') for a in on['snap']['aura'])
                    checks['aura-%s-native-keeps-aura' % key] = bool(native.get('snap', {}).get('aura'))
    entry_after = {}
    for st in aura.get('steps', []):
        entry_after = st.get('aura_after', {}) or entry_after
    checks['aura-still-on-standee'] = bool(entry_after) and entry_after.get('standee')

    # Sequential auras: A, wait a turn, B, then remove A, with no refresh between.
    seq = {}
    for st in scenes.get('standee-sequential-L1', {}).get('steps', []):
        seq = st.get('sequential', {}) or seq
    checks['seq-first-active'] = bool(seq.get('first')) and seq['first'].get('active')
    checks['seq-second-active'] = bool(seq.get('second')) and seq['second'].get('active')
    sstages = {s['stage']: s for s in seq.get('shots', [])}
    # entries counts the display add_mos: one sdm aura + one invis base-redraw
    # per aura kind.
    checks['seq-a-one-aura'] = bool(sstages.get('a')) \
        and sstages['a']['state'].get('kinds') == ['ice_armour'] \
        and sstages['a']['state'].get('entries') == 2
    checks['seq-ab-two-auras'] = bool(sstages.get('ab')) \
        and set(sstages['ab']['state'].get('kinds', [])) == {'ice_armour', 'essence_of_the_dead'} \
        and sstages['ab']['state'].get('entries') == 3
    checks['seq-b-after-remove-one'] = bool(sstages.get('b')) \
        and sstages['b']['state'].get('kinds') == ['essence_of_the_dead'] \
        and sstages['b']['state'].get('entries') == 2

    facing_runs = {}
    informative_checks = {}
    invalid_checks = {}
    for scene_name, prefix in (
        ('standee-facing-L1', 'facing'),
        ('standee-facing-new-tall-L1', 'facing-new-tall'),
        ('standee-facing-ogre-L1', 'facing-ogre'),
        ('standee-facing-heavy-bone-L1', 'facing-heavy-bone'),
        ('standee-facing-daelach-L1', 'facing-daelach'),
        ('standee-facing-bill-L1', 'facing-bill'),
        ('standee-facing-batch4-L1', 'facing-batch4'),
    ):
        scene = scenes.get(scene_name, {})
        run_checks = {}
        _verify_facing_scene(scene, prefix, run_checks, metrics)
        actor = next((st['placed']['id'] for st in scene.get('steps', [])
                      if st.get('placed') and st.get('facing')), None)
        # Missing subjects remain failures; only a measured low-asymmetry
        # subject can be informative. Never discard raw check results.
        asymmetry = static_aura_asymmetry(actor)['static_asymmetry'] if actor else None
        light_records = [r.get('lighting', {}) for st in scene.get('steps', [])
                         for r in st.get('facing', []) + st.get('facing_aura', [])]
        lighting_ok = bool(light_records) and all(r.get('valid') for r in light_records)
        status = (facing_run_status(asymmetry, run_checks) if actor else 'FAIL') if lighting_ok else 'INVALID (lighting)'
        facing_runs[prefix] = {'actor': actor, 'static_asymmetry': asymmetry,
                               'status': status, 'raw_checks': run_checks,
                               'lighting': [{k: value for k, value in record.items() if k != 'states'}
                                            for record in light_records]}
        checks.update(run_checks)
        if status == 'INFORMATIVE':
            informative_checks.update(run_checks)
        elif status == 'INVALID (lighting)':
            invalid_checks.update(run_checks)
    # Top visible row: the actor's own row really is the first visible map row
    # (same_row), and the standee's screen top is above the viewport top.
    top = scenes.get('standee-top-L1', {})
    tgeo = {}
    for st in top.get('steps', []):
        tgeo = st.get('top_geometry', {}) or tgeo
    checks['top-same-row'] = bool(tgeo.get('same_row'))
    checks['top-standee-above-viewport'] = bool(tgeo.get('quad')) \
        and tgeo['quad']['screen_top'] < tgeo['viewport_top']
    tcs = capture_set(top)
    checks['top-48'] = any(c['tile'] == 48 and c['changed'] for c in tcs)
    checks['top-48-native-frame'] = any(c['tile'] == 48 and 'native' in c for c in tcs)
    checks['top-crop-reaches-viewport'] = bool(tgeo) and any(
        c['tile'] == 48 and c['region'][1] <= tgeo.get('viewport_top', -1) for c in tcs)
    # Wide-body path: a wide native-tall id with no standee layer stays flat.
    wide = scenes.get('standee-wide-L1', {})
    wstate = {}
    for st in wide.get('steps', []):
        wstate = st.get('wide_state', {}) or wstate
    checks['wide-flat-token'] = bool(wstate) and wstate.get('rendered_token') == 'corrupted-sand-wyrm' \
        and not wstate.get('standee') and not wstate.get('layered') \
        and (wstate.get('height') or 0) > 1.0
    checks['wide-no-layer'] = bool(wstate) and not wstate.get('has_box')
    checks['wide-native-frame'] = any(c['tile'] == 48 and 'native' in c for c in capture_set(wide))
    # All accepted standee batches retain the same per-actor/crowd floors.
    for batch, batch_ids, layout in (
            ('batch1', set(R39_BATCH1_IDS), STANDEE_BATCH1_CROWD),
            ('batch2', set(R39_BATCH2_IDS), STANDEE_BATCH2_CROWD),
            ('batch3', set(R39_BATCH3_IDS), STANDEE_BATCH3_CROWD),
            ('batch4', set(R39_BATCH4_IDS), STANDEE_BATCH4_CROWD),
            ('briagh', set(R53_BRIAGH_IDS), STANDEE_BRIAGH_CROWD)):
        batch_scene = scenes.get('standee-' + batch + '-L1', {})
        bplaced = []
        for st in batch_scene.get('steps', []):
            bplaced.extend(st.get('placed', []))
        checks[batch + '-all-placed'] = {p['id'] for p in bplaced} == batch_ids
        checks[batch + '-rows'] = bool(bplaced) and all(p.get('row', {}).get('identify') == p['id'] for p in bplaced)
        bper = actor_set(batch_scene)
        planned = {(tid, t) for tid in batch_ids for t in (32, 48, 64)}
        for t in (32, 48, 64):
            rows = [p for p in bper if p.get('found') and p.get('tile') == t]
            checks[batch + '-per-actor-%d-ids' % t] = {p['id'] for p in rows} == batch_ids
            checks[batch + '-per-actor-%d-crops' % t] = bool(rows) and all(
                (OUT / p['on']).is_file() and (OUT / p['off']).is_file() and (OUT / p['native']).is_file()
                and (p['region'][2] - p['region'][0]) == 3 * t
                and (p['region'][3] - p['region'][1]) == 4 * t
                for p in rows)
            checks[batch + '-per-actor-%d-size' % t] = bool(rows) and all(
                p.get('height_cap') and p.get('drawn_cells')
                and 1.0 < p['height_cap'] <= 1.75
                and 0 < p['drawn_cells'] <= p['height_cap'] + 1e-9 for p in rows)
        checks[batch + '-per-actor-count'] = len({(p['id'], p['tile']) for p in bper if p.get('found')}) == len(planned)
        bcrowd = capture_set(batch_scene)
        checks[batch + '-crowd-48-changed'] = any(c['tile'] == 48 and c['changed'] for c in bcrowd)
        checks[batch + '-crowd-48-native'] = any(c['tile'] == 48 and 'native' in c for c in bcrowd)
        bcrowdst = []
        for st in batch_scene.get('steps', []):
            for c in st.get('captures', []):
                bcrowdst.extend(c.get('state', []))
        bcrowd_ids = {R39_STANDS[i][3] for _, _, _, i in layout}
        checks[batch + '-crowd-all-standee'] = bool(bcrowdst) and all(
            s['standee'] and s['layered'] and s['has_box'] and s['canvas'] == 256
            for s in bcrowdst if s.get('id') in bcrowd_ids)
        checks[batch + '-crowd-ids'] = {c['id'] for c in bcrowdst} == bcrowd_ids
    # Flat scene at 16px: every standee id must stay flat (below the 24px gate).
    flat = scenes.get('standee-flat-L1', {})
    fcs = capture_set(flat)
    checks['flat-16-runs'] = bool(fcs) and not flat.get('failed')
    checks['flat-16-crop'] = any(c['tile'] == 16 and (OUT / c['crop']).is_file() for c in fcs)
    fstate = fcs[0].get('state', []) if fcs else []
    checks['flat-16-all-flat'] = bool(fstate) and all(not s['standee'] for s in fstate)
    zh = scenes.get('standee-crowd-zh-L1', {})
    zhcs = {c['tile']: c for c in capture_set(zh)}
    checks['crowd-zh-32-changed'] = bool(zhcs.get(32, {}).get('changed'))
    checks['crowd-zh-32-native-frame'] = 'native' in zhcs.get(32, {})
    errors = [(lab, x.get('step'), x.get('error')) for lab, rec in scenes.items()
              for x in rec.get('steps', []) if 'error' in x]
    lua_errors = {lab: rec.get('lua_errors') for lab, rec in scenes.items()}
    missing = [s[0] for s in SCENES_STANDEE if s[0] not in scenes]
    checks['no-errors'] = not missing and not errors and not any(lua_errors.values())
    counted_checks = {k: v for k, v in checks.items()
                      if k not in informative_checks and k not in invalid_checks}
    return {'facing_runs': facing_runs, 'informative_checks': informative_checks,
            'invalid_checks': invalid_checks,
            'counted_checks': counted_checks,
            'check_totals': {'counted': len(counted_checks), 'passed': sum(counted_checks.values()),
                             'failed': sum(not v for v in counted_checks.values()),
                             'informative': len(informative_checks), 'invalid': len(invalid_checks), 'raw': len(checks),
                             'raw_passed': sum(checks.values())},
            'aura_validity': aura_validity,
            'scene_validity': 'INVALID' if any(x['status'] != 'VALID' for x in aura_validity.values()) or any(x['status'] == 'INVALID (lighting)' for x in facing_runs.values()) else 'VALID',
            'checks': checks, 'metrics': metrics, 'step_errors': errors, 'lua_errors': lua_errors,
            'aura_ratios': aura_ratios, 'aura_normalised': aura_normalised,
            'aura_upper_diagnostic': aura_upper_diagnostic,
            'aura_reach': aura_reach, 'aura_flame': aura_flame,
            'creature_still': creature_still, 'aura_pixels': aura_pixels,
            'missing_scenes': missing, 'pass': all(counted_checks.values()) and
            all(v['status'] == 'VALID' for v in aura_validity.values()) and
            all(v['status'] != 'INVALID (lighting)' for v in facing_runs.values())}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--only', nargs='*')
    parser.add_argument('--batch', choices=('ab', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'aa', 'ab', 'ac', 'ad', 'ae', 'af', 'ag', 'ua', 'ta1', 'ta2', 'ub1', 'ub2', 'layer', 'standee', 'legacy', 'summons', 'summons-zh'), default='legacy')
    args = parser.parse_args()
    global OUT, SHOTS, CROPS, CLEAN
    scenes = SCENES
    if args.batch == 'c':
        OUT, scenes = OUT_C, SCENES_C
        SHOTS, CROPS = OUT / 'screenshots', OUT / 'crops'
    elif args.batch == 'd':
        OUT, scenes = OUT_D, SCENES_D
        SHOTS, CROPS = OUT / 'screenshots', OUT / 'crops'
    elif args.batch == 'e':
        OUT, scenes = OUT_E, SCENES_E
        SHOTS, CROPS = OUT / 'screenshots', OUT / 'crops'
    elif args.batch == 'f':
        OUT, scenes = OUT_F, SCENES_F
        SHOTS, CROPS = OUT / 'screenshots', OUT / 'crops'
    elif args.batch == 'g':
        OUT, scenes = OUT_G, SCENES_G
        SHOTS, CROPS = OUT / 'screenshots', OUT / 'crops'
    elif args.batch == 'h':
        OUT, scenes = OUT_H, SCENES_H
        SHOTS, CROPS = OUT / 'screenshots', OUT / 'crops'
    if args.batch == 'i':
        OUT, scenes = OUT_I, SCENES_I
        SHOTS, CROPS = OUT / 'screenshots', OUT / 'crops'
    if args.batch == 'j':
        OUT, scenes = OUT_J, SCENES_J
        SHOTS, CROPS = OUT / 'screenshots', OUT / 'crops'
    if args.batch == 'k':
        OUT, scenes = OUT_K, SCENES_K
        SHOTS, CROPS = OUT / 'screenshots', OUT / 'crops'
    if args.batch == 'l':
        OUT, scenes = OUT_L, SCENES_L
        SHOTS, CROPS = OUT / 'screenshots', OUT / 'crops'
    if args.batch == 'm':
        OUT, scenes = OUT_M, SCENES_M
        SHOTS, CROPS = OUT / 'screenshots', OUT / 'crops'
    if args.batch == 'n':
        OUT, scenes = OUT_N, SCENES_N
        SHOTS, CROPS = OUT / 'screenshots', OUT / 'crops'
    if args.batch == 'o':
        OUT, scenes = OUT_O, SCENES_O
        SHOTS, CROPS = OUT / 'screenshots', OUT / 'crops'
    if args.batch == 'p':
        OUT, scenes = OUT_P, SCENES_P
        SHOTS, CROPS = OUT / 'screenshots', OUT / 'crops'
    if args.batch == 'q':
        OUT, scenes = OUT_Q, SCENES_Q
        SHOTS, CROPS = OUT / 'screenshots', OUT / 'crops'
    if args.batch == 'r':
        OUT, scenes = OUT_R, SCENES_R
        SHOTS, CROPS = OUT / 'screenshots', OUT / 'crops'
    if args.batch == 's':
        OUT, scenes = OUT_S, SCENES_S
        SHOTS, CROPS = OUT / 'screenshots', OUT / 'crops'
    if args.batch == 't':
        OUT, scenes = OUT_T, SCENES_T
        SHOTS, CROPS = OUT / 'screenshots', OUT / 'crops'
    if args.batch == 'u':
        OUT, scenes = OUT_BU, SCENES_BU
        SHOTS, CROPS = OUT / 'screenshots', OUT / 'crops'
    if args.batch == 'v':
        OUT, scenes = OUT_BV, SCENES_BV
        SHOTS, CROPS = OUT / 'screenshots', OUT / 'crops'
    if args.batch == 'w':
        OUT, scenes = OUT_BW, SCENES_BW
        SHOTS, CROPS = OUT / 'screenshots', OUT / 'crops'
    if args.batch == 'x':
        OUT, scenes = OUT_BX, SCENES_BX
        SHOTS, CROPS = OUT / 'screenshots', OUT / 'crops'
    if args.batch == 'y':
        OUT, scenes = OUT_BY, SCENES_BY
        SHOTS, CROPS = OUT / 'screenshots', OUT / 'crops'
    if args.batch == 'z':
        OUT, scenes = OUT_BZ, SCENES_BZ
        SHOTS, CROPS = OUT / 'screenshots', OUT / 'crops'
    if args.batch == 'aa':
        CLEAN = True
        OUT, scenes = OUT_BA, SCENES_BA
        SHOTS, CROPS = OUT / 'screenshots', OUT / 'crops'
    if args.batch == 'ab':
        CLEAN = True
        OUT, scenes = OUT_BB, SCENES_BB
        SHOTS, CROPS = OUT / 'screenshots', OUT / 'crops'
    if args.batch == 'ac':
        CLEAN = True
        OUT, scenes = OUT_BC, SCENES_BC
        SHOTS, CROPS = OUT / 'screenshots', OUT / 'crops'
    if args.batch == 'ad':
        CLEAN = True
        OUT, scenes = OUT_BD, SCENES_BD
        SHOTS, CROPS = OUT / 'screenshots', OUT / 'crops'
    if args.batch == 'ae':
        CLEAN = True
        OUT, scenes = OUT_BE, SCENES_BE
        SHOTS, CROPS = OUT / 'screenshots', OUT / 'crops'
    if args.batch == 'af':
        if not os.environ.get('MLV_TEAA'):
            parser.error('--batch af requires MLV_TEAA: never test loose product code')
        CLEAN = True
        OUT, scenes = OUT_BF, SCENES_BF
        SHOTS, CROPS = OUT / 'screenshots', OUT / 'crops'
    if args.batch == 'ua':
        if not os.environ.get('MLV_TEAA'):
            parser.error('--batch ua requires MLV_TEAA: never test loose product code')
        CLEAN = True
        OUT, scenes = OUT_UA, SCENES_UA
        SHOTS, CROPS = OUT / 'screenshots', OUT / 'crops'
    if args.batch == 'ag':
        if not os.environ.get('MLV_TEAA'):
            parser.error('--batch ag requires MLV_TEAA: never test loose product code')
        CLEAN = True
        OUT, scenes = OUT_BG, SCENES_BG
        SHOTS, CROPS = OUT / 'screenshots', OUT / 'crops'
    if args.batch == 'ta1':
        if not os.environ.get('MLV_TEAA'):
            parser.error('--batch ta1 requires MLV_TEAA: never test loose product code')
        CLEAN = True
        OUT, scenes = OUT_BTA, SCENES_TA1
        SHOTS, CROPS = OUT / 'screenshots', OUT / 'crops'
    if args.batch == 'ub1':
        if not os.environ.get('MLV_TEAA'):
            parser.error('--batch ub1 requires MLV_TEAA: never test loose product code')
        CLEAN = True
        OUT, scenes = OUT_BUB, SCENES_UB1
        SHOTS, CROPS = OUT / 'screenshots', OUT / 'crops'
    if args.batch == 'ub2':
        if not os.environ.get('MLV_TEAA'):
            parser.error('--batch ub2 requires MLV_TEAA: never test loose product code')
        CLEAN = True
        OUT, scenes = OUT_BUB2, SCENES_UB2
        SHOTS, CROPS = OUT / 'screenshots', OUT / 'crops'
    if args.batch == 'ta2':
        if not os.environ.get('MLV_TEAA'):
            parser.error('--batch ta2 requires MLV_TEAA: never test loose product code')
        CLEAN = True
        OUT, scenes = OUT_BTA2, SCENES_TA2
        SHOTS, CROPS = OUT / 'screenshots', OUT / 'crops'
    if args.batch == 'layer':
        if not os.environ.get('MLV_TEAA'):
            parser.error('--batch layer requires MLV_TEAA: never test loose product code')
        CLEAN = True
        OUT, scenes = OUT_LAYER, SCENES_LAYER
        SHOTS, CROPS = OUT / 'screenshots', OUT / 'crops'
    if args.batch == 'standee':
        if not os.environ.get('MLV_TEAA'):
            parser.error('--batch standee requires MLV_TEAA: never test loose product code')
        CLEAN = True
        OUT, scenes = OUT_STANDEE, SCENES_STANDEE
        if args.only and 'standee-aura-dim-L1' in args.only:
            assert args.only == ['standee-aura-dim-L1'], 'Run the INFORMATIVE scene separately'
            OUT = OUT_STANDEE / 'informative-dim'
            scenes = [("standee-aura-dim-L1", "mark-spellblaze", 1, {}, [("midstart",), ("standee_grid", "aura-dim")])]
        SHOTS, CROPS = OUT / 'screenshots', OUT / 'crops'
    if args.batch == 'summons-zh':
        OUT, scenes = OUT_U, SCENES_ZH
        SHOTS, CROPS = OUT / 'screenshots', OUT / 'crops'
    if args.batch == 'summons':
        OUT, scenes = OUT_U, SCENES_U
        SHOTS, CROPS = OUT / 'screenshots', OUT / 'crops'
    OUT.mkdir(parents=True, exist_ok=True)
    census_path = OUT / 'census.json'
    result = json.loads(census_path.read_text()) if census_path.exists() else {'scenes': {}}
    result['expected'] = EXPECT
    if args.batch == 'ua':
        result['expected_ua'] = [{'name': n, 'source': src, 'define_as': das, 'id': tid}
                                 for n, src, das, tid in UA_CASES]
    if args.batch == 'ag':
        result['expected_ag'] = [{'name': n, 'source': src, 'define_as': das, 'id': tid}
                                 for n, src, das, tid in AG_CASES]
    if args.batch == 'ub2':
        result['expected_ub2'] = [{'name': n, 'source': src, 'define_as': das, 'id': tid}
                                  for n, src, das, tid in UB2_CASES + [UB2_ABOM, UB2_PALADIN]]
    if args.batch == 'ta2':
        result['expected_ta2'] = [{'name': n, 'source': PLACE_SRC_TA2[n], 'define_as': None, 'id': EXPECT[n]}
                                  for n in TA2]
    if os.environ.get('MLV_TEAA'):
        result['runtime_teaa'] = {'path': os.environ['MLV_TEAA'], 'sha256': digest(os.environ['MLV_TEAA'])}
    result['scene_sha256'] = {'tests/live_monster_batch.lua': digest(ADDON / 'tests/live_monster_batch.lua'),
                              'tests/live_map_survey.lua': digest(ADDON / 'tests/live_map_survey.lua'),
                              'overload/mod/class/CheckerTokens.lua': digest(ADDON / 'overload/mod/class/CheckerTokens.lua')}
    if args.batch in ('af', 'ag', 'ua', 'ta1', 'ub1', 'ub2', 'ta2', 'layer', 'standee'):
        import zipfile
        with zipfile.ZipFile(os.environ['MLV_TEAA']) as package:
            result['tested_runtime_sha256'] = {
                path: hashlib.sha256(package.read(path)).hexdigest()
                for path in ('overload/mod/class/CheckerTokens.lua', 'superload/mod/class/Actor.lua')}
        # The working-tree product file may be under concurrent edits; it is not tested.
        result['scene_sha256'].pop('overload/mod/class/CheckerTokens.lua', None)
    for scene in scenes:
        label = scene[0]
        if args.only and label not in args.only:
            continue
        wait_fixture_free()
        launch = subprocess.run([sys.executable, str(ADDON / 'tools/launch_fixture.py'), '--shaders', '--tiles', '64',
                                 '--terrain', 'refined', '--resolution', '1920x1080']
                                + (['--locale', os.environ['MLV_LOCALE']] if os.environ.get('MLV_LOCALE') else [])
                + (['--teaa', 'checker-revised=' + os.environ['MLV_TEAA']] if os.environ.get('MLV_TEAA') else []),
                                cwd=ADDON / 'tools', capture_output=True, text=True)
        if launch.returncode:
            raise RuntimeError(f'{label} launch failed: {launch.stdout} {launch.stderr}')
        meta = json.loads((SESSION / 'processes.json').read_text())
        plan = json.loads((SESSION / 'launch-plan.json').read_text())
        print('START', label, meta['game'], meta['xvfb'], meta['display'], flush=True)
        bridge = Bridge()
        log_start = 0  # launch_fixture truncates game.log for each new process
        try:
            wait_ready(bridge, log_start)
            record = run_scene(scene, bridge)
            record['launch'] = {k: plan[k] for k in ('shaders', 'tiles', 'resolution', 'terrain', 'addons', 'fixture', 'tokens')}
            if args.batch in ('af', 'ag', 'ua', 'ta1', 'ub1', 'ub2', 'ta2', 'layer', 'standee'):
                record['launch']['locale'] = plan['locale']
                record['launch']['teaa'] = plan['teaa']
            record['processes'] = {'game': meta['game'], 'xvfb': meta['xvfb'], 'display': meta['display']}
            text = LOG.read_bytes()[log_start:].decode('utf-8', 'replace')
            record['lua_errors'] = text.count('Lua Error')
            # R48: the engine prints the SDM readback (source texture px :: sdm
            # texture px) in src/core_lua.c gl_texture_alter_sdm. Record it so
            # the aura texture size is a runtime fact, not a file guess.
            record['sdm_texture_lines'] = sorted(set(re.findall(r'==SDM \d+x\d+ :: \d+x\d+', text)))
            result['scenes'][label] = record
            census_path.write_text(json.dumps(result, ensure_ascii=False, indent=1) + '\n')
            print('DONE', label, flush=True)
        finally:
            for f in ('board-test-command.txt', 'checker-command.txt'):
                (HOME / f).unlink(missing_ok=True)
            stop_started(meta)
            alive = [k for k in ('game', 'xvfb') if (Path('/proc') / str(meta[k]) / 'cmdline').exists()]
            sock = Path('/tmp/.X11-unix') / ('X' + meta['display'][1:])
            print('STOP', label, meta['game'], meta['xvfb'], 'alive=', alive, 'socket=', sock.exists(), flush=True)
    if args.batch == 'ua':
        result['batch_ua_verdict'] = verify_ua(result)
        census_path.write_text(json.dumps(result, ensure_ascii=False, indent=1) + '\n')
    if args.batch == 'ag':
        result['batch_ag_verdict'] = verify_ag(result)
        census_path.write_text(json.dumps(result, ensure_ascii=False, indent=1) + '\n')
    if args.batch == 'ta1':
        result['batch_ta1_verdict'] = verify_ta1(result)
        census_path.write_text(json.dumps(result, ensure_ascii=False, indent=1) + '\n')
        print('VERDICT', json.dumps(result['batch_ta1_verdict'], ensure_ascii=False), flush=True)
    if args.batch == 'ta2':
        result['batch_ta2_verdict'] = verify_ta2(result)
        census_path.write_text(json.dumps(result, ensure_ascii=False, indent=1) + '\n')
        print('VERDICT', json.dumps(result['batch_ta2_verdict'], ensure_ascii=False), flush=True)
    if args.batch == 'ub1':
        result['batch_ub1_verdict'] = verify_ub1(result)
        census_path.write_text(json.dumps(result, ensure_ascii=False, indent=1) + '\n')
        print('VERDICT', json.dumps(result['batch_ub1_verdict'], ensure_ascii=False), flush=True)
    if args.batch == 'ub2':
        result['batch_ub2_verdict'] = verify_ub2(result)
        census_path.write_text(json.dumps(result, ensure_ascii=False, indent=1) + '\n')
        print('VERDICT', json.dumps(result['batch_ub2_verdict'], ensure_ascii=False), flush=True)
    if args.batch == 'af':
        result['batch_af_verdict'] = verify_af(result)
        census_path.write_text(json.dumps(result, ensure_ascii=False, indent=1) + '\n')
    if args.batch == 'ae':
        result['batch_ae_verdict'] = verify_ae(result)
        census_path.write_text(json.dumps(result, ensure_ascii=False, indent=1) + '\n')
        print('VERDICT', json.dumps(result['batch_ae_verdict'], ensure_ascii=False), flush=True)
    if args.batch == 'ad':
        result['batch_ad_verdict'] = verify_ad(result)
        census_path.write_text(json.dumps(result, ensure_ascii=False, indent=1) + '\n')
        print('VERDICT', json.dumps(result['batch_ad_verdict'], ensure_ascii=False), flush=True)
    if args.batch == 'ac':
        result['batch_ac_verdict'] = verify_ac(result)
        census_path.write_text(json.dumps(result, ensure_ascii=False, indent=1) + '\n')
        print('VERDICT', json.dumps(result['batch_ac_verdict'], ensure_ascii=False), flush=True)
    if args.batch == 'ab':
        result['batch_ab_verdict'] = verify_ab(result)
        census_path.write_text(json.dumps(result, ensure_ascii=False, indent=1) + '\n')
        print('VERDICT', json.dumps(result['batch_ab_verdict'], ensure_ascii=False), flush=True)
    if args.batch == 'aa':
        result['batch_aa_verdict'] = verify_aa(result)
        census_path.write_text(json.dumps(result, ensure_ascii=False, indent=1) + '\n')
        print('VERDICT', json.dumps(result['batch_aa_verdict'], ensure_ascii=False), flush=True)
    if args.batch == 'standee' and OUT == OUT_STANDEE / 'informative-dim':
        result['informative_only'] = True
        result['lighting_reference'] = AURA_CONTRACT['DIM_LIGHTING_REFERENCE']
        census_path.write_text(json.dumps(result, ensure_ascii=False, indent=1) + '\n')
    elif args.batch == 'standee':
        result['batch_standee_verdict'] = verify_standee(result)
        census_path.write_text(json.dumps(result, ensure_ascii=False, indent=1) + '\n')
        print('VERDICT', json.dumps({k: result['batch_standee_verdict'][k]
                                     for k in ('pass', 'check_totals', 'scene_validity',
                                               'missing_scenes', 'step_errors', 'lua_errors')},
                                    ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
