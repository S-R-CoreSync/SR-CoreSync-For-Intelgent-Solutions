# -*- coding: utf-8 -*-
"""Key the five testimonials - keeping the text this time.

The first attempt dropped the aria-label of the rating: the pattern captured the
label but the replacement only re-emitted the quotes around it, so screen readers
lost "rated 5 out of 5". This version keeps every captured group.
"""
import os, re, sys

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
TEXT = re.compile(r'(<p class="tes-text[^"]*")>')
RATING = re.compile(r'(<p class="tes-rating"[^>]*aria-label=")([^"]*)(")')

pages = [(os.path.join(ROOT, 'index.html'), 'ar')]
for n in sorted(os.listdir(ROOT)):
    if n.startswith(('.', '_')) or n in {'build', 'node_modules', 'docs', 'partials', 'scripts',
                                         'assets', 'css', 'js', 'i18n', 'workers'}:
        continue
    if os.path.isfile(os.path.join(ROOT, n, 'index.html')):
        pages.append((os.path.join(ROOT, n, 'index.html'), n))

dry = '--dry' in sys.argv
for path, lang in pages:
    s = open(path, encoding='utf-8', newline='').read()
    if 'data-i18n="testimonials.01.quote"' in s:
        continue

    idx = 0
    def add_quote(m):
        global idx
        idx += 1
        return m.group(1) + ' data-i18n="testimonials.%02d.quote"' % idx + '>'
    s = TEXT.sub(add_quote, s)
    quotes = idx

    idx = 0
    def add_rating(m):
        global idx
        idx += 1
        return m.group(1) + ' data-i18n="testimonials.%02d.rating"' % idx + '"' + m.group(2) + m.group(3)
    s = RATING.sub(add_rating, s)
    ratings = idx

    if not dry:
        open(path, 'w', encoding='utf-8', newline='').write(s)
    print('%-4s quotes=%d ratings=%d (label kept=%s)'
          % (lang, quotes, ratings, 'yes' if 'aria-label="التقييم' in s or 'aria-label="' in s else '?'))
