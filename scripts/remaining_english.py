# -*- coding: utf-8 -*-
"""Whatever English is left on a page, verbatim, so nothing is guessed."""
import re, sys, os
import lxml.html

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
STOP = re.compile(r'\b(the|and|with|your|from|that|this|will|have|about|package|price|request|'
                  r'software|solutions|included|everything|built|designed|complete|custom)\b', re.I)

lang = sys.argv[1]
p = os.path.join(ROOT, lang, 'index.html')
html = open(p, encoding='utf-8', newline='').read()
doc = lxml.html.fromstring(html)
for bad in doc.xpath('//script|//style|//noscript'):
    bad.getparent().remove(bad)

seen = []
for el in doc.iter():
    if not isinstance(el.tag, str):
        continue
    t = re.sub(r'\s+', ' ', (el.text or '').strip())
    if len(t) < 20 or len(STOP.findall(t)) < 2:
        continue
    if t not in seen:
        seen.append(t)

print('remaining english on /%s/: %d' % (lang, len(seen)))
for t in seen:
    print('  ·', t)
