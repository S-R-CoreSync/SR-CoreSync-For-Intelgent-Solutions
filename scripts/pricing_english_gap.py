# -*- coding: utf-8 -*-
"""How many languages still carry the English pricing text, now that it is in one file?"""
import json, os

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
data = json.load(open(os.path.join(ROOT, 'i18n', 'sections', 'pricing.json'), encoding='utf-8'))
en = data.get('en', {})

print('%-4s %-8s %s' % ('lang', 'english', 'which'))
rows = []
for lang, keys in sorted(data.items()):
    if lang == 'en':
        continue
    same = [k.split('.', 1)[1] for k, v in keys.items() if k in en and v.strip() == en[k].strip() and len(v) > 12]
    rows.append((lang, len(same), same))

for lang, n, same in sorted(rows, key=lambda r: -r[1]):
    print('%-4s %-8d %s' % (lang, n, ', '.join(same[:4])))

total = sum(n for _, n, _ in rows)
print('\nlanguages with identical-to-English pricing text: %d · cells: %d'
      % (sum(1 for _, n, _ in rows if n), total))
