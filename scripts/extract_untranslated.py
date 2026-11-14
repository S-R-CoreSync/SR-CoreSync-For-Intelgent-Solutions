"""Find the English sentences that leak into every translated page, and name the section they sit in."""
import gzip, re, urllib.request
from collections import Counter, OrderedDict
import lxml.html

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
SKIP_TAGS = {'script', 'style', 'noscript'}


def label_of(el):
    """nearest ancestor that names itself"""
    n = el
    while n is not None:
        if getattr(n, 'tag', None) in ('body', 'html'):
            return 'body'
        idv = n.get('id') or ''
        cls = n.get('class') or ''
        if idv:
            return '#' + idv
        if cls and ('section' in cls or cls.split()[0] in
                    {'hero', 'wg-plan', 'tf-header', 'container', 'srf', 'srf-cols', 'about-me', 'faq'}):
            return '.' + cls.split()[0]
        n = n.getparent()
    return '?'


def harvest(html):
    doc = lxml.html.fromstring(html)
    for bad in doc.xpath('//script|//style|//noscript'):
        bad.getparent().remove(bad)
    found = OrderedDict()
    for el in doc.iter():
        if el.tag in SKIP_TAGS or not isinstance(el.tag, str):
            continue
        text = (el.text or '').strip()
        if len(text) < 25:
            continue
        if len(STOP.findall(text)) < 2:
            continue
        # skip if a child already carries the same text (double count)
        found.setdefault(text, label_of(el))
    return found


tr = harvest(get('/tr/'))
ar = harvest(get('/'))
print('english lines found on /tr/ :', len(tr))
print('same lines also on /        :', sum(1 for t in tr if t in ar))

by_section = Counter(tr.values())
print('\nwhere they live:')
for sec, n in by_section.most_common():
    print('  %-24s %d' % (sec, n))

print('\n--- the lines ---')
for i, (t, sec) in enumerate(tr.items(), 1):
    print('%2d. [%s] %s' % (i, sec, re.sub(r'\s+', ' ', t)[:150]))
