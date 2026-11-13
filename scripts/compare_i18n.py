import re, os, subprocess, json, urllib.request, gzip

def fetch(url):
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36'})
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            raw = r.read()
            enc = r.headers.get('Content-Encoding', '')
            if 'gzip' in enc:
                raw = gzip.decompress(raw)
            return raw.decode('utf-8', 'replace'), dict(r.headers), r.status
    except Exception as e:
        return '', {'error': str(e)}, 0

def scan(url, label):
    h, hd, st = fetch(url)
    out = {'label': label, 'status': st, 'bytes': len(h)}
    m = re.search(r'<html[^>]*>', h, re.I)
    out['html_tag'] = m.group(0)[:120] if m else ''
    out['hreflang'] = len(re.findall(r'rel=["\']alternate["\'][^>]*hreflang', h, re.I))
    out['canonical'] = len(re.findall(r'rel=["\']canonical["\']', h, re.I))
    out['og_locale'] = len(re.findall(r'og:locale', h, re.I))
    out['jsonld'] = len(re.findall(r'application/ld\+json', h, re.I))
    out['manifest'] = len(re.findall(r'rel=["\']manifest["\']', h, re.I))
    out['sw'] = len(re.findall(r'serviceWorker', h))
    out['preload'] = len(re.findall(r'rel=["\']preload["\']', h, re.I))
    out['fonts_google'] = len(re.findall(r'fonts\.(googleapis|gstatic)', h, re.I))
    out['font_face_inline'] = len(re.findall(r'@font-face', h, re.I))
    out['script_tags'] = len(re.findall(r'<script', h, re.I))
    out['stylesheet_links'] = len(re.findall(r'rel=["\']stylesheet["\']', h, re.I))
    out['nav_element'] = len(re.findall(r'<nav[\s>]', h, re.I))
    out['skip_link'] = len(re.findall(r'skip|تخطَّ إلى', h, re.I))
    out['viewport'] = (re.search(r'<meta[^>]+viewport[^>]*>', h, re.I) or [None])
    out['viewport'] = out['viewport'].group(0)[:150] if out['viewport'] else ''
    out['csp'] = hd.get('Content-Security-Policy', '')[:80]
    out['server'] = hd.get('Server', '')
    out['accept_lang_vary'] = hd.get('Vary', '')
    return out

rows = [scan('https://dananajmah.com/', 'dananajmah ar'),
        scan('https://dananajmah.com/en/', 'dananajmah en'),
        scan('https://sr-coresync.com/', 'coresync ar'),
        scan('https://sr-coresync.com/en/', 'coresync en')]

keys = ['status', 'bytes', 'hreflang', 'canonical', 'og_locale', 'jsonld', 'manifest', 'sw',
        'preload', 'fonts_google', 'font_face_inline', 'script_tags', 'stylesheet_links',
        'nav_element', 'skip_link']
print('%-18s' % 'metric', end='')
for r in rows:
    print('%-16s' % r['label'], end='')
print()
for k in keys:
    print('%-18s' % k, end='')
    for r in rows:
        print('%-16s' % r.get(k, ''), end='')
    print()
print()
for r in rows:
    print(r['label'], '|', r['html_tag'])
    print('   viewport:', r['viewport'])
    print('   server:', r['server'], '| csp:', (r['csp'] or '-')[:60])
