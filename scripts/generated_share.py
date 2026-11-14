# -*- coding: utf-8 -*-
"""How much of a page is already generated from the master, and how much is still hand-kept?"""
import os

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
part = os.path.join(ROOT, 'partials')
files = [os.path.join(part, f) for f in os.listdir(part) if f.endswith('.html')]
gen = sum(os.path.getsize(f) for f in files)

page = os.path.getsize(os.path.join(ROOT, 'index.html'))
# the language pages carry the same generated hero/footer but a different body
de = os.path.getsize(os.path.join(ROOT, 'de', 'index.html'))

print('root page            %.0f KB' % (page / 1024))
print('parts that are the source of truth  %.0f KB  (%.0f%% of the page)'
      % (gen / 1024, 100 * gen / page))
print('still hand-maintained per language  %.0f KB  (%.0f%%)'
      % ((page - gen) / 1024, 100 * (page - gen) / page))
print()
print('german page          %.0f KB' % (de / 1024))
print('29 pages on disk     %.1f MB' % (sum(
    os.path.getsize(os.path.join(ROOT, d, 'index.html'))
    for d in os.listdir(ROOT)
    if os.path.isfile(os.path.join(ROOT, d, 'index.html'))) / 1024 / 1024))
