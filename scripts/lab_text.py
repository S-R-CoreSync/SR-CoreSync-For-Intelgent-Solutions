# -*- coding: utf-8 -*-
"""Extract the lab block from the English part and list every text node it carries."""
import re
import lxml.html

P = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project\partials\en\23-store.html'
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
print('block: %.1f KB' % (len(block.encode()) / 1024))

doc = lxml.html.fromstring(block)
print('\ntext nodes:')
seen = []
for el in doc.iter():
    if not isinstance(el.tag, str):
        continue
    for chunk in (el.text, el.tail):
        t = re.sub(r'\s+', ' ', (chunk or '').strip())
        if len(t) > 12 and t not in seen:
            seen.append(t)
            print('  %-14s %s' % (el.tag, t[:96]))
print('\ndistinct strings:', len(seen))
