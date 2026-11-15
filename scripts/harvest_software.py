# -*- coding: utf-8 -*-
"""Harvest the nine software descriptions and report the English gap."""
import json, os, re
import lxml.html

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
OUT = os.path.join(ROOT, 'i18n', 'sections', 'software.json')

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
        if key and key.startswith('software.'):
            found[key] = re.sub(r'\s+', ' ', (el.text or '').strip())
    data[lang] = found

json.dump(data, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, sort_keys=True)
print('keys: %d across %d languages (%.1f KB)'
      % (sum(len(v) for v in data.values()), len(data), os.path.getsize(OUT) / 1024))

en = data.get('en', {})
rows = []
for lang, keys in sorted(data.items()):
    if lang == 'en':
        continue
    same = [k.split('.', 1)[1] for k, v in keys.items() if k in en and v == en[k]]
    if same:
        rows.append((lang, len(same)))

print('\nlanguages with English descriptions: %d · cells: %d'
      % (len(rows), sum(n for _, n in rows)))
for lang, n in sorted(rows, key=lambda r: -r[1])[:10]:
    print('  %-4s %d/9' % (lang, n))

print('\nclean:', ' '.join(l for l, k in sorted(data.items()) if l != 'en' and not any(
    v == en.get(k2) for k2, v in k.items())))
