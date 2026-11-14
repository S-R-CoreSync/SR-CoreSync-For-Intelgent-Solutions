"""Give the hint script a cache key - it had none, so browsers kept the old one."""
import os, re

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
pages = [os.path.join(ROOT, 'index.html')]
for n in sorted(os.listdir(ROOT)):
    if n.startswith(('.', '_')) or n in {'build', 'node_modules', 'docs', 'partials', 'scripts',
                                         'assets', 'css', 'js', 'i18n', 'workers'}:
        continue
    p = os.path.join(ROOT, n, 'index.html')
    if os.path.isfile(p):
        pages.append(p)

pat = re.compile(r'(js/sr-lang-hint\.js)(?!\?v=)"')
changed = 0
for p in pages:
    s = open(p, encoding='utf-8', newline='').read()
    s2, n = pat.subn(r'\1?v=20261114-ring"', s)
    if n:
        open(p, 'w', encoding='utf-8', newline='').write(s2)
        changed += 1
print('pages re-keyed:', changed)
