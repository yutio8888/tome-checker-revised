"""Capture the local HTML art review at a true device scale of 1; no image edits."""
from pathlib import Path
import argparse
import json
import os
import subprocess

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--batch', choices=('monsters-v1', 'monsters-v2'), default='monsters-v1')
parser.add_argument('--browser', type=Path, default=Path('~/.cache/ms-playwright/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell'))
parser.add_argument('--libraries', type=Path, default=Path('~/.cache/sgstory-chrome-deps/usr/lib/x86_64-linux-gnu'))
parser.add_argument('--playwright', type=Path, default=Path('~/.npm/_npx/e41f203b7505f1fb/node_modules/playwright-core'))
args = parser.parse_args()
ART = ROOT / 'art' / args.batch
assert args.browser.exists(), 'Provide --browser for a locally installed Chromium'
assert args.playwright.exists(), 'Provide --playwright for a locally installed playwright-core module'
env = dict(os.environ)
if args.libraries.exists():
    env['LD_LIBRARY_PATH'] = str(args.libraries) + (':' + env['LD_LIBRARY_PATH'] if env.get('LD_LIBRARY_PATH') else '')
outdir = ART / 'review'
outdir.mkdir(exist_ok=True)
pages = [('five-monsters.png',''), ('faction-enemy.png','?faction=enemy'), ('grayscale.png','?grey=1')]
if args.batch == 'monsters-v2':
    pages = [('seventeen-monsters.png','?compact=1&all=1'), ('twelve-monsters.png','?compact=1'), ('giants.png','?group=giants'), ('beasts.png','?group=beasts'), ('shapes.png','?group=shapes'), ('grayscale.png','?compact=1&all=1&grey=1')]
jobs = [{'file': str(outdir/filename), 'url': (ART/'index.html').as_uri()+query,
         'count': (17 if 'all=1' in query else 4 if 'group=' in query else 12)
                  if args.batch == 'monsters-v2' else 5}
        for filename, query in pages]
if args.batch == 'monsters-v2':
    jobs.extend([
        {'file': str(outdir/'shapes-water.png'), 'url': (ART/'index.html').as_uri()+'?group=shapes',
         'count': 4, 'select': {'#ground': 'water'}},
        {'file': str(outdir/'beasts-faction.png'), 'url': (ART/'index.html').as_uri()+'?group=beasts',
         'count': 4, 'select': {'#faction': '#cf6356'}},
    ])
config = {'browser': str(args.browser), 'playwright': str(args.playwright), 'jobs': jobs,
          'report': str(outdir/'capture-report.json')}
subprocess.run(['node', str(ROOT/'tools/capture_monster_review.cjs')], env=env,
               input=json.dumps(config), text=True, check=True, timeout=90)
