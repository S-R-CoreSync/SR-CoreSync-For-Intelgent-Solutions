# -*- coding: utf-8 -*-
"""English left on a page, including text that follows an inline element.

The first version read el.text only, so 'Everything included in the Starter
package' hid behind <span>//</span> as a tail. That is why two passes claimed
zero while the page still showed English.
"""
import re, sys, os
import lxml.html

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
STOP = re.compile(r'\b(the|and|with|your|from|that|this|will|have|about|package|price|request|'
                  r'software|solutions|included|everything|built|designed|complete|custom|'
                  r'partner|trusted|months|within|day)\b', re.I)


def harvest(path):
    html = open(path, encoding='utf-8', newline='').read()
    doc = lxml.html.fromstring(html)
    for bad in doc.xpath('//script|//style|//noscript'):
        bad.getparent().remove(bad)
    out = []
    for el in doc.iter():
        if not isinstance(el.tag, str):
            continue
        for chunk in (el.text, el.tail):
            t = re.sub(r'\s+', ' ', (chunk or '').strip())
            if len(t) >= 20 and len(STOP.findall(t)) >= 2 and t not in out:
                out.append(t)
    return out


lang = sys.argv[1]
items = harvest(os.path.join(ROOT, lang, 'index.html'))
print('remaining english on /%s/: %d' % (lang, len(items)))
for t in items:
    print('  ·', t)
