# -*- coding: utf-8 -*-
"""The shell script that defines six inline handlers is loaded by the Arabic page only.

So on 28 pages, clicking the estimate backdrop or the PWA button throws
"function is not defined" - a silent dead click. This adds the one script tag
to every page, through the part that actually closes </body> so the generator
keeps it.
"""
import os, re, sys

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
TAG = '<script src="%sjs/sr-master-shell.js" defer></script>'

# 1 · language pages (all except ar and en)
pages = []
for n in sorted(os.listdir(ROOT)):
    if n.startswith(('.', '_')) or n in {'build', 'node_modules', 'docs', 'partials', 'scripts',
                                         'assets', 'css', 'js', 'i18n', 'workers'}:
        continue
    p = os.path.join(ROOT, n, 'index.html')
    if os.path.isfile(p) and n not in ('en',):
        pages.append((p, '../'))

dry = '--dry' in sys.argv
done = 0
for path, prefix in pages:
    s = open(path, encoding='utf-8', newline='').read()
    if 'sr-master-shell.js' in s:
        print('%-16s already' % os.path.relpath(path, ROOT))
        continue
    tag = TAG % prefix
    i = s.rfind('</body>')
    if i < 0:
        print('%-16s no </body>' % os.path.relpath(path, ROOT))
        continue
    s2 = s[:i] + tag + '\r\n' + s[i:]
    if not dry:
        open(path, 'w', encoding='utf-8', newline='').write(s2)
    done += 1

# 2 · the English tail part, so the rebuilt page keeps it
tail = os.path.join(ROOT, 'partials', 'en', '99-tail.html')
t = open(tail, encoding='utf-8', newline='').read()
if 'sr-master-shell.js' not in t:
    i = t.rfind('</body>')
    if i > 0:
        t = t[:i] + (TAG % '../') + '\r\n' + t[i:]
        if not dry:
            open(tail, 'w', encoding='utf-8', newline='').write(t)
        print('partials/en/99-tail.html updated')
else:
    print('partials/en/99-tail.html already')

print('\nlanguage pages updated: %d' % done)
