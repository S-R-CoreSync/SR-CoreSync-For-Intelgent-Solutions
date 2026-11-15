# -*- coding: utf-8 -*-
"""ku/index.html ends with '/body>' - the '<' was eaten by an earlier edit.

Browsers forgive it; the handler audit does not, because it cannot find the end
of the document. This repairs the tag and then places the script where it belongs.
"""
import os, re

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
TAG = '<script src="../js/sr-master-shell.js" defer></script>'

# 1 · report every page whose body close tag is malformed
pages = [('index.html', 'ar')]
for n in sorted(os.listdir(ROOT)):
    if n.startswith(('.', '_')) or n in {'build', 'node_modules', 'docs', 'partials', 'scripts',
                                         'assets', 'css', 'js', 'i18n', 'workers'}:
        continue
    if os.path.isfile(os.path.join(ROOT, n, 'index.html')):
        pages.append((n + '/index.html', n))
    if os.path.isfile(os.path.join(ROOT, n, 'demo.html')):
        pages.append((n + '/demo.html', n + '/demo'))

broken = []
for rel, lang in pages:
    s = open(os.path.join(ROOT, rel), encoding='utf-8', newline='').read()
    if re.search(r'(?<!<)/body>', s):
        broken.append((rel, lang))
print('pages with a malformed body close:', broken if broken else 'none')

# 2 · repair and inject
fixed = 0
for rel, lang in broken:
    p = os.path.join(ROOT, rel)
    s = open(p, encoding='utf-8', newline='').read()
    s = re.sub(r'(?<!<)/body>', '</body>', s)
    if 'sr-master-shell.js' not in s:
        i = s.rfind('</body>')
        s = s[:i] + TAG + '\r\n' + s[i:]
    open(p, 'w', encoding='utf-8', newline='').write(s)
    fixed += 1
print('repaired pages:', fixed)
