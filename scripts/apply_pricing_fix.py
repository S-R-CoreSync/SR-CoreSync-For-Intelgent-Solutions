# -*- coding: utf-8 -*-
"""Write the four missing translations into the JSON, then into the pages."""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pricing_fix_66 import FIX
import lxml.html

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
P = os.path.join(ROOT, 'i18n', 'sections', 'pricing.json')
data = json.load(open(P, encoding='utf-8'))

applied = 0
for lang, pairs in FIX.items():
    data.setdefault(lang, {})
    for k, v in pairs.items():
        data[lang][k] = v
        applied += 1

json.dump(data, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, sort_keys=True)
print('json updated: %d values' % applied)

# now push the same values into the pages
pages = [('index.html', 'ar')]
for n in sorted(os.listdir(ROOT)):
    if n.startswith(('.', '_')) or n in {'build', 'node_modules', 'docs', 'partials', 'scripts',
                                         'assets', 'css', 'js', 'i18n', 'workers'}:
        continue
    if os.path.isfile(os.path.join(ROOT, n, 'index.html')):
        pages.append((n + '/index.html', n))

changed = 0
for rel, lang in pages:
    if lang not in FIX:
        continue
    p = os.path.join(ROOT, rel)
    s = open(p, encoding='utf-8', newline='').read()
    orig = s
    for key, value in FIX[lang].items():
        # replace the text right after the element that carries this key
        pattern = re.compile(r'(data-i18n="%s"[^>]*>)([^<]*)' % re.escape(key))
        s = pattern.sub(lambda m: m.group(1) + value, s)
    if s != orig:
        open(p, 'w', encoding='utf-8', newline='').write(s)
        changed += 1

print('pages updated:', changed)
