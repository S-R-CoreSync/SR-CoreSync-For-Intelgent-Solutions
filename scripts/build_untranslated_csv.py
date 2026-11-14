"""Build the list: what is still English, where it lives, and what the Arabic says.

The site translates by XPath dictionary (i18n/xx.json). A string stays English
when its entry was never filled in. So the list is worth more as keys than as
sentences: fill the value once per language and the page is done.
"""
import csv, gzip, json, os, re, urllib.request
import lxml.html

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
BASE = 'https://sr-coresync.com'
UA = {'User-Agent': 'Mozilla/5.0 Chrome/120', 'Accept-Encoding': 'gzip'}


def get(path):
    req = urllib.request.Request(BASE + path, headers=UA)
    with urllib.request.urlopen(req, timeout=40) as r:
        b = r.read()
        if r.headers.get('Content-Encoding') == 'gzip':
            b = gzip.decompress(b)
    return b.decode('utf-8', 'replace')


STOP = re.compile(r'\b(the|and|with|your|from|that|this|will|have|about|package|price|request|'
                  r'software|solutions|included|everything|built|designed|complete|custom)\b', re.I)


def harvest(html):
    doc = lxml.html.fromstring(html)
    out = []
    for el in doc.iter():
        if el.tag in ('script', 'style', 'noscript') or not isinstance(el.tag, str):
            continue
        t = (el.text or '').strip()
        if len(t) < 25 or len(STOP.findall(t)) < 2:
            continue
        out.append((doc.getroottree().getpath(el) + '/text()', re.sub(r'\s+', ' ', t)))
    return out


tr = harvest(get('/tr/'))
ar = dict(harvest(get('/')))

# cross-check against the dictionary of one language
bg = json.load(open(os.path.join(ROOT, 'i18n', 'bg.json'), encoding='utf-8'))

rows = []
for key, text in tr:
    rows.append({
        'key': key,
        'english': text,
        'arabic': ar.get(key, ''),
        'in_bg_dict': 'yes' if key in bg else 'no',
        'bg_value': (bg.get(key, '') or '')[:60],
    })

out = os.path.join(ROOT, 'docs', 'ترجمات-ناقصة.csv')
os.makedirs(os.path.dirname(out), exist_ok=True)
with open(out, 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['key', 'english', 'arabic', 'in_bg_dict', 'bg_value'])
    w.writeheader()
    w.writerows(rows)

print('rows written:', len(rows), '->', out)
print('with an arabic original:', sum(1 for r in rows if r['arabic']))
print('with a dictionary key  :', sum(1 for r in rows if r['in_bg_dict'] == 'yes'))

# how many languages still carry the English for these keys?
langs = [f[:-5] for f in sorted(os.listdir(os.path.join(ROOT, 'i18n'))) if f.endswith('.json')]
print('\nlanguage files:', len(langs))
for lang in langs[:6]:
    d = json.load(open(os.path.join(ROOT, 'i18n', lang + '.json'), encoding='utf-8'))
    still = sum(1 for r in rows if (d.get(r['key']) or '') == r['english'])
    print('  %-4s still english: %d of %d' % (lang, still, len(rows)))
