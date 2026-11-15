# -*- coding: utf-8 -*-
"""What text does the inserted block actually carry, after entity decoding?"""
import re
import lxml.html

P = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project\partials\23-store.html'
s = open(P, encoding='utf-8', newline='').read()
i = s.find('id="softwareArchitectLab"')
start = s.rfind('<div', 0, i)
depth = 0
end = None
for m in re.finditer(r'<div\b|</div>', s[start:], re.I):
    depth += -1 if m.group(0).startswith('</') else 1
    if depth == 0:
        end = start + m.end()
        break
block = s[start:end]

doc = lxml.html.fromstring(block)
print('text nodes still in latin script:')
latin = []
for el in doc.iter():
    if not isinstance(el.tag, str):
        continue
    for chunk in (el.text, el.tail):
        t = re.sub(r'\s+', ' ', (chunk or '').strip())
        if len(t) > 8 and re.search(r'[A-Za-z]{4,}', t) and not re.search(r'[\u0600-\u06FF]', t):
            latin.append(t)
            print('  ·', t[:90])
print('\ncount:', len(latin))
