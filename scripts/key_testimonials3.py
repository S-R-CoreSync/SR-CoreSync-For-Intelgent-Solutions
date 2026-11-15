# -*- coding: utf-8 -*-
"""Key the five testimonials, keeping every character of the original text.

Two failed attempts before this one:
  1. the rating label was captured and then thrown away;
  2. the key was inserted inside the attribute value.
Both were caught by comparing the file to its own copy after stripping the new
attributes. That comparison is now part of the script, not a separate check.
"""
import os, re, sys

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
TEXT = re.compile(r'(<p class="tes-text[^"]*")>')
RATING = re.compile(r'(<p class="tes-rating"[^>]*?aria-label=")([^"]*)(")')

pages = [(os.path.join(ROOT, 'index.html'), 'ar')]
for n in sorted(os.listdir(ROOT)):
    if n.startswith(('.', '_')) or n in {'build', 'node_modules', 'docs', 'partials', 'scripts',
                                         'assets', 'css', 'js', 'i18n', 'workers'}:
        continue
    if os.path.isfile(os.path.join(ROOT, n, 'index.html')):
        pages.append((os.path.join(ROOT, n, 'index.html'), n))

STRIP = re.compile(r' data-i18n="testimonials\.\d\d\.(?:quote|rating)"')
dry = '--dry' in sys.argv
fail = 0

for path, lang in pages:
    s = open(path, encoding='utf-8', newline='').read()
    if 'data-i18n="testimonials.01.quote"' in s:
        continue
    original = s

    i = 0
    def add_quote(m):
        global i
        i += 1
        return m.group(1) + ' data-i18n="testimonials.%02d.quote"' % i + '>'
    s = TEXT.sub(add_quote, s)
    quotes = i

    i = 0
    def add_rating(m):
        global i
        i += 1
        # keep label and its closing quote, then append the attribute
        return m.group(1) + m.group(2) + m.group(3) + ' data-i18n="testimonials.%02d.rating"' % i
    s = RATING.sub(add_rating, s)
    ratings = i

    if STRIP.sub('', s) != original:
        print('%-4s TEXT CHANGED - not written' % lang)
        fail += 1
        continue

    if not dry:
        open(path, 'w', encoding='utf-8', newline='').write(s)
    print('%-4s quotes=%d ratings=%d ok' % (lang, quotes, ratings))

print('\nchanged text in %d page(s)' % fail)
