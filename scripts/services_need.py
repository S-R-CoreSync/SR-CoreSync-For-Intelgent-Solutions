import json
d = json.load(open(r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project\i18n\sections\services.json', encoding='utf-8'))
en = d['en']
need = {}
for lang, keys in sorted(d.items()):
    if lang == 'en':
        continue
    miss = [k.split('.', 1)[1] for k, v in keys.items() if k in en and v == en[k]]
    if miss:
        need[lang] = miss
print('languages:', len(need), '· cells:', sum(len(v) for v in need.values()))
for lang, miss in need.items():
    print('%-4s %s' % (lang, ' '.join(miss)))
print()
for k in ('01.title', '02.title', '03.title', '03.desc'):
    print('%-10s EN: %s' % (k, en['services.' + k]))
