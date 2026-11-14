# -*- coding: utf-8 -*-
"""Ground truth for the three-options document: who serves the site, how many pages, how big."""
import os, urllib.request, gzip

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
BASE = 'https://sr-coresync.com'

req = urllib.request.Request(BASE + '/', headers={'User-Agent': 'Mozilla/5.0 Chrome/120'})
with urllib.request.urlopen(req, timeout=30) as r:
    h = dict(r.headers)

print('=== who serves the site ===')
for k in ('Server', 'CF-Ray', 'X-GitHub-Request-Id', 'Via', 'Cache-Control', 'Content-Encoding'):
    print('  %-22s %s' % (k, h.get(k, '—')))

print('\n=== how many pages, how heavy ===')
pages, total = [], 0
for name in sorted(os.listdir(ROOT)):
    p = os.path.join(ROOT, 'index.html') if name == 'index.html' else os.path.join(ROOT, name, 'index.html')
    if name == 'index.html' or (not name.startswith(('.', '_')) and os.path.isfile(p)):
        size = os.path.getsize(p)
        pages.append((name, size))
        total += size

top = sorted(pages, key=lambda x: -x[1])[:5]
print('  pages on disk: %d' % len(pages))
print('  total bytes: %.1f MB' % (total / 1024 / 1024))
print('  largest:', ', '.join('%s %.0fKB' % (n, s / 1024) for n, s in top))

print('\n=== what is already generated from the master ===')
print('  partials/:      %d files' % len([f for f in os.listdir(os.path.join(ROOT, 'partials')) if f.endswith('.html')]))
print('  partials/en:    %d files' % len([f for f in os.listdir(os.path.join(ROOT, 'partials', 'en')) if f.endswith('.html')]))
print('  scripts:        build_site.py · build_lang.py · sync_locales.py · preflight.py')
