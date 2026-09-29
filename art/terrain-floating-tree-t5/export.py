#!/usr/bin/env python3
"""Compose reviewed transparent burnt-tree art on Abashed's connected rock cells."""
from pathlib import Path
from PIL import Image,ImageEnhance
import json,hashlib
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
OUT=ROOT/'data/gfx/refined/void';OUT.mkdir(exist_ok=True)
TREE=ROOT/'art/terrain-burnt-v1/masters/burnt-tree-v1.png'
source=Image.open(TREE).convert('RGBA').resize((128,128),Image.Resampling.LANCZOS)
for mask in range(16):
 for parity in (0,1):
  rock=Image.open(OUT/f'rocks-{mask}-{parity}.png').convert('RGBA')
  tree=source if parity==0 else ImageEnhance.Brightness(source).enhance(.82)
  rock.alpha_composite(tree,(0,0))
  rock.convert('RGB').save(OUT/f'rocks-tree-{mask}-{parity}.png')
files={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(OUT.glob('rocks-tree-*.png'))}
(HERE/'export-manifest.json').write_text(json.dumps({'source_master':str(TREE.relative_to(ROOT)),'source_sha256':hashlib.sha256(TREE.read_bytes()).hexdigest(),'files':files,'new_imagegen_calls':0},indent=2)+'\n')
