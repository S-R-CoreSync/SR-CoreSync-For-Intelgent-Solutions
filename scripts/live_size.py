import gzip, urllib.request

req = urllib.request.Request('https://sr-coresync.com/index.html?cb=live-check',
                             headers={'User-Agent': 'Mozilla/5.0 Chrome/120'})
with urllib.request.urlopen(req, timeout=40) as r:
    raw = r.read()
    enc = r.headers.get('Content-Encoding', '')
    if 'gzip' in enc:
        raw = gzip.decompress(raw)

print('live HTML  : %.1f KB (%d bytes)' % (len(raw) / 1024, len(raw)))
print('gzip level9: %.1f KB' % (len(gzip.compress(raw, 9)) / 1024))

css = urllib.request.urlopen(urllib.request.Request(
    'https://sr-coresync.com/css/sr-inline-block-a.css',
    headers={'User-Agent': 'Mozilla/5.0 Chrome/120'})).read()
print('extracted css: %.1f KB raw, %.1f KB gzip' % (len(css) / 1024, len(gzip.compress(css, 9)) / 1024))
