"""26 language pages point their canonical at /en/. Fix that one line per page.

The canonical is the page's own address; any other value tells a search engine
that this page is a duplicate of that address instead.
"""
import os, re, sys

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
BASE = 'https://sr-coresync.com'
PAGES = []
for name in sorted(os.listdir(ROOT)):
    p = os.path.join(ROOT, name, 'index.html')
    if name.startswith(('.', '_')) or name in {'build', 'node_modules', 'docs', 'partials'}:
        continue
    if os.path.isdir(os.path.join(ROOT, name)) and os.path.exists(p):
        PAGES.append(name)

PAT = re.compile(r'(<link[^>]+rel="canonical"[^>]*href=")([^"]+)(")', re.I)
dry = '--dry' in sys.argv
fixed = 0
for lang in PAGES:
    p = os.path.join(ROOT, lang, 'index.html')
    s = open(p, encoding='utf-8', newline='').read()
    want = '%s/%s/' % (BASE, lang)
    m = PAT.search(s)
    if not m:
        print('%-4s no canonical' % lang); continue
    if m.group(2).rstrip('/') == want.rstrip('/'):
        continue
    s2 = PAT.sub(lambda mm: mm.group(1) + want + mm.group(3), s, count=1)
    if not dry:
        open(p, 'w', encoding='utf-8', newline='').write(s2)
    print('%-4s %s -> %s' % (lang, m.group(2), want))
    fixed += 1

print('\ncanonicals corrected: %d' % fixed)
