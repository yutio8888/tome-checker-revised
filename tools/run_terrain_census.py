#!/usr/bin/env python3
"""Measurement-only native-terrain census (Refined mode) in the isolated fixture.

Uses tests/live_terrain_census.lua (installed by launch_fixture as
monster-live_terrain_census.lua). Repeated ms.enter calls regenerate the level
with a fresh random seed, so "seeds" are repeated enters inside one process;
the fixture is cold-started once per --chunk enters. Results append to
evidence/terrain-census-20260929/raw.jsonl (resumable). Every process this tool
starts is stopped; nothing else is touched.
"""
import argparse, json, sys, time
from pathlib import Path
from run_batch5_validation import ROOT, launch, read, lua_opts
from run_norgos_validation import stop_started
from capture_korpul import Fixture, LOG

OUT = ROOT / 'evidence/terrain-census-20260929'
RAW = OUT / 'raw.jsonl'

# (zone, opts-list, max_level)
ITEM1 = [
    ('trollmire', [{'flooded': False}, {'flooded': True}], 3),
    ('old-forest', [{'crystaline': False}, {'crystaline': True}], 4),
    ('slazish-fen', [{}], 3),
    ('ruins-kor-pul', [{'hideout': False}, {'hideout': True}], 3),
    ('rhaloren-camp', [{'overground': False}, {'overground': True}], 3),
]
S1 = [
    ('heart-gloom', [{'purified': False}, {'purified': True}], 3),
    ('deep-bellow', [{}], 3),
    ('ritch-tunnels', [{}], 3),
    ('scintillating-caves', [{'twisted': False}, {'twisted': True}], 5),
    ('ardhungol', [{}], 3),
    ('mark-spellblaze', [{}], 2),
    ('rak-shor-pride', [{}], 3),
    ('blighted-ruins', [{}], 3),
    ('reknor', [{}], 4),
    ('halfling-ruins', [{}], 4),
    ('dreadfell', [{}], 9),
]
# S3 before/after: the forest zones with crystal patches and stone rooms.
S3 = [
    ('trollmire', [{'flooded': False}, {'flooded': True}], 3),
    ('old-forest', [{'crystaline': False}, {'crystaline': True}], 4),
    ('scintillating-caves', [{'twisted': True}], 5),
    ('daikara', [{}], 4),
    ('tempest-peak', [{}], 2),
]

# S1 before/after: every zone with a census aura baseline (terrain-census-20260929).
S1_AFTER = [
    ('heart-gloom', [{'purified': False}, {'purified': True}], 3),
    ('deep-bellow', [{}], 3),
    ('ritch-tunnels', [{}], 3),
    ('scintillating-caves', [{'twisted': True}], 5),
    ('ardhungol', [{}], 3),
    ('mark-spellblaze', [{}], 2),
    ('rak-shor-pride', [{}], 3),
    ('blighted-ruins', [{}], 3),
    ('reknor', [{}], 4),
    ('halfling-ruins', [{}], 4),
    ('dreadfell', [{}], 9),
    ('trollmire', [{'flooded': True}], 3),
    ('old-forest', [{'crystaline': True}], 4),
    ('ruins-kor-pul', [{'hideout': False}, {'hideout': True}], 3),
    ('rhaloren-camp', [{'overground': False}, {'overground': True}], 3),
]


def plan(item, seeds):
    zones = {'1': ITEM1, '2': S1, 's3': S3, 's1': S1_AFTER, 'all': ITEM1 + S1}[item]
    jobs = []
    for seed in range(seeds):
        for zone, optlist, maxl in zones:
            for opts in optlist:
                for level in range(1, maxl + 1):
                    jobs.append((zone, level, opts, seed))
    return jobs


def key(job):
    zone, level, opts, seed = job
    return f'{zone}|{level}|{json.dumps(opts, sort_keys=True)}|{seed}'


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--item', default='all')
    p.add_argument('--seeds', type=int, default=1)
    p.add_argument('--chunk', type=int, default=45)
    p.add_argument('--zone')
    p.add_argument('--limit', type=int, default=0)
    p.add_argument('--gap', type=float, default=4)
    p.add_argument('--out', help='evidence directory (default: terrain-census-20260929)')
    a = p.parse_args()
    global OUT, RAW
    if a.out:
        OUT = ROOT / a.out
        RAW = OUT / 'raw.jsonl'
    OUT.mkdir(parents=True, exist_ok=True)
    done = set()
    if RAW.exists():
        for line in RAW.read_text().splitlines():
            r = json.loads(line)
            if not r.get('error'):
                done.add(r['job'])
    jobs = [j for j in plan(a.item, a.seeds) if key(j) not in done and (not a.zone or a.zone == j[0])]
    if a.limit:
        jobs = jobs[:a.limit]
    print('jobs', len(jobs), flush=True)
    starts = 0
    tries = {}
    hangs = 0
    while jobs:
        meta = launch(); starts += 1
        f = Fixture()
        count = 0
        try:
            f.lua("assert(config.settings.cheat and config.settings.disable_all_connectivity and not profile.auth);"
                  "tc=dofile('/data-checker-fixture/monster-live_terrain_census.lua');tc.setup()")
            while jobs and count < a.chunk:
                job = jobs[0]
                zone, level, opts, seed = job
                k = key(job)
                rec = {'job': k, 'zone': zone, 'level': level, 'opts': opts, 'seed': seed, 'coldstart': starts}
                hung = False
                try:
                    f.lua(f"tc.enterAndCensus({zone!r},{level},{lua_opts(opts) if opts else 'nil'},'/tc-out.json')")
                    rec['census'] = read('tc-out.json')
                    c = rec['census']
                    print('OK', k, 'total', c['total'], 'conv', c['converted'], 'native', c['native'], flush=True)
                    jobs.pop(0)
                    time.sleep(a.gap)  # let the async persistent-zone save finish
                except Exception as e:
                    rec['error'] = str(e)[-800:]
                    hung = 'did not finish' in rec['error']
                    tries[k] = tries.get(k, 0) + 1
                    print('ERR', k, 'hang' if hung else '', rec['error'][-160:].replace('\n', ' '), flush=True)
                    if not hung or tries[k] >= 3:
                        jobs.pop(0)
                    if hung:
                        hangs += 1
                with RAW.open('a') as out:
                    out.write(json.dumps(rec, ensure_ascii=False) + '\n')
                count += 1
                if hung:
                    break  # restart cold; the fixture is wedged
        finally:
            (OUT / f'transcript-cold{starts}.txt').write_text((''.join(f.transcript) + f.new_log()).rstrip() + '\n')
            stop_started(meta)
            print('STOP cold start', starts, 'hangs so far', hangs, flush=True)


if __name__ == '__main__':
    main()
