# -*- coding: utf-8 -*-
"""Second section: the three service cards get meaning keys, then their text is harvested.

Same two conditions as the pricing cards: data-i18n="services.01.title" in the
markup, and one JSON per section holding every language's version.
"""
import json, os, re, sys
import lxml.html

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
OUT = os.path.join(ROOT, 'i18n', 'sections', 'services.json')

pages = [('index.html', 'ar')]
for n in sorted(os.listdir(ROOT)):
    if n.startswith(('.', '_')) or n in {'build', 'node_modules', 'docs', 'partials', 'scripts',
                                         'assets', 'css', 'js', 'i18n', 'workers'}:
        continue
    if os.path.isfile(os.path.join(ROOT, n, 'index.html')):
        pages.append((n + '/index.html', n))

TITLE = re.compile(r'(<h3 class="dana-card-title")>')
DESC = re.compile(r'(<p class="dana-card-desc")>')

# en is generated from partials/en, so it is handled through its part
TARGETS = [p for p in pages if p[1] != 'en']
TARGETS.append(('partials/en/22-pricing.html', 'en'))  # placeholder replaced below

dry = '--dry' in sys.argv
total = 0
for rel, lang in [(r, l) for r, l in pages if l != 'en']:
    p = os.path.join(ROOT, rel)
    s = open(p, encoding='utf-8', newline='').read()
    if 'data-i18n="services.01.title"' in s:
        continue
    titles = [m.start() for m in TITLE.finditer(s)]
    if len(titles) != 3:
        print('%-16s %d titles - skipped' % (lang, len(titles)))
        continue
    out, cursor = [], 0
    for idx, st in enumerate(titles, 1):
        end = titles[idx] if idx < len(titles) else len(s)
        block = s[st:end]
        mt = TITLE.search(block)
        block = block[:mt.start()] + mt.group(1) + ' data-i18n="services.%02d.title"' % idx + block[mt.end() - 1:]
        md = DESC.search(block)
        if md:
            block = block[:md.start()] + md.group(1) + ' data-i18n="services.%02d.desc"' % idx + block[md.end() - 1:]
            total += 1
        total += 1
        out.append(s[cursor:st] + block)
        cursor = end
    out.append(s[cursor:])
    if not dry:
        open(p, 'w', encoding='utf-8', newline='').write(''.join(out))

print('keys placed in 28 pages:', total)
