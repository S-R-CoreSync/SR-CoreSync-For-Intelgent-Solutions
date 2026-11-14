# -*- coding: utf-8 -*-
"""Pick the first section to key: it must exist in every language with the same shape."""
import os, re

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
LANGS = []
for n in sorted(os.listdir(ROOT)):
    if n.startswith(('.', '_')) or n in {'build', 'node_modules', 'docs', 'partials', 'scripts', 'assets', 'css', 'js', 'i18n', 'workers'}:
        continue
    if os.path.isfile(os.path.join(ROOT, n, 'index.html')):
        LANGS.append(n)

CANDIDATES = {
    'dana-card (خدمات)': r'class="dana-card"',
    'wg-plan (أسعار)': r'class="wg-plan"',
    'metric-val (عدادات)': r'class="metric-val"',
    'footer columns': r'class="srf-col',
    'service-card': r'class="service-card',
}

print('%-24s %s' % ('candidate', 'count per page (min..max, pages with 0)'))
for label, pat in CANDIDATES.items():
    counts = []
    zero = 0
    for lang in LANGS:
        p = os.path.join(ROOT, 'index.html') if lang == 'index.html' else os.path.join(ROOT, lang, 'index.html')
        s = open(p, encoding='utf-8', newline='').read()
        c = len(re.findall(pat, s))
        counts.append(c)
        if c == 0:
            zero += 1
    print('%-24s %d..%d  · pages without it: %d of %d'
          % (label, min(counts), max(counts), zero, len(counts)))
