"""Bump the cache key on every stylesheet link.

The CSS bytes changed but the ?v= token did not, so browsers kept the old sheet
and still rendered Plus Jakarta. A new token makes the change visible on the
next load instead of whenever the cache happens to expire.
"""
import os, re, sys

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
TOKEN = '20261114-type'

pages = ['index.html']
for name in sorted(os.listdir(ROOT)):
    if name.startswith(('.', '_')) or name in {'build', 'node_modules', 'docs', 'partials', 'scripts', 'assets', 'css', 'js', 'i18n', 'workers'}:
        continue
    if os.path.isdir(os.path.join(ROOT, name)) and os.path.exists(os.path.join(ROOT, name, 'index.html')):
        pages.append(os.path.join(name, 'index.html'))

LINK = re.compile(r'(<link[^>]+href="(?:\.{1,2}/)?css/[^"?]+\.css)\?v=[^"]*(")', re.I)
dry = '--dry' in sys.argv
changed = 0
for rel in pages:
    p = os.path.join(ROOT, rel)
    s = open(p, encoding='utf-8', newline='').read()
    s2, n = LINK.subn(lambda m: m.group(1) + '?v=' + TOKEN + m.group(2), s)
    if n:
        changed += 1
        if not dry:
            open(p, 'w', encoding='utf-8', newline='').write(s2)
print('pages updated: %d (links re-keyed in each)' % changed)
