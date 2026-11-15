# -*- coding: utf-8 -*-
"""Key the three service cards inside the English part, then rebuild the page."""
import os, re

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
P = os.path.join(ROOT, 'partials', 'en', '21-services.html')
s = open(P, encoding='utf-8', newline='').read()

if 'data-i18n="services.01.title"' in s:
    print('already keyed')
    raise SystemExit

TITLE = re.compile(r'(<h3 class="dana-card-title")>')
DESC = re.compile(r'(<p class="dana-card-desc")>')

starts = [m.start() for m in TITLE.finditer(s)]
print('cards:', len(starts))
out, cursor, n = [], 0, 0
for idx, st in enumerate(starts, 1):
    end = starts[idx] if idx < len(starts) else len(s)
    block = s[st:end]
    mt = TITLE.search(block)
    block = block[:mt.start()] + mt.group(1) + ' data-i18n="services.%02d.title"' % idx + block[mt.end() - 1:]
    n += 1
    md = DESC.search(block)
    if md:
        block = block[:md.start()] + md.group(1) + ' data-i18n="services.%02d.desc"' % idx + block[md.end() - 1:]
        n += 1
    out.append(s[cursor:st] + block)
    cursor = end
out.append(s[cursor:])
open(P, 'w', encoding='utf-8', newline='').write(''.join(out))
print('keys added:', n)
