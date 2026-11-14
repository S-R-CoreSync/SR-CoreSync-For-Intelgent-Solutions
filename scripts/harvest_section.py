# -*- coding: utf-8 -*-
"""Harvest the current text of every keyed element into JSON, then verify.

This is the second condition: the text of a section lives in one JSON file per
section, addressed by meaning. Harvesting changes nothing - it records what is
already on the page, so the next edit has a single place to change.
"""
import json, os, re, sys
import lxml.html

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
OUT = os.path.join(ROOT, 'i18n', 'sections', 'pricing.json')

pages = [('index.html', 'ar')]
for n in sorted(os.listdir(ROOT)):
    if n.startswith(('.', '_')) or n in {'build', 'node_modules', 'docs', 'partials', 'scripts',
                                         'assets', 'css', 'js', 'i18n', 'workers'}:
        continue
    if os.path.isfile(os.path.join(ROOT, n, 'index.html')):
        pages.append((n + '/index.html', n))

data, gaps = {}, {}
for rel, lang in pages:
    doc = lxml.html.fromstring(open(os.path.join(ROOT, rel), encoding='utf-8', newline='').read())
    found = {}
    for el in doc.iter():
        key = el.get('data-i18n') if isinstance(el.tag, str) else None
        if key:
            found[key] = re.sub(r'\s+', ' ', (el.text or '').strip())
    data[lang] = found
    missing = [k for k in ('pricing.plan%d.%s' % (i, s) for i in range(1, 5) for s in ('period', 'desc', 'cta')) if k not in found]
    if missing:
        gaps[lang] = missing

os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(data, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, sort_keys=True)

total = sum(len(v) for v in data.values())
print('keys harvested: %d across %d languages' % (total, len(data)))
print('written: i18n/sections/pricing.json (%.1f KB)' % (os.path.getsize(OUT) / 1024))
print('\nlanguages with gaps: %d' % len(gaps))
for lang, miss in list(gaps.items())[:6]:
    print('  %-4s missing %d: %s' % (lang, len(miss), ', '.join(m.split('.', 1)[1] for m in miss)))

# distinct value per key, to show the text really differs by language
sample = 'pricing.plan1.desc'
print('\nsample — %s:' % sample)
for lang in ('ar', 'de', 'tr', 'en'):
    if lang in data and sample in data[lang]:
        print('  %-3s %s' % (lang, data[lang][sample][:70]))
