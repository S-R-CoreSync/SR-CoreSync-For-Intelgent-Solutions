import re, json, urllib.request, gzip, io

URL = 'https://dananajmah.com'
req = urllib.request.Request(URL, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36',
    'Accept-Encoding': 'gzip, deflate, br',
})
with urllib.request.urlopen(req, timeout=40) as r:
    raw = r.read()
    enc = r.headers.get('Content-Encoding', '')
    headers = dict(r.headers)
if 'gzip' in enc:
    raw = gzip.decompress(raw)
html = raw.decode('utf-8', 'replace')

print('bytes', len(html))
print('--- html tag ---')
m = re.search(r'<html[^>]*>', html, re.I)
print(m.group(0)[:300] if m else 'n/a')

print('\n--- title / meta ---')
for pat in (r'<title[^>]*>(.*?)</title>', r'<meta name="generator"[^>]*>', r'<meta name="description"[^>]*>'):
    for mm in re.finditer(pat, html, re.I | re.S):
        print(mm.group(0)[:200])

print('\n--- stylesheets ---')
for mm in re.finditer(r'<link[^>]+rel=["\']stylesheet["\'][^>]*>', html, re.I):
    print(mm.group(0)[:180])

print('\n--- scripts (external) ---')
for mm in re.finditer(r'<script[^>]+src=["\']([^"\']+)["\']', html, re.I):
    print(mm.group(1)[:160])

print('\n--- hreflang ---')
for mm in re.finditer(r'<link[^>]+hreflang=["\']([^"\']+)["\'][^>]*>', html, re.I):
    print(mm.group(0)[:200])

print('\n--- inline script count / size ---')
inl = list(re.finditer(r'<script(?![^>]*src)[^>]*>(.*?)</script>', html, re.I | re.S))
print('inline scripts:', len(inl), 'chars:', sum(len(x.group(1)) for x in inl))

print('\n--- tech signals ---')
for sig in ['wp-content', 'wp-json', 'elementor', 'swiper', 'owl', 'aos', 'gsap', 'lottie',
            'fontawesome', 'font-awesome', 'fonts.googleapis', 'gstatic', 'cdn.jsdelivr', 'unpkg',
            'sweetalert', 'animate.css', 'wow.js', 'wpml', 'polylang', 'translatepress', 'trp-',
            'gtranslate', 'weglot', 'conveythis', 'lang-switch', 'hreflang', 'og:locale']:
    c = len(re.findall(re.escape(sig), html, re.I))
    if c:
        print('%-20s %d' % (sig, c))
