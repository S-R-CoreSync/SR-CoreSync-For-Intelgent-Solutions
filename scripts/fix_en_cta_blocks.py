# -*- coding: utf-8 -*-
"""The English pricing cards have no action block at all for three of four plans.

This appends the master's block for the same plan position, with the label in
English. Only cards that show a price but offer no action are touched.
"""
import os, re

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
MASTER = os.path.join(ROOT, 'index.html')
EN = os.path.join(ROOT, 'en', 'index.html')


def blocks(html):
    out = []
    for m in re.finditer(r'<div class="pricing-card-actions">', html):
        start = m.start()
        depth = 0
        for t in re.finditer(r'<div\b|</div>', html[start:], re.I):
            depth += -1 if t.group(0).startswith('</') else 1
            if depth == 0:
                out.append(html[start:start + t.end()])
                break
    return out


master = open(MASTER, encoding='utf-8', newline='').read()
mblocks = blocks(master)

s = open(EN, encoding='utf-8', newline='').read()
print('english action blocks before:', len(blocks(s)))

# the four plans of the first pane, in order
plan_spans = []
for m in re.finditer(r'<div class="wg-plan">', s):
    start = m.start()
    depth = 0
    for t in re.finditer(r'<div\b|</div>', s[start:], re.I):
        depth += -1 if t.group(0).startswith('</') else 1
        if depth == 0:
            plan_spans.append((start, start + t.end()))
            break

print('english plans:', len(plan_spans))
added = 0
for i, (start, end) in enumerate(plan_spans[:4]):
    plan = s[start:end]
    if 'pricing-card-actions' in plan:
        continue
    src = mblocks[i] if i < len(mblocks) else None
    if not src:
        continue
    block = src.replace('حجز الباقة عبر واتساب 💬', 'Book the package on WhatsApp 💬')
    block = re.sub(r'<span>[^<]*</span>(?=\s*</button>)', '<span>Request an official quote 📄</span>', block, count=1)
    # place it before the benefit list if there is one, else before the plan closes
    anchor = plan.find('<ul class="benefit-list')
    cut = start + (anchor if anchor > 0 else len(plan) - len('</div>'))
    s = s[:cut] + block + '\r\n' + s[cut:]
    added += 1

open(EN, 'w', encoding='utf-8', newline='').write(s)
print('blocks added:', added, '· english action blocks after:', len(blocks(s)))
