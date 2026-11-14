"""Rebuild the list with the dictionary's own key format (/body[0]/main[0]/...)."""
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


def dict_path(el):
    """the translator's own addressing: /body[0]/main[0]/section[1]/p[0]"""
    parts = []
    node = el
    while node is not None and node.tag not in ('html',):
        parent = node.getparent()
        if parent is None:
            break
        same = [c for c in parent if getattr(c, 'tag', None) == node.tag]
        parts.append('/%s[%d]' % (node.tag, same.index(node)))
        node = parent
    return ''.join(reversed(parts))


STOP = re.compile(r'\b(the|and|with|your|from|that|this|will|have|about|package|price|request|'
                  r'software|solutions|included|everything|built|designed|complete|custom)\b', re.I)


def harvest(html):
    doc = lxml.html.fromstring(html)
    out = []
    for el in doc.iter():
        if not isinstance(el.tag, str) or el.tag in ('script', 'style', 'noscript', 'title'):
            continue
        t = (el.text or '').strip()
        if len(t) < 25 or len(STOP.findall(t)) < 2:
            continue
        out.append((dict_path(el) + '/text()', re.sub(r'\s+', ' ', t)))
    return out


tr = harvest(get('/tr/'))
ar = dict(harvest(get('/')))
bg = json.load(open(os.path.join(ROOT, 'i18n', 'bg.json'), encoding='utf-8'))

rows = []
for key, text in tr:
    rows.append({
        'key': key,
        'english': text,
        'arabic': ar.get(key, ''),
        'in_dict': 'yes' if key in bg else 'no',
        'bg_value': (bg.get(key, '') or '')[:70],
    })

out = os.path.join(ROOT, 'docs', 'ترجمات-ناقصة.csv')
with open(out, 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['key', 'english', 'arabic', 'in_dict', 'bg_value'])
    w.writeheader()
    w.writerows(rows)

print('rows:', len(rows))
print('arabic original found:', sum(1 for r in rows if r['arabic']))
print('key present in bg dict:', sum(1 for r in rows if r['in_dict'] == 'yes'))
print('\nsample:')
for r in rows[:3]:
    print('  key  ', r['key'][:70])
    print('  en   ', r['english'][:70])
    print('  ar   ', (r['arabic'] or '—')[:70])
    print('  bg   ', (r['bg_value'] or '—')[:70])
    print()
