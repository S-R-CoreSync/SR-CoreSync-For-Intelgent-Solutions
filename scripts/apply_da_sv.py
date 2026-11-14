# -*- coding: utf-8 -*-
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from translations_da_sv import DA, SV

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
for lang, table in (('da', DA), ('sv', SV)):
    p = os.path.join(ROOT, lang, 'index.html')
    s = open(p, encoding='utf-8', newline='').read()
    hits = 0
    for en, tr in table.items():
        n = s.count(en)
        if n:
            s = s.replace(en, tr)
            hits += n
    open(p, 'w', encoding='utf-8', newline='').write(s)
    left = sum(1 for en in table if en in s)
    print('%-3s replaced %-3d · still english: %d of %d' % (lang, hits, left, len(table)))
