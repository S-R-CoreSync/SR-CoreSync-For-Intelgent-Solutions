"""Preload the one font file each page will certainly need.

Both families are variable, so a single file covers every weight:
  · arabic pages  -> the Arabic subset of Alexandria
  · arabic-script pages (ckb) -> the same
  · every other   -> the basic-Latin subset of Figtree

Latin pages also carry Latin text inside Arabic pages, so the basic-Latin file
is preloaded there too - it is the face behind "S&R CoreSync" and every digit.
"""
import os, re, sys

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
ALEX_AR = 'assets/fonts/gf/fb351b4fc0e6cce9.woff2'
ALEX_LAT = 'assets/fonts/gf/d09128cc926d6565.woff2'
FIG_LAT = 'assets/fonts/gf/figtree-3c512d8e38.woff2'
ARABIC_SCRIPT = {'ar', 'ckb'}

pages = [('index.html', 'ar')]
for n in sorted(os.listdir(ROOT)):
    if n.startswith(('.', '_')) or n in {'build', 'node_modules', 'docs', 'partials', 'scripts',
                                         'assets', 'css', 'js', 'i18n', 'workers'}:
        continue
    p = os.path.join(ROOT, n, 'index.html')
    if os.path.isfile(p):
        pages.append((n + '/index.html', n))

dry = '--dry' in sys.argv
for rel, lang in pages:
    p = os.path.join(ROOT, rel)
    s = open(p, encoding='utf-8', newline='').read()
    if 'rel="preload" as="font"' in s:
        print('%-16s already' % lang)
        continue

    prefix = './' if rel == 'index.html' else '../'
    files = [ALEX_AR, ALEX_LAT] if lang in ARABIC_SCRIPT else [FIG_LAT]
    tags = ''.join(
        '<link rel="preload" as="font" type="font/woff2" crossorigin href="%s%s">\n' % (prefix, f)
        for f in files)

    anchor = '<link rel="stylesheet" href="%sassets/fonts/gf/fonts.css' % prefix
    i = s.find(anchor)
    if i < 0:
        print('%-16s anchor missing' % lang)
        continue
    s2 = s[:i] + tags + s[i:]
    if not dry:
        open(p, 'w', encoding='utf-8', newline='').write(s2)
    print('%-16s %d preload(s)' % (lang, len(files)))
