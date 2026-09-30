"""Recompute the survey-2 score (sum of E over all zones, +12 for guaranteed
boss/story identities) for every identity still unmapped and print the ranking.
Run from the addon root: python3 art/monster-batch-y/score_candidates.py"""
import re, collections
doc = open('docs/expansion-plan-20260928/MONSTER-GAP-2-20260929.md').read().splitlines()
s3 = next(n for n, l in enumerate(doc) if l.startswith('## 3.'))
e3 = next(n for n, l in enumerate(doc) if l.startswith('## 4.'))
E, G, zone = collections.defaultdict(float), set(), None
for l in doc[s3:e3]:
    m = re.match(r'### 3\.\d+ .*（`([^`]+)`）', l)
    if m: zone = m.group(1)
    if re.match(r'- (常见池|偶见池|稀有池)', l):
        for nm, ev in re.findall(r'([^、（）,，]+?)（(\d+(?:\.\d+)?)）', l.split('：', 1)[1]):
            E[nm.strip()] += float(ev)
    m = re.match(r'  - \*\*(.+?)\*\*(\[[A-Z]\])?（', l)
    if m: G.add(m.group(1))
rows, sec = {}, None
for l in doc:
    m = re.match(r'### 4\.(.+?)（', l)
    if m: sec = m.group(1)
    if sec and l.startswith('| ') and not l.startswith('| 名称') and not l.startswith('|---'):
        c = [x.strip() for x in l.strip('|').split('|')]
        if len(c) >= 8: rows.setdefault(c[0], []).append((sec, c[6]))
cat = set(re.findall(r'name="((?:[^"\\]|\\.)*)"', open('overload/mod/class/CheckerTokens.lua').read()))
sched = set()
for l in doc[next(n for n, l in enumerate(doc) if l.startswith('### 批次 1')):next(n for n, l in enumerate(doc) if l.startswith('### 后续'))]:
    if re.match(r'\| \d+ \|', l): sched.add(l.split('|')[2].strip())
out = []
for nm, r in rows.items():
    if nm in cat or nm in sched or {k for _, k in r} & {'I', 'N', 'K'}: continue
    out.append((round(E.get(nm, 0) + (12 if nm in G else 0), 6), nm, r[0][0], [x[1] for x in r], [i for i,l in enumerate(doc) if l.startswith("| "+nm+" |")]))
for v, nm, sub, k, ln in sorted(out, key=lambda x: -x[0])[:30]: print(v, nm, sub, k, ln)
print(len(out), 'unmapped candidates (Training Dummy, kept native in batch T, still listed at 12.0)')
