# -*- coding: utf-8 -*-
"""Fourth section: nine software cards. The product names stay; the descriptions get keys.

Same safety as the last section: after stripping the new attributes the file must
be byte-identical to what it was, or nothing is written.
"""
import os, re, sys

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
DESC = re.compile(r'(<p class="text-white-64 software-card-desc")>')
STRIP = re.compile(r' data-i18n="software\.\d\d\.desc"')

pages = [(os.path.join(ROOT, 'index.html'), 'ar')]
for n in sorted(os.listdir(ROOT)):
    if n.startswith(('.', '_')) or n in {'build', 'node_modules', 'docs', 'partials', 'scripts',
                                         'assets', 'css', 'js', 'i18n', 'workers'}:
        continue
    if os.path.isfile(os.path.join(ROOT, n, 'index.html')):
        pages.append((os.path.join(ROOT, n, 'index.html'), n))

dry = '--dry' in sys.argv
bad = 0
for path, lang in pages:
    s = open(path, encoding='utf-8', newline='').read()
    if 'data-i18n="software.01.desc"' in s:
        continue
    original = s
    i = 0

    def add(m):
        global i
        i += 1
        return m.group(1) + ' data-i18n="software.%02d.desc"' % i + '>'

    s = DESC.sub(add, s)
    if i != 9:
        print('%-4s %d descriptions (expected 9) - skipped' % (lang, i))
        bad += 1
        continue
    if STRIP.sub('', s) != original:
        print('%-4s text changed - skipped' % lang)
        bad += 1
        continue
    if not dry:
        open(path, 'w', encoding='utf-8', newline='').write(s)
    print('%-4s 9 keys' % lang)

print('\nskipped:', bad)
