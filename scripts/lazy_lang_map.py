"""Replace the eager language-map tag with the lazy loader, on all 29 pages."""
import os, re, sys

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
PAGES = ['index.html']
for name in sorted(os.listdir(ROOT)):
    if name.startswith(('.', '_')) or name in {'build', 'node_modules', 'docs', 'partials', 'scripts'}:
        continue
    if os.path.isdir(os.path.join(ROOT, name)) and os.path.exists(os.path.join(ROOT, name, 'index.html')):
        PAGES.append(os.path.join(name, 'index.html'))

TAG = re.compile(r'<script[^>]+src="(\.\./)?js/sr-lang-map\.js[^"]*"[^>]*>\s*</script>', re.I)
dry = '--dry' in sys.argv
n = 0
for rel in PAGES:
    p = os.path.join(ROOT, rel)
    s = open(p, encoding='utf-8', newline='').read()
    m = TAG.search(s)
    if not m:
        print('%-22s no eager tag' % rel)
        continue
    prefix = '../' if rel != 'index.html' else './'
    tag = '<script src="%sjs/sr-lang-map-lazy.js?v=20261114" defer></script>' % prefix
    s2 = s[:m.start()] + tag + s[m.end():]
    if not dry:
        open(p, 'w', encoding='utf-8', newline='').write(s2)
    print('%-22s eager -> lazy' % rel)
    n += 1
print('\npages changed: %d' % n)
