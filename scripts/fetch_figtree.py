"""Fetch Figtree (her Latin face) so it can be compared honestly, not described."""
import hashlib, os, re, urllib.request

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
OUT = os.path.join(ROOT, 'docs', 'font-compare')
os.makedirs(OUT, exist_ok=True)

UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
URL = 'https://fonts.googleapis.com/css2?family=Figtree:wght@300..900&display=swap'


def get(u, binary=False):
    req = urllib.request.Request(u, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        d = r.read()
    return d if binary else d.decode('utf-8')


css = get(URL)
blocks = re.findall(r'@font-face\s*\{[^}]*\}', css)
seen, out = {}, []
for b in blocks:
    m = re.search(r'url\((https://fonts\.gstatic\.com/[^)]+\.woff2)\)', b)
    if not m:
        continue
    u = m.group(1)
    if u not in seen:
        name = 'figtree-' + hashlib.sha1(u.encode()).hexdigest()[:10] + '.woff2'
        open(os.path.join(OUT, name), 'wb').write(get(u, binary=True))
        seen[u] = name
    out.append(b.replace(m.group(0), 'url(./%s)' % seen[u]))

open(os.path.join(OUT, 'figtree.css'), 'w', encoding='utf-8', newline='\n').write('\n'.join(out))
print('figtree files:', len(seen), 'css written')
