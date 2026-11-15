# -*- coding: utf-8 -*-
"""Which pricing CTA in the English part still has no key, and what does its markup look like?"""
import os, re

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
P = os.path.join(ROOT, 'partials', 'en', '22-pricing.html')
s = open(P, encoding='utf-8', newline='').read()

for i in range(1, 5):
    has = 'pricing.plan%d.cta' % i in s
    print('plan%d cta key: %s' % (i, 'yes' if has else 'NO'))

PLAN = re.compile(r'class="wg-plan"')
starts = [m.start() for m in PLAN.finditer(s)]
print('\nCTA markup per plan:')
for idx, st in enumerate(starts, 1):
    end = starts[idx] if idx < len(starts) else len(s)
    block = s[st:end]
    m = re.search(r'<a[^>]*class="(pricing-card-btn-[a-z-]+)"[^>]*>\s*<span[^>]*>([^<]{0,50})', block)
    print('  plan%d: %s -> %s' % (idx, m.group(1) if m else '?', m.group(2).strip()[:40] if m else '?'))
