"""Copy approved ImageGen exports; generate only the independent geometric UI ring."""
from pathlib import Path
import hashlib
import json
import math
import re
import shutil
import struct
import subprocess
import zlib

ROOT = Path(__file__).resolve().parents[1]
dest = ROOT/'data/gfx/tokens'
dest.mkdir(parents=True, exist_ok=True)
version='.'.join(re.search(r'addon_version\s*=\s*\{([^}]+)\}',(ROOT/'init.lua').read_text())[1].replace(' ','').split(','))
manifest = {'version': version, 'size': 128, 'assets': []}
selected={}
copies=[]
# Ordered oldest to newest. A later batch that re-exports an existing identity
# replaces the earlier selection for that id; monsters-v9-refine supersedes the
# C0b giant-brown-mouse texture without touching the C0b batch on disk.
for batch in ('monsters-v1', 'monsters-v2', 'monsters-v3', 'monsters-v4', 'monsters-v5', 'monsters-v6', 'monsters-v7-c0-sol', 'monsters-v8-c0b', 'monsters-v9-refine', 'monsters-e1-gel', 'monster-batch-a', 'monster-batch-b', 'monster-batch-c', 'monster-batch-d', 'monster-batch-e', 'monster-batch-f', 'monster-batch-g', 'monster-batch-h', 'monster-batch-i', 'monster-batch-j', 'monster-batch-k', 'monster-batch-l', 'monster-batch-m', 'monster-batch-n', 'monster-batch-o', 'monster-batch-p', 'monster-batch-q', 'monster-batch-r', 'monster-batch-s', 'monster-batch-t', 'monster-batch-u', 'monster-batch-v', 'monster-batch-w', 'monster-batch-x', 'monster-batch-y', 'monster-batch-z', 'monster-batch-aa', 'monster-batch-ab', 'monster-batch-ac', 'monster-batch-ad', 'monster-batch-ae', 'monster-batch-af', 'monster-batch-ag', 'monster-batch-ua', 'monster-batch-ta1', 'monster-batch-ub1', 'monster-batch-ub2'):
    art = ROOT/'art'/batch
    if batch == 'monsters-v4' and not (art/'export-report.json').exists():
        continue
    report = json.loads((art/'export-report.json').read_text())
    if isinstance(report, list):
        # v5 retained the original flat exporter records. Its approved hashes
        # live in the artifact manifest; do not rewrite historical art metadata.
        assert batch == 'monsters-v5', 'Unknown legacy export schema'
        approved = {e['path']: e['sha256'] for e in json.loads((art/'artifact-manifest.json').read_text())}
        choices = json.loads((art/'selected-masters.json').read_text())
        assets = []
        for asset_id, master in choices.items():
            rows = [e for e in report if e['id'] == asset_id and e['size'] == 128]
            assert len(rows) == 1, 'Legacy catalog needs one 128px export per identity'
            file = rows[0]['output']
            assets.append({'id': asset_id, 'master': master, 'sha256': approved[master],
                           'exports': [{'path': file, 'size': 128, 'sha256': approved[file]}]})
        report = {'assets': assets}
    for entry in report['assets']:
        # 不在这里重测像素：128px 导出件已由 build_monster_art.py 的风格门控判定，
        # 下面的 SHA-256 校验保证拷进运行目录的就是同一批字节。只拒绝带
        # advisory 降级记录的批次，堵住"降级导出再悄悄发布"这条路。
        gate = entry.get('style_gate')
        assert gate is None or gate.get('passed', True), (
            batch, entry['id'], 'style gate failed at export; see art/production/README.md')
        assert hashlib.sha256((art/entry['master']).read_bytes()).hexdigest() == entry['sha256']
        exported = next(e for e in entry['exports'] if e['size'] == 128)
        source = art/exported['path']
        assert hashlib.sha256(source.read_bytes()).hexdigest() == exported['sha256']
        target = dest/(entry['id']+'.png')
        copies.append((source, target))
        selected[entry['id']]={'id': entry['id'], 'batch': batch, 'master_sha256': entry['sha256'],
                              'runtime_sha256': exported['sha256']}
manifest['assets']=list(selected.values())
catalog_ids = set(subprocess.check_output(['lua','-'], cwd=ROOT, text=True,
    input="local t=dofile('overload/mod/class/CheckerTokens.lua'); for _,e in ipairs(t.catalog) do print(e.id) end").splitlines())
assert set(selected) == catalog_ids, 'Art selection must exactly match the approved runtime identity catalog'
for source, target in copies:
    shutil.copy2(source, target)

# Geometric UI masks, not creature artwork or a repaint of a source image.
size = 256
def chunk(name, data):
    return struct.pack('>I',len(data))+name+data+struct.pack('>I',zlib.crc32(name+data)&0xffffffff)
def mask(name, rings, pattern=None):
    rows=bytearray()
    for y in range(size):
        rows.append(0)
        for x in range(size):
            dx,dy=x+.5-size/2,y+.5-size/2
            distance=math.hypot(dx,dy)/size
            coverage=max(max(0.,min(1.,(distance-inner)*size+.5,(outer-distance)*size+.5)) for inner,outer in rings)
            angle=math.atan2(dy,dx)%(2*math.pi)
            if pattern=='enemy' and min(angle%(math.pi/2),math.pi/2-angle%(math.pi/2))<.075: coverage=0
            if pattern=='neutral' and angle%(math.pi/6)>math.pi/12: coverage=0
            if pattern=='ticks' and min(angle%(math.pi/2),math.pi/2-angle%(math.pi/2))>.035: coverage=0
            rows.extend((255,255,255,round(255*coverage)))
    png=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',size,size,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(rows))+chunk(b'IEND',b'')
    (dest/(name+'.png')).write_bytes(png)
mask('_relation-back',[(.402,.498)])
for relation in ('enemy','neutral','friend','player'):
    mask('_relation-'+relation,[(.416,.49)],relation)
    # Persistent relation rim stays readable even when almost all HP is lost.
    mask('_relation-edge-'+relation,[(.474,.495)],relation)
# This neutral mask is clipped by native vertex geometry at runtime. The
# smooth health arc is independent of the faction outline's notch/dash shape.
mask('_health-band',[(.410,.463)])
mask('_player-inner',[(.388,.403)])
mask('_shield-track',[(.459,.499)])
mask('_shield-band',[(.465,.493)])
mask('_shield-ticks',[(.473,.495)],'ticks')

def polygon_mask(name,polygons):
    def inside(px,py,poly):
        found=False
        j=len(poly)-1
        for i,(x,y) in enumerate(poly):
            xx,yy=poly[j]
            if (y>py)!=(yy>py) and px<(xx-x)*(py-y)/(yy-y)+x: found=not found
            j=i
        return found
    rows=bytearray()
    for y in range(size):
        rows.append(0)
        for x in range(size):
            coverage=sum(any(inside((x+sx)/size,(y+sy)/size,p) for p in polygons)
                         for sx,sy in ((.25,.25),(.75,.25),(.25,.75),(.75,.75)))
            rows.extend((255,255,255,round(coverage*255/4)))
    png=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',size,size,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(rows))+chunk(b'IEND',b'')
    (dest/(name+'.png')).write_bytes(png)

polygon_mask('_badge-back',[[(.07,.03),(.93,.03),(1,.18),(1,.91),(.08,1),(0,.83),(0,.16)]])
polygon_mask('_badge-rare',[[(.5,.18),(.8,.5),(.5,.82),(.2,.5)]])
polygon_mask('_badge-unique',[
    [(.32,.17),(.51,.5),(.32,.82),(.13,.5)],[(.68,.17),(.87,.5),(.68,.82),(.49,.5)]])
crown=[(.12,.2),(.31,.46),(.5,.12),(.69,.46),(.88,.2),(.81,.73),(.19,.73)]
bar=[(.19,.8),(.81,.8),(.81,.9),(.19,.9)]
polygon_mask('_badge-boss',[crown,bar])
polygon_mask('_badge-elite_boss',[
    [(.1,.2),(.24,.42),(.3,.16),(.4,.4),(.5,.09),(.6,.4),(.7,.16),(.76,.42),(.9,.2),(.83,.73),(.17,.73)],bar])
polygon_mask('_badge-god',[crown,bar,[(.12,.05),(.18,.05),(.22,.16),(.16,.16)],[(.82,.05),(.88,.05),(.84,.16),(.78,.16)]])
# Rank 3 (elite) is deliberately unmarked. The old filename meant elite boss.
(dest/'_badge-elite.png').unlink(missing_ok=True)
# The old concentric gold rank marker is replaced by a corner badge.
(dest/'_rank-ring.png').unlink(missing_ok=True)
# Keep the obsolete 0.4.0 texture out of the new package.
(dest/'_relation-ring.png').unlink(missing_ok=True)
(ROOT/'data/token-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(f'Prepared {len(selected)} selected 128px AI exports + relation, shield and rank badge UI masks')
