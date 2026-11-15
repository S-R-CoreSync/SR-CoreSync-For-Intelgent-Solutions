# -*- coding: utf-8 -*-
"""Which section is shaped the same in all 29 pages, and carries real copy?

A section can only be generated from the master if every page has the same
skeleton. This measures uniformity, then size, so the next keying is not a guess.
"""
import os, re

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
pages = []
for n in sorted(os.listdir(ROOT)):
    if n.startswith(('.', '_')) or n in {'build', 'node_modules', 'docs', 'partials', 'scripts',
                                         'assets', 'css', 'js', 'i18n', 'workers'}:
        continue
    if os.path.isfile(os.path.join(ROOT, n, 'index.html')):
        pages.append(os.path.join(ROOT, n, 'index.html'))
pages.append(os.path.join(ROOT, 'index.html'))

CANDIDATES = [
    ('services cards', r'class="dana-card'),
    ('service tiles', r'class="service-card'),
    ('testimonials', r'class="testimonial'),
    ('faq items', r'class="accordion-item'),
    ('footer columns', r'class="srf-col'),
    ('software cards', r'class="software-card'),
    ('pillars', r'class="tech-pillar'),
    ('pricing plans', r'class="wg-plan"'),
    ('metrics strip', r'class="trust-metric-item'),
    ('process steps', r'class="process-step'),
]

for label, pat in CANDIDATES:
    counts = []
    for p in pages:
        s = open(p, encoding='utf-8', newline='').read()
        counts.append(len(re.findall(pat, s)))
    uniq = sorted(set(counts))
    verdict = 'uniform' if len(uniq) == 1 and uniq[0] > 0 else 'varies'
    print('%-18s %-8s counts=%s' % (label, verdict, uniq[:6]))
