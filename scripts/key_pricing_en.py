# -*- coding: utf-8 -*-
"""The English page is generated from partials/en, so the keys belong in the part."""
import os, re

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
P = os.path.join(ROOT, 'partials', 'en', '22-pricing.html')
s = open(P, encoding='utf-8', newline='').read()

if 'data-i18n="pricing.plan1' in s:
    print('already keyed')
    raise SystemExit

PLAN = re.compile(r'class="wg-plan"')
PERIOD = re.compile(r'(<span class="text-body-2 fw-normal[^"]*")>')
DESC = re.compile(r'(<p class="plan-desc[^"]*")>')
CTA = re.compile(r'(<a[^>]+class="pricing-card-btn-wa"[^>]*>\s*<span)>')

starts = [m.start() for m in PLAN.finditer(s)]
print('plans in the part:', len(starts))
if len(starts) != 4:
    raise SystemExit('unexpected plan count')

out, cursor, n = [], 0, 0
for idx, st in enumerate(starts, 1):
    end = starts[idx] if idx < len(starts) else len(s)
    block = s[st:end]
    for rx, suffix in ((PERIOD, 'period'), (DESC, 'desc'), (CTA, 'cta')):
        m = rx.search(block)
        if not m:
            print('missing slot %s in plan %d' % (suffix, idx))
            continue
        key = 'pricing.plan%d.%s' % (idx, suffix)
        block = block[:m.start()] + m.group(1) + ' data-i18n="%s"' % key + block[m.end() - 1:]
        n += 1
    out.append(s[cursor:st] + block)
    cursor = end
out.append(s[cursor:])

open(P, 'w', encoding='utf-8', newline='').write(''.join(out))
print('keys added to the part:', n)
