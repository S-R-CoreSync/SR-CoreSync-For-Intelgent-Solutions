# -*- coding: utf-8 -*-
"""Apply the service-card translations to the JSON and to the pages."""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from services_fix import build

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
FIX = build()

P = os.path.join(ROOT, 'i18n', 'sections', 'services.json')
data = json.load(open(P, encoding='utf-8'))
n = 0
for lang, pairs in FIX.items():
    data.setdefault(lang, {})
    for k, v in pairs.items():
        data[lang][k] = v
        n += 1
json.dump(data, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, sort_keys=True)
print('json updated:', n)

pages = [('index.html', 'ar')]
for d in sorted(os.listdir(ROOT)):
    if d.startswith(('.', '_')) or d in {'build', 'node_modules', 'docs', 'partials', 'scripts',
                                         'assets', 'css', 'js', 'i18n', 'workers'}:
        continue
    if os.path.isfile(os.path.join(ROOT, d, 'index.html')):
        pages.append((d + '/index.html', d))

changed = 0
for rel, lang in pages:
    if lang not in FIX:
        continue
    p = os.path.join(ROOT, rel)
    s = open(p, encoding='utf-8', newline='').read()
    orig = s
    for key, value in FIX[lang].items():
        s = re.sub(r'(data-i18n="%s"[^>]*>)[^<]*' % re.escape(key), lambda m: m.group(1) + value, s, count=1)
    if s != orig:
        open(p, 'w', encoding='utf-8', newline='').write(s)
        changed += 1
print('pages updated:', changed)
