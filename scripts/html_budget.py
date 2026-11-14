import gzip, os, re, zlib

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
P = os.path.join(ROOT, 'index.html')
s = open(P, encoding='utf-8', newline='').read()
raw = s.encode('utf-8')

styles = re.findall(r'<style[^>]*>(.*?)</style>', s, re.S | re.I)
scripts = re.findall(r'<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>', s, re.S | re.I)
linked_scripts = re.findall(r'<script[^>]+src="([^"]+)"', s, re.I)
links = re.findall(r'<link[^>]+rel="stylesheet"[^>]*href="([^"]+)"', s, re.I)

css_bytes = sum(len(x.encode('utf-8')) for x in styles)
js_bytes = sum(len(x.encode('utf-8')) for x in scripts)

print('file bytes          %8.1f KB' % (len(raw) / 1024))
print('gzip (level 9)      %8.1f KB' % (len(gzip.compress(raw, 9)) / 1024))
print('brotli-ish (zlib9)  %8.1f KB  (approx)' % (len(zlib.compress(raw, 9)) / 1024))
print()
print('inline <style>      %8.1f KB  in %d blocks' % (css_bytes / 1024, len(styles)))
print('inline <script>     %8.1f KB  in %d blocks' % (js_bytes / 1024, len(scripts)))
print('markup + rest       %8.1f KB' % ((len(raw) - css_bytes - js_bytes) / 1024))
print()
print('external css files  %d' % len(links))
print('external js files   %d' % len(linked_scripts))

print('\nlargest inline style blocks:')
for i, x in sorted(enumerate(styles), key=lambda kv: -len(kv[1]))[:6]:
    head = re.sub(r'\s+', ' ', x[:70])
    print('  %5.1f KB  #%d  %s' % (len(x.encode()) / 1024, i, head))

print('\nlargest inline script blocks:')
for i, x in sorted(enumerate(scripts), key=lambda kv: -len(kv[1]))[:6]:
    head = re.sub(r'\s+', ' ', x[:70])
    print('  %5.1f KB  #%d  %s' % (len(x.encode()) / 1024, i, head))

# what does the browser actually pay: html gz + linked css/js gz
print('\nexternal assets (raw KB / gzip KB):')
tot_raw = tot_gz = 0
for href in links + linked_scripts:
    if href.startswith('http'):
        continue
    p = os.path.join(ROOT, href.split('?')[0].lstrip('./').replace('/', os.sep))
    if os.path.exists(p):
        d = open(p, 'rb').read()
        g = len(gzip.compress(d, 9))
        tot_raw += len(d); tot_gz += g
        if len(d) > 60000:
            print('  %-52s %7.1f / %6.1f' % (href[:52], len(d) / 1024, g / 1024))
print('  ---- totals for linked assets: %.1f KB raw / %.1f KB gzip' % (tot_raw / 1024, tot_gz / 1024))
