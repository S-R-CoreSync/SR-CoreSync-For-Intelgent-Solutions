# -*- coding: utf-8 -*-
"""ku is Kurmanji (Latin script). I had put Sorani (Arabic script) into it.

The publish guard refused: "Contamination in ku/index.html" - four lines of
Arabic-script text on a Latin-script page. This replaces them with Kurmanji.
"""
import json, os, re

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'

KU = {
 'pricing.plan1.desc': 'Ji bo destpêkirina platformeke ewrayî ya taybet an hilberîna yekem a bingehîn îdeal e.',
 'pricing.plan3.desc': 'Audita tam a ewlehiyê, avahiyê û darayî ji bo rakirina tengasiyan',
 'pricing.plan3.period': '/ audita temam',
 'pricing.plan4.desc': 'Nasnameyên dîtbar ên cihê, bi stratejî, zelalî û yekgirtinê hatine avakirin da ku ewlehiya sazîyî xurt bikin.',
}

# 1 · the JSON
p = os.path.join(ROOT, 'i18n', 'sections', 'pricing.json')
data = json.load(open(p, encoding='utf-8'))
before = dict(data.get('ku', {}))
for k, v in KU.items():
    data['ku'][k] = v
json.dump(data, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, sort_keys=True)
print('json: ku fixed (%d values)' % len(KU))

# 2 · the page
page = os.path.join(ROOT, 'ku', 'index.html')
s = open(page, encoding='utf-8', newline='').read()
orig = s
for key, value in KU.items():
    pattern = re.compile(r'(data-i18n="%s"[^>]*>)[^<]*' % re.escape(key))
    s = pattern.sub(lambda m: m.group(1) + value, s)

open(page, 'w', encoding='utf-8', newline='').write(s)
print('page: ku updated' if s != orig else 'page: no change')

# 3 · prove no Arabic script is left in the four slots
import lxml.html
doc = lxml.html.fromstring(s)
bad = []
for el in doc.iter():
    if isinstance(el.tag, str) and (el.get('data-i18n') or '').startswith('pricing.'):
        t = (el.text or '')
        if re.search(r'[\u0600-\u06FF]', t):
            bad.append(el.get('data-i18n'))
print('arabic-script text left in pricing slots:', bad if bad else 'none')
