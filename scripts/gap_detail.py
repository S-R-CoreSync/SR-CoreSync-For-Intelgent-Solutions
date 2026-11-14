# -*- coding: utf-8 -*-
"""Exactly which cells are English, and what the four source strings say."""
import json, os

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
data = json.load(open(os.path.join(ROOT, 'i18n', 'sections', 'pricing.json'), encoding='utf-8'))
en = data['en']

KEYS = ['pricing.plan1.desc', 'pricing.plan3.desc', 'pricing.plan3.period', 'pricing.plan4.desc']
for k in KEYS:
    print('%s\n   EN: %s\n' % (k, en.get(k, '(missing)')))

need = {}
for lang, keys in data.items():
    if lang == 'en':
        continue
    for k, v in keys.items():
        if k in en and v.strip() == en[k].strip() and len(v) > 12:
            need.setdefault(lang, []).append(k.split('.', 1)[1])

print('cells to close: %d in %d languages' % (sum(len(v) for v in need.values()), len(need)))
print()
for lang, ks in sorted(need.items()):
    print('%-4s %s' % (lang, ' '.join(ks)))
