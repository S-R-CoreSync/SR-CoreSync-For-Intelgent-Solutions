"""Any page still on Google Fonts or Plus Jakarta gets the same treatment as the rest."""
import os, re

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
pages = [('index.html', 'ar')]
for n in sorted(os.listdir(ROOT)):
    if n.startswith(('.', '_')) or n in {'build', 'node_modules', 'docs', 'partials', 'scripts',
                                         'assets', 'css', 'js', 'i18n', 'workers'}:
        continue
    if os.path.isfile(os.path.join(ROOT, n, 'index.html')):
        pages.append((n + '/index.html', n))

LINK = re.compile(r'<link[^>]+href="https://fonts\.googleapis\.com/css2\?[^"]+"[^>]*>', re.I)
PRE = re.compile(r'[ \t]*<link rel="preconnect" href="https://fonts\.(?:googleapis|gstatic)\.com"[^>]*>\r?\n', re.I)
ARABIC_SCRIPT = {'ar', 'ckb'}
ALEX_AR = 'assets/fonts/gf/fb351b4fc0e6cce9.woff2'
ALEX_LAT = 'assets/fonts/gf/d09128cc926d6565.woff2'
FIG_LAT = 'assets/fonts/gf/figtree-3c512d8e38.woff2'

touched = 0
for rel, lang in pages:
    p = os.path.join(ROOT, rel)
    s = open(p, encoding='utf-8', newline='').read()
    orig = s
    prefix = './' if rel == 'index.html' else '../'

    s = PRE.sub('', s)
    s = LINK.sub('<link rel="stylesheet" href="%sassets/fonts/gf/fonts.css?v=20261114">' % prefix, s)
    s = s.replace('Plus Jakarta Sans', 'Figtree')

    if 'rel="preload" as="font"' not in s:
        files = [ALEX_AR, ALEX_LAT] if lang in ARABIC_SCRIPT else [FIG_LAT]
        tags = ''.join('<link rel="preload" as="font" type="font/woff2" crossorigin href="%s%s">\n' % (prefix, f) for f in files)
        i = s.find('<link rel="stylesheet" href="%sassets/fonts/gf/fonts.css' % prefix)
        if i < 0:
            i = s.find('<link rel="stylesheet" href="%scss/' % prefix)
        if i > 0:
            s = s[:i] + tags + s[i:]

    if s != orig:
        open(p, 'w', encoding='utf-8', newline='').write(s)
        touched += 1
        print('%-16s updated' % lang)

print('\npages updated: %d' % touched)

# verify
print('\n--- verification ---')
bad = []
for rel, lang in pages:
    s = open(os.path.join(ROOT, rel), encoding='utf-8', newline='').read()
    g = len(re.findall(r'fonts\.(googleapis|gstatic)', s))
    pj = s.count('Plus Jakarta')
    pre = len(re.findall(r'rel="preload" as="font"', s))
    if g or pj or pre == 0:
        bad.append((lang, g, pj, pre))
print('pages with leftovers:', bad if bad else 'none')
