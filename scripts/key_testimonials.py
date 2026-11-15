# -*- coding: utf-8 -*-
"""Third section: the five testimonials get meaning keys.

Names and companies stay as they are - they are proper nouns. What gets a key:
the quote itself, and the rating label read by screen readers.
"""
import json, os, re, sys
import lxml.html

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
TEXT = re.compile(r'(<p class="tes-text[^"]*")>')
RATING = re.compile(r'(<p class="tes-rating"[^>]*aria-label=")[^"]*(")')

pages = [(os.path.join(ROOT, 'index.html'), 'ar', './')]
for n in sorted(os.listdir(ROOT)):
    if n.startswith(('.', '_')) or n in {'build', 'node_modules', 'docs', 'partials', 'scripts',
                                         'assets', 'css', 'js', 'i18n', 'workers'}:
        continue
    if os.path.isfile(os.path.join(ROOT, n, 'index.html')):
        pages.append((os.path.join(ROOT, n, 'index.html'), n, '../'))

dry = '--dry' in sys.argv
placed = 0
for path, lang, _ in pages:
    if lang == 'en':
        continue
    s = open(path, encoding='utf-8', newline='').read()
    if 'data-i18n="testimonials.01.quote"' in s:
        continue

    # quotes: walk the five blocks in order
    out, cursor, idx = [], 0, 0
    for m in TEXT.finditer(s):
        idx += 1
        out.append(s[cursor:m.start()])
        out.append(m.group(1) + ' data-i18n="testimonials.%02d.quote"' % idx + '>')
        cursor = m.end()
    out.append(s[cursor:])
    s = ''.join(out)

    # rating labels: five aria-labels, keyed by position
    out, cursor, idx = [], 0, 0
    for m in RATING.finditer(s):
        idx += 1
        out.append(s[cursor:m.start()])
        out.append(m.group(1) + ' data-i18n="testimonials.%02d.rating"' % idx + m.group(2))
        cursor = m.end()
    out.append(s[cursor:])
    s = ''.join(out)

    placed += idx + len(TEXT.findall(s))
    if not dry:
        open(path, 'w', encoding='utf-8', newline='').write(s)
    print('%-4s %d quotes · %d ratings' % (lang, len(TEXT.findall(s)), idx))

print('\nkeys placed:', placed)
