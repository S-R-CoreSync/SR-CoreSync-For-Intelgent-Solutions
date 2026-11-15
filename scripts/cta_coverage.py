# -*- coding: utf-8 -*-
"""How many pricing action blocks does each page carry?

The Arabic page has 13 (four plans × panes, plus the bundle card). The English
page has 1 - meaning three of its four packages cannot be booked from the card.
"""
import os, re

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
pages = [('index.html', 'ar')]
for n in sorted(os.listdir(ROOT)):
    if n.startswith(('.', '_')) or n in {'build', 'node_modules', 'docs', 'partials', 'scripts',
                                         'assets', 'css', 'js', 'i18n', 'workers'}:
        continue
    if os.path.isfile(os.path.join(ROOT, n, 'index.html')):
        pages.append((n + '/index.html', n))

rows = []
for rel, lang in pages:
    s = open(os.path.join(ROOT, rel), encoding='utf-8', newline='').read()
    rows.append((lang,
                 len(re.findall(r'pricing-card-actions', s)),
                 len(re.findall(r'pricing-card-btn-pdf', s)),
                 len(re.findall(r'pricing-card-btn-wa', s))))

print('%-4s %-8s %-6s %s' % ('lang', 'actions', 'pdf', 'wa'))
for lang, a, p, w in rows:
    flag = '' if a >= 10 else '   <-- short'
    print('%-4s %-8d %-6d %d%s' % (lang, a, p, w, flag))

short = [l for l, a, _, _ in rows if a < 10]
print('\npages missing most of the pricing CTAs: %d of %d' % (len(short), len(rows)))
print(' '.join(short))
