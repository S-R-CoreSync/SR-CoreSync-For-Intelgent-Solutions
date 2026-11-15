# -*- coding: utf-8 -*-
"""Harvest the testimonial text and report what is still English."""
import json, os, re
import lxml.html

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
OUT = os.path.join(ROOT, 'i18n', 'sections', 'testimonials.json')
PREFIX = 'testimonials.'

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
        if not isinstance(el.tag, str):
            continue
        key = el.get('data-i18n') or ''
        if not key.startswith(PREFIX):
            continue
        if key.endswith('.rating'):
            found[key] = el.get('aria-label') or ''
        else:
            found[key] = re.sub(r'\s+', ' ', (el.text or '').strip())
    data[lang] = found

os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(data, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, sort_keys=True)
print('keys harvested: %d across %d languages (%.1f KB)'
      % (sum(len(v) for v in data.values()), len(data), os.path.getsize(OUT) / 1024))

en = data.get('en', {})
rows = []
for lang, keys in sorted(data.items()):
    if lang == 'en':
        continue
    same = [k.split('.', 1)[1] for k, v in keys.items() if k in en and v == en[k] and len(v) > 12]
    if same:
        rows.append((lang, len(same), same))

print('\nlanguages whose testimonial text equals the English one: %d' % len(rows))
for lang, n, same in sorted(rows, key=lambda r: -r[1])[:8]:
    print('  %-4s %d  %s' % (lang, n, ' '.join(same[:5])))
print('  ... total cells: %d' % sum(n for _, n, _ in rows))

print('\nfirst quote, three languages:')
for lang in ('ar', 'en', 'de'):
    print('  %-3s %s' % (lang, data.get(lang, {}).get('testimonials.01.quote', '(missing)')[:80]))
