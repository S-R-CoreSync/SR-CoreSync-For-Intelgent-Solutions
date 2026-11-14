"""Point every Latin rule at Figtree.

147 declarations name Plus Jakarta Sans; 20 already name Figtree. After this the
site has two faces only: Alexandria for Arabic, Figtree for Latin, everywhere.
"""
import os, re, sys

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
targets = []
for base, dirs, names in os.walk(ROOT):
    dirs[:] = [d for d in dirs if d not in {'.git', '_site', 'node_modules', 'docs', 'scripts', 'build', '.zwork'}]
    for n in names:
        if n.endswith(('.css', '.html')):
            targets.append(os.path.join(base, n))

PATTERNS = [
    ("'Plus Jakarta Sans'", "'Figtree'"),
    ('"Plus Jakarta Sans"', "'Figtree'"),
    ('Plus Jakarta Sans', 'Figtree'),
]

dry = '--dry' in sys.argv
total = 0
files = 0
for p in targets:
    try:
        s = open(p, encoding='utf-8', newline='').read()
    except Exception:
        continue
    orig = s
    n = 0
    for old, new in PATTERNS:
        n += s.count(old)
        s = s.replace(old, new)
    if s != orig:
        files += 1
        total += n
        if not dry:
            open(p, 'w', encoding='utf-8', newline='').write(s)
        print('%-46s %d' % (os.path.relpath(p, ROOT)[:46], n))

print('\nfiles touched: %d · declarations changed: %d' % (files, total))
