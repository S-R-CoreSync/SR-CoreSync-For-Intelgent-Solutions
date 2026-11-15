# -*- coding: utf-8 -*-
"""Extract the Arabic pricing action blocks, in document order, with their exact markup."""
import re

P = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project\index.html'
s = open(P, encoding='utf-8', newline='').read()

blocks = []
for m in re.finditer(r'<div class="pricing-card-actions">', s):
    start = m.start()
    depth = 0
    end = None
    for t in re.finditer(r'<div\b|</div>', s[start:], re.I):
        depth += -1 if t.group(0).startswith('</') else 1
        if depth == 0:
            end = start + t.end()
            break
    blocks.append(s[start:end])

print('action blocks:', len(blocks))
for i, b in enumerate(blocks, 1):
    btns = re.findall(r'<(a|button)[^>]*class="(pricing-card-btn-[a-z-]+)"', b)
    args = re.findall(r"data-sr-args='([^']*)'", b)
    print('  %2d: %-28s args=%s' % (i, ','.join(c.replace('pricing-card-btn-', '') for _, c in btns), args[:1]))

# keep the first block for reuse
open(r'C:\Users\msali\AppData\Local\Temp\ar_block_1.html', 'w', encoding='utf-8').write(blocks[0])
print('\nsaved block 1 for inspection')
