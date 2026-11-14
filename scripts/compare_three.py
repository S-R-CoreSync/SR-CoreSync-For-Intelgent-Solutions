"""Three questions, measured on this site and compared with what dananajmah does.

7  fonts: is the Arabic face conditioned to Arabic script, and is the Latin face
          separate? does each language preload only what it needs?
8  translations: does any Arabic text leak into a non-Arabic page, and does any
          English leak into a non-English one?
9  urls: does every address have exactly one canonical form, or do /en,
         /en/ and /en/index.html all answer 200?
"""
import os, re, urllib.request, gzip

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
BASE = 'https://sr-coresync.com'
UA = {'User-Agent': 'Mozilla/5.0 Chrome/120', 'Accept-Encoding': 'gzip'}


def get(url, head=False):
    req = urllib.request.Request(url, headers=UA, method='HEAD' if head else 'GET')
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            body = b'' if head else r.read()
            if r.headers.get('Content-Encoding') == 'gzip' and body:
                body = gzip.decompress(body)
            return r.status, r.geturl(), body.decode('utf-8', 'replace')
    except urllib.error.HTTPError as e:
        return e.code, url, ''
    except Exception as e:
        return 0, url, str(e)


print('=== 9 · URL shapes ===')
for u in ('/en', '/en/', '/en/index.html', '/index.html', '/'):
    st, final, _ = get(BASE + u, head=True)
    print('%-22s %s  -> %s' % (u, st, final.replace(BASE, '') or '/'))

print('\n=== 7 · fonts ===')
css = get(BASE + '/assets/fonts/gf/fonts.css')[2]
faces = re.findall(r'@font-face\s*\{[^}]*\}', css)
fam = {}
for f in faces:
    name = re.search(r"font-family:\s*'([^']+)'", f)
    if not name:
        continue
    fam.setdefault(name.group(1), []).append('ranged' if 'unicode-range' in f else 'all-glyphs')
for k, v in fam.items():
    print('  %-12s %d faces · %s' % (k, len(v), 'all with unicode-range' if all(x == 'ranged' for x in v) else 'mixed'))

for page, label in (('/', 'ar'), ('/en/', 'en'), ('/de/', 'de')):
    html = get(BASE + page)[2]
    pre = re.findall(r'<link[^>]+rel="preload"[^>]+as="font"[^>]*href="([^"]+)"', html)
    print('  %-3s preloads: %s' % (label, [p.split('/')[-1] for p in pre] or 'none'))

print('\n=== 8 · leftovers ===')
AR = re.compile(r'[\u0600-\u06FF]')
EN_WORDS = re.compile(r'\b(the|and|with|your|from|about|contact|price|home)\b', re.I)
for lang in ('en', 'nl', 'de', 'fr', 'es', 'tr', 'ckb', 'ku'):
    html = get(BASE + '/%s/' % lang)[2]
    body = re.sub(r'<script.*?</script>|<style.*?</style>', ' ', html, flags=re.S | re.I)
    text = re.sub(r'<[^>]+>', ' ', body)
    ar = AR.findall(text)
    en = len(EN_WORDS.findall(text))
    print('  %-4s arabic chars=%-4d english-words=%-4d' % (lang, len(ar), en))
