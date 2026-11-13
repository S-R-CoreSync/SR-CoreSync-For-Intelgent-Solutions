# -*- coding: utf-8 -*-
"""Which image requests could a sprite remove?"""
import re, os, collections

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
s = open(os.path.join(ROOT, 'index.html'), encoding='utf-8', newline='').read()

srcs = re.findall(r'<img\b[^>]*(?:src|data-src)="([^"#]+)"', s)
css = re.findall(r'url\((["\']?)([^)\'"]+\.(?:png|jpg|jpeg|webp|svg))\1\)', s)
files = [x[1] for x in css]

def size(p):
    q = os.path.join(ROOT, p.lstrip('./'))
    return os.path.getsize(q) / 1024 if os.path.exists(q) else -1

uniq = list(dict.fromkeys([f for f in srcs if not f.startswith(('http', 'data:'))]))
small = [(f, size(f)) for f in uniq if 0 <= size(f) < 12]
big = [(f, size(f)) for f in uniq if size(f) >= 12]

print('img tags on the master      :', len(srcs))
print('unique local images         :', len(uniq))
print('css background urls         :', len(set(files)))
print()
print('under 12KB (sprite candidates):', len(small), ' files,', round(sum(k for _, k in small), 1), 'KB total')
for f, k in sorted(small, key=lambda x: -x[1])[:10]:
    print('   %6.1f KB  %s' % (k, f))
print()
print('12KB and above              :', len(big))
for f, k in sorted(big, key=lambda x: -x[1])[:5]:
    print('   %6.1f KB  %s' % (k, f))
