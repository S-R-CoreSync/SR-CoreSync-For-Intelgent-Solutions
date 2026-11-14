# -*- coding: utf-8 -*-
"""Apply the translation maps to the pages and count every replacement."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from translations_batch import DE, NL

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
MAPS = {'de': DE, 'nl': NL}
dry = '--dry' in sys.argv

total = 0
for lang, table in MAPS.items():
    p = os.path.join(ROOT, lang, 'index.html')
    s = open(p, encoding='utf-8', newline='').read()
    hits = 0
    for en, tr in table.items():
        n = s.count(en)
        if n:
            s = s.replace(en, tr)
            hits += n
    print('%-4s replaced %d occurrence(s)' % (lang, hits))
    total += hits
    if not dry and hits:
        open(p, 'w', encoding='utf-8', newline='').write(s)

print('\ntotal replacements:', total)
