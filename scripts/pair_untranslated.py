"""Pair each leaked English line with the Arabic sentence in the same place.

The dictionary addresses strings by XPath, so a change in markup moves every key
and the value silently falls back to English. Matching by section + order does
not depend on the path, and it tells us what the Arabic original actually says.
"""
import csv, gzip, json, os, re, urllib.request
import lxml.html

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
BASE = 'https://sr-coresync.com'
UA = {'User-Agent': 'Mozilla/5.0 Chrome/120', 'Accept-Encoding': 'gzip'}

STOP = re.compile(r'\b(the|and|with|your|from|that|this|will|have|about|package|price|request|'
                  r'software|solutions|included|everything|built|designed|complete|custom)\b', re.I)


def get(path):
    req = urllib.request.Request(BASE + path, headers=UA)
    with urllib.request.urlopen(req, timeout=40) as r:
        b = r.read()
        if r.headers.get('Content-Encoding') == 'gzip':
            b = gzip.decompress(b)
    return b.decode('utf-8', 'replace')


def section_of(el):
    n = el
    while n is not None and getattr(n, 'tag', None) not in ('body', 'html'):
        idv = n.get('id') or ''
        cls = (n.get('class') or '').split()
        if idv:
            return '#' + idv
        if cls and ('section' in cls[0] or cls[0].startswith('wg')):
            return '.' + cls[0]
        n = n.getparent()
    return 'body'


def lines(html, english_only):
    doc = lxml.html.fromstring(html)
    out = []
    for el in doc.iter():
        if not isinstance(el.tag, str) or el.tag in ('script', 'style', 'noscript', 'title'):
            continue
        t = re.sub(r'\s+', ' ', (el.text or '').strip())
        if len(t) < 12:
            continue
        if english_only:
            if len(t) < 25 or len(STOP.findall(t)) < 2:
                continue
        out.append((section_of(el), t))
    return out


en_lines = lines(get('/tr/'), True)
ar_lines = lines(get('/'), False)

# bucketed by section, then aligned by position inside that bucket
buckets = {}
for sec, t in ar_lines:
    buckets.setdefault(sec, []).append(t)

rows = []
cursor = {}
for sec, t in en_lines:
    pool = buckets.get(sec, [])
    i = cursor.get(sec, 0)
    ar = pool[i] if i < len(pool) else ''
    cursor[sec] = i + 1
    rows.append({'section': sec, 'english': t, 'arabic': ar})

out = os.path.join(ROOT, 'docs', 'ترجمات-ناقصة.csv')
with open(out, 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['section', 'english', 'arabic'])
    w.writeheader()
    w.writerows(rows)

print('rows:', len(rows), '· with an arabic counterpart:', sum(1 for r in rows if r['arabic']))
print()
for r in rows[:6]:
    print('%-24s EN: %s' % (r['section'], r['english'][:70]))
    print('%-24s AR: %s' % ('', (r['arabic'] or '—')[:70]))
