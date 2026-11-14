"""How much English is still visible on each language page?"""
import gzip, re, urllib.request
from concurrent.futures import ThreadPoolExecutor

BASE = 'https://sr-coresync.com'
UA = {'User-Agent': 'Mozilla/5.0 Chrome/120', 'Accept-Encoding': 'gzip'}
LANGS = ['bg','ckb','cs','da','de','el','en','es','et','fi','fr','ga','hr','hu','it','ku',
         'lt','lv','mt','nl','no','pl','pt','ro','sk','sl','sv','tr']

EN = re.compile(r'\b(the|and|with|your|from|that|this|will|have|about|package|price|request|software|solutions)\b', re.I)


def get(lang):
    req = urllib.request.Request(BASE + '/%s/' % lang, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        b = r.read()
        if r.headers.get('Content-Encoding') == 'gzip':
            b = gzip.decompress(b)
    html = b.decode('utf-8', 'replace')
    body = re.sub(r'<script.*?</script>|<style.*?</style>', ' ', html, flags=re.S | re.I)
    text = re.sub(r'<[^>]+>', '\n', body)
    lines = [re.sub(r'\s+', ' ', l).strip() for l in text.split('\n')]
    lines = [l for l in lines if len(l) > 25]
    eng = [l for l in lines if len(EN.findall(l)) >= 2]
    return lang, len(lines), len(eng)


with ThreadPoolExecutor(max_workers=6) as ex:
    rows = list(ex.map(get, LANGS))

rows.sort(key=lambda r: -r[2])
print('%-4s %-10s %-10s %s' % ('lang', 'lines', 'english', 'share'))
for lang, total, eng in rows[:14]:
    print('%-4s %-10d %-10d %.1f%%' % (lang, total, eng, 100 * eng / max(1, total)))
print('\nclean pages (<=2 lines):', ', '.join(l for l, t, e in rows if e <= 2))
