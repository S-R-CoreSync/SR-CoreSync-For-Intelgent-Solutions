# -*- coding: utf-8 -*-
"""Reorder the master's page sections to match the menu: services, pricing, store, about, leadership."""
import re

P = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project\index.html'
s = open(P, encoding='utf-8', newline='').read()

ORDER = ['service', 'services', 'pricing', 'software-hub', 'about', 'founders-showcase']
TAG = {'service': 'div'}


def find(tag, ident):
    m = re.search(r'<%s\b[^>]*\bid="%s"' % (tag, re.escape(ident)), s)
    assert m, 'not found: ' + ident
    i = m.start()
    depth = 0
    for t in re.finditer(r'<%s\b|</%s>' % (tag, tag), s[i:]):
        if t.group(0).startswith('</'):
            depth -= 1
            if depth == 0:
                return i, i + t.end()
        else:
            depth += 1
    raise SystemExit('unbalanced: ' + ident)


spans = {}
for b in ORDER:
    spans[b] = find(TAG.get(b, 'section'), b)

for b in ORDER:
    a, z = spans[b]
    print('%-18s %7d .. %7d  (%d bytes)' % (b, a, z, z - a))

insert_at = spans['about'][0]
ordered = ''.join(s[spans[b][0]:spans[b][1]] for b in ORDER)

# remove the six, last first
for b in sorted(ORDER, key=lambda x: -spans[x][0]):
    a, z = spans[b]
    s = s[:a] + s[z:]

# insert at the earliest position (about's old start)
s = s[:insert_at] + ordered + s[insert_at:]

open(P, 'w', encoding='utf-8', newline='').write(s)
print('reordered. bytes:', len(s))
