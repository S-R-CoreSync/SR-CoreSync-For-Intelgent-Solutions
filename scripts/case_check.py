# -*- coding: utf-8 -*-
"""Case-sensitive reference check: Windows forgives, the Linux runner does not."""
import os, re

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
GF = os.path.join(ROOT, 'assets', 'fonts', 'gf')
actual = {f.lower(): f for f in os.listdir(GF)}

for sheet in ('fonts.css', 'mono.css'):
    p = os.path.join(GF, sheet)
    if not os.path.exists(p):
        continue
    css = open(p, encoding='utf-8').read()
    for ref in re.findall(r'url\(\./([^)]+\.woff2)\)', css):
        if ref not in actual.values():
            hint = actual.get(ref.lower())
            print('%-12s %-30s -> %s' % (sheet, ref, ('case differs: ' + hint) if hint else 'MISSING'))

# and every page's font preloads
pages = ['index.html'] + [os.path.join(d, 'index.html') for d in sorted(os.listdir(ROOT))
                          if os.path.isfile(os.path.join(ROOT, d, 'index.html'))]
bad = 0
for rel in pages:
    s = open(os.path.join(ROOT, rel), encoding='utf-8', newline='').read()
    for m in re.finditer(r'href="(?:\.\./|\./)assets/fonts/gf/([^"?]+)', s):
        name = m.group(1)
        if name not in actual.values():
            hint = actual.get(name.lower())
            print('%-18s %-28s -> %s' % (rel, name, ('case: ' + hint) if hint else 'MISSING'))
            bad += 1
print('\npreload mismatches:', bad)
