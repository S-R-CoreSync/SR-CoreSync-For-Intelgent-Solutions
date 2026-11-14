# -*- coding: utf-8 -*-
"""How much of a language page is actually rewritten from the master?"""
import os, re

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
src = open(os.path.join(ROOT, 'scripts', 'sync_locales.py'), encoding='utf-8').read()

m = re.search(r"BEGIN\s*=\s*['\"](.+?)['\"]", src)
n = re.search(r"END\s*=\s*['\"](.+?)['\"]", src)
print('the synced block is delimited by:')
print('  BEGIN:', (m.group(1)[:70] + '…') if m else '?')
print('  END  :', (n.group(1)[:70] + '…') if n else '?')

page = os.path.getsize(os.path.join(ROOT, 'de', 'index.html'))
hero = 0
if m and n:
    s = open(os.path.join(ROOT, 'de', 'index.html'), encoding='utf-8').read()
    a, b = s.find(m.group(1)), s.find(n.group(1))
    if a > 0 and b > a:
        hero = b - a

print()
print('german page                 %.0f KB' % (page / 1024))
print('rewritten from the master   %.0f KB  (%.0f%%)' % (hero / 1024, 100 * hero / page))
print('left to the language itself %.0f KB  (%.0f%%)' % ((page - hero) / 1024, 100 * (page - hero) / page))
