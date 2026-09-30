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
import os
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

    def shot(self, name):
        if CLEAN:
            self.lua("ms.caveClearDialogs();return true")
        src = HOME / (name + '.png')
        src.unlink(missing_ok=True)
        time.sleep(.5)
        run = subprocess.run([sys.executable, str(ADDON / 'tools/fixture_command.py'), 'shot', name],
                             capture_output=True, text=True, timeout=40)
        assert run.returncode == 0, run.stdout + run.stderr
        for _ in range(300):
            if src.exists() and src.stat().st_size:
                break
            time.sleep(.1)
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


def run_scene(scene, bridge):
    label, zone, level, opts, steps = scene
    record = {'label': label, 'zone': zone, 'level': level, 'opts': opts, 'steps': []}
    bridge.lua("assert(config.settings.cheat and config.settings.disable_all_connectivity and not profile.auth);"
               "assert(core.shader.active(4));ms.setup()")
    names = '{' + ','.join(f'[{json.dumps(n, ensure_ascii=False)}]=true' for n in A + B + C + D + E + F + G + H + NATIVE + NATIVE_D + NATIVE_F + NATIVE_H + I + NATIVE_I + OOZES_SHIPPED + J + NATIVE_J + K + NATIVE_K + ['Grand Corruptor'] + L + NATIVE_L + M + NATIVE_M + N + NATIVE_N + O + NATIVE_O + P + NATIVE_P + Q + NATIVE_Q + R + NATIVE_R + S + NATIVE_S + T + NATIVE_T + BU + NATIVE_BU + BV + NATIVE_BV + BW + NATIVE_BW + BX + NATIVE_BX + BY + NATIVE_BY + BZ + NATIVE_BZ + BA + NATIVE_BA + BB + BC + NATIVE_BC + ['dread', 'swarming horror', 'minotaur', 'ritch flamespitter', 'giant spider'] + ['assassin', 'bandit', 'thief', 'rogue', 'fire drake'] + U + ['ghoul', 'gigantic sandworm tunneler']) + '}'
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
        if kind in ('toggle', 'aura', 'sustain', 'fade', 'wound', 'hide', 'stealth', 'urhrok', 'forcesus', 'thoughtform', 'friendly', 'neutral'):
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
            elif kind == 'randboss':
                # Real GameState random_boss filter path (as the renegade-wyrmics vault): a non-unique native-tall wyrm stays native.
                nm = json.dumps(step[1], ensure_ascii=False)
                entry['cleared'] = bridge.lua("return {n=mb.clearAround(6)}")  # the small start room is otherwise full
                entry['row'] = bridge.lua(
                    "local Map=require 'engine.Map';local p=game.player;"
                    f"local m=game.zone:makeEntity(game.level,'actor',{{name={nm},random_boss={{name_scheme='#rng# the Flame Terror',nb_classes=1,rank=4,loot_quality='store',loot_quantity=1,ai_move='move_complex'}}}},nil,true);"
                    "assert(m and m.randboss,'no random boss');local mm=game.level.map;local x,y,bs;for cx=p.x-8,p.x+8 do for cy=p.y-6,p.y+6 do if cx>=1 and cy>=1 and cx<mm.w-1 and cy<mm.h-1 and (cx~=p.x or cy~=p.y) and not mm(cx,cy,Map.ACTOR) and not mm:checkEntity(cx,cy,Map.TERRAIN,'block_move',p) and mm.seens(cx,cy) then local d=(cx-p.x-3)^2+(cy-p.y-1)^2;if not bs or d<bs then x,y,bs=cx,cy,d end end end end;assert(x,'no free grid');"
                    "m._checker_live_placed=true;m.never_act=true;game.zone:addEntity(game.level,m,'actor',x,y);"
                    "pcall(function() p:resetCanSeeCache() end);mb.refresh();mb.focus(x,y);local r=mb.row(m);"
                    "r.randboss=m.randboss or false;r.unique=m.unique or false;r.define_as_field=m.define_as or false;r.rank=m.rank;return r")
                row = entry['row']
                entry['native_ok'] = not row['rendered_token'] and not row['identify'] and not row['display_image']
                ps = bridge.shot(f'randboss-fire-wyrm-{label}')
                entry['shots'] = [{'file': rel(ps), 'sha256': digest(ps), 'crop': rel(crop(ps, row['screen'], f'randboss-fire-wyrm-{label}-crop', 3))}]
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
                q = json.dumps(actor, ensure_ascii=False)
                entry['off'] = bridge.lua(f"mb.tokens(false);local a=mb.byName({q});mb.focus(a.x,a.y);"
                                          "local rows={};for _,r in ipairs(mb.find()) do if r.rendered_token then rows[#rows+1]=r end end;"
                                          "return {enabled=game:checkerTokensEnabled(),row=mb.row(a),still_mapped=#rows}")
                p1 = bridge.shot(f'toggle2-native-{label}')
                entry['on'] = bridge.lua(f"mb.tokens(true);local a=mb.byName({q});mb.focus(a.x,a.y);"
                                         "return {enabled=game:checkerTokensEnabled(),row=mb.row(a)}")
                time.sleep(3)
                entry['on_later'] = bridge.lua(f"local a=mb.byName({q});mb.focus(a.x,a.y);return mb.row(a)")
                p2 = bridge.shot(f'toggle2-refined-{label}')
                row = entry['on_later']
                entry['shots'] = [{'file': rel(p1), 'sha256': digest(p1), 'crop': rel(crop(p1, row['screen'], f'toggle2-native-{label}-crop', 3))},
                                  {'file': rel(p2), 'sha256': digest(p2), 'crop': rel(crop(p2, row['screen'], f'toggle2-refined-{label}-crop', 3))}]
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--only', nargs='*')
    parser.add_argument('--batch', choices=('ab', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'aa', 'ab', 'ac', 'legacy', 'summons', 'summons-zh'), default='legacy')
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
    if os.environ.get('MLV_TEAA'):
        result['runtime_teaa'] = {'path': os.environ['MLV_TEAA'], 'sha256': digest(os.environ['MLV_TEAA'])}
    result['scene_sha256'] = {'tests/live_monster_batch.lua': digest(ADDON / 'tests/live_monster_batch.lua'),
                              'tests/live_map_survey.lua': digest(ADDON / 'tests/live_map_survey.lua'),
                              'overload/mod/class/CheckerTokens.lua': digest(ADDON / 'overload/mod/class/CheckerTokens.lua')}
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
            record['processes'] = {'game': meta['game'], 'xvfb': meta['xvfb'], 'display': meta['display']}
            text = LOG.read_bytes()[log_start:].decode('utf-8', 'replace')
            record['lua_errors'] = text.count('Lua Error')
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


if __name__ == '__main__':
    main()
