# -*- coding: utf-8 -*-
"""The union of English strings still on the four pages of this batch."""
import os, re
import lxml.html

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
STOP = re.compile(r'\b(the|and|with|your|from|that|this|will|have|about|package|price|request|'
                  r'software|solutions|included|everything|built|designed|complete|custom|'
                  r'partner|trusted|months|within|study|capital|highlight)\b', re.I)

LANGS = ['no', 'fi', 'el', 'et']
union = {}

for lang in LANGS:
    p = os.path.join(ROOT, lang, 'index.html')
    doc = lxml.html.fromstring(open(p, encoding='utf-8', newline='').read())
    for bad in doc.xpath('//script|//style|//noscript'):
        bad.getparent().remove(bad)
    found = set()
    for el in doc.iter():
        if not isinstance(el.tag, str):
            continue
        for chunk in (el.text, el.tail):
            t = re.sub(r'\s+', ' ', (chunk or '').strip())
            if len(t) >= 20 and len(STOP.findall(t)) >= 2:
                found.add(t)
    union[lang] = found
    print('%-3s %d' % (lang, len(found)))

allstr = set().union(*union.values())
print('\nunion: %d strings' % len(allstr))
for i, t in enumerate(sorted(allstr, key=len, reverse=True), 1):
    print('%2d. %s' % (i, t))
