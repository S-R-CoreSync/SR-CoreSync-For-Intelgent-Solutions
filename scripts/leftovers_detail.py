import gzip, re, urllib.request

BASE = 'https://sr-coresync.com'
UA = {'User-Agent': 'Mozilla/5.0 Chrome/120', 'Accept-Encoding': 'gzip'}


def get(u):
    req = urllib.request.Request(u, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        b = r.read()
        if r.headers.get('Content-Encoding') == 'gzip':
            b = gzip.decompress(b)
        return b.decode('utf-8', 'replace')


print('=== preload tags on the arabic page ===')
h = get(BASE + '/')
for m in re.finditer(r'<link[^>]+rel="preload"[^>]*>', h):
    print(' ', re.sub(r'\s+', ' ', m.group(0))[:150])

print('\n=== english phrases left in the turkish page ===')
tr = get(BASE + '/tr/')
body = re.sub(r'<script.*?</script>|<style.*?</style>', ' ', tr, flags=re.S | re.I)
text = re.sub(r'<[^>]+>', '\n', body)
lines = [re.sub(r'\s+', ' ', l).strip() for l in text.split('\n')]
eng = [l for l in lines if len(l) > 25 and re.search(r'\b(the|and|with|your|from|about|contact|price|request|software|solutions)\b', l, re.I)]
for l in eng[:12]:
    print('  ·', l[:120])

print('\n=== english phrases left in the kurmanji page ===')
ku = get(BASE + '/ku/')
body = re.sub(r'<script.*?</script>|<style.*?</style>', ' ', ku, flags=re.S | re.I)
text = re.sub(r'<[^>]+>', '\n', body)
lines = [re.sub(r'\s+', ' ', l).strip() for l in text.split('\n')]
eng = [l for l in lines if len(l) > 25 and re.search(r'\b(the|and|with|your|from|about|contact|price|request|software|solutions)\b', l, re.I)]
for l in eng[:12]:
    print('  ·', l[:120])
