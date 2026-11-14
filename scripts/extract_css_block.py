"""Move the 45 KB inline style block of the home page into a cached file.

It sits in the middle of the <head>, between two <link>s, so it is replaced by
exactly one <link> in exactly the same place: the cascade order does not move,
nothing else is touched, and the block becomes cacheable across the 29 pages.
"""
import os, re, hashlib, sys

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
PAGE = os.path.join(ROOT, 'index.html')
OUT = os.path.join(ROOT, 'css', 'sr-inline-block-a.css')

s = open(PAGE, encoding='utf-8', newline='').read()

best = None
for m in re.finditer(r'<style(?![^>]*\bid=)[^>]*>(.*?)</style>', s, re.S | re.I):
    if best is None or len(m.group(1)) > len(best.group(1)):
        best = m
if not best:
    raise SystemExit('no anonymous style block')

body = best.group(1)
digest = hashlib.sha1(body.encode()).hexdigest()[:10]
print('block: %.1f KB, sha1 %s' % (len(body.encode()) / 1024, digest))

open(OUT, 'w', encoding='utf-8', newline='\n').write(
    '/* Extracted verbatim from index.html; same place in the cascade. */\n' + body.strip() + '\n')
print('written css/sr-inline-block-a.css  %.1f KB' % (os.path.getsize(OUT) / 1024))

link = '<link rel="stylesheet" href="./css/sr-inline-block-a.css?v=%s">' % digest
s2 = s[:best.start()] + link + s[best.end():]

if '--dry' in sys.argv:
    print('dry run: page would go from %.1f KB to %.1f KB'
          % (len(s.encode()) / 1024, len(s2.encode()) / 1024))
else:
    open(PAGE, 'w', encoding='utf-8', newline='').write(s2)
    print('page: %.1f KB -> %.1f KB' % (len(s.encode()) / 1024, len(s2.encode()) / 1024))
