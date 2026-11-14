# -*- coding: utf-8 -*-
"""English uses pricing-card-btn-gold where Arabic uses -wa; key both."""
import os, re

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
P = os.path.join(ROOT, 'partials', 'en', '22-pricing.html')
s = open(P, encoding='utf-8', newline='').read()

PLAN = re.compile(r'class="wg-plan"')
CTA = re.compile(r'(<a[^>]+class="pricing-card-btn-gold"[^>]*>\s*<span)>')

starts = [m.start() for m in PLAN.finditer(s)]
out, cursor, n = [], 0, 0
for idx, st in enumerate(starts, 1):
    end = starts[idx] if idx < len(starts) else len(s)
    b = s[st:end]
    m = CTA.search(b)
    if m and 'pricing.plan%d.cta' % idx not in b:
        b = b[:m.start()] + m.group(1) + ' data-i18n="pricing.plan%d.cta"' % idx + b[m.end() - 1:]
        n += 1
    out.append(s[cursor:st] + b)
    cursor = end
out.append(s[cursor:])
open(P, 'w', encoding='utf-8', newline='').write(''.join(out))
print('cta keys added:', n)
