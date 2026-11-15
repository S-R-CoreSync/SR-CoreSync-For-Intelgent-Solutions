# -*- coding: utf-8 -*-
"""Harvest the services text into JSON and show what is still English."""
import json, os, re
import lxml.html

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
OUT = os.path.join(ROOT, 'i18n', 'sections', 'services.json')

pages = [('index.html', 'ar')]
for n in sorted(os.listdir(ROOT)):
    if n.startswith(('.', '_')) or n in {'build', 'node_modules', 'docs', 'partials', 'scripts',
                                         'assets', 'css', 'js', 'i18n', 'workers'}:
        continue
    if os.path.isfile(os.path.join(ROOT, n, 'index.html')):
        pages.append((n + '/index.html', n))

data = {}
for rel, lang in pages:
    doc = lxml.html.fromstring(open(os.path.join(ROOT, rel), encoding='utf-8', newline='').read())
    found = {}
    for el in doc.iter():
        key = el.get('data-i18n') if isinstance(el.tag, str) else None
        if key and key.startswith('services.'):
            found[key] = re.sub(r'\s+', ' ', (el.text or '').strip())
    data[lang] = found

os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(data, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, sort_keys=True)
print('keys harvested: %d across %d languages' % (sum(len(v) for v in data.values()), len(data)))
print('written: i18n/sections/services.json (%.1f KB)' % (os.path.getsize(OUT) / 1024))

en = data.get('en', {})
print('\nsame text as English:')
rows = []
for lang, keys in sorted(data.items()):
    if lang == 'en':
        continue
    same = [k.split('.', 1)[1] for k, v in keys.items() if k in en and v == en[k]]
    if same:
        rows.append((lang, same))
for lang, same in rows:
    print('  %-4s %s' % (lang, ' '.join(same)))
print('\nlanguages affected: %d' % len(rows))

print('\nsample:')
for k in ('services.01.title', 'services.01.desc'):
    for lang in ('ar', 'en', 'de'):
        if k in data.get(lang, {}):
            print('  %-3s %-18s %s' % (lang, k.split('.', 1)[1], data[lang][k][:60]))
